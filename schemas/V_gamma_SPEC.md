# V_gamma_SPEC.md — DID/NDI Document Schema Format (V_gamma)

## Purpose

This document is a complete specification for the **V_gamma** schema set in the
`did-schema` repository. V_gamma inherits the V_beta flat directory layout
(one JSON file per document type at the top of `schemas/V_gamma/`) and
snake_case naming rules, and adds three things:

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
3. **A redesigned `_ontology` annotation shape** — the field-level ontology
   annotation now uses `{"_node": "<curie>", "_name": "<label>"}` instead of
   the four-key V_beta form.

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
named `<classname>.json`. The filename stem must equal the document's
`_classname` value, and because classnames must be snake_case (see below) the
filename is also snake_case. There is exactly one schema file per document
type; subdirectories and per-type directories are not used.

The meta-schema (`did_schema_meta.json`) and the CURIE registry
(`CURIE_lookups_meta.json`) live alongside the document-type schemas in
`schemas/V_gamma/`. They are metadata files, not document type definitions;
they are not schemas for documents, and they are not themselves validated by
the meta-schema.

Path references in schema files use the `$NDISCHEMAPATH` token, resolved at
runtime by consumer tooling. Under the flat layout, a reference to another
schema resolves as `$NDISCHEMAPATH/<classname>.json`. Blank document
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
  system (i.e., not part of the JSON Schema vocabulary) is **prefixed with an
  underscore (`_`)**. This makes it immediately visible to readers and tooling
  whether a property is a standard JSON Schema keyword or an NDI extension.

The one deliberate overlap is the `type` keyword: it is the standard JSON Schema
keyword, but the enum values it accepts (`char`, `did_uid`, `matrix`, `duration`,
`ontology_term`, etc.) are NDI-specific. The key itself is kept without prefix
because it is standard; the allowed values are documented below.

### snake_case requirements (inherited from V_beta)

Every identifier introduced by the schema author must be snake_case.
Specifically:

- **Classnames.** `_classname` (top-level and inside each `_superclasses`
  entry) must match `^[a-z][a-z0-9_]*$`.
- **Field names.** `_name` on every field definition object (inside `_fields`,
  at any nesting depth, including inside structure sub-fields) must match
  `^[a-z][a-z0-9_]*$`, with no more than two consecutive underscores.
- **Dependency names.** `_name` on every `_depends_on` entry must match
  `^[a-z][a-z0-9_]*(_#)?$` — the optional trailing `_#` is the numeric
  placeholder described in "Numbered Dependencies" below.
- **Directory record names.** `_name` on every `_directory` entry must match
  `^[a-z][a-z0-9_]*$`.
- **File record names.** `_name` on every `_file` entry should be snake_case
  where it is an identifier. When the `_name` is a literal filename (e.g.
  `"level1.bin"`), the stem before the extension must be snake_case.
- **Filenames.** Each schema file is named `<classname>.json`.

The **sub-field names of named composite types** (e.g., `seconds`,
`source_unit`, `node`, `name`) are fixed by this specification and also
happen to be snake_case. They are not underscore-prefixed because they are
document-value field names, not schema-extension keys.

Keys that are standard JSON Schema keywords or underscore-prefixed structural
keys (`_classname`, `_class_version`, `_mustBeNonEmpty`, etc.) are fixed by
this specification and are not subject to the snake_case rule above — they are
literal keys defined by the spec, not user-chosen names.

---

## JSON Format: Schema Files

Every schema file must conform to the following structure exactly. The
meta-schema enforces this.

### Top-Level Keys

| Key               | Type   | Required | May be empty? | Description |
|-------------------|--------|----------|---------------|-------------|
| `_classname`      | string | yes      | no            | Unique name of the document type. Must match `^[a-z][a-z0-9_]*$` (snake_case). |
| `_class_version`  | string | yes      | no            | Semantic version string `"MAJOR.MINOR.PATCH"`. |
| `_maturity_level` | string | yes      | no            | `"work_in_progress"` or `"mature"`. |
| `_superclasses`   | array  | yes      | yes (`[]`)    | Array of superclass reference objects. |
| `_depends_on`     | array  | yes      | yes (`[]`)    | Array of dependency objects. |
| `_file`           | array  | no       | yes (`[]`)    | Array of file record objects. Omit for document types with no associated files. |
| `_directory`      | array  | no       | yes (`[]`)    | Array of directory record objects. Omit for document types with no associated directories. |
| `_fields`         | array  | yes      | yes (`[]`)    | Array of field definition objects. |

