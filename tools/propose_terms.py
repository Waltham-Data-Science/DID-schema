#!/usr/bin/env python3
"""Check a batch of terms for the term registry, and print the rows to add.

The step it replaces is the hand-written one in "Adding terms for a new
dataset" (NDI-matlab Using_V2.md): a V2 import lists the terms the registry
does not hold (did2.build.unregisteredTerms), someone picks a node for each,
and then each one has to be written into schemas/V_eta_term_registry.json by
hand -- the registry's exact name for a node it already holds, the prefix in
the CURIE registry's spelling, an EMPTY term's label and definition copied
letter for letter from empty-ontology. A slip in any of those is found only
when tools/check_term_registry.py (or did2.build) refuses it.

This reads the batch, says for each term what it is, and prints the JSON rows
to append to `terms`. It writes NOTHING: the rows are pasted by whoever edits
the registry, so adding a term stays a reviewed edit (Operating Rule 1).

Input: a JSON list of objects, or a TSV file with a header row. Columns
(keys): name, node (may be empty), definition (optional), decided and
first_used_in (optional per row; --decided / --first-used-in give a default).
Other columns (such as `field` from did2.build.unregisteredTerms) are shown,
not used. Rows repeating one (name, node) are read once.

Each term gets one verdict:
  REGISTERED      the registry holds it exactly; nothing to add
  USE REGISTRY    the node is registered under another name; nothing to add,
                  the writer must use the registry's name
                  (ndi.setup.V2.registeredTerm does)
  ADD             a row is printed for it
  FAIL            it cannot be added as given; the reason says why
FAIL lines are the gate's own rules (R1..R5, R7 of check_term_registry.py),
and the whole registry plus the new rows is re-run through that tool's
check(), so a batch that passes here passes the gate.

Usage:
  python3 tools/propose_terms.py BATCH.tsv --decided "Jess Haley, 2026-10-21" \\
      --first-used-in "Smith et al. 2026 (NDI-matlab ndi.setup.conv.smith)"
Exit 0 when nothing FAILs, 1 otherwise.
"""
import argparse
import copy
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_term_registry as ctr

KEYS = ("name", "node", "definition", "status", "decided", "first_used_in", "obsolete",
        "number_unit")


