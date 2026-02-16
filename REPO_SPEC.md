# REPO_SPEC.md — did-schema: DID/NDI Document Schema Format

## Purpose

This document is a complete specification for a new repository called `did-schema`.
Implement everything described here. Where implementation details are left to judgment,
prefer simplicity and clarity over cleverness. Prefer flat file structures. Prefer
readable code over terse code. Leave TODO comments where behaviour is intentionally
deferred.

---

## Repository Overview

**Repo name:** `did-schema`

**Language:** MATLAB (primary), with JSON as the schema/document file format.

**Purpose:** Define and validate the JSON schema format used by DID (data-interface
database) documents and NDI (neuroscience data interface) documents. This repo is
not NDI itself — it is the schema layer that NDI and DID both depend on.

**What this repo does:**
- Defines the canonical JSON format for schema files that describe DID/NDI document types.
- Provides a MATLAB class `did.schema.Schema` that loads, parses, and validates schema files.
- Provides a MATLAB class `did.schema.Document` that loads document instances and validates them against their schema.
- Provides a meta-schema (a schema for schema files themselves) that validates schema files before they are used.
- Ships example schema files for `base` and `probe_location` document types.
- Ships unit tests for all of the above.

---

## Repo File Structure

Create the following files and directories. Details for each are given in subsequent sections.

```
did-schema/
│
├── README.md
├── REPO_SPEC.md                        ← (this file, copy it in)
│
├── schemas/
│   ├── meta/
│   │   └── did_schema_meta.json        ← meta-schema: validates schema files
│   ├── base_schema.json                ← schema for the base document type
│   └── probe/
│       └── probe_location_schema.json  ← schema for probe_location document type
│
├── definitions/
│   ├── base.json                       ← blank document definition for base
│   └── probe/
│       └── probe_location.json         ← blank document definition for probe_location
│
├── +did/
│   └── +schema/
│       ├── Schema.m                    ← class: loads + validates a schema file
│       ├── Document.m                  ← class: loads + validates a document instance
│       ├── Validator.m                 ← class: runs validation logic
│       ├── MetaValidator.m             ← class: validates schema files against meta-schema
│       └── util/
│           ├── loadJSON.m              ← helper: read a JSON file into a MATLAB struct
│           ├── semver.m                ← helper: parse and compare semver strings
│           └── resolveSchemaPath.m     ← helper: resolve $NDISCHEMAPATH / $NDIDOCUMENTPATH tokens
│
└── tests/
    ├── test_Schema.m                   ← unit tests for Schema class
    ├── test_Document.m                 ← unit tests for Document class
    ├── test_Validator.m                ← unit tests for Validator class
    ├── test_MetaValidator.m            ← unit tests for MetaValidator class
    ├── test_semver.m                   ← unit tests for semver helper
    └── fixtures/
        ├── valid_base_document.json
        ├── invalid_base_document_missing_id.json
        ├── invalid_base_document_bad_datestamp.json
        ├── valid_probe_location_document.json
        └── invalid_schema_missing_classname.json
```

---

## JSON Format: Schema Files

Every schema file must conform to the following structure exactly. The meta-schema
enforces this.

### Top-Level Keys (all required)

| Key             | Type   | May be empty? | Description |
|-----------------|--------|---------------|-------------|
| `classname`     | string | no            | Unique name of the document type. Must match `^[a-zA-Z][a-zA-Z0-9_]*$`. |
| `class_version` | string | no            | Semantic version string `"MAJOR.MINOR.PATCH"`. |
| `superclasses`  | array  | yes (`[]`)    | Array of superclass reference objects (see below). |
| `depends_on`    | array  | yes (`[]`)    | Array of dependency objects (see below). |
| `file`          | array  | yes (`[]`)    | Array of file record objects (see below). |
| `fields`        | array  | yes (`[]`)    | Array of field definition objects (see below). |

No other top-level keys are permitted. The validator must reject schema files with
unrecognized top-level keys.

### Superclass Reference Object

```json
{ "classname": "base", "schema": "$NDISCHEMAPATH/base_schema.json" }
```

