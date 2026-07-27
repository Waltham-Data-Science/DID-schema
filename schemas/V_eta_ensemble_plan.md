# V_eta — the `ensemble` model (DECIDED; build deferred)

*Worked design for how V_eta represents a neuron ensemble, decided in the audit-walkthrough
revisit (the user reopened the whole class + its name). **All decisions below are FINAL; the
BUILD is deferred** — batched with the other walkthrough decisions. This SUPERSEDES the
earlier "grain A — carry the map doc as ⑦ acquisition-infra" decision. Cross-refs:
`V_eta_tenets.md` (T1 group-ness, T6 storage, T10 derived motif, T12 parsimony),
`V_eta_tenet_audit.md` (boundary classes).*

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
   membership is expressed by `member_of` `directed_relation`s from each constituent
   neuron-subject to the ensemble-subject (T1: "group-ness comes from incoming `member_of`
   edges"). Its joint activity is *projected* from the members on demand.

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

4. **The per-epoch MAP / legend document DISSOLVES.** Column indices exist only to read the
   combined binary; once each train is attached to its neuron-subject id and the cache carries
   its own ordering, the standalone "column 1 = neuron_A" legend is unnecessary. Its residual
   content (which neurons, in which order, this epoch) is carried by the `member_of` edges +
   the cache's inline ordering. `num_neurons` is derivable (count the members) — dropped
   (T11). `value_type`/`value_description` container fields collapse into the spike-time
   observation's `variable`/description. The stray `app` superclass is dropped (R1).

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

1. **`member_of` edges need the second pass.** The neuron ids live inside `neuron_names.txt`;
   single-doc migrators carry files but do NOT read their contents (confirmed — `pyraview`
   reads the *file list*, not the bytes), and the ids must resolve to migrated neuron-subjects.
   So minting `member_of` (and building the cache with resolved ids) is the **NDI second pass**
   (like `resolveStimulusPresentations` / Path-S), which has the element graph + file access.
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
3. **Second pass** (`ndi.migrate` / NDI-matlab): read `neuron_names.txt`, resolve neuron ids →
   subjects, mint `member_of` edges, materialize the derived cache (`sampled_body` +
   `derived_from` the members, marked rebuildable), and drop the map/legend document.
4. **Verify-before-delete gate** on the corpus (0 stranded per-neuron trains).
5. **Retire the v1 `ensemble` MAP class** from the persist set once the second pass lands
   (until then it stays a green passthrough — do NOT phase-8-delete early).
