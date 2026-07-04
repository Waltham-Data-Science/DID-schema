# V_zeta schemas

The `V_zeta/` directory is the working set-version directory for the sandbox
iteration that implements **Brainstorm I**. Like V_epsilon before it, V_zeta is
a sandbox: contents are expected to change in place, and consumers should not
pin to V_zeta as a stable target. The set will be copied to `schemas/V1/` and
frozen when ready (see `V_zeta_SPEC.md` § "Promotion to V1").

This notes file tracks V_zeta's status, the decisions taken where the source
proposals were open, and the open follow-ups.

## What V_zeta changes versus V_epsilon

V_epsilon implemented Brainstorm **E** (an observation class per measured
*property*). The merge that landed V_epsilon on main records that **Brainstorm E
is superseded by Brainstorm I**; V_epsilon is kept as an archived reference.
V_zeta is the Brainstorm-I implementation.

Brainstorm I is *"Brainstorm H plus three field-level changes and two
restorations."* Concretely, versus V_epsilon:

1. **One spine.** The whole identity/where/when payload moves onto
   `subject_interaction` (← `base`): `subject_id`, `time_reference_#`, `method`,
   `variable`, `target_structure`. `observation` / `manipulation` / `annotation`
   become empty direction markers. `subject_statement` is removed;
   `subject_assertion` is re-rooted under `base`.
2. **Off-class identity.** The observation tier is named by **data-type
   (shape)**, not property: 12 dimensional `scalar_<dim>_observation` leaves +
   `generic_scalar_observation` replace E's ~20 property leaves, and
   `categorical_observation` collapses to one concrete class. The property rides
   on the `variable` term. This is the direct answer to E's enumeration failure
   (the EPM dilemma).
3. **Shaped time.** `time_reference` gains a `sampling` structure
   (point/grid/enumerated); `sample_time` is retired from the scalar genera.
4. **Path T locus.** `target_structure` is restored as a spine field.
5. **Dataseries branch** (`dataseries_observation` → `timeseries_` /
   `imageseries_observation`) is retained from the E draft as the observation-tier
   handle for acquired data.
6. **Manipulation tier by structure, not identity.** The same off-class rule is
   applied to manipulations: a class exists only when it adds structure (a typed
   value, a dependency, an invariant). The pure-identity `procedural_manipulation`
   and `environmental_manipulation` (only an ontology `procedure`/`factor` + prose)
   are **removed** and fold into a new concrete `generic_manipulation`
   escape-hatch leaf (the manipulation-side analog of `generic_scalar_observation`);
   the act is named by the spine `variable`. Shared `notes` prose moves up to the
   abstract `manipulation` base; `biological_transfer` re-parents onto
   `manipulation` (it earns its class via the `donor_id` dependency).
