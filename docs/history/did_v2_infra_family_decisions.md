# V_eta — the infra families: proposed dispositions (evidence, not assertion)

Read from the real NDI `origin/main` templates. Nothing built. This covers three
of the eight genuinely-undecided families on the status board.

**The test applied throughout:** does the class record *what happened in the
experiment* (archival — V_eta keeps it), or *how NDI was configured to read it on
one machine* (runtime — V_eta does not)? A migration target is an archival
record, not a serialisation of the tool that produced it.

## The templates, as they actually are

| class | depends_on | fields |
|---|---|---|
| `syncgraph` | — | `ndi_syncgraph_class` |
| `syncrule` | — | `ndi_syncrule_class`, `parameters` |
| `syncrule_mapping` | `syncgraph_id`, `syncrule_id` | `cost`, `mapping`, `epochnode_a`, `epochnode_b` |
| `filenavigator` | — | `ndi_filenavigator_class`, `fileparameters`, `epochprobemap_class`, `epochprobemap_fileparameters` |
| `filter` | — | `label`, `type`, `algorithm`, `parameters` |
| `projectvar` | `element_id` | `project`, `type`, `user`, `lab`, `description`, `data` |

## The "sync" family is TWO decisions, not one

The status board grouped these three together by name. The templates say they are
not alike.

**`syncgraph` and `syncrule` are runtime configuration.** Their entire content is
a MATLAB class name plus its parameters — `ndi_syncgraph_class`,
`ndi_syncrule_class` + `parameters`. They record *which code was configured to
align clocks*, not any alignment that resulted. This is the same `ndi_<x>_class`
shape the ⑥/⑦ governance sweep already flagged as needs-NDI.

> **CORRECTED 2026-08-05 — TEAM DECISION.** The original proposal here was
> **"not archival V_eta classes"**, i.e. dissolve them. **That is wrong and would
> have dangled live edges.** It is the IDENTICAL mistake the daq family made and
> that `V_eta_daq_family_decisions.md` reverses — made twice, one family apart,
> from the same habit of reading a template's *contents* without checking its
> *referents*. Recorded as a reversal, not edited away.

### The reference check the original proposal skipped

```
$ for dep in syncgraph_id syncrule_id; do ... git show origin/main:<each template> ...
syncgraph_id   referenced by: syncrule_mapping
syncrule_id    referenced by: syncrule_mapping
```

Both are referenced BY EDGE from `syncrule_mapping`. Dissolving either dangles
that edge — the 11,448-orphan lesson (T10). **Their `base.id`s must be preserved.**

### And a LIVE QUERY depends on fields V_eta has already dropped

```matlab
% +ndi/+time/syncgraph.m:404-408  -- live code, feeding database_search
q_savedRules = ndi.query('','isa','syncrule_mapping') & ...
    ndi.query('','depends_on','syncgraph_id', ndi_syncgraph_obj.id()) & ...
    ( ndi.query('syncrule_mapping.epochnode_a.objectname','exact_string', ndi_daqsystem_obj.name) | ...
      ndi.query('syncrule_mapping.epochnode_b.objectname','exact_string', ndi_daqsystem_obj.name));
```

**V_eta's `syncrule_mapping` breaks this query in TWO independent ways:**

