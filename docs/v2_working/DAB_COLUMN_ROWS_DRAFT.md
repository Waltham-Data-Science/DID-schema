# Dab dataset map: column rows for the v1 `ontologyTableRow` tables (DRAFT)

Draft for Jess Haley to check one table at a time. **Every row below is
Proposed (not decided).** Nothing here is built, committed or posted.

Read at: did-schema 078ab84 (branch `claude/ecstatic-pascal-md91fw`, clean);
NDI-matlab `origin/V2` 9b99061 (the Dab importer and `tableDocMaker.m` are
identical at the locked head f273026: `git diff --stat f273026 origin/V2 --
'+dabrowska' tableDocMaker.m` printed nothing); DID-matlab `origin/V2` f6486be;
empty-ontology `origin/V2` a16c805; Dab corpus zip
`scratchpad/corpora/Dab.zip` (sha256 506fbbdf...c735), extracted to
`scratchpad/dabmap/corpus_Dab/`. Evidence commands and outputs are in §5.

---

## 1. Summary

| table | v1 rows (Dab corpus) | columns | proposed row | open question |
|---|---|---|---|---|
| EPM (elevated plus maze) | 45 | 51 | 44 | 7 |
| FPS (fear-potentiated startle) | 6,160 | 13 | 6 | 7 |
| **total** | **6,205** | **64** | **50** | **14** |

- The Dab corpus holds 6,205 `ontologyTableRow` documents in exactly two
  column signatures, EPM and FPS. There are no other Dab tables (§5, E1).
- Every row resolves to exactly one subject by its local identifier (45/45,
  6160/6160), the only route Dab has (§5, E2).
- None of the 64 column nodes is in the term registry. The only Dab nodes
  registered are EMPTY:0000074 and EMPTY:0000358 (§5, E5). The map
  cannot be built until the variables are registered (or replaced).
- Seven table-level questions (§4) block both tables, chiefly: what time an
  EPM statement carries (the row has none), what a NaN cell becomes, and
  whether a per-trial FPS row becomes per-cell statements or trial series.
- "CNO or saline": **no dose row is proposed.** The data holds only the
  words `CNO` / `Saline`; the amount (2 mg/kg i.p.) and timing (45 min before)
  are only in the term's definition, and saline has no amount at all (§2.3).

## 2. Common ground (applies to both tables)

### 2.1 How a v1 row identifies its table and its subject

- A row has four fields: `names`, `variableNames`, `ontologyNodes`, `data`
  (NDI `+NDIMaker/tableDocMaker.m:276-279`). Each column's node and short
  name come from the importer's dictionary through `ndi.ontology.lookup`
  (`tableDocMaker.m:221, 254`).
- **No table id is stored.** The table is known only by its set of columns.
  Proposed match for the table: the exact `ontologyTableRow.ontologyNodes`
  string of that table (51 nodes for EPM, 13 for FPS; §5, E1). This is an
  exact v1 value, as [map rows match exact values] requires
  (`V_eta_go_forward_class_audit.md:1250`).
- A column row must match the table AND the column's node. A node alone is
  not enough: EMPTY:0000059 "experimental group code" is in both tables with
  different meanings (§3.1 E49, §3.2 F4).
- **No subject edge.** 0 of 45 EPM and 0 of 6,160 FPS rows have any
  `depends_on` (§5, E2). `doImport.m:442-447` passes no dependency variable.
  The subject is found by the `SubjectLocalIdentifier` cell, joined exactly to
  a subject's `local_identifier` in the same session (NDI
  `+migrate/+internal/ontologyRowSubjects.m:131-152`; kept by
  [dataset audit batch 1 and 2] (3), `V_eta_go_forward_class_audit.md:1228`).
