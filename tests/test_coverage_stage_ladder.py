"""The DERIVED per-class stage, and proof that the classifier still classifies.

WHY THIS FILE EXISTS
--------------------
"How far has this v1 class actually got?" was a judgement assembled by hand from
five fields of `V_eta_coverage_ledger.json`. Five people assemble it five ways
and none of them is re-derivable next week. `tools/coverage.py` now DERIVES a
stage 0-5 per class, and this file is the thing that keeps it honest.

THE TWO FAILURES THIS FILE IS AIMED AT, both of which print identically to a
healthy result:

  1. A CLASSIFIER THAT HAS STOPPED CLASSIFYING. `partitions_hold -> return True`
     cost this repository 76 green tests. A stage function that returns a
     constant, or one that finds every rung satisfied, produces a clean rollup
     and an empty anomaly list -- exactly what "everything is fine" looks like.
  2. A RUNG SATISFIED BY AN EMPTY LIST. `schema_targets_missing == []` is TRUE
     for all 102 rows, and for 77 of them it is true because no target was ever
     named. A stage 2 that reads that list alone reports 102 of 102 classes
     "targets built" and is wrong about three quarters of them.

HOW THESE TESTS AVOID BEING WRITTEN FROM THE SAME PREMISE AS THE CODE
---------------------------------------------------------------------
CLAUDE.md: "A TEST WRITTEN FROM THE SAME PREMISE AS THE CODE CANNOT CATCH THE
CODE" -- three tests in this repository had to be INVERTED rather than updated.
So:

  * the ladder rule ("highest rung with every rung below it satisfied") is
    RE-IMPLEMENTED here, in `_independent_reached`, from the rung states alone.
    It never calls coverage.py's `stage_ladder` to decide what the answer is;
  * every stage-1 `yes` is re-verified by OPENING the cited plan document and
    parsing for a `TEAM-SIGN-OFF` line with a parser written in this file, not
    by calling `check_decision_citations`;
  * the counts that matter are PINNED as literals, so deleting rows from the
    tool's tables fails rather than silently redefining "correct";
  * MUTATION TESTS run at the end. Each one damages the classifier in a
    specific, named way and asserts that at least one invariant above turns
    RED. A mutation that cannot redden means today's data cannot distinguish
    it, and the fix is a constructed fixture -- which is why two of the
    mutations below run against fixtures rather than the live ledger.
"""
import copy
import json
import os
import re
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))

import coverage  # noqa: E402

LEDGER_JSON = os.path.join(REPO_ROOT, "schemas", "V_eta_coverage_ledger.json")
LEDGER_MD = os.path.join(REPO_ROOT, "schemas", "V_eta_coverage_ledger.md")

# PINNED, DELIBERATELY. The v1 source universe is 102 (NOT 87, NOT 91) and a
# classifier whose denominator quietly shrinks is the failure every operating
# rule in CLAUDE.md is written against.
V1_UNIVERSE = 102

# The rungs whose states are `yes`/`n/a` let the climb continue. Written out
# here rather than imported so a change to coverage.py's tuple is a test
# failure and not a silent redefinition.
PASSING = ("yes", "n/a")

# A minimal well-formed row, used where the live 102 cannot exhibit a condition.
# No row in today's ledger is malformed, so "an unclassifiable class is reported
# rather than dropped" is UNOBSERVABLE on live data -- and asserting "0
# unclassifiable" and calling it covered is the shape of every all-zero census
# this project has shipped. Hence a constructed fixture.
FIXTURE_ROW = {
    "v1_class": "fixture_class", "targets": [], "decided_targets": [],
    "second_pass": [], "no_target_reason": None, "decided_signoff": None,
    "no_target_signoff": None, "decided_targets_source": None,
    "build_state": {"schema_targets_named": 0, "schema_targets_built": [],
                    "schema_targets_missing": [],
                    "migrator_emits_decided_targets": False,
                    "has_per_class_migrator": True},
}


