# V_eta: one entity class, statements by composition, CURIE identifiers

PROPOSAL, built ahead of signature at Jess's request (2026-10-08): "I'll sign
them after you make the changes." Nothing below carries a sign-off line. Each
section ends with "To be signed:" and the decision its sign-off line has to
name; the line itself is added by the team, never by Claude (operating rule 4). Decided in conversation with Jess,
2026-10-08.

The rule the whole document applies:

> **An entity is something the science describes**, including the named periods
> of the experiment (a session, an epoch). What is true of it is a statement,
> how it connects is a relation, and when it existed is its time reference.
> **Configuration is what the software needs to read the data**: its own class
> off `base`, with no statements. **A class exists only when its documents have
> a different shape** (T12).

## 1. Statements by composition

A statement's class is its DIRECTION -- `assertion`, `observation`,
`manipulation`, `calculation` -- and its value kind is a MIXIN: the document
lists the kind's chain in `document_class.superclasses` after its own.

    "document_class": {"class_name": "observation",
      "superclasses": ["interaction", "statement", "base", "temperature", "value", "data"]}
    "temperature": {"value": [{"celsius": 21.62, ...}]}

- The 42 `<kind>_<direction>` join classes go: they declared no field and no
  edge of their own (`term_assertion`'s `strain_id` excepted, see 4).
- **Exactly one value kind per statement.** A direction declares
  `"value_kind": {"root": "value", "count": 1}` on its `document_class`; the
  validator accepts the class's own chain followed by ONE concrete descendant of
  `value` (and that kind's chain, without repeating what the class chain already
  holds). A class whose own chain already contains a kind (a named calculator)
  takes none.
- **Named calculators: a v1 calculator that carries content of its own.** Kept:
  `tuning_curve_calculation` (`significance`, `model_fit`) and the four with an
  extra block -- `contrast_tuning_calculation`, `orientation_direction_tuning_calculation`,
  `spatial_frequency_tuning_calculation`, `temporal_frequency_tuning_calculation`.
  Folded (no content of their own): `speed_tuning_calculation` ->
  `tuning_curve_calculation`; `contrast_sensitivity_calculation`,
  `receptive_field_calculation`, `model_fit_calculation` -> `calculation` with
  that value kind.
- Search: `isa observation` AND `isa temperature`; both names are in the
  document's own superclasses, which the database indexes.

To be signed: statements are a direction class plus one value-kind mixin; the join leaves and the content-free named calculators go

## 2. `datum_type` becomes `data_type`, and is needed only for bytes

`value.datum_type` / `source_datum_type` are renamed `data_type` /
`source_data_type` (the class `data_type` became `value` on 2026-10-08, so the
name is free, and it is the v1 spelling of the same fact on five tombstones).
The rule narrows: present when `data_body` is true, or when the inline value is
an untyped array (a kind whose `value` is not a declared cell). A typed cell
already says its type (`celsius` is a `double`).

To be signed: datum_type is renamed data_type and required only for bytes or untyped arrays

## 3. `text`, a value kind

`text` with cells `{text, language}` (language optional, a BCP 47 tag). What
the text IS lives in the statement's `variable` (given name, email, how to
cite). No `name` or `email` kinds: neither has a canonical form.

To be signed: add the text value kind {text, language}

## 4. One `entity` class

`entity` becomes concrete. Its fields are identity only:

| field | |
|---|---|
| `type` | bound, required: organism, culture, tissue, cell, group, device, material, strain, product, software, person, organization, funding, dataset, study, publication, session, epoch, protocol |
| `name` | display name |
| `local_identifier` | handle, unique within its dataset; required per type (registry) |
| `description` | free text |
| `global_identifier` | list of CURIE / IRI strings (6) |
| `time_reference_#` | optional: when it existed or took place (a worm, hatching to death; a session, start to end; an epoch, one per clock) |

Deleted, each becoming `entity` with that `type`: `subject`, `strain`,
`product`, `software`, `person`, `organization`, `funding`, `web_resource`,
`dataset`, `study`, `publication`, `session`, `epoch`. Their other fields
become assertions (`term`, `text`, `date`) or relations:

| was | becomes |
|---|---|
| `strain.species`, `.genetic_strain_type`, `.phenotype`, `.breeding_type`, `.disease_model` | term assertions |
| `strain.laboratory_code`, `.synonym` | text assertions |
| `strain.background_strain_id` | relation `derived_from` (strain -> strain) |
| `product.catalog_number`, `.lot_number` | text assertions |
| `product.vendor_id` | relation `sold_by` (product -> organization) |
| `person.given_name`, `.family_name`, `.alternate_name`, `.email` | text assertions |
| `software.version` | text assertion |
| `dataset.*` (license, accessibility, ethics assessment, experimental approach, keyword) | term assertions |
| `dataset.how_to_cite`, `.version_innovation`, `.support_channel`, `.version`, `.short_name` | text assertions |
| `dataset.release_date`, `.copyright_year` | date / text assertions |
| `study.factors`, `.design` | term assertions |
| `publication.publication_date` / `.authors` | date assertion / `has_author` relations |
| `organization.short_name` | text assertion |

The value sets that were bound on those fields move to
`statement_bindings`, keyed on the variable.

**The type registry** (`entity_type_bindings` in `binding_registry_meta.json`):
for each type, what it requires (`local_identifier` for organism ... epoch,
session; `name` for the rest) and a description. The relation registry's
`child_types` / `parent_types` name these types.

To be signed: one concrete entity class with a bound type; the entity leaves go; per-type requirements live in a type registry

## 5. Strain is a relation

`term_assertion.strain_id` goes. A subject is an `instance_of` its strain
(`instance_of` widens to subject -> strain), and a strain's background is
`derived_from` (strain -> strain, the existing RO:0001000 relation). T17 gains a downward rule: what is asserted
of a strain or a product holds of each of its instances. This reverses the
2026-08-05 strain decision (an inline term plus an optional edge).

To be signed: strain is an instance_of relation; T17 adds type-to-instance inheritance

## 6. CURIE identifiers

`global_identifier` is a list of strings: a CURIE whose prefix is registered in
`CURIE_lookups_meta.json`, or a full IRI. The `scheme` field and its binding go.
Every registered prefix carries its Bioregistry `pattern`, fetched 2026-10-08
(`https://bioregistry.io/api/registry/<prefix>`), so the local id can be
checked. Prefixes are lowercase -- the registry's own recorded convention
("Prefixes are matched case-insensitively; by convention prefixes are written in
lowercase"), which is also Bioregistry's normalised prefix. Term nodes are
normalised to it (`NCIT:` -> `ncit:`, `RO:` -> `ro:`, ...).

- Award numbers: a grant DOI when there is one, else the funding entity's
  `local_identifier`. `AwardNumber` is not a prefix.
- UDI: Bioregistry has no prefix (`udi`, `gudid`: not found), so it is dropped.
- WormBase strains: Bioregistry has no `wbstrain`; the id is
  `wormbase:WBStrain00000001` (pattern `^(CE[0-9]{5}|WB[A-Z][a-z]+\d+)$`).
- `ndicloud` is registered as ours.

To be signed: global identifiers are CURIEs or IRIs from one lowercase prefix registry with Bioregistry patterns

## 7. `web_resource` retires; `protocol` is a type

A URL is an address for the thing it names, so it goes in that thing's
`global_identifier`. `has_homepage`, `stored_at` and `hosted_by` (web_resource -> organization) go.
`follows_protocol` points at an `entity {type: protocol}`; `input_data` at an
`entity {type: dataset}`; `documented_by` at a protocol or a publication.

To be signed: web_resource and the has_homepage / stored_at relations retire; protocol is an entity type

## 8. `acquisition_system` is configuration

`acquisition_system` moves off `entity` to `base`, gains an optional
`device_id` (the hardware, an entity of type device), and an epoch is
`recorded_by` its acquisition system (relation, epoch -> acquisition_system).
This reverses `acquisition_system ⊂ entity` from `V_eta_daq_family_decisions.md`
(team correction of 2026-08-08), which was chosen so an epoch's `instrument_id -> entity`
could reach it; the instrument is now the device entity behind `device_id`.

To be signed: acquisition_system is configuration off base, with an optional device_id; epochs are recorded_by it

## 9. `method_parameters.subject_id` becomes `entity_id`

Missed by the 2026-10-08 rename.

To be signed: method_parameters scopes to entity_id

## What this does NOT change, and what it costs

- The DID-matlab migrators and NDI's second pass stay pinned to the pre-#73
  schema (`v_eta-pre73`). Every corpus Bar-2 figure in CLAUDE.md was measured on
  that shape and says nothing about this one. Moving the migrators is one item
  on the PR #76 checklist.
- NDI's `getsubjects()` default (organism, culture, tissue, cell, group) is
  agreed and waits for the `ndi.entity` update.
- The configuration classes are not reviewed here.
