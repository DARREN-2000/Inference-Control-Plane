"""Property/fuzz invariants for the Metric Governance + privacy contracts.

Throws thousands of hostile, malformed, and adversarial records at the pipeline
and asserts the guarantees the design claims hold NO MATTER the input:

  1. Totality        every input record is accounted for (processed, malformed,
                     or de-duplicated) and the pipeline never raises.
  2. Governed values every emitted dimension value is drawn from its declared
                     vocabulary in the governance registry - no free-text label,
                     no unbounded cardinality.
  3. Cardinality     distinct primary series never exceed estimated_max_series().
  4. Privacy         no raw content / PII / high-cardinality id ever reaches the
                     serialized OTLP payload.
"""

from __future__ import annotations

import json
import random

from gateway_sli.config import Config
from gateway_sli.emit.otel import OtelJsonExporter
from gateway_sli.governance import PRIMARY_DIMENSIONS, REGISTRY, estimated_max_series
from gateway_sli.pipeline import run

# Embedded in every raw content / id field. If governance or the privacy
# projection ever leaked, this string would surface in the serialized export.
SENTINEL = "ZZ_PII_SENTINEL_ZZ"

_TEAMS = [
    "AdvisorChat",
    "KYC",
    "DevAgent",
    "DigestBot",
    "Research",
    "Marketing",
    "advisorchat",
    "ADVISORCHAT",
    "TotallyNewTeam",
    "m\u00fcnchen",
    "",
    "  ",
    "x" * 200,
    "team-<script>alert(1)</script>",
]
_ROUTES = [
    "advisorchat-turn",
    "digestbot-summary",
    "new-unregistered-route",
    "session-4f9a2c-user-42",
    "Has Spaces And CAPS!",
    "",
    "UPPER-CASE",
    "a" * 200,
    "kyc.verify.step-1",
    "'; DROP TABLE metrics;--",
]
_ENVS = ["production", "prod", "staging", "dev", "development", "qa", "", "PROD"]
_MODELS = [
    "claude-sonnet-4-6",
    "claude-haiku-4-5",
    "claude-opus-4",
    "gpt-5.4",
    "gpt-5-mini",
    "gpt-4o",
    "mistral-large",
    "llama-3",
    "",
    "gpt-5-nano-mini",
]
_INTERNAL = [
    "eu.anthropic.claude-sonnet-4-6",
    "us.anthropic.claude-haiku-4-5",
    "external.openai.gpt-5",
    "on-prem.mistral",
    "",
    "eu.anthropic",
]
_ERR_TYPES = [
    "ThrottlingException",
    "TimeoutError",
    "AccessDeniedException",
    "ValidationException",
    "SomethingBrandNew",
    "ContentPolicyViolation",
    None,
]


class _ListSource:
    def __init__(self, records):
        self._records = records

    def read(self):
        return self._records


def _fuzz_records(make_raw, n=2500):
    rng = random.Random(20260710)
    out = []
    for _ in range(n):
        s = rng.randint(0, 40)
        d = rng.randint(1, 15)
        start = f"2026-01-15T09:10:{s:02d}.000Z"
        end = f"2026-01-15T09:10:{s + d:02d}.000Z"
        comp = f"2026-01-15T09:10:{s:02d}.400Z"
        out_tok = rng.choice([50, 100, 150, 200, 250, 5000])
        ov = {
            "id": rng.choice(["", f"obs-{rng.randint(0, 60)}"]),
            "traceName": rng.choice(_ROUTES),
            "traceMetadata": {
                "team": rng.choice(_TEAMS),
                "env": rng.choice(_ENVS),
                "product": "x",
                "data_class": "pii_sensitive",
            },
            "providedModelName": rng.choice(_MODELS),
            "internalModelId": rng.choice(_INTERNAL),
            "input": f"{SENTINEL} customer ssn 123-45-6789 {rng.random()}",
            "output": f"{SENTINEL} response body",
            "startTime": start,
            "completionStartTime": comp,
            "endTime": end,
            "usageDetails": {"input": 600, "output": out_tok, "total": 600 + out_tok},
            "inputUsage": 600,
            "outputUsage": out_tok,
            "totalUsage": 600 + out_tok,
        }
        if rng.random() < 0.25:  # error record
            et = rng.choice(_ERR_TYPES)
            ov["level"] = "ERROR"
            ov["completionStartTime"] = None
            ov["output"] = None
            ov["statusMessage"] = f"{SENTINEL} boom in eu-central-1"
            md = {"request_id": f"req-{SENTINEL}"}
            if et:
                md["error"] = {"type": et, "provider": "bedrock", "retryable": True}
            ov["metadata"] = md
        c = rng.random()
        if c < 0.15:
            ov["costDetails"] = {}
        elif c < 0.25:
            ov["costDetails"] = {"total": "not-a-number"}
        f = rng.random()
        if f < 0.05:
            ov["startTime"] = None  # missing timestamp -> malformed
        elif f < 0.09:
            ov["startTime"], ov["endTime"] = end, start  # end before start
        elif f < 0.12:
            ov["startTime"] = "garbage-timestamp"  # unparseable
        out.append(make_raw(**ov))
    return out


def test_fuzz_pipeline_is_total_and_never_raises(make_raw):
    records = _fuzz_records(make_raw)
    result = run(_ListSource(records), Config())
    # Every input is accounted for: processed, rejected as malformed, or deduped.
    assert result.stats.records_read == len(records)
    assert (result.stats.observations + result.stats.malformed + result.stats.duplicates) == len(
        records
    )


def test_fuzz_every_emitted_value_is_governed(make_raw):
    result = run(_ListSource(_fuzz_records(make_raw)), Config())
    assert result.points
    for p in result.points:
        for key, value in p.dims.items():
            assert key in REGISTRY, (p.name, key)
            assert value in REGISTRY[key].vocabulary, (p.name, key, value)


def test_fuzz_primary_series_within_estimated_max(make_raw):
    result = run(_ListSource(_fuzz_records(make_raw)), Config())
    series = {
        tuple(p.dims[k] for k in PRIMARY_DIMENSIONS)
        for p in result.points
        if all(k in p.dims for k in PRIMARY_DIMENSIONS)
    }
    assert series  # the fuzz actually exercised workload series
    assert len(series) <= estimated_max_series()


def test_fuzz_no_pii_in_serialized_export(make_raw):
    result = run(_ListSource(_fuzz_records(make_raw)), Config())
    blob = json.dumps(OtelJsonExporter().export(result.points))
    assert SENTINEL not in blob
    for banned in (
        "123-45-6789",
        "eu-central-1",
        "not-a-number",
        "garbage-timestamp",
        "m\u00fcnchen",
        "DROP TABLE",
    ):
        assert banned not in blob, banned
