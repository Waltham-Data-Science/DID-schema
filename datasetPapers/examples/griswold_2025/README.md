# Griswold 2025 — Worked Example

This directory is a **worked example** of what a full metadata + data description would look like for the Griswold & Van Hooser 2025 eLife paper (`elife-106513-v2.pdf`, DOI 10.7554/eLife.106513), using openMINDS for general-purpose metadata and NDI-native documents only for the things openMINDS does not cover.

## Why this example?

This is the "easy case" in the two-paper drill described in `datasetPapers/summaries/00_schema_design_synthesis.md`:

- Straightforward in-vivo electrophysiology in a vertebrate (ferret).
- Clean three-group design (control / EO1 / EO2).
- Data already deposited on NDI Cloud (DOI 10.63884/ndic.2025.28xb47y1).
- Per-animal mixed-effects analysis maps cleanly onto per-document `depends_on`.

The companion example at `datasetPapers/examples/bhar_2025/` will be the "hard case" — population subject, cyclic training, plate-as-substrate, exchange assay.

## How to read this directory

```
griswold_2025/
├── README.md         (this file)
├── QUERIES.md        5 worked queries with step-by-step resolution through the doc graph
├── FINDINGS.md       What was awkward, what's missing, what to fix before writing schemas
├── openminds/        Instance documents that would live as openMINDS instances (not NDI docs)
└── ndi/              NDI-native documents for the gaps openMINDS doesn't cover
```

All JSON instance documents use **fake but readable UUIDs** of the form `griswold-<category>-<n>-<hash>`. These are obviously not real UUIDs — the point is that a reader can trace references visually (e.g. `"subject_id": "griswold-subject-EO1-01"` appears verbatim in the doc for that subject).

All openMINDS references use string IRIs prefixed with `openminds:` for readability; real deployments would use resolvable URIs (e.g. `https://kg.ebrains.eu/api/instances/<uuid>`).

All field names match the actual schemas in the openMINDS repos (as of v3/v4-transition) and the existing NDI V_gamma schemas where relevant. Fields that are paradigm-specific and currently have no home are flagged in `FINDINGS.md`.

## Scope of this example

To keep the example readable, one subject (EO1-01) is fleshed out in full, and two others (Control-01, EO2-01) are skeletal. Where a paper would have 128 epoch documents per session, we show 2 representative ones per stimulus set.

| Subject | Detail level |
|---|---|
| `griswold-subject-EO1-01` | Full — states, all three protocol executions, recording, tuning curves for one unit, fits, analysis output |
| `griswold-subject-control-01` | Skeleton — subject + one terminal state + one session |
| `griswold-subject-EO2-01` | Skeleton — subject + one terminal state + one session |

For the fully detailed subject, one example single unit (`griswold-unit-001`) has complete orientation / direction / SF / TF / contrast tuning curves, fits (Movshon SF, Movshon TF, Naka-Rushton contrast), and derived indices (1−CV, 1−DCV, LPI, bandwidth).

## Document-type inventory

### openMINDS documents (stored at `openminds/`)

| File prefix | openMINDS type | Purpose |
|---|---|---|
| `01_project` | `core:Project` | The Van Hooser-lab premature-vision project |
| `02_dataset` / `03_dataset_version` | `core:Dataset` / `core:DatasetVersion` | The paper's data release |
| `04_05_person` | `core:Person` | Griswold, Van Hooser |
| `06_organization` | `core:Organization` | Brandeis University |
| `07_08_doi` | `core:DOI` | eLife DOI, NDI-Cloud DOI |
| `10_species` | `controlledTerms:Species` | Ferret (*Mustela putorius furo*) |
| `20..22_subject_group` | `core:SubjectGroup` | Control / EO1 / EO2 cohorts |
| `30_subject_EO1_01` | `core:Subject` | One ferret |
| `31..34_subject_state_EO1_01` | `core:SubjectState` | State transitions: P25 pre-open → P25 post-open → P28 post-exposure → P55 terminal |
| `35..38` | `core:Subject` / `core:SubjectState` | Other two subjects, skeletal |
| `40..43_protocol` | `core:Protocol` | Eye-opening / exposure / surgery / recording protocols |
| `44..46_protocol_execution` | `core:ProtocolExecution` | Per-subject executions |
| `50_electrode_array` | `ephys:ElectrodeArray` | Plexon S probe (32 ch, 50 µm spacing) |
| `51_electrode_array_usage` | `ephys:ElectrodeArrayUsage` | Time-bounded usage on EO1-01 |
| `60..62_stimulus` | `stimulation:Stimulus` | Example gratings from set 1 / set 2 and blank |
| `63..64_stimulation_activity` | `stimulation:StimulationActivity` | Per-session stimulus-block executions |
| `70_coordinate` | `sands:CoordinatePoint` + `sands:AnatomicalTargetPosition` | V1 monocular penetration location |
| `71_recording_activity` | `ephys:RecordingActivity` | The recording session as an Activity |
| `72_file` | `core:File` | Raw ephys file reference |

### NDI-native documents (stored at `ndi/`)

| File prefix | NDI classname | Purpose |
|---|---|---|
| `01..03_session` | `session` | Sample-aligned session wrapper with NDI `did_uid`s |
| `10..11_factor_design` | `factor_design` (proposed) | Factorial stimulus-parameter tables for set 1 and set 2 |
| `20_recording` | `recording` | Sample-aligned raw recording (channels, sampling rate, file pointer) |
| `30_spikesort_output` | `spikesort_output` (based on existing `sorting/SpikeInterfaceSortingOutputs`) | JRClust cluster assignments |
| `40..43_tuning` | `tuning_curve` (based on existing `stimulus/stimulus_tuningcurve`) | Per-unit tuning for each stimulus axis |
| `44..46_fit` | `fit_curve` (based on existing `data/fitcurve`) | Movshon and Naka-Rushton fits |
| `47_indices` | `analysis_output` | Derived indices (1−CV, 1−DCV, LPI, bandwidth) |
| `50..51_epoch` | `epoch` (based on existing `oneepoch` / `epochfiles_ingested`) | Per-trial sample-aligned windows |
| `60_mixed_effects` | `analysis_output` | Across-animal mixed-effects fit |

## Key observations you can already see from the file list

1. **openMINDS handles the "who/what/when" cleanly.** 27 documents under `openminds/` describe everything about the subjects, protocols, devices, stimuli, and institutional context.
2. **NDI-native is small and focused.** Only ~15 documents, each doing something openMINDS does not: sample alignment, spike sorting, factorial design, tuning curves, fits.
3. **`depends_on` spans both systems.** NDI `recording` depends on openMINDS `ephys:RecordingActivity`; NDI `epoch` depends on openMINDS `stimulation:StimulationActivity`; NDI `analysis_output` depends on openMINDS `core:SubjectGroupState`.

See `FINDINGS.md` for what is awkward and what is missing.
