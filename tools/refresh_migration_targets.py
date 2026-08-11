#!/usr/bin/env python3
"""Refresh the `targets` field of `schemas/V_eta_migration_targets.json`.

WHAT THIS TOOL OWNS, AND WHAT IT DELIBERATELY DOES NOT.
`V_eta_migration_targets.json` mixes two kinds of statement, and the file's own
`_comment` draws the line:

    targets      "the V_eta document class(es) its migrator ACTUALLY EMITS"
                 -- a fact about code, MECHANICALLY DERIVABLE.
    how / flags / carried / second_pass / decided_targets
                 -- authored prose and cross-repo facts. NOT derivable.

So this tool derives `targets` and touches nothing else. A hand-maintained
`targets` drifts every time a migrator lands (it had: the calculator family
gained a `software` emission and 12 rows never heard about it); a derived one
cannot.

HOW A TARGET IS DERIVED, AND WHY IT IS NOT A THIRD EXTRACTOR.
The regex that recognises `'class_name', '<X>'` lives in `tools/coverage.py`
(`_CLASS_EMIT`). `tools/status_board.py` already imports it BY PATH and adds the
two filters that turn "a class name appears" into "a document of this class is
minted": comments dropped, and `superclasses` entries dropped BY POSITION INSIDE
THE JOINED LOGICAL STATEMENT (a `document_class = struct(...)` spans up to eight
physical lines, so a per-line rule reads a superclass as a document class). This
file imports THAT -- `logical_statements`, `split_matlab_line`,
`assignment_split`, `emitted_document_classes`, `CLASS_EMIT` -- rather than
re-deriving any of it. Three copies of one regex is how this project produced two
contradicting records of `dataseries_channel_map`.

WHAT IS ADDED ON TOP, AND WHY IT HAD TO BE.
`status_board.emitted_document_classes` answers "is this class minted ANYWHERE in
the migrators" -- a per-class question over all files at once. This file answers
"what does the migrator FOR THIS SOURCE CLASS emit" -- a per-entry-point question.
Three things separate them, and each one, left out, would have DELETED true
targets from the record:

  1. THREE EMISSION IDIOMS, NOT ONE. status_board's docstring says every emission
     is `<body>.document_class = struct('class_name', ...)`. Measured now, on the
     same files, that is 46 of 68 `document_class` writes. The other two idioms
     are invisible to a `'class_name'`-comma regex:
         obs.document_class = classBlock('score_observation', {...})   (7 files)
         v2Body.document_class.class_name = 'daqreader_epochdata_ingested';
     `classBlock` is a LOCAL SUBFUNCTION redefined in seven files with two
     different arities. Deriving `targets` from the comma idiom alone would have
     emptied `fitcurve`, `vmspikefit`, `neuron_extracellular`, `pyraview`,
     `image_stack`, `jrclust_clusters`, `oneepoch`, `daqreader_ndr`,
     `daqreader_mfdaq_epochdata_ingested` and `element_epoch`.
  2. THE EMISSION USUALLY IS NOT IN THE FILE NAMED AFTER THE SOURCE CLASS.
     `contrast_tuning.m` is thirteen lines and emits nothing directly; its three
     targets come from `private/jCalculation.m`, which in turn calls
     `jSessionAnchor` and `jSoftwareFromApp`. So the analysis follows the call
     graph into `private/`, into local subfunctions, and into the cross-package
     calls the migrators make.
  3. THE CLASS NAME IS OFTEN A PARAMETER.
     `jCalculation.m:67` is `struct('class_name', leafClass, ...)`. The literal
     lives at the CALL SITE (`jCalculation(preBody, 'harmonic_component_
     calculation', ...)`). So an emission is carried as a symbol -- literal, or
     "parameter #k of this function" -- and parameters are substituted with the
     actual argument at each call site.
  4. THE EMITTER NEED NOT LIVE IN A MIGRATOR PACKAGE AT ALL, and this one was
     added on 2026-08-11 after the omission DELETED SEVEN TRUE TARGETS from
     `metadata_editor`. That day `entityDoc` / `relationDoc` / `orgFor` /
     `buildGids` / `emptyGids` moved out of `migrators_j/metadata_editor.m`
     into a new `+did2/+convert/+entities` package, because a second reader of
     the same six entity classes appeared (`resolveOpenmindsCitations`). The
     migrator now reaches them by `import did2.convert.entities.entityDoc` and
     a bare `entityDoc(preBody, 'dataset', ...)`. Neither spelling was in this
     tool's scope: `private/` and file-local subfunctions were, and the
     fully-qualified branch matched `migrators*.` only. So the call did not
     resolve -- AND, worse, DID NOT REPORT: the generic call scan drops any
     name it does not recognise, because it also sees `isfield(`, `numel(` and
     every other builtin. `metadata_editor` therefore read as a migrator that
     mints NOTHING, i.e. a carry-forward, and this tool proposed removing
     `dataset, person, organization, funding, publication, web_resource,
     directed_relation` from a migrator that plainly emits all seven. That is
     operating rule 3 violated by an instrument built to honour it: absence
     used as evidence. Scope now follows `import did2.convert.<...>` bindings
     (including a trailing `.*`) and fully-qualified `did2.convert.<pkg>.<fn>(`
     / `did2.convert.<fn>(` calls into the file that defines them, with
     arguments captured so parameter substitution still works. A
     `did2.convert.` call that CANNOT be resolved to a file is now an
     UNRESOLVED SITE, not a silent skip -- the row degrades to PARTIAL, which
     can only gain, instead of collapsing to a false carry-forward. Only
     explicitly `did2.convert.`-qualified or explicitly imported names are
     held to this; a bare builtin is still skipped, so the report cannot
     flood.

WHEN THIS TOOL MAY REMOVE A TARGET, AND WHEN IT MAY NOT (operating rule 3).
Not seeing a class is ABSENCE, and absence never contradicts the record. So a
row is rewritten wholesale ONLY when the derivation is COMPLETE for it: every
`document_class` write reachable from its entry point resolved to a literal, and
every function it calls was found. Then "X is not in the emission set" is a
POSITIVE fact about enumerated code, and a stale target can be dropped.

If ANY site did not resolve -- `jRecordingObservation.m:209` is
`classBlock(e.class, ...)`, where `e` comes from a struct array built in
`jRecordingModality.mk` -- the row is PARTIAL: the derived set is UNIONED into
the existing one, nothing is removed, and the unresolved sites are printed so a
human can close them. A partial row can gain a target it provably emits without
ever losing one this tool merely failed to see.

Run with no arguments to print the diff and write. `--check` prints the diff and
exits non-zero if anything would change (for CI). `--dry-run` prints only.
"""

