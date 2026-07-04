# Conversion: did_v1 → V_delta — `ontology_label`

## Identity

- **V_delta `class_name`:** `ontology_label`
- **V_delta tier:** `stable`
- **V_delta schema path:** `schemas/V_delta/stable/ontology_label.json`
- **did_v1 source:** legacy NDI/DID `ontologyLabel` document type
  (`_classname: "ontologyLabel"` — camelCase). Schema-shape ancestor in
  this repository is `schemas/V_alpha/ontologyLabel.json`;
  `schemas/V_beta/ontology_label.json` is the same shape after the
  V_alpha → V_beta snake-case housekeeping
  (`ontologyLabel` → `ontology_label`).
- **Status:** `drafted`

## Summary

`ontology_label` attaches an ontology-derived label to an element
(e.g., a brain-region label from Allen CCF). did_v1 stored three
coordinated fields — `ontology_name` (the source ontology),
`label` (the human-readable region name), and `label_id` (a numeric
id within that ontology). V_delta collapses these into a single
`term` field of `ontology_term` composite type, where the CURIE
`<ontology_name>:<label_id>` becomes the node and `label` becomes the
label snapshot.

## Field mapping

Beyond these fields, the universal renames listed in
[`_universal_renames.md`](_universal_renames.md) apply (snake-case
classname `ontologyLabel` → `ontology_label`, ontology-annotation
reshape, superclass-reference reshape, class-scoped property block
keyed by `ontology_label`).

| did_v1 field | V_delta field | Transformation | Notes |
|---|---|---|---|
| `ontologyLabel.ontology_name` (char) | `ontology_label.term.node` (CURIE prefix) | composed into `ontology_term`; combined with `label_id` | See "Transformations in detail". |
| `ontologyLabel.label_id` (integer) | `ontology_label.term.node` (CURIE local part) | composed into `ontology_term`; combined with `ontology_name` | See "Transformations in detail". |
| `ontologyLabel.label` (char) | `ontology_label.term.name` | composed into `ontology_term` | Human-readable label snapshot. |
| — | `ontology_label.term` (ontology_term) | new composite field | Created by composing the three did_v1 fields above. `mustBeNonEmpty: true`. |
| `depends_on[element_id]` | `depends_on[element_id]` | identity | |

## Transformations in detail

- **Three-field collapse into one `ontology_term`.** Unlike
  `probe_location` / `treatment` / `ontology_image`, which collapse two
  did_v1 chars into a composite, `ontology_label` collapses three
  fields (one char + one char + one integer). The migration rule is:

      term = {
          "node": "<ontology_name>:<label_id>",
          "name": <did_v1 ontologyLabel.label>
      }

  The CURIE is built by concatenating the source-ontology name (the
  CURIE prefix), a colon, and the string form of `label_id`. The
  V_delta schema's `documentation` for `term` describes this layout
  explicitly: "The CURIE prefix identifies the source ontology (e.g.,
  'allen_ccf_v3'), the local part is the numeric ID (e.g.,
  'allen_ccf_v3:12345'), and 'name' carries the human-readable label."

