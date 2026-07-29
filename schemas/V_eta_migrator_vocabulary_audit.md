# V_eta — migrator vocabulary audit (Phase 2 evidence + decisions)

**Companion to `V_eta_ground_truth_plan.md`.** That file holds the plan and the phases; this
one holds the **per-class evidence and verdicts** for every migrator found reading field names
that no real did_v1 document has. Written before compaction — it is the durable record of a
long working session, so prefer it over re-deriving.

## The rule (restated, because everything below depends on it)

> The **current NDI-matlab templates read from `origin/main`** are the did_v1 source of truth,
> and where a template and its **WRITER** disagree, **the writer wins** — the data follows the
> writer. `schemas/V_alpha/` is history, not evidence. **Fixtures are built from the writer or
> the template, never from a DID-side schema.**

## Three failure modes (not one)

A migrator reading a field that does not exist fails in one of three ways. They need different
detection, which is why Phase 1 has more than one counter:

| mode | what happens | which counter sees it |
|---|---|---|
| **HOLLOW** | emits documents with blank/zero values | `did2.validate.silentLoss` — **only if** the blank is an empty struct or empty required edge. A numeric `0` is INVISIBLE to it. |
| **PASSTHROUGH** | read fails → `bodies = {preBody}` → never migrated | `summary.unconverted_by_class` |
| **FRAGMENT** | payload skipped, only side documents emitted (e.g. a lone session anchor) | **NOTHING SEES IT.** Not hollow (no blank required field), not a passthrough (output was produced). |

The FRAGMENT gap is real and unclosed. `simple_calc`, `fitcurve`, `vmspikefit` and
`vmneuralresponseresiduals` all failed this way — emitting only a `session_relative_reference`
anchor while dropping the entire payload.

## A correction that recurs — read this before trusting any brief

Three of six research agents independently claimed `element_id` is a dangling non-subject edge
and that classes carrying it must therefore defer. **That is wrong for this pipeline.**
`+migrators_j/element.m` promotes every `element` to a `subject` **with its id preserved**, so
`element_id → subject_id` resolves by design (device-as-subject, D2). Only the
`spike_clusters`/`spikewaves` brief got this right.

The real caveat is subtler and worth keeping: the subject reached is the **recording element**,
not the animal. The animal is one further hop via `element.subject_id`. Which one is wanted is a
modelling decision, not a defect.

---

## Verdicts — all 15 classes, evidence-backed

### FIXED (6)

| class | what was actually wrong | fix |
|---|---|---|
| `ontology_image` | read `region` — the **V_delta migrator's OUTPUT**, not a v1 field. `migrators_j` runs *instead of* the V_delta migrator, so it sees a `universalRenames`-only body. Two vintages exist; the legacy one is DID-INVENTED. | vintage split + guard; current NDI shape passes through |
| `fitcurve` | read `fit_function` + `goodness_of_fit`; real = `fit_equation` + `fit_sse`. **0 commits** in NDI history for the old names, 7 for the real ones. | rename + report SSE as a residual |
| `vmspikefit` | same, with `r_squared` | same |
| `simple_calc` | read `result_value`/`result_units`; real = `answer`/`input_parameters`. **No units field exists at all**, so unit-dispatch had nothing to dispatch on. **No subject edge** — only `document_id` → the input document. | guarded passthrough → second pass |
| `probe_geometry` | read `channel_positions`/`position_units`/`probe_type` — **not one name overlaps** the real class | one `length_observation` per populated axis |
| `electrode_offset_voltage` | read `offset_voltages`/`voltage_units`; real = `offset`/`temperature`, both **scalars** (one doc per CSV row, not a per-channel array) | scalar value; temperature as a `conditions` qualifier |

**Key semantic traps caught, and worth remembering as a class of error:**
- `fit_sse` is NOT `r²`: unbounded, units², and **lower is better**. Writing it into a 0..1
  "goodness" score would have **inverted polarity** on every downstream comparison.
- `electrode_offset_voltage.temperature` is a **qualifier** of the voltage measurement, not a
  second observation of the probe.
- `probe_geometry` is **three already-named parallel arrays**, so concatenating them into one
  anonymous array would discard naming the source gives for free.

### APPROVED FOR GUARDED PASSTHROUGH — 7, decided, NOT YET BUILT

The user approved: **stop fabricating, guard the invented shape so it errors, pass through for
the NDI second pass.**

| class | why pass 1 cannot do it honestly |
|---|---|
| `spike_clusters` | reads **0 of 1** real fields. Real = `epoch_info`, `clusterinfo`, `waveform_sample_times`. Payload is `spike_cluster.bin` **bytes**. |
| `spikewaves` | counts live in the `.vsw` **binary header**. Reads 1 of 3. |
| `spike_interface_sorting_outputs` | **`depends_on: []`** — no edges at all, so no subject exists to attach to. Counts are inside `sioutputs.zip`. |
| `site2channelmap` | real field `map` is never read; its meaning is **defined by the `probe_geometry` it references** — needs the join |
| `binnedspikeratevm` | **no writer exists in any repo we have**; payload is inline `"string"`-typed fields of unknown encoding |
| `vmneuralresponseresiduals` | same missing writer; `goodness_of_fit` has **no documented range or polarity** |
| `ontology_label` | see below — needs the graph to reach a referent |

