# Audit B: the 47 persist data_type composites

**Denominator.** I read 47 of 47 composite schemas (`schemas/V_eta/{stable,draft}/<class>.json`, every field and its documentation). I also read these for cross-checks: `relation`, `subject_statement`, `subject_interaction` (grep only), `draft/sampled_body`, `draft/data_body`, `tuning_curve_calculation`, `contrast_tuning_calculation`, `contrast_sensitivity_calculation`, `hartley_calc`, and V_zeta `reverse_correlation`/`hartley_reverse_correlation`.

I read 10 plan documents:
- read in full: `V_eta_tenets.md` and `V_eta_spatial_transcriptomics_plan.md`;
- `V_eta_tuning_model_plan.md`: :1-100 and :140-229 (I skipped :100-140);
- `V_eta_data_body_model_plan.md`: :505-530 and :870-1105, plus greps;
- `V_eta_ngrid_family_findings.md`: :300-406;
- `V_eta_stimulus_model_plan.md`: :222-300, plus greps;
- `V_eta_logical_observation_plan.md`: :340-459;
- `V_eta_clock_alignment_cluster_plan.md`: :129-150 and the sign-offs at :493-495, plus greps;
- `V_eta_image_model_plan.md`: headings and the tail;
- `V_gamma_SPEC.md`: :605-630, for the canonical-unit rule.

I did not read `V_eta_time_reference_model_plan.md` beyond what CLAUDE.md quotes.

This report is read-only. It decides nothing, and every fix below is a suggestion.

## Summary

| class | count |
|---|---|
| VIOLATION | 3 |
| INCONSISTENCY | 11 |
| STALE-DOC | 5 |
| QUESTION | 8 |

None of the 47 composites has an `is_`/`has_` boolean, a camelCase field or a 1-based index. I also found none of the retired class names in any composite's documentation (`session_relative_reference`, `relative_reference`, `ngrid` used as a live parent, `calculator`, `stimulus_presentation`). The only boolean names are `approximate`, `blank`, `complete`, `regular`, `cyclic` and `modulated_response`.

## Quantity-shape table (the `value` cell)

