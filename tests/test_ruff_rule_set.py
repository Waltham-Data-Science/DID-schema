"""The lint gate's RULE SET is evidence, and evidence needs a denominator.

WHAT WENT WRONG, 2026-08-11. `.github/workflows/tests.yml` pins ruff and says
why: "An unpinned linter is an unreviewed dependency that can fail the build on
someone else's release schedule. Pinned FORWARD to the version that caught these
-- not back to the one that missed them."

Pinning the BINARY does not pin the CONTRACT. The repository declared no rules
at all, so the gate was whatever that release happened to enable by default, and
a default set moves in BOTH directions:

        DENOMINATOR: 2 ruff versions, every enabled rule read from
                     `ruff check tests --show-settings`
        0.15.8       59 rules enabled
        0.16.2      413 rules enabled
        gained      372
        LOST         18   E401 E402 E701 E702 E703 E711 E712 E713 E714 E721
                          E731 E741 E742 E743 F403 F405 F406 F722

Four of those eighteen were being violated in `tests/` at that moment and no
gate saw it, because CI ran the version that had stopped looking. F405 is "name
may be undefined, or defined from a star import"; E711/E712 are `== None` /
`== True`; E721 compares types with `==`. None of that is style.

The rule set now lives in `pyproject.toml` (`[tool.ruff.lint] extend-select`),
and these tests hold it there:

  * the enabled set may GROW freely and may NEVER SHRINK below the baseline --
    a rule leaving ruff's defaults is now a red gate rather than a silent gap;
  * the ruff actually running must be the version `tests.yml` pins, because a
    rule-set measurement taken with a different binary is a measurement of a
    different tool. This is the failure that hid the eighteen: the only machine
    running the older ruff was a developer's, and it was the one telling the
    truth.
"""
import pathlib
import re
import shutil
import subprocess

REPO = pathlib.Path(__file__).resolve().parent.parent
BASELINE = pathlib.Path(__file__).resolve().parent / "ruff_rule_baseline.txt"
WORKFLOW = REPO / ".github" / "workflows" / "tests.yml"

RULE = re.compile(r"\(([A-Z]+[0-9]+)\)")


def _pinned_version():
    """The ruff version `tests.yml` installs -- parsed, never hard-coded here."""
    text = WORKFLOW.read_text(encoding="utf-8")
    hits = re.findall(r"pip install ruff==([0-9]+(?:\.[0-9]+)*)", text)
    assert hits, (
        f"{WORKFLOW.name} pins no ruff version, so this test has nothing to "
        "compare the running binary against and would pass vacuously")
    # MORE THAN ONE PIN IS FINE; MORE THAN ONE *VERSION* IS NOT. The `chain`
    # job and both `older-pythons` legs each install ruff, and the whole point
    # of this file is that two machines must not run different linters -- so
    # the check is that every pin in the workflow names the SAME version.
    assert len(set(hits)) == 1, (
        f"DENOMINATOR: {len(hits)} `pip install ruff==` line(s) in "
        f"{WORKFLOW.name}, {len(set(hits))} distinct version(s): "
        f"{sorted(set(hits))}. Jobs in one workflow must not lint with "
        "different ruffs -- that is the divergence this file exists to stop, "
        "arriving inside a single file instead of across two machines.")
    return hits[0]


def _ruff():
    path = shutil.which("ruff")
    assert path, (
        "no `ruff` on PATH. This is NOT a skip: the lint gate is one of the "
        "eighteen steps `tools/gates.py` runs, and a gate that cannot run has "
        "not passed. Install the version pinned in .github/workflows/tests.yml.")
    return path


def _enabled_rules():
    out = subprocess.run(
        [_ruff(), "check", "tests", "--no-cache", "--show-settings"],
        cwd=REPO, capture_output=True, text=True, check=False).stdout
    block = re.search(r"^linter\.rules\.enabled = \[(.*?)^\]", out,
                      re.DOTALL | re.MULTILINE)
    assert block, (
        "`ruff check --show-settings` printed no `linter.rules.enabled` block. "
        "The output format changed; this test is reporting nothing and must be "
        "repaired rather than deleted.")
    return set(RULE.findall(block.group(1)))


def test_the_running_ruff_is_the_pinned_one():
    pinned = _pinned_version()
    actual = subprocess.run([_ruff(), "--version"], capture_output=True,
                            text=True, check=False).stdout.split()[-1]
    assert actual == pinned, (
        f"DENOMINATOR: 1 pin read from {WORKFLOW.name}, 1 binary on PATH.\n"
        f"  pinned in CI : {pinned}\n"
        f"  on PATH here : {actual}  ({_ruff()})\n"
        "These MUST agree. On 2026-08-11 they did not, and the two versions "
        "disagreed in both directions at once: the local one reported four "
        "errors CI could not see, while CI reported 266 the local one could "
        "not. Either state alone reads as 'the other machine is broken'.\n"
        f"  fix: pip install ruff=={pinned}")


def test_the_enabled_rule_set_never_shrinks():
    baseline = {ln.strip() for ln in BASELINE.read_text(encoding="utf-8").split()
                if ln.strip()}
    enabled = _enabled_rules()
    missing = sorted(baseline - enabled)
    print(f"DENOMINATOR: {len(baseline)} rule(s) in the baseline, "
          f"{len(enabled)} enabled now, {len(enabled - baseline)} added since")
    assert not missing, (
        f"DENOMINATOR: {len(baseline)} baseline rule(s), {len(enabled)} enabled.\n"
        f"{len(missing)} RULE(S) STOPPED BEING ENFORCED: {missing}\n"
        "A rule leaving the enabled set is exactly how eighteen checks were "
        "lost silently when ruff was bumped 0.15.8 -> 0.16.2. If the drop is "
        "intended, say so by editing tests/ruff_rule_baseline.txt in the same "
        "commit -- do not widen this test.")


def test_the_rule_set_is_declared_and_not_inherited_from_a_default():
    """`select`/`extend-select` must be present -- defaults are not a decision."""
    text = (REPO / "pyproject.toml").read_text(encoding="utf-8")
    assert re.search(r"^\[tool\.ruff\.lint\]", text, re.MULTILINE), (
        "pyproject.toml declares no [tool.ruff.lint] section, so the lint gate "
        "is whatever the installed ruff enables by default. That is a release "
        "note, not a decision, and it is how the eighteen went missing.")
    assert re.search(r"^(extend-)?select\s*=", text, re.MULTILINE), (
        "[tool.ruff.lint] is present but names no rules. Declare them.")


def test_the_baseline_covers_the_eighteen_that_were_lost():
    """The specific rules 0.16.2 dropped are IN the baseline, by name.

    Written as a literal list rather than a count: a count would still pass if
    these eighteen were swapped for eighteen others.
    """
    lost = {"E401", "E402", "E701", "E702", "E703", "E711", "E712", "E713",
            "E714", "E721", "E731", "E741", "E742", "E743", "F403", "F405",
            "F406", "F722"}
    baseline = {ln.strip() for ln in BASELINE.read_text(encoding="utf-8").split()
                if ln.strip()}
    print(f"DENOMINATOR: {len(lost)} rule(s) dropped from ruff's defaults at "
          f"0.16.2, {len(baseline)} in the baseline")
    assert lost <= baseline, sorted(lost - baseline)
