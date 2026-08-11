# Data Analysis: Findings from `spend_30d.csv` and `data/sample_traces.json`

> Purpose: evidence base for the design document. Every design decision below is traceable to a
> concrete observation in the supplied data, not to assumption. Numbers were computed with pandas;
> the analysis scripts are reproducible.

## 0. Scope and data quality summary

| File | Shape | Notes |
|------|-------|-------|
| `spend_30d.csv` | 151 rows, 30 days (2025-11-01 → 2025-11-30), 6 teams, 6 models | Per day / per key / per model spend |
| `data/sample_traces.json` | 5 `GENERATION` observations | Supplied artifact; AdvisorChat + DigestBot; includes 1 error trace |
| `data/demo_runaway_traces.json` | 6 `GENERATION` observations | Supplied fixture plus 1 clearly labelled synthetic DevAgent runaway record |

**Total 30-day spend: `$36,468.89` ≈ `$36.5k/month` ≈ `$438k/year` run-rate.**

---

## 1. Spend breakdown

### Per team

| Team | Cost (USD) | % of bill | Requests | $/1k req |
|------|-----------:|----------:|---------:|---------:|
| DevAgent | 20,153.30 | 55.3% | 278,074 | 72.48 |
| AdvisorChat | 9,179.65 | 25.2% | 708,601 | 12.96 |
| KYC | 2,794.80 | 7.7% | 194,332 | 14.38 |
| **(untagged / personal)** | 2,008.29 | 5.5% | 55,888 | 35.93 |
| DigestBot | 1,990.19 | 5.5% | 301,981 | 6.59 |
| Research | 335.12 | 0.9% | 14,909 | 22.48 |
| Marketing | 7.54 | 0.0% | 766 | 9.84 |

### Per model

| Model | Cost (USD) | % | Requests | Blended $/1M tok |
|-------|-----------:|--:|---------:|-----------------:|
| gpt-5.4 | 22,156.26 | 60.8% | 333,682 | 7.96 |
| claude-sonnet-4-6 | 12,263.03 | 33.6% | 915,701 | 4.89 |
| claude-haiku-4-5 | 1,990.19 | 5.5% | 301,981 | 1.41 |
| gpt-4o | 43.32 | 0.1% | 2,379 | 3.92 |
| claude-opus-4-7 | 8.55 | 0.0% | 42 | 26.23 |
| gpt-5.4-mini | 7.54 | 0.0% | 766 | 2.87 |

**Two models = 94% of spend.** claude-haiku is ~12x cheaper per token than gpt-5.4.

---

## 2. Critical findings

### F1: DevAgent cost runaway

This finding comes from `spend_30d.csv`. The supplied trace fixture has no DevAgent
observation, so it cannot reproduce the ratio alert by itself. The separate
`data/demo_runaway_traces.json` file adds one synthetic record with a 4.2 ratio. It
exists only to demonstrate the monitor and is not used as evidence for the finding.
DevAgent is **55% of the entire bill ($20,153)** on only ~278k requests. Through Nov 18 it ran
~$120–160/day. **From Nov 19 onward it explodes to $864 → $1,826/day**, and on nearly every one of those
days **completion tokens exceed prompt tokens** (12 of the 13 days from Nov 19; Nov 20 is the lone exception): the signature of an agent stuck in a
tool-call / self-response loop.

| Date | DevAgent cost | prompt→completion |
|------|--------------:|-------------------|
| ≤ Nov 18 | ~$120–160/day | completion << prompt (normal) |
| Nov 19 | 864.32 | 48.4M → 49.6M ⚠️ |
| Nov 21 | 1,603.93 | 80.4M → 93.5M ⚠️ |
| Nov 24 | 1,826.88 | 77.0M → 109.0M ⚠️ |
| Nov 26 | 1,553.31 | 67.4M → 92.3M ⚠️ |

This is exactly the *"stop a runaway request before it becomes a runaway invoice"* scenario in the
brief: present in the data. **This motivates Task 2 Option B (tiered budget + graceful downgrade)
and/or Option A (destructive-action / loop control).**

