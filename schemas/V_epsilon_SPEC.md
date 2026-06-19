# V_epsilon_SPEC.md — DID/NDI Document Schema Format (V_epsilon)

## Purpose

V_epsilon is the next iteration of the DID/NDI schema set after V_delta. It
is still a sandbox (like V_delta), iterated against until the set is ready
to be promoted to a stable `V1`. When that promotion happens, V_epsilon's
contents will be copied to `schemas/V1/` and frozen.

This document specifies the **differences** between V_delta and V_epsilon.
For everything not listed here, the V_delta specification
([`V_delta_SPEC.md`](V_delta_SPEC.md)) is authoritative — the directory
layout (`stable/` / `draft/` / `deprecated/` / `examples/` /
`conversions/`), `index.json` as the resolution source of truth,
resolution-by-`class_name`, the `maturity_level` vocabulary, the
`document_class.schema_version` instance tag, and the field/dependency
object shapes all carry over unchanged.

Where V_delta's substantive changes were organizational, **V_epsilon's
changes are to the schema content itself**: it implements the
`subject_interaction` redesign drafted in the `ndi-next-steps`
"Summer 2026 / 1_Ingestion" proposals. Schema content inside V_epsilon
begins as a verbatim copy of V_delta; this spec records what changed on
top of that copy.

The meta-schema is **unchanged** from V_delta. Every new V_epsilon class
validates against the existing `did_schema_meta.json` — the redesign needs
no new field types, constraint keys, or header keys. (The one exception is
the binding-registry concept, which is carried advisorily inside the open
`constraints` object and is not enforced by the meta-schema; see §7.)

---

## Source of the redesign

V_epsilon implements the design recorded across ~40 proposal and decision
documents in the `ndi-next-steps` repository under
`Summer 2026/1_Ingestion/`. The anchoring document is
`Subject_Interaction_Brainstorm.md`; the consolidated structural decision
is `Subject_Interaction_Proposal.md`; per-family field shapes come from the
individual `*_Proposal.md` files; and disposition of legacy classes comes
from the `*_Decision.md` files.

