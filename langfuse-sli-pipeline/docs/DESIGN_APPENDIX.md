# Design appendix - detailed derivations

The reasoning and exact constants behind the choices summarised in
[`DESIGN.md`](../DESIGN.md). Everything here is drawn directly from the code
(`config.py`, `quality.py`, `governance.py`, `sli.py`) and the checked-in monitors,
so the numbers are authoritative, not illustrative.

- Design overview & decisions -> [`DESIGN.md`](../DESIGN.md)
- Data evidence base (F1-F11) -> [`DATA_ANALYSIS.md`](DATA_ANALYSIS.md)
- Commands and operating notes -> [`../README.md`](../README.md)
- Target-state diagram -> [`architecture.md`](architecture.md)

---

## A. Completion-length anomaly: robust z-score (median + MAD)

**Where:** `quality.py`. **Config:** `AnomalyConfig(min_sample=30, threshold=3.5, baseline_grouping="route")`.

The standard z-score `(x - mean) / stdev` is not robust: a single runaway
completion (F1) poisons both the mean and the standard deviation, masking the
very outliers we want to catch. We use the **Iglewicz-Hoaglin modified z-score**
built on the median and the Median Absolute Deviation (MAD):

```
MAD          = median(|x_i - median(x)|)
robust_z(x)  = 0.6745 * (x - median) / MAD
```

- **0.6745** is the 0.75 quantile of the standard normal (i.e. `1 / 1.4826`).
  Since `MAD * 1.4826 -> sigma` for normal data, multiplying the deviation by
  `0.6745 / MAD` puts the score on the same scale as a classic z-score, so the
  familiar `|z| >= 3.5` threshold is meaningful.
- **Threshold 3.5** is the Iglewicz-Hoaglin recommended cut-off for the modified
  z-score. Configurable via `AnomalyConfig.threshold`.
- **min_sample = 30**: below this the group is in **cold start** and is *not*
  scored (returns `cold_start`, no metric) - small baselines make the MAD
  unstable and would generate false anomalies.

**Degenerate baselines are handled explicitly (no divide-by-zero):**
1. If `MAD == 0` (more than half the samples identical), fall back to the mean
   absolute deviation scaled by **1.2533** (`meanAD * 1.2533 -> sigma` for normal
   data): `z = (x - median) / (1.2533 * meanAD)`.
2. If both MAD and meanAD are 0 (a **perfectly constant** baseline), any
   deviation from the median is flagged (`degenerate_constant_baseline`); a value
   equal to the median is not.

**Avoiding self-inclusion while scaling.** Up to 2,000 samples, `score_group` uses
exact leave-one-out baselines. Above that, deterministic two-fold cross-fitting scores
each half against robust statistics from the other half. A value is never scored against
itself. `QualityAccumulator` keeps at most **50,000** lengths per group via **reservoir
sampling (Algorithm R)**, RNG seeded at **1729** for reproducibility, so a huge
window scores in bounded memory and, below the cap, matches the exact batch path.

**Why it is a counter + gauge, not a "latest z" gauge.** A per-record z-score is
an *event*. We emit a per-window **counter** of breaches
(`gateway.quality.completion_length_anomalies`) plus a **gauge** of the window's
maximum magnitude (`...max_zscore`). A single last-write-wins gauge would be
order-dependent and hide every record but the last. The signal is
**investigation-only** - never an automated control - which also bounds the blast
radius of baseline poisoning by a compromised source.

> Token-length distributions are right-skewed, so the normal-scaled robust z is a
> screening heuristic, not a calibrated probability. A log transform or empirical
> per-route quantiles would refine it; investigation-only usage keeps it safe.

---

## B. Streaming histograms and percentile interpolation

**Where:** `sli.py` (`_HistAcc`, `_hist_percentile`). **Buckets (ms):**
`50, 100, 200, 300, 500, 750, 1000, 1500, 2000, 3000, 5000, 10000, 30000`.

We emit **explicit-bucket histograms** and let the backend compute percentiles.
The reason is statistical: **you cannot average pre-computed percentiles across
instances or windows** - the p95 of two hosts is not the mean of their p95s.
Emitting buckets lets Datadog/OTel compute a correct global p50/p95/p99 from the
summed bucket counts.

