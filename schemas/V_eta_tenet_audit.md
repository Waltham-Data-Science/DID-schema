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

## Walkthrough decisions & build queue (batching — decide now, build later)

The audit is being walked item-by-item; **decisions are recorded as we go and builds are
batched** (per the team's request) so we amass several before touching code.

| item | decision | built? |
|---|---|---|
| **R1** `app` → `software` entity + `software_id` edge + `execution_environment` | FINAL | ✅ built + green |
| **R6/`image`** full model | FINAL → `V_eta_image_model_plan.md` | ⏳ **build deferred** (5 tasks + a strand-bug fix) |
| **R4** `ngrid` → rename `array`, N-D-array `data_type`; **`image ⊂ array`** (re-audit: subclass, not parallel); RF family folds to calc leaves | FINAL (re-audit revised) | ⏳ **build deferred** (batched w/ image; also un-defers the RF fold) |
| **R2/R3** tuning composites → one `tuning_curve` data_type + **ARRAY** of `model_fit` + **typed queryable** summary scalars + one `tuning_curve_calculation` leaf | FINAL (re-audit revised: array + typed, not single bag) → `V_eta_tuning_model_plan.md` | ⏳ **build deferred** (7 tasks; re-targets the shipped calc folds — corpus re-verify required) |
| **R5** infra naming smells → RENAME in lockstep with NDI (not an accepted exception) | FINAL (targets to confirm w/ NDI) | ⏳ **build deferred** (cross-repo: DID-schema + NDI-matlab writers, landed together) |
| **boundary: instrument** → RETIRE | FINAL (evidence-audited: V_epsilon review class, no emitter) | ⏳ mark retire in `build_v_eta` markers |
| **boundary: projectvar** → **PASSTHROUGH** (re-audit: retire evidence was FALSE — it IS an ndi v1 source) | FINAL (re-audit corrected) | ⏳ keep green passthrough; corpus 0-doc check before any future retire |
| **boundary: demo_ndi(_mock)** → **PASSTHROUGH** (re-audit: drop evidence was FALSE — ndi sources; the cited test was misread) | FINAL (re-audit corrected) | ⏳ keep green passthrough; corpus 0-doc check before any drop |
| **boundary: interaction_purpose** → **KEEP as a standalone repeatable annotation class** (re-audit: reversed the retire→field call) | FINAL (re-audit revised) | ⏳ **build deferred** (standalone class: `purpose` term + comment; `interaction_id` multiple ≥1) |
| **boundary/stimulus: stimulus_presentation** → **`timed_sequence` model** (data_type + `timed_sequence_manipulation` leaf; references stimulus data_type docs; storage_mode multi-subject) — SUPERSEDES the dissolve | FINAL (re-audit) → `V_eta_stimulus_model_plan.md` | ⏳ **build deferred** (2nd-pass decompose; supersedes #19) |
| **boundary: openminds_import** → PERSIST + close emitter gap | FINAL (evidence-audited: nothing emits it) | ⏳ **build deferred** (maturity draft-vs-stable OPEN; openMINDS import path must stamp it) |
| **boundary: ensemble** → per-neuron primary + group-subject membership + derived cache; map doc dissolves | FINAL → `V_eta_ensemble_plan.md` | ⏳ **build deferred** (2nd pass: member_of + cache; verify-before-delete) |
| **raw-recording model** (voltage-attribution gap) → a `<modality>_observation` of the specimen (`instrument_id`→electrode), not device-attached data | FINAL → `V_eta_recording_observation_plan.md` | ⏳ **build deferred** (assembler migrator + modality map; 0-orphan re-verify) |

**Deferred-build queue (what to build once we batch):** the `image` model
(`V_eta_image_model_plan.md`, tasks 1–6, incl. the `image` migrator that fixes the strand
risk) + the `array`/RF fold (R4, same batch) + the tuning-curve collapse
(`V_eta_tuning_model_plan.md`, tasks 1–7, re-targets the shipped calc folds + corpus
re-verify) + `software` follow-ups (dedup pass; openMINDS `software` crosswalk). See the
TaskList.

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

### R2 — The five tuning composites collapse to one `tuning_curve` + an ARRAY of `model_fit`. 🟡 DECIDED (re-audit revised), build deferred (T12/T8/T10)
`orientation_direction_tuning`, `contrast_tuning`, `spatial_frequency_tuning`,
`temporal_frequency_tuning`, `speed_tuning` all share the skeleton
`{properties, tuning_curve, significance, fit}` and differ only in the fit form
(double-gaussian / Naka-Rushton / DoG-Movshon-spline / Priebe). **Decision** (see
`V_eta_tuning_model_plan.md`): collapse to **one parameterized `tuning_curve` `data_type`**
(the independent variable is a `variable` per T11, not a name suffix), with the fits as an
**ARRAY of `model_fit` entries** — each `{model (T8 controlled term), coefficients, goodness}`
— NOT a class per fit; new fits extend the `model` `value_set`. **Re-audit corrected two
defects in the first draft:** (1) `model_fit` MUST be an array — spatial/temporal-freq tunings
carry FIVE co-existing fits, a single slot would drop four; (2) the empirical summary scalars
(circular_variance, ANOVA p, c50/pref/bandwidth — all `queryable:true` today) stay **TYPED,
queryable fields**, NOT a `{name,value}` bag (flattening them was a real query regression), and
`vector`/`significance` are summaries, not `model_fit` entries (false stance otherwise, T13).
**T10:** the calculators keep folding id-preserving 1→1, but onto **one
`tuning_curve_calculation` leaf** (not five) — re-targets the already-shipped folds, so a
corpus re-verify (0-orphan invariant) is required.

### R3 — `stimulus_tuningcurve` (raw) IS the fit-less `tuning_curve`. 🟡 DECIDED, build deferred (T3, T12)
`stimulus_tuningcurve` is a flat raw-curve shape (`independent_variable_*` +
`response_mean/stddev/stderr` + `control_*`) — the pre-calculator-framework curve. **Decision
(with R2):** it is a `tuning_curve` with `model_fit` empty; its migrator maps the flat fields
into the `tuning_curve` composite. It does not re-declare the shape and the fitted composites
do not re-declare it either — all six are instances of the single `tuning_curve`
`data_type`. Recorded in `V_eta_tuning_model_plan.md`.

### R4 — `ngrid` → rename `array`, a generic N-D-array `data_type`. 🟡 DECIDED, build deferred
`ngrid` is the image model minus picture semantics: a labeled N-D numeric grid
(`ndims`/`dim_sizes`/`dim_labels`/`data_type`) whose bulk data was a file (`ngrid_file`),
`element_id`-scoped. Only `reverse_correlation` (→ `hartley_reverse_correlation` →
`hartley_calc`, the RF family) builds on it. **Decision** (applies the `image` model, T6;
`V_eta_image_model_plan.md`): rename `ngrid` → **`array`**, an abstract N-D-numeric-array
`data_type` composite, and make **`image ⊂ array`** *(re-audit revised the earlier "parallel,
not nested": `array` defines the shared N-D core once, `image` specializes it with
color/channels — parallel siblings would define the core twice, a T12 duplication)*; grid data
governed by `storage_mode` (inline small / body large: `opaque_body` default, `sampled_body`
for chunked reads);
descriptors always explicit (`dtype` ← `data_type`, `axes` ← `dim_sizes`/`dim_labels`); drop
`ngrid_file` + `element_id` (D2). **Payoff:** un-blocks the deferred RF fold —
`reverse_correlation`/`hartley_*` fold to `subject_calculation` leaves (like the 12 tuning
calculators; id-preserved, `software_id`, `derived_from`), RF map = the body-backed `array`
value. Build batched with the image build (TaskList #24).

### R5 — Naming smells in the kept infra. 🟡 DECIDED = RENAME IN LOCKSTEP, build deferred (T11, T13)
**Decision (user's call): do NOT accept the NDI-mirroring exception — RENAME these to T11/T13
compliance, coordinated with NDI-matlab so the class strings stay in sync.** Because NDI
writes these exact class strings, the rename is a **single cross-repo change** (DID-schema
class rename + `build_v_eta` markers + NDI-matlab writer strings + any migrator that reads the
old name), landed together. Build deferred to the batch; concrete target names below are
PROPOSALS to confirm with the NDI side (they own the writers and know the cache shapes).

- **Subtype-in-name (T11):** `daqreader_image_epochdata_ingested`. First resolve the FACTUAL
  question with NDI: is `_image` a genuinely distinct cache *shape*, or just a modality label
  on the same shape as `daqreader_epochdata_ingested`? **If modality variant → fold** into
  `daqreader_epochdata_ingested` + a modality field (T11). **If distinct shape → keep the
  class but still drop `_image`** and name the shape it actually is. Default assumption pending
  NDI confirmation: modality variant → fold.
- **Container words (T13):** name the content, not the box —
  - `binaryseries_parameters` → drop `parameters` (it's the binary-series read/layout spec);
    propose `binaryseries` or `binaryseries_layout` (confirm which is the content with NDI).
  - `dataseries_channel_map` → drop `map`; propose `dataseries_channel` (the channel
    assignment IS the content; `map` is the container word).
  - the `*_epochdata_ingested` caches (`data`/`ingested`) — hardest: `epochdata`/`data` is a
    container word and `_ingested` encodes provenance-state in the name. Propose naming the
    cache by what it holds; exact target to be agreed with NDI (these are the most
    implementation-mirroring names, so most likely to need the writer changed in lockstep).

  The high-value T13 wins are already banked (the v1 `stimulus_parameter_table` /
  `stimulus_response_scalar_parameters` container names are retired, not carried forward;
  `parameters` → `conditions`/`method_parameters`).

### R6 — `image` model. 🟡 DECIDED (full model), BUILD DEFERRED → `V_eta_image_model_plan.md`
The walkthrough went well past "R6 coupling": it worked out the whole `image` model. Item-2's
reparent (`image` `base` → abstract `data_type`, drop `image_file`/`element_id`) is COMMITTED
and correct as far as it goes, but the FINAL model changes the *fields* and adds a direction —
so R6 is **decided, not built**. Decisions (final; spec in `V_eta_image_model_plan.md`):
`image` is a `data_type` (a raster value) used across `image_observation` (measured) and a
NEW `image_manipulation` (shown as a visual stimulus); `storage_mode` governs only the pixels
(`inline` small / `body` opaque-default, sampled for huge chunked / `reference` opt-in for a
shared multi-subject FOV); **descriptors are always explicit on the composite** (`dtype`,
`axes`, `color_model`, `channels`, `value`) because `dtype` is *not* recoverable from an
inline matrix; modality → the `variable`; `image` is NOT an entity (openMINDS = File).
**Known bug to fix in the build:** the abstract reparent + no `image` migrator can strand
standalone encoded-`image` docs (needs an `image` → `image_observation` + `opaque_body`
migrator). Still **sets the pattern for R4** (`ngrid` → same treatment).

---

## ❓→✅ The boundary classes — ALL DECIDED (walkthrough, evidence-audited)

The 11 `in_progress` classes were the *edges of the model*. All are now decided. The
"clear-cut" ones were **evidence-audited**, and a later **fresh-eyes re-audit** (3 independent
adversarial reviewers + a check of the coverage ledger) **corrected two false-evidence calls**
(`projectvar`, `demo_ndi`) and **revised two more** (`interaction_purpose`, `stimulus_presentation`).
Builds deferred to the batch.

| Class | Decision (tenet) | Evidence / note |
|---|---|---|
| ~~`app`~~ | ✅ **Item 1:** `software` ENTITY + typed `software_id` edge + `execution_environment` block (T7/T9). | Built + green. |
| ~~`image`~~ | ✅ **Item 2/R6:** `data_type` composite, **`image ⊂ array`** (re-audit); raster by `storage_mode`; not an entity. | `V_eta_image_model_plan.md`. |
| `instrument` | ✅ **RETIRE** (T7). | **Audited (held up in re-audit):** provenance = V_epsilon "review/infra" — **not a did_v1 source**; no migrator emits it; the `instrument_id` edge already exists in `subject_interaction`. Retiring strands nothing. |
| `interaction_purpose` | ✅ **KEEP as a standalone repeatable annotation class** (`purpose` ontology_term + `comment`; `interaction_id → subject_interaction`, multiple ≥1). *(Re-audit REVERSED the earlier retire→field call.)* | A field loses: instance-level grouping (one purpose spanning several interactions), per-group comment, and immutability-safety (a field mutates a possibly machine-generated interaction). Standalone doc is J-compatible (annotation-as-document, T4). Corroborated by the ndi-next-steps `Interaction_Purpose_Proposal.md` + a reviewer. |
| `stimulus_presentation` | ✅ **`timed_sequence` model** → `V_eta_stimulus_model_plan.md`. *(Re-audit SUPERSEDED "always subject_manipulation / dissolve".)* | `timed_sequence` (data_type: ordered+timed refs to stimulus data_type docs) + `timed_sequence_manipulation` (leaf). Presentation is decomposed around its preserved id (not dissolved); multi-subject via `storage_mode`; stimulator → `instrument_id` (T7). Value-by-reference, same as recording/ensemble. |
| `control_stimulus_ids` | 🔄 **RE-OPENED** — how control-stimulus annotation attaches to a `timed_sequence_manipulation` (and vs the `stimulus_approach` curator class) is a pending walkthrough item. | Confirmed: it IS an ndi v1 source (not a cleanup); `app` superclass present (drop); `stimulus_presentation_id` is optional (presentation-less docs need a home); the `control_stimulus_id_method` struct must be carried. |
| `demo_ndi`, `demo_ndi_mock` | ✅ **PASSTHROUGH** (green, in_progress). *(Re-audit CORRECTED the earlier "drop from production".)* | The earlier evidence was FALSE: the coverage ledger lists `demoNDI`/`demoNDIMock` as **ndi v1 sources** (`in_progress`), and the cited `testConvertV1ToV2.m:385` is a `RenameClassNames=false` test (asserts `demo_ndi` absent because the rename was OFF), NOT a drop-safety proof. Corpus 0-doc check required before any future drop. |
| `openminds_import` | ✅ **PERSIST as ⑦ + CLOSE THE EMITTER GAP** (T9). Maturity `draft`-vs-`stable` still OPEN (re-audit flagged `stable` while it validates 0 docs). | **Audited:** schema exists (commit 4a20b46) but **NOTHING emits it** — no migrator, no importer, not even the round-trip CI test. Persisting is right (crosswalk/version provenance) ONLY paired with a *scheduled* emitter task; add to `V_eta_class_provenance.md`. |
| `projectvar` | ✅ **PASSTHROUGH** (green, in_progress). *(Re-audit CORRECTED the earlier "retire".)* | The earlier evidence was FALSE: the coverage ledger lists `projectvar` as an **ndi v1 source** (`in_progress`). Its `deprecated/` schema + no DID migrator is consistent with "vestigial," but "not a source" is disproven by the arbiter. Corpus 0-doc check required before any future retire. |
| `ensemble` | ✅ **RE-DECIDED** (supersedes grain A) → `V_eta_ensemble_plan.md`. | Per-neuron spike times = PRIMARY data (each neuron-subject); the ensemble is a **group subject** (id preserved, no own body) whose members are `member_of` edges (T1); the combined (times,ids) stream = an explicitly-**derived, rebuildable CACHE** (`sampled_body` + `derived_from` the neurons, T10; user asked to keep it). The per-epoch MAP/legend doc **dissolves** (column indices unnecessary once trains are keyed by subject id). `ensemble` kept for the group; `member_of` + cache built in the 2nd pass (needs file read + id resolution); verify-before-delete gate. |

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
