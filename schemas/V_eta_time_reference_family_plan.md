# V_eta — the time_reference family (SCOPING; nothing built)

**8 classes, all `in_progress`.** (An earlier note said 9 — miscounted; the list is below.)
This is the ⑤ group of the `in_progress` walkthrough, plus one class that was deleted and
should not have been.

## The family as it stands today

| class | superclasses | dependencies | fields |
|---|---|---|---|
| `time_reference` | base | — | `is_approximate` |
| `session_bounded_reference` | time_reference | — | `relation`, `start`, `end` |
| `session_relative_reference` | time_reference | — | `relation` **(required, enum-bound)** |
| `epoch_bounded_reference` | time_reference, epochid | `element_id` → subject **(required)** | `epoch_clock` (required, bound) |
| `epoch_relative_reference` | time_reference, epochid | `element_id` → subject **(required)** | `epoch_clock`, `t0`, `start`, `end` |
| `event_bounded_reference` | time_reference | `bounding_event` → subject_interaction, directed_relation | — |
| `event_relative_reference` | time_reference | `reference_event` → subject_interaction, directed_relation | `start`, `end` |
| `utc_reference` | time_reference | — | `start`, `end` |

## Defect 1 — "bounded" and "relative" mean different things per anchor kind

The grammar reads as: **bounded** = *the whole extent of the thing named*, so it needs no
offsets; **relative** = *an interval measured from the thing named*, so it needs `start`/`end`.
Three of the four families disagree with that, and with each other:

| kind | bounded carries | relative carries | consistent? |
|---|---|---|---|
| session | `relation` + `start`/`end` | `relation` only | **inverted** — the bounded one has the offsets |
| epoch | `epoch_clock` | `epoch_clock` + `t0` + `start` + `end` | bounded ✅, relative has **three** offset fields |
| event | the event edge | the event edge + `start`/`end` | ✅ both correct |
| utc | *(no bounded class)* | *(no relative class)* | neither — `utc_reference` is absolute |

Two things to settle:

- **`session_bounded_reference` has `start`/`end`; `session_relative_reference` has neither.**
  That is backwards from epoch and event. Either the session pair is misnamed, or the other
  two are.
- **`epoch_relative_reference` has `t0` AND `start` AND `end`.** Three offsets where the event
  pair uses two. Whether `t0` is the epoch's own origin (making it a property of the epoch, not
  the reference) or a third offset is not recorded anywhere.

`utc_reference` breaking the `<anchor>_<kind>_reference` grammar (T11) may be correct — an
absolute timestamp is neither bounded by nor relative to anything — but it should be a stated
exception rather than an accident.

## Defect 2 — the same field is governed two ways (T8)

```
session_relative_reference.relation : char, REQUIRED, enum-bound
session_bounded_reference.relation  : char, optional, NO constraints
```

Same name, same family, two governance levels. And `relation` exists **only** on the session
pair — epoch, event and utc have no equivalent, so it is not clear whether it is a general
property of a reference or something session-specific.

## Defect 3 — `element_id` points at a class that no longer exists

`epoch_bounded_reference` and `epoch_relative_reference` both declare:

```
element_id  →  must_refer_to_document_class: subject   (mustBeNonEmpty: true)
```

`element` is **retired**. The edge resolves only because `migrators_j/element.m` promotes every
element to a `subject` with its id preserved — so it works by accident of the migration, and the
name now describes nothing in V_eta.

Worse, the referent looks wrong independently of the name. These classes reference an **epoch**.
V_eta has `acquisition_epoch`, a real document class carrying exactly what an epoch reference
needs:

```
acquisition_epoch.clocks : { name, t0, t1 }
```

Meanwhile the epoch's *identity* already arrives twice: as the inherited `epochid` block (a
string) and as this dependency. Whether a reference should carry the epoch string, an edge to
the epoch document, or both is undecided.

## Where `epochclocktimes` lands — and why it must not come back as a class

did_v1 `epochclocktimes` is `{clocktype, t0_t1}` — the extent of an epoch under a named clock —
and it is a **superclass of `pyraview`**, so real pyraview documents carry that block.

⑥/⑦ chunk (a) deleted it as one of "the 4 time-redundant classes… all 0-usage". That was wrong:
0-usage was true of the DID schema, not of NDI. The check_tombstones run flagged the consequence
independently (`LOSSY migrated pyraview — superclasses the real document has: epochclocktimes`).

**It should not be restored as a class.** Its content is already modelled:

```
epochclocktimes.clocktype  ==  acquisition_epoch.clocks[].name
epochclocktimes.t0_t1      ==  acquisition_epoch.clocks[].t0 / .t1
```

Re-adding it would be a third representation of one fact, which is what T13 exists to prevent.

**What is actually lost today** (smaller than first stated): the pyraview migrator already
carries the sample cadence from `native_start_time` and `native_rate`. What it drops is
`clocktype` — *which clock those numbers are in* — and the epoch's own extent. Its anchor is a
generic `session_relative_reference` with `relation: 'during'` and `is_approximate: true`: a
placeholder where the document carries what an exact reference needs.

## The forks — these need a decision before anything is built

**A. Does an epoch reference point at the epoch document, or carry the epoch inline?**
An edge to `acquisition_epoch` is cleaner and puts the clock extent in one place. But
`acquisition_epoch` is a separate document, and pyraview's migrator is single-document — it
cannot patch an epoch document it does not own. Options: (i) the migrator MINTS an
`acquisition_epoch` (risking duplicates when several documents share an epoch — a dedup problem
for the second pass); (ii) the reference carries clock + bounds inline and the second pass
reconciles; (iii) it stays approximate until the second pass, and the loss is accepted meanwhile.

**B. Which way round are `bounded` and `relative`?** Fixing the session pair to match epoch/event
is a rename plus a field move on classes that already have documents in every corpus
(`session_relative_reference` is minted by nearly every migrator as the standard anchor). This
is the highest blast-radius change in the group.

**C. Is `relation` a property of all references or only session ones?** And if it stays, it must
be governed one way — enum-bound on both, or neither.

## Sequencing note

`session_relative_reference` is the anchor almost every migrator emits, so a change to it touches
the whole migrator set and needs a corpus run. `epoch_*_reference` is comparatively contained.
The `epochclocktimes` repair depends on fork A and nothing else, so it can land first if A is
decided independently.

**Nothing here is built. Recorded for the walkthrough decision.**
