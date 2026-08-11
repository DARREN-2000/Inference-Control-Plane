"""Metric Governance Contract (MGC) - the single source of truth for every
dimension the pipeline is permitted to emit.

Each governed dimension declares its owner, bounded vocabulary, normalization
policy, privacy classification, estimated cardinality budget, and unknown-value
behavior. The privacy allowlist (``emit/base.ALLOWED_ATTRIBUTE_KEYS``) and the
default known-team / known-route sets (``config.py``) are DERIVED from this
registry, so there is exactly one place to reason about "what may be emitted."

Tests (``test_governance``, ``test_fuzz_invariants``) enforce that nothing
outside this contract can appear on an exported metric, which makes uncontrolled
dimension expansion a test failure rather than a production incident.
"""

from __future__ import annotations

from dataclasses import dataclass

# --- bounded fold tokens ---------------------------------------------------
OTHER = "other"
UNKNOWN = "unknown"
UNATTRIBUTED = "unattributed"

# --- closed vocabularies (fold token added per-dimension below) ------------
MODEL_FAMILIES = frozenset(
    {"claude-sonnet", "claude-haiku", "claude-opus", "gpt-5", "gpt-5-mini", "gpt-4o"}
)
ERROR_CATEGORIES = frozenset(
    {"throttling", "timeout", "provider_error", "auth", "invalid_request", "content_filter"}
)
ENVS = frozenset({"prod", "staging", "dev"})
PROVIDER_REGIONS = frozenset({"bedrock_eu", "bedrock_us", "external_zdr"})
OUTCOMES = frozenset({"success", "error"})

_PLATFORM = "AI Platform (paved road)"
_OBSERVABILITY = "AI Platform (observability)"


@dataclass(frozen=True)
class Dimension:
    """One governed metric dimension. This IS the contract for that label."""

    name: str
    owner: str
    privacy_class: str  # non-sensitive | internal | sensitive
    vocabulary: frozenset[str]  # closed set of allowed values (incl. fold tokens)
    bounded_open: bool  # True => values registered out-of-band, folded to a token
    unknown_behavior: str
    cardinality_budget: int
    normalization: str


# Dimensions allowed on workload SLIs. "vocabulary" is the exhaustive set of
# values the projection may emit; bounded_open marks dimensions whose membership
# is governed by an allowlist that folds unknowns to a token.
WORKLOAD_DIMENSIONS: tuple[Dimension, ...] = (
    Dimension(
        "team",
        _PLATFORM,
        "non-sensitive",
        frozenset(
            {
                "AdvisorChat",
                "KYC",
                "DevAgent",
                "DigestBot",
                "Research",
                "Marketing",
                OTHER,
                UNATTRIBUTED,
            }
        ),
        True,
        "case-insensitive allowlist; blank -> unattributed; unknown -> other",
        8,
        "normalize.team",
    ),
    Dimension(
        "route",
        _PLATFORM,
        "non-sensitive",
        frozenset({"advisorchat-turn", "digestbot-summary", "devagent-task", OTHER}),
        True,
        "shape-validated + known-route allowlist; unknown -> other",
        32,
        "normalize.route",
    ),
    Dimension(
        "model_family",
        _PLATFORM,
        "non-sensitive",
        MODEL_FAMILIES | {OTHER},
        False,
        "explicit prefix rules; unknown -> other",
        8,
        "normalize.model_family",
    ),
    Dimension(
        "env",
        _PLATFORM,
        "non-sensitive",
        ENVS | {OTHER},
        False,
        "explicit map; unknown -> other",
        4,
        "normalize.env",
    ),
    Dimension(
        "outcome",
        _PLATFORM,
        "non-sensitive",
        OUTCOMES,
        False,
        "literal success|error",
        2,
        "sli.aggregate",
    ),
    Dimension(
        "error_category",
        _PLATFORM,
        "non-sensitive",
        ERROR_CATEGORIES | {UNKNOWN},
        False,
        "bounded map on structured error.type (never statusMessage); unknown -> unknown",
        8,
        "normalize.error_category",
    ),
    Dimension(
        "provider_region",
        _PLATFORM,
        "non-sensitive",
        PROVIDER_REGIONS | {OTHER},
        False,
        "explicit bounded mapping; never parsed from internalModelId; unknown -> other",
        4,
        "normalize.provider_region",
    ),
)

# Meta-dimension used ONLY on pipeline self-health metrics.
PIPELINE_DIMENSIONS: tuple[Dimension, ...] = (
    Dimension(
        "dimension",
        _OBSERVABILITY,
        "non-sensitive",
        frozenset({"team", "route", "model_family", "env", "provider_region"}),
        False,
        "names which governed dimension folded a non-blank value to a token",
        5,
        "sli.aggregate unknown-dimension counter",
    ),
)

REGISTRY: dict[str, Dimension] = {d.name: d for d in (*WORKLOAD_DIMENSIONS, *PIPELINE_DIMENSIONS)}


@dataclass(frozen=True)
class MetricDefinition:
    """Closed contract for a metric's shape, not just its label values."""

    type: str
    unit: str
    allowed_dimensions: frozenset[str]


_PRIMARY = frozenset({"team", "route", "model_family", "env"})
_COST = frozenset({"team", "route", "model_family", "provider_region"})
_QUALITY = frozenset({"route", "model_family"})

