# V_eta — the acquisition epoch family

**DECIDED with the team, 2026-08-05. Build deferred. NO `TEAM-SIGN-OFF` LINE** —
the marker is the team's to write (Operating Rule 4), so the status board renders
this as *awaiting a signature*.

> **READ THE REVISION AT THE BOTTOM FIRST.** The decision recorded immediately
> below was answered about the WRONG OBJECT — `element_epoch` is per-element-per-
> epoch, not the epoch — and was revised the same day. The revision supersedes the
> "THE DECISION — option B" section. Everything else here (the reframe, the ground
> truth, the four defects) stands.

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

---

# REVISION, same day — the earlier decision was about the WRONG OBJECT

**The team's words:** asked whether we should mint a real per-epoch document, *"I
think this makes sense."* Asked whether `acquisition_epoch` should be an entity as
`session` is, and told the choice turns on reading `entity` as *"has identity in the
world"* (argues no) versus *"the named, addressable spine of the archive"* (argues
yes): **"I read it as the spine of the archive."**

## What was wrong

The decision above ("identity + extent") was answered about `element_epoch`, which
is **not the epoch**. From the writer:

```matlab
% +ndi/element.m:367-378
epochdoc = E.newdocument('element_epoch', ...
    'element_epoch.epoch_clock', epochclockstr, ...
    'element_epoch.t0_t1', t0_t1_input, ...
    'epochid.epochid', epochid);
epochdoc = epochdoc.set_dependency_value('element_id', elementdoc.id());
```

**One document per ELEMENT per EPOCH** — its own clock, its own extent, its own
`.vhsb` payload. Many share one `epochid.epochid`.

**So there is no epoch document in v1 at all.** An epoch is only a shared string,
which is exactly why every join is a string match: there is nothing to point at.
V_eta renamed `element_epoch` → `acquisition_epoch`, a name that reads as "the
epoch itself", and this plan then described it that way — "when did this epoch run"
when the document answers "when did this ELEMENT's recording run". A T13 naming
error that propagated into a decision.

**The project already assumed the fix.** `V_eta_time_reference_model_plan.md`:

> the `(referent, epoch)` pair collapses to ONE edge **only because V_eta reifies
> the epoch as a document**

The time model is written on the assumption that an epoch IS a document. Nothing
had minted one.

## THE REVISED MODEL

```
acquisition_epoch  ⊂ entity        ONE PER EPOCH -- MINTED; does not exist in v1
   base.id                         the archive's own key (every document has one)
   local_identifier   "t00023"     the v1 epochid string, preserved as the handle
   global_identifier  (empty)      an epoch has no external cross-reference
   depends_on: session_id
               time_reference_#    the epoch's own extent

element_epoch      DISSOLVES       it is one element's data for one epoch:
   t0_t1 / epoch_clock       -> time_references
   epoch_binary_data.vhsb    -> sampled_body
   element_id                -> the observation's subject/instrument (T7, #30)
   + acquisition_epoch_id    -> the epoch it belonged to

every epoch-scoped document gains   acquisition_epoch_id -> acquisition_epoch
   resolvable at migration by GROUPING on epochid.epochid
```

The 11+ string joins become graph edges. `epochid` the mixin survives as **migration
input**, not as the target's join mechanism.

## Why `entity`, and why it is NOT about identifiers

`base.id` and `global_identifier` are different things. `base.id` is a `did_uid` —
the primary key on every document, entity or not. `global_identifier` is documented
as *"Cross-reference identifier(s) … ORCID | ROR | DOI | PMID | PMCID | RRID | UDI"*
— identifiers from OTHER systems. An epoch has none and never will, which by the
signed-off `frequency_filter` reasoning would argue AGAINST entity.

**The deciding argument is structural, not identity-based.** T9: *"Aggregation…
are `directed_relation`s"*, and `directed_relation` declares **both endpoints as
`entity`**:

```
directed_relation(child=session, parent=dataset, relation=part_of)   works
directed_relation(child=epoch,   parent=session, relation=part_of)   works ONLY if epoch is an entity
```

With `acquisition_epoch ⊂ base` the containment spine is expressible for the top
link and not the bottom one. For `strain` the entity tier's **gift** mattered
(a repeatable `global_identifier`, four schemes in play); for an epoch its
**consequence** matters — being a legal relation endpoint.

