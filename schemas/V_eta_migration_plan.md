# V_eta migration plan — `did_v1` → V_eta (Brainstorm J)

**Status:** proposal, awaiting team approval. Nothing here is built yet.
**Implements:** Brainstorm **J** — "the subject model, and one class family for
everything about a subject"
(`ndi-next-steps/Summer 2026/1_Ingestion/20260615/Brainstorm_J_Subject_Model.md`,
issue #69), developed from Brainstorm H.
**Supersedes as sandbox direction:** V_zeta (Brainstorm I). V_zeta is kept on
`main` as an archived reference, exactly as V_epsilon was kept when V_zeta landed.

This is the **plan document** the maintainers asked for before any code is
written. It has two jobs:

1. **Define the V_eta target** as a set of *differences from V_zeta* (Part A) —
   enough to anchor the migration, not the full class-by-class SPEC. The full
   `V_eta_SPEC.md` + the `schemas/V_eta/` tree are the first implementation step
   *after* this plan is approved.
2. **Specify how a `did_v1` corpus is converted into V_eta** (Parts B–E) — the
   per-class mapping, the genuinely new migrator machinery Brainstorm J forces,
   the open decisions that need a team call, and the DID-matlab / NDI-matlab
   build-and-test phasing.

Throughout, **`V1` = `did_v1`**: our sole production document version. V_alpha…
V_zeta never shipped, so — as with every prior sandbox — `conversions/from_did_v1/`
is the only conversion tree, and the real corpora (JH, Dab, B, PRED, Soph,
20211116) are the acceptance test.

---

## Part A — What V_eta is (the Brainstorm-J deltas vs V_zeta)

V_zeta implemented Brainstorm I: **one thin `subject_interaction` spine**,
direction carried by empty `observation`/`manipulation` classes, observation
leaves named by **data-type (shape)** with identity on the `variable` ontology
term, a **shaped `time_reference`**, **Path T** locus (`target_structure` on the
spine), and a `dataseries_observation` branch.

Brainstorm J keeps I's best idea — **identity is off the class; the data-type/
shape is the leaf and the property rides on `variable`** — and rebuilds the
**subject side** around it. The changes below are the whole delta; everything
not listed carries over from V_zeta verbatim (§A.9).

### A.1 The class tree (target)

```
base
├── time_reference          (abstract)
├── subject                                ◄ CHANGED    bare identity (drop is_group / is_biological)
├── subject_relation        (abstract)     ◄ NEW        relationships are documents
│   ├── directed_relation                  ◄ NEW        ordered child → parent (containment, provenance)
│   └── undirected_relation                ◄ NEW        unordered { a, b } (association)
└── subject_statement       (abstract)     ◄ RESTORED   owns variable + value (+ optional time)
    ├── subject_assertion    (abstract)    ◄ RE-ROOTED  timeless facts, now a data-typed genus
    │   ├── term_assertion
    │   ├── date_assertion
    │   └── numeric_assertion (abstract)
    └── subject_interaction  (abstract)    ◄ RE-ROOTED  timed; adds method, time required
        ├── subject_observation    (abstract)   ◄ RENAMED   (was observation)
        └── subject_manipulation   (abstract)   ◄ RENAMED   (was manipulation)
```

*Leaf classes (examples, not exhaustive) — a leaf = a direction + a data type,
named after the data type (one word, no `scalar_` prefix):* **assertions** —
`term_assertion`, `date_assertion`, `numeric_assertion` → `mass_assertion`,
`temperature_assertion`, …; **observations** — `temperature_observation`,
`mass_observation`, …, the single `term_observation` (every `{node, name}`
value), and body-backed `image_observation` / `matrix_observation` for large
data; **manipulations** — `temperature_manipulation`, `dose_manipulation`,
`term_manipulation`, …. The `◄` markers are relative to V_zeta; any class not
marked carries over unchanged. There is **no** `scalar_`/`dataseries` class split
and **no** `injection` / `bath` / `categorical_observation` — those are V_zeta
(Brainstorm I) names; the leaf tier is rebuilt per J in §A.9.

`subject_relation` and `subject_statement` are **siblings** (a relation has no
`variable`/`value`; a statement has no `from`/`to`). What unifies "everything
about subject X" is not a shared parent but `depends_on`: every relation and
every statement records its subject, so it is one reverse-`depends_on` lookup.

### A.2 `subject` → a bare identity card  ◄ the load-bearing subject change

- **Remove `is_group` and `is_biological`** (both are `subject` fields in
  V_zeta v2.0.0). `subject` becomes `local_identifier` + optional `description`,
  **no `depends_on`**. → `subject` v3.0.0.
- *Group-ness* is derived from the relationship graph (a subject is a group
  because `member_of` edges point at it). *Kind* (organism / device / culture)
  is a `subject_assertion` carrying an ontology `term`; "biological" is derived
  from whether that term sits under an organism branch.
- **Any level is a subject** — organism, slice, neuron, region, group. There is
  no privileged level. This is the premise Path S (A.6) rests on.
- **Kind is a bound `term_assertion`, not a field** (D9). A subject's kind
  (species, device type, cell type, material) is a `term_assertion` whose `value`
  is constrained to a suitable ontology subtree by a `variable`-keyed binding
  (species → NCBITaxon, instrument → OBI device, …). Its **presence is an
  ingestion-layer invariant**, not a schema field-requirement — a separate
  document's existence can't be required by the subject's own per-document
  validation, and some subjects' kind is derived (groups) or learned later.

### A.3 `subject_relation` — relationships are documents  ◄ NEW

Two concrete shapes, endpoints as typed `depends_on` (so referential integrity
is automatic and "what links to X?" is reverse-`depends_on`):

- **`directed_relation`** — ordered **`child` → `parent`** (`child` = the
  finer/subordinate subject; `parent` = whole/group/source). `relation` is an
  ontology term the class **enumerates** (no registry):
  - *containment* — `part_of` · `contained_in` · `member_of`
  - *provenance* — `derived_from` · `aliquot_of` · `sample_of` · `passage_of`
  - Both feed the **ancestry spine** (data on the child counts as data of the parent).
- **`undirected_relation`** — unordered `subjects: [a, b]`, `relation` ∈
  *association* (`paired_with` · `same_as`). Lateral, no spine; `same_as`
  additionally makes search **unify** the two records.

Relations are **binary** — a many-way group is a reified `subject` + `member_of`
edges, never a list frozen in one document. `sibling_of` is derived, not stored.

### A.4 `subject_statement` restored; identity fields move up  ◄ CHANGED from V_zeta

V_zeta removed `subject_statement` and put `variable`/`value`/`time_reference`
on `subject_interaction`. J **restores `subject_statement`** as the abstract
parent that owns `variable`, `value`, and *optional* `time_reference`, so
**identity search spans assertions and interactions** in one query
(`variable = species, subject = X` finds it whether it was asserted or observed).

### A.5 `subject_assertion` — timeless facts, typed by data shape  ◄ CHANGED

V_zeta's `subject_assertion` is a single concrete class under `base` with
`asserted_property` / `value` / `source` ontology terms. J makes it an
**abstract genus under `subject_statement`**, with leaves named by data type
(the same rule as the observation tier):

- `term_assertion` (any `{node, name}` — species, sex, strain, a UBERON region),
  `date_assertion` (date of birth — a real `date`, not a duration),
  `numeric_assertion` (abstract) → dimensioned `mass_assertion`,
  `temperature_assertion`, … using the **atomic (non-series) subset** of the
  data-type library. One-word data-type names, **no `scalar_` prefix** (§A.9).
- An assertion has a `variable` + `value` and **no `method`, no series**; its
  time is optional. It is the untimed sibling of `subject_observation`.
- The bundled openMINDS subject is **not** stored — it decomposes into component
  assertions at ingest; openMINDS survives as vocabulary + a derived projection.

### A.6 Locus: Path S replaces Path T  ◄ the migration-defining reversal

V_zeta chose **Path T** (`target_structure` ontology term on the spine; the
subject stays the whole specimen) *specifically because Path S needs a standing
find-or-create/dedup service under minted subject UIDs* (V_zeta_notes, "Locus:
Path T"). **Brainstorm J commits to Path S** and to the rule that disambiguates
it:

- **`target_structure` is removed from the spine.**
- **A structure a value is *attributed to* is a `subject`**; a structure that is
  merely *located* is a **value**:
  - *attributed-to* (you cool V1, you record from CA1) → the part is its own
    `subject`, `part_of` the specimen via a `directed_relation`; the interaction's
    `subject_id` is the **part**, because the value describes the part.
  - *merely located* (the FOV also caught the liver) → a `term_observation`
    whose `variable` is a spatial relation (`primary_target`,
    `field_of_view_contains`, `confirmed_location`) and whose value is the atlas
    term. A brain region is **normally an address (a value), not a subject** —
    minting "CA1-of-mouse-042" for every animal would explode identity and break
    cross-animal search.

The migration consequence is large and is the crux of Part C: converting a
`did_v1` `target_structure`/anatomy column is no longer a field copy — it is a
*decision* (attributed vs located) and, in the attributed case, a **stateful
mint-and-dedup of part-subjects + relations** across the corpus.

### A.7 `storage_mode` + `data_body` — one storage model  ◄ CHANGED (consolidation)

J replaces V_zeta's several body/epoch classes with one axis:

- Every value field carries a machine-set **`storage_mode` ∈ {inline, reference,
  body}** (a *sibling discriminator*, not an envelope — inline stays `value: […]`).
- **`data_body` (abstract)** → **`sampled_body`** (self-describing: a
  `sample_time` axis + typed `datum` + `summary`; partial-readable,
  value-searchable) and **`opaque_body`** (uninterpreted bytes; descriptor-only,
  load-only). A body reverse-`depends_on`s its statement, so a stream appends
  bodies without rewriting the anchor.
- **The body is the single home of a body-backed value's timeline** (D1). For
  `storage_mode: body` the statement carries **no** `sample_time` (only the anchor
  `time_reference`); the cadence lives in `sampled_body.sample_time`. That is what
  lets a body be read in windows and **appended as a stream** without joining back
  to — or rewriting — the immutable statement. It is not a duplicate of the
  statement's timeline (the statement has none for body values); it is the one
  copy. Each appended body owns its own time slice, so streaming never rewrites the
  anchor. The absolute anchor (t0, clock) still comes from the shared
  `time_reference`; the body restates only the cadence + its local offset.
- **Supersession:** `sampled_body` ← V_zeta's `dataseries_data` (+ its
  `timeseries_/imageseries_` leaves) and the DAQ-path `element_epoch`;
  `opaque_body` ← `generic_file` and `expression_matrix_data`.
- Search is unchanged across storage: the projection reads `value` inline or
  walks `statement ← body → summary`, landing the same index record.

### A.8 Value cell, series, and the timing model  ◄ one open reconciliation

- The **value cell** (canonical working unit + lossless `source_value`/
  `source_unit`/`approximate`) and **series-as-cardinality** (`value` is a list;
  a scalar is a length-1 list) carry over from V_zeta unchanged.
- **Timing is where J and I differ, and it is really two questions** (D1):
  **(A) shape** — a literal per-sample array vs a compressible descriptor
  (`point` / `{t0, dt, n}` grid / `offsets[]`); and **(B) location** — does the
  per-sample cadence live *inside* the referenced `time_reference` (V_zeta) or in
  a field *beside the value* on the statement (J's `sample_time`)? On **(A)** both
  agree: always compress (three numbers for a regular grid; an array only when
  genuinely irregular). On **(B)** the plan now leans **J's location + I's
  compression** — the **anchor** (frame + t0, the queryable min/max) stays in the
  shared `time_reference`; the **cadence** is a compressed descriptor co-located
  with the value (on the statement inline, in the body when body-backed). Chiefly
  because co-locating value + cadence makes length-consistency a *single-document*
  check, and a cadence-free anchor stays shareable across values of different
  rates under one clock (multi-rate under one epoch). **Resolved (D1):** anchor in
  the shared `time_reference`; compressed cadence beside the value (statement
  inline / body when body-backed); the body is the single home of a body-backed
  timeline (§A.7).

### A.9 The leaf tier — one class per data type (restructured, **not** carried from V_zeta)

This is the biggest thing V_eta inherits *conceptually* from I but must
**rebuild** structurally. J keeps I's "identity is off the class" insight and
pushes it one step further: **a leaf class = a direction + a data type**, and the
data type is the *only* thing that makes a class (J §5, §7). Three rules follow,
and each undoes a V_zeta habit:

- **Named after the physical quantity, one word, no `scalar_` prefix.** A body
  weight is a `mass_observation` (with `variable = "body weight"`), a temperature
  a `temperature_observation`. V_zeta's `scalar_mass_observation`, … are renamed.
- **Cardinality and storage are *not* class distinctions.** J §8: "`temperature`
  is one class whether it is one reading, a series, reused, or file-backed." There
  is **no** `scalar_<dim>` vs `dataseries_observation` split — a series is a
  length-N `value` list and where it lives is `storage_mode` (§A.7), not a class.
  V_zeta's whole `dataseries_`/`timeseries_`/`imageseries_observation` branch
  collapses into the data-type leaves + `sampled_body`.
- **One `term` type; no `injection`/`bath`/`pharmacological` family.** Every
  ontology-term value is the single `term` type, so V_zeta's
  `categorical_observation` becomes `term_observation`. Delivery *method* is not a
  data type, so it cannot be a class: a drug delivery is a data-type-named
  manipulation (e.g. `dose_manipulation`) whose substance is a composite `value`
  (`dose` = formulation + volume, from J §7's named composites
  `chemical`/`formulation`/`dose`), the route rides on the spine `method` verb,
  and the site is Path S. **Nothing is lost** — the structured fields V_zeta
  welded onto `injection`/`bath` (volume, formulation, route, coordinates, kind)
  re-home into composite values, `method`, and part-subjects.

Payload-free acts (a craniotomy, a rearing regime) have no measured value; under
strict J they are a `term_manipulation` (the imposed value is the act's ontology
term). There is **no** generic escape hatch — `generic_manipulation` and
`generic_scalar_observation` do not survive; an un-typed value is flagged in
discovery mode, never dumped into a generic bin (**Resolved, D8**).

### A.10 What carries over verbatim (design-neutral for J)

The **value-cell composites themselves** (the dimensioned `mass`/`temperature`/…
cells, `term`, `date`, `score`, and the named composites
`dose`/`formulation`/`chemical`), the `time_reference` frames, and **all
non-subject infrastructure** — `base`, session/dataset, `element`/`epoch*`,
`daqsystem`/`daqreader*`, `stimulus_*`, the tuning/response calculators,
`openminds*`, `ontology_*`, `zarr`/`image*`, `probe_*`. The five V_zeta
deprecations stay deprecated. The relational event classes V_zeta introduced
(`group_assignment`, `placement`, `derivation`) are **re-cast as
`subject_relation` documents** (they were already "relations as events"); they
have no `did_v1` source, so this is a forward-looking rename, not a migration.
Note the boundary with §A.9: the *value shapes* carry over; the
*observation/manipulation leaf classes* that wrapped them are renamed and de-split.

**Individuated referents (`element_id`).** V_zeta's optional spine
`element_id → element` (an `ndi.neuron`, a probe, a derived signal) is **kept**
on `subject_interaction` in V_eta as the NDI acquisition-graph handle — distinct
from Path S. The split we propose (**Decision D2**): *anatomical/biological
parts* use the part-subject model (A.6); *NDI elements that back acquired data*
keep the `element_id` handle and their data lives in a `sampled_body`. Migrators
do not populate `element_id` today and will not in the first V_eta pass either.
**Under revision (D2):** the device role is likely to become an
`instrument_id → subject` edge (device-as-subject), retiring `element_id` — see
Part E D2.

---

## Part B — Migration strategy overview

V_eta reuses the existing, target-generic converter unchanged in shape; only new
per-class migrators and one dispatcher branch are added.

- **DID-matlab.** `did2.convert.v1_to_v2(bodies, TargetVersion='V_eta')` dispatches
  each `did_v1` body — after `universalRenames` — to a new
  **`+did2/+convert/+migrators_j/`** package (the letter tracks the brainstorm,
  as `_e`=E, `_i`=I). Add one `elseif strcmp(targetVersion,'V_eta')` branch in
  `runConcreteMigrator` pointing at `did2.convert.migrators_j.`; everything else
  (`isAlreadyTarget` short-circuit, `ensureClassBlocks`, `schema_version`
  stamping, quarantine, reference-integrity via `did2.validate.references`) is
  already version-agnostic. Splits/folds emit a **cell of bodies**; the loop
  lands each as its own document, minting `did.ido.unique_id()` up front so
  intra-batch `depends_on` edges resolve.
- **NDI-matlab.** `ndi.migrate.local` (and `.cloud`) already forward any
  non-`V_delta` target and write `<TargetVersion>.sqlite`. The V_eta-specific
  work here is the **session-context second pass** (Part C.1/C.3): context-
  dependent folds the per-document converter cannot resolve are **deferred**
  (`error('did2:convert:needsSessionContext')`) and re-assembled in
  `local.m`'s `assembleDeferred` using `ndi.migrate.internal.bodyResolver`
  (which holds the whole body/element graph). This is exactly how V_zeta handles
  `stimulus_bath → bath`.
- **Discovery mode is the tuning loop.** `runCorpusDiscovery(…, TargetVersion=
  'V_eta')` downloads a real corpus, runs the converter with `Validate=true`,
  writes the routing-inventory + quarantine reports, and hard-gates on
  reference-integrity (`AssertNoOrphans`). Per-term dispatch tables (Part C) are
  **seeded from these reports, not guessed** — report-only before any rewrite.

**Cardinality shifts vs V_zeta.** Every `did_v1` document that carries an
attributed anatomical locus now emits **extra documents** (a part-`subject` +
one `directed_relation` per distinct part), on top of V_zeta's split/anchor
fan-out. A single thermal `treatment` on V1 goes `1 → 4` in V_eta (manipulation
+ time anchor + V1 part-subject + `part_of` relation) where it was `1 → 2` in
V_zeta. The dedup service (C.1) keeps the part-subject and relation counts
*per-animal-per-region*, not per-row.

---

## Part C — New machinery Brainstorm J forces (not in any prior migrator)

These four capabilities do not exist in `+migrators_e/` or `+migrators_i/`. They
are the real cost of J and the reason the plan comes before the code.

### C.1 Part-subject find-or-create + relation minting (Path S) — the standing service

**The problem V_zeta's Path T deliberately dodged.** Under Path S, an interaction
"of V1" must point `subject_id` at a **V1 subject**, which must exist, be
**deduplicated per animal** (one `V1-of-mouse-042`, reused across every V1
recording in the corpus), and be tied to the animal by a `part_of`
`directed_relation`. This is stateful across the whole batch.

**Proposed mechanism** (`ndi.migrate.internal` — needs the corpus-wide view, so
it lives in the NDI second pass, mirroring bath resolution):

- **Deterministic key.** `key = hash(parent_subject_id, region_CURIE, side?)`.
  The migrator maintains a batch-scoped map `key → minted_subject_id`. First
  sighting mints the part-`subject` (`local_identifier` synthesized as
  `<animal_local_id>::<region_name>[::<side>]`) **and** a `directed_relation`
  (`child = part`, `parent = animal`, `relation = part_of`); later sightings
  reuse the id. This resolves J §10-Q5 ("consistent sub-subject identifiers")
  the only way that keeps cross-animal search working: the *identifier* is
  synthetic and per-animal, but the *region term* stays a shared value on the
  observations for cross-animal queries.
- **Attributed vs located dispatch** (A.6) is a **per-term routing table**,
  seeded in discovery mode exactly like `treatment`'s branch table. Default when
  unresolved: **located** (emit a `term_observation` value, do *not* mint a
  subject) — the conservative choice, since minting a spurious subject is harder
  to undo than promoting a value later.
- **Corpus reality check first.** Before building this, the discovery reports
  must quantify how many `did_v1` rows actually carry an anatomical locus
  (`treatment.string_value` UBERON CURIEs — the Dab optogenetic-tetanus rows —
  and `ontology_table_row` anatomy columns). If the count is small, a
  narrower "located-by-default, mint only on an allowlist" policy may be enough
  for the first pass. **This is Decision D3.**

### C.2 Assertion-vs-observation routing (timeless facts → `subject_assertion`)

V_zeta routes *every* `ontology_table_row` column to the **observation** tier
(species → `categorical_observation`; DOB → `scalar_duration_observation`). J
splits the destination by **timelessness**:

- **Timeless fact, no act** → `subject_assertion`: species/sex/strain/genotype →
  `term_assertion`; date of birth → `date_assertion` (a real date, an
  improvement over V_zeta's duration-since-epoch); a timeless numeric → a
  `numeric_assertion` leaf.
- **Timed measurement** → `subject_observation`, a quantity-named leaf (body
  weight → `mass_observation`; term-valued label → `term_observation`) — see §A.9
  for the naming.

The classifier is a **per-property table** keyed on the column's `variable`
term (seeded in discovery mode). Because `subject_statement` owns `variable`,
both destinations remain findable by one identity query — so a mis-route is
low-stakes and correctable, not a data-loss event.

### C.3 Relations synthesized from legacy edges / flags

Only a few `did_v1` constructs produce V_eta relations (most relation surface is
forward-looking):

- **`subject_group` → a bare `subject`.** No `is_group` flag; group-ness is
  derived. `did_v1` records **no membership** (the body is an empty marker), so
  **no `member_of` edges are synthesized** — inventing them would fabricate
  data (unchanged conclusion from V_zeta, new destination shape).
- **`treatment_transfer` donor.** V_zeta kept a dedicated `biological_transfer`
  class carrying a `donor_id` dependency. Under strict J that class does not
  survive (a transfer is not a data type): the act becomes a data-type-named
  manipulation (term-valued) and the donor relationship becomes a **provenance
  `directed_relation`** — recipient material `derived_from`/`sample_of` donor.
  **Resolved (D4):** the donor is a provenance `directed_relation`; the transfer
  act is a term-valued manipulation — no `donor_id`-on-manipulation and no
  `biological_transfer` class.
- **Attributed anatomical parts** (C.1) — the one place relations are minted at
  volume.

### C.4 `data_body` consolidation + `storage_mode` stamping

- **`image_stack`** (V_zeta's most elaborate fold, `1 → 6`: imageseries handle +
  element + `element_epoch` + `daqreader_image_epochdata_ingested` + `daqreader`
  + anchor) re-targets in V_eta to: a **`subject_observation`** on an image/matrix
  data-type leaf (body-backed — there is **no** `imageseries_observation` class in
  J, §A.9) + an **`element`** + a **`sampled_body`** (or `opaque_body` for an
  un-decodable stack) holding the frames, carrying `storage_mode: body`. Net fold
  likely `1 → 4/5` (the `element_epoch` + ingested-frames pair collapses into one
  `sampled_body`). This is the main `did_v1` class exercising the new storage model.
- Every emitted value field gets its **`storage_mode`** set mechanically by type
  and size (scalars/terms/dates → `inline`; large/opaque → `body`). Curators
  never choose; the migrator sets it.
- The dataseries/expression/omics branches are **draft** in V_zeta and largely
  NDI-side ingest, not `did_v1` corpus content, so their reshape onto
  `sampled_body`/`opaque_body` is a schema-tree task (Phase 1), not a heavy
  migrator task.

---

## Part D — Per-class mapping (`did_v1` → V_eta)

The **universal renames** (underscore-strip, `document_class` nesting,
snake_case, superclass-ref reshape, `maturity_level` enum, ontology 4→2-key,
class-scoped blocks, `depends_on.id → document_id`, `schema_version` stamp) are
**unchanged from V_zeta's `_universal_renames.md`**, except the stamp value is
`"V_eta"`. The one V_eta-specific universal addition: the migrator may **emit a
`subject_assertion`/part-`subject`/`directed_relation` alongside** the primary
output (fan-out), which the framework already supports.

### D.1 Hard transforms (subject-side restructuring)

| `did_v1` source | V_eta destination(s) | What changes vs V_zeta | Card. |
|---|---|---|---|
| `treatment` | a data-type-named `subject_manipulation` — `dose_manipulation` (substance), `temperature_manipulation` (thermal), another `<quantity>_manipulation`, or `term_manipulation` (payload-free procedure/regime) **+ time anchor**, **+ part-`subject` + `part_of`** when the site is attributed, **or** a `term_observation` location value when merely located | **no `injection`/`bath`/`generic_manipulation` (§A.9)** — route → `method`, substance → `dose` composite value; **`target_structure` → Path S (C.1)** | 1→2…4 |
| `ontology_table_row` | per column: a `subject_assertion` leaf (timeless) **or** a `subject_observation` leaf (timed) + shared anchor; anatomy column → Path S (C.1) | **timeless columns → `subject_assertion` (C.2)**; scalar columns → quantity-named `mass_observation`/`temperature_observation`/… (**no `scalar_` prefix**); term columns → `term_observation` (**not `categorical_observation`**); DOB → `date_assertion` | 1→N(+1) |
| `subject_group` | bare `subject` (v3.0.0) | **`is_group`/`is_biological` removed (A.2)**; no membership edges | 1→1 |
| `treatment_drug` | `dose_manipulation` (substance = `dose`/`formulation` composite; drug identity on the chemical term) + anchor; site → C.1 | **not `injection`** — `mixture`/CSV parse feeds the `formulation` composite; route → `method` | 1→2…3 |
| `virus_injection` | `dose_manipulation` / `formulation_manipulation` (virus on the chemical term; titer/dilution in the composite) + anchor; site → C.1 | as above; **not `injection` (`kind: virus`)** | 1→2…3 |
| `treatment_transfer` | a `term_manipulation` for the transfer act **+ a provenance `directed_relation`** (recipient material `derived_from`/`sample_of` donor) + anchor | **not `biological_transfer`** — donor → relation, transferred material → value/term (D4) | 1→3…4 |

### D.2 Locus / label terms → `term_observation` (Decision D5)

`probe_location`, `ontology_image`, `ontology_label` each attach an ontology term
to an element (a probe's anatomical location; a region term on an image; a label
on an element). Per **Decision D5**, these become **`term_observation`s** rather
than carried-over composite-term classes: `element_id`/`subject_id` = the element,
`variable` = the spatial/labeling relation (`location`, `field_of_view_contains`,
`annotated_as`, …), `value` = the atlas/label term (the same `ontology_name`+`name`
collapse, now landing in the observation's `value`). Each needs a time anchor
(synthesized `session_relative_reference`, as elsewhere), so 1→1 becomes 1→2; any
associated file (e.g. `ontology_image`'s image) becomes an `opaque_body` /
`sampled_body` (§A.7). A genuinely timeless label may instead be a
`term_assertion`; the default per D5 is `term_observation`.

### D.3 Mechanical (renames / snake_case / type-tightening — design-neutral)

All 14 tuning/calculator classes (`contrast_tuning`(+`_calc`),
`contrast_sensitivity_calc`, `orientation_direction_tuning`/`oridirtuning_calc`,
`spatial_frequency_tuning`(+`_calc`), `speed_tuning`(+`_calc`),
`temporal_frequency_tuning`(+`_calc`), `reverse_correlation`,
`hartley_reverse_correlation`, `hartley_calc`) **carry over verbatim** from the
V_zeta conversions — they are infrastructure with no subject-side surface, just
as V_zeta reused them from V_epsilon.

---

## Part E — Open decisions for the team

Approve or redirect these before implementation; each is a genuine fork, not a
default we can quietly pick.

- **D1 — Timing model (two axes). Resolved.** **(A) shape:** always compress
  (`point` / `{t0, dt, n}` grid / `offsets[]`), never a literal N-array when
  regular. **(B) location:** anchor in the shared `time_reference`; compressed
  **cadence beside the value** (statement inline / body when body-backed), *not*
  welded into `time_reference` — single-document length-consistency, cadence-free
  shareable anchor, body owns its own timeline (§A.7, A.8). (A.8)
- **D2 — The measuring/manipulating device: an instrument-as-subject (replacing
  `element_id`).** *Brainstorm direction (supersedes "keep element_id"):* a device
  (probe, electrode, microscope, Peltier, pump, stimulator) is a **`subject`**
  (bare identity; its kind asserted via a `term_assertion` = an OBI/NCIT device
  term — J's "a subject is a *tungsten electrode*" case), and a measurement or
  manipulation links to it by an **optional typed `instrument_id → subject`**
  dependency on `subject_interaction`. This **retires `element_id`**: the device
  role → an instrument-subject; the derived-signal role of `element` (spikes, LFP)
  → a body-backed `subject_observation` + `derived_from` provenance; the
  `ndi.neuron` role → a subject. No new top-level class is required (pure J: kind
  is an assertion, not a class); an optional `instrument` **subclass** of `subject`
  is available only if a cheap class-level "list all devices" filter is wanted, in
  which case the draft V_zeta `instrument` class becomes that subclass.
  **Roles are carried by the typed edges, not by a subclass:** `subject_id` is the
  patient (measured/acted on), `instrument_id` is the agent (the device that
  performed the `method`), `method` is the verb, observation-vs-manipulation is the
  direction — so "the instrument performed the method on the subject" is explicit
  with no kind-class. On **kind-subclasses** (organism / cell / instrument / medium
  / …): *lean against a taxonomy* — J keeps `subject` bare and puts kind in a
  `term_assertion` (finer than a class: *Mus musculus*, not "organism"; refinable
  and multi-valued; and kinds don't map to classes cleanly — a substance/medium is
  usually a `formulation` **value**, a region an address value, a group derived from
  edges). The one narrow exception worth a class is a single **`instrument`
  subclass of `subject`** (the one kind referenced by a typed edge and wanting a
  cheap `isa` filter). **Resolved:** device-as-subject + optional typed
  `instrument_id → subject`; **no kind-subclasses** (kind via `term_assertion`,
  role via the typed edges); `element_id` retired. Kind requiredness + vocabulary
  → **D9**. `element` dissolution at the schema layer is deferred (`ndi.element`
  stays an NDI-matlab implementation detail; migrators populate no individuated
  referent in pass 1). (A.10)
- **D3 — Path S scope for the first pass. Resolved + measured.** *Measure before
  we build.* Discovery on B/Dab (`V_eta_discovery_notes.md`) found the
  attributed-locus volume is **small — 49 loci in Dab (all distinct subjects), 0
  in B** — so **located-by-default** (emit a `term_observation` value, mint no
  subject) + a mint allowlist is sufficient; the full find-or-create/dedup service
  is **not warranted** for these corpora. Re-confirm against JH before locking. (C.1)
- **D4 — `treatment_transfer` donor. Resolved:** a provenance `directed_relation`
  (recipient material `derived_from`/`sample_of` donor); the transfer act is a
  term-valued manipulation. No `donor_id`-on-manipulation, no `biological_transfer`
  class. (C.3)
- **D5 — Element/probe location terms. Resolved:** → `term_observation`
  (`probe_location`/`ontology_image`/`ontology_label`): element = subject,
  spatial/labeling relation = `variable`, term = `value`. (D.2)
- **D6 — Relation vocabulary. Resolved: declare the minimum now.** Declare only
  the corpus-exercised terms — `part_of` (Path S) + one provenance term
  (`sample_of`/`derived_from`, `treatment_transfer`) — confirmed by the D3
  discovery reports, RO-backed. J's remaining designed terms (`member_of`,
  `contained_in`, `aliquot_of`, `passage_of`, `paired_with`, `same_as`) have no
  `did_v1` source and are **added only when a source or authoring need appears** (a
  closed-set addition is a cheap version bump). (A.3)
- **D7 — Closure index is tooling, not schema.** J's "everything under X"
  closure index is a materialized view over `directed_relation` documents. The
  current abstract query model (`did_query_model.md`) has **no cross-document
  join beyond `depends_on` and no closure** — so the closure index is a
  consumer-side index (NDI framework), declared but not schema-enforced, and the
  fallback is a bounded reverse-`depends_on` walk. **Resolved:** yes — this is an
  **ingestion / consumer-layer** materialised view, built and incrementally
  maintained at ingest by the NDI framework; it is **not** schema-enforced and not
  part of the abstract query model (which has no join/closure). Stays out of the
  schema layer.
- **D9 — Subject kind: requiredness + controlled vocabulary.** Kind stays a
  `term_assertion` (per J — provenance-blind, refinable, multi-valued), **not** a
  field on the bare `subject`. **(i) Requiredness:** a subject cannot require, via
  its own per-document validation, that a separate kind-assertion *exist* — a
  reverse-existence / cross-document constraint neither the meta-schema nor the
  query model expresses. So "every subject has a kind" is an **ingestion-layer
  invariant** (consumer tooling, like the D7 closure index), applied to primary
  entities (organisms, devices, samples) and *not* to derived-kind subjects
  (groups) or genuinely-unknown ones. **(ii) Vocabulary:** the kind assertion's
  `value` is constrained to an ontology subtree by a `variable`-keyed **binding**
  (the same soft-nudge machinery as `categorical`/`term_observation` in V_zeta) —
  `variable = species` → NCBITaxon descendants, `variable = instrument type` → OBI
  device descendants, etc. **(iii)** Optionally enumerate a small set of
  **kind-defining variables** (species, instrument type, cell type, material type,
  developmental stage, …) so the (i) invariant is precise. **Resolved: hard
  validation from day 1 — do not defer the registry.** V_eta ships the
  **binding-registry / `value_set`** machinery in Phase 1 (V_zeta deferred it):
  a **`value_set`** class (a named admissible set = an ontology root + `expansion:
  descendants`, or an enumerated list), a **binding-registry meta-file** mapping
  `variable` (and, on interactions, `method`+`variable`) → `value_set` / leaf, the
  **`binding` block formalized in the meta-schema** (no longer advisory in the open
  `constraints` object), and an **ontology-aware validator** that resolves a
  document's term `value` against the bound `value_set` at validation time.
  **Scope note:** this hardens *every* binding, not just kind — the
  `categorical`/`term_observation` value binding and the `(method, variable) → leaf`
  nudge all become validated, and the validator gains an ontology-resolution
  dependency (a cached/queryable term hierarchy for NCBITaxon, OBI, CL, CHEBI,
  UBERON, RO). The (i) subject-kind *presence* check stays an ingestion invariant
  (still cross-document); day-1 hard validation covers the *vocabulary* (ii). (A.2,
  A.5, Part F)

  **Extension — the registry as a general type oracle for open parameters.**
  The Phase-1 registry types *closed* things (kind assertions, `categorical`/
  `term_observation` values, the `(method, variable) → leaf` nudge). D10 adds **open,
  author-supplied parameters** (the `parameters` field on `subject_statement`): they
  have no schema-fixed leaf, yet still need a data type and admissible set. The
  extension keys the registry on the parameter's `variable` and returns a **data type
  + `value_set`**, so an open `arm direction`, `OD600`, or `trial type` validates
  exactly like a bound term value would. The one invariant is the cardinality rule: a
  parameter's value length is 1 or the measurement's value length. This is what lets
  D10 claim "every field is validated by data type" even for the open columns.
  *Status:* **needed now that D10 adopts parameters** — the remaining choice is the
  parameter **value representation** (uniform `{variable, value}` resolved by the
  registry vs a nested typed block). No change to the Phase-1 closed-binding
  machinery, which ships as Resolved above. (A.2, A.5, D10, D11)
- **D8 — Payload-free manipulations. Resolved:** `term_manipulation` (imposed
  value = the act's ontology term). **No escape hatch** — strict J resolves every
  act to a data type; an un-typed numeric is flagged/quarantined in discovery
  mode, never dumped into a generic bin. `generic_manipulation` and
  `generic_scalar_observation` do not exist in V_eta. (A.9)
- **D10 — Flat tables: column roles and where a qualifier lives. OPEN — under
  discussion, no option locked.** A `did_v1` `ontology_table_row` is **not** N
  independent subject facts — it is a mini-record whose columns play distinct ROLES,
  and the naive per-column → `subject_observation` split (what
  `+migrators_j/ontology_table_row.m` does today) mis-models most of them: it makes
  "trial type = 95 dB" an *observation of the subject* when it is a **qualifier of**
  the startle-amplitude measurement, and in Dab's elevated-plus-maze it inherits the
  source table's mistake of pre-splitting one measurement across arm types (51
  columns) instead of carrying `arm type` as a covariate. So D10 asks two coupled
  questions — *what role does each column play* (the column-role rule below —
  settled) and *where does the answer get stored* (**decided for now:** a typed
  `parameters` field on `subject_statement`).

  **The column-role rule (the deterministic part we agree on).** Discovery over
  **all 11 distinct table signatures** (Dab fear-potentiated-startle and
  elevated-plus-maze; JH *C. elegans* encounter, bacterial-patch
  fluorescence/geometry, plate-prep conditions, subject↔plate link tables) shows
  every column resolves to exactly one of five roles by a rule a migrator can apply
  without per-table hand-tuning:
  - **Measurement** (a value read off an entity: startle amplitude, arm entries,
    patch fluorescence) → a `subject_observation` leaf, typed by data shape;
  - **Qualifier / condition** (the context the measurement was taken under: trial
    type, phase, chamber, CNO-vs-saline, exclusion flag, OD600, ambient temperature,
    *and the pre-split `arm type`*) → a **trial parameter**, not an observation;
  - **Reference / foreign key** (`BacterialPatchDocumentIdentifier`,
    `MicroscopyImageIdentifier`) → a `directed_relation` / `depends_on`, not a value;
  - **Identity** (the row's subject/entity key) → the anchor, not an observation;
  - **Total / derived** (a row/column sum reconstructable from the others) →
    dropped, not stored.

  The rule is deterministic *given a per-column role label*; producing that label is
  the D11 question below. This is the one piece we treat as settled enough to build
  the classifier against.

  **Where the qualifier lives — the option space (all OPEN).** Eight shapes were
  surveyed against ease-of-curation ("is there exactly one correct way to encode
  this?"), ease-of-analysis, and honesty about the science:
  1. `qualifiers` list of `{variable, value}` bolted onto each
     `subject_observation` — self-contained and directly queryable, but denormalizes
     the condition onto every response and gives two authors two ways to encode the
     same trial;
  2. a **trial/epoch event** document the responses and manipulations `depend_on` —
     owns the shared `time_reference` and the conditions once, links
     observations↔manipulations, and can span multiple entities;
  3. **covariate → value axis** — a multi-dimensional reading keeps the varying
     condition as an *axis* of the value cell (J-native: the arm-type split collapses
     back into one `entries` measurement indexed by an `arm type` axis);
  4. reuse `stimulus_presentation` / `stimulus_response` for stimulus-driven assays;
  5. condition-as-subject (a `subject` per condition, measurements relate to it);
  6. a free `conditions` block on the session/epoch anchor only;
  7. per-condition document sets keyed by a shared tag;
  8. leave it flat (status quo) and push disambiguation entirely to the consumer.
  **Decided (for now): one `parameters` field on `subject_statement`.** Options 1 and
  3 unify into a single mechanism — a `parameters` list of typed `{variable, value}`
  where the value is a data-typed array (term/count/duration/…, the same value cells a
  leaf uses). A **cardinality rule** distinguishes the two cases without a second
  construct: a parameter's value length is **1** (a constant condition — the old
  option-1 "qualifiers list" case) or **equal to the measurement's value length** (one
  label per reading — the old option-3 "axis" case; the EPM `entries` value
  `[8,4,12,9,15]` carries an `arm direction` parameter `[north,south,east,west,center]`
  and an `arm state` parameter alongside). **"Axis" is retired as a separate term** —
  it is just a per-element parameter. The **trial/epoch event (shape 2) is DEFERRED**:
  shared context is handled by copying the parameter onto each measurement plus a
  `directed_relation` for inter-entity ties. In the *C. elegans* encounter (verbatim
  JH columns) the `CElegansBehavioralAssay_EncounterIdentifier` is the encounter's
  *identity* (it rides as a parameter on each worm reading, not as its own doc), OD600
  lives on the referenced patch document (`BacterialPatchDocumentIdentifier`), and a
  `worm --encountered--> patch` `directed_relation` carries the cross-entity tie.
  Revisit a trial/epoch hub only if per-measurement copying of shared context becomes
  painful, or when cross-entity trial-based analysis wants a first-class trial. The
  deferred trial model and the worked mock-ups live in the EDM design note
  (`ndi-next-steps`).

  **How every field still gets validated by data type (the tie to D9).** Parameter
  values are *open* (author-supplied `variable`s, not schema-fixed leaves). The answer
  is the **D9 binding registry acting as a type oracle**: a parameter keyed on its
  `variable` resolves through the registry to a data-type + `value_set`, so
  `arm direction ∈ {north, south, east, west, center}`, `OD600 ∈ non-negative real`,
  `trial type ∈ <startle-protocol value_set>` are all checkable at validation time —
  the same machinery that types kind-assertions, just pointed at parameters. The one
  invariant is the cardinality rule: a parameter's value length is 1 or the
  measurement's value length. See the D9 extension below.

  *Status:* **DECIDED (for now)** — qualifier placement is a typed `parameters` field
  on `subject_statement` (cardinality rule; options 1+3 unified); the trial/epoch
  (option 2) is **deferred**. Still open: the parameter **value representation** (one
  uniform `{variable, value}` resolved by the registry vs a nested typed block per
  parameter), and the per-entity resolution (**D11**). The column-role rule is the
  classifier backbone. `ontology_table_row.m` stays flagged (knowingly-wrong) until it
  is rewritten to this shape. (A.9, C.2)
- **D11 — Which entity a column describes (subject-of-column / multi-entity rows).
  OPEN — split out of D10.** The column-role rule (D10) says *what* a column is; D11
  asks *whose* it is. The migrator cannot blindly anchor every column on the row's
  `SubjectLocalIdentifier`, because in the JH corpus the measured entity is routinely
  **not the animal**: the bacterial-patch tables (13k+ rows) measure a *bacterial
  patch* (its own `subject`), the plate-prep tables measure a *plate/session*, and
  two tables are pure **relations** (a worm *encountered* a patch; a subject *is on* a
  plate) carrying no measurements at all. A single flat row can therefore mint
  observations about several distinct entities plus edges between them. Open
  questions: **(i)** how is per-column subject resolved — a per-table discovery map
  (like the +migrators_i seeding), a heuristic on column-name prefixes
  (`BacterialPatch*` → the patch entity), or an explicit author-supplied binding?
  **(ii)** when the row has no natural single subject (encounter/link tables), we mint
  the `directed_relation`(s) directly with **no trial anchor** — the trial/epoch is
  deferred (D10) — so confirm bare relations are sufficient for the link tables.
  **(iii)** how do reference columns (D10 role 3) get paired with the entity they point
  at so the `directed_relation` is well-formed? With D10 decided (parameters, trial
  deferred), (ii) resolves to bare relations for now; **(i)** and **(iii)** remain and
  couple to D2 (instrument-as-subject). *Status:* OPEN — (i)/(iii). (A.9, A.10, C.2)

---

## Part F — Implementation & phasing (after approval)

1. **Schema (DID-schema).** Write `V_eta_SPEC.md` + `V_eta_notes.md`; build
   `schemas/V_eta/` as a copy of V_zeta with the Part-A transform applied
   (subject → bare identity; add `subject_relation`/`directed_`/`undirected_`;
   restore `subject_statement`; re-root + rename `subject_observation`/
   `_manipulation`; **rebuild the leaf tier per §A.9** — rename the shape leaves
   to one-word data-type names (drop the `scalar_` prefix), collapse the
   `scalar_`/`dataseries_`/`timeseries_`/`imageseries_` split into one class per
   type, fold `categorical_observation`→`term_observation`, and retire the
   `injection`/`bath`/`pharmacological`/`biological_transfer`/`generic_manipulation`
   families into data-type-named manipulations + composites; assertion genus +
   leaves; `storage_mode` + `data_body`/`sampled_body`/`opaque_body`, retiring the
   superseded body classes; drop `target_structure`). **Build the binding registry
   (D9):** a `value_set` class, a binding-registry meta-file (`variable` /
   `method`+`variable` → `value_set` / leaf), the `binding` block formalized in the
   meta-schema, and the enumerated kind-variable set. Add `tests/test_veta.py`
   (meta-validation, index/disk agreement, superclass +
   `must_refer_to_document_class` resolution, spine composition, **plus binding
   integrity: every `binding` names a real `value_set`, every `value_set` root
   resolves**). Seed `schemas/V_eta/conversions/from_did_v1/` (`_index.md`,
   `_universal_renames.md` = V_zeta's with the stamp value changed, per-class
   docs mirroring Part D).
2. **DID-matlab.** Add `+did2/+convert/+migrators_j/` (one `.m` per source class
   in Part D + `Contents.m`); wire the `V_eta` branch in `v1_to_v2.m`. Transform-
   level tests `tests/+did2/+unittest/testMigratorsJ.m` (no schema needed,
   `Validate=false`). **Add the ontology-aware binding validator (D9)** — resolve a
   term `value` against its bound `value_set` at validation time (a cached/queryable
   NCBITaxon/OBI/CL/CHEBI/UBERON/RO hierarchy); wire it into
   `did2.schema.cache.validateDocument` so `Validate=true` enforces the vocabulary.
3. **NDI-matlab.** Extend `ndi.migrate.internal` with the part-subject
   find-or-create/dedup service (C.1) and the assertion/observation +
   attributed/located routing tables (C.2/C.1); add the `assembleDeferred` cases.
4. **Corpora acceptance (discovery mode).** Point `runCorpusDiscovery` at
   `TargetVersion='V_eta'` for JH → Dab → B → PRED → Soph → 20211116; read the
   routing + quarantine + orphan reports, curate the per-term tables, iterate to
   zero orphans and an empty (or explained) quarantine. **The corpora are the
   spec** — the dispatch tables in Part C/D are seeds, finalized here.

**Non-goals for this plan / first pass.** The `dataSeriesType` registry;
live-correction/supersession of shared `reference` value documents (immutable
references need none); populating the individuated referent (`instrument_id` /
`element_id`); and any relation surface with no `did_v1` source (forward-looking
`member_of`/`placement`/`derivation` authoring). *(The binding-registry meta-file
and `value_set` class are now **in scope** for Phase 1 — see D9.)*

---

*V_eta migration plan · implements Brainstorm J · proposal for issue #69 ·
provisional until approved. The subject-model change (bare-identity subjects +
relations-as-documents + Path S) has been accepted by the team per Brainstorm J.
Decisions D1–D9 are resolved (D3/D6 gate final term lists on the discovery
reports); the migration mechanics and cardinality are what remain for the team to
sign off before Phase 1 begins.*
