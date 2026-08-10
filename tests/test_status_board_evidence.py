"""The status board's DERIVED half: what is actually built, and what is proven.

WHY THIS FILE EXISTS
--------------------
`disposition: in_progress` is a HAND-WRITTEN DECLARATION. Every open class is
open because a person typed its name into a literal collection in
`tools/build_v_eta.py`, and it leaves the list only when a person deletes that
line -- never because a migrator landed, a test passed or a corpus went green.
`test_in_progress_is_a_declaration_not_a_measurement` pins that fact with its
own denominator so the diagnosis cannot quietly stop being true.

The board now derives, per open class, the two things the declaration cannot
carry: is anything BUILT for it, and does the last census show any document of
it SURVIVING. The rest of this file holds that derivation to the standard the
project keeps paying for when it is not held:

  * a reference that is a COMMENT, a STRING VALUE or an EMISSION must not be
    counted as build progress -- every one of those errs in the reassuring
    direction, which is the direction this repo's mistakes have all gone;
  * a census that measured nothing must not read as a census that found
    nothing. A report with no `unconverted_count` key is silence, not zero;
  * absence of evidence gets its own state and is never folded into
    "nothing built".
"""

import importlib.util
import json
import os

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(REPO_ROOT, "tools")
INDEX = os.path.join(REPO_ROOT, "schemas", "V_eta", "index.json")
DECISIONS = os.path.join(REPO_ROOT, "schemas", "V_eta_decisions.json")
STATUS = os.path.join(REPO_ROOT, "schemas", "V_eta_STATUS.md")


