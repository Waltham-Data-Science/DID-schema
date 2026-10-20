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
      terms than the source (run tools/build_v_eta.py)

It prints its denominator first and checks NOTHING against an ontology over
the network: that a node's label is the ontology's label is recorded when the
term is decided, not re-fetched on every run.

Usage: python3 tools/check_term_registry.py
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "schemas", "V_eta_term_registry.json")
BUILT = os.path.join(ROOT, "schemas", "V_eta", "stable", "term_registry_meta.json")
CURIES = os.path.join(ROOT, "schemas", "V_eta", "stable", "CURIE_lookups_meta.json")
STATUSES = {"decided", "staged"}


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
    if built is None:
        failures.append("R6 the built term_registry_meta.json does not exist (run tools/build_v_eta.py)")
    elif built.get("terms") != terms:
        failures.append("R6 the built term_registry_meta.json differs from the source (run tools/build_v_eta.py)")
    return terms, staged, failures


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
