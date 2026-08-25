# V_eta — the tuning-composite model (DECIDED; build deferred)

*Worked design for how V_eta represents tuning curves and their fits, decided in the audit
walkthrough (R2/R3). **All decisions below are FINAL; the BUILD is deferred** — batched with
the other walkthrough decisions (image/array). When building, this doc is the spec.
Cross-refs: `V_eta_tenets.md` (T3/T8/T10/T12), `V_eta_tenet_audit.md` (R2/R3),
`V_eta_subject_calculation_plan.md` (the calculator fold).*

## The one-line model

> **There is ONE tuning value: a `tuning_curve` `data_type` — a response-vs-independent-
> variable curve. The independent variable is a `variable` (T11), not a name suffix. The fits
> are an ARRAY of `model_fit` entries, each identified by a controlled `model` term (T8) with
> a coefficient block — not a class per fit; the empirical summary scalars (circular variance,
> ANOVA p, c50/pref/bandwidth) stay TYPED, queryable fields. The six overlapping v1 classes and
> five fit shapes collapse to `tuning_curve` + `tuning_curve_calculation` (one leaf).**

## What was in the v1 classes (the grounding)

Six overlapping classes, one shared curve, five genuinely-different fits:

| v1 class | shared core | the distinct part |
|---|---|---|
| `stimulus_tuningcurve` (raw) | flat `independent_variable_label/value`, `response_mean/stddev/stderr`, `individual_responses_*`, `control_*` | *(none — the raw curve)* |
| `orientation_direction_tuning` | `properties`, `tuning_curve`, `significance` | `vector` (circular variance, pref, Hotelling) + `fit` = **double-gaussian** |
| `contrast_tuning` | ″ | `fit` = **Naka-Rushton** (rb/rbn/rbns) + fitless `interpolated_c50` |
| `spatial_frequency_tuning` | ″ | `fit_dog / fit_movshon / fit_spline / fit_gausslog` + fitless (l50/pref/h50/bandwidth) |
| `temporal_frequency_tuning` | ″ | same DoG/Movshon/spline family |
| `speed_tuning` | ″ | `fit` = **Priebe** + `fit_no_speed / fit_fullspeed` |

The curve (`{independent-variable axis, response mean/stddev/stderr, individuals, control}`)
is identical in all six; only the fitted model differs.

## Decisions (final)