- Today the generic stage passes these rows through (no subject edge,
  DID-matlab `ontology_table_row.m:6, 54`); a row whose subject NDI resolves
  is carried whole as v1 with a `needs_mapping` note (`ontology_table_row.m:79`;
  carry register `carry-026`, `V_eta_carry_register.json:475`). These map
  rows are what `carry-026` says resolves it ("the dataset map's column rows
  for that table (not yet written)").

### 2.2 Shapes used

- Statement directions and their value kinds are from T2/T3
  (`V_eta_tenets.md:49-160`). Value kinds used here all exist:
  `count`, `time` (stable); `frequency`, `voltage`, `intensity` (stable);
  `label`, `logical` (draft). There is **no percent / fraction / proportion
  value kind** (46 classes list `value` as superclass; none is one; §5, E6).
- Observation vs calculation is by provenance: inputs in the dataset make a
  calculation with `input_id` (`V_eta_tenets.md:96-105`).
- Units from the registry: `om:second-Time` (registry :1514),
  `om:millisecond-Time` (:2404), `om:hertz` (:2444), `om:millivolt` (:5934),
  `om:percent` (:5724).
- The **variable** of each statement is the column's own v1 node (from
  `ontologyNodes`). Its unit is the one written in the node's EMPTY definition
  (`empty-edit.owl`, line given per row; §5, E4).
- Entity: the row's subject (the animal). Every interaction needs a
  `time_reference_id` (`interaction.json:15`): see Q-T1.

### 2.3 "CNO or saline" (EPM column `Treatment_CNOOrSalineAdministration`)

- Data: 45 rows, values `CNO` (23) and `Saline` (22) only (§5, E1, E3).
- The term EMPTY:0000200's definition (`empty-edit.owl:1967`) says: CNO
  "(2 mg/kg, i.p.)", saline "vehicle control administration (i.p.)",
  "administered 45 minutes before fear conditioning and before EPM testing".
- A `dose` "always has an amount" (`dose.json:41`). Saline has no amount
  anywhere. A CNO amount exists only in a term definition, not in the row.
  [no invented values] (`V_eta_go_forward_class_audit.md:1142`) forbids
  writing a value the source does not state.
- **So no dose row is proposed.** The column is listed as open question Q-E1,
  with one candidate: a `manipulation` of the subject, value kind `term`,
  whose value names what was given (a CNO term or a saline term; neither is
  in the registry, §5, E5), with `intraperitoneal injection` as method if
  wanted (registry row "intraperitoneal injection" exists, registry :7363).

---

## 3. Tables

### 3.1 EPM — elevated plus maze (check this first)

**What it is.** One row per animal per EPM test: the five-minute EPM scores
from `EPM_OTR-cre+_Saline vs CNO_DREADDs-Gi_2 Groups_final-5.23.25.xlsx`,
sheets joined on Animal/Test/Treatment (`doImport.m:315-350`). The importer
adds `Test_Duration` = 300 (`:356`), `Experiment_ID` = 1, or 2 when
Animal >= 300 (`:358-360`), and `Exclude` = true for animals 239 and 258
"not expressing mCherry" (`:362-364`). Written by
`tdm.table2ontologyTableRowDocs(dataTable_EPM, {'SubjectString','Treatment'})`
(`doImport.m:442-443`).

**Rows.** 45 v1 documents, 45 distinct subjects, one session (§5, E1, E2).

**Table match (all rows below):** `v1_class` = `ontologyTableRow`,
`ontologyTableRow.ontologyNodes` = the 51-node EPM string (§5, E1, signature 1).

Legend: obs = `observation`, calc = `calculation`; "def" = the node's
`empty-edit.owl` definition line; dict = `tableDoc_dictionary.json` line.

