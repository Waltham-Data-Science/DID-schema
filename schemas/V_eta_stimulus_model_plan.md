# V_eta — the stimulus model (DECIDED; build deferred)

*Worked design for how V_eta represents stimulus presentations, decided in the fresh-eyes
re-audit walkthrough. **FINAL; build deferred** — batched. Supersedes the earlier
"stimulus_presentation → visual_grating_manipulation dissolve" (#19). Cross-refs:
`V_eta_tenets.md` (T3 direction×data_type, T6 storage/cache, T7 instrument), the
ndi-next-steps `Stimulus_Manipulation_Proposal.md` (prior art, V_delta/Brainstorm-F frame —
mined, not adopted wholesale). Subject to further re-audit like every decision.*

## The model (final)

A stimulus presentation is an **ordered, timed list of referenced stimulus values shown to a
subject**. Two classes, factored on J's T3 (leaf = direction × data_type):

1. **`timed_sequence`** — a **`data_type`** (③). The value: an ordered, timed list of
   **references to other `data_type` documents** (the distinct stimuli) + the order + timing.
   **Direction-neutral** (chosen deliberately so a future `timed_sequence_observation` is
   possible without renaming; today only the manipulation leaf exists). Shape:
   - `depends_on`: `presented_id → data_type` (**broad — the abstract parent**, so ANY typed
     value doc — `visual_grating`, `image`, a sound, a future type — can be referenced),
     **multiple**, one per **distinct** stimulus (deduped by content).
   - value: `presentation_order` (an index array into the `presented_id` refs — the playlist;
     e.g. 225 distinct refs + a 4000-long index array for a Hartley run). **Distinct-refs +
     index-array encoding** (normalized; not one ref per trial).
   - `files`: the per-trial timing (`presentation_time.bin`) — onsets/offsets.
   - `storage_mode` (T6) governs inline-vs-shared (see multi-subject below).

2. **`timed_sequence_manipulation`** — the **leaf** (④) = `subject_manipulation` +
   `timed_sequence`. Adds:
   - `subject_id` → the subject shown the sequence (required, by tier).
   - `instrument_id` → the **stimulator** device (T7 — the stimulator is the *instrument*,
     exactly parallel to the electrode on a `voltage_observation`; **replaces** the v1
     `stimulus_element_id`).
   - `time_reference` → `epoch_bounded_reference` (a presentation spans an epoch).

## Why this shape (the walkthrough reasoning)

- **Stimuli are values, referenced — not dissolved, not duplicated.** Each distinct config
  (e.g. each of the 225 Hartley basis gratings) is a **standalone `visual_grating` document**
  (an instance of the `visual_grating` data_type — which already has a `document_class`, so it
  can stand alone and be referenced). Stored **once**, queryable directly, reusable/dedupable
  across presentations. This is the **ensemble pattern** (reusable atoms + ordered references),
  applied to stimuli.
- **The reference is broad (`→ data_type`).** One manipulation shape covers gratings, images,
  sounds, any typed stimulus — no per-stimulus-type manipulation class. (This is why the
  earlier "mint hartley_stimulus / sparse_noise / dispatch-by-type" branch is **moot**: the
  stimulus type lives in the referenced data_type doc, not in the manipulation.)
- **Multi-subject falls out of `storage_mode`, not a structural fork.** Because
  `timed_sequence` is a data_type, its value can be **inline** (single subject: the playlist
  lives in the manipulation) or **reference** (multi-subject: one shared standalone
  `timed_sequence` doc, and N `timed_sequence_manipulation`s — one per subject — reference it;
  the heavy config docs are shared by reference either way, only nothing duplicates under
  reference mode). Same inline-vs-reference knob every value has (T6), same "value by reference
  to a body-of-record" pattern as the recording and ensemble decisions.
- **Manipulation, not observation** (now): presenting stimuli *acts on* the subject (T7
  patient/agent; the project-wide "presenting is manipulating" stance). No compelling
  observed-ordered-sequence case was found; the data_type name is kept neutral so an
  `_observation` leaf can be added later if one arises.
- **`visual_grating` stays exactly what it is** — a `data_type`. It is no longer *dissolved
  into* a manipulation; it is *referenced by* a `timed_sequence`. (`visual_grating_manipulation`
  — the direct inline-grating leaf — may still serve a presentation-less single-grating case;
  reconcile in the build.)

## Worked example (Hartley reverse-correlation, one subject)

```json
// 225 distinct configs → standalone visual_grating docs (stored once each, deduped by content)
{ "class_name": "visual_grating", "base": { "id": "grating_kx0_ky1" },
  "visual_grating": { "value": { "kx": 0, "ky": 1, "phase": 0 } } }
// ... 224 more ...

// the timed_sequence value (here shared/standalone; storage_mode reference)
{ "class_name": "timed_sequence", "base": { "id": "presentation_epoch7" },
  "depends_on": [ { "presented_id": "grating_kx0_ky1", "must_refer_to": "data_type" }, ... ],
  "timed_sequence": { "value": { "presentation_order": [3,17,3,200, ...] } },   // indexes the refs
  "files": [ "presentation_time.bin" ] }

// the manipulation leaf (one per subject; references the shared timed_sequence)
{ "class_name": "timed_sequence_manipulation",         // [subject_manipulation, timed_sequence]
  "base": { "id": "stimman_ferret1_ep7" },
  "depends_on": [
     { "subject_id": "Ferret_001" }, { "instrument_id": "stimulator_vhvis" },
     { "time_reference": "epoch7_bounded_ref" },
     { "timed_sequence_id": "presentation_epoch7" } ],
  "subject_statement": { "storage_mode": "reference" } }
// multi-subject: a second timed_sequence_manipulation (Ferret_002) referencing the SAME
// presentation_epoch7 — shared playlist.
```

Queries: "all manipulations on Ferret_001" = `isa timed_sequence_manipulation` + subject.
"presentations using a 45° grating" = find the `visual_grating` doc at ~45° (atan2(ky,kx)) →
its referrers (`timed_sequence`s) → their manipulations → subjects. A reverse lookup on a
first-class typed doc — no dictionary-digging.

## Migration (build conditions)

- **Decompose the v1 `stimulus_presentation`**: its `stimuli` dictionary → N standalone
  `data_type` docs (deduped by content); its `presentation_order` → the index array; its
  `stimulus_element_id` → `instrument_id`; mint the `timed_sequence` + (per resolved subject)
  a `timed_sequence_manipulation`. Reading the dictionary + resolving the subject(s) from the
  syncgraph is a **2nd-pass** job (like ensemble/Path-S), not a single-doc migrator step.
- **id / no-orphan**: the v1 `stimulus_presentation` id is preserved on the body-of-record it
  becomes (the `timed_sequence`), so `stimulus_response.stimulus_presentation_id` and other
  fan-in dependents resolve — **the presentation is not renamed/destroyed, it is decomposed
  around its preserved id.** (Compare the dissolve model, which had to reassign the id and
  broke for shared/multi-subject presentations.)
- **stimulus_response** keeps referencing the presentation body (now `timed_sequence`);
  per-trial detail stays inside it (`responses` keyed by stim). Grain 1 confirmed (one
  manipulation per presentation, not per trial), grounded in the dependency shape.
- **Retire** the v1 `stimulus_presentation` class only after the decomposition lands; until
  then it is a green passthrough. Supersedes #19 (visual_grating_manipulation dissolve).

## Open / deferred

- **Naming** `timed_sequence` is provisional pending the T11/T13 naming pass (neutral by
  design; the leaf `timed_sequence_manipulation` reads a little flat for "a stimulus
  presentation" — accepted cost of neutrality).
- **`control_stimulus_ids` → `control_designation` — RESOLVED.** A separate **derived**
  annotation doc (option c): references the `timed_sequence` + the control stimulus `data_type`
  doc(s), carries the `method` (how derived), marked `derived_from`/`software_id` (T10 — it is
  computed by the `tuning_response` app, `tuning_response.m:653–656`). NOT baked into the
  immutable body. Renamed off the `ids` container word (T13); `app` straggler dropped. The
  app always sets `stimulus_presentation_id`, so presentation-less docs are a non-issue.
- **`stimulus_approach` — RESOLVED: no such class in V_eta.** Investigated the writer
  (`add_stimulus_approach.m`): it creates **openMINDS `StimulationApproach` controlled terms**
  per epoch (looked up from the ontology, e.g. "spatial frequency tuning") — i.e. an *approach/
  purpose term tagging an interaction*, not a bespoke condition class (matching the proposal's
  own note that it drifted onto purpose content). So: a stimulus "approach" **folds into
  `interaction_purpose`** (an approach term on the epoch's interaction, via the openMINDS
  controlled-term path); genuine out-of-band *subject conditions* ("left eye occluded"), if ever
  needed, are a **`term_observation` of the subject** (epoch-scoped). No new class; the stale
  `stimulus_approach` provenance row is corrected to RETIRE.
- **`visual_grating_manipulation`** reconciliation (keep for presentation-less single gratings,
  or retire) — build-time.
- **Hartley/sparse-noise data_types — RESOLVED.** A **Hartley basis function IS a
  `visual_grating`** (the Ringach basis = 2-D sinusoidal gratings indexed by `(kx,ky,sign)`,
  inter-convertible with `(orientation,sf,phase)`; the proposal itself calls the dictionary
  "the 225 Hartley basis functions"). So each is a referenced `visual_grating` doc — **no
  `hartley` data_type**. The only residual is a **build-time param-mapping check** against the
  vhlab code (NDIcalc-vis, out of scope here) — a verification, not a design fork.
  **`sparse_noise`** earns its own `data_type` **only if/when a real corpus needs it**
  (mint-when-warranted, T12, like `kernel`); until then it's just another referenced
  `data_type` doc. The "dispatch by stimulus type" branch stays moot (stimulus type lives in
  the referenced doc).
