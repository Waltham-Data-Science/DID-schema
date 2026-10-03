"""`formulation.value.type` (V_eta_study_plan.md): what kind of mixture a recipe is."""
import json
from pathlib import Path

STABLE = Path(__file__).resolve().parent.parent / "schemas/V_eta/stable"


def test_a_formulation_can_say_what_kind_of_mixture_it_is():
    with (STABLE / "formulation.json").open() as f:
        d = json.load(f)
    assert [x["name"] for x in d["fields"]] == ["value"], "one payload field (T14)"
    sub = {x["name"]: x for x in d["fields"][0]["fields"]}
    t = sub["type"]
    assert t["type"] == "ontology_term"
    assert t["mustBeNonEmpty"] is False
    assert t["constraints"] == {"binding": {"strength": "preferred", "node_form": "curie"}}