import argparse
import collections
import glob
import importlib.util
import json
import os
import re
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA_ROOT = os.path.dirname(HERE)
TARGETS_JSON = os.path.join(SCHEMA_ROOT, "schemas", "V_eta_migration_targets.json")


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Loaded BY PATH, not by `import status_board`: this file is also run by the test
# suite with an arbitrary sys.path, and `coverage` (which status_board itself
# loads the same way) is a widely installed PyPI package. Failure is loud on
# purpose -- a local copy of the regex is the silent divergence the reuse exists
# to prevent.
SB = _load("_rmt_status_board", os.path.join(HERE, "status_board.py"))
COV = _load("_rmt_coverage", os.path.join(HERE, "coverage.py"))

DIDM = COV.DIDM
CONVERT = os.path.join(DIDM or "", "src/did/+did2/+convert")

# Under TargetVersion 'V_eta', `v1_to_v2.runConcreteMigrator` (v1_to_v2.m:393-403)
# routes a class to +migrators_j when a file of that name exists there, and
# otherwise falls back to `lookupMigrator` in +migrators. +migrators_i is the
# V_zeta package and never runs under V_eta, so it is NOT a source of V_eta
# targets. The superclass pass may additionally run +migrators_j/+super/<name>.m,
# which by contract returns exactly ONE body and mints nothing.
PACKAGE_ORDER = ("migrators_j", "migrators")

# `syncrule_mapping` IS SUBTRACTED FROM coverage.py's shared-helper list, and the
# subtraction carries its evidence rather than being a taste call.
# `+migrators_j/syncrule_mapping.m:1` is `function bodies = syncrule_mapping(preBody)`
# under the header "Brainstorm-J migrator: did_v1 `syncrule_mapping` ->
# `clock_alignment`. Routed from did2.convert.v1_to_v2 only when TargetVersion ==
# 'V_eta'"; it quotes its own TEAM-SIGN-OFF; and `grep -rn "syncrule_mapping("`
# across +migrators_j returns only its own definition line -- no caller, because
# like every per-class migrator it is reached solely by v1_to_v2's dynamic
# dispatch. It is a migrator, not a helper. Left in the set, this tool would
# report "no pass-1 migrator" for a class whose migrator emits three document
# classes.
#
# THE SUBTRACTION IS NOW A NO-OP, AND IS KEPT ANYWAY. coverage.py has since
# dropped the entry itself (commit "syncrule_mapping was listed as a shared
# HELPER. It is a migrator.": "Coverage counted 83; it is 84"), so the set no
# longer contains it. The line stays because it is the only place the two tools'
# disagreement was ever written down: if `syncrule_mapping` -- or anything else
# that is a real per-class migrator -- is appended to that set again, this tool
# keeps deriving the class's targets and the difference is visible here instead
# of silently reappearing as an empty row.
_HELPERS = set(COV._MIG_HELPERS) - {"syncrule_mapping"}


