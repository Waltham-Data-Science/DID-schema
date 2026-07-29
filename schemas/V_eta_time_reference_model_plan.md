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

## `frame` — which timeline within the referent

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

**Deciding this exposed a real hole, and it is bigger than an edge.** Chasing what a required
`relative_to` would point AT:

- **NDI never writes a `session` document.** `session.json` is a template, but the only thing any
  writer emits is `session_in_a_dataset` (`ndi.dataset.m`), and only when a session is added to a
  dataset. A plain `ndi.session` has no document representing itself.
- **No migrator emits one either** — nothing in `+did2/+convert/` mints a `session` document.

So `base.session_id`, a **required** field on **every** document in the corpus, holds an id for
which no document exists. The "discovery-mode orphans" that caused the session edge to be reverted
were therefore **not a validation-mode artifact** — the referent genuinely is not there.

Consequence: required `relative_to` cannot be built as-is. It forces a prerequisite — **mint the
session document** — which is defensible on its own terms (every document claims membership in a
session and nothing describes that session) but is separate, scoped work with its own gate. Recorded
as its own item rather than smuggled into this build.

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

**C. May `start` and `end` have different referents/frames?**
 - **C1** no — one referent + one frame per reference; a `valid_interval` whose endpoints differ
   becomes **two** references on the statement. Keeps the class simple and gives item 2 a concrete
   meaning, but only if the edges are role-named rather than numbered.
 - **C2** yes — but that nests a whole reference inside a reference, which is the bespoke inline
   structure this track has been removing everywhere else.