| id | v1 `variableName` (node) | V2 home: direction, value kind, unit | rests on |
|---|---|---|---|
| E1 | `ElevatedPlusMaze_TestIdentifier` (EMPTY:0000051) | **open: Q-E3** | dict :62; def :907 |
| E2 | `Treatment_CNOOrSalineAdministration` (EMPTY:0000200) | **open: Q-E1** (see §2.3) | dict :3; def :1967 |
| E3 | `ElevatedPlusMaze_OpenArmNorth_Entries` (EMPTY:0000006) | obs, `count` | def :590 "Unit: count"; dict :4 |
| E4 | `ElevatedPlusMaze_OpenArmSouth_Entries` (EMPTY:0000007) | obs, `count` | def :596; dict :5 |
| E5 | `ElevatedPlusMaze_OpenArmTotalEntries` (EMPTY:0000008) | calc, `count`; `input_id` = E3, E4 | def :602; = E3+E4 in 45/45 rows (§5, E3) |
| E6 | `ElevatedPlusMaze_OpenArmNorth_HeadEntries` (EMPTY:0000009) | obs, `count` | def :608 |
| E7 | `ElevatedPlusMaze_OpenArmSouth_HeadEntries` (EMPTY:0000010) | obs, `count` | def :614 |
| E8 | `ElevatedPlusMaze_OpenArmTotalHeadEntries` (EMPTY:0000011) | calc, `count`; `input_id` = E6, E7 | def :620; sum 45/45 |
| E9 | `ElevatedPlusMaze_OpenArmNorth_Time` (EMPTY:0000012) | obs, `time`, s (`om:second-Time`) | def :626 "Unit: seconds" |
| E10 | `ElevatedPlusMaze_OpenArmSouth_Time` (EMPTY:0000013) | obs, `time`, s | def :633 |
| E11 | `ElevatedPlusMaze_OpenArmTotalTime` (EMPTY:0000014) | calc, `time`, s; `input_id` = E9, E10 | def :640; sum 45/45 |
| E12 | `ElevatedPlusMaze_OpenArmTotal_PercentTimeDuringTestDuration` (EMPTY:0000015) | **open: Q-E2** | def :647 "Unit: %" |
| E13 | `ElevatedPlusMaze_OpenArmNorth_LatencyToFirstEntry` (EMPTY:0000016) | obs, `time`, s | def :653 |
| E14 | `ElevatedPlusMaze_OpenArmSouth_LatencyToFirstEntry` (EMPTY:0000017) | obs, `time`, s | def :660 |
| E15 | `ElevatedPlusMaze_OpenArmTotalLatencyToFirstEntry` (EMPTY:0000018) | obs, `time`, s (not derivable: equals min(E13,E14) in 1 of 44 rows) | def :667 |
| E16 | `ElevatedPlusMaze_OpenArmNorth_TimeMovingTowards` (EMPTY:0000019) | obs, `time`, s | def :674 |
| E17 | `ElevatedPlusMaze_OpenArmSouth_TimeMovingTowards` (EMPTY:0000020) | obs, `time`, s | def :681 |
| E18 | `ElevatedPlusMaze_OpenArmTotalTimeMovingTowards` (EMPTY:0000021) | calc, `time`, s; `input_id` = E16, E17 | def :688; sum 45/45 |
| E19 | `ElevatedPlusMaze_OpenArmNorth_TimeFreezing` (EMPTY:0000022) | obs, `time`, s | def :695 |
| E20 | `ElevatedPlusMaze_OpenArmSouth_TimeFreezing` (EMPTY:0000023) | obs, `time`, s | def :702 |
| E21 | `ElevatedPlusMaze_OpenArmTotalTimeFreezing` (EMPTY:0000024) | calc, `time`, s; `input_id` = E19, E20 | def :709; sum 45/45 |
| E22 | `ElevatedPlusMaze_ClosedArmWest_Entries` (EMPTY:0000025) | obs, `count` | def :716 |
| E23 | `ElevatedPlusMaze_ClosedArmEast_Entries` (EMPTY:0000026) | obs, `count` | def :723 |
| E24 | `ElevatedPlusMaze_ClosedArmTotalEntries` (EMPTY:0000027) | calc, `count`; `input_id` = E22, E23 | def :730; sum 45/45 |
| E25 | `ElevatedPlusMaze_ClosedArmWest_HeadEntries` (EMPTY:0000028) | obs, `count` | def :737 |
| E26 | `ElevatedPlusMaze_ClosedArmEast_HeadEntries` (EMPTY:0000029) | obs, `count` | def :744 |
| E27 | `ElevatedPlusMaze_ClosedArmTotalHeadEntries` (EMPTY:0000030) | calc, `count`; `input_id` = E25, E26 | def :751; sum 45/45 |
| E28 | `ElevatedPlusMaze_ClosedArmWest_Time` (EMPTY:0000031) | obs, `time`, s | def :758 |
| E29 | `ElevatedPlusMaze_ClosedArmEast_Time` (EMPTY:0000032) | obs, `time`, s | def :766 |
| E30 | `ElevatedPlusMaze_ClosedArmTotalTime` (EMPTY:0000033) | calc, `time`, s; `input_id` = E28, E29 | def :774; sum 45/45 |
| E31 | `ElevatedPlusMaze_ClosedArmTotal_PercentTimeDuringTestDuration` (EMPTY:0000034) | **open: Q-E2** | def :782 "Unit: %" |
| E32 | `ElevatedPlusMaze_ClosedArmWest_LatencyToFirstEntry` (EMPTY:0000035) | obs, `time`, s | def :789 |
| E33 | `ElevatedPlusMaze_ClosedArmEast_LatencyToFirstEntry` (EMPTY:0000036) | obs, `time`, s | def :797 |
| E34 | `ElevatedPlusMaze_ClosedArmTotalLatencyToFirstEntry` (EMPTY:0000037) | obs, `time`, s (not derivable: min matches 0 of 45) | def :805 |
| E35 | `ElevatedPlusMaze_ClosedArmWest_TimeMovingTowards` (EMPTY:0000038) | obs, `time`, s | def :813 |
| E36 | `ElevatedPlusMaze_ClosedArmEast_TimeMovingTowards` (EMPTY:0000039) | obs, `time`, s | def :821 |
| E37 | `ElevatedPlusMaze_ClosedArmTotalTimeMovingTowards` (EMPTY:0000040) | calc, `time`, s; `input_id` = E35, E36 | def :829; sum 45/45 |
| E38 | `ElevatedPlusMaze_ClosedArmWest_TimeFreezing` (EMPTY:0000041) | obs, `time`, s | def :837 |
| E39 | `ElevatedPlusMaze_ClosedArmEast_TimeFreezing` (EMPTY:0000042) | obs, `time`, s | def :845 |
| E40 | `ElevatedPlusMaze_ClosedArmTotalTimeFreezing` (EMPTY:0000043) | calc, `time`, s; `input_id` = E38, E39 | def :853; sum 45/45 |
| E41 | `ElevatedPlusMaze_Center_Entries` (EMPTY:0000044) | obs, `count` | def :861 |
| E42 | `ElevatedPlusMaze_Center_HeadEntries` (EMPTY:0000045) | obs, `count` | def :867 |
| E43 | `ElevatedPlusMaze_Center_Time` (EMPTY:0000046) | obs, `time`, s | def :873 |
| E44 | `ElevatedPlusMaze_Center_PercentTimeDuringTestDuration` (EMPTY:0000047) | **open: Q-E2** | def :880 "Unit: %" |
| E45 | `ElevatedPlusMaze_Center_LatencyToFirstEntry` (EMPTY:0000048) | obs, `time`, s | def :886 |
| E46 | `ElevatedPlusMaze_Center_TimeMovingTowards` (EMPTY:0000049) | obs, `time`, s | def :893 |
| E47 | `ElevatedPlusMaze_Center_TimeFreezing` (EMPTY:0000050) | obs, `time`, s | def :900 |
| E48 | `ElevatedPlusMaze_TestDuration` (EMPTY:0000068) | not a statement: a method parameter of every EPM statement of the row, `time`, s (= 300 in 45/45; set by the importer, `doImport.m:356`) | def :1020; dict :61 |
| E49 | `ExperimentalGroupCode` (EMPTY:0000059) | **open: Q-E4** | dict :63 (`Experiment_ID`); def :961 |
| E50 | `DataExclusionFlag` (EMPTY:0000069) | **open: Q-E5** | dict :64; def :1028 |
| E51 | `SubjectLocalIdentifier` (EMPTY:0000052) | not a statement: names the entity of every statement of the row (route 3); already the subject's `local_identifier` | dict :2; def :914; [dataset audit batch 1 and 2] (3) |

