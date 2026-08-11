from __future__ import annotations

from datetime import datetime, timezone
from contextlib import redirect_stdout
from io import StringIO

from gateway_sli.checkpoint import FileCheckpointStore, prune_seen
from gateway_sli.config import Config
from gateway_sli.models import _parse_ts, parse_observation
from gateway_sli.normalize import model_family, route
from gateway_sli.pipeline import run
from gateway_sli.sli import MetricPoint, _percentile
from gateway_sli.emit.otel import OtelJsonExporter
from gateway_sli.sources.langfuse_api import LangfuseApiTraceSource


def test_empty_checkpoint_is_first_run(tmp_path):
    path = tmp_path / "empty.json"
    path.write_text("")
    assert FileCheckpointStore(str(path)).load() is None


def test_corrupt_seen_timestamp_is_skipped():
    out = prune_seen(
        {"bad": "not-a-time"},
        [],
        cutoff=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    assert out == {}


def test_none_id_stays_blank(make_raw):
    assert parse_observation(make_raw(id=None)).obs_id == ""


def test_non_mapping_metadata_is_contained(make_raw):
    obs = parse_observation(make_raw(metadata="bad", traceMetadata="bad"))
    assert obs.team == ""
    assert obs.error is None


def test_route_matching_is_case_insensitive(make_raw):
    obs = parse_observation(make_raw(traceName="AdvisorChat-Turn"))
    assert route(obs, Config()) == "advisorchat-turn"


def test_gpt_nano_does_not_fold_into_gpt5():
    assert model_family("gpt-5-nano") == "other"
    assert model_family("eu.anthropic.claude-3-5-sonnet-v2:0") == "claude-sonnet"


def test_rfc3339_parser_normalizes_offset_and_nanoseconds():
    parsed = _parse_ts("2026-01-15T12:14:22.123456789+01:00")
    assert parsed.isoformat() == "2026-01-15T11:14:22.123456+00:00"


def test_rfc3339_parser_rejects_timezone_free_input():
    try:
        _parse_ts("2026-01-15T11:14:22")
    except ValueError:
        return
    raise AssertionError("timezone-free timestamps must fail closed")


def test_single_observation_percentile_is_exact():
    assert _percentile([150.0], 95) == 150.0


def test_cursor_chain_does_not_fall_back_to_page_request():
    calls = []
    responses = [
        (200, {}, '{"data":[{"id":"a"}],"meta":{"cursor":"c1"}}'),
        (200, {}, '{"data":[{"id":"b"}],"meta":{}}'),
    ]

    def transport(url, headers):
        calls.append(url)
        return responses[len(calls) - 1]

    source = LangfuseApiTraceSource("https://lf", "pk", "sk", transport=transport)
    assert [row["id"] for row in source.read()] == ["a", "b"]
    assert len(calls) == 2


def test_source_failure_sets_export_health_zero():
    class Broken:
        def iter_records(self):
            raise RuntimeError("source down")
            yield  # pragma: no cover

    class Capture:
        def __init__(self):
            self.health = []

        def export(self, points):
            raise AssertionError("partial data must not export")

        def heartbeat(self, points):
            self.health.extend(points)

    exporter = Capture()
    result = run(Broken(), Config(), exporter)
    assert result.stats.source_ok is False
    assert result.stats.export_ok is False
    assert exporter.health[0].value == 0.0


def test_eager_iter_records_failure_is_contained():
    class EagerBroken:
        def iter_records(self):
            raise ConnectionError("source unavailable before iterator construction")

    class Capture:
        def __init__(self):
            self.health = []

        def export(self, points):
            raise AssertionError("partial data must not export")

        def heartbeat(self, points):
            self.health.extend(points)

    exporter = Capture()
    result = run(EagerBroken(), Config(), exporter)
    assert result.stats.source_ok is False
    assert result.stats.source_error == "ConnectionError"
    assert result.stats.export_ok is False
    assert any(
        p.name == "gateway.pipeline.export_success" and p.value == 0.0 for p in exporter.health
    )
    assert any(
        p.name == "gateway.pipeline.source_success" and p.value == 0.0 for p in exporter.health
    )


def test_eager_read_failure_is_contained():
    class EagerReadBroken:
        def read(self):
            raise OSError("fixture or source read failed")

    result = run(EagerReadBroken(), Config())
    assert result.stats.source_ok is False
    assert result.stats.source_error == "OSError"
    assert result.stats.export_ok is False
    health = {p.name: p.value for p in result.points}
    assert health["gateway.pipeline.export_success"] == 0.0
    assert health["gateway.pipeline.source_success"] == 0.0


def test_otel_stdout_is_one_clean_json_document():
    out = StringIO()
    with redirect_stdout(out):
        exporter = OtelJsonExporter()
        exporter.export(
            [
                MetricPoint(
                    "gateway.pipeline.series_emitted",
                    "gauge",
                    "1",
                    {},
                    value=1,
                )
            ]
        )
        exporter.heartbeat([])
    import json

    payload = json.loads(out.getvalue())
    assert "resourceMetrics" in payload


def test_otel_creates_parent_directories(tmp_path):
    path = tmp_path / "nested" / "metrics.json"
    OtelJsonExporter(str(path)).export(
        [
            MetricPoint(
                "gateway.pipeline.series_emitted",
                "gauge",
                "1",
                {},
                value=1,
            )
        ]
    )
    assert path.exists()
