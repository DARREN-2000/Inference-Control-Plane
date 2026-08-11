"""M2: baseline grouping keys map to CLEAN allowlisted dimensions. route_model
grouping must not leak a synthetic 'route|model' string into the route label.
"""

from __future__ import annotations

from gateway_sli.config import AnomalyConfig, Config
from gateway_sli.models import parse_observation
from gateway_sli.quality import QualityKey, group_completion_lengths


def test_route_grouping_produces_route_only_dims(make_raw):
    cfg = Config()
    groups = group_completion_lengths([parse_observation(make_raw())], cfg)
    keys = list(groups.keys())
    assert keys == [QualityKey(route="advisorchat-turn")]
    assert keys[0].as_dict() == {"route": "advisorchat-turn"}


def test_route_model_grouping_uses_separate_model_dim(make_raw):
    cfg = Config(anomaly=AnomalyConfig(baseline_grouping="route_model"))
    groups = group_completion_lengths([parse_observation(make_raw())], cfg)
    key = next(iter(groups))
    # model_family lives in its OWN allowlisted dimension, not concatenated into route.
    assert key.as_dict() == {"route": "advisorchat-turn", "model_family": "claude-sonnet"}
    assert "|" not in key.route
