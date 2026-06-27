# Monitoring & Observability

To confidently run AI workloads in production, you need deep visibility into request lifecycles, latency, and token consumption. Laminar provides a comprehensive observability suite out-of-the-box.

## 1. Prometheus Metrics

Laminar exposes a `/metrics` endpoint on the API server. This should be scraped by your Prometheus server.

**Key Metrics Exposed:**
- `request_count_total` (Counter): Total requests processed, labeled by `tenant_id`, `model`, and `status_code`.
- `request_latency_seconds` (Histogram): End-to-end proxy latency.
- `upstream_latency_seconds` (Histogram): The time the upstream provider (e.g., OpenAI) took to respond.
- `cache_hits_total` / `cache_misses_total` (Counter): Efficacy of the Redis cache.
- `rate_limit_exceeded_total` (Counter): Number of 429 errors returned.

**Example PromQL (Cache Hit Rate):**
```promql
rate(cache_hits_total[5m]) / (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m]))
```

## 2. OpenTelemetry Tracing (OTLP)

Laminar supports distributed tracing via OpenTelemetry. This is crucial for visualizing the "waterfall" of an AI request, especially when fallback routing is triggered.

**Configuration:**
Set the `OTLP_ENDPOINT` environment variable to point to your collector (e.g., Jaeger, Honeycomb, Datadog Agent).
```bash
OTLP_ENDPOINT=http://otel-collector:4317
```

**Trace Anatomy:**
A single request trace will include spans for:
- API Key Validation
- Rate Limit check
- Cache lookup
- HTTP Client connection to Provider
- First Token response
- Stream completion

## 3. Structured Logging

By default, Laminar outputs JSON structured logs to `stdout` in production environments (`ENVIRONMENT=production`).

**Log Format:**
```json
{
  "timestamp": "2024-06-27T12:00:00Z",
  "level": "INFO",
  "request_id": "req_12345",
  "tenant_id": "tenant_abc",
  "action": "generate_completion",
  "model": "gpt-4o",
  "latency_ms": 1250,
  "tokens": 450,
  "cache_hit": false
}
```
These logs should be ingested by your logging platform (e.g., Elasticsearch, Datadog, Splunk) for querying and alerting.

## 4. Usage Logging (PostgreSQL)

While Prometheus handles ephemeral metrics, Laminar writes persistent usage data to PostgreSQL. This data is used by the Dashboard to display historical charts and calculate billing.

Data stored includes:
- Timestamp
- Tenant ID & User ID
- Requested Model vs. Provided Model (if fallback occurred)
- Prompt Tokens, Completion Tokens, Total Tokens
- Estimated Cost

*Note: Payloads (prompts and completions) are NOT logged by default to protect PII. To enable payload logging for debugging, set `LOG_PAYLOADS=true`.*
