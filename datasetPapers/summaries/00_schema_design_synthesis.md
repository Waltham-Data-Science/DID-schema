# Cross-Paper Synthesis: NDI Document Types for the 7 `datasetPapers`

This note synthesises the seven per-paper summaries in this directory into a proposal for the minimal set of NDI document types needed to fully encapsulate the data + metadata for reuse, plus a validation strategy that balances standardisation with per-paradigm flexibility. This is a design sketch for discussion, not a decided plan.

## Common themes that recur across all 7 papers

Even across tree shrew / rat / ferret / mouse / *C. elegans* / *C. briggsae*, and across in-vivo ephys / slice ephys / behavior / imaging / LC-MS, the same structural skeleton appears:

- **Something-subject**: an organism (or population, for *C. elegans*) with species + strain/genotype + developmental stage + sex + source.
- **Something-treatment**: drugs, surgeries, AAV injections, eye-opening, water restriction, chemical supplementation — every paper has at least one, most have several staged over days/weeks.
- **Something-apparatus**: probes, opto-fibers, cannulas, EMG wires, cameras, microscopes. Provenance matters (fabrication, calibration, impedance, magnification).
- **Something-placement**: where the apparatus was put (stereotaxic coordinates, laminar depth, arena geometry, slide orientation).
- **Something-stimulus**: visual gratings, tastants, heat + odor, bacterial patches, light pulses, shock + cue, startle noise. Often *factorial* (orientation × SF × TF, direction × TF, taste × perturbation timing).
- **Something-trial/epoch**: a time window with defined conditions, linked to stimulus presentations.
- **Something-raw-stream**: spikes, LFP, EMG, videos, Z-stacks, mass spectra.
- **Something-derived**: tuning curves, fits (DOG / Movshon / Naka-Rushton), indices (CI, LPI, 1 − CV), classifiers (GMM/QDA/HMM), change points.
- **Something-histology**: post-hoc anatomical verification (DiI tracks, NeuN, CO, immunolabel).
- **Something-publication/access**: DOI, repo, NDI-Cloud accession, or "contact the PI."

The key *differences* across papers are what fills those slots, not the slots themselves. That's the design lever.

## Proposed minimal document set (~15 core types)

Most of these already exist in some form in the schema:

1. **`subject_identifier`** — the immutable tag that ties together all of a given subject's records (per `Ideas.md`).
2. **`subject`** — species / strain / sex / age / source metadata; extend for populations (e.g., a plate of worms).
3. **`session`** — time-bounded experimental run; `depends_on` subject.
4. **`treatment_protocol`** — reusable *recipe* (no timestamps, no subject). Carries step list, cycle count, and references to stimuli/drugs/environments. Versioned so "Dahiya 2019 LTAM training v1.2" is a single citable object. See the "Cyclic and multi-stage treatments" section below.
5. **`treatment_event`** — *execution* of a `treatment_protocol` against a specific `subject`/`subject_group`/`substrate`, with clock times and optional per-step deviations. Naturally a specialisation of `epoch`. Subclasses of either type: `anesthesia`, `drug_administration`, `surgery`, `stereotaxic_injection`, `cannulation`, `sensory_manipulation`, `training`.
6. **`apparatus`** — abstract base; subclasses: `probe` (with construction + impedance history), `optical_fiber`, `cannula`, `emg_electrode`, `camera`, `microscope`.
7. **`placement`** — subject-relative location of an apparatus; subclasses for stereotaxic vs arena vs slice.
8. **`stimulus`** — abstract base; subclasses: `visual_grating`, `visual_bar`, `auditory`, `tactile`, `taste`, `optogenetic_pulse`, `chemogenetic_dose`, `chemoattractant_field`, `foot_shock`.
9. **`trial`** / **`epoch`** — window with trial-type factors and references to stimulus + treatment + apparatus-in-use.
10. **`recording`** — raw stream (channels, sampling rate, filter, file pointer).
11. **`observation`** — non-ephys measurement: behavior score, EMG burst, gape event, chemotaxis index, imaging puncta count.
12. **`analysis_output`** — derived data: tuning curve, fit, classification, spike sort, change point — with links back to the `recording`s and `trial`s that produced it and the `analysis_model` that produced it.
13. **`histology`** — section-level anatomical verification, stains, lesions, track reconstruction.
14. **`data_access`** — how to get the raw bytes: DOI, NDI-Cloud accession, Zenodo, request-only contact, file share path.

