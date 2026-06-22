# `treatment_drug` → `injection` (`kind: "drug"`)  [Brainstorm E]

Status: **drafted**

`treatment_drug` is **deprecated** in V_epsilon and folds into `injection`
(a `pharmacological_manipulation`).

## Mapping (per document, 1 → 2)

| did_v1 `treatment_drug` | V_epsilon | Transformation |
|---|---|---|
| (class) `treatment_drug` | (class) `injection`, `injection.kind = "drug"` | class fold |
| `mixture_table` (CSV) | `pharmacological_manipulation.mixture[]` (`{chemical, amount}`) | best-effort CSV parse; ≥1 record (blank if unparseable) |
| `location_ontologyNode` / `location_name` | `injection.target_structure[]` | ontology_term |
| `administration_*` times | (timing) | ordinal `session_relative_reference` (`during`) for now; UTC/event refinement is a follow-up |
| `subject_id` | `subject_id` | carried |
| `base.*` | `base.*` | carried (same id) |

The second emitted document is the shared `session_relative_reference`
anchor (`subject_interaction` requires a `time_reference`).

`injection.volume` / `injection.route` are required but absent in v1; they
are emitted as blank composites (curator-fillable). Branch/field mapping is
a **heuristic seed**, finalised in discovery mode.

## Engine
Routed by `did2.convert.v1_to_v2` under `TargetVersion='V_epsilon'` to
`+did2/+convert/+migrators_e/treatment_drug.m`. Default `V_delta` target is
unaffected.
