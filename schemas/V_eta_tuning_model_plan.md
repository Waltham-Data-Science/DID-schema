# V_eta — the tuning-composite model (DECIDED; build deferred)

*Worked design for how V_eta represents tuning curves and their fits, decided in the audit
walkthrough (R2/R3). **All decisions below are FINAL; the BUILD is deferred** — batched with
the other walkthrough decisions (image/array). When building, this doc is the spec.
Cross-refs: `V_eta_tenets.md` (T3/T8/T10/T12), `V_eta_tenet_audit.md` (R2/R3),
`V_eta_subject_calculation_plan.md` (the calculator fold).*

## The one-line model

> **There is ONE tuning value: a `tuning_curve` `data_type` — a response-vs-independent-
> variable curve. The independent variable is a `variable` (T11), not a name suffix. The fit
> is ONE flexible `model_fit` sub-block identified by a controlled term (T8), not a class per
> model. The six overlapping v1 classes and five fit shapes collapse to `tuning_curve` +
> `tuning_curve_calculation` (one leaf).**

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
   - `model_fit` (structure, optional) — decision 2.
   - `derived_summary` (structure[], optional) — the fitless scalars (c50, l50, h50, pref,
     bandwidth, low/high-pass index) as named `{name, value, units}` entries, so a
     fitless composite carries them without a fit.

2. **R2 — ONE flexible `model_fit` sub-block, NOT a class per model** (T8/T12; the user's
   call, option A). The fitted models (double-gaussian, Naka-Rushton, DoG/Movshon/spline,
   Priebe) are genuinely different *structures*, but they are all "parameters of a fitted
   model," so they are distinguished by a **controlled term + a named parameter array**, not
   by minting `*_fit` data_types. `model_fit` fields:
   - `model_name` (ontology_term, T8 binding) — `double_gaussian` | `naka_rushton` |
     `difference_of_gaussians` | `movshon` | `spline` | `gausslog` | `priebe` | … (a
     controlled `value_set`; extend the set, not the class list, for a new fit).
   - `parameters` (structure[]) — `{name, value}` coefficient entries (e.g. Naka-Rushton
     `rb`/`rbn`/`rbns`; double-gaussian center/width/amplitudes).
   - `goodness` (structure, optional) — fit-quality scalars (r², residual, …).
   - **Trade-off recorded (T12 requires it):** a free-form `parameters` array is *less*
     self-validating than five typed fit structures — T8 enforces "`model_name` is a valid
     term," but NOT "the parameters match the term" (a Naka-Rushton having exactly rb/rbn/rbns
     is by-convention, not schema-enforced). Accepted for parsimony. If a corpus need for
     per-model schema enforcement arises later, escalate to option B (typed `*_fit`
     data_types) — the curve collapse (decision 1) is unaffected either way.

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
2. **Add `model_fit`** as a shared sub-structure + a `model_name` `value_set` (T8) with the
   fit-model terms; seed bindings.
3. **Add `tuning_curve_calculation` leaf** = `subject_calculation` + `tuning_curve`.
4. **Re-target the 12 calculator migrators** (`migrators_j.*_calc`, `tuningcurve_calc`,
   `stimulus_tuningcurve`) onto `tuning_curve_calculation` + `tuning_curve`; map each v1
   fit block (`vector`/`fit`/`fit_dog`/`fit_movshon`/`priebe_fit_*`/…) into `model_fit`
   (`model_name` + `parameters`) and the fitless scalars into `derived_summary`.
5. **Retire the five per-tuning composite class names + `stimulus_tuningcurve`** as distinct
   composites (they become instances of `tuning_curve`); update `V_eta_migration_targets.json`
   (the 13 calc-family entries) to point at `tuning_curve_calculation`; update
   `_DELETE_PHASE8` / `_RET_*` markers so the doc counts follow.
6. **Fixtures/tests**: a raw `tuning_curve` (no fit), a double-gaussian orientation fit, a
   Naka-Rushton contrast fit, a Priebe speed fit — assert id-preserved, `model_fit.model_name`
   bound, `derived_summary` populated for a fitless case.
7. **Corpus re-verify**: re-run the Soph gate after the re-target; the 0-orphan invariant must
   hold (id preserved). This is the real gate, not the fast fixtures.

## Out of scope / deferred

- **NDIcalc-vis `ndi.query` rename** to the leaf name (`tuning_curve_calculation`) — separate
  repo, naming-B, out of scope (as with the current leaf names).
- **Per-model schema enforcement** (option B) — only if a corpus need arises; see decision 2.