**EPM open questions (one line each):**

- **Q-E1** Treatment (CNO or saline): a `term` manipulation of the animal
  (value = a CNO or saline term, both to be registered), or carried as v1,
  since no amount for saline exists and CNO's 2 mg/kg is only in a term
  definition?
- **Q-E2** The three percent-of-test-time columns: there is no percent value
  kind. (a) mint one (T12), (b) drop as derivable (each equals total time /
  300 x 100 bit-exactly in every non-NaN row, but 5 cells are NaN where the
  time is not, so dropping is not lossless), or (c) carry?
- **Q-E3** `ElevatedPlusMaze_TestIdentifier`: what is it? 28 rows hold 2..29
  (never the animal number), 17 are NaN; a `label` condition, or what?
- **Q-E4** `ExperimentalGroupCode` here is the importer's `Experiment_ID`
  (1 for animals < 300, 2 for >= 300; matches 45/45), not the treatment group
  its definition describes: a cohort `group` entity with `member_of` (T20),
  a `label` condition, or something else?
- **Q-E5** `DataExclusionFlag` (true for animals 239 and 258, "not expressing
  mCherry"): a `logical` assertion on the animal with this variable, an
  observation that mCherry is not expressed, or a note?

### 3.2 FPS — fear-potentiated startle

**What it is.** One row per startle trial: sheets `Pre-test 1`, `Pre-test 2`,
`Shock Reactivity`, `Cue test 1`, `Context 1`, `Cue test 2`, `Context 2`,
`Cue test 3` of `FPS_OTR-Cre+_Saline vs CNO_DREADDs-Gi_Experiment 1-final.xlsx`,
stacked (`doImport.m:366-392`). The importer adds `Sheet_Name` (`:385`),
`Group_ID` = the 6th character of `Session_ID` (`:398`), and drops
`Trial_List_Block`, `Chamber_ID`, `Session_ID`, `Param`, `TimeStampPT`
(`:401-402`). Written by `table2ontologyTableRowDocs(dataTable_FPS,
{'SubjectString','Trial_Num','Sheet_Name'})` (`:446-447`).

**Rows.** 6,160 v1 documents; 28 subjects (all also in EPM); (subject, trial
number, phase) is unique (6,160 distinct keys); 30 trials per phase, 10 in
Shock Reactivity (§5, E3).

**Table match (all rows below):** `v1_class` = `ontologyTableRow`,
`ontologyTableRow.ontologyNodes` = the 13-node FPS string (§5, E1, signature 0).

| id | v1 `variableName` (node) | V2 home | rests on |
|---|---|---|---|
| F1 | `ExperimentalTrialNumber` (EMPTY:0000075) | not a statement: a condition on every statement of the row, `label` (a local index; 1..30) | def :1071 "index of an individual experimental trial within a set"; dict :49; T12 label (`V_eta_tenets.md:379`) |
| F2 | `Fear_potentiatedStartle_TrialTypeIdentifier` (EMPTY:0000057) | **open: Q-F1** | def :946; dict :50 |
| F3 | `Fear_potentiatedStartle_ApparatusChamberIdentifier` (EMPTY:0000058) | **open: Q-F2** | def :954; dict :51 |
| F4 | `ExperimentalGroupCode` (EMPTY:0000059) | **open: Q-F3** | dict :52 (`Group_ID`); def :961 |
| F5 | `AcousticStartleResponse_NumberOfSamples` (EMPTY:0000060) | not a statement: a method parameter, `count` (200 or 500; 500 only on "FPS Training Trial") | def :967 "Unit: count" |
| F6 | `AcousticStartleResponse_SamplingRate` (EMPTY:0000061) | not a statement: a method parameter, `frequency`, `om:hertz` (= 1000 in 6160/6160) | def :973 "Unit: Hertz (Hz)" |
| F7 | `AcousticStartleResponse_StartleWindowOnsetAmplitude` (EMPTY:0000062) | **open: Q-F4** (obs of the animal; unit unsettled) | def :979 "millivolts (mV) or arbitrary units" |
| F8 | `AcousticStartleResponse_MaximumAmplitude` (EMPTY:0000063) | **open: Q-F4** | def :986 "millivolts (mV) or arbitrary units" |
| F9 | `AcousticStartleResponse_TimeToMaximumAmplitude` (EMPTY:0000064) | obs, `time`, source unit ms (`om:millisecond-Time`) | def :993 "Unit: milliseconds (ms)"; values 0..200 for 200-sample trials, 34..498 for 500 (fits 1 sample = 1 ms at 1000 Hz) |
| F10 | `AcousticStartleResponse_AverageAmplitude` (EMPTY:0000065) | **open: Q-F4** | def :1000 "millivolts (mV) or arbitrary units" |
| F11 | `ExperimentTrialExecutionTimestamp` (EMPTY:0000066) | **open: Q-F5** | def :1007; dict :59 |
| F12 | `Fear_potentiatedStartle_ExperimentalPhaseOrTestName` (EMPTY:0000067) | not a statement: a condition on every statement of the row, `label` (8 values, the sheet names) | def :1013; dict :60; `doImport.m:385`; T12 "a run's condition name" is a label (`V_eta_tenets.md:379`) |
| F13 | `SubjectLocalIdentifier` (EMPTY:0000052) | not a statement: names the entity (route 3) | as E51 |

**FPS open questions (one line each):**

- **Q-F1** Trial type (4 strings: `Startle 95 dB Trial`, `FPS (N) Testing
  Trial`, `FPS (L+N) Testing Trial`, `FPS Training Trial`): a term condition
  (4 terms to mint; one map row per string) or a `label` condition?
- **Q-F2** Chamber (1..8, one per animal in 28/28): an `instrument_id` to one
  device entity per chamber (T7, roles are edges), or a `label` condition?
- **Q-F3** `ExperimentalGroupCode` here is `Session_ID`'s 6th character; it is
  constant per (animal, phase) but changes across phases for 16 of 28
  animals, in squads of 8 (4 in group 4): a run batch, not a treatment group.
  What is it, and is it kept?
- **Q-F4** The three amplitudes: `voltage` with source unit mV (the source
  column keys are `V_Start`, `mV_Max`, `mV_Avg`, dict :55-58), or
  `intensity` (arbitrary units), as the definitions leave both open?
- **Q-F5** The trial timestamp (`8/19/2022 9:22:39 AM`, one per row, no time
  zone): the time reference of the row's statements, with which zone (an
  `absolute_time_reference` needs a UTC instant), or relative?

