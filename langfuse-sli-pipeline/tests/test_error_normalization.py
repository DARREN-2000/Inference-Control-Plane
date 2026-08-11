from gateway_sli.models import parse_observation
from gateway_sli.normalize import error_category


def test_success_has_no_category(make_raw):
    assert error_category(parse_observation(make_raw())) is None


def test_throttling_mapped(make_raw):
    raw = make_raw(
        level="ERROR",
        completionStartTime=None,
        statusMessage="throttling_exception: Rate exceeded for model X in eu-central-1",
        metadata={
            "error": {"type": "ThrottlingException", "provider": "bedrock", "retryable": True}
        },
    )
    assert error_category(parse_observation(raw)) == "throttling"


def test_unknown_type_folds_to_unknown(make_raw):
    raw = make_raw(
        level="ERROR",
        completionStartTime=None,
        metadata={"error": {"type": "SomethingBrandNew", "provider": "x"}},
    )
    assert error_category(parse_observation(raw)) == "unknown"


def test_error_level_without_structured_error(make_raw):
    raw = make_raw(level="ERROR", completionStartTime=None, metadata={})
    assert error_category(parse_observation(raw)) == "unknown"
