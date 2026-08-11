from __future__ import annotations

import json
from collections.abc import Iterator


class FileTraceSource:
    """Fully-implemented deterministic source that reads a Langfuse export file.

    Accepts either the Langfuse export shape ``{"data": [...], "meta": {...}}``
    or a bare list of observation dicts.
    """

    def __init__(self, path: str) -> None:
        self.path = path

    def _load(self) -> list:
        with open(self.path, encoding="utf-8") as fh:
            payload = json.load(fh)
        if isinstance(payload, dict) and "data" in payload:
            data = payload["data"]
        elif isinstance(payload, list):
            data = payload
        else:
            raise ValueError("Unrecognized fixture shape: expected {'data': [...]} or a list")
        if not isinstance(data, list):
            raise ValueError("'data' must be a list of observation objects")
        return data

    def read(self) -> list[dict]:
        return self._load()

    def iter_records(self) -> Iterator[dict]:
        yield from self._load()
