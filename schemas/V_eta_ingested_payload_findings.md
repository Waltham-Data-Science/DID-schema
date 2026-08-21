# V_eta — the daq ingested-payload family (DECIDED; build deferred)

**DECIDED with the team 2026-08-06; SIGNED OFF 2026-08-08 — the `TEAM-SIGN-OFF
[daq ingested payloads]` line is at the bottom of this document. Build still
deferred.**

<!-- HISTORICAL-SIGNOFF-CLAIM -->
*This header asserted "NO `TEAM-SIGN-OFF` LINE" until 2026-08-10, two days after
the signature was added below it. Corrected; see the note in
`V_eta_stimulus_parameter_plan.md` for why this class of staleness is now
CI-gated.*

**The team's words:** *"I accept the suggested naming acquisition_metadata_reader /
acquisition_metadata_file. You can mark that family decided."*

Recorded first as findings-plus-proposal and adopted in the same session; the findings
below are measurements, the model was Claude's and is now the team's.

Covers `daqreader_epochdata_ingested`, `daqmetadatareader_epochdata_ingested`,
`daqreader_image_epochdata_ingested`.

---

## GROUND TRUTH

```
DENOMINATOR   91 NDI templates on origin/main;  1,002 .m files
RE-DERIVED 2026-08-13: 91 NDI templates on origin/main; 1,003 .m files. The did_v1 ground truth did NOT move -- 0 template diffs across the NDI main merge, still 91; main gained one .m file, so only the denominator shifted. RE-DERIVED AGAIN 2026-08-15: 91 NDI templates on origin/main; 1,005 .m files. NDI main moved to 928b1cd5 and two of its nine commits add test .m files (closeAndRemoveDir.m, TestRayoLabStims.m). The did_v1 ground truth is STILL unmoved -- 91 templates, 0 diffs; only the denominator shifted.
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

## THE MODEL

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
acquisition_metadata_file ⊂ base                      base.id PRESERVED
   FILE: data.bin
   depends_on:
      acquisition_metadata_reader_id -> acquisition_metadata_reader   REQUIRED
      epoch_id                       -> epoch                         REQUIRED
```

A thin infra carrier — which is what it already is — repaired and renamed off the
mode-in-name.

**NAME DECIDED 2026-08-06: `acquisition_metadata_file`**, paired with
`acquisition_metadata_reader`. Claude first proposed `ingested_payload`; the team said
it seemed wrong, and it was — it repeated the very mode word this rename removes. The
full reasoning, including why the "metadata" name-collision argument turned out weak,
is in `V_eta_daq_family_decisions.md`.

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

---

## SIGNED OFF 2026-08-08

TEAM-SIGN-OFF [daq ingested payloads]: jess@walthamdatascience.com / 2026-08-08 -- ONE new class, `acquisition_metadata_file`; the reader and image classes RETIRE by decomposing into relative_reference + sampled_body + image_observation, all of which are now themselves signed.

### The classes, as signed

```
acquisition_metadata_file ⊂ base                     base.id PRESERVED
   (NO FIELDS -- its entire content is the file)
   FILE  data.bin                                    REQUIRED
   depends_on
      acquisition_metadata_reader_id -> acquisition_metadata_reader   REQUIRED
      epoch_id                       -> epoch                         REQUIRED

daqreader_epochdata_ingested          RETIRES (decomposes)
daqreader_image_epochdata_ingested    RETIRES (decomposes)
```

It cannot be a `data_body`: both body classes depend on a `statement`, and a per-epoch
metadata blob is not an observation of any subject. That reasoning survives the 2026-08-08
data_body rework unchanged.

### THREE REVISIONS from decisions taken the same day — the plan above is superseded on these

**1. `t0_t1` -> `start` + `duration`, NOT `start`/`end`.** The time model signed
2026-08-08 replaced `end` with `duration`, so an ingested epoch extent becomes an anchor plus
an extent with INDEPENDENT `approximate` flags — a distinction the old shape could not express
("approximately 10 hours after, exactly 60 minutes long").

**AND `epochclock` may mean NO DOCUMENT AT ALL.** `no_time` left the clocktype vocabulary the
same day, and `migrators_i/image_stack.m:199` shows an ingested epoch can carry exactly that
(`if isempty(clockName); clockName = 'no_time'; end`). Under **NO TIMES => NO REFERENCE**,
those emit no `relative_reference` rather than a NaN one.

**2. The image fold goes through the AXIS ENTRY, and `clocktype` does not land on the axis.**
This document says *"`frametimes` + `clocktype` -> the per-frame time axis; `clocktype` ->
`clock`, bound did_clocktype"*. Under the data_body decision an axis has a `variable` and **no
clock** — the clock lives on the time reference. So:

```
frametimes       -> the time axis's `values` (irregular) or origin/spacing (regular)
clocktype        -> the EPOCH's relative_reference, NOT the axis
dimension_order  -> the ORDER OF THE axes[] ENTRIES, not a string
dimension_size   -> each axis's `n`
data_type        -> `datum_type` ON THE STATEMENT (via the class(x) normalisation map)
num_frames       -> the time axis's `n`
```

**3. The `.nbf.tgz` archives now have somewhere to record that they are compressed.**
`data_body.format` + `compression` landed 2026-08-08. NDI's own comment — *"Our payloads are
already compressed archives (.zip, .nbf.tgz)"* (`GetFile.m:61`) — previously had no home and
was lost at migration.

### REPAIRED IN THE BUILD during this review, not deferred

`daqmetadatareader_epochdata_ingested` declared `file: []` in BOTH V_zeta and V_eta while NDI
declares `data.bin` REQUIRED in both the template and the schema document — on a class with no
fields, so it declared nothing it carries, across 2,659 documents. **#64's gap INVERTED**: not
an undeclared attachment but a declared file V_eta stopped declaring. And unlike `depends_on`,
nothing skips an empty `file`, so `mustBeNonEmpty` here is not the decorative case.
Restated through `_tombstone` from the real template; 226 schemas, 497 tests green.

### Gates carried, none waived

1. **A cannot be built until #65 and #30 land** — it decomposes into `relative_reference`
   documents and a `sampled_body` on an observation.
2. **R5's `_epoch_cache` rename stays REJECTED**, not merely deferred: for an ingested session
   those archives are the ONLY copy of the recording, and "cache" invites deleting primary data.
3. **The undeclared-file gap (#64) is unfixed** — `daqreader_epochdata_ingested` still declares
   no files while `mfdaq.m:829,916,955` attaches the recording under runtime-computed names.
4. **`data.bin` stays UNTYPED.** The readers produce TSV in the cases seen; nothing declares it.


RE-DERIVED 2026-08-21 (ndi_m_files, `check_prose_counts`): 91 NDI templates on origin/main; 1,012 .m files (`git ls-tree -r origin/main | grep -c '\.m$'` = 1012 at 5df51cf9; +7 since the 1,005 reading). The did_v1 ground truth is STILL unmoved -- 91 templates, 0 template diffs; only the denominator shifted.
