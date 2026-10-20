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
