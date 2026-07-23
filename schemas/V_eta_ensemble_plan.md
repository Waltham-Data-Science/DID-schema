# V_eta — `ensemble` grain (decision)

Status: **DECIDED — grain A (acquisition-infra); `member_of` relations deferred to the
NDI second pass.** The DID single-doc pass keeps `ensemble` as a retained
acquisition-infra document (its current green passthrough); the population/composition
modeling that needs the constituent neuron ids is a second-pass job.

## What `ensemble` is
`ensemble` is new-on-`main` NDI (the V_eta NDI feature branch lags main). Two distinct
things share the name:

1. **The ensemble ELEMENT** — an `ndi.element.timeseries` of type `ensemble`, built on a
   probe, representing the JOINT spiking of the neurons recorded on that probe. Each epoch
   stores a **marked point process** (every spike of every neuron, with a "mark" = which
   neuron fired) as a standard `element_epoch`/vhsb binary. This is an `element` document →
   already handled: the `element` migrator makes it a `subject` (id preserved) + a kind
   `term_assertion` + a lineage `directed_relation` (derived_from the underlying probe).
   The point-process binary → `sampled_body` via the ⑤ data_body machinery.

2. **The per-epoch `ensemble` MAP document** (what THIS decision is about) — records the
   column→neuron mapping for ONE epoch: `depends_on` = `element_id` (the ensemble element) +
   `element_epoch_id` (the epoch); fields `ensemble_name`, `value_type`, `value_description`,
   `num_neurons`, `clocktype`; and a `neuron_names.txt` FILE listing the neuron element ids /
   names in column order. It is the recording-structure metadata for that epoch, NOT a subject
   statement in its own right.

## The constraint that drives the grain
The constituent neuron ids live in the `neuron_names.txt` FILE, **not** in `depends_on`
(only `element_id` + `element_epoch_id` are there). A single-doc DID migrator therefore
CANNOT mint resolvable `member_of` / `part_of` relations from the map document alone — the
same shape of problem as `distance_metadata`'s endpoints (#18) and `stimulus_presentation`'s
animal (#19), both of which resolved only in the NDI second pass where the element graph
(and the file contents) are in hand.

## Options considered
- **A. Acquisition-infra (CHOSEN).** Treat the map like `element_epoch` / a channel map:
  keep it as an epoch-scoped acquisition-infra document (⑦), carrying `num_neurons`,
  `clocktype`, and the `neuron_names` file. Honest (it IS recording metadata), single-doc,
  references intact, corpus stays green. The population/composition modeling is DEFERRED —
  see below.
- **B. Group-subject + `member_of`.** Model the ensemble as a population subject with a
  `part_of`/`member_of` `directed_relation` from each constituent neuron-subject. Semantically
  richest, but IMPOSSIBLE single-doc (neuron ids in the file) — it would need the NDI second
  pass. Nothing lands in the DID pass. Rejected as the DID-pass grain; ADOPTED as the
  second-pass target (below).
- **C. `count_observation` fold.** `num_neurons` → a `count_observation` on the ensemble
  subject + `neuron_names.txt` → `opaque_body`. Simple and single-doc, but structurally loses
  WHICH neurons compose the ensemble (only the count survives). Rejected — the count is
  derivable and the composition is the scientifically meaningful part.

## The plan
1. **DID pass (now):** `ensemble` map → retained acquisition-infra document (⑦). This is the
   current green passthrough; no reshape needed. Disposition stays `in_progress` only because
   the second-pass relations below are pending — the GRAIN itself is settled.
2. **NDI second pass (deferred):** with the element graph + the `neuron_names.txt` file in
   hand, ADD `member_of` `directed_relation`s from each constituent neuron-`subject` to the
   ensemble-`subject` (grain B), WITHOUT removing the map doc (the map remains the per-epoch,
   column-ordered record). Mirrors `resolveStimulusPresentations` / Path-S: a pass over the
   whole migrated body set that mints relations the single-doc migrator cannot.

## Why not just decompose now
Minting `member_of` edges to neuron ids that do not resolve in-batch would turn a green
passthrough into a GATING orphan failure — exactly the trap that reverted `distance_metadata`
Part A (4156 orphans) and that the calculator dissolution hit (11448 orphans). The relation
edges must be minted where their targets resolve: the second pass.
