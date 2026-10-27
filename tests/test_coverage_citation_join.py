"""The DECISION flag, derived from each class's own citation.

REPLACES tests/test_coverage_signature_join.py (2026-10-21, Jess Haley: remove
the decision families; "nothing wrongly reported").

The old join went ledger row -> the decision FAMILY naming the row -> that
family's sign-off. It is gone. A class is now DECIDED if and only if it CITES a
decision line that exists: `tools/decision_citations.py` maps the class (by its
v1 name or its V_eta name) to (document, tag), and the citation RESOLVES when
that document holds an accepted

    TEAM-SIGN-OFF [tag]: ...                     (named by its tag), or
    TEAM-SIGN-OFF: ... <date> ...                (untagged: named by its date), or
    Decided by <team member>, <date> [tag]: ...  (named by its tag; the tag
                                                  is required and unique among
                                                  the document's Decided-by
                                                  lines, and the name must be
                                                  in the TEAM)

Anything else is "proposed (not decided)".

HOW THESE TESTS AVOID BEING WRITTEN FROM THE SAME PREMISE AS THE CODE
---------------------------------------------------------------------
Every citation is re-resolved here with a parser written in THIS file
(`_scan`), from the rule above -- never by calling the tool's scanner. If the
two disagree, one is wrong and the test says so rather than agreeing with
itself. The mutation tests then damage the tool and prove an invariant turns
red.
"""
import copy
import json
import os
import re
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))

import coverage  # noqa: E402
import decision_citations as dc  # noqa: E402
import doc_paths  # noqa: E402
import status_board  # noqa: E402

SCHEMAS = os.path.join(REPO_ROOT, "schemas")
DOCS = os.path.join(REPO_ROOT, "docs")
LEDGER_JSON = os.path.join(SCHEMAS, "did_v2_coverage_ledger.json")
LEDGER_MD = os.path.join(DOCS, "generated", "did_v2_coverage_ledger.md")

# 115: NDI-matlab#979 added lightsheetZarrPyramid + lightsheetZarrLevel (2026-10).
V1_UNIVERSE = 115


def _ledger():
    with open(LEDGER_JSON) as fh:
        return json.load(fh)


def _rows():
    return _ledger()["rows"]


def _gov():
    return _ledger()["summary"]["stage_rollup"]["governance"]


# ---------------------------------------------------------------------------
# THE SECOND OPINION -- a decision-line parser written here, from the rule.
# ---------------------------------------------------------------------------

TEMPLATE_SLOTS = ("<family>", "<tag>", "<who/when>", "<what was decided>")
_DATE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
# THE TEAM, written here from CLAUDE.md Operating Rule 4 -- not imported, so a
# change to the tool's list is a disagreement this file reports.
TEAM = {"Jess Haley", "Steve Van Hooser"}
_DECIDED_BY = re.compile(
    r"^(?:[-*>]\s+)?(?:\*\*)?Decided by ([^,]+?),\s*(\d{4}-\d{2}-\d{2})"
    r"\s*(?:\[([^\]]+)\])?\s*(?:\*\*)?\s*:\s*(.*)$")


def _path(document):
    return doc_paths.resolve(document)


