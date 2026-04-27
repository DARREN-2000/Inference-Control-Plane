import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_openai_mode_requires_api_key() -> None:
    with pytest.raises(ValidationError, match="LLM_API_KEY is required"):
        Settings(llm_mode="openai-compatible", llm_api_key=None)


def test_production_rejects_default_api_key() -> None:
    with pytest.raises(ValidationError, match="DEFAULT_API_KEY"):
        Settings(environment="production", default_api_key="dev-inference-key")


def test_production_rejects_wildcard_cors() -> None:
    with pytest.raises(ValidationError, match="CORS_ALLOWED_ORIGINS"):
        Settings(
            environment="production",
            default_api_key="replace-me",
            cors_allowed_origins=["*"],
        )


def test_valid_production_config() -> None:
    settings = Settings(
        environment="production",
        default_api_key="prod-key-123",
        cors_allowed_origins=["https://console.example.com"],
        llm_mode="simulated",
    )

    assert settings.environment == "production"
