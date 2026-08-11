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
import json
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA_ROOT = os.path.dirname(HERE)
INDEX = os.path.join(SCHEMA_ROOT, "schemas", "V_eta", "index.json")
LEDGER = os.path.join(SCHEMA_ROOT, "schemas", "V_eta_coverage_ledger.md")
TARGETS = os.path.join(SCHEMA_ROOT, "schemas", "V_eta_migration_targets.json")


def targets_map():
    """Curated did_v1 -> V_eta emitted-target map (schemas/V_eta_migration_targets.json):
    for each source class, the V_eta document class(es) its migrator actually emits
    (superclasses excluded), plus carried/second_pass/how/flags. Keyed by snake-cased
    source class name. Empty if the file is absent."""
    try:
        return json.load(open(TARGETS)).get("classes", {})
    except Exception:
        return {}


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
    idx = json.load(open(INDEX))
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
        except Exception:
            continue
        out = {}
        for f in files:
            if not f.endswith(".json"):
                continue
            try:
                blob = subprocess.run(["git", "-C", NDI, "show", "%s:%s" % (ref, f)],
                                      capture_output=True, text=True, check=True).stdout
                d = json.loads(blob)
            except Exception:
                continue
            cn = d.get("document_class", {}).get("class_name")
            if cn:
                out[cn] = "%s @%s" % (f, ref)
        if out:
            return out, ref
    return None, None


