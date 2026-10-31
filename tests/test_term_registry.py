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
    "wikidata": {"spelling": "wikidata", "synonyms": ["wd"]},
}}


def registry(*terms):
    return {"description": "test", "terms": list(terms)}


def term(name, node, status="decided", definition="d", obsolete=False, number_unit=False,
         equivalent=None, synonyms=None):
    return {"name": name, "node": node, "status": status, "definition": definition,
            "decided": "J, 2026-10-22", "first_used_in": "test", "obsolete": obsolete,
            "number_unit": number_unit, "equivalent": equivalent or [],
            "synonyms": [] if synonyms is None else synonyms}


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


def test_two_entries_for_one_name_fail_ignoring_spaces_underscores_and_hyphens():
    # [term names match ignoring spacing] (Jess Haley, 2026-10-29): DID-matlab
    # finds "path name" as Pathname, so the two cannot both be registered
    src = registry(term("Pathname", "NCIT:C47922"), term("path_name", "EMPTY:0000001"))
    assert any(f.startswith("R2") for f in run(src)[2])
    src = registry(term("Pathname", "NCIT:C47922"), term("path names", "EMPTY:0000001"))
    assert not any(f.startswith("R2") for f in run(src)[2])


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
    reg = ctr._load(os.path.join(ctr.ROOT, "schemas", "registry", "binding_registry_meta.json"))
    nodes = {r["variable"]["name"]: r["variable"]["node"]
             for r in reg["subject_statement_bindings"]}
    # named by the registered labels (Jess Haley 2026-10-22 [developmental stage])
    assert nodes["Species"] == "NCIT:C45293"
    assert nodes["Developmental Stage"] == "NCIT:C43531"


# Jess Haley, 2026-10-21 (binding variables): each decided row is named by its
# registered term's label and carries that term's node.
DECIDED_BINDING_VARIABLES = {
    "study design independent variable": "OBI:0000750",   # was `factors`
    "Gene Expression": "NCIT:C16608",                     # was `gene expression`
    "cell type": "EFO:0000324",
    "Equipment Type": "NCIT:C178920",                     # was `instrument type`
    "material type": "EMPTY:0000354",
    "culture type": "EMPTY:0000357",                     # Jess Haley, 2026-10-21
    "ethics jurisdiction": "EMPTY:0000359",               # replaces ethics assessment, 2026-10-21
    "experimental approach": "EMPTY:0000356",
    "Open or Controlled Data Access Indicator": "NCIT:C175887",  # was `accessibility`
}


def test_the_decided_binding_variables_carry_their_registered_term():
    reg = ctr._load(os.path.join(ctr.ROOT, "schemas", "registry", "binding_registry_meta.json"))
    nodes = {r["variable"]["name"]: r["variable"]["node"]
             for r in reg["subject_statement_bindings"]}
    for name, node in DECIDED_BINDING_VARIABLES.items():
        assert nodes.get(name) == node, (name, nodes.get(name))
    for old in ("factors", "design", "gene expression", "instrument type", "accessibility",
                "study design", "ethics assessment"):
        assert old not in nodes, old
    registered = {t["node"]: t["name"] for t in ctr._load(ctr.SOURCE)["terms"] if t.get("node")}
    for name, node in DECIDED_BINDING_VARIABLES.items():
        assert registered.get(node) == name, (node, registered.get(node))


def test_no_binding_variable_is_unregistered():
    terms = [t for t in ctr._load(ctr.SOURCE)["terms"]]
    built = ctr._load(os.path.join(ctr.ROOT, "schemas", "registry", "binding_registry_meta.json"))
    failures, report = ctr.check_bindings(terms, built)
    assert failures == []
    assert not [r for r in report if "NOT in the term registry" in r], report


# Jess Haley, 2026-10-21 (value sets): a binding row may carry a CLOSED list of
# value terms, each registered; an empty list is legal; Gene Expression is not
# term-valued.

