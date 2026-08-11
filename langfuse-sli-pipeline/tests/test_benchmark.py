import tracemalloc
import time

from gateway_sli.pipeline import run

try:
    from tests.conftest import _make_raw_impl
except ImportError:
    _make_raw_impl = None


class _GenSource:
    def __init__(self, make_raw, count):
        self.make_raw = make_raw
        self.count = count

    def iter_records(self):
        for i in range(self.count):
            yield self.make_raw(id=f"bench-obs-{i}", traceId=f"bench-trace-{i}")


def test_streaming_memory_bound():
    if _make_raw_impl is None:
        return
    make_raw = _make_raw_impl()

    # Measure memory for 100 records
    source_100 = _GenSource(make_raw, 100)
    tracemalloc.start()
    run(source_100)
    _, peak_100 = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Measure memory for 10000 records
    source_10k = _GenSource(make_raw, 10000)
    tracemalloc.start()
    t0 = time.monotonic()
    res = run(source_10k)
    t1 = time.monotonic()
    _, peak_10k = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print("\n--- Benchmark Results ---")
    print(f"100 records: peak memory = {peak_100 / 1024:.2f} KB")
    print(f"10,000 records: peak memory = {peak_10k / 1024 / 1024:.2f} MB, time = {t1 - t0:.2f}s")

    # Assertions
    assert res.stats.records_read == 10000

    # Memory bound: should not exceed 50MB (it should be very small since it's streaming)
    assert peak_10k < 50 * 1024 * 1024
