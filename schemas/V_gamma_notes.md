# V_gamma schemas

The `V_gamma/` directory is a forward-evolution of `V_beta/`. It inherits
V_beta's flat directory layout (one JSON file per document type at the top
of `schemas/V_gamma/`) and snake_case naming requirements for class_names,
field names, and filenames. See `V_beta_SPEC.md` for the rules that carry
over unchanged.

V_gamma adds five related features on top of V_beta:

- **Named composite types.** Eight new entries in the field-definition
  `type` enum, each backed by a fixed sub-field layout in document values:
  - The SI-dimensioned family, all sharing the four-sub-field shape
    (`<canonical_unit>` double, `approximate` boolean, `source_unit`
    char, `source_value` double) and the same three `constraints`
    keys (`minimum`, `maximum`, `allowed_units`). `minimum` and
    `maximum` always bound the canonical value; the unit is determined
    by the field's type.
    - `duration`: canonical `seconds`.
    - `volume`: canonical `liters`.
    - `mass`: canonical `grams`.
    - `length`: canonical `meters`.
    - `voltage`: canonical `volts`.
    - `current`: canonical `amperes`.
    - `frequency`: canonical `hertz`.
  - `ontology_term`: `node` (char, a CURIE), `name` (char, label snapshot).
    Supported `constraints` keys: `allowed_namespaces`.
  These composite types let a single field carry what previously required
  several coordinated char/double fields. The canonical units of the
  SI-dimensioned family are practical SI (grams over kilograms, liters
  over cubic metres) so lab-scale values read naturally.

- **CURIE registry.** A new advisory file `CURIE_lookups_meta.json` maps
  CURIE prefixes (e.g., `iao`, `uberon`, `schema`, `allen_ccf_v3`) to their
  authoritative URI base and metadata. The registry is consumed by tooling
  to resolve CURIEs to URIs and to warn on unknown or approximate prefixes.
  It is not structurally enforced by the meta-schema.

- **Redesigned `ontology` annotation shape.** The field-level `ontology`
  annotation now uses two keys `node` and `name` instead of the V_beta
  four-key shape. The CURIE replaces the `_namespace`/`_term`/`_uri` trio:
  `node` is `"<lowercased_namespace>:<term>"` and `_uri` is dropped
  (derivable from the CURIE registry). `ontology: null` is still valid.

- **Class-scoped property blocks at the document-instance level.**
  V_beta's intended wire shape was a single flat namespace per document;
  V_gamma reverts to per-class property blocks keyed by `class_name`
  (one block per class in the inheritance chain). This restores the
  V_alpha document layout, collapsed so that the block key equals
  `class_name` verbatim (V_alpha's separate `property_list_name` is
  removed). Flattening remains an internal step for validators and
  query-path indexing; it is no longer the wire shape. See the new
  "JSON Format: Document Instances" section in `V_gamma_SPEC.md`.

  Motivation, in brief:
  - **Per-field provenance.** A reader can tell at a glance which class
    declared each value (it sits in that class's block), and find the
    field's `documentation`/`ontology`/`constraints` by opening
    `schemas/V_gamma/<block_key>.json`.
  - **No shadowing by construction.** Field identity is
    `(declaring_class, name)`. A subclass can declare a `name` that
    an ancestor also declares — the two are simply distinct fields
    living at distinct paths (e.g., `base.id` vs. `<subclass>.id`),
    not an override or shadow of one another.
  - **NDI-matlab compatibility.** NDI-matlab — the largest consumer of
    did-schema — is built end-to-end on the class-scoped layout. Keeping
    it at the wire-shape level reduces the V_alpha → V_gamma transition
    to a per-document data migration rather than a code rewrite of the
    toolbox.

- **Class metadata under a top-level `document_class` header.** The
  class-identity fields (`class_name`, `class_version`, `superclasses`,
  `maturity_level`) live under a top-level `document_class` block on both
  schema files and document instances, restoring the V_alpha legacy
  NDI-matlab layout. Previously V_gamma kept these at the top level with
  underscore prefixes (`_class_name`, `_class_version`, `_superclasses`);
  they are now nested and unprefixed inside `document_class`.
  `maturity_level`, which earlier V_gamma drafts also kept at the top
  level, is part of class identity and so lives inside `document_class`
  too. `depends_on` stays at the top level (it is a cross-document
  concern, not a piece of class identity).

  Inside `document_class.superclasses[i]`:
  - Schema files use `class_name` plus `schema` (the schema-file path).
  - Document instances use `class_name` plus `class_version` (no path).

  This is a schema-file-syntax change; no `class_version` bumps result
  from it. The motivation is one-to-one alignment with the V_alpha
  NDI-matlab wire shape so that the V_alpha → V_gamma transition
  remains a mechanical per-document data migration rather than a code
  rewrite of consumer tooling.

  `abstract` follows the same reasoning: whether a class is instantiable
  is class-identity metadata in the same sense as `maturity_level`, so
  it lives inside `document_class` as an optional boolean (default
  `false` when omitted) rather than as a sibling top-level key. This
  too is a schema-file-syntax change and does not trigger
  `class_version` bumps on the two schemas that carry `abstract: true`
  (`zarr`, `stimulus_response_scalar_parameters`).

## Class-version bumps (2.0.0)

Four schemas collapse multiple coordinated fields into a single
`ontology_term` field:

| Schema               | Removed fields                              | Added field              |
|----------------------|---------------------------------------------|--------------------------|
| `probe_location`     | `ontologyname`, `name`                     | `location`               |
| `treatment`          | `ontologyname`, `name`                     | `treatmentname`         |
| `ontology_image`     | `ontologyname`, `ontology_region`          | `region`                 |
| `ontologylabel`     | `ontologyname`, `label`, `label_id`        | `term`                   |

Each of these files bumped `_class_version` from `1.0.0` to `2.0.0` because
the document-visible field layout changed.

`ontology_table_row.json` was **not** refactored: its `ontology_nodes`
field is a comma-separated list of CURIEs (not a single composite), so it
stays at `1.0.0`.

## `duration` constraint-key rename

`duration` originally shipped with `constraints` keys
`minimum_seconds` and `maximum_seconds`. These were renamed to plain
`minimum` and `maximum` to align with the rest of the SI-dimensioned
family (`volume`, `mass`, `length`, `voltage`, `current`, `frequency`)
and with the unqualified `minimum`/`maximum` already used by the
primitive `double` and `integer` types. The field's `type` is enough
to determine the unit in which `minimum`/`maximum` are interpreted, so
the unit suffix added no information.

This is a schema-file-syntax change, not a document-shape change —
document values for `duration` fields (the `seconds`/`approximate`/
`source_unit`/`source_value` sub-fields) are unaffected. No
`_class_version` bump is required. Any schemas or external tooling
that referenced `minimum_seconds`/`maximum_seconds` must be updated
to use `minimum`/`maximum`.

## Annotation-shape change is not a version bump

The `ontology` annotation-shape transform was applied to every schema
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
