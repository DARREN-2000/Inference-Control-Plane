from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator, model_validator
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
    database_pool_size: int = Field(default=10, ge=1, le=200)
    database_max_overflow: int = Field(default=20, ge=0, le=200)
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
    llm_provider_order: list[str] = Field(default_factory=lambda: ["openai"])
    llm_base_url: str = "https://api.openai.com"
    llm_api_key: str | None = None
    anthropic_base_url: str = "https://api.anthropic.com"
    anthropic_api_key: str | None = None
    anthropic_version: str = "2023-06-01"
    azure_openai_base_url: str | None = None
    azure_openai_api_key: str | None = None
    azure_openai_deployment: str | None = None
    azure_openai_api_version: str = "2024-02-01"
    llm_timeout_seconds: float = Field(default=20.0, ge=1.0, le=120.0)
    llm_max_retries: int = Field(default=2, ge=0, le=5)
    llm_max_output_tokens: int = Field(default=1024, ge=1, le=8192)

    default_api_key: str = "dev-inference-key"
    auth_cache_ttl_seconds: int = Field(default=600, ge=60, le=86400)

    otlp_endpoint: str | None = None
    prometheus_namespace: str = "inference_control_plane"

    @field_validator("llm_provider_order", mode="before")
    @classmethod
    def parse_llm_provider_order(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return [item.strip() for item in value if item.strip()]
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return ["openai"]

    @model_validator(mode="after")
    def validate_runtime_security(self) -> "Settings":
        if not self.database_url:
            raise ValueError("DATABASE_URL is required.")
        if not self.redis_url:
            raise ValueError("REDIS_URL is required.")

        if self.llm_mode == "openai-compatible":
            if not self.llm_provider_order:
                raise ValueError("LLM_PROVIDER_ORDER must include at least one provider.")

            providers = {provider.lower() for provider in self.llm_provider_order}
            if "openai" in providers and not self.llm_api_key:
                raise ValueError("LLM_API_KEY is required when using the openai provider.")
            if "anthropic" in providers and not self.anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY is required when using the anthropic provider.")
            if "azure" in providers:
                if not self.azure_openai_base_url or not self.azure_openai_api_key:
                    raise ValueError("AZURE_OPENAI_BASE_URL and AZURE_OPENAI_API_KEY are required.")
                if not self.azure_openai_deployment:
                    raise ValueError(
                        "AZURE_OPENAI_DEPLOYMENT is required when using azure provider."
                    )

        if self.environment.lower() == "production":
            if self.default_api_key == "dev-inference-key":
                raise ValueError("DEFAULT_API_KEY must be overridden in production")
            if "*" in self.cors_allowed_origins:
                raise ValueError("CORS_ALLOWED_ORIGINS cannot include '*' in production")

        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
