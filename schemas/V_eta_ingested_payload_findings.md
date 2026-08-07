# V_eta — the daq ingested-payload family: findings and a proposal

**STATUS: FINDINGS ARE FACTS; THE MODEL IS A CLAUDE PROPOSAL, NOT DECIDED.**
The team walked through this on 2026-08-06 and asked for it to be recorded, but has
not adopted the model. The board therefore still shows this family as *written up by
Claude alone, unreviewed*. NO `TEAM-SIGN-OFF` LINE (Operating Rule 4).

Covers `daqreader_epochdata_ingested`, `daqmetadatareader_epochdata_ingested`,
`daqreader_image_epochdata_ingested`.

---

## GROUND TRUTH

```
DENOMINATOR   91 NDI templates on origin/main;  1,002 .m files
              5 corpora (20211116, B, Dab, JH, Soph), 221,813 v1 documents
              223 V_eta class schemas
```

### The three templates

```
daqreader_epochdata_ingested          ⊂ base, epochid    dep: daqreader_id
   epochtable { epochclock, t0_t1 }         BOTH CELL ARRAYS -- see below
   files: { file_list: [ ] }                DECLARED EMPTY

daqmetadatareader_epochdata_ingested  ⊂ base, epochid    dep: daqmetadatareader_id
   (NO FIELDS AT ALL)
   files: { file_list: [ "data.bin" ] }

daqreader_image_epochdata_ingested    ⊂ base, daqreader_epochdata_ingested
                                                        dep: daqreader_id
   dimension_order "YXCZT", dimension_size, data_type, num_frames,
   frametimes, clocktype, metadata
   files: { file_list: [ "frames.bin" ] }
```

V_eta additionally carries a `parameters` field on the first
(`sample_analog_segment`, `sample_digital_segment`) — folded in from the
`daqreader_mfdaq_epochdata_ingested` subclass by the ⑥/⑦ chunk (c) de-encoding.

### Volumes (test-code.yml run #257 / 0458dae, 2026-07-29)

```
daqmetadatareader_epochdata_ingested   B 1242 / Dab 1242 / Soph 175 = 2,659
                                       UNCONVERTED -- no migrator, passes through whole
daqreader_epochdata_ingested           has a migrator (migrators_j/daqreader_mfdaq_epochdata_ingested.m)
daqreader_image_epochdata_ingested     EMITTED by migrators_i/image_stack.m:107
```

---

## THE FINDING THAT REFRAMES THE FAMILY

`daqreader_epochdata_ingested` **carries the recorded signal itself**, as attached
files, under names the writer computes at runtime:

```
mfdaq.m:829   d = d.add_file('channel_list.bin', channel_file_name);
mfdaq.m:916   d = d.add_file([fileprefix '_group' int2str(groups(g)) '_seg.nbf_' int2str(s)], ...)
mfdaq.m:955   d = d.add_file(['evmktx_group' ...], [filename_here '.nbf.tgz']);
              prefixes: ao, ax, di, evmktx, ti
```

**For an ingested session these `.nbf.tgz` archives are the only copy of the
recording.** There are no raw files to fall back to — that is what ingestion means.

### The undeclared-file gap

```
NDI template   "files": { "file_list": [ ] }     EMPTY
V_eta          files: []                          EMPTY
the writer     add_file(...) with RUNTIME-COMPUTED names
```

**Both the source template and V_eta declare no files, while the writer attaches
them.** A migrator working from the declaration carries zero files and silently drops
the entire recording. This is a NEW variant of the silent-loss family — not an
invented field but an *undeclared* one — and **no existing detector looks for it**:
`silentLoss` checks empty required edges and vacuous required fields; the vocabulary
sweep compares field names; neither counts attached files against a declaration.

Tracked separately, because it is not specific to this family.

### It also kills R5's proposed rename