### F2: Shadow / personal key bypassing governance
`key-personal-mhuber` (a **personal**, non-team key) ran gpt-5.4 and burned **~$2,003 in 3 days**
($674 / $620 / $710) with **no team attribution**. Personal keys that escape team tagging and
budgets are a direct cost- and data-governance hole. **→ Governance: no un-tagged / personal keys
on the sanctioned path.**

### F3: ~5.5% of spend is unattributable
Several rows have a **blank/null `team`** (the personal key above + a stray `key-research-shared`
row). You cannot enforce a per-team budget on spend you cannot attribute. **→ Self-service
onboarding must make `team` a mandatory, validated tag.**

### F4: The spend data itself is dirty (proof that staleness is real)
- **Null `cost_usd`**: KYC, Nov 17: cost silently missing.
- **Phantom charge**: DigestBot, Nov 5: **$12.40 with 0 requests and 0 tokens**.

These prove billing/reconciliation lag and gaps are real → a budget enforcer must **tolerate stale /
incomplete spend data** rather than trust it blindly. **→ Directly answers Option B's staleness
question.**

### F5: Model-routing leakage on the most sensitive workload
AdvisorChat (customer-facing, handles customer data) **intermittently routes to `gpt-4o`** (5 days,
~$43). If gpt-4o is not on the sanctioned Bedrock-Frankfurt / ZDR path, that is a data-residency
risk. This is the *"which model alias a team happens to call"* problem: enforcement must be
**structural, not alias-dependent**. **→ Data governance.**

### F6: Strong weekly seasonality → flat thresholds misfire
AdvisorChat drops from ~35k requests on weekdays to ~8k on weekends (visible every Sat/Sun).
Anomaly and budget alerting must be **day-of-week aware** or it will page every Monday and miss
weekend anomalies. **→ Observability / alerting design.**

### F7: Cost concentration → model-sourcing leverage
gpt-5.4 (external provider) is the cost center: **60.8% of spend at ~$7.96/1M tokens.** This is the
"show your math" anchor for the model-sourcing question (stay / add Bedrock open-weight / self-host).

---

## 3. Trace findings (observability + governance)

### F8: PII stored in plaintext in self-hosted Langfuse
Every AdvisorChat trace is tagged `data_class: pii_sensitive` yet stores the **full user prompt and
model answer verbatim**. Retention/redaction is not structural. **→ Redact/hash input+output at the
gateway for PII-classed traffic; define a retention TTL.**

### F9: Bedrock throttling is a live reliability signal
One observation is an `ERROR`:
`ThrottlingException: Rate exceeded for anthropic.claude-sonnet-4 in eu-central-1` (retryable).
Frankfurt capacity is a real risk. **→ Provider error rate is a page-worthy SLI; argue for retry /
cross-region fallback.**

### F10: Latency is spiky for a latency-sensitive workload
Across the small sample: end-to-end **p95 ≈ 5.4s**, and one **time-to-first-token = 3.56s**: high
for customer-facing chat. **→ TTFT and end-to-end p95 are the obvious SLO candidates for Option D.**

### F11: SLIs are derivable without duplicating raw traces
Each trace carries `usageDetails` + `costDetails`, so cost-per-route, latency percentiles, TTFT,
error rate, and a completion-length quality signal can be computed straight from the trace stream.
exactly what Option D asks, **no second storage layer**. Traces also expose
`cache_read_input_tokens`, so **cache-hit-rate** is a free, high-value SLI and cost lever.

---

## 4. How findings map to the design document

| Finding | Design section it drives |
|---------|--------------------------|
| F1 runaway, F4 staleness, F7 concentration | Cost governance + Task 2 (Option B) |
| F2 shadow key, F3 untagged, F5 gpt-4o leakage, F8 PII | Data governance |
| F1 loop, F2 write-capable agent | Agentic safety (Option A alternative) |
| F6 seasonality, F9 throttling, F10 latency, F11 SLIs | Observability (SLI/SLO, alert vs. page) |
| F3 mandatory tags | Self-service onboarding validations |
| F7 unit economics | Model sourcing |

---

*Generated as the evidence base for the Scalable Capital AI Platform Engineer case study.*
