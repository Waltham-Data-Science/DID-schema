# V_zeta_SPEC.md — DID/NDI Document Schema Format (V_zeta)

## Purpose

V_zeta is the next sandbox iteration of the DID/NDI schema set. It implements
**Brainstorm I**, the current direction of the `ndi-next-steps`
"Summer 2026 / 1_Ingestion" design thread (issue #69). Like every prior
sandbox (V_gamma → V_delta → V_epsilon), V_zeta is iterated against real
curation corpora until ready to be promoted to a stable `V1`.

This document specifies the **differences** from V_delta. For everything not
listed here — the tiered directory layout (`stable/` / `draft/` /
`deprecated/` / `examples/` / `conversions/`), `index.json` as the resolution
source of truth, resolution-by-`class_name`, the `maturity_level` vocabulary,
the `document_class.schema_version` set-version tag, and the field/dependency
object shapes — the V_delta specification (`V_delta_SPEC.md`) remains
authoritative. The meta-schema (`did_schema_meta.json`) is **unchanged**:
every V_zeta class validates against it with no new field types, constraint
keys, or header keys. (The one advisory exception is the `binding` block,
carried inside the open `constraints` object; the meta-schema does not enforce
it.)

## Relationship to V_epsilon (Brainstorm E)

**V_zeta supersedes V_epsilon.** V_epsilon implemented Brainstorm **E**
(identity-named observation tiers — a `..._observation` class per measured
*property*). On main, V_epsilon is preserved as an archived reference, and the
merge that landed it records the reason: *"Brainstorm E is superseded by
Brainstorm I."*

Brainstorm I keeps almost all of V_epsilon's design-neutral machinery — the
infrastructure classes, the manipulation families, the `time_reference`
reference frames, the dataseries/expression bodies, and the scalar/categorical
shape library — and V_zeta reuses those verbatim. What it **rebuilds** is the
observation tier, the spine, and the timing model, per §§1–4 below. V_zeta
therefore begins as a copy of V_epsilon's content with the Brainstorm-I deltas
applied, but its *design lineage* traces to V_delta (`based_on: "V_delta"`);
the E-specific observation classes are removed, not carried.

---

## Source of the redesign

The anchoring document is
`ndi-next-steps/Summer 2026/1_Ingestion/20260615/Brainstorm_I_Tour_and_Comparison.md`
(with `Brainstorm_I_slides.html`). Brainstorm I is stated there as **"Brainstorm
H plus three field-level changes and two restorations."** Supporting decisions
come from `Observations_Manipulations_overview.md` (the shared skeleton),
`Scalar_Dataseries_Boundary_Decision.md` (#59, the shape test),
`Channel_Model_and_Daqless_Element_Decision.md` (the record/array channel
model), `Temporal_Scope_Proposal.md` (`time_reference`), and the 2026-07-03
`Locus_Encoding_Paths_Summary.md` / `Choosing_the_Subject_Guide.md` (the locus
fork). Where those proposals leave a choice open, V_zeta resolves it with a
documented default (see §9); the defaults are revisitable while V_zeta is a
sandbox.

---

## Differences from V_delta

### 1. One spine: `subject_interaction` (rewritten, `stable/`)

Brainstorm I collapses the observation/manipulation asymmetry to **one shared
skeleton**. Every timed record is a `subject_interaction`, and the whole
identity/where/when payload lives on the spine:

```
subject_interaction    (abstract, isa base)
  subject_id       → subject          the whole specimen measured or acted on
  time_reference_# → time_reference   WHEN — a SHAPED reference (§2), one or more, ≥1
  method           { node, name }      the verb: what was done (measure, inject, heat)   [optional]
  variable         { node, name }      the noun: what it is about (temperature, a drug)  [required]
  target_structure { node, name }[]    (optional) the locus on the subject (§3, Path T)
  element_id       → element           (optional) the specific individuated part /
                                       derived entity this is about (§3.1)
```

- **Direction is two empty classes.** `observation` and `manipulation` (and the
  carried-over `annotation`) extend `subject_interaction` and **add no fields** —
  membership carries direction, and `isa observation` replaces a `direction`
  filter. `observation`'s former `measured_property`/`target_structure` fields
  are gone (folded into the spine's `variable`/`target_structure`).
- **Identity is off the class.** V_zeta keeps H's `(method, variable)` ontology
  pair (settled in Brainstorm I) rather than E's per-property classes or the
  proposals' `measured_property`/`applied_action`. `variable` is the queryable
  fine identity; correctness of variable-vs-value-shape is a **binding-registry
  nudge**, not a class weld — this is the direct answer to E's enumeration
  failure (the EPM assay mints ~40 property columns; they all land in one
  shape/data-type leaf, with the fine identity on `variable`).
- `subject_statement` (V_epsilon's abstract shared parent) is **removed**;
  `subject_interaction` is-a `base` directly. `subject_assertion` (timeless
  facts — species/strain/sex/genotype) is re-rooted under `base` and owns its
  own `subject_id`.

### 2. Timing is a SHAPED reference; `sample_time` is retired (§2)

Brainstorm I removes H's parallel `sample_time` array and carries the timing in
`time_reference`, **whose shape matches the value's shape**. `time_reference`
gains an optional `sampling` structure (discriminator `kind`):

| data shape | `sampling` | note |
|---|---|---|
| scalar (1) | `{ kind: point }` | one moment at the anchor |
| regular series (N) | `{ kind: grid, sample_rate, n }` | O(1) — never grows with N |
| irregular series (N) | `{ kind: enumerated, offsets[] }` | explicit per-sample offsets |

The anchoring instant (t0) is supplied by the concrete reference-frame subclass
(`utc_reference.start`, `epoch_relative_reference.t0`, …); the time of sample
*i* is **derived** (`anchor + i/sample_rate` for a grid), never stored beside
the value. Two payoffs the proposal calls out: **same-sample search holds**
(value and time share an index by construction — the false positives of the
independent `[*]` arrays cannot arise), and **regular grids are three numbers,
not N**. `sample_time` is dropped from the `scalar_observation` /
`scalar_manipulation` genera.

The `time_reference` reference *frames* are unchanged from V_epsilon:
`utc_reference`, `epoch_relative_reference`, `epoch_bounded_reference`,
`event_relative_reference`, `event_bounded_reference`,
`session_relative_reference` (+ `session_extent`).

### 3. Locus: the `target_structure` field — Path T (§3)

V_zeta records *which part of a subject* an interaction is about with an
optional `target_structure` ontology term (a list) on the spine; the subject
stays the **whole specimen** (`mouse_042`, not `V1_of_mouse_042`). This is
**Path T** of `Locus_Encoding_Paths_Summary.md`, chosen over Path S
(subject-as-part) as the pragmatic default: it is near the decided model and
needs no standing find-or-create/dedup service under random subject UIDs. The
accepted trade-off is the region/slice wall and no per-locus biography; the
objective annotation rule and the imaging-FOV convention from
`Choosing_the_Subject_Guide.md` govern curation. `target_structure` is a **list**
(bilateral/multi-structure); the multi-structure-image rule is FOV-container +
derived observations.

### 3.1 The individuated referent: optional `element_id` on the spine

`target_structure` names the *ontological KIND* of locus (a place — "CA1",
"layer 5 pyramidal"). It cannot point at a **specific individuated entity that is
part of the subject** and has its own document identity but is neither a
`subject_group` nor reducible to an anatomy term — the canonical case being an
`ndi` element (an `ndi.neuron`, a probe, a derived signal). "Neuron #47 that I
recorded from" is a *thing*, not a *place*, and Path T had no slot for it.

V_zeta adds an **optional `element_id → element`** dependency on the spine,
completing the referent set every `subject_interaction` can express:

| slot | question it answers | type |
|---|---|---|
| `subject_id` | the whole specimen (mandatory objective anchor) | ref → `subject` |
| `target_structure` | the ontological KIND of locus ("a place") | ontology_term[] |
| `element_id` | THIS specific individuated part / derived entity ("which one") | ref → `element` |

The three are orthogonal and co-occur (an interaction may name a specimen, an
anatomy term, *and* the exact element). `element_id` is **optional** — whole-subject
records (a bath, a body weight) leave it empty — and `subject_id` stays mandatory,
so "everything about subject X" queries are unchanged. Identity stays **off the
class** (the EPM lesson): this is a reference edge, not a `neuron_observation`
subclass. Since an `element` already carries its own `subject_id`, the invariant
`element_id.subject == subject_id` is a **binding-registry nudge**, not a class
weld. The restored dataseries event-graph handle (§4, `depends_on element_id →
element`) is this same spine edge; its "the handle must point at an element"
requiredness is a per-leaf / binding-registry concern layered on the optional
spine slot. (Migrators do not yet populate `element_id`; preserving source
element references from element-scoped `did_v1` observations is a deliberate
per-migrator follow-up.)

### 4. Observation leaves named by DATA-TYPE (shape), not property (§4)

The core Brainstorm-I change to the observation tier. The shape/data-type is the
class; the property is the `variable` term.

- **Scalar tier.** `scalar_observation` (abstract, ← `observation`) is a bare
  `isa` umbrella. Concrete leaves are named by their **dimensional composite**
  and acquire their typed `value` from the shared shape library (a second
  superclass): `scalar_mass_observation`, `scalar_length_observation`,
  `scalar_duration_observation`, `scalar_volume_observation`,
  `scalar_temperature_observation`, `scalar_pressure_observation`,
  `scalar_frequency_observation`, `scalar_voltage_observation`,
  `scalar_current_observation`, `scalar_concentration_observation`,
  `scalar_count_observation`, `scalar_score_observation`, plus the escape hatch
  `generic_scalar_observation`. (E's ~20 property leaves — `body_weight_`,
  `core_temperature_`, … — are removed; a body-weight reading is now
  `scalar_mass_observation` with `variable = {body weight}`.) The **same** shape
  class is shared with the manipulation that imposes it
  (`scalar_temperature` ← both `scalar_temperature_observation` and
  `temperature_manipulation`), so `value` is defined once and
  `isa scalar_temperature` sweeps both tiers.
- **Series-as-cardinality (kept, retimed).** Each shape mixin's `value` is an
  ARRAY of its composite; a single reading is the length-1 case, a curve is
  length N of the *same* class. Per-sample timing is the shaped `time_reference`
  (§2), not `sample_time`.
- **Categorical tier.** `categorical_observation` is now a single **concrete**
  class (E's abstract genus + per-property leaves + `categorical_concept`
  placement machinery are removed): one `ontology_term` `value`, one concept per
  document, admissible root a binding nudge keyed on `variable`.
- **Dataseries tier (restored).** `dataseries_observation` (abstract,
  ← `observation`; `axes[]` + `channels[]` header) → `timeseries_observation`
  (ordering axes → traces) and `imageseries_observation` (≥2 spatial axes →
  images/movies). A dataseries observation is a light event-graph handle
  (`depends_on element_id → element`) whose native-unit samples live in
  `element_epoch`; its payoff is subject-wide discovery in one query
  (`isa timeseries_observation` + `subject_id = X`). The record/array channel
  model and the newest-wins `dataseries_channel_map` sidecar carry over from the
  channel-model decision. `expression_observation` / `spatial_expression_observation`
  (omics endpoints) carry over.

#### 4.1 Imaging: `image_stack` retired onto the ingested imageseries

The legacy standalone `image_stack` / `image_stack_parameters` (a file-backed
pixel blob + geometry bundle, tied to a subject but off the spine) are **retired
to `deprecated/`** and folded onto NDI's imaging stack — the same model NDI-main
ships in code (`ndi.element.image` / `ndi.probe.image`, whose frames are timed
through the epoch clock / syncgraph, `'no_time'` for a clockless stack). Three
roles replace the one document:

| role | class |
|---|---|
| discoverable subject-facing handle | `imageseries_observation` (spine: `subject_id` + shaped `time_reference` + `variable`/`kind` = modality + `element_id`; the caption is `dataseries_observation.label`) |
| the **digital, in-database** pixels | **`daqreader_image_epochdata_ingested`** — a `frames.bin` raw binary + a queryable YXCZT header (`dimension_order`/`size`, `data_type`, `num_frames`, `frametimes`, `clocktype`). This is exactly what `ndi.daq.reader.image.ingest_epochfiles` writes: once ingested, the image is digital data resident in the database with no external file dependency. **Newly ported into V_zeta** (it was in NDI's `ndi_common` but absent from did-schema). |
| the element the frames belong to | `ndi.element.image` (non-direct = ingested), with `element_epoch` as the epoch record |

The geometry that lived in `image_stack_parameters` (`dimension_order`/`size`/
`scale`/`units`) becomes the dataseries `axes[]` and the ingested header;
`data_type`/`data_limits` are added to the `element_epoch`/`dataseries_data`
`storage` descriptor; `timestamp`+`clocktype` become the epoch clock. A did_v1
`image_stack` migrates 1→6 (`did2.convert.migrators_i.image_stack`): the handle,
the ingested frames, the element, its epoch, a minimal `daqreader`, and the
ordinal time anchor — dropping the legacy `document_id` edge (the corpus
reference-integrity orphan). Discovery-mode fallback: an un-migrated `image_stack`
still resolves 1→1 to the deprecated class.

### 5. Manipulation tier — classes earn their place by STRUCTURE

Symmetric with the observation tier: a manipulation is a class only when it adds
**structure** (a typed value, a dependency, or an invariant), never for identity
alone — the identity is the spine `variable` term. The abstract `manipulation`
direction class hosts a shared `notes` prose field; concrete leaves:

- `scalar_manipulation` (abstract) → `temperature_manipulation` /
  `pressure_manipulation` / `frequency_manipulation` /
  `generic_scalar_manipulation` — impose a **typed value**.
- `pharmacological_manipulation` (abstract) → `injection` / `bath`
  (+ `stimulus_bath`) — carry a `mixture` + delivery structure.
- `biological_transfer` — earns its class via the `donor_id` **dependency**
  (re-parented directly onto `manipulation`).
- `stimulus_manipulation` — a `stimulus_presentation_id` dependency.
- `generic_manipulation` (concrete) — the escape-hatch leaf for payload-free
  acts: surgical/physical procedures, environmental/husbandry regimes,
  behavioral training. No typed value, no extra structure; the specific act is
  the spine `variable`, its ontology branch (OBI/NCIT procedure vs husbandry)
  carrying the coarse kind. This is the manipulation-side analog of
  `generic_scalar_observation`.

**`procedural_manipulation` and `environmental_manipulation` do NOT exist** —
they were pure-identity classes (only an ontology `procedure`/`factor` + `notes`,
no distinct structure), which the framework forbids; they fold into
`generic_manipulation` with the act named by `variable`. The spine-owned
`target_structure` is stripped from every family that declared it (now
inherited). Event-sourced relations `placement`, `derivation`,
`group_assignment` (← `annotation`), and the standalone `interaction_purpose` /
`instrument` / re-scoped `stimulus_approach` carry over.

### 6. Preserved infrastructure

All non-interaction infrastructure is preserved verbatim from the canonical set:
`base`, `session`/`dataset_*`, `subject` (with `is_biological`/`is_group`
facets), `element`/`element_epoch`/`epoch*`, `daqsystem`/`daqreader*`,
`probe_location`/`probe_geometry`/`site2channelmap`, the `stimulus_*` family and
tuning/response calculators, `openminds*`, `ontology_*`, `zarr`/`image*`, etc.

### 7. Deprecations

`treatment`, `treatment_drug`, `treatment_transfer`, `virus_injection`, and
`subject_group` remain in `deprecated/` (replaced as in V_epsilon:
treatment-family → the manipulation tiers; `virus_injection`/`treatment_drug` →
`injection`; `treatment_transfer` → `biological_transfer`; `subject_group` →
`subject(is_group)` + `group_assignment`). Conversion notes are in
`conversions/`.

### 8. Carryover cleanup

`hartley_calc`'s `file` record (a long-standing defect copied through V_delta →
V_epsilon: field-definition keys on a file record) is stripped to `name` +
`documentation` so the whole V_zeta set passes meta-validation (v2.0.0).

---

## 9. Resolved open questions

| # | question (source) | V_zeta default |
|---|---|---|
| 1 | Locus encoding — Path S vs Path T (#69) | **Path T** — `target_structure` field; subject is the whole specimen. |
| 2 | `target` vs `target_structure` | **`target_structure`** (Brainstorm I recommendation; corpus's existing name; a list). |
| 3 | identity field names | **`method` / `variable`** (settled in Brainstorm I). |
| 4 | observation identity placement | **off-class** — shape/data-type is the class, property on `variable` (the EPM lesson). |
| 5 | in-document series timing | **shaped `time_reference`** (`sampling`: point/grid/enumerated); `sample_time` retired. |
| 6 | scalar vs dataseries boundary (#59) | **one axis test** — sampled metric axis ⇒ dataseries; else scalar (composite) or categorical; no third class. |
| 7 | `method` requiredness on observations | **optional** at the schema level (verb ≈ "measurement"); `variable` required. |

Counts: **202 document classes** (156 `stable`, 40 `draft`, 6 `deprecated`) +
3 meta files.

## Promotion to V1

Same procedure as V_delta: copy `schemas/V_zeta/` to `schemas/V1/`, freeze it,
replace the `"V_zeta"` value in `schema_version`/`index.json`, and tag. Before
promotion the `draft/` families (the genomics/omics + file-backed dataseries
data-format classes) are expected to be exercised against real corpora and
re-tiered to `stable/`.
