from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=20000)
    user_id: str = Field(..., min_length=1, max_length=128)
    priority: Literal["low", "high"] = "low"
    model_override: str | None = Field(default=None, max_length=128)
    provider_override: str | None = Field(default=None, max_length=128)
    provider_api_key: str | None = Field(default=None, description="Optional BYOK API Key to use instead of the system default")


class GenerateResponse(BaseModel):
    request_id: str
    model_used: str
    response: str
    cached: bool
    latency_ms: float
    tokens: int
    cost: float
    timestamp: datetime


class UsageSummaryResponse(BaseModel):
    user_id: str
    requests: int
    total_tokens: int
    total_cost: float


class UsageLogEntry(BaseModel):
    request_id: str
    model_used: str
    latency_ms: float
    tokens: int
    cost: float
    cache_hit: bool
    status: str
    created_at: datetime
    error_message: str | None


class UsageLogsResponse(BaseModel):
    user_id: str
    limit: int
    entries: list[UsageLogEntry]


class DashboardMetric(BaseModel):
    label: str
    value: str
    delta: str


class DashboardMetricsResponse(BaseModel):
    metrics: list[DashboardMetric]


class DashboardActivityResponse(BaseModel):
    activity: list[str]
