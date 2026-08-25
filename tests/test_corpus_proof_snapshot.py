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


class ZeroReportSourceCase(unittest.TestCase):
    """A run that MEASURED NOTHING must decline in words, not crash.

    THE PRODUCTION FAILURE, run 31888793256 (2026-08-15). All six corpus jobs
    were cancelled, so `corpus_proven.py` found no reports, exited 1, and STILL
    wrote its json -- the document carries the instrument faults that explain
    the emptiness, so writing it is correct. That json has a `rung` carrying
    nothing and no `rows`, and this tool raised:

        ValueError: the source names no per-class verdicts

    THE GRACEFUL PATH EXISTED AND WAS UNREACHABLE. `main()`'s anti-clobber rule
    already handled "the source measured 0 classes" in words, and the workflow
    step's comment promises exactly that ("a run that measured nothing cannot
    erase the last one that did"). But `ingest()` raised BEFORE `main()`
    computed the count, so the promised refusal could only fire for a source
    that parsed to an empty map -- never for the one shape a zero-report run
    actually produces.

    AND IT WAS INVISIBLE: the step carries `continue-on-error: true`, so the
    crash rendered as a GREEN step. A tool that dies and reports success is the
    silentLoss shape. It was found by reading the log line by line, which is
    why this case is pinned rather than left to the next reader.
    """

    def zero_report_doc(self):
        """The shape run 31888793256 produced, in the WRITER's vocabulary.

        Keys are the ones `corpus_proven.py` writes unconditionally in
        `publish()` -- `tool`, `instrument_faults`, `exit_code` -- which is
        also what tells a recognised-but-empty document apart from a wrong
        file. Built from the writer's key list, not from the reader's guess."""
        return {
            "tool": "DID-matlab tools/corpus_proven.py",
            "rung": {},
            "corpora": [],
            "instrument_faults": [
                ("NO CORPUS REPORTS FOUND. 2 root(s) named, 2 of them "
                 "missing, 0 director(ies) walked.")],
            "exit_code": 1,
        }

    def test_a_recognised_but_empty_source_yields_no_verdicts_without_raising(self):
        classes, rung = SNAP.verdicts(self.zero_report_doc())
        self.assertEqual(classes, {})
        self.assertEqual(rung, {})

    def test_a_wrong_shaped_file_still_raises(self):
        """The narrowing must not become a blanket. `verdicts` returning {} for
        anything unparseable is what the function's own docstring argues
        against: a writer whose shape changed under us would look like a quiet
        weekend."""
        with self.assertRaises(ValueError):
            SNAP.verdicts({"not": "a corpus_proven document"})

    def test_the_faults_are_carried_so_the_refusal_can_say_why(self):
        faults = SNAP.source_faults(self.zero_report_doc())
        self.assertEqual(len(faults), 1)
        self.assertIn("NO CORPUS REPORTS FOUND", faults[0])

    def test_a_source_that_measured_nothing_and_named_no_reason_is_still_empty(self):
        """Zero faults is not an error here -- it is a DIFFERENT report.

        The refusal prints `0 instrument fault(s)` with a note that measuring
        nothing without saying why is itself worth chasing. Silence about the
        reason must not be dressed up as a reason."""
        doc = self.zero_report_doc()
        doc["instrument_faults"] = []
        self.assertEqual(SNAP.verdicts(doc)[0], {})
        self.assertEqual(SNAP.source_faults(doc), [])

    def test_refusing_writes_nothing_even_with_no_committed_snapshot(self):
        """The condition was `got == 0 and have > 0`; with `have == 0` the old
        code fell through and WROTE a snapshot carrying zero verdicts -- a file
        that looks like evidence and asserts nothing, in a repository whose
        complaint is that its record says nothing has been proven."""
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            src = os.path.join(td, "v_eta_corpus_proven.json")
            with open(src, "w") as fh:
                json.dump(self.zero_report_doc(), fh)
            snap = os.path.join(td, "V_eta_corpus_proof.json")
            old_snap, old_md = SNAP.SNAPSHOT, SNAP.SNAPSHOT_MD
            SNAP.SNAPSHOT = snap
            SNAP.SNAPSHOT_MD = os.path.join(td, "V_eta_corpus_proof.md")
            try:
                argv = sys.argv
                sys.argv = ["corpus_proof_snapshot.py", "--from", src]
                try:
                    rc = SNAP.main()
                finally:
                    sys.argv = argv
            finally:
                SNAP.SNAPSHOT, SNAP.SNAPSHOT_MD = old_snap, old_md
            self.assertEqual(rc, 1, "an empty source must not exit 0")
            self.assertFalse(os.path.exists(snap),
                             "an empty source must write NO snapshot at all")
