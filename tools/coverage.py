#!/usr/bin/env python3
"""V_eta migration coverage ledger + guardrail.

Answers two questions fast (no MATLAB, no 2-hour corpus):

  1. LEDGER  -- for every did_v1 source class, what is its V_eta fate (disposition +
     migrator)? Written to schemas/V_eta_coverage_ledger.md so "migrate every v1
     class" becomes a visible checklist.

  2. GUARDRAIL -- every class_name a V_eta migrator EMITS must exist in the built
     V_eta schema. Catches "reviving a dead class" / "inventing a non-existent class"
     (the stimulus_manipulation / bath class of error) in <1s. Exits non-zero on a
     violation so CI fails.

Reads the sibling repos (NDI-matlab for the v1 class templates + second-pass
functions; DID-matlab for the migrators_j package). Discover order: env vars
NDI_MATLAB / DID_MATLAB, then /home/user/<repo>, then ../<repo>. Degrades
gracefully (skips a section) when a sibling is absent.

Usage:  python3 tools/coverage.py [--check]
  (no args) regenerate the ledger + print the guardrail report.
  --check   guardrail only; exit non-zero on any violation (for CI).
"""
import glob
import json
import os
import re
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
# ONE PARSER FOR `TEAM-SIGN-OFF`, and it lives in status_board.py because that
# is where operating rule 4 is enforced. This tool used to hand-carry four
# transcriptions and read nothing else, so 94 of 102 rows reported stage 1 as
# `not measured` -- correctly, since that was the absence of a TRANSCRIPTION
# rather than evidence of no decision, but it also meant the team's signatures
# could not reach the ledger at all. A second copy of the sign-off parsing here
# would be a second place for the two laundering holes it closes (HTML
# comments, untagged lines in shared documents) to reopen.
import status_board  # noqa: E402

SCHEMA_ROOT = os.path.dirname(HERE)
INDEX = os.path.join(SCHEMA_ROOT, "schemas", "V_eta", "index.json")
LEDGER = os.path.join(SCHEMA_ROOT, "schemas", "V_eta_coverage_ledger.md")
TARGETS = os.path.join(SCHEMA_ROOT, "schemas", "V_eta_migration_targets.json")


# DENOMINATORS for the two reads this tool's whole left-hand side is built from.
# Printed by main() before any figure that depends on them; see the comments at
# each read for why a silent failure there is not a filter.
TARGETS_SCAN = {"rows": 0, "read": False, "why": None}
# Stage 5's input, and the reason it is a module global like the two above:
# `_summary()` is called from three places and none of them is the one that
# knows where the corpus reports are. Defaults to NOT MEASURED, which is the
# state every run is in until a corpus artifact is put in reach.
CORPUS_SCAN = {"measured": False, "denominator": None,
               "why": "no corpus report root was supplied to this run"}
TEMPLATE_SCAN = {"candidates": 0, "unreadable": 0, "unparseable": 0,
                 "not_a_document_class": 0, "classes": 0,
                 "refs_tried": [], "source": None}


def targets_map():
    """Curated did_v1 -> V_eta emitted-target map (schemas/V_eta_migration_targets.json):
    for each source class, the V_eta document class(es) its migrator actually emits
    (superclasses excluded), plus carried/second_pass/how/flags. Keyed by snake-cased
    source class name. Empty if the file is absent.

    A SHRINKING DENOMINATOR, NOT A FILTER, WHICH IS WHY IT REPORTS. `{}` here is
    not "no class has a target" -- it silently strips the `targets` column off
    EVERY row, and the ledger's no-target census then counts each stripped row
    as a class naming no target. The empty-file case is a designed degrade; the
    unreadable-file case is a failure wearing the same clothes. Both are now
    stated in the output with the row count beside them.
    """
    try:
        rows = json.loads(Path(TARGETS).read_text()).get("classes", {})
    except OSError as exc:
        TARGETS_SCAN["why"] = f"{type(exc).__name__}: {exc}"
        return {}
    except json.JSONDecodeError as exc:
        TARGETS_SCAN["why"] = f"JSONDecodeError: {exc}"
        return {}
    TARGETS_SCAN["read"] = True
    TARGETS_SCAN["rows"] = len(rows)
    return rows


def find_repo(name, env):
    for cand in (os.environ.get(env), os.path.join("/home/user", name),
                 os.path.join(os.path.dirname(SCHEMA_ROOT), name)):
        if cand and os.path.isdir(cand):
            return cand
    return None


NDI = find_repo("NDI-matlab", "NDI_MATLAB")
DIDM = find_repo("DID-matlab", "DID_MATLAB")


def snake(name):
    """Mirror universalRenames' camelCase -> snake_case (block/class field names)."""
    s = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    return s.lower()


def veta_index():
    idx = json.loads(Path(INDEX).read_text())
    return {e["class_name"]: e.get("disposition", "?") for e in idx["schemas"]}


# NDI ships test/demo scaffolding as production templates; these are NOT real v1
# corpus data, so they never count as an unmapped coverage gap (they stay in the
# ledger, tagged nonprod, for completeness).
#
# EVERY ENTRY IS AN ASSERTION THAT NOTHING IN PRODUCTION WRITES THE CLASS, and
# tagging one here has teeth: it suppresses the coverage gap, which is why
# `oneepoch` reached 2026-08-10 with no V_eta schema, no migrator and no row on
# anyone's worklist. The check is a writer sweep on the BARE CLASS NAME,
# splitting src/ from tests/ -- not a guess from the name.
#
# REMOVED 2026-08-10, because it was FALSE: `oneepoch`. It is a documented
# production entry point, and both its writer and its reader are in src/:
#
#   DENOMINATOR: 1,002 .m files on NDI origin/main; every file mentioning "oneepoch"
#     SRC   src/ndi/+ndi/+element/oneepoch.m        the production function
#     SRC   src/ndi/+ndi/+element/oneepoch_bkup.m
#     SRC   src/ndi/+ndi/+element/timeseries.m      addepoch's 7-arg override
#     SRC   src/ndi/+ndi/element.m:387              THE WRITER, inside addepoch()
#     SRC   ndi_common/database_documents/oneepoch.json
#     SRC   ndi_common/schema_documents/oneepoch_schema.json
#     TEST  tests/+ndi/+symmetry/+time/scenario.m
#     TEST  tests/+ndi/+unittest/+element/OneEpochTest.m
#
# `ndi.element.oneepoch` concatenates an element's N epochs into one, and the
# document records that concatenation (`oneepoch.epoch_ids` = the source ids).
# Its epoch id is SYNTHETIC -- `whole_session_<reference>` (oneepoch.m:42) -- and
# did2.validate.sourceCensus has been tracking exactly that string as a grouping
# hazard since it was written, CITING oneepoch.m:42 by line. So the instrument
# already knew this class was real while this list said it was scaffolding: the
# same prose-versus-artifact split that the CLAUDE.md rules exist to break.
#
# REMOVED 2026-08-12, for the same evidence shape as `oneepoch`: `demoNDIMock`.
# THE TEAM RULED, verbatim: *"an example calculator counts as production"*
# (recorded in `V_eta_OPEN_WORK.md` row 111). Its two construction sites are
# both in `src/`, in an example calculator, and neither is a test:
#
#   src/ndi/+ndi/+calc/+example/simple.m:107
#       mock_doc1 = ndi.document('demoNDIMock', 'demoNDI', ...) + ...
#   src/ndi/+ndi/+calc/+example/simple.m:126
#       mock_doc2 = ndi.document('demoNDIMock', 'demoNDI', ...) + ...
#
#   DENOMINATOR: 1,002 .m files on NDI origin/main; `demoNDIMock` appears in
#     exactly ONE of them, the file above -- 0 under tests/.
#
# The paragraph below already said this class was constructed there. What was
# missing was the RULING about what that construction means, and the entry
# survived because "demo scaffolding by construction" reads as an argument
# while being a restatement of the name.
#
# CONSEQUENCE, AND IT IS THE POINT OF THE CHANGE: `demoNDIMock` now shows as a
# coverage GAP. It has no V_eta schema (build_v_eta.py os.removes it), no
# migrator, and no suppression. DO NOT close that gap here and do not suppress
# it another way -- the missing migrator is a separate build, routed elsewhere.
#
# THE TWO THAT REMAIN, and why each stays:
#   `demoNDI`     THE RULING DOES NOT REACH IT. It is a TEST HELPER, and the
#                 ruling covers example calculators. Its construction sites are
#                 10 files: 9 under tests/, and ONE under src/ --
#                 src/ndi/+ndi/+test/+database/test_ndi_document.m:33, which
#                 lives in src/ but sits inside a `+test` PACKAGE. **That last
#                 reading is a JUDGEMENT, made here and not stated by the
#                 team**: a strict src/-vs-tests/ split would call that file
#                 production and remove `demoNDI` too. `simple.m` READS
#                 `demoNDI.value` and constructs `demoNDIMock`, never a
#                 `demoNDI` document -- so the example calculator the ruling is
#                 about does not write this class.
#   `mock`        NO DIRECT CONSTRUCTION SITE AT ALL. `git grep -E
#                 "(ndi\.document|newdocument)\(\s*'mock'"` over origin/main
#                 returns 0 lines; every `mock` hit is the `ndi.mock.*` package
#                 or a comment, which is a different thing wearing the name.
#
# Note the three were NOT unreferenced -- do not re-derive "nonprod" as
# "nothing mentions it"; that grep was run once against the snake_case spelling
# and returned zero for a repository that has never contained that string.
_NONPROD_CLASSES = {"mock", "demoNDI"}

# did_v1 classes dissolved into their modern form BEFORE the V_zeta base V_eta was
# copied from (hence absent from V_zeta). Reviewed and dissolved long ago -- not
# gaps. Value = where they went.
#
# EVERY ENTRY HERE IS AN ASSERTION ABOUT NDI, so it must be checked against NDI
# `origin/main` before being added, and re-checked when NDI moves. Verified:
#   animalsubject -- template still shipped, but ZERO .m files reference it, so
#                    nothing writes one. Dissolution not contradicted.
#
# REMOVED, because it was FALSE: `subjectmeasurement: measurement`. NDI never
# performed that dissolution. `subjectmeasurement` is still a shipped template
# with FOUR in-tree emitters (build_intan_flat_exp.m and three session builders),
# and `measurement` is a NEWER PARALLEL class added 2026-01-05, not a
# replacement. The false entry made the ledger report those documents as
# deliberately retired when in fact they have no V_eta home and no migrator --
# the exact silent loss this ledger exists to surface.
_PRE_ZETA_DISSOLVED = {"animalsubject": "subject"}


def vzeta_classes():
    """Class names present in the V_zeta base (the set V_eta was copied from).
    A v1 class absent here AND without a V_eta home/migrator was never reviewed by
    the migration -> a genuine gap (vs. one V_zeta reviewed and chose to dissolve)."""
    out = set()
    for p in glob.glob(os.path.join(SCHEMA_ROOT, "schemas", "V_zeta", "**", "*.json"),
                       recursive=True):
        out.add(os.path.basename(p)[:-5])
    return out


# Migrator files that are NOT per-class consumers (shared helpers / default
# passthrough / second-pass reshapers) -- excluded when a migrator filename is
# read as a v1 source-class name.
_MIG_HELPERS = {
    "identity", "calcCommon", "universalRenames", "Contents",
    "resolveDatasetEntities", "resolveDeferredBaths",
    "jSampledBody", "jGetCharAny",
}
# `syncrule_mapping` WAS IN THIS SET AND IS NOT A HELPER. Removed 2026-08-10.
#
# It is a per-class migrator -- `+migrators_j/syncrule_mapping.m`, the #58 repair
# that keeps the fields a LIVE NDI query reads (syncgraph.m:404-408) -- and it
# had been excluded from `migrator_files()`, so the ledger reported
# `migrator: false` for a class that has had one for as long as #58 has been
# closed. The coverage count was 83 when it should have been 84.
#
# HOW IT GOT HERE: it sits directly after `jSampledBody` and `jGetCharAny` in a
# set of `j`-prefixed shared helpers. It reads as an append into the nearest
# collection rather than a considered exclusion, and nothing distinguished the
# two -- a helper and a real migrator are both just filenames here.
#
# WHY IT SURFACED ONLY NOW, which is the useful part: the ledger's own guard,
# test_no_passthrough_row_claims_a_migrator_emits_it, fires when a row is marked
# `emitted` while nothing backs it. This row only became `emitted` when
# V_eta_migration_targets.json was refreshed and gave it non-empty targets.
# Before that it sat in a state the guard does not inspect, so a wrong exclusion
# and a missing target cancelled each other out and the row looked consistent.
# Two errors agreeing is not the same as being right.
#
# Same direction as every other instrument defect found today: it UNDERSTATED
# what is built. Nothing was ever wrongly claimed as migrated.


def _ndi_main_templates():
    """NDI production v1 templates read from `origin/main` (falling back to `main`)
    via git, NOT the checked-out working tree -- a V_eta feature branch of NDI can
    lag main and silently drop classes main has since added (ensemble,
    kilosort_clusters, ...). Returns ({class_name: 'path @ref'}, ref) or (None, None)
    if git/main is unavailable, so the caller falls back to the working tree."""
    if not NDI:
        return None, None
    import subprocess
    ddir = "src/ndi/ndi_common/database_documents"
    for ref in ("origin/main", "main"):
        try:
            files = subprocess.run(
                ["git", "-C", NDI, "ls-tree", "-r", "--name-only", ref, "--", ddir],
                capture_output=True, text=True, check=True).stdout.splitlines()
        except (OSError, subprocess.CalledProcessError) as exc:
            # RECORDED, not merely skipped. The fallback chain is
            # origin/main -> main -> the working tree, and the docstring above
            # says why that is not neutral: a V_eta feature branch of NDI lags
            # main and ships FEWER classes. Which one was actually read is a
            # fact about every number in the ledger.
            TEMPLATE_SCAN["refs_tried"].append(f"{ref}: {type(exc).__name__}")
            continue
        out = {}
        wanted = [f for f in files if f.endswith(".json")]
        TEMPLATE_SCAN["candidates"] = len(wanted)
        for f in wanted:
            # COUNTED. Each of these skips removes one class from the did_v1
            # SOURCE UNIVERSE -- the `102 v1 classes` headline gates.py matches
            # on, and the denominator of the ledger's no-target census. A
            # template that would not show or would not parse used to make that
            # universe smaller and leave every percentage reading better.
            try:
                blob = subprocess.run(["git", "-C", NDI, "show", f"{ref}:{f}"],
                                      capture_output=True, text=True, check=True).stdout
            except (OSError, subprocess.CalledProcessError):
                TEMPLATE_SCAN["unreadable"] += 1
                continue
            try:
                d = json.loads(blob)
            except json.JSONDecodeError:
                TEMPLATE_SCAN["unparseable"] += 1
                continue
            cn = d.get("document_class", {}).get("class_name")
            if cn:
                out[cn] = f"{f} @{ref}"
            else:
                TEMPLATE_SCAN["not_a_document_class"] += 1
        if out:
            TEMPLATE_SCAN["source"] = ref
            TEMPLATE_SCAN["classes"] = len(out)
            return out, ref
        TEMPLATE_SCAN["refs_tried"].append(f"{ref}: 0 classes")
    return None, None


def _ndi_worktree_templates():
    """Fallback: NDI templates from the checked-out working tree.

    Counted exactly like the ref path: this is the branch that runs when the ref
    could not be read, so it is the branch most likely to be quietly short.
    """
    out = {}
    paths = sorted(glob.glob(os.path.join(
        NDI, "src/ndi/ndi_common/database_documents/**/*.json"), recursive=True))
    TEMPLATE_SCAN["candidates"] = len(paths)
    for p in paths:
        try:
            blob = Path(p).read_text()
        except OSError:
            TEMPLATE_SCAN["unreadable"] += 1
            continue
        try:
            d = json.loads(blob)
        except json.JSONDecodeError:
            TEMPLATE_SCAN["unparseable"] += 1
            continue
        cn = d.get("document_class", {}).get("class_name")
        if cn:
            out[cn] = os.path.relpath(p, NDI) + " @worktree"
        else:
            TEMPLATE_SCAN["not_a_document_class"] += 1
    TEMPLATE_SCAN["source"] = "worktree"
    TEMPLATE_SCAN["classes"] = len(out)
    return out


def v1_classes():
    """The complete did_v1 SOURCE-class universe, keyed to its provenance.

    Two independent writers put v1 documents in real corpora, and NEITHER alone
    is the whole universe -- the earlier ledger read only the first and undercounted:

      A. NDI production templates (ndi_common/database_documents/**.json). This is
         the NDI half: 87 classes = the go-forward survivors PLUS the dissolved
         v1 classes (subject_group, treatment*, imageStack*, stimulus_bath, ...).
      B. vhlab app / calculator classes -- contrast_tuning, *_tuning, *_calc,
         hartley_calc, etc. -- generated by analysis apps into real corpora (Soph)
         but NOT shipped as NDI templates. Their footprint is the set of bespoke
         migrators that CONSUME them (a migrators_j / migrators file named after the
         source class). The DID class-provenance doc tags these origin=V_delta
         because the NAME first entered the DID schema then, but the DOCS are v1-era.

    We deliberately do NOT fold in the post-v1 DID intermediate classes (zarr,
    directory, interaction_purpose, daqreader_image_epochdata_ingested, the
    *_observation leaves, data_body, openminds_import, ...): those are V_eta/V_zeta/
    V_gamma TARGET representations, not v1 sources, so they belong on the right-hand
    side of the ledger, never the left.

    Returns {class_name: provenance_note}."""
    out = {}
    # A. NDI shipped templates -- from origin/main so a lagging NDI feature branch
    #    can't silently shrink the v1 universe (working tree is the fallback).
    if NDI:
        main, _ref = _ndi_main_templates()
        out.update(main if main is not None else _ndi_worktree_templates())
    # B. vhlab app/calculator classes: a bespoke migrator consumes them but NDI
    #    ships no template. Match on class name AND its snake form.
    if DIDM:
        have = set(out) | {snake(c) for c in out}
        for pkg in ("migrators_i", "migrators", "migrators_j"):
            base = os.path.join(DIDM, "src/did/+did2/+convert/+" + pkg)
            for p in glob.glob(os.path.join(base, "*.m")):
                cn = os.path.basename(p)[:-2]
                if cn in _MIG_HELPERS or cn in have or snake(cn) in have:
                    continue
                out[cn] = f"app-generated (migrators_{pkg}, no NDI template)"
                have.add(cn)
    return out


def migrator_files():
    """Bespoke per-class migrators across ALL three convert packages (DID-matlab):
    +migrators_j (V_eta), +migrators (V_zeta/older), +migrators_i (intermediate).
    Each file is named after the SOURCE class it consumes; shared helpers are
    excluded. Scanning all three (not just migrators_j) is why e.g. epochclocktimes
    -- handled in +migrators -- is not mis-flagged as an unmapped gap."""
    if not DIDM:
        return set()
    out = set()
    for pkg in ("migrators_j", "migrators", "migrators_i"):
        base = os.path.join(DIDM, "src/did/+did2/+convert/+" + pkg)
        for p in glob.glob(os.path.join(base, "*.m")):
            cn = os.path.basename(p)[:-2]
            if cn not in _MIG_HELPERS:
                out.add(cn)
    return out


_CLASS_EMIT = [re.compile(r"'class_name'\s*,\s*'([A-Za-z_]\w*)'"),
               re.compile(r'"class_name"\s*,\s*"([A-Za-z_]\w*)"')]


def emitted_classes():
    """class_name values emitted by the V_eta migrators + V_eta second pass.
    Maps class_name -> set of files. stimulusBathToBath is multi-version (also emits
    V_zeta bath/pharmacological_manipulation); those show as violations against the
    V_eta schema -- which is the point (the live V_eta path must not emit them)."""
    out = {}
    roots = []
    if DIDM:
        roots.append(os.path.join(DIDM, "src/did/+did2/+convert/+migrators_j"))
    if NDI:
        roots.append(os.path.join(NDI, "src/ndi/+ndi/+migrate/+internal"))
    for root in roots:
        for p in glob.glob(os.path.join(root, "**/*.m"), recursive=True):
            txt = Path(p).read_text()
            for pat in _CLASS_EMIT:
                for m in pat.finditer(txt):
                    out.setdefault(m.group(1), set()).add(os.path.basename(p))
    return out


# ============================================================================
# THE BATCH POST-PASS DECLARATIONS -- the third consumption channel (row 107).
# ============================================================================
#
# THE UNDERSTATEMENT THIS REPAIRS, IN ONE ROW. `generic_file` is folded into a
# `term_observation` + an `opaque_body` by `did2.convert.foldGenericFiles`, and
# this tool reported it at stage 0, "source identified" -- because rung 1 asks
# whether a migrator file NAMED AFTER the class exists, and a batch post-pass is
# not one. `_rung_consumed` said so in its own comment for weeks: *"the fix is a
# field in V_eta_migration_targets.json, not a grep in this function: a bare
# name sweep over the convert package matches `base` in 9 of the 9 passes and
# `app` in universalRenames, which is noise a stage cannot be built on."*
#
# The fix landed one step further out than that comment predicted, and for the
# better reason. A field HERE would be a DID-schema author's claim about
# DID-matlab code, going stale silently the day the pass changed. Instead the
# PASSES DECLARE, in their own headers, and this reads the declaration --
# the reasoning `_EDGE_REFERENT_UNIQUE` is declared by name in build_v_eta.py
# rather than derived. The parser lives in DID-matlab beside the code it
# describes (`tools/batch_pass_declarations.py`) and is imported by path, so
# there is ONE grammar and one place it can drift from.
#
# THREE PROPERTIES ARE LOAD-BEARING AND EACH IS ASSERTED BY A TEST.
#   1. A PASS WITH NO DECLARATION IS `MISSING`, NEVER AN EMPTY SET. The scan
#      reports the missing ones separately and unconditionally, and a credit is
#      only ever ADDED by a declaration present -- so an unread, unreadable or
#      undeclared pass can never make a rung look better than it is. It can
#      only leave it where it was.
#   2. THE CREDIT IS DISTINGUISHABLE. `build_state.batch_pass_consumers` and
#      `.batch_pass_emits` carry the pass names, the rung `why` strings say
#      "batch post-pass" in words, and the rollup prints which rows moved.
#   3. ONLY AN ATTRIBUTED EMISSION CREDITS RUNG 3. `UNATTRIBUTED` emissions and
#      the `nothing` form credit nothing at all. `resolveValidIntervals`
#      declares `valid_interval -> nothing` because it is dormant by team
#      decision; that row must stay at rung 3 = `no`, and it does.
BATCH_PASS_SCAN = {
    "measured": False, "chain_size": 0, "declared": [], "missing": [],
    "invalid": [], "index": {}, "why": "not read yet",
    "path": None, "chain_info": {}, "per_pass": {},
    "accounting_disagreement": [],
}


