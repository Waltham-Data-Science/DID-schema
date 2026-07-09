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
  rates under one clock (multi-rate under one epoch). Pending confirmation — see
  the D1 discussion.

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

- **D1 — Timing model (two axes).** **(A) shape:** always compress (`point` /
  `{t0, dt, n}` grid / `offsets[]`), never a literal N-array when regular —
  *agreed*. **(B) location:** anchor in the shared `time_reference`; compressed
  **cadence beside the value** (statement inline / body when body-backed), *not*
  welded into `time_reference`. *Leaning* per the D1 discussion (single-document
  length-consistency; cadence-free anchor is shareable across rates). Confirm (B).
  (A.8)
- **D2 — Individuated referent: `element_id`, part-subject, or an `instrument`?**
  Anatomical/biological parts → part-`subject` (Path S). For the *device that did
  the measuring*, three options: keep `element_id → element` (the NDI acquisition
  handle; simplest, migration-ready); promote the existing draft **`instrument`**
  class + an `instrument_id` edge on `subject_interaction` (OBI-style device role);
  or model the device as a `subject` + a "measured_with" relation (pure J). No
  `did_v1` corpus needs an explicit instrument, so *provisional:* keep `element_id`
  for pass 1 and treat `instrument` promotion as a parallel design thread. (A.10)
- **D3 — Path S scope for the first pass. Resolved:** *measure before we build.*
  Discovery mode counts attributed anatomical loci per corpus first; default
  **located-by-default** (emit a `term_observation` value, mint no subject), and
  build the full find-or-create/dedup service only if the volume warrants it. (C.1)
- **D4 — `treatment_transfer` donor. Resolved:** a provenance `directed_relation`
  (recipient material `derived_from`/`sample_of` donor); the transfer act is a
  term-valued manipulation. No `donor_id`-on-manipulation, no `biological_transfer`
  class. (C.3)
- **D5 — Element/probe location terms. Resolved:** → `term_observation`
  (`probe_location`/`ontology_image`/`ontology_label`): element = subject,
  spatial/labeling relation = `variable`, term = `value`. (D.2)
- **D6 — Relation vocabulary — measure before building (same reports as D3).**
  The migration only *mints* relations for `part_of` (Path S) and one provenance
  term (`sample_of`/`derived_from`, from `treatment_transfer`); `member_of` has no
  `did_v1` source (empty `subject_group`), and J's remaining terms
  (`contained_in`, `aliquot_of`, `passage_of`, `paired_with`, `same_as`) have no
  migration source at all. So the **corpus-exercised set is expected to be ~2
  terms**, confirmed by the same discovery reports as D3. Open sub-choice: declare
  J's full designed 9-term set now (closed, cheap, forward-looking authoring uses
  `member_of` etc.) vs. declare only the measured subset. *Leaning:* declare the
  full J set (RO-backed), wire migrator + tests only for the measured subset.
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
- **D8 — Payload-free manipulations. Resolved:** `term_manipulation` (imposed
  value = the act's ontology term). **No escape hatch** — strict J resolves every
  act to a data type; an un-typed numeric is flagged/quarantined in discovery
  mode, never dumped into a generic bin. `generic_manipulation` and
  `generic_scalar_observation` do not exist in V_eta. (A.9)

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
   superseded body classes; drop `target_structure`). Add `tests/test_veta.py` (meta-validation, index/disk
   agreement, superclass + `must_refer_to_document_class` resolution, spine
   composition). Seed `schemas/V_eta/conversions/from_did_v1/` (`_index.md`,
   `_universal_renames.md` = V_zeta's with the stamp value changed, per-class
   docs mirroring Part D).
2. **DID-matlab.** Add `+did2/+convert/+migrators_j/` (one `.m` per source class
   in Part D + `Contents.m`); wire the `V_eta` branch in `v1_to_v2.m`. Transform-
   level tests `tests/+did2/+unittest/testMigratorsJ.m` (no schema needed,
   `Validate=false`).
3. **NDI-matlab.** Extend `ndi.migrate.internal` with the part-subject
   find-or-create/dedup service (C.1) and the assertion/observation +
   attributed/located routing tables (C.2/C.1); add the `assembleDeferred` cases.
4. **Corpora acceptance (discovery mode).** Point `runCorpusDiscovery` at
   `TargetVersion='V_eta'` for JH → Dab → B → PRED → Soph → 20211116; read the
   routing + quarantine + orphan reports, curate the per-term tables, iterate to
   zero orphans and an empty (or explained) quarantine. **The corpora are the
   spec** — the dispatch tables in Part C/D are seeds, finalized here.

**Non-goals for this plan / first pass.** The binding-registry meta-file and
`value_set` class; the `dataSeriesType` registry; live-correction/supersession
of shared `reference` value documents (immutable references need none); populating
`element_id`; and any relation surface with no `did_v1` source (forward-looking
`member_of`/`placement`/`derivation` authoring).

---

*V_eta migration plan · implements Brainstorm J · proposal for issue #69 ·
provisional until approved. The subject-model change (bare-identity subjects +
relations-as-documents + Path S) has been accepted by the team per Brainstorm J;
the migration mechanics, cardinality, and Decisions D1–D7 above are what this
document asks the team to approve before code is written.*
