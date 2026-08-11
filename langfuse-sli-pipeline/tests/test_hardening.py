from __future__ import annotations

from datetime import datetime, timezone

from gateway_sli.config import Config
from gateway_sli.emit.base import assert_allowed
from gateway_sli.emit.otel import OtelJsonExporter
from gateway_sli.models import parse_observation
from gateway_sli.pipeline import run
from gateway_sli.sli import MetricPoint


def test_metric_values_are_governed():
    point = MetricPoint(
        "gateway.request.count", "counter", "1", {"team": "person@example.com"}, value=1
    )
    try:
        assert_allowed([point])
    except ValueError as exc:
        assert "disallowed value" in str(exc)
    else:
        raise AssertionError("expected governed-value rejection")


def test_metric_name_type_unit_and_dimension_set_are_governed():
    bad_points = [
        MetricPoint("gateway.unregistered", "counter", "1", {}, value=1),
        MetricPoint("gateway.request.count", "gauge", "1", {}, value=1),
        MetricPoint("gateway.request.count", "counter", "ms", {}, value=1),
        MetricPoint(
            "gateway.pipeline.records_read", "counter", "1", {"team": "AdvisorChat"}, value=1
        ),
    ]
    for point in bad_points:
        try:
            assert_allowed([point])
        except ValueError:
            continue
        raise AssertionError(f"metric schema accepted invalid point: {point}")


def test_dirty_numbers_and_string_false_are_sanitized(make_raw):
    raw = make_raw(
        inputUsage=-1,
        outputUsage=2.5,
        usageDetails={"input": -1, "output": 2.5},
        costDetails={"total": "NaN"},
        modelParameters={"stream": "false"},
    )
    obs = parse_observation(raw)
    assert obs.input_tokens == 0
    assert obs.output_tokens == 0
    assert obs.cost_total is None
    assert obs.stream is False


def test_invalid_ttft_is_excluded(make_raw):
    raw = make_raw(
        startTime="2026-01-15T11:00:10Z",
        completionStartTime="2026-01-15T11:00:00Z",
        endTime="2026-01-15T11:00:20Z",
        modelParameters={"stream": True},
    )
    assert parse_observation(raw).ttft_ms is None


def test_strict_json_rejects_nonfinite_metric():
    point = MetricPoint("gateway.pipeline.series_emitted", "gauge", "1", {}, value=float("nan"))
    try:
        OtelJsonExporter().export([point])
    except ValueError:
        return
    raise AssertionError("NaN must not serialize")


class _Store:
    def __init__(self):
        self.saved = False

    def load(self):
        return None

    def save(self, cp):
        self.saved = True


class _Source:
    def __init__(self, rows):
        self.rows = rows

    def iter_records(self):
        yield from self.rows


def test_truncated_window_never_checkpoints(make_raw):
    store = _Store()
    rows = [make_raw(id=f"x-{i}") for i in range(3)]
    run(
        _Source(rows),
        Config(),
        window_end=datetime.now(timezone.utc),
        checkpoint_store=store,
        max_records=1,
    )
    assert store.saved is False


def test_empty_completion_is_counted(make_raw):
    raw = make_raw(outputUsage=0, usageDetails={"output": 0})
    result = run(_Source([raw]), Config())
    points = [p for p in result.points if p.name == "gateway.quality.empty_completion_count"]
    assert points and points[0].value == 1
