# V_beta_SPEC.md — DID/NDI Document Schema Format (V_beta)

## Purpose

This document is a complete specification for the **V_beta** schema set in the
`did-schema` repository. V_beta inherits the V_alpha flat directory layout
(one JSON file per document type at the top of `schemas/V_beta/`) and adds
**snake_case naming requirements** for classnames, field names, and filenames.
See the "Naming Convention" section below and — for every rule that V_beta
shares with V_alpha — `schemas/V_alpha_SPEC.md`.

The specification is language-agnostic — language-specific tooling (MATLAB,
Python, etc.) lives in separate repositories and consumes these schemas as a
dependency.

---

## Repository Overview

**Repo name:** `did-schema`

**Language:** JSON (schema definitions), Python (test tooling only).

**Purpose:** Define and validate the JSON schema format used by DID (data-interface
database) documents and NDI (neuroscience data interface) documents. This repo is
not NDI itself — it is the schema layer that NDI and DID both depend on.

**What this repo does:**
- Defines the canonical JSON format for schema files that describe DID/NDI document types.
- Provides a meta-schema (a schema for schema files themselves) that validates schema files before they are used.
- Ships one JSON file per document type under `schemas/V_beta/` using a flat layout.
- Ships Python-based unit tests that validate all schemas and document fixtures.

**What this repo does NOT do:**
- Provide runtime tooling for loading, parsing, or manipulating documents. That belongs in language-specific repos (e.g., `DID-matlab`, `DID-python`).

---

## Repo File Structure

```
did-schema/
│
├── README.md
├── pyproject.toml                      ← Python test dependencies
│
├── schemas/
│   ├── V_beta_SPEC.md                  ← (this file) V_beta specification
│   ├── V_beta_notes.md                 ← V_beta status and V_alpha→V_beta renames
│   └── V_beta/                         ← flat directory of V_beta schemas
│       ├── did_schema_meta.json        ← meta-schema: validates schema files
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
        ├── invalid_base_document_bad_datestamp.json
        ├── valid_probe_location_document.json
        └── invalid_schema_missing_classname.json
```

### Schema directory layout

Each document type is a **single JSON file** at the top of `schemas/V_beta/`,
named `<classname>.json`. The filename stem must equal the document's
`_classname` value, and because classnames must be snake_case (see below) the
filename is also snake_case. There is exactly one schema file per document
type; subdirectories and per-type directories are not used.

The meta-schema (`did_schema_meta.json`) lives alongside the document-type
schemas in `schemas/V_beta/`.

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
keyword, but the enum values it accepts (`char`, `did_uid`, `matrix`, etc.) are
NDI-specific. The key itself is kept without prefix because it is standard; the
allowed values are documented below.

### V_beta snake_case requirements

V_beta tightens V_alpha's naming rules: every identifier introduced by the
schema author must be snake_case. Specifically:

- **Classnames.** The value of `_classname` (at the top level and inside each
  `_superclasses` entry) must match `^[a-z][a-z0-9_]*$` — lowercase letters,
  digits, and underscores, starting with a letter. No uppercase letters, no
  camelCase, no PascalCase.
- **Field names.** The value of `_name` on every field definition object
  (inside `_fields`, at any nesting depth, including nested `structure`
  subfields) must match `^[a-z][a-z0-9_]*$`, with no more than two consecutive
  underscores.
- **Dependency names.** The value of `_name` on every `_depends_on` entry must
  match `^[a-z][a-z0-9_]*(_#)?$` — the optional trailing `_#` is the numeric
  placeholder described in "Numbered Dependencies" below.
- **Directory record names.** The value of `_name` on every `_directory` entry
  must match `^[a-z][a-z0-9_]*$`.
- **File record names.** The value of `_name` on every `_file` entry should
  be snake_case where it is an identifier. When the `_name` is a literal
  filename (e.g. `"level1.bin"`), the stem before the extension must be
  snake_case; the extension is preserved.
