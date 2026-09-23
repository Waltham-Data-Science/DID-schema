#!/usr/bin/env python3
"""The V_eta shape panel reads the schema tree, and its inputs must agree.

WHY THIS EXISTS
---------------
The web viewer's V_eta shape panel (`web/src/veta/`, issue #72) renders the
go-forward class set straight from the files: Vite globs
`schemas/V_eta/**/*.json` and imports `schemas/V_eta_final_class_set.md` and
`schemas/V_eta_tenets.md` as raw text AT BUILD TIME. No class data is copied
into the viewer, so the bundle cannot be a stale snapshot of its own commit.

What CAN go wrong is quieter, and it is the shape this repository keeps
paying for -- a reader that parses nothing and renders an empty page that
looks like a small one:

  * the final-set document's headings change and the panel parses 0
    categories, or a category's `(n)` stops matching its list;
  * a class is built but placed in no category (the viewer would show it in an
    "in no category" bucket, but only a reader who opens the panel sees that);
  * the final-set document names a class the tree no longer has;
  * a tenet heading changes and T7 silently disappears from the tenets tab;
  * someone moves an input and edits the glob in one place but not the other;
  * someone "fixes" the panel by pasting class names into it -- the
    embedded-snapshot the issue explicitly rules out.

This gate catches every one of those before `npm run build` would ship them.

THE CONTRACT IS DERIVED, NOT RESTATED
-------------------------------------
Which files the viewer loads is read out of `web/src/veta/sources.ts` itself
(its `import.meta.glob(...)` pattern and its `?raw` imports), and how the two
markdown files are parsed is read out of `web/src/veta/grammar.json` -- the
SAME file `web/src/veta/model.ts` imports. So the gate and the viewer cannot
disagree about what a category heading or a tenet heading looks like: there is
one copy of the grammar, and both read it.

The post-build half of the gate -- that every file the glob matches reached
the bundle -- needs a built `dist/` and lives in `web/scripts/check-veta-bundle.mjs`,
run by the web workflows after `npm run build`.

RULE 5. The denominator prints first and unconditionally. Zero JSON files
matched, zero categories or zero tenets parsed is a FAILURE, never a clean
zero.

Usage:  python3 tools/check_veta_viewer.py [--root PATH]
"""

import argparse
import glob
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

VETA_DIR = os.path.join("web", "src", "veta")
SOURCES = os.path.join(VETA_DIR, "sources.ts")
GRAMMAR = os.path.join(VETA_DIR, "grammar.json")

GLOB_RE = re.compile(r'import\.meta\.glob\(\s*"([^"]+)"')
RAW_RE = re.compile(r'from\s+"([^"]+)\?raw"')
STRING_LITERAL_RE = re.compile(r'"([A-Za-z][A-Za-z0-9_]*)"')


class ContractError(Exception):
    """sources.ts or grammar.json could not be read as a contract. Never a
    soft skip: a contract that cannot be derived is not an empty contract."""


def _rel(root, path_from_module):
    """A specifier relative to web/src/veta/ -> a repository-relative path."""
    absolute = os.path.normpath(os.path.join(root, VETA_DIR, path_from_module))
    return os.path.relpath(absolute, root).replace(os.sep, "/")


def derive_contract(root):
    src_path = os.path.join(root, SOURCES)
    gram_path = os.path.join(root, GRAMMAR)
    if not os.path.exists(src_path):
        raise ContractError(f"{SOURCES} is missing")
    if not os.path.exists(gram_path):
        raise ContractError(f"{GRAMMAR} is missing")
    with open(src_path, encoding="utf-8") as fh:
        src = fh.read()
    with open(gram_path, encoding="utf-8") as fh:
        grammar = json.load(fh)
    globs = [_rel(root, g) for g in GLOB_RE.findall(src)]
    raws = [_rel(root, r) for r in RAW_RE.findall(src)]
    if len(globs) != 1:
        raise ContractError(
            f"{SOURCES} must declare exactly one import.meta.glob; found {len(globs)}")
    if len(raws) != 2:
        raise ContractError(
            f"{SOURCES} must declare exactly two ?raw imports; found {len(raws)}")
    return {"glob": globs[0], "raws": raws, "grammar": grammar}


def parse_final_class_set(text, g):
    cat_re = re.compile(g["category_heading"])
    excl_re = re.compile(g["excluded_section_heading"])
    disp_re = re.compile(g["disposition_heading"])
    any_re = re.compile(g["any_heading"])
    tok_re = re.compile(g["class_token"])
    categories, excluded = [], []
    in_excluded = False
    cur = None
    for line in text.splitlines():
        m = cat_re.match(line)
        if m:
            cur = {"symbol": m.group(1), "title": m.group(2),
                   "declared": int(m.group(3)), "classes": []}
            categories.append(cur)
            in_excluded = False
            continue
        if excl_re.match(line):
            in_excluded, cur = True, None
            continue
        if any_re.match(line):
            in_excluded, cur = False, None
            continue
        d = disp_re.match(line) if in_excluded else None
        if d:
            cur = {"disposition": d.group(1), "declared": int(d.group(2)),
                   "classes": []}
            excluded.append(cur)
            continue
        if cur is not None:
            cur["classes"].extend(tok_re.findall(line))
    return categories, excluded


