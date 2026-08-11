#!/usr/bin/env python3
"""Stamp NDI's own `mustbenotempty` verdict onto the matching V_eta edge.

WHY THIS EXISTS
---------------
`did2.validate.silentLoss/requiredDependencies` returns names only for edges
declared `mustBeNonEmpty` somewhere in the V_eta class chain. So wherever V_eta
RELAXED an edge NDI requires, that edge is OUT OF SCOPE for the empty-edge
census entirely -- it is not counted as zero, it is not looked at. The corpus's
"0 empty required edges across 627,526 documents" is therefore SILENT about
that whole set rather than reassuring about it. This module makes NDI's verdict
visible to the census so the set can be measured.

The motivating case, and the reason it is not about enforcement:

    NDI    ndi_common/schema_documents/data/ontologyLabel_schema.json
           {"name": "document_id", "mustbenotempty": 1}
    V_eta  schemas/V_eta/stable/ontology_label.json
           {"name": "document_id", "mustBeNonEmpty": false}  -> base

`ontology_label` is `disposition: retire` -- a GUARDED PASSTHROUGH deferred to
the NDI second pass, ~7,007 documents. `document_id` is the JOIN KEY that pass
needs (label -> document_id -> image_stack -> subject). If the edge is empty on
some fraction, the dissolution cannot resolve those documents, and we would
find that out only after building it. The census is an INPUT TO PLANNING.

WHAT THIS CAN AND CANNOT DO
---------------------------
It writes ONE new key, `ndi_mustBeNonEmpty`, on a `depends_on` entry. It never
reads, writes or derives `mustBeNonEmpty`. Both consumers of required-ness --
`did2.schema.cache/requiredDependencies` (which the armed
`DID_ENFORCE_REQUIRED_DEPENDENCIES` gate calls) and
`did2.validate.silentLoss/requiredDependencies` -- test `dep.mustBeNonEmpty`
and nothing else, and both ignore unrecognised keys on a dependency entry. So
this cannot move the corpus's 0-quarantined / 0-orphan result in either
direction.

THREE STATES, NOT TWO
---------------------
The key is written when NDI STATED a verdict, carrying NDI's value -- true or
false. It is ABSENT when NDI stated nothing, and absence is a real condition
with three distinct causes, all counted separately below:

  * the V_eta class has no did_v1 source (dissolved, phase-8 deleted, or
    renamed past the RENAME map);
  * the source's NDI schema document is in the JSON Schema draft-2019-09 form,
    which carries no `mustbenotempty` anywhere (5 of NDI's 91);
  * V_eta renamed or dropped the edge, so no name matched.

Reading absence as `false` would turn "NDI never said" into "NDI agrees with
us" -- the reassuring direction, and the error this repository keeps making.

WHY A BUILD-TIME STAMP RATHER THAN A RUNTIME READ OF THE GROUND-TRUTH JSON
--------------------------------------------------------------------------
The alternative was to have `silentLoss` read `V_eta_ndi_ground_truth.json` at
runtime. The deciding factor is the RENAME map. Resolving an NDI camelCase
class to its V_eta snake_case class is what `build_v_eta.py` knows and what
nothing on the MATLAB side does: `element_epoch` -> `acquisition_epoch` already
hid a whole class from an earlier tombstone audit for exactly this reason, and
`check_tombstones.py` has to PARSE the RENAME dict out of `build_v_eta.py`'s
source to avoid repeating the hole. A runtime read would put a THIRD copy of
that mapping in MATLAB, where it could drift from the two that exist. It would
also make the validator do file IO against a sibling repository that is only
present in the corpus job, and re-implement the class-chain walk it already
gets from the schema cache for free.

With the stamp, the fact arrives in the schema cache like every other
declaration and `silentLoss` reads it off the class chain exactly as it reads
`mustBeNonEmpty`: one source of truth, one code path, no new IO.
"""

import glob
import json
import os