def _ledger():
    with open(LEDGER_JSON) as fh:
        return json.load(fh)


def _rows():
    return _ledger()["rows"]


def _reclassify(rows, evidence=None):
    """Re-derive the stage for each row, in memory, from coverage.py."""
    return [dict(r, stage=coverage.stage_ladder(r, evidence)) for r in rows]


def _independent_reached(stage):
    """The ladder rule, re-implemented from the rung states alone.

    This is the second opinion. If it ever disagrees with `stage["reached"]`,
    one of the two is wrong and the test says so rather than trusting the tool.
    """
    reached = 0
    for rung in stage["ladder"]:
        if rung["state"] in PASSING:
            reached = rung["stage"]
        else:
            break
    return reached


def _signoff_lines(plan):
    """TEAM-SIGN-OFF lines in a plan document -- parser written HERE.

    HTML comments are stripped for the reason status_board.py strips them: a
    document that tells the team HOW to sign off carries the marker inside a
    comment, and counting it lets instruction text validate a citation.
    """
    path = os.path.join(REPO_ROOT, "schemas", plan)
    if not os.path.exists(path):
        return []
    with open(path) as fh:
        text = re.sub(r"<!--.*?-->", "", fh.read(), flags=re.DOTALL)
    return [ln for ln in text.splitlines()
            if ln.lstrip().startswith("TEAM-SIGN-OFF")]


# ===========================================================================
# THE INVARIANTS. Each raises AssertionError when violated, and each is used
# BOTH as a test (against the live ledger) and as a mutation detector.
# ===========================================================================

def check_every_row_is_placed(rows):
    """DENOMINATOR FIRST: every row is either placed or reported unplaceable."""
    assert len(rows) == V1_UNIVERSE, (
        f"the v1 source universe is {V1_UNIVERSE}; the ledger carries {len(rows)}")
    for r in rows:
        st = r.get("stage")
        assert isinstance(st, dict), f"{r['v1_class']}: no derived stage at all"
        if st["unclassifiable"]:
            assert st["unclassifiable_why"], (
                f"{r['v1_class']}: unclassifiable with no reason -- a row that "
                "cannot be placed must say why, or it is indistinguishable "
                "from one that was dropped")
            assert st["reached"] is None
            continue
        assert st["reached"] in (0, 1, 2, 3, 4, 5), (
            f"{r['v1_class']}: reached={st['reached']!r} is not a stage")
        assert [rung["stage"] for rung in st["ladder"]] == [1, 2, 3, 4, 5], (
            f"{r['v1_class']}: the ladder must carry all five rungs, in order")


def check_exactly_one_stage_and_no_promotion(rows):
    """The highest rung, and ONLY if every rung below it is satisfied."""
    for r in rows:
        st = r["stage"]
        if st["unclassifiable"]:
            continue
        want = _independent_reached(st)
        assert st["reached"] == want, (
            f"{r['v1_class']}: tool says stage {st['reached']}, the ladder "
            f"states say {want}")
        for rung in st["ladder"]:
            if rung["stage"] <= st["reached"]:
                assert rung["state"] in PASSING, (
                    f"{r['v1_class']}: reached stage {st['reached']} while rung "
                    f"{rung['stage']} is `{rung['state']}` -- a class may not "
                    "climb past a rung it does not satisfy")


def check_the_ladder_still_discriminates(rows):
    """A classifier that answers the same thing for everything is not one.

    Two separate ways to be dead, because a mutation can produce either: one
    stage for every class, or one state for every rung.
    """
    placed = [r["stage"] for r in rows if not r["stage"]["unclassifiable"]]
    reached = {st["reached"] for st in placed}
    assert len(reached) > 1, (
        f"every classified row landed on stage {reached} -- the classifier is "
        "constant, which prints exactly like a healthy result")
    for n in (1, 2, 3, 4):
        states = {rung["state"] for st in placed for rung in st["ladder"]
                  if rung["stage"] == n}
        assert len(states) > 1, (
            f"rung {n} returned `{states}` for all {len(placed)} rows -- a rung "
            "with one answer measures nothing")