- **Bucket rule is `v <= b`**, matching the OpenTelemetry explicit-bucket `le`
  ("less than or equal") convention, so our buckets line up with OTLP semantics.
- Each accumulator keeps one integer per bucket plus `sum`, `count`, `min`,
  `max` - **O(buckets x series)** memory regardless of trace volume, folded one
  observation at a time. This is the whole point of streaming histograms.
- **Local display percentiles** (`p50/p95/p99` in console output) are estimated
  by **linear interpolation within the containing bucket**: find the bucket where
  the cumulative count crosses `q% * count`, then interpolate between its edges
  (lower edge of the first bucket assumed 0, valid for non-negative latencies).
  These are labelled **approximate**; the authoritative percentiles are computed
  backend-side from the emitted buckets. A value landing in the `+Inf` overflow
  bucket is reported as the observed `max`.

---

## C. Cardinality budget - exact derivation

**Where:** `governance.py` (`estimated_max_series`, `estimated_max_total_series`).

Governed vocabulary sizes (each includes its fold token):

| Dimension | Values | Size |
|---|---|---|
| team | AdvisorChat, KYC, DevAgent, DigestBot, Research, Marketing, other, unattributed | 8 |
| route | advisorchat-turn, digestbot-summary, devagent-task, other | 4 |
| model_family | claude-sonnet/-haiku/-opus, gpt-5, gpt-5-mini, gpt-4o, other | 7 |
| env | prod, staging, dev, other | 4 |
| outcome | success, error | 2 |
| error_category | throttling, timeout, provider_error, auth, invalid_request, content_filter, unknown | 7 |
| provider_region | bedrock_eu, bedrock_us, external_zdr, other | 4 |

**Primary grouping** (latency + TTFT): `team x route x model_family x env`
= `8 x 4 x 7 x 4 = 896` series (`estimated_max_series()`).

**Worst-case total metric points per window** (`estimated_max_total_series()`):

```
duration + ttft   = 2 x 896                              = 1,792
request.count     = 896 x outcome(2)                     = 1,792
request.errors    = 896 x error_category(7)              = 6,272
cost family       = (team x route x model_family x provider_region) x 9 kinds
                  = (8 x 4 x 7 x 4) x 9 = 896 x 9        = 8,064
                                                   TOTAL = 17,920
```

(The 9 cost-family point kinds: `cost.usd`, `cost.request_count`, `tokens.input`,
`tokens.output`, `cache.read_tokens`, `cache.hit_count`, `cost.records_missing`,
`cost.records_invalid`, `tokens.completion_ratio`.
The `tokens.completion_ratio` gauge shares the same grouping.)

The `gateway.pipeline.series_emitted` tripwire critical threshold is set at
**18,000** - just above the 17,920 ceiling (`> ceiling`, `< 2 x ceiling`, asserted
by `test_monitors.py`). Any window above it is a dimension-explosion regression,
not legitimate traffic. The test derives the ceiling from the registry and fails if
the checked-in monitor is no longer above it, forcing a reviewed monitor update when
the vocabulary expands.

---

## D. Multi-window burn-rate alerting

**Where:** `monitors/datadog_monitors.json`. Based on the Google SRE Workbook
multi-window, multi-burn-rate method on the AdvisorChat 30-day availability SLO.

| Severity | Long / short window | Burn rate | Budget consumed | Action |
|---|---|---|---|---|
| Page (fast) | 1h / 5m | **> 14.4x** | ~2% of 30-day budget in 1h (exhausted in ~2 days) | `@pagerduty-advisorchat` |
| Ticket (slow) | 6h / 30m | **> 6x** | ~5% of budget over 6h | `@slack-advisorchat-oncall` |

- **14.4** is the canonical fast-burn factor: at 14.4x, a 30-day budget is spent
  in `30 / 14.4 ~= 2.08` days, i.e. ~2% in one hour - fast enough to page.
- Requiring **both** the long and short window to breach removes single-spike
  false pages while still catching a genuine sustained burn, and the short window
  makes recovery de-alert quickly.
- Thresholds are **starting points**, tuned against the SLOs agreed per team.

