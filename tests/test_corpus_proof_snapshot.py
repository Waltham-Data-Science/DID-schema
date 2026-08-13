"""`corpus_proof_snapshot.py` against the shape its SOURCE actually writes.

WHY THIS FILE EXISTS. The tool shipped with no tests and crashed on every real
document it was ever handed:

    File ".../did-schema/tools/corpus_proof_snapshot.py", line 88, in ingest
        for r in rows:
    TypeError: 'int' object is not iterable

It read `rung.rows` as a list of per-class rows. DID-matlab's
`corpus_proven.py` sets `doc["rung"] = state["rung"]`, the TALLY, whose `rows`
is `len(rows)` -- a count. The reader was written from a CI log rather than
from the writer, and nothing compared the two. That is the migrator
ground-truth rule (`where template and WRITER disagree, the WRITER wins`) one
layer up, in Python.

SO THE FIXTURE IS BUILT BY THE WRITER, NOT BY THIS FILE. `test_the_writers_own
_document_ingests` drives DID-matlab's `analyse()` and `publish()` to produce a
real `v_eta_corpus_proven.json` and feeds THAT to the reader. A fixture I typed
here would agree with whatever premise I held while fixing the bug -- the
failure this repository has already recorded as "a test written from the same
premise as the code cannot catch the code", where three tests asserted the
`epochid` bug and had to be INVERTED rather than patched.

THE SIBLING-ABSENT SKIP IS ANNOUNCED. A silent skip would make this file a
vacuous instrument on any machine without DID-matlab, which is most of them;
the shape tests below run unconditionally so something still fails if the
reader regresses.
"""
import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA_ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(SCHEMA_ROOT, "tools"))

import corpus_proof_snapshot as SNAP  # noqa: E402


def find_did_matlab():
    """The sibling checkout, by the same precedence coverage.py uses."""
    for cand in (os.environ.get("DID_MATLAB"),
                 os.path.join(os.path.dirname(SCHEMA_ROOT), "DID-matlab"),
                 "/home/user/DID-matlab"):
        if cand and os.path.isdir(os.path.join(cand, "tools")):
            return cand
    return None


class WriterShapeCase(unittest.TestCase):
    """The regression, stated in the writer's vocabulary."""

    def tally(self, **kw):
        """The `rung` block corpus_proven.py publishes: a TALLY, not rows.

        Keys taken from its own construction --
            tally = {"rows": len(rows), "with_state": 0, "yes": 0, "no": 0,
                     "not_measured": 0, "unknown": 0, "absent_from_corpora": 0,
                     "yes_classes": [], "no_rows": []}
        """
        rung = {"rows": 102, "with_state": 12, "yes": 10, "no": 2,
                "not_measured": 5, "unknown": 0, "absent_from_corpora": 5,
                "yes_classes": ["element", "pyraview", "session"],
                "no_rows": [{"v1_class": "image_stack", "why": "orphans"}]}
        rung.update(kw)
        return {"rung": rung}

    def write(self, doc):
        path = os.path.join(self.tmp, "v_eta_corpus_proven.json")
        with open(path, "w") as fh:
            json.dump(doc, fh)
        return path

    def setUp(self):
        import tempfile
        self.tmp = tempfile.mkdtemp()

    def test_an_integer_row_count_is_not_iterated(self):
        # THE BUG. `rung.rows` is 102, an int; the old reader did `for r in rows`.
        blob = SNAP.ingest(self.write(self.tally()), run="r", sha="s")
        self.assertEqual(blob["counts"]["proven"], 3)
        self.assertEqual(blob["counts"]["failed"], 1)
        self.assertEqual(blob["classes"]["element"]["state"], SNAP.S_YES)
        self.assertEqual(blob["classes"]["image_stack"]["state"], SNAP.S_NO)

    def test_rows_read_is_the_sources_denominator_not_the_map_size(self):
        # 102 rows were walked; 4 classes are NAMED. Reporting 4 as `rows read`
        # would shrink the universe silently -- the `find_repo` failure mode.
        blob = SNAP.ingest(self.write(self.tally()), run="r", sha="s")
        self.assertEqual(blob["counts"]["rows_read"], 102)
        self.assertEqual(blob["counts"]["classes_named"], 4)

    def test_not_measured_is_carried_from_the_tally_never_counted_off_the_map(self):
        # The source counts 5 and names none of them. Counting the map gives 0,
        # and 0 reads as "none unmeasured" -- `not measured` collapsing into a
        # verdict, which is the one thing this project's ladder forbids.
        blob = SNAP.ingest(self.write(self.tally()), run="r", sha="s")
        self.assertEqual(blob["counts"]["not_measured"], 5)
        named = [n for n, v in blob["classes"].items()
                 if v["state"] == SNAP.S_NOT_MEASURED]
        self.assertEqual(named, [])
        self.assertIn("never `no`", blob["limits"])

    def test_an_unrecognised_shape_raises_instead_of_returning_empty(self):
        # An empty ingest hits the anti-clobber rule and prints REFUSING TO
        # WRITE, which is indistinguishable from the safe no-op it exists to be.
        # A writer whose shape moved must be loud.
        with self.assertRaises(ValueError) as caught:
            SNAP.ingest(self.write({"rung": {"rows": 102}}))
        self.assertIn("yes_classes", str(caught.exception))

    def test_a_list_of_rows_still_works(self):
        # The shape the tool was written for. No writer emits it; it costs one
        # isinstance and a list is unambiguous.
        path = self.write({"rows": [{"v1_class": "element", "state": "yes"},
                                    {"v1_class": "ngrid", "state": "no",
                                     "why": "quarantined"}]})
        blob = SNAP.ingest(path)
        self.assertEqual(blob["counts"]["proven"], 1)
        self.assertEqual(blob["counts"]["failed"], 1)

    def test_the_markdown_says_the_unmeasured_are_unnamed(self):
        md = SNAP.render_md(SNAP.ingest(self.write(self.tally())))
        self.assertIn("UNNAMED HERE", md)
        self.assertIn("`element`", md)


