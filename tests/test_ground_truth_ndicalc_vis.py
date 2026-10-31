"""`tools/ndi_ground_truth.py` reads the NDIcalc-vis-matlab templates at the
LOCKED commit ([ground truth reads NDIcalc-vis templates], Jess Haley,
2026-10-27, did_v2_go_forward_class_audit.md), so a changed tuning template
shows up as a diff in `schemas/generated/did_v2_ndi_ground_truth.json`.

These tests build a throwaway repository, lock it at one commit, then commit a
changed template and a working-tree edit after it:

  test_reads_the_locked_commit_not_later_ones_or_the_worktree
        the record is the locked commit's template; neither the later commit
        nor the uncommitted edit leaks in.

  test_a_changed_template_changes_the_record
        locking the later commit changes the record: the property the decision
        asks for.

  test_counts_what_it_skips
        an unparseable file and a non-document JSON are counted in the scan,
        not silently dropped (rule 5).
"""

import json
import os
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))

import ndi_ground_truth as GT  # noqa: E402  (needs the sys.path line above)


def _git(repo, *args):
    env = dict(os.environ)
    env.update({
        "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.com",
    })
    return subprocess.run(["git", "-C", str(repo)] + list(args),
                          capture_output=True, text=True, check=True, env=env).stdout.strip()


def _template(fields):
    return json.dumps({
        "document_class": {"class_name": "speedtuning_calc",
                           "property_list_name": "speedtuning_calc"},
        "speedtuning_calc": {f: "" for f in fields},
        "depends_on": [{"name": "element_id", "value": ""}],
    })


def _repo(tmp_path):
    repo = tmp_path / "NDIcalc-vis-matlab"
    d = repo / GT.CDIR / "calc"
    d.mkdir(parents=True)
    _git(repo, "init", "-q")
    (d / "speedtuning_calc.json").write_text(_template(["input_parameters"]))
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "one")
    first = _git(repo, "rev-parse", "HEAD")
    (d / "speedtuning_calc.json").write_text(_template(["input_parameters", "fit"]))
    _git(repo, "commit", "-q", "-am", "two")
    second = _git(repo, "rev-parse", "HEAD")
    (d / "speedtuning_calc.json").write_text(_template(["worktree_only"]))
    return repo, first, second


def _lock(tmp_path, monkeypatch, sha):
    p = tmp_path / f"lock_{sha[:7]}.json"
    p.write_text(json.dumps({"why": "t", "date": "2026-10-28", "siblings": {
        "NDIcalc-vis-matlab": {"url": "u", "head_ref": "main", "head": sha, "main": sha}}}))
    monkeypatch.setenv("DID_SCHEMA_SIBLING_LOCK", str(p))


def test_reads_the_locked_commit_not_later_ones_or_the_worktree(tmp_path, monkeypatch):
    repo, first, _second = _repo(tmp_path)
    _lock(tmp_path, monkeypatch, first)
    got = GT.calc_templates(str(repo), {})
    assert sorted(got["speedtuning_calc"]["raw_fields"]) == ["input_parameters"], got
    assert GT.CALC_SCAN["rev_used"] == first
    assert GT.CALC_SCAN["candidates"] == 1 and GT.CALC_SCAN["classes"] == 1


def test_a_changed_template_changes_the_record(tmp_path, monkeypatch):
    repo, first, second = _repo(tmp_path)
    _lock(tmp_path, monkeypatch, first)
    a = GT.calc_templates(str(repo), {})
    _lock(tmp_path, monkeypatch, second)
    b = GT.calc_templates(str(repo), {})
    assert a != b
    assert sorted(b["speedtuning_calc"]["raw_fields"]) == ["fit", "input_parameters"]


def test_counts_what_it_skips(tmp_path, monkeypatch):
    repo, _first, _second = _repo(tmp_path)
    d = repo / GT.CDIR / "calc"
    (d / "speedtuning_calc.json").write_text(_template(["input_parameters"]))
    (d / "broken.json").write_text("{not json")
    (d / "notadoc.json").write_text(json.dumps({"x": 1}))
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "three")
    _lock(tmp_path, monkeypatch, _git(repo, "rev-parse", "HEAD"))
    got = GT.calc_templates(str(repo), {"speedtuning_calc": {}})
    s = GT.CALC_SCAN
    assert (s["candidates"], s["classes"], s["unparseable"], s["not_a_document_class"]) == (3, 1, 1, 1), s
    assert s["also_in_ndi"] == ["speedtuning_calc"]
    assert list(got) == ["speedtuning_calc"]
