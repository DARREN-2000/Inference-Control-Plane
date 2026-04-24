from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.security import get_auth_context
from app.db.redis import get_redis_optional, ping_redis
from app.db.session import get_db_session
from app.schemas.generate import GenerateRequest, GenerateResponse, UsageSummaryResponse
from app.services.auth import AuthContext
from app.services.inference import handle_generate_request
from app.services.usage import get_usage_summary

router = APIRouter()


@router.post("/generate", response_model=GenerateResponse)
async def generate(
    payload: GenerateRequest,
    auth_context: AuthContext = Depends(get_auth_context),
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> GenerateResponse:
    redis_client = get_redis_optional()
    return await handle_generate_request(
        payload=payload,
        auth_context=auth_context,
        session=session,
        settings=settings,
        redis_client=redis_client,
    )


@router.get("/usage/summary", response_model=UsageSummaryResponse)
async def usage_summary(
    user_id: str = Query(..., min_length=1, max_length=128),
    auth_context: AuthContext = Depends(get_auth_context),
    session: AsyncSession = Depends(get_db_session),
) -> UsageSummaryResponse:
    return await get_usage_summary(
        session,
        tenant_id=auth_context.tenant_id,
        user_id=user_id,
    )


@router.get("/health/live")
async def health_live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
async def health_ready(session: AsyncSession = Depends(get_db_session)) -> dict[str, str]:
    try:
        await session.execute(select(1))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "not-ready", "database": False, "redis": False},
        ) from exc

    redis_ready = await ping_redis()
    if not redis_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "not-ready", "database": True, "redis": False},
        )

    return {"status": "ready"}


@router.get("/metrics")
async def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
