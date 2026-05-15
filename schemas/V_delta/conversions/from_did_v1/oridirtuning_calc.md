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
| `superclasses: [base, orientation_direction_tuning]` | `superclasses: [base, orientation_direction_tuning, tuning_fit]` | added `tuning_fit` (and transitively `calculator`) so the calculator interface lives on the shared base, not on each subclass |
| `oridirtuning_calc.input_parameters` | `calculator.input_parameters` | moved up to the abstract `calculator` base (field is now inherited, not declared per-subclass) |
| (absent in did_v1) | `calculator.calculator_name: "ndi.calc.vis.oridir_tuning"` | the migrator populates this required field from the v1 class name; the value identifies the concrete NDI calculator class |
| `oridirtuning_calc.depends_on` (internal struct with `stimulus_tuningcurve_id`) | (removed — inherited from `orientation_direction_tuning`) | redundant in did_v1; V_delta does not re-declare an already-inherited dependency |

## Transformations in detail

- **Calculator base.** V_delta introduces a new abstract `calculator` class
  declaring `calculator_name` (required, char) and `input_parameters`
  (structure). Every `*_calc` schema inherits from it (directly, or via the
  intermediate abstract `tuning_fit` base when the calculator is a tuning
  fit). `oridirtuning_calc` reaches `calculator` through `tuning_fit`.
- **calculator_name origin.** did_v1 calc documents do not carry a
  `calculator_name` field; the v1 class name was the calculator identity.
  The migrator hard-codes the V_delta value
  `ndi.calc.vis.oridir_tuning` for every document migrating out of v1
  `oridirtuning_calc`. The lookup table for all calc classes lives in the
  did-matlab migrator under `+did2.+convert.+migrators.+_calc/`.
- **Inherited dependency.** did_v1 redundantly listed
  `stimulus_tuningcurve_id` as an internal `depends_on` entry even though
  the parent class `orientation_direction_tuning` already declared it.
  V_delta drops the redundancy.

## Default values for new fields

| Field | Default |
|---|---|
| `calculator.calculator_name` | `"ndi.calc.vis.oridir_tuning"` (set by the migrator; cannot be defaulted by the schema because the value is per-subclass) |
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
