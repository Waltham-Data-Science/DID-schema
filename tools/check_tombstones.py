#!/usr/bin/env python3
"""Does every V_eta SOURCE TOMBSTONE describe the did_v1 document it has to hold?

This exists because the same defect was found ten separate times by hand.

A migrator that defers a class passes the document through UNCHANGED, so the
document arrives at validation in its did_v1 shape and is checked against the
V_eta schema of the same name -- the "tombstone". The DID validator is strict in
BOTH directions:

    did2:validation:undeclaredField   rejects a block field the schema does not
                                      declare
    mustBeNonEmpty                    rejects a declared field the real document
                                      does not carry

So a tombstone written from DID-schema's own `V_alpha` snapshot rather than from
NDI QUARANTINES THE VERY DOCUMENTS IT EXISTS TO PRESERVE. Ten tombstones were
found in that state one at a time -- simple_calc, then seven more, then two more
after that. Every one was discovered by a human reading a template. This tool
does that comparison mechanically, for the whole v1 universe at once.

REPORT-ONLY BY DEFAULT (exit 0). Pass --enforce to exit non-zero when any
high-risk divergence remains.

  python3 tools/check_tombstones.py
  python3 tools/check_tombstones.py --enforce
  python3 tools/check_tombstones.py --all      # include low-risk rows in full

Ground truth is `V_eta_ndi_ground_truth.json` (regenerate with
tools/ndi_ground_truth.py); it reads NDI `origin/main`, never a feature branch.
"""

import argparse
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
GT = os.path.join(REPO, "schemas", "V_eta_ndi_ground_truth.json")
VETA = os.path.join(REPO, "schemas", "V_eta")
DIDM = os.environ.get("DID_MATLAB", os.path.join(os.path.dirname(REPO), "DID-matlab"))

# NDI ships test/demo scaffolding as production templates; no corpus holds these.
NONPROD = {"mock", "oneepoch", "demoNDI", "demoNDIMock"}

# Chain classes that are not v1 SOURCE documents in their own right -- they are
# mixins every document inherits. A tombstone comparison on them is meaningless.
CHAIN = {"base", "app", "epochid", "ndi_document"}

# Shared helpers / non-per-class migrators, mirrored from tools/coverage.py.
MIG_HELPERS = {
    "identity", "calcCommon", "universalRenames", "Contents",
    "resolveDatasetEntities", "resolveDeferredBaths",
    "jSampledBody", "jGetCharAny", "syncrule_mapping",
}


def snake(name):
    """EXACT port of universalRenames.m's snakeCase, same as tools/ndi_ground_truth.py.

    Acronym-aware: a run of two or more uppercase letters lowercases with no
    internal separator ('MD5' -> 'md5'). A near-miss here invents field names no
    document has, and this tool exists to be trusted about exactly that -- the
    first draft used coverage.py's simpler regex and reported three tombstones as
    broken because it turned `curated_output_MD5_checksum` into
    `curated_output_m_d5_checksum`."""
    name = str(name)
    if not name:
        return name
    out = name[0].lower()
    for k in range(1, len(name)):
        c = name[k]
        if not c.isupper():
            out += c
            continue
        prev_upper = name[k - 1].isupper()
        next_lower = k + 1 < len(name) and name[k + 1].islower()
        if (not prev_upper or next_lower) and out[-1] != "_":
            out += "_" + c.lower()
        else:
            out += c.lower()
    return out


def rename_map():
    """did_v1 class name -> V_eta class name, read from build_v_eta.py's RENAME.

    WITHOUT THIS THE CHECKER HAS A HOLE EXACTLY WHERE IT MATTERS. It resolves an
    NDI class to its V_eta counterpart BY NAME, so any class V_eta renamed simply
    fails to resolve and drops into the "no tombstone" skip list -- silently, and
    counted as nothing to check.

    `element_epoch` -> `acquisition_epoch` is the case that exposed it. The did_v1
    class has TWO scalar fields (`epoch_clock`, `t0_t1`); the V_eta class has four
    structured groups (`clocks`, `axes`, `channels`, `storage`). A deliberately
    reshaped, live v1 class -- the single thing most worth comparing -- was the one
    the tool could not see.

    Parsed from the source rather than duplicated here, so the two cannot drift.
    """
    src = open(os.path.join(REPO, "tools", "build_v_eta.py")).read()
    m = re.search(r"^RENAME = \{(.*?)^\}", src, re.M | re.S)
    if not m:
        return {}
    return dict(re.findall(r'"([A-Za-z0-9_]+)"\s*:\s*"([A-Za-z0-9_]+)"', m.group(1)))


