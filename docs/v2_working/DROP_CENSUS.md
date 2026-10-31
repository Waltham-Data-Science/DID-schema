# Drop census: v1 information the generic migration drops or rewrites by an earlier choice

This is research only. Nothing was pushed, committed or merged, no repository was edited, and no decision line was written. Every recommendation below is **Proposed (not decided)**.

The rule each row is checked against is [generic stage is lossless] and [partly placed is carried as v1] (Jess Haley, 2026-10-25, `docs/plans/did_v2_go_forward_class_audit.md` on did-schema `claude/ecstatic-pascal-md91fw`).

## 1. Denominators

### What was read, and at which commit

All clones are fresh, in `scratchpad/dropcensus/`, with one worktree per ref under `wt/`.

| repo | ref | commit | files in scope | how they were inspected |
|---|---|---|---|---|
| DID-matlab | `origin/V2` | `0ea690a9` | 220 `.m` under `src/did/+did2/+convert/**` | grep of all 220; diff against the lossless branch |
| DID-matlab | `origin/claude/lossless-generic` | `8f3b904c` | 220 `.m` (22 differ from V2) | see the next table |
| NDI-matlab | `origin/V2` | `25a1f83e3` | 38 `.m` under `src/ndi/+ndi/+migrate/**` | grep of all 38; diff against the lossless branch |
| NDI-matlab | `origin/claude/lossless-generic` | `240fcafad` | 38 `.m` (7 differ from V2) | grep of all 38. Read in part: `local.m` (stimulus and control fold, `decodeBodies`, bath), `stimulusPresentationToItem.m` (`unplacedPresentationFields`), `epochAnchorFold.m` (header). **0 read in full.** |
| NDI-matlab | locked `main` | `3cb19a85` | 104 v1 templates under `src/ndi/ndi_common/database_documents/` | parsed by script |
| did-schema | `origin/main` | `6154b1a` | 65 `schemas/*.md` | grep for decision lines and drop prose |
| did-schema | `origin/claude/ecstatic-pascal-md91fw` | `bc4029c` | 65 `schemas/*.md` | same grep |

### How the DID-matlab migrators were compared (lossless branch)

| check | denominator | result |
|---|---|---|
| Code read in full (comments skipped) | **43 files** | The 34 short `+migrators_j` migrators named in the template check, plus `element.m`, `dataset_session_info.m`, `syncrule.m`, `+super/image_stack_parameters.m`, `private/jMethodParameters.m`, `private/jParameterList.m`, `private/jMembershipBodies.m`, `+migrators/distance_metadata.m` and `+migrators/element_epoch.m`. |
| Header and mapping sections read, code only where it matters | 21 files | `hartley_calc`, `lightsheet_zarr_pyramid`, `lightsheet_zarr_level`, `image`, `image_stack`, `probe_geometry`, `daqreader_ndr`, `neuron_extracellular`, `metadata_editor`, `syncrule_mapping`, `session_in_a_dataset`, `private/jClockAlignmentBodies`, `private/jFrequencyFilter`, `private/jTuningCurve`, `private/jCalculation`, `calcCommon`, `epochMint`, `resolveDatasetEntities`, `resolveSessionAnchors`, `resolveEpochProbemap`, `foldGenericFiles` |
| Grepped only | the other 156 of 220 | |
| Template check (`scripts/fieldcov.py`) | 104 templates; 84 have a `+migrators_j` migrator | Each template's own-block leaf fields and `depends_on` names were compared with the code of the routed migrator (its private-helper closure, plus `+super` and `+migrators` for its superclasses). 52 templates had at least one field the code never names. Each of the 52 was then read by hand. Most are whole-document passthroughs (`bodies = {preBody}`), so they lose nothing. |
| Corpus check (`scripts/corpuscov.py`) | 44 classes, every field path filled in a held corpus | Same comparison, driven by the fields that real documents fill. Output: `corpuscov_ll.txt`. |

### Corpora

- **Held locally** (the zips the earlier agent used): `20211116` (1,220 JSON), `Dab` (27,561), `JH` (78,688) and `Soph` (101,427). Unreadable: 0.
  - Field census: `scripts/fullcensus.py`, output `census_*.json`. A field counts as filled when it is not null, `""`, `[]` or `{}`, read to depth 5.
