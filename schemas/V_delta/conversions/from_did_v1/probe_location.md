# Conversion: did_v1 → V_delta — `probe_location`

## Identity

- **V_delta `class_name`:** `probe_location`
- **V_delta tier:** `stable`
- **V_delta schema path:** `schemas/V_delta/stable/probe_location.json`
- **did_v1 source:** legacy NDI/DID `probe_location` document type
  (`_classname: "probe_location"`). The schema-shape ancestor in this
  repository is `schemas/V_alpha/probe_location.json`; the
  `schemas/V_beta/probe_location.json` revision is the same shape with
  only naming-convention housekeeping applied.
- **Status:** `drafted`

## Summary

`probe_location` records the anatomical or functional location at which a
probe is sampling. did_v1 carried this as a pair of coordinated `char`
fields (`ontology_name` + `name`); V_delta collapses them into a single
`location` field of the V_gamma-introduced `ontology_term` composite
type, which packages a CURIE node and a label snapshot under one key.

## Field mapping

One row per field across the V_alpha/V_beta-era shape and the V_delta
target. Beyond these fields, the universal renames listed in
[`_universal_renames.md`](_universal_renames.md) apply (snake-case
classname, ontology-annotation reshape, superclass-reference reshape,
class-scoped property block keyed by `probe_location`).

| did_v1 field | V_delta field | Transformation | Notes |
|---|---|---|---|
| `probe_location.ontology_name` (char) | `probe_location.location.node` | composed into `ontology_term` | CURIE (e.g., `uberon:0002436`). See "Transformations in detail". |
| `probe_location.name` (char) | `probe_location.location.name` | composed into `ontology_term` | Human-readable label snapshot (e.g., `primary visual cortex`). |
| — | `probe_location.location` (ontology_term) | new composite field | Created by composing the two did_v1 chars above. |
| `depends_on[probe_id]` | `depends_on[probe_id]` | identity | Declared on the schema; the document_id travels with each document. |

## Transformations in detail

- **Collapse two coordinated chars into one `ontology_term`.** did_v1
  stored the ontology identifier and its human-readable label as two
  separate `char` fields. V_delta declares a single `location` field of
  type `ontology_term` (introduced in V_gamma — see `V_gamma_notes.md`
  § "Class-version bumps (2.0.0)"). The composite value carries two
  sub-keys: `node` (the CURIE) and `name` (the label snapshot). The
  migration rule is:

      location = {
          "node": <did_v1 probe_location.ontology_name>,
          "name": <did_v1 probe_location.name>
      }

  Both inputs are `char`; the output sub-fields are `char`. If either
  input is empty, the corresponding sub-field is the empty string.

- **CURIE normalization.** did_v1's `ontology_name` was a free-form
  string; V_delta's `node` is a CURIE. If the did_v1 value already looks
  like `<prefix>:<term>` (e.g., `uberon:0002436`), it carries over
  verbatim. If it carries only a prefix name (e.g., `UBERON`) with the
  term elsewhere, the migrator must reconstruct the CURIE. See "Open
  questions" for the under-specified cases.

- **Document-instance shape.** V_delta uses class-scoped property
  blocks; the migrated `location` value lives under the
  `probe_location` block at path `probe_location.location`.

## Default values for new fields

V_delta introduces no required field on this class that did_v1 documents
do not already supply. The planned global `schema_version` field
(landing in this PR, or a follow-up, on `base.json`) will be inherited
once it ships; until then no migrated document needs to carry it.

## Worked example

### Before (did_v1)

```json
{
    "document_class": {
        "class_name": "probe_location",
        "class_version": "1.0.0",
        "superclasses": [
            { "class_name": "base", "class_version": "1.0.0" }
        ]
    },
    "depends_on": [
        { "name": "probe_id", "document_id": "aabb1122ccdd3344_aabb1122ccdd3344" }
    ],
    "base": {
        "id":         "aabb1122ccdd3344_1122334455667788",
        "session_id": "aabb1122ccdd3344_9900aabbccddeeff",
        "name":       "left_hemisphere_probe_location",
        "datestamp":  "2024-06-01T12:00:00.000Z"
    },
    "probe_location": {
        "ontology_name": "uberon:0002436",
        "name":          "primary visual cortex"
    }
}
```

### After (V_delta)

```json
{
    "document_class": {
        "class_name": "probe_location",
        "class_version": "1.0.0",
        "superclasses": [
            { "class_name": "base", "class_version": "1.0.0" }
        ]
    },
    "depends_on": [
        { "name": "probe_id", "document_id": "aabb1122ccdd3344_aabb1122ccdd3344" }
    ],
    "base": {
        "id":         "aabb1122ccdd3344_1122334455667788",
        "session_id": "aabb1122ccdd3344_9900aabbccddeeff",
        "name":       "left_hemisphere_probe_location",
        "datestamp":  "2024-06-01T12:00:00.000Z"
    },
    "probe_location": {
        "location": {
            "node": "uberon:0002436",
            "name": "primary visual cortex"
        }
    }
}
```

## File handling

This document type does not reference files. The generic file-handling
rules in [`_files.md`](_files.md) do not apply.

## Open questions

- **TODO-domain:** are did_v1 `ontology_name` values guaranteed to be
  well-formed CURIEs (`<prefix>:<term>`) in every dataset in the wild,
  or do some carry only a prefix string (e.g., `UBERON` with the term
  on `name` or elsewhere)? If the latter, the migrator needs a
  per-source rule to reconstruct the CURIE before populating
  `location.node`.
- **TODO-domain:** should the CURIE prefix be lowercased on migration
  (e.g., `UBERON:0002436` → `uberon:0002436`) to match the V_gamma
  CURIE-registry convention? `CURIE_lookups_meta.json` uses lowercase
  prefixes; the conservative behavior is to lowercase only the prefix
  segment.
- **TODO-domain:** the `mustBeNonEmpty` for `location` is `false` in
  the V_delta schema. If a did_v1 document has both inputs empty, the
  migrator can emit an empty composite (`{"node": "", "name": ""}`),
  or it can omit the field entirely. Confirm the preferred behavior.

## Cross-references

- General file-handling rules: [`_files.md`](_files.md)
- Universal did_v1 → V_delta renames: [`_universal_renames.md`](_universal_renames.md)
- V_delta schema file: [`schemas/V_delta/stable/probe_location.json`](../../stable/probe_location.json)
- Related conversions that follow the same two-char-to-`ontology_term`
  pattern: [`treatment.md`](treatment.md),
  [`ontology_image.md`](ontology_image.md),
  [`ontology_label.md`](ontology_label.md)