**Counts are NOT derivable in pass 1.** They exist only as `numel()` of binary file contents,
and single-document migrators carry files without reading their bytes (the `pyraview`
precedent). Every `n = 0` currently emitted is a **fabricated measurement** that validates
cleanly and is invisible to both Phase 1 counters.

### `ontology_label` — BENIGN VERDICT REFUTED (the biggest single find)

Previously assessed benign because it reads the right *field*. It does. **The dependency is the
bug**, and it was never checked.

```
real template deps    : [{ name: document_id }]     schema: mustbenotempty: 1
migrator asks for     : {'element_id','subject_id','probe_id'}
jStartInteraction:38  : body.depends_on = jCarrySubject(...)   <-- OVERWRITES, not extends
```

`document_id` is not a candidate. So on every real document `subject_id` comes out **empty**
(declared `mustBeNonEmpty`, enforced nowhere) **and** the `document_id` edge — the only link to
the labelled thing — is **discarded**. The label value survives; its referent does not.

**~7,007 documents.** The coverage audit
(`ndi-next-steps/Summer 2026/1_Ingestion/V_eta_Migration_Field_Coverage_Audit.md:39`) marks it
✅ with "ontologyNode + document_id carried" — the `document_id` half is **not implemented**.
That audit was graded by reading migrator source, so **other ✅ rows may carry the same reading
error and need re-checking.**

**Decided target** (mine, agreed as "the correct way"): resolve through to the subject in the
**second pass** and keep the link to the labelled document.

```
ontologyLabel --document_id--> imageStack --migrates--> image_observation --subject_id--> subject
```

Emit a `term_observation` about that subject with `derived_from` → the migrated data statement.
Keeps both facts (the term, and what it was about) and asserts nothing false. Renaming
`document_id → subject_id` would claim an `imageStack` is a subject — it is not.

**Cheap confirmation available:** a corpus run's `silent_loss.empty_required_dependency` should
show ≈7,007 empty `subject_id` edges on `term_observation`.

### BENIGN — CONFIRMED (2)

- **`daqreader_ndr`** — reads the real `ndr_reader_string`; the `file_extension` branch is
  `isfield`-guarded and never fires. Caveat: the dropped `ndi_daqreader_ndr_class` is
  recoverable **only because the writer sets it identically to the parent field** — an
  empirical property, not a schema guarantee. Separately flags an NDI **read-path** break
  (`+daq/+reader/+mfdaq/ndr.m:41` reads the old path) — scheduling, not data loss.
- **`subject_group`** — structure survives; membership rides on numbered `subject_id` edges,
  read correctly. **But the stated reason was wrong:** nothing is lost because there was never a
  name or description — three writers construct it with **no property arguments at all**. What
  actually happens is `jEnsureLocalId` falls back to `base.id`, so every migrated group
  satisfies a field documented "Human-facing handle… REQUIRED" with a **raw UUID** (~353×).
  Not a loss; a required quality floor met with filler, invisible to the census because the
  field is non-empty.

---

## Open questions — NOT resolved

1. **Where is the `vhlab_voltage2firingrate` writer?** NDI-matlab has its 5 document templates
   and 5 schemas under `ndi_common/.../apps/vhlab_voltage2firingrate/` but **zero `.m` files,
   and never had any** (no add-commit in full history). `NDIcalc-ephys-matlab` was checked and
   does **not** have it (it contains exactly one `.m` file, `+ndi/+calc/+ephys/spike_shape.m`).
   Still unchecked: `vhlab-toolbox-matlab`, `NDIcalc-marder-matlab`, `NDIcalc-birren-matlab`.
   **Blocks:** `binnedspikeratevm` (its `Hz` unit is hardcoded, but binned rates are commonly
   spikes-per-bin — at `binsize=0.030` that is a silent **33× error**) and
   `vmneuralresponseresiduals`.

2. **The 102-class v1 universe may be drawn too small.** `coverage.py` counts 91 NDI templates
   + 11 vhlab app classes from `NDIcalc-vis-matlab` only, and reports **0 gaps**. But
   `NDIcalc-ephys-matlab` ships `spike_shape_calc` — a real class with a real writer — that is
   **absent from the ledger entirely** and has no migrator. It is not a gap *in* the ledger; it
   is *outside* it. `NDIcalc-birren-matlab` and `NDIcalc-marder-matlab` plausibly add more
   (`electrode_offset_voltage`'s writer is Marder-lab code). **Every coverage claim rests on
   this count.** User's call: "keep it as is for now."

3. **The FRAGMENT detection gap** (see the table at the top) — no counter sees a migrator that
   emits only its side documents.

4. **Recording element vs animal** as the subject reached via `element_id` — a live modelling
   choice for every spike/waveform class.

## CI / state at time of writing

- Fast gate green on `d04e7e1`, `7dd8b2f`, `86a9c08`, `3894c59`; `e863c1a` was in flight.
- Full corpus **run #252** on DID-matlab `cebb0ab` — **predates all migrator fixes**, so its
  per-class numbers describe the OLD behaviour. Useful for the id-preservation check, the
  hollow census, and the `ontology_label` prediction above; **not** a Phase 2 ranking.
- Repos added to session scope this session: `VH-Lab/NDIcalc-vis-matlab` (@`65718ed`),
  `VH-Lab/NDIcalc-ephys-matlab` (@`e9724a5`). **Both clones are ephemeral** — re-add to re-check.
