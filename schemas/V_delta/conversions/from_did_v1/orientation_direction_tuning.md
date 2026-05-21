# Conversion: did_v1 → V_delta — `orientation_direction_tuning`

## Identity

- **V_delta `class_name`:** `orientation_direction_tuning`
- **V_delta tier:** `stable`
- **V_delta schema path:** `schemas/V_delta/stable/orientation_direction_tuning.json`
- **did_v1 source:** `VH-Lab/NDIcalc-vis-matlab` —
  `ndi_common/schema_documents/stimulus/vision/oridir/orientation_direction_tuning_schema.json`
  plus the paired template
  `ndi_common/database_documents/stimulus/vision/oridir/orientation_direction_tuning.json`.
- **Status:** `drafted`

## Summary

This is the **result type** for empirical and fit-derived orientation /
direction tuning of a visual element. The class is independent of how the
tuning was computed; calculator types (e.g.,
`oridirtuning_calc`) inherit from it.

Conversion is primarily a structural reshaping: did_v1 declares every
top-level grouping (`properties`, `tuning_curve`, `significance`, `vector`,
`fit`) as `type: "structure"` with no inner declarations, so all
field-level typing in V_delta is recovered from the paired db_doc template
(the schema file alone is insufficient).

## Field mapping

| did_v1 location | V_delta location | Transformation |
|---|---|---|
| `orientation_direction_tuning.properties.coordinates` | same | char placeholder → `char` with enum `{compass, cartesian}` |
| `orientation_direction_tuning.properties.response_units` | same | type `0` placeholder → `char` (per user decision) |
| `orientation_direction_tuning.properties.response_type` | same | identity (char) |
| `orientation_direction_tuning.tuning_curve.direction` | same | scalar placeholder → `matrix<double>` (1xN direction angles in degrees) |
| `orientation_direction_tuning.tuning_curve.{mean,stddev,stderr}` | same | scalar placeholders → `matrix<double>` |
| `orientation_direction_tuning.tuning_curve.individual` | same | empty struct in v1 → `matrix<double>` (rows index directions; columns index trials) |
| `orientation_direction_tuning.tuning_curve.raw_individual` | same | empty struct in v1 → `matrix<double>` (rows index directions; columns index trials; no blank subtraction / normalization) |
| `orientation_direction_tuning.tuning_curve.control_individual` | same | empty struct in v1 → `matrix<double>` (per-trial control responses) |
| `orientation_direction_tuning.significance.{visual_response_anova_p,across_stimuli_anova_p}` | same | identity (double) |
| `orientation_direction_tuning.vector.{circular_variance,direction_circular_variance,hotelling2test,direction_hotelling2test,dot_direction_significance}` | same | identity (double); semantics documented per-field |
| `orientation_direction_tuning.vector.{orientation_preference,direction_preference}` | same | scalar placeholder → `double` (angle in degrees of the vector-sum preference) |
| `orientation_direction_tuning.fit.double_gaussian_parameters` | same | `[0]` placeholder → `matrix<double>` (vector of length 5: `[Rsp Rp theta_pref sigma Rn]`) |
| `orientation_direction_tuning.fit.double_gaussian_fit_angles` | same | `[0]` placeholder → `matrix<double>` (angle axis, typically 0:359) |
| `orientation_direction_tuning.fit.double_gaussian_fit_values` | same | `[0]` placeholder → `matrix<double>` (fit values at each angle) |
| `orientation_direction_tuning.fit.orientation_preferred_orthogonal_ratio` | same | `[0]` 1-element array placeholder → scalar `double` |
| `orientation_direction_tuning.fit.direction_preferred_null_ratio` | same | `[0]` 1-element array placeholder → scalar `double` |
| `orientation_direction_tuning.fit.orientation_preferred_orthogonal_ratio_rectified` | same | `[0]` 1-element array placeholder → scalar `double` |
| `orientation_direction_tuning.fit.direction_preferred_null_ratio_rectified` | same | `[0]` 1-element array placeholder → scalar `double` |
| `orientation_direction_tuning.fit.orientation_angle_preference` | same | identity (double) |
| `orientation_direction_tuning.fit.direction_angle_preference` | same | identity (double) |
| `orientation_direction_tuning.fit.hwhh` | same | identity (double) |
| (top-level) `depends_on: [element_id, stimulus_tuningcurve_id]` | top-level `depends_on` array | identity (named refs declared on the schema, document_id carried on document instances) |

## Transformations in detail

- **`coordinates` enum.** did_v1 stores `coordinates` as a free-form
  string placeholder. V_delta constrains it to the documented vocabulary
  `{"compass", "cartesian"}`. Migration tools must lower-case any
  legacy capitalisations.
- **Scalar metrics stored as 1-element arrays.** Four fit-derived ratio
  fields appear as `[0]` in the did_v1 template:
  `orientation_preferred_orthogonal_ratio`,
  `direction_preferred_null_ratio`,
  `orientation_preferred_orthogonal_ratio_rectified`,
  `direction_preferred_null_ratio_rectified`. The conversion *unwraps*
  these to plain `double` scalars in V_delta — the V_delta schema declares
  them as `type: double` / `mustBeScalar: true`. Migration tools must
  extract `arr[0]` and verify the array has exactly one element.
- **Vector-space preferences.** `vector.orientation_preference` and
  `vector.direction_preference` are stored as scalar angles (in degrees)
  giving the argument of the orientation- and direction-space vector
  sums respectively. Tools that represent these as complex numbers
  internally must convert to angle-in-degrees on output.
- **Trial-axis convention.** For the per-trial matrices (`individual`,
  `raw_individual`, `control_individual`) V_delta documents the
  row-vs-column convention explicitly: rows index sampled directions,
  columns index trials. did_v1 did not commit to a layout.

## Default values for new fields

V_delta does not introduce new required fields on this class beyond what
existed in did_v1. The planned global `schema_version` field will land via
a follow-up PR that updates `base`; once it does, migrated
`orientation_direction_tuning` documents will carry
`schema_version: "V_delta"` inherited from base.

## Worked example

The before-and-after pair is large; rather than inline the entire document,
see:

- **Before (did_v1):** [`NDIcalc-vis-matlab/ndi_common/database_documents/stimulus/vision/oridir/orientation_direction_tuning.json`](https://github.com/VH-Lab/NDIcalc-vis-matlab/blob/main/ndi_common/database_documents/stimulus/vision/oridir/orientation_direction_tuning.json)
- **After (V_delta):** an example will be added to
  `schemas/V_delta/examples/orientation_direction_tuning_minimal.json` in a
  follow-up PR once the migration engine produces one.

## File handling

This document type does not reference files. The generic file-handling
rules in [`_files.md`](_files.md) do not apply.

## Open questions

- **TODO-domain:** ontology terms. Most field-level `ontology` slots are
  `null` pending a sweep through the V_gamma CURIE registry. Candidate
  CURIE families: `stato:` for the ANOVA and Hotelling p-values,
  `iao:` for data items, `efo:` / `obi:` for the stimulus-direction axis.
- **TODO-domain:** confirm whether `vector.orientation_preference` and
  `vector.direction_preference` should be kept as scalar angles (current
  V_delta choice) or expanded to a 2-element `[real, imag]` matrix to
  preserve vector-sum magnitude alongside the angle.

## Cross-references

- General file-handling rules: [`_files.md`](_files.md)
- Calculator that produces this result type: `oridirtuning_calc` (see
  [`oridirtuning_calc.md`](oridirtuning_calc.md))
