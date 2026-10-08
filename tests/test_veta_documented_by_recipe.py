"""`documented_by` may start at a formulation (V_eta_study_plan.md).

A standard recipe (WormBook's S-Complete or LB) cites where it is written down.
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


def test_a_recipe_can_cite_its_source():
    with REGISTRY.open() as f:
        rows = _relation_rows(json.load(f))
    row = [r for r in rows if r["relation"]["name"] == "documented_by"]
    assert len(row) == 1
    assert row[0]["child_types"] == ["entity", "formulation"]
    # web_resource retired 2026-10-08 (PROPOSAL): a recipe cites a protocol or a publication
    assert row[0]["parent_types"] == ["protocol", "publication"]
