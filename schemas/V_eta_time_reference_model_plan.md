# V_eta — the time_reference model (DECIDED in walkthrough; build deferred)

*Supersedes the defect list in `V_eta_time_reference_family_plan.md`, which scoped the existing
8-class family. That file stays as the record of what was wrong; this one is the go-forward
model. Nothing here is built.*

## The model

**Two concrete classes under an abstract root**, replacing eight.

```
time_reference                    abstract, ⊂ base
├── absolute_reference            a wall-clock instant or interval; NO dependency
└── relative_reference            a time measured against something; ONE dependency
```

### `absolute_reference`

```
value : { start_utc          timestamp   canonical
          end_utc            timestamp   canonical; absent ⇒ a point, not an interval
          source_timezone    char        IANA tz name, BOUND to the tz value_set
          source_utc_offset  char        e.g. "-05:00", when the source gave only an offset
          source_start       char        the string exactly as the source gave it
          source_end         char
          approximate        boolean }
```

### `relative_reference`

```
depends_on: relative_to → base      what the time is measured against

value : { relation     ontology_term  OWL-Time; the qualitative position when no metric exists
          start        duration       offset from the frame's origin
          end          duration       absent ⇒ a point
          frame        ontology_term  WHICH timeline within the referent
          approximate  boolean }
```

## Why two, and only two

The old family crossed `origin` (session/epoch/event/utc) with `mode` (bounded/relative) into
eight classes. Neither axis is a class axis:

- **`origin` is a relation** — T4/T7: *"roles are edges, not subclasses."* It becomes
  `relative_to`.
- **`mode` is cardinality** — T12 item 3: *"same quantity, different cardinality → same
  composite."* It becomes "are `start`/`end` populated?"

And `mode` was not even self-consistent: in the **session** pair it meant *with metric* vs
*without metric*; in the **event** pair it meant *whole extent* vs *offset interval*. Two
meanings of one word inside one family — the axis was incoherent, not merely untidy.

What *is* a real difference in kind is **absolute vs relative**: absolute carries `timestamp`,
relative carries `duration`, and relative needs a referent to be interpretable at all. Two
classes earn their existence; eight did not.

**T11 says `time_reference = <origin>_<mode>_reference`.** That grammar describes the family as
it stood; it is a naming rule, not a mandate that those classes exist. T11 should be amended
along with this change rather than treated as blocking it.

## Following the value convention (T14)

Both classes carry **one `value` slot**, canonical form plus lossless source provenance inside
the cell — exactly `voltage` and `duration`:

```
voltage.value  = { volts,   source_unit, source_value, approximate }
duration.value = { seconds, source_unit, source_value, approximate }
```

Consequences:

- `is_approximate` moves **off the root and into the cell**, where every other value keeps it.
- `start`/`end` on `relative_reference` are `duration`-typed, so canonical seconds and source-unit
  preservation come for free — nothing new to design.
- The class is named for the **kind** (`absolute_reference`), not the canonical frame
  (`utc_reference`) — the same reason the class is `voltage` and not `volt`.

## `start`/`end`, not `start`/`duration`

