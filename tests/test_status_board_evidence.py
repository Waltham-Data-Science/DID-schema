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
from pathlib import Path

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
    src = Path(os.path.join(TOOLS, "build_v_eta.py")).read_text()
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
# MINTING -- the OTHER half of "is anything built", added 2026-08-10
#
# Every kind above answers "does something CONSUME this v1 block". None of them
# can see a V_eta TARGET that a migrator BUILDS, because no file is named after
# the target of a rename -- and that is how `control_designation` rendered as
# "decided, nothing built" while control_stimulus_ids.m:111 was minting it.
# ---------------------------------------------------------------------------

def test_the_emission_patterns_are_coverage_pys_own():
    """Reuse, asserted rather than intended.

    `tools/coverage.py` already extracts every `'class_name', '<X>'` a V_eta
    migrator writes, for its emitted-class guardrail. A second regex here would
    be a second thing to keep in step with the migrators, and the two would
    disagree silently -- the `dataseries_channel_map` failure, where two
    hand-maintained records contradicted each other and neither won.
    """
    cov = _load_tool("coverage")
    assert [p.pattern for p in sb.CLASS_EMIT] == \
           [p.pattern for p in cov._CLASS_EMIT], (
        "status_board has grown its own copy of coverage.py's class_name "
        "patterns; the two will drift")


def test_a_minted_document_class_is_build_evidence(tmp_path):
    """control_stimulus_ids.m:111, reduced. The v1 source is
    `control_stimulus_ids`; the V_eta target is `control_designation`; no file
    is named after it and nothing reads a `preBody.control_designation`."""
    k = _kinds(tmp_path,
               "v2Body.document_class = struct('class_name', "
               "'control_designation', 'class_version', '1.0.0');\n",
               ["control_designation"])
    assert k["control_designation"] == [sb.EMITTED_CLASS_KIND]
    assert sb.EMITTED_CLASS_KIND not in sb.CONSUMING_KINDS, (
        "a mint is not a consumption; it is a separate fact about a target")


def test_a_superclass_entry_is_not_a_mint(tmp_path):
    """The precision coverage.py's raw sweep does not have, and needs not have.

    A `document_class` struct carries the document's OWN class_name plus a
    `superclasses` array of more class_names. `stimulusBathToBath.m` spells one
    across eight physical lines, so the split is by position inside the JOINED
    statement -- a per-line rule reads the superclass line as a document class,
    and `time_reference` and `epochid` (both open classes) are minted nowhere
    except as somebody else's ancestors.
    """
    text = ("timeRefBody.document_class = struct( ...\n"
            "    'class_name', 'epoch_bounded_reference', 'class_version', '1.0.0', ...\n"
            "    'superclasses', [ ...\n"
            "        struct('class_name', 'time_reference', 'class_version', '1.0.0'), ...\n"
            "        struct('class_name', 'epochid',        'class_version', '1.0.0')]);\n")
    minted = {c for c, _l in sb.emitted_document_classes(text.splitlines(True))}
    assert minted == {"epoch_bounded_reference"}, (
        f"superclass entries counted as minted document classes: {minted}")


def test_a_commented_out_emission_is_not_a_mint():
    """+migrators_j quotes NDI templates and its own prior shapes at length in
    comments. Counting one reports unbuilt work as built."""
    text = ("% v2Body.document_class = struct('class_name', 'ngrid');\n"
            "%{\n"
            "b.document_class = struct('class_name', 'projectvar');\n"
            "%}\n"
            "real.document_class = struct('class_name', 'directory');\n")
    minted = {c for c, _l in sb.emitted_document_classes(text.splitlines(True))}
    assert minted == {"directory"}, f"a commented emission was counted: {minted}"


def test_a_mint_is_reported_at_the_line_a_human_will_find_it_on():
    text = ("x = 1;\n"
            "body.document_class = struct( ...\n"
            "    'class_name', 'control_designation', 'class_version', '1');\n")
    assert sb.emitted_document_classes(text.splitlines(True)) == \
        {("control_designation", 3)}


def test_a_mint_of_a_class_the_decision_retires_is_not_progress():
    """The inversion this scan already recorded once, arriving through a new door.

    `session_relative_reference`'s whole open question is its COLLAPSE into
    `relative_reference` (signed, V_eta_time_reference_model_plan.md:468). Three
    migrators still mint the old class. That is the work outstanding, not
    evidence of it being done -- so a mint must not move it to (b).
    """
    cls = "session_relative_reference"
    assert cls in sb.RETIRED_BY_ITS_OWN_DECISION
    mig = {cls: {"migrator_file": None, "n_consuming_refs": 0,
                 "consuming_refs": [], "n_emitted_class_refs": 3,
                 "emitted_class_refs": [], "n_emitting_refs": 0,
                 "emitting_refs": []}}
    ocs = sb.open_class_state({cls}, [], [], mig, {"available": True},
                              None, {"available": False})
    row = ocs["classes"][0]
    assert row["state"] == sb.STATE_A, (
        "minting a class the signed decision retires was read as build progress")
    assert row["emission_discounted"], "the discount must be stated, not silent"
    assert row["n_emitted_class_refs"] == 3, (
        "the discounted mint count must still be REPORTED -- a suppressed "
        "signal that leaves no trace is how a number stops being checkable")


def test_a_mint_of_a_kept_class_is_progress():
    """The other side of the same rule, so the discount cannot quietly become
    universal and take the whole signal back out again."""
    cls = "control_designation"
    assert cls not in sb.RETIRED_BY_ITS_OWN_DECISION
    mig = {cls: {"migrator_file": None, "n_consuming_refs": 0,
                 "consuming_refs": [], "n_emitted_class_refs": 1,
                 "emitted_class_refs": [], "n_emitting_refs": 0,
                 "emitting_refs": []}}
    ocs = sb.open_class_state({cls}, [], [], mig, {"available": True},
                              None, {"available": False})
    assert ocs["classes"][0]["state"] == sb.STATE_B


