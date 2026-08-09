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
| 45 | **DECIDED 2026-08-08: the data_body model — axes, datum, encoding** | `V_eta_data_body_model_plan.md`. BLOCKED ON #32. **2026-08-09 ADDENDUM: the `axis` entry gains its own `datum_type`** — required when the axis is body-mounted and `regular` is false, i.e. when the coordinates are stored in the bytes. Found from `binaryseries_parameters`, which declares TWO encodings (`time_type` and `data_type`) where the plan had one. `byte_order` stays on `sampled_body` (one per file); only the element type varies per column. Without it the `binaryseries_parameters` fold drops the timestamp encoding. |
| 46 | Phase 3: retire ngrid, gated on BOTH consumers | **image / ngrid SIGNED 2026-08-08.** Gates: both consumers; both tombstones rewritten FROM THE WRITER; `dimension_labels` is the axis `variable` source, not the `dimension_order` letter; `data_limits` has no destination; re-verify the Hartley plane labels (`NDIcalc-vis-matlab` @ `65718ed`, out of session scope) |
| 47 | Phase 3: confirm the ontology_image raster has a home under R6 | **F5 CORRECTED**: ONE vintage, not two. Tombstone needs exactly `ontology_nodes`; drop `ontology_name` + `ontology_region`. DO NOT follow `check_tombstones.py` here — it compares against the TEMPLATE and the template loses to the writer |
| 48 | Phase 4: the RF/Hartley fold (group F) and the rest of the roadmap | |
| 51 | Verify `session` documents are present in every corpus | a CHECK, not a build; gates making `relative_to` REQUIRED |
| 52 | Role-name the `time_reference_#` statement edges | **SHRUNK 2026-08-08** to ONE rule: within a `_#` family every member describes the same instant/extent and `value.clock` is UNIQUE. Split-anchored intervals have NO INSTANCE — do NOT build `start_anchor`/`end_anchor` |
| 53 | `ontology_table_row` emits ~76,766 observations with an EMPTY `subject_id` | |
| 56 | Build deferred: strain entity + `strain_id` edge | `V_eta_openminds_family_record.md` Part 6 |
| 57 | Build deferred: the clock alignment cluster | `V_eta_clock_alignment_cluster_plan.md` |
| 59 | Build deferred: acquisition_system + software fold | GATED on #37. **2026-08-08: `acquisition_system ⊂ entity`**, beside software and session |
| 60 | Build deferred: the epoch family — MINT `epoch` entity, drop `epochid`, probemap → edges | `V_eta_epoch_plan.md`. **2026-08-08: `epoch.instrument_id -> entity`, OPTIONAL** |
| 61 | Build deferred: stimulus response family | `V_eta_stimulus_response_model_plan.md` |
| 62 | Build deferred: stimulus parameters | `V_eta_stimulus_parameter_plan.md` — GATED on #32 |
| 63 | **Express and ENFORCE cardinality on `name_#` edge families** | WIDENED 2026-08-08 from "a required numbered edge can never be checked". `mustBeNonEmpty: true` on a `_#` family is unenforceable AND meaningless — `silentLoss.requiredDependencies` excludes numbered edges, and its reasoning is right: *"a missing instance of one is not the same as a blank one."* You cannot check a blank `time_reference_3`; you CAN check **how many instances exist**, and the meta-schema has no way to say how many are required. **SIX families exist, THREE declared REQUIRED and verified by nothing**: `subject_interaction.time_reference_#` (the spine), `interaction_purpose.interaction_id_#`, `syncgraph.syncrule_id_#` — plus optional `directed_relation.time_reference_#`, `subject_calculation.derived_from_#`, `subject_observation.derived_from_#`. FIX: min/max on the edge declaration + a count check. Targets: `time_reference_#` min 1; `interaction_id_#` min 1; `acquisition_channels_#` min 2 max 2; `syncrule_id_#` min 0 (NDI's own schema says `"mustbenotempty": 0` — V_eta tightened it wrongly). **Naming the slots (`_A`/`_B`) was rejected** — that is `x_1`/`x_2` wearing letters, and for an unordered pair it creates two representations of one fact. Cardinality belongs in the declaration, not the names. Also closes the visibility half of #52. |
| 64 | Detector gap: attached files are never checked against the declared `file_list` | |
| 65 | **Build: the time-reference collapse — 8 classes to 2** | `V_eta_time_reference_model_plan.md` — **SIGNED 2026-08-08**. Increment 1 built but now STALE against the walkthrough. BLOCKED ON #67 + #32 |
| 66 | Build deferred: the ingested-payload family | `V_eta_ingested_payload_findings.md` |
| 67 | **Mint NDI clocktype terms in an ontology, then convert `clock` to `ontology_term`** | **NOW A PREREQUISITE of #65**, not a follow-up. FOUR terms: utc, dev_local_time, dev_global_time, exp_global_time |
| 68 | Define a `sampled_body` value rollup (`summary` dropped 2026-08-08) | rationale in `V_eta_data_body_model_plan.md` §9 |
| 69 | **Constraint refinement: a child cannot tighten a parent field — and redeclaring is SILENT** | opened 2026-08-08. `resolvePlacement`'s collision check fires only *within one* `targetBlock`, and the default `placement=declaring_class` puts ancestor and descendant in DIFFERENT blocks, so a redeclaration never trips it — and a cross-block duplicate name is checked NOWHERE (not `+did2/+schema`, not `+did2/+validate`, not DID-schema's tools or tests). Result: TWO live storage locations with nothing saying which is authoritative. **The docstring claims it errors; the code does not — read the code.** `build_v_eta.py:576` already defers "TIGHTENING a constraint rather than redeclaring it" to binding governance. MINIMAL FIX: merge a redeclaration into the ancestor's block entry and require the child to NARROW (`mustBeNonEmpty` false→true allowed, true→false an error). BUYS: `entity` declares the optional handle once and `subject`/`epoch` require it, collapsing 8 duplicate `local_identifier` declarations — today *"every entity has an optional handle"* is a convention held by NINE COPIES and a tenth subclass can omit it silently. COSTS: meta-schema + validator + `fieldsFor`'s contract. **Decide with #32.** Cheap interim: a DID-schema CI check that fails on one field name declared in two blocks of a chain, which at least makes it loud. Full write-up in the second correction block of `V_eta_epoch_plan.md`. |

