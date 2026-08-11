from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from inference_control_plane.core.config import Settings, get_settings
from inference_control_plane.db.redis import get_redis_optional
from inference_control_plane.db.session import get_db_session
from inference_control_plane.services.auth import AuthContext, validate_api_key

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


async def extract_api_key(api_key: str | None = Depends(api_key_header)) -> str:
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Provide x-api-key header.",
        )
    return api_key


async def get_auth_context(
    api_key: str = Depends(extract_api_key),
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> AuthContext:
    redis_client = get_redis_optional()
    return await validate_api_key(
        api_key=api_key,
        session=session,
        settings=settings,
        redis_client=redis_client,
    )