# ---------------------------------------------------------------------------
# MATLAB function-level parsing
# ---------------------------------------------------------------------------

_FUNC_LINE = re.compile(
    r"^\s*function\s+"
    r"(?:\[(?P<outs>[^\]]*)\]\s*=\s*|(?P<out1>[A-Za-z_]\w*)\s*=\s*)?"
    r"(?P<name>[A-Za-z_]\w*)\s*(?:\((?P<args>[^)]*)\))?")


class Func:
    __slots__ = ("lines", "name", "outs", "params", "path", "start")

    def __init__(self, name, params, outs, lines, start, path):
        self.name = name
        self.params = params
        self.outs = outs
        self.lines = lines
        self.start = start
        self.path = path


def parse_functions(path):
    """[Func] for one .m file, in file order. Subfunctions are not nested in
    MATLAB, so a `function` keyword at the start of a line always opens a new
    one."""
    with open(path, errors="replace") as fh:
        lines = fh.readlines()
    starts = []
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
        m = _FUNC_LINE.match(line)
        if m and line.lstrip().startswith("function"):
            starts.append((i, m))
    out = []
    for k, (i, m) in enumerate(starts):
        end = starts[k + 1][0] if k + 1 < len(starts) else len(lines)
        args = (m.group("args") or "").strip()
        params = [a.strip() for a in args.split(",") if a.strip()] if args else []
        outs = m.group("outs") or m.group("out1") or ""
        outs = [o.strip() for o in outs.split(",") if o.strip()]
        out.append(Func(m.group("name"), params, outs, lines[i:end], i + 1, path))
    return out


# ---------------------------------------------------------------------------
# Emission recognisers -- three idioms, one statement model
# ---------------------------------------------------------------------------

# `'class_name', <bare identifier>` -- the value is a VARIABLE, so the literal is
# somewhere else (a parameter, or a local assignment). Deliberately separate from
# coverage.py's `_CLASS_EMIT`, which matches only quoted values.
_SYMBOLIC_CLASS_NAME = re.compile(r"""['"]class_name['"]\s*,\s*([A-Za-z_]\w*(?:\.\w+)*)""")
# `x.document_class.class_name = <rhs>` -- the direct field write.
_DC_FIELD_WRITE = re.compile(r"document_class\s*\.\s*class_name\s*$")
_CALL = re.compile(r"(?<![\w.])([A-Za-z_]\w*)\s*\(")
# A fully-qualified call into `+convert` that is NOT a migrator package. The
# migrator branch is matched separately (and first), so `migrators` is excluded
# here rather than being matched twice with different argument handling.
_FQ_CONVERT_CALL = re.compile(
    r"(?<![\w.])did2\.convert\.(?!migrators)"
    r"(?:(?P<pkg>[A-Za-z_]\w*)\.)?(?P<fn>[A-Za-z_]\w*)\s*\(")
# `import did2.convert.entities.entityDoc` / `import did2.convert.entities.*`.
_IMPORT_LINE = re.compile(
    r"^\s*import\s+(did2\.convert\.[A-Za-z_][\w.]*(?:\.\*)?)\s*;?\s*$")
_LIT = re.compile(r"^\s*'((?:[^']|'')*)'\s*$")
_IDENT_ONLY = re.compile(r"^\s*([A-Za-z_]\w*)\s*$")

LIT = "lit"
PARAM = "param"
DYN = "dyn"


def _top_level_args(text, code, open_paren):
    """Positional argument source strings of the call whose `(` is at
    `open_paren`. `code` (strings blanked, same length as `text`) supplies the
    nesting depth so a comma inside a string literal cannot split an argument."""
    depth, start, args = 0, open_paren + 1, []
    for i in range(open_paren, len(code)):
        ch = code[i]
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
            if depth == 0:
                args.append(text[start:i])
                return [a for a in args], i
        elif ch == "," and depth == 1:
            args.append(text[start:i])
            start = i + 1
    return [a for a in args], len(code)


def _local_literals(func):
    """{var: {literal, ...}} for plain `var = 'literal';` assignments, plus the
    set of vars that are ALSO assigned something this tool cannot read.

    `ontology_table_row.dispatchNumeric` assigns `leafClass` fifteen different
    literals down a switch; each one is a real target. A var that is additionally
    assigned a non-literal is recorded as ambiguous, so it degrades to `dyn`
    rather than silently reporting a subset."""
    lits = collections.defaultdict(set)
    murky = set()
    for text, _spans in SB.logical_statements(func.lines):
        code, _ = SB.split_matlab_line(text)
        eq = SB.assignment_split(code)
        if eq is None:
            continue
        lhs, rhs = text[:eq], text[eq + 1:]
        m = _IDENT_ONLY.match(lhs)
        if not m:
            continue
        name = m.group(1)
        lm = _LIT.match(rhs.rstrip().rstrip(";"))
        if lm:
            lits[name].add(lm.group(1))
        else:
            murky.add(name)
    return lits, murky


