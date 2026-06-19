# Conversion: did_v1 → V_epsilon — `ontology_table_row` → observation tiers (Brainstorm E split)

> The observation-tier companion to [`treatment.md`](treatment.md). The legacy `ontology_table_row` open key/value bag is **retired** and **split** across the Brainstorm E observation property classes (and, for non-observation rows, out of the tier). This is the genuinely **one-to-many** migration: one `ontology_table_row` document → N destination documents.

## Identity

- **Target tier:** V_epsilon observation families (`schemas/V_epsilon/draft/`).
- **did_v1 source:** legacy NDI/DID `ontology_table_row` (open table of `(ontology term, value[, unit])` rows attached to a subject at a time).
- **Status:** `drafted` — needs the 1→N migrator capability (see [Engine note](#engine-note)) and the per-term dispatch table (finalized in discovery mode).
- **Cardinality:** **1 → N.** Each row dispatches independently; a single source document fans out to several destinations across tiers.

## Summary

Each row names a property (an ontology term) and a value. Brainstorm E dispatches per row by **what the property is** and **what shape its value takes**:
- a **scalar** measurement → the matching scalar property class (`body_weight_observation`, `core_temperature_observation`, …), value as the typed composite;
- a **categorical** label → the matching categorical property class (`developmental_stage_observation`, …), value as a bound `ontology_term`;
- a **subject-intrinsic, set-once** fact (species, strain, sex) → **not an observation** → the `subject` document / `openminds_subject`;
- a **relational/assigned** fact (cohort, housing, derivation source) → the relevant **event/annotation** class (`group_assignment`, `placement`, `derivation`);
- a fact with **no minted property class yet** → the escape hatch (`generic_scalar_observation` / `generic_categorical_observation`), promoted later.

## Per-row dispatch table

First match wins, on the row's property term (branch) and value shape.

| Row property (branch) + value shape | Destination | Mapping |
|---|---|---|
| Mass-dimensioned, numeric (body weight, brain/tumor mass) | `body_weight_observation` (`value : scalar_mass`) | term → `measured_property`; structure → `target_structure`; value+unit → `scalar_mass` composite |
| Length-dimensioned | `body_length_observation` (`scalar_length`) | as above |
| Duration / age | `age_observation` (`scalar_duration`) | |
| Temperature | `core_temperature_observation` (`scalar_temperature`) | |
| Frequency (heart/respiration rate) | `heart_rate_observation` / `respiration_rate_observation` (`scalar_frequency`) | |
| Pressure (BP, IOP, partial pressure) | `blood_pressure_observation` (`scalar_pressure`) | |
| Count (litter size, cell count) | `litter_size_observation` / `cell_count_observation` (`scalar_count`) | |
| Score (body condition, behavioral) | `body_condition_observation` / `behavioral_score_observation` (`scalar_score`) | |
| Concentration (glucose, cortisol, titer) | `concentration_observation` (`scalar_concentration`) | |
| Voltage (transcribed Vm) | `membrane_potential_observation` (`scalar_voltage`) | |
| **Scalar with no minted property class** | `generic_scalar_observation` (`generic_scalar`) | value → `{source_unit, source_value, approximate}`; promote later |
| Categorical: developmental/life stage | `developmental_stage_observation` (bound under `UBERON:0000105`) | term → `value`; property → `measured_property` |
| Categorical: health status / coat / estrous / behavioral label | `health_status_observation` / `pigmentation_observation` / `estrous_stage_observation` / `behavioral_phenotype_observation` | term → `value` |
| **Categorical with no minted property class** | `generic_categorical_observation` (free `ontology_term`, no binding) | term → `value`; promote later |
| **Subject-intrinsic, set-once** (species, strain, sex, DOB) | **out of tier** → `subject` / `openminds_subject` (merge) | not an observation |
| **Relational / assigned** (cohort, housing, derivation source) | **out of tier** → `group_assignment` / `placement` / `derivation` | event/annotation tiers |
| Empty / unresolvable term | **curator review queue** (routing off) | flagged |

## Common field mapping (per generated observation)

| did_v1 row element | V_epsilon field | Transformation |
|---|---|---|
| row property term | `measured_property` (inherited from `observation`) | `ontology_term` |
| anatomical qualifier (if any) | `target_structure` | `ontology_term[]`; else `[]` |
| row value (+ unit) | `value` on the destination shape block | typed composite (scalar) or bound `ontology_term` (categorical) per shape |
| source `subject_id` | inherited `subject_id` | identity, shared by all generated docs |
| source time anchor | inherited `time_reference_#` | shared by all generated docs (the whole row burst is one moment) |

## Engine note

This conversion is **1 → N** and so requires the converter to support a migrator that **returns multiple bodies** (the current `+did2.+convert.+migrators.<class>` contract returns one body). The migrator emits one destination document per row, all sharing the source `subject_id` + synthesized `time_reference`, and routes non-observation rows out of tier. See [DID-matlab] `+did2/+convert/` for where the pipeline fans out. Until the 1→N capability lands, this conversion stays `drafted`.

## Worked example — a 2-row intake burst → two observations

### Before (did_v1, one document, two rows)
```json
{
    "document_class": { "class_name": "ontology_table_row", "class_version": "1.0.0",
        "superclasses": [ { "class_name": "base", "class_version": "1.0.0" } ] },
    "depends_on": [ { "name": "subject_id", "document_id": "aabb1122ccdd3344_aabb1122ccdd3344" } ],
    "base": { "id": "aabb1122ccdd3344_1122334455667788", "session_id": "aabb1122ccdd3344_9900aabbccddeeff",
        "name": "intake_row", "datestamp": "2024-05-15T09:30:00.000Z" },
    "ontology_table_row": {
        "rows": [
            { "ontologyName": "schema:weight", "name": "weight", "value": 22.5, "unit": "g" },
            { "ontologyName": "uberon:0000105", "name": "life cycle stage", "value": "FBdv:00005336" }
        ]
    }
}
```

### After (V_epsilon, two documents)
```json
[
  {
    "document_class": { "class_name": "body_weight_observation", "class_version": "1.0.0",
        "superclasses": [ { "class_name": "scalar_observation" }, { "class_name": "scalar_mass" } ] },
    "depends_on": [
        { "name": "subject_id",       "value": "aabb1122ccdd3344_aabb1122ccdd3344" },
        { "name": "time_reference_1", "value": "aabb1122ccdd3344_synthesized" } ],
    "base": { "id": "aabb1122ccdd3344_aaaa000000000001", "session_id": "aabb1122ccdd3344_9900aabbccddeeff",
        "name": "intake_weight", "datestamp": "2024-05-15T09:30:00.000Z" },
    "observation": { "measured_property": { "node": "schema:weight", "name": "weight" }, "target_structure": [] },
    "scalar_mass": { "value": { "kilograms": 0.0225, "source_unit": "g", "source_value": 22.5, "approximate": false } }
  },
  {
    "document_class": { "class_name": "developmental_stage_observation", "class_version": "1.0.0",
        "superclasses": [ { "class_name": "categorical_observation" }, { "class_name": "categorical_concept" } ] },
    "depends_on": [
        { "name": "subject_id",       "value": "aabb1122ccdd3344_aabb1122ccdd3344" },
        { "name": "time_reference_1", "value": "aabb1122ccdd3344_synthesized" } ],
    "base": { "id": "aabb1122ccdd3344_aaaa000000000002", "session_id": "aabb1122ccdd3344_9900aabbccddeeff",
        "name": "intake_stage", "datestamp": "2024-05-15T09:30:00.000Z" },
    "observation": { "measured_property": { "node": "uberon:0000105", "name": "life cycle stage" }, "target_structure": [] },
    "developmental_stage_observation": { "value": { "node": "fbdv:00005336", "name": "larval stage" } }
  }
]
```

## Open questions

- **Per-term dispatch table** — the property-term → property-class map is finalized in discovery mode against real corpora (the same report-only loop as `treatment`). Terms with no minted class fall to the generic escape hatches.
- **New `base.id` per generated doc** — N new documents need N stable ids; define the derivation (e.g. source id + row index) so re-runs are idempotent.
- **1→N engine capability** — prerequisite; see [Engine note](#engine-note).

## Cross-references

- Manipulation-tier split: [`treatment.md`](treatment.md)
- Universal renames: [`_universal_renames.md`](_universal_renames.md)
- Design sources (ndi-next-steps): `Scalar_Observation_Proposal.md`, `Categorical_Observation_Proposal.md`, `20260615/Brainstorm_E_Class_Catalog.md` §3, `Pulakat_Datatype_Homes.md`.