R5 (#27) proposes `*_epochdata_ingested` → `<device>_epoch_cache`. **"Cache" is
exactly wrong**: a cache is by definition rebuildable, and these files are the only
copy. A name that invites deletion of the primary data is worse than the mode-in-name
error it was fixing.

---

## THE SECOND FINDING — where the epoch's clock extents actually live

```matlab
reader.m:83-90
   et = d_ingested{i}.document_properties.daqreader_epochdata_ingested.epochtable;
   for j=1:numel(et.epochclock)                       % <- A CELL ARRAY
      ec_here{j} = ndi.time.clocktype(et.epochclock{j});
   end
   t0t1_here = et.t0_t1;                              % indexed alongside
```

`epochtable` is **one (clock, extent) pair per entry, several per epoch**. That is the
real, NDI-backed source of exactly what `acquisition_epoch.clocks` was *inventing* (the
epoch plan already flags `axes`/`channels`/`storage` as existing in no NDI template).

And it is precisely the `relative_reference` document that `clock_alignment`'s
endpoints are (`V_eta_clock_alignment_cluster_plan.md`). **The epoch, time-reference,
clock-alignment and ingested-payload families all meet here.**

Note the polynomial lesson applies: `epochclock` is a CELL ARRAY, so a single `clock`
field would be lossy in exactly the way `{slope, intercept}` would have been.

---

## THE ID-REFERENCE CHECK — clean

```
<class>_id as a dependency name, anywhere (91 templates, 1,002 .m files, DID schemas):
   daqreader_epochdata_ingested           0
   daqmetadatareader_epochdata_ingested   0
   daqreader_image_epochdata_ingested     0

templates "depending on" daqreader_epochdata_ingested:
   daqreader_image_epochdata_ingested.json    SUBCLASSES it -- inheritance, not an edge
   daqreader_mfdaq_epochdata_ingested.json    SUBCLASSES it
```

**No document points at any of the three by id.** Decomposition carries no orphan risk,
unlike the calculators.

Per the string-reference lesson, the check went further. They ARE found — by class name
plus the epoch join, never by their own id:

```
reader.m:54,72   ndi.query('','isa','daqreader_epochdata_ingested')
                   & depends_on daqreader_id & epochid.epochid
```

Retiring the class breaks those queries, but they are v1-runtime queries against v1
documents — the same category as every other rename here.

---

## WHAT EACH CLASS IS, IN PLAIN LANGUAGE

**`daqreader_epochdata_ingested`** — the recording itself, for one epoch, when the
session was ingested. Two unrelated things fused into one document: a table of when the
epoch started and ended *on each clock*, and the actual signal as attached archives.

**`daqmetadatareader_epochdata_ingested`** — the companion spreadsheet's bytes for one
epoch, preserved. Many rigs write a TSV next to the raw recording listing what happened
on each trial; `ndi.daq.metadatareader`'s own doc calls it *"a tab-separated-value file
that describes stimulus parameters."* No fields at all, one `data.bin`.

**`daqreader_image_epochdata_ingested`** — the same, for a camera: `frames.bin` plus the
raster header (dimension order `YXCZT`, sizes, dtype, frame count) and the time of every
frame.

---

## THE PROPOSAL (Claude's, not decided)

### A. `daqreader_epochdata_ingested` — DECOMPOSES, then RETIRES

Not a fold: it is two tiers fused.

```
epochtable.epochclock[i] + t0_t1[i]
   -> ONE relative_reference PER (epoch, clock)
         relative_to -> epoch;  clock (bound did_clocktype);  start; end
      >>> these ARE the clock_alignment endpoints (#57) <<<

attached files (channel_list.bin, *_group*_seg.nbf_*)
   -> sampled_body on the <modality>_observation (#30)

daqreader_id  -> the observation's acquisition_system / instrument_id (T7)
epochid       -> epoch_id edge
parameters { sample_analog_segment, sample_digital_segment }
   -> DROP. A chunked-read strategy -- the category the spike-parameters plan bags as
      one program's internals (read_time, center_range_time) -- and after decomposition
      there is no document left to bag them on.
```

Nothing survives, so the class retires. The id check above is the gate, and it passes.

### B. `daqmetadatareader_epochdata_ingested` — KEEPS a class

An earlier Claude claim that this family *"needs no new class"* was **wrong**, for a
structural reason: `sampled_body` and `opaque_body` both declare `depends_on: statement`.
A body must hang off a statement, and a per-epoch metadata blob is not an observation of
any subject. There is no statement for it to hang from.

```
metadata_file ⊂ base                                  base.id PRESERVED
   FILE: data.bin
   depends_on:
      metadata_reader_id -> metadata_reader   REQUIRED
      epoch_id           -> epoch             REQUIRED
```

A thin infra carrier — which is what it already is — repaired and renamed off the
mode-in-name.

**NAME OPEN.** Claude first proposed `ingested_payload`; the team said it seemed wrong,
and it was — it repeated the very mode word this rename removes. `metadata_file` pairs
with `metadata_reader` (the reader and the file it read). The team then asked whether
BOTH should be `acquisition_`-qualified (`acquisition_metadata_reader` /
`acquisition_metadata_file`) and has not answered; that question is recorded in
`V_eta_daq_family_decisions.md`.

**Do not type `data.bin`.** The readers produce TSV in the cases seen, but nothing
declares it. Carry the bytes; model them when someone has read real ones. Proposing a
shape from a template alone is the failure that produced the ~2,078 `distance_metadata`
quarantines and the wholly-invented `stimulus_parameter` fields.

### C. `daqreader_image_epochdata_ingested` — folds into the image model

```
frames.bin + dimension_order + dimension_size + data_type + num_frames
   -> image_observation + the `image` data_type, descriptors ALWAYS EXPLICIT
      (R6: dtype is not recoverable from the payload)

frametimes[] + clocktype
   -> the per-frame time axis; clocktype -> `clock`, bound did_clocktype

metadata[]   -> UNTYPED ARRAY. Bag it honestly or read real documents first.
daqreader_id -> acquisition_system;   epochid -> epoch_id
```

---

## WHAT THE OTHER 2026-08-06 WALKTHROUGHS CHANGED HERE

1. **`_ingested` is mode-in-name (T13)** — the same error corrected by
   `epochfiles_ingested` → `ingestion_manifest`. All three names go.
2. **R5's `_epoch_cache` is dangerous**, not merely imprecise (above).
3. **Don't narrow a shape without checking the source** — the polynomial lesson;
   `epochclock` is a cell array.
4. **`clocktype` → `clock`**, bound to the existing `did_clocktype` value_set
   (`V_eta_time_reference_model_plan.md`, amended 2026-08-06).

---

## OPEN

1. **The undeclared-file gap** is bigger than this family and needs its own detector.
2. **2,659 `daqmetadatareader_epochdata_ingested` documents have NO migrator today** and
   pass through whole.
3. **`data.bin` and `metadata[]` both need real bytes** before any typing.
4. **Two DID migrators need rework** under A and C: `migrators_i/image_stack.m:107`
   EMITS `daqreader_image_epochdata_ingested`, and
   `migrators_j/daqreader_mfdaq_epochdata_ingested.m` migrates the reader one.
5. **A cannot be built** until the time model and #30 both land — it decomposes into
   `relative_reference` documents and a `sampled_body` on an observation, and neither
   target exists yet.
