# V_eta — `subject_calculation` composite-leaf family (scoping)

Status: **IMPLEMENTED — 11/12 vision calculators green** (CI gates #17–#21). Done:
`parameters→conditions` rename; the `subject_calculation` direction + composites/leafs;
the 5 tuning result classes + their 5 `*_calc` wrappers + `contrast_sensitivity_calc`
all fold id-preserved via `migrators_j.private.jCalculation`. DEFERRED (legit):
`tuningcurve_calc` needs the NDI session-aware second pass (no subject on the doc —
resolve the neuron from the response→element graph); its composite/leaf scaffold is
ready and it passes through meanwhile. Follow-ups: NDIcalc-vis `ndi.query` rename
(naming B, separate repo) + optional alias; `hartley`/RF → 2.D; the full-corpus run to
lock the un-deferral. Original scoping (below) requested by the team following
Lepsky, Severson, Wang, Cheng, Rodriguez, Gong & Van Hooser, *"A motif for
domain-specific analysis applets … application to vision science"* (bioRxiv
2026.04.27.721136): keep calculators as **composite leafs** rather than (a) deferring
them as passthrough `*_calc` bags or (b) dissolving them into bare `*_observation`s
(D-C grain A). This doc scopes a `subject_calculation` direction + a set of composite
`data_type`s, mirroring `visual_grating_manipulation = subject_manipulation +
visual_grating`.

> ⚠️ This **revises two settled D-C decisions** (see §6). It needs team sign-off
> before implementation. The biggest open call is **naming** (§7): the paper makes
> the output document *type* the pipeline-composition contract, so renaming a `*_calc`
> class is not free.

## 0. What the paper prescribes (grounding)

The motif's hard constraints, and how each lands in V_eta:

- **One calculator → exactly one output document type** ("a calculator object can only
  produce a single type of output document whose form is rigorously specified", §3.2).
  ⇒ **one `subject_calculation` leaf class per calculator.** The leaf set is the
  calculator set: oridir, contrast, spatial-freq, temporal-freq, speed, tuningcurve,
  (contrast-sensitivity), hartley.
- **The output document is the pipeline interface.** Pipelines are not wired; a
  downstream calculator *searches the database for the output document type* of an
  upstream one (e.g. the Direction-Fit calc searches for `stimulus_tuningcurve` docs;
  Fig 5). ⇒ the leaf's **class name and searchable fields are a contract**, not
  incidental — this drives the naming decision (§7).
- **Document shape** (Fig 4, `oridirtuning_calc`): top-level `app` (program version),
  `depends_on` (the input documents used), `document_class`, `base`; a **provenance
  block** `<calc>` = `input_parameters` + an in-block `depends_on` naming the specific
  input (e.g. `stimulus_tuningcurve_id`); and a **result block** `<result>` (e.g.
  `orientation_direction_tuning` = properties / tuning_curve / significance / vector /
  fit). "All fields are exposed to search." ⇒ the two blocks map exactly to
  **`subject_calculation` (provenance: app→method, input_parameters→method_parameters,
  input refs→depends_on) + the result composite `data_type`.**
- **Everything a calculator emits is a *calculation*** (a computed output), including
  the raw tuning curve (`stimulus_tuningcurve`, the output of `ndi.calc.tuningcurve`,
  and itself an *input* to the fit calcs). The measured `stimulus_response` is the
  observation; tuning curves and fits are calculations. ⇒ resolves the
  calculation-vs-observation question (old §7.1) in favor of *calculation*.
- **FAIR at every stage** via provenance carried in `depends_on`. ⇒ the migration MUST
  preserve `depends_on` verbatim (it already must, for zero-orphan).

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

## 7. Open questions

### 7.0 THE decision: leaf class naming (paper-driven)
The paper makes the output document *type* the pipeline-composition contract
(downstream calcs `ndi.query` for it by class). So renaming a `*_calc` class is not
a free schema cleanup — it can break NDIcalc-vis searches. Two options:

- **(A) Preserve the type names** — keep `oridirtuning_calc`, `contrast_tuning_calc`,
  `tuningcurve_calc`, … as the leaf class names; only *re-parent* them onto
  `subject_calculation` + the result composite and reshape the block. Migration is
  1→1 with **no class rename** (strongest ref/search preservation) and NDIcalc-vis
  keeps working unchanged. Cost: the `_calc` suffix stays (mildly against V_eta's
  de-encode-names philosophy, since the `subject_calculation` direction already says
  "computed").
- **(B) Clean `<composite>_calculation` names** — `orientation_direction_tuning_calculation`,
  … V_eta-idiomatic, but requires migrating NDIcalc-vis search queries to the new
  types (and possibly a class alias for back-compat). More disruptive.

**Recommendation: (A)** — the paper's whole thesis is that the output document type is
a durable, searchable contract other code depends on; preserving it honors the motif
and makes this the least-risky un-deferral. (B) can be a later cosmetic pass with an
alias.

**DECISION (team, 2026-07): (B) — clean `<composite>_calculation` names.** Required
follow-up (separate, NDIcalc-vis repo, out of this schema's scope): migrate the
`ndi.query` calls in the `ndi.calc.vis.*` calculators to the new leaf class names;
consider a back-compat class alias so old queries keep resolving during transition.
`method`/`method_parameters` default (below) also decided by delegation.

**DECISION (app / input_parameters):** keep `app` verbatim (the program+version
reproducibility record, paper Fig 4/§4.2 FAIR) AND surface the algorithm identity in
`subject_interaction.method` (queryable) with `input_parameters` →
`subject_interaction.method_parameters` (the slot already documents itself as the
calculator input_parameters, Fig 3E). So provenance is both preserved (`app`) and
spine-queryable (`method`/`method_parameters`).

### 7.1 Resolved / remaining
- ~~Are tuning results calculations or observations?~~ **RESOLVED (§0): calculation.**
  Everything a calculator emits is a computed output; the measured `stimulus_response`
  is the observation.
- **Composite `value` schemas** — field lists are lifted from the current classes +
  Fig 4/6; confirm which fields are first-class (queryable) vs. carried-opaque, and the
  ontology terms for `variable`/`method` (the `ndi.calc.vis.*` app identity).
- **Provenance representation** — keep input `*_id` links as `depends_on` (zero-orphan,
  minimal, and what the paper shows — both top-level and in-block) or ALSO mint
  `directed_relation(derived_from)` (queryable graph, D-E)? Keep `depends_on` as the
  default; the relation is an optional follow-up.
- **`app` / `input_parameters`** — map `app`→`subject_interaction.method` (ontology_term
  of the `ndi.calc.*` applet) + `input_parameters`→`method_parameters`, or keep a
  literal `app` block for version fidelity? Fig 4 keeps `app` top-level; leaning
  method+method_parameters with `app` retained for the program version.
- **`simple_calc`** — its own `scalar_calculation` leaf, or map to an existing scalar
  composite (`score`/`frequency`/…) with the calculation direction?
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