def batch_pass_declarations():
    """Load DID-matlab's declaration scan. Populates BATCH_PASS_SCAN; no return.

    DEGRADES BY SAYING SO. Every failure path here sets `measured` False with a
    `why`, and leaves the index empty -- which cannot promote a row, because
    the two rung functions only ever ADD on evidence found. A missing sibling
    is therefore an UNDER-report that announces itself, never a silent one.
    """
    s = BATCH_PASS_SCAN
    s.update({"measured": False, "chain_size": 0, "declared": [],
              "missing": [], "invalid": [], "index": {}, "chain_info": {},
              "per_pass": {}, "accounting_disagreement": []})
    if not DIDM:
        s["why"] = ("DID-matlab not found, so no pass could be read. Rung 1 and "
                    "rung 3 carry NO batch-post-pass credit in this run -- an "
                    "UNDERSTATEMENT, not a measurement")
        return
    path = os.path.join(DIDM, "tools", "batch_pass_declarations.py")
    s["path"] = path
    if not os.path.isfile(path):
        s["why"] = (f"{path} is absent -- this DID-matlab checkout predates the "
                    "declarations. No batch-post-pass credit in this run")
        return
    # NAMED, not blind (tests/test_tool_skip_denominators.py). The three ways
    # this import can fail are the three named here: the file is unreadable
    # (OSError), it is not valid Python or its own `import census_digest` is
    # missing (ImportError/SyntaxError), or the scan hits a data shape it does
    # not expect (AttributeError/KeyError/TypeError/ValueError). Every one of
    # them lands in `why` and leaves `measured` False, so the failure is an
    # announced UNDER-report and never a silent zero.
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_did_batch_pass_declarations", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        out = mod.scan(DIDM)
    except (OSError, ImportError, SyntaxError, AttributeError, KeyError,
            TypeError, ValueError) as exc:
        s["why"] = f"{type(exc).__name__} reading {path}: {exc}"
        return
    if not out.get("chain_derived"):
        s["why"] = ("the batch-pass chain could not be DERIVED from the "
                    "DID-matlab harness: " + str(out.get("why")))
        return
    s["measured"] = True
    s["why"] = None
    s["chain_size"] = out["chain_size"]
    s["declared"] = list(out["declared"])
    s["missing"] = list(out["missing"])
    s["invalid"] = list(out["invalid"])
    s["chain_info"] = out.get("chain_info", {})
    # THE TWO ACCOUNTINGS, KEPT APART SO THEY CAN BE COMPARED. `declared` and
    # `missing` are the scan's SUMMARY lists; `per_pass` is the per-file verdict
    # they were built from. Storing only the summary means a bug that laundered
    # a missing declaration into the declared list -- the one collapse this
    # whole mechanism exists to prevent -- would be invisible on this side of
    # the repo boundary, and invisible on any day the real tree happens to have
    # no missing declarations. `corpus_proven.py` cross-checks its rung against
    # the census it fed in for the same reason.
    s["per_pass"] = {fn: {"declared": bool(d["declared"]),
                          "errors": list(d["errors"])}
                     for fn, d in out["passes"].items()}
    s["accounting_disagreement"] = sorted(
        fn for fn, d in s["per_pass"].items()
        if d["declared"] != (fn in s["declared"])
        or d["declared"] == (fn in s["missing"]))
    # {consumed name -> [{pass, form, targets, reason}]}. An INVALID declaration
    # is indexed for the names it did parse: it is reported as invalid either
    # way, and dropping it whole would turn a malformed line into a silent loss
    # of a credit the pass genuinely earns.
    index = {}
    for fn in out["declared"]:
        d = out["passes"][fn]
        for name in d["consumes"]:
            e = d["emits"].get(name) or {"form": None, "targets": [],
                                         "reason": None}
            index.setdefault(name, []).append(
                {"pass": fn, "form": e["form"], "targets": list(e["targets"]),
                 "reason": e["reason"]})
    s["index"] = index


def batch_pass_entries(v1_class, veta_class):
    """Declarations naming this row, matched on EITHER spelling.

    V_eta is snake_case and NDI is camelCase (CLAUDE.md, the `demo_ndi` bug), and
    a batch pass reads whichever spelling the batch carries at its point in the
    chain -- `resolveLawnPlateSubjects` matches the MIGRATED `ontology_table_row`
    while the ledger row is NDI's `ontologyTableRow`. So both names on the row
    are offered, plus the snake form of the v1 name. A declared name that
    matches NOTHING is reported by the rollup rather than dropped.
    """
    idx = BATCH_PASS_SCAN["index"]
    out = []
    for n in (v1_class, veta_class, snake(v1_class or "")):
        for e in idx.get(n or "", []):
            if e["pass"] in {x["pass"] for x in out}:
                continue          # one pass credits a row once, not per spelling
            out.append(dict(e, matched_on=n))
    return out


# A RENAME IS A FOURTH SPELLING, and it is the only one of its kind that is
# safe to join on. Added 2026-08-17 for `epochMint`, which reads
# `acquisition_epoch` bodies -- the migrated form of did_v1 `element_epoch` --
# and mints a `relative_reference` per clock. It declared that consumption
# truthfully and the ledger still could not credit it, because `element_epoch`
# carries `veta_class = None`, so none of the three spellings above is the name
# the batch actually holds at that point in the chain.
#
# WHY NOT JUST MATCH ON `targets`, WHICH WOULD HAVE BEEN ONE LINE. Measured
# before it was written, over the committed ledger:
#
#   DENOMINATOR: 102 rows; 81 distinct target class name(s) claimed
#     claimed by EXACTLY ONE row : 55
#     claimed by SEVERAL rows    : 26
#   `session_relative_reference`, declared by resolveSessionAnchors, is a
#   target of THIRTY-SIX rows.
#
# So the one-line version credits one pass to 36 rows -- a mass over-credit in
# the reassuring direction, which is the trade this file refuses everywhere
# else. Uniqueness alone is not enough either: `session_bounded_reference` has
# exactly one owner (`ontologyTableRow`), and crediting that row with "a pass
# consumes it" because a pass consumes an ANCHOR its migrator emitted is a
# different claim from the one rung 1 makes.
#
# THE RULE IS THEREFORE THE RENAME CASE AND NOTHING ELSE: the declared name is
# the row's SOLE target, and no other row claims it. Then the migrated name IS
# the row, 1:1, and consuming it is consuming the row's documents. On today's
# ledger that admits exactly one join -- `acquisition_epoch` -> `element_epoch`
# -- and refuses every other declared name, including all 36 above.
def rename_target_owner(targets_by_class):
    """{sole-target name: v1_class} for classes whose migration is a pure rename.

    Takes {v1_class: [target, ...]} for the WHOLE universe and is computed once,
    before rows are built. Not per-row on purpose: the uniqueness half needs
    every class to have answered, so a version that accumulated as rows were
    built would silently degrade to "unique among the classes seen so far" --
    which would make the join depend on iteration order.
    """
    claims = {}
    for cn, targets in targets_by_class.items():
        for t in (targets or []):
            claims.setdefault(t, []).append(cn)
    return {name: owners[0]
            for name, owners in claims.items()
            if len(owners) == 1 and list(targets_by_class[owners[0]]) == [name]}


RENAME_OWNER = {}


def rename_entries(v1_class):
    """Declarations naming this row by its MIGRATED name, rename case only."""
    idx = BATCH_PASS_SCAN["index"]
    out = []
    for name, owner in RENAME_OWNER.items():
        if owner != v1_class:
            continue
        for e in idx.get(name, []):
            out.append(dict(e, matched_on=name))
    return out


# ============================================================================
# THE SHARED HELPER -- the FOURTH consumption channel (the `app` mis-score).
# ============================================================================
#
# `app` read rung 3 = `no`, "the decided target `software` is not among what
# the migrator emits today (nothing)", while `+migrators_j/private/
# jSoftwareFromApp.m` has been folding it into a `software` entity at six call
# sites. Every channel above asks a question about a NAME -- a migrator file
# named after the class, a pass in the derived chain, an `emitted_by`
# cross-reference -- and that helper is named after neither the source nor the
# target. It is tell (1) of the four the open-list reconciliation recorded:
# work landed under a different name and read as work not done.
#
# THE DIRECTION MATTERS AND IT IS THE UNUSUAL ONE. This mis-score UNDERSTATES
# progress, and the cost is the one that has now been paid three times this
# week: a decision re-litigated and an agent dispatched at finished work. It
# was two hours from being reported as a buildable gap.
#
# WHAT WAS REJECTED, AND WHY IT MATTERS MORE THAN WHAT WAS BUILT. The obvious
# repair is to DERIVE this -- walk the call graph from each migrator and credit
# any mint site reachable through its helpers. That was written and measured
# over all 102 rows before it was thrown away. It agrees with the ledger on 22
# of the 31 scored rows, recovers `app` -- and gets `valid_interval` WRONG, in
# the reassuring direction: `resolveValidIntervals.m` contains a
# `logical_observation` mint site behind a guard that is off by team decision,
# so reachability credits a rung for code that cannot run. A derivation cannot
# see dormancy; a declaration states it, and that pass already declares
# `valid_interval -> nothing` with the reason. Trading a pessimistic miss for
# an optimistic one is the worse trade in this repository, so the credit comes
# from a DECLARATION, in the grammar the batch passes already use.
#
# THE ASYMMETRY WITH `batch_pass_declarations` IS DELIBERATE. A pass in the
# chain MUST declare -- the chain is derived, so the denominator is known and
# every member was declared before that gate was armed. There is no equivalent
# derivation for "a helper that owes a declaration", so declaring is VOLUNTARY,
# an undeclared helper credits NOTHING, and DID-matlab's scan prints how many
# helpers mint while declaring nothing. That keeps the substance of rule 1 -- a
# missing declaration can only leave a rung where it was, never make one look
# better -- without arming a gate whose blast radius nobody has measured.
HELPER_SCAN = {"measured": False, "candidates": 0, "minting": 0,
               "declared": [], "undeclared": 0, "invalid": [],
               "minting_undeclared": [], "index": {}, "why": "not read yet"}


def helper_declarations():
    """Load DID-matlab's shared-helper scan. Populates HELPER_SCAN; no return.

    Degrades exactly as `batch_pass_declarations` does: every failure path sets
    `measured` False with a named `why` and leaves the index empty, which
    cannot promote a row because the rung functions only ever ADD on evidence
    found. A missing sibling under-reports and says so.
    """
    s = HELPER_SCAN
    s.update({"measured": False, "candidates": 0, "minting": 0, "declared": [],
              "undeclared": 0, "invalid": [], "minting_undeclared": [],
              "index": {}})
    if not DIDM:
        s["why"] = ("DID-matlab not found, so no helper could be read. Rung 1 "
                    "and rung 3 carry NO shared-helper credit in this run -- "
                    "an UNDERSTATEMENT, not a measurement")
        return
    path = os.path.join(DIDM, "tools", "batch_pass_declarations.py")
    if not os.path.isfile(path):
        s["why"] = (f"{path} is absent -- this DID-matlab checkout predates the "
                    "declarations. No shared-helper credit in this run")
        return
    # NAMED, not blind, and the LAST name is the one that matters here: an
    # older DID-matlab carries `batch_pass_declarations.py` WITHOUT
    # `scan_helpers`, which is an AttributeError and must read as "this
    # checkout cannot answer", never as "no helper declares anything".
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_did_batch_pass_declarations_helpers", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        out = mod.scan_helpers(DIDM)
        index = mod.helper_index(out)
    except (OSError, ImportError, SyntaxError, AttributeError, KeyError,
            TypeError, ValueError) as exc:
        s["why"] = (f"{type(exc).__name__} reading scan_helpers from {path}: "
                    f"{exc}")
        return
    if not out.get("candidates"):
        # Zero candidates is "looked in the wrong place", not "no helpers".
        s["why"] = ("the helper directories are absent or empty at "
                    + str(DIDM) + " -- 0 candidates, so this is a failed "
                    "lookup and not a measurement")
        return
    s["measured"] = True
    s["why"] = None
    s["candidates"] = out["candidates"]
    s["minting"] = len(out.get("minting") or [])
    s["declared"] = list(out.get("declared") or [])
    s["undeclared"] = len(out.get("undeclared") or [])
    s["invalid"] = list(out.get("invalid") or [])
    s["minting_undeclared"] = list(out.get("helpers_minting_undeclared") or [])
    s["index"] = index


def helper_entries(v1_class, veta_class):
    """Helper declarations naming this row, matched on EITHER spelling.

    Same both-spellings rule as `batch_pass_entries`, for the same reason: a
    helper reads whichever spelling the body carries at its point in the chain,
    and V_eta is snake_case where NDI is camelCase.
    """
    idx = HELPER_SCAN["index"]
    out = []
    for n in (v1_class, veta_class, snake(v1_class or "")):
        for e in idx.get(n or "", []):
            if e["helper"] in {x["helper"] for x in out}:
                continue      # one helper credits a row once, not per spelling
            out.append(dict(e, matched_on=n))
    return out


# Known emissions of NON-V_eta classes, with a tracked reason. These are NOT
# clean -- each is a real issue to fix -- but they are explicitly acknowledged so
# the guardrail fails on NEW (unacknowledged) revived/invented classes.
#   bath / pharmacological_manipulation: stimulusBathToBath is the V_zeta/V_epsilon
#     assembler and emits these V_zeta classes. Under a LIVE V_eta migration
#     assembleDeferred still routes a deferred stimulus_bath through it, so the V_eta
#     path would emit a `bath` V_eta lacks (the corpus is unaffected -- it uses the
#     coarse resolveDeferredBaths -> dose_manipulation). FIX: make the V_eta stimulus
#     _bath assembly emit dose_manipulation (TaskList: stimulusBathToBath V_eta path).
KNOWN_NON_VETA = {"bath", "pharmacological_manipulation"}


def guardrail(veta, emitted):
    """Emitted classes that exist in neither the V_eta schema nor the known set.
    Returns (new_violations, acknowledged)."""
    missing = [(c, sorted(f)) for c, f in emitted.items() if c not in veta]
    new = sorted((c, f) for c, f in missing if c not in KNOWN_NON_VETA)
    ack = sorted((c, f) for c, f in missing if c in KNOWN_NON_VETA)
    return new, ack


LEDGER_JSON = os.path.join(SCHEMA_ROOT, "schemas", "V_eta_coverage_ledger.json")


# ============================================================================
# NO TARGET IS A CLAIM. IT HAS TO BE MADE, NOT LEFT TO AN EMPTY LIST.
# ============================================================================
#
# Until 2026-08-11 a row with no target of any kind rendered as
#
#     · **will dissolve / be deleted** (no target by design)
#
# and that string was produced by `if dt else` -- an ASSERTION READ OFF AN
# EMPTY LIST. It is the project's own recurring error in its purest form: an
# absence turned into a reassuring conclusion, in the direction of "settled".
# It was printed for SEVEN rows, and it was wrong for at least one of them
# (`filter`, whose signed model makes it a `frequency_filter` document) and
# contested for another (`ngrid`).
#
# The two facts a blank cell was standing in for are opposites:
#
#   DISSOLVED   the class stops existing and no document class replaces it.
#               Naming no target is the CORRECT and FINAL answer.
#   GAP         the target is fixed in a signed plan and nobody wrote it down.
#               Naming no target is a MISSING RECORD.
#
# So dissolution is now stated POSITIVELY, here, with the sign-off that
# licenses it -- and a row that names no target and carries no entry below
# renders as `⚠ NO TARGET AND NO DISSOLUTION RECORDED`, a visible gap. "No
# target" is no longer expressible by omission alone, which is the whole point:
# forgetting to record a target produces a warning, not a settled-looking row.
#
# THESE ARE NOT DISPOSITIONS (operating rule 4). Every entry is TRANSCRIBED
# from a `TEAM-SIGN-OFF` line the team wrote, and the transcription is CHECKED
# by `check_decision_citations()` below: the named document must exist, must
# carry a line beginning `TEAM-SIGN-OFF`, and that line must contain the quoted
# fragment. A fabricated citation, a stale one, or a fragment that drifted
# after a plan edit fails the ledger build. Claude may fill these in; it cannot
# invent what they say.

# reason vocabulary for a row that names no target class
NO_TARGET_DISSOLVED = "dissolved"      # nothing replaces it; final
NO_TARGET_PASSTHROUGH = "passthrough"  # its decided target IS itself
NO_TARGET_DISPUTED = "disputed"        # the record says two incompatible things
NO_TARGET_UNRECORDED = "unrecorded"    # THE GAP -- no reason, no target

NO_TARGET_REASON_LABEL = {
    NO_TARGET_DISSOLVED:
        "DISSOLVES -- no target class, and that is the signed answer",
    NO_TARGET_PASSTHROUGH:
        "PASSES THROUGH as itself by decision -- the target is the class",
    NO_TARGET_DISPUTED:
        "DISPUTED -- the record states two incompatible dispositions",
    NO_TARGET_UNRECORDED:
        "NO TARGET AND NO DISSOLUTION RECORDED -- a gap, not a decision",
}

# class -> (reason, plan document, fragment that must appear on its sign-off
#           line, one-line account written from that line)
NO_TARGET_BY_DECISION = {
    # "epochid is DROPPED, and a document reaches its epoch through the
    #  TIME_REFERENCE CHAIN" -- so the string mixin is replaced by an EDGE, and
    #  an edge is not a document class. This is the clean example of a genuine
    #  dissolution and it is what the previous inferred label was right about.
    "epochid": (
        NO_TARGET_DISSOLVED, "V_eta_epoch_plan.md",
        "epochid is DROPPED",
        ("DROPPED as a class. The `epoch_id` edge that replaces it is an edge, "
        "not a document class, so there is no target and that is final.")),

    # "stimulus_response and stimulus_response_scalar_parameters DELETE
    #  (superclass-only, 0 docs)". A class no document has ever been an
    #  instance of cannot have a migration target.
    "stimulus_response": (
        NO_TARGET_DISSOLVED, "V_eta_stimulus_response_model_plan.md",
        "stimulus_response and stimulus_response_scalar_parameters DELETE",
        ("DELETED. Superclass-only with zero documents in any corpus, so there "
        "is nothing to migrate and no target to name.")),
    "stimulus_response_scalar_parameters": (
        NO_TARGET_DISSOLVED, "V_eta_stimulus_response_model_plan.md",
        "stimulus_response and stimulus_response_scalar_parameters DELETE",
        ("DELETED. Superclass-only with zero documents in any corpus, so there "
        "is nothing to migrate and no target to name.")),

    # `binaryseries_parameters` WAS HERE, as the second row of the `ngrid`
    # shape, and is deliberately not, as of 2026-08-11. It is now in
    # DECIDED_TARGETS_BY_SIGNOFF with TWO targets -- see the entry there for the
    # team ruling that resolved it and why the count is two rather than one.
    # `ngrid` below is UNAFFECTED and stays contested: nothing about that row was
    # decided, and the two rows only ever shared a shape.

    # THE ROW THIS TABLE WAS BUILT FROM, LEFT VISIBLE RATHER THAN RESOLVED
    # HERE. Two statements in the SAME document:
    #
    #   V_eta_image_model_plan.md:107  "## `ngrid` / `array` -- KILLED as a
    #                                   data_type; `ngrid` -> `sampled_body`"
    #     :116  "**`ngrid` -> phases into `sampled_body`** like every other
    #            carrier (drop `ngrid_file` + `element_id`). NOT a `data_type`."
    #   V_eta_image_model_plan.md:144  the TEAM-SIGN-OFF line: "ngrid is
    #            DISSOLVED (deleted, not migrated)"; and the FINAL class block
    #            at :163 reads "ngrid   DELETED".
    #
    # "phases into `sampled_body`" is a fold WITH a target; "deleted, not
    # migrated" is a dissolution. Only the second is in the team's own words,
    # so `sampled_body` is NOT recorded as a decided target (operating rule 4
    # -- Claude may not promote its reading over the signature). But recording
    # a clean dissolution would bury the disagreement, and this row has already
    # flipped sides once in a single day: commit 94cacb3 called it a
    # dissolution, 0eb58d9 corrected that to a fold citing the section heading,
    # and the sign-off says the first was closer. Both commits read one half of
    # the document.
    #
    # So it renders as DISPUTED, which is neither clean nor a silent gap, and
    # it stays on the board until the team says which sentence governs.
    "ngrid": (
        NO_TARGET_DISPUTED, "V_eta_image_model_plan.md",
        "ngrid is DISSOLVED (deleted, not migrated)",
        ("CONTESTED. The sign-off says `ngrid is DISSOLVED (deleted, not "
        "migrated)` and the plan's FINAL class block says `ngrid DELETED`, "
        "while the same document's R4 section says `ngrid` phases into "
        "`sampled_body` -- a fold WITH a target. No target is recorded, "
        "because only the dissolution is in the team's own words; the "
        "disagreement is left visible rather than settled by a tool.")),
}