- **Filenames.** Each schema file is named `<classname>.json`; since the
  classname is snake_case, the filename stem is likewise snake_case.

Keys that are either standard JSON Schema keywords or underscore-prefixed
structural keys (`_classname`, `_class_version`, `_mustBeNonEmpty`, etc.) are
fixed by this specification and are **not** subject to the snake_case rule
above — they are literal keys defined by the spec, not user-chosen names.

The meta-schema for V_beta enforces the classname and field-name patterns
directly.

---

## JSON Format: Schema Files

Every schema file must conform to the following structure exactly. The meta-schema
enforces this.

### Top-Level Keys

| Key               | Type   | Required | May be empty? | Description |
|-------------------|--------|----------|---------------|-------------|
| `_classname`      | string | yes      | no            | Unique name of the document type. Must match `^[a-z][a-z0-9_]*$` (snake_case, see Naming Convention). |
| `_class_version`  | string | yes      | no            | Semantic version string `"MAJOR.MINOR.PATCH"`. |
| `_maturity_level` | string | yes      | no            | `"work_in_progress"` or `"mature"`. |
| `_superclasses`   | array  | yes      | yes (`[]`)    | Array of superclass reference objects (see below). |
| `_depends_on`     | array  | yes      | yes (`[]`)    | Array of dependency objects (see below). |
| `_file`           | array  | no       | yes (`[]`)    | Array of file record objects (see below). Omit for document types with no associated files. |
| `_directory`      | array  | no       | yes (`[]`)    | Array of directory record objects (see below). Omit for document types with no associated directories. |
| `_fields`         | array  | yes      | yes (`[]`)    | Array of field definition objects (see below). |

No other top-level keys are permitted. The validator must reject schema files with
unrecognized top-level keys.

### Superclass Reference Object

```json
{ "_classname": "base", "_schema": "$NDISCHEMAPATH/base.json" }
```

| Key          | Type   | Required | Description |
|--------------|--------|----------|-------------|
| `_classname` | string | yes      | Name of the parent class. |
| `_schema`    | string | yes      | Path or token-substituted path to the parent schema file. Under the flat V_beta layout this is `$NDISCHEMAPATH/<parent_classname>.json`. |

### Dependency Object

```json
{
    "_name":           "probe_id",
    "_mustBeNonEmpty": true,
    "_documentation":  "The unique ID of the probe this location is associated with."
}
```

| Key               | Type    | Required | Description |
|-------------------|---------|----------|-------------|
| `_name`           | string  | yes      | Role name of the dependency (see Numbered Dependencies below). |
| `_mustBeNonEmpty` | boolean | yes      | Whether the dependency value must be non-empty at validation time. |
| `_multiple`       | boolean | no       | If true, this dependency may repeat at runtime with numbered names (see Numbered Dependencies). Omit or set to `false` for exactly-one dependencies. |
| `_documentation`  | string  | yes      | Human-readable description. |

In a document instance, each dependency has a `_name` and a `value`. The `value` must be
the `id` (DID UID) of another document in the database, or of a document queued for
insertion in the same transaction. This referential constraint cannot be checked by
schema-level validation alone — see **Validation Phases** below.

#### Numbered Dependencies (`_name_#` pattern)

Some document types may reference an arbitrary number of instances of a given
dependency (e.g., a sync graph referencing many sync rules). To express this, set
`_multiple: true` and use `#` as a numeric placeholder in `_name`:

```json
{
    "_name":           "syncrule_id_#",
    "_mustBeNonEmpty": true,
    "_multiple":       true,
    "_documentation":  "A sync rule participating in this graph. Instances are named syncrule_id_1, syncrule_id_2, etc."
}
```

At runtime, the actual dependency entries are named by substituting a positive integer
for `#`: `syncrule_id_1`, `syncrule_id_2`, and so on. There is no upper bound on the
count. When `_multiple` is `true`, zero instances is also valid (the dependency is
optional in aggregate).

