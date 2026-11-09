# Standing probe wiring: one relation per wiring, not per epoch

**Status: Proposed (not decided).** Drafted by Claude on 2026-11-09, at Jess
Haley's request ("Write the standing wiring plan for me"). Nothing here is
decided until a `Decided by` line below records a team member's decision.

## 1. The finding

[probe wiring is a relation] (`did_v2_go_forward_class_audit.md`, Jess Haley,
2026-11-01) wires a probe to an acquisition system's channels with a
`directed_relation` "connected to" (RO:0002170), timed by the epoch's time
reference. The migrator writes one such relation per probe **per epoch**.

A read-only count of the migrated Dab database (NDI-matlab Dab workflow run
42535319383, throwaway branch `claude/scratch-dab-census`, test
`testWiringRepeats`, the `WIRING REPEATS` block) found:

    DENOMINATOR: 4737 directed_relation(s) timed by anchors onto 1579 manifest epoch(s)
    relations 4737; distinct wiring keys 600; keys in exactly 1 epoch 0; epochs per key min 3 / median 7 / max 23
    probes (child_id) 600; distinct wiring keys per probe min 1 / median 1 / max 1; probes with one key 600

The wiring key is the class name, the whole `directed_relation` block (term,
order, conditions), the `relation` block, and every edge except `session_id`
and `time_reference_id`. Two copies of a key differ only in `base.id`,
`base.creation_timestamp` and the epoch they are timed to.

So the 4,737 relations hold 600 facts, each written once per epoch where it
holds (3 to 23 times). That is repetition, not normalization: the same fact
stored many times. Only Dab was measured; no other corpus has been counted.

The time anchors were counted in the same run and do **not** repeat in this
way. Each epoch's clock anchors carry that epoch's own start and duration
(1,556 distinct starts and 3,068 distinct durations among 3,158 anchors).
They are per-epoch facts and are not part of this proposal.

## 2. Proposal

**P1. One wiring relation per distinct wiring.** The migrator (and any v2
writer) writes one `connected to` relation for each distinct (probe,
acquisition system, `directed_relation` block). Its time-reference edges name
every epoch in which that wiring holds, as a `time_reference_id_#` family
numbered from 0:

```json
{"directed_relation": {"relation": {"node": "RO:0002170", "name": "connected to"}, "order": -1,
   "conditions": {"variable": {"node": "EMPTY:0000370", "name": "analog input channel"}, "matrix": [[1]]}},
 "depends_on": [{"name": "child_id",  "value": "<probe>"},
                {"name": "parent_id", "value": "<acquisition system>"},
                {"name": "time_reference_id_0", "value": "<anchor of the first epoch>"},
                {"name": "time_reference_id_1", "value": "<anchor of the second epoch>"},
                {"name": "session_id", "value": "<session>"}]}
```

`directed_relation.time_reference_id` is already declared `multiple: true`
(`schemas/did_v2/relation/directed_relation.json`), so the class needs no
change.

**P2. Rewiring stays exact.** A probe whose wiring changes between epochs
gets one relation per distinct wiring, each naming only its own epochs.
Nothing about per-epoch wiring is lost; each distinct fact is stored once.

**P3. Reading is unchanged in meaning.** An epoch's wiring is the set of
wiring relations with an edge to that epoch's anchor. The edge index answers
this in one query. NDI-matlab #1202 (338ab462) made the readers take numbered
`time_reference_id_<n>` edges.

**P4. Which anchor.** The edges point at the same epoch anchor the per-epoch
relation points at today. Which of an epoch's anchors that is has not been
checked; it is checked before building.

**Effect on Dab:** 4,737 wiring relations become 600. Epoch-table reads join
about 4,100 fewer documents. That alone does not bring the Dab probe read to
v1 speed, because the per-epoch anchors and observations remain. The derived
epoch-table index (Jess Haley, 2026-11-09: "Build the derived index") is
being built separately and does not depend on this plan.

## 3. Alternatives considered

- **A time span** (one anchor from the first to the last epoch): wrong when a
  probe's epochs are interleaved with epochs where it was wired differently.
- **No time at all** (the wiring holds for all of the probe's epochs):
  simplest, but cannot express rewiring.
- **Keep one relation per epoch** and rely on the derived index for speed:
  keeps today's repetition. This is the right choice if each epoch's wiring
  is a separate observation whose provenance matters (Q1).

## 4. What it would touch (siblings first)

1. **NDI-matlab:** readers and writers take a wiring relation with several
   epoch edges (mostly done by #1202; to be checked against the probe-map
   readers `ndi.vintage.ingestedEpochs`, `ndi.vintage.wiredDeviceString`,
   `ndi.file.navigator.bodies`), and the round trip still rebuilds each
   epoch's v1 probe map.
2. **DID-matlab:** `resolveEpochProbemap` groups identical wirings across a
   session's epochs before writing; the round-trip tests rebuild v1's
   per-epoch devicestring from the grouped relation.
3. **did-schema:** the decision line only; no class change (P1).

## 5. Questions for the team

- **Q1.** Is "the same wiring in many epochs" one fact with many times (this
  proposal), or one fact per epoch, because each epoch's wiring was recorded
  separately and that record matters?
- **Q2.** If P1: does the same grouping apply to any other per-epoch relation
  that repeats? None has been counted.
