"""P0 regression guard: export_success must be TRANSMITTED, not merely returned.

The pipeline computes export health only after the main flush, so it cannot be in
the main OTLP document. It is instead sent on a separate heartbeat channel. These
tests prove the value actually crosses the exporter boundary and correctly
reports failure.
"""

from gateway_sli.config import Config
from gateway_sli.pipeline import run
from gateway_sli.sources.file_source import FileTraceSource

FIXTURE = "data/sample_traces.json"


class CapturingExporter:
    def __init__(self, fail_main: bool = False) -> None:
        self.fail_main = fail_main
        self.main_batches: list[list] = []
        self.heartbeat_batches: list[list] = []

    def export(self, points):
        if self.fail_main:
            raise RuntimeError("collector down")
        self.main_batches.append(list(points))

    def heartbeat(self, points):
        self.heartbeat_batches.append(list(points))


def _health(batches):
    return [p for b in batches for p in b if p.name == "gateway.pipeline.export_success"]


def test_export_success_transmitted_on_heartbeat_channel():
    exp = CapturingExporter()
    result = run(FileTraceSource(FIXTURE), Config(), exp)
    hp = _health(exp.heartbeat_batches)
    assert hp and hp[0].value == 1.0
    # It must NOT be smuggled into the main flush (computed before export status).
    assert not _health(exp.main_batches)
    assert result.stats.export_ok is True


def test_export_failure_surfaces_zero_on_heartbeat():
    exp = CapturingExporter(fail_main=True)
    result = run(FileTraceSource(FIXTURE), Config(), exp)
    assert result.stats.export_ok is False
    hp = _health(exp.heartbeat_batches)
    assert hp and hp[0].value == 0.0


def test_final_run_duration_crosses_heartbeat_boundary():
    exp = CapturingExporter()
    result = run(FileTraceSource(FIXTURE), Config(), exp)
    transmitted = [p for batch in exp.heartbeat_batches for p in batch]
    duration = [p for p in transmitted if p.name == "gateway.pipeline.run_duration_seconds"]
    assert duration and duration[0].value >= 0
    assert any(p.name == "gateway.pipeline.run_duration_seconds" for p in result.points)
