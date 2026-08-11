#!/usr/bin/env python3
"""Derive the binding registry's `strength` column from the FIELD that owns it.

    python3 tools/regen_binding_strengths.py            rewrite the column
    python3 tools/regen_binding_strengths.py --check    fail if it is stale
    python3 tools/regen_binding_strengths.py --json     machine-readable

WHY THIS EXISTS
---------------
`strength` -- how hard a binding is enforced -- was stored in TWO places. The
field constraint carries it (14 of 14 bound field declarations state one) and
`entity_field_bindings` carries it again for three of them. The two copies
AGREED, and they agreed by coincidence: nothing compared them, and nothing
generated one from the other. Three facts stored twice with no arbiter is the
`did_clocktype` failure one layer out -- the same property resolving two ways
depending on which file you happen to read.

THE FIELD IS AUTHORITATIVE. This tool makes the registry's copy DERIVED, so the
second copy is a projection and not a second truth. The registry keeps its own
job -- the CATALOGUE: what is bound, to which vocabulary, open or closed -- which
this tool never touches and never invents.

Reasons, in the order they decide it:

  1. THE VALIDATOR ALREADY HAS THE FIELD. `+did2/+schema/cache.m` walks the
     class chain, resolves the field definition and hands `constraints.binding`
     to `checkBinding`. Reading a registry at validation time would re-implement
     a lookup it has already done, against a second file it does not open.
  2. MOVING THE TRUTH THE OTHER WAY COSTS 31 ROWS. Making the registry
     authoritative means every normative row must state a strength: 34
     normative rows today, 3 of which carry one, so 31 rows would gain a value
     purely to relocate a fact -- 31 new hand-authored assertions, each able to
     disagree with a field.
  3. THE TWO ANSWER DIFFERENT QUESTIONS. "What is bound, and to what" is a
     catalogue question, and the catalogue's whole value is answering it
     without walking 249 schema files. "How hard is this enforced" is a
     property of the declaration site. Deriving the column keeps the catalogue
     complete without making it a rival source of truth.

A FIELD WITH A BINDING AND NO `strength` IS AN ERROR. Not `preferred`, not
inherited from a parent field, not skipped -- an error, at two scopes:

  * HERE, for a row: a registry row that names a field whose binding omits
    `strength` cannot be derived, so this tool refuses and exits non-zero
    rather than writing a value nobody declared.
  * IN pytest, for the WHOLE TREE:
    tests/test_binding_strength_derivation.py
    ::test_every_binding_in_the_built_tree_declares_a_strength
    asserts it over all 14 bound declarations, including the 11 that no
    registry row catalogues -- otherwise the rule would only bite where the
    registry happens to look, and a field could acquire a strength-less
    binding in the 11 unwatched places without a word.

  The reason there is no default: `strength` is an ENFORCEMENT GRADE, and both
  candidate defaults are wrong in a dangerous direction. `preferred` makes an
  ungoverned field read as governed. `required` arms a gate on a 0-quarantine
  corpus, which is the 2,484-quarantine regression this repository has already
  paid for. Absence means the author did not say, and the correct response to
  "did not say" is to stop, not to choose for them.

WHAT IT DOES NOT DO
-------------------
It NEVER adds, removes or reorders a registry row, and it never touches any key
but `strength`. Which fields are catalogued is a decision (operating rule 4);
this tool only fills a derived column on rows that already exist. 11 of the 14
bound fields have no registry row at all -- that count is REPORTED, never
repaired.

It does not arm anything. `binding` conformance is implemented in DID-matlab
(`+did2/+schema/cache.m checkBinding`) behind
`did2.schema.cache.strictMode('BindingConformance')`, which is DISARMED by
default and stays that way; arming it is a separate decision with a separate
blast radius.

WHERE IT SITS
-------------
`tools/gates.py`, immediately after `build_v_eta` (which writes BOTH sides: the
field constraints and the registry) and before `pytest` and
`check_binding_governance` (which read the filled registry). `gates.py --check`
regenerates into a scratch mirror and diffs, and this tool's own `--check` runs
against the working tree in the COMPOSED --check block, so a hand-edited
registry strength fails CI two independent ways.
"""

import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
VETA = os.path.join(REPO, "schemas", "V_eta")
TIERS = ("stable", "draft", "deprecated")

REGISTRY_REL = os.path.join("schemas", "V_eta", "stable",
                            "binding_registry_meta.json")