def test_a_closed_value_list_must_hold_registered_terms():
    terms = [term("assay plate", "EMPTY:0000321"), term("Petri Dish", "NCIT:C96141")]
    ok = {"subject_statement_bindings": [
        {"variable": {"node": "EMPTY:0000354", "name": "material type"},
         "values": [{"node": "EMPTY:0000321", "name": "assay plate"},
                    {"node": "NCIT:C96141", "name": "Petri Dish"}]},
        {"variable": {"node": "EMPTY:9", "name": "empty for now"}, "values": []}]}
    failures, report, n = ctr.check_value_sets(terms, ok)
    assert failures == [] and n == 2
    assert any("closed list of 0 value(s)" in r for r in report)
    bad = {"subject_statement_bindings": [
        {"variable": {"node": "EMPTY:0000354", "name": "material type"},
         "values": [{"node": "EMPTY:0000999", "name": "made up"},
                    {"node": "NCIT:C96141", "name": "petri dish"}]}]}
    failures, _, _ = ctr.check_value_sets(terms, bad)
    assert len(failures) == 2 and all(f.startswith("R9") for f in failures)


def test_a_row_that_is_not_term_valued_is_not_a_gap():
    rows = {"subject_statement_bindings": [
        {"variable": {"node": "NCIT:C16608", "name": "Gene Expression"}, "term_valued": False}]}
    failures, report, _ = ctr.check_value_sets([], rows)
    assert failures == [] and report == ["R9   'Gene Expression': NOT TERM-VALUED (the value is data)"]


def test_the_decided_closed_value_lists():
    reg = ctr._load(os.path.join(ctr.ROOT, "schemas", "registry", "binding_registry_meta.json"))
    rows = {r["variable"]["name"]: r for r in reg["subject_statement_bindings"]}

    def nodes(name):
        return [v["node"] for v in rows[name]["values"]]

    assert nodes("material type") == ["EMPTY:0000321", "EMPTY:0000319", "EMPTY:0000320", "NCIT:C96141"]
    assert nodes("culture type") == ["EMPTY:0000325"]
    assert nodes("Open or Controlled Data Access Indicator") == ["NCIT:C183346", "NCIT:C183345"]
    # openMINDS (latest): 197 sovereignState + 9 supranationalBody; 40 experimentalApproach
    assert len(nodes("ethics jurisdiction")) == 206
    assert all(n.startswith("wikidata:Q") for n in nodes("ethics jurisdiction"))
    assert "wikidata:Q30" in nodes("ethics jurisdiction")       # United States
    ea = nodes("experimental approach")
    assert len(ea) == 40 and "ILX:0739413" in ea and "EDAM:topic_0202" in ea
    # openMINDS (latest) technique 227 and semanticDataType 4, by openMINDS's own
    # ids (Jess Haley 2026-10-26 [census terms] T2), except three technique names
    # the registry already held (R2): brightfield and fluorescence microscopy, video tracking
    tq = nodes("Technique")
    assert len(tq) == 227 and len(set(tq)) == 227
    assert sum(n.startswith("openminds:technique/") for n in tq) == 224
    assert {"NCIT:C19827", "NCIT:C16856", "EMPTY:0000301"} <= set(tq)
    assert nodes("Scientific Data Type") == [
        "openminds:semanticDataType/derivedData", "openminds:semanticDataType/experimentalData",
        "openminds:semanticDataType/rawData", "openminds:semanticDataType/simulatedData"]
    assert rows["Gene Expression"]["term_valued"] is False
    assert "study design" not in rows and "ethics assessment" not in rows
    # [equipment type is the device kind list] (Jess Haley, 2026-10-29): the
    # registered device kinds, n-trode's multielectrode array first; the 17th is
    # [stimulator is SNOMED CT Stimulator] (2026-10-30)
    eq = nodes("Equipment Type")
    assert len(eq) == 17 and eq[0] == "wikidata:Q1952355" and "SNOMEDCT:36645008" in eq
    failures, _, n = ctr.check_value_sets(ctr._load(ctr.SOURCE)["terms"], reg)
    assert failures == [] and n == 4 + 1 + 2 + 206 + 40 + 227 + 4 + 17


