"""The DERIVED per-class COMPLETION stage, and proof it still classifies.

WHY THIS FILE EXISTS
--------------------
"How far has this v1 class actually got?" was a judgement assembled by hand from
five fields of `V_eta_coverage_ledger.json`. Five people assemble it five ways
and none of them is re-derivable next week. `tools/coverage.py` DERIVES a stage
per class, and this file is the thing that keeps it honest.

THE RESTRUCTURE OF 2026-08-12, WHICH THIS FILE WAS REWRITTEN FOR RATHER THAN
UPDATED -- and the difference matters, because a test updated in step with the
code it guards is the failure CLAUDE.md names ("A TEST WRITTEN FROM THE SAME
PREMISE AS THE CODE CANNOT CATCH THE CODE"). The ladder used to open with a
GOVERNANCE rung -- `disposition DECIDED` -- and gate every completion rung
behind it, so a class with a working migrator reported stage 0 whenever no
sign-off could be machine-found for it. 95 of 102 rows read "stage 0" while 86
of them had a migrator consuming their documents: a number that measured our
bookkeeping and was read as the migration's progress.

Governance is now a FLAG BESIDE THE STAGE (`row["governance"]`), never a rung,
and the completion ladder is rungs 1..4:

    1  a migrator CONSUMES it                        (fully measured: 86 / 16)
    2  its decided target classes EXIST in the build
    3  the migrator emits THE DECIDED targets
    4  CORPUS-PROVEN                                 (NOT MEASURED, always,
                                                      without a corpus report)

So these invariants assert something they could not assert before: THAT NOTHING
ABOUT A SIGNATURE CAN MOVE A BUILD STAGE.

THE FAILURES THIS FILE IS AIMED AT, all of which print identically to a healthy
result:

  1. A CLASSIFIER THAT HAS STOPPED CLASSIFYING. `partitions_hold -> return True`
     cost this repository 76 green tests. A stage function that returns a
     constant, or one that finds every rung satisfied, produces a clean rollup
     and an empty anomaly list -- exactly what "everything is fine" looks like.
  2. A RUNG SATISFIED BY AN EMPTY LIST. `schema_targets_missing == []` is TRUE
     for all 102 rows, and for 77 of them it is true because no target was ever
     named. A rung that reads that list alone reports 102 of 102 classes
     "targets built" and is wrong about three quarters of them.
  3. TWO DIFFERENT SILENCES PRINTING THE SAME NUMBER. "capped at 0 by an unread
     rung" and "nothing has happened to this class" were one bucket of 95.

HOW THESE TESTS AVOID BEING WRITTEN FROM THE SAME PREMISE AS THE CODE
---------------------------------------------------------------------
  * the ladder rule ("highest rung with every rung below it satisfied") is
    RE-IMPLEMENTED here, in `_independent_reached`, from the rung states alone.
    It never calls coverage.py's `stage_ladder` to decide what the answer is;
  * governance's independence from the stage is proved by MUTATING the
    governance fields on every row and requiring every `reached` to be
    unchanged -- a structural claim, not a reading of the code;
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

# The completion rungs, written out here rather than imported so a change to
# coverage.py's tuple is a test failure and not a silent redefinition. A FIFTH
# entry appearing here is how a governance rung would come back.
COMPLETION_RUNGS = [1, 2, 3, 4]

# The rungs whose states are `yes`/`n/a` let the climb continue. Written out
# here rather than imported for the same reason.
PASSING = ("yes", "n/a")

# A minimal well-formed row, used where the live 102 cannot exhibit a condition.
# No row in today's ledger is malformed, so "an unclassifiable class is reported
# rather than dropped" is UNOBSERVABLE on live data -- and asserting "0
# unclassifiable" and calling it covered is the shape of every all-zero census
# this project has shipped. Hence a constructed fixture.
FIXTURE_ROW = {
    "v1_class": "fixture_class", "veta_class": None, "targets": [],
    "decided_targets": [], "second_pass": [], "no_target_reason": None,
    "decided_signoff": None, "no_target_signoff": None,
    "decided_targets_source": None, "decided_by_family": None,
    "governance_gap": None, "families_naming_this_class": [],
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


def _with_governance(rows):
    """Rows carrying the governance flag, for the rollup's sake."""
    for r in rows:
        r["governance"] = coverage.governance_state(r)
    return rows


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
        assert st["reached"] in (0, 1, 2, 3, 4), (
            f"{r['v1_class']}: reached={st['reached']!r} is not a stage")
        assert [rung["stage"] for rung in st["ladder"]] == COMPLETION_RUNGS, (
            f"{r['v1_class']}: the ladder must carry the four COMPLETION rungs "
            "in order and nothing else -- a fifth entry is how a governance "
            "rung comes back into the chain")


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
    stage for every class, or one state for every rung. Rung 4 is EXCLUDED from
    the second check: with no corpus report in reach it is `not measured` on
    every row BY DESIGN, and demanding variety there would demand the tool
    invent a corpus verdict.
    """
    placed = [r["stage"] for r in rows if not r["stage"]["unclassifiable"]]
    reached = {st["reached"] for st in placed}
    assert len(reached) > 1, (
        f"every classified row landed on stage {reached} -- the classifier is "
        "constant, which prints exactly like a healthy result")
    for n in (1, 2, 3):
        states = {rung["state"] for st in placed for rung in st["ladder"]
                  if rung["stage"] == n}
        assert len(states) > 1, (
            f"rung {n} returned `{states}` for all {len(placed)} rows -- a rung "
            "with one answer measures nothing")


def check_targets_rung_is_not_satisfied_by_an_empty_list(rows):
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
                f"{r['v1_class']}: the targets rung is satisfied while NO "
                "target class is named. `schema_targets_missing == []` is true "
                "of every row; reading it alone reports 102 of 102 built")
            assert not r["build_state"]["schema_targets_missing"]
        if named == 0 and r.get("no_target_reason") != "dissolved":
            assert rung["state"] == "not measured", (
                f"{r['v1_class']}: names no target and is not signed to "
                f"dissolve, so rung 2 is unreadable, not `{rung['state']}`")


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


def check_corpus_rung_is_not_measured_without_evidence(rows):
    """NOT MEASURED, in those words. Never `no`, never silently skipped."""
    for r in rows:
        st = r["stage"]
        if st["unclassifiable"]:
            continue
        rung = st["ladder"][3]
        assert rung["stage"] == 4
        assert rung["state"] == "not measured", (
            f"{r['v1_class']}: the corpus rung is `{rung['state']}` with no "
            "corpus report in reach. `no corpus proved it` and `nobody looked` "
            "are different facts, and rendering the second as a failure is the "
            "defect silentLoss shipped for two days")
        assert "NOT MEASURED" in rung["why"], (
            f"{r['v1_class']}: the corpus rung must say NOT MEASURED in those "
            f"words; it says {rung['why']!r}")


def check_governance_cannot_move_a_build_stage(rows):
    """THE RESTRUCTURE, ASSERTED STRUCTURALLY RATHER THAN READ OFF THE CODE.

    Every governance field on every row is replaced with its most flattering
    and its least flattering value in turn, and the completion stage must not
    move on any row. A governance rung reinstated anywhere in `stage_ladder`
    fails this immediately -- which is the point, because that is the change
    that would quietly reintroduce "95 classes at stage 0".
    """
    for flavour in ("flattering", "damning"):
        for r in rows:
            probe = copy.deepcopy(r)
            if flavour == "flattering":
                probe["decided_signoff"] = {"document": "X.md",
                                            "signoff_fragment": "f"}
                probe["decided_by_family"] = {
                    "family": "f", "document": "X.md", "line": 1,
                    "signoff": "s", "matched_on": "v1_class",
                    "matched_name": r["v1_class"], "conflict": []}
                probe["governance_gap"] = None
            else:
                probe["decided_signoff"] = None
                probe["decided_by_family"] = None
                probe["governance_gap"] = coverage.GAP_NO_FAMILY
            again = coverage.stage_ladder(probe, coverage.CORPUS_SCAN)
            assert again["reached"] == r["stage"]["reached"], (
                f"{r['v1_class']}: changing GOVERNANCE ({flavour}) moved the "
                f"build stage {r['stage']['reached']} -> {again['reached']}. "
                "Decidedness and builtness are orthogonal; a signature may "
                "never cap or lift a build stage")


def check_capped_and_untouched_are_distinguishable(rows):
    """"Capped by an unread rung" and "nothing happened" must not be one number."""
    for r in rows:
        st = r["stage"]
        if st["unclassifiable"]:
            continue
        yes = [x["stage"] for x in st["ladder"] if x["state"] == "yes"]
        na = [x["stage"] for x in st["ladder"] if x["state"] == "n/a"]
        highest = max(yes) if yes else 0
        assert st["highest_rung_satisfied_independently"] == highest, (
            f"{r['v1_class']}: highest satisfied rung is {highest}, the row "
            f"says {st['highest_rung_satisfied_independently']}")
        assert st["capped"] == (highest > st["reached"]), (
            f"{r['v1_class']}: `capped` disagrees with the two numbers it is "
            "derived from")
        assert st["nothing_built"] == (not yes)
        assert st["nothing_satisfied"] == (not yes and not na), (
            f"{r['v1_class']}: GENUINELY UNTOUCHED must mean no rung is "
            "satisfied AND none is excused by a signed dissolution -- a "
            "dissolution is a fact about the class, not silence about it")


def check_rollup_leads_with_a_fully_measured_rung(rollup):
    """The first figure must be one with no unmeasured rows.

    A reader's first question is "how much is left". Leading with a stage
    histogram whose top bucket was produced by unfindable paperwork answered a
    different question in the voice of that one.
    """
    hl = rollup["headline"]
    assert hl["rung"] == 1 and hl["name"] == coverage.STAGE_NAMES[1]
    assert hl["not measured"] == 0, (
        "the headline rung reports "
        f'{hl["not measured"]} unmeasured row(s) -- it may only lead if it has '
        "an answer on every row")
    assert hl["yes"] + hl["no"] + hl["n/a"] + hl["not measured"] \
        == hl["denominator"], "the headline does not account for every row"
    assert hl["yes"] > 0
    # The headline must be a BUILD fact, and must come first. A governance
    # count leading here is the regression this check exists for.
    keys = list(rollup)
    assert keys.index("headline") < keys.index("by_stage_reached"), (
        "the headline must come before the stage histogram")
    assert keys.index("headline") < keys.index("governance"), (
        "the rollup must lead with what is BUILT, never with governance")


def check_rollup_accounts_for_every_row(rollup, total):
    """RULE 5: the rollup states its denominator and loses nobody."""
    assert rollup["classified"] + rollup["unclassifiable"] == total, (
        f"{rollup['classified']} classified + {rollup['unclassifiable']} "
        f"unclassifiable != {total} rows -- a row was dropped")
    assert sum(rollup["by_stage_reached"].values()) == rollup["classified"], (
        "the stage histogram does not sum to the number of classified rows")
    assert len(rollup["unclassifiable_rows"]) == rollup["unclassifiable"]
    cap = rollup["capped"]
    assert cap["genuinely_untouched"] == len(cap["genuinely_untouched_rows"]), (
        "the untouched COUNT and the untouched NAMES disagree -- one of them "
        "is being maintained and the other quoted")
    assert cap["rows"] == len(cap["row_names"])


ALL_ROW_CHECKS = (
    check_every_row_is_placed,
    check_exactly_one_stage_and_no_promotion,
    check_the_ladder_still_discriminates,
    check_targets_rung_is_not_satisfied_by_an_empty_list,
    check_na_requires_a_signed_dissolution,
    check_corpus_rung_is_not_measured_without_evidence,
    check_governance_cannot_move_a_build_stage,
    check_capped_and_untouched_are_distinguishable,
)


class TestSupersclassOnlySourcesGetTheirEmissionCredited(unittest.TestCase):
    """Shape (1) of row 107: the emitter is ANOTHER class's migrator.

    `filter` is superclass-only -- no document of that class exists, its content
    rides as a block on a `pyraview` document -- so no migrator can ever be
    named after it and rung 3's question is unanswerable in the form it asks.
    Its fold is real and tested (`private/jFrequencyFilter.m`, called at
    `pyraview.m:89`), and the ladder reported it as unbuilt.

    WHY THIS IS AUTHORED AND NOT DERIVED, which is the invariant worth pinning:
    9 rows have a decided target that some other row's migrator emits, and 8 of
    them name a SHARED target (`sampled_body` has 6 emitters) where the standing
    attribution limit forbids any conclusion. An inference would credit 8 rows
    on no evidence to reach the 1 that deserves it. So the credit requires an
    explicit `emitted_by` in the target map, and a row without one gets nothing.
    """

    def setUp(self):
        self.led = _ledger()
        self.rows = {r["v1_class"]: r for r in self.led["rows"]}

    def test_filter_reaches_stage_3_on_the_authored_emitter(self):
        r = self.rows["filter"]
        rung3 = r["stage"]["ladder"][2]
        self.assertEqual(rung3["state"], "yes", rung3["why"])
        self.assertIn("SUPERCLASS-ONLY", rung3["why"])
        self.assertIn("pyraview", rung3["why"])
        self.assertGreaterEqual(r["stage"]["reached"], 3)

    def test_the_credit_is_DISTINGUISHABLE_from_a_migrator_of_its_own(self):
        """A reader must never mistake this for the class's own migrator."""
        why = self.rows["filter"]["stage"]["ladder"][2]["why"]
        self.assertIn("no migrator can be named after this class", why)
        self.assertNotIn("`build_state.migrator_emits_decided_targets`", why)

    def test_an_emitted_by_naming_the_wrong_target_credits_NOTHING(self):
        rows = _with_governance(
            _reclassify(copy.deepcopy(_rows()), coverage.CORPUS_SCAN))
        hit = 0
        for r in rows:
            bs = r.get("build_state") or {}
            if bs.get("emitted_by_migrator"):
                hit += 1
                bs["emitted_by_targets"] = ["something_else_entirely"]
                bs["emitted_by_emits_decided_targets"] = False
                state, _why = coverage._rung_emits_decided(r)
                self.assertNotEqual(state, "yes")
        self.assertTrue(hit, "precondition: a row carries an `emitted_by`")

    def test_only_rows_with_an_authored_emitted_by_are_credited(self):
        """The 8 shared-target rows must NOT be swept in."""
        credited = [n for n, r in self.rows.items()
                    if (r.get("build_state") or {}).get(
                        "emitted_by_emits_decided_targets")]
        self.assertEqual(credited, ["filter"])


