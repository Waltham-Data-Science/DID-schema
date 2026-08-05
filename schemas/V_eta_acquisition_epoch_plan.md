# V_eta — the acquisition epoch family

**DECIDED with the team, 2026-08-05. Build deferred. NO `TEAM-SIGN-OFF` LINE** —
the marker is the team's to write (Operating Rule 4), so the status board renders
this as *awaiting a signature*.

**The team's words, recorded verbatim so this can be audited rather than trusted:**
Claude presented the fork as *"once clocks, axes, storage and payload have all moved
out, what does `acquisition_epoch` retain? **A.** identity only. **B.** identity +
extent"*, and the team replied **"I agree with B."** If that is a narrower agreement
than what is written below, the record is wrong and should be corrected — an earlier
family in this same session was marked decided on a weaker reply and had to be
reverted.

Covers `acquisition_epoch`, `epochid`, `epochfiles_ingested`.

---

## THE REFRAME — `epochid` is a join mechanism, not a class awaiting disposal

Documents do **not** point at an epoch. They **carry its id and are matched on it.**

```
BY EDGE:   element_epoch_id  -> referenced by: ensemble   (that is all)
           epochid / epoch_id / acquisition_epoch_id -> nothing

BY STRING: ndi.query('epochid.epochid','exact_string', ...)   -- 11+ live sites
  +daq/metadatareader.m:164          +element/timeseries.m:58
  +daq/reader.m:56                   +setup/NDIMaker/stimulusDocMaker.m:390,412
  +app/spikeextractor.m:156,310,388  +setup/+stimulus/+vhlab/add_stimulus_approach.m:54,64
  +app/+stimulus/decoder.m:114       +database/+fun/finddocs_elementEpochType.m:32
```

**15 NDI classes carry the `epochid` superclass:**

```
binnedspikeratevm  daqmetadatareader_epochdata_ingested  daqreader_epochdata_ingested
element_epoch  ensemble  epochclocktimes  openminds_stimulus  spikewaves
stimulus_bath  stimulus_parameter  stimulus_parameter_table  stimulus_presentation
vmspikefilteringparameters  vmspikefit  vmspikesummary
```

This is the third time in one session that a dependency-graph check came back nearly
empty while the real references were **string matches** — after
`daqsystem.base.name` (`getprobes`, syncrule parameters, `syncgraph.m:404`) and the
`syncrule_mapping.epochnode_*.objectname` query. **A `depends_on` sweep is not a
reference check.** That belongs in the standing method, not in one family's notes.

## Ground truth

```
NDI origin/main
  epochid              ⊂ base                {epochid: ""}            a SUPERCLASS
  element_epoch        ⊂ base, epochid       dep: element_id
                       {epoch_clock, t0_t1}  files: epoch_binary_data.vhsb
  epochfiles_ingested  ⊂ base                dep: filenavigator_id
                       {epoch_id, files[], epochprobemap}
  acquisition_epoch    ABSENT -- it is V_eta's rename of element_epoch

V_eta today
  acquisition_epoch   ⊂ base, epochid   dep: element_id -> subject (required)
                      clocks{name,t0,t1}  axes{...}  channels{...}  storage{...}
                      files: []
  epochid             ⊂ base, NOT abstract   {epochid: char}
  epochfiles_ingested ⊂ base   dep: epochid -> acquisition_epoch (required)
                      {epoch_id char, files string, epochprobemap char}
```

## THE DECISION — option B: identity + extent

`acquisition_epoch` **survives as a document**, retaining:

```
acquisition_epoch  ⊂ base, epochid
  base.id                          PRESERVED -- ensemble references element_epoch_id
  epochid.epochid                  PRESERVED -- the string 11+ queries match on
  depends_on: element_id -> subject
              time_reference_# -> relative_reference     <- the EXTENT (t0_t1)
```

Everything else leaves, in three directions already settled elsewhere:

| leaves | to | authority |
|---|---|---|
| `clocks` | `time_reference`s | `V_eta_time_reference_model_plan.md` ("`acquisition_epoch.clocks` DISSOLVES") |
| the `.vhsb` payload | `sampled_body` | the 2.D data_body collapse |
| `axes` / `storage` | `sampled_body` | TaskList #45 |

**Why B over A (identity only).** *"When did this epoch run"* is a question the
archive should answer directly rather than force a reader to reconstruct from the
statements inside it. The time model already supplies the shape — a
`relative_reference` with `start`/`end` against the session — so B costs an edge,
not a design.

**What B does NOT decide:** the exact cardinality of the time_reference edge is
subject to TaskList #52 (role-naming `time_reference_#`), which is precisely the
open item saying a bare index cannot distinguish start-anchor from
same-instant-other-frame. Until #52 lands, an epoch with more than one reference is
undefined in meaning. Recorded, not overlooked.

## FOUR DEFECTS — repairs, not decisions, and true under either option

**1. A third invented always-empty required edge — 6,921 documents.**

```
NDI:    epochfiles_ingested depends_on filenavigator_id
V_eta:  epochfiles_ingested depends_on epochid -> acquisition_epoch, mustBeNonEmpty

census run #257, empty required edge   vs   unconverted epochfiles_ingested
   4088  (Dab)                                 4088
   2484  (B)                                   2484
    349  (Soph)                                 349
```

Exact match — **100% empty** — and `filenavigator_id`, which NDI does write and
whose target id `#59` now preserves, was dropped. With `syncrule_mapping.epochid`
(5,316) and `daqmetadatareader.daqsystem_id` (59) this is **12,296 documents across
three classes with one cause**, and one blind spot: the vocabulary checker compares
FIELDS, not `depends_on` (TaskList #54).

**2. `axes` / `channels` / `storage` exist in no NDI template.** `element_epoch`
declares `{epoch_clock, t0_t1}` and nothing else. TaskList #45/#49.

**3. The `.vhsb` payload was dropped.** `element_epoch` declares
`epoch_binary_data.vhsb`; `acquisition_epoch` declares `files: []`. Under B it must
land in a `sampled_body`; verify it does before anything is deleted.

**4. The `epochid` mixin was dropped from three classes that NDI gives it.**

```
stimulus_parameter        V_eta supers = ['base']    NDI: base + epochid
stimulus_parameter_table  V_eta supers = ['base']    NDI: base + epochid
vmspikefit                V_eta supers = ['base']    NDI: base + epochid
```

Those documents lose the epoch association that 11+ live queries depend on.
(`epochclocktimes` and `stimulus_bath` also carry it in NDI but are not in V_eta at
all, which is a separate, already-tracked disposition.) Note `stimulus_parameter`
and `stimulus_parameter_table` are held for #31 — the mixin drop specifically should
be checked when that lands.

## Also derivable, and not part of the fork

**`epochid` should probably be ABSTRACT.** In NDI it is superclass-only — no
document is a bare `epochid`. V_eta made it concrete. Unless something emits a
standalone `epochid` document, it wants `abstract: true`. Not verified either way
here; check before changing.

**`epoch_id` is recorded three ways in v1** — the `epochid` mixin block, a plain
`epoch_id` char field on `epochfiles_ingested` (both in NDI), and V_eta's added
`epochid` edge. The migration should converge on the mixin, since that is what the
queries match.

## What this unblocks

TaskList **#57** (`clock_alignment`) needs epoch endpoints for `from_epoch`/
`to_epoch`. Option B keeps `acquisition_epoch` as a referenceable document, so that
proposal is no longer blocked on this family — though `clock_alignment` itself
remains **a proposal, not a decision**.