def test_every_discounted_class_names_a_replacement_that_exists():
    """`RETIRED_BY_ITS_OWN_DECISION` SUPPRESSES build credit, so a typo or a
    since-renamed replacement pins its class at "nothing built" forever and in
    the direction this board exists to stop. `build()` exits non-zero on this;
    the test says so without needing a subprocess."""
    with open(INDEX) as fh:
        built = {s["class_name"] for s in json.load(fh)["schemas"]}
    bad = {c: t for c, t in sb.RETIRED_BY_ITS_OWN_DECISION.items()
           if t not in built}
    assert bad == {}, f"replacement class(es) absent from the built index: {bad}"

    claimed = {m for f in sb.FAMILIES for m in f[1]}
    orphan = sorted(set(sb.RETIRED_BY_ITS_OWN_DECISION) - claimed)
    assert orphan == [], (
        f"{orphan} are discounted but claimed by no decision family, so the "
        "sign-off the discount is transcribed from cannot be located")


def test_the_denominator_of_the_mint_sweep_is_recorded():
    """Operating rule 5, for the new half of the instrument."""
    with open(DECISIONS) as fh:
        ocs = json.load(fh).get("open_class_state") or {}
    msrc = ocs["sources"]["migrator"]
    if not msrc.get("available"):
        pytest.skip("migrator evidence was reused from the snapshot")
    assert "classes_emitted_as_document_class" in msrc, (
        "the mint sweep reports no denominator")
    assert sb.EMITTED_CLASS_KIND in msrc.get("ref_kinds", [])
    rows = ocs["classes"]
    counted = sum(1 for r in rows if r.get("n_emitted_class_refs"))
    assert counted == msrc["classes_emitted_as_document_class"], (
        "the per-class mint rows and the summary denominator disagree")


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


@pytest.mark.skipif(_did_root() is None, reason="DID-matlab not checked out")
def test_control_designation_is_found_by_minting_and_by_nothing_else():
    """THE ROW THAT PROVED THE UNDERCOUNT, held against the real repo.

    `control_designation` is the V_eta target of the v1 class
    `control_stimulus_ids`. Nothing is named after it, nothing consumes it, and
    the ledger offers no decided target -- so before minting was visible the
    board rendered it "(a) decided, nothing built" while
    `migrators_j/control_stimulus_ids.m:111` was building it.

    Asserted as an AND: if a same-named migrator or a consuming reference ever
    appears, this class stops demonstrating the undercount and the test should
    be re-pointed rather than relaxed.
    """
    classes = set(_open_classes())
    if "control_designation" not in classes:
        pytest.skip("control_designation is no longer an open class")
    mig, src = sb.migrator_evidence(classes, _did_root(),
                                    sb.find_repo("NDI-matlab", "NDI_MATLAB"))
    assert mig is not None and src["files_read"] > 0, (
        "the sweep read no files -- treat as broken, not as clean")
    row = mig["control_designation"]
    assert row["migrator_file"] is None, (
        "a migrator is now NAMED control_designation; this row no longer "
        "demonstrates the filename undercount")
    assert row["n_consuming_refs"] == 0, (
        "something now consumes control_designation; re-point this test")
    assert row["n_emitted_class_refs"] >= 1, (
        "control_designation is minted by control_stimulus_ids.m and the "
        "sweep missed it -- the undercount is back")
    assert any("control_stimulus_ids.m" in r
               for r in row["emitted_class_refs"]), row["emitted_class_refs"]


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


# ---------------------------------------------------------------------------
# THE MINT IDIOMS -- fixtures CUT FROM THE REAL MIGRATORS, not written here
# ---------------------------------------------------------------------------
#
# WHY THESE FIXTURES ARE EXTRACTED AND NOT TYPED. This repo's standing lesson is
# that A TEST WRITTEN FROM THE SAME PREMISE AS THE CODE CANNOT CATCH THE CODE:
# three tests asserted the `epochid` bug and had to be inverted, and the
# `silentLoss` counter shipped measuring nothing with no tests at all. The
# detector these tests cover missed six of nine `session_relative_reference`
# mints for exactly that reason -- its author's model of a mint was
# `struct('class_name', ...)`, so a hand-typed fixture would have been that
# shape too and would have passed while the migrators minted through a helper.
#
# So `_cut_statement` and `_cut_function` lift the bytes OUT OF THE MIGRATOR
# FILE. If a migrator's shape changes, the fixture changes with it; if a
# migrator stops using an idiom, the extractor finds nothing and the test fails
# loudly rather than checking a shape nobody writes any more. Neither extractor
# calls the detector -- they are plain line scans -- so the fixture cannot be
# built by the machinery under test.

def _ndi_root():
    return sb.find_repo("NDI-matlab", "NDI_MATLAB")


def _mig(rel):
    root = _did_root()
    return None if root is None else os.path.join(
        root, "src/did/+did2/+convert/+migrators_j", rel)


def _cut_statement(path, needle):
    """The physical lines of the first MATLAB statement containing `needle`.

    Continuations are followed by looking for a trailing `...`, which is a plain
    line scan and shares nothing with `logical_statements`.
    """
    with open(path, errors="replace") as fh:
        lines = fh.readlines()
    for i, line in enumerate(lines):
        if needle not in line or line.lstrip().startswith("%"):
            continue
        out = [line]
        j = i
        while lines[j].rstrip().endswith("..."):
            j += 1
            out.append(lines[j])
        return "".join(out), i + 1
    return None, None


def _cut_function(path, name):
    """The whole text of local function `name`, from its `function` line to the
    next one (MATLAB subfunctions do not nest)."""
    with open(path, errors="replace") as fh:
        lines = fh.readlines()
    start = None
    for i, line in enumerate(lines):
        s = line.lstrip()
        if not s.startswith("function"):
            continue
        if start is None and re.search(rf"\b{re.escape(name)}\s*\(", line):
            start = i
        elif start is not None:
            return "".join(lines[start:i])
    return "".join(lines[start:]) if start is not None else None


