"""tools/check_term_registry.py: one term per meaning (tenet T19)."""
import copy
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import check_term_registry as ctr

CURIES = {"prefixes": {
    "ncit": {"spelling": "NCIT", "synonyms": ["NCI"]},
    "empty": {"spelling": "EMPTY", "synonyms": []},
    "om": {"spelling": "om", "synonyms": []},
}}


def registry(*terms):
    return {"description": "test", "terms": list(terms)}


def term(name, node, status="decided", definition="d"):
    return {"name": name, "node": node, "status": status, "definition": definition}


def run(src):
    return ctr.check(src, copy.deepcopy(src), CURIES)


def test_a_clean_registry_passes():
    src = registry(term("Median", "NCIT:C28007"), term("body midpoint", "", "staged"))
    terms, staged, failures = run(src)
    assert (len(terms), staged, failures) == (2, 1, [])


def test_two_entries_for_one_node_fail_even_spelled_differently():
    src = registry(term("Median", "NCIT:C28007"), term("median value", "NCI:C28007"))
    failures = run(src)[2]
    assert any(f.startswith("R1") for f in failures)
    assert any("is written NCIT:C28007" in f for f in failures)


def test_two_entries_for_one_name_fail_ignoring_case():
    src = registry(term("Median", "NCIT:C28007"), term("median", "EMPTY:0000001"))
    assert any(f.startswith("R2") for f in run(src)[2])


def test_status_and_node_must_agree():
    src = registry(term("a", "", "decided"), term("b", "NCIT:C1", "staged"), term("c", "NCIT:C2", "maybe"))
    failures = [f[:2] for f in run(src)[2]]
    assert failures.count("R3") == 3


def test_an_unknown_prefix_fails():
    assert any(f.startswith("R4") for f in run(registry(term("x", "WBbt:0005739")))[2])


def test_a_minted_or_staged_term_needs_a_definition():
    src = registry(term("x", "EMPTY:0000001", definition=""), term("y", "", "staged", ""))
    assert [f[:2] for f in run(src)[2]] == ["R5", "R5"]


def test_the_built_copy_must_match_the_source():
    src = registry(term("Median", "NCIT:C28007"))
    built = registry(term("Median", "NCIT:C28007"), term("extra", "NCIT:C1"))
    assert any(f.startswith("R6") for f in ctr.check(src, built, CURIES)[2])
    assert any(f.startswith("R6") for f in ctr.check(src, None, CURIES)[2])


def test_the_real_registry_passes_and_is_built():
    src = ctr._load(ctr.SOURCE)
    built = ctr._load(ctr.BUILT)
    curies = ctr._load(ctr.CURIES)
    terms, _, failures = ctr.check(src, built, curies)
    assert failures == []
    assert len(terms) > 0


def test_an_empty_term_must_carry_the_ontologys_label_and_definition():
    terms = [{"name": "target seeding OD600", "node": "EMPTY:0000105",
              "definition": "planned", "status": "decided"}]
    assert ctr.check_empty(terms, {"0000105": ("target seeding OD600", "planned")}) == []
    bad = ctr.check_empty(terms, {"0000105": ("bacterial OD600", "planned, in units")})
    assert len(bad) == 2 and all(b.startswith("R7 EMPTY:0000105") for b in bad)
    assert ctr.check_empty(terms, {}) == [
        "R7 EMPTY:0000105 (target seeding OD600): not in empty-ontology"]


def test_a_binding_variable_the_registry_names_must_carry_its_node():
    terms = [term("Species", "NCIT:C45293")]
    stale = {"subject_statement_bindings": [{"variable": {"node": "", "name": "species"}}]}
    failures, _ = ctr.check_bindings(terms, stale)
    assert len(failures) == 1 and failures[0].startswith("R8")
    built = {"subject_statement_bindings": [
        {"variable": {"node": "NCIT:C45293", "name": "species"}},
        {"variable": {"node": "", "name": "cell type"}}]}
    failures, report = ctr.check_bindings(terms, built)
    assert failures == []
    assert any("'cell type': no node, NOT in the term registry" in r for r in report)


def test_the_built_bindings_take_their_nodes_from_the_registry():
    reg = ctr._load(os.path.join(ctr.ROOT, "schemas", "V_eta", "stable",
                                 "binding_registry_meta.json"))
    nodes = {r["variable"]["name"]: r["variable"]["node"]
             for r in reg["subject_statement_bindings"]}
    assert nodes["species"] == "NCIT:C45293"
    assert nodes["developmental stage"] == "NCIT:C43531"


# Jess Haley, 2026-10-21 (binding variables): each decided row is named by its
# registered term's label and carries that term's node.
DECIDED_BINDING_VARIABLES = {
    "study design independent variable": "OBI:0000750",   # was `factors`
    "study design": "OBI:0500000",                        # was `design`
    "Gene Expression": "NCIT:C16608",                     # was `gene expression`
    "cell type": "EFO:0000324",
    "Equipment Type": "NCIT:C178920",                     # was `instrument type`
    "material type": "EMPTY:0000354",
    "ethics assessment": "EMPTY:0000355",
    "experimental approach": "EMPTY:0000356",
    "Open or Controlled Data Access Indicator": "NCIT:C175887",  # was `accessibility`
}


def test_the_decided_binding_variables_carry_their_registered_term():
    reg = ctr._load(os.path.join(ctr.ROOT, "schemas", "V_eta", "stable",
                                 "binding_registry_meta.json"))
    nodes = {r["variable"]["name"]: r["variable"]["node"]
             for r in reg["subject_statement_bindings"]}
    for name, node in DECIDED_BINDING_VARIABLES.items():
        assert nodes.get(name) == node, (name, nodes.get(name))
    for old in ("factors", "design", "gene expression", "instrument type", "accessibility"):
        assert old not in nodes, old
    registered = {t["node"]: t["name"] for t in ctr._load(ctr.SOURCE)["terms"] if t.get("node")}
    for name, node in DECIDED_BINDING_VARIABLES.items():
        assert registered.get(node) == name, (node, registered.get(node))


def test_no_binding_variable_is_unregistered():
    terms = [t for t in ctr._load(ctr.SOURCE)["terms"]]
    built = ctr._load(os.path.join(ctr.ROOT, "schemas", "V_eta", "stable",
                                   "binding_registry_meta.json"))
    failures, report = ctr.check_bindings(terms, built)
    assert failures == []
    assert not [r for r in report if "NOT in the term registry" in r], report
