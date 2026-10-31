#!/usr/bin/env python3
"""Generate schemas/V_eta_STATUS.md -- the single generated record of V_eta state.

WHY THIS EXISTS
---------------
V_eta state lives in 27 plan documents, a 400-line CLAUDE.md and a 52-item task
list, and no two agree. Prose cannot be checked, so it rots and is then cited:
"no session document exists anywhere", "all 0-usage, safe to delete",
"dissolved (rename/decompose)" -- each was a written claim that was wrong and
that nothing could catch.

This file replaces PROSE STATE with DERIVED STATE. The plan documents keep the
rationale (why a model was chosen -- what prose is genuinely good for); this
board owns the answer to "how much is left, and what exactly".

THE ONE PIECE OF JUDGEMENT, MADE EXPLICIT
-----------------------------------------
Which classes are DECIDED is not judged here. A class is decided if and only if
it CITES a decision line that exists -- a `TEAM-SIGN-OFF [tag]` line or a
`Decided by <team member>, <date> [<tag>]:` line in the cited document. The citations and
the resolver live in `tools/decision_citations.py`, which replaced the decision
FAMILIES table on 2026-10-21. Every open class is listed by name, decided or
not, so none can be silently dropped from the count, and a citation that does
not resolve FAILS the generator.

`in_progress` IS A DECLARATION, NOT A MEASUREMENT -- AND THAT IS THE OTHER HALF
------------------------------------------------------------------------------
Every one of the open classes is `in_progress` because a HUMAN WROTE ITS NAME in
a literal collection in `tools/build_v_eta.py`. Measured 2026-08-10, and the
denominator first:

    31 classes carry `disposition: in_progress` in the built index.json
       27 are keys of `_DECIDED_PENDING`   (a literal dict + two literal loops)
        4 are members of `_IN_PROGRESS`    (a literal set; 2 more of its 6
                                            members are deleted classes)
        0 are derived from any evidence about the work

`_disposition()` returns `in_progress` on membership alone. A class therefore
leaves the list only when a person deletes its line -- never because a migrator
landed, a test passed or a corpus went green. The count sat at 31 all day while
seven families were built, which is the SAME ONE-DIRECTIONAL BIAS this file
already records twice (the stale sign-off headers; the ledger's "dissolved
(rename/decompose)" labels): the artifact always claims LESS progress than the
record holds. It never produces a wrong build. It just makes the board unable to
answer the only question anyone asks of it.

The lines cannot simply be deleted, and the reason is a real one. For a v1
SOURCE class, flipping `in_progress -> retire` asserts that NO DOCUMENT of that
class survives migration -- the phase-8 criterion, which CLAUDE.md requires
CORPUS EVIDENCE for and which has already caught one over-eager deletion. So the
membership stays a team disposition (operating rule 4, and nothing here edits
it), and the board instead DERIVES, per open class, the two facts the
declaration cannot carry:

    (a) nothing built                 no migrator consumes it, no migrator MINTS
                                      it, no decided target schema exists
    (b) built, awaiting corpus proof  a migrator consumes it, MINTS it, and/or
                                      its decided target is built, but no census
                                      has shown 0 surviving documents
    (c) corpus-proven consumed        the last census read this class and found
                                      no document returned unchanged
    (?) UNMEASURED                    the evidence for this class was never
                                      taken -- printed as its own state, because
                                      absence of evidence is not evidence
                                      (operating rule 3)

WHAT (c) IS AND IS NOT
----------------------
(c) is EVIDENCE, never a disposition. `unconverted_by_class` counts documents a
migrator handed straight back; 0 of them is a fact about the corpora that were
read. It is NOT authority to retire a class, for two reasons that are printed
next to the number every time:

  * THE CORPORA ARE A SAMPLE OF DATASETS, NOT THE UNIVERSE (CLAUDE.md's standing
    caveat). A class absent from the six we run may be well represented in a
    dataset still waiting to migrate, which is what this migration is FOR.
  * THE REPORTS CARRY NO PER-CLASS SOURCE DENOMINATOR. `summary.by_class` counts
    OUTPUT class names, so a class that was fully consumed and a class that had
    no documents at all both come out at zero. "0 survived" and "0 existed" are
    indistinguishable from the report alone.

Usage:  python3 tools/status_board.py [--check]
                                      [--did /path/to/DID-matlab]
                                      [--ndi /path/to/NDI-matlab]
                                      [--census DIR ...]
        --check exits non-zero if the committed board is out of date.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(REPO, "schemas", "generated", "index.json")
LEDGER = os.path.join(REPO, "schemas", "generated", "did_v2_coverage_ledger.json")
OUT = os.path.join(REPO, "schemas", "V_eta_STATUS.md")
# The machine-readable twin of the board, for the schema viewer.
#
# WHY IT EXISTS. Until 2026-08-09 the decisions lived ONLY in a table in this
# file and in the sign-off lines of the plan documents, so nothing downstream
# could see them. The viewer rendered the coverage ledger, where a settled class
# shows as `in_progress` with no hint that its model is decided, signed, and
# merely awaiting a build -- which reads as UNDECIDED. That is the same
# inversion this board already names: a record that reports settled work as
# open is the mirror of one that reports open work as settled, and both make
# the remaining-work count useless. The clock alignment cluster sat unbuilt for
# a day for exactly this reason, because two pieces of prose called a signed
# decision a proposal.
#
# Generated, never hand-edited, and stale-checked in CI like the other four.
DECISIONS_OUT = os.path.join(REPO, "schemas", "generated", "did_v2_decisions.json")

# DECISIONS. A class is DECIDED if and only if it CITES a decision line that
# exists -- a `TEAM-SIGN-OFF [tag]` line or a `Decided by <team member>, <date> [<tag>]:`
# line in the cited document. The citations, the scanner and the resolver live
# in tools/decision_citations.py, which REPLACED the decision FAMILIES table that
# stood here until 2026-10-21 (Jess Haley: "nothing wrongly reported"). A class
# without a citation that resolves renders "Proposed (not decided)", whatever
# any prose says.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decision_citations as dc  # noqa: E402

SIGNOFF = dc.SIGNOFF
GENERATED_MARKDOWN = dc.GENERATED_MARKDOWN
# The one scanner, re-exported under its old name for the tools and tests that
# read it from here.
scan_signoff_lines = dc.scan_decision_lines



def load():
    with open(INDEX) as fh:
        idx = json.load(fh)
    with open(LEDGER) as fh:
        led = json.load(fh)
    return idx["schemas"], led["rows"]


# ===========================================================================
# EVIDENCE LAYER -- the part of the board that is measured rather than declared
# ===========================================================================
#
# Two external sources, each optional, each reported with its own denominator:
#
#   MIGRATOR EVIDENCE  DID-matlab `+did2/+convert/+migrators_j` (the V_eta pass)
#                      and NDI-matlab `+ndi/+migrate/+internal` (the V_eta
#                      second pass). Answers "is anything built for this class".
#   CENSUS EVIDENCE    the per-corpus `*-summary.json` reports written by
#                      did2.unittest.helpers.writeCorpusReport. Answers "do
#                      documents of this class still survive migration".
#
# Neither repo is checked out in this repo's CI, so both are SNAPSHOTTED into
# the generated `did_v2_decisions.json` and reused verbatim when the live source
# is unreachable. That keeps `--check` meaningful: a developer with the sibling
# repos re-measures, and a change in the evidence changes the committed file
# exactly like a change in the schema does. Nothing time-stamped goes into the
# snapshot -- a wall-clock field would make every run differ from every other
# and turn the staleness check into noise.

def find_repo(name, env):
    """Locate a sibling repo the same way tools/coverage.py does."""
    for cand in (os.environ.get(env), os.path.join("/home/user", name),
                 os.path.join(os.path.dirname(REPO), name)):
        if cand and os.path.isdir(cand):
            return cand
    return None


def batch_evidence_line(hits):
    """One MEASURED / REUSED / NONE line for the evidence log."""
    if hits.get("reused"):
        return (f'batch post-pass evidence: REUSED from the committed snapshot ({hits["files_scanned"]} file(s) when last measured); not read in this run -- {", ".join(hits["roots_missing"])}')
    if hits["files_scanned"]:
        return (f'batch post-pass evidence: MEASURED -- {hits["files_scanned"]} file(s) under `+did2/+convert`')
    return (f'batch post-pass evidence: NONE -- 0 file(s) read and no usable snapshot ({", ".join(hits["roots_missing"]) or "no root given"}). Every \'passes through\' row is UNMEASURED, not clean.')


def batch_consumers(classes, didm, snapshot_key="batch_consumers"):
    """Which BATCH POST-PASSES name each of `classes`, by bare quoted literal.

    WHY IT EXISTS. The ledger's `migrator` column means one thing only: a file
    in `+migrators_j` / `+migrators` / `+migrators_i` is NAMED after this class.
    The board then printed "so the documents pass through untouched today",
    which is a different and stronger claim -- and on 2026-08-11 it was false
    for `generic_file`: `+did2/+convert/foldGenericFiles.m` folds it into a
    `term_observation` + an `opaque_body` (carrying `content_hash` from
    `checksum`), a batch post-pass with no per-class file to be named after.
    Absence in one directory, reported as absence everywhere.

    DELIBERATELY NARROW. It is run ONLY over the handful of rows the board is
    about to describe, never over all 102 -- a bare-name sweep across the whole
    ledger matches `'base'` in eight files and `'app'` in one, and a
    false-positive rate like that turns the instrument into noise. Over a
    candidate set of one or two named classes it is exact and checkable.

    The match is the BARE CLASS NAME as a quoted literal, per this project's own
    rule: the construction idiom is not uniform (`ndi.document('valid_interval')`
    finds nothing because `markgarbage` uses `session.newdocument`), so a search
    keyed on one call shape reports absence that is a property of the query.

    Returns {"files_scanned": n, "roots_missing": [...], "by_class": {cls: [files]},
             "reused": bool}.

    IT REACHED PAST `--did` AND THAT MADE THE BOARD PERMANENTLY STALE ON A
    RUNNER. Until 2026-08-11 this called `find_repo` directly, so the `--did`
    the rest of the tool honours was ignored -- which is why pointing both
    siblings at a path that does not exist reproduced NOTHING locally while CI
    reported `V_eta_STATUS.md DIFFERS -- 4 changed line(s)` on three
    consecutive runs. The local "reproduction" was quietly reading the real
    DID-matlab.

    The second half is worse than a wrong path. Every other figure on the board
    falls back to the committed snapshot when the sibling is absent, and this
    one did not: it rendered `0 batch post-pass file(s)` against a committed
    `10`, so the artifact could NEVER be current on a machine without
    DID-matlab. A generated file that is unconditionally stale in CI is a gate
    that fails every run, which is a gate people stop reading -- the same cost
    as `0f34485` earlier the same day.

    So the snapshot is now the fallback here too, and it is ANNOUNCED
    (`reused`) rather than passed off as a measurement.
    """
    base = os.path.join(didm or "", "src/did/+did2/+convert")
    out = {"files_scanned": 0, "roots_missing": [], "by_class": {}, "reused": False}
    if not didm or not os.path.isdir(base):
        out["roots_missing"].append(base or "DID-matlab (not given)")
        prior = (committed_snapshot().get("sources", {}) or {}).get(snapshot_key)
        if prior and not prior.get("reused"):
            # Only a MEASURED snapshot is worth reusing. Reusing a reused one
            # would let a single sibling-less run freeze the figure forever
            # with nothing in the output saying when it was last real.
            out["files_scanned"] = prior.get("files_scanned", 0)
            out["by_class"] = {c: v for c, v in (prior.get("by_class") or {}).items()
                               if c in set(classes)}
            out["reused"] = True
        return out
    # The per-class migrator packages are excluded: a hit there is the
    # `migrator` column's business and would double-count. `universalRenames`
    # and the drivers are excluded because they enumerate every class by
    # construction and would match everything.
    skip_dirs = {"+migrators", "+migrators_i", "+migrators_e", "+migrators_j"}
    skip_files = {"Contents.m", "universalRenames.m", "v1_to_v2.m",
                  "fromV1Database.m", "calcCommon.m"}
    texts = {}
    for name in sorted(os.listdir(base)):
        if name in skip_dirs or not name.endswith(".m") or name in skip_files:
            continue
        with open(os.path.join(base, name)) as fh:
            texts[name] = "\n".join(ln.split("%")[0] for ln in fh.read().splitlines())
    out["files_scanned"] = len(texts)
    for cls in classes:
        pat = re.compile(rf"'{re.escape(cls)}'")
        hit = sorted(n for n, t in texts.items() if pat.search(t))
        if hit:
            out["by_class"][cls] = hit
    return out


_IDENT = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")
# After one of these, a `'` is the TRANSPOSE operator, not the start of a string.
_TRANSPOSE_AFTER = _IDENT | set(")]}.'")


def split_matlab_line(line):
    """Split one MATLAB line into (code with strings blanked, [string literals]).

    WHY BOTH HALVES ARE NEEDED, AND WHY THEY MUST NOT BE SEARCHED TOGETHER.
    A class is consumed in one of two spellings:

        isfield(preBody, 'app')      a QUOTED NAME  -> search the literals
        blk = preBody.filter;        a FIELD ACCESS -> search the code

    Searching the raw text for `.app` finds it inside the string literal
    'ndi.app.stimulus.tuning_response' (stimulus_response_scalar.m:210), which
    is a MATLAB function path and has nothing to do with the `app` class. Two
    of the six shortest open class names collide that way, so the split is not
    a nicety.

    Comments are dropped -- a `%` outside a string, and the `...` continuation
    marker. THIS MATTERS IN THE OTHER DIRECTION TOO: +migrators_j documents its
    reasoning at length, and every migrator that mentions a class it does NOT
    touch mentions it in a comment. Counting those would report unbuilt work as
    built, which is the failure this whole board exists to prevent.

    KNOWN LIMIT: the transpose/quote disambiguation is a heuristic (a `'` after
    an identifier, `)`, `]`, `}`, `.` or `'` is read as transpose). It is the
    same heuristic every MATLAB syntax highlighter uses and it can be fooled by
    exotic lines; it cannot be fooled by anything in +migrators_j today.
    """
    out, lits = [], []
    i, n, prev = 0, len(line), ""
    while i < n:
        ch = line[i]
        if ch == "%":
            break
        if line.startswith("...", i):
            break
        if ch in "'\"" and not (ch == "'" and prev in _TRANSPOSE_AFTER):
            j, buf = i + 1, []
            while j < n:
                if line[j] == ch:
                    if j + 1 < n and line[j + 1] == ch:   # doubled = escaped
                        buf.append(ch)
                        j += 2
                        continue
                    break
                buf.append(line[j])
                j += 1
            lits.append(("".join(buf), i))
            out.append(" " * (j - i + 1))
            i, prev = j + 1, ch
            continue
        out.append(ch)
        if not ch.isspace():
            prev = ch
        i += 1
    return "".join(out), lits


# ===========================================================================
# EMISSION -- "a migrator BUILDS a document of this class"
# ===========================================================================
#
# WHY THIS EXISTS. Until 2026-08-10 the build signal could see a class only
# through the SOURCE side: a migrator file NAMED after it, an `isfield(preBody,
# '<class>')` guard, a read of `preBody.<class>`. Every one of those asks "does
# something consume this v1 block". None of them can see a V_eta TARGET that is
# MINTED by a migrator named after its v1 source, and that is a whole category:
#
#     control_designation   built, and rendered "(a) decided, nothing built".
#                           `migrators_j/control_stimulus_ids.m:111` is
#                           `v2Body.document_class = struct('class_name',
#                           'control_designation', ...)` -- the v1 source is
#                           `control_stimulus_ids`, the V_eta target is the
#                           renamed `control_designation`, and no file is or
#                           should be named after the target.
#
# The undercount is the same shape as the private-helper one `migrator_evidence`
# already documents (`app`, `filter`), one step further out: there the file name
# was the wrong key for a v1 SUPERCLASS BLOCK, here it is the wrong key for a
# V_eta TARGET. Both err in the reassuring-in-the-other-direction way this repo
# keeps hitting -- the artifact claims LESS progress than the record holds.
#
# THE PATTERNS ARE IMPORTED FROM tools/coverage.py, NOT RE-WRITTEN. coverage.py's
# guardrail already extracts every `'class_name', '<X>'` a V_eta migrator emits
# ("40 emitted class_names checked against V_eta schema"). A second regex here
# would be a second thing to keep in step with the migrators, and the two would
# disagree silently -- which is how this project produced two contradicting
# hand-maintained records of `dataseries_channel_map`.
#
# WHAT IS ADDED ON TOP OF coverage.py, AND WHY IT IS NOT DIVERGENCE. coverage.py
# needs a SUPERSET: its question is "does every class name this code writes down
# exist in the schema", and for that a superclass entry counts exactly as much as
# a document class. This board needs the narrower fact "a document OF THIS CLASS
# is produced", so two filters are applied to the same patterns:
#
#   * COMMENTS ARE DROPPED. +migrators_j documents its ground truth at length and
#     quotes NDI templates verbatim; counting a quoted class name as an emission
#     would report unbuilt work as built.
#   * SUPERCLASS ENTRIES ARE DROPPED. A `document_class` struct carries the
#     document's own `class_name` AND a `superclasses` array of more
#     `class_name`s. Measured on the 132 migrator files: coverage.py's raw sweep
#     reports 42 distinct names, of which 29 are document classes -- and the 13
#     it conflates include `time_reference` and `epochid`, both of which are
#     emitted ONLY as superclasses of something else and both of which are open
#     classes. Counting those would have moved two classes to "built" on the
#     strength of a superclass mixin.
#
# MATLAB continuation lines make this a STATEMENT-level question, not a
# line-level one: `stimulusBathToBath.m:68-75` spells one `document_class` struct
# across eight physical lines, with `'superclasses'` on line 71 and
# `'time_reference'` on line 72. A per-line rule reads line 72 as a document
# class. So statements are joined first, and the split is by POSITION within the
# joined statement.

def _coverage_class_emit_patterns():
    """`tools/coverage.py`'s `'class_name', '<X>'` patterns, imported.

    Loaded by path rather than by `import coverage`, because `coverage` is also
    a widely installed PyPI package and this file is exec'd by the test suite
    with an arbitrary sys.path. Failure is deliberately LOUD: falling back to a
    local copy of the regex is exactly the silent divergence this reuse exists
    to prevent.
    """
    import importlib.util
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "coverage.py")
    spec = importlib.util.spec_from_file_location(
        "_status_board_coverage_patterns", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return list(mod._CLASS_EMIT)


CLASS_EMIT = _coverage_class_emit_patterns()


def _coverage_supersession():
    """coverage.py's table of names the 2026-10-08 composition (signed) retired,
    imported for the same reason as CLASS_EMIT: one table, never two."""
    import importlib.util
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "coverage.py")
    spec = importlib.util.spec_from_file_location("_status_board_coverage_sup", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return dict(mod.SUPERSEDED_BY_ENTITY_COMPOSITION)


SUPERSEDED = _coverage_supersession()


def _coverage_module():
    import importlib.util
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "coverage.py")
    spec = importlib.util.spec_from_file_location("_status_board_coverage_keys", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# coverage.py's #88 target spelling (`observation + intensity`), imported for the
# same reason as CLASS_EMIT: one definition of what two spellings agree on.
_COV = _coverage_module()
compose_target = _COV.compose_target
target_key = _COV.target_key


def _target_built(name, built_classes):
    return all(x in built_classes for x in _COV.target_parts(name, built_classes))


def code_before_comment(line):
    """(the line up to its comment/continuation, does it continue?).

    Strings are left INTACT -- unlike `split_matlab_line`'s first return value,
    which blanks them, because the emission patterns match string literals. The
    cut point is taken from `split_matlab_line` rather than recomputed: that
    function already owns the transpose-versus-quote heuristic, and a second
    walk over the line would be a second place for it to be wrong.
    """
    code, _lits = split_matlab_line(line)
    n = len(code)
    return line[:n], line[n:].lstrip().startswith("...")


def logical_statements(lines):
    """Yield (text, spans) per MATLAB statement, continuations joined.

    `spans` is [(offset_in_text, physical_line_no)] so a match inside the joined
    text can be reported at the line a human will find it on. Comments and block
    comments are gone before anything is joined.
    """
    out, buf, spans = [], [], []
    in_block = False
    for lno, line in enumerate(lines, 1):
        s = line.strip()
        if in_block:
            if s == "%}":
                in_block = False
            continue
        if s == "%{":
            in_block = True
            continue
        piece, cont = code_before_comment(line)
        spans.append((sum(len(b) for b in buf), lno))
        buf.append(piece)
        if cont:
            continue
        text = "".join(buf)
        if text.strip():
            out.append((text, spans))
        buf, spans = [], []
    text = "".join(buf)
    if text.strip():
        out.append((text, spans))
    return out


def _line_of(spans, offset):
    lno = spans[0][1] if spans else 0
    for start, n in spans:
        if start <= offset:
            lno = n
        else:
            break
    return lno


# THREE MINT IDIOMS, NOT ONE -- and for four months this function knew about
# one of them.
#
# The docstring below used to say "every one of the 29 document-class emissions
# is written as `<body>.document_class = struct(...)`". Measured on the same
# files on 2026-08-11, that is 45 of the 62 `document_class` WRITES; the other
# 17 are two idioms a `'class_name'`-comma regex cannot see:
#
#   IDIOM 2  obs.document_class = classBlock('score_observation', {...})
#            `classBlock` is a LOCAL SUBFUNCTION, redefined in 8 files with two
#            different arities, which returns the struct. Nothing in the call
#            statement says `class_name` at all.
#   IDIOM 3  v2Body.document_class.class_name = 'acquisition_epoch';
#            The field write. Again no `'class_name', '<X>'` comma pair.
#
# THE COST WAS NOT HYPOTHETICAL. `session_relative_reference` -- a class whose
# whole open question is that it must STOP being emitted -- renders its mint
# count. With idiom 1 alone that count is 3. The real number is 9: six migrators
# (fitcurve, image_stack, jrclust_clusters, neuron_extracellular, pyraview,
# vmspikefit) mint it through `classBlock`. The board reported a THIRD of the
# outstanding work, in this repo's characteristic direction -- less left to do
# than there is. The six missed mints were not dropped; they were filed as
# `named`, i.e. as the weakest possible evidence, which is worse than dropping
# them because it looks like a measurement.
#
# IDIOM 2 IS RESOLVED FROM THE HELPER'S OWN SOURCE, NOT FROM ITS NAME. Nothing
# here knows the string "classBlock". A local function qualifies when its body
# assigns ITS OWN OUTPUT a struct that declares `superclasses` and takes its
# `class_name` from one of its PARAMETERS -- that is what a class block is, and
# nothing else in these packages does it. The parameter's INDEX is what is
# recorded, so the literal is read from the right argument at the call site and
# the superclass list (argument 2) cannot be mistaken for a mint. A helper that
# gains an argument, or is renamed, or is copied into a ninth file, is handled
# without an edit here; a hard-coded name would have to be chased.
#
# WHAT STILL CANNOT BE SEEN, STATED SO THE COUNT IS READ AS A FLOOR. When the
# class name is a VARIABLE -- `struct('class_name', leafClass, ...)`,
# `classBlock(e.class, ...)` -- the literal lives at a call site in another
# function and resolving it needs the CALL GRAPH. That is a real analysis and it
# already exists in `tools/refresh_migration_targets.py`, which walks from each
# migrator entry point through `private/` helpers substituting arguments for
# parameters. This function is deliberately the narrower, per-file one, so it
# reports those sites as UNRESOLVED and counts them, rather than passing over
# them in silence. Six such sites exist today and they are named in the board's
# own denominator table.
_DC_CLASS_NAME_WRITE = re.compile(r"document_class\s*\.\s*class_name\s*$")
# `'class_name', <bare identifier>` -- the value is a VARIABLE, so the literal is
# somewhere else. Deliberately separate from coverage.py's `CLASS_EMIT`, which
# matches only quoted values.
_SYMBOLIC_CLASS_NAME = re.compile(
    r"""['"]class_name['"]\s*,\s*([A-Za-z_]\w*(?:\.\w+)*)""")
