# DID-schema — working context for Claude

# OPERATING RULES — read before doing anything, no exceptions

These exist because on 2026-07-29 a series of mistakes shared one property:
**they were biased toward things looking fine, or toward looking like progress
had been made.** All-zero counts read as clean. All-decided read as done. A grep
that could not have matched was reported as "this does not exist anywhere". An
error that is random is a nuisance; an error that always points at *we are
further along than we are* makes every report unusable. These five rules remove
the mechanisms, because a documented warning does not work — the "recurring
epistemic error" section below was READ and then committed again within the hour.

**1. DO NOT WRITE TO `schemas/`.** Not schema files, not plan documents, not
notes. Findings go to the chat or a scratch file. Nothing enters the record until
the user says "commit that". Research quietly becoming the record is how five
V_eta families Claude wrote up alone ended up reported to the team as decided.

**2. EVERY factual claim about NDI, a migrator, or a corpus ships with the
command output that proves it, in the same message.** If the output cannot be
pasted, the sentence is not written. "No session document exists anywhere" dies
instantly under this rule: the grep that produced it plainly did not show that.

**3. CONTRADICTING an existing comment, decision or document requires POSITIVE
EVIDENCE. Never absence.** `jSessionAnchor`'s note that its orphans were
discovery-mode was correct and was overridden with a failed search. Not finding
something is not evidence it is not there.

**4. ONLY THE TEAM DECIDES A V_eta DISPOSITION.** Claude may research and
propose; it may not record a decision. Enforced in `tools/status_board.py`: a
family counts as decided ONLY if its plan document carries a line

        TEAM-SIGN-OFF: <who/when> -- <what was decided>

Claude must never add that line. Without it the family renders as
"awaiting review" no matter what the FAMILIES table says.

**5. AN INSTRUMENT MUST REPORT ITS DENOMINATOR.** Any counter, census or report
states how many things it inspected, first and unconditionally. `silentLoss`
printed "0 empty edges" while reading nothing for two days, and the digest that
rendered it repeated the omission. A count without a denominator is not evidence.

**Scope: do exactly what was asked, and stop.** "Look at X if you like" is not
authorisation to change X. Ambiguity is resolved by asking, not by doing more.

---

## START HERE — the generated state artifacts (read these FIRST, before any prose)

Everything below this section is PROSE, and prose in this project has been wrong
often enough to be dangerous: "no session document exists anywhere", "all 0-usage,
safe to delete" (3 of 4 wrong), "dissolved (rename/decompose)" (32 rows asserted,
never verified), "the epoch link is the epochid dep" (no such dep). Each was
written down confidently and cost real time. **When prose and a generated artifact
disagree, the artifact wins. When prose makes a claim about NDI or a migrator, do
not repeat it — re-derive it with the tool.**

| artifact | what it answers | regenerate |
|---|---|---|
| **`schemas/V_eta_STATUS.md`** | **how much of V_eta is left, and exactly what** | `python3 tools/status_board.py` |
| `schemas/V_eta_coverage_ledger.md` / `.json` | every v1 source class → its V_eta target | `python3 tools/coverage.py` |
| `schemas/V_eta_final_class_set.md` | the authoritative persist set | `python3 tools/regen_final_class_set.py` |
| `schemas/V_eta_ndi_ground_truth.json` | what NDI templates + writers actually declare | `python3 tools/ndi_ground_truth.py` |

All four are CHECKED IN CI and fail when stale, so they cannot drift while
unattended. `tools/status_board.py --check` additionally fails when an
`in_progress` class belongs to no decision family (an open question nobody is
tracking), when two families claim one class, or when a family cites a decision
document that does not exist.

**The status board is the answer to "where are we".** Do not reconstruct that from
the task list or from the plan documents — they disagree with each other. The plan
documents are RATIONALE (why a model was chosen); the board is STATE.

The DID-matlab side has the same rule: `tools/census_digest.py` renders the corpus
census and `tools/test_census_digest.py` tests it in ~5 ms on the fast gate. The
census itself (`did2.validate.silentLoss`) is the instrument that finds hollow
documents; it reported zeros for two days because it was reading nothing, so
**always check `total_docs` is non-zero before believing any census number.**
The DIGEST had the same defect one layer up, and it survived one repair:
corpus run #3 (31315510527, 2026-08-09) ran six corpora for over an hour, went
GREEN on all six, downloaded five artifacts, wrote ten files — and printed
`NO CORPUS REPORTS FOUND`, then **exited 0**. Cause, from the runner's own log:
MATLAB's pwd during a corpus run is `tests/`, so reports land in
`tests/corpus-reports/`; `upload-artifact` given two search paths promotes the
artifact root to their least common ancestor (the repo root); so the download
lands them at `corpus-reports/tests/corpus-reports/` and a one-level glob
matches neither copy. *The two-path upload added to make the reports findable
is what moved them out of reach.* Now: the search is RECURSIVE over any number
of roots, **zero reports is a non-zero exit**, and the digest prints its own
denominator first (files matched, directories walked, paths read, named roots
that do not exist) so "found nothing" and "looked in the wrong place" are
distinguishable from the output alone. `test-code.yml` had the identical bug
independently — it digested `corpus-reports` from the repo root — so its
end-of-log census had been empty too. **`testCorpusPRED` also now writes a
report**: it is a hard 0-quarantine gate rather than a discovery run, so it
never went through `runCorpusDiscovery` and contributed NOTHING to the census —
a corpus we gate on but never measure is a denominator missing from every
figure we quote.