def check_stage2_is_not_satisfied_by_an_empty_list(rows):
    """THE ANTI-VACUITY RULE, in the one place it was going to be broken."""
    for r in rows:
        st = r["stage"]
        if st["unclassifiable"]:
            continue
        rung = st["ladder"][1]
        assert rung["stage"] == 2
        named = r["build_state"]["schema_targets_named"]
        if rung["state"] == "yes":
            assert named > 0, (
                f"{r['v1_class']}: stage 2 satisfied while NO target class is "
                "named. `schema_targets_missing == []` is true of every row; "
                "reading it alone reports 102 of 102 classes built")
            assert not r["build_state"]["schema_targets_missing"]
        if named == 0 and r.get("no_target_reason") != "dissolved":
            assert rung["state"] == "not measured", (
                f"{r['v1_class']}: names no target and is not signed to "
                f"dissolve, so stage 2 is unreadable, not `{rung['state']}`")


def check_stage1_yes_rests_on_a_real_signoff(rows):
    """Every stage-1 `yes` is re-verified against the document it cites."""
    for r in rows:
        st = r["stage"]
        if st["unclassifiable"] or st["ladder"][0]["state"] != "yes":
            continue
        cite = r.get("decided_signoff") or r.get("no_target_signoff")
        assert cite, (
            f"{r['v1_class']}: stage 1 is `yes` with no transcribed sign-off "
            "on the row -- a decision cannot be inferred from absence")
        frag = cite.get("signoff_fragment")
        hits = [ln for ln in _signoff_lines(cite["document"]) if frag in ln]
        assert hits, (
            f"{r['v1_class']}: no TEAM-SIGN-OFF line in {cite['document']} "
            f"contains {frag!r}")
        assert r.get("no_target_reason") != "disputed", (
            f"{r['v1_class']}: a DISPUTED record is not a decided disposition")


def check_na_requires_a_signed_dissolution(rows):
    """`n/a` may only be issued where a signed line says the rung cannot apply."""
    for r in rows:
        st = r["stage"]
        if st["unclassifiable"]:
            continue
        for rung in st["ladder"]:
            if rung["state"] != "n/a":
                continue
            assert r.get("no_target_reason") == "dissolved", (
                f"{r['v1_class']}: rung {rung['stage']} is `n/a` without a "
                "signed dissolution. `n/a` lets a class climb, so issuing one "
                "from an empty list is a promotion produced by absence")
            assert r.get("no_target_signoff"), (
                f"{r['v1_class']}: dissolution with no citation")


def check_stage5_is_not_measured_without_evidence(rows):
    """NOT MEASURED, in those words. Never `no`, never silently skipped."""
    for r in rows:
        st = r["stage"]
        if st["unclassifiable"]:
            continue
        rung = st["ladder"][4]
        assert rung["stage"] == 5
        assert rung["state"] == "not measured", (
            f"{r['v1_class']}: stage 5 is `{rung['state']}` with no corpus "
            "report in reach. `no corpus proved it` and `nobody looked` are "
            "different facts")
        assert "NOT MEASURED" in rung["why"], (
            f"{r['v1_class']}: stage 5 must say NOT MEASURED in those words; "
            f"it says {rung['why']!r}")


def check_rollup_accounts_for_every_row(rollup, total):
    """RULE 5: the rollup states its denominator and loses nobody."""
    assert rollup["classified"] + rollup["unclassifiable"] == total, (
        f"{rollup['classified']} classified + {rollup['unclassifiable']} "
        f"unclassifiable != {total} rows -- a row was dropped")
    assert sum(rollup["by_stage_reached"].values()) == rollup["classified"], (
        "the stage histogram does not sum to the number of classified rows")
    assert len(rollup["unclassifiable_rows"]) == rollup["unclassifiable"]


