"""Every relation declares what passes along it (V_eta_relation_inheritance_plan.md).

Tenet T17 reads what reaches a child from its parent off the relation's own
`passes` in binding_registry_meta.json, so a reader cannot disagree with the
schema and a new relation cannot be added without the choice being made.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REG = ROOT / "schemas" / "V_eta" / "stable" / "binding_registry_meta.json"
BASE = ROOT / "schemas" / "V_eta" / "stable" / "base.json"
PASSES = {"assertions", "distributive", "context", "nothing"}
PHYSICAL = ["organism", "culture", "tissue", "cell", "group", "device", "material"]


def _rows():
    return json.loads(REG.read_text())["relation_bindings"]


def _row(name):
    return next(r for r in _rows() if r["relation"]["name"] == name)


def test_every_relation_declares_one_of_the_four_values():
    rows = _rows()
    assert rows, "no relation_bindings rows read"
    bad = [r["relation"]["name"] for r in rows if r.get("passes") not in PASSES]
    assert not bad, f"{len(bad)} of {len(rows)} row(s) without a valid `passes`: {bad}"


def test_the_inheriting_relations_are_the_ones_t17_names():
    by = {}
    for r in _rows():
        by.setdefault(r["passes"], set()).add(r["relation"]["name"])
    # aliquot_of and passage_of folded into sample_of, "derives from part of"
    # (Jess Haley 2026-10-22 [vocabulary nodes] K5)
    assert by["assertions"] == {"part_of", "sample_of", "instance_of"}
    assert by["distributive"] == {"member_of"}
    assert by["context"] == {"contained_in"}


def test_part_of_is_physical_and_records_use_included_in():
    part = _row("part_of")
    assert part["child_types"] == PHYSICAL and part["parent_types"] == PHYSICAL
    inc = _row("included_in")
    assert inc["relation"]["node"] == "schema:isPartOf"
    assert inc["passes"] == "nothing"
    assert set(inc["child_types"]) == {"session", "study"}
    assert set(inc["parent_types"]) == {"study", "dataset"}


def test_session_id_is_an_edge_not_a_field():
    base = json.loads(BASE.read_text())
    assert "session_id" not in {f["name"] for f in base["fields"]}
    edge = next(d for d in base["depends_on"] if d["name"] == "session_id")
    assert edge["mustBeNonEmpty"] is True
    assert edge["must_refer_to_document_class"] == "entity"
