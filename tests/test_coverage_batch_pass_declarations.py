"""The third consumption channel: a batch post-pass DECLARING what it folds.

WHAT IS BEING GATED, AND THE DIRECTION IT FAILS IN
--------------------------------------------------
`V_eta_OPEN_WORK.md` row 107: rung 1 asks whether a migrator file NAMED AFTER
the class exists and rung 3 asks whether THAT migrator emits the decided target.
A DID batch post-pass (`+did2/+convert`) is neither, so `generic_file` -- folded
by `did2.convert.foldGenericFiles` into a `term_observation` + an `opaque_body`
-- reported stage 0, "source identified". The ladder UNDERSTATED progress
structurally, and that is the direction that cost the team the "94 classes at
stage 0" reading.

The repair reads a DECLARATION the pass carries in its own header. So this file
gates two opposite failures, and the second is the one worth writing tests for:

  1. A DECLARED consumer MOVES the rung. Without this the repair does nothing.
  2. AN ABSENT DECLARATION MOVES NOTHING, AND SAYS SO. A pass that forgot to
     declare, a DID-matlab checkout too old to have the parser, an unreadable
     source -- none of them may read as "this class is consumed", and none of
     them may read as "this class is NOT consumed" either. The honest word is
     that the channel was not measured, and the rung `why` must print it.

Rule 2 of the same file is the reason 2 has more tests than 1: every claim here
is asserted against evidence PRESENT, never against an absence.

DENOMINATOR: every test that reads the live scan prints how many passes it saw
before it asserts anything about them.
"""

import copy
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))

import coverage  # noqa: E402

LEDGER_JSON = os.path.join(ROOT, "schemas", "V_eta_coverage_ledger.json")


def _ledger():
    with open(LEDGER_JSON) as fh:
        return json.load(fh)


# A row shaped like a real one, with NOTHING that could climb a rung on its
# own: no per-class migrator, no second pass, no decided target. Every stage
# movement below is therefore attributable to the declaration and to nothing
# else.
BARE_ROW = {
    "v1_class": "fixture_class", "veta_class": "fixture_class", "targets": [],
    "decided_targets": [], "second_pass": [], "no_target_reason": None,
    "decided_signoff": None, "no_target_signoff": None,
    "decided_targets_source": None, "decided_by_family": None,
    "governance_gap": None, "families_naming_this_class": [],
    "build_state": {
        "schema_targets_named": 0, "schema_targets_built": [],
        "schema_targets_missing": [], "migrator_emits_decided_targets": False,
        "has_per_class_migrator": False,
        "batch_pass_consumers": [], "batch_pass_emits": {},
        "batch_pass_emits_decided_targets": False,
        # The FOURTH channel's fields, empty for the same reason as the third's:
        # this row must climb nothing on its own, so every movement below stays
        # attributable to the declaration under test. They are `_need`-read, not
        # `.get`-read, because `build_rows` computes them for all 102 rows --
        # so a row without them is malformed and should say so loudly.
        "helper_consumers": [], "helper_emits": {},
        "helper_emits_decided_targets": False,
    },
}


class ScanState:
    """Set BATCH_PASS_SCAN for one test and put it back afterwards.

    The scan is a module global because `build_ledger` fills it once for every
    caller. A test that mutated it and did not restore it would leak into every
    later test in the process, which is the kind of cross-test dependency that
    makes a red run unreadable.
    """

    def __init__(self, **kw):
        self.kw = kw

    def __enter__(self):
        self.saved = copy.deepcopy(coverage.BATCH_PASS_SCAN)
        coverage.BATCH_PASS_SCAN.update(self.kw)
        return coverage.BATCH_PASS_SCAN

    def __exit__(self, *exc):
        coverage.BATCH_PASS_SCAN.clear()
        coverage.BATCH_PASS_SCAN.update(self.saved)
        return False


def _measured(index, missing=(), chain=9):
    return {"measured": True, "why": None, "chain_size": chain,
            "index": index, "declared": [], "missing": list(missing),
            "invalid": []}


