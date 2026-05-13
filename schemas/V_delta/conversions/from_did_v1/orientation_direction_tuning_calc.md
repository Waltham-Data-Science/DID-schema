# Conversion: did_v1 → V_delta — `orientation_direction_tuning_calc`

## Identity

- **V_delta `class_name`:** `orientation_direction_tuning_calc`
- **V_delta tier:** `stable`
- **V_delta schema path:** `schemas/V_delta/stable/orientation_direction_tuning_calc.json`
- **did_v1 source:** `VH-Lab/NDIcalc-vis-matlab` —
  `ndi_common/schema_documents/calc/oridirtuning_calc_schema.json` plus
  `ndi_common/database_documents/calc/oridirtuning_calc.json`.
- **Status:** `drafted`

## Summary

A calculator type that computes a `orientation_direction_tuning` result and stores the
calculator's own input parameters alongside the inherited result fields.
 The did_v1 name `oridirtuning_calc` is normalized to `orientation_direction_tuning_calc` to match the snake-cased naming of the result type it inherits from.

## Field mapping

| did_v1 location | V_delta location | Transformation |
|---|---|---|
| `document_class.class_name: "oridirtuning_calc"` | `document_class.class_name: "orientation_direction_tuning_calc"` | rename (snake-case normalization) |
| `superclasses: [base, orientation_direction_tuning]` | `superclasses: [base, orientation_direction_tuning]` | identity (inherited fields stay in their declaring classes) |
| `oridirtuning_calc.input_parameters` | `orientation_direction_tuning_calc.input_parameters` | empty struct → `type: structure` with empty `fields` |
| `oridirtuning_calc.depends_on` (internal struct with `stimulus_tuningcurve_id`) | (removed — inherited from `orientation_direction_tuning`) | redundant in did_v1; V_delta does not re-declare an already-inherited dependency |

## Transformations in detail

- **Inherited dependency.** did_v1 redundantly listed
  `stimulus_tuningcurve_id` as an internal `depends_on` entry even though
  the parent class `orientation_direction_tuning` already declared it. V_delta drops the
  redundancy.

## Default values for new fields

None.

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