def _scan_text(text):
    """[(line, keys, accepted)] for every decision line in `text`."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    lines = text.splitlines()
    out, fence, superseded = [], False, set()
    for n, raw in enumerate(lines, 1):
        line = raw.lstrip()
        if line.startswith("```"):
            fence = not fence
            continue
        m = re.match(r"SIGN-OFF SUPERSEDED\s*\[([^\]]+)\]", line)
        if m and not fence:
            superseded.add(m.group(1).strip())
            continue
        d = _DECIDED_BY.match(line)
        decided_by = bool(d)
        if d:
            who, tag, rest = d.group(1).strip(), d.group(3), d.group(4)
            tag = tag.strip() if tag else None
            # An untagged line, or one by someone outside the team, is not
            # a decision: it is named by nothing.
            keys = [tag] if (tag and who in TEAM) else []
        elif line.startswith("TEAM-SIGN-OFF"):
            rest = line[len("TEAM-SIGN-OFF"):].strip()
            tag = None
            mt = re.match(r"\[([^\]]+)\]\s*(.*)$", rest)
            if mt:
                tag, rest = mt.group(1).strip(), mt.group(2)
            rest = rest.lstrip(":").strip()
            if not rest:      # a bare `[tag]:` header continues below
                for nxt in lines[n:]:
                    s = nxt.strip()
                    if not s or s.startswith("TEAM-SIGN-OFF"):
                        break
                    rest += " " + s
                    if len(rest) > 20:
                        break
                rest = rest.strip()
            dm = _DATE.search(rest)
            keys = [tag] if tag else ([dm.group(1)] if dm else [])
        else:
            continue
        ok = not fence and not any(s in rest for s in TEMPLATE_SLOTS) \
            and len(rest) >= 10
        if ok and tag is not None and tag in superseded:
            superseded.discard(tag)
            ok = False
        out.append((n, keys, ok, decided_by))
    # A Decided-by tag on two lines names neither.
    dup = {}
    for n, keys, ok, dec in out:
        if ok and dec and keys:
            dup[keys[0]] = dup.get(keys[0], 0) + 1
    return [(n, keys, ok and not (dec and keys and dup.get(keys[0], 0) > 1))
            for n, keys, ok, dec in out]


def _resolve(document, tag):
    """The line number a citation resolves to, or None."""
    p = _path(document)
    if not os.path.exists(p):
        return None
    with open(p) as fh:
        for n, keys, ok in _scan_text(fh.read()):
            if ok and tag in keys:
                return n
    return None


def _decided_names():
    """Every name (v1 or V_eta) whose citation resolves, by this file's parser."""
    return {c for c, v in dc.CITATIONS.items()
            if any(_resolve(d, t) is not None for d, t in v)}


# ===========================================================================
# THE INVARIANTS.
# ===========================================================================

def check_every_decided_row_cites_a_real_line(rows):
    """Open the cited document at the cited line and read it."""
    for r in rows:
        g = r.get("governance") or {}
        if g.get("state") != coverage.G_SIGNED:
            continue
        hit = r.get("decided_by_citation")
        if not hit:
            continue          # a checked transcription; verified elsewhere
        n = _resolve(hit["document"], hit["tag"])
        assert n is not None, (
            f"{r['v1_class']}: decided via {hit['document']} [{hit['tag']}], "
            "which this file's own parser cannot resolve")
        assert n == hit["line"], (
            f"{r['v1_class']}: the tool says line {hit['line']}, this file's "
            f"parser says line {n}")


def check_only_resolved_citations_reach_a_row(rows):
    """A citation that names no decision line decides nothing."""
    for r in rows:
        hit = r.get("decided_by_citation")
        if hit:
            assert _resolve(hit["document"], hit["tag"]) is not None, (
                f"{r['v1_class']}: an UNRESOLVED citation reached the row")


def check_the_join_is_exact_and_two_namespaced(rows):
    """No substring, no normalisation, both namespaces offered."""
    decided = _decided_names()
    for r in rows:
        names = [n for n in (r["v1_class"], r.get("veta_class")) if n]
        want = any(n in decided for n in names)
        got = bool(r.get("decided_by_citation"))
        assert want == got, (
            f"{r['v1_class']}: a resolving citation names one of {names} = "
            f"{want}, but the row's join says {got}. An extra match is a "
            "substring or case-folded join; a missing one is a namespace the "
            "join forgot")


def check_no_row_is_joined_by_spelling_alone(rows):
    for r in rows:
        hit = r.get("decided_by_citation")
        if hit:
            assert hit["matched_name"] in (r["v1_class"], r.get("veta_class")), (
                f"{r['v1_class']}: matched on {hit['matched_name']!r}")


def check_governance_accounts_for_every_row(rows, gov):
    assert gov["denominator"] == len(rows)
    assert sum(gov["by_state"].values()) == len(rows), (
        "the decision histogram does not sum to the row count")
    for k in coverage.GOVERNANCE_STATES:
        assert k in gov["by_state"], f"bucket {k} missing"
    for r in rows:
        g = r.get("governance") or {}
        assert g.get("state") in coverage.GOVERNANCE_STATES, (
            f"{r['v1_class']}: state {g.get('state')!r}")
        assert g.get("why"), f"{r['v1_class']}: a state with no reason"