class TestTheLiveScan(unittest.TestCase):
    """Read the real DID-matlab declarations, if the sibling is in reach."""

    @classmethod
    def setUpClass(cls):
        coverage.batch_pass_declarations()
        cls.s = coverage.BATCH_PASS_SCAN
        print(f'\nDENOMINATOR: DID-matlab={coverage.DIDM}; '
              f'measured={cls.s["measured"]}, chain of '
              f'{cls.s["chain_size"]} pass(es), {len(cls.s["declared"])} '
              f'declared, {len(cls.s["missing"])} MISSING, '
              f'{len(cls.s["invalid"])} INVALID')

    def test_the_scan_reports_measured_or_says_why_not(self):
        if not self.s["measured"]:
            self.assertTrue(self.s["why"], "an unmeasured scan MUST carry a why")
            self.skipTest("DID-matlab not in reach: " + str(self.s["why"]))
        self.assertGreater(self.s["chain_size"], 0)
        self.assertIsNone(self.s["why"])

    def test_the_two_accountings_agree(self):
        """The scan's summary lists vs its own per-pass verdicts.

        ADDED AFTER A MUTATION FAILED TO REDDEN. Laundering `missing` into
        `declared` -- the exact collapse this mechanism exists to prevent --
        was invisible from this side, because the real tree has no missing
        declarations and every other test reads the summary lists the mutation
        rewrote. A cross-check between two independently-derived accountings
        catches it on any tree, including a clean one.
        """
        if not self.s["measured"]:
            self.skipTest("scan not measured")
        self.assertEqual(self.s["accounting_disagreement"], [])
        self.assertEqual(
            len(self.s["per_pass"]), self.s["chain_size"],
            "every pass in the chain must carry a per-pass verdict")
        for fn, d in self.s["per_pass"].items():
            self.assertEqual(d["declared"], fn in self.s["declared"], fn)
            self.assertEqual(not d["declared"], fn in self.s["missing"], fn)

    def test_no_pass_in_the_chain_is_missing_a_declaration(self):
        if not self.s["measured"]:
            self.skipTest("scan not measured")
        self.assertEqual(self.s["missing"], [], "MISSING A DECLARATION")
        self.assertEqual(self.s["invalid"], [], "INVALID declaration")

    def test_the_three_row_107_instances_are_declared(self):
        if not self.s["measured"]:
            self.skipTest("scan not measured")
        idx = self.s["index"]
        # shape (2), the plain batch fold
        self.assertIn("generic_file", idx)
        self.assertEqual([e["pass"] for e in idx["generic_file"]],
                         ["foldGenericFiles"])
        self.assertEqual(idx["generic_file"][0]["form"], "document")
        # shape (3), an INLINE field block rather than a minted document
        k = "stimulus_response_scalar_parameters_basic"
        self.assertIn(k, idx)
        self.assertEqual(idx[k][0]["form"], "inline")
        self.assertEqual(idx[k][0]["targets"], ["method_parameters"])
        # the honesty case: declared, dormant, emitting nothing
        self.assertEqual(idx["valid_interval"][0]["form"], "nothing")
        self.assertTrue(idx["valid_interval"][0]["reason"])


