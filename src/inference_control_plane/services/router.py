from dataclasses import dataclass

from inference_control_plane.core.config import Settings
from inference_control_plane.schemas.generate import GenerateRequest


@dataclass(slots=True)
class RouteDecision:
    model: str
    estimated_tokens: int


def estimate_tokens_from_length(length: int) -> int:
    # Approximate token estimation suitable for model-routing and cost estimation.
    return max(1, (length + 3) // 4)


def estimate_tokens(text: str) -> int:
    return estimate_tokens_from_length(len(text))


def choose_model(request: GenerateRequest, settings: Settings) -> RouteDecision:
    estimated_tokens = estimate_tokens(request.prompt)

    if request.model_override:
        return RouteDecision(
            model=request.model_override.strip(),
            estimated_tokens=estimated_tokens,
        )

    if request.priority == "high":
        return RouteDecision(model=settings.premium_model_name, estimated_tokens=estimated_tokens)

    routed_model = (
        settings.premium_model_name
        if estimated_tokens > settings.router_token_threshold
        else settings.cheap_model_name
    )
    return RouteDecision(model=routed_model, estimated_tokens=estimated_tokens)
