# V_gamma schemas

The `V_gamma/` directory is a forward-evolution of `V_beta/`. It inherits
V_beta's flat directory layout (one JSON file per document type at the top
of `schemas/V_gamma/`) and snake_case naming requirements for classnames,
field names, and filenames. See `V_beta_SPEC.md` for the rules that carry
over unchanged.

V_gamma adds three related features on top of V_beta:

- **Named composite types.** Two new entries in the field-definition `type`
  enum, each backed by a fixed sub-field layout in document values:
  - `duration`: `seconds` (double), `approximate` (boolean),
    `source_unit` (char), `source_value` (double). Supported `_constraints`
    keys: `minimum_seconds`, `maximum_seconds`, `allowed_units`.
  - `ontology_term`: `node` (char, a CURIE), `name` (char, label snapshot).
    Supported `_constraints` keys: `allowed_namespaces`.
  These composite types let a single field carry what previously required
  several coordinated char/double fields.

- **CURIE registry.** A new advisory file `CURIE_lookups_meta.json` maps
  CURIE prefixes (e.g., `iao`, `uberon`, `schema`, `allen_ccf_v3`) to their
  authoritative URI base and metadata. The registry is consumed by tooling
  to resolve CURIEs to URIs and to warn on unknown or approximate prefixes.
  It is not structurally enforced by the meta-schema.

- **Redesigned `_ontology` annotation shape.** The field-level `_ontology`
  annotation now uses two keys `_node` and `_name` instead of the V_beta
  four-key shape. The CURIE replaces the `_namespace`/`_term`/`_uri` trio:
  `_node` is `"<lowercased_namespace>:<term>"` and `_uri` is dropped
  (derivable from the CURIE registry). `_ontology: null` is still valid.

## Class-version bumps (2.0.0)

Four schemas collapse multiple coordinated fields into a single
`ontology_term` field:

| Schema               | Removed fields                              | Added field              |
|----------------------|---------------------------------------------|--------------------------|
| `probe_location`     | `ontology_name`, `name`                     | `location`               |
| `treatment`          | `ontology_name`, `name`                     | `treatment_name`         |
| `ontology_image`     | `ontology_name`, `ontology_region`          | `region`                 |
| `ontology_label`     | `ontology_name`, `label`, `label_id`        | `term`                   |

Each of these files bumped `_class_version` from `1.0.0` to `2.0.0` because
the document-visible field layout changed.

`ontology_table_row.json` was **not** refactored: its `ontology_nodes`
field is a comma-separated list of CURIEs (not a single composite), so it
stays at `1.0.0`.

## Annotation-shape change is not a version bump

The `_ontology` annotation-shape transform was applied to every schema
file in `V_gamma/` that carried the old four-key shape, but those files did
**not** receive a `_class_version` bump. The annotation is schema-file
syntax describing the field; it does not change the shape of documents
produced under the schema. Bumping `_class_version` is reserved for changes
that alter what a valid document looks like.

## Status

V_gamma is the current target once migration completes. The V_gamma test
suite (when added) will load `did_schema_meta.json` and the per-type
schemas from this directory.

Do not add new document types to `V_gamma/` without following the naming
requirements in `V_beta_SPEC.md` and the new type / annotation conventions
above.
