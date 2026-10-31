"""tools/validate_v_eta.py: the JSON under schemas/did_v2 is the source (#128).

Each test plants ONE defect in a scratch copy of the tree and asserts the
validator names it. A rule that passes on the real tree and on every planted
defect is checking nothing, so the planted defects are the evidence that each
rule bites.
"""
import importlib.util
import io
import json
import math
import os
import shutil
from contextlib import redirect_stdout

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VETA = os.path.join(REPO, "schemas", "did_v2")
_spec = importlib.util.spec_from_file_location(
    "_validate_v_eta", os.path.join(REPO, "tools", "validate_v_eta.py"))
V = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V)


def _run(veta):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = V.main(["--check", "--quiet-stamp", "--veta", str(veta)])
    return rc, buf.getvalue()


@pytest.fixture
def tree(tmp_path):
    """A scratch copy of the whole schemas/ tree; returns its did_v2 folder.
    The registers sit beside it in registry/ and generated/."""
    dst = tmp_path / "schemas"
    shutil.copytree(os.path.dirname(VETA), dst)
    return dst / "did_v2"


def _f(tree, name):
    """A file of the scratch tree by basename: a class file at any depth under
    did_v2/, or a register in registry/ or generated/."""
    for sub in ("registry", "generated"):
        if (tree.parent / sub / name).exists():
            return tree.parent / sub / name
    hits = sorted(tree.rglob(name))
    assert len(hits) == 1, (name, hits)
    return hits[0]


def _edit(path, fn):
    with open(path) as f:
        d = json.load(f)
    fn(d)
    with open(path, "w") as f:
        f.write(V.dumps(d))


def test_the_tree_in_the_repository_validates():
    rc, out = _run(VETA)
    assert out.startswith("DENOMINATOR: "), out[:200]
    assert rc == 0, out


def test_a_retired_class_name_is_refused(tree):
    src = _f(tree, "statement.json")
    d = json.loads(src.read_text())
    d["document_class"]["class_name"] = "subject_statement"
    (tree / "subject_statement.json").write_text(V.dumps(d))
    rc, out = _run(tree)
    assert rc == 1 and "subject_statement is a retired class name" in out, out


def test_an_unresolved_superclass_is_refused(tree):
    _edit(_f(tree, "statement.json"),
          lambda d: d["document_class"]["superclasses"].append(
              {"class_name": "no_such_class"}))
    rc, out = _run(tree)
    assert rc == 1 and "no_such_class" in out, out


def test_a_binding_on_a_non_term_field_is_refused(tree):
    def fn(d):
        f = next(x for x in d["fields"] if x["type"] == "char")
        f["constraints"] = {"binding": {"strength": "preferred"}}
    _edit(_f(tree, "base.json"), fn)
    rc, out = _run(tree)
    assert rc == 1 and "is bound but typed 'char'" in out, out


def test_a_relation_without_passes_is_refused(tree):
    _edit(_f(tree, "binding_registry_meta.json"),
          lambda d: d["relation_bindings"][0].pop("passes"))
    rc, out = _run(tree)
    assert rc == 1 and "passes None" in out, out


def test_a_numbered_edge_is_refused(tree):
    def fn(d):
        d["depends_on"][0]["name"] = "thing_id_#"
    _edit(_f(tree, "statement.json"), fn)
    rc, out = _run(tree)
    assert rc == 1 and "is numbered (T15)" in out, out


def test_a_method_block_that_drifts_is_refused(tree):
    def fn(d):
        m = next(x for x in d["fields"] if x["name"] == "method")
        par = next(x for x in m["fields"] if x["name"] == "parameters")
        par["fields"] = [x for x in par["fields"] if x["name"] != "matrix"]
    _edit(_f(tree, "interaction.json"), fn)
    rc, out = _run(tree)
    assert rc == 1 and "method block shapes" in out and "entry list shapes" in out, out


def test_a_new_class_needs_a_hand_written_disposition(tree):
    d = json.loads((_f(tree, "statement.json")).read_text())
    d["document_class"]["class_name"] = "brand_new_class"
    d["document_class"]["superclasses"] = [{"class_name": "base"}]
    d["depends_on"] = []
    (tree / "brand_new_class.json").write_text(V.dumps(d))
    rc, out = _run(tree)
    assert rc == 1 and "brand_new_class needs a `disposition`" in out, out


