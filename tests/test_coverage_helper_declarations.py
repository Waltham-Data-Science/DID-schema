"""The fourth consumption channel: a SHARED HELPER declaring what it folds.

WHAT IS BEING GATED, AND WHY IT IS NOT THE OBVIOUS REPAIR
---------------------------------------------------------
`app` reported rung 3 = `no` -- "the decided target `software` is not among
what the migrator emits today (nothing)" -- while
`+migrators_j/private/jSoftwareFromApp.m` had been folding it into a `software`
entity at six call sites. Every channel that existed asks a question about a
NAME: is there a migrator file named after the class, a pass in the derived
chain, an authored `emitted_by`. That helper is named after neither the source
nor the target, so all three missed it.

THE OBVIOUS FIX WAS MEASURED AND REJECTED, AND THAT IS THE PROPERTY MOST WORTH
PINNING. Deriving the credit -- walking the call graph from each migrator and
crediting any mint site reachable through its helpers -- agrees with the ledger
on 22 of the 31 scored rows and recovers `app`. It also credits
`valid_interval`, whose `logical_observation` mint site sits inside
`resolveValidIntervals.m` behind a guard that is OFF by team decision. A
reachability walk cannot see dormancy; a declaration states it, and that pass
already declares `valid_interval -> nothing` with the reason. Trading a
pessimistic miss for an optimistic one is the worse trade here, so the credit
comes from a DECLARATION. `test_reachability_would_credit_valid_interval` is
the test that keeps that reasoning from being quietly re-litigated.

THE ASYMMETRY WITH THE THIRD CHANNEL IS DELIBERATE AND IS ALSO PINNED. A pass
in the derived chain MUST declare and the gate is armed, because the chain is
derived so the denominator is known. Nothing derives "a helper that owes a
declaration", so declaring is VOLUNTARY here -- and the safety property that
replaces the gate is that an undeclared helper credits NOTHING and the scan
prints how many mint while declaring nothing.

DENOMINATOR: every test that reads the live scan prints how many helpers it saw
before asserting anything about them.
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


# Shaped like a real row and able to climb NOTHING on its own: no per-class
# migrator, no second pass, no batch post-pass. Every movement below is
# therefore attributable to the helper declaration and to nothing else.
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
        "helper_consumers": [], "helper_emits": {},
        "helper_emits_decided_targets": False,
    },
}


class HelperScanState:
    """Set HELPER_SCAN for one test and restore it afterwards.

    Same reasoning as the third channel's `ScanState`: the scan is a module
    global filled once per `build_ledger`, so a test that mutated it without
    restoring would leak into every later test in the process.
    """

    def __init__(self, **kw):
        self.kw = kw

    def __enter__(self):
        self.saved = copy.deepcopy(coverage.HELPER_SCAN)
        coverage.HELPER_SCAN.update(self.kw)
        return coverage.HELPER_SCAN

    def __exit__(self, *exc):
        coverage.HELPER_SCAN.clear()
        coverage.HELPER_SCAN.update(self.saved)
        return False


def _measured(index, candidates=53, minting_undeclared=()):
    return {"measured": True, "why": None, "candidates": candidates,
            "minting": 16, "declared": sorted({e["helper"] for v in index.values()
                                               for e in v}),
            "undeclared": candidates - 1, "invalid": [],
            "minting_undeclared": list(minting_undeclared), "index": index}


class TestTheLiveScan(unittest.TestCase):
    """Read the real DID-matlab helper declarations, if the sibling is here."""

    @classmethod
    def setUpClass(cls):
        coverage.helper_declarations()
        cls.s = coverage.HELPER_SCAN
        print(f'\nDENOMINATOR: DID-matlab={coverage.DIDM}; '
              f'measured={cls.s["measured"]}, {cls.s["candidates"]} helper '
              f'candidate(s), {cls.s["minting"]} minting, '
              f'{len(cls.s["declared"])} declared, {cls.s["undeclared"]} '
              f'undeclared, {len(cls.s["invalid"])} INVALID')

    def _live(self):
        if not self.s["measured"]:
            self.assertTrue(self.s["why"], "an unmeasured scan MUST carry a why")
            self.skipTest("DID-matlab not in reach: " + str(self.s["why"]))

    def test_the_scan_reports_measured_or_says_why_not(self):
        self._live()
        self.assertGreater(self.s["candidates"], 0)
        self.assertIsNone(self.s["why"])

    def test_zero_candidates_is_a_failed_lookup_not_a_measurement(self):
        """The `silentLoss` defect in this channel's shape: a scan that found
        no helper directory must not report `measured` with an empty index,
        because that is indistinguishable from a tree where nothing declares."""
        self._live()
        self.assertTrue(
            self.s["candidates"] or not self.s["measured"],
            "candidates==0 with measured==True would make 'looked in the wrong "
            "place' read exactly like 'no helper declares'")

    def test_no_declaration_is_malformed(self):
        self._live()
        self.assertEqual(
            self.s["invalid"], [],
            "a half-written declaration (one marker present, the other absent) "
            "is INVALID, not undeclared -- it was written on purpose")

    def test_jSoftwareFromApp_declares_the_app_fold(self):
        """The row this channel exists for, asserted against evidence PRESENT."""
        self._live()
        entries = coverage.helper_entries("app", "app")
        self.assertTrue(
            entries,
            "jSoftwareFromApp must declare `app`; without it the ladder reports "
            "`app` unbuilt while six call sites fold it")
        self.assertIn("jSoftwareFromApp", [e["helper"] for e in entries])
        self.assertIn("software",
                      [t for e in entries for t in e["targets"]])

    def test_the_undeclared_minters_are_named_not_counted(self):
        """`nobody looked` stays a third state: the helpers that mint while
        declaring nothing are listed, so the unmeasured set has a shape."""
        self._live()
        self.assertLessEqual(len(self.s["minting_undeclared"]),
                             self.s["minting"])
        for fn in self.s["minting_undeclared"]:
            self.assertNotIn(fn, self.s["declared"])


class TestADeclarationMovesTheRung(unittest.TestCase):

    def test_a_declared_consumer_moves_rung_1(self):
        row = copy.deepcopy(BARE_ROW)
        idx = {"fixture_class": [{"helper": "jFixture", "form": "document",
                                  "targets": ["fixture_target"], "reason": None}]}
        with HelperScanState(**_measured(idx)):
            row["build_state"]["helper_consumers"] = ["jFixture"]
            state, why = coverage._rung_consumed(row)
        self.assertEqual(state, coverage.S_YES)
        self.assertIn("SHARED HELPER", why)
        self.assertIn("jFixture", why)

    def test_a_declared_emission_moves_rung_3(self):
        row = copy.deepcopy(BARE_ROW)
        row["decided_targets"] = ["fixture_target"]
        bs = row["build_state"]
        bs["schema_targets_named"] = 1
        bs["helper_consumers"] = ["jFixture"]
        bs["helper_emits"] = {"jFixture": ["fixture_target"]}
        bs["helper_emits_decided_targets"] = True
        with HelperScanState(**_measured({})):
            state, why = coverage._rung_emits_decided(row)
        self.assertEqual(state, coverage.S_YES)
        self.assertIn("SHARED HELPER", why)
        self.assertIn("NOT a corpus proof", why)

    def test_the_credit_is_distinguishable_from_a_migrators(self):
        """A reader must be able to tell WHICH mechanism climbed the rung; the
        `app` shape is invisible if the four channels are summed."""
        row = copy.deepcopy(BARE_ROW)
        row["build_state"]["helper_consumers"] = ["jFixture"]
        with HelperScanState(**_measured({})):
            _, why = coverage._rung_consumed(row)
        self.assertNotIn("has_per_class_migrator", why)
        self.assertIn("helper_consumers", why)


class TestAnAbsentDeclarationSatisfiesNothing(unittest.TestCase):
    """The direction that matters: nothing here may make a rung look better."""

    def test_an_undeclared_helper_leaves_rung_1_no(self):
        row = copy.deepcopy(BARE_ROW)
        with HelperScanState(**_measured({})):
            state, why = coverage._rung_consumed(row)
        self.assertEqual(state, coverage.S_NO)
        self.assertNotIn("SHARED HELPER", why)

    def test_an_unread_scan_says_UNDERSTATEMENT_rather_than_no(self):
        row = copy.deepcopy(BARE_ROW)
        row["decided_targets"] = ["fixture_target"]
        row["build_state"]["schema_targets_named"] = 1
        with HelperScanState(measured=False, why="DID-matlab not found",
                             index={}, candidates=0, minting=0, declared=[],
                             undeclared=0, invalid=[], minting_undeclared=[]):
            state, why = coverage._rung_emits_decided(row)
        self.assertEqual(state, coverage.S_NO)
        self.assertIn("UNDERSTATEMENT", why)
        self.assertIn("NOT READ", why)

    def test_a_measured_scan_names_the_unmeasured_minters_in_the_why(self):
        """A `no` from a fully-read scan must still say what it could not see."""
        row = copy.deepcopy(BARE_ROW)
        row["decided_targets"] = ["fixture_target"]
        row["build_state"]["schema_targets_named"] = 1
        with HelperScanState(**_measured({}, minting_undeclared=["jSampledBody"])):
            state, why = coverage._rung_emits_decided(row)
        self.assertEqual(state, coverage.S_NO)
        self.assertIn("jSampledBody", why)
        self.assertIn("MINT a document while declaring nothing", why)

    def test_a_helper_declaration_cannot_shadow_the_per_class_migrator(self):
        """Ordering: a migrator that already emits the decided target must be
        credited to the migrator, or the rollup's channel counts are fiction."""
        row = copy.deepcopy(BARE_ROW)
        row["decided_targets"] = ["fixture_target"]
        bs = row["build_state"]
        bs["schema_targets_named"] = 1
        bs["migrator_emits_decided_targets"] = True
        bs["helper_emits_decided_targets"] = True
        bs["helper_emits"] = {"jFixture": ["fixture_target"]}
        with HelperScanState(**_measured({})):
            state, why = coverage._rung_emits_decided(row)
        self.assertEqual(state, coverage.S_YES)
        self.assertIn("migrator_emits_decided_targets", why)
        self.assertNotIn("SHARED HELPER", why)