The source data is **t0/t1 pairs everywhere** — `element_epoch.t0_t1`, `epochclocktimes.t0_t1`,
`acquisition_epoch.clocks{t0,t1}`. Storing start+duration makes every migrator compute `t1-t0`
and every reader compute it back. Allen's relations are also defined over intervals `[start,
end]`, so `end` is what the relation vocabulary talks about. Duration remains derivable.

## `relation` is ontology-backed

The current `enum: [before, after, at_start_of, at_end_of, concurrent_with, during]` fails T8
three ways: it is a bare char enum where T11 requires `{node, name}` + a binding; it covers **6
of Allen's 13** interval relations; and `concurrent_with` is ambiguous between
`intervalEquals` and `intervalOverlaps`.

It becomes an `ontology_term` bound to **OWL-Time** (`time:intervalBefore`, `intervalDuring`,
`intervalStarts`, …).

## AMENDED 2026-08-06 — the field is `clock`, not `frame`

**The team's words:** *"We can change to clock and clock_alignment."*

The section below chose `frame` over `clock` because it *"generalises past clocks — for
an organism it selects conception vs birth."* The reasoning is sound and the
generalisation is **anticipatory**: nothing in V_eta has a non-clock frame today, so
this is the same T12 error as minting a general container before there is a second
thing to put in it.

An intermediate proposal, `timeline`, was also rejected — a timeline reads as a span
with ordered events on it, which is what a session or an epoch is, not a coordinate
system. (`frame` has a second problem in THIS schema: `image` makes "frame" mean a
raster.)

```
field on absolute_reference / relative_reference:   clock
bound to:                                           did_clocktype   (ALREADY EXISTS, 9 members)
```

`clock` needs no new vocabulary, matches the value_set already built, and is what NDI
calls it. Read the section below for the ORIGINAL reasoning; the NAME is `clock`.
Downstream: `clock_alignment` and `clock_alignment_configuration` in
`V_eta_clock_alignment_cluster_plan.md`.

## `frame` — which timeline within the referent  (ORIGINAL reasoning; the name is now `clock`)

NDI times an epoch in **several frames at once** (`ndi.time.clocktype`): `utc`, `approx_utc`,
`exp_global_time`, `approx_exp_global_time`, `dev_global_time`, `approx_dev_global_time`,
`dev_local_time`, `no_time`. "10 seconds in" is ambiguous until the frame is named, because
devices drift.

`frame` generalises past clocks. For an **epoch** it selects `dev_local_time` vs `utc`; for an
**organism** it selects `conception` vs `birth` vs `hatching` (prenatal day 7). Which is why it
is `frame` and not `clock`.

*Note:* NDI encodes precision in the frame name (`approx_*`) while the value cell has
`approximate`. Two representations of one fact — to be reconciled.

## `relative_to` — not `event_id`

The referent is a **session**, an **`acquisition_epoch`**, a **subject** (developmental time), or
an **event**. `event_id` is wrong for three of the four. `relative_to` names the role at the
right altitude (T13), and role-named deps already exist in V_eta (`child`, `parent`,
`bounding_event`).

## `acquisition_epoch.clocks` DISSOLVES into time_references

`clocks` is an inline array duplicating what `time_reference` already expresses — the same smell
as every other bespoke structure this track has removed. An epoch's position in each frame
becomes a reference document hanging off the epoch:

```
dev_local_time   → relative_reference, relative_to → the device-subject
exp_global_time  → relative_reference, relative_to → the session
utc              → absolute_reference
```

**All three are references.** An earlier draft claimed `dev_local_time.t0` is always 0, making it
the epoch's intrinsic axis and reducible to a duration. **That is false**, and checking the
writers is what showed it: `+daq/+reader/+mfdaq/blackrock.m` sets
`t0 = ns_h.MetaTags.Timestamp` — the device's hardware counter, not zero. (`cedspike2` does use
0, and even notes it is approximate.) NDI's prose *"a device keeps its own local time only
within epochs"* says the clock is **scoped** to epochs, not that it **starts at zero** in them.

This also makes `frame` verifiable: as a dependency, existence is checked by the validator,
where a bare frame string could not be.

## NO TIMES ⇒ NO REFERENCE (decided)

The abstract reader base returns `{[NaN NaN]}`, so some epochs genuinely have no times. **A
reference is not emitted in that case** — absence, never a null- or NaN-valued reference.

A reference carrying NaN is a **hollow document**: it validates, it is counted, and it says
nothing. That is precisely the failure mode `did2.validate.silentLoss` and the FRAGMENT detector
exist to catch; emitting one would manufacture it deliberately.

Consequences: "does this epoch have timing?" is a **presence test**, not a value test; and
`mustBeNonEmpty` on the value becomes genuine and checkable rather than a declaration that NaN
quietly satisfies.

## Pass 1 vs pass 2

A pass-1 migrator knows the epoch **string** (from the inherited `epochid` block) but not the
`acquisition_epoch` **document id**, so it cannot populate `relative_to`. That is the same wall
`distance_metadata`, `ontology_label` and the `daqreader` caches hit.

The existing schema already hints at the pattern — `epoch_bounded_reference` carries both the
`epochid` superclass and a dependency. So: **the string is the pass-1 handle; the edge is the
pass-2 resolution.** Precise device time only starts flowing when the second pass runs; until
then statements keep the approximate session anchor they get today.

## Migration

```
session_relative_reference  ─┐
session_bounded_reference   ─┤
epoch_bounded_reference     ─┼─→  relative_reference
epoch_relative_reference    ─┤
event_bounded_reference     ─┤
event_relative_reference    ─┘
utc_reference               ───→  absolute_reference
```

Ids preserved, so nothing dangles. Real volumes: **107,308** `session_relative_reference` and
**20,411** `session_bounded_reference` across the five corpora; the epoch, event and utc classes
have **zero documents** — and **no migrator has ever emitted one**. Only the session pair is
exercised, which is why all epoch timing currently collapses to *"during the session,
approximately"* while 11,118 `acquisition_epoch` documents carry real clock data nothing points
at.

## EVIDENCE PASS — NDI already has this model (read from the writers)

Everything below was read from `NDI-matlab origin/main`, not inferred. It **confirms the two-class
model** and **closes three of the five open items** with facts rather than guesses. It also opens
two new forks that the model as drafted cannot express.

### NDI's own runtime time reference is (referent, frame, epoch, origin)

`+ndi/+time/timereference.m`:

```
referent    the ndi.daq.system / ndi.probe / ndi.element the time is measured against
clocktype   utc | exp_global_time | dev_global_time | dev_local_time
epoch       required iff clocktype.needsepoch()  (i.e. dev_local_time)
time        "the time of the referent that is referred to"   <-- the ORIGIN
session_ID
```

Serialised as `ndi_timereference_struct()` = `{referent_epochsetname, referent_classname,
clocktypestring, epoch, time}`, and stored inline by the `valid_interval` template.

The decided model was arrived at independently and lands on the same decomposition:

| NDI `timereference` | V_eta `relative_reference` |
|---|---|
| `referent` | `relative_to` (edge) |
| `clocktype` | `frame` |
| `epoch` | *folded into `relative_to`* — see below |
| `time` | **no home yet** — fork B |
| `session_ID` | `base.session_id` |

**`referent` + `epoch` collapse to ONE edge in V_eta, and the collapse is earned.** NDI needs two
slots because its referent is a live MATLAB object and the epoch is a string inside it. V_eta
reifies the epoch as an `acquisition_epoch` document, and that document already knows which
element it belongs to — so `relative_to → acquisition_epoch` carries both. This is a real
simplification, not an assumption, and it is a second reason `acquisition_epoch` must exist.

### Item 3 is CLOSED — `epoch_relative_reference.t0` is not a mystery

It is NDI's `timeref_struct.time`: the **curator-chosen origin** within the frame, from which
`start`/`end` are measured. The V_eta field's own documentation already says so — *"Curator's
reference origin within the epoch_clock (commonly 0; e.g. stimulus onset)"* — and it matches
`markgarbage.markvalidinterval(epochset, t0, timeref_t0, t1, timeref_t1)`, where the timerefs
supply the origin and `t0`/`t1` the offsets from it.

The earlier guess — *"likely the epoch's own origin, which would make it the epoch's property"* —
is **wrong**. It is not the epoch's intrinsic origin; it is a point the curator picked. It cannot
be moved onto `acquisition_epoch`, because two references into the same epoch may pick different
origins. What remains open is only its *representation* (fork B).

### The two classes that have documents differ ONLY by cardinality

Read from the live emitters, `migrators_j.private.jSessionAnchor` and
`ontology_table_row.makeEncounterWindow`:

```
session_relative_reference  { is_approximate: true,  relation: 'during' }
session_bounded_reference   { is_approximate: false, relation: 'during', start, end }
```

`relation` takes exactly **one** value — `during` — across all 14 emitter call sites and both
classes. So the sole difference between the 107,308 documents of one class and the 20,411 of the
other is *whether `start`/`end` are populated*. That is T12 item 3 verbatim, now measured rather
than argued. The collapse is empirically confirmed.

### NEITHER live emitter carries a dependency — fork A

Both build `depends_on` empty and let session identity ride on `base.session_id`. `jSessionAnchor`
records why:

> *"Session identity rides on base.session_id — no redundant session_id edge (it only produced
> discovery-mode orphans)."*

So a **required** `relative_to` would either strand all 127,719 existing anchors or force back the
session edge that was already tried and reverted.

### `valid_interval` gives start and end INDEPENDENT references — fork C

`markvalidinterval(epochset, t0, timeref_t0, t1, timeref_t1)` takes **two** timerefs, and the
template stores both (`timeref_structt0`, `timeref_structt1`). The drafted model has one
`relative_to` and one `frame` covering both ends. This is a genuine expressiveness gap with a real
API behind it. The template is also an **array** — one document holds N intervals.

*(Incidental, and it answers a standing question: `valid_interval` is `ndi.app.markgarbage`'s
record of which stretches of an epoch are good data, everything else being garbage. It is one of
the 4 UNVERIFIED coverage rows — no V_eta home, no migrator — so those documents strand today.)*

## Open

1. ~~**Chaining and termination.**~~ — **CLOSED by fork B.** Chains are the normal case and are
   well-founded, because every link is a real document (observation → stimulus → epoch) rather
   than a synthetic anchor. Terminates at a timeline-defining referent: an `acquisition_epoch`, a
   session, or an `absolute_reference`.
2. **Multiple references per statement.** `time_reference_#` is numbered, so multiples are
   structurally allowed; what two references *mean* has never been decided. There are now **three**
   live readings, not one — same instant in different frames; a start anchor and an end anchor
   (fork C); and recurrence. A bare number cannot distinguish them, which argues the role belongs
   in the **edge name** (T4/T7) rather than an index.