### File Record Object

```json
{ "_name": "spike_waveforms", "_documentation": "Raw spike waveform binary data." }
```

| Key              | Type   | Required | Description |
|------------------|--------|----------|-------------|
| `_name`          | string | yes      | Identifier for this file record. |
| `_documentation` | string | yes      | Description of the file's contents. |

### Directory Record Object

```json
{ "_name": "raw_data", "_documentation": "Directory of raw acquisition files." }
```

| Key              | Type   | Required | Description |
|------------------|--------|----------|-------------|
| `_name`          | string | yes      | Identifier for this directory record. Must not collide with any `_file` record `_name` on the same schema. |
| `_documentation` | string | yes      | Description of the directory's contents. |

A `_directory` entry declares a named directory slot on a document type, analogous to
how `_file` declares a named file slot. Consumer tooling provides a `get_directory(name)`
method (parallel to `open_binary_file(name)`) to retrieve the directory object for a
given slot.

Each directory slot is backed by a `directory` document in the database (see
**Directory Document Type** below). The directory document depends on the owning
document via `parent_doc_id`, and stores the directory's file listing in a manifest
file — keeping the JSON metadata small regardless of how many files the directory
contains.

#### Directory Document Type

The `directory` document type (`schemas/V_beta/directory.json`) is the storage
backing for `_directory` slots. It extends `base` and has the following structure:

**Dependencies:**
- `parent_doc_id` (required) — the `id` of the root document that owns this directory.
  For subdirectories, this is still the root owning document, not the parent directory.
  This enables a single query (`isa directory AND depends_on parent_doc_id = X`) to
  retrieve the entire directory tree for a document.
- `parent_directory_id` (optional) — the `id` of the parent directory document. Empty
  for top-level directories (those filling a `_directory` slot). Non-empty for
  subdirectories nested within another directory.

**File:**
- `manifest_file` — a file listing the contents of this directory. The manifest is
  internal infrastructure and is not accessible via `open_binary_file`. Use
  `get_directory_manifest` instead.

**Fields:**
- `dirname` (char) — the actual directory name (e.g., `"raw_data/"`, `"metadata/"`).
- `directory_role` (char) — the `_name` of the `_directory` slot this directory fills
  on the parent document's schema. Non-empty for top-level directories, empty for
  subdirectories. This is how consumer tooling matches a directory document back to its
  schema slot when the user calls `get_directory("raw_data")`.
- `num_entries` (integer) — number of file entries in the manifest.
- `manifest_format` (char) — format of the manifest file (default: `"jsonlines"`).

#### Tree Structure

Directories form a tree via the `parent_directory_id` dependency:

```
experiment doc (id=A)
  _directory: ["raw_data", "analysis_output"]

  directory doc (id=B, parent_doc_id=A, parent_directory_id="",
                 dirname="raw_data/", directory_role="raw_data")
    manifest_file: [trial_001.tif, trial_002.tif, ...]

    directory doc (id=D, parent_doc_id=A, parent_directory_id=B,
                   dirname="metadata/", directory_role="")
      manifest_file: [params.json, config.yaml]

  directory doc (id=C, parent_doc_id=A, parent_directory_id="",
                 dirname="analysis_output/", directory_role="analysis_output")
    manifest_file: [results.csv, summary.pdf]
```

Useful queries:
- **All directories for document A:** `isa directory AND depends_on parent_doc_id = A`
- **Children of directory B:** `isa directory AND depends_on parent_directory_id = B`
- **Top-level directories for document A:** above query + `parent_directory_id is empty`

#### Manifest Format

The recommended manifest format is JSON Lines (`"jsonlines"`): one JSON object per
line, streamable, no need to parse the entire file into memory:

```jsonl
{"filename": "trial_001.tif", "size": 4096, "checksum_sha256": "ab3f..."}
{"filename": "trial_002.tif", "size": 4096, "checksum_sha256": "cd7e..."}
```

#### Consumer Tooling Methods

The following methods are the responsibility of consumer tooling (DID-python,
DID-matlab), not this schema repo:

- `get_directory(name)` — retrieve the directory object for a named `_directory` slot.
- `get_directory_manifest(directory_doc_id)` — read and parse the manifest file,
  returning a structured listing. This is the only way to access the manifest.
- `open_binary_file(doc_id, name)` — when `doc_id` is a directory document, `name` is
  resolved as a filename in the manifest (not a `_file` slot). The `manifest_file`
  `_file` slot is never accessible via `open_binary_file` on a directory document.

#### Subclassing for Constrained Directory Structures

To enforce specific directory layouts (e.g., BIDS, NWB), create a subclass of
`directory` that adds required fields, constraints, or specific `_depends_on`
entries. For example, a `bids_directory` subclass could require specific
subdirectory names or mandate a particular manifest format.

### Field Definition Object

Every entry in `"_fields"` (at any nesting depth) must have **all** of the following keys:

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
        "_namespace": "pato",
        "_term":      "0000044",
        "_name":      "frequency",
        "_uri":       "http://purl.obolibrary.org/obo/PATO_0000044"
    },
    "_documentation":  "Sampling rate in Hz.",
    "_constraints":    { "minimum": 0.0 }
}
```

| Key               | Type            | Required | Notes |
|-------------------|-----------------|----------|-------|
| `_name`           | string          | yes      | `^[a-z][a-z0-9_]*$` (snake_case), no more than two consecutive underscores. |
| `type`            | string          | yes      | One of the valid types (see Type System below). Standard JSON Schema keyword. |
| `_blank_value`    | any             | yes      | Value in a freshly constructed blank document. May fail validation. |
| `_default_value`  | any             | yes      | Legitimate fallback. Must pass validation. |
| `_mustBeNonEmpty` | boolean         | yes      | Value may not be null, `""`, `[]`, or `{}` at validation time. |
| `_mustBeScalar`   | boolean         | yes      | Value must be a single element (not array/matrix). Domain-specific; no JSON Schema equivalent. |
| `_mustNotHaveNaN` | boolean         | yes      | No NaN values permitted. For non-numeric types, must be `false`. Domain-specific; no JSON Schema equivalent. |
| `_queryable`      | boolean         | yes      | Whether this field is indexed in the database. |
| `_ontology`       | object or null  | yes      | Ontology node (see below), or `null`. |
| `_documentation`  | string          | yes      | Human-readable description. |
| `_constraints`    | object          | yes      | Standard JSON Schema validation keywords constraining this field's value (e.g., `minLength`, `minimum`, `maximum`, `pattern`, `enum`). Use `{}` for unconstrained. JSON Schema validators can apply these directly to field values. |

For `"type": "structure"` fields, an additional key is required:

| Key       | Type  | Required            | Notes |
|-----------|-------|---------------------|-------|
| `_fields` | array | yes (for structure) | Nested field definition objects. Same format, recursive. |

### Ontology Object

```json
{
    "_namespace": "uberon",
    "_term":      "0002436",
    "_name":      "primary visual cortex",
    "_uri":       "http://purl.obolibrary.org/obo/UBERON_0002436"
}
```

| Key          | Type           | Required | Description |
|--------------|----------------|----------|-------------|
| `_namespace` | string         | yes      | Ontology name (e.g., `"uberon"`, `"schema"`, `"iao"`, `"pato"`). |
| `_term`      | string         | yes      | Term identifier within the namespace. |
| `_name`      | string         | yes      | Human-readable name or label of the ontology term (e.g., `"centrally registered identifier"`). |
| `_uri`       | string or null | yes      | Full resolvable URI, or `null` if unavailable. |

Setting the entire `"_ontology"` value to `null` is valid.

### Useful Ontology Terms

The following ontology terms are relevant to DID/NDI schemas and may be used in
`_ontology` annotations on fields:

| Namespace       | Term    | Label                           | URI | Notes |
|-----------------|---------|----------------------------------|-----|-------|
| iao             | 0000578 | centrally registered identifier | http://purl.obolibrary.org/obo/IAO_0000578 | Used for `id` fields |
| NCI Thesaurus   | C169028 | Study Unique Identifier         | https://ncit.nci.nih.gov/ncitbrowser/ConceptReport.jsp?dictionary=NCI_Thesaurus&code=C169028 | Useful for `id` / `session_id` style fields |
| NCI             | C67447  | Session                         | https://ncit.nci.nih.gov/ncitbrowser/ConceptReport.jsp?dictionary=NCI_Thesaurus&code=C67447 | "Time, period, or term devoted to some activity." |

---

## JSON Format: Type System

### Valid Types

| Type        | Description                                     | `_constraints` keys                                   | Notes |
|-------------|-------------------------------------------------|------------------------------------------------------|-------|
| `did_uid`   | NDI/DID unique identifier string                | `{}` (none)                                          | |
| `char`      | Character array / string                        | `{ "maxLength": integer or null }`                   | `"string"` is accepted as an alias |
| `integer`   | Single integer value                            | `{ "minimum": integer or null, "maximum": integer or null }` | |
| `double`    | Single double-precision float                   | `{ "minimum": number or null, "maximum": number or null }`   | |
| `matrix`    | 2D array of doubles                             | `{ "rows": int or null, "cols": int or null, "minimum": number or null, "maximum": number or null }` | `_mustBeScalar` should be `false` |
| `timestamp` | ISO 8601 UTC timestamp string                   | `{}` (none)                                          | Validator checks format |
| `boolean`   | true/false                                      | `{}` (none)                                          | |
| `structure` | Nested sub-document (JSON object)               | `{}` (none); use `"_fields"` key for nested fields   | Recursive |

#### Semantics of validation flags by type

| Type        | `_mustBeNonEmpty` applies? | `_mustBeScalar` applies? | `_mustNotHaveNaN` applies? |
|-------------|---------------------------|--------------------------|---------------------------|
| `did_uid`   | yes (non-empty string)    | yes                      | no — must be `false`      |
| `char`      | yes (non-empty string)    | yes                      | no — must be `false`      |
| `integer`   | yes                       | yes                      | yes                       |
| `double`    | yes                       | yes                      | yes                       |
| `matrix`    | yes (non-empty array)     | no — should be `false`   | yes (element-wise)        |
| `timestamp` | yes (non-empty string)    | yes                      | no — must be `false`      |
| `boolean`   | yes                       | yes (implicitly)         | no — must be `false`      |
| `structure` | yes (non-empty object)    | yes                      | no — must be `false`      |

---

## JSON Format: `_blank_value` vs. `_default_value`

These are intentionally and importantly different:

- **`_blank_value`**: The value a field holds in a document that was just constructed from
  the definition file, before the user has provided any data. This value is *allowed to
  fail validation*. Common blank values: `null`, `""`, `[]`, `{}`, `0`. The blank document
  is useful for display, templating, and as a starting point for editing.

- **`_default_value`**: A value that *must pass validation* and is used as a fallback during
  programmatic document construction when the caller does not supply a value. Think of it
  as the "reasonable default" for automated pipelines.

The validator must:
1. Accept `_blank_value` without complaint (it is never validated).
2. Validate `_default_value` against the field's type and constraints when the schema is
   loaded, and emit a warning if `_default_value` does not itself pass validation (this
   catches schema authoring errors).

---

## JSON Format: Versioning Rules

`_class_version` uses semantic versioning: `"MAJOR.MINOR.PATCH"`.

| Part    | Increment when... | Effect on existing documents |
|---------|-------------------|------------------------------|
| MAJOR   | A field is removed, renamed, or changes type; a `_mustBeNonEmpty` is added to a previously optional field; a new required dependency is added; a superclass is added or removed | Existing documents **may fail** validation against the new schema. Migration required. |
| MINOR   | A new optional field is added; an ontology annotation is added or corrected; a constraint is relaxed; documentation is substantially improved | Existing documents still **pass** validation. New fields can be populated on re-save. |
| PATCH   | Documentation text is corrected; `_default_value` is changed; formatting cleanup with no behavioural change | No change to validation behaviour. |

The validator must be able to compare two semver strings and determine if a document's
declared version is compatible with the current schema version (same MAJOR, any MINOR/PATCH).

---

## Validation Phases

Document validation is split into two phases. Phase 1 requires only the document and its
schema. Phase 2 requires access to the database (or a batch of documents being inserted
together). Both phases are the responsibility of consumer tooling — this repo defines the
rules; consumer tooling enforces them.

### Phase 1 — Schema-level validation (single document)

Checks that can be performed with only the document and its schema file(s):

- All fields declared in the schema (including inherited superclass fields) are present.
- `_mustBeNonEmpty` fields are not `null`, `""`, `[]`, or `{}`.
- `_mustBeScalar` fields are single values, not arrays.
- `_mustNotHaveNaN` fields contain no NaN values.
- Type-specific format checks (e.g., `timestamp` matches ISO 8601 UTC, `did_uid` matches
  the UID pattern).
- Type-specific constraint checks using standard JSON Schema keywords in `_constraints`
  (e.g., `minimum`/`maximum` for numeric types, `maxLength` for strings).
- `_depends_on` entries with `_mustBeNonEmpty: true` have non-empty values.
- `_class_version` compatibility (same MAJOR version as the schema).
- `_directory` and `_file` record names are unique across both arrays (no collisions).

Phase 1 is fully specified by this repo and tested in the test suite.

### Phase 2 — Database-level validation (cross-document)

Checks that require access to the database or a transaction context:

- **Referential integrity of `_depends_on`**: each dependency `value` must be the `id` of
  an existing document in the database, or of a document queued for insertion in the same
  transaction. The referenced document must exist and be of an appropriate type.
- **Uniqueness of `id`**: the document's `id` field must not collide with any existing
  document in the database.
- **Any other cross-document invariants** defined by the application layer.

Phase 2 is specified here but enforced by consumer tooling (e.g., the database insert
path in `DID-matlab` or `DID-python`). This repo does not test Phase 2 because it has
no database.

---

## The Meta-Schema

`schemas/V_beta/did_schema_meta.json` is a JSON Schema Draft 7 file (standard JSON
Schema, not NDI format) that validates any NDI schema file. This lets you use any standard JSON
Schema validator (e.g., Python `jsonschema`) to check that an NDI schema file is
well-formed before loading it.

The meta-schema must enforce:
- Required top-level keys are present: `_classname`, `_class_version`, `_maturity_level`, `_superclasses`, `_depends_on`, `_fields`.
- Optional top-level keys, if present, have correct structure: `_file`, `_directory`.
- `_classname` matches `^[a-z][a-z0-9_]*$` (snake_case).
- Every `_name` on a field, dependency, or record matches the appropriate snake_case pattern (see "V_beta snake_case requirements" above).
- `_class_version` matches `^\d+\.\d+\.\d+$`.
- `_maturity_level` is `"work_in_progress"` or `"mature"`.
- `_superclasses` is an array of objects each with `_classname` (string) and `_schema` (string).
- `_depends_on` is an array of dependency objects.
- `_file` (if present) is an array of file record objects.
- `_directory` (if present) is an array of directory record objects.
- `_fields` is an array of field definition objects.
- Each field definition object has all required keys with correct types.
- `type` is one of the valid type strings.
- `_ontology` is either `null` or an object with `_namespace`, `_term`, `_uri`.
- `_mustBeNonEmpty`, `_mustBeScalar`, `_mustNotHaveNaN`, `_queryable` are all booleans.
- For `type: "structure"`, the `_fields` key is present.

---

## Example Schema Files

### `schemas/V_beta/base.json`

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
                "_namespace": "iao",
                "_term":      "0000578",
                "_name":      "centrally registered identifier",
                "_uri":       "http://purl.obolibrary.org/obo/IAO_0000578"
            },
            "_documentation":  "Unique identifier for this document instance.",
            "_constraints":    {}
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
                "_namespace": "schema",
                "_term":      "name",
                "_name":      "name",
                "_uri":       "https://schema.org/name"
            },
            "_documentation":  "Human-readable name for this document.",
            "_constraints":    { "maxLength": 256 }
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
                "_namespace": "schema",
                "_term":      "dateCreated",
                "_name":      "dateCreated",
                "_uri":       "https://schema.org/dateCreated"
            },
            "_documentation":  "UTC timestamp of document creation in ISO 8601 format.",
            "_constraints":    {}
        }
    ]
}
```

