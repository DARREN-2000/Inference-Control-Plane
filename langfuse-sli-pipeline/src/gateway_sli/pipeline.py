"""Orchestration: read -> parse (with quarantine) -> dedup -> aggregate ->
quality -> telemetry-trust self-metrics -> guarded export.

Records are STREAMED one at a time (parse, in-batch + cross-run dedup, fold into
the aggregator and quality accumulator) so a large window never has to be held
in memory at once. Bounded-memory accumulators plus a bounded seen map make the
histogram and quality state are bounded. The exact in-window de-duplication set
is bounded by the required ``max_records`` production safety limit.

This service is OFF the request hot path. If a source or exporter fails it must
never block user traffic: it contains per-record failures, guards the export,
and emits its own trust signals so on-call sees the blind spot rather than a
silent gap. Those self-metrics are the Telemetry Trust Contract (DESIGN 5.6).
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import time

from .checkpoint import Checkpoint, CheckpointConflict, prune_seen
from .config import Config
from .models import MalformedObservation, Observation, parse_observation
from .quality import QualityAccumulator
from .sli import AggregationStats, Aggregator, MetricPoint


@dataclass
class PipelineResult:
    points: list[MetricPoint]
    stats: AggregationStats
    quality: dict  # baseline_key -> status string (mostly cold_start on tiny inputs)
    malformed_by_reason: dict = field(default_factory=dict)


def _dedup(observations: list[Observation]) -> tuple[list[Observation], int]:
    """In-batch idempotency: drop repeated observation ids within one window.

    Retained for direct unit testing and callers that hold the full list; the
    streaming pipeline applies the same rule inline. The production pipeline rejects blank ids as malformed because they cannot
    be de-duplicated safely. Cross-run/window de-duplication
    is handled by the checkpoint layer (see checkpoint.py).
    """
    seen: set[str] = set()
    unique: list[Observation] = []
    duplicates = 0
    for obs in observations:
        if obs.obs_id and obs.obs_id in seen:
            duplicates += 1
            continue
        if obs.obs_id:
            seen.add(obs.obs_id)
        unique.append(obs)
    return unique, duplicates


def _counter(name: str, value: float, dims: dict | None = None, unit: str = "1") -> MetricPoint:
    return MetricPoint(name, "counter", unit, dims or {}, value=value)


def _gauge(name: str, value: float, unit: str = "1") -> MetricPoint:
    return MetricPoint(name, "gauge", unit, {}, value=value)


def run(
    source,
    cfg: Config | None = None,
    exporter=None,
    *,
    window_start: datetime | None = None,
    window_end: datetime | None = None,
    checkpoint_store=None,
    overlap_minutes: float = 10.0,
    max_records: int | None = None,
) -> PipelineResult:
    run_started = time.monotonic()
    cfg = cfg or Config()

    # Cross-run idempotency state is loaded UP FRONT so the streaming pass can
    # drop prior-overlap ids without buffering the window.
    checkpoint = checkpoint_store.load() if checkpoint_store is not None else None
    prior_seen = checkpoint.seen_ids() if checkpoint is not None else set()

    aggregator = Aggregator(cfg)
    quality_acc = QualityAccumulator(cfg)

    # Bound the cross-run seen map to the overlap horizon as we go, so it never
    # grows with window volume.
    collect_seen = checkpoint_store is not None and window_end is not None
    cutoff = window_end - timedelta(minutes=overlap_minutes) if window_end is not None else None
    current_seen: dict[str, datetime] = {}

    malformed_by_reason: dict[str, int] = defaultdict(int)
    quarantined = 0
    duplicates = 0
    cross_run_duplicates = 0
    records_read = 0
    processed = 0
    max_end: datetime | None = None
    read_truncated = False
    seen_batch: set[str] = set()

    source_error: str | None = None

    def guarded_records():
        """Contain failures from source construction *and* lazy iteration.

        A generator normally raises only when advanced, but a valid source adapter
        may raise eagerly from ``iter_records()`` or ``read()`` before returning an
        iterator. Keep lookup, invocation, iterator construction, and iteration in
        the same guard so every broken-source shape becomes bounded trust telemetry
        instead of escaping the pipeline.
        """
        nonlocal source_error
        try:
            iter_records = getattr(source, "iter_records", None)
            raw_iter = iter_records() if callable(iter_records) else iter(source.read())
            yield from raw_iter
        except Exception as exc:  # bounded type only; never raw response content
            source_error = type(exc).__name__

    for raw in guarded_records():
        if max_records is not None and records_read >= max_records:
            read_truncated = True
            break
        records_read += 1
        try:
            obs = parse_observation(raw)
        except MalformedObservation as exc:
            # Expected, schema-level rejection with a bounded reason code.
            malformed_by_reason[exc.reason] += 1
            continue
        except Exception:  # noqa: BLE001 - containment: one poison record must
            # never fail the whole window. Reason is bounded (never raw content).
            quarantined += 1
            malformed_by_reason["unexpected_error"] += 1
            continue

        # An id is the idempotency key.  Processing an id-less record would make
        # DELTA metrics non-idempotent across overlap windows, so fail closed and
        # account for it as bounded malformed telemetry.
        if not obs.obs_id:
            malformed_by_reason["missing_observation_id"] += 1
            continue

        # In-batch idempotency first, then cross-run (same order as _dedup +
        # the checkpoint filter), so counts match the batch implementation.
        if obs.obs_id:
            if obs.obs_id in seen_batch:
                duplicates += 1
                continue
            seen_batch.add(obs.obs_id)
            if obs.obs_id in prior_seen:
                cross_run_duplicates += 1
                continue

        aggregator.add(obs)
        quality_acc.add(obs)
        processed += 1
        if obs.end is not None and (max_end is None or obs.end > max_end):
            max_end = obs.end
        if (
            collect_seen
            and obs.obs_id
            and cutoff is not None
            and obs.end is not None
            and obs.end >= cutoff
        ):
            current_seen[obs.obs_id] = obs.end

    malformed = sum(
        value for reason, value in malformed_by_reason.items() if reason != "unexpected_error"
    )
    points, stats = aggregator.build(malformed, duplicate_count=duplicates)
    stats.cross_run_duplicates = cross_run_duplicates
    stats.records_read = records_read
    stats.quarantined = quarantined
    stats.read_truncated = read_truncated
    if source_error is not None:
        stats.source_ok = False
        stats.source_error = source_error
        stats.export_ok = False
        stats.export_error = "skipped_source_failure"

    # --- quality: per-window anomaly COUNT (+ max |z|), never a latest-value gauge ---
    quality: dict[str, str] = {}
    for key, result in quality_acc.results().items():
        label = "|".join(key.as_dict().values())
        quality[label] = result.status
        if result.status in ("ok", "degenerate_constant_baseline"):
            points.append(
                _counter(
                    "gateway.quality.completion_length_anomalies",
                    result.anomaly_count,
                    key.as_dict(),
                )
            )
            if result.max_abs_z is not None:
                points.append(
                    MetricPoint(
                        "gateway.quality.completion_length_max_zscore",
                        "gauge",
                        "score",
                        key.as_dict(),
                        value=round(result.max_abs_z, 4),
                    )
                )
    for key, count in quality_acc.empty_counts.items():
        points.append(_counter("gateway.quality.empty_completion_count", count, key.as_dict()))

    # --- Telemetry Trust Contract self-metrics (completeness + freshness) ---
    points.append(_counter("gateway.pipeline.records_read", records_read))
    points.append(_counter("gateway.pipeline.records_processed", processed))
    if cross_run_duplicates:
        points.append(
            _counter("gateway.pipeline.cross_run_duplicate_records", cross_run_duplicates)
        )
    if quarantined:
        points.append(_counter("gateway.pipeline.quarantined_records", quarantined))
    if read_truncated:
        # Safety valve tripped: the window exceeded --max-records and was read
        # only partially, so DELTA counters UNDERCOUNT it. Emitted as a loud,
        # alertable signal rather than failing silently.
        points.append(_gauge("gateway.pipeline.read_truncated", 1.0))
    if stats.cost_missing:
        points.append(_counter("gateway.pipeline.records_missing_cost", stats.cost_missing))
    if stats.cost_invalid:
        points.append(_counter("gateway.pipeline.records_invalid_cost", stats.cost_invalid))

    # Source implementations expose bounded operational counters without raw
    # URLs, bodies, cursor values, or credentials.
    source_stats = getattr(source, "stats", None)
    if isinstance(source_stats, dict):
        for stat_key, metric in (
            ("requests", "gateway.pipeline.source_requests"),
            ("retries", "gateway.pipeline.source_retries"),
            ("pages", "gateway.pipeline.source_pages"),
        ):
            value = source_stats.get(stat_key, 0)
            if value:
                points.append(_counter(metric, value))
        latency = source_stats.get("latency_seconds", 0.0)
        if latency:
            points.append(_gauge("gateway.pipeline.source_latency_seconds", latency, unit="s"))
    if window_end is not None and max_end is not None:
        raw_freshness = (window_end - max_end).total_seconds()
        if raw_freshness < 0:
            points.append(_gauge("gateway.pipeline.clock_skew_seconds", -raw_freshness, unit="s"))
        freshness = max(0.0, raw_freshness)
        stats.freshness_seconds = freshness
        points.append(_gauge("gateway.pipeline.freshness_seconds", freshness, unit="s"))

    # Cardinality health: how many workload series this window emitted.
    workload_series = sum(
        1
        for p in points
        if p.name.startswith("gateway.")
        and not p.name.startswith("gateway.pipeline.")
        and not p.name.startswith("gateway.quality.")
    )
    points.append(_gauge("gateway.pipeline.series_emitted", workload_series))

    # --- guarded main flush; a failing exporter must not crash the batch ---
    if exporter is not None and stats.source_ok:
        try:
            exporter.export(points)
        except Exception as exc:  # noqa: BLE001
            stats.export_ok = False
            stats.export_error = type(exc).__name__

    # Export health is emitted as a SEPARATE run-completion heartbeat, not
    # appended to the single main flush. Appending after the only export() call
    # (the previous behavior) meant the value could never actually reach the
    # backend - it was visible in the returned result but never transmitted. We
    # now send it on a separate exporter.heartbeat() call, so a partly- or
    # fully-failing main flush still surfaces export_success=0 through a distinct
    # path. It is a gauge (last-value-wins), so a separate call never
    # double-counts. If the exporter exposes no heartbeat channel we still append
    # it to the returned points for local inspection.
    export_health = _gauge("gateway.pipeline.export_success", 1.0 if stats.export_ok else 0.0)
    points.append(export_health)
    heartbeat_points = [export_health]
    if not stats.source_ok:
        source_health = _gauge("gateway.pipeline.source_success", 0.0)
        points.append(source_health)
        heartbeat_points.append(source_health)
    heartbeat = getattr(exporter, "heartbeat", None) if exporter is not None else None
    if heartbeat is not None:
        try:
            heartbeat(heartbeat_points)
        except Exception as exc:  # noqa: BLE001
            stats.heartbeat_ok = False
            stats.export_error = stats.export_error or type(exc).__name__

    # --- advance the watermark ONLY after a clean export, so a failed run is
    # retried from the same point instead of skipping a window. The seen set
    # is pruned to the overlap horizon so it stays bounded. A concurrent writer
    # winning the conditional write is surfaced; it is not considered a clean run. ---
    if (
        checkpoint_store is not None
        and window_end is not None
        and stats.export_ok
        and stats.heartbeat_ok
        and not stats.read_truncated
    ):
        cutoff_save = window_end - timedelta(minutes=overlap_minutes)
        prior_map = checkpoint.seen if checkpoint is not None else {}
        current = list(current_seen.items())
        new_seen = prune_seen(prior_map, current, cutoff=cutoff_save)
        try:
            checkpoint_store.save(Checkpoint(watermark=window_end, seen=new_seen))
        except CheckpointConflict:
            stats.checkpoint_conflict = True

    # Final operational heartbeat is computed after export and checkpoint work,
    # so run_duration is genuinely end-to-end and a checkpoint conflict actually
    # crosses the exporter boundary rather than existing only in the return value.
    final_health = [
        _gauge(
            "gateway.pipeline.run_duration_seconds",
            max(0.0, time.monotonic() - run_started),
            unit="s",
        )
    ]
    if stats.checkpoint_conflict:
        final_health.append(_counter("gateway.pipeline.checkpoint_conflicts", 1))
    points.extend(final_health)
    if heartbeat is not None:
        try:
            heartbeat(final_health)
        except Exception as exc:  # noqa: BLE001
            stats.heartbeat_ok = False
            stats.export_error = stats.export_error or type(exc).__name__

    return PipelineResult(
        points=points,
        stats=stats,
        quality=quality,
        malformed_by_reason=dict(malformed_by_reason),
    )
