# Conversion: did_v1 → V_epsilon — `stimulus_bath` (re-rooted under `bath`)

## Identity

- **V_epsilon target class:** `stimulus_bath` (v2.0.0), now a concrete
  subclass of `bath` (← `pharmacological_manipulation` ← `manipulation`
  ← `subject_interaction`). Moved from `stable/` to `draft/`.
- **V_epsilon tier:** `draft`
- **did_v1 source:**
  `ndi_common/schema_documents/stimulus/stimulus_bath_schema.json`:
  `location` (structure), `mixture_table` (CSV); superclasses
  `[base, epochid]`; depends_on `stimulus_element_id` (req).
- **Status:** `applied-in-tooling`
  (`DID-matlab/+did2/+convert/+migrators/stimulus_bath.m`)

## Summary

V_epsilon re-roots `stimulus_bath` into the pharmacological-manipulation
tree. The legacy `epochid` superclass is dropped (timing now lives in
`time_reference` documents). Fields redistribute across the inherited
blocks; the migration is 1:1 (no companion) because the legacy class
carries neither a subject nor a wall-clock time.

## Field mapping

| did_v1 field | V_epsilon field | Transformation |
|---|---|---|
| `mixture_table` | `pharmacological_manipulation.mixture` | CSV → records `{chemical, amount:concentration}`; empty ⇒ one blank backfill record |
| `location` | `bath.location` | `{ontologyNode→node, name}` |
| — | `bath.kind` | constant `"drug"` default (legacy has no kind; backfill vehicle/wash/tracer) |
| `stimulus_element_id` | `stimulus_element_id` | carried |
| (epochid fields) | — | dropped; timing → `time_reference` (backfill) |
| — | `subject_id` | omitted — legacy carries no subject; backfill |

## Default values for new fields

`bath.kind = "drug"`; `stimulus_bath` block is empty (no own fields).
`subject_id` and `time_reference` dependencies are omitted (the did2
validator enforces field/block shape, not depends_on cardinality), and
flagged for curator backfill.

## Worked example

`stimulus_bath` (location LGN, one-row `mixture_table` for a blocker,
`stimulus_element_id → E`) → `stimulus_bath` v2 with `mixture` on the
`pharmacological_manipulation` block, `bath.location = LGN`,
`bath.kind = "drug"`, and `stimulus_element_id → E`.

## Open questions

- `bath.kind` defaulting to `"drug"` is a heuristic; wash/vehicle baths
  need curator confirmation.
- Whether `stimulus_bath` should also gain a `stimulus_presentation`
  link (vs the bare `stimulus_element_id`) is open in `Bath_Proposal.md`.

## Cross-references

- `Bath_Proposal.md`, `Injection_Proposal.md`
- Migrator: `DID-matlab/src/did/+did2/+convert/+migrators/stimulus_bath.m`
- General file-handling rules: [`_files.md`](_files.md)
