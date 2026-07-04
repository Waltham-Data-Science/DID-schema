# Conversion: did_v1 → V_zeta — `treatment` → manipulation tiers (Brainstorm I split)

> **Supersedes the conservative class-preserving `treatment` → `treatment` conversion** (kept in git history). Under Brainstorm I the legacy `treatment` catch-all is **retired** and **split** across the manipulation tier (and, for non-manipulation rows, out of the tier entirely). This doc is the dispatch spec for that split. Companion: [`ontology_table_row.md`](ontology_table_row.md) (the observation-tier split).

## Identity

- **Target tier:** V_zeta manipulation families (`schemas/V_zeta/stable/`).
- **did_v1 source:** legacy NDI/DID `treatment` (`_classname: "treatment"`; shape ancestor `schemas/V_alpha/treatment.json`, used here only to document the did_v1 field shape). Fields: `treatment.ontologyName` + `treatment.name` (ontology identity), `treatment.numeric_value` (matrix), `treatment.string_value` (char); `depends_on`: `subject_id`, `manipulation_id`, `protocol_id`.
- **Status:** `drafted` (dispatch table seeded from real corpora; per-term branch list finalized in discovery mode — see [Open questions](#open-questions)).
- **Cardinality:** **1 → 1** in the common case (one `treatment` → one manipulation document), **1 → 2** when a recognizable `numeric_value` spawns a companion shape-typed observation. Genuinely-not-a-manipulation rows route **out of tier** (1 → 1 into observation/annotation/session metadata).

## Summary

A `treatment` row carries an ontology identity + an optional number + optional prose. Brainstorm I reads that identity and dispatches the row to the manipulation family whose **action** it names — substance delivery → `injection`/`bath`; physical operation on the body → `procedural_manipulation`; imposed typed quantity → a `scalar_manipulation` (e.g. `temperature_manipulation`); changed condition/regime → `environmental_manipulation`. In the I model the identity itself lands on the **spine** `variable` term (the queryable "what"), the verb on the spine `method`; focal-vs-ambient structure is the spine `target_structure`; and the value/agent is the family's typed data. Rows that are not manipulations at all (date of birth, experiment time) are routed out of the manipulation tier.

## Dispatch table (on `treatment.ontologyName` branch)

First match wins; resolved against the term's ontology branch, not a string match.

| `ontologyName` branch | Destination class | Key field mapping |
|---|---|---|
| Drug / vehicle / virus / tracer / contrast **delivered by injection** (CHEBI drug branch; OBI injection) | **`injection`** (← `pharmacological_manipulation`) | identity → spine `variable`; agent → `mixture`; `numeric_value` (if volume) → `volume`; route/coords → curator backfill; `kind` ∈ {drug,virus,tracer,vehicle,contrast} |
| Substance applied **as a bath** | **`bath`** / **`stimulus_bath`** | identity → spine `variable`; agent → `mixture`; `location` from prose/backfill |
| Surgical / minor physical **operation on the body** (OBI/NCIT procedure branch — craniotomy, implant, lesion, eye-opening, ear-notch, perfusion) | **`procedural_manipulation`** | identity → spine `variable` (mirrored in the family `procedure` slot); structure → spine `target_structure`; prose → `notes` |
| **Heating / cooling** (thermal) | **`temperature_manipulation`** (← `scalar_manipulation`, `scalar_temperature`) | identity → spine `variable`; verb → spine `method`; thermal `numeric_value` → `value` (typed temperature array); focal site → spine `target_structure` (empty ⇒ ambient) |
| Other **imposed typed quantity** (applied pressure/force, field, frequency) | matching `scalar_manipulation` subclass (`pressure_manipulation`, …) or `generic_scalar_manipulation` | identity → spine `variable`; `numeric_value` → `value` |
| **Environmental / husbandry / behavioral regime** with no typed value (dark rearing, deprivation regime, social isolation, enrichment, light cycle, diet/water restriction, training) | **`environmental_manipulation`** | identity → spine `variable` (mirrored in the family `factor` slot); structure (lateralized) → spine `target_structure`; prose → `notes`; duration → bounded `time_reference` |
| **Not a manipulation** (`Treatment: Date of birth`, `Treatment: Non-survival experiment time`, …) | **out of tier** → `scalar_duration_observation`/`categorical_observation` (DOB/age) or session metadata/annotation | per [`ontology_table_row.md`](ontology_table_row.md) routing |
| Empty / unresolvable `ontologyName` | **curator review queue** (default routing **off**) | flagged, never silently forced into a residual family |

### Edge cases captured from real corpora

- **`string_value` carrying an ontology target, not prose** (the `Dab` treeshrew optogenetic-tetanus rows: `ontologyName = EMPTY:0000074`, `name = "…Target Location"`, `string_value = UBERON CURIE`). Route `string_value` → **spine `target_structure`** (as `ontology_term`), strip the "Target Location" role-suffix from the action name, register an NDIC term for the `EMPTY:` placeholder (curator backfill until then). Detection rule: `name` ends in "Target Location" **and/or** `string_value` matches a CURIE pattern.
- **`numeric_value` → companion observation.** A recognizable typed quantity that is *measured*, not the manipulation's own payload (e.g. a training-exposure duration), becomes a companion shape-typed observation (`scalar_duration_observation`, …) sharing `subject_id` + `time_reference`, with the property on its `variable`. Unrecognizable numbers are **flagged, never silently kept** (the `numeric_value` grab-bag is exactly what I retires).

## Common field mapping (all manipulation destinations)

| did_v1 field | V_zeta destination | Transformation |
|---|---|---|
| `treatment.ontologyName` + `treatment.name` | spine **`variable`** (the queryable identity), + the family's structured slot where one exists (`procedure` for procedural, `factor` for environmental, `mixture` agent for injection/bath) | collapse the two chars into one `ontology_term` (same merge rule as `probe_location`), place on `variable`, and mirror into the family slot per the dispatch table |
| — (the verb) | spine **`method`** | the action verb (apply, inject, heat, lesion); optional, defaulted from the family |
| `treatment.numeric_value` | typed `value` **or** companion observation **or** flagged | per dispatch; thermal/pressure/etc. → typed `value` (an array); measured quantity → companion; else flag |
| `treatment.string_value` | `notes` (prose) **or** spine `target_structure` (Dab case) | default prose → `notes`; CURIE/Target-Location → `target_structure` |
| `depends_on[subject_id]` | inherited spine `subject_id` | identity |
| — | inherited spine `time_reference_#` | **emits a `session_relative_reference`** document (`relation: during`, `depends_on session_id → session` from `base.session_id`) and points `time_reference_1` at it. v1 treatment rows have no epoch and (often) no UTC date, so the honest anchor is ordinal-against-the-session; `during` is the universal fallback, `at_end_of` reserved for known-terminal cases. Makes the migration **1 → 2**. |
| `depends_on[manipulation_id]` | — | **dropped** (stale in v1) |
| `depends_on[protocol_id]` | — | **dropped + flagged** for the tier-level `protocol_id` commonality (issue #8 Option C / #10) |

## Default values for new fields

- `target_structure`: `[]` (empty ⇒ whole-subject/ambient) unless recoverable.
- `variable`: required — the migrator must resolve the collapsed `ontologyName`+`name` term; unresolvable ⇒ review queue.
- `kind` (injection): inferred from the agent branch where possible; else curator backfill.
- `time_reference_#`: synthesized; required, so the migrator must produce at least one (a session-relative reference anchored to the session) and flag for widening.

## Worked example — thermal `treatment` → `temperature_manipulation`

### Before (did_v1)
```json
{
    "document_class": { "class_name": "treatment", "class_version": "1.0.0",
        "superclasses": [ { "class_name": "base", "class_version": "1.0.0" } ] },
    "depends_on": [
        { "name": "subject_id",      "document_id": "aabb1122ccdd3344_aabb1122ccdd3344" },
        { "name": "manipulation_id", "document_id": "" },
        { "name": "protocol_id",     "document_id": "ccdd_protocol" }
    ],
    "base": { "id": "aabb1122ccdd3344_1122334455667788", "session_id": "aabb1122ccdd3344_9900aabbccddeeff",
        "name": "v1_cooling", "datestamp": "2024-06-01T12:00:00.000Z" },
    "treatment": { "ontologyName": "ndic:0000nnnn", "name": "focal cortical cooling",
        "numeric_value": [12.0], "string_value": "Peltier, V1" }
}
```

### After (V_zeta)
```json
{
    "document_class": { "class_name": "temperature_manipulation", "class_version": "1.0.0",
        "superclasses": [ { "class_name": "scalar_manipulation" }, { "class_name": "scalar_temperature" } ] },
    "depends_on": [
        { "name": "subject_id",       "value": "aabb1122ccdd3344_aabb1122ccdd3344" },
        { "name": "time_reference_1", "value": "aabb1122ccdd3344_synthesized" }
    ],
    "base": { "id": "aabb1122ccdd3344_1122334455667788", "session_id": "aabb1122ccdd3344_9900aabbccddeeff",
        "name": "v1_cooling", "datestamp": "2024-06-01T12:00:00.000Z" },
    "subject_interaction": {
        "method":           { "node": "ncit:C60658", "name": "cooling" },
        "variable":         { "node": "ndic:0000nnnn", "name": "focal cortical cooling" },
        "target_structure": [ { "node": "uberon:0002436", "name": "primary visual cortex" } ]
    },
    "scalar_manipulation": { "notes": "Peltier, V1" },
    "scalar_temperature": { "value": [ { "celsius": 12.0, "source_unit": "°C", "source_value": 12.0, "approximate": false } ] }
}
```
(identity → spine `variable`; verb → spine `method`; `target_structure` recovered from `string_value` onto the spine; `applied_property` no longer exists — it is the spine `variable` in the I model; `value` is an array; `protocol_id`/`manipulation_id` dropped; `time_reference` synthesized.)

## File handling

`treatment` references no files. [`_files.md`](_files.md) does not apply.

## Open questions

- **Per-term branch list.** The dispatch table is branch-level; the concrete `ontologyName` → destination mapping per corpus is finalized in **discovery mode** (run the corpus through the converter, read the quarantine/review report, extend the branch list). Report-only before any rewrite.
- **`time_reference` synthesis fidelity.** What session/epoch anchor each corpus exposes; bounded vs point default per family.
- **`protocol_id` carryover.** Dropped now; belongs to the tier-level commonality decision (#8 Option C / #10).
- **Family identity slots.** `procedure` / `factor` currently mirror the spine `variable` on the procedural/environmental families; whether to keep them as structured detail or drop them in favour of `variable` alone is an open V_zeta schema question (identity is off-class in Brainstorm I).

## Cross-references

- Observation-tier split: [`ontology_table_row.md`](ontology_table_row.md)
- Universal renames: [`_universal_renames.md`](_universal_renames.md)
- Design sources (ndi-next-steps): `Procedural_Manipulation_Proposal.md`, `Environmental_Manipulation_Proposal.md`, `Scalar_Manipulation_Proposal.md`, `Injection_Proposal.md`, `Bath_Proposal.md`, `20260615/Brainstorm_I_Tour_and_Comparison.md`.