def check_every_unmoved_row_has_a_named_cause(rows, gov):
    j = gov["join"]
    unmoved = [r for r in rows if not (r.get("decided_by_citation")
                                       or r.get("decided_signoff")
                                       or r.get("no_target_signoff"))]
    assert sum(j["unmoved_by_cause"].values()) == len(unmoved)
    for r in unmoved:
        assert r.get("governance_gap"), f"{r['v1_class']}: no cause recorded"
    named = {n for v in j["unmoved_rows_by_cause"].values() for n in v}
    assert named == {r["v1_class"] for r in unmoved}


ALL_CHECKS_ON_ROWS = (
    check_every_decided_row_cites_a_real_line,
    check_only_resolved_citations_reach_a_row,
    check_the_join_is_exact_and_two_namespaced,
    check_no_row_is_joined_by_spelling_alone,
)


class TestTheCommittedLedger(unittest.TestCase):

    def setUp(self):
        self.rows = _rows()
        self.gov = _gov()
        self.assertEqual(len(self.rows), V1_UNIVERSE)

    def test_every_decided_row_cites_a_real_decision_line(self):
        check_every_decided_row_cites_a_real_line(self.rows)

    def test_only_resolved_citations_reach_a_row(self):
        check_only_resolved_citations_reach_a_row(self.rows)

    def test_the_join_is_exact_in_both_namespaces(self):
        check_the_join_is_exact_and_two_namespaced(self.rows)

    def test_no_row_is_joined_by_spelling_alone(self):
        check_no_row_is_joined_by_spelling_alone(self.rows)

    def test_governance_accounts_for_every_row(self):
        check_governance_accounts_for_every_row(self.rows, self.gov)

    def test_every_unmoved_row_has_a_named_cause(self):
        check_every_unmoved_row_has_a_named_cause(self.rows, self.gov)

    def test_every_citation_resolves(self):
        bad = [(c, d, t) for c, v in dc.CITATIONS.items() for d, t in v
               if _resolve(d, t) is None]
        self.assertEqual(bad, [], "a citation names no decision line")
        self.assertEqual(self.gov["census"]["citations_unresolved"], [])

    def test_the_counts_are_pinned(self):
        # Measured 2026-10-21 when the families were removed: 57 rows were
        # `signed` under the family join, 69 are `decided` under citations.
        # The 57 are all still decided at the same document:line; the 12 added
        # each cite a signed line that names the class (see
        # tools/decision_citations.py, the ADDED block). 69 -> 70 the same day:
        # `daqreader_mfdaq_epochdata_ingested` cites Jess's 2026-10-21 recording
        # decision ("Decided by Jess Haley", which names the
        # `daqreader_*_epochdata_ingested` archives). 70 -> 71 and DISPUTED
        # 1 -> 0 on 2026-10-23: `ngrid` resolved by [ngrid block into
        # sampled_body]. Re-derive, do not bump.
        st = self.gov["by_state"]
        self.assertEqual(st[coverage.G_SIGNED], 71)
        self.assertEqual(st[coverage.G_DISPUTED], 0)
        self.assertEqual(st[coverage.G_UNSIGNED], 0)
        self.assertEqual(st[coverage.G_NOT_FOUND], 44)

    def test_a_resolved_dispute_reads_as_decided(self):
        # `ngrid` was the last DISPUTED row; the team ruled on it 2026-10-23.
        ngrid = next(r for r in self.rows if r["v1_class"] == "ngrid")
        self.assertEqual(ngrid["governance"]["state"], coverage.G_SIGNED)

    def test_the_emitted_target_rows_are_counted_not_joined(self):
        j = self.gov["join"]
        for name in j["unmoved_rows_by_cause"].get(coverage.GAP_TARGET_ONLY, []):
            row = next(r for r in self.rows if r["v1_class"] == name)
            self.assertIsNone(row["decided_by_citation"],
                              f"{name} was joined through an emitted target")

    def test_the_markdown_carries_the_report(self):
        with open(LEDGER_MD) as fh:
            md = fh.read()
        self.assertIn("Decisions -- is each class DECIDED?", md)
        self.assertNotIn("no signature found", md.split(
            "Decisions -- is each class DECIDED?", 1)[1],
            "the ledger says 'no signature found'; the state is 'proposed "
            "(not decided)'")
        for cause in self.gov["join"]["unmoved_by_cause"]:
            self.assertIn(cause, md)
        census = self.gov["census"]
        for e in census["uncited_lines"]:
            self.assertIn("({}:{})".format(e["document"], e["line"]), md)

    def test_the_census_reports_its_denominator(self):
        c = self.gov["census"]
        docs = sorted(os.path.basename(p) for p in doc_paths.record_documents()
                      if os.path.basename(p) not in dc.GENERATED_MARKDOWN)
        outside = sorted({d for v in dc.CITATIONS.values() for d, _t in v
                          if "/" in d})
        self.assertEqual(c["documents_read"], len(docs) + len(outside))
        mine = 0
        for d in docs + outside:
            with open(_path(d)) as fh:
                mine += len(_scan_text(fh.read()))
        self.assertEqual(c["accepted_lines"] + len(c["rejected_lines"]), mine,
                         "accepted + rejected must equal every decision line")
        self.assertEqual(c["lines_cited"] + len(c["uncited_lines"]),
                         c["accepted_lines"])
        self.assertEqual(c["documents_excluded_as_generated"],
                         list(dc.GENERATED_MARKDOWN))

    def test_no_tagged_line_is_rejected_by_the_placeholder_guard(self):
        rejected = self.gov["census"]["rejected_lines"]
        tagged = [r for r in rejected if r["tag"]
                  and not r["why"].startswith(("SUPERSEDED",
                                               "inside a fenced code block"))]
        self.assertEqual(tagged, [])
        # The `<modality>_observation` signature is visible, not merely not
        # rejected (an empty list is also what a scanner reading nothing gives).
        self.assertEqual(_resolve("did_v2_recording_observation_plan.md",
                                  "raw recording observation"), 99)

    def test_the_generated_markdown_list_matches_what_gates_declares(self):
        with open(os.path.join(REPO_ROOT, "tools", "gates.py")) as fh:
            written = set(re.findall(r'"(docs/generated/[A-Za-z0-9_./]+\.md)"', fh.read()))
        self.assertEqual({os.path.basename(p) for p in written},
                         set(dc.GENERATED_MARKDOWN))