No other top-level keys are permitted.

### Superclass Reference Object

```json
{ "_classname": "base", "_schema": "$NDISCHEMAPATH/base.json" }
```

### Dependency Object

```json
{
    "_name":           "probe_id",
    "_mustBeNonEmpty": true,
    "_documentation":  "The unique ID of the probe this location is associated with.",
    "_must_refer_to_document_class": ""
}
```

`_multiple: true` enables the numbered-dependency pattern (`_name_#`), see the
V_beta/V_gamma spec section on numbered dependencies for details; unchanged
in V_gamma.

### File Record Object

```json
{ "_name": "spike_waveforms", "_documentation": "Raw spike waveform binary data." }
```

### Directory Record Object

```json
{ "_name": "raw_data", "_documentation": "Directory of raw acquisition files." }
```

Directory record handling is unchanged from V_beta — see `V_beta_SPEC.md`'s
"Directory Document Type" section for the full tree-structure, manifest
format, and consumer tooling details. V_gamma does not alter this subsystem.

### Field Definition Object

Every entry in `_fields` (at any nesting depth) must have **all** of the
following keys:

```json
{
    "_name":           "sample_rate",
    "type":            "double",
    "_blank_value":    null,
    "_default_value":  30000.0,
    "_mustBeNonEmpty": true,
    "_mustBeScalar":   true,
    "_mustNotHaveNaN": true,
    "_queryable":      true,
    "_ontology": {
        "_node": "pato:0000044",
        "_name": "frequency"
    },
    "_documentation":  "Sampling rate in Hz.",
    "_constraints":    { "minimum": 0.0 }
}
```

| Key               | Type            | Required | Notes |
|-------------------|-----------------|----------|-------|
| `_name`           | string          | yes      | `^[a-z][a-z0-9_]*$` (snake_case), no more than two consecutive underscores. |
| `type`            | string          | yes      | One of the valid types (see Type System below). |
| `_blank_value`    | any             | yes      | Value in a freshly constructed blank document. May fail validation. |
| `_default_value`  | any             | yes      | Legitimate fallback. Must pass validation. |
| `_mustBeNonEmpty` | boolean         | yes      | See per-type semantics below. |
| `_mustBeScalar`   | boolean         | yes      | Value must be a single element (not array/matrix). |
| `_mustNotHaveNaN` | boolean         | yes      | No NaN values permitted. For types where this is meaningless, must be `false`. |
| `_queryable`      | boolean         | yes      | Whether this field is indexed in the database. |
| `_ontology`       | object or null  | yes      | CURIE-based annotation of what the field itself means (e.g., this field denotes the concept of "frequency"). Not a place to store an ontology-rooted value — that is the `ontology_term` type. See below, or `null` if no suitable term exists. |
| `_documentation`  | string          | yes      | Human-readable description. |
| `_constraints`    | object          | yes      | Type-specific constraint keywords. Use `{}` for unconstrained. |

For `"type": "structure"` fields, an additional key is required:

| Key       | Type  | Required            | Notes |
|-----------|-------|---------------------|-------|
| `_fields` | array | yes (for structure) | Nested field definition objects. Same format, recursive. |

### Ontology Annotation Object (new in V_gamma)

```json
{
    "_node": "uberon:0002436",
    "_name": "primary visual cortex"
}
```

| Key     | Type   | Required | Description |
|---------|--------|----------|-------------|
| `_node` | string | yes      | CURIE identifier of the form `prefix:local`, where `prefix` must be a key in `CURIE_lookups_meta.json`. |
| `_name` | string | yes      | Human-readable label of the ontology term (e.g., `"primary visual cortex"`). |

Setting the entire `_ontology` value to `null` is valid.