class TestTheUntouchedBucketCarriesItsReasons(unittest.TestCase):
    """The six names are not six units of work, and the bucket must say so.

    "No rung satisfied" is a fact about the LADDER. Read as a fact about the
    WORK it overstates what is left: three of the six are recorded
    PASSTHROUGHS, where the document is carried through unchanged and no
    per-class migrator is expected at all (`projectvar` is documented in exactly
    those terms). A bare list of names made a settled passthrough and an
    unexamined class identical.

    THE RISK IN THE OTHER DIRECTION IS THE ONE THESE TESTS GUARD. A detail
    block that INVENTED a reason would excuse real work, so every field must be
    copied verbatim from the row, and a row with no recorded disposition must
    show as absent rather than be filled in.
    """

    def setUp(self):
        self.led = _ledger()
        self.cap = self.led["summary"]["stage_rollup"]["capped"]
        self.rows = {r["v1_class"]: r for r in self.led["rows"]}

    def test_every_untouched_row_appears_in_the_detail(self):
        self.assertEqual([d["v1_class"] for d in self.cap["genuinely_untouched_detail"]],
                         self.cap["genuinely_untouched_rows"])

    def test_the_detail_is_COPIED_from_the_row_never_derived(self):
        for d in self.cap["genuinely_untouched_detail"]:
            row = self.rows[d["v1_class"]]
            self.assertEqual(d["disposition"], row.get("disposition"),
                             d["v1_class"] + ": disposition was not copied")
            self.assertEqual(d["target_source"], row.get("target_source"),
                             d["v1_class"] + ": target_source was not copied")

    def test_the_passthrough_count_is_the_recorded_value_not_a_judgement(self):
        expected = sum(1 for d in self.cap["genuinely_untouched_detail"]
                       if d["target_source"] == "passthrough")
        self.assertEqual(self.cap["genuinely_untouched_recorded_passthrough"],
                         expected)
        # and it must be a PROPER subset -- if it ever equals the bucket, the
        # bucket has stopped distinguishing anything
        self.assertLess(self.cap["genuinely_untouched_recorded_passthrough"],
                        self.cap["genuinely_untouched"],
                        "every untouched row reads as a passthrough; the "
                        "distinction has gone inert")

    def test_a_missing_disposition_is_shown_as_missing(self):
        """Absence must be visible, not filled in with something plausible."""
        rows = _with_governance(
            _reclassify(copy.deepcopy(_rows()), coverage.CORPUS_SCAN))
        for r in rows:
            r.pop("disposition", None)
        cap = coverage._stage_rollup(rows, None)["capped"]
        self.assertTrue(cap["genuinely_untouched_detail"],
                        "precondition: the fixture has untouched rows")
        for d in cap["genuinely_untouched_detail"]:
            self.assertIsNone(d["disposition"])


