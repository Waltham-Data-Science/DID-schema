# V_eta schemas

The `V_eta/` directory is the working set-version directory for the sandbox
iteration that implements **Brainstorm J**. Like V_zeta before it, V_eta is a
sandbox: contents change in place, and consumers should not pin to it. The set
will be copied to `schemas/V1/` and frozen when ready (see `V_eta_SPEC.md`
§ "Promotion to V1").

This notes file tracks V_eta's status, the decisions taken, and open follow-ups.
The full design rationale and the `did_v1` → V_eta migration live in
`V_eta_migration_plan.md`; the target-model spec is `V_eta_SPEC.md`.

## What V_eta changes versus V_zeta

V_zeta implemented Brainstorm **I** (one thin `subject_interaction` spine, Path T
`target_structure`, shape-typed observation leaves with a `scalar_`/`dataseries_`
split, a shaped `time_reference`). V_eta is the Brainstorm-**J** implementation,
which keeps I's "identity off the class" and rebuilds the subject side. Concretely
(see `V_eta_SPEC.md` §§1–9):

1. **`subject` → bare identity** — `is_group`/`is_biological` removed (v3.0.0);
   kind is a `term_assertion`, group-ness is derived from edges.
2. **`subject_relation` branch** — `directed_relation` / `undirected_relation`;
   relationships are documents with a closed, RO-backed vocabulary.
3. **`subject_statement` restored** — owns `variable`/`value`/optional time, so
   identity search spans assertions and interactions.
4. **`subject_assertion` genus** — timeless facts typed by data shape
   (`term_assertion`, `date_assertion`, `numeric_assertion` → dimensioned leaves).
5. **`subject_interaction` re-rooted; direction renamed** to
   `subject_observation` / `subject_manipulation`; Path S replaces Path T
   (`target_structure` removed; parts become subjects + `part_of` relations).
6. **Leaf tier rebuilt** — one class per data type, one-word names, no `scalar_`
   prefix, no `scalar_`/`dataseries_` split; `categorical_observation` →
   `term_observation`; no `injection`/`bath`/`pharmacological`/`biological_transfer`/
   `generic_manipulation` (→ data-type-named manipulations + composites +
   `term_manipulation`; no escape hatch).
7. **Bindings hard-validated** — a `value_set` class + binding-registry meta-file
   + formalized `binding` block + ontology-aware validator (D9).
8. **`storage_mode` + `data_body`** (`sampled_body`/`opaque_body`) consolidate the
   V_zeta body/epoch classes; timing cadence moves beside the value; `element_id`
   retired in favour of `instrument_id → subject` (device-as-subject).

The value-cell composites, the `time_reference` frames (minus `sampling`), and all
non-subject infrastructure carry over verbatim.

## Decisions taken (D1–D9)

All resolved with the maintainer; recorded in `V_eta_migration_plan.md` Part E.

- **D1 timing** — anchor in `time_reference`; compressed cadence beside the value
  (statement `sample_time` inline, `sampled_body.sample_time` for bodies); the
  body is the single home of a body-backed timeline; `time_reference.sampling`
  removed.
- **D2 individuated referent** — device-as-subject + optional
  `instrument_id → subject`; **no** `element_id`; **no** kind-subclasses (kind via
  `term_assertion`, role via typed edges).
- **D3 Path S scope** — measure attributed-locus volume in discovery mode before
  building the mint/dedup service; located-by-default.
- **D4 transfer donor** — provenance `directed_relation`; act is a
  `term_manipulation`; no `biological_transfer`.
- **D5 locus/label terms** — `probe_location`/`ontology_image`/`ontology_label`
  → `term_observation`.
- **D6 relation vocabulary** — declare the corpus-exercised minimum
  (`part_of` + one provenance term); add the rest when a source appears.
- **D7 closure index** — ingestion/consumer-layer materialised view; not
  schema-enforced; outside the abstract query model.
- **D8 payload-free manipulations** — `term_manipulation`; no escape hatch.
- **D9 subject kind** — bound `term_assertion`; **hard vocabulary validation +
  binding registry from day 1** (do not defer). Presence stays an ingestion
  invariant; vocabulary is validated.

