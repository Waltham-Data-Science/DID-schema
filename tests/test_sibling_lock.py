"""The sibling lock (`tools/sibling_lock.json`, `tools/sibling_lock.py`).

WHAT THIS PROTECTS. The chain read NDI-matlab's live `origin/main`, and on
2026-10-23 NDI gained `.m` files twice (1,300 -> 1,305 -> 1,307): the
`ndi_m_files` prose count went red and generated files changed with no change
here. The lock names the exact sibling commits; every `origin/main` read reads
the locked sha and the working trees are verified against the locked head.

Each test builds its own tiny git repositories in a tmp dir and points the lock
at them through `$DID_SCHEMA_SIBLING_LOCK`, so nothing here depends on the real
siblings or on the committed lock's shas.
"""
import contextlib
import importlib.util
import io
import json
import os
import subprocess

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV = "DID_SCHEMA_SIBLING_LOCK"


def _load(name):
    path = os.path.join(REPO, "tools", name + ".py")
    spec = importlib.util.spec_from_file_location("_lock_test_" + name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SL = _load("sibling_lock")


def _git(root, *args):
    return subprocess.run(
        ["git", "-C", str(root), "-c", "user.email=t@t", "-c", "user.name=t",
         *args], check=True, capture_output=True, text=True).stdout.strip()


def _commit(root, files, msg):
    for rel, text in files.items():
        p = os.path.join(str(root), rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as fh:
            fh.write(text)
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", msg)
    return _git(root, "rev-parse", "HEAD")


def _repo(tmp_path, name="NDI-matlab"):
    """A sibling with two commits on `main`: A (2 .m files), then B (3).
    `origin/main` points at B -- the live ref has MOVED past A."""
    root = tmp_path / name
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    a = _commit(root, {"src/one.m": "x\n", "src/two.m": "x\n"}, "A")
    b = _commit(root, {"src/three.m": "x\n"}, "B")
    _git(root, "update-ref", "refs/remotes/origin/main", b)
    return root, a, b


def _write_lock(path, siblings):
    with open(path, "w") as fh:
        json.dump({"why": "test", "date": "2026-10-23", "siblings": siblings}, fh)
    return str(path)


def _verify(paths, path):
    buf = io.StringIO()
    bad = SL.verify(paths=paths, path=path, out=lambda s: buf.write(s + "\n"))
    return bad, buf.getvalue()


# --------------------------------------------------------------------------
# a missing, malformed or stale lock is REPORTED
# --------------------------------------------------------------------------

def test_a_missing_lock_is_a_reported_problem(tmp_path):
    bad, out = _verify({}, str(tmp_path / "no-such-lock.json"))
    assert bad == 1, out
    assert "MISSING" in out and "--update" in out, out


def test_a_malformed_lock_is_unreadable_not_absent(tmp_path):
    p = tmp_path / "lock.json"
    p.write_text('{"siblings": {"NDI-matlab": {"head": "abc", "main": "def"}}}')
    bad, out = _verify({}, str(p))
    assert bad == 1, out
    assert "UNREADABLE" in out, out


def test_a_checkout_not_at_the_locked_head_is_a_mismatch_with_the_fix(tmp_path):
    root, a, b = _repo(tmp_path)
    lock = _write_lock(tmp_path / "lock.json",
                       {"NDI-matlab": {"head": a, "main": a, "head_ref": "V2"}})
    bad, out = _verify({"NDI-matlab": str(root)}, lock)   # HEAD is B
    print(out)
    assert bad == 1, out
    assert "HEAD MISMATCH" in out, out
    assert f"checkout --detach {a}" in out, "the fix command is not printed"
    # and the live origin/main having moved is NOTED, not silently read
    assert "past the lock" in out, out


def test_a_locked_main_the_clone_does_not_hold_is_a_problem(tmp_path):
    root, _a, b = _repo(tmp_path)
    missing = "0" * 40
    lock = _write_lock(tmp_path / "lock.json",
                       {"NDI-matlab": {"head": b, "main": missing}})
    bad, out = _verify({"NDI-matlab": str(root)}, lock)
    assert bad == 1, out
    assert "NOT IN THIS CLONE" in out, out


def test_a_matching_checkout_passes_and_an_absent_one_is_not_checked(tmp_path):
    """The control: without it the tests above would pass on a verifier that
    always complains. An absent sibling is NOT CHECKED, never a pass."""
    root, a, b = _repo(tmp_path)
    lock = _write_lock(tmp_path / "lock.json", {
        "NDI-matlab": {"head": b, "main": a},
        "DID-matlab": {"head": a, "main": a}})
    bad, out = _verify({"NDI-matlab": str(root), "DID-matlab": None}, lock)
    assert bad == 0, out
    assert "DENOMINATOR: 2 sibling(s) locked" in out, out
    assert "NOT CHECKED: no DID-matlab checkout here" in out, out


def test_gates_refuses_to_run_on_a_lock_problem(tmp_path, monkeypatch):
    """Through the real driver: a lock problem stops the chain BEFORE any step
    runs -- in regenerate mode a step would otherwise write artifacts from a
    tree nobody committed to."""
    g = _load("gates")
    monkeypatch.setenv(ENV, str(tmp_path / "no-such-lock.json"))
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = g.main(["--only", "check_vacuous_tests"])
    out = buf.getvalue()
    assert rc == 1, out
    assert "SIBLING LOCK: MISSING" in out, out
    assert "nothing was run" in out, out
    assert "[ 1/ 1]" not in out, "a step ran despite the lock problem"


# --------------------------------------------------------------------------
# --update writes the shas
# --------------------------------------------------------------------------

def test_update_records_head_and_origin_main(tmp_path):
    ndi, a, b = _repo(tmp_path, "NDI-matlab")
    _git(ndi, "checkout", "-q", "-b", "V2", a)        # HEAD = A on V2, origin/main = B
    did, _da, db = _repo(tmp_path, "DID-matlab")
    path = str(tmp_path / "lock.json")
    rc = SL.update(paths={"NDI-matlab": str(ndi), "DID-matlab": str(did)},
                   path=path, today="2026-10-23", out=lambda s: None)
    assert rc == 0
    with open(path) as fh:
        lk = json.load(fh)
    assert lk["date"] == "2026-10-23" and lk["why"]
    assert lk["siblings"]["NDI-matlab"]["head"] == a
    assert lk["siblings"]["NDI-matlab"]["main"] == b
    assert lk["siblings"]["NDI-matlab"]["head_ref"] == "V2"
    assert lk["siblings"]["DID-matlab"]["head"] == db
    # and what it wrote is a lock the verifier accepts for those checkouts
    bad, out = _verify({"NDI-matlab": str(ndi), "DID-matlab": str(did)}, path)
    assert bad == 0, out


def test_update_keeps_an_absent_siblings_entry(tmp_path):
    ndi, a, b = _repo(tmp_path, "NDI-matlab")
    path = _write_lock(tmp_path / "lock.json",
                       {"DID-matlab": {"head": a, "main": a, "head_ref": "V2"}})
    rc = SL.update(paths={"NDI-matlab": str(ndi), "DID-matlab": None},
                   path=path, today="2026-10-24", out=lambda s: None)
    assert rc == 0
    with open(path) as fh:
        sib = json.load(fh)["siblings"]
    assert sib["DID-matlab"]["head"] == a, "an absent sibling's entry was dropped"
    assert sib["NDI-matlab"]["head"] == b


# --------------------------------------------------------------------------
# reads use the LOCKED main, not the live origin/main
# --------------------------------------------------------------------------

def test_main_refs_is_the_locked_sha_alone_and_falls_back_only_without_a_lock(tmp_path):
    lock = _write_lock(tmp_path / "lock.json",
                       {"NDI-matlab": {"head": "a" * 40, "main": "b" * 40}})
    assert SL.main_refs("NDI-matlab", path=lock) == [("origin/main", "b" * 40)]
    # a repository the lock does not name reads its live main, as before
    assert SL.main_refs("Fake-matlab", path=lock) == [
        ("origin/main", "origin/main"), ("main", "main")]
    assert SL.main_refs("NDI-matlab", path=str(tmp_path / "none.json")) == [
        ("origin/main", "origin/main"), ("main", "main")]


def test_the_ndi_m_files_count_reads_the_locked_main(tmp_path, monkeypatch):
    """The `ndi_m_files` prose count moves only when the lock moves: the live
    `origin/main` (B, 3 files) has moved past the lock (A, 2 files)."""
    root, a, _b = _repo(tmp_path)
    lock = _write_lock(tmp_path / "lock.json",
                       {"NDI-matlab": {"head": a, "main": a}})
    monkeypatch.setenv(ENV, lock)
    monkeypatch.setenv("NDI_MATLAB", str(root))
    pc = _load("check_prose_counts")
    assert pc.derive_ndi_m_files() == 2
    monkeypatch.setenv(ENV, "")                      # no lock: the live ref
    assert pc.derive_ndi_m_files() == 3


def test_the_ground_truth_reads_templates_at_the_locked_main(tmp_path, monkeypatch):
    ngt = _load("ndi_ground_truth")
    root = tmp_path / "NDI-matlab"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")

    def tmpl(cn):
        return json.dumps({"document_class": {"class_name": cn,
                                              "property_list_name": cn,
                                              "class_version": 1,
                                              "superclasses": []},
                           cn: {"f": 1}})
    a = _commit(root, {f"{ngt.DDIR}/old.json": tmpl("old_class")}, "A")
    b = _commit(root, {f"{ngt.DDIR}/new.json": tmpl("new_class")}, "B")
    _git(root, "update-ref", "refs/remotes/origin/main", b)
    lock = _write_lock(tmp_path / "lock.json",
                       {"NDI-matlab": {"head": b, "main": a}})
    monkeypatch.setenv(ENV, lock)
    truth, ref = ngt.ndi_templates(str(root))
    assert ref == "origin/main", "the artifact label must stay origin/main"
    assert ngt.TEMPLATE_SCAN["rev_used"] == a
    assert set(truth) == {"old_class"}, (
        f"read {sorted(truth)}: the live origin/main was read, not the lock")
