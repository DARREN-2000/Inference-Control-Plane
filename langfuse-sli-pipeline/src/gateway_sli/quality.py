"""Lightweight quality signal: completion-length anomaly via robust z-score.

This is an OPERATIONAL proxy, not semantic evaluation. It catches truncation
(max_tokens hits), empty/degenerate outputs, and prompt-template regressions
cheaply, using only token counts (no raw content). Richer signals (groundedness,
refusal correctness, schema validity, citation quality, task success) require
context, labels, or judge-model calls and belong in a separate asynchronous
evaluation lane, off the SLI hot path.

Emission semantics (see DESIGN 5.3): a per-record z-score is an EVENT, not a
gauge. We therefore emit a per-window COUNTER of anomalies
(gateway.quality.completion_length_anomalies) plus a gauge of the window's
maximum |z| (gateway.quality.completion_length_max_zscore). A single overwriting
gauge of \"the latest z-score\" would be order-dependent and misleading.

:class:`QualityAccumulator` folds observations one at a time with a bounded
per-group reservoir sample, so a very large window scores with bounded memory
while a normal window (below the cap) keeps every value and matches
:func:`group_completion_lengths` exactly.
"""

from __future__ import annotations

import random
from collections import defaultdict
from dataclasses import dataclass
from statistics import median

from .config import AnomalyConfig, Config
from .models import Observation
from .normalize import model_family, route

# Consistency constants: MAD * 1.4826 ~= sigma (=> z = 0.6745 * dev / MAD).
# meanAD * 1.2533 ~= sigma for a normal distribution.
_MAD_TO_SIGMA = 0.6745
_MEANAD_TO_SIGMA = 1.2533


@dataclass
class AnomalyResult:
    status: str  # "ok" | "cold_start" | "degenerate_constant_baseline"
    score: float | None  # robust z-score; None when not computable
    is_anomaly: bool


@dataclass
class GroupResult:
    """Per-window scoring of one baseline group."""

    status: str  # "ok" | "cold_start" | "degenerate_constant_baseline"
    anomaly_count: int  # records in the window breaching the threshold
    max_abs_z: float | None


@dataclass(frozen=True)
class QualityKey:
    """Baseline grouping key that maps cleanly to allowlisted metric dimensions.

    This prevents composite grouping (route_model) from leaking a synthetic
    'route|model' string into the route dimension.
    """

    route: str
    model_family: str | None = None

    def as_dict(self) -> dict[str, str]:
        dims = {"route": self.route}
        if self.model_family is not None:
            dims["model_family"] = self.model_family
        return dims


def robust_zscore(value: float, baseline: list[float], cfg: AnomalyConfig) -> AnomalyResult:
    """Score ``value`` against ``baseline`` using median + MAD.

    MAD == 0 is handled explicitly: fall back to mean absolute deviation, and if
    the baseline is perfectly constant, flag any deviation as an anomaly.
    """
    n = len(baseline)
    if n < cfg.min_sample:
        return AnomalyResult("cold_start", None, False)

    med = median(baseline)
    abs_dev = [abs(x - med) for x in baseline]
    mad = median(abs_dev)

    if mad > 0:
        score = _MAD_TO_SIGMA * (value - med) / mad
        return AnomalyResult("ok", score, abs(score) >= cfg.threshold)

    mean_ad = sum(abs_dev) / n
    if mean_ad > 0:
        score = (value - med) / (_MEANAD_TO_SIGMA * mean_ad)
        return AnomalyResult("ok", score, abs(score) >= cfg.threshold)

    # Perfectly constant baseline: MAD and meanAD are both 0.
    if value == med:
        return AnomalyResult("degenerate_constant_baseline", 0.0, False)
    return AnomalyResult("degenerate_constant_baseline", None, True)


