#!/usr/bin/env python3
"""Per-class migration walkthrough asset for the web viewer.

WHAT THIS IS FOR. The Coverage panel answers "what is the fate of every v1
class" one row at a time. It cannot answer "what condition is THIS class in",
because the three facts that would settle it live in three different places and
only one of them reaches the browser:

    the v1 source as NDI declares it   schemas/V_eta_ndi_ground_truth.json
    what consumes it                   DID-matlab +did2/+convert/**
    what it becomes, and is it built   schemas/V_eta_coverage_ledger.json
                                       + the built schemas/V_eta tree

The ledger and the built tree are already served (public/coverage.json and
public/schemas/V_eta). The other two are not, and this tool is what puts them
where a browser can read them: web/public/class_walkthrough.json, committed, so
`npm run build` on a runner with no Python and no sibling checkout still ships
them. Nothing here is a new fact -- every field is a projection of a generated
artifact or a file:line in DID-matlab.

WHAT IT DELIBERATELY DOES NOT DO. It does not decide whether a class is
"handled". `migrator: true` already lives in the ledger, computed by
tools/coverage.py, and a SECOND opinion on that question rendered beside the
first is how two instruments come to disagree in front of a reader with no way
to tell which is right. This tool locates FILES and reports them with their line
numbers; where its own find disagrees with the ledger's boolean it says so, in
the denominator, rather than quietly winning.

Usage:  python3 tools/gen_class_walkthrough.py [--check]
  (no args)  regenerate web/public/class_walkthrough.json
  --check    regenerate in memory and exit non-zero if the committed copy differs
"""
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
LEDGER = REPO / "schemas" / "V_eta_coverage_ledger.json"
GROUND_TRUTH = REPO / "schemas" / "V_eta_ndi_ground_truth.json"
VETA_INDEX = REPO / "schemas" / "V_eta" / "index.json"
OUT = REPO / "web" / "public" / "class_walkthrough.json"

# The three convert packages tools/coverage.py reads, in the same order and for
# the same reason: a class handled in +migrators (V_zeta/older) is handled, and
# looking only at +migrators_j reports it as unhandled.
MIGRATOR_PACKAGES = ("migrators_j", "migrators", "migrators_i")
CONVERT_REL = "src/did/+did2/+convert"


def find_repo(name, env):
    """Same discovery order as tools/coverage.py: env var, /home/user, sibling."""
    for cand in (os.environ.get(env), os.path.join("/home/user", name),
                 str(REPO.parent / name)):
        if cand and os.path.isdir(cand):
            return cand
    return None


DIDM = find_repo("DID-matlab", "DID_MATLAB")


def _read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _quoted_name_re(name):
    """A MATLAB single- or double-quoted occurrence of an exact class name.

    Substring matching is what makes a sweep like this lie: `image` occurs
    inside `imageStack`, `ontologyImage` and `image_observation`, so a bare
    `in` test would attach half the convert package to the shortest class
    names in the ledger. The quotes are the word boundary MATLAB gives us.
    """
    lit = re.escape(name)
    return re.compile(r"(?<![\w.])'" + lit + r"'|(?<![\w.])\"" + lit + r"\"")


def _per_class_migrators(names):
    """Files named after the SOURCE class, across all three convert packages.

    This is the same criterion tools/coverage.py uses for its `migrator`
    boolean -- a file named for the class it consumes -- so the two can be
    compared. It is a criterion about NAMES, not about behaviour: a file that
    exists proves a migrator was written, not that it works.

    BOTH SPELLINGS ARE SEARCHED, AND THAT IS NOT DEFENSIVENESS. V_eta is
    snake_case and NDI is camelCase, and the migrator files are named in the
    V_eta spelling while the ledger keys its rows by the NDI one. Searching
    only `v1_class` found 0 files for SpikeInterfaceSortingOutputs, imageStack,
    ontologyImage, ontologyLabel and ontologyTableRow -- five classes that have
    had a migrator all along (`+migrators_j/ontology_image.m` and friends). The
    zero was a property of the query, which is the `demo_ndi` failure verbatim.
    It surfaced only because this tool cross-checks itself against the ledger's
    boolean and prints the disagreement, so the check stays.
    """
    if not DIDM:
        return []
    out = []
    seen = set()
    for pkg in MIGRATOR_PACKAGES:
        for name in names:
            if not name:
                continue
            p = Path(DIDM) / CONVERT_REL / ("+" + pkg) / (name + ".m")
            rel = f"{CONVERT_REL}/+{pkg}/{name}.m"
            if p.is_file() and rel not in seen:
                seen.add(rel)
                out.append({
                    "package": pkg,
                    "spelling": name,
                    "path": rel,
                    "lines": len(p.read_text(encoding="utf-8",
                                             errors="replace").splitlines()),
                })
    return out