7. **Individuated referent on the spine.** `subject_interaction` gains an
   **optional** `element_id → element` dependency (SPEC §3.1): the specific
   element that is part of the subject (an `ndi.neuron`, a probe, a derived
   signal) that an interaction is about, when that entity has its own document
   identity and is neither a `subject_group` nor an anatomy term. Completes the
   spine referent set — `subject_id` (whole specimen) / `target_structure`
   (ontological KIND of locus) / `element_id` (which specific one). Optional;
   identity stays off the class. (Added after the initial build, per maintainer
   feedback on element-scoped observations; migrators don't populate it yet.)

The typed manipulation families (`injection`/`bath`/`scalar_manipulation` tier),
`time_reference` reference frames, dataseries/expression bodies, the
scalar/categorical shape library, all infrastructure, and the five deprecated
classes carry over from V_epsilon (design-neutral for I).

## Initial state

- V_zeta content began as a verbatim copy of V_epsilon, then the Brainstorm-I
  transform (above) was applied.
- **201 document classes**: 155 `stable`, 40 `draft`, 6 `deprecated`, + 3 meta.
  `index.json` `set_version`/`schema_version_value` = `"V_zeta"`; `based_on` =
  `"V_delta"` (the format/content ancestor V_zeta's files were copied from);
  `legacy_schema_version_values` = `["did_v1"]` — did_v1 is the only production
  document version, so it is the sole migration source (V_alpha..V_epsilon never
  shipped).
- 23 Brainstorm-E classes removed (the property-named observation leaves,
  `categorical_concept`, `subject_statement`); 13 shape-typed scalar observation
  leaves authored; `categorical_observation` made concrete; `time_reference`
  `sampling` added; spine rewritten; `target_structure` / `sample_time` /
  `expression.method` stripped where they duplicated the spine.
- Every schema validates against `did_schema_meta.json`; `index.json` agrees
  with disk (tier/maturity/path); every superclass and `must_refer_to_document_class`
  resolves; the spine composes onto every interaction leaf; no
  `placement:concrete_class` collisions. Enforced by `tests/test_vzeta.py` and validated by the full suite (515 tests pass).

## Decisions taken where the source proposals were open

Brainstorm I is explicitly provisional and leaves several load-bearing choices
open. V_zeta resolves each with a documented default (see `V_zeta_SPEC.md` §9),
confirmed with the maintainer for the two spine-shaping forks:

- **Locus: Path T (`target_structure` field), not Path S (subject-as-part).**
  Confirmed. Near the decided model; no standing find-or-create/dedup service
  required under random subject UIDs. Trade-off accepted: the region/slice wall
  and no per-locus biography.
- **Scope: the full coverage set** — spine + shaped time + scalar/categorical/
  dataseries observation leaves + manipulation families + preserved
  infrastructure + deprecations, sufficient to express every existing V_delta
  document. Confirmed.
- **Identity: keep `method` / `variable`** (settled in Brainstorm I), off-class,
  with a soft binding-registry nudge rather than a class weld.
- **`method` optional at the schema level** (the verb is nearly always
  "measurement" on the observation tier); `variable` required.
- **`annotation` kept as a third direction** for curatorial/relational events
  (`group_assignment`). Brainstorm I foregrounds observation/manipulation
  symmetry but does not preclude it; it is carried from V_epsilon.
- **Optional `element_id` on the spine** (individuated referent, §3.1) —
  confirmed with the maintainer for element-scoped observations that Path T's
  ontology `target_structure` cannot address.
- **`session_relative_reference` declares no `session_id` edge.** Session
  identity rides on `base.session_id` (every DID document carries it), so the
  ordinal fallback anchor needs no `session_id` dependency. The edge was
  redundant with `base` and produced only discovery-mode reference-integrity
  orphans — the migrators synthesize thousands of these anchors (one per
  timeless treatment / ontology_table_row / resolved bath), and the `session`
  document is not part of a corpus dump, so every one dangled (~41k on JH, ~8k
  on Dab). Dropping the edge removes the orphans at the source; the real
  `ndi.migrate.local` path is unaffected (it referenced the session the same way
  via `base`).

## Provisional / still open (from Brainstorm I)

These are flagged open in `Brainstorm_I_Tour_and_Comparison.md` §1.7 and are
revisitable while V_zeta is a sandbox:

- **The subject-vs-target rule** (the ex-vivo case) and single-vs-nested
  `target_structure` multiplicity. V_zeta uses a list; the multi-structure-image
  rule (FOV container + derived observations) is a curation convention, not a
  schema constraint.
- **The in-document (scalar/small series) vs `element_epoch` boundary**, and the
  document-size cap that enforces it. The scalar/dataseries axis test (#59)
  decides the *class*; the size cap that routes a small vs large series is a
  tooling policy, not encoded here.
- **The axis split** — time in `time_reference.sampling` vs all axes in the
  dataseries header. V_zeta puts the time axis in `sampling` and the spatial/
  other axes + channel model in the dataseries header (I's provisional
  reconciliation).
- **`stimulus_approach` v2 write-time invariants** — documented in the proposal,
  enforced by tooling, not the schema.

## Not implemented in this pass (open follow-ups, separate PRs)

- **Binding registry as a meta-file.** V_zeta carries `binding` blocks inline
  (advisory, in `constraints`) on `variable`-keyed / `categorical_observation.value`
  fields; the registry meta-file + `value_set` class are not added.
- **`dataSeriesType` registry** (a `probetype2object`-style type→template) and
  per-element channel-identity materialization — registry/tooling artifacts.
- **Conversion docs.** The only production document version is **`did_v1`** (our
  first version); V_alpha..V_epsilon were sandbox iterations that never shipped,
  so there is nothing to migrate *from* them — `conversions/from_did_v1/` is the
  sole conversion tree. It has been **retargeted from V_epsilon (Brainstorm E) to
  V_zeta (Brainstorm I)**: the `treatment` split and the `ontology_table_row`
  1→N split now target the shape-typed observation tier + the `(method, variable)`
  spine (property leaf → shape leaf + `variable`; the retired `measured_property`/
  `applied_property` → spine `variable`; `sample_time` → the shaped `time_reference`),
  and the four folds (`treatment_drug`/`virus_injection` → `injection`,
  `treatment_transfer` → `biological_transfer`, `subject_group` → `subject(is_group)`)
  target the V_zeta classes. Remaining: finalize each corpus's per-term dispatch in
  discovery mode; the migrator itself lands in DID-matlab.
- **NDI-matlab / DID-matlab consumer tooling** — resolve V_zeta via `index.json`;
  emit the shaped `time_reference`; write the record/array channel model +
  `dataseries_channel_map`; the E→I observation migrator.

## Carried-over cleanup

`hartley_calc`'s malformed `file` record (field-definition keys on a file
record, present identically in V_delta and V_epsilon) is fixed in V_zeta
(stripped to `name` + `documentation`, v2.0.0), so the whole set passes
meta-validation with no carryover defect.
