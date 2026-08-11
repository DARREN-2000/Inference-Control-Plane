# Monitors as code

`datadog_monitors.json` defines the SLO burn-rate alerts and the **Telemetry
Trust Contract (TTC)** / **Metric Governance Contract (MGC)** meta-monitors as
declarative Datadog monitor definitions.

These are **example definitions**, validated by `tests/test_monitors.py` (they
parse as JSON and every query references a metric this service actually emits).
They are intentionally **not applied** from this repo - in production they would
be managed by the platform Terraform stack (see below), reviewed like any other
infrastructure change.

## Two layers of monitoring

1. **Workload SLOs** - what users feel: AdvisorChat p95 latency, gateway error
   ratio, plus a **multi-window burn-rate pair** on the AdvisorChat availability
   SLO (fast 1h/5m at 14.4x pages; slow 6h/30m at 6x tickets) so a brief blip
   does not page while a sustained budget burn does. These burn an error budget.
   (The burn-rate monitors reference an SLO id placeholder,
   `REPLACE_WITH_ADVISORCHAT_AVAILABILITY_SLO_ID`, resolved at apply time.)
2. **Telemetry Trust / Governance meta-monitors** - whether the *observability
   itself* is trustworthy: freshness lag, pipeline stalled (no-data blind spot),
   export health, cost completeness, unknown-dimension (ungoverned) spikes, and
   cardinality budget. A green workload dashboard is only meaningful if these
   are also green.

The blind-spot monitors (`records_read` no-data, `export_success`) deliberately
set `notify_no_data: true`: on a regulated platform, *silence must page*.

## Terraform integration (illustrative - not applied here)

```hcl
resource "datadog_monitor_json" "gateway_sli" {
  for_each = { for m in jsondecode(file("${path.module}/datadog_monitors.json")) : m.name => m }
  monitor  = jsonencode(each.value)
}
```

Thresholds shown are starting points; they would be tuned against the
service-level objectives agreed with each team (AdvisorChat latency, FinOps cost
completeness, KYC auditability).
