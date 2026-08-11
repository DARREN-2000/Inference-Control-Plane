from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timedelta, timezone

from .checkpoint import DynamoDbCheckpointStore, FileCheckpointStore
from .config import Config
from .emit.console import ConsoleExporter
from .emit.otel import OtelJsonExporter
from .emit.otlp_http import OtlpHttpExporter
from .pipeline import run
from .sources.file_source import FileTraceSource
from .sources.langfuse_api import LangfuseApiTraceSource


class SourceConfigError(RuntimeError):
    """Raised when a requested source is misconfigured (e.g. missing credentials)."""


def build_source(source: str, window_start, window_end):
    """Return a TraceSource for the ``--source`` argument.

    ``\"langfuse\"`` selects the live Langfuse Observations API, reading credentials
    from the environment (never from the command line): ``LANGFUSE_HOST`` or
    ``LANGFUSE_BASE_URL`` (default ``https://cloud.langfuse.com``),
    ``LANGFUSE_PUBLIC_KEY``, ``LANGFUSE_SECRET_KEY``.
    The aggregation window is passed straight through as the closed-window bounds.
    Any other value is treated as a path to a Langfuse export fixture (JSON).
    """
    if source == "langfuse":
        host = (
            os.environ.get("LANGFUSE_HOST")
            or os.environ.get("LANGFUSE_BASE_URL")
            or "https://cloud.langfuse.com"
        )
        public_key = os.environ.get("LANGFUSE_PUBLIC_KEY")
        secret_key = os.environ.get("LANGFUSE_SECRET_KEY")
        missing = [
            name
            for name, val in (
                ("LANGFUSE_PUBLIC_KEY", public_key),
                ("LANGFUSE_SECRET_KEY", secret_key),
            )
            if not val
        ]
        if missing:
            raise SourceConfigError(
                "--source langfuse requires these environment variables: " + ", ".join(missing)
            )
        return LangfuseApiTraceSource(
            host,
            str(public_key),
            str(secret_key),
            from_timestamp=window_start.isoformat() if window_start else None,
            to_timestamp=window_end.isoformat() if window_end else None,
        )
    return FileTraceSource(source)


