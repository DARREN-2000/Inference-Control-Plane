"""Monitors-as-code guardrail: the Datadog definitions must be valid JSON and
must only reference metrics this service actually emits (no drift between the
code's metric catalogue and the alerting layer).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from gateway_sli.governance import METRIC_REGISTRY

MONITORS = Path("monitors/datadog_monitors.json")

# One source of truth: monitor validation consumes the production metric schema.
EMITTED = frozenset(METRIC_REGISTRY)

_METRIC_RE = re.compile(r"gateway\.[a-z_.]+")


def _load():
    return json.loads(MONITORS.read_text())


def test_monitors_parse_and_have_required_fields():
    monitors = _load()
    assert isinstance(monitors, list) and monitors
    for m in monitors:
        assert m["name"] and m["type"] and m["query"] and m["message"]
        assert "thresholds" in m["options"]


def test_every_referenced_metric_is_emitted():
    for m in _load():
        for metric in _METRIC_RE.findall(m["query"]):
            assert metric in EMITTED, f"{m['name']} references unknown metric {metric}"


def test_trust_contract_monitors_present():
    queries = " ".join(m["query"] for m in _load())
    # The TTC/MGC meta-monitors must exist, not just workload SLOs.
    for metric in (
        "gateway.pipeline.freshness_seconds",
        "gateway.pipeline.records_read",
        "gateway.pipeline.export_success",
        "gateway.pipeline.unknown_dimension",
        "gateway.pipeline.series_emitted",
    ):
        assert metric in queries, metric


def test_multiwindow_burn_rate_monitors_present():
    burn = [m for m in _load() if "burn_rate(" in m["query"]]
    assert len(burn) >= 2, "expected paired fast + slow burn-rate monitors"
    windows = " ".join(m["query"] for m in burn)
    assert "short_window" in windows and "long_window" in windows


def test_series_emitted_threshold_is_derived_from_governance():
    from gateway_sli.governance import estimated_max_total_series

    ceiling = estimated_max_total_series()
    card = [m for m in _load() if "series_emitted" in m["query"]][0]
    crit = card["options"]["thresholds"]["critical"]
    # The tripwire sits just above the worst-case legitimate cardinality so it
    # cannot false-fire on real traffic, but still catches an explosion.
    assert crit >= ceiling, (crit, ceiling)
    assert crit < 2 * ceiling, (crit, ceiling)
