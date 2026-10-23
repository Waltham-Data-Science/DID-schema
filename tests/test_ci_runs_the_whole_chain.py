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
    NDI's main at the LOCKED sha (`tools/sibling_lock.json`), which is not the
    clone's HEAD, and the ground truth also walks history from it to find each
    class's add-commit. A shallow clone does not error -- the ref lookup falls
    through and the tool reports a smaller universe -- so the step checks that
    the locked main commit is present and fails if it is not.
  * The LOCKED HEAD, not a branch name and not main. `check_pipeline_parity.py`
    and the status board's migrator evidence read NDI's `ndi_second_pass/`,
    which lives on the siblings' V2 line, not on their main. One checkout serves
    both readers only because a full clone brings the locked main along with it.
    Since 2026-10-23 the commit comes from the sibling lock (Jess Haley: build
    and check against locked commits), so a sibling's branch moving no longer
    changes what CI measures.
  * `NDI_MATLAB` / `DID_MATLAB` exported. `find_repo` in gates.py treats an
    explicitly set variable as authoritative; without them a child falls back to
    a default the driver already rejected, and the two disagree again.

These are structural checks on the workflow file. They cannot prove CI is green
-- only a run does that -- but they fail when the step is deleted, shallowed, or
quietly pointed somewhere else.
"""
import json
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parent.parent
WORKFLOW = REPO / ".github" / "workflows" / "tests.yml"

SIBLINGS = ("NDI-matlab", "DID-matlab")


# PARSED FROM THE TEXT, NOT WITH PyYAML, AND THAT IS DELIBERATE. The first
# draft of this file did `import yaml`, which worked here and turned all three
# CI jobs red on `ModuleNotFoundError: No module named 'yaml'` -- PyYAML is not
# in `[project.optional-dependencies].test`, it just happened to be installed on
# the machine the test was written on. That is the same mistake as the ruff
# version split one layer down: a check that depends on what the author's box
# happens to have is a check that measures the box.
#
# Adding the dependency would have been the other fix. Not importing it is
# better: every assertion below is about the TEXT of a shell step -- a flag that
# must not appear, a variable that must be exported, a word that must be printed
# -- so a YAML object model buys nothing and costs a package that must then be
# installed in three jobs.

STEP_RE = re.compile(r"^      - (?:name:|uses:|run:)", re.MULTILINE)


def _chain_steps():
    """Every step block of the `chain` job, as raw text."""
    text = WORKFLOW.read_text(encoding="utf-8")
    start = text.index("\n  chain:")
    end = text.index("\n  older-pythons:", start)
    body = text[start:end]
    bounds = [m.start() for m in STEP_RE.finditer(body)] + [len(body)]
    return [body[a:b] for a, b in zip(bounds, bounds[1:])]


def _checkout_step():
    for block in _chain_steps():
        if all(n in block for n in SIBLINGS) and "run:" in block:
            return block
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
    run = _checkout_step()
    shallow = re.findall(r"--depth[= ]\d+|--shallow-since|fetch-depth:\s*[1-9]", run)
    assert not shallow, (
        f"the sibling clone is shallow ({shallow}). coverage.py reads NDI at "
        "`origin/main` and ndi_ground_truth.py walks history for each class's "
        "add-commit; neither ERRORS on a shallow clone -- the ref lookup falls "
        "through and the tool reports a smaller universe.")


def test_the_missing_locked_main_guard_is_still_there():
    """A clone that lands without the locked main commit must FAIL, not proceed."""
    run = _checkout_step()
    assert re.search(r'--get "\$name" main', run), (
        "the step no longer reads the locked `main` sha from the sibling lock")
    assert re.search(r'cat-file -e "\$\{main\}\^\{commit\}"', run), (
        "the step no longer checks that the locked main commit resolves in the "
        "sibling clone. That check is what turns a silently-smaller universe "
        "into a red step.")
    assert re.search(r"rc=1", run), (
        "nothing in the step sets a non-zero exit. A checkout that could not "
        "give the gates what they read must fail loudly; the gates downstream "
        "would otherwise report NOT RUNNABLE and the run would go green on a "
        "third of the chain.")


def test_the_sibling_paths_are_exported_under_the_names_gates_reads():
    run = _checkout_step()
    for var in ("NDI_MATLAB", "DID_MATLAB"):
        assert re.search(rf"{var}=", run), (
            f"`{var}` is not exported. gates.py's find_repo treats an "
            "explicitly set variable as authoritative and hands it to every "
            "child; without it a child falls back to a default the driver "
            "already rejected.")


def _lock():
    with open(REPO / "tools" / "sibling_lock.json", encoding="utf-8") as fh:
        return json.load(fh)


def test_the_checkout_is_the_locked_head_not_a_branch_name():
    """The commits come from `tools/sibling_lock.json`, and nothing else.

    The branch-resolution logic this replaced (branch under test, PR base,
    integration ref, default branch) measured whatever those branches held at
    run time; NDI's main moving twice on 2026-10-23 turned the chain red with
    no change here. A surviving `head_ref` or `base_ref` would mean a branch
    name can still decide what CI measures."""
    step = _checkout_step()
    assert re.search(r'--get "\$name" head', step), (
        "the sibling checkout does not read the locked head")
    assert re.search(r'checkout --quiet --detach "\$head"', step), (
        "the sibling working tree is not checked out at the locked head")
    for leftover in ("head_ref", "base_ref", "SIBLING_INTEGRATION_REF",
                     "symbolic-ref"):
        assert leftover not in step, (
            f"`{leftover}` survives in the sibling checkout: a branch name can "
            "still decide what CI measures, which is what the lock replaced")
    assert "sibling_lock.py --check" in step, (
        "the step does not verify the checkout against the lock afterwards")


def test_the_lock_names_both_siblings_with_a_head_off_main():
    """The lock exists (there is no fallback without it), names both siblings,
    and locks each working tree to a commit that is NOT its main: the files the
    gates read from the working tree (NDI's second pass, the migrators) are on
    the V2 line, while the v1 truth is read from the locked main."""
    lk = _lock()
    sib = lk["siblings"]
    print(f"DENOMINATOR: {len(sib)} sibling(s) in the lock, {len(SIBLINGS)} required")
    assert set(SIBLINGS) <= set(sib), f"the lock is missing {set(SIBLINGS) - set(sib)}"
    for name in SIBLINGS:
        rec = sib[name]
        for key in ("head", "main"):
            assert re.fullmatch(r"[0-9a-f]{40}", rec[key]), (name, key, rec[key])
        assert rec["head"] != rec["main"] and rec.get("head_ref") != "main", (
            f"{name}'s locked working tree is its main; the gates that read the "
            "V2 line would measure a tree without it")
    assert lk.get("why") and re.fullmatch(r"\d{4}-\d{2}-\d{2}", lk.get("date", "")), (
        "the lock carries no `why` or no date")
