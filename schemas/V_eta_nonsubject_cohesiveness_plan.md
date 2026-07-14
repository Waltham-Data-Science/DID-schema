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

### 2.C Analysis / calc  *(~0.9k docs)*  — **DECOMPOSE (D-C)**

`*_calc`, `*_tuning`, `stimulus_response`, `hartley`, `reverse_correlation`,
`fitcurve`, `tuning_fit`. Exhibit: `orientation_direction_tuning` jams three
different kinds of thing into one doc. **Decision:** decompose, don't flatten and
don't defer wholesale:

1. **Interpretable scalar results → `*_observation`s on the subject.**
   `orientation_preference` (→ `angle_observation`), OSI / `hwhh` bandwidth (→
   `score_`/`angle_observation`), the ANOVA p-values (→ `score_observation`).
   These are *measured properties of the neuron-subject*; today they are bare
   `double`s buried in a nested `structure` with **no units, no ontology, no
   discoverability**. Promoting them to observations puts the biology on the
   queryable spine.
2. **The derived function (the tuning curve matrices) → a `data_body`** (a
   `sampled_body`/dataseries indexed by the independent variable), or a recompute
   **projection** if not stored.
3. **The computation itself → ONE generic `derivation` genus** — `derived_from`
   edges to inputs + the algorithm as an ontology term + a parameters block + the
   body-backed output. This carries the irreducible provenance (algorithm,
   parameters, measured-vs-fitted) an observation has no slot for.

**Retire the per-analysis class zoo** (`tuningcurve_calc`, `oridirtuning_calc`,
`contrast_/speed_/spatial_/temporal_frequency_tuning_calc`, `hartley_calc`,
`tuning_fit`, `fitcurve`, …) → the single `derivation` shape parameterized by the
algorithm *term*. This is the same anti-proliferation move J made on the
observation leaf tier (the `scalar_`/`dataseries_`/`imageseries_` split → one
class per data type). New V_eta class: **`derivation`** (a `data_body`-adjacent
provenance genus).

### 2.D Genomics / data-format  *(dataseries, timeseries, imageseries, expression_matrix, sequence_read, reference_\*)*  — **FOLD to `data_body`**

Fold all under the **`data_body`** model — `sampled_body` (regular index axis),
`opaque_body` (file blob), `table_body` deferred (J:193). Several are already
drafted this way. Mostly mechanical.

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
- **D-C** Analysis/calc — **RESOLVED:** decompose — interpretable scalars →
  `*_observation`s on the subject; curve → `data_body`/projection; provenance →
  ONE generic `derivation` genus; retire the per-analysis class zoo.
- **D-D** Round-trip — **RESOLVED (principle):** adopt J's *drop-fully-with-projection*
  — decompose bundles, store no provenance copy, reconstruct openMINDS/element
  *views* as query-time projections. The stricter "byte-exact `did_v1`
  reconstruction required?" question is **deferred** until something demands it;
  it does not block any phase.

---

*Companion to `V_eta_migration_plan.md`. Decisions 1–3 locked; Part 2 proposals
and Part 4 questions open. The subject-side work (the original plan D1–D11) is
unaffected; this plan extends cohesiveness to the non-subject half so V_eta can
be promoted to `V1` as one coherent schema.*