def test_stale_relation_values_are_reported_not_fixed_in_check_mode(tree):
    _edit(_f(tree, "binding_registry_meta.json"),
          lambda d: d["relation_bindings"].append(dict(
              d["relation_bindings"][0],
              relation={"node": "", "name": "planted_relation"})))
    before = (_f(tree, "directed_relation.json")).read_text()
    rc, out = _run(tree)
    assert rc == 1 and "STALE D3 relation binding values" in out, out
    assert (_f(tree, "directed_relation.json")).read_text() == before


def test_the_tree_holds_each_family_root_in_its_folder():
    """[family roots and relation folder] (Jess Haley, 2026-10-31): each
    family's root class lives in its family folder, as time_reference does."""
    assert len(V.SP.ROOTED_FAMILIES) >= 5   # denominator
    for fam in V.SP.ROOTED_FAMILIES:
        p = V.SP.class_path(fam)
        assert p is not None, fam
        assert V.SP.family(p) == fam, (fam, p)
    for name in ("directed_relation", "undirected_relation"):
        assert V.SP.family(V.SP.class_path(name)) == "relation", name


def test_the_acquisition_classes_are_in_acquisition():
    """[acquisition folder] (Jess Haley, 2026-10-31)."""
    names = ("acquisition_system", "acquisition_channels", "acquisition_reader",
             "epoch_file_pattern", "epoch_parameter_reader", "ingestion_manifest")
    for name in names:
        assert V.SP.family(V.SP.class_path(name)) == "acquisition", name


def test_the_clock_alignment_classes_are_in_time_reference():
    """[clock alignment in time_reference] (Jess Haley, 2026-10-31)."""
    for name in ("clock_alignment", "clock_alignment_configuration", "clock_alignment_policy"):
        assert V.SP.family(V.SP.class_path(name)) == "time_reference", name


@pytest.mark.parametrize("fam", ["value", "relation", "data_body"])
def test_a_family_root_outside_its_folder_is_refused(tree, fam):
    src = _f(tree, fam + ".json")
    shutil.move(str(src), str(tree / (fam + ".json")))
    rc, out = _run(tree)
    assert rc == 1 and f"family root {fam} is in schemas/did_v2/{fam}.json" in out, out


def test_a_hand_layout_is_refused(tree):
    p = _f(tree, "statement.json")
    p.write_text(json.dumps(json.loads(p.read_text()), indent=2) + "\n")
    rc, out = _run(tree)
    assert rc == 1 and "statement.json is not indent-4" in out, out


def test_a_closed_value_list_naming_an_unregistered_term_is_refused(tree):
    def plant(d):
        row = next(r for r in d["subject_statement_bindings"]
                   if r["variable"]["name"] == "material type")
        row["values"].append({"node": "EMPTY:0009999", "name": "a plate nobody registered"})
    _edit(_f(tree, "binding_registry_meta.json"), plant)
    rc, out = _run(tree)
    assert rc == 1 and "EMPTY:0009999 is not in the term registry" in out, out


def test_an_empty_closed_value_list_is_legal(tree):
    def plant(d):
        row = next(r for r in d["subject_statement_bindings"]
                   if r["variable"]["name"] == "culture type")
        row["values"] = []
    _edit(_f(tree, "binding_registry_meta.json"), plant)
    rc, out = _run(tree)
    assert "R15 closed value sets are registered terms" in out
    assert rc == 0 and "FAIL R15" not in out, out


def test_a_row_that_is_not_term_valued_names_no_set(tree):
    def plant(d):
        row = next(r for r in d["subject_statement_bindings"]
                   if r["variable"]["name"] == "Gene Expression")
        row["values"] = []
    _edit(_f(tree, "binding_registry_meta.json"), plant)
    rc, out = _run(tree)
    assert rc == 1 and "is term_valued false but names an admissible set" in out, out


