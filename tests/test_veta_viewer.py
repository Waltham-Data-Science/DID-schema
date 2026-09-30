"""Tests for `tools/check_veta_viewer.py` -- the V_eta shape panel's input gate.

Every mutation test builds a miniature repository under tmp_path (the viewer's
real `sources.ts` and `grammar.json`, plus a tiny schema tree and the two
markdown inputs), breaks ONE thing, and asserts that the gate names it. A gate
that passed a broken fixture would look exactly like a gate whose inputs agree,
so each failure mode is pinned by a test that goes red without it.
"""

import importlib.util
import json
import os
import shutil

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location(
    "check_veta_viewer", os.path.join(REPO_ROOT, "tools", "check_veta_viewer.py"))
cv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cv)

CATEGORIES = ["①", "②", "③", "④", "⑤", "⑥", "⑦"]


def _class(name, supers=()):
    return {
        "document_class": {"class_name": name, "class_version": "1.0.0",
                           "superclasses": [{"class_name": s} for s in supers],
                           "maturity_level": "stable"},
        "depends_on": [], "file": [], "fields": [],
    }


def _final_set(per_category, excluded=()):
    lines = ["# V_eta -- The Final Class Set", ""]
    for sym, names in zip(CATEGORIES, per_category):
        lines += [f"## {sym} Category {sym} ({len(names)})",
                  ", ".join(f"`{n}`" for n in names), ""]
    lines += ["## NOT in the final set (by disposition)", ""]
    lines += [f"**retire ({len(excluded)}):**", ", ".join(f"`{n}`" for n in excluded)]
    return "\n".join(lines) + "\n"


def _tenets(ids=None):
    ids = ids or [f"T{i}" for i in range(1, 16)]
    body = ["# Tenets", "", "## Thesis", "", "text", "", "## The tenets", ""]
    for t in ids:
        body += [f"### {t} — Tenet {t}.", "body", ""]
    return "\n".join(body)


def make_repo(tmp_path, names=None, final_set=None, tenets=None):
    root = tmp_path
    veta = root / "web" / "src" / "veta"
    veta.mkdir(parents=True)
    for f in ("sources.ts", "grammar.json"):
        shutil.copy(os.path.join(REPO_ROOT, "web", "src", "veta", f), veta / f)
    names = names if names is not None else [f"class_{i}" for i in range(7)] + ["gone_one"]
    stable = root / "schemas" / "V_eta" / "stable"
    stable.mkdir(parents=True)
    for n in names:
        (stable / f"{n}.json").write_text(json.dumps(_class(n)))
    (root / "schemas" / "V_eta" / "index.json").write_text(json.dumps(
        {"schemas": [{"class_name": n, "path": f"schemas/V_eta/stable/{n}.json"}
                     for n in names]}))
    if final_set is None:
        final_set = _final_set([[f"class_{i}"] for i in range(7)], ["gone_one"])
    (root / "schemas" / "V_eta_final_class_set.md").write_text(final_set)
    (root / "schemas" / "V_eta_tenets.md").write_text(tenets or _tenets())
    return root


def test_the_real_repository_agrees():
    assert cv.check(REPO_ROOT) == []


def test_a_clean_fixture_passes(tmp_path):
    assert cv.check(str(make_repo(tmp_path))) == []


def test_a_class_in_no_category_fails(tmp_path):
    root = make_repo(tmp_path)
    (root / "schemas" / "V_eta" / "stable" / "orphan_class.json").write_text(
        json.dumps(_class("orphan_class")))
    fails = cv.check(str(root))
    assert any("orphan_class" in f and "in no category" in f for f in fails)


def test_a_category_naming_a_missing_class_fails(tmp_path):
    fs = _final_set([[f"class_{i}"] for i in range(6)] + [["class_6", "never_built"]],
                    ["gone_one"])
    fails = cv.check(str(make_repo(tmp_path, final_set=fs)))
    assert any("never_built" in f and "not in the tree" in f for f in fails)


def test_a_heading_count_that_disagrees_with_its_list_fails(tmp_path):
    fs = _final_set([[f"class_{i}"] for i in range(7)], ["gone_one"])
    fs = fs.replace("Category ③ (1)", "Category ③ (5)")
    fails = cv.check(str(make_repo(tmp_path, final_set=fs)))
    assert any("heading says 5, lists 1" in f for f in fails)


def test_a_class_named_twice_fails(tmp_path):
    fs = _final_set([[f"class_{i}"] for i in range(7)], ["gone_one", "class_0"])
    fails = cv.check(str(make_repo(tmp_path, final_set=fs)))
    assert any("class_0 is named twice" in f for f in fails)


def test_a_missing_category_fails(tmp_path):
    fs = _final_set([[f"class_{i}"] for i in range(7)], ["gone_one"])
    fs = fs.replace("## ⑦ Category ⑦ (1)", "## Category seven (1)")
    fails = cv.check(str(make_repo(tmp_path, final_set=fs)))
    assert any("categories parsed" in f for f in fails)


def test_a_missing_tenet_fails(tmp_path):
    ids = [f"T{i}" for i in range(1, 16) if i != 7]
    fails = cv.check(str(make_repo(tmp_path, tenets=_tenets(ids))))
    assert any("tenets parsed" in f for f in fails)


def test_the_glob_is_derived_from_sources_ts(tmp_path):
    root = make_repo(tmp_path)
    src = root / "web" / "src" / "veta" / "sources.ts"
    src.write_text(src.read_text().replace("V_eta/**/*.json", "V_zeta/**/*.json"))
    fails = cv.check(str(root))
    assert any("sources.ts globs" in f for f in fails)


def test_a_class_name_written_into_the_viewer_fails(tmp_path):
    root = make_repo(tmp_path)
    (root / "web" / "src" / "veta" / "Snapshot.tsx").write_text(
        'export const PINNED = ["class_3"];\n')
    fails = cv.check(str(root))
    assert any("class name written into the viewer" in f and "class_3" in f
               for f in fails)


def test_an_empty_tree_is_a_failure_not_a_clean_zero(tmp_path):
    fails = cv.check(str(make_repo(tmp_path, names=[],
                                   final_set=_final_set([[]] * 7))))
    assert "the glob matched no files" not in fails  # index.json still matches
    assert "no class files were found" in fails


def test_a_missing_sources_file_is_a_contract_error(tmp_path):
    root = make_repo(tmp_path)
    os.remove(root / "web" / "src" / "veta" / "sources.ts")
    assert cv.main(["--root", str(root)]) == 1
