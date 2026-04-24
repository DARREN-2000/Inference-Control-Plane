import time
from dataclasses import dataclass

from redis.asyncio import Redis


@dataclass(slots=True)
class RateLimitResult:
    allowed: bool
    remaining: int
    retry_after_seconds: int


def _bucket_key(scope: str, identifier: str, window_seconds: int) -> str:
    bucket = int(time.time()) // window_seconds
    return f"rate:{scope}:{identifier}:{bucket}"


async def check_rate_limit(
    redis_client: Redis | None,
    *,
    scope: str,
    identifier: str,
    limit: int,
    window_seconds: int,
) -> RateLimitResult:
    if redis_client is None:
        return RateLimitResult(allowed=True, remaining=limit, retry_after_seconds=0)

    key = _bucket_key(scope=scope, identifier=identifier, window_seconds=window_seconds)

    try:
        pipeline = redis_client.pipeline(transaction=True)
        pipeline.incr(key)
        pipeline.ttl(key)
        current_count, ttl = await pipeline.execute()

        count = int(current_count)
        ttl_seconds = int(ttl)

        if count == 1:
            await redis_client.expire(key, window_seconds)
            ttl_seconds = window_seconds

        allowed = count <= limit
        remaining = max(limit - count, 0)
        retry_after_seconds = ttl_seconds if not allowed else 0
        return RateLimitResult(
            allowed=allowed,
            remaining=remaining,
            retry_after_seconds=max(retry_after_seconds, 1) if not allowed else 0,
        )
    except Exception:
        return RateLimitResult(allowed=True, remaining=limit, retry_after_seconds=0)
