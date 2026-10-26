# Lossless carries (DID-matlab #247, NDI-matlab #1067): which v1 fields block the fold

This is research only. Nothing was pushed, merged or written to any repository. Every option and recommendation below is **Proposed (not decided)**.

## Denominator

**13 classes inspected.** These are every class whose carried count rose between the V2 baseline (DID run 40176326172) and the PR (DID run 40200884753). The source is the `unconverted_by_class` field of the corpus report artifacts (`scratchpad/art/base/*` against `scratchpad/art/{12602971412,12603802313,jh}/`), plus `stimulus_response_scalar`, whose carry is counted by epochMint rather than pass 1.

Corpora where a class rose: Soph, 20211116, JH and Dab. In B and PRED the unconverted count did not change (6,223 → 6,223 and 0 → 0).

| corpus | class | carried before → after (measured) |
|---|---|---|
| Soph | tuningcurve_calc | 0 → 34,606 |
| Soph | contrast_tuning_calc (v1 `contrasttuning_calc`) | 0 → 22,896 |
| Soph | spatial_frequency_tuning_calc | 0 → 2,804 |
| Soph | temporal_frequency_tuning_calc | 0 → 2,800 |
| Soph | jrclust_clusters | 0 → 1 |
| Soph | stimulus_response_scalar | `response_scalar_folds_emitted` 9,851 → 0; `response_refused_migrator_declined` 0 → 9,851 |
| 20211116 | tuningcurve_calc | 0 → 84 |
| 20211116 | hartley_calc | 0 → 210 |
| 20211116 | stimulus_response_scalar | folds 273 → 0; declined 0 → 273 |
| JH | ontology_table_row | 14,478 → 34,889 (+20,411) |
| JH | image_stack | 4,563 → 7,007 (+2,444) |
| JH | position_metadata | 0 → 2,078 |
| JH | subject_group | 0 → 353 |
| Dab | treatment | 0 → 49 |

Two classes did not rise, as a check on the method: Soph `oridirtuning_calc` (6,106) and `contrastsensitivity_calc` (1,431).

### How "blocks" was measured

- **Four tuning families and the encounter rows.** I re-implemented the PR's "unplaced" logic in Python and ran it over every document of the class in the corpus zips:
  - tuning families: `jTuningCurve.m`, emulated by `scratchpad/scripts/tuning_drop.py`;
  - encounter rows: `ontology_table_row.m` `encounterUnplaced`, emulated by `scratchpad/scripts/otr_drop.py`.

  The emulated carry counts equal the measured CI counts exactly:

  | class | emulated carries |
  |---|---|
  | tuningcurve_calc | 34,606 / 84 |
  | contrast | 22,896 |
  | SF | 2,804 |
  | TF | 2,800 |
  | oridir | 0 |
  | encounter rows | 20,411 |

  I take that match as evidence that the per-field counts are right. This was not run in MATLAB.
- **The other classes** have a single-field condition. Their counts come from the field census `scratchpad/scripts/census.py`: a field counts as filled when it is not null, `""`, `[]` or `{}`, read to depth 3. Its outputs are `scratchpad/census_*.json`.
- **Carry notes not read.** The per-document `carried_as_v1` notes are not kept in the corpus reports, so they were not read. Every count here is a field census or an emulation.
- **References.**
  - DID-matlab is cited at PR head `94bb904`. NDI-matlab is cited at the locked `main` `3cb19a85` (`tools/sibling_lock.json`); NDI `origin/main` has since moved to `8f2b0c7`.
  - did-schema is cited at `origin/main` `6154b1a`. "Candidate V2 home" is searched only among classes whose `index.json` disposition is `persist`.

## Per-field table

"Always" means the field is filled in every document of that class in that corpus.

