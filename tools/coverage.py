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
# The three that REMAIN are named for what they are (`mock`, `demoNDI`,
# `demoNDIMock`) and are demo scaffolding by construction. Note that they are
# NOT unreferenced -- +ndi/+calc/+example/simple.m queries demoNDI.value and
# constructs demoNDIMock documents -- so do not re-derive "nonprod" as "nothing
# mentions it"; that grep was run once against the snake_case spelling and
# returned zero for a repository that has never contained that string.
_NONPROD_CLASSES = {"mock", "demoNDI", "demoNDIMock"}

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
    return lines, fails

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
    veta = veta_index()
    v1 = v1_classes()
    migs = migrator_files()
    vz = vzeta_classes()
    tmap = targets_map()
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
        signed = DECIDED_TARGETS_BY_SIGNOFF.get(cn) or \
            DECIDED_TARGETS_BY_SIGNOFF.get(sn)
        decided_cite = None
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
        _named = list(decided_targets)
        build_state = {
            "schema_targets_named": len(_named),
            "schema_targets_built": sorted(t for t in _named if t in veta),
            "schema_targets_missing": sorted(t for t in _named if t not in veta),
            # A migrator implements the decision only when it EMITS the decided
            # class. Emitting the source class back out is a passthrough.
            "migrator_emits_decided_targets": bool(
                _named and all(t in targets for t in _named)),
            "has_per_class_migrator": mig,
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
    # THE DERIVED STAGE, added last because it reads the finished row. It is a
    # function of fields already on that row -- there is no list here to hand-set
    # and nothing to override it with.
    for r in rows:
        r["stage"] = stage_ladder(r, CORPUS_SCAN)
    # sanity: every named target class should exist in the built V_eta schema
    unknown = sorted({t for r in rows
                      for t in (r["targets"] + r["second_pass"] + r["decided_targets"])
                      if t not in veta})
    if unknown:
        print("  WARNING: target classes not in V_eta schema: " + ", ".join(unknown))
    return veta, v1, rows


# ============================================================================
# THE STAGE LADDER -- "how far has this class actually got?", DERIVED.
# ============================================================================
#
# The question the team asks of this ledger is one question, and answering it
# used to mean reading five columns and forming a judgement:
# `decided_signoff`, `build_state.schema_targets_missing`,
# `build_state.has_per_class_migrator`,
# `build_state.migrator_emits_decided_targets`, and a corpus report nobody has
# open. A judgement assembled by hand drifts; five people assemble it five ways.
#
# So it is a DERIVED FIELD. Never hand-set, never overridable by a list beside a
# paragraph. Every boundary below reads a field that already exists on the row,
# and the `why` string on each rung names the field it read, so a stage can be
# audited without reading this file.
#
# FOUR STATES PER RUNG, NOT TWO. This is the whole design, and it is the
# difference between an instrument and a reassurance:
#
#   yes           the evidence is on the row
#   no            POSITIVE evidence the rung is not met (a target named and not
#                 built; a record that states two incompatible dispositions)
#   n/a           the rung cannot apply, and a SIGNED line says why (a class
#                 signed to dissolve has no target class to build)
#   not measured  this tool cannot see the answer. NOT a `no`.
#
# `not measured` exists because of operating rule 3. A row with no transcribed
# sign-off is not a row with no decision -- coverage.py reads only its own
# checked transcriptions (DECIDED_TARGETS_BY_SIGNOFF, NO_TARGET_BY_DECISION),
# and the team's sign-offs live in ~54 plan documents this tool never opens.
# Rendering that absence as "not decided" would be this repository's signature
# error pointed the other way: an absence promoted to a finding about the
# record. It would also be UNFALSIFIABLE progress -- every transcription added
# would look like the migration advancing.
#
# THE ANTI-VACUITY RULE. A rung is `yes` only on evidence PRESENT, never on an
# empty list. `schema_targets_missing == []` is TRUE for all 102 rows, and for
# 77 of them it is true because no target was ever named -- an empty list
# reading as "everything is built". Stage 2 therefore requires
# `schema_targets_named > 0` as well, which is why it is satisfied by 25 rows
# and not by 102. The same trap is what `_no_target_cell` above was written to
# close one column over.
STAGE_NAMES = {
    0: "source identified",
    1: "disposition DECIDED",
    2: "target classes EXIST in the build",
    3: "a migrator CONSUMES it",
    4: "the migrator emits THE DECIDED targets",
    5: "CORPUS-PROVEN",
}
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


def _stage1_decided(row):
    """A CHECKED sign-off transcription, or nothing this tool can read."""
    reason = row.get("no_target_reason")
    cite = row.get("decided_signoff") or row.get("no_target_signoff")
    if reason == NO_TARGET_DISPUTED:
        # Positive evidence AGAINST: the transcription exists and says the
        # record holds two incompatible dispositions. That is a `no`, not an
        # absence -- and it is the one row on the ladder whose lower rung fails
        # while higher rungs hold.
        doc = (row.get("no_target_signoff") or {}).get("document", "?")
        return S_NO, (f"`no_target_reason` is DISPUTED -- {doc} states two "
                      "incompatible dispositions, so no disposition is decided")
    if cite:
        doc = cite.get("document", "?")
        return S_YES, (f"a TEAM-SIGN-OFF line in `{doc}` is transcribed onto this "
                       "row and re-checked against that document by "
                       "check_decision_citations() on every ledger build")
    claim = row.get("decided_targets_source") == "curated_targets_file"
    extra = ("; V_eta_migration_targets.json DOES claim a signed decision for "
             "this class (`decided_targets`), but that claim is authored and "
             "UNCHECKED -- transcribing it into DECIDED_TARGETS_BY_SIGNOFF "
             "would make this rung readable" if claim else "")
    return S_NOT_MEASURED, (
        "no checked TEAM-SIGN-OFF transcription is attached to this row. "
        "coverage.py reads only its own transcriptions; the team's sign-offs "
        "live in plan documents this tool never opens, so this is the absence "
        "of a TRANSCRIPTION and not evidence that no decision exists" + extra)


def _stage2_targets_built(row):
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


def _stage3_consumed(row):
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
    # THE KNOWN UNDERSTATEMENT, NAMED RATHER THAN PATCHED. Two consumption
    # channels are visible to this tool: a per-class migrator file, and the
    # `second_pass` column. A DID BATCH POST-PASS (+did2/+convert, nine of them)
    # is a third, and NO LEDGER FIELD RECORDS IT -- `generic_file` is consumed
    # by `foldGenericFiles.m` and reads `no` here. That is an understatement,
    # and the fix is a field in V_eta_migration_targets.json, not a grep in this
    # function: a bare name sweep over the convert package matches `base` in 9
    # of the 9 passes and `app` in universalRenames, which is noise a stage
    # cannot be built on.
    return S_NO, ("neither `build_state.has_per_class_migrator` nor a "
                  "`second_pass` entry. NOTE the ledger carries no field for a "
                  "DID batch post-pass (+did2/+convert), so a class consumed only "
                  "by one reads `no` here -- an UNDERSTATEMENT, not a measurement")


def _stage4_emits_decided(row):
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
        return S_NO, ("the decided target(s) "
                      + ", ".join(f"`{t}`" for t in want)
                      + " are not all among what the migrator emits today ("
                      + (", ".join(f"`{t}`" for t in have) if have else "nothing")
                      + ")")
    if row.get("no_target_reason") == NO_TARGET_DISSOLVED:
        doc = (row.get("no_target_signoff") or {}).get("document", "?")
        return S_NA, (f"signed to DISSOLVE in `{doc}`: no target class is decided, "
                      "so there is no emission to check")
    return S_NOT_MEASURED, (
        "`build_state.schema_targets_named` is 0 -- no decided target to check an "
        "emission against")


def _stage5_corpus(row, evidence):
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
    """The full ladder for one row: per-rung state, the stage REACHED, anomalies.

    THE RULE, and it is not negotiable: a class lands on EXACTLY ONE stage, and
    that stage is the highest N for which every rung 1..N is `yes` or `n/a`. A
    rung that is `no` or `not measured` STOPS the climb -- including when a
    higher rung is satisfied.

    A higher rung satisfied over a stopped one is not a promotion and not an
    error to be smoothed away. It is a REAL CONDITION with a name in this
    repository -- `valid_interval` is "BUILT AHEAD OF THE DECISION" in
    CLAUDE.md's own words -- so it is reported as an anomaly, counted, and the
    class is named. Two kinds are counted separately because they mean opposite
    things:

      over_failed      a lower rung has POSITIVE evidence against it. A real
                       contradiction: something was built for a class whose
                       record disagrees with itself.
      over_unmeasured  a lower rung could not be read. Evidence exists above a
                       hole in the RECORD, which is a transcription job, not a
                       build job.
    """
    rungs = []
    try:
        for n, fn in ((1, _stage1_decided), (2, _stage2_targets_built),
                      (3, _stage3_consumed), (4, _stage4_emits_decided)):
            state, why = fn(row)
            rungs.append({"stage": n, "name": STAGE_NAMES[n],
                          "state": state, "why": why})
        state, why = _stage5_corpus(row, evidence)
        rungs.append({"stage": 5, "name": STAGE_NAMES[5],
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
            "stage5_state": S_NOT_MEASURED,
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
    return {
        "unclassifiable": False,
        "unclassifiable_why": None,
        "reached": reached,
        "reached_name": STAGE_NAMES[reached],
        "blocked_by": blocked_by,
        "blocked_by_state": blocked_state,
        "ladder": rungs,
        "anomalies": anomalies,
        "stage5_state": rungs[-1]["state"],
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
    faults, checked = [], []
    for c in ev["corpora"]:
        if not seen.get(c["corpus"]):
            continue
        checked.append(c["corpus"])
        for key, label in (("quarantine_count", "quarantined document(s)"),
                           ("fragment_count", "fragment(s)"),
                           ("orphan_count", "orphan edge(s)")):
            n = c.get(key)
            if n is None:
                faults.append(f'{c["corpus"]}: `{key}` is absent from the report '
                              "-- NOT a zero")
            elif n:
                per_class = (c["fragment_by_class"] if key == "fragment_count"
                             else c["orphan_classes"] if key == "orphan_count"
                             else None)
                if per_class is None or (mine & set(per_class)):
                    faults.append(f'{c["corpus"]}: {n} {label} and the report '
                                  "does not clear this class of them")
        if mine & c["empty_edge_classes"]:
            faults.append(f'{c["corpus"]}: an empty required edge is recorded on '
                          + ", ".join(sorted(mine & c["empty_edge_classes"])))
    if faults:
        return S_NO, ("; ".join(faults)
                      + f' (over {total} document(s) in {len(checked)} corpus(es))')
    return S_YES, (f"{total} document(s) across {len(checked)} corpus(es) "
                   f'({", ".join(checked)}) migrated with 0 quarantine, 0 '
                   "orphans, no empty required edge and no fragment")


def _stage_rollup(rows, evidence):
    """The rollup, DENOMINATOR FIRST. Reports what it could not place."""
    from collections import Counter
    reached = Counter()
    per_stage_state = {n: Counter() for n in (1, 2, 3, 4, 5)}
    anomalies, unclassifiable, with_na = [], [], []
    for r in rows:
        st = r["stage"]
        if st["unclassifiable"]:
            unclassifiable.append({"v1_class": r["v1_class"],
                                   "why": st["unclassifiable_why"]})
            continue
        reached[st["reached"]] += 1
        for rung in st["ladder"]:
            per_stage_state[rung["stage"]][rung["state"]] += 1
        if any(rung["state"] == S_NA for rung in st["ladder"]
               if rung["stage"] <= (st["reached"] or 0)):
            with_na.append(r["v1_class"])
        for a in st["anomalies"]:
            anomalies.append(dict(a, v1_class=r["v1_class"]))
    return {
        # RULE 5, positionally: how many were classified and how many were not,
        # before any figure that depends on either.
        "classified": len(rows) - len(unclassifiable),
        "unclassifiable": len(unclassifiable),
        "unclassifiable_rows": unclassifiable,
        "by_stage_reached": {str(n): reached.get(n, 0) for n in range(6)},
        "reached_with_an_n_a_in_the_chain": sorted(with_na),
        # Each rung on its own, ignoring the ladder order. The GAP between this
        # and `by_stage_reached` is the anomaly story, and printing only the
        # first would hide how much is built above an unreadable record.
        "per_stage_state_counts": {str(n): dict(c)
                                   for n, c in per_stage_state.items()},
        "per_stage_satisfied_independently": {
            str(n): per_stage_state[n][S_YES] for n in (1, 2, 3, 4, 5)},
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
                         for n in (1, 2, 3, 4, 5)},
            "rows": anomalies,
        },
        "stage5": {
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
        "decision_claimed_but_unchecked": sorted(
            r["v1_class"] for r in rows
            if not r["stage"]["unclassifiable"]
            and r["stage"]["ladder"][0]["state"] == S_NOT_MEASURED
            and r.get("decided_targets_source") == "curated_targets_file"),
    }


def _summary(rows):
    from collections import Counter
    return {
        "total": len(rows),
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
    says only "not far"; `stage 0 (stopped at 1, not measured)` says WHICH
    question is unanswered and whether it is unanswered or answered NO -- and
    for 94 of these rows the honest word is `not measured`, not `no`.
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
    return cell


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
    out = [
        "**Stage rollup.** DENOMINATOR: {c} of {t} row(s) classified, {u} "
        "UNCLASSIFIABLE{ulist}. A class lands on EXACTLY ONE stage -- the highest "
        "rung for which every rung below it is satisfied -- so a rung that is "
        "`no` or `not measured` stops the climb even when a higher one holds. "
        "The stage is DERIVED from fields on the row; there is no list to "
        "hand-set. `not measured` is not `no`: coverage.py reads only its own "
        "checked sign-off transcriptions, so an unread rung is a hole in what "
        "this tool can see, never a finding about the record.".format(
            c=sr["classified"], t=s["total"], u=sr["unclassifiable"],
            ulist=(" (" + ", ".join("`" + u["v1_class"] + "`"
                                    for u in sr["unclassifiable_rows"]) + ")"
                   if sr["unclassifiable_rows"] else "")),
        "",
        "| stage | what it means | classes AT this stage | rung satisfied on its own | yes / no / n/a / not measured |",
        "|---|---|---:|---:|---|",
        f'| 0 | {STAGE_NAMES[0]} | {reach["0"]} | {s["total"]} (by construction) | — |',
    ]
    for n in (1, 2, 3, 4, 5):
        st = states[str(n)]
        out.append(
            f'| {n} | {STAGE_NAMES[n]} | {reach[str(n)]} | {ind[str(n)]} | '
            f'{st.get(S_YES, 0)} / {st.get(S_NO, 0)} / {st.get(S_NA, 0)} / '
            f'{st.get(S_NOT_MEASURED, 0)} |')
    an = sr["anomalies"]
    out += [
        "",
        ("**Stage 5 is NOT MEASURED** -- {why}. It is not `no` and it is not "
         "skipped: \"no corpus proved it\" and \"nobody looked\" are different "
         "facts, and this container has no MATLAB and cannot download run "
         "artifacts. WHAT WOULD LIGHT IT UP: {light}"
         if not sr["stage5"]["measured"] else
         "**Stage 5 is COMPUTED** from the corpus reports supplied to this "
         "run.{why}{light}").format(
            why=sr["stage5"]["why"] if not sr["stage5"]["measured"] else "",
            light=sr["stage5"]["what_would_light_it_up"]
            if not sr["stage5"]["measured"] else ""),
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
            "**{n} row(s) claim a signed decision that is not transcribed here** "
            "-- `V_eta_migration_targets.json` gives them `decided_targets`, "
            "which its own header calls \"a signed decision no migrator "
            "implements yet\", but no `TEAM-SIGN-OFF` line is quoted and checked "
            "for them. They read `not measured` at stage 1 and cannot climb. "
            "Transcribing each into `DECIDED_TARGETS_BY_SIGNOFF` (which "
            "re-reads the cited document on every build) is what moves them: "
            "{lst}.".format(n=len(sr["decision_claimed_but_unchecked"]),
                            lst=", ".join("`" + c + "`" for c in
                                          sr["decision_claimed_but_unchecked"])),
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
    migr = ("MIGRATOR: emits them today"
            if bs.get("migrator_emits_decided_targets")
            else "MIGRATOR: does NOT emit them yet")
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
        "| v1 class | stage | → V_eta target(s) | what happens to it | disposition | source |",
        "|---|---|---|---|---|---|",
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
            f"| `{r['v1_class']}` | {_stage_cell(r)} | {tgt} | {acct} "
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
    print("  stage ladder: DENOMINATOR %d row(s) classified, %d UNCLASSIFIABLE%s"
          % (sr["classified"], sr["unclassifiable"],
             ("" if not sr["unclassifiable_rows"] else
              " (" + ", ".join(u["v1_class"]
                               for u in sr["unclassifiable_rows"]) + ")")))
    for n in range(6):
        print("      stage %d  %-38s %4d at this stage | %s satisfied on its own"
              % (n, STAGE_NAMES[n], sr["by_stage_reached"][str(n)],
                 (str(s["total"]) + " (by construction)") if n == 0
                 else str(sr["per_stage_satisfied_independently"][str(n)])))
    an = sr["anomalies"]
    print("      anomalies: %d across %d class(es) (%d over a FAILED rung, "
          "%d over an UNMEASURED rung)"
          % (an["total"], an["classes"], an["by_kind"].get("over_failed", 0),
             an["by_kind"].get("over_unmeasured", 0)))
    print("      stage 5: *** NOT MEASURED *** -- " + sr["stage5"]["why"]
          if not sr["stage5"]["measured"] else
          "      stage 5: computed from corpus reports")


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
        _print_stage_rollup(s)
    else:
        print("ledger: SKIPPED (NDI-matlab sibling not found)")


if __name__ == "__main__":
    main()
