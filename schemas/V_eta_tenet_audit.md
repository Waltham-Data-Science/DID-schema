# V_eta — tenet audit of the class set

*Audits every persisting + in-progress V_eta class against the tenets in
`V_eta_tenets.md` (T1–T13). Three buckets: **✅ fully conceived** (clean under all
tenets), **⚠️ needs reconsidering** (a tenet tension/violation to resolve), **❓ needs
deciding** (a genuinely open modeling call). Retired/consumed source classes are audited
only for "is the retirement decided" at the end. Snapshot: 166 persist + 11 in_progress;
tiers per `V_eta_final_class_set.md`.*

## Summary

| Bucket | Count | Where |
|---|--:|---|
| ✅ Fully conceived | ~140 | spine core, entities, dimensioned-quantity composites + their leaves, substances, time_reference family, data_body, the decided acquisition/infra |
| ⚠️ Needs reconsidering | 6 (R1–R6) | `subject_calculation` placement + `app` coupling; the 5-way tuning-composite family; `stimulus_tuningcurve` raw-vs-fitted overlap; `ngrid` bulk-data carrier; infra naming smells (T11/T13); `image`→`image_observation` coupling |
| ❓ Needs deciding | 11 in_progress + the deferred-retire migrations | the model's boundary classes + unfinished source folds |

---

## ✅ Fully conceived

These conform to the tenets by construction; no open questions.

- **① Spine core (12 of 13):** `base`, `data`, `data_body`, `data_type`, `entity`,
  `relation`, `directed_relation`, `undirected_relation`, `subject_statement`,
  `subject_assertion`, `subject_interaction`, `subject_observation`,
  `subject_manipulation`. These *are* the T1–T4 skeleton. (`subject_calculation` — the
  4th direction — is ⚠️, below.)
- **② Entities (8/8):** `dataset`, `funding`, `organization`, `person`, `publication`,
  `session`, `subject`, `web_resource` — T9, openMINDS parity. Clean.
- **③ Dimensioned-quantity composites (≈30):** `acceleration`, `amount`, `angle`,
  `angular_velocity`, `area`, `capacitance`, `charge`, `concentration`, `conductance`,
  `count`, `current`, `duration`, `energy`, `force`, `frequency`, `intensity`, `length`,
  `mass`, `ph`, `power`, `pressure`, `resistance`, `score`, `temperature`, `velocity`,
  `voltage`, `volume` — each a genuine unit-bearing quantity (T12 pass). Substances
  `chemical`, `dose`, `formulation` — structured value composites (T3). `visual_grating`
  — a genuine structured stimulus descriptor (T12 pass).
- **④ Leaf tier (≈72 of 78):** every `<quantity>_<direction>` leaf is mechanically clean
  under T11 (name = data type + stance, nothing else) and T3. Includes the one `term`
  family (`term_observation/manipulation/assertion`, T11), `date_assertion`,
  `numeric_assertion` (abstract parent), `dose_manipulation`, `visual_grating_manipulation`.
  (The 6 `*_calculation` leaves inherit the ③ tuning ⚠️; `image_observation` is ⚠️.)
- **⑤ time_reference family (8/8):** `time_reference` + `epoch_/event_/session_bounded_`
  and `_relative_reference` + `utc_reference` — regular `<origin>_<mode>_reference`
  naming (T11), the T6 timing model. Clean.
- **⑥ data_body (2/2):** `sampled_body`, `opaque_body` — **exactly two** (T6). Canonical.
- **⑦ Acquisition/infra, decided KEEP (most of 19):** `acquisition_epoch`, `epochid`,
  `epochfiles_ingested`, `daqsystem`, `daqreader`, `daqmetadatareader`,
  `daqreader_epochdata_ingested`, `daqmetadatareader_epochdata_ingested`, `filenavigator`,
  `syncgraph`, `syncrule`, `syncrule_mapping`, `directory`, `dataseries_channel_map`,
  `binaryseries_parameters`, `filter`. Device/sync/epoch acquisition layer (needs_ndi,
  T7-adjacent); the ⑥/⑦ walkthrough decided these KEEP. (`ngrid`,
  `daqreader_image_epochdata_ingested`, `subject_calculation` are ⚠️, below.)

---

## ⚠️ Needs reconsidering

Each is a concrete tenet tension with a recommended resolution.

### R1 — `subject_calculation` built on `app` + mis-shelved as infra. ✅ RESOLVED (Item 1)
`subject_calculation ⊂ [subject_interaction, app]` (abstract) had two problems, both now fixed:
- **Mis-shelved:** it is the 4th statement direction, so it belongs in ① spine, not ⑦
  infra — it landed in ⑦ only because `regen_final_class_set.py`'s `SPINE` set omitted it.
  Added to that set (spine 13→14).
