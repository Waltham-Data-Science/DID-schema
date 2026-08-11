"""CI must run all eighteen gates, not the twelve that need no sibling.

WHAT THIS PROTECTS. Until 2026-08-11 `tests.yml` checked out this repository
alone, so six of the eighteen steps reported NOT RUNNABLE HERE on every run:

    ndi_ground_truth, refresh_migration_targets, coverage, check_tombstones,
    check_empty_ontology_nodes, check_pipeline_parity

That report was honest -- "not runnable" has never been rendered as "passed" --
but a third of the chain was still never exercised on a runner, and it left
THREE OF THE FOUR artifacts CLAUDE.md calls "checked in CI" unprotected, because
the steps that produce them could not run. Both siblings are public; nothing but
a clone was in the way.

The clone has three properties that are each load-bearing, and each is asserted
here because each fails QUIETLY if it regresses:

  * FULL history, not `--depth 1`. `coverage.py` and `ndi_ground_truth.py` read
    NDI at `origin/main`, and the ground truth also walks history to find each
    class's add-commit. A shallow clone does not error -- the ref lookup falls
    through and the tool reports a smaller universe.
  * The FEATURE branch, not main. `check_pipeline_parity.py` and the status
    board's migrator evidence read NDI's `ndi_second_pass/`, which exists only
    on the feature branch. One checkout serves both readers only because a full
    clone brings `origin/main` along with it.
  * `NDI_MATLAB` / `DID_MATLAB` exported. `find_repo` in gates.py treats an
    explicitly set variable as authoritative; without them a child falls back to
    a default the driver already rejected, and the two disagree again.

These are structural checks on the workflow file. They cannot prove CI is green
-- only a run does that -- but they fail when the step is deleted, shallowed, or
quietly pointed somewhere else.
"""
import pathlib
import re

import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
WORKFLOW = REPO / ".github" / "workflows" / "tests.yml"

SIBLINGS = ("NDI-matlab", "DID-matlab")


def _chain_steps():
    doc = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    return doc["jobs"]["chain"]["steps"]


def _checkout_step():
    for s in _chain_steps():
        if "run" in s and all(n in s["run"] for n in SIBLINGS):
            return s
    return None


def test_the_workflow_checks_out_both_siblings():
    steps = _chain_steps()
    step = _checkout_step()
    print(f"DENOMINATOR: {len(steps)} step(s) in the `chain` job, "
          f"{len(SIBLINGS)} sibling(s) required")
    assert step, (
        "no step in the `chain` job names both siblings. Without them six of "
        "the eighteen gates report NOT RUNNABLE HERE -- including the two that "
        "produce the coverage ledger and the NDI ground truth, so those "
        "artifacts go unchecked on every run.")


def test_the_sibling_clone_is_not_shallow():
    run = _checkout_step()["run"]
    shallow = re.findall(r"--depth[= ]\d+|--shallow-since|fetch-depth:\s*[1-9]", run)
    assert not shallow, (
        f"the sibling clone is shallow ({shallow}). coverage.py reads NDI at "
        "`origin/main` and ndi_ground_truth.py walks history for each class's "
        "add-commit; neither ERRORS on a shallow clone -- the ref lookup falls "
        "through and the tool reports a smaller universe.")


def test_the_missing_origin_main_guard_is_still_there():
    """A clone that lands without `origin/main` must FAIL, not proceed."""
    run = _checkout_step()["run"]
    assert "origin/main" in run, (
        "the step no longer checks that `origin/main` resolves in the sibling "
        "clone. That check is what turns a silently-smaller universe into a "
        "red step.")
    assert re.search(r"rc=1", run), (
        "nothing in the step sets a non-zero exit. A checkout that could not "
        "give the gates what they read must fail loudly; the gates downstream "
        "would otherwise report NOT RUNNABLE and the run would go green on a "
        "third of the chain.")


def test_the_sibling_paths_are_exported_under_the_names_gates_reads():
    run = _checkout_step()["run"]
    for var in ("NDI_MATLAB", "DID_MATLAB"):
        assert re.search(rf"{var}=", run), (
            f"`{var}` is not exported. gates.py's find_repo treats an "
            "explicitly set variable as authoritative and hands it to every "
            "child; without it a child falls back to a default the driver "
            "already rejected.")


def test_the_requested_ref_is_the_branch_under_test_with_an_announced_fallback():
    step = _checkout_step()
    env = step.get("env", {})
    ref = " ".join(str(v) for v in env.values())
    assert "head_ref" in ref and "ref_name" in ref, (
        "the sibling ref is not the branch under test. Pinning it to a fixed "
        "branch would measure a tree nobody changed.")
    assert "FALLBACK" in step["run"], (
        "there is no announced fallback. After this branch merges the ref "
        "stops existing in the siblings; a bare checkout then goes red for a "
        "reason unrelated to the change, and a SILENT fallback is worse -- the "
        "gates would measure main while the log implies the branch.")
