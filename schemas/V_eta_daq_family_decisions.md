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
