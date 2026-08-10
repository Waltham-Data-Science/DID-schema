# V_eta status board (GENERATED -- do not hand-edit)

Regenerate with `python3 tools/status_board.py`. CI runs `--check`.

State lives here. The plan documents under `schemas/` keep the RATIONALE
for each model; this board owns *how much is left and what exactly*.

## Where V_eta stands

| | count |
|---|---|
| target classes | 243 |
| settled (persist) | 162 |
| settled (retire) | 50 |
| **still open (`in_progress`)** | **31** |
| **`retire` with no migrator YET** | **0** |
| open **decision families** | **18** |
| &nbsp;&nbsp;DECIDED and signed off, awaiting build | 18 |
| &nbsp;&nbsp;decided in a walkthrough, **awaiting a signature** | 0 |
| &nbsp;&nbsp;**written up by Claude alone, unreviewed** | **0** |
| &nbsp;&nbsp;nobody has proposed anything yet | 0 |

| open-class BUILD/PROOF state (derived, see below) | count |
|---|---|
| (a) decided, nothing built | 14 |
| (b) built, awaiting corpus proof | 17 |
| (c) corpus: 0 survivors in the corpora read | 0 |
| (?) UNMEASURED -- no build evidence was ever taken | 0 |

The class count is not the work count. 31 open classes are 18 decisions, because most open classes move as a family.

**0 of those 18 are not settled**: 0 awaiting a signature on a decision already taken, 0 written up by Claude alone and unreviewed, 0 with nothing proposed. Only 18 are signed off.

## What is actually left on the 31 open classes

`in_progress` is a HAND-WRITTEN DECLARATION: every one of these classes is
open because its name is a literal in `_DECIDED_PENDING` / `_IN_PROGRESS` in
`tools/build_v_eta.py`, and it leaves the list only when a person deletes
that line. Nothing about a landed migrator, a passing test or a green corpus
moves it. The table below does not change that membership -- only the team
decides a disposition -- it DERIVES, per class, how far the work has got.

### The measurement and its denominator

| evidence source | reach |
|---|---|
| build: V_eta migrator packages read | `migrators_j`, `ndi_second_pass` |
| build: migrator files inspected | 132 |
| build: migrator lines inspected | 16901 |
| build: classes queried | 31 |
| corpus: `*-summary.json` reports read | 0 |
| corpus: reports carrying an `unconverted_count` | 0 |
| corpus: documents behind those reports | 0 |
| corpus: corpora named | **NONE** |

**NO CORPUS SURVIVOR DATA.** 0 report(s) were read and 0 of them carry
an `unconverted_count`, so **state (c) cannot be reached by any class in**
**this run** and none is rendered as corpus-proven. A report without that
key measured nothing; its silence is not a zero. Point `--census` at a
directory of corpus reports, or run the DID-matlab corpus gate.

### Where the 31 open classes sit

| state | classes |
|---|---|
| (a) decided, nothing built | 14 |
| (b) built, awaiting corpus proof | 17 |
| (c) corpus: 0 survivors in the corpora read | 0 |
| (?) UNMEASURED -- no build evidence was ever taken | 0 |

**(c) IS EVIDENCE, NOT A DISPOSITION.** 0 survivors is a fact about the
corpora that were read, and it may not be promoted to `retire` on its own:
the corpora are a SAMPLE of datasets, not the universe, and the reports carry
no per-class SOURCE denominator -- `by_class` counts OUTPUT names, so a class
fully consumed and a class with no documents at all both read as zero. Only
the team flips a disposition.

### A REFERENCE IS CLASSIFIED BEFORE IT COUNTS

