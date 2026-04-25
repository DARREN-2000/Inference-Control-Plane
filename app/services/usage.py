from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.request_log import RequestLog
from app.schemas.generate import UsageLogEntry, UsageLogsResponse, UsageSummaryResponse


async def get_usage_summary(
    session: AsyncSession,
    *,
    tenant_id: str,
    user_id: str,
) -> UsageSummaryResponse:
    stmt = (
        select(
            func.count(RequestLog.id),
            func.coalesce(func.sum(RequestLog.tokens), 0),
            func.coalesce(func.sum(RequestLog.cost), 0),
        )
        .where(RequestLog.tenant_id == tenant_id)
        .where(RequestLog.user_id == user_id)
    )

    result = await session.execute(stmt)
    requests, total_tokens, total_cost = result.one()

    return UsageSummaryResponse(
        user_id=user_id,
        requests=int(requests or 0),
        total_tokens=int(total_tokens or 0),
        total_cost=float(total_cost or 0.0),
    )


async def get_usage_logs(
    session: AsyncSession,
    *,
    tenant_id: str,
    user_id: str,
    limit: int,
) -> UsageLogsResponse:
    stmt = (
        select(RequestLog)
        .where(RequestLog.tenant_id == tenant_id)
        .where(RequestLog.user_id == user_id)
        .order_by(RequestLog.created_at.desc())
        .limit(limit)
    )
    rows = (await session.execute(stmt)).scalars().all()

    entries = [
        UsageLogEntry(
            request_id=row.id,
            model_used=row.model_used,
            latency_ms=row.latency_ms,
            tokens=row.tokens,
            cost=float(row.cost),
            cache_hit=row.cache_hit,
            status=row.status,
            created_at=row.created_at,
            error_message=row.error_message,
        )
        for row in rows
    ]

    return UsageLogsResponse(user_id=user_id, limit=limit, entries=entries)
