"""`subject.type` and `distributive` (V_eta_study_plan.md, 2026-10-02).

`subject.type` is the coarse kind, as a field; the finer kind stays a
term_assertion. `distributive` says whether a statement or relation about a
group holds of each member.
"""
import json
from pathlib import Path

STABLE = Path(__file__).resolve().parent.parent / "schemas/V_eta/stable"


def _fields(cls):
    with (STABLE / f"{cls}.json").open() as f:
        return {x["name"]: x for x in json.load(f)["fields"]}


def test_subject_type_is_an_optional_bound_term_over_seven_values():
    t = _fields("subject")["type"]
    assert t["type"] == "ontology_term"
    assert t["mustBeNonEmpty"] is False
    b = t["constraints"]["binding"]
    assert b["strength"] == "required"
    assert b["root"] == "did_subject_type"
    assert [v["name"] for v in b["values"]] == [
        "organism", "culture", "tissue", "cell", "group", "device", "material"]
    # The two values the design turned on: no "cell population", no "population".
    assert "cell population" not in t["documentation"]


def test_subject_stays_a_bare_identity_otherwise():
    assert set(_fields("subject")) == {"local_identifier", "description", "name",
                                       "type"}


def test_distributive_is_an_optional_boolean_on_statements_and_relations():
    for cls in ("statement", "directed_relation"):
        d = _fields(cls)["distributive"]
        assert d["type"] == "boolean"
        assert d["mustBeNonEmpty"] is False
        assert "each member" in d["documentation"].lower()
