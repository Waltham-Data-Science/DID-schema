# V_eta status board (GENERATED -- do not hand-edit)

Regenerate with `python3 tools/status_board.py`. CI runs `--check`.

State lives here. The plan documents under `schemas/` keep the RATIONALE
for each model; this board owns *how much is left and what exactly*.

## Where V_eta stands

| | count |
|---|---|
| target classes | 225 |
| settled (persist) | 144 |
| settled (retire) | 47 |
| **still open (`in_progress`)** | **34** |
| **`retire` with no migrator and no plan** | **12** |
| open **decision families** | **20** |
| &nbsp;&nbsp;DECIDED and signed off, awaiting build | 2 |
| &nbsp;&nbsp;decided in a walkthrough, **awaiting a signature** | 8 |
| &nbsp;&nbsp;**written up by Claude alone, unreviewed** | **2** |
| &nbsp;&nbsp;nobody has proposed anything yet | 8 |

The class count is not the work count. 34 open classes are 20 decisions, because most open classes move as a family.

**18 of those 20 are not settled**: 8 awaiting a signature on a decision already taken, 2 written up by Claude alone and unreviewed, 8 with nothing proposed. Only 2 are signed off.

## AWAITING A SIGNATURE -- decided with the team, not yet recorded

These were settled in walkthroughs. They are not built and do not render as
decided because no document carries the sign-off line yet. Nothing here needs
re-deciding -- it needs recording.

| family | classes | what was decided | document |
|---|---|---|---|
| **time_reference** | 8 | 8 classes collapse to absolute_reference + relative_reference | `V_eta_time_reference_model_plan.md` |
| **stimulus** | 1 | timed_sequence data_type + timed_sequence_manipulation leaf | `V_eta_stimulus_model_plan.md` |
| **ensemble** | 1 | group subject + epoch-scoped member_of edges + rebuildable cache | `V_eta_ensemble_plan.md` |
| **image / ngrid** | 1 | ngrid phases into sampled_body; image is a standalone data_type | `V_eta_image_model_plan.md` |
| **acquisition epoch** | 3 | acquisition_epoch keeps identity + extent; clocks/axes/storage/payload leave | `V_eta_acquisition_epoch_plan.md` |
| **daq configuration** | 3 | acquisition_system + metadata_reader keep ids; class names fold to software entities | `V_eta_daq_family_decisions.md` |
| **sync configuration** | 2 | PERSIST as infra, ids preserved; class names fold to software entities | `V_eta_infra_family_decisions.md` |
| **software** | 1 | app -> software entity + software_id edge + execution_environment (R1) | `V_eta_tenet_audit.md` |

- **time_reference**: `epoch_bounded_reference`, `epoch_relative_reference`, `event_bounded_reference`, `event_relative_reference`, `session_bounded_reference`, `session_relative_reference`, `time_reference`, `utc_reference`
- **stimulus**: `stimulus_presentation`
- **ensemble**: `ensemble`
- **image / ngrid**: `ngrid`
- **acquisition epoch**: `acquisition_epoch`, `epochfiles_ingested`, `epochid`
- **daq configuration**: `daqmetadatareader`, `daqreader`, `daqsystem`
- **sync configuration**: `syncgraph`, `syncrule`
- **software**: `app`

## WRITTEN UP BY CLAUDE ALONE -- nobody has checked the reasoning

Each has template evidence and a written rationale, and **none of it has been
reviewed**. Counted as open work.

To sign one off, add a line to its document:

```
TEAM-SIGN-OFF: <who/when> -- <what was decided>
```

Until that line exists the family shows here regardless of what
`tools/status_board.py` claims -- Claude cannot promote its own work.

| family | classes | proposal | written up in |
|---|---|---|---|
| **daq ingested payloads** | 3 | -> relative_reference / opaque_body / image model; no new class | `V_eta_daq_family_decisions.md` |
| **sync mapping** | 1 | clock_alignment PROPOSED (relation tier); the relative_reference fold is disproven | `V_eta_infra_family_decisions.md` |