def _ndi_worktree_templates():
    """Fallback: NDI templates from the checked-out working tree."""
    out = {}
    for p in glob.glob(os.path.join(
            NDI, "src/ndi/ndi_common/database_documents/**/*.json"), recursive=True):
        try:
            d = json.load(open(p))
        except Exception:
            continue
        cn = d.get("document_class", {}).get("class_name")
        if cn:
            out[cn] = os.path.relpath(p, NDI) + " @worktree"
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
        main, ref = _ndi_main_templates()
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
                out[cn] = "app-generated (migrators_%s, no NDI template)" % pkg
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
            txt = open(p).read()
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
        "DROPPED as a class. The `epoch_id` edge that replaces it is an edge, "
        "not a document class, so there is no target and that is final."),

    # "stimulus_response and stimulus_response_scalar_parameters DELETE
    #  (superclass-only, 0 docs)". A class no document has ever been an
    #  instance of cannot have a migration target.
    "stimulus_response": (
        NO_TARGET_DISSOLVED, "V_eta_stimulus_response_model_plan.md",
        "stimulus_response and stimulus_response_scalar_parameters DELETE",
        "DELETED. Superclass-only with zero documents in any corpus, so there "
        "is nothing to migrate and no target to name."),
    "stimulus_response_scalar_parameters": (
        NO_TARGET_DISSOLVED, "V_eta_stimulus_response_model_plan.md",
        "stimulus_response and stimulus_response_scalar_parameters DELETE",
        "DELETED. Superclass-only with zero documents in any corpus, so there "
        "is nothing to migrate and no target to name."),

    # NOT `sampled_body`, and the difference is the reason this table exists.
    # The sign-off re-homes FOUR FIELDS -- `time_type` to the time axis's
    # `datum_type`, `data_type` to the STATEMENT's, `data_dim` to the axis
    # count, `samples_regular_intervals` to the axis `regular` flag -- and the
    # axis entry mounts on `subject_statement` OR `sampled_body` depending on
    # `storage_mode` (V_eta_data_body_model_plan.md). Writing `sampled_body`
    # here would pick one of the two mounts, which is a modelling decision the
    # team has not made. The class is retired; its fields land in a MODEL, not
    # in a named document class.
    "binaryseries_parameters": (
        NO_TARGET_DISSOLVED, "V_eta_go_forward_class_audit.md",
        "`binaryseries_parameters` folds into the data_body model and is retired",
        "The sign-off names FIELD destinations and NO TARGET CLASS -- so "
        "`sampled_body` is NOT recorded as its target: the axis entry mounts on "
        "`subject_statement` or on `sampled_body` by `storage_mode`, and "
        "choosing between the two mounts is a modelling call nobody has made."),

    # THE ONE ROW WHERE THE RECORD CONTRADICTS ITSELF, LEFT VISIBLE RATHER THAN
    # RESOLVED HERE. Two statements in the SAME document:
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
        "CONTESTED. The sign-off says `ngrid is DISSOLVED (deleted, not "
        "migrated)` and the plan's FINAL class block says `ngrid DELETED`, "
        "while the same document's R4 section says `ngrid` phases into "
        "`sampled_body` -- a fold WITH a target. No target is recorded, "
        "because only the dissolution is in the team's own words; the "
        "disagreement is left visible rather than settled by a tool."),
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
        "v1 `filter` is a superclass block on `pyraview`. It becomes a "
        "separate `frequency_filter` document",
        "Becomes a separate `frequency_filter` document plus a `filter_id` "
        "edge from the observation the pyraview fold mints. Today the migrator "
        "only renames the block in place."),

    # "epochfiles_ingested becomes `ingestion_manifest` with filenavigator_id
    #  RESTORED" -- a named class, in the signed line itself.
    "epochfiles_ingested": (
        ["ingestion_manifest"], "V_eta_epoch_plan.md",
        "epochfiles_ingested becomes `ingestion_manifest`",
        "epochfiles_ingested becomes `ingestion_manifest`",
        "Becomes `ingestion_manifest`, with `filenavigator_id` restored and "
        "the invented required `epochid` edge replaced by `epoch_id`."),

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
        "the v1 `stimulus_presentation` id is preserved on the body-of-record "
        "it becomes (the `timed_sequence`)",
        "DECOMPOSED around its preserved id: the id rides on the "
        "`timed_sequence`, with one `timed_sequence_manipulation` per resolved "
        "subject. The deduped stimulus `data_type` documents it also mints are "
        "not a fixed class set and are not listed."),
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
        text = re.sub(r"<!--.*?-->", "", fh.read(), flags=re.S)
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

    lines = ["DENOMINATOR: %d transcribed decision(s) checked against %d plan "
             "document(s); every one must quote a real TEAM-SIGN-OFF line"
             % (len(checks), len({c[2] for c in checks}))]
    for kind, cls, plan, frag, mapping in checks:
        path = os.path.join(SCHEMA_ROOT, "schemas", plan)
        if not os.path.exists(path):
            fails.append("%s %s: cited document %s does not exist"
                         % (kind, cls, plan))
            continue
        hits = [n for n, ln in _signoff_lines(plan) if frag in ln]
        if not hits:
            fails.append("%s %s: no TEAM-SIGN-OFF line in %s contains %r"
                         % (kind, cls, plan, frag))
            continue
        # The MAPPING sentence need not be on the sign-off line -- a sign-off
        # routinely approves "the model as written below". It must be in the
        # document, though, or the class mapping is unsourced.
        if mapping is not None:
            with open(path) as fh:
                body = re.sub(r"\s+", " ", fh.read())
            if re.sub(r"\s+", " ", mapping) not in body:
                fails.append("%s %s: %s does not contain the mapping sentence "
                             "%r" % (kind, cls, plan, mapping))
                continue
        lines.append("  [ok] %-14s %-28s %s:%d" % (kind, cls, plan, hits[0]))
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
                "coverage: `%s` has decided_targets in BOTH "
                "V_eta_migration_targets.json (%s) and "
                "DECIDED_TARGETS_BY_SIGNOFF (%s). One fact, one place -- "
                "delete whichever is the copy." % (cn, curated_decided, signed[0]))
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
    # sanity: every named target class should exist in the built V_eta schema
    unknown = sorted({t for r in rows
                      for t in (r["targets"] + r["second_pass"] + r["decided_targets"])
                      if t not in veta})
    if unknown:
        print("  WARNING: target classes not in V_eta schema: " + ", ".join(unknown))
    return veta, v1, rows


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
        return "· **DISSOLVES** -- no target class, per `%s`" % (
            (r.get("no_target_signoff") or {}).get("document"))
    if reason == NO_TARGET_DISPUTED:
        return "· ⚠ **DISPUTED** -- the record states two dispositions; see `%s`" % (
            (r.get("no_target_signoff") or {}).get("document"))
    if reason == NO_TARGET_PASSTHROUGH:
        return "· **passes through as itself** by decision"
    return "· ⚠ **NO TARGET AND NO DISSOLUTION RECORDED** -- a gap, not a decision"


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
    schema = ("SCHEMA: %d of %d decided target class(es) present in the built "
              "set" % (len(built), bs["schema_targets_named"]))
    if built:
        schema += " (" + ", ".join("`%s`" % t for t in built) + ")"
    if missing:
        schema += "; NOT built: " + ", ".join("`%s`" % t for t in missing)
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
            gaplist=(" (" + ", ".join("`%s`" % c
                                      for c in s["no_target"]["target_gaps"]) + ")"
                     if s["no_target"]["target_gaps"] else "")),
        "",
        "| v1 class | → V_eta target(s) | what happens to it | disposition | source |",
        "|---|---|---|---|---|",
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
            tgt = "· passes through as `%s` (no migrator; target unrecorded)" % (
                r["targets"][0])
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
            f"| `{r['v1_class']}` | {tgt} | {acct} | {r['disposition']} | {r['source']} |")
    lines.append("")
    lines.append("*`class`\\* = minted in the NDI second pass. "
                 "\"on `subject`\" = the pre-existing class the statements attach to. "
                 "**will become** = a signed decision that no migrator implements yet. "
                 "The `what happens to it` column is the authored per-class account; "
                 "`⚠` prefixes its caveat; `⚑` prefixes the DERIVED build state, "
                 "which states the SCHEMA half and the MIGRATOR half separately and "
                 "may correct an authored `BUILD NOT DONE` beside it.*")
    lines.append("")
    open(LEDGER, "w").write("\n".join(lines))


