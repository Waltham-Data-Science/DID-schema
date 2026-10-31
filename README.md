# did-schema

## What is this repo?

`did-schema` is the schema layer for DID (data-interface database) and NDI (neuroscience data interface). It holds **did_v2**, the schema NDI V2 is built on: one JSON file per document class, the registries those classes bind to, the meta-schema that validates the class files themselves, the tools that check all of it, and the record of every decision about it. It is not NDI itself; the MATLAB code that builds, migrates and validates documents lives in [DID-matlab](https://github.com/VH-Lab/DID-matlab) and [NDI-matlab](https://github.com/VH-Lab/NDI-matlab), which read this repository.

How to work here (rules, gates, the sibling lock, who decides) is in [CLAUDE.md](CLAUDE.md).

## The model in brief

Every identifiable thing is an `entity` with a bound `type` (organism, device, session, dataset, ...). What is said about an entity is a statement whose class is its direction (`assertion`, `observation`, `manipulation` or `calculation`) and whose value kind (`mass`, `term`, `text`, ...) is a mixin in its `superclasses`. Relations are documents (`directed_relation`, `undirected_relation`). A value is inline or in data bodies (`sampled_body`, `opaque_body`). The principles are the tenets, [docs/did_v2_tenets.md](docs/did_v2_tenets.md); each decision is a `Decided by <name>, <date> [<tag>]` line in a plan document under [docs/plans/](docs/plans/).

## Layout

```
did-schema/
+-- README.md, CLAUDE.md
+-- schemas/
|   +-- did_v2/              class files only, one <class_name>.json per class, by family:
|   |   +-- *.json           the core classes (base, entity, statement and its directions,
|   |   |                    method, ...)
|   |   +-- value/           value and the value kinds (mass, length, term, text, ...)
|   |   +-- calculation/     calculation and the named calculation classes (tuning curves,
|   |   |                    receptive fields)
|   |   +-- data_body/       data_body, sampled_body, opaque_body
|   |   +-- time_reference/  time_reference, its absolute / relative forms, and clock_alignment,
|   |   |                    clock_alignment_configuration, clock_alignment_policy
|   |   +-- relation/        relation, directed_relation, undirected_relation
|   |   +-- acquisition/     acquisition_system, acquisition_channels, acquisition_reader,
|   |   |                    epoch_file_pattern, epoch_parameter_reader, ingestion_manifest
|   |   +-- retiring/        the retire classes still in the tree, until each is deleted
|   +-- registry/            authored data: did_schema_meta.json (the meta-schema),
|   |                        binding_registry_meta, CURIE_lookups_meta, ndi_reserved_keys,
|   |                        topics (viewer), did_v2_term_registry, did_v2_carry_register,
|   |                        did_v2_openminds_crosswalk, did_v2_class_dispositions,
|   |                        did_v2_migration_decisions
|   +-- generated/           written by tools only: index.json, term_registry_meta,
|   |                        class_disposition_meta, quantity_list_meta, did_v2_coverage_ledger,
|   |                        did_v2_decisions, did_v2_ndi_ground_truth, did_v2_migration_targets
|   +-- did_v1/              reserved for the frozen v1 set; until then NDI-matlab main is the v1 truth
+-- docs/
|   +-- did_v2_tenets.md, did_v2_OPEN_WORK.md, did_query_model.md   entry points
|   +-- plans/               plan and decision documents (flat)
|   +-- generated/           did_v2_STATUS.md, did_v2_coverage_ledger.md,
|   |                        did_v2_final_class_set.md (do not hand-edit)
|   +-- history/             superseded documents, kept for their record
|   +-- v2_working/, V2_PLAN.md   working notes and the working plan (not the record)
+-- tools/                   gates.py and the tools it runs; schema_paths.py and
|                            doc_paths.py say where every file lives
+-- tests/                   pytest suite (run by gates.py)
+-- web/                     the schema viewer (see web/README.md)
```

A folder under `schemas/did_v2/` means a family, never a tier or a maturity. A family's root class lives in its family folder (`value/value.json`, `relation/relation.json`). Class names are unique across the tree, and no file name repeats anywhere under `schemas/`: DID-matlab and NDI-matlab find class files at any depth under `schemas/did_v2/` and every other file by its name. A document cited by bare name (`did_v2_epoch_plan.md`) is the unique file of that name under `docs/`.

## A class file

A class file has four top-level keys:

- **`document_class`**: `class_name` (the file name), `class_version` (`"MAJOR.MINOR.PATCH"`), `superclasses` (a list of `{class_name}`), `maturity_level`
- **`depends_on`**: the class's edges to other documents
- **`file`**: the files a document of the class may carry
- **`fields`**: field definitions, nested for structures; each has `name`, `type`, `blank_value`, `default_value`, `mustBeNonEmpty`, `mustBeScalar`, `mustNotHaveNaN`, `queryable`, `ontology`, `documentation` and `constraints`

`schemas/registry/did_schema_meta.json` is the meta-schema every class file must pass.

## Changing a class

1. Edit or add `schemas/did_v2/<family>/<class_name>.json` (JSON, indent 4).
2. For a new class, add its `disposition` (`persist`, `retire` or `in_progress`) to `schemas/registry/did_v2_class_dispositions.json`. A `retire` class lives in `schemas/did_v2/retiring/`.
3. Run `python3 tools/gates.py`. Its `validate_v_eta` step checks the class and rewrites `schemas/generated/` (the index and the built registries); do not hand-edit anything there.
4. A schema change the sibling code must follow lands in DID-matlab and NDI-matlab first (CLAUDE.md, section 3).

The team decides; a change is recorded as a decision line in the plan document it belongs to and reaches `main` through a reviewed PR.

## Running the gates

```bash
pip install -e ".[test]"
python3 tools/gates.py            # regenerate every derived artifact, then run every gate (includes pytest)
python3 tools/gates.py --check    # the same in a scratch mirror; writes nothing
python3 tools/gates.py --explain  # the order of the steps, and why
```

The gates read the sibling repositories at the commits locked in `tools/sibling_lock.json`. Point `NDI_MATLAB`, `DID_MATLAB`, `NDICALC_VIS_MATLAB` and `EMPTY_ONTOLOGY` at the checkouts you mean, at the locked heads (CLAUDE.md, section 3).

## Versioning a class

Increment **MAJOR** for a breaking change (removing, renaming or retyping a field, adding `mustBeNonEmpty` to an optional field, adding a required dependency, changing the superclasses). Increment **MINOR** for an additive change (a new optional field, a relaxed constraint, an ontology annotation). Increment **PATCH** for documentation, `default_value` or formatting changes with no behavioural effect.

## blank_value and default_value

`blank_value` is the value in a freshly constructed document before the user provides data; it may fail validation. `default_value` is the fallback used when a caller supplies nothing; it must pass validation.

## Validation

Validation is explicit: a document does not validate itself on construction. DID-matlab's `did2.build` and the database layer validate against these schemas; `tools/validate_v_eta.py` (run by `tools/gates.py`) validates the schema files themselves.
