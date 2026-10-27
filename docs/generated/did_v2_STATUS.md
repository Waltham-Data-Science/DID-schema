# V_eta status board (GENERATED -- do not hand-edit)

Regenerate with `python3 tools/status_board.py`. CI runs `--check`.

State lives here. The plan documents under `schemas/` keep the RATIONALE
for each model; this board owns *how much is left and what exactly*.

**A class is DECIDED only when it cites a decision line that exists**: a
`TEAM-SIGN-OFF [tag]` line, or a `Decided by <team member>, <date> [<tag>]:` line, in
the document its citation names (`tools/decision_citations.py`). Anything
else is **Proposed (not decided)**, whatever any prose says.

## Where V_eta stands

| | count |
|---|---|
| target classes | 177 |
| settled (persist) | 93 |
| settled (retire) | 80 |
| **still open (`in_progress`)** | **4** |
| **`retire` with no migrator YET** | **2** |
| **open classes in all** | **6** |
| &nbsp;&nbsp;decided (cites a decision line), awaiting build | 6 |
| &nbsp;&nbsp;**proposed (not decided), awaiting review** | **0** |

| open-class BUILD/PROOF state (derived, see below) | count |
|---|---|
| (a) nothing built (the decision state is a separate column) | 2 |
| (b) built, awaiting corpus proof | 2 |
| (c) corpus: 0 survivors in the corpora read | 0 |
| (?) UNMEASURED -- no build evidence was ever taken | 0 |

## What is actually left on the 4 open classes

`in_progress` is a HAND-WRITTEN DECLARATION: every one of these classes is
open because its hand-written `disposition` in `schemas/did_v2/index.json` is
`in_progress`, and it leaves the list only when a person changes that entry.
Nothing about a landed migrator, a passing test or a green corpus
moves it. The table below does not change that membership -- only the team
decides a disposition -- it DERIVES, per class, how far the work has got.

### The measurement and its denominator

| evidence source | reach |
|---|---|
| build: V_eta migrator packages read | `DID-matlab:migrators_j`, `NDI-matlab:ndi_second_pass`, `DID-matlab:convert` |
| build: &nbsp;&nbsp;-- of those, per-document migrator | `DID-matlab:migrators_j`, `NDI-matlab:ndi_second_pass` |
| build: &nbsp;&nbsp;-- of those, batch post-pass | `DID-matlab:convert` |
| build: migrator files inspected | 230 |
| build: &nbsp;&nbsp;-- of those, per-document migrator | 194 |
| build: &nbsp;&nbsp;-- of those, batch post-pass | 36 |
| build: V_zeta files DELIBERATELY EXCLUDED (`+migrators`, `+migrators_i`, `+migrators_e`) | 22 |
| build: migrator lines inspected | 57334 |
| build: &nbsp;&nbsp;-- of those, per-document migrator | 37244 |
| build: &nbsp;&nbsp;-- of those, batch post-pass | 20090 |
| build: classes queried | 4 |
| build: open classes MINTED as a document class | 0 |
| build: &nbsp;&nbsp;-- open classes minted in a per-document migrator (rows overlap) | 0 |
| build: &nbsp;&nbsp;-- open classes minted in a batch post-pass (rows overlap) | 0 |
| build: of those, discounted (decision retires the class) | 0 |
| build: `document_class` writes whose class name is a VARIABLE | 10 |
| build: &nbsp;&nbsp;-- of those, in a per-document migrator | 6 |
| build: &nbsp;&nbsp;-- of those, in a batch post-pass | 4 |
| corpus: `*-summary.json` reports read | 0 |
| corpus: reports carrying an `unconverted_count` | 0 |
| corpus: documents behind those reports | 0 |
| corpus: corpora named | **NONE** |

**NO CORPUS SURVIVOR DATA.** 0 report(s) were read and 0 of them carry
an `unconverted_count`, so **state (c) cannot be reached by any class in**
**this run** and none is rendered as corpus-proven. A report without that
key measured nothing; its silence is not a zero. Point `--census` at a
directory of corpus reports, or run the DID-matlab corpus gate.

### Where the 4 open classes sit

| state | classes |
|---|---|
| (a) nothing built (the decision state is a separate column) | 2 |
| (b) built, awaiting corpus proof | 2 |
| (c) corpus: 0 survivors in the corpora read | 0 |
| (?) UNMEASURED -- no build evidence was ever taken | 0 |

**(c) IS EVIDENCE, NOT A DISPOSITION.** 0 survivors is a fact about the
corpora that were read, and it may not be promoted to `retire` on its own:
the corpora are a SAMPLE of datasets, not the universe, and the reports carry
no per-class SOURCE denominator -- `by_class` counts OUTPUT names, so a class
fully consumed and a class with no documents at all both read as zero. Only
the team flips a disposition.

### A REFERENCE IS CLASSIFIED BEFORE IT COUNTS

Two kinds of reference make a class (b), and they answer different
questions.

**CONSUMED** -- a migrator file named after it, an `isfield(preBody,
'<class>')` / `strcmp(classNameOf(s), '<class>')` guard, or a read of
`preBody.<class>`. That is evidence about a v1 SOURCE: something eats it.

**MINTED** -- the migrator sets a document's class. That is evidence about
a V_eta TARGET: something builds it. The scan could not see this at all
until 2026-08-10, and the cost was concrete: `control_designation`
rendered as *decided, nothing built* while
`DID-matlab:migrators_j/control_stimulus_ids.m:111` was minting it -- no
file is named after the target of a rename, so a filename key can never
find one.

### THE V_eta PASS HAS TWO HALVES AND THE BOARD READ ONE

Corrected 2026-08-11. The DID-side V_eta pass is `+migrators_j` (one file
per v1 class, each seeing ONE document) **and** the BATCH POST-PASSES that
run over the whole converted batch afterwards and do what a single-document
migrator provably cannot -- mint an epoch, resolve a session anchor, fold
the deferred baths. Those live one directory UP, in `+did2/+convert` itself
and in its `+entities/` and `+readers/` helper packages, and the scan roots
did not name them. Re-derived census of `+did2/+convert`:

| files | where | this board |
|---|---|---|
| 125 | `+migrators_j` | scans, always did |
| 38 | `+migrators` (22) + `+migrators_i` (9) + `+migrators_e` (7) | EXCLUDED, deliberately -- the V_zeta path |
| 24 | 14 in `+convert`, 7 in `+entities/`, 3 in `+readers/` | **ADDED 2026-08-11 -- previously invisible** |
| 187 | total `.m` under `+did2/+convert` | |

The 38 stay out: a V_zeta migrator is not evidence a V_eta target is
built. That exclusion is now COUNTED in the denominator table above rather
than left as an omission from a list -- an exclusion nobody can see in the
output is indistinguishable from a root somebody forgot, which is exactly
how the 24 went missing.

**THE TWO GROUPS ARE NEVER MERGED INTO ONE COUNT.** Every column below is
carried per group as well as in total, because *a batch post-pass mints
this class* and *a per-document migrator mints this class* are different
facts. Each site names its repository AND its package, so the group is
readable off any citation: `DID-matlab:convert/resolveDeferredBaths.m:177`
is a batch post-pass, `DID-matlab:migrators_j/fitcurve.m:139` is not.

**THERE ARE THREE MINT IDIOMS AND UNTIL 2026-08-11 THIS BOARD KNEW ONE.**

| idiom | shape | sites | per-document migrator | batch post-pass |
|---|---|---|---|---|
| 1 | `b.document_class = struct('class_name', '<class>', ...)` | 8 | 5 | 3 |
| 2 | `b.document_class = classBlock('<class>', {supers})` | 0 | 0 | 0 |
| 3 | `b.document_class.class_name = '<class>';` | 5 | 5 | 0 |
| 4 | `did2.build.statement('<direction>', ..., 'ValueKind', '<kind>')`, `did2.build.document('<class>', ...)` or a fixed-class builder | 74 | 42 | 32 |
| 5 | a wrapper of idiom 4: `jStatement(preBody, '<class>', ...)` | 48 | 48 | 0 |
| - | class name is a VARIABLE -- unresolved here | 10 | 6 | 4 |

**THE THREE IDIOMS ARE RE-MEASURED IN THE NEW ROOTS, NOT ASSUMED TO CARRY
OVER.** The per-group columns are counted per file, so which idioms the
batch post-passes actually use is read off the table rather than asserted
in a sentence that can go stale; a zero there is a measured zero over the
file and line denominators above, and if a post-pass adopts `classBlock`
tomorrow the column moves on its own.

Idioms 2 and 3 carry no `'class_name', '<X>'` comma pair, so the regex
imported from `tools/coverage.py` cannot see them. `classBlock` is a LOCAL
SUBFUNCTION, redefined in eight files with two different arities, and it is
recognised HERE BY ITS SHAPE, not its name: a local function that assigns
its own output a struct declaring `superclasses` whose `class_name` comes
from one of its parameters. The literal is then read from that parameter's
INDEX at each call site, so the superclass argument beside it cannot be
mistaken for a mint.

**WHAT THE MISS COST, stated as the number and not as a lesson.**
`session_relative_reference` is a class whose whole open question is that
it must STOP being emitted. Idiom 1 in `+migrators_j` alone puts its mint
count at **3**; this run measures **n/a -- no longer open**
Two corrections got it there, and they are separate faults. Six migrators
(`fitcurve`, `image_stack`, `jrclust_clusters`, `neuron_extracellular`,
`pyraview`, `vmspikefit`) mint it through `classBlock`, which the
`'class_name'`-comma regex could not see; and the batch post-pass
`+convert/resolveDeferredBaths.m` mints it twice in a package the board
was not reading at all. The board reported a third of the outstanding
work, in this project's characteristic direction. Neither set was dropped
-- the six were filed as `named`, the weakest bucket, and the two were
filed nowhere, which is worse than dropping them because the first looks
like a measurement and the second looks like clean ground.

**A `document_class` WRITE WHOSE CLASS NAME IS A VARIABLE IS COUNTED, NOT
SKIPPED.** `struct('class_name', leafClass, ...)` and
`classBlock(e.class, ...)` need the CALL GRAPH to resolve, which is
`tools/refresh_migration_targets.py`'s job, not this per-file scan's. Those
sites appear in the denominator table above. The mint counts in this
artifact are therefore a FLOOR.

| unresolved `document_class` write | class name expression |
|---|---|
| `DID-matlab:convert/resolveEpochProbemap.m:1566` | `entry.class` |
| `DID-matlab:convert/resolveEpochProbemap.m:947` | `kind.className` |
| `DID-matlab:convert/resolveLawnPlateSubjects.m:1028` | `entry{1}` |
| `DID-matlab:convert/universalRenames.m:242` | `v2ClassName;` |
| `DID-matlab:migrators_j/image_stack.m:265` | `calculation + kind` |
| `DID-matlab:migrators_j/ontology_table_row.m:233` | `measures{i, 2}` |
| `DID-matlab:migrators_j/ontology_table_row.m:379` | `measures{i, 2}` |
| `DID-matlab:migrators_j/ontology_table_row.m:650` | `observation + shapeClass` |
| `DID-matlab:migrators_j/private/jMeasurementFold.m:78` | `observation + leaf` |
| `DID-matlab:migrators_j/treatment.m:102` | `manipulation + kind` |