def read_batch(path):
    """The batch as a list of dicts (JSON list, or TSV with a header)."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if text.lstrip().startswith("["):
        rows = json.loads(text)
    else:
        rows = list(csv.DictReader(text.splitlines(), delimiter="\t"))
    out = []
    for r in rows:
        out.append({k.strip(): (v or "").strip() if isinstance(v, str) else v
                    for k, v in r.items() if k})
    return out


def classify(batch, registry, curies, owl=None, decided="", first_used_in=""):
    """(verdicts, rows). verdicts: [(verdict, term label, message)]; rows: new entries."""
    names, spelling = ctr.prefix_index(curies)
    terms = registry.get("terms", [])

    def key_of(node):
        pre, _, local = node.partition(":")
        k = names.get(pre.lower())
        return (f"{k}:{local}" if k and local else None), k, pre, local

    by_key, by_name = {}, {}
    for t in terms:
        if t.get("node"):
            k = key_of(t["node"])[0]
            if k:
                by_key[k] = t
        by_name[t["name"].lower()] = t

    verdicts, rows, seen = [], [], set()
    for b in batch:
        name, node = b.get("name", ""), b.get("node", "")
        if (name, node) in seen:
            continue
        seen.add((name, node))
        label = f'"{name}" {node or "(no node)"}'
        if b.get("field"):
            label += f" [{b['field']}]"
        definition = b.get("definition", "")
        if not name:
            verdicts.append(("FAIL", label, "no name"))
            continue
        if node:
            k, regkey, pre, local = key_of(node)
            if not k:
                verdicts.append(("FAIL", label, (f"R4 the CURIE registry does not know the "
                                 f"prefix {pre!r}: add it (did-schema "
                                 f"schemas/did_v2/stable/CURIE_lookups_meta.json, with a "
                                 f"`spelling`; ndi-ontology-matlab for lookups) before the term")))
                continue
            if k in by_key:
                reg = by_key[k]
                if reg["name"] == name:
                    verdicts.append(("REGISTERED", label, "nothing to add"))
                else:
                    verdicts.append(("USE REGISTRY", label,
                                     (f'registered as "{reg["name"]}" ({reg["node"]}); '
                                     f"write that name (ndi.setup.V2.registeredTerm)")))
                continue
            if name.lower() in by_name:
                reg = by_name[name.lower()]
                verdicts.append(("FAIL", label, (f'R2 the name is registered for '
                                 f'{reg.get("node") or "a staged term"}: reuse that term if '
                                 f"the meaning is the same, else the ontology's label differs "
                                 f"and is the name to use")))
                continue
            note = ""
            if pre != spelling[regkey]:
                node = f"{spelling[regkey]}:{local}"
                note = f" (respelled {pre}: -> {spelling[regkey]}:)"
            if spelling[regkey] == "EMPTY":
                if owl is None:
                    note += " (R7 NOT CHECKED: no empty-ontology checkout)"
                elif local not in owl:
                    verdicts.append(("FAIL", label, (f"R7 {node} is not in empty-ontology: "
                                     f"mint it there first (src/ontology/empty-edit.owl)")))
                    continue
                else:
                    olabel, odef = owl[local]
                    if olabel != name:
                        verdicts.append(("FAIL", label, (f"R7 empty-ontology labels {node} "
                                         f"{olabel!r}; the registry name must be the label")))
                        continue
                    if definition and definition != odef:
                        verdicts.append(("FAIL", label, (f"R7 the definition differs from "
                                         f"empty-ontology's for {node}")))
                        continue
                    definition = odef or ""
                if not definition:
                    verdicts.append(("FAIL", label, "R5 an EMPTY term needs its definition"))
                    continue
            elif not definition:
                note += " (no definition given: the registry carries the ontology's)"
            status = "decided"
        else:
            if name.lower() in by_name:
                reg = by_name[name.lower()]
                if not reg.get("node") and reg["name"] == name:
                    verdicts.append(("REGISTERED", label, "staged; nothing to add"))
                elif not reg.get("node"):
                    verdicts.append(("USE REGISTRY", label,
                                     f'staged as "{reg["name"]}"; write that name'))
                else:
                    verdicts.append(("USE REGISTRY", label,
                                     (f'registered with node {reg["node"]} as "{reg["name"]}"; '
                                     f"give the node (ndi.setup.V2.registeredTerm)")))
                continue
            if not definition:
                verdicts.append(("FAIL", label, ("R5 no node and no definition: find an "
                                 "ontology term or mint an EMPTY one, or give a definition "
                                 "to register it staged")))
                continue
            status, note = "staged", " (staged: its node is still to be found or minted)"
        row = {"name": name, "node": node, "definition": definition, "status": status,
               "decided": b.get("decided") or decided,
               "first_used_in": b.get("first_used_in") or first_used_in,
               "obsolete": False, "number_unit": False}
        missing = [k for k in ("decided", "first_used_in") if not row[k]]
        if missing:
            verdicts.append(("FAIL", label, (f"no {' or '.join(missing)}: give the column or "
                             f"--{missing[0].replace('_', '-')}")))
            continue
        rows.append(row)
        verdicts.append(("ADD", label, "row printed" + note))

    # the gate's own check over the registry with the rows appended: catches
    # two rows in this batch for one node or one name (R1, R2)
    merged = {"terms": terms + rows}
    for f in ctr.check(merged, copy.deepcopy(merged), curies)[2]:
        verdicts.append(("FAIL", "the batch", f))
    return verdicts, rows


def render_rows(rows):
    """The rows as they are written in the registry (indent 2, so each entry sits at 4)."""
    text = json.dumps([{k: r[k] for k in KEYS} for r in rows], indent=2, ensure_ascii=False)
    body = text[1:-1].strip("\n")
    return "\n".join("  " + line for line in body.splitlines())


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("batch", help="JSON list or TSV (header: name, node, ...)")
    ap.add_argument("--decided", default="", help='e.g. "Jess Haley, 2026-10-21"')
    ap.add_argument("--first-used-in", default="", help="the dataset that first uses the terms")
    a = ap.parse_args(argv)

    batch = read_batch(a.batch)
    registry = ctr._load(ctr.SOURCE)
    curies = ctr._load(ctr.CURIES)
    owl, owl_path = ctr.empty_ontology_terms()
    print(f"DENOMINATOR: {len(batch)} row(s) read from {a.batch}; "
          f"{len(registry.get('terms', []))} registered term(s); "
          f"{len(curies.get('prefixes', {}))} CURIE prefix(es); "
          + (f"empty-ontology read from {owl_path}" if owl is not None
             else "NO empty-ontology checkout (EMPTY labels NOT CHECKED; set EMPTY_ONTOLOGY)"))
    verdicts, rows = classify(batch, registry, curies, owl, a.decided, a.first_used_in)
    for v, label, msg in verdicts:
        print(f"  {v:<12} {label}: {msg}")
    counts = {v: sum(1 for x in verdicts if x[0] == v)
              for v in ("REGISTERED", "USE REGISTRY", "ADD", "FAIL")}
    print("SUMMARY: " + ", ".join(f"{n} {v}" for v, n in counts.items()))
    if rows:
        print("\nROWS TO APPEND to the end of `terms` in schemas/V_eta_term_registry.json"
              " (add a comma after the entry before them):")
        print(render_rows(rows))
    return 1 if counts["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())
