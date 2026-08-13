"""The GOVERNANCE flag, DERIVED from the team's own TEAM-SIGN-OFF lines.

WHAT THIS GUARDS, AND WHY IT IS A SEPARATE FILE FROM THE STAGE LADDER
---------------------------------------------------------------------
Governance answers "can we PROVE the team agreed to this class's
disposition?". It is a FLAG beside the build stage and never a rung in it
(`test_coverage_stage_ladder.py` asserts that separation structurally). This
file guards the flag's INPUT.

The input used to be four transcriptions hand-carried in `coverage.py`:

    DENOMINATOR: transcriptions hand-carried in coverage.py: 4
      binaryseries_parameters, epochfiles_ingested, filter, stimulus_presentation

while the team had signed nineteen decision families in ~19 plan documents the
tool never opened. So 94 of 102 rows reported "no checked transcription", which
was HONEST -- an absence of transcription is not evidence of no decision -- and
useless. `status_board.py` already parsed the signatures; `coverage.py`
hand-copied four of them. One fact, two records, and only one of them read.

Now the flag is DERIVED: ledger row -> the decision family naming that row's
class -> that family's signature. Re-derived every build. The properties below
are the ones that make that derivation safe rather than merely bigger, and each
exists because breaking it would produce a REASSURING number:

  1. IT JOINS ON THE SIGNATURE, NOT ON MEMBERSHIP. `FAMILIES` names classes
     whether or not anyone signed anything. Joining on membership would let one
     unsigned family promote every class it names -- operating rule 4 broken by
     a lookup instead of by a sentence.
  2. IT JOINS ON THE ROW'S OWN IDENTITY, NOT ON WHAT ITS MIGRATOR EMITS.
     Matching emitted `targets` too would move 62 rows rather than 34, and 36
     of those arrive through one class: `session_relative_reference`, the time
     anchor nearly every migrator writes alongside its real output.
  3. IT MATCHES EXACTLY, IN TWO NAMESPACES, AND NORMALISES NOTHING. A ledger row
     is keyed by its v1 (NDI, camelCase) name; a family member may be a v1 name
     or a V_eta snake_case class. Substring or case-folded matching would
     promote `openminds_subject` on a signature about `openminds`, and CLAUDE.md
     records five classes a previous generator got wrong on exactly this axis.
  4. THE GAPS ARE A FIRST-CLASS OUTPUT. Orphan tags, unsigned families and every
     unmoved row bucketed by CAUSE. This drifted precisely because "nothing to
     see" and "nobody looked" printed the same way.

HOW THESE TESTS AVOID BEING WRITTEN FROM THE SAME PREMISE AS THE CODE
---------------------------------------------------------------------
Every signature this file verifies is re-read from the plan document with a
parser written HERE (`_scan`), never by calling `status_board.find_signoff` or
`coverage.check_decision_citations`. The tag rule -- a tagged line signs only
its own family, an untagged line signs a document cited by exactly one family --
is re-implemented here too. If the tool's parser and this one ever disagree,
one of them is wrong and the test says so rather than agreeing with itself.
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
import status_board  # noqa: E402

SCHEMAS = os.path.join(REPO_ROOT, "schemas")
LEDGER_JSON = os.path.join(SCHEMAS, "V_eta_coverage_ledger.json")
LEDGER_MD = os.path.join(SCHEMAS, "V_eta_coverage_ledger.md")

V1_UNIVERSE = 102


def _ledger():
    with open(LEDGER_JSON) as fh:
        return json.load(fh)


def _rows():
    return _ledger()["rows"]


def _gov(rows=None):
    return (_ledger()["summary"]["stage_rollup"]["governance"] if rows is None
            else coverage._governance_rollup(rows))


# ---------------------------------------------------------------------------
# THE SECOND OPINION. A sign-off parser written in this file, from the rule as
# stated in status_board's docstring -- not from its implementation.
# ---------------------------------------------------------------------------

def _scan(path):
    """(line, tag, content) for every line-initial TEAM-SIGN-OFF in a file."""
    with open(path) as fh:
        text = re.sub(r"<!--.*?-->", "", fh.read(), flags=re.DOTALL)
    out = []
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.lstrip()
        if not line.startswith("TEAM-SIGN-OFF"):
            continue
        rest = line[len("TEAM-SIGN-OFF"):].strip()
        tag = None
        m = re.match(r"\[([^\]]+)\]\s*(.*)$", rest)
        if m:
            tag, rest = m.group(1).strip(), m.group(2).strip()
        out.append((n, tag, rest.lstrip(":").strip()))
    return out


# THE TEMPLATE SLOTS, re-stated here rather than imported from status_board.
# This file's whole point is to be a SECOND OPINION -- importing the tool's
# constant would make both sides agree by construction, which is the "a test
# written from the same premise as the code cannot catch the code" failure.
# Read off the template as this repository renders it into V_eta_STATUS.md:
#
#     TEAM-SIGN-OFF [<family>]: <who/when> -- <what was decided>
#
# NARROWED 2026-08-13 in step with the tool. Both sides used to reject ANY
# paired `<...>`, which discarded a real dated decision whose text names a
# class-name pattern (`<modality>_observation`). Angle brackets in prose are
# not a placeholder; an unfilled SLOT is.
TEMPLATE_SLOTS = ("<family>", "<who/when>", "<what was decided>")


def _is_placeholder(content):
    """A sign-off line that is really an unfilled template row."""
    return any(slot in content for slot in TEMPLATE_SLOTS)


def _plan_documents():
    """Every schemas/*.md that is NOT a generated artifact."""
    return sorted(n for n in os.listdir(SCHEMAS)
                  if n.endswith(".md") and n not in status_board.GENERATED_MARKDOWN)


def _independent_signed_families():
    """Which families a reader would call signed, from the documents alone."""
    signed = {}
    for name, members, plan, _what, status in status_board.FAMILIES:
        if status != "team" or not plan:
            continue
        path = os.path.join(SCHEMAS, plan)
        if not os.path.exists(path):
            continue
        shared = sum(1 for f in status_board.FAMILIES if f[2] == plan) > 1
        for line, tag, content in _scan(path):
            if _is_placeholder(content) or len(content) < 10:
                continue          # a template slot is not a decision
            if tag is not None and tag != name:
                continue
            if tag is None and shared:
                continue          # an untagged line in a shared document
            signed[name] = {"plan": plan, "line": line, "members": list(members)}
            break
    return signed


# ===========================================================================
# THE INVARIANTS.
# ===========================================================================

def check_every_signed_row_cites_a_real_signoff(rows):
    """Open the cited document at the cited line and read it."""
    for r in rows:
        g = r.get("governance") or {}
        if g.get("state") != coverage.G_SIGNED:
            continue
        cite = g.get("signoff")
        assert cite, f"{r['v1_class']}: `signed` with no citation at all"
        doc = cite.get("document")
        path = os.path.join(SCHEMAS, doc)
        assert os.path.exists(path), f"{r['v1_class']}: cites a missing {doc}"
        lines = _scan(path)
        if cite.get("family"):
            # DERIVED from a family signature: the cited line must be a real
            # sign-off, its tag must reach that family, and the family must
            # NAME this row's class exactly.
            hit = [(n, t, c) for n, t, c in lines if n == cite["line"]]
            assert hit, (
                f"{r['v1_class']}: cites {doc}:{cite['line']} as a sign-off "
                "line; no TEAM-SIGN-OFF line is there")
            _n, tag, content = hit[0]
            fam = cite["family"]
            shared = sum(1 for f in status_board.FAMILIES
                         if f[2] == doc) > 1
            assert tag == fam or (tag is None and not shared), (
                f"{r['v1_class']}: {doc}:{cite['line']} is tagged {tag!r}, "
                f"which does not sign the family {fam!r} the row claims")
            assert not _is_placeholder(content) and len(content) >= 10, (
                f"{r['v1_class']}: {doc}:{cite['line']} is a template slot, "
                "not a decision")
            members = [f[1] for f in status_board.FAMILIES if f[0] == fam]
            assert members, f"{r['v1_class']}: family {fam!r} does not exist"
            assert cite["matched_name"] in members[0], (
                f"{r['v1_class']}: family {fam!r} does not name "
                f"{cite['matched_name']!r}")
            assert cite["matched_name"] in (r["v1_class"], r.get("veta_class")), (
                f"{r['v1_class']}: matched on {cite['matched_name']!r}, which "
                "is neither its v1 name nor its V_eta class -- the join must "
                "be on the row's OWN identity")
        else:
            frag = cite.get("signoff_fragment")
            assert any(frag in c for _n, _t, c in lines), (
                f"{r['v1_class']}: no TEAM-SIGN-OFF line in {doc} contains "
                f"{frag!r}")


def check_only_signed_families_reach_a_row(rows):
    """MEMBERSHIP IS NOT A SIGNATURE. An unsigned family must reach nothing."""
    signed = _independent_signed_families()
    for r in rows:
        fam = r.get("decided_by_family")
        if not fam:
            continue
        assert fam["family"] in signed, (
            f"{r['v1_class']}: joined to family {fam['family']!r}, which this "
            "test's own reading of the plan documents finds UNSIGNED. A family "
            "exists in the table whether or not anyone signed it; only the "
            "signature admits it")
        assert fam["document"] == signed[fam["family"]]["plan"]
        assert fam["line"] == signed[fam["family"]]["line"]
    # And the other direction: a family with no signature must claim no row.
    unsigned = [f[0] for f in status_board.FAMILIES if f[0] not in signed]
    claimed = {r["decided_by_family"]["family"] for r in rows
               if r.get("decided_by_family")}
    assert not (set(unsigned) & claimed), (
        f"unsigned families reached rows: {sorted(set(unsigned) & claimed)}")


def check_the_join_is_exact_and_two_namespaced(rows):
    """No substring, no normalisation, both namespaces offered."""
    signed = _independent_signed_families()
    members = {m for v in signed.values() for m in v["members"]}
    for r in rows:
        names = [n for n in (r["v1_class"], r.get("veta_class")) if n]
        want = any(n in members for n in names)
        got = bool(r.get("decided_by_family"))
        assert want == got, (
            f"{r['v1_class']}: a signed family names one of {names} = {want}, "
            f"but the row's join says {got}. An extra match is a substring or "
            "case-folded join; a missing one is a namespace the join forgot")


def check_no_row_is_joined_by_spelling_alone(rows):
    """V_eta is snake_case, NDI is camelCase, and normalising joins them wrongly."""
    for r in rows:
        fam = r.get("decided_by_family")
        if not fam:
            continue
        assert fam["matched_name"] in (r["v1_class"], r.get("veta_class")), (
            f"{r['v1_class']}: matched on {fam['matched_name']!r} -- not one of "
            "this row's own names")


def check_governance_accounts_for_every_row(rows, gov):
    """RULE 5: every row carries exactly one state, and the states sum."""
    assert gov["denominator"] == len(rows)
    assert sum(gov["by_state"].values()) == len(rows), (
        "the governance histogram does not sum to the row count -- a row "
        "carries a state nobody counted")
    for k in coverage.GOVERNANCE_STATES:
        assert k in gov["by_state"], f"bucket {k} missing: an absent bucket " \
            "makes 'none of these' and 'not counted' the same output"
    for r in rows:
        g = r.get("governance") or {}
        assert g.get("state") in coverage.GOVERNANCE_STATES, (
            f"{r['v1_class']}: governance state {g.get('state')!r}")
        assert g.get("why"), f"{r['v1_class']}: a state with no reason"


def check_every_unmoved_row_has_a_named_cause(rows, gov):
    """"decided but unrecorded" and "nobody looked" must not print the same."""
    j = gov["join"]
    unmoved = [r for r in rows if not r.get("decided_by_family")]
    assert sum(j["unmoved_by_cause"].values()) == len(unmoved), (
        f'{sum(j["unmoved_by_cause"].values())} bucketed != {len(unmoved)} '
        "rows with no signed family -- a row fell out of the census")
    for r in unmoved:
        assert r.get("governance_gap"), (
            f"{r['v1_class']}: unmoved with no cause recorded")
    named = {n for v in j["unmoved_rows_by_cause"].values() for n in v}
    assert named == {r["v1_class"] for r in unmoved}, (
        "the per-cause row lists do not name exactly the unmoved rows")


def check_orphan_tags_and_unsigned_families_are_reported(gov):
    """Both directions of the mismatch, by name, and never paired up."""
    census = gov["census"]
    fam_names = {f[0] for f in status_board.FAMILIES}
    # Re-scan the documents with this file's own parser.
    mine = {}
    for name in _plan_documents():
        for line, tag, content in _scan(os.path.join(SCHEMAS, name)):
            if tag is None or _is_placeholder(content) or len(content) < 10:
                continue
            mine.setdefault(tag, []).append((name, line))
    orphans = {t: v for t, v in mine.items() if t not in fam_names}
    assert set(census["orphan_tags"]) == set(orphans), (
        f'the census reports orphan tags {sorted(census["orphan_tags"])}; this '
        f"test's own scan finds {sorted(orphans)} -- a signature that reaches "
        "no family must never be dropped silently")
    for tag, where in orphans.items():
        assert census["orphan_tags"][tag][0]["document"] == where[0][0]
        assert census["orphan_tags"][tag][0]["line"] == where[0][1]
    signed = _independent_signed_families()
    assert set(census["families_unsigned"]) == {
        f[0] for f in status_board.FAMILIES if f[0] not in signed}, (
        "the unsigned-family list disagrees with this test's own reading")
    # NEITHER IS RESOLVED. No orphan tag may appear as a family the join used.
    assert not (set(census["orphan_tags"]) & set(census["families_signed"])), (
        "an orphan tag has been mapped onto a family -- that is recording a "
        "disposition, which operating rule 4 puts with the team")


def check_the_census_reports_its_denominator(gov):
    census = gov["census"]
    docs = _plan_documents()
    assert census["documents_read"] == len(docs), (
        f'census read {census["documents_read"]} document(s); {len(docs)} '
        "non-generated .md files exist under schemas/")
    mine = sum(len(_scan(os.path.join(SCHEMAS, d))) for d in docs)
    assert census["accepted_lines"] + len(census["rejected_lines"]) == mine, (
        "accepted + rejected must equal every line-initial marker found; a "
        "line counted by neither is a signature nobody can see")
    for r in census["rejected_lines"]:
        assert r["why"], "a rejected line with no reason is indistinguishable "\
            "from one that was never read"
    assert census["documents_excluded_as_generated"] == list(
        status_board.GENERATED_MARKDOWN)


ALL_CHECKS_ON_ROWS = (
    check_every_signed_row_cites_a_real_signoff,
    check_only_signed_families_reach_a_row,
    check_the_join_is_exact_and_two_namespaced,
    check_no_row_is_joined_by_spelling_alone,
)


class TestTheCommittedLedger(unittest.TestCase):

    def setUp(self):
        self.rows = _rows()
        self.gov = _gov()
        self.assertEqual(len(self.rows), V1_UNIVERSE)

    def test_every_signed_row_cites_a_real_team_signoff(self):
        check_every_signed_row_cites_a_real_signoff(self.rows)

    def test_only_signed_families_reach_a_row(self):
        check_only_signed_families_reach_a_row(self.rows)

    def test_the_join_is_exact_in_both_namespaces(self):
        check_the_join_is_exact_and_two_namespaced(self.rows)

    def test_no_row_is_joined_by_spelling_alone(self):
        check_no_row_is_joined_by_spelling_alone(self.rows)

    def test_governance_accounts_for_every_row(self):
        check_governance_accounts_for_every_row(self.rows, self.gov)

    def test_every_unmoved_row_has_a_named_cause(self):
        check_every_unmoved_row_has_a_named_cause(self.rows, self.gov)

    def test_the_gaps_are_reported_by_name(self):
        check_orphan_tags_and_unsigned_families_are_reported(self.gov)

    def test_the_census_reports_its_denominator(self):
        check_the_census_reports_its_denominator(self.gov)

    def test_the_join_moved_more_than_the_transcriptions_did(self):
        # The whole point, stated as a number so a silent regression to the
        # four hand-carried transcriptions is a failure and not a shrug.
        transcribed = sum(1 for r in self.rows
                          if r.get("decided_signoff") or r.get("no_target_signoff"))
        derived = sum(1 for r in self.rows if r.get("decided_by_family")
                      and not (r.get("decided_signoff")
                               or r.get("no_target_signoff")))
        # WAS 26 DERIVED / 33 SIGNED UNTIL 2026-08-13 AND IS NOW 28 / 35.
        # The two new rows are `subject` and `session`, and NEITHER is a new
        # decision: both were signed that day and both were already visible to
        # `signature_census` -- as ORPHAN TAGS, "a signature that exists and
        # reaches nothing" -- while their ledger rows read `no signature
        # found`. One fact, printed as two absences, because no FAMILIES row
        # joined them. Adding the rows is the join, not the decision; this
        # count moves BECAUSE the derivation reached further, which is exactly
        # what it is here to measure.
        # 28 -> 29 on 2026-08-13: `valid_interval` joined when its FAMILY was
        # renamed to `logical_observation` to match the tag its signature has
        # carried since the classes were renamed validity -> logical. The
        # signature is not new and the decision is not new; the NAME the family
        # was looked up by is. That rename also forced the row's `status` from
        # `open` to `team`, because `open` had been carrying two meanings at
        # once -- "no decision" and "decided, narrower items outstanding" --
        # and the contradiction was invisible only while the tag mismatch kept
        # the signature unreachable.
        self.assertEqual(transcribed, 8)
        self.assertEqual(derived, 29)
        self.assertEqual(self.gov["by_state"][coverage.G_SIGNED], 36,
                         "8 transcribed + 29 derived, less `ngrid`, whose "
                         "DISPUTED record outranks its family signature")

    def test_a_DISPUTED_record_outranks_a_family_signature(self):
        # `ngrid` IS named by the signed family `image / ngrid` AND carries a
        # transcription saying its plan document states two incompatible
        # dispositions. The contradiction is the finding; a lookup must not
        # erase it.
        ngrid = next(r for r in self.rows if r["v1_class"] == "ngrid")
        self.assertTrue(ngrid["decided_by_family"],
                        "precondition: a signed family names ngrid")
        self.assertEqual(ngrid["governance"]["state"], coverage.G_DISPUTED)

    def test_the_emitted_target_rows_are_counted_not_joined(self):
        # The 36-row reach a looser join would buy, reported rather than taken.
        j = self.gov["join"]
        self.assertGreater(
            j["unmoved_by_cause"][coverage.GAP_TARGET_ONLY], 0,
            "precondition: some rows emit a class a signed family names")
        via = j["target_only_reached_via"]
        self.assertTrue(via, "the reach must be itemised, not just counted")
        top = max(via.items(), key=lambda kv: kv[1])
        self.assertIn("session_relative_reference", top[0])
        for name in j["unmoved_rows_by_cause"][coverage.GAP_TARGET_ONLY]:
            row = next(r for r in self.rows if r["v1_class"] == name)
            self.assertIsNone(row["decided_by_family"],
                              f"{name} was joined through an emitted target")

    def test_the_markdown_carries_the_gap_report(self):
        with open(LEDGER_MD) as fh:
            md = fh.read()
        census = self.gov["census"]
        self.assertIn("Governance -- can we PROVE the team agreed?", md)
        for tag in census["orphan_tags"]:
            self.assertIn("`" + tag + "`", md)
        for fam in census["families_unsigned"]:
            self.assertIn("`" + fam + "`", md)
        self.assertIn("QUESTION FOR THE TEAM", md)
        for cause in self.gov["join"]["unmoved_by_cause"]:
            self.assertIn(cause, md)

    def test_no_tagged_signoff_is_rejected_by_the_placeholder_guard(self):
        # INVERTED 2026-08-13, NOT PATCHED. This test used to ASSERT THE
        # DEFECT: that `V_eta_recording_observation_plan.md:99` -- a real,
        # dated, tagged team sign-off -- was REJECTED, because the guard threw
        # away any line containing a paired `<...>` and that decision's text
        # says `<modality>_observation`. The test was correct about the facts
        # and it pinned the wrong behaviour in place, which is the same call
        # the three `epochid` tests needed: a test written from the same
        # premise as the code cannot catch the code.
        #
        # The guard now rejects only the three slot names the TEMPLATE uses,
        # so prose naming a class-name pattern survives. The blast radius was
        # measured before the change: of all 55 schemas/*.md, exactly two
        # SCANNED lines carry a paired `<...>` -- the rendered template in
        # V_eta_STATUS.md (still rejected, and generated markdown the census
        # excludes anyway) and this signature (now accepted).
        #
        # WHY IT MATTERED rather than being a tidy-up: that signature is what
        # settles `element`'s disposition. While it was discarded, `element`
        # read `no signature found` in the coverage ledger and reached the team
        # on the confirm sheet as an open question it had already answered.
        rejected = self.gov["census"]["rejected_lines"]
        tagged = [r for r in rejected if r["tag"]]
        self.assertEqual(tagged, [], "a tagged team sign-off is being "
                         "discarded by the placeholder guard: "
                         + str([(r["document"], r["line"], r["why"])
                                for r in tagged]))

        # ...and the signature really is visible now, rather than merely not
        # rejected. An empty `rejected_lines` would also be produced by a
        # scanner that read no documents at all.
        tags = self.gov["census"]["tags"]
        self.assertIn("raw recording observation", tags)
        where = tags["raw recording observation"][0]
        self.assertEqual(where["document"],
                         "V_eta_recording_observation_plan.md")

        # THE REPORTING INVARIANT SURVIVES THE INVERSION, AND IS ASSERTED IN
        # BOTH DIRECTIONS SO IT CANNOT GO VACUOUS. The renderer prints its
        # rejected-line warning only when there IS one, so a bare `assertIn`
        # here would fail today for the right reason and a bare `assertNotIn`
        # would stop covering the case that matters. Asserting the ledger
        # AGREES WITH THE CENSUS covers both: a rejection nobody prints is a
        # signature nobody can find, and a warning printed over an empty list
        # is a defect reported that does not exist.
        marker = "rejected line(s) carry a family tag"
        with open(LEDGER_MD) as fh:
            md = fh.read()
        if tagged:
            self.assertIn(marker, md, "a tagged line is rejected and the "
                          "ledger does not say so")
        else:
            self.assertNotIn(marker, md, "the ledger warns about rejected "
                             "tagged lines while the census reports none")

    def test_the_generated_markdown_list_matches_what_gates_declares(self):
        # DERIVED CROSS-CHECK. The census excludes generated artifacts; the
        # list of them is a literal, and a new generated document could
        # quietly become an input to the census. gates.py declares what each
        # step WRITES, so that declaration is the second record.
        with open(os.path.join(REPO_ROOT, "tools", "gates.py")) as fh:
            written = set(re.findall(r'"(schemas/[A-Za-z0-9_./]+\.md)"', fh.read()))
        self.assertEqual(
            {os.path.basename(p) for p in written},
            set(status_board.GENERATED_MARKDOWN),
            "status_board.GENERATED_MARKDOWN and the .md files gates.py "
            "declares its steps write have diverged")


class TestTheReconciliation(unittest.TestCase):
    """The hand-carried table and the derivation, checked against each other.

    `DECIDED_TARGETS_BY_SIGNOFF` SURVIVES the derivation because it carries
    something the join cannot produce: the TARGET CLASSES a signature names. It
    must not survive as a second, unchecked opinion about WHERE a decision
    lives -- so a transcription citing one document while the signed family
    naming the same class cites another is fatal.
    """

    def test_the_reconciliation_is_non_vacuous(self):
        lines, fails = coverage.check_decision_citations()
        self.assertEqual(fails, [])
        den = [ln for ln in lines if "reconciled against the DERIVED" in ln]
        self.assertEqual(len(den), 1, "the reconciliation must print a "
                                      "denominator, unconditionally")
        self.assertIn("8 transcription(s)", den[0])
        self.assertIn("8 also named by a signed family", den[0],
                      "a reconciliation that matches nothing proves nothing")

    def test_the_table_still_carries_what_the_join_cannot(self):
        # If every entry lost its target list there would be nothing left to
        # keep. Each must name at least one target class the derivation cannot
        # produce.
        self.assertTrue(coverage.DECIDED_TARGETS_BY_SIGNOFF)
        for cls, entry in coverage.DECIDED_TARGETS_BY_SIGNOFF.items():
            self.assertTrue(entry[0], f"{cls}: no target list, so nothing the "
                                      "derivation could not do")


# ===========================================================================
# MUTATION TESTS. Damage the join; prove an invariant turns red.
# ===========================================================================


class _Swap:
    """Swap attributes on a module for the duration of a block."""

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
    all_idx, signed_idx = coverage.family_index(), coverage.signed_family_index()
    out = []
    for r in copy.deepcopy(rows):
        r["decided_by_family"] = coverage.match_signed_family(
            r["v1_class"], r["veta_class"], signed_idx)
        r["families_naming_this_class"] = sorted(
            {f for n in (r["v1_class"], r["veta_class"]) if n
             for f in all_idx.get(n, [])})
        r["governance_gap"] = coverage.governance_gap(r, all_idx, signed_idx)
        r["governance"] = coverage.governance_state(r)
        out.append(r)
    return out


class TestMutationsRedden(unittest.TestCase):

    def _assert_reddens(self, swap, checks=ALL_CHECKS_ON_ROWS, rows=None):
        rows = rows if rows is not None else _rows()
        with swap:
            mutated = _rejoin(rows)
            gov = coverage._governance_rollup(mutated)
            caught = []
            for check in checks:
                try:
                    check(mutated)
                except AssertionError as exc:
                    caught.append((check.__name__, str(exc).splitlines()[0]))
            for check in (check_governance_accounts_for_every_row,
                          check_every_unmoved_row_has_a_named_cause):
                try:
                    check(mutated, gov)
                except AssertionError as exc:
                    caught.append((check.__name__, str(exc).splitlines()[0]))
        self.assertTrue(caught, (
            "MUTATION PRODUCED NO FAILURE. Today's data cannot distinguish it, "
            "so the invariants above do not cover this damage. The fix is a "
            "constructed fixture, not a weaker claim."))
        return [c[0] for c in caught]

    def test_joining_on_MEMBERSHIP_instead_of_the_signature_reddens(self):
        # THE OPERATING-RULE-4 MUTATION. Every family admits its classes,
        # signed or not -- `valid_interval` is unsigned today and would be
        # promoted, and any family added tomorrow would arrive pre-decided.
        def all_families(signed=None):
            idx = {}
            for name, members, plan, _w, _s in status_board.FAMILIES:
                for m in members:
                    idx.setdefault(m, []).append(
                        {"family": name, "document": plan or "?", "line": 1,
                         "signoff": "membership"})
            return idx

        caught = self._assert_reddens(
            _Swap(coverage, signed_family_index=all_families))
        self.assertIn("check_only_signed_families_reach_a_row", caught)

    def test_a_signature_parser_that_accepts_everything_reddens(self):
        # `find_signoff_line` returning a line for every family -- the parser
        # dead in the most flattering direction. Every family becomes signed
        # and 60+ rows become "decided" on the strength of nothing.
        def always(plan, family):
            return {"line": 1, "tag": family, "content": "x" * 40,
                    "accepted": True, "rejected_because": None,
                    "document": plan or "V_eta_OPEN_WORK.md"}

        caught = self._assert_reddens(
            _Swap(status_board, find_signoff_line=always))
        self.assertIn("check_only_signed_families_reach_a_row", caught)

    def test_matching_on_a_SUBSTRING_instead_of_the_whole_name_reddens(self):
        # `openminds_subject` promoted by a signature about `openminds`;
        # `daqreader_ndr` by one about `daqreader`. Five rows today.
        def loose(v1_class, veta_class, index):
            exact = _real_match(v1_class, veta_class, index)
            if exact:
                return exact
            for member, entries in index.items():
                for name, how in ((v1_class, "v1_class"),
                                  (veta_class, "veta_class")):
                    if name and member in name:
                        return dict(entries[0], matched_on=how,
                                    matched_name=member, conflict=[])
            return None

        _real_match = coverage.match_signed_family
        caught = self._assert_reddens(
            _Swap(coverage, match_signed_family=loose))
        self.assertIn("check_the_join_is_exact_and_two_namespaced", caught)
        self.assertIn("check_no_row_is_joined_by_spelling_alone", caught)

    def test_normalising_the_spelling_before_matching_reddens(self):
        """CONSTRUCTED FIXTURE, because today's data cannot show this.

        No member of any family differs from a ledger name by case or
        underscores alone, so a normalising join changes NOTHING on the live
        102 -- and "the mutation produced no failure" would be a fact about
        the data, not a licence to drop the claim. So the fixture is the
        historical bug itself: CLAUDE.md records `demo_ndi` dispositioned
        DELETE on a grep that could not match, because NDI spells the class
        `demoNDI`. A family member spelled `demo_ndi` must reach NOTHING.
        """
        fixture = [(n, list(m), p, w, s)
                   for n, m, p, w, s in status_board.FAMILIES]
        for i, (n, m, p, w, s) in enumerate(fixture):
            if n == "misc singletons":          # a SIGNED family
                fixture[i] = (n, m + ["demo_ndi"], p, w, s)
                break
        else:                                    # pragma: no cover
            self.fail("the fixture needs a signed family to hang a member on")

        with _Swap(status_board, FAMILIES=fixture):
            honest = _rejoin(_rows())
            demo = next(r for r in honest if r["v1_class"] == "demoNDI")
            self.assertIsNone(
                demo["decided_by_family"],
                "`demo_ndi` is not `demoNDI`: an exact join must not reach it")
            # The near-miss REPORT must see what the join refused to do.
            near = coverage.signature_join_census(
                honest, coverage.family_index(fixture),
                coverage.signed_family_index())["spelling_near_misses"]
            self.assertTrue(
                any(m["family_member"] == "demo_ndi"
                    and m["ledger_name"] == "demoNDI" for m in near),
                "a member matching a ledger name only after normalisation must "
                f"be REPORTED as a near miss; got {near}")

            def normalised(v1_class, veta_class, index):
                exact = _real(v1_class, veta_class, index)
                if exact:
                    return exact
                for member, entries in index.items():
                    for name, how in ((v1_class, "v1_class"),
                                      (veta_class, "veta_class")):
                        if name and coverage._normalised(member) \
                                == coverage._normalised(name):
                            return dict(entries[0], matched_on=how,
                                        matched_name=member, conflict=[])
                return None

            _real = coverage.match_signed_family
            caught = self._assert_reddens(
                _Swap(coverage, match_signed_family=normalised))
        self.assertIn("check_no_row_is_joined_by_spelling_alone", caught)

    def test_dropping_an_orphan_tag_silently_reddens(self):
        # A signature whose tag reaches no family, filtered out of the census.
        # It is the exact shape of "found nothing" that is really "looked in
        # the wrong place".
        real = status_board.signature_census

        def silent(*a, **kw):
            c = real(*a, **kw)
            c["orphan_tags"] = {}
            return c

        with _Swap(status_board, signature_census=silent):
            gov = coverage._governance_rollup(_rejoin(_rows()))
            with self.assertRaises(AssertionError):
                check_orphan_tags_and_unsigned_families_are_reported(gov)

    def test_dropping_an_unsigned_family_from_the_report_reddens(self):
        # THIS TEST WENT VACUOUS ON 2026-08-13 AND THE SUITE STAYED GREEN FOR
        # ONE RUN. It used to clear `families_unsigned` on the LIVE census and
        # assert that the checker noticed. That worked only while some family
        # really was unsigned; renaming `valid_interval` -> `logical_observation`
        # joined the last one, the list became empty, and clearing an empty list
        # mutates nothing -- so `assertRaises` failed and said, correctly, that
        # no error was raised. A mutation test whose mutation is a no-op reports
        # exactly like a passing one; this is the `silentLoss` defect wearing a
        # different hat, and the honest repair is to stop depending on the tree
        # having a defect in it.
        #
        # So the fixture SUPPLIES the unsigned family. A synthetic row with
        # status `team` and a plan document carrying no line its tag reaches is
        # unsigned by construction, and both the census and this file's
        # independent re-scan agree on that -- which is what makes dropping it
        # detectable.
        unsigned = ("a_family_nothing_signs", ["nothing_at_all"],
                    "V_eta_tenets.md",
                    "a synthetic row: no TEAM-SIGN-OFF tag names it", "team")
        families = list(status_board.FAMILIES) + [unsigned]

        with _Swap(status_board, FAMILIES=families):
            # PRECONDITION, ASSERTED RATHER THAN ASSUMED. If the synthetic row
            # were somehow signed, the mutation below would be a no-op again and
            # this test would go quietly vacuous a second time.
            census = status_board.signature_census()
            self.assertIn(unsigned[0], census["families_unsigned"],
                          "the synthetic family is not reported unsigned, so "
                          "the mutation would have nothing to remove")

            real = status_board.signature_census

            def silent(*a, **kw):
                c = real(*a, **kw)
                c["families_unsigned"] = [f for f in c["families_unsigned"]
                                          if f != unsigned[0]]
                return c

            with _Swap(status_board, signature_census=silent):
                gov = coverage._governance_rollup(_rejoin(_rows()))
                with self.assertRaises(AssertionError):
                    check_orphan_tags_and_unsigned_families_are_reported(gov)

    def test_a_hand_edit_contradicting_the_derivation_is_FATAL(self):
        # `epochfiles_ingested` is transcribed as decided in
        # V_eta_epoch_plan.md AND named by the signed family `epoch`, which
        # cites the same document. Move the class to a DIFFERENT signed family
        # and the two records now point at two documents -- which is exactly
        # the state nobody would notice, and it must stop the build.
        #
        # NOTE the direction: the fragment check alone does NOT catch this
        # (the cited document still contains the quoted line). Only the
        # reconciliation does, which is what makes it worth having.
        _lines, fails = coverage.check_decision_citations()
        self.assertEqual(fails, [], "precondition: the tables reconcile today")

        mutated = []
        for name, members, plan, what, status in status_board.FAMILIES:
            members = [m for m in members if m != "epochfiles_ingested"]
            if name == "misc singletons":
                members = members + ["epochfiles_ingested"]
            mutated.append((name, members, plan, what, status))

        with _Swap(status_board, FAMILIES=mutated):
            _lines, fails = coverage.check_decision_citations()
        self.assertTrue(fails, "a transcription and the derived signature now "
                               "cite different documents and nothing failed")
        self.assertTrue(any("epochfiles_ingested" in f for f in fails), fails)
        self.assertTrue(any("misc singletons" in f for f in fails), fails)

    def test_hand_editing_the_TABLE_side_is_an_error_too(self):
        # The mutation above edits the FAMILIES side; this one edits the
        # hand-carried table, which is the side a person is most likely to
        # touch. Either direction must stop the build rather than silently
        # override the other record.
        #
        # WHICH CHECK CATCHES IT IS REPORTED, not assumed: re-pointing a
        # transcription at a document that does not contain its quoted
        # fragment is caught by the older citation check, and re-pointing it
        # at one that DOES would be caught by the reconciliation. Both are
        # fatal, which is the property under test.
        table = dict(coverage.DECIDED_TARGETS_BY_SIGNOFF)
        targets, _plan, frag, mapping, note = table["epochfiles_ingested"]
        table["epochfiles_ingested"] = (targets, "V_eta_stimulus_model_plan.md",
                                        frag, mapping, note)
        with _Swap(coverage, DECIDED_TARGETS_BY_SIGNOFF=table):
            _lines, fails = coverage.check_decision_citations()
        self.assertTrue(fails, "a transcription now cites a document that "
                               "neither carries its sign-off line nor is the "
                               "one the signed family cites, and nothing failed")
        self.assertTrue(any("epochfiles_ingested" in f for f in fails), fails)

    def test_the_reconciliation_denominator_cannot_be_faked_by_deleting_members(self):
        # A class no family names is COUNTED, not failed -- families track open
        # classes and a class can be signed and closed. So the check must not
        # be satisfiable by emptying FAMILIES: the denominator line has to show
        # the reconciled count collapsing.
        emptied = [(n, [], p, w, s) for n, _m, p, w, s in status_board.FAMILIES]
        with _Swap(status_board, FAMILIES=emptied):
            lines, fails = coverage.check_decision_citations()
        self.assertEqual(fails, [])
        den = next(ln for ln in lines if "reconciled against the DERIVED" in ln)
        self.assertIn("0 also named by a signed family", den)
        self.assertIn("8 named by no family at all", den)


if __name__ == "__main__":
    unittest.main()
