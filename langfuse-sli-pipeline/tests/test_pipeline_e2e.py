import json

from gateway_sli.config import Config
from gateway_sli.emit.otel import OtelJsonExporter
from gateway_sli.pipeline import run
from gateway_sli.sources.file_source import FileTraceSource

FIXTURE = "data/sample_traces.json"


def test_end_to_end_on_fixture():
    exporter = OtelJsonExporter()
    result = run(FileTraceSource(FIXTURE), Config(), exporter)

    assert result.stats.observations > 0
    names = {p.name for p in result.points}
    assert "gateway.request.duration" in names
    assert "gateway.request.count" in names
    assert "gateway.cost.usd" in names

    # Serialized payload must be valid OTLP-ish JSON and PII-free.
    payload = exporter.export(result.points)
    text = json.dumps(payload)
    # Raw content and high-cardinality identifiers must never appear. (Note:
    # substrings like "input" are legitimate in metric names such as
    # gateway.tokens.input, so we assert on actual leak markers only.)
    for banned in (
        "PIISECRET",
        "litellm_call_id",
        "litellm_proxy_key_alias",
        "request_id",
        "traceId",
        "statusMessage",
    ):
        assert banned not in text


def test_empty_input_produces_no_points(tmp_path):
    empty = tmp_path / "empty.json"
    empty.write_text(json.dumps({"data": [], "meta": {"cursor": None}}))
    result = run(FileTraceSource(str(empty)), Config())
    # Telemetry Trust Contract: an empty window is NOT silent. No workload
    # points, but the pipeline still reports records_read=0 so on-call can alert
    # on the blind spot instead of mistaking absence of data for health.
    assert result.stats.observations == 0
    workload = [
        p
        for p in result.points
        if p.name.startswith("gateway.")
        and not p.name.startswith("gateway.pipeline.")
        and not p.name.startswith("gateway.quality.")
    ]
    assert workload == []
    read = [p for p in result.points if p.name == "gateway.pipeline.records_read"]
    assert read and read[0].value == 0