- **daq ingested payloads**: `daqmetadatareader_epochdata_ingested`, `daqreader_epochdata_ingested`, `daqreader_image_epochdata_ingested`
- **sync mapping**: `syncrule_mapping`

## Nobody has proposed anything yet

| family | classes | the call to make |
|---|---|---|
| **dataseries_channel_map** | 1 | ABSENT on NDI origin/main -- needs a writer check before any disposition |
| **file navigation** | 2 | filenavigator DECIDED (-> file_navigator); `directory` absent on origin/main, needs a writer check |
| **spike processing parameters** | 4 | algorithm config for spike extraction/sorting; 3 of 4 carry their own filter |
| **stimulus parameters** | 2 | stimulus description; likely folds with the stimulus model but not yet decided |
| **stimulus response** | 4 | measured response to a stimulus -- observation tier, feeds the tuning fold |
| **subject measurement** | 1 | live v1 class parallel to `measurement`; four emitters; disposition unrecorded |
| **misc singletons** | 4 | four unrelated classes, each its own small call |
| **demo / mock** | 2 | test fixtures; decide whether they ship in the set |

- **dataseries_channel_map**: `dataseries_channel_map`
- **file navigation**: `directory`, `filenavigator`
- **spike processing parameters**: `sorting_parameters`, `spike_extraction_parameters`, `spike_extraction_parameters_modification`, `vmspikefilteringparameters`
- **stimulus parameters**: `stimulus_parameter`, `stimulus_parameter_table`
- **stimulus response**: `stimulus_response`, `stimulus_response_scalar`, `stimulus_response_scalar_parameters`, `stimulus_response_scalar_parameters_basic`
- **subject measurement**: `subjectmeasurement`
- **misc singletons**: `binaryseries_parameters`, `control_designation`, `interaction_purpose`, `projectvar`
- **demo / mock**: `demo_ndi`, `demo_ndi_mock`

## DECIDED by the team, awaiting build

The model is settled and recorded; the schema has not changed yet. Every
one of these re-targets migrators that are already written, which is why
migrator work before the target closes is rework.

| family | classes | decision | recorded in |
|---|---|---|---|
| **openMINDS** | 1 | strain -> entity + recursive background_strain_#; strain_id on term_assertion | `V_eta_openminds_family_record.md` |
| **frequency_filter** | 1 | referenced document (not entity); band edges; typed gain fields; no sample_rate | `V_eta_frequency_filter_model_plan.md` |

## v1 source side (from the coverage ledger)

| disposition | count |
|---|---|
| retire | 42 |
| consumed by migrator (no tombstone) | 28 |
| in_progress | 21 |
| persist | 4 |
| no V_eta home, no migrator -- UNVERIFIED | 4 |
| test/demo fixture (non-production) | 2 |
| dissolved → subject | 1 |

### `retire`, but nothing decided -- 12 rows

Marked `retire` with **no migrator and no recorded plan**: the documents
pass through untouched. `retire` reads as settled, so these do not appear
in the family counts above -- but they are open work. Several hold real
data (e.g. `spike_extraction_parameters` carries filter_type / filter_low /
filter_high / filter_order / filter_ripple).

- `openminds`
- `sorting_parameters`
- `spike_extraction_parameters`
- `spike_extraction_parameters_modification`
- `stimulus_parameter`
- `stimulus_parameter_table`
- `stimulus_response`
- `stimulus_response_scalar`
- `stimulus_response_scalar_parameters`
- `stimulus_response_scalar_parameters_basic`
- `subjectmeasurement`
- `vmspikefilteringparameters`

**UNVERIFIED** -- no V_eta home, no migrator, fate never established. These strand today:

- `generic_file`
- `imageCollection`
- `imageStack_parameters`
- `valid_interval`

