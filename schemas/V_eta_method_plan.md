# V_eta: one `method` shape, and stimuli as `method` documents

Written 2026-10-21 at Jess Haley's request ("ok, build the new method document and
drop visual grating"). A PROPOSAL, built ahead of signature at her request. Nothing
here is signed; the line to sign is at the end.

## The problem

Three things were wrong with how V_eta said HOW something was done.

1. **The settings were separated from their method.** An interaction carried a
   `method` term and, beside it, a `method_parameters` entry list. The standalone
   document (`method_parameters`, #74) carried only the list, so a named protocol
   ("default" spike-extraction settings) could say what its knobs were set to but
   not what technique they configure. `relation` carried only the term;
   `clock_alignment_configuration` only the list. One idea, three spellings.
2. **A playlist mixes stimulus kinds.** A presentation becomes one
   `item_manipulation` whose `item` names the distinct stimuli shown. The
   manipulation has ONE `method`, so it cannot name each stimulus's kind when a
   sequence interleaves gratings, bars and a blank -- which the vhlab NewStim
   corpora do.
3. **A class per stimulus kind does not generalise.** `visual_grating` was a
   composite with typed cells for orientation, spatial and temporal frequency,
   contrast, size, centre, duration, phase and a blank flag, plus a
   `spatial_frequency` composite that existed only for it. The next kind (a bar, a
   sparse-noise frame, a shape movie, an odour pulse train, an auditory chirp) would
   each need its own class. T12 says a class per vocabulary entry is wrong (rule 2):
   the kind of stimulus is vocabulary.

## The decision (proposed)

1. **One `method` shape, inline and standalone: `method: {term, parameters}`.**
   - `term`: an `ontology_term` (`{node, name}`), carrying the binding the old
     `method` term had (`{strength: preferred, node_form: curie}`).
   - `parameters`: the existing entry list, unchanged in shape (data_body
     AMENDMENT 3): `variable`, `unit`, `source_unit`, `approximate`, plus ONE value
     form -- `term`, `quantity {value, source_value}`, `count` or `text`.
2. **The standalone class `method_parameters` is renamed `method`.** Its own block
   IS the method: `method.term` and `method.parameters` sit beside `method.name`
   (the protocol name, kept), so a document reads exactly like an interaction's
   inline block. Its edges are kept: `software_id`, `entity_id`, `epoch_id`, and
   `parent_id` (lineage), which now points at `method`.
3. **The edge `method_parameters_id` on `interaction` is renamed `method_id`**
   (-> `method`). The existing rule stands: a statement carries the inline `method`
   OR `method_id`, never both (team, 2026-08-09).
4. **Stimuli given as a recipe are `method` documents.** An `item`'s `item_id`
   names one `method` document per distinct stimulus: term "drifting sinusoidal
   grating", parameters orientation / spatial frequency / temporal frequency /
   contrast / waveform ... A blank is its own `method` document. Stimuli given as
   what was delivered (a movie's frames, a current trace, a measured light level)
   keep using the value for that quantity (`intensity`, `current`, ...).
5. **`visual_grating` and `spatial_frequency` are deleted.** Spatial frequency
   becomes a parameter whose `unit` is a bound term (cycles per degree), as every
   other knob's unit already is.
6. **Tenets** (proposed amendments, in `V_eta_tenets.md`, marked as such): T12 --
   a stimulus given as a recipe is a method term plus parameters, vocabulary not a
   class per generator; a stimulus given as what was delivered uses the value for
   that quantity. T13 -- the naming lesson of the old "`visual_grating` rule" is
   kept under a new example (`tuning_curve`), and `parameters` is allowed only
   inside `method`, where its owner names it (the same reason `method_parameters`
   was accepted).

## Example: a Dab grating, a blank, and the manipulation that shows them

Two distinct stimuli from one NewStim periodicstim script, as `method` documents
(only the `method` block is shown; `base` and the edges are as for any document).
The terms are LABELS (`{name}`, no node) until the term registry carries them --
follow-up (a).

```json
{"method": {
   "name": "",
   "term": {"node": "", "name": "drifting sinusoidal grating"},
   "parameters": [
     {"variable": {"node": "", "name": "orientation"},
      "unit": {"node": "", "name": "degree"},
      "quantity": {"value": 90, "source_value": "90"}},
     {"variable": {"node": "", "name": "spatial frequency"},
      "unit": {"node": "", "name": "cycles per degree"},
      "quantity": {"value": 0.1, "source_value": "0.1"}},
     {"variable": {"node": "", "name": "temporal frequency"},
      "unit": {"node": "", "name": "hertz"},
      "quantity": {"value": 4, "source_value": "4"}},
     {"variable": {"node": "", "name": "contrast"},
      "quantity": {"value": 1, "source_value": "1"}},
     {"variable": {"node": "", "name": "waveform"},
      "term": {"node": "", "name": "sinusoid"}}]}}
```

```json
{"method": {
   "name": "",
   "term": {"node": "", "name": "blank screen"},
   "parameters": []}}
```

The presentation is an `item_manipulation` on the animal: its `item` value's
`item_id` names the two `method` documents (deduplicated, in order), `value.item`
is the playlist (0-based positions into `item_id`, one per trial along the onset
key), and `value.control_item` is 1, the blank. Its own inline `method` says how the
sequence was delivered (for example term "visual stimulation", parameters the
monitor's frame rate and viewing distance), not what each stimulus was -- that is
on the documents the playlist names.

## What it touches

**did-schema (this change).** `tools/build_v_eta.py` section 12.20 reshapes four
sites and the item edge, and the earlier `visual_grating` / `spatial_frequency`
definitions, their later patches, the `spatial_frequency` type-enum entry, the
`DATA_TYPES` membership, the `cycles_per_degree` unit-table row and the
`visual_grating_manipulation` write are removed:

| site | was | now |
|---|---|---|
| `interaction` | `method` (term) + `method_parameters` (list) | `method {term, parameters}` |
| `interaction` edge | `method_parameters_id` -> `method_parameters` | `method_id` -> `method` |
| `relation` | `method` (term) | `method {term, parameters}` |
| `clock_alignment_configuration` | `method_parameters` (list) | `method {term, parameters}` |
| `method_parameters` (class) | block `{name, method_parameters}` | class `method`, block `{name, term, parameters}`; `parent_id` -> `method` |
| `item` edge `item_id` | documentation | says a recipe stimulus is a `method` document |
| `visual_grating`, `spatial_frequency` | value classes | deleted |

Fields named `method` that are NOT changed: `control_stimulus_ids`'s
`control_stimulus_id_method.method`, `gene_list_mapping.method` and
`reverse_correlation.method` are did_v1 tombstones and keep the v1 writer's
spelling.

Migration-target record: the five rows whose `decided_targets` named
`method_parameters` (sorting_parameters, spike_extraction_parameters,
spike_extraction_parameters_modification, stimulus_response_scalar_parameters_basic,
vmspikefilteringparameters) now name `method`. Their migrators still emit
`method_parameters`, so the coverage ladder reads rung 3 `no` for them until the
migrators move -- the schema is ahead of the migrators, which is the honest state.
`stimulus_presentation`'s `second_pass` still records `visual_grating`, because that
list records what NDI's second pass emits today, not the decision. `coverage.py`
acknowledges `method_parameters` and `visual_grating` as names the pinned
migrators still mint.

**DID-matlab (`did2.build` and the migrators).** Builders and readers must move:
`method` (term) -> `method.term`; `method_parameters` (inline list) ->
`method.parameters`; class `method_parameters` -> `method`, its block's
`method_parameters` -> `term` + `parameters`; edge `method_parameters_id` ->
`method_id`; `relation.method` -> `relation.method.term`;
`clock_alignment_configuration.method_parameters` ->
`clock_alignment_configuration.method.parameters`. `jMethodParameters.m` and
`resolveResponseParameters` mint the old class.

**NDI-matlab (the second pass and the reader).** The stimulus decomposition
(`stimulusPresentationToTimedSequence`, `hartleyBasisGratings`) mints
`visual_grating` documents; it should mint one `method` document per distinct
stimulus instead. Readers that look up a protocol by name (`spikeextractor`,
`spikesorter`) query the renamed class.

## Open follow-ups

(a) **A term-registry row per method term listing its required parameters** --
"drifting sinusoidal grating" requires orientation, spatial frequency, temporal
frequency and contrast -- so a method document can be checked for completeness,
the way a binding checks a variable.

(b) **A `matrix` parameter value form** for noise palettes and random seeds, which
are arrays and fit none of `term` / `quantity` / `count` / `text` today. **PROPOSED AND
BUILT 2026-10-21 as `V_eta_data_body_model_plan.md` AMENDMENT 4** (the entry's
home), awaiting signature there.

(c) **The NDI second-pass emitter and the DID-matlab migrators move to this shape
when they are ported to the #88 shape.** They are pinned to `v_eta-pre73`, so
nothing breaks now.

**Shape movies (Jess Haley, 2026-10-21; built with the emitter port, not now).**
NewStim `shapemoviestim` stimuli -- 80 presentations, 769 stimuli, all in the
Fitzpatrick tree-shrew dataset (corpus B) -- become `method` documents with a
method term for "shape movie" and the parameters the v1 document records: the
frame rectangle (width / height, source pixels), background, scale, frame rate,
frame count, inter-stimulus interval, and the per-stimulus label (`angle` in
degrees, or `disparity`, source units as written). The drawn shapes are NOT
recorded in v1 -- they live in NewStim's `nframemovies` property, only in the
original `stims.mat`, which was never uploaded to NDI Cloud -- so each document
says so in its notes.

(d) **The same-entry query operator** (being built separately in DID-matlab): a
query for "orientation = 90 AND spatial frequency = 0.1" must match both
conditions within ONE method document, and "unit = degree" must match the entry
whose variable is orientation, not any entry in the list.

To be signed: one method shape {term, parameters} inline and as the standalone method document (method_parameters renamed method, method_parameters_id renamed method_id); stimuli given as a recipe are method documents referenced by item; visual_grating and spatial_frequency deleted; T12/T13 amended

TEAM-SIGN-OFF [method]: jess@walthamdatascience.com / 2026-10-21 -- one method shape {term, parameters} inline and as the standalone method document (method_parameters renamed method, method_parameters_id renamed method_id); recipe stimuli are method documents referenced by item; visual_grating and spatial_frequency deleted; T12/T13 amended

Decided by Jess Haley, 2026-10-21 [non-grating stimuli as methods]: a visual stimulus that is not a grating (sparse noise / reverse correlation, other noise, disparity, flashed bars, shape movies) migrates the same way as a grating: one `method` document per distinct stimulus, its term naming the stimulus kind and every v1 parameter an entry, a parameter with no ontology term taking a label as its variable. No new class (answer "3A"; did-schema issue #94 item 1).

Decided by Jess Haley, 2026-10-22 [flashed bar]: a NewStim periodicstim with imageType 0 drawn in a narrow oriented rectangle is a "flashed bar" (a new EMPTY term: a stationary bar of uniform luminance presented briefly against the background), not "uniform luminance field". Evidence (VH-Lab/vhlab-NewStim-matlab `@periodicstim/periodicstim.m`): imageType 0 = "field (single luminance across field)", windowShape 2 = "oriented rectangle", animType 0 = "no animation", flickerType 0/1 = light/dark; all 17,260 imageType-0 stimuli in corpus B are rectangles at most 50 px on their short side, animType 0, nCycles 1 at 10 Hz. Light vs dark stays a parameter (T19). Her words: "flashed bar if that's truly the right term".

Decided by Jess Haley, 2026-10-22 [shape movie note]: a presentation whose playlist includes a shapemoviestim carries, in its own `notes` (statement.notes), that the shapes drawn on each frame (NewStim `nframemovies`) are not in the v1 record, which holds only the settings (`SMSparams`). The shared method document carries no note. (Answer: "If you think that's the best do it", to option (b).)

Decided by Jess Haley, 2026-10-22 [Hartley without enumeration]: a Hartley presentation with no `hartley_calc` enumeration is converted like every other stimulus kind: one method document, term "Hartley stimulus", its raw v1 parameters as entries; the presentation's `notes` says the individual gratings are not listed in the source. Nothing is refused or invented. (Answer: "What do you think, a?", agreeing to (a).)

Decided by Jess Haley, 2026-10-22 [spatial phase in degrees]: a stimulus's spatial phase (NewStim periodicstim `sPhaseShift`, "in radians where 2*pi is 1 cycle") is stored in the canonical angle unit, degrees (`om:degree`), per T14 ("Canonical units are PRACTICAL SI ... `degrees` (not radians)"), with `source_value` the v1 number in radians and `source_unit` `om:radian`. This corrects the earlier answer "A" (radian as the stored unit), which conflicted with T14; om:radian stays registered as the source unit. (Her words: "Agreed. You can fix the degrees issue.")

Decided by Jess Haley, 2026-10-22 [flashed bar parent]: EMPTY:0000366 "flashed bar" sits under NCIT:C61406 Stimulation, as EMPTY:0000358 does (empty-ontology #23), not XCO visual stimulus or NCIT Stimulus. Answer "3a".

Deferred by Jess Haley, 2026-10-22, to after the merge: the stimulus vocabulary proposals (non-blocking). Answer "5y".

## 2026-10-22 -- tenet audit

Decided by Jess Haley, 2026-10-22 [method shared plus own]: an interaction may carry `method_id` (shared) AND an inline `method` whose parameters add settings only this run had: no variable in both, and the inline term empty. A changed shared setting still makes a variant method document with `parent_id`. This replaces "never both" (team, 2026-08-09) (answer "O6a").

Decided by Jess Haley, 2026-10-22 [rules and clock_alignment tenet]: named validator rules: an assertion has no time dimension; `method_id` and an inline method share no variable ([method shared plus own]). T15 gains a clock_alignment paragraph (a relation with four named edges) (answer "P1a"). Built: rules `assertion_no_time_dimension` (assertion) and `method_shared_and_own` (interaction); the T15 paragraph is in V_eta_tenets.md.
