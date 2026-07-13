# NDI DID-schema — Consolidated Schema & Data-Shape Reference

**What this is:** A durable, de-staled synthesis of two pre-compaction working docs (the schema-v2 dual-accessor / V_epsilon-latest plan, and the real-NDI-data-shape ground-truth study) for an agent working in the **DID-schema** repo. It carries forward the schema versioning model, the version-agnostic lineage-resolution mechanism, the structural facts that generate real work (diamond hierarchies, series-as-cardinality, the v1→v2 rename table), and the empirically observed document shapes/gotchas. Planning chatter tied to a specific moving SHA has been dropped or marked historical.

**Status legend:** ✅ still true · ⚠️ partially superseded (durable core kept, specifics historical) · ❌ historical/superseded

> **Re-anchor note (2026-07-13):** DID-schema's leading edge is now **V_zeta**. "V_epsilon" and every SHA/PR/branch below (`5a91a85`, `978a2ae`, PR #62, `claude/optimistic-ritchie-f06jvs`) are an **intermediate step — ❌ historical**. The *structural* facts V_epsilon introduced (observation-tier diamonds, series-as-cardinality, the identity-first spine, the conversion tables) persisted into V_zeta and are the durable content here. Always pin a SHA, never a branch — it's a sandbox schema heading to a future `V1` freeze.

---

## 1. Schema versioning model ✅