## Build status

**In progress.** V_eta is built deterministically from V_zeta by
`tools/build_v_eta.py` (re-runnable); the tree validates and
`tests/test_veta.py` (451 checks) passes alongside the full suite (970 total).

Increment 1 — the subject-side core — **done**:

- [x] Tree stood up (`schemas/V_eta/`; `index.json` `set_version` /
  `schema_version_value` = `"V_eta"`, `based_on` = `"V_zeta"`; 218 classes + 3 meta).
- [x] Subject side: bare `subject` (v3.0.0); `subject_relation` /
  `directed_relation` / `undirected_relation`; restored `subject_statement`
  (owns `subject_id` + `variable`); `subject_assertion` genus + `term_assertion` /
  `date_assertion` / `numeric_assertion` + 12 dimensioned scalar assertion leaves;
  `subject_interaction` re-rooted under `subject_statement` (adds `method`,
  `sample_time`, optional `instrument_id`; required time); direction renamed to
  `subject_observation` / `subject_manipulation`; `target_structure` and
  `element_id` dropped; `annotation` / `group_assignment` retired.
- [x] Leaf renames: `<dim>_observation` (one word, no `scalar_` prefix), the
  `scalar_observation` / `scalar_manipulation` umbrellas removed,
  `categorical_observation` → `term_observation`, shape mixins `scalar_<dim>` →
  `<dim>`.
- [x] Timing relocation (D1): `time_reference.sampling` removed; the cadence is
  `sample_time` on `subject_interaction`.
- [x] `value_set` class (binding-registry primitive).
- [x] `tests/test_veta.py` (meta-validation, index/disk, superclass + dependency
  resolution, spine composition, subject-side structure).

Increment 2 — leaf-tier depth — **done** (manipulation tier, storage model,
binding registry). Full suite 975 passing (`test_veta.py` 456 checks):

- [x] Retired the delivery-method family (`injection` / `bath` / `stimulus_bath` /
  `pharmacological_manipulation`) and the escape hatches (`generic_manipulation` /
  `generic_scalar_*`) → `dose_manipulation` / `formulation_manipulation` +
  `dose` / `formulation` / `chemical` composite mixins + `term_manipulation` for
  payload-free acts (D8). `biological_transfer` retired (→ `term_manipulation` +
  a provenance `directed_relation` minted by the migrator, D4).
- [x] `storage_mode` on `subject_statement` + `data_body` / `sampled_body` /
  `opaque_body` (draft tier); the body carries the value's timeline (D1).
- [x] Binding registry hardened (D9): the `binding` block is **formalized in the
  meta-schema** (validated `constraints.binding`), and `binding_registry_meta.json`
  ships the enumerated kind-variable set (species, instrument type, cell type,
  material type, developmental stage) + their ontology roots.

Increment 3 — remaining (entangled with NDI-side infra; needs the NDI-matlab work):

- [ ] Collapse the `dataseries_` / `timeseries_` / `imageseries_` observation +
  `*_data` body classes and `element_epoch` / `generic_file` /
  `expression_matrix_data` onto the data-type leaves + `sampled_body` (they are
  carried unchanged for now so the set validates).
- [ ] The **ontology-aware binding validator** (consumer tooling — DID-matlab /
  DID-python; resolves a term value against its bound `value_set`).
- [ ] `schemas/V_eta/conversions/from_did_v1/` retarget to the J targets (mirrors
  migration-plan Part D); the copied docs are still V_zeta-targeted.

## Not implemented in this pass (open follow-ups)

- **`dataSeriesType` registry** and per-element channel-identity materialization.
- **Live-correction / supersession** of shared `reference` value documents
  (immutable references need none).
- **Populating the individuated referent** (`instrument_id`) — a per-migrator
  follow-up, as in V_zeta.
- **Forward-looking relation surface** with no `did_v1` source (`member_of`,
  `placement`, `derivation` authoring; the extra J relation terms).
- **The migrator itself** (`+migrators_j/`) and the NDI second pass — Phase 2,
  after the schema tree lands.
