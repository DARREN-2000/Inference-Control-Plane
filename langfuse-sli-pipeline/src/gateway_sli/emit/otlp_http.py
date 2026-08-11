from __future__ import annotations

import json
import time
from collections.abc import Sequence
from datetime import datetime

from ..sli import MetricPoint
from .base import assert_allowed
from .otel import OtelJsonExporter


class OtlpExportError(RuntimeError):
    """Raised when the collector rejects an OTLP/HTTP metrics export (non-2xx)."""

    def __init__(self, status: int, body: str) -> None:
        super().__init__(f"OTLP export failed: HTTP {status}")
        self.status = status
        self.body = body


class OtlpHttpExporter:
    """Transmit metrics to an OpenTelemetry Collector over OTLP/HTTP (JSON).

    POSTs the exact OTLP/JSON document produced by :class:`OtelJsonExporter` to
    ``<endpoint>/v1/metrics`` with ``Content-Type: application/json``. This closes
    the "serialized but never transmitted" gap: the JSON exporter writes a
    document; this exporter actually delivers it.

    Network I/O is injected via ``transport`` so the wire contract is
    unit-testable without a live collector; the default transport uses only the
    Python standard library (urllib) - no third-party dependency. Retry/timeout/
    backpressure policy is delegated to the transport layer (a real deployment
    fronts this with the collector's own queueing and retry).
    """

    def __init__(
        self,
        endpoint: str,
        *,
        headers: dict[str, str] | None = None,
        window_start: datetime | None = None,
        window_end: datetime | None = None,
        service_version: str = "1.0.14",
        deployment_environment: str | None = None,
        transport=None,
        timeout: float = 10.0,
        max_retries: int = 3,
        backoff_base: float = 0.25,
        sleep=time.sleep,
    ) -> None:
        self.endpoint = endpoint.rstrip("/")
        self._headers = {"Content-Type": "application/json", **(headers or {})}
        self._timeout = timeout
        self._transport = transport or self._default_transport
        self._max_retries = max_retries
        self._backoff_base = backoff_base
        self._sleep = sleep
        self._serializer = OtelJsonExporter(
            None,
            window_start=window_start,
            window_end=window_end,
            service_version=service_version,
            deployment_environment=deployment_environment,
        )

    @property
    def metrics_url(self) -> str:
        return f"{self.endpoint}/v1/metrics"

    def export(self, points: Sequence[MetricPoint]) -> dict:
        assert_allowed(points)
        payload = self._serializer.build_payload(points)
        body = json.dumps(payload, allow_nan=False).encode("utf-8")
        status, resp = 599, "transport failure"
        for attempt in range(self._max_retries + 1):
            status, resp = self._transport(self.metrics_url, body, dict(self._headers))
            if 200 <= status < 300:
                return payload
            if status not in {429, 500, 502, 503, 504, 599} or attempt >= self._max_retries:
                break
            self._sleep(self._backoff_base * (2**attempt))
        raise OtlpExportError(status, resp)

    def heartbeat(self, points: Sequence[MetricPoint]) -> dict:
        # Export health is a gauge; a separate POST is idempotent (no double count).
        return self.export(points)

    def _default_transport(self, url: str, body: bytes, headers: dict[str, str]):
        import urllib.error
        import urllib.request

        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                return resp.status, resp.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as exc:  # 4xx / 5xx
            return exc.code, exc.read().decode("utf-8", "replace")
        except (urllib.error.URLError, TimeoutError, OSError):
            return 599, "transport failure"