def ndi_snake(n):
    """EXACT port of universalRenames.m's snakeCase -- acronym-aware.

    The same function `tools/ndi_ground_truth.py` and `tools/check_tombstones.py`
    carry, for the same reason: a near-miss invents names no document has
    (`curated_output_MD5_checksum` -> `curated_output_m_d5_checksum`), and a
    comparison against an invented name reports a divergence that is a property
    of the transform.
    """
    n = str(n)
    if not n:
        return n
    out = n[0].lower()
    for k in range(1, len(n)):
        c = n[k]
        if not c.isupper():
            out += c
            continue
        prev_upper = n[k - 1].isupper()
        next_lower = k + 1 < len(n) and n[k + 1].islower()
        if (not prev_upper or next_lower) and out[-1] != "_":
            out += "_" + c.lower()
        else:
            out += c.lower()
    return out


#: The key written on a V_eta `depends_on` entry. Named so it can never be
#: confused with `mustBeNonEmpty` by a case-insensitive reader or a careless
#: grep -- it carries a different repository's opinion and gates nothing.
MARKER = "ndi_mustBeNonEmpty"

#: Every counter the stamp reports, initialised to zero so the report shape is
#: fixed whether or not anything was found. A missing counter and a zero one
#: must not print differently by accident.
COUNTERS = (
    "ndi_classes_read",
    "ndi_classes_with_a_verdict",
    "ndi_required_edges",
    "ndi_optional_edges",
    "classes_resolved_to_v_eta",
    "classes_with_no_v_eta_class",
    "edges_lost_to_unresolved_class",
    "edges_matched_by_name",
    "edges_with_no_v_eta_edge",
    "edges_inherited_not_stamped",
    "stamped_required",
    "stamped_optional",
    "divergences",
)


def stamp_ndi_required(veta_dir, gt_path, rename, tiers, meta_files):
    """Stamp NDI's verdict onto matching V_eta edges; return the denominators.

    VETA_DIR    the built schema tree (mutated in place)
    GT_PATH     schemas/V_eta_ndi_ground_truth.json
    RENAME      build_v_eta.py's did_v1 -> V_eta class rename map
    TIERS       schema tier folder names
    META_FILES  basenames that are not document classes

    Returns a dict carrying every counter in COUNTERS plus:

      ground_truth_readable   0 when the extract could not be parsed. NOT a
                              silent zero: with it at 0 every other number is a
                              property of this run, and the caller says so.
      unresolved_classes      NDI class names with no V_eta counterpart --
                              their edges are NOT MEASURED, not zero.
      divergence_rows         'class.edge' for each stamped-required edge that
                              V_eta declares optional. The census's subject.

    THE COUNTERS ARE THE POINT (operating rule 5). A zero in the divergence row
    can mean four different things -- nothing diverges / no class resolved / no
    edge name matched / the ground truth was unreadable -- and only these
    numbers tell them apart.
    """
    d = {k: 0 for k in COUNTERS}
    d["unresolved_classes"] = []
    d["divergence_rows"] = []
    try:
        with open(gt_path) as f:
            gt = json.load(f)
    except Exception:
        d["ground_truth_readable"] = 0
        return d
    d["ground_truth_readable"] = 1

    files, by_class = {}, {}
    for tier in tiers:
        for p in glob.glob(os.path.join(veta_dir, tier, "*.json")):
            if os.path.basename(p) in meta_files:
                continue
            try:
                with open(p) as f:
                    doc = json.load(f)
                cn = doc["document_class"]["class_name"]
            except Exception:
                continue
            files[cn] = p
            by_class[cn] = doc
    supers = {cn: [s["class_name"] for s in doc["document_class"]["superclasses"]]
              for cn, doc in by_class.items()}

    def ancestors(cn, seen=()):
        out = []
        for s in supers.get(cn, []):
            if s in seen:
                continue
            out.append(s)
            out += ancestors(s, tuple(seen) + (cn,))
        return out

    touched = set()
    for ndi_cn, rec in sorted((gt.get("classes") or {}).items()):
        d["ndi_classes_read"] += 1
        verdicts = rec.get("depends_on_required") or {}
        if not verdicts:
            continue
        d["ndi_classes_with_a_verdict"] += 1
        d["ndi_required_edges"] += sum(1 for v in verdicts.values() if v)
        d["ndi_optional_edges"] += sum(1 for v in verdicts.values() if not v)
        # RESOLVE THROUGH THE RENAME MAP, not by name alone. Skipping this is
        # what hid element_epoch -> acquisition_epoch from an earlier audit:
        # a renamed class simply fails to resolve and is counted as nothing to
        # check, silently.
        target = None
        for cand in (ndi_cn, ndi_snake(ndi_cn),
                     rename.get(ndi_snake(ndi_cn)), rename.get(ndi_cn)):
            if cand and cand in by_class:
                target = cand
                break
        if target is None:
            d["classes_with_no_v_eta_class"] += 1
            d["edges_lost_to_unresolved_class"] += len(verdicts)
            d["unresolved_classes"].append(ndi_cn)
            continue
        d["classes_resolved_to_v_eta"] += 1
        doc = by_class[target]
        own = {e["name"]: e for e in doc.get("depends_on", [])}
        anc_names = set()
        for a in ancestors(target):
            anc_names |= {e["name"]
                          for e in by_class.get(a, {}).get("depends_on", [])}
        for raw_name, req in sorted(verdicts.items()):
            name = ndi_snake(raw_name)
            if name not in own:
                if name in anc_names:
                    # NOT STAMPED, ON PURPOSE. The NDI fact belongs to ONE
                    # class; stamping it on a shared superclass would assert it
                    # of every subclass, including classes with no did_v1
                    # source at all. Counted so the omission is visible.
                    d["edges_inherited_not_stamped"] += 1
                else:
                    d["edges_with_no_v_eta_edge"] += 1
                continue
            d["edges_matched_by_name"] += 1
            own[name][MARKER] = bool(req)
            touched.add(target)
            if req:
                d["stamped_required"] += 1
                if not own[name].get("mustBeNonEmpty", False):
                    d["divergences"] += 1
                    d["divergence_rows"].append("%s.%s" % (target, name))
            else:
                d["stamped_optional"] += 1

    for cn in sorted(touched):
        with open(files[cn], "w") as f:
            json.dump(by_class[cn], f, indent=4)
            f.write("\n")
    d["unresolved_classes"] = sorted(d["unresolved_classes"])
    d["divergence_rows"] = sorted(d["divergence_rows"])
    return d


