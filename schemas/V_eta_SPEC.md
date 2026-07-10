# V_eta_SPEC.md — DID/NDI Document Schema Format (V_eta)

## Purpose

V_eta is the next sandbox iteration of the DID/NDI schema set. It implements
**Brainstorm J** (*"the subject model, and one class family for everything about
a subject"* — `ndi-next-steps/Summer 2026/1_Ingestion/20260615/Brainstorm_J_Subject_Model.md`,
issue #69), developed from Brainstorm H. Like every prior sandbox
(V_gamma → V_delta → V_epsilon → V_zeta), V_eta is iterated against real curation
corpora until ready to be promoted to a stable `V1`.

This document specifies the **differences** from V_zeta. For everything not
listed here — the tiered directory layout (`stable/` / `draft/` / `deprecated/` /
`examples/` / `conversions/`), `index.json` as the resolution source of truth,
resolution-by-`class_name`, the `maturity_level` vocabulary, the
`document_class.schema_version` set-version tag, and the field/dependency object
shapes — the V_delta specification (`V_delta_SPEC.md`) remains authoritative.

The migration story (how `did_v1` corpora convert into V_eta) lives in its
companion, **`V_eta_migration_plan.md`**, together with the resolved design
decisions **D1–D9** referenced throughout this spec.

## Relationship to V_zeta (Brainstorm I)

**V_eta supersedes V_zeta.** V_zeta implemented Brainstorm **I** — a single thin
`subject_interaction` spine, direction via the empty `observation`/`manipulation`
classes, observation leaves named by data-type (shape) with identity on the
`variable` term, a shaped `time_reference`, **Path T** locus (`target_structure`
on the spine), and a `dataseries_observation` branch. On `main`, V_zeta is
preserved as an archived reference.

Brainstorm J keeps I's load-bearing idea — **identity is off the class; the
data-type/shape is the leaf and the property rides on `variable`** — and rebuilds
the **subject side** around it. V_eta therefore begins as a copy of V_zeta's
content (`based_on: "V_zeta"`) with the §§1–8 transform applied; the
design-neutral infrastructure (§9) is reused verbatim.

The meta-schema (`did_schema_meta.json`) gains **one** addition: the `binding`
block is formalized (previously advisory inside the open `constraints` object),
because V_eta hard-validates controlled vocabularies (§7, D9).

---

## Differences from V_zeta

### 1. `subject` is a bare identity card (`stable/`, → v3.0.0)

`subject` loses `is_group` and `is_biological`; it is now `local_identifier` +
optional `description` and **no `depends_on`**.

- *Group-ness* is derived from the relationship graph (a subject is a group
  because `member_of` edges point at it), not a flag.
- *Kind* (organism / device / culture) is a `subject_assertion` carrying an
  ontology `term`; "biological" is derived from whether that term sits under an
  organism branch. Kind's **presence** is an ingestion-layer invariant; its
  **vocabulary** is hard-validated by a `variable`-keyed binding (§7, D9).
- **Any level is a subject** — organism, slice, neuron, region, group, or a
  device. There is no privileged level; this is the premise Path S (§4) rests on.

### 2. `subject_relation` — relationships are documents (`stable/`, NEW)

A new abstract branch off `base`, sibling to `subject_statement`:

```
subject_relation      (abstract, isa base)
├── directed_relation      ordered child → parent
│     child  → subject   (mustBeNonEmpty)   the finer/subordinate subject
│     parent → subject   (mustBeNonEmpty)   the whole / group / source
│     relation { node, name }               enumerated: part_of · contained_in ·
│                                            member_of · derived_from · aliquot_of ·
│                                            sample_of · passage_of
└── undirected_relation    unordered pair
      subjects → subject   (mustBeNonEmpty, multiple, exactly 2)
      relation { node, name }               enumerated: paired_with · same_as
```

- Endpoints are typed `depends_on` (referential integrity is automatic;
  "what links to X?" is reverse-`depends_on`). Relations are **binary** — a
  many-way group is a reified `subject` + `member_of` edges, never a list.
- Each class **enumerates** its permitted `relation` terms (a small closed set,
  RO-backed — D6); no registry is needed for relations. Directed relations feed
  the containment/provenance **ancestry spine**; undirected relations are lateral
  (`same_as` additionally makes search *unify* the two records).
- **Declared minimal for V_eta (D6):** only the corpus-exercised terms —
  `part_of` and one provenance term — are wired in the migrator; the remaining
  designed terms are declared but exercised only by forward-looking authoring.
- V_zeta's event-sourced relation classes (`group_assignment`, `placement`,
  `derivation`) are **re-cast** as `subject_relation` documents.

