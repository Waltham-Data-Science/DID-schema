# Conversion: did_v1 → V_delta — `contrast_tuning`

## Identity

- **V_delta `class_name`:** `contrast_tuning`
- **V_delta tier:** `stable`
- **V_delta schema path:** `schemas/V_delta/stable/contrast_tuning.json`
- **did_v1 source:** `VH-Lab/NDIcalc-vis-matlab` —
  `ndi_common/schema_documents/vision/contrast_tuning_schema.json` plus
  the paired template
  `ndi_common/database_documents/vision/contrast_tuning.json`.
- **Status:** `drafted`

## Summary

This is the **result type** for empirical and fit-derived contrast tuning
of a visual element. The class is independent of how the tuning was
computed; calculator types (e.g., `contrast_tuning_calc`) inherit from it.

Conversion is primarily a structural reshaping: did_v1 declares every
top-level grouping as `type: "structure"` with no inner declarations, so
all field-level typing in V_delta is recovered from the paired db_doc
template (the schema file alone is insufficient).

## Field mapping

| did_v1 location | V_delta location | Transformation |
|---|---|---|
| `contrast_tuning.properties.response_units` | `contrast_tuning.properties.response_units` | type `0` placeholder → `char` (per user decision) |
| `contrast_tuning.properties.response_type` | `contrast_tuning.properties.response_type` | identity (char) |
| `contrast_tuning.tuning_curve.contrast` | `contrast_tuning.tuning_curve.contrast` | scalar placeholder → `matrix<double>` |
| `contrast_tuning.tuning_curve.{mean,stddev,stderr}` | same | scalar placeholders → `matrix<double>` |
| `contrast_tuning.tuning_curve.individual` | same | empty struct in v1 → `matrix<double>` (rows index sampled points along the tuning axis; columns index trials) |
| `contrast_tuning.tuning_curve.{control_stddev,control_stderr}` | same | scalar placeholder → `matrix<double>` |
| `contrast_tuning.significance.{visual_response_anova_p,across_stimuli_anova_p}` | same | identity (double) |
| `contrast_tuning.fitless.interpolated_c50` | same | identity (double) |
| `contrast_tuning.fit.naka_rushton_RB_*` (9 fields) | `contrast_tuning.fit.naka_rushton_rb.*` | regrouped into nested struct + snake-cased; scalar metrics → `double`, array metrics → `matrix<double>`; `sensitivity` is a 1x10 `matrix<double>` (see below) |
| `contrast_tuning.fit.naka_rushton_RBN_*` | `contrast_tuning.fit.naka_rushton_rbn.*` | same |
| `contrast_tuning.fit.naka_rushton_RBNS_*` | `contrast_tuning.fit.naka_rushton_rbns.*` | same |
| (top-level) `depends_on: [element_id, stimulus_tuningcurve_id]` | top-level `depends_on` array | identity (named refs declared on the schema, value carried on document instances) |

## Transformations in detail

- **Naka-Rushton fit grouping.** did_v1 stores the three model variants
  (RB, RBN, RBNS) as 27 sibling fields with `naka_rushton_<VARIANT>_<metric>`
  names. V_delta groups them under a `fit` structure containing three
  sub-structures `naka_rushton_rb`, `naka_rushton_rbn`, `naka_rushton_rbns`,
  each carrying nine identically-named metrics. Migration is a name split
  on the second underscore (after `naka_rushton_`).
- **Scalar metrics stored as 1-element arrays.** Several did_v1 fields
  (e.g., `naka_rushton_RB_pref`, `_empirical_c50`, `_r2`,
  `_relative_max_gain`, `_saturation_index`) appear as `[0]` in the
  template. The conversion *unwraps* these to plain `double` scalars in
  V_delta — the V_delta schema declares them as `type: double` /
  `mustBeScalar: true`. Migration tools must extract `arr[0]` and verify
  the array has exactly one element.
- **`sensitivity` is genuinely a vector, not a scalar.** The did_v1
  template stores `naka_rushton_<VARIANT>_sensitivity` as `[0]` like the
  other scalar metrics, but the user-supplied field documentation
  describes it as a 1x10 vector: for each i in 1..10, an inverse-threshold
  sensitivity at i standard deviations of the control response. V_delta
  declares `sensitivity` as `matrix<double>` in all three Naka-Rushton
  blocks (do **not** unwrap to scalar). Migration tools must preserve the
  full vector rather than extracting `arr[0]`.
- **Snake-case.** Variant tags are lowercased (`RB` → `rb`).
- **RB-specific `saturation_index`.** The RB form has 2 free parameters
  with no saturation-controlling term, so `saturation_index` is always 0
  under the RB fit. V_delta encodes that note in the field documentation
  on `naka_rushton_rb.saturation_index`.

## Default values for new fields

V_delta does not introduce new required fields on this class beyond what
existed in did_v1. The planned global `schema_version` field will land via
a follow-up PR that updates `base`; once it does, migrated `contrast_tuning`
documents will carry `schema_version: "V_delta"` inherited from base.

## Worked example

The before-and-after pair is large; rather than inline the entire document,
see:

- **Before (did_v1):** [`NDIcalc-vis-matlab/ndi_common/database_documents/vision/contrast_tuning.json`](https://github.com/VH-Lab/NDIcalc-vis-matlab/blob/main/ndi_common/database_documents/vision/contrast_tuning.json)
- **After (V_delta):** an example will be added to
  `schemas/V_delta/examples/contrast_tuning_minimal.json` in a follow-up
  PR once the migration engine produces one.

## File handling

This document type does not reference files. The generic file-handling
rules in [`_files.md`](_files.md) do not apply.

## Open questions


- **TODO-domain:** ontology terms. Most field-level `ontology` slots are
  `null` pending a sweep through the V_gamma CURIE registry. Candidate
  CURIE families: `stato:` for statistical measures, `iao:` for data
  items, `efo:` / `obi:` for stimulus parameters.

## Cross-references

- General file-handling rules: [`_files.md`](_files.md)
- Calculator that produces this result type: `contrast_tuning_calc` (see
  [`contrast_tuning_calc.md`](contrast_tuning_calc.md))
- Related contrast analysis: `contrast_sensitivity_calc` (see
  [`contrast_sensitivity_calc.md`](contrast_sensitivity_calc.md))
