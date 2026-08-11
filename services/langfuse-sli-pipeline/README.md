# Langfuse SLI Telemetry Sidecar

This sidecar service provides privacy-safe, bounded-cardinality operational SLIs (Service Level Indicators) for the Inference Control Plane gateway. It derives metrics dynamically from Langfuse request-level traces.

## Overview

A standalone observability job that reads traces produced by the AI Gateway, calculating:
- Latency (TTFT, Total Time)
- Reliability (Error Rates)
- Cost (Token ratios)
- Prompt/Completion lengths

All without a secondary trace store, without sending PII/Prompts to external telemetry dashboards, and fully compatible with OpenTelemetry (OTLP).

## Deployment

This sidecar runs alongside the main FastAPI Gateway. It uses a pull-based scheduled mechanism to ingest new completed trace windows from Langfuse, processes the aggregates in-memory, and pushes the metrics downstream (e.g. to Prometheus/Datadog via OTel Collector).

```yaml
gateway-sli:
  build:
    context: ./services/langfuse-sli-pipeline
    dockerfile: Dockerfile
  environment:
    - LANGFUSE_PUBLIC_KEY=${LANGFUSE_PUBLIC_KEY}
    - LANGFUSE_SECRET_KEY=${LANGFUSE_SECRET_KEY}
```

## Telemetry Export

The sidecar supports emitting metrics via OTLP/HTTP. Output goes directly to the OpenTelemetry Collector:

```bash
# OTLP/HTTP Output
python -m src.run --source api --emit otlp-http --otlp-endpoint http://otel-collector:4318
```
