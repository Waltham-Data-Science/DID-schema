#!/usr/bin/env python3
"""#70 -- the empty-node harvest: which ontology_terms do the migrators emit with
no CURIE, and is that backlog growing?

WHY THIS EXISTS
---------------
Staging a term as `{node: '', name: 'refractory period'}` is ALREADY the practice
across the J migrators, and it is a reasonable one: a migration can go green and
the CURIEs can be minted afterwards. Both sub-fields are `mustBeNonEmpty: false`,
so nothing rejects it.

The hazard is that an empty node is INDISTINGUISHABLE FROM "we looked and no term
exists". The backlog is therefore invisible: nobody can answer "how many terms are
still unminted, and which", so the debt neither shrinks nor gets reported. That is
the same shape as every other defect in this migration -- a silence that reads as
success.

WHAT IT DOES
------------
TWO sweeps, each with its own denominator and its own ratchet, because they read
different things and either can be broken while the other works:

  MIGRATOR SIDE  the J migrators, for `jOntologyTerm('', <name>)` -- terms emitted
                 into DOCUMENTS with no CURIE. Gated on BASELINE_MIGRATORS.
  SCHEMA SIDE    the built V_eta schemas, for `constraints.binding.values[]`
                 entries that are NodeRefs with an empty `node` -- controlled
                 vocabularies we ENUMERATED but cannot yet resolve. Gated on
                 BASELINE_SCHEMAS.

The schema side was added 2026-08-10 with #67, and it was added because a claim
turned out to be false: `V_eta_OPEN_WORK.md` #57 says the staged
`clock_alignment_configuration.clock` / `clock_alignment.relation` terms are
"counted by #70". They were not. This tool walked ONLY `+migrators_j`, so every
term staged in a SCHEMA was invisible to the one instrument built to make staged
terms visible -- the backlog hiding from its own counter.

Each count may FALL freely; any INCREASE fails under --enforce, so minting terms
is always allowed and adding new unminted ones is a deliberate act that has to
move a number.

NOT CURRENTLY RUN BY CI, despite what this docstring said until 2026-08-10.
`.github/workflows/tests.yml` invokes check_migrator_vocabulary, status_board,
check_duplicate_field_declarations, check_vacuous_tests and
check_signoff_header_staleness -- and not this one. The migrator sweep needs a
DID-matlab checkout the CI job does not have; the SCHEMA sweep needs nothing but
this repo, so it can be wired up whenever someone edits the workflow (outside
this tool's reach).

WHAT IT DELIBERATELY IS NOT
---------------------------
It does NOT write a sentinel into the data. The instrument is the record, not the
documents: putting a marker in `node` would make the schema carry our bookkeeping,
and a future reader could not tell it from a real CURIE.

The name argument is often a VARIABLE (`jOntologyTerm('', variableName)`), not a
literal. Those are reported as `<computed>` with their call site -- the count is
still exact, but the term list is only as specific as the source allows.

Usage:  python3 tools/check_empty_ontology_nodes.py [--did /path/to/DID-matlab]
        python3 tools/check_empty_ontology_nodes.py --enforce   # exit 1 if grown
"""

import argparse
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
VETA = os.path.join(REPO, "schemas", "V_eta")
TIERS = ("stable", "draft", "deprecated")
META_FILES = {"did_schema_meta.json", "CURIE_lookups_meta.json",
              "ndi_reserved_keys.json", "binding_registry_meta.json"}

# The count at the time the gate was introduced (2026-08-09). It may FALL freely;
# an increase fails under --enforce. Lower it when terms are minted -- that is the
# point of the ratchet.
BASELINE_MIGRATORS = 33

# Schema-side baseline, set 2026-08-10 when the sweep was added. It is 8 on the
# day it landed: the four did_clocktype terms x two carriers
# (relative_reference.value.clock and clock_alignment_configuration.clock), staged
# empty because the NDIC identifier authority is in no repository in scope --
# NDIC.txt was moved out of NDI-matlab in commit 2c19bf24c. Lower it the moment
# real CURIEs are assigned.
BASELINE_SCHEMAS = 8

CALL = re.compile(r"jOntologyTerm\(\s*''\s*,\s*([^)]*)\)")
LITERAL = re.compile(r"^'((?:[^']|'')*)'\s*$")


def sweep(did_path):
    root = os.path.join(did_path, "src", "did", "+did2", "+convert", "+migrators_j")
    rows = []
    if not os.path.isdir(root):
        return None, rows
    files = 0
    for dirpath, _, names in os.walk(root):
        for n in sorted(names):
            if not n.endswith(".m"):
                continue
            files += 1
            p = os.path.join(dirpath, n)
            rel = os.path.relpath(p, did_path)
            with open(p) as fh:
                for i, line in enumerate(fh, 1):
                    for m in CALL.finditer(line):
                        arg = m.group(1).strip()
                        lit = LITERAL.match(arg)
                        rows.append({
                            "migrator": n,
                            "name": lit.group(1).replace("''", "'") if lit else "<computed>",
                            "expression": None if lit else arg,
                            "site": "%s:%d" % (rel, i),
                        })
    return files, rows


