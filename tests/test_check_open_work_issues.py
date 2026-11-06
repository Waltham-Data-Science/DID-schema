"""tools/check_open_work_issues.py: every OPEN row of did_v2_OPEN_WORK.md points
at an open GitHub issue, and the file takes no new rows (Jess Haley,
2026-11-03, did_v2_go_forward_class_audit.md [open work lives in issues])."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import check_open_work_issues as cow

U = "https://github.com/Waltham-Data-Science/DID-schema/issues/"


def doc(open_rows, other=(), completed=()):
    lines = ["# t", "", "## OPEN", "", "| # | item -> issue |", "|---|---|"]
    lines += open_rows
    lines += ["", "### Open in another repository (not tracked here)", "",
              "| row | repository | what is open |", "|---|---|---|"]
    lines += list(other)
    lines += ["", "## COMPLETED (kept)", "", "| # | what completed |", "|---|---|"]
    lines += list(completed)
    lines += ["", "## DECISIONS RECORDED IN THIS FILE (verbatim)", "",
              "| 999 | a table below COMPLETED is not a row |"]
    return "\n".join(lines) + "\n"


def snap(**states):
    return {"issues": {f"Waltham-Data-Science/DID-schema#{n}": {"state": s, "state_reason": None}
                       for n, s in ((int(k[1:]), v) for k, v in states.items())}}


FROZEN = ("30", "31", "9", "113 step 3")


def run(text, snapshot, awaiting=None):
    return cow.check(text, snapshot, frozen_open=FROZEN, frozen_max=165,
                     awaiting={} if awaiting is None else awaiting)


def test_an_open_row_on_an_open_issue_passes():
    fails, waits, rows, cited = run(doc([f"| 30 | x -> {U}104 |"]), snap(i104="open"))
    assert (fails, waits) == ([], [])
    assert [r[0] for r in rows] == ["30"]
    assert cited == {"Waltham-Data-Science/DID-schema#104"}


def test_an_open_row_on_a_closed_issue_fails():
    fails, _w, _r, _c = run(doc([f"| 30 | x -> {U}104 |"]), snap(i104="closed"))
    assert len(fails) == 1 and "W4" in fails[0] and "closed" in fails[0]


def test_an_issue_the_snapshot_does_not_hold_is_not_measured_and_fails():
    fails, _w, _r, _c = run(doc([f"| 30 | x -> {U}104 |"]), snap())
    assert len(fails) == 1 and "W3" in fails[0] and "NOT MEASURED" in fails[0]


def test_no_snapshot_at_all_fails_every_row_rather_than_passing():
    fails, _w, _r, _c = run(doc([f"| 30 | x -> {U}104 |"]), None)
    assert len(fails) == 1 and "W3" in fails[0]


def test_a_row_with_no_issue_fails_including_in_the_other_repository_table():
    fails, _w, rows, _c = run(doc([], other=["| 113 step 3 | DID-matlab | y |"]), snap())
    assert [r[0] for r in rows] == ["113 step 3"]
    assert len(fails) == 1 and "W2" in fails[0]


def test_the_first_issue_url_in_a_row_is_its_issue():
    line = f"| 30 | x -> {U}104 (see also {U}105) |"
    assert cow.row_issue(line) == "Waltham-Data-Science/DID-schema#104"
    fails, _w, _r, _c = run(doc([line]), snap(i104="open", i105="closed"))
    assert fails == []


def test_a_new_open_row_fails_the_freeze():
    fails, _w, _r, _c = run(doc([f"| 166 | new work -> {U}300 |"]), snap(i300="open"))
    assert any(f.startswith("W1 row 166") and "above 165" in f for f in fails)
    assert any(f.startswith("W1 row 166") and "not an OPEN row" in f for f in fails)


def test_a_row_below_the_max_that_was_not_open_at_the_freeze_fails():
    fails, _w, _r, _c = run(doc([f"| 57 | reopened as a row -> {U}95 |"]), snap(i95="open"))
    assert len(fails) == 1 and fails[0].startswith("W1 row 57")


def test_a_new_completed_row_above_the_max_fails_the_freeze():
    fails, _w, _r, _c = run(doc([], completed=["| 170 | done |"]), snap())
    assert len(fails) == 1 and "W1 row 170" in fails[0]


def test_a_row_moved_to_completed_passes():
    fails, _w, rows, _c = run(doc([], completed=["| 31 | done; #94 closed |"]), snap())
    assert (fails, rows) == ([], [])


def test_an_awaiting_row_is_reported_not_failed():
    fails, waits, _r, _c = run(doc([f"| 31 | x -> {U}94 |"]), snap(i94="closed"),
                               awaiting={"31": "reopen #94"})
    assert fails == []
    assert len(waits) == 1 and "row 31" in waits[0] and "reopen #94" in waits[0]


def test_an_awaiting_entry_whose_row_now_passes_fails_so_the_list_only_shrinks():
    fails, waits, _r, _c = run(doc([f"| 31 | x -> {U}94 |"]), snap(i94="open"),
                               awaiting={"31": "reopen #94"})
    assert waits == []
    assert len(fails) == 1 and fails[0].startswith("W5 row 31")


def test_an_awaiting_entry_for_a_row_no_longer_open_fails():
    fails, _w, _r, _c = run(doc([], completed=["| 31 | done |"]), snap(),
                            awaiting={"31": "reopen #94"})
    assert len(fails) == 1 and fails[0].startswith("W5 row 31") and "not an OPEN row" in fails[0]


def test_refresh_reads_only_the_issues_open_rows_cite():
    asked = []

    def fetch(key):
        asked.append(key)
        return {"state": "open"}

    text = doc([f"| 30 | x -> {U}104 |"], completed=[f"| 46 | done; {U}92 closed |"])
    s = cow.refresh(text, fetch=fetch)
    assert asked == ["Waltham-Data-Science/DID-schema#104"]
    assert set(s) == {"why", "fetched_at", "issues"}


def test_the_committed_file_passes_with_the_committed_snapshot():
    """The real file, the real snapshot and the real AWAITING_ISSUE list agree,
    and every row the file was frozen with is accounted for."""
    with open(cow.OPEN_WORK, encoding="utf-8") as f:
        text = f.read()
    fails, waits, rows, _c = cow.check(text, cow.load_snapshot())
    assert rows, "no OPEN row read"
    assert fails == [], fails
    assert len(waits) == len(cow.AWAITING_ISSUE)
    assert {r[0] for r in rows} <= set(cow.FROZEN_OPEN)


def test_every_carry_awaiting_a_home_cites_an_open_row():
    """With check_carry_register C5 this is the composition the decision asks
    for: a home a carry awaits is tracked by an OPEN row, and every OPEN row
    points at an open issue or is listed as awaiting one."""
    import check_carry_register as ccr
    with open(cow.OPEN_WORK, encoding="utf-8") as f:
        text = f.read()
    rows, _ = cow.parse(text)
    labels = {lab for lab, _ln in rows}
    known = ccr.open_rows(text)
    assert {str(n) for n in known} <= labels
