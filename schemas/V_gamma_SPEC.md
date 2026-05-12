# V_gamma_SPEC.md — DID/NDI Document Schema Format (V_gamma)

## Purpose

This document is a complete specification for the **V_gamma** schema set in the
`did-schema` repository. V_gamma inherits the V_beta flat directory layout
(one JSON file per document type at the top of `schemas/V_gamma/`) and
snake_case naming rules, and adds four things:

1. **Named composite types** (typedefs) — a spec-level mechanism for types
   that name a fixed composite shape with documented sub-fields. V_gamma
   defines `ontology_term` plus a family of SI-dimensioned quantity types
   that all share one sub-field layout: a canonical-unit value, an
   `approximate` flag, and a `source_unit`/`source_value` provenance pair.
   The shipped dimension types are `duration` (canonical: `seconds`),
   `volume` (`liters`), `mass` (`grams`), `length` (`meters`), `voltage`
   (`volts`), `current` (`amperes`), and `frequency` (`hertz`).
2. **A CURIE registry** — `schemas/V_gamma/CURIE_lookups_meta.json` maps
   CURIE prefixes to URI bases, labels, and metadata. Used by tooling to
   expand CURIEs and to flag approximate or unknown namespaces.
3. **A redesigned `ontology` annotation shape** — the field-level ontology
   annotation now uses `{"node": "<curie>", "name": "<label>"}` instead of
   the four-key V_beta form.
4. **Class-scoped property blocks at the document-instance level** — a
   V_gamma document carries its fields under per-class top-level blocks
   keyed by the declaring class's `class_name` (one block per class in
   the inheritance chain), rather than as a single flattened bag of
   fields. This restores the V_alpha document layout — collapsed so that
   the block key equals the class's `class_name` exactly, with no
   separate `property_listname` knob — and is described in "JSON
   Format: Document Instances" below.