class TestADeclarationMovesTheRung(unittest.TestCase):

    def test_a_declared_consumer_moves_rung_1(self):
        row = copy.deepcopy(BARE_ROW)
        before = coverage.stage_ladder(row, None)
        self.assertEqual(before["ladder"][0]["state"], coverage.S_NO)
        row["build_state"]["batch_pass_consumers"] = ["foldGenericFiles"]
        after = coverage.stage_ladder(row, None)
        self.assertEqual(after["ladder"][0]["state"], coverage.S_YES)
        self.assertIn("BATCH POST-PASS", after["ladder"][0]["why"])
        self.assertIn("foldGenericFiles", after["ladder"][0]["why"])

    def test_a_declared_emission_moves_rung_3(self):
        row = copy.deepcopy(BARE_ROW)
        row["decided_targets"] = ["method_parameters"]
        row["build_state"].update(
            schema_targets_named=1, schema_targets_built=["method_parameters"],
            has_per_class_migrator=True)
        self.assertEqual(coverage.stage_ladder(row, None)["ladder"][2]["state"],
                         coverage.S_NO)
        row["build_state"].update(
            batch_pass_consumers=["resolveResponseParameters"],
            batch_pass_emits={"resolveResponseParameters": ["method_parameters"]},
            batch_pass_emits_decided_targets=True)
        st = coverage.stage_ladder(row, None)
        self.assertEqual(st["ladder"][2]["state"], coverage.S_YES)
        self.assertIn("BATCH POST-PASS", st["ladder"][2]["why"])

    def test_the_credit_is_distinguishable_in_the_rendered_cell(self):
        """A reader of the ARTIFACT, not only of stdout, sees the channel."""
        row = copy.deepcopy(BARE_ROW)
        row["build_state"]["batch_pass_consumers"] = ["foldGenericFiles"]
        row["stage"] = coverage.stage_ladder(row, None)
        cell = coverage._stage_cell(row)
        self.assertIn("rung 1 via DID BATCH POST-PASS", cell)
        self.assertIn("foldGenericFiles", cell)

    def test_the_build_state_clause_does_not_contradict_the_stage(self):
        """It used to say `MIGRATOR: does NOT emit them yet` beside stage 3."""
        row = copy.deepcopy(BARE_ROW)
        row["decided_targets"] = ["method_parameters"]
        row["build_state"].update(
            schema_targets_named=1, schema_targets_built=["method_parameters"],
            batch_pass_consumers=["resolveResponseParameters"],
            batch_pass_emits={"resolveResponseParameters": ["method_parameters"]},
            batch_pass_emits_decided_targets=True)
        clause = coverage._build_state_clause(row)
        self.assertIn("BATCH POST-PASS", clause)
        self.assertNotIn("does NOT emit them yet", clause)

    def test_a_per_class_migrator_is_never_attributed_to_a_batch_pass(self):
        """The migrator branch is read FIRST, so a real migrator keeps credit."""
        row = copy.deepcopy(BARE_ROW)
        row["targets"] = ["method_parameters"]
        row["decided_targets"] = ["method_parameters"]
        row["build_state"].update(
            schema_targets_named=1, schema_targets_built=["method_parameters"],
            migrator_emits_decided_targets=True, has_per_class_migrator=True,
            batch_pass_consumers=["resolveResponseParameters"],
            batch_pass_emits={"resolveResponseParameters": ["method_parameters"]},
            batch_pass_emits_decided_targets=False)
        why = coverage.stage_ladder(row, None)["ladder"][2]["why"]
        self.assertIn("migrator_emits_decided_targets", why)
        self.assertNotIn("BATCH POST-PASS", why)


