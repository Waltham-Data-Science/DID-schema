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
`method` (the verb), a per-sample `sample_time` cadence, an optional `instrument_id`, and
requires a `time_reference`. (SPEC §3–§5)

### T3 — A leaf class = a direction × a data type. This is the move that collapses the zoo.
Instead of hundreds of classes, **factor**: data-type composites (`mass`, `dose`,
`term`, `visual_grating`, …) × directions = one-word leaves (`mass_observation`,
`dose_manipulation`, `term_assertion`, `visual_grating_manipulation`,
`orientation_direction_tuning_calculation`). A new measurement is a new composite or a
new `variable`; it is **not** a new hand-written class. (SPEC §6)

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
`sampled_body` (self-describing — sample-time axis + typed datum + summary; partial-read,
value-searchable) and `opaque_body` (uninterpreted bytes). Every carrier — timeseries,
dataseries, zarr, image, generic_file — phases into those; **encoding/format is a field,
not a class**. Timing splits: the anchor lives in `time_reference`, the per-sample
cadence rides beside the value. (SPEC §8)

### T7 — Roles are edges, not subclasses.
The measuring/manipulating device is a subject (kind asserted), linked by a typed
`instrument_id`. `subject_id` = patient, `instrument_id` = agent, `method` = verb. No
organism/cell/instrument/medium subclasses. (SPEC §8, D2)

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
  `<data_type>`. **time_reference** = `<origin>_<mode>_reference`.
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
   vocabulary entry.
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
  role: v1's generic `parameters` split into **`conditions`** (the experimental conditions
  on a statement) and **`method_parameters`** (the algorithm config on an interaction);
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
