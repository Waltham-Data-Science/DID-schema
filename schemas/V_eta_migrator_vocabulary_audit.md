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

### GUARDED PASSTHROUGH — 7, BUILT

Decided as: **stop fabricating, guard the invented shape so it errors, pass through for the NDI
second pass.** Now built — migrators, V_eta tombstones, unit tests and fixture-corpus fixtures.

| class | why pass 1 cannot do it honestly |
|---|---|
| `spike_clusters` | reads **0 of 3** real fields. Real = `epoch_info`, `clusterinfo`, `waveform_sample_times`. Payload is `spike_cluster.bin` **bytes**. |
| `spikewaves` | counts live in the `.vsw` **binary header**. Reads 1 of 1 real field; both counts were invented. |
| `spike_interface_sorting_outputs` | **`depends_on: []`** — no edges at all, so no subject exists to attach to. Counts are inside `sioutputs.zip`. |
| `site2channelmap` | real field `map` is never read; its meaning is **defined by the `probe_geometry` it references** — needs the join |
| `binnedspikeratevm` | **no writer exists in any repo we have**; payload is inline `"string"`-typed fields of unknown encoding |
| `vmneuralresponseresiduals` | same missing writer; `goodness_of_fit` has **no documented range or polarity** |
| `ontology_label` | see below — needs the graph to reach a referent |

**The tombstones were wrong too, and that was nearly a silent gate failure.** All 7 V_eta
source tombstones had themselves been written from the V_alpha snapshot — every declared field
was invented (`num_spikes`, `num_units`, `site_to_channel`, `mean_residual`,
`ontology_label.term`, …). The validator is strict in **both** directions:

- `did2:validation:undeclaredField` rejects any block field the schema does not declare;
- `mustBeNonEmpty` rejects a declared field the real document does not carry.

So passing a real document through would have **quarantined it against our own schema**. All 7
tombstones are now restated from the NDI `origin/main` template + `schema_documents` pair
(names from the template, types and required deps from the schema). This is the same repair
`simple_calc` got, and it is a standing hazard for any future deferral: *a passthrough is only
safe if the tombstone describes the real document.*

Two source disagreements surfaced and are recorded rather than resolved:

- `binnedspikeratevm`'s first dependency is `vmspikefilteringparameters_id` in the template and
  `sorting_parameters_id` in the schema. No writer to arbitrate → both declared optional.