_SINGLE_LITERAL = re.compile(r"^\s*'((?:[^']|'')*)'\s*;?\s*$")
_CALL_HEAD = re.compile(r"^\s*([A-Za-z_]\w*)\s*\(")
_FUNCTION_HEAD = re.compile(
    r"^\s*function\s+"
    r"(?:\[(?P<outs>[^\]]*)\]\s*=\s*|(?P<out1>[A-Za-z_]\w*)\s*=\s*)?"
    r"(?P<name>[A-Za-z_]\w*)\s*(?:\((?P<args>[^)]*)\))?")


def class_block_helpers(lines):
    """{local function name: index of its class-name PARAMETER}.

    A CLASS BLOCK HELPER is recognised by what it does, never by its name: it
    assigns its own output variable a struct that declares `superclasses` and
    whose `class_name` value is one of the function's own parameters. See the
    block comment above for why the shape and not the name.
    """
    heads = []
    in_block = False
    for i, line in enumerate(lines):
        s = line.strip()
        if in_block:
            if s == "%}":
                in_block = False
            continue
        if s == "%{":
            in_block = True
            continue
        if not s.startswith("function"):
            continue
        m = _FUNCTION_HEAD.match(line)
        if m:
            heads.append((i, m))
    out = {}
    for k, (i, m) in enumerate(heads):
        end = heads[k + 1][0] if k + 1 < len(heads) else len(lines)
        args = (m.group("args") or "").strip()
        params = [a.strip() for a in args.split(",") if a.strip()]
        outs = [o.strip()
                for o in (m.group("outs") or m.group("out1") or "").split(",")
                if o.strip()]
        if not params or not outs:
            continue
        for text, _spans in logical_statements(lines[i:end]):
            code, _lits = split_matlab_line(text)
            eq = assignment_split(code)
            if eq is None or text[:eq].strip() not in outs:
                continue
            rhs = text[eq + 1:]
            if "superclasses" not in rhs:
                continue
            cut = rhs.find("superclasses")
            for sm in _SYMBOLIC_CLASS_NAME.finditer(rhs[:cut]):
                if sm.group(1) in params:
                    out[m.group("name")] = params.index(sm.group(1))
    return out


def _top_level_args(text, code, open_paren):
    """Positional argument source strings of the call whose `(` is at
    `open_paren`. Depth is taken from `code` (strings blanked, same length as
    `text`) so a comma inside a literal cannot split an argument."""
    depth, start, args = 0, open_paren + 1, []
    for i in range(open_paren, len(code)):
        ch = code[i]
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
            if depth == 0:
                args.append((start, text[start:i]))
                return args
        elif ch == "," and depth == 1:
            args.append((start, text[start:i]))
            start = i + 1
    return args


# ---------------------------------------------------------------------------
# IDIOMS 4 AND 5 -- THE #88 BUILDER (DID-matlab #218, the migrator port)
# ---------------------------------------------------------------------------
# The port to did-schema #88 (merged into DID-matlab #218 at 229c12e) replaced
# all three idioms above in the per-document migrators with calls into
# `did2.build`, which reads the class, its blocks and its edges from the schema:
#
#   IDIOM 4  did2.build.statement('observation', ..., 'ValueKind', 'intensity')
#            did2.build.document('entity', ...)
#            did2.build.relativeTimeReference(...)   (and the other builders
#            named in BUILDER_FIXED_CLASS, each of which mints one fixed class)
#   IDIOM 5  jStatement(preBody, 'manipulation', ..., 'ValueKind', 'dose')
#            -- a WRAPPER: a function whose body passes one of its own
#            PARAMETERS as the class of a did2.build.statement/document call.
#            Recognised by that shape, never by its name (as idiom 2 is).
#
# A statement's IDENTITY on #88 is its direction plus its value kind, so the
# class recorded is coverage.py's `compose_target` spelling
# (`manipulation + dose`). did2.build also accepts the older leaf name
# (`'intensity_observation'`, +did2/+build/private/resolveLeaf.m) and builds
# the same document, so a leaf name composes to the same spelling.
#
# The old idioms are still recognised: older trees (the `v_eta-pre73` pin)
# mint that way, and NDI's second pass still does.
BUILDER_CALL = re.compile(r"(?<![\w.])did2\.build\.([A-Za-z_]\w*)\s*\(")
# The builders whose class is their first argument.
BUILDER_CLASS_ARG = ("statement", "document")
# The builders that mint ONE fixed class: the literal is the first argument of
# `forward(...)` in DID-matlab +did2/+build/<builder>.m
# (tests/test_status_board_evidence.py checks this table against those files).
# `method` reads its class from the schema (`methodShape(...).docClass`):
# `method` on #88, `method_parameters` before it.
BUILDER_FIXED_CLASS = {
    "relativeTimeReference": "relative_time_reference",
    "absoluteTimeReference": "absolute_time_reference",
    "sampledBody": "sampled_body",
    "opaqueBody": "opaque_body",
    "directedRelation": "directed_relation",
    "undirectedRelation": "undirected_relation",
    "method": "method",
}
VALUE_KIND_OPTION = "ValueKind"
_ANY_CALL = re.compile(r"(?<![\w.])([A-Za-z_]\w*)\s*\(")


def builder_call_args(text, code, open_paren):
    """[(start, source)] of a call's top-level arguments; see `_top_level_args`."""
    return _top_level_args(text, code, open_paren)


def value_kind_arg(args):
    """(start, source) of the argument after a literal `'ValueKind'`, or None."""
    for i, (_st, src) in enumerate(args):
        lm = _SINGLE_LITERAL.match(src)
        if lm and lm.group(1) == VALUE_KIND_OPTION and i + 1 < len(args):
            return args[i + 1]
    return None


def has_splat(args):
    """True when an argument is `x{:}` -- options forwarded from elsewhere."""
    return any(src.strip().endswith("{:}") for _st, src in args)


def builder_wrappers(lines, known=None):
    """{function name: (class PARAMETER index, kind spec)} for wrappers in `lines`.

    A WRAPPER passes one of its own parameters as the class of a
    `did2.build.statement` / `did2.build.document` call (`jStatement`), or of
    a call to a wrapper already `known` (`jCalculation` -> `jStatement`; the
    caller iterates to a fixed point). The
    kind spec says where its value kind comes from: ('param', i) when the
    `'ValueKind'` option is one of its parameters, ('varargin',) when it
    forwards its `varargin` (the caller's `'ValueKind', <x>` pair), or None.
    """
    heads = []
    in_block = False
    for i, line in enumerate(lines):
        s = line.strip()
        if in_block:
            if s == "%}":
                in_block = False
            continue
        if s == "%{":
            in_block = True
            continue
        if not s.startswith("function"):
            continue
        m = _FUNCTION_HEAD.match(line)
        if m:
            heads.append((i, m))
    out = {}
    for k, (i, m) in enumerate(heads):
        end = heads[k + 1][0] if k + 1 < len(heads) else len(lines)
        params = [a.strip() for a in (m.group("args") or "").split(",")
                  if a.strip()]
        if not params:
            continue
        for text, _spans in logical_statements(lines[i + 1:end]):
            code, _lits = split_matlab_line(text)
            calls = [(bm, 0, ("varargin",))
                     for bm in BUILDER_CALL.finditer(code)
                     if bm.group(1) in BUILDER_CLASS_ARG]
            for wm in _ANY_CALL.finditer(code):
                if known and wm.group(1) in known:
                    calls.append((wm,) + tuple(known[wm.group(1)]))
            for bm, cls_idx, inner_kind in calls:
                args = builder_call_args(text, code, bm.end() - 1)
                if len(args) <= cls_idx:
                    continue
                cls_src = args[cls_idx][1].strip()
                if cls_src not in params:
                    continue
                kind = None
                kv = (value_kind_arg(args[cls_idx + 1:])
                      if inner_kind and inner_kind[0] == "varargin" else
                      (args[inner_kind[1]] if inner_kind
                       and inner_kind[1] < len(args) else None))
                if kv and kv[1].strip() in params:
                    kind = ("param", params.index(kv[1].strip()))
                elif kv is None and has_splat(args) and "varargin" in params:
                    kind = ("varargin",)
                out[m.group("name")] = (params.index(cls_src), kind)
    return out


