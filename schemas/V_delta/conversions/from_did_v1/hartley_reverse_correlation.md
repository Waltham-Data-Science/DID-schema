# Conversion: did_v1 → V_delta — `hartley_reverse_correlation`

## Identity

- **V_delta `class_name`:** `hartley_reverse_correlation`
- **V_delta tier:** `stable`
- **V_delta schema path:** `schemas/V_delta/stable/hartley_reverse_correlation.json`
- **did_v1 source:** `VH-Lab/NDIcalc-vis-matlab` —
  `ndi_common/schema_documents/neuro/hartley_reverse_correlation_schema.json`
  plus
  `ndi_common/database_documents/neuro/hartley_reverse_correlation.json`.
- **Status:** `drafted`

## Summary

Reverse-correlation specialized for Hartley basis stimuli. Inherits from
`base` and `reverse_correlation`, adding stimulus-presentation metadata
(M, L_max, K_max, sf_max, fps, colors, on-screen rect), reconstruction
grids, and the spike-time / frame-time / Hartley-index arrays used to
compute the kernel.

## Field mapping

| did_v1 location | V_delta location | Transformation |
|---|---|---|
| `class_name: "hartley_reverse_correlation"` | same | identity |
| `superclasses: [base, reverse_correlation]` | same | identity |
| `hartley_reverse_correlation.stimulus_properties.{M,L_max,K_max,sf_max,fps}` | same | scalar `double` |
| `hartley_reverse_correlation.stimulus_properties.{color_high,color_low,rect}` | same | `matrix<double>` |
| `hartley_reverse_correlation.reconstruction_properties.{T_coords,X_coords,Y_coords}` | same | `matrix<double>` |
| `hartley_reverse_correlation.spiketimes` | same | `matrix<double>` |
| `hartley_reverse_correlation.frameTimes` | same | `matrix<double>` (consider renaming to `frame_times` in a follow-up) |
| `hartley_reverse_correlation.hartley_numbers` | same | `matrix<double>` (integer-valued; consider integer subtype) |

## Transformations in detail

- **Field name `frameTimes`** is preserved verbatim from did_v1 even
  though it is camelCase rather than snake_case. The V_gamma SPEC
  requires snake_case for field names, so this is a known
  spec-conformance issue that should be addressed by a follow-up rename
  to `frame_times`. The conversion engine should support reading either
  during the transition.
- **`hartley_numbers` semantics.** Indexed in parallel with `frameTimes`
  — each entry is the Hartley basis index of the frame presented at the
  corresponding time.

## Default values for new fields

The did_v1 template carries non-empty defaults for several
`stimulus_properties` fields (e.g., `L_max: 20`, `fps: 10`, `rect: [0, 0,
800, 600]`). V_delta preserves those as the `default_value` of each
field.

## Worked example

- **Before (did_v1):** [`NDIcalc-vis-matlab/ndi_common/database_documents/neuro/hartley_reverse_correlation.json`](https://github.com/VH-Lab/NDIcalc-vis-matlab/blob/main/ndi_common/database_documents/neuro/hartley_reverse_correlation.json)
- **After (V_delta):** to be added under `schemas/V_delta/examples/`.

## File handling

No direct file references on this class. Inherited `ngrid` from
`reverse_correlation` carries the kernel data. See [`_files.md`](_files.md)
for generic rules.

## Open questions

- **TODO-domain:** rename `frameTimes` to `frame_times` for snake-case
  compliance, with a back-compat read path during the transition.
- **TODO-domain:** introduce an integer subtype for `hartley_numbers`
  rather than storing as `double`.
- **TODO-domain:** ontology terms for `stimulus_properties` fields
  (cycles per degree, frames per second, RGB color).

## Cross-references

- Parent: [`reverse_correlation.md`](reverse_correlation.md)
- Calculator: [`hartley_calc.md`](hartley_calc.md)
- General file-handling rules: [`_files.md`](_files.md)
