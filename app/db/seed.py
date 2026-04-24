import hashlib
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import Settings
from app.models.api_key import APIKey

logger = logging.getLogger(__name__)


async def seed_default_api_key(
    session_factory: async_sessionmaker[AsyncSession],
    settings: Settings,
) -> None:
    key_hash = hashlib.sha256(settings.default_api_key.encode("utf-8")).hexdigest()

    async with session_factory() as session:
        stmt = select(APIKey).where(APIKey.key_hash == key_hash)
        existing = (await session.execute(stmt)).scalar_one_or_none()
        if existing is not None:
            return

        session.add(
            APIKey(
                key_hash=key_hash,
                name="default-dev-key",
                tenant_id="default-tenant",
                rate_limit_per_minute=settings.default_rate_limit_per_minute,
                is_active=True,
            )
        )
        await session.commit()

    logger.info(
        "Seeded default API key. Configure x-api-key with DEFAULT_API_KEY in production.",
    )
