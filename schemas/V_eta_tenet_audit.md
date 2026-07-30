# V_eta — tenet audit of the class set

*Audits every persisting + in-progress V_eta class against the tenets in
`V_eta_tenets.md` (T1–T13). Three buckets: **✅ fully conceived** (clean under all
tenets), **⚠️ needs reconsidering** (a tenet tension/violation to resolve), **❓ needs
deciding** (a genuinely open modeling call). Retired/consumed source classes are audited
only for "is the retirement decided" at the end. Snapshot: 162 persist + 9 in_progress;
tiers per `V_eta_final_class_set.md`.*

## Summary

| Bucket | Count | Where |
|---|--:|---|
| ✅ Fully conceived | ~140 | spine core, entities, dimensioned-quantity composites + their leaves, substances, time_reference family, data_body, the decided acquisition/infra |
| ⚠️ Needs reconsidering | 6 (R1–R6) | `subject_calculation` placement + `app` coupling; the 5-way tuning-composite family; `stimulus_tuningcurve` raw-vs-fitted overlap; `ngrid` bulk-data carrier; infra naming smells (T11/T13); `image`→`image_observation` coupling |
| ❓ Needs deciding | 9 in_progress + the deferred-retire migrations | the model's boundary classes + unfinished source folds |

---

## Walkthrough decisions & build queue (batching — decide now, build later)

