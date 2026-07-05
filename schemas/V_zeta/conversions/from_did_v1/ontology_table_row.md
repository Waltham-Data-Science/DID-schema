# Conversion: `ontology_table_row` → the Brainstorm-I observation tier

**Status:** V_zeta (Brainstorm I) rewrite of the V_epsilon (Brainstorm E) split
spec. The 1→N shape is unchanged (one table row → N observation documents, one
per measured column); what changes is the **destination**: I names observation
leaves by **data-type (shape)**, not property, and carries the property on the
spine `variable` term.

---

## The split, in the I model

A `did_v1` `ontology_table_row` packs several measured facts about a subject
into one row. Each **column** becomes one observation document. The destination
**class** is chosen by the value's **shape** (the #59 axis test), and the
column's property term becomes the queryable `variable`:

- a **scalar** measurement → the matching `scalar_<dim>_observation`
  (`scalar_mass_observation`, `scalar_temperature_observation`, …), value as the
  typed composite;
- a **categorical** label → `categorical_observation`, value as a bound
  `ontology_term`;
- a fact with **no usable value** (missing key, empty, `NaN`) → skipped;
- a value with no minted dimensional shape → the escape hatch
  `generic_scalar_observation` (`{source_unit, source_value, approximate}`),
  promoted to a dimensional leaf later.

There is **no property class** anymore: a body-weight column and a brain-mass
column both become `scalar_mass_observation`, distinguished only by their
`variable` term.

## Column → destination class (by shape, not property)

| Column value shape | Destination class (`value` type) | Field mapping |
|---|---|---|
| Mass-dimensioned (body weight, brain/tumor mass) | `scalar_mass_observation` (`value : mass`) | term → `variable`; anatomy → `target_structure`; value+unit → `mass` composite |
| Length / distance | `scalar_length_observation` (`length`) | as above |
| Duration / age | `scalar_duration_observation` (`duration`) | |
| Volume | `scalar_volume_observation` (`volume`) | |
| Temperature | `scalar_temperature_observation` (`temperature`) | |
| Frequency (heart / respiration rate) | `scalar_frequency_observation` (`frequency`) | |
| Pressure (BP, IOP, partial pressure) | `scalar_pressure_observation` (`pressure`) | |
| Count (litter size, cell count, spike count) | `scalar_count_observation` (`count`) | |
| Score (body condition, behavioral) | `scalar_score_observation` (`score`) | |
| Concentration (glucose, cortisol, titer) | `scalar_concentration_observation` (`concentration`) | |
| Voltage (transcribed Vm) | `scalar_voltage_observation` (`voltage`) | |
| Current | `scalar_current_observation` (`current`) | |
| **Scalar with no dimensional shape** | `generic_scalar_observation` (`generic_scalar`) | value → `{source_unit, source_value, approximate}`; promote later |
| Categorical: any concept (developmental stage, health status, coat colour, estrous, behavioral label) | `categorical_observation` (`value : ontology_term`) | term → `value`; property → `variable` |

## Field-by-field (all destinations)

| `ontology_table_row` source | I destination | type |
|---|---|---|
| row subject | `subject_id` (spine dep, inherited) | dep → `subject` |
| — (verb) | `method` (spine) = measurement | `ontology_term` (optional) |
| row property term | `variable` (spine) | `ontology_term` (**required**) |
| row anatomy/structure, if any | `target_structure` (spine) | `ontology_term[]` (optional) |
| row value (+ unit) | `value` on the destination block | scalar: typed composite in the shape-mixin block (`scalar_mass`, …); categorical: bound `ontology_term` on `categorical_observation`'s block |
| row time | a `time_reference` dep (below) | dep → `time_reference` |

The former `observation.measured_property` is gone — property identity is the
spine `variable`. Per-sample timing uses the shaped `time_reference` (§2 of
`V_zeta_SPEC.md`), not a `sample_time` array.

## Timing anchor

Each migrated observation must resolve a `time_reference`. When the source row
carries no device clock or wall-clock date, emit/link a
`session_relative_reference` (`relation = during`, → `session` via
`base.session_id`), exactly as the treatment split does. A shared row-level
anchor is reused across the N column-observations produced from one row
(1 → N+1 documents: N observations + 1 shared reference).

## Worked example (one row → two observations)

```jsonc
// column 1: body weight 24.3 g  ->  scalar_mass_observation
{
  "document_class": { "class_name": "scalar_mass_observation", "class_version": "1.0.0",
      "superclasses": [ { "class_name": "scalar_observation" }, { "class_name": "scalar_mass" } ] },
  "depends_on": [ { "name": "subject_id", "value": "…" }, { "name": "time_reference_1", "value": "…" } ],
  "subject_interaction": {
      "method":   { "node": "ncit:C41355", "name": "measurement" },
      "variable": { "node": "schema:weight", "name": "weight" },
      "target_structure": [] },
  "scalar_mass": { "value": [ { "kilograms": 0.0243, "source_unit": "g", "source_value": 24.3, "approximate": false } ] }
}

// column 2: life stage = larval  ->  categorical_observation
{
  "document_class": { "class_name": "categorical_observation", "class_version": "2.0.0",
      "superclasses": [ { "class_name": "observation" } ] },
  "depends_on": [ { "name": "subject_id", "value": "…" }, { "name": "time_reference_1", "value": "…" } ],
  "subject_interaction": {
      "method":   { "node": "ncit:C41355", "name": "measurement" },
      "variable": { "node": "uberon:0000105", "name": "life cycle stage" },
      "target_structure": [] },
  "categorical_observation": { "value": { "node": "fbdv:00005336", "name": "larval stage" } }
}
```

## The dominant `did_v1` form and the migrator

The dominant `ontology_table_row` layout is **parallel char fields** —
comma-separated `names`, `variable_names`, `ontology_nodes` plus a `data` struct
keyed by `variable_names`. One document is one table **row**; each **column** is
a measured property. The migrator splits it: column *i* → one observation with
`variable = ontology_nodes[i] + names[i]` and value `= data.(variable_names[i])`,
dispatched scalar-vs-categorical by the value type, and the destination scalar
class chosen by the value's dimension. Columns with no usable value are skipped;
an unrecognised layout falls back to migrating unchanged as an
`ontology_table_row` (the class carries over) rather than quarantining.