3. ~~`epoch_relative_reference.t0`~~ — **CLOSED and then KILLED.** It is NDI's
   `timeref_struct.time`, and fork B decided that value has no home on a reference at all: it is
   either 0 or a property of an event that already has a document.
4. **Frame validation** once `frame` is a term rather than a dependency on the epoch's own
   reference — `must_refer` is existence-only, so a cross-document field check has no mechanism.
5. **`approx_*` frames vs `approximate`** — two encodings of one fact.

## Forks opened by the evidence pass

**A. Is `relative_to` required?** — **DECIDED: REQUIRED.**

127,719 live anchors have no referent edge at all. The team's call is that a reference must name
what it is measured against; an implicit referent is the "structure is conventional, not declared"
smell T14 exists to kill.

**A CLAIM RECORDED HERE WAS WRONG, AND IS CORRECTED IN PLACE.** An earlier revision of this
section asserted that *no `session` document exists anywhere* — that NDI only ever writes
`session_in_a_dataset`, that no migrator mints one, and that `base.session_id` therefore points at
nothing. **All of that is false.**

`ndi.session.dir` creates and persists a session document the first time a session directory is
opened:

```matlab
g = ndi.document('session','session.reference', ndi_session_dir_obj.reference) + ...
    ndi_session_dir_obj.newdocument();
ndi_session_dir_obj.database_add(g);
```

