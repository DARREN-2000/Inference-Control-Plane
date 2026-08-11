"""Configuration objects. Kept separate from logic so behavior is tunable
without code changes and is easy to reason about in review.

Known-team / known-route defaults are DERIVED from the Metric Governance
Contract (governance.py) so the allowlist has a single source of truth. All
configs validate their invariants in __post_init__ so a bad value fails fast at
construction instead of silently corrupting aggregation.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .governance import OTHER, REGISTRY, UNATTRIBUTED

# Explicit histogram bucket boundaries in milliseconds. Explicit buckets are the
# key to correct percentile aggregation across multiple instances/windows: we
# emit bucketed histograms and let the backend (Datadog/OTel) compute p50/p95/p99.
# Averaging pre-computed percentiles across instances would be statistically wrong.
DEFAULT_LATENCY_BUCKETS_MS: tuple[float, ...] = (
    50,
    100,
    200,
    300,
    500,
    750,
    1000,
    1500,
    2000,
    3000,
    5000,
    10000,
    30000,
)

# NOTE: the primary grouping (team x route x model_family x env) is declared
# once in governance.py (PRIMARY_DIMENSIONS) as the single source of truth and is
# intentionally NOT redeclared here, so the two can never drift.

# Enumerated allowlists, derived from the governance registry so there is one
# source of truth. Any team/route not in these sets folds to "other", so a typo,
# a casing variant, or an id-bearing route name can never mint a new time series.
DEFAULT_KNOWN_TEAMS: frozenset[str] = REGISTRY["team"].vocabulary - {OTHER, UNATTRIBUTED}
# Only routes actually registered on the paved road are seeded here; unknown
# Production routes must be enumerated; unknown routes fold to "other" until registered.
DEFAULT_KNOWN_ROUTES: frozenset[str] | None = REGISTRY["route"].vocabulary - {OTHER}


@dataclass(frozen=True)
class AnomalyConfig:
    """Completion-length anomaly detection (robust z-score via median + MAD)."""

    min_sample: int = 30  # below this, we are in cold start and do not score
    threshold: float = 3.5  # |robust z| >= threshold => anomaly
    baseline_grouping: str = "route"  # "route" or "route_model"; route avoids over-fragmentation

    def __post_init__(self) -> None:
        if self.min_sample < 1:
            raise ValueError("AnomalyConfig.min_sample must be >= 1")
        if self.threshold <= 0:
            raise ValueError("AnomalyConfig.threshold must be > 0")
        if self.baseline_grouping not in ("route", "route_model"):
            raise ValueError("AnomalyConfig.baseline_grouping must be 'route' or 'route_model'")


@dataclass(frozen=True)
class Config:
    latency_buckets_ms: tuple[float, ...] = DEFAULT_LATENCY_BUCKETS_MS
    anomaly: AnomalyConfig = field(default_factory=AnomalyConfig)
    # provider_region is allowed only on provider-relevant reliability/cost metrics,
    # never on latency/ttft/quality. Derived via an explicit bounded mapping.
    include_provider_region: bool = True
    known_teams: frozenset[str] = DEFAULT_KNOWN_TEAMS
    known_routes: frozenset[str] | None = DEFAULT_KNOWN_ROUTES

    def __post_init__(self) -> None:
        b = self.latency_buckets_ms
        if not b:
            raise ValueError("latency_buckets_ms must be non-empty")
        if any(x <= 0 for x in b):
            raise ValueError("latency_buckets_ms values must be positive")
        if list(b) != sorted(b) or len(set(b)) != len(b):
            raise ValueError("latency_buckets_ms must be strictly ascending with no duplicates")
        if not self.known_teams:
            raise ValueError("known_teams must be non-empty")
        registered_teams = REGISTRY["team"].vocabulary - {OTHER, UNATTRIBUTED}
        if not self.known_teams.issubset(registered_teams):
            raise ValueError("known_teams must be registered in the governance vocabulary")
        if self.known_routes is None:
            raise ValueError("known_routes cannot be None; production cardinality must be bounded")
        registered_routes = REGISTRY["route"].vocabulary - {OTHER}
        if not self.known_routes.issubset(registered_routes):
            raise ValueError("known_routes must be registered in the governance vocabulary")