- **`app` coupling:** decided `app` (D-app) → **`app` becomes a `software` ENTITY** (T9,
  ≈ openMINDS SoftwareVersion) referenced by a typed optional `software_id` edge on
  `subject_interaction` (T7 — the agent role, like `instrument_id`), plus an optional
  `execution_environment` block for the per-run os/interpreter. `subject_calculation`
  drops `app` from its superclasses (→ just `subject_interaction`), so the coupling to the
  open class is gone; `jCalculation` mints/dedups a `software` and sets `software_id`.
  Dedup by (name, version) across the corpus is a follow-up second pass. `app` itself is
  now superseded (retires once every generator extracts its block → a software entity).

### R2 — The five tuning composites are a look-alike family without a recorded T12 exception. (T12)
`orientation_direction_tuning`, `contrast_tuning`, `spatial_frequency_tuning`,
`temporal_frequency_tuning`, `speed_tuning` all share the skeleton
`{properties, tuning_curve, significance, fit}` and differ only in the fit form
(`vector` / `fitless` / `fit_no_speed` + `fit_fullspeed` / …). Under T12 this is the
canonical "prefer one parameterized composite" case — a single `tuning_curve` composite
whose independent variable is a field, with the fit as a variant sub-block. **The split is
defensible under T10** (one calculator → one document type), **but that rationale is not
recorded next to the classes**, which T12 requires. **Resolve one of:** (a) collapse to a
parameterized `tuning_curve` composite (+ keep the per-calculator *leaves* if T10 needs
distinct document types), or (b) keep the split and write the T10 rationale into each
composite's documentation. Recommendation: (a) — collapse the composites, keep the leaves.

### R3 — `stimulus_tuningcurve` (raw) overlaps the fitted tuning composites. (T3, T12)
`stimulus_tuningcurve` is a flat raw-curve shape (`independent_variable_*` +
`response_mean/stddev/stderr` + `control_*`); the five fitted composites re-express the
same curve as `tuning_curve` + add fits. Both fold to `*_calculation` leaves. This is the
raw-vs-analyzed overlap. If R2 collapses to a parameterized `tuning_curve`, **`stimulus_tuningcurve`
should be that shared base** (the raw curve) and the fitted composites should *reference/
extend* it, not re-declare it. Reconsider together with R2.

### R4 — `ngrid` is shelved as infra but carries bulk data. (T6)
`ngrid` keeps grid metadata (`ndims`, `dim_sizes`, `data_type`) in the body and the actual
N-dimensional array in a **file** (`ngrid_file`). By T6, a grid of sampled data is a
`sampled_body` (a multi-dimensional `datum` + descriptor), not a distinct infra carrier —
"encoding/format is a field, not a class." **Reconsider:** fold `ngrid` → `sampled_body`
(N-dim datum), OR justify it as a pure index/geometry descriptor that never holds the data
(it currently does). This also **blocks the hartley/RF calculator fold** (its receptive
field is an `ngrid`), so resolving R4 unblocks that deferral.

### R5 — Naming smells in the kept infra. (T11, T13)
- **Subtype-in-name (T11):** `daqreader_image_epochdata_ingested` — chunk (c) de-encoded
  `_ndr`/`_mfdaq` but the `_image` modality variant remains a named class. Fold it into
  `daqreader_epochdata_ingested` with a modality field, OR confirm it is a genuinely
  distinct cache *shape* (not just a modality label) and record why it earns its own class.
- **Container words (T13):** `binaryseries_parameters`, the `*_epochdata_ingested`
  caches (`data`/`ingested`), and `dataseries_channel_map` carry wrapper/altitude-noise
  words (`parameters`, `data`, `map`) — T13 says name the content, not the box. These are
  **needs_ndi acquisition infra whose names mirror the NDI implementation**, so the bar is
  lower and a rename is cross-repo (NDI writes these class names); treat as low-priority
  and only rename in lockstep with NDI, or accept the NDI-mirroring exception and note it.
  The high-value T13 wins are already banked (the v1 `stimulus_parameter_table` /
  `stimulus_response_scalar_parameters` container names are retired, not carried forward;
  `parameters` → `conditions`/`method_parameters`).

### R6 — `image_observation` depends on `image` (in_progress). ✅ RESOLVED (Item 2)
Decided `image` (D-image): it is **not** an entity (openMINDS has no Image type — an image
is a File = DATA, so its raster is a `sampled_body`, T6, unlike the citable `software`
agent). Reparented `image` from `base` → an **abstract `data_type` composite** (③) — the
geometry/format descriptor `image_observation` pairs with, exactly as `visual_grating` is
for `visual_grating_manipulation`. Dropped the redundant `image_file` (pixels already live
in the `sampled_body`: the `image_stack` migrator emits `storage_mode: body` + a
`sampled_body` and sets only the geometry block — zero `image_file` refs in any migrator)
and the dead `element_id` dep (D2). `image` now persists ③ via the abstract-data_type rule,
so `image_observation` couples to a settled composite. This also **sets the pattern for R4**
(`ngrid` → fold its grid to `sampled_body`, keep the grid descriptor).

