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
- **Dropping epochid creates NO drift** — every epoch-scoped document reaches its epoch the
  same way, always. One representation, no cases. **AMENDED 2026-08-10:** that one way is the
  TIME_REFERENCE CHAIN, not a direct edge on every class. This line originally read "every
  epoch-scoped document gets the edge, uniformly, always", which is the reading the amendment
  narrowed. The drift argument is unaffected and is why it survives: what matters is that the
  route is uniform, not that it is short. A direct edge on some classes and a chain on others
  would be the drift; a chain everywhere is not.

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

**THE TWO LINES ABOVE ARE SUPERSEDED — do not build from them.** They are the draft this
section was written at, and BOTH halves have since been decided otherwise:

- `acquisition_epoch_id -> acquisition_epoch` — the 2026-08-08 sign-off DISSOLVES
  `acquisition_epoch`; the epoch entity is `epoch`. Superseded before this amendment, and by
  the sign-off in this same document.
- `every epoch-scoped document gains` the edge — narrowed 2026-08-10: a document reaches its
  epoch through the TIME_REFERENCE CHAIN, and a direct edge exists only where the epoch is the
  document's own content (`directed_relation`). See the amendment at the bottom of this file.

The GROUPING mechanism survives both and is what `did2.convert.epochMint` implements — with one
correction the draft did not have: **the key is the PAIR `(base.session_id, epoch-id string)`,
not the string alone.** 142 of corpus B's 149 distinct epoch ids appear in more than one
session, so grouping on the string would fuse epochs from different sessions.

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

### THE CHECK WAS RUN, 2026-08-10. Two of its claims hold; it missed a consumer.

```
DENOMINATOR: NDI origin/main, 1,002 .m files and every ndi_common template + schema

element_epoch_id, searched as a BARE STRING (not as a depends_on sweep):
    src/ndi/+ndi/+element/ensemble.m:273          WRITER  set_dependency_value(...)
    src/ndi/+ndi/+fun/+ensemble/allElement.m:98   READER  dependency_value(...)
    ndi_common/database_documents/ensemble/ensemble.json:18   its own template
    ndi_common/schema_documents/ensemble/ensemble_schema.json:6  its own schema
    -> 2 .m files, 2 JSON files, ZERO other declarations
```

**CONFIRMED — `ensemble` is the only holder.** Four hits, all its own.

**CONFIRMED — it points at one element's epoch RECORD, not at the epoch.**
`buildMapDoc(obj, epochid, epochclock, epochdoc, ...)` sets the edge from
`epochdoc.id()`, and `allElement.m`'s cleanup names the referent in its own words:
*"remove existing ensemble map documents and their element_epoch parents"*, then
`S.database_rm(ee_id)` — *"remove the element_epoch doc and its binary"*. The
referent is the PAYLOAD-BEARING per-element record: `element_epoch` declares
`epoch_binary_data.vhsb` plus `epoch_clock` and `t0_t1`. So the plan's instruction
stands: `element_epoch_id` retargets to whatever absorbs that payload (the
`sampled_body` cache under the ensemble model), NOT to the new `epoch` entity.

**NOT CONFIRMED — `ensemble` is NOT the only thing that breaks when `element_epoch`
dissolves. `oneepoch` inherits from it, and that is recorded nowhere:**

```
ndi_common/database_documents/oneepoch.json     superclasses: [ element_epoch ]
ndi_common/schema_documents/oneepoch_schema.json
                        "superclasses": ["element_epoch","base","epochid"]
oneepoch's OWN block: one field, `epoch_ids`
```

`element_epoch` is `oneepoch`'s ONLY declared superclass in the template — so
`element_id`, `epoch_clock`, `t0_t1` and the `.vhsb` file declaration all reach
`oneepoch` by inheritance and it declares none of them itself. And it is
production-written: `src/ndi/element.m:387` builds one
(`E.newdocument('oneepoch', ..., 'oneepoch.epoch_ids', epochids)`) and
`src/ndi/+ndi/+element/oneepoch.m:78-80` reads it back through
`finddocs_elementEpochType(..., 'oneepoch')`. **Dissolving `element_epoch` without
deciding where `oneepoch`'s inherited half goes strands a real class.** This is a
build prerequisite, not a decision already taken — it needs the team.