def _convert_package_files():
    """Every .m directly under +did2/+convert -- the batch post-passes and the
    shared entry points, read ONCE and reused for all 102 classes."""
    if not DIDM:
        return []
    base = Path(DIDM) / CONVERT_REL
    files = []
    for p in sorted(base.glob("*.m")):
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        files.append({"name": p.stem,
                      "path": f"{CONVERT_REL}/{p.name}",
                      "lines": text.splitlines()})
    return files


def _batch_sites(convert_files, names):
    """Where a convert-package file names this class as a quoted string.

    Reported as evidence (file + line + the line itself), NOT as a claim that
    the pass consumes the class: a name can be mentioned in a comment, an
    allow-list or an error message. The reader gets the line and judges. Naming
    which pass runs, and in what order, is the corpus harness's fact and it is
    not derivable from this repository -- so this tool does not pretend to it.
    """
    pats = [(n, _quoted_name_re(n)) for n in names if n]
    out = []
    for f in convert_files:
        sites = []
        for i, line in enumerate(f["lines"], start=1):
            for spelling, pat in pats:
                if pat.search(line):
                    sites.append({"line": i,
                                  "spelling": spelling,
                                  "text": line.strip()[:200]})
                    break
        if sites:
            out.append({"pass": f["name"], "path": f["path"],
                        "sites": sites[:12], "site_count": len(sites)})
    return out


def build():
    """Assemble the asset. Returns (payload, denominator)."""
    ledger = _read_json(LEDGER)
    gt = _read_json(GROUND_TRUTH)
    index = _read_json(VETA_INDEX)

    rows = ledger["rows"]
    gt_classes = gt.get("classes", {})
    built = {e["class_name"]: {"path": e["path"],
                               "tier": e.get("tier"),
                               "maturity_level": e.get("maturity_level"),
                               "disposition": e.get("disposition"),
                               "superclasses": e.get("superclasses", [])}
             for e in index["schemas"]}

    # Side tables in the ground truth are keyed by NDI class name; invert them
    # once so a per-class lookup is a dict hit rather than a scan.
    writer_div = {}
    for w in gt.get("writer_divergence", []):
        writer_div.setdefault(w.get("class"), []).append(w)
    alpha_div = {d.get("ndi_class") or d.get("class"): d
                 for d in gt.get("v_alpha_divergence", [])}
    mig_reads = {}
    for m in gt.get("migrator_reads", []):
        mig_reads.setdefault(m.get("ndi_class"), []).append(m)

    convert_files = _convert_package_files()

    classes = {}
    with_ndi = 0
    with_migrator_file = 0
    disagree = []
    for r in rows:
        v1 = r["v1_class"]
        ndi = gt_classes.get(v1)
        if ndi:
            with_ndi += 1
        names = {v1}
        if r.get("veta_class"):
            names.add(r["veta_class"])
        migs = _per_class_migrators(sorted(names))
        if migs:
            with_migrator_file += 1
        # The ledger's boolean and this tool's file search answer the same
        # question two ways. Recorded when they differ; never reconciled here.
        if DIDM and bool(migs) != bool(r.get("migrator")):
            disagree.append({"v1_class": v1,
                             "ledger_migrator": bool(r.get("migrator")),
                             "files_found": [m["path"] for m in migs]})
        classes[v1] = {
            "ndi": ndi,
            "ndi_absent_reason": None if ndi else (
                "vhlab app/calculator class -- NDI ships no template for it "
                "(ledger source=app), so there is no NDI declaration to show"),
            "writer_divergence": writer_div.get(v1, []),
            "v_alpha_divergence": alpha_div.get(v1),
            "migrator_reads": mig_reads.get(v1, []),
            "consumers": {
                "per_class_migrators": migs,
                "convert_package_mentions": _batch_sites(convert_files, names),
            },
        }

    payload = {
        "title": "Per-class migration walkthrough",
        "description": (
            "For each did_v1 source class: what NDI actually declares, what "
            "consumes it in DID-matlab, and the built V_eta schemas its "
            "targets resolve to. A projection of generated artifacts plus a "
            "file:line search of the convert package -- no new facts."),
        "generated_by": "tools/gen_class_walkthrough.py",
        "sources": {
            "ledger": "schemas/V_eta_coverage_ledger.json",
            "ground_truth": "schemas/V_eta_ndi_ground_truth.json",
            "veta_index": "schemas/V_eta/index.json",
            "did_matlab": CONVERT_REL if DIDM else None,
        },
        "denominator": {
            "ledger_rows_read": len(rows),
            "ndi_ground_truth_classes": len(gt_classes),
            "rows_with_an_ndi_declaration": with_ndi,
            "rows_without_one": len(rows) - with_ndi,
            "built_veta_schemas": len(built),
            "convert_package_files_scanned": len(convert_files),
            "migrator_packages_searched": list(MIGRATOR_PACKAGES),
            "rows_with_a_per_class_migrator_file": with_migrator_file,
            "did_matlab_available": bool(DIDM),
            "ledger_disagreements": disagree,
        },
        "built_schemas": built,
        "classes": classes,
    }
    return payload


