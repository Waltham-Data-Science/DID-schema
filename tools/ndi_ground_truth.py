#!/usr/bin/env python3
"""Phase 0 of V_eta_ground_truth_plan.md -- extract the did_v1 GROUND TRUTH.

WHY THIS EXISTS
---------------
The migrators were written against DID-schema's own `V_alpha` snapshot instead of
the real NDI document templates. Where the snapshot was wrong, a migrator reads
fields the source document does not have and emits an EMPTY BUT VALID document:
an all-blank composite still has fieldnames so it passes `mustBeNonEmpty`, and an
empty depends_on edge is skipped by the reference validator. The corpus gate stays
green and the data quietly goes missing. `distance_metadata`, `ontology_image` and
`ontology_label` are confirmed instances.

So this tool makes the real thing machine-readable, and every later phase checks
against it rather than against anything on the DID side.

WHAT IT EMITS  (schemas/V_eta_ndi_ground_truth.json)
----------------------------------------------------
  classes[<ndi class name>]:
      fields            declared property-block field names (snake-cased)
      raw_fields        as spelled in the template
      depends_on        dependency names
      files             declared file names
      superclasses      referenced superclass template basenames
      path              template path @ ref
  v_alpha_divergence[]  classes whose V_alpha snapshot disagrees with the template
  migrator_reads[]      J migrators reading names no template has  (the suspects)
  writer_divergence[]   hand-recorded: shipped writer emits what the template does not

The NDI templates are read from `origin/main` via git, NOT the working tree --
same rule as tools/coverage.py, because a V_eta feature branch of NDI can lag main.

Usage:  python3 tools/ndi_ground_truth.py [--ndi /path/to/NDI-matlab]
"""

import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(REPO, "schemas", "V_eta_ndi_ground_truth.json")
DDIR = "src/ndi/ndi_common/database_documents"

# Divergences between a shipped NDI template and the writer that actually produces
# the documents. The DATA FOLLOWS THE WRITER, so the writer wins for migration --
# and each entry here is worth reporting upstream to NDI. Hand-maintained: found by
# reading the writer, which no static scan of the templates can do for us.
WRITER_DIVERGENCE = [
    {
        "class": "ontologyImage",
        "template_says": "ontologyNode (singular, a single CURIE)",
        "writer_emits": "ontologyNodes (plural) -- a comma-joined, sorted list of "
                        "ONE OR MORE CURIEs, each normalised via ndi.ontology.lookup",
        "writer": "NDI-matlab +ndi/+setup/+NDIMaker/imageDocMaker.m:80-85,122",
        "note": "The writer's own lookup query also uses the plural "
                "(ndi.query('ontologyImage.ontologyNodes', ...)), so the plural is "
                "authoritative and the template is stale. Multi-CURIE means a single "
                "ontology_term field cannot hold it.",
    },
    {
        "class": "hartley_reverse_correlation",
        "template_says": "hartley_numbers: [] (an empty matrix)",
        "writer_emits": "a struct {S, KXV, KYV, ORDER} of parallel per-frame arrays",
        "writer": "NDIcalc-vis-matlab +ndi/+calc/+vis/hartley.m:405-408",
        "note": "The V_delta conversion doc recorded it as matrix<double>, matching "
                "the template rather than the data.",
    },
    {
        "class": "ngrid",
        "template_says": "coordinates (declared, and genuinely populated)",
        "writer_emits": "coordinates -- concatenated per-axis coordinates, "
                        "size [sum(data_dim), 1]",
        "writer": "NDIcalc-vis hartley.m:443-445; NDI ndi.fun.data.mat2ngrid",
        "note": "NOT a template/writer disagreement -- recorded because the MIGRATOR "
                "(+did2/+convert/+migrators/ngrid.m) deletes it with rmfield, so real "
                "coordinate data is dropped today. Phase 3.",
    },
]


def snake(n):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", n).lower().replace("__", "_")


