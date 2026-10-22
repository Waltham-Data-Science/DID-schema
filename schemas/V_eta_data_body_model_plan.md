# V_eta — the data_body model: axes, datum, and the encoding fields (DECIDED; build deferred)

**DECIDED with the team, 2026-08-08, in the coordinates walkthrough. SIGNED 2026-08-14**
— the signature is at the bottom of this file, under "SIGNED OFF 2026-08-14".

> ## READ THIS BEFORE ACTING ON ANYTHING BELOW
>
> This document was SIGNED and then AMENDED TWICE on 2026-08-14. **Three claims in
> the body below are superseded** and are marked in place where they sit, but a
> reader who skims will still meet the old text first — which is the failure this
> repository has already paid for once ("A PLAN DOCUMENT'S HEADER IS NOT ITS
> STATE. READ THE BOTTOM, OR READ THE BOARD").
>
> | at the bottom of this file | what it changes |
> |---|---|
> | `SIGNED OFF 2026-08-14` | the signature, and what it does NOT cover |
> | `ADDENDUM — the storage-mode walkthrough` | closes OPEN items 3, 4 and 7; a body is emitted only when bytes are attached; axes live with the thing whose extent they describe |
> | `AMENDMENT 1 — the axis carries its own unit` | **REVERSES** `THERE IS NO \`unit\` FIELD`; angles are radians; #32 and #115 leave the critical path |
> | `AMENDMENT 2 — conditions reaches format parity` | restructures `conditions`: four descriptors move up, `count` flattens |
> | `AMENDMENT 3 — one entry for keys, conditions and method parameters` | renames the value forms: a key's `labels`/`values` become `term`/`quantity`; a condition's `term.value`/`count.value` flatten (2026-10-19, decided with Jess; built) |
> | `AMENDMENT 4 — a \`matrix\` value form` | a condition or method parameter may hold one numeric N-D array (`matrix`); noise colours are `NCIT:C75765` Arbitrary Unit plus a bit-depth count (2026-10-21, Jess; PROPOSAL built ahead of signature) |
> | `AMENDMENT 5 — a value is inline or in bodies, never neither` | ONE rule on `value` (`value_inline_or_body`) replaces the required inline `value` of nine classes; a `receptive_field` can now be body-backed; a statement may also take its value through `value_id` (2026-10-21, Jess; signed; built) |
>
> **The axis entry has NO remaining prerequisite.** Anything below that says
> otherwise is superseded.
>
> **BUILD STATUS, 2026-09-25 (#73 review):** build step 5 is DONE -- `sample_time` is
> retired from both schema sites (`sampled_body` earlier, `subject_interaction` now), and
> the composites' documentation points at the time key instead. Emitters still write it
> (NDI + DID-matlab sites listed in step 4) -- PR #76 checklist.
>
> **AND AMENDMENT 2 is BUILT (#73 item 23):** `conditions` has the four descriptors at the top
> of each entry, `count` flattened, `quantity` as {value, source_value}.
>
> **AND THE LIGHTSHEET WALKTHROUGH (2026-09-25, NDI-matlab PR #979; agreed with jess, NOT
> signed; record in `review/73/OPEN_ITEMS.md` L1–L4) changed the tier, and is BUILT
> schema-side:** the two bodies split by WHO LAYS OUT THE BYTES — `sampled_body` = raw bytes
> V_eta lays out (`byte_order`, `datum_order`, `chunk`, new `fill_value`); `opaque_body` =
> bytes laid out by their own `format`. `keys`, `complete` and the `key_labels_id` edge moved
> UP to `data_body` (keys required on a sampled body, optional on an opaque one, `chunk` only
> on a sampled one), and `conditions` was added there too (a one-value fact true of one
> body's values only). Keys are EXACTLY the stored array's dimensions; any other one-value
> fact is a condition. Edge chunks are stored at full chunk shape (positions past `n` are
> padding); a dense body's missing member holds `fill_value`. **Sec.7's open question is
> answered:** the first real per-chunk codec (Blosc + zstd + shuffle) is self-describing —
> checked with python-blosc 1.11.4, `decompress` with no parameters round-trips — so one
> `compression` value holds (the MATLAB encoder NDI calls is not yet checked).

Owns TaskList **#45**. Supersedes the `axes[]`-only framing of that task: the walkthrough
started at "where do coordinates go" and ended at the whole `data_body` tier, because every
field on `sampled_body` turned out to be either half-built, ambiguous between writers, or
holding a fact that belongs somewhere else.

Gates **#46** (ngrid retirement), which was held pending exactly this.

---

## GROUND TRUTH

```
DENOMINATOR   224 V_eta document classes, 896 field nodes
              263 DID-matlab .m files;  915 NDI-matlab .m files
              5 corpora (20211116, B, Dab, JH, Soph), 221,813 v1 documents
```

### The three classes as they stand

```
data_body    (draft) ⊂ data          depends_on: []      file: body_data    FIELDS: NONE
opaque_body  (draft) ⊂ data_body     depends_on: statement  mustBeNonEmpty FALSE
                format / filename / description
sampled_body (draft) ⊂ data_body     depends_on: statement  mustBeNonEmpty TRUE
                                                  filter_id            FALSE
                datum { kind, dtype, unit, shape }
                sample_time { regular, t0(duration), dt(duration), n, offsets }
                summary { value: {}, time: {} }
                axes[] { name, kind, length, regularity, spacing, unit }
                content_hash
```

`data_body` carries nothing. The `statement` edge is declared on **both** children with
**opposite** required-ness — same edge, same referent, two answers, and under #37 neither is
enforced.

### What is actually populated

```
sampled_body.axes[]     ZERO writers.  jSampledBody -- the shared skeleton for every
                        body-backed fold -- builds datum + sample_time + summary and no axes.
sampled_body.summary    ONE writer, writing nothing:
                           jSampledBody.m:30  'summary', struct('value',struct(),'time',struct())
                        ZERO readers in either repo.
content_hash            ZERO writers, ZERO readers. Two comment lines in NDI
                           (stimulusPresentationToManipulation.m:19,111) note that something
                           else is expected to fill it in. Nothing does.
datum                   FOUR writers, THREE readers (all test assertions), no production reader.
```

Four never-populated things on one class.

### The three encodings of one distinction

```
subject_interaction.sample_time.kind    char     point | grid | enumerated
sampled_body.sample_time.regular        boolean  regular grid vs enumerated
sampled_body.axes[].regularity          char     regular | irregular
```

Plus a fourth spelling of the same fact one level up: `acquisition_epoch.axes.sample_rate` is
typed `frequency` while `sampled_body.sample_time.dt` is typed `duration` — the same quantity
stored as a rate in one place and a period in the other.

And three unrelated fields named `kind`: `datum.kind` (scalar|array|record),
`axes[].kind` (a quantity vocabulary, **prose only** — `constraints {}`), and
`subject_interaction.sample_time.kind` (the regularity enum). Same trap as `mode` meaning two
different things in the time family.

### `axes[]` cannot store what it declares

`regularity: irregular` is declarable and there is **nowhere to put the coordinates**.
`sample_time` got the same case right with `offsets`. There is also **no `origin`**, so even a
*regular* axis cannot say where it starts — the regular case is reconstructible only by
convention (T14), not by declaration.

---

## THE DECISION

### 1. One axis entry, replacing all three encodings

```
axis
   variable        ontology_term  REQUIRED   what varies along this dimension;
                                             UNIQUE within the list. Its dimension and
                                             canonical unit come from the D9 registry --
                                             the same contract as conditions.quantity.
                                             THERE IS NO `unit` FIELD.
                                             ^^^ SUPERSEDED 2026-08-14 by
                                             AMENDMENT 1 at the bottom of this
                                             file: the axis DOES carry `unit`,
                                             as a bound `ontology_term`. Do not
                                             act on this line.
   source_unit     char           optional   the unit exactly as the source gave it
   approximate     boolean        optional   applies to the whole axis
   n               integer        REQUIRED
   regular         boolean        REQUIRED

   origin   { value, source_value }      REQUIRED iff regular
   spacing  { value, source_value }      REQUIRED iff regular
   values   { values, source_values }    REQUIRED iff NOT regular, numeric
   labels   ontology_term[]              REQUIRED iff NOT regular, categorical
```

```
RULE  `value` / `values` are in the canonical unit the D9 registry gives for `variable`.
RULE  any source_* is OMITTED when the source unit is already canonical.
RULE  axes[k] IS array dimension k. Array order IS the dimension order.
RULE  n equals the extent of the value this axis indexes.
RULE  values XOR labels.
```

`kind`, `regularity` and `length` go. `name` goes — its examples (`'contrast'`,
`'orientation'`) *are* variables, and `conditions`, the live axis mechanism, carries exactly
one identifier. A free-text `name` beside a bound `variable` is the escape hatch that makes
the binding pointless. Uniqueness of `variable` is what makes "which axis is X" well defined.

`point` becomes `n == 1` — cardinality, the same argument the time_reference collapse turned on.

### 2. Time is an ordinary axis

Both `sample_time` blocks are replaced by an `axes[]` entry whose `variable` is the time term.
`regular -> regular`, `t0 -> origin`, `dt -> spacing`, `n -> n`, `offsets -> values`. Nothing is
lost, `t0`/`dt` rise to the right altitude (T13), and the rate-vs-period drift resolves — an
axis stores `spacing` in its own quantity, so `sample_rate` goes away.

**This is a CROSS-REPO change.** NDI-matlab writes `sample_time` in three places
(`+migrate/+internal/stimulusPresentationToManipulation.m:16,108`,
`stimulusBathToBath.m:120`, `tests/+migrate/TestPathSPromotion.m:124,148`), on top of 17 DID
files. The string-reference sweep found this; a structural sweep would not have.

### 3. `axes[]` mounts twice, and it is NOT duplication

```
storage_mode: inline   ->  subject_statement.axes[] populated;  no bodies
storage_mode: body     ->  each sampled_body.axes[] populated;  statement.axes[] EMPTY
```

Mutually exclusive, and **checked** — unlike today, where nothing stops both `sample_time`
blocks being filled. This is not a new pattern; it is what `sample_time` already does
(`subject_interaction.sample_time` and `sampled_body.sample_time`). Two `sample_time` blocks
become two `axes[]` blocks.

Statement-only does not work, and `pyraview` is the proof — one observation, N bodies, a
different rate and start per body:

```matlab
% Levels are told apart by sample_time.dt (the per-level sampling rate); level 1 is native.
for k = 1:numel(fileList)
    rate_k = ...;  dt_k = 1.0/rate_k;  t0_k = starts(k);        % PER LEVEL
    b = jSampledBody(..., struct('kind','array','dtype',dataType,'unit','','shape',channels), ...
        struct('regular',true,'t0',durationComposite(t0_k),'dt',durationComposite(dt_k),'n',0));
```

`dt_k`/`t0_k` are indexed by `k`; `dataType`/`channels` are not. **Extent varies per body;
element type is constant per statement.** That is why the two fields mount differently — it is
read off the writer, not chosen for tidiness.

### 4. `conditions` is NOT an axis — the D10 sentence is amended

> **STILL TRUE, AND RESTRUCTURED 2026-08-14 (AMENDMENT 2).** `conditions` is
> still NOT an axis and merging the two was NOT reopened. What changed is its
> SHAPE: `variable`, `unit`, `source_unit` and `approximate` move up to the top
> of the entry (matching the axis), and `count` flattens. Read AMENDMENT 2
> before writing a `conditions` field.

The declaration says:

> *"A condition whose value is a per-reading ARRAY is the independent-variable axis (e.g. a
> tuning curve's direction); a length-1 value is a held-fixed covariate — **same kind of thing,
> distinguished only by cardinality**."*

That is wrong, on positive evidence:

1. **The schema already puts the commonest axis outside `conditions`.** A body's time axis is a
   dimension and lives in `sample_time`, never in `conditions`. If axis-ness were just a long
   condition, time would be a condition.
2. **Two structurally identical documents mean different things.** A per-reading array can be a
   *coordinate* (element k indexes response element k) or a *co-measurement* (element k merely
   co-occurs). Both legal, both length-N, indistinguishable.
3. **The code was written under the covariate reading.** `jTuningFold` never checks that the
   independent and response arrays are the same length — the equality that would make it an
   axis is asserted nowhere.

Collapsing a *cardinality* is safe (`point`); collapsing a *coincidence* is not. Covariate and
axis coincide at n=1 and are different relationships either side of it.

```
subject_statement.conditions[]     WHAT WAS TRUE of the whole statement
   cardinality: EXACTLY 1
   variable   ontology_term  REQUIRED
   EXACTLY ONE OF:
      term      { value: ontology_term }
      count     { value: integer, unit: ontology_term, approximate }
      quantity  { value, source_value, source_unit, approximate }
```

`quantity` gains the canonical `value` it currently lacks — it is the only dimensioned
representation in the schema with a source side and no canonical side.

The test, in one line: **does element k of this entry say something about element k of the
value? Yes -> axis. No -> condition.** A per-reading co-measurement is neither; it is a
statement in its own right about the same subject with the same time reference (T4).

### 5. `datum` collapses to a type, and the type moves to the statement

```
unit    EMPTY at 4 of 4 writers. Under the registry decision the value's unit comes from
        subject_statement.variable + D9, exactly as an axis's does.            GOES.
shape   The writers DISAGREE about what it means. The declaration says "array only:
        intra-datum dims" and three writers honour it; NDI's writes [nTrials,7] alongside
        sample_time.n = nTrials, so the sample dimension is counted twice -- and
        TestStimulusPresentation.m:35 locks the wrong reading in. Once axes[] is populated
        the payload shape is [axes.n] in array order.                          GOES.
kind    scalar = one axis, array = more. `record` appears once, and it is dtype 'double'
        over [nTrials,7] -- a homogeneous matrix whose 7 columns are the grating
        parameters, i.e. a LABELLED CATEGORICAL AXIS, not a record. A genuinely
        heterogeneous record is unrepresentable anyway (one dtype field).       GOES.
dtype   R6 already settled that dtype is not recoverable from the payload.     STAYS.
```

`record`'s one real use becoming a labelled axis is the **second** independent justification
for `labels`; the first is the Hartley plane axis (§8).

```
subject_statement
   datum_type          char   REQUIRED, BOUND to the 14-value vocabulary
   source_datum_type   char   optional; the source's spelling, OMITTED when identical
```

**Named `datum_type`, not `data_type` and not `element_type`.**

- `data_type` is **taken**: it is a class with **41 direct subclasses** (acceleration, angle,
  concentration, duration, image, length, voltage, …) — tier ③. The five fields spelled
  `data_type` today (`ngrid`, `pyraview`, `binaryseries_parameters`,
  `daqreader_image_epochdata_ingested`, `acquisition_epoch.storage`) all sit on v1 classes on
  their way out; every V_eta-native site already spells it `dtype`.
- `element_type` collides with v1's `element` — **95 of 915 NDI files mention it, 223 hits for
  `element_id` / `ndi.element` / `@element`.** `element_type` reads as "the type of the
  element (probe/neuron)", a question v1 genuinely asks with a different answer.
- `datum` has **zero** v1 meaning: 3 NDI hits, all our own migration code. And
  `datum.dtype -> datum_type` is a flattening of the existing path, not a new word.

**BOTH FIGURES IN THE THREE BULLETS ABOVE WERE RE-DERIVED 2026-08-12 AND BOTH HAVE MOVED.
THE ARGUMENT SURVIVES BOTH — one of the two is now STRONGER — so the bullets keep their
reasoning and only the numbers are corrected, here, beside them.**

**WHY HERE, AND NOT ONLY IN `CLAUDE.md`.** That file corrected these same two numbers
earlier the same day, inside its one-paragraph summary of THIS plan. The correction landed
in the file that QUOTES the fact and never reached the file that STATES it, so a reader of
this document had no way to know a correction existed two files away, and would have gone
on quoting 38 subclasses and a 915-file NDI tree indefinitely. **A correction is only where
it is written.**

**(1) `data_type` now has 41 direct subclasses, not 38 — and the bullet's case gets
STRONGER, which is worth more than the digit.** Derived from the built tree:

        DENOMINATOR: 247 json file(s) under schemas/V_eta/ read
        RE-DERIVED 2026-08-15: 247 json file(s) under schemas/V_eta/. This read 248 on 2026-08-13, when `acquisition_reader` was minted; the step-2 data_body build then DELETED `zarr` (signed sec.10 -- a V_gamma invention with no v1 source), so the count went +1 then -1 and is back where it started.
        classes declaring `data_type` as a DIRECT superclass: 41
           acceleration amount angle angular_velocity area capacitance charge chemical
           concentration conductance contrast_sensitivity count current date dose
           duration energy force formulation frequency gain harmonic_component image
           intensity length logical mass ph polynomial power pressure resistance score
           temperature term timed_sequence tuning_curve velocity visual_grating voltage
           volume

The bullet's case is *"`data_type` is TAKEN, so `datum_type` cannot reuse the name"*, and
the count moved UP: the name is spoken for by three more classes than when the walkthrough
ran (`logical`, `timed_sequence` and `tuning_curve` are among the arrivals). **A "this name
is already taken" argument cannot be weakened by the name being taken more.** §5 stands
unchanged; this is a figure correction, not a re-opening.

**(2) The NDI denominator said 915 and is now 1,002 — but the `element_type` bullet's
NUMERATOR IS NOT REPRODUCIBLE, so it is MARKED rather than restated.**

        $ git -C NDI-matlab ls-tree -r --name-only origin/main | grep -c '\.m$'
        1002

i.e. `git ls-tree -r origin/main | grep -c '\.m$'` = **1002**, a denominator of 1,002 NDI
files on `origin/main`.

RE-DERIVED 2026-08-13: 91 NDI templates on origin/main; 1,003 .m files. The did_v1 ground truth did NOT move -- 0 template diffs across the NDI main merge, still 91; main gained one .m file, so only the denominator shifted.
RE-DERIVED AGAIN 2026-08-15: 91 NDI templates on origin/main; 1,005 .m files. NDI main moved to 928b1cd5 and two of its nine commits add test .m files (closeAndRemoveDir.m, TestRayoLabStims.m). The did_v1 ground truth is STILL unmoved -- 91 templates, 0 diffs; only the denominator shifted.

**The bullet is NOT rewritten to read `95 of 1002`, and that is deliberate.** No reading of
"hits" reproduces its `223` / `95` — `CLAUDE.md` records the three that were tried:
substring `element` gives 1780 hits across 177 files, word-boundary `\belement\b` gives 765
across 128, quoted `'element'` gives 25 across 13. Pairing a freshly derived denominator
with a numerator nobody can re-derive would manufacture precision the measurement never had
— a number that LOOKS checked and is not, which is the failure this project pays for most
often. **What the bullet needs from those figures is a THRESHOLD, and every available
reading clears it by an order of magnitude, so `element_type` stays rejected on exactly the
grounds given.** Operating Rule 5 asks for a denominator; this is the case that shows it
does not also ask for the NUMERATOR'S METHOD, and that is the gap both halves escaped
through. If the claim is ever needed as a number rather than as a threshold, re-measure it
and write the command down beside it.

Both were found by `tools/check_prose_counts.py`, which derives the quantities from the
tree and the generated artifacts instead of reading prose about them.

### 6. The bytes tier — what moves to `data_body`

**The rule: the statement says what the values ARE; the body says how the bytes ENCODE them.**

```
data_body   (abstract; everything about the BYTES)
   format         char   container / MIME format of the carried bytes   (was opaque_body.format)
   compression    char   compression applied within or around that format          NEW
   filename       char   original filename of the payload, if any        (was opaque_body)
   content_hash   char   hash of the payload bytes -- MUST STATE WHICH bytes,
                         compressed or decompressed; ambiguous today     (was sampled_body)
   description    char   human description of the payload               (was opaque_body)
   depends_on     statement -> subject_statement    ONE required-ness, settled here
   file           body_data

sampled_body ⊂ data_body   (how the bytes lay out as an array)
   byte_order     char   'little' | 'big'   REQUIRED when datum_type is multi-byte
   datum_order    char   'C' | 'F'          REQUIRED when there is more than one axis
   axes[]
   depends_on     filter_id -> frequency_filter  (optional)

opaque_body ⊂ data_body
   (nothing of its own -- its content is "these bytes are not an array", which the class
    name states. `data_body` has EXACTLY two members; that is not reopened.)
```

`byte_order` / `datum_order`, not `endianness` / `chunk_order`: two orders at two nesting
levels — bytes within a datum, data within the array — named the same way, and readable
without a glossary. (`zarr` spells its own field `endianness` and uses `endian` only where it
transcribes zarr v3's literal codec key.)

### 7. Encoding: `format` + `compression`, and NOT zarr's codec pipeline

This is not new scope. The 2.D collapse already decided *"every format carrier phases into
sampled_body/opaque_body (**encoding becomes a field**)"*, and the field was never built.
`migrators_j/image.m:51-56` documents the deferral in its own header: v1 `image.format` +
`image.compression` (`'tiff'`, `'lzw'`) *"have no home yet … It should land with the data_body
encoding field."* This is that field.

Compression is live, and it is not the kind `zarr` models:

```
1. container / archive        .nbf.tgz, .zip     LIVE  (NDI mfdaq.m:917,942,955,967;
                                                  metadatareader.m:144; GetFile.m:61
                                                  "Our payloads are already compressed
                                                  archives (.zip, .nbf.tgz)";
                                                  spike_interface_sorting_outputs .zip)
2. format w/ internal compression   tiff + lzw   LIVE  (v1 image)
3. per-chunk array codecs     blosc/zstd/gzip    NO INSTANCE  (zarr.codecs[])
```

Copying `zarr.codecs[]` would model the case that does not occur and miss the two that do —
the shape-from-a-template error that produced the ~2,078 `distance_metadata` quarantines.

**One `compression` char is enough for the requirement.** To *read* bytes you need the
transform chain; level, blocksize, checksum and shuffle are *write-time* parameters, and gzip /
zstd / blosc streams self-describe what a decoder needs. We never re-compress a migrated
archive — these are archival payloads. zarr models the pipeline because zarr *writes* chunks.
The one thing that would break a single char is a multi-step pipeline with a
non-self-describing step (blosc shuffle); there is no instance. If the vocabulary sweep finds
one, promote `compression` to an ordered list.

**Do NOT bind `format` or `compression` yet.** The observed values are `tiff`, `lzw`,
`.nbf.tgz`, `.zip`, `application/pdf`, `image/tiff` — two vocabularies (bare tokens and MIME
types) needing reconciliation, and the full set is unknown. Sweep the corpus first, bind second.

### 8. `labels`, and the Hartley plane axis

`V_eta_ngrid_family_findings.md` F2/F3, from the writer at `65718ed`:

```
the .ngrid file is a 4-D [T × X × Y × 2] double array:
   plane 1 = spike-triggered average, plane 2 = per-voxel p-value map
hartley.m:443   ngridp.coordinates = [ T_coords(:); X_coords(:); Y_coords(:) ];
```

The writer enumerates coordinates for **three** axes. The plane axis is **unlabelled in the v1
document** — "plane 1 is STA, plane 2 is p-value" lives only in the writer's code.

So the migrator **supplies** the labels from writer semantics. Under the ground-truth rule
(*where template and writer disagree, the WRITER wins*) that is transcription, not invention,
and it is the same call R6 already made for dtype. Without it, which plane is which stays
structure-by-convention — what T14 exists to stop.

**Caveat on the record:** this is the read from the prior session's shallow clone of
`VH-Lab/NDIcalc-vis-matlab` @ `65718ed`, not a fresh one. The repo is out of session scope and
`add_repo` was not approved this session. Re-verify before the build.

### 9. `summary` is DROPPED, not deferred in place

Tracked as TaskList **#68**. `summary.time` is not coming back: it restates the time axis entry,
and did2 **can** query array elements numerically —
`+did2/+database/compileQuery.m` compiles `lessthan` / `lessthaneq` / `greaterthan` /
`greaterthaneq` on a `[*]` path to real SQL against `queryable_array_elem.value_num`
(`splitPathOnStar` + `buildArrayJoin` -> `json_each` + `EXISTS`).

> **CORRECTION recorded here so it is not repeated.** An earlier turn in this walkthrough
> claimed numeric predicates inside an array of structs silently match everything. That was read
> off `+did/+datastructures/fieldsearch.m` — the **legacy** layer — and does not describe the
> V_eta query surface. The residual limitation is narrower: each `[*]` predicate is its own
> `EXISTS`, so a numeric subfield cannot be ANDed with a string subfield of the SAME element
> ("the axis whose variable is time AND whose origin < T" degrades to "some axis is time AND
> some axis starts before T"). Per-element conjunction exists only for string subfields, via
> `hasanysubfield_*_string` with cell-valued `param1`/`param2`.

`summary.value` is the one rollup that genuinely cannot be derived from the document (the values
live in a file), but a "per-type value rollup" depends on `datum.kind`, and min/max means
nothing for a record. It needs a discriminated design of its own. Carrying an empty structure
on every body until someone does that work is what `isFragment` and `silentLoss` exist to catch.

### 10. `zarr` is DELETED, not migrated

```
V_eta_class_provenance.md:279   | zarr | stable | V_gamma | J dim abstract |
V_eta_coverage_ledger.md:3      "Post-v1 DID intermediate classes (zarr, directory, the
                                 *_observation leaves, ...) are V_eta TARGETS, not v1 sources"
DID-matlab, 263 .m files        migrators referencing zarr:  ZERO
build_v_eta.py:3485-3487        "an orphaned abstract storage-format descriptor (nothing
                                 subclasses it) ... pending the corpus confirming no zarr docs."
build_v_eta.py:3492             _RET_CARRIERS = {"zarr", "pyraview"}
```

A V_gamma-era DID invention: no v1 source, so no v1 document can become one; no migrator emits
or consumes it; its two subclasses (`ephys_zarr`, `image_zarr`) were already deleted in the 2.D
pass. The only thing on it anyone needs is the encoding vocabulary, and that is copied onto
`data_body` — **copied, not referenced: 0 of 224 classes use `$ref`.**

**The stated gate still runs.** "Pending the corpus confirming no zarr docs" is a formality
given no writer exists, but it is the project's own gate, and waiving it is the shape of
reasoning that produced the "all 0-usage, safe to delete" errors (3 of 4 wrong).

---

## WHAT IS BOUND, AND WHAT IS CHECKED

```
BOUND    datum_type              the 14-value vocabulary, DECLARED ON data_body
                                 (copied from zarr.dtype: uint8 uint16 uint32 uint64
                                  int8 int16 int32 int64 float16 float32 float64
                                  complex64 complex128 bool)
BOUND    byte_order              little | big     -- `native` is NOT carried: it means
                                 "whatever machine wrote it", i.e. the fact you need and
                                 do not have once the file moves. A stored `native` is a
                                 hollow value.
BOUND    datum_order             C | F
BOUND    variable (axes + conditions)   via the D9 registry -- #32. A HARD PREREQUISITE:
                                 with no unit field, the registry is the only thing that
                                 says what the numbers mean.
NOT BOUND YET  format, compression      sweep the corpus for real values first.

CHECKED  axis.n == the extent of the value it indexes
CHECKED  every conditions value length == 1
CHECKED  variable unique within a list
CHECKED  regular => origin+spacing present, values/labels absent
CHECKED  NOT regular => values XOR labels, origin/spacing absent
CHECKED  source_* absent when the source unit is canonical
CHECKED  storage_mode inline => statement.axes populated and no bodies;
         storage_mode body   => statement.axes EMPTY and each body carries its own
```

---

## BUILD ORDER

```
1.  #32   bind `variable`. PREREQUISITE, not parallel work.
2.  schema: the axis entry; axes[] on subject_statement and sampled_body; conditions
    tightened to cardinality 1; datum -> datum_type on the statement; the data_body
    hoist (format, compression, filename, content_hash, description, the statement edge);
    byte_order + datum_order on sampled_body; summary deleted; zarr deleted (gated).
3.  DID-matlab
       jTuningFold.m:53            independent variable moves conditions -> axes; gains the
                                   numel(indep) == numel(response) check
       electrode_offset_voltage.m:90  stays in conditions; its DELIBERATELY empty unit
                                   ("Unit deliberately left unstated") must be recovered
                                   from the writer before `variable` can be bound
       image_stack.m:257 imageAxes rebuild: per-axis variable instead of a dimension_order
                                   letter and ONE dimension_scale_units string applied to
                                   every axis -- including the channel and time axes
       image_stack.m:121 / pyraview.m:114 / jrclust_clusters.m:71   datum -> datum_type
       jrclust_clusters.m:71       writes dtype '' -- must supply a real type
       pyraview.m:117              writes 'n', 0 on every body with real bytes attached --
                                   must derive the per-level length
       jSampledBody.m              emits axes; stops emitting the empty summary
       jMeasureArray.m             stops copying the unit once per reading (it writes one
                                   {source_unit,source_value,approximate} PER READING: a
                                   16-direction tuning curve stores 'deg' sixteen times)
       ngrid migrator              stops rmfield'ing coordinates
4.  NDI-matlab -- CROSS-REPO, found by the string-reference sweep
       +migrate/+internal/stimulusPresentationToManipulation.m:98,108
       +migrate/+internal/stimulusBathToBath.m:120
       tests/+ndi/+unittest/+migrate/TestPathSPromotion.m:124,148
       tests/+ndi/+unittest/+migrate/TestStimulusPresentation.m:35
5.  retire sample_time from both schema sites.
```

### The datum_type normalisation map

From the writer (`NDI +ndi/+fun/+data/mat2ngrid.m:38-44`):

```matlab
ngrid.data_size = props.bytes/numel(x);
ngrid.data_type = class(x);        % MATLAB class name
if islogical(x); ngrid.data_type = 'ubit1'; end
```

```
int8 int16 int32 int64          identical    -> source_datum_type omitted
uint8 uint16 uint32 uint64      identical    -> source_datum_type omitted
double     -> float64                        -> source 'double'
single     -> float32                        -> source 'single'
logical    -> bool                           -> source 'logical'
ubit1      -> bool                           -> source 'ubit1'
char       -> DECISION: no canonical in the 14
complex    -> DECISION: MATLAB has no complex class name; complex data arrives as
              'double' and the imaginary part is invisible to class(x)
```

`image_stack` and `pyraview` pass `data_type` through verbatim, so **the moment `datum_type` is
bound, every migrated image and pyraview body fails validation** — `double` is not in the enum.
That is the binding working, but it is planned work, not a CI surprise. `image_stack` also has
`firstNonEmpty(dataType, 'uint16')`, so a silent default is not hypothetical.

Keeping `source_datum_type` is not symmetry for its own sake: the map is **not invertible**
(`bool` maps back to `logical` *or* `ubit1`; `char` has no canonical at all), and retaining the
source spelling makes the map **auditable** — you can query the corpus afterwards and verify
every `float64` came from a `double` rather than from a default.

---

## OPEN

1. **[SUPERSEDED 2026-08-14 -- AMENDMENT 1. #32 is NOT a prerequisite; the axis
   carries its own `unit` and the registry becomes a VALIDATION follow-up. The
   text below is kept for its reasoning only.]** #32 is a hard prerequisite, not adjacent cleanup. This puts a bound vocabulary on every
   axis of every sampled body — the most-instantiated bound field in the schema — and
   `binding` is enforced by nothing today (`validateConstraints` handles only
   maxLength/minLength/minimum/maximum/enum).
2. **`format` / `compression` vocabularies** need a corpus sweep before binding.
3. **[CLOSED 2026-08-14 — see the walkthrough addendum.]** **`content_hash` must state which bytes** it hashes, now that compression is declarable.
4. **[CLOSED 2026-08-14 — see the walkthrough addendum.]** **THREE axes declarations, not two.** `image.value.axes` is a third shape —
   `{name, length, spacing, unit}`, four fields, no regularity, no coordinates — and is in
   scope for this decision.
5. **The Hartley plane read is from the record, not a fresh clone** (§8).
6. **`char` and complex datum types** are decisions, not mappings, and want a corpus check for
   whether either occurs.
7. **[CLOSED 2026-08-14 — see the walkthrough addendum.]** **`storage_mode: reference`** — where the axes live when the value is a reference is not
   settled here.

---

## THE TEAM CALLS INSIDE THIS

1. The D10 sentence is amended and `conditions` tightens to cardinality 1.
2. `axes[]` gains a mount on `subject_statement`.
3. ~~The axis carries no `unit`; the dimension comes from `variable` + D9, making #32
   blocking.~~ **REVERSED 2026-08-14, AMENDMENT 1: the axis carries `unit` as a bound
   `ontology_term`, and #32 is out of its path.**
4. `datum` collapses to a bound, required `datum_type`, which lives on the **statement**.
5. `record` is retired as a datum kind; its one real use becomes a labelled axis.
6. `format` + `compression` land on `data_body`, with `filename`, `content_hash` and
   `description` hoisted alongside; `zarr` is deleted rather than migrated.

---

# ADDENDUM — the axis carries its own `datum_type`. Team, 2026-08-09.

Found in the misc-singletons sign-off review, from `binaryseries_parameters`, which
declares TWO independent byte encodings where this plan had one:

```
origin/main:.../database_documents/data/binaryseries_parameters.json
   time_size, time_type          the TIMESTAMPS' encoding
   data_size, data_type          the SAMPLES' encoding
   data_dim, samples_regular_intervals
```

Time is an ordinary axis under this plan, so an irregularly-sampled series that stores
its timestamps in the bytes alongside its samples had nowhere to say how those
timestamps are encoded: `subject_statement.datum_type` describes the VALUES, and the
axis entry had no encoding slot at all.

```
axis
   ...
   datum_type   char   NEW. Bound to the same 14-value vocabulary as
                       subject_statement.datum_type. REQUIRED when the axis is
                       body-mounted AND `regular` is false -- i.e. when the
                       coordinates are stored in the bytes. Absent otherwise.
```

**The principle, unchanged from this plan's own rule** (*the statement says what the
values ARE; the body says how the bytes ENCODE them*): an axis's coordinates are the
AXIS's numbers, not the statement's values, so their encoding belongs to the axis. This
is the same shape as `source_unit`, which already appears both on the axis and on the
value cells.

**`byte_order` does NOT move and is NOT duplicated.** Endianness is a property of the
file, and every column in one body shares it, so it stays on `sampled_body`. Only the
element type varies per column — which is exactly the split `binaryseries_parameters`
makes.

**The checkable rule.** On a body-mounted axis, `regular: false` means the coordinates
live in the bytes and `datum_type` is REQUIRED; the inline `values` slot is for
statement-mounted axes only. A regular axis stores no coordinates at all (`origin` +
`spacing` generate them), so it needs neither.

**Not a `binaryseries_parameters` special case.** Any irregularly sampled recording that
stores timestamps beside its samples needs this. The class is what surfaced it; the gap
was general.

Fold consequence: `binaryseries_parameters` maps cleanly and losslessly —
`data_type -> subject_statement.datum_type`, `time_type -> the time axis's datum_type`,
`data_dim -> the number of axes`, `samples_regular_intervals -> axis.regular`, the two
`*_size` fields implied by their `datum_type`. Without this addendum the fold would have
had to drop the timestamp encoding, or declare that only regularly-sampled series
survive it — a real limit, not a lossless fold.

---

## SIGNED OFF 2026-08-14

TEAM-SIGN-OFF [data_body]: jess@walthamdatascience.com / 2026-08-14 -- the axis entry replacing all three regularity encodings; time becomes an ordinary axis and both sample_time blocks retire; datum collapses to datum_type on the statement; conditions tightens to cardinality 1; format + compression + filename + content_hash + description hoist onto data_body; byte_order + datum_order on sampled_body; summary is dropped; zarr is deleted rather than migrated.

**WRITTEN BY CLAUDE ON EXPLICIT INSTRUCTION, AND THAT IS WORTH RECORDING BESIDE THE
LINE ITSELF.** Operating Rule 4 says *"Claude must never add that line."* The rule exists
because Claude-authored write-ups once reached the team as decided work. It was raised
before this was typed, the exact text was shown first, and the instruction to write it was
given twice ("A1. sign off", then "A1. Write it"). The decision is the team's; the typing
is not. A reader who wants the provenance should read this paragraph, not assume it.

**WHAT THE SIGNATURE DOES NOT COVER.** The plan's own `## OPEN` list is not resolved by
it, and four of those seven items were re-opened or answered on 2026-08-14 in the
walkthrough that led here:

  * `format` / `compression` vocabularies still need a corpus sweep before binding. The
    DIRECTION was decided that day -- an IANA media type for `format`, a short closed enum
    of transforms for `compression`, and explicitly NOT file extensions -- but the value
    set is still unmeasured.
  * `content_hash` hashes the bytes AS STORED in the attachment, with `format` +
    `compression` saying what those bytes are. Decided 2026-08-14.
  * `summary` is dropped and NOT replaced for now; a value rollup may be reconsidered
    later. Decided 2026-08-14.
  * `image.value.axes` folds into the one axis entry. Every axes declaration is to carry
    `kind`, `regularity` and `origin`; none is to carry `sample_rate`. Decided 2026-08-14.
  * `storage_mode: reference` -- where the axes live when the value is a reference -- is
    STILL OPEN, and 2026-08-14 sharpened it rather than settling it (see below).

**AND ONE CASE THIS PLAN DOES NOT HANDLE, FOUND THE SAME DAY BY READING A REAL MIGRATED
DOCUMENT.** The plan predates the raw-recording observation build, so it never saw a body
with NO BYTES TO DESCRIBE. Two instances, and they are the same shape:

        DENOMINATOR: 2 emitters inspected, both writing a sampled_body with no file
        jRecordingObservation   sets storage_mode 'body' and attaches nothing; the raw
                                acquisition files are beside the session, never in the
                                database. 11 such bodies in one migrated PRED-like
                                session, each with dtype '', shape [], empty sample_time.
        jrclust_clusters        the v1 template is `res_mat_MD5_checksum` + `element_id`
                                and NO file list at all, so there is not even an
                                attachment to measure. The migrator writes n = 0 and says
                                why.

  The axis entry makes `n` REQUIRED, so neither can produce a valid axis. That is not a
  defect in the axis -- it is the question of whether a body should be emitted at all when
  the payload is outside the database. It needs a team call and is NOT covered by the
  signature above.

  **BOTH HALVES ARE NOW ANSWERED, AND A THIRD CASE THIS PARAGRAPH DID NOT KNOW ABOUT
  ARRIVED WITH THEM.** The OUTSIDE-the-database half is closed by walkthrough item 6
  below (*"A body means bytes"*), which is what the two instances above were waiting
  for: `jRecordingObservation` and `jrclust_clusters` emit NO body, so neither is
  asked for an axis and `n` stays safe to require. Read item 6 rather than this
  paragraph for that case.

  The third case is `element_epoch`, and it inverts the premise: its payload is INSIDE
  the database (one of the 15 v1 templates declaring a `file_list`; `ingest: 1` on all
  252 documents in corpus 20211116), so a body IS earned -- and `n` is still
  unreachable, because a single-document migrator carries files without reading their
  bytes. **TEAM, 2026-08-17: the dissolution SPLITS.** Pass 1 emits the metadata that
  needs no bytes; the NDI second pass, which holds a live session and the ingested
  file, attaches the `sampled_body` with a COMPLETE axis. That follows this plan's own
  reasoning -- an axis is asserted only when the array is held, and pass 1 does not
  hold it -- and the `jRecordingObservation.m:53` precedent, where a channel-axis count
  is already *"a second-pass fill"*. Recorded in full, with its measurements and its
  accepted costs, at `V_eta_epoch_plan.md`, "ADDENDUM -- the #60 scoping walkthrough",
  which carries the signature; nothing is decided here.

---

# ADDENDUM — the storage-mode walkthrough. Team, 2026-08-14.

Six questions were put to the team on the day of the signature. Four of the plan's
seven `## OPEN` items close here. Recorded in this file rather than in a task
description, because a task list is not a durable record.

## 1. A LEAF GIVES THE UNIT; AN AXIS HAS NO LEAF

The team asked whether pairing `variable` with a leaf class already fixes the
canonical unit implicitly. **It does, and that makes the registry work SMALLER than
this plan implies.** Two value cells from the built tree, side by side:

        voltage.value              volts, source_unit, source_value, approximate
        conditions.quantity.value         source_unit, source_value, approximate

`voltage` has a canonical slot NAMED FOR ITS UNIT, so the class fixes the dimension
and no registry row is needed -- which is what the registry's own `binding_examples`
already says about `body mass` (*"dimensional leaf: mass_observation already fixes
the value type, so no admissible-set spec is needed"*). `conditions.quantity.value`
has NO canonical slot, only what the source said, so its number is uninterpretable
without one.

An axis is the `conditions` case: a `voltage_observation` fixes that the VALUES are
volts and says nothing about what the time axis is measured in.

**CONSEQUENCE: the D9 seed set is axis variables and condition variables ONLY**, not
every variable in the system. That is the material half of the #32 -> #115 split, and
it is why the axis work does not wait on the NDIC vocabulary.

## 2. THE ENCODING VOCABULARIES

`format` -> an IANA media type (`image/tiff`, `application/zip`), `application/x-…`
for lab formats with no registration. `compression` -> a short closed enum of
transforms (`none`, `gzip`, `zstd`, `lzw`, `deflate`). **NOT file extensions** --
`.zip` / `application/zip` / `zip` are three spellings of one thing, and an extension
is a filename convention rather than an identifier.

This separates the two cases the observed values tangle: `tiff` + `lzw` is a format
with internal compression (`image/tiff` + `lzw`); `.nbf.tgz` is a format wrapped in
one (`application/x-nbf` + `gzip`).

**DIRECTION DECIDED, VOCABULARY NOT.** OPEN item 2 stands: the full value set needs a
corpus sweep before either field is bound.

**AMENDED 2026-10-14 (Jess, lightsheet migrator point 4; no sign-off line): `format` is a
bound `ontology_term`, not an IANA media type.** IANA is the only registry for media types,
so a lab format (OME-Zarr has no registration) could only ever be an `application/x-`
string; v1 already records formats as CURIEs (`fileReference` / `generic_file`
`format_ontology`: `EDAM:format_3620`, `EMPTY:0000253`), so those migrate as written. EDAM
format terms first (`EDAM:format_3591` TIFF, `EDAM:format_3997` MPEG-4, `EDAM:format_2333`
binary, `EDAM:format_3915` Zarr), an EMPTY term where EDAM has none (OME-Zarr, minted as a
kind of `EDAM:format_3915`). Bound `{strength: preferred, node_form: curie}`, like
`variable`; the admissible set is not enumerated. `compression` is unchanged.

## 3. `content_hash` HASHES THE BYTES AS STORED

With `format` + `compression` declared, "the stored bytes" is unambiguous, and it is
the only hash checkable without decompressing -- which is what an integrity check is
for. Closes OPEN item 3.

## 4. `summary` IS DROPPED AND NOT REPLACED

Reconsider a value rollup later if a query need appears. `jSampledBody` stops minting
the empty `{value:{}, time:{}}` scaffold it puts on every body today.

## 5. ALL THREE AXES DECLARATIONS FOLD INTO THE ONE ENTRY

Measured over the built tree -- THREE incompatible shapes, not two:

        DENOMINATOR: 3 axes declarations found under schemas/V_eta/
        sampled_body.axes        name, kind, length, regularity, spacing, unit
        image.value.axes         name,       length,             spacing, unit
        acquisition_epoch.axes   name, kind, length, regularity, spacing, unit, sample_rate

`image.value.axes` has no `regularity`, so it declares a `spacing` with no way to say
whether spacing is meaningful. `acquisition_epoch.axes` carries `sample_rate` -- the
same fact as `spacing`, inverted. **None of the three has an `origin` and none can
store coordinates**, so `regularity: irregular` is declarable and unstorable today.

Team: all three fold into the one entry; every one carries the regularity flag and an
origin; none carries `sample_rate`. Closes OPEN item 4. Note `image.value.axes` sits
inside a composite's `value` rather than on a body, so the fold must respect the
statement/body mount rule rather than just renaming fields.

## 6. A BODY IS EMITTED ONLY WHEN THERE ARE BYTES TO ATTACH

The question that was NOT in this plan. It came from reading a real migrated document
rather than a schema.

**THIS IS V1'S OWN DIVISION, not a new concept.** Measured:

        DENOMINATOR: 91 v1 template(s) parsed from NDI origin/main
          declare a file_list : 15
          declare NONE        : 76

Fifteen classes carry bytes; seventy-six are pure metadata. `jrclust_clusters` is one
of the 76 -- its entire body is `res_mat_MD5_checksum` + an `element_id` edge, a
fingerprint of a `res.mat` file living outside the database, with **no file list at
all**. V_eta had been minting a `sampled_body` for it anyway, with `n = 0`.

**THE RULE.** When the payload lives outside the database the document records a
REFERENCE -- `filename` + `content_hash`, both already hoisted onto `data_body` by
this plan -- and NO body. A body means bytes.

**Why it matters for the axis:** it makes `n` safe to require. An axis is asserted
only when the array is held, so "required but unknowable" cannot arise.

**AND THE PRED CASE IS A DIAGNOSIS, NOT A DESIGN GAP.** `jRecordingObservation` emits
11 bodies with `storage_mode: 'body'` and nothing attached in a PRED-like session --
because that session is **NOT INGESTED**. The `.rhd` files sit beside the session and
are read on demand by the file navigator; they were never in the database, so there
was nothing to attach. **After ingestion there is**, and the body becomes the honest
shape. The hollow bodies are a symptom of migrating a non-ingested session, not of
the model.

## 7. AXES LIVE WITH THE THING WHOSE EXTENT THEY DESCRIBE

The team asked whether axes should ALWAYS live on the statement, so a consumer finds
them in one place regardless of storage mode. **They should not, and `pyraview` is
why:**

        pyraview.m:284-287   for k = 1:numel(fileList)
                                 rate_k = ...; dt_k = 1.0/rate_k; t0_k = starts(k);
                                 b = jSampledBody(..., struct('regular',true, ...
                                     't0',...,'dt',durationComposite(dt_k),'n',0));

One observation, ten bodies, a different rate and start per body -- a decimation
pyramid. A statement-level list cannot say "this one has 30,000 samples at 30 kHz and
that one has 3,000 at 3 kHz". Extent genuinely varies per body.

**The rule is uniform even though the location is not:**

> Axes live with the thing whose extent they describe.
>   inline    -> the value is on the statement    -> axes on the statement
>   reference -> one external payload, one extent -> axes on the statement
>   body      -> each body has its own extent     -> axes on each body

A consumer never branches on storage mode: it asks *where is the value*, which it must
do anyway, and the axes are with it. **`reference` joining `inline` on the statement
CLOSES OPEN item 7**, which the signature above explicitly did not cover.

Rejected: statement-always with a per-body override. The override becomes the common
case the moment anything is multi-body, and then the axes are in two places with a
precedence rule to remember.

## WHAT REMAINS OPEN AFTER THIS ADDENDUM

Of the seven `## OPEN` items: **3, 4 and 7 are CLOSED**; **1** narrows to the D9
dimension seed (#115) rather than the whole of #32; **2** and **6** need a corpus
sweep (the format/compression value set; whether `char` or complex datum types occur);
**5** (the Hartley plane read) is unchanged and still wants the NDIcalc-vis writer,
which no session has been able to attach.

**AND TWO ITEMS THIS ADDENDUM ADDS, both from reading writers on 2026-08-14:**

  * `electrode_offset_voltage.m:90` leaves its temperature qualifier's unit
    *"deliberately unstated"*. NDI's own schema documentation settles it --
    *"The temperature at which the measurement was made, in degrees C"* -- so the unit
    was documented and dropped on the way through, not unknown. Recoverable.
  * `pyraview`'s per-level `n` IS derivable (file size / (bytes-per-sample x channels);
    `dataType`, `channels` and a ten-entry `file_list` are all on the v1 template).
    `jrclust_clusters`'s is NOT, and under rule 6 above it should emit no body at all.

---

# AMENDMENT — the axis carries its own unit. Team, 2026-08-14.

**THIS AMENDS THE SIGNATURE ABOVE, on the same day, and it reverses one line of
it.** The signed axis entry says `THERE IS NO `unit` FIELD` and routes the
canonical unit through the D9 registry. That is changed here. The rest of the
signed entry is untouched.

## WHAT PROMPTED IT: the registry could not express the one variable that needed it

Working through the seed set for #115, `spatial frequency` has no expressible
canonical unit:

  * there is **no `spatial_frequency` data_type** -- `frequency` is `hertz`, which
    is temporal;
  * cycles-per-degree is inverse-angle, a dimension nothing in V_eta declares;
  * and the registry row shape that would say so **does not exist**. Measured --
    four lists, and not one carries a dimension or a unit:

        DENOMINATOR: schemas/V_eta/stable/binding_registry_meta.json, 4 list(s)
        subject_statement_bindings  class, ontology, root_node, subject_defining, variable
        binding_examples            class, method, notes, ontology, root_node, values, variable
        relation_bindings           child_role, child_types, class, ordered,
                                    parent_role, parent_types, relation, timed
        entity_field_bindings       class, closed, field, strength, term_set, vocabulary

So the one axis variable that most needed the registry was the one it could not
answer for, and the machinery to answer at all was unbuilt.

## 1. THE AXIS CARRIES `unit`, AS A BOUND `ontology_term`

```
axis
   variable      ontology_term   REQUIRED   what varies along this dimension
   unit          ontology_term   NEW        the canonical unit of `value`/`values`
   source_unit   char            optional   the unit exactly as the source gave it
   ...           (everything else unchanged from the signed entry)
```

**BOUND, NOT FREE TEXT, and that distinction is the whole reason this is safe.**
The signed entry's objection to a unit field was that a free-text unit beside a
bound `variable` is the escape hatch that makes the binding pointless. That
objection is about `char`. An `ontology_term` is not an escape hatch.

**THE PATTERN IS ALREADY IN THE SCHEMA, TWICE, and this borrows rather than
invents:** `voltage.value` is canonical-plus-source (`volts`, `source_unit`,
`source_value`); `conditions.count.value` carries a BOUND `unit` inline
(`{value: integer, unit: ontology_term, approximate}`). The axis needs both
halves because it cannot name its slot after a unit the way `voltage` does --
one `values` list serves time, position, contrast and orientation.

**THE FAILURE MODE THIS FIXES IS THE ONE THIS PROJECT CARES ABOUT MOST.** As
signed: an unpopulated registry row makes the number SILENTLY MEANINGLESS -- the
document carries a quantity nothing can interpret, and nothing reports it. With
`unit` on the axis the worst case is an UNVALIDATED number, which is the
difference between "wrong" and "not checked", and this repository has spent four
separate corrections keeping those two apart.

## 2. ANGLES ARE RADIANS, EVERYWHERE

> **AMENDED 2026-09-25 (jess, #73 review item 44): ANGLES ARE DEGREES, EVERYWHERE.** The
> section below is kept as the record of the earlier reasoning, which rested on "every
> quantity in V_eta names its canonical slot after an SI unit". That premise no longer
> holds: V_eta's canonical units are PRACTICAL SI (grams, liters, celsius, mmHg), and the
> practical unit for angles in neuroscience -- orientation and direction, phase, degrees of
> visual angle, stereotaxic angles -- is the degree. `angle.value.degrees` is the canonical
> slot; radians are a conversion at analysis time. `angular_velocity` follows it: degrees per
> second (item 47, same day).

Read off the built tree, not chosen:

        angle      value: radians, source_unit, source_value, approximate
        duration   value: seconds, ...
        frequency  value: hertz,   ...
        length     value: meters,  ...
        voltage    value: volts,   ...

Every quantity in V_eta names its canonical slot after an SI unit, and `angle`'s
is `radians`. So `orientation` and `direction` axes are RADIANS.

**A degrees-based proposal was put and rejected on this evidence.** NDI's vision
calculators work in degrees throughout -- which is an argument about
`source_unit`, not about the canonical value. Converting on the way in is
precisely what `source_unit`/`source_value` exist for.

## 3. `conditions` IS RESCOPED AGAINST `axis` FOR FORMAT PARITY -- NEW WORK, NOT DECIDED HERE

The team's call, and it is a SCOPE, not a design. Recorded so the next reader
does not treat the two as settled.

The overlap is exact and the asymmetry is already inside one field today:

        conditions.term      ontology_term array          <-> axis.labels    ontology_term array
        conditions.count     {value, unit, approximate}   <-> axis has no count form
        conditions.quantity  {source_unit, source_value}  <-> axis origin/spacing/values
                             NO canonical, NO unit             canonical + source + unit

`conditions.count` carries a BOUND unit inline; `conditions.quantity` -- one slot
over -- carries neither a canonical value nor a unit, and its own documentation
says *"the dimension is carried by `variable` + the D9 registry"*. So the schema
already does it both ways, adjacently, and that predates this plan.

**What parity would mean, stated as the question rather than the answer:** does
`conditions.quantity` gain `unit` + a canonical value, matching `count` and the
amended axis -- so every dimensioned value in V_eta is self-describing -- or do
conditions and axes converge on ONE cell shape? `quantity` has live writers, so
this is a real change with a real blast radius, and it is deliberately NOT
decided by this amendment.

## 4. THE REGISTRY BECOMES VALIDATION, AND MOVES OUT OF THE CRITICAL PATH

Its rows say which units are ADMISSIBLE for a variable, rather than being the
only place the unit lives. A missing row can then no longer produce
uninterpretable data -- it can only fail to confirm interpretable data.

**#115 CHANGES MEANING: it is a FOLLOW-UP, not a prerequisite.** The axis entry
is buildable with no registry work at all. The dimension-seed framing in that
row is superseded by this amendment; what it becomes is a variable -> admissible
units check.

## CONSEQUENCE

**The axis entry has no remaining prerequisite.** #32 and #115 are both out of
its path, and the two corpus-sweep items (the format/compression value set;
whether char or complex datum types occur) gate the ENCODING FIELDS only, not
the axis.

---

# AMENDMENT 2 — `conditions` reaches format parity with `axis`. Team, 2026-08-14.

Closes the rescope opened by AMENDMENT 1 item 3. **Merging `conditions` INTO
`axes` was NOT reopened** -- the signed plan rejects it (*"time is the commonest
axis and has never been a condition"*), and that stands. An axis INDEXES a
value; a condition QUALIFIES it. Same descriptors, different job.

## THE SCOPE, MEASURED BEFORE DECIDING

        DENOMINATOR: 210 .m file(s) under DID-matlab src/did/+did2 scanned,
                     comment-only lines excluded
        files referencing `conditions` in CODE: 2
          electrode_offset_voltage.m:90   quantity -- temperature, unit ''
          jTuningFold.m:53                quantity -- tuning independent variable

**`term` and `count` have ZERO writers. Ever.** Three forms are declared and one
is used. And `jTuningFold`'s condition is an AXIS by construction -- it writes a
`variable`, a unit and a value list -- so the signed build order moves it, leaving
`conditions` with exactly ONE live writer: a scalar temperature qualifier.

## THE SHAPE

```
conditions
   variable     ontology_term   what is being qualified
   unit         ontology_term   canonical unit
   source_unit  char            as the source gave it
   approximate  boolean         applies to the whole condition
   term     { value : ontology_term[] }
   count    { value : integer[] }
   quantity { value : { value:double, source_value:double }[] }
```

Against the amended axis -- same four descriptors, same place, then the value
forms:

```
axis
   variable, unit, source_unit, approximate
   n, regular, origin, spacing
   values { values, source_values }
   labels ontology_term[]
```

## WHY THIS IS THE SHAPE, AND WHY A SMALLER CHANGE WAS REJECTED

A first proposal added `unit` + a canonical value to `quantity` ALONE. **It was
withdrawn: it does not achieve parity, it creates a THIRD placement.**

        axis        unit at the TOP level, one for the whole axis
        count       unit INSIDE each value element
        quantity    unit at the quantity level      <- the proposed third

Three placements for one concept is the disease, not the cure.

**MOVING THE DESCRIPTORS UP LOSES NOTHING, and that is measured rather than
asserted.** `jMeasureArray` -- the shared helper both writers use -- applies ONE
unit to every reading and writes `approximate` false at every position:

        m(k) = struct('source_unit', char(unit), ...
                      'source_value', double(vals(k)), 'approximate', false);

So per-element `source_unit` is identical across the array in every writer that
exists, and per-element `approximate` has never been anything but false. Moving
both up removes redundancy, not expressiveness.

**The one objection this had to answer** -- a descriptor that only some value
forms use -- is already the accepted pattern: the axis's `unit` applies to
`values` and not to `labels`. `conditions` doing the same is parity, not new
looseness.

**AND `count`'s PLACEMENT HAS NEVER BEEN EXERCISED.** Zero writers means no
legacy to preserve. If it is not aligned now, the first `count` writer cements
the third pattern permanently.

## WHAT THIS IS, HONESTLY

**A RESTRUCTURE of `conditions`, not a field addition.** Three descriptors move
up a level and `count` flattens. Small in code -- zero writers for two forms, two
for the third and one of those is leaving -- but it is a schema change to a class
with live documents, and it was approved as that rather than as the smaller thing
first described.


---

**COUNT CORRECTION, 2026-08-17 — `receptive_field` and `receptive_field_calculation` were
minted** (TEAM-SIGN-OFF [receptive field naming], `V_eta_ngrid_family_findings.md`). The
dated measurements above are left exactly as taken; this is the live claim beside them:

        DENOMINATOR: 249 json file(s) under schemas/V_eta/ read
        243 distinct V_eta class names
        42 direct subclasses of `data_type`

Only the COMPOSITE is a `data_type` subclass — the leaf hangs off
`subject_calculation` — which is why the class count moved by two and the
data_type-subclass count by one. One signed decision moved four counters at once
(these three plus the inert-set canary in `tests/test_veta_stimulus_response.py`),
which is the per-document cost `check_prose_counts` exists to find.


RE-DERIVED 2026-08-21 (ndi_m_files, `check_prose_counts`): 91 NDI templates on origin/main; 1,012 .m files (`git ls-tree -r origin/main | grep -c '\.m$'` = 1012 at 5df51cf9; +7 since the 1,005 reading). The did_v1 ground truth is STILL unmoved -- 91 templates, 0 template diffs; only the denominator shifted.


RE-DERIVED 2026-08-21 (ndi_m_files, sibling drift): NDI `origin/main` advanced to `1c0fe1283` (PR #882, parallel-workers), so `git ls-tree -r origin/main | grep -c '\.m$'` = **1013** (was 1012). The did_v1 ground truth is UNMOVED -- 91 templates, 0 template diffs; only the denominator shifted. Re-derive, do not quote.


RE-DERIVED 2026-09-22 (#67 calculator restructure + sibling drift, `check_prose_counts`): 254 distinct V_eta class names; 260 json file(s) under schemas/V_eta; 102 NDI templates on origin/main; 1,179 .m files. Re-derive rather than quote; #67 added `calculator` + `runtime_environment` + the `tuning_curve`/`tuning_curve_calculation` families (11 new classes total), and NDI `origin/main` gained 11 templates (gene-expression family + demoNDISeries pair + fileReference).

RE-DERIVED 2026-09-23 (spatial-transcriptomics family landed via #64 commit `71298fd`, `check_prose_counts`): **262 distinct V_eta class names** (was 254; +8 spatial-transcriptomics classes); **268 json file(s) under `schemas/V_eta`** (was 260; +8); 102 NDI templates on origin/main; 1,180 .m files (was 1,179; sibling drift). Re-derive with `python3 tools/check_prose_counts.py`, do not quote these directly.


RE-DERIVED 2026-09-23 (#73 calculator restructure: `calculator` mixin dropped, 5 tuning markers dropped, 6 `*_calc` leaves -> 5 `*_tuning_calculation` + concrete `tuning_curve_calculation`; `check_prose_counts` re-derives all nouns): **256 distinct V_eta class names** (was 262; -5 markers, -6 `*_calc` leaves, +5 renamed leaves); **262 json file(s) under `schemas/V_eta/`** (was 268; same -6); tombstones classes compared: 74 (was 76; `orientation_direction_tuning` and `tuningcurve_calc` left for "no tombstone" 17 -> 19 when they joined `_DELETE_PHASE8`, and LOSSY fell 11 -> 9 because the V_eta classes that had taken those two did_v1 names never declared their real fields); **20 deleted** in `_DELETE_PHASE8` (was 11; +4 v1 calc tombstones `oridirtuning_calc`, `tuningcurve_calc`, `spatial_frequency_tuning_calc`, `temporal_frequency_tuning_calc`, +5 v1 result tombstones `orientation_direction_tuning`, `contrast_tuning`, `spatial_frequency_tuning`, `temporal_frequency_tuning`, `speed_tuning`). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-09-25 (the #73 review build; `check_prose_counts` re-derives all nouns): the build added label, label_calculation, coordinate_system, position, position_observation, position_calculation, count/area/score/term_calculation and restored harmonic_component_calculation. Live figures: **267 distinct V_eta class names** (was 256); **273 json file(s) under `schemas/V_eta/`** (was 262); **44 direct subclasses** of `data_type` (was 42; +`label`, +`position`) -- and since #73 item 19 NONE of them is abstract. Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-09-25 (#65 increment 3b: `session_relative_reference`, `session_bounded_reference` and `epoch_bounded_reference` deleted schema-first, `is_approximate` removed from `time_reference`; `check_prose_counts` re-derives all nouns): **264 distinct V_eta class names** (was 267); **270 json file(s) under `schemas/V_eta/`** (was 273). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-09-25 (#73 review item 45: the new `spatial_frequency` composite; `check_prose_counts` re-derives all nouns): **265 distinct V_eta class names** (was 264); **271 json file(s) under `schemas/V_eta/`** (was 270); **45 direct subclasses** of `data_type` (was 44). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-09-25 (#73 review item 48: the new `voltage_calculation` leaf; `check_prose_counts` re-derives all nouns): **266 distinct V_eta class names** (was 265); **272 json file(s) under `schemas/V_eta/`** (was 271). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-09-25 (#73 review item 50: 51 unused statement leaves deleted; `check_prose_counts` re-derives all nouns): **215 distinct V_eta class names** (was 266); **221 json file(s) under `schemas/V_eta/`** (was 272). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-09-25 (#73 review item 51: the V_eta `image` data_type and `image_observation` retired, `image` restated as the did_v1 tombstone; `check_prose_counts` re-derives all nouns): **214 distinct V_eta class names** (was 215); **220 json file(s) under `schemas/V_eta/`** (was 221); **44 direct subclasses** of `data_type` (was 45). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-09-25 (#73 review item 52: `logical_observation` retired; `check_prose_counts` re-derives all nouns): **213 distinct V_eta class names** (was 214); **219 json file(s) under `schemas/V_eta/`** (was 220). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-09-25 (#73 review item 53: the run-environment entity split into two `software` edges and deleted; `check_prose_counts` re-derives all nouns): **212 distinct V_eta class names** (was 213); **218 json file(s) under `schemas/V_eta/`** (was 219). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-09-25 (ndi_m_files, sibling drift; `check_prose_counts`): NDI `origin/main` at `0a2cdeccb`: 102 NDI templates on origin/main; 1,181 .m files (was 1,180; `git ls-tree -r origin/main | grep -c '\.m$'` = 1181). Only the denominator moved. Re-derive, do not quote.

RE-DERIVED 2026-09-25 (#73 review item 59: `product` minted, `amount` renamed `substance_amount`; `check_prose_counts` re-derives all nouns): **213 distinct V_eta class names** (was 212); **219 json file(s) under `schemas/V_eta/`** (was 218); **44 direct subclasses** of `data_type` (unchanged: `substance_amount` replaces `amount`, and `product` is an entity). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-09-25 (#73 review item 61: `acquisition_metadata_file` retired; `check_prose_counts` re-derives all nouns): **212 distinct V_eta class names** (was 213); **218 json file(s) under `schemas/V_eta/`** (was 219). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-09-29 (#73 review item 67: `control_designation` deleted; `check_prose_counts` re-derives all nouns): **211 distinct V_eta class names** (was 212); **217 json file(s) under `schemas/V_eta/`** (was 218). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-09-29 (#73 review item 68: `model_fit` + `model_fit_calculation` minted; `check_prose_counts` re-derives all nouns): **213 distinct V_eta class names** (was 211); **219 json file(s) under `schemas/V_eta/`** (was 217); **45 direct subclasses** of `data_type` (was 44; +`model_fit`). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-10-03 (did-schema PR #86: the `humidity` composite, its `humidity_observation` leaf, and the `length_calculation`, `velocity_calculation` and `intensity_calculation` leaves, for the Haley import's stages 9-10; `check_prose_counts` re-derives all nouns): **217 distinct V_eta class names** (was 212); **223 json file(s) under `schemas/V_eta/`** (was 218). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-10-04 (the tenet audit, did-schema PR #87: `humidity` moved under `data_type`, where #86 should have put it; `check_prose_counts` re-derives all nouns): **46 direct subclasses** of `data_type` (was 45; +`humidity`). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-10-04 (`timed_sequence` becomes `item`, signed in `V_eta_study_plan.md`: the class and its manipulation leaf renamed, plus the new `item_calculation` leaf; `check_prose_counts` re-derives all nouns): **218 distinct V_eta class names** (was 217); **224 json file(s) under `schemas/V_eta/`** (was 223). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-10-05 (the `time_calculation` and `acceleration_calculation` leaves, for the Haley import's stage 11; `check_prose_counts` re-derives all nouns): **220 distinct V_eta class names** (was 218); **226 json file(s) under `schemas/V_eta/`** (was 224). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-10-08 (one `entity` class and statements by composition, a PROPOSAL built ahead of signature, `V_eta_entity_composition_plan.md`; `check_prose_counts` re-derives all nouns): **47 direct subclasses** of `value` (`data_type` until 2026-10-08; was 46, +`text`); classes compared: 72 (in `check_tombstones.py --enforce`); **166 distinct V_eta class names** (was 220; -42 join leaves, -13 entity classes, +`text`); **172 json file(s) under `schemas/V_eta/`** (was 226). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-10-08 (every v1 calculator keeps its named class, Jess; `check_prose_counts` re-derives all nouns): **169 distinct V_eta class names** (was 166; +`contrast_sensitivity_calculation`, `receptive_field_calculation`, `speed_tuning_calculation`); **175 json file(s) under `schemas/V_eta/`** (was 172). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-10-09 (`linked_session`, a PROPOSAL built ahead of signature in `draft/`, `V_eta_linked_session_plan.md`; `check_prose_counts` re-derives all nouns): **170 distinct V_eta class names** (was 169); **176 json file(s) under `schemas/V_eta/`** (was 175). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-10-14 (ndi_m_files, sibling drift; `check_prose_counts`): NDI `origin/main` at `695e8d86`: 1,236 .m files (`git ls-tree -r origin/main | grep -c '\.m$'` = 1236). Only the denominator moved. Re-derive, do not quote.

RE-DERIVED 2026-10-14 (NDI-matlab#979 merged `lightsheetZarrPyramid` and `lightsheetZarrLevel` into NDI `origin/main`, restated here as v1 tombstones `lightsheet_zarr_pyramid` / `lightsheet_zarr_level`; `check_prose_counts` re-derives all nouns): **104 NDI templates** on origin/main (was 102); **172 distinct V_eta class names** (was 170); **178 json file(s) under `schemas/V_eta/`** (was 176). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-10-19 (ndi_m_files, sibling drift; `check_prose_counts`): NDI `origin/main` at `358b2fbf`: 1,300 .m files (`git ls-tree -r origin/main | grep -c '\.m$'` = 1300). Only the denominator moved. Re-derive, do not quote.


# AMENDMENT 3 — one entry for keys, conditions and method parameters. Jess, 2026-10-19.

Decided with Jess Haley in the Haley import's term pass. **SIGNED 2026-10-19** -- the
`TEAM-SIGN-OFF [data_body amendment 3]` line is at the end of this section.

# AMENDMENT 4 — a `matrix` value form on the single-value entry. Jess, 2026-10-21.

**A PROPOSAL, built ahead of signature at Jess Haley's request (2026-10-21).** It
closes `V_eta_method_plan.md` open follow-up (b). It lives here, not in the method
plan, because the entry it changes is AMENDMENT 3's, shared by `conditions` and
`method.parameters`; the method plan points here.

## WHAT PROMPTED IT

Noise stimuli (sparse noise, reverse correlation; vhlab NewStim stochastic grid
stimuli) become `method` documents (`V_eta_method_plan.md`). Their settings include
values that are lists or matrices, which none of `term` / `quantity` / `count` /
`text` can hold:

| setting | shape |
|---|---|
| colour palette | n x 3 |
| colour weights | n |
| background colour | 3 (an RGB triple) |
| random-state seed | 35 numbers (MATLAB's legacy `rand('state')` vector) |

## THE SHAPE

The single-value entry gains a fifth value form:

```
variable, unit, source_unit, approximate
+ ONE value form:  term | quantity {value, source_value} | count | text | matrix
```

- **`matrix`**: type `matrix`, `mustBeScalar: false`, blank `[]`. A numeric N-D
  array, **row-major as JSON nested arrays, every dimension written**: an n x 3
  palette is `[[r, g, b], ...]` with one inner array per row, a 1 x n row is
  `[[a, b, c]]` and an n x 1 column is `[[a], [b], [c]]`. A flat `[a, b, c]`
  cannot say row or column (MATLAB's `jsondecode` reads it as a column), so the
  writer never emits one; a reader treats a flat array from another tool as a
  column. (Corrected 2026-10-21 from "a vector is `[a, b, c]`" when did2.build's
  round-trip tests showed the orientation was lost; VH-Lab/DID-matlab 415368f.)
  Its unit is the entry's `unit` (absent for a unitless number), as for `quantity`.
- **The whole array is ONE value of the entry's `variable`.** A palette is not
  split into n entries; the variable names the whole thing ("colour palette").
- **No `source_value` beside it.** `quantity.source_value` keeps a scalar exactly as
  the source spelled it; a numeric array has no spelling to keep. A source in a
  non-canonical unit is converted, and `source_unit` says what it was.
- **Keys do NOT get `matrix`.** AMENDMENT 3 says a key's positions are terms or
  quantities, one scalar per position along one axis. A key whose positions are
  themselves vectors (a palette as an axis of n colours) is a different question
  and is NOT decided here.

## NOISE COLOURS (Jess, 2026-10-21)

- Colour values are in **`NCIT:C75765` "Arbitrary Unit"** (registered in
  `V_eta_term_registry.json`). A colour channel is a device level, not a physical
  quantity.
- The scale goes in the data, not in a convention: a separate **"bit depth"**
  parameter, a `count` (8), so that 255 = full scale is recorded on the document.

## VARIABLE TERMS

Registered, because an existing term matches: **`NCIT:C64220` "Random Seed"** --
*"A number (or vector) used to generate random numbers in a system."*

**MISSING -- no matching term found (EBI OLS, exact search, 2026-10-21); NOT minted
here**, naming them is a decision:

| variable | nearest found | why it is not a match |
|---|---|---|
| colour palette | -- | nothing |
| colour weights | -- | nothing |
| background colour | `NCIT:C37927` Color | the generic quality, not the background's |
| bit depth | -- | nothing ("color depth" finds only vision tests) |

## WHAT IT TOUCHES

Built in `tools/build_v_eta.py` section 12.15 (`_entry_subs`), so `_PARAMS_SHAPE`
(section 12.20) inherits it and stays the single source: `matrix` appears on both
`conditions` mounts (`statement`, `data_body`) and on every `method.parameters`
(`interaction`, `relation`, `clock_alignment_configuration`, the `method` document).
Writers and readers follow in DID-matlab (`did2.build`, the validator).

To be signed: a condition or method parameter may hold one numeric N-D array as a fifth value form `matrix` (row-major JSON nested arrays with every dimension written, in the entry's unit, no source_value; keys excluded); noise colours are in NCIT:C75765 Arbitrary Unit with a separate bit-depth count parameter; NCIT:C64220 Random Seed registered as the seed variable.

TEAM-SIGN-OFF [data_body amendment 4]: jess@walthamdatascience.com / 2026-10-21 -- a condition or method parameter may hold one numeric N-D array as a fifth value form matrix (row-major, every dimension written, in the entry's unit, no source_value, not on keys); noise colours in NCIT:C75765 Arbitrary Unit plus a bit-depth count; NCIT:C64220 Random Seed as the seed variable

AMENDMENT 2 gave keys and conditions the same four descriptors and kept their value forms
apart. Laid side by side with `method_parameters` (which the 2026-08-09 sign-off says was
"modelled on the `axis` entry"), the three lists still spelled each value form
differently:

| | key | condition | method parameter |
|---|---|---|---|
| category | `labels` | `term.value` | `term` |
| number | `values.values` / `.source_values` | `quantity.value.value` / `.source_value` | `value.value` / `.source_value` |
| integer | -- | `count.value` | -- |
| free text | -- | -- | `text` |
| `approximate` | yes | yes | no |

AMENDMENT 2's own argument -- *"three placements for one concept is the disease, not the
cure"* -- applies to the value forms as it did to the unit. So every entry is now

```
variable, unit, source_unit, approximate
+ ONE value form:  term | quantity {value, source_value} | count | text
```

- **A condition and a method parameter are the SAME entry, holding ONE value** (every
  form scalar). `quantity.source_value` is TEXT, kept verbatim, as the method-parameters
  plan already required (v1 writes a threshold as the string `"0.030"`).
- **A key is that entry holding n positions.** Its `term` is an array of n terms (was
  `labels`) and its `quantity` is `{value, source_value}` as two arrays of n (was
  `values {values, source_values}`). A key's positions are terms or quantities only, and
  a key's `source_value` stays NUMERIC: an irregular time key can hold thousands of
  positions. `regular` keys (`origin` + `spacing`) are unchanged.
- **The axis/condition split stands.** A key INDEXES a value; a condition QUALIFIES it.
  This amendment shares their spelling, not their job.

Built in `tools/build_v_eta.py` section 12.15 (2 key lists, 2 `conditions` mounts, 3
`method_parameters` mounts). Writers and readers follow in DID-matlab (`did2.build`, the
validator, the migrators) and NDI-matlab (the Haley import, `ndi.value`).

TEAM-SIGN-OFF [data_body amendment 3]: jess@walthamdatascience.com / 2026-10-19 -- conditions and method parameters are one entry {variable, unit, source_unit, approximate} plus one of term, quantity {value, source_value as text}, count or text; a key is that entry holding n positions (term, quantity {value, source_value numeric}), labels and values renamed.

RE-DERIVED 2026-10-20 (the term registry, tenet T19, `V_eta_term_registry_plan.md`; `check_prose_counts` re-derives all nouns): **179 json file(s) under `schemas/V_eta/`** (was 178; +`stable/term_registry_meta.json`, a meta file, so the class count is unchanged). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-10-21 (one `method` shape and `visual_grating` deleted, a PROPOSAL built ahead of signature, `V_eta_method_plan.md`; `check_prose_counts` re-derives all nouns): **170 distinct V_eta class names** (was 172); **177 json file(s) under `schemas/V_eta/`** (was 179; -`visual_grating`, -`spatial_frequency`, `method_parameters` renamed `method`). Re-derive with `check_prose_counts`, do not quote these directly.

# AMENDMENT 5 — a value is inline or in bodies, never neither. Jess, 2026-10-21.

**DECIDED by Jess Haley, 2026-10-21, and SIGNED the same day** -- the
`TEAM-SIGN-OFF [data_body amendment 5]` line is at the end of this section, followed by a

Clarification (Jess Haley, 2026-10-21): a statement may also take its value from a shared
value document through `value_id` (`statement.json`: "When present, this statement's own
value and value descriptors are empty: the shared document states them"); the shared
document itself is inline or in bodies. So the check passes when `value` is filled, OR
`data_body` is true, OR a non-empty `value_id` edge is present. This follows from the
existing `value_id` decision and is not a new decision.

Decided by Jess Haley, 2026-10-21 [data_type only for plain arrays]: "`data_type` is required only when a value's bytes are a plain array -- a `sampled_body`, or an untyped inline array; when its bodies are opaque (`opaque_body`), their `format` term is the encoding and no `data_type` is needed."

Why it came up: with this amendment a value with no inline `value` must say
`data_body: true`, and `data_type_when_bytes` then demanded a `data_type` for every such
value. Two kinds of value have bytes with no single datum type: the spike sorter's output
(an `observation` with a `count` value kind, whose sorter files are an `opaque_body`;
DID-matlab `jSorterOutput.m` left `data_body` unset to avoid the demand) and raw
acquisition files (Intan `.rhd` and the like, linked as `opaque_body`). The rule
`data_type_when_bytes` on `value` now says so. A body's kind is not visible on its owner,
so a per-document check cannot tell a sampled owner from an opaque one; the
`sampled_body` half is a batch check.
dated clarification about `value_id`. (Until c8260da this paragraph read "NOT SIGNED";
HISTORICAL-SIGNOFF-CLAIM.)

## THE RULE

A value is either **inline** (its `value` field filled) or **in data bodies**
(`data_body: true`, the bytes in `sampled_body` / `opaque_body` documents pointing at it
through `owner_id`), **never neither**. It is ONE rule on the parent `value` class,
`value_inline_or_body`, declared beside `data_type_when_bytes` in the same rules format.
It does not say whether a value may be both; that is not decided here.

## WHAT IT REPLACES

Nine value classes made their inline `value` required (`mustBeNonEmpty: true`): `term`,
`date`, `logical`, `polynomial`, `model_fit`, `tuning_curve`, `contrast_sensitivity`,
`harmonic_component`, `receptive_field`. A required inline value refuses every
body-backed document of that class, which this plan's storage-mode walkthrough already
allows for every value. All nine are now `mustBeNonEmpty: false`; the rule on `value`
carries the requirement for them and for the other 36 direct subclasses of `value`, whose
inline `value` was already optional (their field declarations are unchanged).

## WHAT PROMPTED IT

`receptive_field.value` was a REQUIRED structure with NO sub-fields: #73 item 57 moved the
method to the statement and audit 2 D11 moved the plane labels to body conditions, so
nothing was left inline and no document could satisfy it. DID-matlab's `hartley_calc`
migrator therefore passes all 210 20211116 documents through (guard `foldExpressible()`,
ab02782 on DID-matlab `claude/port-88`, `hartley_calc.m:259,687`), while the signed `[receptive field fold]`
(`V_eta_ngrid_family_findings.md`) keeps the payload in two `sampled_body` documents. With
this rule a `receptive_field` document is `data_body: true` with an empty `value`, and
the fold can emit it.

## WHERE IT IS CHECKED

- did-schema: `tools/validate_v_eta.py` rule R16 checks that `value` declares the rule and
  that no class under `value` makes its inline `value` required; its
  `value_inline_or_body(doc)` is the reference statement of the document check, pinned by
  `tests/test_validate_v_eta.py`.
- DID-matlab: `did2.build` checks it by name (`+did2/+build/private/checkRules.m`, case
  `value_inline_or_body`, pinned by `testBuild.testValueInlineOrBody`); the `did2` validator
  and `hartley_calc` (dropping its `foldExpressible()` passthrough) follow separately.

To be signed: a value is inline (its `value` field filled) or in data bodies (`data_body: true`), never neither -- one rule `value_inline_or_body` on the parent `value` class, replacing `mustBeNonEmpty: true` on the `value` field of term, date, logical, polynomial, model_fit, tuning_curve, contrast_sensitivity, harmonic_component and receptive_field.

TEAM-SIGN-OFF [data_body amendment 5]: jess@walthamdatascience.com / 2026-10-21 -- a value is inline (its value field filled) or in data bodies (data_body: true), never neither: one rule value_inline_or_body on the parent value class, replacing the required inline value of term, date, logical, polynomial, model_fit, tuning_curve, contrast_sensitivity, harmonic_component and receptive_field

## 2026-10-21 — sorter output by location

Decided by Jess Haley, 2026-10-21 [sorter output by location]: a v1 sorter output that names an external directory (kilosort/kiasort) migrates to an opaque_body whose single member records that directory by location, with the curated-output MD5 as the member's checksum and format EMPTY:0000315 "directory of files".

Decided by Jess Haley, 2026-10-14 [format is an ontology term]: "`format` is a bound `ontology_term`, not an IANA media type ... EDAM format terms first ..., an EMPTY term where EDAM has none (OME-Zarr, minted as a kind of `EDAM:format_3915`)" (the AMENDED 2026-10-14 note above, confirmed by Jess Haley 2026-10-21, answer "4A"). This is the decision behind EMPTY:0000259 "OME-Zarr".

Decided by Jess Haley, 2026-10-22 [NDI binary format]: the ingested stimulus metadata archive (v1 `daqmetadatareader_epochdata_ingested` `data.bin`, a `.nbf.tgz`) gets a new EMPTY format term rather than EDAM:format_2333 "Binary format" (answer "5b"). Evidence (Waltham-Data-Science/NDI-compress 37c8c05, `+ndi/+compress/write_ndibinary.m`): `.nbf.tgz` is NDI's own "NDI binary" format, `ndi_binary_version` 1, a gzip-compressed tar of an `.nbh` header and an `.nbf` data file; `compress_metadata` stores the parameter structs as JSON text in it, and `compress_ephys`, `compress_digital`, `compress_time` and `compress_eventmarktext` write the same format. Proposed (not decided): ONE generic term "NDI binary format" for every `.nbf.tgz`, not a metadata-only term.

# AMENDMENT 6 — dimensions and covariates replace keys. Jess, 2026-10-22.

**Why.** A value could describe each position along an axis only through its
key, one per dimension. Anything else that varies along an axis had nowhere to
go, so it grew as one-off fields on one value kind (`item.value.offset`, the
per-trial end of a timed sequence; `item.value.control_item`, the control).
Separating the axis from what is known along it removes both, and gives every
other per-position fact (an electrode's depth per channel, a frame's quality, a
trial's reward) a place without a new field. This is the NetCDF/CF and xarray
model: dimensions, and auxiliary coordinates along them.

**The shape, on `data` (value documents and data bodies alike, wherever `keys`
was).**

- `dimensions`: one entry per axis of the stored array, in array order
  (dimension k IS array axis k). Each entry:
  - `term` (ontology_term, required): what the axis is. Not unique: a channel x
    channel matrix has two `channel` dimensions.
  - `n` (integer, required): the axis length.
  - `chunk` (sampled_body only): unchanged.
- `covariates`: what is known about the value's positions along one or more
  dimensions. Each entry is the AMENDMENT 3 entry with:
  - `variable` (ontology_term, required).
  - `along` (integer list, required, NON-EMPTY, distinct): 0-based indices into
    `dimensions`.
  - `unit`, `source_unit`, `approximate` as on every entry; `cyclic` only on a
    numeric covariate along exactly one dimension.
  - EXACTLY ONE value form:
    - `origin` + `spacing` (each `{value, source_value}`): positions
      origin + k * spacing; numeric; along exactly one dimension.
    - `quantity` `{value, source_value}`: numbers in `unit`.
    - `count`: integers.
    - `term`: terms `{node, name}` or labels `{name}`.
    - `text`: strings.
    - `logical`: true / false (new).
    - `matrix`: a whole numeric array at each position (AMENDMENT 4).
    - `document`: the 0-based position of a `key_id` entry; position k is entry
      k of that document's value (was the key's `positions_from`); along
      exactly one dimension.
  - Shape: the extents of the `along` dimensions, in that order; for `matrix`,
    those extents followed by the array's own shape.
- `datum_order`: unchanged; it orders the dimensions.

**Rules.**
- A covariate is never `along: []`. A fact true of the whole value is a
  `condition`, and conditions STAY ON THE STATEMENT: a value document may be
  shared by several statements (item 30), and conditions describe each
  statement's circumstances.
- A dimension may have no covariate (a plain index).
- Covariates describe positions; they are not further measurements. A standard
  error is its own value at the same positions, not a covariate.
- A variable appears at most once across a statement's conditions, its value's
  covariates, and any one of its bodies' covariates (the existing batch check,
  with covariates in place of keys).

**Removed.** `keys`; the entry's `n` (on the dimension now) and `regular` (the
presence of `origin`/`spacing` says it); `positions_from` (now `document`);
`complete` (sparse or ragged data is one `row` dimension with a covariate per
former key, the long format); `item.value.offset` and `item.value.control_item`.
`acquisition_epoch`'s own copy of the key entry becomes the same `dimensions` +
`covariates`.

**A stimulus presentation** (v1 `stimulus_presentation`, now an `item` value):
one dimension, a presentation; covariates `onset time` (always), `offset time`
(when v1 recorded ends) and `control condition` (XCO:0000099, `logical`; see
the stimulus-response plan's [control as covariate]).

Decided by Jess Haley, 2026-10-22 [covariates]: `data` carries `dimensions` and `covariates` in place of `keys`, as above. Her question that opened it: "why can't we come up with a way to specify additional covariates along one or more of a value's axes?"; then "Forget what's signed. What's truly the best shape"; the list name "Covariates"; built "Before" the merge.

Decided by Jess Haley, 2026-10-22 [conditions stay on the statement]: conditions are not moved onto the value; a covariate always runs along at least one dimension. Her "Ok" to the revised proposal, after asking "Is there any reason moving conditions off the statement is going to be a problem?" (answer: a shared value document, item 30).

Decided by Jess Haley, 2026-10-22 [along by index]: `along` lists dimension indices, not names ("I'm still not sold on along referencing the name of the dimension term rather than the index"), and a dimension carries a term ("Why do dimensions not have terms?"; required: "3y"). The value form that takes positions from another document is `document` ("Why isn't it just 'document'?").

Decided by Jess Haley, 2026-10-22 [matrix covariate]: a `matrix` covariate holds a whole array at each position; dimensions stay exactly the value's own axes (answer "B").

Decided by Jess Haley, 2026-10-22 [onset time]: a stimulus presentation's times are the covariate `onset time`, not `time` and not `stimulus onset time` ("Actually I think onset time would be correct. Stimulus is redundant?"); the end is `offset time`.

Decided by Jess Haley, 2026-10-22 [no complete]: `complete` is deleted; sparse data is one row dimension with covariates (answer "1a").

Decided by Jess Haley, 2026-10-22 [bare dimension]: a dimension may have no covariate (answer "2a").

Decided by Jess Haley, 2026-10-22 [epoch covariates]: `acquisition_epoch`'s copy of the key entry moves to `dimensions` + `covariates` (answer "4y").

Decided by Jess Haley, 2026-10-22 [tenets follow covariates]: the tenets are updated to the covariate model ("If we need to update the tenets following the covariate changes, let's do that.").

Decided by Jess Haley, 2026-10-22 [covariate terms]: terms for the presentation dimension, `onset time` and `offset time` are found by T19 order (an existing ontology term first, an EMPTY term only where none fits) and brought back as one list (answer "4y").

Proposed (not decided) [covariate terms chosen]: from the T19 search of 2026-10-22 (scratch write-up; 503 registry terms, 49 prefixes, 402 EMPTY classes, 59 OLS4 queries; CogPO, CogAt and NEMO not searched): the presentation dimension is OBI:0000807 "presentation of stimulus" (its definition says "organism", a weak point for slices and cultures); `onset time` and `offset time` are new EMPTY:0000368 / EMPTY:0000369 (empty-ontology #24, unmerged), because NDI's stimulus decoder records `onset`/`offset` apart from `stimopen`/`stimclose`, so SIO:000669 "start time" / NCIT:C78441 "Start Time" would name `stimopen`; the sparse `row` dimension is SIO:000752 "row" (needs a new `sio` prefix). Until confirmed, builds write these four as labels (`{name}`, no node). `onset time` and `offset time` are registered as `staged` (name decided by [onset time], node still to be confirmed) because the Haley import, whose term registry is armed, writes `offset time` for encounter exit times; `presentation` and `row` have no row. Open with it: whether EMPTY:0000140 "encounter onset time" becomes a subclass of, or is replaced by, `onset time` (T19).

Decided by Jess Haley, 2026-10-22 [presentation dimension term]: the dimension of a stimulus presentation sequence is OBI:0000807 "presentation of stimulus" (answer "1A"), replacing the label `presentation`. Supersedes that part of the proposed [covariate terms chosen].

Decided by Jess Haley, 2026-10-22 [onset and offset terms]: `onset time` and `offset time` are new EMPTY:0000368 and EMPTY:0000369 (empty-ontology #24), not SIO or NCIT start/end time, which name the start of the period around the stimulus (`stimopen`); EMPTY:0000140 "encounter onset time" is made obsolete, replaced by `onset time` (answer "2a-ii"; asked first "Does no existing ontology use onset time?" -- OLS4: clinical uses only). Supersedes that part of [covariate terms chosen].

Decided by Jess Haley, 2026-10-22 [row term deferred]: the term for a sparse `row` dimension is chosen when a writer first produces sparse data; nothing does today (answer "3c").

Decided by Jess Haley, 2026-10-22 [tuning grid]: a tuning curve over several independent variables whose conditions form a full grid has one dimension per variable, each with its covariate, and the response an array over them; otherwise one `stimulus condition` dimension with a covariate per variable (answer "4c"; the corpora hold no such curve -- 34,690 tuning curves in 221,827 v1 documents, all over one variable). The `stimulus condition` term is to be brought back before use.

Decided by Jess Haley, 2026-10-22 [covariate details]: `cyclic` only on `origin`+`spacing` and `quantity` covariates (5.1a); a missing member of a tiled sampled body takes the body's `fill_value` and is refused without one (5.2a); `acquisition_epoch` dimensions carry no `chunk` (5.3a); a dimension's term is bound `preferred`, and each corpus report counts dimensions whose term has no node, so dimension terms move to `required` with variables under OPEN_WORK #129 after the merge (answer "B" to 5.4).

Decided by Jess Haley, 2026-10-22 [covariate rules named]: the covariate shape rule (extents of `along`, then a matrix's own shape) and the one-variable-across-conditions-and-covariates rule are named schema rules (6.1a); a covariate that only repeats its dimension's positions 0..n-1 is not written (6.2a); `datum_order` stays required only on a sampled body of more than one dimension (6.3a); migration reports count the v1 `stimulus_control_id` edges dropped by [control as covariate] (answer "A" to 6.4).

Decided by Jess Haley, 2026-10-22 [stimulus condition term]: the `stimulus condition` dimension of [tuning grid] (one position per distinct combination of stimulus parameter values, when the conditions do not form a full grid) is XCO:0000000 "experimental condition", the parent of XCO:0000099 control condition; no ontology term names a combination of factor levels (answer "A").

Decided by Jess Haley, 2026-10-22 [index covariates]: a covariate that only lists a dimension's positions is not written whether they count from 0 or from 1 (1..n, or origin 1 / spacing 1 with no unit and no recorded scale), extending [covariate rules named] 6.2a; an origin/spacing that comes from a recorded scale or carries a unit is kept. Migration and corpus digests render the new counts (dimensions without a node; dropped `stimulus_control_id` edges) with denominators. Answer "yes to all three". Built: DID-matlab 9c9cab9 (index covariates), b5ded13 (digests).

## 2026-10-22 -- tenet audit: units, entries and value kinds

Decided by Jess Haley, 2026-10-22 [units bound]: `unit` on covariates, conditions and method parameters binds to registered unit terms, and the canonical-unit list is restored as a gate in tools/, read by check_term_registry (answer "C2a"). Built: every entry and covariate `unit` is bound {strength: preferred, node_form: curie}; tools/canonical_units.py holds the list (the canonical slot of each value kind and its unit term) and check_term_registry.py R11 checks the value-kind cells against it, the listed unit terms against the registry, and the unit fields bound. 25 of the 34 canonical units have no registered term yet (volt, ampere, mmHg, ...); R11 lists them and chooses none.

Decided by Jess Haley, 2026-10-22 [remaining units bound]: `response_unit` (tuning_curve, contrast_sensitivity) and the fit entry's unit fields are bound too, and the missing units are registered: spikes per second, and dF/F as a dimensionless ratio (answer "M1a"). Built: those fields are bound; "spikes per second" and "dF/F" are registered STAGED (by name, no node): no ontology term matches either exactly (candidates noted on the rows: NCIT:C94877 Count per Second; om:one, UO:0010006 ratio), so the node is still to be chosen.

Decided by Jess Haley, 2026-10-22 [logical entries]: the `logical` form is added to conditions and method parameters (answer "F2a"). Built on all six entry lists (statement and data_body conditions; interaction, method, relation and clock_alignment_configuration method parameters), one shape (validate_v_eta R13).

Decided by Jess Haley, 2026-10-22 [irradiance]: a new `irradiance` value kind, canonical W/m2; `intensity` stays dimensionless; T12's example says a measured light intensity uses `irradiance` (answer "G4a"). Built: `irradiance` (draft), slot `watts_per_square_meter`, om:wattPerSquareMetre registered.

Decided by Jess Haley, 2026-10-22 [ratio slots named by unit]: concentration's `mass_fraction` becomes `grams_per_gram`, `volume_fraction` becomes `liters_per_liter`, and `od600` becomes `optical_density`, with the wavelength (600 nm) as a condition or in the source unit "OD600"; the Haley OD600 and formulation writers change (answer "O2a").

Decided by Jess Haley, 2026-10-22 [missing integers]: integer slots accept NaN for a missing position, stored as a literal NaN; the validator accepts a whole number or NaN (answer "O4a"). Built: stated on the meta-schema's `type` (no integer slot sets `mustNotHaveNaN`).

Decided by Jess Haley, 2026-10-22 [audit mechanical fixes 2]: rule `variable_once` covers a body's conditions; decision 6.3a gets a named rule (`datum_order` required on a multi-dimensional sampled body) and the "Empty means F" documentation is fixed; the pattern-syntax documentation says the syntax is that of the class behind `software_id`; the acquisition_channels stale note and its two uses are fixed; the stale `acquisition_system` under `entity` and `acquisition_metadata_reader_#` prose is fixed (the daq decisions document here; daqsystem.m, vintage/map.m and isaQuery.m comments in DID-matlab and NDI) (answer "E2 yes"). Built here: the two rules (`variable_once` on data, `datum_order_multidimensional` on sampled_body) and the `datum_order` documentation; the documentation items follow in the documentation commit of this batch.

RE-DERIVED 2026-10-22 (the `irradiance` value kind, Jess Haley [irradiance], V_eta_data_body_model_plan.md; `check_prose_counts` re-derives all nouns): **171 distinct V_eta class names** (was 170); **178 json file(s) under `schemas/V_eta/`** (was 177). Re-derive with `check_prose_counts`, do not quote these directly.

Decided by Jess Haley, 2026-10-22 [audit mechanical fixes]: the audit's mechanical fixes: `interaction.software_id`'s documentation (optional on calculations); the `matrix` documentation drops "a vector is [a, b, c]"; tuning_curve's "stimulus condition term still to be chosen" becomes XCO:0000000; the Gene Expression binding row is re-keyed off the retired spatial_gene_expression_pyramid; om:RelativeHumidity's definition; the stale names in the tenets (timed_sequence, datum_type, `<value>_<direction>` leaves in T11, subject and web_resource in T9, the T15 table's key_labels_id, strain and build_v_eta.py, T2's method "proposed", T2's clock_alignment input_id exception); about 15 field documentations with retired names; EMPTY:0000140 marked obsolete in the registry, its row removed once NDI stops writing it (answer "E yes"). Built across this batch: the registry and binding-row items with [vocabulary nodes], the matrix and tuning_curve documentation with [units bound], the field documentations and software_id here, and the tenet names with the tenet text. om:RelativeHumidity's definition is now empty: OM gives that class no English definition (om-2.0.rdf), and the one it carried belonged to mass flow.

Decided by Jess Haley, 2026-10-22 [harmonic response unit bound]: `harmonic_component.response_unit` is bound like `tuning_curve.response_unit` (preferred, CURIE node) — the same kind of field, which [remaining units bound] did not name (answer "4a").

Decided by Jess Haley, 2026-10-22 [response variable]: what a tuning response measures goes in the statement's existing `variable` (firing rate, dF/F, ...); `response_type` keeps the statistic (mean, peak, F0, F1, F2); `response_unit` is the plain unit, so a spike rate is `om:hertz` (T19), not a "spikes per second" unit (answer "J1b", on the explanation that `tuning_curve_calculation` inherits `statement.variable` and the tuning migrators leave it empty). Built here: the staged "spikes per second" registry row is removed and the `response_unit` documentation says so. Build pending: did-schema (the firing-rate `variable` node is not chosen: no exact quantity term found; OLS4 exact "firing rate" gives only SNOMED "Motor unit firing rate" and GO:0099605, a process), then DID-matlab (tuning migrators fill `variable` from v1 `response_units` and write `om:hertz`; empty where the source does not say).

Decided by Jess Haley, 2026-10-22 [dF/F as variable]: dF/F is the response variable, not a unit: a calcium-imaging tuning response has `variable` = dF/F and `response_unit` = `om:one` (dimensionless), as [response variable] does for firing rate (answer "J2 sounds good"). Built here: the staged "dF/F" unit row is removed. Build pending: did-schema (a dF/F `variable` node), then DID-matlab (tuning migrators write it).

Decided by Jess Haley, 2026-10-22 [pressure in mmHg]: the `pressure` canonical slot stays `mmhg`, its unit om:millimetreOfMercury ("The millimetre of mercury is a unit of pressure defined as 1.0e-3 metre of mercury."), not pascal: physiology reports pressure in mmHg, and the source unit is kept either way (answer "J3a"). Built: registry row and canonical-unit node.

Decided by Jess Haley, 2026-10-22 [pH unit one]: the `ph` canonical slot's unit is om:one ("Unit one is a unit of dimension one."); the value kind names the quantity, the unit stays plain, as [response variable] and [dF/F as variable] do; no UO prefix is registered (answer "J4c"). Built: registry row om:one (shared with dF/F responses) and canonical-unit node. SUPERSEDED the same day by [pH unit is UO pH].

Decided by Jess Haley, 2026-10-22 [pH unit is UO pH]: the `ph` canonical slot's unit is UO:0000196 "pH" ("A dimensionless concentration notation which denotes the acidity of a solution in terms of activity of hydrogen ions (H+)."), replacing [pH unit one]: T14 makes a canonical unit the one the field's practitioners use, and OM has pH only as the quantity om:Acidity, with no unit. The UO prefix is registered for this unit; other units stay OM (answer "agreed on J3 and J4", after review against T14). [pressure in mmHg] is reconfirmed on the same review: T14 names `mmhg`, and pascal was already reversed on 2026-09-29 (review/73/audit2_SUMMARY.md D10 (e)). Built: UO prefix in CURIE_lookups_meta.json, registry row UO:0000196, canonical-unit node; om:one stays for dF/F.
