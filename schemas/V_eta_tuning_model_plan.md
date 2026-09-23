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

TEAM-SIGN-OFF [tuning_curve composite + tuning_curve_calculation leaf, restructure]:
Steve Van Hooser 2026-09-21 -- (1) REVERSE R2/R3's LEAF COLLAPSE: restore
per-calculator subclasses (oridirtuning_calc, contrasttuning_calc,
spatial_frequency_tuning_calc, temporal_frequency_tuning_calc, speedtuning_calc,
tuningcurve_calc) under a new abstract `tuning_curve_calculation` leaf, per Lepsky
et al. 2026 §3.2 / Fig. 2F / Fig. 4 / Fig. 5Bii. (2) PRESERVE R2's SHAPE
COLLAPSE: one `tuning_curve` composite carries the raw curve (independent_variables[],
mean, stddev, stderr, individual, raw_individual optional, control{...},
response_units, response_type, coordinates). (3) FIELD SPLIT: significance and
model_fit[] on the LEAF (calc-produced); everything else on the composite. (4)
Per-family fit shapes ride as `model_fit[]` array entries (R2 approach preserved),
not typed field declarations. (5) Multi-D tuning is first-class via
`independent_variables[]` cardinality — speed_tuning is a thin marker. Full spec:
Waltham-Data-Science/DID-schema#67.


## Amendment — #73 (2026-09-23): markers dropped, leaves renamed, family metrics typed

Decided by jess@walthamdatascience.com in the #73 review session, 2026-09-23.
It revises items (1) and (5) of the 2026-09-21 signature above and fills in
the per-family scalars that signature left empty; items (2)–(4) stand.
Source: Waltham-Data-Science/DID-schema#73.

1. **The five marker composites are dropped** (`orientation_direction_tuning`,
   `contrast_tuning`, `spatial_frequency_tuning`, `temporal_frequency_tuning`,
   `speed_tuning`). They were abstract with no fields. The fact each encoded is
   already `tuning_curve.value.independent_variables[].variable`, and nothing
   tied the two together (T11, T14). The one-calculator-one-document-type
   contract (T10, Lepsky §3.2) is met by the calculation leaves, not by the
   composites.
2. **`tuning_curve_calculation` is CONCRETE and ⊂ [`subject_calculation`,
   `tuning_curve`].** It is the generic tuning-curve calculator's own output
   type, the same `<result>_calculation` shape as
   `contrast_sensitivity_calculation` and `receptive_field_calculation`. An
   `isa tuning_curve_calculation` query returns all six. A consumer wanting only
   the generic calculator's output matches the exact class name. The contract is
   about the emitted class name, and all six stay distinct.
3. **The leaves are renamed to the `<result>_calculation` form (T13)**, each
   ⊂ `tuning_curve_calculation`:

   | #67 name | #73 name |
   |---|---|
   | `tuningcurve_calc` | `tuning_curve_calculation` (item 2) |
   | `oridirtuning_calc` | `orientation_direction_tuning_calculation` |
   | `contrasttuning_calc` | `contrast_tuning_calculation` |
   | `spatial_frequency_tuning_calc` | `spatial_frequency_tuning_calculation` |
   | `temporal_frequency_tuning_calc` | `temporal_frequency_tuning_calculation` |
   | `speedtuning_calc` | `speed_tuning_calculation` |

   The published v1 names stay the SOURCE side of the migration: every one is a
   ledger row folded by a completed migrator. The v1 tombstones at the four
   colliding calc names and the five result names join `_DELETE_PHASE8`.
4. **Each family carries its own typed summary block**: values read off the
   RAW curve. These are what v1 carried as `vector` and `fitless`, named as this
   plan's signed naming pass named them:
   - `orientation_direction_tuning_calculation.circular_statistics`
   - `interpolated_values` on the contrast, spatial-frequency and
     temporal-frequency calculations (contrast carries only the lower half-max
     point; SF/TF share one generated declaration)
   - speed and the generic calculation carry none.
5. **`model_fit[]` entries become `{model, coefficients, goodness, metrics,
   sampled_fit}`.** `goodness` = {`r2`, `sse`}. `metrics` = values read off THAT
   fit, one fixed set of optional typed fields across every fit family, so each
   stays queryable (no `{name, value}` bag). `sampled_fit` = the fit evaluated on
   a grid, kept as v1 stored it rather than recomputed. KNOWN LOOSENESS: nothing
   yet stops a fit filling a metric that does not apply to its `model`. Keying
   the admissible metrics on `model` waits on the model terms being bound.
6. **Names (T13).** The v1 contractions are replaced: `pref` → `preferred_value`;
   `l50` and `interpolated_c50` → `half_maximum_below` (C50 is the lower half-max
   point of a curve that only rises); `h50` → `half_maximum_above`; `hwhh` →
   `half_width_at_half_maximum`; `hotelling2test` / `direction_hotelling2test` →
   `hotelling_t2_p` / `direction_hotelling_t2_p`; `dot_direction_significance` →
   `direction_dot_product_p`. `bandwidth` keeps its name and is documented in
   octaves.

**A LIVE DEFECT THIS AMENDMENT DOES NOT FIX BY ITSELF.** Measured 2026-09-23 on
DID-matlab `claude/v-eta-migration-plan-35jj1z` @ `47cf8ba`, over 209 `.m` files
under `+did2/+convert`: **0 files read a v1 `vector` or `fitless` block.**
`jTuningCurveValue.m` lifts only `significance` and the `fit`/`fit_*` blocks. So
every oridir circular statistic and every SF/TF/contrast interpolated value is
dropped on migration today, while the documents validate. `collectFits` copies
each whole v1 fit block (parameters, derived metrics, sampled curve, r²) verbatim
into `coefficients`, leaves `goodness` empty, and turns contrast's single `fit`
block (three Naka-Rushton variants) into ONE entry named `fit`. SF/TF's `abs`
block (every block recomputed on absolute responses; declared empty in v1) is not
read either. Closing all of this is the DID-matlab half of #73.
