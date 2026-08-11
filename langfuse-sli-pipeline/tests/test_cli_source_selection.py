"""The CLI must actually wire --source langfuse to the live API adapter, not just
the file source -- otherwise the documented deployment command would silently
read a file path named 'langfuse'. Credentials come only from the environment.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone

from gateway_sli.cli import SourceConfigError, build_source
from gateway_sli.sources.file_source import FileTraceSource
from gateway_sli.sources.langfuse_api import LangfuseApiTraceSource

WS = datetime(2026, 1, 15, 10, 46, tzinfo=timezone.utc)
WE = datetime(2026, 1, 15, 11, 46, tzinfo=timezone.utc)


def test_file_source_selected_for_path():
    src = build_source("data/sample_traces.json", WS, WE)
    assert isinstance(src, FileTraceSource)


def test_langfuse_source_selected_with_env():
    os.environ["LANGFUSE_HOST"] = "https://lf.example.com"
    os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-test"
    os.environ["LANGFUSE_SECRET_KEY"] = "sk-test"
    src = build_source("langfuse", WS, WE)
    assert isinstance(src, LangfuseApiTraceSource)
    assert src.base_url == "https://lf.example.com"
    # Window is threaded through as the closed-window bounds (ISO-8601).
    assert src.from_timestamp == WS.isoformat()
    assert src.to_timestamp == WE.isoformat()


def test_langfuse_base_url_alias_selected():
    os.environ.pop("LANGFUSE_HOST", None)
    os.environ["LANGFUSE_BASE_URL"] = "https://lf-alias.example.com/"
    os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-test"
    os.environ["LANGFUSE_SECRET_KEY"] = "sk-test"
    src = build_source("langfuse", WS, WE)
    assert isinstance(src, LangfuseApiTraceSource)
    assert src.base_url == "https://lf-alias.example.com"
    os.environ.pop("LANGFUSE_BASE_URL", None)


def test_langfuse_source_requires_credentials():
    for key in ("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"):
        os.environ.pop(key, None)
    raised = False
    try:
        build_source("langfuse", WS, WE)
    except SourceConfigError as exc:
        raised = True
        assert "LANGFUSE_PUBLIC_KEY" in str(exc)
        assert "LANGFUSE_SECRET_KEY" in str(exc)
    assert raised, "missing credentials must raise SourceConfigError"