def test_every_row_has_one_shape():
    """R10: DID-matlab did2.schema.termIndex concatenates the rows, so a row with
    other keys than the rest breaks it (Jess Haley 2026-10-22 [vocabulary nodes]
    made rows carry `obsolete`)."""
    bad = term("Median", "NCIT:C28007")
    del bad["obsolete"]
    assert any(f.startswith("R10") for f in run(registry(bad))[2])


def test_an_obsolete_term_names_a_registered_term_to_consider():
    src = registry(term("onset time", "EMPTY:0000368"),
                   term("encounter onset time", "EMPTY:0000140",
                        obsolete={"consider": "EMPTY:0000368"}),
                   term("x", "EMPTY:0000001", obsolete={"consider": "EMPTY:0000999"}))
    fails = [f for f in run(src)[2] if f.startswith("R10")]
    assert len(fails) == 1 and "EMPTY:0000999" in fails[0], fails


def test_an_obsolete_term_matches_the_ontologys_obsolete_label():
    terms = [{"name": "encounter onset time", "node": "EMPTY:0000140", "definition": "d",
              "obsolete": {"consider": "EMPTY:0000368"}}]
    owl = {"0000140": ("obsolete encounter onset time", "d")}
    assert ctr.check_empty(terms, owl) == []
    terms[0]["obsolete"] = False
    assert ctr.check_empty(terms, owl) != []


def test_a_term_states_the_unit_of_its_number():
    """R12 (Jess Haley, 2026-10-26, V_eta_go_forward_class_audit.md [term-stated
    unit is generic]): when a term's definition states the unit its number takes,
    the registry row says so, as a registered unit term, and a migrator reads it
    there. First case: EMPTY:0000199, "(provided in hours)"."""
    hour = term("hour", "om:hour")
    ok = term("t", "EMPTY:0000199", number_unit={"node": "om:hour", "name": "hour"})
    assert run(registry(hour, ok))[2] == []
    bad = [term("u", "EMPTY:0000001", number_unit={"node": "om:minute", "name": "minute"}),
           term("v", "EMPTY:0000002", number_unit={"node": "om:hour", "name": "hours"}),
           term("w", "EMPTY:0000003", number_unit={"node": "NCIT:C28007", "name": "Median"}),
           term("x", "EMPTY:0000004", number_unit="hours"),
           term("Median", "NCIT:C28007")]
    fails = [f for f in run(registry(hour, *bad))[2] if f.startswith("R12")]
    assert len(fails) == 4, fails
    assert "not a registered term" in fails[0] and "registered as 'hour'" in fails[1]
    assert "not a unit term" in fails[2] and "not false or" in fails[3]


def test_the_live_registry_states_hours_for_grating_training():
    terms = ctr._load(ctr.SOURCE)["terms"]
    row = [t for t in terms if t["node"] == "EMPTY:0000199"]
    assert len(row) == 1 and row[0]["number_unit"] == {"node": "om:hour", "name": "hour"}
    assert "(provided in hours)" in row[0]["definition"]


def test_equivalents_are_curies_with_one_meaning_each():
    """R13 (Jess Haley, 2026-10-27, V_eta_go_forward_class_audit.md [term
    equivalents recorded]): `equivalent` lists the ids in other vocabularies that
    mean the same thing; each is a CURIE in a known prefix, written in its
    spelling, and no id stands for two registered meanings."""
    ok = term("Median", "NCIT:C28007", equivalent=["wikidata:Q226995"])
    assert run(registry(ok, term("mean", "NCIT:C53319")))[2] == []
    bad = [term("a", "NCIT:C1", equivalent=["XYZ:1"]),
           term("b", "NCIT:C2", equivalent=["wd:Q2"]),
           term("c", "NCIT:C3", equivalent=["NCIT:C3"]),
           term("d", "NCIT:C4", equivalent=["NCIT:C1"]),
           term("e", "NCIT:C5", equivalent=["wikidata:Q5", "wikidata:Q5"]),
           term("f", "NCIT:C6", equivalent=["wikidata:Q5"]),
           term("g", "NCIT:C7", equivalent="wikidata:Q7")]
    fails = [f for f in run(registry(*bad))[2] if f.startswith("R13")]
    assert len(fails) == 7, fails
    assert "does not know" in fails[0] and "is written wikidata:Q2" in fails[1]
    assert "own node" in fails[2] and 'registered as "a"' in fails[3]
    assert "listed twice" in fails[4] and 'equivalent of "e"' in fails[5]
    assert "not a list" in fails[6]


