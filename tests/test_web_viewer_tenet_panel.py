"""The tenet panel must not render an unmapped tenet as an empty box.

The map is CURATED (tools/tenet_map.py), so it will always be incomplete in
some direction, and the failure mode is specific: a tenet nobody has mapped and
a tenet that shaped nothing render identically as a heading with nothing under
it. One of those is a fact about the project and the other is a fact about the
table, and a reader cannot tell them apart from an empty box.

The generator already NAMES the unmapped tenets in its denominator. These tests
hold the other half -- that the panel says so on the page, and that a
decided-but-unbuilt class cannot be drawn like a shipped one.
"""
import json
import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB_SRC = os.path.join(REPO_ROOT, "web", "src")
ASSET = os.path.join(REPO_ROOT, "web", "public", "tenets.json")


def read(name):
    with open(os.path.join(WEB_SRC, name)) as fh:
        return fh.read()


def code_only(body):
    body = re.sub(r"/\*.*?\*/", "", body, flags=re.DOTALL)
    return re.sub(r"//.*$", "", body, flags=re.MULTILINE)


def asset():
    with open(ASSET) as fh:
        return json.load(fh)


def test_all_fourteen_tenets_reach_the_panel_whether_or_not_they_have_rows():
    a = asset()
    assert len(a["tenets"]) == 14, (
        f"DENOMINATOR: {len(a['tenets'])} tenets in the asset, expected 14")
    body = code_only(read("Tenets.tsx"))
    # The panel iterates the asset's tenet list, not the rows: iterating rows
    # would drop an unmapped tenet off the page entirely, which is the same
    # defect one step worse.
    assert "doc.tenets.map" in body


def test_a_tenet_with_no_rows_is_captioned_rather_than_left_blank():
    body = read("Tenets.tsx")
    assert "rows.length === 0" in body, (
        "nothing distinguishes a tenet with no rows from one with rows")
    assert "No substantiated mapping" in body, (
        "an unmapped tenet must SAY it is unmapped; an empty box is "
        "indistinguishable from a tenet that shaped nothing")


def test_the_citation_is_shown_not_hidden_in_a_tooltip():
    """The citation is the only reason to believe a curated row. Putting it in
    a `title=` makes it invisible when scanning, on a phone, and in print --
    the same mistake the coverage ledger's `how` field was rescued from."""
    body = code_only(read("Tenets.tsx"))
    assert "citation.quote" in body
    assert "citation.doc" in body
    assert "citation.line" in body


def test_a_plan_only_class_is_drawn_differently_from_a_built_one():
    body = code_only(read("Tenets.tsx"))
    assert "plan_only_classes" in body, (
        "a decided-but-unbuilt or superseded class must be visually distinct; "
        "drawing it like a shipped class is the most misleading thing this "
        "panel could do")
    assert "class_registers" in body, (
        "the register comes from the artifact, which already checked each name "
        "against the v1 universe, the built set and the cited document")


def test_the_panel_reports_the_generators_denominator():
    body = code_only(read("Tenets.tsx"))
    for key in ("tenets_declared", "tenets_with_at_least_one_row",
                "tenets_with_no_substantiated_row", "negative_control"):
        assert key in body, f"the panel hides the generator's `{key}`"


def test_every_row_the_panel_will_draw_carries_a_citation():
    a = asset()
    checked = 0
    for row in a["rows"]:
        assert row["citation"]["doc"].startswith("schemas/")
        assert row["citation"]["quote"].strip()
        assert row["citation"]["line"] > 0
        checked += 1
    assert checked == a["denominator"]["rows"] > 0, (
        f"{checked} row(s) inspected -- a row set of zero would pass this "
        "while checking nothing")