Recorded honestly: the containment hierarchy is currently expressed **nowhere**.
`base.session_id` is a universal FIELD, not an edge, and nothing at all expresses
dataset→session. So this decision makes the spine expressible; it does not by itself
build it.

## Knock-ons

- **Weakens one objection to TaskList #57.** That proposal noted `directed_relation`
  cannot carry `clock_alignment` partly because its endpoints are `entity` and an
  epoch is not. With epochs as entities that objection dissolves — but
  `directed_relation` still has **no value slot**, so the affine transform and cost
  would still be dropped, and a separate class is still required. #57 remains a
  PROPOSAL.
- **`base.session_id` and a `part_of` relation would be two representations of one
  fact.** Flagged, not solved.
- **Minting needs the SECOND PASS.** One document per distinct `epochid.epochid` is
  a grouping over the whole corpus; a single-doc migrator cannot do it.

## What this does NOT revise

The four defects recorded above stand unchanged — they are repairs, true under any
model: the invented always-empty `epochfiles_ingested.epochid` (6,921 documents),
`axes`/`channels`/`storage` appearing in no NDI template, the dropped `.vhsb`
payload, and the `epochid` mixin dropped from three classes NDI gives it.

And the `epochid`-should-be-abstract question is now CHECKED rather than assumed:

```
$ grep -rn "'epochid'" --include=*.m src/          # 23 mentions in NDI
  every one is ndi.document('<realclass>', ..., 'epochid', epochid_struct)
  +migrate/+internal/stimulusBathToBath.m:74 lists it in a SUPERCLASSES array
  ZERO constructions of ndi.document('epochid', ...) as a primary class
$ grep -rn "class_name','epochid'" src/did/+did2/+convert/   # no migrator emits one
```

Positive evidence, not a failed search: **`epochid` wants `abstract: true`.**

## NAMING — the class is `epoch`, not `acquisition_epoch` (team, 2026-08-05)

**The team's words:** *"If we have session as one chunk of time, would it be fair to
just call this an epoch? We don't say acquisition_session?"* → **"Let's call it
epoch."**

Evidence, all pointing the same way:

```
$ ls schemas/V_eta/*/epoch.json                 FREE -- no collision

$ grep -n "acquisition_epoch" tools/build_v_eta.py
  138:    "element_epoch": "acquisition_epoch",   <- a RENAME-MAP entry

$ grep -rni "acquisition.epoch" NDI src/         NDI never uses the phrase

NDI's own epoch vocabulary is UNQUALIFIED throughout:
  element_epoch  epochclocktimes  epochfiles_ingested  epochid  oneepoch
  daqreader_epochdata_ingested  daqmetadatareader_epochdata_ingested  ...
```

**`acquisition_` was a substitute for `element_`, not a disambiguator.** It existed
to get "element" out of the name once elements became subjects. With the class now
meaning *the epoch itself* rather than *one element's slice of it*, that
justification is gone and the word does no work — a T13 unearned qualifier.

The spine reads as three bare nouns: **`dataset` → `session` → `epoch`**.
`acquisition_session` would be obviously redundant; `acquisition_epoch` was the same
redundancy, less visible only through familiarity.

**No collision after the time-model collapse.** `epoch_bounded_reference` and
`epoch_relative_reference` fold into `relative_reference` (8→2), `epochid` goes
abstract/migration-only, and `epochfiles_ingested` + the `*_epochdata_ingested`
trio use "epoch" as a modifier. `epoch` ends up the only class plainly named that.