Plus one type that the edge-case analysis below adds:

15. **`substrate`** — a physical medium prepared ahead of time, shared across subjects/trials, that can itself carry a history of treatments and observations: agar plates, nematode arenas, brain slices, coverslips. See "Edge case 1" below for why this doesn't reduce to `apparatus`.

Plus two cross-cutting supports already half-built in the current schema:

- **`analysis_model`** — schema for fit families and their parameter structures; generalises `data/fitcurve`, `apps/calculators/tuningcurve_calc`, and `apps/vhlab_voltage2firingrate/vmspikefit` using the existing `dynamic_keys_from: "fit_function"` pattern.
- **`factor_design`** — expresses factorial / covaried trial structure (orientation × SF × contrast with shared blank; taste × perturbation timing). This is what the current `stimulus_parameter_table` / `stimulus_presentation` pair is reaching for.

### Hierarchy (via `depends_on`)

```
subject_identifier
    └── subject
          └── session
                ├── treatment_event* ─── treatment_protocol, (subject | substrate)
                ├── apparatus* ─── placement
                ├── stimulus*
                ├── trial/epoch* ─── stimulus, treatment_event
                ├── recording ─── apparatus, placement
                ├── observation
                ├── analysis_output ─── recording / trial / analysis_model
                ├── histology ─── subject, placement
                └── data_access

treatment_protocol  (library, not per-session; reusable across sessions and labs)
    └── depends_on other treatment_protocols (for composition)
```

(`*` = typically many per session.)

## Validation strategy — three layers, hybrid

1. **Structural (JSON Schema Draft 7, as today).** Handles types, required fields, enums, min/max, regex on identifiers. Good at "does this document have the right shape." Already wired up via the meta-schema.

2. **Class-hierarchical (superclass + subclass).** Use the existing `superclasses` mechanism to define abstract bases (`stimulus`, `treatment`, `apparatus`) with mandatory shared fields, and concrete subclasses for modality-specific fields. *Critical move*: keep the base **narrow** (just enough to link to a trial/session and expose a discriminator) and push modality fields into subclasses — otherwise you get a kitchen-sink base that fails to validate any real document.

3. **Ontology-backed controlled vocabularies.** The `ontology` field already exists; wire it to real terms for the highest-leverage axes:
   - **NCBITaxon** — species.
   - **UBERON** + Allen CCF — anatomy.
   - **ChEBI** / **DrugBank** / **RRID** — reagents, drugs, antibodies, cell lines.
   - **PATO** — qualities (sex, age, developmental stage).
   - **EFO** — experimental factors.
   - **openMINDS** — where already aligned.

   Validation at ingest checks the term resolves and is of the expected kind (e.g., "species must be a descendant of `NCBITaxon:33208` Metazoa").

Where per-paradigm flexibility is essential, lean on the existing **`structure` type with `dynamic_keys_from`** convention — typed at the parent ("these keys come from the `fit_function` field") rather than left as opaque JSON. That pattern is already adopted for ~14 fields and should remain the main escape hatch.

### Optional: add a `profile` / paradigm concept

Consider adding one new concept: a **profile** document that declares, per experimental paradigm, which document types must be present and which are optional (e.g. "visual-ephys profile", "slice-ephys-pharmacology profile", "worm-behavior profile"). This separates *schema correctness* (always enforced) from *paradigm completeness* (profile-dependent) and keeps the base schemas lean.

## Main tradeoff to decide

The core tension is **depth of subclassing vs. use of `structure` + `dynamic_keys`**.

- **Deep subclassing** (a schema per stimulus type) gives strong validation and IDE/tooling support but creates a long tail of rarely-used schemas and slows down new experiments.
- **Wide `structure` + `dynamic_keys`** stays flexible but pushes validation out to consumer tooling and ontology lookups.

Recommendation: subclass the *common* cases you can see across these seven papers (~5–8 stimulus types cover almost everything here) and use `dynamic_keys` for the long tail.

## How the 7 papers map onto the proposal

