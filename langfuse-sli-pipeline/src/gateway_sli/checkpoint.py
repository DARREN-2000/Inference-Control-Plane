"""Cross-run checkpoint + watermark persistence with cross-run idempotency.

The pipeline processes one bounded, closed window per run. To make consecutive
runs correct across process restarts we persist two things:

  * a WATERMARK - the end of the last successfully-exported window, so the next
    run resumes from there (minus a trailing overlap) instead of guessing; and
  * a bounded SEEN map - observation id -> end timestamp, for ids whose end
    falls inside the trailing overlap window, so a trace re-read in the next
    run's overlap is de-duplicated ACROSS runs rather than double-counted.

Correctness properties:
  * The watermark advances ONLY after a clean export (the caller guards on
    export health), so a failed run is safely retried from the same point
    rather than silently skipping a window of data.
  * The seen map is PRUNED to the overlap horizon every run, so it stays
    O(traces in one overlap window) and never grows unbounded.
  * Metrics are DELTA temporality, so re-emitting a re-read window would
    double-count; the seen map prevents that at the observation level.

Two stores implement the same two-method interface:
  * FileCheckpointStore - local JSON, atomic write; single-writer/local + tests.
  * DynamoDbCheckpointStore - durable + concurrency-safe (optimistic version via
    a conditional write); the production store for ephemeral, possibly-
    overlapping tasks. Only ids and timestamps are persisted - never raw content.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol

from .models import _parse_ts


@dataclass
class Checkpoint:
    """Persisted cross-run state. ``seen`` maps observation id -> ISO end time."""

    watermark: datetime | None = None
    seen: dict[str, str] = field(default_factory=dict)

    def seen_ids(self) -> set[str]:
        return set(self.seen)

    def to_json(self) -> dict:
        return {
            "version": 1,
            "watermark": self.watermark.isoformat() if self.watermark else None,
            "seen": self.seen,
        }

    @classmethod
    def from_json(cls, payload: dict) -> "Checkpoint":
        return cls(
            watermark=_parse_ts(payload.get("watermark")),
            seen=dict(payload.get("seen") or {}),
        )


class CheckpointStore(Protocol):
    """Load/save the cross-run checkpoint. Implementations must be durable enough
    that a crash between runs never loses a committed watermark.
    """

    def load(self) -> "Checkpoint | None": ...

    def save(self, cp: "Checkpoint") -> None: ...


class FileCheckpointStore:
    """Local JSON checkpoint written atomically (temp file + os.replace).

    ``load`` returns None when no checkpoint exists yet (first run). A corrupt
    state file raises rather than being silently treated as \"no checkpoint\", so
    it fails loudly instead of silently re-processing all of history.
    """

    def __init__(self, path: str) -> None:
        self.path = path

    def load(self) -> "Checkpoint | None":
        if not os.path.exists(self.path):
            return None
        if os.path.getsize(self.path) == 0:
            return None
        with open(self.path, encoding="utf-8") as fh:
            return Checkpoint.from_json(json.load(fh))

    def save(self, cp: "Checkpoint") -> None:
        directory = os.path.dirname(os.path.abspath(self.path))
        os.makedirs(directory, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=directory, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(cp.to_json(), fh, sort_keys=True)
            os.replace(tmp, self.path)
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)


class ConditionalCheckFailed(Exception):
    """Low-level signal that a DynamoDB conditional write failed (another writer
    advanced the item first). Raised by the injected client / boto3 adapter and
    translated into :class:`CheckpointConflict` by the store."""


class CheckpointConflict(RuntimeError):
    """A concurrent writer committed a newer checkpoint for this job.

    Another worker already committed this (or a later) window, so this run must
    NOT overwrite it. The pipeline surfaces the conflict and the CLI fails the
    run. The conditional write protects the watermark; because detection follows
    export, delivery remains explicitly at-least-once.
    """


class DynamoClient(Protocol):
    """Minimal DynamoDB client surface used by :class:`DynamoDbCheckpointStore`.

    Matches the boto3 ``dynamodb`` client call shape (keyword-only, AttributeValue
    maps) so the real client drops in unchanged. ``put_item`` must raise
    :class:`ConditionalCheckFailed` when its ``ConditionExpression`` is not met.
    """

    def get_item(self, *, TableName: str, Key: dict) -> dict: ...

    def put_item(
        self,
        *,
        TableName: str,
        Item: dict,
        ConditionExpression: str | None = None,
        ExpressionAttributeValues: dict | None = None,
    ) -> dict: ...


class DynamoDbCheckpointStore:
    """Durable, concurrency-safe checkpoint store backed by a single DynamoDB item.

    This is the production store the module docstring refers to. It provides the
    two guarantees a local file cannot on ephemeral, possibly-overlapping tasks:

      * **Durability** across task restarts (the item outlives any Fargate task),
        so a committed watermark is never lost; and
      * **Single-writer-wins concurrency** via an optimistic ``version`` counter
        enforced with a conditional write. If two tasks race the same window,
        exactly one commit succeeds; the loser gets :class:`CheckpointConflict`
        instead of silently clobbering a newer watermark.

    Item schema (values are DynamoDB AttributeValue maps)::

        { "job_id": {"S": <job>},          # partition key
          "version": {"N": <int>},         # optimistic-concurrency token
          "watermark": {"S": <iso8601>},   # last cleanly-exported window end
          "seen": {"S": <json map>} }      # bounded id -> end-iso overlap map
    """

    def __init__(
        self,
        client: DynamoClient,
        table_name: str,
        *,
        job_id: str = "gateway-sli",
    ) -> None:
        self._client = client
        self._table = table_name
        self._job_id = job_id
        self._version = 0  # 0 => item does not exist yet (first run)

    @classmethod
    def from_boto3(
        cls,
        table_name: str,
        *,
        job_id: str = "gateway-sli",
        region_name: str | None = None,
        client=None,
    ) -> "DynamoDbCheckpointStore":
        """Build a store around a real boto3 DynamoDB client (imported lazily so
        the default install stays dependency-free). Pass ``client`` to reuse a
        session."""
        if client is None:
            import boto3  # lazy: only needed when the DynamoDB store is selected

            client = boto3.client("dynamodb", region_name=region_name)
        return cls(Boto3DynamoClient(client), table_name, job_id=job_id)

    def load(self) -> "Checkpoint | None":
        resp = self._client.get_item(TableName=self._table, Key={"job_id": {"S": self._job_id}})
        item = resp.get("Item") if resp else None
        if not item:
            self._version = 0
            return None
        self._version = int(item["version"]["N"])
        watermark = item.get("watermark", {}).get("S")
        seen_raw = item.get("seen", {}).get("S")
        seen = json.loads(seen_raw) if seen_raw else {}
        return Checkpoint(watermark=_parse_ts(watermark), seen=seen)

    def save(self, cp: "Checkpoint") -> None:
        new_version = self._version + 1
        item: dict = {
            "job_id": {"S": self._job_id},
            "version": {"N": str(new_version)},
            "seen": {"S": json.dumps(cp.seen, sort_keys=True)},
        }
        if cp.watermark is not None:
            item["watermark"] = {"S": cp.watermark.isoformat()}
        try:
            if self._version == 0:
                self._client.put_item(
                    TableName=self._table,
                    Item=item,
                    ConditionExpression="attribute_not_exists(job_id)",
                )
            else:
                self._client.put_item(
                    TableName=self._table,
                    Item=item,
                    ConditionExpression="version = :expected",
                    ExpressionAttributeValues={":expected": {"N": str(self._version)}},
                )
        except ConditionalCheckFailed as exc:
            raise CheckpointConflict(
                f"checkpoint for job '{self._job_id}' was advanced by another "
                f"writer (expected version {self._version})"
            ) from exc
        self._version = new_version


class Boto3DynamoClient:
    """Adapt a boto3 ``dynamodb`` client to :class:`DynamoClient`, translating a
    conditional-check failure into :class:`ConditionalCheckFailed` so the store
    stays decoupled from botocore exception types."""

    def __init__(self, client) -> None:
        self._client = client

    def get_item(self, *, TableName: str, Key: dict) -> dict:
        return self._client.get_item(TableName=TableName, Key=Key)

    def put_item(
        self,
        *,
        TableName: str,
        Item: dict,
        ConditionExpression: str | None = None,
        ExpressionAttributeValues: dict | None = None,
    ) -> dict:
        kwargs: dict = {"TableName": TableName, "Item": Item}
        if ConditionExpression is not None:
            kwargs["ConditionExpression"] = ConditionExpression
        if ExpressionAttributeValues is not None:
            kwargs["ExpressionAttributeValues"] = ExpressionAttributeValues
        try:
            return self._client.put_item(**kwargs)
        except Exception as exc:  # noqa: BLE001 - narrowed by DynamoDB error code
            response = getattr(exc, "response", None) or {}
            code = response.get("Error", {}).get("Code")
            if code == "ConditionalCheckFailedException":
                raise ConditionalCheckFailed(str(exc)) from exc
            raise


def prune_seen(
    prior: dict[str, str],
    current: list[tuple[str, datetime]],
    *,
    cutoff: datetime,
) -> dict[str, str]:
    """Merge prior + current seen ids, retaining only those whose end >= cutoff.

    ``prior`` is the previous seen map; ``current`` is (id, end) for this window.
    Ids older than the overlap horizon are dropped so the set stays bounded to
    one overlap window's worth of traces.
    """
    out: dict[str, str] = {}
    for oid, end_iso in prior.items():
        try:
            end = _parse_ts(end_iso)
        except (ValueError, TypeError, AttributeError):
            continue
        if oid and end is not None and end >= cutoff:
            out[oid] = end_iso
    for oid, end in current:
        if oid and end >= cutoff:
            out[oid] = end.isoformat()
    return out
