from redis.asyncio import Redis

from inference_control_plane.core.config import Settings

_redis_client: Redis | None = None


def init_redis(settings: Settings) -> None:
    global _redis_client
    if _redis_client is not None:
        return

    _redis_client = Redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )


def get_redis() -> Redis:
    if _redis_client is None:
        raise RuntimeError("Redis client has not been initialized.")
    return _redis_client


def get_redis_optional() -> Redis | None:
    return _redis_client


async def ping_redis() -> bool:
    client = get_redis_optional()
    if client is None:
        return False
    try:
        return bool(await client.ping())
    except Exception:
        return False


async def close_redis() -> None:
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
    _redis_client = None
