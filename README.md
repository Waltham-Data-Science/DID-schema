# did-schema

## What is this repo?

`did-schema` is the schema layer for DID (data-interface database) and NDI (neuroscience data interface). It defines the canonical JSON format for schema files that describe DID/NDI document types and ships a meta-schema that validates schema files themselves. This repo is not NDI itself -- it is a standalone dependency that both DID and NDI rely on for document type definitions. Language-specific tooling (MATLAB, Python, etc.) lives in separate repositories and consumes these schemas.

## Schema format overview

The schema in use is **V_eta**. Each document class is one JSON file under `schemas/did_v2/<tier>/<class_name>.json`, where the tier is `stable`, `draft` or `deprecated` (v1 tombstones that migrated documents validate through). A class file has four top-level keys:

- **`document_class`** -- `class_name`, `class_version` (semantic version `"MAJOR.MINOR.PATCH"`), `superclasses` (a list of `{class_name}`), and `maturity_level`
- **`depends_on`** -- the class's edges to other documents (name, mustBeNonEmpty, documentation)
- **`file`** -- the files a document of the class may carry (name, documentation)
- **`fields`** -- field definition objects, nested for structures

Each field definition object contains: `name`, `type`, `blank_value`, `default_value`, `mustBeNonEmpty`, `mustBeScalar`, `mustNotHaveNaN`, `queryable`, `ontology`, `documentation`, and `constraints`, plus `fields` for a structure.

`schemas/did_v2/index.json` lists every class with its tier, version and superclasses (derived) and its `disposition` (hand-written: `persist`, `retire` or `in_progress`). The registries the classes bind to live in `schemas/did_v2/stable/*_meta.json`; the term registry's source is `schemas/did_v2_term_registry.json`.

The model in one paragraph: every identifiable thing is an `entity` with a bound `type`; what is said about it is a statement (`assertion`, `observation`, `manipulation` or `calculation`) whose value kind is a mixin in its `superclasses`; relations are `directed_relation` documents; values are inline or in data bodies (`sampled_body`, `opaque_body`). The principles are in [docs/did_v2_tenets.md](docs/did_v2_tenets.md), and each decision is recorded in a plan document under `schemas/` (`Decided by <name>, <date> [<tag>]` lines). [docs/history/did_v2_SPEC.md](docs/history/did_v2_SPEC.md) predates the 2026-10-08 entity merge; where it disagrees with the tenets or a plan document, those win.

The earlier versions (`V_alpha` .. `V_zeta`) are retired: their schema trees are deleted, and only their `*_SPEC.md` / `*_notes.md` files remain in `schemas/` as history.

## Directory layout

```
did-schema/
|
+-- README.md, CLAUDE.md (how to work in this repository)
+-- schemas/
|   +-- V_eta/
|   |   +-- index.json                  <- class index (tier, version, superclasses, disposition)
|   |   +-- stable/  draft/  deprecated/  <- one <class_name>.json per class; *_meta.json registries
|   |   +-- conversions/from_did_v1/    <- per-class v1 -> V_eta conversion notes
|   +-- did_v2_term_registry.json        <- source of the term registry
|   +-- V_eta_*_plan.md, did_v2_tenets.md  <- decisions and principles
|   +-- did_v2_STATUS.md, did_v2_coverage_ledger.*, ...  <- generated (do not hand-edit)
+-- tools/                              <- gates.py and the tools it runs
+-- tests/                              <- pytest suite
+-- web/                                <- schema viewer (see web/README.md)
```

## Versioning

Schema files use semantic versioning (`MAJOR.MINOR.PATCH`). Increment **MAJOR** when making breaking changes (removing/renaming fields, changing types, adding required constraints or dependencies, modifying superclass hierarchy). Increment **MINOR** when adding new optional fields, relaxing constraints, or improving ontology annotations -- existing documents will still pass validation. Increment **PATCH** for documentation corrections, `default_value` changes, or formatting cleanup with no behavioral effect.

## blank_value vs. default_value

Every field has both a `blank_value` and a `default_value`. The `blank_value` is the value in a freshly constructed document before the user provides data -- it is allowed to fail validation (common values: `""`, `null`, `[]`). The `default_value` is a fallback that must pass validation and is used during programmatic document construction when the caller does not supply a value.

## Validation

Validation is explicit and deferred -- documents do not validate themselves on construction. Consumer tooling (MATLAB, Python, etc.) calls a validate function explicitly, or the database layer triggers validation before insert. Class files are checked by `tools/validate_v_eta.py`, which `tools/gates.py` runs.

## Running the tests and gates

```bash
pip install -e ".[test]"
python3 tools/gates.py            # regenerate every derived artifact, then run every gate (includes pytest)
python3 tools/gates.py --check    # the same in a scratch mirror; writes nothing
```

Some gates read the sibling repositories (NDI-matlab, DID-matlab, empty-ontology); point `NDI_MATLAB`, `DID_MATLAB` and `EMPTY_ONTOLOGY` at the checkouts you mean (see `CLAUDE.md`, section 3).

## Adding or changing a class

1. Edit or add `schemas/did_v2/<tier>/<class_name>.json` (JSON, indent 4).
2. For a new class, add a hand-written `disposition` to its entry in `schemas/did_v2/index.json`; the other index fields are derived.
3. Run `python3 tools/gates.py`. Its `validate_v_eta` step checks the class and rewrites the derived files (`index.json`, the built registries); do not hand-edit those.
4. Record the decision behind the change in the plan document it belongs to.

## Contributing

When editing a schema file, choose the version bump carefully: use **MAJOR** when removing, renaming, or retyping fields, adding `mustBeNonEmpty` to previously optional fields, adding required dependencies, or changing the superclass hierarchy. Use **MINOR** when adding new optional fields, relaxing constraints, or adding/correcting ontology annotations. Use **PATCH** for documentation fixes, `default_value` adjustments, or formatting changes with no behavioral impact.
