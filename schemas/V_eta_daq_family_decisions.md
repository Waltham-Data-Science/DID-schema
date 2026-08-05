# V_eta — the daq ingestion family: proposed dispositions

Read from the NDI `origin/main` templates. Seven classes, and they are **three
different kinds of thing**. Nothing built.

**The test, unchanged:** does the class record *what happened in the experiment*
(archival — V_eta keeps it), or *how NDI was configured to read it on one
machine* (runtime — V_eta does not)?

## The templates, as they actually are

| class | superclasses | depends_on | fields | files |
|---|---|---|---|---|
| `daqsystem` | base | filenavigator_id, daqreader_id, daqmetadatareader_id | `ndi_daqsystem_class` | — |
| `daqreader` | base | — | `ndi_daqreader_class` | — |
| `daqmetadatareader` | base | — | `ndi_daqmetadatareader_class`, `tab_separated_file_parameter` | — |
| `daqreader_epochdata_ingested` | base, epochid | daqreader_id | `epochtable {epochclock, t0_t1}` | `[]` |
| `daqmetadatareader_epochdata_ingested` | base, epochid | daqmetadatareader_id | *(none)* | `data.bin` |
| `daqreader_image_epochdata_ingested` | base, **daqreader_epochdata_ingested** | daqreader_id | `dimension_order`, `dimension_size`, `data_type`, `num_frames`, `frametimes`, `clocktype`, `metadata` | `frames.bin` |
| `dataseries_channel_map` | **ABSENT ON `origin/main`** | | | |

## 1. Three are pure runtime configuration → not archival V_eta classes

`daqsystem`, `daqreader`, `daqmetadatareader`.

Their entire content is a **MATLAB class name**: `ndi_daqsystem_class`,
`ndi_daqreader_class`, `ndi_daqmetadatareader_class`. `daqmetadatareader` adds
`tab_separated_file_parameter` (a file-matching rule) and `daqsystem` adds three
dependencies wiring which reader and navigator it uses. None of that records
anything that happened to a specimen — it records which code was pointed at which
files on the acquisition machine.

This is the identical `ndi_<x>_class` shape already decided for `syncgraph` /
`syncrule` in `V_eta_infra_family_decisions.md`, and flagged before that by the
⑥/⑦ governance sweep. **Same shape, same decision, no new reasoning required.**

→ **Proposed: not archival.** Where the provenance matters it is `software` +
`method_parameters`, the shape already used for calculator configuration.

*Note `daqsystem` is the only one with dependencies, and all three point at the
other runtime classes. The whole cluster refers only to itself — it never
reaches a subject, an epoch's data, or a measurement. That is the structural
signature of configuration.*

## 2. `daqreader_epochdata_ingested` is TIME DATA — it folds into the time model

```
epochtable : { epochclock, t0_t1 }        files: []
```

No bytes. Its entire payload is **a clock name and an interval** — the epoch's
extent under a named clock. That is the *fourth* place this project has found the
same fact:

```
epochclocktimes            { clocktype, t0_t1 }
acquisition_epoch.clocks   { name, t0, t1 }
syncrule_mapping           { epochnode_a, epochnode_b, mapping }
daqreader_epochdata_ingested.epochtable  { epochclock, t0_t1 }
```

→ **Proposed: folds into `relative_reference`** (`V_eta_time_reference_model_plan.md`),
exactly as `syncrule_mapping` does. `epochclock` → `frame`, `t0_t1` →
`start`/`end`, `relative_to` → the epoch.

**This is the second family in a row that resolves into the time model rather
than needing a model of its own.** That is what closing the target buys: the
count of *remaining* decisions falls faster than the count of remaining classes,
because settled models absorb them.

## 3. Two are byte carriers → `opaque_body`

**`daqmetadatareader_epochdata_ingested`** — *no fields at all*, one file
`data.bin`. A pure byte carrier with an epoch and a reader edge.

→ **Proposed: `opaque_body`**, per the standing rule that every format carrier
phases into `sampled_body` / `opaque_body` with the encoding as a field.

**`daqreader_image_epochdata_ingested`** — subclasses
`daqreader_epochdata_ingested`, carries `frames.bin` plus real descriptors:
`dimension_order`, `dimension_size`, `data_type`, `num_frames`, `frametimes`,
`clocktype`, `metadata`.

This one is **not** purely opaque, and it splits cleanly along the lines already
decided elsewhere:

- `frames.bin` + `dimension_order`/`dimension_size`/`data_type`/`num_frames` →
  the **`image` model** (`V_eta_image_model_plan.md`), which already requires
  dtype and axes to be explicit on the composite because they are not
  recoverable from the payload.
- `frametimes` + `clocktype` → **time references**, one per frame or a sampled
  axis — the same fold as (2).
