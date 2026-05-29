from threading import Lock

from prometheus_client import Counter, Gauge, Histogram

REQUEST_COUNT = Counter(
    "request_count",
    "Total number of inference requests",
    ["model", "status", "cache_hit"],
)
LATENCY_HISTOGRAM = Histogram(
    "latency_histogram_ms",
    "End-to-end request latency in milliseconds",
    ["model", "status"],
    buckets=(5, 10, 25, 50, 100, 200, 500, 1000, 2500, 5000, 10000),
)
CACHE_HITS = Counter("cache_hits_total", "Total cache hits")
CACHE_MISSES = Counter("cache_misses_total", "Total cache misses")
CACHE_HIT_RATIO = Gauge("cache_hit_ratio", "Cache hit ratio")
MODEL_USAGE_COUNT = Counter("model_usage_count", "Per-model usage count", ["model"])
RATE_LIMIT_REJECTIONS = Counter(
    "rate_limit_rejections_total",
    "Total rate-limit rejections",
    ["scope"],
)
MODEL_COST_USD_TOTAL = Counter(
    "model_cost_usd_total",
    "Total model spend in USD",
    ["model"],
)

_cache_lock = Lock()
_cache_hits = 0
_cache_misses = 0


def record_cache_result(hit: bool) -> None:
    global _cache_hits, _cache_misses

    with _cache_lock:
        if hit:
            _cache_hits += 1
            CACHE_HITS.inc()
        else:
            _cache_misses += 1
            CACHE_MISSES.inc()

        total = _cache_hits + _cache_misses
        ratio = (_cache_hits / total) if total > 0 else 0.0
        CACHE_HIT_RATIO.set(ratio)


def record_request(model: str, status: str, latency_ms: float, cache_hit: bool) -> None:
    REQUEST_COUNT.labels(
        model=model,
        status=status,
        cache_hit=str(cache_hit).lower(),
    ).inc()
    LATENCY_HISTOGRAM.labels(model=model, status=status).observe(max(latency_ms, 0.0))


def record_model_usage(model: str) -> None:
    MODEL_USAGE_COUNT.labels(model=model).inc()


def record_rate_limit_rejection(scope: str) -> None:
    RATE_LIMIT_REJECTIONS.labels(scope=scope).inc()


def record_cost(model: str, cost_usd: float) -> None:
    MODEL_COST_USD_TOTAL.labels(model=model).inc(max(cost_usd, 0.0))