def collect_builder_wrappers(paths):
    """`builder_wrappers` over many files, to a fixed point (wrappers of
    wrappers: `jCalculation` passes its class to `jStatement`)."""
    texts = []
    for path in paths:
        try:
            with open(path, errors="replace") as fh:
                texts.append(fh.readlines())
        except OSError:
            continue
    wrappers = {}
    while True:
        before = dict(wrappers)
        for lines in texts:
            wrappers.update(builder_wrappers(lines, before))
        if wrappers == before:
            return wrappers


def _function_params(lines):
    """Every parameter name of every function in `lines`."""
    out = set()
    for line in lines:
        if not line.lstrip().startswith("function"):
            continue
        m = _FUNCTION_HEAD.match(line)
        if m:
            out |= {a.strip() for a in (m.group("args") or "").split(",")
                    if a.strip()}
    return out


def _builder_mints(text, spans, wrappers, params, found, unresolved, tally):
    """Idioms 4 and 5 for one joined statement (see the block comment above)."""
    code, _lits = split_matlab_line(text)
    if code.lstrip().startswith("function"):
        return

    def _one(args, cls_arg, kind_arg, idiom):
        st, src = cls_arg
        lm = _SINGLE_LITERAL.match(src)
        line = _line_of(spans, st)
        if not lm:
            # A class passed in from a PARAMETER is a wrapper's body: the class
            # is named at the wrapper's call site (idiom 5), not here.
            if src.strip() not in params and unresolved is not None:
                unresolved.append((line, src.strip()[:80]))
            return
        kind = None
        if kind_arg is not None:
            km = _SINGLE_LITERAL.match(kind_arg[1])
            if not km:
                if unresolved is not None:
                    unresolved.append((line, f"{lm.group(1)} + {kind_arg[1].strip()[:60]}"))
                return
            kind = km.group(1)
        found.add((compose_target(lm.group(1), kind), line))
        tally(idiom)

    for bm in BUILDER_CALL.finditer(code):
        name = bm.group(1)
        if name in BUILDER_FIXED_CLASS:
            found.add((BUILDER_FIXED_CLASS[name], _line_of(spans, bm.start())))
            tally(4)
            continue
        if name not in BUILDER_CLASS_ARG:
            continue
        args = builder_call_args(text, code, bm.end() - 1)
        if args:
            _one(args, args[0], value_kind_arg(args), 4)
    for wm in _ANY_CALL.finditer(code):
        spec = wrappers.get(wm.group(1))
        if spec is None:
            continue
        idx, kind_spec = spec
        args = builder_call_args(text, code, wm.end() - 1)
        if idx >= len(args):
            if unresolved is not None:
                unresolved.append((_line_of(spans, wm.start()),
                                   f"{wm.group(1)}(...) omits its class argument"))
            continue
        if kind_spec and kind_spec[0] == "param":
            kind_arg = args[kind_spec[1]] if kind_spec[1] < len(args) else None
        elif kind_spec:
            kind_arg = value_kind_arg(args[idx + 1:])
        else:
            kind_arg = None
        _one(args, args[idx], kind_arg, 5)


def emitted_document_classes(lines, unresolved=None, idioms=None, wrappers=None):
    """{(class_name, physical_line_no)} -- documents this file MINTS.

    Three idioms are recognised (see the block comment above). In every one, a
    match counts only when it is the class of a document being BUILT and not one
    of that document's ancestors:

      1. `<body>.document_class = struct('class_name', '<X>', ...)` -- the
         literal must appear AFTER the word `document_class` and BEFORE the word
         `superclasses` within its own joined statement. MATLAB continuations
         make this a statement-level question: `stimulusBathToBath.m:136-141`
         spells one such struct over six physical lines with `'superclasses'` on
         line 138, and a per-line rule reads line 139 as a document class.
      2. `<body>.document_class = <helper>('<X>', ...)` where `<helper>` is a
         local class-block function -- the literal is read from the argument at
         that helper's own class-name parameter INDEX, so the superclass
         argument beside it cannot be mistaken for a mint.
      3. `<body>.document_class.class_name = '<X>';`
      4. `did2.build.statement('<direction>', ..., 'ValueKind', '<kind>')`,
         `did2.build.document('<X>', ...)` and the fixed-class builders
         (`BUILDER_FIXED_CLASS`) -- the #88 port. A statement is recorded as
         `compose_target(<class>, <kind>)`: `observation + intensity`.
      5. a call to a WRAPPER of idiom 4 (`jStatement(preBody, '<X>', ...,
         'ValueKind', '<kind>')`), found by shape in `lines` or passed in as
         `wrappers` ({name: spec} from `builder_wrappers`) when the wrapper
         lives in another file (a `private/` helper).

    `unresolved`, if given a list, collects `(physical_line_no, expression)` for
    every `document_class` write whose class name is a VARIABLE. Those are mints
    this per-file analysis cannot name; they are counted and reported, never
    dropped. `idioms`, if given a dict, is tallied per idiom number so the
    artifact can state how many sites each shape accounts for instead of
    carrying a hand-written figure that goes stale.
    """
    def _tally(n):
        if idioms is not None:
            idioms[n] = idioms.get(n, 0) + 1
    found = set()
    helpers = class_block_helpers(lines)
    wrap = dict(wrappers or {})
    while True:
        local = builder_wrappers(lines, wrap)
        if all(wrap.get(k) == v for k, v in local.items()):
            break
        wrap.update(local)
    params = _function_params(lines)
    for text, spans in logical_statements(lines):
        _builder_mints(text, spans, wrap, params, found, unresolved, _tally)
        anchor = text.find("document_class")
        if anchor < 0:
            continue
        code, _lits = split_matlab_line(text)
        eq = assignment_split(code)
        lhs = text[:eq] if eq is not None else ""
        rhs_off = (eq + 1) if eq is not None else 0
        hit = False

        # IDIOM 3 -- the field write. Checked first: its LHS also contains the
        # word `document_class`, so idiom 1's window would otherwise open on it.
        if _DC_CLASS_NAME_WRITE.search(lhs.rstrip()):
            rhs = text[rhs_off:]
            lm = _SINGLE_LITERAL.match(rhs)
            line = _line_of(spans, rhs_off)
            if lm:
                found.add((lm.group(1), line))
                _tally(3)
            elif unresolved is not None:
                unresolved.append((line, rhs.strip()[:80]))
            continue

        # IDIOM 1 -- the struct literal. Unchanged, including the anchor rule,
        # so nothing this function already saw can stop being seen.
        cut = text.find("superclasses")
        for pat in CLASS_EMIT:
            for m in pat.finditer(text):
                if m.start() < anchor:
                    continue
                if cut != -1 and m.start() > cut:
                    continue
                found.add((m.group(1), _line_of(spans, m.start())))
                _tally(1)
                hit = True

        # IDIOM 2 -- the local class-block helper.
        if "document_class" in lhs:
            cm = _CALL_HEAD.match(text[rhs_off:])
            if cm and cm.group(1) in helpers:
                idx = helpers[cm.group(1)]
                args = _top_level_args(text[rhs_off:], code[rhs_off:],
                                       cm.end() - 1)
                if idx < len(args):
                    start, src = args[idx]
                    lm = _SINGLE_LITERAL.match(src)
                    line = _line_of(spans, rhs_off + start)
                    if lm:
                        found.add((lm.group(1), line))
                        _tally(2)
                        hit = True
                    elif unresolved is not None:
                        unresolved.append((line, src.strip()[:80]))
                        hit = True

        # A `document_class` write whose class name resolved to nothing is a
        # mint this analysis cannot name. Rule 3: that is not a zero.
        if not hit and unresolved is not None and "document_class" in lhs:
            window = text[rhs_off:cut if cut != -1 else len(text)]
            for sm in _SYMBOLIC_CLASS_NAME.finditer(window):
                unresolved.append((_line_of(spans, rhs_off + sm.start()),
                                   sm.group(1)))
    return found


def assignment_split(code):
    """Column of the top-level `=` in a MATLAB statement, or None.

    Used to tell a READ from a WRITE, which is the difference between a migrator
    CONSUMING a class and a migrator EMITTING one -- see `REF_KINDS`. Skips
    ==, ~=, <= and >=, and anything inside brackets (so `f(a==b)` and
    `s.x(i) = 1` both read correctly).
    """
    depth = 0
    for i, ch in enumerate(code):
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        elif ch == "=" and depth == 0:
            if i + 1 < len(code) and code[i + 1] == "=":
                continue
            if i and code[i - 1] in "=~<>":
                continue
            return i
    return None


# WHY A REFERENCE'S KIND DECIDES WHETHER IT COUNTS.
#
# The first draft of this scan counted any mention, and it promoted classes in
# the REASSURING DIRECTION -- the exact bias this board exists to remove. Two
# live examples from the first run:
#
#   `directory`  matched jSorterOutput.m:77, which is
#                `body.opaque_body = struct('format', 'directory', ...)`.
#                That is a FORMAT VALUE, not the class. `directory` has nothing
#                built and was rendered as built.
#   `session_relative_reference`
#                matched 18 lines, every one of them a migrator EMITTING the
#                class (fitcurve.m:139 `classBlock('session_relative_reference',
#                {'time_reference'})`, then `anchor.session_relative_reference =
#                struct(...)`). The open work on that class is its COLLAPSE into
#                `relative_time_reference`; a migrator still writing the old class is
#                evidence the collapse has NOT landed, and counting it as
#                "built" inverted the meaning of the number.
#
# So a reference is classified, and only CONSUMPTION counts toward (b):
#
#   guard       `isfield(preBody, 'app')`        the migrator tests for the block
#               `strcmp(classNameOf(s),'ensemble')`  ... or dispatches on the class
#   field_read  `blk = preBody.filter;`          the migrator reads the block
#   field_write `anchor.time_reference = ...`    the migrator WRITES this class
#   named       `classBlock('x'), 'format','x'`  the name appears, nothing more
#
# `field_write` and `named` are still reported per class -- a fact about an open
# class that is deliberately unflattering -- they just do not make it (b).
#
# THEY ARE REPORTED SEPARATELY, EACH WITH ITS OWN COUNT, AND THAT IS THE POINT.
# Until 2026-08-11 the artifact summed them into one cell captioned "still
# emitted/named at N site(s)". `session_relative_reference`'s N was 15 and it was
# SIX MISSED MINTS plus NINE field writes -- three unlike facts wearing one
# number. Anyone reading it had no way to tell an outstanding emission from a
# block write, and the number was quoted onwards as though it were one kind of
# thing. A summed count of unlike categories is not a measurement; it is the
# shape of a measurement.
#
# `comment_mention` IS A SIXTH KIND, AND IT COUNTS TOWARD NOTHING AT ALL.
# Comments have always been dropped by `split_matlab_line` before this scan sees
# a line, so they have never inflated a count -- but "they are not in there" was
# a claim a reader had to take on trust, and this project does not run on trust.
# Counting them EXPLICITLY, in their own column, makes the claim checkable from
# the artifact: +migrators_j mentions `session_relative_reference` in 16 comments
# and every one of them is visible, in the column that counts toward nothing.
#
# THE GUARD LIST IS NOT COSMETIC. Its first version held only isfield/isstruct
# and missed the SECOND PASS entirely: an NDI assembler selects its input with
# `if ~strcmp(classNameOf(s), 'ensemble'); continue; end`
# (ensembleMembership.m:227), which is the whole ensemble consumer and was being
# filed as a bare mention. A comparison names what the code is LOOKING FOR; an
# assignment names what it PRODUCES.
#
# `emitted_class` IS THE FIFTH KIND, ADDED 2026-08-10, and it is the only one
# that is evidence about a V_eta TARGET rather than about a v1 source:
#
#   emitted_class  `b.document_class = struct('class_name','x', ...)`
#                  the migrator MINTS a document of this class
#
# It was previously swept up as `named` -- indistinguishable from
# `struct('format','directory', ...)` -- which is why `control_designation`
# rendered as "(a) decided, nothing built" while control_stimulus_ids.m:111 was
# building it. Whether it counts as BUILD PROGRESS is decided per class, in
# `RETIRED_BY_ITS_OWN_DECISION` below, and NOT here: for a class whose signed
# decision is that it stops existing, an emission means the opposite.
GUARD_FUNCS = ("isfield", "isstruct", "strcmp", "strcmpi", "ismember", "matches")
CONSUMING_KINDS = ("guard", "field_read")
EMITTED_CLASS_KIND = "emitted_class"
COMMENT_KIND = "comment_mention"
REF_KINDS = ("guard", "field_read", "field_write", "named", COMMENT_KIND,
             EMITTED_CLASS_KIND)
# Kinds that are evidence about CODE. `comment_mention` is prose and is excluded
# from every count that means anything; it is carried so its absence from those
# counts can be checked rather than believed.
CODE_KINDS = tuple(k for k in REF_KINDS if k != COMMENT_KIND)


def scan_matlab_file(path, patterns, unresolved=None, idioms=None, wrappers=None):
    """Return ({class: [(line_no, kind)]}, n_lines) for one .m file.

    `unresolved`, if given a list, collects `(line_no, expression)` for every
    `document_class` write whose class name is a variable this per-file analysis
    cannot resolve to a literal -- mints that are real and unnamed, not absent.
    """
    hits, in_block = {}, False
    try:
        with open(path, errors="replace") as fh:
            lines = fh.readlines()
    except OSError:
        return hits, 0
    # Statement-level, so it is computed over the whole file before the
    # line-level sweep below can mis-file one of its hits as `named`.
    emissions = emitted_document_classes(lines, unresolved, idioms, wrappers)
    # Matched by TARGET KEY: a queried leaf name and the `direction + kind`
    # the builder idioms record are one class spelled two ways.
    emission_keys = {(target_key(c), ln) for c, ln in emissions}
    word = {cls: re.compile(r"(?<![\w])" + re.escape(cls) + r"(?![\w])")
            for cls in patterns}
    for lno, line in enumerate(lines, 1):
        s = line.strip()
        if in_block:
            if s == "%}":
                in_block = False
            else:
                for cls, wrx in word.items():
                    if wrx.search(line):
                        hits.setdefault(cls, []).append((lno, COMMENT_KIND))
            continue
        if s == "%{":
            in_block = True
            continue
        code, lits = split_matlab_line(line)
        # Whatever `split_matlab_line` refused to read is a `%` comment or the
        # tail after a `...` continuation -- prose either way.
        prose = line[len(code):]
        if prose.strip():
            for cls, wrx in word.items():
                if wrx.search(prose):
                    hits.setdefault(cls, []).append((lno, COMMENT_KIND))
        if not lits and not code.strip():
            continue
        eq = assignment_split(code)
        guardish = any(g in code for g in GUARD_FUNCS)
        by_name = {}
        for text, col in lits:
            by_name.setdefault(text, col)
        for cls, rx in patterns.items():
            if cls in by_name:
                if (target_key(cls), lno) in emission_keys:
                    kind = EMITTED_CLASS_KIND
                elif guardish:
                    kind = "guard"
                else:
                    kind = "named"
                hits.setdefault(cls, []).append((lno, kind))
                continue
            if cls not in code:
                continue
            m = rx.search(code)
            if not m:
                continue
            kind = "field_read" if (eq is None or m.start() > eq) else "field_write"
            hits.setdefault(cls, []).append((lno, kind))
    # A MINT WITH NO LITERAL OF THE QUERIED SPELLING ON ITS LINE: a fixed-class
    # builder (`did2.build.relativeTimeReference(...)` names no class at all) or
    # a statement queried in the #88 spelling (`manipulation + temperature`
    # where the line says 'manipulation' ... 'temperature'). Filed as a mint
    # by TARGET KEY, once per line, so the literal pass above is not doubled.
    keys = {}
    for cls in patterns:
        keys.setdefault(target_key(cls), []).append(cls)
    for c, ln in sorted(emissions, key=lambda e: (e[1], e[0])):
        for cls in keys.get(target_key(c), ()):
            spots = hits.setdefault(cls, [])
            if (ln, EMITTED_CLASS_KIND) not in spots:
                spots.append((ln, EMITTED_CLASS_KIND))
    return hits, len(lines)


