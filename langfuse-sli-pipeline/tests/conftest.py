from __future__ import annotations

import copy

try:
    import pytest
except ModuleNotFoundError:  # offline runner fallback; canonical suite uses pytest
    pytest = None

# A realistic, valid GENERATION observation matching the Langfuse export schema.
# PII/raw content fields are present so privacy tests can prove they never leak.
_BASE = {
    "id": "obs-base",
    "traceId": "trace-base",
    "type": "GENERATION",
    "name": "litellm-completion",
    "startTime": "2026-01-15T09:00:00.000Z",
    "completionStartTime": "2026-01-15T09:00:00.400Z",
    "endTime": "2026-01-15T09:00:02.000Z",
    "level": "DEFAULT",
    "statusMessage": "",
    "environment": "production",
    "traceName": "advisorchat-turn",
    "traceMetadata": {
        "team": "AdvisorChat",
        "product": "chat",
        "env": "prod",
        "data_class": "pii_sensitive",
    },
    "traceTags": ["streaming", "rag"],
    "input": "Customer SSN is 123-45-6789 PIISECRET",
    "output": "Your portfolio PIISECRET details ...",
    "metadata": {
        "litellm_call_id": "call-PIISECRET-999",
        "litellm_proxy_key_alias": "key-advisorchat-prod",
        "request_id": "req-PIISECRET-abc",
    },
    "providedModelName": "claude-sonnet-4-6",
    "internalModelId": "eu.anthropic.claude-sonnet-4-6",
    "modelParameters": {"temperature": 0.2, "max_tokens": 1024, "stream": True},
    "usageDetails": {"input": 600, "output": 200, "total": 800},
    "inputUsage": 600,
    "outputUsage": 200,
    "totalUsage": 800,
    "costDetails": {"input": 0.001, "output": 0.003, "total": 0.004},
}


def _make_raw_impl():
    def _make(**overrides):
        record = copy.deepcopy(_BASE)
        record.update(overrides)
        return record

    return _make


if pytest is not None:
    make_raw = pytest.fixture(_make_raw_impl)