# E402: this import sits beside the block it serves rather than at the top,
# so the reader meets it where it is used. Deliberate, not an oversight.
import re  # noqa: E402

_IDIOM_SOURCES = [
    # idiom, file, the needle that finds the mint statement, helper to carry
    ("1 struct literal", "private/jSessionAnchor.m",
     "'class_name', 'session_relative_reference'", None),
    ("2 local class-block helper", "fitcurve.m",
     "classBlock('session_relative_reference'", "classBlock"),
    ("2 local class-block helper, 3-arg", "pyraview.m",
     "classBlock('session_relative_reference'", "classBlock"),
    ("3 class_name field write", "element_epoch.m",
     "document_class.class_name = 'acquisition_epoch'", None),
]


@pytest.mark.skipif(_did_root() is None, reason="DID-matlab not checked out")
@pytest.mark.parametrize("idiom,rel,needle,helper", _IDIOM_SOURCES,
                         ids=[s[0] for s in _IDIOM_SOURCES])
def test_every_mint_idiom_in_the_real_migrators_is_detected(
        tmp_path, idiom, rel, needle, helper):
    """One fixture per idiom, cut from the migrator that uses it.

    IDIOM 2 IS THE ONE THAT WAS MISSING, and it is not exotic: six migrators
    mint `session_relative_reference` through a local `classBlock`, which is
    twice as many sites as the idiom the detector could see.
    """
    path = _mig(rel)
    stmt, lineno = _cut_statement(path, needle)
    assert stmt, (f"{rel} no longer contains {needle!r} -- this fixture has stopped "
                  "describing the real migrator, so re-point it rather than "
                  "relaxing it")
    text = stmt
    if helper:
        fn = _cut_function(path, helper)
        assert fn, f"{rel} no longer defines {helper}()"
        text = stmt + "\n" + fn

    p = tmp_path / "fixture.m"
    p.write_text(text)
    with open(str(p)) as fh:
        minted = {c for c, _l in sb.emitted_document_classes(fh.readlines())}

    # The class is the LAST quoted literal in the needle -- `'class_name',
    # 'session_relative_reference'` names the field first.
    quoted = re.findall(r"'([a-z_][a-z_0-9]*)'", needle)
    want = quoted[-1] if quoted else None
    assert want and want != "class_name", (
        f"could not read the expected class out of {needle!r}")
    assert want in minted, (
        f'idiom {idiom}, cut verbatim from {rel}:{lineno}, was NOT recognised as a mint. Detected: {sorted(minted)}. This is the undercount coming back: the site is filed as a bare mention and the class renders with less outstanding work than it has.')


@pytest.mark.skipif(_did_root() is None, reason="DID-matlab not checked out")
def test_a_class_block_helper_argument_is_not_mistaken_for_a_mint(tmp_path):
    """`classBlock('session_relative_reference', {'time_reference'})` names TWO
    classes and mints ONE. `time_reference` is itself an open class, and
    counting a superclass as a mint would move it toward "built" on somebody
    else's ancestry -- the same error the statement-position rule already
    prevents for the struct idiom."""
    path = _mig("fitcurve.m")
    stmt, _ = _cut_statement(path, "classBlock('session_relative_reference'")
    fn = _cut_function(path, "classBlock")
    assert stmt and fn
    p = tmp_path / "fixture.m"
    p.write_text(stmt + "\n" + fn)
    with open(str(p)) as fh:
        minted = {c for c, _l in sb.emitted_document_classes(fh.readlines())}
    assert minted == {"session_relative_reference"}, (
        f"the superclass argument was counted as a mint: {sorted(minted)}")


@pytest.mark.skipif(_did_root() is None, reason="DID-matlab not checked out")
def test_a_helper_is_recognised_by_shape_and_not_by_its_name(tmp_path):
    """Nothing in the detector knows the string "classBlock".

    The real helper is renamed in the fixture. If the recogniser were keyed on
    the name this passes only by accident today and breaks the first time a
    migrator spells its helper differently -- which is how the board came to
    know one idiom out of three in the first place.
    """
    path = _mig("fitcurve.m")
    stmt, _ = _cut_statement(path, "classBlock('session_relative_reference'")
    fn = _cut_function(path, "classBlock")
    assert stmt and fn
    text = (stmt + "\n" + fn).replace("classBlock", "buildTheClassStruct")
    p = tmp_path / "fixture.m"
    p.write_text(text)
    with open(str(p)) as fh:
        lines = fh.readlines()
    assert "classBlock" not in "".join(lines)
    assert sb.class_block_helpers(lines) == {"buildTheClassStruct": 0}, (
        "the class-block helper is being recognised by NAME")
    minted = {c for c, _l in sb.emitted_document_classes(lines)}
    assert minted == {"session_relative_reference"}


@pytest.mark.skipif(_did_root() is None, reason="DID-matlab not checked out")
def test_session_relative_reference_mints_are_counted_in_full():
    """THE ROW THAT PROVED THIS UNDERCOUNT, held against the real repo.

    Its signed decision is that the class COLLAPSES into `relative_reference`,
    so every mint is work still to undo and the count IS the size of the job.
    The board said 3. Nine migrator files mint it, and this test names the six
    the `'class_name'`-comma regex could not see, so a regression cannot show up
    as a smaller number nobody notices.
    """
    classes = set(_open_classes())
    if "session_relative_reference" not in classes:
        pytest.skip("session_relative_reference is no longer an open class")
    mig, src = sb.migrator_evidence(classes, _did_root(), _ndi_root())
    assert mig is not None and src["files_read"] > 0, (
        "the sweep read no files -- treat as broken, not as clean")
    row = mig["session_relative_reference"]
    # REF_CAP truncates the listed refs, so the count is asserted from the
    # count field and the membership from whatever was listed.
    assert row["n_emitted_class_refs"] >= 9, (
        f'{row["n_emitted_class_refs"]} mint site(s); at least 9 exist -- three `document_class = struct` and six through a local classBlock helper. A smaller number is the undercount returning.')
    assert row["n_named_refs"] == 0, (
        f'{row["n_named_refs"]} site(s) are still filed as bare mentions: {row["named_refs"]}. Every occurrence of this class in the two packages is a mint, a field write or a comment.')


