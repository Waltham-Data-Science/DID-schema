# V_eta — NDI second-pass plan

Status: design. Grounded in the existing harness (`ndi.migrate.local`,
`ndi.migrate.internal.bodyResolver` / `stimulusBathToBath` / `pathSPromotion`).

## The harness (how the second pass works)
1. A pass-1 migrator that needs the recording graph does NOT quarantine — it
   `error('did2:convert:needsSessionContext', ...)` to DEFER the v1 doc.
2. `ndi.migrate.local` builds `resolver = bodyResolver(bodies)` over the **v1** body
   set (the source graph) and runs the second pass on the deferred docs.
3. Two sub-pass shapes:
   - **per-document** (`stimulusBathToBath(v1Body, resolver, targetVersion)`) — resolve
     one deferred doc's context, emit the complete V_eta doc (id preserved).
   - **whole-corpus** (`pathSPromotion(structs)` → `kept/minted/changed`) — graph
     analysis across all bodies; mint/retarget.
4. Minted bodies fold back through `v1_to_v2`. Sub-passes are UNIT-TESTABLE without a
   corpus (see `TestPathSPromotion`).
`bodyResolver` today: `subjectOfElement(elementId)`,
`epochClockOfElement(elementId, epochId)`.

## Item 1: stimulus_presentation → visual_grating_manipulation (body-backed)
DECISION (architect): a visual `stimulus_presentation` becomes a body-backed
`visual_grating_manipulation` on the ANIMAL. The target leaf is the new
`visual_grating` composite (angle, spatial_frequency, temporal_frequency, contrast,
size, position, duration, is_blank) — a grating is inherently multi-parameter, so it is
its own data_type, NOT one of the single-quantity leaves and NOT a `stimulus_manipulation`
class (which doesn't exist).

**Animal resolution — SOLVED (no syncgraph needed):**
`stimulus_response` carries BOTH `stimulus_presentation_id` and `element_id` (the
responding element). So: presentation ← stimulus_response (stimulus_presentation_id) →
element_id → `resolver.subjectOfElement` → the animal. That is the semantic link (the
stimulus was presented and this element responded). Add
`bodyResolver.subjectsForPresentation(presentationId)`.

**Body of data — the stimulus TIMELINE.** A presentation shows MANY stimuli
(`presentation_order` + the `stimuli[i].parameters` array + `presentation_time`), so the
manipulation's value is the sequence of gratings over time → a `sampled_body`
(`storage_mode: body`), NOT one inline grating. This is the substantive remaining build
(element-data → data_body construction for the stimulus timeline).

**Build:** (1) pass-1 defers `stimulus_presentation` with `needsSessionContext`;
(2) a second-pass resolver reads `stimuli.parameters` → `visual_grating` values (angle,
sFrequency→spatial_frequency, tFrequency→temporal_frequency, contrast, size, isblank→
is_blank), resolves the animal via the response link, wraps the timeline as a
`sampled_body`, and emits `visual_grating_manipulation` on the animal.
(`stimulus_bath` keeps its own `stimulusBathToBath` resolver.)

### DRAFT — the stimulus-timeline sampled_body datum layout
A presentation is an ordered list of stimulus EVENTS (`presentation_order` indexes into
`stimuli[]`; `presentation_time` gives per-event onset/offset). One body-backed
`visual_grating_manipulation` per presentation-epoch, on the animal:

- **`visual_grating_manipulation`** (the statement): `subject_id` = the animal;
  `time_reference_#` = an epoch anchor on the presentation's epoch; `storage_mode` =
  `body`; inline value blank (the data is in the body); `method` = "visual stimulus
  presentation"; `variable` = "visual grating".
- **`sampled_body`** (`statement` → that manipulation): a sample-per-TRIAL series.
    - **`sample_time`**: `regular = false`, **`offsets`** = the trial ONSET times (the
      array of sample times — the schema gap is now closed: `sample_time.offsets` is a
      matrix of explicit per-sample times), `n = N_trials`. So onset IS the sample time.
    - **`datum`**: kind = `record`, one record per trial = the trial's grating value
      (`angle, spatial_frequency, temporal_frequency, contrast, size, is_blank`) from
      `gratingValueFromParameters(stimuli(stimid).parameters)` + a `duration`
      (offset − onset). `stimid` DROPPED (redundant once params are expanded; keep only
      if a grouping key is wanted). shape = `[N_trials, n_fields]`.
    - `axes`: (none needed — the trial axis IS sample_time).
    - `content_hash`: hash of the payload.

RESOLVED: irregular event times → `sample_time.offsets` (the array of onsets). `stimid`
dropped. OPEN (architect):
  1. One body-backed manipulation per presentation with the full trial series (this
     draft), vs one `visual_grating_manipulation` per DISTINCT condition (param-only,
     inline, no body) — pivot on how you query it (trial-by-trial vs by-condition).
  2. Do `is_blank` control trials stay as rows, or get dropped?

**Blocker / decision needed — how to identify the co-recorded ANIMAL.**
`stimulus_presentation.element_id` is the STIMULATOR (its own subject is the stimulus
system, not the animal). Getting the animal needs epoch → co-recorded animal element →
`subjectOfElement`. But co-recorded elements almost certainly carry DIFFERENT epoch ids
linked by the **syncgraph** (`syncrule_mapping`), not a shared `epochid`. Options:
  - **(a) syncgraph traversal** — stimulator epoch → `syncrule_mapping` → the animal's
    epoch → the animal element → subject. Most correct; needs a new
    `bodyResolver.animalOfStimulusEpoch` built on the sync mappings. Heaviest.
  - **(b) session heuristic** — the animal subject(s) of the session (the elements that
    are NOT devices/stimulators). Simple; may be wrong when a session has >1 animal.
  - **(c) shared-epoch match** — only correct if co-recorded elements DO share an
    epochid; must be confirmed against the corpus first.
This is an architect's call + needs corpus validation; it gates the resolver.

## Item 2: distance_metadata → length_observation (Part B, TaskList #18)
Blocked additionally on the element-data → observation machinery (turning the distance
element's epoch timeseries into a body-backed `length_observation`). The endpoint
identities can only be resolved here (the pass-1 relation attempt failed — endpoint ids
don't resolve before the second pass). Defer until the element-data tier exists.

## Recommended sequence
1. CONFIRM the epoch model against the corpus: do co-recorded elements share an
   `epochid`, or are they syncgraph-linked? (Decides Item 1 option a/b/c.)
2. Extend `bodyResolver` with the chosen animal-resolution capability + a unit test.
3. Write the `stimulus_presentation` resolver sub-pass (sibling of `stimulusBathToBath`)
   + unit test; add the pass-1 `needsSessionContext` defer; corpus-validate.
4. Item 2 rides the element-data → observation tier (deferred).

## Do NOT
- Do NOT build a graph primitive (e.g. exact-`epochid` element matching) before the
  epoch model is confirmed — a wrong primitive silently resolves the wrong subject.
- Do NOT emit endpoint/subject relations whose ids can't be shown to resolve (the
  distance_metadata Part A lesson: it turned a non-gating quarantine into gating
  orphans).
