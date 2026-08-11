from gateway_sli.config import Config
from gateway_sli.models import parse_observation
from gateway_sli.sli import aggregate


def _agg(raws):
    obs = [parse_observation(r) for r in raws]
    return aggregate(obs, 0, Config())


def test_cost_summed(make_raw):
    points, stats = _agg([make_raw(id="cost-1"), make_raw(id="cost-2")])
    cost = [p for p in points if p.name == "gateway.cost.usd"]
    assert len(cost) == 1
    assert abs(cost[0].value - 0.008) < 1e-9
    assert stats.cost_missing == 0


def test_missing_cost_surfaced(make_raw):
    raw = make_raw(costDetails={})  # empty cost, as on failed rows
    points, stats = _agg([raw])
    assert stats.cost_missing == 1
    missing = [p for p in points if p.name == "gateway.cost.records_missing"]
    assert missing and missing[0].value == 1
    cost = [p for p in points if p.name == "gateway.cost.usd"]
    assert cost[0].value == 0.0  # missing excluded, never counted as a real spend


def test_malformed_cost_is_distinct_from_missing(make_raw):
    raw = make_raw(costDetails={"total": "not-a-number"})
    points, stats = _agg([raw])
    assert stats.cost_missing == 0
    assert stats.cost_invalid == 1
    invalid = [p for p in points if p.name == "gateway.cost.records_invalid"]
    assert invalid and invalid[0].value == 1


def test_provider_region_only_bounded_values(make_raw):
    raw = make_raw(internalModelId="eu.anthropic.claude-sonnet-4-6")
    points, _ = _agg([raw])
    cost = [p for p in points if p.name == "gateway.cost.usd"][0]
    assert cost.dims["provider_region"] == "bedrock_eu"
