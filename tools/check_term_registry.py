#!/usr/bin/env python3
"""The term registry's own gate (tenet T19; V_eta_term_registry_plan.md).

schemas/V_eta_term_registry.json lists every ontology term an NDI V2 import
writes in a vocabulary slot, and did2.build refuses a term that is not in it
(strictMode 'TermRegistry'). That only works if the list itself has ONE term
per meaning, so this checks, and fails on any of:

  R1  two entries with the same node (prefix read by key, spelling or synonym,
      ignoring case, as did2.schema.curieKey reads it)
  R2  two entries with the same name, ignoring case
  R3  a status other than `decided` (a node) or `staged` (no node yet)
  R4  a node whose prefix the CURIE registry does not know, or that is not
      written in the registry's `spelling` (V_eta_prefix_spelling_plan.md)
  R5  a term we mint (EMPTY) or a staged term with no definition
  R6  the built schemas/V_eta/stable/term_registry_meta.json listing other
      terms than the source (run tools/validate_v_eta.py)
  R7  an EMPTY term whose name or definition is not the ontology's own label
      or definition, read from an empty-ontology checkout ($EMPTY_ONTOLOGY,
      else a sibling `empty-ontology` folder). Without a checkout R7 is
      reported NOT CHECKED, never passed. A term marked `obsolete` matches
      the label either as written or with the ontology's "obsolete " prefix.
  R8  a binding variable (binding_registry_meta.json subject_statement_bindings)
      with no node while the registry holds a term of that name (the builder
      filled it until 2026-10-21; the JSON is the source now, so write it there). Variables the registry does
      not hold are LISTED, not failed: naming them is a decision.
  R9  a binding row's closed `values` list (Jess Haley, 2026-10-21) naming a
      term the registry does not hold, or holds under another name. An empty
      list is legal (nothing admitted yet). Each row is reported with its
      admissible set: a closed list (and its size), an ontology subtree,
      any registered term (node_form curie), or NOT TERM-VALUED
      (`term_valued: false`, the value is data, e.g. Gene Expression) --
      the last is not a gap.

  R10 every entry carries the same keys (name, node, definition, status,
      decided, first_used_in, obsolete): DID-matlab
      did2.schema.termIndex concatenates the rows, which fails on rows of
      different shapes. `obsolete` is false or {consider: <node>} (a term the ontology made obsolete, kept while
      something still writes it), and the node it names is registered.

It prints its denominator first and checks NOTHING against an ontology over
the network: that a node's label is the ontology's label is recorded when the
term is decided, not re-fetched on every run.

Usage: python3 tools/check_term_registry.py
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "schemas", "V_eta_term_registry.json")
BUILT = os.path.join(ROOT, "schemas", "V_eta", "stable", "term_registry_meta.json")
CURIES = os.path.join(ROOT, "schemas", "V_eta", "stable", "CURIE_lookups_meta.json")
STATUSES = {"decided", "staged"}
ROW_KEYS = ["name", "node", "definition", "status", "decided", "first_used_in",
            "obsolete"]


def prefix_index(curies):
    """lower(name) -> registry key, for each entry's key, spelling and synonyms."""
    names, spelling = {}, {}
    for key, e in curies.get("prefixes", {}).items():
        spelling[key] = e.get("spelling") or key
        for n in [key, e.get("spelling") or ""] + list(e.get("synonyms") or []):
            if n:
                names.setdefault(n.lower(), key)
    return names, spelling