class TestAnAbsentDeclarationSatisfiesNothing(unittest.TestCase):
    """THE HALF THAT MATTERS. Absence must never read as an empty set."""

    def test_a_missing_declaration_leaves_the_rung_no_and_names_the_pass(self):
        row = copy.deepcopy(BARE_ROW)
        with ScanState(**_measured({}, missing=["someNewPass"])):
            st = coverage.stage_ladder(row, None)
        self.assertEqual(st["ladder"][0]["state"], coverage.S_NO)
        why = st["ladder"][0]["why"]
        self.assertIn("NO DECLARATION", why)
        self.assertIn("someNewPass", why)
        self.assertIn("not measured", why)

    def test_an_unread_scan_says_UNDERSTATEMENT_rather_than_no(self):
        row = copy.deepcopy(BARE_ROW)
        with ScanState(measured=False, why="DID-matlab not found", index={},
                       chain_size=0, declared=[], missing=[], invalid=[]):
            why = coverage.stage_ladder(row, None)["ladder"][0]["why"]
        self.assertIn("NOT READ", why)
        self.assertIn("UNDERSTATEMENT", why)
        self.assertIn("DID-matlab not found", why)

    def test_a_fully_read_chain_says_so_positively(self):
        """`no` from a complete read is a MEASUREMENT and must say which."""
        row = copy.deepcopy(BARE_ROW)
        with ScanState(**_measured({}, chain=9)):
            why = coverage.stage_ladder(row, None)["ladder"][0]["why"]
        self.assertIn("All 9 batch post-pass(es)", why)
        self.assertNotIn("UNDERSTATEMENT", why)

    def test_a_nothing_emission_credits_no_rung(self):
        """`resolveValidIntervals` is dormant; its row must stay at rung 3 no."""
        row = copy.deepcopy(BARE_ROW)
        row["v1_class"] = row["veta_class"] = "valid_interval"
        row["decided_targets"] = ["logical_observation"]
        row["build_state"].update(
            schema_targets_named=1,
            schema_targets_built=["logical_observation"],
            batch_pass_consumers=["resolveValidIntervals"],
            batch_pass_emits={}, batch_pass_emits_decided_targets=False)
        st = coverage.stage_ladder(row, None)
        self.assertEqual(st["ladder"][0]["state"], coverage.S_YES)
        self.assertEqual(st["ladder"][2]["state"], coverage.S_NO)

    def test_an_unattributed_emission_reaches_no_row(self):
        """UNATTRIBUTED is indexed under no class name, so it credits nothing."""
        text = ("function [result, r] = p(result)\n"
                "%P.\n"
                "%   " + "BATCH-PASS-CONSUMES" + ": NONE -- reads no v1 class\n"
                "%   " + "BATCH-PASS-EMITS" + ": NONE -- emits nothing\n")
        mod = _parser()
        if mod is None:
            self.skipTest("DID-matlab parser not in reach")
        d = mod.parse_declaration(text)
        self.assertTrue(d["declared"])
        self.assertEqual(d["consumes"], [])
        self.assertEqual(d["errors"], [])


