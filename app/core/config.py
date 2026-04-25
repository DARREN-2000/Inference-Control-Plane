from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Inference Control Plane"
    service_name: str = "inference-control-plane"
    environment: str = "development"
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000
    cors_allowed_origins: list[str] = ["http://localhost:3000"]

    database_url: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/inference_cp"
    redis_url: str = "redis://redis:6379/0"

    cache_ttl_seconds: int = Field(default=300, ge=1, le=86400)
    rate_limit_window_seconds: int = Field(default=60, ge=1, le=3600)
    default_rate_limit_per_minute: int = Field(default=120, ge=1)
    user_rate_limit_per_minute: int = Field(default=60, ge=1)

    cheap_model_name: str = "cheap-model"
    premium_model_name: str = "premium-model"
    router_token_threshold: int = Field(default=1200, ge=1)

    cheap_model_cost_per_1k_tokens: float = Field(default=0.0008, ge=0)
    premium_model_cost_per_1k_tokens: float = Field(default=0.01, ge=0)

    llm_mode: Literal["simulated", "openai-compatible"] = "simulated"
    llm_base_url: str = "https://api.openai.com"
    llm_api_key: str | None = None
    llm_timeout_seconds: float = Field(default=20.0, ge=1.0, le=120.0)
    llm_max_retries: int = Field(default=2, ge=0, le=5)

    default_api_key: str = "dev-inference-key"
    auth_cache_ttl_seconds: int = Field(default=600, ge=60, le=86400)

    otlp_endpoint: str | None = None
    prometheus_namespace: str = "inference_control_plane"


@lru_cache
def get_settings() -> Settings:
    return Settings()
