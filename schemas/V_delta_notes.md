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

- **`depends_on(k).document_id` (renamed from `value`).** The
  `depends_on` array entries on every V_delta document instance carry
  the keys `name` (role) and `document_id` (DID UID of the referenced
  document). This replaces the earlier V_delta draft choice of `value`,
  which was generic but uninformative — every entry's value in practice
  always is a `did_uid` referring to another document. The rename lets
  the field name signal its semantics. V_alpha → V_delta migration in
  `did2.convert.universalRenames` now produces `document_id` (was
  `value`); existing V_delta corpora with `value` are accepted by the
  universal-rename pass and converted forward. See
  `ndi_reserved_keys.json` for the registry entry.
- **`maturity_level` values updated.** All 101 V_delta document-class
  schemas now declare `"maturity_level": "stable"` to match their
  current `stable/` folder placement. The meta-schema enforces the new
  `{stable, draft, deprecated}` enum. Re-tiering of specific schemas
  (moving any from `stable/` to `draft/` or `deprecated/`) remains a
  domain-review follow-up.
- **`$NDISCHEMAPATH` references removed from superclass references.**
  Superclass reference objects in V_delta are now `{"class_name": "<x>"}`
  only; the `schema` path key is gone. The meta-schema enforces the new
  shape (the legacy `schema` key is now forbidden via
  `additionalProperties: false`). Consumer tooling must resolve
  superclasses by `class_name` through `index.json`.
- ~~**Add the `schema_version` field** to `base.json` (and therefore to
  every inheriting document type) as a required `char` field with
  enumeration `["did_v1", "V_delta"]` (extend as new set versions are
  added).~~ **Done.** `schema_version` is declared on
  `schemas/V_delta/stable/base.json` as a required `char` field with
  `constraints.enum: ["did_v1", "V_delta"]`, and described in
  `V_delta_SPEC.md` § 4.

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
