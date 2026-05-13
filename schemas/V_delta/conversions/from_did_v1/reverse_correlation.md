# Conversion: did_v1 → V_delta — `reverse_correlation`

## Identity

- **V_delta `class_name`:** `reverse_correlation`
- **V_delta tier:** `stable`
- **V_delta schema path:** `schemas/V_delta/stable/reverse_correlation.json`
- **did_v1 source:** `VH-Lab/NDIcalc-vis-matlab` —
  `ndi_common/schema_documents/neuro/reverse_correlation_schema.json` plus
  `ndi_common/database_documents/neuro/reverse_correlation.json`.
- **Status:** `drafted`

## Summary

Generic reverse-correlation result type. Inherits from `base` and `ngrid`
(an existing V_delta type) — the n-dimensional grid carries the
reverse-correlation kernel itself, and this class adds the metadata
describing the method and axis labels.

## Field mapping

| did_v1 location | V_delta location | Transformation |
|---|---|---|
| `class_name: "reverse_correlation"` | same | identity |
| `superclasses: [base, ngrid]` | same | identity |
| (top-level) `depends_on: [element_id, stimulus_presentation_id]` | top-level `depends_on` | identity |
| `reverse_correlation.method` | same | `char` (candidate for promotion to `ontology_term`) |
| `reverse_correlation.dimension_labels` | same | `char` (comma-separated axis names; consider splitting into a `matrix<char>` in a follow-up) |

## Transformations in detail

- Minimal structural change. The class is a thin metadata layer over the
  inherited `ngrid`; the kernel itself lives in the `ngrid` block.

## Default values for new fields

None.

## Worked example

- **Before (did_v1):** [`NDIcalc-vis-matlab/ndi_common/database_documents/neuro/reverse_correlation.json`](https://github.com/VH-Lab/NDIcalc-vis-matlab/blob/main/ndi_common/database_documents/neuro/reverse_correlation.json)
- **After (V_delta):** to be added under `schemas/V_delta/examples/`.

## File handling

No direct file references on this class; the inherited `ngrid` carries
the kernel data. See [`_files.md`](_files.md) for the generic rules that
govern how the inherited file references migrate.

## Open questions

- **TODO-domain:** is `dimension_labels` best kept as a comma-separated
  `char` (preserves the v1 shape), promoted to `matrix<char>` of axis
  names, or constrained by enumeration?
- **TODO-domain:** controlled vocabulary for `method` — likely candidates
  include `spike-triggered average`, `STC`, `MID`. Promote to
  `ontology_term` once a CURIE is identified.

## Cross-references

- Inherited type: `ngrid` (existing V_delta type — not migrated by this
  PR; conversion doc not required here)
- Specialization: [`hartley_reverse_correlation.md`](hartley_reverse_correlation.md)
- General file-handling rules: [`_files.md`](_files.md)