**THE OTHER CATEGORIES ARE REPORTED SEPARATELY AND ARE NEVER SUMMED.** A
migrator that WRITES a block of that name (`x.<class> = ...`), one that
merely NAMES it as a string value, and one that MENTIONS it in a comment
are three different facts, and a single cell reading *still emitted/named
at N site(s)* merged them. It also swallowed the six missed mints above.
Each now has its own column and its own count; comment mentions count
toward nothing and are shown so that can be checked rather than believed.

**A MINT IS DISCOUNTED WHEN THE DECISION RETIRES THE CLASS.** For a class
whose signed decision is that it stops existing, minting it is the work
still outstanding, not progress -- so `session_relative_reference` and its
family stay where they are however many sites emit them. The list is
transcribed from the sign-off lines in
`tools/status_board.py:RETIRED_BY_ITS_OWN_DECISION`, and every replacement
named there is checked to exist. Note this is an OPEN CONTRADICTION between
two committed records, not a settled fact: `did_v2_migration_targets.json`
still lists `session_relative_reference` as a decided target of 40+ v1
sources, written before the time model collapsed it. The board takes the
under-reporting side and does not settle it.

**The `decided target(s) built` signal is the WEAKER of the two** and is
marked separately for that reason. A decided target can be a class that
already existed for other reasons -- `ensemble` reaches (b) on `subject`,
`directed_relation` and `sampled_body`, none of which was built for it. Read
a row whose only evidence is a built target as *the target exists*, not as
*the work is done*.

Each of the last four columns is one kind of fact and they are NOT added
together. `minted` = a document of this class is produced; `field writes`
= a block of that name is written; `named` = the name appears as a string
value; `comments` = prose, which counts toward nothing. Each cell is
written `total (M+B)` -- M from a per-document migrator, B from a batch
post-pass -- so no cell in this table is an undifferentiated count.

| class | decision | state | build evidence | minted (M+B) | field writes (M+B) | named (M+B) | comments (M+B) | survivors |
|---|---|---|---|---|---|---|---|---|
| `app` | decided | (b) | 5 consuming reference(s) (2 per-document migrator, 3 batch post-pass); decided target(s) built: `entity (software)` | - | 2 (1+1) | 1 (0+1) | 180 (141+39) | n/a -- not measured |
| `binaryseries_parameters` | decided | (b) | migrator `DID-matlab:migrators_j/binaryseries_parameters.m`; decided target(s) built: `statement`, `sampled_body` | - | - | 1 (1+0) | 15 (15+0) | n/a -- not measured |
| `interaction_purpose` | decided | (a) | *none* | - | - | - | 3 (3+0) | n/a -- not measured |
| `projectvar` | decided | (a) | *none* | - | - | - | 3 (3+0) | n/a -- not measured |

#### (a) nothing built (the decision state is a separate column) -- 2

- `interaction_purpose` (decided) -- mentioned in 3 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/openminds_stimulus.m:49 (comment_mention)`, `DID-matlab:migrators_j/openminds_stimulus.m:50 (comment_mention)`, `DID-matlab:migrators_j/openminds_stimulus.m:70 (comment_mention)`
- `projectvar` (decided) -- mentioned in 3 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:387 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:405 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:49 (comment_mention)`

#### (b) built, awaiting corpus proof -- 2