1. **R3 — ONE `tuning_curve` `data_type` composite** (T12 look-alike collapse). Fields:
   - `variable` (ontology_term, T8) — the independent variable the curve is over
     (orientation / contrast / spatial_frequency / temporal_frequency / speed). This is the
     `subject_statement.variable`, **not** a name suffix (T11) — so we do NOT mint
     `orientation_tuning_curve` / `contrast_tuning_curve` / … as separate types.
   - `independent_values` (matrix) — the axis samples.
   - `response_mean`, `response_stddev`, `response_stderr` (matrix) — per-sample response.
   - `individual_responses` (matrix) — trial-level responses (real/imaginary preserved where
     present).
   - `control_response` (structure) — the flat `control_*` block.
   - `response_units` (char).
   - `model_fit` (structure**[]**, optional) — decision 2. **An ARRAY** (a curve may carry
     several co-existing fits).
   - **typed, queryable metric sub-blocks** for the empirical/fitless summary scalars, named by
     content (NAMING PASS — final): **`significance`** (visual_response / across-stimuli ANOVA
     p — keep, it's meaningful); **`circular_statistics`** (was v1 `vector` — circular_variance,
     orientation/direction preference, Hotelling test); **`interpolated_values`** (was v1
     `fitless` — c50, l50, h50, pref, bandwidth, low/high-pass index). **Typed, `queryable:
     true` fields — NOT a `{name,value}` bag, and NOT one `derived_summary` bag** (that name
     failed T13's "predict the content" test and overloaded "derived"; killed).

2. **R2 — `model_fit` is an ARRAY of typed fits; the summary scalars stay typed & queryable**
   (the re-audit fix; revises the earlier "single flexible bag, option A"). Two defects the
   fresh-eyes audit caught in the first draft, now corrected:
   - **`model_fit` MUST be `structure[]` (an array).** `spatial_frequency_tuning` and
     `temporal_frequency_tuning` each carry **five co-existing fits** (`fit_dog`,
     `fit_movshon`, `fit_movshon_c`, `fit_spline`, `fit_gausslog`); `speed_tuning` carries
     three. A single `model_fit` slot would silently drop all but one. Each array entry:
     `{ model (ontology_term, T8 — double_gaussian | naka_rushton | difference_of_gaussians |
     movshon | spline | gausslog | priebe | …; extend the value_set, not the class list),
     coefficients (the fit params), goodness (r²/residual) }`. **NAMING PASS (final): `model`**
     (bare bound term, matching the `color_model` convention — NOT `model_name`, whose `_name`
     suffix reads as a free string); **`coefficients`** (NOT `parameters` — a T13-flagged v1
     smell); metric sub-blocks `significance` / `circular_statistics` / `interpolated_values`.
   - **The queryable summary scalars stay TYPED fields, not name/value bags.** In the shipped
     schemas, `vector.circular_variance`, `significance.visual_response_anova_p`,
     `fitless.pref/l50/bandwidth`, `fit_dog.r2` are all `queryable: true`. Flattening them into
     an unordered `{name,value}` array would make them non-queryable — a real regression
     (scientists filter on exactly these: "circular_variance < 0.5 AND anova_p < 0.01"). So
     they remain typed, queryable fields (decision 1's metrics block). This was the earlier
     draft's mistake (it logged only "less self-validating" and missed the query regression).
   - **`vector`/`significance` are NOT `model_fit`.** They are empirical/circular-statistics
     summaries of the measured curve, not fitted models — labeling them `model_fit` would be a
     false stance-name (T13). They live in the typed metrics block.
   - **T12 note:** distinguishing fits by a controlled `model` term + a coefficient block (not
     a class per fit) is still the parsimony choice; the array + typed-summary shape keeps
     per-model queryability without minting `*_fit` classes.

3. **T10 — ONE `tuning_curve_calculation` leaf** (id-preserving 1→1 fold), NOT five
   `*_tuning_calculation` leaves. `tuning_curve_calculation` = `subject_calculation` +
   `tuning_curve` (result composite carrying its `model_fit`). Every v1 tuning-calculator
   output folds into it via `migrators_j.private.jCalculation` (id- AND deps-preserved;
   `input_parameters` → `method_parameters`; `software_id` per R1; `input` →
   `derived_from_1`). Because the id is preserved and `must_refer` is existence-only,
   downstream `*_id` refs resolve → 0 orphans (the T10 invariant).

4. **`stimulus_tuningcurve` IS the raw `tuning_curve`** (R3) — the pre-calculator-framework
   curve with no `model_fit`. It does not re-declare the shape; it is a `tuning_curve` with
   `model_fit` empty. Its migrator (`migrators_j.stimulus_tuningcurve`) maps the flat
   `independent_variable_*` / `response_*` / `control_*` into the `tuning_curve` fields.

## Relationship to what already shipped (do not regress)

The 12 vision calculators ALREADY fold single-doc to `subject_calculation` leaves and are
**green** (Soph corpus run #2, ~101k docs, 0 orphans). Today they land on *five distinct*
`*_calculation` leaf names (orientation_direction_tuning_calculation, contrast_… etc.) reusing
the v1 result-class names as composites. **This build RE-TARGETS those folds onto the single
`tuning_curve_calculation` leaf + `tuning_curve` composite.** The fold *mechanism*
(jCalculation, id-preserving) is unchanged — only the target class name + composite shape
change. The orphan-safety argument is identical (id preserved), so the 0-orphan result must
be re-verified on the corpus after the re-target, not assumed.

## Deferred build tasks (the batch)

1. **Add `tuning_curve` composite** (decision-1 fields) as an abstract `data_type`; wire
   `_disposition` so it persists structurally (it shares the "tuning" stem with v1 sources —
   same guard the existing calc composites needed).
2. **Add `model_fit` as an ARRAY sub-structure** + a `model` (T8) `value_set` of fit-model
   terms; seed bindings. Add the typed, queryable metrics block for the summary scalars.
   *(Field/block names finalized in the naming pass.)*
3. **Add `tuning_curve_calculation` leaf** = `subject_calculation` + `tuning_curve`.
4. **Re-target the 12 tuning-family calculator migrators** — the 5 `*_tuning` result
   classes, their 5 `*_tuning_calc`/`oridirtuning_calc` wrappers, `tuningcurve_calc`, and
   the raw `stimulus_tuningcurve` — onto `tuning_curve_calculation` + `tuning_curve`.
   NOT `contrast_sensitivity_calc`: it is a distinct aggregate that stays on
   `contrast_sensitivity_calculation` (the tuning collapse does not touch it). Map each v1
   fit block (`fit`/`fit_dog`/`fit_movshon`/`fit_spline`/`priebe_fit_*`/…) into a `model_fit`
   ARRAY entry (`model` term + coefficients + goodness); map the `vector`/`significance`/
   `fitless` scalars into the TYPED metrics block (queryable), NOT into `model_fit`.
5. **Retire the five per-tuning composite class names + `stimulus_tuningcurve`** as distinct
   composites (they become instances of `tuning_curve`); update `V_eta_migration_targets.json`
   (the 12 tuning-family entries) to point at `tuning_curve_calculation` — the 13th
   calc-family entry, `contrast_sensitivity_calc`, stays on `contrast_sensitivity_calculation`;
   update
   `_DELETE_PHASE8` / `_RET_*` markers so the doc counts follow.
6. **Fixtures/tests**: a raw `tuning_curve` (no fit), a double-gaussian orientation fit, a
   Naka-Rushton contrast fit, a Priebe speed fit, and a frequency case with **multiple
   co-existing fits** (assert the `model_fit` array holds all of them, none dropped) —
   assert id-preserved, each entry's `model` term bound, the typed metrics block queryable.
7. **Corpus re-verify**: re-run the Soph gate after the re-target; the 0-orphan invariant must
   hold (id preserved). This is the real gate, not the fast fixtures.

## Out of scope / deferred

- **NDIcalc-vis `ndi.query` rename** to the leaf name (`tuning_curve_calculation`) — separate
  repo, naming-B, out of scope (as with the current leaf names).
- **Per-model schema enforcement** (option B) — only if a corpus need arises; see decision 2.