- **Version is set-level data.** A schema set's `index.json` carries `schema_version_value` (e.g. `"V_epsilon"` → now `"V_zeta"`) plus `legacy_schema_version_values` (e.g. `["did_v1","V_delta"]`). A document instance tags its own `document_class.schema_version`.
- **Absence ⇒ `did_v1`.** Producers still emit no `schema_version` on many docs; the inference rule is **absent ⇒ did_v1**, never V_delta/latest. Any version-select code must default to did_v1 on absence.
- **Segregate v1 and latest-v2 datasets** until a migrated corpus exists. The accessor reads each corpus in its own terms; **no on-read v1→v2 transform**. Producer-side migrators (Steve's DID-matlab / NDI-matlab) emit v2; we consume, we don't migrate on read.

## 2. The version-agnostic lineage mechanism (reference contract) ✅

Stored documents **self-describe their immediate superclasses identically in v1 and latest-v2**, and every accessor reads the stored doc (never an external schema set) for *read-path lineage*. This is why the dual-accessor is version-agnostic **for free** — it already resolves frozen v1 and the still-moving latest v2 without change.

Three consumers, one contract — each unions `class_name` + `definition`-derived name over `document_class.superclasses`, tolerating **array-or-single** shape:

| Stack | File / symbol | Notes |
|---|---|---|
| cloud-node | `api/src/dal/class_lineage.ts :: computeClassLineage` | **Reference implementation.** class_name-first union; handles array or single superclasses. |
| DID-python | `src/did/implementations/doc2sql.py :: _get_superclass_str` | Same class_name-first **union** (not fallback), both format branches; populates sqlite `meta.superclass`. |
| NDI-python | `src/ndi/document.py :: doc_superclass` | Same union; reads `class_name` directly for v2 (no file load); bundled `.json` used only for the legacy `{definition}` path (v1 defs ARE bundled). |

**Contract invariant:** `superclasses` may serialize as an **object/single on most classes but an array on some** (e.g. `stimulus_presentation`). Any new lineage consumer MUST normalize both. This is not hypothetical — see §6.

## 3. Diamond hierarchies → transitive isa closure ✅ (the real schema-side work)

The observation tier introduced **multiple inheritance** v1 never had. Example: `body_weight_observation isa {scalar_observation, scalar_mass}`, and both parents reach `base` by different paths. Stored docs carry only *immediate* superclasses, so `isa(ancestor)` for deep multi-parent classes requires a **transitive closure** (`all_ancestors` map) generated from the schema files.

- The prior `all_ancestors` / integrity work (audriB local branch `fix/v-delta-index-superclass-integrity`) was **V_delta-scoped — ⚠️ rebuild over the current edge (V_zeta).**
- Add a **multi-inheritance integrity assertion**: every observation leaf must resolve `base` through **both** parents.
- Confirm cloud-node / DID-python / NDI-python isa-closure consumers read the regenerated map.

## 4. series-as-cardinality — scalar values are ARRAYS ✅ (field-shape gotcha)

Every `scalar_*` shape-library mixin's `value` flipped `mustBeScalar: true → false`. **A scalar `value` is now an array, element-aligned with `sample_time`.** Any tool/reader that reads a scalar value as a single number is wrong under v2. This must be encoded in field catalogs, validators, and any downstream reader.

Shape-library mixins in play: `scalar_mass`, `_temperature`, `_pressure`, `_frequency`, `_voltage`, `_length`, `_score`, …

## 5. v1 → v2 conversion / rename table ✅

Machine-readable mapping tables live under `conversions/from_did_v1/` (prose + tables). Drive **all** renames off this single generated map — never scatter class-name literals. Known mappings:

| v1 | v2 |
|---|---|
| `treatment_drug` | `injection(kind:"drug")` |
| `virus_injection` | `injection(kind:"virus")` |
| `treatment_transfer` | `biological_transfer` |
| `treatment` | `procedural` / `environmental` / `temperature_manipulation` |
| `subject_group` | `subject(is_group:true)` |
| `ontology_table_row` | per-column observations |
| `projectvar` | deprecated |

The **identity-first spine** promoted draft→stable: `subject_statement` / `subject_assertion` / `subject_interaction`; the observation tier (`scalar_observation` + `categorical_observation` + ~25 concrete leaves like `body_weight_observation`, `core_temperature_observation`); manipulation tiers (`injection`, `bath`, `*_manipulation`); `time_reference` family; annotation/event classes. ~100 stable document classes at V_epsilon.

**Consumer-side coupling (⚠️ verify against current cloud-app, v3 editorial):** apply this table wherever the platform hard-codes v1 class names / field paths — historically cloud-app `table-column-definitions.ts`, the `imageStack→image_stack` normalizer, tool class assumptions.

## 6. Real document anatomy + shape gotchas ✅ (ground truth from live SQLite)

Envelope every doc carries:
`base{id, session_id, name, datestamp}` · `depends_on` · `document_class{class_name, class_version, superclasses}` · a class-named property block.

Real, thin, class-specific examples (from `2013_treeshrew_LGNctx`, 12,917 docs):
- **subject** (2 fields): `{local_identifier:"ts0822@fitzpatrick_duke", description:""}`
- **element** (5): `{ndi_element_class:"ndi.neuron", name:"tet_1", reference:2, type:"spikes", direct:false}` · depends_on → `underlying_element_id`, `subject_id`
- **stimulus_presentation** (12): carries an `app` provenance block (`ndi_app_stimulus_decoder`, MATLAB) · depends_on → `stimulus_element_id`

⚠️ **Two shape inconsistencies that MUST be tolerated everywhere:**
1. `depends_on` is an **array** on `element`, a single **object** on `stimulus_presentation`.
2. `superclasses` is an **object** on most classes, an **array** on `stimulus_presentation`.

Docs are **thin + class-specific (2–12 fields)** — "wide dynamic columns" is real only for stimulus/tuning, not most classes.

## 7. The document graph is PLUMBING-dominated ✅ (data-distribution ground truth)

Real class distribution over 12,917 docs (tree-shrew, raw/pre-analysis):

| class | count | kind |
|---|--:|---|
| syncrule_mapping | 2484 | 🔧 plumbing |
| epochfiles_ingested | 2484 | 🔧 plumbing |
| daqreader_mfdaq_epochdata_ingested | 2484 | 🔧 plumbing |
| stimulus_presentation | 1242 | 🔬 science |
| daqmetadatareader_epochdata_ingested | 1242 | 🔧 plumbing |
| control_stimulus_ids | 1242 | 🔧 plumbing |
| element_epoch | 1239 | 🔬 science |
| element | 290 | 🔬 science (probes/neurons) |
| filenavigator / daqsystem / daqreader | 39 each | 🔧 plumbing |
| syncrule | 26 | 🔧 plumbing |
| session | 14 | 🔬 science |
| syncgraph / daqmetadatareader / session_in_a_dataset | 13 each | 🔧 meta |
| subject | 13 | 🔬 science |
| dataset_remote | 1 | 🔧 meta |

- **~75% of documents are DAQ / sync / ingestion plumbing.** Scale is per-class and extreme within one dataset: 1 → 13–14 → 290 → 1242 → 2484, and the giant tiers are mostly plumbing (so scientist-facing counts stay modest).
- **Pipeline-state matters:** this dataset is **raw/mid-pipeline** (recordings + stimuli + DAQ; no `neuron_extracellular`, no `tuningcurve_calc`). Analyzed datasets (e.g. carbon-fiber: 743 docs with 17 sorted units + 160 tuning calcs) look completely different. Any consumer must handle **both raw (plumbing-heavy, pre-analysis) and analyzed**.

## 8. The 88-class taxonomy, in families ✅

- **Science grains:** subject, element (probe/neuron), element_epoch, neuron/neuron_extracellular, stimulus/* (presentation, response, response_scalar, tuningcurve), apps/calculators/tuningcurve_calc, apps/{kilosort,spikesorter,spikeextractor}/*, sorting/SpikeInterfaceSortingOutputs, probe/*, data/{image, imageStack→`image_stack`, ngrid, fitcurve}
- **Infrastructure (collapse by default):** daq/* (daqreader, daqsystem, syncgraph, syncrule, filenavigator), ingestion/* (`*_ingested`, `syncrule_mapping`, `epochfiles_ingested`), session_in_a_dataset, dataset_*
- **Metadata:** metadata/openminds* (subject/element/stimulus), epochid, app

## 9. Verification fixture (extend the cross-stack conformance test) ⚠️

Add a **latest-v2** document to the Leg-A conformance fixture; assert identical `isa()` in cloud-node + DID-python (both paths) + NDI-python:
1. **Multi-superclass observation** (`body_weight_observation`) → `isa("scalar_observation")` AND `isa("scalar_mass")` AND `isa("base")` all true (the diamond / transitive-closure case).
2. **series-as-cardinality** value (array `value` + `sample_time`) round-trips and doesn't break a scalar-expecting reader.
3. **Renamed/deprecated class** (`subject{is_group:true}`; `injection{kind:"drug"}`) resolves and maps back to its v1 source via the conversion table.
4. **A v1 (`did_v1`)** doc with `{definition}` superclasses resolves alongside v2 docs in the same corpus (the actual dual-read).

Blocked on: a real latest-v2 **test corpus**, which needs Steve's producer-side migrator PRs (DID-matlab #145 / NDI-matlab #826 territory).

## 10. What is historical / superseded ❌ ⚠️

- ❌ SHA/PR anchors: `5a91a85` (old blueprint anchor), `978a2ae` / PR #62 / `claude/optimistic-ritchie-f06jvs` (V_epsilon leading edge). Re-anchor to the current **V_zeta** SHA.
- ⚠️ **`WEB_PLATFORM_V2_BLUEPRINT.md`** and any "v2 explorer" design specifics — the web build is now **`feat/v3-editorial`** (v3 editorial / workspace-first, card-archetype dispatcher). Durable data-driven rationale that carried into v3: **curated science-grain rail + collapsed plumbing** (a flat browser is unusable on real data), **per-class scale tier** (compact/table/virtualized keyed off real counts), **per-class inline preview** (waveform/raster/tuning/stimulus-params, since docs are thin + class-specific), **depends_on graph as first-class provenance** (must tolerate array|object), **pipeline-state awareness** (raw dataset surfaces "what's next", not "empty").
- ⚠️ Leg-A dual-accessor **mechanism = done**; remaining work is the schema-derived artifacts (§3 transitive closure, §4 field catalog, §5 rename map, §1 NDI-python version-select of the bundled schema set), not a rewrite.

---

## Source docs (kept locally at ndi-projects root)
- `/Users/audribhowmick/Documents/ndi-projects/SCHEMA_V2_EPSILON_LATEST_UPDATE_2026-06.md` — dual-accessor → V_epsilon-latest plan (mechanism, diamond closure, series-as-cardinality, conversion table, verification).
- `/Users/audribhowmick/Documents/ndi-projects/REAL_NDI_DATA_SHAPE_2026-06.md` — real-data ground truth (plumbing-dominated distribution, document anatomy, array|object shape gotchas, 88-class taxonomy).
