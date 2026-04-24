import hashlib
import json
from dataclasses import dataclass

from redis.asyncio import Redis


@dataclass(slots=True)
class CachedResponse:
    response: str
    model_used: str
    tokens: int
    cost: float


def _cache_key(prompt: str, model: str) -> str:
    digest = hashlib.sha256(f"{model}:{prompt}".encode("utf-8")).hexdigest()
    return f"cache:inference:{digest}"


async def get_cached_response(
    redis_client: Redis | None,
    *,
    prompt: str,
    model: str,
) -> CachedResponse | None:
    if redis_client is None:
        return None

    try:
        raw = await redis_client.get(_cache_key(prompt=prompt, model=model))
        if not raw:
            return None
        payload = json.loads(raw)
        return CachedResponse(
            response=str(payload["response"]),
            model_used=str(payload["model_used"]),
            tokens=int(payload["tokens"]),
            cost=float(payload["cost"]),
        )
    except Exception:
        return None


async def set_cached_response(
    redis_client: Redis | None,
    *,
    prompt: str,
    model: str,
    response: str,
    model_used: str,
    tokens: int,
    cost: float,
    ttl_seconds: int,
) -> None:
    if redis_client is None:
        return

    payload = {
        "response": response,
        "model_used": model_used,
        "tokens": tokens,
        "cost": cost,
    }

    try:
        await redis_client.set(
            _cache_key(prompt=prompt, model=model),
            json.dumps(payload),
            ex=ttl_seconds,
        )
    except Exception:
        return
