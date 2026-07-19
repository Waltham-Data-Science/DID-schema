# V_eta — Non-Subject Cohesiveness Redesign

*Amends `V_eta_migration_plan.md`. **Supersedes Part A.10** ("what carries over
verbatim"), which contradicted Brainstorm J's own text: A.10 lists `openminds*`
and `element/epoch*` as verbatim carry-overs, but the J source says openMINDS is
**not stored** (decomposed to assertions, J:92) and `element_epoch` /
`generic_file` / `expression_matrix_data` are **superseded** by the body model
(J:194). The first V_eta migration followed A.10 (1→1 fall-through), so the green
corpus run faithfully migrates ~24k documents into classes J says should not
exist. This plan makes the **non-subject** half of V_eta cohesive with J.*

## Decisions locked (this session)

1. **Implement J's decomposition** for the families J already decided (below).
2. **Fully retire `element`** — no `element` class; what it represented becomes a
   `subject` (device/part/derived signal) + the appropriate relation; acquired
   data lives in a `data_body`.
3. **Audit all non-subject families**, not just the ones J names.

## Guiding principle

Post-J, every stored document is one of: a **`subject`** (any identifiable thing —
organism, part, device, culture, derived signal), a **statement about a subject**
(`subject_assertion` / `_observation` / `_manipulation` leaf), a **`subject_relation`**
(`directed_`/`undirected_`), a **`time_reference`**, or a **`data_body`**
(`sampled_`/`opaque_`). The one genuinely-open question is whether **acquisition
provenance** (DAQ/sync/nav) is a legitimate *separate infrastructure layer* or
must also fold into this set — see Part 2.

---

## Part 1 — Decided families (concrete migration)

### 1.1 openMINDS → decompose to assertions  *(11,384 docs)*

`openminds_subject` (10,337), `openminds_element` (404), `openminds_stimulus`
(635), `openminds` (8). Each carries an `openminds` mixin block: an
`openminds_type` + a `fields` sub-struct (`species`, `geneticStrainType`,
`biologicalSex`, `backgroundStrain`, `ontologyIdentifier`, …).

**Migration:** for each populated `fields.*`, emit one **assertion on the
referenced subject** (the doc's `subject_id` / `element_id` / `stimulus_element_id`):
- ontology-valued fields (`species`, `strain`, `biologicalSex`, `cell type`, …)
  → **`term_assertion`** with `variable` = the D9 kind-variable, `value` = the
  ontology term. This is exactly what the **binding registry kind-variables**
  are for (species→`organism_species`, etc.).
- date fields (`dateOfBirth`) → **`date_assertion`**; numeric (`age`, `weight`) →
  the dimensioned `*_assertion`.
- Provenance decision (from the anchor Q): decompose fully; **do not** keep the
  bundle. openMINDS survives as *vocabulary* (the terms) + a *derived projection*
  (rebuilt at query time), never as a stored doc.

**Schema:** remove `openminds`, `openminds_subject`, `openminds_element`,
`openminds_stimulus` from V_eta.

### 1.2 `element` → retire to `subject` + relations  *(5,365 docs; blast radius 14 classes)*

Every `element` already has a `subject_id` (5,365/5,365): an element is a
device/signal **attached to** a specimen. Retire the class:

- **element → `subject`** (id preserved), kind asserted via a `term_assertion`
  (`ndi_element_class`/`type` → a device/signal ontology term; `name`/`reference`
  → `local_identifier`), plus a relation to its old `subject_id`:
  - a **recording device / probe** → `subject` (instrument) + a `member_of` /
    `part_of` edge to the specimen (device-as-subject, D2);
  - a **derived signal / neuron / cluster** → `subject` + a **`derived_from`**
    `directed_relation` to `underlying_element_id` (289 docs) and/or the specimen.
- **`element_id` dependents keep their reference** — because the target is now a
  `subject` doc with the same id, the 14 dependent classes resolve unchanged
  (the dep name may be normalized `element_id`→`subject_id`/`instrument_id`).

Blast radius (classes with an `element_id` edge, from the corpus):
`element_epoch` (6,886), `position_metadata` (2,078), `distance_metadata` (2,078),
`stimulus_presentation`/`stimulus_bath`/`openminds_stimulus` (via
`stimulus_element_id`), `openminds_element` (404), `stimulus_response_scalar`
(273), `hartley_calc` (210), `tuningcurve_calc` (84), `oridirtuning_calc` (42),
`neuron_extracellular` (21), `jrclust_clusters` (1).

### 1.3 `element_epoch` → `sampled_body`  *(6,886 docs)*

J:194 — `sampled_body` ← `element_epoch`. The ingested per-epoch data folds into a
`sampled_body` whose `statement` is the (now-subject) element's data-backed
`*_observation`; the `epoch_clock`/`t0_t1` become the body's `sample_time`.

### 1.4 `position_metadata` / `distance_metadata` → retire  *(4,156 docs)*

current_state:459 — retired as **projections over the element graph**. Migration:
- `position_metadata` (an element's atlas position) → a **`term_observation`** (or
  a spatial `*_observation`) about the element-subject.
- `distance_metadata` (between two elements) → a **relation** or a paired
  observation between the two element-subjects.

### 1.5 `generic_file` / `expression_matrix_data*` → `opaque_body`

J:194 — `opaque_body` ← `generic_file` and `expression_matrix_data`. Fold the
file-backed blobs into `opaque_body` under `storage_mode: opaque`.

---

## Part 2 — Silent families (resolved this session)

### 2.A Acquisition provenance — DAQ / sync / navigator  *(~20k docs)*  — **KEEP as infra + governance pass**

`daqsystem`, `daqreader*`, `daqmetadatareader*`, `filenavigator`, `syncrule`,
`syncgraph`, `syncrule_mapping`, `epochfiles_ingested`, `*_epochdata_ingested`,
`epoch*` describe *how the dataset was acquired/assembled*, not a subject.
**Decision (D-A):** they stay as a legitimate acquisition-provenance
**infrastructure layer** (provenance isn't "about a subject"; forcing a sync
rule to be a subject is a category error). The physical **instrument** becomes a
`subject` (device-as-subject) via the element retirement (1.2); the reader / nav
/ sync *configs* remain infra that reference it.

**But they are pre-J carry-overs and do NOT meet J governance.** An audit of the
retained classes found (see §Governance findings below): none of their
dependencies declare `must_refer_to_document_class` (untyped references — a
`daqreader_id` could point at anything and validate); structured payloads are
stored as raw `char` (`fileparameters`, `epochprobemap`, `parameters`,
`tab_separated_file_parameter`); the schema stores MATLAB class paths
(`ndi_<x>_class`); time is free strings (`epoch_clock: char`) not the
`time_reference` model; `files` is a string blob not the `data_body` model. A
**governance pass** brings them up to J standard — see the do-now vs needs-NDI
split in §Governance findings and Phase 7.

### 2.B Stimulus  *(~5.5k docs)*  — **RESOLVED (D-B); pass-1 = bodies-of-record, minting deferred**

The subject-side model is: `stimulus_presentation` (+ `control_stimulus_ids`) is
the manipulation's *value*, surfaced to the subject as a **`stimulus_manipulation`**
(a thin `subject_manipulation` that carries `subject_id` + `stimulus_presentation_id`
— the class already exists in `V_eta/stable`); `stimulus_response_scalar*` (a
computed response) is surfaced as a **derived `*_observation`**.

**Where each half runs (decided this session):**

- **`stimulus_presentation` / `control_stimulus_ids` → kept as bodies-of-record**
  in DID pass-1 (they already migrate 1→1 at **0 quarantine**). Minting the
  subject-side `stimulus_manipulation` is **deferred to the NDI second pass**
  (`ndi.migrate.local`, a sibling of `stimulusBathToBath`): the manipulation's
  true subject is the *animal recorded during the presentation's epochs*, which is
  **not in the presentation document** (it names only the stimulus system via
  `element_id`, now a subject). Resolving it is a recording-graph fact NDI owns.
  The NDI pass mints the `stimulus_manipulation` on the correct animal subject and
  a `presented_to`/`during` relation to the stimulus system. Minting it in pass-1
  on the in-document stimulus-system subject was rejected: it would hang the
  manipulation off the *deliverer*, not the recipient — an anti-cohesive handle.
- **`stimulus_response_scalar*` → kept as a body-of-record** in DID pass-1; the
  derived `*_observation` is **folded into the D-C analysis decomposition** (§2.C).
  The response payload is a complex-valued vector over stimulus index — the *raw
  tuning data* — so it shares D-C's decomposition and provenance model rather than
  getting a second, divergent shape here. (Its subject *is* resolvable in pass-1:
  `stimulus_response.element_id` → the recorded-neuron subject.)
- **Correction to the original phrasing:** a "`derived_from` edge to the
  presentation" does **not** typecheck — `directed_relation` is subject→subject and
  a `stimulus_presentation` is not a subject. The stimulus context therefore rides
  on the kept response body-of-record's `stimulus_presentation_id`, not a relation.

**Governance done now (D-B has settled the family):** `build_v_eta.py` §8d types the
one unambiguous edge — every empty `stimulus_presentation_id`
(`control_stimulus_ids`, `stimulus_response`, `stimulus_parameter[_table]`) →
`stimulus_presentation`. `stimulus_response_scalar.stimulus_response_id` stays
untyped pending referent-class review (its v1 antecedent pointed at a *parameters*
doc, not a response).

### 2.C The analysis tier — calc **and** spike-sorting  *(~0.9k + spike-sorting docs)*  — **DECOMPOSE (D-C, generalized)**

**D-C is not "calc" — it is the whole analysis tier.** The holdover audit found the
spike-sorting family (`spikewaves`, `spike_clusters`, `spike_extraction_parameters`,
`sorting_parameters`, `vmspikesummary`, `binnedspikeratevm`, `vmneuralresponseresiduals`,
`site2channelmap`, …, 11 classes) is the **same pattern** as the calc/tuning zoo —
a computation over raw data emitting scalars + signals + provenance — and had no J
disposition. Both are covered by one decomposition rule.

Calc exhibit: `orientation_direction_tuning` jams three kinds of thing into one doc.
Spike exhibit: `vmspikesummary` carries `mean_firing_rate`/`mean_vm` (scalars) while
`spikewaves` carries the waveform blob (a signal). **Decision:** decompose the whole
tier by output kind, don't flatten and don't defer wholesale:

1. **Interpretable scalars → `*_observation`s on the subject, `method` = algorithm.**
   Calc: `orientation_preference` (→ `angle_observation`), OSI/`hwhh` (→
   `score_`/`angle_observation`), the ANOVA p-values (→ `score_observation`).
   Spike: `mean_firing_rate` (→ `frequency_observation`), `mean_vm` (→
   `voltage_observation`). Measured properties of the neuron-subject; today bare
   `double`s in a nested `structure` with no units/ontology/discoverability.
   `subject_interaction.method` = the algorithm marks them *computed*.
2. **Derived signals → `data_body`.** The tuning curve / fit curve; the spike
   `spikewaves` blob; `binnedspikeratevm`; `vmneuralresponseresiduals` → a
   `dataseries_observation` + `sampled_body` on the neuron.
3. **A derived *unit that earns identity* → a derived subject.** A spike-sorted
   cluster IS a neuron (you record tuning from it): mint a `subject`, linked by
   `directed_relation(child=unit, parent=electrode-subject, relation=derived_from,
   method=spike_sorting)` — the folded provenance primitive (D-E), no bespoke class.
   A tuning result does **not** earn this (grain A, below).
4. **The computation itself → NO genus.** Provenance is `method` (on the outputs) +
   `directed_relation(derived_from)` (for derived units) + the extraction/sorting
   `*_parameters` carried as `method`/D10 `parameters`. There is no `calculation`
   class (rejected — see the scope note).

**Retire the analysis-tier zoo** — calc (`tuningcurve_calc`, `oridirtuning_calc`,
`contrast_/speed_/spatial_/temporal_frequency_tuning_calc`, `hartley_calc`,
`tuning_fit`, `fitcurve`, `simple_calc`, …) **and** spike-sorting (`spikewaves`,
`spike_clusters`, `vmspikesummary`, `binnedspikeratevm`, `*_parameters`, …) →
observations + `data_body` + relations. The same anti-proliferation move J made on
the observation leaf tier (the `scalar_`/`dataseries_` split → one class per data type).

#### D-C scope — **SETTLED (grain locked; impl pending)**

*Locked:* full curves as `data_body` (not projections); **grain A** for computed
*properties* (below); **tuning family first** (`tuningcurve_calc`, `oridirtuning_calc`
+ the `*_tuning` result classes, ~130 corpus docs), then the **spike-sorting family**
(same pattern), deferring `hartley_calc` / `reverse_correlation` (RF maps = big
spatial data → 2.D) and generic fits (`fitcurve` / `vmspikefit`).

*No provenance genus.* An earlier proposal minted a `calculation` leaf (under the
pre-J NDI `calculator`) to hold `source_document_id_#` links. **Rejected:** it
reinvents `directed_relation`/`derived_from`, J's provenance primitive (D-E); and
`calculator` is a pre-J NDI-app artifact J dissolves, not a genus to build on. The
decomposition uses **only** existing primitives — observations (`method` = algorithm),
`data_body`, and `directed_relation(derived_from)` for derived units.

*Grain — **LOCKED to A** for computed properties.* A tuning result / spike summary
is a **property of the neuron**, not a new entity: scalars → `*_observation`s on the
neuron with `method` = algorithm; curves/waveforms → `data_body` on the neuron; **no**
derived subject, **no** relation. Grain **B** (a derived subject + `derived_from`) is
**reserved for units that earn independent identity** — the canonical case being a
**spike-sorted cluster** (a neuron you then record tuning from): mint the subject,
link `derived_from` the electrode with `method=spike_sorting`. This is J's "cheap
representation until it earns full identity" ladder (`Multiresolution_Read_Proposal`).

*Honest boundary:* `directed_relation` is subject→subject, so "which *response
documents* fed this fit" is **not** an expressible edge — inputs are bodies-of-record;
their tie to the result is co-location on the same neuron + `method`. Accepted.

*Remaining open:* the scalar→ontology-term mapping (OSI, circular variance, the
p-values; `mean_firing_rate`, `mean_vm`) is D3/D6 term curation — seeded heuristically,
refined in discovery.

### 2.D Genomics / data-format  *(dataseries, timeseries, imageseries, expression_matrix, sequence_read, reference_\*)*  — **FOLD to `data_body`**

Fold all under the **`data_body`** model — `sampled_body` (regular index axis),
`opaque_body` (file blob), `table_body` deferred (J:193). Several are already
drafted this way. Mostly mechanical.

**DECISION — the header/payload split (Option 1, locked).** The two parallel data
models (`sampled_body`'s `datum`/`sample_time`/`summary`/bytes vs.
`dataseries_data`/`zarr`'s `axes`/`channels`/`storage` header) merge by SPLITTING,
not by fattening the body:
- **`sampled_body` stays LEAN** — `datum` + `sample_time` + `summary` + payload
  file, and (new) an **optional `axes`** for the non-time dims of a *multi-dimensional*
  body. That is the complete shape of a body that arrives **without a daq** (a
  derived/imported signal: the timeline is self-contained in `sample_time`, the
  value type in `datum`; there are no hardware channels, no native storage
  encoding, no acquisition axes). The #9 analysis tier mints huge numbers of these,
  so the common case must not carry empty header fields.
- **The acquisition header** — physical `channels`/gains, native `storage`/`codec`
  (incl. `zarr`), device `clocks`, the recording's `axes` — lives on
  **`acquisition_epoch`** (ex-`element_epoch`, which already carries axes/channels/
  storage), present exactly when there IS a daq and absent otherwise.
- **Fold each carrier** by routing its header → `acquisition_epoch` and its bytes
  → `sampled_body` (`opaque_body` for uninterpreted blobs: `image`,
  `image_collection`). `zarr` stays a storage-format descriptor (⊂ base); its
  format/codec becomes `acquisition_epoch.storage`. Worked example: `ephys_zarr`.
- The rationale is the "no daq" test: everything Option 1 moves onto the epoch is
  precisely *acquisition context*, which does not exist for derived/imported data —
  so it was never intrinsic to sampled data, and the lean body is the universal shape.

**Slices:** (A) `generic_file` → `opaque_body` ✅. (B) dissolve
`timeseries_data_{binary,csv,edf}` encoding-in-name subtypes ✅ (format is
`storage.format`). (C) ✅ dissolve the draft dataseries carrier family
(`dataseries_data`/`timeseries_data`/`imageseries_data`) — 0 migrator refs / 0
corpus presence, schema-only; `content_hash` preserved onto `sampled_body`;
`sampled_body.axes` (opt-in, multi-dim) landed. **`zarr` KEPT** — the references
showed it is the ⊂ base storage-recipe descriptor, load-bearing for `directory`'s
`zarr_implicit` manifest mode (derives chunk paths from the zarr recipe), matching
the hard-won fact. (D) — the OBSERVATION-TIER remainder. **`image` STAYS** (it is
`image_observation`'s geometry mixin — `image_observation` ⊂ `subject_observation`
+ `image`; referenced by 5 classes). **`image_collection` dissolved schema-only** ✅
(created by nothing — 0 refs in NDI/DID, not a did_v1 source class; intended fold →
`opaque_body`; corpus run is the presence probe, mirroring `generic_file`; if a
historical corpus carries one, add a split that mints an `image_observation` of its
`element_id` subject + `opaque_body`). **Still open (design-gated, NDI-coordinated):**
`ephys_zarr`/`image_zarr` (STABLE, possible corpus presence) and `pyraview`/
`dataseries_pyramid` are NOT mechanical — each carries an `element_id`→subject edge,
so folding = minting the OBSERVATION it is the value of (ephys → `voltage_observation`
of the probe-subject + `sampled_body`; imaging → `imageseries_observation` +
`sampled_body`; pyramid = a multi-resolution representation decision). This is the
same observation-tier fold as the imaging model captured under #9 — the subject is
already on the doc (element retirement), so a DID-side 1→N split can do it, but the
per-carrier target (variable term, single-vs-collection, which sampled_body shape,
pyramid levels) is a modeling call. Fold these WITH #9's observation tier.

## Governance findings — the retained acquisition-infra classes

The classes kept in 2.A carry pre-J shapes. Bringing them to J standard:

**Do-now (schema-side, no NDI dependency):**
- **Type every dependency** — ✅ **DONE** (`build_v_eta.py` §8c). Typed the unset
  `must_refer_to_document_class` on the unambiguous references: element / probe /
  device / agent refs (`element_id`, `underlying_element_id`, `probe_id`,
  `stimulator_id`, `recipient_id`, `donor_id`) → **`subject`** (44 deps —
  completing the element retirement, since the 8b rename only caught the ones
  already typed `element`), and the surviving acquisition classes
  (`filenavigator_id`, `daqreader_id`, `daqsystem_id`, `daqmetadatareader_id`,
  `syncrule_id[_#]`) → their class. References into families still being
  restructured (stimulus, calc, spike sorting) are left untyped until those
  settle. `syncrule_mapping.epochid` has no clean document target (epoch is not a
  standalone doc) and is left untyped.
- ~~Fix questionable ontology tags~~ — **withdrawn (false alarm):**
  `epochid.epochid` / `epochfiles_ingested.epoch_id` carry `iao:0000578`
  ("centrally registered identifier"), which is a correct *field-concept*
  annotation (the field holds an identifier), not a claim that the value is an
  ontology term. No change.
- **Declare the shapes** — `filenavigator.fileparameters` /
  `epochprobemap_fileparameters` / `epochprobemap`, `syncrule.parameters`,
  `daqmetadatareader.{metadata_names, tab_separated_file_parameter}`,
  `tuningcurve_calc.result_data`, `stimulus_response_scalar.responses`,
  `fitcurve.fit_parameters` → structured sub-fields, or a typed `opaque_body`
  when genuinely opaque file config.
- **Route time through `time_reference`** — `syncrule_mapping.epochnode_*.epoch_clock`
  and `epoch_id`, not bare `char`.
- **`epochfiles_ingested.files`** (string blob) → the `data_body`/`file` model.
- **Fix questionable ontology tags** — `epochid.epochid`,
  `epochfiles_ingested.epoch_id` are annotated `ONTOLOGY`, but an epoch id is not
  an ontology term.
- **De-encode subtypes from class names** — `daqreader_mfdaq_epochdata_ingested`
  puts the reader subtype in the class name; move it to a field/discriminator.

**Needs-NDI (coordinate with NDI-matlab):**
- **`stimulus_presentation` → `stimulus_manipulation` resolver** (D-B). A new
  `ndi.migrate.internal` function, sibling of `stimulusBathToBath`: for each kept
  `stimulus_presentation`, resolve the **animal recorded during its epochs** via
  the recording graph (presentation epochs → the element(s) recorded in them →
  `subjectOfElement`), then mint a `stimulus_manipulation` (`subject_id` = that
  animal, `stimulus_presentation_id` = the presentation, `variable` = the stimulus
  term) + a `presented_to`/`during` relation to the stimulus-system subject. The
  epoch→element→subject resolution is exactly the graph NDI already carries and
  the single-document DID migrator lacks.
- **`ndi_<x>_class` MATLAB class-path fields** (`ndi_daqreader_class`,
  `ndi_syncrule_class`, `ndi_filenavigator_class`, `ndi_daqsystem_class`, …).
  These are load-bearing — NDI reconstructs the reader/rule *object* from them.
  Dropping/reshaping them (→ a typed enum or ontology term, no `ndi_` namespace)
  requires a coordinated NDI object-model change, so it is scheduled with NDI
  input, not as a pure schema edit.
- **Probe-measurement J-ifications** (from the Part 5 misc triage):
  `electrode_offset_voltage` (`offset_voltages`/`voltage_units` on `probe_id`) →
  a `voltage_observation` on the probe-subject; `probe_geometry`
  (`channel_positions`/`num_channels`) → an observation / `data_body`. Both are
  **live NDI classes** actively written/read by NDI (`makeVoltageOffsets.m`,
  `plotProbeGeometry.m`, `site2channelmap`), so reshaping needs a coordinated NDI
  writer + migrator change, not a pure schema edit.

---

## Part 3 — Phasing (keep the corpus migrating between phases)

The migration must stay green (validate + 0 orphans) after each phase, so order
by dependency:

1. **Reconcile the plan** — rewrite A.10; add this document's target models to the
   per-class table (Part D). *(schema/docs only)*
2. **openMINDS decomposition** — self-contained; no other class depends on the
   openMINDS bundle. Retire the 4 classes. *(1.1)*
3. **element retirement** — the keystone; do it before its dependents so their
   references resolve to subjects. element → subject (+ kind assertion + relation);
   normalize `element_id` edges. *(1.2)*
4. **element_epoch → sampled_body; position/distance → observations.** *(1.3, 1.4)*
5. **data-format fold** — generic_file/expression_matrix → opaque_body; the
   genomics/series families → data_body. *(1.5, 2.D)*
6. **stimulus → manipulation/observation** *(2.B)*; **analysis → decompose**
   *(2.C)*: add the `derivation` genus, promote interpretable scalars to
   `*_observation`s, curve → body/projection, retire the per-analysis class zoo.
7. **acquisition-infra governance pass** *(2.A / Governance findings)*: do-now
   schema fixes (type every dep with `must_refer_to_document_class`; declare the
   `char`/`structure` payloads; time → `time_reference`; `files` → `data_body`;
   fix ontology tags; de-encode subtypes from class names). The `ndi_<x>_class`
   redesign is split out to coordinate with NDI-matlab.
8. **schema cleanup** — delete every retired class from `V_eta/`; update
   `index.json`, `topics.json`, `test_veta.py`; re-run the full corpus with the
   orphan gate to confirm cohesive + green.

Each phase = one commit set across DID-schema (target classes / retirements) +
DID-matlab (migrators) + tests, validated by the quick CI then the full corpus.

## Part 4 — Decisions (resolved this session)

- **D-A** Acquisition provenance — **RESOLVED:** keep as an infrastructure layer
  (not subjects), instrument→subject via 1.2, **plus a governance pass** to bring
  the classes to J standard (§Governance findings). `ndi_<x>_class` redesign
  deferred to coordinate with NDI-matlab.
- **D-B** Stimulus — **RESOLVED + dispositioned:** `stimulus_presentation` →
  `stimulus_manipulation` and `stimulus_response*` → derived `*_observation` remain
  the target model, but the **minting is deferred**: the manipulation to the **NDI
  second pass** (the animal subject is a recording-graph fact absent from the
  presentation doc), the response observation into **D-C** (it is the raw tuning
  data). DID pass-1 keeps `stimulus_presentation` / `stimulus_response_scalar` as
  bodies-of-record (already 0-quarantine) and types the settled
  `stimulus_presentation_id` edge (§8d). Note: `derived_from` cannot point at a
  presentation (not a subject); stimulus context rides on `stimulus_presentation_id`.
- **D-C** The analysis tier (calc **+ spike-sorting**) — **RESOLVED (grain locked):**
  D-C is generalized from "calc" to the whole analysis tier — the spike-sorting
  family (`spikewaves`/`spike_clusters`/`vmspikesummary`/`binnedspikeratevm`/
  `*_parameters`, found by the holdover audit) is the same pattern and shares this
  decomposition. Computed **scalars → `*_observation`s** (`method` = algorithm);
  **signals → `data_body`**; **derived units that earn identity → a derived subject**
  + `directed_relation(derived_from, method=…)` (per D-E — **no** `calculation`/
  `calculator` genus). **Grain LOCKED to A** for computed properties (a tuning result
  / spike summary is a property of the neuron, not a new entity); grain B (derived
  subject) reserved for spike-sorted units. Scope: tuning first, then spike-sorting;
  `hartley`/`reverse_correlation` + generic fits deferred. Open: scalar→term mapping
  (D3/D6). See §2.C.
- **D-E** `derivation` ↔ `directed_relation` redundancy — **RESOLVED (fold):**
  `derivation` (a V_epsilon/Brainstorm-E holdover) duplicated
  `directed_relation`'s provenance verbs (`derived_from`/`sample_of`/`aliquot_of`/
  `passage_of`) — a derivation doc was just a timed `derived_from` edge plus a
  `method`. **Retire `derivation`; fold into `directed_relation`** (`build_v_eta.py`:
  add to DELETE; add optional `method` field carrying the ex-`derivation_method`
  vocabulary; broaden `event_relative_reference`/`event_bounded_reference` anchors to
  `subject_interaction,directed_relation` so developmental anchoring — "P25" against
  the `biological_reproduction` event — still resolves now that the birth event is a
  relation, not an interaction). Zero corpus impact (nothing minted `derivation`).
  `test_veta` 553 pass. A birth is now `derived_from` + `method: biological_reproduction`
  + a `time_reference`; a dissection `sample_of` + `method: surgical_dissection`.
- **D-D** Round-trip — **RESOLVED (principle):** adopt J's *drop-fully-with-projection*
  — decompose bundles, store no provenance copy, reconstruct openMINDS/element
  *views* as query-time projections. The stricter "byte-exact `did_v1`
  reconstruction required?" question is **deferred** until something demands it;
  it does not block any phase.

---

## Part 5 — Holdover audit (full-schema coverage sweep)

Every V_eta `class_name` (266) was cross-referenced against all three plan docs to
find classes carried over from V_zeta with **no explicit J disposition**. Excluding
the ~130 J-native leaves (the `*_observation`/`*_assertion` data-type tier + time
references, covered by pattern), the undiscussed holdovers and their dispositions:

| Family | n | Disposition |
|---|--:|---|
| **spike-sorting** (`spikewaves`, `spike_clusters`, `vmspikesummary`, `binnedspikeratevm`, `*_extraction/sorting_parameters`, `vmneuralresponseresiduals`, `site2channelmap`, …) | 11 | **→ D-C (analysis tier).** Same decomposition: scalars (`mean_firing_rate`→`frequency_observation`, `mean_vm`→`voltage_observation`) → observations; `spikewaves`/`binnedspikeratevm` → `data_body`; a sorted **cluster → a derived subject** (grain B); `*_parameters` → `method`/D10 `parameters`. |
| data-representation (`ephys_zarr`, `image_zarr`, `image_collection`, `dataseries_pyramid`, `dataseries_channel_map`, `binaryseries_parameters`, `ngrid`, `pyraview`) | 8 | array/blob reps → `data_body`/`opaque_body` (**2.D**); `ngrid`/`*_channel_map`/`binaryseries_parameters` → kept **index/geometry infra** (governance-only). |
| acquisition/epoch infra (`daq*_epochdata_ingested`, `daqreader_ndr`, `epochclocktimes`, `oneepoch`, `valid_interval`, `session_extent`) | 7 | **→ D-A** governance umbrella (kept as infra; type deps, declare shapes). Enumerated here so they are no longer implicit. |
| dataset/session infra (`dataset_remote`, `dataset_session_info`, `session_in_a_dataset`) | 3 | **→ DISSOLVE to relations (D-F).** `session` joins the `entity` genus, so session↔dataset membership is a first-class `directed_relation` (`session -part_of-> dataset`, `sequence`=index), and the remote copy is `dataset -stored_at-> web_resource -hosted_by-> organization`. See §D-F. |
| misc NDI | 11 | **triage — on inspection, ZERO safe deletions** (the audit's "delete cruft" was wrong; all are load-bearing): `demo_ndi`/`demo_ndi_mock` are recognized `did_v1` source classes (`demoNDI`/`demoNDIMock` renames) **and** migration-test fixtures (`testConvertV1ToV2`); `projectvar` is a **live NDI class** (`projectvardef.m`); `image_stack_parameters` is read by the **active `image_stack` migrator** + tests → **KEEP all four**. **J-ify measurements → needs-NDI** (not cleanup): `electrode_offset_voltage` (→ `voltage_observation`) and `probe_geometry` (→ observation/`data_body`) are **live NDI classes** (`makeVoltageOffsets.m`, `plotProbeGeometry.m`, `site2channelmap`); reshaping needs a coordinated NDI writer + migrator change → moved to the needs-NDI list. Keep true infra (`directory`, `ndi_reserved_keys`, `metadata_editor`, `interaction_purpose`). |
| genomics/data-format (`expression_matrix_data_*`, `reference_*`, `sequence_read_data_*`, `timeseries_data_*`, …) | 32 | already **= 2.D** (draft `data_body` subtypes). |

After this sweep, every non-leaf class has a disposition: an analysis-tier decompose
(D-C), a `data_body` fold (2.D), or a D-A infra/governance **keep**. The misc-triage
inspection found **no safe deletions** — every "cruft" candidate is a recognized
source class, a test fixture, a live NDI class, or an active migrator dependency, so
all are kept. **Open items** left: the D3/D6 term mapping; the two probe-measurement
J-ifications (`electrode_offset_voltage`, `probe_geometry` → needs-NDI); and the
per-class spike-sorting decomposition detail (to be written when D-C is implemented).

## D-F — Entity model: dataset metadata + the dataset/session containers

The metadata redesign (this session) makes referenceable identities a genus,
`entity`, over `subject`, `person`, `organization`, `publication`, `award`,
`dataset`, `web_resource`, and now **`session`**. Each carries a
`global_identifier[]` {scheme, value}; all cross-entity relationships are
`directed_relation`s at the entity layer, enumerated in the D6 **relation
vocabulary** (`binding_registry_meta.json → relation_vocabulary`).

**Decided target models:**

- **`metadata_editor` → dataset entity + relations** — DONE (`migrators_j/
  metadata_editor.m`): the NDIMetaDataEditorApp `metadata_structure` blob → a
  `dataset` + `person`/`organization`/`award`/`publication`/`web_resource` entities
  + `has_author`(seq)/`affiliated_with`/`funded_by`/`issued_by`/`cites`/
  `documented_by` edges. Projections (species/technique lists) and GUI state dropped.
- **`session` ⊂ `entity`** — DONE (schema): the most-referenced identity gains
  `global_identifier` and becomes a valid relation endpoint. No blast radius —
  existing `session_id` deps still resolve (must_refer is declarative).
- **`session_in_a_dataset` / `dataset_session_info` → `session -part_of-> dataset`**
  — DECIDED, migrator DEFERRED. The membership is a `directed_relation`
  (`sequence`=session index); `is_linked` rides the edge; `session_creator*` is
  session-construction provenance. Deferred because the `dataset` parent must
  resolve to a real `dataset` entity, and today only editor-metadata datasets mint
  one → needs the **bare-`dataset`-per-dataset** decision + a cross-doc second-pass
  resolver (same shape as Path-S subject minting / the deferred-bath pass).
- **`dataset_remote` → `dataset -stored_at-> web_resource -hosted_by-> organization`**
  — DECIDED, migrator DEFERRED. The cloud id + `remote_type` become the
  web_resource's `global_identifier` {scheme, value}; the remote org is a
  `hosted_by` edge. Deferred for the same cross-doc reason (`dataset_remote`
  carries no dep on its local dataset — the link is by co-location, so a second
  pass supplies the `stored_at` parent).

**Blocking sub-decision for the two deferred dissolutions:** does *every* dataset
get a minted bare `dataset` entity (so session/remote edges always resolve), or
only datasets with editor metadata (leaving editor-less datasets' containers as
un-dissolved infra)? This is separable and is the next call on this track.

---

*Companion to `V_eta_migration_plan.md`. The subject-side work (the original plan
D1–D11) is unaffected; this plan extends cohesiveness to the non-subject half so
V_eta can be promoted to `V1` as one coherent schema. Decisions D-A…D-F resolved
(D-F migrators partially deferred on the bare-dataset-entity call); Part 5 closes
full-schema coverage.*