def write_ledger_json(rows):
    """Machine-readable ledger for the web viewer (Coverage panel)."""
    doc = {
        "title": "V_eta migration coverage ledger",
        "description": LEDGER_BLURB.replace(" -- ", " — "),
        "summary": _summary(rows),
        "rows": rows,
    }
    open(LEDGER_JSON, "w").write(json.dumps(doc, indent=2) + "\n")


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
        sys.exit("coverage: %d transcribed decision(s) no longer match the "
                 "document they cite." % len(cite_fails))

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

    veta, v1, rows = build_ledger()
    if v1:
        write_ledger(veta, v1, rows)
        write_ledger_json(rows)
        s = _summary(rows)
        print(f"ledger: wrote {os.path.relpath(LEDGER, SCHEMA_ROOT)} + "
              f"{os.path.relpath(LEDGER_JSON, SCHEMA_ROOT)} ({len(v1)} v1 classes"
              + (f", {s['gaps']} UNMAPPED" if s["gaps"] else "") + ")")
        nt = s["no_target"]
        print("  no-target census: DENOMINATOR %d rows, %d naming no target -- "
              "%d dissolved, %d DISPUTED, %d GAP%s (+%d self-target passthroughs, "
              "which do name a target)"
              % (s["total"], nt["rows_naming_no_target"],
                 nt["by_reason"][NO_TARGET_DISSOLVED],
                 nt["by_reason"][NO_TARGET_DISPUTED],
                 nt["by_reason"][NO_TARGET_UNRECORDED],
                 (" (" + ", ".join(nt["target_gaps"]) + ")")
                 if nt["target_gaps"] else "",
                 nt["by_reason"][NO_TARGET_PASSTHROUGH]))
    else:
        print("ledger: SKIPPED (NDI-matlab sibling not found)")


if __name__ == "__main__":
    main()
