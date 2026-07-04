# Conversion: did_v1 → V_delta — `ontology_image`

## Identity

- **V_delta `class_name`:** `ontology_image`
- **V_delta tier:** `stable`
- **V_delta schema path:** `schemas/V_delta/stable/ontology_image.json`
- **did_v1 source:** legacy NDI/DID `ontologyImage` document type
  (`_classname: "ontologyImage"` — camelCase). Schema-shape ancestor in
  this repository is `schemas/V_alpha/ontologyImage.json`;
  `schemas/V_beta/ontology_image.json` is the same shape after the
  V_alpha → V_beta snake-case housekeeping
  (`ontologyImage` → `ontology_image`).
- **Status:** `drafted`

## Summary

`ontology_image` carries a labelled image of an anatomical or
functional region (e.g., a brain-atlas slice for a given Allen CCF
region). did_v1 stored the ontology identity as a pair of `char` fields
(`ontology_name` + `ontology_region`); V_delta collapses them into a
single `region` field of `ontology_term` composite type. The image
file reference (`ontology_image_file`) is unchanged.

## Field mapping

Beyond these fields, the universal renames listed in
[`_universal_renames.md`](_universal_renames.md) apply (snake-case
classname `ontologyImage` → `ontology_image`, ontology-annotation
reshape, superclass-reference reshape, class-scoped property block
keyed by `ontology_image`).

| did_v1 field | V_delta field | Transformation | Notes |
|---|---|---|---|
| `ontologyImage.ontology_name` (char) | `ontology_image.region.node` | composed into `ontology_term` | CURIE (e.g., `allen_ccf_v3:12345`). See "Transformations in detail". |
| `ontologyImage.ontology_region` (char) | `ontology_image.region.name` | composed into `ontology_term` | Human-readable label snapshot. |
| — | `ontology_image.region` (ontology_term) | new composite field | Created by composing the two did_v1 chars above. `mustBeNonEmpty: true`. |
| `_file[ontology_image_file]` | `file[ontology_image_file]` | identity (declaration); underscore-prefix stripped from the structural key | See [`_files.md`](_files.md) for the generic file-reference rules. |
| `depends_on[element_id]` | `depends_on[element_id]` | identity | |

## Transformations in detail

- **Collapse two coordinated chars into one `ontology_term`.** Same
  pattern as `probe_location` and `treatment`. did_v1's `ontology_name`
  (the ontology CURIE-or-name) and `ontology_region` (the
  human-readable region label) merge into V_delta's `region`
  composite:

      region = {
          "node": <did_v1 ontologyImage.ontology_name>,
          "name": <did_v1 ontologyImage.ontology_region>
      }

  V_delta's schema declares this field `mustBeNonEmpty: true`. Migrated
  documents that have empty inputs for either part fail validation
  until the missing value is supplied — see "Open questions".

- **Class name normalization.** `ontologyImage` (V_alpha) →
  `ontology_image` (V_beta and later) is a snake-case rename. The
  migrator rewrites `document_class.class_name` and the property-block
  key.

- **Document-instance shape.** V_delta uses class-scoped property
  blocks; the `region` value lives at `ontology_image.region`.

- **File reference.** The schema-level `_file` array (V_alpha) is
  renamed `file` and its inner entries lose the underscore prefix
  (`_name` → `name`, `_documentation` → `documentation`). The
  `ontology_image_file` slot itself is unchanged. Per-document
  file-reference values follow [`_files.md`](_files.md).

## Default values for new fields

V_delta introduces no required field on this class beyond what did_v1
documents already supply, modulo the `mustBeNonEmpty: true` tightening
on `region` (which is a stricter validation of an existing input, not
a new field).

## Worked example

### Before (did_v1)

```json
{
    "document_class": {
        "class_name": "ontologyImage",
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
        "name":       "ccf_v1_slice_42",
        "datestamp":  "2024-06-01T12:00:00.000Z"
    },
    "ontologyImage": {
        "ontology_name":   "allen_ccf_v3:12345",
        "ontology_region": "primary visual cortex"
    }
}
```

### After (V_delta)

```json
{
    "document_class": {
        "class_name": "ontology_image",
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
        "name":       "ccf_v1_slice_42",
        "datestamp":  "2024-06-01T12:00:00.000Z"
    },
    "ontology_image": {
        "region": {
            "node": "allen_ccf_v3:12345",
            "name": "primary visual cortex"
        }
    }
}
```

## File handling

`ontology_image` carries one file slot, `ontology_image_file`, declared
at the schema level. The slot's name and semantics are unchanged
between did_v1 and V_delta; only the underscore-prefix stripping
applies to the surrounding structural keys. The per-document file
reference itself follows the generic rules in
[`_files.md`](_files.md). No `ontology_image`-specific file-handling
rules apply.

## Open questions

- **TODO-domain:** the V_delta schema requires `region` to be
  non-empty. did_v1 made `ontology_region` optional (`_mustBeNonEmpty:
  false`). Migrated documents that lack a region label cannot satisfy
  the V_delta constraint as written. Options: (a) tighten by demoting
  to `mustBeNonEmpty: false` to preserve migration completeness; (b)
  populate `region.name` from a fallback (e.g., the resolved
  CURIE-registry label for `region.node`) and emit a warning; (c)
  reject such documents and ask the producer to supply the label. The
  conversion-engine choice needs a domain decision before the V1
  freeze.
- **TODO-domain:** are did_v1 `ontology_name` values guaranteed to be
  well-formed CURIEs (e.g., `allen_ccf_v3:12345`), or do some carry
  just an ontology label such as `Allen CCF v3` with the numeric ID
  on a different field? If the latter, see the parallel question in
  [`probe_location.md`](probe_location.md).

## Cross-references

- General file-handling rules: [`_files.md`](_files.md)
- Universal did_v1 → V_delta renames: [`_universal_renames.md`](_universal_renames.md)
- V_delta schema file: [`schemas/V_delta/stable/ontology_image.json`](../../stable/ontology_image.json)
- Sibling ontology-annotation type: [`ontology_label.md`](ontology_label.md)
- Same two-char-to-`ontology_term` pattern:
  [`probe_location.md`](probe_location.md),
  [`treatment.md`](treatment.md)
