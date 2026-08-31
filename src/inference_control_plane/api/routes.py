from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Response, status
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from inference_control_plane.core.config import Settings, get_settings
from inference_control_plane.core.security import get_auth_context
from inference_control_plane.db.redis import get_redis_optional, ping_redis
from inference_control_plane.db.session import get_db_session
from inference_control_plane.schemas.generate import (
    DashboardActivityResponse,
    DashboardMetricsResponse,
    GenerateRequest,
    GenerateResponse,
    UsageLogsResponse,
    UsageSummaryResponse,
)
from inference_control_plane.services.auth import AuthContext
from inference_control_plane.services.inference import handle_generate_request
from inference_control_plane.services.usage import get_usage_logs, get_usage_summary

router = APIRouter()


@router.post("/generate", response_model=GenerateResponse)
async def generate(
    payload: GenerateRequest,
    background_tasks: BackgroundTasks,
    auth_context: AuthContext = Depends(get_auth_context),
    settings: Settings = Depends(get_settings),
) -> GenerateResponse:
    """Handle generation requests for LLM models.

    This endpoint orchestrates caching, rate limiting, and inference fallback logic.

    Args:
        payload (GenerateRequest): The incoming generation request payload.
        background_tasks (BackgroundTasks): Background task scheduler for logging.
        auth_context (AuthContext): The authenticated user context.
        settings (Settings): Application settings.

    Returns:
        GenerateResponse: The generation result containing response text and metadata.
    """


    redis_client = get_redis_optional()
    return await handle_generate_request(
        payload=payload,
        auth_context=auth_context,
        settings=settings,
        redis_client=redis_client,
        background_tasks=background_tasks,
    )


@router.get("/usage/summary", response_model=UsageSummaryResponse)
async def usage_summary(
    user_id: str = Query(..., min_length=1, max_length=128),
    auth_context: AuthContext = Depends(get_auth_context),
    session: AsyncSession = Depends(get_db_session),
) -> UsageSummaryResponse:
    """Retrieve usage summary for a specific user.

    Requires admin privileges.

    Args:
        user_id (str): The identifier of the user to query.
        auth_context (AuthContext): The authenticated user context.
        session (AsyncSession): The database session.

    Returns:
        UsageSummaryResponse: Summary metrics for the user's usage.
    
    Raises:
        HTTPException: If the user lacks admin privileges.
    """
    if auth_context.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required to view usage summary.",
        )
    return await get_usage_summary(
        session,
        tenant_id=auth_context.tenant_id,
        user_id=user_id,
    )


@router.get("/usage/logs", response_model=UsageLogsResponse)
async def usage_logs(
    user_id: str = Query(..., min_length=1, max_length=128),
    limit: int = Query(10, ge=1, le=100),
    auth_context: AuthContext = Depends(get_auth_context),
    session: AsyncSession = Depends(get_db_session),
) -> UsageLogsResponse:
    """Retrieve detailed usage logs for a specific user.

    Requires admin privileges.

    Args:
        user_id (str): The identifier of the user to query.
        limit (int): Maximum number of records to return.
        auth_context (AuthContext): The authenticated user context.
        session (AsyncSession): The database session.

    Returns:
        UsageLogsResponse: Detailed historical usage logs for the user.
    
    Raises:
        HTTPException: If the user lacks admin privileges.
    """
    if auth_context.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required to view usage logs.",
        )
    return await get_usage_logs(
        session,
        tenant_id=auth_context.tenant_id,
        user_id=user_id,
        limit=limit,
    )


@router.get("/dashboard/metrics", response_model=DashboardMetricsResponse)
async def dashboard_metrics(
    auth_context: AuthContext = Depends(get_auth_context),
    session: AsyncSession = Depends(get_db_session),
) -> DashboardMetricsResponse:
    """Retrieve overall system metrics for the dashboard.

    Requires admin privileges.

    Args:
        auth_context (AuthContext): The authenticated user context.
        session (AsyncSession): The database session.

    Returns:
        DashboardMetricsResponse: High-level system metrics over the past 24 hours.
    
    Raises:
        HTTPException: If the user lacks admin privileges.
    """
    from inference_control_plane.services.dashboard import get_dashboard_metrics
    
    if auth_context.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required to view dashboard metrics.",
        )
    return await get_dashboard_metrics(session)


@router.get("/dashboard/activity", response_model=DashboardActivityResponse)
async def dashboard_activity(
    auth_context: AuthContext = Depends(get_auth_context),
    session: AsyncSession = Depends(get_db_session),
) -> DashboardActivityResponse:
    """Retrieve recent system activity for the dashboard.

    Requires admin privileges.

    Args:
        auth_context (AuthContext): The authenticated user context.
        session (AsyncSession): The database session.

    Returns:
        DashboardActivityResponse: Recent system activity logs, typically errors.
    
    Raises:
        HTTPException: If the user lacks admin privileges.
    """
    from inference_control_plane.services.dashboard import get_dashboard_activity
    
    if auth_context.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required to view dashboard activity.",
        )
    return await get_dashboard_activity(session)


@router.get("/health/live")
async def health_live() -> dict[str, str]:
    """Check if the service is live.

    Returns:
        dict[str, str]: Liveness status indicator.
    """
    return {"status": "ok"}


@router.get("/health/ready")
async def health_ready(session: AsyncSession = Depends(get_db_session)) -> dict[str, str]:
    """Check if the service and its dependencies are ready.

    Validates connectivity to the database and Redis cache.

    Args:
        session (AsyncSession): The database session.

    Returns:
        dict[str, str]: Readiness status indicator.
    
    Raises:
        HTTPException: If any dependent service is down.
    """
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
    """Expose Prometheus metrics for observability.

    Returns:
        Response: The serialized metrics payload.
    """
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