| Key         | Type   | Required | Description |
|-------------|--------|----------|-------------|
| `classname` | string | yes      | Name of the parent class. |
| `schema`    | string | yes      | Path or token-substituted path to the parent schema file. |

### Dependency Object

```json
{
    "name":           "probe_id",
    "mustBeNonEmpty": true,
    "documentation":  "The unique ID of the probe this location is associated with."
}
```

| Key              | Type    | Required | Description |
|------------------|---------|----------|-------------|
| `name`           | string  | yes      | Role name of the dependency. |
| `mustBeNonEmpty` | boolean | yes      | Whether the dependency value must be non-empty at validation time. |
| `documentation`  | string  | yes      | Human-readable description. |

### File Record Object

```json
{ "name": "spike_waveforms", "documentation": "Raw spike waveform binary data." }
```

| Key             | Type   | Required | Description |
|-----------------|--------|----------|-------------|
| `name`          | string | yes      | Identifier for this file record. |
| `documentation` | string | yes      | Description of the file's contents. |

### Field Definition Object

Every entry in `"fields"` (at any nesting depth) must have **all** of the following keys:

```json
{
    "name":           "sample_rate",
    "type":           "double",
    "blank_value":    null,
    "default_value":  30000.0,
    "mustBeNonEmpty": true,
    "mustBeScalar":   true,
    "mustNotHaveNaN": true,
    "queryable":      true,
    "ontology": {
        "namespace": "pato",
        "term":      "0000044",
        "uri":       "http://purl.obolibrary.org/obo/PATO_0000044"
    },
    "documentation":  "Sampling rate in Hz.",
    "constraints":    { "min": 0.0, "max": null }
}
```

| Key              | Type            | Required | Notes |
|------------------|-----------------|----------|-------|
| `name`           | string          | yes      | `^[a-zA-Z][a-zA-Z0-9_]*$`, no more than two consecutive underscores. |
| `type`           | string          | yes      | One of the valid types (see Type System below). |
| `blank_value`    | any             | yes      | Value in a freshly constructed blank document. May fail validation. |
| `default_value`  | any             | yes      | Legitimate fallback. Must pass validation. |
| `mustBeNonEmpty` | boolean         | yes      | Value may not be null, `""`, `[]`, or `{}` at validation time. |
| `mustBeScalar`   | boolean         | yes      | Value must be a single element (not array/matrix). |
| `mustNotHaveNaN` | boolean         | yes      | No NaN values permitted. For non-numeric types, must be `false`. |
| `queryable`      | boolean         | yes      | Whether this field is indexed in the database. |
| `ontology`       | object or null  | yes      | Ontology node (see below), or `null`. |
| `documentation`  | string          | yes      | Human-readable description. |
| `constraints`    | object          | yes      | Type-specific constraints (see Type System). Use `{}` for unconstrained. |

For `"type": "structure"` fields, an additional key is required:

| Key     | Type  | Required           | Notes |
|---------|-------|--------------------|-------|
| `fields`| array | yes (for structure) | Nested field definition objects. Same format, recursive. |

### Ontology Object

```json
{
    "namespace": "uberon",
    "term":      "0002436",
    "uri":       "http://purl.obolibrary.org/obo/UBERON_0002436"
}
```

| Key         | Type           | Required | Description |
|-------------|----------------|----------|-------------|
| `namespace` | string         | yes      | Ontology name (e.g., `"uberon"`, `"schema"`, `"iao"`, `"pato"`). |
| `term`      | string         | yes      | Term identifier within the namespace. |
| `uri`       | string or null | yes      | Full resolvable URI, or `null` if unavailable. |

Setting the entire `"ontology"` value to `null` is valid.

---

## JSON Format: Type System

### Valid Types