and the branch above it reads one back out of the database
(`session_doc.document_properties.session.reference`). It is a real, persisted, searchable
document, and the coverage ledger already carries it:

```
| `session` | `session` | persist | ndi |
```

— a did_v1 source class that migrates **1:1 into V_eta with its id preserved**, by passthrough.

So `relative_to → session` has a referent, and required `relative_to` needs **no prerequisite
work**. There is nothing to mint.

**How the error happened, since it is the third of its kind in this file.** The search that
produced it looked for `newdocument('session'` and a comma-terminated `ndi.document('session',`;
the real call site matches neither, because the arguments continue on the same line with a
different shape. A grep that *could not have found* the writer was read as evidence the writer did
not exist — absence of evidence promoted to a claim, the exact failure this project has now
recorded four separate times.

Worse, it was used to OVERRIDE a correct note. `jSessionAnchor` says its session edge produced
**discovery-mode** orphans, and this section rewrote that as "not a mode artifact — the referent
genuinely is not there, in any mode." The original comment stands: in discovery mode the batch is
a subset that need not contain the session document, so the edge dangles there while resolving in
a full migration.

**What is still unverified** (stated as unknown, not resolved by assertion): whether every corpus
actually contains its session document, and therefore whether a required `relative_to → session`
would resolve for all 127,719 anchors in a full run. The `by_class` counts in the corpus report
answer this directly and should be read before the build.

