# Standing probe wiring: one relation per wiring, not per epoch

**Status: partly decided.** Drafted by Claude on 2026-11-09, at Jess Haley's
request ("Write the standing wiring plan for me"). Decided: [wiring recorded
once] and [wiring per ingest] (section 5). Proposed (not decided): the
mechanism, P1 and P4 (Q4). Q5 is answered by [stimulator manipulation dropped].

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

**Correction (2026-11-09, Claude).** The first version of this section (merged
in did-schema #302) proposed listing the epochs as a `time_reference_id_#`
family on the wiring relation and said "the class needs no change". That was
wrong. The family's own documentation (did_v2_time_reference_model_plan.md
CHANGE 5, #52; amended by [device clocks on one epoch]) says: "within this
family every member describes THE SAME instant or extent, and `value.clock`
on the REFERENCED document must be unique across the family". Several time
references are one time on several clocks or referents, not a list of
different times. Jess Haley asked "Is multiple time references meant to be
multiple clocks? Or multiple points in time?", which found it. The proposal
below replaces it.

**P1. One wiring relation per distinct wiring, listing its epochs on a new
edge.** The wiring relation gains an edge family for the epochs it holds in,
separate from time references, for example `epoch_id_#`, each member naming
one epoch entity. Time references keep their meaning. This is a schema change
(a new edge on `directed_relation`), so it lands in NDI-matlab and DID-matlab
first (CLAUDE.md, "Changes the siblings must follow land in the siblings
first"). The name is a proposal.

```json
{"directed_relation": {"relation": {"node": "RO:0002170", "name": "connected to"}, "order": -1,
   "conditions": {"variable": {"node": "EMPTY:0000370", "name": "analog input channel"}, "matrix": [[1]]}},
 "depends_on": [{"name": "child_id",  "value": "<probe>"},
                {"name": "parent_id", "value": "<acquisition system>"},
                {"name": "epoch_id_0", "value": "<epoch 1>"},
                {"name": "epoch_id_1", "value": "<epoch 2>"},
                {"name": "session_id", "value": "<session>"}]}
```

**P2. One relation per ingest, never edited.** Each ingest (and each migrated
session) writes one relation per distinct wiring, listing that ingest's
epochs. A later ingest that adds epochs with the same wiring writes a new
relation for its own epochs; no document is edited after it is written, as
in v1 and v2 today. Repetition is bounded by the number of ingests, not
epochs. A migrated Dab session gets 600 relations.

**P3. Rewiring stays exact.** A probe whose wiring changes between epochs
gets one relation per distinct wiring, each naming only its own epochs.

**P4. Reading.** An epoch's wiring is the set of wiring relations with an
`epoch_id_#` edge to that epoch. The edge index answers this in one query.

**Effect on Dab:** 4,737 wiring relations become 600. That alone does not
bring the Dab probe read to v1 speed; the derived epoch-table index (Jess
Haley, 2026-11-09, "1 yes, 2 a, 3 yes", docs/V2_PLAN.md) does that and does
not depend on this plan.

**Compared with v1.** v1 also records the wiring once per epoch: each
`epochfiles_ingested` document holds that epoch's probe map beside its
clocks. P1-P2 give up v1's self-contained epoch document (the wiring is one
indexed query away) and keep its write-only history.

## 3. Alternatives considered

- **Several time references** (this plan's first version): conflicts with
  CHANGE 5, see the correction above.
- **Change CHANGE 5** so time-reference members may be different times:
  blurs what a time reference means everywhere, not only for wiring.
- **A group of epochs** (T20): the wiring is timed "during group G", each
  epoch a `member_of` G. No new edge, but one membership relation per epoch,
  so no fewer documents.
- **One time reference for "during the session"**: wrong; a Dab probe is in
  3 to 23 of its session's epochs.
- **A time span** (first to last epoch): wrong when a probe's epochs are
  interleaved with epochs where it was wired differently.
- **Edit one relation per wiring as epochs arrive**: fewest documents, but
  documents change after they are written (P2 avoids it).
- **Keep one relation per epoch** and rely on the derived index for speed.

## 4. What it would touch (siblings first)

1. **NDI-matlab:** readers take the wiring from `epoch_id_#` edges (and the
   old per-epoch shape, while both exist), writers write P1-P2; the round
   trip still rebuilds each epoch's v1 probe map.
2. **DID-matlab:** `resolveEpochProbemap` groups identical wirings of a
   session's epochs into one relation; `did2.build` accepts the new edge;
   round-trip tests.
3. **did-schema:** the new edge on `directed_relation`, after 1 and 2.

## 5. Questions for the team

- **Q1.** Is "the same wiring in many epochs" one fact? ANSWERED below
  [wiring recorded once].
- **Q2.** Do other per-epoch documents repeat the same way? Counted on Dab
  and B (Jess Haley, 2026-11-09: "Count them"): NDI-matlab Dab run
  42558437238 and B run 42558440061, test `testEpochRepeats` on the
  throwaway branch, same key as section 1:

      Dab  directed_relation |  4762 |  602 | 0    | 3/7/23  | 4160 (87.4%)
      Dab  observation       |  3208 |  408 | 0    | 3/7/23  | 2800 (87.3%)
      Dab  manipulation      |  2037 |  637 | 433  | 1/1/23  | 1400 (68.7%)
      B    directed_relation |  2484 |  156 | 1    | 1/9/142 | 2328 (93.7%)
      B    manipulation      |  2484 | 1255 | 1242 | 1/1/142 | 1229 (49.5%)
      B    observation       |  1242 |  143 | 1    | 1/9/18  | 1099 (88.5%)
      (documents | distinct keys | keys in exactly 1 epoch | epochs per key | repeats)

  `ingestion_manifest` never repeats. The observations' keys repeat, but each
  observation's `opaque_body` names its own file (Dab: 6,416 bodies, 6,416
  distinct files; B: 4,968 and 4,968), so they hold different data and are
  not repeats; whether the bytes differ is not measured (no hashes, no
  binaries in the corpus zips, NDI-matlab #785). B's 1,242 manipulations
  that own a body each have a key of their own. The true repeats are the
  wiring relations and the body-less "Stimulator" (SNOMEDCT:36645008)
  manipulations. (The Dab figures here count 1,605 typed epochs; section 1
  counted the 1,579 a manifest names.)
- **Q5.** Should the "Stimulator" manipulation be grouped like the wiring?
  It is the same kind of standing fact, repeated per epoch. But a
  manipulation is an interaction, and `interaction.time_reference_id` has
  `min_count: 1`, so the epoch-list edge would sit beside a required time
  reference, or the statement belongs elsewhere. Not proposed yet.
  ANSWERED below [stimulator manipulation dropped]: the body-less Stimulator
  manipulation says nothing the wiring relation and the stimulator element do
  not already say (its value is the term "Stimulator" as both variable and
  value; it owns no data body since [ingested stimulus file is a body of the
  presentation] moved the stimulus file to the presentation manipulation, NDI-matlab
  `+migrate/+internal/ingestedStimulusBodies.m`). The stimuli are in the
  `timed_sequence_manipulation` that NDI's second pass builds from v1
  `stimulus_presentation`. Its readers today: DID-matlab
  `+did2/+convert/+roundtrip/private/manifestProbemap.m` rebuilds the v1
  probe map's stimulator row from it; NDI's presentation attribution reads the
  stimulator element's own subject instead (`bodyResolver.m`
  `subjectsViaStimulator`). Before it is dropped, the build confirms that the
  migrated stimulator element keeps its subject and moves the round trip to
  the wiring and the element.
- **Who writes wiring.** Today only the migration writes wiring relations,
  from v1 ingested epochs (`resolveEpochProbemap`). For new data, which v2
  writer writes them at ingest is part of the parked ingest questions
  (docs/V2_PLAN.md G84, with G75, G76); P2 assumes ingestion writes them, as
  in v1, and is settled with G84 for new data. For migration it can be built
  once Q3 and Q4 are answered.
- **Q3.** When a later ingest adds epochs with an existing wiring: write a new
  relation for them (P2), or edit the existing one? Claude recommends P2.
  ANSWERED below [wiring per ingest].
- **Q4.** The mechanism: a new epoch edge on the relation (P1), a group of
  epochs, or a change to CHANGE 5? Claude recommends P1 if Q5 is no. If the
  Stimulator manipulations are grouped too (Q5 yes), the wiring and the
  manipulations would list the same set of epochs, and T20 ("a set referred
  to as a unit is a group entity"; statements "never list its members") then
  points to a group of epochs instead. How many distinct epoch sets Dab and B
  hold is not measured. Under P1 the relation carries no time reference
  (`time_reference_id` is optional on `directed_relation`); its time is its
  epochs' own anchors.

Decided by Jess Haley, 2026-11-09 [wiring recorded once]: ("I think the same fact only needs to be recorded once", to Q1 of this plan) a probe's wiring that holds in several epochs is recorded once, not once per epoch. How (Q3, Q4) is not decided. Build pending: NDI-matlab (readers and writers of the grouped wiring), DID-matlab (`resolveEpochProbemap` groups identical wirings), did-schema (the edge that lists the epochs), all after Q3 and Q4.

Decided by Jess Haley, 2026-11-09 [wiring per ingest]: ("Q3: yes", to Q3 of this plan, Claude recommending P2) a later ingest that adds epochs with an existing wiring writes a new wiring relation for its own epochs; no wiring relation is edited after it is written. Build pending: NDI-matlab (writers write one relation per wiring per ingest), DID-matlab (`resolveEpochProbemap` writes one per migrated session), after Q4.

Decided by Jess Haley, 2026-11-09 [stimulator manipulation dropped]: ("If stimulator manipulations carry nothing new, they should be dropped. The timed sequence manipulations are where the stimuli lie") the body-less per-epoch Stimulator (SNOMEDCT:36645008) manipulation that DID-matlab's `resolveEpochProbemap` writes for each stimulator row of a v1 probe map is no longer written, once the build confirms it carries nothing the wiring relation and the stimulator element do not; the stimuli are recorded by the stimulus-presentation `timed_sequence_manipulation`. Build pending: DID-matlab (the round trip rebuilds the stimulator row from the wiring and the element, then `mkManipulation` is no longer called), NDI-matlab (readers that read it, including the derived epoch index, checked and moved).

**Correction (2026-11-09, Claude), to the evidence quoted in [stimulator manipulation dropped].** The decision quoted Claude's statement that the stimuli are in a "timed sequence" manipulation in every corpus. Measured (NDI-matlab throwaway branch `claude/scratch-dab-census`, test `testStimCensus`; Dab run 42636988371, B run 42636992763): no `timed_sequence` document exists in either corpus. B's 1,242 v1 `stimulus_presentation` documents become 1,242 item-valued manipulations ("visual stimulus"), each owning the epoch's ingested stimulus file as an `opaque_body`. Dab has none (the "1242 presentations" in NDI-matlab `bodyResolver.m`'s comment are B's, counted inside the Dab zip, which bundles B); Dab's stimulation is its optogenetic tetanus manipulations (one per recording run per slice, method EMPTY:0000358 with frequency and duration parameters, built by the Dab dataset map, `sliceTetanus.m`) and its 433 bath-solution manipulations. The census ran the generic stage only, without the Dab map, so it counted no tetanus manipulation. The Stimulator manipulations own no data body in either corpus (Dab 1,604, B 1,242). Claude's reading, not re-decided: the decision's condition ("carry nothing new") holds in Dab too, where the information lives with the tetanus and bath manipulations; Jess Haley asked "shouldn't the info live with those manipulations?" on seeing it. The Dab map re-attributes the Stimulator manipulations to the slice today; that step goes when they are no longer written.

**Q4 (2026-11-09).** Counted (test `testEpochSets`, Dab run 42635685601, B run 42635689923): Dab 602 wiring keys over 202 distinct epoch sets (up to 3 keys share a set), B 156 keys over 156 sets; no set spans sessions. In discussion with Jess Haley the question widened from wiring to how v2 records time at all (Claude's epoch edge, then a time aggregate, then a repeated `referent_id`, then one time per holder with clock readings). Jess Haley: "I'm okay with fixing the schema and migration for a genuinely better version. I'm not convinced we've landed on it though." Q4 is therefore open and waits on a time-model proposal: Jess Haley's requirements list, fixed test cases, a survey of how NWB, BIDS, OWL-Time, CIDOC CRM, FHIR and iCalendar model time, and two or three candidates compared with measured costs, for Jess Haley and Steve Van Hooser to choose from.

Decided by Jess Haley, 2026-11-09 [repeat on a time]: ("I think this sounds good", then "I approve gap unless you think there is a better term") a time can carry a regular repeat, `repeat {count, period and/or gap}`: `count` the number of occurrences including the first (at least 1); `period` start to start and `gap` end to next start, each a time value cell keeping its source unit and value, at least one given, and with both `period` = `duration` + `gap`; the start, duration and end describe the first occurrence; a repeat needs a start. First use: Babu's trainings (5 times, every 12 or 24 min; NDI-matlab `+babu/TreatmentCreator.m`), on its reimport. Where the field sits waits on the time-model proposal (Q4). Build pending: did-schema, DID-matlab, NDI-matlab (after the time-model proposal is decided).

Decided by Jess Haley, 2026-11-09 [probe map rows compared as a set]: ("Simulator round trip B", to the DID-matlab build agent's question under [stimulator manipulation dropped]: the v1 round trip rebuilds an epoch's probe map as text and compares it row by row in order, and the stimulator row's place came from its Stimulator manipulation) the v1 round trip compares a probe map's rows as an unordered set, as NDI-matlab finds a probe's rows by name, reference and type (`epochprobemapmatch`), so no document records a row's position; the stimulator row is rebuilt from the wiring relation (rig, channels) and the stimulator element (name, reference, type, subject through its `observes` / `derived_from` relation). Build pending: DID-matlab (the round trip compares rows as a set and rebuilds the stimulator row; then `resolveEpochProbemap` stops calling `mkManipulation` for body-less stimulator rows, once NDI-matlab's readers of those manipulations have moved), NDI-matlab (readers of the Stimulator manipulation, including the Dab map's re-attribution, checked and moved).

