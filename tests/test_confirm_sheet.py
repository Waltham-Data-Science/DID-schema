"""The confirm sheet must sort EVERY open class, and decide none of them.

The sheet exists because 65 classes sit at ladder stage 1 -- migrator runs, rung
2 unread -- and that reads like 65 classes of unbuilt work when it is really 65
unanswered questions. A sheet that quietly dropped a class would recreate the
exact defect it addresses: a class nobody reviews, looking like a class that
needs no review.

So the invariants are about COVERAGE and RESTRAINT, not about the prose:

  * every stage-N class lands in exactly one bucket, and an unsortable class is
    counted, named and exits non-zero -- never omitted;
  * the classification reads RECORDED evidence only (the generated `targets`,
    the authored `how`), so it cannot drift into an opinion;
  * a self-named emission is a PASSTHROUGH and is asked about separately,
    because "the tombstone is the end state" and "we deferred this" are
    different answers that look identical in the data;
  * the tool refuses to write into `schemas/` (Operating Rule 1) -- a proposal
    may not enter the record on its own;
  * the denominator is the first line of output (Operating Rule 5).
"""
import io
import json
import os
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))

import confirm_sheet as cs  # noqa: E402


def ledger(rows):
    return {"rows": rows}


def row(cls, reached=1, governance="no signature found", corpus="not measured"):
    ladder = [{"state": "yes"}, {"state": "not measured"},
              {"state": "not measured"}, {"state": corpus}]
    return {"v1_class": cls,
            "stage": {"reached": reached, "ladder": ladder},
            "governance": {"state": governance}}


class Classification(unittest.TestCase):
    def test_a_new_target_set_is_CONFIRM(self):
        self.assertEqual(cs.classify("contrast_tuning",
                                     {"targets": ["tuning_curve_calculation"]}),
                         cs.B_CONFIRM)

    def test_emitting_only_its_own_name_is_a_PASSTHROUGH(self):
        self.assertEqual(cs.classify("epochfiles_ingested",
                                     {"targets": ["epochfiles_ingested"]}),
                         cs.B_PASSTHROUGH)

    def test_case_does_not_decide_a_passthrough(self):
        """NDI is camelCase and V_eta is snake_case; the comparison is normalised."""
        self.assertEqual(cs.classify("imageStack", {"targets": ["imagestack"]}),
                         cs.B_PASSTHROUGH)

    def test_a_passthrough_PLUS_a_real_target_is_not_a_passthrough(self):
        self.assertEqual(
            cs.classify("image_stack",
                        {"targets": ["image_stack", "image_observation"]}),
            cs.B_CONFIRM)

    def test_no_recorded_emission_is_its_own_bucket(self):
        self.assertEqual(cs.classify("filter", {"targets": [], "how": "x"}),
                         cs.B_NO_EMISSION)

    def test_absent_from_the_map_is_its_own_bucket(self):
        self.assertEqual(cs.classify("ontologyImage", None), cs.B_UNMAPPED)


class TheMapIsKeyedDifferentlyFromTheLedger(unittest.TestCase):
    """The third instance of one trap in a day, so it gets a test of its own.

    The ledger keys rows by the did_v1 class name (`demoNDI`, `ontologyImage`);
    `V_eta_migration_targets.json` is keyed the way the migrator FILES are named
    (`demo_ndi`, `ontology_image`). Looking up by the ledger spelling alone
    reported 8 classes as ABSENT FROM THE TARGET MAP when 7 were present all
    along -- and the direction is what makes it worth a test: it MANUFACTURES
    work, handing a reviewer seven classes to investigate that are already
    recorded.
    """

    def test_a_camelCase_class_finds_its_snake_case_row(self):
        m = {"demo_ndi": {"targets": ["demo"]}}
        self.assertEqual(cs.lookup(m, "demoNDI"), {"targets": ["demo"]})

    def test_an_exact_key_still_wins(self):
        m = {"demoNDI": {"targets": ["exact"]}, "demo_ndi": {"targets": ["snake"]}}
        self.assertEqual(cs.lookup(m, "demoNDI")["targets"], ["exact"])

    def test_a_genuinely_absent_class_is_still_absent(self):
        """The fix must not make everything findable."""
        self.assertIsNone(cs.lookup({"demo_ndi": {}}, "nothing_like_this"))

    def test_against_the_live_map_only_one_stage_row_is_unmapped(self):
        """`generic_file` folds in a batch post-pass and has no per-class row.

        Pinned as ONE so that a regression in `lookup` -- which would push this
        back to 8 -- fails here rather than showing up as seven phantom review
        items on the sheet.
        """
        led, tmap = cs.load(cs.LEDGER), cs.load(cs.TARGETS)["classes"]
        rows, _ = cs.build(led, tmap)
        unmapped = [r["v1_class"] for r in rows if r["bucket"] == cs.B_UNMAPPED]
        self.assertEqual(unmapped, ["generic_file"])


