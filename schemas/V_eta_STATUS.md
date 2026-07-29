# V_eta status board (GENERATED -- do not hand-edit)

Regenerate with `python3 tools/status_board.py`. CI runs `--check`.

State lives here. The plan documents under `schemas/` keep the RATIONALE
for each model; this board owns *how much is left and what exactly*.

## Where V_eta stands

| | count |
|---|---|
| target classes | 222 |
| settled (persist) | 140 |
| settled (retire) | 47 |
| **still open** | **35** |
| open **decision families** | **15** |
| &nbsp;&nbsp;of which decided, awaiting build | 9 |
| &nbsp;&nbsp;of which genuinely undecided | 6 |

The class count is not the work count. 35 open classes are 15 decisions, because most open classes move as a family.

## Genuinely undecided -- this is what closing V_eta means

| family | classes | the call to make |
|---|---|---|
| **acquisition epoch** | 3 | epoch header contents + whether clocks dissolve into time_references |
| **dataseries_channel_map** | 1 | ABSENT on NDI origin/main -- needs a writer check before any disposition |
| **openMINDS** | 1 | import provenance vs crosswalk; entangled with the openminds_* sources |
| **software / method** | 2 | dedup + crosswalk after the app rename; filter is algorithm+parameters |
| **misc singletons** | 4 | four unrelated classes, each its own small call |
| **demo / mock** | 2 | test fixtures; decide whether they ship in the set |

- **acquisition epoch**: `acquisition_epoch`, `epochfiles_ingested`, `epochid`
- **dataseries_channel_map**: `dataseries_channel_map`
- **openMINDS**: `openminds_import`
- **software / method**: `app`, `filter`
- **misc singletons**: `binaryseries_parameters`, `control_designation`, `interaction_purpose`, `projectvar`
- **demo / mock**: `demo_ndi`, `demo_ndi_mock`

## Decided, awaiting build

The model is settled and recorded; the schema has not changed yet. Every
one of these re-targets migrators that are already written, which is why
migrator work before the target closes is rework.

| family | classes | decision | recorded in |
|---|---|---|---|
| **time_reference** | 8 | 8 classes collapse to absolute_reference + relative_reference | `V_eta_time_reference_model_plan.md` |
| **stimulus** | 1 | timed_sequence data_type + timed_sequence_manipulation leaf | `V_eta_stimulus_model_plan.md` |
| **ensemble** | 1 | group subject + epoch-scoped member_of edges + rebuildable cache | `V_eta_ensemble_plan.md` |
| **image / ngrid** | 1 | ngrid phases into sampled_body; image is a standalone data_type | `V_eta_image_model_plan.md` |
| **daq configuration** | 3 | ndi_<x>_class + params -- runtime config, not archival | `V_eta_daq_family_decisions.md` |
| **daq ingested payloads** | 3 | -> relative_reference / opaque_body / image model; no new class | `V_eta_daq_family_decisions.md` |
| **sync configuration** | 2 | runtime config (ndi_<x>_class + parameters), not archival | `V_eta_infra_family_decisions.md` |
| **sync mapping** | 1 | folds into relative_reference -- it IS an epoch-to-epoch time relation | `V_eta_infra_family_decisions.md` |
| **file navigation** | 2 | runtime, machine-specific paths; not archival | `V_eta_infra_family_decisions.md` |

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

**UNVERIFIED** -- no V_eta home, no migrator, fate never established. These strand today:

- `generic_file`
- `imageCollection`
- `imageStack_parameters`
- `valid_interval`