1. it **dropped `syncgraph_id`**, replacing it with the invented, always-empty
   `epochid` (5,316 documents — TaskList #58); and
2. it **dropped `epochnode_*.objectname`**, which the same query matches against
   the daqsystem's name.

So this is not "dropped data" in the abstract — it is dropped data with a **known,
in-tree consumer**, and it upgrades the severity of TaskList #58 accordingly. It
also makes `daqsystem.base.name` load-bearing in a THIRD place, after
`getprobes()` and the syncrule parameters.

### The decision — REVISED 2026-08-06, see `V_eta_clock_alignment_cluster_plan.md`

The PERSIST call below stands. **What is superseded is the rest of it**, in three
places, all recorded in the cluster plan:

1. *"`syncrule`'s `parameters` … land on the `clock_alignment` document the rule
   produced"* — **NO.** `syncrule` persists with its id, so the alignment POINTS at it;
   copying its parameters onto the result is duplication and a drift surface.
2. *"what survives is only … the preserved id plus the edge to the software entity"* —
   **too thin.** `parameters` is not an open bag but the union of four closed sets, so
   the shared parts become EDGES (two `acquisition_channels`) and DECLARED fields
   (`clock`, three thresholds); nothing is left to bag.
3. Both classes are RENAMED: `syncrule` → `clock_alignment_configuration`,
   `syncgraph` → `clock_alignment_policy`. `syncgraph`'s `syncrule_id_#` is NOT
   invented — `syncgraph.m:850` writes it and `syncgraph_schema.json:4` declares it
   `mustbenotempty: 0`; V_eta wrongly tightened that to required.

→ **`syncgraph` and `syncrule` PERSIST as ⑦ infra with `base.id` preserved.**
Their class names fold to deduplicated `software` entities exactly as the daq
family's do (`V_eta_daq_family_decisions.md`), and `syncrule`'s `parameters` —
including `daqsystem_ch1`/`ch2`, the only physical-wiring fields in the whole
daq/sync cluster — land on the `clock_alignment` document the rule produced
(`method` + `method_parameters`; see the sync-mapping section below).

**What survives in each document is therefore only what has nowhere cheaper to
live**: the preserved id that `syncrule_mapping` points at, plus the edge to the
software entity. That is the same shape the daq family landed on, and it is the
same shape for the same reason.

**`syncrule_mapping` is real measured data, and it is a RELATION between two
timelines.** `epochnode_a`, `epochnode_b`, `mapping`, `cost` is the *computed*
relationship between two epochs' clocks. That is not configuration; it is the
answer.

> **CORRECTED 2026-08-05 — the OLD claim is withdrawn; the NEW one is NOT DECIDED.**
> This section previously proposed that `syncrule_mapping` **folds into
> `relative_reference`**. That was written without checking it against the time
> model it cited, and **it does not survive the check** — the evidence below is
> solid and the fold is dead. The claim was right about the concept (it is an
> epoch-to-epoch time relation) and wrong about the shape.
>
> **What REPLACES it is a Claude proposal that the team has NOT decided.** An
> earlier revision of this document and of `tools/status_board.py` recorded
> `clock_alignment` as a team decision dated 2026-08-05. **That was wrong** — the
> team read the options and did not adopt one, and Claude promoted a discussion to
> a decision. Corrected here and on the board. Operating Rule 4 exists for exactly
> this, and it failed in the direction it always fails: toward looking further
> along than we are.

### Why the `relative_reference` fold fails

```
relative_reference  ⊂ time_reference ⊂ base
  depends_on: relative_to → base                        ONE referent
  value: { relation, start, end, frame, approximate }   ONE frame

syncrule_mapping  ⊂ base
  deps: syncrule_id → syncrule,  epochid → (untyped)
  cost double,  mapping matrix
  epochnode_a { time_reference{kind, epoch_clock, epoch_id}, epoch_session_id, ... }
  epochnode_b { ...same... }
```

1. **Two referents, one slot.** `relative_to` is singular; the mapping names two
   epochs.
2. **Two frames, one slot.** `frame` is singular; each epochnode carries its own
   `epoch_clock`.
3. **The payload is a different kind of thing.** `relative_reference` says *"X sits
   at time T on timeline Y."* `mapping` is an AFFINE TRANSFORM — `[1,0]` is slope
   and intercept — converting timeline A's coordinates into timeline B's. A
   relation BETWEEN timelines, not a position ON one.

The time plan's own **decision C** blocks the obvious workaround: *"ONE ANCHOR PER
DOCUMENT ... an interval whose ends are anchored differently becomes TWO reference
documents. Rejected nesting an anchor block per end."* Two `relative_reference`s
would record that each epoch exists somewhere in time and lose the transform, which
is the entire content.

`subject_calculation` (T10) fails for a different reason: it is
`⊂ subject_interaction ⊂ subject_statement`, so it requires `subject_id → subject`.
The referent of a clock alignment is a pair of epochs, not a subject.

### SUPERSEDED 2026-08-06 — see `V_eta_clock_alignment_cluster_plan.md`

**Everything from here to the end of this section is SUPERSEDED and contains three
statements now known FALSE.** Kept in place rather than deleted, because how they
failed is the useful part:

1. *"its endpoints are declared `entity` (an epoch is not one)"* — **FALSE.** The epoch
   family decided `epoch ⊂ entity` (`V_eta_epoch_plan.md`).
2. `from_epoch` / `to_epoch` → `acquisition_epoch` — that class is **retired**; the
   endpoints are now `relative_reference` documents, which carry epoch AND clock.
3. *"BLOCKED on the acquisition epoch family (nothing proposed)"* — that family is
   **decided**.

Also corrected there: `cost` is NOT a disposable artifact (read at three sites), and
copying `syncrule`'s parameters onto the alignment is duplication, because the sync
configuration decision persists `syncrule` with its id.

The cluster is now DECIDED with the team as `clock_alignment` +
`clock_alignment_configuration` + `clock_alignment_policy` + `polynomial` +
`acquisition_channels`.

### The ORIGINAL PROPOSAL (not decided; superseded — read the plan above instead)

T4: *"Relationships are first-class documents; the graph carries structure."* A
clock alignment is a relation between two epochs, so it belongs on the RELATION
tier, not the time-reference tier. The existing `directed_relation` cannot carry it:
its endpoints are declared `entity` (an epoch is not one) and **the relation tier has
no value slot at all**, so the transform and the cost would be dropped.

```
clock_alignment ⊂ relation
  depends_on:  from_epoch  -> acquisition_epoch
               to_epoch    -> acquisition_epoch
               software_id -> software
  value:       { slope, intercept }      the affine transform; ONE payload slot (T14)
  from_frame   ontology_term             epochnode_a.epoch_clock
  to_frame     ontology_term             epochnode_b.epoch_clock
  method       ontology_term             which syncrule (T8-bound)
  method_parameters  structure           daqsystem_ch1/ch2, minEmbeddedFileOverlap, ...
  cost         double                    the syncgraph path-finding edge weight
```

**Litmus** (*which of the four axes is genuinely new — the subject, the direction,
the data-type structure, or the relation?*): **the relation.** It passes.

**This also closes the sync half of the session-level provenance gap.** `syncrule`'s
`method` and `parameters` — including `daqsystem_ch1`/`ch2`, the only fields in the
whole daq/sync cluster that describe physical wiring — land on the document the rule
produced. No separate provenance class is needed for them.

### BLOCKED, and on what

`from_epoch` / `to_epoch` point at `acquisition_epoch`, whose own model is
**undecided** (board family "acquisition epoch", nothing proposed). So the DECISION
is final and the BUILD is blocked on that family. Per the standing pattern, that is
allowed — decide now, batch builds — but it must not be built first.

### TWO DEFECTS that need fixing under EVERY option

Found while checking the fold; they are independent of which model wins.

**1. `epochid` is invented, untyped, required, and always empty.**

```
V_eta:  deps = syncrule_id -> syncrule,  epochid -> ''   (must_refer EMPTY, mustBeNonEmpty true)
NDI origin/main: deps = syncgraph_id, syncrule_id        (NO epochid)

corpus census, run #257 -- empty required edge:
   2484  syncrule_mapping.epochid   (B)
   2484  syncrule_mapping.epochid   (Dab)
    348  syncrule_mapping.epochid   (Soph)
```

5,316 documents. We require an edge NDI never writes, and we DROPPED `syncgraph_id`,
which it does. Same defect class as `daqmetadatareader.daqsystem_id` (59 documents,
100% empty) and the same blind spot -- the vocabulary checker compares fields, not
`depends_on` (TaskList #54).

**2. V_eta's epochnode drops `t0_t1` and `objectname`.**

```
NDI:    { epoch_id, epoch_session_id, epochprobemap, epoch_clock, t0_t1, objectname, objectclass }
V_eta:  { time_reference{kind, epoch_clock, epoch_id}, epoch_session_id, epochprobemap, objectclass }
```

`t0_t1` is the epoch's extent -- **the only actual time values in the document.** The
class earmarked to fold into the time model has had its times removed.

## The "file navigation" family was mis-grouped

**`filter` is not navigation.** It lives at `data/filter.json` and carries
`label`, `type`, `algorithm`, `parameters` — a signal-processing filter
description. It belongs with software/method provenance, not with file paths.
Grouping it by a guess at its name was wrong; the status board's `FAMILIES` map
is corrected accordingly.

→ **Proposed: `filter` moves to the software/method family** — `algorithm` +
`parameters` is `software` + `method_parameters`.

**`filenavigator` is runtime, and machine-specific.** `ndi_filenavigator_class`,
`fileparameters`, `epochprobemap_class`, `epochprobemap_fileparameters` describe
how to locate epoch files *on the machine that made them*. Those paths do not
survive the dataset moving, which is what an archival migration is for.

→ **Proposed: not an archival V_eta class.**

**`directory` has no NDI template at all** — it is a post-v1 DID intermediate,
not a v1 source. Per the provenance rule (`V_eta_class_provenance.md`), only
`did_v1`-origin classes are sources.

→ **Proposed: out of scope as a source; disposition is a V_eta-side question
only.**

## `projectvar` — a genuine open call, and a small one

`project`, `type`, `user`, `lab`, `description`, `data`, attached to an
`element_id`. Free-form per-project user metadata on an element-subject. `data`
is an open bag.

Two honest options, and this one is a modelling call rather than an
evidence question:

1. **A `subject_statement`** with `variable` = the project-variable name — the
   same treatment `ontology_table_row` columns get. Makes it queryable, at the
   cost of forcing a `variable` binding onto free-form user text.
2. **Opaque passthrough** — preserve it exactly, model nothing, on the grounds
   that a free-form bag is not a measurement and forcing it into the statement
   tier fabricates structure the source never had.

No recommendation until someone says what these documents actually hold in
practice; the corpora will show it. **The one thing that must not happen is the
`ontology_table_row` failure repeated** — inventing a statement whose subject or
variable cannot be resolved, and emitting it hollow.

## What this closes

Of the eight undecided families, this proposes dispositions for **six classes**
across three families, and moves one class between families. The `sync` split
also removes a class from the undecided pile by absorbing it into an
already-decided model rather than inventing anything.

Nothing is built. `projectvar` remains genuinely open.
