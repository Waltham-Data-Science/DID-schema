"""Tests for `tools/regen_binding_strengths.py` -- the derived `strength` column.

WHY THIS FILE EXISTS
--------------------
`strength` was stored twice: on the field's `constraints.binding`, and again on
`entity_field_bindings` in the registry. The three pairs AGREED, and nothing
compared them, so they agreed by coincidence. The team's call is that THE FIELD
IS AUTHORITATIVE; the registry's copy is now a DERIVED column.

A derived column is only worth the name if three things are true, and each is
pinned here by MUTATION -- break it, watch the named test go red, revert:

  * a change to the FIELD moves the registry
        test_a_change_to_the_field_moves_the_registry_column
  * a hand-edited REGISTRY strength fails --check rather than standing
        test_a_hand_edited_registry_strength_fails_check
  * a binding with NO strength is an ERROR, not a silent default
        test_a_binding_with_no_strength_is_an_error_not_a_default
        test_every_binding_in_the_built_tree_declares_a_strength

Most tests build a MINIMAL synthetic tree in tmp_path rather than reading the
live one. That is deliberate and it is the same reasoning
`check_binding_governance.strength_agreement` records: a test that can only read
the live files cannot check a rule about rows nobody has written yet -- and
every failure mode here is a row or a field that does not exist in the tree
today. The live tree is asserted separately, where the question really is about
the tree.
"""

import importlib.util
import json
import os
from pathlib import Path

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(REPO_ROOT, "tools")
VETA = os.path.join(REPO_ROOT, "schemas", "V_eta")
LIVE_REGISTRY = os.path.join(VETA, "stable", "binding_registry_meta.json")


