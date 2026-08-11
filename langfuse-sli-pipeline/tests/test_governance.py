"""Metric Governance Contract (MGC) enforcement.

These tests make the governance registry (governance.py) the single, *testable*
source of truth. They fail the build - rather than letting a cardinality or
privacy regression reach production - if:

  * the exporter allowlist or the config default known-team/route sets stop being
    DERIVED from the registry;
  * any dimension's vocabulary outgrows its declared ``cardinality_budget``;
  * ``estimated_max_series()`` stops equalling the product of the primary
    dimension vocabularies;
  * the primary grouping is redeclared outside governance.py.
"""

from __future__ import annotations

import gateway_sli.config as config_mod
from gateway_sli.config import DEFAULT_KNOWN_ROUTES, DEFAULT_KNOWN_TEAMS, Config
from gateway_sli.emit.base import ALLOWED_ATTRIBUTE_KEYS as EXPORT_ALLOWED
from gateway_sli.governance import (
    ALLOWED_ATTRIBUTE_KEYS,
    OTHER,
    PRIMARY_DIMENSIONS,
    REGISTRY,
    UNATTRIBUTED,
    estimated_max_series,
)


def test_export_allowlist_is_derived_from_registry():
    # The exporter's defense-in-depth allowlist must be exactly the set of
    # governed dimension names - no more, no less.
    assert EXPORT_ALLOWED == ALLOWED_ATTRIBUTE_KEYS
    assert ALLOWED_ATTRIBUTE_KEYS == frozenset(REGISTRY)


def test_config_known_sets_are_derived_from_registry():
    assert DEFAULT_KNOWN_TEAMS == REGISTRY["team"].vocabulary - {OTHER, UNATTRIBUTED}
    assert DEFAULT_KNOWN_ROUTES == REGISTRY["route"].vocabulary - {OTHER}
    # Config() must adopt those derived defaults verbatim.
    cfg = Config()
    assert cfg.known_teams == DEFAULT_KNOWN_TEAMS
    assert cfg.known_routes == DEFAULT_KNOWN_ROUTES


def test_every_vocabulary_fits_its_cardinality_budget():
    # cardinality_budget is an ENFORCED ceiling, not documentation: a vocabulary
    # may never exceed its budget. Onboarding enough new values to exceed it must
    # be a deliberate budget bump reviewed in the same PR.
    for name, dim in REGISTRY.items():
        assert len(dim.vocabulary) <= dim.cardinality_budget, (
            f"{name}: vocabulary size {len(dim.vocabulary)} exceeds "
            f"cardinality_budget {dim.cardinality_budget}"
        )


def test_estimated_max_series_matches_primary_vocabulary_product():
    expected = 1
    for name in PRIMARY_DIMENSIONS:
        expected *= len(REGISTRY[name].vocabulary)
    assert estimated_max_series() == expected
    assert estimated_max_series() > 0


def test_primary_grouping_has_single_source_of_truth():
    for name in PRIMARY_DIMENSIONS:
        assert name in REGISTRY, name
    # config.py must NOT redeclare its own copy of the primary grouping; if a
    # future edit re-adds one, it must at least match governance.py.
    shadow = getattr(config_mod, "PRIMARY_DIMENSIONS", None)
    assert shadow is None or tuple(shadow) == tuple(PRIMARY_DIMENSIONS)