def ndi_templates(ndi_path):
    """Read every NDI document template from origin/main (falling back to main,
    then the working tree). Returns (dict, ref)."""
    for ref in ("origin/main", "main"):
        try:
            files = subprocess.run(
                ["git", "-C", ndi_path, "ls-tree", "-r", "--name-only", ref, "--", DDIR],
                capture_output=True, text=True, check=True).stdout.splitlines()
        except Exception:
            continue
        out = {}
        for f in files:
            if not f.endswith(".json"):
                continue
            try:
                blob = subprocess.run(["git", "-C", ndi_path, "show", "%s:%s" % (ref, f)],
                                      capture_output=True, text=True, check=True).stdout
                d = json.loads(blob)
            except Exception:
                continue
            rec = _parse(d, "%s @%s" % (f, ref))
            if rec:
                out[rec.pop("_class")] = rec
        if out:
            return out, ref
    # working-tree fallback
    out = {}
    root = os.path.join(ndi_path, DDIR)
    for dirpath, _, names in os.walk(root):
        for n in names:
            if not n.endswith(".json"):
                continue
            p = os.path.join(dirpath, n)
            try:
                d = json.load(open(p))
            except Exception:
                continue
            rec = _parse(d, os.path.relpath(p, ndi_path) + " @worktree")
            if rec:
                out[rec.pop("_class")] = rec
    return out, "worktree"


def _parse(d, path):
    dc = d.get("document_class") or {}
    cn = dc.get("class_name")
    if not cn:
        return None
    blk = d.get(dc.get("property_list_name") or cn)
    raw = sorted(blk.keys()) if isinstance(blk, dict) else []
    deps = d.get("depends_on") or []
    if isinstance(deps, dict):
        deps = [deps]
    files = ((d.get("files") or {}).get("file_list")) or []
    if isinstance(files, str):
        files = [files]
    supers = []
    for s in dc.get("superclasses") or []:
        defn = s.get("definition", "")
        supers.append(os.path.basename(defn).replace(".json", ""))
    return {
        "_class": cn,
        "fields": sorted({snake(k) for k in raw}),
        "raw_fields": raw,
        "depends_on": [x.get("name") for x in deps if isinstance(x, dict) and x.get("name")],
        "files": list(files),
        "superclasses": supers,
        "path": path,
    }


def v_alpha_divergence(truth):
    """Classes whose V_alpha snapshot disagrees with the real template. V_alpha is
    NOT authoritative -- this list exists to size the damage, not to arbitrate."""
    rows = []
    adir = os.path.join(REPO, "schemas", "V_alpha")
    if not os.path.isdir(adir):
        return rows
    by_snake = {snake(k): k for k in truth}
    for n in sorted(os.listdir(adir)):
        if not n.endswith(".json"):
            continue
        try:
            d = json.load(open(os.path.join(adir, n)))
        except Exception:
            continue
        cn = d.get("_classname") or n[:-5]
        key = by_snake.get(snake(cn))
        if not key:
            continue
        ours = {snake(f["_name"]) for f in d.get("_fields", []) if f.get("_name")}
        theirs = set(truth[key]["fields"])
        if ours != theirs:
            rows.append({
                "class": cn,
                "ndi_class": key,
                "only_in_our_snapshot": sorted(ours - theirs),
                "only_in_ndi_template": sorted(theirs - ours),
            })
    return rows