def _resolve_symbol(sym, func, lits, murky):
    """A variable used as a class name -> emission symbols."""
    if sym in func.params:
        return [(PARAM, func.params.index(sym))]
    if sym in lits and sym not in murky:
        return [(LIT, v) for v in sorted(lits[sym])]
    if sym in lits:
        return ([(LIT, v) for v in sorted(lits[sym])]
                + [(DYN, f"{sym} (also assigned non-literally)")])
    return [(DYN, sym)]


def analyse_function(func, known, imported=None):
    """(direct emissions, calls) for one function.

    direct : [(symbol, line_no)] where symbol is (LIT, name) / (PARAM, i) /
             (DYN, why)
    calls  : [(callee_name, [arg_source, ...], line_no)]
    """
    imported = imported or {}
    lits, murky = _local_literals(func)
    direct, calls = [], []
    for text, spans in SB.logical_statements(func.lines):
        code, _ = SB.split_matlab_line(text)
        eq = SB.assignment_split(code)
        lhs = text[:eq] if eq is not None else ""
        rhs_off = (eq + 1) if eq is not None else 0
        # IDIOM 4 -- a helper that RETURNS a class block instead of assigning one.
        # `classBlock` (7 files, two arities) is
        #     function dc = classBlock(name, supers)
        #     dc = struct('class_name', name, ..., 'superclasses', sc, ...);
        # so nothing in that statement mentions `document_class` at all; the word
        # appears only at the CALL SITE (`obs.document_class = classBlock(...)`).
        # A `document_class`-anchored rule sees none of it -- which emptied ten
        # rows on the first run of this tool, including `fitcurve` and `pyraview`.
        # The narrow signature used here is "the statement assigns the function's
        # OWN OUTPUT VARIABLE a struct that declares `superclasses`": a class
        # block, and nothing else in these packages, does that.
        returns_class_block = (
            lhs.strip() in func.outs and "superclasses" in text[rhs_off:])
        writes_dc = "document_class" in lhs or returns_class_block

        if writes_dc:
            # idiom 3: `x.document_class.class_name = <rhs>`
            if _DC_FIELD_WRITE.search(lhs.rstrip()):
                rhs = text[rhs_off:].rstrip().rstrip(";")
                lm = _LIT.match(rhs)
                line = _phys(spans, rhs_off, func)
                if lm:
                    direct.append(((LIT, lm.group(1)), line))
                else:
                    im = _IDENT_ONLY.match(rhs)
                    if im:
                        for s in _resolve_symbol(im.group(1), func, lits, murky):
                            direct.append((s, line))
                    else:
                        direct.append(((DYN, rhs.strip()[:60]), line))
                continue

            # idiom 1: `x.document_class = struct('class_name', <v>, ...)`
            # Superclass entries are dropped BY POSITION, exactly as
            # status_board.emitted_document_classes does it: everything at or
            # after the word `superclasses` inside this joined statement is an
            # ancestor, not the document's own class.
            cut = text.find("superclasses")
            window_end = cut if cut != -1 else len(text)
            window = text[rhs_off:window_end]
            hit = False
            for pat in SB.CLASS_EMIT:
                for m in pat.finditer(window):
                    direct.append(((LIT, m.group(1)),
                                   _phys(spans, rhs_off + m.start(), func)))
                    hit = True
            for m in _SYMBOLIC_CLASS_NAME.finditer(window):
                sym = m.group(1)
                line = _phys(spans, rhs_off + m.start(), func)
                if "." in sym:
                    direct.append(((DYN, sym), line))
                else:
                    for s in _resolve_symbol(sym, func, lits, murky):
                        direct.append((s, line))
                hit = True
            if hit:
                continue
            # idiom 2: `x.document_class = <helper>(...)`. Nothing recognised
            # here; the generic call scan below picks the helper up.

        # calls -- a helper that mints documents mints them for its caller too,
        # whether its result is a document_class block (`classBlock`) or whole
        # bodies (`jSessionAnchor`, `jCalculation`, `jSampledBody`).
        for m in _CALL.finditer(code):
            name = m.group(1)
            # A name bound by `import did2.convert.<...>` wins over the generic
            # skip: it is an explicit reference to a known file, not a builtin.
            target = name if name in known else imported.get(name)
            if target is None:
                continue
            args, _end = _top_level_args(text, code, m.end() - 1)
            calls.append((target, args, _phys(spans, m.start(), func)))
        # fully-qualified cross-package calls: `did2.convert.migrators.element_epoch(`
        for m in re.finditer(
                r"(?:did2\.convert\.)?migrators(?:_[ije])?\.(?:super\.)?"
                r"([A-Za-z_]\w*)\s*\(", code):
            calls.append(("pkg:" + m.group(1), [], _phys(spans, m.start(), func)))
        # fully-qualified calls into the rest of `+convert`:
        # `did2.convert.entities.entityDoc(preBody, 'dataset', ...)`. Arguments
        # ARE captured here -- unlike the migrator branch above -- because this
        # is exactly the shape that carries the class name as a literal
        # argument, and dropping the arguments would report every one of them
        # as "omits class-name argument #2".
        for m in _FQ_CONVERT_CALL.finditer(code):
            parts = ([m.group("pkg")] if m.group("pkg") else []) + [m.group("fn")]
            cand = convert_member_path(parts)
            ref = (FILEREF + cand) if (cand and os.path.isfile(cand)) \
                else (MISSING + "did2.convert." + ".".join(parts))
            args, _end = _top_level_args(text, code, m.end() - 1)
            calls.append((ref, args, _phys(spans, m.start(), func)))
    return direct, calls


