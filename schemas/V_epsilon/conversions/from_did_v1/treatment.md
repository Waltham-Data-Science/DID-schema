# Conversion: did_v1 → V_epsilon — `treatment` (split)

## Identity

- **V_epsilon target classes:** `temperature_manipulation`,
  `procedural_manipulation`, `environmental_manipulation` (plus a
  companion `generic_scalar_observation` when a numeric value is
  present). `treatment` itself moves to `deprecated/`.
- **V_epsilon tier:** `draft` (targets); `deprecated` (`treatment`)
- **did_v1 source:** legacy NDI/DID `treatment`
  (`ndi_common/schema_documents/treatment_schema.json`): fields
  `ontologyName`, `name`, `numeric_value` (matrix), `string_value`;
  depends_on `subject_id` (req), `manipulation_id` (opt),
  `protocol_id` (opt).
- **Status:** `applied-in-tooling`
  (`DID-matlab/+did2/+convert/+migrators/treatment.m`)

## Summary

`treatment` is a catch-all spanning thermal, surgical/minor-procedure,
and husbandry/behavioral interventions (and a few non-manipulation
records). V_epsilon retires it by **splitting on `name`/`ontologyName`**
into the dedicated manipulation families. This is an active, fan-out
conversion: a single `treatment` becomes one manipulation document, plus
a companion observation when it carried a numeric value.

## Routing table

Dispatch on the (lowercased) `name`; first match wins. `manipulation_id`
(stale) and `protocol_id` are dropped on every branch.

| Branch test (on `name`) | Target class | Notes |
|---|---|---|
| contains `date of birth`, `non-survival`, `experiment time` | — (quarantine) | Not a manipulation; route manually to an observation / session metadata. |
| ends with `target location` **and** `string_value` is a CURIE | `procedural_manipulation` | Dab-corpus convention: `string_value` → `target_structure` (ontology_term), `name` minus the "Target Location" suffix → `procedure.name`. |
| heat / cool / cold / thermal / temperature / warm | `temperature_manipulation` | `applied_property` = {ontologyName, name}; `value` = temperature composite from `numeric_value` (source-only; unit backfill). |
| dark rear / rearing / deprivation / monocular / housing / isolation / enrichment / light cycle / diet / food–water restrict / social / training / exposure | `environmental_manipulation` | `factor` = {ontologyName, name}; `string_value` → `notes`. |
| craniotomy / durotomy / implant / lesion / surgery / eye opening / ear notch / tail clip / whisker trim / perfusion / dissection / transection / resection / enucleation / suture / blood draw / opening / procedure | `procedural_manipulation` | `procedure` = {ontologyName, name}; `string_value` → `notes`. |
| otherwise | — (quarantine) | Unresolvable; curator review queue. |

## Field mapping (per target)

| did_v1 field | target field | Transformation |
|---|---|---|
| `ontologyName` + `name` | `procedure` / `factor` / `applied_property` (ontology_term) | `{node: ontologyName, name: name}`; blank node ⇒ backfill |
| `string_value` (prose) | `.notes` (procedural/environmental) | identity |
| `string_value` (CURIE, target-location case) | `procedural_manipulation.target_structure[0]` | `{node: string_value, name: ""}` |
| `numeric_value` | companion `generic_scalar_observation.value` | source-only `{source_unit:"", source_value:<first>, approximate:true}`; consumed into `temperature_manipulation.value` on the thermal branch |
| `subject_id` | `subject_id` (inherited) | carried |
| `manipulation_id` | — | dropped (stale) |
| `protocol_id` | — | dropped (tier-level commonality, issue #8 Option C) |
| — | `time_reference_#` | **omitted** — legacy carries no timing; curator backfill |

## Default values for new fields

- `temperature_manipulation`/`scalar_manipulation` blocks: `notes` from
  `string_value`; `target_structure` empty (backfill).
- The companion observation gets a fresh `base.id` and the source's
  `base.session_id`; the primary keeps the source's `base.id`.

## Worked example

did_v1 `treatment` (`name = "Treatment: craniotomy"`,
`string_value = "5 mm window, left hemisphere"`) →
`procedural_manipulation` with `procedure = {node:"NCIT:C15329",
name:"Treatment: craniotomy"}`, `notes = "5 mm window, left hemisphere"`,
`target_structure = []`, and `depends_on.subject_id` carried.

## Open questions

- The keyword routing lists are heuristic and intended to run
  report-only first against each corpus before rewrite (per
  `Procedural_Manipulation_Proposal.md`). Bottom out per-corpus before
  promoting `treatment` to deletion.
- Non-manipulation records (DOB, experiment time) currently quarantine;
  a dedicated observation/metadata mapping is a follow-up.

## Cross-references

- `Procedural_Manipulation_Proposal.md`, `Environmental_Manipulation_Proposal.md`,
  `Thermal_Manipulation_Proposal.md`, `Boundary_Mapping_Proposal.md` §5
- Migrator: `DID-matlab/src/did/+did2/+convert/+migrators/treatment.m`
- General file-handling rules: [`_files.md`](_files.md)
