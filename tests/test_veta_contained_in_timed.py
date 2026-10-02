"""`contained_in` is timed: a container holds its contents for a while.

V_eta_study_plan.md, "`contained_in` is timed". The Haley import gives every
contained_in edge a time window (a worm on each plate in turn), so the
registry must declare that the relation may carry a time_reference.
"""
import json
from pathlib import Path

REGISTRY = Path(__file__).resolve().parent.parent / "schemas/V_eta/stable/binding_registry_meta.json"


def _relation_rows(node):
    if isinstance(node, dict):
        if isinstance(node.get("relation_bindings"), list):
            return node["relation_bindings"]
        for v in node.values():
            rows = _relation_rows(v)
            if rows:
                return rows
    if isinstance(node, list):
        for v in node:
            rows = _relation_rows(v)
            if rows:
                return rows
    return None


def test_contained_in_may_carry_a_time_reference():
    with REGISTRY.open() as f:
        rows = _relation_rows(json.load(f))
    row = [r for r in rows if r["relation"]["name"] == "contained_in"]
    assert len(row) == 1
    assert row[0]["relation"]["node"] == "RO:0001018"
    assert row[0]["timed"] is True
    assert row[0]["ordered"] is False