def check(source, built, curies):
    terms = source.get("terms", [])
    names, spelling = prefix_index(curies)
    failures = []
    by_key, by_name = {}, {}
    staged = 0
    for i, t in enumerate(terms):
        if sorted(t) != sorted(ROW_KEYS):
            failures.append(f"R10 term {i + 1} ({t.get('name')!r}): keys {sorted(t)}, "
                            f"not the row shape {ROW_KEYS}")
        name = (t.get("name") or "").strip()
        node = (t.get("node") or "").strip()
        where = f'term {i + 1} ("{name}")'
        if not name:
            failures.append(f"{where}: no name")
        status = t.get("status")
        if status not in STATUSES:
            failures.append(f"R3 {where}: status {status!r}, not one of {sorted(STATUSES)}")
        elif status == "decided" and not node:
            failures.append(f"R3 {where}: decided but has no node")
        elif status == "staged" and node:
            failures.append(f"R3 {where}: staged but has node {node}")
        staged += status == "staged"
        if node:
            pre, _, local = node.partition(":")
            key = names.get(pre.lower())
            if not key or not local:
                failures.append(f"R4 {where}: node {node} has a prefix the CURIE registry does not know")
            else:
                if pre != spelling[key]:
                    failures.append(f"R4 {where}: node {node} is written {spelling[key]}:{local}")
                k = f"{key}:{local}"
                if k in by_key:
                    failures.append(f'R1 {where}: node {node} is already "{by_key[k]}"')
                by_key.setdefault(k, name)
            if pre.upper() == "EMPTY" and not (t.get("definition") or "").strip():
                failures.append(f"R5 {where}: an EMPTY term with no definition")
        elif not (t.get("definition") or "").strip():
            failures.append(f"R5 {where}: a staged term with no definition")
        if name:
            if name.lower() in by_name:
                failures.append(f'R2 {where}: the name is already used for {by_name[name.lower()] or "a staged term"}')
            by_name.setdefault(name.lower(), node)
    failures += _obsolete(terms, names)
    if built is None:
        failures.append("R6 the built term_registry_meta.json does not exist (run tools/validate_v_eta.py)")
    elif built.get("terms") != terms:
        failures.append("R6 the built term_registry_meta.json differs from the source (run tools/validate_v_eta.py)")
    return terms, staged, failures


def _obsolete(terms, names):
    """R10: `obsolete` is false, or {consider: <a registered node>}."""
    out, nodes = [], set()
    for t in terms:
        node = (t.get("node") or "").strip()
        if node:
            pre, _, local = node.partition(":")
            nodes.add(f"{names.get(pre.lower(), pre)}:{local}".lower())
    for i, t in enumerate(terms):
        where = f'term {i + 1} ("{t.get("name")}")'
        ob = t.get("obsolete")
        if ob is False:
            continue
        if not (isinstance(ob, dict) and set(ob) == {"consider"} and isinstance(ob["consider"], str)):
            out.append(f"R10 {where}: `obsolete` is {ob!r}, not false or {{consider: <node>}}")
            continue
        c = ob["consider"]
        pre, _, local = c.partition(":")
        if f"{names.get(pre.lower(), pre)}:{local}".lower() not in nodes:
            out.append(f"R10 {where}: obsolete, but the term to consider ({c}) is not registered")
    return out


def empty_ontology_terms():
    """{local id: (label, definition)} from an empty-ontology checkout, or None."""
    cands = [os.environ.get("EMPTY_ONTOLOGY", ""),
             os.path.join(os.path.dirname(ROOT), "empty-ontology"),
             "/home/user/empty-ontology"]
    for c in cands:
        f = os.path.join(c, "src", "ontology", "empty-edit.owl") if c else ""
        if f and os.path.exists(f):
            with open(f) as fh:
                owl = fh.read()
            labels = dict(re.findall(r'rdfs:label obo:EMPTY_(\d+) "([^"]*)"@en', owl))
            defs = dict(re.findall(r'IAO_0000115 obo:EMPTY_(\d+) "([^"]*)"', owl))
            return {k: (labels.get(k), defs.get(k)) for k in set(labels) | set(defs)}, f
    return None, None


def check_empty(terms, owl):
    """R7: every EMPTY term is named and defined as the ontology names and defines it."""
    out = []
    for t in terms:
        node = t.get("node") or ""
        if not node.upper().startswith("EMPTY:"):
            continue
        k = node.split(":", 1)[1]
        if k not in owl:
            out.append(f"R7 {node} ({t.get('name')}): not in empty-ontology")
            continue
        label, definition = owl[k]
        if t.get("obsolete") and label == "obsolete " + (t.get("name") or ""):
            label = t.get("name")
        if label != t.get("name"):
            out.append(f"R7 {node}: name {t.get('name')!r}, the ontology's label {label!r}")
        if definition != t.get("definition"):
            out.append(f"R7 {node} ({t.get('name')}): definition differs from the ontology's")
    return out