| composites | canonical slot(s) | source provenance | `approximate` |
|---|---|---|---|
| acceleration, amount, angle, angular_velocity, area, capacitance, charge, conductance, current, energy, force, frequency, length, power, resistance, velocity, voltage (17) | one per class, named after an SI unit: `meters_per_second_squared`, `moles`, `radians`, `radians_per_second`, `square_meters`, `farads`, `coulombs`, `siemens`, `amperes`, `joules`, `newtons`, `hertz`, `meters`, `watts`, `ohms`, `meters_per_second`, `volts` | `source_unit` + `source_value` | yes |
| time, mass, volume, temperature | `seconds`, **`grams`**, **`liters`**, **`celsius`**: practical SI, not base SI | same | yes |
| **pressure** | **`mmhg`**: not SI at all | same | yes |
| gain | `decibels` | same | yes |
| **intensity** | **`arbitrary_units`** | same | yes |
| **ph** | **`ph`** (the slot has the class's own name) | same, although a pH has no unit | yes |
| **concentration** | **five** optional slots: `molar`, `grams_per_liter`, `mass_fraction`, `volume_fraction`, `particles_per_liter` | same | yes |
| **count** | **`value`** (integer) + `unit` (an unbound ontology_term that names what is counted) | **none** | yes |
| **score** | **`value`** + `scale` (term) + `scale_min` / `scale_max` | **none** | yes |
| **date** | `instant` (ISO char) + `precision` (enum) | **`source`** (raw string), not `source_value` | **no** |
| image `keys[].origin` / `spacing` / `values` | `value` / `values` + a bound `unit` term on the key | `source_value(s)` + `source_unit` | per key |
| tuning_curve `independent_variables[]` | `values` + `unit` term | **none** | **no** |
| visual_grating | bare doubles, with the unit given **only in prose** | a separate `source_geometry` block with a char `unit` | no |

## Findings, most severe first

### visual_grating

1. **VIOLATION: the angles are in degrees, but angles are decided to be radians everywhere.**
   - Schema: `stable/visual_grating.json:38` `value.angle`, *"Orientation/direction of the grating, degrees"*, and `:170` `value.phase`, *"Spatial phase of the grating, degrees"*.
   - Decision: `V_eta_data_body_model_plan.md:927` *"ANGLES ARE RADIANS, EVERYWHERE"*, `:937-938` *"`angle`'s is `radians`. So `orientation` and `direction` axes are RADIANS"*, and a degrees-based proposal *"was put and rejected"*.
   - Consequence: after migration a 45° grating stores `45` while the `tuning_curve` axis it drives stores `0.785` (`tuning_curve.json` `independent_variables.unit`: *"radians for angles"*). The stimulus plan's own example query, *"find the `visual_grating` doc at ~45°"* (`V_eta_stimulus_model_plan.md:91`), then compares across two unit systems.
   - Suggestion: store radians canonically and keep degrees as the source value, the same way `angle` does.

2. **VIOLATION (T14): the units of every numeric field are written only in prose.** `angle`, `spatial_frequency` (*"cycles/degree"*), `size`, `position.x`/`.y` and `duration` are all bare `double`s, and their units live only in `documentation`. T14 requires *"Anything a consumer must know in order to read a value is declared in the schema"*, and warns against the case where a value's *"internals are then known solely to whoever wrote the migrator"*.
   - Suggestion: type these fields as the existing composites (`angle`, `time`, …), or declare a unit term for each.

3. **QUESTION: `value.position` (x, y in degrees) reuses the name of the `position` data type.** That data type requires a `coordinate_system_id` (`draft/position.json`, depends_on). T13 says *"a field's noun must match its semantics"*. The same collision exists for `tuning_curve.value.coordinates` (a char basis, `tuning_curve.json:309`) against `position.value.coordinates` (a numeric matrix). `coordinates` is named in the 2026-09-21 tuning sign-off, so that name is signed.

### contrast_sensitivity

4. **VIOLATION (T14): `value.model_fit.goodness` declares no sub-fields.** It is a `structure` with `"fields": []` (`stable/contrast_sensitivity.json:124-126`), documented as *"Fit-quality scalars (r², residual, …)"*. T14 says *"undeclared internals are an opaque blob no matter how well named"*. Its sibling declares them: `tuning_curve_calculation.model_fit.goodness` has `{r2, sse}`.
   - Suggestion: declare `{r2, sse}`.

5. **INCONSISTENCY: its fit shape and names differ from the tuning family's.**
   - Its `model_fit` is `{model, coefficients:matrix, goodness, sensitivity, relative_max_gain, empirical_c50, saturation_index}`.
   - The #73 amendment sets fit entries to *"`{model, coefficients, goodness, metrics, sampled_fit}`"* (`V_eta_tuning_model_plan.md`, amendment item 5), and `tuning_curve_calculation` builds `coefficients` as a `structure`.
   - `interpolated_values.c50` keeps the name that #73 item 6 retires (*"`l50` and `interpolated_c50` → `half_maximum_below`"*).
   - The significance fields are `*_p_bonferroni` here and `*_anova_p` on the tuning leaf.
   - Suggestion: align it with the #73 fit-entry shape, or record why contrast sensitivity differs.

6. **INCONSISTENCY: calculation outputs sit on the composite here, but on the leaf for tuning.** The 2026-09-21 sign-off moved *"significance and model_fit[] on the LEAF (calc-produced); everything else on the composite"* (`V_eta_tuning_model_plan.md:144ff`, item 3). `contrast_sensitivity` keeps `model_fit`, `significance` and `interpolated_values` on the composite, and `contrast_sensitivity_calculation` declares no fields. That sign-off is scoped to tuning, so this is a disagreement between siblings, not a violation.
   - Suggestion: a team call on whether the field split applies here too.

### reverse_correlation / hartley_reverse_correlation / receptive_field

7. **INCONSISTENCY: `hartley_reverse_correlation` puts the method in the class name, which a signed decision rules out.**
   - Signed: `TEAM-SIGN-OFF [receptive field fold]` 2026-08-17 (`V_eta_ngrid_family_findings.md:358`): *"`reverse_correlation.method` becomes a bound term on the composite, NOT part of the class name"*. The schema says the same: `receptive_field.value.method`, *"The METHOD, never part of the class name (T11)"*.
   - Counter-authority: the builder cites *"TEAM-SIGN-OFF 2026-09-21, issue #67 category ③"* for keeping both as thin markers (`tools/build_v_eta.py:3626-3633`). I did not find that line in any plan document.
   - The #73 amendment dropped the five tuning markers on exactly this ground: *"The fact each encoded is already `…variable`, and nothing tied the two together (T11, T14)"*. The same holds here: nothing ties `hartley_reverse_correlation` to `value.method`.
   - Both classes have empty `fields`, and their only descendant is the retired v1 tombstone `hartley_calc`. `receptive_field_calculation` does not inherit through either of them.
   - Suggestion: a team call on whether #73's marker reasoning retires both, leaving `hartley_calc` directly under `receptive_field` or `base`.

8. **QUESTION: I could not confirm item 38's claim that unmigrated `hartley_calc` documents still validate.** Item 38 (`V_eta_spatial_transcriptomics_plan.md`) says they do. But the tombstone now inherits `hartley_reverse_correlation` and `reverse_correlation`, and both declare **zero** fields in V_eta. The V_zeta versions declared `stimulus_properties`, `reconstruction_properties`, `spiketimes`, `frame_times`, `hartley_numbers`, `method` and `dimension_labels`, and `V_eta_ndi_ground_truth.json:88` records the writer emitting `hartley_numbers`. The tombstone also inherits `receptive_field.value` with `mustBeNonEmpty: true`, which a v1 document does not carry. I found no test or checker that covers this tombstone: `check_tombstones.py`'s output does not list it.
   - Suggestion: add a fixture-validation test for a v1 `hartley_calc` passthrough.

9. **STALE-DOC: the receptive_field documentation still says `axes[]`.** `stable/receptive_field.json:25` reads *"the axes … are declared there, on `axes[]`"*, but item 14 renamed *"`axes` → `keys` in all four places"*, and `draft/sampled_body.json:31` declares `keys`. The builder source carries the same text (`tools/build_v_eta.py` near :3617).

10. **INCONSISTENCY (T6/T11): `value.storage_mode` duplicates the statement's field.** It is a char inside the payload (`receptive_field.json:76`), while `subject_statement.json:806` already declares `storage_mode`. T6 treats storage as orthogonal to meaning, and T14's one-payload-slot rule means the payload should not restate how it is stored. Two homes can also disagree.
    - Suggestion: drop it from `value`.

### The quantity composites (28 of them)

11. **STALE-DOC: 28 composites say timing lives in `sample_time`, which is signed to retire.** The 28 are all of the quantity classes plus `count` and `score`. For example `stable/voltage.json:31`: *"Per-sample timing is the statement's sample_time cadence (D1)"*.
    - Signed: `TEAM-SIGN-OFF [data_body]` 2026-08-14 (`V_eta_data_body_model_plan.md:648`): *"time becomes an ordinary axis and both sample_time blocks retire"*; build step `:519` is *"retire sample_time from both schema sites"*.
    - The sibling `image.json:51` already says *"Time is an ordinary key"*.
    - The retirement is not built: `subject_interaction.json:117` still declares `sample_time`. The prose therefore matches the build but not the decision.
    - Suggestion: reword to "per-sample timing is a time key", either when the retirement lands or now.

12. **INCONSISTENCY: the "SI" claim does not match the canonical units actually used.**
    - Claims: `V_eta_data_body_model_plan.md:937` *"Every quantity in V_eta names its canonical slot after an SI unit"*. `image.json:117` and `subject_statement.json:455` say *"the SI convention every other quantity in V_eta follows"*, and `tuning_curve.json:117` says *"per SI convention"*.
    - Schema: `pressure.value.mmhg` (`pressure.json:35`) is not SI. `celsius`, `liters`, `grams`, `decibels` and `arbitrary_units` are not SI base units.
    - The rule that actually governs is *"practical SI unit … not necessarily the strict SI base unit"* (`V_gamma_SPEC.md:612-617`), plus the 2026-09-23 grams decision (`build_v_eta.py:9055-9060`).
    - The radians conclusion survives, because `angle.value.radians` exists.
    - Suggestion: reword the three documentation strings to "practical-SI canonical".

13. **QUESTION: the "practical SI" family is not internally consistent.** `length` is `meters` and `area` is `square_meters`, but `volume` is `liters`, not `cubic_meters`. `pressure` is `mmhg` rather than `pascals`, and nothing in the table relates it to the other SI-derived units (`newtons`, `square_meters`). I found no dated decision for `mmhg`; the builder calls it *"attested in migrator code"* (`build_v_eta.py:9052-9054`). A team call.

14. **QUESTION (T14): `intensity.value.arbitrary_units` calls itself comparable.** Its documentation says it is *"the normalised, cross-document comparable number"* (inherited wording). An a.u. value (dF/F against raw fluorescence) is by definition not comparable across documents without `variable`. `ph.value.ph` likewise has a `source_unit` with nothing to hold. Suggestion: document that the dimensionless cells carry no cross-document normalisation.

15. **QUESTION: `count`, `score` and `date` depart from the quantity pattern** (see the table). The documentation for `count` justifies its choice (*"semantic, NOT dimensional"*). For `score` (no `source_value` / `source_unit`) and `date` (`source`, no `approximate`) I found no recorded reason. Suggestion: record the reason next to each, or align them.

### tuning_curve

16. **INCONSISTENCY: `value.response_units` is free-text `char`** (`tuning_curve.json:283`, e.g. *"'spikes/s', 'dF/F'"*). The amended key carries `unit` as a bound `ontology_term`, because *"a free-text unit beside a bound `variable` is the escape hatch that makes the binding pointless"* (`V_eta_data_body_model_plan.md:898-907`). `response_type` and `coordinates` are free `char` as well, and so is `contrast_sensitivity.response_type`. Suggestion: make `response_units` an `ontology_term`.

17. **INCONSISTENCY (T14): `independent_variables[]` is a thinner copy of the key entry.** It has `{variable, values, unit}`, with no `source_values` / `source_unit` / `approximate`, and no `labels` even though its own documentation says the unit is *"absent for a categorical variable"*. Categorical positions therefore have nowhere to go. Converting degrees to radians loses the as-recorded values that T14's *"canonical value plus lossless source provenance"* requires. Keeping the name `independent_variables` is signed (#67); the reduced shape is not.
    - Suggestion: reuse the key sub-field layout under the signed name.

18. **QUESTION: parallel statistic columns, against item 15.** `mean`, `stddev`, `stderr`, `individual` and `raw_individual` are parallel columns over one grid. Item 15 says *"anything that looks like another column is a key (pyraview's min/max is a `statistic` key)"*. Item 15 is scoped to bodies, but a body-backed `tuning_curve` would hit it. A team call on whether the composite's layout survives in body storage.

### harmonic_component

19. **INCONSISTENCY: the control fields use the flat prefix that tuning_curve avoids on purpose.** `value.control_real` / `value.control_imaginary` are prefixed (`draft/harmonic_component.json:68`). Its sibling nests them for exactly this reason: `tuning_curve.value.control`, *"nested for symmetry … avoids parallel `control_*` prefixed fields"* (`tuning_curve.json:225`). Suggestion: `control: {real, imaginary}`.

### chemical / formulation / dose / amount / concentration

20. **INCONSISTENCY (T14 "declared once"): one agent shape is declared three times, and the copies already disagree.** The agent `{substance, amount}` is declared separately in `chemical.value`, `formulation.value.chemicals[]` and `dose.value.formulation.chemicals[]`, each as an inline `structure` rather than typed as `chemical` or `formulation`. Quantities, by contrast, nest by type name (`type: concentration`). The copies disagree: `formulation.json:33` has `chemicals` `mustBeNonEmpty: true`, and `dose.json:46` has `false`. This is also why `chemical` has no user (sweep item).
    - Suggestion: type the nested fields as `chemical` / `formulation`.

21. **INCONSISTENCY (T13): the field `chemical.value.amount` has type `concentration`** (`chemical.json:76`), while a composite named `amount` (moles) exists. The same field name and class name mean different quantities. Suggestion: rename the field `concentration`.

22. **QUESTION (T11, one home): `dose.value.route` is documented *"optional; else on method"*.** That gives route two admissible homes.

### clock_alignment / polynomial

23. **QUESTION (T6 / items 24 and 30): clock_alignment holds its data two different ways.** It is ⊂ [`relation`, `polynomial`], so it carries its data inline as a data type. Item 24/30 later gave `relation` a `value_id` edge for exactly this purpose (*"the standalone data_type document holding this relation's data"*, `relation.json:17`). A relation carrying data is therefore modelled in two ways, and `clock_alignment` inherits both an inline `value` and a `value_id`. Separately, T6 says *"a standalone data-type document is CONTENT, NOT A CLAIM"*, yet `isa data_type` returns this relation, which is a claim. The multiple inheritance is signed (`V_eta_clock_alignment_cluster_plan.md:495`, 2026-08-08) and predates items 24 and 30. A team call.

24. **STALE-DOC: polynomial's documentation still says `axis.n`.** `draft/polynomial.json:51` reads *"Same test that kept `axis.n`"*; item 14 renamed it to `keys[].n`.

### logical

25. **STALE-DOC: logical's documentation still describes the withdrawn `valid_interval` fold.** `draft/logical.json:25` says *"FOR THE `valid_interval` FOLD, EACH CELL IS ONE INTERVAL"*, and the long block of consumer reading rules is written for that fold. `TEAM-SIGN-OFF [logical_observation amendment 1]` 2026-08-18 (`V_eta_logical_observation_plan.md:420`) says *"`valid_interval` migrates to `time_observation`, not `logical_observation` … The array of booleans is WITHDRAWN"*. `logical` has since gained a stated user (item 24: gene-mapping *"`score` (or `logical`) document"*), so the documentation now describes the wrong consumer.
    - Suggestion: move the validity reading rules to wherever `time_observation` validity lives.

### image

26. **INCONSISTENCY: `keys[].labels_from` points at an edge a standalone `image` cannot have.** The field (`image.json:371`) names *"an `axis_labels_#` edge on this document"*. `image` declares no `depends_on`; only `subject_statement.json:21` declares `axis_labels_#`. Item 19 makes `image` concrete for storage by reference, and a standalone `image` document can then never satisfy `labels_from`.
    - Suggestion: declare `axis_labels_#` on `image`, or document that `labels_from` is statement-only.

### Composites carrying edges (judgement; no finding)

`position.coordinate_system_id` (required) and `timed_sequence.presented_id_#` are the only edges on a composite. Both are needed to interpret the value, like a unit (item 9, and the stimulus sign-off at `:224`), so I do not read them as claims. `presented_id_#` follows the T14 `_#` + `multiple` rule.

### The yardstick itself

27. **STALE-DOC: the tenets repeat superseded wording.** `V_eta_tenets.md:43` (T2) still gives an interaction *"a per-sample `sample_time` cadence"*, and T6 still describes `sampled_body` as *"sample-time axis + typed datum + summary"*. The 2026-08-14 data_body signature retires `sample_time` and drops `summary`. Suggestion: re-sync T2 and T6 with the data_body signature.
