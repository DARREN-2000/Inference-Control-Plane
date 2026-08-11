from gateway_sli.models import parse_observation
from gateway_sli.sli import _percentile


def test_percentile_interpolation():
    values = [10, 20, 30, 40, 50]
    assert _percentile(values, 50) == 30
    assert abs(_percentile(values, 95) - 48.0) < 1e-9
    assert abs(_percentile(values, 99) - 49.6) < 1e-9


def test_percentile_edge_cases():
    assert _percentile([], 50) is None
    assert _percentile([42], 99) == 42


def test_latency_ms(make_raw):
    raw = make_raw(
        startTime="2026-01-15T09:14:22.000Z",
        endTime="2026-01-15T09:14:24.100Z",
    )
    obs = parse_observation(raw)
    assert abs(obs.latency_ms - 2100.0) < 1e-6