# class -> (targets, plan document, fragment on the sign-off line, the mapping
#           sentence in the same document, one-line account)
#
# ONLY where a signed line names the target class. A row whose decision is
# unsigned, or whose sign-off names a MODEL rather than a class, is left out
# and shows up as a gap -- which is the honest state, and it is recoverable.
# An unsigned target entered here would be Claude recording a decision.
DECIDED_TARGETS_BY_SIGNOFF = {
    # The sign-off approves "the frequency_filter model as written below", and
    # the migration section of that same document (below the line, so inside
    # what was approved) states the class mapping outright:
    #   :178 "v1 `filter` is a superclass block on `pyraview`. It becomes a
    #         separate `frequency_filter` document plus a `filter_id` edge from
    #         the observation the pyraview fold already mints."
    # CAVEAT, from the document itself: this sign-off line was TRANSCRIBED by
    # Claude on the team's explicit verbal instruction (2026-07-30), and the
    # document says so in the paragraph directly beneath it. The guarantee here
    # is therefore only as good as that transcription -- noted, not hidden.
    "filter": (
        ["frequency_filter"], "V_eta_frequency_filter_model_plan.md",
        "Approved the frequency_filter model as written below",
        ("v1 `filter` is a superclass block on `pyraview`. It becomes a "
        "separate `frequency_filter` document"),
        ("Becomes a separate `frequency_filter` document plus a `filter_id` "
        "edge from the observation the pyraview fold mints. Today the migrator "
        "only renames the block in place.")),

    # "epochfiles_ingested becomes `ingestion_manifest` with filenavigator_id
    #  RESTORED" -- a named class, in the signed line itself.
    "epochfiles_ingested": (
        ["ingestion_manifest"], "V_eta_epoch_plan.md",
        "epochfiles_ingested becomes `ingestion_manifest`",
        "epochfiles_ingested becomes `ingestion_manifest`",
        ("Becomes `ingestion_manifest`, with `filenavigator_id` restored and "
        "the invented required `epochid` edge replaced by `epoch_id`.")),

    # The sign-off names both classes and says the presentation is DECOMPOSED
    # around its preserved id rather than dissolved. Which of the two carries
    # the id is stated in the plan:
    #   :102 "the v1 `stimulus_presentation` id is preserved on the
    #         body-of-record it becomes (the `timed_sequence`)"
    #   :99  "mint the `timed_sequence` + (per resolved subject) a
    #         `timed_sequence_manipulation`"
    # The N standalone stimulus `data_type` documents the same paragraph names
    # are deliberately NOT listed: their classes depend on the stimulus
    # (`visual_grating`, `image`, ...) and no fixed set is signed.
    "stimulus_presentation": (
        ["timed_sequence", "timed_sequence_manipulation"],
        "V_eta_stimulus_model_plan.md",
        "stimulus_presentation is DECOMPOSED around its preserved id",
        ("the v1 `stimulus_presentation` id is preserved on the body-of-record "
        "it becomes (the `timed_sequence`)"),
        ("DECOMPOSED around its preserved id: the id rides on the "
        "`timed_sequence`, with one `timed_sequence_manipulation` per resolved "
        "subject. The deduped stimulus `data_type` documents it also mints are "
        "not a fixed class set and are not listed.")),

    # RESOLVED 2026-08-11, and it moved OUT of NO_TARGET_BY_DECISION to get
    # here. It sat as DISPUTED because `V_eta_go_forward_class_audit.md` says two
    # things about this class:
    #
    #   :459  a SECTION HEADING -- "## `binaryseries_parameters` -- folds into
    #         `sampled_body`, no new decision"
    #   :3    the TEAM-SIGN-OFF [misc singletons] line, in full --
    #         "`binaryseries_parameters` folds into the data_body model and is
    #          retired (its `time_type` is the time axis's new `datum_type`, its
    #          `data_type` the statement's, `data_dim` the axis count,
    #          `samples_regular_intervals` the axis `regular` flag)"
    #
    # THE TEAM RULED (2026-08-11) THAT THE SIGNATURE IS WHAT IS INTENDED. That
    # settles which sentence governs; it does NOT by itself say how many targets
    # to record, and the answer is TWO, not the heading's one:
    #
    #   `data_type`                -> "the statement's"        -> subject_statement
    #   `time_type`                -> the time axis's datum_type   |
    #   `data_dim`                 -> the axis count               |- the AXIS ENTRY
    #   `samples_regular_intervals`-> the axis `regular` flag      |
    #
    # and the axis entry is not a class of its own: it MOUNTS, on
    # `subject_statement` (inline) or on `sampled_body` (body), selected by
    # `storage_mode` and mutually exclusive -- V_eta_data_body_model_plan.md:136
    # "storage_mode: inline -> subject_statement.axes[] populated; no bodies" /
    # :137 "storage_mode: body -> each sampled_body.axes[] populated;
    # statement.axes[] EMPTY". So a document of this class reaches ONE of the two
    # mounts, and WHICH one is per-document data, not a modelling choice anybody
    # can make once. Recording only `sampled_body` (the heading's reading) drops
    # the mount the signature names OUTRIGHT and unconditionally -- `data_type`
    # goes to the statement whatever `storage_mode` says.
    #
    # Note what is NOT claimed: no migrator emits either target today. The fold
    # is gated on the data_body tier (#45, BLOCKED ON #32) -- `axes[]`,
    # `datum_type` and `regular` do not exist yet. These are DECIDED targets, and
    # the ledger renders them in the future voice for exactly that reason.
    #
    # The cited document is the one carrying the signature. The mount rule lives
    # in V_eta_data_body_model_plan.md, which carries NO sign-off line at all --
    # so it is quoted above as the mechanism, and is not the citation.
    "binaryseries_parameters": (
        ["subject_statement", "sampled_body"],
        "V_eta_go_forward_class_audit.md",
        "`binaryseries_parameters` folds into the data_body model and is retired",
        ("its `time_type` is the time axis's new `datum_type`, its `data_type` "
        "the statement's, `data_dim` the axis count, `samples_regular_intervals` "
        "the axis `regular` flag"),
        ("RETIRED into the data_body model, field by field, per the signature -- "
        "which the team ruled (2026-08-11) is what is intended, over the same "
        "document's section heading (:459) naming `sampled_body` alone. TWO "
        "targets, because the signature routes to two mounts: `data_type` goes "
        "to the STATEMENT unconditionally, while `time_type` / `data_dim` / "
        "`samples_regular_intervals` become an AXIS ENTRY, which mounts on "
        "`subject_statement` when storage_mode is inline and on `sampled_body` "
        "when it is body (V_eta_data_body_model_plan.md:136-137, mutually "
        "exclusive). Recording one mount would drop the other. NOT BUILT: the "
        "fold is gated on the data_body tier (#45, blocked on #32), since "
        "`axes[]`, `datum_type` and `regular` do not exist yet.")),
}


def _signoff_lines(plan):
    """(line_number, text) for every TEAM-SIGN-OFF line in a plan document.

    HTML comments are stripped first, for the same reason `status_board.py`
    strips them: a plan document that TELLS the team how to sign off carries the
    marker inside a comment, and counting it once let Claude's own instruction
    text validate a citation.
    """
    path = os.path.join(SCHEMA_ROOT, "schemas", plan)
    if not os.path.exists(path):
        return []
    with open(path) as fh:
        text = re.sub(r"<!--.*?-->", "", fh.read(), flags=re.DOTALL)
    return [(i, ln) for i, ln in enumerate(text.splitlines(), 1)
            if ln.lstrip().startswith("TEAM-SIGN-OFF")]


def check_decision_citations():
    """Verify every transcription above against the document it cites.

    RULE 2 MADE MECHANICAL. Each entry claims a team sign-off says something;
    this opens the document and checks that a line beginning `TEAM-SIGN-OFF`
    contains the quoted fragment. It is the difference between a citation and a
    recollection -- and this repository has already paid for the difference
    twice (a `demo_ndi` grep that could not match, six plan headers denying
    sign-offs they carried).

    Returns (denominator_lines, failures). Failures are fatal for the caller.
    """
    checks, fails = [], []
    for cls, (_reason, plan, frag, _note) in sorted(NO_TARGET_BY_DECISION.items()):
        checks.append(("no-target", cls, plan, frag, None))
    for cls, (_t, plan, frag, mapping, _note) in sorted(
            DECIDED_TARGETS_BY_SIGNOFF.items()):
        checks.append(("decided-target", cls, plan, frag, mapping))

    lines = [f'DENOMINATOR: {len(checks)} transcribed decision(s) checked against {len({c[2] for c in checks})} plan document(s); every one must quote a real TEAM-SIGN-OFF line']
    for kind, cls, plan, frag, mapping in checks:
        path = os.path.join(SCHEMA_ROOT, "schemas", plan)
        if not os.path.exists(path):
            fails.append(f"{kind} {cls}: cited document {plan} does not exist")
            continue
        hits = [n for n, ln in _signoff_lines(plan) if frag in ln]
        if not hits:
            fails.append(f"{kind} {cls}: no TEAM-SIGN-OFF line in {plan} contains {frag!r}")
            continue
        # The MAPPING sentence need not be on the sign-off line -- a sign-off
        # routinely approves "the model as written below". It must be in the
        # document, though, or the class mapping is unsourced.
        if mapping is not None:
            with open(path) as fh:
                body = re.sub(r"\s+", " ", fh.read())
            if re.sub(r"\s+", " ", mapping) not in body:
                fails.append(f"{kind} {cls}: {plan} does not contain the mapping sentence "
                             f"{mapping!r}")
                continue
        lines.append(f'  [ok] {kind:<14} {cls:<28} {plan}:{hits[0]}')

    # ---- THE TWO RECORDS RECONCILED, which is the whole reason the tables
    # above survive the signature join at all.
    #
    # The join DERIVES that a class is decided; these tables ALSO carry
    # something it cannot derive -- the TARGET CLASSES a signature names, and
    # the reason a signed row has no target. So they stay. What must not
    # survive is the two records DISAGREEING: a transcription citing document A
    # while the signed family that names the same class cites document B means
    # one of them is pointing at the wrong decision, and today it would be
    # noticed by nobody. Hand-editing either side into a contradiction is now
    # fatal, in the same run, with both citations printed.
    #
    # NOT an error: a transcribed class that NO family names. Families track
    # open classes; a class can be signed and closed. That case is counted, not
    # failed, so the check cannot be satisfied by deleting family members.
    signed_idx = signed_family_index()
    reconciled, unfamilied = 0, []
    for kind, cls, plan, _frag, _mapping in checks:
        hits = [e for name in (cls, snake(cls)) for e in (signed_idx.get(name) or [])]
        if not hits:
            unfamilied.append(cls)
            continue
        docs = {e["document"] for e in hits}
        if plan not in docs:
            fails.append(
                f"{kind} {cls}: the transcription cites {plan}, but the SIGNED "
                f'family {", ".join(sorted(e["family"] for e in hits))} that '
                f'names this class is signed in {", ".join(sorted(docs))}. '
                "Two records of one decision, pointing at different documents "
                "-- fix whichever is wrong; do not keep both.")
            continue
        reconciled += 1
    lines.append(
        f'  DENOMINATOR: {len(checks)} transcription(s) reconciled against the '
        f'DERIVED signature join -- {reconciled} also named by a signed family '
        f'and citing that family\'s document, {len(unfamilied)} named by no '
        f'family at all (not an error: families track OPEN classes)'
        + (": " + ", ".join(sorted(unfamilied)) if unfamilied else ""))
    return lines, fails

# ============================================================================
# THE SIGNATURE JOIN -- rung 1, DERIVED from the team's own sign-off lines.
# ============================================================================
#
# WHAT WAS WRONG. `DECIDED_TARGETS_BY_SIGNOFF` above is hand-carried, and it
# carries FOUR classes. The team has written far more than four sign-off lines,
# in ~19 plan documents this tool never opened, so 94 of 102 rows reported rung
# 1 as `not measured`. That reading was HONEST -- absence of a transcription is
# not evidence of no decision, and rendering it as "not decided" would be this
# repository's signature error -- but it made the ladder unable to see the one
# record that is authoritative.
#
# WHAT REPLACES IT. `status_board.FAMILIES` groups open classes into decision
# units and each family cites a plan document; `status_board.signed_families()`
# returns the families whose document carries a `TEAM-SIGN-OFF` line that
# family's tag reaches. The join is: ledger row -> the family naming that row's
# class -> that family's SIGNATURE. Re-derived on every build; nothing is
# transcribed, so a signature added tomorrow moves rows tomorrow.
#
# THREE PROPERTIES OF THE JOIN, EACH CHOSEN AGAINST A SPECIFIC FAILURE:
#
# 1. IT JOINS ON THE SIGNATURE, NEVER ON MEMBERSHIP. A family exists in the
#    table whether or not anyone signed it; `signed_families()` is the only
#    admission. Joining on membership would let one unsigned family promote
#    every class it names -- operating rule 4 broken by a lookup.
#
# 2. IT JOINS ON THE ROW'S OWN IDENTITY, NEVER ON WHAT ITS MIGRATOR EMITS.
#    Measured before it was written: matching a row's `targets` as well would
#    move 62 rows instead of 26, and 36 of those 62 arrive through ONE class --
#    `session_relative_reference`, the time anchor almost every migrator emits
#    alongside its real output. The `time_reference` signature decides the time
#    model; it says nothing about whether `treatment_drug`'s disposition is
#    settled. Those 36 are counted and reported as their own bucket instead, so
#    the reach a looser join would buy is visible rather than taken.
#
# 3. IT MATCHES EXACTLY, IN BOTH NAMESPACES, AND NORMALISES NOTHING. A ledger
#    row is keyed by its v1 (NDI, camelCase) name; a family member may be
#    EITHER a v1 name (`imageCollection`, `imageStack_parameters` -- status_board
#    says so in its own comment) or a V_eta snake_case class (`acquisition_epoch`).
#    So the row's v1 name AND its V_eta class name are each compared, unchanged,
#    by string equality. No lowercasing, no underscore-stripping, no substring:
#    `filter` is a substring of `frequency_filter` and `image` of `image_stack`,
#    and CLAUDE.md records five classes a previous generator got wrong on
#    exactly this axis. Names that match only after normalisation are REPORTED
#    as near misses and never joined.


def _normalised(name):
    """CLAUDE.md's own spelling sweep: lowercase, strip underscores.

    Used ONLY to REPORT a near miss. Never to join -- a join on this would make
    `demo_ndi` and `demoNDI` the same class, which is a fact about spelling and
    not about identity.
    """
    return name.lower().replace("_", "")


def family_index(families=None):
    """class name -> [family names that claim it], over ALL families.

    Signed or not. The unsigned half is what lets a gap be labelled "a family
    tracks this class and nobody has signed it" instead of "nothing tracks it",
    which are different questions for the team.
    """
    idx = {}
    for name, members, _plan, _what, _status in (
            families if families is not None else status_board.FAMILIES):
        for m in members:
            idx.setdefault(m, []).append(name)
    return idx


def signed_family_index(signed=None):
    """class name -> [{family, document, line, signoff}], SIGNED families only."""
    idx = {}
    sf = status_board.signed_families() if signed is None else signed
    for fam in sorted(sf):
        info = sf[fam]
        for m in info["members"]:
            idx.setdefault(m, []).append({
                "family": fam, "document": info["plan"], "line": info["line"],
                "signoff": info["signoff"]})
    return idx


def match_signed_family(v1_class, veta_class, index):
    """The signed family that names THIS row, or None. Pure; exact match only.

    Both namespaces are offered and the match records WHICH one hit, because
    `imageStack_parameters` matches on its v1 name while its V_eta name
    (`image_stack_parameters`) matches nothing -- the snake/camel split, and a
    join that reported only "matched" would hide which spelling carried it.

    A row claimed by TWO different signed families is returned with `conflict`
    populated rather than silently resolved: status_board already fails when two
    families claim one class, but it compares within one namespace and this join
    spans two, so the condition is reachable here and unreachable there.
    """
    hits = []
    for name, how in ((v1_class, "v1_class"), (veta_class, "veta_class")):
        for entry in (index.get(name) or []) if name else []:
            hits.append(dict(entry, matched_on=how, matched_name=name))
    if not hits:
        return None
    fams = sorted({h["family"] for h in hits})
    first = dict(hits[0])
    first["conflict"] = fams if len(fams) > 1 else []
    return first


# The gap buckets, named so "nothing to see" and "nobody looked" cannot print
# the same way. Every rung-1 row that is still `not measured` after the join
# carries exactly one of these.
GAP_FAMILY_UNSIGNED = "a family names this class and that family is UNSIGNED"
GAP_TARGET_ONLY = ("no family names this class; a SIGNED family names a class "
                   "its migrator EMITS")
GAP_NOTHING_TO_JOIN = ("no family names this class, and the row has no V_eta "
                       "class and no target either")
GAP_NO_FAMILY = "no family in FAMILIES names this class"


def governance_gap(row, all_idx, signed_idx):
    """Why no signature is FINDABLE for this row, in ONE named bucket, or None."""
    if row.get("decided_signoff") or row.get("no_target_signoff") \
            or row.get("decided_by_family"):
        return None
    identity = [n for n in (row.get("v1_class"), row.get("veta_class")) if n]
    if any(all_idx.get(n) for n in identity):
        return GAP_FAMILY_UNSIGNED
    emitted = list(row.get("targets") or []) + list(row.get("decided_targets") or [])
    if any(signed_idx.get(t) for t in emitted):
        return GAP_TARGET_ONLY
    if not row.get("veta_class") and not emitted:
        return GAP_NOTHING_TO_JOIN
    return GAP_NO_FAMILY


def signature_join_census(rows, all_idx, signed_idx):
    """RULE 5 for the join: what it inspected, what it moved, what it did not.

    The three outputs a reader needs and could not get before:
      * the DENOMINATOR and how many rows the signature reached;
      * every unmoved row bucketed by CAUSE, so "decided but unrecorded" and
        "nobody has looked at this class" stop printing identically;
      * the SPELLING near misses, which is the failure mode CLAUDE.md records
        five instances of and which a join reports as a clean zero.
    """
    from collections import Counter
    matched = [r for r in rows if r.get("decided_by_family")]
    gaps = Counter()
    gap_rows = {}
    for r in rows:
        g = r.get("governance_gap")
        if g:
            gaps[g] += 1
            gap_rows.setdefault(g, []).append(r["v1_class"])
    # Which signed-family class each target-only row reached, so the bucket is
    # inspectable rather than a number. `session_relative_reference` dominates
    # it and that is the whole argument for excluding emitted targets.
    via = Counter()
    for r in rows:
        if r.get("governance_gap") != GAP_TARGET_ONLY:
            continue
        for t in list(r.get("targets") or []) + list(r.get("decided_targets") or []):
            for e in signed_idx.get(t) or []:
                via[t + " (" + e["family"] + ")"] += 1

    row_names = {n for r in rows for n in (r["v1_class"], r.get("veta_class")) if n}
    near = []
    for member in sorted(all_idx):
        if member in row_names:
            continue
        for n in sorted(row_names):
            if _normalised(member) == _normalised(n):
                near.append({"family_member": member, "ledger_name": n,
                             "families": all_idx[member]})
    unmatched_members = sorted(m for m in all_idx if m not in row_names)
    return {
        "rows_inspected": len(rows),
        "rows_matched_by_a_signed_family": len(matched),
        "matched_on": dict(Counter(r["decided_by_family"]["matched_on"]
                                   for r in matched)),
        # WHICH NAMESPACE UNIQUELY CARRIED THE MATCH. `matched_on` records the
        # FIRST hit and the v1 name is offered first, so it would read "34 on
        # v1_class" even if every one of them also matched on its V_eta name.
        # These two say whether the second namespace is doing any work at all
        # -- 0 today, and that is worth knowing before anyone deletes it.
        "matched_on_v1_class_only": sum(
            1 for r in matched
            if r["v1_class"] in signed_idx
            and (r.get("veta_class") or "") not in signed_idx),
        "matched_on_veta_class_only": sum(
            1 for r in matched
            if r["v1_class"] not in signed_idx
            and (r.get("veta_class") or "") in signed_idx),
        "matched_by_family": dict(Counter(r["decided_by_family"]["family"]
                                          for r in matched)),
        "conflicting_claims": sorted(
            r["v1_class"] for r in matched if r["decided_by_family"]["conflict"]),
        "unmoved_by_cause": {k: gaps.get(k, 0) for k in (
            GAP_FAMILY_UNSIGNED, GAP_TARGET_ONLY, GAP_NOTHING_TO_JOIN,
            GAP_NO_FAMILY)},
        "unmoved_rows_by_cause": {k: sorted(v) for k, v in gap_rows.items()},
        "target_only_reached_via": dict(via.most_common()),
        # A family member that names no ledger row is NORMAL -- families track
        # V_eta target classes too (`acquisition_epoch`, `control_designation`).
        # Reported as a count, with the spelling near misses split out, because
        # a member that SHOULD have matched and did not is invisible otherwise.
        "family_members_matching_no_ledger_row": len(unmatched_members),
        "spelling_near_misses": near,
    }


LEDGER_BLURB = (
    "One row per did_v1 SOURCE class, from BOTH v1 writers: the NDI production "
    "templates (read from NDI-matlab `origin/main`, not a lagging feature branch) "
    "AND the vhlab app/calculator classes that appear in real corpora but ship no "
    "NDI template (footprint = a bespoke migrator that consumes them). Post-v1 DID "
    "intermediate classes (zarr, directory, the `*_observation` leaves, ...) are "
    "V_eta TARGETS, not v1 sources, and are excluded."
)


