# Conversion: did_v1 → V_epsilon — `treatment_drug` → `injection`

## Identity

- **V_epsilon target class:** `injection` (kind = `"drug"`).
  `treatment_drug` moves to `deprecated/`.
- **V_epsilon tier:** `draft` (`injection`); `deprecated` (`treatment_drug`)
- **did_v1 source:**
  `ndi_common/schema_documents/treatment/treatment_drug_schema.json`:
  `location_ontologyName`, `location_name`, `mixture_table` (CSV),
  `administration_onset_time` (ISO), `administration_offset_time` (ISO),
  `administration_duration` (days); depends_on `subject_id` (req).
- **Status:** `applied-in-tooling`
  (`DID-matlab/+did2/+convert/+migrators/treatment_drug.m`)

## Summary

A pharmacological administration maps to the `injection` family with
`kind = "drug"` (`Injection_Proposal.md`). Active fan-out: produces the
`injection` plus a companion `utc_reference` when an onset time exists.

## Field mapping

| did_v1 field | V_epsilon field | Transformation |
|---|---|---|
| `mixture_table` | `pharmacological_manipulation.mixture` | CSV `ontologyName,name,value,ontologyUnit,unitName` → records `{chemical:{node,name}, amount:concentration{source_unit,source_value}}`. Empty ⇒ one blank backfill record (mixture is required non-empty). |
| `location_ontologyName` + `location_name` | `injection.target_structure[0]` | `{node,name}` when present; else empty array |
| `administration_onset_time` | companion `utc_reference.start` | ISO timestamp |
| `administration_offset_time` | companion `utc_reference.end` | ISO timestamp (interval) |
| `administration_duration` | — | dropped; onset/offset interval is canonical |
| `subject_id` | `subject_id` (inherited) | carried |
| — | `injection.kind` | constant `"drug"` |
| — | `injection.volume` | source-only blank composite (legacy has none; backfill) |
| — | `injection.route` | blank ontology_term (legacy has none; backfill) |

## Default values for new fields

`kind = "drug"`; `volume`/`route` present but source-empty for curator
backfill. The injection keeps the source `base.id`; the companion
`utc_reference` mints a fresh id and shares `base.session_id`. The
injection's `time_reference_1` depends_on points at the companion; when
no onset time exists the dependency is omitted (backfill).

## Worked example

`treatment_drug` with a one-row `mixture_table` for ketamine and
`administration_onset_time = "2024-05-15T09:22:00Z"` →
`injection{kind:"drug"}` with that chemical in `mixture`, plus a
`utc_reference{start:"2024-05-15T09:22:00Z"}` wired as `time_reference_1`.

## Open questions

- Legacy `treatment_drug` records dose/concentration only inside
  `mixture_table`; rows without a unit leave concentration canonicals
  empty (source preserved). `route` and `volume` are not in the legacy
  shape and always need curator backfill.

## Cross-references

- `Injection_Proposal.md` (Migration §)
- Migrator: `DID-matlab/src/did/+did2/+convert/+migrators/treatment_drug.m`
- General file-handling rules: [`_files.md`](_files.md)
