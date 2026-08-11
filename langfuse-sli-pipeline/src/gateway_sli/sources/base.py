from __future__ import annotations

from collections.abc import Iterator
from typing import Protocol


class TraceSource(Protocol):
    """Contract for anything that yields raw Langfuse observation dicts.

    Two read shapes are supported so the pipeline can process one bounded
    aggregation window without materializing it all at once:

      * ``read()`` returns the whole window as a list (convenient for tests and
        small fixtures); and
      * ``iter_records()`` yields records lazily (the pipeline prefers this so a
        very large window streams through aggregation with bounded memory).

    Implementations must not mutate the underlying store.
    """

    def read(self) -> list[dict]: ...

    def iter_records(self) -> Iterator[dict]: ...
