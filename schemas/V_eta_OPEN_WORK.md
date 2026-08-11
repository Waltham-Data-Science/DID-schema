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
| 29 | Build deferred: ensemble model | `V_eta_ensemble_plan.md` — SIGNED. **NEW 2026-08-09, from the ground-truth extractor fix:** NDI's SCHEMA document declares a third edge the template does not — `ensemble_schema.json` has `element_id` (req), `element_epoch_id` (req) and **`neuron_id` (`mustbenotempty: 0`)** — and V_eta declares no `neuron_id` at all. This was invisible until the extractor started reading `schema_documents/` as well as `database_documents/`. It bears directly on the signed model, which makes the per-epoch roster `member_of` edges: NDI already has a per-neuron edge here, so check whether `member_of` is re-inventing it before building. |
| 30 | Build deferred: raw recordings as typed observations | `V_eta_recording_observation_plan.md` |
| 31 | Build deferred: stimulus model | `V_eta_stimulus_model_plan.md` |
| 32 | **Binding governance (T8): bind `variable`/`method`; decide field-vs-registry authority** | **PREREQUISITE** for #45 and #65, not adjacent cleanup |
| 34 | Phase 1: make silent data loss impossible — REPORT-ONLY landed, enforcement open | |
| 35 | Phase 2: fix migrators reading invented field names — 17/17 closed AS SCOPED | **THE SCOPE HAD A HOLE, found 2026-08-09: fixing a migrator did not fix its TOMBSTONE.** `migrators_j/vmspikefit.m` was repaired to read `fit_equation`/`fit_sse` once it was established that `fit_function` and `r_squared` have never existed on the NDI template (0 commits mention either, against 7 for `fit_equation`/`fit_sse`; both names came from V_alpha). The V_eta tombstone was left declaring **exactly those two invented names, with `fit_function` REQUIRED**, and none of the seven real fields — plus it had dropped the `epochid`+`app` superclasses, dropped `fit_input_id`, and invented a `vmspikefit_file` the template does not have. NOW REPAIRED from the template. It was not firing only by luck: the migrator consumes every document (1 → score_observation + anchor) so nothing reaches validation under the class, but the class is not phase-8 deleted and so still advertises itself as describing a document that has never existed. **THE OTHER 16 WERE CHECKED THE SAME DAY AND THREE MORE HAD IT.** `probe_geometry` was the sharpest: its tombstone declared `channel_positions`, `position_units` and `probe_type` — **the exact three names its own migrator RAISES on, by name, as proof that a body was built against our schema instead of a real document** (`migrators_j/probe_geometry.m:70-77`) — plus a REQUIRED `num_channels` no document has. So the schema described the shape the migrator rejects as impossible. `position_metadata` declared a REQUIRED `measurement`, which is the name the MIGRATOR gives its OUTPUT field: the tombstone had been written from the migrator's target instead of its source, so the one real descriptive field (`ontologyNode`) went undeclared. `fitcurve` is `vmspikefit`'s twin — same invented `fit_function`, same missing real fields. All four now restated from NDI's template + schema; `check_tombstones` went 22 rows → 16, and the LOSSY *passthrough* tier is empty. **A FIFTH WAS NEARLY 'REPAIRED' AND WOULD HAVE BEEN BROKEN.** The checker reports `filter` as declaring `filter_type` (in no NDI template) and missing the real `type`. Both true of the template, both irrelevant: `+did2/+convert/+migrators/filter.m:29-34` performs exactly that rename and DELETES `type`, and it still runs under V_eta — `runConcreteMigrator` falls back to the V_delta `+migrators` package whenever no `migrators_j` entry exists (`v1_to_v2.m:393-402`), there is no `migrators_j/filter.m`, and `filter` is a SUPERCLASS migrator applied to everything declaring it (`pyraview`, chiefly). Declaring `type` would have left the real field undeclared and the declared one permanently blank — introducing the very defect the sweep exists to remove. **The checker compares against the v1 template and cannot see a migrator that legitimately renames: its output is a STARTING POINT, NOT AN INSTRUCTION, and the thing to check is what actually runs.** **ONE DEFECT FOUND THAT IS NOT A TOMBSTONE AND NEEDS A DECISION** — see the fitcurve subject-attribution entry below. |
| 37 | Phase 1.1: enforce mustBeNonEmpty on depends_on | fixes the 26,406-doc invented-empty-edge pattern |
| 38 | Phase 1.2: make an all-blank composite count as empty | |
| 43 | Phase 2b: **8 of 9 BLOCKING tombstones fixed; 1 stimulus row left** | **2026-08-10**: `stimulus_parameter` + `stimulus_parameter_table` restated from NDI origin/main, so `check_tombstones.py` BLOCKING went 3 -> 1. Both shared ZERO field names and ZERO edge names with their templates and would have quarantined every document twice over (`undeclaredField` on what the document carries, `missingField` on the invented required name). The remaining row is `stimulus_presentation`, still held for the stimulus model (#31) deliberately -- it needs `presentation_time` and `stimulus_element_id`, which that model decides. |
| 45 | **DECIDED 2026-08-08: the data_body model — axes, datum, encoding** | `V_eta_data_body_model_plan.md`. BLOCKED ON #32. **2026-08-09 ADDENDUM: the `axis` entry gains its own `datum_type`** — required when the axis is body-mounted and `regular` is false, i.e. when the coordinates are stored in the bytes. Found from `binaryseries_parameters`, which declares TWO encodings (`time_type` and `data_type`) where the plan had one. `byte_order` stays on `sampled_body` (one per file); only the element type varies per column. Without it the `binaryseries_parameters` fold drops the timestamp encoding. |
| 46 | Phase 3: retire ngrid, gated on BOTH consumers | **image / ngrid SIGNED 2026-08-08.** Gates: both consumers; both tombstones rewritten FROM THE WRITER; `dimension_labels` is the axis `variable` source, not the `dimension_order` letter; `data_limits` has no destination; re-verify the Hartley plane labels (`NDIcalc-vis-matlab` @ `65718ed`, out of session scope) |
| 47 | Phase 3: confirm the ontology_image raster has a home under R6 | **F5 CORRECTED**: ONE vintage, not two. Tombstone needs exactly `ontology_nodes`; drop `ontology_name` + `ontology_region`. DO NOT follow `check_tombstones.py` here — it compares against the TEMPLATE and the template loses to the writer |
| 48 | Phase 4: the RF/Hartley fold (group F) and the rest of the roadmap | |
| 51 | Verify `session` documents are present in every corpus | **ANSWERED 2026-08-09 — PASSES on all six.** Corpus run 31327383671, the first census that was readable (the digest had been aggregating nothing). Session documents are present in every corpus and are 1:1 with the distinct `base.session_id` values, so the referent a required `relative_to` needs exists everywhere it would be demanded: 20211116 1/1, B 14/14, Dab 16/16, JH 3/3, PRED 1/1, Soph 33/33 (0 unreadable, 0 skipped documents). This also settles the correction recorded in `V_eta_time_reference_model_plan.md`: the claim that NO session document exists anywhere was false, and the measurement now says so rather than the argument. The BUILD it gates (making `relative_to` required) is still blocked behind the time-reference collapse. |
| 52 | Role-name the `time_reference_#` statement edges | **SHRUNK 2026-08-08** to ONE rule: within a `_#` family every member describes the same instant/extent and `value.clock` is UNIQUE. Split-anchored intervals have NO INSTANCE — do NOT build `start_anchor`/`end_anchor` |
| 53 | `ontology_table_row` emits ~76,766 observations with an EMPTY `subject_id` | |
| 57 | **Build: the clock alignment cluster — MIGRATOR half** | `V_eta_clock_alignment_cluster_plan.md`. **SIGNED 2026-08-08** (two `TEAM-SIGN-OFF` lines, one per family). **SCHEMA HALF BUILT 2026-08-09**: `polynomial ⊂ data_type` (coefficients HIGHEST ORDER FIRST + a `degree` kept because did2 has NO length predicate, so `degree > 1` is expressible only if stored), `clock_alignment ⊂ relation, polynomial` (named `from_reference`/`to_reference` endpoints — the rule is symmetric, its OUTPUT is directed — plus `cost` on the leaf, not in `value`), `clock_alignment_configuration` (was syncrule), `clock_alignment_policy` (was syncgraph), `acquisition_channels` (the devicestring decomposition, grouped not flat). **GATE 3 IS NOW MET**: #63 landed, so `acquisition_channels_#` carries a real `min_count: 2, max_count: 2` instead of the word "EXACTLY 2" in a plan. **THIS ROW SAT UNBUILT FOR A DAY BECAUSE TWO PIECES OF PROSE SAID IT WAS A PROPOSAL** — the plan's own header ("NO `TEAM-SIGN-OFF` LINE", 474 lines above two of them) and `V_eta_epoch_plan.md:451`. Both corrected. The status board was right the whole time; it derives from the sign-off lines, which is Operating Rule 4 doing its job. **STILL OPEN, all migrator + still gated**: (a) **#67 gates this cluster** — `clock_alignment_configuration.clock` binds to `did_clocktype`, whose 4 terms have no ontology nodes yet, and `clock_alignment.relation` needs an NDIC term for "temporally aligned with" (a MAPPING predicate, so it cannot reuse relative_reference's OWL-Time binding); both staged `{node: '', name: ...}` per the plan's §5 and counted by #70. (b) `acquisition_channels.acquisition_system_id` is UNTYPED — `acquisition_system` is #59's class, itself gated on #37. (c) the migrators; until they exist `syncrule`, `syncgraph` and `syncrule_mapping` REMAIN as v1 source tombstones and must not be deleted. |
| 59 | Build deferred: acquisition_system + software fold | GATED on #37. **2026-08-08: `acquisition_system ⊂ entity`**, beside software and session |
| 60 | **Build: the epoch family — MIGRATOR half** | `V_eta_epoch_plan.md`. **SCHEMA HALF LANDED 2026-08-09**: `epoch ⊂ entity` is minted (local_identifier REQUIRED — 30 live NDI sites join on that string; session_id REQUIRED; `time_reference_#` min 0; `instrument_id -> entity` OPTIONAL), and `epochfiles_ingested` is RENAMED `ingestion_manifest` with `filenavigator_id` RESTORED and a real `epoch_id`. STILL OPEN, all migrator work: mint one `epoch` per distinct `epochid.epochid` by GROUPING (a second pass — a single-document migrator cannot see the group); rewire the 15 `epochid`-carrying classes to `epoch_id`; dissolve `acquisition_epoch` (its clocks become `relative_reference` documents, which is BLOCKED behind #65 → #67/#32); drop the `epochid` class itself. Nothing may be deleted until the corpus proves the fold. | **REGRESSION FOUND AND FIXED BY CORPUS RUN #2 (2026-08-09): the schema half DELETED the source tombstone.** `epochfiles_ingested.json` was removed the moment `ingestion_manifest` was minted, and nothing migrates those documents yet — so every one reached validation under a class with no schema. **Corpus B: 2,484 quarantines**, on a 0-quarantine gate. This is precisely what `_DELETE_PHASE8` exists to prevent (a source class may be removed ONLY once its documents provably cannot survive migration) and the rename bypassed it by deleting the file directly. The tombstone is restored from the NDI template — `filenavigator_id`, `epoch_id` char, `files`, `epochprobemap` carried verbatim — and leaves for real when the fold lands and a corpus proves it. `test_phase1_source_cleanup_and_dep_typing` asserted the class was GONE, i.e. it was written from the same premise as the code and could not catch it; INVERTED, the third time that lesson has been paid for.
| 61 | **Build: stimulus response family — MIGRATOR half** | `V_eta_stimulus_response_model_plan.md`. **SCHEMA HALF LANDED 2026-08-09**: `harmonic_component ⊂ data_type` (abstract; value = harmonic 0/1/2 + real/imaginary + control_real/control_imaginary, the control kept BESIDE the response because v1 stores them together and a control is meaningless apart from what it controls for) and `harmonic_component_calculation ⊂ subject_calculation, harmonic_component`. STILL OPEN, all migrator: the v1 scalar/vector/tuning folds; RECOVERING the dropped `instrument_id` (stimulator, T7) and `derived_from_#` (presentation + control) edges; `responses.stimid -> axes[] variable: stimulus`; **THE LARGEST INVENTED-EMPTY-EDGE INSTANCE IS NOW REPAIRED, SCHEMA-SIDE (2026-08-09).** `stimulus_response_scalar_parameters.stimulus_response_scalar_id` — 11,440 documents, 100% of the class — is GONE: NDI's template declares NO dependencies on that class at all, and the real edge runs the other way (`stimulus_response_scalar` → `stimulus_response_scalar_parameters_id`, `mustbenotempty: 1`, set at `+ndi/+app/+stimulus/tuning_response.m:323`). `stimulus_response_scalar.stimulus_response_id` — a name no did_v1 document carries — is replaced by that real edge, answering the suspicion the 8d build comment had already recorded. TWO REAL REQUIRED EDGES WERE ALSO RESTORED: `stimulator_id` (T7, the instrument that delivered the stimulus, `tuning_response.m:328`) and `stimulus_control_id` (`:327`), both `mustbenotempty: 1` in NDI and both simply dropped, so a migrated response could not say what stimulated the subject or what it was compared with. NO CORPUS RISK, and the reason is worth keeping: `ensureClassBlocks` never touches `depends_on` and `references.m` walks the DOCUMENT's edges, not the schema's — so these documents already carried and already resolved these ids; the schema was merely lying about them. `check_tombstones.py` cleared 3 rows (2 LOSSY + 1 COSMETIC) and the family now produces no output at all. **NOTE THE CHECKER HAD BEEN REPORTING TWO OF THESE AS LOSSY ALL ALONG** — `real dependencies not declared: stimulator_id, stimulus_control_id` — and nobody had acted on it; a report nobody reads is the same as no report. STILL OPEN, all migrator: The 3 stimulus tombstones held under #43 ride with it. |
| 62 | Stimulus parameters: **tombstone repair BUILT; dissolution still gated** | `V_eta_stimulus_parameter_plan.md`. **2026-08-10**: the repair required under BOTH signed options is done (see #43). Decision C is COMPLETE -- `stimulus_parameter_table` is a deprecated/ passthrough with the NDI shape. Decision A (dissolve `stimulus_parameter` into a typed leaf keyed by its CURIE) is NOT built and now has TWO live gates, not one: (a) #32 signed at `preferred` on 2026-08-10, which is not yet the ADMISSIBLE SET that dissolution needs -- an unregistered CURIE would have no typed home; (b) the plan's own OPEN item 3, UNMEASURED: how many distinct `ontology_name` values a real Marder corpus carries and how many resolve through the D9 registry. That measurement needs a Marder corpus, and none of the six we run is one. |
| 65 | **Build: the time-reference collapse — 8 classes to 2** | `V_eta_time_reference_model_plan.md` — **SIGNED 2026-08-08**. Increment 1 built but now STALE against the walkthrough. BLOCKED ON #67 + #32 |
| 66 | **Build: the ingested-payload family — MIGRATOR half** | `V_eta_ingested_payload_findings.md`. **SCHEMA HALF LANDED 2026-08-09**: `acquisition_metadata_file ⊂ base` (a `data.bin` file, `acquisition_metadata_reader_id` + `epoch_id`, both REQUIRED) and `acquisition_metadata_reader ⊂ base` beside it. The earlier claim that this family needs no new class was WRONG for a structural reason now recorded in the plan: `sampled_body` and `opaque_body` BOTH require a `statement` edge, and a per-epoch metadata blob is not an observation of any subject, so there is no statement for a body to hang from. STILL OPEN: the migrators that route `daqmetadatareader_epochdata_ingested` and its siblings onto it, which need `epoch` documents to exist first (#60's migrator half). |
| 67 | **Mint NDI clocktype terms in an ontology, then convert `clock` to `ontology_term`** | **NOW A PREREQUISITE of #65**, not a follow-up. FOUR terms: utc, dev_local_time, dev_global_time, exp_global_time |
| 68 | Define a `sampled_body` value rollup (`summary` dropped 2026-08-08) | rationale in `V_eta_data_body_model_plan.md` §9 |
| 69 | **Constraint refinement: a child cannot tighten a parent field — and redeclaring is SILENT** | opened 2026-08-08. `resolvePlacement`'s collision check fires only *within one* `targetBlock`, and the default `placement=declaring_class` puts ancestor and descendant in DIFFERENT blocks, so a redeclaration never trips it — and a cross-block duplicate name is checked NOWHERE (not `+did2/+schema`, not `+did2/+validate`, not DID-schema's tools or tests). Result: TWO live storage locations with nothing saying which is authoritative. **The docstring claims it errors; the code does not — read the code.** `build_v_eta.py:576` already defers "TIGHTENING a constraint rather than redeclaring it" to binding governance. MINIMAL FIX: merge a redeclaration into the ancestor's block entry and require the child to NARROW (`mustBeNonEmpty` false→true allowed, true→false an error). BUYS: `entity` declares the optional handle once and `subject`/`epoch` require it, collapsing 8 duplicate `local_identifier` declarations — today *"every entity has an optional handle"* is a convention held by NINE COPIES and a tenth subclass can omit it silently. COSTS: meta-schema + validator + `fieldsFor`'s contract. **Decide with #32.** **CHEAP INTERIM BUILT 2026-08-09** — `tools/check_duplicate_field_declarations.py`, enforced in CI and asserted in `tests/test_veta.py`. A RATCHET (baseline 8): the count may fall freely, any increase fails, and a count BELOW the baseline fails too so ground won is not quietly given back. **IT FOUND EIGHT ROWS, and the split matters** — 5 are V1 FIDELITY (NDI's own templates declare a class-block `name` beside `base.name`: `element`, `measurement`, `probe_location`, plus `subjectmeasurement.datestamp` and `pyraview.label` over `filter.label`; a tombstone that dropped these would stop matching the writer, so they are correct and must stay). The other 3 are V_eta TARGET classes where no template forces it and the question is genuinely open: `software.name` (carried in from its v1 source — `app` declares `name`), and **`method_parameters.name` + `strain.name`, both minted in the 2026-08-09 session with the duplicate unnoticed at the time**. That is the argument for the check, made against its own author: two classes acquired a silent second storage location for `name` in the same session that recorded the defect. THE REMAINING DECISION is which block is authoritative for those three — not a build; it rides with binding governance. Full write-up in the second correction block of `V_eta_epoch_plan.md`. |

| 72 | **Build deferred: the 8 unattached `openminds` documents (PROPOSED, not signed)** | **NEW 2026-08-09: the `openminds` edge is DECLARED BY NDI, not merely written by it.** `schema_documents/metadata/openminds_schema.json` declares a dependency literally named `openminds` (`mustbenotempty: 0`); the template declares none, and V_eta declares none. #54's writer sweep had already found 2 writer sites setting it — the schema now confirms it independently, so the `openminds_#` fragment edges this build depends on are NDI's own design and not an artifact of `ErrorIfNotFound, 0`. opened 2026-08-08. Group A (all 8 in the corpora — Haley's E. coli food): 3 → `strain ⊂ entity` id-preserved, with `background_strain_1` from OP50-GFP's `backgroundStrain`; the other 5 are Species/GeneticStrainType FRAGMENTS consumed into the parents' `species`/`genetic_strain_type` fields; NO `term_assertion` (no subject). Group B (0 docs here, live production path — the metadata-app dataset graph): → the six classes `metadata_editor` already emits, no new classes. A SECOND-PASS assembler, not a `+migrators_j` file: the fragments are separate documents reachable only via the undeclared `openminds_#` edges. Rides with #53/#56 — `ontologyTableRow.bacteriaStrain` holds the strain document's ID in a plain table cell (`haley/doImport.m:164,734`), so the pass that mints row subjects is the pass that attaches `strain_id`, and id preservation is load-bearing. `V_eta_openminds_family_record.md` Part 7. |
| 73 | **Check: is `metadata_editor` always written alongside the openMINDS dataset graph?** | opened 2026-08-08. Decides whether #72 group B is a harmless duplicate or a total gap. `saveEditor2Doc` (writes `metadata_editor`) and `save_dataset_docs` (writes the bare-`openminds` graph) both have ZERO in-tree callers — both are entry points for the metadata-editor GUI, which is not in NDI-matlab. If the app can write one without the other, a submitted dataset's entire metadata record has no V_eta home. Needs the app repo, or a corpus containing a cloud submission. |

| 74 | **Build: the settings model — MIGRATOR half** | `V_eta_method_parameters_plan.md` FINAL MODEL, SIGNED. **SCHEMA HALF LANDED 2026-08-09**: `method_parameters ⊂ base` is minted (name; a `method_parameters[]` entry list keyed by a bound `variable`, with no `unit` and no `data_type` field; an `other` bag; `software_id`/`subject_id`/`epoch_id`/`derived_from_id`), and `subject_interaction` gains an OPTIONAL `method_parameters_id`. STILL OPEN, all of it cross-repo: RETYPING the inline `subject_interaction.method_parameters` from `structure` to the entry list BREAKS every calculator migration (`jCalculation.m:99` writes a struct there), so it is a lockstep change; the four spike-settings classes need their migrator; `forbid both inline and edge` needs enforcing; and the bound variables themselves ride with #32. |

| 75 | **CLOSED 2026-08-11: there were never two signed plans. One plan and one migrator, and the migrator was already re-targeted.** | opened 2026-08-09 as *"two signed plans send the 635 `StimulationApproach` documents to different places"*: `migrators_j/openminds_stimulus.m` turned each into a `term_assertion` on the stimulus-subject; `V_eta_stimulus_model_plan.md:126-132` says an approach term becomes an `interaction_purpose` on the epoch's interaction. **THE PREMISE IS THE PART THAT WAS WRONG, and it is worth naming because it is the expensive kind of wrong** — it framed a code defect as a clash between two team decisions, i.e. as something nobody but the team could touch. Read literally, the row's own text names ONE plan document and ONE `.m` file. **DENOMINATOR: 54 markdown files under `schemas/`, 54 read, 24 `TEAM-SIGN-OFF` lines (23 real + the format template at `V_eta_STATUS.md:216`).** Exactly ONE names these documents — `V_eta_go_forward_class_audit.md:3`, `TEAM-SIGN-OFF [misc singletons]: jess, 2026-08-09`, *"`interaction_purpose` … is the destination for the 635 `StimulationApproach` documents via a second pass -- so #71 is repaired by re-targeting, with pass 1 emitting nothing"*. Exactly TWO mention `term_assertion` at all, both in `V_eta_openminds_family_record.md` (:10, :20) and **both about STRAIN** — :20 makes `strain_id` an optional edge ON a term_assertion, :10 says *"no `term_assertion` is emitted, because there is no subject"*. Neither routes an approach term anywhere. Corroborating: `tools/status_board.py` FAMILIES gives the openMINDS family the class list `['openminds']` — `openminds_stimulus` is not in its scope — while `interaction_purpose` belongs to `misc singletons`, whose document is the sign-off above. So the two SIGNED artifacts that speak to these documents ([stimulus] 2026-08-08 via its body at :124-132, and [misc singletons] 2026-08-09 naming the 635 outright) **agree**; the dissenting `term_assertion` route was migrator code, and pass 1 stopped emitting it when #71 landed (`openminds_stimulus.m:84` is now `bodies = {preBody}` behind a `stimulus_id` guard; the tombstone declares `stimulus_element_id` + the `epochid` superclass). Nothing was chosen here and no disposition was recorded — the team had already decided, twice. **What is still OPEN is the BUILD, and it is #31/#76a, not this row**: the second pass must resolve epoch+stimulator to interactions, and #76a measured that the epoch string cannot do it (in Dab all 635 approach epoch ids carry an `epoch_` prefix, all 1,242 presentation epoch ids do not, shared ids: 0). The surviving join is the stimulator — both classes point at one via `stimulus_element_id`, so `(base.session_id, stimulus_element_id)` crosses the namespace gap. Until that pass exists the guarded passthrough is the answer: `interaction_purpose.interaction_id_#` is `min_count: 1`, and emitting it blank is the invented-empty-edge pattern with the `RequiredDependencies` gate now armed. Schema-side regression guard added: `tests/test_veta.py::test_openminds_stimulus_passthrough_keeps_the_second_pass_join_keys`. |

| 76 | **MEASURE: does one approach cover several interactions?** (decides whether `interaction_purpose` collapses to a field) | opened 2026-08-09. Named in the `misc singletons` sign-off as the one open item. **THE MEASUREMENT:** for every `openminds_stimulus` document take its `epochid`, then count the DISTINCT SUBJECTS among the `stimulus_presentation` documents sharing that epoch; the distribution of that count over the 635 is the answer. One subject per epoch → one purpose maps to one interaction and `purpose` should be a FIELD on `subject_interaction` (removing a class and a numbered required edge, which #63 says is unverifiable anyway); several subjects → the class earns its `interaction_id_#`. **NOT MEASURABLE from the dev container — no corpora on disk** — and the census reports by class only, so it needs a grouped count added plus a full corpus run (~1–2 h). **DO NOT substitute the class totals**: 635 approaches against 2,670 `stimulus_presentation` is not a ratio, because only some datasets write approaches at all, so the two counts come from different populations. **Already settled structurally from the writers, so do not re-derive:** an epoch may carry SEVERAL approaches (`add_stimulus_approach.m` reads a table of (Epoch, Approach) rows and dedups on (epochid, name); `stimulusDocMaker.m:342-380` takes a cell array of approach strings and emits one document each), and the stimulator is SINGULAR (`probe = S.getprobes('type','stimulator'); probe = probe{1}`) — so the purpose cannot be folded onto the epoch either. |
| 76a | **The #76 grouped measurement RAN. The join it assumes does not exist by epoch id.** | Corpus run **31415147934** (`02854c7`, 2026-08-10). **DENOMINATOR: 6 corpus reports, 6 read, 0 unreadable, 0 skipped; 562,422 documents inspected.** Dab is the only corpus with StimulationApproach documents: **635 approaches over 635 epochs, and 635 of those epochs have NO `stimulus_presentation` document at all.** Epoch ids carried by BOTH classes: **0**. The cross-tab says why, and it is not a data gap -- **the two classes use different epoch-id namespaces**: every one of the 635 approach epoch ids carries the `epoch_` prefix (635 distinct / 635 docs), and every one of the 1,242 presentation epoch ids is in the `other` bucket (149 distinct / 1,242 docs). Neither class has a single id in the other's bucket. The pooled Dab histogram decomposes exactly against this: 1,605 distinct `epoch_` over 3,845 docs (the 635 are a subset) and 149 distinct `other` over 6,207 docs -- and corpus B, whose data Dab contains, reports the SAME 149 distinct `other` ids over the SAME 6,207 docs. **CONSEQUENCE for #76: the distribution it asks for cannot be computed on this corpus, because the grouping key does not join.** That is an answer, not a failed measurement -- but it is an answer about Dab, and the corpora are a sample. What #76 still needs is either a corpus where both classes are written by the same converter, or a different join key than `epochid`. **CONSEQUENCE for #75: unchanged** -- routing 635 approaches to `interaction_purpose` on "the epoch's interaction" presumes an interaction exists for that epoch, and in Dab none does. |


| 78 | **#56 remainder: the strain MIGRATOR (a second pass)** | opened 2026-08-09 when the schema half of #56 landed. The classes exist; nothing populates them yet. Needs: `openminds_subject` Strain documents -> `strain` entities with `strain_id` back on the assertion; the `openminds_#` pedigree edges read so `backgroundStrain` becomes `background_strain_#` (~2,362 composite Strain documents currently drop their pedigree); ~2,365 `genetic strain type` assertions moved off subjects onto the strain; duplicate `species` assertions deduped; strain documents deduped (roughly ten distinct strains behind 2,365 documents, because `getStrain` constructs fresh objects per call). A SECOND PASS: the pedigree lives in other documents, which a single-document migrator cannot follow. Rides with #72. |

| 79 | **#63 remainder: the family-count MEASUREMENT — BUILT 2026-08-09; the corpus number is still unmeasured** | `silentLoss` now reports `family_count_violation` + `family_violation_count` against the declared min_count/max_count. REPORT ONLY: `subject_interaction.time_reference_#` min 1 has never been measured on real data and enforcing it blind is how a gate turns red on a corpus, so what remains is READING the number off a full corpus run. **This row previously said the cause of the second CI failure was "unknown" and the work "needs someone with a local MATLAB". Both were wrong, and the way they were wrong is the point.** The detector was correct throughout; `famKeys`/`famCounts` were accumulated in the loop and then never assigned to the report, while their four sibling fields were — so the report read `family_violation_count: 0` on a document the detector had just flagged. A zero meaning *not reported* rather than *nothing wrong* is the exact silentLoss failure mode, occurring inside silentLoss. It survived two CI rounds and a revert because a pass/fail result cannot distinguish a broken detector from a discarded answer. What actually unblocked it was the ability to PRINT: `.github/workflows/matlab-scratch.yml` + `tools/scratch.m` run arbitrary MATLAB in CI (~2 min) and print to the log. No local MATLAB was ever required. |
| 80 | **CLOSED 2026-08-10: six signed plan documents told their readers they were unsigned** | Sign-offs are APPENDED AT THE BOTTOM of a plan document; the reader's summary of its state is at the TOP; nothing kept the two in agreement. `V_eta_clock_alignment_cluster_plan.md` sat unbuilt for a day on exactly this, and it was found by accident. A mechanical sweep on 2026-08-10 found FIVE MORE: `V_eta_epoch_plan.md`, `V_eta_ingested_payload_findings.md`, `V_eta_stimulus_response_model_plan.md`, `V_eta_daq_family_decisions.md` and `V_eta_stimulus_parameter_plan.md`, plus a partially-stale line in `V_eta_go_forward_class_audit.md`. **DENOMINATOR: 54 markdown files under `schemas/`, 54 read, 16 carrying at least one `TEAM-SIGN-OFF` line.** The defect is ONE-DIRECTIONAL -- the header always claims LESS progress than the record holds -- so its cost is always work not done, never work wrongly done, which is why it never announced itself. `status_board.py` was never fooled, because it reads the signature and not the prose; the human read the prose. Headers corrected (per-proposal for `go_forward`, where two of four ARE signed and a blanket claim in either direction is what made the line wrong), and the condition is now gated by `tools/check_signoff_header_staleness.py` in CI and in pytest, verified to fire. Historical quotations are exempted by a `HISTORICAL-SIGNOFF-CLAIM` marker so a correction note does not re-trip it. |
| 81 | **`oneepoch`: fork A1 chosen (NOT signed); passthrough repair BUILT** | opened 2026-08-10 out of the epoch plan's own pre-build check. `oneepoch` is not an epoch class -- it is the record of a CONCATENATION (`ndi.element.oneepoch` glues an element's N epochs into one; its single own field `epoch_ids` lists the sources). Everything else it carries arrives by INHERITANCE from `element_epoch`, its ONLY declared superclass -- which the signed epoch model dissolves. **IT HAD NO V_eta SCHEMA AT ALL**, because `coverage.py`'s `_NONPROD_CLASSES` asserted it was test scaffolding; that tag suppresses the coverage gap, which is why the class had no schema, no migrator and no worklist row. The assertion was false (writer `src/ndi/element.m:387`, reader `+ndi/+element/oneepoch.m:78-80`, both in `src/`), and the tag is removed. **A real document quarantined -- MEASURED, not predicted** (scratch probe 8, DID-matlab run 31423494433: `No schema file for class "oneepoch"`). **BUILT:** the tombstone (chain `base, epochid`; declares `clocks`, NOT the did_v1 `epoch_clock`/`t0_t1`, because the base superclass migrator collapses them before validation sees the document) + `migrators_j/oneepoch.m` folding the inherited block onto the concrete one + 4 tests including one with validation ON. **STILL OPEN, and it needs the team:** fork A1 is the chosen DIRECTION (the concatenation becomes a typed observation whose `derived_from_#` edges point at the N per-epoch observations; NO `epoch` entity is minted for the synthetic `whole_session_<ref>` id, since that would make `epoch` mean both a recording and a derived aggregate -- and `sourceCensus` already treats those ids as a grouping hazard, citing `oneepoch.m:42`). It is NOT signed, and it is NOT buildable until the raw-recording plan is: `derived_from_#` is typed `-> subject_statement`, and the source recordings only become statements there. |

## COMPLETED (kept so the `#nn` numbering stays stable)

**56 — `strain` is an entity, schema half (2026-08-09).** `strain ⊂ entity` is built with the
11 fields from Part 6 (`name`, `species`, `genetic_strain_type` REQUIRED — required BY
openMINDS, not by us — plus description, phenotype, breeding_type, disease_model[],
laboratory_code, stock_number{vendor,code}, synonym[], local_identifier), inheriting
`entity`'s REPEATABLE `global_identifier` which subsumes openMINDS's three identifier slots
and the four schemes in our data. `background_strain_#` is a RECURSIVE self-edge declaring
**min 0, max 2** per #63, so a shared background is stored once instead of duplicated into
every descendant. `term_assertion` gains an OPTIONAL `strain_id`, and KEEPS its inline
`{node, name}` — the drift test decides it: dropping the inline value would make
`variable: strain` resolve two ways depending on whether a pedigree happened to exist.
`global_identifier` stays optional because Dabrowska's Cre lines carry none. Tested. The
MIGRATOR half is #78.

**63 — numbered edge families declare their cardinality; the MEASUREMENT is still open (2026-08-09).**
The meta-schema gains optional `min_count` / `max_count` on a dependency; **all seven**
`name_#` families declare a count and NONE claims `mustBeNonEmpty` any more, because that
flag cannot describe a family (a MISSING instance is not a blank one — `silentLoss`
excluded numbered edges for exactly that reason, and three families were nonetheless
declared REQUIRED and verified by nothing). Counts: `subject_interaction.time_reference_#`
min 1 (the spine), `interaction_purpose.interaction_id_#` min 1, and **`syncgraph.syncrule_id_#`
min 0 — NDI's own schema says `"mustbenotempty": 0` and V_eta had tightened it wrongly**;
the three `derived_from_#` families and `directed_relation.time_reference_#` min 0.
**THE MEASUREMENT HALF WAS BUILT AND THEN REVERTED, and that is recorded rather than
hidden.** `silentLoss` gained a `family_count_violation` report; its test failed on the
MATLAB gate twice, and the second failure survived the fix that explained the first (schema
`depends_on` decodes to a CELL once the entries stop sharing keys, so `[deps{:}]` throws --
and the throw was swallowed by the audit's own try/catch, so the census went quiet exactly
where it should have spoken). MATLAB cannot be run in the dev container, so the remaining
cause is unknown, and guessing at three minutes per CI round-trip is not diagnosis. The
counter is OUT; **the declarations, which are the half that removes the false assurance,
are IN and tested.** Re-open the counter with a MATLAB run available: it was REPORT ONLY,
so nothing depends on it, and the counts it would produce have never been measured. `acquisition_channels_# min 2
max 2` is NOT declared: that class does not exist until the clock-alignment cluster is
built, so it rides with #57. Tested both sides. Also closes the visibility half of #52.

**64 — the file-list detector exists (2026-08-09).** `did2.validate.fileList` compares each
document's `files.file_list` against the files its class chain declares, both directions:
**declared-but-absent** (the class says the bytes are there and the document has none — the
direction that LOSES data; `data.bin` was dropped from
`daqmetadatareader_epochdata_ingested` exactly this way and was found by hand) and
**present-but-undeclared** (bytes survive but nothing can find them). Neither tripped
anything before: `+did2/+schema/cache.m:598` allows `file`/`files` as a top-level key and
never looks inside. Wired into `v1_to_v2` as `result.file_list_audit` (REPORT ONLY, raises
nothing) and printed by the corpus driver beside the silent-loss census. **17 of 228 V_eta
classes declare a file**, so the quiet majority is deliberately not reported. `toBodies`
was EXTRACTED from `silentLoss` into `+validate/private/vBodies.m` and is now shared — a
second copy would have been a second chance to re-introduce the bug that made the census
read 0 documents for two days. Tested (`testFileList`), and the first two tests are about
whether the detector can SEE its input rather than about file lists at all.

**77 — `measurement.m` was NOT a regression (2026-08-09).** Opened the same day from a
vocabulary-checker row and closed by reading the code, which is the only thing that settles
one. `measurement.m:69-75` does not READ `measurement_class`/`parameters` — it ERRORS on
them, exactly as `binnedspikeratevm` errors on `num_bins`. The detector cannot tell a guard
from a read (both are `isfield(blk, 'name')`), which is what `RESOLVED_BY_GUARD` exists for;
the entry was simply missing. Added with its reason. **The checker now reports 0 confirmed
offenders and 0 regressions.** A worked example of the tool's own contract: a row is a place
to go and read, never an instruction.

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

**54 — AND A THIRD ROUND: NDI's SCHEMA DOCUMENTS WERE BEING READ INCOMPLETELY IN THREE WAYS
(2026-08-09).** Now `summary.ndi_schema_document_scan` reports the denominator —
`{files: 91, flat_form: 57, json_schema_form: 5, unparseable: 0}` — and `tests/test_veta.py`
asserts it with one positive control per failure mode.
(a) Schema documents key the class as **`classname`**, not `document_class.class_name`.
(b) **FIVE of the 89 files are JSON Schema draft 2019-09**, not the flat shape, with dependency
names as `const` under `properties.depends_on.items[]`. They are the entire
`vhlab_voltage2firingrate` family — **the family whose WRITER is in no repository we have**, so
these schemas are the ONLY ground truth that exists for it, and they were being skipped in
silence. Reading them proves `binnedspikeratevm` declares `vmspikefilteringparameters_id`,
`element_id` and `sorting_parameters_id` (the last had been reported as a DID-side invention),
and `vmspikefit` declares `fit_input_id`, which V_eta still does not.
(c) **TWO files are not valid JSON**: `apps/markgarbage/valid_interval_schema.json` and
`apps/calculations/simple_calc_schema.json` contain `"parameters": [-Inf,Inf,0]` — MATLAB, not
JSON — so a strict parse discarded each whole file INCLUDING its well-formed `depends_on` block
sitting above the offending line. **One of them is `valid_interval`, one of the four UNVERIFIED
coverage rows**: its declaration (`element_id`, `mustbenotempty: 1`) had been sitting there
readable the whole time. Now parsed with the bare `Inf`/`NaN` tokens replaced by null.

**54 — CORRECTED THE SAME DAY. The sweep was reading almost nothing, and its zero was a
property of its regex.** It matched `set_dependency_value` only in the FUNCTIONAL form
`set_dependency_value(doc, 'name', id)` — the name as the SECOND argument. NDI writes METHOD
calls, `doc.set_dependency_value('name', id)`, where the name is the FIRST. So it found
**5 call sites in 1,002 `.m` files** and reported *"0 dependencies declared by no template"*,
which read as a clean result. It missed all five in `+ndi/+app/+stimulus/tuning_response.m:323-328`
and all three in `+ndi/+daq/system.m:489-497`. Fixed: **126 call sites, 29 distinct
dependencies.** THE SWEEP NOW REPORTS ITS DENOMINATOR (`summary.writer_dependency_scan`:
files scanned, call sites, distinct names) and `tests/test_veta.py` asserts the denominator
plus six named positive controls, because the answer is legitimately ZERO now and a zero with
no denominator is not evidence. **Two things fell out of the same fix.** (a) The ground truth
now reads NDI's `schema_documents/` as well as `database_documents/` and UNIONS the dependency
names: a dependency can be declared in the schema and NOT in the template — `syncgraph.json`
has `depends_on: []` while `syncgraph_schema.json` declares `syncrule_id` — so V_eta was being
told off for declaring the edge correctly. That surfaced two REAL gaps that had been invisible,
`ensemble.neuron_id` and `openminds.openminds`, recorded on rows 29 and 72. (b) The schema
documents key the class as **`classname`**, not `document_class.class_name`; the first cut read
the template spelling, matched nothing, and returned a clean empty result — the same
could-not-have-matched failure, caught only because a row that should have disappeared did not.

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

## MEASURED — all five corpora, run #2 (2026-08-09)

`test-corpus.yml` run #2 at DID-matlab `6a9421b` / DID-schema `61f9439`. All six
jobs green. **The numbers below were read out of the per-job STDOUT: the reports
were never uploaded (see the artifact-path defect, fixed in `e532dae`), so the
digest aggregated nothing.** JH, PRED and 20211116 were not read in detail — only
Soph, B and Dab are quoted here.

        corpus B    12,917 docs   6,207 carry an epoch id,   149 distinct
                    epoch_ 0 / whole_session_ 0 / other 149 (6,207 docs)
                    142 id(s) span >1 session
                    session documents 14   distinct session_id 14
                    approaches 0
        Soph       101,427 docs   4,931 carry an epoch id,    18 distinct
                    epoch_ 0 / whole_session_ 0 / other 18 (4,931 docs)
                    12 id(s) span >1 session
                    session documents 33   distinct session_id 33
                    approaches 0
        Dab         27,561 docs  10,052 carry an epoch id, 1,754 distinct
                    epoch_ 1,605 (3,845 docs) / whole_session_ 0 / other 149 (6,207 docs)
                    142 id(s) span >1 session
                    session documents 16   distinct session_id 16
                    approaches 635 over 635 epochs

**1. A CORRECTION TO WHAT WAS WRITTEN HERE AFTER CORPUS B ALONE.** That entry said
*"the prefix analysis describes no document in this corpus"* and generalised from
one corpus. **Dab has 1,605 distinct `epoch_` ids over 3,845 documents**, so the
`ndi.file.navigator` writer the plan is built around IS represented. The earlier
sentence was true of B and Soph and false as a general claim. This is the corpora-
are-a-sample rule catching me one entry after I invoked it.

**2. WHAT DOES HOLD, ON ALL THREE: ZERO `whole_session_` ids anywhere.** The
synthetic-collision hazard the plan devotes its HAZARD section to has **no
instances at all** in the measured corpora. It is a real writer and may appear in
a dataset still waiting to migrate — but nothing here exercises it.

**3. THE REAL COLLISION IS IN THE BUCKET THE PLAN DOES NOT MODEL.** The
cross-session count tracks the `other` bucket exactly: B has only `other` ids and
142 collide; Dab has the same 149 `other` ids and the same 142 collide, while its
1,605 `epoch_` ids add none. So **`epoch_<uid>` is globally unique exactly as the
plan says, and the collisions are entirely among the bare local names** (the
`"t00023"` shape). **Grouping on `epochid.epochid` alone would fuse epochs across
sessions**; the key must be at least `(base.session_id, epochid.epochid)`.
(Note B's `other` figures — 149 distinct, 6,207 docs, 142 colliding — are
IDENTICAL to Dab's. The two corpora appear to share documents. Not investigated;
do not treat B and Dab as independent samples without checking.)

**4. #51 IS ANSWERED, AND CLEANLY: session documents match distinct session ids
1:1 in all three — 14/14, 33/33, 16/16.** The referent a REQUIRED `relative_to`
needs exists. This is the check fork A was gated on. JH, PRED and 20211116 still
to read.

**5. #76 IS NOT ANSWERED, AND THE RESULT AS PRINTED CANNOT BE TRUSTED.** Dab holds
all 635 approaches, over 635 distinct epochs — exactly one approach per epoch —
and reported **635 approach epochs with NO presentation document**, i.e. every
one. Dab is known to hold ~1,242 `stimulus_presentation` documents, so either the
approaches and the presentations genuinely carry disjoint epoch ids, or the census
never saw the presentations. **The census as run could not tell those apart: it
reported no denominator for the presentation side.** Fixed in `e532dae`
(`presentation_doc_count`, `presentation_docs_with_epoch`); re-run before reading
anything into this. Dab also printed one distribution row with a BLANK subject
count against 0 epochs — a phantom row from an empty distribution, also fixed.

**6. THE STIMULUS-RESPONSE REPAIR IS CONFIRMED ON REAL DATA.** Soph's silent-loss
census now reads **175 empty required edges, 0 vacuous required fields**, and the
only row is `stimulus_presentation.element_id` (held for #31). The 11,167
`stimulus_response_scalar_parameters_basic.stimulus_response_scalar_id` empties
that dominated the previous census are GONE — that schema half was in the
`61f9439` the run picked up.

**7. QUARANTINES ARE ENTIRELY THE `epochfiles_ingested` REGRESSION**: Dab 4,088,
B 2,484, Soph 349 — every quarantine in every corpus, one cause, fixed in
`8987265`. A re-run should return all five to 0.

## DECISION NEEDED — `fitcurve` migrates to an observation about NOBODY (2026-08-09)

Found while restating the Phase-2 tombstones. **Not a tombstone problem, and not
fixable by a single-document migrator**, so it is recorded rather than built.

`migrators_j/fitcurve.m:53-54` resolves its subject with

        subjectId = firstNonEmpty(dependencyValue(preBody, 'element_id'), ...
                                  dependencyValue(preBody, 'subject_id'));

**NDI's `fitcurve` has NEITHER.** `database_documents/data/fitcurve.json` declares
exactly one dependency, `fit_example_data_id`; the schema document agrees; and NDI
has no writer for the class at all — `+ndi/+data/evaluate_fitcurve.m` only READS
one. So `subjectId` is `''` for every real document, and the migrator emits a
`score_observation` whose `subject_id` is empty: an observation of a residual sum
of squares, about nobody. That is the `ontology_image` failure exactly, and it is
invisible to the corpus gate because `+did2/+validate/references.m:90` skips empty
edges.

**Why this is a decision and not a build.** The three obvious repairs each change
migration output, and each has a real cost:

- **Guard + pass through** (the `openminds_stimulus` / `probe_geometry` precedent).
  Honest, and preserves the document for a second pass. BUT `fitcurve` currently
  DISSOLVES, so its `fit_example_data_id` edge disappears; passing the document
  through re-introduces that edge into reference validation, and if the referent is
  not in the batch that is a NEW ORPHAN on a 0-orphan gate.
- **Emit only the anchor when no subject resolves.** Loses `fit_sse` entirely —
  worse than the hollow document.
- **Attribute via a second pass.** Correct, and needs the graph a single-document
  migrator does not have. There is nothing in the document to attribute FROM: the
  only edge points at example data, not at a subject.

**Where the subject actually is, is not established.** No writer exists in any
repository we have, so we do not know who writes `fitcurve` documents or whether
they set an `element_id` the template never declared (which is legal — that is the
#54 append path). **Check a corpus for `fitcurve` documents and read their real
`depends_on` before choosing.** The v1 source census added today reports per-class
counts, so the next full run answers "do any exist, and what do they carry".

Sibling: `vmspikefit` uses the same `residualFold` but its template DOES declare
`element_id`, so it is unaffected.

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

---

## MEASURED 2026-08-10 — corpus run 31415147934 (`02854c7`), census digest job 93561591223

Two questions that three builds were each blocked on are now answered from the same run.
The digest text is quoted verbatim; nothing here is transcribed from memory.

```
REPORT SEARCH: 6 file(s) matching *-summary.json under 'corpus-reports',
               'tests/corpus-reports' (3 director(ies) walked, 0 duplicate(s) collapsed)
DENOMINATOR:   6 corpora, 221,827 v1 documents read, 0 unreadable
               (20211116 1220 / B 12917 / Dab 27561 / JH 78688 / PRED 14 / Soph 101427)
```

### #51 RE-CONFIRMED on a second, later run. A `session` document exists in every corpus, one per session id.

Row 51 already records this from run 31327383671 (2026-08-09). This is an INDEPENDENT
re-measurement on a different run of a different commit, and it agrees to the document.

```
20211116   session documents: 1    (distinct base.session_id: 1)
B          session documents: 14   (distinct base.session_id: 14)
Dab        session documents: 16   (distinct base.session_id: 16)
JH         session documents: 3    (distinct base.session_id: 3)
PRED       session documents: 1    (distinct base.session_id: 1)
Soph       session documents: 33   (distinct base.session_id: 33)
```

Six of six, and in every corpus the count EQUALS the number of distinct session ids — so
there is no session whose document is missing. This is the fork-A verification
`V_eta_time_reference_model_plan.md` made a prerequisite for **`relative_to` REQUIRED**, and
it is the measured refutation of the old "no session document exists anywhere" claim. That
claim came from a grep that could not have matched; this comes from the census.

**`relative_to` REQUIRED has no remaining prerequisite.**

### THE EPOCH MINT MUST KEY ON `(session_id, epoch_id)`, NOT ON THE ID STRING

The epoch plan named ONE grouping hazard — the synthetic `whole_session_<reference>` id, which
is minted per ELEMENT and so evaluates the same for every element in a session. That hazard
measures **ZERO in all six corpora**. A *different* hazard is non-zero:

```
                 synthetic (whole_session_) ids   ids spanning >1 session
20211116                     0                            0
B                            0                          142        <-- of 149 distinct
Dab                          0                          142        <-- of 1754 distinct
JH                           0                            0
PRED                         0                            0
Soph                         0                           12        <-- of 18 distinct
```

**One `epoch` document per distinct `epochid.epochid` string would FUSE epochs that belong to
different sessions** — 142 strings in B, 142 in Dab, 12 in Soph. In B that is 142 of 149
distinct ids, i.e. almost the whole corpus. The mint key must be the PAIR.

Two things worth stating plainly about this row:

1. **The plan predicted hazard A and the instrument found hazard B.** The prediction was
   sound reasoning about a writer; it was simply not the failure the data has. This is the
   argument for measuring before minting, made concrete.
2. **B and Dab report identical figures** for the `other` bucket (149 distinct / 6207 docs /
   142 spanning). Two corpora agreeing to the document is more likely a shared source than a
   coincidence, but nothing here establishes that — flagged, not asserted, and it does not
   change the disposition either way.

### The 2,670-document `stimulus_presentation.element_id` row, per corpus

```
B 1242 / Dab 1242 / Soph 175 / 20211116 11        total 2,670
```

Repaired 2026-08-10 by the `stimulus_presentation` tombstone (the invented `element_id` is
replaced by NDI's real `stimulus_element_id`). **That is a prediction until a corpus run at or
after that commit reports it**, exactly like the `image_stack` guard. The same run still
carries `image_observation.subject_id` at 4,563 (JH), also pre-guard.

**MEASURED 2026-08-10, corpus run 31438980133 (`fd36421`) — the prediction HELD on the two
corpora that finished.** Both report zero, and both report a non-zero denominator alongside,
so this is a measurement and not a dead instrument:

```
DENOMINATOR: 2 of 4 affected corpora reported; Dab and Soph were CANCELLED mid-flight
             (test-corpus.yml sets concurrency cancel-in-progress, and a later push
             killed them), so they are UNMEASURED, not zero.

  B          12917 v1 documents read, 0 unreadable
             silent-loss: 0 empty required edge(s), 0 vacuous required field(s)
             was 1,242                                          -> 0
  20211116   silent-loss: 0 empty required edge(s)
             was 11                                             -> 0

  Dab        was 1,242                                          -> NOT MEASURED
  Soph       was   175                                          -> NOT MEASURED
```

So 1,253 of the 2,670 documents are confirmed repaired on real data and the remaining 1,417
are merely expected. B is the meaningful one: it is the largest single contributor to the row
and it also returns `quarantine_count: 0` and `fragments: 0`, so the repair did not buy the
empty edge back as a quarantine somewhere else.

**The same run found a NEW gating orphan, in the class this row's sibling repair created.**
`clock_alignment_policy.session_id` dangled on BOTH reporting corpora — 1 of 2814 edges on
20211116 and **13 of 19069 on B** — and in both cases it is 100% of the class (1 of 1
syncgraph, 13 of 13). Cause and fix are recorded in the header of
`DID-matlab/src/did/+did2/+convert/+migrators_j/syncgraph.m`: the migrator filled a
`must_refer_to_document_class: session` edge from `base.session_id`, which is a DIFFERENT ID
SPACE from a session document's `base.id` (`ndi.document.m:57` mints one, `ndi.session.m:215`
sets the other, separately). `did2.convert.epochMint` had refused that exact assumption in
its own header; `syncgraph.m` was written in parallel and made it. The fold is now gated
behind `jSessionDocId`, which answers `''` by construction in pass 1, so every real document
passes through until a batch pass supplies the id. **Not yet re-measured** — the fix
(`fef145f`) postdates the run that found it.

---

## FINDINGS FROM THE PARALLEL BUILD (2026-08-10) — recorded because they lived only in agent reports

Five families were built concurrently. **None of the MATLAB has been executed** — these
containers have no MATLAB — so every migrator and test below is UNVERIFIED, and the quick gate
is the first thing that will have an opinion.

### Bugs found by reading the WRITER, each the same shape as one already in the record

- **`jSoftwareFromApp` had never emitted a software entity on a real document.** It read
  `app.name` / `app.version`, but `universalRenames.m:145-164` renames those to `app_name` /
  `app_version` before any migrator runs. The unit tests call the migrator DIRECTLY with a
  hand-built body, so they never run `universalRenames` and never saw the renamed field —
  *"a test written from the same premise as the code cannot catch the code"*, arriving through
  the HARNESS rather than the premise. Both spellings are now read. **Fixed.**
- **`epochprobemap` was silently dropped on every real `syncrule_mapping`.**
  `syncgraph.m:313-314` calls `.serialize()`, documented at
  `epochprobemap_daqsystem.m:136-143` as *"Create a CHARACTER ARRAY representation"*, and the
  template default is `""`. The reader required `isstruct`, so it returned an empty struct.
  The old fixture used a struct, which no writer produces — `distance_metadata`'s
  wrong-assumed-shape failure again. **Fixed.**
- **`jFrequencyFilter` would have read the wrong field name.** `v1_to_v2.m:154` runs
  `applySuperclassMigrators` BEFORE `runConcreteMigrator` at `:162`, and
  `+migrators/filter.m:30-33` renames `block.type` → `block.filter_type`. Reading `type` —
  the name both the NDI template AND the writer use — returns `''` on every real document, so
  the guard would have fired every time and the fold would have emitted nothing **while
  looking like a correct cautious guard**. Caught before shipping.
- **NDI's own `filter.json` documentation misspells two of its own fields.** The writer
  (`+gui/+app/+pyraview/filterData.m:37-41,49-53`) writes `passBandRipple` and
  `stopbandAttentuation`; `git grep passbandRipple` → 0 hits, `stopbandAttenuation` → 0 hits.
  The misspellings are the real field names. Writer beats template, inside NDI's own pair.
- **`ensemble`'s template and its own schema disagree about `neuron_id`.** The schema pair
  declares it; the template's `depends_on` does not. `ensemble.m:273-277` writes it with
  `add_dependency_value_n`, so the WRITER settles it — and because
  `did/document.m:349` appends `neuron_id_1`, `neuron_id_2`, …, **the suffix index IS the
  column index**, so the per-epoch column order needs no file read at all.

### A test that must be INVERTED, not patched

`testMigratorsJ.m::testElementDirectDeviceObservesSpecimen` asserts the loose
`observes` relation for a direct `n-trode` element. The recording-observation build retires
exactly that relation in favour of a typed `<modality>_observation` with `instrument_id`. The
test is asserting the behaviour being replaced — the third instance of this pattern
(`test_phase1_source_cleanup_and_dep_typing`, `test_ingested_caches_epochid_dep_only`,
`testMfdaqIngestedDeEncodesToDaqreaderEpochdataIngested` were the first three).

### Blockers found in DID-schema, each of which stops a signed model being finished

| what | where | consequence |
|---|---|---|
| `timed_sequence` is `"abstract": true` | `V_eta/draft/timed_sequence.json` | `cache.m` raises `abstractInstantiation`, so the signed stimulus plan's own worked example — a standalone `timed_sequence` document — **cannot be instantiated**, and the signed multi-subject `storage_mode: reference` case is unimplementable. **BUT THE ONE-WORD FIX IS WRONG — see the correction directly below. This is a TEAM CALL, not a build.** |
| `is_cache` exists in NO schema | only in `V_eta_tenets.md`, `V_eta_tenet_audit.md`, `V_eta_ensemble_plan.md` | the ensemble's rebuildable-cache half cannot be declared. |
| `directed_relation` has no `epoch_id` slot, and no migrator mints an `epoch` | `directed_relation` declares exactly `child`, `parent`, `time_reference_#` | the ensemble's `member_of` edges **cannot be epoch-scoped**, so the per-epoch MAP document cannot be consumed and stays a passthrough. |
| `method_parameters` has no `filter_id` edge | its `depends_on` is `['software_id','subject_id','epoch_id','derived_from_id']` | the spike-parameters plan's prose says filter settings leave via `filter_id`; the artifact says there is no such edge. **The artifact wins** — the settings are grouped whole under `other.filter` instead, and nothing was invented. |
| `subject_observation` is abstract and there is no `modality_unresolved` field | 30 concrete leaves subclass it; **none** without a `data_type` mixin | the signed recording-observation Guard A ("a valued observation with no dimensioned quantity") has no class to be and no field to set. Built instead as a `term_assertion` on the element-subject, keeping `observes`. |
| the D9 registry has no dimensional rows | `binding_registry_meta.json` — all 5 `subject_statement_bindings` bind to `term_assertion`; the one dimensional row ("body mass" → `mass_observation`) is under `binding_examples`, which is illustrative | the signed `subjectmeasurement` fold says the leaf must come from the registry. **It cannot today.** `jQuantityLeaf` is the documented pass-1 stand-in and the single place that changes when the registry gains rows. |

### Two artifacts that contradict each other, and only the team can say which is wrong

- **`member_of` timed/ordered.** `relation_bindings` declares it `"timed": false, "ordered":
  false`; the signed ensemble model requires it to be BOTH (the recorded neuron set changes
  epoch to epoch, and column order matters). Nothing enforces `binding` yet, so this is cheap
  to fix now and expensive once a validator reads it.
- **`ndi.migrate.internal.stimulusPresentationToManipulation` implements the SUPERSEDED model
  (#19)** — one `visual_grating_manipulation` per presentation, reading only the deprecated
  inline `presentation_time`, and **reassigning the id**. The current signed plan
  (`V_eta_stimulus_model_plan.md`) decomposes around the PRESERVED id. The second-pass build
  must **replace** that function, not extend it. Same trap one layer up:
  `tests/test_veta.py:1057-1070` (`test_visual_grating_manipulation_leaf`) carries a docstring
  describing the superseded model.

### Smaller things, recorded so they are not rediscovered

- **A substring hazard in the measurement fold: `contains('voltage', 'age')` is TRUE.**
  `subjectmeasurement.measurement` is free text, so substring matching could type a voltage as
  an age. `subjectmeasurement` uses word-boundary matching; **`measurement.m` keeps substring
  matching unchanged**, because its haystack is a resolved CURIE and narrowing it is a
  separate decision.
- **`isFragment` will mis-classify `clock_alignment`.** Its signature is structural — every
  `time_reference` or `relation` subclass reads as scaffolding — and `clock_alignment ⊂
  relation`, so `{clock_alignment, ref, ref}` counts as a fragment while the polynomial,
  degree and cost are the whole payload. Zero on real data only because the fold is gated; the
  census's "fragments 0" invariant stops meaning what it means the day that gate opens.
- **`acquisition_system` DOES exist** (`V_eta/stable/acquisition_system.json`, maturity
  `stable`, an `entity` subclass). A schema comment saying otherwise is stale. It changes
  nothing for the syncrule fold: a syncrule stores a device NAME, and name→id needs the
  migrated-id graph a single-document migrator does not have, so the optional edge is OMITTED
  rather than blanked.
- **`syncrule.parameters.daqsystem1_name` is NOT a query path.**
  `git grep "syncrule\.parameters" origin/main -- '*.m'` returns exactly two hits: the writer
  (`syncrule.m:187`) and the object-reconstruction read (`syncrule.m:21`). The live
  `syncgraph.m:404-408` query reads `syncrule_mapping`, which passes through unchanged.
- **`vmspikefilteringparameters` has no writer anywhere.**
  `git grep -c -i "vmspikefilteringparameters" origin/main -- '*.m'` → no output (0 files).
  Per the standing rule this is NOT evidence it is unused; it now has a migrator regardless.
- **v1 has no spelling for a notch filter.** `band_stop` / `stopband` cannot be emitted, so
  `jFrequencyFilter` does not pretend to. FIR taps and windows likewise have no home.

---

## CORRECTION 2026-08-10 — "just un-abstract `timed_sequence`" is WRONG, and it is a TEAM CALL

The stimulus agent reported that `timed_sequence` is `"abstract": true` and therefore the
signed plan's own worked example cannot be instantiated. **That half is correct and it is a
real blocker.** The implied fix — take the flag off — is not, and it would have been a
one-word change that quietly broke a system-wide convention. Measured before touching it:

```
DENOMINATOR: 40 classes declaring `data_type` as a direct superclass
   abstract : 40   acceleration, amount, angle, angular_velocity, area, capacitance,
                   charge, chemical, concentration, conductance, contrast_sensitivity,
                   count, current, date, dose, duration, energy, force, formulation,
                   frequency, gain, harmonic_component, image, intensity, length, mass,
                   ph, polynomial, score, temperature, term, TIMED_SEQUENCE, tuning_curve,
                   velocity, visual_grating, voltage, volume, pressure, power, resistance
   concrete :  0
```

**Every single data_type composite is abstract. There are no exceptions today.** They are
MIXINS: a quantity is instantiated through a concrete leaf that mixes it in
(`voltage` → `voltage_observation`, `image` → `image_observation`/`image_manipulation`).
`timed_sequence` follows that convention exactly — `timed_sequence_manipulation` is
`[subject_manipulation, timed_sequence]`, which is the plan's own declaration.

So this is not a defect in one file. It is a GENUINE CONFLICT between two signed things:

- the **stimulus plan's worked example**, which shows a standalone
  `{"class_name": "timed_sequence", "base": {"id": "presentation_epoch7"}, ...}` document
  that two `timed_sequence_manipulation` leaves both reference (the shared-playlist,
  multi-subject case, `storage_mode: reference`); and
- the **③ composite tier's architecture**, in which a `data_type` is never a document on its
  own and always rides on a leaf.

Flipping the flag makes `timed_sequence` the only concrete data_type of 40 and sets a
precedent nobody agreed to. The alternative — a concrete carrier class for a shared sequence,
the way every other data_type gets a leaf — needs a name and a tier, which is modelling.

**Operating rule 4: only the team decides a disposition. So the flag STAYS as it is and this
is recorded, not fixed.** Two options, for the team, no recommendation implied by ordering:

  A. `timed_sequence` becomes concrete — accept one exception, and say why the shared value
     document is different in kind from a quantity.
  B. Mint a concrete carrier that mixes in `timed_sequence`, so the referenced document is a
     leaf like every other instantiated data_type, and the plan's example names that class
     instead.

Until one is chosen, the stimulus second pass is blocked on the SHARED case only. The
single-subject inline case is unaffected, and pass 1 already passes `stimulus_presentation`
through with its id and its repaired tombstone, so nothing is lost meanwhile.

**Why this is worth the paragraphs.** The agent's finding was accurate and its proposed fix
was one word. Applying it would have gone green, looked like progress, and left the schema
with a silent exception nobody could later explain — the exact failure mode the operating
rules exist for. The check that caught it was mechanical and cheap: count the siblings before
believing a class is uniquely broken.

---

# DECISIONS WAITING ON THE TEAM (assembled 2026-08-10, from the parallel build)

Every item here was found by a build that then STOPPED rather than choose. They are collected
in one place because they arrived from nine different agents over a few hours and would
otherwise trickle out one at a time. **Nothing below has been decided, and no code embodies a
preference except where explicitly noted as a documented stand-in.**

Grouped by what it costs to leave open.

## A. BLOCKS A BUILD THAT IS OTHERWISE FINISHED

**A1. `timed_sequence` is abstract, and the one-word fix is wrong.**
The signed stimulus plan's own worked example is a standalone `timed_sequence` document that
two `timed_sequence_manipulation` leaves both reference — the shared-playlist, multi-subject
case. `cache.m` raises `abstractInstantiation`, so it cannot exist. But **all 40 `data_type`
composites are abstract and none is concrete**: they are mixins, instantiated through a leaf.
Options: (a) make `timed_sequence` the sole concrete data_type and say why a shared VALUE
document differs in kind from a quantity; (b) mint a concrete carrier that mixes it in, and
have the plan's example name that class. Full working in the correction section above.
*Blocks: the shared multi-subject stimulus case only. Inline single-subject is unaffected.*

**A2. `element_epochid` is DESTROYED by the stimulus-response fold, and no counter sees it.**
The signed mapping preserves it as a `relative_reference` pointing at an `epoch`. The migrator
cannot build that: `relative_to` is required and no migrator mints an `epoch`. Today the
document passes through whole and the string survives; after the fold it does not. `silentLoss`
counts empty edges, vacuous fields and fragments — **a dropped source field is none of those**.
Options: carry the string in a slot the schema lacks (contradicts the recorded "`epochid` is
dropped" decision); suppress the fold until the epoch mint lands (the `epochfiles_ingested`
precedent); or accept the loss on the argument that the second pass can re-derive it from the
syncgraph. *This is a DATA LOSS question, not a defect.*

**A3. Guard A (raw recordings) has no schema home.**
The signed model wants a valued observation with no dimensioned quantity, plus a
`modality_unresolved` flag. Measured: **30 concrete leaves subclass `subject_observation`, and
every one carries a `data_type` mixin; `subject_observation` itself is abstract; `grep -rn
"modality_unresolved" schemas/` matches only decision documents — no class, no field.**
Shipped as a documented STAND-IN: a queryable `term_assertion` on the element-subject that
keeps `observes`. Needs a leaf + a field, or a different model.

**A4. The D9 registry cannot answer the question the signed measurement fold asks it.**
That fold says the quantity leaf must come from the registry. All five
`subject_statement_bindings` bind to `term_assertion`; the only dimensional row
("body mass" → `mass_observation`) sits under `binding_examples`, which is illustrative.
So a strict lookup resolves nothing for `age`. Shipped as a documented STAND-IN
(`jQuantityLeaf`), which is the single place that changes when the registry gains rows.

**A5. Two signed artifacts contradict each other on `member_of`.**
`relation_bindings` declares it `"timed": false, "ordered": false`; the signed ensemble model
requires it to be **both** (the recorded neuron set changes epoch to epoch, and column order
matters). One of the two is wrong and only the team can say which. Nothing enforces `binding`
yet — cheap now, expensive once a validator reads it.

**A6. `is_cache` exists in NO schema** (only in three prose documents), and
**`directed_relation` has no `epoch_id` slot** and no `epoch` document to point at. Together
these block two of the ensemble model's four signed pieces: the rebuildable cache, and
epoch-scoped `member_of`. Consequence, deliberate: the per-epoch MAP document is the only
durable roster, so it is NOT consumed.

## B. NEEDS A RULING, BUT NOTHING IS BLOCKED WAITING FOR IT

**B1. Arm `NonVacuousFields` by default?** Its measured cost is **zero across six corpora**;
it is a one-line change. Left off only for symmetry with the required-edge switch and because
the census's field scan and the validator's do not share a denominator. The agent that built
it said plainly this is the call a reviewer could most reasonably overrule.

**B2. `patch` and `sharp` emit TWO observations each** (voltage + current), because
PROBE-TYPES.md documents them as two channels of two DIFFERENT quantities. Read as a
refinement of the signed multi-channel rule (N sites of ONE modality), not a contradiction —
labelling a current trace 'voltage' to keep the count at one would be a real error. Confirm.

**B3. `image_observation.subject_id`: do those documents ever get a subject?** NDI's own
writer leaves the edge empty at three `ndi.document('imageStack')` sites in
`+setup/+conv/+haley/doImport.m` (789, 811, 827). 4,563 JH documents. The guard now passes
them through instead of minting husks, which is strictly better, but the attribution question
is untouched.

**B4. `threshold_sign` — bag or bound variable?** The signed plan's list does not name it; a
superseded draft had it as an enum. Left in `other` rather than make an unmandated call.
Same for `min_clusters`/`max_clusters`.

**B5. `measurement.m` uses substring matching, and `contains('voltage', 'age')` is TRUE.**
`subjectmeasurement` uses word boundaries; `measurement.m` was left unchanged because its
haystack is a resolved CURIE and narrowing it is a separate decision. Flagged, not fixed.

## C. FACTS THAT WILL MISLEAD A READER UNTIL SOMEONE ACTS

**C1. PASS 1 GROWS THE CORPUS.** The stimulus-response plan's table (21,564 → 10,124) is the
END state. Pass 1 adds one anchor per response and deletes nothing: 6 v1 documents → 9.
**A corpus run read against that table will look like a 3× regression and will not be one.**

**C2. `schemas/V_eta_migration_targets.json` is stale.** All four stimulus-response rows still
say "BUILD NOT DONE. The migrator does not do this yet", and `stimulus_response_scalar` has
`targets: []` while a migrator now emits `harmonic_component_calculation` +
`session_relative_reference`. It is HAND-CURATED and lives in `schemas/`, so operating rule 1
stopped the agent editing it. Someone with authority over that file needs to.

**C3. `method_parameters_id` points at a `stimulus_response_scalar_parameters_basic` document
while the edge declares `must_refer_to_document_class: method_parameters`.** Declarative
today. If `must_refer` ever becomes type-checked, 10,124 documents break.

**C4. `method_parameters` has no `filter_id` edge.** The spike-parameters plan's prose says
filter settings leave via `filter_id`; the built artifact declares
`['software_id','subject_id','epoch_id','derived_from_id']`. **The artifact wins** — the
settings are grouped whole under `other.filter` and nothing was invented. The prose needs
correcting or the edge needs adding.

**C5. A THIRD ENFORCEMENT HOLE, the mirror image of the two just closed.** `test_veta.py`
records that the validator allows UNDECLARED `depends_on` entries wholesale: an edge NDI's
writer sets that no V_eta schema declares is silently accepted. Unaddressed.

---

## DECISION 2026-08-10 — a statement reaches its epoch through the REFERENCE CHAIN, not a direct edge

Team decision, jess@walthamdatascience.com, 2026-08-10, verbatim:

> "Use the reference chain, don't add the direct edge"

**What it settles.** The epoch family's signed line reads *"epochid is DROPPED in favour of a
uniform `epoch_id` edge"*, and the epoch plan says every epoch-scoped document gains one. Read
literally that includes `subject_interaction`. It does not get one. A statement reaches its
epoch by:

        subject_interaction --time_reference_#--> relative_reference
                            --relative_to------> epoch

A direct edge would store one fact in two places — the hazard the epoch plan itself raises for
`base.session_id` vs `part_of` and marks "Flagged, not solved". Two copies of one fact agree by
coincidence until something checks them, and nothing would.

**`directed_relation` KEEPS its optional `epoch_id`, and that is not an inconsistency.** It is
signed separately under the ensemble decision ("EPOCH-SCOPED `member_of` edges carrying their
epoch"): there the epoch is the edge's OWN content, because the recorded roster changes from
epoch to epoch. On a statement it would be a restatement of when the statement happened.

**THE SIGNED PLAN LINE NOW UNDER-DESCRIBES THIS, AND ONLY THE TEAM MAY AMEND IT.**
`V_eta_epoch_plan.md:849` still says "uniform `epoch_id` edge". This entry does NOT amend it and
no `TEAM-SIGN-OFF` line was added or edited — that is the team's to write. Recorded here so the
decision is not lost while the plan says something broader than what was decided.

**KNOWN WEAK LINK — measured, and the reason to revisit this if anything does.**

        DENOMINATOR: 3 classes read from the built set (subject_interaction,
                     directed_relation, subject_statement)

        subject_interaction  time_reference_#  mustBeNonEmpty=False  min_count=1
        directed_relation    epoch_id          mustBeNonEmpty=False  (optional by design)

`min_count: 1` guarantees the family EXISTS on every `subject_interaction`, and
`relative_reference.relative_to` is REQUIRED, so a populated reference does resolve. But
`mustBeNonEmpty` is False, so `time_reference_1 = ''` satisfies the family and reaches no
epoch — and the newly ARMED `RequiredDependencies` gate keys on `mustBeNonEmpty`, so it will
not catch it. This is the invented-empty-edge pattern one link along the chain. **Tighten that
before concluding the chain is insufficient** — an empty reference would otherwise look like
evidence the direct edge was needed, when it is evidence the edge we have is unenforced.

The deliberate omission is stated at the `subject_interaction` definition in
`tools/build_v_eta.py`, not left silent, because an unexplained absence is exactly what someone
"completing the family" would helpfully fix.

---

# FINDINGS FROM THE 2026-08-11 RESEARCH PASSES — recorded because they lived only in chat

Three agents were run READ-ONLY and told to write nothing, so their results reached a
human and no file. That is the failure mode this document exists to prevent, and it is
recorded here rather than re-derived. **Nothing below is a decision**; no
`TEAM-SIGN-OFF` line was added by any of it.

## A. Sizing option B for the openMINDS metadata split

The problem: `metadata_editor` and the openMINDS dataset graph are written on INDEPENDENT
paths (`saveEditor2Doc.m` on the editor's window CLOSE; `save_dataset_docs.m` on the Save
BUTTON after a required-field check that early-returns). Neither reads or removes the
other. BOTH cloud upload paths (`+cloud/uploadDataset.m:75`,
`+cloud/+upload/newDataset.m:20`) read only the GRAPH.

Measured, corpus run 31441923369, 6 corpora, 221,827 v1 source documents:

        1  metadata_editor        8  openminds        404  openminds_element
      635  openminds_stimulus  10401  openminds_subject
      CO-OCCURRENCE: 0 BOTH · 1 GRAPH-WITHOUT-EDITOR (JH) · 1 EDITOR-WITHOUT-GRAPH (Soph)
                     · 4 NEITHER
      migrated tier: dataset=5, organization=5, web_resource=5,
                     person=0, funding=0, publication=0

**Where the citation facts live.** `convertFormDataToDocuments.m:197` calls
`openMINDSobj2ndi_document(dataset, sessionId)` with NO dependency_type, and the switch in
that file defaults `docName = 'openminds'`. So the ENTIRE dataset graph — Dataset,
DatasetVersion, every Person, Organization, Affiliation, ORCID, ContactInformation,
Funding, Contribution, DOI, WebResource, License — lands as the bare `openminds` class.
The `openminds_subject` / `_element` / `_stimulus` counts come from other call sites
entirely and are unrelated to citation metadata.

**Size.** ~13 openMINDS types → the SAME six entity classes `metadata_editor.m` already
emits, + `directed_relation`. **Cannot be per-document**: one `person` requires FIVE
documents (Person + Affiliation + Organization + ORCID + ContactInformation) joined by
`ndi://<base.id>` strings. Shape is a pass-1 guarded passthrough + a BATCH assembler, and
the precedent is in-tree — `did2.convert.resolveDatasetEntities` is exactly that shape and
is already wired at 4 sites. It must run BEFORE that pass, so its rich `dataset` wins the
richness ranking against `dataset_remote` stubs. The emitter half
(`entityDoc`/`relationDoc`/`orgFor`/`buildGids`) transfers unchanged; the new half is a
graph walk. One genuine advantage: each openMINDS instance is its own document, so a
graph-sourced `person` can be id-preserving 1→1, which `metadata_editor.m:117` cannot
(it mints a fresh id).

**THE FINDING THAT SHOULD SHAPE THE DECISION: the two stores are NOT information-
equivalent.** The graph holds only a DOI for a related publication — no title, no PMID,
no PMCID. `ndidataset2metadataeditorstruct` recovers those via a NETWORK lookup
(`resolveRelatedPublication`). So a graph-sourced `publication` carries a DOI and no
title, where the editor path carries all four. A migrator must not fabricate the
difference. This argues for B **as well as** A rather than instead of it.

Three more reader facts a build must respect: `fullDocumentation` is bimodal (DOI first,
WebResource fallback) while the reader unconditionally reads `.IRI`, which a DOI document
lacks; two IRI vintages exist for `openminds_type`
(`https://openminds.ebrains.eu/core/...` and `https://openminds.om-i.org/types/...`);
and `core.Dataset` is written but never read — only `DatasetVersion` is queried.

**Two cheap verifications before building.** (1) Does any corpus contain a `DatasetVersion`
`openminds` document at all? The 8 in JH are probably E. coli STRAIN graphs —
`haley/doImport.m:87,706` writes `OP50` and `OP50GFP` with no dependency type. If none
exists, B must be written from writer + reader with a fixture from
`convertFormDataToDocuments`' output shape, never from corpus data. (2) Dump Soph's one
`metadata_editor.metadata_structure`; it settles whether `person=0` is "no authors" or a
shape bug.

## B. Option C for the E. coli images is a DIFFERENT design from the one first scoped

Option C as originally written is DEAD: the subject-carrying and subject-less `imageStack`
sites are in DIFFERENT SESSIONS (`doImport.m:46-49` builds
`{'haley_2025_Celegans','haley_2025_Ecoli'}`; sites 421/461/477/496 are Step 5 under
`sessions{1}`, sites 789/811/827 are Step 8 under `sessions{2}` opened at :694). The last
subject mention in that 881-line file is line 689. The E. coli session mints NO subject.
And `plateID` COLLIDES across sessions (`:166` adds `expType*1000`, `:729` does not), so a
cross-session join would invent attributions rather than recover them.

**The only design that works: mint a subject for the E. coli PLATE.** Its
`ontologyTableRow` carries `plateID` (identity), a `bacteriaStrain` document-id STRING
(`:734`), and OD600/CFU/lawnVolume covariates; `plateTable` is built
`'UniqueVariables','plateID'` so one plate = one row = one subject. The chain
image → image row → plateID → plate row → plate-subject then resolves ENTIRELY within
session 2. **Whether a bacterial lawn is a `subject` is a MODELLING CALL the team has not
made.**

Three things that must be weighed with it:
- The image→plate hop can only ever be a STRING join. `imageVariables` (`:718`) is
  `{plateID, imageID, lawnGrowthDuration, exposureTime}` — `plate_id`, the document id, is
  NOT on the image row. So it must be session-scoped and uniqueness-checked.
- `bacteriaStrain` is NOT an edge: no Haley `table2ontologyTableRowDocs` call passes
  `dependencyVariable`, so the strain document id sits in `data` as a char and the plate
  row's `depends_on` is `[{document_id, ""}]`. Minting `strain_id` from it is a second
  unverified-resolvability edge — the `distance_metadata` shape. NOT in step 1.
- `subject.local_identifier` collides at dataset level: `jEnsureLocalId` does no
  qualification and BOTH sessions land in one `ndi.dataset.dir`.

**The gate cannot see any of it.** `runCorpusDiscovery` runs exactly five passes
(`v1_to_v2`, `resolveDeferredBaths`, `resolveDatasetEntities`, `epochMint`,
`resolveSessionAnchors`) and zero `ndi.migrate.*`. So NDI-side subject resolution is
invisible to the corpus gate — it would report the same passthrough counts whether the
work succeeded, no-opped, or threw (every sub-pass in `local.m` is wrapped in a warn-and-
continue `try`). The recommendation from that scout: build the join DID-side as a batch
post-pass, because it needs only documents already in the migrated batch — no session, no
database, no file bytes — which is the same criterion that put `epochMint` and
`resolveSessionAnchors` DID-side.

## C. `ontology_label.document_id` — the analysis, not a decision

        NDI    ontologyLabel_schema.json   "mustbenotempty": 1
        V_eta  stable/ontology_label.json  mustBeNonEmpty: false  -> base  (untyped)

`document_id` is the label's ONLY dependency — the thing it is about. The optional
declaration is what makes the loss invisible: `silentLoss.m:930 requiredDependencies`
returns names only for edges declared `mustBeNonEmpty`, so **this edge is out of scope for
the empty-edge census entirely**, and "0 empty required edges over 627,526 documents" is
silent about it rather than reassuring.

The writer is unanimous — 10 of 10 construction sites call
`set_dependency_value('document_id', ...)`: `haley/doImport.m` 445/470/486/505/799/816/832
and `babu/import.m` 487/534/583 (2 of the babu sites label a `generic_file`). Zero sites
set any other dependency, so there is no writer-vs-template disagreement to arbitrate.

Against raising it: a call site proves the CALL, not a non-empty VALUE; the corpora are a
SAMPLE and this is a ~7,007-document passthrough class that cannot be repaired in flight;
and quarantine is GATING, so raising it spends a measured 0-quarantine baseline on an
unmeasured risk.

**Proposed sequence (not a decision):** make it visible before enforcing it, which is the
sequence that worked for #37 (armed on an accepted 7,233) and #38 (armed on a measured 0).
Concretely, teach the census to report empty edges that **NDI declares required where
V_eta does not** — a generalisable check that catches this whole divergence class, costs
nothing because it is report-only, and turns arming into a one-line call with a number
behind it. Separately, the tombstone types this edge `-> base`; NDI's referent is always a
real class.

## D. Housekeeping that needs credentials this session does not have

Four throwaway refs from the `image_stack` CI mutation proofs need deleting;
`git push --delete` returns HTTP 403 here. In `VH-Lab/DID-matlab`:
`claude/v-eta-imgstack-docid-mutation` and `…-b`. In `Waltham-Data-Science/DID-schema`:
the two same-named pointer refs (no commits; they exist only because the workflow checks
out did-schema at `github.ref_name`).

---

## TEAM DECISION 2026-08-11 — the E. coli lawns and plates are subjects, in two tiers

Team decision, jess@walthamdatascience.com, 2026-08-11, verbatim:

> "Yes, each lawn can be a subject and a plate of lawns is another subject where each lawn
> is a member of it"

This is RICHER than the single plate-subject that was scoped from the scouting pass. Two
subject tiers plus a group relation:

        lawn   (a bacterial patch)   -> subject
        plate  (a plate of lawns)    -> subject, the GROUP
        lawn --member_of--> plate

**No TEAM-SIGN-OFF line has been added by Claude.** The governing plan document still needs
the team's signature; this entry records the decision so it is not lost, and the board will
keep rendering the family as awaiting review until that line exists.

### The source data supports both tiers — read from NDI `origin/main`

`+setup/+conv/+haley/doImport.m`, Step 8 (`session = sessions{2}`, the E. coli session):

        plateVariables   keyed  plateID              14 cols  expID, OD600Label, peptoneFlag,
                                                              timePoured, bacteriaStrain, CFU,
                                                              OD600Real, OD600, lawnVolume, ...
        imageVariables   keyed  {plateID, imageID}    4 cols
        patchVariables   keyed  {imageID, patchID}   10 cols  lawnRadius, circularity, yPeak,
                                                              yOuterEdge, borderAmplitude,
                                                              meanAmplitude, centerAmplitude,
                                                              borderCenterRatio

So the LAWN is already a first-class row with its own geometry and fluorescence measures —
it is not something that has to be invented to carry the decision.

### Consequences and constraints, each established rather than assumed

1. **Membership is a TWO-HOP join.** `patchVariables` keys on `imageID`, NOT `plateID`, so
   lawn → plate runs patch → image → plate. Both hops are STRING joins on `data` values,
   because no Haley `table2ontologyTableRowDocs` call passes `dependencyVariable` — every
   row's `depends_on` is `[{document_id, ""}]`. Both hops must be scoped to
   `base.session_id`: `plateID` COLLIDES across the two Haley sessions (`doImport.m:166`
   adds `expType*1000`, `:729` does not), and both sessions land in ONE `ndi.dataset.dir`.

2. **`local_identifier` must be qualified.** `patchID` is `1:numPatch` WITHIN a plate
   (`doImport.m:275`), so `'0001'` recurs on every plate, and `jEnsureLocalId` does no
   dataset-level qualification. Unqualified lawn ids collide immediately.

3. **`member_of` already exists and is already bound.** The registry carries it with
   `timed=True, ordered=True`, and the ensemble decision uses the same relation for
   epoch-scoped group membership. This is not a new relation.

4. **Do NOT bundle the strain edge.** `bacteriaStrain` is a document-id STRING sitting in
   `data` (`doImport.m:734`), not an edge. Minting `strain_id` from it is a second
   unverified-resolvability edge — the shape that turned `distance_metadata` from a quiet
   passthrough into a GATING orphan failure. Separate step, separate decision.

5. **No corpus can grade this.** `runCorpusDiscovery` runs five passes and ZERO
   `ndi.migrate.*`, so NDI-side subject resolution is invisible to the corpus gate. The
   scouting recommendation is to build the join DID-SIDE as a batch post-pass, since it
   needs only documents already in the migrated batch — no session, no database, no file
   bytes — the same criterion that put `epochMint` and `resolveSessionAnchors` DID-side.

### What it unblocks

4,563 JH `image_stack` documents stop being observations about nobody, and the ~4,563
`ontology_label` documents that inherit their subject through the image unblock with them
(`ndi.migrate.internal.ontologyLabelSubjects.m:59-73` records that bucket as blocked on
exactly this). The plate's OD600 / CFU / lawn-volume covariates and the lawn's geometry
become real observations rather than dropped columns.