def _phys(spans, offset, func):
    return SB._line_of(spans, offset) + func.start - 1


# ---------------------------------------------------------------------------
# The scope: which functions a migrator file can call
# ---------------------------------------------------------------------------

def build_scopes():
    """{package: {func_name: Func}} for private/ helpers, and {path: {name: Func}}
    for each file's own subfunctions."""
    private = {}
    for pkg in PACKAGE_ORDER:
        base = os.path.join(CONVERT, "+" + pkg, "private")
        table = {}
        for p in sorted(glob.glob(os.path.join(base, "*.m"))):
            for f in parse_functions(p):
                # only the FIRST function in a private file is visible outside it
                table.setdefault(f.name, f)
                break
        private[pkg] = table
    return private


def convert_member_path(parts):
    """`['entities', 'entityDoc']` -> `.../+convert/+entities/entityDoc.m`.

    MATLAB spells a package folder `+name`, so every element but the last is a
    package and the last is the function file."""
    if not parts:
        return None
    return os.path.join(CONVERT, *(["+" + p for p in parts[:-1]] + [parts[-1] + ".m"]))


MISSING = "missing:"
FILEREF = "file:"


def parse_imports(path):
    """{bare_name: 'file:<abs path>' or 'missing:<dotted>'} for one .m file.

    MATLAB's `import` binds the trailing name into the whole function scope, so
    after `import did2.convert.entities.entityDoc` a bare `entityDoc(...)` IS
    that function. Unresolvable imports are kept as `missing:` rather than
    dropped: a dropped one becomes a silent skip again, and a silent skip is
    what deleted metadata_editor's seven targets."""
    out = {}
    try:
        with open(path, errors="replace") as fh:
            lines = fh.readlines()
    except OSError:
        return out
    for line in lines:
        m = _IMPORT_LINE.match(line)
        if not m:
            continue
        dotted = m.group(1)
        parts = dotted.split(".")[2:]          # drop the `did2.convert` prefix
        if parts and parts[-1] == "*":
            pkgdir = os.path.join(CONVERT, *["+" + p for p in parts[:-1]])
            if os.path.isdir(pkgdir):
                for p in sorted(glob.glob(os.path.join(pkgdir, "*.m"))):
                    base = os.path.basename(p)[:-2]
                    if base != "Contents":
                        out.setdefault(base, FILEREF + p)
            else:
                out.setdefault(parts[-2] if len(parts) > 1 else dotted,
                               MISSING + dotted)
            continue
        cand = convert_member_path(parts)
        out[parts[-1]] = (FILEREF + cand) if (cand and os.path.isfile(cand)) \
            else (MISSING + dotted)
    return out


def entry_points():
    """{source_class: (package, path)} -- the migrator V_eta actually runs."""
    out = {}
    for pkg in PACKAGE_ORDER:
        base = os.path.join(CONVERT, "+" + pkg)
        for p in sorted(glob.glob(os.path.join(base, "*.m"))):
            cn = os.path.basename(p)[:-2]
            if cn == "Contents" or cn in _HELPERS:
                continue
            out.setdefault(cn, (pkg, p))
    return out


# ---------------------------------------------------------------------------
# Interprocedural resolution
# ---------------------------------------------------------------------------

