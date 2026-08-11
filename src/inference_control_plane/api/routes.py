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
    from datetime import UTC, datetime, timedelta

    from sqlalchemy import func

    from inference_control_plane.models.request_log import RequestLog

    if auth_context.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required to view dashboard metrics.",
        )
    now = datetime.now(UTC)
    yesterday = now - timedelta(days=1)
    stmt_reqs = select(func.count(RequestLog.id)).where(RequestLog.created_at >= yesterday)
    req_count = (await session.execute(stmt_reqs)).scalar() or 0
    stmt_cost = select(func.sum(RequestLog.cost)).where(RequestLog.created_at >= yesterday)
    total_cost = (await session.execute(stmt_cost)).scalar() or 0.0
    cost_per_1k = (float(total_cost) / req_count * 1000) if req_count > 0 else 0.0
    stmt_hits = select(func.count(RequestLog.id)).where(RequestLog.created_at >= yesterday, RequestLog.cache_hit)
    hit_count = (await session.execute(stmt_hits)).scalar() or 0
    cache_hit_ratio = (hit_count / req_count * 100) if req_count > 0 else 0.0
    stmt_lat = select(func.avg(RequestLog.latency_ms)).where(RequestLog.created_at >= yesterday)
    avg_lat = (await session.execute(stmt_lat)).scalar() or 0.0
    return DashboardMetricsResponse(
        metrics=[
            {"label": "Avg Latency", "value": f"{avg_lat:.1f}ms", "delta": "0%"},
            {"label": "Cache Hit Ratio", "value": f"{cache_hit_ratio:.1f}%", "delta": "0%"},
            {"label": "Requests (24h)", "value": str(req_count), "delta": "0%"},
            {"label": "Cost / 1K req", "value": f"${cost_per_1k:.4f}", "delta": "0%"},
        ]
    )


@router.get("/dashboard/activity", response_model=DashboardActivityResponse)
async def dashboard_activity(
    auth_context: AuthContext = Depends(get_auth_context),
    session: AsyncSession = Depends(get_db_session),
) -> DashboardActivityResponse:
    from inference_control_plane.models.request_log import RequestLog

    if auth_context.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required to view dashboard activity.",
        )
    stmt = select(RequestLog).where(RequestLog.status != "success").order_by(RequestLog.created_at.desc()).limit(5)
    recent_errors = (await session.execute(stmt)).scalars().all()
    activity_list = [f"Error on {err.model_used}: {err.error_message}" for err in recent_errors]
    if not activity_list:
        activity_list = ["System operating normally."]
    return DashboardActivityResponse(activity=activity_list)


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
