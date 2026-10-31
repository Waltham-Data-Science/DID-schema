> **V_eta retarget (D4).** → a `term_manipulation` for the transfer act **+ a provenance `directed_relation`** (recipient material `derived_from`/`sample_of` donor). No `biological_transfer` class; the donor is a relation, not a dependency.

# `treatment_transfer` → `biological_transfer`  [Brainstorm J]

Status: **drafted**

`treatment_transfer` is **deprecated** in V_eta and folds into
`biological_transfer` (a `manipulation` that earns its class via the
`donor_id` dependency).

## Mapping (per document, 1 → 2)

| did_v1 `treatment_transfer` | V_eta | Transformation |
|---|---|---|
| (class) `treatment_transfer` | (class) `biological_transfer` | class fold |
| `recipient_id` (depends_on) | `subject_id` | the recipient is the subject |
| `donor_id` (depends_on) | `biological_transfer` donor dependency (`donor_id`) | carried |
| `entity_ontologyNode` / `entity_name` | spine `variable` (the transferred material) | ontology_term |
| `method_ontologyNode` / `method_name` | spine `variable` (the transfer act) / spine `method` | ontology_term |
| `method_name` | `biological_transfer.kind` | char (fallback `"transfer"`) |
| `timestamp` / `clocktype` | (timing) | ordinal `session_relative_reference` (`during`) for now; UTC/event refinement is a follow-up |
| `base.*` | `base.*` | carried (same id) |

The second emitted document is the shared `session_relative_reference`
anchor (`subject_interaction` requires a `time_reference`).

## Engine
Routed by `did2.convert.v1_to_v2` under `TargetVersion='V_eta'` to
`+did2/+convert/+migrators_e/treatment_transfer.m`. Default `V_eta`
target is unaffected.
