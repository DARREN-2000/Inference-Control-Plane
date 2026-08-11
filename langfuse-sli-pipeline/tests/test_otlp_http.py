"""Unit tests for the OTLP/HTTP exporter using an injected transport, so the
delivery contract (endpoint, content-type, payload shape, error handling,
privacy allowlist) is verified without a live collector.
"""

import json

from gateway_sli.emit.otlp_http import OtlpExportError, OtlpHttpExporter
from gateway_sli.sli import MetricPoint


def make_transport(status=200, body="{}"):
    captured = {}

    def transport(url, data, headers):
        captured["url"] = url
        captured["data"] = data
        captured["headers"] = headers
        return status, body

    transport.captured = captured
    return transport


def _points():
    return [MetricPoint("gateway.request.count", "counter", "1", {"team": "AdvisorChat"}, value=3)]


def test_posts_to_v1_metrics_with_json_content_type():
    t = make_transport()
    exp = OtlpHttpExporter("https://collector.example", transport=t)
    payload = exp.export(_points())
    assert t.captured["url"].endswith("/v1/metrics")
    assert t.captured["headers"]["Content-Type"] == "application/json"
    sent = json.loads(t.captured["data"].decode())
    assert "resourceMetrics" in sent
    assert "resourceMetrics" in payload


def test_non_2xx_raises():
    t = make_transport(status=503, body="unavailable")
    exp = OtlpHttpExporter("https://collector.example", transport=t)
    try:
        exp.export(_points())
    except OtlpExportError as exc:
        assert exc.status == 503
    else:
        raise AssertionError("expected OtlpExportError")


def test_rejects_disallowed_dimension_before_transmit():
    t = make_transport()
    exp = OtlpHttpExporter("https://collector.example", transport=t)
    bad = [MetricPoint("gateway.request.count", "counter", "1", {"user_id": "u1"}, value=1)]
    try:
        exp.export(bad)
    except ValueError as exc:
        assert "user_id" in str(exc)
    else:
        raise AssertionError("expected ValueError")
    assert "url" not in t.captured  # nothing was transmitted