**B. Where does the curator's origin live?** — **DECIDED: NOWHERE. There is no origin field, and
`t0` dies with no replacement.**

The team's reading, and it is correct: *the anchor is not a property of the reference.* If the
stimulus started 12.4 s into the epoch, that is a fact about **the stimulus** — a
`subject_manipulation`, which is already a document — not bookkeeping inside whatever else happens
to be measured against it.

**The writers settle it.** Every construction of `ndi.time.timereference` in NDI, and what it
passes as the anchor:

| call site | anchor |
|---|---|
| `+daq/+system/mfdaq.m:282` | `0` |
| `+element/timeseries.m:40` | `0` |
| `+probe/timeseries.m:41` | `0` |
| `+probe/+timeseries/mfdaq.m:54` | `0` |
| `+probe/+timeseries/stimulator.m:184` | `0` |
| `+element/oneepoch_bkup.m:64, :126` | `0` |
| `+time/syncgraph.m:697, :798` | `0` |
| `+app/+stimulus/tuning_response.m:241` | `0` |
| `+time/syncgraph.m:681` | propagates an existing one |
| `+probe/timeseries.m:106` | propagates an existing one |
| **`+app/+stimulus/tuning_response.m:92`** | **`presentation_time(1).onset`** |

**One** call site in all of NDI passes a non-zero anchor, and it passes the stimulus onset — which
is already stored on the stimulus document:

```
stimulus_presentation.presentation_time = { clocktype, stimopen, onset, offset, stimclose, stimevents }
```

So the anchor is never independent data. It is **zero** (the epoch's own origin — nothing to
store) or **a property of an event that already has a document** (point at it with `relative_to`).

An `origin` field would have added a slot to 100% of references to carry a number that is 0 in
every case but one, and in that one case duplicates a fact owned by another document. That is the
T13/T14 failure this track keeps finding, and `epoch_relative_reference.t0` is the same invention
one version earlier.

**How the worked example is written instead** — the stimulus onset at 12.4 s into epoch 3, and the
curator's "good data from 5 s to 300 s after onset":

```
the manipulation (the stimulus):
  relative_reference  relative_to → acquisition_epoch "epoch_0003"
                      frame = dev_local_time,  start = 12.4 s

the observation (the good data), EITHER:
  relative_reference  relative_to → acquisition_epoch "epoch_0003"
                      start = 17.4 s,  end = 312.4 s
                  OR:
  relative_reference  relative_to → the subject_manipulation
                      start = 5 s,  end = 300 s
```

Both are true and denote the same instant. Which is stored is a question of the honest source: if
the curator said *"5 s after onset"*, writing 17.4 invents precision the source never had and
severs the link to the stimulus.

**This also resolves open item 1 (chaining).** Chaining was listed as a worry — depth, cycles,
termination — because the drafted alternative was a *synthetic* anchor document existing only to
hold a number. Under this model every link is a real document with independent meaning
(observation → stimulus → epoch), so chains are the normal case and are well-founded.
**Termination rule:** a chain ends at something that defines a timeline — an `acquisition_epoch`,
a session, or an `absolute_reference`.

**C. May `start` and `end` have different referents/frames?** — **DECIDED: NO. One anchor per
document. The edge renaming is DEFERRED as its own item.**

One `relative_to` + one `frame` govern both `start` and `end`. An interval whose two ends are
anchored differently — which `markvalidinterval(epochset, t0, timeref_t0, t1, timeref_t1)` permits
— becomes **two reference documents** that the statement points at.

The rejected alternative was a `start`/`end` pair each carrying its own anchor block. That nests a
whole reference inside a reference: the bespoke inline structure this track has removed from
`acquisition_epoch.clocks`, `epochclocktimes`, `distance_metadata` and the tuning bag. Matching
NDI's API shape is not worth reintroducing it, especially when the split case is rare and the
ordinary case — both ends off one anchor — is one clean document.

**The consequence, and it is deferred deliberately.** The statement edges are `time_reference_#` —
numbered, not named. With two references on one statement a bare index cannot say which document
is which, and there are **three** live readings it must distinguish:

1. the start anchor vs the end anchor (this fork),
2. the same instant expressed in two frames (an epoch is timed in several at once),
3. recurrence — it happened more than once.

A number cannot carry that; the role belongs in the edge name (T4/T7). But renaming touches
`subject_interaction` and `directed_relation` plus every migrator that writes them, so it is
**tracked separately with its own blast-radius check** rather than folded into this build. Until
it lands, multiple references on one statement remain undefined in meaning — a known, recorded
gap, not an oversight.

*Open item 2 stays open for that reason, and it is now the only thing between this model and a
complete design.*

---

# THE 2026-08-08 WALKTHROUGH — the model is now COMPLETE. Read this section, not the ones above.

TEAM-SIGN-OFF [time_reference]: jess@walthamdatascience.com / 2026-08-08 -- 8 classes collapse to absolute_reference + relative_reference; anchor and extent are separated (start + duration, NOT start + end); every value-level `approximate` is deleted; `clock` becomes a bound ontology_term over FOUR terms and the approx_ prefix de-encodes to an explicit clock_tolerance on the root.

Everything above stands except where this section overrides it. Reached by working the family
field by field; the team's questions drove four changes and caught two of Claude's errors.

## THE FAMILY, FINAL

```
time_reference  ⊂ base                                              ABSTRACT ROOT
   clock_tolerance   duration   optional; the stated precision of the TIMELINE these
                                times are expressed on. ABSENT = no stated tolerance.
                                For absolute_reference that timeline is UTC by construction.
      seconds           double
      source_unit       char
      source_value      double
      approximate       boolean

absolute_reference  ⊂ time_reference
   value
      start                            the ANCHOR
         utc                timestamp    canonical instant
         source_value       char         the instant exactly as the source wrote it
         source_timezone    char         IANA zone as the source gave it
         source_utc_offset  char         offset as the source gave it
         approximate        boolean      is the ANCHOR imprecise
      duration                         the EXTENT; ABSENT means an instant, not an interval
         seconds            double
         source_unit        char
         source_value       double
         approximate        boolean      is the EXTENT imprecise
      source_end            char       the end instant verbatim, when the source expressed
                                        the interval as two instants

relative_reference  ⊂ time_reference
   depends_on   relative_to -> base   REQUIRED
   value
      relation   ontology_term   BOUND owl_time_interval        { node, name }
      clock      ontology_term   BOUND ndic clocktype, 4 terms  { node, name }
      start      duration        ANCHOR: offset from the referent
                                 { seconds, source_unit, source_value, approximate }
      duration   duration        EXTENT; ABSENT means an instant
                                 { seconds, source_unit, source_value, approximate }
```

**THREE distinct precisions, none duplicating another:**

```
clock_tolerance          the TIMELINE is good to +/-5 s      applies to EVERY value on it
start.approximate        the ANCHOR is imprecise             this document only
duration.approximate     the EXTENT is imprecise             this document only
```

## CHANGE 1 — `end` becomes `duration`. ANCHOR and EXTENT are independent facts.

The team's case: *"I may have a time reference that is approximately 10 hours after another
event, but exactly 60 minutes in duration. Are we capturing that?"* **We were not.**

`start` and `end` are both offsets from the referent, so a fuzzy anchor makes both offsets
fuzzy and the exactness of their DIFFERENCE is unrecoverable. Replacing `end` with `duration`
is informationally equivalent (`end = start + duration`) and separates the two uncertainties:

```
start    { seconds: 36000, approximate: TRUE  }     ~10 hours after
duration { seconds:  3600, approximate: FALSE }     exactly 60 minutes
```

**`absolute_reference` takes the same change, for the same reason** — two wall-clock instants
inherit anchor fuzziness exactly as two offsets do. "Started around 09:00, ran exactly 60
minutes" is unrecoverable from `start_utc` + `end_utc`.

**`source_end` is NOT renamed to `source_duration`.** The source wrote an END INSTANT, not a
duration; putting that string in a duration's source slot would label it as a quantity it is
not — the same class of error as `distance_metadata`'s assumed nested shape. `end` is exactly
recoverable from the canonical values, so what `source_end` preserves is only the verbatim
formatting of the second instant. It stays, at value level, as provenance of the SOURCE'S
SHAPE rather than of one of our fields.