class TestTheCommittedLedger(unittest.TestCase):
    """The artifact a human and the web viewer read."""

    def test_every_row_carries_a_derived_stage(self):
        check_every_row_is_placed(_rows())

    def test_exactly_one_stage_and_never_a_promotion(self):
        check_exactly_one_stage_and_no_promotion(_rows())

    def test_the_ladder_discriminates(self):
        check_the_ladder_still_discriminates(_rows())

    def test_the_targets_rung_is_not_satisfied_by_an_empty_list(self):
        check_targets_rung_is_not_satisfied_by_an_empty_list(_rows())

    def test_n_a_is_only_ever_issued_on_a_signed_dissolution(self):
        check_na_requires_a_signed_dissolution(_rows())

    def test_the_corpus_rung_reports_NOT_MEASURED_and_never_no(self):
        check_corpus_rung_is_not_measured_without_evidence(_rows())

    def test_governance_cannot_move_a_build_stage(self):
        check_governance_cannot_move_a_build_stage(_rows())

    def test_capped_and_untouched_are_two_quantities(self):
        check_capped_and_untouched_are_distinguishable(_rows())

    def test_the_rollup_reports_its_denominator(self):
        led = _ledger()
        check_rollup_accounts_for_every_row(
            led["summary"]["stage_rollup"], led["summary"]["total"])

    def test_the_rollup_leads_with_what_is_measured(self):
        check_rollup_leads_with_a_fully_measured_rung(
            _ledger()["summary"]["stage_rollup"])

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
        hl = rollup["headline"]
        self.assertIn(
            f'DENOMINATOR: {hl["denominator"]} of {total} row(s) classified, '
            f'{rollup["unclassifiable"]} UNCLASSIFIABLE', md)
        self.assertIn(
            f'**{hl["yes"]} of {hl["denominator"]} v1 source classes have '
            f'something in the migration that CONSUMES them; {hl["no"]} do '
            "not.**", md)
        for n in range(5):
            row = [ln for ln in md.splitlines()
                   if ln.startswith(f"| {n} | {coverage.STAGE_NAMES[n]} |")]
            self.assertEqual(len(row), 1, f"stage {n} must have one rollup row")
            self.assertIn(f"| {rollup['by_stage_reached'][str(n)]} |", row[0])
        self.assertIn("Stage 4 (CORPUS-PROVEN) is NOT MEASURED", md)

    def test_the_markdown_states_the_untouched_count_separately(self):
        # THE DEFECT: one bucket of 95 rows. The rendered form must carry both
        # quantities, and the untouched rows must be NAMED.
        cap = _ledger()["summary"]["stage_rollup"]["capped"]
        with open(LEDGER_MD) as fh:
            md = fh.read()
        self.assertIn(
            f'**{cap["genuinely_untouched"]} are GENUINELY UNTOUCHED: no rung '
            "is satisfied at all**", md)
        for name in cap["genuinely_untouched_rows"]:
            self.assertIn("`" + name + "`", md)
        self.assertIn(f'{cap["rows"]} are CAPPED', md)

    def test_a_capped_row_and_an_untouched_row_render_differently(self):
        # The two sentences a reader distinguishes them by. If either
        # disappears the numbers are still right and the page is not.
        rows = _rows()
        capped = [r for r in rows if r["stage"].get("capped")]
        untouched = [r for r in rows if r["stage"].get("nothing_satisfied")]
        self.assertTrue(capped and untouched,
                        "precondition: today's ledger holds both kinds")
        for r in capped:
            self.assertIn("highest rung satisfied on its own",
                          coverage._stage_cell(r))
        for r in untouched:
            self.assertIn("nothing above it satisfied either",
                          coverage._stage_cell(r))

    def test_the_untouched_rows_are_the_ones_we_expect(self):
        # PINNED. These have NOTHING built and nothing excused: no migrator, no
        # second pass, no batch post-pass declaring them, no decided target, no
        # signed dissolution. If the list changes, something real changed and
        # someone must look.
        #
        # WAS NINE UNTIL 2026-08-12 AND IS NOW EIGHT: `generic_file` LEFT, and
        # it left because it was never untouched. `did2.convert.foldGenericFiles`
        # folds it into a `term_observation` + an `opaque_body`, and the ladder
        # could not see that -- rung 1 asked only whether a migrator FILE named
        # after the class exists. The pass now DECLARES what it consumes
        # (OPEN_WORK row 107) and the row reads rung 1 `yes`. Nothing about
        # `generic_file` changed; what changed is that the instrument can see
        # the third consumption channel.
        # WAS EIGHT EARLIER THE SAME DAY AND IS NOW SIX: `demoNDI` and
        # `demoNDIMock` LEFT, and unlike `generic_file` they left because
        # something was BUILT. The team collapsed demoNDI/demoNDIMock/mock into
        # one `demo` class on 2026-08-06; only the schema half landed, and the
        # migrator half was written on 2026-08-12
        # (`+migrators_j/demo_ndi.m`, `demo_ndi_mock.m`, shared
        # `private/jDemoFold.m`), 1->1 with `base.id` preserved and `is_mock`
        # FALSE/TRUE respectively. Their curated rows were authored in the same
        # pass, so `targets: ["demo"]` is derived rather than asserted.
        #
        # `mock` STAYS, and that is a measurement rather than an oversight:
        # nothing in NDI ever constructs a bare `mock` document -- over 1,002
        # `.m` files, `ndi.document('mock'`, `newdocument('mock'` and
        # `'isa','mock'` return 0 each, and all 13 quoted `'mock'` literals are
        # something else (a `subject.local_identifier` substring, an email
        # prefix, a path segment, epochfile names, openMINDS object names). A
        # class that cannot have documents needs no migrator.
        # WAS SIX UNTIL 2026-08-13 AND IS NOW FIVE: `session` LEFT, and like the
        # demo pair it left because something was BUILT rather than because the
        # instrument learned to see. `session` had no migrator, and until
        # 2026-08-13 that was CORRECT: it migrated 1:1 with its id preserved and
        # every field carried, so a passthrough said everything there was to say.
        # The signed change gives it work to do -- `reference` is renamed to
        # `local_identifier` (required, matching `subject` and `epoch`) and the
        # three V_zeta inventions `type`/`date`/`purpose` are deleted -- so
        # `+migrators_j/session.m` now exists and rung 1 reads `yes`.
        cap = _ledger()["summary"]["stage_rollup"]["capped"]
        self.assertEqual(cap["genuinely_untouched_rows"], [
            "animalsubject", "base", "imageCollection",
            "imageStack_parameters", "mock"])

    def test_a_signed_dissolution_is_not_counted_as_untouched(self):
        # The rows that separate "nothing built" from "nothing known".
        #
        # WAS THREE UNTIL 2026-08-12 AND IS NOW TWO. `epochid` left this bucket
        # in the direction that matters: `only_excused` means nothing is BUILT
        # and the rungs above are `n/a`, and something IS built --
        # `did2.convert.epochMint` mints one `epoch` per (session, epoch-id
        # string) with the v1 string as its `local_identifier`, which is the
        # mint half of the signed dissolution, in code. It now satisfies rung 1
        # on a declaration, so it is no longer "nothing built".
        cap = _ledger()["summary"]["stage_rollup"]["capped"]
        self.assertEqual(cap["nothing_built_but_excused_rows"],
                         ["stimulus_response",
                          "stimulus_response_scalar_parameters"])
        for name in cap["nothing_built_but_excused_rows"]:
            self.assertNotIn(name, cap["genuinely_untouched_rows"])

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

    def test_the_build_ahead_rows_are_named(self):
        # PINNED, and it is a REAL CONDITION rather than a defect: these four
        # have their decided target class BUILT while nothing consumes them yet
        # -- schema ahead of migrator, which CLAUDE.md records for `app` in its
        # own words ("`software` IS built and shipping ... only the migrator is
        # outstanding"). Under the old governance-gated ladder this condition
        # was invisible: the only anomaly was `ngrid`, and it was one about
        # paperwork.
        an = _ledger()["summary"]["stage_rollup"]["anomalies"]
        failed = sorted({a["v1_class"] for a in an["rows"]
                         if a["kind"] == "over_failed"})
        self.assertEqual(failed, ["app", "ensemble", "projectvar",
                                  "stimulus_parameter_table"])

    def test_the_no_target_understatement_is_named_not_hidden(self):
        # Rungs 2 and 3 are unreadable for every row with no recorded target.
        # That is a hole in the RECORD and must be reported as its own
        # quantity, with the join's contribution stated as the zero it is.
        ntr = _ledger()["summary"]["stage_rollup"]["no_target_recorded"]
        rows = _rows()
        want = sorted(r["v1_class"] for r in rows
                      if not r["build_state"]["schema_targets_named"])
        self.assertEqual(ntr["row_names"], want)
        self.assertEqual(ntr["rows"], len(want))
        self.assertEqual(ntr["moved_by_the_signature_join"], 0)
        self.assertIn("signs a FAMILY", ntr["why_the_join_moves_none_of_them"])
        with open(LEDGER_MD) as fh:
            self.assertIn(f'**{ntr["rows"]} of {ntr["denominator"]} rows record '
                          "NO TARGET CLASS**", fh.read())


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
        rows = _with_governance(_reclassify([good, bad]))
        rollup = coverage._stage_rollup(rows, None)
        check_rollup_accounts_for_every_row(rollup, len(rows))
        self.assertEqual(rollup["unclassifiable"], 1)
        self.assertEqual([u["v1_class"] for u in rollup["unclassifiable_rows"]],
                         ["broken_class"])
        self.assertEqual(rollup["classified"], 1)


