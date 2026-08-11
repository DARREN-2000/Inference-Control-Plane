from __future__ import annotations

import json
import os
import sys
from collections.abc import Sequence
from datetime import datetime, timezone

from ..sli import MetricPoint
from .base import assert_allowed


def _to_unix_nanos(dt: datetime | None) -> int:
    if dt is None:
        dt = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1_000_000_000)


class OtelJsonExporter:
    """Serialize metric points into an OTLP/JSON-shaped payload.

    Produces the exact structure an OpenTelemetry collector expects
    (resourceMetrics -> scopeMetrics -> metrics with histogram/sum/gauge data
    points), including per-point ``startTimeUnixNano``/``timeUnixNano`` for the
    aggregation window. It does NOT perform network I/O - swapping in a real
    OTLP gRPC/HTTP exporter is a localized change. Keeping it offline makes the
    output deterministic and testable without a live collector.

    Temporality: DELTA. Each run aggregates one bounded, closed window and emits
    the delta for that window, so counters are correct across process restarts
    (there is no cumulative in-process state to lose) and multiple workers can
    emit disjoint windows that the backend sums. DELTA sums are still monotonic
    (request counts only increase within a window), so ``isMonotonic`` is true.
    """

    def __init__(
        self,
        out_path: str | None = None,
        *,
        window_start: datetime | None = None,
        window_end: datetime | None = None,
        service_version: str = "1.0.14",
        deployment_environment: str | None = None,
    ) -> None:
        self.out_path = out_path
        self._start_nanos = _to_unix_nanos(window_start)
        self._time_nanos = _to_unix_nanos(window_end)
        self._service_version = service_version
        self._deployment_environment = deployment_environment
        self._heartbeat_points: list[MetricPoint] = []

    def build_payload(self, points: Sequence[MetricPoint]) -> dict:
        """Public serializer: MetricPoints -> OTLP/JSON dict (no I/O). Reused by
        the OTLP/HTTP exporter so the wire format has one implementation."""
        assert_allowed(points)
        return self._to_otlp(points)

    def export(self, points: Sequence[MetricPoint]) -> dict:
        payload = self.build_payload(points)
        text = json.dumps(payload, indent=2, allow_nan=False)
        if self.out_path:
            directory = os.path.dirname(os.path.abspath(self.out_path))
            os.makedirs(directory, exist_ok=True)
            with open(self.out_path, "w", encoding="utf-8") as fh:
                fh.write(text)
        else:
            print(text, file=sys.stdout)
        return payload

    def heartbeat(self, points: Sequence[MetricPoint]) -> dict:
        """Emit the run-completion heartbeat (export health) as a SEPARATE OTLP
        document so it never clobbers the main window payload. Written to a
        sibling ``.heartbeat.json`` file when an output path is configured."""
        # Multiple lifecycle heartbeats may occur (export status, then final run
        # duration/checkpoint status). Keep the file exporter as one valid OTLP
        # document containing all heartbeat points rather than overwriting the
        # earlier export-health signal.
        self._heartbeat_points.extend(points)
        payload = self.build_payload(self._heartbeat_points)
        if self.out_path:
            directory = os.path.dirname(os.path.abspath(self.out_path))
            os.makedirs(directory, exist_ok=True)
            with open(self.out_path + ".heartbeat.json", "w", encoding="utf-8") as fh:
                fh.write(json.dumps(payload, indent=2, allow_nan=False))
        return payload

    @staticmethod
    def _attrs(dims: dict[str, str]) -> list[dict]:
        return [{"key": k, "value": {"stringValue": str(v)}} for k, v in sorted(dims.items())]

    def _resource_attrs(self) -> list[dict]:
        # Resource-level identity. deployment.environment describes where the SLI
        # *service* itself runs; per-workload env stays a metric dimension.
        attrs = [
            {"key": "service.name", "value": {"stringValue": "gateway-sli"}},
            {"key": "service.version", "value": {"stringValue": self._service_version}},
        ]
        if self._deployment_environment:
            attrs.append(
                {
                    "key": "deployment.environment",
                    "value": {"stringValue": self._deployment_environment},
                }
            )
        return attrs

    def _to_otlp(self, points: Sequence[MetricPoint]) -> dict:
        st, tt = self._start_nanos, self._time_nanos
        metrics: list[dict] = []
        for p in points:
            attrs = self._attrs(p.dims)
            if p.type == "histogram" and p.histogram:
                h = p.histogram
                bucket_counts = [h["bucket_counts"][b] for b in h["bounds"]]
                bucket_counts.append(h["bucket_counts"]["inf"])
                dp: dict = {
                    "attributes": attrs,
                    "startTimeUnixNano": str(st),
                    "timeUnixNano": str(tt),
                    # OTLP/JSON encodes 64-bit ints (fixed64 count/bucketCounts)
                    # as strings per the proto3 JSON mapping: JSON numbers are
                    # IEEE-754 doubles and lose precision past 2^53.
                    "count": str(h["count"]),
                    "sum": h["sum"],
                    "explicitBounds": list(h["bounds"]),
                    "bucketCounts": [str(c) for c in bucket_counts],
                }
                if h.get("min") is not None:
                    dp["min"] = h["min"]
                if h.get("max") is not None:
                    dp["max"] = h["max"]
                metrics.append(
                    {
                        "name": p.name,
                        "unit": p.unit,
                        "histogram": {
                            "aggregationTemporality": "AGGREGATION_TEMPORALITY_DELTA",
                            "dataPoints": [dp],
                        },
                    }
                )
            elif p.type == "counter":
                metrics.append(
                    {
                        "name": p.name,
                        "unit": p.unit,
                        "sum": {
                            "isMonotonic": True,
                            "aggregationTemporality": "AGGREGATION_TEMPORALITY_DELTA",
                            "dataPoints": [
                                {
                                    "attributes": attrs,
                                    "startTimeUnixNano": str(st),
                                    "timeUnixNano": str(tt),
                                    "asDouble": p.value,
                                }
                            ],
                        },
                    }
                )
            else:  # gauge
                metrics.append(
                    {
                        "name": p.name,
                        "unit": p.unit,
                        "gauge": {
                            "dataPoints": [
                                {
                                    "attributes": attrs,
                                    "timeUnixNano": str(tt),
                                    "asDouble": p.value,
                                }
                            ]
                        },
                    }
                )
        return {
            "resourceMetrics": [
                {
                    "resource": {"attributes": self._resource_attrs()},
                    "scopeMetrics": [
                        {
                            "scope": {"name": "gateway_sli", "version": "1.0.14"},
                            "metrics": metrics,
                        }
                    ],
                }
            ]
        }
