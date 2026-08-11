"""Resilience to the dirty / stale data documented in DATA_ANALYSIS.md (F4, F9)
and the production failure modes described in DESIGN.md.

The production spend data contained null costs, a phantom zero-token / non-zero
cost row, and error traces with empty usage. This service must never crash on
those shapes, must never count them as real spend, and must surface them as
data-quality signals. These tests pin that contract.

Note on token precedence: parse_observation reads inputUsage/outputUsage first
and falls back to usageDetails, so tests override both to be unambiguous.
"""

from __future__ import annotations

from gateway_sli.config import Config
from gateway_sli.models import parse_observation
from gateway_sli.sli import aggregate


def _agg(raws):
    obs = [parse_observation(r) for r in raws]
    return aggregate(obs, 0, Config())


def test_phantom_zero_token_nonzero_cost_row(make_raw):
    # F4: the $12.40 / 0-token / 0-request DigestBot row. Cost is honoured but no
    # completion_ratio is emitted (division would be undefined with 0 prompt tokens).
    raw = make_raw(
        inputUsage=0,
        outputUsage=0,
        totalUsage=0,
        usageDetails={"input": 0, "output": 0, "total": 0},
        costDetails={"input": 0.0, "output": 0.0, "total": 12.40},
    )
    points, stats = _agg([raw])
    cost = [p for p in points if p.name == "gateway.cost.usd"][0]
    assert abs(cost.value - 12.40) < 1e-9
    assert stats.cost_missing == 0
    ratio = [p for p in points if p.name == "gateway.tokens.completion_ratio"]
    assert ratio == []  # divide-by-zero guard held


def test_null_cost_row_surfaced_not_dropped(make_raw):
    # F4: the KYC null-cost row - excluded from spend, surfaced as missing, kept
    # for volume/latency (never silently discarded).
    raw = make_raw(costDetails={"input": None, "output": None, "total": None})
    points, stats = _agg([raw])
    assert stats.cost_missing == 1
    cost = [p for p in points if p.name == "gateway.cost.usd"][0]
    assert cost.value == 0.0
    missing = [p for p in points if p.name == "gateway.cost.records_missing"]
    assert missing and missing[0].value == 1


def test_error_observation_with_empty_usage(make_raw):
    # F9: a Bedrock throttling ERROR trace carries no usage/cost. It is counted as
    # an error and does not crash aggregation.
    raw = make_raw(
        level="ERROR",
        statusMessage="throttling_exception",
        inputUsage=0,
        outputUsage=0,
        totalUsage=0,
        usageDetails={},
        costDetails={},
    )
    points, stats = _agg([raw])
    assert stats.errors == 1
    errs = [p for p in points if p.name == "gateway.request.errors"]
    assert errs and errs[0].value == 1
    # error rows with no prompt tokens do not emit a ratio
    assert [p for p in points if p.name == "gateway.tokens.completion_ratio"] == []


def test_completion_ratio_flags_runaway(make_raw):
    # F1: completion tokens far exceeding prompt tokens is the runaway signature.
    raw = make_raw(
        inputUsage=100,
        outputUsage=900,
        totalUsage=1000,
        usageDetails={"input": 100, "output": 900, "total": 1000},
    )
    points, _ = _agg([raw])
    ratio = [p for p in points if p.name == "gateway.tokens.completion_ratio"][0]
    assert ratio.value == 9.0
    assert ratio.type == "gauge"


def test_healthy_ratio_below_one(make_raw):
    # Normal traffic: prompt >> completion, ratio well under 1 (no alert).
    raw = make_raw(
        inputUsage=600,
        outputUsage=200,
        totalUsage=800,
        usageDetails={"input": 600, "output": 200, "total": 800},
    )
    points, _ = _agg([raw])
    ratio = [p for p in points if p.name == "gateway.tokens.completion_ratio"][0]
    assert abs(ratio.value - 0.3333) < 1e-3
