"""The tenet -> class map, and the four ways a curated table goes wrong.

A curated table is an assertion until something checks it, and the failure mode
is specific: a row that reads well, cites a document nobody opens, and puts a
class name in front of a reader that no longer means anything. Every test below
MUTATES the generator and proves the mutation reddens -- a check nobody has
watched fail is a check nobody has evidence for.

The mutations, and what each one stands for:

    a row citing a document that does not exist   the citation is decorative
    a row whose anchor is not in its document     the citation points nowhere
    a row naming a class in no register           a typo, or an invention
    the lookup stubbed to match EVERYTHING        the instrument measures nothing

The last is the one this repository keeps paying for. A substantiation lookup
that says yes to everything substantiates every row, including the wrong ones,
and looks exactly like one that works -- so the generator asks it for a canary
string that cannot occur in any document before it trusts a single row.

The fifth check is not a mutation: a tenet with no rows must be REPORTED. An
empty panel and an unmapped tenet render the same and are not the same fact.
"""
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

import tenet_map as tm  # noqa: E402

ASSET = REPO / "web" / "public" / "tenets.json"


def _asset():
    assert ASSET.exists(), (
        f"{ASSET.relative_to(REPO)} is absent -- run "
        "`python3 tools/tenet_map.py` and commit the result")
    return json.loads(ASSET.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# The table as it stands
# --------------------------------------------------------------------------
def test_denominator_is_stated_and_every_tenet_is_accounted_for():
    a = _asset()
    d = a["denominator"]
    assert d["tenets_declared"] == 14
    assert len(a["tenets"]) == 14
    assert d["rows"] == len(a["rows"]) > 0
    # Reported, not asserted to be zero: the point is that the count exists and
    # the unmapped tenets are NAMED. A future table with a bare tenet must
    # still pass this -- and must still say which one.
    assert isinstance(d["tenets_with_no_substantiated_row"], list)
    assert (d["tenets_with_at_least_one_row"]
            + len(d["tenets_with_no_substantiated_row"]) == 14)


def test_every_citation_resolves_in_the_document_on_disk():
    """Re-checked against `schemas/` rather than trusted from the artifact:
    a citation is only worth what a reader finds when they open the file."""
    a = _asset()
    for row in a["rows"]:
        c = row["citation"]
        doc = REPO / c["doc"]
        assert doc.is_file(), f"{row['tenet']}: cited {c['doc']} does not exist"
        lines = doc.read_text(encoding="utf-8").splitlines()
        assert 1 <= c["line"] <= len(lines), (
            f"{row['tenet']}: cited line {c['line']} is outside {c['doc']}")
        assert c["anchor"] in lines[c["line"] - 1], (
            f"{row['tenet']}: the anchor is not on the line {c['doc']} cites")


def test_tenet_statements_are_quoted_from_the_north_star():
    """The tenet text is parsed out of V_eta_tenets.md, never retyped here --
    a paraphrase drifting from the tenet it renders is the same defect as a
    plan document's header drifting from its own sign-off."""
    a = _asset()
    doc = (REPO / "schemas" / "V_eta_tenets.md").read_text(encoding="utf-8")
    # DENOMINATOR FIRST. The loop asserts a property of every tenet, so an
    # artifact carrying none would pass it having compared nothing --
    # `check_vacuous_tests.py` flagged this function for exactly that, and the
    # flag was correct.
    checked = 0
    for t in a["tenets"]:
        assert f"### {t['id']} — {t['title']}" in doc
        assert t["statement"].strip(), f"{t['id']} carries an empty statement"
        checked += 1
    assert checked == 14, (
        f"{checked} tenet statement(s) compared against the north star, "
        "expected 14")


def test_plan_only_class_names_are_flagged_rather_than_rendered_plain():
    """A name vouched for by the cited plan ALONE is a decided-but-unbuilt
    target or a superseded class. It must reach the viewer captioned."""
    a = _asset()
    flagged = {c for r in a["rows"] for c in r["plan_only_classes"]}
    assert flagged == set(a["denominator"]["classes_vouched_only_by_the_cited_plan"])
    for row in a["rows"]:
        for name in row["plan_only_classes"]:
            assert row["class_registers"][name] == ["named_in_cited_plan"]


def test_committed_asset_matches_the_generator():
    fresh = tm.serialize(tm.build())
    assert ASSET.read_text(encoding="utf-8") == fresh, (
        f"{ASSET.relative_to(REPO)} is STALE -- run `python3 tools/tenet_map.py`")


# --------------------------------------------------------------------------
# THE MUTATIONS
# --------------------------------------------------------------------------
def _row(**kw):
    base = {"tenet": "T1", "change": "c", "before": ["subject"],
            "after": ["subject"], "doc": "V_eta_tenets.md",
            "anchor": "### T1", "note": ""}
    base.update(kw)
    return tm.Row(**base)


def test_mutation_a_row_citing_a_missing_document_fails():
    with pytest.raises(FileNotFoundError) as exc:
        tm.build(table=[_row(doc="V_eta_no_such_plan.md")])
    assert "does not exist" in str(exc.value)


def test_mutation_a_row_whose_anchor_is_absent_fails():
    with pytest.raises(ValueError) as exc:
        tm.build(table=[_row(anchor="this sentence is not in the tenets file")])
    assert "UNSUBSTANTIATED ROW" in str(exc.value)


def test_mutation_a_row_naming_an_unknown_class_fails():
    with pytest.raises(ValueError) as exc:
        tm.build(table=[_row(after=["subject", "wibble_observation"])])
    assert "UNKNOWN CLASS NAME" in str(exc.value)
    assert "wibble_observation" in str(exc.value)


def test_mutation_a_lookup_that_matches_everything_fails():
    """THE VACUITY GUARD. Stub the substantiation lookup so it returns a hit
    for anything. Without the negative control this run would emit a full,
    confident artifact in which every row is 'substantiated' -- including rows
    whose anchors are nowhere."""
    def matches_everything(text, anchor):
        return [(1, "whatever you were looking for")]

    with pytest.raises(ValueError) as exc:
        tm.build(finder=matches_everything)
    assert "VACUOUS" in str(exc.value)

    # And prove the guard is what stopped it, not the row content: the same
    # stubbed lookup would otherwise have substantiated a row that cites an
    # anchor no document contains.
    hits = matches_everything("anything at all", tm.CANARY)
    assert hits, "the stub must match the canary, else this test proves nothing"


def test_mutation_a_tenet_with_no_rows_is_reported_not_silently_empty():
    """The one that is NOT an exception. A tenet nobody mapped must arrive at
    the viewer NAMED, so an empty panel and an unmapped tenet stop looking the
    same."""
    only_t1 = [r for r in tm.TENET_MAP if r.tenet == "T1"]
    assert only_t1, "the table has no T1 row, so this mutation proves nothing"
    payload = tm.build(table=only_t1)
    unmapped = payload["denominator"]["tenets_with_no_substantiated_row"]
    assert unmapped == [f"T{i}" for i in range(2, 15)]
    assert payload["denominator"]["tenets_with_at_least_one_row"] == 1
    # Still rendered -- all 14 tenets reach the viewer, 13 of them with no row.
    assert len(payload["tenets"]) == 14


def test_the_real_table_leaves_no_tenet_unmapped_today():
    """Separate from the test above ON PURPOSE. That one holds the REPORTING
    machinery, which must keep working when a tenet loses its last row; this
    one records what is true right now, and is allowed to fail the day the
    table shrinks."""
    payload = _asset()
    unmapped = payload["denominator"]["tenets_with_no_substantiated_row"]
    assert unmapped == [], (
        f"{len(unmapped)} tenet(s) have no substantiated row: {unmapped}. "
        "That is reportable, not fatal -- update this test with the reason.")