def build_ledger():
    """Return (veta_index, v1_dict, rows) where each row is a dict:
    {v1_class, veta_class|None, disposition, migrator(bool), source(ndi|app), gap(bool)}.
    A `gap` is a v1 class with NO V_eta class and NO bespoke migrator -- unmapped,
    the actionable coverage hole (e.g. classes NDI/main added after V_eta forked)."""
    # THE THIRD CONSUMPTION CHANNEL, read HERE rather than in main() so every
    # caller that builds rows -- the tool, the tests, the board -- reads the
    # same declarations. It cannot promote a row on its own: a failed read
    # leaves the index empty and every rung exactly where it was.
    batch_pass_declarations()
    # THE FOURTH, read in the same place and for the same reason.
    helper_declarations()
    veta = veta_index()
    v1 = v1_classes()
    migs = migrator_files()
    vz = vzeta_classes()
    tmap = targets_map()
    # THE RENAME JOIN, computed over the WHOLE universe before any row is built
    # (see `rename_target_owner`: uniqueness cannot be accumulated per row).
    RENAME_OWNER.clear()
    RENAME_OWNER.update(rename_target_owner({
        _cn: list((tmap.get(snake(_cn)) or tmap.get(_cn) or {}).get("targets", []))
        for _cn in sorted(v1)}))
    rows = []
    for cn in sorted(v1):
        sn = snake(cn)
        # find its V_eta class: by snake name, else by raw name
        vname = sn if sn in veta else (cn if cn in veta else None)
        mig = bool(cn in migs or sn in migs)
        # emitted V_eta targets: prefer the curated map (real decomposition), else the
        # same-name class (passthrough/rename). Keyed by snake source name.
        tinfo = tmap.get(sn) or tmap.get(cn) or {}
        targets = list(tinfo.get("targets", []))
        carried = list(tinfo.get("carried", []))
        second_pass = list(tinfo.get("second_pass", []))
        how = tinfo.get("how", "")
        tflags = tinfo.get("flags", "")
        # WHERE THE TARGET COLUMN COMES FROM, stated per row instead of implied.
        #
        # This line used to be `targets = [vname]` with the comment
        # "passthrough/rename: same-name class is the target" -- and that is an
        # ASSERTION, not an observation. For 34 of 102 rows there is no curated
        # entry at all, and the fallback rendered every one of them as
        # `X -> X`: indistinguishable from a measured 1:1 migration. Fifteen of
        # those carry a SIGNED decision saying the class becomes something else
        # (filenavigator -> epoch_file_pattern, daqsystem -> acquisition_system,
        # and so on), so the ledger was quietly contradicting the plan documents.
        #
        # It is the same failure already paid for twice here: the old
        # "dissolved (rename/decompose)" label on 32 rows, and chunk (a)'s
        # "all 0-usage, safe to delete". A default that reads as a finding.
        #
        # Three states now, and they are different claims:
        #   emitted      a migrator really emits these (the curated map)
        #   passthrough  no migrator: the document reaches validation UNDER THE
        #                SAME-NAME CLASS. True today, and NOT a statement about
        #                where the class is going.
        #   unknown      no migrator and no same-name class to land on.
        # FOUR states, not three. The first draft of this split had only
        # `passthrough` for "no curated entry", and its own test caught the
        # error immediately: `control_stimulus_ids` HAS a migrator, so labelling
        # it "no migrator; passes through" replaced one false statement with
        # another. A migrator with no curated entry is not a passthrough -- it
        # emits something nobody has written down.
        # FIVE states as of 2026-08-10, and the fifth exists because writing the
        # 28 per-class accounts broke the fourth. A curated entry USED TO mean
        # "we know what a migrator emits" -- so simply describing a class flipped
        # its row to `emitted`, and
        # test_no_passthrough_row_claims_a_migrator_emits_it caught it on the
        # first run, exactly as its docstring predicted ("marking a row emitted
        # because a decision says so ... would make the ledger claim a migration
        # nobody wrote").
        #
        # The two things had been conflated: an entry can record WHAT WILL HAPPEN
        # (a signed decision, in `decided_targets`) without claiming anything is
        # produced today. So an entry that names no `targets` and no
        # `second_pass` is a DECISION, not an emission:
        #   decided      the disposition is recorded and signed; NO migrator
        #                emits it yet. Includes dissolutions and deletions, which
        #                legitimately have no target at all.
        _claims_emission = bool((tinfo or {}).get("targets")
                                or (tinfo or {}).get("second_pass"))
        if tinfo and not _claims_emission:
            target_source = "decided"        # recorded + signed; nothing emits it yet
            targets = []
        elif tinfo:
            target_source = "emitted"        # curated: we know what it emits
        elif mig:
            target_source = "uncurated"      # a migrator runs; its output is unrecorded
            targets = [vname] if vname else []
        elif vname:
            target_source = "passthrough"    # no migrator: lands on the same-name class
            targets = [vname]
        else:
            target_source = "unknown"        # no migrator, nothing to land on
        note = v1[cn]
        source = "app" if str(note).startswith("app-generated") else "ndi"
        nonprod = cn in _NONPROD_CLASSES
        reviewed = (cn in vz or sn in vz or cn in _PRE_ZETA_DISSOLVED)
        # A genuine gap: no V_eta home, no migrator, never reviewed (absent from the
        # V_zeta base), and not test/demo scaffolding. Catches classes NDI added
        # after V_eta forked (ensemble, kilosort_clusters, ...) without false-flagging
        # the many classes the migration reviewed and deliberately dissolved.
        gap = vname is None and not mig and not reviewed and not nonprod
        if vname:
            disp = veta[vname]
        elif gap:
            disp = "UNMAPPED (needs a V_eta home)"
        elif cn in _PRE_ZETA_DISSOLVED:
            disp = "dissolved → " + _PRE_ZETA_DISSOLVED[cn]
        elif nonprod:
            disp = "test/demo fixture (non-production)"
        elif mig:
            # No V_eta class, but a bespoke migrator CONSUMES this class -- the
            # documents are transformed into other classes and the source schema is
            # deliberately phase-8 deleted. Genuinely accounted for; the migrator is
            # the evidence (treatment, virus_injection, image_stack, subject_group...).
            disp = "consumed by migrator (no tombstone)"
        else:
            # No V_eta class AND no migrator, but present in the V_zeta base -- so the
            # migration SAW this class at some point. That is ALL we know: nothing
            # here says the documents went anywhere.
            #
            # This used to read "dissolved (rename/decompose)" for both this case and
            # the `mig` case above, which asserted a deliberate decision from the mere
            # absence of evidence and turned an unknown into a reassuring claim. It
            # was wrong at least twice: `imageCollection` (no class, no migrator, and
            # `image.imageCollection_id` still points at it) and `subjectmeasurement`
            # (still actively written by four NDI emitters). Both read as
            # accounted-for while in fact having nowhere to go.
            #
            # The honest label names the evidence, not a conclusion. Promote a row out
            # of this state by recording WHERE the class went -- in _PRE_ZETA_DISSOLVED
            # with a verification note -- or by giving it a home or a migrator.
            disp = "no V_eta home, no migrator -- UNVERIFIED"

        # ---- decided targets: the curated file, PLUS the signed transcriptions
        # ONE FACT, ONE PLACE. `V_eta_migration_targets.json` is the curated
        # home for `decided_targets`; the table above fills rows it never got.
        # If both ever name the same class the ledger stops rather than picking
        # one -- two records of one fact that agree by coincidence is the
        # binding-strength defect this repository already has open (#32), and
        # it is not worth reproducing for a target list.
        curated_decided = list((tinfo or {}).get("decided_targets") or [])
        # ---- THE ANSWER SINK, added 2026-08-13 -------------------------------
        # The confirm sheet asks 69 classes "is what the migrator ALREADY emits
        # the answer we want?" and until today a YES had nowhere to go. The two
        # existing keys both mean something else: `targets` is GENERATED from the
        # call graph and cannot be hand-set, and `decided_targets` is defined by
        # the map's own header as "a signed decision NO MIGRATOR IMPLEMENTS YET"
        # -- the exact opposite of a confirmed emission. So five classes signed
        # on 2026-08-13 stayed at stage 1 with rung 2 reading `not measured`,
        # and every other answered row would have done the same.
        #
        # `confirmed_targets` is that sink, and it is a THIRD key rather than a
        # reuse of `decided_targets` on purpose: collapsing "already right" into
        # "still owed" would make the ladder report finished work as a gap, and
        # this repository has paid for exactly that kind of conflation before.
        #
        # IT IS NOT A FREE PASS. The confirmed set is fed through the SAME rung 2
        # and rung 3 machinery as any other decided set -- so if a migrator later
        # stops emitting one of these classes, rung 3 goes `no` and the stale
        # confirmation becomes visible instead of silently standing.
        confirmed = (tinfo or {}).get("confirmed_targets") or {}
        confirmed_list = list(confirmed.get("targets") or [])
        signed = DECIDED_TARGETS_BY_SIGNOFF.get(cn) or \
            DECIDED_TARGETS_BY_SIGNOFF.get(sn)
        decided_cite = None
        if confirmed_list and (curated_decided or signed):
            raise SystemExit(
                f"coverage: `{cn}` carries BOTH `confirmed_targets` and a "
                "decided-target record. `confirmed_targets` means the EMITTED "
                "set is the end state; `decided_targets` means a signed "
                "decision no migrator implements yet. A class cannot be both -- "
                "delete whichever is wrong.")
        if signed and curated_decided:
            raise SystemExit(
                f"coverage: `{cn}` has decided_targets in BOTH "
                f"V_eta_migration_targets.json ({curated_decided}) and "
                f"DECIDED_TARGETS_BY_SIGNOFF ({signed[0]}). One fact, one place -- "
                "delete whichever is the copy.")
        if signed:
            decided_targets = list(signed[0])
            decided_source = "signoff_transcription"
            decided_cite = {"document": signed[1], "signoff_fragment": signed[2],
                            "mapping_fragment": signed[3], "account": signed[4]}
        elif confirmed_list:
            decided_targets = confirmed_list
            decided_source = "confirmed_emission"
            # `decided_cite` STAYS None, and that is load-bearing rather than an
            # omission: this field becomes the row's GOVERNANCE citation, and a
            # confirmation of a target set is not a signature. Setting it here
            # overrode the family-derived citation on all five confirmed rows,
            # leaving them `signed` while citing a document-less record --
            # caught by test_every_signed_row_cites_a_real_team_signoff. The
            # confirmation's own provenance lives in the map beside the
            # confirmed set, where it describes what it actually is.
        else:
            decided_targets = curated_decided
            decided_source = "curated_targets_file" if curated_decided else None

        # ---- why the DECIDED state names no target, stated rather than inferred
        #
        # This is a fact about the DECISION, not about today's emission, and the
        # first draft of it conflated the two: it only looked at the table when
        # a row had no targets at all, so `binaryseries_parameters` -- signed
        # "folds into the data_body model and is retired", but emitting itself
        # through a guarded passthrough today -- recorded no reason at all. Its
        # own test caught that on the first run. What a migrator emits today and
        # what the team signed are different columns; a recorded dissolution
        # governs the second one whatever the first says.
        no_target_cite, no_target_account = None, None
        entry = NO_TARGET_BY_DECISION.get(cn) or NO_TARGET_BY_DECISION.get(sn)
        if entry:
            no_target_reason, plan, frag, no_target_account = entry
            no_target_cite = {"document": plan, "signoff_fragment": frag}
        elif decided_targets and decided_targets == [cn if cn in veta else vname]:
            # Its decided target IS itself: a deliberate passthrough, which is
            # neither a dissolution nor a gap. Downstream consumers strip a
            # self-target (`open_class_state` does, correctly -- a passthrough
            # is not build evidence), so without this the row would arrive at
            # the board looking blank.
            no_target_reason = NO_TARGET_PASSTHROUGH
        elif targets or second_pass or decided_targets:
            no_target_reason = None
        elif nonprod or cn in _PRE_ZETA_DISSOLVED:
            # Not a gap in the DECISION record: test scaffolding and pre-V_zeta
            # dissolutions carry their own honest label in the `disposition`
            # column. Flagging them here would drown the rows really missing a
            # target. An UNMAPPED row is NOT excused -- `unmapped` says nobody
            # gave it a home, which is precisely a missing decision.
            no_target_reason = None
        else:
            no_target_reason = NO_TARGET_UNRECORDED

        # ---- build state, SPLIT. Schema and migrator are different halves and
        # a single flag reads as neither. The authored `flags` prose says
        # "DECIDED AND SIGNED, BUILD NOT DONE" on 8 rows -- true of the
        # migrator, and false of the schema for 3 of them (`app`'s `software`
        # is built and shipping). A reader acting on the undifferentiated
        # sentence re-authors schema that already exists.
        #
        # CORRECTED 2026-08-17: "true of the migrator" IS NOT TRUE OF `app`,
        # and that is the example this comment leads with. `app`'s migrator
        # half is done -- `+migrators_j/private/jSoftwareFromApp.m` folds it
        # into a `software` entity at six call sites -- and it read as
        # outstanding because all three consumption channels ask about a NAME
        # and that helper is named after neither the source nor the target.
        # The SPLIT this comment argues for is unaffected and is the reason the
        # error was findable at all; what was wrong was the assumption that the
        # migrator half is the reliable one. It was the schema half that
        # happened to be right about `app`. See `helper_declarations()`.
        _named = list(decided_targets)
        # THE THIRD CONSUMPTION CHANNEL, carried as its own two fields so the
        # credit is never mistaken for a per-class migrator's. `_consumers` is
        # every batch post-pass DECLARING it reads this class; `_emits` is only
        # the ATTRIBUTED emissions -- an `UNATTRIBUTED` line and the `nothing`
        # form contribute an empty list, deliberately.
        # `targets` is what the DERIVATION could read. A row may also carry
        # `unread_targets` -- classes it provably emits whose names the walker
        # cannot resolve (a struct field carried across two files), authored
        # with a citation. Rung 3 asks whether the migrator EMITS the decided
        # classes, and those are emitted; excluding them would fail the rung for
        # a limitation of the reader rather than a fact about the migrator.
        _unread = list(((tinfo or {}).get("unread_targets") or {}).get("targets")
                       or [])
        _emitted_known = set(targets) | set(_unread)
        _bp = batch_pass_entries(cn, vname)
        # The rename spelling, added last so it can only ADD a pass, never
        # displace one already matched by a direct spelling.
        for _re in rename_entries(cn):
            if _re["pass"] not in {x["pass"] for x in _bp}:
                _bp.append(_re)
        _bp_targets = sorted({t for e in _bp for t in e["targets"]})
        # THE FOURTH CHANNEL, carried apart from the third for the same reason
        # the third is carried apart from the first: a reader must be able to
        # tell WHICH mechanism earned the rung. A batch post-pass runs once
        # over the whole corpus; a shared helper runs inside a migrator that
        # is named after some OTHER class. Summing them would hide the `app`
        # shape, which is the shape this channel exists to surface.
        _hp = helper_entries(cn, vname)
        _hp_targets = sorted({t for e in _hp for t in e["targets"]})
        _eb = tinfo.get("emitted_by")
        build_state = {
            "schema_targets_named": len(_named),
            "schema_targets_built": sorted(t for t in _named if t in veta),
            "schema_targets_missing": sorted(t for t in _named if t not in veta),
            # A migrator implements the decision only when it EMITS the decided
            # class. Emitting the source class back out is a passthrough.
            "migrator_emits_decided_targets": bool(
                _named and all(t in _emitted_known for t in _named)),
            "has_per_class_migrator": mig,
            "batch_pass_consumers": [e["pass"] for e in _bp],
            "batch_pass_emits": {e["pass"]: e["targets"] for e in _bp
                                 if e["targets"]},
            "batch_pass_emits_decided_targets": bool(
                _named and not all(t in targets for t in _named)
                and all(t in set(targets) | set(_bp_targets) for t in _named)),
            "helper_consumers": [e["helper"] for e in _hp],
            "helper_emits": {e["helper"]: e["targets"] for e in _hp
                             if e["targets"]},
            # Credit only where the decided set is NOT already satisfied by the
            # per-class migrator, so a row cannot be credited twice and the
            # rollup's "rows this channel moved" stays a true count.
            "helper_emits_decided_targets": bool(
                _named
                and not all(t in _emitted_known for t in _named)
                and all(t in _emitted_known | set(_bp_targets) | set(_hp_targets)
                        for t in _named)),
            # THE FIRST EMISSION SHAPE OF ROW 107, and the last to get a home.
            # A SUPERCLASS-ONLY v1 class has no documents of its own -- its
            # content rides as a BLOCK on another class's document -- so no
            # migrator can ever be named after it, and rung 3's question is
            # unanswerable in the form it asks. `filter` is the case: its fold
            # is real and tested, carried by `pyraview`'s migrator.
            #
            # AUTHORED, NOT DERIVED, AND DELIBERATELY SO. The derivation was
            # measured and does not exist: 9 rows have a decided target that
            # some other row's migrator emits, and 8 of them name a SHARED
            # target (`sampled_body` has 6 emitters, `subject` 5) where the
            # standing attribution limit forbids any conclusion. Inferring
            # would credit 8 rows on no evidence to reach the 1 that deserves
            # it. So the map states the emitter by name, with its citation, the
            # same way `_EDGE_REFERENT_UNIQUE` is declared rather than derived.
            "emitted_by_migrator": (_eb or {}).get("migrator"),
            "emitted_by_targets": sorted((_eb or {}).get("targets") or []),
            # THE UNION HERE IS DELIBERATELY NARROWER THAN THE BATCH-PASS ONE
            # ABOVE, and the first draft got it wrong by copying that line: it
            # left `_bp_targets` in, so a class covered by a BATCH PASS also
            # set this flag. The rung was unaffected (the batch branch is
            # evaluated first) which is exactly why it would have gone
            # unnoticed -- a flag that lies while the behaviour looks right.
            # Caught by `test_only_rows_with_an_authored_emitted_by_are_credited`.
            "emitted_by_emits_decided_targets": bool(
                _eb and _named and not all(t in targets for t in _named)
                and all(t in set(targets) | set((_eb or {}).get("targets") or [])
                        for t in _named)),
        }

        rows.append({
            "v1_class": cn,
            "veta_class": vname,
            "disposition": disp,
            "migrator": mig,
            "source": source,
            "nonprod": nonprod,
            "gap": gap,
            "targets": targets,
            # The DECIDED target, carried separately so it can never be mistaken
            # for an emitted one. `targets` means "a migrator produces this";
            # this means "the team signed that it will". The viewer renders them
            # in different voices for that reason.
            "decided_targets": decided_targets,
            "decided_targets_source": decided_source,
            "decided_signoff": decided_cite,
            "target_source": target_source,
            "no_target_reason": no_target_reason,
            "no_target_reason_label": NO_TARGET_REASON_LABEL.get(no_target_reason),
            "no_target_account": no_target_account,
            "no_target_signoff": no_target_cite,
            "target_gap": no_target_reason == NO_TARGET_UNRECORDED,
            "build_state": build_state,
            "carried": carried,
            "second_pass": second_pass,
            "how": how,
            "target_flags": tflags,
        })
    # THE DERIVED COLUMNS, added last because they read the finished row. Each
    # is a function of fields already on that row -- there is no list here to
    # hand-set and nothing to override any of them with.
    #
    # ORDER IS LOAD-BEARING: the signature join fills `decided_by_family`, the
    # gap bucket reads it, `governance_state` reads both, and the completion
    # ladder reads NONE of them. That last clause is the restructure of
    # 2026-08-12 in one line -- a signature can no longer cap a build stage.
    all_idx, signed_idx = family_index(), signed_family_index()
    for r in rows:
        r["decided_by_family"] = match_signed_family(
            r["v1_class"], r["veta_class"], signed_idx)
        r["families_naming_this_class"] = sorted(
            {f for n in (r["v1_class"], r["veta_class"]) if n
             for f in all_idx.get(n, [])})
        r["governance_gap"] = governance_gap(r, all_idx, signed_idx)
        r["governance"] = governance_state(r)
        r["stage"] = stage_ladder(r, CORPUS_SCAN)
    # sanity: every named target class should exist in the built V_eta schema
    unknown = sorted({t for r in rows
                      for t in (r["targets"] + r["second_pass"] + r["decided_targets"])
                      if t not in veta})
    if unknown:
        print("  WARNING: target classes not in V_eta schema: " + ", ".join(unknown))
    return veta, v1, rows


# ============================================================================
# TWO QUANTITIES, NEVER SUMMED: what a class has BUILT, and whether we can
# PROVE the team agreed to it.
# ============================================================================
#
# THE DESIGN ERROR THIS REPLACES, stated plainly because it was expensive.
# Until 2026-08-12 there was ONE ladder and its first rung was `disposition
# DECIDED`. Every completion rung was gated behind it, so a class with a
# working migrator reported stage 0 whenever no sign-off could be machine-found
# for it. That measures our BOOKKEEPING and renders it as the migration's
# progress -- 95 of 102 rows read "stage 0" while 86 of them had a migrator
# consuming their documents. It is the reassuring-direction error inverted:
# the number was pessimistic, and a pessimistic number that nobody can act on
# is just as useless as an optimistic one.
#
# DECIDEDNESS AND BUILTNESS ARE ORTHOGONAL. A migrator exists or does not,
# whatever any document says; a signature exists or does not, whatever any
# migrator does. So:
#
#   `stage`       THE COMPLETION LADDER. What has been BUILT for this class,
#                 rungs 1..4, strictly ordered among themselves. Governance
#                 cannot cap it.
#   `governance`  A FLAG BESIDE IT, never in the chain: can this tool find the
#                 team's signature for this class's disposition? Its states are
#                 about the RECORD, and none of them is progress.
#
# The two are printed as two columns and must never be added together. A class
# can be fully built and unsigned (`valid_interval` was, in this repository's
# own words: BUILT AHEAD OF THE DECISION) or signed and unbuilt (most of the
# decided families). Those are different problems for different people.
#
# THE COMPLETION LADDER IS DERIVED. Never hand-set, never overridable by a list
# beside a paragraph. Every boundary below reads a field that already exists on
# the row, and the `why` string on each rung names the field it read, so a stage
# can be audited without reading this file.
#
# FOUR STATES PER RUNG, NOT TWO. This is the whole design, and it is the
# difference between an instrument and a reassurance:
#
#   yes           the evidence is on the row
#   no            POSITIVE evidence the rung is not met (a target named and not
#                 built; a migrator that does not emit what was decided)
#   n/a           the rung cannot apply, and a SIGNED line says why (a class
#                 signed to dissolve has no target class to build)
#   not measured  this tool cannot see the answer. NOT a `no`.
#
# `not measured` exists because of operating rule 3, and it is why rung 4 reads
# `not measured` on every row in a run with no corpus report rather than `no`:
# "no corpus proved it" and "nobody looked" are different facts.
#
# THE RUNG ORDER, AND THE ONE PLACE IT IS A JUDGEMENT CALL. Rung 3 (the
# migrator emits the decided targets) genuinely requires both rung 1 (something
# consumes the class) and rung 2 (the target classes exist), so it sits above
# both. Rungs 1 and 2 do not imply each other in either direction -- a schema
# can be built before its migrator and a migrator can run before its target is
# named -- so their order is a TIE, and it is broken toward the rung that is
# FULLY MEASURED. `a migrator CONSUMES it` has an answer on all 102 rows (86
# yes, 16 no); `target classes EXIST` reads `not measured` on 74, because no
# target is recorded for them. Putting the unmeasured rung first would cap 74
# rows below a fact this tool knows for certain, which is the burial this
# restructure exists to end. The tie-break is stated here so it is a choice on
# the record rather than an accident of declaration order.
#
# THE ANTI-VACUITY RULE. A rung is `yes` only on evidence PRESENT, never on an
# empty list. `schema_targets_missing == []` is TRUE for all 102 rows, and for
# 77 of them it is true because no target was ever named -- an empty list
# reading as "everything is built". The targets rung therefore requires
# `schema_targets_named > 0` as well, which is why it is satisfied by 25 rows
# and not by 102. The same trap is what `_no_target_cell` above was written to
# close one column over.
STAGE_NAMES = {
    0: "source identified",
    1: "a migrator CONSUMES it",
    2: "its decided target classes EXIST in the build",
    3: "the migrator emits THE DECIDED targets",
    4: "CORPUS-PROVEN",
}
COMPLETION_RUNGS = (1, 2, 3, 4)
S_YES = "yes"
S_NO = "no"
S_NA = "n/a"
S_NOT_MEASURED = "not measured"
# States that let the ladder continue upward. `not measured` deliberately does
# NOT: a class cannot be reported as having climbed past a rung nobody read.
_STAGE_PASSING = (S_YES, S_NA)


class StageDataError(Exception):
    """A row whose fields cannot carry the classifier.

    Raised, caught, and REPORTED as an unclassifiable row -- never swallowed.
    A row that cannot be placed is the one row a reader most needs to see, and
    dropping it would shrink the denominator silently, which is the failure
    mode operating rule 5 exists for.
    """


_MISSING = object()


def _need(row, key, kinds):
    val = row.get(key, _MISSING)
    if val is _MISSING:
        raise StageDataError(f"row has no `{key}` field")
    if not isinstance(val, kinds):
        raise StageDataError(
            f"`{key}` is {type(val).__name__}, expected "
            + "/".join(k.__name__ for k in (kinds if isinstance(kinds, tuple) else (kinds,))))
    return val


# ---------------------------------------------------------------------------
# GOVERNANCE -- a FLAG, not a rung. Nothing here may cap a completion stage.
# ---------------------------------------------------------------------------
G_SIGNED = "signed"
G_DISPUTED = "DISPUTED"
G_UNSIGNED = "family UNSIGNED"
G_NOT_FOUND = "no signature found"

# The order matters and is asserted by a test: DISPUTED outranks a derived
# family signature. `ngrid` is claimed by the SIGNED family `image / ngrid` AND
# carries a transcription saying `V_eta_image_model_plan.md` states two
# incompatible dispositions. Letting the family join answer first would erase a
# recorded contradiction with a lookup -- the disagreement is the finding.
GOVERNANCE_STATES = (G_SIGNED, G_DISPUTED, G_UNSIGNED, G_NOT_FOUND)