class Analyser:
    def __init__(self):
        self.private = build_scopes()
        self.entries = entry_points()
        try:
            self.veta = set(COV.veta_index())
        except Exception:
            self.veta = set()
        self._file_cache = {}
        self._fn_cache = {}
        self._import_cache = {}

    def imports(self, path):
        if path not in self._import_cache:
            self._import_cache[path] = parse_imports(path)
        return self._import_cache[path]

    def file_funcs(self, path):
        if path not in self._file_cache:
            fns = parse_functions(path)
            self._file_cache[path] = (fns, {f.name: f for f in fns})
        return self._file_cache[path]

    def resolve_name(self, name, path, pkg):
        """A called name -> the Func it binds to, or None. Local subfunction
        first (MATLAB's own precedence), then the package's private/ folder."""
        if name.startswith(MISSING):
            return None
        if name.startswith(FILEREF):
            fns = self.file_funcs(name[len(FILEREF):])[0]
            return fns[0] if fns else None
        _fns, table = self.file_funcs(path)
        if name in table:
            return table[name]
        if name.startswith("pkg:"):
            bare = name[4:]
            for p2 in PACKAGE_ORDER:
                cand = os.path.join(CONVERT, "+" + p2, bare + ".m")
                if os.path.isfile(cand):
                    return self.file_funcs(cand)[0][0]
            cand = os.path.join(CONVERT, "+migrators_j", "+super", bare + ".m")
            if os.path.isfile(cand):
                return self.file_funcs(cand)[0][0]
            return None
        return self.private.get(pkg, {}).get(name)

    def analyse(self, func, pkg, stack):
        """{(kind, value)} emission symbols of `func`, params unsubstituted,
        plus [(why, path:line)] unresolved sites."""
        key = (func.path, func.name)
        if key in stack:
            return set(), []
        if key in self._fn_cache:
            return self._fn_cache[key]
        stack = stack | {key}
        direct, calls = analyse_function(func, self._callable_names(func.path, pkg),
                                         self.imports(func.path))
        out, unresolved = set(), []
        for sym, line in direct:
            if sym[0] == DYN:
                unresolved.append((f"dynamic class name `{sym[1]}`",
                                   f'{_rel(func.path)}:{line}'))
            out.add(sym)
        for name, args, line in calls:
            callee = self.resolve_name(name, func.path, pkg)
            if callee is None:
                if name.startswith("pkg:"):
                    unresolved.append((f"unresolved package call `{name[4:]}`",
                                       f'{_rel(func.path)}:{line}'))
                elif name.startswith(MISSING):
                    # An explicit `did2.convert.` reference whose file is not
                    # where the name says it is. Reported, never skipped: a
                    # skipped emitter reads as "mints nothing".
                    unresolved.append(
                        (f"`{name[len(MISSING):]}` names no file under +convert",
                         f'{_rel(func.path)}:{line}'))
                elif name.startswith(FILEREF):
                    unresolved.append(
                        (f"`{_rel(name[len(FILEREF):])}` defines no function",
                         f'{_rel(func.path)}:{line}'))
                continue
            sub, subunres = self.analyse(callee, pkg, stack)
            unresolved.extend(subunres)
            for sym in sub:
                if sym[0] != PARAM:
                    out.add(sym)
                    continue
                idx = sym[1]
                if idx >= len(args):
                    # the callee's parameter has a default the caller did not
                    # override; the default is not a class name in any migrator
                    # today, so this is reported rather than guessed
                    unresolved.append(
                        (f'call to `{callee.name}` omits class-name argument #{idx + 1}',
                         f'{_rel(func.path)}:{line}'))
                    continue
                arg = args[idx]
                lm = _LIT.match(arg)
                if lm:
                    out.add((LIT, lm.group(1)))
                    continue
                im = _IDENT_ONLY.match(arg)
                if im:
                    lits, murky = _local_literals(func)
                    for s in _resolve_symbol(im.group(1), func, lits, murky):
                        if s[0] == DYN:
                            unresolved.append(
                                (f"class name `{im.group(1)}` passed to `{callee.name}` is not a literal",
                                 f'{_rel(func.path)}:{line}'))
                        else:
                            out.add(s)
                    continue
                unresolved.append(
                    (f"class-name argument to `{callee.name}` is an expression (`{arg.strip()[:40]}`)",
                     f'{_rel(func.path)}:{line}'))
        res = (out, unresolved)
        self._fn_cache[key] = res
        return res

    def _callable_names(self, path, pkg):
        _fns, table = self.file_funcs(path)
        return set(table) | set(self.private.get(pkg, {}))

    def targets_for(self, cls):
        """(target classes, unresolved sites, carries_forward, entry path).

        `(None, [], False, None)` when V_eta runs no pass-1 migrator at all."""
        ent = self.entries.get(cls)
        if ent is None:
            return None, [], False, None
        pkg, path = ent
        fns, _table = self.file_funcs(path)
        if not fns:
            return set(), [], True, path
        syms, unresolved = self.analyse(fns[0], pkg, frozenset())
        names = set()
        for kind, val in syms:
            if kind == LIT:
                names.add(val)
            elif kind == PARAM:
                unresolved.append(
                    ("entry point takes its class name as a parameter", _rel(path)))
        # A PURE CARRY-FORWARD MIGRATOR MINTS NOTHING, and that is a THIRD state,
        # not a kind of failure. `migrators_j/subject.m` copies `v2Body = preBody`,
        # fills `local_identifier` and returns; `migrators_j/spike_clusters.m`
        # returns `{preBody}` under a header that begins "DEFERRED to the NDI
        # second pass; the document is passed through UNCHANGED". Neither writes
        # a `document_class`, so the emission set is EMPTY -- and empty here is a
        # measured fact (every reachable statement was read and none minted a
        # document), not an unresolved one.
        #
        # BUT AN EMPTY `targets` DOES NOT MEAN THE SAME THING DOWNSTREAM. A row
        # with no `targets` and no `second_pass` is read by coverage.py as
        # `decided`, and with no `decided_targets` it renders in the ledger as
        # "dissolves / deleted (no target by design)" -- i.e. the documents were
        # consumed. For a passthrough that is FALSE, and false in the direction
        # this project keeps paying for: the reassuring one. So the carried
        # document is recorded as what it is, a V_eta document of its own class,
        # which is exactly how the file already spells `subject` and
        # `hartley_calc`. The two spellings were inconsistent; the one that makes
        # the generated ledger say a true thing wins.
        #
        # It is claimed only on POSITIVE evidence that the document is returned:
        # an output variable assigned from `preBody` (`bodies = {preBody}`,
        # `v2Body = preBody`, or `{ did2.convert.migrators.<x>(preBody) }`, which
        # is 1 -> 1 by contract). `migrators_j/stimulus_bath.m` mints nothing AND
        # returns nothing -- it always errors, deferring to resolveDeferredBaths
        # -- so it gets no self-target.
        #
        # AND ONLY FOR A +migrators_j ENTRY POINT. A file in +migrators reached
        # under V_eta is one of two different things and this tool cannot tell
        # them apart: a CONCRETE fallback migrator (`hartley_calc`) or a
        # SUPERCLASS BLOCK migrator run by the superclass pass (`filter`, `ngrid`,
        # `epochclocktimes` -- each rewrites a block in place and mints no
        # document, and `epochclocktimes` is not even a V_eta class: build_v_eta.py
        # DELETES it). +migrators_j has no such ambiguity, because v1_to_v2 puts
        # its superclass overrides in the separate +migrators_j/+super/
        # subpackage exactly so the names cannot collide (v1_to_v2.m:531). So a
        # +migrators entry point with no emission makes NO claim: the row is
        # reported and left alone. The self-target is additionally checked
        # against the built V_eta set, so a class the schema does not have can
        # never be named as a target.
        if not names:
            if pkg != "migrators_j":
                unresolved.append(
                    (("entry point is in +migrators, where a concrete fallback "
                     "migrator and a superclass block migrator are "
                     "indistinguishable -- no claim made"), _rel(path)))
            elif self._returns_source(fns[0]) and cls in self.veta:
                names = {cls}
        return names, unresolved, not names or names == {cls}, path

    def _returns_source(self, func):
        """True when an output variable of `func` is assigned from `preBody`."""
        outs = set(func.outs)
        for text, _spans in SB.logical_statements(func.lines):
            code, _ = SB.split_matlab_line(text)
            eq = SB.assignment_split(code)
            if eq is None:
                continue
            lhs = text[:eq].strip()
            if lhs in outs and re.search(r"(?<![\w.])preBody(?![\w])", text[eq + 1:]):
                return True
        return False


