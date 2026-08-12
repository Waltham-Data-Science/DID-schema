"""Tests for `tools/check_prose_counts.py`.

WHY THIS FILE EXISTS
--------------------
The checker's whole value rests on two properties, and BOTH of them fail
quietly when they fail:

  * its expected values come from the TREE, not from the document it is
    checking. A checker whose expectation is read out of the prose agrees by
    construction and reports a clean zero forever. That is `silentLoss`
    printing "0 empty edges" while reading nothing, one level up.
  * its historical-quote rule exempts the wrong numbers these documents quote
    ON PURPOSE, and NOTHING ELSE. A rule that drifts wide silently stops
    checking; a rule that drifts narrow fails on every correction note and gets
    disabled.

So each property is pinned by MUTATION rather than by inspection: break the
tool, watch the named test go red, revert. The two fixture tests below are
constructed rather than read off today's corpus deliberately -- a rule tested
only against data that happens to exercise it stops being tested the day the
data changes.
"""

import importlib.util
import inspect
import json
import os
import re
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(REPO_ROOT, "tools")


def _load(name):
    spec = importlib.util.spec_from_file_location(name,
                                                  os.path.join(TOOLS, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


C = _load("check_prose_counts")


# --------------------------------------------------------------------------
# THE VOCABULARY IS COMPLETE AND SELF-DESCRIBING
# --------------------------------------------------------------------------

def test_every_noun_has_a_derivation_and_patterns():
    assert C.NOUNS, "the vocabulary is empty -- the tool would locate nothing"
    for noun in C.NOUNS:
        assert callable(noun.derive), f"{noun.key} has no derivation"
        assert noun.patterns, f"{noun.key} has no patterns"
        assert noun.what, f"{noun.key} does not say what it counts"
        for pat in noun.patterns:
            assert pat.groups == 1, f"{noun.key}: {pat.pattern} must capture exactly one number"


def test_no_noun_is_silently_dropped_from_the_report():
    """Every located claim lands in exactly one bucket, and every noun whose
    derivation is unavailable is NAMED.

    THE MUTATION THIS CATCHES: filtering a noun out of `derive_all` or out of
    `adjudicate` so its claims vanish instead of being reported. Conservation
    is the only thing standing between "nothing to say about it" and "nothing
    was looked at"."""
    claims, docs_read, _lines, _bad = C.scan(C.documents())
    assert docs_read > 0
    live = [c for c in claims if c.live]
    hist = [c for c in claims if c.demoted]
    scoped = [c for c in claims if c.scoped and not c.demoted]
    assert len(live) + len(hist) + len(scoped) == len(claims)

    values, unavailable = C.derive_all(sorted({c.noun for c in claims}))
    assert set(values) | set(unavailable) == {c.noun for c in claims}, \
        "a noun with claims was neither derived nor reported as underivable"

    agree, disagree, _sup, undecidable = C.adjudicate(claims, values, unavailable)
    pairs = {(c.path, c.noun) for c in claims}
    adjudicated = {(p, n) for p, n, _d, _r in agree + disagree + undecidable}
    assert adjudicated == pairs, "a (document, noun) pair was dropped without a verdict"


def test_an_underivable_noun_is_named_not_dropped(monkeypatch, tmp_path):
    """CONSTRUCTED, because today's checkout can derive all thirteen.

    The mutation this pins -- `if noun in unavailable: continue` in
    `adjudicate`, i.e. drop the pair instead of reporting it -- is INVISIBLE on
    today's data: nothing is underivable here, so the branch never runs. A
    checker whose most dangerous branch is only reachable on a machine we do
    not test on is a checker with an untested exemption, which is how one
    stops checking. So the unavailable case is manufactured."""
    doc = tmp_path / "fixture.md"
    doc.write_text("DENOMINATOR: 7 NDI templates on origin/main\n", encoding="utf-8")

    def boom():
        raise C.Unavailable("NDI-matlab checkout not found")

    monkeypatch.setattr(C.BY_KEY["ndi_templates"], "derive", boom)
    claims, _d, _l, _b = C.scan([str(doc)])
    values, unavailable = C.derive_all(["ndi_templates"])
    assert values == {}
    assert "ndi_templates" in unavailable

    agree, disagree, _sup, undecidable = C.adjudicate(claims, values, unavailable)
    assert not agree and not disagree
    assert len(undecidable) == 1, "the pair was dropped instead of reported"

    lines = []
    C.render([str(doc)], claims, 1, 1, [], values, unavailable,
             agree, disagree, _sup, undecidable, out=lines.append)
    text = "\n".join(lines)
    assert "NOT DERIVABLE HERE" in text
    assert "ndi_templates" in text
    assert "claims whose noun is NOT DERIVABLE   : 1" in text


def test_an_underivable_noun_never_fails_the_gate(monkeypatch, tmp_path):
    """The other half: a gap in THIS checkout is not a defect in the prose.
    `--enforce` on a runner without the siblings must not go red for it."""
    doc = tmp_path / "fixture.md"
    doc.write_text("DENOMINATOR: 7 NDI templates on origin/main\n", encoding="utf-8")

    def boom():
        raise C.Unavailable("NDI-matlab checkout not found")

    monkeypatch.setattr(C.BY_KEY["ndi_templates"], "derive", boom)
    monkeypatch.setattr(C, "documents", lambda: [str(doc)])
    assert C.main(["--enforce"]) == 0


# --------------------------------------------------------------------------
# THE DERIVATIONS DO NOT READ THE PROSE
# --------------------------------------------------------------------------

def test_no_derivation_opens_a_markdown_file():
    """A checker that reads its expectation out of the document it is checking
    passes by construction. Nothing in the derivation half may mention `.md`,
    `CLAUDE` or the scan's own document list."""
    for noun in C.NOUNS:
        src = inspect.getsource(noun.derive)
        assert "CLAUDE" not in src, f"{noun.key}'s derivation names CLAUDE.md"
        for forbidden in (r"(?<![\w])documents\(\)", r"(?<![\w])scan\("):
            assert not re.search(forbidden, src), \
                f"{noun.key}'s derivation calls the scan -- it must read the tree"
        # `plan_documents` legitimately GLOBS `*.md` -- it counts the documents.
        # What no derivation may do is OPEN one and read what it says.
        if ".md" in src:
            assert "open(" not in src and "read_text" not in src, \
                f"{noun.key}'s derivation reads a markdown file's contents"


def test_derivations_match_an_independent_recomputation():
    """THE ANTI-TAUTOLOGY TEST, and the one the 'stub the derivation' mutation
    reddens. Each expected value is recomputed here by a DIFFERENT route --
    shell/glob/json rather than the tool's own walk -- so a derivation replaced
    by `return <whatever the prose says>` disagrees with something."""
    veta = os.path.join(REPO_ROOT, "schemas", "V_eta")

    files = subprocess.run(["find", veta, "-name", "*.json"],
                           capture_output=True, text=True, check=True)
    assert C.derive_veta_schema_files() == len(files.stdout.split())

    with open(os.path.join(REPO_ROOT, "schemas",
                           "V_eta_coverage_ledger.json")) as fh:
        assert C.derive_ledger_rows() == len(json.load(fh)["rows"])

    with open(os.path.join(REPO_ROOT, "schemas",
                           "V_eta_ndi_ground_truth.json")) as fh:
        assert C.derive_ndi_templates() == len(json.load(fh)["classes"])

    with open(os.path.join(veta, "stable", "binding_registry_meta.json")) as fh:
        reg = json.load(fh)
    assert C.derive_registry_rows() == (len(reg["subject_statement_bindings"])
                                        + len(reg["binding_examples"])
                                        + len(reg["relation_bindings"])
                                        + len(reg["entity_field_bindings"]))

    md = subprocess.run(["ls", os.path.join(REPO_ROOT, "schemas")],
                        capture_output=True, text=True, check=True)
    assert C.derive_plan_documents() == len(
        [n for n in md.stdout.split() if n.endswith(".md")])

    # `_DELETE_PHASE8` counted by reading the source's set literal directly.
    with open(os.path.join(TOOLS, "build_v_eta.py")) as fh:
        src = fh.read()
    start = src.index("_DELETE_PHASE8 = {")
    body = src[start:src.index("\n}", start)]
    names = {ln.strip().strip(",").strip('"\'')
             for ln in body.splitlines()[1:]
             if ln.strip().startswith(('"', "'"))}
    names = {n for part in names for n in part.replace('"', "").replace("'", "").split(", ")}
    assert C.derive_phase8_deleted() == len(names), sorted(names)


# --------------------------------------------------------------------------
# THE HISTORICAL-QUOTE RULE -- both directions, on constructed fixtures
# --------------------------------------------------------------------------

FIXTURE_HISTORY = """\
# a correction note in the house style

The registry is **{live} rows, not {old}** (the four illustrative
`binding_examples` were never counted).
"""

FIXTURE_LIVE_WRONG = """\
# an ordinary assertion that has gone stale

The registry carries **{wrong} rows**, so the catalogue is complete.
"""


def _adjudicate_text(tmp_path, text, noun_key):
    path = tmp_path / "fixture.md"
    path.write_text(text, encoding="utf-8")
    claims, _d, _l, _b = C.scan([str(path)])
    values, unavailable = C.derive_all([noun_key])
    return claims, C.adjudicate(claims, values, unavailable), values[noun_key]


def test_a_quoted_historical_number_is_not_flagged(tmp_path):
    """The house style -- both numbers in one breath -- must pass."""
    derived = C.derive_registry_rows()
    text = FIXTURE_HISTORY.format(live=derived, old=derived + 7)
    claims, (agree, disagree, _sup, undecidable), _ = _adjudicate_text(
        tmp_path, text, "registry_rows")

    assert not disagree, f"a correction note was flagged: {disagree}"
    assert not undecidable
    assert len(agree) == 1
    quoted = [c for c in claims if c.value == derived + 7]
    assert quoted, "the old half of the correction pair was not even located"
    assert all(c.demoted for c in quoted), \
        "the old half was located but not recognised as quoted history"


def test_a_live_wrong_number_is_flagged(tmp_path):
    """The same shape WITHOUT a correction connective must fail."""
    derived = C.derive_registry_rows()
    text = FIXTURE_LIVE_WRONG.format(wrong=derived + 7)
    _claims, (agree, disagree, _sup, _und), _ = _adjudicate_text(
        tmp_path, text, "registry_rows")
    assert not agree
    assert len(disagree) == 1, disagree
    assert disagree[0][2] == derived


def test_demotion_does_not_reach_across_a_clause(tmp_path):
    """THE MUTATION THIS PINS: widening the demotion window.

    An earlier draft searched the preceding 46 characters for a cue, and
    demoted the live `38` in "NOT `data_type` -- that is a CLASS with **38
    direct subclasses**" because the `NOT` forty-one characters upstream was
    about something else entirely. A widened rule silently exempts live claims,
    which is a checker that has stopped checking."""
    derived = C.derive_data_type_subclasses()
    text = (f"NOT `element_type` -- that is a CLASS with **{derived + 3} "
            "direct subclasses**\n")
    _claims, (_agree, disagree, _sup, _und), _ = _adjudicate_text(
        tmp_path, text, "data_type_subclasses")
    assert len(disagree) == 1, \
        "a cue in an unrelated clause demoted a live claim"


def test_a_document_that_only_quotes_history_is_undecidable_not_clean(tmp_path):
    """If the demotion rule were widened to exempt everything, every pair would
    land here -- reported and, under --enforce, failing. It must never read as
    agreement."""
    derived = C.derive_registry_rows()
    text = f"The registry was **{derived + 7} rows** back then.\n"
    _claims, (agree, disagree, _sup, undecidable), _ = _adjudicate_text(
        tmp_path, text, "registry_rows")
    assert not agree and not disagree
    assert len(undecidable) == 1


def test_a_scoped_count_is_exempt_and_reported(tmp_path):
    """`245 json files under schemas/V_eta read (examples/ excluded)` is a
    different count, not a stale one."""
    derived = C.derive_veta_schema_files()
    text = (f"DENOMINATOR: {derived - 2} json files under schemas/V_eta read "
            "(examples/ excluded)\n")
    claims, (agree, disagree, _sup, undecidable), _ = _adjudicate_text(
        tmp_path, text, "veta_schema_files")
    assert not agree and not disagree
    assert len(undecidable) == 1
    assert [c.scoped for c in claims] == [True]


# --------------------------------------------------------------------------
# BLOCK FLATTENING MUST NOT INVENT A CLAIM
# --------------------------------------------------------------------------

def test_tabular_lines_are_never_joined(tmp_path):
    """Joining these two produced the phrase `45 ledger rows` -- a claim nobody
    wrote, adjudicated against a real derivation, reported as a defect."""
    text = ("        distinct normalised class names across all six: 45\n"
            "        ledger rows: 102\n")
    path = tmp_path / "fixture.md"
    path.write_text(text, encoding="utf-8")
    claims, _d, _l, _b = C.scan([str(path)])
    assert claims == [], [(c.value, c.noun, c.text) for c in claims]


def test_wrapped_prose_is_joined(tmp_path):
    """The other direction: a claim that wraps must still be reachable. This is
    how `**1002**, not 915` -- whose subject ends on the previous line -- is
    seen at all."""
    text = ("the denominator moved (`git ls-tree -r origin/main | grep -c "
            "'\\.m$'` =\n**1002**, not 915, and coverage.py already records "
            "1,002), and no obvious\n")
    path = tmp_path / "fixture.md"
    path.write_text(text, encoding="utf-8")
    claims, _d, _l, _b = C.scan([str(path)])
    assert 1002 in [c.value for c in claims if c.noun == "ndi_m_files"]


# --------------------------------------------------------------------------
# A SCAN THAT FINDS NOTHING IS A FAILURE
# --------------------------------------------------------------------------

def test_zero_claims_exits_non_zero(tmp_path, monkeypatch):
    """THE MUTATION THIS PINS: narrowing the scan so it matches nothing.

    A checker that reads no documents prints the same clean zero as one that
    finds nothing wrong. This repository has had exactly that for two days."""
    empty = tmp_path / "empty.md"
    empty.write_text("nothing countable here\n", encoding="utf-8")
    monkeypatch.setattr(C, "documents", lambda: [str(empty)])
    assert C.main([]) == 1


def test_the_denominator_prints_first_and_unconditionally():
    res = subprocess.run([sys.executable,
                          os.path.join(TOOLS, "check_prose_counts.py")],
                         capture_output=True, text=True, cwd=REPO_ROOT, check=False)
    first = res.stdout.splitlines()[0]
    assert first.startswith("DENOMINATOR:"), first
    assert "document(s) globbed" in first and "numeric claim(s) located" in first


def test_enforce_fails_on_a_disagreement_and_report_only_does_not(tmp_path, monkeypatch):
    derived = C.derive_registry_rows()
    doc = tmp_path / "wrong.md"
    doc.write_text(f"the registry carries **{derived + 7} rows**\n",
                   encoding="utf-8")
    monkeypatch.setattr(C, "documents", lambda: [str(doc)])
    assert C.main([]) == 0
    assert C.main(["--enforce"]) == 1
