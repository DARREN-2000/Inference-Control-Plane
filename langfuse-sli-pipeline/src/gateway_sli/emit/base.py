from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from ..governance import ALLOWED_ATTRIBUTE_KEYS, METRIC_REGISTRY, REGISTRY
from ..sli import MetricPoint

# The bounded set of attribute keys any exporter is permitted to emit is DERIVED
# from the Metric Governance Contract (governance.py) - defense in depth: even if
# aggregation produced an unexpected key, the exporter drops it. Tests assert
# emitted points never exceed this set.
__all__ = ["ALLOWED_ATTRIBUTE_KEYS", "assert_allowed", "Exporter"]


def assert_allowed(points: Sequence[MetricPoint]) -> None:
    for p in points:
        definition = METRIC_REGISTRY.get(p.name)
        if definition is None:
            raise ValueError(f"unregistered metric: {p.name}")
        if p.type != definition.type or p.unit != definition.unit:
            raise ValueError(
                f"metric {p.name} has invalid shape: {p.type}/{p.unit}; "
                f"expected {definition.type}/{definition.unit}"
            )
        forbidden = set(p.dims) - definition.allowed_dimensions
        if forbidden:
            raise ValueError(
                f"metric {p.name} has dimensions not allowed for this metric: {sorted(forbidden)}"
            )
        extra = set(p.dims) - ALLOWED_ATTRIBUTE_KEYS
        if extra:
            raise ValueError(f"metric {p.name} has disallowed attributes: {sorted(extra)}")
        for key, value in p.dims.items():
            if value not in REGISTRY[key].vocabulary:
                raise ValueError(f"metric {p.name} has disallowed value for {key}: {value!r}")


class Exporter(Protocol):
    def export(self, points: Sequence[MetricPoint]) -> object: ...
