from gateway_sli.config import AnomalyConfig
from gateway_sli.quality import robust_zscore

CFG = AnomalyConfig(min_sample=10, threshold=3.5)


def test_cold_start_below_min_sample():
    result = robust_zscore(500, [100, 110, 90], CFG)
    assert result.status == "cold_start"
    assert result.is_anomaly is False
    assert result.score is None


def test_clear_anomaly_detected():
    baseline = [200, 205, 198, 202, 199, 201, 203, 197, 200, 204, 196, 202]
    result = robust_zscore(5, baseline, CFG)
    assert result.status == "ok"
    assert result.is_anomaly is True
    assert result.score is not None and result.score < 0


def test_normal_value_not_anomaly():
    baseline = [200, 205, 198, 202, 199, 201, 203, 197, 200, 204, 196, 202]
    result = robust_zscore(201, baseline, CFG)
    assert result.status == "ok"
    assert result.is_anomaly is False


def test_constant_baseline_matching_value():
    baseline = [100] * 12
    result = robust_zscore(100, baseline, CFG)
    assert result.status == "degenerate_constant_baseline"
    assert result.is_anomaly is False


def test_constant_baseline_deviating_value():
    baseline = [100] * 12
    result = robust_zscore(150, baseline, CFG)
    assert result.status == "degenerate_constant_baseline"
    assert result.is_anomaly is True
    assert result.score is None


def test_threshold_is_configurable():
    baseline = [200, 205, 198, 202, 199, 201, 203, 197, 200, 204, 196, 202]
    strict = AnomalyConfig(min_sample=10, threshold=2.0)
    loose = AnomalyConfig(min_sample=10, threshold=50.0)
    assert robust_zscore(215, baseline, strict).is_anomaly is True
    assert robust_zscore(215, baseline, loose).is_anomaly is False
