import hashlib
import time
from collections.abc import Awaitable, Callable

import httpx
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential

from inference_control_plane.core.config import Settings


class LLMClientError(RuntimeError):
    pass


class LLMClientRetryableError(LLMClientError):
    pass


class LLMClientTimeoutError(LLMClientRetryableError):
    pass


class CircuitBreakerOpenError(LLMClientError):
    pass


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

    def record_success(self):
        self.failure_count = 0
        self.state = "CLOSED"

    def is_allowed(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        if self.state == "HALF_OPEN":
            return True
        return True


_shared_client: httpx.AsyncClient | None = None
_circuit_breaker = CircuitBreaker()


def init_http_client(settings: Settings) -> None:
    global _shared_client
    if _shared_client is None:
        _shared_client = httpx.AsyncClient(timeout=settings.llm_timeout_seconds)


async def close_http_client() -> None:
    global _shared_client
    if _shared_client is not None:
        await _shared_client.aclose()
        _shared_client = None


def _get_client() -> httpx.AsyncClient:
    if _shared_client is None:
        raise LLMClientError("HTTP client is not initialized.")
    return _shared_client


def _simulated_response(prompt: str, model: str) -> str:
    prompt_preview = prompt.strip().replace("\n", " ")[:180]
    digest = hashlib.sha1(prompt.encode("utf-8")).hexdigest()[:8]
    return f"[{model}] simulated response :: {prompt_preview} :: id={digest}"


def _extract_message_text(payload: dict) -> str:
    choices = payload.get("choices", [])
    if not choices:
        raise LLMClientError("LLM response payload had no choices.")

    first_choice = choices[0]
    message = first_choice.get("message", {})

    if isinstance(message, dict) and "content" in message:
        return str(message["content"])

    if "text" in first_choice:
        return str(first_choice["text"])

    raise LLMClientError("Unable to extract generated text from LLM response payload.")


def _extract_anthropic_text(payload: dict) -> str:
    content = payload.get("content", [])
    if not content:
        raise LLMClientError("Anthropic response payload had no content.")

    first_block = content[0]
    if isinstance(first_block, dict) and "text" in first_block:
        return str(first_block["text"])

    raise LLMClientError("Unable to extract generated text from Anthropic payload.")


async def _request_with_retry(
    settings: Settings,
    request_fn: Callable[[], Awaitable[str]],
) -> str:
    if not _circuit_breaker.is_allowed():
        raise CircuitBreakerOpenError("Circuit breaker is OPEN. Fast failing request.")

    retryer = AsyncRetrying(
        retry=retry_if_exception_type(LLMClientRetryableError),
        stop=stop_after_attempt(settings.llm_max_retries + 1),
        wait=wait_exponential(multiplier=0.25, min=0.25, max=2.0),
        reraise=True,
    )
    try:
        async for attempt in retryer:
            with attempt:
                result = await request_fn()
                _circuit_breaker.record_success()
                return result
        raise LLMClientError("LLM request failed unexpectedly.")
    except Exception:
        _circuit_breaker.record_failure()
        raise


def _coerce_retryable_error(exc: Exception) -> LLMClientError:
    if isinstance(exc, httpx.TimeoutException):
        return LLMClientTimeoutError("LLM request timed out.")
    if isinstance(exc, httpx.HTTPStatusError):
        status_code = exc.response.status_code
        if 500 <= status_code < 600:
            return LLMClientRetryableError("LLM provider returned a server error.")
        return LLMClientError(f"LLM provider returned status {status_code}.")
    if isinstance(exc, httpx.RequestError):
        return LLMClientRetryableError("LLM request failed due to a network error.")
    if isinstance(exc, LLMClientError):
        return exc
    return LLMClientError("LLM request failed unexpectedly.")


async def _request_openai_compatible(
    settings: Settings,
    *,
    prompt: str,
    model: str,
    provider_api_key: str | None = None,
) -> str:
    key_to_use = provider_api_key or settings.llm_api_key
    if not key_to_use:
        raise LLMClientError("LLM_API_KEY is required when llm_mode=openai-compatible.")

    endpoint = f"{settings.llm_base_url.rstrip('/')}/v1/chat/completions"
    headers = {"Authorization": "Bearer " + key_to_use}
    body = {
        "model": model,
        "max_tokens": settings.llm_max_output_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }

    async def _execute() -> str:
        try:
            client = _get_client()
            response = await client.post(endpoint, json=body, headers=headers)
            response.raise_for_status()
            payload = response.json()
            return _extract_message_text(payload)
        except (httpx.HTTPStatusError, httpx.RequestError, httpx.TimeoutException) as exc:
            raise _coerce_retryable_error(exc) from exc
        except (ValueError, KeyError, IndexError, TypeError, LLMClientError) as exc:
            raise LLMClientError("Unable to parse LLM response payload.") from exc

    return await _request_with_retry(settings, _execute)


async def _request_azure_openai(
    settings: Settings,
    *,
    prompt: str,
    model: str,
) -> str:
    if not settings.azure_openai_base_url or not settings.azure_openai_api_key:
        raise LLMClientError("Azure OpenAI configuration is missing.")
    if not settings.azure_openai_deployment:
        raise LLMClientError("Azure OpenAI deployment is required.")

    endpoint = f"{settings.azure_openai_base_url.rstrip('/')}/openai/deployments/{settings.azure_openai_deployment}/chat/completions"
    headers = {"api-key": settings.azure_openai_api_key}
    params = {"api-version": settings.azure_openai_api_version}
    body = {
        "model": model,
        "max_tokens": settings.llm_max_output_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }

    async def _execute() -> str:
        try:
            client = _get_client()
            response = await client.post(endpoint, json=body, headers=headers, params=params)
            response.raise_for_status()
            payload = response.json()
            return _extract_message_text(payload)
        except (httpx.HTTPStatusError, httpx.RequestError, httpx.TimeoutException) as exc:
            raise _coerce_retryable_error(exc) from exc
        except (ValueError, KeyError, IndexError, TypeError, LLMClientError) as exc:
            raise LLMClientError("Unable to parse Azure OpenAI response payload.") from exc

    return await _request_with_retry(settings, _execute)


async def _request_anthropic(
    settings: Settings,
    *,
    prompt: str,
    model: str,
) -> str:
    if not settings.anthropic_api_key:
        raise LLMClientError("Anthropic API key is required when using the anthropic provider.")

    endpoint = f"{settings.anthropic_base_url.rstrip('/')}/v1/messages"
    headers = {
        "x-api-key": settings.anthropic_api_key,
        "anthropic-version": settings.anthropic_version,
    }
    body = {
        "model": model,
        "max_tokens": settings.llm_max_output_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }

    async def _execute() -> str:
        try:
            client = _get_client()
            response = await client.post(endpoint, json=body, headers=headers)
            response.raise_for_status()
            payload = response.json()
            return _extract_anthropic_text(payload)
        except (httpx.HTTPStatusError, httpx.RequestError, httpx.TimeoutException) as exc:
            raise _coerce_retryable_error(exc) from exc
        except (ValueError, KeyError, IndexError, TypeError, LLMClientError) as exc:
            raise LLMClientError("Unable to parse Anthropic response payload.") from exc

    return await _request_with_retry(settings, _execute)


async def generate_completion(
    settings: Settings,
    *,
    prompt: str,
    model: str,
    provider_api_key: str | None = None,
) -> str:
    if settings.llm_mode == "simulated":
        return _simulated_response(prompt=prompt, model=model)

    providers = [provider.lower() for provider in settings.llm_provider_order]
    last_timeout: LLMClientTimeoutError | None = None

    for provider in providers:
        try:
            if provider == "openai":
                return await _request_openai_compatible(settings, prompt=prompt, model=model, provider_api_key=provider_api_key)
            if provider == "anthropic":
                return await _request_anthropic(settings, prompt=prompt, model=model)
            if provider == "azure":
                return await _request_azure_openai(settings, prompt=prompt, model=model)
            raise LLMClientError(f"Unknown LLM provider '{provider}'.")
        except LLMClientTimeoutError as exc:
            last_timeout = exc
            continue

    if last_timeout is not None:
        raise last_timeout
    raise LLMClientError("No available LLM providers succeeded.")
