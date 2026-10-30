"""#114 item 2: a hash CLAUDE.md calls a branch's head is checked against it.

Written from the defect, not from the code: three hashes found by hand on
2026-10-22 named heads that had moved, and read as current facts. Each test
builds a throwaway git repository whose branch is at a known commit, so the
three states (CURRENT, STALE, NOT CHECKED) are each reached on purpose. The
full 40-character hashes are used: a 7-character prefix can be all digits,
which the hash pattern rightly does not read as a hash.
"""
import importlib.util
import os
import subprocess

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location(
    "_cpc", os.path.join(REPO_ROOT, "tools", "check_prose_counts.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)


def _repo(tmp_path, n):
    r = tmp_path / "DID-matlab"
    r.mkdir()
    run = lambda *a: subprocess.run(["git", "-C", str(r), *a], check=True,  # noqa: E731
                                    capture_output=True, text=True)
    run("init", "-q", "-b", "V2")
    run("config", "user.email", "t@t")
    run("config", "user.name", "t")
    shas = []
    for k in range(n):
        (r / "f").write_text(str(k))
        run("add", "f")
        run("commit", "-q", "-m", str(k))
        shas.append(run("rev-parse", "HEAD").stdout.strip())
    return r, shas


def _claude(tmp_path, text):
    p = tmp_path / "CLAUDE.md"
    p.write_text(text)
    return str(p)


def test_a_current_head_passes_and_a_moved_one_is_stale(tmp_path, monkeypatch):
    r, shas = _repo(tmp_path, 2)
    monkeypatch.setenv("DID_MATLAB", str(r))
    doc = _claude(tmp_path,
                  f"DID-matlab `V2` head is {shas[1]} today.\n\n"
                  f"DID-matlab `V2` head is {shas[0]} (written last week).\n")
    rows = C.head_claims(doc)
    assert [row[4] for row in rows] == ["CURRENT", "STALE"], rows
    assert C.render_head_claims(rows, out=lambda *_: None) == 1


def test_a_hash_with_no_head_word_is_not_a_claim(tmp_path, monkeypatch):
    r, shas = _repo(tmp_path, 1)
    monkeypatch.setenv("DID_MATLAB", str(r))
    doc = _claude(tmp_path, f"The fix landed in DID-matlab {shas[0]} on V2.\n")
    assert C.head_claims(doc) == []


def test_no_checkout_is_not_checked_never_current(tmp_path, monkeypatch):
    monkeypatch.setenv("DID_MATLAB", "")
    doc = _claude(tmp_path, "DID-matlab `V2` head is abc1234 today.\n")
    rows = C.head_claims(doc)
    assert [row[4] for row in rows] == ["NOT CHECKED"], rows


def test_the_real_claude_md_is_read(tmp_path):
    # denominator: the real file is opened and every claim lands in one state
    rows = C.head_claims()
    assert all(row[4] in ("CURRENT", "STALE", "NOT CHECKED") for row in rows)