# The V_eta migration is TWO passes, and both count as "something is built".
# +migrators (V_zeta) and +migrators_i (intermediate) are deliberately NOT
# scanned: a V_zeta migrator is not evidence that the V_eta target is built, and
# counting it would inflate (b) with work that predates every decision here.
#
# THE TWO PASSES LIVE IN DIFFERENT REPOSITORIES, AND EVERY SITE SAYS WHICH.
# The board used to print `ndi_second_pass/stimulusBathToBath.m:137` -- a package
# label and a path, with nothing naming the repository. A reader looking for that
# file in DID-matlab, which is where the board's other 130-odd files are and
# where its `--did` argument points, finds NOTHING: it is
# NDI-matlab `src/ndi/+ndi/+migrate/+internal/stimulusBathToBath.m`. A citation
# that cannot be followed to the repository holding it is not a citation, and a
# reader who cannot find the file has to choose between believing the board and
# believing their own search. So the repository is part of every reference now:
#     NDI-matlab:ndi_second_pass/stimulusBathToBath.m:137
#
# ---------------------------------------------------------------------------
# THE BOARD READ HALF THE V_eta PATH -- corrected 2026-08-11
# ---------------------------------------------------------------------------
# `+migrators_j` is the PER-DOCUMENT half of the DID-side pass: one file per v1
# class, each seeing one document at a time. The other half is the BATCH
# POST-PASSES, which run over the whole converted batch after the per-document
# migrators and do the work a single-document migrator provably cannot -- mint
# an epoch, resolve a session anchor, fold deferred baths. They live one
# directory UP, in `+did2/+convert` itself and in its `+entities/`/`+readers/`
# helper packages, and the scan roots did not name them. Re-derived census of
# `+did2/+convert`, which is the denominator this correction is measured
# against:
#
#     187  .m files under +did2/+convert
#     125    +migrators_j                     SCANNED, always was
#      22    +migrators           \
#       9    +migrators_i          >  38  V_zeta path   EXCLUDED, deliberately
#       7    +migrators_e         /
#      14    directly in +convert \
#       7    +entities/            >  24  V_eta batch post-passes  ADDED HERE
#       3    +readers/            /
#
# The 38 stay out for the reason at the top of this comment, and that exclusion
# is now EXPLICIT and COUNTED (`files_excluded_v_zeta`) instead of being an
# omission from a list: an exclusion nobody can see in the output is
# indistinguishable from a root somebody forgot, which is precisely how the 24
# went missing.
#
# THE TWO GROUPS ARE NEVER MERGED INTO ONE COUNT. A mint in a batch post-pass
# and a mint in a per-document migrator are different facts about a class -- the
# first says the whole-batch pass builds it, the second says the per-document
# pass does -- and this file has already paid once for summing unlike categories
# (see the `GUARD_FUNCS` block comment). Every count below is carried per group
# as well as in total, and the artifact prints the split.
GROUP_MIGRATOR = "per_document_migrator"
GROUP_BATCH = "batch_post_pass"
GROUP_LABEL = {
    GROUP_MIGRATOR: "per-document migrator",
    GROUP_BATCH: "batch post-pass",
}
GROUPS = (GROUP_MIGRATOR, GROUP_BATCH)

# The V_zeta / intermediate packages. NOT a cosmetic list: the batch root is the
# whole of `+did2/+convert`, so without these names the recursive walk would
# swallow the 38 files the board is right to ignore. `+migrators_j` is here too
# because it has its OWN root above -- reaching it twice would double every
# per-document count.
V_ZETA_PACKAGES = ("+migrators", "+migrators_i", "+migrators_e")
_CONVERT_ALREADY_SCANNED = ("+migrators_j",)

MIGRATOR_PACKAGES = [
    ("did", "DID-matlab", "migrators_j", "src/did/+did2/+convert/+migrators_j",
     GROUP_MIGRATOR, ()),
    ("ndi", "NDI-matlab", "ndi_second_pass", "src/ndi/+ndi/+migrate/+internal",
     GROUP_MIGRATOR, ()),
    # The batch post-passes. ONE recursive root with a NAMED exclusion, rather
    # than three enumerated roots: enumeration is what failed here, and a new
    # `+convert/+something` helper package would be missed again by a list.
    ("did", "DID-matlab", "convert", "src/did/+did2/+convert",
     GROUP_BATCH, V_ZETA_PACKAGES + _CONVERT_ALREADY_SCANNED),
]

REF_CAP = 6            # refs listed per class in the artifact; the count is exact


def package_files(base, skip_dirs):
    """(files under `base`, files pruned by `skip_dirs`) -- both counted.

    `os.walk` with pruning rather than `glob('**/*.m')`, because the batch root
    is the parent of the V_zeta packages and the exclusion has to be able to cut
    a subtree. The pruned files are RETURNED, keyed by the package that cut
    them, not discarded: "38 files were skipped on purpose" and "the root was
    wrong" have to be distinguishable from the output alone, which is the whole
    defect this root list is fixing -- and "skipped because it is V_zeta" has to
    be distinguishable from "skipped because another root already read it".
    """
    kept, skipped = [], {}
    for dirpath, dirs, names in os.walk(base):
        pruned = [d for d in dirs if d in skip_dirs]
        dirs[:] = sorted(d for d in dirs if d not in skip_dirs)
        for d in pruned:
            bucket = skipped.setdefault(d, [])
            for sdir, _sd, snames in os.walk(os.path.join(dirpath, d)):
                bucket.extend(os.path.join(sdir, nm) for nm in snames
                              if nm.endswith(".m"))
        kept.extend(os.path.join(dirpath, nm) for nm in sorted(names)
                    if nm.endswith(".m"))
    return sorted(kept), {d: sorted(v) for d, v in skipped.items()}


def migrator_evidence(classes, did_root, ndi_root):
    """Scan the V_eta migrator packages for every open class.

    THE SIGNAL IS DELIBERATELY WIDER THAN A FILENAME MATCH, and the reason is
    that filename matching UNDERCOUNTS in a specific, known way: several classes
    are v1 SUPERCLASS BLOCKS rather than standalone documents, so no file is
    named after them and they are consumed by a shared helper in `private/` --
    `app` by jSoftwareFromApp.m:64, `filter` by jFrequencyFilter.m:112. The
    coverage ledger's `migrator` boolean is exactly that filename match, and it
    reports `app` as having no migrator while jSoftwareFromApp folds it.

    WHAT THIS SIGNAL MISSES, stated so nobody reads it as more than it is:

      * A MIGRATOR THAT NAMES A CLASS IS NOT NECESSARILY CONSUMING IT. Several
        +migrators_j files exist only to pass their class THROUGH deliberately
        (daqsystem.m says so in its own header: the document "shows in
        unconverted_by_class at its full corpus count; that is the honest
        signal"). This scan cannot tell a fold from a passthrough. That is
        precisely why a build signal alone is state (b) and never (c) -- only
        the census can tell them apart.
      * A CLASS REACHED THROUGH A COMPUTED NAME is invisible to the MINT
        recogniser -- `struct('class_name', leafClass, ...)`,
        `classBlock(e.class, ...)`. Those sites are COUNTED and LISTED
        (`unresolved_mint_sites`) rather than passed over, because "the analysis
        could not read it" and "there is nothing there" are different facts and
        this project has paid for conflating them. Six exist today.
      * FIELD-ACCESS HITS CAN BE INCIDENTAL for the short names. `.filter` is
        matched in jSpikeExtractionSettings.m as a grouping key as well as in
        jFrequencyFilter.m as the v1 block. Every reference is listed with its
        file and line so the reading is checkable rather than trusted.

    EVERY OCCURRENCE LANDS IN EXACTLY ONE BUCKET, AND THE BUCKETS ARE NEVER
    SUMMED. `mint`, `consumed`, `field_write`, `named` and `comment_mention` are
    five different facts about a class; each is returned with its own count.

    NOR ARE THE TWO GROUPS SUMMED WITHOUT BEING SHOWN. Every bucket is returned
    per group (`by_group`) as well as in total, so a mint in a batch post-pass
    is never indistinguishable from a mint in a per-document migrator.
    """
    patterns = {c: re.compile(r"\.\s*" + re.escape(c) + r"\b") for c in classes}
    per_class, roots_read, roots_missing = {}, [], []
    unresolved_sites, idiom_counts = [], {}
    files_read = lines_read = 0
    excluded_files = {}
    by_group_files = {g: 0 for g in GROUPS}
    by_group_lines = {g: 0 for g in GROUPS}
    by_group_idioms = {g: {} for g in GROUPS}
    by_group_unresolved = {g: [] for g in GROUPS}
    # IDIOM 5's wrappers live in `private/` helpers (`jStatement`), so they are
    # collected from every file a root reaches BEFORE any file is scanned.
    planned = []
    for kind, repo, label, rel, group, skip_dirs in MIGRATOR_PACKAGES:
        root = did_root if kind == "did" else ndi_root
        base = os.path.join(root, rel) if root else None
        if not base or not os.path.isdir(base):
            planned.append((repo, label, group, base, None, None))
            continue
        kept, skipped = package_files(base, set(skip_dirs))
        planned.append((repo, label, group, base, kept, skipped))
    # Only a `private/` function is visible outside its own file; a local
    # subfunction wrapper is found by `emitted_document_classes` in its file.
    wrappers = collect_builder_wrappers(
        [p for _r, _l, _g, _b, kept, _s in planned if kept for p in kept
         if os.path.basename(os.path.dirname(p)) == "private"])
    for repo, label, group, base, kept, skipped in planned:
        if kept is None:
            roots_missing.append(f"{repo}:{label}")
            continue
        roots_read.append(f"{repo}:{label}")
        for pkg, paths in skipped.items():
            excluded_files.setdefault(pkg, []).extend(
                f"{repo}:{label}/{os.path.relpath(p, base)}"
                for p in paths)
        for path in kept:
            rel_path = f"{repo}:{label}/{os.path.relpath(path, base)}"
            files_read += 1
            by_group_files[group] += 1
            name = os.path.basename(path)[:-2]
            # A FILE NAMED AFTER A CLASS is the per-document migrator's naming
            # convention and only that group's: `+convert/epochMint.m` is not a
            # migrator for a class called `epochMint`. Recording a batch file
            # here would invent build evidence out of a filename.
            if (group == GROUP_MIGRATOR and name in classes
                    and os.path.dirname(path) == base):
                per_class.setdefault(name, {}).setdefault("file", rel_path)
            unresolved = []
            idioms_here = {}
            hits, n_lines = scan_matlab_file(path, patterns, unresolved,
                                             idioms_here, wrappers)
            for k, v in idioms_here.items():
                idiom_counts[k] = idiom_counts.get(k, 0) + v
                by_group_idioms[group][k] = by_group_idioms[group].get(k, 0) + v
            lines_read += n_lines
            by_group_lines[group] += n_lines
            for lno, expr in unresolved:
                site = f'{rel_path}:{lno} ({expr})'
                unresolved_sites.append(site)
                by_group_unresolved[group].append(site)
            for cls, spots in hits.items():
                refs = per_class.setdefault(cls, {}).setdefault("refs", [])
                for lno, why in spots:
                    refs.append((f'{rel_path}:{lno}', why, group))

    if not roots_read:
        return None, {"available": False, "packages_read": [],
                      "packages_missing": roots_missing, "files_read": 0,
                      "lines_read": 0, "classes_queried": len(classes)}

    def _bucket(refs, kinds):
        """(count, capped citation list, per-group counts, per-group citations).

        The tuple carries the group, so the caller never has to guess it back
        out of a path.
        """
        sel = [r for r in refs if r[1] in kinds]
        n_by = {g: sum(1 for r in sel if r[2] == g) for g in GROUPS}
        refs_by = {g: [f"{r[0]} ({r[1]})"
                       for r in sel if r[2] == g][:REF_CAP] for g in GROUPS}
        return (len(sel), [f"{r[0]} ({r[1]})" for r in sel[:REF_CAP]],
                n_by, refs_by)

    _BUCKETS = (
        ("consuming_refs", CONSUMING_KINDS),
        # THE CLASS THIS PASS MINTS -- a document of it is produced.
        ("emitted_class_refs", (EMITTED_CLASS_KIND,)),
        # A BLOCK OF THAT NAME IS WRITTEN -- `anchor.<class> = struct(...)`.
        # Not a mint: the mint is the `document_class` statement a few lines
        # above it, and counting the pair together double-counts one document
        # while making the two indistinguishable.
        ("field_write_refs", ("field_write",)),
        # THE NAME APPEARS IN CODE AND NOTHING MORE -- a string value such as
        # `struct('kind', 'epoch_bounded_reference', ...)`.
        ("named_refs", ("named",)),
        # PROSE. Counts toward nothing; carried so that can be verified.
        ("comment_mentions", (COMMENT_KIND,)),
    )

    out = {}
    n_with_emission = 0
    n_emission_by_group = {g: 0 for g in GROUPS}
    for cls in sorted(classes):
        ev = per_class.get(cls, {})
        refs = sorted(ev.get("refs", []))
        row = {"migrator_file": ev.get("file")}
        by_group = {g: {} for g in GROUPS}
        for key, kinds in _BUCKETS:
            n, cited, n_by, cited_by = _bucket(refs, kinds)
            nkey = "n_" + key
            row[nkey] = n
            row[key] = cited
            for g in GROUPS:
                by_group[g][nkey] = n_by[g]
                by_group[g][key] = cited_by[g]
        row["by_group"] = by_group
        if row["n_emitted_class_refs"]:
            n_with_emission += 1
        for g in GROUPS:
            if by_group[g]["n_emitted_class_refs"]:
                n_emission_by_group[g] += 1
        out[cls] = row
    return out, {"available": True, "packages_read": roots_read,
                 "packages_missing": roots_missing, "files_read": files_read,
                 "lines_read": lines_read, "classes_queried": len(classes),
                 "classes_emitted_as_document_class": n_with_emission,
                 "unresolved_mint_sites": sorted(unresolved_sites),
                 "n_unresolved_mint_sites": len(unresolved_sites),
                 # Sites per mint idiom, over ALL classes in these packages --
                 # not only the open ones queried. The artifact prints these
                 # rather than a hand-written figure that cannot go stale
                 # quietly.
                 "mint_sites_by_idiom": {str(k): idiom_counts[k]
                                         for k in sorted(idiom_counts)},
                 # THE SAME FIGURES SPLIT BY GROUP. Present so that no reader
                 # has to take "the batch post-passes are in there now" on
                 # trust: if this block is all zeros, the 24 were not read.
                 "groups": list(GROUPS),
                 "group_labels": dict(GROUP_LABEL),
                 "packages_by_group": {
                     g: [f"{repo}:{label}"
                         for _k, repo, label, _r, grp, _s in MIGRATOR_PACKAGES
                         if grp == g and f"{repo}:{label}" in roots_read]
                     for g in GROUPS},
                 "files_read_by_group": by_group_files,
                 "lines_read_by_group": by_group_lines,
                 "classes_emitted_as_document_class_by_group":
                     n_emission_by_group,
                 "mint_sites_by_idiom_by_group": {
                     g: {str(k): by_group_idioms[g][k]
                         for k in sorted(by_group_idioms[g])} for g in GROUPS},
                 "n_unresolved_mint_sites_by_group": {
                     g: len(by_group_unresolved[g]) for g in GROUPS},
                 "unresolved_mint_sites_by_group": {
                     g: sorted(by_group_unresolved[g]) for g in GROUPS},
                 # THE V_zeta EXCLUSION, COUNTED RATHER THAN ASSUMED. These
                 # files are skipped on purpose; a zero here would mean the
                 # exclusion stopped reaching them, not that they went away.
                 # `+migrators_j` is kept in its own row because it is skipped
                 # by the BATCH root for a different reason -- its own root
                 # already read it -- and folding the two would make 125 read
                 # files look like 125 ignored ones.
                 "v_zeta_packages_excluded": list(V_ZETA_PACKAGES),
                 "n_files_excluded_by_package": {
                     pkg: len(v) for pkg, v in sorted(excluded_files.items())},
                 "n_files_excluded_v_zeta": sum(
                     len(excluded_files.get(p, ())) for p in V_ZETA_PACKAGES),
                 "files_excluded_v_zeta": sorted(
                     f for p in V_ZETA_PACKAGES
                     for f in excluded_files.get(p, ())),
                 "ref_kinds": list(REF_KINDS),
                 "code_kinds": list(CODE_KINDS),
                 "comment_kind": COMMENT_KIND,
                 "consuming_kinds": list(CONSUMING_KINDS),
                 "emitted_class_kind": EMITTED_CLASS_KIND}


