# Conversion: did_v1 → V_epsilon — `treatment_transfer` → `biological_transfer`

## Identity

- **V_epsilon target class:** `biological_transfer` (a
  `procedural_manipulation` subclass). `treatment_transfer` moves to
  `deprecated/`.
- **V_epsilon tier:** `draft` (`biological_transfer`); `deprecated`
  (`treatment_transfer`)
- **did_v1 source:**
  `ndi_common/schema_documents/treatment/treatment_transfer_schema.json`:
  `timestamp` (double), `clocktype`, `entity_name`,
  `entity_ontologyNode`, `method_name`, `method_ontologyNode`;
  depends_on `recipient_id` (req), `donor_id` (opt).
- **Status:** `applied-in-tooling`
  (`DID-matlab/+did2/+convert/+migrators/treatment_transfer.m`)

## Summary

A donor→recipient transfer maps to `biological_transfer`
(`Biological_Transfer_Proposal.md`). The legacy `method_*` pair lands on
the **inherited** `procedural_manipulation.procedure` (not a separate
`method`); `entity_*` becomes `entity`; the recipient becomes
`subject_id`; the donor carries forward as `donor_id`.

## Field mapping

| did_v1 field | V_epsilon field | Transformation |
|---|---|---|
| `method_name` + `method_ontologyNode` | `procedural_manipulation.procedure` | `{node: method_ontologyNode, name: method_name}` (required) |
| `entity_name` + `entity_ontologyNode` | `biological_transfer.entity` | `{node: entity_ontologyNode, name: entity_name}` (required) |
| `entity_name` | `biological_transfer.kind` | bucket: blood/plasma/serum→`blood`; cell/marrow→`cells`; graft/tissue/explant→`tissue_graft`; else→`lysate` |
| `recipient_id` | `subject_id` (inherited) | rename |
| `donor_id` | `donor_id` (added) | carried (optional) |
| `timestamp` + `clocktype` | companion `utc_reference.start` | only when `clocktype` is a global/UTC clock and `timestamp > 0`: datenum → ISO. Local-clock timing ⇒ omitted (backfill). |
| — | `procedural_manipulation.target_structure` | empty (legacy none; backfill) |
| — | `procedural_manipulation.notes` | empty |

## Default values for new fields

`kind` is assigned from `entity_name` (ambiguous ⇒ `"lysate"`, flagged).
`target_structure` empty. The transfer keeps the source `base.id`; the
companion `utc_reference` shares `base.session_id`.

## Worked example

`treatment_transfer` (recipient R, donor D, `entity_name = "blood"`,
`method_name = "blood transfusion"`, global-clock `timestamp`) →
`biological_transfer` with `subject_id = R`, `donor_id = D`,
`procedure = {NCIT:C15325, "blood transfusion"}`, `kind = "blood"`,
`entity = {UBERON:0000178, "blood"}`, and a `utc_reference` from the
datenum.

## Open questions

- `kind` bucketing from free-text `entity_name` is heuristic; ambiguous
  entries default to `lysate` and should be curator-confirmed.
- Local-clock transfers need an `epoch_relative_reference` rather than a
  `utc_reference`; deferred (current migrator omits timing for those).

## Cross-references

- `Biological_Transfer_Proposal.md`, `Boundary_Mapping_Proposal.md` §4a
- Migrator: `DID-matlab/src/did/+did2/+convert/+migrators/treatment_transfer.m`
- General file-handling rules: [`_files.md`](_files.md)
