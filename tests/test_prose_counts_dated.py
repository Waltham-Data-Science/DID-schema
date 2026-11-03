"""Rule (3) of `tools/check_prose_counts.py`: DATED claims, a third state.

Decided by Jess Haley, 2026-11-03 [dated counts in OPEN_WORK]
(`did_v2_go_forward_class_audit.md`). A number governed by `at <YYYY-MM-DD>:`,
and every number in a `RE-DERIVED <YYYY-MM-DD>` block of
`docs/did_v2_OPEN_WORK.md`, is a dated measurement: not adjudicated, counted
and printed. A group of ONLY dated claims is not the all-history failure; a
group of only `was N` claims still is.

The fixtures are constructed, not read off today's corpus, so the rule stays
tested when the corpus changes.
"""

import importlib.util
import os
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


def _scan(tmp_path, text, name="fixture.md"):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    claims, _d, _l, _b = C.scan([str(path)])
    return str(path), claims


def _adjudicate(claims, noun_key):
    values, unavailable = C.derive_all([noun_key])
    return C.adjudicate(claims, values, unavailable)


def test_at_date_colon_is_dated(tmp_path):
    derived = C.derive_registry_rows()
    _p, claims = _scan(tmp_path,
                       f"at 2026-08-11: the registry carries **{derived + 7} rows**.\n")
    rows = [c for c in claims if c.noun == "registry_rows"]
    assert len(rows) == 1
    assert rows[0].dated and not rows[0].live and not rows[0].demoted


def test_at_date_governs_the_sentence_and_no_further(tmp_path):
    """`at <date>:` reaches every number in its sentence (a denominator line
    dates all its figures) and stops at a sentence break."""
    derived = C.derive_data_type_subclasses()
    text = (f"DENOMINATOR: at 2026-08-17: {derived + 1} direct subclasses on "
            f"origin/main, then {derived + 2} direct subclasses. "
            f"Today {derived + 3} direct subclasses.\n")
    _p, claims = _scan(tmp_path, text)
    by_value = {c.value: c for c in claims if c.noun == "data_type_subclasses"}
    assert by_value[derived + 1].dated
    assert by_value[derived + 2].dated
    assert by_value[derived + 3].live, "the dated cue reached across a sentence"


def test_a_bare_date_without_at_colon_is_not_dated(tmp_path):
    """Narrow, like rule (1): a date elsewhere in the sentence dates nothing."""
    derived = C.derive_registry_rows()
    _p, claims = _scan(tmp_path,
                       f"On 2026-08-11 the registry carries **{derived + 7} rows**.\n")
    rows = [c for c in claims if c.noun == "registry_rows"]
    assert rows and rows[0].live and not rows[0].dated


def test_a_re_derived_block_of_open_work_is_dated(tmp_path):
    derived = C.derive_registry_rows()
    text = (f"RE-DERIVED 2026-09-25 (registry): the registry carries\n"
            f"**{derived + 7} rows** (the registry was **{derived + 5} rows**).\n"
            "\n"
            f"The registry carries **{derived + 9} rows**.\n")
    _p, claims = _scan(tmp_path, text, name="did_v2_OPEN_WORK.md")
    rows = {c.value: c for c in claims if c.noun == "registry_rows"}
    assert rows[derived + 7].dated
    # Rule (3) wins over rule (1) inside the log.
    assert rows[derived + 5].dated and not rows[derived + 5].demoted
    # The next block is not part of the log.
    assert rows[derived + 9].live


def test_a_re_derived_block_elsewhere_is_not_dated(tmp_path):
    """The log is OPEN_WORK's; the same words in another document date nothing."""
    derived = C.derive_registry_rows()
    _p, claims = _scan(tmp_path,
                       f"RE-DERIVED 2026-09-25: the registry carries **{derived + 7} rows**.\n",
                       name="other.md")
    rows = [c for c in claims if c.noun == "registry_rows"]
    assert rows and rows[0].live


def test_a_group_of_only_dated_claims_passes(tmp_path, monkeypatch):
    derived = C.derive_registry_rows()
    path, claims = _scan(tmp_path,
                         f"at 2026-08-11: the registry carries **{derived + 7} rows**.\n")
    agree, disagree, _sup, undecidable = _adjudicate(claims, "registry_rows")
    assert not agree and not disagree and not undecidable
    assert [(p, n) for p, n, _r in C.dated_only_groups(claims)] == \
        [(path, "registry_rows")]
    monkeypatch.setattr(C, "documents", lambda: [path])
    assert C.main(["--enforce"]) == 0


def test_a_group_of_only_was_claims_still_fails(tmp_path, monkeypatch):
    derived = C.derive_registry_rows()
    path, claims = _scan(tmp_path,
                         f"The registry was **{derived + 7} rows** back then.\n")
    agree, disagree, _sup, undecidable = _adjudicate(claims, "registry_rows")
    assert not agree and not disagree
    assert len(undecidable) == 1
    assert not C.dated_only_groups(claims)
    monkeypatch.setattr(C, "documents", lambda: [path])
    assert C.main(["--enforce"]) == 1


def test_dated_plus_history_with_no_live_claim_still_fails(tmp_path, monkeypatch):
    """A dated claim does not excuse a group whose other claims are all
    history: the verdict is reached on the non-dated claims as before."""
    derived = C.derive_registry_rows()
    text = (f"at 2026-08-11: the registry carries **{derived + 7} rows**.\n\n"
            f"The registry was **{derived + 5} rows** back then.\n")
    path, claims = _scan(tmp_path, text)
    _agree, _dis, _sup, undecidable = _adjudicate(claims, "registry_rows")
    assert len(undecidable) == 1
    monkeypatch.setattr(C, "documents", lambda: [path])
    assert C.main(["--enforce"]) == 1


def test_a_live_wrong_claim_beside_a_dated_one_still_disagrees(tmp_path):
    derived = C.derive_registry_rows()
    text = (f"at 2026-08-11: the registry carries **{derived} rows**.\n\n"
            f"The registry carries **{derived + 7} rows**.\n")
    _p, claims = _scan(tmp_path, text)
    agree, disagree, _sup, _und = _adjudicate(claims, "registry_rows")
    assert not agree, "a dated claim satisfied the check"
    assert len(disagree) == 1


def test_dated_claims_are_counted_in_the_output(tmp_path, monkeypatch, capsys):
    derived = C.derive_registry_rows()
    text = (f"at 2026-08-11: the registry carries **{derived + 7} rows**.\n\n"
            f"The registry carries **{derived} rows**.\n")
    path, _claims = _scan(tmp_path, text)
    monkeypatch.setattr(C, "documents", lambda: [path])
    assert C.main(["--enforce"]) == 0
    out = capsys.readouterr().out
    lines = out.splitlines()
    assert lines[0].startswith("DENOMINATOR:") and "2 numeric claim(s)" in lines[0]
    dated = [ln for ln in lines if ln.strip().startswith("claims DATED (exempt)")]
    assert dated and dated[0].rstrip().endswith(": 1"), dated
    assert any(ln.strip().startswith("claims ASSERTED (checked)")
               and ln.rstrip().endswith(": 1") for ln in lines)