5. **Class metadata under a top-level `document_class` header** — the
   class-identity fields (`class_name`, `class_version`, `superclasses`)
   live under a top-level `document_class` block on both schema files
   and document instances, restoring the V_alpha legacy NDI-matlab
   layout. `depends_on` stays at the top level (see "JSON Format:
   Document Instances" for the rationale).

The specification is language-agnostic — language-specific tooling (MATLAB,
Python, etc.) lives in separate repositories and consumes these schemas as a
dependency.

See `schemas/V_beta_SPEC.md` for the V_beta predecessor. This file stands
alone; a reader does not need to bounce between documents.

---

## Repository Overview

**Repo name:** `did-schema`

**Language:** JSON (schema definitions), Python (test tooling only).

**Purpose:** Define and validate the JSON schema format used by DID
(data-interface database) documents and NDI (neuroscience data interface)
documents. This repo is not NDI itself — it is the schema layer that NDI and
DID both depend on.

**What this repo does:**
- Defines the canonical JSON format for schema files that describe DID/NDI document types.
- Provides a meta-schema (a schema for schema files themselves) that validates schema files before they are used.
- Provides a CURIE registry for expanding ontology identifiers.
- Ships one JSON file per document type under `schemas/V_gamma/` using a flat layout.
- Ships Python-based unit tests that validate all schemas and document fixtures.

**What this repo does NOT do:**
- Provide runtime tooling for loading, parsing, or manipulating documents. That belongs in language-specific repos (e.g., `DID-matlab`, `DID-python`).
- Resolve CURIEs at validation time. The meta-schema does not structurally enforce that every CURIE prefix appears in the registry; consumer tooling does that and issues warnings.

---

## Repo File Structure

```
did-schema/
│
├── README.md
├── pyproject.toml                      ← Python test dependencies
│
├── schemas/
│   ├── V_gamma_SPEC.md                 ← (this file) V_gamma specification
│   ├── V_gamma_notes.md                ← V_gamma status and V_beta→V_gamma changes
│   ├── V_alpha/                        ← retained during migration (see notes)
│   ├── V_beta/                         ← retained during migration (see notes)
│   └── V_gamma/                        ← flat directory of V_gamma schemas
│       ├── did_schema_meta.json        ← meta-schema: validates schema files
│       ├── CURIE_lookups_meta.json     ← CURIE registry (prefix → URI base)
│       ├── base.json                   ← schema for the base document type
│       ├── directory.json              ← schema for the directory document type
│       ├── probe_location.json         ← schema for probe_location document type
│       └── ...                         ← one JSON file per document type (all snake_case)
│
└── tests/
    ├── conftest.py                     ← shared fixtures and helpers
    ├── test_meta_schema.py             ← meta-schema validation tests
    ├── test_schemas.py                 ← structural tests for schema files
    ├── test_documents.py               ← document fixture validation tests
    └── fixtures/
        ├── valid_base_document.json
        ├── invalid_base_document_missing_id.json
        └── ...
```

`V_alpha/` and `V_beta/` persist alongside `V_gamma/` during migration and
are removed only after migration completes, matching the approach described
in `V_beta_notes.md`.

### Schema directory layout

Each document type is a **single JSON file** at the top of `schemas/V_gamma/`,
named `<class_name>.json`. The filename stem must equal the document's
`document_class.class_name` value, and because class names must be
snake_case (see below) the filename is also snake_case. There is exactly
one schema file per document type; subdirectories and per-type directories
are not used.

The meta-schema (`did_schema_meta.json`) and the CURIE registry
(`CURIE_lookups_meta.json`) live alongside the document-type schemas in
`schemas/V_gamma/`. They are metadata files, not document type definitions;
they are not schemas for documents, and they are not themselves validated by
the meta-schema.

Path references in schema files use the `$NDISCHEMAPATH` token, resolved at
runtime by consumer tooling. Under the flat layout, a reference to another
schema resolves as `$NDISCHEMAPATH/<class_name>.json`. Blank document
definitions (templates) are the responsibility of language-specific tooling
repos, not this repo.

---

## Naming Convention

Schema files mix two vocabularies:

- **Standard JSON Schema keywords** — used as-is, without modification:
  `type`, `$schema`, `$id`, `$ref`, `$defs`, `properties`, `required`,
  `additionalProperties`, `items`, `oneOf`, `if`, `then`, `enum`, `const`,
  `pattern`, `description`, `title`, etc.

- **NDI-specific properties** — every property name introduced by this schema
  system (i.e., not part of the JSON Schema vocabulary) is written without
  any prefix. V_gamma drops the V_beta underscore prefix; the authoritative
  enumeration of reserved NDI names lives in
  `schemas/V_gamma/ndi_reserved_keys.json` (see "Reserved Keys" below) and is
  enforced by the meta-schema. Readers and tools that need to distinguish
  NDI vocabulary from JSON Schema vocabulary should consult the manifest
  rather than rely on a sigil.

The one deliberate overlap is the `type` keyword: it is the standard JSON Schema
keyword, but the enum values it accepts (`char`, `did_uid`, `matrix`, `duration`,
`ontology_term`, etc.) are NDI-specific. The key itself is kept without prefix
because it is standard; the allowed values are documented below.

### snake_case requirements (inherited from V_beta)

Every identifier introduced by the schema author must be snake_case.
Specifically:

- **Classnames.** `document_class.class_name` (and the `class_name` key
  inside each `document_class.superclasses` entry) must match
  `^[a-z][a-z0-9_]*$`.
- **Field names.** `name` on every field definition object (inside `fields`,
  at any nesting depth, including inside structure sub-fields) must match
  `^[a-z][a-z0-9_]*$`, with no more than two consecutive underscores.
- **Dependency names.** `name` on every `depends_on` entry must match
  `^[a-z][a-z0-9_]*(_#)?$` — the optional trailing `_#` is the numeric
  placeholder described in "Numbered Dependencies" below.
- **Directory record names.** `name` on every `directory` entry must match
  `^[a-z][a-z0-9_]*$`.
- **File record names.** `name` on every `file` entry should be snake_case
  where it is an identifier. When the `name` is a literal filename (e.g.
  `"level1.bin"`), the stem before the extension must be snake_case.
- **Filenames.** Each schema file is named `<class_name>.json`.

The **sub-field names of named composite types** (e.g., `seconds`,
`source_unit`, `node`, `name`) are fixed by this specification and also
happen to be snake_case. They are document-value field names, distinct
from the NDI-extension keys that wrap them.

Keys that are standard JSON Schema keywords or structural keys defined by
this specification (`document_class`, `class_name`, `class_version`,
`superclasses`, `mustBeNonEmpty`, etc.) are fixed by this specification
and are not subject to the snake_case rule above — they are literal keys
defined by the spec, not user-chosen names.

### Reserved Keys

The complete list of property names reserved by this schema system lives
in `schemas/V_gamma/ndi_reserved_keys.json`. That file is the discoverable,
machine-readable surface for the reserved vocabulary; the meta-schema
(`did_schema_meta.json`) is the enforcement surface. The manifest is split
into two short lists:

- `schema_file_keys` — names that appear in a class schema file
  (e.g. `base.json`, `probe_location.json`).
- `document_instance_keys` — names that appear in an NDI document instance
  on disk.

Schema authors **must not** reuse any reserved name as their own data
field name (i.e., as a `name` inside a `fields` entry). Tools and agents
that need to know whether a given key is part of NDI's vocabulary should
consult this manifest rather than guessing from the underscore prefix.

---

## JSON Format: Schema Files

Every schema file must conform to the following structure exactly. The
meta-schema enforces this.

### Top-Level Keys

| Key               | Type    | Required | May be empty? | Description |
|-------------------|---------|----------|---------------|-------------|
| `document_class`  | object  | yes      | no            | Class-identity header. Contains `class_name`, `class_version`, `superclasses`, `maturity_level`, and optional `abstract` — see "Document-Class Header" below. |
| `depends_on`     | array   | yes      | yes (`[]`)    | Array of dependency objects. Stays at the top level (not under `document_class`) because dependency *values* in document instances are cross-document; keeping the key at the top level mirrors the instance shape and lets a query engine answer `isa X AND depends_on Y` without descending into the header. |
| `file`           | array   | no       | yes (`[]`)    | Array of file record objects. Omit for document types with no associated files. |
| `directory`      | array   | no       | yes (`[]`)    | Array of directory record objects. Omit for document types with no associated directories. |
| `fields`         | array   | yes      | yes (`[]`)    | Array of field definition objects. |

No other top-level keys are permitted.

### Document-Class Header

```json
"document_class": {
    "class_name":      "probe_location",
    "class_version":   "2.0.0",
    "superclasses": [
        { "class_name": "base", "schema": "$NDISCHEMAPATH/base.json" }
    ],
    "maturity_level":  "work_in_progress"
}
```

| Key              | Type    | Required | Description |
|------------------|---------|----------|-------------|
| `class_name`     | string  | yes      | Unique name of the document type. Must match `^[a-z][a-z0-9_]*$` (snake_case). |
| `class_version`  | string  | yes      | Semantic version string `"MAJOR.MINOR.PATCH"`. |
| `superclasses`   | array   | yes      | Array of superclass reference objects (may be `[]`). |
| `maturity_level` | string  | yes      | `"work_in_progress"` or `"mature"`. |
| `abstract`       | boolean | no       | If `true`, no document may have `document_class.class_name` equal to this class — only concrete subclasses may be instantiated. Default `false` when omitted. Does not affect inheritance, field resolution, or `isa` query matching. |

**Naming-convention note.** `document_class` and its sub-keys form the
class-metadata header restored from the V_alpha legacy NDI-matlab layout.
Their unprefixed names are reserved (see `ndi_reserved_keys.json`) and
matching the V_alpha layout verbatim keeps tooling migrations mechanical.

### Abstract Classes (new in V_gamma)

A schema with `document_class.abstract: true` defines a type whose only
purpose is to be inherited from. Concrete subclasses of an abstract class
are instantiable; the abstract class itself is not. The single enforced
rule:

> A document is invalid if its `document_class.class_name` equals the
> `document_class.class_name` of a schema whose `document_class.abstract`
> is `true`.

Everything else about an abstract class behaves like a normal schema:

- Its `fields`, `depends_on`, `file`, `directory`, and
  `document_class.superclasses` participate in inheritance exactly as for
  a concrete class. The validator walks the class chain to collect the
  full set of required fields and dependencies; in a document instance,
  fields declared by an abstract class live in that class's own property
  block (see "JSON Format: Document Instances"), not in a subclass's
  block.
- `isa <abstract_class_name>` queries match every document whose class
  chain includes the abstract class.
- The meta-schema permits the key but does not enforce the instantiation
  rule — Phase 1 validation does (see "Validation Phases").

Marking a previously concrete class as `document_class.abstract: true` is
a **MAJOR** class-version change because existing documents with that
`document_class.class_name` become invalid. Use the abstract marker for
placeholder parent classes whose only role is shared structure (e.g.,
`zarr` as the parent of `image_zarr` and `ephys_zarr`).

### Superclass Reference Object (in schema files)

```json
{ "class_name": "base", "schema": "$NDISCHEMAPATH/base.json" }
```

Each entry in `document_class.superclasses` carries `class_name` (the
parent class's `class_name`) and `schema` (the path or token-substituted
path to the parent schema file).

### Dependency Object

```json
{
    "name":           "probe_id",
    "mustBeNonEmpty": true,
    "documentation":  "The unique ID of the probe this location is associated with.",
    "must_refer_to_document_class": ""
}
```

`multiple: true` enables the numbered-dependency pattern (`name_#`), see the
V_beta/V_gamma spec section on numbered dependencies for details; unchanged
in V_gamma.

### File Record Object

```json
{ "name": "spike_waveforms", "documentation": "Raw spike waveform binary data." }
```

### Directory Record Object

```json
{ "name": "raw_data", "documentation": "Directory of raw acquisition files." }
```

Directory record handling is unchanged from V_beta — see `V_beta_SPEC.md`'s
"Directory Document Type" section for the full tree-structure, manifest
format, and consumer tooling details. V_gamma does not alter this subsystem.

### Field Definition Object

Every entry in `fields` (at any nesting depth) must have **all** of the
following keys:

```json
{
    "name":           "sample_rate",
    "type":            "double",
    "blank_value":    null,
    "default_value":  30000.0,
    "mustBeNonEmpty": true,
    "mustBeScalar":   true,
    "mustNotHaveNaN": true,
    "queryable":      true,
    "ontology": {
        "node": "pato:0000044",
        "name": "frequency"
    },
    "documentation":  "Sampling rate in Hz.",
    "constraints":    { "minimum": 0.0 }
}
```

| Key               | Type            | Required | Notes |
|-------------------|-----------------|----------|-------|
| `name`           | string          | yes      | `^[a-z][a-z0-9_]*$` (snake_case), no more than two consecutive underscores. |
| `type`            | string          | yes      | One of the valid types (see Type System below). |
| `blank_value`    | any             | yes      | Value in a freshly constructed blank document. May fail validation. |
| `default_value`  | any             | yes      | Legitimate fallback. Must pass validation. |
| `mustBeNonEmpty` | boolean         | yes      | See per-type semantics below. |
| `mustBeScalar`   | boolean         | yes      | Value must be a single element (not array/matrix). |
| `mustNotHaveNaN` | boolean         | yes      | No NaN values permitted. For types where this is meaningless, must be `false`. |
| `queryable`      | boolean         | yes      | Whether this field is indexed for did.query/ndi.query. See `did_query_model.md` for the operators and shapes a queryable field is promised to support. |
| `ontology`       | object or null  | yes      | CURIE-based annotation of what the field itself means (e.g., this field denotes the concept of "frequency"). Not a place to store an ontology-rooted value — that is the `ontology_term` type. See below, or `null` if no suitable term exists. |
| `documentation`  | string          | yes      | Human-readable description. |
| `constraints`    | object          | yes      | Type-specific constraint keywords. Use `{}` for unconstrained. |

For `"type": "structure"` fields, an additional key is required, plus two
optional keys for the array-of-structure and discriminated-union variants:

| Key             | Type    | Required            | Notes |
|-----------------|---------|---------------------|-------|
| `fields`       | array   | yes (for structure) | Nested field definition objects. Same format, recursive. |
| `discriminator`| string  | no                  | Name of a sub-field within `fields` whose value tags variant elements. The discriminator sub-field must itself be of type `char` (typically with an `enum` in `constraints`). When present, consumer tooling and per-schema documentation specify which other sub-fields are required for each discriminator value; the meta-schema does not enforce variant-specific required-field rules. Only meaningful when the structure represents a discriminated union of element shapes. |

#### Scalar vs. array structure values (new in V_gamma)

The `mustBeScalar` flag selects the value shape carried by a
`"type": "structure"` field:

- `mustBeScalar: true` — value is **one object** matching `fields`. This
  is the historical V_gamma structure semantics.
- `mustBeScalar: false` — value is an **array of objects**, each matching
  `fields`. Empty array (`[]`) is permitted unless `mustBeNonEmpty:
  true`. Use this for repeated records (e.g., per-axis records, per-channel
  rendering settings, per-pyramid-level descriptors).

For an array-of-structure value, `mustBeNonEmpty: true` means the array
itself is non-empty; per-element non-empty checks happen via the per-element
`fields` rules. Consumer query tooling reaches into array-of-structure
values with `[*]` path syntax (see `did_query_model.md`).

The `matrix` type continues to be the right choice for numeric tabular data
(2D arrays of doubles or integers). The `structure` type with
`mustBeScalar: false` is the right choice for record-like repetition where
each element has named sub-fields.

### Ontology Annotation Object (new in V_gamma)

```json
{
    "node": "uberon:0002436",
    "name": "primary visual cortex"
}
```

| Key     | Type   | Required | Description |
|---------|--------|----------|-------------|
| `node` | string | yes      | CURIE identifier of the form `prefix:local`, where `prefix` must be a key in `CURIE_lookups_meta.json`. |
| `name` | string | yes      | Human-readable label of the ontology term (e.g., `"primary visual cortex"`). |

Setting the entire `ontology` value to `null` is valid.

The full resolvable URI is derived from the CURIE registry at lookup time; it
is not stored per-annotation. Consumer tooling is responsible for expansion
and for warning on unknown prefixes.

**Purpose:** `ontology` describes **what the field itself means** — it
annotates the field's concept so a reader can tell that, say, a
`sample_rate` field denotes the ontology concept "frequency". It is NOT
a place to store an ontology-rooted *value* that a document instance
carries. That is the job of the `ontology_term` type: a field with
`"type": "ontology_term"` holds a CURIE + label pair **as data** in each
document (e.g., a `location` field whose value is
`uberon:0002436`/"primary visual cortex"). Put differently:
- `ontology` (schema-level annotation) — "this field is *about* X."
- `ontology_term` (document-value type) — "the value *is* X."
The two can coexist on the same field: a field of type `ontology_term`
still has its own `ontology` annotation describing what the field
represents (often `iao:0000219` / "denotes").

**Note on key reuse:** the `ontology` annotation object (in a schema
file) and the `ontology_term` composite-type value (in a document
instance) share the sub-field names `node` and `name`. The annotation
describes what a field denotes; the value carries an ontology-rooted
datum. The two forms carry the same information model (CURIE + label)
but appear in different places — see "Named Composite Types" below.

### Query model (pointer)

The abstract query model that `queryable: true` promises is specified in
`schemas/did_query_model.md` (operators, composition, and known
limitations). The SPEC defines schema shape; the query model defines what
can be asked of a queryable field. The two evolve independently.

### Useful Ontology Terms

Relevant CURIEs for annotating fields:

| CURIE              | Label                           | Notes |
|--------------------|---------------------------------|-------|
| `iao:0000578`      | centrally registered identifier | Used for `id` fields |
| `iao:0000219`      | denotes                         | Used when a field names an entity in another ontology |
| `schema:name`      | name                            | Human-readable name |
| `schema:dateCreated` | dateCreated                   | Document creation timestamp |
| `ncit:C169028`     | Study Unique Identifier         | Useful for `id` / `session_id` style fields |
| `ncit:C67447`      | Session                         | "Time, period, or term devoted to some activity." |

---

## JSON Format: Type System

### Valid Types

| Type            | Description                                     | `constraints` keys                                   | Notes |
|-----------------|-------------------------------------------------|-------------------------------------------------------|-------|
| `did_uid`       | NDI/DID unique identifier string                | `{}` (none)                                           | |
| `char`          | Character array / string                        | `{ "maxLength": integer or null }`                    | `"string"` is accepted as an alias |
| `integer`       | Single integer value                            | `{ "minimum": integer or null, "maximum": integer or null }` | |
| `double`        | Single double-precision float                   | `{ "minimum": number or null, "maximum": number or null }`   | |
| `matrix`        | 2D array of doubles                             | `{ "rows": int or null, "cols": int or null, "minimum": number or null, "maximum": number or null }` | `mustBeScalar` should be `false` |
| `timestamp`     | ISO 8601 UTC timestamp string                   | `{}` (none)                                           | Validator checks format |
| `boolean`       | true/false                                      | `{}` (none)                                           | |
| `structure`     | Nested sub-document (JSON object)               | `{}` (none); use `fields` key for nested fields      | Recursive |
| `duration`      | Named composite: canonical seconds with unit provenance | `{ "minimum": number or null, "maximum": number or null, "allowed_units": array or null }` | Sub-fields: `seconds`, `approximate`, `source_unit`, `source_value`. See "Named Composite Types". `minimum`/`maximum` bound the canonical (`seconds`). |
| `volume`        | Named composite: canonical liters with unit provenance | `{ "minimum": number or null, "maximum": number or null, "allowed_units": array or null }` | Sub-fields: `liters`, `approximate`, `source_unit`, `source_value`. `minimum`/`maximum` bound the canonical (`liters`). |
| `mass`          | Named composite: canonical grams with unit provenance | `{ "minimum": number or null, "maximum": number or null, "allowed_units": array or null }` | Sub-fields: `grams`, `approximate`, `source_unit`, `source_value`. `minimum`/`maximum` bound the canonical (`grams`). |
| `length`        | Named composite: canonical meters with unit provenance | `{ "minimum": number or null, "maximum": number or null, "allowed_units": array or null }` | Sub-fields: `meters`, `approximate`, `source_unit`, `source_value`. `minimum`/`maximum` bound the canonical (`meters`). |
| `voltage`       | Named composite: canonical volts with unit provenance | `{ "minimum": number or null, "maximum": number or null, "allowed_units": array or null }` | Sub-fields: `volts`, `approximate`, `source_unit`, `source_value`. `minimum`/`maximum` bound the canonical (`volts`). |
| `current`       | Named composite: canonical amperes with unit provenance | `{ "minimum": number or null, "maximum": number or null, "allowed_units": array or null }` | Sub-fields: `amperes`, `approximate`, `source_unit`, `source_value`. `minimum`/`maximum` bound the canonical (`amperes`). |
| `frequency`     | Named composite: canonical hertz with unit provenance | `{ "minimum": number or null, "maximum": number or null, "allowed_units": array or null }` | Sub-fields: `hertz`, `approximate`, `source_unit`, `source_value`. `minimum`/`maximum` bound the canonical (`hertz`). |
| `ontology_term` | Named composite: CURIE ontology reference with label snapshot | `{ "allowed_namespaces": array or null }` | Sub-fields: `node`, `name`. See "Named Composite Types". |

#### Semantics of validation flags by type

| Type            | `mustBeNonEmpty` applies?                        | `mustBeScalar` applies?                | `mustNotHaveNaN` applies?                    |
|-----------------|---------------------------------------------------|------------------------------------------|------------------------------------------------|
| `did_uid`       | yes (non-empty string)                            | yes                                      | no — must be `false`                          |
| `char`          | yes (non-empty string)                            | yes                                      | no — must be `false`                          |
| `integer`       | yes                                               | yes                                      | yes                                            |
| `double`        | yes                                               | yes                                      | yes                                            |
| `matrix`        | yes (non-empty array)                             | no — should be `false`                   | yes (element-wise)                             |
| `timestamp`     | yes (non-empty string)                            | yes                                      | no — must be `false`                          |
| `boolean`       | yes                                               | yes (implicitly)                         | no — must be `false`                          |
| `structure`     | yes (non-empty object)                            | yes                                      | no — must be `false`                          |
| `duration`      | yes (seconds not null, source_unit non-empty, source_value not null) | yes — always true (single structured value) | yes (seconds and source_value not NaN) |
| `volume`        | yes (liters not null, source_unit non-empty, source_value not null) | yes — always true (single structured value) | yes (liters and source_value not NaN) |
| `mass`          | yes (grams not null, source_unit non-empty, source_value not null) | yes — always true (single structured value) | yes (grams and source_value not NaN) |
| `length`        | yes (meters not null, source_unit non-empty, source_value not null) | yes — always true (single structured value) | yes (meters and source_value not NaN) |
| `voltage`       | yes (volts not null, source_unit non-empty, source_value not null) | yes — always true (single structured value) | yes (volts and source_value not NaN) |
| `current`       | yes (amperes not null, source_unit non-empty, source_value not null) | yes — always true (single structured value) | yes (amperes and source_value not NaN) |
| `frequency`     | yes (hertz not null, source_unit non-empty, source_value not null) | yes — always true (single structured value) | yes (hertz and source_value not NaN) |
| `ontology_term` | yes (node non-empty)                              | yes — always true                        | no — must be `false`                          |

---

## Named Composite Types

V_gamma introduces a **named composite type** mechanism: certain `type`
values name a fixed composite shape with documented sub-fields, primitive
types, and validation-flag semantics. A named composite is a value-level
structure whose shape is known to the validator intrinsically from this
specification — schema authors do NOT declare the sub-fields with
`fields` (that is the role of the generic `structure` type).

### Why named composites?

- **DRY.** A recurring multi-field pattern becomes a single declaration.
- **Consistency.** Every value of a given named composite has identical
  shape across the corpus.
- **Semantic tagging.** Tooling can recognise "this field is a duration"
  or "this field is an ontology term" by `type`, not by naming convention.
- **Invariant enforcement.** The validator can check cross-sub-field
  invariants that would be unenforceable on four loose sibling fields.
- **Centralised evolution.** If the shape ever needs to grow, the change
  lives in this spec — not in every document type that uses it.

### Rules for named composites

- Sub-field names are fixed by the spec; authors do not choose them.
- Sub-field types are primitive (`char`, `double`, `boolean`, etc.).
- Sub-field names are data field names, parallel to the field names
  inside a generic `structure` — distinct from the NDI-extension keys
  enumerated in `ndi_reserved_keys.json`.
- `mustBeScalar` for a named composite value is always `true` (the value
  is a single structured object, not an array).
- A `null` value for a named composite field is allowed in
  `blank_value` / `default_value` positions; `mustBeNonEmpty`
  determines whether `null` is permitted at validation time.
- Query engines access sub-fields via dot paths (e.g.,
  `treatment_duration.seconds > 172800`).

### The SI-dimensioned family

`duration`, `volume`, `mass`, `length`, `voltage`, `current`, and
`frequency` are all variants of the same four-sub-field pattern. Each
stores a **canonical value** in a fixed SI unit alongside the author's
**original value and unit**, plus an **`approximate`** flag that
propagates precision loss through unit conversion. The sub-field that
holds the canonical value is named after the unit (`seconds`, `liters`,
`grams`, `meters`, `volts`, `amperes`, `hertz`) so queries read
naturally (e.g., `injection_volume.liters > 1.5e-9`,
`sample_rate.hertz >= 30000`).

The canonical unit for each dimension is the **practical SI unit** used in
lab work, not necessarily the strict SI base unit. That means `liters`
rather than cubic metres, and `grams` rather than kilograms. The rule is:
for a given dimension, there is exactly one canonical unit across the
whole corpus, so cross-document numeric queries are meaningful without
per-field conversion.

Each type supports the same three `constraints` keys. `minimum` and
`maximum` bound the canonical-unit value; the unit is determined by the
field's type (e.g., on a `volume` field, `minimum: 0` means "0 liters").

- `minimum` (number or null) — lower bound on the canonical value.
- `maximum` (number or null) — upper bound on the canonical value.
- `allowed_units` (array of strings or null) — restrict permissible
  `source_unit` values for this field.

All SI-dimensioned types share the `duration` sub-field layout:

| Sub-field           | Type    | Description |
|---------------------|---------|-------------|
| `<canonical_unit>`  | double  | Canonical value; what queries target. |
| `approximate`       | boolean | `true` iff `source_unit` is not an exact ratio of the canonical. Derived from the unit, not independently authored. For the pure-SI dimensions below, all listed source units are exact ratios, so `approximate` is always `false`; the sub-field is kept for structural uniformity with `duration`. |
| `source_unit`       | char    | The unit the author supplied. One of the listed source units for this dimension. |
| `source_value`      | double  | The original number the author supplied. |

### `duration` (new in V_gamma)

A duration value stores a canonical seconds value alongside the original
unit and value the author supplied, plus a flag marking values derived from
approximate units.

**Sub-fields (in document values):**

| Sub-field      | Type    | Description |
|----------------|---------|-------------|
| `seconds`      | double  | Canonical duration in seconds. This is what queries target. |
| `approximate`  | boolean | `true` iff `source_unit` is not an exact second-multiple. Derived from the unit, not independently authored. |
| `source_unit`  | char    | The unit the author supplied. One of: `nanosecond`, `microsecond`, `millisecond`, `second`, `minute`, `hour`, `day`, `week` (exact); `month`, `year` (approximate — see below). |
| `source_value` | double  | The original number the author supplied (e.g., `2` for "2 days"). |

**Unit conversions.** The exact units convert as expected. The approximate
units use fixed conventions:
- `month` = 30 × 86400 = 2,592,000 s
- `year` = 365 × 86400 = 31,536,000 s

Authors wanting calendar-aware durations should use a separate type (not
yet defined; see Future Candidates below).

**`constraints` keys allowed:**
- `minimum` (number or null) — lower bound on the canonical value (seconds).
- `maximum` (number or null) — upper bound on the canonical value (seconds).
- `allowed_units` (array of strings or null) — restrict permissible
  `source_unit` values for this field.

**Queries.** The generic dot-path query engine accesses a duration's
canonical value as `<field>.seconds`. Parsers that accept expressions like
`> 2 days` convert the literal to seconds (using the same registry) before
comparison. Because `source_unit`/`source_value` are plain sub-fields, they
are queryable too — e.g., to find all durations authored in weeks.

**Why canonical seconds?** One fixed canonical unit lets the generic
numeric query engine work unchanged. The `source_*` pair preserves author
intent for display and export. The `approximate` flag propagates the
precision information so consumers do not mistake a converted value for a
measured one. The three-field provenance plus one canonical value is the
minimum shape that keeps all three workflows (querying, displaying,
warning) honest.

### `volume` (new in V_gamma)

Canonical sub-field: `liters` (double).

**Allowed source units and conversion factors (unit → liters):**

| Source unit  | Factor (L) |
|--------------|------------|
| `nanoliter`  | 1e-9       |
| `microliter` | 1e-6       |
| `milliliter` | 1e-3       |
| `liter`      | 1          |
| `kiloliter`  | 1e3        |

All ratios are exact, so `approximate` is always `false` for volume values.

**`constraints` keys allowed:** `minimum`, `maximum`, `allowed_units`.
`minimum` and `maximum` bound the canonical (`liters`).

### `mass` (new in V_gamma)

Canonical sub-field: `grams` (double). Chosen over the strict SI base
`kilogram` because lab-scale masses read more naturally in grams.

**Allowed source units and conversion factors (unit → grams):**

| Source unit  | Factor (g) |
|--------------|------------|
| `nanogram`   | 1e-9       |
| `microgram`  | 1e-6       |
| `milligram`  | 1e-3       |
| `gram`       | 1          |
| `kilogram`   | 1e3        |

All ratios are exact.

**`constraints` keys allowed:** `minimum`, `maximum`, `allowed_units`.
`minimum` and `maximum` bound the canonical (`grams`).

### `length` (new in V_gamma)

Canonical sub-field: `meters` (double).

**Allowed source units and conversion factors (unit → meters):**

| Source unit  | Factor (m) |
|--------------|------------|
| `nanometer`  | 1e-9       |
| `micrometer` | 1e-6       |
| `millimeter` | 1e-3       |
| `centimeter` | 1e-2       |
| `meter`      | 1          |
| `kilometer`  | 1e3        |

All ratios are exact.

**`constraints` keys allowed:** `minimum`, `maximum`, `allowed_units`.
`minimum` and `maximum` bound the canonical (`meters`).

### `voltage` (new in V_gamma)

Canonical sub-field: `volts` (double).

**Allowed source units and conversion factors (unit → volts):**

| Source unit  | Factor (V) |
|--------------|------------|
| `nanovolt`   | 1e-9       |
| `microvolt`  | 1e-6       |
| `millivolt`  | 1e-3       |
| `volt`       | 1          |

All ratios are exact.

**`constraints` keys allowed:** `minimum`, `maximum`, `allowed_units`.
`minimum` and `maximum` bound the canonical (`volts`).

### `current` (new in V_gamma)

Canonical sub-field: `amperes` (double).

**Allowed source units and conversion factors (unit → amperes):**

| Source unit   | Factor (A) |
|---------------|------------|
| `nanoampere`  | 1e-9       |
| `microampere` | 1e-6       |
| `milliampere` | 1e-3       |
| `ampere`      | 1          |

All ratios are exact.

**`constraints` keys allowed:** `minimum`, `maximum`, `allowed_units`.
`minimum` and `maximum` bound the canonical (`amperes`).

### `frequency` (new in V_gamma)

Canonical sub-field: `hertz` (double). Hertz is SI-derived (1/second)
rather than an SI base unit, but it is the unit actually written in lab
work for sampling rates, firing rates, oscillation frequencies, and
stimulus frequencies, so it fits the practical-SI rule.

**Allowed source units and conversion factors (unit → hertz):**

| Source unit  | Factor (Hz) |
|--------------|-------------|
| `microhertz` | 1e-6        |
| `millihertz` | 1e-3        |
| `hertz`      | 1           |
| `kilohertz`  | 1e3         |
| `megahertz`  | 1e6         |
| `gigahertz`  | 1e9         |

All ratios are exact.

**`constraints` keys allowed:** `minimum`, `maximum`, `allowed_units`.
`minimum` and `maximum` bound the canonical (`hertz`).

### `ontology_term` (new in V_gamma)

An ontology term value stores a CURIE identifier alongside a human-readable
label snapshot taken at write time.

**Sub-fields (in document values):**

| Sub-field | Type | Description |
|-----------|------|-------------|
| `node`    | char | CURIE identifier of the form `prefix:local`, where `prefix` is a key in `CURIE_lookups_meta.json`. |
| `name`    | char | Human-readable label of the term at the time the document was written. Snapshot, not live — see note below. |

**`constraints` keys allowed:**
- `allowed_namespaces` (array of strings or null) — restrict the permitted
  CURIE prefixes for this field (e.g., `["uberon", "emapa"]` for a brain
  region field).

**Why carry a name at all?** Denormalisation, deliberately:
1. Raw-document readability — a human can read the JSON without consulting
   the ontology.
2. Cheap name-based search — substring and autocomplete queries against
   `<field>.name` work with the generic query engine, no ontology service
   needed.
3. Snapshot semantics — if the ontology later renames the term, the
   document still reflects the author's understanding.

`node` is authoritative identity; `name` is a convenience snapshot and may
drift from the ontology's current label. Queries that must be stable across
time use `<field>.node`; queries meant for discovery within a corpus can
use `<field>.name`.

**Provenance version.** V_gamma does NOT store a per-value
`source_version` for ontology terms. Document-level `datestamp` (inherited
from `base`) is sufficient to establish which ontology release era a
document was written in. If a particular study deliberately pins to a
specific ontology release across time, that belongs in a study-level
annotation, not on each term value.

### Future Candidate Composite Types

The following shapes recur in scientific data and are plausible additions
in a future version. They are **not** part of V_gamma.

- **`dimensioned_quantity`** — author-extensible escape hatch for
  dimensions the spec has not yet named. Shape would mirror the SI
  dimension family but carry the canonical unit name as a sub-field
  (`{canonical_value, canonical_unit, source_value, source_unit,
  approximate}`) or select a spec-registered dimension via
  `constraints.dimension`. V_gamma intentionally does not ship this:
  the seven pre-named dimensions (`duration`, `volume`, `mass`,
  `length`, `voltage`, `current`, `frequency`) cover current needs, and
  deferring the generic form avoids two authors disagreeing on
  canonical units for the same dimension. Add when an unnamed dimension
  clearly needs it in three or more schemas, or promote it to a named
  dimension instead.
- **`stereotaxic_coordinate`** — `{ap, ml, dv, reference_point, units}`.
  Strong near-term candidate given the existing `probe_location`,
  `virus_injection`, and `probe_geometry` schemas.
- **`value_with_uncertainty`** — `{value, stddev, distribution, units}`
  for measurements with known noise.
- **`software_version`** — `{name, version, commit_sha}` for
  reproducibility metadata.
- **`date_with_precision`** — `{datetime, precision}` for partial or
  uncertain dates.

Adding a named composite is a spec change: the type is added to the
`Valid Types` table, its sub-fields and `constraints` are documented, and
the meta-schema's `type` enum is extended. Schema authors cannot define
their own named composites; only the spec can.

---

## JSON Format: Document Instances

A V_gamma **document instance** — the JSON object stored in the database or
serialised on the wire — is not a flat bag of fields. It is organised into
**class-scoped property blocks**: one top-level block per class in the
document's inheritance chain, keyed by that class's `class_name`. Field
values live in the block of the class that declared the field.

This is the V_alpha document layout, collapsed: the property-block key is
the declaring class's `class_name` verbatim. V_alpha's separate
`property_listname` knob is removed — the block key must equal
`class_name` exactly, with no second name to coordinate.

The schema-file shape is unaffected: a class's `<class_name>.json` still
declares its own `fields` and its own `document_class` header.
Inheritance still works by walking the `document_class.superclasses`
chain. The class-scoped layout applies only to the document-instance
wire shape; field-collection ("flattening") remains an internal
validation and query-indexing step.

### Top-level keys of a document instance

| Key              | Type    | Required | Description |
|------------------|---------|----------|-------------|
| `document_class` | object  | yes      | Class-identity header. Sub-keys `class_name`, `class_version`, `superclasses` — see "Document-Class Header (in document instances)" below. |
| `depends_on`    | array   | yes      | Array of dependency-value objects (see "Dependency Values" below). Empty `[]` if the class chain declares no dependencies. Top-level, not under `document_class`, because dependency values are cross-document. |
| `<class_name>`   | object  | one per class in the chain | A property block whose key is the `class_name` of a class in this document's inheritance chain (including the concrete class itself). Contents are described below. |

No other top-level keys are permitted. Exactly one property block must
appear for each class in `{concrete class} ∪ {transitive superclasses}`,
with no extras and no omissions, even when a class declares zero fields
(in which case its block is `{}`).

### Document-Class Header (in document instances)

```json
"document_class": {
    "class_name":    "probe_location",
    "class_version": "2.0.0",
    "superclasses": [
        { "class_name": "base", "class_version": "1.0.0" }
    ]
}
```

| Key             | Type   | Required | Description |
|-----------------|--------|----------|-------------|
| `class_name`    | string | yes      | Concrete class this document instantiates. Must match `^[a-z][a-z0-9_]*$` and must not equal the `class_name` of any schema with `document_class.abstract: true`. |
| `class_version` | string | yes      | Semantic version of the concrete class's schema at write time. Must satisfy the MAJOR-version rule under "Versioning Rules" relative to the schema used at validation time. |
| `superclasses`  | array  | yes      | Snapshot of the inheritance chain at write time. Each entry is a superclass reference object (see "Schema-Reference Forms" below) listing the superclass's `class_name` and `class_version`. Empty `[]` for `base`. |

### Schema-reference forms (in document instances vs. schema files)

Schema files and document instances both reference superclasses, but they
serve different purposes and so carry different keys.

| Position                                              | Required keys                  | Optional keys | Purpose |
|-------------------------------------------------------|--------------------------------|---------------|---------|
| `document_class.superclasses[i]` in a schema file     | `class_name`, `schema`        | —             | Resolve the superclass schema file at validation time. |
| `document_class.superclasses[i]` in a document instance | `class_name`, `class_version` | —             | Pin the inheritance chain as it stood when the document was written. No `schema` path is required because the validator looks the class up by name. |

### Property block contents

Each property block holds the field values declared by that class's
schema, keyed by `name`:

```json
"base": {
    "id":         "412...",
    "session_id": "412...",
    "name":       "rig_1",
    "datestamp":  "2026-05-11T..."
}
```

Rules:

- **Provenance is structural.** Every field value sits inside the property
  block of the class that *declared* it. A reader who wants to find a
  field's `documentation`, `ontology`, `constraints`, or type opens
  `schemas/V_gamma/<block_key>.json` and looks the field up by `name`.
- **No shadowing, by construction.** A subclass `fields` entry named
  `id` and the `base.fields` entry named `id` are not in conflict —
  each lives in its own block, so the document paths `base.id` and
  `<subclass>.id` are distinct values with distinct definitions. Field
  identity is `(declaring_class, name)`, not `name` alone. There is
  no override mechanism because there is nothing to override: if two
  classes in a chain happen to declare the same `name`, they simply
  define two separate fields that happen to share a leaf name.
- **Required vs. empty blocks.** A class with zero declared fields still
  contributes a block; that block is the empty object `{}`. This keeps
  the wire shape predictable: the set of top-level keys equals
  `{document_class, depends_on}` plus the class chain, with no implicit
  omissions.
- **No cross-block field movement.** A field declared in `base` is not
  copied into the subclass's block. Validators and query engines that
  need a flat view of all fields build it themselves by walking the
  chain (see "Field collection for validation and queries" below).

### Dependency Values

The top-level `depends_on` array carries the runtime dependency
**values** (the IDs of other documents). Each entry is:

```json
{ "name": "probe_id", "value": "aabb1122ccdd3344_aabb1122ccdd3344" }
```

| Key      | Type   | Required | Description |
|----------|--------|----------|-------------|
| `name`  | string | yes      | Role name matching a `name` declared in some class's `depends_on` (after numbered-dependency expansion — `syncrule_id_1`, `syncrule_id_2`, etc. — for `multiple: true` declarations). |
| `value`  | string | yes      | The `id` (DID UID) of another document. May be empty only if the declaring `depends_on` entry has `mustBeNonEmpty: false`. |

Dependency declarations live in the class schemas; dependency *values*
live at the top level of the document, not inside any class's property
block. Two reasons: (a) `depends_on` referential integrity is a
cross-document concern that does not belong to any one class's data, and
(b) keeping the dependency list in one place lets a query engine answer
`isa X AND depends_on Y` without walking class blocks.

### Field collection for validation and queries

The class-scoped wire shape is the **storage** layout. Internal tooling
that wants a single flat view still has one:

- **Validators** walk the `document_class.superclasses` chain to collect
  the union of required fields and dependencies, then check that each
  declared field is present in the right block.
- **Query engines** derive a flat set of indexed paths from the chain
  (e.g., `daqsystem.sample_rate.hertz`). Class-scoped storage does not
  change which paths are queryable — only that the leading segment is
  the declaring class's name. See `did_query_model.md`.
- **`isa <class_name>`** matches any document whose
  `document_class.class_name` is `<class_name>` or whose
  `document_class.superclasses` chain transitively contains
  `<class_name>`. Class-scoped storage makes the chain explicit on every
  document; no separate inheritance index is required.

### Example document

For a `daqsystem` class whose `superclasses` snapshot is
`[{"class_name": "base", "class_version": "1.0.0"}]`:

```json
{
    "document_class": {
        "class_name":    "daqsystem",
        "class_version": "1.0.0",
        "superclasses": [
            { "class_name": "base", "class_version": "1.0.0" }
        ]
    },
    "depends_on": [],
    "base": {
        "id":         "4126919195e6b5af_40d651024919a2e4",
        "session_id": "4126919195e8839b_40c6d9f78d173ae7",
        "name":       "rig_1",
        "datestamp":  "2026-05-11T12:00:00.000Z"
    },
    "daqsystem": {
        "sample_rate": {
            "hertz":        30000.0,
            "approximate":  false,
            "source_unit":  "hertz",
            "source_value": 30000.0
        }
    }
}
```

A reader staring at this JSON can tell at a glance that `sample_rate`
was declared by `daqsystem` (it sits inside the `daqsystem` block) and
that `id`/`session_id`/`name`/`datestamp` were declared by `base`.
Looking up the field definitions is a one-step path: open
`schemas/V_gamma/<block_key>.json` and find the field by `name`.

### V_alpha → V_gamma migration (document instances)

V_alpha already used class-scoped property blocks with a separate
`property_listname` per class and a top-level `document_class` header.
The V_gamma migration for a V_alpha document is mechanical:

1. Keep the V_alpha `document_class` header in place; its three sub-keys
   (`class_name`, `class_version`, `superclasses`) carry over verbatim.
   Each entry of `superclasses` in an instance keeps `class_name` and
   `class_version`; drop legacy `definition`/`property_list_name`
   sub-keys.
2. Rename `depends_on` (V_alpha) to `depends_on` (V_gamma); inside each
   entry, the role key is `name`.
3. Rename each property block whose `property_list_name` differs from
   the class's `class_name` so the block key equals `class_name`.
4. Apply the V_alpha → V_gamma transformations to field values
   themselves (e.g., named-composite refactors documented in
   `V_gamma_notes.md`).

No re-flattening or de-flattening of the document body is required.

---

## CURIE Registry

`schemas/V_gamma/CURIE_lookups_meta.json` is an advisory registry that maps
CURIE prefixes (used in `ontology_term.node` values and in field-level
`ontology.node` annotations) to their authoritative URI base and
metadata. It is not a JSON Schema; the meta-schema does not validate
against it.

### Prefix entry shape

Each entry under `prefixes` has the following keys:

| Key              | Type    | Description |
|------------------|---------|-------------|
| `label`         | string  | Human-readable name of the ontology (e.g., `"Uber-anatomy Ontology"`). |
| `uri_base`      | string  | URI base to which the CURIE local part is appended. May be empty if `uri_style` is `local`. |
| `uri_style`     | string  | One of `obo_underscore`, `direct`, `local` (see below). |
| `approximate`   | boolean | `true` if identifiers in this namespace are placeholders or otherwise not expected to resolve. |
| `documentation` | string  | Human-readable description. |

### URI expansion styles

| Style              | Expansion rule |
|--------------------|----------------|
| `obo_underscore`   | Concatenate `uri_base` with the CURIE local part verbatim. E.g., `uberon:0002436` → `http://purl.obolibrary.org/obo/UBERON_0002436`. |
| `direct`           | Concatenate `uri_base` with the CURIE local part verbatim. E.g., `schema:name` → `https://schema.org/name`. |
| `local`            | No URI expansion; the CURIE is the authoritative identifier and `uri_base` is empty. Used for namespaces without a canonical web URI. |

### What consumer tooling should do

- Expand CURIEs to URIs using this registry.
- Warn (not error) when a CURIE uses a prefix not in the registry.
- Warn when a CURIE uses a prefix flagged `approximate: true` (e.g.,
  `placeholder:` values in in-progress data).
- Treat prefix matching as case-insensitive; by convention, authors write
  prefixes in lowercase.

### Adding a prefix

1. Add an entry under `prefixes` with all five metadata keys.
2. Bump `format_version` by at least PATCH.
3. Update the "CURIE Registry" entry in this SPEC if the new prefix is
   widely used in the schemas.

### Relationship to `ontology` annotations and `ontology_term` values

Both the field-level `ontology` annotation and the `ontology_term`
document-value type use CURIEs. A CURIE in either location is valid iff
its prefix appears in this registry. The meta-schema does not enforce this;
consumer tooling does.

---

## JSON Format: `blank_value` vs. `default_value`

These are intentionally and importantly different:

- **`blank_value`**: The value a field holds in a document that was just
  constructed from the definition file, before the user has provided any
  data. This value is *allowed to fail validation*. Common blank values:
  `null`, `""`, `[]`, `{}`, `0`. For named composite types (the
  SI-dimensioned family and `ontology_term`), `null` is the conventional
  blank value.

- **`default_value`**: A value that *must pass validation* and is used as
  a fallback during programmatic document construction when the caller
  does not supply a value. Think of it as the "reasonable default" for
  automated pipelines. For composite types, either `null` (when the field
  is optional) or a full valid structure.

The validator must:
1. Accept `blank_value` without complaint (it is never validated).
2. Validate `default_value` against the field's type and constraints when
   the schema is loaded, and emit a warning if `default_value` does not
   itself pass validation.

---

## JSON Format: Versioning Rules

`document_class.class_version` uses semantic versioning: `"MAJOR.MINOR.PATCH"`.

| Part    | Increment when... | Effect on existing documents |
|---------|-------------------|------------------------------|
| MAJOR   | A field is removed, renamed, or changes type; a `mustBeNonEmpty` is added to a previously optional field; a new required dependency is added; a superclass is added or removed | Existing documents **may fail** validation against the new schema. Migration required. |
| MINOR   | A new optional field is added; an ontology annotation is added or corrected; a constraint is relaxed; documentation is substantially improved | Existing documents still **pass** validation. New fields can be populated on re-save. |
| PATCH   | Documentation text is corrected; `default_value` is changed; formatting cleanup with no behavioural change | No change to validation behaviour. |

Changes that affect only schema-file syntax (such as the V_beta → V_gamma
transformation of the `ontology` annotation shape from four keys to two,
or the move of class-identity fields under the `document_class` header)
do **not** bump `document_class.class_version`, because the validity of
existing documents is unaffected. Such edits are recorded in
`V_gamma_notes.md`.

---

## Validation Phases

Document validation is split into two phases. Phase 1 requires only the
document and its schema. Phase 2 requires access to the database. Both
phases are the responsibility of consumer tooling — this repo defines the
rules; consumer tooling enforces them.

### Phase 1 — Schema-level validation (single document)

Checks that can be performed with only the document and its schema file(s):

- The document's top-level keys are exactly
  `{document_class, depends_on}` plus one property block per class in
  the inheritance chain (concrete class plus every transitive
  superclass). No extras and no omissions.
- The `document_class.class_name` is not the `class_name` of a schema
  with `document_class.abstract: true`. (Documents must instantiate a
  concrete subclass.)
- The `document_class.superclasses` snapshot at the top of the document
  is consistent with the class chain derived from the schema files
  (same set, same order, class-name-by-class-name).
- Each property block contains exactly the fields declared in that
  class's `fields`, with no extras. Fields declared by an ancestor
  live in the ancestor's block, not in the subclass's block.
- `mustBeNonEmpty` fields satisfy the per-type semantics above.
- `mustBeScalar` fields are single values, not arrays — **except** for
  `type: "structure"` fields where `mustBeScalar: false` declares the
  value to be an array of objects each matching `fields`. For such
  array-of-structure fields, each element is validated against the
  per-element `fields` rules.
- `mustNotHaveNaN` fields contain no NaN values.
- Type-specific format checks: `timestamp` matches ISO 8601 UTC,
  `did_uid` matches the UID pattern, each SI-dimensioned type
  (`duration`, `volume`, `mass`, `length`, `voltage`, `current`,
  `frequency`) is an object with exactly the four sub-fields
  (`<canonical_unit>`, `approximate`, `source_unit`, `source_value`) of
  correct primitive types, `ontology_term` is an object with exactly
  the two sub-fields.
- SI-dimensioned types: `approximate` is consistent with `source_unit` per
  the unit registry; the canonical sub-field value must equal
  `source_value × unit_factor(source_unit)` exactly, using the fixed
  conversion table for the dimension given in this spec (for `duration`,
  `month = 2,592,000 s`, `year = 31,536,000 s`, other units exact; for
  `volume`, `mass`, `length`, `voltage`, `current`, `frequency`, every
  listed source unit is an exact ratio of the canonical unit). All unit
  conversions are constants, so no tolerance window applies.
- `ontology_term`: `node` matches CURIE pattern `^[a-z][a-z0-9_]*:[^\s:]+$`.
- Type-specific constraint checks in `constraints`: on every
  SI-dimensioned type, `minimum` and `maximum` (if present) bound the
  canonical value; on `ontology_term`, `allowed_namespaces` restricts
  the permitted CURIE prefixes.
- `depends_on` entries with `mustBeNonEmpty: true` have non-empty values.
- `document_class.class_version` compatibility (same MAJOR version as
  the schema's `document_class.class_version`).
- `directory` and `file` record names are unique across both arrays.

### Phase 2 — Database-level validation (cross-document)

Unchanged from V_beta:

- **Referential integrity of `depends_on`**: each dependency `value` must
  be the `id` of an existing document or one queued for insertion.
- **Uniqueness of `id`**: no collisions with existing documents.
- **Any other cross-document invariants** defined by the application layer.

Phase 2 is specified here but enforced by consumer tooling.

### CURIE resolution (advisory, not a validation phase)

Consumer tooling should check, with warnings rather than errors, that
every CURIE used in an `ontology.node` or `ontology_term.node` position
uses a prefix present in `CURIE_lookups_meta.json`. Prefixes flagged
`approximate: true` should produce an informational warning.

---

## The Meta-Schema

`schemas/V_gamma/did_schema_meta.json` is a JSON Schema Draft 7 file
(standard JSON Schema) that validates any NDI schema file.

The meta-schema must enforce:
- Required top-level keys: `document_class`, `depends_on`, `fields`.
- Optional top-level keys, if present, have correct structure: `file`,
  `directory`.
- `document_class` is an object with the required keys `class_name`,
  `class_version`, `superclasses`, and `maturity_level`, and the optional
  key `abstract` (boolean). No other keys are permitted.
- `document_class.class_name` matches `^[a-z][a-z0-9_]*$`.
- Every `name` on a field, dependency, or record matches the appropriate
  snake_case pattern.
- `document_class.class_version` matches `^\d+\.\d+\.\d+$`.
- `document_class.maturity_level` is `"work_in_progress"` or `"mature"`.
- `document_class.superclasses` is an array of superclass references,
  each with exactly the keys `class_name` and `schema`.
- `depends_on` is an array of dependency objects.
- `file` / `directory` (if present) are arrays of the correct shape.
- `fields` is an array of field definition objects.
- Each field definition has all required keys with correct types.
- `type` is one of: `did_uid`, `char`, `string`, `integer`, `double`,
  `matrix`, `timestamp`, `boolean`, `structure`, `duration`, `volume`,
  `mass`, `length`, `voltage`, `current`, `frequency`, `ontology_term`.
- `ontology` is either `null` or an object with exactly `node` (string)
  and `name` (string).
- `mustBeNonEmpty`, `mustBeScalar`, `mustNotHaveNaN`, `queryable`
  are all booleans.
- For `type: "structure"`, the `fields` key is present. The optional
  `discriminator` key, if present, is a string naming a sub-field within
  `fields` (the discriminator semantics themselves are not validated by
  the meta-schema).

The meta-schema does **not** structurally validate the internal shape of
named composite document values (the SI-dimensioned types and
`ontology_term`) — that is the document validator's responsibility. The
meta-schema validates schema files, not documents. Similarly, the
meta-schema does not validate that CURIE prefixes appear in the registry.

---

## Example Schema Files

### `schemas/V_gamma/base.json`

```json
{
    "document_class": {
        "class_name":      "base",
        "class_version":   "1.0.0",
        "superclasses":    [],
        "maturity_level":  "work_in_progress"
    },
    "depends_on":     [],
    "file":           [],
    "fields": [
        {
            "name":           "id",
            "type":            "did_uid",
            "blank_value":    "",
            "default_value":  "",
            "mustBeNonEmpty": true,
            "mustBeScalar":   true,
            "mustNotHaveNaN": false,
            "queryable":      true,
            "ontology": {
                "node": "iao:0000578",
                "name": "centrally registered identifier"
            },
            "documentation": "Unique identifier for this document instance.",
            "constraints":   {}
        },
        {
            "name":           "session_id",
            "type":            "did_uid",
            "blank_value":    "",
            "default_value":  "",
            "mustBeNonEmpty": true,
            "mustBeScalar":   true,
            "mustNotHaveNaN": false,
            "queryable":      true,
            "ontology":       null,
            "documentation":  "Unique identifier of the session this document belongs to.",
            "constraints":    {}
        },
        {
            "name":           "name",
            "type":            "char",
            "blank_value":    "",
            "default_value":  "",
            "mustBeNonEmpty": false,
            "mustBeScalar":   true,
            "mustNotHaveNaN": false,
            "queryable":      true,
            "ontology": {
                "node": "schema:name",
                "name": "name"
            },
            "documentation": "Human-readable name for this document.",
            "constraints":   { "maxLength": 256 }
        },
        {
            "name":           "datestamp",
            "type":            "timestamp",
            "blank_value":    "",
            "default_value":  "2018-12-05T18:36:47.241Z",
            "mustBeNonEmpty": true,
            "mustBeScalar":   true,
            "mustNotHaveNaN": false,
            "queryable":      true,
            "ontology": {
                "node": "schema:dateCreated",
                "name": "dateCreated"
            },
            "documentation": "UTC timestamp of document creation in ISO 8601 format.",
            "constraints":   {}
        }
    ]
}
```

### `schemas/V_gamma/probe_location.json`

```json
{
    "document_class": {
        "class_name":      "probe_location",
        "class_version":   "2.0.0",
        "superclasses": [
            { "class_name": "base", "schema": "$NDISCHEMAPATH/base.json" }
        ],
        "maturity_level":  "work_in_progress"
    },
    "depends_on": [
        {
            "name":           "probe_id",
            "mustBeNonEmpty": true,
            "documentation":  "The unique ID of the probe document this location is associated with.",
            "must_refer_to_document_class": ""
        }
    ],
    "file":   [],
    "fields": [
        {
            "name":           "location",
            "type":            "ontology_term",
            "blank_value":    null,
            "default_value":  null,
            "mustBeNonEmpty": false,
            "mustBeScalar":   true,
            "mustNotHaveNaN": false,
            "queryable":      true,
            "ontology": {
                "node": "schema:location",
                "name": "location"
            },
            "documentation": "Anatomical or functional location where the probe is sampling, as an ontology term (e.g., 'uberon:0002436' / 'primary visual cortex').",
            "constraints":   {}
        }
    ]
}
```

### Example `duration` field (hypothetical `treatment_duration` on `treatment`)

```json
{
    "name":           "treatment_duration",
    "type":            "duration",
    "blank_value":    null,
    "default_value":  null,
    "mustBeNonEmpty": false,
    "mustBeScalar":   true,
    "mustNotHaveNaN": true,
    "queryable":      true,
    "ontology":       null,
    "documentation":  "How long the treatment was administered.",
    "constraints": {
        "minimum":       0,
        "allowed_units": ["second", "minute", "hour", "day", "week"]
    }
}
```

A document value for this field might look like:

```json
"treatment_duration": {
    "seconds":      172800.0,
    "approximate":  false,
    "source_unit":  "day",
    "source_value": 2.0
}
```

### Example `volume` field (hypothetical `injection_volume` on `virus_injection`)

```json
{
    "name":           "injection_volume",
    "type":            "volume",
    "blank_value":    null,
    "default_value":  null,
    "mustBeNonEmpty": false,
    "mustBeScalar":   true,
    "mustNotHaveNaN": true,
    "queryable":      true,
    "ontology":       null,
    "documentation":  "Volume of virus solution injected.",
    "constraints": {
        "minimum":       0,
        "allowed_units": ["nanoliter", "microliter", "milliliter"]
    }
}
```

A document value for this field might look like:

```json
"injection_volume": {
    "liters":       1.5e-9,
    "approximate":  false,
    "source_unit":  "nanoliter",
    "source_value": 1.5
}
```

The other SI-dimensioned types (`mass`, `length`, `voltage`, `current`,
`frequency`) follow the same template with their canonical sub-field
name; the `constraints` keys are identical (`minimum`, `maximum`,
`allowed_units`), with `minimum`/`maximum` interpreted in the
dimension's canonical unit.

---

## Test Tooling (Python)

The test suite uses Python with `pytest` and `jsonschema`. These tests
validate the schema files themselves — they do not provide runtime
document tooling.

### Test categories

- **`test_meta_schema.py`** — Validates all schema files against
  `did_schema_meta.json` using JSON Schema Draft 7.
- **`test_schemas.py`** — Structural tests: field names match naming
  patterns, types are valid, required keys are present, superclass
  references are consistent, class_names are unique.
- **`test_documents.py`** — Validates document fixtures against their
  schemas using a lightweight Python validator.

### Running

```bash
pip install pytest jsonschema
pytest
```

---

## Key Design Decisions

1. **`blank_value` and `default_value` are always both present** in
   every field definition.
2. **All three validation flags are always present** on every field.
3. **`fields` is the universal key** for property lists.
4. **Validation is a pull action, not a push action.**
5. **Superclass fields are inherited by chain-walking, not by
   document-instance flattening.** Inheritance is resolved by walking
   `document_class.superclasses` at validation and query-planning
   time. Document instances carry fields in class-scoped property
   blocks (one top-level block per class in the chain, keyed by
   `class_name`), not in a single flat namespace. See "JSON Format:
   Document Instances".
6. **`ontology` is required on every field, but may be `null`.**
   `ontology` annotates what the field *means* (the concept the field
   represents); it is not a place to store an ontology-rooted value.
   Ontology-rooted values go in a field of type `ontology_term`.
7. **Validation has two phases.** Phase 1 (schema-level) and Phase 2
   (database-level).
8. **Language-specific tooling lives elsewhere.**
9. **Custom property names are prefixed with `_`.**
10. **`constraints` accepts standard JSON Schema validation keywords**
    for primitive types, and named composite-specific keys for
    composites (`minimum` / `maximum` / `allowed_units` for each
    SI-dimensioned type — `minimum`/`maximum` always apply to the
    canonical value, whose unit is determined by the field's type;
    `allowed_namespaces` for `ontology_term`).
11. **Numbered dependencies use the `name_#` pattern.**
12. **`file` and `directory` are optional top-level keys.**
13. **Directories are stored as separate documents, not inline metadata.**
14. **`open_binaryfile` on a directory document resolves filenames from
    the manifest.**
15. **Named composite types are spec-defined, not author-defined.**
    V_gamma ships `duration`, `volume`, `mass`, `length`, `voltage`,
    `current`, `frequency`, and `ontology_term`. Adding a new composite
    is a spec change, not a schema-author action.
16. **SI-dimensioned types use practical SI units as canonical.** One
    fixed canonical unit per dimension (`seconds`, `liters`, `grams`,
    `meters`, `volts`, `amperes`, `hertz`) keeps the generic numeric
    query engine working unchanged and makes cross-document comparisons
    meaningful without per-field conversion. The canonical is the unit
    actually written in lab literature, not necessarily the strict SI
    base (`grams` rather than `kilogram`, `liters` rather than `cubic
    metre`; `hertz` is SI-derived rather than base but is what lab work
    uses). The `source_*` sub-fields preserve author intent;
    `approximate` propagates precision loss through unit conversion.
17. **`ontology_term` carries a label snapshot.** `node` is authoritative;
    `name` is a provenance snapshot frozen at write time. This enables
    raw-document readability and cheap name-based search without an
    ontology service, at the cost of accepting label drift.
18. **The CURIE registry is advisory.** The meta-schema does not enforce
    prefix membership. Consumer tooling warns on unknown or approximate
    prefixes.
19. **`ontology` annotations use CURIE form.** The V_gamma shape
    `{node, name}` replaces V_beta's four-key
    `{_namespace, _term, _name, _uri}`. The URI is derived from the
    registry.
20. **Schema-file-syntax changes do not bump `class_version`.**
    Transforming `ontology` annotation shape, or relocating
    class-identity keys under `document_class`, does not invalidate
    existing documents; only document-level changes bump the class
    version.
21. **Class-scoped property blocks are the document-instance wire shape.**
    A document carries fields in per-class top-level blocks keyed by
    `class_name`, restoring the V_alpha layout collapsed so that the
    block key equals `class_name` exactly (no separate
    `property_listname`). Provenance is structural: a field's
    declaring class is the block it sits in, and field identity is
    `(declaring_class, name)` — same-named entries in two classes
    along a chain are simply two distinct fields, not a shadow or
    override of one another. See "JSON Format: Document Instances".

22. **Class metadata lives under a top-level `document_class` header.**
    `class_name`, `class_version`, and `superclasses` sit inside a
    nested `document_class` block on both schema files and document
    instances, restoring the V_alpha legacy NDI-matlab layout. Matching
    the V_alpha layout verbatim keeps tooling migrations mechanical.
    `depends_on` stays at the top
    level because dependency *values* are cross-document and keeping
    them out of the header lets a query engine answer
    `isa X AND depends_on Y` without descending into the header.
