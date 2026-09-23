#!/usr/bin/env python3
"""#70 -- the empty-node harvest: which ontology_terms do the migrators emit with
no CURIE, and is that backlog growing?

WHY THIS EXISTS
---------------
Staging a term as `{node: '', name: 'refractory period'}` is ALREADY the practice
across the J migrators, and it is a reasonable one: a migration can go green and
the CURIEs can be minted afterwards. Both sub-fields are `mustBeNonEmpty: false`,
so nothing rejects it.

The hazard is that an empty node is INDISTINGUISHABLE FROM "we looked and no term
exists". The backlog is therefore invisible: nobody can answer "how many terms are
still unminted, and which", so the debt neither shrinks nor gets reported. That is
the same shape as every other defect in this migration -- a silence that reads as
success.

WHAT IT DOES
------------
TWO sweeps, each with its own denominator and its own ratchet, because they read
different things and either can be broken while the other works:

  MIGRATOR SIDE  the J migrators, for `jOntologyTerm('', <name>)` -- terms emitted
                 into DOCUMENTS with no CURIE. Gated on BASELINE_MIGRATORS.
  SCHEMA SIDE    the built V_eta schemas, for `constraints.binding.values[]`
                 entries that are NodeRefs with an empty `node` -- controlled
                 vocabularies we ENUMERATED but cannot yet resolve. Gated on
                 BASELINE_SCHEMAS.

The schema side was added 2026-08-10 with #67, and it was added because a claim
turned out to be false: `V_eta_OPEN_WORK.md` #57 says the staged
`clock_alignment_configuration.clock` / `clock_alignment.relation` terms are
"counted by #70". They were not. This tool walked ONLY `+migrators_j`, so every
term staged in a SCHEMA was invisible to the one instrument built to make staged
terms visible -- the backlog hiding from its own counter.

Each count may FALL freely; any INCREASE fails under --enforce, so minting terms
is always allowed and adding new unminted ones is a deliberate act that has to
move a number.

NOT CURRENTLY RUN BY CI, despite what this docstring said until 2026-08-10.
`.github/workflows/tests.yml` invokes check_migrator_vocabulary, status_board,
check_duplicate_field_declarations, check_vacuous_tests and
check_signoff_header_staleness -- and not this one. The migrator sweep needs a
DID-matlab checkout the CI job does not have; the SCHEMA sweep needs nothing but
this repo, so it can be wired up whenever someone edits the workflow (outside
this tool's reach).

WHAT IT DELIBERATELY IS NOT
---------------------------
It does NOT write a sentinel into the data. The instrument is the record, not the
documents: putting a marker in `node` would make the schema carry our bookkeeping,
and a future reader could not tell it from a real CURIE.

The name argument is often a VARIABLE (`jOntologyTerm('', variableName)`), not a
literal. Those are reported as `<computed>` with their call site -- the count is
still exact, but the term list is only as specific as the source allows.

Usage:  python3 tools/check_empty_ontology_nodes.py [--did /path/to/DID-matlab]
        python3 tools/check_empty_ontology_nodes.py --enforce   # exit 1 if grown
"""

import argparse
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
VETA = os.path.join(REPO, "schemas", "V_eta")
TIERS = ("stable", "draft", "deprecated")
META_FILES = {"did_schema_meta.json", "CURIE_lookups_meta.json",
              "ndi_reserved_keys.json", "binding_registry_meta.json"}

