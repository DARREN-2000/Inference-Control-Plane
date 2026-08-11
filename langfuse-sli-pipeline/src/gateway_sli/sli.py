"""Aggregation: turn parsed observations into bounded-cardinality metric points.

Histograms are accumulated in STREAMING form (bucket counts + sum + count +
min/max) so memory is O(buckets x series) regardless of trace volume - the whole
point of emitting explicit-bucket histograms and letting the backend compute
cross-instance percentiles. Local display percentiles are interpolated from the
same buckets and are therefore approximate (labeled as such).

The :class:`Aggregator` folds observations one at a time so a large window can be
streamed through with a bounded footprint; :func:`aggregate` is a thin batch
wrapper for callers that already hold the full list (unchanged public contract).

Workload metrics emitted:
  gateway.request.duration    histogram(ms)  team,route,model_family,env
  gateway.request.ttft        histogram(ms)  team,route,model_family,env
  gateway.request.count       counter        + outcome(success|error)
  gateway.request.errors      counter        + error_category
  gateway.cost.usd            counter(USD)   team,route,model_family[,provider_region]
  gateway.cost.request_count  counter        (same dims)
  gateway.cost.records_missing counter       (same dims)
  gateway.tokens.input/output counter        (same dims)
  gateway.cache.read_tokens   counter        (same dims; only when cache hits > 0)
  gateway.cache.hit_count     counter        (same dims; requests served cached tokens)
  gateway.tokens.completion_ratio gauge    (same dims; out/in - runaway signature, F1)

Telemetry-trust signals emitted here (the rest live in pipeline.py):
  gateway.pipeline.malformed_records  counter (no dims)
  gateway.pipeline.duplicate_records  counter (no dims)
  gateway.pipeline.unknown_dimension  counter (dimension=<which governed dim folded>)
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from . import normalize as nz
from .config import Config
from .models import Observation


@dataclass
class MetricPoint:
    name: str
    type: str  # "histogram" | "counter" | "gauge"
    unit: str
    dims: dict[str, str]
    value: float | None = None
    histogram: dict | None = None


def _percentile(values: list[float], q: float) -> float | None:
    """Linear-interpolation percentile (type 7) over an in-memory list. q in
    [0, 100]. Retained as a utility and for exact-percentile unit tests; the
    aggregation path uses the streaming, bucket-based estimator below.
    """
    if not values:
        return None
    s = sorted(values)
    if len(s) == 1:
        return s[0]
    rank = (q / 100.0) * (len(s) - 1)
    lo = int(rank)
    hi = min(lo + 1, len(s) - 1)
    frac = rank - lo
    return s[lo] + (s[hi] - s[lo]) * frac


class _HistAcc:
    """Streaming histogram accumulator. Bounded memory: one integer per bucket
    plus running sum/count/min/max. No per-observation retention.
    """

    __slots__ = ("bounds", "counts", "sum", "count", "min", "max")

    def __init__(self, bounds: tuple[float, ...]) -> None:
        self.bounds = bounds
        self.counts: dict = {b: 0 for b in bounds}
        self.counts["inf"] = 0
        self.sum = 0.0
        self.count = 0
        self.min: float | None = None
        self.max: float | None = None

    def add(self, v: float) -> None:
        self.count += 1
        self.sum += v
        self.min = v if self.min is None or v < self.min else self.min
        self.max = v if self.max is None or v > self.max else self.max
        for b in self.bounds:
            if v <= b:
                self.counts[b] += 1
                return
        self.counts["inf"] += 1


def _hist_percentile(acc: _HistAcc, q: float) -> float | None:
    """Percentile estimated from bucket counts via linear interpolation within
    the containing bucket. Approximate by construction; the authoritative
    percentile is computed backend-side from the emitted buckets.
    """
    if acc.count == 0:
        return None
    if acc.count == 1:
        return acc.min
    target = (q / 100.0) * acc.count
    cum = 0.0
    # Tighten the open-ended histogram edges with the observed min/max. This
    # avoids inventing a zero lower bound for the first non-empty bucket while
    # retaining bounded memory. Values inside a bucket remain approximate.
    prev = acc.min if acc.min is not None else 0.0
    for b in acc.bounds:
        c = acc.counts[b]
        if c > 0 and cum + c >= target:
            frac = (target - cum) / c
            lower = max(prev, acc.min) if cum == 0 and acc.min is not None else prev
            upper = min(b, acc.max) if acc.max is not None else b
            return lower + (max(lower, upper) - lower) * frac
        cum += c
        prev = b
    # Falls in the overflow (+Inf) bucket: best estimate is the observed max.
    return acc.max if acc.max is not None else prev


def _acc_to_point(name: str, dims: dict[str, str], acc: _HistAcc) -> MetricPoint:
    hist = {
        "bounds": list(acc.bounds),
        "bucket_counts": dict(acc.counts),
        "sum": acc.sum,
        "count": acc.count,
        "min": acc.min,
        "max": acc.max,
        # Convenience percentiles for local display (bucket-approximate); the
        # authoritative cross-instance percentiles are computed backend-side.
        "p50": _hist_percentile(acc, 50),
        "p95": _hist_percentile(acc, 95),
        "p99": _hist_percentile(acc, 99),
    }
    return MetricPoint(name, "histogram", "ms", dims, histogram=hist)


@dataclass
class AggregationStats:
    observations: int = 0
    malformed: int = 0
    duplicates: int = 0
    cross_run_duplicates: int = 0
    errors: int = 0
    ttft_eligible: int = 0
    cost_missing: int = 0
    cost_invalid: int = 0
    records_read: int = 0
    quarantined: int = 0
    export_ok: bool = True
    heartbeat_ok: bool = True
    export_error: str | None = None
    freshness_seconds: float | None = None
    read_truncated: bool = False
    checkpoint_conflict: bool = False
    source_ok: bool = True
    source_error: str | None = None
    unknown_dims: dict = field(default_factory=dict)
    extra: dict = field(default_factory=dict)


class Aggregator:
    """Streaming aggregation. Fold observations one at a time into bounded,
    per-series accumulators, then materialize metric points with :meth:`build`.
    Memory is O(buckets x series), independent of window volume.
    """

    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self._buckets = cfg.latency_buckets_ms
        self.dur: dict = {}
        self.ttft: dict = {}
        self.counts: dict = defaultdict(lambda: {"success": 0, "error": 0})
        self.errcat: dict = defaultdict(int)
        self.cost: dict = defaultdict(
            lambda: {
                "usd": 0.0,
                "count": 0,
                "missing": 0,
                "invalid": 0,
                "in": 0,
                "out": 0,
                "cache_read": 0,
                "cache_hits": 0,
            }
        )
        self.unknown: dict = defaultdict(int)
        self.observations = 0
        self.errors = 0
        self.ttft_eligible = 0
        self.cost_missing = 0
        self.cost_invalid = 0

    def add(self, obs: Observation) -> None:
        self.observations += 1
        pk = nz.primary_dims(obs, self.cfg)
        for dim in nz.folded_dimensions(obs, self.cfg):
            self.unknown[dim] += 1

        if obs.is_error:
            self.counts[pk]["error"] += 1
            self.errors += 1
            self.errcat[(pk, nz.error_category(obs) or "unknown")] += 1
        else:
            self.counts[pk]["success"] += 1

        self.dur.setdefault(pk, _HistAcc(self._buckets)).add(obs.latency_ms)
        t = obs.ttft_ms
        if t is not None:
            self.ttft.setdefault(pk, _HistAcc(self._buckets)).add(t)
            self.ttft_eligible += 1

        prov = nz.provider_region(obs) if self.cfg.include_provider_region else "n/a"
        ck = (pk.team, pk.route, pk.model_family, prov)
        entry = self.cost[ck]
        entry["count"] += 1
        entry["in"] += obs.input_tokens
        entry["out"] += obs.output_tokens
        entry["cache_read"] += obs.cache_read_tokens
        if obs.is_cache_hit:
            entry["cache_hits"] += 1
        if obs.cost_invalid:
            entry["invalid"] += 1
            self.cost_invalid += 1
        elif obs.cost_total is None:
            entry["missing"] += 1
            self.cost_missing += 1
        else:
            entry["usd"] += obs.cost_total

    def build(
        self, malformed_count: int, duplicate_count: int = 0
    ) -> tuple[list[MetricPoint], AggregationStats]:
        stats = AggregationStats(
            observations=self.observations,
            malformed=malformed_count,
            duplicates=duplicate_count,
        )
        stats.errors = self.errors
        stats.ttft_eligible = self.ttft_eligible
        stats.cost_missing = self.cost_missing
        stats.cost_invalid = self.cost_invalid
        stats.unknown_dims = dict(self.unknown)

        points: list[MetricPoint] = []
        for name, src in (
            ("gateway.request.duration", self.dur),
            ("gateway.request.ttft", self.ttft),
        ):
            for pk, acc in src.items():
                if acc.count:
                    points.append(_acc_to_point(name, pk.as_dict(), acc))

        for pk, c in self.counts.items():
            points.append(
                MetricPoint(
                    "gateway.request.count",
                    "counter",
                    "1",
                    {**pk.as_dict(), "outcome": "success"},
                    value=c["success"],
                )
            )
            if c["error"]:
                points.append(
                    MetricPoint(
                        "gateway.request.count",
                        "counter",
                        "1",
                        {**pk.as_dict(), "outcome": "error"},
                        value=c["error"],
                    )
                )

        for (pk, cat), n in self.errcat.items():
            points.append(
                MetricPoint(
                    "gateway.request.errors",
                    "counter",
                    "1",
                    {**pk.as_dict(), "error_category": cat},
                    value=n,
                )
            )

        for (team, route_, mf, prov), c in self.cost.items():
            dims = {"team": team, "route": route_, "model_family": mf}
            if self.cfg.include_provider_region:
                dims["provider_region"] = prov
            points.append(
                MetricPoint("gateway.cost.usd", "counter", "USD", dims, value=round(c["usd"], 6))
            )
            points.append(
                MetricPoint("gateway.cost.request_count", "counter", "1", dims, value=c["count"])
            )
            points.append(MetricPoint("gateway.tokens.input", "counter", "1", dims, value=c["in"]))
            points.append(
                MetricPoint("gateway.tokens.output", "counter", "1", dims, value=c["out"])
            )
            # Completion:prompt token ratio - the direct signature of a runaway /
            # looping agent (DATA_ANALYSIS.md F1: DevAgent emitted more completion
            # than prompt tokens on 12 of 13 days). Emitted per series as an
            # alertable gauge so the runaway is a first-class SLI, not a
            # dashboard-only derivation. Guarded against divide-by-zero.
            if c["in"] > 0:
                points.append(
                    MetricPoint(
                        "gateway.tokens.completion_ratio",
                        "gauge",
                        "ratio",
                        dict(dims),
                        value=round(c["out"] / c["in"], 4),
                    )
                )
            # Cache economics: emitted only when the window actually served cached
            # tokens for this series, so cache-free routes add no noise.
            if c["cache_hits"]:
                points.append(
                    MetricPoint(
                        "gateway.cache.read_tokens",
                        "counter",
                        "1",
                        dict(dims),
                        value=c["cache_read"],
                    )
                )
                points.append(
                    MetricPoint(
                        "gateway.cache.hit_count", "counter", "1", dict(dims), value=c["cache_hits"]
                    )
                )
            if c["missing"]:
                points.append(
                    MetricPoint(
                        "gateway.cost.records_missing",
                        "counter",
                        "1",
                        dict(dims),
                        value=c["missing"],
                    )
                )
            if c["invalid"]:
                points.append(
                    MetricPoint(
                        "gateway.cost.records_invalid",
                        "counter",
                        "1",
                        dict(dims),
                        value=c["invalid"],
                    )
                )

        if malformed_count:
            points.append(
                MetricPoint(
                    "gateway.pipeline.malformed_records", "counter", "1", {}, value=malformed_count
                )
            )
        if duplicate_count:
            points.append(
                MetricPoint(
                    "gateway.pipeline.duplicate_records", "counter", "1", {}, value=duplicate_count
                )
            )
        for dim, n in sorted(self.unknown.items()):
            points.append(
                MetricPoint(
                    "gateway.pipeline.unknown_dimension",
                    "counter",
                    "1",
                    {"dimension": dim},
                    value=n,
                )
            )

        return points, stats


def aggregate(
    observations: list[Observation],
    malformed_count: int,
    cfg: Config,
    duplicate_count: int = 0,
) -> tuple[list[MetricPoint], AggregationStats]:
    """Batch wrapper over :class:`Aggregator` (unchanged public contract)."""
    agg = Aggregator(cfg)
    seen: set[str] = set()
    for obs in observations:
        if obs.obs_id and obs.obs_id in seen:
            duplicate_count += 1
            continue
        if obs.obs_id:
            seen.add(obs.obs_id)
        agg.add(obs)
    return agg.build(malformed_count, duplicate_count)