### `schemas/V_beta/probe_location.json`

```json
{
    "_classname":     "probe_location",
    "_class_version": "1.0.0",
    "_superclasses": [
        { "_classname": "base", "_schema": "$NDISCHEMAPATH/base.json" }
    ],
    "_depends_on": [
        {
            "_name":           "probe_id",
            "_mustBeNonEmpty": true,
            "_documentation":  "The unique ID of the probe document this location is associated with."
        }
    ],
    "_file":   [],
    "_fields": [
        {
            "_name":           "ontology_name",
            "type":            "char",
            "_blank_value":    "",
            "_default_value":  "",
            "_mustBeNonEmpty": false,
            "_mustBeScalar":   true,
            "_mustNotHaveNaN": false,
            "_queryable":      true,
            "_ontology": {
                "_namespace": "iao",
                "_term":      "0000219",
                "_name":      "denotes",
                "_uri":       "http://purl.obolibrary.org/obo/IAO_0000219"
            },
            "_documentation":  "Formal ontology identifier for the probe location (e.g., 'uberon:0002436').",
            "_constraints":    { "maxLength": 256 }
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
                "_namespace": "schema",
                "_term":      "name",
                "_name":      "name",
                "_uri":       "https://schema.org/name"
            },
            "_documentation":  "Human-readable name or label of the probe location as used by the ontology referenced in ontology_name (e.g., 'primary visual cortex').",
            "_constraints":    { "maxLength": 256 }
        }
    ]
}
```