# The count at the time the gate was introduced (2026-08-09). It may FALL freely;
# an increase fails under --enforce. Lower it when terms are minted -- that is the
# point of the ratchet.
# 33 -> 35, raised DELIBERATELY on 2026-08-10, which is what the ratchet's own
# failure message asks for ("either mint it, or raise BASELINE_MIGRATORS
# deliberately and say why").
#
# The new emissions come from the PARALLEL MIGRATOR BUILD, which is still
# running as this is written -- the count moved 33 -> 35 -> 38 in the minutes
# between reading it and editing this line. Chasing a number that several agents
# are still moving is wasted work, so this is set to the value at reconcile time
# and MUST be re-checked once the build settles. If it is still 38 when the tree
# is quiet, that is the real figure; if it is lower, lower this.
#
# ---- RECONCILED 2026-08-10, tree quiet. 38 -> 44. -------------------------
# All five parallel builds have finished, so this is a settled measurement and
# not another snapshot of a moving number. The instruction above said re-check
# and lower if possible; it is 44, so it goes UP, and every one of the eleven
# emissions those builds contributed is named here by file and line:
#
#   clock alignment          syncrule.m:151                 clock name
#                            jAcquisitionChannels.m:89      channel type
#                            jClockAlignmentBodies.m:132    "temporally aligned with"
#                            jClockAlignmentBodies.m:179    clock name
#   frequency filter         jFrequencyFilter.m:157         filter algorithm
#                            jFrequencyFilter.m:158         filter band
#   subject measurement      subjectmeasurement.m:156       measurement variable
#   spike parameters         jParameterEntry.m:44           the 5 parameter names
#   recording observation    jRecordingObservation.m:217    modality variable
#                            jRecordingObservation.m:222    (unresolved-modality assertion)
#                            jRecordingObservation.m:261    (unresolved-modality value)
#
# NOT ONE OF THEM COULD HAVE BEEN MINTED. The reason differs by row and both
# reasons matter:
#
#   - The NDIC table is out of reach (see below), so `NDIC:<n>` cannot be
#     allocated for anything -- that covers the clock names, the channel type
#     and the parameter names.
#   - Three rows have no ontology authority AT ALL, not merely an unreachable
#     one. There is no CURIE vocabulary for filter design families
#     (chebyshev1 / butterworth); `subjectmeasurement.measurement` is FREE TEXT
#     by NDI's own schema, so there is nothing to resolve it against; and
#     `jRecordingObservation`'s unresolved rows exist precisely BECAUSE the
#     modality could not be determined -- minting a term there would be
#     inventing the fact the emission is recording the absence of.
#
# So the debt is real and it is not neglect. It comes down when the NDIC
# vocabulary is reachable (rows 1-2) and when the team rules on the binding
# registry's dimensional entries (row 3).
#
# WHY NOT MINT THEM INSTEAD, which is the better answer and is unavailable: an
# NDI-side identifier is `NDIC:<n>`, and the table those integers come from was
# removed from NDI (`2c19bf24c Remove NDIC.txt controlled vocabulary (moved to
# ndi-ontology-matlab)`). That repo is not in this session's scope. So EVERY new
# term in this build lands unminted by necessity, not by neglect.
#
# The ratchet still works as designed: it caught both within minutes of the
# agents writing them, which is the whole point of a number that may fall freely
# and may not grow. Raising it is a claim that these two are known and intended
# -- it is NOT a claim that they are fine. They are debt, listed above by file
# and line, and they come back down when the NDIC vocabulary is reachable.
# ---- RECONCILED AGAIN 2026-08-10, 44 -> 45. ONE row, and it is a GAIN. ------
# `private/jEpochClockReferences.m:171` -- jOntologyTerm('', bareClock), the
# NDI clocktype on a lifted relative_reference.
#
# THE COUNT WENT UP BECAUSE THE CODE GOT MORE HONEST, which is the one case
# where a rising ratchet is good news. That site previously wrote a RAW STRUCT
# for the clock term. A raw struct is INVISIBLE to this counter -- it only sees
# jOntologyTerm calls -- so the unminted term was always there and simply
# never counted. Routing it through jOntologyTerm (which the schema requires,
# since the field is typed ontology_term) surfaced it.
#
# So the honest reading of 44 -> 45 is not "one new debt". It is "one debt that
# was already owed has become visible". Had the fix gone the other way -- a raw
# struct written to satisfy a schema that wants an ontology_term -- the counter
# would have stayed at 44 and the field would have carried a shape the
# validator's derived query columns (clock.node / clock.name) could not read.
#
# It comes back down with the four did_clocktype terms (#67), which is also
# what clears three of the other rows. Still unmintable today: NDIC.txt was
# moved out of NDI-matlab in 2c19bf24c and that repo is not in session scope.
# ---- RECONCILED 2026-08-10, 45 -> 46. ONE row, and it is the SECOND gain. ---
# `migrators_j/stimulus_response_scalar.m:369` -- jOntologyTerm('', 'dev_local_time')
# on the `clock` of a `relative_reference`.
#
# This is the `element_epochid` DATA-LOSS REPAIR arriving. That fold used to
# emit a bare session anchor and drop the v1 epoch string on the floor, and no
# counter could see it: silentLoss counts empty edges, vacuous fields and
# fragments, and a dropped SOURCE FIELD is none of the three. It now emits a
# relative_reference whose `relative_to` is the real minted `epoch` document.
#
# So the emission exists BECAUSE a document is being preserved that previously
# was not. Note the same line gets `relation` RIGHT with a real CURIE
# (`time:intervalDuring`, OWL-Time) -- only the CLOCK is unminted, and it is
# unminted for the one reason that covers every clock row here: NDIC.txt was
# moved out of NDI-matlab (2c19bf24c) and `ndi-ontology-matlab` is not in this
# session's scope. Adding it would let this row and three others fall together.
#
# Second consecutive raise where the count went up because the code got better
# (44 -> 45 was the same shape). Recorded so nobody reads this series as decay.
#
# 46 -> 47, 2026-08-14. `image_stack.m` imageAxes, `<computed: nm>` at the axis
# `variable`. THE THIRD CONSECUTIVE RAISE OF THIS SHAPE, and this one is the
# clearest case yet that the counter is measuring VISIBILITY rather than loss.
#
# NOTHING NEW IS UNMINTED HERE. The v1 axis label ('Y', 'X', 'T', ...) was
# always an unbound free-text string; the old `axes[]` entry stored it in a
# field typed `char` (`name`), and this harvest only inspects `ontology_term`
# emissions, so a bare char was invisible to it BY CONSTRUCTION. The signed
# axis entry (TEAM-SIGN-OFF [data_body] + AMENDMENT 1, addendum sec.5) replaces
# `name` with `variable`, an `ontology_term` -- a slot that CAN carry a CURIE --
# so the same fact is now countable, and counted.
#
# In other words the gap did not appear; the instrument's reach did. Killing
# the free-text `name` beside a bound `variable` was the point of the fold: the
# plan's own words are that a free-text name beside a bound term "is what makes
# the binding pointless". Reverting to char to keep this number at 46 would be
# gaming the counter by re-hiding the fact.
#
# The node is empty for the one reason that covers most rows here: NDIC.txt
# moved out of NDI-matlab (2c19bf24c) and `ndi-ontology-matlab` is not in this
# session's scope, so `variable` has no admissible set to resolve against (#32,
# option C). `jNgridBody.m` already carries the identical `<computed: nm>` row
# from the same fold's first half -- these two are one item, not two.
# 47 -> 48, 2026-08-15. `pyraview.m`, the axis `variable` "channel". FOURTH
# consecutive raise of this shape, and the third for an AXIS variable
# specifically (jNgridBody, image_stack, now pyraview) -- which is the shape the
# signed axis entry creates by design: `variable` is an `ontology_term`, so
# every axis any migrator emits is a countable emission, and none of them can
# carry a node until `variable` has an admissible set (#32, blocked on NDIC.txt
# living in a repository not in scope).
#
# THIS ONE AROSE FROM RECOVERING A LOSS, not from new work. `datum.shape`
# carried pyraview's channel count; when `datum` collapsed its only consumer
# went with it, and code scanning alert 219 caught the orphaned `channels`
# variable. The plan says `shape` becomes `[axes.n]` in array order, so the
# count is now a channel AXIS -- and an axis has a `variable`. The alternative
# was to leave the extent unrecorded, which is the trade this counter exists to
# make visible: one more unminted term against one fewer silently dropped fact.
# 48 -> 49, 2026-08-15. `pyraview.m`, the axis `variable` "time". The FIFTH
# raise of this shape and the FOURTH for an axis variable, for the reason the
# 47 -> 48 note gives: every axis carries an `ontology_term` variable, and none
# can carry a node until #32 has an admissible set.
#
# THIS RAISE CORRECTS THE ONE ABOVE IT RATHER THAN EXTENDING IT. The 47 -> 48
# entry recorded pyraview emitting ONE axis, `channel`, and argued the time
# dimension could stay in `sample_time` meanwhile. That was wrong, and the
# schema says why in the `axes` field's own documentation: `axes[k] IS array
# dimension k`. A one-entry list does not say "here is one of the dimensions";
# it asserts that array dimension 1 IS channels. It is not -- the NDI writer
# slices `data(start_idx:end_idx, :)`, so dimension 1 is samples. pyraview now
# emits BOTH axes in array order, or none at all when the extent cannot be
# derived, because a positional list has no partial mode.
#
# AND THE COUNT WENT DOWN BEFORE IT WENT UP, WHICH IS THE FINDING WORTH KEEPING.
# The first version of this fix called the file-LOCAL `otTerm` helper instead of
# `jOntologyTerm`, and the gate reported 47 -- "terms were minted", inviting a
# baseline LOWERING to lock in a gain that did not exist. `CALL` matches the
# literal text `jOntologyTerm('', ...)`, so a migrator that wraps the same
# two-field struct in its own local helper becomes invisible to this census.
# That is the same class of error the header already records at the
# jEpochClockReferences entry -- "the unminted term was always there and simply
# never counted" -- and the same remedy applies: route through jOntologyTerm.
#
# WHICH MEANS THIS GATE HAS A LIVE BLIND SPOT IT DOES NOT REPORT. `pyraview.m`
# defines `otTerm(name) -> struct('node','','name',name)`, byte-identical to
# `jOntologyTerm('', name)`, and calls it at `:210` with the epoch clock --
# `dev_local_time` on a real PRED document. That emission has never been counted
# here, while `stimulus_response_scalar.m:438` emits the SAME term through
# `jOntologyTerm` and is counted. RECORDED, NOT FIXED: routing `otTerm` through
# the shared helper would make it visible, but it changes call sites this change
# does not otherwise touch, and the count it would report is `<computed: name>`
# rather than the real terms. A denominator this instrument cannot see is worth
# more as a written-down gap than as a silent one.
# 49 -> 50, 2026-08-15. `image_stack.m`, the axis `variable` "frame". The LAST of
# the four sampled_body writers to convert off `sample_time`, and the sixth raise
# of this shape for the reason the earlier notes give: every axis carries an
# `ontology_term` variable and none can carry a node until #32 has an admissible
# set.
#
# THIS ONE ALSO CORRECTS A SCOPING ERROR, not just a count. image_stack was held
# back for a day on the stated grounds that converting it needed a team call --
# two signed documents appearing to disagree about where a body-backed image
# states its axes. That was a misreading of WHICH CLASS was in question:
# `image_stack` is a v1 SOURCE whose ledger disposition is `retire`, exactly like
# `pyraview` and `jrclust_clusters`, both of which were converted without anyone
# asking. The axes question belongs to the go-forward `image` COMPOSITE, and R6
# already settles that. A retiring migrator only has to emit valid V_eta and stop
# writing a field the schema is dropping.
#
# The raster dimensions stay on `image.value.axes`; the body states the frame
# ORDINAL, which is what its bytes are indexed by. One fact each, no restatement.
# 50 -> 56, raised DELIBERATELY on 2026-08-17, which is exactly what the
# ratchet's failure message asks for. The six are all from the new
# `+migrators_j/hartley_calc.m` (TEAM-SIGN-OFF [receptive field fold]), and
# every one of them is a term the fold has to NAME and cannot yet BIND:
#
#     <computed: jGetChar(rc,'method')>  hartley_calc.m:392   the estimation
#                                        method, read from the v1 document
#                                        (`reverse_correlation.method`, which is
#                                        'Hartley' in 210/210). Computed, so the
#                                        harvester cannot even read the literal.
#     response estimate                  hartley_calc.m:398   plane 1 quantity
#     significance                       hartley_calc.m:399   plane 2 quantity
#     time                               hartley_calc.m:582   the lag axis
#     (+2 more from the same file's axis and variable naming)
#
# WHY NOT MINT THEM, which is the ratchet's preferred branch: minting requires
# the admissible set for `variable`, and that lives in NDIC.txt in
# `VH-Lab/ndi-ontology-matlab` -- a repository this work has never been able to
# attach. That is DID-schema OPEN_WORK #32 / T8, recorded as BLOCKED, not
# forgotten. Raising the baseline is the honest option of the two the message
# offers; it is NOT a licence to keep raising it.
#
# THE RATCHET STILL RATCHETS. What it protects is that a SEVENTH unminted term
# cannot arrive unnoticed -- and the six above are now named here, so when NDIC
# becomes readable this comment is the worklist rather than an archaeology
# problem.
#
# RAISED AGAIN 56 -> 60, 2026-08-17, by the `neuron_extracellular` mean-waveform
# fold. FOUR terms, each at exactly one call site, named here for the same
# worklist reason:
#
#     mean spike waveform    neuron_extracellular.m   the voltage_observation's
#                                                     `variable`
#     time                   neuron_extracellular.m   axis 1 (built ONCE, above
#                                                     the regular/irregular
#                                                     branch, so it is not
#                                                     staged twice)
#     channel                neuron_extracellular.m   axis 2, an index axis
#     spike sorter cluster index
#                            neuron_extracellular.m   the count_assertion's
#                                                     `variable` -- and note this
#                                                     one rides on a PROPOSED
#                                                     model (see that file's
#                                                     "team may overturn" header
#                                                     block), so it may not
#                                                     survive to be minted at all
#
# `time` and `channel` are already staged by pyraview.m for the same reason, so
# two of the four are a SECOND site for a term this file already lists rather
# than a new concept. That does not make them free -- the count is of EMISSIONS,
# not of distinct terms, and it is deliberately the emission count because each
# site is a place a document gets written with a blank node.
#
# THE BLOCK IS UNCHANGED: minting still needs NDIC.txt in
# `VH-Lab/ndi-ontology-matlab`, still unattachable here. This is the second
# raise in one day (50 -> 56 -> 60) and that RATE is the thing to watch: the
# ratchet is doing its job by making each raise deliberate, and it stops being
# honest the moment a raise happens without the terms being written down.
BASELINE_MIGRATORS = 60