| Type        | Description                                     | `constraints` keys                                   | Notes |
|-------------|-------------------------------------------------|------------------------------------------------------|-------|
| `did_uid`   | NDI/DID unique identifier string                | `{}` (none)                                          | |
| `char`      | Character array / string                        | `{ "max_length": integer or null }`                  | `"string"` is accepted as an alias |
| `integer`   | Single integer value                            | `{ "min": integer or null, "max": integer or null }` | |
| `double`    | Single double-precision float                   | `{ "min": number or null, "max": number or null }`   | |
| `matrix`    | 2D array of doubles                             | `{ "rows": int or null, "cols": int or null, "min": number or null, "max": number or null }` | `mustBeScalar` should be `false` |
| `timestamp` | ISO 8601 UTC timestamp string                   | `{}` (none)                                          | Validator checks format |
| `boolean`   | true/false                                      | `{}` (none)                                          | |
| `structure` | Nested sub-document (JSON object)               | `{}` (none); use `"fields"` key for nested fields    | Recursive |

#### Semantics of validation flags by type

| Type        | `mustBeNonEmpty` applies? | `mustBeScalar` applies? | `mustNotHaveNaN` applies? |
|-------------|--------------------------|------------------------|--------------------------|
| `did_uid`   | yes (non-empty string)   | yes                    | no — must be `false`      |
| `char`      | yes (non-empty string)   | yes                    | no — must be `false`      |
| `integer`   | yes                      | yes                    | yes                       |
| `double`    | yes                      | yes                    | yes                       |
| `matrix`    | yes (non-empty array)    | no — should be `false` | yes (element-wise)        |
| `timestamp` | yes (non-empty string)   | yes                    | no — must be `false`      |
| `boolean`   | yes                      | yes (implicitly)       | no — must be `false`      |
| `structure` | yes (non-empty object)   | yes                    | no — must be `false`      |

---

## JSON Format: blank_value vs. default_value

These are intentionally and importantly different:

- **`blank_value`**: The value a field holds in a document that was just constructed from
  the definition file, before the user has provided any data. This value is *allowed to
  fail validation*. Common blank values: `null`, `""`, `[]`, `{}`, `0`. The blank document
  is useful for display, templating, and as a starting point for editing.

- **`default_value`**: A value that *must pass validation* and is used as a fallback during
  programmatic document construction when the caller does not supply a value. Think of it
  as the "reasonable default" for automated pipelines.

The validator must:
1. Accept `blank_value` without complaint (it is never validated).
2. Validate `default_value` against the field's type and constraints when the schema is
   loaded, and emit a warning if `default_value` does not itself pass validation (this
   catches schema authoring errors).

---

## JSON Format: Versioning Rules

`class_version` uses semantic versioning: `"MAJOR.MINOR.PATCH"`.

| Part    | Increment when... | Effect on existing documents |
|---------|-------------------|------------------------------|
| MAJOR   | A field is removed, renamed, or changes type; a `mustBeNonEmpty` is added to a previously optional field; a new required dependency is added; a superclass is added or removed | Existing documents **may fail** validation against the new schema. Migration required. |
| MINOR   | A new optional field is added; an ontology annotation is added or corrected; a constraint is relaxed; documentation is substantially improved | Existing documents still **pass** validation. New fields can be populated on re-save. |
| PATCH   | Documentation text is corrected; `default_value` is changed; formatting cleanup with no behavioural change | No change to validation behaviour. |

The validator must be able to compare two semver strings and determine if a document's
declared version is compatible with the current schema version (same MAJOR, any MINOR/PATCH).

---

## The Meta-Schema

`schemas/meta/did_schema_meta.json` is a JSON Schema Draft 7 file (standard JSON Schema,
not NDI format) that validates any NDI schema file. This lets you use any standard JSON
Schema validator (e.g., the MATLAB `jsonschema` toolbox, or Python `jsonschema`) to
check that an NDI schema file is well-formed before loading it.

The meta-schema must enforce:
- All six top-level keys are present.
- `classname` matches `^[a-zA-Z][a-zA-Z0-9_]*$`.
- `class_version` matches `^\d+\.\d+\.\d+$`.
- `superclasses` is an array of objects each with `classname` (string) and `schema` (string).
- `depends_on` is an array of dependency objects.
- `file` is an array of file record objects.
- `fields` is an array of field definition objects.
- Each field definition object has all required keys with correct types.
- `type` is one of the valid type strings.
- `ontology` is either null or an object with `namespace`, `term`, `uri`.
- `mustBeNonEmpty`, `mustBeScalar`, `mustNotHaveNaN`, `queryable` are all booleans.
- For `type: "structure"`, the `fields` key is present.

