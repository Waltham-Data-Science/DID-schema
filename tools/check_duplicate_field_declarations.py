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

Nor does it decide the eight rows it currently finds. It reports them with their
provenance so a decision can be made on evidence.

WHAT THE BASELINE MEANS
-----------------------
Enforcement is a RATCHET, following the same shape as check_empty_ontology_nodes.
The count may FALL freely; any INCREASE fails. A hard zero is impossible today and
would be wrong to demand: five of the eight rows are V1 FIDELITY. NDI's own
templates declare a class-block `name` beside `base.name`, and a source tombstone
that dropped it would stop matching the writer -- which is the one thing tombstones
exist to do.

    $ git show origin/main:.../database_documents/element.json
        element -> ['ndi_element_class', 'name', 'reference', 'type', 'direct']
    $ git show origin/main:.../database_documents/measurement.json
        measurement -> ['ontologyName', 'name', 'numeric_value', 'string_value']
    $ git show origin/main:.../database_documents/probe/probe_location.json
        probe_location -> ['ontology_name', 'name']
    $ git show origin/main:.../database_documents/subjectmeasurement.json
        subjectmeasurement -> ['measurement', 'value', 'datestamp']
    $ git show origin/main:.../database_documents/data/pyraview.json
        pyraview -> ['label', 'nativeRate', ...]      over filter -> ['label', ...]

The remaining three are V_eta TARGET classes, where no template forces the
duplicate and the question is open. `software` inherits it from its v1 source
(`app -> ['name', 'version', ...]`), so the fold carried it in rather than
inventing it; `method_parameters` and `strain` were minted in the 2026-08-09
session and the duplicate was NOT noticed at the time -- which is the argument for
this check existing, made against its own author.

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

# The count as of 2026-08-09, with every row verified against NDI origin/main.
# May fall freely; an increase fails.
BASELINE = 8

# Rows whose duplicate is NDI's own, quoted in the module docstring above. A
# tombstone must match the writer, so removing these would be the defect, not the
# fix. Keyed (leaf class, field name) -- deliberately not by ancestor, so moving a
# declaration up the chain still shows up as a change.
V1_FIDELITY = {
    ("element", "name"),
    ("measurement", "name"),
    ("probe_location", "name"),
    ("subjectmeasurement", "datestamp"),
    ("pyraview", "label"),
}


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


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--enforce", action="store_true",
                    help="exit 1 if the count has grown past BASELINE")
    args = ap.parse_args()

    classes = load_classes()
    rows = find_duplicates(classes)

    # DENOMINATOR FIRST, unconditionally. A count with no denominator is not
    # evidence -- silentLoss printed "0 empty edges" for two days while reading
    # nothing, and every report that rendered it repeated the omission.
    print(f"DENOMINATOR: {len(classes)} V_eta classes read from {SCHEMA_ROOT}, "
          f"{len(classes)} chains walked")
    print(f"FIELD NAMES DECLARED IN MORE THAN ONE BLOCK OF A CHAIN: {len(rows)} "
          f"(baseline {BASELINE})")

    if rows:
        fidelity = [r for r in rows if (r[0], r[1]) in V1_FIDELITY]
        target = [r for r in rows if (r[0], r[1]) not in V1_FIDELITY]

        print(f"\n  V1 FIDELITY -- NDI's own template declares both ({len(fidelity)}). "
              "Removing these would stop the tombstone matching the writer:")
        for cn, name, owners in fidelity:
            print(f"    {cn:<26} {name:<14} declared in: {' + '.join(owners)}")

        print(f"\n  V_ETA TARGET CLASSES -- no template forces this ({len(target)}). "
              "OPEN: which block is authoritative?")
        for cn, name, owners in target:
            print(f"    {cn:<26} {name:<14} declared in: {' + '.join(owners)}")

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
