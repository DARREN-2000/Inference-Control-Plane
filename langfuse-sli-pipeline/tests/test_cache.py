"""Cache economics SLIs: cached-token volume and cache-hit count per series.

These reuse the existing bounded cost dimensions (no new cardinality) and are
emitted ONLY when a series actually served cached tokens, so cache-free routes
add no noise. A cache-hit ratio is derivable as cache.hit_count /
cost.request_count; token savings as cache.read_tokens / (tokens.input +
cache.read_tokens).
"""

from gateway_sli.config import Config
from gateway_sli.models import parse_observation
from gateway_sli.sli import aggregate

_CACHED_USAGE = {"input": 402, "cache_read_input_tokens": 3812, "output": 284, "total": 4498}


def _agg(raws):
    obs = [parse_observation(r) for r in raws]
    return aggregate(obs, 0, Config())


def _named(points, name):
    return [p for p in points if p.name == name]


def test_cache_tokens_and_hits_summed(make_raw):
    first = make_raw(id="cache-1", usageDetails=_CACHED_USAGE)
    second = make_raw(id="cache-2", usageDetails=_CACHED_USAGE)
    points, _ = _agg([first, second])
    tokens = _named(points, "gateway.cache.read_tokens")
    hits = _named(points, "gateway.cache.hit_count")
    assert len(tokens) == 1 and tokens[0].value == 3812 * 2
    assert len(hits) == 1 and hits[0].value == 2


def test_no_cache_metrics_without_cache_reads(make_raw):
    points, _ = _agg([make_raw()])
    assert not _named(points, "gateway.cache.read_tokens")
    assert not _named(points, "gateway.cache.hit_count")


def test_cache_hit_count_only_counts_cached_records(make_raw):
    # Cached and plain share identical primary/cost dims -> one series.
    points, _ = _agg([make_raw(id="cache-1", usageDetails=_CACHED_USAGE), make_raw(id="plain-1")])
    hits = _named(points, "gateway.cache.hit_count")
    tokens = _named(points, "gateway.cache.read_tokens")
    assert len(hits) == 1 and hits[0].value == 1
    assert len(tokens) == 1 and tokens[0].value == 3812


def test_cache_dims_are_governed(make_raw):
    from gateway_sli.emit.base import assert_allowed

    points, _ = _agg([make_raw(usageDetails=_CACHED_USAGE)])
    # Must not raise: cache metrics only carry allowlisted cost dimensions.
    assert_allowed(points)