### 3. `subject_statement` restored; identity fields move up (`stable/`)

`subject_statement` (abstract, isa `base`) is **restored** as the parent that
owns `variable`, `value`, and *optional* `time_reference`, so **identity search
spans assertions and interactions** in one query. Its two children:

```
subject_statement    (abstract)   variable + value (+ optional time_reference)
├── subject_assertion (abstract)  a timeless fact — no act, no series (§5)
└── subject_interaction (abstract) TIGHTENS time_reference to required; ADDS method,
                                    sample_time, optional instrument_id (§4, §6)
```

### 4. `subject_interaction` re-rooted; direction renamed; Path S (§4)

- `subject_interaction` is re-rooted under `subject_statement`. It **adds**
  `method` (the verb, optional), the per-sample `sample_time` cadence (§6, D1),
  and an optional `instrument_id → subject` dependency (§8, D2); it tightens
  `time_reference` to **required**.
- The direction classes are renamed **`subject_observation`** and
  **`subject_manipulation`** (from `observation`/`manipulation`). `annotation` is
  removed (its `group_assignment` becomes a `subject_relation`).
- **Path S replaces Path T.** `target_structure` is **removed** from the spine. A
  structure a value is *attributed to* becomes its own `subject` + a `part_of`
  `directed_relation` (the interaction's `subject_id` is the part, because the
  value describes the part); a structure that is merely *located* is a
  `term_observation` value whose `variable` is a spatial relation
  (`primary_target`, `field_of_view_contains`, `confirmed_location`) and whose
  value is the atlas term. A brain region is normally an address (a value), not a
  subject.

### 5. `subject_assertion` — timeless facts, typed by data shape (`stable/`)

`subject_assertion` becomes an **abstract genus** under `subject_statement`
(was a single concrete class under `base` in V_zeta), with leaves named by data
type — the same rule as the observation tier (§7 leaf tier):

- `term_assertion` (any `{node, name}` — species, sex, strain, a region),
  `date_assertion` (date of birth — a real `date`), and `numeric_assertion`
  (abstract) → the dimensioned assertion leaves (`mass_assertion`,
  `temperature_assertion`, …) using the **atomic (non-series) subset** of the
  data-type library.
- An assertion carries `variable` + `value`, **no `method`, no series**; its time
  is optional. The bundled openMINDS subject is not stored — it decomposes into
  component assertions at ingest.

### 6. The leaf tier — one class per data type (`stable/`)

The Brainstorm-J core, and the biggest structural change from V_zeta. **A leaf
class = a direction + a data type**, named after the data type in one word:

- **No `scalar_` prefix.** `scalar_mass_observation` → `mass_observation`;
  `scalar_temperature` (shape mixin) → `temperature`; etc.
