# Conversion: did_v1 → V_delta — `oridirtuning_calc`

## Identity

- **V_delta `class_name`:** `oridirtuning_calc`
- **V_delta tier:** `stable`
- **V_delta schema path:** `schemas/V_delta/stable/oridirtuning_calc.json`
- **did_v1 source:** `VH-Lab/NDIcalc-vis-matlab` —
  `ndi_common/schema_documents/calc/oridirtuning_calc_schema.json` plus
  `ndi_common/database_documents/calc/oridirtuning_calc.json`.
- **Status:** `drafted`

## Summary

A calculator type that computes an `orientation_direction_tuning` result and
stores the calculator's own input parameters in the inherited
`calculator.input_parameters` slot. The V_delta name `oridirtuning_calc`
matches the did_v1 source — earlier V_delta drafts had renamed it to
`orientation_direction_tuning_calc` "to match the snake-cased naming of the
result type it inherits from", but that rename invented a class name that
does not appear in the NDI calculator hierarchy
(`ndi.calc.vis.oridir_tuning`), so the original name is restored.

## Field mapping

| did_v1 location | V_delta location | Transformation |
|---|---|---|
| `document_class.class_name: "oridirtuning_calc"` | `document_class.class_name: "oridirtuning_calc"` | identity |
| `superclasses: [base, orientation_direction_tuning]` | `superclasses: [base, orientation_direction_tuning, tuning_fit]` | added `tuning_fit` (and transitively `calculator` and `app`) so the calculator interface lives on the shared base, not on each subclass |
| `oridirtuning_calc.input_parameters` | `calculator.input_parameters` | moved up to the abstract `calculator` base (field is now inherited, not declared per-subclass) |
| `app.name`, `app.version` (top-level v1 block) | `app.app_name`, `app.app_version` (same block) | universal app-block field rename in did2.convert.universalRenames; the v1 source already carries the canonical NDI calculator class name in `app.name` (e.g., "ndi.calc.vis.oridir_tuning"), so V_delta does not need a separate `calculator_name` field |
| `oridirtuning_calc.depends_on` (internal struct with `stimulus_tuningcurve_id`) | (removed — inherited from `orientation_direction_tuning`) | redundant in did_v1; V_delta does not re-declare an already-inherited dependency |

## Transformations in detail

- **Calculator base.** V_delta introduces a new abstract `calculator` class
  whose superclasses are `base` and `app`. It declares one field
  (`input_parameters`, structure, optional). The required calculator
  identity comes from the inherited `app.app_name` -- there is no
  `calculator.calculator_name` in V_delta, because that field would
  duplicate `app.app_name`. Every `*_calc` schema inherits from
  `calculator` (directly, or via the intermediate abstract `tuning_fit`
  base when the calculator is a tuning fit). `oridirtuning_calc`
  reaches `calculator` (and therefore `app`) through `tuning_fit`.
- **app block migration.** did_v1 calc documents already ship a top-level
  `app` block whose `name` field holds the NDI calculator class identity
  (e.g., `ndi.calc.vis.oridir_tuning`). V_delta renames `app.name ->
  app.app_name` and `app.version -> app.app_version`; the rename is
  applied universally by `did2.convert.universalRenames` to any
  document carrying an `app` block, not just calc docs. The other app
  fields (`url`, `os`, `os_version`, `interpreter`, `interpreter_version`)
  match V_delta verbatim.
- **Inherited dependency.** did_v1 redundantly listed
  `stimulus_tuningcurve_id` as an internal `depends_on` entry even though
  the parent class `orientation_direction_tuning` already declared it.
  V_delta drops the redundancy.

## Default values for new fields

| Field | Default |
|---|---|
| `app.app_name` | derived from v1 `app.name` (the universal rename); never defaulted by the migrator |
| `calculator.input_parameters` | `{}` if v1 had no `input_parameters` |

## Worked example

- **Before (did_v1):** [`NDIcalc-vis-matlab/ndi_common/database_documents/calc/oridirtuning_calc.json`](https://github.com/VH-Lab/NDIcalc-vis-matlab/blob/main/ndi_common/database_documents/calc/oridirtuning_calc.json)
- **After (V_delta):** to be added under `schemas/V_delta/examples/`.

## File handling

No file references. See [`_files.md`](_files.md) for generic rules.

## Open questions

- **TODO-domain:** concrete shape of `input_parameters` when populated by
  real calculators.

## Cross-references

- Parent result type: [`orientation_direction_tuning.md`](./orientation_direction_tuning.md)
- Calculator base: see `stable/calculator.json` and `stable/tuning_fit.json`