Write this as a proper JSON Schema Draft 7 document. Use `$defs` for reusable
sub-schemas (field definition, ontology object, etc.).

---

## Example Schema Files to Create

### `schemas/base_schema.json`

```json
{
    "classname":     "base",
    "class_version": "1.0.0",
    "superclasses":  [],
    "depends_on":    [],
    "file":          [],
    "fields": [
        {
            "name":           "id",
            "type":           "did_uid",
            "blank_value":    "",
            "default_value":  "",
            "mustBeNonEmpty": true,
            "mustBeScalar":   true,
            "mustNotHaveNaN": false,
            "queryable":      true,
            "ontology": {
                "namespace": "iao",
                "term":      "0000578",
                "uri":       "http://purl.obolibrary.org/obo/IAO_0000578"
            },
            "documentation":  "Unique identifier for this document instance.",
            "constraints":    {}
        },
        {
            "name":           "session_id",
            "type":           "did_uid",
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
            "type":           "char",
            "blank_value":    "",
            "default_value":  "",
            "mustBeNonEmpty": false,
            "mustBeScalar":   true,
            "mustNotHaveNaN": false,
            "queryable":      true,
            "ontology": {
                "namespace": "schema",
                "term":      "name",
                "uri":       "https://schema.org/name"
            },
            "documentation":  "Human-readable name for this document.",
            "constraints":    { "max_length": 256 }
        },
        {
            "name":           "datestamp",
            "type":           "timestamp",
            "blank_value":    "",
            "default_value":  "2018-12-05T18:36:47.241Z",
            "mustBeNonEmpty": true,
            "mustBeScalar":   true,
            "mustNotHaveNaN": false,
            "queryable":      true,
            "ontology": {
                "namespace": "schema",
                "term":      "dateCreated",
                "uri":       "https://schema.org/dateCreated"
            },
            "documentation":  "UTC timestamp of document creation in ISO 8601 format.",
            "constraints":    {}
        }
    ]
}
```

### `schemas/probe/probe_location_schema.json`

```json
{
    "classname":     "probe_location",
    "class_version": "1.0.0",
    "superclasses": [
        { "classname": "base", "schema": "$NDISCHEMAPATH/base_schema.json" }
    ],
    "depends_on": [
        {
            "name":           "probe_id",
            "mustBeNonEmpty": true,
            "documentation":  "The unique ID of the probe document this location is associated with."
        }
    ],
    "file":   [],
    "fields": [
        {
            "name":           "ontology_name",
            "type":           "char",
            "blank_value":    "",
            "default_value":  "",
            "mustBeNonEmpty": false,
            "mustBeScalar":   true,
            "mustNotHaveNaN": false,
            "queryable":      true,
            "ontology": {
                "namespace": "iao",
                "term":      "0000219",
                "uri":       "http://purl.obolibrary.org/obo/IAO_0000219"
            },
            "documentation":  "Formal ontology identifier for the probe location (e.g., 'uberon:0002436').",
            "constraints":    { "max_length": 256 }
        },
        {
            "name":           "name",
            "type":           "char",
            "blank_value":    "",
            "default_value":  "",
            "mustBeNonEmpty": false,
            "mustBeScalar":   true,
            "mustNotHaveNaN": false,
            "queryable":      true,
            "ontology": {
                "namespace": "schema",
                "term":      "name",
                "uri":       "https://schema.org/name"
            },
            "documentation":  "Human-readable name of the probe location (e.g., 'primary visual cortex').",
            "constraints":    { "max_length": 256 }
        }
    ]
}
```

---

## Example Definition Files to Create

Definition files describe the blank document (not the schema). They are what the system
reads to construct an empty document object in memory. They are **not** validated against
the schema — they represent the blank/template state.

### `definitions/base.json`

