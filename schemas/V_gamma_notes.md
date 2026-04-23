# V_gamma schemas

The `V_gamma/` directory is a forward-evolution of `V_beta/`. It inherits
V_beta's flat directory layout (one JSON file per document type at the top
of `schemas/V_gamma/`) and snake_case naming requirements for classnames,
field names, and filenames. See `V_beta_SPEC.md` for the rules that carry
over unchanged.

V_gamma adds three related features on top of V_beta:

- **Named composite types.** Ten new entries in the field-definition
  `type` enum, each backed by a fixed sub-field layout in document values:
  - The SI-dimensioned family, all sharing the four-sub-field shape
    (`<canonical_unit>` double, `approximate` boolean, `source_unit`
    char, `source_value` double) and the same three `_constraints`
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
    Supported `_constraints` keys: `allowed_namespaces`.
  - `timeref_epochset`: four-field tuple naming an acquisition-clock
    origin — `epochsetname` (char), `classname` (char), `epoch` (char),
    `clocktype` (char enum: `dev_local_time`, `dev_global_time`,
    `exp_global_time`). Supported `_constraints` keys: `allowed_classnames`,
    `allowed_clocktypes`.
  - `time_reference`: a time value expressed as `(origin, offset_seconds)`,
    where the origin is one of: a depended-on document (via the
    containing schema's `_depends_on` array, so cascading deletes apply),
    an acquisition-clock epoch (a nested `timeref_epochset`), a UTC
    wall-clock timestamp (no offset applies), an ontology-anchored
    developmental stage (a nested `ontology_term`), or `unknown`. Sub-fields:
    `referent_kind` (enum), `depends_on_name`, `anchor_point` (`start` or
    `end`), `epochset`, `utc_timestamp`, `stage`, `offset_seconds`,
    `approximate`, `notes`. Supported `_constraints` keys: `allowed_kinds`,
    `allowed_stage_namespaces`. See `V_gamma_SPEC.md` for the
    required-by-kind table.
  These composite types let a single field carry what previously required
  several coordinated char/double fields. The canonical units of the
  SI-dimensioned family are practical SI (grams over kilograms, liters
  over cubic metres) so lab-scale values read naturally.

  Composites may now nest other composites: `time_reference` embeds
  `timeref_epochset` and `ontology_term` as sub-fields. The validator
  resolves the nested shape from this spec by type name; schema authors
  do not redeclare the sub-shape.

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

## `time_reference` migration of `valid_interval` (2.0.0)

`valid_interval.json` previously carried two ad-hoc 5-sub-field structures
(`timeref_structt0`, `timeref_structt1`) plus two loose `t0` / `t1`
doubles. With the introduction of the `time_reference` composite type,
that schema is rewritten to:

| Removed fields                                                   | Added fields                                                       |
|------------------------------------------------------------------|--------------------------------------------------------------------|
| `timeref_structt0`, `t0`, `timeref_structt1`, `t1` (4 fields)    | `t0_reference` (`time_reference`), `t1_reference` (`time_reference`) |

Two new optional `_depends_on` entries (`t0_referent_id`,
`t1_referent_id`) carry the document references when either side's
`referent_kind == 'document'`, so referential integrity (and cascading
delete) is inherited from the existing dependency machinery rather than
re-implemented. `_class_version` is bumped from `1.0.0` to `2.0.0`
because the document-visible field layout changed.

The acquisition-clock case (the only one the old `timeref_struct*` shapes
could really express) round-trips through the new composite by setting
`referent_kind == 'acquisition_clock'` and populating the nested
`epochset` sub-composite (`epochsetname`, `classname`, `epoch`,
`clocktype`).

## `time_reference` adoption on existing schemas (MINOR bumps)

Two existing schemas gained a single optional `time_reference` field plus
a matching optional `_depends_on` entry:

| Schema             | Old version → new | Field added       | Depends-on added              |
|--------------------|-------------------|-------------------|-------------------------------|
| `treatment`        | `2.0.0` → `2.1.0` | `administered_at` | `administered_at_referent_id` |
| `virus_injection`  | `1.0.0` → `1.1.0` | `injected_at`     | `injected_at_referent_id`     |

Both fields are `_mustBeNonEmpty: false`; documents written before the
bump remain valid.

## New schemas: `session_occurrence`, `subject_birth_event`

Two new tag-style companion documents were added rather than overloading
existing tag documents:

- `session_occurrence` — depends on a `session` document; carries
  optional `started_at` and `ended_at` `time_reference` fields. Created
  separately so that `session.json` remains a stable identifier other
  documents can `_depends_on` before its occurrence times are known.
- `subject_birth_event` — depends on a `subject` document; carries
  required `occurred_at` (a `time_reference`). The `subject` document
  remains a tag-only identifier, so DOB does not live there. For
  wild-caught animals or subjects without recorded DOB, the
  `occurred_at` value uses `referent_kind == 'unknown'`; for
  stage-only knowledge, `referent_kind == 'ontology_stage'` with a
  developmental-stage CURIE (e.g., `mmusdv:0000037`).

## CURIE registry: `mmusdv`, `hsapdv` added (1.1.0)

`CURIE_lookups_meta.json` `_format_version` bumped `1.0.0` → `1.1.0`.
Two new prefixes registered to support stage-anchored time references:

- `mmusdv` — Mouse Developmental Stages (`http://purl.obolibrary.org/obo/MmusDv_`)
- `hsapdv` — Human Developmental Stages (`http://purl.obolibrary.org/obo/HsapDv_`)

## `duration` constraint-key rename

`duration` originally shipped with `_constraints` keys
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
