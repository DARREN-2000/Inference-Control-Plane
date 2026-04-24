from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.request_log import RequestLog
from app.schemas.generate import UsageSummaryResponse


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
