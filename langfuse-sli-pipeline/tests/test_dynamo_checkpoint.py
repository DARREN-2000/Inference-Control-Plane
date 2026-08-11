"""DynamoDbCheckpointStore is exercised through an in-memory fake DynamoDB client
that honors conditional writes, so optimistic concurrency is verified without a
live table or boto3. A tiny local ``raises`` helper keeps this file runnable
under both the canonical suite and the zero-dependency offline runner."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone

from gateway_sli.checkpoint import (
    Checkpoint,
    CheckpointConflict,
    ConditionalCheckFailed,
    DynamoDbCheckpointStore,
)
from gateway_sli.config import Config
from gateway_sli.pipeline import run


@contextmanager
def raises(exc_type):
    try:
        yield
    except exc_type:
        return
    except Exception as exc:  # noqa: BLE001
        raise AssertionError(f"expected {exc_type.__name__}, got {type(exc).__name__}") from exc
    raise AssertionError(f"expected {exc_type.__name__}, nothing raised")


class FakeDynamo:
    """Minimal DynamoDB stand-in: one item per job_id, conditional put support."""

    def __init__(self):
        self.items: dict[str, dict] = {}
        self.put_calls = 0

    def get_item(self, *, TableName, Key):
        job_id = Key["job_id"]["S"]
        item = self.items.get(job_id)
        return {"Item": item} if item is not None else {}

    def put_item(
        self, *, TableName, Item, ConditionExpression=None, ExpressionAttributeValues=None
    ):
        self.put_calls += 1
        job_id = Item["job_id"]["S"]
        existing = self.items.get(job_id)
        if ConditionExpression == "attribute_not_exists(job_id)":
            if existing is not None:
                raise ConditionalCheckFailed("exists")
        elif ConditionExpression == "version = :expected":
            expected = ExpressionAttributeValues[":expected"]["N"]
            if existing is None or existing["version"]["N"] != expected:
                raise ConditionalCheckFailed("version mismatch")
        self.items[job_id] = Item


def test_roundtrip_and_first_write():
    client = FakeDynamo()
    store = DynamoDbCheckpointStore(client, "tbl", job_id="j")
    assert store.load() is None
    wm = datetime(2026, 1, 15, 11, 0, tzinfo=timezone.utc)
    store.save(Checkpoint(watermark=wm, seen={"a": wm.isoformat()}))
    loaded = store.load()
    assert loaded is not None
    assert loaded.watermark == wm
    assert "a" in loaded.seen_ids()


def test_optimistic_concurrency_conflict():
    client = FakeDynamo()
    a = DynamoDbCheckpointStore(client, "tbl", job_id="j")
    b = DynamoDbCheckpointStore(client, "tbl", job_id="j")
    wm = datetime(2026, 1, 15, 11, 0, tzinfo=timezone.utc)
    a.save(Checkpoint(watermark=wm, seen={}))
    a.load()
    b.load()  # both read version 1
    wm2 = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)
    a.save(Checkpoint(watermark=wm2, seen={}))  # a wins -> version 2
    with raises(CheckpointConflict):
        b.save(Checkpoint(watermark=wm2, seen={}))  # b stale -> conflict


def test_first_write_conflict_when_item_appears():
    client = FakeDynamo()
    a = DynamoDbCheckpointStore(client, "tbl", job_id="j")
    b = DynamoDbCheckpointStore(client, "tbl", job_id="j")
    wm = datetime(2026, 1, 15, 11, 0, tzinfo=timezone.utc)
    a.load()
    b.load()  # both see empty -> both attempt first write
    a.save(Checkpoint(watermark=wm, seen={}))
    with raises(CheckpointConflict):
        b.save(Checkpoint(watermark=wm, seen={}))


def test_pipeline_saves_to_dynamo(make_raw):
    client = FakeDynamo()
    store = DynamoDbCheckpointStore(client, "tbl", job_id="j")
    rows = [make_raw(id=f"o-{i}") for i in range(5)]
    we = datetime(2026, 1, 15, 11, 46, tzinfo=timezone.utc)
    run(_L(rows), Config(), window_end=we, checkpoint_store=store)
    loaded = store.load()
    assert loaded is not None and loaded.watermark == we


class _ConflictStore:
    """Store whose save() always conflicts; the pipeline must surface it without clobbering state."""

    def load(self):
        return None

    def save(self, checkpoint):
        raise CheckpointConflict("lost race")


def test_pipeline_checkpoint_conflict_is_surfaced(make_raw):
    rows = [make_raw(id=f"o-{i}") for i in range(3)]
    we = datetime(2026, 1, 15, 11, 46, tzinfo=timezone.utc)
    result = run(_L(rows), Config(), window_end=we, checkpoint_store=_ConflictStore())
    assert result.stats.checkpoint_conflict is True
    assert any(p.name == "gateway.pipeline.checkpoint_conflicts" for p in result.points)
    assert result.stats.observations == 3


class _L:
    def __init__(self, rows):
        self._rows = rows

    def read(self):
        return list(self._rows)
