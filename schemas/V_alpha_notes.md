# V_alpha schemas

The `V_alpha/` directory holds the original (pre-spec) DID/NDI schema files
kept for historical reference and to support migration of existing documents.
These files use the older flat-directory layout (one JSON per document type at
the top of `V_alpha/`), not the per-type directory layout with `schema.json`
described in `REPO_SPEC.md`. They are **not** loaded by the meta-schema test
suite.

## Status

V_alpha schemas are **legacy**. New document types should be added under
`schemas/` following the layout in `REPO_SPEC.md` (a directory per document
type containing a `schema.json` that conforms to the meta-schema). The V_alpha
files will remain in the repo until migration to the current format is
complete, at which point the directory will be removed.

Do not add new document types to `V_alpha/`.

## Deprecated / removed document types

The following V_alpha document types have been removed because they are no
longer used and were not migrated to the current schema format:

- `animalsubject` — animal-specific subject metadata (scientific name,
  GenBank common name). Superseded; subject metadata is now carried by
  `subject` and its successors (see `Ideas.md` for the planned
  `subject_identifier` split).
- `subjectmeasurement` — ad-hoc subject measurements stored as
  `(measurement, value, measurement_datestamp)` triples. Superseded by
  treatment / measurement document types in the current schema set.

If you are migrating existing documents of these types, map them onto the
appropriate current-format document type rather than reintroducing the old
schema.