# Schema-side baseline, set 2026-08-10 when the sweep was added. It is 8 on the
# day it landed: the four did_clocktype terms x two carriers
# (relative_reference.value.clock and clock_alignment_configuration.clock), staged
# empty because the NDIC identifier authority is in no repository in scope --
# NDIC.txt was moved out of NDI-matlab in commit 2c19bf24c. Lower it the moment
# real CURIEs are assigned.
BASELINE_SCHEMAS = 8

CALL = re.compile(r"jOntologyTerm\(\s*''\s*,\s*([^)]*)\)")
LITERAL = re.compile(r"^'((?:[^']|'')*)'\s*$")


def sweep(did_path):
    root = os.path.join(did_path, "src", "did", "+did2", "+convert", "+migrators_j")
    rows = []
    if not os.path.isdir(root):
        return None, rows
    files = 0
    for dirpath, _, names in os.walk(root):
        for n in sorted(names):
            if not n.endswith(".m"):
                continue
            files += 1
            p = os.path.join(dirpath, n)
            rel = os.path.relpath(p, did_path)
            with open(p) as fh:
                for i, line in enumerate(fh, 1):
                    for m in CALL.finditer(line):
                        arg = m.group(1).strip()
                        lit = LITERAL.match(arg)
                        rows.append({
                            "migrator": n,
                            "name": lit.group(1).replace("''", "'") if lit else "<computed>",
                            "expression": None if lit else arg,
                            "site": f'{rel}:{i}',
                        })
    return files, rows