| 72 | **Build deferred: the 8 unattached `openminds` documents (PROPOSED, not signed)** | opened 2026-08-08. Group A (all 8 in the corpora — Haley's E. coli food): 3 → `strain ⊂ entity` id-preserved, with `background_strain_1` from OP50-GFP's `backgroundStrain`; the other 5 are Species/GeneticStrainType FRAGMENTS consumed into the parents' `species`/`genetic_strain_type` fields; NO `term_assertion` (no subject). Group B (0 docs here, live production path — the metadata-app dataset graph): → the six classes `metadata_editor` already emits, no new classes. A SECOND-PASS assembler, not a `+migrators_j` file: the fragments are separate documents reachable only via the undeclared `openminds_#` edges. Rides with #53/#56 — `ontologyTableRow.bacteriaStrain` holds the strain document's ID in a plain table cell (`haley/doImport.m:164,734`), so the pass that mints row subjects is the pass that attaches `strain_id`, and id preservation is load-bearing. `V_eta_openminds_family_record.md` Part 7. |
| 73 | **Check: is `metadata_editor` always written alongside the openMINDS dataset graph?** | opened 2026-08-08. Decides whether #72 group B is a harmless duplicate or a total gap. `saveEditor2Doc` (writes `metadata_editor`) and `save_dataset_docs` (writes the bare-`openminds` graph) both have ZERO in-tree callers — both are entry points for the metadata-editor GUI, which is not in NDI-matlab. If the app can write one without the other, a submitted dataset's entire metadata record has no V_eta home. Needs the app repo, or a corpus containing a cloud submission. |

| 74 | **Build deferred: the settings model — `method_parameters` as a document + a bound `parameter` entry** | opened 2026-08-09, `V_eta_method_parameters_plan.md` "FINAL MODEL". The four spike-app settings classes fold into ONE generic `method_parameters` document (id + `base.name` preserved; optional `software_id`/`subject_id`/`epoch_id -> epoch`/`derived_from_id` — the last being LINEAGE only: precedence comes from the scope fields, not the edge), and `subject_interaction` gains an optional `method_parameters_id`. The settings SHAPE is a `parameter[]` entry modelled on the `axis` entry — identity in a BOUND `variable`, no `unit` field and no `data_type` field — named `method_parameters` in BOTH mount points — the inline field KEEPS its name; a 2026-08-09 proposal to rename it to `parameters` was reverted because `parameters` was deliberately vacated when the statement's field became `conditions`, and a document will carry three variable-keyed lists (`conditions`, `axes`, `method_parameters`) that must not be confusable — used BOTH inline and in the document, so a calculator's knobs and a spike app's knobs become queryable by the same mechanism. Routing is per class: the source gave it a name+id and things point at it → document; otherwise inline. FORBID BOTH on one statement (team, 2026-08-09). GATED on the registry carrying dimension + canonical unit (same extension the axis entry needs — the registry has 5 bindings today, none with a dimension). Supersedes the typed-blocks shape and the three rejected class names. |

| 75 | **Two signed plans send the 635 `StimulationApproach` documents to different places** | opened 2026-08-09. `migrators_j/openminds_stimulus.m` turns each into a `term_assertion` on the stimulus-subject; `V_eta_stimulus_model_plan.md:126-132` says an approach term becomes an `interaction_purpose` on the epoch's interaction. Both cannot be right, and the `term_assertion` route is independently broken (#71 — empty `subject_id`, because the migrator reads `stimulus_id` while NDI writes `stimulus_element_id`). **RESOLVED 2026-08-09: `interaction_purpose`.** The assertion branch is timeless by construction (`time_reference_#` is on `subject_interaction`, the other branch), so a `term_assertion` cannot carry the epoch the writer sets — and today's migrator drops it outright while asserting, falsely and timelessly, that the stimulator IS-A spatial-frequency-tuning. **So #71 is fixed by RE-TARGETING: pass 1 emits nothing and passes these through guarded; the build is a SECOND PASS** that resolves epoch+stimulator to the interactions. Rationale in `V_eta_go_forward_class_audit.md`. |

| 76 | **MEASURE: does one approach cover several interactions?** (decides whether `interaction_purpose` collapses to a field) | opened 2026-08-09. Named in the `misc singletons` sign-off as the one open item. **THE MEASUREMENT:** for every `openminds_stimulus` document take its `epochid`, then count the DISTINCT SUBJECTS among the `stimulus_presentation` documents sharing that epoch; the distribution of that count over the 635 is the answer. One subject per epoch → one purpose maps to one interaction and `purpose` should be a FIELD on `subject_interaction` (removing a class and a numbered required edge, which #63 says is unverifiable anyway); several subjects → the class earns its `interaction_id_#`. **NOT MEASURABLE from the dev container — no corpora on disk** — and the census reports by class only, so it needs a grouped count added plus a full corpus run (~1–2 h). **DO NOT substitute the class totals**: 635 approaches against 2,670 `stimulus_presentation` is not a ratio, because only some datasets write approaches at all, so the two counts come from different populations. **Already settled structurally from the writers, so do not re-derive:** an epoch may carry SEVERAL approaches (`add_stimulus_approach.m` reads a table of (Epoch, Approach) rows and dedups on (epochid, name); `stimulusDocMaker.m:342-380` takes a cell array of approach strings and emits one document each), and the stimulator is SINGULAR (`probe = S.getprobes('type','stimulator'); probe = probe{1}`) — so the purpose cannot be folded onto the epoch either. |

| 77 | **Regression surfaced by the vocabulary checker: `measurement.m`** | opened 2026-08-09. The checker reports it reading `measurement_class` and `parameters`, and it is NOT on the known-broken list — so by the tool's own contract this is a regression, not a legacy offender. NOT yet verified against the template and the writer, which is the only thing that settles it (the tool's rows are a place to go and read). Do that before touching the migrator. |

## COMPLETED (kept so the `#nn` numbering stays stable)

**70 — the empty-node backlog is visible and ratcheted (2026-08-09).**
`tools/check_empty_ontology_nodes.py` sweeps the J migrators for
`jOntologyTerm('', <name>)` and reports every emission grouped by (migrator, name),
denominator first. **Current state: 33 emissions across 82 migrator files.** Wired into
DID-matlab's fast gate (`--enforce`) rather than DID-schema CI, because the migrators live
there and that is where an edit adding one would break it. The count may FALL freely; any
INCREASE fails, so minting is always allowed and adding a new unminted term has to move
`BASELINE` deliberately. **NO SENTINEL IS WRITTEN INTO THE DATA** — the instrument is the
record; a marker in `node` would make the schema carry our bookkeeping and be
indistinguishable from a real CURIE to a later reader. Names passed as VARIABLES report as
`<computed>` with their call site: the count is exact, the term list is only as specific as
the source allows. Minting the terms themselves is still open — it rides with #32 and #67.

**54 — the vocabulary checker now covers dependency names, both directions (2026-08-09).**
`check_tombstones.py` already compared a V_eta class's declared edges against the NDI
template (declared-but-not-written — the invented-empty-edge pattern). The direction NOTHING
could see was the reverse: a WRITER appending an edge no template declares, because both
checkers compare against the template and the template does not have it either.
`tools/ndi_ground_truth.py` gained a `writer_dependencies` sweep of NDI's `.m` files for
`set_dependency_value` / `add_dependency_value_n`, joining MATLAB `...` continuations (the
live call site spans lines, and a line-at-a-time scan found only one of its two sites).
`check_migrator_vocabulary.py` reports it. Current finding: **`openminds`, 2 writer sites**
— the openMINDS pedigree edges carrying a Strain's backgroundStrain graph, declared by no
template and no V_eta class. Tested (`test_writer_set_dependencies_are_reported`) so an
empty result must mean "none found" rather than "the scan broke", which is the silentLoss
failure. THE SWEEP IS TEXTUAL: a row names call sites, not a proven per-class mapping.

**58 — `syncrule_mapping`: the live NDI query works again (2026-08-09).** V_eta declared a
REQUIRED `epochid` dependency that no did_v1 document has (empty on all 5,316 corpus
documents) and declared NEITHER of the two things `+ndi/+time/syncgraph.m:404-408` reads:
the `syncgraph_id` edge and `epochnode_a/_b.objectname`. The schema now declares
`syncgraph_id` + `syncrule_id` (both REQUIRED, as NDI's template and schema do), and the
migrator's `reshapeEpochNode` carries `objectname` and `t0_t1` instead of discarding them.
The DID-schema test that asserted the phantom `epochid` "untyped by design", and the
migrator fixture built on the same invented shape, are INVERTED not updated. **This is the
interim repair, not the model** — the class dissolves into `clock_alignment` under #57, and
its `time_reference` sub-structure still names `epoch_bounded_reference`, a class the time
collapse removes.

**71 — `openminds_stimulus` stops emitting hollow statements (2026-08-09).** The tombstone
declares `stimulus_element_id` (template, schema and writer all agree) instead of the
invented `stimulus_id`; the migrator emits NOTHING and passes the document through guarded,
because correcting the name alone would still have produced 635 well-formed statements in
the timeless assertion tier, without the epoch the writer sets. Destination is
`interaction_purpose` via the second pass — that build rides with #75/#31. The curated
target map and the generated coverage ledger were re-pointed so they stop asserting a
target that is not produced. Unit test inverted; both fixtures rebuilt from the writer.
CI: quick migrator gate run #150 green.


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
~101k docs, **0 orphans** — the 11,448-orphan dissolution failure does not recur) and the
tuning collapse (#26).

**The spike zoo, RE-DERIVED 2026-08-08 from `+migrators_j/` (60 top-level migrators, 22 private
helpers). All eleven classes have a migrator; the split is 5 folded / 6 deliberately deferred:**

```
FOLDED
   jrclust_clusters                 -> observation + sampled_body (one datum per spike)
   kilosort_clusters                -> D-C shape: count_observation + opaque_body + anchor
   kiasort_clusters                 -> D-C shape: count_observation + opaque_body + anchor
                                       (both via migrators_j.private.jSorterOutput)
   neuron_extracellular             -> emits
   vmspikefit                       -> emits

DEFERRED to the NDI second pass — passed through UNCHANGED, by design, each with a
guarded `bodies = {preBody}` and a header saying so
   binnedspikeratevm                <- CARRIES THE KNOWN OPEN RISK: Hz vs spikes-per-bin.
                                       The vhlab_voltage2firingrate writer is in no repo we
                                       have, so the units are unverified — a silent 33x risk
   spike_clusters
   spike_interface_sorting_outputs  <- num_units does not exist; the count is inside the .zip
   spikewaves
   vmspikesummary                   <- models a DIFFERENT document than exists: the real class
                                       is a mean spike WAVEFORM + 8 shape medians
   vmneuralresponseresiduals
```

So "the rest of the spike zoo" is **not unwritten migrators** — it is six deliberate
second-pass deferrals plus the **ensemble** (#29: `member_of` edges + the rebuildable cache,
needing the `neuron_names.txt` read and neuron-id → subject resolution). There is no
`ensemble.m` in `+migrators_j`, which is consistent with #29 being unbuilt.

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

**#53 — ontology_table_row. RE-DERIVED 2026-08-08, and the subject line overstates it: the
bleeding is already STOPPED.** The repair was written down — in the migrator itself, not in the
task.

The defect, as the code records it: the real NDI template declares exactly one dependency and
it is not the one the migrator scanned for —

```
ndi_common/database_documents/data/ontologyTableRow.json
   depends_on: [ { "name": "document_id", "value": "" } ]
```

— so `carrySubject`'s scan for a `subject_id` dependency never succeeded on a real document and
every statement was emitted with `subject_id = ''`. **Corpus run #256 measured 76,766 on Dab
alone** — intensity, count, term, duration, frequency, date_assertion, term_assertion — each
recording that SOMETHING was measured without recording WHAT. All of it passed validation,
because `references.m` skips empty edges and `mustBeNonEmpty` on a `depends_on` is not enforced.

**What is already built:**

```
1. A GUARD in the main function:  if isempty(resolvedSubject(preBody))
                                      bodies = {preBody};  return;   % pass through whole
2. carrySubject now ERRORS rather than emitting an empty edge:
      error('did2:convert:noSubject', 'refusing to emit a statement with an empty subject_id …')
   with the comment: "if it ever does, the guard has been removed and 76,766 hollow
   observations per corpus are back."
3. Mapped tables (isEncounterTable / isPatchGeometryTable) resolve their subject explicitly
   and never reach the guard.
```

**And the approach that was REJECTED, with its reason** — worth keeping, because it is the
obvious-looking fix: `document_id` **cannot** simply be renamed to `subject_id`. It points at
the document the row describes, which need not be a subject, and *"minting an unresolvable edge
is what turned `distance_metadata`'s non-gating quarantine into a GATING orphan failure."*

**What actually remains:** the NDI second pass, which can see the migrated-id graph and resolve
the subject. Until it lands these documents pass through unconverted — which is a deliberate
deferral, not a loss. Same treatment `ontology_label` got.

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