class WritersOwnDocumentCase(unittest.TestCase):
    """End to end, with DID-matlab's writer producing the file."""

    def test_the_writers_own_document_ingests(self):
        didm = find_did_matlab()
        if didm is None:
            self.skipTest(
                "DID-matlab sibling not found (tried $DID_MATLAB, "
                "../DID-matlab, /home/user/DID-matlab) -- the writer-authored "
                "fixture cannot be built here. The WriterShapeCase tests above "
                "still ran.")
        # Drive the writer in a subprocess so its sys.path games and cwd
        # assumptions stay its own. It builds a report, runs analyse() with a
        # stubbed coverage interface, and publishes -- the same publish() the
        # census job calls.
        script = r'''
import json, os, sys, tempfile
sys.path.insert(0, os.path.join(DID_MATLAB, "tools"))
from corpus_proven import analyse, publish, norm_class

out = tempfile.mkdtemp()
reports = os.path.join(out, "corpus-reports")
os.makedirs(reports)
rep = {"corpus": "PRED", "total": 14, "migrated_count": 14,
       "quarantine_count": 0, "by_class": {"subject": 1},
       "quarantine_reasons": [], "fragment_count": 0, "fragment_by_class": {},
       "silent_loss": {"empty_required_dependency": []},
       "reference_integrity": {"edges_examined": 50, "orphans": [],
                               "orphan_count": 0},
       "source_census": {"total_docs": 14, "skipped_docs": 0,
                         "by_class": {norm_class("element"): 7,
                                      norm_class("pyraview"): 7}}}
with open(os.path.join(reports, "PRED-summary.json"), "w") as fh:
    json.dump(rep, fh)

schema = os.path.join(out, "did-schema", "schemas")
os.makedirs(schema)
rows = [{"v1_class": c, "targets": [c], "decided_targets": [],
         "second_pass": [],
         "stage": {"corpus_rung_state": s,
                   "ladder": [{"stage": 4, "name": "CORPUS-PROVEN",
                               "state": s, "why": ""}]}}
        for c, s in (("element", "yes"), ("pyraview", "yes"),
                     ("ngrid", "not measured"))]
with open(os.path.join(schema, "V_eta_coverage_ledger.json"), "w") as fh:
    json.dump({"rows": rows}, fh)

stub = lambda repo, roots: {"ran": True, "exit_code": 0, "stdout": ""}
cwd = os.getcwd()
os.chdir(out)
try:
    state = analyse([reports], os.path.join(out, "did-schema"),
                    run_coverage_fn=stub)
    publish(state, os.path.join(out, "corpus-proven"),
            os.path.join(out, "did-schema"), [])
finally:
    os.chdir(cwd)
print(os.path.join(out, "corpus-proven", "v_eta_corpus_proven.json"))
'''
        script = f"DID_MATLAB = {didm!r}\n" + script
        proc = subprocess.run([sys.executable, "-c", script],
                              capture_output=True, text=True,
                              check=False)
        if proc.returncode != 0:
            self.fail("the writer could not be driven -- this test is then "
                      "measuring nothing, so it fails rather than skips:\n"
                      + proc.stderr[-2000:])
        source = proc.stdout.strip().splitlines()[-1]

        # THE ASSERTION THAT MATTERS: the reader survives the writer's real
        # document. Before the fix this raised TypeError here.
        blob = SNAP.ingest(source, run="31744202105", sha="d6f14cd")
        with open(source) as fh:
            raw = json.load(fh)
        self.assertIsInstance(raw["rung"]["rows"], int,
                              "the writer's `rung.rows` stopped being a count "
                              "-- re-read verdicts() before trusting this test")
        self.assertEqual(blob["counts"]["rows_read"], raw["rung"]["rows"])
        self.assertEqual(blob["counts"]["proven"], raw["rung"]["yes"])
        self.assertEqual(blob["counts"]["failed"], raw["rung"]["no"])
        self.assertEqual(blob["counts"]["not_measured"],
                         raw["rung"]["not_measured"])


if __name__ == "__main__":
    unittest.main()
