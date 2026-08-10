# V_eta — the acquisition epoch family

**DECIDED with the team 2026-08-05; SIGNED OFF 2026-08-08 — the `TEAM-SIGN-OFF
[epoch]` line is at the bottom of this document. Build still deferred.**

<!-- HISTORICAL-SIGNOFF-CLAIM -->
*This header said "NO `TEAM-SIGN-OFF` LINE ... the status board renders this as
awaiting a signature" until 2026-08-10, two days after the signature was added 735
lines below it. It was false on both counts: the line exists, and the board reads
the line, not this paragraph. Sign-offs get appended at the bottom, so a header
that asserts their absence must be updated in the same commit.*

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

**1. An invented always-empty required edge — 6,921 documents.**

```
NDI:    epochfiles_ingested depends_on filenavigator_id
V_eta:  epochfiles_ingested depends_on epochid -> acquisition_epoch, mustBeNonEmpty

census run #257, empty required edge   vs   unconverted epochfiles_ingested
   4088  (Dab)                                 4088
   2484  (B)                                   2484
    349  (Soph)                                 349
```

Exact match — **100% empty** — and `filenavigator_id`, which NDI does write and
whose target id `#59` now preserves, was dropped.

**COUNT CORRECTED 2026-08-06.** This paragraph said the pattern was *"12,296
documents across three classes"* (this row plus `syncrule_mapping.epochid` 5,316 and
`daqmetadatareader.daqsystem_id` 59). That was an undercount by more than half, and
it named the three smallest. Re-derived from the same census (run #257):

```
stimulus_response_scalar_parameters_basic.stimulus_response_scalar_id   11,440
epochfiles_ingested.epochid                                              6,921   <- this row
syncrule_mapping.epochid                                                 5,316
stimulus_presentation.element_id                                         2,670
daqmetadatareader.daqsystem_id                                              59
                                                                        ------
                                                                        26,406   FIVE classes
```

The two stimulus-tier rows were in the same report all along; the sweep that produced
the original figure stopped at the daq/sync families. See `CLAUDE.md` and
`V_eta_stimulus_response_model_plan.md`. **Re-derive the row set from a fresh census
before quoting a total.** The blind spot is unchanged: the vocabulary checker compares
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

**`epochid` — DECIDED 2026-08-05: DROPPED FROM THE TARGET ENTIRELY.**

Claude first wrote this as *"probably abstract"* and separately as *"migration input
only"*. **Those are different claims and conflating them was sloppy** — `abstract:
true` leaves the class in the target still stamping its block onto documents,
whereas "migration input only" removes it. Put as a fork, the team chose removal.

```
the epochid CLASS        DELETED from V_eta.
the epochid.epochid      NOT carried by migrated documents.
   block
migrators                READ epochid.epochid from v1 INPUT to work out which epoch
                         a document belongs to, then write `epoch_id -> epoch`
                         and nothing else.
"t00023"                 lives in exactly ONE place: epoch.local_identifier
```

## Why this is the OPPOSITE of the `strain` decision, and neither is a precedent

For `strain` (`V_eta_openminds_family_record.md`, Part 6) the assertion KEEPS its
inline `{node, name}` value AND gains a `strain_id` edge. Here the document keeps
ONLY the edge. Three differences, and they compound:

| | strain | epoch |
|---|---|---|
| **Is the inline value a complete fact on its own?** | **YES** — `{WBStrain:00000002, "PR811"}` is a CURIE naming a real thing in the world; a reader holding no other document can interpret it. | **NO** — `"t00023"` is a bare local string, meaningless outside its session. It names nothing. |
| **Will the referenced document always exist?** | **NO** — 115 strains carry no identifier at all, and a single-strain subject with no pedigree may not warrant one. The assertion must stand alone. | **YES** — one `epoch` is minted per distinct `epochid.epochid`, by construction. The edge cannot dangle. |
| **Is the value the document's CONTENT, or a JOIN KEY?** | **Content.** A `term_assertion` *is* a statement about that value. Strip it and the document says nothing. | **A join key**, stapled on. Strip it and the document still says everything it said. |

**The drift test is what actually decides it.** The rule from
`V_eta_openminds_family_record.md` Part 3: a representation must not vary between
datasets.

- **Dropping strain's inline value WOULD create drift** — some strain assertions
  would have a `strain` document behind them and some would not, so `variable:
  strain` would resolve two different ways depending on whether a pedigree happened
  to exist. The inline value therefore stays and the edge is ADDITIVE.
- **Dropping epochid creates NO drift** — every epoch-scoped document gets the edge,
  uniformly, always. One representation, no cases.

**In one line:**

> **strain: the value IS the fact, and the document is optional extra structure.**
> **epoch: the document IS the fact, and the string was only ever a way to find it.**

**The general test, for the next class that looks like either.** Keep BOTH when the
value is a complete fact, the referent may not exist, and the value is the
statement's content. Keep ONLY the edge when the value is a local id, the referent
is always minted, and the value is a join key.

Query consequence, and it is an improvement: *"everything in epoch t00023"* becomes
two INDEXED lookups — find the epoch by `local_identifier`, then match `epoch_id` —
rather than an `exact_string` scan across 15 classes.

The supporting check is unchanged and one-sided:

```
$ grep -rn "'epochid'" --include=*.m src/          # 23 mentions in NDI
  every one is ndi.document('<realclass>', ..., 'epochid', epochid_struct)
  stimulusBathToBath.m:74 lists it in a SUPERCLASSES array
  ZERO constructions of ndi.document('epochid', ...) as a primary class
$ grep -rn "class_name','epochid'" src/did/+did2/+convert/   # no migrator emits one
```

**Migration ordering this forces:** every epoch-scoped document must have its
`epoch_id` edge populated BEFORE `epochid` is removed, or the epoch association is
lost outright. That is a second-pass ordering constraint, not a schema one — and
given the 12,296-document invented-empty-edge pattern (see `CLAUDE.md`), the first
corpus run must check `epoch_id` by name in `silentLoss` rather than trusting
`quarantine=0`.

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

## THE CLASS, FINAL — read this block, not the one above

The model block above predates the rename and the `instrument_id` revision, and still
says `acquisition_epoch`. **This is the authoritative shape** (team, 2026-08-06:
*"Epoch looks good. Record it."*):

```
epoch ⊂ entity                                          MINTED, one per epoch id
   local_identifier    char     "epoch_4126958b19a21a41_..."   <- the v1 epochid string
   global_identifier   char     empty -- an epoch has no external cross-reference
   depends_on:
      session_id       -> session                        REQUIRED
      time_reference_# -> relative_reference             the epoch's own extent
      instrument_id    -> acquisition_system | subject   OPTIONAL
```

Everything else in this document (element_epoch dissolves, epochid drops, the
epochfiles_ingested fold) is unchanged.

**One typing wrinkle, flagged not resolved:** `subject_interaction.instrument_id`
declares `must_refer_to_document_class: subject`, but an epoch's instrument may be an
`acquisition_system`, which is `⊂ base` and NOT a subject. So `epoch.instrument_id`
spans a wider target set than the statement-tier edge of the same name. `must_refer`
is existence-only so nothing breaks, but two edges sharing a name and not a target set
is a governance question for #32.

## REVISION 2026-08-06 — `epoch` gains an optional `instrument_id`

**The team's words:** *"I agree to that for epoch."* Arrived at by the team asking
*"does it make sense that a daqsystem owns a period of time?"* — it does not, and the
objection exposed that the model above was missing a fact rather than misnaming one.

```
epoch ⊂ entity
   depends_on: session_id
               time_reference_#
               instrument_id -> acquisition_system | subject      ADDED, OPTIONAL
```

**An epoch is not an interval; it is a RECORDING.** It is minted from one acquisition
device's files for one run (`ndi.file.navigator.m:271`, `id = ['epoch_'
ndi.ido.unique_id()]`, written to a hidden file beside them), and everything derived
from it — probes, elements, spike trains — **inherits that id rather than minting its
own** (`ndi.element.m:276,293`). Its temporal extent is a property of it, not its
identity. Two daqsystems recording the same wall-clock period get two DIFFERENT
epochs, which is the only reason a syncgraph has to exist.

So the device is the epoch's **agent**, not its owner, and the edge is T7's existing
`instrument_id` — the same edge the observations derived from that epoch already
carry — not a new relation.

**OPTIONAL, deliberately.** A `whole_session_*` epoch (below) has no instrument.
Making it required would force a false edge on those documents, which is the
invented-required-edge pattern now found five times.

**Alternatives checked, not asserted:**
- *Rename to `acquisition`?* NO. The synthetic epoch below corresponds to no
  acquisition, and it is a supported feature with its own test
  (`tests/+ndi/+unittest/+element/OneEpochTest.m`), not a stray. Every such document
  would assert something false. Splitting into two classes is a T12 look-alike family
  and forces a polymorphic edge on every epoch-scoped document.
- *Is it a statement rather than an entity?* NO. `ndi.daq.system.m:301`,
  `buildepochtable` is `filenavigator.epochtable` — built entirely from files, with no
  subject anywhere. A leaf requires `subject_id`. And #30 already models the
  recording-of-a-specimen as an observation; making `epoch` an act would be two
  representations of one event at different grains.
- *A `time_reference`?* NO — backwards. `epoch` carries `time_reference_#` edges; it
  is their referent, not one of them.
- *No document at all?* NO. `clock_alignment` and the syncgraph relate two epochs'
  timelines; without an epoch document there is no referent for either end, which is
  the string-joining this decision exists to remove.

`entity` is positively right, not right by elimination: ② is *things with durable
identity that other documents refer to*. An epoch's id *"will never change once
established"* (`epochset.m:44`), is inherited down the derivation chain, and is joined
to by 11+ classes. `dataset` and `session` are already in ②; `dataset ⊃ session ⊃
epoch` is one containment chain and the third level belongs with the first two.

### HAZARD for the build — synthetic epoch ids COLLIDE

The model resolves epochs *"by GROUPING on `epochid.epochid`"*. That is safe only if
the string is unique per epoch. **It is not always.**

```
ndi.file.navigator.m:271    id = ['epoch_' ndi.ido.unique_id()]
                            unique per recording  ->  grouping is SAFE

ndi.element.oneepoch.m:42   epoch_id = ['whole_session_' session.reference]
                            DETERMINISTIC -- every element in a session produces the
                            SAME string  ->  grouping would FUSE all of those elements'
                            epochs into ONE document
```

`oneepoch` mints a synthetic whole-session span so an element with no natural epoch
structure can still be addressed. It is not a recording, which is exactly why it
collides and why it has no instrument.

**Count UNMEASURED** — this needs a census of `epochid.epochid` values by prefix,
which no current report emits. The mechanism is certain; the exposure is not. Do not
build the grouping without either measuring it or keying the group on
`(epochid.epochid, owning object)`.

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
  would still be dropped, and a separate class is still required. **The last sentence
  here read "#57 remains a PROPOSAL" until 2026-08-09; it was stale.** #57 was SIGNED
  2026-08-08 (both families) and its schema half is BUILT. The technical point above is
  unaffected — `directed_relation` still has no value slot, so `clock_alignment` is
  still its own class, which is what got built.
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

**BUILD CONSEQUENCE — CORRECTED.** An earlier revision of this line said the rename
map entry becomes `"element_epoch": "epoch"`. **That is wrong and contradicts the
model two sections up.** A rename would preserve `element_epoch` as a per-element
class wearing a new name — precisely the conflation this revision exists to fix.

What actually happens:

```
build_v_eta.py RENAME map:  DELETE  "element_epoch": "acquisition_epoch"
                                    (no rename target -- element_epoch DISSOLVES)

NEW CLASS:                  epoch ⊂ entity, MINTED by the second pass,
                                    one per distinct epochid.epochid

element_epoch_id -> acquisition_epoch   does NOT retarget to `epoch`.
   `ensemble` uses it to point at ONE ELEMENT'S epoch record, not at the epoch.
   Where that record dissolves, the edge must retarget to whatever absorbs it
   (the observation / sampled_body), NOT to the new epoch entity.
```

That last point needs checking against `ensemble` before the build: an edge named
`element_epoch_id` pointing at a class that no longer exists is exactly the dangling
reference T10 warns about, and `ensemble` is the only holder of it.

---

# `epochfiles_ingested` → RENAMED `ingestion_manifest` (team, 2026-08-06)

**The team's words:** *"I agree ingestion_manifest is a better name."*

`epochfiles_ingested` encodes a MODE in the class name — the same T13 error `_ndr` and
`_mfdaq` were de-encoded for in ⑥/⑦ chunk (c). The document is a manifest of what was
ingested for one epoch; that is what it should be called.

```
ingestion_manifest ⊂ base                                ⑦ infra
   files  string[]                          the manifest        <- v1 files[]
   depends_on:
      filenavigator_id -> file_navigator    REQUIRED  <- RESTORED; NDI writes it
      epoch_id         -> epoch             REQUIRED  <- replaces the invented `epochid`
                                                         (6,921 docs, 100% empty)
   epochprobemap  REMOVED -- decomposed into edges (option B, below)
```

**It earns existence (T12):** the manifest records which files were physically copied
into the archive for this epoch. Nothing else carries that — the data bodies hold
payloads, not an inventory of what was ingested. Delete it and "what did this epoch
physically consist of" becomes unanswerable.

Unlike `file_navigator` / `metadata_reader` — deferred to R5 (#27) because their
meaning is unchanged and renaming twice is worse than once — this class's content
changes in the same build (the probemap comes out), so this is the cheapest moment,
the same argument used for `element_epoch` → `epoch`.

# `epochfiles_ingested` — DECIDED: option B (team, 2026-08-05)

**The team's words:** *"Go with B and drop the epochid mixin."*

Was recorded as open because the walkthrough moved on to the naming question before
it was settled; now decided.

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

## THE FORK, and the answer: **B**

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

### THE DECISION: B as the model, A as pass-1 behaviour

**B as the model, A as pass-1 behaviour** — repair now so nothing is lost,
decompose in the second pass. B is the same shape as two decisions already taken:
the ensemble's epoch-scoped `member_of` edges (*"the recorded neuron set changes
epoch-to-epoch"*) and `distance_metadata`'s deferral to the second pass for exactly
this id-resolution reason. A probe's subject genuinely can change between epochs, so
the per-epoch mapping is real information rather than a redundant copy of the
migrated graph.

---

## RESOLVED 2026-08-08 — `instrument_id -> entity`, and `acquisition_system ⊂ entity`

**The team's words:** *"We can do epoch.instrument_id -> entity and move acquisition_system to
entity."* Recorded as a decision on the open typing wrinkle above. **NO sign-off line for the
epoch family** — that is separate and the team has not given it.

The wrinkle was: `subject_interaction.instrument_id` declares
`must_refer_to_document_class: subject`, but an epoch's instrument may be an
`acquisition_system`. Two findings settled it.

**1. `must_refer_to_document_class` is a SINGLE class name. A union is not expressible.** So
"acquisition_system | subject" was never a declarable target, and the choice was really
"which common ancestor".

**2. The hierarchy, measured (226 classes per index.json):**

```
entity  ⊂ base
subject ⊂ entity          subject has NO subclasses
entity's direct children: dataset, funding, organization, person, publication,
                          session, software, subject, web_resource
acquisition_system        DOES NOT EXIST YET (#59)
epoch                     DOES NOT EXIST YET (#60)
```

### The decision

```
acquisition_system   ⊂ entity        alongside software and session
epoch.instrument_id  -> entity       OPTIONAL
```

**`acquisition_system` is NOT `⊂ subject`.** T1's bare subject is the thing statements are
ABOUT; a DAQ rig is what does the recording. Subclassing would say you can enrol the rig as a
research subject.

**But `instrument_id` MUST still be able to point at a subject**, which is why the target is
`entity` and not `acquisition_system`: `element.m` promotes probes to subjects with ids
preserved, and `electrode_offset_voltage` is a real observation whose subject IS the electrode.
A probe is a subject when observed and an instrument when recording. That is T7 — instrument is
a ROLE carried by an edge, not a type.

**CORRECTION.** Claude first proposed `epoch.instrument_id -> base`, by analogy with
`relative_reference.relative_to -> base`. `entity` is strictly tighter and still covers both
cases; `relative_to` needs `base` only because its referent can be an epoch or a stimulus,
which are not entities.

**Still a #32 item:** `subject_interaction.instrument_id -> subject` and
`epoch.instrument_id -> entity` are the same role name with different declared targets.
`must_refer` is existence-only so nothing breaks today, but if it ever becomes type-checked
that is the question to answer.

---

## SIGNED OFF 2026-08-08

TEAM-SIGN-OFF [epoch]: jess@walthamdatascience.com / 2026-08-08 -- MINT `epoch` as an entity (one per epoch id, local_identifier = the v1 epochid string, REQUIRED); acquisition_epoch dissolves and its clocks become relative_reference documents; epochid is DROPPED in favour of a uniform epoch_id edge; epochfiles_ingested becomes `ingestion_manifest` with filenavigator_id RESTORED; instrument_id -> entity, OPTIONAL.

### The class, as signed

```
epoch  ⊂ entity                                      MINTED, one per epoch id
   local_identifier   char    REQUIRED -- the v1 epochid string
                              ("epoch_4126958b19a21a41_...")
                              Declared ON epoch, not inherited: `entity` deliberately
                              declares no local_identifier so a child can ADD it as
                              required. See build_v_eta.py:283-288 and the
                              placementCollision note below.
   global_identifier  struct  inherited from entity; left empty -- an epoch has no
                              external cross-reference
   depends_on
      session_id       -> session               REQUIRED
      time_reference_# -> relative_reference    the epoch's own extent
      instrument_id    -> entity                OPTIONAL
```

### v1 ground truth, re-read from NDI `origin/main`

```
epochid              ⊂ base            deps: []                  { epochid }
element_epoch        ⊂ base, epochid   deps: [element_id]        { epoch_clock, t0_t1 }
                                       files: epoch_binary_data.vhsb
epochfiles_ingested  ⊂ base            deps: [filenavigator_id]  { epoch_id, files,
                                                                   epochprobemap }
```

Two things this confirms, against the V_eta classes as built:

1. **`epochfiles_ingested`'s real dependency is `filenavigator_id`.** V_eta declares
   `epochid -> acquisition_epoch` REQUIRED and drops the one NDI writes — the
   invented-empty-edge pattern, **6,921 documents, 100% empty**. The rename to
   `ingestion_manifest` RESTORES `filenavigator_id`.
2. **`axes` / `channels` / `storage` on `acquisition_epoch` exist in NO NDI template.**
   `element_epoch` carries `{epoch_clock, t0_t1}` and a `.vhsb` file, nothing more. The real
   per-clock extents live in `daqreader_epochdata_ingested.epochtable`, one `(clock, extent)`
   pair per entry — which is a `relative_reference` per entry, and is why
   `epoch.time_reference_#` is well defined under #52's uniqueness rule.

### THE `epochid` BLAST RADIUS — sweep re-run 2026-08-08, and the recorded figure was LOW

```
DENOMINATOR: 91 NDI templates on origin/main; 915 .m files

templates carrying the `epochid` SUPERCLASS: 15
   binnedspikeratevm  daqmetadatareader_epochdata_ingested  daqreader_epochdata_ingested
   element_epoch  ensemble  epochclocktimes  openminds_stimulus  spikewaves
   stimulus_bath  stimulus_parameter  stimulus_parameter_table  stimulus_presentation
   vmspikefilteringparameters  vmspikefit  vmspikesummary

live .m sites referencing `epochid.epochid`: 30      <- the record said "11+". LOW by ~3x.
   ~12 QUERY-JOIN   ndi.query('epochid.epochid','exact_string', ...)
                    metadatareader.m:164, reader.m:56, timeseries.m:58,
                    stimulusDocMaker.m:390,412, add_stimulus_approach.m:54,64,
                    spikeextractor.m:156,310,388, decoder.m:114
   ~18 direct reads document_properties.epochid.epochid
                    reader.m:82, marder/demo.m:44,45, tuning_response.m:94,243,317,
                    docTable/epoch.m:96, ...
   14 writer sites  ndi.document(..., 'epochid', epochid_struct)
```

This does not change the disposition — these are v1-runtime queries against v1 documents, the
same category as every other rename in V_eta — but it is the largest blast radius in the
family, and `epochid` genuinely is the join mechanism for the epoch-scoped half of the
database. Anyone building this should expect to touch all three groups.

**CORRECTION on the sweep itself:** the first run of the superclass half returned ZERO, because
it grepped for `"epochid.json"` with a leading quote while NDI writes
`"$NDIDOCUMENTPATH/epochid.json"` — a pattern that could not have matched. The same failure
mode as the `demo_ndi` grep. Re-run without the leading quote, it returns 16, of which 15 are
carriers and one is `epochid.json` itself.

### A CLAIM MADE AND WITHDRAWN IN THE SAME SESSION — `local_identifier`

Claude reported that `local_identifier` is declared on nine entity subclasses but not on
`entity`, concluded the "lift" of TaskList #10 had been implemented as replication rather than
a hoist, and proposed hoisting it to `entity` with `subject` tightening it to required.
**All of that was wrong**, and the evidence was in the generator:

```python
build_v_eta.py:283-288
# local_identifier is REQUIRED on subject -- schema-enforced (a subject must be
# nameable), not an ingest convention. This is legal because `entity` (the parent)
# declares no local_identifier, so subject is *adding* a required field, not
# overriding a parent-optional one (which DID placement forbids). The same field is
# declared OPTIONAL on the other entities below.
```

`entity` declares no `local_identifier` **on purpose**, and `build_v_eta.py:2280` names it as an
established pattern: *"child-required override — the same pattern used for local_identifier /
time_reference."*

> **SECOND CORRECTION, same session, on the REASON.** The paragraph above originally said
> `did2.schema.cache.resolvePlacement` *"raises `placementCollision` on any class redeclaring a
> name an ancestor has placed"*, so hoisting would turn `subject`'s declaration into a schema
> error. **That was quoted from the DOCSTRING and the CODE is narrower.** The check fires only
> within one `targetBlock`:
>
> ```matlab
> targetBlock = leaf;   % placement = concrete_class
> targetBlock = cls;    % placement = declaring_class  <- THE DEFAULT
>
> if isKey(entriesByBlock, targetBlock)
>     for j = 1:numel(existing)
>         if strcmp(existing(j).fieldDef.name, fieldName)
>             error('did2:schema:placementCollision', ...)
> ```
>
> An ancestor and a descendant using the default placement land in DIFFERENT blocks, so a
> redeclaration never trips it. And a cross-block duplicate name is checked **nowhere** — not in
> `+did2/+schema`, not in `+did2/+validate`, not in DID-schema's tools or tests.
>
> **So placement does not forbid the override; it silently PERMITS it**, producing two live
> storage locations (`body.entity.local_identifier` and `body.subject.local_identifier`) with
> nothing saying which is authoritative. That is worse than a rejection.
>
> **The conclusion is unchanged and the reason is stronger:** keep `entity` silent, because
> declaring the field in both places splits it in two silently rather than erroring.
>
> **The real gap is that DID has no CONSTRAINT REFINEMENT construct** — a way to say "the same
> field, tightened" as distinct from a new declaration. The project already knows this:
> `build_v_eta.py:576` — *"TIGHTENING a constraint rather than redeclaring it — is deferred to
> the binding [governance]"*. The minimal fix, if it is ever taken: when a class redeclares an
> ancestor's `declaring_class` name, MERGE into the ancestor's block entry instead of creating a
> second one, and require the child to NARROW (`mustBeNonEmpty` false→true allowed, true→false an
> error). That would let `entity` declare the optional handle once, let `subject` and `epoch`
> require it, and collapse the eight duplicate declarations on dataset / funding / organization /
> person / publication / session / software / web_resource. As it stands, *"every entity has an
> optional handle"* is a convention held by nine copies — a new entity subclass can omit it and
> nothing complains. #32-adjacent governance; it changes `fieldsFor`'s contract, which today
> returns one entry per declaration tagged with `declaringClass`.

**#10 is correctly closed. Do not hoist.** Two general lessons, both earned here: a defect
inferred from generated OUTPUT must be checked against the GENERATOR before it is reported —
and a claim about enforcement must be read off the CODE, not the docstring above it.