def find_census_reports(roots):
    """Every *-summary.json under each root, at ANY depth, deduped by basename.

    Mirrors DID-matlab tools/census_digest.py:find_reports, and for the same
    reason it is recursive there: MATLAB's pwd during a corpus run is `tests/`,
    and upload-artifact re-roots the paths, so a one-level glob matched neither
    copy and a six-corpus run reported nothing while exiting 0.
    """
    found, missing, walked = [], [], 0
    for root in roots:
        if not os.path.isdir(root):
            missing.append(root)
            continue
        for dirpath, _dirs, names in os.walk(root):
            walked += 1
            for nm in sorted(names):
                if nm.endswith("-summary.json"):
                    found.append(os.path.join(dirpath, nm))
    found.sort(key=lambda p: (len(p.split(os.sep)), p))
    chosen, seen = [], set()
    for p in found:
        b = os.path.basename(p)
        if b not in seen:
            seen.add(b)
            chosen.append(p)
    return chosen, missing, walked, len(found)


def census_evidence(classes, roots):
    """Per-class SURVIVOR counts from the corpus reports.

    `summary.unconverted_by_class` is the survivor count: v1_to_v2.m:186 bumps
    it when a migrator hands its input straight back (`isequaln(v2Bodies{1},
    v2Body)`). It is keyed by the POST-universalRenames class name, which is the
    same name the built index uses, so no translation is needed.

    THE PRESENCE OF THE KEY IS WHAT MATTERS, NOT ITS CONTENTS. A report with
    `unconverted_count: 0` and an EMPTY `unconverted_by_class` has measured
    every class and found no survivor -- that is real evidence. A report with no
    `unconverted_count` AT ALL has measured nothing, and its silence must not be
    read as a zero. The two are one missing key apart and were the difference
    between a census and a decoration for two days on the DID-matlab side.
    """
    paths, missing, walked, n_all = find_census_reports(roots)
    reports, unreadable = [], []
    for p in paths:
        try:
            with open(p) as fh:
                reports.append((os.path.basename(p), json.load(fh)))
        except (OSError, ValueError) as err:
            unreadable.append(f"{os.path.basename(p)} ({err})")

    with_data = [(n, r) for n, r in reports if "unconverted_count" in r]
    corpora = sorted({str(r.get("corpus") or n.replace("-summary.json", ""))
                      for n, r in reports})
    # WHERE WE LOOKED goes to the console, not into the artifact. It is a
    # property of the INVOCATION (which --census roots were passed), not of the
    # evidence, and a field that changes with the command line would make the
    # staleness check fire on nothing -- which is how a real check becomes an
    # ignored one.
    probe = {"roots_walked": walked, "roots_missing": missing,
             "reports_unreadable": unreadable}
    src = {"available": bool(with_data),
           "reports_found": n_all,
           "reports_read": len(reports),
           "reports_unreadable": len(unreadable),
           "reports_with_survivor_data": len(with_data),
           "corpora": corpora,
           "source_documents": sum(int(r.get("total") or 0) for _n, r in reports),
           "classes_queried": len(classes)}
    if not with_data:
        return None, src, probe

    out = {}
    for cls in sorted(classes):
        total, per = 0, {}
        for _n, r in with_data:
            tbl = r.get("unconverted_by_class") or {}
            if not isinstance(tbl, dict):
                tbl = {}
            n = int(tbl.get(cls) or 0)
            if n:
                per[str(r.get("corpus") or "?")] = n
            total += n
        out[cls] = {"survivors": total, "by_corpus": per}
    return out, src, probe


# AN EMISSION MEANS THE OPPOSITE FOR A CLASS THAT IS SUPPOSED TO DISAPPEAR.
#
# `emitted_class` says a migrator MINTS documents of this class. For a class the
# decision KEEPS, that is the build landing (`control_stimulus_ids.m` minting
# `control_designation`). For a class the decision RETIRES, the same fact is
# evidence the change has NOT landed -- and counting it as progress would invert
# the number, which is exactly what this file already records happening to
# `session_relative_reference` the first time the migrator scan was written.
#
# Nothing derivable separates the two. Both are `disposition: in_progress`;
# both are named as decided targets in `did_v2_migration_targets.json` (which
# still lists `session_relative_reference` as the target of 40+ sources, written
# before the time model collapsed it -- an open question, not a fact this tool
# may settle). So the distinction is written here, TRANSCRIBED FROM THE SIGNED
# DECISION, with the quote that licenses each entry. This is not a disposition:
# the disposition is the sign-off line in the plan document, and adding one is
# the team's job (operating rule 4). It is the board declining to read a
# retirement as a build.
#
# Entries are CHECKED: the replacement must exist in the built schema set, so a
# typo or a renamed replacement fails loudly instead of silently discounting a
# class forever.
RETIRED_BY_ITS_OWN_DECISION = {
    # V_eta_time_reference_model_plan.md:468 --
    #   "TEAM-SIGN-OFF [time_reference]: ... 8 classes collapse to
    #    absolute_time_reference + relative_time_reference ..."
    # Three of the eight are minted today -- session_relative_reference,
    # session_bounded_reference and epoch_bounded_reference -- and every site is
    # work the collapse has still to undo.
    #
    # NO LINE NUMBERS HERE, DELIBERATELY. This comment used to carry four
    # (`ontology_table_row.m:262/:669`, `private/jSessionAnchor.m:19`,
    # `treatment_transfer.m:101`), and on 2026-08-11 not one of them was a mint
    # any more: :262 is a scale-field struct, :669 is an `end`, and the other
    # two are comments. A hand-written citation in a source file is the one
    # thing in this pipeline nothing regenerates, so it goes stale silently
    # while the artifact beside it stays right. The live sites, with their
    # repositories, are listed in `schemas/V_eta_STATUS.md` under each class --
    # generated, and therefore correct or loudly broken.
    # FOUR ENTRIES REMOVED 2026-08-11 (#65 increment 3a):
    # `epoch_relative_reference` -> relative_time_reference,
    # `event_bounded_reference` -> relative_time_reference,
    # `event_relative_reference` -> relative_time_reference and
    # `utc_reference` -> absolute_time_reference are gone from this dict because the
    # CLASSES are gone from the built set. A discount only means anything for a
    # class that still has a board row to discount; keeping the keys made them
    # "discounted but claimed by no decision family", which
    # test_every_discounted_class_names_a_replacement_that_exists rejects --
    # correctly, since the sign-off a discount is transcribed from has to be
    # locatable through a family. The collapse they name is EXECUTED for those
    # four, not pending.
    # THE LAST FOUR REMOVED 2026-09-25 (#65 increment 3b), for the same reason:
    # session_bounded/session_relative/epoch_bounded_reference are deleted, and
    # `time_reference` is no longer a retiring class -- it persists as the root.
    # V_eta_epoch_plan.md, signed 2026-08-08 -- the `epoch` ENTITY is minted and
    # `epochid` is DROPPED (the string mixin becomes an `epoch_id` EDGE on that
    # entity; `epoch_id` is a dependency name, not a class, so the replacement
    # CLASS is `epoch`). Listed to keep the rule general rather than fitted to
    # one family; it changes no state, because `epochid` reaches (b) on nine
    # CONSUMING references and is minted only as a superclass mixin anyway.
    # 2026-10-08 (signed, V_eta_entity_composition_plan.md sec. 4): the `epoch`
    # class merged into `entity` (type epoch), so the replacement CLASS is `entity`.
    "epochid": "entity",
}


STATE_A = "a_nothing_built"
STATE_B = "b_built_awaiting_corpus_proof"
STATE_C = "c_corpus_zero_survivors"
STATE_U = "u_unmeasured"

OPEN_STATE_LABEL = {
    STATE_A: "(a) nothing built (the decision state is a separate column)",
    STATE_B: "(b) built, awaiting corpus proof",
    STATE_C: "(c) corpus: 0 survivors in the corpora read",
    STATE_U: "(?) UNMEASURED -- no build evidence was ever taken",
}


def open_class_state(open_work, schemas, rows, mig, mig_src, cen, cen_src):
    """Merge the two evidence halves into one derived row per open class.

    A class is BUILT when a V_eta migrator names it OR a decided target of its
    own is present in the built schema set. The second half matters because a
    family can be half-landed: `app`'s target `software` is built and shipping
    while `app` itself is still carried, and a migrator-only signal would call
    that nothing.

    THE `app` EXAMPLE IS NOW THE WRONG ONE, 2026-08-17, and the rule it
    illustrates still holds. A migrator-only signal DOES now find `app`:
    `+migrators_j/private/jSoftwareFromApp.m` declares the fold and
    `coverage.py`'s fourth consumption channel reads it, so the class reaches
    rung 3. The second half of the OR is still load-bearing for genuinely
    half-landed families -- it is just no longer this one that proves it.

    A DECIDED TARGET THAT IS THE CLASS ITSELF IS NOT EVIDENCE. `projectvar`'s
    ledger row names `projectvar` as its own decided target (it passes through
    deliberately), and counting that would report every passthrough as built.
    """
    built_classes = {s["class_name"] for s in schemas}
    ledger = {r["v1_class"]: r for r in rows}
    # The DECISION state of each open class, from its own citations
    # (tools/decision_citations.py). Rendered beside the build evidence and never
    # combined with it: a class can be decided and unbuilt, or built and
    # proposed.
    def _decision(cls):
        names = [n for n in (cls, (ledger.get(cls) or {}).get("veta_class")) if n]
        return dc.decision_for(names)

    out = []
    for cls in sorted(open_work):
        row = ledger.get(cls) or {}
        decided = [t for t in (row.get("decided_targets") or []) if t != cls]
        # A name retired by the 2026-10-08 composition (signed) is built when what
        # replaced it is (coverage.py SUPERSEDED_BY_ENTITY_COMPOSITION), so the
        # board never lists a mixin's old join leaf as schema still to build.
        built_t = [t for t in decided if _target_built(t, built_classes)]
        missing_t = [t for t in decided if not _target_built(t, built_classes)]

        m = (mig or {}).get(cls)
        measured = m is not None
        mfile = m.get("migrator_file") if measured else None
        n_con = m.get("n_consuming_refs", 0) if measured else 0
        con_refs = m.get("consuming_refs", []) if measured else []
        n_write = m.get("n_field_write_refs", 0) if measured else 0
        write_refs = m.get("field_write_refs", []) if measured else []
        n_named = m.get("n_named_refs", 0) if measured else 0
        named_refs = m.get("named_refs", []) if measured else []
        n_comment = m.get("n_comment_mentions", 0) if measured else 0
        comment_refs = m.get("comment_mentions", []) if measured else []
        n_mint = m.get("n_emitted_class_refs", 0) if measured else 0
        mint_refs = m.get("emitted_class_refs", []) if measured else []
        # THE SAME FIVE BUCKETS, SPLIT BY WHICH HALF OF THE V_eta PASS THEY CAME
        # FROM. A snapshot written before the batch roots existed carries no
        # `by_group`, so the fallback puts everything under the group that was
        # being read then rather than inventing a zero for either.
        by_group = (m.get("by_group") if measured else None) or {
            GROUP_MIGRATOR: {"n_consuming_refs": n_con,
                             "consuming_refs": con_refs,
                             "n_emitted_class_refs": n_mint,
                             "emitted_class_refs": mint_refs,
                             "n_field_write_refs": n_write,
                             "field_write_refs": write_refs,
                             "n_named_refs": n_named, "named_refs": named_refs,
                             "n_comment_mentions": n_comment,
                             "comment_mentions": comment_refs},
            GROUP_BATCH: {"n_consuming_refs": 0, "consuming_refs": [],
                          "n_emitted_class_refs": 0, "emitted_class_refs": [],
                          "n_field_write_refs": 0, "field_write_refs": [],
                          "n_named_refs": 0, "named_refs": [],
                          "n_comment_mentions": 0, "comment_mentions": []},
        }

        def _split(nkey, by_group=by_group):
            """`3 per-document migrator, 2 batch post-pass` -- never a bare sum."""
            return ", ".join(f'{by_group[g].get(nkey, 0)} {GROUP_LABEL[g]}'
                             for g in GROUPS if by_group[g].get(nkey, 0))

        # A MINTED CLASS IS BUILT -- unless the decision is that it stops
        # existing, in which case the mint is the work still outstanding.
        retired_to = RETIRED_BY_ITS_OWN_DECISION.get(cls)
        mint_counts = bool(n_mint) and retired_to is None
        discount = None
        if n_mint and retired_to is not None:
            discount = (f'minted at {n_mint} site(s) ({_split("n_emitted_class_refs")}), NOT counted as build progress: the signed decision retires this class in favour of `{retired_to}`, so an emission is work still to undo')

        why = []
        if mfile:
            why.append(f"migrator `{mfile}`")
        if n_con:
            why.append(f'{n_con} consuming reference(s) ({_split("n_consuming_refs")})')
        if mint_counts:
            why.append(f'minted as a document class at {n_mint} site(s) ({_split("n_emitted_class_refs")})')
        if built_t:
            why.append("decided target(s) built: {}".format(", ".join(f"`{t}`" for t in built_t)))
        has_build = bool(mfile or n_con or mint_counts or built_t)

        c = (cen or {}).get(cls)
        survivors = c.get("survivors") if c else None
        by_corpus = c.get("by_corpus") if c else {}

        if not measured and not built_t:
            # No migrator scan happened AND the ledger offers nothing, so this
            # class has no evidence either way. Rule 3: that is not "(a)".
            state = STATE_U
        elif not has_build:
            state = STATE_A
        elif survivors == 0:
            state = STATE_C
        else:
            state = STATE_B

        dec = _decision(cls)
        out.append({
            "class_name": cls,
            "decision": dec["state"],
            "decided_in": ("{}:{} [{}]".format(dec["decided_by"]["document"],
                                               dec["decided_by"]["line"],
                                               dec["decided_by"]["tag"])
                           if dec["decided_by"] else None),
            "state": state,
            "state_label": OPEN_STATE_LABEL[state],
            "build_evidence": why,
            "migrator_file": mfile,
            "n_consuming_refs": n_con,
            "consuming_refs": con_refs,
            "n_emitted_class_refs": n_mint,
            "emitted_class_refs": mint_refs,
            "emission_counts_as_build": mint_counts,
            "retired_by_decision_in_favour_of": retired_to,
            "emission_discounted": discount,
            # THREE CATEGORIES, THREE COUNTS, NEVER A SUM. See the block comment
            # above `GUARD_FUNCS`: the single `n_emitting_refs` these replace
            # merged six missed mints with nine field writes under one caption.
            "n_field_write_refs": n_write,
            "field_write_refs": write_refs,
            "n_named_refs": n_named,
            "named_refs": named_refs,
            "n_comment_mentions": n_comment,
            "comment_mentions": comment_refs,
            # TWO HALVES OF ONE PASS, NEVER ONE UNDIFFERENTIATED COUNT. Every
            # bucket above is a total over both; this is the same evidence split
            # by whether it came from a per-document migrator or from a batch
            # post-pass, which are different facts about the class.
            "by_group": by_group,
            "decided_targets": decided,
            "decided_targets_built": built_t,
            "decided_targets_missing": missing_t,
            "survivors": survivors,
            "survivors_by_corpus": by_corpus,
            "build_evidence_measured": measured,
            "corpus_evidence_measured": c is not None,
        })
    return {"sources": {"migrator": mig_src, "census": cen_src},
            "state_labels": OPEN_STATE_LABEL,
            "counts": {k: sum(1 for r in out if r["state"] == k)
                       for k in OPEN_STATE_LABEL},
            "classes": out}


