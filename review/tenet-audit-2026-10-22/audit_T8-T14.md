# V_eta audit against tenets T8-T14 (did-schema #88)

Read-only. Nothing in /home/user/DID-schema was written. `git pull`: "Already up to date"; HEAD = origin/claude/ecstatic-pascal-md91fw = 701a5dec75ca8a3908a71df00e4673bb81ead409.
Dump of every class/field used for this audit: (session scratchpad) audit/dump.txt (made by dump.py in the same folder).

## D. Denominators (stated first)

- Class JSON files under `schemas/V_eta/{stable,draft}/`: **163**, plus 5 non-class meta files (CURIE_lookups_meta, binding_registry_meta, did_schema_meta, ndi_reserved_keys, term_registry_meta). Fields, nested sub-fields included: **1571**.
- Index dispositions of those 163 (index.json): stable persist 69, draft persist 17, stable in_progress 7, stable retire 70.
- **Live set audited field by field (persist + in_progress): 93 classes, 1172 fields.** The 70 `retire` classes are v1 source tombstones (T13 exempts their spelling). They were only grepped for stale names and are not reported as violations.
- Binding registry: 11 subject_statement_bindings, 34 relation_bindings, 1 entity_field_binding, 19 entity_type_bindings. Term registry: 508 terms, all `status: decided`.
- Plan decision lines read: V_eta_tenets.md (T3, T6, T8-T14, and the 3 TEAM-SIGN-OFF lines), data_body plan AMENDMENTS 1-6 with their Decided-by and TEAM-SIGN-OFF lines, source_unit plan (2 sign-offs), time_reference plan sign-offs, method plan (1 sign-off and 6 Decided-by lines), stimulus_response plan Decided-by lines 604-616.
- Not run: `tools/gates.py`. Findings come from the JSON and the plan text, not from validator output.

---

## A. VIOLATIONS (a tenet or a signed decision as written)

### HIGH

**A1. Calculator summary values have no declared unit (T14: "Every canonical slot names its complete unit ... never a unit implied by the field it sits in"; "Canonical units are PRACTICAL SI ... `degrees`").**
- `orientation_direction_tuning_calculation.circular_statistics.orientation_preference` / `.direction_preference` (double): "Same unit as the curve's direction variable."
- `tuning_curve_calculation.model_fit.metrics.orientation_preference` (double): "Orientation evoking the maximum response under the fit". No unit is stated at all. The same holds for `direction_preference`, `spatial_frequency_preference` and `temporal_frequency_preference`.
- `...metrics.preferred_value`, `half_maximum_below`, `half_maximum_above` and `half_width_at_half_maximum`: "Same unit as the curve's independent variable" / "direction variable".
- Effect: an angle or a frequency sits in a bare double whose unit is found only through another document's covariate `unit`. That covariate unit is itself unbound (A3). Nothing in the schema says these values are in degrees. No decision line exempts them.

**A2. The `matrix` documentation contradicts the signed AMENDMENT 4 correction.**
- AMENDMENT 4 (TEAM-SIGN-OFF [data_body amendment 4], 2026-10-21) says "row-major, every dimension written". Its text: "A flat `[a, b, c]` cannot say row or column ... so the writer never emits one ... (Corrected 2026-10-21 from "a vector is `[a, b, c]`")".
- Six files still carry the pre-correction text, "a vector is [a, b, c], an n x 3 palette is [[r, g, b], ...]": `statement.conditions.matrix`, `interaction.method.parameters.matrix`, `relation.method.parameters.matrix`, `method.parameters.matrix`, `clock_alignment_configuration.method.parameters.matrix` and `data_body.conditions.matrix` (found with `grep -rln "a vector is \[a, b, c\]"`).
- Effect: a writer that follows the field docs emits exactly the ambiguous form the amendment bans.

**A3. Entry `unit` slots are unbound, and nothing says which unit is canonical (T14 practical SI; T8).**
- `data.covariates.unit`, `statement.conditions.unit`, `data_body.conditions.unit`, every `method.parameters.unit` and `acquisition_epoch.covariates.unit` have `constraints: {}`. Their doc says only "Canonical unit of ... Angles are DEGREES ... PRACTICAL SI (V_gamma_SPEC.md)".
- The same entries' `source_unit` is `{"binding": {"strength": "preferred", "node_form": "curie"}}` (source_unit plan sign-off).
- T14 says the canonical list is "`_DIM_CANON` in `tools/build_v_eta.py`". That file is deleted (`ls tools/build_v_eta.py`: No such file), and `grep -rn _DIM_CANON tools/` finds nothing. `tools/validate_v_eta.py` and `veta_record.py` contain no "canonical unit", "practical", "degrees" or "radian" check.
- So nothing stops a covariate in `om:millimetre` or `om:radian` as its canonical `unit`. "One quantity has one canonical slot" is not enforceable for entries.
- Uncertain: AMENDMENT 1 (2026-08-14) says "the axis carries `unit` as a bound `ontology_term`", but in the same section it equates "bound" with "not free text" ("An `ontology_term` is not an escape hatch"). Read that way, being an ontology_term may be all it required.

