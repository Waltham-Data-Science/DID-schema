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

Consumer tooling SHOULD resolve schemas by `class_name` via `index.json`
rather than by literal `$NDISCHEMAPATH/...` path. Resolution by path
remains supported for backwards compatibility during the V_delta sandbox
phase but is expected to be retired before V1.

### 3. Expanded `maturity_level` values

V_gamma allows `maturity_level` ∈ `{"work_in_progress", "mature"}`.

V_delta expands this to `{"stable", "draft", "deprecated"}` with the
following intended mapping for migrated content:

| V_gamma `maturity_level` | V_delta target |
|---|---|
| `"mature"` | `"stable"` |
| `"work_in_progress"` | `"draft"` |
| — | `"deprecated"` (new, no V_gamma analog) |

The initial scaffolding commit copies schemas verbatim from V_gamma and
places all of them under `stable/` regardless of their original
`maturity_level` value, on the understanding that the V_gamma schemas
represent the working set of types intended to reach V1. Re-tiering and
updates to the in-schema `maturity_level` field will land as follow-up
PRs and are tracked in `V_delta_notes.md`.

### 4. `schema_version` field on document instances (planned)

V_delta will add a required `schema_version` field to document instances,
inherited via `base`, carrying the set-version string of the schema set
under which the document was authored. Established values:

- `"V_delta"` — documents authored against V_delta
- `"did_v1"` — legacy DID/NDI documents predating the V_alpha→V_gamma
  iterations; this value is used by the `conversions/from_did_v1/`
  migration path to recognize incoming legacy documents

This field is **planned**, not yet present in the schemas in the initial
scaffolding commit. The schema change will land as a follow-up PR; until
then, the existing V_gamma document instance shape applies.

### 5. Conversion documentation lives alongside schemas

Migration from `did_v1` (the legacy NDI-matlab document format that has
real consumers) is documented per V_delta document type as a markdown
file under `conversions/from_did_v1/`. One file per class. The template
is `_TEMPLATE.md`, the index is `_index.md`, and generalized
file-handling rules are in `_files.md`.

Conversion **from V_gamma** is not provided. V_gamma was an internal
sandbox with no external consumers; documents authored against V_gamma
are expected to be regenerated against V_delta rather than migrated.

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