def committed_snapshot():
    """The `open_class_state` block already committed in did_v2_decisions.json."""
    try:
        with open(DECISIONS_OUT) as fh:
            return json.load(fh).get("open_class_state") or {}
    except (OSError, ValueError):
        return {}


def gather_evidence(open_work, schemas, rows, args, log):
    """Measure what is reachable; fall back to the committed snapshot otherwise.

    The fallback is what makes `--check` runnable in a CI job that checks out
    only this repo. It is a CACHE, so it is announced on stdout every time and
    never silently: `log` gets one line per half saying MEASURED or REUSED.
    """
    snap = committed_snapshot()
    snap_rows = {r["class_name"]: r for r in snap.get("classes", [])}
    snap_src = snap.get("sources", {})

    mig, mig_src = migrator_evidence(open_work, args.did, args.ndi)
    if mig is None:
        prior = {c: {"migrator_file": r.get("migrator_file"),
                     "n_consuming_refs": r.get("n_consuming_refs", 0),
                     "consuming_refs": r.get("consuming_refs", []),
                     "n_emitted_class_refs": r.get("n_emitted_class_refs", 0),
                     "emitted_class_refs": r.get("emitted_class_refs", []),
                     "n_field_write_refs": r.get("n_field_write_refs", 0),
                     "field_write_refs": r.get("field_write_refs", []),
                     "n_named_refs": r.get("n_named_refs", 0),
                     "named_refs": r.get("named_refs", []),
                     "n_comment_mentions": r.get("n_comment_mentions", 0),
                     "comment_mentions": r.get("comment_mentions", []),
                     "by_group": r.get("by_group")}
                 for c, r in snap_rows.items()
                 if r.get("build_evidence_measured")}
        if prior:
            mig = prior
            mig_src = snap_src.get("migrator", mig_src)
            log.append(f'migrator evidence: REUSED from the committed snapshot ({len(prior)} class(es)); no V_eta migrator package under {args.did} or {args.ndi}')
        else:
            log.append("migrator evidence: UNAVAILABLE and never snapshotted "
                       f"(looked under {args.did} and {args.ndi}). Every open class renders as "
                       "UNMEASURED.")
    else:
        log.append(f'migrator evidence: MEASURED -- {mig_src["files_read"]} file(s), {mig_src["lines_read"]} line(s), package(s) {", ".join(mig_src["packages_read"]) or "none"}')

    cen, cen_src, probe = census_evidence(open_work, args.census)
    log.append(f'census roots: {probe["roots_walked"]} walked, {len(probe["roots_missing"])} missing ({", ".join(probe["roots_missing"]) or "none"})')
    if cen is None:
        prior = {c: {"survivors": r.get("survivors"),
                     "by_corpus": r.get("survivors_by_corpus", {})}
                 for c, r in snap_rows.items()
                 if r.get("corpus_evidence_measured")}
        if prior:
            cen = prior
            cen_src = snap_src.get("census", cen_src)
            log.append(f'census evidence: REUSED from the committed snapshot ({len(prior)} class(es))')
        else:
            log.append(f'census evidence: NONE -- {cen_src["reports_read"]} report(s) read, {cen_src["reports_with_survivor_data"]} carried an `unconverted_count`. State (c) is UNPROVABLE in this run and no class is rendered as corpus-proven.')
    else:
        log.append(f'census evidence: MEASURED -- {cen_src["reports_with_survivor_data"]} report(s) with survivor data over {cen_src["source_documents"]} document(s), corpora: {", ".join(cen_src["corpora"]) or "none"}')

    return open_class_state(open_work, schemas, rows, mig, mig_src, cen, cen_src)


def render_open_state(p, ocs):
    """Render the derived open-class table. DENOMINATOR FIRST, unconditionally."""
    msrc = ocs["sources"]["migrator"]
    csrc = ocs["sources"]["census"]
    counts = ocs["counts"]
    rowsv = ocs["classes"]

    p(f'## What is actually left on the {len(rowsv)} open classes')
    p("")
    p("`in_progress` is a HAND-WRITTEN DECLARATION: every one of these classes is")
    p("open because its hand-written `disposition` in `schemas/registry/did_v2_class_dispositions.json` is")
    p("`in_progress`, and it leaves the list only when a person changes that entry.")
    p("Nothing about a landed migrator, a passing test or a green corpus")
    p("moves it. The table below does not change that membership -- only the team")
    p("decides a disposition -- it DERIVES, per class, how far the work has got.")
    p("")
    p("### The measurement and its denominator")
    p("")
    p("| evidence source | reach |")
    p("|---|---|")
    _pkg_by_group = msrc.get("packages_by_group") or {}
    _files_by_group = msrc.get("files_read_by_group") or {}
    _lines_by_group = msrc.get("lines_read_by_group") or {}
    _mint_by_group = msrc.get("classes_emitted_as_document_class_by_group") or {}
    _unres_by_group = msrc.get("n_unresolved_mint_sites_by_group") or {}
    p(f'| build: V_eta migrator packages read | {", ".join(f"`{s}`" for s in msrc.get("packages_read") or []) or "**NONE**"} |')
    for _g in GROUPS:
        p("| build: &nbsp;&nbsp;-- of those, {} | {} |".format(GROUP_LABEL[_g],
             ", ".join(f"`{s}`" for s in _pkg_by_group.get(_g) or [])
             or "**NONE**"))
    p(f'| build: migrator files inspected | {msrc.get("files_read", 0)} |')
    for _g in GROUPS:
        p(f'| build: &nbsp;&nbsp;-- of those, {GROUP_LABEL[_g]} | {_files_by_group.get(_g, 0)} |')
    p(f'| build: V_zeta files DELIBERATELY EXCLUDED (`{"`, `".join(msrc.get("v_zeta_packages_excluded") or [])}`) | {msrc.get("n_files_excluded_v_zeta", 0)} |')
    p(f'| build: migrator lines inspected | {msrc.get("lines_read", 0)} |')
    for _g in GROUPS:
        p(f'| build: &nbsp;&nbsp;-- of those, {GROUP_LABEL[_g]} | {_lines_by_group.get(_g, 0)} |')
    p(f'| build: classes queried | {msrc.get("classes_queried", 0)} |')
    p(f'| build: open classes MINTED as a document class | {msrc.get("classes_emitted_as_document_class", 0)} |')
    for _g in GROUPS:
        # NOT "of those" -- a class minted in both halves is in both rows, so
        # these two do not sum to the line above and must not read as if they
        # did. Two overlapping facts, stated as two.
        p(f'| build: &nbsp;&nbsp;-- open classes minted in a {GROUP_LABEL[_g]} (rows overlap) | {_mint_by_group.get(_g, 0)} |')
    p(f'| build: of those, discounted (decision retires the class) | {sum(1 for r in rowsv if r.get("emission_discounted"))} |')
    p(f'| build: `document_class` writes whose class name is a VARIABLE | {msrc.get("n_unresolved_mint_sites", 0)} |')
    for _g in GROUPS:
        p(f'| build: &nbsp;&nbsp;-- of those, in a {GROUP_LABEL[_g]} | {_unres_by_group.get(_g, 0)} |')
    p(f'| corpus: `*-summary.json` reports read | {csrc.get("reports_read", 0)} |')
    p(f'| corpus: reports carrying an `unconverted_count` | {csrc.get("reports_with_survivor_data", 0)} |')
    p(f'| corpus: documents behind those reports | {csrc.get("source_documents", 0)} |')
    p(f'| corpus: corpora named | {", ".join(f"`{c}`" for c in csrc.get("corpora") or []) or "**NONE**"} |')
    p("")
    if not msrc.get("available") and not msrc.get("files_read"):
        p("**NO MIGRATOR PACKAGE WAS READ.** The build column below is not clean;")
        p("it is UNMEASURED. Re-run with `--did /path/to/DID-matlab`.")
        p("")
    if not csrc.get("reports_with_survivor_data"):
        p(f'**NO CORPUS SURVIVOR DATA.** {csrc.get("reports_read", 0)} report(s) were read and {csrc.get("reports_with_survivor_data", 0)} of them carry')
        p("an `unconverted_count`, so **state (c) cannot be reached by any class in**")
        p("**this run** and none is rendered as corpus-proven. A report without that")
        p("key measured nothing; its silence is not a zero. Point `--census` at a")
        p("directory of corpus reports, or run the DID-matlab corpus gate.")
        p("")
    p(f'### Where the {len(rowsv)} open classes sit')
    p("")
    p("| state | classes |")
    p("|---|---|")
    for k in (STATE_A, STATE_B, STATE_C, STATE_U):
        p(f'| {OPEN_STATE_LABEL[k]} | {counts.get(k, 0)} |')
    p("")
    p("**(c) IS EVIDENCE, NOT A DISPOSITION.** 0 survivors is a fact about the")
    p("corpora that were read, and it may not be promoted to `retire` on its own:")
    p("the corpora are a SAMPLE of datasets, not the universe, and the reports carry")
    p("no per-class SOURCE denominator -- `by_class` counts OUTPUT names, so a class")
    p("fully consumed and a class with no documents at all both read as zero. Only")
    p("the team flips a disposition.")
    p("")
    p("### A REFERENCE IS CLASSIFIED BEFORE IT COUNTS")
    p("")
    p("Two kinds of reference make a class (b), and they answer different")
    p("questions.")
    p("")
    p("**CONSUMED** -- a migrator file named after it, an `isfield(preBody,")
    p("'<class>')` / `strcmp(classNameOf(s), '<class>')` guard, or a read of")
    p("`preBody.<class>`. That is evidence about a v1 SOURCE: something eats it.")
    p("")
    p("**MINTED** -- the migrator sets a document's class. That is evidence about")
    p("a V_eta TARGET: something builds it. The scan could not see this at all")
    p("until 2026-08-10, and the cost was concrete: `control_designation`")
    p("rendered as *decided, nothing built* while")
    p("`DID-matlab:migrators_j/control_stimulus_ids.m:111` was minting it -- no")
    p("file is named after the target of a rename, so a filename key can never")
    p("find one.")
    p("")
    p("### THE V_eta PASS HAS TWO HALVES AND THE BOARD READ ONE")
    p("")
    p("Corrected 2026-08-11. The DID-side V_eta pass is `+migrators_j` (one file")
    p("per v1 class, each seeing ONE document) **and** the BATCH POST-PASSES that")
    p("run over the whole converted batch afterwards and do what a single-document")
    p("migrator provably cannot -- mint an epoch, resolve a session anchor, fold")
    p("the deferred baths. Those live one directory UP, in `+did2/+convert` itself")
    p("and in its `+entities/` and `+readers/` helper packages, and the scan roots")
    p("did not name them. Re-derived census of `+did2/+convert`:")
    p("")
    p("| files | where | this board |")
    p("|---|---|---|")
    p("| 125 | `+migrators_j` | scans, always did |")
    p("| 38 | `+migrators` (22) + `+migrators_i` (9) + `+migrators_e` (7) | "
      "EXCLUDED, deliberately -- the V_zeta path |")
    p("| 24 | 14 in `+convert`, 7 in `+entities/`, 3 in `+readers/` | "
      "**ADDED 2026-08-11 -- previously invisible** |")
    p("| 187 | total `.m` under `+did2/+convert` | |")
    p("")
    p("The 38 stay out: a V_zeta migrator is not evidence a V_eta target is")
    p("built. That exclusion is now COUNTED in the denominator table above rather")
    p("than left as an omission from a list -- an exclusion nobody can see in the")
    p("output is indistinguishable from a root somebody forgot, which is exactly")
    p("how the 24 went missing.")
    p("")
    p("**THE TWO GROUPS ARE NEVER MERGED INTO ONE COUNT.** Every column below is")
    p("carried per group as well as in total, because *a batch post-pass mints")
    p("this class* and *a per-document migrator mints this class* are different")
    p("facts. Each site names its repository AND its package, so the group is")
    p("readable off any citation: `DID-matlab:convert/resolveDeferredBaths.m:177`")
    p("is a batch post-pass, `DID-matlab:migrators_j/fitcurve.m:139` is not.")
    p("")
    p("**THERE ARE THREE MINT IDIOMS AND UNTIL 2026-08-11 THIS BOARD KNEW ONE.**")
    p("")
    _idiom_shape = {
        "1": "`b.document_class = struct('class_name', '<class>', ...)`",
        "2": "`b.document_class = classBlock('<class>', {supers})`",
        "3": "`b.document_class.class_name = '<class>';`",
        # Idioms 4 and 5 (the #88 builder) are RECOGNISED by
        # emitted_document_classes; without a label here the row printed
        # "*unrecognised*", which read as uncounted mints.
        "4": "`did2.build.statement('<direction>', ..., 'ValueKind', '<kind>')`, "
             "`did2.build.document('<class>', ...)` or a fixed-class builder",
        "5": "a wrapper of idiom 4: `jStatement(preBody, '<class>', ...)`",
    }
    _by_idiom = msrc.get("mint_sites_by_idiom") or {}
    _idiom_by_group = msrc.get("mint_sites_by_idiom_by_group") or {}
    p("| idiom | shape | sites | {} |".format(" | ".join(GROUP_LABEL[g] for g in GROUPS)))
    p(f'|---|---|---|{"---|" * len(GROUPS)}')
    for _k in sorted(set(_idiom_shape) | set(_by_idiom)):
        p("| %s | %s | %d | %s |"
          % (_k, _idiom_shape.get(_k, "*unrecognised*"), _by_idiom.get(_k, 0),
             " | ".join(str((_idiom_by_group.get(g) or {}).get(_k, 0))
                        for g in GROUPS)))
    p(f'| - | class name is a VARIABLE -- unresolved here | {msrc.get("n_unresolved_mint_sites", 0)} | {" | ".join(str(_unres_by_group.get(g, 0)) for g in GROUPS)} |')
    p("")
    p("**THE THREE IDIOMS ARE RE-MEASURED IN THE NEW ROOTS, NOT ASSUMED TO CARRY")
    p("OVER.** The per-group columns are counted per file, so which idioms the")
    p("batch post-passes actually use is read off the table rather than asserted")
    p("in a sentence that can go stale; a zero there is a measured zero over the")
    p("file and line denominators above, and if a post-pass adopts `classBlock`")
    p("tomorrow the column moves on its own.")
    p("")
    p("Idioms 2 and 3 carry no `'class_name', '<X>'` comma pair, so the regex")
    p("imported from `tools/coverage.py` cannot see them. `classBlock` is a LOCAL")
    p("SUBFUNCTION, redefined in eight files with two different arities, and it is")
    p("recognised HERE BY ITS SHAPE, not its name: a local function that assigns")
    p("its own output a struct declaring `superclasses` whose `class_name` comes")
    p("from one of its parameters. The literal is then read from that parameter's")
    p("INDEX at each call site, so the superclass argument beside it cannot be")
    p("mistaken for a mint.")
    p("")
    _srr = next((r for r in rowsv
                 if r["class_name"] == "session_relative_reference"), None)
    p("**WHAT THE MISS COST, stated as the number and not as a lesson.**")
    p("`session_relative_reference` is a class whose whole open question is that")
    p("it must STOP being emitted. Idiom 1 in `+migrators_j` alone puts its mint")
    p(f'count at **3**; this run measures **{_srr["n_emitted_class_refs"] if _srr else "n/a -- no longer open"}**')
    if _srr:
        _srr_g = _srr.get("by_group") or {}
        p("({}).".format("; ".join(f'{(_srr_g.get(g) or {}).get("n_emitted_class_refs", 0)} in a {GROUP_LABEL[g]}' for g in GROUPS)))
    p("Two corrections got it there, and they are separate faults. Six migrators")
    p("(`fitcurve`, `image_stack`, `jrclust_clusters`, `neuron_extracellular`,")
    p("`pyraview`, `vmspikefit`) mint it through `classBlock`, which the")
    p("`'class_name'`-comma regex could not see; and the batch post-pass")
    p("`+convert/resolveDeferredBaths.m` mints it twice in a package the board")
    p("was not reading at all. The board reported a third of the outstanding")
    p("work, in this project's characteristic direction. Neither set was dropped")
    p("-- the six were filed as `named`, the weakest bucket, and the two were")
    p("filed nowhere, which is worse than dropping them because the first looks")
    p("like a measurement and the second looks like clean ground.")
    p("")
    p("**A `document_class` WRITE WHOSE CLASS NAME IS A VARIABLE IS COUNTED, NOT")
    p("SKIPPED.** `struct('class_name', leafClass, ...)` and")
    p("`classBlock(e.class, ...)` need the CALL GRAPH to resolve, which is")
    p("`tools/refresh_migration_targets.py`'s job, not this per-file scan's. Those")
    p("sites appear in the denominator table above. The mint counts in this")
    p("artifact are therefore a FLOOR.")
    p("")
    _unres = msrc.get("unresolved_mint_sites") or []
    if _unres:
        p("| unresolved `document_class` write | class name expression |")
        p("|---|---|")
        for _s in _unres:
            _site, _, _expr = _s.rpartition(" (")
            p("| `{}` | `{}` |".format(_site, _expr.rstrip(")")))
        p("")
    p("**THE OTHER CATEGORIES ARE REPORTED SEPARATELY AND ARE NEVER SUMMED.** A")
    p("migrator that WRITES a block of that name (`x.<class> = ...`), one that")
    p("merely NAMES it as a string value, and one that MENTIONS it in a comment")
    p("are three different facts, and a single cell reading *still emitted/named")
    p("at N site(s)* merged them. It also swallowed the six missed mints above.")
    p("Each now has its own column and its own count; comment mentions count")
    p("toward nothing and are shown so that can be checked rather than believed.")
    p("")
    p("**A MINT IS DISCOUNTED WHEN THE DECISION RETIRES THE CLASS.** For a class")
    p("whose signed decision is that it stops existing, minting it is the work")
    p("still outstanding, not progress -- so `session_relative_reference` and its")
    p("family stay where they are however many sites emit them. The list is")
    p("transcribed from the sign-off lines in")
    p("`tools/status_board.py:RETIRED_BY_ITS_OWN_DECISION`, and every replacement")
    p("named there is checked to exist. Note this is an OPEN CONTRADICTION between")
    p("two committed records, not a settled fact: `did_v2_migration_targets.json`")
    p("still lists `session_relative_reference` as a decided target of 40+ v1")
    p("sources, written before the time model collapsed it. The board takes the")
    p("under-reporting side and does not settle it.")
    p("")
    p("**The `decided target(s) built` signal is the WEAKER of the two** and is")
    p("marked separately for that reason. A decided target can be a class that")
    p("already existed for other reasons -- `ensemble` reaches (b) on `subject`,")
    p("`directed_relation` and `sampled_body`, none of which was built for it. Read")
    p("a row whose only evidence is a built target as *the target exists*, not as")
    p("*the work is done*.")
    p("")
    p("Each of the last four columns is one kind of fact and they are NOT added")
    p("together. `minted` = a document of this class is produced; `field writes`")
    p("= a block of that name is written; `named` = the name appears as a string")
    p("value; `comments` = prose, which counts toward nothing. Each cell is")
    p("written `total (M+B)` -- M from a per-document migrator, B from a batch")
    p("post-pass -- so no cell in this table is an undifferentiated count.")
    p("")
    p("| class | decision | state | build evidence | minted (M+B) | field writes "
      "(M+B) | named (M+B) | comments (M+B) | survivors |")
    p("|---|---|---|---|---|---|---|---|---|")

    def _cell(r, nkey):
        """`9 (7+2)` -- the total, then the migrator/batch split. Never one number."""
        total = r.get(nkey) or 0
        if not total:
            return "-"
        g = r.get("by_group") or {}
        return "%d (%s)" % (total, "+".join(
            str((g.get(grp) or {}).get(nkey, 0)) for grp in GROUPS))

    for r in rowsv:
        surv = ("n/a -- not measured" if r["survivors"] is None
                else str(r["survivors"]))
        ev = "; ".join(r["build_evidence"]) or ("*not measured*"
                                                if not r["build_evidence_measured"]
                                                else "*none*")
        mint_cell = _cell(r, "n_emitted_class_refs")
        if r.get("emission_discounted") and mint_cell != "-":
            mint_cell += " discounted"
        p("| `{}` | {} | {} | {} | {} | {} | {} | {} | {} |".format(r["class_name"], r.get("decision") or "-",
             OPEN_STATE_LABEL[r["state"]].split(" ", 1)[0], ev,
             mint_cell, _cell(r, "n_field_write_refs"),
             _cell(r, "n_named_refs"), _cell(r, "n_comment_mentions"),
             surv))
    p("")
    for k in (STATE_A, STATE_U, STATE_C, STATE_B):
        members = [r for r in rowsv if r["state"] == k]
        if not members:
            continue
        p(f'#### {OPEN_STATE_LABEL[k]} -- {len(members)}')
        p("")
        for r in members:
            bits = []
            grp = r.get("by_group") or {}

            def _per_group(_n, _refs, _caption, _row=r, _grp=grp):
                """One caption PER GROUP, never one caption over both.

                A site in `+convert/resolveDeferredBaths.m` and a site in
                `+migrators_j/fitcurve.m` say different things about a class --
                the batch pass builds it versus the per-document pass does --
                and this file has already paid once for a caption that summed
                unlike facts into one number.
                """
                said = []
                for g in GROUPS:
                    gr = _grp.get(g) or {}
                    n = gr.get(_n, 0)
                    if not n:
                        continue
                    cited = gr.get(_refs, [])
                    said.append((f"{_caption % n}, {GROUP_LABEL[g]}")
                                + ": {}{}".format(", ".join(f"`{x}`" for x in cited),
                                   " ..." if n > len(cited) else ""))
                if said:
                    return said
                # No per-group breakdown at all (a snapshot older than the
                # split). Report the total and say it is not split, rather than
                # silently printing a group's worth of evidence as if it were
                # one group's.
                n = _row.get(_n) or 0
                if not n:
                    return []
                cited = _row.get(_refs, [])
                return [("{}, group NOT RECORDED in this snapshot: {}{}".format(_caption % n,
                            ", ".join(f"`{x}`" for x in cited),
                            " ..." if n > len(cited) else ""))]

            if r["migrator_file"]:
                bits.append("migrator `{}`".format(r["migrator_file"]))
            bits.extend(_per_group("n_consuming_refs", "consuming_refs",
                                   "consumed at %d site(s)"))
            bits.extend(_per_group("n_emitted_class_refs", "emitted_class_refs",
                                   "MINTED as a document class at %d site(s)"))
            if r.get("emission_discounted"):
                bits.append(r["emission_discounted"])
            # ONE CAPTION PER CATEGORY. The single "still emitted/named at N
            # site(s)" line these three replace merged mints the scan had
            # misfiled, block writes and string values into one number.
            for _n, _refs, _caption in (
                    ("n_field_write_refs", "field_write_refs",
                     "a block of this name is WRITTEN at %d site(s)"),
                    ("n_named_refs", "named_refs",
                     "NAMED as a string value at %d site(s)"),
                    ("n_comment_mentions", "comment_mentions",
                     ("mentioned in %d COMMENT(s) -- prose, counts toward "
                     "nothing"))):
                bits.extend(_per_group(_n, _refs, _caption))
            if r["decided_targets_built"]:
                bits.append("target(s) BUILT: {}".format(", ".join(f"`{t}`"
                                        for t in r["decided_targets_built"])))
            if r["decided_targets_missing"]:
                bits.append("target(s) NOT built: {}".format(", ".join(f"`{t}`"
                                        for t in r["decided_targets_missing"])))
            if r["survivors"]:
                bits.append("survivors %d (%s)"
                            % (r["survivors"],
                               ", ".join("%s %d" % kv for kv in
                                         sorted(r["survivors_by_corpus"].items()))))
            p("- `{}` ({}) -- {}".format(r["class_name"], r.get("decision") or "no decision recorded",
                 "; ".join(bits) or "no evidence found"))
        p("")


