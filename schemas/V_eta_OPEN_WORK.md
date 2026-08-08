# V_eta — OPEN WORK (the committed index)

**This file is the durable index of remaining work.** Every `#nn` reference in the plan
documents points here. The TaskList tool is a working mirror of this file, not the other way
round.

**WHY THIS FILE EXISTS.** On 2026-08-08 the container was re-provisioned mid-session and **all
68 tasks were wiped** — the same event reset this repo's working tree 274 commits back to an
older upstream revision. Everything pushed survived; everything living only in a task
description did not. The task list survives compaction and does not survive re-provisioning.
Only git does.

Reconstructed 2026-08-08 from the last complete listing. **Subjects and statuses are faithful;
the long descriptions are NOT recoverable** — where they held findings, those findings are in
the plan documents cited below, and where a row says *(description lost)* the detail is gone
and would need re-deriving.

`python3 tools/status_board.py` owns *decision* state. This file owns *build and repair* state.
They are different questions and they disagree on purpose: a family can be DECIDED here and
still be `awaiting a signature` there.

---

## OPEN

| # | subject | notes |
|---|---|---|
| 9 | D-C: analysis-tier decomposition (calc/tuning/spike zoo → observations + data_body + derived_from) | **in_progress** |
| 25 | software follow-ups: app retires BY ATTRITION (not a sweep) + dedup + crosswalk | |
| 27 | Build deferred: R5 infra renames (DID-only, NOT cross-repo — T11/T13) | R5's `_epoch_cache` is DANGEROUS, see `V_eta_ingested_payload_findings.md` |
| 28 | Build deferred: boundary-class dispositions (7 of 8) | |
| 29 | Build deferred: ensemble model | `V_eta_ensemble_plan.md` — SIGNED |
| 30 | Build deferred: raw recordings as typed observations | `V_eta_recording_observation_plan.md` |
| 31 | Build deferred: stimulus model | `V_eta_stimulus_model_plan.md` |
| 32 | **Binding governance (T8): bind `variable`/`method`; decide field-vs-registry authority** | **PREREQUISITE** for #45 and #65, not adjacent cleanup |
| 34 | Phase 1: make silent data loss impossible — REPORT-ONLY landed, enforcement open | |
| 35 | Phase 2: fix migrators reading invented field names — 17/17 closed AS SCOPED | |
| 37 | Phase 1.1: enforce mustBeNonEmpty on depends_on | fixes the 26,406-doc invented-empty-edge pattern |
| 38 | Phase 1.2: make an all-blank composite count as empty | |
| 43 | Phase 2b: 6 of 9 BLOCKING tombstones fixed; 3 stimulus rows held for #31 | |
| 45 | **DECIDED 2026-08-08: the data_body model — axes, datum, encoding** | `V_eta_data_body_model_plan.md`. BLOCKED ON #32 |
| 46 | Phase 3: retire ngrid, gated on BOTH consumers | **image / ngrid SIGNED 2026-08-08.** Gates: both consumers; both tombstones rewritten FROM THE WRITER; `dimension_labels` is the axis `variable` source, not the `dimension_order` letter; `data_limits` has no destination; re-verify the Hartley plane labels (`NDIcalc-vis-matlab` @ `65718ed`, out of session scope) |
| 47 | Phase 3: confirm the ontology_image raster has a home under R6 | **F5 CORRECTED**: ONE vintage, not two. Tombstone needs exactly `ontology_nodes`; drop `ontology_name` + `ontology_region`. DO NOT follow `check_tombstones.py` here — it compares against the TEMPLATE and the template loses to the writer |
| 48 | Phase 4: the RF/Hartley fold (group F) and the rest of the roadmap | |
| 51 | Verify `session` documents are present in every corpus | a CHECK, not a build; gates making `relative_to` REQUIRED |
| 52 | Role-name the `time_reference_#` statement edges | **SHRUNK 2026-08-08** to ONE rule: within a `_#` family every member describes the same instant/extent and `value.clock` is UNIQUE. Split-anchored intervals have NO INSTANCE — do NOT build `start_anchor`/`end_anchor` |
| 53 | `ontology_table_row` emits ~76,766 observations with an EMPTY `subject_id` | |
| 54 | Extend the vocabulary checker to `depends_on` names (the blind spot) | |
| 56 | Build deferred: strain entity + `strain_id` edge | `V_eta_openminds_family_record.md` Part 6 |
| 57 | Build deferred: the clock alignment cluster | `V_eta_clock_alignment_cluster_plan.md` |
| 58 | **URGENT: `syncrule_mapping` breaks a LIVE NDI query** — dropped `syncgraph_id` + `objectname` | |
| 59 | Build deferred: acquisition_system + software fold | GATED on #37. **2026-08-08: `acquisition_system ⊂ entity`**, beside software and session |
| 60 | Build deferred: the epoch family — MINT `epoch` entity, drop `epochid`, probemap → edges | `V_eta_epoch_plan.md`. **2026-08-08: `epoch.instrument_id -> entity`, OPTIONAL** |
| 61 | Build deferred: stimulus response family | `V_eta_stimulus_response_model_plan.md` |
| 62 | Build deferred: stimulus parameters | `V_eta_stimulus_parameter_plan.md` — GATED on #32 |
| 63 | Detector gap: a REQUIRED numbered edge (`name_#`) can never be checked | |
| 64 | Detector gap: attached files are never checked against the declared `file_list` | |
| 65 | **Build: the time-reference collapse — 8 classes to 2** | `V_eta_time_reference_model_plan.md` — **SIGNED 2026-08-08**. Increment 1 built but now STALE against the walkthrough. BLOCKED ON #67 + #32 |
| 66 | Build deferred: the ingested-payload family | `V_eta_ingested_payload_findings.md` |
| 67 | **Mint NDI clocktype terms in an ontology, then convert `clock` to `ontology_term`** | **NOW A PREREQUISITE of #65**, not a follow-up. FOUR terms: utc, dev_local_time, dev_global_time, exp_global_time |
| 68 | Define a `sampled_body` value rollup (`summary` dropped 2026-08-08) | rationale in `V_eta_data_body_model_plan.md` §9 |

