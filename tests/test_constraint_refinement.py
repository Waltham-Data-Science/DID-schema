"""#69 -- the gate for tools/check_constraint_refinement.py.

REPORT-ONLY, DELIBERATELY. There is no ratchet here and no threshold: #69 landed
reporting so the team can pick an enforcement threshold from real counts, and a
test that froze today's numbers would have made that call for them (operating
rule 4). What these tests DO assert is that the instrument is not lying about
having looked:

  1. THE DENOMINATOR IS REAL. Classes loaded, inheritance edges resolved and
     field declarations read are all asserted non-trivial. `silentLoss` printed
     "0 empty edges" for two days while reading nothing, and every report that
     rendered it repeated the omission; "0 LOOSENED" would read exactly as clean
     if the walker had stopped at the first directory.

  2. THE CLASSIFIER IS DRIVEN THROUGH A SYNTHETIC TREE whose answers are known
     independently of the tool. "A test written from the same premise as the
     code cannot catch the code" (CLAUDE.md): asserting the tool's verdicts
     against the same tree it derived them from proves only determinism. Every
     verdict -- IDENTICAL, TIGHTENED, LOOSENED, DIVERGENT -- is exercised on a
     hand-built class pair where the right answer was decided before the tool
     ran.

  3. IT AGREES WITH THE NAME-LEVEL TOOL. check_duplicate_field_declarations.py
     answers "declared twice?" and this one answers "which way did it move?".
     They must see the SAME set of redeclarations over the tiers they share --
     if they diverge, one of them is reading a corpus it does not think it is.
"""