Only a CONSUMING reference makes a class (b) -- a migrator file named
after it, an `isfield(preBody, '<class>')` / `strcmp(classNameOf(s),
'<class>')` guard, or a read of `preBody.<class>`. A migrator that WRITES
the class (`x.<class> = ...`, `classBlock('<class>')`) or merely names it
as a value is counted
separately and shown as *still emitted*, because for an open class that is
evidence the decided change has **not** landed. Counting those as build
progress is what the first draft of this scan did: it made `directory`
look built off `struct('format', 'directory', ...)` and put all 18 of
`session_relative_reference`'s emission sites on the wrong side of the
ledger.

**The `decided target(s) built` signal is the WEAKER of the two** and is
marked separately for that reason. A decided target can be a class that
already existed for other reasons -- `ensemble` reaches (b) on `subject`,
`directed_relation` and `sampled_body`, none of which was built for it. Read
a row whose only evidence is a built target as *the target exists*, not as
*the work is done*.

| class | family | state | build evidence | still emitted | survivors |
|---|---|---|---|---|---|
| `acquisition_epoch` | epoch | (a) | *none* | 2 | n/a -- not measured |
| `app` | software | (b) | 2 consuming reference(s); decided target(s) built: `software` | 1 | n/a -- not measured |
| `binaryseries_parameters` | misc singletons | (a) | *none* | - | n/a -- not measured |
| `control_designation` | stimulus | (a) | *none* | 2 | n/a -- not measured |
| `daqmetadatareader` | daq configuration | (b) | migrator `migrators_j/daqmetadatareader.m`; 3 consuming reference(s); decided target(s) built: `acquisition_metadata_reader` | - | n/a -- not measured |
| `daqmetadatareader_epochdata_ingested` | daq ingested payloads | (b) | migrator `migrators_j/daqmetadatareader_epochdata_ingested.m`; decided target(s) built: `acquisition_metadata_file` | - | n/a -- not measured |
| `daqreader` | daq configuration | (b) | migrator `migrators_j/daqreader.m`; 4 consuming reference(s); decided target(s) built: `software` | 3 | n/a -- not measured |
| `daqreader_epochdata_ingested` | daq ingested payloads | (b) | migrator `migrators_j/daqreader_epochdata_ingested.m`; 3 consuming reference(s); decided target(s) built: `relative_reference` | 5 | n/a -- not measured |
| `daqreader_image_epochdata_ingested` | daq ingested payloads | (b) | migrator `migrators_j/daqreader_image_epochdata_ingested.m`; decided target(s) built: `image_observation`, `relative_reference`, `sampled_body` | - | n/a -- not measured |
| `daqsystem` | daq configuration | (b) | migrator `migrators_j/daqsystem.m`; 3 consuming reference(s); decided target(s) built: `acquisition_system` | - | n/a -- not measured |
| `directory` | file navigation | (a) | *none* | 1 | n/a -- not measured |
| `ensemble` | ensemble | (b) | 1 consuming reference(s); decided target(s) built: `subject`, `directed_relation`, `sampled_body` | - | n/a -- not measured |
| `epoch_bounded_reference` | time_reference | (a) | *none* | 3 | n/a -- not measured |
| `epoch_relative_reference` | time_reference | (a) | *none* | - | n/a -- not measured |
| `epochfiles_ingested` | epoch | (b) | migrator `migrators_j/epochfiles_ingested.m` | - | n/a -- not measured |
| `epochid` | epoch | (b) | 9 consuming reference(s) | 5 | n/a -- not measured |
| `event_bounded_reference` | time_reference | (a) | *none* | - | n/a -- not measured |
| `event_relative_reference` | time_reference | (a) | *none* | - | n/a -- not measured |
| `filenavigator` | file navigation | (b) | migrator `migrators_j/filenavigator.m`; 3 consuming reference(s); decided target(s) built: `epoch_file_pattern` | - | n/a -- not measured |
| `filter` | frequency_filter | (b) | 2 consuming reference(s) | 2 | n/a -- not measured |
| `interaction_purpose` | misc singletons | (a) | *none* | - | n/a -- not measured |
| `ngrid` | image / ngrid | (b) | 2 consuming reference(s) | 1 | n/a -- not measured |
| `projectvar` | misc singletons | (a) | *none* | - | n/a -- not measured |
| `session_bounded_reference` | time_reference | (a) | *none* | 2 | n/a -- not measured |
| `session_relative_reference` | time_reference | (a) | *none* | 18 | n/a -- not measured |
| `stimulus_presentation` | stimulus | (b) | migrator `migrators_j/stimulus_presentation.m`; 2 consuming reference(s) | - | n/a -- not measured |
| `syncgraph` | sync configuration | (b) | migrator `migrators_j/syncgraph.m`; 2 consuming reference(s); decided target(s) built: `clock_alignment_policy` | - | n/a -- not measured |
| `syncrule` | sync configuration | (b) | migrator `migrators_j/syncrule.m`; 2 consuming reference(s); decided target(s) built: `clock_alignment_configuration` | - | n/a -- not measured |
| `syncrule_mapping` | sync mapping | (b) | migrator `migrators_j/syncrule_mapping.m`; 2 consuming reference(s); decided target(s) built: `clock_alignment` | 2 | n/a -- not measured |
| `time_reference` | time_reference | (a) | *none* | 28 | n/a -- not measured |
| `utc_reference` | time_reference | (a) | *none* | - | n/a -- not measured |

