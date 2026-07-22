# V_eta — `subject_calculation` composite-leaf family (scoping)

Status: **SCOPING / proposal — not implemented.** Requested by the team following
the [paper fed 2 sessions ago — cite here]: keep calculators as **composite leafs**
rather than (a) deferring them as passthrough `*_calc` bags or (b) dissolving them
into bare `*_observation`s (D-C grain A). This doc scopes a `subject_calculation`
direction + a set of composite `data_type`s, mirroring
`visual_grating_manipulation = subject_manipulation + visual_grating`.

> ⚠️ This **revises two settled D-C decisions** (see §6). It needs team sign-off
> before implementation, and the composite field schemas need the paper's specifics.

## 1. Why this is the right shape (and why it un-defers calculators)

The calculator-deferral problem (CLAUDE.md): the corpus stores calc outputs as
`*_calc` docs that DOWNSTREAM calcs reference by id (e.g.
`contrast_sensitivity_calc.contrasttuning_id_* -> contrast_tuning_calc`). Dissolving
a `*_calc` into observations changes/removes its id → every downstream ref dangles →
orphans (Soph went red: 11448 orphans). So D-C deferred them as passthrough.

A `subject_calculation` **leaf** fixes this because the migration is **1 → 1,
id-preserved, deps-preserved**: the calc doc keeps its `base.id` and its
`depends_on` (input) edges; only its *class* changes (`contrast_tuning_calc` →
`contrast_tuning_calculation`). Downstream refs resolve because:
- the referent id is unchanged, and
- `must_refer` is DECLARATIVE (existence-only, not type-checked) — the pointer does
  not care that the target's class changed.

So calculators become first-class, typed, queryable leafs **without** dangling a
single reference. This is strictly better than passthrough (which keeps the untyped
`*_calc` bag) and avoids the orphan explosion that killed grain-A dissolution.

## 2. The spine: `subject_calculation` as a fourth direction

```
subject_statement (abstract; variable, parameters, storage_mode)
├── subject_interaction (abstract; method, method_parameters, sample_time)
│   ├── subject_observation   (measured FROM the subject)
│   ├── subject_manipulation  (done TO the subject; + notes)
│   └── subject_calculation   (NEW — COMPUTED about the subject)   ◀── add
└── subject_assertion         (declared about the subject)
```

`subject_calculation` ⊂ `subject_interaction` inherits exactly what a computed
statement needs:
- `variable` — what was computed (e.g. "contrast tuning").
- `method` (ontology_term) — **the algorithm** (`ndi.calc.vis.contrast_tuning`, …).
  This is where the old `calculator`/`*_calc` app identity lands.
- `method_parameters` — the algorithm config; absorbs `calculator.input_parameters`.
- `sample_time` — when the underlying data was taken (point/grid as appropriate).
- `storage_mode` — `inline` for small structured results; `body` when a curve is
  large enough to spill to a `sampled_body` (rare; most tuning results are small).

Provenance to inputs (the `*_id` links between calcs) stays on the leaf's
`depends_on` **and/or** becomes a `directed_relation(derived_from, method=…)` edge
(D-E) — TBD per §7. Preserving `depends_on` verbatim is the zero-orphan default.

`subject_calculation`'s own block: none required (it is a pure direction marker,
like `subject_observation`). The value lives in the composite (§3).

## 3. The composite `data_type`s (the value carriers)

Each leaf pairs `subject_calculation` with one composite `data_type` (⊂ `data_type`,
a single `value` field), exactly like `visual_grating`. The tuning "result" classes
already carry these structures as base-bags; this **reframes them as composites**
(re-parent `base` → `data_type`, wrap their blocks under `value`). Proposed set:

| composite (`data_type`) | `value` payload (from the current class) | source class(es) |
|---|---|---|
| `tuning_curve` | independent_variable_{label,value}, response_{mean,stddev,stderr}, individual, control_*, units | `stimulus_tuningcurve`, `tuningcurve_calc` |
| `contrast_tuning` | tuning_curve, properties, significance, fitless, fit (naka_rushton) | `contrast_tuning`, `contrast_tuning_calc` |
| `orientation_direction_tuning` | tuning_curve, properties, significance, vector (OSI/DSI/pref), fit (double_gaussian) | `orientation_direction_tuning`, `oridirtuning_calc` |
| `spatial_frequency_tuning` | tuning_curve, significance, fitless, fit_{dog,movshon,movshon_c,spline,gausslog} | `spatial_frequency_tuning`, `spatial_frequency_tuning_calc` |
| `temporal_frequency_tuning` | (same shape as spatial_frequency) | `temporal_frequency_tuning`, `temporal_frequency_tuning_calc` |
| `speed_tuning` | tuning_curve (sf×tf), significance, fit_{,no_speed,fullspeed} (priebe) | `speed_tuning`, `speed_tuning_calc` |
| `contrast_sensitivity` | spatial_frequencies, sensitivity_{rb,rbn,rbns}, gain, c50, saturation, p-values | `contrast_sensitivity_calc` |
| *(reuse)* `score` / `frequency` / `angle` / `intensity` | a single scalar result + unit | `simple_calc` (result_value/result_units) |

Leaf naming = `<composite>_calculation` (parallel to `<composite>_manipulation`):
`contrast_tuning_calculation`, `orientation_direction_tuning_calculation`,
`spatial_frequency_tuning_calculation`, `temporal_frequency_tuning_calculation`,
`speed_tuning_calculation`, `tuning_curve_calculation`,
`contrast_sensitivity_calculation`, and a `scalar_calculation` (or reuse an existing
`*_observation`-style leaf name with the calculation direction) for `simple_calc`.