- **No `scalar_` / `dataseries_` split.** Cardinality and storage are *not* class
  distinctions (J §8: "`temperature` is one class whether it is one reading, a
  series, reused, or file-backed"). A series is a length-N `value` list; where it
  lives is `storage_mode` (§8). V_zeta's whole
  `dataseries_`/`timeseries_`/`imageseries_observation` branch collapses into the
  data-type leaves + `sampled_body`.
- **One `term` type.** V_zeta's `categorical_observation` becomes
  `term_observation` (every `{node, name}` value is the single `term` type).
- **No delivery-method family.** `injection` / `bath` /
  `pharmacological_manipulation` are removed: a drug delivery is a
  data-type-named manipulation (e.g. `dose_manipulation`) whose substance is a
  composite `value` (`dose` = formulation + volume; the named composites
  `chemical` / `formulation` / `dose` carry over), the route rides on `method`,
  the site is Path S. `biological_transfer` is removed (its donor is a provenance
  `directed_relation`, D4). Payload-free acts are `term_manipulation` — **no
  generic escape hatch** (`generic_manipulation` / `generic_scalar_observation`
  do not exist; an un-typed value is flagged at ingest, D8).

The **value cell** (canonical working unit + lossless `source_value` /
`source_unit` / `approximate`) and series-as-cardinality carry over from V_zeta.

### 7. Bindings are hard-validated; the binding registry ships (`stable/`, D9)

V_zeta carried `binding` blocks as *advisory* nudges inside the open
`constraints` object. V_eta makes them **enforced**:

- A **`value_set`** class declares a named admissible set — an ontology root +
  `expansion: descendants`, or an enumerated list.
- A **binding-registry meta-file** maps `variable` (and, on interactions,
  `method` + `variable`) → a `value_set` (for term values) or a leaf class (for
  the shape dispatch).
- The **`binding` block is formalized in `did_schema_meta.json`** (structurally
  validated, no longer advisory).
- Consumer tooling gains an **ontology-aware validator** that resolves a term
  `value` against its bound `value_set` at `Validate=true` time (a
  cached/queryable NCBITaxon / OBI / CL / CHEBI / UBERON / RO hierarchy).
- A small enumerated set of **kind-defining variables** (species, instrument
  type, cell type, material type, developmental stage, …) makes the subject-kind
  ingestion invariant (§1, D9) precise.

This hardens *every* binding — the `term_observation` value binding, the kind
assertion, and the `(method, variable) → leaf` dispatch — not just kind.

### 8. `storage_mode` + `data_body`; timing relocated (`stable/` + `draft/`)

- Every value field carries a machine-set **`storage_mode` ∈ {inline, reference,
  body}** (a sibling discriminator; inline stays `value: […]`).
- **`data_body` (abstract)** → **`sampled_body`** (self-describing: a
  `sample_time` axis + typed `datum` + `summary`; partial-readable,
  value-searchable) and **`opaque_body`** (uninterpreted bytes; descriptor-only).
  Supersession: `sampled_body` ← V_zeta `dataseries_data` (+ its
  `timeseries_`/`imageseries_` leaves) and the DAQ-path `element_epoch`;
  `opaque_body` ← `generic_file` and `expression_matrix_data`.
- **Timing (D1).** The **anchor** (frame + t0, the queryable min/max) stays in the
  referenced `time_reference`; the per-sample **cadence** is a compressed
  descriptor (`point` / `{t0, dt, n}` grid / `offsets[]`) **beside the value** —
  a `sample_time` on the statement for inline values, `sampled_body.sample_time`
  for body-backed. V_zeta's `time_reference.sampling` is removed; the body is the
  single home of a body-backed value's timeline.
- **Individuated referent (D2).** V_zeta's `element_id → element` is retired. The
  measuring/manipulating device is a **`subject`** (kind asserted), linked by an
  optional typed **`instrument_id → subject`** on `subject_interaction`. There are
  **no kind-subclasses** (organism/cell/instrument/medium) — kind is a
  `term_assertion`, role is the typed edge (`subject_id` = patient,
  `instrument_id` = agent, `method` = verb). `ndi.element` survives inside
  NDI-matlab as an implementation detail; the schema-layer referent is
  `instrument_id`.

### 9. Preserved infrastructure (verbatim)

The value-cell composites (`mass`/`temperature`/… cells, `term`, `date`,
`score`, `dose`/`formulation`/`chemical`), the `time_reference` frames (minus
`sampling`), and **all non-subject infrastructure** — `base`, session/dataset,
`element`/`epoch*` (NDI-side), `daqsystem`/`daqreader*`, `stimulus_*`, the
tuning/response calculators, `openminds*`, `ontology_*`, `zarr`/`image*`,
`probe_*` — carry over from V_zeta. The V_zeta deprecations stay deprecated.

---

## Resolved decisions

The load-bearing forks are resolved in `V_eta_migration_plan.md` Part E (D1–D9):
timing (D1: cadence beside the value), individuated referent (D2:
instrument-as-subject, no `element_id`, no kind-subclasses), Path S scope (D3:
measure first), transfer donor (D4: provenance relation), locus/label terms (D5:
`term_observation`), relation vocabulary (D6: declare the minimum), closure index
(D7: ingestion-layer, not schema), payload-free manipulations (D8:
`term_manipulation`, no escape hatch), and subject kind (D9: bound
`term_assertion`, hard vocabulary validation + registry from day 1).

## Promotion to V1

Same procedure as prior sandboxes: copy `schemas/V_eta/` to `schemas/V1/`, freeze
it, replace the `"V_eta"` value in `schema_version`/`index.json`, and tag. Before
promotion the `draft/` families (the `sampled_body`/`opaque_body` data-format
descriptors, the genomics/omics endpoints) are exercised against real corpora and
re-tiered to `stable/`.