def migrator_reads(truth, did_path):
    """J migrators referencing field names that no NDI template has. Regex over the
    migrator source, so these are RANKED SUSPECTS, not confirmed bugs -- a name can
    appear in a comment. Confirm each against the template + writer before fixing."""
    rows = []
    mdir = os.path.join(did_path, "src/did/+did2/+convert/+migrators_j")
    if not os.path.isdir(mdir):
        return rows
    by_snake = {snake(k): k for k in truth}
    for n in sorted(os.listdir(mdir)):
        if not n.endswith(".m"):
            continue
        cls = n[:-2]
        key = by_snake.get(snake(cls))
        if not key:
            continue
        src = open(os.path.join(mdir, n), errors="replace").read()
        # Strip MATLAB comments and superclass/mixin cell literals before matching.
        # Both produced false positives on the first pass: `image_stack` was flagged
        # for `image_format` occurring only in a comment, and `treatment_drug` for
        # `{'dose'}` -- which is a V_eta data_type mixin passed to jStartInteraction,
        # not a did_v1 field read at all.
        src = "\n".join(re.sub(r"(?<!\.)%.*$", "", ln) for ln in src.splitlines())
        src = re.sub(r"\{\s*'[a-z0-9_']*(?:'\s*,\s*'[a-z0-9_]*)*'\s*\}", " ", src)
        theirs = set(truth[key]["fields"])
        alpha_only = _alpha_names(key) - theirs

        # TIER 1 (confident): the name appears in an idiom that can only be a READ
        # OF THE SOURCE BLOCK, and is a field our V_alpha snapshot claims but no NDI
        # template has -- i.e. the migrator provably took its vocabulary from the
        # snapshot. Deliberately NOT matching bare `x.field`: that cannot distinguish
        # reading the source from WRITING the emitted body, and it produced a false
        # positive on treatment_drug (`dose` is the V_eta output mixin, not a v1
        # field). Precision matters more than recall here -- tier 2 is the safety net.
        read = set(re.findall(r"(?:isfield|isstruct)\(\s*\w+\s*,\s*'([a-z0-9_]+)'", src))
        read |= set(re.findall(r"jGet\w*\(\s*\w+\s*,\s*'([a-z0-9_]+)'", src))
        tier1 = sorted(r for r in read if r in alpha_only)

        # TIER 2 (possible): the name occurs anywhere in the source. Catches reads
        # via helpers or dynamic field access that tier 1's idioms miss, at the cost
        # of matching comments. Confirm each against the template + writer.
        tier2 = sorted(f for f in alpha_only
                       if f not in tier1 and re.search(r"\b" + re.escape(f) + r"\b", src))

        if tier1 or tier2:
            rows.append({
                "migrator": n,
                "ndi_class": key,
                "confidence": "confirmed-vocabulary" if tier1 else "possible",
                "reads_names_absent_from_template": tier1,
                "mentions_names_absent_from_template": tier2,
                "template_fields": sorted(theirs),
            })
    return rows


def classify_divergence(ndi_path, truth, div):
    """0.3 -- for each divergent class, was this NDI CHANGING its template (real
    drift, so old-shaped documents may exist and the migrator needs two paths), or
    did we INVENT the shape (only one shape ever existed, one path)?

    Decisive test: compare our V_alpha field set against the EARLIEST version of the
    NDI template. If they never matched, the snapshot was never a copy of NDI.

    UNKNOWN is honest, not benign: usually the earliest template predates the modern
    property-block format, so the comparison is not meaningful that far back. Those
    classes need reading by hand."""
    def sh(*a):
        return subprocess.run(["git", "-C", ndi_path] + list(a),
                              capture_output=True, text=True).stdout

    first = {}
    cur = None
    for line in sh("log", "--all", "--reverse", "--diff-filter=A",
                   "--format=@%h %ai", "--name-only", "--", "*.json").splitlines():
        if line.startswith("@"):
            cur = line[1:]
        elif line.endswith(".json") and cur:
            first.setdefault(line.rsplit("/", 1)[-1][:-5], (cur, line))

    out = {}
    for cn, rec in div.items():
        alpha = set(rec["only_in_our_snapshot"]) | (
            set(truth[cn]["fields"]) - set(rec["only_in_ndi_template"]))
        hit = first.get(cn)
        if not hit:
            out[cn] = {"verdict": "UNKNOWN", "why": "no add-commit found"}
            continue
        sha, when = hit[0].split()[0], hit[0].split()[1]
        try:
            d = json.loads(sh("show", "%s:%s" % (sha, hit[1])))
            dc = d.get("document_class") or {}
            blk = d.get(dc.get("property_list_name") or dc.get("class_name"))
            if not isinstance(blk, dict):
                out[cn] = {"verdict": "UNKNOWN",
                           "why": "no property block at first version (%s)" % when}
                continue
            ff = {snake(k) for k in blk}
        except Exception:
            out[cn] = {"verdict": "UNKNOWN", "why": "unparseable first version"}
            continue
        out[cn] = {
            "verdict": "NDI-CHANGED" if ff == alpha else "DID-INVENTED",
            "why": "first NDI version %s" % when,
            "first_version_fields": sorted(ff),
        }
    return out


_ALPHA_CACHE = {}