- **CURIE prefix normalization.** did_v1's `ontology_name` is a
  free-form string (e.g., `Allen CCF v3`). For V_delta the prefix must
  match a registered CURIE prefix in `CURIE_lookups_meta.json` (or at
  least follow that file's conventions). The migrator should
  lower-case the prefix and replace spaces with underscores; the
  resulting `Allen CCF v3` → `allen_ccf_v3`. The mapping is not
  bijective in the general case (multiple did_v1 strings can map to
  one CURIE prefix), so this is a one-way normalization step. See
  "Open questions" for un-registrable cases.

- **Class name normalization.** `ontologyLabel` (V_alpha) →
  `ontology_label` (V_beta and later) is a snake-case rename. The
  migrator rewrites `document_class.class_name` and the property-block
  key.

- **Document-instance shape.** V_delta uses class-scoped property
  blocks; the `term` value lives at `ontology_label.term`.

## Default values for new fields

V_delta introduces no required field on this class beyond what did_v1
documents already supply, modulo the `mustBeNonEmpty: true` tightening
on `term` (which is a stricter validation of an existing input, not a
new field).

## Worked example

### Before (did_v1)

```json
{
    "document_class": {
        "class_name": "ontologyLabel",
        "class_version": "1.0.0",
        "superclasses": [
            { "class_name": "base", "class_version": "1.0.0" }
        ]
    },
    "depends_on": [
        { "name": "element_id", "document_id": "" }
    ],
    "base": {
        "id":         "aabb1122ccdd3344_1122334455667788",
        "session_id": "aabb1122ccdd3344_9900aabbccddeeff",
        "name":       "v1_label_for_element_x",
        "datestamp":  "2024-06-01T12:00:00.000Z"
    },
    "ontologyLabel": {
        "ontology_name": "Allen CCF v3",
        "label":         "primary visual cortex",
        "label_id":      12345
    }
}
```

### After (V_delta)

```json
{
    "document_class": {
        "class_name": "ontology_label",
        "class_version": "1.0.0",
        "superclasses": [
            { "class_name": "base", "class_version": "1.0.0" }
        ]
    },
    "depends_on": [
        { "name": "element_id", "document_id": "" }
    ],
    "base": {
        "id":         "aabb1122ccdd3344_1122334455667788",
        "session_id": "aabb1122ccdd3344_9900aabbccddeeff",
        "name":       "v1_label_for_element_x",
        "datestamp":  "2024-06-01T12:00:00.000Z"
    },
    "ontology_label": {
        "term": {
            "node": "allen_ccf_v3:12345",
            "name": "primary visual cortex"
        }
    }
}
```

## File handling

This document type does not reference files. The generic file-handling
rules in [`_files.md`](_files.md) do not apply.

## Open questions

- **TODO-domain:** the V_delta `term.node` is documented as
  "<prefix>:<numeric ID>". did_v1's `label_id` is declared `integer`
  with `mustBeNonEmpty: false` and `_default_value: 0`. Documents that
  carry the default `0` (or no `label_id`) cannot form a meaningful
  CURIE local part. Options: (a) emit `<prefix>:0` and rely on
  consumers to recognize it as a placeholder; (b) reject the migration
  and require the producer to supply a real id; (c) introduce a
  side-channel for "label-only" ontology entries (no numeric id),
  e.g., `<prefix>:<label-as-slug>`. Decision pending.
- **TODO-domain:** for did_v1 `ontology_name` values that do not map
  cleanly to a registered CURIE prefix (e.g., free-form lab-specific
  labels), what should the migrator do — fail, emit a TODO-marked
  CURIE, or write to a side-channel? Mirrors the open question in
  [`ontology_image.md`](ontology_image.md).
- **TODO-domain:** the V_delta schema declares `term` as
  `mustBeNonEmpty: true`. did_v1 made each of the three input fields
  individually nullable. Whether to demote `term` to `mustBeNonEmpty:
  false` to preserve migration completeness, or to enforce non-empty
  and reject deficient sources, is the same question as in
  [`ontology_image.md`](ontology_image.md).

## Cross-references

- General file-handling rules: [`_files.md`](_files.md)
- Universal did_v1 → V_delta renames: [`_universal_renames.md`](_universal_renames.md)
- V_delta schema file: [`schemas/V_delta/stable/ontology_label.json`](../../stable/ontology_label.json)
- Sibling ontology-annotation type: [`ontology_image.md`](ontology_image.md)
- Same composite-collapse pattern (two-input variant):
  [`probe_location.md`](probe_location.md),
  [`treatment.md`](treatment.md)
- CURIE prefix registry (V_delta):
  [`schemas/V_delta/stable/CURIE_lookups_meta.json`](../../stable/CURIE_lookups_meta.json)
