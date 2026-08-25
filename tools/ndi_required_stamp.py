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
    # -- THE V_eta SIDE'S OWN DENOMINATOR. `v_eta_files_seen` is what the tier
    #    glob offered; `v_eta_classes_read` is what was actually parsed. They
    #    were one number by construction until 2026-08-11, because an
    #    unreadable schema file silently became an NDI class with no V_eta
    #    counterpart -- an accounted-looking bucket.
    "v_eta_files_seen",
    "v_eta_files_unreadable",
    "v_eta_classes_read",
    "ndi_classes_read",
    "ndi_classes_with_a_verdict",
    "ndi_required_edges",
    "ndi_optional_edges",
    "edges_carrying_an_ndi_verdict",
    "classes_resolved_to_v_eta",
    "classes_with_no_v_eta_class",
    "edges_lost_to_unresolved_class",
    "edges_matched_by_name",
    "edges_with_no_v_eta_edge",
    "edges_inherited_not_stamped",
    "stamped_required",
    "stamped_optional",
    "divergences",
    # -- the COMPARED / NOT COMPARED split. These two must never be summed and
    #    no counter here is their total; `edges_carrying_an_ndi_verdict` is the
    #    denominator both are measured against.
    "edges_compared",
    "edges_not_compared",
    "edges_not_compared_ndi_required",
    # -- WHY a class did not resolve. Ordered causes, first match wins; the six
    #    partition `classes_with_no_v_eta_class` and their edge counterparts
    #    partition `edges_lost_to_unresolved_class`.
    "unresolved_classes_source_deleted",
    "unresolved_classes_folds_to_target",
    "unresolved_classes_second_pass_only",
    "unresolved_classes_migrator_emits_nothing",
    "unresolved_classes_no_home_no_migrator",
    "unresolved_classes_cause_undetermined",
    "edges_unresolved_source_deleted",
    "edges_unresolved_folds_to_target",
    "edges_unresolved_second_pass_only",
    "edges_unresolved_migrator_emits_nothing",
    "edges_unresolved_no_home_no_migrator",
    "edges_unresolved_cause_undetermined",
    # -- following the fold, ATTEMPTED FOR EVERY unresolved-class edge whatever
    #    its class-level cause. These five also partition
    #    `edges_lost_to_unresolved_class`.
    "fold_followed",
    "fold_unfollowed_no_targets_named",
    "fold_unfollowed_no_target_declares_it",
    "fold_unfollowed_ambiguous_across_targets",
    "fold_unfollowed_inherited_only",
    "fold_divergences",
    "fold_agreements",
    "fold_rows_already_compared_by_name",
    # -- WHY no V_eta edge of that name. These three partition
    #    `edges_with_no_v_eta_edge`.
    "edge_renamed_to_family",
    "edge_dropped_class_declares_no_edges",
    "edge_dropped",
    "edges_with_no_v_eta_edge_ndi_required",
    # -- inputs. 0 means the causes above could not be determined AT ALL and
    #    every unresolved edge is parked in `cause_undetermined` rather than in
    #    a bucket that would read as accounted for.
    "targets_map_readable",
    "phase8_set_supplied",
    "partition_ok",
)

#: The ordered class-level causes. ORDER IS PART OF THE ANSWER: a phase-8
#: deleted source ALSO has a target row, so without a fixed precedence the two
#: buckets would double-count. Read a bucket as "the FIRST of these that is
#: true", never as "the only thing true of it".
UNRESOLVED_CAUSES = (
    ("source_deleted",
     ("SOURCE DELETED by a completed migrator (build_v_eta _DELETE_PHASE8) -- "
     "no schema survives to compare against, and that is correct")),
    ("folds_to_target",
     "FOLDS into differently-named target(s) named by the migration-target map"),
    ("second_pass_only",
     "pass 1 emits nothing; the class is deferred to the NDI second pass"),
    ("migrator_emits_nothing",
     "a migration-target row exists but names no target anywhere"),
    ("no_home_no_migrator",
     "NO V_eta home and NO migrator -- the genuine hole"),
    ("cause_undetermined",
     "CAUSE NOT DETERMINED -- the inputs that decide it were not supplied"),
)

