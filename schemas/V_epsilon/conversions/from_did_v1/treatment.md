# Conversion: did_v1 → V_delta — `treatment`

## Identity

- **V_delta `class_name`:** `treatment`
- **V_delta tier:** `stable`
- **V_delta schema path:** `schemas/V_delta/stable/treatment.json`
- **did_v1 source:** legacy NDI/DID `treatment` document type
  (`_classname: "treatment"`). Schema-shape ancestor in this repository
  is `schemas/V_alpha/treatment.json`; `schemas/V_beta/treatment.json`
  is the same shape with naming-convention housekeeping applied
  (`ontologyName` → `ontology_name`).
- **Status:** `drafted`

## Summary

`treatment` records a treatment applied to a subject (drug, stimulation,
etc.) keyed by ontology term and carrying an optional numeric value and
an optional free-form string value. did_v1 stored the ontology identity
as a pair of `char` fields (`ontologyName` + `name`); V_delta collapses
those into a single `treatment_name` field of the `ontology_term`
composite type. The `numeric_value` and `string_value` fields carry over
unchanged.

## Field mapping

Beyond these fields, the universal renames listed in
[`_universal_renames.md`](_universal_renames.md) apply (snake-case
ontology-annotation reshape, superclass-reference reshape, class-scoped
property block keyed by `treatment`).

| did_v1 field | V_delta field | Transformation | Notes |
|---|---|---|---|
| `treatment.ontologyName` (char) | `treatment.treatment_name.node` | composed into `ontology_term`; snake-case rename of the carrier field | CURIE. See "Transformations in detail". |
| `treatment.name` (char) | `treatment.treatment_name.name` | composed into `ontology_term` | Human-readable label snapshot. |
| — | `treatment.treatment_name` (ontology_term) | new composite field | Created by composing the two did_v1 chars above. |
| `treatment.numeric_value` (matrix) | `treatment.numeric_value` (matrix) | identity | |
| `treatment.string_value` (char) | `treatment.string_value` (char) | identity | |
| `depends_on[subject_id]` | `depends_on[subject_id]` | identity | |
| `depends_on[manipulation_id]` | `depends_on[manipulation_id]` | identity | |
| `depends_on[protocol_id]` | `depends_on[protocol_id]` | identity | |

## Transformations in detail

- **Collapse two coordinated chars into one `ontology_term`.** did_v1's
  `ontologyName` (the ontology CURIE-or-name) and `name` (the
  human-readable label) merge into V_delta's `treatment_name` composite:

      treatment_name = {
          "node": <did_v1 treatment.ontologyName>,
          "name": <did_v1 treatment.name>
      }

  This is the same merge rule as `probe_location` (see
  [`probe_location.md`](probe_location.md)); the *carrier* field is
  renamed from `<class>.name` to `<class>.treatment_name` so it does
  not collide with `base.name`. (Under V_delta's class-scoped property
  blocks, `base.name` and `treatment.name` would in principle be
  distinct, but renaming the carrier here makes the migrated documents
  easier to read and matches the V_gamma `class_version: 2.0.0` shape
  the V_delta schemas inherit — see `V_gamma_notes.md` § "Class-version
  bumps".)

- **camelCase → snake_case of the source field name.** did_v1's
  `ontologyName` is camelCase; the V_beta-era housekeeping snake-cased
  field names. The migrator reads the value from either spelling and
  writes it to `treatment_name.node`. See
  [`_universal_renames.md`](_universal_renames.md) for the
  cross-cutting snake_case rule.

- **`numeric_value` and `string_value` are identity passes.** Both are
  declared identically in did_v1 and V_delta (matrix and char,
  respectively). No type or semantic change.

- **Document-instance shape.** V_delta uses class-scoped property
  blocks. The three carrier fields live at `treatment.treatment_name`,
  `treatment.numeric_value`, `treatment.string_value`.

## Default values for new fields

V_delta introduces no required field on this class beyond what did_v1
documents already supply. The global `schema_version` tag lives at
`document_class.schema_version` (see `_universal_renames.md` § 10) and
is set to `"V_delta"` by the dispatcher rather than the per-class
migrator.

## Worked example

### Before (did_v1)

```json
{
    "document_class": {
        "class_name": "treatment",
        "class_version": "1.0.0",
        "superclasses": [
            { "class_name": "base", "class_version": "1.0.0" }
        ]
    },
    "depends_on": [
        { "name": "subject_id",      "document_id": "aabb1122ccdd3344_aabb1122ccdd3344" },
        { "name": "manipulation_id", "document_id": "" },
        { "name": "protocol_id",     "document_id": "" }
    ],
    "base": {
        "id":         "aabb1122ccdd3344_1122334455667788",
        "session_id": "aabb1122ccdd3344_9900aabbccddeeff",
        "name":       "isoflurane_induction",
        "datestamp":  "2024-06-01T12:00:00.000Z"
    },
    "treatment": {
        "ontologyName":  "chebi:6015",
        "name":          "isoflurane",
        "numeric_value": [2.0],
        "string_value":  "2 percent in O2"
    }
}
```

### After (V_delta)

```json
{
    "document_class": {
        "class_name": "treatment",
        "class_version": "1.0.0",
        "superclasses": [
            { "class_name": "base", "class_version": "1.0.0" }
        ]
    },
    "depends_on": [
        { "name": "subject_id",      "document_id": "aabb1122ccdd3344_aabb1122ccdd3344" },
        { "name": "manipulation_id", "document_id": "" },
        { "name": "protocol_id",     "document_id": "" }
    ],
    "base": {
        "id":         "aabb1122ccdd3344_1122334455667788",
        "session_id": "aabb1122ccdd3344_9900aabbccddeeff",
        "name":       "isoflurane_induction",
        "datestamp":  "2024-06-01T12:00:00.000Z"
    },
    "treatment": {
        "treatment_name": {
            "node": "chebi:6015",
            "name": "isoflurane"
        },
        "numeric_value": [2.0],
        "string_value":  "2 percent in O2"
    }
}
```

## File handling

This document type does not reference files. The generic file-handling
rules in [`_files.md`](_files.md) do not apply.

## Open questions

- **TODO-domain:** what is the canonical CURIE prefix family for
  treatments? Drugs typically resolve under `chebi:` or `drugbank:`;
  stimulation protocols may not have a single canonical source. The
  V_delta schema's `ontology` slot for `treatment_name` is `null`,
  leaving the choice to documents.
- **TODO-domain:** `numeric_value` is a matrix and `mustBeScalar:
  false`. Confirm whether did_v1 documents in the wild ever carry
  multi-element matrices here, or only scalars / 1-element arrays. The
  migrator should pass the value through unchanged in either case, but
  knowing the shape distribution affects downstream tooling
  assumptions.
- **TODO-domain:** the relationship between `numeric_value` /
  `string_value` and `treatment_name` is not enforced (any of the
  three can be empty). Confirm whether the V1 freeze should add a
  semantic constraint (at least one non-empty), or leave it to
  consumer policy.

## Cross-references

- General file-handling rules: [`_files.md`](_files.md)
- Universal did_v1 → V_delta renames: [`_universal_renames.md`](_universal_renames.md)
- V_delta schema file: [`schemas/V_delta/stable/treatment.json`](../../stable/treatment.json)
- Related conversions that follow the same two-char-to-`ontology_term`
  pattern: [`probe_location.md`](probe_location.md),
  [`ontology_image.md`](ontology_image.md),
  [`ontology_label.md`](ontology_label.md)
- Subclass: `treatment_drug` (still at `class_version: 1.0.0`; this
  conversion doc's rules apply to its `treatment` block).
