# `treatment_transfer` → `biological_transfer`  [Brainstorm E]

Status: **drafted**

`treatment_transfer` is **deprecated** in V_epsilon and folds into
`biological_transfer` (a `procedural_manipulation`).

## Mapping (per document, 1 → 2)

| did_v1 `treatment_transfer` | V_epsilon | Transformation |
|---|---|---|
| (class) `treatment_transfer` | (class) `biological_transfer` | class fold |
| `recipient_id` (depends_on) | `subject_id` | the recipient is the subject |
| `donor_id` (depends_on) | `biological_transfer` donor dependency (`donor_id`) | carried |
| `entity_ontologyNode` / `entity_name` | `biological_transfer.entity` | ontology_term |
| `method_ontologyNode` / `method_name` | `procedural_manipulation.procedure` | ontology_term |
| `method_name` | `biological_transfer.kind` | char (fallback `"transfer"`) |
| `timestamp` / `clocktype` | (timing) | ordinal `session_relative_reference` (`during`) for now; UTC/event refinement is a follow-up |
| `base.*` | `base.*` | carried (same id) |

The second emitted document is the shared `session_relative_reference`
anchor (`subject_interaction` requires a `time_reference`).

## Engine
Routed by `did2.convert.v1_to_v2` under `TargetVersion='V_epsilon'` to
`+did2/+convert/+migrators_e/treatment_transfer.m`. Default `V_delta`
target is unaffected.
