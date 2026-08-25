# Conversion: did_v1 → V_eta — `contrast_tuning_calc`

## Identity

- **V_eta `class_name`:** `contrast_tuning_calc`
- **V_eta tier:** `stable`
- **V_eta schema path:** `schemas/V_eta/stable/contrast_tuning_calc.json`
- **did_v1 source:** `VH-Lab/NDIcalc-vis-matlab` —
  `ndi_common/schema_documents/calc/contrasttuning_calc_schema.json` plus
  `ndi_common/database_documents/calc/contrasttuning_calc.json`.
- **Status:** `drafted`

## Summary

A calculator type that computes a `contrast_tuning` result and stores the
calculator's own input parameters alongside the inherited result fields.

The did_v1 name `contrasttuning_calc` is normalized to `contrast_tuning_calc`
in V_eta to match the snake-cased naming of the result type it inherits
from.

## Field mapping

| did_v1 location | V_eta location | Transformation |
|---|---|---|
| `document_class.class_name: "contrasttuning_calc"` | `document_class.class_name: "contrast_tuning_calc"` | rename (snake-case normalization) |
| `superclasses: [base, contrast_tuning]` | `superclasses: [base, contrast_tuning]` | identity (inherited fields stay in their declaring classes) |
| `contrasttuning_calc.input_parameters` | `contrast_tuning_calc.input_parameters` | empty struct → `type: structure` with empty `fields`; calculators may extend in subclasses |
| `contrasttuning_calc.depends_on` (internal struct with `stimulus_tuningcurve_id`) | (removed — inherited from `contrast_tuning`) | the inner `depends_on` referenced `stimulus_tuningcurve_id` which is already declared on `contrast_tuning`. V_eta does not re-declare it. |

## Transformations in detail

- **Class name normalization.** `contrasttuning_calc` → `contrast_tuning_calc`.
  Migration tools must rewrite `document_class.class_name` and the
  enclosing block key in document instances.
- **Inherited dependency.** did_v1 redundantly listed `stimulus_tuningcurve_id`
  as an internal `depends_on` entry even though the parent class already
  declared it. V_eta drops the redundancy; the dependency exists
  exactly once, on `contrast_tuning`.

## Default values for new fields

None — this class adds only `input_parameters`, which is an unconstrained
empty struct.

## Worked example

- **Before (did_v1):** [`NDIcalc-vis-matlab/ndi_common/database_documents/calc/contrasttuning_calc.json`](https://github.com/VH-Lab/NDIcalc-vis-matlab/blob/main/ndi_common/database_documents/calc/contrasttuning_calc.json)
- **After (V_eta):** to be added under `schemas/V_eta/examples/` once
  the migration engine produces one.

## File handling

No file references. See [`_files.md`](_files.md) for generic rules.

## Open questions

- **TODO-domain:** what *should* `input_parameters` carry in practice?
  The did_v1 template leaves it empty. Likely candidates: the
  `response_type` choice (mean/peak/F1), windowing parameters, baseline
  policy. Worth aligning with `contrast_sensitivity_calc.input_parameters`
  if there is overlap.

## Cross-references

- Parent result type: [`contrast_tuning.md`](contrast_tuning.md)
- Related calculator: [`contrast_sensitivity_calc.md`](contrast_sensitivity_calc.md)