@pytest.mark.skipif(_did_root() is None, reason="DID-matlab not checked out")
def test_the_classblock_migrators_are_each_credited_with_their_mint():
    """Named one file at a time, because `>= 9` alone would be satisfied by nine
    mints from anywhere. These six are the ones the old detector could not see.
    """
    classes = set(_open_classes())
    if "session_relative_reference" not in classes:
        pytest.skip("session_relative_reference is no longer an open class")
    root = os.path.join(_did_root(), "src/did/+did2/+convert/+migrators_j")
    expected = []
    for name in ("fitcurve", "image_stack", "jrclust_clusters",
                 "neuron_extracellular", "pyraview", "vmspikefit"):
        path = os.path.join(root, name + ".m")
        stmt, _ = _cut_statement(path, "classBlock('session_relative_reference'")
        if stmt:
            expected.append(name + ".m")
    assert len(expected) == 6, (
        "expected six classBlock minters of session_relative_reference, found "
        f"{expected} -- re-point this test at whatever uses the idiom now, do not "
        "loosen it")
    for name in expected:
        path = os.path.join(root, name)
        with open(path, errors="replace") as fh:
            minted = {c for c, _l in sb.emitted_document_classes(fh.readlines())}
        assert "session_relative_reference" in minted, (
            f"{name} mints session_relative_reference through classBlock and the "
            "detector missed it")


@pytest.mark.skipif(_did_root() is None, reason="DID-matlab not checked out")
def test_every_occurrence_lands_in_exactly_one_category():
    """The denominator closes: buckets + comments == raw grep count.

    This is the check that makes the separated categories mean something. If a
    site can be in two buckets, or in none, the counts are decorative. Run
    against `session_relative_reference` because its buckets are the ones that
    were confused.
    """
    cls = "session_relative_reference"
    classes = set(_open_classes())
    if cls not in classes:
        pytest.skip(f"{cls} is no longer an open class")
    mig, _src = sb.migrator_evidence(classes, _did_root(), _ndi_root())
    row = mig[cls]
    counted = (row["n_emitted_class_refs"] + row["n_consuming_refs"]
               + row["n_field_write_refs"] + row["n_named_refs"]
               + row["n_comment_mentions"])

    raw = 0
    for _kind, _repo, _label, rel, _grp, skip in sb.MIGRATOR_PACKAGES:
        root = _did_root() if _kind == "did" else _ndi_root()
        if root is None:
            pytest.skip(f"{_repo} not checked out")
        kept, _skipped = sb.package_files(os.path.join(root, rel), set(skip))
        for path in kept:
            with open(path, errors="replace") as fh:
                raw += sum(1 for line in fh if cls in line)
    assert raw > 0, "the raw sweep found nothing -- treat as broken, not clean"
    assert counted == raw, (
        f'{raw} occurrence(s) of {cls} in the packages, {counted} accounted for across the five categories. A site in no bucket is a site nobody counts.')


@pytest.mark.skipif(_did_root() is None, reason="DID-matlab not checked out")
def test_a_site_names_the_repository_it_came_from():
    """`ndi_second_pass/stimulusBathToBath.m:137` is NDI-matlab, and DID-matlab
    holds no file of that name. The board cited it beside 130-odd DID-matlab
    paths with nothing saying which tree to look in."""
    classes = set(_open_classes())
    mig, src = sb.migrator_evidence(classes, _did_root(), _ndi_root())
    assert mig is not None
    repos = {p[1] for p in sb.MIGRATOR_PACKAGES}
    for label in src["packages_read"]:
        assert label.split(":", 1)[0] in repos, label
    seen = 0
    for cls, row in mig.items():
        for key in ("consuming_refs", "emitted_class_refs", "field_write_refs",
                    "named_refs", "comment_mentions"):
            for ref in row[key]:
                seen += 1
                assert ref.split(":", 1)[0] in repos, (
                    f"{cls} cites {ref!r} with no repository")
        if row["migrator_file"]:
            assert row["migrator_file"].split(":", 1)[0] in repos
    assert seen > 0, "no references at all -- this sweep checked nothing"

    ndi_only = os.path.join(
        _ndi_root(), "src/ndi/+ndi/+migrate/+internal/stimulusBathToBath.m")
    assert os.path.exists(ndi_only), (
        "stimulusBathToBath.m has moved; re-point this test at whatever "
        "second-pass file the board still cites")
    assert not os.path.exists(_mig("stimulusBathToBath.m")), (
        "DID-matlab now has a stimulusBathToBath.m too, so this file no longer "
        "demonstrates the ambiguity")


@pytest.mark.skipif(_did_root() is None, reason="DID-matlab not checked out")
def test_an_unreadable_class_name_is_counted_and_not_skipped():
    """`struct('class_name', leafClass, ...)` and `classBlock(e.class, ...)` are
    mints this per-file scan cannot NAME. Rule 3: not being able to read a site
    is not evidence there is nothing there, so the sites are counted and listed
    and the mint totals are stated as a floor."""
    classes = set(_open_classes())
    _mig_ev, src = sb.migrator_evidence(classes, _did_root(), _ndi_root())
    assert src["n_unresolved_mint_sites"] > 0, (
        "no unresolved mint sites -- either the migrators stopped computing "
        "class names, in which case delete this test, or the counter stopped "
        "counting, which is the failure it exists to catch")
    assert (len(src["unresolved_mint_sites"])
            == src["n_unresolved_mint_sites"])
    for site in src["unresolved_mint_sites"]:
        assert site.split(":", 1)[0] in {p[1] for p in sb.MIGRATOR_PACKAGES}


