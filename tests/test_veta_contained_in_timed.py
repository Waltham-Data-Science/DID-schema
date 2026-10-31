"""`contained_in` is timed: a container holds its contents for a while.

did_v2_study_plan.md, "`contained_in` is timed". The Haley import gives every
contained_in edge a time window (a worm on each plate in turn), so the
registry must declare that the relation may carry a time_reference.
"""
import json
from pathlib import Path

REGISTRY = Path(__file__).resolve().parent.parent / "schemas/registry/binding_registry_meta.json"


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
    # by node: RO:0001025 located in since 2026-10-22, RO:0001018 is obsolete in
    # RO (Jess Haley [vocabulary nodes] K1); the stored name is its label (L1)
    row = [r for r in rows if r["relation"]["node"] == "RO:0001025"]
    assert len(row) == 1
    assert row[0]["relation"]["name"] == "located in"
    # physical entities only; records use included_in ([contained_in endpoints]);
    # entity types by their label (L2), culture has no node
    phys = ["organism", "culture", "tissue", "cell", "material entity", "device", "Group"]
    assert row[0]["child_types"] == phys and row[0]["parent_types"] == phys
    assert row[0]["timed"] is True
    assert row[0]["ordered"] is False