def serialize(payload):
    return json.dumps(payload, indent=1, sort_keys=True) + "\n"


def print_denominator(payload):
    d = payload["denominator"]
    print(f"DENOMINATOR: {d['ledger_rows_read']} ledger row(s) read, "
          f"{d['ndi_ground_truth_classes']} NDI ground-truth class(es), "
          f"{d['built_veta_schemas']} built V_eta schema(s), "
          f"{d['convert_package_files_scanned']} convert-package file(s) scanned")
    print(f"  rows carrying an NDI declaration: {d['rows_with_an_ndi_declaration']}"
          f"   without one: {d['rows_without_one']}")
    print(f"  rows with a per-class migrator FILE: "
          f"{d['rows_with_a_per_class_migrator_file']}")
    if not d["did_matlab_available"]:
        # NOT a zero. Saying "0 migrators" when the repository holding them was
        # never opened is the shape of defect this project keeps finding.
        print("  DID-matlab NOT FOUND -- consumer evidence is ABSENT, not empty. "
              "Set DID_MATLAB or place the sibling checkout at /home/user/DID-matlab.")
    if d["ledger_disagreements"]:
        print(f"  *** {len(d['ledger_disagreements'])} row(s) where this tool's "
              "file search disagrees with the ledger's `migrator` boolean:")
        for row in d["ledger_disagreements"]:
            print(f"      {row['v1_class']}: ledger={row['ledger_migrator']} "
                  f"files={row['files_found']}")
    else:
        print("  rows where this tool disagrees with the ledger's `migrator`: 0")


def main(argv):
    check = "--check" in argv
    payload = build()
    print_denominator(payload)
    text = serialize(payload)
    if check:
        if not OUT.exists():
            print(f"FAIL: {OUT.relative_to(REPO)} does not exist -- run "
                  "`python3 tools/gen_class_walkthrough.py`")
            return 1
        current = OUT.read_text(encoding="utf-8")
        if current != text:
            print(f"FAIL: {OUT.relative_to(REPO)} is STALE -- regenerate it "
                  "(`python3 tools/gen_class_walkthrough.py`) and commit the result")
            return 1
        print(f"OK: {OUT.relative_to(REPO)} matches the generated content")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print(f"WROTE {OUT.relative_to(REPO)} ({len(text)} bytes, "
          f"{len(payload['classes'])} classes)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