### MEDIUM

**A4. `acquisition_epoch` (in_progress) breaks three 2026-10-22 decisions.**
- (a) [covariate details] 5.3a says "`acquisition_epoch` dimensions carry no `chunk`". Yet `acquisition_epoch.storage.chunk_shape` (matrix) is "Per-axis chunk sizes enabling partial/ROI reads".
- (b) [format is an ontology term] (2026-10-14, confirmed 2026-10-21) makes a format a bound term. Yet `storage.format` is char: "Physical encoding (vhsb | zarr | ome_ngff | ...)". This is also an enum written only in prose (T8, T14).
- (c) [epoch covariates] moves the epoch to `dimensions` + `covariates`. The class copies the entry, but `acquisition_epoch.json` has no `rules` key: `covariate_one_value_form`, `covariate_along`, `covariate_shape`, `covariate_cyclic` and `variable_once` are declared only on `data.json`. `covariates.document` is declared and documented "NOT USABLE HERE".
- The class also keeps a bytes file outside the two bodies (`file: epoch_binary_data.vhsb`, "until that lands ... the bytes stay here"). T6 records only one exemption, `demo`. The class doc acknowledges this, and its disposition is in_progress.

**A5. `clocks.name` is free text while every other clock slot is a required bound term (T8).**
- `acquisition_epoch.clocks.name` is char: "Clock identifier (e.g., 'dev_local_time', 'utc', 'exp_global_time')".
- `relative_time_reference.value.clock` and `clock_alignment_configuration.clock` are bound `did_clocktype`, `strength: required`, with four values.

**A6. Binding registry row targets a retired class.**
- `subject_statement_bindings` row `{"variable": {"node":"NCIT:C16608","name":"Gene Expression"}, "class": "spatial_gene_expression_pyramid", ...}`.
- index.json gives `spatial_gene_expression_pyramid` disposition `retire`. Since 2026-10-08 (T3 amendment) a statement's class is its direction. No decision line permits a binding on a tombstone.

**A7. Terms described as "controlled (T8)" carry no binding.**
- `tuning_curve_calculation.model_fit.model`: "The fitted model as a controlled term (T8): double_gaussian | naka_rushton | ...", `constraints: {}`.
- `contrast_sensitivity.value.model_fit.model` is the same: "(T8): naka_rushton_rb | ...", `{}`.
- `model_fit.value.model` is `{}` as well.
- Unit terms are also unbound:
  - `tuning_curve.value.response_unit`: "Unbound until the unit vocabulary is chosen (#73 item 24)".
  - `harmonic_component.value.response_unit` and `contrast_sensitivity.value.response_unit`: `{}`.
  - `model_fit.value.independent_variables.unit` and `.dependent_variable.unit`: `{}`.
  - `acquisition_epoch.channels.native_unit`: `{}`, with doc "volt | microvolt | digital_count ...".
- Other unbound terms: `coordinate_system.origin`, `.dimensions.axis`, `.dimensions.positive_direction`, `chemical.value.substance` and `score.value.scale`.
- The source_unit sign-off already made units registered, bound terms, so these unit slots disagree with it.

**A8. `clock_alignment.relation` is unbound and has no relation_bindings row (T8; T17 `passes`).**
- `clock_alignment.relation`: `constraints: {}`, doc "STAGED with an empty node ... needs an NDIC term".
- None of the 34 relation_bindings rows names "temporally aligned with", so the relation declares no `passes`. Every other relation's `relation` field is bound to those rows.

**A9. `intensity` cannot hold a measured physical intensity, although the signed T12 amendment sends one there.**
- TEAM-SIGN-OFF [method] (2026-10-21): "T12/T13 amended". The T12 amendment reads: "WHAT WAS DELIVERED (... a measured light intensity) uses the value for that quantity (`intensity`, ...)".
- `intensity.value` has only `arbitrary_units`: "A value cell for a dimensionless intensity (dF/F, fluorescence, ratios ...)".
- A source in W/m² or cd/m² cannot be converted into arbitrary units, so the canonical slot stays empty or loses meaning.

