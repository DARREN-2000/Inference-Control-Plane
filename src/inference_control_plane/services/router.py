import math
from dataclasses import dataclass

from inference_control_plane.core.config import Settings
from inference_control_plane.schemas.generate import GenerateRequest


@dataclass(slots=True)
class RouteDecision:
    model_tier: str
    estimated_tokens: int
    model_override: str | None = None
    provider_override: str | None = None

def estimate_tokens(text: str) -> int:
    return max(1, math.ceil(len(text) / 4))

def choose_model(request: GenerateRequest, settings: Settings) -> RouteDecision:
    estimated_tokens = estimate_tokens(request.prompt)

    if request.model_override:
        return RouteDecision(
            model_tier="override",
            estimated_tokens=estimated_tokens,
            model_override=request.model_override.strip(),
            provider_override=request.provider_override.strip() if request.provider_override else None,
        )

    tier = "premium" if request.priority == "high" or estimated_tokens > settings.router_token_threshold else "cheap"
    return RouteDecision(
        model_tier=tier,
        estimated_tokens=estimated_tokens,
        provider_override=request.provider_override.strip() if request.provider_override else None,
    )