def test_every_live_row_has_an_equivalent_list():
    terms = ctr._load(ctr.SOURCE)["terms"]
    assert terms and all(isinstance(t.get("equivalent"), list) for t in terms)


def test_synonyms_are_spellings_of_one_term_each():
    """R14 (Jess Haley 2026-10-26, V_eta_go_forward_class_audit.md [spelling is
    notation]): the spellings a migrator maps to a term, each naming one term."""
    ok = registry(term("hertz", "om:hertz", synonyms=["Hz", "spikes/s"]),
                  term("dF/F", "EMPTY:0000397", synonyms=["dFF"]))
    assert [f for f in run(ok)[2] if f.startswith("R14")] == []
    bad = [term("a", "NCIT:C1", synonyms=["A"]),
           term("b", "NCIT:C2", synonyms=["c"]),
           term("c", "NCIT:C3", synonyms=["x", "X"]),
           term("d", "NCIT:C4", synonyms=["x"]),
           term("e", "NCIT:C5", synonyms="x"),
           term("f", "NCIT:C6", synonyms=[""])]
    fails = [f for f in run(registry(*bad))[2] if f.startswith("R14")]
    assert len(fails) == 6, fails
    assert "own name" in fails[0] and 'name of "c"' in fails[1]
    assert "listed twice" in fails[2] and 'synonym of "c"' in fails[3]
    assert "not a list" in fails[4] and "not a list" in fails[5]


def test_the_response_unit_spellings_are_recorded():
    """[spelling is notation] (3): DID-matlab jResponseVariable's spellings are
    the registered terms' synonyms (its match is trimmed and case-insensitive,
    with either delta spelled out)."""
    by_node = {t["node"]: t for t in ctr._load(ctr.SOURCE)["terms"]}
    assert all(isinstance(t.get("synonyms"), list) for t in by_node.values())

    def low(node):
        return {x.lower() for x in by_node[node]["synonyms"]}
    assert low("om:hertz") == {"hz", "spikes/s", "sp/s", "1/s", "spikes/sec",
                               "spikes per second"}
    assert low("EMPTY:0000397") == {"δf/f", "deltaf/f", "dff"}


def test_unit_bindings_name_registered_terms():
    """R15 ([allowed units are source units], Jess Haley, 2026-10-29): the shipped
    `unit_bindings` rows all resolve, and the rule can fail -- an unregistered
    unit, a renamed variable, a unit listed twice, a second row for one variable
    and an empty list are each reported."""
    terms = ctr._load(ctr.SOURCE)["terms"]
    reg = ctr._load(os.path.join(ctr.ROOT, "schemas", "registry", "binding_registry_meta.json"))
    failures, n_rows, n_units = ctr.check_unit_bindings(terms, reg)
    assert failures == [] and n_rows >= 2 and n_units >= n_rows
    sec = {"node": "om:second-Time", "name": "second"}
    bad = {"unit_bindings": [
        {"variable": {"node": "om:Time", "name": "time"},
         "source_units": [sec, sec, {"node": "om:fortnight", "name": "fortnight"}]},
        {"variable": {"node": "om:Time", "name": "Time"}, "source_units": []},
    ]}
    failures, _, _ = ctr.check_unit_bindings(terms, bad)
    text = "\n".join(failures)
    assert "listed twice" in text
    assert "om:fortnight is not in the term registry" in text
    assert "registered as 'time'" in text
    assert "has another row" in text
    assert "not a non-empty list" in text