**Deferred to 2.D (`data_body`), NOT this family:** `hartley_calc` /
`hartley_reverse_correlation` / `reverse_correlation` — RF maps are large spatial
data → `sampled_body`, not an inline composite. (Consistent with D-C's existing
deferral of these.)

## 4. Migration mapping (1 → 1, id-preserved)

| v1 / current class | → `subject_calculation` leaf | notes |
|---|---|---|
| `tuningcurve_calc`, `stimulus_tuningcurve` | `tuning_curve_calculation` | method = tuningcurve algo; value = the curve |
| `contrast_tuning`, `contrast_tuning_calc` | `contrast_tuning_calculation` | |
| `orientation_direction_tuning`, `oridirtuning_calc` | `orientation_direction_tuning_calculation` | |
| `spatial_frequency_tuning`, `spatial_frequency_tuning_calc` | `spatial_frequency_tuning_calculation` | |
| `temporal_frequency_tuning`, `temporal_frequency_tuning_calc` | `temporal_frequency_tuning_calculation` | |
| `speed_tuning`, `speed_tuning_calc` | `speed_tuning_calculation` | |
| `contrast_sensitivity_calc` | `contrast_sensitivity_calculation` | |
| `simple_calc` | `scalar_calculation` | value = result_value + result_units |
| `hartley_calc` | *(2.D data_body — not here)* | RF map |

Every row: **keep `base.id`, keep `depends_on`.** The migrator reads the source
block, rewraps it under the composite's `value`, sets `document_class` to the leaf +
`method` to the algorithm, and returns 1 body. No anchor, no split, no new ids →
**zero new orphans by construction.**

## 5. What this retires

`calculator` and `tuning_fit` (the app-mixin bags) dissolve into the spine
(`method`/`method_parameters`); the `*_calc` / `*_tuning` classes become the composite
leafs above. Net: the whole calc/tuning zoo collapses onto ONE pattern
(`subject_calculation` + composite), the same anti-proliferation move J made on the
observation leaf tier.

## 6. ⚠️ Decisions this REVISES (needs sign-off)

1. **D-C "no `calculation`/`calculator` genus" — REVERSED.** The cohesiveness plan
   (§2.C, D-C) explicitly rejected a calculation genus, routing computed scalars →
   `*_observation` (method=algorithm) and curves → `data_body`. The team now wants
   the genus back, as a `subject_calculation` **direction** (not a standalone
   `calculation` class — so J's "provenance is not a class" principle is preserved;
   the genus is a statement *direction*, and provenance is still `method` +
   `derived_from`).
2. **"CALCULATORS ARE DEFERRED" (CLAUDE.md) — SUPERSEDED for the classes above.**
   The deferral existed only because dissolution dangled refs. The id-preserving
   leaf migration removes that reason, so these classes un-defer. (Un-defer only the
   ones with a composite leaf here; `hartley`/RF stays 2.D.)

Both are deliberate team calls from the paper — recording them here so the durable
record (CLAUDE.md, the cohesiveness plan) can be updated in lockstep when this lands.

## 7. Open questions (paper-informed)

- **Are tuning *results* calculations or observations?** A tuning curve is measured
  data reduced by an algorithm — arguably a `subject_observation` with method, not a
  `subject_calculation`. The team's choice (leaf family) says *calculation*; confirm
  the boundary (e.g. raw `stimulus_tuningcurve` = observation, the *fit* = calculation?).
- **Composite `value` schemas** — the per-composite field lists above are lifted from
  the current classes; the paper should confirm which fields are first-class
  (queryable) vs. carried-opaque, and the ontology terms for `variable`/`method`.
- **Provenance representation** — keep input `*_id` links as `depends_on` (zero-orphan,
  minimal) or also mint `directed_relation(derived_from)` (queryable graph, D-E)? The
  former is the safe default; the latter is a follow-up.
- **`scalar_calculation` vs. reuse** — does `simple_calc` earn its own leaf, or map to
  an existing scalar composite leaf (`score`/`frequency`/…) with the calculation
  direction?
- **Subject grain** — calc is about the neuron-subject (element→subject). Same
  `element_id`→`subject_id` carry as the observation migrators; confirm.

## 8. Implementation phases (once signed off)

1. **Schema (build_v_eta.py):** add the `subject_calculation` direction; add/reparent
   the composite `data_type`s (§3); emit the `*_calculation` leaf schemas. Rebuild,
   `pytest tests/test_veta.py`.
2. **Migrators (`+migrators_j`):** one thin 1→1 migrator per calc class (a shared
   helper `jCalculation(preBody, leafClass, composite, methodName)` that rewraps the
   block under `value`, sets the leaf class + method, preserves id + deps). Mirror the
   `jSorterOutput` shared-helper style.
3. **Tests:** `testMigratorsJ` transform tests + `testFixtureCorpus` fixtures
   (id-preserved, a downstream-ref fixture to PROVE 0 orphans across a calc→calc edge).
4. **Un-defer:** remove these classes from the deferred-calculator passthrough set;
   the full corpus (`test-code.yml`) is the gate that no ref dangles.
5. **Docs:** update CLAUDE.md (calculators no longer deferred for these), the
   cohesiveness plan (§2.C / D-C revision), the coverage ledger targets, and the web
   viewer.