---

## E. OTLP / JSON encoding decisions

**Where:** `emit/otlp_http.py`, `emit/otel.py`.

- **Delta temporality, per bounded closed window.** Each run emits one window's
  delta - there is no in-process cumulative counter to lose on restart, and
  disjoint windows from multiple workers simply sum backend-side. DELTA sums stay
  monotonic within a window (`isMonotonic = true`). Per-point
  `startTimeUnixNano`/`timeUnixNano` carry the window bounds so the backend
  attributes deltas correctly.
- **Histogram int64 fields** (`count`, `bucketCounts`) are serialized as JSON strings,
  per proto3 JSON mapping. Metric counters and gauges use `asDouble` because the
  internal `MetricPoint.value` contract is numeric and cost counters are fractional.
- **Histograms** carry `explicitBounds` (N boundaries), `bucketCounts` (N+1
  counts, including the `+Inf` overflow), plus `sum`, `count`, `min`, `max` - the
  exact shape the backend needs to recompute percentiles.
- **Resource attribute** `deployment.environment` is set from
  `OTEL_DEPLOYMENT_ENVIRONMENT` on every exported metric.
- **Export health uses a guarded, separate heartbeat call.** `export_success` (1/0)
  is attempted after the main flush. It is not an independent delivery channel;
  backend no-data/task-failure monitoring remains necessary when the collector
  itself is unreachable.

---

## F. SLI / SLO catalogue (reference)

| SLI | Definition | Example SLO |
|---|---|---|
| End-to-end latency | `endTime - startTime`, p50/p95/p99 via histogram buckets | AdvisorChat p95 < 4s |
| TTFT | `completionStartTime - startTime`; **successful streaming only** | AdvisorChat p95 TTFT < 1.5s |
| Error rate | errors / total, by bounded `error_category` | AdvisorChat < 1% sustained |
| Cost | `cost.usd`, `request_count` per team/route/model[/region] | drift alerts, not an SLO |
| Cache economics | `cache.read_tokens`, `cache.hit_count`; hit ratio = hits / `cost.request_count` | efficiency signal |
| Completion:prompt ratio | `tokens.output / tokens.input` per series | runaway-agent alert (> 3), see G |
| Completion-length anomaly | per-window count of robust-z outliers + max-magnitude gauge | investigation only |

TTFT is **excluded** (not recorded as 0) for non-streaming, failed, or
missing-`completionStartTime` requests - a zero would silently improve the metric
during an outage. Failed requests still count toward latency and error rate.

---

## G. Completion:prompt token ratio (runaway-agent signature)

**Where:** `sli.py`; metric `gateway.tokens.completion_ratio` (gauge).

DATA_ANALYSIS.md **F1** found DevAgent emitted more completion than prompt tokens
on 12 of 13 runaway days - the fingerprint of a looping agent. Rather than leave
this as a dashboard-only formula over two counters, we emit the ratio
`output / input` per series as a first-class, alertable gauge (only when
`input > 0`, so there is no divide-by-zero on phantom zero-token rows). The paired
Datadog monitor pages at ratio **> 3** per route. Prevention (step caps,
per-conversation USD budgets, loop detection) lives in the gateway; this service's
job is to make the runaway *visible fast and attributably*.

---

## H. Window semantics & idempotency (summary)

- **Single-writer-per-window**; in-batch dedup handles retries within a window,
  a persisted watermark + bounded seen-set handles cross-run dedup on the trailing
  overlap (surfaced as `duplicate_records` / `cross_run_duplicate_records`).
- **Watermark advances only after a clean export**, so a failed run is retried,
  not skipped. The DynamoDB store guards the checkpoint item with an optimistic
  version counter (conditional write); a race surfaces
  `CheckpointConflict`; because detection follows export, delivery remains at-least-once, never a clobbered watermark.
- **Deferred:** corrective-delta re-emission for observations whose values are
  *updated* after a window closes (current policy keeps the first-seen value,
  consistent with in-batch dedup). Called out, not glossed.

The production semantics and residual atomicity limitation are summarized on
page 3 of `DESIGN.md`; runnable configuration is in `README.md`.
