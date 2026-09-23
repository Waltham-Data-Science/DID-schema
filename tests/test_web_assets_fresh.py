"""Tests for `tools/check_web_assets_fresh.py`, and for the mutations it must catch.

WHY THIS FILE EXISTS, AND WHY HALF OF IT IS MUTATION
----------------------------------------------------
A freshness checker whose comparison has stopped comparing and a freshness
checker that finds nothing wrong print the SAME clean result. This repository
has been bitten by exactly that shape more than once -- `silentLoss` reported
"0 empty edges" for two days while reading nothing, and a `partitions_hold ->
return True` left all 76 tests of another sweep green. So the properties here
are pinned by BREAKING the tool and watching a named test go red:

  * a stale served file reddens                     -> stubbing `same_bytes` to
                                                      "always equal" makes that
                                                      finding vanish, and the
                                                      test that proves it is
                                                      `test_stubbing_the_comparison_...`
  * an unpairable served file is REPORTED and fails -> not silently skipped,
                                                      because "found nothing"
                                                      and "looked in the wrong
                                                      place" must not print the
                                                      same thing
  * zero served files is a FAILURE                  -> a denominator of zero is
                                                      never a clean result
  * the contract is DERIVED from sync-schemas.mjs   -> edit the script in a
                                                      fixture and the derived
                                                      contract moves with it

Every test builds its own miniature repository under tmp_path -- a `schemas/`
tree, a `web/scripts/sync-schemas.mjs`, a `web/public/` -- so nothing here
depends on the state of the checkout, which several agents are editing while
these run.
"""

import importlib.util
import json
import os
import subprocess
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(REPO_ROOT, "tools")