## 4. Table-level questions (both tables)

- **Q-T1** An EPM row has no time at all, yet every observation needs a
  `time_reference_id` (`interaction.json:15`): what time do EPM statements carry?
- **Q-T2** A NaN cell (39 EPM cells, §5, E3): write no statement for that cell
  and place the rest, or carry the whole row ([partly placed is carried as v1])?
- **Q-T3** FPS: one statement per cell (8 measured columns x 6,160 rows), or
  one series per (animal, phase, variable) along a trial dimension (T2
  "recurring event", `V_eta_tenets.md:112`)?
- **Q-T4** The totals (E5, E8, E11, E18, E21, E24, E27, E30, E37, E40): a
  `calculation` from the two arm statements (proposed; exact sums in 45/45),
  or an `observation` as the software reported it?
- **Q-T5** The 64 column nodes are not in the term registry: register them as
  they are (T19 step 1, already used in a dataset), or mint general variables
  ("open arm entries") with the assay in the method, as T19's naming rule asks?
- **Q-T6** What `method` term do the EPM and FPS statements carry (none is
  registered; EMPTY:0000003 / 0000004 are measurement categories, not methods)?
- **Q-T7** Table identity: is the full `ontologyNodes` string the right exact
  match, or one node only that table holds (EMPTY:0000068 for EPM,
  EMPTY:0000057 for FPS)?