```json
{
    "document_class": {
        "definition":    "$NDIDOCUMENTPATH/base.json",
        "schema":        "$NDISCHEMAPATH/base_schema.json",
        "classname":     "base",
        "class_version": "1.0.0",
        "superclasses":  []
    },
    "depends_on": [],
    "base": {
        "id":          "",
        "session_id":  "",
        "name":        "",
        "datestamp":   ""
    }
}
```

Note: the blank values here (`""`) correspond to the `blank_value` for each field in
the schema. They are not required to pass validation.

### `definitions/probe/probe_location.json`

```json
{
    "document_class": {
        "definition":    "$NDIDOCUMENTPATH/probe/probe_location.json",
        "schema":        "$NDISCHEMAPATH/probe/probe_location_schema.json",
        "classname":     "probe_location",
        "class_version": "1.0.0",
        "superclasses": [
            { "classname": "base", "definition": "$NDIDOCUMENTPATH/base.json" }
        ]
    },
    "depends_on": [
        { "name": "probe_id", "value": "" }
    ],
    "base": {
        "id":          "",
        "session_id":  "",
        "name":        "",
        "datestamp":   ""
    },
    "probe_location": {
        "ontology_name": "",
        "name":          ""
    }
}
```

Note: when a definition has superclasses, the inherited fields are flattened into the
definition document directly (here, the `"base"` block appears in the probe_location
definition). This mirrors the existing NDI convention.

---

## MATLAB Classes to Implement

All classes live in the `+did/+schema/` package directory.

---

### `+did/+schema/Schema.m`

Loads and represents a single schema file.

```
Properties (public, read-only after construction):
    classname       (string)   — document type name
    class_version   (string)   — semver string
    superclasses    (struct array) — loaded superclass schemas (recursive)
    depends_on      (struct array) — dependency definitions
    file            (struct array) — file record definitions
    fields          (struct array) — field definitions for this class only
    all_fields      (struct array) — fields from this class + all superclasses (flattened)
    schema_path     (string)   — resolved filesystem path to this schema file
    raw             (struct)   — the raw parsed JSON struct

Constructor:
    s = did.schema.Schema(schema_path)
    s = did.schema.Schema(schema_path, path_tokens)
        schema_path  : path to the schema JSON file
                       may contain tokens like $NDISCHEMAPATH
        path_tokens  : (optional) struct with token -> path mappings
                       e.g., struct('NDISCHEMAPATH', '/path/to/schemas')

Methods (public):
    result = s.validate_schema_file()
        Validates the schema file itself against the meta-schema.
        Returns a did.schema.ValidationResult object.

    result = s.validate_document(doc_struct)
        Validates a document struct against this schema (including superclass fields).
        Returns a did.schema.ValidationResult object.

    field = s.get_field(field_name)
        Returns the field definition struct for a named field.
        Searches this class's fields and all inherited fields.
        Returns empty struct if not found.

    disp(s)
        Pretty-prints the schema summary.
```

---

### `+did/+schema/Document.m`

Loads and represents a document instance.

```
Properties (public, read-only after construction):
    classname       (string)
    class_version   (string)
    schema          (did.schema.Schema)  — the schema for this document type
    data            (struct)             — the full document data
    definition_path (string)

Constructor:
    d = did.schema.Document(definition_path_or_struct)
    d = did.schema.Document(definition_path_or_struct, schema_search_paths)

Methods (public):
    result = d.validate()
        Validates this document against its schema.
        Returns a did.schema.ValidationResult object.

    value = d.get(field_name)
        Returns the value of a named field, searching all property blocks.

    d2 = d.set(field_name, value)
        Returns a new Document with the named field set to value.
        Does not mutate the original.

    s = d.to_struct()
        Returns the document as a plain MATLAB struct.

    json = d.to_json()
        Returns the document as a JSON string.
```

---

### `+did/+schema/Validator.m`

Contains all validation logic. Stateless — all methods are static.