# Decided by Jess Haley, 2026-10-29 [one folder, final classes only]
# (V_eta_go_forward_class_audit.md): no class is `in_progress` and no `retire`
# class remains; a retire class's file is deleted once nothing passes through
# it. So a `retire` class still in the tree is open work too.
OPEN_DISPOSITIONS = ("in_progress", "retire")


def open_class_names(schemas):
    """The open set -- `in_progress`, and `retire` classes whose file is still in
    the tree -- computed once so build() and the evidence layer cannot disagree
    about what "open" means."""
    return {s["class_name"] for s in schemas
            if s.get("disposition") in OPEN_DISPOSITIONS and not s.get("is_meta")}


def unplanned_retire_rows(rows):
    """`retire` rows with no migrator and no `how`: open work wearing a settled label.

    Found when spike_extraction_parameters turned out to hold filter_type /
    filter_low / filter_high / filter_order / filter_ripple -- exactly the data
    the frequency_filter model was designed for -- while counted as settled.
    """
    return sorted(
        r["v1_class"] for r in rows
        if r["disposition"] == "retire" and not r["migrator"]
        and not (r.get("how") or "").strip())


def class_names_for(cls, ledger_by_class):
    """The names a class may be cited under: itself, and its ledger row's V_eta class."""
    row = ledger_by_class.get(cls) or {}
    return [n for n in (cls, row.get("veta_class")) if n]


def _short(text, n=220):
    text = " ".join((text or "").split())
    text = text if len(text) <= n else text[:n - 3].rstrip() + "..."
    # A cut inside a `code span` leaves one backtick open, which re-pairs every
    # quotation after it on the line -- and the citation beside it then quotes
    # nothing check_citations can read. Close it.
    text = text + "`" if text.count("`") % 2 else text
    return text + '"' if text.count('"') % 2 else text


def _cite_cell(rec):
    """[tag]. `<line opening>` (document:line). for a resolved citation.

    The quoted opening of the decision line is the ANCHOR
    tools/check_citations.py looks for on the cited line, so every rendered
    citation can be verified (decision_citations.cite_md)."""
    if rec is None:
        return "-"
    if rec.get("line"):
        return "[{}]{}".format(rec["tag"], dc.cite_md(
            rec["document"], rec["line"], rec["anchor"]).rstrip())
    return "[{}] in {}".format(rec["tag"], rec["document"])