class TestTheReconciliation(unittest.TestCase):
    """The hand-carried transcriptions and the citations, checked together."""

    def test_the_reconciliation_is_non_vacuous(self):
        lines, fails = coverage.check_decision_citations()
        self.assertEqual(fails, [])
        den = [ln for ln in lines if "own decision citations" in ln]
        self.assertEqual(len(den), 1)
        self.assertIn("10 transcription(s)", den[0])
        # 8 -> 9 on 2026-10-21: `stimulus_bath` now cites the bath line its
        # transcription quotes (did_v2_go_forward_class_audit.md, "Decided by
        # Jess Haley, 2026-10-21"), so every transcription is reconciled.
        # 9 -> 10 on 2026-10-22: `control_stimulus_ids` dissolves ([control as
        # covariate], did_v2_stimulus_response_model_plan.md), and its citation
        # names the same line.
        self.assertIn("10 cite the same document", den[0],
                      "a reconciliation that matches nothing proves nothing")

    def test_the_table_still_carries_what_the_join_cannot(self):
        self.assertTrue(coverage.DECIDED_TARGETS_BY_SIGNOFF)
        for cls, entry in coverage.DECIDED_TARGETS_BY_SIGNOFF.items():
            self.assertTrue(entry[0], cls)


class TestTheRuleOnConstructedDocuments(unittest.TestCase):
    """The new line form and the old one, on fixtures, through the TOOL."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="decision-citations-")
        self.saved = dc.DOCS
        dc.DOCS = self.tmp

    def tearDown(self):
        dc.DOCS = self.saved

    def _doc(self, name, text):
        with open(os.path.join(self.tmp, name), "w") as fh:
            fh.write(text)
        return name

    def _read(self, name):
        with open(os.path.join(self.tmp, name)) as fh:
            return fh.read()

    def test_a_tagged_team_line_decides_by_its_tag(self):
        d = self._doc("a.md", "intro\n\nDecided by Jess Haley, 2026-10-21 "
                              "[foo fold]: the foo class folds into bar.\n")
        r = dc.resolve(d, "foo fold")
        self.assertTrue(r["resolved"], r)
        self.assertEqual((r["line"], r["kind"]), (3, dc.KIND_DECIDED_BY))
        self.assertEqual(dc.decision_for(["foo"], {"foo": [(d, "foo fold")]})
                         ["state"], dc.DECIDED)
        # Named by its tag only: the date names every decision of the day.
        self.assertFalse(dc.resolve(d, "2026-10-21")["resolved"])

    def test_every_team_member_decides(self):
        d = self._doc("b.md",
                      "- **Decided by Jess Haley, 2026-10-21 [foo fold]:** "
                      "foo folds into bar.\n"
                      "Decided by Steve Van Hooser, 2026-10-22 [baz fold]: "
                      "baz folds into qux.\n")
        self.assertTrue(dc.resolve(d, "foo fold")["resolved"])
        r = dc.resolve(d, "baz fold")
        self.assertTrue(r["resolved"], r)
        self.assertEqual(r["line"], 2)

    def test_the_team_is_kept_in_one_place(self):
        self.assertEqual(set(dc.TEAM), TEAM)
        self.assertTrue(dc.is_team_member("Steve  Van Hooser"))
        self.assertFalse(dc.is_team_member("jess"))

    def test_a_non_team_name_does_not_count(self):
        d = self._doc("n.md", "Decided by Claude, 2026-10-21 [foo fold]: "
                              "foo folds into bar.\n"
                              "Decided by jess, 2026-10-21 [bar fold]: "
                              "bar folds into baz.\n")
        for tag in ("foo fold", "bar fold"):
            r = dc.resolve(d, tag)
            self.assertFalse(r["resolved"], tag)
            self.assertIn("NOT A TEAM MEMBER", r["why"])
        # Reported, not dropped: both lines are in the census as rejected.
        rej = [e for e in dc.scan_decision_lines(self._read(d))
               if not e["accepted"]]
        self.assertEqual([e["line"] for e in rej], [1, 2])

    def test_an_untagged_decided_by_line_is_flagged_not_counted(self):
        d = self._doc("u.md", "Decided by Jess Haley, 2026-10-21: "
                              "the foo class folds into bar.\n")
        entries = dc.scan_decision_lines(self._read(d))
        self.assertEqual(len(entries), 1)
        self.assertFalse(entries[0]["accepted"])
        self.assertIn("UNTAGGED", entries[0]["rejected_because"])
        self.assertEqual(entries[0]["keys"], [])
        self.assertFalse(dc.resolve(d, "2026-10-21")["resolved"])
        # The census reports it among the rejected lines.
        census = dc.decision_census(docs_dir=self.tmp, table={})
        self.assertEqual([(r["document"], r["line"]) for r in
                          census["rejected_lines"]], [(d, 1)])
        self.assertEqual(census["accepted_lines"], 0)

    def test_tagged_lines_resolve_uniquely(self):
        d = self._doc("t.md",
                      "Decided by Jess Haley, 2026-10-21 [one]: first decision.\n"
                      "Decided by Jess Haley, 2026-10-21 [two]: second decision.\n"
                      "Decided by Steve Van Hooser, 2026-10-22 [dup]: a decision.\n"
                      "Decided by Jess Haley, 2026-10-23 [dup]: another decision.\n")
        self.assertEqual(dc.resolve(d, "one")["line"], 1)
        self.assertEqual(dc.resolve(d, "two")["line"], 2)
        self.assertEqual(dc.resolve(d, "one")["matches"], 1)
        r = dc.resolve(d, "dup")
        self.assertFalse(r["resolved"])
        self.assertIn("TAG NOT UNIQUE", r["why"])

    def test_every_real_decided_by_line_is_tagged_unique_and_by_the_team(self):
        """The record itself: no `Decided by` line under docs/ or review/
        is rejected for its name, a missing tag or a shared tag."""
        bad = []
        for root in (DOCS, os.path.join(REPO_ROOT, "review")):
            for dirpath, _dirs, files in os.walk(root):
                for f in files:
                    if not f.endswith(".md") or f in dc.GENERATED_MARKDOWN:
                        continue
                    with open(os.path.join(dirpath, f), encoding="utf-8") as fh:
                        for e in dc.scan_decision_lines(fh.read()):
                            if (e["kind"] == dc.KIND_DECIDED_BY
                                    and not e["accepted"]
                                    and e["rejected_because"].startswith(
                                        ("NOT A TEAM", "UNTAGGED", "TAG NOT UNIQUE"))):
                                bad.append((f, e["line"], e["rejected_because"]))
        self.assertEqual(bad, [])

    def test_a_team_signoff_line_still_decides(self):
        d = self._doc("c.md", "TEAM-SIGN-OFF [foo]: jess, 2026-08-01 -- foo is bar.\n"
                              "TEAM-SIGN-OFF: jess, 2026-08-02 -- untagged, by date.\n")
        self.assertTrue(dc.resolve(d, "foo")["resolved"])
        self.assertTrue(dc.resolve(d, "2026-08-02")["resolved"])
        # A tagged line is NOT named by its date: the tag is its name.
        self.assertFalse(dc.resolve(d, "2026-08-01")["resolved"])

    def test_what_is_not_a_decision(self):
        d = self._doc("d.md", (
            "Decided by jess, 2026-10-21 [jess]: not a team member's name.\n"
            "Decided by Jess Haley, <date>: <what was decided>\n"
            "```\n"
            "Decided by Jess Haley, 2026-10-22: a quotation.\n"
            "TEAM-SIGN-OFF [quoted]: jess, 2026-08-01 -- a quotation.\n"
            "```\n"
            "<!-- Decided by Jess Haley, 2026-10-23: inside a comment. -->\n"
            "SIGN-OFF SUPERSEDED [old]: jess 2026-09-01 -- replaced\n"
            "TEAM-SIGN-OFF [old]: jess, 2026-08-01 -- superseded.\n"
            "TEAM-SIGN-OFF [tiny]: x\n"
            "Proposed (not decided): foo folds into bar.\n"))
        for tag in ("2026-10-21", "2026-10-22", "2026-10-23", "quoted", "old",
                    "tiny", "<date>", "jess"):
            self.assertFalse(dc.resolve(d, tag)["resolved"], tag)
        dec = dc.decision_for(["foo"], {"foo": [(d, "old"), (d, "2026-10-21")]})
        self.assertEqual(dec["state"], dc.PROPOSED)
        self.assertEqual(len(dec["unresolved"]), 2)

    def test_no_citation_is_proposed(self):
        self.assertEqual(dc.decision_for(["nothing"], {})["state"], dc.PROPOSED)

    def test_a_missing_document_does_not_resolve(self):
        r = dc.resolve("no_such_plan.md", "foo")
        self.assertFalse(r["resolved"])
        self.assertIn("does not exist", r["why"])


# ===========================================================================
# MUTATION TESTS. Damage the join; prove an invariant turns red.
# ===========================================================================


class _Swap:
    def __init__(self, module, **attrs):
        self.module, self.attrs, self.saved = module, attrs, {}

    def __enter__(self):
        for k, v in self.attrs.items():
            self.saved[k] = getattr(self.module, k)
            setattr(self.module, k, v)
        return self

    def __exit__(self, *exc):
        for k, v in self.saved.items():
            setattr(self.module, k, v)
        return False


def _rejoin(rows):
    """Re-run the derivation over rows, exactly as build_ledger does."""
    out = []
    for r in copy.deepcopy(rows):
        hit, cites = coverage.citation_for_row(r["v1_class"], r["veta_class"])
        r["decided_by_citation"] = hit
        r["decision_citations"] = cites
        r["governance_gap"] = coverage.governance_gap(r)
        r["governance"] = coverage.governance_state(r)
        out.append(r)
    return out


class TestMutationsRedden(unittest.TestCase):

    def _assert_reddens(self, swap):
        with swap:
            mutated = _rejoin(_rows())
            caught = []
            for check in ALL_CHECKS_ON_ROWS:
                try:
                    check(mutated)
                except AssertionError as exc:
                    caught.append((check.__name__, str(exc).splitlines()[0]))
        self.assertTrue(caught, "MUTATION PRODUCED NO FAILURE")
        return [c[0] for c in caught]

    def test_a_resolver_that_accepts_everything_reddens(self):
        # THE OPERATING-RULE-4 MUTATION: every citation counts, signed or not.
        # A bogus citation for an undecided class makes the difference visible.
        table = dict(dc.CITATIONS)
        table["measurement"] = [("did_v2_tenets.md", "no such decision")]

        def always(document, tag):
            return {"document": document, "tag": tag, "resolved": True,
                    "line": 1, "kind": dc.KIND_SIGNOFF, "decision": "x",
                    "matches": 1, "why": None}
        with _Swap(dc, CITATIONS=table):
            caught = self._assert_reddens(_Swap(dc, resolve=always))
        self.assertIn("check_only_resolved_citations_reach_a_row", caught)

    def test_an_unresolved_citation_never_decides(self):
        table = dict(dc.CITATIONS)
        table["measurement"] = [("did_v2_tenets.md", "no such decision")]
        with _Swap(dc, CITATIONS=table):
            row = next(r for r in _rejoin(_rows()) if r["v1_class"] == "measurement")
        self.assertIsNone(row["decided_by_citation"])
        self.assertEqual(row["governance"]["state"], coverage.G_UNSIGNED)
        self.assertEqual(row["governance_gap"], coverage.GAP_CITATION_UNRESOLVED)

    def test_matching_on_a_SUBSTRING_instead_of_the_whole_name_reddens(self):
        real = dc.decision_for

        def loose(names, table=None):
            table = dc.CITATIONS if table is None else table
            grown = list(names)
            for n in names:
                grown += [k for k in table if k in n and k != n]
            return real(grown, table)
        caught = self._assert_reddens(_Swap(dc, decision_for=loose))
        self.assertIn("check_the_join_is_exact_and_two_namespaced", caught)

    def test_normalising_the_spelling_before_matching_reddens(self):
        real = dc.decision_for

        def folded(names, table=None):
            table = dc.CITATIONS if table is None else table
            want = {coverage._normalised(n) for n in names}
            return real([k for k in table if coverage._normalised(k) in want]
                        + list(names), table)
        # `demoNDI` would join a citation of `demo_ndi`; construct one.
        table = dict(dc.CITATIONS)
        table["demo_ndi"] = [("did_v2_epoch_plan.md", "epoch")]
        with _Swap(dc, CITATIONS=table):
            caught = self._assert_reddens(_Swap(dc, decision_for=folded))
        self.assertTrue(caught)

    def test_a_transcription_contradicting_the_citation_is_FATAL(self):
        table = dict(dc.CITATIONS)
        table["filter"] = [("did_v2_epoch_plan.md", "epoch")]
        with _Swap(dc, CITATIONS=table):
            _lines, fails = coverage.check_decision_citations()
        self.assertTrue(any("filter" in f for f in fails), fails)

    def test_the_board_fails_on_an_unresolved_citation(self):
        table = dict(dc.CITATIONS)
        table["app"] = [("did_v2_tenet_audit.md", "no such decision")]
        with _Swap(dc, CITATIONS=table):
            text, ok = status_board.build()
        self.assertFalse(ok)
        self.assertIn("ERROR -- citations that do not resolve", text)
        self.assertIn("`app`", text.split("## Where V_eta stands", 1)[0])


if __name__ == "__main__":
    unittest.main()