## CHANGE 2 — every value-level `approximate` is DELETED

`time_reference.is_approximate` (root) and `value.approximate` (both children) both go.
Approximateness lives ONLY where there is a quantity to qualify.

**The argument, in two cases:**

1. **`start` or `duration` present** — the cells already say which fact is approximate. A
   value-level flag can only restate them or contradict them.
2. **Neither present** — the assertion is purely qualitative (`relation: during`, no offsets).
   An Allen interval relation is either true or false; there is no quantity for "approximate"
   to qualify. *"Approximately during the session"* is not a weaker claim, it is not a claim.

**And the field is empirically vacuous.** Eleven writers, every one a hardcoded constant:

```
DENOMINATOR: 263 DID-matlab .m files
   migrators_i/treatment_drug.m:111      anchor.time_reference = struct('is_approximate', true);
   migrators_i/virus_injection.m:115     ... true
   migrators_i/treatment.m:219           ... true
   migrators_i/treatment_transfer.m:83   ... true
   migrators_i/ontology_table_row.m:212  ... true
   migrators_i/image_stack.m:132         ... true
   resolveDeferredBaths.m:153            ... true
   migrators_e/  (4 more)                ... true
```

Not read from any source — asserted. What they are expressing is *"we do not know exactly
when"*, which is already fully expressed by having no `start` and no `duration`.
**THE ABSENCE IS THE IMPRECISION.**

## CHANGE 3 — `clock` becomes a bound `ontology_term` (#67 is now BLOCKING)

`relation` beside it is already an `ontology_term` bound to OWL-Time, and `variable` is an
`ontology_term` everywhere. A bare `char` between them was the odd one out.

**#67 moves from follow-up to PREREQUISITE**, alongside #32: building `clock` as a char and
converting later means migrating every reference document twice.

## CHANGE 4 — the `approx_` prefix de-encodes to `clock_tolerance`; 9 terms become 4

```
clocktype.m:21   'approx_utc'              | Universal coordinated time (within 5 seconds)
clocktype.m:23   'approx_exp_global_time'  | Experiment global time (within 5s)
clocktype.m:26   'approx_dev_global_time'  | A device keeps its own global time (within 5 s)
epochset.m:554-558   'utc' -> 'approx_utc'; 'exp_global_time' -> 'approx_exp_global_time';
                     'dev_global_time' -> 'approx_dev_global_time'
```

The prefix is mode-in-a-name (T13) AND it hides a NUMBER in a docstring (T14). It must NOT
fold into `approximate` — that is a boolean with no magnitude and the five seconds would be
lost. It de-encodes to data:

```
approx_utc              ->  clock: utc              + clock_tolerance { seconds: 5 }
approx_exp_global_time  ->  clock: exp_global_time  + clock_tolerance { seconds: 5 }
approx_dev_global_time  ->  clock: dev_global_time  + clock_tolerance { seconds: 5 }
```

The migrator supplies the 5 from writer semantics — transcription, not invention, the same
call R6 made for dtype and the Hartley plane labels.

**`clock_tolerance` sits on the ROOT, not on `relative_reference`.** A UTC time good to +/-5 s
can land on EITHER class: as a wall-clock instant it is an `absolute_reference`; as offsets
measured in UTC seconds from a referent it is a `relative_reference` with `clock: utc`. Claude
first put it on the relative class only, which would have dropped the tolerance for every
absolute one; the team caught it.

**`no_time` and `inherited` leave the value_set.** Final vocabulary: **utc, dev_local_time,
dev_global_time, exp_global_time**.

`no_time` is REAL and load-bearing in NDI — but never as a timeline:

```
+daq/system.m:178 / +daq/reader.m:131 / +epoch/epochset.m:276 / +time/syncrule.m:113
      ec = {ndi.time.clocktype('no_time')};                       abstract-class defaults
+file/navigator.m:185
      epoch_clock = {ndi.time.clocktype('no_time')};  % filenavigator does not keep time
DID  migrators_i/image_stack.m:196,199,219
      % image_stack (no clocktype) maps to the 'no_time' clock
      if isempty(clockName); clockName = 'no_time'; end
      if strcmp(clockName, 'no_time')
```