The audit is being walked item-by-item; **decisions are recorded as we go and builds are
batched** (per the team's request) so we amass several before touching code.

| item | decision | built? |
|---|---|---|
| **R1** `app` → `software` entity + `software_id` edge + `execution_environment` | FINAL | ✅ built + green |
| **R6/`image`** full model | FINAL → `V_eta_image_model_plan.md` | ✅ **built + corpus-green** (run #251, see gate record below). `image` is a standalone `data_type` with one `value` cell (T14). |
| **R4** `ngrid`/`array` → **`array` KILLED** (re-audit): `ngrid` **phases into `sampled_body`** (a carrier, T6; a generic array duplicates the body + names a container, T13); **`image` is standalone** (reverses `image ⊂ array`); RF family folds to calc leaves w/ **`sampled_body`-valued** maps | FINAL (re-audit revised) | ⏳ **build deferred** (batched w/ image) |
| **R2/R3** tuning composites → one `tuning_curve` data_type + **ARRAY** of `model_fit` + **typed queryable** summary scalars + one `tuning_curve_calculation` leaf | FINAL (re-audit revised: array + typed, not single bag) → `V_eta_tuning_model_plan.md` | ✅ **built + corpus-green** (run #251). The required re-verify of the re-targeted calc folds is DONE: 0 orphans on all 5 corpora, so the id-preserving 1→1 fold survived the re-target. |
| **R5** infra naming smells → RENAME (T11/T13). Proposed targets: `binaryseries_parameters`→`acquisition_layout`, `dataseries_channel_map`→`channel_assignment`, `*_epochdata_ingested`→`<device>_epoch_cache`, `daqreader_image_*`→fold+modality field | **RE-OPENED — awaiting review.** An earlier naming pass marked these FINAL, but the ⑦ walkthrough re-opened the whole infra tier ("the KEEP predated T11/T13 scrutiny; needs a naming + governance confirmation"), which covers four of these five classes. A build was started on the strength of the old FINAL marking and **reverted** — the targets need confirming first. | ⏳ **not built** (all five back to `in_progress`). Useful finding kept from the attempt: the rename is **DID-only**, NOT a cross-repo lockstep — every NDI hit is a v1 WRITER and `+migrate/` has no V_eta-side reader of these strings, same as `element_epoch`. Also still open: the factual `_image` question for NDI. |
| **boundary: instrument** → RETIRE | FINAL (evidence-audited: V_epsilon review class, no emitter) | ⏳ mark retire in `build_v_eta` markers |
| **boundary: projectvar** → **PASSTHROUGH** (re-audit: retire evidence was FALSE — it IS an ndi v1 source) | FINAL (re-audit corrected) | ⏳ keep green passthrough; corpus 0-doc check before any future retire |
| **boundary: demo_ndi(_mock)** → **PASSTHROUGH** (re-audit: drop evidence was FALSE — ndi sources; the cited test was misread) | FINAL (re-audit corrected) | ⏳ keep green passthrough; corpus 0-doc check before any drop |
| **boundary: interaction_purpose** → **KEEP as a standalone repeatable annotation class** (re-audit: reversed the retire→field call) | FINAL (re-audit revised) | ⏳ **build deferred** (standalone class: `purpose` term + comment; `interaction_id` multiple ≥1) |
| **boundary/stimulus: stimulus_presentation** → **`timed_sequence` model** (data_type + `timed_sequence_manipulation` leaf; references stimulus data_type docs; storage_mode multi-subject) — SUPERSEDES the dissolve | FINAL (re-audit) → `V_eta_stimulus_model_plan.md` | ⏳ **build deferred** (2nd-pass decompose; supersedes #19) |
| ~~**boundary: openminds_import** → PERSIST + close emitter gap~~ **REVERSED 2026-07-30 → REMOVED** | REVERSED (team sign-off) | ✅ removed from the built set. The original call persisted it ONLY on the condition that an emitter be scheduled -- none ever was, so it validated zero documents, had no migrator and no importer, and was not even exercised by the openMINDS round-trip test. It is a V_eta invention, not a did_v1 source, so removal strands nothing. Re-add when there is an import path to stamp it; at that point decide whether it is a class at all or a `software` reference, since `crosswalk_version` is the version of a translation program. |
| **boundary: ensemble** → per-neuron primary + group-subject membership + derived cache; map doc dissolves | FINAL → `V_eta_ensemble_plan.md` | ⏳ **build deferred** (2nd pass: member_of + cache; verify-before-delete) |
| **raw-recording model** (voltage-attribution gap) → a `<modality>_observation` of the specimen (`instrument_id`→electrode), not device-attached data. Re-audit: **multi-channel = one obs w/ channel axis**; **unknown modality = bare self-describing `sampled_body` value + `modality_unresolved` flag (Guard A, never a `timeseries_observation`/`array`), gated to 0 fallbacks** | FINAL → `V_eta_recording_observation_plan.md` | ⏳ **build deferred** (assembler migrator + modality map; 0-orphan AND 0-fallback re-verify) |

**Deferred-build queue (what to build once we batch):** the `ngrid`→`sampled_body` / RF fold
(R4; `array` killed) + `software` follow-ups (dedup pass; the openMINDS `software` crosswalk
is partially landed — `SoftwareVersion` mapped, exhaustive property parity still blocked on
access to the authoritative openMINDS property surface). See the TaskList. *(The `image` model
and the tuning-curve collapse have LEFT this queue — both are built and corpus-verified.)*

### Corpus gate record — run #251 (2026-07-28)

DID-matlab `test-code.yml` run **#251**, DID-matlab `324b776` / DID-schema `4b4f81d`,
branch `claude/v-eta-migration-plan-35jj1z`. Duration 145 min. **373/373 tests passed,
0 failed, 0 incomplete.**

| corpus | source docs | migrated | edges | orphans | quarantine |
|---|---|---|---|---|---|
| 20211116 | 1,220 | 1,484 | 2,644 | **0** | **0** |
| B | 12,917 | 13,778 | 17,424 | **0** | **0** |
| Dab | 27,561 | 110,086 | 102,167 | **0** | **0** |
| JH | 78,688 | 435,881 | 615,005 | **0** | **0** |
| Soph | 101,427 | 181,760 | 280,969 | **0** | **0** |

This is the first full-corpus gate covering, in one run: the tuning-collapse re-target, the
`image` `value`-cell normalization (T14), the `contrast_sensitivity` reshape (RB/RBN/RBNS →
`model_fit` array), the `term`/`date` composites across all 17 emission sites (incl.
`resolveDeferredBaths`), and group A (27 assertions repointed, `numeric_assertion` deleted).
R5 is NOT in this run — it was reverted pending review.

Two things worth flagging beyond the pass/fail: **(1)** JH quarantine is now **0** — the
~2078 `distance_metadata` "required `endpoints` missing" quarantines are gone, cleared by the
flat→nested `endpoints` reshape. **(2)** Routing inventory reports **0 unmatched term routes
to `generic_*`** on every corpus, so no document fell through to a generic class.

## Naming pass — FINAL decisions (T11/T12/T13)

All names below are decided (no longer "provisional"):
- **Tuning** (`V_eta_tuning_model_plan.md`): fit entry = `{model` (bare bound term, matching
  `color_model` — NOT `model_name`), `coefficients` (NOT `parameters`, a T13 v1 smell),
  `goodness}`; metric sub-blocks **`significance` / `circular_statistics` / `interpolated_values`**
  (the `derived_summary` bag is KILLED — failed the T13 "predict the content" test, overloaded
  "derived").
- **Stimulus** (`V_eta_stimulus_model_plan.md`): data_type **`timed_sequence`** + leaf
  **`timed_sequence_manipulation`** (neutral so a future `_observation` leaf is possible);
  control annotation **`control_designation`** (was `control_stimulus_ids` — drops the `ids`
  container word).
- **`software`** (R1): **KEEP `software`** (not `software_version`). It's the reusable entity;
  `version` is a *field*, not part of the name (T13 — name the thing, not a coordinate). The
  openMINDS crosswalk maps it to `SoftwareVersion`; parity is a crosswalk-entry concern, not a
  rename.
- **R5 infra** (cross-repo, NDI lockstep): `binaryseries_parameters` → **`acquisition_layout`**;
  `dataseries_channel_map` → **`channel_assignment`**; `*_epochdata_ingested` →
  **`<device>_epoch_cache`**; `daqreader_image_epochdata_ingested` → **fold** + modality field.
  (Kills every T11/T13-banned word: `binary`/`series`/`data`/`map`/`parameters`/`ingested`/`_image`.)
- **`array`** — N/A (KILLED; not a data_type). `image` stays `image`.
- **`ngrid`** — retired (phases into `sampled_body`), so no go-forward name.

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
  (The one `tuning_curve_calculation` leaf inherits the ③ tuning ⚠️; `image_observation` is ⚠️.)
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

### R4 — `ngrid`/`array`: **`array` KILLED**; `ngrid` → `sampled_body`. 🟡 DECIDED (re-audit REVISED), build deferred
`ngrid` is a labeled N-D numeric grid (`ndims`/`dim_sizes`/`dim_labels`/`data_type`) whose bulk
data was a file (`ngrid_file`), `element_id`-scoped. Only `reverse_correlation` (→
`hartley_reverse_correlation` → `hartley_calc`, the RF family) builds on it. **Decision (final
re-audit):** do **NOT** mint an `array` `data_type` — a bare N-D numeric grid is a *storage*
concept that (a) duplicates `sampled_body` (T6: `sampled_body` is already "self-describing —
axis + typed datum"), and (b) names a container, not content (T13). So:
- **`ngrid` phases into `sampled_body`** like every other carrier (T6); drop `ngrid_file` +
  `element_id` (D2). Not a `data_type`.
- **`image` is a STANDALONE `data_type`** (reverses the earlier `image ⊂ array` — with no
  `array` parent there is nothing to duplicate; `image` is a meaningful raster).
- **RF fold:** `reverse_correlation`/`hartley_*` fold to `subject_calculation` leaves
  (id-preserved, `software_id`, `derived_from`), the RF map = a **`sampled_body`** value (meaning
  on the leaf's `variable`), **not** an `array`.
- Meaningful numeric arrays (`kernel`, a specific RF type) → their own named `data_type` only
  when T12 warrants; never a generic `array`. Build batched with the image build (TaskList #24).

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
- **Container/format/cardinality words (T11/T13) — apply the grammar FULLY** (the re-audit
  flagged the first-round targets as half-renames that left `binary`/`series`/`data` alive).
  **NAMING PASS final proposals** (kill every banned word; confirm + land in lockstep with NDI):
  - `binaryseries_parameters` → **`acquisition_layout`** (drops `binary`=format, `series`=
    cardinality, `parameters`=container; the content is the read/byte-layout spec for a raw
    acquired stream).
  - `dataseries_channel_map` → **`channel_assignment`** (drops `data`+`series`+`map`; the
    content is which channel is what).
  - the `*_epochdata_ingested` caches → **`<device>_epoch_cache`** (e.g.
    `daqreader_epoch_cache`; drops `data`/`ingested` — "cache" honestly names what it is per
    the new T6 cache concept, `epoch` is the legitimate scope).
  - `daqreader_image_epochdata_ingested` → **fold** into `daqreader_epoch_cache` + a modality
    field (default: `_image` is a modality variant, T11), unless NDI confirms a genuinely
    distinct cache *shape* (then keep a distinct class but still drop `_image`).

  The high-value T13 wins are already banked (the v1 `stimulus_parameter_table` /
  `stimulus_response_scalar_parameters` container names are retired, not carried forward;
  `parameters` → `conditions`/`method_parameters`). **These target names are DECIDED
  (T11/T13-clean); the only NDI dependency is the cross-repo lockstep landing + confirming the
  `_image` shape question — a build-coordination fact, not a deferred decision.**

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
| ~~`image`~~ | ✅ **Item 2/R6:** standalone `data_type` composite (**`array` KILLED** — image does not subclass anything); raster by `storage_mode`; not an entity. | `V_eta_image_model_plan.md`. |
| `instrument` | ✅ **RETIRE** (T7). | **Audited (held up in re-audit):** provenance = V_epsilon "review/infra" — **not a did_v1 source**; no migrator emits it; the `instrument_id` edge already exists in `subject_interaction`. Retiring strands nothing. |
| `interaction_purpose` | ✅ **KEEP as a standalone repeatable annotation class** (`purpose` ontology_term + `comment`; `interaction_id → subject_interaction`, multiple ≥1). *(Re-audit REVERSED the earlier retire→field call.)* | A field loses: instance-level grouping (one purpose spanning several interactions), per-group comment, and immutability-safety (a field mutates a possibly machine-generated interaction). Standalone doc is J-compatible (annotation-as-document, T4). Corroborated by the ndi-next-steps `Interaction_Purpose_Proposal.md` + a reviewer. |
| `stimulus_presentation` | ✅ **`timed_sequence` model** → `V_eta_stimulus_model_plan.md`. *(Re-audit SUPERSEDED "always subject_manipulation / dissolve".)* | `timed_sequence` (data_type: ordered+timed refs to stimulus data_type docs) + `timed_sequence_manipulation` (leaf). Presentation is decomposed around its preserved id (not dissolved); multi-subject via `storage_mode`; stimulator → `instrument_id` (T7). Value-by-reference, same as recording/ensemble. |
| `control_stimulus_ids` → **`control_designation`** | ✅ **Separate DERIVED annotation doc (option c)**, RENAMED `control_stimulus_ids` → **`control_designation`** (drops the `ids` container word, T13). References the `timed_sequence` + the control stimulus `data_type` doc(s), carries the `method`, marked `derived_from`/`software_id` (T10). NOT baked into the immutable body. | **Investigated:** the `tuning_response` app *derives* it (`tuning_response.m:653–656`) and **always** sets `stimulus_presentation_id` → presentation-less docs are a non-issue (schema `optional` is just permissiveness; can tighten to required). Since it's derived, keeping it out of the machine body is correct. Drop the `app` straggler (→ `software_id`). |
| `demo_ndi`, `demo_ndi_mock` | ✅ **PASSTHROUGH** (green, in_progress). *(Re-audit CORRECTED the earlier "drop from production".)* | The earlier evidence was FALSE: the coverage ledger lists `demoNDI`/`demoNDIMock` as **ndi v1 sources** (`in_progress`), and the cited `testConvertV1ToV2.m:385` is a `RenameClassNames=false` test (asserts `demo_ndi` absent because the rename was OFF), NOT a drop-safety proof. Corpus 0-doc check required before any future drop. |
| `openminds_import` | ✅ **PERSIST as ⑦ + CLOSE THE EMITTER GAP** (T9); **maturity → `draft`** until an emitter exercises it (promote to `stable` then). Added to `V_eta_class_provenance.md`. | **Audited:** schema exists (commit 4a20b46) but **NOTHING emits it** — no migrator, no importer, not even the round-trip CI test. Persisting is right (crosswalk/version provenance) ONLY paired with a *scheduled* emitter task; `stable` overstated readiness while it validates 0 docs. |
| `projectvar` | ✅ **PASSTHROUGH** (green, in_progress). *(Re-audit CORRECTED the earlier "retire".)* | The earlier evidence was FALSE: the coverage ledger lists `projectvar` as an **ndi v1 source** (`in_progress`). Its `deprecated/` schema + no DID migrator is consistent with "vestigial," but "not a source" is disproven by the arbiter. Corpus 0-doc check required before any future retire. |
| `ensemble` | ✅ **RE-DECIDED** (supersedes grain A) → `V_eta_ensemble_plan.md`. | Per-neuron spike times = PRIMARY data (each neuron-subject); the ensemble is a **group subject** (id preserved, no own body) whose members are **EPOCH-SCOPED `member_of` edges** (re-audit: the recorded neuron set changes epoch-to-epoch, so each edge carries its epoch + column order); the combined (times,ids) stream = an explicitly-**derived, rebuildable CACHE** (`sampled_body` + `derived_from` + `is_cache`, T10). The per-epoch MAP/legend doc **dissolves INTO the epoch-scoped edges** (roster preserved durably, NOT lost to the cache). Per-neuron spike bodies land via the recording-observation assembler. `member_of` + cache built in the 2nd pass (file read + id resolution); verify-before-delete gate. |

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

## Seven-tier WIP walkthrough — findings (class-by-class review)

A full pass over **every** class, tier by tier, asking one question: *is this settled, or
is it work-in-progress?* Its purpose was to stop the ledger reporting a blanket `persist`
for classes we had already decided to change, or had never really scrutinised. Result:
**persist 162 → 101, in_progress 9 → 69** — all disposition-only, no class shape changed
in the pass itself. The markers carry the decided target in `disposition_note`, so the
viewer says *why* something is WIP.

| Tier | Verdict |
|---|---|
| ① Spine & genus (14) | **persist** — reviewed, nothing flagged |
| ② Entities (9) | **persist** — reviewed, nothing flagged |
| ③ Composites (35) | 34 persist; **`contrast_sensitivity` → WIP**, since RESHAPED (below) |
| ④ Leaves (74) | 42 persist; **32 → WIP** (findings A + B below) |
| ⑤ time_reference (8) | **all 8 → WIP** (findings C, D, E below) |
| ⑥ data_body (2) | **persist — CLEAN.** Exactly two members per T6, both with a `statement` dep |
| ⑦ Infra (14, + the 6 already-marked R5 targets) | **all → WIP** (finding F) |

### ④ leaf tier

- **(A) The assertion family bypassed its data_type** — ✅ **RESOLVED.** 27 leaves + the
  `numeric_assertion` genus. `voltage_assertion` was a `numeric_assertion`, **not**
  `subject_assertion` + `voltage`, and redeclared `value` locally. The difference was
  exactly **one flag**: same field name, same type, `mustBeScalar` true vs the composite's
  false (J §5, "an assertion is one cell, no series"). That flag cost an
  **`isa <data_type>` lineage query** — it returned observations and silently missed every
  assertion — and sat against **T12 rule 3** (cardinality is not a class distinction).
  The 27 now pair with their composite and own no fields; `numeric_assertion` is deleted
  (0 fields, 0 remaining members, existed only to host the flag).
  **Why this was nearly free:** `mustBeScalar: false` *permits* a scalar, it does not
  require an array, so no document's shape changes — and nothing emits a dimensioned
  assertion in the first place (across all 102 v1 sources the only assertion targets are
  `term_assertion` and `date_assertion`). Schema-only: no migrator work, no corpus risk.
  **Deferred with it:** whether "one cell" should be re-enforceable — i.e. whether a
  subclass may *tighten* a constraint rather than redeclare it (redeclaration currently
  raises) — goes to the binding-governance pass (TaskList #32), which is already the
  "make declarations actually enforced" workstream.
- **(B) `term` and `date` had no ③ composite at all** — ✅ **RESOLVED.** They were the only
  leaf families without a composite partner, so each declared its value locally and an
  `isa term` query could not span them. `term` and `date` are now real ③ composites and
  the four leaves pair with them (`term_observation` = `subject_observation` × `term`, and
  so on), owning no fields of their own.
  **Binding strength is now uniform: `required`.** The v1 leaves had drifted apart —
  observation `preferred`, manipulation and assertion `required` — but there is no reason
  the strength should vary by statement *direction*: a term is a term, and every one must
  resolve against the binding registry. If a vocabulary cannot express something observed,
  the fix is to extend the vocabulary, not to weaken the constraint on the observation
  (T8: controlled vocabularies are hard-validated, **not** advisory). Hoisting to the
  shared composite makes that uniformity structural rather than something three leaves
  have to agree on. Note the validator does not enforce `binding` yet (only
  maxLength/minLength/minimum/maximum/enum), so this is declarative until the
  ontology-aware validator T8 describes exists — but it declares the right rule.

### ⑤ time_reference — the family re-opened as a whole, on three findings

- **(C) BUG: a retired class survives in two deps.** `epoch_bounded_reference` and
  `epoch_relative_reference` each carry a dep literally named **`element_id`** — naming the
  **retired** `element` — whose `must_refer` is `subject`, not `acquisition_epoch`. So an
  *epoch* reference names a dead class **and points at the wrong target**; the
  `element_epoch → acquisition_epoch` rename missed these two.
- **(D) `bounded` vs `relative` do not denote the same shape** (T11 says the name encodes
  the shape). `session_bounded` has start/end but `session_relative` does not;
  `epoch_bounded` has **no bounds at all** while `epoch_relative` has t0+start+end;
  `event_bounded` has no fields. Session and epoch are effectively inverted.
- **(E) `relation` is governed inconsistently** (T8 *hard-validated, not advisory*):
  `session_relative_reference.relation` carries a proper enum; its sibling
  `session_bounded_reference.relation` is a bare `char` with **no constraints**.

### ⑦ acquisition & infra

- **(F) The KEEP predated T11/T13 scrutiny.** The ⑥/⑦ walkthrough closed this tier as
  "reviewed, KEEP" — then R5 found **five of its siblings** needed renames or a fold. A
  KEEP that has already proven incomplete is not evidence of settledness, so the remaining
  classes are re-opened for the same naming + governance confirmation. Several are
  NDI-owned (the writers emit these class strings), so any rename lands as a cross-repo
  lockstep.

### Resolved during the walkthrough (no longer WIP)

- `interaction_purpose` → **persist**: the re-audit KEPT it as a standalone annotation
  class and it is already built to that shape; "pending" was stale.
- `control_stimulus_ids` → **retire**: a consumed v1 source — `migrators_j` emits the
  renamed `control_designation`, so its docs migrate away.
- `contrast_sensitivity` → **RESHAPED and back to persist.** The flat 21-field v1 bag now
  sits on a `value` cell. The conversion doc settled what the suffixes are: RB / RBN / RBNS
  are three **Naka-Rushton fit variants**, so each becomes one `model_fit` entry carrying
  its coefficients *and* the per-spatial-frequency metrics derived from that fit;
  `fitless_interpolated_c50` → `interpolated_values`, the two `*_p_bonferroni` →
  `significance`, `parameters_*` → `coefficients` (T13). It stays its **own class** — it
  aggregates *across* spatial frequencies rather than being one curve; the collapse was
  never the issue, the unreshaped bag was.
- `image` → **normalized and persist**: descriptors moved inside the cell
  (`value = {pixels, dtype, axes, color_model, channels}`), so every `data_type` now
  exposes exactly one payload slot. Query paths went 2 → 7.

### Deferred follow-up — binding governance (T8) — AFTER the current WIP items

Surfaced while resolving finding B, and deliberately **not** folded into it: the `term`
composite's binding is one field, but the binding *system* has two unresolved questions.
Evidence as built (re-derive with a walk over `constraints.binding`):

**Only SIX fields in the whole schema carry a binding at all:**

| class | field | strength |
|---|---|---|
| `term` | `value` | required *(set in the finding-B work)* |
| `dataset` | `accessibility` | required |
| `dataset` | `ethics_assessment` | required |
| `dataset` | `experimental_approach` | preferred |
| `epoch_bounded_reference` | `epoch_clock` | required |
| `epoch_relative_reference` | `epoch_clock` | required |

The dimensioned leaves carry none, correctly — their values are numbers, nothing to bind.

**(1) `variable` and `method` are completely unbound.**
```
subject_statement.variable   ontology_term   constraints = {}
subject_interaction.method   ontology_term   constraints = {}
interaction_purpose.purpose  ontology_term   constraints = {}
```
This is backwards from T8, which says the registry maps **`variable`** (and
`method`+`variable`) to a value_set — and `term.value`'s binding is literally
`keyed_by: variable`. So `variable` is the key the entire binding system pivots on, and
nothing declares that `variable` itself must resolve to a controlled term. `method` is
named explicitly by T8 and is equally unbound. These are the identity and the verb of
every statement (T2); if anything deserves a hard-validated vocabulary, they do.

**(3) Should a subclass be able to TIGHTEN a constraint?** Raised by finding A: the
dimensioned assertions used to enforce "one cell, no series" (J §5) with a locally
redeclared `mustBeScalar`. Pairing them with their composite dropped that guarantee,
because subclass redeclaration raises and there is no tightening mechanism. Same shape of
problem as the binding strengths above — a leaf wanting to narrow what it inherits — so
decide it here rather than twice.

**(2) Strength lives on the field, not in the registry.**
All five `subject_statement_bindings` entries are keyed `(variable, class)`, every one is
`class: term_assertion`, and **every `strength` is null** — the field constraint has been
doing the job the registry was designed for. Decide which is authoritative before adding
more entries, or the two will drift.

*Also note: nothing enforces `binding` yet at all — `validateConstraints` handles only
maxLength / minLength / minimum / maximum / enum, so every binding above is declarative
pending the ontology-aware validator T8 describes. That does not make the questions
academic; it means the declarations are cheap to get right now and expensive to correct
after a validator starts reading them.*

### What the walkthrough produced beyond markers

The ③ review surfaced that the **named composite types were undeclared** — enum strings
whose real layout lived in prose and in migrator string literals — which meant **26 of 35
composites emitted no query path at all**. That is now fixed (layouts declared inline; the
DID-matlab path generator recurses through them) and generalised into **T14 — "structure is
declared, not conventional"**. Four pytest guards enforce it: one payload slot per
composite, a self-expiring exception allowlist, named cells must declare sub_fields, and
dimensioned cells must carry the full source triple.

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