ALL_ROW_CHECKS = (
    check_every_row_is_placed,
    check_exactly_one_stage_and_no_promotion,
    check_the_ladder_still_discriminates,
    check_stage2_is_not_satisfied_by_an_empty_list,
    check_stage1_yes_rests_on_a_real_signoff,
    check_na_requires_a_signed_dissolution,
    check_stage5_is_not_measured_without_evidence,
)


class TestTheCommittedLedger(unittest.TestCase):
    """The artifact a human and the web viewer read."""

    def test_every_row_carries_a_derived_stage(self):
        check_every_row_is_placed(_rows())

    def test_exactly_one_stage_and_never_a_promotion(self):
        check_exactly_one_stage_and_no_promotion(_rows())

    def test_the_ladder_discriminates(self):
        check_the_ladder_still_discriminates(_rows())

    def test_stage_2_is_not_satisfied_by_an_empty_target_list(self):
        check_stage2_is_not_satisfied_by_an_empty_list(_rows())

    def test_every_stage_1_yes_quotes_a_real_team_signoff(self):
        check_stage1_yes_rests_on_a_real_signoff(_rows())

    def test_n_a_is_only_ever_issued_on_a_signed_dissolution(self):
        check_na_requires_a_signed_dissolution(_rows())

    def test_stage_5_reports_NOT_MEASURED_and_never_no(self):
        check_stage5_is_not_measured_without_evidence(_rows())

    def test_the_rollup_reports_its_denominator(self):
        led = _ledger()
        check_rollup_accounts_for_every_row(
            led["summary"]["stage_rollup"], led["summary"]["total"])

    def test_the_committed_stage_is_what_the_tool_derives(self):
        # A hand-edited ledger is the thing the whole "derived, never hand-set"
        # claim rests on. Re-derive and compare.
        for r in _rows():
            again = coverage.stage_ladder(r, coverage.CORPUS_SCAN)
            self.assertEqual(again["reached"], r["stage"]["reached"],
                             f"{r['v1_class']}: committed stage differs from a "
                             "fresh derivation")

    def test_the_markdown_rollup_matches_the_json(self):
        # The defect this repository keeps paying for is a RENDERING that
        # contradicts the data it renders.
        rollup = _ledger()["summary"]["stage_rollup"]
        with open(LEDGER_MD) as fh:
            md = fh.read()
        total = _ledger()["summary"]["total"]
        self.assertIn(
            f'**Stage rollup.** DENOMINATOR: {rollup["classified"]} of {total} '
            f'row(s) classified, {rollup["unclassifiable"]} UNCLASSIFIABLE', md)
        for n in range(6):
            row = [ln for ln in md.splitlines()
                   if ln.startswith(f"| {n} | {coverage.STAGE_NAMES[n]} |")]
            self.assertEqual(len(row), 1, f"stage {n} must have one rollup row")
            self.assertIn(f"| {rollup['by_stage_reached'][str(n)]} |", row[0])
        self.assertIn("Stage 5 is NOT MEASURED", md)

    def test_the_anomaly_count_names_its_two_kinds(self):
        an = _ledger()["summary"]["stage_rollup"]["anomalies"]
        self.assertEqual(an["total"], len(an["rows"]))
        self.assertEqual(an["classes"], len({a["v1_class"] for a in an["rows"]}))
        self.assertEqual(
            sum(an["by_kind"].values()), an["total"],
            "every anomaly is either over a FAILED rung or over an UNMEASURED "
            "one; a third bucket would be unaccounted for")
        for a in an["rows"]:
            self.assertIn(a["kind"], ("over_failed", "over_unmeasured"))

    def test_the_one_contradiction_is_named(self):
        # PINNED. `ngrid` is the single row whose lower rung has POSITIVE
        # evidence against it (V_eta_image_model_plan.md states two
        # dispositions) while a higher rung holds -- a migrator consumes it.
        # If this list changes, a real condition changed and someone must look.
        an = _ledger()["summary"]["stage_rollup"]["anomalies"]
        failed = sorted({a["v1_class"] for a in an["rows"]
                         if a["kind"] == "over_failed"})
        self.assertEqual(failed, ["ngrid"])


