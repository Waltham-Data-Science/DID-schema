# V_eta — raw recordings as typed observations (SIGNED 2026-08-10)

*Decided in the audit walkthrough (the "voltage-attribution gap"). **FINAL; build deferred**
— batched. Cross-refs: `V_eta_tenets.md` (T3 direction×data_type, T6 storage, T7 instrument
vs. subject). Subject to the fresh-eyes re-audit like every other decision.*

## The gap this closes

Tracing a probe's extracellular recording through the current migrators showed the raw signal
is migrated as **loose device-attached pieces**, never assembled into a typed observation:
- `element.m`: the probe → a `subject` + kind assertions + a `probe observes specimen`
  `directed_relation`.
- `element_epoch.m`: the epoch timing → an `acquisition_epoch` doc.
- data-body collapse (#7): the raw samples → a bare `sampled_body`.

No migrator produces a `voltage_observation` (a `subject_observation` of the specimen with
`instrument_id → electrode`, `variable = voltage`). So the modality/units typing is dropped
and the instrument role is only a loose `observes` relation — contradicting T7 (patient =
`subject_id`, agent = `instrument_id`).

## Decision (final): a raw recording IS a typed observation of the specimen

A raw continuous recording becomes a **`<modality>_observation`** = `subject_observation` +
the modality data_type:
- **`subject_id` = the specimen** (the slice/animal — v1's `element.subject_id`; faithful).
- **`instrument_id` = the recording device** (the electrode/probe — still its own subject per
  T1/D2, referenced here in the instrument role, T7).
- **`variable` = the modality** (voltage / current / image / …), derived from the element/probe
  type. The general rule: *the recording is a `<modality>_observation`*; `voltage_observation`
  is the extracellular-electrode case.
- **body = `sampled_body`** (self-describing samples; `reference` if the recording is huge —
  storage_mode is orthogonal, T6).
- **timing** = the `acquisition_epoch` / `time_reference` anchor (unchanged).
- **the `probe observes specimen` relation is REPLACED by the `instrument_id` edge** — one
  coherent statement instead of a loose relation + an orphan body. (The electrode-subject and
  its kind assertions stay; only the redundant `observes` relation retires.)

This makes raw recordings first-class, typed, queryable ("all `voltage_observation`s of
specimen S, taken with electrode E"), and captures modality/units that the bare-body path lost.

## Consequences / open sub-points (for the build + re-audit)

- **Modality→variable mapping + the unknown-modality guard (Guard A — DECIDED).** A map from
  element/probe `type` (or `ndi_element_class`) to the modality data_type
  (voltage/current/image/…) drives the typed leaf. **Never mint a `timeseries_observation` /
  `signal_observation` class** (T11-banned words). For an element type NOT in the map, the
  recording is STILL a valued observation — its value is a **bare self-describing
  `sampled_body`** (`dtype`/`axes` on the body; no dimensioned data_type, since `array` is
  killed) with `variable` carrying the best-known label + a **queryable `modality_unresolved`
  flag**; re-type to the specific `<modality>_observation` when the modality is identified.
  **So there are NO untyped docs** (the body is self-describing and the observation is valued),
  and unresolved-modality is a *tracked, terminal* state, not a ragged edge:
  1. Populate the map for **every element type present in the corpus** (a finite, enumerable
     set) → the bare-body fallback is a safety net, not the normal path.
  2. **Build gate: 0 fallbacks.** On the real corpus, assert **zero recordings fell to the
     bare-body fallback** (same discipline as the 0-orphan gate). Any that did ⇒ the map is
     incomplete ⇒ add the type ⇒ re-migrate. Drives the count to zero.
  3. The bare-body fallback + `modality_unresolved` flag then only ever catch *unexpected future*
     element types — surfaced as a queryable worklist, resolved by extending the map (+ re-run)
     or in the NDI second pass (element/instrument graph), never silently.
- **Multi-channel (DECIDED).** A multi-channel recording (e.g. a 32-site probe) is **ONE**
  observation whose `sampled_body` carries a **channel axis** (a dimension + per-channel labels,
  T6) — not N per-channel observations. Path-S (below) can split into per-site part-subjects
  later only if a real need arises.
- **Specimen granularity (T5/Path-S).** Attributing to the whole specimen is faithful to v1
  but coarse (a probe records a *locus*, not the whole animal). Path-S can later promote a
  recording-locus part-subject if a real query need arises; not now.
- **Relationship to derived features.** Spikes/tuning remain `derived_from` this recording
  observation (or its subject) — the derived-tier folds (neuron_extracellular, calculators)
  are unaffected except that their provenance now points at a typed observation.
- **`neuron_extracellular` lineage.** Currently `derived_from` the recording element-subject;
  `part_of` the specimen is left to curation. Unchanged by this decision, but flagged: the
  re-audit should check whether the neuron→specimen `part_of` (Path-S) should be minted.

## Deferred build tasks (the batch)

1. **Recording-observation assembler.** A migrator step that, for a direct recording element,
   emits a `<modality>_observation`: `subject_id`=specimen, `instrument_id`=element-subject,
   `variable`=modality (via the map), body=the `sampled_body` (multi-channel → a channel axis
   on the body), timing=the acquisition epoch. Retire the redundant `observes` relation for
   direct devices. (Also handles spike-train elements → the per-neuron spike-time bodies the
   ensemble model depends on.)
2. **Modality map** (element type → modality data_type) covering every element type in the
   corpus; the **bare self-describing `sampled_body` fallback + `modality_unresolved` flag**
   (Guard A) for anything else; **NEVER** a `timeseries_observation` or generic `array` class.
3. **Fixtures/tests**: an extracellular `voltage_observation` (specimen subject, electrode
   instrument, voltage variable, multi-channel sampled_body); a multi-channel body with a
   channel axis; a bare-body fallback case (assert the observation is valued by a
   self-describing sampled_body, `modality_unresolved` flagged, no `timeseries_observation`/
   `array` class minted); assert the `observes` relation is gone and the body is wrapped.
4. **Corpus re-verify**: the reshape must stay 0-orphan (the sampled_body's referrers now
   resolve through the observation; ids preserved where they were) **AND 0 bare-body fallbacks**
   (the map covers every corpus element type).

---

## SIGNED OFF 2026-08-10

TEAM-SIGN-OFF [raw recording observation]: jess@walthamdatascience.com / 2026-08-10 -- a raw continuous recording IS a typed `<modality>_observation` of the SPECIMEN: `subject_id` = the specimen, `instrument_id` = the electrode/probe in the instrument role (T7), `variable` = the modality from the element/probe type, body = `sampled_body`, timing = the existing epoch anchor; the loose `probe observes specimen` relation RETIRES in favour of the `instrument_id` edge. Guard A stands: an unmapped element type still yields a VALUED observation over a bare self-describing `sampled_body` with a queryable `modality_unresolved` flag -- never a `timeseries_observation` or `array` class -- and the build gate is ZERO fallbacks on the real corpus. Multi-channel is ONE observation with a channel axis, not N observations. Specimen granularity is accepted as faithful-but-coarse; Path-S may promote a recording-locus part-subject later. Signed KNOWING the body shape rides on the data_body model, which is NOT signed: the `sampled_body` under these observations will be reshaped when that lands, and that rework is accepted rather than waiting on binding enforcement plus two corpus measurements.

> **Tagged `[raw recording observation]` deliberately.** No decision family in `status_board.py` cites this document today, so an untagged marker would sign nothing else -- but the tag is cheap and the untagged-marker hole has bitten this project before.

> **SIXTH TRANSCRIPTION.** Claude wrote this line on explicit instruction ("Sign #30, don't sign #45"), 2026-08-10. The standing request that the team type these itself is now four sittings old.
