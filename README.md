# did-schema

## What is this repo?

`did-schema` is the schema layer for DID (data-interface database) and NDI (neuroscience data interface). It defines the canonical JSON format for schema files that describe DID/NDI document types and ships a meta-schema that validates schema files themselves. This repo is not NDI itself -- it is a standalone dependency that both DID and NDI rely on for document type definitions. Language-specific tooling (MATLAB, Python, etc.) lives in separate repositories and consumes these schemas.

## Schema format overview

Every schema file is a JSON object with exactly six top-level keys:

- **`classname`** -- unique name of the document type (e.g., `"base"`, `"probe_location"`)
- **`class_version`** -- semantic version string `"MAJOR.MINOR.PATCH"`
- **`superclasses`** -- array of superclass references (classname + schema path)
- **`depends_on`** -- array of dependency objects (name, mustBeNonEmpty, documentation)
- **`file`** -- array of file record objects (name, documentation)
- **`fields`** -- array of field definition objects

Each field definition object contains: `name`, `type`, `blank_value`, `default_value`, `mustBeNonEmpty`, `mustBeScalar`, `mustNotHaveNaN`, `queryable`, `ontology`, `documentation`, and `constraints`. Supported types are `did_uid`, `char`, `integer`, `double`, `matrix`, `timestamp`, `boolean`, and `structure`.

See [schemas/V_alpha_SPEC.md](schemas/V_alpha_SPEC.md) for the V_alpha specification and [schemas/V_beta_SPEC.md](schemas/V_beta_SPEC.md) for the V_beta specification (V_alpha plus snake_case naming requirements).

The current sandbox iteration is **V_eta** (see [schemas/V_eta_SPEC.md](schemas/V_eta_SPEC.md)), which implements **Brainstorm J** from the `ndi-next-steps` thread: a subject-centric, statement-based reduction — thin subjects × one `subject_statement` family × data-type composites × typed relations, with vocabularies enforced by ontology bindings (the principles are in [schemas/V_eta_tenets.md](schemas/V_eta_tenets.md)). V_eta develops from **Brainstorm I** (V_zeta — a single `subject_interaction` spine with direction on the class and identity on the `variable` term; retained as an archived reference, see [schemas/V_zeta_SPEC.md](schemas/V_zeta_SPEC.md)), which in turn supersedes V_epsilon (Brainstorm E). Within each `V_*` directory, `index.json` is the resolution source of truth.

## Directory layout

Each document type is a directory under `schemas/` containing its schema definition:

```
did-schema/
|
+-- README.md
+-- pyproject.toml
|
+-- schemas/
|   +-- meta/
|   |   +-- did_schema_meta.json        <- meta-schema (JSON Schema Draft 7)
|   +-- base/
|   |   +-- schema.json                 <- schema for the base document type
|   +-- probe/
|       +-- probe_location/
|           +-- schema.json             <- schema for probe_location document type
|
+-- tests/
    +-- conftest.py
    +-- test_meta_schema.py
    +-- test_schemas.py
    +-- test_documents.py
    +-- fixtures/
        +-- valid_base_document.json
        +-- invalid_base_document_missing_id.json
        +-- invalid_base_document_bad_datestamp.json
        +-- valid_probe_location_document.json
        +-- invalid_schema_missing_classname.json
```

## Versioning

Schema files use semantic versioning (`MAJOR.MINOR.PATCH`). Increment **MAJOR** when making breaking changes (removing/renaming fields, changing types, adding required constraints or dependencies, modifying superclass hierarchy). Increment **MINOR** when adding new optional fields, relaxing constraints, or improving ontology annotations -- existing documents will still pass validation. Increment **PATCH** for documentation corrections, `default_value` changes, or formatting cleanup with no behavioral effect.

## blank_value vs. default_value

Every field has both a `blank_value` and a `default_value`. The `blank_value` is the value in a freshly constructed document before the user provides data -- it is allowed to fail validation (common values: `""`, `null`, `[]`). The `default_value` is a fallback that must pass validation and is used during programmatic document construction when the caller does not supply a value.

## Validation

Validation is explicit and deferred -- documents do not validate themselves on construction. Consumer tooling (MATLAB, Python, etc.) calls a validate function explicitly, or the database layer triggers validation before insert. Schema files are validated against the meta-schema at load time.

## Path tokens

Schema files use `$NDISCHEMAPATH` tokens in path references (e.g., superclass references). These are resolved at runtime by consumer tooling. For example, `$NDISCHEMAPATH/base/schema.json` resolves to the base schema file.

## Running the tests

```bash
pip install pytest jsonschema
pytest
```

Or install as a project with test dependencies:

```bash
pip install -e ".[test]"
pytest
```

## Adding a new document type

1. Create a directory under `schemas/` (e.g., `schemas/mytype/` or `schemas/category/mytype/`).
2. Add `schema.json` with the six required top-level keys.
3. Add test fixtures under `tests/fixtures/` if needed.
4. Run `pytest` to verify the new schema passes meta-validation.

## Contributing

When editing a schema file, choose the version bump carefully: use **MAJOR** when removing, renaming, or retyping fields, adding `mustBeNonEmpty` to previously optional fields, adding required dependencies, or changing the superclass hierarchy. Use **MINOR** when adding new optional fields, relaxing constraints, or adding/correcting ontology annotations. Use **PATCH** for documentation fixes, `default_value` adjustments, or formatting changes with no behavioral impact.