*The check found this only because it searched the BARE CLASS NAME across templates
as well as `.m` files. A `depends_on` sweep could not have: `oneepoch` reaches
`element_epoch` by INHERITANCE, not by edge. Third instance of the standing rule.*

### `oneepoch` — the team chose fork A1 (2026-08-10). NOT YET SIGNED.

Three options were put to the team and **A1 was chosen**. Recorded here as the
team's choice; the `TEAM-SIGN-OFF` line is theirs to write (Operating Rule 4),
and this decision additionally cannot be *built* until its own prerequisite is
signed — see the gate below.

**What A1 is.** `oneepoch` is not an epoch class; it is the record of a
CONCATENATION. `ndi.element.oneepoch` glues an element's N epochs into one, and
the document's single own field, `oneepoch.epoch_ids`, is the comma-joined list of
the sources. Everything else it has — `element_id`, `epoch_clock`, `t0_t1` and the
`epoch_binary_data.vhsb` payload — arrives by inheritance from `element_epoch`.

```
v1                                V_eta under A1
--------------------------------  ----------------------------------------------
oneepoch (one document)           <modality>_observation  ⊂ subject_observation
  element_id                        instrument_id -> the element-subject (id kept)
  epochid.epochid                   -- NO `epoch` entity is minted for it --
    'whole_session_<ref>'              the id is SYNTHETIC (oneepoch.m:42); it
     (SYNTHETIC)                       names a span nothing recorded as one epoch
  oneepoch.epoch_ids                derived_from_1..N -> the N per-epoch
    't00001,t00002,...'                observations of the same element
  element_epoch.epoch_clock         relative_reference x K, one per clock
    'utc,dev_local_time'               (the v1 value is a COMMA-JOINED LIST,
     (a LIST, not one clock)            oneepoch.m:124 -- unlike a plain
  element_epoch.t0_t1                   element_epoch, which carries one clock)
    a MATRIX, not a 2x1               each carrying that clock's start/end
     (oneepoch.m:109-115)
  epoch_binary_data.vhsb            sampled_body, `statement` -> the observation
```

**Why not mint an `epoch` for the synthetic id.** It would make `epoch` mean two
things — a recording, and a derived aggregate — which is the T12/T13 conflation
this plan exists to remove. `did2.validate.sourceCensus` already treats exactly
these ids as a **grouping hazard** (it cites `oneepoch.m:42` by line), so minting
would realise a hazard the instrument was built to warn about.

**THE GATE, stated rather than assumed.** `derived_from_#` is declared on
`subject_observation` as `-> subject_statement`. The N source per-epoch recordings
only BECOME statements under `V_eta_recording_observation_plan.md`, **which is not
yet signed** (checked 2026-08-10: it carries no signature line). Until it is, A1's
`derived_from_#` edges have nothing to point at. A1 is a decision about direction;
it is not buildable yet.

Separately, A1's body half lands on `sampled_body`, whose `datum` / `sample_time` /
`axes` fields `V_eta_data_body_model_plan.md` redefines — also unsigned. Building
the body shape before that lands means building it twice.

**What was built now, because it needs neither.** `oneepoch` had NO V_eta schema at
all, so a real document quarantines today on `undeclaredBlock` /
`superclassesChainMismatch` — the `epochfiles_ingested` failure. A source tombstone
restating the real inherited shape is a repair under every option, exactly as the
stimulus-parameters tombstones were. Its precise chain was MEASURED, not derived:
see scratch probe 8.

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