The full resolvable URI is derived from the CURIE registry at lookup time; it
is not stored per-annotation. Consumer tooling is responsible for expansion
and for warning on unknown prefixes.

**Purpose:** `_ontology` describes **what the field itself means** — it
annotates the field's concept so a reader can tell that, say, a
`sample_rate` field denotes the ontology concept "frequency". It is NOT
a place to store an ontology-rooted *value* that a document instance
carries. That is the job of the `ontology_term` type: a field with
`"type": "ontology_term"` holds a CURIE + label pair **as data** in each
document (e.g., a `location` field whose value is
`uberon:0002436`/"primary visual cortex"). Put differently:
- `_ontology` (schema-level annotation) — "this field is *about* X."
- `ontology_term` (document-value type) — "the value *is* X."
The two can coexist on the same field: a field of type `ontology_term`
still has its own `_ontology` annotation describing what the field
represents (often `iao:0000219` / "denotes").

**Note on underscore convention:** the annotation keys carry the leading
`_` because they are NDI-extension keys inside a schema file. The
document-value sub-fields of the `ontology_term` composite type (`node`,
`name`) do NOT carry leading underscores because those are data field
names — see "Named Composite Types" below. The two forms carry the same
information model (CURIE + label) but appear in different places.

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

| Type            | Description                                     | `_constraints` keys                                   | Notes |
|-----------------|-------------------------------------------------|-------------------------------------------------------|-------|
| `did_uid`       | NDI/DID unique identifier string                | `{}` (none)                                           | |
| `char`          | Character array / string                        | `{ "maxLength": integer or null }`                    | `"string"` is accepted as an alias |
| `integer`       | Single integer value                            | `{ "minimum": integer or null, "maximum": integer or null }` | |
| `double`        | Single double-precision float                   | `{ "minimum": number or null, "maximum": number or null }`   | |
| `matrix`        | 2D array of doubles                             | `{ "rows": int or null, "cols": int or null, "minimum": number or null, "maximum": number or null }` | `_mustBeScalar` should be `false` |
| `timestamp`     | ISO 8601 UTC timestamp string                   | `{}` (none)                                           | Validator checks format |
| `boolean`       | true/false                                      | `{}` (none)                                           | |
| `structure`     | Nested sub-document (JSON object)               | `{}` (none); use `_fields` key for nested fields      | Recursive |
| `duration`      | Named composite: canonical seconds with unit provenance | `{ "minimum_seconds": number or null, "maximum_seconds": number or null, "allowed_units": array or null }` | Sub-fields: `seconds`, `approximate`, `source_unit`, `source_value`. See "Named Composite Types". |
| `volume`        | Named composite: canonical liters with unit provenance | `{ "minimum_liters": number or null, "maximum_liters": number or null, "allowed_units": array or null }` | Sub-fields: `liters`, `approximate`, `source_unit`, `source_value`. |
| `mass`          | Named composite: canonical grams with unit provenance | `{ "minimum_grams": number or null, "maximum_grams": number or null, "allowed_units": array or null }` | Sub-fields: `grams`, `approximate`, `source_unit`, `source_value`. |
| `length`        | Named composite: canonical meters with unit provenance | `{ "minimum_meters": number or null, "maximum_meters": number or null, "allowed_units": array or null }` | Sub-fields: `meters`, `approximate`, `source_unit`, `source_value`. |
| `voltage`       | Named composite: canonical volts with unit provenance | `{ "minimum_volts": number or null, "maximum_volts": number or null, "allowed_units": array or null }` | Sub-fields: `volts`, `approximate`, `source_unit`, `source_value`. |
| `current`       | Named composite: canonical amperes with unit provenance | `{ "minimum_amperes": number or null, "maximum_amperes": number or null, "allowed_units": array or null }` | Sub-fields: `amperes`, `approximate`, `source_unit`, `source_value`. |
| `frequency`     | Named composite: canonical hertz with unit provenance | `{ "minimum_hertz": number or null, "maximum_hertz": number or null, "allowed_units": array or null }` | Sub-fields: `hertz`, `approximate`, `source_unit`, `source_value`. |
| `ontology_term` | Named composite: CURIE ontology reference with label snapshot | `{ "allowed_namespaces": array or null }` | Sub-fields: `node`, `name`. See "Named Composite Types". |