#: The ordered edge-level causes for "no V_eta edge of that name". A renamed
#: edge and a dropped edge are different facts and were one bucket until
#: 2026-08-11.
NO_EDGE_CAUSES = (
    ("renamed_to_family",
     ("RENAMED to a numbered edge family `<name>_#` -- present, under the "
     "family spelling; NOT stamped, because a missing family member is not a "
     "blank edge (silentLoss applies the same exclusion)")),
    ("dropped_class_declares_no_edges",
     "DROPPED -- the V_eta class declares no `depends_on` at all"),
    ("dropped",
     "DROPPED -- the V_eta class declares edges, none of that name"),
)


def _load_targets_map(targets_path):
    """The migration-target map, or None.

    `schemas/V_eta_migration_targets.json` is the record of WHAT EACH MIGRATOR
    ACTUALLY EMITS -- `targets` is generated by tools/refresh_migration_targets.py
    from the migrator call graph, and `tools/gates.py` runs that tool's
    `--check` as a GATE, so in any green run the file is not stale. It is read
    here rather than the coverage ledger because the ledger is generated AFTER
    this build step and would therefore be one run behind.

    Returns None on any failure. None is NOT an empty map: it parks every
    unresolved edge in `cause_undetermined` instead of letting it fall into a
    bucket that reads as accounted for.
    """
    if not targets_path:
        return None
    # A LEGITIMATE FILTER. The skip is already a counter: the caller sets
    # `targets_map_readable` from this `None` and reports it, and the docstring
    # above says what `None` buys -- every unresolved edge parks in
    # `cause_undetermined` rather than in a bucket that reads as accounted for.
    # Nothing leaves a denominator. Named so a failure that is NOT "no usable
    # targets file" stops the build instead of being demoted to one.
    try:
        with open(targets_path) as f:
            return json.load(f)["classes"]
    except (OSError, json.JSONDecodeError, KeyError, TypeError):
        return None