| Paper | Subject | Notable stress-tests for the schema |
|---|---|---|
| Van Hooser 2013 (tree shrew V1) | tree shrew | multi-electrode-type `probe`, laminar `placement` with normalised depth, `stimulus/visual_grating` + `visual_bar`, DOG fits |
| Francesconi 2025 (BNST AVP/OT) | rat (transgenic Cre) | `stereotaxic_injection` w/ AAV Addgene IDs, `cannulation`, bath-drug `treatment` with washout, `optogenetic_pulse` bursts, multi-assay behavior (FPS + EPM) |
| Reikersdorfer 2022 (carbon fiber MEA) | mouse + ferret | `probe` *construction* provenance (fiber, parylene, gold plating), impedance history, two species in one paper |
| Bhar 2025 (*C. elegans* EV LTAM) | worm population | population-level `subject`, cyclic `training_protocol`, `stimulus/chemoattractant_field`, LC-MS `observation`, chemical supplementation `treatment` |
| Haley 2024 (*C. elegans* foraging) | worm, individual + group | arena geometry `placement`, patch-density `stimulus`, environmental covariates, tracking pipeline → `observation`, normative model → `analysis_model` |
| Griswold 2025 (ferret premature vision) | ferret, female | developmental `sensory_manipulation` with per-eye timing, multi-group design, mixed-effects `analysis_model` |
| Mukherjee 2019 (rat GC taste) | rat, female | simultaneous ephys + EMG + IOC, factorial trial design (`factor_design`), ArchT `optogenetic_pulse` with timing variants, Bayesian hierarchical `analysis_model`, HMM change-points, request-only `data_access` |

## Cyclic and multi-stage treatments

Many paradigms across these papers are cyclic or multi-stage: Bhar's 5× (2 min IAA+heat / 10 min rest) → 20 h rest → readout; Mukherjee's 20 mL/day × 7 day water restriction; Francesconi's 10 min antagonist → 12–15 min AVP+antagonist → 12–15 min washout; Griswold's 2 h/day × 4 day exposure. The clean way to represent these is to separate **recipe** from **execution**.

### Pattern: `treatment_protocol` (recipe) + `treatment_event` (execution)

**`treatment_protocol`** — reusable template, no timestamps, no subject:

- `name`, `version` — so protocols are citable objects (semantic versioning, same convention as schema files).
- `steps` — ordered list; `structure` field with `dynamic_keys: true`, one entry per step, each with:
  - `step_type` — controlled enum: `exposure`, `rest`, `washout`, `wait`, `readout`, `sub_protocol`.
  - `duration` (+ tolerance if relevant).
  - `stimulus` / `drug` / `environment` references.
- `cycles` — number of times `steps` repeat, plus any between-cycle interval.
- `depends_on` other `treatment_protocol`s — protocols compose, so an outer protocol can reference an inner one.

**`treatment_event`** — actual execution:

- `depends_on` a `treatment_protocol` **and** a `subject`/`subject_group`/`substrate`.
- `start_time`, `end_time` (wall-clock or session-relative).
- `deviations` — optional list of per-step actual timings, missed cycles, dose adjustments, environmental excursions.
- One `treatment_event` per real execution.

A `treatment_event` is naturally a specialisation of `epoch`: it inherits time-boundedness so spikes, videos, and observations can be aligned against it the same way they align against any other epoch.

### Worked example — Bhar 2025 LTAM training

```
treatment_protocol: "Bhar 2025 IAA+heat LTAM training"
  steps:
    - step_type: sub_protocol
      ref: "IAA+heat pairing cycle"
      cycles: 5
      inter_cycle_gap: null     # gap is inside the sub-protocol
    - step_type: rest
      duration: 20 h
      environment: "22 °C incubator"
    - step_type: readout
      ref: "chemotaxis_index_assay"

treatment_protocol: "IAA+heat pairing cycle"
  steps:
    - step_type: exposure
      duration: 2 min
      stimulus_refs: ["heat_pulse", "IAA_vapor"]   # co-applied
    - step_type: rest
      duration: 10 min
      environment: "22 °C"

treatment_event: "Plate A, experiment 2025-04-12"
  protocol: "Bhar 2025 IAA+heat LTAM training"
  applied_to: substrate "60 mm NGM plate #A"       # note: substrate, not subject
  subjects: subject_group "~30 N2 young-adult hermaphrodites"
  start_time: 2025-04-12T10:00
  end_time:   2025-04-13T06:30
  deviations: []
```

Composition via `depends_on` between protocols lets the pairing cycle be authored once and reused by future paradigms (diacetyl + heat, 3 vs 5 cycles, etc.) without duplicating the cycle definition.