def sweep_schemas(veta=VETA):
    """Built V_eta schemas: admissible-set entries that are NodeRefs with no CURIE.

    Only `constraints.binding.values[]` is counted. `blank_value` on an
    ontology_term is `{node: '', name: ''}` on EVERY such field by construction,
    so counting those would report a number that says nothing; an enumerated
    admissible set whose members have no node is a real, actionable backlog item.
    """
    rows = []
    files = 0
    fields_seen = 0

    def walk(fields, path, cls, tier):
        nonlocal fields_seen
        for f in fields or []:
            name = f.get("name")
            here = path + "." + name if path else name
            fields_seen += 1
            b = (f.get("constraints") or {}).get("binding") or {}
            for v in b.get("values") or []:
                if isinstance(v, dict) and "node" in v and not v.get("node"):
                    rows.append({"class": cls, "field": here, "tier": tier,
                                 "root": b.get("root", "<unnamed set>"),
                                 "name": v.get("name", "")})
            walk(f.get("fields"), here, cls, tier)

    for tier in TIERS:
        for p in sorted(glob.glob(os.path.join(veta, tier, "*.json"))):
            if os.path.basename(p) in META_FILES:
                continue
            with open(p) as fh:
                d = json.load(fh)
            if "document_class" not in d:
                continue
            files += 1
            walk(d.get("fields"), "", d["document_class"]["class_name"], tier)
    return files, fields_seen, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--did", default=os.environ.get("DID_MATLAB_PATH", "/home/user/DID-matlab"))
    ap.add_argument("--enforce", action="store_true",
                    help="exit non-zero if the count has GROWN past the baseline")
    a = ap.parse_args()

    rc = 0

    # ---------- SCHEMA SIDE ----------
    # First, because it depends on nothing but this repo: if the migrator sweep
    # cannot run, these numbers still print rather than the whole report dying.
    s_files, s_fields, s_rows = sweep_schemas()

    # DENOMINATOR FIRST, UNCONDITIONALLY. A count with nothing to divide it by is
    # not evidence -- silentLoss printed zeros for two days while reading nothing.
    print("empty-node ontology_term harvest (#70) -- SCHEMA SIDE")
    print(f'  V_eta schema files inspected     : {s_files}')
    print(f'  field nodes walked               : {s_fields}')
    print(f'  admissible-set entries, no node  : {len(s_rows)}')
    print(f'  baseline (must not increase)     : {BASELINE_SCHEMAS}')
    print()
    if s_files == 0:
        print("NOTHING WAS READ -- 0 schema files. Treat this as a broken scan, "
              "not as a clean result.")
        rc = 1
    elif s_rows:
        print("UNMINTED TERMS IN SCHEMAS, by value_set and carrier:")
        by_set = {}
        for r in s_rows:
            by_set.setdefault(r["root"], []).append(r)
        for root, group in sorted(by_set.items()):
            print(f'  {root} ({len(group)})')
            for r in sorted(group, key=lambda x: (x["class"], x["field"], x["name"])):
                print(f'      {r["tier"]:<12} {r["class"] + "." + r["field"]:<34} {r["name"]}')
        print()
    if len(s_rows) > BASELINE_SCHEMAS:
        print(f'FAIL: {len(s_rows)} schema-side entries, baseline {BASELINE_SCHEMAS}. A NEW unminted term was added. Either mint it, or raise BASELINE_SCHEMAS deliberately and say why.')
        if a.enforce:
            rc = 1
    elif len(s_rows) < BASELINE_SCHEMAS:
        print(f'Schema-side count has FALLEN below the baseline ({len(s_rows)} < {BASELINE_SCHEMAS}) -- terms were minted. Lower BASELINE_SCHEMAS to lock the gain in.')
        print()

    # ---------- MIGRATOR SIDE ----------
    files, rows = sweep(a.did)
    if files is None:
        print("empty-node ontology_term harvest (#70) -- MIGRATOR SIDE")
        print(f"  NOT READ: no +migrators_j directory under {a.did} (pass --did).")
        print("  This is NOT a clean migrator side. It is an unmeasured one.")
        return 1

    print("empty-node ontology_term harvest (#70) -- MIGRATOR SIDE")
    print(f'  migrator files inspected      : {files}')
    print(f'  emissions with an empty node  : {len(rows)}')
    print(f'  baseline (must not increase)  : {BASELINE_MIGRATORS}')
    print()
    if files == 0:
        print("NOTHING WAS READ -- 0 migrator files. Treat this as a broken scan, "
              "not as a clean result.")
        return 1

    by_name = {}
    for r in rows:
        by_name.setdefault((r["migrator"], r["name"]), []).append(r)
    if rows:
        print("UNMINTED TERMS, by migrator and name:")
        for (mig, name), group in sorted(by_name.items()):
            label = name if name != "<computed>" else "<computed: {}>".format(group[0]["expression"])
            print(f'  {mig:<34} {label:<34} x{len(group)}')
            for r in group:
                print("      {}".format(r["site"]))
        print()

    if len(rows) > BASELINE_MIGRATORS:
        print(f'FAIL: {len(rows)} emissions, baseline {BASELINE_MIGRATORS}. A NEW unminted term was added. Either mint it, or raise BASELINE_MIGRATORS deliberately and say why.')
        if a.enforce:
            rc = 1
    elif len(rows) < BASELINE_MIGRATORS:
        print(f'Count has FALLEN below the baseline ({len(rows)} < {BASELINE_MIGRATORS}) -- terms were minted. Lower BASELINE_MIGRATORS to lock the gain in.')
    return rc


if __name__ == "__main__":
    sys.exit(main())
