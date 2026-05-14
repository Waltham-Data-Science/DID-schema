# Conversion: did_v1 → V_delta — `speed_tuning`

## Identity

- **V_delta `class_name`:** `speed_tuning`
- **V_delta tier:** `stable`
- **V_delta schema path:** `schemas/V_delta/stable/speed_tuning.json`
- **did_v1 source:** `VH-Lab/NDIcalc-vis-matlab` —
  `ndi_common/schema_documents/vision/speed_tuning_schema.json` plus
  the paired template
  `ndi_common/database_documents/vision/speed_tuning.json`.
- **Status:** `drafted`

## Summary

Result type for empirical and fit-derived tuning along (SF, TF) pairs in
the speed plane. Independent of the calculator that produced it;
calculators (e.g., `speed_tuning_calc`) inherit from this class.

Conversion is primarily a structural reshaping: did_v1 declares each
top-level grouping as an unconstrained `type: "structure"`, so all
field-level typing in V_delta is recovered from the paired db_doc
template.

## Field mapping

| did_v1 location | V_delta location | Transformation |
|---|---|---|
| `speed_tuning.properties.{response_units,response_type}` | same | `char` types (response_units per user decision) |
| `speed_tuning.tuning_curve.{spatial_frequency,temporal_frequency}` | same | scalar placeholder → `matrix<double>` (1xN sampled values) |
| `speed_tuning.tuning_curve.{mean,stddev,stderr}` | same | scalar placeholder → `matrix<double>` |
| `speed_tuning.tuning_curve.individual` | same | empty struct in v1 → `matrix<double>` (rows index sampled (SF, TF) points; columns index trials) |
| `speed_tuning.tuning_curve.raw_individual` | same | empty struct in v1 → `matrix<double>` (no blank subtraction / normalization) |
| `speed_tuning.tuning_curve.control_individual` | same | empty struct in v1 → `matrix<double>` (per-trial control responses) |
| `speed_tuning.significance.{visual_response_anova_p,across_stimuli_anova_p}` | same | identity (double) |
| `speed_tuning.fit.Priebe_fit_*` (9 fields) | `speed_tuning.fit.priebe_fit_*` | snake-case; scalar metrics → `double`, array metrics → `matrix<double>`; `Priebe_fit_speed_tuning_index` (`[0]`) unwrapped to scalar `double` |
| `speed_tuning.fit_no_speed.*` | same (snake-cased) | same as `fit` plus `partial_r2` and `priebe_fit_nested_f_test_p_value` |
| `speed_tuning.fit_fullspeed.*` | same (snake-cased) | same as `fit_no_speed` |
| (top-level) `depends_on: [element_id, stimulus_tuningcurve_id]` | top-level `depends_on` | identity |

## Transformations in detail

- **Snake-case.** `Priebe_*` prefix is lowercased to `priebe_*`.
- **`speed_tuning_index` unwrapped.** did_v1 stores
  `Priebe_fit_speed_tuning_index` as a 1-element array `[0]` in all three
  fit blocks. The user-supplied documentation describes it as a singular
  index ("Provides an index of the relationship between preferred speed
  and spatial frequency"), so V_delta declares it as scalar `double` /
  `mustBeScalar: true`. Migration tools must extract `arr[0]` and verify
  the array has exactly one element. This is the same unwrap convention
  applied to the scalar `[0]` placeholders in `contrast_tuning` and
  `orientation_direction_tuning`.
- **Three fit families.** did_v1 stores three nested fit blocks
  (`fit`, `fit_no_speed`, `fit_fullspeed`) with overlapping field sets.
  `fit_no_speed` and `fit_fullspeed` add `partial_r2` and
  `priebe_fit_nested_f_test_p_value` for the nested F-test comparison;
  `fit` does not. V_delta preserves all three blocks and the
  field-membership difference between them.
- **Trial-axis convention.** For the per-trial matrices (`individual`,
  `raw_individual`, `control_individual`) V_delta documents the
  row-vs-column convention explicitly: rows index sampled (SF, TF) points,
  columns index trials.

## Default values for new fields

None added by this PR. The planned global `schema_version` field will
land via a follow-up that updates `base`.

## Worked example

- **Before (did_v1):** [`NDIcalc-vis-matlab/ndi_common/database_documents/vision/speed_tuning.json`](https://github.com/VH-Lab/NDIcalc-vis-matlab/blob/main/ndi_common/database_documents/vision/speed_tuning.json)
- **After (V_delta):** to be added under `schemas/V_delta/examples/`.

## File handling

No file references. See [`_files.md`](_files.md) for generic rules.

## Open questions

- **TODO-domain:** ontology terms for fit-parameter fields.
- **TODO-domain:** the meaning and shape of the seven Priebe
  parameters in `priebe_fit_parameters` should be documented (currently
  the schema notes only the parameter count).

## Cross-references

- Calculator that produces this result type:
  [`speed_tuning_calc.md`](./speed_tuning_calc.md)
- Sibling fit-block patterns:
  [`contrast_tuning.md`](./contrast_tuning.md)
- General file-handling rules: [`_files.md`](_files.md)