def governance_state(row):
    """Can this tool find the TEAM's signature for this class? A flag, not progress.

    NONE OF THESE FOUR STATES IS AN ACHIEVEMENT AND NONE OF THEM IS A STAGE.
    `signed` says the record is findable, not that anything was built;
    `no signature found` says this tool could not reach one, NOT that no
    decision exists -- operating rule 3, and the reason the state is named for
    the search and not for the record.

    Two independent sources, in this order:
      1. a CHECKED TRANSCRIPTION on the row (`DECIDED_TARGETS_BY_SIGNOFF` /
         `NO_TARGET_BY_DECISION`), re-verified against its document on every
         build by check_decision_citations();
      2. the DERIVED join: a signed decision family in status_board.FAMILIES
         names this class. Re-derived every build, never transcribed.
    """
    reason = row.get("no_target_reason")
    if reason == NO_TARGET_DISPUTED:
        doc = (row.get("no_target_signoff") or {}).get("document", "?")
        return {"state": G_DISPUTED, "signoff": row.get("no_target_signoff"),
                "why": (f"the transcription on this row says `{doc}` states two "
                        "incompatible dispositions. POSITIVE evidence that the "
                        "record disagrees with itself -- not an absence")}
    cite = row.get("decided_signoff") or row.get("no_target_signoff")
    if cite:
        doc = cite.get("document", "?")
        return {"state": G_SIGNED, "signoff": cite,
                "why": (f"a TEAM-SIGN-OFF line in `{doc}` is transcribed onto this "
                        "row and re-checked against that document by "
                        "check_decision_citations() on every ledger build")}
    fam = row.get("decided_by_family")
    if fam:
        return {"state": G_SIGNED, "signoff": fam,
                "why": ("DERIVED, not transcribed: the decision family "
                        f'`{fam["family"]}` names this class as `{fam["matched_name"]}` '
                        f'({fam["matched_on"]}), and that family is signed at '
                        f'`{fam["document"]}`:{fam["line"]}. Re-derived on every '
                        "build from status_board.signed_families(); a family "
                        "with no signature reaches nothing")}
    gap = row.get("governance_gap")
    if gap == GAP_FAMILY_UNSIGNED:
        fams = row.get("families_naming_this_class") or []
        return {"state": G_UNSIGNED, "signoff": None,
                "why": ("the decision family "
                        + ", ".join("`" + f + "`" for f in fams)
                        + " names this class and carries no sign-off line this "
                          "tool will honour. What is missing is a SIGNATURE, "
                          "not a model")}
    claim = row.get("decided_targets_source") == "curated_targets_file"
    extra = ("; V_eta_migration_targets.json DOES claim a signed decision for "
             "this class (`decided_targets`), but that claim is authored and "
             "UNCHECKED" if claim else "")
    return {"state": G_NOT_FOUND, "signoff": None,
            "why": ((gap or GAP_NO_FAMILY) + ". This is the absence of a "
                    "FINDABLE signature -- a transcription, or a signed family "
                    "naming this class -- and NOT evidence that no decision "
                    "exists" + extra)}


def _rung_targets_built(row):
    """Named target classes, all present in the built V_eta set."""
    bs = _need(row, "build_state", dict)
    named = _need(bs, "schema_targets_named", int)
    missing = _need(bs, "schema_targets_missing", list)
    if named > 0:
        if missing:
            return S_NO, ("`build_state.schema_targets_missing` names "
                          + ", ".join(f"`{t}`" for t in missing)
                          + f" -- {len(missing)} of {named} decided target class(es) "
                          "are absent from the built V_eta set")
        return S_YES, (f"all {named} decided target class(es) are present in the "
                       "built V_eta set (`build_state.schema_targets_missing` is "
                       "empty AND `schema_targets_named` is non-zero)")
    if row.get("no_target_reason") == NO_TARGET_DISSOLVED:
        doc = (row.get("no_target_signoff") or {}).get("document", "?")
        return S_NA, (f"signed to DISSOLVE in `{doc}`: there is no target class "
                      "to build, so the rung cannot apply")
    return S_NOT_MEASURED, (
        "`build_state.schema_targets_named` is 0 -- no target class is named for "
        "this row, so there is nothing to look for in the built set. This is NOT "
        "'all targets present': an empty `schema_targets_missing` is empty here "
        "because the question was never asked")


def _rung_consumed(row):
    """Something in the migration consumes documents of this class."""
    bs = _need(row, "build_state", dict)
    if _need(bs, "has_per_class_migrator", bool):
        return S_YES, ("`build_state.has_per_class_migrator` -- a per-class "
                       "migrator file named after this class exists in one of the "
                       "three convert packages")
    sp = _need(row, "second_pass", list)
    if sp:
        return S_YES, ("no per-class migrator, but `second_pass` records "
                       + ", ".join(f"`{t}`" for t in sp)
                       + " minted for this class in the NDI second pass")
    # THE THIRD CHANNEL. A DID BATCH POST-PASS (+did2/+convert) is neither a
    # per-class migrator file nor an NDI second-pass mint, and until row 107
    # this function had no field to read for it -- `generic_file` is folded by
    # `foldGenericFiles` and reported `no`. The credit is DECLARED by the pass,
    # not grepped: a bare name sweep over the convert package matches `base` in
    # 9 of the 9 passes and `app` in universalRenames, which is noise a stage
    # cannot be built on. The `why` names the pass, so a reader can always see
    # that this rung was climbed by a batch pass rather than by a migrator.
    consumers = _need(bs, "batch_pass_consumers", list)
    if consumers:
        return S_YES, ("no per-class migrator and no `second_pass` entry, but "
                       "`build_state.batch_pass_consumers` records the DID "
                       "BATCH POST-PASS(es) "
                       + ", ".join(f"`did2.convert.{p}`" for p in consumers)
                       + " DECLARING that they consume this class")
    # THE FOURTH CHANNEL. A SHARED HELPER (+migrators_j/private) runs inside a
    # migrator named after some OTHER class, so it is invisible to all three
    # questions above -- every one of which asks about a NAME. `app` read `no`
    # here while `jSoftwareFromApp` folded it at six call sites. Declared, not
    # derived: a call-graph walk was written and rejected because it credits
    # `valid_interval`, whose mint site sits behind a guard that is off by team
    # decision. Reachability cannot see dormancy; a declaration states it.
    helpers = _need(bs, "helper_consumers", list)
    if helpers:
        return S_YES, ("no per-class migrator, no `second_pass` entry and no "
                       "batch post-pass, but `build_state.helper_consumers` "
                       "records the SHARED HELPER(s) "
                       + ", ".join(f"`{h}`" for h in helpers)
                       + " DECLARING that they consume this class")
    s = BATCH_PASS_SCAN
    if not s["measured"]:
        unread = (" The batch post-pass declarations were NOT READ in this run "
                  "(" + str(s["why"]) + "), so a class consumed only by one "
                  "still reads `no` here -- an UNDERSTATEMENT, not a "
                  "measurement.")
    elif s["missing"]:
        unread = (" " + str(len(s["missing"])) + " pass(es) in the derived "
                  "chain carry NO DECLARATION (" + ", ".join(s["missing"])
                  + "), so a class consumed only by one of those is not "
                  "measured here.")
    else:
        unread = (" All " + str(s["chain_size"]) + " batch post-pass(es) in "
                  "the derived chain were read and none declares this class.")
    return S_NO, ("neither `build_state.has_per_class_migrator`, a "
                  "`second_pass` entry, nor a batch post-pass declaring it."
                  + unread)


def _rung_emits_decided(row):
    """The migrator emits the classes the decision names."""
    bs = _need(row, "build_state", dict)
    named = _need(bs, "schema_targets_named", int)
    if named > 0:
        if _need(bs, "migrator_emits_decided_targets", bool):
            return S_YES, ("`build_state.migrator_emits_decided_targets` -- every "
                           "decided target class is among the classes the "
                           "generated target map records this migrator emitting")
        want = row.get("decided_targets") or []
        have = row.get("targets") or []
        # THE SECOND AND THIRD EMISSION SHAPES OF ROW 107, and the reason this
        # branch sits BELOW the migrator one: a per-class migrator that already
        # emits the decided target needs no help, and reading the declaration
        # first would attribute a migrator's work to a batch pass.
        if _need(bs, "batch_pass_emits_decided_targets", bool):
            em = _need(bs, "batch_pass_emits", dict)
            return S_YES, (
                "the migrator named after this class does not emit the decided "
                "target(s), but `build_state.batch_pass_emits` records the DID "
                "BATCH POST-PASS(es) "
                + "; ".join(f"`did2.convert.{p}` -> "
                            + ", ".join(f"`{t}`" for t in sorted(ts))
                            for p, ts in sorted(em.items()))
                + " DECLARING the emission. A declared emission is a fact about "
                  "code the pass's own header states; it is NOT a corpus proof")
        # SHAPE (1): a SUPERCLASS-ONLY class, whose fold is carried by the
        # migrator of the class its block rides on. Last in the order for the
        # same reason as the batch-pass branch: it may not shadow work the
        # class's own migrator does.
        # `.get`, NOT `_need`, and the distinction is the shape rule this file
        # enforces everywhere else. `_need` says "this key must exist or the row
        # is malformed", which is right for the fields every row carries. This
        # channel is AUTHORED and OPTIONAL: 101 of 102 rows have no `emitted_by`,
        # so demanding the key would declare every one of them malformed and
        # force every constructed row in every test to carry a key meaning "no".
        # It did exactly that on first write -- three batch-pass tests went red
        # with an EMPTY ladder, because the raise made the row unclassifiable.
        if bs.get("emitted_by_emits_decided_targets"):
            return S_YES, (
                "no migrator can be named after this class -- it is "
                "SUPERCLASS-ONLY and its content rides as a block on another "
                "class's document -- and the target map DECLARES the emission "
                "carried by `"
                + str(bs.get("emitted_by_migrator"))
                + "`'s migrator: "
                + ", ".join(f"`{t}`" for t in (bs.get("emitted_by_targets") or []))
                + ". Authored with its citation, not inferred: 8 of the 9 rows "
                  "whose decided target another migrator emits name a SHARED "
                  "target, where nothing is attributable. NOT a corpus proof")
        # SHAPE (4): a SHARED HELPER. Last, with the other two, and for the
        # same reason -- it may not shadow the class's own migrator.
        if _need(bs, "helper_emits_decided_targets", bool):
            em = _need(bs, "helper_emits", dict)
            return S_YES, (
                "the migrator named after this class does not emit the decided "
                "target(s) -- there is no migrator named after it -- but "
                "`build_state.helper_emits` records the SHARED HELPER(s) "
                + "; ".join(f"`{h}` -> " + ", ".join(f"`{t}`" for t in sorted(ts))
                            for h, ts in sorted(em.items()))
                + " DECLARING the emission. Declared, not derived: a call-graph "
                  "walk credits `valid_interval` from a mint site behind a guard "
                  "that is OFF by team decision. NOT a corpus proof")
        hs = HELPER_SCAN
        if not hs["measured"]:
            hunread = (" The shared-helper declarations were NOT READ in this "
                       "run (" + str(hs["why"]) + "), so a target emitted only "
                       "by a helper still reads `no` -- an UNDERSTATEMENT.")
        else:
            hunread = (" %d of %d shared helper(s) declare; %d MINT a document "
                       "while declaring nothing (%s), so a target emitted only "
                       "by one of those is not measured here."
                       % (len(hs["declared"]), hs["candidates"],
                          len(hs["minting_undeclared"]),
                          ", ".join(hs["minting_undeclared"]) or "none"))
        return S_NO, ("the decided target(s) "
                      + ", ".join(f"`{t}`" for t in want)
                      + " are not all among what the migrator emits today ("
                      + (", ".join(f"`{t}`" for t in have) if have else "nothing")
                      + ")"
                      + (", nor among what any batch post-pass declares it emits"
                         if _need(bs, "batch_pass_consumers", list) else "")
                      + "." + hunread)
    if row.get("no_target_reason") == NO_TARGET_DISSOLVED:
        doc = (row.get("no_target_signoff") or {}).get("document", "?")
        return S_NA, (f"signed to DISSOLVE in `{doc}`: no target class is decided, "
                      "so there is no emission to check")
    return S_NOT_MEASURED, (
        "`build_state.schema_targets_named` is 0 -- no decided target to check an "
        "emission against")


def _rung_corpus_proven(row, evidence):
    """CORPUS-PROVEN. NOT MEASURED unless a corpus report was supplied.

    This container has no MATLAB and cannot download run artifacts, so on every
    run today this returns `not measured` WITH THOSE WORDS. It must never return
    `no`: "no corpus proved it" and "nobody looked" are different facts, and
    collapsing them is the defect `silentLoss` shipped for two days.

    `load_corpus_evidence()` below is what turns this on. It is written and
    tested against constructed reports, so the day a real corpus artifact is in
    reach the stage is COMPUTED -- no new code.
    """
    if not evidence or not evidence.get("measured"):
        why = (evidence or {}).get(
            "why", "no corpus report was supplied to this run")
        return S_NOT_MEASURED, "*** NOT MEASURED *** -- " + why
    return corpus_verdict(row, evidence)


def stage_ladder(row, evidence=None):
    """The COMPLETION ladder for one row: per-rung state, stage REACHED, anomalies.

    THE RULE, and it is not negotiable: a class lands on EXACTLY ONE stage, and
    that stage is the highest N for which every rung 1..N is `yes` or `n/a`. A
    rung that is `no` or `not measured` STOPS the climb -- including when a
    higher rung is satisfied.

    NOTHING ABOUT A SIGNATURE ENTERS THIS FUNCTION. Governance is a flag beside
    the stage (`governance_state`), never a rung, so a class with a working
    migrator can no longer report stage 0 because a sign-off was not findable.

    A higher rung satisfied over a stopped one is not a promotion and not an
    error to be smoothed away. It is a REAL CONDITION with a name in this
    repository -- `valid_interval` is "BUILT AHEAD OF THE DECISION" in
    CLAUDE.md's own words -- so it is reported as an anomaly, counted, and the
    class is named. Two kinds are counted separately because they mean opposite
    things:

      over_failed      a lower rung has POSITIVE evidence against it. A real
                       contradiction: something was built past a rung that is
                       measurably not met.
      over_unmeasured  a lower rung could not be read. Evidence exists above a
                       hole in the RECORD, which is a transcription job, not a
                       build job.

    TWO QUANTITIES COME OUT, AND THE SECOND ONE IS WHY:

      reached                              the strict, ordered stage. UNCHANGED
                                           by anything below -- a capped row is
                                           not promoted.
      highest_rung_satisfied_independently the highest rung that is `yes` at
                                           all, order ignored. It is NOT a
                                           stage, it is NOT progress, and it is
                                           deliberately named for what it is: a
                                           rung that holds somewhere above a
                                           rung that does not.

    Reporting only the first made "capped at 0 by an unread rung" and "nothing
    has happened here" print the same number, which is the defect this pair
    closes. `capped` is the flag that separates them and `nothing_satisfied`
    names the genuinely untouched rows -- the ones where no rung is `yes` at
    all, which is a real and much smaller set.
    """
    rungs = []
    try:
        for n, fn in ((1, _rung_consumed), (2, _rung_targets_built),
                      (3, _rung_emits_decided)):
            state, why = fn(row)
            rungs.append({"stage": n, "name": STAGE_NAMES[n],
                          "state": state, "why": why})
        state, why = _rung_corpus_proven(row, evidence)
        rungs.append({"stage": 4, "name": STAGE_NAMES[4],
                      "state": state, "why": why})
    except StageDataError as exc:
        return {
            "unclassifiable": True,
            "unclassifiable_why": str(exc),
            "reached": None,
            "reached_name": None,
            "blocked_by": None,
            "blocked_by_state": None,
            "ladder": rungs,
            "anomalies": [],
            "highest_rung_satisfied_independently": None,
            "capped": None,
            "nothing_built": None,
            "nothing_satisfied": None,
            "only_excused": None,
            "corpus_rung_state": S_NOT_MEASURED,
        }

    reached, blocked_by, blocked_state = 0, None, None
    for rung in rungs:
        if rung["state"] in _STAGE_PASSING:
            reached = rung["stage"]
        else:
            blocked_by, blocked_state = rung["stage"], rung["state"]
            break

    anomalies = []
    for rung in rungs:
        if rung["stage"] > reached and rung["state"] == S_YES:
            anomalies.append({
                "stage": rung["stage"],
                "stage_name": STAGE_NAMES[rung["stage"]],
                "satisfied_over": blocked_by,
                "satisfied_over_name": STAGE_NAMES[blocked_by] if blocked_by else None,
                "kind": ("over_failed" if blocked_state == S_NO
                         else "over_unmeasured"),
            })
    satisfied = [r["stage"] for r in rungs if r["state"] == S_YES]
    excused = [r["stage"] for r in rungs if r["state"] == S_NA]
    highest = max(satisfied) if satisfied else 0
    return {
        "unclassifiable": False,
        "unclassifiable_why": None,
        "reached": reached,
        "reached_name": STAGE_NAMES[reached],
        "blocked_by": blocked_by,
        "blocked_by_state": blocked_state,
        "ladder": rungs,
        "anomalies": anomalies,
        # NOT A STAGE. See the docstring: this is the highest rung that holds
        # on its own, and it exists only so a capped row can say so.
        "highest_rung_satisfied_independently": highest,
        "capped": highest > reached,
        # NOTHING IS BUILT for this class: no rung is `yes`.
        "nothing_built": not satisfied,
        # GENUINELY UNTOUCHED is stricter, and the difference is a real class
        # of row rather than a nicety. `epochid` is signed to DISSOLVE, so its
        # target and emission rungs are `n/a` -- the record says those rungs
        # cannot apply, which is a fact about the class and not silence about
        # it. Counting it as untouched would put a settled dissolution in the
        # same bucket as `base`, which nobody has looked at at all.
        "nothing_satisfied": not satisfied and not excused,
        "only_excused": bool(excused) and not satisfied,
        "corpus_rung_state": rungs[-1]["state"],
    }


# ---------------------------------------------------------------------------
# STAGE 5's INPUT. Written now so the stage is COMPUTED, not coded, on the day
# a corpus artifact is in reach.
# ---------------------------------------------------------------------------
#
# WHAT WOULD LIGHT IT UP: the corpus run reports DID-matlab's harness writes --
# `<corpus>-summary.json`, the same files `tools/census_digest.py` digests --
# reachable from this repo, either via `--corpus-reports DIR` or the
# `V_ETA_CORPUS_REPORTS` environment variable (os.pathsep-separated roots).
# The search is RECURSIVE over any number of roots, for the reason CLAUDE.md
# records: a one-level glob matched neither copy of the reports in corpus run
# #3, and the digest printed NO CORPUS REPORTS FOUND after an hour of green.
#
# WHAT IS READ OUT OF ONE REPORT, and which half of the claim each part carries:
#
#   source_census.by_class      PER-CLASS, keyed by the v1 SOURCE class -- the
#                               only block that can say "documents OF THIS CLASS
#                               were in the batch". Keys are normalised
#                               (lowercase, underscores stripped) exactly as
#                               did2.validate.sourceCensus normalises them; the
#                               pretty spelling returns nothing, which is the
#                               `demo_ndi` failure.
#   quarantine_count            CORPUS-LEVEL, and SOUND as an upper bound: a
#   fragment_count              corpus with 0 quarantined documents has 0 for
#   reference_integrity         every class in it. A corpus-level ZERO therefore
#     .orphan_count             proves the per-class zero; a corpus-level
#                               NON-zero does not disprove it, so a non-zero
#                               falls back to the per-class tables below and
#                               fails the rung if it cannot be attributed.
#   fragment_by_class           PER-TARGET-CLASS.
#   reference_integrity.orphans PER-TARGET-CLASS via `doc_class`.
#   silent_loss                 PER-TARGET-CLASS via `class_name`.
#     .empty_required_dependency
#
# A class with ZERO documents across every readable report is NOT proven and NOT
# refuted: `not measured`, because THE CORPORA ARE A SAMPLE OF DATASETS, NOT THE
# UNIVERSE. Reading "absent from the six corpora" as "clean" is the standing
# error this repository has paid for four times.
CORPUS_REPORT_GLOB = "*-summary.json"
CORPUS_REPORTS_ENV = "V_ETA_CORPUS_REPORTS"


def norm_class(name):
    """lowercase + underscores stripped -- did2.validate.sourceCensus's normClass."""
    return str(name).replace("_", "").lower()


def load_corpus_evidence(roots):
    """Read corpus run reports into the shape `corpus_verdict()` consumes.

    Returns a dict that ALWAYS carries `measured` and a denominator. When
    nothing was read it carries `why` -- and `why` is printed, so "found
    nothing" and "looked in the wrong place" are distinguishable from the
    output alone.
    """
    den = {"roots_named": list(roots), "roots_missing": [], "files_matched": 0,
           "files_unreadable": 0, "files_unparseable": 0,
           "reports_with_source_census": 0, "reports_read": 0}
    if not roots:
        return {"measured": False, "denominator": den,
                "why": ("no corpus report root was supplied (pass "
                        f"--corpus-reports DIR or set {CORPUS_REPORTS_ENV})")}
    paths = []
    for root in roots:
        if not os.path.isdir(root):
            den["roots_missing"].append(root)
            continue
        paths.extend(sorted(glob.glob(os.path.join(root, "**", CORPUS_REPORT_GLOB),
                                      recursive=True)))
    den["files_matched"] = len(paths)
    reports = []
    for p in paths:
        try:
            blob = Path(p).read_text()
        except OSError:
            den["files_unreadable"] += 1
            continue
        try:
            reports.append((os.path.basename(p), json.loads(blob)))
        except json.JSONDecodeError:
            den["files_unparseable"] += 1
    den["reports_read"] = len(reports)

    by_class, corpora = {}, []
    for name, rep in reports:
        if not isinstance(rep, dict):
            den["files_unparseable"] += 1
            continue
        sc = rep.get("source_census")
        corpus = str(rep.get("corpus") or name)
        entry = {
            "corpus": corpus,
            "quarantine_count": rep.get("quarantine_count"),
            "fragment_count": rep.get("fragment_count"),
            "fragment_by_class": {norm_class(k): v for k, v in
                                  (rep.get("fragment_by_class") or {}).items()},
            "orphan_count": None,
            "orphan_classes": set(),
            "empty_edge_classes": set(),
        }
        ri = rep.get("reference_integrity")
        if isinstance(ri, dict):
            entry["orphan_count"] = ri.get("orphan_count")
            for o in (ri.get("orphans") or []):
                if isinstance(o, dict) and o.get("doc_class"):
                    entry["orphan_classes"].add(norm_class(o["doc_class"]))
        sl = rep.get("silent_loss")
        if isinstance(sl, dict):
            erd = sl.get("empty_required_dependency")
            if isinstance(erd, dict):
                erd = [erd]
            for e in (erd or []):
                if isinstance(e, dict) and e.get("class_name"):
                    entry["empty_edge_classes"].add(norm_class(e["class_name"]))
        corpora.append(entry)
        if not isinstance(sc, dict) or "audit_failed" in sc \
                or not isinstance(sc.get("total_docs"), int) \
                or sc["total_docs"] <= 0:
            continue
        den["reports_with_source_census"] += 1
        for key, val in (sc.get("by_class") or {}).items():
            try:
                n = int(val)
            except (TypeError, ValueError):
                continue
            slot = by_class.setdefault(norm_class(key), {})
            slot[corpus] = slot.get(corpus, 0) + n

    if not den["reports_with_source_census"]:
        return {"measured": False, "denominator": den,
                "why": (f'{den["files_matched"]} file(s) matched '
                        f'{CORPUS_REPORT_GLOB}, {den["reports_read"]} parsed, and '
                        "NONE carried a readable v1 source census "
                        "(`source_census.by_class` with a non-zero `total_docs`)")}
    return {"measured": True, "denominator": den,
            "by_class": by_class, "corpora": corpora}