```
Static Methods:

    result = did.schema.Validator.validate_document(doc_struct, schema)
        Top-level entry point. Validates a document struct against a Schema object.
        Validates all fields, including inherited ones from superclasses.
        Validates depends_on entries.
        Returns a did.schema.ValidationResult.

    result = did.schema.Validator.validate_field(value, field_def)
        Validates a single value against a field definition struct.
        Applies type check, constraint check, mustBeNonEmpty, mustBeScalar, mustNotHaveNaN.
        Returns a did.schema.ValidationResult.

    ok = did.schema.Validator.check_type(value, type_string)
        Returns true if value conforms to the declared type.

    ok = did.schema.Validator.check_constraints(value, type_string, constraints)
        Returns true if value satisfies all constraints for the given type.

    ok = did.schema.Validator.check_mustBeNonEmpty(value)
        Returns false if value is [], {}, '', or [].

    ok = did.schema.Validator.check_mustBeScalar(value)
        Returns false if numel(value) != 1 for numeric/logical,
        or if the value is a cell array or non-scalar struct.

    ok = did.schema.Validator.check_mustNotHaveNaN(value)
        Returns false if any element of value is NaN.

    ok = did.schema.Validator.check_timestamp(value)
        Returns true if value is a string matching ISO 8601 UTC format.

    ok = did.schema.Validator.check_did_uid(value)
        Returns true if value looks like a valid DID UID.
        TODO: define the exact UID format regex; for now accept any non-empty string.

    [major, minor, patch] = did.schema.Validator.parse_semver(version_string)
        Parses a semver string. Throws if malformed.

    ok = did.schema.Validator.is_compatible_version(doc_version, schema_version)
        Returns true if doc_version and schema_version have the same MAJOR component.
```

---

### `+did/+schema/MetaValidator.m`

Validates schema files against the meta-schema using standard JSON Schema Draft 7.

```
Methods (public):

    result = did.schema.MetaValidator.validate(schema_path_or_struct)
        Validates a schema file against did_schema_meta.json.
        Returns a did.schema.ValidationResult.

    path = did.schema.MetaValidator.meta_schema_path()
        Returns the filesystem path to did_schema_meta.json,
        resolving relative to the location of this .m file.
```

Implementation note: MATLAB R2022b and later include `jsonschema.Validator`. Use it
if available. Otherwise, implement a lightweight structural checker in pure MATLAB that
checks required keys, types, and patterns without full JSON Schema Draft 7 compliance.
Leave a TODO marking where full Draft 7 compliance would be added.

---

### `+did/+schema/ValidationResult.m`

A simple result object returned by all validation functions.

```
Properties:
    is_valid    (logical)     — true if validation passed
    errors      (cell array of strings)  — error messages; empty if is_valid
    warnings    (cell array of strings)  — warnings (e.g., default_value doesn't pass validation)
    field_path  (string)      — dot-separated path to the field that failed, e.g. "probe_location.name"

Constructor:
    r = did.schema.ValidationResult()          — constructs a passing result
    r = did.schema.ValidationResult(errors)    — constructs a failing result

Methods:
    r = r.add_error(message)
    r = r.add_warning(message)
    r2 = r.merge(other_result)   — combine two results (union of errors and warnings)
    disp(r)                      — pretty-print the result
```

---

### `+did/+schema/util/loadJSON.m`

```
function s = loadJSON(filepath)
% LOADJSON Read a JSON file and return it as a MATLAB struct.
%   s = loadJSON(filepath)
%   filepath : absolute or relative path to a .json file
%   s        : MATLAB struct (or cell array for JSON arrays)
%
% Uses jsondecode internally. Throws a clear error if the file does not
% exist or is not valid JSON.
```

---

### `+did/+schema/util/semver.m`

```
function [major, minor, patch] = semver(version_string)
% SEMVER Parse a semantic version string.
%   [major, minor, patch] = semver('1.2.3')
%   Throws an error if the string does not match \d+\.\d+\.\d+.
```

---

### `+did/+schema/util/resolveSchemaPath.m`

```
function resolved = resolveSchemaPath(path_with_tokens, token_map)
% RESOLVESCHEMAPATH Substitute path tokens in a schema path string.
%   resolved = resolveSchemaPath('$NDISCHEMAPATH/base_schema.json', token_map)
%   token_map : struct where fieldnames are token names (without $),
%               and values are the replacement path strings.
%   Example:
%     token_map.NDISCHEMAPATH = '/home/user/schemas';
%     resolveSchemaPath('$NDISCHEMAPATH/base.json', token_map)
%     → '/home/user/schemas/base.json'
```

