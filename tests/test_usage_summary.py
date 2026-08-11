import asyncio
from decimal import Decimal

from sqlalchemy.ext.asyncio import create_async_engine

from inference_control_plane.db.base import Base
from inference_control_plane.models.request_log import RequestLog
from inference_control_plane.services.usage import get_usage_summary


async def _run_usage_summary_test() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with engine.connect() as conn:
        async with conn.begin():
            await conn.execute(
                RequestLog.__table__.insert(),
                [
                    {
                        "tenant_id": "t-1",
                        "user_id": "u-1",
                        "api_key_hash": "k1",
                        "prompt": "p1",
                        "response": "r1",
                        "model_used": "cheap-model",
                        "latency_ms": 12.3,
                        "tokens": 100,
                        "cost": Decimal("0.0008"),
                        "cache_hit": False,
                        "status": "success",
                        "error_message": None,
                    },
                    {
                        "tenant_id": "t-1",
                        "user_id": "u-1",
                        "api_key_hash": "k1",
                        "prompt": "p2",
                        "response": "r2",
                        "model_used": "premium-model",
                        "latency_ms": 44.2,
                        "tokens": 300,
                        "cost": Decimal("0.0030"),
                        "cache_hit": True,
                        "status": "success",
                        "error_message": None,
                    },
                ],
            )

        result = await get_usage_summary(conn, tenant_id="t-1", user_id="u-1")

    await engine.dispose()

    assert result.user_id == "u-1"
    assert result.requests == 2
    assert result.total_tokens == 400
    assert result.total_cost == 0.0038


def test_usage_summary_aggregation() -> None:
    asyncio.run(_run_usage_summary_test())
