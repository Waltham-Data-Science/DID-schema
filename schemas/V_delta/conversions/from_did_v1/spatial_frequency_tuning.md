# Conversion: did_v1 → V_delta — `spatial_frequency_tuning`

## Identity

- **V_delta `class_name`:** `spatial_frequency_tuning`
- **V_delta tier:** `stable`
- **V_delta schema path:** `schemas/V_delta/stable/spatial_frequency_tuning.json`
- **did_v1 source:** `VH-Lab/NDIcalc-vis-matlab` —
  `ndi_common/schema_documents/vision/spatial_frequency_tuning_schema.json` plus
  `ndi_common/database_documents/vision/spatial_frequency_tuning.json`.
- **Status:** `drafted`

## Summary

Result type for empirical and fit-derived tuning along spatial frequencies (cycles per degree). Independent of the calculator that produced it; calculators (e.g., `spatial_frequency_tuning_calc`) inherit from this class.

Conversion is primarily a structural reshaping: did_v1 declares each top-level grouping as an unconstrained `type: "structure"`, so all field-level typing in V_delta is recovered from the paired db_doc template.

## Field mapping

| did_v1 location | V_delta location | Transformation |
|---|---|---|
| `spatial_frequency_tuning.properties.{response_units,response_type}` | same | `char` types (response_units per user decision) |
| `spatial_frequency_tuning.tuning_curve.spatial_frequency` | same | scalar placeholder → `matrix<double>` |
| `spatial_frequency_tuning.tuning_curve.{mean,stddev,stderr}` | same | scalar placeholder → `matrix<double>` |
| `spatial_frequency_tuning.tuning_curve.individual` (+ for `speed_tuning`: `raw_individual`, `control_individual`) | same | empty struct → `type: structure` with empty `fields` (shape TODO-domain) |
| `spatial_frequency_tuning.tuning_curve.{control_stddev,control_stderr}` (where present) | same | scalar placeholder → `matrix<double>` |
| `spatial_frequency_tuning.significance.{visual_response_anova_p,across_stimuli_anova_p}` | same | identity (double) |
| `spatial_frequency_tuning.fitless.*` (where present) | same | scalar placeholder → `double`; fields: L50, Pref, H50, low_pass_index, high_pass_index, bandwidth |
| `spatial_frequency_tuning.fit*` families | nested `structure` per fit family | scalar metrics → `double`; array metrics → `matrix<double>`; fit families: `fit_dog (DoG)`, `fit_movshon`, `fit_movshon_c`, `fit_spline`, `fit_sgauss` |
| (top-level) `depends_on: [element_id, stimulus_tuningcurve_id]` | top-level `depends_on` | identity |

## Transformations in detail

- **Snake-case everywhere.** Field names like `L50`/`Pref`/`H50`/`R2` are lowercased to `l50`/`pref`/`h50`/`r2` to comply with V_gamma's snake_case rule.
- **Mixed scalar/array fields in did_v1 are normalized.** For example, `fit_movshon.values` is declared as scalar `0` while `fit_dog.values` is `[0]`; V_delta unifies these as `matrix<double>` per user direction ("double arrays for this").
- **No fitless block on `speed_tuning`.** The other tuning types carry a `fitless` block; `speed_tuning` doesn't have one in did_v1, so V_delta doesn't declare it.

## Default values for new fields

None added by this PR. The planned global `schema_version` field will land via a follow-up that updates `base`.

## Worked example

- **Before (did_v1):** [`NDIcalc-vis-matlab/ndi_common/database_documents/vision/spatial_frequency_tuning.json`](https://github.com/VH-Lab/NDIcalc-vis-matlab/blob/main/ndi_common/database_documents/vision/spatial_frequency_tuning.json)
- **After (V_delta):** to be added under `schemas/V_delta/examples/`.

## File handling

No file references. See [`_files.md`](_files.md) for generic rules.

## Open questions

- **TODO-domain:** shape of `tuning_curve.individual` (and, for `speed_tuning`, `raw_individual` / `control_individual`). did_v1 leaves these as empty structs.
- **TODO-domain:** ontology terms for fit-parameter fields.
- **TODO-domain:** the `abs` placeholder block on `spatial_frequency_tuning` and `temporal_frequency_tuning` — purpose unknown; currently declared as an empty `structure`.

## Cross-references

- Calculator(s) that produce this result type: [`spatial_frequency_tuning_calc.md`](./spatial_frequency_tuning_calc.md)
- General file-handling rules: [`_files.md`](_files.md)