- `vmneuralresponseresiduals.goodness_of_fit` is typed `["number", "string"]`. DID's
  meta-schema has **no union type**; declared `string` (the type the template's own value has),
  with the union recorded in the field documentation.

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

### THE "MENTIONS ONLY" BUCKET WAS NEVER CHECKED — 2 more offenders, 1 false positive

The detector splits its hits into names read through a recognised idiom (tier 1) and names that
merely *occur* in the source (tier 2). The 15 above were all tier 1. **Tier 2 was taken on trust,
and it was hiding real defects.**

| class | verdict |
|---|---|
| `vmspikesummary` | **16th offender.** Reads `mean_vm`, `mean_firing_rate`, `num_spikes`, `recording_duration`. The real class is a **mean spike waveform + eight spike-shape medians** — `mean_spikewave`, `sample_times`, `number_of_spikes`, `median_spikekink_vm`, `median_voltageofhalfmaximum`, `median_fullwidthhalfmaximum`, `median_presk_halfwidthmaximum`, `median_postsk_halfwidthmaximum`, `median_max_dvdt`, `median_kink_index`, `slope_criterion`. It was modelling a **different document than the one that exists**. → guarded passthrough |
| `vmspikefilteringparameters` | **17th, and the worst-hidden: it has NO MIGRATOR**, so it passes through by default — into a tombstone declaring `filter_type`/`filter_window`, neither of which exists. Real: `sampling_rate`, `new_sampling_rate`, `threshold`, `spiketimes`, `filter_algorithm`, `filter_algorithm_parameters[]`, `rm60Hz`, `refract`. → correct tombstone, **no migrator needed** |
| `neuron_extracellular` | **FALSE POSITIVE, confirmed clean.** Reads the real `cluster_index` and `quality_number`; the `quality` hit is a local MATLAB variable name. Tombstone matched the template already. Only fix: its `spike_clusters_id` dependency was undeclared. |

`num_spikes` → `number_of_spikes` looks like a near-miss rename, but **correcting the name would
still not have worked**: the real field is an **array**, and the migrator required `isscalar`.

**Why three broken classes never tripped a gate.** All five `vhlab_voltage2firingrate` classes
are template-and-schema only, with **no writer in any repository** — so almost certainly **no
corpus holds a single document of any of them**. This is latent risk, not active loss, and it is
the clearest evidence in this whole audit that *"the corpus is green" cannot substitute for
reading the source.*

**The detector defect is fixed** (`tools/ndi_ground_truth.py`). Tier 1 now also recognises:
- reads through a **local accessor helper** (a same-file function whose body uses `isfield` or
  dynamic field access) — several migrators define their own `getField`, and those reads were
  invisible;
- **unresolvable dispatch**: when an accessor is called with a cell-table lookup like
  `getField(blk, spec{k,1})`, the names live in a literal table no call-site pattern can follow,
  so every quoted candidate in the file is treated as read. Under-reporting here is precisely
  what let a whole class be modelled against fields that do not exist.

That moved `vmspikesummary` and `subject_group` from tier 2 to tier 1, and left
`neuron_extracellular` and `treatment_drug` in tier 2 — both already confirmed false positives.

**A blind spot that remains, recorded so it is not mistaken for coverage:** a class with **no
migrator** never appears in this tool's report at all, because there is no source file to scan.
That is how `vmspikefilteringparameters` stayed invisible; it was found by reading the app's
templates. Coverage of unmigrated passthrough classes belongs to `tools/coverage.py`.

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

## Loss modes the vocabulary checker STRUCTURALLY CANNOT SEE

This tool looks for migrators READING field names that no document has. Three defects found
since fall outside that definition while sharing its root cause — an artifact written from
DID-schema's `V_alpha` snapshot instead of from NDI. The checker is not broken; its scope was
narrower than the problem.

1. **A migrator DELETING real data on a false premise.**
   `+migrators_j/daqreader_mfdaq_epochdata_ingested.m` ends with
   `if isfield(v2Body,'epochid'); v2Body = rmfield(v2Body,'epochid'); end`, commented
   *"the epoch link is the epochid dep"*. **There is no `epochid` dependency in did_v1** — all
   three NDI templates declare only `daqreader_id`, and `epochid` is a SUPERCLASS block holding
   the epoch-id string. So it deletes the only record of which epoch the bytes belong to, and
   the document still validates. Traced to ⑥/⑦ walkthrough chunk (b), decided from the DID-side
   schema rather than the NDI template; corrected in `V_eta_6_7_walkthrough_STATE.md`.

2. **A migrator DESTROYING the source id on its success path.**
   `+migrators_j/fitcurve.m` mints `did.ido.unique_id()` for its observation instead of
   preserving `base.id` via `jStartInteraction`, as its three sibling migrators do. Anything
   referring to a `fitcurve` document dangles. This is the id-preservation rule that cost 11,448
   orphans, broken again in one place.

3. **A coverage document asserting a conclusion from absent evidence.**
   `tools/coverage.py` labelled every class with no V_eta home "dissolved (rename/decompose)" —
   32 rows — which read as accounted-for. Split by whether a migrator actually consumes the
   class, only 28 are; the rest had nowhere to go. `_PRE_ZETA_DISSOLVED` also carried a FALSE
   claim that `subjectmeasurement` dissolved into `measurement` (NDI never did; it has four live
   emitters). Fixed; the ledger now reports 1 UNMAPPED + 4 UNVERIFIED instead of 0 gaps.

**The generalisation worth keeping:** a checker that asks "does this read a name that exists?"
cannot catch a wrong DELETE, a discarded id, or a document that lies about coverage. Each needed
its own check, and each was found by reading source rather than by any gate.

## Open questions — NOT resolved

1. **The `vhlab_voltage2firingrate` writer does not exist — SEARCH CLOSED.** NDI-matlab has its
   5 document templates and 5 schemas under `ndi_common/.../apps/vhlab_voltage2firingrate/` but
   **zero `.m` files, and never had any** (no add-commit in full history). Every candidate
   repository has now been cloned and searched:

   | repo | ref | has the writer? |
   |---|---|---|
   | `NDIcalc-vis-matlab` | `65718ed` | no |
   | `NDIcalc-ephys-matlab` | `e9724a5` | no — exactly one `.m` file, `+ndi/+calc/+ephys/spike_shape.m` |
   | `NDIcalc-marder-matlab` | `dac67c7` | no |
   | `NDIcalc-birren-matlab` | `9d1b4d0` | no |
   | `vhlab-toolbox-matlab` | `0bccce1` | no |

   So the deferral of `binnedspikeratevm` and `vmneuralresponseresiduals` is **permanent until a
   writer or a real corpus document turns up** — it is not waiting on more searching. What stays
   undecidable: whether the binned values are rates or spikes-per-bin (the old code hardcoded
   `Hz`; at `binsize = 0.030` those differ by **33×**), the encoding of the `"string"`-typed
   payload fields, and the range/polarity of `goodness_of_fit`.

2. **The 102-class v1 universe is drawn too small — now with four more instances.**
   `coverage.py` counts 91 NDI templates + 11 vhlab app classes from `NDIcalc-vis-matlab` only,
   and reports **0 gaps**. The clone sweep above found document classes with real templates,
   real schemas and (mostly) real writers that are **absent from the ledger entirely** — not
   gaps *in* it, but *outside* it:

   | class | repo |
   |---|---|
   | `spike_shape_calc` | NDIcalc-ephys |
   | `ppg_beats` | NDIcalc-marder (`ndi_common/database_documents/heart/`) |
   | `spectrogram` | NDIcalc-marder |
   | `currentfrequency_FIcurves_calc` | NDIcalc-birren (`ndi_common/database_documents/calc/`) |

   Birren also ships two schema-only entries with no matching template
   (`naka_rushton_thresh_fit`, `currentFrequency_nakaRushton_calc`) — possibly stale, not
   verified. **Every coverage claim rests on the 102 count.** User's call: "keep it as is for
   now."

3. **The FRAGMENT detection gap** (see the table at the top) — no counter sees a migrator that
   emits only its side documents.

4. **Recording element vs animal** as the subject reached via `element_id` — a live modelling
   choice for every spike/waveform class.

## CI / state at time of writing

- Fast gate green on `d04e7e1`, `7dd8b2f`, `86a9c08`, `3894c59`; `e863c1a` was in flight.
- Full corpus **run #252** on DID-matlab `cebb0ab` — **predates all migrator fixes**, so its
  per-class numbers describe the OLD behaviour. Useful for the id-preservation check, the
  hollow census, and the `ontology_label` prediction above; **not** a Phase 2 ranking.
- Repos added to session scope this session: `NDIcalc-vis-matlab` (@`65718ed`),
  `NDIcalc-ephys-matlab` (@`e9724a5`), `NDIcalc-marder-matlab` (@`dac67c7`),
  `NDIcalc-birren-matlab` (@`9d1b4d0`), `vhlab-toolbox-matlab` (@`0bccce1`), all under `VH-Lab`.
  **All clones are ephemeral** — re-add to re-check.
- `tools/check_migrator_vocabulary.py` now distinguishes a migrator that CONSUMES an invented
  name from one where the name survives only inside a rejection guard (the detector cannot tell
  `isfield` apart, so the split is a hand-maintained list). The report went **15 offenders → 1**
  — `daqreader_ndr`, whose `file_extension` branch is confirmed unreachable dead code. It also
  now flags a guard that has DISAPPEARED, so deleting one later reads as a regression rather
  than as progress.
