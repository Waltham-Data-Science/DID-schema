"""#32 -- binding governance (T8): the CI gate for tools/check_binding_governance.py.

Two jobs, and the second exists because of a lesson this project has already
paid for twice:

  1. RATCHET the live tree. Every binding-governance count may fall freely and
     may not grow. This runs in the existing pytest job, so no workflow edit is
     needed for the gate to be real.

  2. DRIVE THE TOOL THROUGH A SYNTHETIC TREE with known defects. "A test written
     from the same premise as the code cannot catch the code" (CLAUDE.md) --
     asserting the tool's numbers against the very tree the numbers were read
     from proves only that the tool is deterministic. So each finding class is
     also exercised on a fixture built by hand, where the right answer is known
     independently of what the tool says.

None of these tests DECIDES anything. They assert that a fact stated twice
agrees with itself, and that no count silently grows. Which vocabulary a field
binds to, and whether the field or the registry is authoritative, are team calls
(operating rule 4).
"""

import copy
import importlib.util
import json
import os

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VETA = os.path.join(REPO_ROOT, "schemas", "V_eta")


def _load_tool(name):
    """Load tools/<name>.py by PATH -- `tools/` has no __init__.py."""
    path = os.path.join(REPO_ROOT, "tools", name + ".py")
    spec = importlib.util.spec_from_file_location("_bind_tool_" + name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


TOOL = _load_tool("check_binding_governance")
LIVE = TOOL.run(VETA)


# ---------------------------------------------------------------------------
# 1. the live tree
# ---------------------------------------------------------------------------

def test_the_sweep_actually_read_something():
    """DENOMINATOR FIRST (operating rule 5). `silentLoss` printed "0 empty
    edges" for two days while reading nothing; every count below would read as
    clean under the same failure."""
    d = LIVE["denominator"]
    assert d["schema_files"] > 100, d
    assert d["field_declarations"] > 500, d
    assert d["bound_fields"] > 0, (
        "zero bound fields -- the walker stopped descending, which is NOT a "
        "clean result")
    assert d["registry_rows_normative"] > 0, d


def test_no_binding_governance_count_has_grown():
    """The ratchet. Lower a baseline freely; raising one is a deliberate act
    that has to be written down in the tool with its reason."""
    assert TOOL.BASELINES, "no baselines -- this test would verify nothing"
    grown = {k: (LIVE["findings"][k]["count"], b)
             for k, b in TOOL.BASELINES.items()
             if LIVE["findings"][k]["count"] > b}
    assert not grown, (
        f"binding-governance counts grew: {grown}. Either fix the declaration, "
        "or raise the baseline in tools/check_binding_governance.py and say why.")


def test_strength_never_disagrees_between_field_and_registry():
    """The one INVARIANT the team has already decided (2026-08-10): strength is
    authoritative ON THE FIELD, and where the registry also states one the two
    must agree. Before this, three `dataset` facts were stored twice and agreed
    by coincidence.

    This is the tool's own path to the same conclusion that
    test_veta.py::test_field_and_registry_strengths_agree reaches by reading the
    files directly -- deliberately, so a bug in the tool's indexing cannot make
    the check silently vacuous.
    """
    f = LIVE["findings"]["B5_strength_stored_twice"]
    assert f["pairs_checked"] > 0, (
        "no field/registry strength pairs -- this check verified nothing")
    assert f["count"] == 0, f["detail"]


def test_every_finding_reports_a_denominator():
    """An instrument must say how many things it inspected (operating rule 5).
    A finding that reports only a count cannot distinguish "found nothing" from
    "looked at nothing"."""
    findings = LIVE["findings"]
    assert findings, "no findings block -- nothing to check"
    for key, f in findings.items():
        assert "count" in f, key
        others = set(f) - {"count"}
        assert others, f"{key} reports a count with no denominator or detail"


# ---------------------------------------------------------------------------
# 2. the synthetic tree -- each finding class proved on a fixture whose right
#    answer is known independently of the tool
# ---------------------------------------------------------------------------

def _minimal_class(name, fields):
    return {
        "document_class": {"class_name": name, "class_version": "1.0.0",
                           "superclasses": [], "maturity_level": "stable"},
        "depends_on": [], "file": [], "fields": fields,
    }


def _field(name, ftype, binding=None, sub=None):
    f = {"name": name, "type": ftype, "queryable": True, "constraints": {}}
    if binding is not None:
        f["constraints"]["binding"] = binding
    if sub is not None:
        f["fields"] = sub
    return f


@pytest.fixture
def synthetic(tmp_path):
    """A hand-built V_eta with EXACTLY ONE defect of each kind.

    Known answers, by construction:
      B1  one undeclared key use          (`invented_key` on alpha.a)
      B3  one disagreeing value_set       (`vs_x`: {p,q} vs {p,q,r})
      B4  one shape mismatch              (ontology_term field, bare strings)
      B5  one strength disagreement       (field preferred, registry required)
      B6  four uncatalogued bound fields  (5 bound, 1 catalogued)
      B8  one unregistered prefix         (`ZZZ:1` in a registry row)
    """
    root = tmp_path / "V_eta"
    for tier in ("stable", "draft", "deprecated"):
        (root / tier).mkdir(parents=True)

    meta = {"$defs": {"field_definition": {"properties": {"constraints": {
        "type": "object",
        "properties": {"binding": {"type": "object", "properties": {
            "keyed_by": {}, "expansion": {}, "strength": {}, "values": {},
            "vocabulary": {}, "term_set": {}, "root": {},
        }}},
    }}}}}
    (root / "stable" / "did_schema_meta.json").write_text(json.dumps(meta))

    (root / "stable" / "CURIE_lookups_meta.json").write_text(json.dumps(
        {"prefixes": {"uberon": {"uri_base": "x"}}}))

    registry = {
        "subject_statement_bindings": [
            {"variable": {"node": "", "name": "species"}, "class": "term_assertion",
             "ontology": "UBERON", "root_node": "UBERON:1"},
            {"variable": {"node": "", "name": "odd"}, "class": "term_assertion",
             "ontology": "ZZZ", "root_node": "ZZZ:1"},
        ],
        "binding_examples": [
            {"variable": {"node": "", "name": "body mass"}, "class": "mass_observation"},
        ],
        "relation_bindings": [],
        "entity_field_bindings": [
            {"class": "gamma", "field": "g", "vocabulary": "openMINDS",
             "term_set": "T", "strength": "required"},
        ],
        "controlled_vocabularies": {"openMINDS": {"version": None}},
    }
    (root / "stable" / "binding_registry_meta.json").write_text(json.dumps(registry))

    write = lambda n, d: (root / "stable" / (n + ".json")).write_text(json.dumps(d))  # noqa: E731
    write("alpha", _minimal_class("alpha", [
        _field("a", "ontology_term",
               {"strength": "required", "root": "vs_x", "invented_key": 1,
                "values": [{"node": "", "name": "p"}, {"node": "", "name": "q"}]}),
    ]))
    write("beta", _minimal_class("beta", [
        _field("b", "ontology_term",
               {"strength": "required", "root": "vs_x",
                "values": [{"node": "", "name": "p"}, {"node": "", "name": "q"},
                           {"node": "", "name": "r"}]}),
    ]))
    write("delta", _minimal_class("delta", [
        _field("d", "ontology_term",
               {"strength": "required", "root": "vs_y", "values": ["bare", "strings"]}),
    ]))
    write("gamma", _minimal_class("gamma", [
        _field("g", "ontology_term",
               {"strength": "preferred", "vocabulary": "openMINDS", "term_set": "T"}),
    ]))
    write("nested", _minimal_class("nested", [
        _field("outer", "structure", sub=[
            _field("inner", "ontology_term", {"strength": "preferred"}),
        ]),
    ]))
    return str(root)


def test_synthetic_inventory_finds_the_nested_field(synthetic):
    """A binding on a SUB-FIELD must be found. `relative_reference.value.clock`
    and `.value.relation` are two of the fourteen live bindings and both are
    nested one level down -- a walker that only read top-level fields would
    report 12 and look tidy."""
    r = TOOL.run(synthetic)
    names = {(i["class"], i["field"]) for i in r["inventory"]}
    assert ("nested", "outer.inner") in names, sorted(names)
    assert r["denominator"]["bound_fields"] == 5, r["inventory"]


def test_synthetic_b1_undeclared_key(synthetic):
    f = TOOL.run(synthetic)["findings"]["B1_undeclared_binding_keys"]
    assert f["count"] == 1, f
    assert f["distinct_keys"] == ["invented_key"], f


def test_synthetic_b3_value_set_disagreement(synthetic):
    f = TOOL.run(synthetic)["findings"]["B3_value_set_definitions_disagree"]
    assert f["sets_inspected"] == 2, f          # vs_x and vs_y
    assert f["count"] == 1 and "vs_x" in f["detail"], f


def test_synthetic_value_set_catalogue_is_derived_and_shows_drift(synthetic):
    """The catalogue is READ BACK from the inline declarations because no
    central catalogue of `root:`-named value_sets is stored anywhere. It is a
    report, not a source of truth -- and it is the only way to see that one name
    carries two different member lists."""
    cat = TOOL.run(synthetic)["value_set_catalogue"]
    assert set(cat) == {"vs_x", "vs_y", "T"}, cat
    assert cat["vs_x"]["n_definitions"] == 2, cat["vs_x"]
    assert len(cat["vs_x"]["carriers"]) == 2, cat["vs_x"]
    assert cat["T"]["n_definitions"] == 0, (
        "an openMINDS term_set names a library rather than enumerating it, so "
        "it contributes carriers but no inline definition")


def test_synthetic_b4_shape_mismatch(synthetic):
    f = TOOL.run(synthetic)["findings"]["B4_value_shape_vs_field_type"]
    assert f["count"] == 1, f
    assert f["detail"][0]["class"] == "delta", f


def test_synthetic_b5_strength_disagreement_is_caught(synthetic):
    """The registry says `required`, the field says `preferred`. Nothing in the
    repository compared them until 2026-08-10, and the three live pairs agreed
    by coincidence."""
    f = TOOL.run(synthetic)["findings"]["B5_strength_stored_twice"]
    assert f["pairs_checked"] == 1, f
    assert f["count"] == 1, f
    assert f["detail"][0]["field_strength"] == "preferred", f
    assert f["detail"][0]["registry_strength"] == "required", f


def test_synthetic_b6_uncatalogued(synthetic):
    f = TOOL.run(synthetic)["findings"]["B6_bound_fields_not_in_registry"]
    assert f["of_bound_fields"] == 5 and f["count"] == 4, f


def test_synthetic_b7_leaf_selection_gap(synthetic):
    """The jQuantityLeaf case. Both normative rows bind to `term_assertion`; the
    only dimensional row is illustrative. A strict registry lookup for a
    dimensional leaf therefore resolves NOTHING -- which is why DID-matlab
    shipped a keyword-table stand-in."""
    f = TOOL.run(synthetic)["findings"]["B7_d9_leaf_selection_gap"]
    assert f["normative_rows"] == 2, f
    assert f["normative_dimensional_rows"] == 0, f
    assert f["count"] == 1, f
    assert [e["variable"] for e in f["illustrative_dimensional_rows"]] == ["body mass"], f


def test_synthetic_b8_unregistered_prefix(synthetic):
    """The `time:` repair, generalised: a CURIE whose prefix expands to nothing
    is a binding that LOOKS governed and is not."""
    f = TOOL.run(synthetic)["findings"]["B8_unregistered_curie_prefixes"]
    assert "UBERON" in f["prefixes_seen"] and "ZZZ" in f["prefixes_seen"], f
    assert f["unregistered_case_insensitive"] == ["ZZZ"], f
    assert "UBERON" in f["unregistered_case_sensitive"], (
        "the registered prefix is lowercase `uberon` and the CURIE is `UBERON:` "
        "-- whether the lookup is case-sensitive is undecided, so BOTH readings "
        "must be reported")


def test_synthetic_b9_counts_what_a_validator_could_not_resolve(synthetic):
    f = TOOL.run(synthetic)["findings"]["B9_unenforceable_as_declared"]
    kinds = {e["class"] for e in f["detail"]}
    assert "gamma" in kinds, f     # openMINDS version is null
    assert "nested" in kinds, f    # strength-only, no admissible set
    assert f["count"] == 2, f


def test_tool_reports_failure_when_it_reads_nothing(tmp_path, synthetic):
    """A sweep over an empty tree must NOT look like a clean result. Removing
    every bound field leaves the walker with nothing to find, and the counts all
    go to zero -- the exact shape of the `silentLoss` failure."""
    import shutil
    empty = str(tmp_path / "empty" / "V_eta")
    shutil.copytree(synthetic, empty)
    for fn in os.listdir(os.path.join(empty, "stable")):
        p = os.path.join(empty, "stable", fn)
        d = json.load(open(p))
        if "document_class" not in d:
            continue
        stripped = copy.deepcopy(d)

        def drop(flds):
            for x in flds or []:
                x.get("constraints", {}).pop("binding", None)
                drop(x.get("fields"))
        drop(stripped["fields"])
        with open(p, "w") as fh:
            json.dump(stripped, fh)
    r = TOOL.run(empty)
    assert r["denominator"]["bound_fields"] == 0
    # Every FIELD-derived count collapses to zero and the ratchet is satisfied:
    # total failure and a clean sweep are indistinguishable from the counts
    # alone. That is the `silentLoss` failure, and the zero-denominator guard is
    # what separates them -- so assert the guard fires, not the counts.
    for key in ("B1_undeclared_binding_keys", "B3_value_set_definitions_disagree",
                "B4_value_shape_vs_field_type", "B6_bound_fields_not_in_registry",
                "B9_unenforceable_as_declared"):
        assert r["findings"][key]["count"] == 0, (key, r["findings"][key])
    # Only ONE ratchet still fires, and only because it cross-references the
    # registry rather than the fields: B5 notices that a catalogued field no
    # longer declares a binding. Five of the seven ratchets say nothing at all,
    # which is why the guard cannot be left to them.
    silent = [k for k, b in TOOL.BASELINES.items()
              if r["findings"][k]["count"] <= b]
    assert len(silent) >= 5, silent

    import subprocess
    import sys
    proc = subprocess.run(
        [sys.executable, os.path.join(REPO_ROOT, "tools",
                                      "check_binding_governance.py"),
         "--veta", empty, "--enforce"],
        capture_output=True, text=True)
    assert proc.returncode == 2, (proc.returncode, proc.stderr)
    assert "read nothing" in proc.stderr, proc.stderr
