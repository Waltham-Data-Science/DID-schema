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

## Part 2 — Silent families (proposals — need decisions)

J does not specify these. Proposed J-cohesive dispositions to react to:

### 2.A Acquisition provenance — DAQ / sync / navigator  *(~20k docs)*

`daqsystem`, `daqreader*`, `daqmetadatareader*`, `filenavigator`, `syncrule`,
`syncgraph`, `syncrule_mapping`, `epochfiles_ingested`, `*_epochdata_ingested`,
`epoch*`. These describe *how the dataset was acquired/assembled*, not a subject.

> **Proposal A1 (recommended):** keep a thin **acquisition-provenance layer** as
> legitimate infrastructure (not everything is a subject; provenance isn't). But
> reconcile: the physical **instrument** becomes a `subject` (device-as-subject);
> the reader/nav/sync *configs* stay as infra that reference it.
> **Proposal A2:** model the DAQ device as a `subject` and each epoch as an
> `interaction`, dissolving the layer entirely (maximally J, largest rework).

### 2.B Stimulus  *(~5.5k docs)*

> **Proposal:** `stimulus_presentation` (+ `control_stimulus_ids`) → a
> **`subject_manipulation`** (the stimulus is delivered *to* the subject; its
> parameters are the manipulation value) — consistent with `stimulus_bath →
> dose_manipulation`. `stimulus_response_scalar*` (a computed response) → a
> **derived `*_observation`** with a `derived_from` edge to the presentation.

### 2.C Analysis / calc  *(~0.9k docs)*

`*_calc`, `*_tuning`, `stimulus_response`, `hartley`, `reverse_correlation`, fits.

> **Proposal:** keep a **derived-analysis layer** (these are *computed* products,
> not raw statements — collapsing them into observations would lose the
> computed-from provenance), but reconcile inputs (`element_id`→subject) and add
> `derived_from` relations. Open question: how much of this is in-scope for V_eta
> vs the NDI calculation layer.

### 2.D Genomics / data-format  *(dataseries, timeseries, imageseries, expression_matrix, sequence_read, reference_\*)*

> **Proposal (low-controversy):** fold all under the **`data_body`** model —
> `sampled_body` (regular index axis), `opaque_body` (file blob), `table_body`
> deferred (J:193). Several are already drafted this way. Mostly mechanical.

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
6. **stimulus + calc** — per the Part 2 decisions. *(2.B, 2.C)*
7. **acquisition-provenance** — per the 2.A decision (keep-as-infra reconcile, or
   dissolve). *(2.A)*
8. **schema cleanup** — delete every retired class from `V_eta/`; update
   `index.json`, `topics.json`, `test_veta.py`; re-run the full corpus with the
   orphan gate to confirm cohesive + green.

Each phase = one commit set across DID-schema (target classes / retirements) +
DID-matlab (migrators) + tests, validated by the quick CI then the full corpus.

## Part 4 — Open decisions (for sign-off)

- **D-A** Acquisition provenance: layer-as-infra (A1) or dissolve-to-subjects (A2)?
- **D-B** Stimulus: `stimulus_presentation` → `subject_manipulation`? responses →
  derived observations?
- **D-C** Analysis/calc: keep a derived layer, or push into observations / defer to
  the NDI calc layer?
- **D-D** Round-trip: is a lossless `did_v1` reconstruction a requirement (it
  constrains how aggressively we drop bundles), or is a forward-only migration
  acceptable?

---

*Companion to `V_eta_migration_plan.md`. Decisions 1–3 locked; Part 2 proposals
and Part 4 questions open. The subject-side work (the original plan D1–D11) is
unaffected; this plan extends cohesiveness to the non-subject half so V_eta can
be promoted to `V1` as one coherent schema.*
