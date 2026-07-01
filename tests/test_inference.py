import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from decimal import Decimal
from fastapi import HTTPException

from inference_control_plane.core.config import Settings
from inference_control_plane.services.inference import (
    redact_pii,
    _estimate_cost,
    _fallback_model,
    _persist_request_log,
    _queue_request_log,
    _enforce_rate_limits,
    _generate_with_fallback,
    handle_generate_request
)
from inference_control_plane.schemas.generate import GenerateRequest
from inference_control_plane.services.auth import AuthContext
from inference_control_plane.services.llm_client import LLMClientError
from inference_control_plane.services.cache import CachedResponse

def test_redact_pii():
    text = "Contact me at user@example.com or user.name+tag@sub.domain.co.uk."
    redacted = redact_pii(text)
    assert redacted == "Contact me at [REDACTED_EMAIL] or [REDACTED_EMAIL]."
    assert redact_pii("Hello world") == "Hello world"

def test_estimate_cost():
    settings = Settings(cheap_model_cost_per_1k_tokens=0.001, premium_model_cost_per_1k_tokens=0.01)
    assert _estimate_cost(settings.cheap_model_name, 1000, settings) == 0.001
    assert _estimate_cost(settings.premium_model_name, 2000, settings) == 0.02
    assert _estimate_cost("unknown-model", 1000, settings) == 0.01

def test_fallback_model():
    settings = Settings()
    assert _fallback_model(settings.cheap_model_name, settings) == settings.premium_model_name
    assert _fallback_model(settings.premium_model_name, settings) == settings.cheap_model_name
    assert _fallback_model("unknown-model", settings) is None

@pytest.mark.asyncio
async def test_persist_request_log():
    mock_session = AsyncMock()
    mock_session_factory = MagicMock(return_value=mock_session)
    mock_session.__aenter__.return_value = mock_session

    await _persist_request_log(mock_session_factory, tenant_id="tenant", user_id="user", api_key_hash="hash", prompt="prompt", response="response", model_used="model", latency_ms=100.0, tokens=10, cost=0.01, cache_hit=False, status_value="success", error_message=None)
    assert mock_session.add.call_count == 1
    assert mock_session.commit.call_count == 1

    mock_session.commit.side_effect = Exception("db error")
    await _persist_request_log(mock_session_factory, tenant_id="tenant", user_id="user", api_key_hash="hash", prompt="prompt", response="response", model_used="model", latency_ms=100.0, tokens=10, cost=0.01, cache_hit=False, status_value="success", error_message=None)
    assert mock_session.rollback.call_count == 1

def test_queue_request_log():
    mock_tasks = MagicMock()
    with patch("inference_control_plane.services.inference.get_session_factory", return_value=MagicMock()):
        _queue_request_log(mock_tasks, tenant_id="tenant", user_id="user", api_key_hash="hash", prompt="prompt", response="response", model_used="model", latency_ms=100.0, tokens=10, cost=0.01, cache_hit=False, status_value="success", error_message=None)
        assert mock_tasks.add_task.call_count == 1

@pytest.mark.asyncio
async def test_enforce_rate_limits():
    settings = Settings(rate_limit_window_seconds=60, user_rate_limit_per_minute=60)
    auth_context = AuthContext(tenant_id="tenant", api_key_hash="hash", rate_limit_per_minute=100, role="tenant")
    mock_redis = AsyncMock()

    class MockResult:
        def __init__(self, allowed, retry_after_seconds):
            self.allowed = allowed
            self.retry_after_seconds = retry_after_seconds

    with patch("inference_control_plane.services.inference.check_rate_limit") as mock_check:
        mock_check.side_effect = [MockResult(allowed=True, retry_after_seconds=0), MockResult(allowed=True, retry_after_seconds=0)]
        await _enforce_rate_limits(auth_context=auth_context, user_id="user", redis_client=mock_redis, settings=settings)

        mock_check.side_effect = [MockResult(allowed=False, retry_after_seconds=10), MockResult(allowed=True, retry_after_seconds=0)]
        with pytest.raises(HTTPException) as exc:
            await _enforce_rate_limits(auth_context=auth_context, user_id="user", redis_client=mock_redis, settings=settings)
        assert exc.value.status_code == 429
        assert "API key" in exc.value.detail

        mock_check.side_effect = [MockResult(allowed=True, retry_after_seconds=0), MockResult(allowed=False, retry_after_seconds=10)]
        with pytest.raises(HTTPException) as exc:
            await _enforce_rate_limits(auth_context=auth_context, user_id="user", redis_client=mock_redis, settings=settings)
        assert exc.value.status_code == 429
        assert "User" in exc.value.detail