def corpus_verdict(row, ev):
    """Stage 5 for one row, given readable corpus evidence.

    The gate is the project's own: 0 quarantine + 0 orphans, plus no empty
    required edge and not a fragment. It is evaluated ONLY over corpora that
    actually held documents of this v1 class -- a corpus that never saw the
    class cannot vouch for it.
    """
    seen = ev["by_class"].get(norm_class(row["v1_class"]), {})
    total = sum(seen.values())
    if total <= 0:
        return S_NOT_MEASURED, (
            "*** NOT MEASURED *** -- 0 document(s) of this class across "
            f'{ev["denominator"]["reports_with_source_census"]} readable source '
            "census(es). THE CORPORA ARE A SAMPLE OF DATASETS, NOT THE UNIVERSE, "
            "so this is untested, not clean")
    # The classes a defect would be attributed to: what the migrator emits, plus
    # the decided targets, plus the source class itself (a guarded passthrough
    # validates under its own name).
    mine = {norm_class(t) for t in (row.get("targets") or [])}
    mine |= {norm_class(t) for t in (row.get("decided_targets") or [])}
    mine |= {norm_class(t) for t in (row.get("second_pass") or [])}
    mine.add(norm_class(row["v1_class"]))
    faults, checked, blind = [], [], []
    for c in ev["corpora"]:
        if not seen.get(c["corpus"]):
            continue
        # A COUNTER THAT IS ABSENT IS `not measured` FOR THIS CORPUS. IT IS NOT A
        # FAULT. This branch used to append the absence to `faults`, which made
        # any class present in a corpus whose report omits a counter come back
        # rung `no` -- "we proved it broken" for what is actually "nobody
        # looked". That is the `not measured` / `no` collapse this ladder exists
        # to prevent, arriving inside the ladder itself. It fired for real:
        # corpus run 31587869672 reported 10 FAILED classes, and every one named
        # the same cause -- testCorpusPRED is a hard 0-quarantine GATE rather
        # than a discovery run, so its report carries no `orphan_count` at all.
        # Nothing had failed.
        #
        # The corpus is recorded as BLIND and named in the verdict text instead.
        # Absence is not allowed to become a PASS either: a blind corpus never
        # enters `checked`, so it can never be the thing that proves a class, and
        # a class seen ONLY in blind corpora comes back `not measured`.
        #
        # Counters that ARE present are still read on a blind corpus. Suppressing
        # them would be the reassuring direction: a report missing `orphan_count`
        # can still record a quarantine attributable to this class, and that is a
        # real fault whatever else the report omits.
        missing = [k for k in ("quarantine_count", "fragment_count",
                               "orphan_count") if c.get(k) is None]
        if missing:
            blind.append(f'{c["corpus"]} (' + ", ".join("`%s`" % k for k in missing)
                         + " absent from the report)")
        else:
            checked.append(c["corpus"])
        for key, label in (("quarantine_count", "quarantined document(s)"),
                           ("fragment_count", "fragment(s)"),
                           ("orphan_count", "orphan edge(s)")):
            n = c.get(key)
            if n is None:
                continue
            if n:
                per_class = (c["fragment_by_class"] if key == "fragment_count"
                             else c["orphan_classes"] if key == "orphan_count"
                             else None)
                if per_class is None or (mine & set(per_class)):
                    faults.append(f'{c["corpus"]}: {n} {label} and the report '
                                  "does not clear this class of them")
        if mine & c["empty_edge_classes"]:
            faults.append(f'{c["corpus"]}: an empty required edge is recorded on '
                          + ", ".join(sorted(mine & c["empty_edge_classes"])))
    # The document count quoted by a verdict is the count over the corpora that
    # verdict actually rests on -- never the class total, which would let a
    # blind corpus's documents inflate a figure nothing inspected.
    n_checked = sum(n for c, n in seen.items() if c in checked)
    n_blind = total - n_checked
    blind_note = ("" if not blind else
                  "; NOT EVALUABLE in " + ", ".join(sorted(blind))
                  + f" -- {n_blind} document(s) there are UNINSPECTED, not clean")
    if faults:
        return S_NO, ("; ".join(faults)
                      + f' (over {total} document(s) in '
                      f'{len(checked) + len(blind)} corpus(es))')
    if not checked:
        return S_NOT_MEASURED, (
            f"*** NOT MEASURED *** -- {total} document(s) in "
            f'{len(blind)} corpus(es), and EVERY one of them is blind: '
            + ", ".join(sorted(blind))
            + ". No corpus that holds this class carries the counters the rung "
            "reads, so it is UNEVALUATED here -- neither clean nor failed")
    return S_YES, (f"{n_checked} document(s) across {len(checked)} corpus(es) "
                   f'({", ".join(checked)}) migrated with 0 quarantine, 0 '
                   "orphans, no empty required edge and no fragment" + blind_note)


def _stage_rollup(rows, evidence):
    """The rollup, DENOMINATOR FIRST. Reports what it could not place.

    IT LEADS WITH WHAT IS MEASURED. The first figure out of this function is
    rung 1 -- `a migrator CONSUMES it` -- because it is the only rung with an
    answer on every row, and because the question a reader actually arrives
    with is "how much is left". Leading with a capped stage histogram answered
    a different question (how much of our bookkeeping is findable) in a voice
    that sounded like the first one.
    """
    from collections import Counter
    # Keyed for the untouched-bucket detail below; the rows are the same
    # objects, read never written.
    by_name = {r["v1_class"]: r for r in rows}
    reached = Counter()
    per_stage_state = {n: Counter() for n in COMPLETION_RUNGS}
    anomalies, unclassifiable, with_na = [], [], []
    capped, untouched, excused_only = [], [], []
    highest = Counter()
    for r in rows:
        st = r["stage"]
        if st["unclassifiable"]:
            unclassifiable.append({"v1_class": r["v1_class"],
                                   "why": st["unclassifiable_why"]})
            continue
        reached[st["reached"]] += 1
        highest[st["highest_rung_satisfied_independently"]] += 1
        if st["capped"]:
            capped.append(r["v1_class"])
        if st["nothing_satisfied"]:
            untouched.append(r["v1_class"])
        if st["only_excused"]:
            excused_only.append(r["v1_class"])
        for rung in st["ladder"]:
            per_stage_state[rung["stage"]][rung["state"]] += 1
        if any(rung["state"] == S_NA for rung in st["ladder"]
               if rung["stage"] <= (st["reached"] or 0)):
            with_na.append(r["v1_class"])
        for a in st["anomalies"]:
            anomalies.append(dict(a, v1_class=r["v1_class"]))

    placed = [r for r in rows if not r["stage"]["unclassifiable"]]
    # THE UNDERSTATEMENT, NAMED RATHER THAN FIXED BY GUESSING. Rungs 2 and 3
    # both read `not measured` on every row whose `decided_targets` is empty:
    # there is no target to look for in the build and none to check an emission
    # against. That is the missing-transcription problem one level down from
    # governance, and it is NOT evidence that no target exists. The signature
    # join cannot repair it -- a family signature names a FAMILY, not a
    # per-class target list -- so the count it moves is zero, stated here rather
    # than left for a reader to assume either way.
    no_target_recorded = sorted(
        r["v1_class"] for r in placed
        if not (r.get("build_state") or {}).get("schema_targets_named"))
    return {
        # RULE 5, positionally: how many were classified and how many were not,
        # before any figure that depends on either.
        "classified": len(rows) - len(unclassifiable),
        "unclassifiable": len(unclassifiable),
        "unclassifiable_rows": unclassifiable,
        # THE HEADLINE, and it is deliberately the first content key: the one
        # rung with no unmeasured rows.
        "headline": {
            "rung": 1,
            "name": STAGE_NAMES[1],
            "denominator": len(placed),
            "yes": per_stage_state[1][S_YES],
            "no": per_stage_state[1][S_NO],
            "n/a": per_stage_state[1][S_NA],
            "not measured": per_stage_state[1][S_NOT_MEASURED],
        },
        "by_stage_reached": {str(n): reached.get(n, 0) for n in range(5)},
        "reached_with_an_n_a_in_the_chain": sorted(with_na),
        # Each rung on its own, ignoring the ladder order. The GAP between this
        # and `by_stage_reached` is the anomaly story, and printing only the
        # first would hide how much is built above an unreadable record.
        "per_stage_state_counts": {str(n): dict(c)
                                   for n, c in per_stage_state.items()},
        "per_stage_satisfied_independently": {
            str(n): per_stage_state[n][S_YES] for n in COMPLETION_RUNGS},
        # CAPPED vs UNTOUCHED. One bucket of "stage 0" made these identical,
        # and they are the difference between "evidence exists above a hole"
        # and "nothing has happened to this class".
        "capped": {
            "denominator": len(placed),
            "rows": len(capped),
            "row_names": sorted(capped),
            "highest_rung_satisfied_independently_histogram": {
                str(n): highest.get(n, 0) for n in range(5)},
            "genuinely_untouched": len(untouched),
            "genuinely_untouched_rows": sorted(untouched),
            # WHAT THE RECORD ALREADY SAYS ABOUT EACH UNTOUCHED CLASS.
            #
            # "no rung satisfied" is a statement about the LADDER, and it was
            # being read as a statement about the WORK. Every one of these rows
            # already carries a recorded `disposition` and `target_source`, and
            # for some of them no per-class migrator is expected AT ALL: a
            # PASSTHROUGH carries the document through unchanged, which is why
            # `projectvar` is documented as "PASSTHROUGH -- deliberately no
            # migrator". Reporting the bucket as a bare list of six names made a
            # settled passthrough and an unexamined class look identical, which
            # is the same collapse this file keeps having to undo one layer up.
            #
            # NOTHING HERE IS A DISPOSITION THIS TOOL DECIDES. The fields are
            # copied verbatim from the row, and `passthrough` is counted apart
            # only because it is a RECORDED, machine-set value with a defined
            # meaning -- not because this tool judges the class settled. A row
            # whose disposition is absent shows as `None` and stands out, which
            # is the point.
            "genuinely_untouched_detail": [
                {"v1_class": n,
                 "disposition": (by_name.get(n) or {}).get("disposition"),
                 "target_source": (by_name.get(n) or {}).get("target_source"),
                 "governance": ((by_name.get(n) or {}).get("governance")
                                or {}).get("state")}
                for n in sorted(untouched)],
            "genuinely_untouched_recorded_passthrough": sum(
                1 for n in untouched
                if (by_name.get(n) or {}).get("target_source") == "passthrough"),
            # Nothing is BUILT, but the record excuses the rungs above: a
            # signed dissolution. Counted apart from the untouched rows so a
            # settled class and an unexamined one are never one figure.
            "nothing_built_but_excused_by_a_signed_dissolution": len(excused_only),
            "nothing_built_but_excused_rows": sorted(excused_only),
        },
        "no_target_recorded": {
            "denominator": len(placed),
            "rows": len(no_target_recorded),
            "row_names": no_target_recorded,
            "rungs_it_makes_unreadable": [2, 3],
            "cause": ("`decided_targets` is empty, so rung 2 has nothing to look "
                      "for in the built set and rung 3 has nothing to check an "
                      "emission against. NOT evidence that no target exists"),
            "moved_by_the_signature_join": 0,
            "why_the_join_moves_none_of_them": (
                "a TEAM-SIGN-OFF line signs a FAMILY, not a per-class target "
                "list. The join can say a class is decided; it cannot say WHAT "
                "it becomes. Naming a target from it would be inventing one"),
        },
        "anomalies": {
            # BOTH counts, because they answer different questions and one
            # without the other misleads in opposite directions. A class stopped
            # at rung 1 with rungs 2, 3 and 4 all satisfied contributes THREE
            # anomalies and is ONE class; quoting only `total` inflates the
            # number of affected classes, quoting only `classes` hides how far
            # above the stopped rung the evidence reaches.
            "total": len(anomalies),
            "classes": len({a["v1_class"] for a in anomalies}),
            "by_kind": dict(Counter(a["kind"] for a in anomalies)),
            "by_stage": {str(n): sum(1 for a in anomalies if a["stage"] == n)
                         for n in COMPLETION_RUNGS},
            "rows": anomalies,
        },
        "corpus_rung": {
            "rung": 4,
            "measured": bool(evidence and evidence.get("measured")),
            "state": (S_NOT_MEASURED
                      if not (evidence and evidence.get("measured")) else "computed"),
            "why": (evidence or {}).get(
                "why", "no corpus report was supplied to this run"),
            "denominator": (evidence or {}).get("denominator"),
            "what_would_light_it_up": (
                "a DID-matlab corpus run's `<corpus>-summary.json` reports "
                f"reachable from this repo -- pass --corpus-reports DIR or set "
                f"{CORPUS_REPORTS_ENV}. Each report must carry "
                "`source_census.by_class` (per v1 SOURCE class) plus "
                "`quarantine_count`, `fragment_count`, `reference_integrity."
                "orphan_count` and `silent_loss.empty_required_dependency`."),
        },
        # GOVERNANCE, REPORTED BESIDE THE LADDER AND NEVER SUMMED WITH IT.
        # Nothing in this block caps a stage; it answers a different question,
        # for different people. `signed` here means A SIGNATURE IS FINDABLE,
        # not that anything was built.
        "governance": _governance_rollup(rows),
        "decision_claimed_but_unchecked": sorted(
            r["v1_class"] for r in rows
            if not r["stage"]["unclassifiable"]
            and (r.get("governance") or {}).get("state") == G_NOT_FOUND
            and r.get("decided_targets_source") == "curated_targets_file"),
    }


def _governance_rollup(rows):
    """Can we PROVE the team agreed, per class -- and where the gaps are.

    THREE OUTPUTS, and the second and third are the ones that drifted:
      * the per-state histogram over every row, denominator first;
      * the JOIN's own census: what it moved, and every unmoved row bucketed by
        CAUSE, so "decided but unrecorded" and "nobody has looked at this
        class" stop printing identically;
      * the SIGNATURE census: orphan tags and unsigned families, which are
        QUESTIONS FOR THE TEAM and are never paired up here. Mapping a
        signature onto a family it does not name would be recording a
        disposition (operating rule 4).
    """
    from collections import Counter
    states = Counter((r.get("governance") or {}).get("state") for r in rows)
    by_source = Counter()
    for r in rows:
        g = r.get("governance") or {}
        if g.get("state") != G_SIGNED:
            continue
        by_source["derived from a signed family" if r.get("decided_by_family")
                  and not (r.get("decided_signoff") or r.get("no_target_signoff"))
                  else "checked transcription on the row"] += 1
    all_idx, signed_idx = family_index(), signed_family_index()
    return {
        "denominator": len(rows),
        "by_state": {k: states.get(k, 0) for k in GOVERNANCE_STATES},
        "signed_by": dict(by_source),
        "join": signature_join_census(rows, all_idx, signed_idx),
        "census": status_board.signature_census(),
    }


def batch_pass_rollup(rows):
    """How much the batch-post-pass declarations moved, and which rows.

    DENOMINATOR FIRST AND UNCONDITIONALLY, and it is a THREE-PART one, because
    "the declarations said nothing" and "nobody read the declarations" and "a
    pass forgot to declare" are three different facts that a single count would
    fuse:

        measured        the chain was derived and the sources were read
        chain_size      how many passes were in reach
        missing         passes in the chain carrying NO declaration

    `credited_rung_1` / `credited_rung_3` name the rows this channel moved, and
    each row carries the pass that moved it -- so no number here can be read
    without seeing what produced it. `declared_matching_no_row` is the honest
    other side: a declared name that is not a did_v1 source class (every
    `session_*_reference`, for one) credits nothing and is REPORTED rather than
    dropped, because a silent non-match is how a typo becomes an absent credit.
    """
    s = BATCH_PASS_SCAN
    out = {
        "measured": s["measured"], "why": s["why"],
        "chain_size": s["chain_size"], "declared": sorted(s["declared"]),
        "missing": sorted(s["missing"]), "invalid": sorted(s["invalid"]),
        # AN INSTRUMENT FAULT, NOT A MIGRATION FACT. Non-empty means the scan's
        # summary lists disagree with its own per-pass verdicts, so no count
        # below can be trusted -- reported separately from `missing` for that
        # reason.
        "accounting_disagreement": sorted(s["accounting_disagreement"]),
        "denominator_rows": len(rows),
        "credited_rung_1": [], "credited_rung_3": [],
        "rows_naming_a_pass": [], "declared_matching_no_row": [],
        "unattributed_or_nothing": [],
    }
    matched = set()
    for r in rows:
        bs = r.get("build_state") or {}
        consumers = bs.get("batch_pass_consumers") or []
        if not consumers:
            continue
        matched.update(consumers)
        out["rows_naming_a_pass"].append(
            {"v1_class": r["v1_class"], "passes": list(consumers)})
        lad = {x["stage"]: x for x in (r.get("stage") or {}).get("ladder", [])}
        if (not bs.get("has_per_class_migrator")
                and not r.get("second_pass")
                and lad.get(1, {}).get("state") == S_YES):
            out["credited_rung_1"].append(
                {"v1_class": r["v1_class"], "passes": list(consumers),
                 "stage_reached": (r.get("stage") or {}).get("reached")})
        if bs.get("batch_pass_emits_decided_targets") and \
                lad.get(3, {}).get("state") == S_YES:
            out["credited_rung_3"].append(
                {"v1_class": r["v1_class"],
                 "emits": bs.get("batch_pass_emits") or {},
                 "decided_targets": list(r.get("decided_targets") or []),
                 "stage_reached": (r.get("stage") or {}).get("reached")})
        if not (bs.get("batch_pass_emits") or {}):
            out["unattributed_or_nothing"].append(
                {"v1_class": r["v1_class"], "passes": list(consumers)})
    for name, entries in sorted(s["index"].items()):
        # The RENAME spelling counts as a hit here for the same reason it
        # counts in `batch_pass_entries`: `acquisition_epoch` is the migrated
        # form of `element_epoch` and that row IS credited. Omitting it would
        # put the name in `declared_matching_no_row` -- "matched nothing" --
        # while the row it matched carries the pass in its own build_state.
        # The two accountings in this function exist to be COMPARED, so a
        # disagreement between them is worse than either being wrong alone.
        hit = (RENAME_OWNER.get(name) is not None
               or any(name in (r["v1_class"], r["veta_class"],
                               snake(r["v1_class"] or ""))
                      for r in rows))
        if not hit:
            out["declared_matching_no_row"].append(
                {"name": name, "passes": [e["pass"] for e in entries]})
    return out


def _print_batch_pass_rollup(bp):
    print("  BATCH POST-PASS DECLARATIONS (the third consumption channel)")
    print("    DENOMINATOR: %d ledger row(s); chain of %d pass(es), "
          "%d declared, %d MISSING A DECLARATION, %d INVALID"
          % (bp["denominator_rows"], bp["chain_size"], len(bp["declared"]),
             len(bp["missing"]), len(bp["invalid"])))
    if not bp["measured"]:
        print("    *** NOT MEASURED: " + str(bp["why"]))
        print("    Every rung below is therefore an UNDERSTATEMENT, not a "
              "measurement -- no row was credited by this channel.")
        return
    if bp.get("accounting_disagreement"):
        print("    *** INSTRUMENT FAULT -- the scan's declared/missing lists "
              "disagree with its own per-pass verdicts for: "
              + ", ".join(bp["accounting_disagreement"])
              + ". No count in this section can be trusted.")
    if bp["missing"]:
        print("    *** MISSING A DECLARATION: " + ", ".join(bp["missing"])
              + " -- a class consumed only by one of those is NOT measured. "
                "This is an absence, never an empty set.")
    if bp["invalid"]:
        print("    *** INVALID DECLARATION: " + ", ".join(bp["invalid"]))
    print("    rung 1 (`a migrator CONSUMES it`) credited via a batch pass: %d"
          % len(bp["credited_rung_1"]))
    for e in bp["credited_rung_1"]:
        print("      %-42s <- %s (now stage %s)"
              % (e["v1_class"], ", ".join(e["passes"]), e["stage_reached"]))
    print("    rung 3 (`the migrator emits THE DECIDED targets`) credited via "
          "a batch pass: %d" % len(bp["credited_rung_3"]))
    for e in bp["credited_rung_3"]:
        print("      %-42s <- %s (decided %s; now stage %s)"
              % (e["v1_class"],
                 "; ".join("%s -> %s" % (p, ", ".join(t))
                           for p, t in sorted(e["emits"].items())),
                 ", ".join(e["decided_targets"]), e["stage_reached"]))
    print("    rows naming a pass but credited NOTHING by it (an "
          "`UNATTRIBUTED` or `nothing` emission, or a rung already climbed): %d"
          % len(bp["unattributed_or_nothing"]))
    for e in bp["unattributed_or_nothing"]:
        print("      %-42s <- %s" % (e["v1_class"], ", ".join(e["passes"])))
    print("    declared names matching NO ledger row (not a did_v1 source "
          "class, so nothing to credit): %d" % len(bp["declared_matching_no_row"]))
    for e in bp["declared_matching_no_row"]:
        print("      %-42s <- %s" % (e["name"], ", ".join(e["passes"])))


def _print_emitted_by_rollup(rows):
    """Shape (1) of row 107, printed SEPARATELY and on purpose.

    This lived inside `_print_batch_pass_rollup` for ten minutes and was wrong
    there: that function RETURNS EARLY when the batch-pass scan is not measured
    (no DID-matlab checkout), and this credit does not depend on DID-matlab at
    all -- it is authored in the target map. So on a runner without the sibling
    the rung would have been credited in the artifact and invisible in the
    output, which is the asymmetry between what a tool does and what it says
    that this repository keeps paying for.
    """
    # A row is listed ONLY if its own migrator does not already emit the
    # decided target, so the count is the credit, not the population.
    eb = [r for r in rows if (r.get("build_state") or {}).get("emitted_by_migrator")]
    credited = [r for r in eb
                if (r["build_state"].get("emitted_by_emits_decided_targets"))]
    print("    rung 3 credited via ANOTHER CLASS'S MIGRATOR (superclass-only "
          "sources, authored in the target map with a citation): %d of %d "
          "row(s) carrying an `emitted_by`" % (len(credited), len(eb)))
    for r in credited:
        print("      %-42s <- %s -> %s (now stage %s)"
              % (r["v1_class"], r["build_state"]["emitted_by_migrator"],
                 ", ".join(r["build_state"]["emitted_by_targets"]),
                 r["stage"]["reached"]))
    for r in eb:
        if r not in credited:
            print("      %-42s <- %s, but it credits NOTHING (its own migrator "
                  "already emits the decided target, or the declared targets do "
                  "not cover it)"
                  % (r["v1_class"], r["build_state"]["emitted_by_migrator"]))


