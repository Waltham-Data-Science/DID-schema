"""The ledger fields that were computed, committed, and rendered by nothing.

`tools/coverage.py` computes `build_state` and `target_gap` for all 102 rows and
writes them into the ledger the viewer serves. Measured 2026-08-12, before the
class-detail view existed:

    field occurrences in web/src/Coverage.tsx
      disposition 10   targets 10   how 15   migrator 13   carried 7
      decided_targets 3   second_pass 2   no_target_reason 1
      build_state 0    <-- never rendered
      target_gap  0    <-- never rendered

A number nobody can see is not evidence, and these two are the ones that answer
"is this finished". `build_state` splits a question the `fate` badge runs
together -- is the SCHEMA built, and does a MIGRATOR emit it -- and for several
classes exactly one of those halves is true. `target_gap` is the narrow
successor to the retired `gap`: no target AND no dissolution recorded, which is
a hole in the RECORD rather than a decision to delete a class.

These tests hold the rendering, and hold it AGAINST THE LEDGER rather than
against a literal: if a future ledger stops carrying either field, the tests say
so instead of passing on a viewer that renders a field nothing produces.
"""
import json
import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB_SRC = os.path.join(REPO_ROOT, "web", "src")
LEDGER = os.path.join(REPO_ROOT, "schemas", "V_eta_coverage_ledger.json")


def read(name):
    with open(os.path.join(WEB_SRC, name)) as fh:
        return fh.read()


def code_only(body):
    """Strip comments: a field NAMED in a comment is not a field rendered."""
    body = re.sub(r"/\*.*?\*/", "", body, flags=re.DOTALL)
    return re.sub(r"//.*$", "", body, flags=re.MULTILINE)


def ledger_rows():
    with open(LEDGER) as fh:
        return json.load(fh)["rows"]


def test_the_ledger_really_carries_the_fields_the_viewer_renders():
    """The denominator for everything below. A viewer rendering a field the
    ledger does not produce would be a different defect wearing the same
    green."""
    rows = ledger_rows()
    assert len(rows) > 0
    with_build_state = [r for r in rows if "build_state" in r]
    with_target_gap = [r for r in rows if "target_gap" in r]
    assert len(with_build_state) == len(rows), (
        f"DENOMINATOR: {len(rows)} ledger rows, only {len(with_build_state)} "
        "carry build_state")
    assert len(with_target_gap) == len(rows)
    # And the five keys the panel renders individually, so a rename upstream
    # fails here rather than rendering five blanks.
    keys = {"schema_targets_named", "schema_targets_built",
            "schema_targets_missing", "migrator_emits_decided_targets",
            "has_per_class_migrator"}
    for r in with_build_state:
        assert keys <= set(r["build_state"]), (
            f"{r['v1_class']}: build_state is missing {keys - set(r['build_state'])}")


def test_build_state_is_rendered_field_by_field():
    body = code_only(read("ClassDetail.tsx"))
    assert "build_state" in body, (
        "build_state is computed for every row and rendered nowhere -- which is "
        "the state this view was built to end")
    for key in ("schema_targets_named", "schema_targets_built",
                "schema_targets_missing", "migrator_emits_decided_targets",
                "has_per_class_migrator"):
        assert key in body, f"build_state.{key} reaches no reader"


def test_the_two_halves_of_build_state_are_not_summed_into_one_verdict():
    """`schema_targets_built` is a fact about THIS repository;
    `migrator_emits_decided_targets` is a fact about DID-matlab. Collapsing
    them into a single done/not-done light is the specific thing the split
    exists to prevent, so the panel must render both."""
    body = code_only(read("ClassDetail.tsx"))
    i_schema = body.find("schema_targets_built")
    i_migrator = body.find("migrator_emits_decided_targets")
    assert i_schema >= 0 and i_migrator >= 0
    assert i_schema != i_migrator


def test_target_gap_is_rendered_and_is_not_called_a_decision():
    body = code_only(read("ClassDetail.tsx")) + code_only(read("Coverage.tsx"))
    assert "target_gap" in body, "target_gap reaches no reader"
    # The wording matters as much as the presence: the retired `gap` concept
    # was what let 32 rows be labelled "dissolved (rename/decompose)" without
    # evidence. A gap is a hole in the record, and must say so.
    assert "not a decision" in body


def test_the_ndi_declaration_reaches_the_reader():
    """The other half of the walkthrough: what the v1 document ACTUALLY is.
    The ground truth is generated, committed and, until this view, was served
    to nobody."""
    body = code_only(read("ClassDetail.tsx"))
    for key in ("depends_on_required", "writer_divergence",
                "v_alpha_divergence", "migrator_reads"):
        assert key in body, f"{key} is in the ground truth and reaches no reader"


def test_the_writer_wins_rule_is_stated_where_the_divergence_is_shown():
    """`where template and WRITER disagree, the WRITER wins` is the whole
    ground-truth track. A reader shown both without the rule takes the losing
    side."""
    body = read("ClassDetail.tsx")
    assert "the writer wins" in body.lower()


def test_the_derived_stage_is_optional_and_never_invented():
    """Another generator is adding a derived 0-5 migration stage. This viewer
    renders it if present and must NOT synthesise one: rendering an absent
    stage as 0 would be a claim about every class in the ledger."""
    body = code_only(read("ClassDetail.tsx"))
    assert "stage" in body
    # The guard that makes it optional, spelled exactly as the component does.
    assert "stage === undefined || stage === null" in body, (
        "the stage renderer must return nothing when the ledger carries no "
        "stage, rather than defaulting")
    rows = ledger_rows()
    carrying = [r for r in rows if r.get("stage") is not None]
    print(f"DENOMINATOR: {len(rows)} ledger rows, {len(carrying)} carry a "
          "`stage` today -- the renderer is present either way")
