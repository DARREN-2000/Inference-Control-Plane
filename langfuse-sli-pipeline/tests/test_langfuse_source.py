"""Unit tests for the live Langfuse adapter using an injected transport, so the
pagination / auth / windowing / 429-backoff contract is exercised without a live
API (the network call itself is the only unverified layer).
"""

import json

from gateway_sli.sources.langfuse_api import (
    LangfuseApiError,
    LangfuseApiTraceSource,
    LangfuseSourceIncomplete,
)


def make_transport(responses):
    state = {"n": 0, "calls": []}

    def transport(url, headers):
        state["calls"].append((url, headers))
        resp = responses[min(state["n"], len(responses) - 1)]
        state["n"] += 1
        return resp

    transport.state = state
    return transport


def _resp(data, *, cursor=None, page=1, total_pages=1, status=200, headers=None):
    body = json.dumps(
        {"data": data, "meta": {"cursor": cursor, "page": page, "totalPages": total_pages}}
    )
    return (status, headers or {}, body)


def test_pagination_concatenates_all_pages():
    responses = [
        _resp([{"id": "a"}], page=1, total_pages=3),
        _resp([{"id": "b"}], page=2, total_pages=3),
        _resp([{"id": "c"}], page=3, total_pages=3),
    ]
    t = make_transport(responses)
    src = LangfuseApiTraceSource("https://lf.example", "pk", "sk", transport=t, page_limit=1)
    out = src.read()
    assert [o["id"] for o in out] == ["a", "b", "c"]
    assert t.state["n"] == 3


def test_cursor_pagination_followed_when_present():
    responses = [
        _resp([{"id": "a"}], cursor="c1"),
        _resp([{"id": "b"}], cursor=None),
    ]
    t = make_transport(responses)
    src = LangfuseApiTraceSource("https://lf.example", "pk", "sk", transport=t)
    out = src.read()
    assert [o["id"] for o in out] == ["a", "b"]


def test_basic_auth_header_present():
    t = make_transport([_resp([], page=1, total_pages=1)])
    src = LangfuseApiTraceSource("https://lf.example", "pk", "sk", transport=t)
    src.read()
    _, headers = t.state["calls"][0]
    assert headers["Authorization"].startswith("Basic ")


def test_429_is_retried_with_backoff():
    slept = []
    responses = [
        (429, {"Retry-After": "0"}, ""),
        _resp([{"id": "a"}], page=1, total_pages=1),
    ]
    t = make_transport(responses)
    src = LangfuseApiTraceSource("https://lf.example", "pk", "sk", transport=t, sleep=slept.append)
    out = src.read()
    assert [o["id"] for o in out] == ["a"]
    assert slept  # backoff slept at least once
    assert src.stats["retries"] == 1
    assert src.stats["requests"] == 2


def test_http_error_raises():
    t = make_transport([(500, {}, "boom")])
    src = LangfuseApiTraceSource("https://lf.example", "pk", "sk", transport=t)
    try:
        src.read()
    except LangfuseApiError as exc:
        assert exc.status == 500
    else:
        raise AssertionError("expected LangfuseApiError")


def test_window_and_type_params_included():
    t = make_transport([_resp([], page=1, total_pages=1)])
    src = LangfuseApiTraceSource(
        "https://lf.example",
        "pk",
        "sk",
        transport=t,
        from_timestamp="2026-01-15T10:00:00Z",
        to_timestamp="2026-01-15T11:00:00Z",
    )
    src.read()
    url, _ = t.state["calls"][0]
    assert "type=GENERATION" in url
    assert "fromStartTime" in url and "toStartTime" in url


def test_empty_cursor_page_is_incomplete_not_success():
    t = make_transport([_resp([], cursor="still-more")])
    src = LangfuseApiTraceSource("https://lf.example", "pk", "sk", transport=t)
    try:
        src.read()
    except LangfuseSourceIncomplete:
        return
    raise AssertionError("contradictory empty cursor page must fail closed")


def test_non_object_json_is_incomplete():
    t = make_transport([(200, {}, "[]")])
    src = LangfuseApiTraceSource("https://lf.example", "pk", "sk", transport=t)
    try:
        src.read()
    except LangfuseSourceIncomplete:
        return
    raise AssertionError("non-object JSON must fail closed")
