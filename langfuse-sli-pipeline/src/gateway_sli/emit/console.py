from __future__ import annotations

from collections.abc import Sequence

from ..sli import MetricPoint
from .base import assert_allowed


class ConsoleExporter:
    """Human-readable exporter for local runs and debugging."""

    def __init__(self, printer=print) -> None:
        self._print = printer

    def export(self, points: Sequence[MetricPoint]) -> None:
        assert_allowed(points)
        self._print("=== gateway SLI metrics ===")
        for p in sorted(points, key=lambda x: (x.name, sorted(x.dims.items()))):
            dims = " ".join(f"{k}={v}" for k, v in sorted(p.dims.items()))
            if p.type == "histogram" and p.histogram:
                h = p.histogram
                self._print(
                    f"{p.name} [{dims}] n={h['count']} "
                    f"p50={h['p50']:.1f}{p.unit} p95={h['p95']:.1f}{p.unit} "
                    f"p99={h['p99']:.1f}{p.unit}"
                )
            else:
                # Dimensionless counters use unit "1"; don't print it as a suffix.
                unit = "" if p.unit == "1" else f" {p.unit}"
                self._print(f"{p.name} [{dims}] = {p.value}{unit}")

    def heartbeat(self, points: Sequence[MetricPoint]) -> None:
        """Run-completion heartbeat (export health), emitted on a separate call
        from the main flush so export_success is actually surfaced."""
        assert_allowed(points)
        for p in points:
            self._print(f"[heartbeat] {p.name} = {p.value}")
