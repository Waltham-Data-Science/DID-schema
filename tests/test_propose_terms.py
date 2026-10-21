"""tools/propose_terms.py: a batch of terms checked, and its registry rows printed."""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import check_term_registry as ctr
import propose_terms as pt

CURIES = {"prefixes": {
    "ncit": {"spelling": "NCIT", "synonyms": ["NCI"]},
    "empty": {"spelling": "EMPTY", "synonyms": []},
}}
REGISTRY = {"terms": [
    {"name": "Arithmetic Mean", "node": "NCIT:C53319", "definition": "d", "status": "decided",
     "decided": "J, 2026-10-19", "first_used_in": "Haley"},
    {"name": "body midpoint", "node": "", "definition": "d", "status": "staged",
     "decided": "J, 2026-10-19", "first_used_in": "Haley"},
]}
OWL = {"0000400": ("plate wiping", "Wiping a plate.")}
WHO = {"decided": "J, 2026-10-21", "first_used_in": "Smith"}


def run(*batch, owl=OWL, **kw):
    kw = {**WHO, **kw}
    return pt.classify(list(batch), REGISTRY, CURIES, owl, **kw)


def verdicts(*batch, **kw):
    return [v for v, _, _ in run(*batch, **kw)[0]]


def test_a_registered_term_adds_nothing():
    v, rows = run({"name": "Arithmetic Mean", "node": "NCIT:C53319"},
                  {"name": "body midpoint", "node": ""})
    assert [x[0] for x in v] == ["REGISTERED", "REGISTERED"] and rows == []


def test_a_registered_node_under_another_name_points_the_writer_at_the_registry():
    v, rows = run({"name": "mean", "node": "NCI:C53319"})
    assert v[0][0] == "USE REGISTRY" and '"Arithmetic Mean"' in v[0][2] and rows == []


def test_a_registered_name_with_another_node_fails():
    assert verdicts({"name": "arithmetic mean", "node": "NCIT:C1"}) == ["FAIL"]


def test_a_new_term_is_respelled_and_printed_in_registry_order():
    v, rows = run({"name": "Median", "node": "nci:C28007", "definition": "the middle"})
    assert v[0][0] == "ADD" and "respelled" in v[0][2]
    assert rows == [{"name": "Median", "node": "NCIT:C28007", "definition": "the middle",
                     "status": "decided", **WHO}]
    assert list(json.loads("[" + pt.render_rows(rows) + "]")[0]) == list(pt.KEYS)


def test_an_unknown_prefix_fails():
    assert verdicts({"name": "x", "node": "WBbt:0005739", "definition": "d"}) == ["FAIL"]


def test_an_empty_term_takes_its_label_and_definition_from_the_ontology():
    v, rows = run({"name": "plate wiping", "node": "EMPTY:0000400"})
    assert v[0][0] == "ADD" and rows[0]["definition"] == "Wiping a plate."
    assert verdicts({"name": "plate cleaning", "node": "EMPTY:0000400"}) == ["FAIL"]
    assert verdicts({"name": "plate wiping", "node": "EMPTY:0000400", "definition": "other"}) == ["FAIL"]
    assert verdicts({"name": "not minted", "node": "EMPTY:0000401", "definition": "d"}) == ["FAIL"]


def test_without_a_checkout_an_empty_term_needs_a_definition_and_says_unchecked():
    assert verdicts({"name": "plate wiping", "node": "EMPTY:0000400"}, owl=None) == ["FAIL"]
    v, _ = run({"name": "plate wiping", "node": "EMPTY:0000400", "definition": "d"}, owl=None)
    assert v[0][0] == "ADD" and "NOT CHECKED" in v[0][2]


def test_a_term_with_no_node_is_staged_only_with_a_definition():
    v, rows = run({"name": "wiping", "node": "", "definition": "d"})
    assert v[0][0] == "ADD" and rows[0]["status"] == "staged"
    assert verdicts({"name": "wiping", "node": ""}) == ["FAIL"]


def test_who_decided_and_where_first_used_are_required():
    assert verdicts({"name": "Median", "node": "NCIT:C28007", "definition": "d"},
                    decided="", first_used_in="") == ["FAIL"]


def test_two_rows_of_one_batch_for_one_node_fail_by_the_gates_own_rule():
    v, _ = run({"name": "Median", "node": "NCIT:C28007", "definition": "d"},
               {"name": "median value", "node": "NCIT:C28007", "definition": "d"})
    assert any(x[0] == "FAIL" and x[2].startswith("R1") for x in v)


def test_repeated_rows_from_the_writer_listing_are_read_once():
    v, rows = run({"name": "Median", "node": "NCIT:C28007", "definition": "d", "field": "a"},
                  {"name": "Median", "node": "NCIT:C28007", "definition": "d", "field": "b"})
    assert [x[0] for x in v] == ["ADD"] and len(rows) == 1


def test_a_tsv_batch_against_the_real_registry(tmp_path, capsys):
    reg = ctr._load(ctr.SOURCE)["terms"][0]
    batch = tmp_path / "batch.tsv"
    batch.write_text("name\tnode\tfield\n"
                     f"{reg['name']}\t{reg['node']}\tvariable\n"
                     "Zzz Test Quantity\tNCIT:C999999999\tvariable\n", encoding="utf-8")
    assert pt.main([str(batch), "--decided", "J, 2026-10-21", "--first-used-in", "T"]) == 0
    out = capsys.readouterr().out
    assert out.startswith("DENOMINATOR: 2 row(s)")
    assert "1 REGISTERED, 0 USE REGISTRY, 1 ADD, 0 FAIL" in out
    assert '"node": "NCIT:C999999999"' in out