def test_the_artifact_never_sums_unlike_categories():
    """The cell that read *still emitted/named at N site(s)* merged six missed
    mints with nine field writes under one number, and the number was quoted
    onward as one kind of thing."""
    # Asserted on the PER-CLASS BULLETS, which is where the caption lived, and
    # on the format string in the tool. The explanatory prose above the table
    # quotes the old caption on purpose; a rule that forbade the phrase outright
    # would forbid the artifact from explaining what it stopped doing.
    with open(STATUS) as fh:
        bullets = [ln for ln in fh if ln.startswith("- `")]
    assert bullets, "no per-class bullets -- this sweep would check nothing"
    offenders = [ln for ln in bullets if "emitted/named" in ln]
    assert offenders == [], (
        f'the summed caption is back on {len(offenders)} class row(s); mint, field write and comment are not one quantity: {offenders[:2]}')
    src = Path(os.path.join(TOOLS, "status_board.py")).read_text()
    assert "still emitted/named at %d site(s)" not in src, (
        "the summed caption's format string is back in the renderer")
    with open(DECISIONS) as fh:
        rows = json.load(fh)["open_class_state"]["classes"]
    assert rows, "no rows -- this sweep would check nothing"
    for r in rows:
        assert "n_emitting_refs" not in r, (
            "{} carries the summed count again".format(r["class_name"]))
        for key in ("n_emitted_class_refs", "n_field_write_refs",
                    "n_named_refs", "n_comment_mentions"):
            assert key in r, "{} has no {}".format(r["class_name"], key)


def test_a_comment_mention_counts_toward_nothing():
    """Comments are the biggest bucket for several classes and they are evidence
    of nothing. They are counted anyway, in their own column, so that claim is
    checkable from the artifact instead of taken on trust."""
    assert sb.COMMENT_KIND not in sb.CONSUMING_KINDS
    assert sb.COMMENT_KIND not in sb.CODE_KINDS
    assert sb.COMMENT_KIND != sb.EMITTED_CLASS_KIND
    with open(DECISIONS) as fh:
        rows = json.load(fh)["open_class_state"]["classes"]
    commented = [r for r in rows if r.get("n_comment_mentions")]
    assert commented, "no class has a comment mention -- the counter is dead"
    only_comments = [r for r in commented
                     if not (r["n_consuming_refs"] or r["n_emitted_class_refs"]
                             or r["n_field_write_refs"] or r["migrator_file"]
                             or r["decided_targets_built"])]
    for r in only_comments:
        assert r["state"] == sb.STATE_A, (
            f'{r["class_name"]} has {r["n_comment_mentions"]} comment mention(s) and nothing else, and is rendered {r["state"]}')


# ---------------------------------------------------------------------------
# THE OTHER HALF OF THE V_eta PASS -- the batch post-passes
# ---------------------------------------------------------------------------
#
# The scan roots named `+migrators_j` and stopped. `+migrators_j` is the
# PER-DOCUMENT half of the DID-side V_eta pass; the other half is the BATCH
# POST-PASSES in `+did2/+convert` itself and its `+entities/`/`+readers/` helper
# packages, which run over the whole converted batch and do what a
# single-document migrator cannot. Roughly half the V_eta-path code built on
# 2026-08-11 lives there and the board could not see any of it.
#
# THE V_zeta PACKAGES STAY OUT. `+migrators`, `+migrators_i` and `+migrators_e`
# are a deliberate, sound exclusion and this section pins it rather than
# relaxing it -- the batch root is their PARENT, so a walk with no exclusion
# would sweep all 38 of them into the build signal.

_CONVERT = "src/did/+did2/+convert"


def _convert_root():
    root = _did_root()
    return None if root is None else os.path.join(root, _CONVERT)


def _batch_package():
    """The MIGRATOR_PACKAGES row for the batch post-passes."""
    rows = [p for p in sb.MIGRATOR_PACKAGES if p[4] == sb.GROUP_BATCH]
    assert len(rows) == 1, (
        f'expected exactly one batch post-pass root, found {len(rows)}')
    return rows[0]


@pytest.mark.skipif(_did_root() is None, reason="DID-matlab not checked out")
def test_the_convert_census_is_the_one_the_board_measures():
    """DENOMINATOR FIRST: 187 = 125 scanned + 38 excluded + 24 added.

    Re-derived from the tree, never from a number written down here: the totals
    are computed by walking `+did2/+convert` and the assertions compare the
    board's own denominator fields against that walk. A file added to
    `+convert` tomorrow shows up on BOTH sides, so this test measures the
    board's reach and not the repo's size.
    """
    base = _convert_root()
    per_dir = {}
    for dirpath, _dirs, names in os.walk(base):
        rel = os.path.relpath(dirpath, base)
        top = "." if rel == "." else rel.split(os.sep)[0]
        per_dir[top] = per_dir.get(top, 0) + sum(1 for n in names
                                                 if n.endswith(".m"))
    total = sum(per_dir.values())
    assert total > 0, "no .m files under +convert -- treat as broken, not clean"

    v_zeta = sum(per_dir.get(p, 0) for p in sb.V_ZETA_PACKAGES)
    migrators_j = per_dir.get("+migrators_j", 0)
    batch = total - v_zeta - migrators_j
    assert v_zeta and migrators_j and batch, (
        f'one of the three groups is empty: +migrators_j={migrators_j} v_zeta={v_zeta} batch={batch}')

    mig, src = sb.migrator_evidence(set(_open_classes()), _did_root(),
                                    _ndi_root())
    assert mig is not None and src["files_read"], (
        "the sweep read no files -- treat as broken, not as clean")
    assert src["files_read_by_group"][sb.GROUP_BATCH] == batch, (
        f'the board read {src["files_read_by_group"][sb.GROUP_BATCH]} batch post-pass file(s); {batch} .m files sit under +convert outside +migrators_j and the V_zeta packages. The roots have stopped covering the batch half of the pass.')
    assert src["n_files_excluded_v_zeta"] == v_zeta, (
        f'the V_zeta exclusion reports {src["n_files_excluded_v_zeta"]} file(s), the tree holds {v_zeta}. An exclusion that has stopped reaching its files is indistinguishable from a root nobody wrote down -- which is how the batch passes went missing.')
    assert (src["files_read_by_group"][sb.GROUP_MIGRATOR]
            >= migrators_j), "the +migrators_j root stopped being read in full"


