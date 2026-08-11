"""Dashboard service for Inference Control Plane."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from inference_control_plane.models.request_log import RequestLog
from inference_control_plane.schemas.generate import DashboardActivityResponse, DashboardMetricsResponse


async def get_dashboard_metrics(session: AsyncSession) -> DashboardMetricsResponse:
    """Retrieve dashboard metrics for the last 24 hours.

    Calculates aggregate metrics such as request count, cache hit ratio, average
    latency, and estimated cost per 1K requests.

    Args:
        session (AsyncSession): The asynchronous database session.

    Returns:
        DashboardMetricsResponse: The calculated metrics for the dashboard.
    """
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


async def get_dashboard_activity(session: AsyncSession) -> DashboardActivityResponse:
    """Retrieve recent dashboard activity, focusing on errors.

    Args:
        session (AsyncSession): The asynchronous database session.

    Returns:
        DashboardActivityResponse: A list of recent activity messages.
    """
    stmt = select(RequestLog).where(RequestLog.status != "success").order_by(RequestLog.created_at.desc()).limit(5)
    recent_errors = (await session.execute(stmt)).scalars().all()
    
    activity_list = [f"Error on {err.model_used}: {err.error_message}" for err in recent_errors]
    if not activity_list:
        activity_list = ["System operating normally."]
        
    return DashboardActivityResponse(activity=activity_list)