def _summary(rows):
    from collections import Counter
    return {
        "total": len(rows),
        "batch_pass": batch_pass_rollup(rows),
        "by_disposition": dict(Counter(r["disposition"] for r in rows)),
        "by_source": dict(Counter(r["source"] for r in rows)),
        "with_migrator": sum(1 for r in rows if r["migrator"]),
        "gaps": sum(1 for r in rows if r["gap"]),
        # RULE 5. The no-target census reports what it inspected, and reports
        # every bucket including the empty ones -- a missing key would make
        # "no gaps" and "never counted" identical, which is the whole defect
        # this field exists to close.
        "no_target": {
            "rows_naming_no_target": sum(
                1 for r in rows
                if not (r["targets"] or r["second_pass"] or r["decided_targets"])),
            "by_reason": {k: sum(1 for r in rows if r.get("no_target_reason") == k)
                          for k in (NO_TARGET_DISSOLVED, NO_TARGET_DISPUTED,
                                    NO_TARGET_PASSTHROUGH, NO_TARGET_UNRECORDED)},
            "target_gaps": sorted(r["v1_class"] for r in rows if r.get("target_gap")),
        },
        "decided_targets_from_signoff_transcription": sorted(
            r["v1_class"] for r in rows
            if r.get("decided_targets_source") == "signoff_transcription"),
        "stage_rollup": _stage_rollup(rows, CORPUS_SCAN),
    }


def _no_target_cell(r):
    """The target cell for a row that names no target class.

    Four different sentences, because the four states are four different facts.
    The one that matters is the last: a row with no target and no recorded
    reason says so, loudly, instead of borrowing the settled-sounding wording
    that used to be printed for all of them.
    """
    reason = r.get("no_target_reason")
    if reason == NO_TARGET_DISSOLVED:
        return "· **DISSOLVES** -- no target class, per `{}`".format((r.get("no_target_signoff") or {}).get("document"))
    if reason == NO_TARGET_DISPUTED:
        return "· ⚠ **DISPUTED** -- the record states two dispositions; see `{}`".format((r.get("no_target_signoff") or {}).get("document"))
    if reason == NO_TARGET_PASSTHROUGH:
        return "· **passes through as itself** by decision"
    return "· ⚠ **NO TARGET AND NO DISSOLUTION RECORDED** -- a gap, not a decision"


def _stage_cell(r):
    """One class's stage, plus the rung that stopped it and any anomaly.

    The stopping rung is printed BESIDE the number, always. A bare `stage 0`
    says only "not far"; `stage 0 (stops at 2, not measured)` says WHICH
    question is unanswered and whether it is unanswered or answered NO. The
    two are different facts and the cell must not merge them: `no` is a
    measurement, `not measured` is a hole.

    THE COUNT THAT USED TO BE QUOTED HERE IS GONE ON PURPOSE. This docstring
    said "for 94 of these rows the honest word is `not measured`" -- a number
    produced by the governance rung that no longer exists in this ladder, and
    the kind of figure CLAUDE.md has three separate corrections about. The
    live counts are in the rollup, which prints them.
    """
    st = r.get("stage") or {}
    if st.get("unclassifiable"):
        return "⚠ **UNCLASSIFIABLE** -- " + str(st.get("unclassifiable_why", "?"))
    cell = f'**{st.get("reached")}** {STAGE_NAMES.get(st.get("reached"), "?")}'
    if st.get("blocked_by"):
        cell += (f' · stops at {st["blocked_by"]}'
                 f' ({st.get("blocked_by_state")})')
    anom = st.get("anomalies") or []
    if anom:
        cell += (" · ⚠ but "
                 + "+".join(str(a["stage"]) for a in anom)
                 + " satisfied ("
                 + ("CONTRADICTION"
                    if any(a["kind"] == "over_failed" for a in anom)
                    else "above an unread rung") + ")")
    # BOTH QUANTITIES, IN THE CELL. A capped row says which rung holds above
    # its cap; a row where nothing holds says THAT, in words. Printing only the
    # stage made "capped at 0 by an unread rung" and "nothing has happened
    # here" the same number, which is what a reader was misled by.
    if st.get("capped"):
        cell += (" · highest rung satisfied on its own: "
                 f'{st["highest_rung_satisfied_independently"]} (NOT a stage)')
    elif st.get("nothing_satisfied"):
        cell += " · nothing above it satisfied either"
    elif st.get("only_excused"):
        cell += (" · nothing BUILT; the rungs above are `n/a` by a signed "
                 "dissolution")
    # WHICH KIND OF CODE CLIMBED IT (row 107). A rung reached through a DID
    # batch post-pass rather than through a migrator NAMED AFTER the class is
    # marked here, in the cell, so the reader of the artifact -- not only the
    # reader of the rollup on stdout -- can see the channel. Silently improving
    # a number is the failure this whole mechanism is a correction for.
    bs = r.get("build_state") or {}
    passes = bs.get("batch_pass_consumers") or []
    if passes and not bs.get("has_per_class_migrator") \
            and not (r.get("second_pass") or []):
        cell += (" · rung 1 via DID BATCH POST-PASS "
                 + ", ".join(f"`did2.convert.{p}`" for p in passes))
    if bs.get("batch_pass_emits_decided_targets"):
        cell += (" · rung 3 via DID BATCH POST-PASS "
                 + ", ".join(f"`did2.convert.{p}`"
                             for p in sorted(bs.get("batch_pass_emits") or {})))
    return cell


def _governance_cell(r):
    """The governance flag, printed as its own column. Never a stage."""
    g = r.get("governance") or {}
    state = g.get("state", G_NOT_FOUND)
    cite = g.get("signoff") or {}
    where = ""
    if cite.get("document"):
        where = " `{}`{}".format(cite["document"],
                                 ":" + str(cite["line"]) if cite.get("line") else "")
    if state == G_SIGNED:
        how = ("derived: family `{}`".format(cite.get("family"))
               if cite.get("family") else "transcribed")
        return f"**signed** ({how}){where}"
    if state == G_DISPUTED:
        return f"⚠ **DISPUTED**{where}"
    if state == G_UNSIGNED:
        return "⚠ **family UNSIGNED** -- " + ", ".join(
            "`" + f + "`" for f in (r.get("families_naming_this_class") or []))
    return "· no signature found (NOT `undecided`)"


def _stage_rollup_md(s):
    """The stage rollup table, DENOMINATOR FIRST and unconditionally.

    Two columns, not one, and the gap between them is the point. `classes AT
    this stage` is the strict ladder -- a class counts once, at the highest rung
    it reached with every rung below it satisfied. `rung satisfied on its own`
    ignores the order. A migration that has built far ahead of its written
    record shows up as a large second column over a small first one, which is
    exactly what it does today.
    """
    sr = s["stage_rollup"]
    reach, ind, states = (sr["by_stage_reached"],
                          sr["per_stage_satisfied_independently"],
                          sr["per_stage_state_counts"])
    hl, cap, ntr = sr["headline"], sr["capped"], sr["no_target_recorded"]
    out = [
        # THE HEADLINE FIRST, and it is a BUILD fact rather than a bookkeeping
        # one. Until 2026-08-12 this section opened with a stage histogram in
        # which 95 of 102 rows read `0` because a signature could not be
        # machine-found for them -- a number that answered "how findable is our
        # paperwork" while looking like an answer to "how much is left".
        "**How much is built.** DENOMINATOR: {d} of {t} row(s) classified, {u} "
        "UNCLASSIFIABLE{ulist}. **{yes} of {d} v1 source classes have something "
        "in the migration that CONSUMES them; {no} do not.** That rung has an "
        "answer on every row -- {nm} unmeasured -- which is why it leads. "
        "Governance is NOT part of this ladder: whether a sign-off can be found "
        "for a class is reported in its own column and never caps a build "
        "stage.".format(
            d=hl["denominator"], t=s["total"], u=sr["unclassifiable"],
            yes=hl["yes"], no=hl["no"], nm=hl["not measured"],
            ulist=(" (" + ", ".join("`" + u["v1_class"] + "`"
                                    for u in sr["unclassifiable_rows"]) + ")"
                   if sr["unclassifiable_rows"] else "")),
        "",
        ("**Completion ladder.** A class lands on EXACTLY ONE stage -- the "
        "highest rung for which every rung below it is satisfied -- so a rung "
        "that is `no` or `not measured` stops the climb even when a higher one "
        "holds. The stage is DERIVED from fields on the row; there is no list "
        "to hand-set. `not measured` is not `no`. Rungs 1 and 2 do not imply "
        "each other, so their order is a tie broken toward the FULLY MEASURED "
        "one -- putting the unread rung first would cap "
         f'{ntr["rows"]} rows below a fact this tool knows for certain.'),
        "",
        "| stage | what it means | classes AT this stage | rung satisfied on its own | yes / no / n/a / not measured |",
        "|---|---|---:|---:|---|",
        f'| 0 | {STAGE_NAMES[0]} | {reach["0"]} | {s["total"]} (by construction) | — |',
    ]
    for n in COMPLETION_RUNGS:
        st = states[str(n)]
        out.append(
            f'| {n} | {STAGE_NAMES[n]} | {reach[str(n)]} | {ind[str(n)]} | '
            f'{st.get(S_YES, 0)} / {st.get(S_NO, 0)} / {st.get(S_NA, 0)} / '
            f'{st.get(S_NOT_MEASURED, 0)} |')
    an = sr["anomalies"]
    out += [
        "",
        # CAPPED vs UNTOUCHED, IMMEDIATELY UNDER THE HISTOGRAM, because the
        # histogram is what made them indistinguishable.
        "**Capped, or untouched? DENOMINATOR: {d} classified row(s).** {c} are "
        "CAPPED -- a rung above their stage is satisfied while a lower one is "
        "unread or unmet -- and **{u} are GENUINELY UNTOUCHED: no rung is "
        "satisfied at all**{ulist}. A further {e} have nothing built while the "
        "rungs above them are `n/a` by a SIGNED DISSOLUTION{elist} -- counted "
        "apart, because a settled class and an unexamined one must never be one "
        "figure. The untouched number is the honest floor. "
        "`highest rung satisfied on its own` is NOT a stage and must never be "
        "quoted as one; it exists so a capped row can say which rung holds "
        "above its cap.".format(
            d=cap["denominator"], c=cap["rows"], u=cap["genuinely_untouched"],
            e=cap["nothing_built_but_excused_by_a_signed_dissolution"],
            ulist=(" (" + ", ".join("`" + c + "`"
                                    for c in cap["genuinely_untouched_rows"]) + ")"
                   if cap["genuinely_untouched_rows"] else ""),
            elist=(" (" + ", ".join("`" + c + "`"
                                    for c in cap["nothing_built_but_excused_rows"]) + ")"
                   if cap["nothing_built_but_excused_rows"] else "")),
        "",
        # THE UNDERSTATEMENT, NAMED. Asked for by the team rather than patched.
        "**{n} of {d} rows record NO TARGET CLASS**, which makes rungs 2 and 3 "
        "unreadable for them: {cause}. The signature join moves **{moved}** of "
        "them, and that zero is structural, not a shortfall -- {why}.".format(
            n=ntr["rows"], d=ntr["denominator"], cause=ntr["cause"],
            moved=ntr["moved_by_the_signature_join"],
            why=ntr["why_the_join_moves_none_of_them"]),
        "",
        ("**Stage 4 (CORPUS-PROVEN) is NOT MEASURED on all {t} rows** -- {why}. "
         "It is not `no` and it is not skipped: \"no corpus proved it\" and "
         "\"nobody looked\" are different facts, and this container has no "
         "MATLAB and cannot download run artifacts. It is the only honest "
         "\"done\" measure this ledger has. WHAT WOULD LIGHT IT UP: {light}"
         if not sr["corpus_rung"]["measured"] else
         "**Stage 4 (CORPUS-PROVEN) is COMPUTED** from the corpus reports "
         "supplied to this run.{why}{light}").format(
            t=s["total"],
            why=sr["corpus_rung"]["why"] if not sr["corpus_rung"]["measured"] else "",
            light=sr["corpus_rung"]["what_would_light_it_up"]
            if not sr["corpus_rung"]["measured"] else ""),
        "",
        "**Anomalies: {n} across {k} class(es).** A rung satisfied above the "
        "stage a class reached. "
        "Not smoothed away and not promoted -- `over_failed` ({f}) means a lower "
        "rung has POSITIVE evidence against it, a real contradiction; "
        "`over_unmeasured` ({u}) means evidence exists above a hole in the "
        "record, which is a transcription job and not a build job.{rows}".format(
            n=an["total"], k=an["classes"],
            f=an["by_kind"].get("over_failed", 0),
            u=an["by_kind"].get("over_unmeasured", 0),
            rows=("" if not an["by_kind"].get("over_failed") else
                  " CONTRADICTIONS: " + ", ".join(
                      "`" + a["v1_class"] + "` (stage " + str(a["stage"]) + ")"
                      for a in an["rows"] if a["kind"] == "over_failed") + ".")),
        "",
    ]
    if sr["decision_claimed_but_unchecked"]:
        out += [
            "**{n} row(s) claim a signed decision this tool cannot find** "
            "-- `V_eta_migration_targets.json` gives them `decided_targets`, "
            "which its own header calls \"a signed decision no migrator "
            "implements yet\", but no `TEAM-SIGN-OFF` line is quoted and checked "
            "for them and no signed family names them. This caps NOTHING (the "
            "completion ladder no longer reads governance); it is a hole in the "
            "RECORD: {lst}.".format(n=len(sr["decision_claimed_but_unchecked"]),
                                    lst=", ".join("`" + c + "`" for c in
                                                  sr["decision_claimed_but_unchecked"])),
            "",
        ]
    out += _governance_md(sr["governance"])
    return out


def _governance_md(g):
    """The governance flag + the signature gaps, as their own section.

    A FIRST-CLASS OUTPUT WITH A DENOMINATOR, which is the whole point: this
    drifted precisely because "nothing to see" and "nobody looked" printed the
    same way. Nothing here is summed with a stage and nothing here is resolved
    -- the orphan tags and the unsigned families are printed as QUESTIONS,
    because pairing a signature with a family it does not name is recording a
    disposition and operating rule 4 puts that with the team.

    HOW AN ORPHAN TAG GETS CREATED, since the count moved twice on 2026-08-17
    and the mechanism is not obvious from the output. `find_signoff_line` joins
    a signature to a family by EXACT TAG MATCH against the family NAME. So a
    signature written with a tag that reads naturally -- `[receptive field
    naming]`, `[stimulus -- visual_grating_manipulation reconciliation]` --
    reaches nothing at all unless a family of exactly that name exists in
    status_board.FAMILIES. Both of those were written that day and are
    COSMETIC: each sits in a document a signed family already cites, so the
    decision is on the record and only the join is missing.

    THE WAY TO AVOID ADDING A NINTH is to check, before writing a signature,
    whether an existing family already names the class -- and if one does, use
    ITS name as the tag. That is what the `[epoch]` signature added later the
    same day did, which is why the count stayed at 8 rather than becoming 9.
    A tag is not free-text; it is a foreign key.
    """
    j, c = g["join"], g["census"]
    st = g["by_state"]
    out = [
        "**Governance -- can we PROVE the team agreed? A FLAG, NOT A STAGE, and "
        "never added to one.** DENOMINATOR: {d} row(s) classified. "
        "**{signed} signed** ({by}), **{disputed} DISPUTED** (the record states "
        "two incompatible dispositions), **{unsigned} named by a family that "
        "carries no signature**, **{none} with no signature this tool can "
        "find**. That last number is the absence of a FINDABLE signature and "
        "not evidence that no decision exists -- operating rule 3.".format(
            d=g["denominator"], signed=st[G_SIGNED], disputed=st[G_DISPUTED],
            unsigned=st[G_UNSIGNED], none=st[G_NOT_FOUND],
            by=", ".join(f"{v} {k}" for k, v in sorted(g["signed_by"].items()))
            or "none"),
        "",
        "**The join, measured.** DENOMINATOR: {n} row(s) inspected; {m} reached "
        "by a signed decision family ({how}; {v1o} matched on the v1 name ONLY, "
        "{veo} on the V_eta name ONLY). It joins on the SIGNATURE, never "
        "on family membership -- an unsigned family names classes too, and "
        "promoting them would break operating rule 4 with a lookup. It joins on "
        "the row's OWN identity (its v1 name or its V_eta class, matched "
        "EXACTLY, in both namespaces, with no normalisation), never on what its "
        "migrator emits.".format(
            n=j["rows_inspected"], m=j["rows_matched_by_a_signed_family"],
            v1o=j["matched_on_v1_class_only"],
            veo=j["matched_on_veta_class_only"],
            how=", ".join(f"{v} on {k}" for k, v in sorted(j["matched_on"].items()))
            or "none"),
        "",
        "| rows with no findable signature | cause |",
        "|---:|---|",
    ]
    for cause, n in j["unmoved_by_cause"].items():
        out.append(f"| {n} | {cause} |")
    via = j["target_only_reached_via"]
    if via:
        top = ", ".join(f"`{k}` ×{v}" for k, v in list(via.items())[:4])
        out += [
            "",
            ("**Why the emitted-target rows are NOT joined.** Matching a row's "
             "emitted `targets` as well would move more rows, and most of them "
             f"would arrive through one class: {top}. A signature on the time "
             "model decides the time model; it says nothing about whether the "
             "disposition of the class that happens to emit a time anchor is "
             "settled. The reach is counted here instead of taken."),
        ]
    if j["spelling_near_misses"]:
        out += [
            "",
            "⚠ **{n} family member(s) match a ledger name ONLY after "
            "normalisation** (lowercase + strip underscores): {lst}. V_eta is "
            "snake_case and NDI is camelCase; these are NOT joined, because a "
            "join on a normalised name would make `demo_ndi` and `demoNDI` one "
            "class. Fix the spelling in `FAMILIES` or confirm they are "
            "different things.".format(
                n=len(j["spelling_near_misses"]),
                lst=", ".join("`{}` ~ `{}`".format(m["family_member"],
                                                   m["ledger_name"])
                              for m in j["spelling_near_misses"])),
        ]
    if j["conflicting_claims"]:
        out += [
            "",
            "⚠ **{n} row(s) claimed by TWO signed families**: {lst}. One class, "
            "two decisions -- for the team.".format(
                n=len(j["conflicting_claims"]),
                lst=", ".join("`" + c + "`" for c in j["conflicting_claims"])),
        ]
    out += [
        "",
        "**Where the signatures are. DENOMINATOR: {d} plan document(s) read "
        "({x} generated artifact(s) excluded, carrying {xm} marker(s) between "
        "them -- a generated file quotes signatures, it does not hold them); "
        "{a} sign-off line(s) accepted, {r} rejected.** {ft} of {fa} decision "
        "families are signed.".format(
            d=c["documents_read"], x=len(c["documents_excluded_as_generated"]),
            xm=c["signoff_markers_inside_excluded_documents"],
            a=c["accepted_lines"], r=len(c["rejected_lines"]),
            ft=len(c["families_signed"]), fa=c["families_total"]),
        "",
    ]
    # THE TWO DIRECTIONS OF THE MISMATCH, AS QUESTIONS. Never paired.
    if c["orphan_tags"]:
        out += [
            "**QUESTION FOR THE TEAM -- {n} signed tag(s) name no decision "
            "family**, so the signature reaches nothing this tool joins: {lst}. "
            "Whether each is a family that needs renaming, a family that needs "
            "creating, or a decision that belongs to no family is a TEAM call; "
            "mapping one onto a family it does not name would be recording a "
            "disposition.".format(
                n=len(c["orphan_tags"]),
                lst="; ".join(
                    "`{}` ({}:{})".format(t, v[0]["document"], v[0]["line"])
                    for t, v in c["orphan_tags"].items())),
            "",
        ]
    if c["families_unsigned"]:
        out += [
            "**QUESTION FOR THE TEAM -- {n} decision family(ies) carry no "
            "signature this tool will honour**: {lst}. Their classes read "
            "`family UNSIGNED` above, which is a missing SIGNATURE and not a "
            "missing model.".format(
                n=len(c["families_unsigned"]),
                lst=", ".join("`" + f + "`" for f in c["families_unsigned"])),
            "",
        ]
    tagged_rejects = [r for r in c["rejected_lines"] if r["tag"]]
    if tagged_rejects:
        out += [
            "⚠ **{n} rejected line(s) carry a family tag and read as a real "
            "signature.** The scanner's placeholder guard rejects a line that "
            "carries one of the TEMPLATE's own unfilled slots (`<family>`, "
            "`<who/when>`, `<what was decided>`): {lst}. The direction is safe "
            "(less signed than reality, never more) and the blast radius is "
            "printed beside each -- a rejected line in a document NO family "
            "cites changes nothing today. NARROWED 2026-08-13: this guard used "
            "to fire on a paired `<...>` ANYWHERE after the marker, which "
            "rejected a real dated decision whose text names a class-name "
            "pattern (`<modality>_observation`) and left the class it settles "
            "reading as unsigned. Changing which lines count as a decision is "
            "a team call; this narrowing restored one the guard should never "
            "have taken.".format(
                n=len(tagged_rejects),
                lst="; ".join(
                    "`{}` ({}:{}, cited by {})".format(
                        r["tag"], r["document"], r["line"],
                        ", ".join(r["document_cited_by_families"]) or "NO family")
                    for r in tagged_rejects)),
            "",
        ]
    return out