def parse_tenets(text, g):
    tenet_re = re.compile(g["tenet_heading"])
    return [m.group(1) for line in text.splitlines()
            for m in [tenet_re.match(line)] if m]


def load_classes(root, glob_pattern, tiers, index_rel):
    files = sorted(
        os.path.relpath(p, root).replace(os.sep, "/")
        for p in glob.glob(os.path.join(root, glob_pattern), recursive=True))
    classes, meta = {}, set()
    for rel in files:
        with open(os.path.join(root, rel), encoding="utf-8") as fh:
            data = json.load(fh)
        if rel == index_rel:
            meta = {e["class_name"] for e in data.get("schemas", [])
                    if e.get("is_meta")}
            continue
        parts = rel.split("/")
        tier = parts[2] if len(parts) > 3 else None
        dc = data.get("document_class") if isinstance(data, dict) else None
        if tier in tiers and isinstance(dc, dict) and "fields" in data:
            classes[dc["class_name"]] = rel
    return files, classes, meta


def embedded_names(root, classes):
    """V_eta class names that appear as string literals in the viewer's own
    source. Only names with an underscore are looked for: they are distinctive
    enough that a hit is a class name and not an English word (`data`,
    `time`). The viewer must know no class names at all."""
    hits = []
    distinctive = {n for n in classes if "_" in n}
    for path in sorted(glob.glob(os.path.join(root, VETA_DIR, "*.ts*"))):
        rel = os.path.relpath(path, root).replace(os.sep, "/")
        with open(path, encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, 1):
                for name in STRING_LITERAL_RE.findall(line):
                    if name in distinctive:
                        hits.append(f"{rel}:{lineno} {name}")
    return hits


def check(root):
    c = derive_contract(root)
    g = c["grammar"]
    fcs, ten, tree = g["final_class_set"], g["tenets"], g["schema_tree"]
    failures = []

    if c["glob"] != tree["glob"]:
        failures.append(f"sources.ts globs {c['glob']!r} but grammar.json "
                        f"names {tree['glob']!r}")
    for want in (fcs["path"], ten["path"]):
        if want not in c["raws"]:
            failures.append(f"sources.ts does not import {want}?raw "
                            f"(it imports {c['raws']})")

    files, classes, meta = load_classes(root, c["glob"], set(tree["class_tiers"]),
                                        tree["index"])

    def read(rel):
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            failures.append(f"{rel} is missing")
            return ""
        with open(p, encoding="utf-8") as fh:
            return fh.read()

    categories, excluded = parse_final_class_set(read(fcs["path"]), fcs)
    tenets = parse_tenets(read(ten["path"]), ten)

    placed = {}
    for grp in categories + excluded:
        label = grp.get("symbol") or grp.get("disposition")
        if len(grp["classes"]) != grp["declared"]:
            failures.append(f"{label}: heading says {grp['declared']}, "
                            f"lists {len(grp['classes'])}")
        for n in grp["classes"]:
            if n in placed:
                failures.append(f"{n} is named twice ({placed[n]} and {label})")
            placed[n] = label
            if n not in classes:
                failures.append(f"{n} is named by {fcs['path']} ({label}) "
                                f"but is not in the tree")
    unplaced = sorted(n for n in classes if n not in placed and n not in meta)
    for n in unplaced:
        failures.append(f"{n} ({classes[n]}) is in the tree but in no category")

    symbols = [cat["symbol"] for cat in categories]
    if symbols != fcs["expected_categories"]:
        failures.append(f"categories parsed {symbols}, expected "
                        f"{fcs['expected_categories']}")
    if tenets != ten["expected_tenets"]:
        failures.append(f"tenets parsed {tenets}, expected {ten['expected_tenets']}")

    embedded = embedded_names(root, classes)
    for hit in embedded:
        failures.append(f"class name written into the viewer: {hit}")

    in_categories = sum(len(cat["classes"]) for cat in categories)
    in_excluded = sum(len(grp["classes"]) for grp in excluded)
    print(f"DENOMINATOR: {len(files)} JSON file(s) matched by {c['glob']}; "
          f"{len(classes)} class file(s) in {tree['class_tiers']}; "
          f"{len(categories)} categor(y/ies) and {len(tenets)} tenet(s) parsed")
    print(f"  placed: {in_categories} in the final set, {in_excluded} not in it, "
          f"{len(unplaced)} in no category, {len(meta)} meta file(s) excused")
    for cat in categories:
        print(f"    {cat['symbol']} {cat['title']:<48} {len(cat['classes'])}")
    for grp in excluded:
        print(f"    (not in final set) {grp['disposition']:<32} {len(grp['classes'])}")
    print(f"  class names written into the viewer source: {len(embedded)}")

    if not files:
        failures.append("the glob matched no files")
    if not classes:
        failures.append("no class files were found")
    return failures


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=REPO)
    args = ap.parse_args(argv)
    try:
        failures = check(args.root)
    except ContractError as e:
        print("DENOMINATOR: 0 JSON file(s) matched -- the contract could not be "
              "derived")
        print(f"FAIL: {e}")
        return 1
    if failures:
        print(f"FAIL: {len(failures)} disagreement(s) between the viewer's inputs:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("OK: the V_eta shape panel's inputs agree")
    return 0


if __name__ == "__main__":
    sys.exit(main())
