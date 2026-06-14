#!/usr/bin/env python3
"""Build/verify the V_delta index auxiliaries.

Both jobs are sourced from the authoritative per-class schema files (each
class's ``document_class.superclasses``), never from ``index.json`` itself:

1. ``--fix-index`` rewrites ``schemas/V_delta/index.json`` so every entry's
   ``superclasses`` mirror equals its class file's
   ``document_class.superclasses`` (in file order). Only entries whose
   superclass *set* differs are rewritten, so the diff stays minimal.

2. (always) (re)generates ``schemas/V_delta/all_ancestors.json`` -- the
   flattened transitive-closure inheritance map ``{class_name: [ancestors]}``
   -- so consumers can look up the full isa() chain without re-deriving it
   (and without diverging from it).

The index ``superclasses`` mirror had silently dropped all non-``base`` parents
for 14 classes (e.g. ``neuron_extracellular`` was missing ``app``,
``tuningcurve_calc`` was missing ``stimulus_tuningcurve``). Any consumer that
resolved inheritance from the index rather than the class files got false
negatives. ``tests/test_index_integrity.py`` is the guard that keeps this from
recurring; this script is the reproducible fixer + closure builder.

Run from anywhere; paths resolve relative to the repo root.
"""
import argparse
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "schemas", "V_delta", "index.json")
ALL_ANCESTORS = os.path.join(ROOT, "schemas", "V_delta", "all_ancestors.json")


def superclass_names(superclasses):
    """Class-name strings from a superclasses list (handles {class_name} or str)."""
    names = []
    for sc in superclasses or []:
        if isinstance(sc, dict) and "class_name" in sc:
            names.append(sc["class_name"])
        elif isinstance(sc, str):
            names.append(sc)
    return names


def load_index():
    with open(INDEX, encoding="utf-8") as fh:
        return json.load(fh)


def file_superclasses(entry):
    """The class's own document_class.superclasses (file order, as strings)."""
    with open(os.path.join(ROOT, entry["path"]), encoding="utf-8") as fh:
        doc = json.load(fh)
    return superclass_names((doc.get("document_class") or {}).get("superclasses"))


def _closure(cls, direct, seen):
    for parent in direct.get(cls, []):
        if parent not in seen:
            seen.add(parent)
            _closure(parent, direct, seen)
    return seen


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def fix_index():
    index = load_index()
    changed = []
    for entry in index["schemas"]:
        want = file_superclasses(entry)
        have = superclass_names(entry.get("superclasses"))
        if set(have) != set(want):
            entry["superclasses"] = want
            changed.append(entry["class_name"])
    write_json(INDEX, index)
    print(f"fix-index: rewrote {len(changed)} entries: {sorted(changed)}")
    return changed


def build_all_ancestors():
    index = load_index()
    direct = {e["class_name"]: file_superclasses(e) for e in index["schemas"]}
    out = {cn: sorted(_closure(cn, direct, set())) for cn in sorted(direct)}
    write_json(ALL_ANCESTORS, out)
    print(f"all_ancestors: wrote {len(out)} classes -> {os.path.relpath(ALL_ANCESTORS, ROOT)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fix-index",
        action="store_true",
        help="rewrite index.json superclasses from the per-class schema files",
    )
    args = parser.parse_args()
    if args.fix_index:
        fix_index()
    build_all_ancestors()