@pytest.mark.skipif(_did_root() is None, reason="DID-matlab not checked out")
def test_a_mint_in_a_batch_post_pass_is_found(tmp_path):
    """The fixture is CUT FROM `resolveDeferredBaths.m`, not written here.

    Same rule as the idiom fixtures above: a fixture built from the same premise
    as the detector cannot catch the detector. These bytes are the migrator's
    own, so if the batch passes change shape the fixture changes with them.
    """
    path = os.path.join(_convert_root(), "resolveDeferredBaths.m")
    assert os.path.exists(path), (
        "resolveDeferredBaths.m has moved; re-point this test at whatever "
        "batch post-pass mints a document now")
    stmt, lineno = _cut_statement(
        path, "struct('class_name', 'session_relative_reference'")
    assert stmt, (
        "resolveDeferredBaths.m no longer mints session_relative_reference -- "
        "re-point this fixture rather than relaxing it")
    p = tmp_path / "fixture.m"
    p.write_text(stmt)
    with open(str(p)) as fh:
        minted = {c for c, _l in sb.emitted_document_classes(fh.readlines())}
    assert "session_relative_reference" in minted, (
        f'the mint at resolveDeferredBaths.m:{lineno} was not recognised. Detected: {sorted(minted)}')
    assert "time_reference" not in minted, (
        "the superclass in the same statement was counted as a mint")

    # ... and the whole-repo sweep must cite it, filed under the batch group.
    classes = set(_open_classes())
    if "session_relative_reference" not in classes:
        pytest.skip("session_relative_reference is no longer an open class")
    mig, _src = sb.migrator_evidence(classes, _did_root(), _ndi_root())
    row = mig["session_relative_reference"]
    batch = row["by_group"][sb.GROUP_BATCH]
    assert batch["n_emitted_class_refs"] >= 2, (
        f'{batch["n_emitted_class_refs"]} batch mint(s) of session_relative_reference; resolveDeferredBaths.m has two. The board is back to reading half the path.')
    assert any("resolveDeferredBaths.m" in r
               for r in batch["emitted_class_refs"]), batch["emitted_class_refs"]
    assert row["n_emitted_class_refs"] == (
        batch["n_emitted_class_refs"]
        + row["by_group"][sb.GROUP_MIGRATOR]["n_emitted_class_refs"]), (
        "the per-group mint counts do not add up to the total")


@pytest.mark.skipif(_did_root() is None, reason="DID-matlab not checked out")
def test_the_v_zeta_packages_are_still_excluded():
    """A V_zeta migrator is not evidence a V_eta target is built.

    The batch root is `+convert`, the PARENT of `+migrators`, `+migrators_i` and
    `+migrators_e`, so this exclusion is now load-bearing in a way it was not
    when the roots were enumerated one package at a time. Checked two ways: no
    citation anywhere in the sweep comes from those packages, and the sweep
    reports a NON-ZERO count of files it skipped on their account -- a zero
    would mean the exclusion had stopped reaching them, not that they were gone.
    """
    classes = set(_open_classes())
    mig, src = sb.migrator_evidence(classes, _did_root(), _ndi_root())
    assert mig is not None and src["files_read"], (
        "the sweep read no files -- treat as broken, not as clean")
    seen = 0
    for cls, row in mig.items():
        for key in ("consuming_refs", "emitted_class_refs", "field_write_refs",
                    "named_refs", "comment_mentions"):
            for ref in row[key]:
                seen += 1
                for pkg in sb.V_ZETA_PACKAGES:
                    assert (f"/{pkg}/") not in ref, (
                        f"{cls} is cited from the V_zeta package {pkg}: {ref!r}. That "
                        "inflates (b) with work predating every decision here.")
    assert seen > 0, "no references at all -- this sweep checked nothing"
    for site in src["unresolved_mint_sites"]:
        for pkg in sb.V_ZETA_PACKAGES:
            assert (f"/{pkg}/") not in site, site

    assert src["n_files_excluded_v_zeta"] > 0, (
        "no file was excluded on V_zeta grounds; the exclusion is either dead "
        "or unreported, and both look identical from the artifact")
    for f in src["files_excluded_v_zeta"]:
        assert any((f"/{p}/") in f for p in sb.V_ZETA_PACKAGES), f