def _parser():
    if not coverage.DIDM:
        return None
    path = os.path.join(coverage.DIDM, "tools", "batch_pass_declarations.py")
    if not os.path.isfile(path):
        return None
    import importlib.util
    spec = importlib.util.spec_from_file_location("_bpd_for_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestTheCommittedLedger(unittest.TestCase):
    """What the channel actually moved, pinned by name so a change is seen."""

    @classmethod
    def setUpClass(cls):
        cls.bp = _ledger()["summary"]["batch_pass"]
        print(f'\nDENOMINATOR: {cls.bp["denominator_rows"]} ledger row(s); '
              f'chain of {cls.bp["chain_size"]}, '
              f'{len(cls.bp["declared"])} declared, '
              f'{len(cls.bp["missing"])} MISSING, '
              f'{len(cls.bp["invalid"])} INVALID')

    def test_the_rollup_is_measured_and_complete(self):
        self.assertTrue(self.bp["measured"], self.bp["why"])
        self.assertEqual(self.bp["missing"], [])
        self.assertEqual(self.bp["invalid"], [])
        self.assertEqual(self.bp["chain_size"], 9)

    def test_the_rows_this_channel_moved_are_pinned(self):
        # PINNED BY NAME. Three shapes, three rows, and each is one of the
        # three row 107 names -- not an accident of a name collision.
        self.assertEqual(
            sorted(e["v1_class"] for e in self.bp["credited_rung_1"]),
            ["epochid", "generic_file"])
        self.assertEqual(
            sorted(e["v1_class"] for e in self.bp["credited_rung_3"]),
            ["stimulus_response_scalar_parameters_basic"])

    def test_a_dormant_pass_credited_nothing(self):
        named = {e["v1_class"] for e in self.bp["unattributed_or_nothing"]}
        self.assertIn("valid_interval", named)
        for bucket in ("credited_rung_1", "credited_rung_3"):
            self.assertNotIn("valid_interval",
                             {e["v1_class"] for e in self.bp[bucket]})

    def test_declared_names_that_are_not_v1_classes_are_reported(self):
        """Reported, not dropped: a silent non-match hides a typo."""
        names = {e["name"] for e in self.bp["declared_matching_no_row"]}
        self.assertEqual(
            names, {"session_relative_reference", "session_bounded_reference"})

    def test_the_moved_rows_carry_the_channel_in_their_own_why(self):
        rows = {r["v1_class"]: r for r in _ledger()["rows"]}
        for name in ("epochid", "generic_file"):
            why = rows[name]["stage"]["ladder"][0]["why"]
            self.assertIn("BATCH POST-PASS", why, name)
        why3 = rows["stimulus_response_scalar_parameters_basic"][
            "stage"]["ladder"][2]["why"]
        self.assertIn("BATCH POST-PASS", why3)


class TestMutationsRedden(unittest.TestCase):
    """Break the reader; confirm the claims above stop holding.

    A gate that cannot be shown to go red is a decoration. Each mutation below
    is one realistic way this mechanism could silently stop working.
    """

    def test_mutation_dropping_the_index_stops_crediting(self):
        """The reader returns nothing -- every credit must vanish, not persist."""
        row = copy.deepcopy(BARE_ROW)
        row["build_state"]["batch_pass_consumers"] = []
        with ScanState(**_measured({})):
            st = coverage.stage_ladder(row, None)
        self.assertEqual(st["ladder"][0]["state"], coverage.S_NO)

    def test_mutation_treating_a_missing_declaration_as_an_empty_set(self):
        """The collapse this whole mechanism exists to prevent.

        If `missing` were folded into "declared nothing", the rung `why` would
        stop naming the pass and a reader could not tell an unwritten
        declaration from a class no pass touches.
        """
        row = copy.deepcopy(BARE_ROW)
        with ScanState(**_measured({}, missing=["forgottenPass"])):
            with_missing = coverage.stage_ladder(row, None)["ladder"][0]["why"]
        with ScanState(**_measured({})):
            without = coverage.stage_ladder(row, None)["ladder"][0]["why"]
        self.assertNotEqual(with_missing, without,
                            "a MISSING declaration and a complete read must "
                            "not produce the same sentence")

    def test_mutation_crediting_rung_3_from_an_unattributed_emission(self):
        """An emission no class owns must not satisfy any class's rung 3."""
        row = copy.deepcopy(BARE_ROW)
        row["decided_targets"] = ["epoch"]
        row["build_state"].update(schema_targets_named=1,
                                  schema_targets_built=["epoch"],
                                  batch_pass_consumers=["epochMint"],
                                  batch_pass_emits={},
                                  batch_pass_emits_decided_targets=False)
        self.assertEqual(coverage.stage_ladder(row, None)["ladder"][2]["state"],
                         coverage.S_NO)

    def test_mutation_laundering_missing_into_declared_is_caught(self):
        """M3, reproduced in-process: the mutation that did NOT redden at first.

        `batch_pass_declarations()` used to store the scan's summary lists and
        nothing else, so moving a name from `missing` to `declared` changed no
        assertion on a tree with no missing declarations. The cross-check
        against the per-pass verdicts is what makes it visible.
        """
        laundered = _measured({}, missing=[])
        laundered["declared"] = ["forgottenPass"]
        laundered["per_pass"] = {"forgottenPass": {"declared": False,
                                                   "errors": ["no marker"]}}
        laundered["accounting_disagreement"] = sorted(
            fn for fn, d in laundered["per_pass"].items()
            if d["declared"] != (fn in laundered["declared"])
            or d["declared"] == (fn in laundered["missing"]))
        self.assertEqual(laundered["accounting_disagreement"],
                         ["forgottenPass"],
                         "a pass reported as declared while its own verdict "
                         "says otherwise MUST show as an accounting "
                         "disagreement")

    def test_mutation_a_row_missing_the_new_build_state_fields_is_loud(self):
        """`_need` must raise, not default. A defaulted field is an absence."""
        row = copy.deepcopy(BARE_ROW)
        del row["build_state"]["batch_pass_consumers"]
        st = coverage.stage_ladder(row, None)
        self.assertTrue(st["unclassifiable"])
        self.assertIn("batch_pass_consumers", st["unclassifiable_why"])


if __name__ == "__main__":
    unittest.main()


class TestTheRenameJoin(unittest.TestCase):
    """A batch pass runs AFTER the migrators, so it names the MIGRATED class.

    `epochMint` reads `acquisition_epoch` bodies -- the migrated form of did_v1
    `element_epoch` -- and declared that truthfully, and the ledger still could
    not credit it: `element_epoch` carries `veta_class = None`, so none of the
    three spellings the matcher offers is the name the batch holds.

    THE DANGEROUS FIX IS THE OBVIOUS ONE, and these tests exist to keep it out.
    Matching a declared name against every row's `targets` credits one pass to
    every row that emits that class, and `session_relative_reference` -- which
    `resolveSessionAnchors` declares -- is a target of THIRTY-SIX rows. So the
    rule is the RENAME case only: sole target, single owner.
    """

    def test_a_pure_rename_joins(self):
        owners = coverage.rename_target_owner(
            {"element_epoch": ["acquisition_epoch"], "other": ["something_else"]})
        self.assertEqual(owners.get("acquisition_epoch"), "element_epoch")

    def test_a_target_claimed_by_several_rows_never_joins(self):
        """The 36-row case, in miniature. This is the whole point of the rule."""
        owners = coverage.rename_target_owner(
            {"a": ["session_relative_reference"],
             "b": ["session_relative_reference"],
             "c": ["session_relative_reference"]})
        self.assertNotIn("session_relative_reference", owners)

    def test_a_row_with_several_targets_never_joins(self):
        """Uniqueness alone is NOT enough. `session_bounded_reference` has
        exactly one owner, and crediting that row with "a pass consumes it"
        because a pass consumes an ANCHOR its migrator emitted is a different
        claim from the one rung 1 makes."""
        owners = coverage.rename_target_owner(
            {"ontologyTableRow": ["subject", "session_bounded_reference"]})
        self.assertEqual(owners, {},
                         "a decomposition is not a rename; only a 1:1 rename "
                         "makes the migrated name identify the row")

    def test_the_order_of_classes_cannot_change_the_answer(self):
        """Uniqueness is computed over the WHOLE universe. Accumulating it per
        row would degrade to `unique among the rows seen so far`, which makes
        the join depend on iteration order."""
        a = coverage.rename_target_owner({"x": ["t"], "y": ["t"]})
        b = coverage.rename_target_owner({"y": ["t"], "x": ["t"]})
        self.assertEqual(a, b)
        self.assertEqual(a, {})

    def test_the_live_ledger_credits_element_epoch_and_nothing_else_moved(self):
        rows = _ledger()["rows"]
        print(f"\nDENOMINATOR: {len(rows)} ledger rows read")
        by = {r["v1_class"]: r for r in rows}
        self.assertIn("epochMint",
                      by["element_epoch"]["build_state"]["batch_pass_consumers"])
        # The refusal, on real data: 36 rows emit `session_relative_reference`
        # and not one of them may be credited to `resolveSessionAnchors` by it.
        emitters = [r["v1_class"] for r in rows
                    if "session_relative_reference" in (r.get("targets") or [])]
        self.assertGreater(len(emitters), 1)
        for cn in emitters:
            self.assertNotIn(
                "resolveSessionAnchors",
                by[cn]["build_state"]["batch_pass_consumers"],
                f"{cn} was credited through a SHARED target -- the over-credit "
                "the rename rule exists to refuse")
