# Audit 2C: the 40 statement leaves, and cross-cutting checks over the built V_eta tree

READ-ONLY. DID-schema `claude/ecstatic-pascal-md91fw` at `51250ef`. Siblings as checked out locally, not fetched: DID-matlab `47cf8ba` and NDI-matlab `9609273e1`, both on `claude/v-eta-migration-plan-35jj1z`. This report decides nothing and writes no sign-off. Every status is a reading of the record, not a disposition.

## Denominator

- **Built tree.** 217 json files read under `schemas/V_eta/{stable,draft,deprecated,examples}`.
  - 211 are schema classes: 129 `persist`, 62 `retire`, 20 `in_progress` (from `index.json` `disposition`).
  - 4 are meta schemas (`is_meta`, no `document_class`).
  - 2 are example instances under `examples/`. They are excluded from every check except finding 9.
- **Fields and edges.** 1,281 field declarations walked, nested ones included. 148 edge (`depends_on`) declarations, with 72 distinct names.
- **Leaves.**
  - All 40 leaf files were read in full. They are exactly the persist classes whose names end in `_observation`, `_calculation`, `_manipulation` or `_assertion`, apart from the 4 `subject_*` direction parents.
  - 34 leaves have the shape `[subject_<direction>, <data_type>]`, direction first.
  - The other 6 are the tuning family: `tuning_curve_calculation` and its 5 single-parent family leaves (the signed shape).
  - 33 of the 40 declare nothing of their own. The 7 that do: `term_assertion` has one edge; the 6 tuning leaves have fields.
- **Who needs a leaf.**
  - The 105 rows of `schemas/V_eta_migration_targets.json`, reading `targets`, `decided_targets` and `second_pass`.
  - 1,232 `.m` files: 291 under DID-matlab `src`, 941 under NDI-matlab `src`. I searched them for each leaf name as a quoted string literal, skipping comment-only lines. Leaf names built at runtime, such as `[leaf '_observation']` at `jMeasurementFold.m:82`, cannot be found this way.
- **Governance.**
  - `status_board.signature_census()` reads 53 `schemas/*.md` files; 3 generated files are excluded. It accepts 48 sign-off lines and rejects 2: the code-fence quotation at `V_eta_method_parameters_plan.md:694` and the superseded line at `V_eta_go_forward_class_audit.md:798`.
  - The board has 27 families, 25 of them signed. The two unsigned families are `calculator mixin dropped (#73)` and `spatial_transcriptomics_family`.
  - For each class, I matched its name, as a whole word, against the paragraph of every accepted sign-off line.
- **Yardstick.** Read in full: `V_eta_tenets.md` (504 lines), `V_eta_spatial_transcriptomics_plan.md` (items 1–70, 534 lines), `review/73/OPEN_ITEMS.md`, and `review/73/audit_C_leaves_governance.md`.

## Summary

20 findings: **2 VIOLATION, 5 INCONSISTENCY, 8 STALE-DOC, 5 QUESTION**.

**Every one of the 40 leaves has a recorded need.**
- 28 have a migrator or batch pass that names the leaf as a literal in DID-matlab or NDI-matlab source; these literals are the evidence of a writer.
- 12 have no literal writer. Each of those 12 is a `decided_targets` entry or an NDI second-pass target.
- No leaf is needed without existing. Every `decided_targets` class exists in the tree.
- No #73 decision names a leaf that is not built. I checked every `*_observation|calculation|manipulation|assertion` name in the tenets, the #73 record and `OPEN_ITEMS.md`; every miss is a mention of a deleted class, in its historical context.

The five most important findings:
1. **VIOLATION (T2)**: `vmspikefit` is routed to `score_observation`, but its inputs are in the dataset. It has the same fit fields as `fitcurve`, which item 68 moved to `model_fit_calculation`, and no decision covers it (finding 1).
2. **VIOLATION (T13 tombstone rule)**: the retired spatial "tombstones" are not the v1 shape.
   - `spatial_gene_expression_pyramid` ⊂ `subject_observation`.
   - Four of these tombstones require snake_cased edges that v1 writes in camelCase.
   - So an unmigrated v1 document cannot validate against them (finding 14).
3. **INCONSISTENCY (governance)**: the rule that 9 calculation leaves rest on is unsigned, and it contradicts a signed line that the record says "stands".
   - That signed line is item (5) of `[calculator + subject_calculation restructure]`. The rule is T2's provenance rule.
   - The same amendment still says item (3), `runtime_environment`, stands, but item 53 deleted that class.
   - Separately, a signed end state (`jrclust_clusters` → `count_observation`) was revised by an unsigned decision (finding 18).
4. **INCONSISTENCY (T14)**: `tuning_curve_calculation.model_fit.coefficients` is a `structure` with no declared fields. That is the exact defect item 66 cited to drop `goodness` elsewhere. The leaf's `model_fit` field also shares its name with the new `model_fit` class but not its shape (finding 3).
5. **STALE-DOC (T15)**: the T15 vocabulary appendix in the tenets still lists edges and classes that items 56, 57, 60, 65 and 67 removed. Five persist-class doc strings still cite pre-T15 edge names: `presented_id_k`, `relative_to` ×3, `derived_from` (findings 10–11).

