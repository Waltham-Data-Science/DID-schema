> **V_eta retarget.** → `dose_manipulation`/`formulation_manipulation` (virus on the chemical term; titer/dilution in the composite); site → Path S. Not `injection (kind:virus)`.

# `virus_injection` → `injection` (`kind: "virus"`)  [Brainstorm J]

Status: **drafted**

`virus_injection` is **deprecated** in V_eta and folds into `injection`
(a `pharmacological_manipulation`). Serotype/identity ride in the mixture
ontology term; dilution rides in its concentration amount.

## Mapping (per document, 1 → 2)

| did_v1 `virus_injection` | V_eta | Transformation |
|---|---|---|
| (class) `virus_injection` | (class) `injection`, `injection.kind = "virus"` | class fold |
| `virus_OntologyName` / `virus_name` | `mixture[1].chemical` | ontology_term |
| `dilution` | `mixture[1].amount` | concentration (`source_value`, `source_unit="dilution"`) |
| `diluent_OntologyName` / `diluent_name` | `mixture[2].chemical` (if named) | ontology_term |
| `virusLocation_OntologyName` / `virusLocation_name` | `injection.target_structure[]` | ontology_term |
| `virus_AdministrationDate` / `virus_AdministrationPND` | (timing) | ordinal `session_relative_reference` (`during`) for now; UTC/developmental refinement is a follow-up |
| `subject_id` | `subject_id` | carried |
| `base.*` | `base.*` | carried (same id) |

The second emitted document is the shared `session_relative_reference`
anchor. `injection.volume` / `route` are emitted blank (curator-fillable).

## Engine
Routed by `did2.convert.v1_to_v2` under `TargetVersion='V_eta'` to
`+did2/+convert/+migrators_e/virus_injection.m`. Default `V_eta` target
is unaffected.