def stamp_ndi_required(veta_dir, gt_path, rename, tiers, meta_files,
                       deleted_phase8=None, targets_path=None):
    """Stamp NDI's verdict onto matching V_eta edges; return the denominators.

    VETA_DIR    the built schema tree (mutated in place)
    GT_PATH     schemas/V_eta_ndi_ground_truth.json
    RENAME      build_v_eta.py's did_v1 -> V_eta class rename map
    TIERS       schema tier folder names
    META_FILES  basenames that are not document classes
    DELETED_PHASE8  build_v_eta.py's `_DELETE_PHASE8` set, or None
    TARGETS_PATH    schemas/V_eta_migration_targets.json, or None

    The last two are what turn "NOT MEASURED" from one opaque bucket into
    causes. Supplying neither is legal and reports every unresolved edge as
    CAUSE NOT DETERMINED -- the answer that cannot be misread as accounted for.

    Returns a dict carrying every counter in COUNTERS plus:

      ground_truth_readable   0 when the extract could not be parsed. NOT a
                              silent zero: with it at 0 every other number is a
                              property of this run, and the caller says so.
      unresolved_classes      NDI class names with no V_eta counterpart --
                              their edges are NOT MEASURED, not zero.
      unresolved_by_cause     cause -> ['class (n edge(s))', ...]
      no_edge_by_cause        cause -> ['ndi_class.edge -> v_eta_class', ...]
      divergence_rows         'class.edge' for each stamped-required edge that
                              V_eta declares optional. The census's subject.
      fold_divergence_rows    'ndi_class.edge -> v_eta_class.edge' for each
                              edge brought into comparison by FOLLOWING a fold.
                              Reported separately and NEVER added to
                              `divergences`: these are not stamped, so
                              silentLoss cannot see them, and summing the two
                              would put an edge the corpus counts and an edge
                              it cannot count in one figure.

    THE COUNTERS ARE THE POINT (operating rule 5). A zero in the divergence row
    can mean five different things -- nothing diverges / no class resolved / no
    edge name matched / nothing was ever compared / the ground truth was
    unreadable -- and only these numbers tell them apart.
    """
    d = {k: 0 for k in COUNTERS}
    d["unresolved_classes"] = []
    d["divergence_rows"] = []
    d["fold_divergence_rows"] = []
    d["unresolved_by_cause"] = {c: [] for c, _ in UNRESOLVED_CAUSES}
    d["no_edge_by_cause"] = {c: [] for c, _ in NO_EDGE_CAUSES}
    # A LEGITIMATE FILTER, for the same reason: `ground_truth_readable` IS the
    # counter for this skip, it is returned to the caller and printed, and the
    # docstring above states that with it at 0 every other number is a property
    # of the run. The universe does not shrink -- the whole measurement declares
    # itself void.
    try:
        with open(gt_path) as f:
            gt = json.load(f)
    except (OSError, json.JSONDecodeError):
        d["ground_truth_readable"] = 0
        return d
    d["ground_truth_readable"] = 1
    targets_map = _load_targets_map(targets_path)
    d["targets_map_readable"] = 1 if targets_map is not None else 0
    d["phase8_set_supplied"] = 1 if deleted_phase8 is not None else 0
    phase8 = set(deleted_phase8 or ())

    # A SHRINKING DENOMINATOR, and a well-disguised one. `by_class` IS the V_eta
    # side of the comparison: a schema file skipped here does not appear as a
    # missing file, it appears as an NDI class with no V_eta counterpart, which
    # lands in `classes_with_no_v_eta_class` -- a bucket that reads as
    # accounted for, with a named cause attached. So a build tree that could not
    # be fully read would report itself as a migration that has not homed a
    # class yet. Counted, and reported beside the candidate count.
    files, by_class = {}, {}
    for tier in tiers:
        for p in glob.glob(os.path.join(veta_dir, tier, "*.json")):
            if os.path.basename(p) in meta_files:
                continue
            d["v_eta_files_seen"] += 1
            try:
                with open(p) as f:
                    doc = json.load(f)
                cn = doc["document_class"]["class_name"]
            except (OSError, json.JSONDecodeError, KeyError, TypeError):
                d["v_eta_files_unreadable"] += 1
                continue
            files[cn] = p
            by_class[cn] = doc
    d["v_eta_classes_read"] = len(by_class)
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

    def own_deps(cn):
        return {e["name"]: e for e in by_class.get(cn, {}).get("depends_on", [])}

    def inherited_dep_names(cn):
        out = set()
        for a in ancestors(cn):
            out |= set(own_deps(a))
        return out

    def targets_row(ndi_cn):
        """The migration-target row for an NDI class, or None.

        Two spellings are tried because the map's keys are NOT uniformly
        snake_cased -- `imageStack_parameters` is a real key -- and looking up
        only one spelling is the `demo_ndi`/`demoNDI` failure: a miss would be
        a property of the query and would land the class in the
        no-home-no-migrator bucket, which is the alarming one.
        """
        if targets_map is None:
            return None
        for cand in (ndi_cn, ndi_snake(ndi_cn)):
            if cand in targets_map:
                return targets_map[cand]
        return None

    def unresolved_cause(ndi_cn):
        """FIRST of the ordered causes that is true of this NDI class."""
        if targets_map is None or deleted_phase8 is None:
            return "cause_undetermined"
        if ndi_cn in phase8 or ndi_snake(ndi_cn) in phase8:
            return "source_deleted"
        row = targets_row(ndi_cn)
        if row is None:
            return "no_home_no_migrator"
        if row.get("targets"):
            return "folds_to_target"
        if row.get("second_pass") or row.get("decided_targets"):
            return "second_pass_only"
        return "migrator_emits_nothing"

    def follow_fold(ndi_cn, edge_name):
        """Try to reach the edge through the fold. Returns (outcome, holder).

        THE RULE IS DELIBERATELY NARROW, and a narrow honest number is the
        point: a comparison is made only when EXACTLY ONE emitted target
        declares an edge of that name and declares it in its OWN `depends_on`.

          * more than one target declares it -> AMBIGUOUS. `treatment`
            decomposes into four manipulation/observation documents that each
            inherit `subject_id`; which of them carries NDI's requirement is a
            modelling question, not a lookup, and picking one would be a guess.
          * only an ancestor declares it -> NOT FOLLOWED, the same rule the
            by-name path already applies (`edges_inherited_not_stamped`):
            an NDI fact about one class must not be read off a shared
            superclass that other sources also reach.
        """
        row = targets_row(ndi_cn)
        tg = list((row or {}).get("targets") or [])
        if not tg:
            return "no_targets_named", None
        holders = [t for t in tg
                   if edge_name in own_deps(t)
                   or edge_name in inherited_dep_names(t)]
        if not holders:
            return "no_target_declares_it", None
        if len(holders) > 1:
            return "ambiguous_across_targets", None
        if edge_name not in own_deps(holders[0]):
            return "inherited_only", holders[0]
        return "followed", holders[0]

    touched = set()
    unresolved_records = []
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
            unresolved_records.append((ndi_cn, verdicts))
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
                    if req:
                        d["edges_with_no_v_eta_edge_ndi_required"] += 1
                    # A RENAMED EDGE AND A DROPPED EDGE ARE DIFFERENT FACTS.
                    # They were one bucket, and the family case is the larger
                    # half: the edge is PRESENT, spelled `<name>_#`.
                    fam = name + "_#"
                    if fam in own or fam in anc_names:
                        cause = "renamed_to_family"
                    elif not own and not anc_names:
                        cause = "dropped_class_declares_no_edges"
                    else:
                        cause = "dropped"
                    d["edge_" + cause] += 1
                    d["no_edge_by_cause"][cause].append(
                        "{}.{} -> {}{}".format(ndi_cn, raw_name, target,
                                           "" if req else "  (NDI-optional)"))
                continue
            d["edges_matched_by_name"] += 1
            own[name][MARKER] = bool(req)
            touched.add(target)
            if req:
                d["stamped_required"] += 1
                if not own[name].get("mustBeNonEmpty", False):
                    d["divergences"] += 1
                    d["divergence_rows"].append(f"{target}.{name}")
            else:
                d["stamped_optional"] += 1

    # ---- WHY the unresolved classes are unresolved, and how far the fold can
    # ---- be followed. Two ORTHOGONAL partitions of the same edges: the first
    # ---- says why the CLASS did not resolve, the second whether the EDGE
    # ---- could nonetheless be reached. Neither is a subset of the other, and
    # ---- neither is ever added to the compared count.
    for ndi_cn, verdicts in unresolved_records:
        cause = unresolved_cause(ndi_cn)
        d["unresolved_classes_" + cause] += 1
        d["edges_unresolved_" + cause] += len(verdicts)
        d["unresolved_by_cause"][cause].append(
            f'{ndi_cn} ({len(verdicts)} edge(s))')
        for raw_name, req in sorted(verdicts.items()):
            name = ndi_snake(raw_name)
            outcome, holder = follow_fold(ndi_cn, name)
            if outcome != "followed":
                d["fold_unfollowed_" + outcome] += 1
                continue
            d["fold_followed"] += 1
            dep = own_deps(holder)[name]
            # NOT STAMPED. The marker is a per-class declaration that
            # silentLoss reads off the class chain; writing NDI's verdict about
            # the SOURCE class onto the TARGET would assert it of every
            # document of that target class, including ones that arrived from
            # a different source entirely. Comparison only.
            if req and not dep.get("mustBeNonEmpty", False):
                d["fold_divergences"] += 1
                d["fold_divergence_rows"].append(
                    f"{ndi_cn}.{raw_name} -> {holder}.{name}")
            else:
                d["fold_agreements"] += 1
            if MARKER in dep:
                # The target edge already carries a verdict from its OWN NDI
                # class, so this row is ALREADY inside `divergences`. Counted
                # so the two figures cannot be added together by a reader who
                # assumes they are disjoint.
                d["fold_rows_already_compared_by_name"] += 1

    for cn in sorted(touched):
        with open(files[cn], "w") as f:
            json.dump(by_class[cn], f, indent=4)
            f.write("\n")
    d["unresolved_classes"] = sorted(d["unresolved_classes"])
    d["divergence_rows"] = sorted(d["divergence_rows"])
    d["fold_divergence_rows"] = sorted(d["fold_divergence_rows"])
    for k in d["unresolved_by_cause"]:
        d["unresolved_by_cause"][k] = sorted(d["unresolved_by_cause"][k])
    for k in d["no_edge_by_cause"]:
        d["no_edge_by_cause"][k] = sorted(d["no_edge_by_cause"][k])

    d["edges_carrying_an_ndi_verdict"] = (d["ndi_required_edges"]
                                          + d["ndi_optional_edges"])
    # COMPARED means: an NDI verdict and a V_eta declaration were put side by
    # side. Everything else was NEVER LOOKED AT. The stamp writes the marker
    # exactly on the compared set, which is why the two are the same number --
    # if they ever diverge the partition check below fails.
    d["edges_compared"] = d["edges_matched_by_name"]
    d["edges_not_compared"] = (d["edges_lost_to_unresolved_class"]
                               + d["edges_with_no_v_eta_edge"]
                               + d["edges_inherited_not_stamped"])
    d["edges_not_compared_ndi_required"] = (
        sum(1 for _, v in unresolved_records for r in v.values() if r)
        + d["edges_with_no_v_eta_edge_ndi_required"])
    d["partition_ok"] = 1 if partitions_hold(d) else 0
    return d


