#!/usr/bin/env python3
"""#69, the cheap interim -- which field names are declared TWICE in one class chain?

WHY THIS EXISTS
---------------
A subclass that redeclares a field its ancestor already declares creates TWO live
storage locations for one fact, and NOTHING anywhere says which is authoritative.

The collision is invisible by construction. `resolvePlacement`'s collision check
fires only *within one* `targetBlock`, and the default `placement=declaring_class`
puts the ancestor and the descendant in DIFFERENT blocks -- so a redeclaration
never trips it. A cross-block duplicate name is checked NOWHERE: not in
`+did2/+schema`, not in `+did2/+validate`, not in this repo's tools or tests. The
docstring claims it errors. The code does not. Read the code.

So this is the third instance of the standing pattern: a rule everyone believes is
enforced, enforced by nothing, and therefore silently violated.

WHAT THIS IS NOT
----------------
It is NOT the fix. The fix -- merge a redeclaration into the ancestor's block entry
and require the child to NARROW rather than widen -- touches the meta-schema, the
validator and `fieldsFor`'s contract, and is to be decided with the binding-
governance work. This check only makes the condition LOUD, which is what the open
item asks for in as many words.

Nor does it decide the rows it finds. It reports them with their provenance so a
decision can be made on evidence.

THE SPLIT IS DERIVED, NOT HAND-MAINTAINED -- AND THAT IS A REPAIR
------------------------------------------------------------------
Some duplicates are NDI's own: an NDI template declares a class-block `name`
beside `base.name`, and a source tombstone that dropped it would stop matching
the writer, which is the one thing tombstones exist to do. Others were minted on
this side, and for those "which block is authoritative" is a live question. The
two need to be told apart, and until 2026-08-12 they were told apart BY HAND.

THE HAND LIST DRIFTED, IN THE DIRECTION THAT COSTS DOCUMENTS. This module's own
docstring said "six of the nine rows are V1 FIDELITY" and called
`stimulus_parameter.name` "the SIXTH fidelity row"; the `V1_FIDELITY` set below
it held FIVE and omitted exactly that row. So the tool filed a field NDI's own
schema declares under "no template forces this -- OPEN: which block is
authoritative?", which is an invitation to delete it. Deleting it would have been
expensive and silent: `migrators_j/stimulus_parameter.m` is a PURE PASSTHROUGH
held for #31, so the document reaches validation in its did_v1 shape, and a
dropped declaration leaves a field every real document carries undeclared ->
`undeclaredField` quarantines all of them.

A list that describes an external fact, maintained by hand next to a prose
description of itself, will disagree with one of the two eventually. So the split
is now READ from `schemas/V_eta_ndi_ground_truth.json` -- the artifact
`tools/ndi_ground_truth.py` extracts from NDI `origin/main` -- exactly the way
`tools/check_constraint_refinement.py` already derives its provenance column.
Names are matched with underscores stripped and case folded, because V_eta is
snake_case and NDI is camelCase and a sweep that forgets it searches for a string
the other repository has never contained (`demo_ndi` against `demoNDI` cost this
project a whole disposition).

THREE BUCKETS, NOT TWO, BECAUSE THE GROUND TRUTH CANNOT ALWAYS ANSWER
----------------------------------------------------------------------
    V1-FIDELITY     did_v1 declares the name in the blocks of TWO OR MORE of the
                    classes that declare it here. Positive evidence. Removing the
                    duplicate would stop the tombstone matching the writer.

    V_eta-SHADOW    EVERY declaring class has a did_v1 counterpart, and fewer
                    than two of them declare this name. Also positive evidence,
                    in the other direction: the second storage location was
                    minted on this side.

    NOT-DERIVABLE   at least one declaring class has NO did_v1 counterpart. The
                    ground truth did not answer, and the honest report is that it
                    did not -- NOT "V_eta invented this". A class V_eta RENAMED
                    from its did_v1 source (v1 `app` -> V_eta `software`) lands
                    here too, and reading it as "no template forces this" is the
                    absence-as-evidence error operating rule 3 forbids.

A NOT-DERIVABLE row with no override is REPORTED, never failed. Forcing one would
make this tool record a disposition, which is operating rule 4's business and not
its own.

THE HAND LIST SURVIVES ONLY AS AN EXPLICIT OVERRIDE, AND AN UNUSED ONE IS AN ERROR
-----------------------------------------------------------------------------------
`OVERRIDES` below states a bucket for a NOT-DERIVABLE row where a human has
positive evidence the artifact cannot carry -- a rename the lookup cannot follow,
say. It applies to NOTHING ELSE: an override naming a row the ground truth CAN
answer is refused rather than honoured, so a hand entry can never quietly outvote
NDI, which is the failure this repair exists to remove.

An override that matches no row is a HARD ERROR, with or without `--enforce`. A
stale exception is exactly how the old list drifted -- it went wrong by omission
and nothing noticed for two days -- and an exception nobody is using is an
exception nobody is checking.

WHAT THE BASELINE MEANS
-----------------------
Enforcement is a RATCHET, following the same shape as check_empty_ontology_nodes.
The count may FALL freely; any INCREASE fails, and a count BELOW the baseline
fails too so ground won is not quietly given back. A hard zero is impossible
today and would be wrong to demand: most rows are NDI's own.

WHAT THE DERIVATION FOUND ON 2026-08-12, re-derivable and therefore not
maintained here -- run the tool, do not trust this paragraph:

    9 rows: 6 V1-FIDELITY, 0 V_eta-SHADOW, 3 NOT-DERIVABLE, 0 overrides in use.

    V1-FIDELITY   element.name, measurement.name, probe_location.name,
                  pyraview.label, stimulus_parameter.name,
                  subjectmeasurement.datestamp
    NOT-DERIVABLE method_parameters.name, software.name, strain.name -- none of
                  the three leaves has a did_v1 counterpart. Which block is
                  authoritative for them is OPEN and rides with binding
                  governance (#69, V_eta_OPEN_WORK.md).

The old hand list and the derivation agree on all six fidelity rows, which is the
cross-check that matters: the repair reproduces the corrected list rather than
replacing it with a different one.

Usage:  python3 tools/check_duplicate_field_declarations.py
        python3 tools/check_duplicate_field_declarations.py --enforce
"""

