"""H1: team/route are enumerated allowlists, so typos, casing variants, and
id-bearing route names cannot mint unbounded time series.
"""

from __future__ import annotations

from gateway_sli import normalize as nz
from gateway_sli.config import Config
from gateway_sli.models import parse_observation


def test_unknown_team_folds_to_other(make_raw):
    cfg = Config()
    obs = parse_observation(make_raw(traceMetadata={"team": "TotallyNewTeam", "env": "prod"}))
    assert nz.team(obs, cfg) == "other"


def test_team_match_is_case_insensitive(make_raw):
    cfg = Config()
    obs = parse_observation(make_raw(traceMetadata={"team": "advisorchat", "env": "prod"}))
    assert nz.team(obs, cfg) == "AdvisorChat"


def test_blank_team_is_unattributed(make_raw):
    cfg = Config()
    obs = parse_observation(make_raw(traceMetadata={"team": "", "env": "prod"}))
    assert nz.team(obs, cfg) == "unattributed"


def test_id_bearing_route_folds_to_other(make_raw):
    cfg = Config()
    obs = parse_observation(make_raw(traceName="session-4f9a2c-user-42"))
    assert nz.route(obs, cfg) == "other"


def test_known_route_passes_through(make_raw):
    cfg = Config()
    obs = parse_observation(make_raw(traceName="advisorchat-turn"))
    assert nz.route(obs, cfg) == "advisorchat-turn"


def test_route_passthrough_when_allowlist_disabled(make_raw):
    try:
        Config(known_routes=None)
    except ValueError as exc:
        assert "bounded" in str(exc)
    else:
        raise AssertionError("open-cardinality route configuration must be rejected")


def test_malformed_route_shape_folds_to_other(make_raw):
    cfg = Config()
    obs = parse_observation(make_raw(traceName="Has Spaces And CAPS!"))
    assert nz.route(obs, cfg) == "other"
