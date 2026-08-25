"""Tests for `tools/gates.py`, the one entry point for the regenerate-and-gate chain.

WHY THIS FILE EXISTS
--------------------
A driver's whole value is that the chain runs in the RIGHT order and that a
failure inside it is visible. Both properties fail silently when they fail:
running `coverage.py` before `build_v_eta.py` still writes a ledger, still
prints a count, still updates an mtime -- it just describes the previous schema
set. And a step that exits 0 while printing nothing is indistinguishable from a
step nobody ran. So each property here is pinned by MUTATION: break the driver,
watch the named test go red, revert.

Three claims, one test each:

  * the order is DERIVED (a topological sort of the edge table) and every
    producer really does precede its consumer;
  * every edge's REASON is checkable -- the consumer's own source must contain
    a literal proving it reads the producer's artifact -- so a dependency
    cannot be asserted into existence by a comment;
  * a failing step, a missing headline, and a skipped dependent each force a
    non-zero exit, and `--check` never writes to the working tree.
"""

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(REPO_ROOT, "tools")


def _load_tool(name):
    spec = importlib.util.spec_from_file_location(name,
                                                  os.path.join(TOOLS, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


g = _load_tool("gates")


# --------------------------------------------------------------------------
# 1. the order is what it claims
# --------------------------------------------------------------------------

def test_the_published_order_is_the_derived_one():
    """`ORDER` must be the topological sort, not a list somebody typed.

    A hand-maintained order is the failure this driver exists to remove: it
    agrees with the graph on the day it is written and never again."""
    assert g.ORDER == g.derive_order(), (
        "tools/gates.py:ORDER is not the sort of its own EDGES table")
    assert len(g.ORDER) == len(g.STEPS)
    assert len(g.ORDER) == len(set(g.ORDER)), "a step appears twice in the order"


def test_every_producer_precedes_every_consumer():
    """The property the whole driver is for, asserted over the WHOLE edge set
    rather than the handful of pairs a person would remember."""
    assert g.EDGES, "the edge table is empty -- this test would check nothing"
    pos = {n: i for i, n in enumerate(g.ORDER)}
    for e in g.EDGES:
        assert pos[e.producer] < pos[e.consumer], (
            f"{e.producer} runs after {e.consumer}, but {e.consumer} reads {e.artifact} that {e.producer} writes")


def test_the_four_orderings_this_repo_gets_wrong_by_hand():
    """Named individually because these are the ones the commit log shows being
    reordered or dropped, and a general property does not say which pair broke.

    Each is a REAL read, not a convention:
      ndi_ground_truth -> build_v_eta   the build stamps ndi_mustBeNonEmpty from it
      build_v_eta      -> coverage      the ledger grades V_eta/index.json
      coverage         -> status_board  the board joins the ledger JSON
      status_board     -> the signoff gate, which reads V_eta_decisions.json
    """
    pos = {n: i for i, n in enumerate(g.ORDER)}
    pairs = [("ndi_ground_truth", "build_v_eta"),
             ("build_v_eta", "coverage"),
             ("coverage", "status_board"),
             ("status_board", "check_signoff_header_staleness")]
    assert len(pairs) == 4
    for before, after in pairs:
        assert pos[before] < pos[after], f"{before} must run before {after}"


def test_every_edge_reason_is_substantiated_by_the_consumers_own_source():
    """RULE 3 applied to this driver's own claims: an edge asserts that one tool
    reads another's output, and the witness is the literal in the consumer's
    source that proves it. An edge whose witness does not match is an invented
    dependency, and `--explain` refuses to run the chain when one exists."""
    assert g.EDGES, "the edge table is empty -- this test would check nothing"
    unsubstantiated = []
    for e in g.EDGES:
        ok, detail = e.substantiated(REPO_ROOT)
        if not ok:
            unsubstantiated.append(f"{e.producer} -> {e.consumer}: {detail}")
    assert not unsubstantiated, "\n".join(unsubstantiated)


def test_only_a_step_that_writes_can_skip_its_dependents():
    """DERIVED from `writes`, not declared. A report-only gate that fails is a
    failure of the run and nothing more -- stopping the rest would hide the
    other failures a developer ran the chain to see."""
    writers = [s for s in g.STEPS if s.blocks_dependents]
    reporters = [s for s in g.STEPS if not s.blocks_dependents]
    assert writers, "no step writes anything -- the chain would be pointless"
    assert reporters, "no step is report-only -- this test would check nothing"
    for s in writers:
        assert s.writes
    for s in reporters:
        assert not s.writes


def test_ci_owns_no_second_list_of_gates():
    """CI and the driver must be ONE list, not two that agree today.

    They were two, and they had diverged: the workflow ran 8 of the 16 steps and
    never rebuilt the schema set at all, so a hand-edit under schemas/V_eta
    passed every gate -- while CLAUDE.md said the generated artifacts were
    "CHECKED IN CI and fail when stale". This asserts the workflow invokes no
    gate of its own: every `run:` that reaches for a tool, pytest or ruff must
    go through tools/gates.py."""
    wf = os.path.join(REPO_ROOT, ".github", "workflows", "tests.yml")
    with open(wf) as fh:
        lines = [ln.strip() for ln in fh if ln.strip().startswith("- run:")
                 or ln.strip().startswith("run:")]
    assert lines, "no run: steps found in tests.yml -- this test would check nothing"
    gate_like = [ln for ln in lines
                 if "tools/" in ln or "pytest" in ln or "ruff check" in ln]
    assert gate_like, "the workflow runs no gate at all"
    strays = [ln for ln in gate_like if "tools/gates.py" not in ln]
    assert not strays, (
        "tests.yml runs a gate outside the driver -- that is a second list:\n  "
        + "\n  ".join(strays))


def test_every_gate_ci_used_to_run_by_hand_is_still_in_the_chain():
    """Folding eight workflow steps into the driver must not have dropped one.

    Named individually, because "the driver is a superset" is exactly the kind
    of claim this repository has been burned by when it was asserted instead of
    listed."""
    was_in_ci = ["ruff", "pytest", "check_migrator_vocabulary", "status_board",
                 "check_duplicate_field_declarations", "check_constraint_refinement",
                 "check_vacuous_tests", "check_signoff_header_staleness"]
    assert len(was_in_ci) == 8
    missing = [n for n in was_in_ci if n not in g.BY_NAME]
    assert not missing, f"the driver dropped a gate CI used to run: {missing}"


def test_a_step_needing_a_sibling_checkout_names_it_in_its_own_source():
    """The `requires` declarations are the reason CI legitimately runs a shorter
    chain, so they cannot be guesses. Each named sibling must appear in the
    step's own source -- the same standard the edge witnesses are held to."""
    needy = [s for s in g.STEPS if s.requires]
    assert needy, "no step declares a sibling -- this test would check nothing"
    for s in needy:
        src = s.source_path()
        assert src, f"{s.name} declares requires but runs no script"
        with open(os.path.join(REPO_ROOT, src), errors="replace") as fh:
            body = fh.read()
        for sib in s.requires:
            assert sib in body, (
                f"{s.name} says it needs {sib}, but {src} never names it")


def test_every_step_is_told_the_same_sibling_answer():
    """One resolution for the whole chain, in all four spellings the tools use.

    Not hypothetical. Run the chain from a checkout that is not beside
    DID-matlab and check_tombstones.py -- which consults only $DID_MATLAB then
    ../DID-matlab -- grades all 66 tombstones as passthroughs and reports
    BLOCKING 6, while the driver's own header says the sibling was found. It
    happened on the first full-chain run here: 6 with the fallback, 0 once the
    resolved path was passed down. A gate that fails on where the repository
    happens to sit is a red build with a true-looking cause."""
    env = g.child_env()
    for var in ("NDI_MATLAB", "NDI_MATLAB_PATH", "DID_MATLAB", "DID_MATLAB_PATH"):
        assert var in env, f"child steps are not told {var}"
    assert env["NDI_MATLAB"] == env["NDI_MATLAB_PATH"]
    assert env["DID_MATLAB"] == env["DID_MATLAB_PATH"]
    for name, var in (("NDI-matlab", "NDI_MATLAB"), ("DID-matlab", "DID_MATLAB")):
        resolved = g.SIBLINGS.get(name)
        if resolved:
            assert env[var] == resolved
        else:
            # absent must be SAID, not left to a child's own default
            assert not os.path.isdir(env[var]), (
                f"{name} is absent to the driver but {var} points somewhere real")


# --------------------------------------------------------------------------
# 2. a failing step produces a non-zero exit
# --------------------------------------------------------------------------

def _stub(step_name, code, printed):
    """Swap one step's argv for a stub with a chosen exit code and output."""
    step = g.BY_NAME[step_name]
    saved = step.argv
    step.argv = [sys.executable, "-c",
                 f'import sys; sys.stdout.write({printed!r}); sys.exit({code})']
    return step, saved


def _run(argv):
    """Run gates.main with stdout captured, returning (rc, text)."""
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = g.main(argv)
    return rc, buf.getvalue()


def test_a_step_that_exits_non_zero_fails_the_run():
    step, saved = _stub("check_vacuous_tests", 3,
                        "VACUOUS-TEST SWEEP: 15 test file(s) parsed\n")
    try:
        rc, out = _run(["--only", "check_vacuous_tests"])
    finally:
        step.argv = saved
    assert rc != 0, out
    assert "FAIL" in out
    assert "check_vacuous_tests" in out


def test_a_step_that_exits_zero_while_printing_nothing_fails_the_run():
    """The `silentLoss` defect, one layer up. Exit 0 is not evidence a step ran:
    the headline count is. A step with no headline is reported NO-HEADLINE and
    fails, because it is indistinguishable from a step that was skipped."""
    step, saved = _stub("check_vacuous_tests", 0, "")
    try:
        rc, out = _run(["--only", "check_vacuous_tests"])
    finally:
        step.argv = saved
    assert rc != 0, out
    assert "NO-HEADLINE" in out, out


def test_the_same_step_passing_exits_zero():
    """The control. Without it the two tests above would also pass on a driver
    that always returns non-zero."""
    step, saved = _stub("check_vacuous_tests", 0,
                        "VACUOUS-TEST SWEEP: 15 test file(s) parsed\n")
    try:
        rc, out = _run(["--only", "check_vacuous_tests"])
    finally:
        step.argv = saved
    assert rc == 0, out
    assert "15: test files parsed" in out


def test_the_denominator_prints_before_anything_runs():
    """Operating rule 5, on the real output. The step count must appear whether
    or not a step does -- and BEFORE the first step line, so a run that died
    early is still countable."""
    step, saved = _stub("check_vacuous_tests", 1, "")
    try:
        _rc, out = _run(["--only", "check_vacuous_tests"])
    finally:
        step.argv = saved
    assert "DENOMINATOR:" in out
    assert out.index("DENOMINATOR:") < out.index("[ 1/ 1]"), out


def test_a_failed_generator_skips_its_dependents_and_still_exits_non_zero():
    """Continuing past a failed producer would gate against a stale artifact and
    report it GREEN. The dependents are named as SKIPPED -- not silently
    dropped, and never counted as passes."""
    step, saved = _stub("coverage", 1, "(101 v1 classes\n")
    try:
        rc, out = _run(["--only", "coverage", "--only", "status_board",
                        "--only", "check_signoff_header_staleness"])
    finally:
        step.argv = saved
    assert rc != 0, out
    assert "SKIPPED" in out
    assert "status_board" in out
    assert "check_signoff_header_staleness" in out


# --------------------------------------------------------------------------
# 3. --check does not mutate the working tree
# --------------------------------------------------------------------------

def _clone_with_live_driver(tmp):
    """A one-writer clone of the repo, running the driver AS IT IS ON DISK.

    The clone comes from git, so it carries the COMMITTED gates.py -- and a
    mutation test that edits the working copy would then exercise the old file
    and pass while the property is broken. That happened here: mutating
    `--check`'s cwd handling changed nothing until the live file was copied in.
    So the driver under test is copied over the clone's copy, and its own path
    is excluded from the cleanliness assertion below."""
    clone = os.path.join(tmp, "repo")
    subprocess.run(["git", "clone", "--local", "--quiet", REPO_ROOT, clone],
                   check=True, capture_output=True)
    shutil.copy2(os.path.join(TOOLS, "gates.py"),
                 os.path.join(clone, "tools", "gates.py"))
    return clone


def _dirty(clone):
    """`git status --porcelain` minus the driver we deliberately copied in."""
    out = subprocess.run(["git", "-C", clone, "status", "--porcelain"],
                         capture_output=True, text=True, check=True).stdout
    return "".join(ln + "\n" for ln in out.splitlines()
                   if ln.strip() not in ("M tools/gates.py",)
                   and not ln.endswith(" tools/gates.py"))


def _stat_tree(root, rels):
    """(mtime_ns, size) for every file under the given repo-relative paths.

    mtime, NOT a content hash. These generators are deterministic, so writing
    them in the wrong place produces BYTE-IDENTICAL files and a content digest
    sees nothing -- which is exactly how a --check that quietly regenerated in
    place would pass this test. The mtime detects the WRITE, which is the thing
    forbidden. (The driver's own runtime guard uses content instead, on purpose:
    there a concurrent no-op regeneration by another agent must not be reported
    as damage.)"""
    out = {}
    for rel in rels:
        p = os.path.join(root, rel)
        if os.path.isdir(p):
            for base, dirs, files in os.walk(p):
                dirs.sort()
                for f in sorted(files):
                    fp = os.path.join(base, f)
                    st = os.stat(fp)
                    out[os.path.relpath(fp, root)] = (st.st_mtime_ns, st.st_size)
        elif os.path.exists(p):
            st = os.stat(p)
            out[rel] = (st.st_mtime_ns, st.st_size)
    return out


def test_check_mode_writes_nothing_into_the_repository():
    """Run in a CLONE, not in the live tree.

    Two reasons, and the second is the one that matters: other agents edit this
    repository concurrently, so a before/after snapshot taken in the live tree
    would report their work as this driver's mutation -- a test that fails for
    a reason it did not measure. The clone has exactly one writer."""
    tmp = tempfile.mkdtemp(prefix="gates-check-test-")
    try:
        clone = _clone_with_live_driver(tmp)
        before_git = _dirty(clone)
        assert before_git == "", f"the clone did not start clean: {before_git!r}"

        watched = sorted({w for s in g.STEPS for w in s.writes})
        assert watched, "no step declares a write -- this test would check nothing"
        before = _stat_tree(clone, watched)
        assert before, "nothing to watch in the clone"

        p = subprocess.run([sys.executable, os.path.join(clone, "tools", "gates.py"),
                            "--check", "--only", "build_v_eta",
                            "--only", "regen_final_class_set"],
                           capture_output=True, text=True, cwd=clone, check=False)
        after = _dirty(clone)
        assert after == "", (
            f"--check changed tracked content in the working tree:\n{after}\n"
            f"--- driver output ---\n{p.stdout[-3000:]}")
        touched = sorted(k for k, v in _stat_tree(clone, watched).items()
                         if before.get(k) != v)
        assert not touched, (
            "--check WROTE these working-tree paths (mtime moved) even though "
            "the bytes did not change:\n  {}\n--- driver output ---\n{}".format("\n  ".join(touched[:20]), p.stdout[-3000:]))
        # It must also have actually DONE something -- a --check that ran no
        # step would trivially satisfy the assertions above.
        assert "ARTIFACT DIFF" in p.stdout, p.stdout
        assert "build_v_eta" in p.stdout
        assert "WORKING-TREE GUARD" in p.stdout
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_check_mode_reports_a_stale_artifact_as_a_difference():
    """The other half: --check must NOTICE. Hand-edit a generated artifact in a
    clone, run --check, and the artifact is named as DIFFERS with a non-zero
    exit -- while the working tree is still untouched."""
    tmp = tempfile.mkdtemp(prefix="gates-stale-test-")
    try:
        clone = _clone_with_live_driver(tmp)
        target = os.path.join(clone, "schemas", "V_eta_final_class_set.md")
        with open(target, "a") as fh:
            fh.write("\n## FABRICATED CATEGORY (9999)\n")
        p = subprocess.run([sys.executable, os.path.join(clone, "tools", "gates.py"),
                            "--check", "--only", "build_v_eta",
                            "--only", "regen_final_class_set"],
                           capture_output=True, text=True, cwd=clone, check=False)
        assert p.returncode != 0, p.stdout
        assert "V_eta_final_class_set.md" in p.stdout
        assert "DIFFERS" in p.stdout, p.stdout
        # and the hand edit is still there -- --check reported it, did not fix it
        assert "FABRICATED CATEGORY" in Path(target).read_text()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