# The registry's list-valued blocks. Same set and same normativity flags as
# tools/check_binding_governance.py REGISTRY_LISTS -- asserted equal by
# tests/test_binding_strength_derivation.py, because two hand-kept copies of
# one list is the defect this whole file is about.
REGISTRY_LISTS = {
    "subject_statement_bindings": True,
    "relation_bindings": True,
    "entity_field_bindings": True,
    "binding_examples": False,
}

# The derived column is written LAST in the row, so a reader can see at a glance
# which key is a projection and which keys are the catalogue. Position is the
# only thing about the key this tool chooses.
DERIVED_KEY = "strength"


def load(path):
    with open(path) as fh:
        return json.load(fh)


def bound_fields(veta=VETA):
    """Every `constraints.binding` in the built tree, keyed (class, dotted field).

    Returns (index, denominator). The denominator is measured, not assumed: a
    walker that stopped descending would report "no bindings" and read as
    clean, and two of the fourteen live declarations are NESTED
    (relative_reference.value.relation and .value.frame), so a top-level-only
    sweep would miss them and call the tree consistent.
    """
    index = {}
    files_read = 0
    fields_walked = 0
    nested_hits = 0

    def walk(flds, prefix, cls, tier, depth):
        nonlocal fields_walked, nested_hits
        for f in flds or []:
            name = f.get("name", "?")
            here = prefix + name
            fields_walked += 1
            b = (f.get("constraints") or {}).get("binding")
            if isinstance(b, dict):
                index[(cls, here)] = {"binding": b, "tier": tier,
                                      "type": f.get("type"), "depth": depth}
                if depth:
                    nested_hits += 1
            walk(f.get("fields"), here + ".", cls, tier, depth + 1)

    for tier in TIERS:
        for p in sorted(glob.glob(os.path.join(veta, tier, "*.json"))):
            d = load(p)
            if not (isinstance(d, dict) and "document_class" in d):
                continue
            files_read += 1
            walk(d.get("fields"), "", d["document_class"]["class_name"], tier, 0)

    return index, {"document_class_files_read": files_read,
                   "field_declarations_walked": fields_walked,
                   "bound_field_declarations": len(index),
                   "bound_field_declarations_nested": nested_hits}


def derive(reg, index):
    """Compute the desired `strength` for every registry row.

    Returns (plan, errors). `plan` has one entry per row in declaration order:
    (list_name, position, row, desired, why) where `desired` is the strength the
    row should carry, or None for "must carry none".

    THE RULE, entire:
      names class AND field -> strength is that field's binding strength
      names neither/one     -> no strength is derivable, so it must carry none
    Anything that cannot follow the rule is an ERROR, never a skip. A skip is
    how a row with an underivable second copy of an authoritative fact survives
    a generator that claims to have regenerated the column.
    """
    plan, errors = [], []
    for list_name in REGISTRY_LISTS:
        for i, row in enumerate(reg.get(list_name, [])):
            cls, fname = row.get("class"), row.get("field")
            names_field = bool(cls) and bool(fname)
            if not names_field:
                if DERIVED_KEY in row:
                    errors.append(
                        "%s[%d] (class=%r field=%r) states %s=%r but names no "
                        "field, so nothing can derive it and nothing can "
                        "contradict it. Name the field or drop the key."
                        % (list_name, i, cls, fname, DERIVED_KEY,
                           row.get(DERIVED_KEY)))
                plan.append((list_name, i, row, None, "names no field"))
                continue
            hit = index.get((cls, fname))
            if hit is None:
                errors.append(
                    "%s[%d] catalogues %s.%s, which declares no "
                    "constraints.binding in the built tree. The registry is a "
                    "catalogue of real bindings; there is nothing to derive "
                    "from." % (list_name, i, cls, fname))
                continue
            strength = hit["binding"].get(DERIVED_KEY)
            if strength is None:
                errors.append(
                    "%s[%d] catalogues %s.%s, whose binding declares NO "
                    "%s. There is no default: `preferred` would make an "
                    "ungoverned field read as governed and `required` would "
                    "arm a gate nobody measured. Declare it on the field."
                    % (list_name, i, cls, fname, DERIVED_KEY))
                continue
            plan.append((list_name, i, row, strength,
                         "derived from %s.%s" % (cls, fname)))
    return plan, errors


def rebuild(reg, plan):
    """Apply the plan to a COPY of the registry, touching only DERIVED_KEY."""
    out = dict(reg)
    for list_name in REGISTRY_LISTS:
        if list_name not in out:
            continue
        out[list_name] = [dict(r) for r in out[list_name]]
    for list_name, i, _row, desired, _why in plan:
        row = out[list_name][i]
        row.pop(DERIVED_KEY, None)
        if desired is not None:
            row[DERIVED_KEY] = desired
    return out