### How this pattern covers the other papers

| Paper | Outer protocol | Inner unit |
|---|---|---|
| Bhar 2025 | 5× IAA+heat pairing, 20 h rest, readout | 2 min exposure + 10 min rest |
| Mukherjee 2019 water restriction | 20 mL/day × 7 days from habituation day 2 | 1 day allocation |
| Mukherjee 2019 session | 128 trials, pseudo-random, 16 sets × 8 trials | 1 trial (taste ± laser) |
| Francesconi 2025 ephys drug | 10 min antagonist → 12–15 min antagonist + AVP → 12–15 min washout | single bath step |
| Griswold 2025 premature exposure | 2 h/day × 4 days from P25 | one 2 h session |
| Haley 2024 acclimation | 24 h on large OP50 patch at 20 °C | one plate |
| Reikersdorfer 2022 post-op | buprenorphine SR 0.5–1 mg/kg at t=0, antibiotic 24/48 h | single drug administration |

The same protocol/event split expresses all of these.

### Open design questions specific to cyclic treatments

- **`treatment_event` as a subclass of `epoch`?** Cleaner alignment with downstream queries (spikes/videos already know how to reference an epoch); costs a small increase in the epoch taxonomy.
- **Per-step events.** Does a reader need to query "what happened during cycle 3, step 2"? Default to one flat `treatment_event` + a `deviations` field; emit per-step sub-events only when something non-nominal actually happened.
- **How strict should `steps` be?** `structure` with `dynamic_keys` + a controlled `step_type` enum gives flexibility; a fully enumerated list of typed step subclasses gives stricter validation but much more schema volume. Lean flexible — with this many paradigms the long tail will never close.

## Edge cases that strain the core proposal

The core list above covers the main skeleton, but several specific patterns across these papers don't fit cleanly. The most important is the **"plate as subject"** pattern.

### Edge case 1 — plate-as-measured-object (Bhar 2025, Haley 2024)

In both *C. elegans* papers the agar plate is simultaneously (a) the environment, (b) the stimulus source, and (c) the thing being measured. Concretely:

- **Bhar 2025** — after training, worms are removed and *the plate itself* is the object under test. Naïve worms placed on a "trained plate" acquire LTAM 20–24 h later; naïve worms placed on a "naïve plate" do not. The plate carries a causally relevant history (trained / naïve / heat-killed *E. coli* / IAA-only / klp-6 mutant-trained / cross-species).
- **Haley 2024** — patch density (from OP50-GFP fluorescence), patch-edge position, growth time, and isometric-grid layout are measured *per plate* before the assay starts. Multiple worms on the same plate share these measurements; worms on different plates do not.

Neither fits into `subject`, `treatment`, `stimulus`, or `apparatus` cleanly.

#### Proposed extension — new type: `substrate`

A physical medium that is (i) prepared ahead of the session, (ii) shared across multiple subjects/trials, and (iii) can itself carry measurements and a history of treatments.

Fields:

- `substrate_type` enum: `ngm_agar_plate`, `nematode_arena`, `brain_slice`, `coverslip`, `microfluidic_chip`, ...
- `geometry` — dimensions / shape (Ø 60 mm plate, 30 mm PET arena, 300 µm slice).
- Accepts `treatment` documents via `depends_on` (seeding with OP50, chemical supplementation, prior-occupant exposure).
- Accepts `observation` documents (patch-density map, contrast video, LC-MS of supernatant).
- Accepts `stimulus` documents (the patches *are* the stimulus to any worm placed on the plate).

Position in the hierarchy:

```
session ─── substrate ─── {treatment*, observation*, stimulus*}
           ↑
           └── subject (or subject_group) is "placed on" this substrate
```

This also subsumes slice electrophysiology cleanly: a `brain_slice` substrate is prepared, treated (aCSF composition, drug wash-in), recorded from (patch recording = a `recording` scoped to that substrate), and has its own histology.

#### Proposed extension — new relationship: `placement_on` (subject ↔ substrate, time-bounded)

Not a simple `depends_on` — it's time-windowed and reversible. Bhar's exchange assay is literally *moving subjects between substrates within 30 min of training* and measuring 20–24 h later. The same applies to Haley's transfer of animals onto a condition plate via agar plug.