**A10. Software on a calculation: the doc says required, the schema says optional, and the change is only proposed.**
- `interaction.software_id` doc: "REQUIRED on calculations (calculation.require_inherited)".
- `calculation.json` has `"require_inherited": []`. Commit fd83a6c made that change: "Proposed: calculation.software_id optional ... recorded as Proposed (not decided)".
- So the document says one thing, the schema another, and the schema state is not decided.

**A11. "datum_order stays required" is not declared anywhere.**
- [covariate rules named] 6.3a: "`datum_order` stays required only on a sampled body of more than one dimension".
- `data.datum_order` doc: "Empty means F ... a writer with more than one dimension states it".
- No class declares a rule for it: `sampled_body.json`, `data_body.json` and `statement.json` have no `rules` key, `data.json`'s 7 rules do not mention it, and validate_v_eta.py has no match.
- T14 requires such a rule to be declared. "Empty means F" also gives a meaning to the very omission the decision forbids.

### LOW

**A12. Integer stored as a boolean.**
- `binaryseries_parameters.samples_regular_intervals` is an integer documented "0/1 -- whether samples are at regular intervals".
- `time_size` and `data_size` carry their unit (BITS) only in prose (T13, T14).
- The class is in_progress and mirrors v1, so this may fall under the tombstone exemption. Uncertain.

---

## B. INCONSISTENCIES

### MEDIUM

**B1. The entry is called "the same entry as a covariate's", but `logical` exists only on covariates.**
- `data.covariates.logical` exists ("New in data_body plan AMENDMENT 6").
- The conditions and parameters entries list "`term`, `quantity`, `count`, `text` or `matrix`" and say "the same entry as a covariate's": `statement.conditions`, `data_body.conditions`, `interaction`/`relation`/`method`/`clock_alignment_configuration` `.method.parameters`.
- So a whole-value boolean condition or setting has no form. AMENDMENT 6 adds `logical` only to covariates, so this is a scope gap, not a contradiction of a decision.

**B2. Three different shapes are each called "the shared fit entry".**
- `model_fit.value` has model, equation, independent_variables, dependent_variable, coefficients, constraints, goodness, sampled_fit, input_field and output_field.
- `tuning_curve_calculation.model_fit` has model, coefficients, goodness, metrics and sampled_fit ("each the shared fit entry {model, coefficients[], goodness, sampled_fit}").
- `contrast_sensitivity.value.model_fit` has model, coefficients, goodness, sensitivity, relative_max_gain, empirical_c50, saturation_index and sampled_fit.
- `sampled_fit.independent_values` doc cites "a model_fit's `independent_variables`", which two of the three shapes lack.

**B3. Significance and interpolated summaries sit in different places for the two vision calculators.**
- `tuning_curve.value` doc: "Calc-produced metadata (ANOVA p-values, fits) lives on `tuning_curve_calculation`". There it is the top-level `significance`.
- `contrast_sensitivity.value` instead holds `significance`, `interpolated_values` and `model_fit` inside the value.
- One concept also has two names: `contrast_sensitivity.value.interpolated_values.c50` against `contrast_tuning_calculation.interpolated_values.half_maximum_below` ("on a contrast curve ... this is C50").

**B4. An epoch is modelled two ways.**
- `entity.type` includes `epoch` ("one recording"). `entity.time_reference_id` doc: "an epoch's extent, one member per clock (the epoch's epochtable)" (time plan TEAM-SIGN-OFF [epoch and session wall-clock time]).
- `acquisition_epoch` is a separate class with `clocks[{name,t0,t1}]` "in the units of the clock", so its clock units are undeclared.
- Edges disagree on the referent: `directed_relation.epoch_id`, `method.epoch_id` and `ingestion_manifest.epoch_id` point at `entity`, while `ensemble.element_epoch_id` points at `acquisition_epoch`.
- The doc says "the epoch-family re-walk (#73 audit 2 D13)" is pending.

**B5. Same word, different concept.**
- `gain`: the `gain` value class is decibels; `acquisition_epoch.channels.gain` is a linear factor, "native = (stored - offset) * gain".
- `dimensions`: `data.dimensions` is `{term, n, chunk}`; `coordinate_system.dimensions` is `{axis, positive_direction, spacing}`.
- `origin`: `coordinate_system.origin` is an ontology_term with the doc "The same concept as a covariate's `origin`", but `data.covariates.origin` is numeric `{value, source_value}`.
- `coordinates`: `tuning_curve.value.coordinates` is char ('compass', 'cartesian'), an enum in prose only; `position.value.coordinates` is a numeric matrix.

