import json

from gateway_sli.config import Config
from gateway_sli.emit.base import ALLOWED_ATTRIBUTE_KEYS, assert_allowed
from gateway_sli.emit.otel import OtelJsonExporter
from gateway_sli.models import parse_observation
from gateway_sli.sli import MetricPoint, aggregate

PII = "PIISECRET"


def _points(make_raw):
    raws = [
        make_raw(),
        make_raw(
            id="obs-err",
            level="ERROR",
            completionStartTime=None,
            output=None,
            statusMessage=f"boom {PII} region eu-central-1",
            metadata={
                "error": {"type": "ThrottlingException", "provider": "bedrock"},
                "request_id": f"req-{PII}",
            },
            costDetails={},
            usageDetails={},
            outputUsage=0,
        ),
    ]
    obs = [parse_observation(r) for r in raws]
    points, _ = aggregate(obs, 0, Config())
    return points


def test_no_disallowed_dimension_keys(make_raw):
    points = _points(make_raw)
    for p in points:
        assert set(p.dims).issubset(ALLOWED_ATTRIBUTE_KEYS), p.dims


def test_pii_never_reaches_serialized_metrics(make_raw):
    points = _points(make_raw)
    serialized = json.dumps(OtelJsonExporter().export(points))
    assert PII not in serialized
    # High-cardinality identifiers and raw content must be absent too.
    for banned in ("key-advisorchat-prod", "call-", "req-", "123-45-6789", "SSN"):
        assert banned not in serialized


def test_internal_observation_cannot_retain_raw_sensitive_fields(make_raw):
    raw = make_raw(
        traceId=f"trace-{PII}",
        statusMessage=f"status-{PII}",
        traceTags=[PII],
        metadata={
            "error": {
                "type": f"SecretType-{PII}",
                "message": f"message-{PII}",
                "stack": f"stack-{PII}",
            }
        },
    )
    obs = parse_observation(raw)
    projected = repr(obs)
    assert PII not in projected
    assert not hasattr(obs, "status_message")
    assert not hasattr(obs, "trace_id")
    assert not hasattr(obs, "tags")


def test_exporter_rejects_injected_bad_attribute():
    bad = MetricPoint(
        "gateway.request.count", "counter", "1", {"team": "x", "user_id": "u-1"}, value=1
    )
    try:
        assert_allowed([bad])
    except ValueError as exc:
        assert "user_id" in str(exc)
    else:
        raise AssertionError("expected ValueError for disallowed attribute")