class EveryClassIsSorted(unittest.TestCase):
    def test_the_buckets_partition_the_stage(self):
        led = ledger([row("a"), row("b"), row("c"), row("d"),
                      row("elsewhere", reached=3)])
        tmap = {"a": {"targets": ["x"]}, "b": {"targets": ["b"]},
                "c": {"targets": []}}
        rows, unsorted = cs.build(led, tmap)
        self.assertEqual(unsorted, [])
        self.assertEqual(len(rows), 4, "a stage-1 class went missing")
        self.assertEqual({r["v1_class"] for r in rows}, {"a", "b", "c", "d"})
        self.assertEqual({r["bucket"] for r in rows},
                         {cs.B_CONFIRM, cs.B_PASSTHROUGH, cs.B_NO_EMISSION,
                          cs.B_UNMAPPED})

    def test_a_class_at_another_stage_is_not_swept_in(self):
        led = ledger([row("only_me", reached=2)])
        rows, unsorted = cs.build(led, {"only_me": {"targets": ["x"]}})
        self.assertEqual((rows, unsorted), ([], []))

    def test_the_denominator_is_the_first_line(self):
        buf = io.StringIO()
        cs.render([], [], 102, 1, out=buf)
        first = buf.getvalue().splitlines()
        self.assertIn("DENOMINATOR", first[1])
        self.assertIn("102 ledger row(s) read", first[1])

    def test_an_unsortable_class_is_NAMED_and_counted(self):
        buf = io.StringIO()
        cs.render([], ["mystery_class"], 102, 1, out=buf)
        text = buf.getvalue()
        self.assertIn("1 UNSORTED", text)
        self.assertIn("mystery_class", text)
        self.assertIn("FELL OUT OF EVERY BUCKET", text)


class ItRefusesToEnterTheRecord(unittest.TestCase):
    def test_writing_into_schemas_is_refused(self):
        target = os.path.join(REPO_ROOT, "schemas", "not_a_real_sheet.md")
        with self.assertRaises(SystemExit) as cm:
            cs.main(["--markdown", target])
        self.assertIn("Operating Rule 1", str(cm.exception))
        self.assertFalse(os.path.exists(target))

    def test_writing_elsewhere_is_allowed(self):
        tmp = tempfile.mkdtemp(prefix="confirm-sheet-")
        out = os.path.join(tmp, "sheet.json")
        cs.main(["--json", out])
        with open(out) as fh:
            blob = json.load(fh)
        self.assertTrue(blob["rows"], "the sheet came back empty")
        self.assertEqual(blob["unsorted"], [])

    def test_it_writes_no_signoff_line(self):
        """Operating Rule 4: Claude may propose, never decide."""
        tmp = tempfile.mkdtemp(prefix="confirm-sheet-")
        out = os.path.join(tmp, "sheet.md")
        cs.main(["--markdown", out])
        with open(out) as fh:
            body = fh.read()
        self.assertNotIn("TEAM-SIGN-OFF", body)
        with open(os.path.join(REPO_ROOT, "tools", "confirm_sheet.py")) as fh:
            src = fh.read()
        self.assertNotIn('"TEAM-SIGN-OFF:"', src)


class AgainstTheLiveLedger(unittest.TestCase):
    """The real data, so the sort cannot rot while the fixtures stay green."""

    def setUp(self):
        self.led = cs.load(cs.LEDGER)
        self.tmap = cs.load(cs.TARGETS)["classes"]

    def test_every_open_class_is_sorted(self):
        rows, unsorted = cs.build(self.led, self.tmap)
        self.assertEqual(unsorted, [],
                         "these classes would be reviewed by nobody")
        stage1 = [r for r in self.led["rows"] if r["stage"]["reached"] == 1]
        self.assertEqual(len(rows), len(stage1))

    def test_the_sheet_is_not_empty_and_not_everything(self):
        """A sort that put all 102 in one bucket would 'pass' every test above."""
        rows, _ = cs.build(self.led, self.tmap)
        counts = {b: sum(1 for r in rows if r["bucket"] == b) for b in cs.BUCKETS}
        self.assertGreater(counts[cs.B_CONFIRM], 0)
        self.assertGreater(counts[cs.B_PASSTHROUGH], 0)
        self.assertLess(max(counts.values()), len(rows),
                        "every class landed in one bucket -- the sort is inert")


if __name__ == "__main__":
    unittest.main()
