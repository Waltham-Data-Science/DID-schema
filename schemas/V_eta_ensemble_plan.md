# V_eta — the `ensemble` model (DECIDED; build deferred)

*Worked design for how V_eta represents a neuron ensemble, decided in the audit-walkthrough
revisit (the user reopened the whole class + its name). **All decisions below are FINAL; the
BUILD is deferred** — batched with the other walkthrough decisions. This SUPERSEDES the
earlier "grain A — carry the map doc as ⑦ acquisition-infra" decision. Cross-refs:
`V_eta_tenets.md` (T1 group-ness, T6 storage, T10 derived motif, T12 parsimony),
`V_eta_tenet_audit.md` (boundary classes).*

TEAM-SIGN-OFF [ensemble]: jess, 2026-08-06 -- per-neuron spike times are the PRIMARY archival data (each neuron-subject, event times to a sampled_body); the ensemble is a GROUP SUBJECT with its id preserved and NO data body of its own, whose members are EPOCH-SCOPED member_of edges carrying their epoch and column order; the combined (times, ids) array is kept as an explicitly-DERIVED, REBUILDABLE CACHE (derived_from the neurons, T10) for fast windowed population reads, not as source of truth; the per-epoch MAP document dissolves. Build is sequenced: pass 1 keeps a green passthrough, the NDI second pass mints member_of and builds the cache, and a verify-before-delete (0 stranded per-neuron trains) gates dropping the combined bytes.

