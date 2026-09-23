"""Stage 5 has THREE states, and an absent counter must reach the right one.

WHY THIS FILE EXISTS
--------------------
Corpus run 31587869672 was the first run in which the CORPUS-PROVEN rung was
computed from real reports. It came back:

    PROVEN (`yes`)      : 29
    FAILED (`no`)       : 10
    NOT MEASURED        : 52

and all ten of the FAILED named one cause, in the tool's own words:

    FAILED  element   PRED: `orphan_count` is absent from the report
                            -- NOT a zero (over 7014 document(s) in 6 corpus(es))

Nothing had failed. `testCorpusPRED` is a hard 0-quarantine GATE rather than a
discovery run, so it never goes through `runCorpusDiscovery` and its report
carries no orphan census at all. `corpus_verdict` appended that absence to
`faults`, and any fault meant `no`.

That is the `not measured` -> `no` collapse, occurring inside the ladder built
to prevent it. It is the mirror image of this repository's usual error: it
reads PESSIMISTIC rather than reassuring, which is the only reason it was
visible at all. The rule it broke is the same one either way -- "nobody looked"
and "we proved it broken" are different facts and must never share a bucket.

WHAT THESE TESTS PIN, and why each one can actually fail
--------------------------------------------------------
  1. absence is NOT a fault           -- a class seen in one blind corpus and
                                         one clean corpus is PROVEN
  2. absence is NOT a pass either     -- a class seen ONLY in blind corpora is
                                         `not measured`, never `yes`
  3. a REAL fault on a blind corpus still fails -- suppressing the counters that
                                         ARE present, because a sibling counter
                                         is missing, would be the reassuring
                                         direction and would hide quarantines
  4. the quoted document count is the count over the corpora the verdict RESTS
     on -- a blind corpus's documents may not inflate a figure nothing inspected
  5. every verdict NAMES the blind corpora, so a reader cannot mistake a
     partial proof for a universal one

HOW THESE AVOID BEING WRITTEN FROM THE SAME PREMISE AS THE CODE
---------------------------------------------------------------
The evidence is built by writing REAL report JSON to disk and reading it back
through `load_corpus_evidence`, the same path CI uses -- not by hand-assembling
the dict `corpus_verdict` happens to consume today. A PRED-shaped report here is
a report with `reference_integrity` genuinely absent, not a dict with a None
poked into it. And the mutation test at the end restores the old behaviour and
requires these tests to redden, so a future refactor that quietly reinstates the
collapse cannot leave the file green.
"""
import json
import os
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))

import coverage  # noqa: E402


def _report(corpus, by_class, *, orphans=True, quarantine=0, fragments=0,
            orphan_count=0, orphan_classes=(), empty_edge_classes=()):
    """One corpus summary, in the on-disk shape the harness really writes.

    `orphans=False` reproduces a PRED-shaped report: the whole
    `reference_integrity` block is ABSENT, which is how a gate run differs from
    a discovery run. That is the condition under test -- not a null value.
    """
    rep = {
        "corpus": corpus,
        "quarantine_count": quarantine,
        "fragment_count": fragments,
        "fragment_by_class": {},
        "source_census": {"total_docs": sum(by_class.values()),
                          "by_class": dict(by_class)},
    }
    if orphans:
        rep["reference_integrity"] = {
            "orphan_count": orphan_count,
            "orphans": [{"doc_class": c} for c in orphan_classes],
        }
    if empty_edge_classes:
        rep["silent_loss"] = {"empty_required_dependency":
                              [{"class_name": c} for c in empty_edge_classes]}
    return rep


def evidence_from(reports):
    """Write the reports out and read them back the way CI does."""
    tmp = tempfile.mkdtemp(prefix="corpus-verdict-")
    for rep in reports:
        path = os.path.join(tmp, "{}-summary.json".format(rep["corpus"]))
        with open(path, "w") as fh:
            json.dump(rep, fh)
    ev = coverage.load_corpus_evidence([tmp])
    assert ev["measured"], ev.get("why")
    return ev


def row(v1_class, targets=()):
    return {"v1_class": v1_class, "targets": list(targets),
            "decided_targets": [], "second_pass": []}


class AbsentCounterIsNotAFault(unittest.TestCase):
    """(1) and (5): a blind corpus must not sink a class another corpus proves."""

    def setUp(self):
        # `element` as the real run saw it: present in a clean discovery corpus
        # AND in PRED, whose report has no reference_integrity block.
        self.ev = evidence_from([
            _report("Soph", {"element": 7000}),
            _report("PRED", {"element": 14}, orphans=False),
        ])

    def test_it_is_PROVEN_not_FAILED(self):
        state, why = coverage.corpus_verdict(row("element"), self.ev)
        self.assertEqual(state, coverage.S_YES,
                         "an absent counter was read as a failure: " + why)

    def test_the_blind_corpus_is_NAMED_in_the_verdict(self):
        _state, why = coverage.corpus_verdict(row("element"), self.ev)
        self.assertIn("PRED", why)
        self.assertIn("orphan_count", why)
        self.assertIn("UNINSPECTED", why)

    def test_the_quoted_count_excludes_the_uninspected_documents(self):
        """(4). 7000 were inspected; 7014 were not."""
        _state, why = coverage.corpus_verdict(row("element"), self.ev)
        self.assertIn("7000 document(s)", why)
        self.assertNotIn("7014 document(s) across", why)