#### Semantics of validation flags by type

| Type            | `_mustBeNonEmpty` applies?                        | `_mustBeScalar` applies?                | `_mustNotHaveNaN` applies?                    |
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
`_fields` (that is the role of the generic `structure` type).

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
- Sub-field names are **not** underscore-prefixed — they are data field
  names, parallel to the field names inside a generic `structure`.
- `_mustBeScalar` for a named composite value is always `true` (the value
  is a single structured object, not an array).
- A `null` value for a named composite field is allowed in
  `_blank_value` / `_default_value` positions; `_mustBeNonEmpty`
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

Each type supports the same three `_constraints` keys, with the
minimum/maximum keys named after the canonical unit:

- `minimum_<canonical>` (number or null)
- `maximum_<canonical>` (number or null)
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

**`_constraints` keys allowed:**
- `minimum_seconds` (number or null) — lower bound on the canonical seconds.
- `maximum_seconds` (number or null) — upper bound.
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

**`_constraints` keys allowed:** `minimum_liters`, `maximum_liters`,
`allowed_units`.

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

**`_constraints` keys allowed:** `minimum_grams`, `maximum_grams`,
`allowed_units`.

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

**`_constraints` keys allowed:** `minimum_meters`, `maximum_meters`,
`allowed_units`.

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

**`_constraints` keys allowed:** `minimum_volts`, `maximum_volts`,
`allowed_units`.

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

**`_constraints` keys allowed:** `minimum_amperes`, `maximum_amperes`,
`allowed_units`.

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

**`_constraints` keys allowed:** `minimum_hertz`, `maximum_hertz`,
`allowed_units`.

### `ontology_term` (new in V_gamma)

An ontology term value stores a CURIE identifier alongside a human-readable
label snapshot taken at write time.

**Sub-fields (in document values):**

| Sub-field | Type | Description |
|-----------|------|-------------|
| `node`    | char | CURIE identifier of the form `prefix:local`, where `prefix` is a key in `CURIE_lookups_meta.json`. |
| `name`    | char | Human-readable label of the term at the time the document was written. Snapshot, not live — see note below. |

**`_constraints` keys allowed:**
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
  `_constraints.dimension`. V_gamma intentionally does not ship this:
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
`Valid Types` table, its sub-fields and `_constraints` are documented, and
the meta-schema's `type` enum is extended. Schema authors cannot define
their own named composites; only the spec can.

---

## CURIE Registry

`schemas/V_gamma/CURIE_lookups_meta.json` is an advisory registry that maps
CURIE prefixes (used in `ontology_term.node` values and in field-level
`_ontology._node` annotations) to their authoritative URI base and
metadata. It is not a JSON Schema; the meta-schema does not validate
against it.

### Prefix entry shape

Each entry under `_prefixes` has the following keys:

| Key              | Type    | Description |
|------------------|---------|-------------|
| `_label`         | string  | Human-readable name of the ontology (e.g., `"Uber-anatomy Ontology"`). |
| `_uri_base`      | string  | URI base to which the CURIE local part is appended. May be empty if `_uri_style` is `local`. |
| `_uri_style`     | string  | One of `obo_underscore`, `direct`, `local` (see below). |
| `_approximate`   | boolean | `true` if identifiers in this namespace are placeholders or otherwise not expected to resolve. |
| `_documentation` | string  | Human-readable description. |

### URI expansion styles

| Style              | Expansion rule |
|--------------------|----------------|
| `obo_underscore`   | Concatenate `_uri_base` with the CURIE local part verbatim. E.g., `uberon:0002436` → `http://purl.obolibrary.org/obo/UBERON_0002436`. |
| `direct`           | Concatenate `_uri_base` with the CURIE local part verbatim. E.g., `schema:name` → `https://schema.org/name`. |
| `local`            | No URI expansion; the CURIE is the authoritative identifier and `_uri_base` is empty. Used for namespaces without a canonical web URI. |

### What consumer tooling should do

