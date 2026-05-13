# Conversion: did_v1 → V_delta — `hartley_calc`

## Identity

- **V_delta `class_name`:** `hartley_calc`
- **V_delta tier:** `stable`
- **V_delta schema path:** `schemas/V_delta/stable/hartley_calc.json`
- **did_v1 source:** `VH-Lab/NDIcalc-vis-matlab` —
  `ndi_common/schema_documents/calc/hartley_calc_schema.json` plus
  `ndi_common/database_documents/calc/hartley_calc.json`.
- **Status:** `drafted`

## Summary

Calculator type that computes a Hartley-basis reverse correlation.
Inherits from `base` and `hartley_reverse_correlation`. Unlike the
empty-`input_parameters` calc types in NDIcalc-vis-matlab, this one
has actual input parameters (time-lag grid `T`, spatial samplings) and
a file reference to the produced kernel.

## Field mapping

| did_v1 location | V_delta location | Transformation |
|---|---|---|
| `class_name: "hartley_calc"` | same | identity |
| `superclasses: [base, hartley_reverse_correlation]` | same | identity |
| (top-level) `files.file_list: ["hartley_results.ngrid"]` | top-level `file` array, one entry `name: "hartley_results.ngrid"` | structural rename: did_v1 `files.file_list` → V_delta top-level `file` |
| `hartley_calc.input_parameters.T` | `hartley_calc.input_parameters.t` | snake-case rename; type `matrix<double>` |
| `hartley_calc.input_parameters.X_sampling` | `hartley_calc.input_parameters.x_sampling` | snake-case rename; `double` |
| `hartley_calc.input_parameters.Y_sampling` | `hartley_calc.input_parameters.y_sampling` | snake-case rename; `double` |
| `hartley_calc.depends_on` (internal struct with `element_id`, `stimulus_presentation_id`) | (removed — already inherited from `reverse_correlation`) | dependency redundancy dropped |

## Transformations in detail

- **`files.file_list` → top-level `file`.** did_v1 carries a class-block
  `files.file_list` array; V_delta has a dedicated top-level `file` field
  on schemas (file record objects with `name`, `mustBeNonEmpty`,
  `documentation`). Migration must move and reshape this list.
- **Capital-letter inputs renamed.** `T` / `X_sampling` / `Y_sampling`
  become `t` / `x_sampling` / `y_sampling` for snake-case compliance.
- **Inherited dependencies.** `element_id` and `stimulus_presentation_id`
  are inherited via `reverse_correlation`; they are not re-declared on
  `hartley_calc`.

## Default values for new fields

The did_v1 template carries `T: [0, 0.05, 0.10, 0.15, 0.20, 0.25]`,
`X_sampling: 1`, `Y_sampling: 1`. V_delta preserves these as
`default_value` on the respective fields.

## Worked example

- **Before (did_v1):** [`NDIcalc-vis-matlab/ndi_common/database_documents/calc/hartley_calc.json`](https://github.com/VH-Lab/NDIcalc-vis-matlab/blob/main/ndi_common/database_documents/calc/hartley_calc.json)
- **After (V_delta):** to be added under `schemas/V_delta/examples/`.

## File handling

This class declares one file: `hartley_results.ngrid`. See
[`_files.md`](_files.md) for how `.ngrid` file paths and integrity hashes
are translated under migration; this class follows those generic rules
with no type-specific behavior.

## Open questions

- **TODO-domain:** confirm `hartley_results.ngrid` is the only file the
  Hartley calculator produces, and that there are no auxiliary debug or
  intermediate files that should be declared.
- **TODO-domain:** ontology terms for the input-parameter fields
  (sampling intervals).

## Cross-references

- Parent: [`hartley_reverse_correlation.md`](hartley_reverse_correlation.md)
- Sibling: [`reverse_correlation.md`](reverse_correlation.md)
- General file-handling rules: [`_files.md`](_files.md)