---

## Test Fixtures to Create

### `tests/fixtures/valid_base_document.json`

```json
{
    "document_class": {
        "definition":    "$NDIDOCUMENTPATH/base.json",
        "schema":        "$NDISCHEMAPATH/base_schema.json",
        "classname":     "base",
        "class_version": "1.0.0",
        "superclasses":  []
    },
    "depends_on": [],
    "base": {
        "id":          "4126919195e6b5af_40d651024919a2e4",
        "session_id":  "4126919195e8839b_40c6d9f78d173ae7",
        "name":        "my_test_document",
        "datestamp":   "2024-06-01T12:00:00.000Z"
    }
}
```

### `tests/fixtures/invalid_base_document_missing_id.json`

Same as above but with `"id": ""` — should fail `mustBeNonEmpty` for the `id` field.

### `tests/fixtures/invalid_base_document_bad_datestamp.json`

Same as valid but with `"datestamp": "not-a-timestamp"` — should fail timestamp format check.

### `tests/fixtures/valid_probe_location_document.json`

```json
{
    "document_class": {
        "definition":    "$NDIDOCUMENTPATH/probe/probe_location.json",
        "schema":        "$NDISCHEMAPATH/probe/probe_location_schema.json",
        "classname":     "probe_location",
        "class_version": "1.0.0",
        "superclasses": [
            { "classname": "base", "definition": "$NDIDOCUMENTPATH/base.json" }
        ]
    },
    "depends_on": [
        { "name": "probe_id", "value": "aabb1122ccdd3344_aabb1122ccdd3344" }
    ],
    "base": {
        "id":          "aabb1122ccdd3344_1122334455667788",
        "session_id":  "aabb1122ccdd3344_9900aabbccddeeff",
        "name":        "left_hemisphere_probe_location",
        "datestamp":   "2024-06-01T12:00:00.000Z"
    },
    "probe_location": {
        "ontology_name": "uberon:0002436",
        "name":          "primary visual cortex"
    }
}
```

### `tests/fixtures/invalid_schema_missing_classname.json`

A schema file with the `classname` key omitted — should fail meta-schema validation.

---

## Unit Tests to Implement

Each test file should use MATLAB's `matlab.unittest.TestCase` framework.

### `tests/test_Schema.m`

- Test that a valid schema file loads without error.
- Test that `Schema.fields` contains the correct number of fields for `base_schema.json`.
- Test that `Schema.all_fields` for `probe_location` includes both `base` and `probe_location` fields.
- Test that loading a schema with a bad path throws a clear error.
- Test that `validate_schema_file()` returns `is_valid = true` for `base_schema.json`.
- Test that `validate_schema_file()` returns `is_valid = false` for `invalid_schema_missing_classname.json`.

### `tests/test_Document.m`

- Test that `valid_base_document.json` loads and validates cleanly.
- Test that `valid_probe_location_document.json` loads and validates cleanly.
- Test that `invalid_base_document_missing_id.json` fails validation with an error mentioning `id`.
- Test that `invalid_base_document_bad_datestamp.json` fails validation with an error mentioning `datestamp`.
- Test that `Document.get('id')` returns the correct value.
- Test that `Document.set('name', 'new_name')` returns a new document with the updated value and does not modify the original.

### `tests/test_Validator.m`

- Test `check_mustBeNonEmpty` with: `""`, `[]`, `{}`, `null` (fail); `"hello"`, `1`, `struct('a',1)` (pass).
- Test `check_mustBeScalar` with: `[1 2 3]` (fail); `1`, `"hi"` (pass).
- Test `check_mustNotHaveNaN` with: `NaN`, `[1 NaN 3]` (fail); `1.5`, `[1 2 3]` (pass).
- Test `check_timestamp` with: `"2024-06-01T12:00:00.000Z"` (pass); `"not-a-date"`, `""` (fail).
- Test `check_type` for each of the valid type strings.
- Test `check_constraints` for integer min/max, double min/max, char max_length, matrix rows/cols.
- Test `parse_semver` with valid and invalid strings.
- Test `is_compatible_version` for same MAJOR (compatible), different MAJOR (incompatible).