@pytest.mark.asyncio
async def test_generate_with_fallback():
    settings = Settings()
    with patch("inference_control_plane.services.inference.generate_completion") as mock_generate:
        mock_generate.return_value = "success"
        model, res = await _generate_with_fallback(model=settings.cheap_model_name, prompt="test", settings=settings)
        assert model == settings.cheap_model_name
        assert res == "success"

        mock_generate.side_effect = [LLMClientError("error"), "fallback_success"]
        model, res = await _generate_with_fallback(model=settings.cheap_model_name, prompt="test", settings=settings)
        assert model == settings.premium_model_name
        assert res == "fallback_success"

        mock_generate.side_effect = LLMClientError("error")
        with pytest.raises(LLMClientError):
            await _generate_with_fallback(model="unknown-model", prompt="test", settings=settings)

@pytest.mark.asyncio
async def test_handle_generate_request_cached():
    settings = Settings()
    auth_context = AuthContext(tenant_id="tenant", api_key_hash="hash", rate_limit_per_minute=100, role="tenant")
    payload = GenerateRequest(prompt="test", user_id="user")
    mock_redis = AsyncMock()
    mock_tasks = MagicMock()

    with patch("inference_control_plane.services.inference._enforce_rate_limits"):
        with patch("inference_control_plane.services.inference.get_cached_response") as mock_cache:
            mock_cache.return_value = CachedResponse(model_used="model", response="response", tokens=10, cost=0.01)
            with patch("inference_control_plane.services.inference._queue_request_log") as mock_queue:
                res = await handle_generate_request(payload=payload, auth_context=auth_context, settings=settings, redis_client=mock_redis, background_tasks=mock_tasks)
                assert res.cached is True
                assert res.model_used == "model"
                assert res.response == "response"
                assert mock_queue.call_count == 1

@pytest.mark.asyncio
async def test_handle_generate_request_not_cached():
    settings = Settings()
    auth_context = AuthContext(tenant_id="tenant", api_key_hash="hash", rate_limit_per_minute=100, role="tenant")
    payload = GenerateRequest(prompt="test", user_id="user")
    mock_redis = AsyncMock()
    mock_tasks = MagicMock()

    with patch("inference_control_plane.services.inference._enforce_rate_limits"):
        with patch("inference_control_plane.services.inference.get_cached_response", return_value=None):
            with patch("inference_control_plane.services.inference._generate_with_fallback", return_value=("model", "generated")):
                with patch("inference_control_plane.services.inference._estimate_cost", return_value=0.01):
                    with patch("inference_control_plane.services.inference._queue_request_log") as mock_queue:
                        res = await handle_generate_request(payload=payload, auth_context=auth_context, settings=settings, redis_client=mock_redis, background_tasks=mock_tasks)
                        assert res.cached is False
                        assert res.model_used == "model"
                        assert res.response == "generated"
                        assert mock_queue.call_count == 1
                        assert mock_tasks.add_task.call_count == 1

@pytest.mark.asyncio
async def test_handle_generate_request_http_exception():
    settings = Settings()
    auth_context = AuthContext(tenant_id="tenant", api_key_hash="hash", rate_limit_per_minute=100, role="tenant")
    payload = GenerateRequest(prompt="test", user_id="user")
    mock_redis = AsyncMock()
    mock_tasks = MagicMock()

    with patch("inference_control_plane.services.inference._enforce_rate_limits", side_effect=HTTPException(status_code=429, detail="rate limit")):
        with patch("inference_control_plane.services.inference._queue_request_log") as mock_queue:
            with pytest.raises(HTTPException) as exc:
                await handle_generate_request(payload=payload, auth_context=auth_context, settings=settings, redis_client=mock_redis, background_tasks=mock_tasks)
            assert exc.value.status_code == 429
            assert mock_queue.call_count == 1
            assert mock_queue.call_args[1]["status_value"] == "error"

@pytest.mark.asyncio
async def test_handle_generate_request_internal_exception():
    settings = Settings()
    auth_context = AuthContext(tenant_id="tenant", api_key_hash="hash", rate_limit_per_minute=100, role="tenant")
    payload = GenerateRequest(prompt="test", user_id="user")
    mock_redis = AsyncMock()
    mock_tasks = MagicMock()

    with patch("inference_control_plane.services.inference._enforce_rate_limits", side_effect=ValueError("internal error")):
        with patch("inference_control_plane.services.inference._queue_request_log") as mock_queue:
            with pytest.raises(HTTPException) as exc:
                await handle_generate_request(payload=payload, auth_context=auth_context, settings=settings, redis_client=mock_redis, background_tasks=mock_tasks)
            assert exc.value.status_code == 502
            assert mock_queue.call_count == 1
            assert mock_queue.call_args[1]["status_value"] == "error"