| class | v1 field | fold/step that cannot place it, and why | v1 writer (template; .m) | always / sometimes | corpora, count blocking | candidate V2 home (did-schema `schemas/V_eta/`) |
|---|---|---|---|---|---|---|
| tuningcurve_calc | `stimulus_tuningcurve.stimid` | `jTuningCurve.m` `rawCurve` reads no `stimid`, so it falls into `rest` and is listed as dropped (`jTuningCurve.m:272-274`). `jCalculation.m:137-145` then carries the document. | template `database_documents/stimulus/stimulus_tuningcurve.json` (`"stimid": []`); writer `+ndi/+app/+stimulus/tuning_response.m:452,464` | ALWAYS | Soph 34,606/34,606; 20211116 84/84 | No field named for it. Candidate: a covariate along the stimulus dimension (`stable/data.json` `/covariates`). That is how `stimulus_response_scalar.m` already places `responses.stimid` (header, "responses.stimid -> dimension 0 ... a `stimulus` covariate"). Not verified that it fits the tuning_curve value. |
| tuningcurve_calc | `stimulus_tuningcurve.stimulus_presentation_number` | Same as `stimid` (`jTuningCurve.m:272-274`) | same template; writer `tuning_response.m:473,500` (point × trial matrix) | ALWAYS | Soph 34,606; 20211116 84 | None found by name. Candidate: a covariate along the [condition, trial] axes that `individual` already has (`stable/tuning_curve.json` `/value/individual`). Not verified. |
| tuningcurve_calc (latent) | `tuningcurve_calc.log`, `tuningcurve_calc.stim_property_list` | **Not checked by the carry test.** jCalculation reads the calculator block only for `input_parameters` (`jCalculation.m:216-229`) and lists unplaced fields only for `sourceBlock` (`:137-139`). `grep -rn "'log'\|stim_property_list"` under `+did2/+convert` returns nothing. These fields block nothing today, because `stimid` already carries every document. If `stimid` were given a home, they would be dropped silently. | template `apps/calculators/tuningcurve_calc.json` (`"log": []`); writer `+ndi/+calc/+stimulus/tuningcurve.m:249` | `log`: sometimes (Soph 32,984/34,606; 20211116 84/84). `stim_property_list`: sometimes (Soph 22,896/34,606) | not blocking (latent) | none found |
| contrast_tuning_calc | `contrast_tuning.fit.naka_rushton_{RB,RBN,RBNS}_relative_max_gain` (3 fields) | `jTuningCurve.m` `oneFit` maps only the names in `mmap` (`:494-506`). `relative_max_gain` is not one of them, so it is dropped (`:526`, then `fitEntries` `:472`). | No contrast_tuning template or writer in NDI-matlab at `3cb19a85` (`git ls-tree -r` shows none). Writer not found; it is in NDIcalc-vis, which is not held. | ALWAYS | Soph 22,896/22,896 each | `stable/tuning_curve.json` `/value/model_fit/metrics` is a closed list without it. The same name exists on `stable/contrast_sensitivity.json` (`relative_max_gain`, line 619). Needs a schema change: add it to `model_fit.metrics`. |
| contrast_tuning_calc | `...naka_rushton_{RB,RBN,RBNS}_saturation_index` (3) | same as above | writer not found | ALWAYS | Soph 22,896 each | same; the name is on `contrast_sensitivity.json` (line 645) |
| contrast_tuning_calc | `...naka_rushton_{RB,RBN,RBNS}_sensitivity` (3) | same as above | writer not found | ALWAYS | Soph 22,896 each | same; the name is on `contrast_sensitivity.json` (line 606) |
| spatial_frequency_tuning_calc | `spatial_frequency_tuning.abs` (sub-blocks `fitless`, `fit_dog`, `fit_gausslog`, `fit_movshon`, `fit_movshon_c`, `fit_spline`) | `jTuningCurve.m:217-222`: `abs` is not in `known`, so it is listed whole as dropped. The block is not a copy of the top-level fits: in 0/2,804 documents is every `abs` sub-block identical to its top-level counterpart, and `fit_dog` differs in 2,804/2,804 (measured). | writer not found (NDIcalc-vis, not held) | ALWAYS | Soph 2,804/2,804 | None found. No persist class has an `abs` field or a second fit set. |
| temporal_frequency_tuning_calc | `temporal_frequency_tuning.abs` (same 6 sub-blocks) | same as SF | writer not found | ALWAYS | Soph 2,800/2,800 (identical in 0) | none found |
| hartley_calc | `reverse_correlation.method` (value `"Hartley"` in 210/210) | `hartley_calc.m:332-338` passes it as `Dropped`, because the method term `ndi.calc.vis.hartley` is taken to imply it. `jCalculation.m:137-145` then carries the document. | writer not found (NDIcalc-vis, not held; `git ls-tree` at `3cb19a85` shows no hartley template) | ALWAYS | 20211116 210/210 | Candidate: `stable/interaction.json` `/method/parameters` (a term or label entry). Or the team accepts that `method.term` restates it. No schema change needed. |
| stimulus_response_scalar | `stimulus_response.stimulator_epochid` | `stimulus_response_scalar.m:123-125`. The plan drops this field as "a copy of the presentation's own epoch" (header, `:58`); epochMint then counts the document as `response_refused_migrator_declined` (`epochMint.m:1323`). | template `stimulus/stimulus_response.json`; writer `tuning_response.m:322` (`stim_doc.document_properties.epochid.epochid`) | ALWAYS | Soph 9,851/9,851; 20211116 273/273 | None on a persist class (`stable/stimulus_response.json` has the field, but its disposition is `retire`). Candidate: the stimulator's epoch reached through the presentation's time reference. Redundancy with the presentation epoch is asserted in the header, not measured. |
| stimulus_response_scalar | `depends_on stimulus_control_id` | `stimulus_response_scalar.m:126-127`. "Decided by Jess Haley, 2026-10-22 [control as covariate]" (`V_eta_stimulus_response_model_plan.md:618`) says the control record becomes no V2 document. | template `stimulus/stimulus_response.json`; writer `tuning_response.m:332` | ALWAYS | Soph 9,851; 20211116 273 | Under [control as covariate] the content's home is the presentation's `control condition` covariate (XCO:0000099). The edge itself has none. |
| image_stack | `depends_on document_id` (the ontologyTableRow the image belongs to) | `image_stack.m:197-202`. #88 gives the observation no edge for it. The removed baseline comment said "#88 dropped image_observation's `ontology_table_row_id` edge (#73 item 42)" (`git diff origin/V2...HEAD -- image_stack.m`). | template `data/imageStack.json` (`depends_on document_id`); writer `+ndi/+setup/+conv/+haley/doImport.m` sets `document_id` at :430, :448, :464, :473, :480, :489, :499, :508, :794, :802, :814, :819 (which document each line belongs to was not checked one by one) | ALWAYS (7,007/7,007). The other 4,563 already carried in the baseline for having no `subject_id` (`image_stack.m:~187-191`). | JH 7,007, of which 2,444 are new | None found (`grep -rln ontology_table_row_id schemas/V_eta` is empty). Candidate: a relation document. Not verified. |
| position_metadata | `position_metadata.units` | `position_metadata.m:63-73`: the observation fold has no place for it | template `element/position_metadata.json`; writer `haley/doImport.m:598` (constant `'NCIT:C48367'`, pixels) | ALWAYS | JH 2,078/2,078 | Candidate: `draft/coordinate_system.json` `axes[].spacing` (`source_unit`). Not verified. |
| position_metadata | `position_metadata.dimensions` | same | writer `doImport.m:599` (constant `'NCIT:C44477,NCIT:C44478'`, X and Y) | ALWAYS | JH 2,078/2,078 | Candidate: `draft/coordinate_system.json` `axes[].axis`, or `stable/data.json` `/dimensions/term`. Not verified. |
| subject_group | *missing* `subject_group.group_name` (no v1 field blocks; a required V2 value has no source) | `subject_group.m:44-51`. `entity.local_identifier` would have to be invented ("Decided by Jess Haley, 2026-10-25 [no invented values]", `V_eta_go_forward_class_audit.md:1142`). | template `subject_group.json` is `"subject_group": {}`: the v1 class declares **no** `group_name`. Writers `+haley/doImport.m:340`, `+babu/import.m:260,271,507,555` write `ndi.document('subject_group')` with no fields. | ALWAYS (353/353 have `subject_group` = `{}`) | JH 353 | `stable/entity.json` `local_identifier`: the home exists, the value does not. Whether `local_identifier` is required for type group depends on `entity_type_bindings` (not checked). |
| treatment | `treatment.name` = "Optogenetic Tetanus Stimulation Target Location" | `treatment.m:79-84`. The fold would strip the "target location" suffix from the variable's label and keep the v1 spelling nowhere. | template `treatment.json`; writer `+dabrowska/doImport.m:301-306` (constant name, `ontologyName` EMPTY:0000074, `string_value` an UBERON site) | ALWAYS | Dab 49/49 | No change needed if the label is kept unstripped as `variable.name`. EMPTY:0000074 is not in `V_eta_term_registry.json` (grep empty). The Dab meaning (stimulation at a site) belongs to the Dab map (NDI `sliceTetanus`, EMPTY:0000358). |
| ontology_table_row (encounter rows) | the column ontology node of every one of the 13 columns (`ontologyTableRow.ontologyNodes`, EMPTY:0000096, :0000134, :0000139-:0000149) | `ontology_table_row.m:229-263` (`encounterUnplaced`): `applyEncounterMap` writes each measure's variable with `node ''` (`:305`), so a non-empty column node counts as unplaced | template `data/ontologyTableRow.json`; writer `+ndi/+setup/+NDIMaker/tableDocMaker.m:177-219` (node per column from `ndi.ontology.lookup`) | ALWAYS (20,411/20,411; 13 distinct nodes) | JH 20,411 | **Home exists:** the variable's `node` (ontology_term). A code change in the map, not a schema change. |
| ontology_table_row (encounter rows) | `data.CElegansBehavioralAssay_EncounterIdentifier` | `encounterUnplaced`: the map does not read it ("derived", `:288`) | writer `haley/doImport.m:645,680,688-689` (`encounterNum`, a key of the table). The mapping to this column name through `+haley/tableDoc_dictionary.json` was not verified. | ALWAYS | JH 20,411 | None found. Candidates: `local_identifier` on the encounter relation or window. Not verified. |
| ontology_table_row (encounter rows) | `data.CElegansBehavioralAssay_PeakVelocityBeforeEncounterOnset`, non-finite | `encounterUnplaced` `numericValue` fails | same writer | sometimes (3/20,411, emulated) | JH 3 (also blocked by the two rows above) | as for the other measures |
| jrclust_clusters | `ndi_document` (`{"name": "jrclust.prm"}`) beside `base` (`base.name` is `""`) | `universalRenames.m:287-298` discards `ndi_document` when `base` exists. `v1_to_v2.m:297-327` carries the document on a non-empty `renameDropped`. | current template `apps/jrclust/jrclust_clusters.json` has no `ndi_document`; current writer `+ndi/+fun/+probe/+import/+jrclust/probe.m:242`. The legacy block is from NDI before `ndi_document.json` was deleted (9783809c2, 2023-04-13, per `universalRenames.m:122-136`). | sometimes (1/61 in Soph) | Soph 1 (`legacy_ndi_document.discarded_by_class`) | **Home exists:** `stable/base.json` `name`, which is empty on this document. A code change: fill `base.name` when it is empty. |