import argparse
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SCHEMA_ROOT = os.path.join(REPO, "schemas", "V_eta")

# The did_v1 truth, extracted from NDI origin/main by tools/ndi_ground_truth.py.
# READ, never written here. Its absence is an ERROR, not a fallback: a split that
# quietly reports every row as unclassifiable because the file was missing would
# look exactly like a clean run to the ratchet.
GROUND_TRUTH = os.path.join(REPO, "schemas", "V_eta_ndi_ground_truth.json")

# The count as of 2026-08-12. May fall freely; an increase fails, and so does a
# fall that is not recorded here.
BASELINE = 9

V1_FIDELITY = "V1-FIDELITY"
V_ETA_SHADOW = "V_eta-SHADOW"
NOT_DERIVABLE = "NOT-DERIVABLE"

# Explicit, named exceptions for NOT-DERIVABLE rows only -- see the docstring.
# Keyed (declaring class, field name) -> (bucket, the evidence, in one line).
# EMPTY TODAY, deliberately: the three NOT-DERIVABLE rows are the three the open
# item calls genuinely open, and writing a bucket for them here would be
# recording a decision rather than an exception.
OVERRIDES = {}


def _norm(s):
    """Fold a class or field name so snake_case and camelCase compare equal.

    V_eta is snake_case, NDI is camelCase, and a sweep that forgets it searches
    for a string the other repository has never contained. Underscores stripped,
    case folded, nothing else.
    """
    return str(s).replace("_", "").lower()


def load_classes(root=SCHEMA_ROOT):
    """Every built V_eta class, keyed by class_name."""
    classes = {}
    for sub in ("stable", "draft"):
        d = os.path.join(root, sub)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".json") or fn == "index.json":
                continue
            with open(os.path.join(d, fn)) as fh:
                j = json.load(fh)
            cn = j.get("document_class", {}).get("class_name")
            if cn:
                classes[cn] = j
    return classes


