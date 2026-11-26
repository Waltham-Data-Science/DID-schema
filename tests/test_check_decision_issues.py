"""tools/check_decision_issues.py: a decision line with a build left names an open issue."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import check_decision_issues as cdi

LINE = "Decided by Jess Haley, 2026-11-26 [x]: something. "
OPEN = {"state": "open"}
CLOSED = {"state": "closed"}


def _doc(tmp_path, text):
    d = tmp_path / "docs"
    d.mkdir()
    (d / "plan.md").write_text(text, encoding="utf-8")
    (d / "generated").mkdir()
    (d / "generated" / "board.md").write_text(LINE + "Build pending: X.\n", encoding="utf-8")
    return str(d)


def test_tracked_issues_reads_every_ref_and_folds_case():
    keys = cdi.tracked_issues("... Tracked in: VH-Lab/DID-matlab#484, Waltham-Data-Science/did-schema#350.")
    assert keys == ["vh-lab/did-matlab#484", "waltham-data-science/did-schema#350"]


def test_a_pending_line_with_no_issue_fails(tmp_path):
    read, pend = cdi.pending_lines(_doc(tmp_path, LINE + "Build pending: NDI-matlab (it).\n"))
    assert read == 1 and len(pend) == 1
    assert cdi.check(pend, {"issues": {}})[0].startswith("D1 ")


def test_the_spatial_spelling_counts_as_pending(tmp_path):
    _, pend = cdi.pending_lines(_doc(tmp_path, LINE + "Build pending (waits for a dataset): DID-matlab.\n"))
    assert len(pend) == 1


def test_a_line_whose_every_issue_is_closed_fails(tmp_path):
    _, pend = cdi.pending_lines(_doc(tmp_path, LINE + "Build pending: A. Tracked in: o/r#1, o/r#2.\n"))
    fails = cdi.check(pend, {"issues": {"o/r#1": CLOSED, "o/r#2": CLOSED}})
    assert len(fails) == 1 and fails[0].startswith("D2 ")


def test_one_open_issue_is_enough(tmp_path):
    """Control: a line may also name an issue that closed after its part landed."""
    _, pend = cdi.pending_lines(_doc(tmp_path, LINE + "Build pending: A. Tracked in: o/r#1, o/r#2.\n"))
    assert cdi.check(pend, {"issues": {"o/r#1": CLOSED, "o/r#2": OPEN}}) == []


def test_an_issue_missing_from_the_snapshot_is_not_measured(tmp_path):
    _, pend = cdi.pending_lines(_doc(tmp_path, LINE + "Build pending: A. Tracked in: o/r#9.\n"))
    assert cdi.check(pend, {"issues": {}})[0].startswith("D3 ")
    assert cdi.check(pend, None)[0].startswith("D3 ")


def test_a_built_line_is_not_checked(tmp_path):
    """Control: a line with no pending marker is history; its closed issue is fine."""
    read, pend = cdi.pending_lines(_doc(tmp_path, LINE + "Built: DID-matlab abc (#1). Tracked in: o/r#1 (closed).\n"))
    assert read == 1 and pend == []


def test_generated_documents_are_not_read(tmp_path):
    read, _ = cdi.pending_lines(_doc(tmp_path, "no decision here\n"))
    assert read == 0


def test_the_committed_tree_passes_against_the_committed_snapshot():
    read, pend = cdi.pending_lines()
    print(f"\nDENOMINATOR: {read} decision lines read, {len(pend)} with a build left")
    assert read > 0 and pend
    assert cdi.check(pend, cdi.load_snapshot()) == []