---

## Test Tooling (Python)

The test suite uses Python with `pytest` and `jsonschema`. These tests validate the
schema files themselves — they do not provide runtime document tooling.

### Test categories

- **`test_meta_schema.py`** — Validates all schema files against `did_schema_meta.json`
  using JSON Schema Draft 7. Tests that valid schemas pass and invalid schemas fail with
  expected errors.

- **`test_schemas.py`** — Structural tests: field names match naming patterns, types are
  valid, required keys are present, superclass references are consistent, classnames are
  unique across the repo.

- **`test_documents.py`** — Validates document fixtures against their schemas using a
  lightweight Python validator. Tests that valid documents pass and invalid documents
  fail with the expected error fields (e.g., missing `id`, bad `datestamp` format).

### Running

```bash
pip install pytest jsonschema
pytest
```

---

## Key Design Decisions (for reference)

1. **`_blank_value` and `_default_value` are always both present** in every field definition. Neither is optional. This is enforced by the meta-schema.

2. **All three validation flags are always present** on every field (`_mustBeNonEmpty`, `_mustBeScalar`, `_mustNotHaveNaN`). For types where a flag is meaningless (e.g., `_mustNotHaveNaN` on a `char`), the flag must still be present and must be `false`. The meta-schema enforces this.

3. **`"_fields"` is the universal key** for property lists, not a per-class key. The old format used a class-named key (e.g., `"base": [...]`, `"probe_location": [...]`). The new format always uses `"_fields": [...]`. The classname is already in `_classname`; there is no need to repeat it as a key.