TEAM-SIGN-OFF [epoch]: jess@walthamdatascience.com / 2026-08-08, AMENDED 2026-08-10 -- MINT `epoch` as an entity (one per epoch id, local_identifier = the v1 epochid string, REQUIRED); acquisition_epoch dissolves and its clocks become relative_reference documents; epochid is DROPPED, and a document reaches its epoch through the TIME_REFERENCE CHAIN (subject_interaction -> time_reference_# -> relative_reference -> relative_to -> epoch) -- a direct `epoch_id` edge is added ONLY where the epoch is the document's own content (`directed_relation`, per the ensemble sign-off), NOT on subject_interaction; epochfiles_ingested becomes `ingestion_manifest` with filenavigator_id RESTORED; instrument_id -> entity, OPTIONAL.

### Amendment 2026-08-10 — "use the reference chain, don't add the direct edge"

Amended at the team's instruction (jess, 2026-08-10). Only the `epochid` clause changed;
every other clause above stands exactly as signed on 2026-08-08.

The line as originally signed read, verbatim — HISTORICAL-SIGNOFF-CLAIM:

> ... epochid is DROPPED in favour of a uniform epoch_id edge; ...

**Why it needed narrowing.** "Uniform" was read literally by the build as *every* epoch-scoped
document gaining the edge, `subject_interaction` included. A statement already reaches its
epoch through its time reference, so a direct edge would store one fact in two places — the
hazard this very document raises for `base.session_id` vs `part_of` and marks "Flagged, not
solved". Two copies of one fact agree by coincidence until something checks them, and nothing
would.

**`directed_relation` keeps its optional `epoch_id`, and that is not an exception being carved
out.** There the epoch is the edge's OWN content: the ensemble sign-off requires EPOCH-SCOPED
`member_of` edges because the recorded roster changes from epoch to epoch. On a statement the
edge would only restate when the statement happened.

**The weak link, recorded because it is what would later be mistaken for evidence against this
amendment.** The chain is guaranteed by `min_count: 1` on `time_reference_#`, and
`relative_reference.relative_to` is REQUIRED — but that family entry is `mustBeNonEmpty: false`,
so `time_reference_1 = ''` satisfies the family and reaches no epoch, and the ARMED
`RequiredDependencies` gate keys on `mustBeNonEmpty` and will not catch it. That is the
invented-empty-edge pattern one link along the chain. An epoch-less statement found later is
evidence the edge we HAVE is unenforced, not evidence the direct edge was needed. Tighten it
before re-opening this.

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

**A SECOND CORRECTION ON THE SAME SWEEP, 2026-08-12 — this one on its DENOMINATOR, and it is
a figure that MOVED rather than a method that was wrong.** The block above opens with a
denominator of 91 NDI templates on `origin/main` and a `.m`-file count that said 915. The
template half still derives to 91. The file half does not:

        $ git -C NDI-matlab ls-tree -r --name-only origin/main | grep -c '\.m$'
        1002

i.e. `git ls-tree -r origin/main | grep -c '\.m$'` = **1002**, a denominator of 1,002 NDI
files.

RE-DERIVED 2026-08-13: 91 NDI templates on origin/main; 1,003 .m files. The did_v1 ground truth did NOT move -- 0 template diffs across the NDI main merge, still 91; main gained one .m file, so only the denominator shifted.
RE-DERIVED AGAIN 2026-08-15: 91 NDI templates on origin/main; 1,005 .m files. NDI main moved to 928b1cd5 and two of its nine commits add test .m files (closeAndRemoveDir.m, TestRayoLabStims.m). The did_v1 ground truth is STILL unmoved -- 91 templates, 0 diffs; only the denominator shifted.

**The 2026-08-08 block is LEFT AS WRITTEN.** It is a dated measurement whose numerators — 15
carrier templates, 30 live `epochid.epochid` sites, 14 writer sites — were counted against
that denominator on that day, and rewriting one figure out from under the others would make
the block internally inconsistent while looking better measured than it is. **What the sweep
CONCLUDED is untouched**: a denominator that grew does not bear on "`epochid` is the join
mechanism for the epoch-scoped half of the database", and the three groups a builder must
touch are enumerated individually rather than as a fraction of the tree.

**Why this is written HERE and not only in `CLAUDE.md`:** that file corrected 915 to 1,002
earlier the same day, but inside its summary of a DIFFERENT document
(`V_eta_data_body_model_plan.md`). The correction reached the file that QUOTES the fact and
neither of the two that STATE it — this plan and the data_body plan — so a reader of either
had no way to know it existed. Both were found by `tools/check_prose_counts.py`, which
derives the count from NDI `origin/main` instead of reading prose about it.

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

---

# ADDENDUM — the #60 scoping walkthrough. Team, 2026-08-17.

Four questions were put to the team while scoping the `element_epoch` dissolution
on corpus 20211116. Three were answered by the team; the fourth was answered by
measurement and needed no decision. Recorded here rather than in a task
description, because a task list is not a durable record.

**PROVENANCE.** Claude scoped and proposed; the team chose. Operating Rule 1 and
Rule 4 were both waived explicitly for this entry — *"Note the sign-offs and write
to schemas"* (jess@walthamdatascience.com, 2026-08-17), following *"Take them one
at a time"* and, on Q2, *"What's the correct way?"* — a request for a
recommendation, which is recorded below as the team ADOPTING that recommendation
rather than as Claude deciding it.

## THE POPULATION, measured before anything was asked

        DENOMINATOR: 1220 json file(s) read from corpus 20211116
          252 element_epoch = 21 element_id target(s) x 12 (session,epochid) pair(s), exact
          epoch_clock   `dev_local_time` on all 252   (ONE value)
          t0_t1         [0, T]; t0 == 0 on ALL 252; T 352.66 .. 4037.08 s
          depends_on    element_id, and nothing else
          files         epoch_binary_data.vhsb on all 252, ingest: 1
          23 element document(s): 21 direct==false, 2 direct==true (n-trode, stimulator)
          documents REFERENCING an element_epoch id: 0 (2436 edge values scanned)

## Q1. THE BODIES ATTACH TO THE ELEMENT'S OBSERVATION

Half of this was already decided and is NOT re-opened: `element_epoch` is one of
the 15 v1 templates declaring a `file_list`, and all 252 documents carry the
file, so under the signed *"A body is emitted only when there are bytes to
attach"* (`V_eta_data_body_model_plan.md`, walkthrough item 6, 2026-08-14) it
EARNS a `sampled_body`. `element` declares no files and correctly emits none.

What was open is that `jRecordingObservation.m:262` sets `storage_mode:
'reference'` on the reasoning that *"the raw acquisition files are beside the
session, never in the database"* — false for an ingested session, where the bytes
are declared IN the database on `element_epoch`.

**TEAM: the bodies attach to the element's observation.** For an INGESTED
session the `<modality>_observation` becomes `storage_mode: 'body'` and carries
its per-epoch `sampled_body` documents — 21 statements, 252 bodies, not 252
statements. The rationale accepted: `storage_mode` exists to say where the bytes
are, and ingested-vs-not is a real difference in where they are — v1's own
two-state division (`navigator.m:218`, `:795-807`), which
`jRecordingObservation`'s header already cites approvingly.

ACCEPTED COST, stated rather than discovered later: the same class then carries
two storage_modes across datasets.

## Q2. `epochid` STAYS DROPPED, AND THE READER IS PORTED IN THE SAME CHANGE

The signature at `:869` says *"epochid is DROPPED"*. That breaks
`ndi.element.loadaddedepochs` for all 21 derived elements, in THREE places at
once rather than the one this document's own risk note names:

        element.m:459  if isfield(...document_properties,'element_epoch')
        element.m:463      newet.epoch_id = ...epochid.epochid;
        element.m:468      clocks_array = ...element_epoch.clocks;

The `:459` GATE is the dangerous one: once the block is gone the loop matches
nothing, `et_added` returns empty, and every derived element reports NO epochs
— silently. In this corpus 252 of the 263 documents carrying `epochid.epochid`
are `element_epoch` (96%).

**TEAM: keep it dropped; port `loadaddedepochs` in the SAME change; land a
characterization test FIRST.** Keeping the string was rejected on the ground
that this project's own inline-value-vs-join-key rule already decided it — a
bare local id is not a complete fact, one epoch is minted per distinct id by
construction so the edge cannot dangle, and the id is a join key rather than
content. Porting the reader first was rejected because it would be written
against a shape no document has, testable only from a fixture built from our own
model of that shape.

THE PRECONDITION IS THE POINT: `loadaddedepochs` had ZERO test coverage — it
appeared in exactly one file in NDI-matlab, `element.m` itself — so the change
would have landed blind either way. The characterization test landed first
(`NDI-matlab 0d97bc69f`, `TestMigrateLocalEta20211116`).

## Q3. THE METADATA MIGRATES IN PASS 1; THE BODY IS BUILT IN THE SECOND PASS

A third case the data_body plan never considered. That plan reasoned about
payloads OUTSIDE the database (`jRecordingObservation`) and about a checksum with
no file list (`jrclust_clusters`), and both correctly emit no body.
`element_epoch` is the opposite: the payload is INSIDE the database, so a body is
earned — and then `n` is REQUIRED on the axis and unreachable, because
single-document migrators carry files without reading their bytes.

The absent bytes in the corpus are an EXPORT artifact, not a fact about the data:

        DENOMINATOR: all entries in the 20211116 corpus zip
          entries: 2443 ; non-.json: 3
          all three are macOS junk (.DS_Store and two `._` resource forks)

**TEAM: split it.** Pass 1 dissolves the half needing no bytes — the
`relative_reference` from `t0_t1` + `epoch_clock`, the epoch anchor, the
observation edges. The NDI SECOND PASS, which holds a live session and the
ingested file, attaches the `sampled_body` with a COMPLETE axis. This follows the
data_body plan's own logic — *"n is safe to require because an axis is asserted
only when the array is held"*, and pass 1 does not hold it — and the
`jRecordingObservation.m:53` precedent, where the channel-axis count is already
*"a second-pass fill"*.

This CLOSES the open team call named at `V_eta_data_body_model_plan.md`
(*"whether a body should be emitted at all when the payload is outside the
database ... needs a team call and is NOT covered by the signature above"*) for
the INSIDE-the-database case. The outside case is unchanged: no body.

ACCEPTED COST: neither the bodies nor the `storage_mode` flip appear in a corpus
run, so the coverage ladder cannot see them — the same NDI-side blind spot that
makes `stimulus_presentation` read `no` on rung 3 today (`V_eta_OPEN_WORK.md`
row #107).

CONSEQUENCE OF Q1 + Q3 TOGETHER, stated so it is not discovered later: in pass 1
the observation stays `storage_mode: 'reference'`; the SECOND PASS flips it to
`'body'` when it attaches the 252.

## Q4. THE 384 SESSION ANCHORS ARE CORRECT — NO DECISION NEEDED

The post-mint chain census (built 2026-08-17 for exactly this question; corpus
run 32063177881) reports, on the SHIPPED batch:

        20211116   2761 inspected   12 `epoch` document(s)   0 REACH AN EPOCH
        PRED         42 inspected    1 `epoch` document       0 REACH AN EPOCH

That zero was initially read as "the anchor half has not started". IT IS NOT A
DEFECT, and the correction is recorded because it ran in the alarming direction
rather than the reassuring one. None of the sources behind those anchors carries
an epoch string at all:

        DENOMINATOR: 1220 document(s); anchors owned by 6 source classes
          hartley_calc 210, tuningcurve_calc 84, oridirtuning_calc 42,
          neuron_extracellular 21, element 23, jrclust_clusters 1
          carrying an epochid string: 0 of every one of them
          (210 receptive_field_calculation + 126 tuning_curve_calculation
           + 22 voltage_observation + 21 score_observation + 5 = 384, exact)

A session anchor is the ONLY honest anchor for them; re-anchoring would invent an
attribution the source does not have. The one family that CAN anchor to an epoch
is `stimulus_response_scalar` — `element_epochid` populated on 273 of 273, 11
distinct values — and it is precisely the family branch 2 suppresses today.

**So the anchor emission is not a separate item and not a large build: it is the
arming row.** No team decision was required and none is recorded.

## WHAT #60 THEREFORE IS, ordered by size

        the 384 session anchors        384 docs   NOTHING -- already correct
        stimulus_response_scalar       273 docs   the arming row in
                                                  epochMint.defaultArmingMigrators;
                                                  NO schema increment (the
                                                  migrator's own header derives
                                                  why: the fold path never copies
                                                  preBody.depends_on wholesale)
        element_epoch                  252 docs   the dissolution, split pass-1 /
                                                  second-pass, with the
                                                  loadaddedepochs port in the
                                                  same change

PREDICTION, NOT A RESULT: arming should take `REACH AN EPOCH` from 0 to 273 in
this corpus. The fold has three other guards (`element_id`, `response_type`,
`responses.response_real`) that may refuse some of the 273 before the anchor is
reached, and none of this has been run.

TEAM-SIGN-OFF [epoch]: jess@walthamdatascience.com / 2026-08-17 -- the #60 scoping walkthrough above. Q1: for an INGESTED session the element's `<modality>_observation` becomes `storage_mode: 'body'` and carries its per-epoch `sampled_body` documents (21 statements, 252 bodies), accepting that the class then carries two storage_modes across datasets. Q2: `epochid` STAYS DROPPED, `ndi.element.loadaddedepochs` is ported in the SAME change as the dissolution, and a characterization test lands FIRST (done, NDI-matlab 0d97bc69f). Q3: the dissolution SPLITS -- pass 1 emits the relative_reference, the epoch anchor and the observation edges; the NDI second pass attaches the `sampled_body` with a complete axis and flips the storage_mode, accepting that neither is visible to the corpus gate. Q4 required no decision: the 384 session anchors are correct because none of their sources carries an epoch string, so the anchor work is the `stimulus_response_scalar` arming row alone. This signature covers the four answers above and NOT the arming row itself, which is a build.

---

# AMENDMENT 1 to the #60 scoping walkthrough — Q1 IS CORRECTED. Team, 2026-08-17.

**PROVENANCE.** Claude measured, proposed and was asked for a recommendation
(*"I'm not sure. What's the right answer?"*, jess@walthamdatascience.com,
2026-08-17); the team then instructed that the recommendation be recorded
(*"Record that"*). Operating Rules 1 and 4 are waived for this entry on that
instruction. Recorded as the team ADOPTING the recommendation below, not as
Claude deciding it.

## What Q1 got wrong, and what it got right

Q1 (above, same day) places the 252 `element_epoch` bodies on **"the element's
`<modality>_observation`"**. **No such observation exists for any of the 252, and
none can be emitted today.** Measured from the corpus rather than from the plan:

        DENOMINATOR: 1220 json file(s) read from corpus 20211116
          element_epoch                      252
          distinct element_id targets         21   (12 documents each, exact)
          of those 21 targets, direct=true     0
          of those 21 targets, direct=false   21   all type='spikes',
                                                   ndi_element_class='ndi.neuron'
          element documents in total          23   (the other 2 are the DIRECT
                                                   n-trode and stimulator, and
                                                   NEITHER owns an element_epoch)

`jRecordingObservation` — the only emitter of a `<modality>_observation` — is
called from `+migrators_j/element.m:118` behind `if isDirect`, and that file
states the exclusion in its own words at `:111-113`: *"A DERIVED element
(direct = 0) is a computed signal or a sorted unit — **spike trains ride with
the ensemble model and its NDI second pass, not here**"*.

**Q1'S ARITHMETIC AND ITS STORAGE-MODE REASONING SURVIVE UNCHANGED, and that is
why this is a correction rather than a reversal.** "21 statements, 252 bodies" is
exactly right under the amendment: 21 neuron-subjects, each with one spike-time
observation carrying twelve per-epoch bodies. What was wrong is only WHICH
statement class hosts them.

## TEAM: the destination is the ensemble model's per-neuron body, and it was already signed

**This is not a new decision. It is `V_eta_ensemble_plan.md`'s signature, joined
to `element_epoch` for the first time.** That sign-off (jess, 2026-08-06, `:10`)
reads *"per-neuron spike times are the PRIMARY archival data (each
neuron-subject, event times to a sampled_body)"*, and its deferred-build list
asks for precisely the check performed here:

> 1. **Per-neuron spike-time observation** shape (event times → `sampled_body`)
>    on each neuron-subject — confirm the element migrator already lands this for
>    'spikes' elements; if not, add it.

**The confirmation was run and the answer is NO.** The 252 documents ARE those
per-neuron spike trains: 21 `ndi.neuron` elements × 12 epochs, every one
`type='spikes'`. The two plans were written two weeks apart and neither said the
other half.

## TEAM: `acquisition_epoch` stays the carrier until the ensemble second pass lands

Destination and interim are separate answers and both are recorded, because
taking only the first would strand the payload:

* **DESTINATION** — the neuron-subject's spike-time observation, per the
  ensemble sign-off. NOT a raw-recording `<modality>_observation`.
* **INTERIM** — `acquisition_epoch` continues to carry the 252, migrating 1:1
  exactly as it does today. This is row #60's own standing rule (*nothing may be
  deleted until the corpus proves the fold*) and it keeps
  `ensemble.element_epoch_id` resolving.

## TEAM: the `isDirect` gate is NOT reversed

Rejected, and on a measurement rather than on taste. Reversing it would emit
nothing, because `'spikes'` is not in the modality map at all:

        $ grep -n "spikes" \
              DID-matlab .../+migrators_j/private/jRecordingModality.m
        157:%   be the spikewaves bug (a body declaring zero spikes of zero
             samples each).

One hit, in a COMMENT. So `'spikes'` falls to `otherwise` → `disposition =
'unresolved'` → Guard A, which emits **no observation and 21 `modality
unresolved` term_assertions**. Reversing the gate is three changes deep — the
gate, a map row, and a leaf class — and the third does not exist. See the open
question below.

## OPEN, AND DELIBERATELY NOT ANSWERED HERE: what does a series of event times instantiate?

The ensemble plan names the host as *"a spike-time `subject_observation` of that
neuron"*, and **`subject_observation` is ABSTRACT** —
`+did2/+schema/cache.m` raises `did2:validation:abstractInstantiation` for any
document naming it. So the model is signed and the concrete leaf is neither
named nor built:

        DENOMINATOR: 249 json file(s) under schemas/V_eta/ read
          classes ending `_observation`: 33
          any of them for event TIMES  :  0

`count_observation` is the neighbour — `jrclust_clusters` already folds to it for
its integer label series — but a spike TIME is not a count, and picking it here
would assert a quantity nobody has agreed. Tracked as `V_eta_OPEN_WORK.md`
row #117.

## A SECOND CONSTRAINT ON WHATEVER IS BUILT, so it is not discovered later

`element_epoch`'s `.vhsb` is a GENERIC `(timepoints, datapoints)` series, not a
spike-specific one — `+ndi/+element/timeseries.m:274` writes both, from
`ep.timepoints` and `ep.datapoints`, for any derived element type. So the
destination must be keyed on element `type` the way `jRecordingModality` already
is. Hardcoding it to spikes would silently give the next derived element type a
spike-shaped home, which is the `pyraview` "the physical quantity is not carried
on the doc" hazard one class over.

TEAM-SIGN-OFF [epoch]: jess@walthamdatascience.com / 2026-08-17, AMENDMENT 1 to the same day's scoping walkthrough -- Q1 is CORRECTED. The 252 `element_epoch` payloads attach to the NEURON-SUBJECT's spike-time observation per the already-signed `V_eta_ensemble_plan.md` (jess, 2026-08-06), NOT to the raw-recording `<modality>_observation` Q1 named, which is emitted only for DIRECT elements and which none of the 252 owners is. Q1's cardinality (21 statements, 252 bodies) and its ingested-session `storage_mode: 'body'` reasoning stand unchanged; only the host class moves. `acquisition_epoch` REMAINS the carrier until the ensemble second pass lands, so nothing is deleted and `ensemble.element_epoch_id` keeps resolving. The `isDirect` gate in `+migrators_j/element.m:118` is NOT reversed. The concrete leaf class for a series of EVENT TIMES is NOT decided here and is open work (row #117); `subject_observation` is abstract and none of the 33 `*_observation` classes carries event times. Whatever is built must key on element `type`, because the `.vhsb` is a generic (timepoints, datapoints) series and not spike-specific.

## TEAM DECISION 2026-08-21 — build the probemap decomposition now (option B), staged

Recorded per the build process (a directive from the team, NOT a new sign-off line;
the option-B model was already signed above). On 2026-08-21 the team directed that the
`epochprobemap` decomposition be BUILT now rather than left as pass-1 behaviour A, on
the grounds that its stated blocker (#30) is built and the measure-first numbers are in
(corpus B, run 32427048919: 2,484 `epochfiles_ingested`, 9,936 probe rows, mean 4.0/doc,
min 1 / max 7; subjectstring join 13/13 distinct matched, 0 unmatched; 277 #30
observations all session-scoped, 0 epoch-scoped -> the per-epoch observations are
additive, nothing to duplicate).

Four calls the team made, each refining the signed model rather than changing it:

- **Decompose to edges now (option B), superseding "A as pass-1 behaviour"** for these
  documents. The manifest survives thinner; the probemap's content becomes edges on the
  observations the model already describes.
- **`devicestring` -> `acquisition_system_id` (device half) + a `channels` field
  (channel half)** on the observation, NOT `instrument_id`. `instrument_id` is the PROBE
  (`probe_ctx1`), per T7. This matches the signed shape at :776-777.
- **REPLACE, not coexist.** For an ingested probe, the epoch-scoped observations are the
  Bar-2 record and #30's coarse session-scoped observation for that probe is retired in
  the same pass (safe: #30 observations are unreferenced -- `jRecordingObservation.m`).
- **Build in verifiable increments** (nothing is validatable with MATLAB outside CI, and
  it is a ~10k-document second pass): (1) the load-bearing attribution -- epoch-scoped
  `<modality>_observation` per probemap row with `subject_id` + `instrument_id` + an epoch
  `during` anchor, replacing #30's session observation; (2) the device half
  (`acquisition_system_id` + `channels`, which needs a schema increment); (3) the
  rename+thin `epochfiles_ingested -> ingestion_manifest` (drop the probemap), only after
  1+2 prove the content is captured. Increment 1 needs NO schema change: `relative_to`
  is typed to `base` so `relative_to -> epoch` is valid, and epoch-scoping rides the
  existing `subject_interaction.time_reference_#`.

The emitter is a batch post-pass `did2.convert.resolveEpochProbemap`, ordered after
`epochMint` (it anchors to the minted epochs) -- the same posture as `distance_metadata`
and the ensemble, and the "SECOND PASS" the model names. Tracked as `V_eta_OPEN_WORK.md`
row #66 (the ingested-payload family).

### BUILD STATUS 2026-08-21 — all three increments landed (status, not a sign-off)

All three increments above are now built, plus a #30-retirement fix the first Soph
corpus run surfaced. NOT a new decision -- the model is the signed one above; this is a
record of what shipped, per "a finding is not recorded until it is committed."

- **Increment 1** (observation half): landed earlier; first real-data run on Soph
  (corpus run 47) emitted 174 epoch-scoped observations, 0 quarantine.
- **Increment 2** (device half): `subject_observation` gains OPTIONAL
  `acquisition_system_id` (-> acquisition_system, resolved from the devicestring's device
  name against `acquisition_system.base.name`) + a structured `channels` field (the
  team's existing draft `acquisition_channels` shape, reused so the two cannot drift).
  `resolveEpochProbemap` parses `intan1:ai27-28,45;di1-4` into the edge + grouped
  `{type, numbers}` channels.
- **Increment 3** (rename-thin): `resolveEpochProbemap` rewrites each source
  `epochfiles_ingested` to `ingestion_manifest` (schema already built) once its probemap
  is decomposed -- GUARDED on `filenavigator_id` + a resolved epoch, and a manifest that
  fails validation keeps the `epochfiles_ingested` tombstone (Bar-1 fallback), never
  quarantines.
- **#30 dedup**: the first Soph run left the #30 retirement 174/174 skipped-ambiguous,
  because a spike-sorted probe carries a #30 observation per derived neuron on the same
  instrument. The retirement now keys on the `(subject_id, instrument_id, class)` triple,
  superseding only the probe's own direct recording and leaving neuron spike-trains
  intact; it also resolves patch/sharp (voltage vs current are different classes).

Commits: DID-matlab `45a44bd` (resolveEpochProbemap + tests), DID-schema (this + the
subject_observation device-half fields + regenerated ledger/board/walkthrough).

**READ-PATH FOLLOW-UP (NOT built, NOT gated by the corpus run):** NDI's object layer
queries `epochfiles_ingested` by class name (`+ndi/+database/+fun/find_ingested_docs.m`,
`+ndi/+file/navigator.m`, `+ndi/session.m`). Reading a MIGRATED INGESTED session now
needs a vintage-map entry `epochfiles_ingested -> ingestion_manifest` plus field/edge
remapping (`epochprobemap` is gone, `epoch_id` is now an edge). This joins the existing
deferred ingestion-read-path items (`daq/reader.m:82` reads `epochid.epochid`); it does
not regress any passing test (the e2e runs PRED, which is not ingested), and the corpus
gate validates MIGRATION, not NDI reads.


RE-DERIVED 2026-08-21 (ndi_m_files, `check_prose_counts`): 91 NDI templates on origin/main; 1,012 .m files (`git ls-tree -r origin/main | grep -c '\.m$'` = 1012 at 5df51cf9; +7 since the 1,005 reading). The did_v1 ground truth is STILL unmoved -- 91 templates, 0 template diffs; only the denominator shifted.


RE-DERIVED 2026-08-21 (ndi_m_files, sibling drift): NDI `origin/main` advanced to `1c0fe1283` (PR #882, parallel-workers), so `git ls-tree -r origin/main | grep -c '\.m$'` = **1013** (was 1012). The did_v1 ground truth is UNMOVED -- 91 templates, 0 template diffs; only the denominator shifted. Re-derive, do not quote.
