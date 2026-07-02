import hashlib
import json
from dataclasses import dataclass

from fastapi import HTTPException, status
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from inference_control_plane.core.config import Settings
from inference_control_plane.models.api_key import APIKey


@dataclass(slots=True)
class AuthContext:
    tenant_id: str
    api_key_hash: str
    rate_limit_per_minute: int
    role: str


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def _auth_cache_key(api_key_hash: str) -> str:
    return f"auth:key:{api_key_hash}"


async def _load_cached_auth_context(
    redis_client: Redis,
    api_key_hash: str,
) -> AuthContext | None:
    cached = await redis_client.get(_auth_cache_key(api_key_hash))
    if not cached:
        return None

    payload = json.loads(cached)
    if not payload.get("is_active", False):
        return None

    return AuthContext(
        tenant_id=payload["tenant_id"],
        api_key_hash=api_key_hash,
        rate_limit_per_minute=int(payload["rate_limit_per_minute"]),
        role=payload.get("role", "tenant"),
    )


async def _store_cached_auth_context(
    redis_client: Redis,
    api_key: APIKey,
    settings: Settings,
) -> None:
    payload = {
        "tenant_id": api_key.tenant_id,
        "rate_limit_per_minute": api_key.rate_limit_per_minute,
        "is_active": api_key.is_active,
        "role": getattr(api_key, "role", "tenant"),
    }
    await redis_client.set(
        _auth_cache_key(api_key.key_hash),
        json.dumps(payload),
        ex=settings.auth_cache_ttl_seconds,
    )


async def validate_api_key(
    api_key: str,
    session: AsyncSession,
    settings: Settings,
    redis_client: Redis | None = None,
) -> AuthContext:
    api_key_hash = hash_api_key(api_key)

    if redis_client is not None:
        try:
            cached_context = await _load_cached_auth_context(redis_client, api_key_hash)
            if cached_context is not None:
                return cached_context
        except Exception:
            pass

    stmt = select(APIKey).where(APIKey.key_hash == api_key_hash)
    key_record = (await session.execute(stmt)).scalar_one_or_none()

    if key_record is None or not key_record.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        )

    if redis_client is not None:
        try:
            await _store_cached_auth_context(redis_client, key_record, settings)
        except Exception:
            pass

    return AuthContext(
        tenant_id=key_record.tenant_id,
        api_key_hash=key_record.key_hash,
        rate_limit_per_minute=key_record.rate_limit_per_minute,
        role=getattr(key_record, "role", "tenant"),
    )
