import asyncio
import hashlib

import httpx

from app.core.config import Settings


class LLMClientError(RuntimeError):
    pass


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


async def _request_openai_compatible(
    settings: Settings,
    *,
    prompt: str,
    model: str,
) -> str:
    if not settings.llm_api_key:
        raise LLMClientError("LLM_API_KEY is required when llm_mode=openai-compatible.")

    endpoint = f"{settings.llm_base_url.rstrip('/')}/v1/chat/completions"
    headers = {"Authorization": f"Bearer {settings.llm_api_key}"}
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }

    max_attempts = settings.llm_max_retries + 1
    for attempt in range(max_attempts):
        try:
            async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
                response = await client.post(endpoint, json=body, headers=headers)
                response.raise_for_status()
                payload = response.json()
                return _extract_message_text(payload)
        except (
            httpx.RequestError,
            httpx.HTTPStatusError,
            ValueError,
            KeyError,
            IndexError,
            TypeError,
            LLMClientError,
        ) as exc:
            if attempt + 1 >= max_attempts:
                raise LLMClientError("LLM request failed after retries.") from exc
            await asyncio.sleep(min(0.25 * (2**attempt), 2.0))

    raise LLMClientError("LLM request failed unexpectedly.")


async def generate_completion(
    settings: Settings,
    *,
    prompt: str,
    model: str,
) -> str:
    if settings.llm_mode == "simulated":
        return _simulated_response(prompt=prompt, model=model)
    return await _request_openai_compatible(settings, prompt=prompt, model=model)
