from inference_control_plane.core.config import Settings
from inference_control_plane.schemas.generate import GenerateRequest
from inference_control_plane.services.router import choose_model, estimate_tokens


def test_estimate_tokens_minimum_one() -> None:
    assert estimate_tokens("") == 1


def test_choose_model_honors_override() -> None:
    settings = Settings()
    payload = GenerateRequest(
        prompt="Short prompt",
        user_id="user-1",
        priority="low",
        model_override="custom-model",
    )

    decision = choose_model(payload, settings)

    assert decision.model == "custom-model"


def test_choose_model_uses_premium_for_high_priority() -> None:
    settings = Settings()
    payload = GenerateRequest(
        prompt="Short prompt",
        user_id="user-1",
        priority="high",
    )

    decision = choose_model(payload, settings)

    assert decision.model == settings.premium_model_name


def test_choose_model_uses_token_threshold_for_low_priority() -> None:
    settings = Settings(router_token_threshold=10)
    payload = GenerateRequest(
        prompt="x" * 100,
        user_id="user-1",
        priority="low",
    )

    decision = choose_model(payload, settings)

    assert decision.estimated_tokens > settings.router_token_threshold
    assert decision.model == settings.premium_model_name