4. **Validation is a pull action, not a push action.** A document does not validate itself on construction. Validation is triggered explicitly by calling the appropriate method in the consumer tooling, or by the database layer before insert.

5. **Superclass fields are inherited by flattening.** `all_fields` is a flat array combining fields from the schema and all its ancestors, in superclass-first order (base fields first). Duplicate field names are not permitted; the meta-validator checks for this across the inheritance chain.

6. **`_ontology` is required on every field, but may be `null`.** Requiring the key (even if null) makes it clear that the schema author considered ontology annotation and made a deliberate choice. A missing `_ontology` key is a meta-schema validation error.

7. **Validation has two phases.** Phase 1 (schema-level) checks a single document against its schema — types, constraints, non-empty rules, format patterns. Phase 2 (database-level) checks cross-document invariants — referential integrity of `_depends_on` values, uniqueness of `id`. This repo specifies both phases but only tests Phase 1. Phase 2 enforcement belongs in consumer tooling.

8. **Language-specific tooling lives elsewhere.** This repo holds only schema definitions and test validation. Runtime classes for loading, parsing, manipulating documents, and generating blank document templates belong in language-specific repos (e.g., `DID-matlab`, `DID-python`).

9. **Custom property names are prefixed with `_`.** Any property name introduced by this schema system — one that is not a standard JSON Schema keyword — is prefixed with an underscore. Standard JSON Schema keywords (`type`, `$schema`, `$id`, `$ref`, `$defs`, `properties`, `required`, `items`, `enum`, `const`, `pattern`, etc.) are used as-is. The one deliberate exception is `type`, whose key is standard but whose allowed values (`char`, `did_uid`, `matrix`, etc.) are NDI-specific. This convention makes it unambiguous to readers and tooling whether any given property is part of the JSON Schema vocabulary or an NDI extension.