- the inherited `epochtable` → as (2).

→ **Proposed: decomposes into the image model + time references.** No new class.

## What this closes

Seven classes, **zero new models**:

| | disposition |
|---|---|
| `daqsystem`, `daqreader`, `daqmetadatareader` | runtime config — not archival |
| `daqreader_epochdata_ingested` | → `relative_reference` |
| `daqmetadatareader_epochdata_ingested` | → `opaque_body` |
| `daqreader_image_epochdata_ingested` | → image model + time references |
| `dataseries_channel_map` | **absent on `origin/main` — see below** |

## `dataseries_channel_map` — absent, and that must be resolved, not assumed

It is **not on NDI `origin/main`**. It is therefore not a did_v1 source under the
provenance rule, and its presence in the V_eta `in_progress` set means it is
either a V_eta-side invention or a class from a vintage this checkout does not
carry.

**It is NOT being written off on that basis.** The corpora are a sample of
datasets, not the universe, and "absent from the tree I looked at" has been wrong
here before. What is required is a writer check: does any NDI vintage, or any
lab repo, emit it? Until that is answered its disposition is *unknown*, recorded
as unknown.

---

# DECIDED with the team, 2026-08-05 — `acquisition_system` + software fold

**Supersedes section 1 above** ("three are pure runtime configuration → not archival
V_eta classes"). That proposal was written without checking who references these
documents, and **it was wrong in a way that would have lost data.** Recorded as a
reversal in place.

**NO `TEAM-SIGN-OFF` LINE.** The team decided in walkthrough; the marker is theirs.

## What the earlier proposal missed

`daqsystem`'s `base.name` is a **join key**, referenced by two mechanisms that use
NAMES rather than `depends_on` edges — which is exactly why a dependency-graph
check came back empty:

```matlab
% +ndi/+daq/system.m:229  -- getprobes()
myprobemap = ndi.daq.daqsystemstring(epc(ec).devicestring);
if strcmpi(myprobemap.devicename, ndi_daqsystem_obj.name)

% +ndi/+time/+syncrule/commonTriggersOverlappingEpochs.m
parameters.daqsystem1_name, parameters.daqsystem2_name
```

The epochprobemap says which device a probe was plugged into **by the daqsystem's
name**. So does every syncrule. Dissolving `daqsystem` would silently break
probe→device attribution.

**Reference census, read from NDI `origin/main` templates:**

```
daqsystem_id           referenced by: (nothing, by edge)   BUT base.name IS referenced by string
daqreader_id           daqsystem, daqreader_epochdata_ingested,
                       daqreader_image_epochdata_ingested, daqreader_mfdaq_epochdata_ingested
daqmetadatareader_id   daqsystem, daqmetadatareader_epochdata_ingested
filenavigator_id       daqsystem, epochfiles_ingested
```

So **every one of the four must keep its `base.id`** (T10's id-preservation rule —
the payload carriers dangle otherwise), and `daqsystem` must additionally keep its
`base.name`.

## Under writer-wins, these describe SOFTWARE, not hardware

The payload is `ndi_daqsystem_class` — a MATLAB class name. No serial number, no
model, no manufacturer. So T7's device-as-subject route is closed: there is no
hardware fact in the document to attach to a device-subject, and T5 ("a structure
earns subjecthood only when it is a thing-in-itself") does not license minting one.

## The model

Real values, from the writer (`+ndi/+test/+daq/intan_flat_metadata.m:29-33`):

```matlab
fn   = ndi.file.navigator(E, {'#\.rhd\>', '#\.tsv\>'});
dev1 = ndi.daq.system.mfdaq('intan1', fn, ndi.daq.reader.mfdaq.intan(), ...
                            {ndi.daq.metadatareader('.*\.tsv\>')});
```

```
software (entity)      name "ndi.daq.reader.mfdaq.intan"    DEDUPLICATED across sessions
software (entity)      name "ndi.file.navigator"
software (entity)      name "ndi.daq.metadatareader"

daqreader  -> DISSOLVES into the software entity, base.id PRESERVED.
              It has NO parameters -- the only one of the four that fully collapses.

file_navigator ⊂ base        base.id PRESERVED  (epochfiles_ingested.filenavigator_id)
   depends_on: software_id -> software
   data_file_pattern   char[]   {'#\.rhd\>', '#\.tsv\>'}       PARSED, not eval'd
   epoch_map_pattern   char[]   {'(.*)epochprobemap.ndi'}
   epoch_map_format    char     "ndi.epoch.epochprobemap_daqsystem"

metadata_reader ⊂ base       base.id PRESERVED  (daqmetadatareader_epochdata_ingested)
   depends_on: software_id -> software
   metadata_file_pattern  char  ".*\.tsv\>"

acquisition_system ⊂ base    base.id PRESERVED   base.name "intan1"  <- THE JOIN KEY
   depends_on: reader_id            -> software
               navigator_id         -> file_navigator
               metadata_reader_id_# -> metadata_reader
```

## Why a DECLARED block and not `method_parameters`

`setfileparameters` normalises to a **one-field struct, `filematch`** — a CLOSED set,
not an open one:

```matlab
if isa(thefileparameters,'char'), thefileparameters = {thefileparameters}; end
if isa(thefileparameters,'cell'), thefileparameters = struct('filematch',{thefileparameters}); end
```

The signed-off `frequency_filter` document drew the line: a free-form bag is honest
when the knobs are **one program's, author-chosen, open**; typed fields are right
when the set is **closed**. And the decisive point is worse than closed-vs-open —
v1 stores `fileparameters` as **executable MATLAB text**, recovered by `eval`
(`navigator.m:45`). That is exactly T14's litmus failing: *"could a consumer that
has never read our migrator code get the value out… from the schema alone?"* The
migration's job is to PARSE it into declared structure, not carry the code forward.

Note `acquisition_system ⊂ base` would not inherit `method_parameters` anyway —
that field lives on `subject_interaction`. Using it would mean declaring a bag on
purpose.

## Why the configuration stays WITH each component

`system.m:495` uses `add_dependency_value_n('daqmetadatareader_id', ...)` — **N
metadata readers per system**, each with its own `tab_separated_file_parameter`.
Corpus: Soph has 96 `daqsystem` and 32 `daqmetadatareader`, so the count varies and
is often zero.

One `metadata_file_pattern` on the bundle would keep only the first.
`metadata_file_pattern_#` aligned positionally to `metadata_reader_id_#` is
convention-instead-of-declaration, which T14 forbids. So each component's
configuration stays with that component.

**Honest accounting: only ONE of the four fully dissolves.** The class NAMES all
move to deduplicated `software` entities; what remains in each surviving document
is only per-instance configuration, which is a real fact with nowhere cheaper to
live.

---

## THREE CONDITIONS attached to this decision

### 1. Sequence behind TaskList #37, or gate the first corpus run explicitly

**Empty `depends_on` edges are skipped by the validator:**

```
src/did/+did2/+validate/references.m:8    "case) are skipped -- they represent intentionally unfilled"
                                  :90-91  if isempty(documentId) / continue;
```

So `mustBeNonEmpty` on an edge is decorative. That is how all three of today's
findings passed every gate:

```
daqmetadatareader.daqsystem_id      59 of 59 empty        validates clean
syncrule_mapping.epochid         5,316    empty           validates clean
ontology_table_row -> 76,766 statements with empty subject_id   validates clean
```

This model **adds five edges** (`software_id` ×2, and `reader_id` /
`navigator_id` / `metadata_reader_id_#`). Under current validation a migrator that
silently fails to populate any of them emits hollow documents that pass. That is
the same defect, pre-built. Either **#37** lands first, or the first corpus run
checks those five edge names BY NAME in the `silentLoss` output rather than
trusting `quarantine=0`.

### 2. The probe→device join stays a NAME match — a known limitation

We preserve `base.name`, but we do not turn the join into an edge, and cannot
cheaply: `instrument_id` declares `must_refer='subject'`, and
`acquisition_system ⊂ base` is not a subject. `directed_relation` does not help
either — its endpoints are declared `entity`, which `⊂ base` also is not.

So *"which probes were on intan1"* remains `strcmpi` on a name after migration,
exactly as in `system.m:229`. **Not a regression, but not an improvement** — and
recorded here so it is a known limit rather than a later surprise.

### 3. `epoch_map_format` stays a plain `char` for now

It is a MATLAB class name and is really the *format* of the epochprobemap file —
closer to a content type than to software. Binding it to a value_set buys nothing
until #32 makes bindings real: the validator handles only
`maxLength`/`minLength`/`minimum`/`maximum`/`enum`, so a `binding` today is
declarative. Revisit under #32.

## What query gains

- `data_file_pattern` becomes **indexable at all** — today it is `eval`-able text,
  which by T14's own measure is zero query paths.
- Software identity **deduplicates**: "everything acquired with the Intan reader" is
  one `software` entity -> N `acquisition_system`s, instead of a string match on a
  class name repeated once per session.

## Open naming question (NOT decided)

`file_navigator` and `metadata_reader` still name *the code that reads*, not *what
the document holds*. By T13 the honest names may be `file_selection` and
`metadata_file_selection` — the document is a selection rule, not a navigator. Left
open deliberately; cross-repo naming lives in the R5 track (#27).