# ------------------------------------------- rule value_inline_or_body (R16)
# data_body AMENDMENT 5 (Jess Haley, 2026-10-21, signed): a value is inline
# (`value` filled) or in data bodies (`data_body: true`), never neither; by its
# clarification a statement may instead name a shared value document through
# `value_id`. One rule on `value` replaces the per-class required `value` of
# the nine classes that set it.

NINE = ("term", "date", "logical", "polynomial", "model_fit", "tuning_curve",
        "contrast_sensitivity", "harmonic_component", "receptive_field")


def _value_field(name):
    for dirpath, _dirs, files in os.walk(VETA):
        if name + ".json" in files:
            with open(os.path.join(dirpath, name + ".json")) as f:
                d = json.load(f)
            return next(x for x in d["fields"] if x["name"] == "value")
    raise AssertionError(name)


def test_value_declares_the_rule_and_the_nine_no_longer_require_value():
    with open(V.SP.class_path("value")) as f:
        rules = {r["name"]: r for r in json.load(f)["rules"]}
    assert set(rules["value_inline_or_body"]["fields"]) == {"value", "data_body", "value_id"}
    assert "data_type_when_bytes" in rules
    for name in NINE:
        assert _value_field(name)["mustBeNonEmpty"] is False, name


def test_a_document_with_neither_inline_value_nor_data_body_is_refused():
    for doc in ({}, {"value": {}, "data_body": False}, {"value": [], "data_body": False},
                {"value": {"node": "", "name": ""}}):
        assert V.value_inline_or_body(doc), doc


def test_a_receptive_field_in_bodies_with_no_inline_value_passes():
    # receptive_field.value declares no sub-fields: it can only be body-backed
    assert not _value_field("receptive_field").get("fields")
    doc = {"document_class": {"class_name": "receptive_field"},
           "value": {}, "data_body": True}
    assert V.value_inline_or_body(doc) == []


def test_a_term_with_no_inline_value_and_no_data_body_is_refused():
    doc = {"document_class": {"class_name": "term"},
           "value": {"node": "", "name": ""}}
    out = V.value_inline_or_body(doc)
    assert out and "value_inline_or_body" in out[0], out
    # and the inline-filled term passes, as does a false boolean (a value, not a blank)
    assert V.value_inline_or_body(dict(doc, value={"node": "NCBITaxon:10090",
                                                   "name": "Mus musculus"})) == []
    assert V.value_inline_or_body({"value": [False]}) == []


def test_an_unrecorded_amount_written_as_nan_counts_as_stated():
    # Jess Haley, 2026-10-21 (did_v2_go_forward_class_audit.md): an unrecorded
    # amount is written as NaN in its quantity, e.g. a dose's volume.liters.
    # NaN is a number, not a blank, so the value is stated. The text V2 writes
    # (the literal NaN, as V1 writes it) parses here to float('nan').
    doc = json.loads('{"document_class": {"class_name": "dose"}, '
                     '"value": {"volume": {"liters": NaN, '
                     '"source_unit": {"node": "", "name": ""}}}}')
    assert math.isnan(doc["value"]["volume"]["liters"])
    assert V.value_inline_or_body(doc) == []
    # the same document with the amount written as null (plain jsonencode)
    # would be refused: that is why V2 must keep the literal
    lost = json.loads(json.dumps(doc).replace("NaN", "null"))
    assert V.value_inline_or_body(lost)


def test_a_required_inline_value_is_refused(tree):
    def fn(d):
        next(x for x in d["fields"] if x["name"] == "value")["mustBeNonEmpty"] = True
    _edit(_f(tree, "term.json"), fn)
    rc, out = _run(tree)
    assert rc == 1 and "term.value is mustBeNonEmpty" in out, out


def test_the_rule_missing_from_value_is_refused(tree):
    _edit(_f(tree, "value.json"),
          lambda d: d.__setitem__("rules", [r for r in d["rules"]
                                            if r["name"] != "value_inline_or_body"]))
    rc, out = _run(tree)
    assert rc == 1 and "value declares no rule 'value_inline_or_body'" in out, out


