"""tools/validate_v_eta.py: the JSON under schemas/V_eta is the source (#128).

Each test plants ONE defect in a scratch copy of the tree and asserts the
validator names it. A rule that passes on the real tree and on every planted
defect is checking nothing, so the planted defects are the evidence that each
rule bites.
"""
import importlib.util
import io
import json
import os
import shutil
from contextlib import redirect_stdout

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VETA = os.path.join(REPO, "schemas", "V_eta")
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
    dst = tmp_path / "V_eta"
    shutil.copytree(VETA, dst)
    return dst


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
    src = tree / "stable" / "statement.json"
    d = json.loads(src.read_text())
    d["document_class"]["class_name"] = "subject_statement"
    (tree / "stable" / "subject_statement.json").write_text(V.dumps(d))
    rc, out = _run(tree)
    assert rc == 1 and "subject_statement is a retired class name" in out, out


def test_an_unresolved_superclass_is_refused(tree):
    _edit(tree / "stable" / "statement.json",
          lambda d: d["document_class"]["superclasses"].append(
              {"class_name": "no_such_class"}))
    rc, out = _run(tree)
    assert rc == 1 and "no_such_class" in out, out


def test_a_binding_on_a_non_term_field_is_refused(tree):
    def fn(d):
        f = next(x for x in d["fields"] if x["type"] == "char")
        f["constraints"] = {"binding": {"strength": "preferred"}}
    _edit(tree / "stable" / "base.json", fn)
    rc, out = _run(tree)
    assert rc == 1 and "is bound but typed 'char'" in out, out


def test_a_relation_without_passes_is_refused(tree):
    _edit(tree / "stable" / "binding_registry_meta.json",
          lambda d: d["relation_bindings"][0].pop("passes"))
    rc, out = _run(tree)
    assert rc == 1 and "passes None" in out, out


def test_a_numbered_edge_is_refused(tree):
    def fn(d):
        d["depends_on"][0]["name"] = "thing_id_#"
    _edit(tree / "stable" / "statement.json", fn)
    rc, out = _run(tree)
    assert rc == 1 and "is numbered (T15)" in out, out


def test_a_method_block_that_drifts_is_refused(tree):
    def fn(d):
        m = next(x for x in d["fields"] if x["name"] == "method")
        par = next(x for x in m["fields"] if x["name"] == "parameters")
        par["fields"] = [x for x in par["fields"] if x["name"] != "matrix"]
    _edit(tree / "stable" / "interaction.json", fn)
    rc, out = _run(tree)
    assert rc == 1 and "method block shapes" in out and "entry list shapes" in out, out


def test_a_new_class_needs_a_hand_written_disposition(tree):
    d = json.loads((tree / "stable" / "statement.json").read_text())
    d["document_class"]["class_name"] = "brand_new_class"
    d["document_class"]["superclasses"] = [{"class_name": "base"}]
    d["depends_on"] = []
    (tree / "draft" / "brand_new_class.json").write_text(V.dumps(d))
    rc, out = _run(tree)
    assert rc == 1 and "brand_new_class needs a `disposition`" in out, out


def test_stale_relation_values_are_reported_not_fixed_in_check_mode(tree):
    _edit(tree / "stable" / "binding_registry_meta.json",
          lambda d: d["relation_bindings"].append(dict(
              d["relation_bindings"][0],
              relation={"node": "", "name": "planted_relation"})))
    before = (tree / "stable" / "directed_relation.json").read_text()
    rc, out = _run(tree)
    assert rc == 1 and "STALE D3 relation binding values" in out, out
    assert (tree / "stable" / "directed_relation.json").read_text() == before


def test_a_hand_layout_is_refused(tree):
    p = tree / "stable" / "statement.json"
    p.write_text(json.dumps(json.loads(p.read_text()), indent=2) + "\n")
    rc, out = _run(tree)
    assert rc == 1 and "statement.json is not indent-4" in out, out


def test_a_closed_value_list_naming_an_unregistered_term_is_refused(tree):
    def plant(d):
        row = next(r for r in d["subject_statement_bindings"]
                   if r["variable"]["name"] == "material type")
        row["values"].append({"node": "EMPTY:0009999", "name": "a plate nobody registered"})
    _edit(tree / "stable" / "binding_registry_meta.json", plant)
    rc, out = _run(tree)
    assert rc == 1 and "EMPTY:0009999 is not in the term registry" in out, out


def test_an_empty_closed_value_list_is_legal(tree):
    def plant(d):
        row = next(r for r in d["subject_statement_bindings"]
                   if r["variable"]["name"] == "culture type")
        row["values"] = []
    _edit(tree / "stable" / "binding_registry_meta.json", plant)
    rc, out = _run(tree)
    assert "R15 closed value sets are registered terms" in out
    assert rc == 0 and "FAIL R15" not in out, out


def test_a_row_that_is_not_term_valued_names_no_set(tree):
    def plant(d):
        row = next(r for r in d["subject_statement_bindings"]
                   if r["variable"]["name"] == "Gene Expression")
        row["values"] = []
    _edit(tree / "stable" / "binding_registry_meta.json", plant)
    rc, out = _run(tree)
    assert rc == 1 and "is term_valued false but names an admissible set" in out, out