- **B and PRED** are not held. Their figures come only from the counters in the lossless PR run summaries (`scratchpad/art/12602971412`, `12603802313`, `jh`), via `scripts/counter.py`.
- **NDI second-pass frequencies are not measured.** No NDI corpus run on #1067 is held.

### Counts

| | number |
|---|---|
| Drop rows in the table below (new; not rows of `carry_fields_TABLE.md`) | **25** (rows 1-24 plus 13b) |
| with a decision found (a `Decided by` / `TEAM-SIGN-OFF` line, or a dated, named code comment) | **9** (rows 7, 8, 11, 13, 13b, 14, 15, 19, 22) |
| with only an undated or unnamed code comment, an unsigned plan principle, or a decision about a different class | **10** (rows 2, 3, 6, 9, 10, 12, 16, 17, 18, 24) |
| with no decision found | **6** (rows 1, 4, 5, 20, 21, 23) |
| still dropped on the lossless branch | **21** |
| carried as v1 on the lossless branch | **1** (row 13, `pyramid_type`) |
| placed, or the drop is only an empty value (the content moves elsewhere or there is none) | **3** (rows 15, 22 and 24) |
| affecting documents in the held corpora (more than 0) | rows 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15 |

Checked and excluded because nothing from v1 is lost:

- `time_reference.is_approximate` (`resolveSessionAnchors.m`): no NDI v1 template declares it (`grep -rl is_approximate` over the 104 templates is empty). DID's own writers set it.
- The vmspikefit / fitcurve "0..1 scale": an invention of the old code.
- `withSessionId`'s `base.session_id`: moved to an edge.
- `ingestion_manifest`'s char `epoch_id`: replaced by an edge.
- `ontology_label`: a passthrough now.

## 2. The table

Status abbreviations: **SD** = still dropped on the lossless branch; **V1** = carried as v1; **PL** = placed. Unless a row says so, the V2 and lossless branches behave the same: the file is not among the 22 / 7 the lossless build changed, or the change does not touch this drop.

Corpus abbreviations: **Soph**, **2021** (20211116), **Dab**, **JH**.

### Classes present in the held corpora

