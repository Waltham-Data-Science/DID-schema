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

## Resolved (naming pass + walkthrough) / build-deferred

- **Naming — FINAL.** `timed_sequence` + `timed_sequence_manipulation` confirmed in the naming
  pass (neutral by design so a future `_observation` leaf is possible; the leaf reads a little
  flat for "a stimulus presentation" — accepted cost of neutrality). Not provisional.
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

---

## THREE REVISIONS 2026-08-08 — the sections above are superseded on these points

All three follow from decisions signed the same day. The MODEL is unchanged: stimuli are
deduped, referenced values plus an ordered playlist — the ensemble pattern applied to
stimulation. What changed is where three of its pieces attach.

### 1. `epoch_bounded_reference` NO LONGER EXISTS

The model says `timed_sequence_manipulation.time_reference -> epoch_bounded_reference`.
That class is one of the **eight collapsed into `absolute_reference` + `relative_reference`**
(`V_eta_time_reference_model_plan.md`, SIGNED 2026-08-08). It had **ZERO documents** and no
migrator ever emitted one. A presentation spanning an epoch becomes:

```
time_reference -> relative_reference
                     relative_to  -> epoch
                     clock        -> ontology_term, one of the FOUR NDIC clocktype terms
                     start        -> anchor   { seconds, source_unit, source_value, approximate }
                     duration     -> extent   { … }        ABSENT means an instant
```

Note `start` + **`duration`**, not `start`/`end` — the anchor and the extent are independent
facts and now carry independent `approximate` flags.

### 2. `presentation_time` goes through the BODY TIER, not a bare `files` slot

The model hangs `files: presentation_time.bin` directly off the `timed_sequence` composite.
Under the data_body decision (`V_eta_data_body_model_plan.md`), per-trial onsets are an
**irregular time axis**, and a composite reaches its payload through `storage_mode` exactly as
`image` reaches its pixels:

```
storage_mode: body   ->   sampled_body
                             depends_on  statement -> the timed_sequence_manipulation
                             axes[1]  variable: time
                                      regular: false
                                      values:  { values: [onsets…], source_values: … }
                                      n:       the trial count
                             datum_type / byte_order / datum_order as declared
```

And **`presentation_time.clocktype` does NOT land on the axis.** An axis has a `variable` and
no clock; the clock lives on the time reference. So `clocktype` goes to the manipulation's
`relative_reference` (revision 1), not into `axes[]`.

The v1 block is `presentation_time { clocktype, stimopen, onset, offset, stimclose,
stimevents[] }` — so `onset`/`offset` are the axis values, `stimopen`/`stimclose` are the
outer bounds, and `stimevents` needs its own read before it is typed.

### 3. `derived_from_1` -> `derived_from_#` — FIXED IN THE BUILD, not deferred

`control_designation` was the ONLY class in the set declaring a **concrete numbered edge
instance** where the FAMILY belongs. `subject_calculation` and `subject_observation` both
declare `derived_from_#`. A schema declares the template name; a DOCUMENT names the instances.

Hardcoding `_1` also silently capped provenance at ONE antecedent, which T10 does not.

```
BEFORE  dep("derived_from_1", "subject_interaction", …)
AFTER   dep("derived_from_#", "subject_interaction", …)
226 schemas, 497 tests green.
```

Its cardinality is unexpressed until **#63**, like every other `_#` family.

> **A note on how this one was found, because the reverse mistake was made hours earlier.**
> A claim that `scalar_temperature_observation` declared an untyped `time_reference_1` was
> reported and was FALSE — that file is an EXAMPLE DOCUMENT under `schemas/V_eta/examples/`,
> and a document naming `time_reference_1` is correct. `control_designation` is the genuine
> case: a CLASS, in `draft/`, declaring the index. The distinction is whether the file carries
> `document_class` + `fields` (a schema) or `base` + `depends_on` with `value`s (an instance).
