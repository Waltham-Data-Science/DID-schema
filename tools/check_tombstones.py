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

IT ALSO COMPARES THE `file` BLOCK, and that half exists because of a defect that
shipped on 2026-08-10. The `image_stack` tombstone declared its attachment as
`imagestack_file`; NDI writes `imageStack` -- the template's `file_list` says so
and `add_file('imageStack', ...)` appears at all EIGHT attachment sites on
origin/main (`+ndi/+setup/+conv/+haley/doImport.m:441,469,485,504,797,815,831`
and `+ndi/+setup/+conv/+babu/import.m:483`), with no exceptions.

The rule nobody had written down: a passed-through document carries its `file`
block VERBATIM, because `+did2/+convert/universalRenames.m:308` skips the
structural keys outright (`skip = {'document_class','depends_on','file','files'}`).
So a tombstone restated from an NDI template must snake_case its FIELDS and must
NOT snake_case its FILE NAMES. Getting it wrong trips both directions of the
audit at once -- it declares a file no document has AND leaves the file every
document does have undeclared.

Nothing caught it. This tool did not look at files at all; `did2.validate.fileList`
does, by exact `strcmp`, but only at corpus time and only as a report; and every
`image_stack` fixture in `testTemplateLiteralTypeTraps.m` is built with no `files`
block, so four green MATLAB tests exercised nothing.

A file divergence NEVER quarantines: `+did2/+schema/cache.m:736` allows `file`
and `files` as top-level keys and never looks inside them. That is precisely why
it is dangerous -- the failure mode is a payload that is stranded or unfindable
while every gate stays green. So the file audit is REPORT-ONLY and is NOT summed
into the BLOCKING/LOSSY/COSMETIC tiers, which grade quarantine risk. Pass
--enforce-files to make it exit non-zero once the team sets that threshold.

THE FILE ROWS AS OF 2026-08-10, EACH WRITER-CHECKED. Recorded so the next reader
does not repeat the greps, NOT as a substitute for re-running them -- the row set
is generated, this paragraph is prose, and when they disagree the tool wins.

    DENOMINATOR: 66 tombstones compared, 4 divergent
    element_epoch -> acquisition_epoch  present-but-undeclared
        `epoch_binary_data.vhsb`. SURVIVES: +ndi/+element/timeseries.m:116,268
        attach it. Already known -- migrators_j/element_epoch.m says in its own
        header that acquisition_epoch "declares `files: []` while the real
        documents carry the payload". Rides with #45/#30.
    ensemble                            present-but-undeclared
        `neuron_names.txt`. SURVIVES: +ndi/+element/ensemble.m:277 attaches it,
        and the class is a PASSTHROUGH, so this is the image_stack shape exactly.
    image                               present-but-undeclared
        `imageFile`. DOES NOT SURVIVE: the template declares it but NO writer
        attaches it -- `add_file('imageFile'` has zero hits on origin/main, and a
        bare-name sweep matches only local variables (`imageFiles`,
        `imageFileName`) in 4 files. Also moot: migrators_j.image consumes every
        did_v1 image document, so none reaches the V_eta `image` data_type.
    jrclust_clusters                    declared-but-absent
        `jrclust_output_file`. SURVIVES as an over-declaration: the template has
        no `files` block and the bare name has ZERO hits in any file on
        origin/main. Nothing writes it, so nothing is lost -- but the schema is
        wrong about what it holds.

REPORT-ONLY BY DEFAULT (exit 0). Pass --enforce to exit non-zero when any
high-risk divergence remains.

  python3 tools/check_tombstones.py
  python3 tools/check_tombstones.py --enforce
  python3 tools/check_tombstones.py --enforce-files
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
from pathlib import Path

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
    src = Path(os.path.join(REPO, "tools", "build_v_eta.py")).read_text()
    m = re.search(r"^RENAME = \{(.*?)^\}", src, re.MULTILINE | re.DOTALL)
    if not m:
        return {}
    return dict(re.findall(r'"([A-Za-z0-9_]+)"\s*:\s*"([A-Za-z0-9_]+)"', m.group(1)))


