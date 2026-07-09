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
├── time_reference        (abstract)   utc / epoch / event / session frames  [from V_zeta]
├── subject                            bare identity — a name, nothing more   ◄ CHANGED
├── subject_relation      (abstract)   a claim relating two subjects          ◄ NEW branch
│   ├── directed_relation              ordered child → parent (containment, provenance)
│   └── undirected_relation            unordered { a, b } (association)
└── subject_statement     (abstract)   carries variable + value (+ optional time)  ◄ RESTORED
    ├── subject_assertion (abstract)   a timeless fact — no act, no series     ◄ RE-ROOTED + genus
    │   ├── term_assertion · date_assertion
    │   └── numeric_assertion (abstract genus) → scalar_mass_assertion, …      ◄ NEW leaves
    └── subject_interaction (abstract) tightens time to required; ADDS method  ◄ RE-ROOTED
        ├── subject_observation  (abstract)   value read off the subject       ◄ RENAMED
        │     scalar_<dim>_observation · categorical/term_observation · dataseries…
        └── subject_manipulation (abstract)   value imposed on the subject     ◄ RENAMED
              injection · bath · <dim>_manipulation · biological_transfer · generic_manipulation
```

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
  `numeric_assertion` (abstract) → dimensioned `scalar_mass_assertion`, … using
  the **scalar subset** of the shape library (no series, no body).
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
- **Timing is the one place J and I genuinely differ.** J §7 writes the per-
  sample timeline as an explicit **`sample_time`** list parallel to `value`;
  V_zeta *retired* `sample_time` in favour of a **shaped `time_reference`**
  (`sampling: point | grid | enumerated`), which is O(1) for regular grids and
  makes same-sample search hold by construction. This is a real fork, not a
  detail — see **Decision D1**. The plan's provisional default is to **keep
  V_zeta's shaped `time_reference`** (strictly better for regular grids; J's
  `sample_time` prose predates that refinement and I read J as agnostic on the
  encoding, not committed to N-length arrays), and to treat `sampled_body`'s
  internal `sample_time` axis as the body-local timeline. Flagged for the team.

### A.9 What carries over from V_zeta verbatim (design-neutral for J)

The shape library (`scalar_<dim>` value mixins, `generic_scalar`, `score`,
`date`), the `time_reference` frames, the `injection`/`bath`/`biological_transfer`/
`generic_manipulation` typed manipulation families, `categorical_observation` /
`term_observation`, and **all non-subject infrastructure** — `base`, session/
dataset, `element`/`epoch*`, `daqsystem`/`daqreader*`, `stimulus_*`, the tuning/
response calculators, `openminds*`, `ontology_*`, `zarr`/`image*`, `probe_*`.
The five V_zeta deprecations stay deprecated. The relational event classes
V_zeta introduced (`group_assignment`, `placement`, `derivation`) are **re-cast
as `subject_relation` documents** in V_eta (they were already "relations as
events"); they have no `did_v1` source, so this is a forward-looking rename, not
a migration.

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
- **Timed measurement** → `subject_observation` as before (body weight →
  `scalar_mass_observation`, etc.).

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
- **`treatment_transfer` donor.** V_zeta keeps `donor_id` as a dependency on
  `biological_transfer`. In J the transferred material's provenance is naturally
  a `derived_from`/`sample_of` `directed_relation` (recipient material ← donor).
  **Decision D4:** keep the manipulation-with-`donor_id` shape, *or* additionally
  emit a provenance relation, *or* both. Provisional default: keep the
  `biological_transfer` + `donor_id` edge (least invasive; the relation can be
  derived later) and flag for review.
- **Attributed anatomical parts** (C.1) — the one place relations are minted at
  volume.

### C.4 `data_body` consolidation + `storage_mode` stamping

- **`image_stack`** (V_zeta's most elaborate fold, `1 → 6`: imageseries handle +
  element + `element_epoch` + `daqreader_image_epochdata_ingested` + `daqreader`
  + anchor) re-targets in V_eta to: a **`subject_observation`** imageseries
  handle + an **`element`** + a **`sampled_body`** (or `opaque_body` for an
  un-decodable stack) holding the frames, carrying `storage_mode: body`. Net
  fold likely `1 → 4/5` (the `element_epoch` + ingested-frames pair collapses
  into one `sampled_body`). This is the main `did_v1` class exercising the new
  storage model.
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
| `treatment` | `injection` / `bath` / `<dim>_manipulation` / `generic_manipulation` (all `subject_manipulation`) **+ time anchor**, **+ part-`subject` + `part_of`** when the focal site is attributed, **or** a `term_observation` location value when merely located | dispatch table carries over; **`target_structure` → Path S mint-or-locate (C.1)** instead of a spine field; direction class is `subject_manipulation` | 1→2…4 |
| `ontology_table_row` | per column: `subject_assertion` leaf (timeless) **or** `subject_observation` leaf (timed) + shared anchor; anatomy column → Path S (C.1) | **timeless columns now → `subject_assertion` (C.2)**, DOB → `date_assertion`; shape-typed value leaves carry over | 1→N(+1) |
| `subject_group` | bare `subject` (v3.0.0) | **`is_group`/`is_biological` removed (A.2)**; no membership edges | 1→1 |
| `treatment_drug` | `injection` (`kind: drug`) + anchor; anatomy → C.1 | mixture/CSV parse carries over; `subject_manipulation`; locus → Path S | 1→2…3 |
| `virus_injection` | `injection` (`kind: virus`) + anchor; anatomy → C.1 | as above | 1→2…3 |
| `treatment_transfer` | `biological_transfer` (`donor_id`) + anchor; **± provenance `directed_relation` (D4)** | donor may also become a relation | 1→2…3 |

### D.2 Semi-mechanical (composite-collapse; element/probe-scoped — subject redesign does **not** touch them)

`probe_location`, `ontology_image`, `ontology_label` — the `ontology_name`+`name`
(or 3-field) collapse into one `ontology_term` carries over from V_zeta
unchanged. These describe elements/probes, not subject loci, so Path S does not
apply. **Open nuance (D5):** in J "any level is a subject," so a probe's location
term *could* be re-read as a `term_observation`; the plan keeps them as-is for
V_eta (infrastructure, out of scope for the subject-model migration).

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

- **D1 — Timing model.** Keep V_zeta's shaped `time_reference`
  (`point/grid/enumerated`), or adopt J's explicit parallel `sample_time` list?
  *Provisional:* keep shaped `time_reference` (O(1) regular grids; same-sample
  search holds), use `sampled_body.sample_time` for body-local timelines. (A.8)
- **D2 — `element_id` vs part-subjects.** Confirm the split: anatomical/biological
  parts → part-`subject` (Path S); NDI elements backing acquired data → keep the
  optional `element_id` handle + a `sampled_body`. (A.9)
- **D3 — Path S scope for the first pass.** After discovery reports quantify how
  many `did_v1` rows carry an attributed anatomical locus: full mint-and-dedup
  service, or a narrower "located-by-default, mint only on an allowlist"? (C.1)
- **D4 — `treatment_transfer` donor.** `biological_transfer` + `donor_id` edge
  only, a provenance `directed_relation` only, or both? (C.3)
- **D5 — Element/probe location terms.** Leave `probe_location`/`ontology_image`/
  `ontology_label` as composite terms, or re-read as `term_observation`s under
  J's "any level is a subject"? *Provisional:* leave as-is. (D.2)
- **D6 — Relation vocabulary starting set.** Confirm the enumerated `relation`
  terms per grouping (containment / provenance / association) and their RO
  backing (J §10-Q3).
- **D7 — Closure index is tooling, not schema.** J's "everything under X"
  closure index is a materialized view over `directed_relation` documents. The
  current abstract query model (`did_query_model.md`) has **no cross-document
  join beyond `depends_on` and no closure** — so the closure index is a
  consumer-side index (NDI framework), declared but not schema-enforced, and the
  fallback is a bounded reverse-`depends_on` walk. Confirm this stays out of the
  schema layer.

---

## Part F — Implementation & phasing (after approval)

1. **Schema (DID-schema).** Write `V_eta_SPEC.md` + `V_eta_notes.md`; build
   `schemas/V_eta/` as a copy of V_zeta with the Part-A transform applied
   (subject → bare identity; add `subject_relation`/`directed_`/`undirected_`;
   restore `subject_statement`; re-root + rename `subject_observation`/
   `_manipulation`; assertion genus + leaves; `storage_mode` + `data_body`/
   `sampled_body`/`opaque_body`, retiring the superseded body classes; drop
   `target_structure`). Add `tests/test_veta.py` (meta-validation, index/disk
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