def veta_dispositions():
    """{class_name: disposition} from the built index -- 'persist' marks a class
    the go-forward schema KEEPS, which is how a name collision is spotted."""
    idx = json.load(open(os.path.join(VETA, "index.json")))
    return {e["class_name"]: e.get("disposition", "?") for e in idx["schemas"]}


def veta_schemas():
    """{class_name: parsed schema} for every built V_eta schema."""
    out = {}
    for p in glob.glob(os.path.join(VETA, "*", "*.json")):
        name = os.path.basename(p)[:-5]
        if name in ("index", "did_schema_meta"):
            continue
        try:
            out[name] = json.load(open(p))
        except ValueError:
            continue
    return out


def migrators():
    """{source_class_name: package} for every bespoke per-class migrator."""
    out = {}
    for pkg in ("migrators_j", "migrators_i", "migrators"):
        base = os.path.join(DIDM, "src/did/+did2/+convert/+" + pkg)
        for p in glob.glob(os.path.join(base, "*.m")):
            cn = os.path.basename(p)[:-2]
            if cn in MIG_HELPERS:
                continue
            out.setdefault(cn, pkg)
    return out


def passthrough_migrators():
    """Source classes whose migrators_j entry is a DELIBERATE passthrough --
    detected by the guard-then-`bodies = {preBody}` shape those migrators share.
    For these the tombstone is load-bearing exactly as it is for an unmigrated
    class, so they belong in the same risk tier."""
    out = set()
    base = os.path.join(DIDM, "src/did/+did2/+convert/+migrators_j")
    for p in glob.glob(os.path.join(base, "*.m")):
        cn = os.path.basename(p)[:-2]
        if cn in MIG_HELPERS:
            continue
        src = open(p, errors="replace").read()
        body = "\n".join(re.sub(r"(?<!\.)%.*$", "", ln) for ln in src.splitlines())
        # the whole function body is the guard plus an unconditional passthrough
        if re.search(r"bodies\s*=\s*\{\s*preBody\s*\}\s*;", body) \
                and not re.search(r"document_class\s*=\s*(struct|classBlock)", body) \
                and "jStartInteraction" not in body:
            out.add(cn)
    return out


def declared_field_names(schema):
    return [f["name"] for f in schema.get("fields", [])]


def required_field_names(schema):
    return [f["name"] for f in schema.get("fields", []) if f.get("mustBeNonEmpty")]


def super_chain(name, veta, seen=None):
    """The TRANSITIVE superclass closure of a V_eta class.

    Direct superclasses are not enough. V_eta re-parents freely -- `session` is
    declared `entity`, and `entity` is itself `base` -- so comparing only the
    immediate list reports `base` as missing on a class that plainly has it.
    Every one of those would be a false alarm, and a checker that cries wolf
    about deliberate remodelling is worse than no checker."""
    seen = seen if seen is not None else set()
    for s in veta.get(name, {}).get("document_class", {}).get("superclasses", []):
        sn = s["class_name"]
        if sn in seen:
            continue
        seen.add(sn)
        super_chain(sn, veta, seen)
    return seen


