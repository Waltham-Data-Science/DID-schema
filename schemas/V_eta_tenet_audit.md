# V_eta — tenet audit of the class set

*Audits every persisting + in-progress V_eta class against the tenets in
`V_eta_tenets.md` (T1–T12). Three buckets: **✅ fully conceived** (clean under all
tenets), **⚠️ needs reconsidering** (a tenet tension/violation to resolve), **❓ needs
deciding** (a genuinely open modeling call). Retired/consumed source classes are audited
only for "is the retirement decided" at the end. Snapshot: 166 persist + 11 in_progress;
tiers per `V_eta_final_class_set.md`.*

## Summary

| Bucket | Count | Where |
|---|--:|---|
| ✅ Fully conceived | ~140 | spine core, entities, dimensioned-quantity composites + their leaves, substances, time_reference family, data_body, the decided acquisition/infra |
| ⚠️ Needs reconsidering | 7 findings | `subject_calculation` placement + `app` coupling; the 5-way tuning-composite family; `stimulus_tuningcurve` raw-vs-fitted overlap; `ngrid`; `daqreader_image_epochdata_ingested`; `image`→`image_observation` coupling |
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

### R1 — `subject_calculation` is built on `app` and mis-shelved as infra. (T2, T7, T11)
`subject_calculation ⊂ [subject_interaction, app]` (abstract). Two problems:
- It is the **4th statement direction** (sibling of observation/manipulation/assertion),
  so it belongs in **① spine**, not ⑦ infra. It lands in ⑦ only because
  `regen_final_class_set.py`'s hardcoded `SPINE` set omits it. **Fix:** add
  `subject_calculation` to that SPINE set.
- Inheriting **`app`** couples every calculation leaf to a class that is itself
  `in_progress` (fate unresolved). A persist direction should not superclass an unsettled
  infra class. **Decide `app` first** (see D-app below); if `app` becomes a kept
  provenance block, make that explicit; if it dissolves, move the program/version record
  to fields on the calculation. Until then this is the one structural coupling from the
  finished calculator arc into an open class.

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

### R5 — `daqreader_image_epochdata_ingested` encodes a subtype in the name. (T11)
Chunk (c) de-encoded `_ndr` and `_mfdaq`, but the `_image` variant remains a named class.
T11 forbids a device/modality subtype in the name. **Reconsider:** fold the `_image`
variant into `daqreader_epochdata_ingested` with a modality field/parameter, OR confirm it
is a genuinely distinct cache *shape* (not just a modality label) and record why it earns
its own class.

### R6 — `image_observation` (persist) depends on `image` (in_progress). (coherence)
`image_observation` is a finished leaf, but `image` — its geometry mixin — is unsettled.
A persist class should not rest on an in_progress one. **Decide `image`** (D-image below):
keep it as a ⑦ geometry mixin, or fold its raster to `sampled_body`/`opaque_body` (T6) and
leave `image_observation` carrying only geometry fields.

*(R1/R6 share a root: two finished tiers (calculations, image observations) each rest on
one still-open infra class — `app`, `image`. Settling those two classes closes both.)*

---

## ❓ Needs deciding — the boundary classes

The 11 `in_progress` classes are the *edges of the model*: where a tenet does not yet
cleanly adjudicate. Each is framed as its open question.

| Class | The open question (tenet) |
|---|---|
| `app` | Kept ⑦ provenance/reproducibility block (persist), or dissolve into fields on the calculation? **Blocks R1** — calc leaves superclass it. (T7/T10) |
| `image` | ⑦ geometry mixin (persist), or fold raster → data_body (T6)? **Blocks R6.** |
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