def sweep_schemas(veta=VETA):
    """Built V_eta schemas: admissible-set entries that are NodeRefs with no CURIE.

    Only `constraints.binding.values[]` is counted. `blank_value` on an
    ontology_term is `{node: '', name: ''}` on EVERY such field by construction,
    so counting those would report a number that says nothing; an enumerated
    admissible set whose members have no node is a real, actionable backlog item.
    """
    rows = []
    files = 0
    fields_seen = 0

    def walk(fields, path, cls, tier):
        nonlocal fields_seen
        for f in fields or []:
            name = f.get("name")
            here = path + "." + name if path else name
            fields_seen += 1
            b = (f.get("constraints") or {}).get("binding") or {}
            for v in b.get("values") or []:
                if isinstance(v, dict) and "node" in v and not v.get("node"):
                    rows.append({"class": cls, "field": here, "tier": tier,
                                 "root": b.get("root", "<unnamed set>"),
                                 "name": v.get("name", "")})
            walk(f.get("fields"), here, cls, tier)

    for tier in TIERS:
        for p in sorted(glob.glob(os.path.join(veta, tier, "*.json"))):
            if os.path.basename(p) in META_FILES:
                continue
            with open(p) as fh:
                d = json.load(fh)
            if "document_class" not in d:
                continue
            files += 1
            walk(d.get("fields"), "", d["document_class"]["class_name"], tier)
    return files, fields_seen, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--did", default=os.environ.get("DID_MATLAB_PATH", "/home/user/DID-matlab"))
    ap.add_argument("--enforce", action="store_true",
                    help="exit non-zero if the count has GROWN past the baseline")
    a = ap.parse_args()

    rc = 0

    # ---------- SCHEMA SIDE ----------
    # First, because it depends on nothing but this repo: if the migrator sweep
    # cannot run, these numbers still print rather than the whole report dying.
    s_files, s_fields, s_rows = sweep_schemas()

    # DENOMINATOR FIRST, UNCONDITIONALLY. A count with nothing to divide it by is
    # not evidence -- silentLoss printed zeros for two days while reading nothing.
    print("empty-node ontology_term harvest (#70) -- SCHEMA SIDE")
    print("  V_eta schema files inspected     : %d" % s_files)
    print("  field nodes walked               : %d" % s_fields)
    print("  admissible-set entries, no node  : %d" % len(s_rows))
    print("  baseline (must not increase)     : %d" % BASELINE_SCHEMAS)
    print()
    if s_files == 0:
        print("NOTHING WAS READ -- 0 schema files. Treat this as a broken scan, "
              "not as a clean result.")
        rc = 1
    elif s_rows:
        print("UNMINTED TERMS IN SCHEMAS, by value_set and carrier:")
        by_set = {}
        for r in s_rows:
            by_set.setdefault(r["root"], []).append(r)
        for root, group in sorted(by_set.items()):
            print("  %s (%d)" % (root, len(group)))
            for r in sorted(group, key=lambda x: (x["class"], x["field"], x["name"])):
                print("      %-12s %-34s %s" % (r["tier"], r["class"] + "." + r["field"],
                                                r["name"]))
        print()
    if len(s_rows) > BASELINE_SCHEMAS:
        print("FAIL: %d schema-side entries, baseline %d. A NEW unminted term was "
              "added. Either mint it, or raise BASELINE_SCHEMAS deliberately and "
              "say why." % (len(s_rows), BASELINE_SCHEMAS))
        if a.enforce:
            rc = 1
    elif len(s_rows) < BASELINE_SCHEMAS:
        print("Schema-side count has FALLEN below the baseline (%d < %d) -- terms "
              "were minted. Lower BASELINE_SCHEMAS to lock the gain in."
              % (len(s_rows), BASELINE_SCHEMAS))
        print()

    # ---------- MIGRATOR SIDE ----------
    files, rows = sweep(a.did)
    if files is None:
        print("empty-node ontology_term harvest (#70) -- MIGRATOR SIDE")
        print("  NOT READ: no +migrators_j directory under %s (pass --did)." % a.did)
        print("  This is NOT a clean migrator side. It is an unmeasured one.")
        return 1

    print("empty-node ontology_term harvest (#70) -- MIGRATOR SIDE")
    print("  migrator files inspected      : %d" % files)
    print("  emissions with an empty node  : %d" % len(rows))
    print("  baseline (must not increase)  : %d" % BASELINE_MIGRATORS)
    print()
    if files == 0:
        print("NOTHING WAS READ -- 0 migrator files. Treat this as a broken scan, "
              "not as a clean result.")
        return 1

    by_name = {}
    for r in rows:
        by_name.setdefault((r["migrator"], r["name"]), []).append(r)
    if rows:
        print("UNMINTED TERMS, by migrator and name:")
        for (mig, name), group in sorted(by_name.items()):
            label = name if name != "<computed>" else "<computed: %s>" % group[0]["expression"]
            print("  %-34s %-34s x%d" % (mig, label, len(group)))
            for r in group:
                print("      %s" % r["site"])
        print()

    if len(rows) > BASELINE_MIGRATORS:
        print("FAIL: %d emissions, baseline %d. A NEW unminted term was added. "
              "Either mint it, or raise BASELINE_MIGRATORS deliberately and say why."
              % (len(rows), BASELINE_MIGRATORS))
        if a.enforce:
            rc = 1
    elif len(rows) < BASELINE_MIGRATORS:
        print("Count has FALLEN below the baseline (%d < %d) -- terms were minted. "
              "Lower BASELINE_MIGRATORS to lock the gain in."
              % (len(rows), BASELINE_MIGRATORS))
    return rc


if __name__ == "__main__":
    sys.exit(main())
