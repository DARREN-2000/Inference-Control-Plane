"""M1: in-batch idempotency. Repeated observation ids within one window are
dropped and surfaced via gateway.pipeline.duplicate_records.
"""

from __future__ import annotations

from gateway_sli.config import Config
from gateway_sli.pipeline import run


class _Src:
    def __init__(self, records):
        self._records = records

    def read(self):
        return self._records


def test_duplicate_ids_are_deduped(make_raw):
    records = [make_raw(id="dup-1"), make_raw(id="dup-1"), make_raw(id="unique-2")]
    result = run(_Src(records), Config())
    assert result.stats.duplicates == 1
    assert result.stats.observations == 2
    dup_points = [p for p in result.points if p.name == "gateway.pipeline.duplicate_records"]
    assert len(dup_points) == 1
    assert dup_points[0].value == 1


def test_blank_ids_fail_closed_as_malformed(make_raw):
    records = [make_raw(id=""), make_raw(id="")]
    result = run(_Src(records), Config())
    assert result.stats.duplicates == 0
    assert result.stats.observations == 0
    assert result.stats.malformed == 2
    assert result.malformed_by_reason["missing_observation_id"] == 2
    assert not any(p.name == "gateway.pipeline.duplicate_records" for p in result.points)