def render(reg):
    """Serialise exactly as build_v_eta.py does, so a no-op run is byte-stable."""
    return json.dumps(reg, indent=4) + "\n"


def run(veta=VETA, registry_path=None, check=False, out=print):
    registry_path = registry_path or os.path.join(REPO, REGISTRY_REL)
    index, den = bound_fields(veta)
    reg = load(registry_path)
    plan, errors = derive(reg, index)

    rows_total = sum(len(reg.get(k, [])) for k in REGISTRY_LISTS)
    normative = sum(len(reg.get(k, [])) for k, n in REGISTRY_LISTS.items() if n)
    derived_rows = [p for p in plan if p[3] is not None]
    catalogued = {(p[2].get("class"), p[2].get("field")) for p in derived_rows}
    uncatalogued = sorted(k for k in index if k not in catalogued)

    # RULE 5: the denominator, first and unconditional.
    out("DENOMINATOR: %d bound field declaration(s) read from %d "
        "document_class file(s) (%d field declarations walked, %d of the "
        "bindings NESTED); %d registry list(s), %d row(s) (%d normative, %d "
        "illustrative)"
        % (den["bound_field_declarations"], den["document_class_files_read"],
           den["field_declarations_walked"],
           den["bound_field_declarations_nested"],
           len(REGISTRY_LISTS), rows_total, normative, rows_total - normative))
    out("  rows naming a class AND a field (derivable) : %d" % len(derived_rows))
    out("  rows naming no field (must carry none)      : %d"
        % (len(plan) - len(derived_rows)))
    out("  bound fields with NO registry row           : %d  "
        "(reported, never repaired -- adding a catalogue row is a decision)"
        % len(uncatalogued))

    if errors:
        out("")
        out("UNDERIVABLE: %d row(s). Nothing was written." % len(errors))
        for e in errors:
            out("  ERROR %s" % e)
        return 1, {"errors": errors}

    desired_text = render(rebuild(reg, plan))
    with open(registry_path) as fh:
        current_text = fh.read()

    disagreements = []
    for list_name, i, row, desired, why in plan:
        have = row.get(DERIVED_KEY)
        if have != desired:
            disagreements.append({
                "list": list_name, "index": i,
                "class": row.get("class"), "field": row.get("field"),
                "registry_says": have, "field_says": desired, "why": why})

    out("")
    out("DERIVED COLUMN -- %d row(s), field -> registry" % len(derived_rows))
    for list_name, i, row, desired, why in derived_rows:
        mark = "ok" if row.get(DERIVED_KEY) == desired else "STALE"
        out("  %-5s %-26s %-14s.%-22s %s"
            % (mark, list_name, row.get("class"), row.get("field"), desired))

    out("")
    out("DISAGREEMENTS (registry copy vs the authoritative field): %d"
        % len(disagreements))
    for d in disagreements:
        out("  %s[%d] %s.%s -- registry says %r, the FIELD says %r. The field "
            "is authoritative; this column is derived."
            % (d["list"], d["index"], d["class"], d["field"],
               d["registry_says"], d["field_says"]))

    stale = desired_text != current_text
    if check:
        out("")
        if stale:
            out("STALE: %s does not match what the fields say. Run "
                "`python3 tools/regen_binding_strengths.py` (or "
                "`python3 tools/gates.py`)." % REGISTRY_REL)
            return 1, {"disagreements": disagreements, "stale": True}
        out("UP TO DATE: %s matches the field declarations byte for byte."
            % REGISTRY_REL)
        return 0, {"disagreements": disagreements, "stale": False}

    if stale:
        with open(registry_path, "w") as fh:
            fh.write(desired_text)
        out("")
        out("REGENERATED %s" % REGISTRY_REL)
    else:
        out("")
        out("UNCHANGED %s (already matches the field declarations)" % REGISTRY_REL)
    return 0, {"disagreements": disagreements, "stale": stale}


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Derive binding_registry_meta.json's `strength` column "
                    "from the authoritative field constraints.")
    ap.add_argument("--check", action="store_true",
                    help="write nothing; exit 1 if the column is stale")
    ap.add_argument("--json", action="store_true",
                    help="print the findings as JSON as well")
    a = ap.parse_args(argv)
    lines = []
    rc, detail = run(check=a.check, out=lines.append)
    print("\n".join(lines))
    if a.json:
        print(json.dumps(detail, indent=2, sort_keys=True))
    return rc


if __name__ == "__main__":
    sys.exit(main())
