"""Typed, privacy-projected domain models for Langfuse observations.

``Observation`` is the privacy boundary: it intentionally has no prompt, output,
status-message, trace-id, request-id, tags, or arbitrary metadata fields.  Error
metadata is reduced to a bounded marker before construction.  Consequently a
downstream component cannot accidentally export raw customer content because
that content is not representable in the internal model.

MalformedObservation carries a BOUNDED reason code (never raw content) so the
pipeline can account for schema-level drops by reason without leaking payload.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import math
import re

# Bounded reason codes for schema-level parse failures. Never contains raw data.
MALFORMED_REASONS = frozenset(
    {"unparseable_timestamp", "missing_timestamp", "end_before_start", "missing_observation_id"}
)


class MalformedObservation(Exception):
    """Raised when a raw record cannot be parsed into a valid Observation.

    ``reason`` is a bounded code (see MALFORMED_REASONS); ``detail`` is for logs
    only and is never emitted as a metric dimension.
    """

    def __init__(self, reason: str, detail: str = "") -> None:
        super().__init__(f"{reason}: {detail}" if detail else reason)
        self.reason = reason


_RFC3339 = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})T"
    r"(?P<time>\d{2}:\d{2}:\d{2})"
    r"(?:\.(?P<fraction>\d{1,9}))?"
    r"(?P<zone>Z|[+-]\d{2}:\d{2})$"
)


def _parse_ts(value: str | None) -> datetime | None:
    """Parse the RFC3339 subset emitted by Langfuse and normalize it to UTC.

    This is deliberately strict and dependency-free. It accepts an explicit
    ``Z`` or numeric offset, supports nanosecond input by truncating to Python's
    microsecond precision, and rejects ambiguous timezone-free timestamps.
    """
    if not value:
        return None
    if not isinstance(value, str):
        raise TypeError("timestamp must be a string")
    match = _RFC3339.fullmatch(value.strip())
    if match is None:
        raise ValueError("timestamp must be RFC3339 with an explicit timezone")
    fraction = match.group("fraction")
    fraction_part = f".{(fraction + '000000')[:6]}" if fraction else ""
    zone = "+00:00" if match.group("zone") == "Z" else match.group("zone")
    normalized = f"{match.group('date')}T{match.group('time')}{fraction_part}{zone}"
    return datetime.fromisoformat(normalized).astimezone(timezone.utc)


def _safe_ts(value: str | None) -> datetime | None:
    try:
        return _parse_ts(value)
    except (ValueError, TypeError, AttributeError):
        return None


@dataclass
class Observation:
    obs_id: str
    level: str
    team: str
    route: str
    provided_model: str
    internal_model: str
    env_raw: str
    stream: bool
    start: datetime
    completion_start: datetime | None
    end: datetime
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cache_read_tokens: int
    cost_total: float | None
    cost_invalid: bool
    error: dict | None

    @property
    def is_error(self) -> bool:
        return self.level == "ERROR" or self.error is not None

    @property
    def latency_ms(self) -> float:
        return (self.end - self.start).total_seconds() * 1000.0

    @property
    def ttft_ms(self) -> float | None:
        """Time to first token. Defined only for successful streaming requests
        that recorded a completionStartTime. Non-streaming, failed, or
        missing-timestamp requests are EXCLUDED (returns None), never counted as 0.
        """
        if self.is_error or self.completion_start is None or not self.stream:
            return None
        if not (self.start <= self.completion_start <= self.end):
            return None
        return (self.completion_start - self.start).total_seconds() * 1000.0

    @property
    def is_cache_hit(self) -> bool:
        """True when the provider served cached input tokens for this request."""
        return self.cache_read_tokens > 0


def parse_observation(raw: dict) -> Observation:
    try:
        start = _parse_ts(raw.get("startTime"))
        end = _parse_ts(raw.get("endTime"))
    except (ValueError, TypeError, AttributeError) as exc:
        raise MalformedObservation("unparseable_timestamp", str(exc)) from exc
    if start is None or end is None:
        raise MalformedObservation("missing_timestamp")
    if end < start:
        raise MalformedObservation("end_before_start")

    def _mapping(name: str) -> dict:
        value = raw.get(name)
        return value if isinstance(value, dict) else {}

    tm = _mapping("traceMetadata")
    md = _mapping("metadata")
    usage = _mapping("usageDetails")
    cost = _mapping("costDetails")
    params = _mapping("modelParameters")

    raw_cost_total = cost.get("total")
    cost_total = raw_cost_total
    cost_invalid = False
    if raw_cost_total is not None:
        try:
            parsed_cost = float(raw_cost_total)
            if math.isfinite(parsed_cost) and parsed_cost >= 0:
                cost_total = parsed_cost
            else:
                cost_total = None
                cost_invalid = True
        except (ValueError, TypeError):
            cost_total = None
            cost_invalid = True

    def _int(*candidates: object) -> int:
        for c in candidates:
            if c is not None:
                try:
                    # Reject booleans, negative values and fractional numbers:
                    # all token fields are non-negative integral counters.
                    if isinstance(c, bool):
                        continue
                    f = float(c)  # type: ignore[arg-type]
                    if not math.isfinite(f) or f < 0 or not f.is_integer():
                        continue
                    return int(f)
                except (ValueError, TypeError):
                    continue
        return 0

    stream_raw = params.get("stream", False)
    if isinstance(stream_raw, bool):
        stream = stream_raw
    elif isinstance(stream_raw, str):
        stream = stream_raw.strip().lower() in {"true", "1", "yes"}
    elif isinstance(stream_raw, (int, float)):
        stream = stream_raw == 1
    else:
        stream = False

    # Never retain an arbitrary provider error object.  It can contain messages,
    # stack traces, request ids, or echoed customer data.  Preserve only a
    # bounded type marker needed by normalize.error_category.
    raw_error = md.get("error") if isinstance(md.get("error"), dict) else None
    error = None
    if raw_error is not None:
        raw_type = str(raw_error.get("type") or "").strip().lower()
        safe_types = {
            "throttlingexception",
            "ratelimiterror",
            "ratelimitexception",
            "timeouterror",
            "timeoutexception",
            "serviceunavailable",
            "serviceunavailableexception",
            "internalservererror",
            "modelerrorexception",
            "authenticationerror",
            "accessdeniedexception",
            "badrequesterror",
            "validationexception",
            "contentpolicyviolation",
        }
        error = {"type": raw_type if raw_type in safe_types else "__unknown__"}

    return Observation(
        obs_id=str(raw.get("id") or ""),
        level=str(raw.get("level", "DEFAULT")),
        team=str(tm.get("team", "") or "").strip(),
        route=str(raw.get("traceName", "") or "").strip(),
        provided_model=str(raw.get("providedModelName", "") or ""),
        internal_model=str(raw.get("internalModelId", "") or ""),
        env_raw=str(tm.get("env") or raw.get("environment") or "").strip(),
        stream=stream,
        start=start,
        completion_start=_safe_ts(raw.get("completionStartTime")),
        end=end,
        input_tokens=_int(raw.get("inputUsage"), usage.get("input")),
        output_tokens=_int(raw.get("outputUsage"), usage.get("output")),
        total_tokens=_int(raw.get("totalUsage"), usage.get("total")),
        cache_read_tokens=_int(usage.get("cache_read_input_tokens")),
        cost_total=cost_total,
        cost_invalid=cost_invalid,
        error=error,
    )