## Per-class summary

"All always filled" means the class never folds on real data until either code or schema changes, as noted.

| class | blocking fields | all always filled? | what unblocks it |
|---|---|---|---|
| tuningcurve_calc | 2 (`stimid`, `stimulus_presentation_number`), plus 2 latent (`log`, `stim_property_list`) | **yes**: never folds | a covariate home (code; schema fit not verified) and a decision on the latent two |
| contrast_tuning_calc | 9 (3 metrics × 3 fits) | **yes**: never folds | **schema change** (`model_fit.metrics`) |
| spatial_frequency_tuning_calc | 1 (`abs`, 6 sub-blocks) | **yes**: never folds | **schema change** (none found) |
| temporal_frequency_tuning_calc | 1 (`abs`) | **yes**: never folds | **schema change** (none found) |
| hartley_calc | 1 (`reverse_correlation.method`) | **yes**: never folds | a decision only (method parameter, or "implied") |
| stimulus_response_scalar | 2 (`stimulator_epochid`, `stimulus_control_id`) | **yes**: never folds | a decision: does [control as covariate] count as placing the edge, and is `stimulator_epochid` a copy? |
| image_stack | 1 (`document_id`) | **yes**: never folds (7,007/7,007) | **schema change** (an edge) or a relation |
| position_metadata | 2 (`units`, `dimensions`) | **yes**: never folds | schema fit not verified (coordinate_system candidate) |
| subject_group | 0 fields; 1 missing required value | **yes**: never folds (v1 declares no name) | a decision: `local_identifier` not required for groups, or a value from the dataset map |
| treatment (Dab) | 1 (`name` suffix) | **yes**: never folds in Dab | code only (keep the label), or Dab map |
| ontology_table_row (encounter) | 13 column nodes + 1 (`EncounterIdentifier`), plus 3 rows non-finite | **yes**: never folds | code (write the node) **and** a home for `EncounterIdentifier` |
| jrclust_clusters | 1 (`ndi_document.name`) | no (1/61) | code only (`base.name`) |

