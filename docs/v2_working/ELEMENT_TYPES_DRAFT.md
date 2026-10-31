# v1 element `type` -> V2 entity type: DRAFT list for Jess Haley

**Status: Proposed (not decided).** Nothing here is built. Nothing is committed, pushed or posted.
Draft written 2026-10-26.

## Commits read

| repo | ref | sha |
|---|---|---|
| NDI-matlab | locked `main` (v1 truth), `tools/sibling_lock.json` | `3cb19a85fb77453e1e656728828b08a54c406e96` |
| NDI-matlab | locked `head` (V2 line) | `f27302632736c42999f790026d861eb976618a49` |
| DID-matlab | locked `head` | `a502c76fc03bced56d79832c780fd1af5dcd2ce2` |
| DID-matlab | `origin/V2` | `f6486be1ddd6df5743b8a6aab8f175020319284b` |
| did-schema | `HEAD` (branch `claude/carry-register-rows`) | `5594e59b37227a858db05740df7334fc8aa331dd` |

The sibling clones were read with `git show` / `git grep` only, and HEAD was not moved.
`git rev-parse HEAD origin/main origin/V2` in the NDI clone printed `f273026… 3cb19a8… 9b99061…`. In the DID clone `git rev-parse HEAD origin/V2` printed `a502c76… f6486be…`.
The did-schema working tree has uncommitted edits in `did_v2_STATUS.md` and the two coverage-ledger files. This draft cites none of them. Every did-schema file cited here is clean (`git status --short` on them printed nothing).
In the citations below, `NDI:` means NDI-matlab at `3cb19a8` unless another ref is named.

## What the code does today

DID-matlab `src/did/+did2/+convert/+migrators_j/element.m:209-221` at `a502c76` (the same text is at `:235-247` on `origin/V2` `f6486be`):

```
function t = elementEntityType(elementType)
%ELEMENTENTITYTYPE The entity.type an element-subject takes (PROPOSED, unsigned):
switch lower(strtrim(char(elementType)))
    case {'spikes', 'neuron', 'cell'}   t = 'cell';
    case {'ensemble'}                   t = 'group';
    otherwise                           t = 'device';
```

Under `otherwise`, every JH `position` / `distance` element becomes a `device`.

## The rules this draft applies

- [one correct reading] (`did_v2_go_forward_class_audit.md:1220`): the generic migration writes a V2 document only when the v1 document by itself gives exactly one correct V2 reading. Otherwise the document is carried whole as v1 with a `needs_mapping` register row.
- [dataset-specific logic leaves the generic migration] (`:1208`) and [dataset audit batch 1 and 2] (`:1228`, item 1): the Haley worm-track shapes leave the generic migration, and "the Haley V2 import makes the tracks".
- T1 (`did_v2_tenets.md:39`): `entity.type` is the coarse kind, a bound and required field. The finer kind is a term assertion.
- `entity_type_bindings` (`schemas/registry/binding_registry_meta.json`): 19 rows, at lines 2746-2890. The rows used here:
  - `cell` (`:2770`): "one cell".
  - `Group` (`:2778`, description `:2780`): "an entity whose members are entities, by `member_of`: a cohort, an ensemble".
  - `device` (`:2786`, description `:2788`): "an instrument or a piece of apparatus".

## What NDI says an element `type` is

- A **probe** is an element (`NDI: src/ndi/+ndi/probe.m:1`, `classdef probe < ndi.element`), described as "an instance of an instrument that can be used to MEASURE or to STIMULATE" (`probe.m:4-5`).
- `PROBE-TYPES.md:3` (`NDI: src/ndi/docs/NDI-matlab/under_construction/PROBE-TYPES.md`) says: "a **probe** is an instrument for observing or manipulating the experimental environment".
- `PROBE-TYPES.md:11` says the type is free text: "there are standard types (see below) but users can use any valid string for type".
- **A probe's type is a closed set at runtime.** `NDI: src/ndi/+ndi/+probe/+fun/probestruct2probe.m:21-22` runs `if ~isKey(probeTypeMap, probestruct(i).type) throwProbeTypeNotFoundError(...)`. The map is `NDI: src/ndi/ndi_common/probe/probetype2object.json` (24 entries, read by `initProbeTypeMap.m:6`). So a probe object can only carry one of the 24 registered strings, matched exactly.
- **A non-probe element's type is unconstrained.** `ndi.element` takes `ELEMENT_TYPE` as a plain argument (`NDI: src/ndi/+ndi/element.m:19-20`) and writes it to `element.type` (`element.m:549`).
- **A derived element copies its source's type.** `ndi.element.oneepoch` (`NDI: src/ndi/+ndi/+element/oneepoch.m:63-64`) and `ndi.element.downsample` (`downsample.m:41-44`) both create an `ndi.element.timeseries` with `ndi_element_timeseries_obj_in.type`, not direct.
  So a downsampled LFP of an `n-trode` probe is an element with type **`n-trode`**, class `ndi.element.timeseries`, `direct` 0 and an `underlying_element_id`. That element is a derived signal, not an instrument.
  **The type string alone therefore cannot say "device".** What separates the two cases is `element.ndi_element_class`, which NDI writes as `class(obj)` (`element.m:546`).