#### (a) decided, nothing built -- 14

- `acquisition_epoch` (epoch) -- still emitted/named at 2 site(s): `migrators_j/element_epoch.m:86 (named)`, `migrators_j/element_epoch.m:88 (field_write)`
- `binaryseries_parameters` (misc singletons) -- no evidence found
- `control_designation` (stimulus) -- still emitted/named at 2 site(s): `migrators_j/control_stimulus_ids.m:111 (named)`, `migrators_j/control_stimulus_ids.m:133 (field_write)`
- `directory` (file navigation) -- still emitted/named at 1 site(s): `migrators_j/private/jSorterOutput.m:77 (named)`
- `epoch_bounded_reference` (time_reference) -- still emitted/named at 3 site(s): `migrators_j/syncrule_mapping.m:182 (named)`, `ndi_second_pass/stimulusBathToBath.m:71 (named)`, `ndi_second_pass/stimulusBathToBath.m:81 (field_write)`
- `epoch_relative_reference` (time_reference) -- no evidence found
- `event_bounded_reference` (time_reference) -- no evidence found
- `event_relative_reference` (time_reference) -- no evidence found
- `interaction_purpose` (misc singletons) -- no evidence found
- `projectvar` (misc singletons) -- no evidence found
- `session_bounded_reference` (time_reference) -- still emitted/named at 2 site(s): `migrators_j/ontology_table_row.m:262 (named)`, `migrators_j/ontology_table_row.m:268 (field_write)`
- `session_relative_reference` (time_reference) -- still emitted/named at 18 site(s): `migrators_j/fitcurve.m:139 (named)`, `migrators_j/fitcurve.m:146 (field_write)`, `migrators_j/image_stack.m:101 (named)`, `migrators_j/image_stack.m:106 (field_write)`, `migrators_j/jrclust_clusters.m:47 (named)`, `migrators_j/jrclust_clusters.m:52 (field_write)` ...
- `time_reference` (time_reference) -- still emitted/named at 28 site(s): `migrators_j/fitcurve.m:139 (named)`, `migrators_j/fitcurve.m:145 (field_write)`, `migrators_j/image_stack.m:101 (named)`, `migrators_j/image_stack.m:105 (field_write)`, `migrators_j/jrclust_clusters.m:47 (named)`, `migrators_j/jrclust_clusters.m:51 (field_write)` ...
- `utc_reference` (time_reference) -- no evidence found

#### (b) built, awaiting corpus proof -- 17