#: Each entry is (name, total_key, part_keys). Every part must sum to its
#: total. A bucket that stops partitioning is a bucket that has started
#: double-counting or dropping, and either way the report becomes readable as
#: better news than it is -- so this is checked at run time, not only in tests.
PARTITIONS = (
    ("compared + not compared = every edge carrying an NDI verdict",
     "edges_carrying_an_ndi_verdict",
     ("edges_compared", "edges_not_compared")),
    ("NDI-required + NDI-optional = every edge carrying an NDI verdict",
     "edges_carrying_an_ndi_verdict",
     ("ndi_required_edges", "ndi_optional_edges")),
    ("stamped required + stamped optional = compared",
     "edges_compared", ("stamped_required", "stamped_optional")),
    ("class-level causes = classes that did not resolve",
     "classes_with_no_v_eta_class",
     tuple("unresolved_classes_" + c for c, _ in UNRESOLVED_CAUSES)),
    ("class-level causes (edges) = edges lost to an unresolved class",
     "edges_lost_to_unresolved_class",
     tuple("edges_unresolved_" + c for c, _ in UNRESOLVED_CAUSES)),
    ("fold outcomes = edges lost to an unresolved class",
     "edges_lost_to_unresolved_class",
     ("fold_followed", "fold_unfollowed_no_targets_named",
      "fold_unfollowed_no_target_declares_it",
      "fold_unfollowed_ambiguous_across_targets",
      "fold_unfollowed_inherited_only")),
    ("fold comparisons = folds followed",
     "fold_followed", ("fold_divergences", "fold_agreements")),
    ("no-edge causes = edges with no V_eta edge of that name",
     "edges_with_no_v_eta_edge",
     tuple("edge_" + c for c, _ in NO_EDGE_CAUSES)),
)