def render_stamp_report(d):
    """The build-time report. DENOMINATOR FIRST and unconditionally."""
    out = ["",
           "NDI REQUIRED-NESS STAMP (`%s`) -- report-only; no mustBeNonEmpty "
           "value is read or written" % MARKER]
    if not d.get("ground_truth_readable"):
        out += ["  *** V_eta_ndi_ground_truth.json COULD NOT BE READ. Nothing",
                "  *** was stamped, so every count downstream is a property of",
                "  *** this build, not of the data. Run tools/ndi_ground_truth.py."]
        return out + [""]
    out.append("  DENOMINATOR: %d NDI class(es) read; %d state required-ness "
               "for at least one edge"
               % (d["ndi_classes_read"], d["ndi_classes_with_a_verdict"]))
    out.append("  DENOMINATOR: %d NDI-REQUIRED edge(s) + %d NDI-optional "
               "edge(s) declared"
               % (d["ndi_required_edges"], d["ndi_optional_edges"]))
    out.append("  resolved to a V_eta class: %d   NO V_eta class: %d "
               "(%d edge(s) NOT MEASURED)"
               % (d["classes_resolved_to_v_eta"],
                  d["classes_with_no_v_eta_class"],
                  d["edges_lost_to_unresolved_class"]))
    out.append("  edges matched by name: %d   inherited (not stamped): %d   "
               "no V_eta edge of that name: %d"
               % (d["edges_matched_by_name"],
                  d["edges_inherited_not_stamped"],
                  d["edges_with_no_v_eta_edge"]))
    out.append("  stamped: %d required, %d optional -- of which %d DIVERGE "
               "(NDI requires it, V_eta does not)"
               % (d["stamped_required"], d["stamped_optional"],
                  d["divergences"]))
    if d["edges_matched_by_name"] == 0:
        out += ["  *** NO EDGE MATCHED BY NAME AT ALL. The divergence count",
                "  *** above is a property of the name matching, not of the",
                "  *** schemas. Do NOT read it as agreement with NDI."]
    if d["unresolved_classes"]:
        out.append("  NOT MEASURED, no V_eta class: %s"
                   % ", ".join(d["unresolved_classes"]))
    return out + [""]
