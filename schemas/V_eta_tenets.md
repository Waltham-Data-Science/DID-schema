# V_eta — Brainstorm J tenets (north star)

*The durable statement of WHY V_eta is shaped the way it is. Read this before adding a
class, folding a source, or arguing a disposition. The class-by-class SPEC is
`V_eta_SPEC.md`; the migration mechanics are `V_eta_migration_plan.md`; this file is the
principles those rest on. When a design question arises, answer it from these tenets —
do not re-derive from the class list.*

## Thesis (issue #69)

> **"The subject model, and one class family for everything about a subject."**

Brainstorm J is a **subject-centric, statement-based reduction** of the did_v1 document
zoo. did_v1 put meaning in ~100+ bespoke class names; J moves the meaning **out of the
class name and into the graph + the ontology**, and re-expresses everything as a small
orthogonal spine:

> **thin subjects  ×  one statement family  ×  data-type composites  ×  typed relations**,
> with vocabularies enforced by ontology bindings.

It develops from Brainstorm H, and keeps Brainstorm I's load-bearing idea — *identity is
off the class; the data-type/shape is the leaf and the property rides on `variable`* —
then rebuilds the subject side around it.

---

## The tenets

### T1 — The subject is a bare identity; there is no privileged level.
A `subject` is an id + optional `local_identifier` + `description`, and **no
`depends_on`**. Organism, slice, neuron, brain region, group, or recording device — all
are subjects, with **no kind-subclasses**. Every other property is *derived from the
graph*: group-ness from incoming `member_of` edges; kind from a `term_assertion`;
"biological" from whether that kind term sits under an organism branch. (SPEC §1)