def veta_dispositions():
    """{class_name: disposition} from the built index -- 'persist' marks a class
    the go-forward schema KEEPS, which is how a name collision is spotted."""
    idx = json.loads(Path(os.path.join(VETA, "index.json")).read_text())
    return {e["class_name"]: e.get("disposition", "?") for e in idx["schemas"]}


def veta_schemas():
    """{class_name: parsed schema} for every built V_eta schema."""
    out = {}
    for p in glob.glob(os.path.join(VETA, "*", "*.json")):
        name = os.path.basename(p)[:-5]
        if name in ("index", "did_schema_meta"):
            continue
        try:
            out[name] = json.loads(Path(p).read_text())
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
        src = Path(p).read_text(errors="replace")
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


def _file_names(entries):
    """The file names in a `file` block, accepting both spellings fileList.m
    accepts: a struct with a `name`, or a bare string."""
    out = set()
    for e in entries or []:
        if isinstance(e, dict):
            if e.get("name"):
                out.add(str(e["name"]))
        elif isinstance(e, str) and e:
            out.add(e)
    return out


def veta_files(name, veta):
    """Every file name the V_eta class CHAIN declares.

    Chain, not leaf. This mirrors `did2.validate.fileList`'s `declaredFiles`
    (DID-matlab +did2/+validate/fileList.m:118-144), which walks the whole class
    chain -- so a file declared on a superclass IS declared for the subclass, and
    comparing only the leaf would invent a divergence the runtime instrument does
    not see. `sampled_body` / `opaque_body` / `data_body` all declaring
    `body_data` is the live shape this protects."""
    out = _file_names(veta.get(name, {}).get("file"))
    for sup in super_chain(name, veta):
        out |= _file_names(veta.get(sup, {}).get("file"))
    return out


def ndi_files(cls, classes, seen=None):
    """Every file name the NDI template CHAIN declares.

    Also chain, for the same reason and with a live case: `oneepoch` declares no
    `files` of its own and inherits `epoch_binary_data.vhsb` from `element_epoch`
    (and `demoNDIMock` inherits `filename1.ext` from `demoNDI`). Comparing the
    leaf alone would report V_eta's correct declaration as invented."""
    seen = seen if seen is not None else set()
    if cls in seen or cls not in classes:
        return set()
    seen.add(cls)
    out = set(classes[cls].get("files") or [])
    for sup in classes[cls].get("superclasses") or []:
        out |= ndi_files(sup, classes, seen)
    return out


def compare_file_block(cls, classes, name, veta):
    """The two directions of the file audit, SEPARATELY -- they are different
    failures and summing them hides which one happened.

    declared_but_absent     the tombstone claims a file the real document does
                            not carry. `fileList.m` names this the direction that
                            loses data: a migrator that forgets the attachment
                            produces a document whose class says the bytes are
                            there and which has none.
    present_but_undeclared  the real document carries a file the tombstone does
                            not declare. The bytes survive but nothing can find
                            them, and the schema is wrong about what it holds.

    Compared by EXACT string, deliberately, because `fileList.m:93,99` compares
    by exact `strcmp`. Normalising here would make this tool disagree with the
    instrument it exists to predict -- and normalising is what would have hidden
    `imagestack_file` vs `imageStack`."""
    theirs = ndi_files(cls, classes)
    ours = veta_files(name, veta)
    return {
        "declared_but_absent": sorted(ours - theirs),
        "present_but_undeclared": sorted(theirs - ours),
    }


def _defamily(dep_name):
    """`syncrule_id_#` -> `syncrule_id`. See the note in compare()."""
    return dep_name.removesuffix("_#")


