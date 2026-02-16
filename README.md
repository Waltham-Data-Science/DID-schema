# did-schema

## What is this repo?

`did-schema` is the schema layer for DID (data-interface database) and NDI (neuroscience data interface). It defines the canonical JSON format for schema files that describe DID/NDI document types, provides MATLAB classes for loading, parsing, and validating both schema files and document instances, and ships a meta-schema that validates schema files themselves. This repo is not NDI itself -- it is a standalone dependency that both DID and NDI rely on for document type definitions and validation.

## Schema format overview

Every schema file is a JSON object with exactly six top-level keys:

- **`classname`** -- unique name of the document type (e.g., `"base"`, `"probe_location"`)
- **`class_version`** -- semantic version string `"MAJOR.MINOR.PATCH"`
- **`superclasses`** -- array of superclass references (classname + schema path)
- **`depends_on`** -- array of dependency objects (name, mustBeNonEmpty, documentation)
- **`file`** -- array of file record objects (name, documentation)
- **`fields`** -- array of field definition objects

Each field definition object contains: `name`, `type`, `blank_value`, `default_value`, `mustBeNonEmpty`, `mustBeScalar`, `mustNotHaveNaN`, `queryable`, `ontology`, `documentation`, and `constraints`. Supported types are `did_uid`, `char`, `integer`, `double`, `matrix`, `timestamp`, `boolean`, and `structure`.

See [REPO_SPEC.md](REPO_SPEC.md) for the full specification.

## Versioning

Schema files use semantic versioning (`MAJOR.MINOR.PATCH`). Increment **MAJOR** when making breaking changes (removing/renaming fields, changing types, adding required constraints or dependencies, modifying superclass hierarchy). Increment **MINOR** when adding new optional fields, relaxing constraints, or improving ontology annotations -- existing documents will still pass validation. Increment **PATCH** for documentation corrections, `default_value` changes, or formatting cleanup with no behavioral effect.

## blank_value vs. default_value

Every field has both a `blank_value` and a `default_value`. The `blank_value` is the value in a freshly constructed document before the user provides data -- it is allowed to fail validation (common values: `""`, `null`, `[]`). The `default_value` is a fallback that must pass validation and is used during programmatic document construction when the caller does not supply a value.

## Validation

Validation is explicit and deferred -- documents do not validate themselves on construction. Call `document.validate()` or `schema.validate_document(doc_struct)` to trigger validation. Schema files are lightly checked against the meta-schema when loaded, but full document validation is always a pull action initiated by the caller or the database layer before insert.

## Getting started

### Run the tests

```matlab
% From the repo root directory
addpath(pwd);
runtests('tests');
```

### Load a schema

```matlab
tokens = struct('NDISCHEMAPATH', fullfile(pwd, 'schemas'), ...
                'NDIDOCUMENTPATH', fullfile(pwd, 'definitions'));

s = did.schema.Schema(fullfile(pwd, 'schemas', 'base_schema.json'), tokens);
disp(s);
```

### Validate a document

```matlab
tokens = struct('NDISCHEMAPATH', fullfile(pwd, 'schemas'), ...
                'NDIDOCUMENTPATH', fullfile(pwd, 'definitions'));

d = did.schema.Document(fullfile(pwd, 'tests', 'fixtures', 'valid_base_document.json'), tokens);
result = d.validate();
disp(result);
```

### Load and inspect a schema field

```matlab
field = s.get_field('datestamp');
disp(field);
```

## Repo structure

```
did-schema/
|
+-- README.md
+-- REPO_SPEC.md
|
+-- schemas/
|   +-- meta/
|   |   +-- did_schema_meta.json
|   +-- base_schema.json
|   +-- probe/
|       +-- probe_location_schema.json
|
+-- definitions/
|   +-- base.json
|   +-- probe/
|       +-- probe_location.json
|
+-- +did/
|   +-- +schema/
|       +-- Schema.m
|       +-- Document.m
|       +-- Validator.m
|       +-- MetaValidator.m
|       +-- ValidationResult.m
|       +-- util/
|           +-- loadJSON.m
|           +-- semver.m
|           +-- resolveSchemaPath.m
|
+-- tests/
    +-- test_Schema.m
    +-- test_Document.m
    +-- test_Validator.m
    +-- test_MetaValidator.m
    +-- test_semver.m
    +-- fixtures/
        +-- valid_base_document.json
        +-- invalid_base_document_missing_id.json
        +-- invalid_base_document_bad_datestamp.json
        +-- valid_probe_location_document.json
        +-- invalid_schema_missing_classname.json
```

## Contributing

When editing a schema file, choose the version bump carefully: use **MAJOR** when removing, renaming, or retyping fields, adding `mustBeNonEmpty` to previously optional fields, adding required dependencies, or changing the superclass hierarchy. Use **MINOR** when adding new optional fields, relaxing constraints, or adding/correcting ontology annotations. Use **PATCH** for documentation fixes, `default_value` adjustments, or formatting changes with no behavioral impact.
