"""The signature scanner's two non-signature cases (#73 review, 2026-09-29).

A line carrying the TEAM-SIGN-OFF marker is not a live signature when it is
(1) inside a fenced code block -- a quotation -- or (2) retired by a preceding
`SIGN-OFF SUPERSEDED [tag]` line. Both come back REJECTED with a reason, never
dropped, so the census still shows them.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import status_board as sb

REPO = os.path.join(os.path.dirname(__file__), "..")


def _scan(text):
    return [(r["tag"], r["accepted"], r["rejected_because"]) for r in sb.scan_signoff_lines(text)]


def test_a_signature_quoted_in_a_code_fence_is_not_a_signature():
    text = ("TEAM-SIGN-OFF [a]: jess, 2026-01-01 -- decided a\n\n"
            "```\nTEAM-SIGN-OFF [b]: jess, 2026-01-01 -- quoted, not signed here\n```\n")
    rows = _scan(text)
    assert rows[0] == ("a", True, None)
    assert rows[1][0] == "b" and rows[1][1] is False and "fenced" in rows[1][2]


def test_a_superseded_signature_is_rejected_and_only_the_next_one():
    text = ("SIGN-OFF SUPERSEDED [x]: jess, 2026-09-29 -- replaced by item 18\n\n"
            "TEAM-SIGN-OFF [x]: steve, 2026-09-22 -- the old decision\n\n"
            "TEAM-SIGN-OFF [x]: steve, 2026-10-01 -- a later, live decision\n")
    rows = _scan(text)
    assert rows[0][1] is False and rows[0][2].startswith("SUPERSEDED")
    assert rows[1] == ("x", True, None)


def test_the_two_known_cases_in_the_tree():
    with open(os.path.join(REPO, "schemas", "V_eta_method_parameters_plan.md")) as fh:
        mp = sb.scan_signoff_lines(fh.read())
    assert [r["accepted"] for r in mp if r["tag"] == "epoch"] == [False]
    with open(os.path.join(REPO, "schemas", "V_eta_go_forward_class_audit.md")) as fh:
        gf = sb.scan_signoff_lines(fh.read())
    sp = [r for r in gf if r["tag"] == "spatial_transcriptomics_family"]
    assert len(sp) == 1 and sp[0]["accepted"] is False
    assert sp[0]["rejected_because"].startswith("SUPERSEDED")


def test_coverage_citation_reader_applies_the_same_two_rules():
    """coverage._signoff_lines validates decision citations; a quotation or a
    superseded signature must not be able to validate one."""
    import coverage as cv
    gf = [n for n, _ in cv._signoff_lines("V_eta_go_forward_class_audit.md")]
    with open(os.path.join(REPO, "schemas", "V_eta_go_forward_class_audit.md")) as fh:
        sup_line = next(i for i, ln in enumerate(fh.read().splitlines(), 1)
                        if ln.startswith("TEAM-SIGN-OFF [spatial_transcriptomics_family]"))
    assert sup_line not in gf
    mp = [n for n, _ in cv._signoff_lines("V_eta_method_parameters_plan.md")]
    # The real signature at :18 is accepted and the fenced QUOTATION at :694 is not.
    # Asserted as membership, not `== [18]`: a later genuine signature appended to
    # the document (the #73 audit 2 D4 amendment) must not break this test.
    assert 18 in mp and 694 not in mp
