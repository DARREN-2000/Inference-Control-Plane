"""Cross-run checkpoint + watermark persistence and cross-run idempotency.

Covers: store round-trip + first-run None, watermark advancing ONLY on a clean
export, cross-run de-duplication of a trace re-read in the trailing overlap,
bounded pruning of the seen set, and the CLI wiring end to end.
"""

from __future__ import annotations

from datetime import datetime, timezone

from gateway_sli.checkpoint import Checkpoint, FileCheckpointStore, prune_seen
from gateway_sli.config import Config
from gateway_sli.pipeline import run


class _Src:
    def __init__(self, records):
        self._records = records

    def read(self):
        return self._records


class _Exp:
    def export(self, points):
        pass


class _BadExp:
    def export(self, points):
        raise RuntimeError("collector down")


def _dt(s: str) -> datetime:
    d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def test_file_checkpoint_roundtrip_and_missing(tmp_path):
    store = FileCheckpointStore(str(tmp_path / "cp.json"))
    assert store.load() is None
    cp = Checkpoint(watermark=_dt("2026-01-15T10:00:00Z"), seen={"a": "2026-01-15T09:59:00+00:00"})
    store.save(cp)
    loaded = store.load()
    assert loaded is not None
    assert loaded.watermark == cp.watermark
    assert loaded.seen == cp.seen


def test_watermark_saved_only_on_export_success(tmp_path, make_raw):
    we = _dt("2026-01-15T09:00:05Z")
    store = FileCheckpointStore(str(tmp_path / "cp.json"))
    run(
        _Src([make_raw(id="a")]),
        Config(),
        _BadExp(),
        window_end=we,
        checkpoint_store=store,
        overlap_minutes=30,
    )
    assert store.load() is None
    run(
        _Src([make_raw(id="a")]),
        Config(),
        _Exp(),
        window_end=we,
        checkpoint_store=store,
        overlap_minutes=30,
    )
    cp = store.load()
    assert cp is not None and cp.watermark == we


def test_first_run_processes_all_and_persists(tmp_path, make_raw):
    store = FileCheckpointStore(str(tmp_path / "cp.json"))
    we = _dt("2026-01-15T09:00:05Z")
    r = run(
        _Src([make_raw(id="A"), make_raw(id="B")]),
        Config(),
        _Exp(),
        window_end=we,
        checkpoint_store=store,
        overlap_minutes=30,
    )
    assert r.stats.cross_run_duplicates == 0
    assert r.stats.observations == 2
    cp = store.load()
    assert cp is not None and cp.watermark == we
    assert set(cp.seen) == {"A", "B"}


def test_cross_run_dedup_across_windows(tmp_path, make_raw):
    store = FileCheckpointStore(str(tmp_path / "cp.json"))
    we1 = _dt("2026-01-15T09:00:05Z")
    run(
        _Src([make_raw(id="A"), make_raw(id="B")]),
        Config(),
        _Exp(),
        window_end=we1,
        checkpoint_store=store,
        overlap_minutes=30,
    )
    we2 = _dt("2026-01-15T09:10:05Z")
    r2 = run(
        _Src([make_raw(id="B"), make_raw(id="C")]),
        Config(),
        _Exp(),
        window_end=we2,
        checkpoint_store=store,
        overlap_minutes=30,
    )
    assert r2.stats.cross_run_duplicates == 1
    assert r2.stats.observations == 1
    xr = [p for p in r2.points if p.name == "gateway.pipeline.cross_run_duplicate_records"]
    assert xr and xr[0].value == 1
    cp2 = store.load()
    assert "C" in cp2.seen and "B" in cp2.seen


def test_seen_pruned_outside_overlap():
    prior = {
        "old": "2026-01-15T08:00:00+00:00",
        "recent": "2026-01-15T09:55:00+00:00",
    }
    current = [("new", _dt("2026-01-15T09:59:00Z"))]
    out = prune_seen(prior, current, cutoff=_dt("2026-01-15T09:50:00Z"))
    assert "old" not in out
    assert "recent" in out
    assert "new" in out


def test_cli_checkpoint_end_to_end(tmp_path):
    from gateway_sli.cli import main

    cp_path = str(tmp_path / "cp.json")
    rc = main(
        [
            "--source",
            "data/sample_traces.json",
            "--emit",
            "console",
            "--window-end",
            "2026-01-15T11:46:00Z",
            "--checkpoint",
            cp_path,
            "--overlap-minutes",
            "120",
        ]
    )
    assert rc == 0
    cp = FileCheckpointStore(cp_path).load()
    assert cp is not None and cp.watermark is not None
    assert cp.seen