METRIC_REGISTRY: dict[str, MetricDefinition] = {
    "gateway.request.duration": MetricDefinition("histogram", "ms", _PRIMARY),
    "gateway.request.ttft": MetricDefinition("histogram", "ms", _PRIMARY),
    "gateway.request.count": MetricDefinition("counter", "1", _PRIMARY | {"outcome"}),
    "gateway.request.errors": MetricDefinition("counter", "1", _PRIMARY | {"error_category"}),
    "gateway.cost.usd": MetricDefinition("counter", "USD", _COST),
    "gateway.cost.request_count": MetricDefinition("counter", "1", _COST),
    "gateway.cost.records_missing": MetricDefinition("counter", "1", _COST),
    "gateway.cost.records_invalid": MetricDefinition("counter", "1", _COST),
    "gateway.tokens.input": MetricDefinition("counter", "1", _COST),
    "gateway.tokens.output": MetricDefinition("counter", "1", _COST),
    "gateway.tokens.completion_ratio": MetricDefinition("gauge", "ratio", _COST),
    "gateway.cache.read_tokens": MetricDefinition("counter", "1", _COST),
    "gateway.cache.hit_count": MetricDefinition("counter", "1", _COST),
    "gateway.quality.completion_length_anomalies": MetricDefinition("counter", "1", _QUALITY),
    "gateway.quality.completion_length_max_zscore": MetricDefinition("gauge", "score", _QUALITY),
    "gateway.quality.empty_completion_count": MetricDefinition("counter", "1", _QUALITY),
    "gateway.pipeline.unknown_dimension": MetricDefinition(
        "counter", "1", frozenset({"dimension"})
    ),
}

# Pipeline metrics except unknown_dimension are deliberately dimensionless.
for _name, _type, _unit in (
    ("gateway.pipeline.malformed_records", "counter", "1"),
    ("gateway.pipeline.duplicate_records", "counter", "1"),
    ("gateway.pipeline.records_read", "counter", "1"),
    ("gateway.pipeline.records_processed", "counter", "1"),
    ("gateway.pipeline.cross_run_duplicate_records", "counter", "1"),
    ("gateway.pipeline.quarantined_records", "counter", "1"),
    ("gateway.pipeline.read_truncated", "gauge", "1"),
    ("gateway.pipeline.records_missing_cost", "counter", "1"),
    ("gateway.pipeline.records_invalid_cost", "counter", "1"),
    ("gateway.pipeline.freshness_seconds", "gauge", "s"),
    ("gateway.pipeline.clock_skew_seconds", "gauge", "s"),
    ("gateway.pipeline.series_emitted", "gauge", "1"),
    ("gateway.pipeline.run_duration_seconds", "gauge", "s"),
    ("gateway.pipeline.source_requests", "counter", "1"),
    ("gateway.pipeline.source_retries", "counter", "1"),
    ("gateway.pipeline.source_pages", "counter", "1"),
    ("gateway.pipeline.source_latency_seconds", "gauge", "s"),
    ("gateway.pipeline.export_success", "gauge", "1"),
    ("gateway.pipeline.source_success", "gauge", "1"),
    ("gateway.pipeline.checkpoint_conflicts", "counter", "1"),
):
    METRIC_REGISTRY[_name] = MetricDefinition(_type, _unit, frozenset())

WORKLOAD_ATTRIBUTE_KEYS = frozenset(d.name for d in WORKLOAD_DIMENSIONS)
PIPELINE_ATTRIBUTE_KEYS = frozenset(d.name for d in PIPELINE_DIMENSIONS)
ALLOWED_ATTRIBUTE_KEYS = WORKLOAD_ATTRIBUTE_KEYS | PIPELINE_ATTRIBUTE_KEYS

# The primary SLI grouping; worst-case series count is the product of these.
PRIMARY_DIMENSIONS: tuple[str, ...] = ("team", "route", "model_family", "env")


def estimated_max_series() -> int:
    """Worst-case distinct series for the primary grouping (team x route x
    model_family x env). This is the hard cardinality budget the allowlists
    guarantee; new teams/routes fold to 'other' rather than expanding it.
    """
    product = 1
    for name in PRIMARY_DIMENSIONS:
        product *= len(REGISTRY[name].vocabulary)
    return product


def _vocab(name: str) -> int:
    return len(REGISTRY[name].vocabulary)


def estimated_max_total_series() -> int:
    """Worst-case count of distinct metric points a single window can emit across
    EVERY workload metric family, derived from the governed vocabularies. This is
    the authoritative ceiling the ``gateway.pipeline.series_emitted`` tripwire is
    set above: any window exceeding it is a dimension-explosion regression, not
    legitimate traffic. Keeping it in the registry means the alert threshold is
    derived from the contract rather than hand-picked.

    Families (see ``sli.aggregate``):
      * duration + ttft:   primary grouping (team x route x model_family x env)
      * request.count:     primary x outcome
      * request.errors:    primary x error_category
      * cost family:       (team x route x model_family x provider_region) x 9
                           point kinds (usd, request_count, tokens.input,
                           tokens.output, cache.read_tokens, cache.hit_count,
                           cost.records_missing, cost.records_invalid,
                           tokens.completion_ratio)
    """
    primary = _vocab("team") * _vocab("route") * _vocab("model_family") * _vocab("env")
    cost_group = (
        _vocab("team") * _vocab("route") * _vocab("model_family") * _vocab("provider_region")
    )
    duration_ttft = 2 * primary
    request_count = primary * _vocab("outcome")
    request_errors = primary * _vocab("error_category")
    cost_points = cost_group * 9
    return duration_ttft + request_count + request_errors + cost_points
