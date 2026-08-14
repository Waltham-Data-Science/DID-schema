#!/usr/bin/env python3
"""Which of NDI's document reads name something V_eta MOVES.

WHY THIS EXISTS
---------------
The corpus gate proves documents MIGRATE and VALIDATE. It cannot prove MATLAB
can still READ them. When this tool was written nothing else was asking: no
job opened a migrated database through NDI's object API, so "the documents are
correct" and "NDI can use them" were two claims with only the first tested.

THAT IS NO LONGER TRUE, and the sentence is corrected rather than deleted
because the gap it names is what the tool exists to size.
`ndi.unittest.migrate.TestMigrateLocalEtaPRED` now opens a migrated session
through `ndi.session.dir` and asserts OBJECTS come back -- 2 daq systems, a
syncgraph carrying its rule, 2 elements rebuilt as their probe classes. So the
read path is tested for PRED's 10 v1 classes. The count below is still a SIZE
and still untriaged for everything else.

Asked by the team 2026-08-13, with the case that makes it concrete: after
migration, can `ndi.session.dir` still turn a session document into an object?
That one CAN -- `+ndi/+session/dir.m` and `+ndi/+dataset/dir.m` read either
spelling of `reference` / `local_identifier`. They were fixed because the
session rename tripped over them, not because anything pointed at them, and
they are two sites out of six hundred.

WHAT IT MEASURES, AND WHAT IT DELIBERATELY DOES NOT
---------------------------------------------------
NDI reads document fields BY PATH -- `doc.document_properties.<block>.<field>`
-- and a by-path read is exactly what a rename breaks, silently: the field
resolves to nothing and the caller carries on with an empty value. That is the
`daqsystem` lesson (a live query reading a field V_eta had dropped) generalised
to the whole read surface.

This tool does NOT decide whether any read is broken. It cannot: whether a site
matters depends on which vintage of document reaches it, and NDI still WRITES
v1, so a pure v1 workflow keeps working untouched. What it reports is the
JOIN -- every by-path read whose block is a v1 class the ledger says V_eta
renames, dissolves or consumes -- so the size and shape of the problem is a
number instead of an intuition.

REPORT-ONLY, ON PURPOSE. It lands with hundreds of sites nobody has triaged.
Arming it now would turn a job red for a condition with no owner, which trains
readers to ignore it -- this repository's own rule for a new gate, taken from
`census_digest.py`: "Arming was gated on the count already being 0."

A READ IS NOT A DEFECT AND THIS FILE NEVER SAYS IT IS. Three buckets are
reported separately because they need different work:

    AT RISK    the block is a v1 class V_eta moves, and this file shows no
               sign of handling both spellings
    GUARDED    the same file also mentions the V_eta target, so someone has
               plausibly been here -- still listed, never counted as safe,
               because "mentions it somewhere" is not "handles it here"
    STRUCTURAL `base`, `depends_on`, `document_class`, `files` -- not v1
               classes; `base.datestamp` is called out separately because
               V_eta renames it to `creation_timestamp` on EVERY document
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA_ROOT = os.path.dirname(HERE)
LEDGER = os.path.join(SCHEMA_ROOT, "schemas", "V_eta_coverage_ledger.json")

# `document_properties.<block>` and optionally `.<field>`. The block is what
# joins to the ledger; the field matters only for `base`.
READ = re.compile(r"document_properties\.([A-Za-z_]\w*)(?:\.([A-Za-z_]\w*))?")

# Not v1 document classes -- the envelope every document carries.
STRUCTURAL = {"base", "depends_on", "document_class", "files", "file",
              "ndi_document", "document_id"}

# Renamed on EVERY document, so a by-path read of it is a different kind of
# risk from a class rename: it is not confined to one family.
BASE_RENAMES = {"datestamp": "creation_timestamp"}


def find_ndi():
    for cand in (os.environ.get("NDI_MATLAB"),
                 os.path.join(os.path.dirname(SCHEMA_ROOT), "NDI-matlab"),
                 "/home/user/NDI-matlab"):
        if cand and os.path.isdir(os.path.join(cand, "src")):
            return cand
    return None


def strip_comment(line):
    """Drop a trailing MATLAB comment, respecting single-quoted strings.

    Counting comments would inflate every number here, and this project has
    already published a count that did exactly that.
    """
    out, in_str, i = [], False, 0
    while i < len(line):
        c = line[i]
        if c == "'" and not in_str:
            in_str = True
        elif c == "'" and in_str:
            in_str = False
        elif c == "%" and not in_str:
            break
        out.append(c)
        i += 1
    return "".join(out)


def load_ledger():
    with open(LEDGER) as fh:
        doc = json.load(fh)
    rows = {}
    for r in doc["rows"]:
        rows[r["v1_class"]] = r
    return rows


def moves(row):
    """Does V_eta move this class? Returns a short reason, or None."""
    if row is None:
        return None
    disp = (row.get("disposition") or "").lower()
    targets = [t for t in (row.get("targets") or []) if t != row["v1_class"]]
    if disp.startswith("persist") and not targets:
        return None
    if targets:
        return "-> " + ", ".join(targets[:3]) + ("..." if len(targets) > 3 else "")
    if disp and disp != "persist":
        return "disposition=" + disp
    return None


def scan(ndi_root, rows):
    hits = []
    files_read = 0
    for base, _dirs, names in os.walk(os.path.join(ndi_root, "src")):
        for n in names:
            if not n.endswith(".m"):
                continue
            path = os.path.join(base, n)
            files_read += 1
            try:
                with open(path, errors="replace") as fh:
                    lines = fh.read().split("\n")
            except OSError:
                continue
            text = "\n".join(lines)
            for lineno, raw in enumerate(lines, 1):
                code = strip_comment(raw)
                for m in READ.finditer(code):
                    block, field = m.group(1), m.group(2)
                    hits.append({
                        "file": os.path.relpath(path, ndi_root),
                        "line": lineno,
                        "block": block,
                        "field": field,
                        "row": rows.get(block),
                        "filetext": text,
                    })
    return hits, files_read


def classify(h):
    block, field = h["block"], h["field"]
    if block in STRUCTURAL:
        if block == "base" and field in BASE_RENAMES:
            return "BASE_RENAMED", "base.%s -> base.%s" % (field, BASE_RENAMES[field])
        return "STRUCTURAL", ""
    why = moves(h["row"])
    if why is None:
        if h["row"] is None:
            return "UNKNOWN", "not a v1 class in the ledger"
        return "STABLE", ""
    # Has anyone been here? A file that also names a target spelling has
    # plausibly been updated -- reported, never counted as handled.
    targets = [t for t in (h["row"].get("targets") or []) if t != block]
    if any(t in h["filetext"] for t in targets):
        return "GUARDED", why
    return "AT_RISK", why


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--show", type=int, default=6,
                    help="example sites to print per class (default 6)")
    args = ap.parse_args(argv)

    ndi = find_ndi()
    if ndi is None:
        print("check_ndi_read_path: NOT RUNNABLE HERE -- NDI-matlab not found "
              "(tried $NDI_MATLAB, ../NDI-matlab, /home/user/NDI-matlab). "
              "Nothing is claimed about the read path.")
        return 0
    rows = load_ledger()
    hits, files_read = scan(ndi, rows)

    buckets = {}
    for h in hits:
        kind, why = classify(h)
        h["why"] = why
        buckets.setdefault(kind, []).append(h)

    # RULE 5: the denominator, first and unconditionally.
    print("NDI READ-PATH SWEEP -- by-path document reads vs the V_eta ledger")
    print("  DENOMINATOR: %d .m file(s) under NDI-matlab src/ read, "
          "%d by-path read(s) found (comments excluded), %d ledger row(s)"
          % (files_read, len(hits), len(rows)))
    print("  NDI-matlab: %s" % ndi)
    print()
    print("  THIS DECIDES NOTHING. NDI still WRITES v1, so a pure v1 workflow is")
    print("  untouched; what is measured is the join between where NDI reads by")
    print("  path and what V_eta moves. Report-only.")
    print()
    order = ["AT_RISK", "GUARDED", "BASE_RENAMED", "UNKNOWN", "STABLE",
             "STRUCTURAL"]
    for kind in order:
        hs = buckets.get(kind) or []
        print("  %-13s %4d read(s)" % (kind, len(hs)))
    print()

    for kind in ("AT_RISK", "GUARDED", "BASE_RENAMED", "UNKNOWN"):
        hs = buckets.get(kind) or []
        if not hs:
            continue
        print("=" * 74)
        print("%s -- %d read(s)" % (kind, len(hs)))
        print("=" * 74)
        by_block = {}
        for h in hs:
            by_block.setdefault(h["block"], []).append(h)
        for block in sorted(by_block, key=lambda b: -len(by_block[b])):
            group = by_block[block]
            print("  %-24s %3d read(s)   %s"
                  % (block, len(group), group[0]["why"]))
            for h in group[:args.show]:
                print("        %s:%d" % (h["file"], h["line"]))
            if len(group) > args.show:
                print("        ... and %d more" % (len(group) - args.show))
        print()

    at_risk = len(buckets.get("AT_RISK") or [])
    print("=" * 74)
    print("%d read(s) AT RISK across %d class(es). This is a SIZE, not a defect "
          "count:" % (at_risk, len({h['block'] for h in buckets.get('AT_RISK') or []})))
    print("  whether a site breaks depends on which vintage of document reaches")
    print("  it, and that is a question about callers, not about this join.")
    print("  SETTLED BY: opening a migrated database through NDI's object API --")
    print("  TestMigrateLocalEtaPRED does that for PRED's 10 v1 classes;")
    print("  every other class here is still untested through the object API.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