All 12 rows in the corpus table are always blocked; the one exception is `jrclust_clusters`. On real data the folds for those classes no longer run at all.

## The 6 items that need a decision

Each is written as a question the team can answer without Claude. All options are **Proposed (not decided)**.

### DID 12. resolveDatasetEntities twin dedup and the membership drop

**Question:** When two dataset entities share a `base.id`, may the pass delete the "poorer" one, given that richness is a **count** of non-empty fields, not a comparison of their content?

The pass counts non-empty fields (`resolveDatasetEntities.m:390-410`) and deletes the loser (`:222-243`).

**Options:**
- (a) Merge the twins field by field, and carry both when they conflict. Nothing is lost. This needs new code in the pass.
- (b) Keep the deletion, but only when the loser's every non-empty field equals the winner's. Otherwise carry both sources as v1. This is lossless, and some datasets may keep a duplicate.
- (c) Accept as is. A field held only by the poorer twin is lost.

**Recommendation:** (b). It is the narrowest change that meets [generic stage is lossless], and it reuses the passthrough mechanism.

**Evidence:**
- Measured duplicates dropped:

  | corpus | duplicates dropped | ties (incumbent kept) |
  |---|---|---|
  | B | 13 | 12 |
  | Dab | 14 | 12 |
  | Soph | 33 | 0 |
  | JH | 2 | 0 |

