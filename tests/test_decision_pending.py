"""`decision_citations.py --pending`: decision lines whose build is still pending."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import decision_citations as dc


def _write(tmp_path, text):
    (tmp_path / "plan.md").write_text(text, encoding="utf-8")
    return str(tmp_path)


def test_a_pending_line_is_listed_with_its_tag(tmp_path):
    d = _write(tmp_path, "Decided by Jess Haley, 2026-10-22 [x]: do x. Build pending: DID-matlab (x).\n")
    read, pend = dc.pending_builds(d)
    assert read == 1
    assert [p["tag"] for p in pend] == ["x"]


def test_a_built_line_is_not_pending(tmp_path):
    d = _write(tmp_path, "Decided by Jess Haley, 2026-10-22 [x]: do x. Built: DID-matlab abc1234.\n")
    assert dc.pending_builds(d) == (1, [])


def test_the_marker_outside_a_decision_line_is_not_counted(tmp_path):
    d = _write(tmp_path, "Prose that mentions Build pending: something.\n")
    assert dc.pending_builds(d) == (0, [])