## READ THESE BEFORE answering about V_eta class structure or the migration walkthrough
The conversation gets compacted and loses fine-grained state. The durable record
lives in these files — read them instead of re-deriving from memory:

- **`schemas/V_eta_tenets.md`** — the NORTH STAR: Brainstorm J's thesis + the 14 tenets
  (T1–T14, incl. T11 naming grammar, T12 "when is a new data_type warranted", T14
  "structure is declared, not conventional" — one `value` slot + inline cell layouts, T13 naming
  altitude/case). Answer
  design/naming/disposition questions FROM these, not from the class list.
- **`schemas/V_eta_tenet_audit.md`** — every persist/in_progress class bucketed vs the
  tenets: ✅ fully conceived / ⚠️ reconsider (R1–R6) / ❓ decide (the 11 boundary classes
  + deferred source folds). The go-forward worklist for closing V_eta. Its top
  **"Walkthrough decisions & build queue"** table is the live record of the item-by-item
  audit walkthrough — we DECIDE now and BATCH builds (team's request), so a decision can be
  FINAL while its build is deferred. R1 (app→software) built+green; R2/R3 (tuning collapse)
  + R6 (image standalone) now BUILT schema-side (tuning_curve/tuning_curve_calculation,
  image data_type + image_observation/_manipulation) + migrators — quick fixture gate GREEN,
  full-corpus 0-orphan re-verify **DONE + GREEN** (test-code.yml run #251 / 324b776, 2026-07-28:
  all 5 corpora 0 orphans AND 0 quarantine, 373/373 tests). STILL deferred: R4's ngrid→sampled_body
  fold (ngrid still in stable/), software dedup + openMINDS crosswalk, R5 renames, and the
  NDI second-pass assemblers (ensemble member_of+cache, raw-recording observation, timed_sequence
  decompose).
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
  0-orphan re-verify is required (not assumed). NAMING PASS (final): fit entry = `{model`
  (bare bound term, not `model_name`)`, coefficients` (not `parameters`)`, goodness}`; metric
  sub-blocks `significance` / `circular_statistics` / `interpolated_values` (the `derived_summary`
  bag is killed).
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
  (stimulus type lives in the referenced doc). **Naming is FINAL, not provisional** — the
  plan's own "Resolved" section records `timed_sequence` + `timed_sequence_manipulation` as
  confirmed by the naming pass (neutral by design so a future `_observation` leaf is possible).
  This line said "provisional" long after the plan settled it; do not re-open on its word.
- **`schemas/V_eta_image_model_plan.md`** — the FINAL `image` model (decided in the R6
  walkthrough; build deferred, TaskList #24). image = a **standalone** `data_type` (raster
  value) — **`array` is KILLED** (re-audit: a bare N-D numeric grid duplicates sampled_body
  (T6) + names a container (T13), so `ngrid` phases into `sampled_body` and there is no `array`
  data_type; `image` does NOT subclass anything) across image_observation (measured) +
  image_manipulation (shown-as-stimulus); storage_mode governs only pixels
  (inline/opaque-body/reference);
  descriptors ALWAYS explicit on the composite (dtype/axes/color_model/channels) because dtype
  is NOT recoverable from an inline matrix; modality→variable; NOT an entity. Includes the
  strand-bug the build must fix.
- **BINDING GOVERNANCE (T8) — deferred follow-up, AFTER the current WIP items.** Recorded in
  `V_eta_tenet_audit.md` ("Deferred follow-up — binding governance"). Two open questions,
  evidence already gathered: (1) `subject_statement.variable`, `subject_interaction.method`
  and `interaction_purpose.purpose` are **completely unbound** (`constraints = {}`) even
  though T8 says the registry maps `variable` (and `method`+`variable`) to a value_set —
  `variable` is the key the whole system pivots on (`term.value` is `keyed_by: variable`)
  yet nothing requires `variable` itself to resolve. (2) Strength lives on the FIELD, not
  the registry: all 5 registry entries have `strength: null` while the field constraint does
  the work — decide which is authoritative before adding entries. Only SIX fields carry a
  binding at all (term.value, dataset.accessibility/ethics_assessment/experimental_approach,
  the two epoch_clock fields). `binding` is NOT enforced by the validator yet
  (validateConstraints handles only maxLength/minLength/minimum/maximum/enum), so these are
  declarative — cheap to fix now, expensive once a validator reads them.
- **`schemas/V_eta_ngrid_family_findings.md`** — FACTS (not decisions) for group F, read from
  the real v1 writers: the RF family is **ONE** document class (`hartley_calc`; `reverse_correlation`
  + `hartley_reverse_correlation` are superclass-only, no docs, and `calculator` is a V_delta
  invention), its payload is a **two-plane** `[T×X×Y×2]` volume (STA + p-value), `element_id` IS
  populated so no NDI pass is needed for subject attribution, `ngrid` has a **second consumer**
  (`ontologyImage`) so retiring it is gated on both, `ngrid.coordinates` carries real data and is
  being **deleted** by the migrator. **`ontology_image` (F5) is FIXED**, and this paragraph's
  own account of WHY was wrong until 2026-08-09. It said NDI *redefined* `ontologyImage` so
  **TWO** vintages are both did_v1 — A (legacy `ontology_name`+`ontology_region`, dep
  `element_id`) and B (current NDI `ontology_nodes` = comma-joined multi-CURIE, dep
  `ontologyTableRow_id`, `ngrid` superclass). **THERE IS NO VINTAGE A. NDI NEVER REDEFINED THE
  CLASS.** Positive evidence, three independent ways: `git log --all --diff-filter=A --
  '*ontologyImage.json'` returns exactly ONE commit (`0ae099c`), every revision in the file's
  history carries `ontologyTableRow_id` + `ontologyNode`, and `git log --all -S"ontologyRegion"`
  / `-S"ontology_region"` match only DID-side alias-table commits, never a template. NDI-matlab
  `04dcdf9` (2026-07-29) had already established the same thing while deleting four fabricated
  alias rows: *"ontologyImage created 2025-07-03, three commits total, always {ontologyNode}
  with an ontologyTableRow_id dependency. Never had ontology_name or ontology_region."*
  Vintage A came from DID-schema's own V_alpha/V_beta snapshot — the migrator's header says so
  in its own words ("legacy; DID-schema V_alpha/V_beta ancestry") and still calls it a did_v1
  vintage. It is the ground-truth-track fabrication one more time, wearing the word "legacy".
  **NOTHING IS BEING RIPPED OUT**: the migrator branches on shape and errors on no-match, so a
  branch for a shape that cannot occur simply never fires, and the tombstone's vintage-A fields
  are optional, so an absent field cannot trip `undeclaredField`. Both are safe as written and
  cost nothing. What was expensive was the RECORD — planning around a second vintage that has
  never existed. Read the disposition in `V_eta_OPEN_WORK.md` #47 ("ONE vintage, not two"),
  which was right, over this paragraph, which was not. The old `region` read matched NEITHER (it is the
  V_DELTA migrator's OUTPUT, and `migrators_j` runs INSTEAD of the V_delta migrator on a
  universalRenames-only body), so every doc became a silent husk. Now: A migrates, B PASSES
  THROUGH for the NDI second pass (a table row is not a subject), and anything else ERRORS.
  Also surfaced a systemic gap: `mustBeNonEmpty` on `depends_on` is declared everywhere and
  **enforced nowhere** (`validate/references.m` skips empty edges) — sibling to #32.
  Evidence came from `VH-Lab/NDIcalc-vis-matlab` (added to scope; the clone is EPHEMERAL — re-add
  to re-check). **PROCESS: every remaining item in that doc is DECIDED BEFORE ANY BUILD.**
- **`schemas/V_eta_data_body_model_plan.md`** — the FINAL `data_body` tier (decided 2026-08-08 in
  the coordinates walkthrough; build deferred, TaskList #45; GATES #46). Started at "where do
  `ngrid.coordinates` go" and ended at the whole tier. ONE **axis entry** replaces THREE
  encodings of regular-vs-enumerated (`subject_interaction.sample_time.kind` /
  `sampled_body.sample_time.regular` / `axes[].regularity`) plus a fourth spelling of the same
  fact (`acquisition_epoch.axes.sample_rate` typed `frequency` vs `sample_time.dt` typed
  `duration`). **TIME BECOMES AN ORDINARY AXIS** — both `sample_time` blocks retire, and that is
  CROSS-REPO (NDI writes `sample_time` in 3 places; the STRING sweep found it, a structural sweep
  would not). `axes[]` mounts on BOTH `subject_statement` (inline) and `sampled_body` (body),
  mutually exclusive by `storage_mode` and CHECKED — statement-only is impossible because
  `pyraview` writes N bodies per statement with per-level `dt`/`t0`. **`conditions` is NOT an
  axis**: the D10 sentence "same kind of thing, distinguished only by cardinality" is WRONG
  (time is the commonest axis and has never been a condition) and `conditions` tightens to
  cardinality EXACTLY 1. `datum` collapses to `datum_type` and moves TO THE STATEMENT (the same
  `pyraview` loop indexes `dt`/`t0` by level but NOT `dataType`: extent is per-body, type is
  per-statement). NOT `data_type` — that is a CLASS with **38 direct subclasses**; NOT
  `element_type` — v1 `element` has **223 hits across 95 of 915 NDI files**; `datum` has ZERO v1
  meaning. `data_body` gains `format` + `compression` (the unbuilt half of the 2.D "encoding
  becomes a field" decision, which `migrators_j/image.m:51-56` has been waiting on) plus
  `filename`/`content_hash`/`description` and the `statement` edge — declared on both children
  today with OPPOSITE required-ness. `summary` is DROPPED (#68, empty + unread); `zarr` is
  DELETED not migrated (V_gamma invention, no v1 source, ZERO migrator references) and its
  `codecs[]` is NOT copied — it models per-chunk array codecs, and the live compression is
  archives (`.nbf.tgz`, `.zip`) and `tiff`+`lzw`. **CORRECTION recorded there**: a claim that
  numeric predicates inside an array of structs silently match everything was read off the
  LEGACY `+did/+datastructures/fieldsearch.m`; `did2` DOES support them
  (`compileQuery.m` → `queryable_array_elem.value_num`). BLOCKED ON #32.
- **`schemas/V_eta_ground_truth_plan.md`** + **`schemas/V_eta_migrator_vocabulary_audit.md`** —
  THE REPAIR TRACK. Migrators were written against DID-schema's own `V_alpha` snapshot instead of
  the real NDI templates, so many read fields NO REAL DOCUMENT HAS and emit empty-but-valid
  documents that pass every gate. RULE: **NDI `origin/main` templates are the did_v1 truth; where
  template and WRITER disagree the WRITER wins; fixtures are built from the writer, never from a
  DID-side schema.** Phase 0 (ground truth extract, `tools/ndi_ground_truth.py` →
  `V_eta_ndi_ground_truth.json`) is DONE. Phase 1 is REPORT-ONLY-landed with **1.3 + 1.4
  BUILT** (the vocabulary sweep ENFORCES in DID-schema CI; `did2.validate.isFragment` closes the
  FRAGMENT mode). **1.1/1.2 are blocked on the census — which was measuring NOTHING**:
  `silentLoss` reported `total_docs=0` on all 5 corpora because `asStruct` asked `did2.document`
  for `document_properties` (the property is `documentProperties`), so every doc became `[]` and
  `toBodies` silently dropped them; `total_docs` was then taken from the survivors, making total
  failure and an empty batch identical. FIXED + tested (`testSilentLoss.m`); census must be
  RE-TAKEN. **17 offenders, not 15** — `vmspikesummary` (models a different document than exists:
  the real class is a mean spike WAVEFORM + 8 shape medians) and `vmspikefilteringparameters`
  (NO migrator at all, so it passed through into a tombstone declaring `filter_type`/`filter_window`,
  neither of which exists) were found by re-checking the detector's "mentions only" bucket. All
  BUILT: 6 fixed, 8 guarded passthroughs, 1 tombstone-only, 2 allow-listed benign.
- **`tools/check_tombstones.py`** + **`schemas/V_eta_tombstone_audit.md`** — PHASE 2b, NOT in the
  original plan. Every V_eta SOURCE TOMBSTONE compared against its NDI template: the tombstones
  were written from V_alpha too, so a passthrough would have QUARANTINED the documents it exists
  to preserve (the validator is strict BOTH ways — `undeclaredField` and `mustBeNonEmpty`).
  First run: 36 of 60 diverged. Now **BLOCKING 9 → 3** (the 3 left are `stimulus_parameter`,
  `stimulus_parameter_table`, `stimulus_presentation`, held for #31 deliberately). It reads the
  `RENAME` map, so renamed classes are compared instead of silently skipped — that hole hid
  `element_epoch`→`acquisition_epoch`, which declares `axes`/`channels`/`storage` that no NDI
  template has. THREE failure modes — hollow / passthrough / **fragment**
  (fragment is seen by NO counter). Biggest find: **`ontology_label` is NOT benign** — it
  discards the `document_id` edge (its only referent) and emits an empty `subject_id`, ~7,007
  docs, currently graded ✅ in the coverage audit. RECURRING TRAP: research agents keep claiming
  `element_id` is a dangling non-subject edge — it is NOT, `element.m` promotes elements to
  subjects with ids PRESERVED. OPEN: the `vhlab_voltage2firingrate` writer is in no repo we have
  (blocks `binnedspikeratevm`'s Hz-vs-spikes-per-bin, a silent 33× risk), and the 102-class v1
  universe may be too small (`NDIcalc-ephys-matlab` ships `spike_shape_calc`, absent from the
  ledger entirely). **LIMIT OF THE CHECKER, found 2026-08-08 — its output is a STARTING POINT,
  NOT AN INSTRUCTION.** It compares the tombstone against the NDI **template**, but the
  ground-truth rule is *where template and WRITER disagree, the WRITER wins* — and the checker
  cannot see that disagreement. Live case: it reports `ontology_image` is missing
  `ontology_node`, because `database_documents/.../ontologyImage.json` says `ontologyNode`
  (singular) — while `schema_documents/.../ontologyImage_schema.json` says `ontologyNodes` and
  `imageDocMaker.m:121-127` writes `struct('ontologyNodes', ontologyNodes)`. Following the
  checker there would have made the tombstone WORSE. Always check the writer before acting on a
  row.
- **`schemas/V_eta_time_reference_model_plan.md`** — the FINAL time model (decided in the ⑤
  walkthrough; build deferred). **8 classes collapse to 2**: `absolute_reference` +
  `relative_reference` under an abstract root. `origin` is a RELATION (an edge, T4/T7), `mode` is
  CARDINALITY (T12) — and `mode` meant TWO DIFFERENT THINGS (session = with/without metric; event
  = whole-extent/offset). T11's `<origin>_<mode>_reference` grammar is a NAMING RULE describing
  the old family, not a mandate it exist; amend T11 with the change. Both follow T14 one-`value`
  (canonical + source provenance, like `voltage`/`duration`), so `is_approximate` moves INTO the
  cell. `relation` → `ontology_term` bound to **OWL-Time** (the enum was bare char, 6 of Allen's
  13, `concurrent_with` ambiguous). `frame` not `clock` (it selects conception/birth for an
  organism as readily as dev_local_time for an epoch). `relative_to` not `event_id` (3 of 4
  referent kinds are not events). **`acquisition_epoch.clocks` DISSOLVES into time_references.**
  **NO TIMES ⇒ NO REFERENCE** (a NaN reference is a hollow document — the exact thing silentLoss
  + isFragment exist to catch). CORRECTION recorded there: `dev_local_time.t0` is NOT always 0 —
  `blackrock.m` sets it from the device hardware Timestamp; NDI's prose says the clock is SCOPED
  to epochs, not that it STARTS at zero. Volumes: 107,308 `session_relative_reference` + 20,411
  `session_bounded_reference`; epoch/event/utc classes have ZERO docs and **no migrator has ever
  emitted one**, so all epoch timing collapses to "during the session, approximately" while
  11,118 `acquisition_epoch` docs carry clock data nothing points at.
  **EVIDENCE PASS + 2 MORE DECISIONS (read the plan's later sections, they supersede the
  summary above):** NDI *already has this model* — `ndi.time.timereference` is
  `(referent, clocktype, epoch, time)`, i.e. `relative_to` + `frame`, arrived at independently;
  the `(referent, epoch)` pair collapses to ONE edge only because V_eta reifies the epoch as a
  document. The collapse is now MEASURED, not argued: the only two classes with documents are
  `{is_approximate, relation:'during'}` and the same plus `start`/`end`, and `relation` is
  `'during'` at all 14 emitter call sites — pure cardinality. **A: `relative_to` is REQUIRED**
  (team call). **A claim recorded here was WRONG and is corrected**: an earlier revision said NO
  `session` document exists anywhere, that only `session_in_a_dataset` is ever written, and that
  required `relative_to` was gated on minting one. **False.** `ndi.session.dir` creates and
  PERSISTS a session document on first open (`ndi.document('session','session.reference',...) +
  newdocument()` → `database_add`), reads it back from the database, and the coverage ledger
  already carries `session → session, persist` — a did_v1 source migrating 1:1 with its id
  preserved. So the referent EXISTS and required `relative_to` needs no prerequisite build. The
  error came from a grep that could not have matched the real call site, promoted to a claim —
  and it was then used to OVERRIDE `jSessionAnchor`'s correct note that its orphans were
  DISCOVERY-MODE (a subset batch need not contain the session doc; the edge resolves in a full
  migration). What remains is VERIFICATION, TaskList #51: read `by_class` for a `session` count
  per corpus before the build. **B: THERE IS NO `origin` FIELD and `t0` IS
  KILLED OUTRIGHT** — the anchor is not a property of the reference. Every
  `ndi.time.timereference` construction passes `0` except ONE (`tuning_response.m:92`, which
  passes `presentation_time(1).onset`, already stored on the stimulus document). So the anchor is
  either 0 (nothing to store) or an event that already has a document — point at it. My `origin`
  field recommendation was WRONG. This also CLOSES chaining: chains are normal and well-founded
  (observation → stimulus → epoch, every link a real document), terminating at an
  `acquisition_epoch`, a session, or an `absolute_reference`. **C: ONE ANCHOR PER DOCUMENT** — one
  `relative_to` + one `frame` govern both `start` and `end`; an interval whose ends are anchored
  differently (which `markvalidinterval(epochset, t0, timeref_t0, t1, timeref_t1)` permits) becomes
  TWO reference documents on the statement. Rejected nesting an anchor block per end — that is the
  inline structure removed from `acquisition_epoch.clocks`, `epochclocktimes`, `distance_metadata`
  and the tuning bag. **The model is now FULLY DECIDED; the remaining work is two DEFERRED,
  TRACKED items, not open design**: TaskList **#51** verify a `session` document is present in
  every corpus (a CHECK, not a build — see fork A) and TaskList **#52** role-name the `time_reference_#` statement edges (a bare index
  cannot distinguish start-anchor vs same-instant-other-frame vs recurrence; touches
  subject_interaction + directed_relation + every migrator writing them). Until #52 lands,
  multiple references on one statement are UNDEFINED in meaning — open item 2, recorded not
  overlooked. Also identifies `valid_interval` (an UNVERIFIED coverage row) =
  `ndi.app.markgarbage`'s record of which stretches of an epoch are good data.
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
- **`schemas/V_eta_OPEN_WORK.md`** — the COMMITTED index of open work, and the thing `#nn`
  references in every plan document point at. Keep it current.
- The live task list (TaskList) — a working mirror of `V_eta_OPEN_WORK.md`. **IT IS NOT A
  DURABLE RECORD.** This line used to read "it survives compaction", which is true and is the
  wrong guarantee: on 2026-08-08 the container was RE-PROVISIONED mid-session (a cluster of
  `/root/.claude/` harness files rewritten at 21:18) and **all 68 tasks were wiped**, while the
  same event reset this repo's working tree 274 commits back to an older upstream revision.
  Everything PUSHED survived untouched; everything that lived only in a task description did
  not. **A finding is not recorded until it is committed.** "Compaction-safe" is not
  `git status` clean — clean only proves nothing written was left uncommitted. The check is:
  *is there anything in a task description, or in my head, that is not yet in a file?*

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
  a GROUP SUBJECT (id preserved, NO own data body) whose members are **EPOCH-SCOPED**
  `member_of` edges (T1 group-ness; re-audit: the recorded neuron set changes epoch-to-epoch,
  so each edge carries its epoch + column order — the per-epoch roster is preserved as edges,
  NOT lost to the cache); the combined (times,ids) marked-point-process = an explicitly-DERIVED,
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
  **0 UNMAPPED + 4 UNVERIFIED** (`subjectmeasurement` now has a tombstone). This line used to read "currently
  NONE (0 gaps)", which was true only because the ledger asserted a conclusion it had no
  evidence for: every class with no V_eta home was labelled "dissolved (rename/decompose)"
  — 32 rows — turning each unknown into a reassuring claim. That is now split by whether a
  migrator actually CONSUMES the class (28 rows, genuinely accounted for) versus no home and
  no migrator (4 rows — `generic_file`, `imageCollection`, `imageStack_parameters`,
  `valid_interval` — labelled UNVERIFIED; the last two are probably already resolved but
  unrecorded). Separately, `_PRE_ZETA_DISSOLVED` carried a FALSE entry claiming
  `subjectmeasurement` dissolved into `measurement`. NDI never did that: it is still a
  shipped template, and `measurement` is a NEWER PARALLEL class (added 2026-01-05).
  **CORRECTED 2026-08-05 — this line said "FOUR in-tree emitters", which is numerically right
  and materially misleading: ALL FOUR are TEST-session builders** (`+test/+daq/
  build_intan_flat_exp.m`, `tests/+ndi/+unittest/+session/buildSession.m`,
  `buildSessionNDRIntan.m`, `buildSessionNDRAxon.m`; 7 files total including the template, its
  schema and `ndiDocumentAttributes.json`). There is NO production writer in-tree. That does
  NOT mean no real data exists — the corpora are a sample and older lab scripts could have
  written these — so the class still needs its migrator; DISPOSITION (team, 2026-08-05): route
  it through the `measurement` fold, no new model. The parallel-class fact this line exists to
  protect is unaffected. Every entry in that dict is an assertion about NDI and must be
  verified against `origin/main` before it is added.
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
  resolve to either). **[SUPERSEDED by R2/R3 — see `V_eta_tuning_model_plan.md`: the per-tuning
  result classes + the `stimulus_tuningcurve_calculation` leaf named in this block COLLAPSED to
  the ONE `tuning_curve_calculation` leaf (+ `tuning_curve` composite); `contrast_sensitivity`
  stays on its own `contrast_sensitivity_calculation`. The id-preserving 1→1 fold mechanism +
  the 0-orphan result are unchanged — only the target leaf/composite NAMES changed.]** CORRECTION of an earlier "hard-won fact": tuningcurve_calc does
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
  lacks the element→subject graph + the timeseries values, so it CANNOT do this. STATUS:
  the flat→nested `endpoints` reshape (Part B of #18) SHIPPED and the ~2078 JH quarantines
  are GONE — corpus run #251 (2026-07-28) reports JH `quarantine_count: 0`, so this is no
  longer a standing quarantine. What REMAINS deferred is only the length_observation /
  spatial-relation modelling (the numeric distance still lives in the `distance` timeseries
  ELEMENT and needs the NDI second pass) — a data-completeness follow-up, not a gate.
- General migrator lesson: any NESTED sub-field a migrator reads needs a
  snake+camelCase fallback. AUDIT (this session) of every +migrators_j nested read:
  live nested multi-word reads were `syncrule_mapping.epochnode_*` (fixed) and
  `ontology_table_row.row.numeric_value` (defer WITH the D10/D11 redesign). Everything
  else reads BLOCK-level fields (snake-cased by universalRenames, safe) or PascalCase-
  by-design (metadata_editor's metadata_structure). NOTE distance_metadata is NOT a
  casing bug (see above) — it is a wrong-assumed-shape bug.

## Findings recorded here because they have no other home yet

- **`generic_file` needs `opaque_body` + a statement** (agreed in walkthrough). It is a REAL,
  PRODUCTION class — written by `+ndi/+setup/+conv/+babu/import.m` for plasmid and LCMS
  documents, read by `+ndi/+cloud/+download/downloadGenericFiles.m` — with `filename`,
  `formatOntology`, `dateCreated`, `dateUpdated`, `checksum` and a `generic_file.ext` file. It
  has NO V_eta home and NO migrator: a Babu dataset migrating today strands these. Note V_eta
  already folded a `generic_file` concept into `opaque_body` (`test_generic_file_folded_to_opaque_body`),
  so the class name is taken — reconcile before building.
- **The 4 UNVERIFIED coverage rows** (no V_eta home, no migrator, fate never recorded):
  `generic_file` (above), `imageCollection` (ZERO emitters in NDI, yet `image.imageCollection_id`
  points at it — genuinely unknown), `valid_interval` (see the chunk-(a) correction in
  `V_eta_6_7_walkthrough_STATE.md`), `imageStack_parameters` (**false alarm** — it is a
  SUPERCLASS of `image.json`/`imageStack.json` whose block `image_stack.m` consumes; the ledger
  flags it only because no migrator is *named* after it).
- **DATE OF BIRTH has no home** (TaskList #41). There is no `date_observation` leaf, and a birth
  date is arguably a property of the subject ENTITY rather than an observation of it —
  `treatment.m` already routes DOB out of its tier for that reason. Real Babu/Hunsberger DOB rows
  flow through `measurement` and currently pass through unmodelled. A team modelling call.
- **THE RECURRING EPISTEMIC ERROR, stated once so it stops recurring.** Four separate places
  turned *absence of evidence* into a reassuring claim: the coverage ledger's "dissolved
  (rename/decompose)" label (32 rows), ⑥/⑦ chunk (a)'s "all 0-usage" deletions (3 of 4 wrong),
  chunk (b)'s "the epoch link is the epochid dep" (there is no such dep), and my own "latent
  risk, not active loss" for the vhlab_voltage2firingrate family. **THE CORPORA ARE A SAMPLE OF
  DATASETS, NOT THE UNIVERSE** — a class absent from the five we test may be well represented in
  a dataset still waiting to migrate, which is what this migration is FOR. Nothing may be
  deferred, retired or half-repaired on the grounds that no corpus we looked at holds it. A
  deletion needs a WRITER CHECK against NDI `origin/main`.
- **A TEST WRITTEN FROM THE SAME PREMISE AS THE CODE CANNOT CATCH THE CODE.** Three tests
  asserted the `epochid` bug (`test_phase1_source_cleanup_and_dep_typing`,
  `test_ingested_caches_epochid_dep_only`, `testMfdaqIngestedDeEncodesToDaqreaderEpochdataIngested`)
  and had to be INVERTED, not updated. The `silentLoss` counter had NO tests at all and shipped
  measuring nothing. `testFragmentCensus`'s first draft drove the detector through two migrators
  that had since been repaired, and failed correctly. Same shape as fixtures built from our own
  schema, one level up.
- **V_eta IS snake_case; NDI IS camelCase. A DISPOSITION THAT RESTS ON *ABSENCE* MUST USE
  NDI'S OWN SPELLING.** On 2026-08-06 `demo_ndi`/`demo_ndi_mock` were dispositioned DELETE
  on the evidence *"absent from NDI origin/main; referenced by NOTHING — not even the test
  suite."* Both claims were FALSE. The class is spelled **`demoNDI`**, both templates ship,
  and `+ndi/+calc/+example/simple.m` queries `demoNDI.value` and constructs `demoNDIMock`
  documents at five lines. **The grep searched `demo_ndi` against a repository that has
  never contained that string** — zero hits was a property of the query. This is the
  failure the operating rules name verbatim: *"a grep that could not have matched was
  reported as 'this does not exist anywhere'."* It survived a walkthrough, a commit and a
  board render, and was caught only because two documents happened to disagree.
  The mechanical version of the check, re-runnable: normalise both sides (lowercase,
  strip underscores) and list every V_eta name that matches an NDI name ONLY after
  normalisation.

        DENOMINATOR: 91 NDI template class_names, 224 V_eta class names
        AT RISK: 6
           demo_ndi <-> demoNDI                  <- THE BUG
           demo_ndi_mock <-> demoNDIMock         <- THE BUG
           ontology_image <-> ontologyImage             disposition rests on PRESENCE
           ontology_label <-> ontologyLabel             disposition rests on PRESENCE
           ontology_table_row <-> ontologyTableRow      disposition rests on PRESENCE
           spike_interface_sorting_outputs <-> SpikeInterfaceSortingOutputs   PRESENCE

  The other four were dispositioned from what they CONTAIN, so only `demo_ndi` was
  absence-based. **Re-run the sweep before any new disposition that turns on absence.**
  Sibling to the `depends_on` rule below: that one is about the KIND of reference, this
  one is about the SPELLING of the thing referenced.

- **A `depends_on` SWEEP IS NOT A REFERENCE CHECK. Grep for the NAME too.** Three times in one
  session (2026-08-05) a dependency-graph sweep came back empty or nearly empty while the real
  references were **string matches in ordinary fields**, and each time the "nothing references
  this" reading would have produced a DATA-LOSING decision:
  - `daqsystem` — `daqsystem_id` is referenced by NOTHING. But `daqsystem.base.name` is matched
    by `strcmpi` in `+ndi/+daq/system.m:229` (`getprobes` attributing probes to devices), named
    in every `syncrule.parameters.daqsystem1_name`/`_2_name`, and queried by `exact_string` in
    `+ndi/+time/syncgraph.m:404-408`. Dissolving it would have broken probe→device attribution.
  - `syncrule_mapping` — the same `syncgraph.m:404-408` query reads
    `epochnode_a/_b.objectname`, a field V_eta had already DROPPED, alongside a `syncgraph_id`
    edge V_eta had also dropped. A live in-tree query, broken two ways.
  - `epochid` — only `ensemble` references an epoch by EDGE. But `epochid.epochid` is matched by
    `exact_string` at **11+ live sites** (`+daq/metadatareader.m:164`, `+daq/reader.m:56`,
    `+element/timeseries.m:58`, `stimulusDocMaker.m:390,412`, `add_stimulus_approach.m:54,64`,
    `+app/spikeextractor.m:156,310,388`, `+app/+stimulus/decoder.m:114`,
    `finddocs_elementEpochType.m:32`), and **15 NDI classes carry the `epochid` superclass**.
    It is the join mechanism for the epoch-scoped half of the database.
  **Before any disposition: grep the class's `base.name`, its id STRING, and its distinctive
  field names across NDI `.m` files — not just `<class>_id` in the templates.** v1 joins by
  string wherever the referent is not itself a document, which is most of the interesting cases.
- **THE INVENTED-EMPTY-EDGE PATTERN — 26,406 documents across FIVE classes from the census,
  plus a SIXTH added 2026-08-08 from a walkthrough histogram (openminds_stimulus, 635). The
  total is deliberately NOT restated: re-derive the row set AND the sum from a fresh census
  before quoting either.** ONE cause. V_eta
  declares a REQUIRED `depends_on` that the NDI template does not have, while DROPPING the edge
  NDI does write. Every such document validates clean, because `+did2/+validate/references.m:90`
  SKIPS empty edges (`if isempty(documentId), continue;`) — so `mustBeNonEmpty` on a `depends_on`
  is decorative:

        stimulus_response_scalar_parameters_basic.stimulus_response_scalar_id
                                      11,440 docs  (Soph 11167 / 20211116 273)  NDI has the edge the OTHER WAY
        epochfiles_ingested.epochid    6,921 docs  (Dab 4088 / B 2484 / Soph 349)   NDI has filenavigator_id
        syncrule_mapping.epochid       5,316 docs  (B 2484 / Dab 2484 / Soph 348)   NDI has syncgraph_id
                                       ^^ REPAIRED 2026-08-09 (#58): the schema now declares
                                          syncgraph_id + syncrule_id, and objectname/t0_t1 are
                                          carried again. Row kept so the pattern's history stays legible.
        openminds_stimulus.stimulus_id   635 docs  REPAIRED 2026-08-09 (#71): pass 1 now emits
                                          nothing and passes the document through guarded; the
                                          tombstone declares stimulus_element_id.
        stimulus_presentation.element_id
                                       2,670 docs  (B 1242 / Dab 1242 / Soph 175 / 20211116 11)
                                                                            NDI's dep is named stimulus_element_id
        daqmetadatareader.daqsystem_id    59 docs  (100% of them)            NDI has NO deps at all


  **This line said "12,296 documents, three classes" until 2026-08-06 — an undercount by more
  than half, and it named the three SMALLEST.** The two stimulus-tier rows were found by the
  stimulus response walkthrough reading the same census (test-code.yml run #257 / 0458dae,
  2026-07-29) the original three came from; they were in the report all along and nobody had
  looked past the daq/sync families. The largest instance of the pattern is the one this note
  omitted. **Re-derive the row set from a fresh census before quoting a total.**
  In each case the count EQUALS the class's document count — 100% empty, never partially.
  `ontology_table_row`'s 76,766 empty `subject_id`s (#53) are the same failure one layer up.
  The blind spot is that `check_migrator_vocabulary.py` compares FIELDS and not `depends_on`
  (#54); the fix that would stop all of them is enforcing `mustBeNonEmpty` on edges (#37); the
  repairs are #53, #58, #61 and the ones recorded in `V_eta_epoch_plan.md` +
  `V_eta_stimulus_response_model_plan.md` (`stimulus_presentation.element_id` rides with the
  stimulus model, #31/#43). **Treat these as ONE problem, and check a new required edge against
  the NDI template before adding it.**
- **WHEN AN INLINE VALUE STAYS ALONGSIDE ITS EDGE — and when only the edge survives.** Two
  decisions on 2026-08-05 went OPPOSITE ways and neither is a precedent for the other, so the
  test is written here rather than in one plan document. `strain` KEEPS its inline
  `term.value = {node, name}` AND gains `strain_id`; `epochid` is DROPPED ENTIRELY in favour of
  `epoch_id`. Three questions decide it:
  1. **Is the inline value a complete fact on its own?** A CURIE naming a real thing (`WBStrain:
     00000002`) is; a bare local id (`"t00023"`) is not.
  2. **Will the referenced document always exist?** 115 strains carry no identifier and may
     warrant no document, so the assertion must stand alone. One `epoch` is minted per distinct
     id, by construction, so its edge cannot dangle.
  3. **Is the value the document's CONTENT or a JOIN KEY?** A `term_assertion` *is* a statement
     about its value — strip it and the document says nothing. An epoch id is stapled on — strip
     it and the document still says everything it said.
  **The drift test is what actually decides it** (`V_eta_openminds_family_record.md` Part 3: a
  representation must not vary between datasets). Dropping strain's inline value would make
  `variable: strain` resolve two ways depending on whether a pedigree happened to exist.
  Dropping `epochid` creates no drift, because every epoch-scoped document gets its edge
  uniformly. In one line: **strain — the value IS the fact and the document is optional extra
  structure; epoch — the document IS the fact and the string was only ever a way to find it.**

## Build / test
- `python3 tools/build_v_eta.py` rebuilds `schemas/V_eta/` (copytree V_zeta→V_eta
  then transforms). `python3 -m pytest tests/test_veta.py -q` checks the schema.
- Migrators live in DID-matlab `+did2/+convert/+migrators_j/`; corpus validation is
  DID-matlab `test-code.yml` (full, ~1–2h) and `test-migrators-quick.yml` (~2 min).
