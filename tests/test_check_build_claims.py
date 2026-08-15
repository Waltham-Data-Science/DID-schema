"""Tests for tools/check_build_claims.py.

THE ADJUDICATION TESTS ARE THE POINT, NOT THE HAPPY PATH. This tool's first
draft convicted 10 comments and 7 of the verdicts were false -- signature names
are ordinary words in the files being scanned (`epoch` matched most of
`epochMint.m`), and a plan filename two lines away from an unrelated sentence
convicted it. A gate crying wolf trains its readers to bump digits without
looking, which is how a real drift gets bumped away too.

So each narrowing carries a test that FAILS IF THE NARROWING IS REMOVED, and
each one is written from the real line that produced the false positive rather
than from an invented one. A test written from the same premise as the code
cannot catch the code; these are written from the OUTPUT that was wrong.
"""

import importlib.util
import os
import re
import subprocess
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = os.path.join(REPO_ROOT, "tools", "check_build_claims.py")



def _load():
    spec = importlib.util.spec_from_file_location("check_build_claims", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = _load()


def _adjudicate(line, item_plans=None, rows=None, signed_plans=None):
    """Run one comment line through the tool's own rules.

    Mirrors the adjudication in scan() over a single claim so a case can be
    stated as the LINE that produced it."""
    item_plans = item_plans or {45: ["V_eta_data_body_model_plan.md"],
                                30: ["V_eta_recording_observation_plan.md"]}
    rows = rows or {45: "OPEN", 30: "OPEN", 29: "COMPLETED"}
    signed_plans = signed_plans or {"V_eta_data_body_model_plan.md": 1,
                                    "V_eta_recording_observation_plan.md": 2,
                                    "V_eta_epoch_plan.md": 1,
                                    "V_eta_OPEN_WORK.md": 2}
    verdicts = []
    unsigned = bool(MOD.UNSIGNED_RE.search(line))
    notbuilt = bool(MOD.NOTBUILT_RE.search(line))
    if unsigned:
        for plan in MOD.PLAN_RE.findall(line):
            if signed_plans.get(plan) and plan != "V_eta_OPEN_WORK.md":
                verdicts.append(f"plan {plan}")
        for m in MOD.UNSIGNED_RE.finditer(line):
            for im in MOD.ITEM_RE.finditer(line):
                gap = (im.start() - m.end()) if im.start() >= m.end() \
                    else (m.start() - im.end())
                if gap > MOD.ITEM_ADJACENCY:
                    continue
                for plan in item_plans.get(int(im.group(1)), ()):
                    if signed_plans.get(plan):
                        verdicts.append(f"item #{im.group(1)} -> {plan}")
    if notbuilt:
        for num in MOD.ITEM_RE.findall(line):
            if rows.get(int(num)) == "COMPLETED":
                verdicts.append(f"completed #{num}")
    return verdicts


# ---------------------------------------------------------------- true hits

@pytest.mark.parametrize("line", [
    # element_epoch.m:48 and :50, verbatim -- the two labels that were the
    # STATED REASON the epoch dissolution had not been built.
    "%                                                                 #45, UNSIGNED)",
    "%                                  (raw-recording model, #30, UNSIGNED)",
])
def test_an_item_labelled_unsigned_whose_plan_is_signed_is_caught(line):
    assert _adjudicate(line), (
        "the tool must convict a comment labelling a signed item UNSIGNED; "
        f"got no verdict for {line.strip()!r}")


def test_a_claim_naming_a_signed_plan_document_is_caught():
    line = "%   blocked on V_eta_data_body_model_plan.md, which is UNSIGNED"
    assert _adjudicate(line)


# --------------------------------------------------- the narrowings, pinned

def test_a_family_name_alone_is_not_evidence():
    """`epoch` is a signature name AND an ordinary word in epochMint.m.

    The first draft keyed on normalised family names and convicted this line,
    which is about SYNTHETIC IDS and says nothing about the epoch family's
    signedness. Removing the narrowing brings the false positive back."""
    line = "%   THE SYNTHETIC IDS ARE SKIPPED -- AND THAT IS AN UNSIGNED DECISION"
    assert not _adjudicate(line), (
        "a bare family name must not convict; signature names are ordinary "
        "words in the trees being scanned")


def test_the_word_signature_outside_governance_vocabulary_is_not_a_claim():
    """resolveLawnPlateSubjects.m:350 -- a TABLE signature, not a TEAM-SIGN-OFF.

    The first draft matched bare `no signature`. The word is not owned by this
    project; MATLAB function signatures use it too."""
    line = "%   table WAS recognised, that matched no signature. Zero rows recognised"
    assert not _adjudicate(line)


def test_an_item_number_in_a_subordinate_clause_is_not_the_subject():
    """element_epoch.m:89, verbatim.

    `NOT SIGNED` is about fork A1. `#30` is 28 characters away in a different
    clause and IS signed. Convicting here would report a true sentence as
    false, which is worse than missing a stale one: it teaches the reader to
    override the gate."""
    line = "%       NOT SIGNED, and is gated on #30 besides."
    assert not _adjudicate(line), (
        "co-occurrence on one line is not aboutness; the adjacency bound "
        f"(ITEM_ADJACENCY={MOD.ITEM_ADJACENCY}) must exclude this")


def test_a_plan_named_two_lines_away_does_not_convict():
    """resolveValidIntervals.m:103 -- proximity is not aboutness.

    Adjudication is SAME LINE ONLY. The +-2 window exists for the exemption
    marker and for rule C, never for evidence."""
    line = "%   up as an answer. NOT SIGNED, NOT AGREED. No TEAM-SIGN-OFF line exists for"
    assert not _adjudicate(line)


def test_a_not_built_claim_about_an_open_item_is_left_alone():
    """The record AGREES with the comment, so there is nothing to report.

    This is the refusal that keeps the tool honest: it never decides whether
    something is built. #30 is signed twice and its assembler is live, and its
    row is still OPEN -- so the tool stays silent rather than inferring."""
    line = "%          the attached recording archives -> a <modality>_observation  #30, NOT BUILT"
    assert not _adjudicate(line)


def test_a_not_built_claim_about_a_completed_item_is_caught():
    line = "%   the ensemble second pass (#29) is NOT BUILT"
    assert _adjudicate(line) == ["completed #29"]


# ------------------------------------------------------------ the live run

def test_the_tool_runs_clean_and_reports_a_real_denominator():
    """End to end, against the real siblings.

    DENOMINATORS ASSERTED RATHER THAN PRINTED. A sweep that walked no files, or
    whose signature index came back empty, would print `0 CONTRADICTED` and
    exit 0 -- the silentLoss defect. Both are asserted non-zero."""
    proc = subprocess.run([sys.executable, TOOL, "--enforce"],
                          capture_output=True, text=True, cwd=REPO_ROOT,
                          check=False)
    out = proc.stdout
    assert "UNREADABLE" not in out, (
        "a sibling comment tree was not scanned, so this run covers less than "
        f"it claims:\n{out}")
    files = int(re.search(r"DENOMINATOR: (\d+) \.m file\(s\) walked", out).group(1))
    sigs = int(re.search(r"signature index: (\d+) distinct", out).group(1))
    claims = int(re.search(r"BUILD-STATE CLAIMS LOCATED: (\d+)", out).group(1))
    assert files > 0, "no .m files walked -- the check is vacuous"
    assert sigs > 0, "empty signature index -- nothing could be contradicted"
    assert claims > 0, (
        "no build-state claim was located anywhere in either sibling. If that "
        "is genuinely true the vocabulary should be relaxed deliberately, not "
        "left silently matching nothing")
    assert proc.returncode == 0, (
        f"comments contradict the signed record:\n{out}")