@pytest.mark.skipif(_did_root() is None, reason="DID-matlab not checked out")
def test_batch_evidence_is_distinguishable_from_migrator_evidence():
    """A site in a batch post-pass and a site in a per-document migrator are
    DIFFERENT FACTS about a class and must never arrive as one number.

    Checked at every layer the number passes through: the sweep's per-class
    `by_group`, the derived open-class row, and the rendered artifact.
    """
    classes = set(_open_classes())
    mig, src = sb.migrator_evidence(classes, _did_root(), _ndi_root())
    assert mig is not None and src["files_read"]
    assert set(src["groups"]) == set(sb.GROUPS)
    assert src["files_read_by_group"][sb.GROUP_BATCH] > 0, (
        "the batch post-passes contributed no files; there is nothing to "
        "distinguish and the roots have regressed")

    keys = ("n_consuming_refs", "n_emitted_class_refs", "n_field_write_refs",
            "n_named_refs", "n_comment_mentions")
    split_somewhere = 0
    for cls, row in mig.items():
        for k in keys:
            assert row[k] == sum(row["by_group"][g][k] for g in sb.GROUPS), (
                f"{cls}: {k} does not decompose into its groups")
        if any(row["by_group"][sb.GROUP_BATCH][k] for k in keys):
            split_somewhere += 1
    assert split_somewhere > 0, (
        "no open class has any batch post-pass evidence -- the group column is "
        "carrying nothing and the split is decorative")

    # The derived rows carry it too, and the artifact prints it.
    with open(DECISIONS) as fh:
        rows = json.load(fh)["open_class_state"]["classes"]
    assert rows, "no rows -- this sweep would check nothing"
    for r in rows:
        assert set(r.get("by_group") or {}) == set(sb.GROUPS), (
            "{} carries no per-group split".format(r["class_name"]))
    with open(STATUS) as fh:
        text = fh.read()
    assert sb.GROUP_LABEL[sb.GROUP_BATCH] in text, (
        "the artifact never names the batch post-pass group, so a reader "
        "cannot tell which half of the pass a count came from")
    assert "minted (M+B)" in text, (
        "the mint column stopped carrying its migrator/batch split")


@pytest.mark.skipif(_did_root() is None, reason="DID-matlab not checked out")
def test_a_class_minted_only_in_a_batch_post_pass_is_not_invisible():
    """Some document classes are minted in the batch passes and NOWHERE the
    board used to look. Before the roots were fixed those mints existed in no
    count at all -- which reads from the artifact as clean ground rather than as
    unread ground, the exact failure mode this repo keeps paying for.

    Derived, not listed: the two sweeps are run and compared.
    """
    def _mints(files):
        out = {}
        for path in files:
            with open(path, errors="replace") as fh:
                for cls, lno in sb.emitted_document_classes(fh.readlines()):
                    out.setdefault(cls, []).append(f'{path}:{lno}')
        return out

    old, new = [], []
    for _k, _repo, _l, rel, group, skip in sb.MIGRATOR_PACKAGES:
        root = _did_root() if _k == "did" else _ndi_root()
        if root is None:
            pytest.skip(f"{_repo} not checked out")
        kept, _s = sb.package_files(os.path.join(root, rel), set(skip))
        (new if group == sb.GROUP_BATCH else old).extend(kept)
    assert old and new, "one of the two groups is empty"
    old_m, new_m = _mints(old), _mints(new)
    assert new_m, "the batch post-passes mint nothing -- treat as broken"
    only_batch = sorted(set(new_m) - set(old_m))
    assert only_batch, (
        "no class is minted only in a batch post-pass any more. If the passes "
        "genuinely converged, delete this test; do not weaken it.")
    for cls in only_batch:
        assert new_m[cls], cls


@pytest.mark.skipif(_did_root() is None, reason="DID-matlab not checked out")
def test_an_unresolvable_batch_mint_is_named_and_not_dropped():
    """`struct('class_name', className, ...)` in a batch post-pass is a mint
    this per-file scan cannot NAME. Rule 3 applies in the new roots exactly as
    in the old: the site is reported as a named unresolved site, never as a
    silent omission."""
    classes = set(_open_classes())
    _mig_ev, src = sb.migrator_evidence(classes, _did_root(), _ndi_root())
    by_group = src["n_unresolved_mint_sites_by_group"]
    assert sum(by_group.values()) == src["n_unresolved_mint_sites"]
    assert by_group[sb.GROUP_BATCH] > 0, (
        "no unresolved mint site in the batch post-passes -- either they "
        "stopped computing class names, in which case delete this test, or the "
        "counter stopped reaching them, which is what it exists to catch")
    listed = src["unresolved_mint_sites_by_group"][sb.GROUP_BATCH]
    assert len(listed) == by_group[sb.GROUP_BATCH]
    for site in listed:
        assert site.startswith("DID-matlab:convert/"), site
        assert "(" in site and site.rstrip().endswith(")"), (
            f"{site!r} does not name the expression it could not resolve")


@pytest.mark.skipif(_did_root() is None, reason="DID-matlab not checked out")
def test_all_three_mint_idioms_are_recognised_THROUGH_the_batch_root(tmp_path):
    """The idioms are verified IN the new root, not assumed to carry over.

    Measured on the real files, the batch post-passes use idiom 1 only today --
    which is exactly the shape of premise that produced the original defect, so
    it is not left as an assumption. Statements for all three idioms are cut
    from the real migrators that use them and dropped into a tree laid out like
    DID-matlab, so the sweep reaches them THROUGH the batch root and files them
    under the batch group. If a post-pass adopts `classBlock` tomorrow, this
    already passes.

    The bytes are the migrators' own (`_cut_statement`/`_cut_function`, plain
    line scans that never call the detector), for the reason stated above the
    idiom fixtures: a fixture built from the detector's premise cannot catch the
    detector.
    """
    pieces, want = [], set()
    for idiom, rel, needle, helper in _IDIOM_SOURCES:
        path = _mig(rel)
        stmt, _lineno = _cut_statement(path, needle)
        assert stmt, f"{rel} no longer contains {needle!r}"
        pieces.append(stmt)
        if helper:
            fn = _cut_function(path, helper)
            assert fn, f"{rel} no longer defines {helper}()"
            pieces.append(fn)
        want.add(re.findall(r"'([a-z_][a-z_0-9]*)'", needle)[-1])
    assert len(want) > 1, "the idiom sources no longer cover distinct classes"

    root = tmp_path / "DID-matlab"
    conv = root / "src" / "did" / "+did2" / "+convert"
    (conv / "+migrators_j").mkdir(parents=True)
    (conv / "transplanted_post_pass.m").write_text("\n".join(pieces))
    # A V_zeta package in the same tree, carrying the same statements: the
    # exclusion must hold even when what it is hiding would otherwise pass.
    (conv / "+migrators_i").mkdir()
    (conv / "+migrators_i" / "decoy.m").write_text("\n".join(pieces))

    mig, src = sb.migrator_evidence(want, str(root), None)
    assert mig is not None, "the batch root was not read at all"
    assert src["files_read_by_group"][sb.GROUP_BATCH] == 1, (
        f'expected exactly the transplanted file, read {src["files_read_by_group"][sb.GROUP_BATCH]}')
    for cls in sorted(want):
        batch = mig[cls]["by_group"][sb.GROUP_BATCH]
        assert batch["n_emitted_class_refs"] >= 1, (
            f"{cls} is minted in the transplanted post-pass and the sweep did not "
            "see it through the batch root")
        assert all("transplanted_post_pass.m" in r
                   for r in batch["emitted_class_refs"]), (
            "{} cites something other than the transplanted file: {}".format(cls, batch["emitted_class_refs"]))
    assert src["n_files_excluded_v_zeta"] == 1, (
        "the decoy V_zeta file was not excluded")