Several of those proposals leave load-bearing choices explicitly **open**
("deferred to team discussion", "Path A vs B", "provisional, not yet
ratified"). V_epsilon resolves each with a documented default so the set is
internally consistent and implementable. The resolutions are listed in §9
and in [`V_epsilon_notes.md`](V_epsilon_notes.md); they are revisitable
while V_epsilon remains a sandbox.

---

## Differences from V_delta

### 1. The `subject_interaction` spine (new, `draft/`)

A hierarchy unifying everything documented about a subject. The shared
anchor is lifted to an abstract **`subject_statement`** supertype
(`Subject_Statement_Decision.md`), so timeless claims and timed events
share `subject_id` and one `isa subject_statement` query:

```
subject_statement     (abstract)   depends_on: subject_id          ← any claim about a subject
├── subject_assertion  (concrete)   fields: asserted_property, value, source   ← timeless facts
└── subject_interaction(abstract)   depends_on: time_reference (>=1)           ← timed events
    ├── observation    (abstract)   fields: measured_property, target_structure
    ├── manipulation   (abstract)
    └── annotation     (abstract)
```

- `subject_statement` owns `subject_id` (required, → `subject`). Timing is
  the split between the two subtrees: `subject_assertion` is **timeless**
  (no `time_reference`); `subject_interaction` adds `time_reference_#`
  (required, `multiple: true`). Subclasses tighten, never relax — so the
  timeless concept lives on the parent, the timed one on the child.
- `subject_assertion` is the home for timeless asserted facts (species,
  strain, sex, genotype). One generic class: `asserted_property` + `value`
  + `source`. (Typed/date values are a follow-up.)
- There is **no `direction` field**: class membership in
  `observation` / `manipulation` / `annotation` carries that information,
  and `isa` queries replace `direction`-filter queries.
- `target_structure` is **not** on the abstract base. It is declared per
  family (and on the `observation` tier, where both `measured_property`
  and `target_structure` apply to all observations).

### 2. Timing as a dependency: the `time_reference` family (new, `draft/`)

Timing is a referenced document, not an inline field. The abstract
`time_reference` (← `base`, field `is_approximate`) has these concrete
subclasses:

| class | extends | carries |
|---|---|---|
| `utc_reference` | `time_reference` | `start` (timestamp, req), `end` (timestamp, opt ⇒ interval) |
| `event_relative_reference` | `time_reference` | dep `reference_event` → `subject_interaction`; `start`/`end` as signed `duration` offsets (metric) |
| `epoch_relative_reference` | `time_reference`, `epochid` | dep `element_id` → `element`; `epoch_clock`, `t0`, `start`, `end` |
| `epoch_bounded_reference` | `time_reference`, `epochid` | dep `element_id` → `element`; `epoch_clock` (extent = the named epoch) |
| `event_bounded_reference` | `time_reference` | dep `bounding_event` → `subject_interaction` |
| `session_relative_reference` | `time_reference` | dep `session_id` → `session`; `relation` enum {before, after, at_start_of, at_end_of, concurrent_with, during} — **ordinal, no metric**; for interactions with neither a device clock nor a wall-clock date (e.g. an awake behavioral test "at the end of the session") |

`epoch_clock` is a `char` constrained to the NDI-matlab clocktype set
(carried as an advisory `binding` in `constraints`). The former
`temporal_scope`/`extent` inline fields and the optional `epoch_id`
dependency on interactions are retired — epoch linkage is internal to the
two epoch reference classes.

### 3. Observation families (new, `draft/`)

- **Shape library (Brainstorm E, abstract mixins ← `base`).** The typed
  value-composites are promoted to named classes that *own* the `value` field
  and are mixed into the identity classes as a second superclass:
  `scalar_mass`, `scalar_length`, `scalar_duration`, `scalar_volume`,
  `scalar_temperature`, `scalar_pressure`, `scalar_frequency`, `scalar_voltage`,
  `scalar_current`, `scalar_concentration`, `scalar_count`, `scalar_score`,
  `generic_scalar` (source-only struct), and `categorical_concept`
  (`ontology_term` + advisory binding). The **same** shape class is inherited by
  the observation that reads it and the manipulation that imposes it (e.g.
  `scalar_temperature` ← `core_temperature_observation` *and*
  `temperature_manipulation`), so `value` is defined once and
  `isa scalar_temperature` sweeps both tiers.
- `scalar_observation` (abstract genus, ← `observation`) — shape is only an
  `isa` umbrella; the concrete classes under it are named by the **property
  observed** (Brainstorm E) and acquire their typed `value` by also inheriting
  the matching shape mixin (`class isa scalar_observation, scalar_<unit>`):
  `body_weight_observation`/`organ_volume_observation` (mass/volume),
  `body_length_observation` (length), `age_observation` (duration),
  `core_temperature_observation` (temperature), `heart_rate_observation`/
  `respiration_rate_observation` (frequency), `blood_pressure_observation`
  (pressure), `litter_size_observation`/`cell_count_observation` (count),
  `body_condition_observation`/`behavioral_score_observation` (score),
  `concentration_observation` (concentration), `membrane_potential_observation`
  (voltage), plus the escape hatch `generic_scalar_observation`
  (← `generic_scalar`).
- `categorical_observation` (abstract genus, ← `observation`): concrete classes
  named by the **property observed**, each with an `ontology_term` `value`
  governed by the binding registry — `developmental_stage_observation` (pinned
  root `UBERON:0000105`), `health_status_observation`,
  `behavioral_phenotype_observation`, `pigmentation_observation`,
  `estrous_stage_observation`, plus the escape hatch
  `generic_categorical_observation` (free `ontology_term`, no binding).
- `dataseries_observation` (abstract genus, ← `observation`) carrying the
  `axes[]` + `channels[]` header, with two **concrete** sub-genera:
  `timeseries_observation` (ordering-only axes → traces) and
  `imageseries_observation` (≥2 spatial axes → images/movies/stacks). The
  earlier `standalone_*`/`daq_*`/`opaque_*` leaf split is **not** present
  (see §9, "Standalone removal").
- `expression_observation` (concrete, ← `observation`) for omics endpoint
  snapshots (dep `data_id` → `expression_matrix_data`), with the structural
  subclass `spatial_expression_observation` (adds `coordinate_registration`).

### 4. Manipulation families (new, `draft/`)

- `scalar_manipulation` (abstract, ← `manipulation`; `applied_property`,
  `target_structure`, `notes`) with `temperature_manipulation`,
  `pressure_manipulation`, `frequency_manipulation`, and the escape hatch
  `generic_scalar_manipulation`.
- `procedural_manipulation` (concrete, ← `manipulation`; `procedure`,
  `target_structure`, `notes`) with the concrete subclass
  `biological_transfer` (adds `donor_id`, `entity`, `kind`).
- `environmental_manipulation` (concrete, ← `manipulation`; `factor`,
  `target_structure`, `notes`).
- `pharmacological_manipulation` (abstract, ← `manipulation`; shared
  `mixture` of `{chemical, amount}`) with `injection` (adds `kind`,
  `volume`, `route`, `target_structure`, `coordinates`) and `bath` (adds
  `kind`, `location`).
- `stimulus_manipulation` (concrete bridge, ← `manipulation`; dep
  `stimulus_presentation_id` → `stimulus_presentation`).
- `placement` (concrete, ← `manipulation`; dep `container_id` → `subject`;
  `batch_id`) — event-sourced containment.
- `derivation` (concrete, ← `manipulation`; dep `source_subject_id_#` →
  `subject`; `derivation_method`, `target_structure`) — event-sourced
  provenance.

### 5. Annotation family (new, `draft/`)

- `group_assignment` (concrete, ← `annotation`; dep `group_id` → `subject`;
  `batch_id`) — event-sourced membership.

### 6. Standalone / infrastructure additions (new, `draft/`)

- `interaction_purpose` (← `base`; dep `interaction_id_#` →
  `subject_interaction`; `purpose`, `comment`) — generalizes the legacy
  `stimulus_purpose` to apply to any interaction.
- `instrument` (← `base`; `instrument_type`, `global_identifier`) — a
  subject-agnostic apparatus identity handle.
- `stimulus_approach` (← `base`, v2.0.0) — **re-scoped** from a purpose
  label to a denormalized descriptor of out-of-band stimulus conditions
  (deps `subject_id`, `stimulator_id`, `stimulus_presentation_id`,
  `stimulus_manipulation_id`; fields `epoch_id`, `condition`).
- Dataseries bodies: `dataseries_data` (abstract; `axes`/`channels`/
  `storage`/`storage_mode`/`content_hash`) → `timeseries_data` /
  `imageseries_data` (abstract format branches) → concrete format subtypes
  (`timeseries_data_csv`, `timeseries_data_binary`, `timeseries_data_edf`);
  `dataseries_channel_map` (slot-indexed channel-meaning sidecar);
  `dataseries_pyramid` (disposable multiresolution read cache).
- Expression bodies: `expression_matrix_data` (abstract) + 13 format
  subtypes (`_h5ad`, `_mtx`, `_cellranger_h5`, `_loom`, `_counts_table`,
  `_gef`, `_gem`, `_visium`, `_mzml`, `_mztab`, `_maxquant`, `_dia_report`,
  `_imzml`).
- Reference bodies: `reference_data` (abstract; `species`, `assembly`,
  `version`, `content_hash`, …) → `reference_sequence_data` (+ fasta
  subtypes) and `reference_annotation_data` (+ gtf/gff3 subtypes);
  `sequence_read_data` (abstract) + `_bam`/`_cram`/`_fastq`.

### 7. Modifications to existing classes

| class | change |
|---|---|
| `subject` | v2.0.0; adds intrinsic facets `is_biological`, `is_group`. Carries **no** `depends_on` — containment/membership/provenance are event-sourced via `placement`/`group_assignment`/`derivation`. |
| `element_epoch` | v2.0.0; additive optional `axes`/`channels`/`storage` so an epoch body can self-describe a dataseries. |
| `stimulus_bath` | v2.0.0; re-rooted as a concrete subclass of `bath` and moved to `draft/`. `mixture`/`kind`/`location` are inherited from `bath`; gains `stimulus_element_id`; `epochid` superclass dropped (timing now via `time_reference`). |

`binding` blocks (advisory vocabulary constraints — `root`/`expansion`/
`strength`/`source`, or `keyed_by` for registry-keyed properties) are
carried inside the open `constraints` object on `ontology_term` fields
(`epoch_clock`, `categorical_observation.value`, `reference_data.species`).
They are documentation/tooling aids; the meta-schema does not enforce them.

### 8. Deprecations

Moved to `deprecated/` with `maturity_level: "deprecated"`:

| deprecated class | replaced by |
|---|---|
| `treatment` | split across `procedural_manipulation`, `environmental_manipulation`, `temperature_manipulation` (+ out-of-tier routing) |
| `treatment_drug` | `injection` (`kind: "drug"`) |
| `treatment_transfer` | `biological_transfer` |
| `virus_injection` | `injection` (`kind: "virus"`; serotype/titer carried in the `mixture` ontology term + `concentration`) |
| `subject_group` | `subject` with `is_group: true` + `group_assignment` events |

The five deprecated schemas remain in the set (not deleted) so legacy
instances can still be validated during the migration window.

---

## 9. Resolved open questions

The source proposals left several choices open; V_epsilon resolves them as
follows (rationale in [`V_epsilon_notes.md`](V_epsilon_notes.md)):

1. **Class-per-family vs polymorphic microschema body (Path A vs B).**
   Resolved to **Path A** — concrete class-per-family inheritance, which
   every family proposal is written for and which reuses V_delta's
   existing inheritance machinery with no meta-schema change.
2. **`observation`/`manipulation`/`annotation` abstract vs concrete.**
   Resolved to **abstract** (consistent with Path A; only concrete family
   leaves are instantiable).
3. **Standalone observation leaves.** Resolved per the later
   `Standalone_Removal_Decision.md`: **no** `standalone_*`/`daq_*`/
   `opaque_*` leaves; `timeseries_observation`/`imageseries_observation`
   are concrete sub-genera of `dataseries_observation`.
4. **`virus_injection` disposition.** Resolved per `Injection_Proposal.md`
   (deprecate → `injection`), overriding the earlier
   `Boundary_Mapping_Proposal.md` "subclass under `biological_transfer`".
5. **`time_reference` multiplicity, `epoch_clock` vocabulary, `instrument`
   existence as a class, element subject-binding** — see §2, §6, §7 and
   the notes.

---

## Promotion to V1

Same procedure as V_delta (see `V_delta_SPEC.md` § "Promotion to V1"):
copy `schemas/V_epsilon/` to `schemas/V1/`, freeze it, replace the
`"V_epsilon"` value in `schema_version` fields and `index.json`, and tag
the repository. Before promotion, the `draft/` families are expected to be
exercised against real curations and re-tiered to `stable/`.