**Why rename NOW rather than defer to R5 (#27).** The `file_navigator` /
`metadata_reader` naming was deferred precisely because those classes KEEP their
meaning, and renaming twice is worse than renaming once. Here the meaning is
changing anyway — element-epoch → epoch — so this is the cheapest possible moment.
Renaming at the same time as re-semanticising avoids a class whose name and meaning
changed at two different times, which is what makes an old document unreadable later.

Build consequence: `build_v_eta.py`'s rename map entry becomes
`"element_epoch": "epoch"`, and every `element_epoch_id -> acquisition_epoch`
dependency retarget goes with it, so the schema and the migrators move together.

---

# `epochfiles_ingested` — STILL OPEN. The fork was put to the team and not answered.

Recorded because the walkthrough moved on to the naming question before this was
settled, and it is the one part of the family still undecided.

## What the document actually holds

```
epochfiles_ingested  ⊂ base   dep: filenavigator_id
  epoch_id       the epoch string
  files[]        the ingestion manifest -- which files were ingested
  epochprobemap  THE PROBE -> SUBJECT ATTRIBUTION TABLE, as tab-delimited text
```

`epochprobemap` is not a manifest detail. From the class it deserialises to:

```matlab
% +ndi/+epoch/epochprobemap_daqsystem.m
name          % probe name
reference     % a non-negative integer that uniquely identifies combinable records
type          % the type of recording
devicestring  % an ndi.daq.daqsystemstring -- the DEVICE and CHANNELS
subjectstring % the local_id or document ID of the SUBJECT of the probe
```

A row reads: `ctx1 ⇥ 1 ⇥ n-trode ⇥ intan1:ai1-4 ⇥ mouse_44@lab`. **This is how the
archive knows whose neurons a recording belongs to, per epoch.**

## Reference check

```
BY EDGE:  nothing references epochfiles_ingested.

IN CODE:  navigator.m:236-239, 504, 525   queried on epochfiles_ingested.epoch_id (exact_string)
          session.m:514, find_ingested_docs.m:11      isa epochfiles_ingested
          navigator.m:220
            eval([epochprobemap_class '(d.document_properties.epochfiles_ingested.epochprobemap)'])
```

**The probemap is interpretable ONLY together with `filenavigator.epochprobemap_class`**
— two documents, one meaning. TaskList #59 preserves both the navigator's id and its
`epoch_map_format`, so that coupling survives whichever way this goes.

## THE FORK (put to the team; not answered)

```
A.  keep as ⑦ infra, repaired     fix the invented epochid edge, restore
                                  filenavigator_id, keep the probemap as text
                                  -> lossless and cheap, but the mapping stays an
                                     undeclared blob (T14) and is not queryable

B.  decompose the probemap        each row becomes real epoch-scoped edges
    into edges
```

### What B looks like

```
subject probe_ctx1        (element.m already promotes it, id preserved)
   base.name "ctx1"   local_identifier "ctx1|1"       <- name + reference
   term_assertion variable:{name:"instrument type"}   <- type "n-trode"
                  value:{OBI:..., "n-trode"}             (a subject_defining binding)

<modality>_observation                                 <- #30 creates this
   subject_id    -> mouse_44        <- subjectstring   THE ATTRIBUTION
   instrument_id -> probe_ctx1      <- the probe, per T7
   epoch_id      -> epoch           <- epoch-scoped, so it may differ per epoch
   depends_on: acquisition_system_id -> intan1   <- devicestring, device half
   channels "ai1-4"                              <- devicestring, channel half
   body -> sampled_body

epochfiles_ingested   SURVIVES, thinner
   depends_on: filenavigator_id -> fn-001        <- restored (NDI has it)
               epoch_id -> epoch
   files[]                                       <- the ingestion manifest stays
```

The load-bearing line is `subject_id -> mouse_44`: `subjectstring` becomes a real
edge instead of a string inside a serialised table, so *"every recording from this
animal"* becomes a graph query rather than a text parse. **B mints no new class** —
the rows land on observations #30 already creates.

### What B costs

- **Blocked on #30.** The observations it decomposes into do not exist yet.
- **Needs the SECOND PASS.** `subjectstring` is *"the local_id or unique document ID
  of the subject"*; resolving a local id needs the migrated-id graph, exactly as
  `distance_metadata` and the ensemble do. A single-doc migrator cannot.
- **`devicestring` needs parsing** — `intan1:ai1-4` splits into a device name
  (resolved against `acquisition_system.base.name`, preserved by #59) and a channel
  spec.

### Claude's recommendation, NOT a decision

**B as the model, A as pass-1 behaviour** — repair now so nothing is lost,
decompose in the second pass. B is the same shape as two decisions already taken:
the ensemble's epoch-scoped `member_of` edges (*"the recorded neuron set changes
epoch-to-epoch"*) and `distance_metadata`'s deferral to the second pass for exactly
this id-resolution reason. A probe's subject genuinely can change between epochs, so
the per-epoch mapping is real information rather than a redundant copy of the
migrated graph.