def load_ground_truth(path=GROUND_TRUTH):
    """Return (index, stats) for the did_v1 truth.

    `index` maps a NORMALISED did_v1 class name to its original spelling and the
    normalised set of field names it declares in its OWN block. `stats` says
    whether the artifact was found and how much of it was read, so "no did_v1
    counterpart" and "never opened the file" stay distinguishable in the output.
    """
    stats = {"path": path, "present": False, "error": None, "ndi_ref": None,
             "classes": 0, "field_names": 0}
    if not os.path.exists(path):
        stats["error"] = "artifact not present -- run tools/ndi_ground_truth.py"
        return {}, stats
    try:
        with open(path) as fh:
            gt = json.load(fh)
    except (OSError, ValueError) as exc:
        stats["error"] = f"unreadable: {exc}"
        return {}, stats
    stats["present"] = True
    stats["ndi_ref"] = gt.get("ndi_ref")
    index = {}
    for cn, entry in (gt.get("classes") or {}).items():
        fields = {_norm(f) for f in (entry.get("fields") or [])}
        index[_norm(cn)] = {"class": cn, "fields": fields}
        stats["field_names"] += len(fields)
    stats["classes"] = len(index)
    return index, stats


def chain(classes, cn, seen=None):
    """CN plus its ancestors, depth-first, cycle-safe."""
    if seen is None:
        seen = []
    if cn in seen or cn not in classes:
        return seen
    seen = seen + [cn]
    for s in classes[cn]["document_class"].get("superclasses", []) or []:
        sn = s.get("class_name")
        if sn and sn not in seen:
            seen = chain(classes, sn, seen)
    return seen


def find_duplicates(classes):
    """[(leaf_class, field_name, (declaring classes...))], sorted."""
    rows = []
    for cn in sorted(classes):
        declared = collections.defaultdict(list)
        for c in chain(classes, cn):
            for f in classes[c].get("fields") or []:
                name = f.get("name")
                if name:
                    declared[name].append(c)
        for name, owners in sorted(declared.items()):
            if len(owners) > 1:
                rows.append((cn, name, tuple(sorted(owners))))
    return rows