---

## 5. Evidence (commands run, output abridged; full output files beside this one)

Scripts are in `scratchpad/dabmap/tools/` and were run with `python3 -I`
against `scratchpad/dabmap/corpus_Dab/Dab` (27,561 JSON files).

**E1. Tables and columns** (`tools/otr_census.py`, output `tools/otr_census.out`):

```
json files read: 27561
unparseable: 0
ontologyTableRow docs: 6205
distinct (variableNames, ontologyNodes, names) signatures: 2
=== table signature 0: 6160 rows; 13 variableNames, 13 nodes, 13 names     (FPS)
=== table signature 1: 45 rows; 51 variableNames, 51 nodes, 51 names       (EPM)
  [1] Treatment_CNOOrSalineAdministration | EMPTY:0000200 | ... distinct=2 | top=['"CNO"', '"Saline"']
  [47] ElevatedPlusMaze_TestDuration | EMPTY:0000068 | ... distinct=1 min=300 max=300
  [48] ExperimentalGroupCode | EMPTY:0000059 | ... distinct=2 min=1 max=2
  [5] AcousticStartleResponse_SamplingRate | EMPTY:0000061 | ... distinct=1 min=1000 max=1000
```

**E2. Subjects** (`tools/otr_checks.py`, output `tools/otr_checks.out`):