def compare(cls, ndi, schema, name, veta):
    """Divergences between one NDI template and its V_eta tombstone."""
    theirs = set(ndi["fields"])            # already snake_cased by the extractor
    ours = set(declared_field_names(schema))
    their_deps = set(ndi["depends_on"])
    our_deps = {d["name"] for d in schema.get("depends_on", [])}
    their_sup = {snake(s) for s in ndi["superclasses"]}
    our_sup = super_chain(name, veta)

    # A required field the real document lacks is the worst case: it does not
    # merely fail to describe the document, it GUARANTEES a quarantine.
    required_missing = sorted(set(required_field_names(schema)) - theirs)
    return {
        "undeclared_fields": sorted(theirs - ours),   # -> undeclaredField
        "invented_fields": sorted(ours - theirs),     # not in any NDI template
        "invented_required": required_missing,        # guaranteed quarantine
        "undeclared_deps": sorted(their_deps - our_deps),
        "invented_deps": sorted(our_deps - their_deps),
        "missing_supers": sorted(their_sup - our_sup),
    }


def risk(div, tier, collision):
    """BLOCKING  a real did_v1 document reaching this schema CANNOT validate.
       COLLISION a V_eta TARGET class has taken a did_v1 class name; the schema
                 under that name describes something else entirely.
       LOSSY     real content is declared nowhere, so it has no landing place.
       COSMETIC  the tombstone over-declares, but nothing real is turned away.

    `invented_required` is only BLOCKING on the passthrough tier. On the migrated
    tier the migrator SYNTHESISES the body before validation -- distance_metadata's
    nested `endpoints` is a deliberate reshape, not a defect -- so flagging it
    there would be a false alarm."""
    if collision:
        return "COLLISION"
    if not any(div.values()):
        return None
    if tier == "passthrough" and (div["invented_required"]
                                  or div["undeclared_fields"]
                                  or div["missing_supers"]):
        return "BLOCKING"
    if div["undeclared_fields"] or div["undeclared_deps"] or div["missing_supers"]:
        return "LOSSY"
    return "COSMETIC"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--enforce", action="store_true",
                    help="exit non-zero if any BLOCKING row remains")
    ap.add_argument("--all", action="store_true",
                    help="print COSMETIC rows in full too")
    a = ap.parse_args()

    if not os.path.exists(GT):
        sys.exit("missing %s -- run tools/ndi_ground_truth.py first"
                 % os.path.relpath(GT, REPO))
    gt = json.load(open(GT))
    veta = veta_schemas()
    disp = veta_dispositions()
    migs = migrators()
    pt = passthrough_migrators()
    renames = rename_map()

    rows, reused = [], []
    skipped = {"nonprod": 0, "chain": 0, "no_tombstone": 0}
    for cls, ndi in sorted(gt["classes"].items()):
        if cls in NONPROD:
            skipped["nonprod"] += 1
            continue
        if cls in CHAIN:
            skipped["chain"] += 1
            continue
        # Resolve through the RENAME map as well as by name, so a class V_eta
        # renamed is still compared instead of vanishing into the skip list.
        name = cls if cls in veta else snake(cls)
        if name not in veta and snake(cls) in renames:
            name = renames[snake(cls)]
        if name not in veta and cls in renames:
            name = renames[cls]
        if name not in veta:
            # No tombstone at all. Either phase-8 deleted (the class is provably
            # consumed) or never homed -- coverage.py owns that question, not us.
            skipped["no_tombstone"] += 1
            continue
        if name in pt:
            tier = "passthrough"
        elif name in migs or cls in migs:
            tier = "migrated"
        else:
            tier = "passthrough"      # no migrator -> reaches validation as-is
        div = compare(cls, ndi, veta[name], name, veta)
        # A NAME COLLISION: V_eta KEEPS a class of this name, but what it declares
        # has NOTHING in common with the did_v1 class of the same name -- so the
        # go-forward schema has taken the name for a different concept, and a real
        # v1 document arriving under it meets a schema describing something else.
        ours = set(declared_field_names(veta[name]))
        theirs = set(ndi["fields"])
        # ...and only when the class is a PASSTHROUGH. If a migrator consumes
        # every document of the v1 class, none can ever reach the schema under
        # that name, so the shared name is harmless -- that is how the did_v1
        # `image` collision was resolved (migrators_j.image folds it into an
        # image_observation) rather than by renaming the V_eta data_type.
        collision = (tier == "passthrough" and disp.get(name) == "persist"
                     and ours and theirs and not (ours & theirs))
        if disp.get(name) == "persist" and ours and theirs and not (ours & theirs) \
                and tier != "passthrough":
            reused.append((cls, name))
        r = risk(div, tier, collision)
        if r:
            rows.append((r, tier, cls, name, div))

    order = {"COLLISION": 0, "BLOCKING": 1, "LOSSY": 2, "COSMETIC": 3}
    rows.sort(key=lambda x: (order[x[0]], x[2]))
    counts = {k: sum(1 for r in rows if r[0] == k) for k in order}

    print("V_eta source-tombstone check   (ground truth: NDI %s)"
          % gt.get("ndi_ref", "?"))
    print()
    print("  classes compared : %d" % (len(gt["classes"]) - sum(skipped.values())))
    print("  COLLISION        : %d   (a V_eta class took a did_v1 name)" % counts["COLLISION"])
    print("  BLOCKING         : %d   (a real document CANNOT validate)" % (counts["BLOCKING"] + counts["COLLISION"]))
    print("  LOSSY            : %d   (real content has nowhere to land)" % counts["LOSSY"])
    print("  COSMETIC         : %d   (invented declarations only)" % counts["COSMETIC"])
    if reused:
        print("  name reused      : %d   (a V_eta class shares a did_v1 name, but a"
              % len(reused))
        print("                          migrator consumes every document, so none")
        print("                          can reach it: %s)"
              % ", ".join(c for c, _ in reused))
    print("  skipped          : %d nonprod, %d chain-mixin, %d no tombstone"
          % (skipped["nonprod"], skipped["chain"], skipped["no_tombstone"]))
    print()

    for level, tier, cls, name, div in rows:
        if level == "COSMETIC" and not a.all:
            continue
        arrow = "" if cls == name else "  (-> %s)" % name
        if snake(cls) in renames or cls in renames:
            arrow += "  [RENAMED]"
        print("%-9s %-9s %s%s" % (level, tier, cls, arrow))
        if div["invented_required"]:
            print("    REQUIRED but absent from the real document: %s"
                  % ", ".join(div["invented_required"]))
        if div["undeclared_fields"]:
            print("    real fields the tombstone does NOT declare: %s"
                  % ", ".join(div["undeclared_fields"]))
        if div["invented_fields"]:
            print("    declared but in no NDI template: %s"
                  % ", ".join(div["invented_fields"]))
        if div["undeclared_deps"]:
            print("    real dependencies not declared: %s"
                  % ", ".join(div["undeclared_deps"]))
        if div["invented_deps"]:
            print("    dependencies in no NDI template: %s"
                  % ", ".join(div["invented_deps"]))
        if div["missing_supers"]:
            print("    superclasses the real document has: %s"
                  % ", ".join(div["missing_supers"]))
        print()

    if not a.all and counts["COSMETIC"]:
        print("(%d COSMETIC row(s) hidden; pass --all to see them)\n"
              % counts["COSMETIC"])

    print("HOW TO READ THE TIERS. `passthrough` means the document reaches "
          "validation in its did_v1 shape -- either no migrator exists, or the "
          "migrator deliberately defers -- so the tombstone is the ONLY thing "
          "standing between a real document and a quarantine. `migrated` means a "
          "migrator transforms the body, so a divergence may be a deliberate "
          "reshape rather than a defect; confirm before changing anything.")
    print()
    print("A green run is NOT proof the corpus is safe: several of these classes "
          "have no writer in any repository, so no corpus has ever exercised "
          "them. This checks the SCHEMA against the TEMPLATE, which is the point "
          "-- it is what a green corpus could never tell you.")

    if a.enforce and (counts["BLOCKING"] or counts["COLLISION"]):
        print()
        print("FAIL (--enforce): %d tombstone(s) would quarantine a real document."
              % (counts["BLOCKING"] + counts["COLLISION"]))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