| # | where | class and v1 field | what is lost (example) | decision found | status | frequency | lossless home candidate | reason the drop may still be right | recommendation |
|---|---|---|---|---|---|---|---|---|---|
| 1 | DID `+migrators_j/element.m`, `element` (`depValue` reads only `subject_id` and `underlying_element_id`) | `element`, `depends_on jrclust_clusters_id` | The link from a sorted neuron to the JRCLUST output that produced it. Example: 2021 element `leftcortex_17` (`ndi.neuron`) → `jrclust_clusters` `4126943ebaaa11e6_c0d7d77fd0afeb50`. In 2021 the neuron's own `neuron_extracellular.spike_clusters_id` is empty (21/21, `neuron_extracellular.m` header), so this edge is the only link. | **No decision found.** Searched: `jrclust_clusters_id` in DID `+convert` (0 hits), NDI `+migrate` (0), did-schema `schemas/*.md` (0) and NDI `main` `src` (0: the current writers use `spike_clusters_id` on `neuron_extracellular`, `+jrclust/probe.m:320`). | SD | Soph 1,554/1,647 element docs; 2021 21/23 | The neuron calculation's `input_id`. `neuron_extracellular.m` already writes it from `spike_clusters_id`. Or a `derived_from` relation; `element.m` already emits one to the underlying element. | none found | **Place** as the neuron calculation's input (preferred), else carry the element as v1 when the edge is set. |
| 2 | DID `+migrators_j/session_in_a_dataset.m` and `dataset_session_info.m`, via `jMembershipBodies` | `session_in_a_dataset.{is_linked, session_creator, session_creator_input1..6, session_reference}` | How each member session is opened. Example: `is_linked` 0, `session_creator` `"ndi.session.dir"`, `input1` `"2008-08-07"`, `input3` = the session id. | **Code comment only**, unnamed and undated ("NDI-internal session-assembly reconstruction handles"). It contradicts signed text: `did_v2_linked_session_plan.md:95` (TEAM-SIGN-OFF, jess, 2026-10-09) says "a linked session's location is a linked_session configuration document (path, entity_id)", and `did_v2_nonsubject_cohesiveness_plan.md:485` says "`is_linked` rides the edge". | SD | Dab 14, JH 2, Soph 32. In all 48: `is_linked` 0, `input1` = `session_reference`, `input3` = `session_id`, inputs 2 and 4-6 empty (measured). | `draft/linked_session.json` (disposition `persist`; fields `path`, `entity_id`); the `part_of` relation for `is_linked` | For `is_linked` 0, `input1` and `input3` restate the reference and id (measured), but `session_creator` (the opener class) is stated nowhere else. Not verified: that the member session's own document carries the same reference. | **Guarded drop**: drop only the fields equal to the reference or id; carry as v1 when `is_linked` is 1 or `session_creator` is not the default. Later, build `linked_session` per the signed plan. |
| 3 | DID `+migrators_j/metadata_editor.m` (Bucket 2 and Bucket 3) | `metadata_editor.metadata_structure.{DataType, ExperimentalApproach, TechniquesEmployed, Subjects/SpeciesList/StrainList/BiologicalSexList}`, plus editor GUI state | Example (Soph): `DataType` `"derivedData"`. It is not a projection of any subject statement, which is what the header's reason assumes. | Plan principle with no name, date or decision line: "D-D Round-trip — RESOLVED (principle): adopt J's drop-fully-with-projection" (`did_v2_nonsubject_cohesiveness_plan.md:432`). Header text in `metadata_editor.m:52-63`. | SD (the lossless edit carries only an unrecognised EthicsAssessment and multiple affiliations) | Soph 1/1 (`DataType` only; the other bucket-2 fields are absent) | The header names a dataset `experimental_approach` field (not verified in the schema). For `DataType`: a term assertion on the dataset entity. | The species, strain and sex lists are true projections of the subject assertions. GUI state is not data. | **Carry as v1** when `DataType`, `ExperimentalApproach` or `TechniquesEmployed` is non-empty. Keep the drop for the subject projection lists only if they equal the subjects' assertions (not measured). |
| 4 | NDI `local.m` `resolveStimulusPresentations` + `+internal/stimulusPresentationToItem.m` `unplacedPresentationFields` | `stimulus_presentation.app` (`name`, `version`, `url`, `os`, `os_version`, `interpreter`, `interpreter_version`) | The software that wrote the presentation. Example (2021): `ndi_app_…`, `MATLAB` 24.2, `MACA64`. The lossless check reads only the presentation block, `stimuli` and `parameters`, never `app`. A consumed presentation is removed (`local.m` ~2997). | **No decision found.** The rule `app` → `software` (R1, `did_v2_go_forward_class_audit.md:45`) says to place it. Searched: `app`, `software` and `jSoftwareFromApp` in `stimulusPresentationToItem.m`, `stimulusMethod.m`, `stimulusRecipe.m` and `local.m` 2800-3060 (0 code hits). | SD (NDI) | 1,428 presentations carry `app` (2021 11, Dab 1,242, Soph 175). How many are consumed rather than refused: **not measured**. | a `software` entity plus the manipulation's `software_id` (how DID's `jSoftwareFromApp` places `app` everywhere else) | none found | **Place** (R1). Until then, add `app` to `unplacedPresentationFields`, so that a presentation is carried as v1. |
| 5 | NDI `local.m` ~3004 (`controlFolded`), the fold of `control_stimulus_ids` into the presentation's covariate | `control_stimulus_ids.control_stimulus_id_method.{method, controlid, controlid_value}`, plus `app` | How the controls were picked. Example: `method` `"pseudorandom"` (Dab spells it `"psuedorandom"`), `controlid` `"isblank"`, `controlid_value` 1. Also the app version. | [control as covariate] (Decided by Jess Haley, 2026-10-22, `did_v2_stimulus_response_model_plan.md:618`) says the document "becomes no V2 document" and "the per-trial pairing is dropped". It does **not** name the method block or `app`: **no decision found for those two.** | SD (NDI) | 1,428 docs carry both (2021 11, Dab 1,242, Soph 175) | The `control condition` covariate (XCO:0000099), with the method as method parameters (not verified that the covariate takes a method) | The pairing drop is decided and NDI's vintage layer rebuilds it (same line). | **Ask** (Q5). Without a slot, the strict rule carries the record as v1. |
| 6 | DID `private/jClockAlignmentBodies.m` (the folded arm of `syncrule_mapping`, run by `epochMint`) | `syncrule_mapping.epochnode_{a,b}.{objectname, objectclass, epochprobemap, epoch_session_id}` | The device name, class and probe map of each endpoint. Example: `objectname` `"vhvis_spike2"`, `objectclass` `"ndi.daq.system.mfdaq"`. NDI `+time/syncgraph.m:406` queries `objectname` by `exact_string`. | **Code comment only** (`jClockAlignmentBodies.m:190-197`: "#73 item 54 … V_eta documents write no base.name … on a FOLDED mapping the name is not carried"). No decision line found. | SD | Folds: Dab 2,484, Soph 348, B 2,484 (`epoch_mint.syncrule_folds_emitted`, PR run). Every Dab and Soph mapping fills all four fields. | `objectname` → reachable as `acquisition_system.base.name` (kept per TEAM-SIGN-OFF [daq configuration], 2026-08-08). `epochprobemap` → the epoch's `ingestion_manifest` (kept verbatim, `resolveEpochProbemap.m:16-17`). | Probably redundant through the graph. **Not measured** per document. | **Guarded drop**: drop each field only when it equals what the graph states; carry as v1 otherwise. |
| 7 | DID `+migrators_j/hartley_calc.m` (GUARD 2, `checkStimulusPropertiesAreDroppable`) | `hartley_reverse_correlation.stimulus_properties.{M, L_max, K_max, sf_max, fps, color_high, color_low, rect}` | The Hartley generator settings. Example: M 200, K_max 20, fps 10, rect [-7, -138, 793, 662]. The migrator checks keys only; the values are compared in `did2.validate.sourceCensus`, which only reports. | TEAM-SIGN-OFF [receptive field fold] (jess, 2026-08-17, `did_v2_ngrid_family_findings.md:358`), as the code quotes it: "dropped only when equal, refused and reported when not". | SD (folds now that the method is implied) | 2021 210/210. **Measured equal** to the presentation's generator spec in 210/210 (`scripts/hsp.py`). | the presentation (same values) | Equal on every held document. | **Keep**, but move the value-equality check into the migrator: refuse, carry as v1, when the values differ. |
| 8 | DID `hartley_calc.m` (field map, `:130`) | `reverse_correlation.dimension_labels` | Nothing in the corpus (it is `''`). The code never reads the field, so a non-empty value would be dropped. | Code comment: "DROPPED. Empty in 210 of 210, and the signature names it droppable" (the [receptive field fold] signature). | SD | 2021 0/210 non-empty | the axis labels | Empty everywhere measured | **Guarded drop**: drop when empty, carry as v1 otherwise. |
| 9 | DID `+migrators_j/neuron_extracellular.m` `checkRedundantCount` | `neuron_extracellular.{number_of_samples_per_channel, number_of_channels}` | Nothing when they equal the matrix shape. Otherwise the document errors (quarantine). | Code comment ("go the way `ngrid.data_size` goes"). The header cites the writer, `kilosort/probe.m:546-547`. | SD (guarded) | 2021 21, Soph 1,490. "Holds on 21 of 21" (header); Soph not re-measured. | the axis `n` | Derived and checked per document | **Keep**. Consider carrying as v1 instead of quarantining when they disagree. |
| 10 | DID `+migrators/calcCommon.m` (and `jCalculation`, which never reads the field) | `<calc>.depends_on`, the inner copy inside the calculator block | Nothing when it equals the top-level edge | Code comment (`calcCommon.m:21`, ":72 drop the redundant inner copy") | SD (unguarded) | **Measured equal** in every held document: Soph 69,212 (5 classes); 2021 336 (`scripts/innerdeps.py`) | the top-level `depends_on` | Equal everywhere | **Keep**, with an equality guard. |
| 11 | DID `+migrators_j/daqreader_ndr.m` | `daqreader_ndr.ndi_daqreader_ndr_class` | Nothing when it equals `daqreader.ndi_daqreader_class` | TEAM-SIGN-OFF [daq configuration] (jess, 2026-08-13, `did_v2_daq_family_decisions.md:540`): "`ndi_daqreader_ndr_class` dropped as redundant" | SD (unguarded) | Dab 1. Equal in 1/1 (`"ndi.daq.reader.mfdaq.ndr"`). | `daqreader.ndi_daqreader_class` | Equal | **Keep**, with an equality guard. |
| 12 | DID `private/jMethodParameters.m` (`execution_environment` `rmfield`; the third output of `jSoftwareFromApp` is ignored) | `app.{os, os_version, interpreter, interpreter_version}` on `sorting_parameters`, `spike_extraction_parameters(_modification)` and `vmspikefilteringparameters` | The run environment | TEAM-SIGN-OFF [calculator mixin dropped (#73)] (jess, 2026-09-29, `did_v2_subject_calculation_plan.md:371`) moves the run environment to two software edges **on `subject_calculation`**. Nothing covers a `method` document. The code says "dropped, reported". | SD | 0 in the held corpora (none of the four classes occurs) | the `software` entity (already minted); `interpreter_id` / `operating_system_id` (declared on calculations, not on `method`: not verified) | none found | **Carry as v1** when any of the four is non-empty, until `method` has the edges. |

### Classes absent from the held corpora (0 measured; B and PRED not held)

| # | where | class and v1 field | what is lost | decision found | status | frequency | lossless home candidate | reason the drop may still be right | recommendation |
|---|---|---|---|---|---|---|---|---|---|
| 13 | DID `+migrators_j/lightsheet_zarr_pyramid.m` | `pyramid_type` | the stated reduction type | "DECIDED (Jess 2026-10-15): `pyramid_type` is DROPPED" (code comment, `:136-145`) | **V1** (lossless: carried whole when non-empty) | 0 | none | The v1 docs say not to trust it | done |
| 13b | same | `pyramid_name` when the pyramid has no `source_file_id`; `n_channels`; `byte_order` | the NGFF multiscales name ("a pyramid with no source has no store body, so it is not kept") | Same code comment, Jess, 2026-10-15 | SD | 0 | the observation's `notes` (where `label` already goes) | `byte_order` is repeated on every level; `n_channels` is the channel axis length | **Place** `pyramid_name` in `notes`. Keep the drop of `byte_order` and `n_channels` (derived). |
| 14 | DID `+migrators_j/lightsheet_zarr_level.m` | `codec_params`; `label`, `level`, `chunk_grid`, `n_chunks_stored`, `chunk_index_origin`, `subject_id`, `source_file_id`; and a level that holds **no bytes**, which emits nothing (L3(c)) | the compressor settings; the whole record of an empty level | Code cites "#73 L4" and "L3(c)", under TEAM-SIGN-OFF [lightsheet migrator points 1-11] (coverage ledger row `lightsheetZarrLevel`) | SD | 0 | `data_body.compression` (exists, `draft/data_body.json`); `description` | Most fields are derivable from the dimensions (header). Blosc headers record shuffle and typesize. | Keep the derivable fields. **Carry as v1** a level with no bytes. Put `codec_params` text in the body's `description`. |
| 15 | DID `hartley_calc.m` / `private/jNgridBody.m` / `+super/ngrid.m` | `ngrid.data_size`; `ngrid.coordinates` on the regular index axes | bytes-per-element; index positions | TEAM-SIGN-OFF [image / ngrid] (2026-08-08, `did_v2_image_model_plan.md:154`), and "Decided by Jess Haley, 2026-10-23 [ngrid block into sampled_body]" (`:226`) | **PL**/derived | 2021 hartley 210 (`data_size` = 8, `data_type` "double") | the datum type, the axis `n` | Derived | **Keep**. |
| 16 | DID `+migrators_j/image_stack.m` and `image.m` (fold arm, a document with no `document_id`) | `imageStack.formatOntology`, `imageStack_parameters.data_limits`, `image.{format, compression, label}`, `depends_on imageCollection_id` | the file format (e.g. NCIT:C85437), the value range ([0, 1] / [0, 255]), the collection | Code comments only: "dropped as derivable" (`image_stack.m:20-21`); "deferred, not a loss" and "`imageCollection_id` DELIBERATELY NOT CARRIED" (`image.m:158-180`). [image_collection retired] (2026-10-24) retires the class and does not mention the edge. | SD on the fold arm | JH 7,007/7,007 have `document_id`, so all are carried as v1 on lossless: **0 lost in the held corpora** | `data_body.format` and `data_body.compression` **exist** (`draft/data_body.json`; `sampled_body` ⊂ `data_body`), against `image.m`'s "sampled_body has no encoding field" | `label` is now placed (notes) for `image_stack` | **Place** format and compression. **Carry as v1** when `data_limits` or `imageCollection_id` is set. |
| 17 | DID `+migrators_j/probe_geometry.m` | `shank_id`, `contact_shape(_width/_height/_radius)`, `manufacturer`, `has_planar_contour`, `contour_x/y`, `ndim` | the contact geometry | Code only: "STILL DEFERRED … still dropped" (`:50-54`) | SD | 0 | none found (needs a contact-geometry model, per the header) | `ndim` is derivable | **Carry as v1** when any is non-empty. |
| 18 | DID `private/jFrequencyFilter.m` (called from `pyraview.m`) | `parameters.order` when fractional; `parameters.sampleFrequency`; `label` | the filter order, the design rate, the label | Code comment only (`:88-110`) | SD | 0 | method parameters (`sampleFrequency`) | `label` equals `type` in the PRED document (header; PRED not held) | **Carry as v1** for a fractional order, or a `label` ≠ `type`. **Place** `sampleFrequency` as a parameter. |
| 19 | DID `+migrators_j/syncrule.m` (the configuration arms) | `parameters.errorOnFailure`, and any parameter outside the read set | runtime behaviour | TEAM-SIGN-OFF [sync configuration] (2026-08-08), plan row 5 "DROPPED" (`did_v2_clock_alignment_cluster_plan.md:302`). Amendment 2026-09-29 (jess, **not signed**): "errorOnFailure now fits" in `method_parameters[]`. | SD in code; unreachable for the writer that sets it (a `commonTriggers…` rule has channels, so it passes through whole) | 0 (all held rules are filematch/filefind) | the configuration's `method_parameters[]` | | **Carry as v1** any unread parameter on the configuration arms. |
| 20 | DID `+migrators/element_epoch.m` | `t0_t1` rows beyond the clock count (truncated); `clocktype` when `epoch_clock` is also present | clock extents | **No decision found** | SD | 0: every held document has as many rows as clocks (`scripts/ee.py`) | | | **Carry as v1** on a mismatch. |
| 21 | DID `epochMint.m` (~2978) | a second acquisition_epoch's clock that **disagrees** about t0/t1 | the second extent (the first is kept, which picks a winner) | **No decision found**. The audit lists it (DID item 11), but the lossless build did not change `epochMint.m`. | SD | `epoch_extent_conflicting_clock` = 0 in all six PR-run corpora | | none | **Carry** the conflicting source as v1. |
| 22 | DID `resolveDatasetEntities.m` pass 1b | the session entity minted on the dataset id; its `reference` | lost only when the dataset already has a different `local_identifier` | Decided by Jess Haley, 2026-10-22 [dataset session reference] | **PL** (reference moved); conflict case SD | moved B 1, Dab 2, JH 1, Soph 1; conflicts 0 in all six | the dataset `local_identifier` | | Keep. **Carry as v1** on a conflict. |
| 23 | NDI `+internal/pathSPromotion.m` (`removeMask`, `dropCondition` ~652) | the site observation and its condition | the v1 statement (the fact survives as the part's assertion) | Code ([non-area image node, revisited] keeps non-area nodes). **No decision found** for the removal. | SD (file unchanged on lossless) | not measured (NDI) | the minted part | | Ask whether "the fact moves to the part" counts as placed (same shape as prior Q NDI 2b). |
| 24 | DID `jMeasurementFold`, `jDoseValue`, `jParameterList`, `stimulus_parameter`, `image_stack_parameters`, `binaryseries_parameters`, `ensureClassBlocks` | empty placeholders (`''`, `[]`, empty blocks) | nothing | Code comments (e.g. `stimulus_parameter.m:59` "the empty char is DROPPED, not coerced") | **PL** (empty is absence) | not counted | | Absence equals empty | **Keep**. |

### Cross-reference: the audit's "What blocks a lossless generic stage" lists and the earlier table

The audit lists are in `docs/history/review/corpus-code-audit-2026-10-24/{DID-matlab,NDI-matlab}.md`. The earlier table is `carry_fields_TABLE.md`.

- **Changed by the lossless build:** DID items 1-9, 13, 15, the element half of 14, the treatment half of 14, and the universalRenames half of 10. NDI items 2, 4, 5, 7, 8 and 12.
- **Not changed** (file not in the diff):
  - DID 10a (`is_approximate`: not a v1 field, excluded above)
  - DID 11 (row 21)
  - DID 12 (earlier Q "DID 12")
  - DID 14 `jResponseVariable` spelling and `resolveLawnPlateSubjects` relabel. Not verified whether a caller now carries those documents.
  - NDI 1 (`sliceTetanus`: decided [sliceTetanus to Dab map], build pending)
  - NDI 3 (row 23)
  - NDI 6, 9, 10 and 11 (earlier Qs)
  - NDI 13 (`ontologyRowSubjects` / `imagedEntitySubjects`, not audited)

## 3. Questions for Jess

Each question can be answered alone. All options are Proposed (not decided).

### Batch A: documents in today's corpora with no recorded decision

**Q1. Neuron element → its JRCLUST output (`element`, edge `jrclust_clusters_id`).** On 1,554 Soph and 21 of the 20211116 neuron elements, this edge is the only record of which sorting run produced the neuron, and the migration drops it.
- (a) Write it as the neuron calculation's input.
- (b) Carry the element as v1 when the edge is set.
- (c) Drop it.

**Recommendation:** (a).

**Q2. Session membership details (`session_in_a_dataset`).** `is_linked`, `session_creator` and its inputs, and `session_reference` are dropped. In all 48 documents held, `is_linked` is 0, and the inputs repeat the session's reference and id; `session_creator` ("ndi.session.dir") appears nowhere else.
- (a) Drop only the values equal to the reference or id, and carry the document as v1 otherwise.
- (b) Build `linked_session` now, per the signed 2026-10-09 plan.
- (c) Drop all of them.

**Recommendation:** (a) now, (b) later.

**Q3. Dataset form fields (`metadata_editor`: `DataType`, `ExperimentalApproach`, `TechniquesEmployed`).** These are dropped as "projections of the subjects", but Soph's `DataType` "derivedData" is not about subjects.
- (a) Carry the form as v1 when any of the three is set.
- (b) Write `DataType` as a term about the dataset.
- (c) Keep the drop.

**Recommendation:** (a).

**Q4. The software that wrote a stimulus presentation (`stimulus_presentation.app`).** All 1,428 held presentations name it. NDI's fold removes the presentation without writing it.
- (a) Write a software entity, as every other `app` block becomes one.
- (b) Count `app` as unplaced, so that the presentation is carried as v1.
- (c) Drop it.

**Recommendation:** (a), with (b) until (a) is built.

### Batch B: documents in today's corpora, earlier decisions to re-check

**Q5. How the controls were chosen (`control_stimulus_ids.control_stimulus_id_method` and `app`).** [control as covariate] says the record becomes no document and drops the per-trial pairing. It does not mention the method ("pseudorandom", "isblank" = 1) or the app.
- (a) The decision covers them: drop.
- (b) Put the method on the control covariate.
- (c) Carry the record as v1.

**Recommendation:** (b) if the covariate can hold a method, else (c).

**Q6. Sync mapping endpoints (`syncrule_mapping` `objectname`, `objectclass`, `epochprobemap`).** About 5,300 mappings fold and lose these. They are probably restated by the acquisition system's name and the epoch's manifest, but that was not checked per document.
- (a) Drop each only when it equals what the graph states; carry as v1 otherwise.
- (b) Carry them always.
- (c) Keep the drop.

**Recommendation:** (a).

**Q7. Hartley leftovers (`hartley_calc.stimulus_properties`, `dimension_labels`).** `stimulus_properties` equals the presentation's settings in 210/210 (measured), but the migrator checks only the keys. `dimension_labels` is dropped even if it were set.
- (a) Drop only when equal or empty; carry as v1 otherwise.
- (b) Keep as is.

**Recommendation:** (a). It carries nothing extra today.

**Q8. Restated values.** These are `ngrid.data_size`, the neuron count fields, the inner `depends_on` copy in calculator blocks, and `daqreader_ndr.ndi_daqreader_ndr_class`. All are measured equal to another field.
- (a) A value equal to what another field states is not a loss, so keep the drops, and add an equality check where none exists (the inner `depends_on`, the ndr class).
- (b) Carry them.

**Recommendation:** (a).

### Batch C: classes not in today's corpora

**Q9. Image file details (`image` / `imageStack` with no table-row edge).** `format`, `compression`, `data_limits` and the `imageCollection_id` edge are dropped. `data_body` has `format` and `compression` fields today.
- (a) Write format and compression there, and carry as v1 when `data_limits` or the collection edge is set.
- (b) Carry as v1 whenever any is set.
- (c) Keep the drop.

**Recommendation:** (a).

**Q10. Probe contact geometry (`probe_geometry`: shank, contact shape and size, manufacturer, contour).** These are dropped until a contact model exists.
- (a) Carry the document as v1 when any is set.
- (b) Keep the drop.

**Recommendation:** (a).

**Q11. Light-sheet leftovers.** These are `lightsheetZarrPyramid.pyramid_name` with no source; `lightsheetZarrLevel.codec_params`; and a level with no bytes, which today emits nothing.
- (a) Pyramid name into `notes`, codec settings into the body description, and an empty level carried as v1.
- (b) Keep the drops.

**Recommendation:** (a).

**Q12. Small unread settings.** These are:
- the run OS and interpreter on method documents;
- a fractional filter order, `sampleFrequency`, and a filter `label` that differs from its type;
- syncrule parameters outside the read set;
- `element_epoch` clock rows beyond the named clocks.

All are 0 in today's corpora.
- (a) Carry the document as v1 when any is set.
- (b) Keep the drops.

**Recommendation:** (a).

### Batch D: audit items the lossless build did not change

**Q13. Disagreeing epoch clocks (`epochMint`).** When two acquisition epochs disagree about one clock's extent, the second is dropped and the first kept. The count is 0 in all six corpora.
- (a) Carry the second as v1.
- (b) Keep.

**Recommendation:** (a).

**Q14. Audit items not built.** The audit listed the following, but the lossless build left their files unchanged:
- DID `jResponseVariable` (unit spelling);
- DID `resolveLawnPlateSubjects` (relabel);
- NDI `pathSPromotion` (site observation removed);
- NDI `ontologyRowSubjects` / `imagedEntitySubjects`.

Options:
- (a) Make them lossless in this build.
- (b) After the merge, class by class.

**Recommendation:** (b), recorded as pending in the decision line.

## Not verified

- No MATLAB was run. Every DID and NDI claim is read from code. NDI frequencies are not measured.
- B and PRED corpora are not held. They appear only through PR-run counters.
- **Row 6:** that `objectname` and `epochprobemap` equal the graph values per document.
- **Row 2:** that the member session's own document holds the same reference.
- **Row 4:** how many presentations are consumed rather than refused.
- **Row 1:** whether the neuron calculation's `input_id` can point at a `jrclust_clusters` calculation.
- **Row 3:** that the dataset `experimental_approach` field exists in the schema.
- The template check names fields by string. A field read through a computed name (e.g. `sprintf`) shows as unread. Those cases were resolved by reading the code.

## Scripts (all read-only)

- `scripts/fieldcov.py`
- `scripts/corpuscov.py`
- `scripts/fullcensus.py`
- `scripts/q.py`
- `scripts/counter.py`
- `scripts/innerdeps.py`
- `scripts/hsp.py`
- `scripts/ee.py`
