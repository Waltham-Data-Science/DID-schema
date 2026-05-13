# Conversion: did_v1 → V_delta — `<class_name>`

> Copy this file to `<class_name>.md` (one file per V_delta document type that
> has a `did_v1` analog) and fill in every section. Sections that genuinely do
> not apply should be retained with the text `N/A` so reviewers can see they
> were considered, not skipped.

## Identity

- **V_delta `class_name`:** `<class_name>`
- **V_delta tier:** `stable` | `draft` | `deprecated`
- **V_delta schema path:** `schemas/V_delta/<tier>/<class_name>.json`
- **did_v1 source:** repo + path (or "synthesized from MATLAB class
  `<...>`")
- **Status:** `drafted` | `reviewed` | `applied-in-tooling` | `frozen`

## Summary

One or two sentences. What is this document type, and what is the
high-level shape of the change between did_v1 and V_delta? If there is no
change, say so.

## Field mapping

Use one row per field. Cover every field in both the did_v1 source and the
V_delta target — including dropped fields (V_delta column blank) and new
fields (did_v1 column blank).

| did_v1 field | V_delta field | Transformation | Notes |
|---|---|---|---|
| `<old>` | `<new>` | rename | |
| `<old>` | `<new>` | type change: `<from>` → `<to>` | Validation rules below |
| `<old>` | — | dropped | Reason |
| — | `<new>` | new field | Default value: `<...>` |
| `<old>` | `<new>` | identity | |

## Transformations in detail

For any row above whose transformation is non-trivial (type change, unit
conversion, structural reshape, value mapping), describe the rule here in
enough detail that a reader could implement it without consulting the
author. Cite the relevant spec section if applicable.

## Default values for new fields

If V_delta introduces required fields that did_v1 documents do not carry,
list the default each migrated document gets, and the reasoning. Distinguish
between "constant default" and "computed from other fields."

## Worked example

A minimal but realistic did_v1 document and the V_delta document it converts
to. These pairs double as unit-test fixtures — keep them small enough to
read by eye.

### Before (did_v1)

```json
{
  "schema_version": "did_v1",
  ...
}
```

### After (V_delta)

```json
{
  "schema_version": "V_delta",
  "document_class": { "class_name": "<class_name>", "class_version": "..." },
  ...
}
```

## File handling

If this document type carries or references files (binary blobs, external
paths, hash-addressed content), describe how those are handled on migration.
For anything that follows the generic rules, link to `_files.md` instead of
restating them here. Document only the type-specific behavior.

## Open questions

Anything still undecided. Pose as concrete questions, not vague concerns.
Each question should be resolvable by a domain owner without needing to
re-read this whole doc.

## Cross-references

- Related document types whose conversions interact with this one:
- did_v1 source-of-truth path(s):
- V_delta schema file:
- General file-handling rules: [`_files.md`](_files.md)