- `app` (decided) -- consumed at 2 site(s), per-document migrator: `DID-matlab:migrators_j/private/jSoftwareFromApp.m:124 (guard)`, `DID-matlab:migrators_j/private/jSoftwareFromApp.m:125 (field_read)`; consumed at 3 site(s), batch post-pass: `DID-matlab:convert/resolveValidIntervals.m:660 (guard)`, `DID-matlab:convert/universalRenames.m:287 (guard)`, `DID-matlab:convert/universalRenames.m:288 (field_read)`; a block of this name is WRITTEN at 1 site(s), per-document migrator: `DID-matlab:migrators_j/private/jMethodParameters.m:105 (field_write)`; a block of this name is WRITTEN at 1 site(s), batch post-pass: `DID-matlab:convert/universalRenames.m:289 (field_write)`; NAMED as a string value at 1 site(s), batch post-pass: `DID-matlab:convert/resolveValidIntervals.m:1115 (named)`; mentioned in 141 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:1052 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:150 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:166 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:402 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:403 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:493 (comment_mention)` ...; mentioned in 39 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/calcCommon.m:25 (comment_mention)`, `DID-matlab:convert/calcCommon.m:28 (comment_mention)`, `DID-matlab:convert/resolveEpochProbemap.m:1271 (comment_mention)`, `DID-matlab:convert/resolveOpenmindsCitations.m:883 (comment_mention)`, `DID-matlab:convert/resolveResponseParameters.m:57 (comment_mention)`, `DID-matlab:convert/resolveResponseParameters.m:573 (comment_mention)` ...; target(s) BUILT: `entity (software)`
- `binaryseries_parameters` (decided) -- migrator `DID-matlab:migrators_j/binaryseries_parameters.m`; NAMED as a string value at 1 site(s), per-document migrator: `DID-matlab:migrators_j/binaryseries_parameters.m:277 (named)`; mentioned in 15 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/+super/image_stack_parameters.m:94 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:335 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:573 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:574 (comment_mention)`, `DID-matlab:migrators_j/binaryseries_parameters.m:16 (comment_mention)`, `DID-matlab:migrators_j/binaryseries_parameters.m:190 (comment_mention)` ...; target(s) BUILT: `statement`, `sampled_body`

## Proposed (not decided) -- awaiting review

DENOMINATOR: 6 open class(es); 0 cite no decision line that resolves.

None -- every open class cites a decision line that exists.

## Decided, awaiting build -- the open classes

DENOMINATOR: 6 open class(es); 6 cite a decision line that exists. The decision column is the line's own text, not a summary.

| class | targets built | decided in | decision |
|---|---|---|---|
| `app` | 1 of 1 | [software]. "TEAM-SIGN-OFF [software]: jess, 2026-08-06 -- the" (did_v2_tenet_audit.md:16). | jess, 2026-08-06 -- the `app` mixin is replaced by a `software` ENTITY (deduplicated by name+version) referenced from a statement by `software_id`, with the run-specific os / interpreter details in `execution_environm...` |
| `binaryseries_parameters` | 2 of 2 | [misc singletons]. "TEAM-SIGN-OFF [misc singletons]: jess, 2026-08-09" (did_v2_go_forward_class_audit.md:9). | jess, 2026-08-09 -- `binaryseries_parameters` folds into the data_body model and is retired (its `time_type` is the time axis's new `datum_type`, its `data_type` the statement's, `data_dim` the axis count, `samples_re...` |
| `calculator` | no target recorded | [calculator mixin dropped (#73)]. "TEAM-SIGN-OFF [calculator mixin dropped (#73)]" (did_v2_subject_calculation_plan.md:371). | jess@walthamdatascience.com / 2026-09-29 -- (amends #67) the run environment is two `software` edges on `subject_calculation`, `interpreter_id` and `operating_system_id`; `runtime_environment` (and `execution_environm...` |
| `imageCollection` | no target recorded | [stranded sources]. "TEAM-SIGN-OFF [stranded sources]" (did_v2_OPEN_WORK.md:811). | jess@walthamdatascience.com, 2026-08-11 -- generic_file folds to term_observation + opaque_body; imageCollection is a tombstone. Both are BUILT and ran in 6 of 6 corpora in run 31522068566. THIS SIGNATURE COVERS TWO C... |
| `interaction_purpose` | no target recorded | [misc singletons]. "TEAM-SIGN-OFF [misc singletons]: jess, 2026-08-09" (did_v2_go_forward_class_audit.md:9). | jess, 2026-08-09 -- `binaryseries_parameters` folds into the data_body model and is retired (its `time_type` is the time axis's new `datum_type`, its `data_type` the statement's, `data_dim` the axis count, `samples_re...` |
| `projectvar` | no target recorded | [misc singletons]. "TEAM-SIGN-OFF [misc singletons]: jess, 2026-08-09" (did_v2_go_forward_class_audit.md:9). | jess, 2026-08-09 -- `binaryseries_parameters` folds into the data_body model and is retired (its `time_type` is the time axis's new `datum_type`, its `data_type` the statement's, `data_dim` the axis count, `samples_re...` |

## Every decision citation

DENOMINATOR: 73 class(es) cite 82 decision line(s); 0 citation(s) do not resolve. "targets built" counts the class's decided targets present in the built set (a target equal to the class is a passthrough and is not counted).

| class | disposition | targets built | decided in |
|---|---|---|---|
| `acquisition_epoch` | retire | no target recorded | [epoch]. "TEAM-SIGN-OFF [epoch]: jess@walthamdatascience.com /" (did_v2_epoch_plan.md:884). |
| `app` | in_progress | 1 of 1 | [software]. "TEAM-SIGN-OFF [software]: jess, 2026-08-06 -- the" (did_v2_tenet_audit.md:16). |
| `binaryseries_parameters` | in_progress | 2 of 2 | [misc singletons]. "TEAM-SIGN-OFF [misc singletons]: jess, 2026-08-09" (did_v2_go_forward_class_audit.md:9). |
| `calculator` | retire | no target recorded | [calculator mixin dropped (#73)]. "TEAM-SIGN-OFF [calculator mixin dropped (#73)]" (did_v2_subject_calculation_plan.md:371). |
| `cellTypeLabels` | retire | 4 of 4 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:572). |
| `control_stimulus_ids` | retire | no target recorded | [control as covariate]. "Decided by Jess Haley, 2026-10-22 [control as covariate]" (did_v2_stimulus_response_model_plan.md:618). |
| `daqmetadatareader` | retire | 1 of 1 | [daq configuration]. "TEAM-SIGN-OFF [daq configuration]" (did_v2_daq_family_decisions.md:489). |
| `daqmetadatareader_epochdata_ingested` | retire | 1 of 1 | [daq ingested payloads]. "TEAM-SIGN-OFF [daq ingested payloads]" (did_v2_ingested_payload_findings.md:276). |
| `daqreader` | retire | 1 of 1 | [daq configuration]. "TEAM-SIGN-OFF [daq configuration]" (did_v2_daq_family_decisions.md:489). |
| `daqreader_epochdata_ingested` | retire | 1 of 1 | [daq ingested payloads]. "TEAM-SIGN-OFF [daq ingested payloads]" (did_v2_ingested_payload_findings.md:276).; [epoch files as data bodies]. "Decided by Jess Haley, 2026-10-21 [epoch files as data" (did_v2_recording_observation_plan.md:115). |
| `daqreader_image_epochdata_ingested` | retire | 3 of 3 | [daq ingested payloads]. "TEAM-SIGN-OFF [daq ingested payloads]" (did_v2_ingested_payload_findings.md:276).; [epoch files as data bodies]. "Decided by Jess Haley, 2026-10-21 [epoch files as data" (did_v2_recording_observation_plan.md:115). |
| `daqreader_mfdaq_epochdata_ingested` | consumed by migrator (no tombstone) | 1 of 1 | [epoch files as data bodies]. "Decided by Jess Haley, 2026-10-21 [epoch files as data" (did_v2_recording_observation_plan.md:115). |
| `daqreader_ndr` | consumed by migrator (no tombstone) | 3 of 3 | [daq configuration]. "TEAM-SIGN-OFF [daq configuration]" (did_v2_daq_family_decisions.md:489). |
| `daqsystem` | retire | 1 of 1 | [daq configuration]. "TEAM-SIGN-OFF [daq configuration]" (did_v2_daq_family_decisions.md:489). |
| `element` | retire | 10 of 10 | [raw recording observation]. "TEAM-SIGN-OFF [raw recording observation]" (did_v2_recording_observation_plan.md:99).; [epoch files as data bodies]. "Decided by Jess Haley, 2026-10-21 [epoch files as data" (did_v2_recording_observation_plan.md:115). |
| `element_epoch` | consumed by migrator (no tombstone) | no target recorded | [epoch]. "TEAM-SIGN-OFF [epoch]: jess@walthamdatascience.com /" (did_v2_epoch_plan.md:884). |
| `ensemble` | retire | 3 of 3 | [ensemble]. "TEAM-SIGN-OFF [ensemble]: jess, 2026-08-06 -- per-neuron" (did_v2_ensemble_plan.md:10). |
| `epochclocktimes` | consumed by migrator (no tombstone) | 1 of 1 | [epochclocktimes]. "TEAM-SIGN-OFF [epochclocktimes]" (did_v2_time_reference_family_plan.md:181).; [epoch extent -- row #113]. "TEAM-SIGN-OFF [epoch extent -- row #113]" (did_v2_OPEN_WORK.md:853). |
| `epochfiles_ingested` | retire | 1 of 1 | [epoch]. "TEAM-SIGN-OFF [epoch]: jess@walthamdatascience.com /" (did_v2_epoch_plan.md:884).; [epoch files as data bodies]. "Decided by Jess Haley, 2026-10-21 [epoch files as data" (did_v2_recording_observation_plan.md:115). |
| `epochid` | retire | no target recorded | [epoch]. "TEAM-SIGN-OFF [epoch]: jess@walthamdatascience.com /" (did_v2_epoch_plan.md:884). |
| `fileReference` | retire | 1 of 1 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:572). |
| `filenavigator` | retire | 1 of 1 | [file navigation]. "TEAM-SIGN-OFF [file navigation]: jess, 2026-08-06" (did_v2_daq_family_decisions.md:343). |
| `filter` | retire | 1 of 1 | [2026-07-30]. "TEAM-SIGN-OFF: jess, 2026-07-30" (did_v2_frequency_filter_model_plan.md:5).; [filters are methods]. "Decided by Jess Haley, 2026-10-22 [filters are methods]" (did_v2_frequency_filter_model_plan.md:201). |
| `fitcurve` | retire | 1 of 1 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:572). |
| `geneExpression` | retire | no target recorded | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:572). |
| `geneList` | retire | 4 of 4 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:572). |
| `geneListMapping` | retire | 3 of 3 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:572). |
| `generic_file` | retire | 2 of 2 | [stranded sources]. "TEAM-SIGN-OFF [stranded sources]" (did_v2_OPEN_WORK.md:811). |
| `hartley_calc` | retire | 5 of 5 | [receptive field fold]. "TEAM-SIGN-OFF [receptive field fold]" (did_v2_ngrid_family_findings.md:358). |
| `image` | retire | 4 of 4 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:572). |
| `imageCollection` | retire | no target recorded | [stranded sources]. "TEAM-SIGN-OFF [stranded sources]" (did_v2_OPEN_WORK.md:811). |
| `imageStack` | retire | 4 of 4 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:572). |
| `imageStack_parameters` | retire | no target recorded | [image / ngrid]. "TEAM-SIGN-OFF [image / ngrid]: jess@walthamdatascience.com" (did_v2_image_model_plan.md:154). |
| `interaction_purpose` | in_progress | no target recorded | [misc singletons]. "TEAM-SIGN-OFF [misc singletons]: jess, 2026-08-09" (did_v2_go_forward_class_audit.md:9). |
| `jrclust_clusters` | retire | 1 of 1 | [confirm sheet 2026-08-17]. "TEAM-SIGN-OFF [confirm sheet 2026-08-17]" (did_v2_go_forward_class_audit.md:723).; [spike-sorter output, amends the 2026-08-17 confirm sheet]. "TEAM-SIGN-OFF [spike-sorter output, amends the 2026-08-17" (did_v2_go_forward_class_audit.md:1023). |
| `kiasort_clusters` | retire | 1 of 1 | [spike-sorter output, amends the 2026-08-17 confirm sheet]. "TEAM-SIGN-OFF [spike-sorter output, amends the 2026-08-17" (did_v2_go_forward_class_audit.md:1023). |
| `kilosort_clusters` | retire | 1 of 1 | [spike-sorter output, amends the 2026-08-17 confirm sheet]. "TEAM-SIGN-OFF [spike-sorter output, amends the 2026-08-17" (did_v2_go_forward_class_audit.md:1023). |
| `lightsheetZarrLevel` | retire | 1 of 1 | [lightsheet migrator points 1-11]. "TEAM-SIGN-OFF [lightsheet migrator points 1-11]" (review/73/OPEN_ITEMS.md:317). |
| `lightsheetZarrPyramid` | retire | 3 of 3 | [lightsheet migrator points 1-11]. "TEAM-SIGN-OFF [lightsheet migrator points 1-11]" (review/73/OPEN_ITEMS.md:317). |
| `neuron_extracellular` | retire | 7 of 7 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:572). |
| `ngrid` | retire | no target recorded | [image / ngrid]. "TEAM-SIGN-OFF [image / ngrid]: jess@walthamdatascience.com" (did_v2_image_model_plan.md:154). |
| `ontologyImage` | retire | 4 of 4 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:572). |
| `openminds` | retire | no target recorded | [2026-08-08]. "TEAM-SIGN-OFF: jess, 2026-08-08 -- Part 7: the 3 unattached" (did_v2_openminds_family_record.md:10). |
| `oridirtuning_calc` | consumed by migrator (no tombstone) | 3 of 3 | [confirm sheet 2026-08-17]. "TEAM-SIGN-OFF [confirm sheet 2026-08-17]" (did_v2_go_forward_class_audit.md:723). |
| `probe_geometry` | retire | 3 of 3 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:572). |
| `probe_location` | retire | 2 of 2 | [confirm sheet 2026-08-17]. "TEAM-SIGN-OFF [confirm sheet 2026-08-17]" (did_v2_go_forward_class_audit.md:723). |
| `projectvar` | in_progress | no target recorded | [misc singletons]. "TEAM-SIGN-OFF [misc singletons]: jess, 2026-08-09" (did_v2_go_forward_class_audit.md:9). |
| `pyraview` | retire | 1 of 1 | [raw recording observation]. "TEAM-SIGN-OFF [raw recording observation]" (did_v2_recording_observation_plan.md:99).; [pyraview levels, amends the 2026-08-13 pyraview pyramid confirmation]. "TEAM-SIGN-OFF [pyraview levels, amends the 2026-08-13" (did_v2_recording_observation_plan.md:111). |
| `session` | consumed by migrator (no tombstone) | 1 of 1 | [session]. "TEAM-SIGN-OFF [session]: jess@walthamdatascience.com /" (did_v2_go_forward_class_audit.md:664). |
| `sorting_parameters` | retire | 1 of 1 | [spike processing parameters]. "TEAM-SIGN-OFF [spike processing parameters]: jess" (did_v2_method_parameters_plan.md:32). |
| `spatialGeneExpressionCells` | retire | 5 of 5 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:572). |
| `spatialGeneExpressionPyramid` | retire | 5 of 5 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:572). |
| `spatialGeneExpressionTiles` | retire | 1 of 1 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:572). |
| `spike_extraction_parameters` | retire | 1 of 1 | [spike processing parameters]. "TEAM-SIGN-OFF [spike processing parameters]: jess" (did_v2_method_parameters_plan.md:32). |
| `spike_extraction_parameters_modification` | retire | 1 of 1 | [spike processing parameters]. "TEAM-SIGN-OFF [spike processing parameters]: jess" (did_v2_method_parameters_plan.md:32). |
| `stimulus_bath` | consumed by migrator (no tombstone) | 2 of 2 | [bath is a manipulation]. "Decided by Jess Haley, 2026-10-21 [bath is a manipulation]" (did_v2_go_forward_class_audit.md:727). |
| `stimulus_parameter` | retire | no target recorded | [stimulus parameters]. "TEAM-SIGN-OFF [stimulus parameters]" (did_v2_stimulus_parameter_plan.md:221). |
| `stimulus_parameter_table` | retire | no target recorded | [stimulus parameters]. "TEAM-SIGN-OFF [stimulus parameters]" (did_v2_stimulus_parameter_plan.md:221). |
| `stimulus_presentation` | retire | 2 of 2 | [stimulus]. "TEAM-SIGN-OFF [stimulus]: jess@walthamdatascience.com /" (did_v2_stimulus_model_plan.md:258). |
| `stimulus_response` | retire | no target recorded | [stimulus response]. "TEAM-SIGN-OFF [stimulus response]" (did_v2_stimulus_response_model_plan.md:541). |
| `stimulus_response_scalar` | retire | 1 of 1 | [stimulus response]. "TEAM-SIGN-OFF [stimulus response]" (did_v2_stimulus_response_model_plan.md:541). |
| `stimulus_response_scalar_parameters` | retire | no target recorded | [stimulus response]. "TEAM-SIGN-OFF [stimulus response]" (did_v2_stimulus_response_model_plan.md:541). |
| `stimulus_response_scalar_parameters_basic` | retire | 1 of 1 | [stimulus response]. "TEAM-SIGN-OFF [stimulus response]" (did_v2_stimulus_response_model_plan.md:541). |
| `subject` | consumed by migrator (no tombstone) | 1 of 1 | [subject]. "TEAM-SIGN-OFF [subject]: jess@walthamdatascience.com /" (did_v2_go_forward_class_audit.md:697). |
| `subjectmeasurement` | retire | no target recorded | [subject measurement]. "TEAM-SIGN-OFF [subject measurement]: jess, 2026-08-06" (did_v2_go_forward_class_audit.md:336). |
| `syncgraph` | retire | 1 of 1 | [sync configuration]. "TEAM-SIGN-OFF [sync configuration]" (did_v2_clock_alignment_cluster_plan.md:506). |
| `syncrule` | retire | 1 of 1 | [sync configuration]. "TEAM-SIGN-OFF [sync configuration]" (did_v2_clock_alignment_cluster_plan.md:506). |
| `syncrule_mapping` | retire | 1 of 1 | [sync mapping]. "TEAM-SIGN-OFF [sync mapping]: jess@walthamdatascience.com /" (did_v2_clock_alignment_cluster_plan.md:508). |
| `treatment` | consumed by migrator (no tombstone) | 7 of 7 | [confirm sheet 2026-08-17]. "TEAM-SIGN-OFF [confirm sheet 2026-08-17]" (did_v2_go_forward_class_audit.md:723). |
| `tuningcurve_calc` | consumed by migrator (no tombstone) | 3 of 3 | [confirm sheet 2026-08-17]. "TEAM-SIGN-OFF [confirm sheet 2026-08-17]" (did_v2_go_forward_class_audit.md:723). |
| `valid_interval` | retire | 1 of 1 | [logical_observation]. "TEAM-SIGN-OFF [logical_observation]" (did_v2_logical_observation_plan.md:365).; [logical_observation amendment 1]. "TEAM-SIGN-OFF [logical_observation amendment 1]" (did_v2_logical_observation_plan.md:425). |
| `vmspikefilteringparameters` | retire | 1 of 1 | [spike processing parameters]. "TEAM-SIGN-OFF [spike processing parameters]: jess" (did_v2_method_parameters_plan.md:32). |
| `vmspikefit` | retire | 1 of 1 | [#73 audit 2, D1-D13]. "TEAM-SIGN-OFF [#73 audit 2, D1-D13]" (did_v2_spatial_transcriptomics_plan.md:574). |

Every decided target these classes name is present in the built set, so
what remains for them is MIGRATOR work, not schema work.

## Decision lines no class cites

DENOMINATOR: 62 document(s) read (3 generated copies excluded); 403 decision line(s) accepted, 2 rejected; 42 cited by a class, 361 cited by none.

An uncited line is a decision the record holds that no class points at.
Most decide something that is not one class (a tenet, a naming rule, a
field). If one decides a class's disposition, that class should cite it.

- sync configuration amendment 1. "TEAM-SIGN-OFF [sync configuration amendment 1]" (did_v2_clock_alignment_cluster_plan.md:638).
- data_body. "TEAM-SIGN-OFF [data_body]: jess@walthamdatascience.com /" (did_v2_data_body_model_plan.md:673).
- data_body amendment 4. "TEAM-SIGN-OFF [data_body amendment 4]" (did_v2_data_body_model_plan.md:1285).
- data_body amendment 3. "TEAM-SIGN-OFF [data_body amendment 3]" (did_v2_data_body_model_plan.md:1323).
- data_type only for plain arrays. "Decided by Jess Haley, 2026-10-21 [data_type only for plain" (did_v2_data_body_model_plan.md:1341).
- data_body amendment 5. "TEAM-SIGN-OFF [data_body amendment 5]" (did_v2_data_body_model_plan.md:1396).
- sorter output by location. "Decided by Jess Haley, 2026-10-21 [sorter output by" (did_v2_data_body_model_plan.md:1400).
- format is an ontology term. "Decided by Jess Haley, 2026-10-14 [format is an ontology" (did_v2_data_body_model_plan.md:1402).
- NDI binary format. "Decided by Jess Haley, 2026-10-22 [NDI binary format]: the" (did_v2_data_body_model_plan.md:1404).
- covariates. "Decided by Jess Haley, 2026-10-22 [covariates]" (did_v2_data_body_model_plan.md:1473).
- conditions stay on the statement. "Decided by Jess Haley, 2026-10-22 [conditions stay on the" (did_v2_data_body_model_plan.md:1475).
- along by index. "Decided by Jess Haley, 2026-10-22 [along by index]" (did_v2_data_body_model_plan.md:1477).
- matrix covariate. "Decided by Jess Haley, 2026-10-22 [matrix covariate]: a" (did_v2_data_body_model_plan.md:1479).
- onset time. "Decided by Jess Haley, 2026-10-22 [onset time]: a stimulus" (did_v2_data_body_model_plan.md:1481).
- no complete. "Decided by Jess Haley, 2026-10-22 [no complete]" (did_v2_data_body_model_plan.md:1483).
- bare dimension. "Decided by Jess Haley, 2026-10-22 [bare dimension]: a" (did_v2_data_body_model_plan.md:1485).
- epoch covariates. "Decided by Jess Haley, 2026-10-22 [epoch covariates]" (did_v2_data_body_model_plan.md:1487).
- tenets follow covariates. "Decided by Jess Haley, 2026-10-22 [tenets follow" (did_v2_data_body_model_plan.md:1489).
- covariate terms. "Decided by Jess Haley, 2026-10-22 [covariate terms]: terms" (did_v2_data_body_model_plan.md:1491).
- presentation dimension term. "Decided by Jess Haley, 2026-10-22 [presentation dimension" (did_v2_data_body_model_plan.md:1495).
- onset and offset terms. "Decided by Jess Haley, 2026-10-22 [onset and offset terms]" (did_v2_data_body_model_plan.md:1497).
- row term deferred. "Decided by Jess Haley, 2026-10-22 [row term deferred]: the" (did_v2_data_body_model_plan.md:1499).
- tuning grid. "Decided by Jess Haley, 2026-10-22 [tuning grid]: a tuning" (did_v2_data_body_model_plan.md:1501).
- covariate details. "Decided by Jess Haley, 2026-10-22 [covariate details]" (did_v2_data_body_model_plan.md:1503).
- covariate rules named. "Decided by Jess Haley, 2026-10-22 [covariate rules named]" (did_v2_data_body_model_plan.md:1505).
- stimulus condition term. "Decided by Jess Haley, 2026-10-22 [stimulus condition" (did_v2_data_body_model_plan.md:1507).
- index covariates. "Decided by Jess Haley, 2026-10-22 [index covariates]: a" (did_v2_data_body_model_plan.md:1509).
- units bound. "Decided by Jess Haley, 2026-10-22 [units bound]" (did_v2_data_body_model_plan.md:1513).
- remaining units bound. "Decided by Jess Haley, 2026-10-22 [remaining units bound]" (did_v2_data_body_model_plan.md:1515).
- logical entries. "Decided by Jess Haley, 2026-10-22 [logical entries]: the" (did_v2_data_body_model_plan.md:1517).
- irradiance. "Decided by Jess Haley, 2026-10-22 [irradiance]: a new" (did_v2_data_body_model_plan.md:1519).
- ratio slots named by unit. "Decided by Jess Haley, 2026-10-22 [ratio slots named by" (did_v2_data_body_model_plan.md:1521).
- missing integers. "Decided by Jess Haley, 2026-10-22 [missing integers]" (did_v2_data_body_model_plan.md:1523).
- audit mechanical fixes 2. "Decided by Jess Haley, 2026-10-22 [audit mechanical fixes" (did_v2_data_body_model_plan.md:1525).
- audit mechanical fixes. "Decided by Jess Haley, 2026-10-22 [audit mechanical fixes]" (did_v2_data_body_model_plan.md:1529).
- harmonic response unit bound. "Decided by Jess Haley, 2026-10-22 [harmonic response unit" (did_v2_data_body_model_plan.md:1531).
- response variable. "Decided by Jess Haley, 2026-10-22 [response variable]: what" (did_v2_data_body_model_plan.md:1533).
- dF/F as variable. "Decided by Jess Haley, 2026-10-22 [dF/F as variable]: dF/F" (did_v2_data_body_model_plan.md:1535).
- response variable nodes. "Decided by Jess Haley, 2026-10-22 [response variable" (did_v2_data_body_model_plan.md:1537).
- unstated response variable. "Decided by Jess Haley, 2026-10-23 [unstated response" (did_v2_data_body_model_plan.md:1539).
- pressure in mmHg. "Decided by Jess Haley, 2026-10-22 [pressure in mmHg]: the" (did_v2_data_body_model_plan.md:1541).
- pH unit one. "Decided by Jess Haley, 2026-10-22 [pH unit one]: the" (did_v2_data_body_model_plan.md:1543).
- pH unit is UO pH. "Decided by Jess Haley, 2026-10-22 [pH unit is UO pH]: the" (did_v2_data_body_model_plan.md:1545).
- humidity in percent. "Decided by Jess Haley, 2026-10-22 [humidity in percent]: the" (did_v2_data_body_model_plan.md:1547).
- unit names are labels. "Decided by Jess Haley, 2026-10-22 [unit names are labels]" (did_v2_data_body_model_plan.md:1549).
- molar kept. "Decided by Jess Haley, 2026-10-22 [molar kept]: the" (did_v2_data_body_model_plan.md:1551).
- exact OM units. "Decided by Jess Haley, 2026-10-22 [exact OM units]: the" (did_v2_data_body_model_plan.md:1553).
- prefixed source units. "Decided by Jess Haley, 2026-10-22 [prefixed source units]" (did_v2_data_body_model_plan.md:1555).
- same_as. "TEAM-SIGN-OFF [same_as]: jess@walthamdatascience.com /" (did_v2_duplicate_entities_plan.md:95).
- spike train leaf. "TEAM-SIGN-OFF [spike train leaf]" (did_v2_ensemble_plan.md:218).
- ensemble retired. "Decided by Jess Haley, 2026-10-22 [ensemble retired]: the" (did_v2_ensemble_plan.md:284).
- no ensemble cache. "Decided by Jess Haley, 2026-10-22 [no ensemble cache]: the" (did_v2_ensemble_plan.md:286).
- 2026-10-08. "TEAM-SIGN-OFF: jess / 2026-10-08 -- statements are a" (did_v2_entity_composition_plan.md:49).
- 2026-10-08. "TEAM-SIGN-OFF: jess / 2026-10-08 -- datum_type is renamed" (did_v2_entity_composition_plan.md:61).
- 2026-10-08. "TEAM-SIGN-OFF: jess / 2026-10-08 -- add the text value kind" (did_v2_entity_composition_plan.md:70).
- 2026-10-08. "TEAM-SIGN-OFF: jess / 2026-10-08 -- one concrete entity" (did_v2_entity_composition_plan.md:116).
- entity type requires, report-only. "Decided by Jess Haley, 2026-10-21 [entity type requires" (did_v2_entity_composition_plan.md:118).
- 2026-10-08. "TEAM-SIGN-OFF: jess / 2026-10-08 -- strain is an" (did_v2_entity_composition_plan.md:129).
- 2026-10-08. "TEAM-SIGN-OFF: jess / 2026-10-08 -- global identifiers are" (did_v2_entity_composition_plan.md:150).
- 2026-10-08. "TEAM-SIGN-OFF: jess / 2026-10-08 -- web_resource and the" (did_v2_entity_composition_plan.md:167).
- 2026-10-19. "TEAM-SIGN-OFF: jess@walthamdatascience.com / 2026-10-19" (did_v2_entity_composition_plan.md:178).
- 2026-10-08. "TEAM-SIGN-OFF: jess / 2026-10-08 -- acquisition_system is" (did_v2_entity_composition_plan.md:190).
- 2026-10-08. "TEAM-SIGN-OFF: jess / 2026-10-08 -- method_parameters" (did_v2_entity_composition_plan.md:197).
- dataset session reference. "Decided by Jess Haley, 2026-10-22 [dataset session" (did_v2_entity_composition_plan.md:209).
- epoch dissolution before merge. "Decided by Jess Haley, 2026-10-22 [epoch dissolution before" (did_v2_epoch_plan.md:1508).
- spike train body by bytes. "Decided by Jess Haley, 2026-10-22 [spike train body by" (did_v2_epoch_plan.md:1510).
- spike dimension term. "Decided by Jess Haley, 2026-10-22 [spike dimension term]" (did_v2_epoch_plan.md:1512).
- JH position and distance. "Decided by Jess Haley, 2026-10-22 [JH position and" (did_v2_epoch_plan.md:1514).
- ingested epochs found. "Decided by Jess Haley, 2026-10-22 [ingested epochs found]" (did_v2_epoch_plan.md:1516).
- JH signed distance in pixels. "Decided by Jess Haley, 2026-10-23 [JH signed distance in" (did_v2_epoch_plan.md:1518).
- JH signed distance in metres. "Decided by Jess Haley, 2026-10-23 [JH signed distance in" (did_v2_epoch_plan.md:1520).
- JH build choices. "Decided by Jess Haley, 2026-10-23 [JH build choices]: the" (did_v2_epoch_plan.md:1522).
- imageStack scale label kept. "Decided by Jess Haley, 2026-10-23 [imageStack scale label" (did_v2_epoch_plan.md:1524).
- filter terms from Wikidata. "Decided by Jess Haley, 2026-10-22 [filter terms from" (did_v2_frequency_filter_model_plan.md:203).
- passband edges paired. "Decided by Jess Haley, 2026-10-22 [passband edges paired]" (did_v2_frequency_filter_model_plan.md:205).
- dataseries_channel_map. "TEAM-SIGN-OFF [dataseries_channel_map]: jess, 2026-08-06" (did_v2_go_forward_class_audit.md:228).
- confirm sheet 2026-08-22. "TEAM-SIGN-OFF [confirm sheet 2026-08-22]" (did_v2_go_forward_class_audit.md:725).
- immersion or dose. "Decided by Jess Haley, 2026-10-21 [immersion or dose]: A" (did_v2_go_forward_class_audit.md:729).
- unrecorded amount is NaN. "Decided by Jess Haley, 2026-10-21 [unrecorded amount is" (did_v2_go_forward_class_audit.md:731).
- prepared material recipe. "Decided by Jess Haley, 2026-10-21 [prepared material" (did_v2_go_forward_class_audit.md:768).
- seeding solution preparation day. "Decided by Jess Haley, 2026-10-21 [seeding solution" (did_v2_go_forward_class_audit.md:780).
- treatment routes by location. "Decided by Jess Haley, 2026-10-21 [treatment routes by" (did_v2_go_forward_class_audit.md:793).
- region parts. "Decided by Jess Haley, 2026-10-21 [region parts]" (did_v2_go_forward_class_audit.md:808).
- laterality on the part. "Decided by Jess Haley, 2026-10-21 [laterality on the part]" (did_v2_go_forward_class_audit.md:810).
- laterality variable. "Decided by Jess Haley, 2026-10-21 [laterality variable]" (did_v2_go_forward_class_audit.md:812).
- anatomy variable terms. "Decided by Jess Haley, 2026-10-21 [anatomy variable terms]" (did_v2_go_forward_class_audit.md:814).
- one part per side. "Decided by Jess Haley, 2026-10-21 [one part per side]" (did_v2_go_forward_class_audit.md:816).
- slice region chain. "Decided by Jess Haley, 2026-10-21 [slice region chain]: a" (did_v2_go_forward_class_audit.md:818).
- region anatomy is UBERON. "Decided by Jess Haley, 2026-10-21 [region anatomy is" (did_v2_go_forward_class_audit.md:820).
- babu-media. "Decided by Jess Haley, 2026-10-21 [babu-media]" (did_v2_go_forward_class_audit.md:852).
- virus-location. "Decided by Jess Haley, 2026-10-21 [virus-location]" (did_v2_go_forward_class_audit.md:865).
- unknown-amount-slot. "Decided by Jess Haley, 2026-10-21 [unknown-amount-slot]" (did_v2_go_forward_class_audit.md:881).
- dose per ingredient. "Decided by Jess Haley, 2026-10-21 [dose per ingredient]" (did_v2_go_forward_class_audit.md:892).
- multiple amount rows. "Decided by Jess Haley, 2026-10-21 [multiple amount rows]" (did_v2_go_forward_class_audit.md:904).
- named-chemical amount on the ingredient. "Decided by Jess Haley, 2026-10-21 [named-chemical amount on" (did_v2_go_forward_class_audit.md:906).
- blank per-body-mass on the ingredient. "Decided by Jess Haley, 2026-10-21 [blank per-body-mass on" (did_v2_go_forward_class_audit.md:908).
- generic treatment number. "Decided by Jess Haley, 2026-10-21 [generic treatment" (did_v2_go_forward_class_audit.md:910).
- treatment onset. "Decided by Jess Haley, 2026-10-21 [treatment onset]: a" (did_v2_go_forward_class_audit.md:912).
- virus injection onset. "Decided by Jess Haley, 2026-10-21 [virus injection onset]" (did_v2_go_forward_class_audit.md:914).
- transfer onset. "Decided by Jess Haley, 2026-10-21 [transfer onset]: a v1" (did_v2_go_forward_class_audit.md:916).
- orientation_direction_tuning.json location. "TEAM-SIGN-OFF [orientation_direction_tuning.json location]" (did_v2_go_forward_class_audit.md:989).
- time anchors, amends the 2026-08-22 confirm sheet. "TEAM-SIGN-OFF [time anchors, amends the 2026-08-22 confirm" (did_v2_go_forward_class_audit.md:1025).
- dimensioned classes, batch confirmation. "TEAM-SIGN-OFF [dimensioned classes, batch confirmation]" (did_v2_go_forward_class_audit.md:1027).
- sorter input. "Decided by Jess Haley, 2026-10-21 [sorter input]" (did_v2_go_forward_class_audit.md:1047).
- sorter keys. "Decided by Jess Haley, 2026-10-21 [sorter keys]" (did_v2_go_forward_class_audit.md:1049).
- migrated masks are logical. "Decided by Jess Haley, 2026-10-22 [migrated masks are" (did_v2_go_forward_class_audit.md:1051).
- sorter software. "Decided by Jess Haley, 2026-10-22 [sorter software]: a" (did_v2_go_forward_class_audit.md:1053).
- migrated masks have no software. "Decided by Jess Haley, 2026-10-22 [migrated masks have no" (did_v2_go_forward_class_audit.md:1057).
- encounter axis. "Decided by Jess Haley, 2026-10-22 [encounter axis]: a Haley" (did_v2_go_forward_class_audit.md:1059).
- software dedup after pass one. "Decided by Jess Haley, 2026-10-22 [software dedup after" (did_v2_go_forward_class_audit.md:1061).
- software location. "Decided by Jess Haley, 2026-10-22 [software location]" (did_v2_go_forward_class_audit.md:1065).
- object software scope. "Decided by Jess Haley, 2026-10-22 [object software scope]" (did_v2_go_forward_class_audit.md:1067).
- NDI ref fallback. "Decided by Jess Haley, 2026-10-22 [NDI ref fallback]" (did_v2_go_forward_class_audit.md:1069).
- NDI ref fallback, test-corpus. "Decided by Jess Haley, 2026-10-22 [NDI ref fallback" (did_v2_go_forward_class_audit.md:1071).
- epoch to system link. "Decided by Jess Haley, 2026-10-22 [epoch to system link]" (did_v2_go_forward_class_audit.md:1076).
- channel types. "Decided by Jess Haley, 2026-10-22 [channel types]" (did_v2_go_forward_class_audit.md:1078).
- required acquisition edges. "Decided by Jess Haley, 2026-10-22 [required acquisition" (did_v2_go_forward_class_audit.md:1080).
- instrument and device. "Decided by Jess Haley, 2026-10-22 [instrument and device]" (did_v2_go_forward_class_audit.md:1082).
- rig minting with edges. "Decided by Jess Haley, 2026-10-22 [rig minting with edges]" (did_v2_go_forward_class_audit.md:1084).
- generic_file emitted set. "Decided by Jess Haley, 2026-10-23 [generic_file emitted" (did_v2_go_forward_class_audit.md:1086).
- v1 passthroughs accepted. "Decided by Jess Haley, 2026-10-23 [v1 passthroughs" (did_v2_go_forward_class_audit.md:1088).
- sliceTetanus stays in NDI. "Decided by Jess Haley, 2026-10-23 [sliceTetanus stays in" (did_v2_go_forward_class_audit.md:1090).
- confirm sheet matches. "Decided by Jess Haley, 2026-10-23 [confirm sheet matches]" (did_v2_go_forward_class_audit.md:1092).
- sibling lock. "Decided by Jess Haley, 2026-10-23 [sibling lock]" (did_v2_go_forward_class_audit.md:1094).
- migration not generalizable. "Decided by Jess Haley, 2026-10-23 [migration not" (did_v2_go_forward_class_audit.md:1096).
- migration kept. "Decided by Jess Haley, 2026-10-24 [migration kept]" (did_v2_go_forward_class_audit.md:1098).
- v1 import stages. "Decided by Jess Haley, 2026-10-24 [v1 import stages]: V2" (did_v2_go_forward_class_audit.md:1100).
- optional additions. "Decided by Jess Haley, 2026-10-24 [optional additions]" (did_v2_go_forward_class_audit.md:1102).
- V_delta removed. "Decided by Jess Haley, 2026-10-23 [V_delta removed]" (did_v2_go_forward_class_audit.md:1106).
- v1 read as stored. "Decided by Jess Haley, 2026-10-23 [v1 read as stored]" (did_v2_go_forward_class_audit.md:1108).
- cloud migrate refuses. "Decided by Jess Haley, 2026-10-23 [cloud migrate refuses]" (did_v2_go_forward_class_audit.md:1110).
- V2 stamp. "Decided by Jess Haley, 2026-10-23 [V2 stamp]" (did_v2_go_forward_class_audit.md:1112).
- #112 superseded. "Decided by Jess Haley, 2026-10-24 [#112 superseded]: (" (did_v2_go_forward_class_audit.md:1114).
- image_collection retired. "Decided by Jess Haley, 2026-10-24 [image_collection" (did_v2_go_forward_class_audit.md:1116).
- V2 builder refuses retired. "Decided by Jess Haley, 2026-10-24 [V2 builder refuses" (did_v2_go_forward_class_audit.md:1118).
- warn on v1 open. "Decided by Jess Haley, 2026-10-23 [warn on v1 open]: (answer" (did_v2_go_forward_class_audit.md:1120).
- compat write layer removed. "Decided by Jess Haley, 2026-10-23 [compat write layer" (did_v2_go_forward_class_audit.md:1122).
- passthrough stays v1. "Decided by Jess Haley, 2026-10-24 [passthrough stays v1]: (" (did_v2_go_forward_class_audit.md:1124).
- passthrough stays v1: how. "Decided by Jess Haley, 2026-10-24 [passthrough stays v1" (did_v2_go_forward_class_audit.md:1126).
- document stamps. "Decided by Jess Haley, 2026-10-25 [document stamps]: (" (did_v2_go_forward_class_audit.md:1128).
- V_eta stamp not accepted. "Decided by Jess Haley, 2026-10-25 [V_eta stamp not" (did_v2_go_forward_class_audit.md:1130).
- termNumberKind is per-dataset. "Decided by Jess Haley, 2026-10-25 [termNumberKind is" (did_v2_go_forward_class_audit.md:1132).
- WBStrain prefix is generic. "Decided by Jess Haley, 2026-10-25 [WBStrain prefix is" (did_v2_go_forward_class_audit.md:1134).
- generic stage is lossless. "Decided by Jess Haley, 2026-10-25 [generic stage is" (did_v2_go_forward_class_audit.md:1136).
- subject local identifier is an identifier. "Decided by Jess Haley, 2026-10-25 [subject local identifier" (did_v2_go_forward_class_audit.md:1138).
- NewStim recipes are a default. "Decided by Jess Haley, 2026-10-25 [NewStim recipes are a" (did_v2_go_forward_class_audit.md:1140).
- no invented values. "Decided by Jess Haley, 2026-10-25 [no invented values]" (did_v2_go_forward_class_audit.md:1142).
- dataset name not invented. "Decided by Jess Haley, 2026-10-25 [dataset name not" (did_v2_go_forward_class_audit.md:1144).
- NDI CI picks DID branch. "Decided by Jess Haley, 2026-10-25 [NDI CI picks DID" (did_v2_go_forward_class_audit.md:1146).
- merge when green. "Decided by Jess Haley, 2026-10-25 [merge when green]: (" (did_v2_go_forward_class_audit.md:1148).
- partly placed is carried as v1. "Decided by Jess Haley, 2026-10-25 [partly placed is carried" (did_v2_go_forward_class_audit.md:1150).
- sliceTetanus to Dab map. "Decided by Jess Haley, 2026-10-25 [sliceTetanus to Dab" (did_v2_go_forward_class_audit.md:1152).
- Soph paused. "Decided by Jess Haley, 2026-10-25 [Soph paused]: (" (did_v2_go_forward_class_audit.md:1154).
- lossless first, homes after. "Decided by Jess Haley, 2026-10-25 [lossless first, homes" (did_v2_go_forward_class_audit.md:1156).
- hartley method implied. "Decided by Jess Haley, 2026-10-25 [hartley method implied]" (did_v2_go_forward_class_audit.md:1158).
- schema set renamed did_v2. "Decided by Jess Haley, 2026-10-25 [schema set renamed" (did_v2_go_forward_class_audit.md:1160).
- pyramid type kept as text. "Decided by Jess Haley, 2026-10-25 [pyramid type kept as" (did_v2_go_forward_class_audit.md:1162).
- no-source pyramid carried as v1. "Decided by Jess Haley, 2026-10-25 [no-source pyramid" (did_v2_go_forward_class_audit.md:1164).
- one free-text field: notes. "Decided by Jess Haley, 2026-10-25 [one free-text field" (did_v2_go_forward_class_audit.md:1166).
- no-source pyramid gets a file-less store body. "Decided by Jess Haley, 2026-10-25 [no-source pyramid gets a" (did_v2_go_forward_class_audit.md:1168).
- notes on three classes. "Decided by Jess Haley, 2026-10-25 [notes on three classes]" (did_v2_go_forward_class_audit.md:1170).
- retired classes leave V2. "Decided by Jess Haley, 2026-10-25 [retired classes leave" (did_v2_go_forward_class_audit.md:1172).
- v1 set in did-schema. "Decided by Jess Haley, 2026-10-25 [v1 set in did-schema]: (" (did_v2_go_forward_class_audit.md:1174).
- markdown out of schemas. "Decided by Jess Haley, 2026-10-25 [markdown out of" (did_v2_go_forward_class_audit.md:1176).
- neuron derived from its sorting run. "Decided by Jess Haley, 2026-10-25 [neuron derived from its" (did_v2_go_forward_class_audit.md:1178).
- session membership records linked or ingested. "Decided by Jess Haley, 2026-10-25 [session membership" (did_v2_go_forward_class_audit.md:1180).
- dataset form terms. "Decided by Jess Haley, 2026-10-25 [dataset form terms]: (" (did_v2_go_forward_class_audit.md:1182).
- presentation app is software. "Decided by Jess Haley, 2026-10-26 [presentation app is" (did_v2_go_forward_class_audit.md:1184).
- control selection on the presentation method. "Decided by Jess Haley, 2026-10-26 [control selection on the" (did_v2_go_forward_class_audit.md:1186).
- lossless means round trip. "Decided by Jess Haley, 2026-10-26 [lossless means round" (did_v2_go_forward_class_audit.md:1188).
- hartley leftovers checked. "Decided by Jess Haley, 2026-10-26 [hartley leftovers" (did_v2_go_forward_class_audit.md:1190).
- restated values checked. "Decided by Jess Haley, 2026-10-26 [restated values" (did_v2_go_forward_class_audit.md:1192).
- image file details placed. "Decided by Jess Haley, 2026-10-26 [image file details" (did_v2_go_forward_class_audit.md:1194).
- probe contact geometry carried. "Decided by Jess Haley, 2026-10-26 [probe contact geometry" (did_v2_go_forward_class_audit.md:1196).
- small unread settings. "Decided by Jess Haley, 2026-10-26 [small unread settings]: (" (did_v2_go_forward_class_audit.md:1198).
- carry register. "Decided by Jess Haley, 2026-10-26 [carry register]: (" (did_v2_go_forward_class_audit.md:1200).
- compression block and empty levels. "Decided by Jess Haley, 2026-10-26 [compression block and" (did_v2_go_forward_class_audit.md:1202).
- spelling is notation. "Decided by Jess Haley, 2026-10-26 [spelling is notation]: (" (did_v2_go_forward_class_audit.md:1204).
- Haley logic leaves the generic migration. "Decided by Jess Haley, 2026-10-26 [Haley logic leaves the" (did_v2_go_forward_class_audit.md:1206).
- dataset-specific logic leaves the generic migration. "Decided by Jess Haley, 2026-10-26 [dataset-specific logic" (did_v2_go_forward_class_audit.md:1208).
- site scaffolding not a loss. "Decided by Jess Haley, 2026-10-26 [site scaffolding not a" (did_v2_go_forward_class_audit.md:1210).
- table rows into the dataset audit. "Decided by Jess Haley, 2026-10-26 [table rows into the" (did_v2_go_forward_class_audit.md:1212).
- device clocks on one epoch. "Decided by Jess Haley, 2026-10-26 [device clocks on one" (did_v2_go_forward_class_audit.md:1214).
- clock terms get nodes. "Decided by Jess Haley, 2026-10-26 [clock terms get nodes]: (" (did_v2_go_forward_class_audit.md:1216).
- writer default is not set. "Decided by Jess Haley, 2026-10-26 [writer default is not" (did_v2_go_forward_class_audit.md:1218).
- one correct reading. "Decided by Jess Haley, 2026-10-26 [one correct reading]: (" (did_v2_go_forward_class_audit.md:1220).
- run environment on interactions. "Decided by Jess Haley, 2026-10-26 [run environment on" (did_v2_go_forward_class_audit.md:1222).
- control pairing is a calculation. "Decided by Jess Haley, 2026-10-26 [control pairing is a" (did_v2_go_forward_class_audit.md:1224).
- census terms. "Decided by Jess Haley, 2026-10-26 [census terms]: (" (did_v2_go_forward_class_audit.md:1226).
- dataset audit batch 1 and 2. "Decided by Jess Haley, 2026-10-26 [dataset audit batch 1" (did_v2_go_forward_class_audit.md:1228).
- term-stated unit is generic. "Decided by Jess Haley, 2026-10-26 [term-stated unit is" (did_v2_go_forward_class_audit.md:1230).
- software_id is what produced the statement. "Decided by Jess Haley, 2026-10-26 [software_id is what" (did_v2_go_forward_class_audit.md:1232).
- stimulus_presentation retired. "Decided by Jess Haley, 2026-10-26 [stimulus_presentation" (did_v2_go_forward_class_audit.md:1234).
- ingested stimulus file is a body of the presentation. "Decided by Jess Haley, 2026-10-26 [ingested stimulus file" (did_v2_go_forward_class_audit.md:1236).
- one-reading quick answers. "Decided by Jess Haley, 2026-10-26 [one-reading quick" (did_v2_go_forward_class_audit.md:1238).
- carry register kinds. "Decided by Jess Haley, 2026-10-26 [carry register kinds]: (" (did_v2_go_forward_class_audit.md:1240).
- awaiting home is tracked. "Decided by Jess Haley, 2026-10-26 [awaiting home is" (did_v2_go_forward_class_audit.md:1242).
- dataset map edits V2. "Decided by Jess Haley, 2026-10-26 [dataset map edits V2]: (" (did_v2_go_forward_class_audit.md:1244).
- dataset map location. "Decided by Jess Haley, 2026-10-26 [dataset map location]: (" (did_v2_go_forward_class_audit.md:1246).
- no Haley map. "Decided by Jess Haley, 2026-10-26 [no Haley map]: (" (did_v2_go_forward_class_audit.md:1248).
- map rows match exact values. "Decided by Jess Haley, 2026-10-26 [map rows match exact" (did_v2_go_forward_class_audit.md:1250).
- opto target without a run. "Decided by Jess Haley, 2026-10-26 [opto target without a" (did_v2_go_forward_class_audit.md:1252).
- fraction value kind. "Decided by Jess Haley, 2026-10-26 [fraction value kind]: (" (did_v2_go_forward_class_audit.md:1254).
- migrators read raw v1. "Decided by Jess Haley, 2026-10-26 [migrators read raw v1]: (" (did_v2_go_forward_class_audit.md:1256).
- renames carry is temporary. "Decided by Jess Haley, 2026-10-26 [renames carry is" (did_v2_go_forward_class_audit.md:1258).
- early migration pieces fixed. "Decided by Jess Haley, 2026-10-26 [early migration pieces" (did_v2_go_forward_class_audit.md:1260).
- migration reliability practices. "Decided by Jess Haley, 2026-10-26 [migration reliability" (did_v2_go_forward_class_audit.md:1262).
- carry register kinds 2. "Decided by Jess Haley, 2026-10-26 [carry register kinds 2]" (did_v2_go_forward_class_audit.md:1264).
- unnamed groups named by the map. "Decided by Jess Haley, 2026-10-26 [unnamed groups named by" (did_v2_go_forward_class_audit.md:1266).
- vehicle rate needs a map. "Decided by Jess Haley, 2026-10-26 [vehicle rate needs a" (did_v2_go_forward_class_audit.md:1268).
- second measurement value needs a map. "Decided by Jess Haley, 2026-10-26 [second measurement value" (did_v2_go_forward_class_audit.md:1270).
- ingested session membership. "Decided by Jess Haley, 2026-10-26 [ingested session" (did_v2_go_forward_class_audit.md:1272).
- data_limits not a pair is malformed. "Decided by Jess Haley, 2026-10-26 [data_limits not a pair" (did_v2_go_forward_class_audit.md:1274).
- pass-through filter sample frequency. "Decided by Jess Haley, 2026-10-26 [pass-through filter" (did_v2_go_forward_class_audit.md:1276).
- untied epochs keep the session anchor. "Decided by Jess Haley, 2026-10-26 [untied epochs keep the" (did_v2_go_forward_class_audit.md:1278).
- sorted units are cells or groups. "Decided by Jess Haley, 2026-10-26 [sorted units are cells" (did_v2_go_forward_class_audit.md:1280).
- unlabelled units need a map. "Decided by Jess Haley, 2026-10-26 [unlabelled units need a" (did_v2_go_forward_class_audit.md:1282).
- element types have no default. "Decided by Jess Haley, 2026-10-26 [element types have no" (did_v2_go_forward_class_audit.md:1284).
- dependents of a carried document carry. "Decided by Jess Haley, 2026-10-26 [dependents of a carried" (did_v2_go_forward_class_audit.md:1286).
- electrode spellings and imaging types are devices. "Decided by Jess Haley, 2026-10-26 [electrode spellings and" (did_v2_go_forward_class_audit.md:1288).
- event lines and environment probes are devices. "Decided by Jess Haley, 2026-10-26 [event lines and" (did_v2_go_forward_class_audit.md:1290).
- migrator writes the registry spelling. "Decided by Jess Haley, 2026-10-26 [migrator writes the" (did_v2_go_forward_class_audit.md:1292).
- location carries need a map. "Decided by Jess Haley, 2026-10-26 [location carries need a" (did_v2_go_forward_class_audit.md:1294).
- presentation outside the batch needs a map. "Decided by Jess Haley, 2026-10-26 [presentation outside the" (did_v2_go_forward_class_audit.md:1296).
- missing is_linked is malformed. "Decided by Jess Haley, 2026-10-26 [missing is_linked is" (did_v2_go_forward_class_audit.md:1298).
- term labels stay as the ontology spells them. "Decided by Jess Haley, 2026-10-26 [term labels stay as the" (did_v2_go_forward_class_audit.md:1300).
- element local identifier is name and reference. "Decided by Jess Haley, 2026-10-26 [element local identifier" (did_v2_go_forward_class_audit.md:1302).
- bath is two statements. "Decided by Jess Haley, 2026-10-26 [bath is two statements]" (did_v2_go_forward_class_audit.md:1304).
- chooseLevel skips empty levels. "Decided by Jess Haley, 2026-10-26 [chooseLevel skips empty" (did_v2_go_forward_class_audit.md:1306).
- ingested stimulus reader finds the body. "Decided by Jess Haley, 2026-10-26 [ingested stimulus reader" (did_v2_go_forward_class_audit.md:1308).
- markdown cleanup and rename. "Decided by Jess Haley, 2026-10-26 [markdown cleanup and" (did_v2_go_forward_class_audit.md:1310).
- pipeline defects are not carries. "Decided by Jess Haley, 2026-10-26 [pipeline defects are not" (did_v2_go_forward_class_audit.md:1312).
- unresolved recorded elements make a standalone item. "Decided by Jess Haley, 2026-10-26 [unresolved recorded" (did_v2_go_forward_class_audit.md:1314).
- extra field on an ingested stimulus file is malformed. "Decided by Jess Haley, 2026-10-26 [extra field on an" (did_v2_go_forward_class_audit.md:1316).
- NaN control means no control. "Decided by Jess Haley, 2026-10-26 [NaN control means no" (did_v2_go_forward_class_audit.md:1318).
- conflicting animal records need a map. "Decided by Jess Haley, 2026-10-26 [conflicting animal" (did_v2_go_forward_class_audit.md:1320).
- method terms are general. "Decided by Jess Haley, 2026-10-26 [method terms are" (did_v2_go_forward_class_audit.md:1322).
- Naka-Rushton is one function. "Decided by Jess Haley, 2026-10-26 [Naka-Rushton is one" (did_v2_go_forward_class_audit.md:1324).
- fields outside the template are malformed. "Decided by Jess Haley, 2026-10-27 [fields outside the" (did_v2_go_forward_class_audit.md:1326).
- probe location terms. "Decided by Jess Haley, 2026-10-27 [probe location terms]: (" (did_v2_go_forward_class_audit.md:1328).
- ngrid block into sampled_body. "Decided by Jess Haley, 2026-10-23 [ngrid block into" (did_v2_image_model_plan.md:226).
- 2026-10-09. "TEAM-SIGN-OFF: jess / 2026-10-09 -- membership of a session" (did_v2_linked_session_plan.md:95).
- linked_session withdrawn. "Decided by Jess Haley, 2026-10-25 [linked_session" (did_v2_linked_session_plan.md:97).
- nested studies. "Decided by Jess Haley, 2026-10-23 [nested studies]: a study" (did_v2_linked_session_plan.md:99).
- parameter unit, #73 audit 2 D4. "TEAM-SIGN-OFF [parameter unit, #73 audit 2 D4]" (did_v2_method_parameters_plan.md:862).
- method. "TEAM-SIGN-OFF [method]: jess@walthamdatascience.com /" (did_v2_method_plan.md:188).
- non-grating stimuli as methods. "Decided by Jess Haley, 2026-10-21 [non-grating stimuli as" (did_v2_method_plan.md:190).
- flashed bar. "Decided by Jess Haley, 2026-10-22 [flashed bar]: a NewStim" (did_v2_method_plan.md:192).
- shape movie note. "Decided by Jess Haley, 2026-10-22 [shape movie note]: a" (did_v2_method_plan.md:194).
- Hartley without enumeration. "Decided by Jess Haley, 2026-10-22 [Hartley without" (did_v2_method_plan.md:196).
- spatial phase in degrees. "Decided by Jess Haley, 2026-10-22 [spatial phase in" (did_v2_method_plan.md:198).
- flashed bar parent. "Decided by Jess Haley, 2026-10-22 [flashed bar parent]" (did_v2_method_plan.md:200).
- method shared plus own. "Decided by Jess Haley, 2026-10-22 [method shared plus own]" (did_v2_method_plan.md:206).
- rules and clock_alignment tenet. "Decided by Jess Haley, 2026-10-22 [rules and" (did_v2_method_plan.md:208).
- receptive field naming. "TEAM-SIGN-OFF [receptive field naming]" (did_v2_ngrid_family_findings.md:381).
- hartley method implied. "Decided by Jess Haley, 2026-10-21 [hartley method implied]" (did_v2_ngrid_family_findings.md:419).
- 2026-08-05. "TEAM-SIGN-OFF: jess, 2026-08-05 -- strain is an entity with" (did_v2_openminds_family_record.md:20).
- subject keeps only its own strain. "Decided by Jess Haley, 2026-10-21 [subject keeps only its" (did_v2_openminds_family_record.md:1329).
- shared entities at dataset level. "Decided by Jess Haley, 2026-10-21 [shared entities at" (did_v2_openminds_family_record.md:1333).
- prefix spelling. "TEAM-SIGN-OFF [prefix spelling]" (did_v2_prefix_spelling_plan.md:202).
- spike trains as epoch bodies. "Decided by Jess Haley, 2026-10-21 [spike trains as epoch" (did_v2_recording_observation_plan.md:117).
- spike train variable. "Decided by Jess Haley, 2026-10-21 [spike train variable]: a" (did_v2_recording_observation_plan.md:119).
- ingested epoch documents retired. "Decided by Jess Haley, 2026-10-21 [ingested epoch documents" (did_v2_recording_observation_plan.md:121).
- archive compression. "Decided by Jess Haley, 2026-10-21 [archive compression]: a" (did_v2_recording_observation_plan.md:123).
- ingested epochs use the archive. "Decided by Jess Haley, 2026-10-21 [ingested epochs use the" (did_v2_recording_observation_plan.md:125).
- pyraview levels per epoch. "Decided by Jess Haley, 2026-10-21 [pyraview levels per" (did_v2_recording_observation_plan.md:127).
- pyraview leftovers. "Decided by Jess Haley, 2026-10-21 [pyraview leftovers]" (did_v2_recording_observation_plan.md:129).
- pyraview leftovers, schema form. "Decided by Jess Haley, 2026-10-21 [pyraview leftovers" (did_v2_recording_observation_plan.md:131).
- preview attribution without epoch files. "Decided by Jess Haley, 2026-10-21 [preview attribution" (did_v2_recording_observation_plan.md:165).
- mfdaq archive emitted set. "Decided by Jess Haley, 2026-10-23 [mfdaq archive emitted" (did_v2_recording_observation_plan.md:167).
- relation inheritance. "TEAM-SIGN-OFF [relation inheritance]: jess / 2026-10-21" (did_v2_relation_inheritance_plan.md:113).
- vocabulary nodes. "Decided by Jess Haley, 2026-10-22 [vocabulary nodes]: every" (did_v2_relation_inheritance_plan.md:117).
- member_of endpoints. "Decided by Jess Haley, 2026-10-22 [member_of endpoints]" (did_v2_relation_inheritance_plan.md:121).
- contained_in endpoints. "Decided by Jess Haley, 2026-10-22 [contained_in endpoints]" (did_v2_relation_inheritance_plan.md:123).
- clock alignment relation bound. "Decided by Jess Haley, 2026-10-22 [clock alignment relation" (did_v2_relation_inheritance_plan.md:125).
- distance. "Decided by Jess Haley, 2026-10-22 [distance]" (did_v2_relation_inheritance_plan.md:127).
- derived from general. "Decided by Jess Haley, 2026-10-22 [derived from general]" (did_v2_relation_inheritance_plan.md:129).
- derived from label. "Decided by Jess Haley, 2026-10-22 [derived from label]: the" (did_v2_relation_inheritance_plan.md:131).
- lawn in plate. "Decided by Jess Haley, 2026-10-22 [lawn in plate]: a" (did_v2_relation_inheritance_plan.md:133).
- source unit. "TEAM-SIGN-OFF [source unit]: jess / 2026-10-21" (did_v2_source_unit_plan.md:69).
- source unit amendment 1. "TEAM-SIGN-OFF [source unit amendment 1]: jess / 2026-10-21" (did_v2_source_unit_plan.md:84).
- calculation-os-optional. "Decided by Jess Haley, 2026-10-21 [calculation-os-optional]" (did_v2_spatial_transcriptomics_plan.md:286).
- formulation strain ingredient. "TEAM-SIGN-OFF [formulation strain ingredient]" (did_v2_spatial_transcriptomics_plan.md:602).
- ontology image is an observation of its region. "Decided by Jess Haley, 2026-10-21 [ontology image is an" (did_v2_spatial_transcriptomics_plan.md:604).
- non-area image node. "Decided by Jess Haley, 2026-10-21 [non-area image node]: on" (did_v2_spatial_transcriptomics_plan.md:606).
- calculation-software-optional decided. "Decided by Jess Haley, 2026-10-22" (did_v2_spatial_transcriptomics_plan.md:610).
- non-area image node, revisited. "Decided by Jess Haley, 2026-10-22 [non-area image node" (did_v2_spatial_transcriptomics_plan.md:612).
- coordinate system names. "Decided by Jess Haley, 2026-10-22 [coordinate system names]" (did_v2_spatial_transcriptomics_plan.md:614).
- stimulus -- visual_grating_manipulation reconciliation. "TEAM-SIGN-OFF [stimulus -- visual_grating_manipulation" (did_v2_stimulus_model_plan.md:304).
- onsets on the sequence, #73 audit 2 D11. "TEAM-SIGN-OFF [onsets on the sequence, #73 audit 2 D11]" (did_v2_stimulus_model_plan.md:372).
- presentation with no subject. "Decided by Jess Haley, 2026-10-21 [presentation with no" (did_v2_stimulus_model_plan.md:396).
- response parameters as a shared method. "Decided by Jess Haley, 2026-10-21 [response parameters as a" (did_v2_stimulus_response_model_plan.md:608).
- control input told apart by its document. "Decided by Jess Haley, 2026-10-21 [control input told apart" (did_v2_stimulus_response_model_plan.md:610).
- empty response settings. "Decided by Jess Haley, 2026-10-21 [empty response" (did_v2_stimulus_response_model_plan.md:612).
- control record is a calculation. "Decided by Jess Haley, 2026-10-21 [control record is a" (did_v2_stimulus_response_model_plan.md:614).
- presentation times from the file. "Decided by Jess Haley, 2026-10-22 [presentation times from" (did_v2_stimulus_response_model_plan.md:620).
- presentation file declared. "Decided by Jess Haley, 2026-10-22 [presentation file" (did_v2_stimulus_response_model_plan.md:623).
- 2026-09-30. "TEAM-SIGN-OFF: jess / 2026-09-30 -- add the study entity" (did_v2_study_plan.md:21).
- 2026-10-21. "TEAM-SIGN-OFF: jess@walthamdatascience.com / 2026-10-21" (did_v2_study_plan.md:28).
- 2026-09-30. "TEAM-SIGN-OFF: jess / 2026-09-30 -- add the instance_of" (did_v2_study_plan.md:29).
- 2026-09-30. "TEAM-SIGN-OFF: jess / 2026-09-30 -- add the awarded_to" (did_v2_study_plan.md:30).
- 2026-09-30. "TEAM-SIGN-OFF: jess / 2026-09-30 -- add" (did_v2_study_plan.md:31).
- 2026-09-30. "TEAM-SIGN-OFF: jess / 2026-09-30 -- add optional" (did_v2_study_plan.md:40).
- 2026-09-30. "TEAM-SIGN-OFF: jess / 2026-09-30 -- add optional" (did_v2_study_plan.md:41).
- 2026-10-01. "TEAM-SIGN-OFF: jess / 2026-10-01 -- add optional" (did_v2_study_plan.md:50).
- 2026-10-02. "TEAM-SIGN-OFF: jess / 2026-10-02 -- contained_in is timed" (did_v2_study_plan.md:61).
- 2026-10-02. "TEAM-SIGN-OFF: jess / 2026-10-02 -- add optional" (did_v2_study_plan.md:110).
- 2026-10-02. "TEAM-SIGN-OFF: jess / 2026-10-02 -- add optional" (did_v2_study_plan.md:111).
- 2026-10-03. "TEAM-SIGN-OFF: jess / 2026-10-03 -- a formulation may be" (did_v2_study_plan.md:142).
- 2026-10-03. "TEAM-SIGN-OFF: jess / 2026-10-03 -- add optional" (did_v2_study_plan.md:143).
- 2026-10-03. "TEAM-SIGN-OFF: jess / 2026-10-03 -- add the humidity data" (did_v2_study_plan.md:171).
- 2026-10-03. "TEAM-SIGN-OFF: jess / 2026-10-03 -- T14: canonical units" (did_v2_study_plan.md:172).
- 2026-10-03. "TEAM-SIGN-OFF: jess / 2026-10-03 -- add length_calculation" (did_v2_study_plan.md:189).
- 2026-10-04. "TEAM-SIGN-OFF: jess / 2026-10-04 -- timed_sequence becomes" (did_v2_study_plan.md:336).
- 2026-10-04. "TEAM-SIGN-OFF: jess / 2026-10-04 -- tenet audit fixes" (did_v2_study_plan.md:337).
- 2026-10-04. "TEAM-SIGN-OFF: jess / 2026-10-04" (did_v2_study_plan.md:338).
- 2026-10-05. "TEAM-SIGN-OFF: jess / 2026-10-05 -- key_labels_id becomes" (did_v2_study_plan.md:339).
- 2026-10-05. "TEAM-SIGN-OFF: jess / 2026-10-05 -- T2 paragraph on" (did_v2_study_plan.md:340).
- 2026-10-05. "TEAM-SIGN-OFF: jess / 2026-10-05 -- add time_calculation" (did_v2_study_plan.md:341).
- contributor role nodes. "TEAM-SIGN-OFF [contributor role nodes]" (did_v2_study_plan.md:384).
- author order from 0. "Decided by Jess Haley, 2026-10-21 [author order from 0]: a" (did_v2_study_plan.md:386).
- calculator + subject_calculation restructure. "TEAM-SIGN-OFF [calculator + subject_calculation" (did_v2_subject_calculation_plan.md:270).
- observation vs calculation, amends #67. "TEAM-SIGN-OFF [observation vs calculation, amends #67]" (did_v2_subject_calculation_plan.md:369).
- binding governance. "TEAM-SIGN-OFF [binding governance]: jess, 2026-08-10 -- bind" (did_v2_tenet_audit.md:438).
- date dtype. "TEAM-SIGN-OFF [date dtype]: jess@walthamdatascience.com /" (did_v2_tenet_audit.md:521).
- base naming. "TEAM-SIGN-OFF [base naming]: jess@walthamdatascience.com /" (did_v2_tenet_audit.md:525).
- time dtype. "TEAM-SIGN-OFF [time dtype]: jess@walthamdatascience.com /" (did_v2_tenet_audit.md:529).
- tenet amendments 2026-10-21. "TEAM-SIGN-OFF [tenet amendments 2026-10-21], below): one" (did_v2_tenets.md:835).
- tenet amendments 2026-10-20. "TEAM-SIGN-OFF [tenet amendments 2026-10-20]: jess /" (did_v2_tenets.md:1060).
- tenet amendments 2026-10-21. "TEAM-SIGN-OFF [tenet amendments 2026-10-21]" (did_v2_tenets.md:1062).
- tenet T20, group entities. "TEAM-SIGN-OFF [tenet T20, group entities]" (did_v2_tenets.md:1063).
- tenet signature text. "Decided by Jess Haley, 2026-10-22 [tenet signature text]" (did_v2_tenets.md:1065).
- T1 and T5 signed. "Decided by Jess Haley, 2026-10-22 [T1 and T5 signed]: the" (did_v2_tenets.md:1067).
- T2 time-varying property. "Decided by Jess Haley, 2026-10-22 [T2 time-varying" (did_v2_tenets.md:1069).
- ordered inputs. "Decided by Jess Haley, 2026-10-22 [ordered inputs]: T20's" (did_v2_tenets.md:1071).
- tenet stale names. "Decided by Jess Haley, 2026-10-22 [tenet stale names]: the" (did_v2_tenets.md:1073).
- term registry. "TEAM-SIGN-OFF [term registry]: jess@walthamdatascience.com" (did_v2_term_registry_plan.md:31).
- term registry closed value sets. "TEAM-SIGN-OFF [term registry closed value sets]" (did_v2_term_registry_plan.md:151).
- developmental stage. "Decided by Jess Haley, 2026-10-22 [developmental stage]" (did_v2_term_registry_plan.md:180).
- Haley terms general. "Decided by Jess Haley, 2026-10-22 [Haley terms general]" (did_v2_term_registry_plan.md:182).
- region by condition and input. "Decided by Jess Haley, 2026-10-22 [region by condition and" (did_v2_term_registry_plan.md:184).
- serial number. "Decided by Jess Haley, 2026-10-22 [serial number]: a" (did_v2_term_registry_plan.md:186).
- registry holds nodes. "Decided by Jess Haley, 2026-10-22 [registry holds nodes]" (did_v2_term_registry_plan.md:188).
- synonyms. "Decided by Jess Haley, 2026-10-22 [synonyms]: a synonym is" (did_v2_term_registry_plan.md:190).
- ethics assessment to jurisdiction. "Decided by Jess Haley, 2026-10-22 [ethics assessment to" (did_v2_term_registry_plan.md:192).
- time_reference. "TEAM-SIGN-OFF [time_reference]: jess@walthamdatascience.com" (did_v2_time_reference_model_plan.md:468).
- time_reference uniqueness rule. "TEAM-SIGN-OFF [time_reference uniqueness rule]" (did_v2_time_reference_model_plan.md:735).
- epoch and session wall-clock time. "TEAM-SIGN-OFF [epoch and session wall-clock time]" (did_v2_time_reference_model_plan.md:762).
- time_reference end. "TEAM-SIGN-OFF [time_reference end]" (did_v2_time_reference_model_plan.md:797).
- time_reference tolerance. "TEAM-SIGN-OFF [time_reference tolerance]" (did_v2_time_reference_model_plan.md:840).
- time_reference tolerance amendment 1. "TEAM-SIGN-OFF [time_reference tolerance amendment 1]" (did_v2_time_reference_model_plan.md:861).
- tuning_curve composite + tuning_curve_calculation leaf, restructure. "TEAM-SIGN-OFF [tuning_curve composite +" (did_v2_tuning_model_plan.md:144).
- tuning shape, #73 audit 2 amendment. "TEAM-SIGN-OFF [tuning shape, #73 audit 2 amendment]" (did_v2_tuning_model_plan.md:246).
- complex trial responses. "Decided by Jess Haley, 2026-10-21 [complex trial" (did_v2_tuning_model_plan.md:250).
- pooled blank statistics. "Decided by Jess Haley, 2026-10-21 [pooled blank" (did_v2_tuning_model_plan.md:259).
- one fit entry. "Decided by Jess Haley, 2026-10-22 [one fit entry]: there is" (did_v2_tuning_model_plan.md:267).
- significance with results. "Decided by Jess Haley, 2026-10-22 [significance with" (did_v2_tuning_model_plan.md:269).
- calculator units. "Decided by Jess Haley, 2026-10-22 [calculator units]" (did_v2_tuning_model_plan.md:271).
- contrast sensitivity lossless. "Decided by Jess Haley, 2026-10-23 [contrast sensitivity" (did_v2_tuning_model_plan.md:273).
- lightsheet reader questions R1-R6. "TEAM-SIGN-OFF [lightsheet reader questions R1-R6]" (review/73/OPEN_ITEMS.md:349).
- developed_by, hosted_by, distributed_as. "TEAM-SIGN-OFF [developed_by, hosted_by, distributed_as]" (review/73/OPEN_ITEMS.md:362).

## v1 source side (from the coverage ledger)

| disposition | count |
|---|---|
| retire | 76 |
| consumed by migrator (no tombstone) | 30 |
| in_progress | 3 |
| test/demo fixture (non-production) | 2 |
| UNMAPPED (needs a V_eta home) | 2 |
| dissolved → subject | 1 |
| persist | 1 |

### `retire`, but NO MIGRATOR YET -- 2 rows

Marked `retire` in the ledger with **no per-class migrator and no `how`
note**. `retire` reads as settled, so they are counted with the open classes
above -- they are open work. Several hold real data (e.g.
`spike_extraction_parameters` carries filter_type / filter_low /
filter_high / filter_order / filter_ripple).

**THIS PARAGRAPH SAID "so the documents pass through untouched today"
and that was an INFERENCE from `no migrator`, not a measurement.** The
ledger's `migrator` column means "a file in `+migrators_j` / `+migrators`
/ `+migrators_i` is named after this class" -- it says nothing about the
BATCH POST-PASSES in `+did2/+convert`, which consume classes no
per-class migrator touches. Measured now, per row, below.

**This heading used to say "nothing decided" / "no recorded plan", and that
was WRONG** -- it is computed from the LEDGER (disposition + migrator + `how`),
not from whether a decision exists. Checked 2026-08-08: **every one of these
rows is covered by a plan document**, and most are signed. The list means
"no migrator has been written yet", not "nobody has decided". A board that
reports settled work as undecided is the mirror of the failure this board
exists to prevent, and it cost a review pass to notice.

DENOMINATOR: 2 row(s), each searched for its BARE CLASS NAME as a quoted literal in 21 batch post-pass file(s) under `+did2/+convert` (comments stripped).

- `calculator` -- no per-class migrator and no batch post-pass names it; passes through today
- `imageCollection` -- no per-class migrator and no batch post-pass names it; passes through today

