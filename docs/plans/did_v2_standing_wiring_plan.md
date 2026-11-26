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

Decided by Jess Haley, 2026-11-09 [wiring recorded once]: ("I think the same fact only needs to be recorded once", to Q1 of this plan) a probe's wiring that holds in several epochs is recorded once, not once per epoch. How (Q3, Q4) is not decided. Build pending: NDI-matlab (readers and writers of the grouped wiring), DID-matlab (`resolveEpochProbemap` groups identical wirings), did-schema (the edge that lists the epochs), all after Q3 and Q4. Tracked in: VH-Lab/DID-matlab#484, VH-Lab/NDI-matlab#1270, Waltham-Data-Science/did-schema#306.

Decided by Jess Haley, 2026-11-09 [wiring per ingest]: ("Q3: yes", to Q3 of this plan, Claude recommending P2) a later ingest that adds epochs with an existing wiring writes a new wiring relation for its own epochs; no wiring relation is edited after it is written. Build pending: NDI-matlab (writers write one relation per wiring per ingest), DID-matlab (`resolveEpochProbemap` writes one per migrated session), after Q4. Tracked in: VH-Lab/DID-matlab#484, VH-Lab/NDI-matlab#1270.

Decided by Jess Haley, 2026-11-09 [stimulator manipulation dropped]: ("If stimulator manipulations carry nothing new, they should be dropped. The timed sequence manipulations are where the stimuli lie") the body-less per-epoch Stimulator (SNOMEDCT:36645008) manipulation that DID-matlab's `resolveEpochProbemap` writes for each stimulator row of a v1 probe map is no longer written, once the build confirms it carries nothing the wiring relation and the stimulator element do not; the stimuli are recorded by the stimulus-presentation `timed_sequence_manipulation`. Built: DID-matlab 359a0563 (#428, the round trip rebuilds the stimulator row from the wiring and the element). Built: NDI-matlab bb0a61ec (#1211: `+vintage/ingestedEpochs.m` reads a stimulator row from its wiring relation and element where no statement names the probe; Dab's generic output reads the same with all 1,604 Stimulator manipulations removed, B's with 1,242, 0 mismatches). Built: NDI-matlab, no change needed (checked at NDI-matlab V2 c50e72e18 in DID-matlab #466: `+vintage/ingestedArchives.m` reads no stimulator, manipulation or probe map; a Stimulator manipulation owns no data body). Built: DID-matlab 1048e449 (#466: `resolveEpochProbemap` writes no Stimulator manipulation for a row its wiring and element hold; it keeps one for a row with no wiring, another subject or another type, counters `stimulator_manipulations_not_written` / `_kept_no_wiring` / `_kept_other_subject` / `_kept_other_type`, denominator `rows_stimulator`).

**Correction (2026-11-09, Claude), to the evidence quoted in [stimulator manipulation dropped].** The decision quoted Claude's statement that the stimuli are in a "timed sequence" manipulation in every corpus. Measured (NDI-matlab throwaway branch `claude/scratch-dab-census`, test `testStimCensus`; Dab run 42636988371, B run 42636992763): no `timed_sequence` document exists in either corpus. B's 1,242 v1 `stimulus_presentation` documents become 1,242 item-valued manipulations ("visual stimulus"), each owning the epoch's ingested stimulus file as an `opaque_body`. Dab has none (the "1242 presentations" in NDI-matlab `bodyResolver.m`'s comment are B's, counted inside the Dab zip, which bundles B); Dab's stimulation is its optogenetic tetanus manipulations (one per recording run per slice, method EMPTY:0000358 with frequency and duration parameters, built by the Dab dataset map, `sliceTetanus.m`) and its 433 bath-solution manipulations. The census ran the generic stage only, without the Dab map, so it counted no tetanus manipulation. The Stimulator manipulations own no data body in either corpus (Dab 1,604, B 1,242). Claude's reading, not re-decided: the decision's condition ("carry nothing new") holds in Dab too, where the information lives with the tetanus and bath manipulations; Jess Haley asked "shouldn't the info live with those manipulations?" on seeing it. The Dab map re-attributes the Stimulator manipulations to the slice today; that step goes when they are no longer written.

