# Conversion: did_v1 → V_epsilon — `virus_injection` → `injection`

## Identity

- **V_epsilon target class:** `injection` (kind = `"virus"`).
  `virus_injection` moves to `deprecated/`.
- **V_epsilon tier:** `draft` (`injection`); `deprecated` (`virus_injection`)
- **did_v1 source:**
  `ndi_common/schema_documents/treatment/virus_injection_schema.json`:
  `virus_OntologyName`, `virus_name`, `virusLocation_OntologyName`,
  `virusLocation_name`, `virus_AdministrationDate` (YYYY-MM-DD),
  `virus_AdministrationPND`, `dilution`, `diluent_OntologyName`,
  `diluent_name`; depends_on `subject_id` (req).
- **Status:** `applied-in-tooling`
  (`DID-matlab/+did2/+convert/+migrators/virus_injection.m`)

## Summary

A viral-vector administration maps to `injection` with `kind = "virus"`
(`Injection_Proposal.md`, resolving the earlier "subclass under
biological_transfer" sketch). The construct becomes a `mixture` entry;
serotype is encoded in the construct ontology node, not a separate field.

## Field mapping

| did_v1 field | V_epsilon field | Transformation |
|---|---|---|
| `virus_OntologyName` + `virus_name` | `pharmacological_manipulation.mixture[1].chemical` | `{node,name}` |
| `dilution` | `mixture[1].amount` | source-only `{source_unit:"dilution_factor", source_value:<dilution>}` (legacy has no titer) |
| `diluent_OntologyName` + `diluent_name` | `mixture[2]` | second record when present; `amount` blank |
| `virusLocation_OntologyName` + `virusLocation_name` | `injection.target_structure[0]` | `{node,name}` |
| `virus_AdministrationDate` | companion `utc_reference.start` (approximate) | date-only ⇒ `is_approximate = true` |
| `virus_AdministrationPND` | — | postnatal day; not timing-convertible without DOB; backfill |
| `subject_id` | `subject_id` (inherited) | carried |
| — | `injection.kind` | constant `"virus"` |
| — | `injection.volume` / `route` | source-empty (legacy has none; backfill) |

## Default values for new fields

`kind = "virus"`; `volume`/`route` source-empty. The injection keeps the
source `base.id`; the companion `utc_reference` shares `base.session_id`.

## Worked example

`virus_injection` (AAV construct, `dilution = 0.5`,
`virus_AdministrationDate = "2021-05-01"`, location "primary visual
cortex") → `injection{kind:"virus"}` with the construct in `mixture`
(amount `dilution_factor 0.5`), `target_structure` = the location, and an
approximate `utc_reference{start:"2021-05-01"}`.

## Open questions

- Real `virus_injection` carries `dilution` (not titer); it is preserved
  as a labelled source-only amount. Titer/volume/route need backfill.
- Serotype → ontology-node mapping is a curator lookup (not mechanical).

## Cross-references

- `Injection_Proposal.md` (Migration §; Example 4)
- Migrator: `DID-matlab/src/did/+did2/+convert/+migrators/virus_injection.m`
- General file-handling rules: [`_files.md`](_files.md)
