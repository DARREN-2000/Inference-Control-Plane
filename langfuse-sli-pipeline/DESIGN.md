# AI Platform Design

**Author:** Morris Darren Babu · **Scope:** Task 1 and context for the implemented Option D

**Reading guide:** This Markdown file is designed to print as four pages. The data work is in [`docs/DATA_ANALYSIS.md`](docs/DATA_ANALYSIS.md). Detailed formulas and metric notes are in [`docs/DESIGN_APPENDIX.md`](docs/DESIGN_APPENDIX.md).

## Page 1 of 4: Context, priorities, and cost governance

### Executive summary

Six teams use a shared LiteLLM gateway on ECS Fargate. Anthropic traffic goes through Bedrock in Frankfurt. One approved external provider is available under a Zero Data Retention agreement. Langfuse stores request traces. Postgres stores keys and spend data. Datadog receives aggregate metrics only.

The supplied data points to three immediate problems. Known spend is **$36,468.89 over 30 days**. Daily spend rises from **$589.25** before 17 November to **$1,931.49** afterwards, a **3.28× increase**. DevAgent accounts for **55.3%** of spend. There is also a personal production key with no team owner, plus one high-volume KYC row with missing cost.

I separate the platform into three parts:

1. **Control plane:** admission, policy, routing, budgets, and tool authorization.
2. **Telemetry plane:** Langfuse remains the trace source. Option D produces safe operational metrics.
3. **Governance plane:** a workload registry defines ownership, data rules, budgets, models, and tool access.

**Assumptions:** the finance feed may be 24 hours late; Langfuse exposes the public Observations API; one scheduled worker owns each time window; and raw prompts or responses must never enter Datadog.

### Cost governance

The daily CSV is useful for reconciliation. It is too stale for enforcement. The gateway should keep live per-key and per-team token and cost counters in Redis or Postgres. It should check those counters before each provider call.

| Budget state | Default action | Customer-facing or regulated routes |
|---|---|---|
| <75% | Allow | Allow |
| 75–90% | Notify the owner and Platform | Notify only |
| 90–100% | Reduce concurrency; use an approved downgrade | Escalate; never downgrade silently |
| ≥100% | Queue or block non-critical batch and dev traffic | Require an explicit owner decision |

Each route also needs input and output limits, a maximum agent step count, per-key RPS limits, and concurrency caps. These controls can stop one bad request or loop before it becomes expensive.

DigestBot and Research can tolerate a cheaper model or a delay. AdvisorChat and KYC are different. A model change can affect refusals, accuracy, and audit evidence, so it needs prior product and compliance approval.

The first actions are simple: explain the 17 November jump, replace the personal key, assign an owner to every key, and reconcile live counters against finance. **Option B** would enforce budget decisions in the gateway. **Option D** measures the result but never blocks traffic.

<div style="page-break-after: always;"></div>

## Page 2 of 4: Data governance, agent safety, and self-service

### Data governance

Routing should follow the workload's data class, not a model alias typed by a developer. Each workload registration should list its owner, environment, data class, retention period, approved providers and regions, budget, and model set.

The gateway evaluates that policy. It also records the model version, routing decision, prompt-template version, and request configuration. This gives us a clear audit trail.

AdvisorChat and KYC should use approved in-region paths by default. The external provider is only allowed when both the ZDR agreement and the workload policy permit it. Raw prompts and outputs stay in Langfuse and ClickHouse. Access is scoped, data is encrypted, and retention is defined. Datadog only receives aggregates. Secrets come from Secrets Manager. Workload identities are scoped to one environment.

### Agentic safety

DevAgent is the largest spender and can write through MCP tools. That gives it the highest combined cost and operational risk.

Every tool should be marked as **read**, **write**, or **destructive**. The check belongs between the proposed tool call and its execution.

- Read tools use scoped identities and normal audit logging.
- Write tools need clear resource scopes and a per-session operation budget.
- Destructive actions need approval and a full actor, tool, and resource record.
- Every session has time, token, step, and tool-call limits. It can also be stopped or reset.

Agents get a separate identity for each workload and environment. Shared privileged keys are not allowed. Prompt content is treated as untrusted input. It cannot expand tool permissions. **Option A** would provide this control in the action path. Option D only observes the resulting errors, latency, and token patterns.

### Self-service paved road

Onboarding starts with a pull request to a small workload registry. CI checks for a team owner, budget owner, data class, provider and region policy, retention period, and service identity. It also checks IAM scope, metric dimensions, route names, model names, and destructive tool approvals.

After merge, automation creates the policy and registers the default dashboards, alerts, and budget rules. This setup would have blocked the personal key found in the data. It would also stop an unregistered route from creating unbounded Datadog series.

Teams own quality, budget, and route SLOs. Platform owns the runtime and defaults. Security and the DPO review privileged tools and data egress. Finance owns the budget envelope and reconciliation source. **Option C** would implement this workflow.

<div style="page-break-after: always;"></div>

## Page 3 of 4: Observability and implemented Option D

### Architecture and privacy boundary

Option D reads a delayed, closed window from Langfuse. It parses each record, removes unsafe fields, aggregates the safe values, and sends OTLP metrics to a shared collector. It stores only a watermark and recent observation IDs. It does not create another trace store.

