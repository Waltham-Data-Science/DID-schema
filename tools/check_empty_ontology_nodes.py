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
Sweeps the J migrators for `jOntologyTerm('', <name>)` and reports each emission
grouped by (migrator, name). The count is CI-gated against BASELINE below: it may
FALL freely, and any INCREASE fails, so minting terms is always allowed and adding
new unminted ones is a deliberate act that has to move the number.

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
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

# The count at the time the gate was introduced (2026-08-09). It may FALL freely;
# an increase fails under --enforce. Lower it when terms are minted -- that is the
# point of the ratchet.
BASELINE = 33

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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--did", default=os.environ.get("DID_MATLAB_PATH", "/home/user/DID-matlab"))
    ap.add_argument("--enforce", action="store_true",
                    help="exit non-zero if the count has GROWN past the baseline")
    a = ap.parse_args()

    files, rows = sweep(a.did)
    if files is None:
        sys.exit("no +migrators_j directory under %s (pass --did)" % a.did)

    # DENOMINATOR FIRST, UNCONDITIONALLY. A count with nothing to divide it by is
    # not evidence -- silentLoss printed zeros for two days while reading nothing.
    print("empty-node ontology_term harvest (#70)")
    print("  migrator files inspected      : %d" % files)
    print("  emissions with an empty node  : %d" % len(rows))
    print("  baseline (must not increase)  : %d" % BASELINE)
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

    if len(rows) > BASELINE:
        print("FAIL: %d emissions, baseline %d. A NEW unminted term was added. "
              "Either mint it, or raise BASELINE deliberately and say why."
              % (len(rows), BASELINE))
        return 1 if a.enforce else 0
    if len(rows) < BASELINE:
        print("Count has FALLEN below the baseline (%d < %d) -- terms were minted. "
              "Lower BASELINE to lock the gain in." % (len(rows), BASELINE))
    return 0


if __name__ == "__main__":
    sys.exit(main())