class TestUnclassifiableRowsAreReportedNotDropped(unittest.TestCase):
    """A row that cannot be placed must survive into the output.

    CONSTRUCTED FIXTURE, deliberately: no row in today's 102 is malformed, so
    this condition is unobservable on live data. A weaker claim would be to
    assert "0 unclassifiable" and call it covered -- which is the shape of
    every all-zero census this project has shipped.
    """

    BASE = FIXTURE_ROW

    def test_a_row_with_no_build_state_is_reported(self):
        row = copy.deepcopy(self.BASE)
        del row["build_state"]
        st = coverage.stage_ladder(row)
        self.assertTrue(st["unclassifiable"])
        self.assertIsNone(st["reached"])
        self.assertIn("build_state", st["unclassifiable_why"])

    def test_a_row_with_a_wrong_typed_field_is_reported(self):
        row = copy.deepcopy(self.BASE)
        row["build_state"]["schema_targets_missing"] = "none"
        st = coverage.stage_ladder(row)
        self.assertTrue(st["unclassifiable"])
        self.assertIn("schema_targets_missing", st["unclassifiable_why"])

    def test_an_unclassifiable_row_reaches_the_rollup_by_name(self):
        good = copy.deepcopy(self.BASE)
        bad = copy.deepcopy(self.BASE)
        bad["v1_class"] = "broken_class"
        bad["build_state"]["has_per_class_migrator"] = False
        del bad["second_pass"]        # now REACHED, so the row cannot be placed
        rows = _reclassify([good, bad])
        rollup = coverage._stage_rollup(rows, None)
        check_rollup_accounts_for_every_row(rollup, len(rows))
        self.assertEqual(rollup["unclassifiable"], 1)
        self.assertEqual([u["v1_class"] for u in rollup["unclassifiable_rows"]],
                         ["broken_class"])
        self.assertEqual(rollup["classified"], 1)