10. **`_constraints` accepts standard JSON Schema validation keywords.** Rather than inventing custom constraint names, the `_constraints` object on each field definition holds standard JSON Schema keywords (`minLength`, `maxLength`, `minimum`, `maximum`, `pattern`, `enum`, etc.). A standard JSON Schema validator can apply these directly to field values without custom tooling.

11. **Numbered dependencies use the `_name_#` pattern.** When a document type may reference an arbitrary number of instances of the same dependency kind, the dependency entry in `_depends_on` uses `#` as a placeholder for a positive integer in `_name` (e.g., `"syncrule_id_#"`), and sets `_multiple: true`. At runtime, actual entries are named `syncrule_id_1`, `syncrule_id_2`, etc. This avoids enumerating a fixed maximum in the schema while still giving each runtime entry a unique, queryable name.

12. **`_file` and `_directory` are optional top-level keys.** Not all document types have associated files or directories. Schemas that do not need them simply omit the key. This avoids forcing every schema to declare `"_file": []` or `"_directory": []`.

13. **Directories are stored as separate documents, not inline metadata.** A directory's file listing is stored in a manifest file attached to a `directory` document, not in the JSON metadata of the parent document. This keeps document metadata small regardless of directory size (even for directories with hundreds of thousands of files). The directory tree structure is expressed through `_depends_on` references (`parent_doc_id` and `parent_directory_id`), enabling efficient tree queries.

14. **`open_binary_file` on a directory document resolves filenames from the manifest.** When called on a directory document, `open_binary_file(doc_id, name)` resolves `name` against the manifest entries, not `_file` slots. The `manifest_file` `_file` slot is internal infrastructure and is never accessible via `open_binary_file`; use `get_directory_manifest` instead.