import importlib.util
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_tool(name):
    """Load tools/<name>.py by PATH -- `tools/` has no __init__.py, so
    `import tools.x` resolves locally and raises ModuleNotFoundError in CI."""
    path = os.path.join(REPO_ROOT, "tools", name + ".py")
    spec = importlib.util.spec_from_file_location("_refine_tool_" + name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


TOOL = _load_tool("check_constraint_refinement")
CLASSES, LOAD_STATS = TOOL.load_classes()
FIELD_ROWS, FIELD_STATS = TOOL.sweep(CLASSES, "fields")
EDGE_ROWS, EDGE_STATS = TOOL.sweep(CLASSES, "depends_on")

VERDICTS = {"IDENTICAL", "TIGHTENED", "LOOSENED", "DIVERGENT"}


# ---------------------------------------------------------------------------
# 1. the denominator
# ---------------------------------------------------------------------------

def test_the_sweep_actually_read_the_schema_set():
    """Every number this tool prints is meaningless without these."""
    assert LOAD_STATS["files_seen"] > 100, LOAD_STATS
    assert LOAD_STATS["files_parsed"] == LOAD_STATS["files_seen"], (
        f"unparseable schema file(s): {LOAD_STATS['skipped_unparseable']!r}")
    assert len(CLASSES) > 100, f"only {len(CLASSES)} classes loaded"
    assert LOAD_STATS["tiers_found"], "no tier directory was found at all"
    assert not LOAD_STATS["skipped_duplicate_class_name"], (
        "two files declare one class_name -- the second was NOT compared: "
        f"{LOAD_STATS['skipped_duplicate_class_name']!r}")


def test_the_inheritance_graph_was_actually_walked():
    """A redeclaration can only be seen through a RESOLVED superclass edge. If
    edges stopped resolving, every verdict below would silently become zero."""
    assert FIELD_STATS["classes_walked"] == len(CLASSES)
    assert FIELD_STATS["edges_declared"] > 100, FIELD_STATS
    assert FIELD_STATS["edges_resolved"] > 0, (
        "no inheritance edge resolved -- nothing could have been compared")
    assert not FIELD_STATS["edges_unresolved"], (
        "superclass name(s) that match no loaded class; those chains were cut "
        f"short: {FIELD_STATS['edges_unresolved'][:10]!r}")
    assert FIELD_STATS["chains_with_ancestors"] > 100, FIELD_STATS
    assert FIELD_STATS["declarations_seen"] > 500, FIELD_STATS
    assert EDGE_STATS["declarations_seen"] > 100, EDGE_STATS


def test_every_live_verdict_is_one_of_the_four():
    """No row may fall out of the classification unlabelled. Non-vacuous
    without freezing a count: it asserts the shape of whatever is found, and
    passes honestly if the count ever reaches zero -- which the denominator
    tests above already prove would be a real zero."""
    bad = [(r["child"], r["name"], r["verdict"])
           for r in FIELD_ROWS + EDGE_ROWS if r["verdict"] not in VERDICTS]
    assert not bad, f"unclassified redeclaration(s): {bad!r}"
    for r in FIELD_ROWS + EDGE_ROWS:
        assert r["chains"] >= 1
        assert r["child"] in CLASSES and r["parent"] in CLASSES


# ---------------------------------------------------------------------------
# 2. the synthetic tree -- answers known before the tool ran
# ---------------------------------------------------------------------------

def _field(name="f", **kw):
    f = {"name": name, "type": "char", "blank_value": "", "default_value": "",
         "mustBeNonEmpty": False, "mustBeScalar": True, "mustNotHaveNaN": False,
         "queryable": True, "ontology": None, "documentation": "d",
         "constraints": {}}
    f.update(kw)
    return f


def _tree(parent_field, child_field):
    """A two-class chain: `kid` extends `pop`, both declaring one field."""
    return {
        "pop": ("stable", {"document_class": {"class_name": "pop",
                                              "superclasses": []},
                           "fields": [parent_field], "depends_on": []}),
        "kid": ("stable", {"document_class": {
            "class_name": "kid",
            "superclasses": [{"class_name": "pop"}]},
            "fields": [child_field], "depends_on": []}),
    }


def _verdict(parent_field, child_field):
    rows, stats = TOOL.sweep(_tree(parent_field, child_field), "fields")
    assert stats["comparisons"] >= 1, (
        "the synthetic redeclaration was not even compared -- the sweep is not "
        "seeing what the fixture puts in front of it")
    assert len(rows) == 1, rows
    return rows[0]["verdict"]


def test_synthetic_identical_and_documentation_only():
    assert _verdict(_field(), _field()) == "IDENTICAL"
    # A different docstring is not a different constraint.
    assert _verdict(_field(), _field(documentation="other")) == "IDENTICAL"
    # Nor is a capability: queryable does not change what is admissible.
    assert _verdict(_field(queryable=True),
                    _field(queryable=False)) == "IDENTICAL"


def test_synthetic_tightened():
    assert _verdict(_field(mustBeNonEmpty=False),
                    _field(mustBeNonEmpty=True)) == "TIGHTENED"
    assert _verdict(_field(constraints={"maxLength": 256}),
                    _field(constraints={"maxLength": 32})) == "TIGHTENED"
    assert _verdict(_field(constraints={"minimum": 0}),
                    _field(constraints={"minimum": 1})) == "TIGHTENED"
    # Adding a bound the ancestor did not state narrows the admissible set.
    assert _verdict(_field(constraints={}),
                    _field(constraints={"maxLength": 8})) == "TIGHTENED"
    assert _verdict(_field(constraints={"enum": ["a", "b", "c"]}),
                    _field(constraints={"enum": ["a", "b"]})) == "TIGHTENED"
    assert _verdict(
        _field(constraints={"binding": {"strength": "preferred"}}),
        _field(constraints={"binding": {"strength": "required"}})) == "TIGHTENED"


def test_synthetic_loosened():
    assert _verdict(_field(mustBeNonEmpty=True),
                    _field(mustBeNonEmpty=False)) == "LOOSENED"
    assert _verdict(_field(mustBeScalar=True),
                    _field(mustBeScalar=False)) == "LOOSENED"
    # Dropping a bound the ancestor stated is the direction that goes unseen
    # today: nothing reports it, and validateConstraints reads only the block
    # it was handed.
    assert _verdict(_field(constraints={"maxLength": 256}),
                    _field(constraints={})) == "LOOSENED"
    assert _verdict(_field(constraints={"enum": ["a", "b"]}),
                    _field(constraints={"enum": ["a", "b", "c"]})) == "LOOSENED"
    assert _verdict(
        _field(constraints={"binding": {"strength": "required"}}),
        _field(constraints={"binding": {"strength": "optional"}})) == "LOOSENED"


def test_synthetic_divergent():
    # Mixed direction.
    assert _verdict(_field(mustBeNonEmpty=False, constraints={"maxLength": 4}),
                    _field(mustBeNonEmpty=True,
                           constraints={})) == "DIVERGENT"
    # A retype is not a refinement in either direction.
    assert _verdict(_field(type="char"), _field(type="string")) == "DIVERGENT"
    # Overlapping enums: neither set contains the other.
    assert _verdict(_field(constraints={"enum": ["a", "b"]}),
                    _field(constraints={"enum": ["b", "c"]})) == "DIVERGENT"
    # A constraint key with no defined ordering must NOT be read as harmless.
    assert _verdict(_field(constraints={"element_type": "char"}),
                    _field(constraints={"element_type": "double"})) == "DIVERGENT"
    # Structural change inside a composite cell.
    assert _verdict(
        _field(type="ontology_term", fields=[_field("node"), _field("name")]),
        _field(type="ontology_term", fields=[_field("node")])) == "DIVERGENT"


def test_synthetic_nested_difference_is_not_missed():
    """The redeclaration is at the top level; the DIFFERENCE is two levels down.
    A shallow compare would call this IDENTICAL."""
    parent = _field(type="ontology_term",
                    fields=[_field("node", constraints={"maxLength": 64})])
    child = _field(type="ontology_term",
                   fields=[_field("node", constraints={})])
    rows, _ = TOOL.sweep(_tree(parent, child), "fields")
    assert rows[0]["verdict"] == "LOOSENED"
    paths = {d[0] for d in rows[0]["diffs"]}
    assert "f.node" in paths, f"nested path not reported: {paths!r}"


def test_synthetic_depends_on_edge():
    """`mustBeNonEmpty` on an edge is declared everywhere and enforced nowhere,
    so a child that relaxes one is doubly silent."""
    tree = {
        "pop": ("stable", {"document_class": {"class_name": "pop",
                                              "superclasses": []},
                           "fields": [],
                           "depends_on": [{"name": "e", "mustBeNonEmpty": True,
                                           "must_refer_to_document_class": "x"}]}),
        "kid": ("stable", {"document_class": {
            "class_name": "kid", "superclasses": [{"class_name": "pop"}]},
            "fields": [],
            "depends_on": [{"name": "e", "mustBeNonEmpty": False,
                            "must_refer_to_document_class": "x"}]}),
    }
    rows, stats = TOOL.sweep(tree, "depends_on")
    assert stats["comparisons"] == 1, stats
    assert len(rows) == 1 and rows[0]["verdict"] == "LOOSENED", rows


def test_an_unresolved_superclass_is_counted_not_ignored():
    """The failure this project keeps paying for: a walk that stops early and
    reports a clean zero. An edge to a class we do not hold must show up in the
    denominator as a comparison that did NOT happen."""
    tree = {
        "kid": ("stable", {"document_class": {
            "class_name": "kid",
            "superclasses": [{"class_name": "a_class_we_do_not_have"}]},
            "fields": [_field()], "depends_on": []}),
    }
    rows, stats = TOOL.sweep(tree, "fields")
    assert rows == []
    assert stats["edges_declared"] == 1
    assert stats["edges_resolved"] == 0
    assert len(stats["edges_unresolved"]) == 1, stats


# ---------------------------------------------------------------------------
# 3. agreement with the name-level tool
# ---------------------------------------------------------------------------

def test_agrees_with_the_duplicate_name_checker():
    """Two tools, two questions, one set of rows. Compared over the tiers they
    BOTH read (the name-level tool reads stable+draft; this one also reads
    deprecated), so the check is about agreement, not about tier choice."""
    dup = _load_tool("check_duplicate_field_declarations")
    dup_classes = dup.load_classes()
    assert dup_classes, "the name-level tool read no classes"
    dup_rows = dup.find_duplicates(dup_classes)

    # (declaring class, field name) pairs, from each tool's own output.
    theirs = set()
    for leaf, name, owners in dup_rows:
        for owner in owners:
            if owner != leaf:
                continue
            theirs.add((leaf, name))
    mine = {(r["child"], r["name"]) for r in FIELD_ROWS
            if r["child_tier"] in ("stable", "draft")
            and r["parent_tier"] in ("stable", "draft")}
    assert theirs, "the name-level tool reported no duplicate owners at all"
    assert mine, (
        "this tool found no redeclarations while the name-level tool did -- "
        "one of them is reading a corpus it does not think it is")
    assert theirs <= mine, (
        f"seen by the name-level tool and NOT by this one: {sorted(theirs - mine)!r}")


def test_the_report_prints_its_denominator_first():
    """Operating rule 5, asserted on the rendered output rather than trusted:
    the first line a reader sees must be the denominator, unconditionally."""
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = TOOL.main([])
    out = buf.getvalue().splitlines()
    assert rc == 0
    assert out[0] == "DENOMINATOR", out[:3]
    body = "\n".join(out)
    for required in ("classes walked", "inheritance edges RESOLVED",
                     "FIELD comparisons performed",
                     "declared-but-unreadable SKIPPED"):
        assert required in body, f"denominator omits {required!r}"


def test_enforce_fails_loudly_while_no_threshold_is_set():
    """A report-only tool must not have an --enforce that quietly passes. #69
    landed reporting; until the team sets a threshold, asking for enforcement
    is an error, not a no-op."""
    import io
    import contextlib
    assert TOOL.ENFORCEMENT_THRESHOLD is None, (
        "a threshold was set -- update this test and CI deliberately, with the "
        "count it was set from")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = TOOL.main(["--enforce"])
    assert rc == 1
    assert "ENFORCEMENT_THRESHOLD is unset" in buf.getvalue()