**Clean checks (evidence in the sections below):**
- **T15 edges.** No `_#` name on any V_eta-authored class. Every V_eta repeated edge declares `ordered`. `min_count` / `max_count` appear only beside `multiple` (item 54).
- **T13 booleans.** No `is_` / `has_` boolean on a V_eta-authored class. Case is clean.
- **Bindings.** Every `binding.values` member is `{node, name}` (item 64).
- **Chains.** No persist class inherits a retired class.
- **Mechanical doc pass.** 0 unresolved tokens.

## Per-leaf table

Columns:
- **dir × type**: the leaf's two parents.
- **who needs it**: string-literal hits, then `V_eta_migration_targets.json` lists.
  - "targets" is GENERATED from the call graph; "decided" is authored.
  - The first three files are named.
- **governance (mechanical)**: whether the leaf's name appears in the paragraph of an accepted `TEAM-SIGN-OFF` line.
  - If not, "#73 record only" means the name appears in the unsigned #73 decision record.
  - "no record found" means neither.
  - Rows marked † were classified by hand, taken from the previous audit and re-checked here.

| leaf | tier | dir × type | who needs it (evidence) | governance (mechanical) |
|---|---|---|---|---|
| `acceleration_observation` | stable | observation × acceleration | DID 4 lit (jRecordingModality.m, ontology_table_row.m, resolveEpochProbemap.m) / targets: ontology_table_row | no record found (emitted under the signed `<modality>_observation` pattern, recording_observation_plan.md:99) |
| `area_calculation` | draft | calculation × area | no literal writer / decided: spatial_gene_expression_cells | #73 record only |
| `concentration_observation` | stable | observation × concentration | DID 8 lit (ontology_table_row.m, resolveLawnPlateSubjects.m) / targets: ontology_table_row | no record found |
| `contrast_sensitivity_calculation` | stable | calculation × contrast_sensitivity | DID 1 lit (contrast_sensitivity_calc.m:19) / targets: contrast_sensitivity_calc | no record found (item 66 decides its composite; unsigned) |
| `contrast_tuning_calculation` | stable | tuning_curve_calculation (family leaf) | no literal writer; migrators emit `{'tuning_curve_calculation','contrast_tuning'}` (contrast_tuning_calc.m:18) / decided: contrast_tuning, contrast_tuning_calc | † signed as `contrasttuning_calc` (tuning_model_plan.md:144), renamed by an unsigned #73 amendment |
| `count_calculation` | draft | calculation × count | no literal writer / decided: spatial_gene_expression_cells, _pyramid | #73 record only |
| `count_observation` | stable | observation × count | DID 3 lit (jSorterOutput.m, jrclust_clusters.m, ontology_table_row.m) / targets: jrclust/kiasort/kilosort_clusters, ontology_table_row / decided: spatial_gene_expression_pyramid | † signed via go_forward_class_audit.md:710 table + :717 line (sorters); sorter use revised unsigned to `label_calculation` |
| `current_observation` | stable | observation × current | DID 5 lit (jRecordingModality.m, ontology_table_row.m, resolveEpochProbemap.m) / targets: ontology_table_row | no record found (recording pattern, as above) |
| `date_assertion` | stable | assertion × date | DID 1 lit (ontology_table_row.m:758) / targets: ontology_table_row | no record found |
| `dose_manipulation` | stable | manipulation × dose | DID 4 lit (resolveDeferredBaths.m, treatment_drug.m, virus_injection.m); NDI 1 (stimulusBathToBath.m:206) / targets+decided: treatment, treatment_drug, virus_injection / second_pass: stimulus_bath | sign-off para: OPEN_WORK.md:2969, go_forward_class_audit.md:719 |
| `frequency_observation` | stable | observation × frequency | DID 3 lit (ontology_table_row.m:682 live; jDecomposeScalars.m dead per item 50; jTuningFold.m) / targets: ontology_table_row | no record found |
| `harmonic_component_calculation` | draft | calculation × harmonic_component | DID 3 lit, all READERS (epochMint.m:1219, resolveResponseParameters.m:241); the migrator is a passthrough (stimulus_response_scalar.m:3-7) / decided: stimulus_response_scalar | sign-off para: stimulus_response_model_plan.md:541 (deleted by #67, restored by item 37, unsigned) |
| `intensity_observation` | stable | observation × intensity | DID 8 lit (resolveLawnPlateSubjects.m, ontology_table_row.m, jTuningFold.m) / targets: ontology_table_row / decided: image, image_stack, ontology_image, daqreader_image_epochdata_ingested | #73 record only |
| `label_calculation` | draft | calculation × label | no literal writer / decided: cell_type_labels, image, image_stack, jrclust/kiasort/kilosort_clusters, neuron_extracellular, spatial_gene_expression_cells | #73 record only |
| `length_observation` | stable | observation × length | DID 6 lit (probe_geometry.m, ontology_table_row.m, resolveLawnPlateSubjects.m) / targets: measurement, ontology_table_row, probe_geometry | #73 record only |
| `mass_observation` | stable | observation × mass | DID 1 lit (ontology_table_row.m:676) + runtime `[leaf '_observation']` (jMeasurementFold.m:82) / targets: measurement, ontology_table_row | no record found |
| `model_fit_calculation` | stable | calculation × model_fit | no literal writer / decided: fitcurve | #73 record only (item 68) |
| `orientation_direction_tuning_calculation` | stable | tuning_curve_calculation (family leaf) | no literal writer (oridirtuning_calc.m:22 emits the old pair) / decided: oridirtuning_calc, orientation_direction_tuning | † signed as `oridirtuning_calc`, renamed unsigned |
| `position_calculation` | draft | calculation × position | no literal writer / decided: spatial_gene_expression_cells | #73 record only |
| `position_observation` | draft | observation × position | no literal writer / decided: probe_geometry | #73 record only |
| `pressure_observation` | stable | observation × pressure | DID 1 lit (ontology_table_row.m:704) / targets: ontology_table_row | no record found |
| `receptive_field_calculation` | stable | calculation × receptive_field | DID 1 lit (hartley_calc.m:296) / targets: hartley_calc | sign-off para: ngrid_family_findings.md:358, :381 |
| `score_calculation` | draft | calculation × score | no literal writer / decided: neuron_extracellular | #73 record only |
| `score_observation` | stable | observation × score | DID 9 lit (vmspikefit.m:99, fitcurve.m:105, resolveLawnPlateSubjects.m:1128, …) / targets: fitcurve, neuron_extracellular, ontology_table_row, vmspikefit | #73 record only |
| `spatial_frequency_tuning_calculation` | stable | tuning_curve_calculation (family leaf) | no literal writer / decided: spatial_frequency_tuning, _calc | † signed as `spatial_frequency_tuning_calc`, renamed unsigned |
| `speed_tuning_calculation` | stable | tuning_curve_calculation (family leaf) | no literal writer / decided: speed_tuning, _calc | † signed as `speedtuning_calc`, renamed unsigned |
| `temperature_manipulation` | stable | manipulation × temperature | DID 3 lit (treatment.m in migrators_e/_i/_j) / targets+decided: treatment | † signed via go_forward_class_audit.md:709 table + :717 line |
| `temperature_observation` | stable | observation × temperature | DID 3 lit (jRecordingModality.m, ontology_table_row.m, resolveEpochProbemap.m) / targets: measurement, ontology_table_row | no record found (recording pattern) |
| `temporal_frequency_tuning_calculation` | stable | tuning_curve_calculation (family leaf) | no literal writer / decided: temporal_frequency_tuning, _calc | † signed as `temporal_frequency_tuning_calc`, renamed unsigned |
| `term_assertion` | stable | assertion × term | DID 5 lit (element.m, openminds_element.m, probe_geometry.m, …); NDI 9 (subjectStrainAssembly.m, +vintage/…) / targets: element, ontology_table_row, openminds_* , probe_geometry / second_pass: treatment family | sign-off para: openminds_family_record.md:10, :20 |
| `term_calculation` | draft | calculation × term | no literal writer / decided: cell_type_labels | #73 record only |
| `term_manipulation` | stable | manipulation × term | DID 3 lit (resolveEpochProbemap.m:696, treatment.m, treatment_transfer.m) / targets: treatment, treatment_transfer / decided: treatment | † signed via go_forward_class_audit.md:709 table + :717 line |
| `term_observation` | stable | observation × term | DID 10 lit (foldGenericFiles.m, jMeasurementFold.m, ontology_image.m, …); NDI 3 (ontologyLabelSubjects.m, pathSPromotion.m) / targets: 9 sources / decided: ontology_image, treatment family | sign-off para: OPEN_WORK.md:2969, go_forward_class_audit.md:719 |
| `time_observation` | stable | observation × time | DID 3 lit (jRecordingModality.m, ontology_table_row.m, resolveEpochProbemap.m) / decided + second_pass: valid_interval | sign-off para: ensemble_plan.md:218, logical_observation_plan.md:425, tenet_audit.md:520 |
| `timed_sequence_manipulation` | draft | manipulation × timed_sequence | NDI 2 lit (stimulusPresentationToTimedSequence.m:603, :731) / second_pass: stimulus_presentation | sign-off para: stimulus_model_plan.md:232, :278 (edge rename to `value_id` unsigned, item 30) |
| `tuning_curve_calculation` | stable | calculation × tuning_curve | DID 12 lit (the 12 tuning migrators) / decided: stimulus_tuningcurve, tuningcurve_calc | sign-off para: tuning_model_plan.md:144 (made concrete by the unsigned #73 amendment) |
| `velocity_observation` | stable | observation × velocity | DID 4 lit (ontology_table_row.m:222-224) / targets: ontology_table_row | no record found |
| `voltage_calculation` | draft | calculation × voltage | no literal writer / decided: neuron_extracellular | #73 record only (item 48) |
| `voltage_observation` | stable | observation × voltage | DID 13 lit (resolveEpochProbemap.m, electrode_offset_voltage.m, jRecordingModality.m, …) / targets: electrode_offset_voltage, neuron_extracellular, ontology_table_row, pyraview | sign-off para: recording_observation_plan.md:106 |
| `volume_observation` | stable | observation × volume | DID 3 lit (ontology_table_row.m, resolveLawnPlateSubjects.m) / targets: ontology_table_row | no record found |

**Governance tally for the 40 leaves:**
- 11 appear in a sign-off paragraph.
- 3 more (†) are signed through a table that a sign-off line points to.
- 5 (†) were signed under their #67 names and renamed without a signature.
- 10 have only the unsigned #73 record.
- 11 have no record found.

## Findings

### A. The leaves (T2, T3, T14)

1. **VIOLATION (T2) — `vmspikefit` → `score_observation`, a calculation routed as an observation, with no decision covering it.**
   - Its generated targets are `V_eta_migration_targets.json` `/classes/vmspikefit/targets = ["score_observation", "session_relative_reference", "software"]`, with how "r_squared -> a goodness-of-fit score_observation".
   - The emitter is `DID-matlab …/+migrators_j/vmspikefit.m:99`, `classBlock('score_observation', {'subject_observation', 'score'})`.
   - The v1 template is `V_eta_ndi_ground_truth.json` `classes.vmspikefit`, with deps `['fit_input_id', 'element_id']`. Its fields are `fit_constraints, fit_equation, fit_name, fit_parameter_names, fit_parameters, fit_sse, fit_sse_perpoint`, the `fitcurve` field set.
   - T2 says "A statement whose inputs are other statements in the dataset is a `subject_calculation`". Item 68 routes `fitcurve`, with the same fields, to `model_fit_calculation`.
   - `vmspikefit` has no `decided_targets`. Items 48 and 68 fixed its two siblings and missed it.
   - *Suggestion:* put `vmspikefit` on the team list next to item 68 (a `model_fit_calculation` with `input_id` → `fit_input_id`).

2. **QUESTION (T2) — two emitters produce observations from values probably computed from data already in the dataset.**
   - (a) `resolveLawnPlateSubjects.m:1119-1133` maps the E. coli patch radius → `length_observation`, circularity → `score_observation`, and six fluorescence measures → `intensity_observation`.
     - JH also carries 4,563 `image_stack` documents; that count is from the corpus census and was not re-measured here.
     - Whether these measures were computed from those images decides observation vs calculation.
   - (b) `pyraview` → `voltage_observation` (targets). A pyraview is a decimated copy of a stored recording.
     - Item 29 treats zoom levels as `redundant` bodies of the one observation, not as a separate statement.
   - I found no recorded provenance reasoning for either.
   - *Suggestion:* record where each input comes from, then apply T2.

3. **INCONSISTENCY (T14) — `tuning_curve_calculation.model_fit.coefficients` declares no fields, and the leaf's `model_fit` field diverges from the `model_fit` class of the same name.**
   - The built field is `stable/tuning_curve_calculation.json` `fields[model_fit].fields[coefficients]`: `type: structure`, no `fields`, doc "The fit coefficients (named, per the `model`)".
   - Item 66 dropped `contrast_sensitivity`'s `model_fit[].goodness` because it was "a structure with no fields (T14)" (`V_eta_spatial_transcriptomics_plan.md:460`).
   - Item 68 says "Tuning keeps its named `coefficients` structure", but nothing names them.
   - The same leaf's `model_fit.model` is doc'd "a controlled term (T8)", while the class `model_fit.value.model` is "a term for a named model …, otherwise a label".
   - Two shapes now share the name `model_fit`. Item 68 synchronises only `goodness` and `sampled_fit`; those two match field-for-field (r2, sse; independent_values, response).
   - *Suggestion:* either declare the coefficient entries (the `{variable, value}` list `model_fit` uses), or record why tuning's stay undeclared.

4. **INCONSISTENCY — `model_fit` and `model_fit_calculation` were built in `stable/`, while every other #73-minted leaf is `draft/`.**
   - `tools/build_v_eta.py:3731` and `:3742` call `write("stable", "model_fit" …)` and `write("stable", "model_fit_calculation" …)`.
   - The other #73 leaves and composites are in `draft`: `area_`, `count_`, `label_`, `position_`, `score_`, `term_` and `voltage_calculation`, `position_observation`, `label`, `position`, `product`, `spatial_frequency` (`index.json` `tier`).
   - All were decided in the same unsigned review (item 68, 2026-09-29), and I found no recorded reason for the difference.
   - *Suggestion:* move them to draft, or record why they are stable.

5. **INCONSISTENCY (known, PR #76 checklist) — the emitters still write classes the tree no longer has, and the 5 tuning family leaves have no writer.**
   - This comes from the literal sweep over DID-matlab `+migrators_j`, the batch passes and NDI `src`, looking for leaf-shaped names that are not in the tree:
     - `image_observation`: resolveEpochProbemap.m:952, ontology_image.m:301, image_stack.m:288.
     - `count_assertion`: neuron_extracellular.m:369.
     - `logical_observation`: resolveValidIntervals.m:1018, a dormant path.
     - `visual_grating_manipulation`: NDI stimulusPresentationToManipulation.m:81.
   - The generated `targets` still list `session_relative_reference` (37 rows), `runtime_environment` (14 rows), `relative_reference` (4), `epoch_bounded_reference` and `session_bounded_reference`.
   - The 12 tuning migrators emit `{'tuning_curve_calculation', '<marker>'}` (for example `oridirtuning_calc.m:22`). The markers were deleted in #73, so the 5 family leaves are needed only by decision.
   - Not new: the build acknowledges this at `tools/build_v_eta.py` (the `_DELETE_NO_V1_PROVENANCE` comment: "PR #76 DID-matlab checklist").
   - *Suggestion:* none beyond the existing PR #76 checklist. It is listed so the Bar-2 reading does not assume these leaves are emitted.

6. **STALE-DOC — the `stimulus_response_scalar` row in `V_eta_migration_targets.json` contradicts itself and the migrator.**
   - The row's `flags` say "BUILT (migrators_j/stimulus_response_scalar.m:209): folds via … into `harmonic_component_calculation` … TARGET SUPERSEDED per issue #67 -- pending new signed target".
   - The same row's `how` says "RESTORED TARGET (#73 review … item 37) … The migrator is a guarded passthrough today (PR #68)".
   - The migrator header agrees with `how`: "CONVERTED TO A GUARDED PASSTHROUGH in PR #68" (`stimulus_response_scalar.m:2-7`).
   - *Suggestion:* rewrite `flags` to match `how`.

7. **STALE-DOC — `V_eta_migration_targets.json` `/classes/app/how` still says "Run-specific os/interpreter details move to `execution_environment` on the interaction".** Item 53 dropped `execution_environment` and moved os and interpreter to `subject_calculation.interpreter_id` / `operating_system_id`. *Suggestion:* repoint the sentence to item 53.

8. **STALE-DOC — `term_assertion` edge `strain_id` argues from a count and a convention that no longer hold.**
   - Its doc reads "Named for its target per the convention measured across 97 dependency declarations (45 distinct names, all `<target>_id`)".
   - The tree now has 148 declarations and 72 distinct names.
   - T15 names an edge "for its role when the target is generic", as `input_id`, `owner_id`, `value_id` and `instrument_id` do, so "all `<target>_id`" is no longer the rule.
   - The edge name itself is still correct under T15.
   - *Suggestion:* cite T15 instead of the count.

9. **STALE-DOC — both files under `schemas/V_eta/examples/` are instances of classes the tree does not define.**
   - `scalar_temperature_observation_series.json` has `class_name: scalar_temperature_observation` ⊂ `[scalar_observation, scalar_temperature]`; none of the three exists. The leaf is now `temperature_observation`.
   - `utc_reference_grid.json` has class `utc_reference`.
   - Half known: the `utc` one is recorded as a residue at `tools/build_v_eta.py:10652`, but the temperature one is not.
   - *Suggestion:* replace or delete both when `schemas/` edits are authorised.

### B. Edges (T15)

10. **STALE-DOC — the T15 vocabulary appendix (`V_eta_tenets.md`, "The vocabulary") no longer matches the tree.**
    - Checked against every edge name in the built tree.
    - "16 names are unchanged" includes three names that no longer exist:
      - `session_id`: no class declares it. Item 57 dropped it.
      - `acquisition_metadata_reader_id`: now `epoch_parameter_reader_id` on `acquisition_system` (item 65).
      - `runtime_environment_id` is named as removed, which is correct.
    - The table rows are stale in four places:
      - `control_designation` still has two rows; the class was deleted (item 67).
      - `key_labels_id` is attributed to `subject_statement, data_body`; it is declared on `data` only (items 60 and 65).
      - The `acquisition_system` row reads `acquisition_metadata_reader_#` → `acquisition_metadata_reader_id`.
      - `acquisition_channels_id` is listed only on `clock_alignment_configuration`, but `subject_interaction` also declares it (item 56).
    - Edges missing from the vocabulary: `ingredient_id` (repeated, `ordered: true`), `formulation_id`, `product_id`, `vendor_id`, `epoch_parameter_reader_id`.
    - *Suggestion:* regenerate the appendix from the built edges rather than keep it by hand.

11. **STALE-DOC — five doc strings on persist classes still cite pre-T15 edge names.**
    - `draft/timed_sequence.json` `value.presentation_order`: "a 0-based index naming a `item_id` edge directly (value k -> `presented_id_k`)".
    - `draft/coordinate_system.json` `origin`: "WHICH point on `relative_to` is zero". The edge is `referent_id`.
    - `relative_time_reference` `value`, `value.start` and `value.clock` each say "the referent named by `relative_to`" or "what `relative_to` already says".
    - `stable/subject_calculation.json` edge `software_id`: "Distinct from … `derived_from` (the input data)". The edge is `input_id`.
    - *Suggestion:* a find-and-replace pass in `build_v_eta.py`.

    Clean:
    - All 16 repeated edges were checked. The 13 on V_eta classes all declare `ordered`.
    - The 3 without `ordered` are did_v1 families on `in_progress` v1 tombstones (`daqsystem.daqmetadatareader_id_#`, `ensemble.neuron_id_#`, `syncgraph.syncrule_id_#`), which T15 exempts.
    - No V_eta-authored edge fails to end `_id`. The only failures are `gene_list_mapping.gene_list_id_a/_b`, a retired tombstone; see finding 14.
    - No `min_count` / `max_count` appears without `multiple` (item 54).
    - No persist-class edge targets a retired class.

### C. Names (T13)

12. **QUESTION — `epoch_parameter_reader` (item 65) carries `parameter`, which T13 lists as a container word.**
    - T13: "Drop altitude-noise wrapper words — `parameters`, `data`, `info` …".
    - Item 65 replaced `metadata` with `parameter` and gives the reason "the name says what it reads, the epoch's parameters". T13 itself endorses only `method_parameters` (as a role).
    - The class name and its edge `acquisition_system.epoch_parameter_reader_id` are the only V_eta-authored names with a container word outside the T13/item-65 exemptions. Those exemptions are the spine `data` / `data_type` / `data_body` and `method_parameters`.
    - *Suggestion:* record in item 65 why `parameter` is content here.

13. **INCONSISTENCY — `acquisition_epoch` (V_eta-authored, `in_progress`) carries a drifted private copy of the keyed-array block, plus names and references that no longer exist.**
    - `storage.data_type` is named with a container word, and it collides with the class `data_type` and with item 15's rename "`dtype` is `datum_type`". `storage.data_limits` also carries a container word.
    - Its own `keys` and `complete` duplicate `data.keys` / `data.complete` (item 65). The `keys` copy has drifted:
      - `keys.chunk` still says "a missing member is an empty chunk", which L2 / item 58 removed.
      - `keys.labels_from` names a `key_labels_id` entry, but `acquisition_epoch` declares no such edge; its only edge is `element_id`.
    - `channels` says "Channel meaning lives in a dataseries_channel_map sidecar". No such class exists; a grep of `schemas/V_eta/*/*.json` finds the name only in this file and in `topics.json`.
    - The class is `in_progress` ("⑦ infra tier re-opened"), so this is a record of state, not a demand.
    - *Suggestion:* when the epoch family is re-walked, derive `acquisition_epoch` from `data` or drop the copy.

    Clean:
    - No boolean on a V_eta-authored class uses `is_` / `has_`: 82 boolean fields checked on non-retired classes. The one hit is `daqreader_image_epochdata_ingested.metadata.israster`, a v1 tombstone field, exempt under T13.
    - No field or edge on a non-retired class contains upper case.

### D. Bindings (T8, item 64)

All 12 bound fields, with their strength:

| class | field | strength | members |
|---|---|---|---|
| `clock_alignment_configuration` | `clock` | required | 4, all `{node,name}` (4 with empty node, staged) |
| `dataset` | `accessibility` | required | term_set (no `values`) |
| `dataset` | `ethics_assessment` | required | term_set |
| `dataset` | `experimental_approach` | preferred | term_set |
| `frequency_filter` | `algorithm` | required | 6, all `{node,name}` (6 staged) |
| `frequency_filter` | `band` | required | 4, all `{node,name}` (4 staged) |
| `interaction_purpose` (in_progress) | `purpose` | preferred | `node_form: curie`, no set |
| `relative_time_reference` | `value.relation` | required | 13, all `{node,name}`, all with a `time:` node |
| `relative_time_reference` | `value.clock` | required | 4, all `{node,name}` (4 staged) |
| `subject_interaction` | `method` | preferred | `node_form: curie` |
| `subject_statement` | `variable` | preferred | `node_form: curie` |
| `term` | `value` | required | `keyed_by` variable, no set |

**Item 64 holds.** All 31 enumerated members are `{node, name}` objects, and no bare strings remain. 18 of the 31 have an empty node and match by name, which item 64 allows. `keys.unit` is unbound (OPEN_ITEMS 24, blocked on the unit vocabulary) and is not re-reported. No finding.

### E. Superclass chains

14. **VIOLATION (T13 tombstone rule; item 18) — the retired spatial "tombstones" are not the v1 shape. `spatial_gene_expression_pyramid` inherits the V_eta spine.**
    - The pyramid tombstone (`stable/spatial_gene_expression_pyramid.json`) is ⊂ `[base, gene_expression, subject_observation]` and REQUIRES edge `gene_list_id`.
    - The v1 template is ⊂ `[base, geneExpression]`, with deps `subject_id` and `geneList_id` (`V_eta_ndi_ground_truth.json` `classes.spatialGeneExpressionPyramid`).
    - The same snake_casing of REQUIRED v1 edges appears on three more tombstones:
      - `spatial_gene_expression_cells.spatial_gene_expression_pyramid_id` (v1 `spatialGeneExpressionPyramid_id`);
      - `spatial_gene_expression_tiles.spatial_gene_expression_pyramid_id` (v1 `spatialGeneExpressionPyramid_id`);
      - `gene_list_mapping.gene_list_id_a` / `_b` (v1 `geneList_id_a` / `_b`).
    - It also appears on one OPTIONAL edge: `ontology_image.ontology_table_row_id` (v1 `ontologyTableRow_id`).
    - Edge names are not renamed on the way through: `universalRenames.m:628` has `skip = {'document_class','depends_on','file','files'}`.
    - The validator enforces the superclass chain exactly (`did2.schema.cache.validateDocument`, "must equal the chain derived from the schema files"). Required edges are enforced by #37, which is armed by default (`cache.m:924`).
    - So an unmigrated v1 document of any of these classes cannot validate against its own tombstone.
    - T13 says a did_v1 tombstone "must keep the v1 writer's spelling verbatim so a passthrough still validates". Item 18 says the eight classes "stand as retired tombstones".
    - The DID-matlab migrators write into these copies (`spatial_gene_expression_pyramid.m:4`, "⊂ [base, gene_expression, subject_observation]"), so migrated documents are unaffected. Only a passthrough is at risk.
    - *Suggestion:* restate the eight tombstones from the v1 writer, as `hartley_calc` was in d78f2fa.

15. **STALE-DOC — `hartley_calc`'s chain in the decision record disagrees with the build.**
    - Item 43 (`V_eta_spatial_transcriptomics_plan.md:194`) says "`hartley_calc` ⊂ [`base`, `hartley_reverse_correlation`]", and so does `V_eta_subject_calculation_plan.md:315`.
    - The build has `stable/hartley_calc.json` superclasses `['calculator', 'hartley_reverse_correlation']`, restated from the writer in `d78f2fa`.
    - The change is recorded only in `review/73/OPEN_ITEMS.md` ("To verify … CHECKED AND FIXED").
    - *Suggestion:* amend item 43 with one line.

16. **QUESTION — 13 v1 infra tombstones are `in_progress` with the note "⑦ infra tier re-opened: the KEEP predated T11/T13 scrutiny", although their V_eta successors are signed and built.**
    - The classes are `daqsystem`, `daqreader`, `daqmetadatareader`, `filenavigator`, `syncgraph`, `syncrule`, `syncrule_mapping`, `epochfiles_ingested`, `epochid`, `filter` and the three `*_epochdata_ingested` classes (`index.json` `disposition_note`).
    - Their families are signed on the board: `daq configuration`, `sync configuration`, `sync mapping`, `file navigation`, `epoch`, `frequency_filter`, `daq ingested payloads`.
    - `syncrule_mapping`'s nested `epochnode_a/_b.time_reference` doc also names `epoch_bounded_reference`, which #65 increment 3b deleted.
    - *Suggestion:* confirm whether `in_progress` still means something for these, or whether they should read `retire`.

    Clean: no persist class inherits a retired class (211 chains walked). `spatial_gene_expression_pyramid` is the only retired class whose chain includes a V_eta-only class (finding 14).

### F. Duplicate declarations

17. **QUESTION — `subject_calculation` redeclares the inherited `software_id` edge in order to tighten it, and no gate governs edge redeclaration.**
    - The doc says it "Redeclares -- and TIGHTENS to required -- the optional `software_id` every subject_interaction carries".
    - `OPEN_ITEMS.md` item 3 proposed "a declared, gated rule 'a subclass may tighten an inherited edge to required'; any other redeclaration fails".
    - `tools/check_duplicate_field_declarations.py` covers fields only.
    - `grep -rn -i tighten tests/*.py` finds no edge rule.
    - *Suggestion:* decide the proposed rule.

    Recorded, not findings:
    - The 10 persist `name` fields beside `base.name` are decided (item 54). The checker lists them as `V1-ONLY-SLOT … [OVERRIDE]`, and its V_eta-SHADOW and NOT-DERIVABLE buckets are both 0.
    - The retired and v1 duplicates are v1 fidelity: `hartley_calc` edges `element_id` and `stimulus_presentation_id` vs `reverse_correlation`; `image_stack.document_id`; `pyraview.label`; `daqreader_image_epochdata_ingested.daqreader_id`.

### G. Governance

18. **INCONSISTENCY (governance) — the calculation leaves rest on an unsigned rule that contradicts a signed line the record still says "stands", and one signed end state was revised without a signature.**
    - `TEAM-SIGN-OFF [calculator + subject_calculation restructure]` (`V_eta_subject_calculation_plan.md:270`) item (5) says: "`_calculation` suffix reserved for calculator outputs".
    - The #73 amendment says "items (3)–(5) stand" (`:289-290`). But:
      - item (3), the `runtime_environment` entity, was deleted by item 53;
      - item (5) is replaced by the provenance rule in the next amendment (`:322-`) and in T2, which also still says `derived_from_#`.
    - Leaves justified only by the provenance rule: `area_`, `count_`, `label_`, `position_`, `score_`, `term_`, `voltage_` and `model_fit_calculation`, plus `harmonic_component_calculation` (item 37, "Rule C decides by provenance").
    - `TEAM-SIGN-OFF [confirm sheet 2026-08-17]` (`V_eta_go_forward_class_audit.md:717`) signs `jrclust_clusters` → `count_observation` "IS the intended end state". The unsigned #73 decision retargets it to `label_calculation` (`migration_targets` `jrclust_clusters.decided_targets`).
    - `[confirm sheet 2026-08-22]` (`:719`) names `session_relative_reference`, which #65 increment 3b deleted.
    - *Suggestion:* put the provenance rule, the item (3) reversal and the sorter retarget on the team's sign-off list together.

19. **QUESTION — 26 of the 129 persist classes have no decision record by the mechanical test, 11 of them leaves.**
    - The test: the name appears in no accepted sign-off paragraph and nowhere in the #73 record.
    - The classes: `acceleration_observation`, `concentration_observation`, `current_observation`, `frequency_observation`, `mass_observation`, `pressure_observation`, `temperature_observation`, `velocity_observation`, `volume_observation`, `date_assertion`, `contrast_sensitivity_calculation`; the composites `capacitance`, `conductance`, `current`, `energy`, `force`, `intensity`, `power`, `resistance`; `subject_assertion`; and the 4 tuning family leaves, which are signed under old names (see the table).
    - Across all 129 persist classes: 62 are named in an accepted sign-off paragraph, 41 only in the unsigned #73 record, 26 in neither.
    - The test cannot see a class signed through a table or under an old name, and it counts incidental mentions. The previous audit's hand table remains the finer instrument.
    - Absence of a record is not evidence that nothing was decided: many of these predate the sign-off convention.
    - *Suggestion:* a batch confirmation of the dimensioned-quantity family would close most of the 26.

20. **STALE-DOC — T2 and the tenet audit still describe superseded structure.**
    - T2 (`V_eta_tenets.md:42-44`) says an interaction "adds `method` (the verb), its per-reading positions as `keys` …".
      - `keys` is declared on `data` (item 65).
      - `subject_interaction` declares `method` and `method_parameters` and the edges `time_reference_id`, `instrument_id`, `software_id`, `method_parameters_id`, `acquisition_channels_id`.
    - `V_eta_tenet_audit.md:120` still lists deleted classes as conformant leaves: `numeric_assertion`, `visual_grating_manipulation` (item 50) and `image_observation`.
    - *Suggestion:* correct both in the next prose pass.

## Mechanical pass over the 40 leaves' documentation

**Denominator.**
- 40 leaves, 56 documentation strings. The class-level doc, every edge doc and every nested field doc were read.
- Only 6 leaves carry any doc of their own: `term_assertion` and the 6 tuning leaves (`speed_tuning_calculation` carries none).
- 35 tokens were extracted, 21 distinct: backticked identifiers, `word_id`, and `word.word`.
- Each was resolved against 211 class names, every declared field name at any depth, every edge name, and `class.path` forms.

**Result.**
- 3 tokens resolve directly to V_eta field names: `model` (twice) and `r2`.
- 30 are did_v1 source-field names, each introduced by "v1 `…`". All 17 distinct ones exist as fields in the v1-shaped copies of the vhlab tuning classes under `schemas/V_delta/stable/*tuning*.json`: `fitless, l50, h50, pref, interpolated_c50, vector, hotelling2test, direction_hotelling2test, dot_direction_significance, r_squared, hwhh, orientation_angle_preference, direction_angle_preference, priebe_fit_speed_tuning_index, priebe_fit_spatial_frequency_preference, priebe_fit_temporal_frequency_preference, priebe_fit_nested_f_test_p_value` (the v1 `r2` also exists there).
  - These classes have no NDI template, so V_delta is the in-tree v1 record.
  - Judged correct provenance.
- 2 are in `term_assertion.strain_id`: `<target>_id`, a naming pattern, and `term_id`, a name mentioned as rejected. Both are judged fine, but the sentence around them is stale (finding 8).
- **Unresolved tokens naming something that does not exist: 0.**

**Wider sweep, all non-retired classes.** 998 doc strings; backticked tokens only. It surfaced the stale names in findings 11, 13 and 16. Its other misses were v1 names quoted as provenance or code identifiers, judged fine.

## Previous audit (audit_C_leaves_governance.md, 2026-09-25): status

| # | previous finding | status | evidence |
|---|---|---|---|
| 1 | `reverse_correlation` / `hartley_reverse_correlation` fieldless persist markers under `receptive_field` | FIXED | item 43; `index.json`: both `retire`, ⊂ `[base, ngrid]` / `[base, reverse_correlation]` |
| 2 | `image_observation.ontology_table_row_id` edge to a retiring class | MOOT | item 42 dropped the edge; item 51 retired `image_observation` (no file in the tree) |
| 3 | `migration_targets` routes the stimulus second pass to `visual_grating_manipulation` | FIXED | `/classes/stimulus_presentation/second_pass = [timed_sequence_manipulation, timed_sequence, visual_grating, sampled_body]` |
| 4 | `"duration_observation"` in `migration_targets` | FIXED | `grep -c '"duration_observation"' schemas/V_eta_migration_targets.json` = 0 |
| 5 | `logical_observation` persists with no consumer | FIXED | item 52; no file in the tree |
| 6 | `voltage_`/`current_`/`force_`/`concentration_manipulation` with no warrant | FIXED | item 50; none of the four in `index.json` |
| 7 | `gain_assertion` / `gain_observation` with no warrant | FIXED | item 50; neither in `index.json` (the `gain` composite stays, per T3) |
| 8 | `fitcurve` / `neuron_extracellular` routed to observations (T2) | FIXED at decision level | `decided_targets`: `fitcurve` → `model_fit_calculation`; `neuron_extracellular` → `label_`/`score_`/`voltage_calculation` (items 48, 68). Generated `targets` still observations until PR #76. The sibling `vmspikefit` was missed (new finding 1) |
| 9a | T2 prose: `sample_time` cadence | FIXED | T2 now says "the `sample_time` block retired … built #73 item 21"; but see new finding 20 (keys) |
| 9b | T3 prose: `dtype`/`axes` on the body | FIXED | T3: "its `keys` live on the body, its `datum_type` on the statement" |
| 9c | `tenet_audit.md:120` lists `numeric_assertion` | STILL OPEN | line 120 unchanged (finding 20) |
| G1 | the board counts a quoted sign-off (`method_parameters_plan`) | FIXED | census rejects `V_eta_method_parameters_plan.md:694`, "inside a fenced code block" |
| G2 | the board counts the superseded spatial sign-off | FIXED | census rejects `V_eta_go_forward_class_audit.md:798`, "SUPERSEDED" |
| G3 | "182 persist; 97 with no record" | MOOT | the persist set is now 129 after items 50–53, 59, 61, 67 and 68. The re-measure is in finding 19 (a mechanical 26 with no record; the method differs from the old hand count) |
| clean-note | `visual_grating_manipulation` coexistence signed | MOOT | the class was deleted by item 50 |
