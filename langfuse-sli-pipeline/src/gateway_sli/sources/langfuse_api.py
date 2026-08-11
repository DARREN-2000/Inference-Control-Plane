from __future__ import annotations

import base64
import json
import time
from collections.abc import Iterator
from urllib.parse import urlencode


class LangfuseApiError(RuntimeError):
    """Raised when the Langfuse API returns a non-2xx status (after retries)."""

    def __init__(self, status: int, body: str) -> None:
        super().__init__(f"Langfuse API error: HTTP {status}")
        self.status = status
        self.body = body


class LangfuseSourceIncomplete(RuntimeError):
    """The source could not prove that the complete requested window was read."""


class LangfuseApiTraceSource:
    """Read GENERATION observations from the Langfuse public API for one bounded,
    closed window.

    The HTTP transport is INJECTED (``transport``) so pagination, windowing, auth,
    and 429 backoff are unit-tested deterministically without a live endpoint; the
    default transport uses only the standard library (urllib). ``iter_records``
    yields page by page so a large window streams through the pipeline with
    bounded memory; ``read`` returns the full list for callers that want it.

    Contract:
      * Endpoint: ``GET {base_url}/api/public/observations?type=GENERATION``.
      * Auth: HTTP Basic (public_key, secret_key), sourced from env / secret
        manager - never from code.
      * Windowing: ``fromStartTime`` / ``toStartTime`` bound a CLOSED window
        delayed by a grace period so late/updated traces are captured.
      * Pagination: follows ``meta.cursor`` when the API returns one, else
        increments ``page`` until ``meta.totalPages`` is reached. ``max_pages`` is
        a safety stop.
      * Rate limits: HTTP 429 is retried with exponential backoff honoring
        ``Retry-After``, up to ``max_retries``.

    Why not the Langfuse Metrics API? We deliberately pull raw observations and
    aggregate inside our boundary so that (1) privacy projection and normalization
    happen here, (2) bounded-cardinality governance is enforced before export,
    (3) per-observation completion lengths remain available for the anomaly
    signal, and (4) the output stays backend-portable with no third copy of raw
    data. The Metrics API is right for ad-hoc analytics, not this governed plane.
    """

    OBSERVATIONS_PATH = "/api/public/observations"

    def __init__(
        self,
        base_url: str,
        public_key: str,
        secret_key: str,
        *,
        from_timestamp: str | None = None,
        to_timestamp: str | None = None,
        page_limit: int = 50,
        max_pages: int = 10_000,
        max_retries: int = 5,
        backoff_base: float = 0.5,
        transport=None,
        sleep=time.sleep,
        timeout: float = 30.0,
        clock=time.monotonic,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._public_key = public_key
        self._secret_key = secret_key
        self.from_timestamp = from_timestamp
        self.to_timestamp = to_timestamp
        self.page_limit = page_limit
        self.max_pages = max_pages
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self._transport = transport or self._default_transport
        self._sleep = sleep
        self._timeout = timeout
        self._clock = clock
        self.stats = {"requests": 0, "retries": 0, "pages": 0, "latency_seconds": 0.0}

    def _auth_header(self) -> str:
        token = base64.b64encode(f"{self._public_key}:{self._secret_key}".encode()).decode("ascii")
        return f"Basic {token}"

    def read(self) -> list[dict]:
        return list(self.iter_records())

    def iter_records(self) -> Iterator[dict]:
        """Yield observations using one pagination mode for the whole read.

        The first response selects cursor mode or numbered-page mode. We never
        switch modes mid-read, which keeps the state machine small and prevents
        the final cursor page from being fetched again as a numbered page.
        """
        seen_page_signatures: set[tuple[str, ...]] = set()
        self.stats["pages"] = 0
        data, meta = self._fetch_page(seen_page_signatures, page=1)
        yield from data

        cursor = self._cursor(meta)
        if cursor is not None:
            yield from self._iter_cursor_pages(cursor, seen_page_signatures)
            return
        yield from self._iter_numbered_pages(data, meta, seen_page_signatures)

    def _base_params(self) -> dict[str, object]:
        params: dict[str, object] = {
            "type": "GENERATION",
            "limit": self.page_limit,
        }
        if self.from_timestamp:
            params["fromStartTime"] = self.from_timestamp
        if self.to_timestamp:
            params["toStartTime"] = self.to_timestamp
        return params

    def _fetch_page(
        self,
        seen_signatures: set[tuple[str, ...]],
        *,
        page: int | None = None,
        cursor: str | None = None,
    ) -> tuple[list[dict], dict]:
        if self.stats["pages"] >= self.max_pages:
            raise LangfuseSourceIncomplete(
                f"pagination exceeded safety limit of {self.max_pages} pages"
            )
        params = self._base_params()
        if cursor is not None:
            params["cursor"] = cursor
        elif page is not None:
            params["page"] = page
        body = self._get(self.OBSERVATIONS_PATH, params)
        data = body.get("data") or []
        meta = body.get("meta") or {}
        if not isinstance(data, list):
            raise LangfuseSourceIncomplete("response data is not a list")
        if not isinstance(meta, dict):
            raise LangfuseSourceIncomplete("response meta is not an object")
        if any(not isinstance(item, dict) for item in data):
            raise LangfuseSourceIncomplete("response data contains a non-object")
        signature = tuple(str(item.get("id") or "") for item in data)
        if data and signature in seen_signatures:
            raise LangfuseSourceIncomplete("pagination page repeated")
        if data:
            seen_signatures.add(signature)
        self.stats["pages"] += 1
        return data, meta

    @staticmethod
    def _cursor(meta: dict) -> str | None:
        value = meta.get("cursor")
        return str(value) if value not in (None, "") else None

    def _iter_cursor_pages(
        self, cursor: str, seen_signatures: set[tuple[str, ...]]
    ) -> Iterator[dict]:
        seen_cursors = {cursor}
        while True:
            data, meta = self._fetch_page(seen_signatures, cursor=cursor)
            next_cursor = self._cursor(meta)
            if not data and next_cursor is not None:
                raise LangfuseSourceIncomplete("empty page supplied a continuation cursor")
            yield from data
            if next_cursor is None:
                return
            if next_cursor in seen_cursors:
                raise LangfuseSourceIncomplete("pagination cursor repeated")
            seen_cursors.add(next_cursor)
            cursor = next_cursor

    def _iter_numbered_pages(
        self,
        previous_data: list[dict],
        first_meta: dict,
        seen_signatures: set[tuple[str, ...]],
    ) -> Iterator[dict]:
        raw_total = first_meta.get("totalPages")
        if raw_total is not None:
            try:
                total_pages = int(raw_total)
            except (TypeError, ValueError) as exc:
                raise LangfuseSourceIncomplete("invalid totalPages") from exc
            if total_pages < 0:
                raise LangfuseSourceIncomplete("invalid totalPages")
            if total_pages == 0:
                return
        else:
            total_pages = None

        page = 1
        while (
            page < total_pages if total_pages is not None else len(previous_data) >= self.page_limit
        ):
            page += 1
            data, meta = self._fetch_page(seen_signatures, page=page)
            if self._cursor(meta) is not None:
                raise LangfuseSourceIncomplete("pagination mode changed from page to cursor")
            if not data:
                # Eventual consistency in Langfuse can cause an empty page before totalPages.
                return
            yield from data
            previous_data = data

    def _get(self, path: str, params: dict) -> dict:
        url = f"{self.base_url}{path}?{urlencode(params)}"
        headers = {"Authorization": self._auth_header(), "Accept": "application/json"}
        for attempt in range(self.max_retries + 1):
            started = self._clock()
            status, resp_headers, text = self._transport(url, headers)
            self.stats["requests"] += 1
            self.stats["latency_seconds"] += max(0.0, self._clock() - started)
            if status in {429, 500, 502, 503, 504, 599} and attempt < self.max_retries:
                self.stats["retries"] += 1
                self._sleep(self._retry_after(resp_headers, attempt))
                continue
            if not (200 <= status < 300):
                raise LangfuseApiError(status, text)
            try:
                parsed = json.loads(text) if text else {}
            except (json.JSONDecodeError, TypeError) as exc:
                raise LangfuseSourceIncomplete("response is not valid JSON") from exc
            if not isinstance(parsed, dict):
                raise LangfuseSourceIncomplete("response JSON is not an object")
            return parsed
        raise LangfuseApiError(429, "exhausted retries after repeated 429s")

    def _retry_after(self, headers: dict | None, attempt: int) -> float:
        ra = (headers or {}).get("Retry-After")
        if ra:
            try:
                return min(60.0, max(0.0, float(ra)))
            except (ValueError, TypeError):
                pass
        return self.backoff_base * (2**attempt)

    def _default_transport(self, url: str, headers: dict):
        import urllib.error
        import urllib.request

        req = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                return (
                    resp.status,
                    dict(resp.headers),
                    resp.read().decode("utf-8", "replace"),
                )
        except urllib.error.HTTPError as exc:
            return exc.code, dict(exc.headers or {}), exc.read().decode("utf-8", "replace")
        except (urllib.error.URLError, TimeoutError, OSError):
            return 599, {}, "transport failure"
