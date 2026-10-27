"""`subject.type` and `distributive` (did_v2_study_plan.md, 2026-10-02).

`subject.type` is the coarse kind, as a field; the finer kind stays a
term_assertion. `distributive` says whether a statement or relation about a
group holds of each member.
"""
import json
from pathlib import Path

STABLE = Path(__file__).resolve().parent.parent / "schemas/did_v2/stable"


def _fields(cls):
    with (STABLE / f"{cls}.json").open() as f:
        return {x["name"]: x for x in json.load(f)["fields"]}


def test_subject_type_is_an_optional_bound_term_over_seven_values():
    """`subject.type` became `entity.type` 2026-10-08 (signed,
    did_v2_entity_composition_plan.md sec. 4): REQUIRED now, because it is what
    tells a worm from a dataset, and widened past the seven physical kinds,
    which it still begins with."""
    t = _fields("entity")["type"]
    assert t["type"] == "ontology_term"
    assert t["mustBeNonEmpty"] is True
    b = t["constraints"]["binding"]
    assert b["strength"] == "required"
    assert b["root"] == "did_entity_type"
    # stored by the ontology label of each node since 2026-10-22 (Jess Haley
    # [vocabulary nodes] L2, L3); culture has no node
    assert [(v["node"], v["name"]) for v in b["values"]][:7] == [
        ("COB:0000022", "organism"), ("", "culture"), ("UBERON:0000479", "tissue"),
        ("CL:0000000", "cell"), ("NCIT:C43359", "Group"), ("COB:0001300", "device"),
        ("BFO:0000040", "material entity")]
    # The two values the design turned on: no "cell population", no "population".
    assert "cell population" not in t["documentation"]


def test_subject_stays_a_bare_identity_otherwise():
    assert set(_fields("entity")) == {"type", "name", "local_identifier",
                                      "description", "global_identifier"}


def test_distributive_is_an_optional_boolean_on_statements_and_relations():
    for cls in ("statement", "directed_relation"):
        d = _fields(cls)["distributive"]
        assert d["type"] == "boolean"
        assert d["mustBeNonEmpty"] is False
        assert "each member" in d["documentation"].lower()
