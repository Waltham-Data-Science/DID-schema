# Conversion: did_v1 → V_delta — `speed_tuning_calc`

## Identity

- **V_delta `class_name`:** `speed_tuning_calc`
- **V_delta tier:** `stable`
- **V_delta schema path:** `schemas/V_delta/stable/speed_tuning_calc.json`
- **did_v1 source:** `VH-Lab/NDIcalc-vis-matlab` —
  `ndi_common/schema_documents/calc/speedtuning_calc_schema.json` plus
  `ndi_common/database_documents/calc/speedtuning_calc.json`.
- **Status:** `drafted`

## Summary

A calculator type that computes a `speed_tuning` result and stores the
calculator's own input parameters alongside the inherited result fields.
 The did_v1 name `speedtuning_calc` is normalized to `speed_tuning_calc` to match the snake-cased naming of the result type it inherits from.

## Field mapping

| did_v1 location | V_delta location | Transformation |
|---|---|---|
| `document_class.class_name: "speedtuning_calc"` | `document_class.class_name: "speed_tuning_calc"` | rename (snake-case normalization) |
| `superclasses: [base, speed_tuning]` | `superclasses: [base, speed_tuning]` | identity (inherited fields stay in their declaring classes) |
| `speedtuning_calc.input_parameters` | `speed_tuning_calc.input_parameters` | empty struct → `type: structure` with empty `fields` |
| `speedtuning_calc.depends_on` (internal struct with `stimulus_tuningcurve_id`) | (removed — inherited from `speed_tuning`) | redundant in did_v1; V_delta does not re-declare an already-inherited dependency |

## Transformations in detail

- **Inherited dependency.** did_v1 redundantly listed
  `stimulus_tuningcurve_id` as an internal `depends_on` entry even though
  the parent class `speed_tuning` already declared it. V_delta drops the
  redundancy.

## Default values for new fields

None.

## Worked example

- **Before (did_v1):** [`NDIcalc-vis-matlab/ndi_common/database_documents/calc/speedtuning_calc.json`](https://github.com/VH-Lab/NDIcalc-vis-matlab/blob/main/ndi_common/database_documents/calc/speedtuning_calc.json)
- **After (V_delta):** to be added under `schemas/V_delta/examples/`.

## File handling

No file references. See [`_files.md`](_files.md) for generic rules.

## Open questions

- **TODO-domain:** concrete shape of `input_parameters` when populated by
  real calculators.

## Cross-references

- Parent result type: [`speed_tuning.md`](./speed_tuning.md)