def build_checkpoint_store(args):
    """Build the checkpoint store selected on the command line, if any.

    ``--checkpoint PATH`` -> local JSON (single-writer/local, tests).
    ``--checkpoint-dynamo-table NAME`` -> durable, concurrency-safe DynamoDB store
    (boto3 imported lazily). The two are mutually exclusive.
    """
    if args.checkpoint and args.checkpoint_dynamo_table:
        raise SourceConfigError("use either --checkpoint or --checkpoint-dynamo-table, not both")
    if args.checkpoint:
        return FileCheckpointStore(args.checkpoint)
    if args.checkpoint_dynamo_table:
        return DynamoDbCheckpointStore.from_boto3(
            args.checkpoint_dynamo_table,
            job_id=args.checkpoint_job_id,
            region_name=args.dynamo_region or os.environ.get("AWS_REGION"),
        )
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gateway-sli",
        description="Derive privacy-safe operational SLIs from Langfuse traces.",
    )
    parser.add_argument(
        "--source",
        default="data/sample_traces.json",
        help="'langfuse' to read the live Langfuse Observations API "
        "(credentials from LANGFUSE_HOST or LANGFUSE_BASE_URL, plus "
        "LANGFUSE_SECRET_KEY env vars), or a path to a Langfuse "
        "export fixture (default).",
    )
    parser.add_argument("--emit", choices=["console", "otel", "otlp-http"], default="console")
    parser.add_argument(
        "--otel-out", default=None, help="Write OTLP/JSON to this path instead of stdout."
    )
    parser.add_argument(
        "--otlp-endpoint",
        default=os.environ.get("OTLP_ENDPOINT"),
        help="Collector base URL for --emit otlp-http (POSTs OTLP/JSON to <endpoint>/v1/metrics).",
    )
    parser.add_argument(
        "--window-minutes",
        type=int,
        default=60,
        help="Nominal aggregation window length (freshness/timestamps).",
    )
    parser.add_argument(
        "--window-end",
        default=None,
        help="ISO-8601 window end (default: now). For a static fixture, "
        "set this near the newest trace so freshness reflects a live run.",
    )
    parser.add_argument(
        "--grace-minutes",
        type=float,
        default=10.0,
        help="Delay the live window end behind now so late traces settle.",
    )
    parser.add_argument(
        "--checkpoint",
        default=None,
        help="Path to a JSON checkpoint file. Enables cross-run "
        "watermark + idempotency: resume from the last "
        "watermark minus --overlap-minutes and de-duplicate "
        "traces re-read in that overlap.",
    )
    parser.add_argument(
        "--checkpoint-dynamo-table",
        default=None,
        help="DynamoDB table for a durable, concurrency-safe "
        "checkpoint (production). Mutually exclusive with "
        "--checkpoint. Requires boto3 + AWS credentials.",
    )
    parser.add_argument(
        "--checkpoint-job-id",
        default="gateway-sli",
        help="Partition key for the DynamoDB checkpoint item (one per logical job/window stream).",
    )
    parser.add_argument(
        "--dynamo-region",
        default=None,
        help="AWS region for the DynamoDB checkpoint (default: $AWS_REGION).",
    )
    parser.add_argument(
        "--overlap-minutes",
        type=float,
        default=10.0,
        help="Trailing look-back re-scanned each run to catch "
        "late-arriving traces (deduped across runs).",
    )
    parser.add_argument(
        "--max-records",
        type=int,
        default=250000,
        help="Safety valve: stop after this many raw records and "
        "flag the window as truncated. Guards against a "
        "pathologically large window (default: 250000).",
    )
    args = parser.parse_args(argv)

    if args.window_minutes <= 0:
        parser.error("--window-minutes must be > 0")
    if args.grace_minutes < 0:
        parser.error("--grace-minutes must be >= 0")
    if args.overlap_minutes < 0:
        parser.error("--overlap-minutes must be >= 0")
    if args.max_records is not None and args.max_records <= 0:
        parser.error("--max-records must be > 0")

    if args.window_end:
        window_end = datetime.fromisoformat(args.window_end.replace("Z", "+00:00"))
        if window_end.tzinfo is None:
            window_end = window_end.replace(tzinfo=timezone.utc)
    else:
        window_end = datetime.now(timezone.utc) - timedelta(minutes=args.grace_minutes)
    window_start = window_end - timedelta(minutes=args.window_minutes)

    try:
        checkpoint_store = build_checkpoint_store(args)
    except SourceConfigError as exc:
        parser.error(str(exc))
    if checkpoint_store is not None:
        resume = checkpoint_store.load()
        if resume is not None and resume.watermark is not None:
            # Resume from the last committed watermark, minus the overlap.
            window_start = resume.watermark - timedelta(minutes=args.overlap_minutes)

    deployment_env = os.environ.get("OTEL_DEPLOYMENT_ENVIRONMENT")
    from typing import Any

    exporter: Any
    if args.emit == "console":
        exporter = ConsoleExporter()
    elif args.emit == "otlp-http":
        if not args.otlp_endpoint:
            parser.error("--emit otlp-http requires --otlp-endpoint")
        exporter = OtlpHttpExporter(
            args.otlp_endpoint,
            window_start=window_start,
            window_end=window_end,
            deployment_environment=deployment_env,
        )
    else:
        exporter = OtelJsonExporter(
            args.otel_out,
            window_start=window_start,
            window_end=window_end,
            deployment_environment=deployment_env,
        )

    try:
        source = build_source(args.source, window_start, window_end)
    except SourceConfigError as exc:
        parser.error(str(exc))

    result = run(
        source,
        Config(),
        exporter,
        window_start=window_start,
        window_end=window_end,
        checkpoint_store=checkpoint_store,
        overlap_minutes=args.overlap_minutes,
        max_records=args.max_records,
    )

    stats = result.stats
    export = "ok" if stats.export_ok else f"FAILED:{stats.export_error}"
    fresh = "n/a" if stats.freshness_seconds is None else f"{stats.freshness_seconds:.0f}s"
    checkpoint_enabled = bool(args.checkpoint or args.checkpoint_dynamo_table)
    xr = f" cross_run_dupes={stats.cross_run_duplicates}" if checkpoint_enabled else ""
    tr = " truncated=1" if stats.read_truncated else ""
    print(
        f"\nread={stats.records_read} processed={stats.observations} "
        f"malformed={stats.malformed} quarantined={stats.quarantined} "
        f"duplicates={stats.duplicates} errors={stats.errors} "
        f"ttft_eligible={stats.ttft_eligible} cost_missing={stats.cost_missing} "
        f"freshness={fresh} export={export}{xr}{tr}",
        file=sys.stderr,
    )
    run_ok = (
        stats.export_ok
        and stats.heartbeat_ok
        and not stats.read_truncated
        and not stats.checkpoint_conflict
    )
    return 0 if run_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