The job is outside the request path. If it fails, dashboards become stale, but customer traffic keeps running.

Only governed values can become labels: `team`, `route`, `model_family`, `env`, `outcome`, `error_category`, `provider_region`, and a bounded pipeline `dimension`. Unknown values fold to `other`. A blank team becomes `unattributed`. Before export, one registry checks the metric name, type, unit, dimension set, keys, and values. Prompts, outputs, user IDs, key aliases, trace IDs, and free-text provider messages cannot reach Datadog.

### SLIs and alerting

| Signal | Purpose |
|---|---|
| Latency and TTFT | Histograms for p50, p95, and p99; TTFT only for successful streaming calls |
| Reliability | Request and error counters with bounded outcomes and categories |
| Cost | USD, requests, tokens, cache use, missing cost, and invalid cost |
| Agent efficiency | Completion-to-input ratio and empty completions |
| Quality proxy | Completion-length anomaly by route; investigation only |
| Telemetry trust | Source and export health, freshness, bad records, truncation, checkpoint conflict, and series count |

A sustained customer-facing SLO burn should page. The supplied monitors use paired fast and slow windows to reduce noise. Cost drift and quality proxies should create an investigation ticket. Source failure, export failure, or stale data should page when it creates a real monitoring blind spot.

### Correctness and scale

Aggregation is single-pass. Histograms and quality samples use bounded memory. The record cap also bounds the exact de-duplication set. A record with no ID is rejected because it cannot be processed safely with delta metrics.

Pagination checks response shape and detects repeated cursors, repeated pages, and incomplete continuation pages. Transient failures get bounded retries. An incomplete read is never checkpointed. A grace period catches most late arrivals, and the overlap window removes ordinary re-read duplicates.

Production uses DynamoDB conditional checkpoint writes. The file store is for local use only. Delivery is **at-least-once** because export and checkpoint are separate operations. One scheduled task owns each window, and a checkpoint conflict fails the run. A pre-export lease or backend idempotency key would be the next hardening step.

Cardinality is controlled by small, explicit vocabularies. CI checks the ceiling and the monitor threshold. OTLP uses strict JSON, a deadline, and bounded retries. The container runs as a non-root user with a read-only filesystem.

<div style="page-break-after: always;"></div>

## Page 4 of 4: Model sourcing, roadmap, alternatives, and decisions

### Model sourcing

Managed models should remain the default. Known spend annualizes to about **$438k**. The latest run-rate is closer to **$705k**. Most of that spend is concentrated in two frontier model families.

Self-hosting is not automatically cheaper. For a rough comparison, assume an eight-A100 node costs **$25–33 per hour**. Running it all month costs about **$18–24k** before engineering and redundancy (`730 hours × $25–33`). At 60% useful utilization, the effective compute cost is about **$30–40k per fully used month**. Current total spend is $36.5k, but the low-risk batch workloads are only about $2.3k. DevAgent is about $20.2k, but an open model has not passed its quality or tool-use checks. The current workload mix does not justify self-hosting.

I would pilot a Bedrock-managed open-weight model for DigestBot and Research. These are lower-risk batch workloads. The pilot should use offline quality checks and a small online canary. AdvisorChat, KYC, and DevAgent should stay on frontier models until task-level evidence supports a change.

I would reconsider self-hosting when one workload is large and steady enough to keep GPUs above roughly 60% utilization, and when an open model passes its quality and compliance checks.

### Six-month direction

1. **Month 0–1:** deploy Option D, explain the spend jump, replace the personal key, and add live counters.
2. **Month 1–2:** implement Option B using those counters and reconcile it with finance data.
3. **Month 2–4:** deliver the Option C registry and move existing workloads onto it.
4. **Month 3–5:** add Option A controls for DevAgent, including approvals and session budgets.
5. **Month 4–6:** run the open-weight pilot and add a durable quality baseline.

Success is easy to state. Every workload has an owner, policy, and budget. Personal production keys are gone. Telemetry is fresh and safe. Pages are based on SLO impact. Model changes have clear cost and quality evidence.

### Rejected alternatives

- **Direct ClickHouse reads:** they couple the job to Langfuse internals.
- **A second trace store:** it duplicates PII and creates another retention problem.
- **Per-instance percentiles:** they cannot be combined correctly; histogram buckets can.
- **LLM-as-judge in extraction:** it adds cost and delay. Semantic evaluation belongs in a sampled background job.
- **Immediate self-hosting:** we do not have enough utilization or quality evidence.
- **An exactly-once claim:** it would be false without an atomic sink and checkpoint.

### Open decisions

- **Finance and leadership:** What caused the 17 November jump, and is the new run-rate approved?
- **Legal and DPO:** What is the exact ZDR scope, and how long may PII traces remain?
- **Product:** Which routes may use a cheaper model, and what quality check is required?
- **Security:** Which tool actions need approval, and what budgets apply?
- **Platform:** What are the production API limits, grace period, and duplicate-delivery requirements?

**Evidence:** [`docs/DATA_ANALYSIS.md`](docs/DATA_ANALYSIS.md) · **Engineering detail:** [`docs/DESIGN_APPENDIX.md`](docs/DESIGN_APPENDIX.md) · **Architecture:** [`docs/architecture.md`](docs/architecture.md)