- Expand CURIEs to URIs using this registry.
- Warn (not error) when a CURIE uses a prefix not in the registry.
- Warn when a CURIE uses a prefix flagged `_approximate: true` (e.g.,
  `empty:` placeholders in in-progress data).
- Treat prefix matching as case-insensitive; by convention, authors write
  prefixes in lowercase.

### Adding a prefix

1. Add an entry under `_prefixes` with all five metadata keys.
2. Bump `_format_version` by at least PATCH.
3. Update the "CURIE Registry" entry in this SPEC if the new prefix is
   widely used in the schemas.

### Relationship to `_ontology` annotations and `ontology_term` values

Both the field-level `_ontology` annotation and the `ontology_term`
document-value type use CURIEs. A CURIE in either location is valid iff
its prefix appears in this registry. The meta-schema does not enforce this;
consumer tooling does.

---

## JSON Format: `_blank_value` vs. `_default_value`

These are intentionally and importantly different:

- **`_blank_value`**: The value a field holds in a document that was just
  constructed from the definition file, before the user has provided any
  data. This value is *allowed to fail validation*. Common blank values:
  `null`, `""`, `[]`, `{}`, `0`. For named composite types (the
  SI-dimensioned family and `ontology_term`), `null` is the conventional
  blank value.

- **`_default_value`**: A value that *must pass validation* and is used as
  a fallback during programmatic document construction when the caller
  does not supply a value. Think of it as the "reasonable default" for
  automated pipelines. For composite types, either `null` (when the field
  is optional) or a full valid structure.

The validator must:
1. Accept `_blank_value` without complaint (it is never validated).
2. Validate `_default_value` against the field's type and constraints when
   the schema is loaded, and emit a warning if `_default_value` does not
   itself pass validation.

---

## JSON Format: Versioning Rules

`_class_version` uses semantic versioning: `"MAJOR.MINOR.PATCH"`.

| Part    | Increment when... | Effect on existing documents |
|---------|-------------------|------------------------------|
| MAJOR   | A field is removed, renamed, or changes type; a `_mustBeNonEmpty` is added to a previously optional field; a new required dependency is added; a superclass is added or removed | Existing documents **may fail** validation against the new schema. Migration required. |
| MINOR   | A new optional field is added; an ontology annotation is added or corrected; a constraint is relaxed; documentation is substantially improved | Existing documents still **pass** validation. New fields can be populated on re-save. |
| PATCH   | Documentation text is corrected; `_default_value` is changed; formatting cleanup with no behavioural change | No change to validation behaviour. |

Changes that affect only schema-file syntax (such as the V_beta → V_gamma
transformation of the `_ontology` annotation shape from four keys to two)
do **not** bump `_class_version`, because the validity of existing
documents is unaffected. Such edits are recorded in `V_gamma_notes.md`.

---

## Validation Phases

Document validation is split into two phases. Phase 1 requires only the
document and its schema. Phase 2 requires access to the database. Both
phases are the responsibility of consumer tooling — this repo defines the
rules; consumer tooling enforces them.

### Phase 1 — Schema-level validation (single document)

Checks that can be performed with only the document and its schema file(s):

- All fields declared in the schema (including inherited superclass
  fields) are present.
- `_mustBeNonEmpty` fields satisfy the per-type semantics above.
- `_mustBeScalar` fields are single values, not arrays.
- `_mustNotHaveNaN` fields contain no NaN values.
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
- Type-specific constraint checks in `_constraints` (e.g.,
  `minimum_seconds`/`maximum_seconds` for durations,
  `minimum_liters`/`maximum_liters` for volumes, and so on for each
  SI-dimensioned type; `allowed_namespaces` for ontology terms).
- `_depends_on` entries with `_mustBeNonEmpty: true` have non-empty values.
- `_class_version` compatibility (same MAJOR version as the schema).
- `_directory` and `_file` record names are unique across both arrays.

### Phase 2 — Database-level validation (cross-document)

Unchanged from V_beta:

- **Referential integrity of `_depends_on`**: each dependency `value` must
  be the `id` of an existing document or one queued for insertion.
