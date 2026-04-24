from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=20000)
    user_id: str = Field(..., min_length=1, max_length=128)
    priority: Literal["low", "high"] = "low"
    model_override: str | None = Field(default=None, max_length=128)


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