- `app` (software) -- consumed at 2 site(s): `migrators_j/private/jSoftwareFromApp.m:91 (guard)`, `migrators_j/private/jSoftwareFromApp.m:92 (field_read)`; still emitted/named at 1 site(s): `migrators_j/private/jMethodParameters.m:107 (field_write)`; target(s) BUILT: `software`
- `daqmetadatareader` (daq configuration) -- migrator `migrators_j/daqmetadatareader.m`; consumed at 3 site(s): `migrators_j/daqmetadatareader.m:100 (guard)`, `migrators_j/daqmetadatareader.m:101 (field_read)`, `migrators_j/daqmetadatareader.m:102 (field_read)`; target(s) BUILT: `acquisition_metadata_reader`
- `daqmetadatareader_epochdata_ingested` (daq ingested payloads) -- migrator `migrators_j/daqmetadatareader_epochdata_ingested.m`; target(s) BUILT: `acquisition_metadata_file`
- `daqreader` (daq configuration) -- migrator `migrators_j/daqreader.m`; consumed at 4 site(s): `migrators_j/daqreader.m:100 (guard)`, `migrators_j/daqreader.m:101 (field_read)`, `migrators_j/daqreader.m:102 (field_read)`, `migrators_j/daqreader_ndr.m:21 (guard)`; still emitted/named at 3 site(s): `migrators_j/daqreader_ndr.m:14 (named)`, `migrators_j/daqreader_ndr.m:22 (field_write)`, `migrators_j/daqreader_ndr.m:25 (field_write)`; target(s) BUILT: `software`
- `daqreader_epochdata_ingested` (daq ingested payloads) -- migrator `migrators_j/daqreader_epochdata_ingested.m`; consumed at 3 site(s): `migrators_j/daqreader_mfdaq_epochdata_ingested.m:40 (guard)`, `migrators_j/daqreader_mfdaq_epochdata_ingested.m:41 (field_read)`, `migrators_j/daqreader_mfdaq_epochdata_ingested.m:66 (field_read)`; still emitted/named at 5 site(s): `migrators_j/daqreader_epochdata_ingested.m:84 (named)`, `migrators_j/daqreader_image_epochdata_ingested.m:91 (named)`, `migrators_j/daqreader_mfdaq_epochdata_ingested.m:36 (named)`, `migrators_j/daqreader_mfdaq_epochdata_ingested.m:42 (field_write)`, `migrators_j/daqreader_mfdaq_epochdata_ingested.m:48 (field_write)`; target(s) BUILT: `relative_reference`
- `daqreader_image_epochdata_ingested` (daq ingested payloads) -- migrator `migrators_j/daqreader_image_epochdata_ingested.m`; target(s) BUILT: `image_observation`, `relative_reference`, `sampled_body`
- `daqsystem` (daq configuration) -- migrator `migrators_j/daqsystem.m`; consumed at 3 site(s): `migrators_j/daqsystem.m:144 (guard)`, `migrators_j/daqsystem.m:145 (field_read)`, `migrators_j/daqsystem.m:146 (field_read)`; target(s) BUILT: `acquisition_system`
- `ensemble` (ensemble) -- consumed at 1 site(s): `ndi_second_pass/ensembleMembership.m:227 (guard)`; target(s) BUILT: `subject`, `directed_relation`, `sampled_body`
- `epochfiles_ingested` (epoch) -- migrator `migrators_j/epochfiles_ingested.m`
- `epochid` (epoch) -- consumed at 9 site(s): `migrators_j/private/jMethodParameters.m:122 (guard)`, `ndi_second_pass/bodyResolver.m:216 (guard)`, `ndi_second_pass/bodyResolver.m:217 (guard)`, `ndi_second_pass/bodyResolver.m:218 (field_read)`, `ndi_second_pass/ensembleMembership.m:361 (guard)`, `ndi_second_pass/ensembleMembership.m:362 (field_read)` ...; still emitted/named at 5 site(s): `migrators_j/epochfiles_ingested.m:135 (named)`, `migrators_j/private/jMethodParameters.m:123 (named)`, `migrators_j/private/jMethodParameters.m:126 (field_write)`, `ndi_second_pass/stimulusBathToBath.m:74 (named)`, `ndi_second_pass/stimulusBathToBath.m:80 (named)`
- `filenavigator` (file navigation) -- migrator `migrators_j/filenavigator.m`; consumed at 3 site(s): `migrators_j/filenavigator.m:121 (guard)`, `migrators_j/filenavigator.m:122 (field_read)`, `migrators_j/filenavigator.m:123 (field_read)`; target(s) BUILT: `epoch_file_pattern`
- `filter` (frequency_filter) -- consumed at 2 site(s): `migrators_j/private/jFrequencyFilter.m:112 (guard)`, `migrators_j/private/jFrequencyFilter.m:113 (field_read)`; still emitted/named at 2 site(s): `migrators_j/private/jSpikeExtractionSettings.m:159 (named)`, `migrators_j/vmspikefilteringparameters.m:144 (named)`
- `ngrid` (image / ngrid) -- consumed at 2 site(s): `migrators_j/+super/ngrid.m:100 (field_read)`, `migrators_j/+super/ngrid.m:96 (guard)`; still emitted/named at 1 site(s): `migrators_j/+super/ngrid.m:115 (field_write)`
- `stimulus_presentation` (stimulus) -- migrator `migrators_j/stimulus_presentation.m`; consumed at 2 site(s): `ndi_second_pass/stimulusPresentationToManipulation.m:47 (guard)`, `ndi_second_pass/stimulusPresentationToManipulation.m:48 (field_read)`
- `syncgraph` (sync configuration) -- migrator `migrators_j/syncgraph.m`; consumed at 2 site(s): `migrators_j/syncgraph.m:86 (guard)`, `migrators_j/syncgraph.m:87 (field_read)`; target(s) BUILT: `clock_alignment_policy`
- `syncrule` (sync configuration) -- migrator `migrators_j/syncrule.m`; consumed at 2 site(s): `migrators_j/syncrule.m:95 (guard)`, `migrators_j/syncrule.m:96 (field_read)`; target(s) BUILT: `clock_alignment_configuration`
- `syncrule_mapping` (sync mapping) -- migrator `migrators_j/syncrule_mapping.m`; consumed at 2 site(s): `migrators_j/syncrule_mapping.m:106 (guard)`, `migrators_j/syncrule_mapping.m:107 (field_read)`; still emitted/named at 2 site(s): `migrators_j/syncrule_mapping.m:131 (named)`, `migrators_j/syncrule_mapping.m:149 (field_write)`; target(s) BUILT: `clock_alignment`

