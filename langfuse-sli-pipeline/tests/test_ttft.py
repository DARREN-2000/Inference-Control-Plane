from gateway_sli.models import parse_observation


def test_ttft_streaming_success(make_raw):
    obs = parse_observation(make_raw())
    assert obs.ttft_ms is not None
    assert abs(obs.ttft_ms - 400.0) < 1e-6


def test_ttft_none_for_error(make_raw):
    raw = make_raw(level="ERROR", completionStartTime=None)
    obs = parse_observation(raw)
    assert obs.ttft_ms is None


def test_ttft_none_when_missing_completion_start(make_raw):
    obs = parse_observation(make_raw(completionStartTime=None))
    assert obs.ttft_ms is None


def test_ttft_none_for_non_streaming(make_raw):
    raw = make_raw(modelParameters={"temperature": 0.0, "max_tokens": 256, "stream": False})
    obs = parse_observation(raw)
    assert obs.ttft_ms is None