def partition_failures(d):
    """Every partition that does not add up, as printable sentences."""
    bad = []
    for label, total, parts in PARTITIONS:
        got = sum(d.get(p, 0) for p in parts)
        if got != d.get(total, 0):
            bad.append("%s: %d != %d (%s)"
                       % (label, got, d.get(total, 0),
                          " + ".join(f'{p}={d.get(p, 0)}'
                                     for p in parts)))
    return bad


def partitions_hold(d):
    return not partition_failures(d)


def render_stamp_report(d):
    """The build-time report. DENOMINATOR FIRST and unconditionally."""
    out = ["",
           (f"NDI REQUIRED-NESS STAMP (`{MARKER}`) -- report-only; no mustBeNonEmpty "
           "value is read or written")]
    if not d.get("ground_truth_readable"):
        out += ["  *** V_eta_ndi_ground_truth.json COULD NOT BE READ. Nothing",
                "  *** was stamped, so every count downstream is a property of",
                "  *** this build, not of the data. Run tools/ndi_ground_truth.py."]
        return out + [""]
    # THE V_eta SIDE FIRST. It is the side an unreadable file used to leave
    # silently, disguised as an NDI class with no counterpart.
    out.append(f'  DENOMINATOR: {d["v_eta_files_seen"]} V_eta schema file(s) offered, {d["v_eta_classes_read"]} class(es) read, {d["v_eta_files_unreadable"]} UNREADABLE')
    if d["v_eta_files_unreadable"]:
        out += ["    *** A SCHEMA FILE THAT COULD NOT BE READ IS NOT A CLASS WITH",
                "    *** NO V_eta HOME. Every unresolved-class figure below is",
                "    *** inflated by that many."]
    out.append(f'  DENOMINATOR: {d["ndi_classes_read"]} NDI class(es) read; {d["ndi_classes_with_a_verdict"]} state required-ness for at least one edge')
    out.append(f'  DENOMINATOR: {d["edges_carrying_an_ndi_verdict"]} edge(s) carry an NDI verdict -- {d["ndi_required_edges"]} NDI-REQUIRED + {d["ndi_optional_edges"]} NDI-optional')
    out.append(f'  DENOMINATOR: {d["classes_resolved_to_v_eta"]} NDI class(es) resolved to a V_eta class; {d["classes_with_no_v_eta_class"]} did not')
    out.append("")
    # THE TWO NUMBERS THE WHOLE REPORT TURNS ON, ADJACENT AND SEPARATELY
    # LABELLED. The divergence figure carries its own denominator inline so it
    # can never be quoted without one, and the not-compared figure is stated in
    # the same breath so "0 of 60 compared" and "0 of 5 compared, 55 never
    # looked at" cannot render the same way.
    out.append(f'  COMPARED:     {d["edges_compared"]} of {d["edges_carrying_an_ndi_verdict"]} edge(s) -- of which {d["divergences"]} DIVERGE (NDI requires it, V_eta does not)')
    out.append(f'  NOT COMPARED: {d["edges_not_compared"]} of {d["edges_carrying_an_ndi_verdict"]} edge(s) -- NEVER LOOKED AT. Not a zero, and NOT the')
    out.append("                complement of a clean result: no figure in "
               "this report is the")
    out.append("                sum of these two lines, and none may be "
               "quoted as one.")
    out.append(f'                of them {d["edges_not_compared_ndi_required"]} are NDI-REQUIRED -- each could have been a divergence')
    out.append("                and none of them was examined.")
    if d["edges_compared"] == 0:
        out += ["  *** NOTHING WAS COMPARED AT ALL. The divergence count above",
                "  *** is a property of the matching, not of the schemas. The",
                "  *** zero is 'untested', not 'clean'."]
    out.append("")
    out.append(f'  NOT COMPARED, breakdown A -- the CLASS did not resolve: {d["edges_lost_to_unresolved_class"]} edge(s) in {d["classes_with_no_v_eta_class"]} class(es)')
    if not d.get("targets_map_readable") or not d.get("phase8_set_supplied"):
        out += ["    *** THE CAUSES BELOW COULD NOT BE DETERMINED. {}".format(" and ".join(
                    ([] if d.get("phase8_set_supplied")
                     else ["the _DELETE_PHASE8 set was not supplied"])
                    + ([] if d.get("targets_map_readable")
                       else ["V_eta_migration_targets.json was not read"]))),
                ("    *** Every class below is parked in CAUSE NOT DETERMINED "
                "rather than"),
                "    *** in a bucket that would read as accounted for."]
    for cause, blurb in UNRESOLVED_CAUSES:
        n_cls = d["unresolved_classes_" + cause]
        n_edge = d["edges_unresolved_" + cause]
        out.append(f'    {n_cls} class(es) / {n_edge} edge(s)  {blurb}')
        for row in d.get("unresolved_by_cause", {}).get(cause, []):
            out.append(f"        {row}")
    out.append("")
    out.append(f'  FOLLOWING THE FOLD -- attempted for all {d["edges_lost_to_unresolved_class"]} of those edges; COMPARISON ONLY,')
    out.append("  nothing below is stamped, so `silentLoss` cannot see any of "
               "it and these")
    out.append("  divergences are NEVER added to the COMPARED line above.")
    out.append(f'    {d["fold_followed"]} followed to exactly one target edge -- {d["fold_divergences"]} DIVERGE, {d["fold_agreements"]} agree')
    out.append(f'    {d["fold_rows_already_compared_by_name"]} already carry a verdict from their own NDI class (counted in COMPARED)')
    out.append(f'    {d["fold_unfollowed_no_targets_named"]} not followed: the class names no emitted target')
    out.append(f'    {d["fold_unfollowed_no_target_declares_it"]} not followed: no named target declares an edge of that name')
    out.append(f'    {d["fold_unfollowed_ambiguous_across_targets"]} not followed: AMBIGUOUS -- more than one target declares it')
    out.append(f'    {d["fold_unfollowed_inherited_only"]} not followed: only an ancestor of the target declares it')
    for row in d.get("fold_divergence_rows", []):
        out.append(f"        DIVERGES (unstamped): {row}")
    out.append("")
    out.append('  NOT COMPARED, breakdown B -- the class resolved, the EDGE did not: %d edge(s)'
               % (d["edges_with_no_v_eta_edge"]
                  + d["edges_inherited_not_stamped"]))
    out.append(f'    {d["edges_inherited_not_stamped"]} inherited from an ancestor -- present, but not this class\'s fact to carry')
    out.append(f'    {d["edges_with_no_v_eta_edge"]} no V_eta edge of that name, of which {d["edges_with_no_v_eta_edge_ndi_required"]} are NDI-REQUIRED:')
    for cause, blurb in NO_EDGE_CAUSES:
        out.append(f'      {d["edge_" + cause]}  {blurb}')
        for row in d.get("no_edge_by_cause", {}).get(cause, []):
            out.append(f"          {row}")
    if not d.get("partition_ok"):
        out.append("")
        out += [("  *** A PARTITION DOES NOT ADD UP. Some edge is counted twice "
                "or not at"),
                "  *** all, so every breakdown above is unreliable:"]
        out += ["  ***   " + line for line in partition_failures(d)]
    return out + [""]