def test_a_statement_with_a_shared_value_document_passes():
    doc = {"document_class": {"class_name": "voltage_observation"}, "value": {},
           "depends_on": [{"name": "value_id", "document_id": "4126f0b8c2a1d3e5_c0ffee"}]}
    assert V.value_inline_or_body(doc) == []
    # an EMPTY value_id edge is no value at all
    doc["depends_on"][0]["document_id"] = ""
    assert V.value_inline_or_body(doc)
    # the v1-shaped edge {name, value} reads the same
    assert V.value_inline_or_body({"depends_on": [{"name": "value_id", "value": "x"}]}) == []


def test_data_type_is_required_only_for_plain_array_bytes():
    """Jess Haley, 2026-10-21: `data_type` only when the bytes are a plain
    array (a sampled_body, or an untyped inline array); an opaque_body's
    `format` term is the encoding, so it needs none."""
    with open(V.SP.class_path("value")) as f:
        rules = {r["name"]: r for r in json.load(f)["rules"]}
    st = rules["data_type_when_bytes"]["statement"]
    assert "sampled_body" in st and "opaque_body" in st and "`format`" in st
    assert "`data_body` true, or" not in st


# [schema folders by family] (Jess Haley, 2026-10-30): schemas/did_v2/ holds
# class files only, in the decided family folders; a retire class lives in
# retiring/; no basename repeats under schemas/ (the siblings read every
# non-class file by its basename).

def test_a_retire_class_outside_retiring_is_refused(tree):
    src = _f(tree, "app.json")
    src.rename(tree / "app.json")
    rc, out = _run(tree)
    assert rc == 1 and "app: disposition 'retire' but its file is in" in out, out


def test_a_persist_class_in_retiring_is_refused(tree):
    src = _f(tree, "statement.json")
    src.rename(tree / "retiring" / "statement.json")
    rc, out = _run(tree)
    assert rc == 1 and "statement: disposition 'persist' but its file is in" in out, out


def test_a_folder_that_is_not_a_family_is_refused(tree):
    (tree / "stable").mkdir()
    _f(tree, "statement.json").rename(tree / "stable" / "statement.json")
    rc, out = _run(tree)
    assert rc == 1 and "unexpected directory schemas/did_v2/stable/" in out, out


def test_a_registry_inside_the_class_folder_is_refused(tree):
    (tree / "notes.md").write_text("not a class\n")
    rc, out = _run(tree)
    assert rc == 1 and "schemas/did_v2/notes.md is not a class file" in out, out


def test_a_repeated_basename_under_schemas_is_refused(tree):
    (tree.parent / "registry" / "statement.json").write_text(
        _f(tree, "statement.json").read_text())
    rc, out = _run(tree)
    assert rc == 1 and "statement.json is held by 2 files under schemas/" in out, out


def test_a_class_needs_a_disposition_row(tree):
    p = tree.parent / "registry" / "did_v2_class_dispositions.json"
    d = json.loads(p.read_text())
    del d["classes"]["statement"]
    p.write_text(json.dumps(d, indent=4, ensure_ascii=False) + "\n")
    rc, out = _run(tree)
    assert rc == 1 and "statement needs a `disposition`" in out, out


def test_in_progress_is_refused():
    """[one folder, final classes only] (Jess Haley, 2026-10-29): "No draft or in
    progress". The registry holds persist and retire only, and the validator
    refuses an `in_progress` row."""
    d = json.loads(open(V.SP.CLASS_DISPOSITIONS).read())
    counts = {}
    for row in d["classes"].values():
        counts[row["disposition"]] = counts.get(row["disposition"], 0) + 1
    assert sum(counts.values()) > 100, counts   # denominator
    assert set(counts) <= {"persist", "retire"}, counts
    assert "in_progress" not in V.DISPOSITIONS


def test_an_in_progress_row_fails(tree):
    p = tree.parent / "registry" / "did_v2_class_dispositions.json"
    d = json.loads(p.read_text())
    d["classes"]["statement"]["disposition"] = "in_progress"
    p.write_text(json.dumps(d, indent=4, ensure_ascii=False) + "\n")
    rc, out = _run(tree)
    assert rc == 1 and "statement needs a `disposition`" in out, out