Modelling this as an `epoch`-like document with `subject`, `substrate`, start time, end time, and transfer method (agar plug, eyelash pick, M9 wash) makes the exchange assay expressible and the "which plate was this worm on when?" question answerable.

#### Other patterns this single addition covers

- **Haley's "contrast video"** — a per-plate measurement made *before* worms are added, used later to register patch locations onto the behavioural recording. It's an `observation` on the `substrate`, not on any subject.
- **Bhar's LC-MS of supernatants** — samples collected per-plate after differential centrifugation. Again, `observation` on `substrate`, with no individual subject attached.
- **Pharmacology bath solutions** (Francesconi, Mukherjee in-vitro) — aCSF composition is a property of the slice's environment over time; maps cleanly to `substrate` + time-varying `treatment`.

### Edge case 2 — cross-species exchange (Bhar 2025)

A naïve *C. elegans* placed on a plate that held trained *C. briggsae*. Needs either two `subject` documents sharing one `substrate`, or species-agnostic `substrate` with per-species `subject_group`. The `substrate` extension above makes this straightforward: the substrate has a history that is species-agnostic, and each `placement_on` event carries its own species-typed `subject_group`.

### Edge case 3 — longitudinal reuse of one subject (Reikersdorfer 2022)

Chronic mouse recordings demonstrate stable single units at 11 months post-implantation. The same `subject` + `probe` + `placement` persists across hundreds of `session`s. Implications:

- `session` should carry `days_since_implant` (or more generally, an offset from a named reference event on the subject's timeline).
- `placement` is a persistent object, not per-session; each session `depends_on` an existing `placement` rather than creating one.
- Impedance measurements are per-session per-channel time-series — argues for a dedicated `observation/impedance` rather than embedding in `probe` or `placement`.

### Edge case 4 — multi-stage protocols with rest periods (Bhar 2025, Mukherjee 2019 water restriction)

Training paradigms are cyclic (2 min pair × 5 with 10 min rest; then 20 h rest; then readout). Water-restriction regimens run for days. These don't fit a single `treatment` document cleanly unless the schema allows either:

- A **schedule** embedded in one `treatment` document (structure with dynamic keys per cycle), or
- Many small `treatment` documents per cycle linked to a parent `training_protocol`.

See open question 2 below.

### Edge case 5 — data that is shared across papers (Griswold 2025 ↔ Van Hooser 2013 style reuse)

Mukherjee 2019 explicitly re-analyses 10 rats from Sadacca et al. 2016 and Li et al. 2016. The schema should let an `analysis_output` `depends_on` `recording`s that live in *other* datasets (other NDI-Cloud accessions). This argues for `data_access` references to be first-class citizens that `analysis_output` and `recording` can both point to, rather than an embedded field on `session`.

## Open questions to resolve before writing schemas

1. Is populational `subject` (a plate of worms) a first-class alternative to individual `subject`, or is it always a `subject_group` wrapping N individual `subject`s?
2. ~~Do we want `treatment` to be one document per administration or one document per protocol with a schedule inside it?~~ *Resolved in "Cyclic and multi-stage treatments": split into `treatment_protocol` (recipe) + `treatment_event` (execution).*
3. How much should `analysis_output` be schema-constrained vs. free-form? Right now the existing `apps/calculators/...` schemas are very specific — do we want that pattern for every new analysis, or a single generic `analysis_output` with a `method` reference?
4. Is a `profile` / paradigm concept something we want in the schema layer, or kept in consumer tooling (MATLAB/Python libraries)?
5. Should `data_access` be a separate document or an embedded field on `session` / `recording`? (Edge case 5 argues separate.)
6. Should `substrate` be a top-level type, or is it better modelled as a specialised `apparatus`? (The "has its own history of treatments and observations, independent of any subject" semantics argues for top-level.)
7. How do we represent `placement_on` — as an `epoch` subclass, or as a distinct linking-document type?
8. Is `treatment_event` a subclass of `epoch`, or a sibling type that references an epoch?

## Possible next step

Sketch stub schema files for the ~15 core types on a new branch, then pressure-test the design by instantiating example documents from the metadata captured in each paper's summary — especially the edge cases above (Bhar exchange assay + cyclic training, Haley contrast-video-per-plate, Reikersdorfer 11-month chronic recordings, Mukherjee re-analysis of external data). Failures to express any of these cleanly would drive the next round of schema revision.
