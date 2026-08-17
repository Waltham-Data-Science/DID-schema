# V_eta — the time_reference family (SCOPING; nothing built)

**8 classes, all `in_progress`** — the ⑤ group of the walkthrough — plus `epochclocktimes`,
which chunk (a) deleted and should not have.

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

---

## First: a collapse proposal, and why it is WRONG

The obvious reading of the tenets is that this family is a T3 zoo. Two axes are encoded in
class names — anchor kind (`session`/`epoch`/`event`/`utc`) × offsets-present
(`bounded`/`relative`) — and the meta-principle's litmus seems to condemn it:

> *Which of the four axes is genuinely new — the subject, the statement direction, the
> data-type structure, or the relation?*

The subject does not vary. Direction does not apply. The data-type structure does not vary —
every member is *an anchor plus an optional interval*. Only the **relation** varies, and T4/T7
say a relation is an **edge, not a subclass**. Meanwhile bounded-vs-relative is pure
cardinality, which T12 item 3 names explicitly (*"same quantity, different cardinality →
same composite"*). That argues for collapsing 8 classes to 1, with the anchor as a broad edge.

**T11 forecloses this**, and I proposed it before reading T11:

> **T11** — *"**time_reference** = `<origin>_<mode>_reference`."*

That sits in T11's list of canonical name shapes, alongside `<data_type>_<direction>` for
leaves and the bare `<data_type>` for composites. It is **normative**: the tenets contemplate
this family AS a family and prescribe its naming grammar. A collapse to one parameterized class
would delete a shape the tenets explicitly bless.

So the family stays. **The defects below are not "this family should not exist" — they are
"this family does not obey its own declared shape."**

---

## The real diagnosis (T14): the structure is conventional, not declared

T14: *"A convention that lives in prose, in examples, or in code literals is not a convention —
it is drift waiting to happen. Anything a consumer must know in order to read a value is
declared in the schema."*

`<origin>_<mode>_reference` implies a contract: **`origin` determines what the anchor is, and
`mode` determines the interval shape.** Nothing declares that contract, so every member
improvised, and no two agree.

### Defect 1 — `mode` means something different in each origin

| origin | `_bounded` carries | `_relative` carries | obeys the grammar? |
|---|---|---|---|
| session | `relation` + `start`/`end` | `relation` only | **inverted** — bounded has the offsets |
| epoch | `epoch_clock` | `epoch_clock` + `t0` + `start` + `end` | bounded ✅; relative has **three** offsets |
| event | the event edge | the event edge + `start`/`end` | ✅ both |
| utc | *(no such class)* | *(no such class)* | outside the grammar entirely |

Read from `event`, which is self-consistent, `mode` should mean:

- **`_bounded`** = *the whole extent of the thing named* → **no offsets**
- **`_relative`** = *an interval measured from it* → **`start`, `end`**

Under that contract `session_bounded_reference` and `session_relative_reference` are **swapped**,
and `epoch_relative_reference` carries a third offset (`t0`) that nothing explains — it may be
the epoch's own origin, which would make it a property of the **epoch**, not of the reference.

### Defect 2 — the same field is governed two ways (T8)

```
session_relative_reference.relation : char, REQUIRED, enum-bound
session_bounded_reference.relation  : char, optional, NO constraints
```

Same name, same family, two governance levels. T8 is *"hard-validated, not advisory"* — one of
these is advisory. And `relation` exists **only** on the session pair, so whether it generalises
across origins is undeclared.

Note that under the corrected `mode` contract `relation` may be **redundant on `_bounded`**:
"the whole extent" is what bounded already means.

### Defect 3 — `element_id` names a retired class and points at the wrong thing

```
epoch_bounded_reference.element_id  →  must_refer: subject   (mustBeNonEmpty: true)
epoch_relative_reference.element_id →  must_refer: subject   (mustBeNonEmpty: true)
```

`element` is retired. The edge resolves only because `migrators_j/element.m` promotes elements
to subjects with ids preserved — i.e. **by accident of the migration**, not by design.

The referent is wrong independently of the name. These reference an **epoch**, and V_eta has
`acquisition_epoch` carrying exactly what an epoch reference needs:

```
acquisition_epoch.clocks : { name, t0, t1 }
```

The epoch identity also arrives **twice**: as the inherited `epochid` block (a string) and as
this dependency. Which is authoritative is undeclared.

---

## `epochclocktimes` — migrate it, do not restore it

did_v1 `epochclocktimes` is `{clocktype, t0_t1}` — an epoch's extent under a named clock — and
it is a **superclass of `pyraview`**, so real pyraview documents carry that block. Chunk (a)
deleted it as one of "the 4 time-redundant classes… all 0-usage"; 0-usage was true of the DID
schema, not of NDI. `check_tombstones.py` flagged the consequence independently
(`LOSSY migrated pyraview — superclasses the real document has: epochclocktimes`).

It must not come back as a class. Its content is already modelled:

```
epochclocktimes.clocktype  ==  acquisition_epoch.clocks[].name
epochclocktimes.t0_t1      ==  acquisition_epoch.clocks[].t0 / .t1
```

A third representation of one fact is what T13 exists to prevent.

**What is actually lost** (smaller than first stated — correcting my own overstatement): the
pyraview migrator already carries the sample cadence from `native_start_time` and `native_rate`.
What it drops is **`clocktype`** — which clock those numbers are in — and the epoch's own extent.
Its anchor is a generic `session_relative_reference` with `relation: 'during'` and
`is_approximate: true`: a placeholder where the document carries what an exact reference needs.

---

## Forks — decisions needed before anything is built

**A. Where does the epoch anchor live?**
An edge to `acquisition_epoch` puts the clock extent in one place and lets the reference just
point. But `acquisition_epoch` is a separate document and pyraview's migrator is
single-document — it cannot patch an epoch document it does not own. Options: (i) the migrator
**mints** an `acquisition_epoch` (risking duplicates when several documents share an epoch — a
dedup problem for the second pass); (ii) the reference carries clock + bounds **inline** and the
second pass reconciles; (iii) it stays approximate until the second pass and the loss stands.

*This is the only fork blocking the `epochclocktimes` repair.*

**B. Fix the session pair, and how?** If `_bounded`/`_relative` mean what `event` says they
mean, the session pair is swapped. Renaming is the honest fix and the **highest blast radius
change in the group** — `session_relative_reference` is the anchor nearly every migrator emits,
so it touches the whole migrator set, every fixture, and needs a corpus run. Moving the fields
instead of the names is cheaper but leaves two classes whose names lie about their contents.

**C. Does `relation` generalise, and where is it governed?** Either it is a property of all
references (add it everywhere, bind it once) or it is session-specific (say so). Under the
corrected `mode` contract it may be redundant on `_bounded` entirely.

**D. Is `epoch_relative_reference.t0` an offset or the epoch's origin?** If the latter it
belongs on `acquisition_epoch`, not here, and the class drops to `start`/`end` like `event`.

**E. `utc_reference` sits outside the `<origin>_<mode>` grammar** and carries `timestamp`
rather than `duration`. Absolute time is a genuine shape difference, not a naming lapse — but
T11's grammar does not cover it, so it needs to be a **stated exception** rather than an
accident.

---

## Sequencing

Fork A alone unblocks the `epochclocktimes` repair; nothing else depends on it. Fork B is the
expensive one and should be batched with a corpus run. C, D and E are small and can ride with
whichever lands first.

**Nothing here is built. Recorded for the walkthrough decision.**

---

TEAM-SIGN-OFF [epochclocktimes]: jess@walthamdatascience.com / 2026-08-17 -- `epochclocktimes` IS the same fact as `acquisition_epoch.clocks[]` -- `epochclocktimes.clocktype == clocks[].name` and `epochclocktimes.t0_t1 == clocks[].t0 / .t1`, the equivalence stated at :125-126 above -- so its content becomes `relative_reference` documents by the clause in `V_eta_epoch_plan.md`:869, "acquisition_epoch dissolves and its clocks become relative_reference documents". It does NOT come back as a class. THIS SIGNS THE EQUIVALENCE ONLY. Fork A above (where the epoch anchor lives -- mint / inline / stay approximate) is explicitly LEFT OPEN and still gates the build.

WHY THIS DOCUMENT NEEDED A FAMILY ENTRY BEFORE THE SIGNATURE MEANT ANYTHING.
`tools/status_board.py` joins a signature to a class through its FAMILIES table,
and until today no family cited this file -- so the whole model written above,
including the equivalence, was invisible to every generated artifact and
`epochclocktimes` rendered as `no signature found`. The first attempt at this
signature was appended to `V_eta_time_reference_model_plan.md` instead, because
that document IS cited. It joined to the WRONG LINE: the board takes the first
signature in a document, and that is `:468`, which enumerates four changes and
does not mention this class at all. The row then read `signed` while pointing at
a signature that does not cover it -- a worse state than the honest
`no signature found` it replaced. Hence a family of its own, citing this file.

PROVENANCE, because Operating Rule 4 says Claude must never add a TEAM-SIGN-OFF
line and this one was typed by Claude. It was authorised explicitly, in the same
message as the decision -- "I sign-off on the equivalence and give you permission
to note that for me" (jess, in session, 2026-08-17) -- and after being shown the
verbatim text of `:468` and told that it does not reach this class. The rule
exists so research cannot quietly become the record; the decision is the team's
and only the transcription is mine. Nothing else in that exchange was signed:
the same message asked for Fork A to be explained rather than decided.