```
documents read: 27561
ontologyTableRow: 6205  subject: 228
EPM rows: 45  FPS rows: 6160  other: 0
EPM depends_on present on rows: 0 of 45
FPS depends_on present on rows: 0 of 6160
EPM: rows by number of subjects matching (session, local_identifier) exactly: {1: 45}
FPS: rows by number of subjects matching (session, local_identifier) exactly: {1: 6160}
```

**E3. Values and derivations** (same run; `tools/fps_more.out`, `tools/pct_exact.py`):

```
EPM NaN cells: TestIdentifier 17; OpenArmTotal_Percent 2; OpenArmNorth_Latency 1;
  OpenArmSouth_Latency 2; ClosedArmTotal_Percent 2; Center_* 2,2,2,3,2,2,2   (39 in all)
OpenArmTotalEntries == North + South: equal 45, differ 0      (same for all 10 totals)
OpenArmTotalLatency == min(two arms): equal 1, differ 43, skipped(NaN) 1
ClosedArmTotalLatency == min(two arms): equal 0, differ 45
OpenArmTotal_Percent: bit-exact t/300*100: 43 of 43 non-NaN; NaN percent while time present: 2
ClosedArmTotal_Percent: 43 of 43; NaN while time present: 2
Center_Percent: 42 of 42; NaN while time present: 1
EPM Treatment x ExperimentalGroupCode: (Saline,1):14 (CNO,1):14 (CNO,2):9 (Saline,2):8
EPM ExperimentalGroupCode vs animal>=300: (1,False):28, (2,True):17
EPM excluded animals: [239, 258]
EPM TestIdentifier == animal number? False: 28
FPS key (subject, trial number, phase): distinct 6160 max rows per key 1
FPS subjects 28 also in EPM 28
FPS subjects with >1 group code: 16;  (subject, phase) pairs with >1 group code: 0 of 224
FPS subjects with >1 chamber: 0
FPS samples x trial type: (200,Startle 95 dB):4200 (200,FPS (N)):840 (200,FPS (L+N)):840 (500,FPS Training):280
T_Max range: 200-sample trials 0..200; 500-sample trials 34..498
phase Context 1 group counts {1: 240, 3: 240, 2: 240, 4: 120}   (30 trials x 8 or 4 animals)
```