def classify(rows, gt_index, gt_stats, overrides=None):
    """Bucket every duplicate row against the did_v1 ground truth.

    Returns (classified, override_report). `classified` is one dict per row
    carrying the DERIVED bucket, the bucket actually reported, the evidence, and
    whether an override was applied. `override_report` names every override that
    was used, refused (the row was derivable, so NDI wins) and unused.
    """
    overrides = OVERRIDES if overrides is None else overrides
    used, refused = {}, {}
    out = []
    for leaf, name, owners in rows:
        if not gt_stats.get("present"):
            derived, why = NOT_DERIVABLE, (
                f"ground truth not read ({gt_stats.get('error')}) -- nothing was "
                "looked up; this is not a finding about did_v1")
        else:
            resolved = {o: gt_index.get(_norm(o)) for o in owners}
            unknown = sorted(o for o, e in resolved.items() if e is None)
            declaring = sorted(o for o, e in resolved.items()
                               if e is not None and _norm(name) in e["fields"])
            if len(declaring) >= 2:
                pretty = " and ".join(
                    f"{resolved[o]['class']}.{name}" for o in declaring)
                derived, why = V1_FIDELITY, (
                    f"did_v1 declares it in {len(declaring)} of the declaring "
                    f"blocks -- {pretty}; dropping either would stop the "
                    "tombstone matching the writer")
            elif unknown:
                derived, why = NOT_DERIVABLE, (
                    "no did_v1 class matches "
                    + " and ".join(repr(o) for o in unknown)
                    + " (a V_eta target class, or a rename this lookup cannot "
                      "follow) -- NOT looked up, not 'absent from NDI'")
            else:
                had = ", ".join(f"{resolved[o]['class']}.{name}"
                                for o in declaring) or "none of them"
                derived, why = V_ETA_SHADOW, (
                    "every declaring class has a did_v1 counterpart and did_v1 "
                    f"declares this name in {had} -- the second storage location "
                    "was minted on this side")

        key = (leaf, name)
        override = overrides.get(key)
        bucket, applied = derived, None
        if override is not None:
            if derived == NOT_DERIVABLE:
                bucket, applied = override[0], override
                used[key] = override
            else:
                # An override may never outvote the artifact. Refusing rather
                # than honouring is the whole point: a hand entry that disagrees
                # with NDI is a defect in the hand entry.
                refused[key] = (derived, override)
        out.append({"leaf": leaf, "name": name, "owners": owners,
                    "derived": derived, "bucket": bucket, "why": why,
                    "override": applied})
    unused = sorted(k for k in overrides if k not in used and k not in refused)
    return out, {"used": used, "refused": refused, "unused": unused}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--enforce", action="store_true",
                    help="exit 1 if the count has grown past BASELINE")
    args = ap.parse_args(argv)

    classes = load_classes()
    gt_index, gt_stats = load_ground_truth()
    rows = find_duplicates(classes)
    classified, ovr = classify(rows, gt_index, gt_stats)

    # DENOMINATOR FIRST, unconditionally. A count with no denominator is not
    # evidence -- silentLoss printed "0 empty edges" for two days while reading
    # nothing, and every report that rendered it repeated the omission.
    print(f"DENOMINATOR: {len(classes)} V_eta classes read from {SCHEMA_ROOT}, "
          f"{len(classes)} chains walked")
    print(f"  did_v1 ground truth artifact   "
          f"{'PRESENT' if gt_stats['present'] else 'ABSENT'}   {gt_stats['path']}")
    if gt_stats["present"]:
        print(f"    ndi_ref                      {gt_stats['ndi_ref']}")
        print(f"    did_v1 classes indexed       {gt_stats['classes']}")
        print(f"    did_v1 field names indexed   {gt_stats['field_names']}")
    else:
        print(f"    NOT READ: {gt_stats['error']}")
        print("    Every row below reads NOT-DERIVABLE. That is the tool not "
              "having looked, NOT a finding about did_v1.")
    print(f"  hand overrides declared        {len(OVERRIDES)} "
          f"(used {len(ovr['used'])}, refused {len(ovr['refused'])}, "
          f"unused {len(ovr['unused'])})")
    print(f"FIELD NAMES DECLARED IN MORE THAN ONE BLOCK OF A CHAIN: {len(rows)} "
          f"(baseline {BASELINE})")

    counts = collections.Counter(r["bucket"] for r in classified)
    for bucket, blurb in (
            (V1_FIDELITY,
             ("did_v1 declares both. Removing these would stop the tombstone "
              "matching the writer")),
            (V_ETA_SHADOW,
             ("every declaring class is did_v1 and did_v1 does NOT declare "
              "both. OPEN: which block is authoritative?")),
            (NOT_DERIVABLE,
             ("the ground truth could not answer. NOT a finding that V_eta "
              "invented these"))):
        sel = [r for r in classified if r["bucket"] == bucket]
        print(f"\n  {bucket} -- {blurb} ({counts.get(bucket, 0)}):")
        for r in sel:
            mark = "  [OVERRIDE]" if r["override"] else ""
            print(f"    {r['leaf']:<26} {r['name']:<14} declared in: "
                  f"{' + '.join(r['owners'])}{mark}")
            print(f"        {r['why']}")
            if r["override"]:
                print(f"        OVERRIDE: {r['override'][1]}")

    failures = []
    for key, (derived, override) in sorted(ovr["refused"].items()):
        failures.append(
            f"OVERRIDE REFUSED for {key[0]}.{key[1]}: the ground truth answers "
            f"this row ({derived}), so the hand entry claiming {override[0]!r} "
            "cannot apply. Delete it, or fix the ground truth.")
    for key in ovr["unused"]:
        failures.append(
            f"UNUSED OVERRIDE {key[0]}.{key[1]}: it matches no duplicate row. "
            "A stale exception is how the old hand list drifted -- remove it.")
    if not gt_stats["present"]:
        failures.append(
            "GROUND TRUTH ABSENT: the fidelity split was not derived. "
            "Run tools/ndi_ground_truth.py; do not read this run as clean.")

    if failures:
        print()
        for f in failures:
            print(f"FAIL: {f}")
        return 1

    if args.enforce and len(rows) > BASELINE:
        print(f"\nFAIL: {len(rows)} duplicate declaration(s), baseline {BASELINE}.")
        print("A new one means two storage locations for one fact, and nothing "
              "in the validator will tell you which won.")
        print("Fix the declaration, or raise BASELINE deliberately WITH the "
              "evidence that the duplicate is NDI's.")
        return 1
    if args.enforce and len(rows) < BASELINE:
        print(f"\nBASELINE IS STALE: {len(rows)} < {BASELINE}. Lower it so the "
              "ratchet keeps holding the ground that was won.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