## AWAITING A SIGNATURE -- decided with the team, not yet recorded

These were settled in walkthroughs. They are not built and do not render as
decided because no document carries the sign-off line yet. Nothing here needs
re-deciding -- it needs recording.

| family | classes | what was decided | document |
|---|---|---|---|


## WRITTEN UP BY CLAUDE ALONE -- nobody has checked the reasoning

Each has template evidence and a written rationale, and **none of it has been
reviewed**. Counted as open work.

To sign one off, add a line to its document:

```
TEAM-SIGN-OFF: [<family>] <who/when> -- <what was decided>
```

Until that line exists the family shows here regardless of what
`tools/status_board.py` claims -- Claude cannot promote its own work.

| family | classes | proposal | written up in |
|---|---|---|---|


## Nobody has proposed anything yet

| family | classes | the call to make |
|---|---|---|


## DECIDED by the team, awaiting build

The model is settled and recorded; the schema has not changed yet. Every
one of these re-targets migrators that are already written, which is why
migrator work before the target closes is rework.

| family | classes | decision | recorded in |
|---|---|---|---|
| **time_reference** | 8 | 8 classes collapse to absolute_reference + relative_reference | `V_eta_time_reference_model_plan.md` |
| **stimulus** | 2 | timed_sequence data_type + timed_sequence_manipulation leaf; control_designation resolved here | `V_eta_stimulus_model_plan.md` |
| **ensemble** | 1 | group subject + epoch-scoped member_of edges + rebuildable cache | `V_eta_ensemble_plan.md` |
| **image / ngrid** | 2 | ngrid phases into sampled_body; image is a standalone data_type; the two image_stack tombstones are held until the subject is recoverable | `V_eta_image_model_plan.md` |
| **epoch** | 3 | MINT `epoch` ENTITY (+ OPTIONAL `instrument_id`, 2026-08-06); element_epoch dissolves; epochid DROPPED; probemap -> edges (B) | `V_eta_epoch_plan.md` |
| **daq configuration** | 3 | acquisition_system + `acquisition_metadata_reader` keep ids; class names fold to software entities | `V_eta_daq_family_decisions.md` |
| **daq ingested payloads** | 3 | reader one DECOMPOSES (per-clock relative_references + sampled_body) and retires; metadata one -> `acquisition_metadata_file`; image one folds into the image model | `V_eta_ingested_payload_findings.md` |
| **sync configuration** | 2 | syncrule -> `clock_alignment_configuration` (parameters DECLARED, devices become edges); syncgraph -> `clock_alignment_policy` (earns existence on membership) | `V_eta_clock_alignment_cluster_plan.md` |
| **sync mapping** | 1 | -> `clock_alignment` (relation + `polynomial` data_type); endpoints are relative_reference docs; syncgraph_id restored, invented epochid removed | `V_eta_clock_alignment_cluster_plan.md` |
| **file navigation** | 2 | filenavigator -> `epoch_file_pattern` (id preserved; patterns PARSED not eval'd); `directory` is not a source | `V_eta_daq_family_decisions.md` |
| **openMINDS** | 1 | strain -> entity + recursive background_strain_#; strain_id on term_assertion | `V_eta_openminds_family_record.md` |
| **software** | 1 | app -> software entity + software_id edge + execution_environment (R1) | `V_eta_tenet_audit.md` |
| **frequency_filter** | 1 | referenced document (not entity); band edges; typed gain fields; no sample_rate | `V_eta_frequency_filter_model_plan.md` |
| **spike processing parameters** | 4 | 4 -> 1 `method_parameters` (id+name preserved); canonical parts typed, rest a bag | `V_eta_method_parameters_plan.md` |
| **stimulus parameters** | 2 | stimulus_parameter DISSOLVES to a typed leaf keyed by its CURIE (build gated on #32); stimulus_parameter_table PASSES THROUGH; both tombstones repaired | `V_eta_stimulus_parameter_plan.md` |
| **stimulus response** | 4 | 4 -> 2: `harmonic_component` data_type + calculation leaf (id preserved); parameters fold inline, killing 11,440 empty required edges | `V_eta_stimulus_response_model_plan.md` |
| **subject measurement** | 1 | route through the `measurement` fold -- no new class; `datestamp` is a TIME ANCHOR (-> absolute_reference), NOT a field (corrected 2026-08-06) | `V_eta_go_forward_class_audit.md` |
| **misc singletons** | 3 | binaryseries_parameters -> sampled_body; projectvar PASSES THROUGH (needs real docs); interaction_purpose is a target (#32) | `V_eta_go_forward_class_audit.md` |

## v1 source side (from the coverage ledger)

| disposition | count |
|---|---|
| retire | 45 |
| consumed by migrator (no tombstone) | 27 |
| in_progress | 19 |
| persist | 4 |
| test/demo fixture (non-production) | 3 |
| no V_eta home, no migrator -- UNVERIFIED | 3 |
| dissolved → subject | 1 |

**UNVERIFIED** -- no V_eta home, no migrator, fate never established. These strand today:

- `generic_file`
- `imageCollection`
- `valid_interval`

## Families naming classes that are no longer open

Settled or removed since the family was written -- prune from `FAMILIES`:

- `imageStack_parameters`
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

