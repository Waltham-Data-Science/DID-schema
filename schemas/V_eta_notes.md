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

**In progress.** V_eta is being built from a copy of V_zeta with the §§1–8
transform applied. Tracked increments:

- [ ] Tree stood up (`schemas/V_eta/` copied from V_zeta; `index.json`
  `set_version`/`schema_version_value` = `"V_eta"`, `based_on` = `"V_zeta"`).
- [ ] Subject side: bare `subject`; `subject_relation`/`directed_`/`undirected_`;
  `subject_statement`; `subject_assertion` genus + leaves; `subject_interaction`
  re-root + `subject_observation`/`subject_manipulation`; drop `target_structure`;
  add `instrument_id`.
- [ ] Leaf tier: one-word data-type names, drop `scalar_` prefix, collapse the
  `dataseries_` split, `categorical_observation` → `term_observation`, retire the
  delivery-method / escape-hatch families.
- [ ] `storage_mode` + `sampled_body`/`opaque_body`; retire superseded body
  classes; relocate timing cadence.
- [ ] Binding registry: `value_set` class + binding-registry meta-file +
  meta-schema `binding` formalization + kind-variable set.
- [ ] `tests/test_veta.py` (meta-validation, index/disk agreement, superclass +
  `must_refer_to_document_class` resolution, spine composition, binding integrity).
- [ ] `schemas/V_eta/conversions/from_did_v1/` seed.

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