**E4. Term definitions and units** (`tools/owl_terms.py` on
`git show origin/V2:src/ontology/empty-edit.owl` from empty-ontology a16c805;
the line numbers in §3 are lines of that file):

```
EMPTY:0000006 | label@591 ... | def@590 unit: count
EMPTY:0000012 | label@627 ... | def@626 unit: seconds
EMPTY:0000015 | label@648 ... percent time ... | def@647 unit: %
EMPTY:0000058 | ... apparatus chamber identifier | def@954 unit: count or identifier string
EMPTY:0000059 | experimental group code | def@961 "A numerical code that assigns a subject to a specific experimental group ..."
EMPTY:0000063 | ... maximum amplitude | def@986 unit: millivolts (mV) or arbitrary units
EMPTY:0000064 | ... time to maximum amplitude | def@993 unit: milliseconds (ms)
EMPTY:0000200 def@1967: "... 'CNO' for Clozapine-N-oxide administration (2 mg/kg, i.p.) or 'Saline'
  for vehicle control administration (i.p.). These treatments were administered 45 minutes
  before fear conditioning and before EPM testing."
```

**E5. Term registry** (`schemas/V_eta_term_registry.json`, 865 terms):

```
EMPTY nodes from Dab tables found in registry: ['EMPTY:0000074', 'EMPTY:0000358']
missing: EMPTY:0000006 ... EMPTY:0000075 (every column node), EMPTY:0000200, ...
search for saline|clozapine|CNO|elevated plus maze|startle: no row
```

**E6. Value kinds** (classes under `schemas/did_v2/{stable,draft}` with
superclass `value`):

```
46 classes with superclass value: harmonic_component humidity irradiance item label logical
model_fit polynomial position text acceleration angle angular_velocity area capacitance charge
chemical concentration conductance contrast_sensitivity count current date dose energy force
formulation frequency gain intensity length mass ph power pressure receptive_field resistance
score substance_amount temperature term time tuning_curve velocity voltage volume
```

**E7. Sources read in the repositories:**

- NDI-matlab `origin/V2` 9b99061: `+setup/+conv/+dabrowska/doImport.m`
  (`:315-447`), `tableDoc_dictionary.json` (`:1-65`), `V2_decisions.md`
  (9 decisions, none about EPM/FPS: rows 1-9 are slices, the tetanus, labels,
  terms), `+setup/+NDIMaker/tableDocMaker.m:208-279`,
  `+migrate/+internal/ontologyRowSubjects.m:131-152`.
- DID-matlab `origin/V2` f6486be: `+did2/+convert/+migrators_j/ontology_table_row.m:6, 54, 79`.
- did-schema 078ab84: `docs/v2_working/DATASET_MAP_PROPOSAL.md:190-212, 291-293, 328-329`;
  `schemas/V_eta_carry_register.json:475` (carry-026);
  `schemas/V_eta_go_forward_class_audit.md:1142, 1152, 1212, 1220, 1228, 1238, 1244, 1246, 1250, 1252`;
  `schemas/V_eta_tenets.md` T2 (:49), T3 (:123), T12 (:368), T19 (:946), T20 (:1016);
  `schemas/did_v2/stable/{interaction,statement,dose,intensity}.json`,
  `schemas/did_v2/draft/label.json`.
