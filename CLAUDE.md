# DID-schema — working context for Claude

## READ THESE BEFORE answering about V_eta class structure or the migration walkthrough
The conversation gets compacted and loses fine-grained state. The durable record
lives in these files — read them instead of re-deriving from memory:

- **`schemas/V_eta_tenets.md`** — the NORTH STAR: Brainstorm J's thesis + the 12 tenets
  (T1–T13, incl. T11 naming grammar, T12 "when is a new data_type warranted", T13 naming
  altitude/case). Answer
  design/naming/disposition questions FROM these, not from the class list.
- **`schemas/V_eta_tenet_audit.md`** — every persist/in_progress class bucketed vs the
  tenets: ✅ fully conceived / ⚠️ reconsider (R1–R6) / ❓ decide (the 11 boundary classes
  + deferred source folds). The go-forward worklist for closing V_eta. Its top
  **"Walkthrough decisions & build queue"** table is the live record of the item-by-item
  audit walkthrough — we DECIDE now and BATCH builds (team's request), so a decision can be
  FINAL while its build is deferred. R1 (app→software) built+green; R6 (image), R4 (array),
  R2/R3 (tuning) decided, builds deferred.
- **`schemas/V_eta_tuning_model_plan.md`** — the FINAL tuning-composite model (decided in the
  R2/R3 walkthrough; build deferred, TaskList #26). The 6 overlapping v1 tuning classes +
  5 fit shapes collapse to ONE `tuning_curve` `data_type` (independent variable = a
  `variable` per T11, not a name suffix) + an **ARRAY of `model_fit` entries** (each `{model`
  T8 term`, coefficients, goodness}`; NOT a class per fit) + ONE `tuning_curve_calculation`
  leaf. RE-AUDIT REVISED the first "single flexible bag, option A" draft: `model_fit` MUST be
  an array (freq tunings carry 5 co-existing fits), and the empirical summary scalars
  (circular_variance, ANOVA p, c50/pref/bandwidth) stay TYPED, queryable fields — NOT a
  `{name,value}` bag (flattening them was a real query regression). `stimulus_tuningcurve` =
  the fit-less `tuning_curve`. RE-TARGETS the already-shipped 12-calculator folds, so a corpus
  0-orphan re-verify is required (not assumed). Field NAMES (`model` vs `model_name`,
  `coefficients` vs `parameters`, the metrics-block name) pending the T11/T13 naming pass.
- **`schemas/V_eta_recording_observation_plan.md`** — the FINAL raw-recording model (decided
  in the "voltage-attribution gap" walkthrough; build deferred, TaskList #30). A raw continuous
  recording = a `<modality>_observation` of the SPECIMEN (`subject_id`=specimen,
  `instrument_id`=the electrode/element-subject per T7, `variable`=modality voltage/current/
  image/…, body=`sampled_body`); REPLACES the loose `probe observes specimen` relation +
  bare-body path the migrators emit today. Closes the gap where raw signal was migrated as
  device-attached pieces with no typed observation + dropped modality/units.
- **`schemas/V_eta_stimulus_model_plan.md`** — the FINAL stimulus model (fresh-eyes re-audit;
  build deferred, SUPERSEDES #19). `timed_sequence` = a `data_type` (ordered+timed list of
  references to stimulus `data_type` docs — `presented_id → data_type`, broad; distinct refs +
  index-array playlist) + `timed_sequence_manipulation` leaf (`subject_manipulation` +
  `timed_sequence`; stimulator → `instrument_id` per T7). Distinct stimuli = standalone
  `visual_grating`/`image`/… docs (deduped, referenced — ensemble pattern). Multi-subject via
  `storage_mode` (shared `timed_sequence` reference). Presentation is DECOMPOSED around its
  preserved id, NOT dissolved. Moots the Hartley/sparse-noise per-type-composite question
  (stimulus type lives in the referenced doc). Names provisional (naming pass).
- **`schemas/V_eta_image_model_plan.md`** — the FINAL `image` model (decided in the R6
  walkthrough; build deferred, TaskList #24). image = a `data_type` (raster value), **`image ⊂
  array`** (re-audit: subclass of the N-D-array core, adds color_model/channels — NOT a
  parallel sibling) across image_observation (measured) + image_manipulation
  (shown-as-stimulus); storage_mode governs only pixels (inline/opaque-body/reference);
  descriptors ALWAYS explicit on the composite (dtype/axes/color_model/channels) because dtype
  is NOT recoverable from an inline matrix; modality→variable; NOT an entity. Includes the
  strand-bug the build must fix.
- **`schemas/V_eta_final_class_set.md`** — the authoritative persist set (7
  categories). REGENERATE with `python3 tools/regen_final_class_set.py` (reads the
  built `V_eta/index.json` disposition markers) after every `build_v_eta.py`; never
  hand-edit. NOTE: its counts are only as good as the `disposition` markers in
  build_v_eta.py (`_RET_SOURCES`/`_RET_CARRIERS`/`_IN_PROGRESS`) — dissolved source
  classes not listed there (treatment-family, image_stack, subject_group) still show
  as `persist`; fix the markers, not the doc. CONVERSELY, `_disposition` now persists
  V_eta TARGET classes STRUCTURALLY (a `subject_calculation` leaf, or an abstract
  `data_type` composite) BEFORE the `_ANALYSIS_RE` name heuristic can retire them — the
  calc family's composites (orientation_direction_tuning, contrast_sensitivity,
  stimulus_tuningcurve, …) and `*_calculation` leaves share stems ("tuning") with the v1
  sources they consume, and were being wrongly retired. regen also routes a
  `subject_calculation`-chain class to the ④ leaf tier (not ③). Category order is fixed:
  ① spine → ② entities → ③ **composites (data_type)** → ④ leaf tier →
  ⑤ time_reference → ⑥ **data_body (EXACTLY 2: sampled_body, opaque_body)** → ⑦ infra.
- **`schemas/V_eta_6_7_walkthrough_STATE.md`** — the ⑥/⑦ (infra) walkthrough with
  per-chunk (a–e) status. Update the status table as chunks land.
- **`schemas/V_eta_nonsubject_cohesiveness_plan.md`** — decisions D-A…D-F.
- **`schemas/V_eta_go_forward_class_audit.md`** — per-class dispositions.
- The live task list (TaskList) — the remaining chunks/tracks; it survives
  compaction. Keep it current: mark chunks in_progress/completed as you go.

## Hard-won facts (do not re-litigate)
- `data_body` has EXACTLY two members: `sampled_body`, `opaque_body`. Every
  format/series carrier (`timeseries_data*`, `dataseries_data`, `zarr`,
  `ephys_zarr`, `image_zarr`, `image`, `generic_file`, `pyraview`, …) PHASES OUT
  into those two (encoding becomes a field). Never list them under data_body.
- `zarr` is a storage format (⊂ base), NOT a quantity composite.
- Composites (③) list BEFORE leaves (④). The user has asked for this repeatedly.
- must_refer is DECLARATIVE (existence-only validation), not type-checked.
- Corpus gate: 0 quarantine + 0 orphans; per-class counts shift as classes
  dissolve, total-doc counts are the invariant. Soph needs DID_RUN_SOPH_TEST=1.
- V1 SOURCE UNIVERSE = 102 (NOT 87, NOT 91). Two writers: (A) NDI production
  templates = **91 on NDI-matlab origin/main** — `tools/coverage.py` reads them from
  `origin/main` via git, NOT the working tree, because the V_eta NDI feature branch
  lags main and silently drops classes main added after the fork (ensemble,
  kilosort_clusters, kiasort_clusters, daqreader_image_epochdata_ingested — the
  first 3 now HOMED, task #21 done. D-C (#9): kilosort/kiasort_clusters now
  DECOMPOSE (count_observation + opaque_body + session anchor via
  migrators_j.private.jSorterOutput; schemas retained as a non-gating safety net,
  not yet phase-8-deleted); ensemble MODEL RE-DECIDED (`V_eta_ensemble_plan.md`,
  SUPERSEDES the old grain-A "carry the MAP doc as ⑦ infra"): per-neuron spike times =
  PRIMARY archival data (each neuron-subject, event times→sampled_body); the ensemble is
  a GROUP SUBJECT (id preserved, NO own data body) whose members are `member_of` edges
  (T1 group-ness); the combined (times,ids) marked-point-process = an explicitly-DERIVED,
  REBUILDABLE CACHE (`sampled_body` + `derived_from` the neurons, T10; user asked to keep
  it for fast windowed population reads, NOT as source of truth). The per-epoch MAP/legend
  doc DISSOLVES (column indices unnecessary once each train is keyed by its neuron-subject
  id; drop num_neurons/`app` superclass). `member_of` + cache = NDI SECOND PASS (needs the
  `neuron_names.txt` file read + neuron-id→subject resolution; single-doc migrators carry
  files but do NOT read their bytes — confirmed via pyraview). Pass-1 keeps it a green
  passthrough; VERIFY-BEFORE-DELETE (0 stranded per-neuron trains) before dropping the
  combined bytes. (The ensemble ELEMENT → group-subject via the element migrator.)
  (B) vhlab app/calculator classes with
  no NDI template = 11 (contrast_tuning, the 3 other `*_tuning`, 7 `*_calc`), footprint
  = a bespoke migrator consuming them. Do NOT add post-v1 DID intermediate/target
  classes (zarr, directory, `*_observation`, data_body, openminds_import) to the v1
  side — provenance `origin` (`V_eta_class_provenance.md`) is the arbiter; only
  `did_v1`-origin (+ the 11 app classes) are sources. `coverage.py` also flags GAPS
  (no V_eta home + no migrator + absent from the V_zeta base = never reviewed):
  currently NONE (0 gaps; the 3 ex-gap classes are homed — task #21).
  `V_eta_coverage_ledger.md` AND `.json` are generated — re-run
  `python3 tools/coverage.py` after schema/migrator changes. The web viewer's
  **Coverage ledger** panel (`web/src/Coverage.tsx`) renders the `.json`
  (sync-schemas copies it to `public/coverage.json`).
- PHASE-8 DELETION (started): `build_v_eta.py` `_DELETE_PHASE8` physically removes
  fully-consumed source tombstones from the built set (now 17 deleted). A class qualifies
  ONLY if its docs cannot survive migration: (a) a COMPLETED migrators_i dissolver
  (treatment family, virus_injection, subject_group, image_stack+params), (b)
  abstract/unminted in J (the 3 series-observation classes), or (c) a COMPLETED
  calculator composite-leaf fold — the 7 vision-calculator WRAPPERS (oridirtuning_calc,
  contrast_tuning_calc, spatial_/temporal_frequency_tuning_calc, speed_tuning_calc,
  contrast_sensitivity_calc, tuningcurve_calc) each migrate 1->1 into a `*_calculation`
  leaf (class changes), Soph+fixtures green; the RESULT class names + `stimulus_tuningcurve`
  are REUSED as persisting composites so are NOT deleted. All 17 verified
  unreferenced by any kept schema + unemitted by any migrator. HELD despite being in
  `_RET_SOURCES` (docs NOT provably consumed — deleting strands live docs):
  `element` (highest blast radius; needs a corpus per-class 0-survivor count) and
  `openminds*` (needs migrators / #9-entangled; guarded by
  test_phase1_source_cleanup_and_dep_typing — this test CAUGHT an over-eager delete).
  Deferred-calculator/carrier/to-observation retire classes STAY (docs pass through).
  The DID-matlab corpus CI (test-code.yml) is the final gate that no migrated doc
  still validates against a deleted class.
- CALCULATORS: keep as COMPOSITE LEAFS (team decision from Lepsky et al., the
  calculator-motif paper; scope: `V_eta_subject_calculation_plan.md`). Do NOT
  DISSOLVE a `_calc` doc into observations — dissolution changes/removes its id, so
  every downstream reference DANGLES -> orphans (Soph went red with 11448 such
  orphans, 5445377; e.g. `contrast_sensitivity_calc.contrasttuning_id_* ->
  contrast_tuning_calc`). INSTEAD, a calculator output migrates 1->1, id- AND
  deps-PRESERVED, into a `subject_calculation` LEAF (`<result>_calculation` =
  `subject_calculation` + a result `data_type` composite; the fourth statement
  direction, ⊂ subject_interaction + app). Because the id is preserved and must_refer
  is existence-only, downstream refs resolve -> calculators un-defer with 0 orphans.
  DONE + green (fast fixture gates #17-#21, + the REAL orphan gate: Soph corpus
  run #2 / b3e2e10 SUCCESS 2026-07-23, ~101k docs, 0 orphans — the 11448-orphan
  dissolution failure does NOT recur): 11 of 12 vision calculators fold to
  `subject_calculation` composite leafs — the 5 tuning result classes, their 5 `*_calc`
  wrappers (oridirtuning_calc, contrast_tuning_calc,
  spatial_/temporal_frequency_tuning_calc, speed_tuning_calc), AND contrast_sensitivity
  (new composite+leaf, folds single-doc — its doc HAS element_id) — all via the shared
  `migrators_j.private.jCalculation` (result composite verbatim; input_parameters ->
  method_parameters; app kept; input -> derived_from_1). ALL 12 vision calculators now
  fold single-doc — `tuning_curve` (tuningcurve_calc + raw stimulus_tuningcurve) landed
  as migrators_j.tuningcurve_calc + migrators_j.stimulus_tuningcurve, both -> the
  `stimulus_tuningcurve_calculation` leaf (so downstream stimulus_tuningcurve_id refs
  resolve to either). CORRECTION of an earlier "hard-won fact": tuningcurve_calc does
  NOT lack a subject — it IS-A stimulus_tuningcurve (v1 superclass) and inherits a
  POPULATED element_id (the writer sets it from the consumed stimulus_response_scalar,
  NDI-matlab +app/+stimulus/tuning_response.m line 499; verified against the calc mock
  doc). So element_id -> subject_id, id-preserved, NO NDI second pass needed. The raw
  stimulus_tuningcurve is the pre-calculator-framework curve (from ndi.app.stimulus.
  tuning_response); it also has element_id and folds the same way. Also: NDIcalc-vis
  `ndi.query` rename to the leaf names
  (naming B, separate repo, out of scope); `hartley`/RF -> 2.D data_body (stays deferred).
  The Soph gate (`test-soph-corpus.yml`) was repointed V_zeta->V_eta + this branch so it
  actually validates the fold. NOTE the D10
  statement-conditions field was renamed `parameters` -> `conditions` (axis =
  per-reading array, covariate = length-1); `method_parameters` holds the algorithm
  config (calculator input_parameters), a distinct slot.
- distance_metadata ~2078 JH quarantines ("required `endpoints` missing"): ROOT
  CAUSE (confirmed from the writer NDI-matlab `+setup/+conv/+haley/doImport.m` and
  the v1 template `ndi_common/database_documents/element/distance_metadata.json`):
  the v1 doc is FLAT — `ontologyNode_A/_B`, `integerIDs_A/_B`,
  `ontologyNumericValues_A/_B`, `ontologyStringValues_A/_B`, `units` — with NO nested
  `endpoints` and the numeric values genuinely `[]` (the distance lives in the
  associated `distance` timeseries ELEMENT, not the metadata doc). The migrator was
  written against an ASSUMED nested `endpoints.numeric_values` that does not exist in
  real docs → it always hits the no-vals passthrough → the flat doc fails the V_eta
  schema's required nested `endpoints` → quarantine. So the migrator NEVER worked on
  real corpus docs (its unit test used a wrong-shaped fixture). CORRECT FIX (NOT a
  casing tweak — a first camelCase attempt was WRONG and was reverted): map the flat
  A/B fields into the V_eta `endpoints` shape (integer_ids ← integerIDs_A/_B,
  string_ids ← ontologyStringValues_A/_B, node ← ontologyNode_A/_B) so it validates;
  the numeric distance is empty, so it CANNOT be a length_observation from the metadata
  doc alone. Part A (mint a measured_distance_to relation between the endpoint doc ids)
  was TRIED and REVERTED — the endpoint ids do NOT resolve in JH (4156 orphans = 2078×2,
  both endpoints dangle; the JH animal is likely an openminds_subject minting a NEW id,
  so the stored ontologyNode_A/_B are pre-migration ids), and it turned a non-gating
  quarantine into a GATING orphan failure. A single-doc migrator CANNOT mint a
  resolvable endpoint relation. DECISION: the correct rep is the NDI SECOND PASS
  (TaskList #18), which sees the migrated-id graph —
  decompose the distance timeseries ELEMENT into a length_observation of the
  graph-resolved animal subject (endpoint A), patch (endpoint B) as a spatial relation,
  consuming distance_metadata for the endpoint identities. The single-doc DID migrator
  lacks the element→subject graph + the timeseries values, so it CANNOT do this; it is
  left as-is (quarantine). Optional DID interim to clear the quarantines early: mint a
  directed_relation between the two endpoint DOC IDS (both resolve in-batch). Corpus is
  GREEN with these quarantines (JH's test does not gate quarantine) — data-completeness
  follow-up, not a gate.
- General migrator lesson: any NESTED sub-field a migrator reads needs a
  snake+camelCase fallback. AUDIT (this session) of every +migrators_j nested read:
  live nested multi-word reads were `syncrule_mapping.epochnode_*` (fixed) and
  `ontology_table_row.row.numeric_value` (defer WITH the D10/D11 redesign). Everything
  else reads BLOCK-level fields (snake-cased by universalRenames, safe) or PascalCase-
  by-design (metadata_editor's metadata_structure). NOTE distance_metadata is NOT a
  casing bug (see above) — it is a wrong-assumed-shape bug.

## Build / test
- `python3 tools/build_v_eta.py` rebuilds `schemas/V_eta/` (copytree V_zeta→V_eta
  then transforms). `python3 -m pytest tests/test_veta.py -q` checks the schema.
- Migrators live in DID-matlab `+did2/+convert/+migrators_j/`; corpus validation is
  DID-matlab `test-code.yml` (full, ~1–2h) and `test-migrators-quick.yml` (~2 min).