- **Uniqueness of `id`**: no collisions with existing documents.
- **Any other cross-document invariants** defined by the application layer.

Phase 2 is specified here but enforced by consumer tooling.

### CURIE resolution (advisory, not a validation phase)

Consumer tooling should check, with warnings rather than errors, that
every CURIE used in an `_ontology._node` or `ontology_term.node` position
uses a prefix present in `CURIE_lookups_meta.json`. Prefixes flagged
`_approximate: true` should produce an informational warning.

---

## The Meta-Schema

`schemas/V_gamma/did_schema_meta.json` is a JSON Schema Draft 7 file
(standard JSON Schema) that validates any NDI schema file.

The meta-schema must enforce:
- Required top-level keys: `_classname`, `_class_version`,
  `_maturity_level`, `_superclasses`, `_depends_on`, `_fields`.
- Optional top-level keys, if present, have correct structure: `_file`,
  `_directory`.
- `_classname` matches `^[a-z][a-z0-9_]*$`.
- Every `_name` on a field, dependency, or record matches the appropriate
  snake_case pattern.
- `_class_version` matches `^\d+\.\d+\.\d+$`.
- `_maturity_level` is `"work_in_progress"` or `"mature"`.
- `_superclasses` is an array of superclass references.
- `_depends_on` is an array of dependency objects.
- `_file` / `_directory` (if present) are arrays of the correct shape.
- `_fields` is an array of field definition objects.
- Each field definition has all required keys with correct types.
- `type` is one of: `did_uid`, `char`, `string`, `integer`, `double`,
  `matrix`, `timestamp`, `boolean`, `structure`, `duration`, `volume`,
  `mass`, `length`, `voltage`, `current`, `frequency`, `ontology_term`.
- `_ontology` is either `null` or an object with exactly `_node` (string)
  and `_name` (string).
- `_mustBeNonEmpty`, `_mustBeScalar`, `_mustNotHaveNaN`, `_queryable`
  are all booleans.
