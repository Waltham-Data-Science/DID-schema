# EMPTY synonym audit (report only)

Sources: empty-ontology `845a505` (branch claude/audit-terms-2026-10-22) `src/ontology/empty-edit.owl`; did-schema `1d66bbe` (origin/claude/ecstatic-pascal-md91fw) `schemas/V_eta_term_registry.json`; NDI-matlab `fcfd876` (claude/v2-object-layer); DID-matlab `9c9cab9` (claude/ecstatic-pascal-md91fw).

Registry column: the registry row schema has no synonym field (keys: name, node, definition, status, decided, first_used_in), so "registry synonyms" is empty for every row. "reg" = a registry row exists for the node.

Candidate classes: (1) ontology vs registry; (2) source / v1 / former name; (3) abbreviation or alternative name with a cited source; (4) synonym dropped on obsoletion. Rec = recommendation (Proposed, not decided).

## Live terms (355)

| id | label | ontology synonyms | IAO:0000118 alt label | reg | candidates (class: synonym [type] rec; evidence) |
|---|---|---|---|---|---|
| EMPTY:0000001 | measurement | - | - | - | - |
| EMPTY:0000002 | behavioral measurement | - | - | - | - |
| EMPTY:0000003 | elevated plus maze measurement | - | - | - | - |
| EMPTY:0000004 | acoustic startle response measurement | - | - | - | - |
| EMPTY:0000005 | acoustic startle response derived measurement | - | - | - | - |
| EMPTY:0000006 | elevated plus maze: open arm (north) - entries | - | - | - | (2) `OpenArm_Wall__Entries` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:4 "OpenArm_Wall__Entries": "EMPTY:Elevated Plus Maze: open arm (north) - entries" |
| EMPTY:0000007 | elevated plus maze: open arm (south) - entries | - | - | - | (2) `OpenArm_OpenField__Entries` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:5 "OpenArm_OpenField__Entries": "EMPTY:Elevated Plus Maze: open arm (south) - entries" |
| EMPTY:0000008 | elevated plus maze: open arm total entries | - | - | - | (2) `OpenArmTotalEntries` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:6 "OpenArmTotalEntries": "EMPTY:Elevated Plus Maze: open arm total entries" |
| EMPTY:0000009 | elevated plus maze: open arm (north) - head entries | - | - | - | (2) `OpenArm_Wall__HeadEntries` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:7 "OpenArm_Wall__HeadEntries": "EMPTY:Elevated Plus Maze: open arm (north) - head entries" |
| EMPTY:0000010 | elevated plus maze: open arm (south) - head entries | - | - | - | (2) `OpenArm_OpenField__HeadEntries` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:8 "OpenArm_OpenField__HeadEntries": "EMPTY:Elevated Plus Maze: open arm (south) - head entries" |
| EMPTY:0000011 | elevated plus maze: open arm total head entries | - | - | - | (2) `OpenArmTotalHeadEntries` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:9 "OpenArmTotalHeadEntries": "EMPTY:Elevated Plus Maze: open arm total head entries" |
| EMPTY:0000012 | elevated plus maze: open arm (north) - time | - | - | - | (2) `OpenArm_Wall__Time` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:10 "OpenArm_Wall__Time": "EMPTY:Elevated Plus Maze: open arm (north) - time" |
| EMPTY:0000013 | elevated plus maze: open arm (south) - time | - | - | - | (2) `OpenArm_OpenField__Time` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:11 "OpenArm_OpenField__Time": "EMPTY:Elevated Plus Maze: open arm (south) - time" |
| EMPTY:0000014 | elevated plus maze: open arm total time | - | - | - | (2) `OpenArmTotalTime` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:12 "OpenArmTotalTime": "EMPTY:Elevated Plus Maze: open arm total time" |
| EMPTY:0000015 | elevated plus maze: open arm total - percent time during test duration | - | - | - | (2) `Openarm_TimePer300S_5Min_` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:13 "Openarm_TimePer300S_5Min_": "EMPTY:Elevated Plus Maze: open arm total - percent time during test duration" |
| EMPTY:0000016 | elevated plus maze: open arm (north) - latency to first entry | - | - | - | (2) `OpenArm_Wall__LatencyToFirstEntry` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:14 "OpenArm_Wall__LatencyToFirstEntry": "EMPTY:Elevated Plus Maze: open arm (north) - latency to first entry" |
| EMPTY:0000017 | elevated plus maze: open arm (south) - latency to first entry | - | - | - | (2) `OpenArm_OpenField__LatencyToFirstEntry` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:15 "OpenArm_OpenField__LatencyToFirstEntry": "EMPTY:Elevated Plus Maze: open arm (south) - latency to first entry" |
| EMPTY:0000018 | elevated plus maze: open arm total latency to first entry | - | - | - | (2) `OpenArmTotalLatencyToFirstEntry` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:16 "OpenArmTotalLatencyToFirstEntry": "EMPTY:Elevated Plus Maze: open arm total latency to first entry" |
| EMPTY:0000019 | elevated plus maze: open arm (north) - time moving towards | - | - | - | (2) `OpenArm_Wall__TimeMovingTowards` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:17 "OpenArm_Wall__TimeMovingTowards": "EMPTY:Elevated Plus Maze: open arm (north) - time moving towards" |
| EMPTY:0000020 | elevated plus maze: open arm (south) - time moving towards | - | - | - | (2) `OpenArm_OpenField__TimeMovingTowards` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:18 "OpenArm_OpenField__TimeMovingTowards": "EMPTY:Elevated Plus Maze: open arm (south) - time moving towards" |
| EMPTY:0000021 | elevated plus maze: open arm total time moving towards | - | - | - | (2) `OpenArmTotalTimeMovingTowards` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:19 "OpenArmTotalTimeMovingTowards": "EMPTY:Elevated Plus Maze: open arm total time moving towards" |
| EMPTY:0000022 | elevated plus maze: open arm (north) - time freezing | - | - | - | (2) `OpenArm_Wall__TimeFreezing` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:20 "OpenArm_Wall__TimeFreezing": "EMPTY:Elevated Plus Maze: open arm (north) - time freezing" |
| EMPTY:0000023 | elevated plus maze: open arm (south) - time freezing | - | - | - | (2) `OpenArm_OpenField__TimeFreezing` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:21 "OpenArm_OpenField__TimeFreezing": "EMPTY:Elevated Plus Maze: open arm (south) - time freezing" |
| EMPTY:0000024 | elevated plus maze: open arm total time freezing | - | - | - | (2) `OpenArmTotalTimeFreezing` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:22 "OpenArmTotalTimeFreezing": "EMPTY:Elevated Plus Maze: open arm total time freezing" |
| EMPTY:0000025 | elevated plus maze: closed arm (west) - entries | - | - | - | (2) `ClosedArm_L__Entries` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:23 "ClosedArm_L__Entries": "EMPTY:Elevated Plus Maze: closed arm (west) - entries" |
| EMPTY:0000026 | elevated plus maze: closed arm (east) - entries | - | - | - | (2) `ClosedArm_R__Entries` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:24 "ClosedArm_R__Entries": "EMPTY:Elevated Plus Maze: closed arm (east) - entries" |
| EMPTY:0000027 | elevated plus maze: closed arm total entries | - | - | - | (2) `ClosedArmTotalEntries` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:25 "ClosedArmTotalEntries": "EMPTY:Elevated Plus Maze: closed arm total entries" |
| EMPTY:0000028 | elevated plus maze: closed arm (west) - head entries | - | - | - | (2) `ClosedArm_L__HeadEntries` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:26 "ClosedArm_L__HeadEntries": "EMPTY:Elevated Plus Maze: closed arm (west) - head entries" |
| EMPTY:0000029 | elevated plus maze: closed arm (east) - head entries | - | - | - | (2) `ClosedArm_R__HeadEntries` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:27 "ClosedArm_R__HeadEntries": "EMPTY:Elevated Plus Maze: closed arm (east) - head entries" |
| EMPTY:0000030 | elevated plus maze: closed arm total head entries | - | - | - | (2) `ClosedArmTotalHeadEntries` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:28 "ClosedArmTotalHeadEntries": "EMPTY:Elevated Plus Maze: closed arm total head entries" |
| EMPTY:0000031 | elevated plus maze: closed arm (west) - time | - | - | - | (2) `ClosedArm_L__Time` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:29 "ClosedArm_L__Time": "EMPTY:Elevated Plus Maze: closed arm (west) - time" |
| EMPTY:0000032 | elevated plus maze: closed arm (east) - time | - | - | - | (2) `ClosedArm_R__Time` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:30 "ClosedArm_R__Time": "EMPTY:Elevated Plus Maze: closed arm (east) - time" |
| EMPTY:0000033 | elevated plus maze: closed arm total time | - | - | - | (2) `ClosedArmTotalTime` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:31 "ClosedArmTotalTime": "EMPTY:Elevated Plus Maze: closed arm total time" |
| EMPTY:0000034 | elevated plus maze: closed arm total - percent time during test duration | - | - | - | (2) `Closedarm_TimePer300S_5Min_` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:32 "Closedarm_TimePer300S_5Min_": "EMPTY:Elevated Plus Maze: closed arm total - percent time during test duration" |
| EMPTY:0000035 | elevated plus maze: closed arm (west) - latency to first entry | - | - | - | (2) `ClosedArm_L__LatencyToFirstEntry` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:33 "ClosedArm_L__LatencyToFirstEntry": "EMPTY:Elevated Plus Maze: closed arm (west) - latency to first entry" |
| EMPTY:0000036 | elevated plus maze: closed arm (east) - latency to first entry | - | - | - | (2) `ClosedArm_R__LatencyToFirstEntry` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:34 "ClosedArm_R__LatencyToFirstEntry": "EMPTY:Elevated Plus Maze: closed arm (east) - latency to first entry" |
| EMPTY:0000037 | elevated plus maze: closed arm total latency to first entry | - | - | - | (2) `ClosedArmTotalLatencyToFirstEntry` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:35 "ClosedArmTotalLatencyToFirstEntry": "EMPTY:Elevated Plus Maze: closed arm total latency to first entry" |
| EMPTY:0000038 | elevated plus maze: closed arm (west) - time moving towards | - | - | - | (2) `ClosedArm_L__TimeMovingTowards` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:36 "ClosedArm_L__TimeMovingTowards": "EMPTY:Elevated Plus Maze: closed arm (west) - time moving towards" |
| EMPTY:0000039 | elevated plus maze: closed arm (east) - time moving towards | - | - | - | (2) `ClosedArm_R__TimeMovingTowards` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:37 "ClosedArm_R__TimeMovingTowards": "EMPTY:Elevated Plus Maze: closed arm (east) - time moving towards" |
| EMPTY:0000040 | elevated plus maze: closed arm total time moving towards | - | - | - | (2) `ClosedArmTotalTimeMovingTowards` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:38 "ClosedArmTotalTimeMovingTowards": "EMPTY:Elevated Plus Maze: closed arm total time moving towards" |
| EMPTY:0000041 | elevated plus maze: closed arm (west) - time freezing | - | - | - | (2) `ClosedArm_L__TimeFreezing` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:39 "ClosedArm_L__TimeFreezing": "EMPTY:Elevated Plus Maze: closed arm (west) - time freezing" |
| EMPTY:0000042 | elevated plus maze: closed arm (east) - time freezing | - | - | - | (2) `ClosedArm_R__TimeFreezing` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:40 "ClosedArm_R__TimeFreezing": "EMPTY:Elevated Plus Maze: closed arm (east) - time freezing" |
| EMPTY:0000043 | elevated plus maze: closed arm total time freezing | - | - | - | (2) `ClosedArmTotalTimeFreezing` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:41 "ClosedArmTotalTimeFreezing": "EMPTY:Elevated Plus Maze: closed arm total time freezing" |
| EMPTY:0000044 | elevated plus maze: center - entries | - | - | - | (2) `Center_Entries` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:42 "Center_Entries": "EMPTY:Elevated Plus Maze: center - entries" |
| EMPTY:0000045 | elevated plus maze: center - head entries | - | - | - | (2) `Center_HeadEntries` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:43 "Center_HeadEntries": "EMPTY:Elevated Plus Maze: center - head entries" |
| EMPTY:0000046 | elevated plus maze: center - time | - | - | - | (2) `Center_Time` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:44 "Center_Time": "EMPTY:Elevated Plus Maze: center - time" |
| EMPTY:0000047 | elevated plus maze: center - percent time during test duration | - | - | - | (2) `Center_TimePer300S_5Min_` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:45 "Center_TimePer300S_5Min_": "EMPTY:Elevated Plus Maze: center - percent time during test duration" |
| EMPTY:0000048 | elevated plus maze: center - latency to first entry | - | - | - | (2) `Center_LatencyToFirstEntry` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:46 "Center_LatencyToFirstEntry": "EMPTY:Elevated Plus Maze: center - latency to first entry" |
| EMPTY:0000049 | elevated plus maze: center - time moving towards | - | - | - | (2) `Center_TimeMovingTowards` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:47 "Center_TimeMovingTowards": "EMPTY:Elevated Plus Maze: center - time moving towards" |
| EMPTY:0000050 | elevated plus maze: center - time freezing | - | - | - | (2) `Center_TimeFreezing` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:48 "Center_TimeFreezing": "EMPTY:Elevated Plus Maze: center - time freezing" |
| EMPTY:0000051 | elevated plus maze: test identifier | - | - | - | (2) `Test` [related] low (generic word); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:62 "Test": "EMPTY:Elevated Plus Maze: test identifier" |
| EMPTY:0000052 | subject local identifier | - | - | - | (2) `SubjectString` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:2 "SubjectString": "EMPTY:Subject local identifier"<br>(2) `subjectName` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:40 "subjectName": "EMPTY:subject local identifier" |
| EMPTY:0000053 | fear-potentiated startle: baseline acoustic startle response amplitude | - | - | - | - |
| EMPTY:0000054 | session timeline | - | - | - | - |
| EMPTY:0000055 | postnatal day | - | - | - | (3) `P` [exact (abbreviation)] not recommended: single letter used as a prefix (P0, P10); own definition "Often abbreviated ... with a capital P (as in P0, P10, etc)" |
| EMPTY:0000056 | microelectrode voltage offset | - | - | - | - |
| EMPTY:0000057 | fear-potentiated startle: trial type identifier | - | - | - | (2) `Trial_ID` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:50 "Trial_ID": "EMPTY:Fear-Potentiated Startle: trial type identifier" |
| EMPTY:0000058 | fear-potentiated startle: apparatus chamber identifier | - | - | - | (2) `Channel_ID` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:51 "Channel_ID": "EMPTY:Fear-Potentiated Startle: apparatus chamber identifier" |
| EMPTY:0000059 | experimental group code | - | - | - | (2) `Group_ID` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:52 "Group_ID": "EMPTY:Experimental group code"<br>(2) `Experiment_ID` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:63 "Experiment_ID": "EMPTY:Experimental group code" |
| EMPTY:0000060 | acoustic startle response: number of samples | - | - | - | (2) `Samples` [related] low (generic word); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:53 "Samples": "EMPTY:Acoustic Startle Response: number of samples" |
| EMPTY:0000061 | acoustic startle response: sampling rate | - | - | - | (2) `Rate` [related] low (generic word); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:54 "Rate": "EMPTY:Acoustic Startle Response: sampling rate" |
| EMPTY:0000062 | acoustic startle response: startle window onset amplitude | - | - | - | (2) `V_Start` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:55 "V_Start": "EMPTY:Acoustic Startle Response: startle window onset amplitude" |
| EMPTY:0000063 | acoustic startle response: maximum amplitude | - | - | - | (2) `mV_Max` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:56 "mV_Max": "EMPTY:Acoustic Startle Response: maximum amplitude" |
| EMPTY:0000064 | acoustic startle response: time to maximum amplitude | - | - | - | (2) `T_Max` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:57 "T_Max": "EMPTY:Acoustic Startle Response: time to maximum amplitude" |
| EMPTY:0000065 | acoustic startle response: average amplitude | - | - | - | (2) `mV_Avg` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:58 "mV_Avg": "EMPTY:Acoustic Startle Response: average amplitude" |
| EMPTY:0000066 | experiment trial execution timestamp | - | - | - | (2) `Run_Time` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:59 "Run_Time": "EMPTY:Experiment trial execution timestamp"<br>(2) `ExperimentDate` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+hunsberger/tableDoc_dictionary.json:5 "ExperimentDate": "EMPTY:experiment trial execution timestamp" |
| EMPTY:0000067 | fear-potentiated startle: experimental phase or test name | - | - | - | (2) `Sheet_Name` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:60 "Sheet_Name": "EMPTY:Fear-Potentiated Startle: experimental phase or test name" |
| EMPTY:0000068 | elevated plus maze: test duration | - | - | - | (2) `Test_Duration` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:61 "Test_Duration": "EMPTY:Elevated Plus Maze: test duration" |
| EMPTY:0000069 | data exclusion flag | - | - | - | (2) `Exclude` [related] low (generic word); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:64 "Exclude": "EMPTY:Data exclusion flag"<br>(2) `exclude` [related] low (generic word); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:6 "exclude": "EMPTY:data exclusion flag" |
| EMPTY:0000070 | type II BNST neuron | - | BNSTNeuronTypeII | - | - |
| EMPTY:0000071 | investigator-defined cell type | - | investigatorDefinedCellType | - | - |
| EMPTY:0000072 | type I BNST neuron | - | BNSTNeuronTypeI | - | - |
| EMPTY:0000073 | type III BNST neuron | - | BNSTNeuronTypeIII | - | - |
| EMPTY:0000074 | optogenetic tetanus stimulation target location | - | optogeneticTetanusStimulationTargetLocation | - | - |
| EMPTY:0000075 | experimental trial number | - | - | - | (2) `Trial_Num` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:49 "Trial_Num": "EMPTY:Experimental trial number" |
| EMPTY:0000076 | descriptor | - | - | - | - |
| EMPTY:0000077 | manipulation | - | - | - | - |
| EMPTY:0000078 | epoch-related manipulation | - | - | - | - |
| EMPTY:0000079 | subject-related manipulation | - | - | - | - |
| EMPTY:0000080 | parameter | - | - | - | - |
| EMPTY:0000081 | identifier | - | - | - | - |
| EMPTY:0000082 | universally unique identifier | UUID [Exact] | - | - | - |
| EMPTY:0000083 | enumerated identifier | - | - | - | - |
| EMPTY:0000084 | categorical identifier | - | - | - | - |
| EMPTY:0000085 | flag | - | - | - | - |
| EMPTY:0000086 | ontology node | - | - | - | - |
| EMPTY:0000087 | NDI document identifier | - | - | - | - |
| EMPTY:0000088 | time-related measurement | - | - | - | - |
| EMPTY:0000089 | timestamp | - | - | - | - |
| EMPTY:0000090 | duration | - | - | - | - |
| EMPTY:0000091 | timepoint | - | - | - | - |
| EMPTY:0000092 | elevated plus maze parameter | - | - | - | - |
| EMPTY:0000093 | fear-potentiated startle parameter | - | - | - | - |
| EMPTY:0000096 | subject document identifier | - | - | - | (2) `subject_id` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:41 "subject_id": "EMPTY:subject document identifier" |
| EMPTY:0000097 | C. elegans assay parameter | - | - | - | - |
| EMPTY:0000098 | bacterial parameter | - | - | - | - |
| EMPTY:0000099 | C. elegans assay phase | - | - | - | (2) `assayPhase` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:3 "assayPhase": "EMPTY:C. elegans assay phase" |
| EMPTY:0000100 | C. elegans behavioral assay measurement | - | - | - | - |
| EMPTY:0000101 | C. elegans behavioral assay parameter | - | - | - | - |
| EMPTY:0000102 | C. elegans cultivation parameter | - | - | - | - |
| EMPTY:0000103 | experiment session identifier | - | - | - | (2) `expID` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:2 "expID": "EMPTY:experiment session identifier" |
| EMPTY:0000104 | bacterial strain document identifier | - | - | - | (2) `bacteriaStrain` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:10 "bacteriaStrain": "EMPTY:bacterial strain document identifier" |
| EMPTY:0000105 | target seeding OD600 | - | - | Y | (2) `growthOD600` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:22 "growthOD600": "EMPTY:bacterial OD600 (target) at seeding"<br>(2) `patchOD600` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:34 "patchOD600": "EMPTY:bacterial OD600 (target) at seeding"<br>(2) `OD600` [related] low (generic word); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:57 "OD600": "EMPTY:bacterial OD600 (target) at seeding"<br>(2) `bacterial OD600 (target) at seeding` [related] propose (released label, cited by v1 data); empty-ontology origin/main label of EMPTY_0000105; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:22,34,57; DID-matlab 9c9cab9 src/did/+did2/+convert/resolveLawnPlateSubjects.m:339 v1 shortName BacterialOD600TargetAtSeeding |
| EMPTY:0000106 | bacterial plate seeding timestamp | - | - | - | (2) `growthTimeSeed` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:11 "growthTimeSeed": "EMPTY:bacterial plate seeding timestamp"<br>(2) `timeSeed` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:26 "timeSeed": "EMPTY:bacterial plate seeding timestamp" |
| EMPTY:0000107 | bacterial plate cold storage timestamp | - | - | - | (2) `growthTimeColdRoom` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:12 "growthTimeColdRoom": "EMPTY:bacterial plate cold storage timestamp"<br>(2) `timeColdRoom` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:27 "timeColdRoom": "EMPTY:bacterial plate cold storage timestamp"<br>(2) `timeSeedColdRoom` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:56 "timeSeedColdRoom": "EMPTY:bacterial plate cold storage timestamp" |
| EMPTY:0000108 | bacterial plate room temperature timestamp | - | - | - | (2) `growthTimeRoomTemp` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:13 "growthTimeRoomTemp": "EMPTY:bacterial plate room temperature timestamp"<br>(2) `timeRoomTemp` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:28 "timeRoomTemp": "EMPTY:bacterial plate room temperature timestamp" |
| EMPTY:0000109 | C. elegans developmental stage | - | - | - | (2) `growthAge` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:14 "growthAge": "EMPTY:C. elegans developmental stage"<br>(2) `age` [related] low (generic word); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:29 "age": "EMPTY:C. elegans developmental stage" |
| EMPTY:0000110 | bacterial OD600 measurement | - | - | - | (2) `OD600Real` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:17 "OD600Real": "EMPTY:bacterial OD600 measurement" |
| EMPTY:0000111 | bacterial colony forming units (CFU) measurement | - | - | - | (2) `CFU` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:18 "CFU": "EMPTY:bacterial colony forming units (CFU) measurement" |
| EMPTY:0000112 | bacterial plate identifier | - | - | - | (2) `plateID` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:4 "plateID": "EMPTY:bacterial plate identifier" |
| EMPTY:0000113 | bacterial plate document identifier | - | - | - | (2) `plate_id` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:5 "plate_id": "EMPTY:bacterial plate document identifier" |
| EMPTY:0000114 | C. elegans picked timestamp | - | - | - | (2) `growthTimePicked` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:15 "growthTimePicked": "EMPTY:C. elegans picked timestamp"<br>(2) `timePicked` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:30 "timePicked": "EMPTY:C. elegans picked timestamp" |
| EMPTY:0000115 | C. elegans behavioral assay label | - | - | - | (2) `assayType` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:24 "assayType": "EMPTY:C. elegans behavioral assay label" |
| EMPTY:0000116 | bacterial OD600 label | - | - | - | (2) `growthOD600Label` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:7 "growthOD600Label": "EMPTY:bacterial OD600 label"<br>(2) `OD600Label` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:25 "OD600Label": "EMPTY:bacterial OD600 label" |
| EMPTY:0000117 | bacterial plate growth duration label | - | - | - | (2) `growthConditionLabel` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:8 "growthConditionLabel": "EMPTY:bacterial plate growth duration label" |
| EMPTY:0000118 | bacterial plate peptone inclusion flag | - | - | - | (2) `peptoneFlag` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:9 "peptoneFlag": "EMPTY:bacterial plate peptone inclusion flag" |
| EMPTY:0000119 | bacteria growth duration after seeding | - | - | Y | (2) `growthLawnGrowthDuration` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:16 "growthLawnGrowthDuration": "EMPTY:bacteria growth duration after seeding"<br>(2) `lawnGrowthDuration` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:31 "lawnGrowthDuration": "EMPTY:bacteria growth duration after seeding" |
| EMPTY:0000123 | bacterial patch identifier | - | - | - | (2) `patchID` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:21 "patchID": "EMPTY:bacterial patch identifier" |
| EMPTY:0000124 | bacterial patch center: X coordinate | - | - | - | (2) `patchCenterX` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:35 "patchCenterX": "EMPTY:bacterial patch center: X coordinate" |
| EMPTY:0000125 | bacterial patch center: Y coordinate | - | - | - | (2) `patchCenterY` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:36 "patchCenterY": "EMPTY:bacterial patch center: Y coordinate" |
| EMPTY:0000128 | subject identifier | - | - | - | (2) `wormID` [related] do not add: worm-specific name on a general term; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:39 "wormID": "EMPTY:subject identifier" |
| EMPTY:0000129 | C. elegans behavioral assay: video recording | - | - | - | - |
| EMPTY:0000133 | bacterial patch fluorescence image (normalized) | - | - | - | - |
| EMPTY:0000134 | bacterial patch document identifier | - | - | - | (2) `patch_id` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:45 "patch_id": "EMPTY:bacterial patch document identifier" |
| EMPTY:0000137 | body midpoint | C. elegans midpoint [Related] | - | Y | (1) ontology synonyms not in registry (registry has no synonym field) |
| EMPTY:0000139 | C. elegans behavioral assay: encounter identifier | - | - | - | (2) `encounterNum` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:42 "encounterNum": "EMPTY:C. elegans behavioral assay: encounter identifier" |
| EMPTY:0000141 | C. elegans behavioral assay: encounter offset time | - | - | - | (2) `timeExit` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:44 "timeExit": "EMPTY:C. elegans behavioral assay: encounter offset time" |
| EMPTY:0000150 | bacterial fluorescence assay measurement | - | - | - | - |
| EMPTY:0000151 | agar plate pouring timestamp | - | - | - | (2) `timePoured` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:54 "timePoured": "EMPTY:agar plate pouring timestamp" |
| EMPTY:0000152 | agar plate cold storage timestamp | - | - | - | (2) `timePouredColdRoom` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:55 "timePouredColdRoom": "EMPTY:agar plate cold storage timestamp" |
| EMPTY:0000153 | microscopy image identifier | - | - | - | (2) `imageID` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:58 "imageID": "EMPTY:microscopy image identifier" |
| EMPTY:0000154 | microscopy image exposure time | - | - | - | (2) `exposureTime` [related] propose; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:59 "exposureTime": "EMPTY:microscopy image exposure time" |
| EMPTY:0000161 | bacterial measurement | - | - | - | - |
| EMPTY:0000162 | amplitude | - | - | - | - |
| EMPTY:0000163 | contextual fear conditioning measurement | - | - | - | - |
| EMPTY:0000164 | contextual fear conditioning parameter | - | - | - | - |
| EMPTY:0000165 | brain region name | - | - | - | - |
| EMPTY:0000166 | brain region ontology identifier | - | - | - | (2) `BrainRegionOntology` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+hunsberger/tableDoc_dictionary.json:14 "BrainRegionOntology": "EMPTY:brain region ontology identifier" |
| EMPTY:0000167 | cell count | - | - | - | - |
| EMPTY:0000168 | EYFP average cell count | - | - | - | (2) `eYFPAvg` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+hunsberger/tableDoc_dictionary.json:15 "eYFPAvg": "EMPTY:EYFP average cell count" |
| EMPTY:0000169 | c-Fos average cell count | - | - | - | (2) `cFosAvg` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+hunsberger/tableDoc_dictionary.json:16 "cFosAvg": "EMPTY:c-Fos average cell count" |
| EMPTY:0000170 | EYFP engram average cell count | - | - | - | (2) `eYFPEngramAvg` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+hunsberger/tableDoc_dictionary.json:17 "eYFPEngramAvg": "EMPTY:EYFP engram average cell count" |
| EMPTY:0000171 | c-Fos engram average cell count | - | - | - | (2) `cFosEngramAvg` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+hunsberger/tableDoc_dictionary.json:18 "cFosEngramAvg": "EMPTY:c-Fos engram average cell count" |
| EMPTY:0000172 | subject box identifier | - | - | - | (2) `BoxNumber` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+hunsberger/tableDoc_dictionary.json:4 "BoxNumber": "EMPTY:subject box identifier" |
| EMPTY:0000173 | contextual fear conditioning: block type | - | - | - | (2) `BlockType` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+hunsberger/tableDoc_dictionary.json:8 "BlockType": "EMPTY:contextual fear conditioning: block type" |
| EMPTY:0000174 | contextual fear conditioning: block minute | - | - | - | (2) `BlockMinute` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+hunsberger/tableDoc_dictionary.json:9 "BlockMinute": "EMPTY:contextual fear conditioning: block minute" |
| EMPTY:0000175 | contextual fear conditioning: time freezing | - | - | - | (2) `CFCSeconds` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+hunsberger/tableDoc_dictionary.json:10 "CFCSeconds": "EMPTY:contextual fear conditioning: time freezing" |
| EMPTY:0000176 | contextual fear conditioning: block duration | - | - | - | (2) `CFCDuration` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+hunsberger/tableDoc_dictionary.json:11 "CFCDuration": "EMPTY:contextual fear conditioning: block duration" |
| EMPTY:0000177 | contextual fear conditioning: percent time freezing | - | - | - | (2) `CFCFreezing` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+hunsberger/tableDoc_dictionary.json:12 "CFCFreezing": "EMPTY:contextual fear conditioning: percent time freezing" |
| EMPTY:0000178 | ArcCreERT2 (+) (129S6/SvEv) | - | - | - | - |
| EMPTY:0000179 | transgenic mouse | - | - | - | - |
| EMPTY:0000180 | ROSA26-CAG-loxp-stop-loxp-EYFP-WPRE (-/-) (129S6/SvEv) | - | - | - | - |
| EMPTY:0000181 | ArcCreERT2 x eYFP (129S/SvEv) | - | - | - | - |
| EMPTY:0000182 | dorsal dentate gyrus of hippocampal formation | - | dDG | - | - |
| EMPTY:0000183 | ventral dentate gyrus of hippocampal formation | - | vDG | - | - |
| EMPTY:0000184 | dorsal CA3 | - | dCA3 | - | - |
| EMPTY:0000185 | ventral CA3 | - | vCA3 | - | - |
| EMPTY:0000186 | dorsal CA1 | - | - | - | - |
| EMPTY:0000187 | ventral CA1 | - | - | - | - |
| EMPTY:0000188 | subject cage identifier | - | - | - | - |
| EMPTY:0000189 | treatment | - | - | - | - |
| EMPTY:0000190 | treatment: experienced cricket hunting | - | - | - | - |
| EMPTY:0000191 | treatment: has not experienced cricket hunting | - | - | - | - |
| EMPTY:0000192 | treatment: acclimation onset time | - | - | - | - |
| EMPTY:0000193 | treatment: acclimation temperature | - | - | - | - |
| EMPTY:0000194 | treatment: non-survival experiment time | - | - | - | - |
| EMPTY:0000195 | treatment: left eye premature eye opening | - | - | - | - |
| EMPTY:0000196 | treatment: right eye premature eye opening | - | - | - | - |
| EMPTY:0000197 | treatment: natural left eye opening | - | - | - | - |
| EMPTY:0000198 | treatment: natural right eye opening | - | - | - | - |
| EMPTY:0000199 | treatment: grating direction-of-motion visual stimulation | - | - | - | - |
| EMPTY:0000200 | treatment: CNO or saline administration | - | - | - | (2) `Treatment` [related] low (generic word); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json:3 "Treatment": "EMPTY:Treatment: CNO or saline administration" |
| EMPTY:0000201 | date of birth | - | - | - | - |
| EMPTY:0000202 | treatment: food restriction onset time | - | - | - | - |
| EMPTY:0000203 | treatment: food restriction offset time | - | - | - | - |
| EMPTY:0000204 | treatment: culture from cell type | - | - | - | - |
| EMPTY:0000205 | purpose | - | - | - | - |
| EMPTY:0000206 | purpose: assessing spatial frequency tuning | - | - | - | - |
| EMPTY:0000207 | purpose: assessing temporal frequency tuning | - | - | - | - |
| EMPTY:0000208 | purpose: assessing direction of motion tuning | - | - | - | - |
| EMPTY:0000209 | purpose: assessing contrast tuning | - | - | - | - |
| EMPTY:0000210 | purpose: assessing ocular dominance or binocular matching | - | - | - | - |
| EMPTY:0000211 | purpose: assessing the pyloric rhythm | - | - | - | - |
| EMPTY:0000212 | purpose: assessing the gastric mill rhythm | - | - | - | - |
| EMPTY:0000213 | purpose: assessing activity with temperature manipulation | - | - | - | - |
| EMPTY:0000214 | approach | - | - | - | - |
| EMPTY:0000215 | approach: left eye view blocked | - | - | - | - |
| EMPTY:0000216 | approach: right eye view blocked | - | - | - | - |
| EMPTY:0000217 | approach: command temperature constant | - | - | - | - |
| EMPTY:0000218 | approach: command temperature start | - | - | - | - |
| EMPTY:0000219 | approach: command temperature end | - | - | - | - |
| EMPTY:0000220 | approach: before optogenetic tetanus | - | - | - | - |
| EMPTY:0000221 | approach: after optogenetic tetanus | - | - | - | - |
| EMPTY:0000222 | approach: before artificial visual stimulation | - | - | - | - |
| EMPTY:0000223 | approach: after artificial visual stimulation | - | - | - | - |
| EMPTY:0000224 | subject text identifier | - | - | - | - |
| EMPTY:0000225 | subject enumerated identifier | - | - | - | - |
| EMPTY:0000226 | experiment metadata file | - | - | - | - |
| EMPTY:0000227 | data-independent acquisition (DIA) | - | - | - | - |
| EMPTY:0000228 | slide scanner image acquisition | - | - | - | - |
| EMPTY:0000229 | echocardiogram acquisition | - | - | - | - |
| EMPTY:0000230 | unknown electronic file type | - | - | - | - |
| EMPTY:0000231 | C. elegans chemotaxis assay parameter | - | - | - | - |
| EMPTY:0000232 | C. elegans chemotaxis assay parameter: chemoattractant mixture table | - | - | - | (2) `mixture_table` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+babu/tableDoc_dictionary.json:3 "mixture_table": "EMPTY:C. elegans chemotaxis assay parameter: chemoattractant mixture table" |
| EMPTY:0000233 | C. elegans chemotaxis assay parameter: chemoattractant mixture volume | - | - | - | (2) `odorVolume` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+babu/tableDoc_dictionary.json:4 "odorVolume": "EMPTY:C. elegans chemotaxis assay parameter: chemoattractant mixture volume" |
| EMPTY:0000234 | C. elegans chemotaxis assay parameter: assay duration | - | - | - | (2) `duration` [related] low (generic word); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+babu/tableDoc_dictionary.json:5 "duration": "EMPTY:C. elegans chemotaxis assay parameter: assay duration" |
| EMPTY:0000235 | C. elegans chemotaxis assay measurement | - | - | - | - |
| EMPTY:0000236 | C. elegans chemotaxis assay measurement: McCutcheon index | chemotactic ratio [Exact] | - | - | (2) `CI` [related] hold: #127 says Babu comments call CI the chemotaxis index, not McCutcheon index; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+babu/tableDoc_dictionary.json:6 "CI": "EMPTY:C. elegans chemotaxis assay measurement: McCutcheon index" |
| EMPTY:0000237 | C. elegans chemotaxis assay measurement: mean velocity | - | - | - | (2) `speed` [related] low (generic word); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+babu/tableDoc_dictionary.json:7 "speed": "EMPTY:C. elegans chemotaxis assay measurement: mean velocity" |
| EMPTY:0000238 | investigator-defined strain | - | - | - | - |
| EMPTY:0000239 | C. elegans strain | - | - | - | - |
| EMPTY:0000240 | BAB9001 | - | - | - | - |
| EMPTY:0000241 | BAB9002 | - | - | - | - |
| EMPTY:0000242 | TM5848 | - | - | - | - |
| EMPTY:0000243 | PT3602 | - | - | - | - |
| EMPTY:0000244 | BAB9003 | - | - | - | - |
| EMPTY:0000245 | BAB9004 | - | - | - | - |
| EMPTY:0000246 | BAB9005 | - | - | - | - |
| EMPTY:0000247 | fluorescence imaging measurement | - | - | - | - |
| EMPTY:0000248 | mean fluorescence intensity | - | - | - | (2) `fluorescence` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+babu/tableDoc_dictionary.json:9 "fluorescence": "EMPTY:mean fluorescence intensity" |
| EMPTY:0000249 | fluorescent punctal count | - | - | - | (2) `puncta` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+babu/tableDoc_dictionary.json:8 "puncta": "EMPTY:fluorescent punctal count" |
| EMPTY:0000250 | fluorescence imaging parameter | - | - | - | - |
| EMPTY:0000251 | fluorescence target ontology identifier | - | - | - | (2) `neuronID` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+babu/tableDoc_dictionary.json:11 "neuronID": "EMPTY:fluorescence target ontology identifier" |
| EMPTY:0000252 | fluorescence target name | - | - | - | (2) `neuron` [related] deferred (#127); NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+babu/tableDoc_dictionary.json:10 "neuron": "EMPTY:fluorescence target name" |
| EMPTY:0000253 | SnapGene file format | - | - | - | - |
| EMPTY:0000254 | Escherichia coli OP50: heat-killed | - | - | - | - |
| EMPTY:0000255 | C. elegans transfer method: M9 buffer wash | - | - | - | - |
| EMPTY:0000256 | C. elegans transfer method: titanium pick | - | - | - | - |
| EMPTY:0000257 | C. elegans chemotaxis assay: video recording | - | - | - | - |
| EMPTY:0000258 | fluorescence imaging data | - | - | - | - |
| EMPTY:0000259 | OME-Zarr | - | - | Y | (3) `OME-NGFF` [related] propose; own definition "OME Next-Generation File Format (OME-NGFF) specification" |
| EMPTY:0000260 | frame | - | - | Y | - |
| EMPTY:0000261 | arbitrary unit per millisecond | AU/ms [Exact] | - | Y | (1) ontology synonyms not in registry (registry has no synonym field) |
| EMPTY:0000262 | nematode growth medium | NGM [Exact]; NGM agar [Exact] | - | Y | (1) ontology synonyms not in registry (registry has no synonym field) |
| EMPTY:0000263 | nematode growth medium without peptone | NGM without peptone [Exact]; peptone-free NGM [Exact] | - | Y | (1) ontology synonyms not in registry (registry has no synonym field) |
| EMPTY:0000264 | LB with carbenicillin | LB + carbenicillin [Exact] | - | Y | (1) ontology synonyms not in registry (registry has no synonym field) |
| EMPTY:0000265 | S basal | S Basal [Exact]; S basal buffer [Exact] | - | Y | (1) ontology synonyms not in registry (registry has no synonym field) |
| EMPTY:0000266 | S medium | S Complete [Exact]; S complete medium [Exact]; S-Complete [Exact] | - | Y | (1) ontology synonyms not in registry (registry has no synonym field) |
| EMPTY:0000267 | magnesium sulfate solution | - | - | Y | - |
| EMPTY:0000268 | calcium chloride solution | - | - | Y | - |
| EMPTY:0000269 | potassium phosphate monobasic solution | KH2PO4 solution [Exact] | - | Y | (1) ontology synonyms not in registry (registry has no synonym field) |
| EMPTY:0000270 | potassium phosphate dibasic solution | K2HPO4 solution [Exact] | - | Y | (1) ontology synonyms not in registry (registry has no synonym field) |
| EMPTY:0000271 | cholesterol solution | cholesterol in ethanol [Exact] | - | Y | (1) ontology synonyms not in registry (registry has no synonym field) |
| EMPTY:0000272 | peak speed before an event | - | - | Y | - |
| EMPTY:0000273 | minimum speed after an event | - | - | Y | - |
| EMPTY:0000274 | time to slow down | - | - | - | (2) `timeSlowDown` [related] propose; own rdfs:comment "As timeSlowDown in analyzeEncounters (Haley et al. 2024)"; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/import_V2_decisions.md:138 (derived column) |
| EMPTY:0000275 | entity in contact | - | - | Y | (2) `bacterial patch in contact` [(narrow)] do not add: V2-interim label, never released, generalised away by T19 decision; empty-ontology history (label at an earlier commit on V2); comment "Generalised 2026-10-20 (tenet T19) from ..."<br>(2) `lawnID` [(narrow)] do not add: names the patch, term generalised (same reasoning as distanceLawnEdge); own rdfs:comment "As lawnID in analyzeEncounters"; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/encounterDocuments.m:300-306 enc.lawnID |
| EMPTY:0000276 | nearest bacterial patch edge | - | - | - | - |
| EMPTY:0000277 | encounter period | - | - | Y | (2) `patch encounter period` [(narrow)] do not add: V2-interim label, never released, generalised away by T19 decision; empty-ontology history (label at an earlier commit on V2) |
| EMPTY:0000278 | before the first encounter | - | - | Y | (2) `before the first patch encounter` [(narrow)] do not add: V2-interim label, never released, generalised away by T19 decision; empty-ontology history (label at an earlier commit on V2) |
| EMPTY:0000279 | during the encounter | - | - | Y | (2) `during the patch encounter` [(narrow)] do not add: V2-interim label, never released, generalised away by T19 decision; empty-ontology history (label at an earlier commit on V2) |
| EMPTY:0000280 | after the encounter | - | - | Y | (2) `after the patch encounter` [(narrow)] do not add: V2-interim label, never released, generalised away by T19 decision; empty-ontology history (label at an earlier commit on V2) |
| EMPTY:0000281 | analysis window start | - | - | Y | - |
| EMPTY:0000282 | analysis window end | - | - | Y | - |
| EMPTY:0000283 | bacterial patch edge | - | - | Y | - |
| EMPTY:0000284 | bacterial patch center | - | - | Y | - |
| EMPTY:0000285 | bacterial patch fluorescence peak | - | - | Y | - |
| EMPTY:0000286 | distance end point | - | - | Y | - |
| EMPTY:0000287 | normalization to background illumination | - | - | Y | - |
| EMPTY:0000288 | circularity | - | - | Y | - |
| EMPTY:0000289 | behavioral state | - | - | Y | - |
| EMPTY:0000290 | exploitation | - | - | Y | - |
| EMPTY:0000291 | sensing | - | - | Y | - |
| EMPTY:0000292 | encounter type | - | - | Y | - |
| EMPTY:0000293 | patch exploitation encounter | exploit [Exact] | - | Y | (1) ontology synonyms not in registry (registry has no synonym field) |
| EMPTY:0000294 | patch sampling encounter | sample [Exact] | - | Y | (1) ontology synonyms not in registry (registry has no synonym field) |
| EMPTY:0000295 | on-patch search encounter | search on patch [Exact]; searchOn [Exact] | - | Y | (1) ontology synonyms not in registry (registry has no synonym field) |
| EMPTY:0000296 | off-patch search encounter | search off patch [Exact]; searchOff [Exact] | - | Y | (1) ontology synonyms not in registry (registry has no synonym field) |
| EMPTY:0000297 | nearest bacterial patch | - | - | Y | (2) `closestLawnID` [related] propose; own rdfs:comment "closestLawnID in analyzeWormLabTracks"; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/import_V2_decisions.md:268 |
| EMPTY:0000298 | value basis | - | - | Y | - |
| EMPTY:0000299 | target | - | - | Y | - |
| EMPTY:0000300 | brightfield imaging | - | - | Y | - |
| EMPTY:0000301 | video tracking | - | - | Y | - |
| EMPTY:0000302 | distance transform | - | - | Y | - |
| EMPTY:0000303 | encounter detection | - | - | Y | (2) `patch encounter detection` [(narrow)] do not add: V2-interim label, never released, generalised away by T19 decision; empty-ontology history (label at an earlier commit on V2); comment "Generalised 2026-10-20 (tenet T19) from ..." |
| EMPTY:0000304 | prediction from a fitted model | - | - | Y | - |
| EMPTY:0000305 | interpolation method | - | - | Y | - |
| EMPTY:0000306 | linear interpolation | - | - | Y | - |
| EMPTY:0000307 | maximum gap filled | - | - | Y | - |
| EMPTY:0000308 | bin width | - | - | Y | - |
| EMPTY:0000309 | video frame | - | - | Y | - |
| EMPTY:0000310 | image upper-left corner | - | - | Y | - |
| EMPTY:0000311 | image right | - | - | Y | - |
| EMPTY:0000312 | image down | - | - | Y | - |
| EMPTY:0000313 | dipotassium hydrogen phosphate trihydrate | K2HPO4 trihydrate [Exact] | - | Y | (1) ontology synonyms not in registry (registry has no synonym field) |
| EMPTY:0000314 | inclusion in analysis | - | - | Y | - |
| EMPTY:0000315 | directory of files | folder [Exact] | - | Y | (1) ontology synonyms not in registry (registry has no synonym field) |
| EMPTY:0000316 | Gaussian mixture model clustering | GMM clustering [Exact] | - | Y | (1) ontology synonyms not in registry (registry has no synonym field) |
| EMPTY:0000317 | quadratic discriminant analysis | QDA [Exact] | - | Y | (1) ontology synonyms not in registry (registry has no synonym field) |
| EMPTY:0000319 | acclimation plate | - | - | Y | - |
| EMPTY:0000320 | food deprivation plate | - | - | Y | - |
| EMPTY:0000321 | assay plate | - | - | Y | - |
| EMPTY:0000322 | relative cell density | - | - | Y | (2) `relative bacterial density` [related] optional (V2-interim label only); did-schema #88 schemas/V_eta_term_registry.json:1153 decided "renamed from \"relative bacterial density\" 2026-10-20"; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/import_V2_spec.json:1898 |
| EMPTY:0000323 | normalization reference value | - | - | Y | - |
| EMPTY:0000324 | lower limit of reported value | - | - | Y | - |
| EMPTY:0000325 | bacterial patch | - | - | Y | (3) `bacterial lawn` [related] propose; DID-matlab 9c9cab9 src/did/+did2/+convert/resolveLawnPlateSubjects.m:821 description 'bacterial lawn (a bacterial patch)'; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/import_V2_decisions.md:262 "a patch with bacteria culture (a lawn: ...)"; the lab names patches lawn* (lawnID, lawnVolume, lawnRadius, lawnSpacing in tableDoc_dictionary.json) |
| EMPTY:0000326 | arena | - | - | Y | - |
| EMPTY:0000327 | reference mark | - | - | Y | - |
| EMPTY:0000328 | encountered entity | - | - | Y | - |
| EMPTY:0000329 | potassium phosphate buffer | - | - | Y | - |
| EMPTY:0000330 | potassium citrate solution | - | - | Y | - |
| EMPTY:0000331 | seeding | - | - | Y | - |
| EMPTY:0000332 | pouring | - | - | Y | - |
| EMPTY:0000333 | incubation | - | - | Y | - |
| EMPTY:0000334 | refrigeration | - | - | Y | - |
| EMPTY:0000335 | ambient exposure | - | - | Y | - |
| EMPTY:0000336 | agar plug transfer | - | - | Y | - |
| EMPTY:0000337 | worm picking | - | - | Y | - |
| EMPTY:0000338 | eyelash picking | - | - | Y | - |
| EMPTY:0000339 | cleaning step | - | - | Y | - |
| EMPTY:0000340 | droplet | - | - | - | - |
| EMPTY:0000341 | patch exploitation encounter: minimum probability of exploitation | exploit: minimum probability of exploitation [Related] | - | Y | (1) ontology synonyms not in registry (registry has no synonym field) |
| EMPTY:0000342 | patch sampling encounter: minimum probability of sensing | sample: minimum probability of sensing [Related] | - | Y | (1) ontology synonyms not in registry (registry has no synonym field) |
| EMPTY:0000343 | off-patch search encounter: probability of sensing below | search off patch: probability of sensing below [Related] | - | Y | (1) ontology synonyms not in registry (registry has no synonym field) |
| EMPTY:0000344 | off-patch search encounter: maximum distance into the patch | search off patch: maximum distance into the patch [Related] | - | Y | (1) ontology synonyms not in registry (registry has no synonym field) |
| EMPTY:0000345 | publication date | - | - | Y | - |
| EMPTY:0000346 | release date | - | - | Y | - |
| EMPTY:0000347 | genetic strain type | - | - | Y | - |
| EMPTY:0000348 | oblique illumination imaging | - | - | Y | - |
| EMPTY:0000349 | peak amplitude | - | - | Y | - |
| EMPTY:0000351 | target bacteria growth duration after seeding | growth condition [Related] | - | Y | (1) ontology synonyms not in registry (registry has no synonym field) |
| EMPTY:0000352 | anterior end point | head [Related] | - | Y | (1) ontology synonyms not in registry (registry has no synonym field) |
| EMPTY:0000353 | posterior end point | tail [Related] | - | Y | (1) ontology synonyms not in registry (registry has no synonym field) |
| EMPTY:0000354 | material type | - | - | Y | - |
| EMPTY:0000356 | experimental approach | - | - | Y | - |
| EMPTY:0000357 | culture type | - | - | Y | - |
| EMPTY:0000358 | optogenetic tetanus stimulation | - | - | Y | (3) `tetanic light stimulation` [exact] propose (Dabrowska: may fall under #127 deferral); own rdfs:comment "The method of the tetanic light stimulation (TLS) in the Dabrowska slice recordings"; EMPTY_0000074 definition "tetanic light stimulation (TLS)"<br>(3) `TLS` [exact (abbreviation)] propose (Dabrowska: may fall under #127 deferral); same two sources |
| EMPTY:0000359 | ethics jurisdiction | - | - | Y | - |
| EMPTY:0000360 | chemogenetics | - | - | Y | - |
| EMPTY:0000361 | genetics | - | - | Y | - |
| EMPTY:0000362 | informatics | - | - | Y | - |
| EMPTY:0000363 | optogenetics | - | - | Y | - |
| EMPTY:0000364 | pathology | - | - | Y | - |
| EMPTY:0000365 | number of organisms per arena | - | - | Y | - |
| EMPTY:0000366 | flashed bar | - | - | Y | - |
| EMPTY:0000367 | NDI binary format | - | - | Y | - |
| EMPTY:0000368 | onset time | - | - | Y | (4) `C. elegans behavioral assay: encounter onset time` [(narrow)] do not add: encounter is a covariate position, not part of the term ([onset and offset terms]); hasRelatedSynonym on EMPTY_0000140 at origin/V2, dropped in f6b93d8; 0000140 comment<br>(2) `timeEnter` [(narrow)] do not add: encounter-specific v1 column; v1 column of obsolete EMPTY_0000140: NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:43 |
| EMPTY:0000369 | offset time | - | - | Y | - |
| EMPTY:0000370 | analog input channel | ai [Exact] | - | - | - |
| EMPTY:0000371 | analog output channel | ao [Exact] | - | - | - |
| EMPTY:0000372 | digital input channel | di [Exact] | - | - | - |
| EMPTY:0000373 | digital output channel | do [Exact] | - | - | - |
| EMPTY:0000374 | time channel | t [Exact] | - | - | - |
| EMPTY:0000375 | auxiliary input channel | ax [Exact] | - | - | - |
| EMPTY:0000376 | event channel | e [Exact] | - | - | - |
| EMPTY:0000377 | marker channel | mk [Exact] | - | - | - |
| EMPTY:0000378 | follows protocol | - | - | - | - |
| EMPTY:0000379 | distributed as | - | - | - | - |
| EMPTY:0000380 | paired with | - | - | - | - |
| EMPTY:0000381 | gene alias mapping | - | - | - | - |
| EMPTY:0000382 | instance of | - | - | - | - |
| EMPTY:0000383 | recording epoch | - | - | - | - |
| EMPTY:0000384 | signed distance to region boundary | - | - | - | (4) `distanceLawnEdge` [(narrow)] do not add: names the lawn/patch, which [O3] moved into a condition; provenance already in rdfs:comment; own rdfs:comment "As distanceLawnEdge in analyzeWormLabTracks"; NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/trackDocuments.m:231 column(W, 'distanceLawnEdge'); was hasRelatedSynonym on EMPTY_0000350 at origin/V2<br>(4) `distance from the patch edge` [(narrow)] do not add: same reason; hasRelatedSynonym on EMPTY_0000350 at empty-ontology origin/V2, dropped in 845a505 |
| EMPTY:0000385 | seeding volume | - | - | - | (2) `lawnVolume` [(narrow)] do not add as synonym; consider noting it in rdfs:comment as 0000384 does; v1 column of obsolete EMPTY_0000120: NDI-matlab fcfd876 src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json:23 "lawnVolume": "EMPTY:bacterial patch volume"; 0000120 consider EMPTY:0000385 |
| EMPTY:0000386 | orthologous gene mapping | - | - | - | - |

## Obsolete terms named in the request

| id | label | synonyms at origin/V2 | synonyms now | replacement | does a dropped synonym belong on the replacement? |
|---|---|---|---|---|---|
| EMPTY:0000350 | obsolete signed distance from the nearest bacterial patch edge | distance from the patch edge [Related]; distanceLawnEdge [Related] | none | EMPTY:0000384 signed distance to region boundary | No. Both strings name the patch / lawn, which the decision ([O3 Haley terms general]) moved out of the term into a condition. 0000384's rdfs:comment already records "As distanceLawnEdge in analyzeWormLabTracks". If they are kept anywhere, keep them on 0000350 itself so a search for the old name lands on the obsolete term and its consider pointer. |
| EMPTY:0000122 | obsolete arena diameter | C. elegans behavioral assay: plate or arena diameter [Related] | none | PATO:0001334 diameter (external) | No. The replacement is not an EMPTY term, and the string is arena-specific while diameter is general. |
| EMPTY:0000140 | obsolete encounter onset time | C. elegans behavioral assay: encounter onset time [Related] | none | EMPTY:0000368 onset time | No. Encounter-specific; 0000140's comment says the encounter is the covariate position, not part of the term. |
| EMPTY:0000120 | obsolete bacterial patch volume | none (at every one of the 32 commits of empty-edit.owl on the branch) | none | EMPTY:0000385 seeding volume | Nothing dropped. Its v1 column `lawnVolume` is patch-specific; not a synonym of seeding volume. |
