# #73 team sign-off sheet (prepared 2026-09-29, audit 2 D7c)

**This is a sheet of PROPOSALS, not signatures.** Claude writes no sign-off line (Operating
Rule 4). Each row below is independently signable: to sign one, a team member adds their own
sign-off line, in the house format, to the plan document named in the row. `tools/status_board.py`
reads only `schemas/*.md`, so nothing in this file counts toward any family.

Sources: `schemas/V_eta_spatial_transcriptomics_plan.md` (the #73 decision record, items 1-72)
and `review/73/audit2_SUMMARY.md` (the audit 2 decision log, D1-D13). Decider throughout: jess.

## A. Amendments to lines that ARE signed (sign these first: the signed text is now wrong)

| # | signed line | what changed | amended by | sign in |
|---|---|---|---|---|
| A1 | [subject calculation] #67: `_calculation` is reserved for calculator outputs | decided by provenance instead: inputs in the dataset => calculation (T2) | #73 item 3 (2026-09-23) | V_eta_subject_calculation_plan.md |
| A2 | [calculator] #67: `runtime_environment` "stands" | the run environment is two `software` edges, `interpreter_id` / `operating_system_id` | #73 item 53 | V_eta_subject_calculation_plan.md |
| A3 | 2026-08-17 confirm sheet: `jrclust_clusters` -> `count_observation` | -> `label_calculation` (spike-sorter output) | #73 item 35 | V_eta_go_forward_class_audit.md |
| A4 | 2026-08-22 confirm sheet names `session_relative_reference` | that class is deleted (#65 increment 3b); the target is `relative_time_reference` | #65 3b | V_eta_go_forward_class_audit.md |
| A5 | [tuning] `model_fit[].coefficients` a structure named per model | a NAMED list `{variable, value}`, shared with every fit; `goodness.sse_per_point` | audit 2 D2 | V_eta_tuning_model_plan.md (amendment appended) |
| A6 | [tuning] #67 `independent_variables[]` | dropped; the dimensions are the value's `keys` | audit 2 D3 | V_eta_tuning_model_plan.md (amendment appended) |
| A7 | [spike processing parameters] "no `unit` field" | the parameter entry carries a bound `unit` | audit 2 D4 | V_eta_method_parameters_plan.md (amendment appended) |
| A8 | [stimulus] onsets on a body owned by the manipulation | onsets are the sequence's own time key; `offset` field | audit 2 D11 | V_eta_stimulus_model_plan.md (amendment inline) |
| A9 | [pyraview pyramid] confirmed 2026-08-13: `voltage_observation` + `sampled_body` is the end state | the levels are `redundant` sampled bodies owned by the RECORDING's observation (second-pass join), not a second `voltage_observation` | audit 2 D7 | V_eta_recording_observation_plan.md; then move `confirmed_targets` -> `decided_targets` in V_eta_migration_targets.json |

Also open, carried from earlier: whether the time-reference signature (`V_eta_time_reference_model_plan.md:468`) reaches CHANGE 5 (the `value.clock` uniqueness rule, built).

## B. Unsigned #73 decisions (each row independently signable in V_eta_spatial_transcriptomics_plan.md)

| item | decision (headline as recorded) |
|---|---|
| 1 | Counts are a `count_observation` of the tissue section |
| 2 | Cells are a KEY, not subjects |
| 3 | Observation vs calculation is decided by provenance |
| 4 | `position` |
| 5 | `coordinate_system` (items 5-9): relative_to (now referent_id), origin, dimensions[], required on position |
| 10 | Time leaves say "time" |
| 11 | Boundaries |
| 12 | A key may take its positions from another document's rows |
| 13 | Every index is 0-based |
| 14 | `axes` → `keys` |
| 15 | No `values[]` column list |
| 16 | `image.value` = { keys, complete, pixels } |
| 17 | Many files per body is a DID file series |
| 18 | Nothing is carried forward |
| 19 | Every data type is concrete |
| 20 | A body's owner |
| 21 | The gene list is a standalone `term` document |
| 22 | Provenance of reference content |
| 23 | `gene_symbol_namespace` is dropped (the annotation it came from is recorded) |
| 24 | The gene-list mapping |
| 25 | An external file not held in the database |
| 26 | `geneExpression` dissolves |
| 27 | Cell type labels |
| 28 | The cell list |
| 29 | Zoom levels |
| 30 | `value_id` |
| 31 | `redundant` |
| 32 | The key's `values` field keeps its name |
| 33 | `label` — a term without a node |
| 34 | DID-matlab checks |
| 35 | Spike-sorter output |
| 36 | Edge families |
| 37 | `harmonic_component_calculation` is restored |
| 38 | `ngrid` is dropped from `reverse_correlation` |
| 39 | `ingestion_manifest` drops `epochprobemap` |
| 40 | `ingestion_manifest.filenavigator_id` → `epoch_file_pattern_id` |
| 41 | T15: edges are nouns ending `_id`, and a repeated edge repeats one name |
| 42 | `image_observation` drops `ontology_table_row_id` |
| 43 | The v1 receptive-field chain goes back to its pre-2026-09-21 shape; supersedes item 38 |
| 44 | `angle`'s canonical unit is DEGREES, everywhere |
| 45 | New type `spatial_frequency` |
| 46 | `score` gains `source_value` + `source_unit` |
| 47 | `angular_velocity`'s canonical unit is degrees per second |
| 48 | `neuron_extracellular` migrates to calculations |
| 49 | `fitcurve` is PARKED |
| 50 | Leaves exist only when needed |
| 51 | `image` and `image_observation` retire |
| 52 | `logical_observation` retires |
| 53 | The run environment is two pieces of software |
| 54 | Names live on the classes that have one; `base.name` is did_v1-only |
| 55 | `epoch.instrument_id` is dropped |
| 56 | Channel wiring is one shape: an `acquisition_channels` document |
| 57 | Small audit decisions |
| 58 | Bodies split by who lays out the bytes |
| 59 | Chemical, formulation, dose and product |
| 60 | A value's descriptors live with the value; `storage_mode` is deleted |
| 61 | `acquisition_metadata_file` retires; its bytes become a body |
| 62 | `method_parameters.other` is deleted |
| 63 | `clock_alignment_configuration` keeps WHAT, `method_parameters` takes HOW |
| 64 | Admissible-set members are `{node, name}` terms, one shape |
| 65 | Container words in infrastructure names |
| 66 | `contrast_sensitivity` against the tuning shape |
| 67 | Control trials are marked by the design, not by a designation document |
| 68 | `model_fit`: a fitted model as a value |
| 69 | `harmonic_component`'s control nests like tuning's |
| 70 | `clock_alignment` is a relation leaf |
| 71 | Single-value types hold lists |

### Audit 2 (2026-09-29), built together; record in `review/73/audit2_SUMMARY.md`

| decision | what was decided |
|---|---|
| D1 | Single-value types (`term`, `label`, `date`, `position`, `polynomial`) hold lists; `datum_type` gains `utf8`; a standalone term's binding is checked through the referencing key (built, item 71) |
| D2 | One fit entry shared by tuning, contrast sensitivity and `model_fit`: `model`, named `coefficients[]`, `goodness{r2, sse, sse_per_point}`, `sampled_fit`; Naka-Rushton coefficients named from fitindexes.m |
| D3 | Tuning / contrast state their stimulus dimensions as the value's `keys` (`independent_variables[]` dropped); 'another reading is a key, another statistic is a field' (T14); `response_unit` on every response type; `response_type` a bound term (mean, peak, F0, F1, F2); `modulated_response` dropped |
| D4 | The parameter entry gains a bound `unit` (entry = key / condition shape) at all three mounts |
| D5 | `relation` fields bound to the registry (generated values, preferred); registry drops `observes`, adds the gene mappings, statement / data-type endpoints, undirected `paired_with` / `same_as`; the binding meta-schema declares `root` / `source` and is closed; `channels.type` bound {ai, ao, di, do} |
| D6 | Declared: keys required on a sampled body, `byte_order` / `datum_order` / `hash_algorithm` enums, `format` required on an opaque body, `absolute_time_reference.value.start` required; per-class named `rules`; T6 amended for redundant bodies |
| D7 | `vmspikefit` -> `model_fit_calculation`; JH lawn-plate measures decided in the JH mapping; `pyraview` -> redundant sampled bodies owned by the recording's observation; this sheet |
| D8 | The eight spatial tombstones restated from the v1 templates (v1 chain, v1 edge names, required only where v1 requires); `ontology_image`'s `ontologyTableRow_id` spelling |
| D9 | `local_identifier` loses the copied id terms; `global_identifier.scheme` bound (and a term); `acquisition_system.name` required; `strain.product_id` replaces `stock_number`; `notes` on `subject_interaction` |
| D10 | One value-cell pattern (T14); `count.value` = {count, approximate}; `score.value.score`; pressure stays `mmhg` (revised); `date` = {instant, precision, source_value, approximate}; generated defaults |
| D11 | Receptive-field planes stated on each body; onsets are `timed_sequence`'s time key (+ `offset`); `control_item` authoritative, `blank` a stimulus property; `visual_grating.value.center` |
| D12 | `require_inherited` replaces edge redeclaration; loosening a required edge fails the build |
| D13 | Formulation: ingredients or product; `fill_value` a char literal; `demo` exempt from T6; `standalone_value` batch check; `acquisition_epoch` doc fixes; 12 infra tombstones retire; `parameter` is content; `model_fit` to draft; `file_regex`; nested flags declarative until DID-matlab descends |

## C. Persist classes with no decision record (26, by the mechanical test of audit 2 C19)

The test: the name appears in no accepted sign-off paragraph and nowhere in the #73 record. It
cannot see a class signed through a table or under an old name, and absence of a record is not
evidence nothing was decided (many predate the sign-off convention). Suggested as ONE batch
confirmation per group:

- **Dimensioned observations (9):** `acceleration_observation`, `concentration_observation`,
  `current_observation`, `frequency_observation`, `mass_observation`, `pressure_observation`,
  `temperature_observation`, `velocity_observation`, `volume_observation`.
- **Dimensioned composites (8):** `capacitance`, `conductance`, `current`, `energy`, `force`,
  `intensity`, `power`, `resistance`.
- **Other leaves (2):** `date_assertion`, `contrast_sensitivity_calculation`.
- **Spine (1):** `subject_assertion`.
- **Tuning family leaves (4), signed under their old names:** the renamed
  `*_tuning_calculation` leaves (#73, 2026-09-23); a signature naming the new names closes them.
- Finding 19 names the 24 above and not the other 2 of its 26. Re-run its test before signing,
  both to name them and because audit 2 itself changed the set (D13 (6) retired 12 infra
  tombstones; D13 (8) moved `model_fit` / `model_fit_calculation` to draft).