In every case it is an `epoch_clock` asserting *"this thing keeps no time"* — never a timeline
a time is expressed on, because there is no time to express. Its V_eta translation is the rule
this document already carries, **NO TIMES => NO REFERENCE**: no document, not a value inside
one. `image_stack.m:219` already branches on it, so the migrator behaviour is a skip.

`inherited` is declared and **never constructed** — searching the literal `'inherited'` across
NDI `src` finds it only in `clocktype.m`'s own list and docstrings. Conceptually it is a
resolution instruction (*"take the timing from another device"*), i.e. a pointer, and
`relative_to` already IS that pointer and can name WHICH device, which an enum value cannot.
**CAVEAT, stated because this project's rule requires it: `inherited` is an ABSENCE-BASED
call.** The corpora are a sample. Check a corpus for the value before the term is dropped
rather than merely left unminted.

## CHANGE 5 — open item 2 (#52) shrinks to one rule

The four things multiple references on one document could mean, and what each turned out to be:

```
1. SPLIT-ANCHORED INTERVAL   NO INSTANCE EXISTS.  markvalidinterval(obj, epochset, t0,
                             timeref_t0, t1, timeref_t1) permits two anchors, and EVERY call
                             site passes the SAME reference for both -- including the
                             docstring (markgarbage.m:10), the in-tree test app
                             (+test/+app/markgarbage.m:49) and all six unit-test calls
                             (TestMarkGarbage.m:97,124,161,162,179,180).
                             Fork C's "two reference documents" was reasoned from the
                             SIGNATURE, not from a case. DO NOT BUILD start_anchor/end_anchor
                             until an instance appears.
2. SAME EXTENT, N CLOCKS     LIVE, on the epoch: epochtable is one (clock, extent) pair per
                             entry, several per epoch. THE DISCRIMINATOR ALREADY EXISTS
                             INSIDE THE REFERENCED DOCUMENT -- `value.clock`.
3. RECURRENCE                DISSOLVES. N occurrences are N statements, not one statement with
                             N times (T4).
4. EPOCH EXTENT + STATEMENT TIME    NEVER A CONFLICT: they are on different documents.
```

**So one rule covers everything real:**

> Within a `time_reference_#` family, every member describes the same instant or extent, and
> `value.clock` must be UNIQUE across the family.

Checkable, and it makes `epoch.time_reference_#` well defined as it stands. It is latent today
regardless: every migrator writes only `time_reference_1` (20+ sites across migrators_i, _e, _j
and resolveDeferredBaths). It goes live with the epoch build.

## TWO OF CLAUDE'S ERRORS, RECORDED SO THEY ARE NOT REPEATED

**1. "`scalar_temperature_observation` declares an untyped `time_reference_1`" — FALSE.**
`schemas/V_eta/examples/scalar_temperature_observation_series.json` is an EXAMPLE DOCUMENT
INSTANCE, not a class: its `depends_on` entries carry `value`s. A document names concrete
numbered edges; `_#` is the schema-side family. The sweep treated any file with a
`document_class` block as a class declaration.

**That also means the denominator quoted all session was wrong:**

```
files carrying a document_class block   224   <- what was repeatedly quoted
index.json schemas                      226   <- AUTHORITATIVE
                                              stable 214, draft 11, deprecated 1
                                              examples/ is NOT in the index
```

**2. "The `approx_*` clocktypes duplicate `approximate` and should decompose into it" — WRONG
as stated.** They carry a quantified five-second tolerance on the CLOCK, and `epochset.m`
degrades a clock to its approx variant as a mapping operation. That is a property of the
timeline, not of a value. The de-encoding is right; the destination was not. See Change 4.

## WHAT THIS DOES NOT SETTLE

1. **#67 and #32 are both PREREQUISITES now**, not follow-ups.
2. **#51 is still a CHECK**: verify a `session` document is present in every corpus before
   `relative_to` is made REQUIRED.
3. **`inherited`** wants a corpus check before the term is dropped (above).
4. **Whether `is_approximate` was ever `false`** on the 107,308 `session_relative_reference`
   documents. The field is being deleted either way, but if a v1 writer ever set it
   meaningfully, that meaning needs a home before the migrators are moved.