---

## ❓ Needs deciding — the boundary classes

The 11 `in_progress` classes are the *edges of the model*: where a tenet does not yet
cleanly adjudicate. Each is framed as its open question.

| Class | The open question (tenet) |
|---|---|
| ~~`app`~~ | ✅ **RESOLVED (Item 1):** becomes a `software` ENTITY + typed `software_id` edge + `execution_environment` block (T7/T9). Retires once every generator extracts its block. |
| ~~`image`~~ | ✅ **RESOLVED (Item 2):** reparented to an abstract `data_type` composite (③, geometry descriptor); raster stays in `sampled_body` (T6); not an entity. |
| `instrument` | T7 says devices are subjects + an `instrument_id` edge → does the `instrument` *class* survive at all, or retire into `subject` + `term_assertion`? (leaning retire) |
| `interaction_purpose` | Is "purpose" a field/`method` qualifier on the interaction, a `term_assertion`, or a kept class? (T2/T11) |
| `stimulus_presentation` | The 2nd pass turns a *responded-to* presentation into `visual_grating_manipulation`; the rest passes through. Is a raw presentation always a `subject_manipulation`, or acquisition infra when nothing responds? (T3/T5) |
| `control_stimulus_ids` | A stimulus body-of-record; fate tied to `stimulus_presentation`. Field, edge, or kept? |
| `demo_ndi`, `demo_ndi_mock` | Test/demo fixtures — persist as `examples/`, or drop from the production set? |
| `openminds_import` | Provenance doc pinning the openMINDS release + crosswalk version — persist as ⑦/entity infra (likely yes), or fold into `dataset` provenance? (T9) |
| `projectvar` | Session/project key–value infra — persist as ⑦, or retire? |
| `ensemble` | Grain A (acquisition-infra map) is **decided** (`V_eta_ensemble_plan.md`); `member_of` is a runtime reconstruction, not migration. Arguably ready to **graduate to ⑦ persist** now — the only reason it is still in_progress is bookkeeping on the runtime step. |

### Also open — deferred source migrations still carried as passthrough (disposition `retire`, not yet done)
These are marked `retire` but their schemas still exist and their docs pass through; they
need their migrator finished (or confirmation of consumption) before phase-8 deletion:
- **Spike-sorting zoo remainder:** `spikewaves`, `spike_clusters`, `jrclust_clusters`,
  `neuron_extracellular`, `vmspikefit`, `vmspikesummary`, `vmspikefilteringparameters`,
  `vmneuralresponseresiduals`, `binnedspikeratevm`, `sorting_parameters`,
  `spike_extraction_parameters(_modification)`, `spike_interface_sorting_outputs`. Only
  `kilosort_/kiasort_clusters` fold so far (jSorterOutput). Decide the count/observation +
  `sampled_body`/`opaque_body` grain for the rest (T3/T6/T10).
- **Receptive-field family:** `hartley_calc`, `hartley_reverse_correlation`,
  `reverse_correlation` — should fold to a `subject_calculation` leaf like the tuning
  family (T10), blocked on R4 (`ngrid`→data_body).
- **Other passthrough retires** awaiting their fold/deletion: `element`, `openminds*`,
  `distance_metadata`, `ontology_label/_image/_table_row`, `probe_location/_geometry`,
  `position_metadata`, `electrode_offset_voltage`, `stimulus_response(_scalar*)`,
  `stimulus_parameter(_table)`, `site2channelmap`, `measurement`, `calculator`,
  `fitcurve`, `simple_calc`, `tuning_fit`, `pyraview`, `zarr`. Most have a documented plan
  (element→subject, ontology_*→observations D10/D11, distance→runtime); the audit flag is
  only that they are **not yet closed** (schema still present).

---

## Reading this audit

- **✅** classes need no action; they are the tenets realized.
- **⚠️ R1–R6** are the *model-internal* cleanups — resolvable by the schema team without
  new corpus evidence (naming/parsimony/coupling). R1+R6 hinge on deciding `app`/`image`.
- **❓** splits into (a) the 11 boundary classes needing a modeling call, and (b) the
  still-open source folds (mechanical migration work, tenet-clear but unfinished).

Recommended order: decide `app` + `image` (closes R1, R6, and 2 boundary classes) →
resolve the tuning composites R2/R3 (closes the biggest T12 tension) → `ngrid` R4 (unblocks
the RF fold) → the remaining boundary calls → the deferred source folds.