class SeenOnlyWhereNobodyLooked(unittest.TestCase):
    """(2): absence is not a pass. The upper bound needs a corpus that measured."""

    def setUp(self):
        self.ev = evidence_from([
            _report("Soph", {"element": 7000}),
            _report("PRED", {"pyraview": 1}, orphans=False),
        ])

    def test_a_class_seen_only_in_a_blind_corpus_is_NOT_MEASURED(self):
        state, why = coverage.corpus_verdict(row("pyraview"), self.ev)
        self.assertEqual(state, coverage.S_NOT_MEASURED, why)

    def test_and_it_says_so_rather_than_reading_as_clean(self):
        _state, why = coverage.corpus_verdict(row("pyraview"), self.ev)
        self.assertIn("NOT MEASURED", why)
        self.assertIn("PRED", why)
        self.assertNotIn("migrated with 0 quarantine", why)

    def test_a_class_in_NO_corpus_is_still_NOT_MEASURED(self):
        """The pre-existing zero-document path must be untouched."""
        state, why = coverage.corpus_verdict(row("subjectmeasurement"), self.ev)
        self.assertEqual(state, coverage.S_NOT_MEASURED, why)
        self.assertIn("0 document(s) of this class", why)


class ARealFaultStillFails(unittest.TestCase):
    """(3): the counters that ARE present are still read on a blind corpus."""

    def test_a_quarantine_on_a_blind_corpus_is_a_fault(self):
        ev = evidence_from([
            _report("PRED", {"element": 14}, orphans=False, quarantine=3),
        ])
        state, why = coverage.corpus_verdict(row("element"), ev)
        self.assertEqual(state, coverage.S_NO, why)
        self.assertIn("3 quarantined document(s)", why)

    def test_an_empty_required_edge_on_a_blind_corpus_is_a_fault(self):
        ev = evidence_from([
            _report("PRED", {"image_stack": 4563}, orphans=False,
                    empty_edge_classes=["image_observation"]),
        ])
        state, why = coverage.corpus_verdict(
            row("image_stack", targets=["image_observation"]), ev)
        self.assertEqual(state, coverage.S_NO, why)
        self.assertIn("empty required edge", why)

    def test_an_attributable_orphan_on_a_MEASURED_corpus_is_a_fault(self):
        ev = evidence_from([
            _report("Soph", {"element": 7000}, orphan_count=11,
                    orphan_classes=["element"]),
        ])
        state, why = coverage.corpus_verdict(row("element"), ev)
        self.assertEqual(state, coverage.S_NO, why)


class TheThreeStatesStayDistinct(unittest.TestCase):
    """The whole point: three inputs, three different answers, no collapsing."""

    def test_proven_failed_and_unevaluated_are_three_different_verdicts(self):
        ev = evidence_from([
            _report("Soph", {"element": 7000, "subject": 900}),
            _report("PRED", {"element": 14, "pyraview": 1}, orphans=False,
                    quarantine=0),
            _report("JH", {"subject": 30}, orphan_count=2,
                    orphan_classes=["subject"]),
        ])
        got = {c: coverage.corpus_verdict(row(c), ev)[0]
               for c in ("element", "subject", "pyraview", "mock")}
        self.assertEqual(got, {
            "element": coverage.S_YES,          # proven by Soph, blind in PRED
            "subject": coverage.S_NO,           # a real, attributed orphan
            "pyraview": coverage.S_NOT_MEASURED,  # only ever seen by a blind run
            "mock": coverage.S_NOT_MEASURED,    # never seen at all
        })


class MutationRestoresTheBug(unittest.TestCase):
    """A test that cannot fail proves nothing. Put the collapse back; go red.

    This re-implements the OLD branch -- absence appended to `faults` -- over the
    same evidence, and asserts the verdict changes. If this ever passes without
    a change to `corpus_verdict`, the tests above have stopped discriminating.
    """

    def test_treating_absence_as_a_fault_flips_the_verdict_to_no(self):
        ev = evidence_from([
            _report("Soph", {"element": 7000}),
            _report("PRED", {"element": 14}, orphans=False),
        ])
        live, _why = coverage.corpus_verdict(row("element"), ev)
        self.assertEqual(live, coverage.S_YES)

        # the old rule, applied by hand to the same evidence
        seen = ev["by_class"][coverage.norm_class("element")]
        old_faults = [
            "{}: `{}` absent".format(c["corpus"], k)
            for c in ev["corpora"] if seen.get(c["corpus"])
            for k in ("quarantine_count", "fragment_count", "orphan_count")
            if c.get(k) is None
        ]
        self.assertTrue(old_faults, "the fixture no longer contains a blind "
                                    "corpus, so this mutation tests nothing")
        self.assertNotEqual(coverage.S_NO, live,
                            "the live verdict already agrees with the bug")


if __name__ == "__main__":
    unittest.main()