## COMPLETED (kept so the `#nn` numbering stays stable)

1–8, 10–24, 26, 33, 36, 39–42, 44, 49, 50, 55.

```
 1 Track 1: flat-table-free J migrators          2 Track 2: dataseries -> data_body collapse
 3 Track 3: NDI-matlab second pass (Path-S)      4 ⑥/⑦ chunk (e): rename element_epoch
 5 ⑥/⑦ chunk (c): de-encode subtype-in-name      6 ⑥/⑦ chunk (b): fold data_body collisions
 7 ⑤ data_body collapse (2.D)                    8 ⑥/⑦ governance sweep
10 Lift local_identifier to entity              11 Binding-registry redesign
12 Path-S part-subjects: local_identifier       13 openMINDS full-field parity on entities
14 openMINDS crosswalk doc                      15 openMINDS round-trip CI test
16 Import-provenance document class             17 metadata_editor decomposition migrator
18 distance_metadata flat->nested endpoints     19 stimulus_presentation -> visual_grating_manip
20 Fix stimulusBathToBath V_eta path            21 V_eta home for new-on-main NDI classes
22 Fix TestMigrateLocalEta e2e                  23 subject_calculation composite-leaf family
24 Build: image model                           26 Build: tuning-curve collapse
33 Phase 0: extract did_v1 ground truth         36 Fix the false V_delta provenance line
39 Phase 1.3: vocabulary sweep --enforce in CI  40 Phase 1.4: FRAGMENT detector
41 Phase 2: measurement migrator + tombstone    42 Phase 2: daqreader epochid + fitcurve id
44 Phase 2b: electrode_offset_voltage tombstone 49 2.D half-built -> FOLDED INTO #45
50 Decide whether *_bounded_reference classes earn their existence
55 Board family #17 openMINDS — signed off 2026-08-05
```

---

## RE-DERIVED STATE for the rows whose descriptions were lost

Eight rows came back as a bare subject. Their *model* was never in the task — it is in the plan
documents — but their *progress annotation* was, and that is re-derived here from the documents
and the code, 2026-08-08. Where a figure could not be re-derived it says so.