# --------------------------------------------------------------------------
# The "DECIDED by the team, awaiting build" section used to open with three
# HARDCODED lines asserting "the schema has not changed yet", printed under
# every family regardless of what was in the tree. By 2026-08-11 it was false
# for essentially all of them -- a hand check of the target classes those
# families name found every one already built, one of them as a block on
# `subject_interaction` rather than a class file.
#
# That is this project's recurring defect with the sign flipped. The usual
# direction is prose claiming MORE progress than exists; this claimed LESS,
# which is exactly why it survived: understating never produces a wrong build,
# only wasted work. Both are one thing -- a GENERATED artifact stating a fact
# its generator never checked.
#
# The first replacement then repeated the error one layer up. It computed
# "13 target classes named, 13 built, 0 missing" and printed it as a clean
# bill of health while 11 of the 18 families had contributed NOTHING to those
# numbers, because no member of theirs carries a `decided_targets` entry. A
# reassuring "0 not built" that really meant "0 among the families I could
# see" is the `silentLoss` defect verbatim.
#
# So there are two things to hold down, and the second is the important one.
# --------------------------------------------------------------------------

_AWAITING_HEAD = "## DECIDED by the team, awaiting build"


def _awaiting_section():
    with open(STATUS) as fh:
        text = fh.read()
    assert _AWAITING_HEAD in text, (
        "the awaiting-build section is gone from the board; if it was renamed, "
        "retarget this test rather than deleting it -- it is the only thing "
        "keeping an unchecked claim out of that section")
    body = text.split(_AWAITING_HEAD, 1)[1]
    # Stop at the next top-level heading.
    nxt = body.find("\n## ")
    return body if nxt == -1 else body[:nxt]


def test_awaiting_build_never_asserts_the_schema_is_unbuilt():
    """The hardcoded claim must not come back, in any spelling."""
    sec = _awaiting_section()
    for banned in ("the schema has not changed yet",
                   "the schema has not changed",
                   "none of these is built"):
        assert banned not in sec, (
            f"the awaiting-build section asserts {banned!r} again. That sentence was "
            "removed because it was false for every family it decorated and "
            "would send a reader to rebuild schema that already exists. If "
            "the tree really has regressed, the per-family `targets built` "
            "column will say so on its own.")


def test_awaiting_build_states_how_many_families_it_could_not_check():
    """RULE 5, applied to the fix and not just to the thing it fixed.

    A result is only readable beside the coverage of the check that produced
    it. This asserts the section reports BOTH -- how many families it checked
    and how many it could not -- so a future edit cannot quietly drop the
    second half and leave a bare, reassuring zero.
    """
    sec = _awaiting_section()
    assert "DENOMINATOR" in sec, (
        "the awaiting-build section no longer leads with a denominator")

    m = re.search(r"(\d+) signed families\. (\d+) named at least one decided "
                  r"target class and were checked against the built tree; "
                  r"(\d+) named none and are UNCHECKED HERE", sec)
    assert m, (
        "the awaiting-build denominator no longer states checked-vs-unchecked "
        "family counts. It must, and in a form that cannot be read as a clean "
        "bill of health: an unchecked family is not a passing one.")
    total, checked, unchecked = (int(g) for g in m.groups())
    assert checked + unchecked == total, (
        f"checked ({checked}) + unchecked ({unchecked}) != families ({total}) -- the section's own arithmetic does not close, so one bucket is silently dropping families")

    if unchecked:
        assert "unchecked, NOT clean" in sec, (
            f'{unchecked} families went unchecked and the section does not say that a blank is not a pass')
        # The two causes of a blank must stay distinguished in the prose: a
        # family that DISSOLVES correctly names no target, while one whose
        # target is fixed in a signed plan and never recorded is a real gap.
        # Rendering both as blank is how a settled decision gets re-litigated.
        assert "DISSOLVES" in sec, (
            "the section no longer explains that a blank target has two "
            "causes -- dissolution (final) and an unrecorded target (a gap)")


def test_awaiting_build_table_carries_a_targets_built_column():
    sec = _awaiting_section()
    assert "| targets built |" in sec, (
        "the per-family `targets built` column is gone. It is what makes the "
        "section's claim derive from the tree instead of from a string.")
    # Every family row must carry a verdict -- a ratio, or the explicit
    # admission that no target is on file. A blank cell would be the old
    # failure in miniature.
    rows = [ln for ln in sec.splitlines()
            if ln.startswith("| **") and ln.count("|") >= 5]
    assert rows, "the awaiting-build table has no family rows"
    for ln in rows:
        cell = ln.split("|")[3].strip()
        assert re.fullmatch(r"\d+ of \d+", cell) or cell == "no target recorded", (
            "family row {!r} has an uninterpretable `targets built` cell {!r}".format(ln.split("|")[1].strip(), cell))