class TestMutationsRedden(unittest.TestCase):
    """Each mutation is a way the channel could quietly over-credit."""

    def test_mutation_dropping_the_index_stops_crediting(self):
        with HelperScanState(**_measured({})):
            self.assertEqual(coverage.helper_entries("app", "app"), [])

    def test_mutation_one_helper_credits_a_row_once_not_per_spelling(self):
        """Both spellings are offered (V_eta snake vs NDI camel); a helper that
        matches on two of them must not be counted twice."""
        idx = {"ontologyTableRow": [{"helper": "jFix", "form": "document",
                                     "targets": ["t"], "reason": None}],
               "ontology_table_row": [{"helper": "jFix", "form": "document",
                                       "targets": ["t"], "reason": None}]}
        with HelperScanState(**_measured(idx)):
            got = coverage.helper_entries("ontologyTableRow",
                                          "ontology_table_row")
        self.assertEqual(len(got), 1)

    def test_mutation_an_invalid_declaration_credits_nothing(self):
        """Rule 4 of the grammar: a typo must not become a credited rung. The
        index is built by `helper_index`, which skips a declaration carrying
        errors -- asserted here against the real DID-matlab parser."""
        if not coverage.DIDM:
            self.skipTest("DID-matlab not in reach")
        path = os.path.join(coverage.DIDM, "tools",
                            "batch_pass_declarations.py")
        if not os.path.isfile(path):
            self.skipTest("this DID-matlab predates the declarations")
        import importlib.util
        spec = importlib.util.spec_from_file_location("_bpd_mutation", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        out = {"declared": ["jBroken"],
               "helpers": {"jBroken": {
                   "declared": True, "consumes": ["thing"],
                   "emits": {"thing": {"form": "document",
                                       "targets": ["target"], "reason": None}},
                   "errors": ["EMITS: `other` is not in CONSUMES"]}}}
        self.assertEqual(
            mod.helper_index(out), {},
            "a declaration with any error must contribute NO index entry")


class TestTheRejectedDerivation(unittest.TestCase):
    """Why this is a declaration and not a call-graph walk.

    Pinned so the reasoning survives the next person who notices that a
    reachability walk would be less typing.
    """

    def test_reachability_would_credit_valid_interval(self):
        """`resolveValidIntervals.m` MINTS `logical_observation` and the pass is
        dormant by team decision, so a walk that credits mint sites credits a
        rung for code that cannot run. The mint site's presence is the
        evidence; the declaration is what distinguishes it from a live one."""
        if not coverage.DIDM:
            self.skipTest("DID-matlab not in reach")
        src = os.path.join(coverage.DIDM, "src", "did", "+did2", "+convert",
                           "resolveValidIntervals.m")
        if not os.path.isfile(src):
            self.skipTest("resolveValidIntervals.m absent from this checkout")
        with open(src, errors="replace") as fh:
            text = fh.read()
        self.assertIn(
            "'class_name', 'logical_observation'", text,
            "if this mint site is gone the rejected-derivation argument needs "
            "re-deriving rather than deleting")
        coverage.batch_pass_declarations()
        entries = coverage.batch_pass_entries("valid_interval", "valid_interval")
        if not entries:
            self.skipTest("batch-pass declarations not readable here")
        self.assertEqual(
            [e["form"] for e in entries], ["nothing"],
            "the pass declares `valid_interval -> nothing`; that declaration is "
            "the only thing standing between the mint site and a false credit")

    def test_the_committed_ledger_keeps_valid_interval_at_rung_3_no(self):
        rows = {r["v1_class"]: r for r in _ledger()["rows"]}
        print(f"\nDENOMINATOR: {len(rows)} ledger rows read")
        vi = rows.get("valid_interval")
        self.assertIsNotNone(vi)
        self.assertEqual(vi["stage"]["ladder"][2]["state"], "no")

    def test_the_committed_ledger_has_app_at_rung_3_yes(self):
        rows = {r["v1_class"]: r for r in _ledger()["rows"]}
        app = rows.get("app")
        self.assertIsNotNone(app)
        self.assertEqual(app["stage"]["ladder"][0]["state"], "yes")
        self.assertEqual(app["stage"]["ladder"][2]["state"], "yes")
        self.assertIn("jSoftwareFromApp",
                      app["build_state"]["helper_consumers"])


if __name__ == "__main__":
    unittest.main()
