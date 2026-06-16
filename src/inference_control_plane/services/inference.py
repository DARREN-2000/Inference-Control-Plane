import logging
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from time import perf_counter

from fastapi import BackgroundTasks, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from inference_control_plane.core.config import Settings
from inference_control_plane.db.session import get_session_factory
from inference_control_plane.models.request_log import RequestLog
from inference_control_plane.observability.metrics import (
    record_cache_result,
    record_cost,
    record_model_usage,
    record_rate_limit_rejection,
    record_request,
)
from inference_control_plane.schemas.generate import GenerateRequest, GenerateResponse
from inference_control_plane.services.auth import AuthContext
from inference_control_plane.services.cache import get_cached_response, set_cached_response
from inference_control_plane.services.llm_client import LLMClientError, generate_completion
from inference_control_plane.services.rate_limiter import check_rate_limit
from inference_control_plane.services.router import choose_model, estimate_tokens

logger = logging.getLogger(__name__)


def _estimate_cost(model: str, tokens: int, settings: Settings) -> float:
    token_units = max(tokens, 0) / 1000.0
    rate = (
        settings.cheap_model_cost_per_1k_tokens
        if model == settings.cheap_model_name
        else settings.premium_model_cost_per_1k_tokens
    )
    return token_units * rate


def _fallback_model(model: str, settings: Settings) -> str | None:
    if model == settings.cheap_model_name:
        return settings.premium_model_name
    if model == settings.premium_model_name:
        return settings.cheap_model_name
    return None


async def _persist_request_log(
    session_factory: async_sessionmaker[AsyncSession],
    *,
    tenant_id: str,
    user_id: str,
    api_key_hash: str,
    prompt: str,
    response: str,
    model_used: str,
    latency_ms: float,
    tokens: int,
    cost: float,
    cache_hit: bool,
    status_value: str,
    error_message: str | None,
) -> None:
    async with session_factory() as session:
        try:
            session.add(
                RequestLog(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    api_key_hash=api_key_hash,
                    prompt=prompt,
                    response=response,
                    model_used=model_used,
                    latency_ms=max(latency_ms, 0.0),
                    tokens=max(tokens, 0),
                    cost=Decimal(str(max(cost, 0.0))),
                    cache_hit=cache_hit,
                    status=status_value,
                    error_message=error_message,
                )
            )
            await session.commit()
        except Exception:
            await session.rollback()
            logger.exception("Failed to persist request log.")


def _queue_request_log(
    background_tasks: BackgroundTasks,
    *,
    tenant_id: str,
    user_id: str,
    api_key_hash: str,
    prompt: str,
    response: str,
    model_used: str,
    latency_ms: float,
    tokens: int,
    cost: float,
    cache_hit: bool,
    status_value: str,
    error_message: str | None,
) -> None:
    session_factory = get_session_factory()
    background_tasks.add_task(
        _persist_request_log,
        session_factory,
        tenant_id=tenant_id,
        user_id=user_id,
        api_key_hash=api_key_hash,
        prompt=prompt,
        response=response,
        model_used=model_used,
        latency_ms=latency_ms,
        tokens=tokens,
        cost=cost,
        cache_hit=cache_hit,
        status_value=status_value,
        error_message=error_message,
    )


async def _enforce_rate_limits(
    *,
    auth_context: AuthContext,
    user_id: str,
    redis_client: Redis | None,
    settings: Settings,
) -> None:
    key_result = await check_rate_limit(
        redis_client,
        scope="api_key",
        identifier=auth_context.api_key_hash,
        limit=auth_context.rate_limit_per_minute,
        window_seconds=settings.rate_limit_window_seconds,
    )
    if not key_result.allowed:
        record_rate_limit_rejection(scope="api_key")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="API key rate limit exceeded.",
            headers={"Retry-After": str(key_result.retry_after_seconds)},
        )

    user_key = f"{auth_context.tenant_id}:{user_id}"
    user_result = await check_rate_limit(
        redis_client,
        scope="user",
        identifier=user_key,
        limit=settings.user_rate_limit_per_minute,
        window_seconds=settings.rate_limit_window_seconds,
    )
    if not user_result.allowed:
        record_rate_limit_rejection(scope="user")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="User rate limit exceeded.",
            headers={"Retry-After": str(user_result.retry_after_seconds)},
        )


async def _generate_with_fallback(
    *,
    model: str,
    prompt: str,
    settings: Settings,
) -> tuple[str, str]:
    try:
        generated = await generate_completion(settings, prompt=prompt, model=model)
        return model, generated
    except LLMClientError:
        fallback = _fallback_model(model, settings)
        if fallback is None:
            raise
        generated = await generate_completion(settings, prompt=prompt, model=fallback)
        return fallback, generated


