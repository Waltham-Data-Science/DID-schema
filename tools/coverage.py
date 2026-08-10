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
    "jSampledBody", "jGetCharAny", "syncrule_mapping",
}


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
            "decided_targets": ((tinfo or {}).get("decided_targets") or []),
            "target_source": target_source,
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
    }


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
        if r.get("target_source") == "decided":
            dt = r.get("decided_targets") or []
            tgt = ("· **will become** " + " + ".join("`" + t + "`" for t in dt)
                   if dt else "· **dissolves / deleted** (no target by design)")
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
        # THE ACCOUNT, IN THE TABLE. This footer used to say "see
        # V_eta_migration_targets.json for the per-class `how`" -- which is to say,
        # the one field that answers the question was in a different file, behind
        # a git checkout. That is exactly why the question could not be answered
        # for a team. Pipes and newlines are escaped so a long sentence cannot
        # break the table.
        acct = (r.get("how") or "").strip()
        if r.get("target_flags"):
            acct = (acct + " " if acct else "") + "⚠ " + r["target_flags"].strip()
        acct = acct.replace("|", "\\|").replace("\n", " ") or "—"
        lines.append(
            f"| `{r['v1_class']}` | {tgt} | {acct} | {r['disposition']} | {r['source']} |")
    lines.append("")
    lines.append("*`class`\\* = minted in the NDI second pass. "
                 "\"on `subject`\" = the pre-existing class the statements attach to. "
                 "**will become** = a signed decision that no migrator implements yet. "
                 "The `what happens to it` column is the authored per-class account; "
                 "`⚠` prefixes its caveat.*")
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
    else:
        print("ledger: SKIPPED (NDI-matlab sibling not found)")


if __name__ == "__main__":
    main()