def _load_tool(name):
    spec = importlib.util.spec_from_file_location(name,
                                                  os.path.join(TOOLS, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


w = _load_tool("check_web_assets_fresh")
g = _load_tool("gates")


# --------------------------------------------------------------------------
# a miniature repository
# --------------------------------------------------------------------------

# The real script, reduced to the four statements the derivation reads. It is a
# FIXTURE and not the live file on purpose: a test that ran against the live
# script would change meaning whenever somebody edited the viewer, and the
# derivation is separately proved to track edits by
# `test_the_contract_moves_when_the_sync_script_moves`.
SYNC_JS = '''
import { cp, writeFile } from "node:fs/promises";
const schemasDir = resolve(repoRoot, "schemas");
const publicSchemas = resolve(publicDir, "schemas");
const versions = entries.filter((d) => /^V_/.test(d.name) &&
  existsSync(resolve(schemasDir, d.name, "index.json"))).map((d) => d.name);
for (const v of versions) {
  await cp(resolve(schemasDir, v), resolve(publicSchemas, v), { recursive: true });
}
await writeFile(resolve(publicSchemas, "versions.json"), JSON.stringify({}));
const ledgerSrc = resolve(schemasDir, "V_eta_coverage_ledger.json");
await cp(ledgerSrc, resolve(publicDir, "coverage.json"));
const decisionsSrc = resolve(schemasDir, "V_eta_decisions.json");
await cp(decisionsSrc, resolve(publicDir, "decisions.json"));
'''


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def make_repo(tmp_path, sync_js=SYNC_JS):
    """A repository shaped like this one, synced and clean."""
    root = str(tmp_path / "repo")
    _write(os.path.join(root, "web", "scripts", "sync-schemas.mjs"), sync_js)
    _write(os.path.join(root, "schemas", "V_zeta", "index.json"), '{"set": "zeta"}\n')
    _write(os.path.join(root, "schemas", "V_eta", "index.json"), '{"set": "eta"}\n')
    _write(os.path.join(root, "schemas", "V_eta", "stable", "strain.json"), '{"c": 1}\n')
    _write(os.path.join(root, "schemas", "V_eta_coverage_ledger.json"), '{"rows": 102}\n')
    _write(os.path.join(root, "schemas", "V_eta_decisions.json"), '{"families": 9}\n')
    sync(root)
    return root


def sync(root):
    """Do what the sync script does, in the fixture. Deliberately NOT by
    running node: these tests must pass on a machine with no node, and the
    thing under test is the CHECKER, not the script."""
    pub = os.path.join(root, "web", "public")
    sets = w.schema_sets(root)
    for s in sets:
        src = os.path.join(root, "schemas", s)
        for base, _dirs, files in os.walk(src):
            for f in files:
                rel = os.path.relpath(os.path.join(base, f), src)
                dst = os.path.join(pub, "schemas", s, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                with open(os.path.join(base, f), "rb") as a, open(dst, "wb") as b:
                    b.write(a.read())
    for served, srcname in (("coverage.json", "V_eta_coverage_ledger.json"),
                            ("decisions.json", "V_eta_decisions.json")):
        s = os.path.join(root, "schemas", srcname)
        if os.path.exists(s):
            with open(s, "rb") as a, open(os.path.join(pub, served), "wb") as b:
                b.write(a.read())
    _write(os.path.join(pub, "schemas", "versions.json"),
           json.dumps({"versions": sets, "default": sets[-1]}) + "\n")


def run(root, *extra):
    """Run the checker over a fixture root, returning (rc, printed)."""
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = w.main(["--root", root, *extra])
    return rc, buf.getvalue()


# --------------------------------------------------------------------------
# 1. the control: a synced tree passes
# --------------------------------------------------------------------------

def test_a_synced_tree_passes(tmp_path):
    """Without this every assertion below would also hold for a checker that
    always fails."""
    root = make_repo(tmp_path)
    rc, out = run(root)
    assert rc == 0, out
    assert "OK: all" in out, out
    assert "STALE -- served bytes differ from the source: 0" in out, out


def test_the_denominator_prints_first_and_unconditionally(tmp_path):
    """Rule 5, on the real output: how many served files were inspected, how
    many paired, how many NOT."""
    root = make_repo(tmp_path)
    _rc, out = run(root)
    lines = [ln for ln in out.splitlines() if ln.strip()]
    first = next(i for i, ln in enumerate(lines) if ln.startswith("DENOMINATOR:"))
    assert first <= 1, f"the denominator is not the first thing printed:\n{out}"
    assert "served file(s) inspected" in lines[first]
    body = "\n".join(lines[first:first + 6])
    assert "paired with a generator source" in body, body
    assert "UNPAIRABLE" in body, body


# --------------------------------------------------------------------------
# 2. THE FINDINGS -- one test per failure mode
# --------------------------------------------------------------------------

def test_a_stale_served_file_reddens(tmp_path):
    """The defect this tool was written for: the source moves on, the copy does
    not. THIS is the test that goes red under the always-equal mutation
    below."""
    root = make_repo(tmp_path)
    _write(os.path.join(root, "schemas", "V_eta_coverage_ledger.json"),
           '{"rows": 102, "binaryseries_parameters": "resolved"}\n')
    rc, out = run(root)
    assert rc != 0, out
    assert "STALE -- served bytes differ from the source: 1" in out, out
    assert "coverage.json" in out
    assert "schemas/V_eta_coverage_ledger.json" in out


def test_a_stale_served_schema_reddens_too(tmp_path):
    """Not just the two named JSONs: the whole copied schema set is graded, and
    seven of the nine real findings were files under schemas/V_eta."""
    root = make_repo(tmp_path)
    _write(os.path.join(root, "schemas", "V_eta", "stable", "strain.json"),
           '{"c": 2}\n')
    rc, out = run(root)
    assert rc != 0, out
    assert "stable/strain.json" in out, out


def test_an_unpairable_served_file_is_reported_and_fails(tmp_path):
    """Reported, never silently skipped. A served file nothing produces is the
    shape of 'found nothing' that is really 'looked in the wrong place'."""
    root = make_repo(tmp_path)
    _write(os.path.join(root, "web", "public", "hand_written.json"), "{}\n")
    rc, out = run(root)
    assert rc != 0, out
    assert "UNPAIRABLE -- served, produced by nothing this tool can find: 1" in out, out
    assert "hand_written.json" in out, out


def test_a_served_copy_whose_source_was_deleted_is_an_ORPHAN_not_an_unknown(tmp_path):
    """The distinction is load-bearing. Three real served files were copies of
    classes since deleted from `schemas/`; calling them 'unexplained' would
    hide that the viewer is still serving a class that no longer exists."""
    root = make_repo(tmp_path)
    os.remove(os.path.join(root, "schemas", "V_eta", "stable", "strain.json"))
    rc, out = run(root)
    assert rc != 0, out
    assert "ORPHANED -- served, but the source no longer exists: 1" in out, out
    assert "UNPAIRABLE -- served, produced by nothing this tool can find: 0" in out, out


def test_a_source_with_no_served_copy_is_reported(tmp_path):
    """The other direction, and the one a one-sided sweep misses: a class added
    since the last sync is invisible in the viewer, and invisible is exactly
    what a check over the served files alone would also be."""
    root = make_repo(tmp_path)
    _write(os.path.join(root, "schemas", "V_eta", "stable", "logical.json"), "{}\n")
    rc, out = run(root)
    assert rc != 0, out
    assert "UNSERVED -- the contract serves it, no served copy exists: 1" in out, out
    assert "logical.json" in out, out


def test_zero_served_files_is_a_failure_not_a_clean_zero(tmp_path):
    """A checker that inspects nothing must not print a pass. This is the
    `silentLoss` defect stated as a rule."""
    root = make_repo(tmp_path)
    import shutil
    shutil.rmtree(os.path.join(root, "web", "public"))
    rc, out = run(root)
    assert rc != 0, out
    assert "DENOMINATOR: 0 served file(s) inspected" in out, out
    assert "NOT SYNCED" in out, out
    assert "NOT a clean result" in out, out


def test_an_unreadable_contract_stops_the_tool_rather_than_grading_nothing(tmp_path):
    """An absent contract is not an empty contract. With no sync script there
    is no mapping to grade against, and reporting 'all clear' would be a lie
    about a tree nobody looked at."""
    root = make_repo(tmp_path)
    os.remove(os.path.join(root, "web", "scripts", "sync-schemas.mjs"))
    rc, out = run(root)
    assert rc != 0, out
    assert "CONTRACT UNREADABLE" in out, out


def test_a_sync_script_that_stops_stating_its_selection_rule_stops_the_tool(tmp_path):
    """The one rule this tool restates -- a `V_*` directory with an index.json
    is a served set -- is checked against the script's own text. If the script
    stops saying it, grading against the restatement would be grading against a
    rule the script no longer follows."""
    root = make_repo(tmp_path, sync_js=SYNC_JS.replace("index.json", "manifest.json"))
    rc, out = run(root)
    assert rc != 0, out
    assert "CONTRACT UNREADABLE" in out, out
    assert "selection rule" in out, out


def test_the_versions_manifest_is_checked_against_the_sets_that_exist(tmp_path):
    """The one served file that is WRITTEN rather than copied. It cannot be
    compared byte for byte, so it is compared structurally -- and the tool says
    in its output that this is less than a byte comparison."""
    root = make_repo(tmp_path)
    _write(os.path.join(root, "web", "public", "schemas", "versions.json"),
           json.dumps({"versions": ["V_eta"], "default": "V_eta"}) + "\n")
    rc, out = run(root)
    assert rc != 0, out
    assert "WRITTEN-IN-PLACE problems: 1" in out, out
    assert "the selection rule finds" in out, out


def test_a_new_schema_set_reaches_the_contract_without_being_listed_anywhere(tmp_path):
    """DERIVED, not listed. Adding a set to `schemas/` must put it under the
    contract with no edit here and none in the checker."""
    root = make_repo(tmp_path)
    _write(os.path.join(root, "schemas", "V_theta", "index.json"), "{}\n")
    rc, out = run(root)
    assert rc != 0, out
    assert "V_theta" in out, out
    assert "UNSERVED" in out


# --------------------------------------------------------------------------
# 3. THE MUTATIONS -- break the checker, prove the check was doing the work
# --------------------------------------------------------------------------

def test_stubbing_the_comparison_to_always_equal_makes_the_stale_finding_vanish(tmp_path):
    """THE MUTATION THAT MATTERS.

    `same_bytes` is the single function every byte-level verdict goes through.
    Stub it to return True unconditionally -- the shape of `partitions_hold ->
    return True` -- and the tool prints a clean, confident, WRONG report on a
    tree it has just been shown to be stale. This test asserts BOTH halves:
    that the real function finds it, and that the stub does not. Without the
    second half, `test_a_stale_served_file_reddens` could be passing for some
    reason other than the comparison."""
    root = make_repo(tmp_path)
    _write(os.path.join(root, "schemas", "V_eta_coverage_ledger.json"),
           '{"rows": 102, "changed": true}\n')

    rc_real, out_real = run(root)
    assert rc_real != 0 and "STALE -- served bytes differ from the source: 1" in out_real

    saved = w.same_bytes
    try:
        w.same_bytes = lambda a, b: True          # the mutation
        rc_stub, out_stub = run(root)
    finally:
        w.same_bytes = saved

    assert rc_stub == 0, (
        "the comparison was stubbed to 'always equal' and the tool STILL "
        "failed -- so the stale finding is not coming from the comparison, and "
        f"this suite is not testing what it claims:\n{out_stub}")
    assert "STALE -- served bytes differ from the source: 0" in out_stub
    # and the control: with the stub removed it finds it again
    rc_again, _ = run(root)
    assert rc_again != 0


def test_stubbing_the_pairing_to_pair_nothing_does_not_produce_a_clean_report(tmp_path):
    """The second way a checker goes quiet: not by mis-comparing, but by
    pairing nothing and therefore comparing nothing. Stub `source_of` to return
    None for everything and every served file becomes UNPAIRABLE -- which
    FAILS, loudly, instead of printing 'STALE: 0'."""
    root = make_repo(tmp_path)
    saved = w.source_of
    try:
        w.source_of = lambda *_a, **_k: None       # the mutation
        rc, out = run(root)
    finally:
        w.source_of = saved
    assert rc != 0, out
    assert "UNPAIRABLE" in out
    assert " 0 paired with a generator source" in out.replace("             ", " "), out


def test_deleting_the_zero_served_guard_would_make_an_empty_tree_pass(tmp_path):
    """Why the guard is a guard. With no served files there is nothing to
    compare, so every finding list is legitimately empty -- and without the
    explicit zero check the tool would reach its OK line. The assertion is on
    the FINDINGS being empty, which is what makes the separate guard the only
    thing standing between an empty tree and a pass."""
    root = make_repo(tmp_path)
    import shutil
    shutil.rmtree(os.path.join(root, "web", "public"))
    _rc, out = run(root)
    for empty in ("STALE -- served bytes differ from the source: 0",
                  "ORPHANED -- served, but the source no longer exists: 0",
                  "UNPAIRABLE -- served, produced by nothing this tool can find: 0"):
        assert empty in out, out
    assert "NOT SYNCED" in out


# --------------------------------------------------------------------------
# 4. the contract really is read out of the sync script
# --------------------------------------------------------------------------

def test_the_contract_moves_when_the_sync_script_moves(tmp_path):
    """Rename the served ledger in the script and the checker follows it. A
    hand-kept copy of the mapping would not, and would then grade the tree
    against a contract nobody follows -- the same drift one level up."""
    root = make_repo(tmp_path)
    copies, _inplace, set_root = w.read_contract(root)
    assert copies["coverage.json"] == "V_eta_coverage_ledger.json"
    assert set_root == "schemas"

    moved = SYNC_JS.replace('"coverage.json"', '"ledger.json"')
    root2 = make_repo(tmp_path / "b", sync_js=moved)
    copies2, _i2, _s2 = w.read_contract(root2)
    assert "coverage.json" not in copies2
    assert copies2["ledger.json"] == "V_eta_coverage_ledger.json"


def test_a_generated_viewer_input_the_contract_stops_serving_is_a_HOLE(tmp_path):
    """The contract can go wrong by SHRINKING, and a shrunken contract makes
    the served copy stop updating rather than go stale -- so a byte comparison
    would report nothing. The ledger and the decision families are named here
    because both are produced by tools/gates.py and read by a panel."""
    root = make_repo(tmp_path, sync_js=SYNC_JS.replace(
        'const decisionsSrc = resolve(schemasDir, "V_eta_decisions.json");', ""))
    rc, out = run(root)
    assert rc != 0, out
    assert "CONTRACT HOLES" in out
    assert "V_eta_decisions.json exists and the contract serves no copy of it" in out, out


def test_a_file_a_TOOL_writes_into_public_is_paired_with_that_tool(tmp_path):
    """Discovery, not a list. A generator that writes straight into `public/`
    -- `tools/gen_class_walkthrough.py` does -- must be FOUND by basename and
    its served file delegated to that tool's own `--check`, rather than
    reported as unexplained (which would red the gate on somebody else's
    correctly-generated file)."""
    root = make_repo(tmp_path)
    _write(os.path.join(root, "web", "public", "widget.json"), "{}\n")
    _write(os.path.join(root, "tools", "gen_widget.py"),
           "import sys\n"
           "OUT = 'web/public/widget.json'\n"
           "if '--check' in sys.argv:\n"
           "    print('OK')\n"
           "    sys.exit(0)\n"
           "open(OUT, 'w').write('{}')\n")
    rc, out = run(root)
    assert rc == 0, out
    assert "WRITTEN BY A TOOL -- freshness delegated to the generator: 1" in out, out
    assert "tools/gen_widget.py --check   OK" in out, out


def test_a_tool_that_only_MENTIONS_the_file_in_a_comment_is_not_its_generator(tmp_path):
    """A LIVE FALSE POSITIVE, not a hypothetical.

    `tools/gates.py` names `web/public/class_walkthrough.json` in a comment
    explaining why the step's path precondition is the subtree and not its
    parent. A bare substring search over `tools/*.py` therefore found TWO
    generators for one served file and failed the run as AMBIGUOUS -- a red
    gate whose cause was a sentence. Naming a file and writing it are different
    things."""
    root = make_repo(tmp_path)
    _write(os.path.join(root, "web", "public", "widget.json"), "{}\n")
    _write(os.path.join(root, "tools", "gen_widget.py"),
           "import sys\n"
           "OUT = 'web/public/widget.json'\n"
           "open(OUT, 'w').write('{}')\n"
           "if '--check' in sys.argv:\n    sys.exit(0)\n")
    # THE FIXTURE MUST BE A WRITER OF SOMETHING ELSE. Its first draft only
    # printed, so the write-idiom filter rejected it and this test passed
    # without ever exercising the comment rule -- proved by mutating
    # `_mentions_in_code` to `return True`, which the suite then did not catch.
    # `tools/gates.py`, the real false positive, is exactly this shape: it
    # writes plenty and names the served file only in a sentence.
    _write(os.path.join(root, "tools", "talks_about_it.py"),
           "# this tool explains why web/public/widget.json is special\n"
           "# but it never writes it\n"
           "with open('some/other/file.txt', 'w') as fh:\n"
           "    fh.write('public')\n")
    tools_, _ = w.find_generator(root, "widget.json")
    assert tools_ == [os.path.join("tools", "gen_widget.py")], tools_
    rc, out = run(root)
    assert rc == 0, out
    assert "AMBIGUOUS" not in out, out


def test_two_real_writers_are_reported_as_AMBIGUOUS_rather_than_guessed(tmp_path):
    """When the answer genuinely is not unique, say so. Picking one would make
    the freshness verdict depend on filename ordering."""
    root = make_repo(tmp_path)
    _write(os.path.join(root, "web", "public", "widget.json"), "{}\n")
    for name in ("gen_a.py", "gen_b.py"):
        _write(os.path.join(root, "tools", name),
               "OUT = 'web/public/widget.json'\n"
               "open(OUT, 'w').write('{}')\n")
    rc, out = run(root)
    assert rc != 0, out
    assert "AMBIGUOUS" in out, out


def test_a_tool_written_file_reddens_when_that_tools_own_check_fails(tmp_path):
    """Delegation is not a pass. If the generator says its output is stale,
    this gate says so too."""
    root = make_repo(tmp_path)
    _write(os.path.join(root, "web", "public", "widget.json"), "{}\n")
    _write(os.path.join(root, "tools", "gen_widget.py"),
           "import sys\n"
           "OUT = 'web/public/widget.json'\n"
           "if '--check' in sys.argv:\n"
           "    print('FAIL: widget.json is STALE')\n"
           "    sys.exit(1)\n"
           "open(OUT, 'w').write('{}')\n")
    rc, out = run(root)
    assert rc != 0, out
    assert "FAIL exit=1" in out, out
    assert "GENERATOR --check FAILED" in out or "widget.json" in out


# --------------------------------------------------------------------------
# 5. the wiring
# --------------------------------------------------------------------------

def test_the_gate_is_in_the_chain_after_everything_it_compares(tmp_path):
    """Grade the copies before their sources are regenerated and the comparison
    is against yesterday's artifacts -- a pass that means nothing."""
    assert "check_web_assets_fresh" in g.BY_NAME
    pos = {n: i for i, n in enumerate(g.ORDER)}
    for producer in ("build_v_eta", "coverage", "status_board"):
        assert pos[producer] < pos["check_web_assets_fresh"], (
            f"{producer} writes something the viewer serves a copy of and must "
            "run first")


def test_the_gates_edges_for_this_step_are_substantiated():
    """Same standard as every other edge: the checker's own source must contain
    the literal that proves it reads the artifact."""
    mine = [e for e in g.EDGES if e.consumer == "check_web_assets_fresh"]
    # 3 -> 5 on 2026-08-12. The count is a canary, and it fired exactly as
    # intended: `gen_class_walkthrough` and `tenet_map` were wired into the
    # chain as generators, and each gained an edge into this gate. The three
    # originals (build_v_eta, coverage, status_board) produce artifacts the
    # sync COPIES into public/; the two new ones WRITE into public/ directly,
    # so this gate cannot compare them against a source and delegates to each
    # tool's own --check -- which is worth nothing unless the generator ran
    # first, hence the edge.
    #
    # Bumping this number is the intended response ONLY because the edges below
    # are then re-substantiated one by one. The number alone would be a rubber
    # stamp; the loop is what makes it a check.
    assert len(mine) == 5, [f"{e.producer}->{e.consumer}" for e in mine]
    for e in mine:
        ok, detail = e.substantiated(REPO_ROOT)
        assert ok, f"{e.producer} -> {e.consumer}: {detail}"


def test_the_step_declares_the_path_it_needs_rather_than_failing_on_a_runner():
    """The copied tree is gitignored and is produced by `npm run build`, so a
    CI checkout has none of it. The step declares that dependency, so `--ci`
    reports it as NOT RUNNABLE HERE -- named and counted -- instead of failing
    for a reason that has nothing to do with the change under test."""
    s = g.BY_NAME["check_web_assets_fresh"]
    assert s.needs_paths == [os.path.join("web", "public", "schemas")]
    assert s.kind == "gate"
    assert not s.writes, "a gate that writes would be able to skip its dependents"


def test_the_precondition_is_the_synced_subtree_and_not_its_parent():
    """MEASURED, not assumed, and the measurement is why the marker moved.

    `web/public/class_walkthrough.json` is TRACKED, so `web/public` itself
    EXISTS in a bare checkout while none of the 904 copied paths do. Keying the
    precondition on the parent would let this gate run on a runner and report
    every copied path as UNSERVED -- a red build whose only cause is that the
    sync has not run, which on a runner is correct behaviour. So the marker is
    the sync script's own `publicSchemas` root, and this test fails the day
    that stops being true in either direction."""
    def tracked(path):
        p = subprocess.run(["git", "-C", REPO_ROOT, "ls-files", path],
                           capture_output=True, text=True, check=True)
        return [ln for ln in p.stdout.splitlines() if ln.strip()]

    parent, marker = tracked("web/public"), tracked("web/public/schemas")
    print(f"DENOMINATOR: {len(parent)} tracked file(s) under web/public, "
          f"{len(marker)} of them under web/public/schemas")
    assert not marker, (
        "web/public/schemas is now TRACKED, so a CI checkout would have the "
        "copied tree and the NOT-RUNNABLE-HERE precondition is no longer "
        f"justified: {marker[:5]}")
    s = g.BY_NAME["check_web_assets_fresh"]
    assert s.needs_paths == [os.path.join("web", "public", "schemas")]


@pytest.mark.parametrize("flag", ["--ci"])
def test_ci_reports_the_step_as_not_runnable_rather_than_passed(tmp_path, flag):
    """The distinction this repository insists on: not runnable is COUNTED and
    NAMED, and is never rendered as a pass. Driven through the real driver with
    the step's path precondition pointed at something that does not exist."""
    import contextlib
    import io
    s = g.BY_NAME["check_web_assets_fresh"]
    saved = s.needs_paths
    try:
        s.needs_paths = [os.path.join("web", "public-does-not-exist")]
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = g.main([flag, "--only", "check_web_assets_fresh"])
        out = buf.getvalue()
    finally:
        s.needs_paths = saved
    assert "NOT-RUNNABLE" in out, out
    assert "not runnable here" in out, out
    assert "NOT evidence they would pass" in out, out
    assert rc == 0, out


def test_without_ci_the_step_is_attempted_rather_than_quietly_dropped():
    """A developer running the chain on a machine with no synced tree must SEE
    the failure. Only `--ci` converts the absence into a report."""
    import contextlib
    import io
    s = g.BY_NAME["check_web_assets_fresh"]
    saved_paths, saved_argv = s.needs_paths, s.argv
    try:
        s.needs_paths = [os.path.join("web", "public-does-not-exist")]
        s.argv = [sys.executable, "-c", "import sys; sys.exit(1)"]
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = g.main(["--only", "check_web_assets_fresh"])
        out = buf.getvalue()
    finally:
        s.needs_paths, s.argv = saved_paths, saved_argv
    assert rc != 0, out
    assert "NOT RUNNABLE HERE" in out, out
    assert "will be ATTEMPTED anyway" in out, out
