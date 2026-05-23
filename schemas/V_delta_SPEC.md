# V_delta_SPEC.md — DID/NDI Document Schema Format (V_delta)

## Purpose

V_delta is the next iteration of the DID/NDI schema set. It is still a
sandbox (like V_gamma), iterated against until the set is ready to be
promoted to a stable `V1`. When that promotion happens, V_delta's contents
will be copied to `schemas/V1/` and frozen.

This document specifies the **differences** between V_gamma and V_delta.
For everything not listed here, the V_gamma specification
([`V_gamma_SPEC.md`](V_gamma_SPEC.md)) is authoritative.

The V_delta differences are organizational and have minimal effect on
the JSON shape of schema files or document instances. Schema content
inside V_delta begins as a verbatim copy of V_gamma; substantive content
changes will land in follow-up PRs and be recorded in
[`V_delta_notes.md`](V_delta_notes.md).

---

## Differences from V_gamma

### 1. Tiered directory layout

V_gamma uses a single flat directory: `schemas/V_gamma/<class_name>.json`.

V_delta groups schemas by **maturity tier** under the set-version root:

```
schemas/V_delta/
├── stable/                 ← canonical, change-controlled schemas
│   └── <class_name>.json
├── draft/                  ← work-in-progress, may break between commits
│   └── <class_name>.json
├── deprecated/             ← scheduled for removal in a future set version
│   └── <class_name>.json
├── examples/               ← worked example document instances
├── conversions/            ← migration documentation
│   └── from_did_v1/        ← did_v1 → V_delta conversion docs
│       ├── _index.md
│       ├── _TEMPLATE.md
│       ├── _files.md
│       └── <class_name>.md
├── index.json              ← authoritative list of schemas with tier, path, class_version
├── V_delta_SPEC.md         ← (this file)
└── V_delta_notes.md
```

The tier-folder placement of a schema must agree with its
`document_class.maturity_level` field (see §3). The tier folder is a
projection of the field; the field is authoritative.

`stable`, `draft`, and `deprecated` are **reserved names** at the
V_delta root and may not be used as `class_name`s.

### 2. `index.json` is the resolution source of truth

V_delta introduces `schemas/V_delta/index.json` as the canonical list of
schemas in the set. Each entry records:

- `class_name`
- `tier` (`stable` | `draft` | `deprecated`)
- `class_version`
- `maturity_level` (as declared in the schema file)
- `superclasses` (by `class_name`)
- `path` (relative to the repo root)
- `is_meta` (true for meta-schemas and registries that are not document
  classes)

Consumer tooling resolves schemas by `class_name` via `index.json`. The
superclass reference object in V_delta is `{"class_name": "<name>"}` —
the `schema` path key that existed in V_gamma is removed. The meta-schema
enforces this. There is no `$NDISCHEMAPATH` path-walking fallback.

### 3. New `maturity_level` vocabulary

V_gamma allowed `maturity_level` ∈ `{"work_in_progress", "mature"}`.

V_delta replaces this with `{"stable", "draft", "deprecated"}`. The
value of a schema's `maturity_level` field must equal the name of the
tier folder it lives in (`stable/`, `draft/`, or `deprecated/`). Schemas
do not know where they live on disk; the field is the metadata they
carry to communicate that status to consumers. Disk layout is a
projection of the field for human navigation.

The meta-schema (`did_schema_meta.json`) enforces the enum.

Migration mapping for content carried over from V_gamma:

| V_gamma `maturity_level` | V_delta target |
|---|---|
| `"mature"` | `"stable"` |
| `"work_in_progress"` | `"stable"` (default placement — re-tier to `draft` or `deprecated` per domain review) |
| — | `"deprecated"` (new, no V_gamma analog) |

### 4. `schema_version` on document instances

V_delta tags every document instance with a `schema_version` string
naming the schema set under which the document is interpreted.
Established values:

- `"V_delta"` — documents authored against V_delta
- `"did_v1"` — legacy DID/NDI documents predating the V_alpha→V_gamma
  iterations; this value is used by the `conversions/from_did_v1/`
  migration path to recognize incoming legacy documents

`schema_version` is the version of the overarching schema set the
document was authored against, not a payload field belonging to any
particular class. It therefore lives at `document_class.schema_version`
on document instances, alongside class-level metadata (`class_name`,
`class_version`, `superclasses`) — never as a `base` field. It is not
declared in any per-class `fields` array; the validator treats it as a
structural key on the `document_class` block. Enumerated values are
authoritative in `schemas/V_delta/index.json`
(`schema_version_value`, `legacy_schema_version_values`); extend that
list as new set versions ship.

A migrated did_v1 document temporarily carrying the legacy shape may
declare `"did_v1"`; a document authored against V_delta declares
`"V_delta"`.

### 5. Conversion documentation lives alongside schemas

Migration from `did_v1` (the legacy NDI-matlab document format that has
real consumers) is documented per V_delta document type as a markdown
file under `conversions/from_did_v1/`. One file per class. The template
is `_TEMPLATE.md`, the index is `_index.md`, and generalized
file-handling rules are in `_files.md`.

Conversion **from V_gamma** is not provided. V_gamma was an internal
sandbox with no external consumers; documents authored against V_gamma
are expected to be regenerated against V_delta rather than migrated.

### 6. Field placement is used by `calculator.input_parameters`

V_delta inherits the V_gamma per-field `placement` mechanism (see
[`V_gamma_SPEC.md`](V_gamma_SPEC.md), "Field placement" under "Field
Definition Object"). V_delta is the first set version to make use of
it: the abstract `calculator` superclass declares
`input_parameters` with `"placement": "concrete_class"`, so concrete
calculator subclasses (`simple_calc`, `tuningcurve_calc`,
`oridirtuning_calc`, `contrast_tuning_calc`,
`contrast_sensitivity_calc`, `spatial_frequency_tuning_calc`,
`speed_tuning_calc`, `temporal_frequency_tuning_calc`,
`hartley_calc`, …) carry the field as
`<subclass_class_name>.input_parameters` on instance bodies — and the
abstract `calculator` block is omitted from those bodies entirely
since it has no other declared field to host. This matches the did_v1
on-disk layout: legacy NDI calculator documents already stored
`<class>.input_parameters` on the concrete class block, so no
structural move is required during the `did_v1 -> V_delta` conversion.
This also makes the inheritance-driven required-field contract read
naturally — "every `calculator` subclass instance must supply
`input_parameters`" is satisfied by a field on the subclass block,
not a phantom `calculator` block.

---

## Promotion to V1

When V_delta is ready for stable release:

1. Copy `schemas/V_delta/` to `schemas/V1/` (literally a directory copy).
2. Freeze `schemas/V1/` — no further content changes; subsequent
   iterations happen in a new set-version directory (V2 or
   V_epsilon-then-V2, depending on convention).
3. Replace the `"V_delta"` value in `schema_version` fields and
   `index.json` with `"V1"` (or `"v1_0_0"` if numeric versioning is
   adopted).
4. Tag the repository.