def check_bindings(terms, bindings):
    """R8. Returns (failures, report lines)."""
    by_name = {t["name"].lower(): t for t in terms if t.get("node")}
    by_node = {(t.get("node") or "").lower(): t for t in terms if t.get("node")}
    failures, report = [], []
    for row in bindings.get("subject_statement_bindings", []):
        var = row.get("variable") or {}
        name, node = var.get("name", ""), var.get("node", "")
        if node:
            t = by_node.get(node.lower())
            report.append(f"R8   {name!r}: {node} " + (
                f"registered as {t['name']!r}" if t else "NOT in the term registry"))
        elif name.lower() in by_name:
            failures.append(f"R8 binding variable {name!r} has no node, but the "
                            f"registry names it {by_name[name.lower()]['node']} "
                            f"(write that node on the row in binding_registry_meta.json)")
        else:
            report.append(f"R8   {name!r}: no node, NOT in the term registry")
    return failures, report


def check_value_sets(terms, bindings):
    """R9. Returns (failures, report lines, number of listed values)."""
    by_node = {(t.get("node") or "").lower(): t for t in terms if t.get("node")}
    failures, report, n = [], [], 0
    for row in bindings.get("subject_statement_bindings", []):
        name = (row.get("variable") or {}).get("name", "")
        if row.get("term_valued") is False:
            report.append(f"R9   {name!r}: NOT TERM-VALUED (the value is data)")
            continue
        if "values" in row:
            vals = row["values"] or []
            report.append(f"R9   {name!r}: closed list of {len(vals)} value(s)")
            for v in vals:
                n += 1
                node = (v.get("node") or "") if isinstance(v, dict) else ""
                t = by_node.get(node.lower())
                if t is None:
                    failures.append(f"R9 binding {name!r}: value {v!r} is not in the term registry")
                elif t["name"] != v.get("name"):
                    failures.append(f"R9 binding {name!r}: value {node} is named "
                                    f"{v.get('name')!r}, registered as {t['name']!r}")
        elif row.get("root_node"):
            report.append(f"R9   {name!r}: subtree {row.get('ontology')} {row['root_node']}")
        elif row.get("node_form") == "curie":
            report.append(f"R9   {name!r}: any registered term (node_form curie)")
        else:
            report.append(f"R9   {name!r}: NO ADMISSIBLE SET STATED")
    return failures, report, n


def _load(path):
    with open(path) as f:
        return json.load(f)


def main():
    source = _load(SOURCE)
    built = _load(BUILT) if os.path.exists(BUILT) else None
    curies = _load(CURIES)
    terms, staged, failures = check(source, built, curies)
    print(f"DENOMINATOR: {len(terms)} term(s) read from schemas/V_eta_term_registry.json "
          f"({len(terms) - staged} decided, {staged} staged)")
    owl, owl_path = empty_ontology_terms()
    n_empty = sum(1 for t in terms if (t.get("node") or "").upper().startswith("EMPTY:"))
    if owl is None:
        print(f"R7 NOT CHECKED: no empty-ontology checkout ({n_empty} EMPTY term(s) unread "
              f"against it; set EMPTY_ONTOLOGY)")
    else:
        print(f"R7: {n_empty} EMPTY term(s) compared with {owl_path}")
        failures = failures + check_empty(terms, owl)
    bindings_path = os.path.join(ROOT, "schemas", "V_eta", "stable",
                                 "binding_registry_meta.json")
    if os.path.exists(bindings_path):
        bindings = _load(bindings_path)
        n_var = len(bindings.get("subject_statement_bindings", []))
        bfail, breport = check_bindings(terms, bindings)
        print(f"R8: {n_var} binding variable(s) compared with the registry")
        for line in breport:
            print("  " + line)
        failures = failures + bfail
        vfail, vreport, nvals = check_value_sets(terms, bindings)
        print(f"R9: {n_var} binding row(s), {nvals} closed-list value(s) compared with the registry")
        for line in vreport:
            print("  " + line)
        failures = failures + vfail
    else:
        print("R8 NOT CHECKED: no built binding_registry_meta.json")
    n_obs = sum(1 for t in terms if t.get("obsolete"))
    print(f"R10: {len(terms)} row(s) checked for one shape; {n_obs} obsolete term(s)")
    for f in failures:
        print("  FAIL " + f)
    print(f"term registry terms read: {len(terms)}")
    if failures:
        print(f"FAIL: {len(failures)} problem(s)")
        return 1
    print("OK: one term per node and per name, every node's prefix known and spelled")
    return 0


if __name__ == "__main__":
    sys.exit(main())