*(Transcribed by Claude on the team's explicit instruction -- "I agree ensemble is decided and can be signed off". TAGGED with its family, per the shared-document rule.)*

## What an ensemble actually is (plain)

An electrode picks up the electrical "spikes" of several nearby neurons, all mixed together.
Spike-sorting untangles them into individual **neurons**, each with its own list of firing
times. An **ensemble** is just those neurons **bundled into one who-fired-it-labeled stream**
— a *marked point process*: every spike from all the neurons, in time order, each tagged with
which neuron fired it. NDI builds it by *reading the already-sorted neurons and re-packing
their spikes* (`ndi.fun.ensemble.create` → `ndi.fun.ensemble.load`). So the per-neuron trains
are the source; the combined stream is a derived re-packaging.

The v1 `ensemble` name covers TWO things: (1) the ensemble ELEMENT (the combined stream, an
`ndi.element.timeseries`), and (2) a per-epoch MAP document (the column→neuron legend). This
plan resolves both.

## The core decision: store per-neuron; the group is membership; the combined stream is a cache

The per-neuron form and the combined (times, ids) form are **losslessly inter-convertible**
(merge-with-labels one way, group-by-id the other) — neither holds a bit the other lacks. So
you never need both as source-of-truth; storing both would be duplication (T12). Decision:

1. **Per-neuron spike times = the PRIMARY archival data.** Each neuron is its own subject
   (element→subject, id preserved, Path-S); each carries its spike-time record as a
   `sampled_body` of event times (a spike-time `subject_observation` of that neuron). This is
   the source of truth (it is what sorting produces) and the finest grain.

2. **The ensemble is a GROUP SUBJECT** — kept (id PRESERVED, so any doc that references the
   ensemble by id still resolves), but it **carries no primary data body of its own**. Its
   membership is expressed by **EPOCH-SCOPED** `member_of` `directed_relation`s from each
   constituent neuron-subject to the ensemble-subject (T1: "group-ness comes from incoming
   `member_of` edges"; T4: relations are documents). **Each `member_of` edge carries the epoch
   it holds in** — because the recorded neuron set *changes epoch-to-epoch* (`ensemble.m`:
   "the set of recorded neurons may change from epoch to epoch"). The per-epoch roster is
   therefore the set of `member_of` edges for that epoch (durable, graph-native), NOT something
   that lives only in the cache. Joint activity is *projected* from the members on demand.

3. **The combined marked-point-process = an explicitly-DERIVED CACHE** (INCLUDED — user
   request). Materialize the (time, neuron) stream as a `sampled_body` attached to the
   ensemble group-subject, so windowed *population* reads ("what was the whole group doing in
   [t0,t1]?") stay fast — this is exactly why NDI keeps the binary. Properties:
   - **`derived_from` the member neuron-subjects** (T10 derived motif; provenance explicit).
   - **marked as a rebuildable cache, NOT source of truth** — carries the T6 **`is_cache`**
     marker (+ `derived_from`); it can be regenerated from the per-neuron trains at any time;
     deleting it loses nothing. (Satisfies the T6 cache-warrant test: lossless, real
     population-read need, marked+regenerable, reason recorded here.)
   - **self-identifying**: the cache stores neuron-**subject ids** (or carries its own inline
     column→id ordering as part of the cache body), so it needs no external legend document.

4. **The per-epoch MAP / legend document DISSOLVES INTO the epoch-scoped `member_of` edges.**
   Column indices exist only to read the combined binary; once each train is attached to its
   neuron-subject id, the standalone "column 1 = neuron_A" legend is unnecessary **as a
   document** — but its content (which neurons, this epoch, in column order) is **preserved
   durably as the epoch-scoped `member_of` edges** (decision 2), with column order carried on
   the edges (or the cache's inline ordering). So "dissolves" = re-expressed as edges, **not
   discarded** — per-epoch membership survives even if the cache is deleted. `num_neurons` is
   derivable (count the epoch's members) — dropped (T11). `value_type`/`value_description`
   container fields collapse into the spike-time observation's `variable`/description. The
   stray `app` superclass is dropped (R1).

## Naming (revisit outcome)

- **The group concept keeps `ensemble`** — it is an established systems-neuroscience term for
  "the neurons co-recorded together." (`population` was the neutral alternative; not adopted.)
  The ensemble group-subject's kind is a `term_assertion` (`ensemble` / neuron-group term).
  Renaming the NDI element type is cross-repo (NDI-written) and out of scope here.
- **The map/legend document is NOT named `ensemble`** — it is *dissolved* (decision 4), so the
  "two things named ensemble" collision is removed by construction rather than by renaming.

## Why this over the alternatives (recorded per T12)

- **Storing the combined stream as PRIMARY (old NDI-literal model):** rejected as source of
  truth — it duplicates the per-neuron data and forces the column-index legend. Kept only as a
  derived cache (decision 3).
- **`count_observation` fold (old option C):** rejected — loses *which* neurons compose the
  ensemble; membership is the scientifically meaningful part.
- **Carry the map doc as ⑦ acquisition-infra (old grain A):** SUPERSEDED — it left the roster
  opaque in a file and modeled a derived group as plumbing. The membership + cache model is
  tenet-clean (T1/T6/T12) and dissolves the awkward doc.

## Migration constraints (build conditions — respect these)

1. ~~**`member_of` edges need the second pass.** The neuron ids live inside
   `neuron_names.txt`; single-doc migrators carry files but do NOT read their contents
   (confirmed — `pyraview` reads the *file list*, not the bytes), and the ids must resolve to
   migrated neuron-subjects. So minting `member_of` (and building the cache with resolved ids)
   is the **NDI second pass** (like `resolveStimulusPresentations` / Path-S), which has the
   element graph + file access.~~

   **WRONG PREMISE, CORRECTED 2026-08-10 with positive evidence. The neuron ids are NOT only
   inside the file — they are `depends_on` EDGES on the ensemble document itself.**

   ```
   src/ndi/+ndi/+element/ensemble.m:274-276      (the loop directly below element_epoch_id)
       for i = 1:numel(neuron_ids)
           mapdoc = mapdoc.add_dependency_value_n('neuron_id', neuron_ids{i});
       end

   ndi_common/schema_documents/ensemble/ensemble_schema.json:7
       { "name": "neuron_id", "mustbenotempty": 0}
   ```

   So `neuron_id_1..n` carry the neuron document IDS, in the same loop order that writes the
   names — `neuron_names.txt` carries the NAMES of the same roster, not the roster itself.
   A pass-1 single-document migrator reads `depends_on`; that is what every migrator already
   does. **`member_of` does not need file bytes and does not need the second pass.**

   The id-resolution half also holds without a second pass, for the reason the calculator fold
   turned on: `migrators_j.element` promotes an element to a subject with its **id PRESERVED**,
   so a `neuron_id_#` pointing at a neuron element resolves to the same id afterwards, and
   `must_refer_to_document_class` is existence-only.

   **WHY THE PREMISE SURVIVED: `ensemble.json`, the TEMPLATE, does not declare `neuron_id` —
   only the SCHEMA and the WRITER do.** A check against the template alone sees `element_id`
   and `element_epoch_id` and nothing more. This is the ground-truth rule doing exactly what
   it exists for (*where template and WRITER disagree, the WRITER wins*), on a divergence
   inside NDI's own pair rather than between NDI and V_eta.

   **What still needs the second pass** is narrower than this item claimed: the per-epoch
   **column order** of the cache (if it cannot be taken from the `neuron_id_#` index — check
   before assuming it cannot) and the verify-before-delete gate in item 3.
2. **Pass-1 landing:** carry the v1 `ensemble` element → group-subject (id preserved, via the
   element migrator) and its combined binary as-is, green, no orphans. The second pass then
   (a) mints `member_of` from each neuron-subject, (b) re-labels the combined binary as the
   derived cache (`derived_from` the members), and (c) drops the map/legend document.
3. **Verify-before-delete.** Dropping the map document and treating the combined binary as a
   disposable cache assumes every ensemble's per-neuron trains are present in the corpus (each
   neuron is its own 'spikes' element with its own data — they should be). VERIFY on a real
   corpus (0 stranded neuron trains) before deleting any stored bytes; this is a data-loss
   gate, not an assumption.

## Deferred build tasks (the batch)

1. **Per-neuron spike-time observation** shape (event times → `sampled_body`) on each
   neuron-subject — confirm the element migrator already lands this for 'spikes' elements; if
   not, add it.
2. **Ensemble group-subject**: keep the element→subject fold (id preserved); add the `ensemble`
   kind `term_assertion`; remove any primary data body.
3. **Second pass** (`ndi.migrate` / NDI-matlab): read `neuron_names.txt` **per epoch**, resolve
   neuron ids → subjects, mint **epoch-scoped** `member_of` edges (carrying the epoch + column
   order), materialize the derived cache (`sampled_body` + `derived_from` + `is_cache`), and
   dissolve the map/legend document into those edges (per-epoch roster preserved as edges).
4. **Verify-before-delete gate** on the corpus (0 stranded per-neuron trains).
5. **Retire the v1 `ensemble` MAP class** from the persist set once the second pass lands
   (until then it stays a green passthrough — do NOT phase-8-delete early).

---

## Deferred build task 1 WAS CONFIRMED, 2026-08-17, and the answer is NO — with the source class now named

Task 1 above asks to *"confirm the element migrator already lands this for
'spikes' elements; if not, add it."* The confirmation ran. **It does not, and
until today nothing in this document said WHERE the spike trains currently
live.** They live in `element_epoch`, and that is the join neither this plan nor
`V_eta_epoch_plan.md` was carrying.

        DENOMINATOR: 1220 json file(s) read from corpus 20211116
          element_epoch                      252
          distinct element_id targets         21   (12 documents each, exact)
          of those 21, direct=false           21   all type='spikes',
                                                   ndi_element_class='ndi.neuron'
          the .vhsb payload                  252   one per (neuron, epoch)

So this plan's *"each carries its spike-time record as a `sampled_body` of event
times"* has a concrete, counted source: **21 neuron-subjects × 12 epochs = 252
bodies**, sitting today on `acquisition_epoch` (the class `element_epoch`
migrates to 1:1).

**WHY THE MIGRATOR DOES NOT LAND IT, in two facts rather than one.** The first is
the one this plan would have predicted; the second is not.

  1. `jRecordingObservation` is called from `+migrators_j/element.m:118` behind
     `if isDirect`, and the file says why at `:111-113` — *"spike trains ride
     with the ensemble model and its NDI second pass, not here"*. So a derived
     element gets no observation at all.
  2. **`'spikes'` is not in the modality map**, so even reversing that gate would
     emit nothing: `grep -n "spikes"` over
     `+migrators_j/private/jRecordingModality.m` returns ONE hit, a comment at
     `:157`. The key falls to `otherwise` → `disposition = 'unresolved'` →
     Guard A.

**THE ROUTE IS NOW DECIDED AND THE SIGNATURE IS IN THE OTHER DOCUMENT** —
`V_eta_epoch_plan.md`, "AMENDMENT 1 to the #60 scoping walkthrough",
`TEAM-SIGN-OFF [epoch]` 2026-08-17: the 252 attach to the neuron-subject's
spike-time observation per THIS plan's 2026-08-06 signature, not to a
raw-recording observation, and `acquisition_epoch` stays the carrier until the
second pass lands. Recorded here as a cross-reference so a reader who arrives at
task 1 from this side finds it; the signature is deliberately NOT duplicated,
because two copies of one decision agree by coincidence until something checks
them.

**WHAT TASK 1 STILL CANNOT BE BUILT AGAINST, and it is a class that does not
exist.** This plan names the host as *"a spike-time `subject_observation` of that
neuron"*. `subject_observation` is ABSTRACT — `+did2/+schema/cache.m` raises
`did2:validation:abstractInstantiation` for any document naming it — and of the
33 concrete `*_observation` classes (`DENOMINATOR: 249 json file(s) under
schemas/V_eta/ read`) **none carries event times**. `count_observation` is the
neighbour, used by `jrclust_clusters` for its integer label series, but a spike
TIME is not a count. Open work, `V_eta_OPEN_WORK.md` row #117.

**AND ONE CONSTRAINT ON WHATEVER IS BUILT:** `element_epoch`'s `.vhsb` is a
GENERIC `(timepoints, datapoints)` series — `+ndi/+element/timeseries.m:274`
writes both, for any derived element type — so the fold must key on element
`type`, not assume spikes.