def _load_tool(name):
    spec = importlib.util.spec_from_file_location(name,
                                                  os.path.join(TOOLS, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rbs = _load_tool("regen_binding_strengths")
cbg = _load_tool("check_binding_governance")


# ---------------------------------------------------------------------------
# a minimal synthetic tree
# ---------------------------------------------------------------------------

def _field(name, binding=None, subfields=None):
    f = {"name": name, "type": "ontology_term", "constraints": {}}
    if binding is not None:
        f["constraints"]["binding"] = binding
    if subfields:
        f["fields"] = subfields
    return f


def _make_tree(tmp_path, classes, registry):
    """Write a V_eta-shaped scratch tree. Returns (veta_root, registry_path)."""
    veta = tmp_path / "V_eta"
    for tier in rbs.TIERS:
        (veta / tier).mkdir(parents=True)
    for cls_name, fields in classes.items():
        doc = {"document_class": {"class_name": cls_name, "class_version": 1,
                                  "superclasses": []},
               "fields": fields}
        (veta / "stable" / (cls_name + ".json")).write_text(
            json.dumps(doc, indent=4) + "\n")
    reg_path = veta / "stable" / "binding_registry_meta.json"
    reg_path.write_text(json.dumps(registry, indent=4) + "\n")
    return str(veta), str(reg_path)


def _run(veta, reg_path, check=False):
    lines = []
    rc, detail = rbs.run(veta=veta, registry_path=reg_path, check=check,
                         out=lines.append)
    return rc, "\n".join(lines), detail


def _rows(reg_path, list_name="entity_field_bindings"):
    return json.loads(Path(reg_path).read_text())[list_name]


_ONE_CLASS = {"demo": [_field("f", {"vocabulary": "openMINDS",
                                    "term_set": "DemoSet",
                                    "strength": "required"})]}


def _registry(rows=None, **extra):
    reg = {"$id": "scratch",
           "subject_statement_bindings": [],
           "relation_bindings": [],
           "entity_field_bindings": rows if rows is not None else [
               {"class": "demo", "field": "f", "vocabulary": "openMINDS",
                "term_set": "DemoSet", "closed": True}],
           "binding_examples": []}
    reg.update(extra)
    return reg


# ---------------------------------------------------------------------------
# 1. the derivation itself
# ---------------------------------------------------------------------------

def test_the_column_is_derived_from_the_field_not_from_the_registry(tmp_path):
    """A registry row that states no strength acquires the FIELD's."""
    veta, reg = _make_tree(tmp_path, _ONE_CLASS, _registry())
    assert "strength" not in _rows(reg)[0], "fixture already had the answer in it"

    rc, out, _ = _run(veta, reg)

    assert rc == 0, out
    rows = _rows(reg)
    assert len(rows) == 1
    assert rows[0]["strength"] == "required"
    assert "DENOMINATOR: 1 bound field declaration(s) read" in out


def test_a_change_to_the_field_moves_the_registry_column(tmp_path):
    """MUTATION PROPERTY 1. The field is the only place the value comes from.

    Written as one test over TWO states rather than two tests, because the
    claim is about the DIFFERENCE: a generator that hardcoded `required` would
    pass the first half on its own.
    """
    veta, reg = _make_tree(tmp_path, _ONE_CLASS, _registry())
    rc, out, _ = _run(veta, reg)
    assert rc == 0, out
    first = _rows(reg)[0]["strength"]

    cls_path = os.path.join(veta, "stable", "demo.json")
    doc = json.loads(Path(cls_path).read_text())
    doc["fields"][0]["constraints"]["binding"]["strength"] = "preferred"
    Path(cls_path).write_text(json.dumps(doc, indent=4) + "\n")

    rc, out, _ = _run(veta, reg)
    assert rc == 0, out
    second = _rows(reg)[0]["strength"]

    assert (first, second) == ("required", "preferred"), (
        f"the registry column did not follow the field: {first!r} -> {second!r}")


def test_regeneration_is_idempotent(tmp_path):
    veta, reg = _make_tree(tmp_path, _ONE_CLASS, _registry())
    _run(veta, reg)
    once = Path(reg).read_text()
    rc, out, _ = _run(veta, reg)
    assert rc == 0, out
    assert Path(reg).read_text() == once, "a second run changed the file"
    assert "UNCHANGED" in out


# ---------------------------------------------------------------------------
# 2. the checker: a hand-edited registry must not stand
# ---------------------------------------------------------------------------

def test_a_hand_edited_registry_strength_fails_check(tmp_path):
    """MUTATION PROPERTY 2. This is the only thing standing between the two
    stored copies and a silent divergence, so it is asserted on the EXIT CODE
    and on the message naming both sides."""
    veta, reg = _make_tree(tmp_path, _ONE_CLASS, _registry(rows=[
        {"class": "demo", "field": "f", "vocabulary": "openMINDS",
         "term_set": "DemoSet", "closed": True, "strength": "preferred"}]))

    rc, out, detail = _run(veta, reg, check=True)

    assert rc == 1, out
    assert detail["stale"] is True
    assert len(detail["disagreements"]) == 1
    d = detail["disagreements"][0]
    assert (d["registry_says"], d["field_says"]) == ("preferred", "required")
    assert "the FIELD says 'required'" in out
    assert "STALE" in out


def test_check_writes_nothing_even_when_it_fails(tmp_path):
    veta, reg = _make_tree(tmp_path, _ONE_CLASS, _registry(rows=[
        {"class": "demo", "field": "f", "vocabulary": "openMINDS",
         "term_set": "DemoSet", "closed": True, "strength": "preferred"}]))
    before = Path(reg).read_text()

    rc, _out, _ = _run(veta, reg, check=True)

    assert rc == 1
    assert Path(reg).read_text() == before, "--check modified the registry"


def test_the_live_registry_column_is_up_to_date():
    """The composed `--check` gates.py runs, run again here so a stale column
    fails pytest on its own and not only through the driver."""
    rc, out, detail = _run(VETA, LIVE_REGISTRY, check=True)
    assert rc == 0, out
    assert detail["disagreements"] == []


# ---------------------------------------------------------------------------
# 3. a binding with no strength -- ERROR, not a default
# ---------------------------------------------------------------------------

def test_a_binding_with_no_strength_is_an_error_not_a_default(tmp_path):
    """MUTATION PROPERTY 3, the row scope.

    The decision recorded in the tool: there is NO default. `preferred` would
    make an ungoverned field read as governed; `required` would arm a gate
    nobody has measured. Absence means the author did not say.
    """
    veta, reg = _make_tree(
        tmp_path,
        {"demo": [_field("f", {"vocabulary": "openMINDS", "term_set": "DemoSet"})]},
        _registry())
    before = Path(reg).read_text()

    rc, out, detail = _run(veta, reg)

    assert rc == 1, out
    assert len(detail["errors"]) == 1
    assert "declares NO strength" in out
    assert "There is no default" in out
    assert Path(reg).read_text() == before, "a failed derivation still wrote the file"
    assert "strength" not in _rows(reg)[0]


def test_every_binding_in_the_built_tree_declares_a_strength():
    """MUTATION PROPERTY 3, the TREE scope -- and the reason it is separate.

    The generator can only refuse rows the registry catalogues, which is 3 of
    the bound declarations. The others have no registry row at all, so a
    strength-less binding could arrive there without a word. This asserts the
    rule where it actually has to hold.

    THE FLOOR MOVED 14 -> 13 ON 2026-08-11, AND IT MOVED DOWN, WHICH IS THE
    DIRECTION THIS ASSERTION EXISTS TO CATCH -- so the reason is written here
    rather than the number quietly edited. #65 increment 3a deleted
    `epoch_relative_reference`, and its `epoch_clock` was one of the 14: a
    `char` bound to NDI's nine clocktypes. The declaration did not lose its
    strength, it left with its class. The surviving epoch carrier
    (`epoch_bounded_reference.epoch_clock`) is pinned by
    `test_veta.py::test_retiring_epoch_clock_fields_untouched_by_67`, so the
    binding that mattered is still asserted somewhere.
    """
    index, den = rbs.bound_fields(VETA)
    assert den["bound_field_declarations"] == len(index)
    assert len(index) >= 13, (
        f'only {len(index)} bound declarations found -- the sweep stopped descending, and a shrinking denominator is how this check goes quietly vacuous')
    assert den["bound_field_declarations_nested"] >= 2, (
        "the two nested bindings on relative_reference.value are not being "
        "reached; a top-level-only sweep would call the tree consistent")
    missing = sorted(k for k, v in index.items()
                     if v["binding"].get("strength") is None)
    assert missing == [], (
        f"binding(s) with no strength: {missing}. There is no default -- declare one.")


# ---------------------------------------------------------------------------
# 4. the rules about rows the derivation cannot reach
# ---------------------------------------------------------------------------

def test_a_registry_row_naming_no_field_may_not_state_a_strength(tmp_path):
    """31 of the 34 normative rows name no field. A strength there is an
    authority statement nothing can agree with or contradict."""
    reg_doc = _registry(rows=[])
    reg_doc["relation_bindings"] = [
        {"relation": {"node": "", "name": "part_of"},
         "class": "directed_relation", "strength": "required"}]
    veta, reg = _make_tree(tmp_path, _ONE_CLASS, reg_doc)

    rc, out, detail = _run(veta, reg)

    assert rc == 1, out
    assert len(detail["errors"]) == 1
    assert "names no field" in out


def test_a_registry_row_naming_a_field_with_no_binding_is_an_error(tmp_path):
    """The registry is a catalogue of REAL bindings. A row for a field that
    declares none has nothing to derive from, and inventing `null` for it would
    make the catalogue disagree with the schema silently."""
    veta, reg = _make_tree(tmp_path, {"demo": [_field("f")]}, _registry())

    rc, out, detail = _run(veta, reg)

    assert rc == 1, out
    assert len(detail["errors"]) == 1
    assert "declares no constraints.binding" in out


def test_the_generator_never_adds_removes_or_reorders_a_row(tmp_path):
    """Membership of the catalogue is a DECISION (operating rule 4). This tool
    fills one column and must not be able to change what is catalogued."""
    rows = [
        {"class": "demo", "field": "f", "vocabulary": "openMINDS",
         "term_set": "DemoSet", "closed": True, "notes": "keep me"},
        {"class": "demo", "field": "g", "vocabulary": "openMINDS",
         "term_set": "OtherSet", "closed": False},
    ]
    classes = {"demo": [
        _field("f", {"vocabulary": "openMINDS", "term_set": "DemoSet",
                     "strength": "required"}),
        _field("g", {"vocabulary": "openMINDS", "term_set": "OtherSet",
                     "strength": "preferred"}),
    ]}
    veta, reg = _make_tree(tmp_path, classes, _registry(rows=rows))
    before = json.loads(Path(reg).read_text())

    rc, out, _ = _run(veta, reg)
    assert rc == 0, out
    after = json.loads(Path(reg).read_text())

    assert list(after) == list(before), "a top-level key was added or removed"
    assert len(after["entity_field_bindings"]) == 2
    for i, row in enumerate(after["entity_field_bindings"]):
        original = before["entity_field_bindings"][i]
        assert row["class"] == original["class"]
        assert row["field"] == original["field"]
        assert {k: v for k, v in row.items() if k != "strength"} == original
    assert [r["strength"] for r in after["entity_field_bindings"]] == \
        ["required", "preferred"]


def test_a_nested_binding_is_reachable_by_its_dotted_path(tmp_path):
    """Two of the fourteen live bindings are nested one level down. If the
    index keyed them by bare name they would collide with a top-level field of
    the same name and the wrong strength would be derived."""
    classes = {"demo": [
        _field("value", None, subfields=[
            _field("relation", {"root": "owl_time_interval", "values": ["a"],
                                "strength": "required"})]),
    ]}
    veta, reg = _make_tree(tmp_path, classes, _registry(rows=[
        {"class": "demo", "field": "value.relation", "closed": False}]))

    rc, out, _ = _run(veta, reg)

    assert rc == 0, out
    assert len(_rows(reg)) == 1
    assert _rows(reg)[0]["strength"] == "required"


# ---------------------------------------------------------------------------
# 5. the second-source-of-truth guard
# ---------------------------------------------------------------------------

def test_build_v_eta_hand_authors_no_strength_in_the_registry_literal():
    """The whole point of the derivation is that the value exists ONCE.

    `ENTITY_FIELD_BINDINGS` in build_v_eta.py used to state `strength` beside
    every row. Restoring it would be inert -- the generator overwrites the key
    -- which is exactly why it must not come back: an editor would change a
    literal, see the built file agree, and believe they had changed the rule.
    """
    import ast
    src = Path(os.path.join(TOOLS, "build_v_eta.py")).read_text()
    tree = ast.parse(src)
    literals = [n.value for n in ast.walk(tree)
                if isinstance(n, ast.Assign)
                and any(getattr(t, "id", None) == "ENTITY_FIELD_BINDINGS"
                        for t in n.targets)]
    assert len(literals) == 1, (
        f'expected exactly one ENTITY_FIELD_BINDINGS assignment, found {len(literals)}')
    rows = ast.literal_eval(literals[0])
    assert len(rows) == 3, (
        f'expected the 3 openMINDS dataset rows, found {len(rows)} -- if the catalogue grew, this denominator must move deliberately')
    offenders = [r for r in rows if "strength" in r]
    assert offenders == [], (
        f"build_v_eta.py hand-authors a strength again: {offenders}. The field is "
        "authoritative; tools/regen_binding_strengths.py derives this column.")


def test_the_registry_list_table_is_not_a_second_hand_kept_copy():
    """Two files enumerate the registry's lists and their normativity. Two
    hand-kept copies of one list is the defect this whole change is about, so
    they are asserted equal rather than merely both present."""
    assert rbs.REGISTRY_LISTS == cbg.REGISTRY_LISTS
    assert len(rbs.REGISTRY_LISTS) == 4


# ---------------------------------------------------------------------------
# 6. the live tree's denominators, stated so a shrinking sweep is visible
# ---------------------------------------------------------------------------

def test_the_live_derivation_reports_its_denominator_first():
    lines = []
    rc, _detail = rbs.run(veta=VETA, registry_path=LIVE_REGISTRY, check=True,
                          out=lines.append)
    assert rc == 0
    assert lines[0].startswith("DENOMINATOR: "), lines[0]
    reg = json.loads(Path(LIVE_REGISTRY).read_text())
    total = sum(len(reg[k]) for k in rbs.REGISTRY_LISTS)
    assert total == 38, f'registry row count moved: {total}'
    assert f'{total} row(s)' in lines[0]


@pytest.mark.parametrize("list_name,expected", [
    ("subject_statement_bindings", 5),
    ("relation_bindings", 26),
    ("entity_field_bindings", 3),
    ("binding_examples", 4),
])
def test_the_live_registry_lists_have_the_sizes_the_record_claims(list_name,
                                                                  expected):
    reg = json.loads(Path(LIVE_REGISTRY).read_text())
    assert len(reg[list_name]) == expected


def test_only_the_rows_that_name_a_field_carry_a_strength_in_the_live_registry():
    reg = json.loads(Path(LIVE_REGISTRY).read_text())
    with_strength, naming_a_field = [], []
    for list_name in rbs.REGISTRY_LISTS:
        for i, row in enumerate(reg[list_name]):
            if "strength" in row:
                with_strength.append((list_name, i))
            if row.get("class") and row.get("field"):
                naming_a_field.append((list_name, i))
    assert len(naming_a_field) == 3, naming_a_field
    assert with_strength == naming_a_field