def compare(cls, ndi, schema, name, veta):
    """Divergences between one NDI template and its V_eta tombstone."""
    theirs = set(ndi["fields"])            # already snake_cased by the extractor
    ours = set(declared_field_names(schema))
    their_deps = set(ndi["depends_on"])
    # A `<name>_#` FAMILY SATISFIES AN NDI `<name>` EDGE, and comparing the
    # literal strings said otherwise -- reporting the declaration as invented AND
    # the real edge as undeclared, two false rows for one correct declaration.
    #
    # NDI has no template syntax for a repeated edge: the template names it once
    # and the WRITER makes it plural, with `add_dependency_value_n('<name>', ...)`
    # in a loop and `dependency_value_n('<name>')` to read it back. V_eta spells
    # that `<name>_#`. Two live cases:
    #
    #   +ndi/+daq/system.m:495-497 / :48        daqmetadatareader_id
    #   +ndi/+time/syncgraph.m:850 / :891       syncrule_id
    #
    # This is the checker's documented limit in miniature -- it compares against
    # the TEMPLATE while the ground-truth rule is that the WRITER wins. Left
    # unfixed it costs more than noise: two of this report's LOSSY rows sat
    # unactioned for weeks, and a report with false rows in it is one nobody
    # reads. Normalising here does NOT hide a real divergence: a `_#` family
    # whose base name appears in no template still shows up, because the base
    # name is what gets compared.
    our_deps = {_defamily(d["name"]) for d in schema.get("depends_on", [])}
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
    ap.add_argument("--enforce-files", action="store_true",
                    help="exit non-zero if any file-block divergence remains")
    ap.add_argument("--all", action="store_true",
                    help="print COSMETIC rows in full too")
    a = ap.parse_args()

    if not os.path.exists(GT):
        sys.exit(f"missing {os.path.relpath(GT, REPO)} -- run tools/ndi_ground_truth.py first")
    gt = json.loads(Path(GT).read_text())
    veta = veta_schemas()
    disp = veta_dispositions()
    migs = migrators()
    pt = passthrough_migrators()
    renames = rename_map()

    rows, reused, file_rows = [], [], []
    skipped = {"nonprod": 0, "chain": 0, "no_tombstone": 0}
    # File-audit denominator, accumulated as we go so it cannot be reconstructed
    # (wrongly) afterwards from a different set than the one compared.
    fstat = {"compared": 0, "ndi_declares": 0, "veta_declares": 0,
             "skipped_declaring": 0}
    for cls, ndi in sorted(gt["classes"].items()):
        if cls in NONPROD:
            skipped["nonprod"] += 1
            if ndi_files(cls, gt["classes"]):
                fstat["skipped_declaring"] += 1
            continue
        if cls in CHAIN:
            skipped["chain"] += 1
            if ndi_files(cls, gt["classes"]):
                fstat["skipped_declaring"] += 1
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
            if ndi_files(cls, gt["classes"]):
                fstat["skipped_declaring"] += 1
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

        # ---- the file block, kept SEPARATE from the tiers above -------------
        # It grades a different failure (stranded/undeclared payload) and does
        # not quarantine, so folding it into BLOCKING/LOSSY/COSMETIC would make
        # both numbers mean less than either does alone.
        fstat["compared"] += 1
        fdiv = compare_file_block(cls, gt["classes"], name, veta)
        if ndi_files(cls, gt["classes"]):
            fstat["ndi_declares"] += 1
        if veta_files(name, veta):
            fstat["veta_declares"] += 1
        if fdiv["declared_but_absent"] or fdiv["present_but_undeclared"]:
            file_rows.append((tier, cls, name, fdiv))

    order = {"COLLISION": 0, "BLOCKING": 1, "LOSSY": 2, "COSMETIC": 3}
    rows.sort(key=lambda x: (order[x[0]], x[2]))
    counts = {k: sum(1 for r in rows if r[0] == k) for k in order}

    print("V_eta source-tombstone check   (ground truth: NDI {})".format(gt.get("ndi_ref", "?")))
    print()
    print(f'  classes compared : {len(gt["classes"]) - sum(skipped.values())}')
    print(f'  COLLISION        : {counts["COLLISION"]}   (a V_eta class took a did_v1 name)')
    print(f'  BLOCKING         : {counts["BLOCKING"] + counts["COLLISION"]}   (a real document CANNOT validate)')
    print(f'  LOSSY            : {counts["LOSSY"]}   (real content has nowhere to land)')
    print(f'  COSMETIC         : {counts["COSMETIC"]}   (invented declarations only)')
    if reused:
        print(f'  name reused      : {len(reused)}   (a V_eta class shares a did_v1 name, but a')
        print("                          migrator consumes every document, so none")
        print("                          can reach it: {})".format(", ".join(c for c, _ in reused)))
    print(f'  skipped          : {skipped["nonprod"]} nonprod, {skipped["chain"]} chain-mixin, {skipped["no_tombstone"]} no tombstone')
    print()

    for level, tier, cls, name, div in rows:
        if level == "COSMETIC" and not a.all:
            continue
        arrow = "" if cls == name else f"  (-> {name})"
        if snake(cls) in renames or cls in renames:
            arrow += "  [RENAMED]"
        print(f'{level:<9} {tier:<9} {cls}{arrow}')
        if div["invented_required"]:
            print("    REQUIRED but absent from the real document: {}".format(", ".join(div["invented_required"])))
        if div["undeclared_fields"]:
            print("    real fields the tombstone does NOT declare: {}".format(", ".join(div["undeclared_fields"])))
        if div["invented_fields"]:
            print("    declared but in no NDI template: {}".format(", ".join(div["invented_fields"])))
        if div["undeclared_deps"]:
            print("    real dependencies not declared: {}".format(", ".join(div["undeclared_deps"])))
        if div["invented_deps"]:
            print("    dependencies in no NDI template: {}".format(", ".join(div["invented_deps"])))
        if div["missing_supers"]:
            print("    superclasses the real document has: {}".format(", ".join(div["missing_supers"])))
        print()

    if not a.all and counts["COSMETIC"]:
        print(f'({counts["COSMETIC"]} COSMETIC row(s) hidden; pass --all to see them)\n')

    # ---- FILE BLOCK AUDIT ---------------------------------------------------
    # DENOMINATOR FIRST AND UNCONDITIONALLY (operating rule 5). Every number
    # below is printed even when it is zero, and "declares no file" is stated
    # rather than left to be inferred from a short list of rows.
    veta_any_file = sum(1 for s in veta.values() if _file_names(s.get("file")))
    absent_total = sum(len(d["declared_but_absent"]) for _, _, _, d in file_rows)
    undecl_total = sum(len(d["present_but_undeclared"]) for _, _, _, d in file_rows)
    print("FILE BLOCK AUDIT   (report-only; a file divergence never quarantines)")
    print()
    print(f'  NDI templates read              : {len(gt["classes"])}')
    print(f'  ...declaring a file (chain)     : {sum(1 for c in gt["classes"] if ndi_files(c, gt["classes"]))}')
    print(f'  V_eta schemas read              : {len(veta)}')
    print(f'  ...declaring a file             : {veta_any_file}')
    print(f'  tombstones compared for files   : {fstat["compared"]}')
    print(f'    ...NDI side declares a file   : {fstat["ndi_declares"]}')
    print(f'    ...V_eta side declares a file : {fstat["veta_declares"]}')
    print(f'  skipped (nonprod/chain/no tombstone) that DO declare a file : {fstat["skipped_declaring"]}')
    print(f'  classes with a file divergence  : {len(file_rows)}')
    print(f'    DECLARED BUT ABSENT   (names) : {absent_total}   tombstone claims a file no real document carries')
    print(f'    PRESENT BUT UNDECLARED (names): {undecl_total}   real document carries a file the tombstone does not declare')
    print()
    for tier, cls, name, fdiv in sorted(file_rows, key=lambda x: x[1]):
        arrow = "" if cls == name else f"  (-> {name})"
        print(f'FILE      {tier:<9} {cls}{arrow}')
        if fdiv["declared_but_absent"]:
            print("    declared but in no NDI template: {}".format(", ".join(fdiv["declared_but_absent"])))
        if fdiv["present_but_undeclared"]:
            print("    real files the tombstone does NOT declare: {}".format(", ".join(fdiv["present_but_undeclared"])))
        print()
    print("THE TWO DIRECTIONS ARE DIFFERENT FAILURES AND ARE NOT SUMMED. A file "
          "name is compared by EXACT string, as `did2.validate.fileList` does "
          "(fileList.m:93,99) -- NDI's spelling is NOT snake_cased, because "
          "universalRenames.m:308 skips the `file`/`files` keys outright, so a "
          "passed-through document arrives carrying NDI's own name. And READ THE "
          "WRITER before acting on a row: this compares against the TEMPLATE, "
          "and where template and writer disagree the WRITER wins -- grep "
          "`add_file(` in NDI origin/main for the name.")
    print()

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

    # THE TIER IS DERIVED FROM DID-matlab, SO WITHOUT IT THERE IS NO VERDICT.
    #
    # `passthrough` vs `migrated` is decided by whether a migrator file exists
    # (lines 189 and 204 look under $DID_MATLAB). With no checkout, EVERY class
    # reads as a passthrough -- and a passthrough's tombstone is the only thing
    # between the document and a quarantine, so six classes that are in fact
    # migrated get graded BLOCKING. The tool then prints a confident
    # "6 tombstone(s) would quarantine a real document" computed from an input
    # it could not read.
    #
    # THIS HAD BEEN RED IN CI ALL DAY -- every `tests` run on this branch since
    # 14:58 on 2026-08-11, because `tests/test_check_tombstones_files.py` calls
    # this tool DIRECTLY and so bypasses the `requires=["DID-matlab"]` that lets
    # `tools/gates.py --ci` mark a sibling-dependent step NOT RUNNABLE. The
    # local chain was green throughout, because the siblings are present here.
    #
    # A false red is not the harmless direction. A gate that cries wolf on
    # every run is a gate people stop reading, and the seventh row -- a real
    # one -- would have arrived into a report already dismissed as broken.
    #
    # So: report NOT RUNNABLE and produce no verdict. Exit 0, because an
    # unanswerable question is not a failure -- and say so loudly enough that
    # nobody reads the 0 as a pass.
    tier_source_present = os.path.isdir(DIDM)
    rc = 0
    if a.enforce and not tier_source_present:
        print()
        print("=" * 70)
        print("NOT RUNNABLE HERE -- no --enforce verdict was produced.")
        print(f"  DENOMINATOR: 0 migrator file(s) readable; DID_MATLAB={DIDM}")
        print("  The passthrough/migrated tier is read from that checkout, and")
        print("  without it every class reads as a passthrough -- so the")
        print(f'  {counts["BLOCKING"] + counts["COLLISION"]} BLOCKING row(s) above include classes that ARE migrated and')
        print("  are not quarantine risks. The grading is unsound, not clean.")
        print("  THIS IS NOT A PASS. Re-run with a DID-matlab checkout present.")
        print("=" * 70)
    elif a.enforce and (counts["BLOCKING"] or counts["COLLISION"]):
        print()
        print(f'FAIL (--enforce): {counts["BLOCKING"] + counts["COLLISION"]} tombstone(s) would quarantine a real document.')
        rc = 1
    if a.enforce_files and file_rows:
        print()
        print(f'FAIL (--enforce-files): {len(file_rows)} class(es) diverge on the file block ({absent_total} declared-but-absent, {undecl_total} present-but-undeclared).')
        rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