- `membership_dropped_child_absent` is 0 in all six corpora (PR run artifacts).
- Whether any dropped twin held a field the kept one lacked: **not measured**.

### NDI 2b. subjectStrainAssembly removals

**Question:** subjectStrainAssembly removes background-strain, genetic-strain-type and duplicate-species assertions (`subjectStrainAssembly.m:216-295`) after DID pass 1 has already converted them. Is that removal "placed" (the fact moves to the strain entity), or does the lossless rule require the v1 source to survive?

**Options:**
- (a) DID carries the openminds subject as v1. This conflicts with "Decided by Jess Haley, 2026-10-23 [confirm sheet matches]" (`V_eta_go_forward_class_audit.md:1092`).
- (b) Add a "restore the v1 source" path in NDI. This is a second mechanism, which [partly placed is carried as v1] does not describe.
- (c) Accept as placed, because each removal is conditional on the strain entity being reachable (`:246`, `:274`).

**Recommendation:** (c), if the team agrees the fact survives on the strain.

**Evidence:**
- Header lines cited above.
- Corpus counts (`background_strain_assertions_removed`, `subjectStrainAssembly.m:358`): **not measured**, because the NDI corpus workflows did not run on #1067.

### NDI 6. epochAnchorFold 5 s tolerance

**Question:** Is NDI's `clocktype.m` docstring ("within 5 seconds") a v1 source value, so that writing `clock_tolerance` 5 s transcribes it rather than invents it?