**Q4 (2026-11-09).** Counted (test `testEpochSets`, Dab run 42635685601, B run 42635689923): Dab 602 wiring keys over 202 distinct epoch sets (up to 3 keys share a set), B 156 keys over 156 sets; no set spans sessions. In discussion with Jess Haley the question widened from wiring to how v2 records time at all (Claude's epoch edge, then a time aggregate, then a repeated `referent_id`, then one time per holder with clock readings). Jess Haley: "I'm okay with fixing the schema and migration for a genuinely better version. I'm not convinced we've landed on it though." Q4 is therefore open and waits on a time-model proposal: Jess Haley's requirements list, fixed test cases, a survey of how NWB, BIDS, OWL-Time, CIDOC CRM, FHIR and iCalendar model time, and two or three candidates compared with measured costs, for Jess Haley and Steve Van Hooser to choose from.

Decided by Jess Haley, 2026-11-09 [repeat on a time]: ("I think this sounds good", then "I approve gap unless you think there is a better term") a time can carry a regular repeat, `repeat {count, period and/or gap}`: `count` the number of occurrences including the first (at least 1); `period` start to start and `gap` end to next start, each a time value cell keeping its source unit and value, at least one given, and with both `period` = `duration` + `gap`; the start, duration and end describe the first occurrence; a repeat needs a start. First use: Babu's trainings (5 times, every 12 or 24 min; NDI-matlab `+babu/TreatmentCreator.m`), on its reimport. Where the field sits waits on the time-model proposal (Q4). Build pending: did-schema, DID-matlab, NDI-matlab (after the time-model proposal is decided). Tracked in: VH-Lab/DID-matlab#484, VH-Lab/NDI-matlab#1270, Waltham-Data-Science/did-schema#306.

Decided by Jess Haley, 2026-11-09 [probe map rows compared as a set]: ("Simulator round trip B", to the DID-matlab build agent's question under [stimulator manipulation dropped]: the v1 round trip rebuilds an epoch's probe map as text and compares it row by row in order, and the stimulator row's place came from its Stimulator manipulation) the v1 round trip compares a probe map's rows as an unordered set, as NDI-matlab finds a probe's rows by name, reference and type (`epochprobemapmatch`), so no document records a row's position; the stimulator row is rebuilt from the wiring relation (rig, channels) and the stimulator element (name, reference, type, subject through its `observes` / `derived_from` relation). Built: DID-matlab 359a0563 (#428: the round trip compares rows as a set and rebuilds the stimulator row from the wiring relation and the element). Built: NDI-matlab bb0a61ec (#1211: `+vintage/ingestedEpochs.m` rebuilds stimulator rows from the wiring relation and the element; checked on the generic migrated output, [Dab gets a v2 import]). Built: NDI-matlab, no change needed (checked at NDI-matlab V2 c50e72e18 in DID-matlab #466: `+vintage/ingestedArchives.m` reads no stimulator, manipulation or probe map; a Stimulator manipulation owns no data body). Built: DID-matlab 1048e449 (#466: `resolveEpochProbemap` writes no Stimulator manipulation for a row its wiring and element hold; it keeps one for a row with no wiring, another subject or another type, counters `stimulator_manipulations_not_written` / `_kept_no_wiring` / `_kept_other_subject` / `_kept_other_type`, denominator `rows_stimulator`).

Decided by Jess Haley, 2026-11-19 [acquisition system is a device entity]: ("A.", to Q1 of Claude's acquisition walkthrough: (a) a device entity with the settings hanging off it, (b) settings with `device_id` required, or (c) an entity again, as signed on 2026-08-08 and reversed on 2026-10-08) the digitizer is an `entity` of type device; a probe's `connected to` wiring points at that device entity (answering the walkthrough's Q2); the file-reading settings (v1 navigator, reader and parameter reader) are a separate configuration document that points at the device, not the thing the wiring names. Evidence on read cost (synthetic Dab-size sessions on DID-matlab `did2.database.sqlitedb`, CI runs 44348277259 and 44353953528, scratch branch not for merge): one wiring relation per fact listing its epochs by edge reads one epoch's wiring in 0.9 ms against 1.8 ms for today's one relation per epoch, all epochs in 1.35 s against 2.55 s. Built: did-schema (this commit, additive only: the `connected to` (RO:0002170) relation binding admits a `device` entity as its parent beside `acquisition_system`; `device` was already a registered entity type, COB:0001300, requiring `local_identifier`; the configuration document points at the device by its existing optional `acquisition_system.device_id`, now documented as that edge, which migration will fill). Build pending: DID-matlab (migration mints the device and rewires), NDI-matlab (readers go probe -> device -> configuration), did-schema (after both: `acquisition_system` leaves the binding's parents). Tracked in: Waltham-Data-Science/did-schema#350.

Decided by Jess Haley, 2026-11-19 [migration mints the device by name]: ("1.", to Q3 of the walkthrough: (1) name only, (2) name plus a device-kind term inferred from the reader class, or (3) no device for migrated data) migration mints a migrated rig's device entity with the v1 rig name (`daqsystem` `base.name`) only; the hardware description is added by a person later; the reader class stays on the configuration document. Built: DID-matlab 247aaad4 (#498: `+migrators_j/daqsystem.m` mints one device entity per v1 `daqsystem`, named by its `base.name`; `acquisition_system.device_id` names it), 46f718ba (#516: the device carries the rig name in `name` only). Tracked in: Waltham-Data-Science/did-schema#350.

Decided by Jess Haley, 2026-11-19 [a rig's clock belongs to its device]: ("Yes", to "Shall I record that as your answer to Q4", after Jess: "The entity, right?") a rig's clock is the device's: an epoch's per-rig `relative_time_reference` and both ends of a `clock_alignment_configuration` name the device entity, not the `acquisition_system` settings document; the clock type terms (device local time EMPTY:0000403, device global time EMPTY:0000404, experiment global time EMPTY:0000405, UTC wikidata:Q1536) are unchanged. Built: did-schema (this commit, additive only: `clock_alignment_configuration` `input_id` / `output_id` admit an `entity` beside `acquisition_system`; `relative_time_reference.referent_id` already admitted any document (`base`) and its documentation now says a rig's time reference names the device). Build pending: DID-matlab (migration points them at the minted device), NDI-matlab (the sync graph and readers find a rig's clock through its device), did-schema (after both: `acquisition_system` leaves `input_id` / `output_id`). Tracked in: Waltham-Data-Science/did-schema#350.

Decided by Jess Haley, 2026-11-19 [wiring read from the database only]: ("yes, read from the database only", to Q5 of Claude's acquisition walkthrough) after migration NDI reads a session's wiring only from its `connected to` relations, not from the `*.epochprobemap.ndi` files; the files stay in the session as the source the wiring came from; an edit to a file after migration is not seen. Built: NDI-matlab 19b286db (#1306: `ndi.vintage.folderEpochs` reads a migrated folder epoch's probe map from its `connected to` relations; `ndi.file.navigator` (`epochid`, `getepochprobemap`, `buildepochtable`) and `ndi.daq.system/getepochprobemap` use it; an epoch the database does not hold is read as before). Tracked in: Waltham-Data-Science/did-schema#350.

Decided by Jess Haley, 2026-11-19 [no new hidden epoch-id files]: ("yes, stop writing hidden files", to Q6 of the walkthrough) after migration NDI writes no new `.epochid.ndi` file into a migrated session's folders; an epoch's id is read from its `recording epoch` entity's `local_identifier`; an epoch migration never saw gets its entity and id in the database; existing hidden files are left as they are. Built (the migrated-session half): NDI-matlab 19b286db (#1306: the file navigator reads a migrated folder epoch's id from its `recording epoch` entity's `local_identifier` and writes no `.epochid.ndi` file for it). Build pending: NDI-matlab (an epoch migration never saw still gets its id from a hidden file; its entity is to be written with the v2 epoch writer, [ingest writes v2 directly]). Tracked in: Waltham-Data-Science/did-schema#350.

Decided by Jess Haley, 2026-11-19 [only wired channels recorded]: ("yes, option 2", to Q7 of the walkthrough) migration records only the channels a probe is wired to; a rig's full channel list stays in the file headers, and a native v2 ingest or a person may add it later as statements about the device. Build pending: DID-matlab (check that migration records no other channel). Tracked in: Waltham-Data-Science/did-schema#350.

Decided by Jess Haley, 2026-11-19 [one device per session]: ("yes, option 1", to Q8 of the walkthrough) migration mints one device entity per rig per session (T18: v1 records no serial number, so two sessions' rigs of one name are not known to be one board); devices known to be the same are linked later under did_v2_duplicate_entities_plan.md. Built: DID-matlab 247aaad4 (#498: one device per v1 `daqsystem` document, which is one rig of one session, so a rig name in two sessions gives two devices), 46f718ba (#516). Tracked in: Waltham-Data-Science/did-schema#350.

Decided by Jess Haley, 2026-11-19 [stimulator has no subject of its own]: ("Yes", to "Shall I record option 2 as the direction", after Jess: "I lean 2, but I don't understand how 1 is even being done right now? Show me the json" and Claude's answer that a migrated stimulator's subject is today only an `observes` directed relation, a relation not in the relation bindings that validates because binding conformance is off) the direction is that a stimulator is a device with no subject of its own: what it stimulates is on its statements (stimulus presentations, bath manipulations), and v2 writes no `observes`. Open, proposed to the team: the home of the v1 subject of a migrated stimulator that no statement names (estimated about 55 Dab bath stimulators and PRED's one from the v1 documents; Soph not measured), which is today the only record of each epoch's probe-map subject. That home is decided by [stimulator subject carried as needing information]. Built: did-schema 6715a3fa (carry-172, a field-scoped carry of the element's `depends_on subject_id`), DID-matlab f09dbd0b (#497: the migration report's carried fields, `did2.convert.carryElementSubject`). Built: NDI-matlab b3df0969 (#1279: the second pass writes the carry). Tracked in: Waltham-Data-Science/did-schema#350.

Decided by Jess Haley, 2026-11-19 [stimulator subject carried as needing information]: ("Yes", after Jess: "Why wouldn't we just carry those as needing information? Why create a non-v2 statement?", replacing Claude's proposal of a registered device-to-subject relation) a migrated stimulator whose v1 `subject_id` no statement names gets no `observes`; its v1 subject is recorded as needing information, resolved by the dataset's import, and its entity and wiring are written normally. Exception to [partly placed is carried as v1] (did_v2_go_forward_class_audit.md), recorded as such. Built: did-schema 6715a3fa (carry-172, field-scoped), DID-matlab f09dbd0b (#497: `did2.convert.carryElementSubject`, the round trip reads it). Built: NDI-matlab b3df0969 (#1279: the second pass writes the carried subject). Tracked in: Waltham-Data-Science/did-schema#350.

Decided by Jess Haley, 2026-11-19 [one-field carry in the migration report]: ("A.", to Claude's question after a code check found that DID's carries are whole-document only, `migrationReport.m` `collect` dropping a carry entry for a document that ends up v2) the needing-information subject is held in a new "carried fields" list of the run's migration report: {document_id, class, field, value, carry, reason}, citing a field-scoped carry-register row (kind needs_mapping); it is written by NDI's second pass when no presentation, bath manipulation or Stimulator manipulation names the v1 subject; a DID-only run, with no second pass, keeps `observes`. Built: did-schema (this commit: the carry register's `scope: "field"` and `tools/check_carry_register.py` rule C1 admit a field-scoped row, kind needs_mapping, one field; the row is carry-172, v1 `element` `depends_on subject_id`, for both [stimulator subject carried as needing information] and [recording probe subject carried the same way]). Built: DID-matlab f09dbd0b (#497: `migrationReport` `carriedField`/`carriedFields`, counts and `load`; `did2.convert.carryElementSubject`/`carriedElementSubject`; the round trip's `element.m` and `manifestProbemap.m` read it; Test code run 44480360235). Built: NDI-matlab b3df0969 (#1279: `observesRetirement` writes it; `elementFields` and `prefetchElementFields` read it). Tracked in: Waltham-Data-Science/did-schema#350.

Decided by Jess Haley, 2026-11-19 [recording probe subject carried the same way]: ("Same rule for recording probes") a migrated recording probe with no recording observation (a session never ingested: 1 n-trode in 20211116, 1 in PRED; Soph not measured) gets no `observes`; its v1 subject is recorded in the migration report's carried fields, as [one-field carry in the migration report], resolved when its observations exist. Built: DID-matlab f09dbd0b (#497: the round trip rebuilds an n-trode's subject from the carried field, `testRawV1RoundTripElement`). Built: NDI-matlab b3df0969 (#1279: with [one-field carry in the migration report]; NDI reads the carried subject from the record). Tracked in: Waltham-Data-Science/did-schema#350.

Decided by Jess Haley, 2026-11-19 [uneven time groups and mismatches]: ("yes to both", to Claude's plain-language follow-up on [uneven time is a keyed time value] in did_v2_go_forward_class_audit.md) (1) an ingested archive with several uneven time groups is converted, one `time` value per time group, each channel group keyed to the time group it uses, as the channel list pairs them; (2) a time channel whose sample count differs from the data it times is malformed: the archive is kept as v1, counted (e.g. `uneven_time_mismatch_kept`) and reported. Built: NDI-matlab 2d6376be (#1274; B 44541265674, end-to-end 44566252435, No Cloud 44566271357): `ingestedArchiveBodies` converts an archive with several uneven time groups, one keyed time value per group (`uneven_time_values`), and keeps a sample-count mismatch as v1, counted (`uneven_time_mismatch_kept`) and reported. Not covered by this decision and still kept as `unconvertible`: one uneven time group that holds several time channels. Tracked in: VH-Lab/NDI-matlab#1269.

Decided by Jess Haley, 2026-11-19 [time channel row is notation]: ("yes, go ahead", to Claude's proposal for the open part of [channel list rows get v2 homes] in did_v2_go_forward_class_audit.md) a time channel's own `channel_list.bin` row is rebuilt from its time group: number the time group's, sample rate the group's, offset 0, scale 1, name the standard prefix and number; the file is removed only when the rebuild matches exactly, else it is kept whole as v1 and counted. Built: NDI-matlab 2d6376be (#1274; B 44541265674, end-to-end 44566252435, No Cloud 44566271357) (`ingestedChannelList` rebuilds one time row per time channel a group names; `channel_list.bin` is removed only on an exact match, counters `time_rows_rebuilt`, `channel_list_kept_time_row`), DID-matlab a9d3b89b (#492; Test code 44555033448) (the round trip's `ingestedArchiveFiles`). Tracked in: VH-Lab/NDI-matlab#1269.

Decided by Jess Haley, 2026-11-19 [text channel entries are a JSON array]: ("Your proposal for text channels sounds good", to Claude's proposal for the text-channel body format that [event channel variable terms] in did_v2_go_forward_class_audit.md left undecided) an unpacked text channel's times are an uncompressed array of 64-bit floats, as for events ([unpacked event bodies are uncompressed]); its entries are one uncompressed UTF-8 JSON array of strings in the same order, format EDAM format_3464 "JSON". Built: NDI-matlab 2d6376be (#1274; B 44541265674, end-to-end 44566252435, No Cloud 44566271357) (`ingestedArchiveBodies` unpacks `evmktx` text channels, `ndi.vintage.ingestedTextEntries`, counters `text_channels_unpacked`), DID-matlab a9d3b89b (#492; Test code 44555033448) (the round trip rebuilds them). Tracked in: VH-Lab/NDI-matlab#1269.


Correction, 2026-11-12 (Claude, from the NDI-matlab build agent's finding; see `did_v2_go_forward_class_audit.md` [Dab gets a v2 import]): the Build pending note of [probe map rows compared as a set] says "the Dab map's re-attribution does not depend on the manipulation". It does for one bath: `bath_221202_BNSTI_SCN_a` served two slices after the map's nested-day split, and only its per-epoch Stimulator manipulations say which. Dab gets a v2 import instead, so this does not change the decision; the generic migrated output reads the same without the manipulations.

Decided by Jess Haley, 2026-11-19 [time row and text channel readings]: ("Yes. Next", to Claude's question on three readings VH-Lab/DID-matlab#492 and VH-Lab/NDI-matlab#1274 made beyond [time channel row is notation] and [text channel entries are a JSON array]) (1) the rebuilt time channel row's `time_channel` is its own channel number, as v1 writes it; (2) when an epoch's groups name time groups the v1 channel list holds none of (a dangling `t2`), the rebuild does not match, so the list file is kept as v1 and counted; (3) the text entries' JSON array is stored in a `sampled_body` with `data_type` utf8, beside the times. Also: the NDI-compress UTF-8 read bug is filed (VH-Lab/NDI-matlab#1282). Built: DID-matlab a9d3b89b (#492; Test code 44555033448), NDI-matlab 2d6376be (#1274; B 44541265674, end-to-end 44566252435, No Cloud 44566271357). Tracked in: VH-Lab/NDI-matlab#1269.

Decided by Jess Haley, 2026-11-19 [archive with no digital channel]: ("A. next", to Claude's question after VH-Lab/NDI-matlab#1277 counted as `no_v2_home` the `sample_digital_segment` of an ingested archive with no digital channel) option (a): it is notation, rebuilt by the round trip, if the v1 ingest writer always writes the same default when an archive has no digital channel; Claude checks the writer first, and if the value varies the team is asked again. Built: NDI-matlab ae43b8a5 (#1284: the writer check, NDI `origin/main` 145f651ad `src/ndi/+ndi/+daq/+reader/mfdaq.m:848,851` sets `sample_digital_segment = 1e7` for every archive before any channel is read, in all 49 versions since ingest was added; `archiveSegmentLengths` counts it as `no_digital_default`; No Cloud 44574285403, e2e 44574270014). Built: DID-matlab 2bdc9f81 (#506) (the archive inverse rebuilds 10000000 when the archive has no di_/do_ member, as NDI 145f651ad `mfdaq.m` writes it; deferred values B 2,484 to 1,242, Dab 5,692 to 2,846). Tracked in: VH-Lab/NDI-matlab#1269.

Decided by Jess Haley, 2026-11-19 [device id required and named by the rig]: ("ok to both", to Claude's two questions, after Jess: "are we not removing acquisition_system as a class in favor of the device entity?" and Claude's answer that under [acquisition system is a device entity] `acquisition_system` stays as the file-reading configuration document and leaves the wiring) (1) `acquisition_system.device_id` becomes required once DID-matlab #498 and NDI-matlab #1278 have merged and every corpus fills it; until then it stays optional; (2) the minted device's `local_identifier` is the v1 rig name (the daq system's name). Built: DID-matlab 247aaad4 (#498: each v1 daqsystem mints its rig's device entity; 84 of 84 acquisition systems across 20211116, B, Dab, JH and PRED, DID Test code run 44482303070), NDI-matlab ab5be314 (#1278: readers accept either parent). Part (2) is replaced by [local identifier required only where looked up]: the rig's device writes `name` only. Built: DID-matlab 46f718ba (#516: the device writes `name` only), did-schema (this commit: `device_id` required, after [rig device written by NDI writers]). Tracked in: Waltham-Data-Science/did-schema#350.

Decided by Jess Haley, 2026-11-19 [readtimeseries timed with NDI Cloud]: ("Yes. Next", to Claude's question for VH-Lab/NDI-matlab#1018, since the corpus zips, JH.zip included, carry no binary files and the Haley files are at ndic:// paths) an on-demand NDI-matlab workflow, never on push, signs in to NDI Cloud with a repository secret, fetches the Haley session's binaries and times `readtimeseries` on v1 and on migrated v2, comparing the samples; until a team member adds the secret it reports not measured and exits cleanly. Built: NDI-matlab ae43b8a5 (#1284: `.github/workflows/test-cloud-readtimeseries-haley.yml`, `workflow_dispatch` only, and `tests/+ndi/+unittest/+migrate/cloudReadtimeseriesTiming.m`; secrets `NDI_CLOUD_HALEY_USERNAME` / `NDI_CLOUD_HALEY_PASSWORD`). Not run: GitHub registers a dispatch-only workflow only from the default branch (`main`), so the dispatch returns 404 until the file is on NDI-matlab `main`. Build pending: a team member (the workflow file on NDI-matlab `main`, and the secret). Tracked in: VH-Lab/NDI-matlab#1018.

Decided by Jess Haley, 2026-11-19 [acquisition configuration renamed]: ("Ok. Do the rename.", after Jess: "Do you think acquisition system should even be a class anymore?" and "what do you think the best name is for that class given its function?", and Claude's answer that under [acquisition system is a device entity] the class stays as the one record NDI builds its daq system object from, how a device's recordings are read: reader, epoch file pattern, epoch parameter readers, software and device; it cannot fold into the device entity (T1, identity fields only)) `acquisition_system` is renamed `acquisition_configuration`, documented as how a device's recordings are read. Siblings first: NDI-matlab and DID-matlab read both names, then write the new one, then did-schema renames the class; done with [device id required and named by the rig], after DID-matlab #498 and NDI-matlab #1278. Built: NDI-matlab 4f0a12d1 (#1290, reads both names) and 7427fd19 (#1294, writes the new one); DID-matlab 42c8e671 (#517, reads both names) and 9ff1afe5 (#520, writes the new one); did-schema 573afd67 (#371: the class, its file, the bindings and the relation parents). Tracked in: Waltham-Data-Science/did-schema#350.

Decided by Jess Haley, 2026-11-19 [time group with several time channels split]: ("Split it", to Claude's question after VH-Lab/NDI-matlab#1274 left as `unconvertible` an ingested archive whose one uneven time group file holds several time channels, which [uneven time groups and mismatches] does not cover) each time channel in such a group becomes its own keyed `time` value, and each channel group keys to the time value of the time channel its rows' v1 `time_channel` names; a channel group whose rows name time channels in two different time values cannot be keyed to one, so that archive is kept as v1 and counted, as a sample-count mismatch is. Built: NDI-matlab da5e0dbd (#1286: `ingestedArchiveBodies` splits the group; `ingestedChannelList` rebuilds the time rows), DID-matlab ba2de174 (#508: the round trip). Tracked in: VH-Lab/NDI-matlab#1269.

Decided by Jess Haley, 2026-11-19 [NDI-compress keeps a V2 branch]: ("Don't merge in ndi-compress. Keep a v2 branch instead", then "I" to Claude's option (i) for rebuilding the `.p` files in CI) work on NDI-compress goes into a `V2` branch of each NDI-compress repository, never into `main`; NDI-matlab V2 pins `NDI-compress-matlabp@V2`; the `.p` files are rebuilt from the private NDI-compress source by a workflow on `NDI-compress-matlabp` `V2`, run by a push that changes `build-source-ref`, reading the source with a repository secret. Built: NDI-compress-matlabp b16eae47 (#3: `.github/workflows/build-pcode.yml`, `build-source-ref`; run 44596986555 printed NOT BUILT, no secret) and 0d9a8959 (#4: `build-source-ref` names NDI-compress V2 61f6bb3). Build pending: a team member (the secret `NDI_COMPRESS_READ_TOKEN` on NDI-compress-matlabp, readable access to NDI-compress), then NDI-matlab (VH-Lab/NDI-matlab#1287 pins V2 and adds the round-trip tests). Tracked in: VH-Lab/NDI-matlab#1275, VH-Lab/NDI-matlab#1282.

Decided by Jess Haley, 2026-11-19 [multi-code markers keep every code]: ("A", to Claude's question after VH-Lab/NDI-matlab#1276 reproduced in MATLAB, NDI run 44587076892: a 3×4 marker read back as 3×1 and the event channel after it read wrong times; options (a) a fifth `event_data_description` number K with N×K codes, (b) one event per code, (c) K channels) option (a): a marker event with K codes records K in a fifth `event_data_description` number and stores all N×K codes; a file with one code per event keeps the 4-number header and is unchanged; NDI-compress's C reader and writer read and write the fifth number. Built: NDI-compress 61f6bb3 (V2, #16: MATLAB source for #1276, #1275 and #1282; C reader and writer, ctest `V2HeaderTests`, CI on three systems). Build pending: NDI-compress-matlabp (the `.p` rebuild, [NDI-compress keeps a V2 branch]), NDI-matlab (#1287). Tracked in: VH-Lab/NDI-matlab#1276.

Decided by Jess Haley, 2026-11-19 [Intan aux names no time channel]: ("A", after Jess: "I need you to show me this in json format for v2 classes" and "So this is a v1 problem?", and Claude's answer that in v2 each channel group's body carries its own evenly spaced time covariate, so only the v1 channel list and v1 `readtimeseries` depend on it) an Intan auxiliary channel's v1 `time_channel` is NaN, not 1 (`t1` runs at four times the aux rate) and not a synthesised `t2`; the v1 channel list then rebuilds exactly under [time channel row is notation]; v1 `readtimeseries` on an unmigrated Intan aux probe returns NaN times and is left as it is. Built: NDI-matlab fcb674ad (#1288, `intan.m`; `TestReaderTimeChannels`; No Cloud 44588560859).

Decided by Jess Haley, 2026-11-19 [session folder wiring migrated]: ("3. Ok", to Claude's recommendation after the NDI-matlab build of [wiring read from the database only] measured 0 `connected to` relations for non-ingested epochs on 20211116 (1,220 v1 documents, 12 epochs) and PRED, because the corpus zips hold no session folder and DID's migration reads probe maps only from `epochfiles_ingested`) migration writes the `connected to` relations of a non-ingested epoch from the session folder's `.epochprobemap.ndi` files when the folder is present; the navigator then reads wiring from the database only; the build is tested on a fixture with a real session folder (NDI's example Intan session). Built: NDI-matlab 19b286db (#1306: the migration step was already built by `ndi.migrate.internal.navigatorEpochFiles`; the navigator reads the wiring from the database, [wiring read from the database only]; `TestSessionFolderWiring` tests both on a real session folder of NDI's example Intan file). Tracked in: Waltham-Data-Science/did-schema#350.

Decided by Jess Haley, 2026-11-19 [stimulus log owned by its presentation]: ("D", after Jess asked why the stimulus system's files have no manipulation, and Claude's answer that [stimulator manipulation dropped] removed an empty record that never held them) an epoch's stimulus-system archive files (the event file `evmktx_group1_seg.nbf_1` and `channel_list.bin`, read by `vhlabvisspike2`; kept as v1 archives with no owner: B 1,242, Dab 1,243, Soph 175, DID-matlab Test code run 44622035771 and Soph run 44511300128) become a data body of that epoch's stimulus-presentation `timed_sequence_manipulation`, the raw timing it was built from; where an epoch has no presentation, an observation of the stimulus rig's device owns them, as [non-specimen channel groups get their own owner] does, counted; the archive document then goes ([segment length is the time chunk]). The match of logs to presentations is measured per corpus first. Siblings first: NDI-matlab reads the log from its new home (today `ingestedArchiveBodies` skips an archive with no channel or time group, and `+daq/reader.m` reads these epochs through the kept v1 document), then DID-matlab moves it. Built: NDI-matlab 8ebe602c (#1293: the log read from its owner by its key), DID-matlab 779a57a8 (#518: `resolveEpochProbemap` moves each stimulus archive's files onto its presentation, else a fallback observation). Kept stimulus archives: B 1,242 to 0, Dab 1,242 to 0 (its ndr archive stays), Soph 175 to 0; round trip clean. The fallback observation's variable, NCIT:C25499 "Event", is Proposed (not decided); 0 corpus cases. Tracked in: VH-Lab/DID-matlab#487.

Decided by Jess Haley, 2026-11-22 [rig device written by NDI writers]: ("Ok", to Claude's recommendation after did-schema #371 made `acquisition_configuration.device_id` required and reverted it (2da1396a), because 10 of 322 NDI V2 import tests failed when NDI's own writers did not fill it) NDI's own v2 writers (`ndi.daq.system/newdocumentV2`, and the Haley import's `sessionDocuments` when the instrument is unknown) create the rig's device entity, one per rig per session, named with the rig's name, and the `acquisition_configuration` names it by `device_id`; then did-schema makes `device_id` required, completing [device id required and named by the rig]. Built: NDI-matlab e5fe83e9 (#1299: `ndi.setup.V2.rigDevice`, its id minted as the migration mints it; `newdocumentV2` and `sessionDocuments` write it and fill `device_id`; with `device_id` required the V2 import ran 327 tests, 0 failed, and end-to-end, assemblers and Dab passed), did-schema (this commit: `device_id` required).

Decided by Jess Haley, 2026-11-25 [stimulus log fallback is a manipulation]: ("Yes", after Jess asked why an epoch would have no presentation and why the stimulus rig would be observed, and Claude's answer that a v1 presentation is computed from the log afterwards by NDI's stimulus decoder, so an epoch can have a log and no presentation, and that the log records what was done to the animal, not a measurement of the rig) amends [stimulus log owned by its presentation]: where an epoch has a stimulus log and no presentation, the log is a data body of a `manipulation` of the epoch's subject, with the stimulator as `instrument_id` and variable NCIT:C41210 "Stimulus", not an observation of the rig's device with variable NCIT:C25499 "Event" as DID-matlab 779a57a8 (#518) built; an epoch whose subject is not found is counted and its archive kept as v1. No corpus has the case (2,659 of 2,659 logs matched one presentation). Built: DID-matlab eb668210 (#524: `resolveEpochProbemap`'s fallback owner is the manipulation; a subject not found is counted `stimulus_log_kept_no_subject` and the archive kept as v1); NDI-matlab f226b90c (#1302: `ingestedStimulusLogBodies` already read the log by its key whatever owns it; the `TestStimulusLogOwner` fixture's fallback owner is now the manipulation).

Decided by Jess Haley, 2026-11-25 [unused split time channel kept]: ("Ok", to Claude's recommendation) under [time group with several time channels split], a split time channel that no channel group names would be a time value nothing keys to (an orphan, which integrity forbids), and dropping its column would lose data; so the archive is kept unchanged as v1 and counted, as NDI-matlab da5e0dbd (#1286) already does. Built: NDI-matlab da5e0dbd (#1286).

Decided by Jess Haley, 2026-11-25 [time channels out of order are malformed]: ("Ok", to Claude's recommendation) an ingested archive whose channel list does not give its time channels in increasing number (NDI's v1 writer always does, and its readers take the time file's columns in that order) is malformed: it is kept unchanged as v1, and the migration report names it as malformed with the order found, rather than migration guessing which column is which clock. Built: NDI-matlab da5e0dbd (#1286: kept as v1, `unconvertible`). Built: NDI-matlab f226b90c (#1302: the report names the archive as malformed, `REPORT.malformed` kind `time_channels_out_of_order` with the order found, and `ndi.migrate.local` prints it).

Decided by Jess Haley, 2026-11-26 [unnamed rig is malformed]: ("A", to Claude's question after did-schema #376 made `acquisition_configuration.device_id` required while DID-matlab's `daqsystem.m` mints no device for a v1 rig with no name; all 84 of 84 rigs counted had names, and Soph passed under the required edge) a v1 rig with no name is malformed source data: its documents are carried unchanged as v1 and the migration report names it as malformed, as [several metadata forms are malformed] and [time channels out of order are malformed] do; no device is minted with a made-up name. Unblocks `acquisition_configuration` leaving the wiring and clock edges ([acquisition system is a device entity], [a rig's clock belongs to its device]). Built: DID-matlab b05ccf31 (#527: `daqsystem.m` carries an unnamed rig as v1 and reports it malformed).

Decided by Jess Haley, 2026-11-26 [no migration before the time-reading fix]: ("No datasets have been migrated yet", then "Yes", to Claude's proposal after Waltham-Data-Science/NDI-compress#18 found MATLAB `expand_time` adds where it should subtract, so NDI's second pass judged 167 of 174 Soph and 8 of 1,605 Dabrowska time groups uneven when even (B 0 of 1,242); fixed on NDI-compress `V2` f235447, NDI-compress-matlabp `V2` d67e391, not built into p-code because NDI_COMPRESS_READ_TOKEN is missing, build run 45712436527) no dataset is migrated with its binary files until NDI-matlab runs the rebuilt NDI-compress; no dataset has been migrated, so nothing needs a second pass re-run; NDI-matlab gets a test that reads MATLAB-written uneven time and compares it with the original values. Build pending: NDI-compress-matlabp (the p-code rebuild, after the secret), NDI-matlab (the uneven-time test, with VH-Lab/NDI-matlab#1287).

Decided by Jess Haley, 2026-11-26 [no observes relation in v2]: ("Yes", after Jess asked why the first pass writes `observes` only for a later pass to retire it, and said "Wouldn't we just convert to a v2 manipulation or carry through", to Claude's proposal) v2 has no `observes` relation: DID-matlab's first pass stops turning a v1 element's `subject_id` into one (`+migrators_j/element.m`), and NDI's second pass reads the v1 `subject_id` directly; the animal is the `entity_id` of the observations and manipulations made with the element, or, where none names it, is carried as the element's subject ([stimulator subject carried as needing information], VH-Lab/NDI-matlab#1279). Supersedes the `observes` parts of [observes retires in the second pass], [DID first pass keeps observes] and [stimulator link lives in the presentations]. Siblings first: NDI-matlab readers (`ndi.vintage.elementFields`, `prefetchElementFields`, `recordingAttribution`, `+setup/+conv/+dabrowska`) read statements and the carried subject, not `observes`; then DID-matlab stops writing it and its round trip defers the element's v1 `subject_id` to the second pass; then did-schema retires the `observes` relation binding if nothing else uses it. Build pending: NDI-matlab (after #1279), DID-matlab, did-schema.

Decided by Jess Haley, 2026-11-26 [epochs added after migration read as v1]: ("Ok", to Claude's recommendation) under [no new hidden epoch-id files], an epoch that migration never saw (files added to a migrated session folder) is read the v1 way, its id from its hidden file and its wiring from its file, until the v2 epoch writer ([ingest writes v2 directly]) gives it an entity; without a written link from its files to an entity its id would change on every read. Nothing to build now.