**B6. Dimensionless ratio slots are named two ways (T14).**
- T14 cites `grams_per_gram` as a "complete unit" slot name, and `dose.value.amount_per_body_mass.grams_per_gram` follows it.
- `concentration.value.mass_fraction` and `volume_fraction` (also g/g and L/L) are named for the quantity instead.
- `concentration.value.od600` puts the wavelength in the slot name. Source_unit amendment 1 says "The wavelength (600 nm) is said by the variable and method, not the unit."

**B7. Registry state contradicts a decision.**
- [onset and offset terms] (2026-10-22): "EMPTY:0000140 "encounter onset time" is made obsolete, replaced by `onset time`".
- The term registry still lists EMPTY:0000140 with `"status": "decided"`. The registry has no obsolete status.

**B8. Cardinality flags differ inside the covariate entry.**
- `data.covariates.quantity.value` and `.source_value` are `matrix`, `mustBeScalar: true`.
- `.count`, `.text`, `.logical` and `.matrix` are `mustBeScalar: false`.
- `.term` is `mustBeScalar: false` with a scalar blank `{"node":"","name":""}`.
- acquisition_epoch's copy has the same flags. It is unclear whether `mustBeScalar` on a `matrix` means "one array". Uncertain.

### LOW: stale documentation referring to retired names (each quoted)

- `statement.distributive` and `directed_relation.distributive`: "meaningful only when the subject is a group (`subject.type` group)". Should be `entity.type`. directed_relation also copies "a cohort's size".
- `interaction.instrument_id`: "an instrument modeled as a subject (kind asserted via a term_assertion)".
- `interaction`/`relation`/`method`/`clock_alignment_configuration` `.parameters.variable`: "To be BOUND (not yet declared -- binding worksheet, 2026-09-25)". The field carries `{"binding": {"strength": "preferred", ...}}`.
- `relative_time_reference.referent_id`: "a migrator holds `base.session_id`". base.session_id became an edge on 2026-10-20 (base.json).
- `relative_time_reference.value.clock`: "see the build script for the evidence". The build script is deleted.
- `data.covariates.unit` and `acquisition_epoch.covariates.unit`: "PRACTICAL SI (V_gamma_SPEC.md)". The live statement is T14.
- `tuning_curve.value`: "the `stimulus condition` term is still to be chosen". [stimulus condition term] (2026-10-22) chose XCO:0000000, and it is registered.
- `logical.value`: "[SUPERSEDED IN PART ... `valid_interval` now migrates to `time_observation` ...]". These are leaf names that T3 (2026-10-08) abolished.
- `stimulus_presentation.stimuli.parameters` (in_progress): "become typed fields of the referenced stimulus value documents". TEAM-SIGN-OFF [method] makes recipes into `method` documents.
- `stimulus_presentation.stimulus_element_id`: "Typed `subject`".
- binding_registry_meta `description` and `notes`: "name the concrete leaf class ... (e.g. mass_observation, dose_manipulation, term_assertion)"; "Abstract types (entity, subject)"; "ordered marks terms where the directed sequence field is meaningful" (`sequence` became `order`, T20).
- Term registry `description`: "(a variable, method, unit, condition, parameter or key)"; "tools/build_v_eta.py copies it".
- index.json `notes`: "subject_relation documents, restored subject_statement/subject_assertion ...".
- data_body plan header index table:
  - AMENDMENT 1 row still says "angles are radians". The body is amended to degrees (item 44).
  - AMENDMENT 4 row says "PROPOSAL built ahead of signature". It is signed on 2026-10-21.
  - There is no row for AMENDMENT 6.