def _alpha_names(ndi_class):
    """Field names our V_alpha snapshot claims for this class -- the vocabulary a
    migrator would have picked up if it was written from the snapshot."""
    if not _ALPHA_CACHE:
        adir = os.path.join(REPO, "schemas", "V_alpha")
        if os.path.isdir(adir):
            for n in os.listdir(adir):
                if not n.endswith(".json"):
                    continue
                try:
                    d = json.load(open(os.path.join(adir, n)))
                except Exception:
                    continue
                cn = d.get("_classname") or n[:-5]
                _ALPHA_CACHE[snake(cn)] = {
                    snake(f["_name"]) for f in d.get("_fields", []) if f.get("_name")}
    return _ALPHA_CACHE.get(snake(ndi_class), set())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ndi", default=os.environ.get("NDI_MATLAB_PATH", "/home/user/NDI-matlab"))
    ap.add_argument("--did", default=os.environ.get("DID_MATLAB_PATH", "/home/user/DID-matlab"))
    a = ap.parse_args()

    if not os.path.isdir(a.ndi):
        sys.exit("NDI-matlab not found at %s (pass --ndi)" % a.ndi)

    truth, ref = ndi_templates(a.ndi)
    if not truth:
        sys.exit("no NDI templates found under %s" % DDIR)

    div = v_alpha_divergence(truth)
    reads = migrator_reads(truth, a.did)
    prov = classify_divergence(a.ndi, truth, {r["ndi_class"]: r for r in div})
    for r in div:
        r["provenance"] = prov.get(r["ndi_class"], {"verdict": "UNKNOWN"})

    doc = {
        "_comment": (
            "GROUND TRUTH for the did_v1 side of the V_eta migration: the NDI document "
            "templates, read from %s. THIS FILE IS AUTHORITATIVE -- schemas/V_alpha and the "
            "V_delta conversion markdown are history, not evidence. Where a template and its "
            "WRITER disagree, the writer wins (see writer_divergence): the data follows the "
            "writer. Regenerate with tools/ndi_ground_truth.py. See "
            "V_eta_ground_truth_plan.md." % ref),
        "ndi_ref": ref,
        "summary": {
            "ndi_classes": len(truth),
            "v_alpha_classes_compared": len(div) + sum(
                1 for c in truth if _alpha_names(c)) - len(div),
            "v_alpha_divergences": len(div),
            "migrator_suspects": len(reads),
            "migrator_suspects_confirmed_vocabulary": sum(
                1 for r in reads if r["confidence"] == "confirmed-vocabulary"),
            "writer_divergences": len(WRITER_DIVERGENCE),
            "provenance": {v: sum(1 for r in div if r["provenance"]["verdict"] == v)
                           for v in ("DID-INVENTED", "NDI-CHANGED", "UNKNOWN")},
        },
        "writer_divergence": WRITER_DIVERGENCE,
        "v_alpha_divergence": div,
        "migrator_reads": reads,
        "classes": truth,
    }
    with open(OUT, "w") as f:
        json.dump(doc, f, indent=2, sort_keys=False)
        f.write("\n")

    print("ndi ref:                %s" % ref)
    print("NDI classes captured:   %d" % len(truth))
    print("V_alpha divergences:    %d" % len(div))
    print("migrator suspects:      %d" % len(reads))
    print("writer divergences:     %d (hand-recorded)" % len(WRITER_DIVERGENCE))
    pc = {v: sum(1 for r in div if r["provenance"]["verdict"] == v)
          for v in ("DID-INVENTED", "NDI-CHANGED", "UNKNOWN")}
    print("divergence provenance:  DID-INVENTED %d | NDI-CHANGED %d | UNKNOWN %d"
          % (pc["DID-INVENTED"], pc["NDI-CHANGED"], pc["UNKNOWN"]))
    print("wrote %s" % os.path.relpath(OUT, REPO))
    if reads:
        print("\nmigrators using vocabulary no NDI template has (confirm each individually):")
        for r in sorted(reads, key=lambda x: x["confidence"] != "confirmed-vocabulary"):
            mark = "!!" if r["confidence"] == "confirmed-vocabulary" else "? "
            names = r["reads_names_absent_from_template"] or r["mentions_names_absent_from_template"]
            print("  %s %-34s %s" % (mark, r["migrator"], names))
        print("\n  !! = read via an explicit idiom   ? = mentioned only (may be a comment)")


if __name__ == "__main__":
    main()