def score_group(lengths: list[int], cfg: AnomalyConfig) -> GroupResult:
    """Score a group without evaluating a value against itself.

    Normal windows use exact leave-one-out baselines.  Very large reservoirs use
    deterministic two-fold cross-fitting: each half is scored against robust
    statistics computed from the other half.  Both paths remove self-inclusion
    bias while retaining bounded memory and deterministic results.
    """
    n = len(lengths)
    if n < cfg.min_sample:
        return GroupResult("cold_start", 0, None)

    def score(value: int, baseline: list[int]) -> tuple[str, float | None, bool]:
        med = median(baseline)
        deviations = [abs(x - med) for x in baseline]
        mad = median(deviations)
        if mad > 0:
            z = (value - med) / (mad / _MAD_TO_SIGMA)
            return "ok", abs(z), abs(z) >= cfg.threshold
        mean_ad = sum(deviations) / len(baseline)
        if mean_ad > 0:
            z = (value - med) / (_MEANAD_TO_SIGMA * mean_ad)
            return "ok", abs(z), abs(z) >= cfg.threshold
        return "degenerate_constant_baseline", None if value != med else 0.0, value != med

    scored: list[tuple[str, float | None, bool]] = []
    if n <= 2_000:
        for i, value in enumerate(lengths):
            scored.append(score(value, lengths[:i] + lengths[i + 1 :]))
    else:
        left, right = lengths[::2], lengths[1::2]
        if not left or not right:
            return GroupResult("cold_start", 0, None)
        for i, value in enumerate(lengths):
            scored.append(score(value, right if i % 2 == 0 else left))

    statuses = {item[0] for item in scored}
    status = "ok" if "ok" in statuses else "degenerate_constant_baseline"
    anomaly_count = sum(1 for _, _, anomaly in scored if anomaly)
    finite_scores = [value for _, value, _ in scored if value is not None]
    return GroupResult(status, anomaly_count, max(finite_scores) if finite_scores else None)


def _baseline_key(obs: Observation, cfg: Config) -> QualityKey:
    r = route(obs, cfg)
    if cfg.anomaly.baseline_grouping == "route_model":
        return QualityKey(route=r, model_family=model_family(obs.provided_model))
    return QualityKey(route=r)


def group_completion_lengths(
    observations: list[Observation], cfg: Config
) -> dict[QualityKey, list[int]]:
    """Group successful, non-empty completion token counts by baseline key."""
    groups: dict[QualityKey, list[int]] = defaultdict(list)
    for obs in observations:
        if obs.is_error or obs.output_tokens <= 0:
            continue
        groups[_baseline_key(obs, cfg)].append(obs.output_tokens)
    return dict(groups)


class QualityAccumulator:
    """Streaming per-group completion-length collector with a bounded sample.

    Retains at most ``sample_cap`` lengths per baseline group via reservoir
    sampling (Algorithm R), so a very large window scores with bounded memory.
    Below the cap every value is kept, so results match
    :func:`group_completion_lengths`. The RNG is seeded deterministically so
    runs are reproducible.
    """

    def __init__(self, cfg: Config, *, sample_cap: int = 50_000, seed: int = 1729) -> None:
        self.cfg = cfg
        self.sample_cap = sample_cap
        self.groups: dict[QualityKey, list[int]] = {}
        self.empty_counts: dict[QualityKey, int] = defaultdict(int)
        self._seen: dict[QualityKey, int] = {}
        self._rng = random.Random(seed)

    def add(self, obs: Observation) -> None:
        if obs.is_error:
            return
        key = _baseline_key(obs, self.cfg)
        if obs.output_tokens <= 0:
            self.empty_counts[key] += 1
            return
        bucket = self.groups.setdefault(key, [])
        seen = self._seen.get(key, 0)
        if len(bucket) < self.sample_cap:
            bucket.append(obs.output_tokens)
        else:
            j = self._rng.randint(0, seen)
            if j < self.sample_cap:
                bucket[j] = obs.output_tokens
        self._seen[key] = seen + 1

    def results(self) -> dict[QualityKey, GroupResult]:
        return {k: score_group(v, self.cfg.anomaly) for k, v in self.groups.items()}