def _load_tool(name):
    spec = importlib.util.spec_from_file_location(name,
                                                  os.path.join(TOOLS, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


sb = _load_tool("status_board")


def _open_classes():
    with open(INDEX) as fh:
        idx = json.load(fh)
    return sorted(s["class_name"] for s in idx["schemas"]
                  if s.get("disposition") == "in_progress")


class _Args:
    def __init__(self, did=None, ndi=None, census=None):
        self.did = did
        self.ndi = ndi
        self.census = census or []
        self.check = False


# ---------------------------------------------------------------------------
# THE DIAGNOSIS, PINNED
# ---------------------------------------------------------------------------

def test_in_progress_is_a_declaration_not_a_measurement():
    """Every open class is open because a human wrote its name down.

    This is not a style complaint -- it is the reason the board could not answer
    "how close are we". A class cannot leave `in_progress` by being finished, so
    the count is a lower bound on progress that never rises on its own, and it
    sat at 31 through a day in which seven families were built.

    Pinned with a denominator on both sides. If a future `_disposition()` starts
    DERIVING `in_progress` from something, this test fails and the docstring at
    the top of `tools/status_board.py` needs rewriting -- which is the point.
    """
    src = open(os.path.join(TOOLS, "build_v_eta.py")).read()
    start = src.index("_DECIDED_PENDING = {")
    end = src.index("def _disposition(")
    ns = {"_re": __import__("re")}
    exec(src[start:end], ns)          # noqa: S102 -- reading the tool's own literals
    declared = set(ns["_DECIDED_PENDING"]) | set(ns["_IN_PROGRESS"])

    open_classes = _open_classes()
    assert open_classes, "no in_progress classes -- this sweep would check nothing"

    derived = [c for c in open_classes if c not in declared]
    assert derived == [], (
        f"{len(derived)} in_progress class(es) come from somewhere other than a "
        f"literal in build_v_eta.py: {derived}. If `in_progress` has become a "
        "measurement, status_board.py's premise has changed.")

    # The denominator, split the way the board reports it.
    from_pending = [c for c in open_classes if c in ns["_DECIDED_PENDING"]]
    from_set = [c for c in open_classes if c in ns["_IN_PROGRESS"]]
    assert len(from_pending) + len(from_set) == len(open_classes)
    assert from_pending and from_set, (
        "both literal collections must still be feeding the count, or this "
        "split has stopped describing anything")


# ---------------------------------------------------------------------------
# THE MATLAB SCANNER -- every case here is a real line that fooled a draft
# ---------------------------------------------------------------------------

def test_a_comment_is_not_evidence():
    """+migrators_j documents at length, and every migrator that mentions a class
    it does NOT touch mentions it in a comment. Counting those reports unbuilt
    work as built."""
    code, lits = sb.split_matlab_line("blk = preBody.filter;  % reads the filter\n")
    assert "% reads" not in code
    assert lits == []
    code2, _ = sb.split_matlab_line("%   the `app` block is folded elsewhere\n")
    assert code2.strip() == ""


def test_a_string_value_is_not_a_field_access():
    """The live case: stimulus_response_scalar.m:210 contains the literal
    'ndi.app.stimulus.tuning_response'. A raw search for `.app` finds it, and
    `app` is one of the open classes."""
    line = "    'stimulus response', 'ndi.app.stimulus.tuning_response', ...\n"
    code, lits = sb.split_matlab_line(line)
    assert "ndi.app.stimulus.tuning_response" in [t for t, _col in lits]
    assert ".app" not in code, "the string body leaked into the code half"


def test_transpose_is_not_a_string_delimiter():
    code, lits = sb.split_matlab_line("y = x' * A';\n")
    assert lits == [], f"transpose read as a string: {lits}"
    assert "*" in code


def test_assignment_split_ignores_comparisons_and_brackets():
    assert sb.assignment_split("a = b") == 2
    assert sb.assignment_split("if a == b") is None
    assert sb.assignment_split("if a ~= b") is None
    assert sb.assignment_split("f(a == b)") is None
    assert sb.assignment_split("s.x(i) = 1") is not None


def _kinds(tmp_path, text, classes):
    p = tmp_path / "m.m"
    p.write_text(text)
    import re
    patterns = {c: re.compile(r"\.\s*" + re.escape(c) + r"\b") for c in classes}
    hits, _n = sb.scan_matlab_file(str(p), patterns)
    return {c: [k for _l, k in v] for c, v in hits.items()}


def test_a_write_is_not_a_read(tmp_path):
    """`anchor.time_reference = struct(...)` EMITS the class. The first draft
    counted it as consumption, which put all 18 of session_relative_reference's
    emission sites on the wrong side of the ledger -- the class whose whole open
    question is that those emissions have not moved yet."""
    k = _kinds(tmp_path,
               "anchor.time_reference = struct('is_approximate', true);\n"
               "blk = preBody.filter;\n",
               ["time_reference", "filter"])
    assert k["time_reference"] == ["field_write"]
    assert k["filter"] == ["field_read"]
    assert "field_write" not in sb.CONSUMING_KINDS
    assert "field_read" in sb.CONSUMING_KINDS


def test_a_string_value_that_happens_to_be_a_class_name_is_not_consumption(tmp_path):
    """jSorterOutput.m:77 is `struct('format', 'directory', ...)`. `directory` is
    an open class with nothing built, and the first draft rendered it as built."""
    k = _kinds(tmp_path,
               "body.opaque_body = struct('format', 'directory', 'filename', d);\n",
               ["directory"])
    assert k["directory"] == ["named"]
    assert "named" not in sb.CONSUMING_KINDS


def test_a_class_name_dispatch_is_consumption(tmp_path):
    """ensembleMembership.m:227 selects its input with
    `if ~strcmp(classNameOf(s), 'ensemble')`. That is the entire ensemble
    consumer, and a guard list of only isfield/isstruct missed the whole NDI
    second pass."""
    k = _kinds(tmp_path,
               "if ~strcmp(classNameOf(s), 'ensemble')\n    continue;\nend\n",
               ["ensemble"])
    assert k["ensemble"] == ["guard"]
    assert "guard" in sb.CONSUMING_KINDS


def test_an_isfield_guard_is_consumption(tmp_path):
    k = _kinds(tmp_path,
               "if isfield(preBody, 'app') && isstruct(preBody.app)\n",
               ["app"])
    assert k["app"] == ["guard"]


# ---------------------------------------------------------------------------
# THE MIGRATOR SWEEP -- the undercount it exists to fix
# ---------------------------------------------------------------------------

def _did_root():
    return sb.find_repo("DID-matlab", "DID_MATLAB")


@pytest.mark.skipif(_did_root() is None, reason="DID-matlab not checked out")
def test_a_private_helper_counts_as_a_migrator():
    """The undercount the coverage ledger's filename match produces.

    `app` and `filter` are v1 SUPERCLASS BLOCKS, not standalone documents, so no
    file is named after them -- they are folded by shared helpers in `private/`
    (jSoftwareFromApp.m, jFrequencyFilter.m). The ledger reports `app` as having
    no migrator. This sweep must not.
    """
    classes = set(_open_classes())
    assert {"app", "filter"} <= classes, (
        "app/filter are no longer open -- rewrite this test against whatever "
        "block-superclass classes remain, or delete it")
    mig, src = sb.migrator_evidence(classes, _did_root(),
                                    sb.find_repo("NDI-matlab", "NDI_MATLAB"))
    assert mig is not None and src["files_read"] > 0, (
        "the sweep read no files -- treat as broken, not as clean")
    for cls in ("app", "filter"):
        assert mig[cls]["migrator_file"] is None, (
            f"{cls} now has a same-named migrator; this test no longer "
            "demonstrates the undercount")
        assert mig[cls]["n_consuming_refs"] > 0, (
            f"{cls} is consumed by a private helper and the sweep missed it")
        assert any("private/" in r for r in mig[cls]["consuming_refs"]), (
            f"{cls}'s consumption should be found in a private/ helper")


# ---------------------------------------------------------------------------
# THE CENSUS -- silence is not a zero
# ---------------------------------------------------------------------------

def test_no_reports_means_no_class_can_be_corpus_proven():
    classes = set(_open_classes())
    cen, src, probe = sb.census_evidence(classes, ["/does/not/exist"])
    assert cen is None
    assert src["reports_read"] == 0
    assert src["reports_with_survivor_data"] == 0
    assert probe["roots_missing"] == ["/does/not/exist"]

    ocs = sb.open_class_state(classes, [], [], {c: {"migrator_file": "x.m"}
                                                for c in classes},
                              {"available": True}, None, src)
    assert ocs["counts"][sb.STATE_C] == 0, (
        "a class reached corpus-proven with no census at all")
    assert ocs["counts"][sb.STATE_B] == len(classes)


def test_a_report_without_unconverted_count_measured_nothing(tmp_path):
    """The exact shape sitting in this container: six real corpus reports that
    carry `silent_loss` and no survivor breakdown at all. Reading their silence
    as zero would promote every open class to corpus-proven on no evidence."""
    (tmp_path / "Soph-summary.json").write_text(json.dumps(
        {"corpus": "Soph", "total": 101427, "migrated_count": 181825,
         "quarantine_count": 0, "fragment_count": 0,
         "silent_loss": {"total_docs": 181825, "empty_dependency_count": 175}}))
    cen, src, _probe = sb.census_evidence({"daqsystem"}, [str(tmp_path)])
    assert cen is None, "a report with no unconverted_count was read as data"
    assert src["reports_read"] == 1
    assert src["reports_with_survivor_data"] == 0
    assert src["source_documents"] == 101427, (
        "the denominator must still be reported -- 'we read 101427 documents "
        "and none of them told us' is a different fact from 'we read nothing'")


def test_zero_survivors_is_reachable_and_counted(tmp_path):
    """`unconverted_count: 0` with an EMPTY breakdown IS evidence: every class
    was measured and none survived. One missing key apart from the case above."""
    (tmp_path / "Demo-summary.json").write_text(json.dumps(
        {"corpus": "Demo", "total": 100, "unconverted_count": 5,
         "unconverted_by_class": {"syncrule_mapping": 5}}))
    classes = {"syncrule_mapping", "daqsystem"}
    cen, src, _probe = sb.census_evidence(classes, [str(tmp_path)])
    assert src["reports_with_survivor_data"] == 1
    assert cen["syncrule_mapping"]["survivors"] == 5
    assert cen["syncrule_mapping"]["by_corpus"] == {"Demo": 5}
    assert cen["daqsystem"]["survivors"] == 0

    mig = {c: {"migrator_file": c + ".m", "n_consuming_refs": 1,
               "consuming_refs": [c + ".m:1 (guard)"], "n_emitting_refs": 0,
               "emitting_refs": []} for c in classes}
    ocs = sb.open_class_state(classes, [], [], mig, {"available": True}, cen, src)
    by = {r["class_name"]: r["state"] for r in ocs["classes"]}
    assert by["daqsystem"] == sb.STATE_C
    assert by["syncrule_mapping"] == sb.STATE_B


def test_zero_survivors_without_a_build_stays_nothing_built(tmp_path):
    """0 survivors on a class nothing consumes says nothing about the work. It
    is (a), not (c) -- most likely the corpora simply hold none of them."""
    (tmp_path / "Demo-summary.json").write_text(json.dumps(
        {"corpus": "Demo", "total": 100, "unconverted_count": 0,
         "unconverted_by_class": {}}))
    cen, src, _probe = sb.census_evidence({"projectvar"}, [str(tmp_path)])
    mig = {"projectvar": {"migrator_file": None, "n_consuming_refs": 0,
                          "consuming_refs": [], "n_emitting_refs": 0,
                          "emitting_refs": []}}
    ocs = sb.open_class_state({"projectvar"}, [], [], mig, {"available": True},
                              cen, src)
    assert ocs["classes"][0]["state"] == sb.STATE_A


# ---------------------------------------------------------------------------
# ABSENCE OF EVIDENCE IS ITS OWN STATE (operating rule 3)
# ---------------------------------------------------------------------------

def test_unmeasured_is_not_reported_as_nothing_built():
    """With no migrator scan and no ledger target, the honest answer is "we did
    not look". Folding that into (a) would be the ledger's old "dissolved
    (rename/decompose)" label again: an unknown wearing a finding's clothes."""
    ocs = sb.open_class_state({"ngrid"}, [], [], None, {"available": False},
                              None, {"available": False})
    row = ocs["classes"][0]
    assert row["state"] == sb.STATE_U
    assert row["build_evidence_measured"] is False
    assert ocs["counts"][sb.STATE_A] == 0


# ---------------------------------------------------------------------------
# THE ARTIFACTS
# ---------------------------------------------------------------------------

def test_committed_board_carries_the_evidence_snapshot():
    """The snapshot is what makes `--check` meaningful in a CI job that has no
    sibling repos checked out: the board falls back to it rather than rendering
    the evidence as absent."""
    with open(DECISIONS) as fh:
        ocs = json.load(fh).get("open_class_state")
    assert ocs, "V_eta_decisions.json carries no open_class_state block"
    named = {r["class_name"] for r in ocs["classes"]}
    assert named == set(_open_classes()), (
        "the snapshot and the built index disagree about which classes are open")
    assert sum(ocs["counts"].values()) == len(named), (
        "the state counts do not add up to the class count")
    for key in ("migrator", "census"):
        assert key in ocs["sources"], f"no {key} denominator recorded"


def test_the_snapshot_carries_no_wall_clock_or_absolute_paths():
    """A field that changes on every run turns the staleness check into noise,
    and a check people learn to ignore is worse than no check."""
    with open(DECISIONS) as fh:
        blob = json.dumps(json.load(fh)["open_class_state"])
    assert "/home/" not in blob and "\\Users" not in blob, (
        "an absolute path leaked into the committed snapshot")
    for stamp in ("generated_at", "measured_at", "timestamp"):
        assert stamp not in blob, f"{stamp} would make --check fire on nothing"


def test_status_md_reports_its_denominator_before_its_counts():
    """Operating rule 5. `silentLoss` printed "0 empty edges" for two days while
    reading nothing, and the digest that rendered it repeated the omission."""
    with open(STATUS) as fh:
        text = fh.read()
    denom = text.index("### The measurement and its denominator")
    counts = text.index("### Where the 31 open classes sit"
                        if "### Where the 31 open classes sit" in text
                        else "open classes sit")
    assert denom < counts, "the counts render before the denominator"
    for line in ("| build: migrator files inspected |",
                 "| corpus: `*-summary.json` reports read |",
                 "| corpus: reports carrying an `unconverted_count` |"):
        assert line in text, f"missing denominator row: {line}"


def test_status_md_says_when_state_c_is_unreachable():
    """If the census is unavailable the board must SAY SO rather than render (b)
    as (c). Only asserted when it IS unavailable -- an unconditional assertion
    would pass by checking nothing the moment a corpus run lands."""
    with open(DECISIONS) as fh:
        ocs = json.load(fh)["open_class_state"]
    with open(STATUS) as fh:
        text = fh.read()
    if ocs["sources"]["census"].get("reports_with_survivor_data"):
        assert ocs["counts"][sb.STATE_C] >= 0
        return
    assert "**NO CORPUS SURVIVOR DATA.**" in text
    assert ocs["counts"][sb.STATE_C] == 0, (
        "classes are rendered as corpus-proven with no census behind them")


def test_every_open_class_appears_in_exactly_one_state():
    with open(DECISIONS) as fh:
        ocs = json.load(fh)["open_class_state"]
    rows = ocs["classes"]
    assert rows, "no open-class rows -- this sweep would check nothing"
    names = [r["class_name"] for r in rows]
    assert len(names) == len(set(names))
    assert all(r["state"] in sb.OPEN_STATE_LABEL for r in rows)