class TestStage5BecomesComputable(unittest.TestCase):
    """Stage 5 is CODE ALREADY WRITTEN, waiting on an input.

    These fixtures are the contract: the day a real `<corpus>-summary.json` is
    in reach, the stage is computed and no new code is needed. They also pin
    the three outcomes apart, because collapsing "proven", "refuted" and "no
    documents of this class" is the same defect one level down.
    """

    def _report(self, tmp, name, by_class, **over):
        rep = {"corpus": name, "quarantine_count": 0, "fragment_count": 0,
               "reference_integrity": {"orphan_count": 0, "orphans": []},
               "silent_loss": {"empty_required_dependency": []},
               "source_census": {"total_docs": sum(by_class.values()),
                                 "by_class": by_class}}
        rep.update(over)
        with open(os.path.join(tmp, name + "-summary.json"), "w") as fh:
            json.dump(rep, fh)

    def _row(self, cls="image_stack", targets=("image_observation",)):
        return {"v1_class": cls, "targets": list(targets), "decided_targets": [],
                "second_pass": [], "no_target_reason": None,
                "decided_signoff": None, "no_target_signoff": None,
                "decided_targets_source": None,
                "build_state": {"schema_targets_named": 0,
                                "schema_targets_built": [],
                                "schema_targets_missing": [],
                                "migrator_emits_decided_targets": False,
                                "has_per_class_migrator": True}}

    def setUp(self):
        import tempfile
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_no_roots_is_not_measured_and_says_what_is_missing(self):
        ev = coverage.load_corpus_evidence([])
        self.assertFalse(ev["measured"])
        self.assertIn(coverage.CORPUS_REPORTS_ENV, ev["why"])

    def test_a_named_root_that_does_not_exist_is_reported_not_silent(self):
        ev = coverage.load_corpus_evidence([os.path.join(self.tmp, "nope")])
        self.assertFalse(ev["measured"])
        self.assertEqual(len(ev["denominator"]["roots_missing"]), 1)

    def test_reports_are_found_RECURSIVELY(self):
        # CLAUDE.md, corpus run #3: a one-level glob matched neither copy of
        # the reports and the digest printed NO CORPUS REPORTS FOUND after an
        # hour of green.
        deep = os.path.join(self.tmp, "corpus-reports", "tests", "corpus-reports")
        os.makedirs(deep)
        self._report(deep, "Dab", {"imagestack": 3})
        ev = coverage.load_corpus_evidence([self.tmp])
        self.assertTrue(ev["measured"], ev.get("why"))
        self.assertEqual(ev["denominator"]["files_matched"], 1)

    def test_a_clean_corpus_proves_the_class(self):
        self._report(self.tmp, "Dab", {"image_stack": 4563})
        ev = coverage.load_corpus_evidence([self.tmp])
        st = coverage.stage_ladder(self._row(), ev)
        rung = st["ladder"][4]
        self.assertEqual(rung["state"], "yes", rung["why"])
        self.assertIn("4563 document(s)", rung["why"])

    def test_a_class_absent_from_every_corpus_is_NOT_MEASURED_not_clean(self):
        # THE CORPORA ARE A SAMPLE OF DATASETS, NOT THE UNIVERSE.
        self._report(self.tmp, "Dab", {"something_else": 10})
        ev = coverage.load_corpus_evidence([self.tmp])
        rung = coverage.stage_ladder(self._row(), ev)["ladder"][4]
        self.assertEqual(rung["state"], "not measured")
        self.assertIn("SAMPLE", rung["why"])

    def test_a_quarantine_refutes_it(self):
        self._report(self.tmp, "Dab", {"image_stack": 10}, quarantine_count=7)
        ev = coverage.load_corpus_evidence([self.tmp])
        rung = coverage.stage_ladder(self._row(), ev)["ladder"][4]
        self.assertEqual(rung["state"], "no")
        self.assertIn("quarantined", rung["why"])

    def test_an_empty_required_edge_on_a_target_refutes_it(self):
        self._report(self.tmp, "Dab", {"image_stack": 4563},
                     silent_loss={"empty_required_dependency": [
                         {"count": 4563, "class_name": "image_observation",
                          "edge_name": "subject_id"}]})
        ev = coverage.load_corpus_evidence([self.tmp])
        rung = coverage.stage_ladder(self._row(), ev)["ladder"][4]
        self.assertEqual(rung["state"], "no")
        self.assertIn("empty required edge", rung["why"])

    def test_a_missing_counter_is_a_fault_not_a_zero(self):
        # A report with no orphan block is the state EVERY corpus report was in
        # until 2026-08-12. Silence there must not read as 0 orphans.
        self._report(self.tmp, "Dab", {"image_stack": 10})
        with open(os.path.join(self.tmp, "Dab-summary.json")) as fh:
            rep = json.load(fh)
        del rep["reference_integrity"]
        with open(os.path.join(self.tmp, "Dab-summary.json"), "w") as fh:
            json.dump(rep, fh)
        ev = coverage.load_corpus_evidence([self.tmp])
        rung = coverage.stage_ladder(self._row(), ev)["ladder"][4]
        self.assertEqual(rung["state"], "no")
        self.assertIn("NOT a zero", rung["why"])

    def test_a_report_with_no_source_census_is_not_measured(self):
        with open(os.path.join(self.tmp, "Bare-summary.json"), "w") as fh:
            json.dump({"corpus": "Bare", "quarantine_count": 0}, fh)
        ev = coverage.load_corpus_evidence([self.tmp])
        self.assertFalse(ev["measured"])
        self.assertIn("source_census", ev["why"])

    def test_stage_5_yes_lets_a_class_reach_stage_5(self):
        # The rung is wired into the ladder, not just computed beside it.
        self._report(self.tmp, "Dab", {"epochid": 12})
        ev = coverage.load_corpus_evidence([self.tmp])
        row = self._row(cls="epochid", targets=())
        row["no_target_reason"] = "dissolved"
        row["no_target_signoff"] = {"document": "V_eta_epoch_plan.md",
                                    "signoff_fragment": "epochid is DROPPED"}
        row["build_state"]["has_per_class_migrator"] = True
        st = coverage.stage_ladder(row, ev)
        self.assertEqual(st["reached"], 5, st["ladder"])


