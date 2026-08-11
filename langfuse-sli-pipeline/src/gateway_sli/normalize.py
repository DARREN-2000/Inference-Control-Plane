"""Normalization + the privacy projection boundary.

Every function here converts raw/observation data into BOUNDED, allowlisted
values drawn from the Metric Governance Contract (governance.py). The aggregation
layer may only key on values produced here. Unknown values fold into 'other'
(or 'unattributed' for a blank team) to keep cardinality bounded.

``folded_dimensions`` reports which governed dimensions folded a NON-BLANK input
to a token; the pipeline turns this into the ``gateway.pipeline.unknown_dimension``
governance signal so silent onboarding gaps become visible.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .config import Config
from .governance import OTHER, UNATTRIBUTED, UNKNOWN
from .models import Observation

# --- model family (bounded via explicit rules; unknown -> 'other') ---------
_MODEL_RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"^claude-sonnet", re.I), "claude-sonnet"),
    (re.compile(r"^claude-haiku", re.I), "claude-haiku"),
    (re.compile(r"^claude-opus", re.I), "claude-opus"),
    (re.compile(r"^gpt-5(\.|-).*mini", re.I), "gpt-5-mini"),
    (re.compile(r"^gpt-5", re.I), "gpt-5"),
    (re.compile(r"^gpt-4o", re.I), "gpt-4o"),
]


def model_family(provided_model: str) -> str:
    value = (provided_model or "").lower()
    # Bedrock/provider-qualified IDs often prefix the Claude family name.
    if "claude" in value:
        if "sonnet" in value:
            return "claude-sonnet"
        if "haiku" in value:
            return "claude-haiku"
        if "opus" in value:
            return "claude-opus"
    # Do not greedily classify unregistered variants such as gpt-5-nano.
    if re.match(r"^gpt-5(?:[.-]\d+)*(?:[-.].*mini)$", value):
        return "gpt-5-mini"
    if re.match(r"^gpt-5(?:[.-]\d+)*$", value):
        return "gpt-5"
    for rx, name in _MODEL_RULES:
        if name in {"gpt-5", "gpt-5-mini"}:
            continue
        if rx.match(provided_model or ""):
            return name
    return OTHER


# --- error category (bounded map on structured error.type; never statusMessage) ---
_ERROR_TYPE_MAP: dict[str, str] = {
    "throttlingexception": "throttling",
    "ratelimiterror": "throttling",
    "ratelimitexception": "throttling",
    "timeouterror": "timeout",
    "timeoutexception": "timeout",
    "serviceunavailable": "provider_error",
    "serviceunavailableexception": "provider_error",
    "internalservererror": "provider_error",
    "modelerrorexception": "provider_error",
    "authenticationerror": "auth",
    "accessdeniedexception": "auth",
    "badrequesterror": "invalid_request",
    "validationexception": "invalid_request",
    "contentpolicyviolation": "content_filter",
}


def error_category(obs: Observation) -> str | None:
    if not obs.is_error:
        return None
    etype = (obs.error or {}).get("type") if obs.error else None
    if etype:
        return _ERROR_TYPE_MAP.get(str(etype).lower(), UNKNOWN)
    return UNKNOWN


# --- env (bounded) ---------------------------------------------------------
_ENV_MAP = {
    "production": "prod",
    "prod": "prod",
    "staging": "staging",
    "stage": "staging",
    "dev": "dev",
    "development": "dev",
}


def env(obs: Observation) -> str:
    return _ENV_MAP.get((obs.env_raw or "").lower(), OTHER)


def team(obs: Observation, cfg: Config) -> str:
    """Case-insensitive match against the enumerated team allowlist.

    Blank -> 'unattributed' (a real, distinct governance state). Any non-blank
    team not in the allowlist -> 'other', so typos and casing variants cannot
    mint new series.
    """
    raw = (obs.team or "").strip()
    if not raw:
        return UNATTRIBUTED
    canonical = {t.lower(): t for t in cfg.known_teams}
    return canonical.get(raw.lower(), OTHER)


# route names must both be well-shaped AND (when an allowlist is configured) known.
_ROUTE_RX = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$", re.I)


def route(obs: Observation, cfg: Config) -> str:
    r = (obs.route or "").strip()
    if not _ROUTE_RX.match(r):
        return OTHER
    canonical = {value.lower(): value for value in (cfg.known_routes or ())}
    normalized = canonical.get(r.lower())
    if normalized is None:
        return OTHER
    return normalized


# provider_region: explicit bounded mapping only. Do NOT parse arbitrary values
# out of internalModelId. Unknown -> 'other'.
_PROVIDER_MAP: list[tuple[str, str]] = [
    ("eu.anthropic", "bedrock_eu"),
    ("us.anthropic", "bedrock_us"),
    ("external", "external_zdr"),
]


def provider_region(obs: Observation) -> str:
    im = obs.internal_model or ""
    for prefix, value in _PROVIDER_MAP:
        if im.startswith(prefix):
            return value
    return OTHER


def folded_dimensions(obs: Observation, cfg: Config) -> list[str]:
    """Return the governed dimensions that folded a NON-BLANK raw value to a
    fold token. Used to emit the unknown-dimension governance signal. A blank
    input is NOT a fold (it is expected), so it is not reported here.
    """
    folds: list[str] = []
    if (obs.team or "").strip() and team(obs, cfg) == OTHER:
        folds.append("team")
    if (obs.route or "").strip() and route(obs, cfg) == OTHER:
        folds.append("route")
    if (obs.provided_model or "").strip() and model_family(obs.provided_model) == OTHER:
        folds.append("model_family")
    if (obs.env_raw or "").strip() and env(obs) == OTHER:
        folds.append("env")
    if (obs.internal_model or "").strip() and provider_region(obs) == OTHER:
        folds.append("provider_region")
    return folds


@dataclass(frozen=True)
class PrimaryDims:
    """The only dimension set allowed on primary latency/ttft/count SLIs."""

    team: str
    route: str
    model_family: str
    env: str

    def as_dict(self) -> dict[str, str]:
        return {
            "team": self.team,
            "route": self.route,
            "model_family": self.model_family,
            "env": self.env,
        }


def primary_dims(obs: Observation, cfg: Config) -> PrimaryDims:
    return PrimaryDims(
        team=team(obs, cfg),
        route=route(obs, cfg),
        model_family=model_family(obs.provided_model),
        env=env(obs),
    )