### T2 — Everything you can say about a subject is one `subject_statement` family.
A statement binds a **`variable`** (what — an ontology term) to a **`value`**, about a
subject, optionally at a **time**. Identity rides on `variable`, not the class, so one
query spans all statements. The family branches by *epistemic direction*:
`subject_assertion` (timeless fact), `subject_observation` (measured from),
`subject_manipulation` (done to), `subject_calculation` (derived/computed about). An
assertion has no act/series; an interaction (observation/manipulation/calculation) adds
`method` (the verb), its per-reading positions as `keys` (the `sample_time` block retired
under the signed data_body model, 2026-08-14; built #73 item 21), an optional
`instrument_id`, and
requires a `time_reference`. (SPEC §3–§5)

**Observation vs calculation is decided by provenance, not by whether software ran**
(#73, 2026-09-23). A statement whose inputs are **other statements in the dataset** is a
`subject_calculation` and records them in `derived_from_#`; a statement produced from data
held **outside** the dataset (an instrument, raw reads that are not stored) is a
`subject_observation` and has no `derived_from`. Almost every measurement is processed by
some pipeline, so "computed by software" cannot be the test; whether the inputs are in the
dataset can be read off the document. Consequences: there is no "computed observation";
`derived_from_#` is declared on `subject_calculation` only; a lossless re-assembly of stored
statements (`oneepoch`'s concatenation) is a calculation too.

### T3 — A leaf class = a direction × a data type. This is the move that collapses the zoo.
Instead of hundreds of classes, **factor**: data-type composites (`mass`, `dose`,
`term`, `timed_sequence`, …) × directions = one-word leaves (`mass_observation`,
`dose_manipulation`, `term_assertion`, `timed_sequence_manipulation`,
`orientation_direction_tuning_calculation`). A new measurement is a new composite or a
new `variable`; it is **not** a new hand-written class. (SPEC §6)

**A leaf is made when it is needed, not in advance** (team, 2026-09-25, #73 item 50).
Every data_type stays whether or not it has a leaf (a standalone data-type document is
valid content, T6). An `_observation`, `_manipulation`, `_assertion` or `_calculation`
leaf exists only once something needs it — a migrator or second pass writes it, or a
decision names it as a target — and is then made by combining that direction with the
data_type. No leaf is generated for every direction "just in case": a leaf nothing
writes reads as a supported case nobody has checked.

**Undimensioned values ride a bare self-describing body (no generic numeric data_type).**
`direction × data_type` is the norm — the data_type carries the meaning (`voltage`, `intensity`,
`tuning_curve`). But when a value is **raw numeric with no dimensioned meaning** (an
unknown-modality recording), do **not** invent a generic `array` /
`numeric` data_type — that would only duplicate `sampled_body` (T6, which is already
"self-describing: axis + typed datum"). Instead the value **is** a bare self-describing
`sampled_body`: its `keys` live on the body, its `datum_type` on the statement (#73), and
the `variable` carries the label.
The dimensioned data_types just *add* units on top. So: type it when you can (a modality → a
composite); otherwise the self-describing body is the value. *(This is why `array` was killed
and `ngrid` phases into `sampled_body`.)*

### T4 — Relationships are first-class documents; the graph carries structure.
`subject_relation` → `directed_relation` (ordered child→parent: `part_of`, `member_of`,
`derived_from`, …) + `undirected_relation` (`paired_with`, `same_as`). Relations are
**binary** — a many-way group is a reified subject + `member_of` edges, never a list.
Endpoints are typed `depends_on`, so referential integrity and reverse lookup are
automatic. Containment and provenance live on this ancestry spine. (SPEC §2)

### T5 — Path S: a structure earns subjecthood only when it is a thing-in-itself.
A structure a value is **attributed to** becomes its own subject + `part_of` (the
interaction's subject is the part); a structure merely **located** stays a
`term_observation` value (a spatial-relation `variable` + an atlas term). A brain region
is normally an *address* (a value), not a subject. (SPEC §4)

### T6 — Storage is orthogonal to meaning; there are exactly two data bodies.
`storage_mode ∈ {inline, reference, body}`. `data_body` has **exactly two** members:
`sampled_body` (raw bytes whose layout V_eta declares — `byte_order`, `datum_order`,
`chunk`, `fill_value` — with `datum_type` on the statement; `summary` dropped, #68;
partial-read, value-searchable) and `opaque_body` (bytes laid out by their own `format`:
TIFF, OME-Zarr, an archive). The two split by **who lays out the bytes**, not by whether
there is an array: both may carry `keys` (required on a sampled body; on an opaque body
they describe the array as its format presents it) and `conditions` (lightsheet
walkthrough L1/L3, 2026-09-25). Every carrier — timeseries,
dataseries, zarr, image, generic_file — phases into those; **encoding/format is a field,
not a class**. Timing splits: the anchor lives in `time_reference`, the per-sample
cadence rides beside the value. (SPEC §8)

**Keys vs. conditions.** A **key** is a dimension of the *stored* array — exactly those,
in order, a length-1 dimension included, and never a key for a dimension the array does not
have. A **condition** is a one-value fact true of every value that is *not* a stored
dimension (an electrode offset; a reduced pyramid level's `summary statistic: maximum`). A
condition true of every body sits on the statement; one true of only one body sits on that
body. A variable appears at most once across a statement's keys and conditions and any one
of its bodies'. Bodies point at their owner (`owner_id`) and the owner does not list them —
adding a body never rewrites the statement — so that rule is checked in batch.

**Primary vs. derived (the cache rule; cross-ref T10/T12).** When representation *B* is
**losslessly derivable** from representation *A*, store *A* once at the **finest grain** and
treat *B* as a **rebuildable cache**, never as a second source of truth. A materialized cache
is still one of the two bodies (usually `sampled_body`), but it is marked `derived_from` its
source subjects (T10) and carries no authority — deleting it loses nothing, because it
regenerates from *A*. Store the source, project the view. *Example:* per-neuron spike trains
are the source of truth; an ensemble's combined (time, neuron) marked-point-process is a
derived cache for fast population reads, not primary data (see `V_eta_ensemble_plan.md`).
This is the storage-side face of T12 parsimony: never store the same information twice, but
a *marked, disposable* cache is a permitted performance exception, not a duplicate source.

**The cache marker (required).** `derived_from` alone is overloaded — T10 uses it for
*authoritative* analysis outputs (a calculation result IS the science), while a cache is
*disposable*. A consumer must be able to tell them apart, so a materialized cache carries an
explicit **`redundant: true`** marker (distinct from a plain `derived_from` provenance edge).
`redundant` ⇒ adds no information, regenerable exactly, no authority, safe to drop and
rebuild; absent ⇒ the `derived_from` product is authoritative (a T10 calculation). Never infer
cache-ness from `derived_from` presence. *(Named `is_cache` until 2026-09-24: "cache" reads as
transient and possibly stale, and collides with NDI's in-memory `ndi.cache`; `redundant` names
test 1 below directly, and T13 drops the `is_` prefix. Declared ONLY on `data_body` and
`subject_calculation` — the only places a cache can exist: an observation's source is outside
the dataset, and assertions, manipulations and standalone content are not derived. Most
calculations are NOT redundant — a clustering or a fit depends on method, version and
randomness. Nothing may cite a redundant document as a provenance input.)*

**The cache-warrant test (parallel to T12's data_type-warrant).** Materializing a cache is the
*exception*; before minting one, all of the following must hold — else store only the source
and project on read:
  1. *Losslessly derivable* — the cache adds **no information** the source lacks (else it's a
     source, not a cache).
  2. *A real access need* — a concrete query/read pattern is materially cheaper against the
     cache than against the source at the expected scale (e.g. windowed population reads).
  3. *Marked & regenerable* — it carries `redundant` + `derived_from`, and a deterministic
     rebuild from the source exists.
  4. *Recorded reason* — the warranting access need is written next to it (as T12 requires for
     a new data_type). No silent caches.

**A standalone data-type document is CONTENT, NOT A CLAIM** (team, 2026-09-24). `storage_mode:
reference` means "my value lives in another document", so every `data_type` composite is
concrete: a shared command waveform, a stimulus, an image or a gene list is written once as a
standalone document, and each statement that uses it points at it by its `value_id` edge. The
standalone document says nothing about anything until a statement references it; the statement
carries the subject and the stance.

**One body per ARRAY; a file series where only the bytes split** (team, 2026-09-24). A new
`data_body` document where the array changes (each zoom level of a pyramid); a file-series
member where one array's bytes are cut into chunks (the tiles of one level). Every body's
`body_data` is a DID file series, so an unchunked body is simply member `body_data_0`. A file
held outside the database is a member recorded by location and not ingested.

### T7 — Roles are edges, not subclasses.
The measuring/manipulating device is a subject (kind asserted), linked by a typed
`instrument_id`. `subject_id` = patient, `instrument_id` = agent, `method` = verb. No
organism/cell/instrument/medium subclasses. (SPEC §8, D2)

**Worked example (instrument vs. subject).** Extracellular voltage recorded from a brain
slice with an electrode: the *slice* is the `subject` of the `voltage_observation` (the
**patient** — its voltage is what's measured); the *electrode* is a subject too (T1), but
here it plays the **instrument role**, referenced by `instrument_id` — it is *not* the
subject of the recording.

**The trap (do not fall in):** a device is its own subject, but it is **never the observed
subject of the value it helps measure**. Ask two questions: "Whose value is this?" → the
patient (`subject_id`); "What tool produced it?" → the instrument edge (`instrument_id`).
The same electrode is the *patient* only when the statement is *about the electrode itself*
(e.g., its measured impedance is a `voltage`/`resistance` observation whose `subject_id` is
the electrode). This is the difference between *observing with* a device and *observing* the
device.

### T8 — Controlled vocabularies are hard-validated, not advisory.
A `value_set` declares an admissible set (ontology root + descendants, or an enum); a
binding registry maps `variable` (and `method`+`variable`) → a value_set or a leaf; an
ontology-aware validator resolves term values against NCBITaxon/OBI/CL/CHEBI/UBERON/RO.
`must_refer` is **existence-only** (referential, not type-checked): the graph is loosely
typed and the *ontology* carries the semantics. (SPEC §7, D9)

### T9 — Datasets and provenance are first-class, FAIR entities.
`dataset`, `person`, `organization`, `funding`, `publication`, `web_resource`, `session`,
`subject` carry a `global_identifier`, with full openMINDS field parity and a
machine-readable crosswalk. Aggregation/authorship/funding are `directed_relation`s.

### T10 — The calculator motif: analysis outputs are calculations, migrated id-preserving.
(Lepsky et al.) A calculator produces **one** output document type — a
`subject_calculation` leaf (direction × a result composite). Migration is **1→1 with
`base.id` and `depends_on` preserved**, never a dissolution: dissolving a calc changes
its id and dangles every downstream consumer (the 11,448-orphan lesson). Because
`must_refer` is existence-only, id-preservation keeps the provenance graph intact.

### T11 — Naming grammar: one shape, one canonical name; nothing else in the name.
- **Leaf** = `<data_type>_<direction>` (snake_case; direction ∈
  `observation`/`manipulation`/`assertion`/`calculation`). **Composite** = the bare
  `<data_type>`. **time_reference** = `absolute_time_reference` / `relative_time_reference`
  (the `<origin>_<mode>_reference` family collapsed to these two, #65; the leaves say
  "time", #73).
- The name encodes **only the data type and the stance**. It must **never** encode:
  cardinality (`scalar_`, `_series`), storage/format (`_data`, `_file`, `_zarr`), a
  device/method subtype (`_ndr`, `_mfdaq`, `_image`), or an instrument. Those are a
  `value` length, a `storage_mode`, a field, a `method`, or an edge — never a class name.
- **One canonical spelling per concept.** Every `{node, name}` value is the single `term`
  type (+ a binding), never a bespoke class per vocabulary entry (no `species`,
  `categorical_observation`, …). One direction-suffix set, used consistently.
- A name that reads like a sentence fragment about *how it was made or stored* is a smell:
  the how is `method`/`app`/`storage_mode`, the where is an edge.

### T12 — When a new `data_type` is warranted (the parsimony test).
A new composite is the **last resort**, warranted only when the value has a **new
measurement structure or a new quantity dimension** that no existing composite can carry.
Before minting one, exhaust the cheaper axes — a new composite is wrong if the difference
is any of:
1. **Same shape, different meaning** → keep the composite, change the **`variable`**
   (and/or `method`). *(species vs strain are both `term_assertion`; two different
   scores are both `score_observation` with different `variable`.)*
2. **A controlled term** → `term_*` + a **binding** to a value_set. Never a class per
   vocabulary entry. **A term is anything with a namespace and an id** (`CL:0000617`,
   `ENSEMBL:ENSMODG00000020019`); when none exists, mint one. **A value meaningful only
   LOCALLY is a `label`** — a term without a node (`label.value = {name}`): a source
   cell identifier, a cluster number, a run's condition name (team, 2026-09-24). The
   test: shared or compared across datasets → a term; confined to one source or run →
   a label. So a cluster can never pass as a cell type: one is a label, the other a term.
3. **Same quantity, different cardinality / storage / format** → same composite; use a
   length-N `value` + `storage_mode`. *(a temperature series is `temperature`.)*
4. **A role or relationship** → a typed **edge** (`directed_relation`, `*_id`), not a
   data_type. *(donor, target region, parent group.)*

Mint a composite **only when 1–4 all fail** — i.e. a genuinely new **dimensioned
quantity** (its own unit: `mass`, `charge`, `pressure`) or a genuinely new **structured
object** (several co-varying fields that form one unit: a tuning curve, a grating spec).
When several near-identical structures differ only by an independent variable or a fit
form, **prefer one parameterized composite** (a single `tuning_curve` whose independent
variable is a field/`variable`) over a family of look-alike composites — **unless** a
downstream contract requires the split (e.g. T10's "one calculator → one document type").
If you split for such a contract, **record the reason** next to the classes; an
unexplained look-alike family is a T12 violation to revisit.

### T13 — Name at the concept's altitude: snake_case, wrapper-free, honestly stanced.
T11 fixes the *grammar* of a name (which slots, what must not appear); T13 governs the
*words and case* you actually choose — for both **class/`data_type` names and field
names**. A good name lets a reader predict its content and scope **without a qualifier or
a footnote**.

- **Case.** Every name we author — classes, `data_type`s, fields — is **`snake_case`**,
  lowercase. The *only* verbatim-cased strings are **external identifiers carried as
  values**: ontology CURIEs (`obi:0000750`), openMINDS term-set names. PascalCase/camelCase
  in a document block is a migration smell (snake-case it) unless it is such an external id.
- **Booleans name the property, with no `is_`/`has_` prefix** (team, 2026-09-24). A
  boolean field is named for the property it asserts: `approximate`, `regular`,
  `complete`, `cyclic`, `blank`, `mock`, `modulated_response`, `redundant` — never
  `is_approximate`, `is_blank`. The type already says it is a yes/no; the prefix adds
  nothing a reader needs. This was already the practice in every field V_eta designed
  (the value cell's `approximate`, 54 uses; axes' `regular`, 4) and the `is_` names were
  did_v1 carry-overs. **The one exemption is a did_v1 SOURCE TOMBSTONE**, which must keep
  the v1 writer's spelling verbatim so a passthrough still validates (`israster`,
  `is_unsupervised`, `has_score`, `has_planar_contour`, `isspike`, `do_filter` stay as
  v1 wrote them). `time_reference.is_approximate` is not renamed because the signed time
  model already deletes it (`V_eta_time_reference_model_plan.md`, "both go").
- **Right altitude — the `visual_grating` rule.** Pitch the name at the level a domain
  expert names the thing. Two failure modes, both detectable by their tell:
  - **Too generic → needs a rescue qualifier.** If a base name only becomes usable with a
    bolted-on `_<type>` (`stimulus_parameters_grating`, `stimulus_parameters_bar`), the
    base was under-specified. Name the concept directly: **`visual_grating`**, not
    `stimulus_parameters_visual_grating`. A `_<qualifier>` added to make a vague base
    specific is the signal you named the *container*, not the *content*.
  - **Too specific → near-duplicate fragmentation.** If you would mint a separate class per
    minor variant, lift to the shared concept and push the variant onto a `variable`/field
    (T12). "As simple as possible, but no simpler": the shortest name that stays
    unambiguous and does not over-claim scope.
- **Name the content, not the container.** Drop altitude-noise wrapper words —
  `parameters`, `data`, `info`, `struct`, `table`, `record`, `metadata`, `object`,
  `properties`. They describe the box, not what is in it (`stimulus_parameter_table`,
  `stimulus_response_scalar_parameters` are v1 smells). A field holds a **role** — name the
  role: v1's generic `parameters` split into **`conditions`** (one-value facts true of
  every value — the experimental conditions, on a statement or on one body, T6) and
  **`method_parameters`** (the algorithm config on an interaction);
  a per-stimulus mean is `response_mean`, not `value`.
- **Abbreviate only when the short form is the *more* recognizable one.** `id`, `url`,
  `daq` earn it — the expansion is rarely spoken and the short form is unambiguous. `app`
  does not: prefer the clear full word (`software`). Expand whenever the full word removes
  ambiguity — and note that a longer word is not automatically clearer: `application` is
  *worse* than both, because in a neuroscience corpus it collides with "applying" a
  stimulus or drug. Pick the term that is shortest **among those that are unambiguous**.
- **The stance word must be TRUE, not convenient.** The direction suffix —
  `_observation` (measured *from*), `_manipulation` (done *to*), `_assertion` (declared),
  `_calculation` (computed) — carries meaning, so a wrong one lies. Choose the suffix that
  matches the actual epistemic act; likewise a field's noun must match its semantics.

**Litmus:** could a reader who does not know this project's history *predict what the doc
holds and guess it's not something adjacent*, from the name alone? If they'd need to open
it, or if the name only works once you append a qualifier, re-pitch it.

- **No untyped `{name, value}` bags inside a composite.** A composite's fields must be
  **typed and named for their content**. A generic `{name, value}` (or `{name, value, units}`)
  array names nothing, is not queryable, and is the *field-level* form of the container-word
  smell this tenet forbids at the class level. A per-stimulus mean is `response_mean`, not a
  `{name:"mean", value:…}` entry; fit coefficients are a named `coefficients` block, not a
  `parameters` bag. When a set of things varies, distinguish by a controlled **term + a typed
  slot** (T8/T12), never by an unordered kv-bag. *(This killed the `derived_summary` bag and
  the `model_fit.parameters`-as-bag draft.)*
- **Infra reach.** The grammar (T11 + T13) applies to **⑦ acquisition/infra plumbing too**
  (`daqreader`, `syncgraph`, ingested caches) — infra is **not exempt** from "name the content,
  no container/format/cardinality/subtype words." The *only* concession: when an infra class
  name mirrors an external writer's string (NDI), the rename is a **cross-repo lockstep** change
  batched with the owning repo — same bar, coordinated landing (this is R5). Mirroring an
  implementation is not a license to keep a smelly name.

### T14 — Structure is declared, not conventional.
A convention that lives in prose, in examples, or in code literals is not a convention —
it is drift waiting to happen. **Anything a consumer must know in order to read a value is
declared in the schema.** This is T8's *"hard-validated, not advisory"* applied one level
down: T8 governs the vocabulary a value may take, T14 governs the value's own shape.

- **One payload slot.** Every `data_type` composite exposes its payload at exactly one
  field: **`value`**. This is what makes T3's `direction × data_type` factoring mechanical
  — `voltage.value` means the same thing under `voltage_observation` and `voltage_calculation`,
  so one query spans both. Descriptors needed to *interpret* the payload (unit, keys) ride
  **inside** the cell, beside the value — never hoisted alongside it. *(A `voltage` cell
  carries `source_unit` next to `source_value`; by the same rule an inline raster carries
  its `keys` next to its pixels. Exception, #73 item 15: the value's storage type is
  `datum_type`, stated ONCE on the statement, and colour/channels are read off the channel
  key. There is no `image` class: a raster is a value of what its pixels measure, #73
  item 51.)*
- **The cell layout is declared inline.** A named composite type (`voltage`, `count`,
  `ontology_term`, …) declares its sub-fields in the schema — the canonical value plus
  lossless source provenance — so the validator, the query-path generator, the viewer and
  the docs all read one source of truth. **A type that is only an enum string is
  undeclared**, and its internals are then known solely to whoever wrote the migrator.
- **Declaration is what makes a field queryable.** A value is indexable exactly to the
  depth its structure is declared; undeclared internals are an opaque blob no matter how
  well named. "Typed" must mean *machine-readable*, not *documented*.
- **Counting starts at 0, everywhere, and is declared once** (team, 2026-09-24). An index
  base is exactly the kind of fact a reader cannot recover from the numbers themselves, so
  V_eta has ONE rule rather than a per-field note:
  - **every index is 0-based**: a position along a key, a row of a document named by
    `labels_from`, a chunk number, `timed_sequence.value.presentation_order`;
  - *[SUPERSEDED FOR EDGES by T15, 2026-09-25: edges are no longer numbered at all. A
    position into a multi-edge is still 0-based — `presentation_order` value *k* is the
    *k*-th `item_id` entry — which is the first bullet above, not this one.]*
    **every numbered edge family is numbered from 0**: `time_reference_0`,
    `derived_from_0`, `presented_id_0`, … — so a 0-based index names its edge directly
    (`presentation_order` value *k* → `presented_id_k`);
  - **every file-series member is numbered from 0**: `body_data_0`, `body_data_1`, ….
  A family is declared as a `name_#` template carrying `multiple`, and the two always go
  together. did_v1 numbered its edges from 1 (NDI's `add_dependency_value_n` appends
  `name_(n+1)`). Migrators READ that numbering and never re-emit it. The three v1
  tombstones that declare a family (`ensemble` `neuron_id_#`, `daqsystem`
  `daqmetadatareader_id_#`, `syncgraph` `syncrule_id_#`) describe v1 documents as written,
  and a `_#` template matches a member whatever its number, so they need no change. Where a v1 number carried
  meaning (an ensemble's `neuron_id_3` is its third column), the migrator restates it as
  data — a `sequence` field — rather than trusting a name.

**The failure this names is not hypothetical.** The named types shipped for most of the
project as enum strings whose real layout lived in the meta-schema's prose and in
`struct('celsius', …)` literals inside migrators. The result: the validator could only
check `isstruct` inside a cell, and **26 of 35 `data_type` composites emitted no query
path at all** — no measured value in the corpus was indexable, silently, for as long as
the convention went unwritten. Two composites (`image`, `contrast_sensitivity`) had also
drifted off the one-payload-slot rule for exactly the same reason: nothing checked it.

**Litmus:** could a consumer that has never read our migrator code — a validator, an
indexer, a third-party reader — get the value out and know what it means, from the schema
alone? If it needs prose, an example, or our source, the structure is not declared.

### T15 — An edge is a noun ending `_id`; a repeated edge repeats that one name.
*(Decided in the #73 review, 2026-09-25. Supersedes T14's numbered-edge-family bullet and the
`_#` template. BUILT schema-side the same day (`tools/build_v_eta.py` section 12.7): every
V_eta edge carries its T15 name. Repeated names cannot be STORED until DID-matlab's work in
"What it costs" lands.)*

- **Every edge name is a noun ending `_id`.** No verbs, no prepositions, no bare role words:
  `owner` → `owner_id`, `relative_to` → `referent_id`, `derived_from_#` → `input_id`.
- **Name it for its target class when the edge just means "which X"** (`subject_id`,
  `software_id`, `epoch_id`). **Name it for its role when the target is generic or the role is
  not the target's name** (`instrument_id` → an entity, `value_id` → a data type,
  `parent_id`/`child_id`).
- **A name's meaning is fixed by its class, and stays within one sense across classes.**
  `input_id` is "what goes in" on a calculation (its sources) and on a clock alignment (the
  timeline fed to the polynomial); `parent_id` is the upper end of a typed relation on
  `directed_relation` and the protocol a variant came from on `method_parameters`. A reader who
  needs the exact meaning reads the class — the name never has to carry it alone.
- **A repeated edge repeats its name; it is never numbered.** A calculation with three inputs
  carries three `input_id` entries, with one input it carries one, and it is never
  `input_id_0`. Repetition is declared on the edge (`multiple`, `min_count`, `max_count`), not
  signalled by the name, so the spelling never depends on how many there are, and "what was
  derived from X" is one exact name, never a pattern over `name_*`.
- **Order is declared, not assumed.** Every repeated edge states **`ordered`**. `ordered: true`
  means position is data (0-based, T14): `timed_sequence.item_id` (the playlist indexes it),
  `key_labels_id` (a key's `labels_from` names an entry by position), and
  `clock_alignment_policy.clock_alignment_configuration_id` (NDI keeps the cheapest rule and
  breaks ties by rule order — `syncgraph.m`, `if c<lowcost`). `ordered: false` means the
  entries are a set and their order must not be read.
- **Why not `_k`.** A counter in a name hides a value in an identifier — a relational
  "repeating group" (`item1`, `item2`, …), which first normal form exists to remove — and it is
  structure carried by convention, which T14 forbids. Every established model repeats one
  name instead: a PROV activity has several `used` statements, FHIR elements repeat, a
  relational link table carries one row per edge plus a position column where order matters.
  did_v1's `_1`, `_2`, … came from a storage limit (a document's edge names had to be unique),
  not from a modelling choice.
- **v1 is untouched.** did_v1 tombstones keep their v1 spelling (`neuron_id_#`,
  `daqmetadatareader_id_#`, `syncrule_id_#`) because they describe documents as written;
  migrators read v1 numbering and never emit it.

**What it costs.** DID-matlab's `depends_on` table is keyed `(doc_id, name)`
(`+did2/+database/sqlitedb.m`), so a name cannot repeat today. It becomes
`(doc_id, name, position)`; `add_dependency_value_n` stops appending `_<n>` and
`dependency_value_n` returns every entry of a name in order; every reader that builds
`name_1`, `name_2`, … by hand asks for the list instead. These are the same call sites the
0-based renumbering already touches.

**Litmus:** could you write this edge's name without knowing how many there are, and could
you tell what it points at from the name plus its class alone?

**The vocabulary** (every V_eta edge on a persist or V_eta-designed class; v1 tombstones
excluded). 16 names are unchanged: `subject_id`, `software_id`, `session_id`, `epoch_id`,
`strain_id`, `acquisition_system_id`, `method_parameters_id`,
`coordinate_system_id`, `epoch_file_pattern_id`, `acquisition_metadata_reader_id`,
`clock_alignment_configuration_id`, `clock_alignment_policy_id`, `instrument_id`, `value_id`,
`reader_id`, `filter_id`. (#73 item 53, later, removed `runtime_environment_id` and added
`interpreter_id` and `operating_system_id` → `software`.)

| class | today | T15 | repeats | ordered |
|---|---|---|:-:|:-:|
| `data_body` | `owner` | `owner_id` | | |
| `directed_relation` | `parent`, `child` | `parent_id`, `child_id` | | |
| `relative_time_reference` | `relative_to` | `referent_id` | | |
| `coordinate_system` | `relative_to` | `referent_id` | | |
| `clock_alignment` | `from_reference`, `to_reference` | `input_id`, `output_id` | | |
| `method_parameters` | `derived_from_id` | `parent_id` | | |
| `control_designation` | `timed_sequence_id` | `value_id` *(class shape under review)* | | |
| `subject_calculation` | `derived_from_#` | `input_id` | yes | no |
| `control_designation` | `derived_from_#` | *(class shape under review)* | yes | no |
| `subject_interaction`, `directed_relation`, `epoch` | `time_reference_#` | `time_reference_id` | yes | no |
| `undirected_relation` | `entities_#` | `entity_id` | yes (exactly 2) | no |
| `timed_sequence` | `presented_id_#` | `item_id` | yes | **yes** |
| `subject_statement`, `data_body` | `axis_labels_#` | `key_labels_id` | yes | **yes** |
| `strain` | `background_strain_#` | `background_strain_id` | yes | no |
| `clock_alignment_configuration` | `acquisition_channels_#` | `acquisition_channels_id` | yes (0 or 2) | no |
| `acquisition_system` | `acquisition_metadata_reader_#` | `acquisition_metadata_reader_id` | yes | no |
| `clock_alignment_policy` | `clock_alignment_configuration_#` | `clock_alignment_configuration_id` | yes | **yes** |
| `interaction_purpose` | `interaction_id_#` | `interaction_id` | yes | no |

`referent_id` is the time plan's and NDI's own word for this edge (`ndi.time.timereference`
is `(referent, clocktype, epoch, time)`): the document whose timeline — or, for a coordinate
system, whose space — the values are measured in. The zero point on it is a separate thing
(`clock` for time, `origin` for space). `anchor_id` was rejected because "anchor" already
names the time-reference document itself (T6); `origin_id` because `origin` already names the
zero point.

---

## The meta-principle

**Meaning migrates from the class name into the graph + ontology.** The class set should
*shrink and stay principled*: a new measurement is a new composite (T12) or a new
`variable` (T2); a new grouping is an edge (T4); a new vocabulary is a binding (T8). If a
proposed class encodes a how, a where, a cardinality, a storage format, or a vocabulary
entry, it is not a class — it is a field, an edge, a `storage_mode`, or a binding.

**Litmus for any proposed class:** *Which of the four axes is genuinely new — the subject,
the statement direction, the data-type structure, or the relation?* If the answer is
"none, it's a variant of an existing one," it is not a new class.