class TestCorpusRungBecomesComputable(unittest.TestCase):
    """The corpus rung is CODE ALREADY WRITTEN, waiting on an input.

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
        row = copy.deepcopy(FIXTURE_ROW)
        row.update({"v1_class": cls, "targets": list(targets)})
        return row

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
        rung = st["ladder"][3]
        self.assertEqual(rung["state"], "yes", rung["why"])
        self.assertIn("4563 document(s)", rung["why"])

    def test_a_class_absent_from_every_corpus_is_NOT_MEASURED_not_clean(self):
        # THE CORPORA ARE A SAMPLE OF DATASETS, NOT THE UNIVERSE.
        self._report(self.tmp, "Dab", {"something_else": 10})
        ev = coverage.load_corpus_evidence([self.tmp])
        rung = coverage.stage_ladder(self._row(), ev)["ladder"][3]
        self.assertEqual(rung["state"], "not measured")
        self.assertIn("SAMPLE", rung["why"])

    def test_a_quarantine_refutes_it(self):
        self._report(self.tmp, "Dab", {"image_stack": 10}, quarantine_count=7)
        ev = coverage.load_corpus_evidence([self.tmp])
        rung = coverage.stage_ladder(self._row(), ev)["ladder"][3]
        self.assertEqual(rung["state"], "no")
        self.assertIn("quarantined", rung["why"])

    def test_an_empty_required_edge_on_a_target_refutes_it(self):
        self._report(self.tmp, "Dab", {"image_stack": 4563},
                     silent_loss={"empty_required_dependency": [
                         {"count": 4563, "class_name": "image_observation",
                          "edge_name": "subject_id"}]})
        ev = coverage.load_corpus_evidence([self.tmp])
        rung = coverage.stage_ladder(self._row(), ev)["ladder"][3]
        self.assertEqual(rung["state"], "no")
        self.assertIn("empty required edge", rung["why"])

    def test_a_missing_counter_is_NOT_MEASURED_neither_a_zero_nor_a_refutation(self):
        # INVERTED 2026-08-12, not updated. This test used to assert `no`, and
        # it was WRONG IN ITS ASSERTION WHILE RIGHT IN ITS COMMENT: silence must
        # not read as 0 orphans -- and it must not read as a refutation either.
        #
        # It was written from the same premise as the code, so it could not
        # catch it, and the two agreed all the way into production: corpus run
        # 31587869672 reported 10 classes FAILED, every one of them because
        # PRED's report -- a hard 0-quarantine GATE run, not a discovery run --
        # carries no `reference_integrity` block at all. Nothing had failed.
        #
        # The third state is the whole point of the state set. See
        # tests/test_coverage_corpus_verdict.py, which is where the three-way
        # discrimination is pinned; this case stays here because a stage-ladder
        # reader must see that a blind corpus cannot move the ladder.
        self._report(self.tmp, "Dab", {"image_stack": 10})
        with open(os.path.join(self.tmp, "Dab-summary.json")) as fh:
            rep = json.load(fh)
        del rep["reference_integrity"]
        with open(os.path.join(self.tmp, "Dab-summary.json"), "w") as fh:
            json.dump(rep, fh)
        ev = coverage.load_corpus_evidence([self.tmp])
        rung = coverage.stage_ladder(self._row(), ev)["ladder"][3]
        self.assertEqual(rung["state"], "not measured", rung["why"])
        self.assertIn("blind", rung["why"])
        # and emphatically NOT read as clean
        self.assertNotEqual(rung["state"], "yes")

    def test_a_report_with_no_source_census_is_not_measured(self):
        with open(os.path.join(self.tmp, "Bare-summary.json"), "w") as fh:
            json.dump({"corpus": "Bare", "quarantine_count": 0}, fh)
        ev = coverage.load_corpus_evidence([self.tmp])
        self.assertFalse(ev["measured"])
        self.assertIn("source_census", ev["why"])

    def test_a_corpus_yes_lets_a_class_reach_the_top_stage(self):
        # The rung is wired into the ladder, not just computed beside it.
        self._report(self.tmp, "Dab", {"epochid": 12})
        ev = coverage.load_corpus_evidence([self.tmp])
        row = self._row(cls="epochid", targets=())
        row["no_target_reason"] = "dissolved"
        row["no_target_signoff"] = {"document": "V_eta_epoch_plan.md",
                                    "signoff_fragment": "epochid is DROPPED"}
        row["build_state"]["has_per_class_migrator"] = True
        st = coverage.stage_ladder(row, ev)
        self.assertEqual(st["reached"], 4, st["ladder"])


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

    def test_collapsing_two_adjacent_rungs_reddens(self):
        # The targets rung answers the migrator rung's question. Every class
        # with a migrator now reads "its target classes are built", including
        # the 77 that name no target at all.
        caught = self._assert_reddens(
            _Mutation(_rung_targets_built=coverage._rung_consumed))
        self.assertIn("check_targets_rung_is_not_satisfied_by_an_empty_list",
                      [c[0] for c in caught])

    def test_a_rung_returning_a_constant_YES_reddens(self):
        const = lambda row: ("yes", "constant")  # noqa: E731
        caught = self._assert_reddens(_Mutation(
            _rung_consumed=const, _rung_targets_built=const,
            _rung_emits_decided=const,
            _rung_corpus_proven=lambda row, ev: ("yes", "constant")))
        names = [c[0] for c in caught]
        self.assertIn("check_the_ladder_still_discriminates", names)
        self.assertIn("check_targets_rung_is_not_satisfied_by_an_empty_list",
                      names)

    def test_a_rung_returning_a_constant_NOT_MEASURED_reddens(self):
        # The other way to be dead: everything reads stage 0, which looks like
        # an honest "we have not got far" and is in fact a broken instrument.
        const = lambda row: ("not measured", "constant")  # noqa: E731
        caught = self._assert_reddens(_Mutation(
            _rung_consumed=const, _rung_targets_built=const,
            _rung_emits_decided=const))
        self.assertIn("check_the_ladder_still_discriminates",
                      [c[0] for c in caught])

    def test_dropping_the_satisfies_every_stage_below_rule_reddens(self):
        # `reached` becomes the highest rung that is `yes` regardless of order,
        # which promotes every capped class over a rung nobody read.
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

    def test_promoting_a_capped_row_reddens(self):
        # The single most tempting change: "it has a migrator, call it stage 1
        # even though a lower rung is unread". Distinct from the mutation above
        # -- this one promotes ONLY the capped rows, which is what a reader
        # complaining about the number would ask for.
        real = coverage.stage_ladder

        def promoted(row, evidence=None):
            st = real(row, evidence)
            if st["unclassifiable"] or not st["capped"]:
                return st
            st["reached"] = st["highest_rung_satisfied_independently"]
            st["reached_name"] = coverage.STAGE_NAMES[st["reached"]]
            return st

        caught = self._assert_reddens(_Mutation(stage_ladder=promoted))
        self.assertIn("check_exactly_one_stage_and_no_promotion",
                      [c[0] for c in caught])

    def test_collapsing_the_two_quantities_into_one_reddens(self):
        # `highest_rung_satisfied_independently` set equal to `reached` erases
        # the distinction between a capped row and an untouched one -- the
        # exact defect the pair was added to close.
        real = coverage.stage_ladder

        def collapsed(row, evidence=None):
            st = real(row, evidence)
            if st["unclassifiable"]:
                return st
            st["highest_rung_satisfied_independently"] = st["reached"]
            st["capped"] = False
            return st

        caught = self._assert_reddens(_Mutation(stage_ladder=collapsed))
        self.assertIn("check_capped_and_untouched_are_distinguishable",
                      [c[0] for c in caught])

    def test_counting_an_excused_row_as_untouched_reddens(self):
        # `nothing_satisfied` computed from `yes` alone puts the three signed
        # DISSOLUTIONS (epochid, stimulus_response, ...) in the same bucket as
        # `base`, which nobody has looked at. A settled class reported as
        # untouched inflates the work-remaining figure.
        real = coverage.stage_ladder

        def loose(row, evidence=None):
            st = real(row, evidence)
            if st["unclassifiable"]:
                return st
            st["nothing_satisfied"] = st["nothing_built"]
            return st

        caught = self._assert_reddens(_Mutation(stage_ladder=loose))
        self.assertIn("check_capped_and_untouched_are_distinguishable",
                      [c[0] for c in caught])

    def test_issuing_n_a_without_a_signed_dissolution_reddens(self):
        # `n/a` lets a class climb, so it is the quiet way to fake progress.
        real = coverage._rung_targets_built

        def loose(row):
            if not row["build_state"]["schema_targets_named"]:
                return ("n/a", "nothing named")
            return real(row)

        caught = self._assert_reddens(_Mutation(_rung_targets_built=loose))
        self.assertIn("check_na_requires_a_signed_dissolution",
                      [c[0] for c in caught])

    def test_rendering_NOT_MEASURED_as_a_failure_reddens(self):
        # "no corpus proved it" and "nobody looked" collapsed into one word.
        caught = self._assert_reddens(
            _Mutation(_rung_corpus_proven=lambda row, ev: ("no", "not proven")))
        self.assertIn("check_corpus_rung_is_not_measured_without_evidence",
                      [c[0] for c in caught])

    def test_putting_GOVERNANCE_BACK_into_the_completion_chain_reddens(self):
        # THE REGRESSION THIS RESTRUCTURE EXISTS TO PREVENT, mutated in exactly
        # the shape it had before 2026-08-12: a signature rung, first, gating
        # everything. It caps dozens of rows whose migrators are built.
        real = coverage.stage_ladder

        def governed(row, evidence=None):
            st = real(row, evidence)
            if st["unclassifiable"]:
                return st
            g = coverage.governance_state(row)
            if g["state"] != coverage.G_SIGNED:
                st["reached"] = 0
                st["reached_name"] = coverage.STAGE_NAMES[0]
                st["blocked_by"], st["blocked_by_state"] = 1, "not measured"
            return st

        caught = self._assert_reddens(_Mutation(stage_ladder=governed))
        self.assertIn("check_governance_cannot_move_a_build_stage",
                      [c[0] for c in caught])

    def test_a_rollup_leading_with_a_governance_capped_number_reddens(self):
        # The rollup's headline replaced by the count of rows whose signature
        # is findable -- the number that led this section until 2026-08-12.
        rows = _with_governance(
            _reclassify(copy.deepcopy(_rows()), coverage.CORPUS_SCAN))
        rollup = coverage._stage_rollup(rows, None)
        check_rollup_leads_with_a_fully_measured_rung(rollup)   # precondition
        damaged = copy.deepcopy(rollup)
        signed = sum(1 for r in rows
                     if r["governance"]["state"] == coverage.G_SIGNED)
        damaged["headline"] = {
            "rung": 1, "name": coverage.STAGE_NAMES[1],
            "denominator": len(rows), "yes": signed, "no": 0, "n/a": 0,
            "not measured": len(rows) - signed}
        with self.assertRaises(AssertionError):
            check_rollup_leads_with_a_fully_measured_rung(damaged)

    def test_reporting_the_untouched_count_as_zero_reddens(self):
        rows = _with_governance(
            _reclassify(copy.deepcopy(_rows()), coverage.CORPUS_SCAN))
        rollup = coverage._stage_rollup(rows, None)
        self.assertEqual(rollup["capped"]["genuinely_untouched"], 5,
                         "precondition: five rows have nothing built and "
                         "nothing excused. Nine until `generic_file` was "
                         "credited to did2.convert.foldGenericFiles (OPEN_WORK "
                         "row 107); eight until the demo collapse's migrator "
                         "half was built on 2026-08-12, which took `demoNDI` "
                         "and `demoNDIMock` out; six until `session` gained a "
                         "migrator on 2026-08-13 for the signed `reference` -> "
                         "`local_identifier` rename. Each drop has a different "
                         "cause -- one instrument, two builds -- and the "
                         "distinction is the point of this bucket")
        damaged = copy.deepcopy(rollup)
        damaged["capped"]["genuinely_untouched"] = 0
        with self.assertRaises(AssertionError):
            check_rollup_accounts_for_every_row(damaged, len(rows))

    def test_swallowing_an_unclassifiable_row_reddens(self):
        # CONSTRUCTED FIXTURE, because no live row is malformed -- the mutation
        # is invisible on today's 102 and that is a fact about the data, not a
        # reason to drop the claim.
        rows = [copy.deepcopy(FIXTURE_ROW)]
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
                          highest_rung_satisfied_independently=0,
                          capped=False, nothing_built=True,
                          nothing_satisfied=True, only_excused=False,
                          ladder=[{"stage": n, "name": coverage.STAGE_NAMES[n],
                                   "state": "not measured", "why": "swallowed"}
                                  for n in COMPLETION_RUNGS])
            return st

        with _Mutation(stage_ladder=swallowing):
            rollup = coverage._stage_rollup(
                _with_governance(_reclassify(rows)), None)
        self.assertEqual(
            rollup["unclassifiable"], 0,
            "precondition: the mutation must actually hide the broken row")
        honest = coverage._stage_rollup(
            _with_governance(_reclassify(rows)), None)
        self.assertNotEqual(
            honest["unclassifiable"], rollup["unclassifiable"],
            "the honest tool must report the row the mutation hid")

    def test_the_rollup_dropping_a_row_reddens(self):
        rows = _with_governance(
            _reclassify(copy.deepcopy(_rows()), coverage.CORPUS_SCAN))
        rollup = coverage._stage_rollup(rows, None)
        check_rollup_accounts_for_every_row(rollup, len(rows))
        # Now drop one class from the histogram, as a filtered counter would.
        damaged = copy.deepcopy(rollup)
        damaged["by_stage_reached"]["0"] -= 1
        with self.assertRaises(AssertionError):
            check_rollup_accounts_for_every_row(damaged, len(rows))


if __name__ == "__main__":
    unittest.main()


class ConfirmedTargetsCase(unittest.TestCase):
    """`confirmed_targets` -- the confirm sheet's answer sink.

    The sheet asks 69 classes "is what the migrator ALREADY emits the answer we
    want?" and until 2026-08-13 a YES had nowhere to go: `targets` is generated
    and cannot be hand-set, and `decided_targets` means, by the map's own
    header, "a signed decision no migrator implements yet" -- the opposite. So
    five classes signed that day stayed at stage 1 with rung 2 reading `not
    measured`, and every other answered row would have too.
    """

    def test_the_five_answered_rows_reach_stage_3(self):
        path = os.path.join(REPO_ROOT, "schemas", "V_eta_coverage_ledger.json")
        with open(path) as fh:
            rows = {r["v1_class"]: r for r in json.load(fh)["rows"]}
        for cls in ("daqreader_ndr", "element", "pyraview", "session", "subject"):
            st = rows[cls]["stage"]
            self.assertEqual(
                st["reached"], 3,
                f"{cls} fell back below stage 3 -- a confirmed emission should "
                "satisfy rungs 2 and 3")
            self.assertEqual(
                st["blocked_by"], 4,
                f"{cls} is blocked below rung 4; only the corpus rung should "
                "stop a confirmed, built class")
            self.assertEqual(rows[cls]["decided_targets_source"],
                             "confirmed_emission")

    def test_a_confirmation_is_NOT_a_governance_citation(self):
        # It briefly was, and every one of the five went `signed` while citing a
        # record with no document. Confirming a target set is not signing a
        # disposition; the governance citation must still come from the family.
        path = os.path.join(REPO_ROOT, "schemas", "V_eta_coverage_ledger.json")
        with open(path) as fh:
            rows = {r["v1_class"]: r for r in json.load(fh)["rows"]}
        for cls in ("daqreader_ndr", "element", "pyraview", "session", "subject"):
            cite = (rows[cls]["governance"] or {}).get("signoff") or {}
            self.assertTrue(
                cite.get("document"),
                f"{cls}: signed with a citation carrying no document")

    def test_confirmed_and_decided_cannot_both_be_recorded(self):
        # "already right" and "still owed" are opposites. A row asserting both
        # must stop the ledger, not have one silently win.
        path = os.path.join(REPO_ROOT, "schemas", "V_eta_migration_targets.json")
        with open(path) as fh:
            doc = json.load(fh)
        rows = doc.get("classes") or doc
        both = [k for k, v in rows.items()
                if isinstance(v, dict) and (v.get("confirmed_targets") or {}).get("targets")
                and v.get("decided_targets")]
        self.assertEqual(both, [], f"rows claiming both: {both}")

    def test_an_authored_unread_target_counts_as_emitted_for_rung_3(self):
        # element's raw-recording observation is emitted but underivable, so it
        # lives in `unread_targets`. Excluding it from rung 3 would fail the
        # rung for a limit of the READER rather than a fact about the migrator.
        path = os.path.join(REPO_ROOT, "schemas", "V_eta_coverage_ledger.json")
        with open(path) as fh:
            rows = {r["v1_class"]: r for r in json.load(fh)["rows"]}
        el = rows["element"]
        self.assertIn("voltage_observation", el["decided_targets"])
        self.assertEqual(el["stage"]["reached"], 3)
