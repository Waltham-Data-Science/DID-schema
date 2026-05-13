# V_delta schemas

The `V_delta/` directory is the working set-version directory for the
sandbox iteration that follows V_gamma. Like V_gamma, V_delta is a
sandbox: contents are expected to change in place during this phase,
and consumers should not pin to V_delta as a stable target. The set
will be copied to `schemas/V1/` and frozen when ready (see
`V_delta_SPEC.md` § "Promotion to V1").

This notes file tracks V_delta's status and the open follow-ups that
will land as separate PRs.

## What V_delta changes versus V_gamma

The substantive differences are listed in `V_delta_SPEC.md`. In summary:

1. **Tiered directory layout** — `stable/`, `draft/`, `deprecated/`,
   plus `examples/` and `conversions/`.
2. **`index.json`** as the resolution source of truth.
3. **Expanded `maturity_level` values** — `stable` / `draft` /
   `deprecated`.
4. **`schema_version` field on document instances** (planned, not yet
   in the schemas).
5. **Conversion docs from `did_v1`** colocated with the schemas.

Schema *content* in V_delta begins as a verbatim copy of V_gamma. The
substantive schema content changes will land in follow-up PRs.

## Initial state

- All 88 V_gamma document-class schemas were copied verbatim into
  `V_delta/stable/`.
- The three V_gamma metadata files (`CURIE_lookups_meta.json`,
  `did_schema_meta.json`, `ndi_reserved_keys.json`) were copied verbatim
  into `V_delta/stable/` as well; they are flagged `is_meta: true` in
  `index.json`. A later PR may move them to a `_meta/` sibling folder.
- `draft/`, `deprecated/`, and `examples/` are empty (`.gitkeep`).
- `conversions/from_did_v1/` contains scaffolding only — `_TEMPLATE.md`,
  `_index.md`, `_files.md`. Per-type conversion docs are not yet
  written.
- `index.json` enumerates all 91 stable-tier entries.

## Open follow-ups (separate PRs)

### Schema content

- **Update `maturity_level` field values** in the copied schemas from
  `"work_in_progress"` / `"mature"` to `"stable"` / `"draft"` /
  `"deprecated"` to match V_delta's vocabulary, and re-tier (move
  between folders) any schema whose current `stable/` placement is
  wrong. Currently all schemas are placed in `stable/` as a default;
  this needs domain review.
- **Add the `schema_version` field** to `base.json` (and therefore to
  every inheriting document type) as a required `char` field with
  enumeration `["did_v1", "V_delta"]` (extend as new set versions are
  added).
- **Reconcile `$NDISCHEMAPATH` references in `superclasses`.** The
  V_gamma schema files use `$NDISCHEMAPATH/<path>/schema.json`-style
  references (e.g., `$NDISCHEMAPATH/base/schema.json`) which do not
  match V_gamma's documented flat layout, and will not match V_delta's
  tiered layout either. Either rewrite these to reflect the V_delta
  layout, or — preferred — drop the `schema` path key entirely and let
  resolution proceed via `class_name` + `index.json` lookup. This is a
  V_delta SPEC decision; see `V_delta_SPEC.md` § 2.

### Aggregation

- **Aggregate the ~10 additional mature document types** that currently
  live in other repos (e.g., NDI-matlab) into `V_delta/stable/`. To be
  handled in a separate session with access to those source repos.

### Conversion content

- **Populate `conversions/from_did_v1/`** with one markdown file per
  V_delta document type that has a `did_v1` analog. Use `_TEMPLATE.md`.
  Update `_index.md` to track status as docs are written and reviewed.
- **Fill in `_files.md`** with the real generalized file-handling rules
  (currently a TODO-marked skeleton).

### CI

- **Add an `index.json` consistency check** that:
  - Asserts every schema file under `V_delta/<tier>/` appears in
    `index.json` and vice versa.
  - Asserts uniqueness of `class_name` across the set (excluding
    `is_meta` entries).
  - Asserts that the tier folder matches the schema's
    `maturity_level` field (once §"Schema content" above lands).
  - Rejects schema files placed at `V_delta/` root or in
    `examples/` / `conversions/` (those are not schema locations).
- **Add a conversion-doc-presence check** that every `stable/` class
  with a `did_v1` ancestor has a corresponding `conversions/from_did_v1/`
  markdown file (or an explicit `_no_conversion_needed` marker).

### Tooling

- **Update consumer tooling** (DID-matlab and others) to resolve
  schemas via `index.json` rather than path-walking, so the tier-folder
  reorganization doesn't break loaders.
