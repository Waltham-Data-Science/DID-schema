# Conversion: did_v1 → V_delta — `spatial_frequency_tuning`

## Identity

- **V_delta `class_name`:** `spatial_frequency_tuning`
- **V_delta tier:** `stable`
- **V_delta schema path:** `schemas/V_delta/stable/spatial_frequency_tuning.json`
- **did_v1 source:** `VH-Lab/NDIcalc-vis-matlab` —
  `ndi_common/schema_documents/vision/spatial_frequency_tuning_schema.json` plus
  the paired template
  `ndi_common/database_documents/vision/spatial_frequency_tuning.json`.
- **Status:** `drafted`

## Summary

Result type for empirical and fit-derived tuning along spatial
frequencies (cycles per degree). Independent of the calculator that
produced it; calculators (e.g., `spatial_frequency_tuning_calc`) inherit
from this class.

Conversion is primarily a structural reshaping: did_v1 declares each
top-level grouping as an unconstrained `type: "structure"`, so all
field-level typing in V_delta is recovered from the paired db_doc
template.

## Field mapping

| did_v1 location | V_delta location | Transformation |
|---|---|---|
| `spatial_frequency_tuning.properties.{response_units,response_type}` | same | `char` types (response_units per user decision) |
| `spatial_frequency_tuning.tuning_curve.spatial_frequency` | same | scalar placeholder → `matrix<double>` |
| `spatial_frequency_tuning.tuning_curve.{mean,stddev,stderr}` | same | scalar placeholder → `matrix<double>` |
| `spatial_frequency_tuning.tuning_curve.individual` | same | empty struct in v1 → `matrix<double>` (rows index spatial frequencies; columns index trials) |
| `spatial_frequency_tuning.tuning_curve.{control_stddev,control_stderr}` | same | scalar placeholder → `matrix<double>` |
| `spatial_frequency_tuning.significance.{visual_response_anova_p,across_stimuli_anova_p}` | same | identity (double) |
| `spatial_frequency_tuning.fitless.{L50,Pref,H50,low_pass_index,high_pass_index,bandwidth}` | same (snake-cased) | identity (double); semantics documented per-field |
| `spatial_frequency_tuning.fit_dog` | same | nested struct; `parameters` is `matrix<double>` (DoG `[b a1 b1 a2 b2]`), `values` / `fit` are `matrix<double>`, scalar metrics `{r2, l50, pref, h50, bandwidth}` are `double` |
| `spatial_frequency_tuning.fit_movshon` | same | nested struct; Movshon 2005 fit `[k f fc B]` |
| `spatial_frequency_tuning.fit_movshon_c` | same | nested struct; Movshon 2005 fit with constant term `[k f fc B C]` |
| `spatial_frequency_tuning.fit_spline` | same | nested struct; no `parameters` field, no `r2` field (the spline is non-parametric) |
| `spatial_frequency_tuning.fit_sgauss` | same | nested struct; skewed-Gaussian fit |
| `spatial_frequency_tuning.abs` | same | mirror of all preceding blocks computed on the absolute value of responses; empty in did_v1 |
| (top-level) `depends_on: [element_id, stimulus_tuningcurve_id]` | top-level `depends_on` | identity |

## Transformations in detail

- **Snake-case everywhere.** did_v1 field names like `L50` / `Pref` /
  `H50` / `R2` are lowercased to `l50` / `pref` / `h50` / `r2` to comply
  with V_gamma's snake_case rule.
- **`values` and `fit` semantics, clarified.** In each fit block the
  did_v1 template has two same-shape arrays named `values` and `fit`.
  The user-supplied field documentation establishes the convention that
  **`values` is the X axis** (the spatial frequencies at which the fit
  is evaluated, used to draw a filled-in curve) and **`fit` is the Y
  axis** (the response value of the fit at each X). An earlier draft of
  this schema described them in the opposite sense; that has been
  corrected.
- **Mixed scalar/array fields in did_v1 are normalized.** For example,
  `fit_movshon.values` is declared as scalar `0` while `fit_dog.values`
  is `[0]`; V_delta unifies these as `matrix<double>` per user direction
  ("double arrays for this").
- **Per-fit parameter vectors are documented.** Each fit block's
  `parameters` documentation now records the canonical parameter layout
  (DoG `[b a1 b1 a2 b2]`, Movshon 2005 `[k f fc B]`, Movshon 2005 with
  constant `[k f fc B C]`).
- **Fitless metrics carry semantic details.** `l50` / `pref` / `h50`
  encode the behaviour at boundary conditions (-Inf / +Inf when the
  half-max point is never crossed); `low_pass_index` and
  `high_pass_index` document the rectification rule and the 0..1 / NaN
  value range; `bandwidth` documents the `log2(h50 / l50)` definition
  and the Inf propagation.
- **`abs` block** is a documented mirror of all preceding blocks,
  recomputed on absolute-valued responses. Empty in did_v1; V_delta
  retains it as an empty structure pending domain confirmation.

## Default values for new fields

None added by this PR. The planned global `schema_version` field will
land via a follow-up that updates `base`.

## Worked example

- **Before (did_v1):** [`NDIcalc-vis-matlab/ndi_common/database_documents/vision/spatial_frequency_tuning.json`](https://github.com/VH-Lab/NDIcalc-vis-matlab/blob/main/ndi_common/database_documents/vision/spatial_frequency_tuning.json)
- **After (V_delta):** to be added under `schemas/V_delta/examples/`.

## File handling

No file references. See [`_files.md`](_files.md) for generic rules.

## Open questions

- **TODO-domain:** ontology terms for fit-parameter fields.
- **TODO-domain:** the `abs` block — concrete sub-field shape if and
  when calculators start populating it.

## Cross-references

- Calculator that produces this result type:
  [`spatial_frequency_tuning_calc.md`](./spatial_frequency_tuning_calc.md)
- Sibling result type with identical structure:
  [`temporal_frequency_tuning.md`](./temporal_frequency_tuning.md)
- General file-handling rules: [`_files.md`](_files.md)
