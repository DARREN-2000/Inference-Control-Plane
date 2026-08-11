# Deployment reference

These files are reviewable examples for the production topology described in
[`DESIGN.md`](../DESIGN.md). They are not applied from this repository; the platform's
Terraform/IaC stack should own real resource identifiers, IAM, networking, alarms, and
rollout policy.

## Production topology represented by the checked-in files

```text
EventBridge Scheduler: every 5 minutes
        │
        ▼
ECS Fargate task: gateway-sli (one container, private subnets, no public IP)
        ├── reads a closed 5-minute Langfuse window
        ├── delays the window by 10 minutes for late traces
        ├── re-reads a 10-minute overlap and deduplicates it
        ├── conditionally commits watermark/seen IDs to DynamoDB
        └── sends OTLP/HTTP to the shared collector endpoint
                         │
                         ▼
              shared OTel Collector → Datadog
```

The production task definition references an immutable image digest, runs with a
read-only root filesystem, receives Langfuse credentials from Secrets Manager, and uses
an IAM task role for DynamoDB. The collector is a **shared external service**, not an ECS
sidecar in `ecs-task-def.json`.

`docker-compose.yml` is intentionally different: it starts a local collector container
beside the application for a self-contained smoke test.

## Correctness and retry semantics

- EventBridge starts one task every five minutes.
- The task requests a delayed closed window and uses a ten-minute overlap.
- Duplicate observation IDs from the overlap are suppressed using the checkpoint.
- Missing observation IDs fail closed as malformed telemetry.
- The watermark advances only after source completeness, main export, and heartbeat
  success.
- DynamoDB conditional version writes prevent stale checkpoint overwrite.
- Export and checkpoint are not atomic; delivery is explicitly **at-least-once**.
- Scheduler retry is bounded to two attempts and a 15-minute event age.

## Files

| File | Purpose |
|---|---|
| `../Dockerfile` | Python 3.12 image; non-root runtime; package with AWS extra |
| `../docker-compose.yml` | Local-only application + collector smoke topology |
| `otel-collector-config.yaml` | Production/shared collector example: OTLP receiver → Datadog |
| `otel-collector-config.local.yaml` | Local Compose collector: OTLP receiver → debug output |
| `ecs-task-def.json` | Production Fargate task: application container only |
| `eventbridge-schedule.json` | Five-minute EventBridge Scheduler target |

## Secrets and IAM

The task receives `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` from AWS Secrets
Manager. The shared collector deployment receives `DD_API_KEY`; it is intentionally not
present in the application task definition. The application task role needs only:

- `dynamodb:GetItem` and conditional `dynamodb:PutItem` on the checkpoint table;
- `secretsmanager:GetSecretValue` for the two Langfuse secrets;
- CloudWatch Logs permissions normally supplied through the ECS execution role.

Use a VPC endpoint or controlled egress for DynamoDB, Secrets Manager, Langfuse, and the
collector. Resolve placeholders such as `<ACCOUNT_ID>`, subnet IDs, security groups, and
collector host through IaC.

## Local smoke test

```bash
docker compose up --build
```

The application reads `data/sample_traces.json` and posts OTLP/HTTP to the local
collector. Compose uses `otel-collector-config.local.yaml`, which writes received metrics through
the collector `debug` exporter and requires no Datadog key. The production/shared
example remains separate in `otel-collector-config.yaml`.

## Pre-deployment gates

1. Run `ruff check .`, `ruff format --check .`, `mypy src`, and `pytest -q`.
2. Build and scan the image; deploy by digest, not a mutable tag.
3. Validate the task definition against the target AWS account and region.
4. Run a collector contract test and a Langfuse pagination/volume soak test.
5. Verify EventBridge, ECS task-failure, no-data, export-health, and checkpoint-conflict
   alarms before enabling the schedule.
