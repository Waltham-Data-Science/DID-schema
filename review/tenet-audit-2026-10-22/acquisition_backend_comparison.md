# Acquisition documents: migrated v1 rigs vs the Haley V2 import

Question (Jess Haley): *"Haley doesn't go through the daq reader during import but
other datasets do. Can you compare? Those backend schema types are the ones I'm
least sure about."*

Read-only investigation, 2026-10-22. Nothing was edited in any repository.

**Heads read**

| repo | ref | commit |
|---|---|---|
| did-schema | `claude/ecstatic-pascal-md91fw` (PR #88) | `701a5de` |
| DID-matlab | FETCH_HEAD of `claude/ecstatic-pascal-md91fw` (PR #218) | `6236cc1` |
| NDI-matlab | `claude/v2-object-layer` (PR #1021) | `584b4199` (equal to origin) |

**Caveat on all V2 JSON below.** No MATLAB was run. I put the V2 documents
together by reading the migrator and import code (`did2.build.document`'s output
shape: `document_class`, `depends_on [{name, document_id}]` including the
`session_id` edge, `base {id, creation_timestamp}`, then one block per class).
They show the shape and the edges. They are not captured output. Where an id is
fresh I write `<new>`.

---

## 0. The premise, checked against the corpora

The extracted v1 corpora are untrusted and were read with `python3 -I`. The
count of JSON files read comes first for each corpus; the `__MACOSX` resource
forks were skipped.

```
== 20211116: JSON files read=1220   unparseable=0
   daqmetadatareader 1, daqreader 3, daqsystem 3, filenavigator 3, syncgraph 1, syncrule 2
== B:        JSON files read=12917  unparseable=0
   daqmetadatareader 13, daqmetadatareader_epochdata_ingested 1242, daqreader 39,
   daqreader_mfdaq_epochdata_ingested 2484, daqsystem 39, epochfiles_ingested 2484,
   filenavigator 39, syncgraph 13, syncrule 26, syncrule_mapping 2484
== Dab:      JSON files read=27561  unparseable=0
   daqmetadatareader 13, daqmetadatareader_epochdata_ingested 1242, daqreader 39,
   daqreader_mfdaq_epochdata_ingested 4089, daqreader_ndr 1, daqsystem 40,
   epochfiles_ingested 4088, filenavigator 40, syncgraph 13, syncrule 26, syncrule_mapping 2484
== JH:       JSON files read=78688  unparseable=0
   (none of the daq family)
== PRED:     JSON files read=14     unparseable=0
   daqmetadatareader 1, daqreader_ndr 2, daqsystem 2, filenavigator 2, syncgraph 1, syncrule 1
== Soph:     JSON files read=101427 unparseable=0
   daqmetadatareader 32, daqmetadatareader_epochdata_ingested 175, daqreader 96,
   daqreader_mfdaq_epochdata_ingested 349, daqsystem 96, epochfiles_ingested 349,
   filenavigator 96, syncgraph 32, syncrule 64, syncrule_mapping 348
```

JH is the v1 Haley dataset. All 78,688 of its documents fall into 15 classes,
and none of them is a daq class:

```
ontologyTableRow 41095, openminds_subject 9032, ontologyLabel 7007, imageStack 7007,
element_epoch 4156, element 4156, position_metadata 2078, distance_metadata 2078,
subject 1656, subject_group 353, treatment 56, openminds 8, session 3,
session_in_a_dataset 2, dataset_remote 1
```

So in v1, Haley's data reached elements straight through `element_epoch` and
`imageStack`. The V2 import (`ndi.setup.conv.haley.sessionDocuments`) is the
first time Haley data has any acquisition documents at all, and it writes them
natively. Nothing is migrated.

What the v1 daq objects held across the corpora:

```
daqsystem.ndi_daqsystem_class           ndi.daq.system.mfdaq                (every corpus, every document)
filenavigator.ndi_filenavigator_class   ndi.file.navigator.epochdir (vhlab corpora), ndi.file.navigator (Dab 1),
                                        ndi.file.navigator.rhd_series (PRED 2)
daqreader.ndi_daqreader_class           ndi.daq.reader.mfdaq.intan / .cedspike2 /
                                        ndi.setup.daq.reader.mfdaq.stimulus.vhlabvisspike2
daqreader_ndr.ndr_reader_string         'intan' (PRED 2), 'dabrowska' (Dab 1)
daqmetadatareader                       NewStimStims, tab_separated_file_parameter 'stims.mat' (vhlab);
                                        RayoLabStims, '#_\d{6}_\d{6}\._epochprobemap\.txt\>' (PRED)
syncrule                                filematch {number_fullpath_matches} and
                                        filefind {daqsystem1, daqsystem2, number_fullpath_matches, syncfilename}
```

---

## 1. A real migrated rig: Soph, session `41269342fa7e70d0_40ddb201249e7d06`, the `vhintan` Intan system

### 1a. The v1 documents (copied verbatim from the corpus; `document_class` blocks trimmed)

```json
// daqsystem
{ "base": { "id": "41269342fa7f0372_40dcce432dc1a356",
            "session_id": "41269342fa7e70d0_40ddb201249e7d06",
            "name": "vhintan", "datestamp": "2025-05-08T15:44:31.244Z" },
  "daqsystem": { "ndi_daqsystem_class": "ndi.daq.system.mfdaq" },
  "depends_on": [ { "name": "filenavigator_id",     "value": "41269342fa7f0343_c0c746d863f7d029" },
                  { "name": "daqreader_id",         "value": "41269342fa7f035a_40d89144bf1aac26" },
                  { "name": "daqmetadatareader_id", "value": "" } ] }

// filenavigator
{ "base": { "id": "41269342fa7f0343_c0c746d863f7d029", "name": "", ... },
  "filenavigator": {
    "ndi_filenavigator_class": "ndi.file.navigator.epochdir",
    "fileparameters": "{ 'reference.txt', '.*\\.rhd\\>', 'vhintan_channelgrouping.txt', 'vhintan_intan2spike2time.txt' }",
    "epochprobemap_class": "ndi.setup.epoch.epochprobemap_daqsystem_vhlab",
    "epochprobemap_fileparameters": "{ 'vhintan_channelgrouping.txt' }" } }

// daqreader
{ "base": { "id": "41269342fa7f035a_40d89144bf1aac26", "name": "", ... },
  "daqreader": { "ndi_daqreader_class": "ndi.daq.reader.mfdaq.intan" } }

// syncrule (same session) -- names the two rigs by NAME
{ "base": { "id": "41269342fa7f307c_40bf6dfe548f3289", ... },
  "syncrule": { "ndi_syncrule_class": "ndi.time.syncrule.filefind",
    "parameters": { "number_fullpath_matches": 1, "syncfilename": "vhintan_intan2spike2time.txt",
                    "daqsystem1": "vhintan", "daqsystem2": "vhvis_spike2" } } }

// the metadata reader belongs to the sibling rig vhvis_spike2 (depends_on daqmetadatareader_id_1)
{ "base": { "id": "41269342fa7f2215_c0c166d3e69411f7", ... },
  "daqmetadatareader": { "ndi_daqmetadatareader_class": "ndi.daq.metadatareader.NewStimStims",
                         "tab_separated_file_parameter": "stims.mat" } }

// one ingested epoch, t00003, on vhintan
{ "base": { "id": "4126936a8c436c2c_40d108e48e054002", ... },
  "depends_on": { "name": "filenavigator_id", "value": "41269342fa7f0343_c0c746d863f7d029" },
  "epochfiles_ingested": { "epoch_id": "t00003",
    "files": [ "epochid://t00003", ".../t00003/reference.txt", ".../t00003_230126_163209.rhd",
               ".../vhintan_channelgrouping.txt", ".../vhintan_intan2spike2time.txt" ],
    "epochprobemap": "name\treference\ttype\tdevicestring\tsubjectstring\nrightcortex\t1\tn-trode\tvhintan:ai1-32\tferret_389.1638@vhlab.org\n" } }

// its clock extent (daqreader_mfdaq_epochdata_ingested 4126936a9cef7659_40de5561c622282c, epochid t00003)
"daqreader_epochdata_ingested": { "epochtable": { "epochclock": ["dev_local_time"], "t0_t1": [0, 574.84795] } }
```

### 1b. What the migrator emits (put together from the code; not executed)

Sources: `+migrators_j/daqsystem.m`, `daqreader.m`, `filenavigator.m`,
`daqmetadatareader.m` and `syncrule.m`, `private/jSoftware.m`, and the batch
passes `epochMint`, `resolveEpochProbemap` and `resolveClockAlignment`. Each
per-document migrator emits **its own `software` entity**: `jSoftware(implClass,
'', '', sessionId, datestamp)` is called once per source document. Merging
happens later, in NDI's `ndi.migrate.internal.softwareDedup`.

```json
// acquisition_system   (id PRESERVED; daqsystem.m: Id = preBody.base.id)
{ "document_class": { "class_name": "acquisition_system", "superclasses": [{"class_name":"base"}], "schema_version": "V_eta" },
  "base": { "id": "41269342fa7f0372_40dcce432dc1a356", "creation_timestamp": "2025-05-08T15:44:31.244Z" },
  "acquisition_system": { "name": "vhintan" },
  "depends_on": [ { "name": "software_id",           "document_id": "<new: software ndi.daq.system.mfdaq>" },
                  { "name": "reader_id",             "document_id": "41269342fa7f035a_40d89144bf1aac26" },
                  { "name": "epoch_file_pattern_id", "document_id": "41269342fa7f0343_c0c746d863f7d029" },
                  { "name": "session_id",            "document_id": "41269342fa7e70d0_40ddb201249e7d06" } ] }
   // no epoch_parameter_reader_id (v1 bare entry empty); NO device_id (never emitted)
   // vhvis_spike2's system gets epoch_parameter_reader_id -> 41269342fa7f2215_c0c166d3e69411f7

// acquisition_reader   (id PRESERVED = the v1 daqreader id)
{ "document_class": { "class_name": "acquisition_reader", ... },
  "base": { "id": "41269342fa7f035a_40d89144bf1aac26", ... },
  "acquisition_reader": { },                      // no reader_string: the v1 daqreader had none
  "depends_on": [ { "name": "software_id", "document_id": "<new: software ndi.daq.reader.mfdaq.intan>" },
                  { "name": "session_id", ... } ] }

// epoch_file_pattern   (id PRESERVED = the v1 filenavigator id; eval'd string PARSED by jFileMatchList)
{ "document_class": { "class_name": "epoch_file_pattern", ... },
  "base": { "id": "41269342fa7f0343_c0c746d863f7d029", ... },
  "epoch_file_pattern": {
     "file_pattern":      ["reference.txt", ".*\\.rhd\\>", "vhintan_channelgrouping.txt", "vhintan_intan2spike2time.txt"],
     "epoch_map_pattern": ["vhintan_channelgrouping.txt"],
     "epoch_map_format":  "ndi.setup.epoch.epochprobemap_daqsystem_vhlab" },
  "depends_on": [ { "name": "software_id", "document_id": "<new: software ndi.file.navigator.epochdir>" }, ... ] }

// epoch_parameter_reader (vhvis_spike2's; id PRESERVED)
{ "document_class": { "class_name": "epoch_parameter_reader", ... },
  "base": { "id": "41269342fa7f2215_c0c166d3e69411f7", ... },
  "epoch_parameter_reader": { "file_regex": "stims.mat" },
  "depends_on": [ { "name": "software_id", "document_id": "<new: software ndi.daq.metadatareader.NewStimStims>" }, ... ] }

// software x N  (one per source document, per jSoftware; entity of type software)
{ "document_class": { "class_name": "entity", ... },
  "base": { "id": "<new>", ... },
  "entity": { "type": {"node": "", "name": "software"}, "name": "ndi.daq.system.mfdaq",
              "local_identifier": "ndi.daq.system.mfdaq" },
  "depends_on": [ { "name": "session_id", ... } ] }
   // softwareDedup later merges on (scope, name, version); scope = the DATASET when one is migrated

// epoch (epochMint: one per (session, epoch string), so t00003 is ONE entity shared by vhintan AND vhvis_spike2)
{ "document_class": { "class_name": "entity", ... },
  "entity": { "type": {"node": "", "name": "epoch"}, "local_identifier": "t00003" },
  "depends_on": [ { "name": "session_id", ... } ] }          // no time_reference_id (mintEpoch says so)

// relative_time_reference from the epochtable (daqreader_epochdata_ingested.m -> jEpochClockReferences)
{ "document_class": { "class_name": "relative_time_reference", ... },
  "relative_time_reference": { "value": { "clock": "dev_local_time", "start": 0, "duration": 574.84795 } },
  "depends_on": [ { "name": "referent_id", "document_id": "<epoch t00003>" }, ... ] }

// acquisition_channels from the probemap row's devicestring "vhintan:ai1-32" (resolveEpochProbemap)
{ "document_class": { "class_name": "acquisition_channels", ... },
  "acquisition_channels": { "channels": [ { "type": {"node": "", "name": "ai"}, "numbers": [1, 2, ..., 32] } ] },
  "depends_on": [ { "name": "acquisition_system_id", "document_id": "41269342fa7f0372_40dcce432dc1a356" }, ... ] }

// the recording observation for that row (mkObservation): voltage observation, data_body true,
//   entity_id = the ferret, instrument_id = the 'rightcortex' probe, acquisition_channels_id -> the doc above,
//   time_reference_id -> a relative_time_reference "intervalDuring" the epoch. No `method`.
// + opaque_body per ingested file series (owner_id -> every observation of that epoch)
// + ingestion_manifest (id preserved from epochfiles_ingested):
{ "document_class": { "class_name": "ingestion_manifest", ... },
  "ingestion_manifest": { "files": [ "epochid://t00003", ".../t00003_230126_163209.rhd", ... ] },
  "depends_on": [ { "name": "epoch_file_pattern_id", "document_id": "41269342fa7f0343_c0c746d863f7d029" },
                  { "name": "epoch_id", "document_id": "<epoch t00003>" }, ... ] }   // the serialized epochprobemap is DROPPED

// the filefind syncrule (resolveClockAlignment stamps the two system ids, syncrule.m re-runs)
{ "document_class": { "class_name": "clock_alignment_configuration", ... },
  "base": { "id": "41269342fa7f307c_40bf6dfe548f3289", ... },
  "clock_alignment_configuration": { "method": { "parameters": [ "minimum matching file paths = 1",
                                                                  "sync file name = vhintan_intan2spike2time.txt" ] } },
  "depends_on": [ { "name": "software_id", "document_id": "<new: software ndi.time.syncrule.filefind>" },
                  { "name": "acquisition_channels_id", "document_id": "<new A>" },
                  { "name": "acquisition_channels_id", "document_id": "<new B>" }, ... ] }
// + 2 acquisition_channels with NO `channels`, each only an acquisition_system_id edge (vhintan, vhvis_spike2)
```

---

## 2. The Haley import, camera1 (`sessionDocuments.m` lines 145-174, then the recording loop)

These are written natively. There is no v1 source, so every id is new. Once per
session, if the session has any recording:

```json
// three software entities, ONE SET PER SESSION, shared by every system in it (decision #29)
{ "entity": { "type": {"node": "", "name": "software"}, "name": "ndi.daq.system.image" } }      // sw.system
{ "entity": { "type": {"node": "", "name": "software"}, "name": "ndi.file.navigator.bodies" } }  // sw.navigator
{ "entity": { "type": {"node": "", "name": "software"}, "name": "ndi.daq.reader.image.ndr" } }  // sw.reader
   // no local_identifier (ndi.setup.V2.entityDocuments sets only what is given)

// acquisition_reader: one per reader STRING per session (camera1 and camera2 share it)
{ "document_class": { "class_name": "acquisition_reader", ... },
  "acquisition_reader": { "reader_string": "video" },
  "depends_on": [ { "name": "software_id", "document_id": "<sw.reader>" }, { "name": "session_id", ... } ] }

// epoch_file_pattern: one per system
{ "document_class": { "class_name": "epoch_file_pattern", ... },
  "epoch_file_pattern": { "file_pattern": [".*_1\\.mp4\\>"],
                          "epoch_map_format": "ndi.epoch.epochprobemap_daqsystem" },   // no epoch_map_pattern
  "depends_on": [ { "name": "software_id", "document_id": "<sw.navigator>" }, ... ] }

// acquisition_system
{ "document_class": { "class_name": "acquisition_system", ... },
  "acquisition_system": { "name": "camera1" },
  "depends_on": [ { "name": "software_id",           "document_id": "<sw.system>" },
                  { "name": "reader_id",             "document_id": "<acquisition_reader 'video'>" },
                  { "name": "epoch_file_pattern_id", "document_id": "<epoch_file_pattern above>" },
                  { "name": "session_id", ... } ] }        // NO device_id, NO epoch_parameter_reader_id

// acquisition_channels: one per system, EMPTY (decision #49 (3): cameras have no ai/ao/di/do)
{ "document_class": { "class_name": "acquisition_channels", ... },
  "acquisition_channels": { },
  "depends_on": [ { "name": "acquisition_system_id", "document_id": "<acquisition_system camera1>" }, ... ] }
```

For each recording (one file, one epoch):

```json
// epoch: entity of type epoch, local_identifier = the file stem (e.g. concentration_2022-02-04_12-10-51_1)
{ "entity": { "type": {"node": "", "name": "epoch"}, "local_identifier": "concentration_2022-02-04_12-10-51_1" },
  "depends_on": [ { "name": "time_reference_id", "document_id": "<absolute UTC start+duration>" },
                  { "name": "time_reference_id", "document_id": "<relative: dev_local_time 0..dur, referent = SESSION>" }, ... ] }

// relEpoch: relative_time_reference, clock dev_local_time, start 0, duration = video length, referent = the epoch
// absRef:   absolute_time_reference, UTC start, source value + America/Los_Angeles

// the recording statement (line 228)
{ "document_class": { "class_name": "observation", "superclasses": [..., "intensity"] },
  "interaction": { "method": { "term": "brightfield imaging (EMPTY:0000300)" } },
  "statement": { "variable": "Imaging Signal Intensity (NCIT:C221750)", "data_body": true, "datum_type": "uint8", ... },
  "depends_on": [ { "name": "entity_id",               "document_id": "<plate subject>" },
                  { "name": "instrument_id",           "document_id": "<dataset-level camera_1 entity>" },
                  { "name": "acquisition_channels_id", "document_id": "<camera1's empty acquisition_channels>" },
                  { "name": "time_reference_id",       "document_id": "<relEpoch>" },
                  { "name": "time_reference_id",       "document_id": "<absRef>" }, ... ] }

// opaque_body: the .mp4 by location (not ingested), owner_id -> the statement
```

There is no syncrule or clock-alignment document, no `acquisition_epoch`, no
`ingestion_manifest`, and no `epoch_parameter_reader`. Each recording's time is
fixed against UTC by its own `absolute_time_reference`.

**How NDI reads it back.** `session.daqsystem_load` finds the system through
`ndi.vintage.isaQuery('daqsystem')`, an OR that includes `acquisition_system`.
`ndi.daq.system`'s constructor follows `reader_id` and `epoch_file_pattern_id`
(via `ndi.vintage.edge`). It builds each object from the `software` entity's
`name` (`ndi.vintage.objectClass`). For Haley that gives `ndi.daq.system.image`,
`ndi.daq.reader.image.ndr` (the reader string comes from
`acquisition_reader.reader_string` via `ndi.vintage.field`) and
`ndi.file.navigator.bodies`. `bodies.readRecordings` then walks

```
acquisition_system (depends_on epoch_file_pattern_id = me)
  <- acquisition_channels (acquisition_system_id)
     <- statement (acquisition_channels_id)
        <- data_body (owner_id)          files = body locations; epoch id = epoch.local_identifier
                                         via the statement's relative time reference;
                                         probe map = (system name, 1, method->probe type, '<sys>:image1', subject)
```

**This is why Haley's empty `acquisition_channels` is load-bearing.** It is the
only link from a statement back to its system.

---

## 3. Side by side

| Aspect | Migrated v1 rig (Soph `vhintan`) | Haley camera1 | Agree? / why |
|---|---|---|---|
| Source | v1 `daqsystem` + `filenavigator` + `daqreader` (+ `daqmetadatareader`), all 1:1 per rig per session | none (JH v1 has 0 daq docs); built from the recording table | Haley is native, not migrated |
| `acquisition_system` superclass | `base` | `base` | agree (schema: `superclasses ['base']`) |
| `acquisition_system.name` | `vhintan` (v1 `base.name`, the join key) | `camera1` | agree; both are found by name |
| `acquisition_system` base.id | **preserved** v1 id | new | expected |
| `software_id` (the system class) | `ndi.daq.system.mfdaq`, a new software entity per document | `ndi.daq.system.image`, one per session | the class differs, as it should (mfdaq vs image) |
| `reader_id` -> `acquisition_reader` | 1 per v1 daqreader, id preserved, **no `reader_string`** (vhlab readers have none; PRED/Dab ndr have `intan`/`dabrowska`) | 1 per reader string per session, shared by camera1 and camera2, `reader_string: video` | shapes agree; Haley shares a reader, migrated does not |
| `epoch_file_pattern_id` | id preserved; `file_pattern` = literal names + regex, **no `#`** in vhlab; `epoch_map_pattern` and `epoch_map_format` set from v1 | new; `file_pattern ['.*_1\.mp4\>']` (regex); `epoch_map_format` set, `epoch_map_pattern` absent | fields agree; the meaning of `file_pattern` depends on the navigator class |
| navigator software | `ndi.file.navigator.epochdir` (scans a folder, reads `epochfiles_ingested`) | `ndi.file.navigator.bodies` (walks V2 documents) | **differs, and this decides whether NDI can read the data** (P1) |
| `epoch_parameter_reader_id` | where v1 had one (vhvis_spike2, PRED rayo_stim): `file_regex` from `tab_separated_file_parameter` | never | Haley has no stimulus parameter file |
| `device_id` | never emitted (v1 holds no hardware facts) | never emitted, **although the camera entity exists** | both hollow (P4) |
| software entity scope | per source document, then deduplicated to the **dataset** level when a dataset is migrated (softwareDedup, Jess 2026-10-21) | **per session** (decision #29: "a session opened alone has no link to its dataset") | **disagree** (P3) |
| software `local_identifier` | = name (jSoftware) | absent | minor; dedup keys on name |
| `acquisition_channels` | from probemap devicestring, `channels [{ai,[1..32]}]`, one per (session, rig, channel set); **none** for mk/e/md rows; plus 2 **empty** ones per filefind syncrule | one per system, **empty** | three different uses of one class (P2, P5) |
| statement -> rig | `acquisition_channels_id` (when the channel types bind) | `acquisition_channels_id` (always) | same chain, so the two paths converged |
| instrument | `instrument_id` = the probe (element entity) | `instrument_id` = dataset-level camera entity | agree in kind (T7) |
| statement `method` | none on recording observations | imaging method term (needed: bodies maps node -> probe type) | differs; bodies errors without one |
| epoch entity | one per (session, epoch string), **shared across rigs** (t00003 on vhintan and vhvis_spike2); no `time_reference_id` | one per recording file; `time_reference_id` -> UTC + session-relative | differ in granularity and direction |
| epoch clock extent | `relative_time_reference {dev_local_time, 0, dur}` referent = epoch (from the epochtable) | `relEpoch {dev_local_time, 0, dur}` referent = epoch | **agree exactly** |
| absolute time | via syncrule/clock_alignment to other rigs, no UTC | `absolute_time_reference` per recording | differ (one camera per epoch needs no alignment) |
| clock alignment | filefind -> `clock_alignment_configuration` + 2 empty `acquisition_channels`; filematch -> config with no channels; syncgraph -> `clock_alignment_policy`; syncrule_mapping -> `clock_alignment` | none | Haley has nothing to align |
| ingestion record | `epochfiles_ingested` -> `ingestion_manifest` (epoch_file_pattern_id + epoch_id; probemap dropped) | none (bodies by location) | Haley never ingested |
| `epoch` -> system edge | none | none (decision #33) | agree, but both contradict signed §8 `recorded_by` (P4) |

---

## 4. Problems, by severity

### P1 (high). A migrated ingested rig's epochs cannot be found through its own navigator in NDI V2 (from reading the code; not executed)

The migrated system names `ndi.file.navigator.epochdir`, so NDI builds the
classic navigator. That navigator finds ingested epochs with a raw query:

```
NDI +ndi/+file/navigator.m:514-516
    epoch_query = ndi.query('','isa','epochfiles_ingested') & ...
        ndi.query('','depends_on','filenavigator_id',ndi_filenavigator_obj.id()) & ...
        ndi.query('base.session_id','exact_string',ndi_filenavigator_obj.session.id());
```

Migration renames that document to `ingestion_manifest`, with an
`epoch_file_pattern_id` edge and no `epochprobemap`:

```
DID-matlab resolveEpochProbemap.m mkIngestionManifest:
    % epoch_id edge. No serialized epochprobemap (#73 review item 39)
    m = did2.build.document('ingestion_manifest', struct('files', ...),
        'Edges', struct('epoch_file_pattern_id', ..., 'epoch_id', ...)
```

Nothing bridges the query: `grep -c vintage query.m` prints `0`. `isaQuery.m`
says why `isa` cannot bridge a rename: *"`isa` walks the class chain, and V_eta
does not put the v1 name in it"*. `ndi.vintage.map` has rows for daqsystem,
filenavigator, daqmetadatareader, daqreader, syncgraph, syncrule and element,
and none for `epochfiles_ingested`.

The affected documents are B 2,484, Dab 4,088 and Soph 349 `epochfiles_ingested`.
After migration their epochs are reachable only on disk, and the corpora (and
cloud datasets) have no files on disk. The migrated documents do now carry the
same `system <- channels <- statement <- opaque_body` chain that `bodies` walks,
but the system's software still says `epochdir`, and `bodies` is image-only (its
probe map is `<sys>:image1`, and it errors with `NDI:navigator:bodies:noMethod`
on a statement with no `method`, which migrated recording observations lack).

The file header also contradicts itself. `resolveEpochProbemap.m` line 18 says
the probemap is *"KEPT VERBATIM for lossless read-back"*, while
`mkIngestionManifest` drops it. Related open caveat in CLAUDE.md §6: `+daq/reader.m`
reads `epochid.epochid` on ingested epochs.

### P2 (high). The `acquisition_channels.channels.type` binding drops most stimulus wiring

The schema binds `type` REQUIRED to `ai | ao | di | do` ("daqsystemstring.m:53-56").
NDI's own `ndi.daq.system.mfdaq` (origin/main, header) also lists `'time' or 't'`,
`'auxiliary_in','aux' or 'ax'`, `'event', or 'e'` and `'mark', or 'mk'`.

Probemap census (denominator: `epochfiles_ingested` documents, then probemap rows):

```
B    2484 docs, 9936 rows:  groups ai 1242, mk 3726, e 3726, md 1242  (vhvis_spike2 8694 rows)
Dab  4088 docs, 14748 rows: ai 4450, ao 1604, mk 3726, e 3726, md 1242
Soph  349 docs, 1399 rows:  ai 174, mk 525, e 525, md 175
```

Every vhvis_spike2 stimulator row is one mk, e or md group. That is 8,694 of
9,936 rows in B, 8,694 of 14,748 in Dab and 1,225 of 1,399 in Soph. For these
rows `resolveEpochProbemap` resolves the rig (`acqSystemId`), then refuses to
mint the channels document (`channelsBindable` -> `channels_unbindable_type`).
`acId` therefore stays `''`, and the manipulation carries **no
`acquisition_channels_id` at all**. The rig link is lost even though it was
resolved.

Haley avoids the problem by writing no channels (decision #49 (3), "the schema
binds only ai/ao/di/do"). `md` appears in the data but not in mfdaq's documented
list, so it needs a writer check.

### P3 (medium). Where the software entities live: the two paths decided opposite things

Haley decision #29: the NDI-class software *"live in each session: `daqsystem_load`
rebuilds objects from the session's own database ... a session opened alone has
no link to its dataset."*

`softwareDedup.m` decides the opposite for migrated data:

```
%   THE SCOPE IS THE DATASET WHEN A DATASET IS MIGRATED ... every software entity
%   ... is then stored at the dataset level -- its `session_id` names the dataset entity
```

`objectClass.m` falls back to `database_search_with_dataset`, and that
function's own documentation says *"A session opened from its own folder on its
own holds only its own documents, so the answer is the same as
DATABASE_SEARCH's"*. A migrated session opened alone should therefore hit
`NDI:vintage:softwareNotFound` on every `acquisition_system`, reader, navigator,
metadata reader and syncrule. I have not executed this. There are two options:
exempt object-reconstruction software from dataset-level dedup, or reverse #29.

### P4 (medium). The signed §8 (`device_id`, epochs `recorded_by` the system) is emitted by neither writer and cannot validate as declared

`V_eta_entity_composition_plan.md` §8:
*"TEAM-SIGN-OFF: jess / 2026-10-08 -- acquisition_system is configuration off base,
with an optional device_id; epochs are recorded_by it"*.

- `grep -rn device_id` over 347 DID-matlab and 1,151 NDI-matlab `.m` files finds
  0 hits. A case-insensitive `recorded_?by` search finds 0 hits.
- `recorded_by` is registered (binding_registry: `child_types [epoch]`,
  `parent_types [acquisition_system]`). But `directed_relation.parent_id` has
  `must_refer_to_document_class` `entity,statement,value`, and
  `acquisition_system`'s superclasses are `['base']`. So the declared relation
  cannot point where the binding says it should.
- Haley decision #33 says *"an epoch needs no edge to its system"*, which
  conflicts with the signed "epochs are recorded_by it". Haley has the camera
  (`camera_1`, product `camera`) in hand and could fill `device_id`. It puts the
  camera on every statement as `instrument_id` instead.

### P5 (medium). `acquisition_channels` means three different things

1. **Haley:** an empty junction, system <- statement, needed by `bodies`.
2. **Migrated filefind syncrule:** two empty documents, each only
   `acquisition_system_id` (syncrule.m: `did2.build.document('acquisition_channels',
   struct(), ...)`).
3. **Migrated probemap:** real channel groups.

The schema describes only the third (*"One entry per channel-TYPE GROUP"*), and
its edge note is stale: *"kept OPTIONAL until the minting pass lands, because
nothing fills it today"*. All three emitters fill the edge now. If the edge is
the point, a direct `acquisition_system_id` on the statement would carry it
without a contentless document. That is a team question.

### P6 (medium). Schema documentation on pattern syntax is contradicted by both writers' data

- `epoch_file_pattern.file_pattern` says *"SYNTAX: NDI's #-stem pattern syntax,
  not a plain regular expression"*. In the data, vhlab `fileparameters` hold
  literal names plus regexes and no `#` (`'reference.txt', '.*\.rhd\>'`). Haley's
  `'.*_1\.mp4\>'` is a plain regex, applied by `regexp(name, pattern)` in
  `bodies.m`.
- `epoch_parameter_reader.file_regex` says *"A REGULAR EXPRESSION ... Named apart
  from ... `file_pattern`, which uses NDI's #-stem syntax"*. PRED's value is
  `'#_\d{6}_\d{6}\._epochprobemap\.txt\>'` (it has a `#`), and the vhlab value is
  `'stims.mat'`.

Neither field has a syntax of its own. The syntax is whatever the class behind
`software_id` does (a regex, with `#` substituted for the epoch stem by
`ndi.file.navigator`). The two names imply a distinction the data does not have.

### P7 (low). Schema and NDI let through a system that NDI cannot load

The schema marks `reader_id` and `epoch_file_pattern_id` optional, while
`ndi.daq.system` errors without them (`error(['Could not find daqreader document
with id ' ...])`). Both writers fill them today: Haley always, and the migrator
whenever v1 had them (v1 `"mustbenotempty": 1`). The `acquisition_system` class
documentation does not say they are required in practice.

### P8 (low). Stale prose

- `V_eta_daq_family_decisions.md` still presents `acquisition_system ⊂ entity`
  and `acquisition_metadata_reader_#` as the model, with no pointer to the
  superseding §8 (2026-10-08) or the item-65 rename.
- The same stale description is repeated in the `+migrators_j/daqsystem.m` header
  (*"acquisition_system <- entity ... acquisition_metadata_reader_#"*), in
  `ndi.vintage.map` (*"deps = ... acquisition_metadata_reader_#"*) and in
  `ndi.vintage.isaQuery` (*"`acquisition_system`'s is [entity]"*). The code
  itself emits and reads `epoch_parameter_reader_id`.
- `private/jAcquisitionChannels.m` still hand-builds a body with `base.name`,
  which `did2.build.document` refuses (*"the did_v1-only `base.name` is refused"*).
  `syncrule.m` now only uses its result to decide `haveBoth` / `haveNeither`, so
  this is dead output in a stale shape.

### P9 (low). Hollow or decorative fields

- Haley's `epoch_map_format: 'ndi.epoch.epochprobemap_daqsystem'` has no map
  file or pattern; `bodies` builds the probe map itself. It equals the
  navigator's default, so it is harmless.
- Migrated vhlab `acquisition_reader` documents carry no `reader_string`, which
  leaves a document whose only content is a `software_id` edge. Haley's carries
  `video`.
- Haley's software entities have no `local_identifier`. Dedup keys on name, so
  this is harmless.

### Not measured

- No corpus run of PR #88's shape was available here (CLAUDE.md §6), so the
  emission shapes above come from reading code, not from counts.
- Whether `readtimeseries` works on either path was not tested.
- How Haley's per-recording `absolute_time_reference` interacts with NDI's
  syncgraph (with no syncrule documents present) was not checked.