def _rel(path):
    return os.path.relpath(path, os.path.dirname(DIDM)) if DIDM else path


# ---------------------------------------------------------------------------
# The refresh
# ---------------------------------------------------------------------------

def refresh(write=True, out=sys.stdout):
    doc = json.loads(Path(TARGETS_JSON).read_text())
    classes = doc["classes"]
    an = Analyser()

    rows = sorted(classes)
    def p(*a):
        print(*a, file=out)


    # DENOMINATOR FIRST (operating rule 5).
    p(f'DENOMINATOR: {len(rows)} class rows in {os.path.basename(TARGETS_JSON)}')
    p(f'             {len(an.entries)} migrator entry points across {" + ".join("+" + x for x in PACKAGE_ORDER)}')
    p(f'             {len(an.private["migrators_j"])} private helpers in +migrators_j, {len(an.private["migrators"])} in +migrators')
    p(f'             DID-matlab = {DIDM or "NOT FOUND"}')
    p("")

    n_full = n_partial = n_carry = n_nomig = 0
    changed = []
    partial_report = []
    carry_report = []
    all_derived = set()
    for cls in rows:
        derived, unresolved, carries, path = an.targets_for(cls)
        existing = list(classes[cls].get("targets") or [])
        if derived is None:
            n_nomig += 1
            continue
        all_derived |= derived
        if unresolved:
            # PARTIAL: a class name this tool could not read. Absence is not
            # evidence (operating rule 3), so the row can only GAIN.
            n_partial += 1
            new = existing + [t for t in sorted(derived) if t not in existing]
            partial_report.append((cls, sorted(set(unresolved))))
        elif carries:
            # CARRY-FORWARD: nothing is minted, measured rather than merely
            # unseen. The derived set is the class itself when the document is
            # returned, and empty when it is not (a migrator that always defers).
            # Written the same way as a full derivation -- the separate count
            # exists so a row losing a whole migration is legible in the report.
            n_carry += 1
            new = ([t for t in existing if t in derived]
                   + [t for t in sorted(derived) if t not in existing])
            if [t for t in existing if t not in derived]:
                carry_report.append((cls, [t for t in existing if t not in derived],
                                     _rel(path)))
        else:
            # FULL: existing order preserved for survivors, additions appended,
            # so the diff shows meaning rather than a re-sort.
            n_full += 1
            new = ([t for t in existing if t in derived]
                   + [t for t in sorted(derived) if t not in existing])
        if new != existing:
            mode = "PARTIAL" if unresolved else ("carry-fwd" if carries else "full")
            changed.append((cls, existing, new, mode, _rel(path)))
            classes[cls]["targets"] = new

    p("DERIVATION MODE")
    p(f'  {n_full:>3} rows FULLY DERIVED   (every document_class write resolved -> the set is')
    p("      rewritten; a removal is positive evidence from enumerated code)")
    p(f'  {n_partial:>3} rows PARTIAL         (>=1 unresolved site -> derived set UNIONED in,')
    p("      nothing removed; absence is not evidence, operating rule 3)")
    p(f'  {n_carry:>3} rows CARRY-FORWARD   (the migrator mints nothing: keeps a self-naming')
    p("      target, drops any claim of a migration to another class)")
    p(f'  {n_nomig:>3} rows have NO pass-1 migrator under V_eta (untouched)')
    p("")

    p(f'DIFF: {len(changed)} row(s) change')
    for cls, old, new, mode, path in changed:
        added = [t for t in new if t not in old]
        removed = [t for t in old if t not in new]
        p(f'  {cls:<42} {path}   [{mode}]')
        if added:
            p("      + " + ", ".join(added))
        if removed:
            p("      - " + ", ".join(removed))
    p("")

    if carry_report:
        p(f'CARRY-FORWARD ROWS THAT LOST A TARGET ({len(carry_report)}) -- each named a migration its')
        p("migrator no longer performs. Their `how`/`flags` prose describes the same")
        p("removed migration and is NOT touched by this tool: rewrite it by hand.")
        for cls, dropped, path in carry_report:
            p(f'  {cls:<42} {path}')
            p("      dropped: " + ", ".join(dropped))
        p("")

    if partial_report:
        p(f'UNRESOLVED EMISSION SITES ({len(partial_report)} row(s)) -- these rows keep their existing')
        p("targets and can only GAIN. Close one and its row becomes fully derived.")
        for cls, sites in partial_report:
            p(f"  {cls}")
            for why, where in sites:
                p(f'      {why:<58} {where}')
        p("")

    # SANITY CHECK ON THE INSTRUMENT ITSELF. Every derived name is claimed to be a
    # V_eta document class, so it must exist in the built schema set. A name that
    # does not is either a regex reading something that is not a class, or a
    # migrator emitting a class V_eta lacks -- coverage.py's `KNOWN_NON_VETA`
    # records the two acknowledged cases (`bath`, `pharmacological_manipulation`,
    # from the V_zeta assembler). Anything else is a bug in this tool and must be
    # read before its output is trusted.
    try:
        veta = set(COV.veta_index())
    except Exception:
        veta = None
    if veta:
        stray = sorted(n for n in all_derived
                       if n not in veta and n not in COV.KNOWN_NON_VETA)
        p(f'INSTRUMENT CHECK: {len(all_derived)} distinct target names derived; {len(stray)} absent from the built V_eta set')
        if stray:
            p("  " + ", ".join(stray))
        p("")

    if write and changed:
        with open(TARGETS_JSON, "w") as fh:
            json.dump(doc, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        p(f"WROTE {TARGETS_JSON}")
    elif not changed:
        p("no change")
    return changed


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="print the diff and exit 1 if anything would change")
    ap.add_argument("--dry-run", action="store_true", help="print the diff only")
    args = ap.parse_args(argv)
    if DIDM is None:
        print("DID-matlab not found (set DID_MATLAB); nothing to derive from.",
              file=sys.stderr)
        return 2
    changed = refresh(write=not (args.check or args.dry_run))
    if args.check and changed:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