async def handle_generate_request(
    *,
    payload: GenerateRequest,
    auth_context: AuthContext,
    settings: Settings,
    redis_client: Redis | None,
    background_tasks: BackgroundTasks,
) -> GenerateResponse:
    started = perf_counter()
    request_id = str(uuid.uuid4())
    route = choose_model(payload, settings)
    routed_model = route.model

    try:
        await _enforce_rate_limits(
            auth_context=auth_context,
            user_id=payload.user_id,
            redis_client=redis_client,
            settings=settings,
        )

        cached = await get_cached_response(
            redis_client,
            prompt=payload.prompt,
            model=routed_model,
        )
        if cached is not None:
            latency_ms = (perf_counter() - started) * 1000.0
            timestamp = datetime.now(UTC)

            record_cache_result(hit=True)
            record_request(
                model=cached.model_used,
                status="success",
                latency_ms=latency_ms,
                cache_hit=True,
            )

            _queue_request_log(
                background_tasks,
                tenant_id=auth_context.tenant_id,
                user_id=payload.user_id,
                api_key_hash=auth_context.api_key_hash,
                prompt=payload.prompt,
                response=cached.response,
                model_used=cached.model_used,
                latency_ms=latency_ms,
                tokens=cached.tokens,
                cost=cached.cost,
                cache_hit=True,
                status_value="success",
                error_message=None,
            )

            return GenerateResponse(
                request_id=request_id,
                model_used=cached.model_used,
                response=cached.response,
                cached=True,
                latency_ms=latency_ms,
                tokens=cached.tokens,
                cost=cached.cost,
                timestamp=timestamp,
            )

        record_cache_result(hit=False)

        model_used, generated_text = await _generate_with_fallback(
            model=routed_model,
            prompt=payload.prompt,
            settings=settings,
        )
        total_tokens = estimate_tokens(f"{payload.prompt} {generated_text}")
        total_cost = _estimate_cost(model_used, total_tokens, settings)
        latency_ms = (perf_counter() - started) * 1000.0
        timestamp = datetime.now(UTC)

        await set_cached_response(
            redis_client,
            prompt=payload.prompt,
            model=routed_model,
            response=generated_text,
            model_used=model_used,
            tokens=total_tokens,
            cost=total_cost,
            ttl_seconds=settings.cache_ttl_seconds,
        )

        record_model_usage(model_used)
        record_cost(model_used, total_cost)
        record_request(
            model=model_used,
            status="success",
            latency_ms=latency_ms,
            cache_hit=False,
        )

        _queue_request_log(
            background_tasks,
            tenant_id=auth_context.tenant_id,
            user_id=payload.user_id,
            api_key_hash=auth_context.api_key_hash,
            prompt=payload.prompt,
            response=generated_text,
            model_used=model_used,
            latency_ms=latency_ms,
            tokens=total_tokens,
            cost=total_cost,
            cache_hit=False,
            status_value="success",
            error_message=None,
        )

        return GenerateResponse(
            request_id=request_id,
            model_used=model_used,
            response=generated_text,
            cached=False,
            latency_ms=latency_ms,
            tokens=total_tokens,
            cost=total_cost,
            timestamp=timestamp,
        )
    except HTTPException as exc:
        latency_ms = (perf_counter() - started) * 1000.0
        record_request(
            model=routed_model,
            status="error",
            latency_ms=latency_ms,
            cache_hit=False,
        )

        _queue_request_log(
            background_tasks,
            tenant_id=auth_context.tenant_id,
            user_id=payload.user_id,
            api_key_hash=auth_context.api_key_hash,
            prompt=payload.prompt,
            response="",
            model_used=routed_model,
            latency_ms=latency_ms,
            tokens=0,
            cost=0.0,
            cache_hit=False,
            status_value="error",
            error_message=str(exc.detail),
        )
        raise
    except Exception as exc:
        latency_ms = (perf_counter() - started) * 1000.0
        record_request(
            model=routed_model,
            status="error",
            latency_ms=latency_ms,
            cache_hit=False,
        )

        _queue_request_log(
            background_tasks,
            tenant_id=auth_context.tenant_id,
            user_id=payload.user_id,
            api_key_hash=auth_context.api_key_hash,
            prompt=payload.prompt,
            response="",
            model_used=routed_model,
            latency_ms=latency_ms,
            tokens=0,
            cost=0.0,
            cache_hit=False,
            status_value="error",
            error_message=str(exc)[:1000],
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to generate response from upstream model.",
        ) from exc