# ===========================================================================
# MUTATION TESTS. Damage the classifier; prove an invariant turns red.
# ===========================================================================
#
# A green suite over a dead classifier is this repository's most expensive
# recurring bug, so every mutation below is RUN, and its outcome is asserted.
# `_assert_reddens` fails loudly when a mutation produces no failure at all --
# that is the "the data cannot distinguish it" case, and it is a defect in the
# test set, not a licence to weaken the claim.


class _Mutation:
    """Swap module attributes on `coverage` for the duration of a block."""

    def __init__(self, **attrs):
        self.attrs = attrs
        self.saved = {}

    def __enter__(self):
        for k, v in self.attrs.items():
            self.saved[k] = getattr(coverage, k)
            setattr(coverage, k, v)
        return self

    def __exit__(self, *exc):
        for k, v in self.saved.items():
            setattr(coverage, k, v)
        return False


class TestMutationsRedden(unittest.TestCase):

    def _assert_reddens(self, mutation, rows=None, checks=ALL_ROW_CHECKS):
        """Run every invariant against the mutated classifier; require a red."""
        rows = rows if rows is not None else _rows()
        with mutation:
            mutated = _reclassify(copy.deepcopy(rows))
            caught = []
            for check in checks:
                try:
                    check(mutated)
                except AssertionError as exc:
                    caught.append((check.__name__, str(exc).splitlines()[0]))
        self.assertTrue(caught, (
            "MUTATION PRODUCED NO FAILURE. Today's data cannot distinguish it, "
            "so the invariants above do not cover this damage. The fix is a "
            "constructed fixture, not a weaker claim."))
        return caught

    def test_collapsing_two_adjacent_stages_reddens(self):
        # Stage 2 answers stage 3's question. Every class with a migrator now
        # reads "its target classes are built", including the 77 that name no
        # target at all.
        caught = self._assert_reddens(
            _Mutation(_stage2_targets_built=coverage._stage3_consumed))
        self.assertIn("check_stage2_is_not_satisfied_by_an_empty_list",
                      [c[0] for c in caught])

    def test_a_stage_function_returning_a_constant_YES_reddens(self):
        const = lambda row: ("yes", "constant")  # noqa: E731
        caught = self._assert_reddens(_Mutation(
            _stage1_decided=const, _stage2_targets_built=const,
            _stage3_consumed=const, _stage4_emits_decided=const,
            _stage5_corpus=lambda row, ev: ("yes", "constant")))
        names = [c[0] for c in caught]
        self.assertIn("check_the_ladder_still_discriminates", names)
        self.assertIn("check_stage2_is_not_satisfied_by_an_empty_list", names)
        self.assertIn("check_stage1_yes_rests_on_a_real_signoff", names)

    def test_a_stage_function_returning_a_constant_NOT_MEASURED_reddens(self):
        # The other way to be dead: everything reads stage 0, which looks like
        # an honest "we have not got far" and is in fact a broken instrument.
        const = lambda row: ("not measured", "constant")  # noqa: E731
        caught = self._assert_reddens(_Mutation(
            _stage1_decided=const, _stage2_targets_built=const,
            _stage3_consumed=const, _stage4_emits_decided=const))
        self.assertIn("check_the_ladder_still_discriminates",
                      [c[0] for c in caught])

    def test_dropping_the_satisfies_every_stage_below_rule_reddens(self):
        # `reached` becomes the highest rung that is `yes` regardless of order,
        # which promotes 86 classes over a rung nobody read and promotes `ngrid`
        # over a rung whose record contradicts itself.
        real = coverage.stage_ladder

        def promoted(row, evidence=None):
            st = real(row, evidence)
            if st["unclassifiable"]:
                return st
            best = [r["stage"] for r in st["ladder"] if r["state"] in PASSING]
            st["reached"] = max(best) if best else 0
            st["reached_name"] = coverage.STAGE_NAMES[st["reached"]]
            return st

        caught = self._assert_reddens(_Mutation(stage_ladder=promoted))
        self.assertIn("check_exactly_one_stage_and_no_promotion",
                      [c[0] for c in caught])

    def test_treating_an_ABSENT_signoff_as_a_decision_reddens(self):
        # The operating-rule-3 mutation: absence promoted to a finding. 94 rows
        # would read "decided" on the strength of nothing.
        real = coverage._stage1_decided

        def optimistic(row):
            state, why = real(row)
            return ("yes", why) if state == "not measured" else (state, why)

        caught = self._assert_reddens(_Mutation(_stage1_decided=optimistic))
        self.assertIn("check_stage1_yes_rests_on_a_real_signoff",
                      [c[0] for c in caught])

    def test_issuing_n_a_without_a_signed_dissolution_reddens(self):
        # `n/a` lets a class climb, so it is the quiet way to fake progress.
        real = coverage._stage2_targets_built

        def loose(row):
            if not row["build_state"]["schema_targets_named"]:
                return ("n/a", "nothing named")
            return real(row)

        caught = self._assert_reddens(_Mutation(_stage2_targets_built=loose))
        self.assertIn("check_na_requires_a_signed_dissolution",
                      [c[0] for c in caught])

    def test_defaulting_stage_5_to_NO_reddens(self):
        caught = self._assert_reddens(
            _Mutation(_stage5_corpus=lambda row, ev: ("no", "not proven")))
        self.assertIn("check_stage5_is_not_measured_without_evidence",
                      [c[0] for c in caught])

    def test_swallowing_an_unclassifiable_row_reddens(self):
        # CONSTRUCTED FIXTURE, because no live row is malformed -- the mutation
        # is invisible on today's 102 and that is a fact about the data, not a
        # reason to drop the claim.
        rows = [dict(TestUnclassifiableRowsAreReportedNotDropped.BASE)]
        broken = copy.deepcopy(rows[0])
        broken["v1_class"] = "broken_class"
        del broken["build_state"]
        rows.append(broken)

        real = coverage.stage_ladder

        def swallowing(row, evidence=None):
            st = real(row, evidence)
            if st["unclassifiable"]:
                st = dict(st, unclassifiable=False, reached=0,
                          reached_name=coverage.STAGE_NAMES[0],
                          unclassifiable_why=None,
                          ladder=[{"stage": n, "name": coverage.STAGE_NAMES[n],
                                   "state": "not measured", "why": "swallowed"}
                                  for n in (1, 2, 3, 4, 5)])
            return st

        with _Mutation(stage_ladder=swallowing):
            mutated = _reclassify(rows)
            rollup = coverage._stage_rollup(mutated, None)
        self.assertEqual(
            rollup["unclassifiable"], 0,
            "precondition: the mutation must actually hide the broken row")
        with self.assertRaises(AssertionError):
            # The invariant that catches it: an unplaceable row must be named,
            # and the honest tool reports it. Re-derive without the mutation and
            # require the two to disagree.
            honest = coverage._stage_rollup(_reclassify(rows), None)
            self.assertEqual(honest["unclassifiable"], rollup["unclassifiable"])

    def test_the_rollup_dropping_a_row_reddens(self):
        rows = _reclassify(copy.deepcopy(_rows()))
        rollup = coverage._stage_rollup(rows, None)
        check_rollup_accounts_for_every_row(rollup, len(rows))
        # Now drop one class from the histogram, as a filtered counter would.
        damaged = copy.deepcopy(rollup)
        damaged["by_stage_reached"]["0"] -= 1
        with self.assertRaises(AssertionError):
            check_rollup_accounts_for_every_row(damaged, len(rows))


if __name__ == "__main__":
    unittest.main()