**#9 — analysis-tier decomposition (in_progress).** Done: the 12 vision calculators fold 1→1
into `subject_calculation` leaves with ids and deps PRESERVED (Soph corpus run #2 / `b3e2e10`,
~101k docs, **0 orphans** — the 11,448-orphan dissolution failure does not recur); the tuning
collapse (#26); `kilosort_clusters` / `kiasort_clusters` decompose via
`migrators_j.private.jSorterOutput`. Remaining: the **ensemble second pass** (#29 — `member_of`
edges + the rebuildable cache, needs the `neuron_names.txt` read and neuron-id → subject
resolution) and the rest of the spike zoo. *Which spike-zoo classes were already walked is NOT
recoverable — re-derive from `+migrators_j/` before claiming coverage.*

**#25 — software follow-ups.** `app` → `software` entity + `software_id` edge +
`execution_environment` is BUILT (R1, signed). Remaining: `app` retires **by attrition, not by
a sweep**; software dedup; the openMINDS crosswalk.

**#28 — boundary-class dispositions, "7 of 8".** All eight are DECIDED
(`V_eta_tenet_audit.md` §"The boundary classes — ALL DECIDED"); seven carry a **⏳ build
deferred** marker and one is closed:

```
instrument            -> RETIRE                          mark retire in build_v_eta markers
projectvar            -> PASSTHROUGH   (retire evidence was FALSE — it IS an ndi v1 source)
demo_ndi(_mock)       -> PASSTHROUGH   (drop evidence was FALSE)  [since collapsed to `demo`]
interaction_purpose   -> KEEP standalone (purpose term + comment; interaction_id multiple >=1)
stimulus_presentation -> the timed_sequence model (#31), SUPERSEDES the dissolve
ensemble              -> per-neuron primary + group subject + derived cache (#29)
openminds_import      -> REVERSED 2026-07-30, REMOVED from the built set        <- the 8th, CLOSED
```

**#34 — Phase 1.** Phase 0 DONE. Phase 1 REPORT-ONLY landed with **1.3 and 1.4 BUILT** (the
vocabulary sweep enforces in CI; `did2.validate.isFragment` closes the FRAGMENT mode).
Remaining is the enforcement half: **1.1 (#37)** and **1.2 (#38)**. The plan's own rule:
*flip the sweep to enforcing when the offender count reaches zero.*

**#35 — Phase 2.** **CLOSED as scoped** — 17 offenders, all handled (6 fixed, 8 guarded
passthroughs, 1 tombstone-only, 2 allow-listed benign). What keeps it open is the scope
caveat, not the work: the 102-class v1 universe may be too small — `NDIcalc-ephys-matlab`
ships `spike_shape_calc`, absent from the ledger entirely — and the
`vhlab_voltage2firingrate` writer is in no repo we have (blocks `binnedspikeratevm`'s
Hz-vs-spikes-per-bin, a silent 33x risk).

**#38 — Phase 1.2.** Make an all-blank composite count as empty, so a document that satisfies
every required field with blank values is detected. Sibling of #37; both are the unbuilt
enforcement half of Phase 1.

**#48 — Phase 4.** "Remaining modelling" in `V_eta_ground_truth_plan.md`, plus the RF/Hartley
fold (group F) in `V_eta_ngrid_family_findings.md`, whose standing process rule is: **every
remaining item in that document is DECIDED BEFORE ANY BUILD.**

**#53 — ontology_table_row.** ~76,766 observations emitted with an EMPTY `subject_id`. The
invented-empty-edge pattern one layer up from the five classes #37 fixes. *The repair approach
was never written down outside the task — re-derive from `migrators_j/ontology_table_row.m`.*

---

## FINDINGS THAT LIVED ONLY IN TASK DESCRIPTIONS

Recovered here because the descriptions are gone. Everything else was already mirrored into a
plan document.

**The binding census (2026-08-08).** CLAUDE.md's "only SIX fields carry a binding" is stale:

```
DENOMINATOR: 226 schemas per index.json; 896 field nodes
fields carrying constraints.binding : 10
   dataset.accessibility / .ethics_assessment / .experimental_approach   (openMINDS)
   epoch_bounded_reference.epoch_clock
   epoch_relative_reference.epoch_clock
   frequency_filter.algorithm
   frequency_filter.band
   relative_reference.value.relation      (owl_time_interval)
   relative_reference.value.clock         (did_clocktype)
   term.value                             (the ONLY `keyed_by`, keyed_by: variable)
fields carrying constraints.enum    : 17
```

The count rose from 6 to 10 because this session's time-model increment 1 added the two
`relative_reference` bindings and `frequency_filter` added two.

**Microschemas are DESIGN ONLY and cannot be used.** `schemas/V_eta/microschemas/_DESIGN.md`
is a **V_delta** proposal whose own status line says: no meta-schema changes, no validator
changes, no CI checks, no microschemas added, no host classes converted. So the textbook
mechanism for "the type varies per document" — a discriminator selecting a body shape — **does
not exist**, which is why `conditions` uses three nested blocks with "exactly one populated"
enforced by an ingest validator instead (*"the closed meta-schema has no oneOf"*).

**Three unrelated fields named `kind`.** `datum.kind` (scalar|array|record, real enum),
`axes[].kind` (a quantity vocabulary, **prose only** — `constraints {}`), and
`subject_interaction.sample_time.kind` (point|grid|enumerated, real enum). Same trap as `mode`
meaning two different things in the time family.

**The class denominator.** `index.json` lists **226** schemas (stable 214, draft 11,
deprecated 1). Ad-hoc sweeps that count "files with a `document_class` block" get **224** —
they include the 2 example *documents* under `schemas/V_eta/examples/` and miss 4 stable
files. Examples are not in the index. An example document reads as a class declaration and
its concrete numbered edges (`time_reference_1`) read as untyped declarations; that produced a
false "defect" report on 2026-08-08.
