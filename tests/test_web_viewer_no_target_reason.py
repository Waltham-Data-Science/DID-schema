"""The viewer must not assert a dissolution it was never told about.

`web/src/Coverage.tsx` rendered the literal sentence

    no target — it dissolves or is deleted

for EVERY ledger row with an empty `decided_targets`. There are four causes and
they are different facts: a signed dissolution (no target really is the
answer), a signed passthrough, a DISPUTED row where the record states two
incompatible dispositions, and a gap where nothing was ever recorded. Three of
the four were shown to the reader as a settled decision to delete the class.

    DENOMINATOR: 12 ledger rows with no target of any kind
      DISSOLVES -- the signed answer                     3
      NO TARGET AND NO DISSOLUTION RECORDED -- a gap     3
      DISPUTED -- two incompatible dispositions          1
      (no label recorded)                                5

The DISPUTED row is why this matters rather than being tidy-up. `ngrid` is
contested because one section of its plan says it phases into `sampled_body`
while that same document's sign-off says it is deleted -- and on 2026-08-11 two
commits each read one half and each "corrected" the other. A cell that shows a
contested row as settled is how the losing half stops being looked for.
"""
import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COVERAGE_TSX = os.path.join(REPO_ROOT, "web", "src", "Coverage.tsx")
TYPES_TS = os.path.join(REPO_ROOT, "web", "src", "types.ts")
LEDGER = os.path.join(REPO_ROOT, "schemas", "V_eta_coverage_ledger.json")


def read(path):
    with open(path) as fh:
        return fh.read()


def test_the_viewer_states_no_blanket_dissolution_sentence():
    body = read(COVERAGE_TSX)
    banned = "it dissolves or is deleted"
    # The phrase may legitimately appear inside the explanatory comment that
    # records why it was removed, so only executable text is searched.
    code = re.sub(r"//.*$", "", body, flags=re.MULTILINE)
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    assert banned not in code, (
        f"Coverage.tsx renders {banned!r} again. That sentence asserted a signed "
        "dissolution for rows that are disputed, passed through, or simply "
        "unrecorded.")


def test_a_row_with_no_recorded_reason_renders_as_unknown():
    """The stale-artifact path, which is the one that would regress quietly.

    A ledger predating the reason field carries no label. Falling back to the
    old sentence would reinstate the exact assertion this replaces, and would
    do it invisibly -- the viewer would look correct against a fresh ledger and
    lie against an old one.
    """
    body = read(COVERAGE_TSX)
    assert "reason not recorded" in body, (
        "there is no UNKNOWN rendering for a ledger with no reason label")
    assert "not a dissolution" in body, (
        "the unknown case does not say that it is NOT a dissolution, so a "
        "reader may still take a blank as a decision")


def test_disputed_rows_are_visually_distinguished():
    body = read(COVERAGE_TSX)
    assert "DISPUTED" in body, (
        "the viewer does not single out DISPUTED rows, so a contested "
        "disposition renders identically to a settled one")


def test_the_type_declares_the_field_as_optional():
    """Optional on purpose: an older ledger genuinely lacks it.

    Declaring it required would make the stale-artifact case a type error
    rather than the UNKNOWN rendering it needs to be.
    """
    body = read(TYPES_TS)
    m = re.search(r"no_target_reason_label\?\s*:\s*string\s*\|\s*null", body)
    assert m, (
        "no_target_reason_label is missing or is not declared optional-and-"
        "nullable in types.ts")


def test_the_ledger_actually_supplies_the_field():
    """Guards against the viewer reading a key the generator never writes.

    Without this, every row would take the UNKNOWN branch and the panel would
    honestly report that it cannot tell -- which is safe, and completely
    useless. The point is to check the two sides agree on the name.
    """
    import json
    with open(LEDGER) as fh:
        rows = json.load(fh)["rows"]
    assert rows, "the ledger has no rows"
    blank = [r for r in rows
             if not r.get("decided_targets") and not r.get("targets")]
    assert blank, (
        "no ledger row has an empty target set, so this test proves nothing "
        "about the rendering it is meant to guard")
    labelled = [r for r in blank if r.get("no_target_reason_label")]
    assert labelled, (
        f'{len(blank)} row(s) have no target and NONE carries `no_target_reason_label` -- the viewer would render every one as UNKNOWN, and the field the generator writes is not the one the viewer reads')