def build(ocs=None, didm=None, log=None):
    # `didm` and `log` are passed rather than discovered: the batch
    # post-pass sweep runs HERE and nowhere else, and reaching for
    # `find_repo` inside it is what let it ignore `--did` and render a
    # figure no sibling-less machine could ever reproduce. Neither value
    # may enter `ocs`: everything under `ocs["sources"]` is serialised
    # into did_v2_decisions.json, and an absolute checkout path there
    # would make the artifact differ between every machine that writes it.
    schemas, rows = load()

    # Computed HERE, before anything renders: a summary line must not depend
    # on a number computed after it.
    unplanned_retire = unplanned_retire_rows(rows)
    by_disp = {}
    for s in schemas:
        by_disp.setdefault(s.get("disposition", "(none)"), []).append(s["class_name"])
    open_classes = open_class_names(schemas)
    # Open work is in_progress, every retire class still in the tree
    # ([one folder, final classes only]), and retire-with-no-plan ledger rows.
    open_work = open_classes | set(unplanned_retire)
    ledger_by_class = {r["v1_class"]: r for r in rows}

    # A DISCOUNT MUST NAME A REAL REPLACEMENT. `RETIRED_BY_ITS_OWN_DECISION`
    # suppresses build credit, so a typo or a since-renamed replacement would
    # hold a class at "(a) nothing built" forever, silently. Fail loudly instead.
    built_now = {e["class_name"] for e in schemas}
    bad_repl = sorted((c, t) for c, t in RETIRED_BY_ITS_OWN_DECISION.items()
                      if t not in built_now)
    if bad_repl:
        sys.stderr.write(
            f'status_board: RETIRED_BY_ITS_OWN_DECISION names {len(bad_repl)} replacement class(es) that are not in the built index: {", ".join("{} -> {}".format(*cr) for cr in bad_repl)}\nEach entry discounts a migrator\'s emission, so a stale name pins its class at \'nothing built\' with no way to notice.\n')
        sys.exit(1)

    # A CITATION MUST NAME A CLASS THAT EXISTS, by its built-index name or its
    # did_v1 ledger name (the two differ whenever NDI spells it in camelCase:
    # `imageStack_parameters` in the ledger is `image_stack_parameters` in the
    # index). A citation for a deleted class is a record about nothing.
    known = built_now | set(ledger_by_class)
    ghosts = sorted(c for c in dc.CITATIONS if c not in known)
    if ghosts:
        sys.stderr.write(
            f'decision_citations.CITATIONS names {len(ghosts)} class(es) that are neither in the built index nor in the coverage ledger: {", ".join(ghosts)}\nA collapsed or deleted class must lose its citation.\n')
        sys.exit(1)

    # THE ONE DEFINITION of "this class is decided" (tools/decision_citations.py),
    # shared with tools/coverage.py: the class cites a decision line that exists.
    open_dec = {c: dc.decision_for(class_names_for(c, ledger_by_class))
                for c in sorted(open_work)}
    decided_open = [c for c in sorted(open_work) if open_dec[c]["state"] == dc.DECIDED]
    proposed_open = [c for c in sorted(open_work) if open_dec[c]["state"] != dc.DECIDED]
    unresolved = dc.unresolved_citations()

    total = len(schemas)
    n_persist = len(by_disp.get("persist", []))
    n_retire = len(by_disp.get("retire", []))

    L = []
    p = L.append
    p("# V_eta status board (GENERATED -- do not hand-edit)")
    p("")
    p("Regenerate with `python3 tools/status_board.py`. CI runs `--check`.")
    p("")
    p("State lives here. The plan documents under `schemas/` keep the RATIONALE")
    p("for each model; this board owns *how much is left and what exactly*.")
    p("")
    p("**A class is DECIDED only when it cites a decision line that exists**: a")
    p("`TEAM-SIGN-OFF [tag]` line, or a `Decided by <team member>, <date> [<tag>]:` line, in")
    p("the document its citation names (`tools/decision_citations.py`). Anything")
    p("else is **Proposed (not decided)**, whatever any prose says.")
    p("")

    if unresolved:
        p("## ERROR -- citations that do not resolve")
        p("")
        p("Each names a document and tag with no accepted decision line. The class")
        p("renders as proposed until the citation is corrected; this fails `--check`.")
        p("")
        p("| class | document | tag | why |")
        p("|---|---|---|---|")
        for cls, rec in unresolved:
            p(f'| `{cls}` | `{rec["document"]}` | `{rec["tag"]}` | {rec["why"]} |')
        p("")

    p("## Where V_eta stands")
    p("")
    p("| | count |")
    p("|---|---|")
    p(f'| target classes | {total} |')
    p(f'| settled (persist) | {n_persist} |')
    p(f'| `retire`, file still in the tree (open: delete it once nothing passes through it, [one folder, final classes only]) | {n_retire} |')
    p(f'| **still open (`in_progress`)** | **{len(by_disp.get("in_progress", []))}** |')
    p(f'| **`retire` with no migrator YET** | **{len(unplanned_retire)}** |')
    p(f'| **open classes in all** | **{len(open_work)}** |')
    p(f'| &nbsp;&nbsp;decided (cites a decision line), awaiting build | {len(decided_open)} |')
    p(f'| &nbsp;&nbsp;**proposed (not decided), awaiting review** | **{len(proposed_open)}** |')
    p("")
    if ocs:
        c = ocs["counts"]
        p("| open-class BUILD/PROOF state (derived, see below) | count |")
        p("|---|---|")
        for k in (STATE_A, STATE_B, STATE_C, STATE_U):
            p(f'| {OPEN_STATE_LABEL[k]} | {c.get(k, 0)} |')
        p("")

    # THE DERIVED HALF: measured against the migrator packages and the corpus
    # census, or says it was not.
    if ocs:
        render_open_state(p, ocs)

    p("## Proposed (not decided) -- awaiting review")
    p("")
    p(f'DENOMINATOR: {len(open_work)} open class(es); {len(proposed_open)} cite no decision line that resolves.')
    p("")
    if proposed_open:
        p("| class | citations that did not resolve |")
        p("|---|---|")
        for c in proposed_open:
            bad = open_dec[c]["unresolved"]
            p("| `{}` | {} |".format(c, "; ".join(
                f'`{r["document"]}` `[{r["tag"]}]`' for r in bad) or "none recorded"))
        p("")
    else:
        p("None -- every open class cites a decision line that exists.")
        p("")

    # THE TARGET-BUILD JOIN, per decided class. `open_class_state` computes
    # `decided_targets` / `_built` / `_missing` for open classes; a cited class
    # that is not open (a v1 source row marked `retire` with a migrator) has no
    # such row, so the LEDGER is read directly as the second source.
    tgt_by_class = {r["class_name"]: r for r in (ocs or {}).get("classes", [])}

    def _decided_of(member):
        """(built, missing) for one class, ledger as fallback.

        A decided target that IS the class is dropped, exactly as
        `open_class_state` drops it: a deliberate passthrough is not evidence
        that anything was built.
        """
        row = tgt_by_class.get(member)
        if row:
            return (set(row.get("decided_targets_built") or []),
                    set(row.get("decided_targets_missing") or []))
        led = ledger_by_class.get(member)
        if not led:
            return set(), set()
        dec = [t for t in (led.get("decided_targets") or []) if t != member]
        return ({t for t in dec if _target_built(t, built_now)},
                {t for t in dec if not _target_built(t, built_now)})

    def _targets_cell(member):
        if not ocs:
            return "not measured"
        b, m = _decided_of(member)
        n = len(b) + len(m)
        return f'{len(b)} of {n}' if n else "no target recorded"

    p("## Decided, awaiting build -- the open classes")
    p("")
    p(f'DENOMINATOR: {len(open_work)} open class(es); {len(decided_open)} cite a decision line that exists. The decision column is the line\'s own text, not a summary.')
    p("")
    if decided_open:
        p("| class | targets built | decided in | decision |")
        p("|---|---|---|---|")
        for c in decided_open:
            rec = open_dec[c]["decided_by"]
            p(f'| `{c}` | {_targets_cell(c)} | {_cite_cell(rec)} | {_short(rec["decision"])} |')
        p("")

    # EVERY CITATION, not only the open classes': the record is per class, and
    # most decided classes are no longer `in_progress`.
    cited = sorted(dc.CITATIONS)
    disp_of = {s["class_name"]: s.get("disposition", "(none)") for s in schemas}
    all_missing = set()
    p("## Every decision citation")
    p("")
    p(f'DENOMINATOR: {len(cited)} class(es) cite {sum(len(v) for v in dc.CITATIONS.values())} decision line(s); {len(unresolved)} citation(s) do not resolve. "targets built" counts the class\'s decided targets present in the built set (a target equal to the class is a passthrough and is not counted).')
    p("")
    p("| class | disposition | targets built | decided in |")
    p("|---|---|---|---|")
    for c in cited:
        d = dc.decision_for([c])
        disp = disp_of.get(c) or (ledger_by_class.get(c) or {}).get("disposition", "(absent)")
        if ocs:
            all_missing |= _decided_of(c)[1]
        p("| `{}` | {} | {} | {} |".format(
            c, disp, _targets_cell(c),
            "; ".join(_cite_cell(r) if r["resolved"] else
                      f'**UNRESOLVED** `{r["document"]}` `[{r["tag"]}]`'
                      for r in d["citations"])))
    p("")
    if ocs:
        if all_missing:
            p("Decided targets not yet in the built set (the schema build queue):")
            p("")
            for t in sorted(all_missing - built_now):
                p(f"- `{t}`")
            p("")
        else:
            p("Every decided target these classes name is present in the built set, so")
            p("what remains for them is MIGRATOR work, not schema work.")
            p("")

    census = dc.decision_census()
    p("## Decision lines no class cites")
    p("")
    p(f'DENOMINATOR: {census["documents_read"]} document(s) read ({len(census["documents_excluded_as_generated"])} generated copies excluded); {census["accepted_lines"]} decision line(s) accepted, {len(census["rejected_lines"])} rejected; {census["lines_cited"]} cited by a class, {len(census["uncited_lines"])} cited by none.')
    p("")
    p("An uncited line is a decision the record holds that no class points at.")
    p("Most decide something that is not one class (a tenet, a naming rule, a")
    p("field). If one decides a class's disposition, that class should cite it.")
    p("")
    for e in census["uncited_lines"]:
        p("- {}{}".format(e["tag"] or e["date"] or "undated",
                          dc.cite_md(e["document"], e["line"], e["anchor"]).rstrip()))
    p("")

    # v1 source side
    led_disp = {}
    for r in rows:
        led_disp.setdefault(r["disposition"], []).append(r["v1_class"])

    unverified = sorted(led_disp.get("no V_eta home, no migrator -- UNVERIFIED", []))
    p("## v1 source side (from the coverage ledger)")
    p("")
    p("| disposition | count |")
    p("|---|---|")
    for k in sorted(led_disp, key=lambda k: -len(led_disp[k])):
        p(f'| {k} | {len(led_disp[k])} |')
    p("")
    if unplanned_retire:
        # MEASURED, NOT ASSUMED -- and it caught one immediately. See the note
        # under the heading below.
        batch_hits = batch_consumers(unplanned_retire, didm)
        if log is not None:
            log.append(batch_evidence_line(batch_hits))
        if ocs is not None:
            # NORMALISED before it is stashed, and stashed BEFORE
            # `decisions_text(ocs)` runs so the snapshot is written by the
            # same pass that took the measurement. `reused` and
            # `roots_missing` are DELIBERATELY not persisted -- they
            # describe the RUN, not the finding, and writing them made
            # did_v2_decisions.json itself differ between a machine with
            # DID-matlab and one without, moving the staleness one file
            # sideways instead of removing it.
            ocs.setdefault("sources", {})["batch_consumers"] = {
                "files_scanned": batch_hits["files_scanned"],
                "by_class": batch_hits["by_class"]}
        p(f'### `retire`, but NO MIGRATOR YET -- {len(unplanned_retire)} rows')
        p("")
        p("Marked `retire` in the ledger with **no per-class migrator and no `how`")
        p("note**. `retire` reads as settled, so they are counted with the open classes")
        p("above -- they are open work. Several hold real data (e.g.")
        p("`spike_extraction_parameters` carries filter_type / filter_low /")
        p("filter_high / filter_order / filter_ripple).")
        p("")
        p("**THIS PARAGRAPH SAID \"so the documents pass through untouched today\"")
        p("and that was an INFERENCE from `no migrator`, not a measurement.** The")
        p("ledger's `migrator` column means \"a file in `+migrators_j` / `+migrators`")
        p("/ `+migrators_i` is named after this class\" -- it says nothing about the")
        p("BATCH POST-PASSES in `+did2/+convert`, which consume classes no")
        p("per-class migrator touches. Measured now, per row, below.")
        p("")
        p("**This heading used to say \"nothing decided\" / \"no recorded plan\", and that")
        p("was WRONG** -- it is computed from the LEDGER (disposition + migrator + `how`),")
        p("not from whether a decision exists. Checked 2026-08-08: **every one of these")
        p("rows is covered by a plan document**, and most are signed. The list means")
        p("\"no migrator has been written yet\", not \"nobody has decided\". A board that")
        p("reports settled work as undecided is the mirror of the failure this board")
        p("exists to prevent, and it cost a review pass to notice.")
        p("")
        p('DENOMINATOR: %d row(s), each searched for its BARE CLASS NAME as a quoted literal in %d batch post-pass file(s) under `+did2/+convert` (comments stripped)%s.'
          # THE REUSE NOTICE GOES TO STDOUT, NOT INTO THE ARTIFACT. Writing
          # "REUSED" here was tried first and is self-defeating: the rendered
          # file would then differ between a machine with DID-matlab and one
          # without, which is precisely the staleness the fallback exists to
          # remove. Every other evidence half already reports MEASURED/REUSED
          # on the evidence log for the same reason -- the artifact records
          # what is true, the run records how it was learned.
          % (len(unplanned_retire), batch_hits["files_scanned"],
             "" if batch_hits["files_scanned"]
             else " -- ZERO FILES READ, so every 'passes through' below is "
                  "UNMEASURED, not clean"))
        p("")
        for c in unplanned_retire:
            hits = batch_hits["by_class"].get(c) or []
            if hits:
                p("- `{}` -- **NOT untouched**: consumed by {}".format(c, ", ".join(f"`{h}`" for h in hits)))
            else:
                p(f"- `{c}` -- no per-class migrator and no batch post-pass names "
                  "it; passes through today")
        p("")

    if unverified:
        p("**UNVERIFIED** -- no V_eta home, no migrator, fate never established. "
          "These strand today:")
        p("")
        for c in unverified:
            p(f"- `{c}`")
        p("")


    ok = not unresolved
    return "\n".join(L) + "\n", ok


STATE_LABEL = {
    dc.DECIDED: "decided: cites a decision line that exists",
    dc.PROPOSED: "Proposed (not decided): awaiting review",
}


def decisions_doc(ocs=None):
    """Build the machine-readable decisions artifact: ONE RECORD PER CLASS.

    A record exists for every class that cites a decision line and for every
    open class. Its `state` is `decided` only when one of its citations
    resolves to a decision line; the line's own location and text ride with it.
    """
    schemas, rows = load()
    disp = {s["class_name"]: s.get("disposition", "(none)") for s in schemas}
    ledger_by_class = {r["v1_class"]: r for r in rows}
    open_work = (open_class_names(schemas) | set(unplanned_retire_rows(rows)))

    by_class = {}
    for cls in sorted(set(dc.CITATIONS) | open_work):
        d = dc.decision_for(class_names_for(cls, ledger_by_class))
        by_class[cls] = {
            "class_name": cls,
            "disposition": disp.get(cls) or (ledger_by_class.get(cls) or {}).get(
                "disposition", "(absent)"),
            "open": cls in open_work,
            "state": d["state"],
            "state_label": STATE_LABEL[d["state"]],
            "decided_in": ({k: d["decided_by"][k] for k in
                            ("document", "tag", "line", "kind")}
                           if d["decided_by"] else None),
            "decision": d["decided_by"]["decision"] if d["decided_by"] else None,
            "citations": [{k: r[k] for k in ("document", "tag", "resolved",
                                             "line", "kind", "why")}
                          for r in d["citations"]],
        }

    def _count(recs):
        return {k: sum(1 for r in recs if r["state"] == k) for k in STATE_LABEL}

    open_recs = [r for r in by_class.values() if r["open"]]
    doc = {
        "title": "V_eta decisions, per class (GENERATED -- do not hand-edit)",
        "description":
            "Regenerate with `python3 tools/status_board.py`. The human-readable "
            "twin is schemas/V_eta_STATUS.md. A class is decided ONLY when it "
            "cites a decision line that exists -- a `TEAM-SIGN-OFF [tag]` line "
            "or a `Decided by <team member>, <date> [<tag>]:` line in the cited document "
            "(tools/decision_citations.py). Everything else is proposed (not "
            "decided).",
        "summary": {
            "classes": len(by_class),
            "classes_citing": len(dc.CITATIONS),
            "citations": sum(len(v) for v in dc.CITATIONS.values()),
            "citations_unresolved": len(dc.unresolved_citations()),
            "open_classes": len(open_recs),
            "by_state": _count(by_class.values()),
            "open_by_state": _count(open_recs),
            "state_labels": STATE_LABEL,
        },
        "by_class": by_class,
    }
    if ocs:
        # THE EVIDENCE SNAPSHOT. It lives here, in a committed artifact, because
        # neither sibling repo is checked out in every CI job -- so this block
        # is what `--check` compares against and what a `--check`-only run reads
        # back. It carries no timestamps and no absolute paths on purpose: a
        # field that changes every run makes the staleness check meaningless.
        doc["open_class_state"] = ocs
    return doc


def decisions_text(ocs=None):
    return json.dumps(decisions_doc(ocs), indent=2, sort_keys=False) + "\n"



def parse_args(argv):
    ap = argparse.ArgumentParser(
        description="Generate schemas/V_eta_STATUS.md + did_v2_decisions.json.")
    ap.add_argument("--check", action="store_true",
                    help="exit non-zero if the committed board is out of date")
    ap.add_argument("--did", default=find_repo("DID-matlab", "DID_MATLAB")
                    or os.environ.get("DID_MATLAB_PATH", "/home/user/DID-matlab"),
                    help="DID-matlab checkout (the +migrators_j package)")
    ap.add_argument("--ndi", default=find_repo("NDI-matlab", "NDI_MATLAB")
                    or os.environ.get("NDI_MATLAB_PATH", "/home/user/NDI-matlab"),
                    help="NDI-matlab checkout (the V_eta second pass)")
    ap.add_argument("--census", action="append", default=None, metavar="DIR",
                    help="directory of corpus *-summary.json reports; repeatable. "
                         "Defaults to <did>/corpus-reports and "
                         "<did>/tests/corpus-reports.")
    args = ap.parse_args(argv[1:])
    if args.census is None:
        args.census = [os.path.join(args.did, "corpus-reports"),
                       os.path.join(args.did, "tests", "corpus-reports")]
    return args


def main(argv):
    args = parse_args(argv)
    schemas, rows = load()

    # DENOMINATOR FIRST, UNCONDITIONALLY, and to stdout rather than into the
    # artifact: the reader of a generated file must be able to tell a
    # measurement from a reused snapshot, and a run that measured nothing must
    # not look like a run that found nothing.
    log = []
    ocs = gather_evidence(open_class_names(schemas), schemas, rows, args, log)

    text, ok = build(ocs, didm=args.did, log=log)
    dtext = decisions_text(ocs)

    print("status board evidence:")
    for line in log:
        print("  " + line)
    c = ocs["counts"]
    print("  open classes: %d -- %s"
          % (len(ocs["classes"]),
             ", ".join(f'{OPEN_STATE_LABEL[k].split(" ", 1)[0]} {c.get(k, 0)}'
                       for k in (STATE_A, STATE_B, STATE_C, STATE_U))))

    if args.check:
        current = Path(OUT).read_text() if os.path.exists(OUT) else ""
        if current != text:
            print("V_eta_STATUS.md is STALE. Run: python3 tools/status_board.py")
            return 1
        dcur = Path(DECISIONS_OUT).read_text() if os.path.exists(DECISIONS_OUT) else ""
        if dcur != dtext:
            print("did_v2_decisions.json is STALE. Run: python3 tools/status_board.py")
            return 1
        if not ok:
            print("Status board reports unclaimed or duplicated open classes.")
            return 1
        print("V_eta_STATUS.md + did_v2_decisions.json are current.")
        return 0
    with open(OUT, "w") as fh:
        fh.write(text)
    with open(DECISIONS_OUT, "w") as fh:
        fh.write(dtext)
    print(f"wrote {os.path.relpath(OUT, REPO)}")
    print(f"wrote {os.path.relpath(DECISIONS_OUT, REPO)}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
