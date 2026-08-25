"""Tests for `tools/check_citations.py`.

WHY THIS FILE EXISTS
--------------------
The checker makes ONE claim -- *the cited line still carries what the citing
sentence quotes* -- and every way that claim can fail, fails QUIETLY:

  * a resolver that accepts anything reports a clean corpus forever. So does a
    scan whose pattern stopped matching. Both print the same zero as a correct
    run over a correct corpus, which is `silentLoss` printing "0 empty edges"
    while reading nothing.
  * the deliberate under-specifications in this corpus -- an `origin/main`-only
    citation, a basename citation whose file has moved, a dotted MATLAB
    namespace -- look exactly like broken citations to a naive resolver, and a
    checker that reports them as faults is a checker somebody switches off.

So the properties are pinned by MUTATION over CONSTRUCTED fixtures: break the
tool or the fixture, watch the named test go red, revert. Constructed rather
than read off today's corpus deliberately -- a rule tested only against data
that happens to exercise it stops being tested the day the data changes, and
this corpus changes hourly, which is the whole reason the tool exists.
"""

import contextlib
import importlib.util
import io
import os
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(REPO_ROOT, "tools")


def _load(name):
    spec = importlib.util.spec_from_file_location(
        name, os.path.join(TOOLS, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


C = _load("check_citations")


# --------------------------------------------------------------------------
# A SANDBOX CORPUS -- one markdown document citing one target file, in a
# checkout the tool is told about. Nothing here reads the real repository.
# --------------------------------------------------------------------------

@contextlib.contextmanager
def sandbox(tmp_path, targets, doc_text, repo_name="Fake-matlab"):
    root = tmp_path / repo_name
    for rel, text in targets.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    doc = tmp_path / "RECORD.md"
    doc.write_text(doc_text, encoding="utf-8")

    old_repos, old_trees = C.REPOS, C.TREES
    C.REPOS = {repo_name: str(root)}
    C.TREES = {repo_name: C.Tree(repo_name, str(root))}
    try:
        yield doc
    finally:
        C.REPOS, C.TREES = old_repos, old_trees


def verdicts(doc):
    cites, read, _lines, _orphans, _bare, _bad = C.run([str(doc)])
    assert read == 1, "the sandbox document was not read"
    return {c.cited: c for c in cites}


BODY = "\n".join(
    ["% a header line"] * 9                       # lines 1-9
    + ["if isempty(subjectId)"]                   # line 10
    + ["    bodies = {preBody};"]                 # line 11
    + ["    return;"]                             # line 12
    + ["end"]                                     # line 13
    + ["% filler that is long enough to be a line"] * 20   # 14-33
    + ["THE MOVED SENTENCE ABOUT A DIFFERENT THING"]       # line 34
)


# --------------------------------------------------------------------------
# THE CORE RULE
# --------------------------------------------------------------------------

def test_a_citation_whose_quote_is_still_on_the_line_verifies(tmp_path):
    with sandbox(tmp_path, {"src/guard.m": BODY},
                 "The guard is live at `src/guard.m:10` "
                 "(`if isempty(subjectId)`).\n") as doc:
        c = verdicts(doc)["src/guard.m:10"]
    assert c.verdict == "VERIFIED", c.reason
    assert c.anchor_used == "if isempty(subjectId)"


def test_a_citation_pointed_at_the_wrong_line_is_DRIFTED_and_says_where(tmp_path):
    """MUTATION: move the number, leave everything else alone.

    This is the whole point of the tool, and it is also the mutation that a
    checker testing only line EXISTENCE passes: line 30 exists, is non-empty,
    and reads like source."""
    with sandbox(tmp_path, {"src/guard.m": BODY},
                 "The guard is live at `src/guard.m:30` "
                 "(`if isempty(subjectId)`).\n") as doc:
        c = verdicts(doc)["src/guard.m:30"]
    assert c.verdict == "DRIFTED", c.reason
    assert c.true_lines == [10], "the report must say where the line went"


def test_a_real_line_about_something_else_is_never_VERIFIED(tmp_path):
    """The `Contents.m:348` case -- the worst kind, per the audit.

    The cited line EXISTS and carries a perfectly plausible sentence. A reader
    who follows it concludes the citation was misremembered when the claim was
    fine. Nothing about "the line exists" may reach VERIFIED."""
    with sandbox(tmp_path, {"src/guard.m": BODY},
                 "The guard is live at `src/guard.m:34` "
                 "(`if isempty(subjectId)`).\n") as doc:
        c = verdicts(doc)["src/guard.m:34"]
    assert c.verdict != "VERIFIED"
    assert c.verdict == "DRIFTED"


def test_a_citation_quoting_nothing_is_UNDECIDABLE_never_a_pass(tmp_path):
    """The failure mode is doubt, ANNOUNCED. Not a silent pass, and not a
    fault either -- the tool has nothing to go on and says so."""
    with sandbox(tmp_path, {"src/guard.m": BODY},
                 "The guard is live at `src/guard.m:30`, as anyone can see.\n") as doc:
        c = verdicts(doc)["src/guard.m:30"]
    assert c.verdict == "UNDECIDABLE"
    assert "quotes nothing" in c.reason


def test_a_common_fragment_cannot_verify_a_citation(tmp_path):
    """`% filler...` occurs on twenty lines. Landing on one proves nothing, so
    it may not confirm and it may not deny."""
    with sandbox(tmp_path, {"src/guard.m": BODY},
                 "See `src/guard.m:20` "
                 "(`% filler that is long enough to be a line`).\n") as doc:
        c = verdicts(doc)["src/guard.m:20"]
    assert c.verdict == "UNDECIDABLE", c.reason


# --------------------------------------------------------------------------
# THE ASYMMETRY -- confirmation is cheap, denial is not
# --------------------------------------------------------------------------

def test_denial_needs_a_UNIQUE_anchor(tmp_path):
    """Two lines carry the quote, neither is the cited one. The tool knows the
    citation is not confirmed; it does NOT know where the line went, and
    guessing one of the two would be a finding a reader cannot act on."""
    body = "\n".join([f"padding line number {i}" for i in range(1, 41)])
    body = body.replace("padding line number 5", "the repeated marker text")
    body = body.replace("padding line number 33", "the repeated marker text")
    with sandbox(tmp_path, {"src/two.m": body},
                 "See `src/two.m:20` (`the repeated marker text`).\n") as doc:
        c = verdicts(doc)["src/two.m:20"]
    assert c.verdict == "UNDECIDABLE", c.reason
    assert "unique" in c.reason


def test_denial_needs_an_ADJACENT_anchor(tmp_path):
    """`_DELETE_PHASE8` and the citation shared a sentence seventy-five
    characters apart, in different clauses. The quote was unique in the file
    and nowhere near the cited line, and the tool called a CORRECT citation
    drifted on the strength of it."""
    body = "\n".join([f"% padding {i}" for i in range(1, 41)])
    body = body.replace("% padding 3", "the distant unique marker")
    filler = "x" * 70
    with sandbox(tmp_path, {"src/far.m": body},
                 f"Both classes are out of `the distant unique marker` "
                 f"({filler}), the guard is live at `src/far.m:20`.\n") as doc:
        c = verdicts(doc)["src/far.m:20"]
    assert c.verdict == "UNDECIDABLE", c.reason


def test_a_quote_from_a_DIFFERENT_sentence_decides_nothing(tmp_path):
    """A paragraph-wide anchor window fabricated three drift findings against
    today's corpus. The window is the citation's own sentence."""
    body = "\n".join([f"% padding {i}" for i in range(1, 41)])
    body = body.replace("% padding 3", "the marker in another sentence")
    with sandbox(tmp_path, {"src/sep.m": body},
                 "An earlier sentence mentions `the marker in another sentence`. "
                 "A later one cites `src/sep.m:20` with no quotation at all.\n") as doc:
        c = verdicts(doc)["src/sep.m:20"]
    assert c.verdict == "UNDECIDABLE", c.reason
    assert "quotes nothing verbatim" in c.reason


# --------------------------------------------------------------------------
# WHAT IS DELIBERATE AND MUST NOT BE A FAULT
# --------------------------------------------------------------------------

def _git(root, *args):
    subprocess.run(["git", "-C", str(root), *args], check=True,
                   capture_output=True, text=True)


def test_an_origin_main_only_citation_is_NOT_a_fault(tmp_path):
    """MUTATION 4 of the brief, and it is the one that reads as a bug report.

    `origin/main src/ndi/+ndi/+element/ensemble.m:274-276` does not exist in
    the NDI working tree -- it exists on the ref the sentence NAMES. Resolution
    falls through to `origin/main`, and the citation verifies there. A resolver
    that only reads the working tree calls it DEAD, which is a fault reported
    against a citation that is exactly right."""
    root = tmp_path / "Fake-matlab"
    (root / "src").mkdir(parents=True)
    (root / "src" / "gone.m").write_text(
        "\n".join([f"% pad {i}" for i in range(1, 9)]
                  + ["mapdoc = mapdoc.add_dependency_value_n('neuron_id', x);"]),
        encoding="utf-8")
    _git(root, "init", "-q", "-b", "main")
    _git(root, "-c", "user.email=t@t", "-c", "user.name=t", "add", ".")
    _git(root, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "x")
    # A local ref standing in for `origin/main`, then the file is REMOVED from
    # the working tree -- the NDI feature-branch situation exactly.
    _git(root, "update-ref", "refs/remotes/origin/main", "HEAD")
    os.remove(root / "src" / "gone.m")

    doc = tmp_path / "RECORD.md"
    doc.write_text(
        "The roster is carried as edges -- `origin/main src/gone.m:9`: "
        "`mapdoc = mapdoc.add_dependency_value_n('neuron_id', x);`\n",
        encoding="utf-8")

    old_repos, old_trees = C.REPOS, C.TREES
    C.REPOS = {"Fake-matlab": str(root)}
    C.TREES = {"Fake-matlab": C.Tree("Fake-matlab", str(root))}
    try:
        c = verdicts(doc)["src/gone.m:9"]
    finally:
        C.REPOS, C.TREES = old_repos, old_trees

    assert c.verdict == "VERIFIED", c.reason
    assert c.via == "origin/main", \
        "the ref it resolved through must be REPORTED, not silently used"


def test_a_basename_citation_survives_a_directory_move(tmp_path):
    """`imageDocMaker.m:121-127` and `jMeasurementFold.m:69` are cited by
    basename and both files have moved. The audit calls this UNDER-specified
    in the right dimension; it is not a fault."""
    with sandbox(tmp_path, {"deep/nested/moved/guard.m": BODY},
                 "See `guard.m:10` (`if isempty(subjectId)`).\n") as doc:
        c = verdicts(doc)["guard.m:10"]
    assert c.verdict == "VERIFIED", c.reason
    assert c.resolved.endswith("guard.m")


def test_a_dotted_matlab_namespace_is_expanded_to_its_package_path():
    """`ndi.fun.session.diff.m` IS `+ndi/+fun/+session/diff.m`. Read literally
    it is a basename no repository contains, and five citations were reported
    DEAD on that account -- `V_eta_OPEN_WORK.md` records an earlier hand audit
    making and correcting the identical mistake."""
    assert C._segments("ndi.fun.session.diff.m") == ["ndi", "fun", "session", "diff.m"]
    assert C._basename("ndi.fun.session.diff.m") == "diff.m"
    # A one-dot python path must NOT be split.
    assert C._segments("tools/coverage.py") == ["tools", "coverage.py"]
    assert C._basename("check_prose_counts.py") == "check_prose_counts.py"
    # `+` package prefixes and repo-name prefixes normalise away.
    assert C._segments("DID-matlab/src/did/+did2/+validate/references.m") == \
        ["src", "did", "did2", "validate", "references.m"]
    assert C._segments(".../+migrators_j/Contents.m") == ["migrators_j", "Contents.m"]


def test_a_quoted_OLD_citation_is_exempt_from_the_gate_but_still_reported(tmp_path):
    """The house writes corrections as `old -> new`, and the old value is wrong
    ON PURPOSE. A checker that fails on every correction note gets disabled."""
    text = ("The guard is live at `src/guard.m:10` (was `src/guard.m:30`).\n"
            "\n"
            "        src/guard.m:34    -> :10   the guard\n")
    with sandbox(tmp_path, {"src/guard.m": BODY}, text) as doc:
        cites, _r, _l, _o, _b, _u = C.run([str(doc)])
    hist = [c for c in cites if c.historical]
    live = [c for c in cites if not c.historical]
    assert {c.cited for c in hist} == {"src/guard.m:30", "src/guard.m:34"}
    assert [c.cited for c in live] == ["src/guard.m:10"]
    # Exempt from the gate, NOT from the report: they are still adjudicated.
    assert all(c.verdict is not None for c in hist)


def test_an_item_number_written_with_a_colon_is_a_COLLISION_not_drift(tmp_path):
    """`V_eta_OPEN_WORK.md:51` is indistinguishable from a line reference and
    lands on unrelated prose. Telling a reader to repoint it would be telling
    them to repoint nothing -- the number is right and the COLON is wrong."""
    items = "\n".join(f"### #{n} something\n\nprose about item {n}\n"
                      for n in range(40, 60))
    text = "As recorded in `WORKLIST.md:51` (`prose about item 51`).\n"
    with sandbox(tmp_path, {"WORKLIST.md": items}, text) as doc:
        c = verdicts(doc)["WORKLIST.md:51"]
    assert c.verdict == "COLLISION", c.reason
    assert "row #51" in c.reason


def test_a_markdown_file_with_no_item_vocabulary_is_graded_as_lines(tmp_path):
    """The collision rule may not swallow ordinary markdown citations --
    `V_eta_time_reference_model_plan.md:642` is a real line number."""
    body = "\n".join([f"prose line {i}" for i in range(1, 41)])
    body = body.replace("prose line 12", "CHANGE 5 -- the uniqueness rule")
    with sandbox(tmp_path, {"PLAN.md": body},
                 "See `PLAN.md:12` (`CHANGE 5 -- the uniqueness rule`).\n") as doc:
        c = verdicts(doc)["PLAN.md:12"]
    assert c.verdict == "VERIFIED", c.reason


# --------------------------------------------------------------------------
# RANGES AND MULTI-SPAN CITATIONS
# --------------------------------------------------------------------------

def test_ranges_and_comma_lists_parse_into_spans():
    assert C.parse_spans("90") == [(90, 90)]
    assert C.parse_spans("274-276") == [(274, 276)]
    assert C.parse_spans("93,99") == [(93, 99 - 6)] or True     # shape only
    assert C.parse_spans("93,99") == [(93, 93), (99, 99)]
    assert C.parse_spans("49-56,523-526") == [(49, 56), (523, 526)]
    assert C.parse_spans("156,310,388") == [(156, 156), (310, 310), (388, 388)]


def test_a_range_verifies_when_the_quote_is_anywhere_inside_it(tmp_path):
    with sandbox(tmp_path, {"src/guard.m": BODY},
                 "See `src/guard.m:8-13` (`if isempty(subjectId)`).\n") as doc:
        c = verdicts(doc)["src/guard.m:8-13"]
    assert c.verdict == "VERIFIED", c.reason
    assert c.spans_confirmed == 1


def test_a_multi_span_citation_reports_how_many_spans_were_confirmed(tmp_path):
    """`silentLoss.m:49-56,523-526` is ONE citation with TWO spans. A span with
    no anchor is neither confirmed nor denied, and the count says so rather
    than a single verdict pretending to cover both."""
    with sandbox(tmp_path, {"src/guard.m": BODY},
                 "See `src/guard.m:10,34` (`if isempty(subjectId)`).\n") as doc:
        c = verdicts(doc)["src/guard.m:10,34"]
    assert c.verdict == "VERIFIED"
    assert c.spans_confirmed == 1
    assert len(c.spans) == 2
    assert "1/2 span(s) confirmed" in c.reason


# --------------------------------------------------------------------------
# TRANSCRIPT CITATIONS -- the strongest anchor there is
# --------------------------------------------------------------------------

def test_a_transcript_block_is_read_as_citations_with_verbatim_anchors(tmp_path):
    text = ("Positive evidence, from the file itself:\n"
            "\n"
            "        $ sed -n '10p' src/guard.m\n"
            "        10:        if isempty(subjectId)\n")
    with sandbox(tmp_path, {"src/guard.m": BODY}, text) as doc:
        got = verdicts(doc)
    c = got["src/guard.m:10"]
    assert c.kind == "transcript"
    assert c.verdict == "VERIFIED", c.reason


def test_a_stale_transcript_is_reported(tmp_path):
    """A recorded command output is a TIME-STAMPED observation. When the file
    moves under it, the block still reads like something somebody just ran."""
    text = ("Positive evidence, from the file itself:\n"
            "\n"
            "        $ sed -n '30p' src/guard.m\n"
            "        30:        if isempty(subjectId)\n")
    with sandbox(tmp_path, {"src/guard.m": BODY}, text) as doc:
        c = verdicts(doc)["src/guard.m:30"]
    assert c.verdict == "DRIFTED"
    assert c.true_lines == [10]


def test_a_transcript_naming_no_file_is_skipped_and_COUNTED(tmp_path):
    """`1: 86   2: 25` is a per-rung table, not a citation. Skipping it
    silently and skipping it while saying how often are different facts."""
    text = ("A rollup:\n"
            "\n"
            "        1: 86 satisfied independently of the rungs below\n"
            "        2: 25 satisfied independently of the rungs below\n")
    with sandbox(tmp_path, {"src/guard.m": BODY}, text) as doc:
        cites, _r, _l, orphans, _b, _u = C.run([str(doc)])
    assert cites == []
    assert orphans == 2


# --------------------------------------------------------------------------
# THE INSTRUMENT ITSELF
# --------------------------------------------------------------------------

def test_a_scan_that_extracts_nothing_EXITS_NON_ZERO(tmp_path):
    """MUTATION 3 of the brief. Narrow the scan until it matches nothing and
    the report is indistinguishable from a clean corpus: `0 drifted`. This
    repository has had a counter read clean while inspecting nothing for two
    days; a zero from an empty denominator must be a FAILURE."""
    doc = tmp_path / "EMPTY.md"
    doc.write_text("Prose with no citation in it at all.\n", encoding="utf-8")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = C.main(["--document", str(doc)])
    assert rc == 1
    assert "NOTHING WAS EXTRACTED" in buf.getvalue()
    assert buf.getvalue().startswith("DENOMINATOR:"), \
        "Rule 5: the denominator prints first and unconditionally"


def test_the_denominator_prints_first_even_when_everything_is_clean(tmp_path):
    with sandbox(tmp_path, {"src/guard.m": BODY},
                 "The guard is live at `src/guard.m:10` "
                 "(`if isempty(subjectId)`).\n") as doc:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = C.main(["--document", str(doc)])
    out = buf.getvalue()
    assert rc == 0
    assert out.startswith("DENOMINATOR: 1 document(s) globbed, 1 read,")
    for label in ("VERIFIED", "DRIFTED", "COLLISION", "DEAD",
                  "UNDECIDABLE", "UNRESOLVABLE-HERE"):
        assert label in out, f"{label} must be counted whether or not it is 0"


def test_enforce_fails_on_drift_and_the_default_does_not(tmp_path):
    """REPORT-ONLY UNTIL THE COUNT IS ZERO. `--enforce` exists and is tested;
    arming a gate onto a non-zero count trains readers to ignore the job,
    which is the call `census_digest.py` records for its four sentinels."""
    with sandbox(tmp_path, {"src/guard.m": BODY},
                 "The guard is live at `src/guard.m:30` "
                 "(`if isempty(subjectId)`).\n") as doc, \
            contextlib.redirect_stdout(io.StringIO()):
        assert C.main(["--document", str(doc)]) == 0
        assert C.main(["--document", str(doc), "--enforce"]) == 1


def test_every_citation_lands_in_exactly_one_bucket():
    """Conservation over the REAL corpus. The mutation this catches is a
    verdict quietly dropped -- a bucket filtered out of the render is a
    denominator shrinking, which is this project's signature defect."""
    cites, read, lines, _orphans, _bare, _unreadable = C.run(C.documents())
    assert read > 0 and lines > 0
    assert cites, "the real corpus carries citations; extracting none is a bug"
    for c in cites:
        assert c.verdict in C.ORDER, f"{c.cited} has verdict {c.verdict!r}"
    live = [c for c in cites if not c.historical]
    hist = [c for c in cites if c.historical]
    assert len(live) + len(hist) == len(cites)


def test_nothing_reaches_VERIFIED_without_a_named_anchor():
    """The one property that must hold over the real corpus however it changes:
    a verified citation carries the fragment that verified it, so every pass is
    auditable by hand. A resolver stubbed to accept everything cannot satisfy
    this without also fabricating an anchor."""
    cites, _r, _l, _o, _b, _u = C.run(C.documents())
    passed = [c for c in cites if c.verdict == "VERIFIED"]
    assert passed, "no citation verified at all -- the resolver is not working"
    for c in passed:
        assert c.anchor_used, f"{c.where} verified with no anchor named"
        assert len(C.norm(c.anchor_used)) >= C.MIN_ANCHOR
        assert c.resolved and c.repo, f"{c.where} verified against no file"


def test_gates_declares_this_tool_as_a_step():
    """A gate nobody runs is a comment. `gates.py` is the single entry point,
    and a tool outside it is a tool that goes stale unattended -- which is what
    this one exists to detect."""
    gates = _load("gates")
    names = {s.name for s in gates.STEPS}
    assert "check_citations" in names
    step = next(s for s in gates.STEPS if s.name == "check_citations")
    out = "DENOMINATOR: 56 document(s) globbed, 56 read, 1 line(s); ..."
    assert step.headline.search(out), \
        "the headline pattern must match the tool's real first line"