- For `type: "structure"`, the `_fields` key is present.

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
    "_classname":     "base",
    "_class_version": "1.0.0",
    "_superclasses":  [],
    "_depends_on":    [],
    "_file":          [],
    "_fields": [
        {
            "_name":           "id",
            "type":            "did_uid",
            "_blank_value":    "",
            "_default_value":  "",
            "_mustBeNonEmpty": true,
            "_mustBeScalar":   true,
            "_mustNotHaveNaN": false,
            "_queryable":      true,
            "_ontology": {
                "_node": "iao:0000578",
                "_name": "centrally registered identifier"
            },
            "_documentation": "Unique identifier for this document instance.",
            "_constraints":   {}
        },
        {
            "_name":           "session_id",
            "type":            "did_uid",
            "_blank_value":    "",
            "_default_value":  "",
            "_mustBeNonEmpty": true,
            "_mustBeScalar":   true,
            "_mustNotHaveNaN": false,
            "_queryable":      true,
            "_ontology":       null,
            "_documentation":  "Unique identifier of the session this document belongs to.",
            "_constraints":    {}
        },
        {
            "_name":           "name",
            "type":            "char",
            "_blank_value":    "",
            "_default_value":  "",
            "_mustBeNonEmpty": false,
            "_mustBeScalar":   true,
            "_mustNotHaveNaN": false,
            "_queryable":      true,
            "_ontology": {
                "_node": "schema:name",
                "_name": "name"
            },
            "_documentation": "Human-readable name for this document.",
            "_constraints":   { "maxLength": 256 }
        },
        {
            "_name":           "datestamp",
            "type":            "timestamp",
            "_blank_value":    "",
            "_default_value":  "2018-12-05T18:36:47.241Z",
            "_mustBeNonEmpty": true,
            "_mustBeScalar":   true,
            "_mustNotHaveNaN": false,
            "_queryable":      true,
            "_ontology": {
                "_node": "schema:dateCreated",
                "_name": "dateCreated"
            },
            "_documentation": "UTC timestamp of document creation in ISO 8601 format.",
            "_constraints":   {}
        }
    ]
}
```

### `schemas/V_gamma/probe_location.json`

```json
{
    "_classname":     "probe_location",
    "_class_version": "2.0.0",
    "_superclasses": [
        { "_classname": "base", "_schema": "$NDISCHEMAPATH/base.json" }
    ],
    "_depends_on": [
        {
            "_name":           "probe_id",
            "_mustBeNonEmpty": true,
            "_documentation":  "The unique ID of the probe document this location is associated with.",
            "_must_refer_to_document_class": ""
        }
    ],
    "_file":   [],
    "_fields": [
        {
            "_name":           "location",
            "type":            "ontology_term",
            "_blank_value":    null,
            "_default_value":  null,
            "_mustBeNonEmpty": false,
            "_mustBeScalar":   true,
            "_mustNotHaveNaN": false,
            "_queryable":      true,
            "_ontology": {
                "_node": "iao:0000219",
                "_name": "denotes"
            },
            "_documentation": "Anatomical or functional location of the probe, as an ontology term (e.g., 'uberon:0002436' / 'primary visual cortex').",
            "_constraints":   {}
        }
    ]
}
```

### Example `duration` field (hypothetical `treatment_duration` on `treatment`)

```json
{
    "_name":           "treatment_duration",
    "type":            "duration",
    "_blank_value":    null,
    "_default_value":  null,
    "_mustBeNonEmpty": false,
    "_mustBeScalar":   true,
    "_mustNotHaveNaN": true,
    "_queryable":      true,
    "_ontology":       null,
    "_documentation":  "How long the treatment was administered.",
    "_constraints": {
        "minimum_seconds": 0,
        "allowed_units":   ["second", "minute", "hour", "day", "week"]
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
    "_name":           "injection_volume",
    "type":            "volume",
    "_blank_value":    null,
    "_default_value":  null,
    "_mustBeNonEmpty": false,
    "_mustBeScalar":   true,
    "_mustNotHaveNaN": true,
    "_queryable":      true,
    "_ontology":       null,
    "_documentation":  "Volume of virus solution injected.",
    "_constraints": {
        "minimum_liters": 0,
        "allowed_units":  ["nanoliter", "microliter", "milliliter"]
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
name and dimension-specific `allowed_units` / `minimum_<canonical>` /
`maximum_<canonical>` keys.

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
  references are consistent, classnames are unique.
- **`test_documents.py`** — Validates document fixtures against their
  schemas using a lightweight Python validator.

### Running

```bash
pip install pytest jsonschema
pytest
```

---

## Key Design Decisions

1. **`_blank_value` and `_default_value` are always both present** in
   every field definition.
2. **All three validation flags are always present** on every field.
3. **`_fields` is the universal key** for property lists.
4. **Validation is a pull action, not a push action.**
5. **Superclass fields are inherited by flattening.**
6. **`_ontology` is required on every field, but may be `null`.**
   `_ontology` annotates what the field *means* (the concept the field
   represents); it is not a place to store an ontology-rooted value.
   Ontology-rooted values go in a field of type `ontology_term`.
7. **Validation has two phases.** Phase 1 (schema-level) and Phase 2
   (database-level).
8. **Language-specific tooling lives elsewhere.**
9. **Custom property names are prefixed with `_`.**
10. **`_constraints` accepts standard JSON Schema validation keywords**
    for primitive types, and named composite-specific keys for
    composites (`minimum_<canonical>` / `maximum_<canonical>` /
    `allowed_units` for each SI-dimensioned type,
    `allowed_namespaces` for `ontology_term`).
11. **Numbered dependencies use the `_name_#` pattern.**
12. **`_file` and `_directory` are optional top-level keys.**
13. **Directories are stored as separate documents, not inline metadata.**
14. **`open_binary_file` on a directory document resolves filenames from
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
19. **`_ontology` annotations use CURIE form.** The V_gamma shape
    `{_node, _name}` replaces V_beta's four-key
    `{_namespace, _term, _name, _uri}`. The `_uri` is derived from the
    registry.
20. **Schema-file-syntax changes do not bump `_class_version`.**
    Transforming `_ontology` annotation shape does not invalidate
    existing documents; only document-level changes bump the class
    version.