- Mixed term-name style within one bound set: `did_relation_directed` has `part_of` (snake_case) next to `orthologous gene mapping` (spaces). `did_response_type` uses `F0`/`F1`/`F2` (uppercase). (Low. T19 says a term's name is its label, so this may be intended.)

---

## C. TENET GAPS, CONFLICTS AND STALE TENET TEXT

### Stale tenet text (contradicted by later signed decisions or the built schema)

- **T12 and T13** still say "Proposed amendment (2026-10-21, `V_eta_method_plan.md`, ... not signed)" for "a stimulus recipe is a method" and "`parameters` allowed only inside `method`". TEAM-SIGN-OFF [method] (jess, 2026-10-21) says "T12/T13 amended". Rule 4 requires reading the header against the sign-off. Here the tenet header is stale in the cautious direction.
- **T11**: "**Leaf** = `<value>_<direction>` ... One direction-suffix set". T3's 2026-10-08 amendment says "there are no leaf classes". T11's grammar has no note pointing there. T3's own composite example list still has `timed_sequence` and `timed_sequence_manipulation`.
- **T14**:
  - "`datum_type`, stated ONCE on the data type". The schema field is `value.data_type` (T2 itself says "`datum_type` is renamed `data_type`"). T6 and T3 also say `datum_type`.
  - "the list is `_DIM_CANON` in `tools/build_v_eta.py`". The file is deleted and the list exists nowhere (see A3).
  - Index-base bullet: "`presentation_order` value *k* is the *k*-th `item_id` entry" and "(`presentation_order` value *k* → `presented_id_k`)". The field is `item.value.item`.
- **T6**: "The value's descriptors -- `dimensions`, `covariates`, `datum_type` -- live on `value`". `dimensions`/`covariates` are on `data`, shared by `value` and `data_body`. With bodies, "each body carries the dimensions of its own array" (data.dimensions doc).
- **T9**: names `subject` and `web_resource` as FAIR entities. Neither is in `entity.type`'s 19 values. `entity.global_identifier` says "A URL is an address for this entity, so it lives here rather than on a separate document."
- **T13** boolean list cites `modulated_response`. `tuning_curve.response_type` says "replaces ... contrast's `modulated_response` flag". It also says "`app` does not [earn the abbreviation]: prefer ... `software`", yet the in_progress class `app` (fields `app_name`, `app_version`) remains. The T13 v1 exemption may cover it, but its disposition is in_progress, not retire.

### Gaps (choices the schema makes that no tenet states)

1. **Canonical unit of an entry** (covariate, condition, parameter, model_fit variable, response). T14 fixes canonical units only through slot names on value cells. For `unit`-carrying entries, no tenet or schema rule says the unit must be the quantity's practical-SI unit, and no list exists (A3). Candidate: T14 states that an entry's `unit` must be the canonical unit for the variable's quantity, with a declared list in the schema.
2. **"Practical SI" is undefined for length, area, speed and acceleration.** The schema uses `meters`, `square_meters`, `meters_per_second` and `meters_per_second_squared` (strict SI). T14's examples choose non-base units elsewhere (grams, not kilograms). The Haley import writes mm and um/s (source_unit plan table). The tenet does not say whether metres is the "unit practitioners actually use" for length. It needs to be stated either way.
3. **Units whose dimension varies by document.** `tuning_curve.mean`, `harmonic_component.real` and `contrast_sensitivity.model_fit.sensitivity` carry a `response_unit` term instead of a named slot. `polynomial.coefficients` (clock_alignment) and `position.coordinates` ("in that dimension's spacing units") carry no unit field at all. T14 says "Every canonical slot names its complete unit" and allows multiple slots only for "incommensurable forms". It does not cover a value whose quantity is chosen per document. `tolerance` is also absent on these "dimensioned" cells, against "Every dimensioned cell carries it".
4. **Missing values in integer arrays.** T14 "Missing is not a value" prescribes "NaN (or the body's `fill_value`)". `count.value.count`, `covariates.count`, `item.value.item` (matrix, doc "NaN inline") and integer `data_type`s have no NaN, so an inline integer array cannot mark "attempted, not obtained". `fill_value` covers bodies only.
5. **Tolerance and approximation on covariates.** T14 says "covariates and conditions do not [carry tolerance]". Covariates now carry measured times (`onset time`, `offset time` read from `presentation_time.bin`) whose precision may be known. Only `approximate` ("Applies to the whole covariate") is available. The tenet should state that this is deliberate.
6. **Duplicated entry copies.** `acquisition_epoch` keeps a private copy of `data`'s dimensions/covariates without its rules (A4c). No tenet states that a structure must be declared once and inherited. (T14 "declared, not conventional" implies it but does not say so.)
7. **T8 strength for units.** T8 says vocabularies are "hard-validated, not advisory". The schema binds `source_unit` as `preferred` while leaving `unit`, `response_unit` and model terms unbound. No tenet says which slots may stay unbound, or for how long.
8. **Boolean form for conditions and parameters** (B1). AMENDMENT 6 added `logical` to covariates only. T14 says a condition is "a one-value fact"; it is unstated whether a boolean fact is a `term`, a `count` or forbidden.

### Conflicts between tenets / decisions

- T14 says "`degrees` (not radians)". Data_body plan AMENDMENT 1 section 2 header still reads "ANGLES ARE RADIANS, EVERYWHERE", with the amendment note inside it, and the plan's header index row still says "angles are radians". The schema and the term registry agree with T14: `om:radian` is registered only as a source unit, [spatial phase in degrees]. The conflict is only in the documentation.
- `interaction.software_id`: the signed calculator model expects software on calculations (doc "REQUIRED on calculations"). The proposed [calculation-software-optional] is built (A10). The two have not been reconciled by a decision.