Because of the last point, every row below that proposes `device` carries a condition: **`ndi_element_class` starts with `ndi.probe.`** In every corpus measured, all probe-type elements meet this condition (see the corpus census). A probe-type string on any other class is carried.

## The draft table

Confidence is high, medium or low, and the reason is given after the dash.

### A. The 24 registered probe types

Source: `probetype2object.json`, with line numbers in that file.
**Proposed for every row in this block: `device`, but only when `ndi_element_class` starts with `ndi.probe.`. Otherwise carried: `needs_mapping`.**

| type string | what NDI says it is (evidence) | confidence and why |
|---|---|---|
| `n-trode` | `:3` → `ndi.probe.timeseries.mfdaq`. "A bundle of N extracellular electrodes" (`PROBE-TYPES.md:19`). Classed `Electrode` (`+database/+metadata_app/+fun/loadProbes.m:38`). | **High**: an electrode is an instrument. |
| `electrode-$` | `:5` → mfdaq. "An electrode of a specification that is contained in a reference SPEC" (`PROBE-TYPES.md:20`). | **High** for the literal string. For suffixed forms, see Q4. |
| `patch` | `:7` → mfdaq. "A whole cell patch electrode (two channels…)" (`PROBE-TYPES.md:21`). `Pipette` (`loadProbes.m:29`). | **High** |
| `patch-Vm` | `:9` → mfdaq. `PROBE-TYPES.md:22`, `loadProbes.m:30`. | **High** |
| `patch-I` | `:11` → mfdaq. `PROBE-TYPES.md:23`, `loadProbes.m:31`. | **High** |
| `patch-attached` | `:13` → mfdaq. `PROBE-TYPES.md:24`, `loadProbes.m:32`. | **High** |
| `sharp` | `:15` → mfdaq. "A sharp electrode" (`PROBE-TYPES.md:25`), `loadProbes.m:33`. | **High** |
| `sharp-Vm` | `:17` → mfdaq. `PROBE-TYPES.md:26`. Written by `+setup/+conv/+marder/abf2probetable.m:51`. | **High** |
| `sharp-Im` | `:19` → mfdaq. Written by `abf2probetable.m:54`. | **High**: same instrument as the documented `sharp-I`. |
| `wide-field-imaging` | `:21` → `ndi.probe.image`. "Wide-field imaging data…" (`PROBE-TYPES.md:29`). | **Medium**: the docs describe the data, but the class is a probe, which is an instrument (`probe.m:4-5`). |
| `two-photon-imaging` | `:23` → `ndi.probe.image`. `PROBE-TYPES.md:30`. vhlab `prairieTP` is normalised to it (`+setup/+epoch/epochprobemap_daqsystem_vhlab.m:151-155`). | **Medium**: same reason. |
| `one-photon-imaging` | `:25` → `ndi.probe.image`. `PROBE-TYPES.md:31`. | **Medium**: same reason. |
| `brightfield-imaging` | `:27` → `ndi.probe.image`. `PROBE-TYPES.md:32`. | **Medium**: same reason. |
| `lick-spout` | `:29` → mfdaq. Listed under "_Environment_" (`PROBE-TYPES.md:38`). | **Medium**: apparatus matches the `device` description (`:2788`). What it measures is unstated, but that is a modality question, not an entity-type question. |
| `intraoral-cannula` | `:31` → `ndi.probe.timeseries.stimulator`. "_Environment_" (`PROBE-TYPES.md:39`). | **Medium**: apparatus. |
| `optogenetic-fiber` | `:33` → stimulator. | **High**: an instrument. |
| `reward-well` | `:35` → mfdaq. "_Environment_" (`PROBE-TYPES.md:40`). | **Medium**: apparatus. |
| `stimulator` | `:37` → stimulator. Written by `+setup/+epoch/epochprobemap_daqsystem_vhlab.m:96,124` and `+setup/+conv/+marder/abfprobetable2probemap.m:96`. | **High** |
| `ecg` | `:39` → mfdaq. Written by `+setup/+conv/+gluckman/channelname2probename.m:26`. | **Medium-high**: a sensor. NDI names the measurement, not the device. |
| `eeg` | `:41` → mfdaq. `channelname2probename.m:23` (gluckman's default for any channel). | **Medium-high**: same reason. |
| `accelerometer` | `:43` → mfdaq. `+setup/+conv/+gluckman/channelnames2daqsystemstrings.m:57`. | **High**: names the instrument. |
| `thermometer` | `:45` → mfdaq. `abf2probetable.m:57`. | **High**: names the instrument. |
| `ppg` | `:47` → mfdaq. Read back at `+setup/+conv/+marder/marderprobe2uberon.m:11`. | **Medium-high**: a sensor. |
| `event` | `:49` → stimulator. vhlab writes it for the `vhtaste_sync` sync line (`epochprobemap_daqsystem_vhlab.m:86`). | **Medium**: it is a probe, so an instrument by NDI's definition, but here it is a sync channel rather than a physical instrument. See Q5. |

### B. Probe types that are documented but not registered

`probestruct2probe.m:21-22` throws on these, so no probe object can carry them.

| type string | what NDI says it is (evidence) | proposed | confidence and why |
|---|---|---|---|
| `sharp-I` | "A sharp electrode (single channel, specifies current recording)" (`PROBE-TYPES.md:27`). Mapped in `loadProbes.m:35`. | **carried: needs_mapping** | **High** that it is ambiguous: not in the map (the shipped spelling is `sharp-Im`), so it cannot be a probe's type. An element carrying it is not a probe. |
| `display` | `PROBE-TYPES.md:34`, under "_Stimulators_" | **carried: needs_mapping** | Same reason. |
| `stim-n-trode` | `PROBE-TYPES.md:35` | **carried: needs_mapping** | Same reason. |
| `n-LED` | `PROBE-TYPES.md:36` | **carried: needs_mapping** | Same reason. |

### C. Element types NDI writes that are not probe types

| type string | what NDI says it is (evidence) | proposed | confidence and why |
|---|---|---|---|
| `spikes` | **A sorted unit.** `ndi.neuron` is "an ndi.element that contains data from a neuron … simply an ndi.element.timeseries object that has a different type" (`NDI: src/ndi/+ndi/neuron.m:2-5`). Writers: `+element/spikesForProbe.m:33`; `+app/spikesorter.m:274-276`; `+element/timeseries.m:233` (default `etype = 'spikes'`, class default `'ndi.neuron'` at `:193`); kilosort, kiasort and jrclust `probe.m` (`+kilosort/probe.m:583`). **But NDI also files multi-unit clusters here:** `spikesorter.m:262-263` gives 'Multi-unit' quality 3 and `:273` keeps every value ≤ 4. kilosort imports `["good" "mua"]` by default (`+kilosort/probe.m:196`; "multi=4" at `:120-122`). | **cell**, contested (Q1) | **Low-medium.** NDI calls it a neuron, but a multi-unit cluster is not "one cell" (`:2772`). The element document cannot tell the two apart: the single/multi label is on a separate `neuron_extracellular` document. In the corpora, 621 of the 1,511 units that have that document are `multi` (see the census). |
| `ensemble` | "a spiking-neuron ensemble as a timeseries element … (type 'ensemble')" (`NDI: src/ndi/+ndi/+element/ensemble.m:2-4`, literal at `:55`). Created by `+fun/+ensemble/private/ensembleElementFor.m:17`. | **Group** | **High.** TEAM-SIGN-OFF [ensemble] (`did_v2_ensemble_plan.md:10`) says "the ensemble is a GROUP SUBJECT with its id preserved". The `Group` binding description names "an ensemble" (`:2780`). [ensemble retired] (`:284`) puts the migration in NDI's second pass. No corpus has one. |
| `position` | Haley import: `ndi.element.timeseries(session, [worm,'_',bodyPart,'_position'], 1, 'position', [], 0, subject_id)` (`NDI: src/ndi/+ndi/+setup/+conv/+haley/doImport.m:590-591`). It is a time series of x/y pixel coordinates (`:580`, `:597-599`). | **carried: needs_mapping** | **High** that it is not an entity. It is a derived signal about the worm (`subject_id`), with no underlying element. [dataset audit batch 1 and 2] item 1 gives it to the Haley V2 import. The map entry would say "an observation of the subject, variable position". |
| `distance` | Haley import, `doImport.m:610-611`. Distance to the lawn edge, plus the closest lawn id (`:581-582`, `:617-625`). | **carried: needs_mapping** | **High**: same reason as `position`. |
| *(source's type, copied)* | `oneepoch.m:63-64` and `downsample.m:41-44` create a derived `ndi.element.timeseries` that carries its source probe's type string. | **carried: needs_mapping** | **High**: a derived signal. This is the case the `ndi.probe.` condition in block A catches. |

### D. Strings with no NDI definition, or that never reach `element.type`

| type string | evidence | proposed | confidence and why |
|---|---|---|---|
| `neuron`, `cell` | Mapped to `cell` by today's `elementEntityType` (DID `element.m:214`). This grep found no NDI `main` writer that stores either as an element type: `git grep -n -E "element\.type'?,\s*'(neuron\|cell)'\|'type',\s*'(neuron\|cell)'\|,\s*'(neuron\|cell)'\s*,\s*[A-Za-z_\[]" 3cb19a8 -- 'src/*.m'` printed nothing. Absence of a match is not proof; this only records that no writer was found. | **carried: needs_mapping** | **Medium.** No NDI definition was found to rely on, and no corpus element has either string. See Q3. |
| `field`, `lfp`, `madeup` | Test only: `+test/+element/test_ndi_element.m:45,49,53` | **carried: needs_mapping** | **High**: no NDI definition. `lfp` is a derived signal. |
| `''` (empty) | gluckman sets `probetype = ''` for counter, status and ACC channels (`channelname2probename.m:28-36`) | **carried: needs_mapping** | **High**: nothing to read. |
| `singleEC`, `ntrode`, `prairieTP` | vhlab shorthand, normalised before writing: `singleEC`/`ntrode` → `n-trode` (`epochprobemap_daqsystem_vhlab.m:212-213`), `prairieTP` → `two-photon-imaging` (`:151-155`) | *(never stored)* | Not a row. These strings never reach an element document. |
| `extracellular_electrode-4` | Only as an example in a comment (`+daq/daqsystemstring.m:13`). It is not an exact key, so `probestruct2probe` would throw on it. | **carried: needs_mapping** | See Q4. |
| any other string | `PROBE-TYPES.md:11`: "users can use any valid string for type" | **carried: needs_mapping** | There is no default. This is the agreed direction. |

### Summary counts

- **Distinct strings in the table: 38.** That is 24 registered (A), 4 documented but unregistered (B), 4 written non-probe types (`spikes`, `ensemble`, `position`, `distance`), 2 legacy (`neuron`, `cell`), 3 test strings, the empty string, and `extracellular_electrode-4`. The type-copied case and the three never-stored shorthands are not counted. "Any other string" is a rule, not a row.
- **Proposed mapped: 26.**
  - 24 → `device`, only when the class is `ndi.probe.*`.
  - `spikes` → `cell`, contested (Q1).
  - `ensemble` → `Group`.
- **Proposed carried (`needs_mapping`): 12.** Plus every unlisted string, and any block A string on a class that is not a probe.

## Corpus census (element documents)

Script: `/tmp/claude-0/-home-user-DID-schema/eed0047f-e975-5bb3-82d1-f9571e1b128c/scratchpad/elemtypes/tools/census.py`, run with `python3 -I` on the zips in `scratchpad/corpora/`. The output is saved next to this file as `census_out.txt`.

Denominator: every non-`__MACOSX` JSON entry. Exactly half of each zip's `.json` entries are macOS resource forks. Every real entry parsed (`macosx_check.txt`):

```
20211116.zip json: 2440 __MACOSX: 1220 real: 1220 real unparsed: 0
Dab.zip json: 55122 __MACOSX: 27561 real: 27561 real unparsed: 0
JH.zip json: 157376 __MACOSX: 78688 real: 78688 real unparsed: 0
Soph.zip json: 202854 __MACOSX: 101427 real: 101427 real unparsed: 0
```

Census output (type | ndi_element_class | direct | has underlying → count):

```
== 20211116.zip ... parsed: 1220 ... element docs (class_name element): 23
    spikes | ndi.neuron | False | True -> 21
    n-trode | ndi.probe.timeseries.mfdaq | True | False -> 1
    stimulator | ndi.probe.timeseries.stimulator | True | False -> 1
  neuron_extracellular quality by element type: 21
    ('spikes', ('multi', 4)) -> 17
    ('spikes', ('single', 1)) -> 4
== Dab.zip ... parsed: 27561 ... element docs: 896
    stimulator | ndi.probe.timeseries.stimulator | True | False -> 215
    patch-I | ndi.probe.timeseries.mfdaq | True | False -> 202
    patch-Vm | ndi.probe.timeseries.mfdaq | True | False -> 202
    n-trode | ndi.probe.timeseries.mfdaq | True | False -> 143
    spikes | ndi.neuron | False | True -> 134
== JH.zip ... parsed: 78688 ... element docs: 4156
    distance | ndi.element.timeseries | False | False -> 2078
    position | ndi.element.timeseries | False | False -> 2078
== Soph.zip ... parsed: 101427 ... element docs: 1647
    spikes | ndi.neuron | False | True -> 1554
    n-trode | ndi.probe.timeseries.mfdaq | True | False -> 61
    stimulator | ndi.probe.timeseries.stimulator | True | False -> 32
  neuron_extracellular quality by element type: 1490
    ('spikes', ('multi', 4)) -> 604
    ('spikes', ('single', 1)) -> 886
```

**Not measured:** B, Babu, and any other corpus. None is available in this container.
The zips' origin and date are not established here. The files are dated Oct 25 18:51. The sha256 prefixes are in `census_out.txt`.
Dab has 134 `spikes` elements but no `neuron_extracellular` document, so their single/multi label is not recorded. Soph has 1,554 `spikes` elements but only 1,490 with that document.

Each corpus element under this draft (6,722 elements in all):

| corpus | elements | → device | → cell (if Q1 is yes) | carried |
|---|---|---|---|---|
| 20211116 | 23 | 2 | 21 | 0 |
| Dab | 896 | 762 | 134 | 0 |
| JH | 4,156 | 0 | 0 | **4,156** (`position`, `distance`) |
| Soph | 1,647 | 93 | 1,554 | 0 |
| **total** | **6,722** | **857** | **1,709** | **4,156** |

If Q1 is answered "carry `spikes`", carried becomes 5,865. If Q1 is answered "multi-unit → Group" with the label read from `neuron_extracellular`, 621 units change type and 64 Soph units plus 134 Dab units have no label to read.
Every probe-type element in these corpora is an `ndi.probe.*` class with `direct` true. So the `ndi.probe.` condition carries none of them today.

## Questions for Jess (one line each)

1. Should `spikes` (NDI `ndi.neuron`) map to `cell` even though NDI files multi-unit clusters there too (621 of 1,511 labelled units are `multi`), or should it be carried, or should multi-unit become a `Group`?
2. Should the list key on `ndi_element_class` as well as `type`, so that a probe-type string becomes `device` only on an `ndi.probe.*` class and a derived copy (oneepoch, downsample) is carried?
3. Should `neuron` and `cell` stay on the list, given that no NDI `main` writer was found for them?
4. Should `electrode-<spec>` and `<prefix>_electrode-<spec>` map to `device` like the literal `electrode-$`, even though `probestruct2probe` accepts only the exact key?
5. Is `event` (a sync line on the stimulator class) a `device`, or should it be carried?
6. Are the "_Environment_" probes (`lick-spout`, `reward-well`, `intraoral-cannula`) `device` (apparatus), or should they be carried?
7. Should the four imaging types map to `device`, given that NDI's docs describe them as data while their class is a probe?
8. When an element is carried as v1, do the V2 documents that depend on it (`element_epoch`, `position_metadata`, …) also carry, or do they point at the v1 document?
9. Should the migrator write `Group` (the binding's spelling) rather than today's `group`, or is matching by node enough ([registry holds nodes], `did_v2_term_registry_plan.md:188`)?
