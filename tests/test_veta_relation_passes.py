"""Every relation declares what passes along it (did_v2_relation_inheritance_plan.md).

Tenet T17 reads what reaches a child from its parent off the relation's own
`passes` in binding_registry_meta.json, so a reader cannot disagree with the
schema and a new relation cannot be added without the choice being made.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REG = ROOT / "schemas" / "registry" / "binding_registry_meta.json"
BASE = ROOT / "schemas" / "did_v2" / "base.json"
PASSES = {"assertions", "distributive", "context", "nothing"}
# entity types are stored by their ontology label since 2026-10-22 (Jess Haley
# [vocabulary nodes] L2); culture has no node and keeps its name
PHYSICAL = ["organism", "culture", "tissue", "cell", "Group", "device", "material entity"]


def _rows():
    return json.loads(REG.read_text())["relation_bindings"]


def _row(node):
    # by node: the stored name is the ontology label (Jess Haley 2026-10-22
    # [vocabulary nodes] L1), and code matches relations by node
    return next(r for r in _rows() if r["relation"]["node"] == node)


def test_every_relation_declares_one_of_the_four_values():
    rows = _rows()
    assert rows, "no relation_bindings rows read"
    bad = [r["relation"]["name"] for r in rows if r.get("passes") not in PASSES]
    assert not bad, f"{len(bad)} of {len(rows)} row(s) without a valid `passes`: {bad}"


def test_the_inheriting_relations_are_the_ones_t17_names():
    by = {}
    for r in _rows():
        by.setdefault(r["passes"], set()).add(r["relation"]["node"])
    # aliquot_of and passage_of folded into sample_of, "derives from part of"
    # (Jess Haley 2026-10-22 [vocabulary nodes] K5). By node (L1): part_of,
    # sample_of, instance_of; member_of; contained_in.
    assert by["assertions"] == {"BFO:0000050", "ENVO:01003004", "EMPTY:0000382"}
    assert by["distributive"] == {"RO:0002350"}
    assert by["context"] == {"RO:0001025"}


def test_part_of_is_physical_and_records_use_included_in():
    part = _row("BFO:0000050")
    assert part["relation"]["name"] == "part of"
    assert part["child_types"] == PHYSICAL and part["parent_types"] == PHYSICAL
    inc = _row("schema:isPartOf")
    assert inc["relation"]["name"] == "isPartOf"
    assert inc["passes"] == "nothing"
    assert set(inc["child_types"]) == {"Session", "Study"}
    assert set(inc["parent_types"]) == {"Study", "Data Set"}


def test_session_id_is_an_edge_not_a_field():
    base = json.loads(BASE.read_text())
    assert "session_id" not in {f["name"] for f in base["fields"]}
    edge = next(d for d in base["depends_on"] if d["name"] == "session_id")
    assert edge["mustBeNonEmpty"] is True
    assert edge["must_refer_to_document_class"] == "entity"