### `tests/test_MetaValidator.m`

- Test that `base_schema.json` passes meta-validation.
- Test that `probe_location_schema.json` passes meta-validation.
- Test that `invalid_schema_missing_classname.json` fails meta-validation.
- Test that a schema with an unrecognized `type` string fails meta-validation.

### `tests/test_semver.m`

- Test `semver('1.0.0')` returns `[1, 0, 0]`.
- Test `semver('2.14.3')` returns `[2, 14, 3]`.
- Test `semver('bad')` throws an error.
- Test `semver('1.2')` throws an error.

---

## README.md Contents

Write a README.md with the following sections:

1. **What is this repo?** — one paragraph explaining did-schema as the schema layer for DID/NDI.
2. **Schema format overview** — brief description of the six top-level keys and the field definition object, with a link to `REPO_SPEC.md` for full details.
3. **Versioning** — one paragraph explaining semver usage and the MAJOR/MINOR/PATCH rules.
4. **blank_value vs. default_value** — one short paragraph.
5. **Validation** — explain that validation is explicit/deferred, not automatic on construction.
6. **Getting started** — how to run the tests (`runtests('tests')`), how to load a schema, how to validate a document, with code snippets.
7. **Repo structure** — the file tree reproduced.
8. **Contributing** — one paragraph: when to bump MAJOR vs. MINOR vs. PATCH when editing a schema file.

---

## Implementation Notes and TODOs

Leave the following as `% TODO` comments in the code:

- `Validator.check_did_uid`: The exact UID format regex is not yet standardized. For now, accept any non-empty string that is 33+ characters and contains only hex characters and underscores.
- `MetaValidator`: Full JSON Schema Draft 7 compliance is deferred. Current implementation checks required keys and basic types only.
- `Schema`: Superclass schemas are resolved relative to the referencing schema's directory. Cross-repo superclass resolution (e.g., NDI schema depending on a DID schema in a different repo) is not yet implemented — path tokens are the interim mechanism.
- `Document.validate()`: Dependency existence checks (verifying that `depends_on` values point to real documents in a database) are not implemented at this layer. This layer only checks that `mustBeNonEmpty` dependencies have non-empty values. Full existence checking is the responsibility of the database layer.
- `Validator.check_constraints` for `matrix`: Row/column dimension checking requires the value to actually be a 2D numeric array. The current implementation tolerates 1D arrays with a warning.

---

## Key Design Decisions (for reference, do not implement differently)

1. **`blank_value` and `default_value` are always both present** in every field definition. Neither is optional. This is enforced by the meta-schema.

2. **All three validation flags are always present** on every field (`mustBeNonEmpty`, `mustBeScalar`, `mustNotHaveNaN`). For types where a flag is meaningless (e.g., `mustNotHaveNaN` on a `char`), the flag must still be present and must be `false`. The meta-schema enforces this.

3. **`"fields"` is the universal key** for property lists, not a per-class key. The old format used a class-named key (e.g., `"base": [...]`, `"probe_location": [...]`). The new format always uses `"fields": [...]`. The classname is already in `classname`; there is no need to repeat it as a key.

4. **Validation is a pull action, not a push action.** A document does not validate itself on construction. Validation is triggered explicitly by calling `document.validate()` or by the database layer before insert. Schema files are validated against the meta-schema when `Schema` is constructed (a light check), but full document validation is always explicit.

5. **Superclass fields are inherited by flattening.** `Schema.all_fields` is a flat array combining fields from the schema and all its ancestors, in superclass-first order (base fields first). Duplicate field names are not permitted; the meta-validator checks for this across the inheritance chain.

6. **`ontology` is required on every field, but may be `null`.** Requiring the key (even if null) makes it clear that the schema author considered ontology annotation and made a deliberate choice. A missing `ontology` key is a meta-schema validation error.
