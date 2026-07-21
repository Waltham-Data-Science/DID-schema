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

## Item 1: stimulus_presentation → a body-backed subject_manipulation leaf
DECISION (architect): a `stimulus_presentation` becomes a **body-backed
`subject_manipulation` leaf** on the ANIMAL. The stimulus's time-varying data is a
`data_body` (`storage_mode: body` + a `sampled_body` holding the waveform); the
statement itself is one of the EXISTING typed `subject_manipulation` leaves
(`current_`, `voltage_`, `intensity_`, `frequency_`, …) — there is NO
`stimulus_manipulation` class. The LEAF is chosen by the stimulus's data type (an
electrical stimulus → `current_`/`voltage_manipulation`; a luminance/contrast stimulus
→ `intensity_manipulation`; etc.). Needs the second pass for two reasons:
  - **subject** = the animal stimulated, resolved via the recording graph (the
    presentation only names the stimulator element).
  - **body** = the stimulus data → `sampled_body` (the element-data → data_body
    machinery).
OPEN: the stimulus-type → manipulation-leaf mapping (fixed table? read from
`stimuli.parameters`?). (`stimulus_bath` stays its own `stimulusBathToBath` resolver.)

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