**Options:**
- (a) Yes. Keep it as is; this matches TEAM-SIGN-OFF [time_reference] (`V_eta_time_reference_model_plan.md:468`, "the approx_ prefix de-encodes to an explicit clock_tolerance on the root").
- (b) No. Write the tolerance as unknown, which makes the approximation explicit without a number.

**Recommendation:** (a). The signed plan already decided the de-encoding, and the clock name can be rebuilt from term plus tolerance.

**Evidence:** `epochAnchorFold.m:250-262`, which cites `+ndi/+time/clocktype.m:21,23,26`.

### NDI 9. stimulusBathToBath

**Question:** The bath fold does the following:
- skips mixture rows with fewer than 5 columns and ignores columns after the 5th (`stimulusBathToBath.m:413`, `parseMixture88`);
- uses an amount only when it is finite (`:306-325`);
- writes no site observation for a generic "bath" location (`:366`, `isGenericBath` `:373-383`).

Should a bath with any of these be refused?

**Options:**
- (a) Refuse it, and release the deferred v1 bath from quarantine as a passthrough. This needs a new release path, because the bath comes from the pass-1 quarantine via `assembleDeferred` in `local.m`.
- (b) Write the generic location as a site term, and keep extra columns as mixture-entry text.
- (c) Accept as is.

**Recommendation:** (a) for extra columns and non-finite amounts, which are rare and not modelled. For the generic location, (c): "bath" restates the stimulus kind.

**Evidence:** code lines as cited. How often each case occurs in a corpus: **not measured**.

### NDI 10. settleIngestedFiles

**Question:** The pass does two things:
- it sets `delete_original` to 0 on every ingested location (`settleIngestedFiles.m:40`, `:168`, "a migration never deletes a file");
- when the bytes are missing, it sets `ingest` to 0 and replaces `location` with the store path (`:28-36`).

Are these storage-bookkeeping fields, outside the lossless rule, or v1 content that must be kept?

**Options:**
- (a) Bookkeeping. Accept as is.
- (b) Keep the original `location` beside the new one, which needs a field the file block does not have (not checked).
- (c) Carry the document as v1 when its bytes are missing.

**Recommendation:** (a) for `delete_original` and `ingest` (they describe an action, not the data). For `location` when bytes are missing, (c).

**Evidence:** the header cites, for the Soph corpus, "element_epoch 252, stimulus_presentation 11 ... at a path on the author's computer" (`:20-21`). This was not re-measured.

### NDI 11. ensembleMembership

**Question:** "Decided by Jess Haley, 2026-10-22 [ensemble retired]" (`V_eta_ensemble_plan.md:284`) dissolves the ensemble map into a group plus `member_of` edges. Does [generic stage is lossless] (2026-10-25) override that, for map fields the dissolution does not keep?

**Options:**
- (a) No. The earlier, specific decision stands. The combined bytes are kept: the `acquisition_epoch` holding them "is NOT touched" (`ensembleMembership.m:122`).
- (b) Yes. Carry the map as v1 when any of its fields is not placed.

**Recommendation:** (a). The map's roster lives on its `depends_on` edges (`ensembleMembership.m:28-39`), the dissolution moves it to `member_of`, and the bytes survive.

**Evidence:** lines cited. Which map fields, if any, are left unplaced on a real corpus: **not measured**.

## Commands (as run)

```
python3 -I scratchpad/scripts/tuning_drop.py scratchpad/corpora/Soph.zip      # and 20211116.zip
python3 -I scratchpad/scripts/otr_drop.py scratchpad/corpora/JH.zip
python3 -I scratchpad/scripts/census.py <zip> <out.json> <classes>            # census_*.json
git -C NDI-matlab show 3cb19a85:src/ndi/ndi_common/database_documents/<path>.json
git -C did-schema grep / python over schemas/V_eta/index.json (disposition == persist)
```