def _build_state_clause(r):
    """`SCHEMA: ... MIGRATOR: ...` -- never one undifferentiated verdict.

    The authored `flags` prose says "DECIDED AND SIGNED, BUILD NOT DONE" on
    eight rows. For `app` that is half true and misleading in the direction
    that costs work: `software` IS built and shipping, and only the migrator is
    outstanding, so a reader acting on the sentence re-authors existing schema.
    This clause is DERIVED from the built index and the emitted-target list, so
    it cannot drift from either.
    """
    bs = r.get("build_state") or {}
    if not bs.get("schema_targets_named"):
        return None
    built, missing = bs["schema_targets_built"], bs["schema_targets_missing"]
    schema = (f'SCHEMA: {len(built)} of {bs["schema_targets_named"]} decided target class(es) present in the built set')
    if built:
        schema += " (" + ", ".join(f"`{t}`" for t in built) + ")"
    if missing:
        schema += "; NOT built: " + ", ".join(f"`{t}`" for t in missing)
    # THREE STATES, NOT TWO. Until row 107 this clause said "does NOT emit them
    # yet" for a class whose emission is done by a BATCH POST-PASS -- and the
    # stage cell beside it now reads 3, so the artifact contradicted itself in
    # its own row. The batch-pass case is spelled out, with the pass named, so
    # a reader can see WHICH kind of code emits the decided target.
    if bs.get("migrator_emits_decided_targets"):
        migr = "MIGRATOR: emits them today"
    elif bs.get("batch_pass_emits_decided_targets"):
        em = bs.get("batch_pass_emits") or {}
        migr = ("MIGRATOR: the per-class migrator does NOT emit them; the DID "
                "BATCH POST-PASS(es) "
                + "; ".join(f"`did2.convert.{p}` -> "
                            + ", ".join(f"`{t}`" for t in sorted(ts))
                            for p, ts in sorted(em.items()))
                + " DECLARE the emission")
    else:
        migr = "MIGRATOR: does NOT emit them yet"
    return "⚑ " + schema + ". " + migr + "."


def write_ledger(veta, v1, rows):
    s = _summary(rows)
    lines = [
        "# V_eta migration coverage ledger",
        "",
        "*Generated by `tools/coverage.py` -- do NOT hand-edit; re-run after a schema "
        "or migrator change. " + LEDGER_BLURB + " Each row shows the V_eta document "
        "class(es) the v1 class MIGRATES INTO (from the curated `V_eta_migration_targets."
        "json`), its disposition, and its writer.*",
        "",
        f"**{s['total']} v1 source classes** ({s['by_source'].get('ndi', 0)} NDI/main "
        f"+ {s['by_source'].get('app', 0)} vhlab app) | by V_eta disposition: "
        + ", ".join(f"{k}={v}" for k, v in sorted(s["by_disposition"].items()))
        + f" | {s['with_migrator']} have a bespoke migrator"
        + (f" | ⚠ {s['gaps']} UNMAPPED (no V_eta class, no migrator)" if s["gaps"] else "")
        + ".",
        "",
        # THE NO-TARGET CENSUS, UNCONDITIONALLY AND WITH ITS DENOMINATOR. It
        # prints every bucket including the zeroes: an omitted line would make
        # "none of these" and "not counted" the same output, and a blank target
        # cell reading as settled is precisely the defect being closed.
        "**No-target census.** DENOMINATOR: {n} rows inspected; {b} name no target "
        "class of any kind. Across ALL {n} rows the recorded no-target dispositions "
        "are **{dis} dissolved** (signed, final -- note a dissolution is a fact "
        "about the DECISION, so a row can carry one while its migrator still emits "
        "the class today), **{disp} DISPUTED**, **{pt} signed passthroughs** whose "
        "decided target is the class itself, and **{gap} with NO TARGET AND NO "
        "DISSOLUTION RECORDED**{gaplist}. Only the last is a missing record; the "
        "blank rows not otherwise accounted for are test/demo scaffolding or "
        "pre-V_zeta dissolutions, already labelled in the disposition column. A "
        "blank cell is no longer expressible: a row with no target must carry a "
        "transcribed sign-off saying so, or it renders as a gap.".format(
            n=s["total"], b=s["no_target"]["rows_naming_no_target"],
            dis=s["no_target"]["by_reason"][NO_TARGET_DISSOLVED],
            disp=s["no_target"]["by_reason"][NO_TARGET_DISPUTED],
            pt=s["no_target"]["by_reason"][NO_TARGET_PASSTHROUGH],
            gap=s["no_target"]["by_reason"][NO_TARGET_UNRECORDED],
            gaplist=(" (" + ", ".join(f"`{c}`"
                                      for c in s["no_target"]["target_gaps"]) + ")"
                     if s["no_target"]["target_gaps"] else "")),
        "",
    ]
    lines += _stage_rollup_md(s)
    lines += [
        # TWO COLUMNS, TWO QUANTITIES, NEVER SUMMED. `build stage` is what
        # exists for this class; `governance` is whether the team's agreement
        # can be found. A single column merging them is the shape that reported
        # 95 of 102 classes as "no progress".
        "| v1 class | build stage | governance | → V_eta target(s) | what happens to it | disposition | source |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        chips = ["`" + t + "`" for t in r["targets"]]
        chips += ["`" + t + "`*" for t in r["second_pass"]]  # * = NDI second pass
        # ORDER MATTERS, and getting it wrong is silent. `decided` rows have NO
        # chips by construction, so this must be tested BEFORE the empty case --
        # placed after it, the branch below never fires and every signed-unbuilt
        # row prints "—". Caught by reading the rendered table, not the code.
        # THE REASON OUTRANKS THE BRANCH, and this order is not cosmetic.
        # `imageCollection` has no curated entry at all, so it never reached the
        # `decided` branch and rendered as a bare "—" while the census counted
        # it as a gap: the artifact and its own summary line disagreed, and the
        # dash was the reassuring half. A row carrying a recorded reason and no
        # target of any kind now states that reason first, whatever produced it.
        if (r.get("no_target_reason")
                and not (r["targets"] or r["second_pass"] or r["decided_targets"])):
            tgt = _no_target_cell(r)
        elif r.get("target_source") == "decided":
            dt = r.get("decided_targets") or []
            # THE `else` BRANCH USED TO READ "· **will dissolve / be deleted**
            # (no target by design)" -- an assertion produced by an empty list.
            # It was printed for seven rows and it was wrong for `filter`,
            # whose signed model makes it a `frequency_filter` document. A
            # dissolution now has to be SAID (NO_TARGET_BY_DECISION, with the
            # sign-off quoted); anything else renders as the gap it is.
            if r.get("no_target_reason") == NO_TARGET_PASSTHROUGH:
                # "will become `projectvar`" was the previous rendering of a
                # class whose decided target is ITSELF, and it reads as pending
                # work. It is the opposite: the decision is that nothing
                # happens to it, and that decision is made and signed.
                tgt = _no_target_cell(r)
            else:
                tgt = ("· **will become** " + " + ".join("`" + t + "`" for t in dt)
                       # Present tense here read as ALREADY DONE while the sibling
                       # branch above says "will become" -- and `ngrid` is signed to
                       # dissolve but CANNOT be (two consumers remain). The status
                       # column carries completion; the tense must not contradict it.
                       if dt else _no_target_cell(r))
        elif not chips:
            tgt = "⚠ **unmapped**" if r["gap"] else "—"
        elif r.get("target_source") == "uncurated":
            # A migrator runs but nothing records what it emits. Distinct from
            # both a measured target and a passthrough, and actionable: it is a
            # missing row in V_eta_migration_targets.json.
            tgt = "⚠ migrator runs, **output unrecorded**"
        elif r.get("target_source") == "passthrough":
            # NOT rendered as a migration. No migrator emits this; the document
            # simply reaches validation under the same-name class. Fifteen of
            # these carry a signed decision naming a DIFFERENT target, so
            # printing `X -> X` here read as a contradiction of the plan.
            tgt = "· passes through as `{}` (no migrator; target unrecorded)".format(r["targets"][0])
        else:
            tgt = " + ".join(chips)
            if r["carried"]:
                tgt += " · on " + ", ".join("`" + c + "`" for c in r["carried"])
            # A row that EMITS something today can still carry a signed target
            # it does not emit yet, and until now that never reached the table:
            # only the `decided` branch above printed `decided_targets`, so
            # `epochfiles_ingested -> ingestion_manifest` and the four
            # `method_parameters` folds were invisible in the rendered ledger
            # while sitting in the JSON. Emitted and decided are different
            # voices, printed as different clauses, never merged.
            dt = [t for t in (r.get("decided_targets") or []) if t not in r["targets"]]
            if dt:
                tgt += " · **will become** " + " + ".join("`" + t + "`" for t in dt)
            # A SIGNED DISSOLUTION ON A ROW THAT STILL EMITS ITSELF. Emitting
            # the source class back out is what a guarded passthrough does; it
            # is TODAY, and it must not hide a decision that the class goes
            # away. `binaryseries_parameters` is exactly this shape, and
            # rendering only the emitted chip made a retired class read as a
            # settled 1:1 migration.
            elif r.get("no_target_reason") == NO_TARGET_DISSOLVED:
                tgt += " · **but is SIGNED TO DISSOLVE** -- no target class"
            elif r.get("no_target_reason") == NO_TARGET_DISPUTED:
                tgt += " · ⚠ **DISPUTED disposition**"
        # THE ACCOUNT, IN THE TABLE. This footer used to say "see
        # V_eta_migration_targets.json for the per-class `how`" -- which is to say,
        # the one field that answers the question was in a different file, behind
        # a git checkout. That is exactly why the question could not be answered
        # for a team. Pipes and newlines are escaped so a long sentence cannot
        # break the table.
        acct = (r.get("how") or "").strip()
        if r.get("no_target_account"):
            acct = (acct + " " if acct else "") + r["no_target_account"].strip()
        if r.get("target_flags"):
            acct = (acct + " " if acct else "") + "⚠ " + r["target_flags"].strip()
        # LAST, DELIBERATELY. It is the measured half, and it must be readable
        # as a correction to whatever the authored prose above it claimed.
        _bsc = _build_state_clause(r)
        if _bsc:
            acct = (acct + " " if acct else "") + _bsc
        acct = acct.replace("|", "\\|").replace("\n", " ") or "—"
        lines.append(
            f"| `{r['v1_class']}` | {_stage_cell(r)} | {_governance_cell(r)} "
            f"| {tgt} | {acct} "
            f"| {r['disposition']} | {r['source']} |")
    lines.append("")
    lines.append("*`class`\\* = minted in the NDI second pass. "
                 "\"on `subject`\" = the pre-existing class the statements attach to. "
                 "**will become** = a signed decision that no migrator implements yet. "
                 "The `what happens to it` column is the authored per-class account; "
                 "`⚠` prefixes its caveat; `⚑` prefixes the DERIVED build state, "
                 "which states the SCHEMA half and the MIGRATOR half separately and "
                 "may correct an authored `BUILD NOT DONE` beside it.*")
    lines.append("")
    Path(LEDGER).write_text("\n".join(lines))


def write_ledger_json(rows):
    """Machine-readable ledger for the web viewer (Coverage panel)."""
    doc = {
        "title": "V_eta migration coverage ledger",
        "description": LEDGER_BLURB.replace(" -- ", " — "),
        "summary": _summary(rows),
        "rows": rows,
    }
    Path(LEDGER_JSON).write_text(json.dumps(doc, indent=2) + "\n")


def _print_stage_rollup(s):
    """The stage histogram on the console, denominator first.

    `gates.py` matches a HEADLINE COUNT per step and fails a step that exits 0
    while printing none, so this line is also the step's evidence that the
    classifier ran at all.
    """
    sr = s["stage_rollup"]
    hl, cap, ntr, gov = (sr["headline"], sr["capped"],
                         sr["no_target_recorded"], sr["governance"])
    # LEADS WITH THE MEASURED RUNG. `gates.py` matches the first headline count
    # per step, so this line is also what CI sees -- and what it should see is
    # the build fact, not the bookkeeping one.
    print("  build ladder: DENOMINATOR %d row(s) classified, %d UNCLASSIFIABLE%s"
          % (sr["classified"], sr["unclassifiable"],
             ("" if not sr["unclassifiable_rows"] else
              " (" + ", ".join(u["v1_class"]
                               for u in sr["unclassifiable_rows"]) + ")")))
    print("      rung 1 %-42s %d yes / %d no / %d n/a / %d NOT MEASURED  <- fully measured, so it leads"
          % (hl["name"], hl["yes"], hl["no"], hl["n/a"], hl["not measured"]))
    for n in range(5):
        print("      stage %d  %-46s %4d at this stage | %s satisfied on its own"
              % (n, STAGE_NAMES[n], sr["by_stage_reached"][str(n)],
                 (str(s["total"]) + " (by construction)") if n == 0
                 else str(sr["per_stage_satisfied_independently"][str(n)])))
    print("      capped by a lower rung: %d | GENUINELY UNTOUCHED (no rung satisfied at all): %d%s"
          % (cap["rows"], cap["genuinely_untouched"],
             (" (" + ", ".join(cap["genuinely_untouched_rows"]) + ")")
             if cap["genuinely_untouched_rows"] else ""))
    # The untouched names alone read as six units of unbuilt work. Every one
    # carries a recorded disposition, and for a PASSTHROUGH no per-class
    # migrator is expected at all -- so the reason is printed beside the name
    # rather than left for a reader to look up six times.
    if cap.get("genuinely_untouched_detail"):
        print("        -- of those, %d are a RECORDED PASSTHROUGH (a passthrough "
              "carries the document through unchanged, so no per-class migrator "
              "is expected):" % cap["genuinely_untouched_recorded_passthrough"])
        for u in cap["genuinely_untouched_detail"]:
            print("             %-22s disposition=%-32s target_source=%s"
                  % (u["v1_class"], u["disposition"], u["target_source"]))
    print("      nothing built but EXCUSED by a signed dissolution: %d%s"
          % (cap["nothing_built_but_excused_by_a_signed_dissolution"],
             (" (" + ", ".join(cap["nothing_built_but_excused_rows"]) + ")")
             if cap["nothing_built_but_excused_rows"] else ""))
    print("      no target recorded on %d row(s) -- rungs 2+3 unreadable for them, "
          "and the signature join moves %d of them (a signature names a FAMILY, "
          "not a target)" % (ntr["rows"], ntr["moved_by_the_signature_join"]))
    an = sr["anomalies"]
    print("      anomalies: %d across %d class(es) (%d over a FAILED rung, "
          "%d over an UNMEASURED rung)"
          % (an["total"], an["classes"], an["by_kind"].get("over_failed", 0),
             an["by_kind"].get("over_unmeasured", 0)))
    print("      stage 4: *** NOT MEASURED *** -- " + sr["corpus_rung"]["why"]
          if not sr["corpus_rung"]["measured"] else
          "      stage 4: computed from corpus reports")
    # GOVERNANCE, PRINTED SEPARATELY AND AFTER. It is not part of the ladder and
    # it is not summed with it.
    gst, gj, gc = gov["by_state"], gov["join"], gov["census"]
    print("  governance (a FLAG, never a stage): DENOMINATOR %d row(s) -- "
          "%d signed, %d DISPUTED, %d family UNSIGNED, %d no signature found"
          % (gov["denominator"], gst[G_SIGNED], gst[G_DISPUTED],
             gst[G_UNSIGNED], gst[G_NOT_FOUND]))
    print("      signature join: %d of %d row(s) reached by a SIGNED family "
          "(%d matched on the v1 name ONLY, %d on the V_eta name ONLY)"
          % (gj["rows_matched_by_a_signed_family"], gj["rows_inspected"],
             gj["matched_on_v1_class_only"], gj["matched_on_veta_class_only"]))
    for cause, n in gj["unmoved_by_cause"].items():
        print("        %4d  %s" % (n, cause))
    print("      signatures: %d document(s) read, %d accepted line(s), "
          "%d rejected; %d of %d families signed"
          % (gc["documents_read"], gc["accepted_lines"],
             len(gc["rejected_lines"]), len(gc["families_signed"]),
             gc["families_total"]))
    if gc["orphan_tags"]:
        print("      *** %d SIGNED TAG(S) NAME NO FAMILY (a question for the "
              "team, not a mapping to make here): %s"
              % (len(gc["orphan_tags"]),
                 ", ".join("%s (%s:%d)" % (t, v[0]["document"], v[0]["line"])
                           for t, v in gc["orphan_tags"].items())))
    if gc["families_unsigned"]:
        print("      *** %d FAMILY(IES) CARRY NO SIGNATURE: %s"
              % (len(gc["families_unsigned"]), ", ".join(gc["families_unsigned"])))
    for rj in gc["rejected_lines"]:
        if rj["tag"]:
            print("      *** REJECTED sign-off line with a family tag: [%s] "
                  "%s:%d -- %s (document cited by: %s)"
                  % (rj["tag"], rj["document"], rj["line"], rj["why"],
                     ", ".join(rj["document_cited_by_families"]) or "NO family"))
    if gj["spelling_near_misses"]:
        print("      *** %d family member(s) match a ledger name ONLY after "
              "normalisation: %s"
              % (len(gj["spelling_near_misses"]),
                 ", ".join("%s ~ %s" % (m["family_member"], m["ledger_name"])
                           for m in gj["spelling_near_misses"])))


def _corpus_roots(argv):
    """Corpus report roots from --corpus-reports and the environment.

    Both, not one: a CI job sets the variable, a human passes the flag, and a
    tool that reads only one of them reports NOT MEASURED at the exact moment
    the evidence is on disk.
    """
    roots = []
    for i, a in enumerate(argv):
        if a == "--corpus-reports" and i + 1 < len(argv):
            roots.append(argv[i + 1])
        elif a.startswith("--corpus-reports="):
            roots.append(a.split("=", 1)[1])
    env = os.environ.get(CORPUS_REPORTS_ENV)
    if env:
        roots.extend(p for p in env.split(os.pathsep) if p)
    return roots


def main():
    check_only = "--check" in sys.argv
    # RULE 5, BEFORE ANYTHING ELSE: this tool's universe is two sibling
    # checkouts, and until 2026-08-12 it never said whether it had them. On a
    # GitHub runner `/home/user` does not exist and did-schema sits at
    # $GITHUB_WORKSPACE/did-schema, so `find_repo`'s third candidate for
    # DID-matlab is $GITHUB_WORKSPACE/DID-matlab -- which is not the checkout,
    # because the WORKSPACE DIRECTORY IS the DID-matlab checkout. So DIDM came
    # back None, the migrator scan was skipped whole (`migrator_files` returns
    # an empty set), the 11 vhlab app classes that have no NDI template were
    # dropped, and the tool wrote a 91-row ledger reporting `10 yes / 81 no` on
    # rung 1 -- against 102 rows and `86 yes / 16 no` locally. It exited 0 and
    # said nothing. A tool whose answer depends on a path it silently failed to
    # find must announce the path first.
    print("DENOMINATOR: sibling checkouts this ledger is derived from -- "
          + ", ".join(f"{n}: {p or '*** NOT FOUND'}"
                      for n, p in (("NDI-matlab", NDI), ("DID-matlab", DIDM))))
    if not DIDM:
        print("  *** DID-matlab NOT FOUND: the migrator scan cannot run, so "
              "rung 1 reads `no` for every class and app classes with no NDI "
              "template are absent from the ledger entirely. Set DID_MATLAB.")
    if not NDI:
        print("  *** NDI-matlab NOT FOUND: the did_v1 template universe is "
              "unreadable. Set NDI_MATLAB.")
    # FIRST, UNCONDITIONALLY, AND FATAL. Every transcribed sign-off is
    # re-read from the document it cites before a single row is built, so a
    # citation that has gone stale (a plan reworded, a document renamed) stops
    # the ledger instead of being carried forward as a quotation nobody
    # rechecked. `--check` runs it too: a stale citation is a CI failure.
    cite_lines, cite_fails = check_decision_citations()
    for ln in cite_lines:
        print(ln)
    if cite_fails:
        for f in cite_fails:
            print("  FAIL: " + f)
        sys.exit(f'coverage: {len(cite_fails)} transcribed decision(s) no longer match the document they cite.')

    veta = veta_index()
    emitted = emitted_classes()
    new, ack = guardrail(veta, emitted)

    print(f"guardrail: {len(emitted)} emitted class_names checked against V_eta schema")
    for c, f in ack:
        print(f"  [known] {c:30} <- {', '.join(f)}")
    if new:
        print("  NEW VIOLATIONS (emitted but not in V_eta schema -- revived/invented):")
        for c, f in new:
            print(f"    {c:30} <- {', '.join(f)}")
    else:
        print("  OK: no new revived/invented classes.")

    if check_only:
        sys.exit(1 if new else 0)

    # STAGE 5's INPUT, read before the rows are built so the stage is computed
    # rather than back-filled. Absent on this container and in CI today; the
    # rollup says so in those words rather than defaulting to "not reached".
    CORPUS_SCAN.clear()
    CORPUS_SCAN.update(load_corpus_evidence(_corpus_roots(sys.argv)))

    veta, v1, rows = build_ledger()
    # THE LEFT-HAND SIDE'S OWN DENOMINATORS, printed before the ledger line that
    # quotes `N v1 classes`. Both reads below feed that number and both used to
    # swallow their failures, so `102 v1 classes` could have read 101 with
    # nothing to compare it against.
    ts = TEMPLATE_SCAN
    print(f'  DENOMINATOR: NDI templates from {ts["source"]} -- '
          f'{ts["candidates"]} candidate(s), {ts["classes"]} class(es) captured, '
          f'{ts["unreadable"]} UNREADABLE, {ts["unparseable"]} unparseable, '
          f'{ts["not_a_document_class"]} not a document class')
    if ts["refs_tried"]:
        print("  *** FELL BACK: " + "; ".join(ts["refs_tried"])
              + f' -- read {ts["source"]} instead. A lagging NDI branch or the '
                "working tree ships FEWER classes than origin/main.")
    if ts["unreadable"] or ts["unparseable"]:
        print("  *** SOME TEMPLATES WERE NOT CAPTURED. The v1 universe below is "
              "over the survivors.")
    tm = TARGETS_SCAN
    print("  DENOMINATOR: curated target map -- "
          + (f'{tm["rows"]} class row(s) read from '
             f'{os.path.basename(TARGETS)}' if tm["read"]
             else f'NOT READ ({tm["why"]})'))
    if not tm["read"]:
        print("  *** EVERY ROW'S `targets` COLUMN IS EMPTY BECAUSE OF THAT, not "
              "because no migrator emits anything.")
    if v1:
        write_ledger(veta, v1, rows)
        write_ledger_json(rows)
        s = _summary(rows)
        print(f"ledger: wrote {os.path.relpath(LEDGER, SCHEMA_ROOT)} + "
              f"{os.path.relpath(LEDGER_JSON, SCHEMA_ROOT)} ({len(v1)} v1 classes"
              + (f", {s['gaps']} UNMAPPED" if s["gaps"] else "") + ")")
        nt = s["no_target"]
        print('  no-target census: DENOMINATOR %d rows, %d naming no target -- %d dissolved, %d DISPUTED, %d GAP%s (+%d self-target passthroughs, which do name a target)'
              % (s["total"], nt["rows_naming_no_target"],
                 nt["by_reason"][NO_TARGET_DISSOLVED],
                 nt["by_reason"][NO_TARGET_DISPUTED],
                 nt["by_reason"][NO_TARGET_UNRECORDED],
                 (" (" + ", ".join(nt["target_gaps"]) + ")")
                 if nt["target_gaps"] else "",
                 nt["by_reason"][NO_TARGET_PASSTHROUGH]))
        _print_batch_pass_rollup(s["batch_pass"])
        _print_emitted_by_rollup(rows)
        _print_stage_rollup(s)
    else:
        print("ledger: SKIPPED (NDI-matlab sibling not found)")


if __name__ == "__main__":
    main()
