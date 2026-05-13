# Conversion: did_v1 → V_delta — `contrast_sensitivity_calc`

## Identity

- **V_delta `class_name`:** `contrast_sensitivity_calc`
- **V_delta tier:** `stable`
- **V_delta schema path:** `schemas/V_delta/stable/contrast_sensitivity_calc.json`
- **did_v1 source:** `VH-Lab/NDIcalc-vis-matlab` —
  `ndi_common/schema_documents/calc/contrastsensitivity_calc_schema.json`
  plus `ndi_common/database_documents/calc/contrastsensitivity_calc.json`.
- **Status:** `drafted`

## Summary

Calculator type that produces a per-spatial-frequency contrast sensitivity
profile by fitting a contrast response (RB, RBN, RBNS Naka-Rushton variants)
at each spatial frequency. Unlike the tuning calculators, this class
inherits only from `base` and carries its analysis outputs as its own
top-level fields rather than via a `*_tuning` result superclass.

did_v1 name `contrastsensitivity_calc` is normalized to
`contrast_sensitivity_calc`.

## Field mapping

| did_v1 location | V_delta location | Transformation |
|---|---|---|
| `class_name: "contrastsensitivity_calc"` | `class_name: "contrast_sensitivity_calc"` | rename (snake-case) |
| (top-level) `depends_on: [element_id, stimulus_presentation_id, stimulus_response_scalar_id]` | top-level `depends_on` | identity |
| `contrastsensitivity_calc.input_parameters` | `contrast_sensitivity_calc.input_parameters` | empty struct → typed structure with empty `fields` |
| `contrastsensitivity_calc.depends_on` (internal struct with `element_id`) | (removed — already at top-level `depends_on`) | redundant in did_v1; dropped |
| `spatial_frequencies` | same | `matrix<double>` |
| `sensitivity_{RB,RBN,RBNS}` | `sensitivity_{rb,rbn,rbns}` | snake-case; `matrix<double>` |
| `relative_max_gain_{RB,RBN,RBNS}` | `relative_max_gain_{rb,rbn,rbns}` | same |
| `empirical_c50_{RB,RBN,RBNS}` | `empirical_c50_{rb,rbn,rbns}` | same |
| `saturation_index_{RB,RBN,RBNS}` | `saturation_index_{rb,rbn,rbns}` | same |
| `parameters_{RB,RBN,RBNS}` | `parameters_{rb,rbn,rbns}` | same |
| `fitless_interpolated_c50` | same | `matrix<double>` |
| `is_modulated_response` | same | `double` (boolean stored as 0/1 for v1 compat) |
| `visual_response_p_bonferroni` | same | `matrix<double>` |
| `response_varies_p_bonferroni` | same | `matrix<double>` |
| `response_type` | same | `char` |

## Transformations in detail

- **Snake-case variant tags.** All `_RB` / `_RBN` / `_RBNS` suffixes are
  lowercased to `_rb` / `_rbn` / `_rbns`.
- **Inheritance.** Despite producing contrast-sensitivity outputs, this
  calc does NOT inherit from `contrast_tuning` in did_v1 — only from
  `base`. V_delta preserves that choice. (A future refactor could
  consider whether `contrast_sensitivity_calc` should inherit from
  `contrast_tuning` so the per-frequency RB/RBN/RBNS fits are stored in
  the inherited `contrast_tuning.fit` structure instead of as flat
  per-metric arrays here; deferred to domain review.)
- **`is_modulated_response` as 0/1 double.** did_v1 stores this as a
  numeric scalar (`0`); V_delta declares it `type: double` to preserve
  shape rather than `boolean`, on the assumption that legacy tooling
  reads it as a number. Promote to `boolean` in a follow-up if appropriate.

## Default values for new fields

None.

## Worked example

- **Before (did_v1):** [`NDIcalc-vis-matlab/ndi_common/database_documents/calc/contrastsensitivity_calc.json`](https://github.com/VH-Lab/NDIcalc-vis-matlab/blob/main/ndi_common/database_documents/calc/contrastsensitivity_calc.json)
- **After (V_delta):** to be added under `schemas/V_delta/examples/`.

## File handling

No file references. See [`_files.md`](_files.md) for generic rules.

## Open questions

- **TODO-domain:** should `contrast_sensitivity_calc` inherit from
  `contrast_tuning` so the per-frequency fit metrics ride the existing
  `fit.naka_rushton_*` structure on the parent?
- **TODO-domain:** `is_modulated_response` — promote to `boolean`?
- **TODO-domain:** ontology terms for sensitivity / gain / c50 fields.

## Cross-references

- Related result type: [`contrast_tuning.md`](contrast_tuning.md)
- Related calculator: [`contrast_tuning_calc.md`](contrast_tuning_calc.md)
- General file-handling rules: [`_files.md`](_files.md)
