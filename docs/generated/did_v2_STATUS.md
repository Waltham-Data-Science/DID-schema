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
| target classes | 94 |
| settled (persist) | 94 |
| `retire`, file still in the tree (open: delete it once nothing passes through it, [one folder, final classes only]) | 0 |
| **still open (`in_progress`)** | **0** |
| **`retire` with no migrator YET** | **0** |
| **open classes in all** | **0** |
| &nbsp;&nbsp;decided (cites a decision line), awaiting build | 0 |
| &nbsp;&nbsp;**proposed (not decided), awaiting review** | **0** |

| open-class BUILD/PROOF state (derived, see below) | count |
|---|---|
| (a) nothing built (the decision state is a separate column) | 0 |
| (b) built, awaiting corpus proof | 0 |
| (c) corpus: 0 survivors in the corpora read | 0 |
| (?) UNMEASURED -- no build evidence was ever taken | 0 |

## What is actually left on the 0 open classes

`in_progress` is a HAND-WRITTEN DECLARATION: every one of these classes is
open because its hand-written `disposition` in `schemas/registry/did_v2_class_dispositions.json` is
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
| build: migrator files inspected | 501 |
| build: &nbsp;&nbsp;-- of those, per-document migrator | 223 |
| build: &nbsp;&nbsp;-- of those, batch post-pass | 278 |
| build: V_zeta files DELIBERATELY EXCLUDED (`+migrators`, `+migrators_i`, `+migrators_e`) | 0 |
| build: migrator lines inspected | 101460 |
| build: &nbsp;&nbsp;-- of those, per-document migrator | 51119 |
| build: &nbsp;&nbsp;-- of those, batch post-pass | 50341 |
| build: classes queried | 0 |
| build: open classes MINTED as a document class | 0 |
| build: &nbsp;&nbsp;-- open classes minted in a per-document migrator (rows overlap) | 0 |
| build: &nbsp;&nbsp;-- open classes minted in a batch post-pass (rows overlap) | 0 |
| build: of those, discounted (decision retires the class) | 0 |
| build: `document_class` writes whose class name is a VARIABLE | 21 |
| build: &nbsp;&nbsp;-- of those, in a per-document migrator | 2 |
| build: &nbsp;&nbsp;-- of those, in a batch post-pass | 19 |
| corpus: `*-summary.json` reports read | 0 |
| corpus: reports carrying an `unconverted_count` | 0 |
| corpus: documents behind those reports | 0 |
| corpus: corpora named | **NONE** |

**NO CORPUS SURVIVOR DATA.** 0 report(s) were read and 0 of them carry
an `unconverted_count`, so **state (c) cannot be reached by any class in**
**this run** and none is rendered as corpus-proven. A report without that
key measured nothing; its silence is not a zero. Point `--census` at a
directory of corpus reports, or run the DID-matlab corpus gate.

### Where the 0 open classes sit

| state | classes |
|---|---|
| (a) nothing built (the decision state is a separate column) | 0 |
| (b) built, awaiting corpus proof | 0 |
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
| 1 | `b.document_class = struct('class_name', '<class>', ...)` | 33 | 1 | 32 |
| 2 | `b.document_class = classBlock('<class>', {supers})` | 0 | 0 | 0 |
| 3 | `b.document_class.class_name = '<class>';` | 1 | 1 | 0 |
| 4 | `did2.build.statement('<direction>', ..., 'ValueKind', '<kind>')`, `did2.build.document('<class>', ...)` or a fixed-class builder | 104 | 66 | 38 |
| 5 | a wrapper of idiom 4: `jStatement(preBody, '<class>', ...)` | 47 | 47 | 0 |
| - | class name is a VARIABLE -- unresolved here | 21 | 2 | 19 |

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
| `DID-matlab:convert/+roundtrip/daqmetadatareader.m:40` | `CLASS` |
| `DID-matlab:convert/+roundtrip/daqreader.m:40` | `CLASS` |
| `DID-matlab:convert/+roundtrip/daqreader_mfdaq_epochdata_ingested.m:196` | `CLASS;` |
| `DID-matlab:convert/+roundtrip/daqreader_mfdaq_epochdata_ingested.m:229` | `CLASS` |
| `DID-matlab:convert/+roundtrip/daqsystem.m:63` | `CLASS` |
| `DID-matlab:convert/+roundtrip/epochfiles_ingested.m:85` | `CLASS` |
| `DID-matlab:convert/+roundtrip/filenavigator.m:43` | `CLASS` |
| `DID-matlab:convert/+roundtrip/image.m:61` | `CLASS` |
| `DID-matlab:convert/+roundtrip/imageStack.m:122` | `CLASS` |
| `DID-matlab:convert/+roundtrip/private/calcParts.m:154` | `v1Class` |
| `DID-matlab:convert/+roundtrip/private/demoInverse.m:24` | `v1Class` |
| `DID-matlab:convert/+roundtrip/private/methodDocParts.m:79` | `v1Class` |
| `DID-matlab:convert/+roundtrip/private/openmindsInverse.m:96` | `v1Class` |
| `DID-matlab:convert/+roundtrip/stimulus_response_scalar_parameters_basic.m:201` | `CLASS` |
| `DID-matlab:convert/+roundtrip/subjectmeasurement.m:93` | `CLASS` |
| `DID-matlab:convert/+roundtrip/syncgraph.m:40` | `CLASS` |
| `DID-matlab:convert/+roundtrip/syncrule.m:160` | `CLASS` |
| `DID-matlab:convert/resolveEpochProbemap.m:1299` | `kind.className` |
| `DID-matlab:convert/resolveEpochProbemap.m:2130` | `entry.class` |
| `DID-matlab:migrators_j/gene_list_mapping.m:184` | `valueClass` |
| `DID-matlab:migrators_j/treatment.m:166` | `manipulation + kind` |

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

## Proposed (not decided) -- awaiting review

DENOMINATOR: 0 open class(es); 0 cite no decision line that resolves.

None -- every open class cites a decision line that exists.

## Decided, awaiting build -- the open classes

DENOMINATOR: 0 open class(es); 0 cite a decision line that exists. The decision column is the line's own text, not a summary.

## Every decision citation

DENOMINATOR: 73 class(es) cite 86 decision line(s); 0 citation(s) do not resolve. "targets built" counts the class's decided targets present in the built set (a target equal to the class is a passthrough and is not counted).

| class | disposition | targets built | decided in |
|---|---|---|---|
| `app` | no V_eta home, no migrator -- UNVERIFIED | 1 of 1 | [software]. "TEAM-SIGN-OFF [software]: jess, 2026-08-06 -- the" (did_v2_tenet_audit.md:16). |
| `binaryseries_parameters` | consumed by migrator (no tombstone) | 2 of 2 | [misc singletons]. "TEAM-SIGN-OFF [misc singletons]: jess, 2026-08-09" (did_v2_go_forward_class_audit.md:9). |
| `calculator` | no V_eta home, no migrator -- UNVERIFIED | no target recorded | [calculator mixin dropped (#73)]. "TEAM-SIGN-OFF [calculator mixin dropped (#73)]" (did_v2_subject_calculation_plan.md:371). |
| `cellTypeLabels` | consumed by migrator (no tombstone) | 4 of 4 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:584). |
| `control_stimulus_ids` | consumed by migrator (no tombstone) | no target recorded | [control as covariate]. "Decided by Jess Haley, 2026-10-22 [control as covariate]" (did_v2_stimulus_response_model_plan.md:622). |
| `daqmetadatareader` | consumed by migrator (no tombstone) | 1 of 1 | [daq configuration]. "TEAM-SIGN-OFF [daq configuration]" (did_v2_daq_family_decisions.md:489). |
| `daqmetadatareader_epochdata_ingested` | consumed by migrator (no tombstone) | 1 of 1 | [daq ingested payloads]. "TEAM-SIGN-OFF [daq ingested payloads]" (did_v2_ingested_payload_findings.md:276). |
| `daqreader` | consumed by migrator (no tombstone) | 1 of 1 | [daq configuration]. "TEAM-SIGN-OFF [daq configuration]" (did_v2_daq_family_decisions.md:489). |
| `daqreader_epochdata_ingested` | consumed by migrator (no tombstone) | 1 of 1 | [daq ingested payloads]. "TEAM-SIGN-OFF [daq ingested payloads]" (did_v2_ingested_payload_findings.md:276).; [epoch files as data bodies]. "Decided by Jess Haley, 2026-10-21 [epoch files as data" (did_v2_recording_observation_plan.md:115). |
| `daqreader_image_epochdata_ingested` | consumed by migrator (no tombstone) | 3 of 3 | [daq ingested payloads]. "TEAM-SIGN-OFF [daq ingested payloads]" (did_v2_ingested_payload_findings.md:276).; [epoch files as data bodies]. "Decided by Jess Haley, 2026-10-21 [epoch files as data" (did_v2_recording_observation_plan.md:115). |
| `daqreader_mfdaq_epochdata_ingested` | consumed by migrator (no tombstone) | 1 of 1 | [epoch files as data bodies]. "Decided by Jess Haley, 2026-10-21 [epoch files as data" (did_v2_recording_observation_plan.md:115). |
| `daqreader_ndr` | consumed by migrator (no tombstone) | 2 of 2 | [daq configuration]. "TEAM-SIGN-OFF [daq configuration]" (did_v2_daq_family_decisions.md:489). |
| `daqsystem` | consumed by migrator (no tombstone) | 1 of 1 | [daq configuration]. "TEAM-SIGN-OFF [daq configuration]" (did_v2_daq_family_decisions.md:489). |
| `element` | consumed by migrator (no tombstone) | 10 of 10 | [raw recording observation]. "TEAM-SIGN-OFF [raw recording observation]" (did_v2_recording_observation_plan.md:99).; [epoch files as data bodies]. "Decided by Jess Haley, 2026-10-21 [epoch files as data" (did_v2_recording_observation_plan.md:115). |
| `element_epoch` | consumed by migrator (no tombstone) | no target recorded | [epoch]. "TEAM-SIGN-OFF [epoch]: jess@walthamdatascience.com /" (did_v2_epoch_plan.md:884). |
| `ensemble` | UNMAPPED (needs a V_eta home) | 3 of 3 | [ensemble]. "TEAM-SIGN-OFF [ensemble]: jess, 2026-08-06 -- per-neuron" (did_v2_ensemble_plan.md:10). |
| `epochclocktimes` | no V_eta home, no migrator -- UNVERIFIED | 1 of 1 | [epochclocktimes]. "TEAM-SIGN-OFF [epochclocktimes]" (did_v2_time_reference_family_plan.md:181).; [epoch extent -- row #113]. "TEAM-SIGN-OFF [epoch extent -- row #113]" (did_v2_OPEN_WORK.md:878). |
| `epochfiles_ingested` | consumed by migrator (no tombstone) | 1 of 1 | [epoch]. "TEAM-SIGN-OFF [epoch]: jess@walthamdatascience.com /" (did_v2_epoch_plan.md:884).; [epoch files as data bodies]. "Decided by Jess Haley, 2026-10-21 [epoch files as data" (did_v2_recording_observation_plan.md:115). |
| `epochid` | no V_eta home, no migrator -- UNVERIFIED | no target recorded | [epoch]. "TEAM-SIGN-OFF [epoch]: jess@walthamdatascience.com /" (did_v2_epoch_plan.md:884). |
| `fileReference` | consumed by migrator (no tombstone) | 1 of 1 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:584). |
| `filenavigator` | consumed by migrator (no tombstone) | 1 of 1 | [file navigation]. "TEAM-SIGN-OFF [file navigation]: jess, 2026-08-06" (did_v2_daq_family_decisions.md:343). |
| `filter` | no V_eta home, no migrator -- UNVERIFIED | 1 of 1 | [2026-07-30]. "TEAM-SIGN-OFF: jess, 2026-07-30" (did_v2_frequency_filter_model_plan.md:5).; [filters are methods]. "Decided by Jess Haley, 2026-10-22 [filters are methods]" (did_v2_frequency_filter_model_plan.md:201). |
| `fitcurve` | consumed by migrator (no tombstone) | 1 of 1 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:584). |
| `geneExpression` | consumed by migrator (no tombstone) | no target recorded | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:584). |
| `geneList` | consumed by migrator (no tombstone) | 4 of 4 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:584). |
| `geneListMapping` | consumed by migrator (no tombstone) | 5 of 5 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:584). |
| `generic_file` | no V_eta home, no migrator -- UNVERIFIED | 2 of 2 | [stranded sources]. "TEAM-SIGN-OFF [stranded sources]" (did_v2_OPEN_WORK.md:836). |
| `hartley_calc` | consumed by migrator (no tombstone) | 5 of 5 | [receptive field fold]. "TEAM-SIGN-OFF [receptive field fold]" (did_v2_ngrid_family_findings.md:358). |
| `image` | consumed by migrator (no tombstone) | 4 of 4 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:584). |
| `imageCollection` | no V_eta home, no migrator -- UNVERIFIED | no target recorded | [stranded sources]. "TEAM-SIGN-OFF [stranded sources]" (did_v2_OPEN_WORK.md:836).; [carried v1 validates against NDI templates]. "Decided by Jess Haley, 2026-10-27 [carried v1 validates" (did_v2_go_forward_class_audit.md:1504). |
| `imageStack` | consumed by migrator (no tombstone) | 4 of 4 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:584). |
| `imageStack_parameters` | no V_eta home, no migrator -- UNVERIFIED | no target recorded | [image / ngrid]. "TEAM-SIGN-OFF [image / ngrid]: jess@walthamdatascience.com" (did_v2_image_model_plan.md:154). |
| `jrclust_clusters` | consumed by migrator (no tombstone) | 1 of 1 | [confirm sheet 2026-08-17]. "TEAM-SIGN-OFF [confirm sheet 2026-08-17]" (did_v2_go_forward_class_audit.md:723).; [spike-sorter output, amends the 2026-08-17 confirm sheet]. "TEAM-SIGN-OFF [spike-sorter output, amends the 2026-08-17" (did_v2_go_forward_class_audit.md:1023). |
| `kiasort_clusters` | consumed by migrator (no tombstone) | 1 of 1 | [spike-sorter output, amends the 2026-08-17 confirm sheet]. "TEAM-SIGN-OFF [spike-sorter output, amends the 2026-08-17" (did_v2_go_forward_class_audit.md:1023). |
| `kilosort_clusters` | consumed by migrator (no tombstone) | 1 of 1 | [spike-sorter output, amends the 2026-08-17 confirm sheet]. "TEAM-SIGN-OFF [spike-sorter output, amends the 2026-08-17" (did_v2_go_forward_class_audit.md:1023). |
| `lightsheetZarrLevel` | consumed by migrator (no tombstone) | 1 of 1 | [lightsheet migrator points 1-11]. "TEAM-SIGN-OFF [lightsheet migrator points 1-11]" (OPEN_ITEMS.md:317). |
| `lightsheetZarrPyramid` | consumed by migrator (no tombstone) | 3 of 3 | [lightsheet migrator points 1-11]. "TEAM-SIGN-OFF [lightsheet migrator points 1-11]" (OPEN_ITEMS.md:317). |
| `neuron_extracellular` | consumed by migrator (no tombstone) | 7 of 7 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:584). |
| `ngrid` | no V_eta home, no migrator -- UNVERIFIED | no target recorded | [image / ngrid]. "TEAM-SIGN-OFF [image / ngrid]: jess@walthamdatascience.com" (did_v2_image_model_plan.md:154). |
| `ontologyImage` | consumed by migrator (no tombstone) | 4 of 4 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:584). |
| `openminds` | consumed by migrator (no tombstone) | no target recorded | [2026-08-08]. "TEAM-SIGN-OFF: jess, 2026-08-08 -- Part 7: the 3 unattached" (did_v2_openminds_family_record.md:10). |
| `oridirtuning_calc` | consumed by migrator (no tombstone) | 3 of 3 | [confirm sheet 2026-08-17]. "TEAM-SIGN-OFF [confirm sheet 2026-08-17]" (did_v2_go_forward_class_audit.md:723). |
| `probe_geometry` | consumed by migrator (no tombstone) | 3 of 3 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:584). |
| `probe_location` | consumed by migrator (no tombstone) | 2 of 2 | [confirm sheet 2026-08-17]. "TEAM-SIGN-OFF [confirm sheet 2026-08-17]" (did_v2_go_forward_class_audit.md:723). |
| `projectvar` | no V_eta home, no migrator -- UNVERIFIED | no target recorded | [misc singletons]. "TEAM-SIGN-OFF [misc singletons]: jess, 2026-08-09" (did_v2_go_forward_class_audit.md:9).; [carried v1 validates against NDI templates]. "Decided by Jess Haley, 2026-10-27 [carried v1 validates" (did_v2_go_forward_class_audit.md:1504). |
| `purpose` | persist | no target recorded | [misc singletons]. "TEAM-SIGN-OFF [misc singletons]: jess, 2026-08-09" (did_v2_go_forward_class_audit.md:9).; [purpose class]. "Decided by Jess Haley, 2026-10-27 [purpose class]: (" (did_v2_go_forward_class_audit.md:1566). |
| `pyraview` | consumed by migrator (no tombstone) | 1 of 1 | [raw recording observation]. "TEAM-SIGN-OFF [raw recording observation]" (did_v2_recording_observation_plan.md:99).; [pyraview levels, amends the 2026-08-13 pyraview pyramid confirmation]. "TEAM-SIGN-OFF [pyraview levels, amends the 2026-08-13" (did_v2_recording_observation_plan.md:111). |
| `session` | consumed by migrator (no tombstone) | 1 of 1 | [session]. "TEAM-SIGN-OFF [session]: jess@walthamdatascience.com /" (did_v2_go_forward_class_audit.md:664). |
| `sorting_parameters` | consumed by migrator (no tombstone) | 1 of 1 | [spike processing parameters]. "TEAM-SIGN-OFF [spike processing parameters]: jess" (did_v2_method_parameters_plan.md:32). |
| `spatialGeneExpressionCells` | consumed by migrator (no tombstone) | 5 of 5 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:584). |
| `spatialGeneExpressionPyramid` | consumed by migrator (no tombstone) | 5 of 5 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:584). |
| `spatialGeneExpressionROI` | consumed by migrator (no tombstone) | 2 of 2 | [spatial ROI is an outline]. "Decided by Jess Haley, 2026-11-09 [spatial ROI is an" (did_v2_spatial_transcriptomics_plan.md:657). |
| `spatialGeneExpressionTiles` | consumed by migrator (no tombstone) | 1 of 1 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:584). |
| `spike_extraction_parameters` | consumed by migrator (no tombstone) | 1 of 1 | [spike processing parameters]. "TEAM-SIGN-OFF [spike processing parameters]: jess" (did_v2_method_parameters_plan.md:32). |
| `spike_extraction_parameters_modification` | consumed by migrator (no tombstone) | 1 of 1 | [spike processing parameters]. "TEAM-SIGN-OFF [spike processing parameters]: jess" (did_v2_method_parameters_plan.md:32). |
| `stimulus_bath` | consumed by migrator (no tombstone) | 2 of 2 | [bath is a manipulation]. "Decided by Jess Haley, 2026-10-21 [bath is a manipulation]" (did_v2_go_forward_class_audit.md:727). |
| `stimulus_parameter` | consumed by migrator (no tombstone) | no target recorded | [stimulus parameters]. "TEAM-SIGN-OFF [stimulus parameters]" (did_v2_stimulus_parameter_plan.md:221). |
| `stimulus_parameter_table` | no V_eta home, no migrator -- UNVERIFIED | no target recorded | [stimulus parameters]. "TEAM-SIGN-OFF [stimulus parameters]" (did_v2_stimulus_parameter_plan.md:221).; [carried v1 validates against NDI templates]. "Decided by Jess Haley, 2026-10-27 [carried v1 validates" (did_v2_go_forward_class_audit.md:1504). |
| `stimulus_presentation` | consumed by migrator (no tombstone) | 2 of 2 | [stimulus]. "TEAM-SIGN-OFF [stimulus]: jess@walthamdatascience.com /" (did_v2_stimulus_model_plan.md:258). |
| `stimulus_response` | no V_eta home, no migrator -- UNVERIFIED | no target recorded | [stimulus response]. "TEAM-SIGN-OFF [stimulus response]" (did_v2_stimulus_response_model_plan.md:541). |
| `stimulus_response_scalar` | consumed by migrator (no tombstone) | 1 of 1 | [stimulus response]. "TEAM-SIGN-OFF [stimulus response]" (did_v2_stimulus_response_model_plan.md:541). |
| `stimulus_response_scalar_parameters` | no V_eta home, no migrator -- UNVERIFIED | no target recorded | [stimulus response]. "TEAM-SIGN-OFF [stimulus response]" (did_v2_stimulus_response_model_plan.md:541). |
| `stimulus_response_scalar_parameters_basic` | consumed by migrator (no tombstone) | 1 of 1 | [stimulus response]. "TEAM-SIGN-OFF [stimulus response]" (did_v2_stimulus_response_model_plan.md:541). |
| `subject` | consumed by migrator (no tombstone) | 1 of 1 | [subject]. "TEAM-SIGN-OFF [subject]: jess@walthamdatascience.com /" (did_v2_go_forward_class_audit.md:697). |
| `subjectmeasurement` | consumed by migrator (no tombstone) | no target recorded | [subject measurement]. "TEAM-SIGN-OFF [subject measurement]: jess, 2026-08-06" (did_v2_go_forward_class_audit.md:336). |
| `syncgraph` | consumed by migrator (no tombstone) | 1 of 1 | [sync configuration]. "TEAM-SIGN-OFF [sync configuration]" (did_v2_clock_alignment_cluster_plan.md:506). |
| `syncrule` | consumed by migrator (no tombstone) | 1 of 1 | [sync configuration]. "TEAM-SIGN-OFF [sync configuration]" (did_v2_clock_alignment_cluster_plan.md:506). |
| `syncrule_mapping` | consumed by migrator (no tombstone) | 1 of 1 | [sync mapping]. "TEAM-SIGN-OFF [sync mapping]: jess@walthamdatascience.com /" (did_v2_clock_alignment_cluster_plan.md:510). |
| `treatment` | consumed by migrator (no tombstone) | 7 of 7 | [confirm sheet 2026-08-17]. "TEAM-SIGN-OFF [confirm sheet 2026-08-17]" (did_v2_go_forward_class_audit.md:723). |
| `tuningcurve_calc` | consumed by migrator (no tombstone) | 3 of 3 | [confirm sheet 2026-08-17]. "TEAM-SIGN-OFF [confirm sheet 2026-08-17]" (did_v2_go_forward_class_audit.md:723). |
| `valid_interval` | no V_eta home, no migrator -- UNVERIFIED | 1 of 1 | [logical_observation]. "TEAM-SIGN-OFF [logical_observation]" (did_v2_logical_observation_plan.md:365).; [logical_observation amendment 1]. "TEAM-SIGN-OFF [logical_observation amendment 1]" (did_v2_logical_observation_plan.md:425). |
| `vmspikefilteringparameters` | consumed by migrator (no tombstone) | 1 of 1 | [spike processing parameters]. "TEAM-SIGN-OFF [spike processing parameters]: jess" (did_v2_method_parameters_plan.md:32). |
| `vmspikefit` | consumed by migrator (no tombstone) | 1 of 1 | [#73 audit 2, D1-D13]. "TEAM-SIGN-OFF [#73 audit 2, D1-D13]" (did_v2_spatial_transcriptomics_plan.md:586). |

Every decided target these classes name is present in the built set, so
what remains for them is MIGRATOR work, not schema work.

## Decision lines no class cites

DENOMINATOR: 126 document(s) read (3 generated copies excluded); 986 decision line(s) accepted, 2 rejected; 45 cited by a class, 941 cited by none.

An uncited line is a decision the record holds that no class points at.
Most decide something that is not one class (a tenet, a naming rule, a
field). If one decides a class's disposition, that class should cite it.

- lightsheet reader questions R1-R6. "TEAM-SIGN-OFF [lightsheet reader questions R1-R6]" (OPEN_ITEMS.md:349).
- developed_by, hosted_by, distributed_as. "TEAM-SIGN-OFF [developed_by, hosted_by, distributed_as]" (OPEN_ITEMS.md:362).
- sync configuration amendment 1. "TEAM-SIGN-OFF [sync configuration amendment 1]" (did_v2_clock_alignment_cluster_plan.md:640).
- data_body. "TEAM-SIGN-OFF [data_body]: jess@walthamdatascience.com /" (did_v2_data_body_model_plan.md:673).
- data_body amendment 4. "TEAM-SIGN-OFF [data_body amendment 4]" (did_v2_data_body_model_plan.md:1287).
- data_body amendment 3. "TEAM-SIGN-OFF [data_body amendment 3]" (did_v2_data_body_model_plan.md:1325).
- data_type only for plain arrays. "Decided by Jess Haley, 2026-10-21 [data_type only for plain" (did_v2_data_body_model_plan.md:1343).
- data_body amendment 5. "TEAM-SIGN-OFF [data_body amendment 5]" (did_v2_data_body_model_plan.md:1398).
- sorter output by location. "Decided by Jess Haley, 2026-10-21 [sorter output by" (did_v2_data_body_model_plan.md:1402).
- format is an ontology term. "Decided by Jess Haley, 2026-10-14 [format is an ontology" (did_v2_data_body_model_plan.md:1404).
- NDI binary format. "Decided by Jess Haley, 2026-10-22 [NDI binary format]: the" (did_v2_data_body_model_plan.md:1406).
- covariates. "Decided by Jess Haley, 2026-10-22 [covariates]" (did_v2_data_body_model_plan.md:1478).
- conditions stay on the statement. "Decided by Jess Haley, 2026-10-22 [conditions stay on the" (did_v2_data_body_model_plan.md:1480).
- along by index. "Decided by Jess Haley, 2026-10-22 [along by index]" (did_v2_data_body_model_plan.md:1482).
- matrix covariate. "Decided by Jess Haley, 2026-10-22 [matrix covariate]: a" (did_v2_data_body_model_plan.md:1484).
- onset time. "Decided by Jess Haley, 2026-10-22 [onset time]: a stimulus" (did_v2_data_body_model_plan.md:1486).
- no complete. "Decided by Jess Haley, 2026-10-22 [no complete]" (did_v2_data_body_model_plan.md:1488).
- bare dimension. "Decided by Jess Haley, 2026-10-22 [bare dimension]: a" (did_v2_data_body_model_plan.md:1490).
- epoch covariates. "Decided by Jess Haley, 2026-10-22 [epoch covariates]" (did_v2_data_body_model_plan.md:1492).
- tenets follow covariates. "Decided by Jess Haley, 2026-10-22 [tenets follow" (did_v2_data_body_model_plan.md:1494).
- covariate terms. "Decided by Jess Haley, 2026-10-22 [covariate terms]: terms" (did_v2_data_body_model_plan.md:1496).
- presentation dimension term. "Decided by Jess Haley, 2026-10-22 [presentation dimension" (did_v2_data_body_model_plan.md:1500).
- onset and offset terms. "Decided by Jess Haley, 2026-10-22 [onset and offset terms]" (did_v2_data_body_model_plan.md:1502).
- row term deferred. "Decided by Jess Haley, 2026-10-22 [row term deferred]: the" (did_v2_data_body_model_plan.md:1504).
- tuning grid. "Decided by Jess Haley, 2026-10-22 [tuning grid]: a tuning" (did_v2_data_body_model_plan.md:1506).
- covariate details. "Decided by Jess Haley, 2026-10-22 [covariate details]" (did_v2_data_body_model_plan.md:1508).
- covariate rules named. "Decided by Jess Haley, 2026-10-22 [covariate rules named]" (did_v2_data_body_model_plan.md:1510).
- stimulus condition term. "Decided by Jess Haley, 2026-10-22 [stimulus condition" (did_v2_data_body_model_plan.md:1512).
- index covariates. "Decided by Jess Haley, 2026-10-22 [index covariates]: a" (did_v2_data_body_model_plan.md:1514).
- units bound. "Decided by Jess Haley, 2026-10-22 [units bound]" (did_v2_data_body_model_plan.md:1518).
- remaining units bound. "Decided by Jess Haley, 2026-10-22 [remaining units bound]" (did_v2_data_body_model_plan.md:1520).
- logical entries. "Decided by Jess Haley, 2026-10-22 [logical entries]: the" (did_v2_data_body_model_plan.md:1522).
- irradiance. "Decided by Jess Haley, 2026-10-22 [irradiance]: a new" (did_v2_data_body_model_plan.md:1524).
- ratio slots named by unit. "Decided by Jess Haley, 2026-10-22 [ratio slots named by" (did_v2_data_body_model_plan.md:1526).
- missing integers. "Decided by Jess Haley, 2026-10-22 [missing integers]" (did_v2_data_body_model_plan.md:1528).
- audit mechanical fixes 2. "Decided by Jess Haley, 2026-10-22 [audit mechanical fixes" (did_v2_data_body_model_plan.md:1530).
- audit mechanical fixes. "Decided by Jess Haley, 2026-10-22 [audit mechanical fixes]" (did_v2_data_body_model_plan.md:1534).
- harmonic response unit bound. "Decided by Jess Haley, 2026-10-22 [harmonic response unit" (did_v2_data_body_model_plan.md:1536).
- response variable. "Decided by Jess Haley, 2026-10-22 [response variable]: what" (did_v2_data_body_model_plan.md:1538).
- dF/F as variable. "Decided by Jess Haley, 2026-10-22 [dF/F as variable]: dF/F" (did_v2_data_body_model_plan.md:1540).
- response variable nodes. "Decided by Jess Haley, 2026-10-22 [response variable" (did_v2_data_body_model_plan.md:1542).
- unstated response variable. "Decided by Jess Haley, 2026-10-23 [unstated response" (did_v2_data_body_model_plan.md:1544).
- pressure in mmHg. "Decided by Jess Haley, 2026-10-22 [pressure in mmHg]: the" (did_v2_data_body_model_plan.md:1546).
- pH unit one. "Decided by Jess Haley, 2026-10-22 [pH unit one]: the" (did_v2_data_body_model_plan.md:1548).
- pH unit is UO pH. "Decided by Jess Haley, 2026-10-22 [pH unit is UO pH]: the" (did_v2_data_body_model_plan.md:1550).
- humidity in percent. "Decided by Jess Haley, 2026-10-22 [humidity in percent]: the" (did_v2_data_body_model_plan.md:1552).
- unit names are labels. "Decided by Jess Haley, 2026-10-22 [unit names are labels]" (did_v2_data_body_model_plan.md:1554).
- molar kept. "Decided by Jess Haley, 2026-10-22 [molar kept]: the" (did_v2_data_body_model_plan.md:1556).
- exact OM units. "Decided by Jess Haley, 2026-10-22 [exact OM units]: the" (did_v2_data_body_model_plan.md:1558).
- prefixed source units. "Decided by Jess Haley, 2026-10-22 [prefixed source units]" (did_v2_data_body_model_plan.md:1560).
- covariate key. "Decided by Jess Haley, 2026-11-01 [covariate key]: (" (did_v2_data_body_model_plan.md:1564).
- covariate variable may repeat. "Decided by Jess Haley, 2026-11-01 [covariate variable may" (did_v2_data_body_model_plan.md:1566).
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
- epoch dissolution before merge. "Decided by Jess Haley, 2026-10-22 [epoch dissolution before" (did_v2_epoch_plan.md:1510).
- spike train body by bytes. "Decided by Jess Haley, 2026-10-22 [spike train body by" (did_v2_epoch_plan.md:1512).
- spike dimension term. "Decided by Jess Haley, 2026-10-22 [spike dimension term]" (did_v2_epoch_plan.md:1514).
- JH position and distance. "Decided by Jess Haley, 2026-10-22 [JH position and" (did_v2_epoch_plan.md:1516).
- ingested epochs found. "Decided by Jess Haley, 2026-10-22 [ingested epochs found]" (did_v2_epoch_plan.md:1518).
- JH signed distance in pixels. "Decided by Jess Haley, 2026-10-23 [JH signed distance in" (did_v2_epoch_plan.md:1520).
- JH signed distance in metres. "Decided by Jess Haley, 2026-10-23 [JH signed distance in" (did_v2_epoch_plan.md:1522).
- JH build choices. "Decided by Jess Haley, 2026-10-23 [JH build choices]: the" (did_v2_epoch_plan.md:1524).
- imageStack scale label kept. "Decided by Jess Haley, 2026-10-23 [imageStack scale label" (did_v2_epoch_plan.md:1526).
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
- epochid inheritors answered. "Decided by Jess Haley, 2026-11-19 [epochid inheritors" (did_v2_go_forward_class_audit.md:1174).
- v1 set in did-schema. "Decided by Jess Haley, 2026-10-25 [v1 set in did-schema]: (" (did_v2_go_forward_class_audit.md:1176).
- markdown out of schemas. "Decided by Jess Haley, 2026-10-25 [markdown out of" (did_v2_go_forward_class_audit.md:1178).
- neuron derived from its sorting run. "Decided by Jess Haley, 2026-10-25 [neuron derived from its" (did_v2_go_forward_class_audit.md:1180).
- session membership records linked or ingested. "Decided by Jess Haley, 2026-10-25 [session membership" (did_v2_go_forward_class_audit.md:1182).
- dataset form terms. "Decided by Jess Haley, 2026-10-25 [dataset form terms]: (" (did_v2_go_forward_class_audit.md:1184).
- presentation app is software. "Decided by Jess Haley, 2026-10-26 [presentation app is" (did_v2_go_forward_class_audit.md:1186).
- control selection on the presentation method. "Decided by Jess Haley, 2026-10-26 [control selection on the" (did_v2_go_forward_class_audit.md:1188).
- lossless means round trip. "Decided by Jess Haley, 2026-10-26 [lossless means round" (did_v2_go_forward_class_audit.md:1190).
- hartley leftovers checked. "Decided by Jess Haley, 2026-10-26 [hartley leftovers" (did_v2_go_forward_class_audit.md:1192).
- restated values checked. "Decided by Jess Haley, 2026-10-26 [restated values" (did_v2_go_forward_class_audit.md:1194).
- image file details placed. "Decided by Jess Haley, 2026-10-26 [image file details" (did_v2_go_forward_class_audit.md:1196).
- probe contact geometry carried. "Decided by Jess Haley, 2026-10-26 [probe contact geometry" (did_v2_go_forward_class_audit.md:1198).
- small unread settings. "Decided by Jess Haley, 2026-10-26 [small unread settings]: (" (did_v2_go_forward_class_audit.md:1200).
- carry register. "Decided by Jess Haley, 2026-10-26 [carry register]: (" (did_v2_go_forward_class_audit.md:1202).
- compression block and empty levels. "Decided by Jess Haley, 2026-10-26 [compression block and" (did_v2_go_forward_class_audit.md:1204).
- spelling is notation. "Decided by Jess Haley, 2026-10-26 [spelling is notation]: (" (did_v2_go_forward_class_audit.md:1206).
- Haley logic leaves the generic migration. "Decided by Jess Haley, 2026-10-26 [Haley logic leaves the" (did_v2_go_forward_class_audit.md:1208).
- dataset-specific logic leaves the generic migration. "Decided by Jess Haley, 2026-10-26 [dataset-specific logic" (did_v2_go_forward_class_audit.md:1210).
- dataset-specific audit complete. "Decided by Jess Haley, 2026-11-18 [dataset-specific audit" (did_v2_go_forward_class_audit.md:1212).
- site scaffolding not a loss. "Decided by Jess Haley, 2026-10-26 [site scaffolding not a" (did_v2_go_forward_class_audit.md:1214).
- table rows into the dataset audit. "Decided by Jess Haley, 2026-10-26 [table rows into the" (did_v2_go_forward_class_audit.md:1216).
- device clocks on one epoch. "Decided by Jess Haley, 2026-10-26 [device clocks on one" (did_v2_go_forward_class_audit.md:1218).
- clock terms get nodes. "Decided by Jess Haley, 2026-10-26 [clock terms get nodes]: (" (did_v2_go_forward_class_audit.md:1220).
- writer default is not set. "Decided by Jess Haley, 2026-10-26 [writer default is not" (did_v2_go_forward_class_audit.md:1222).
- one correct reading. "Decided by Jess Haley, 2026-10-26 [one correct reading]: (" (did_v2_go_forward_class_audit.md:1224).
- run environment on interactions. "Decided by Jess Haley, 2026-10-26 [run environment on" (did_v2_go_forward_class_audit.md:1226).
- control pairing is a calculation. "Decided by Jess Haley, 2026-10-26 [control pairing is a" (did_v2_go_forward_class_audit.md:1228).
- census terms. "Decided by Jess Haley, 2026-10-26 [census terms]: (" (did_v2_go_forward_class_audit.md:1230).
- dataset audit batch 1 and 2. "Decided by Jess Haley, 2026-10-26 [dataset audit batch 1" (did_v2_go_forward_class_audit.md:1232).
- term-stated unit is generic. "Decided by Jess Haley, 2026-10-26 [term-stated unit is" (did_v2_go_forward_class_audit.md:1234).
- software_id is what produced the statement. "Decided by Jess Haley, 2026-10-26 [software_id is what" (did_v2_go_forward_class_audit.md:1236).
- stimulus_presentation retired. "Decided by Jess Haley, 2026-10-26 [stimulus_presentation" (did_v2_go_forward_class_audit.md:1238).
- ingested stimulus file is a body of the presentation. "Decided by Jess Haley, 2026-10-26 [ingested stimulus file" (did_v2_go_forward_class_audit.md:1240).
- one-reading quick answers. "Decided by Jess Haley, 2026-10-26 [one-reading quick" (did_v2_go_forward_class_audit.md:1242).
- carry register kinds. "Decided by Jess Haley, 2026-10-26 [carry register kinds]: (" (did_v2_go_forward_class_audit.md:1244).
- awaiting home is tracked. "Decided by Jess Haley, 2026-10-26 [awaiting home is" (did_v2_go_forward_class_audit.md:1246).
- dataset map edits V2. "Decided by Jess Haley, 2026-10-26 [dataset map edits V2]: (" (did_v2_go_forward_class_audit.md:1248).
- dataset map location. "Decided by Jess Haley, 2026-10-26 [dataset map location]: (" (did_v2_go_forward_class_audit.md:1250).
- no Haley map. "Decided by Jess Haley, 2026-10-26 [no Haley map]: (" (did_v2_go_forward_class_audit.md:1252).
- map rows match exact values. "Decided by Jess Haley, 2026-10-26 [map rows match exact" (did_v2_go_forward_class_audit.md:1254).
- opto target without a run. "Decided by Jess Haley, 2026-10-26 [opto target without a" (did_v2_go_forward_class_audit.md:1256).
- fraction value kind. "Decided by Jess Haley, 2026-10-26 [fraction value kind]: (" (did_v2_go_forward_class_audit.md:1258).
- migrators read raw v1. "Decided by Jess Haley, 2026-10-26 [migrators read raw v1]: (" (did_v2_go_forward_class_audit.md:1260).
- renames carry is temporary. "Decided by Jess Haley, 2026-10-26 [renames carry is" (did_v2_go_forward_class_audit.md:1262).
- classes without a migrator carry as v1. "Decided by Jess Haley, 2026-10-31 [classes without a" (did_v2_go_forward_class_audit.md:1264).
- early migration pieces fixed. "Decided by Jess Haley, 2026-10-26 [early migration pieces" (did_v2_go_forward_class_audit.md:1266).
- element name and reference kept together. "Decided by Jess Haley, 2026-11-19 [element name and" (did_v2_go_forward_class_audit.md:1268).
- migration reliability practices. "Decided by Jess Haley, 2026-10-26 [migration reliability" (did_v2_go_forward_class_audit.md:1270).
- carry register kinds 2. "Decided by Jess Haley, 2026-10-26 [carry register kinds 2]" (did_v2_go_forward_class_audit.md:1272).
- unnamed groups named by the map. "Decided by Jess Haley, 2026-10-26 [unnamed groups named by" (did_v2_go_forward_class_audit.md:1274).
- vehicle rate needs a map. "Decided by Jess Haley, 2026-10-26 [vehicle rate needs a" (did_v2_go_forward_class_audit.md:1276).
- second measurement value needs a map. "Decided by Jess Haley, 2026-10-26 [second measurement value" (did_v2_go_forward_class_audit.md:1278).
- ingested session membership. "Decided by Jess Haley, 2026-10-26 [ingested session" (did_v2_go_forward_class_audit.md:1280).
- data_limits not a pair is malformed. "Decided by Jess Haley, 2026-10-26 [data_limits not a pair" (did_v2_go_forward_class_audit.md:1282).
- pass-through filter sample frequency. "Decided by Jess Haley, 2026-10-26 [pass-through filter" (did_v2_go_forward_class_audit.md:1284).
- untied epochs keep the session anchor. "Decided by Jess Haley, 2026-10-26 [untied epochs keep the" (did_v2_go_forward_class_audit.md:1286).
- sorted units are cells or groups. "Decided by Jess Haley, 2026-10-26 [sorted units are cells" (did_v2_go_forward_class_audit.md:1288).
- unlabelled units need a map. "Decided by Jess Haley, 2026-10-26 [unlabelled units need a" (did_v2_go_forward_class_audit.md:1290).
- element types have no default. "Decided by Jess Haley, 2026-10-26 [element types have no" (did_v2_go_forward_class_audit.md:1292).
- dependents of a carried document carry. "Decided by Jess Haley, 2026-10-26 [dependents of a carried" (did_v2_go_forward_class_audit.md:1294).
- electrode spellings and imaging types are devices. "Decided by Jess Haley, 2026-10-26 [electrode spellings and" (did_v2_go_forward_class_audit.md:1296).
- event lines and environment probes are devices. "Decided by Jess Haley, 2026-10-26 [event lines and" (did_v2_go_forward_class_audit.md:1298).
- migrator writes the registry spelling. "Decided by Jess Haley, 2026-10-26 [migrator writes the" (did_v2_go_forward_class_audit.md:1300).
- location carries need a map. "Decided by Jess Haley, 2026-10-26 [location carries need a" (did_v2_go_forward_class_audit.md:1302).
- presentation outside the batch needs a map. "Decided by Jess Haley, 2026-10-26 [presentation outside the" (did_v2_go_forward_class_audit.md:1304).
- missing is_linked is malformed. "Decided by Jess Haley, 2026-10-26 [missing is_linked is" (did_v2_go_forward_class_audit.md:1306).
- term labels stay as the ontology spells them. "Decided by Jess Haley, 2026-10-26 [term labels stay as the" (did_v2_go_forward_class_audit.md:1308).
- element local identifier is name and reference. "Decided by Jess Haley, 2026-10-26 [element local identifier" (did_v2_go_forward_class_audit.md:1310).
- bath is two statements. "Decided by Jess Haley, 2026-10-26 [bath is two statements]" (did_v2_go_forward_class_audit.md:1312).
- chooseLevel skips empty levels. "Decided by Jess Haley, 2026-10-26 [chooseLevel skips empty" (did_v2_go_forward_class_audit.md:1314).
- ingested stimulus reader finds the body. "Decided by Jess Haley, 2026-10-26 [ingested stimulus reader" (did_v2_go_forward_class_audit.md:1316).
- markdown cleanup and rename. "Decided by Jess Haley, 2026-10-26 [markdown cleanup and" (did_v2_go_forward_class_audit.md:1318).
- pipeline defects are not carries. "Decided by Jess Haley, 2026-10-26 [pipeline defects are not" (did_v2_go_forward_class_audit.md:1320).
- unresolved recorded elements make a standalone item. "Decided by Jess Haley, 2026-10-26 [unresolved recorded" (did_v2_go_forward_class_audit.md:1322).
- extra field on an ingested stimulus file is malformed. "Decided by Jess Haley, 2026-10-26 [extra field on an" (did_v2_go_forward_class_audit.md:1324).
- NaN control means no control. "Decided by Jess Haley, 2026-10-26 [NaN control means no" (did_v2_go_forward_class_audit.md:1326).
- conflicting animal records need a map. "Decided by Jess Haley, 2026-10-26 [conflicting animal" (did_v2_go_forward_class_audit.md:1328).
- method terms are general. "Decided by Jess Haley, 2026-10-26 [method terms are" (did_v2_go_forward_class_audit.md:1330).
- Naka-Rushton is one function. "Decided by Jess Haley, 2026-10-26 [Naka-Rushton is one" (did_v2_go_forward_class_audit.md:1332).
- fields outside the template are malformed. "Decided by Jess Haley, 2026-10-27 [fields outside the" (did_v2_go_forward_class_audit.md:1334).
- probe location terms. "Decided by Jess Haley, 2026-10-27 [probe location terms]: (" (did_v2_go_forward_class_audit.md:1336).
- cell spellings are one meaning. "Decided by Jess Haley, 2026-10-27 [cell spellings are one" (did_v2_go_forward_class_audit.md:1338).
- v1 name is the entity name. "Decided by Jess Haley, 2026-10-27 [v1 name is the entity" (did_v2_go_forward_class_audit.md:1340).
- member edge number is notation. "Decided by Jess Haley, 2026-10-27 [member edge number is" (did_v2_go_forward_class_audit.md:1342).
- afo prefix registered. "Decided by Jess Haley, 2026-10-27 [afo prefix registered]: (" (did_v2_go_forward_class_audit.md:1344).
- n-trode is a multielectrode array. "Decided by Jess Haley, 2026-10-27 [n-trode is a" (did_v2_go_forward_class_audit.md:1346).
- site positions are coordinates. "Decided by Jess Haley, 2026-10-27 [site positions are" (did_v2_go_forward_class_audit.md:1348).
- move the locked mains. "Decided by Jess Haley, 2026-10-27 [move the locked mains]: (" (did_v2_go_forward_class_audit.md:1350).
- merge main into V2. "Decided by Jess Haley, 2026-10-27 [merge main into V2]: (" (did_v2_go_forward_class_audit.md:1352).
- lock NDIcalc-vis-matlab. "Decided by Jess Haley, 2026-10-27 [lock" (did_v2_go_forward_class_audit.md:1354).
- tuning stray fields are malformed. "Decided by Jess Haley, 2026-10-27 [tuning stray fields are" (did_v2_go_forward_class_audit.md:1356).
- cell spellings amended. "Decided by Jess Haley, 2026-10-27 [cell spellings amended]" (did_v2_go_forward_class_audit.md:1358).
- element type is a device kind term. "Decided by Jess Haley, 2026-10-27 [element type is a device" (did_v2_go_forward_class_audit.md:1360).
- ndi element class not kept. "Decided by Jess Haley, 2026-10-27 [ndi element class not" (did_v2_go_forward_class_audit.md:1362).
- number of electrodes minted. "Decided by Jess Haley, 2026-10-27 [number of electrodes" (did_v2_go_forward_class_audit.md:1364).
- site frame is a coordinate system. "Decided by Jess Haley, 2026-10-27 [site frame is a" (did_v2_go_forward_class_audit.md:1366).
- ground truth reads NDIcalc-vis templates. "Decided by Jess Haley, 2026-10-27 [ground truth reads" (did_v2_go_forward_class_audit.md:1368).
- writer fields over the template are template fields. "Decided by Jess Haley, 2026-10-27 [writer fields over the" (did_v2_go_forward_class_audit.md:1370).
- tuning split covers the shared fold. "Decided by Jess Haley, 2026-10-27 [tuning split covers the" (did_v2_go_forward_class_audit.md:1372).
- unreached superclass migrators deleted. "Decided by Jess Haley, 2026-10-27 [unreached superclass" (did_v2_go_forward_class_audit.md:1374).
- unknown filter parameter is malformed. "Decided by Jess Haley, 2026-10-27 [unknown filter parameter" (did_v2_go_forward_class_audit.md:1376).
- five probe kinds from NCIT. "Decided by Jess Haley, 2026-10-27 [five probe kinds from" (did_v2_go_forward_class_audit.md:1378).
- ecg and eeg are recorders. "Decided by Jess Haley, 2026-10-27 [ecg and eeg are" (did_v2_go_forward_class_audit.md:1380).
- imaging probes are microscopes or carried. "Decided by Jess Haley, 2026-10-27 [imaging probes are" (did_v2_go_forward_class_audit.md:1382).
- pyraview level keeps its file info. "Decided by Jess Haley, 2026-10-27 [pyraview level keeps its" (did_v2_go_forward_class_audit.md:1384).
- values no writer produces are malformed. "Decided by Jess Haley, 2026-10-27 [values no writer" (did_v2_go_forward_class_audit.md:1386).
- carried file references are not folded. "Decided by Jess Haley, 2026-10-27 [carried file references" (did_v2_go_forward_class_audit.md:1388).
- light-sheet level fields rebuild from the pyramid. "Decided by Jess Haley, 2026-10-27 [light-sheet level fields" (did_v2_go_forward_class_audit.md:1390).
- one bath shape. "Decided by Jess Haley, 2026-10-27 [one bath shape]: (" (did_v2_go_forward_class_audit.md:1392).
- group identifier includes the reference. "Decided by Jess Haley, 2026-10-27 [group identifier" (did_v2_go_forward_class_audit.md:1394).
- drug end and duration on the anchor. "Decided by Jess Haley, 2026-10-27 [drug end and duration on" (did_v2_go_forward_class_audit.md:1396).
- age at injection is an observation. "Decided by Jess Haley, 2026-10-27 [age at injection is an" (did_v2_go_forward_class_audit.md:1398).
- transfer method keeps its node. "Decided by Jess Haley, 2026-10-27 [transfer method keeps" (did_v2_go_forward_class_audit.md:1400).
- sync configuration stays a class. "Decided by Jess Haley, 2026-10-27 [sync configuration stays" (did_v2_go_forward_class_audit.md:1402).
- sync configuration links its rigs. "Decided by Jess Haley, 2026-10-27 [sync configuration links" (did_v2_go_forward_class_audit.md:1404).
- sync rule direction is recorded. "Decided by Jess Haley, 2026-10-27 [sync rule direction is" (did_v2_go_forward_class_audit.md:1406).
- acquisition channels kept for wiring. "Decided by Jess Haley, 2026-10-27 [acquisition channels" (did_v2_go_forward_class_audit.md:1408).
- handed-on documents do not carry dependents. "Decided by Jess Haley, 2026-10-27 [handed-on documents do" (did_v2_go_forward_class_audit.md:1410).
- unit direct and subject rebuild from the probe. "Decided by Jess Haley, 2026-10-27 [unit direct and subject" (did_v2_go_forward_class_audit.md:1412).
- broken transfer values are malformed. "Decided by Jess Haley, 2026-10-27 [broken transfer values" (did_v2_go_forward_class_audit.md:1414).
- treatment transfer stays v1. "Decided by Jess Haley, 2026-10-27 [treatment transfer stays" (did_v2_go_forward_class_audit.md:1416).
- bath ph and osmolarity are formulation fields. "Decided by Jess Haley, 2026-10-27 [bath ph and osmolarity" (did_v2_go_forward_class_audit.md:1418).
- light-sheet level label is a note. "Decided by Jess Haley, 2026-10-27 [light-sheet level label" (did_v2_go_forward_class_audit.md:1420).
- unreadable responses are malformed. "Decided by Jess Haley, 2026-10-27 [unreadable responses are" (did_v2_go_forward_class_audit.md:1422).
- unbuilt spike classes carry as needs home. "Decided by Jess Haley, 2026-10-27 [unbuilt spike classes" (did_v2_go_forward_class_audit.md:1424).
- input names rebuild from the input class. "Decided by Jess Haley, 2026-10-27 [input names rebuild from" (did_v2_go_forward_class_audit.md:1426).
- neuron uses the sorted unit's cell. "Decided by Jess Haley, 2026-10-27 [neuron uses the sorted" (did_v2_go_forward_class_audit.md:1428).
- sample times equal within one rounding step. "Decided by Jess Haley, 2026-10-27 [sample times equal" (did_v2_go_forward_class_audit.md:1430).
- contrast SF bug is a dataset decision. "Decided by Jess Haley, 2026-10-27 [contrast SF bug is a" (did_v2_go_forward_class_audit.md:1432).
- whole-batch round trip. "Decided by Jess Haley, 2026-10-27 [whole-batch round trip]" (did_v2_go_forward_class_audit.md:1434).
- carried documents may point at converted ones. "Decided by Jess Haley, 2026-10-27 [carried documents may" (did_v2_go_forward_class_audit.md:1436).
- simple_calc carries as needs home. "Decided by Jess Haley, 2026-10-27 [simple_calc carries as" (did_v2_go_forward_class_audit.md:1438).
- empty prestimulus normalization is zero. "Decided by Jess Haley, 2026-10-27 [empty prestimulus" (did_v2_go_forward_class_audit.md:1440).
- importer bugs are dataset decisions. "Decided by Jess Haley, 2026-10-27 [importer bugs are" (did_v2_go_forward_class_audit.md:1442).
- hotelling spellings are one field. "Decided by Jess Haley, 2026-10-27 [hotelling spellings are" (did_v2_go_forward_class_audit.md:1444).
- Priebe fits are one function. "Decided by Jess Haley, 2026-10-27 [Priebe fits are one" (did_v2_go_forward_class_audit.md:1446).
- NDI CI picks did-schema branch. "Decided by Jess Haley, 2026-10-27 [NDI CI picks did-schema" (did_v2_go_forward_class_audit.md:1448).
- sorter labels map. "Decided by Jess Haley, 2026-10-27 [sorter labels map]: (" (did_v2_go_forward_class_audit.md:1450).
- image stack name goes to notes. "Decided by Jess Haley, 2026-10-27 [image stack name goes to" (did_v2_go_forward_class_audit.md:1452).
- carry-055 wording follows the group identifier. "Decided by Jess Haley, 2026-10-27 [carry-055 wording" (did_v2_go_forward_class_audit.md:1454).
- treatment location name is the node. "Decided by Jess Haley, 2026-10-27 [treatment location name" (did_v2_go_forward_class_audit.md:1456).
- ingested stimulus body link follow-up. "Decided by Jess Haley, 2026-10-27 [ingested stimulus body" (did_v2_go_forward_class_audit.md:1458).
- cloud organization id is a global identifier. "Decided by Jess Haley, 2026-10-27 [cloud organization id is" (did_v2_go_forward_class_audit.md:1460).
- curve fitting is the fit method term. "Decided by Jess Haley, 2026-10-27 [curve fitting is the fit" (did_v2_go_forward_class_audit.md:1462).
- bath solution minted. "Decided by Jess Haley, 2026-10-27 [bath solution minted]: (" (did_v2_go_forward_class_audit.md:1464).
- second pass reads control stimuli from v1. "Decided by Jess Haley, 2026-10-27 [second pass reads" (did_v2_go_forward_class_audit.md:1466).
- tuning fits use curve fitting now. "Decided by Jess Haley, 2026-10-27 [tuning fits use curve" (did_v2_go_forward_class_audit.md:1468).
- presentation anchored to its epoch. "Decided by Jess Haley, 2026-10-27 [presentation anchored to" (did_v2_go_forward_class_audit.md:1470).
- response links: epoch rebuilt, control as input. "Decided by Jess Haley, 2026-10-27 [response links: epoch" (did_v2_go_forward_class_audit.md:1472).
- openMINDS subject leftovers. "Decided by Jess Haley, 2026-10-27 [openMINDS subject" (did_v2_go_forward_class_audit.md:1474).
- term equivalents recorded. "Decided by Jess Haley, 2026-10-27 [term equivalents" (did_v2_go_forward_class_audit.md:1476).
- dataset form lists carried until homed. "Decided by Jess Haley, 2026-10-27 [dataset form lists" (did_v2_go_forward_class_audit.md:1478).
- old ndi_document blocks carry. "Decided by Jess Haley, 2026-10-27 [old ndi_document blocks" (did_v2_go_forward_class_audit.md:1480).
- tuning stimids rebuild. "Decided by Jess Haley, 2026-10-27 [tuning stimids rebuild]" (did_v2_go_forward_class_audit.md:1482).
- tuning log in notes. "Decided by Jess Haley, 2026-10-27 [tuning log in notes]: (" (did_v2_go_forward_class_audit.md:1484).
- varied properties are conditions by V2 name. "Decided by Jess Haley, 2026-10-27 [varied properties are" (did_v2_go_forward_class_audit.md:1486).
- absolute-value fits are a second calculation. "Decided by Jess Haley, 2026-10-27 [absolute-value fits are" (did_v2_go_forward_class_audit.md:1488).
- contrast metrics added. "Decided by Jess Haley, 2026-10-27 [contrast metrics added]" (did_v2_go_forward_class_audit.md:1490).
- parameter names map by table. "Decided by Jess Haley, 2026-10-27 [parameter names map by" (did_v2_go_forward_class_audit.md:1492).
- E. coli stacks are a dataset decision. "Decided by Jess Haley, 2026-10-27 [E" (did_v2_go_forward_class_audit.md:1494).
- every v1 id survives. "Decided by Jess Haley, 2026-10-27 [every v1 id survives]: (" (did_v2_go_forward_class_audit.md:1496).
- axis letters derive from labels. "Decided by Jess Haley, 2026-10-27 [axis letters derive from" (did_v2_go_forward_class_audit.md:1498).
- v1 name goes to the class's own name field. "Decided by Jess Haley, 2026-10-27 [v1 name goes to the" (did_v2_go_forward_class_audit.md:1500).
- demo keeps its name. "Decided by Jess Haley, 2026-11-19 [demo keeps its name]: (" (did_v2_go_forward_class_audit.md:1502).
- base.name kept until retire classes leave. "Decided by Jess Haley, 2026-10-29 [base.name kept until" (did_v2_go_forward_class_audit.md:1506).
- treatment groups are a dataset decision. "Decided by Jess Haley, 2026-10-27 [treatment groups are a" (did_v2_go_forward_class_audit.md:1508).
- fit classes kept; session list rebuilt. "Decided by Jess Haley, 2026-10-27 [fit classes kept" (did_v2_go_forward_class_audit.md:1510).
- event lines are event channels. "Decided by Jess Haley, 2026-10-27 [event lines are event" (did_v2_go_forward_class_audit.md:1512).
- labels are a field on what they label. "Decided by Jess Haley, 2026-10-27 [labels are a field on" (did_v2_go_forward_class_audit.md:1514).
- ontologyLabel row split. "Decided by Jess Haley, 2026-10-27 [ontologyLabel row" (did_v2_go_forward_class_audit.md:1516).
- openMINDS strain leftovers. "Decided by Jess Haley, 2026-10-27 [openMINDS strain" (did_v2_go_forward_class_audit.md:1518).
- control pairing points at the presentation. "Decided by Jess Haley, 2026-10-27 [control pairing points" (did_v2_go_forward_class_audit.md:1520).
- control record fields split. "Decided by Jess Haley, 2026-10-27 [control record fields" (did_v2_go_forward_class_audit.md:1522).
- unread stimulus parameters are method parameters. "Decided by Jess Haley, 2026-10-27 [unread stimulus" (did_v2_go_forward_class_audit.md:1524).
- session opener inputs. "Decided by Jess Haley, 2026-10-27 [session opener inputs]: (" (did_v2_go_forward_class_audit.md:1526).
- linked session reference follows the ingested rule. "Decided by Jess Haley, 2026-10-27 [linked session reference" (did_v2_go_forward_class_audit.md:1528).
- one affiliation relation each. "Decided by Jess Haley, 2026-10-27 [one affiliation relation" (did_v2_go_forward_class_audit.md:1530).
- position and its metadata are one statement. "Decided by Jess Haley, 2026-10-27 [position and its" (did_v2_go_forward_class_audit.md:1532).
- image stack link needs mapping. "Decided by Jess Haley, 2026-10-27 [image stack link needs" (did_v2_go_forward_class_audit.md:1534).
- image link needs mapping. "Decided by Jess Haley, 2026-11-19 [image link needs" (did_v2_go_forward_class_audit.md:1536).
- reverse correlation waits for a dataset. "Decided by Jess Haley, 2026-11-19 [reverse correlation" (did_v2_go_forward_class_audit.md:1538).
- spike interface sorting carried as v1. "Decided by Jess Haley, 2026-11-19 [spike interface sorting" (did_v2_go_forward_class_audit.md:1540).
- image label goes to notes. "Decided by Jess Haley, 2026-10-27 [image label goes to" (did_v2_go_forward_class_audit.md:1542).
- hartley labels stay carried. "Decided by Jess Haley, 2026-10-27 [hartley labels stay" (did_v2_go_forward_class_audit.md:1544).
- filter label is the method name. "Decided by Jess Haley, 2026-10-27 [filter label is the" (did_v2_go_forward_class_audit.md:1546).
- contact geometry stays carried. "Decided by Jess Haley, 2026-10-27 [contact geometry stays" (did_v2_go_forward_class_audit.md:1548).
- scanner test issue closed. "Decided by Jess Haley, 2026-10-27 [scanner test issue" (did_v2_go_forward_class_audit.md:1550).
- old EMPTY labels generalised. "Decided by Jess Haley, 2026-10-27 [old EMPTY labels" (did_v2_go_forward_class_audit.md:1552).
- no about edge for now. "Decided by Jess Haley, 2026-10-27 [no about edge for now]: (" (did_v2_go_forward_class_audit.md:1554).
- old table rows counted and carried. "Decided by Jess Haley, 2026-10-27 [old table rows counted" (did_v2_go_forward_class_audit.md:1556).
- binaryseries parameters fold as decided. "Decided by Jess Haley, 2026-10-27 [binaryseries parameters" (did_v2_go_forward_class_audit.md:1558).
- Guard A amended. "Decided by Jess Haley, 2026-10-27 [Guard A amended]: (" (did_v2_go_forward_class_audit.md:1560).
- documents without base carry. "Decided by Jess Haley, 2026-10-27 [documents without base" (did_v2_go_forward_class_audit.md:1562).
- oneepoch is a redundant calculation. "Decided by Jess Haley, 2026-10-27 [oneepoch is a redundant" (did_v2_go_forward_class_audit.md:1564).
- redeclarations only narrow. "Decided by Jess Haley, 2026-10-27 [redeclarations only" (did_v2_go_forward_class_audit.md:1568).
- no value rollup now. "Decided by Jess Haley, 2026-10-27 [no value rollup now]: (" (did_v2_go_forward_class_audit.md:1570).
- ngrid migrates to sampled bodies. "Decided by Jess Haley, 2026-10-27 [ngrid migrates to" (did_v2_go_forward_class_audit.md:1572).
- allowed units are closed source_unit lists. "Decided by Jess Haley, 2026-10-27 [allowed units are closed" (did_v2_go_forward_class_audit.md:1574).
- quantity reference type. "Decided by Jess Haley, 2026-10-27 [quantity reference" (did_v2_go_forward_class_audit.md:1576).
- epoch-less presentations carry. "Decided by Jess Haley, 2026-10-27 [epoch-less presentations" (did_v2_go_forward_class_audit.md:1578).
- Babu and Soph workbooks. "Decided by Jess Haley, 2026-10-27 [Babu and Soph" (did_v2_go_forward_class_audit.md:1580).
- sample times within eight rounding steps. "Decided by Jess Haley, 2026-10-27 [sample times within" (did_v2_go_forward_class_audit.md:1582).
- a rebuilt document may lose its id. "Decided by Jess Haley, 2026-10-27 [a rebuilt document may" (did_v2_go_forward_class_audit.md:1584).
- jrclust default name is notation. "Decided by Jess Haley, 2026-10-27 [jrclust default name is" (did_v2_go_forward_class_audit.md:1586).
- organization needs a name or an identifier. "Decided by Jess Haley, 2026-10-27 [organization needs a" (did_v2_go_forward_class_audit.md:1588).
- empty ndi_document block is notation. "Decided by Jess Haley, 2026-10-27 [empty ndi_document block" (did_v2_go_forward_class_audit.md:1590).
- device kinds minted. "Decided by Jess Haley, 2026-10-28 [device kinds minted]: (" (did_v2_go_forward_class_audit.md:1592).
- device kind labels and synonyms. "Decided by Jess Haley, 2026-10-28 [device kind labels and" (did_v2_go_forward_class_audit.md:1594).
- tuning best value is a condition. "Decided by Jess Haley, 2026-10-28 [tuning best value is a" (did_v2_go_forward_class_audit.md:1596).
- one calculation per named calculator output. "Decided by Jess Haley, 2026-10-28 [one calculation per" (did_v2_go_forward_class_audit.md:1598).
- absolute-value fits are fit entries. "Decided by Jess Haley, 2026-10-28 [absolute-value fits are" (did_v2_go_forward_class_audit.md:1600).
- presentations without an epoch keep the session anchor. "Decided by Jess Haley, 2026-10-28 [presentations without an" (did_v2_go_forward_class_audit.md:1602).
- image label goes to the observation's notes. "Decided by Jess Haley, 2026-10-29 [image label goes to the" (did_v2_go_forward_class_audit.md:1604).
- binaryseries parameters carried. "Decided by Jess Haley, 2026-10-29 [binaryseries parameters" (did_v2_go_forward_class_audit.md:1606).
- ngrid with no statement carried. "Decided by Jess Haley, 2026-10-29 [ngrid with no statement" (did_v2_go_forward_class_audit.md:1608).
- old table rows carried by NDI. "Decided by Jess Haley, 2026-10-29 [old table rows carried" (did_v2_go_forward_class_audit.md:1610).
- allowed units are source units. "Decided by Jess Haley, 2026-10-29 [allowed units are source" (did_v2_go_forward_class_audit.md:1612).
- standalone item control stays carried. "Decided by Jess Haley, 2026-10-29 [standalone item control" (did_v2_go_forward_class_audit.md:1614).
- oneepoch method is data combination. "Decided by Jess Haley, 2026-10-29 [oneepoch method is data" (did_v2_go_forward_class_audit.md:1616).
- redeclarations merge when base.name goes. "Decided by Jess Haley, 2026-10-29 [redeclarations merge" (did_v2_go_forward_class_audit.md:1618).
- linked session not in the batch. "Decided by Jess Haley, 2026-10-29 [linked session not in" (did_v2_go_forward_class_audit.md:1620).
- unstated session creator carried. "Decided by Jess Haley, 2026-10-29 [unstated session creator" (did_v2_go_forward_class_audit.md:1622).
- drug end without start needs mapping. "Decided by Jess Haley, 2026-10-29 [drug end without start" (did_v2_go_forward_class_audit.md:1624).
- drug times that disagree need mapping. "Decided by Jess Haley, 2026-10-29 [drug times that disagree" (did_v2_go_forward_class_audit.md:1626).
- text channel replaces NCIT Text. "Decided by Jess Haley, 2026-10-29 [text channel replaces" (did_v2_go_forward_class_audit.md:1628).
- cell-attached is OBI. "Decided by Jess Haley, 2026-10-29 [cell-attached is OBI]: (" (did_v2_go_forward_class_audit.md:1630).
- linked session link on a direct dataset relation. "Decided by Jess Haley, 2026-10-29 [linked session link on a" (did_v2_go_forward_class_audit.md:1632).
- fit model stated once. "Decided by Jess Haley, 2026-10-29 [fit model stated once]: (" (did_v2_go_forward_class_audit.md:1634).
- term names compare by node. "Decided by Jess Haley, 2026-10-29 [term names compare by" (did_v2_go_forward_class_audit.md:1636).
- species text is the openMINDS equivalent. "Decided by Jess Haley, 2026-10-29 [species text is the" (did_v2_go_forward_class_audit.md:1638).
- openMINDS element leftovers carried. "Decided by Jess Haley, 2026-10-29 [openMINDS element" (did_v2_go_forward_class_audit.md:1640).
- segment length is the time chunk. "Decided by Jess Haley, 2026-10-29 [segment length is the" (did_v2_go_forward_class_audit.md:1642).
- one folder, final classes only. "Decided by Jess Haley, 2026-10-29 [one folder, final" (did_v2_go_forward_class_audit.md:1644).
- v1 writes into a V2 session. "Decided by Jess Haley, 2026-10-29 [v1 writes into a V2" (did_v2_go_forward_class_audit.md:1646).
- linked session link details. "Decided by Jess Haley, 2026-10-29 [linked session link" (did_v2_go_forward_class_audit.md:1648).
- reshaped retire classes carried. "Decided by Jess Haley, 2026-10-29 [reshaped retire classes" (did_v2_go_forward_class_audit.md:1650).
- linked session pathname. "Decided by Jess Haley, 2026-10-29 [linked session" (did_v2_go_forward_class_audit.md:1652).
- addSessionV2 folded back. "Decided by Jess Haley, 2026-10-29 [addSessionV2 folded" (did_v2_go_forward_class_audit.md:1654).
- term names match ignoring spacing. "Decided by Jess Haley, 2026-10-29 [term names match" (did_v2_go_forward_class_audit.md:1656).
- n-trode count from the channel list. "Decided by Jess Haley, 2026-10-29 [n-trode count from the" (did_v2_go_forward_class_audit.md:1658).
- imaging mode is a method term. "Decided by Jess Haley, 2026-10-29 [imaging mode is a method" (did_v2_go_forward_class_audit.md:1660).
- equipment type is the device kind list. "Decided by Jess Haley, 2026-10-29 [equipment type is the" (did_v2_go_forward_class_audit.md:1662).
- V2 ingest is one sampled body per channel group. "Decided by Jess Haley, 2026-10-29 [V2 ingest is one sampled" (did_v2_go_forward_class_audit.md:1664).
- short last chunk. "Decided by Jess Haley, 2026-10-29 [short last chunk]: (" (did_v2_go_forward_class_audit.md:1666).
- missing facts are needs info. "Decided by Jess Haley, 2026-10-29 [missing facts are needs" (did_v2_go_forward_class_audit.md:1668).
- vintage-B ontologyImage cases. "Decided by Jess Haley, 2026-10-29 [vintage-B ontologyImage" (did_v2_go_forward_class_audit.md:1670).
- element name and reference stored apart. "Decided by Jess Haley, 2026-10-29 [element name and" (did_v2_go_forward_class_audit.md:1672).
- unit with no probe in the batch carried. "Decided by Jess Haley, 2026-10-29 [unit with no probe in" (did_v2_go_forward_class_audit.md:1674).
- table rows carried as v1. "Decided by Jess Haley, 2026-10-30 [table rows carried as" (did_v2_go_forward_class_audit.md:1676).
- preset name stays on method. "Decided by Jess Haley, 2026-10-30 [preset name stays on" (did_v2_go_forward_class_audit.md:1678).
- redeclaration merge moot. "Decided by Jess Haley, 2026-10-30 [redeclaration merge" (did_v2_go_forward_class_audit.md:1680).
- element name kept apart, base.name carried. "Decided by Jess Haley, 2026-10-30 [element name kept apart" (did_v2_go_forward_class_audit.md:1682).
- Naka-Rushton function minted. "Decided by Jess Haley, 2026-10-30 [Naka-Rushton function" (did_v2_go_forward_class_audit.md:1684).
- synonyms supersede nodes only. "Decided by Jess Haley, 2026-10-30 [synonyms supersede nodes" (did_v2_go_forward_class_audit.md:1686).
- interpolated values are a list. "Decided by Jess Haley, 2026-10-30 [interpolated values are" (did_v2_go_forward_class_audit.md:1688).
- canonical absent only as needs info. "Decided by Jess Haley, 2026-10-30 [canonical absent only as" (did_v2_go_forward_class_audit.md:1690).
- trigger channels named by their link. "Decided by Jess Haley, 2026-10-30 [trigger channels named" (did_v2_go_forward_class_audit.md:1692).
- decibels are their own canonical. "Decided by Jess Haley, 2026-10-30 [decibels are their own" (did_v2_go_forward_class_audit.md:1694).
- Haley mask words leave the generic stage. "Decided by Jess Haley, 2026-10-30 [Haley mask words leave" (did_v2_go_forward_class_audit.md:1696).
- control records carried in pass 1. "Decided by Jess Haley, 2026-10-30 [control records carried" (did_v2_go_forward_class_audit.md:1698).
- image raw round trip and single-read keys. "Decided by Jess Haley, 2026-10-30 [image raw round trip and" (did_v2_go_forward_class_audit.md:1700).
- age is NCIT Age. "Decided by Jess Haley, 2026-10-30 [age is NCIT Age]: (" (did_v2_go_forward_class_audit.md:1702).
- equivalents filled in did-schema. "Decided by Jess Haley, 2026-10-30 [equivalents filled in" (did_v2_go_forward_class_audit.md:1704).
- Hartley settings on the inline method. "Decided by Jess Haley, 2026-10-30 [Hartley settings on the" (did_v2_go_forward_class_audit.md:1706).
- acquisition time on its clock. "Decided by Jess Haley, 2026-10-30 [acquisition time on its" (did_v2_go_forward_class_audit.md:1708).
- data analysis is the general method. "Decided by Jess Haley, 2026-10-30 [data analysis is the" (did_v2_go_forward_class_audit.md:1710).
- image collection carried until a writer. "Decided by Jess Haley, 2026-10-30 [image collection carried" (did_v2_go_forward_class_audit.md:1712).
- global-clock oneepoch details. "Decided by Jess Haley, 2026-10-30 [global-clock oneepoch" (did_v2_go_forward_class_audit.md:1714).
- openMINDS strain leftovers settled. "Decided by Jess Haley, 2026-10-30 [openMINDS strain" (did_v2_go_forward_class_audit.md:1716).
- assay labels batch 1. "Decided by Jess Haley, 2026-10-30 [assay labels batch 1]: (" (did_v2_go_forward_class_audit.md:1718).
- element types batch 1. "Decided by Jess Haley, 2026-10-30 [element types batch 1]: (" (did_v2_go_forward_class_audit.md:1720).
- assay labels batch 2. "Decided by Jess Haley, 2026-10-30 [assay labels batch 2]: (" (did_v2_go_forward_class_audit.md:1722).
- element types batch 2. "Decided by Jess Haley, 2026-10-30 [element types batch 2]: (" (did_v2_go_forward_class_audit.md:1724).
- assay labels batch 3. "Decided by Jess Haley, 2026-10-30 [assay labels batch 3]: (" (did_v2_go_forward_class_audit.md:1726).
- element types batch 3. "Decided by Jess Haley, 2026-10-30 [element types batch 3]: (" (did_v2_go_forward_class_audit.md:1728).
- element types batch 4. "Decided by Jess Haley, 2026-10-30 [element types batch 4]: (" (did_v2_go_forward_class_audit.md:1730).
- assay labels batch 4. "Decided by Jess Haley, 2026-10-30 [assay labels batch 4]: (" (did_v2_go_forward_class_audit.md:1732).
- assay labels batch 5. "Decided by Jess Haley, 2026-10-30 [assay labels batch 5]: (" (did_v2_go_forward_class_audit.md:1734).
- assay labels batch 6. "Decided by Jess Haley, 2026-10-30 [assay labels batch 6]: (" (did_v2_go_forward_class_audit.md:1736).
- assay relabels become new terms. "Decided by Jess Haley, 2026-11-01 [assay relabels become" (did_v2_go_forward_class_audit.md:1738).
- assay term definitions drafted. "Decided by Jess Haley, 2026-11-01 [assay term definitions" (did_v2_go_forward_class_audit.md:1740).
- obsolete assay terms without replacement. "Decided by Jess Haley, 2026-11-01 [obsolete assay terms" (did_v2_go_forward_class_audit.md:1742).
- assay dictionaries look up by id. "Decided by Jess Haley, 2026-11-01 [assay dictionaries look" (did_v2_go_forward_class_audit.md:1744).
- assay ontology cleanup now. "Decided by Jess Haley, 2026-11-01 [assay ontology cleanup" (did_v2_go_forward_class_audit.md:1746).
- assay term definitions approved. "Decided by Jess Haley, 2026-11-01 [assay term definitions" (did_v2_go_forward_class_audit.md:1748).
- obsolete labels in v1 importers accepted. "Decided by Jess Haley, 2026-11-01 [obsolete labels in v1" (did_v2_go_forward_class_audit.md:1750).
- raw v1 switch finished in batches. "Decided by Jess Haley, 2026-10-30 [raw v1 switch finished" (did_v2_go_forward_class_audit.md:1752).
- stimulator is SNOMED CT Stimulator. "Decided by Jess Haley, 2026-10-30 [stimulator is SNOMED CT" (did_v2_go_forward_class_audit.md:1754).
- global-clock oneepoch carried with its element. "Decided by Jess Haley, 2026-10-30 [global-clock oneepoch" (did_v2_go_forward_class_audit.md:1756).
- differing stimulator epoch is malformed. "Decided by Jess Haley, 2026-10-30 [differing stimulator" (did_v2_go_forward_class_audit.md:1758).
- response unit slot settles 110. "Decided by Jess Haley, 2026-10-30 [response unit slot" (did_v2_go_forward_class_audit.md:1760).
- schema folders by family. "Decided by Jess Haley, 2026-10-30 [schema folders by" (did_v2_go_forward_class_audit.md:1762).
- family roots and relation folder. "Decided by Jess Haley, 2026-10-31 [family roots and" (did_v2_go_forward_class_audit.md:1764).
- retire check now. "Decided by Jess Haley, 2026-10-31 [retire check now]: (" (did_v2_go_forward_class_audit.md:1766).
- purpose renamed now. "Decided by Jess Haley, 2026-10-31 [purpose renamed now]: (" (did_v2_go_forward_class_audit.md:1768).
- acquisition folder. "Decided by Jess Haley, 2026-10-31 [acquisition folder]: (" (did_v2_go_forward_class_audit.md:1770).
- clock alignment in time_reference. "Decided by Jess Haley, 2026-10-31 [clock alignment in" (did_v2_go_forward_class_audit.md:1772).
- reference papers as v2 guidance. "Decided by Jess Haley, 2026-10-31 [reference papers as v2" (did_v2_go_forward_class_audit.md:1774).
- gene list mapping is built. "Decided by Jess Haley, 2026-10-31 [gene list mapping is" (did_v2_go_forward_class_audit.md:1776).
- gene list mapping in the generic stage. "Decided by Jess Haley, 2026-10-31 [gene list mapping in the" (did_v2_go_forward_class_audit.md:1778).
- daqreader_ndr confirmed set. "Decided by Jess Haley, 2026-10-31 [daqreader_ndr confirmed" (did_v2_go_forward_class_audit.md:1780).
- layout calls stand. "Decided by Jess Haley, 2026-10-31 [layout calls stand]: (" (did_v2_go_forward_class_audit.md:1782).
- om day registered. "Decided by Jess Haley, 2026-10-31 [om day registered]: (" (did_v2_go_forward_class_audit.md:1784).
- formulation amount needs info. "Decided by Jess Haley, 2026-10-31 [formulation amount needs" (did_v2_go_forward_class_audit.md:1786).
- virus dilution needs info. "Decided by Jess Haley, 2026-10-31 [virus dilution needs" (did_v2_go_forward_class_audit.md:1788).
- UTC acquisition time is absolute. "Decided by Jess Haley, 2026-10-31 [UTC acquisition time is" (did_v2_go_forward_class_audit.md:1790).
- ndi_document read as base. "Decided by Jess Haley, 2026-10-31 [ndi_document read as" (did_v2_go_forward_class_audit.md:1792).
- rename clashes are malformed. "Decided by Jess Haley, 2026-11-01 [rename clashes are" (did_v2_go_forward_class_audit.md:1794).
- ensemble and generic_file keep their conversions. "Decided by Jess Haley, 2026-11-01 [ensemble and" (did_v2_go_forward_class_audit.md:1796).
- ensemble and generic_file checked as v1. "Decided by Jess Haley, 2026-11-01 [ensemble and" (did_v2_go_forward_class_audit.md:1798).
- last rename-pass classes. "Decided by Jess Haley, 2026-11-01 [last rename-pass" (did_v2_go_forward_class_audit.md:1800).
- UTC treatment time is absolute. "Decided by Jess Haley, 2026-11-01 [UTC treatment time is" (did_v2_go_forward_class_audit.md:1802).
- postnatal day 0 not stated. "Decided by Jess Haley, 2026-11-01 [postnatal day 0 not" (did_v2_go_forward_class_audit.md:1804).
- percent volume per volume converted. "Decided by Jess Haley, 2026-11-01 [percent volume per" (did_v2_go_forward_class_audit.md:1806).
- breeding type and disease model text not stored. "Decided by Jess Haley, 2026-11-01 [breeding type and" (did_v2_go_forward_class_audit.md:1808).
- relations get notes. "Decided by Jess Haley, 2026-11-01 [relations get notes]: (" (did_v2_go_forward_class_audit.md:1810).
- hartley implied by its class. "Decided by Jess Haley, 2026-11-01 [hartley implied by its" (did_v2_go_forward_class_audit.md:1812).
- study link without a dataset document. "Decided by Jess Haley, 2026-11-01 [study link without a" (did_v2_go_forward_class_audit.md:1814).
- redeclarations left need no merge. "Decided by Jess Haley, 2026-11-01 [redeclarations left need" (did_v2_go_forward_class_audit.md:1816).
- binding catalogue gap reports only. "Decided by Jess Haley, 2026-11-01 [binding catalogue gap" (did_v2_go_forward_class_audit.md:1818).
- compression terms registered. "Decided by Jess Haley, 2026-11-01 [compression terms" (did_v2_go_forward_class_audit.md:1820).
- compression term definitions approved. "Decided by Jess Haley, 2026-11-01 [compression term" (did_v2_go_forward_class_audit.md:1822).
- unit lists widened then armed. "Decided by Jess Haley, 2026-11-01 [unit lists widened then" (did_v2_go_forward_class_audit.md:1824).
- CLAUDE.md layout corrections drafted. "Decided by Jess Haley, 2026-11-01 [CLAUDE.md layout" (did_v2_go_forward_class_audit.md:1826).
- migration record. "Decided by Jess Haley, 2026-11-01 [migration record]: (" (did_v2_go_forward_class_audit.md:1828).
- gap accepted when the report lists it. "Decided by Jess Haley, 2026-11-01 [gap accepted when the" (did_v2_go_forward_class_audit.md:1838).
- migration report is an attached file. "Decided by Jess Haley, 2026-11-01 [migration report is an" (did_v2_go_forward_class_audit.md:1840).
- migration record points at the dataset. "Decided by Jess Haley, 2026-11-01 [migration record points" (did_v2_go_forward_class_audit.md:1842).
- migration record writer. "Decided by Jess Haley, 2026-11-01 [migration record" (did_v2_go_forward_class_audit.md:1844).
- migration method is conversion. "Decided by Jess Haley, 2026-11-01 [migration method is" (did_v2_go_forward_class_audit.md:1846).
- gene list mapping value shape. "Decided by Jess Haley, 2026-11-01 [gene list mapping value" (did_v2_go_forward_class_audit.md:1848).
- gene list mapping value kind. "Decided by Jess Haley, 2026-11-01 [gene list mapping value" (did_v2_go_forward_class_audit.md:1850).
- gene list mapping method text. "Decided by Jess Haley, 2026-11-01 [gene list mapping method" (did_v2_go_forward_class_audit.md:1852).
- orthology mapping has no method term. "Decided by Jess Haley, 2026-11-01 [orthology mapping has no" (did_v2_go_forward_class_audit.md:1854).
- gene list as a term, file kept. "Decided by Jess Haley, 2026-11-01 [gene list as a term" (did_v2_go_forward_class_audit.md:1856).
- mapping rows counted, indices 0-based. "Decided by Jess Haley, 2026-11-01 [mapping rows counted" (did_v2_go_forward_class_audit.md:1858).
- undirected relation widened. "Decided by Jess Haley, 2026-11-01 [undirected relation" (did_v2_go_forward_class_audit.md:1860).
- undirected ends are relata. "Decided by Jess Haley, 2026-11-01 [undirected ends are" (did_v2_go_forward_class_audit.md:1862).
- undirected registry columns are relata. "Decided by Jess Haley, 2026-11-01 [undirected registry" (did_v2_go_forward_class_audit.md:1864).
- gene list mapping leftovers. "Decided by Jess Haley, 2026-11-01 [gene list mapping" (did_v2_go_forward_class_audit.md:1866).
- gene list mapping other types carried. "Decided by Jess Haley, 2026-11-01 [gene list mapping other" (did_v2_go_forward_class_audit.md:1868).
- no per-pair orthology variable. "Decided by Jess Haley, 2026-11-01 [no per-pair orthology" (did_v2_go_forward_class_audit.md:1870).
- key covariate index. "Decided by Jess Haley, 2026-11-01 [key covariate index]: (" (did_v2_go_forward_class_audit.md:1872).
- recording mode terms. "Decided by Jess Haley, 2026-11-01 [recording mode terms]: (" (did_v2_go_forward_class_audit.md:1881).
- imaging mode terms. "Decided by Jess Haley, 2026-11-01 [imaging mode terms]: (" (did_v2_go_forward_class_audit.md:1883).
- ingest writes no v1 ingested document. "Decided by Jess Haley, 2026-11-01 [ingest writes no v1" (did_v2_go_forward_class_audit.md:1885).
- ingest observation per probe. "Decided by Jess Haley, 2026-11-01 [ingest observation per" (did_v2_go_forward_class_audit.md:1887).
- Haley phase, pick and encounter as written. "Decided by Jess Haley, 2026-11-01 [Haley phase, pick and" (did_v2_go_forward_class_audit.md:1889).
- EMPTY:0000129 retired. "Decided by Jess Haley, 2026-11-01 [EMPTY:0000129 retired]: (" (did_v2_go_forward_class_audit.md:1891).
- ingest waits on native V2 records. "Decided by Jess Haley, 2026-11-01 [ingest waits on native" (did_v2_go_forward_class_audit.md:1893).
- V2 database file renamed. "Decided by Jess Haley, 2026-11-01 [V2 database file" (did_v2_go_forward_class_audit.md:1895).
- V2 is the build target for the siblings. "Decided by Jess Haley, 2026-11-01 [V2 is the build target" (did_v2_go_forward_class_audit.md:1897).
- evenly spaced time is a covariate. "Decided by Jess Haley, 2026-11-01 [evenly spaced time is a" (did_v2_go_forward_class_audit.md:1899).
- ingested archives are sampled bodies. "Decided by Jess Haley, 2026-11-01 [ingested archives are" (did_v2_go_forward_class_audit.md:1901).
- ingested compression settings. "Decided by Jess Haley, 2026-11-01 [ingested compression" (did_v2_go_forward_class_audit.md:1903).
- compression settings without bit size. "Decided by Jess Haley, 2026-11-19 [compression settings" (did_v2_go_forward_class_audit.md:1905).
- probe wiring is a relation. "Decided by Jess Haley, 2026-11-01 [probe wiring is a" (did_v2_go_forward_class_audit.md:1907).
- clock only on the time reference. "Decided by Jess Haley, 2026-11-01 [clock only on the time" (did_v2_go_forward_class_audit.md:1909).
- wiring relation term. "Decided by Jess Haley, 2026-11-01 [wiring relation term]: (" (did_v2_go_forward_class_audit.md:1911).
- Claude drafts the Dab map. "Decided by Jess Haley, 2026-11-02 [Claude drafts the Dab" (did_v2_go_forward_class_audit.md:1913).
- handed-on classes carried at the end. "Decided by Jess Haley, 2026-11-02 [handed-on classes" (did_v2_go_forward_class_audit.md:1915).
- V_eta not kept as an alias. "Decided by Jess Haley, 2026-11-02 [V_eta not kept as an" (did_v2_go_forward_class_audit.md:1917).
- handed-on are v1 as written. "Decided by Jess Haley, 2026-11-03 [handed-on are v1 as" (did_v2_go_forward_class_audit.md:1919).
- one-photon is NCIT fluorescence microscopy. "Decided by Jess Haley, 2026-11-03 [one-photon is NCIT" (did_v2_go_forward_class_audit.md:1921).
- saline placeholder in Hunsberger import. "Decided by Jess Haley, 2026-11-03 [saline placeholder in" (did_v2_go_forward_class_audit.md:1923).
- Dab bath units are Dabrowska's. "Decided by Jess Haley, 2026-11-03 [Dab bath units are" (did_v2_go_forward_class_audit.md:1925).
- probe in several rows is one wiring. "Decided by Jess Haley, 2026-11-03 [probe in several rows is" (did_v2_go_forward_class_audit.md:1927).
- treatment word list deleted. "Decided by Jess Haley, 2026-11-03 [treatment word list" (did_v2_go_forward_class_audit.md:1929).
- one migration document per dataset. "Decided by Jess Haley, 2026-11-03 [one migration document" (did_v2_go_forward_class_audit.md:1931).
- migration formats are plain text. "Decided by Jess Haley, 2026-11-03 [migration formats are" (did_v2_go_forward_class_audit.md:1933).
- clamp mode of unrecorded probe dropped. "Decided by Jess Haley, 2026-11-03 [clamp mode of unrecorded" (did_v2_go_forward_class_audit.md:1935).
- probe with two subjects is Dab's. "Decided by Jess Haley, 2026-11-03 [probe with two subjects" (did_v2_go_forward_class_audit.md:1937).
- v1 session document id not kept. "Decided by Jess Haley, 2026-11-03 [v1 session document id" (did_v2_go_forward_class_audit.md:1939).
- waveform unit gap once. "Decided by Jess Haley, 2026-11-03 [waveform unit gap once]" (did_v2_go_forward_class_audit.md:1941).
- stated unit with no amount is a gap. "Decided by Jess Haley, 2026-11-03 [stated unit with no" (did_v2_go_forward_class_audit.md:1943).
- subject match takes the subject types. "Decided by Jess Haley, 2026-11-03 [subject match takes the" (did_v2_go_forward_class_audit.md:1945).
- gene-list mapping dimension is gene pair. "Decided by Jess Haley, 2026-11-03 [gene-list mapping" (did_v2_go_forward_class_audit.md:1947).
- dataset storage session date dropped. "Decided by Jess Haley, 2026-11-03 [dataset storage session" (did_v2_go_forward_class_audit.md:1949).
- gene pair term is NCIT Pair. "Decided by Jess Haley, 2026-11-03 [gene pair term is NCIT" (did_v2_go_forward_class_audit.md:1951).
- gene-list method text is a description. "Decided by Jess Haley, 2026-11-03 [gene-list method text is" (did_v2_go_forward_class_audit.md:1953).
- gene-list carry kinds confirmed. "Decided by Jess Haley, 2026-11-03 [gene-list carry kinds" (did_v2_go_forward_class_audit.md:1955).
- gene-list facts split. "Decided by Jess Haley, 2026-11-07 [gene-list facts split]: (" (did_v2_go_forward_class_audit.md:1957).
- gene-list history entities. "Decided by Jess Haley, 2026-11-07 [gene-list history" (did_v2_go_forward_class_audit.md:1959).
- gene-list history filled by import. "Decided by Jess Haley, 2026-11-07 [gene-list history filled" (did_v2_go_forward_class_audit.md:1961).
- gene symbol namespace kept. "Decided by Jess Haley, 2026-11-07 [gene symbol namespace" (did_v2_go_forward_class_audit.md:1963).
- annotation source is GENEPIO. "Decided by Jess Haley, 2026-11-07 [annotation source is" (did_v2_go_forward_class_audit.md:1965).
- namespace variable terms. "Decided by Jess Haley, 2026-11-07 [namespace variable" (did_v2_go_forward_class_audit.md:1967).
- no source-facts list. "Decided by Jess Haley, 2026-11-07 [no source-facts list]: (" (did_v2_go_forward_class_audit.md:1969).
- V2 branch writes V2 only. "Decided by Jess Haley, 2026-11-03 [V2 branch writes V2" (did_v2_go_forward_class_audit.md:1971).
- writers are given the session. "Decided by Jess Haley, 2026-11-03 [writers are given the" (did_v2_go_forward_class_audit.md:1973).
- dated counts in OPEN_WORK. "Decided by Jess Haley, 2026-11-03 [dated counts in" (did_v2_go_forward_class_audit.md:1975).
- v1 database read-only on the v2 line. "Decided by Jess Haley, 2026-11-03 [v1 database read-only on" (did_v2_go_forward_class_audit.md:1977).
- v1 and v2 lowercase. "Decided by Jess Haley, 2026-11-03 [v1 and v2 lowercase]: (" (did_v2_go_forward_class_audit.md:1979).
- uneven time is a keyed time value. "Decided by Jess Haley, 2026-11-03 [uneven time is a keyed" (did_v2_go_forward_class_audit.md:1981).
- voltage AFO, current NCIT. "Decided by Jess Haley, 2026-11-03 [voltage AFO, current" (did_v2_go_forward_class_audit.md:1983).
- fixed writer values not written. "Decided by Jess Haley, 2026-11-03 [fixed writer values not" (did_v2_go_forward_class_audit.md:1985).
- hartley planes are two statements. "Decided by Jess Haley, 2026-11-03 [hartley planes are two" (did_v2_go_forward_class_audit.md:1987).
- hartley plane terms. "Decided by Jess Haley, 2026-11-18 [hartley plane terms]: (" (did_v2_go_forward_class_audit.md:1989).
- hartley numbers stored, copies not. "Decided by Jess Haley, 2026-11-03 [hartley numbers stored" (did_v2_go_forward_class_audit.md:1991).
- hartley column terms. "Decided by Jess Haley, 2026-11-19 [hartley column terms]: (" (did_v2_go_forward_class_audit.md:1993).
- term picks batch 1. "Decided by Jess Haley, 2026-11-03 [term picks batch 1]: (" (did_v2_go_forward_class_audit.md:1995).
- term picks batch 1b. "Decided by Jess Haley, 2026-11-03 [term picks batch 1b]: (" (did_v2_go_forward_class_audit.md:1997).
- term picks batch 2. "Decided by Jess Haley, 2026-11-03 [term picks batch 2]: (" (did_v2_go_forward_class_audit.md:1999).
- v2 line reads and writes both. "Decided by Jess Haley, 2026-11-03 [v2 line reads and writes" (did_v2_go_forward_class_audit.md:2001).
- new database defaults to v2. "Decided by Jess Haley, 2026-11-03 [new database defaults to" (did_v2_go_forward_class_audit.md:2003).
- old names guarded in comments. "Decided by Jess Haley, 2026-11-03 [old names guarded in" (did_v2_go_forward_class_audit.md:2005).
- common species registered. "Decided by Jess Haley, 2026-11-06 [common species" (did_v2_go_forward_class_audit.md:2007).
- v2 makers after G84. "Decided by Jess Haley, 2026-11-06 [v2 makers after G84]: (" (did_v2_go_forward_class_audit.md:2009).
- hartley copies kept while files absent. "Decided by Jess Haley, 2026-11-06 [hartley copies kept" (did_v2_go_forward_class_audit.md:2011).
- new dataset named by its reference. "Decided by Jess Haley, 2026-11-06 [new dataset named by its" (did_v2_go_forward_class_audit.md:2013).
- receptive field is SNOMED's. "Decided by Jess Haley, 2026-11-06 [receptive field is" (did_v2_go_forward_class_audit.md:2015).
- JSON descriptions lowercase too. "Decided by Jess Haley, 2026-11-06 [JSON descriptions" (did_v2_go_forward_class_audit.md:2017).
- pipeline is a software entity. "Decided by Jess Haley, 2026-11-06 [pipeline is a software" (did_v2_go_forward_class_audit.md:2019).
- Kilosort importer waits for the makers. "Decided by Jess Haley, 2026-11-18 [Kilosort importer waits" (did_v2_go_forward_class_audit.md:2021).
- openMINDS export answers. "Decided by Jess Haley, 2026-11-06 [openMINDS export" (did_v2_go_forward_class_audit.md:2023).
- unrecorded probe reads general type. "Decided by Jess Haley, 2026-11-06 [unrecorded probe reads" (did_v2_go_forward_class_audit.md:2025).
- open work lives in issues. "Decided by Jess Haley, 2026-11-03 [open work lives in" (did_v2_go_forward_class_audit.md:2026).
- pending builds filed by topic. "Decided by Jess Haley, 2026-11-19 [pending builds filed by" (did_v2_go_forward_class_audit.md:2028).
- Dab map draft closed. "Decided by Jess Haley, 2026-11-19 [Dab map draft closed]: (" (did_v2_go_forward_class_audit.md:2030).
- carry-051 and carry-095 retired. "Decided by Jess Haley, 2026-11-06 [carry-051 and carry-095" (did_v2_go_forward_class_audit.md:2032).
- control pairing without trials stays carried. "Decided by Jess Haley, 2026-11-06 [control pairing without" (did_v2_go_forward_class_audit.md:2034).
- sync rule terms. "Decided by Jess Haley, 2026-11-06 [sync rule terms]: (" (did_v2_go_forward_class_audit.md:2035).
- openMINDS crosswalk on latest. "Decided by Jess Haley, 2026-11-06 [openMINDS crosswalk on" (did_v2_go_forward_class_audit.md:2037).
- crosswalk assertions registered. "Decided by Jess Haley, 2026-11-06 [crosswalk assertions" (did_v2_go_forward_class_audit.md:2039).
- unmapped roles not exported. "Decided by Jess Haley, 2026-11-06 [unmapped roles not" (did_v2_go_forward_class_audit.md:2041).
- read speed margin. "Decided by Jess Haley, 2026-11-06 [read speed margin]: (" (did_v2_go_forward_class_audit.md:2043).
- custodian exports as custodianship. "Decided by Jess Haley, 2026-11-07 [custodian exports as" (did_v2_go_forward_class_audit.md:2045).
- copyright year is a date assertion. "Decided by Jess Haley, 2026-11-07 [copyright year is a date" (did_v2_go_forward_class_audit.md:2047).
- copyright year term confirmed. "Decided by Jess Haley, 2026-11-08 [copyright year term" (did_v2_go_forward_class_audit.md:2049).
- genome assembly term. "Decided by Jess Haley, 2026-11-08 [genome assembly term]: (" (did_v2_go_forward_class_audit.md:2051).
- lock moved to NDI main. "Decided by Jess Haley, 2026-11-09 [lock moved to NDI main]" (did_v2_go_forward_class_audit.md:2053).
- one dataset exports as Dataset and version. "Decided by Jess Haley, 2026-11-07 [one dataset exports as" (did_v2_go_forward_class_audit.md:2055).
- documentation from subjectOf. "Decided by Jess Haley, 2026-11-07 [documentation from" (did_v2_go_forward_class_audit.md:2057).
- receptive field is SNOMED. "Decided by Jess Haley, 2026-11-09 [receptive field is" (did_v2_go_forward_class_audit.md:2059).
- term picks batch 3. "Decided by Jess Haley, 2026-11-09 [term picks batch 3]: (" (did_v2_go_forward_class_audit.md:2061).
- remaining quantity copies removed. "Decided by Jess Haley, 2026-11-09 [remaining quantity" (did_v2_go_forward_class_audit.md:2063).
- tenet audit 6 8 11. "Decided by Jess Haley, 2026-11-09 [tenet audit 6 8 11]: (" (did_v2_go_forward_class_audit.md:2065).
- external parents imported. "Decided by Jess Haley, 2026-11-09 [external parents" (did_v2_go_forward_class_audit.md:2067).
- purpose written by the dataset map. "Decided by Jess Haley, 2026-11-09 [purpose written by the" (did_v2_go_forward_class_audit.md:2069).
- element recognised by its links. "Decided by Jess Haley, 2026-11-10 [element recognised by" (did_v2_go_forward_class_audit.md:2071).
- ensemble has members. "Decided by Jess Haley, 2026-11-10 [ensemble has members]: (" (did_v2_go_forward_class_audit.md:2073).
- sync configuration edges are input and output. "Decided by Jess Haley, 2026-11-10 [sync configuration edges" (did_v2_go_forward_class_audit.md:2075).
- one spelling for the half-maximum point. "Decided by Jess Haley, 2026-11-10 [one spelling for the" (did_v2_go_forward_class_audit.md:2077).
- intensity slot named for the quantity. "Decided by Jess Haley, 2026-11-10 [intensity slot named for" (did_v2_go_forward_class_audit.md:2079).
- culture and alignment nodes. "Decided by Jess Haley, 2026-11-10 [culture and alignment" (did_v2_go_forward_class_audit.md:2081).
- tuning summaries in the value. "Decided by Jess Haley, 2026-11-10 [tuning summaries in the" (did_v2_go_forward_class_audit.md:2083).
- T15 inventory corrected. "Decided by Jess Haley, 2026-11-10 [T15 inventory" (did_v2_go_forward_class_audit.md:2085).
- unbound term fields sorted. "Decided by Jess Haley, 2026-11-10 [unbound term fields" (did_v2_go_forward_class_audit.md:2087).
- display label compared loosely. "Decided by Jess Haley, 2026-11-10 [display label compared" (did_v2_go_forward_class_audit.md:2089).
- four term fields bound. "Decided by Jess Haley, 2026-11-10 [four term fields bound]" (did_v2_go_forward_class_audit.md:2091).
- closing issues 2026-11-10. "Decided by Jess Haley, 2026-11-10 [closing issues" (did_v2_go_forward_class_audit.md:2093).
- culture renamed cell culture. "Decided by Jess Haley, 2026-11-10 [culture renamed cell" (did_v2_go_forward_class_audit.md:2095).
- openMINDS element description in notes. "Decided by Jess Haley, 2026-11-10 [openMINDS element" (did_v2_go_forward_class_audit.md:2097).
- dataset form lists rebuilt. "Decided by Jess Haley, 2026-11-10 [dataset form lists" (did_v2_go_forward_class_audit.md:2099).
- two corpus counts. "Decided by Jess Haley, 2026-11-10 [two corpus counts]: (" (did_v2_go_forward_class_audit.md:2101).
- statement name waits for a dataset. "Decided by Jess Haley, 2026-11-19 [statement name waits for" (did_v2_go_forward_class_audit.md:2103).
- spike clusters wait for a dataset. "Decided by Jess Haley, 2026-11-19 [spike clusters wait for" (did_v2_go_forward_class_audit.md:2105).
- strain leftovers wait for a dataset. "Decided by Jess Haley, 2026-11-19 [strain leftovers wait" (did_v2_go_forward_class_audit.md:2107).
- rare carries wait for a dataset. "Decided by Jess Haley, 2026-11-19 [rare carries wait for a" (did_v2_go_forward_class_audit.md:2109).
- epochclocktimes is pyraview's block. "Decided by Jess Haley, 2026-11-19 [epochclocktimes is" (did_v2_go_forward_class_audit.md:2111).
- variable terms registered before required. "Decided by Jess Haley, 2026-11-19 [variable terms" (did_v2_go_forward_class_audit.md:2113).
- variable terms batch 1. "Decided by Jess Haley, 2026-11-19 [variable terms batch 1]" (did_v2_go_forward_class_audit.md:2115).
- stimulus body link waits on the time model. "Decided by Jess Haley, 2026-11-10 [stimulus body link waits" (did_v2_go_forward_class_audit.md:2117).
- spike waveforms are two calculations. "Decided by Jess Haley, 2026-11-10 [spike waveforms are two" (did_v2_go_forward_class_audit.md:2119).
- spike waveforms built now. "Decided by Jess Haley, 2026-11-10 [spike waveforms built" (did_v2_go_forward_class_audit.md:2121).
- no-migrator classes: build one, count six. "Decided by Jess Haley, 2026-11-10 [no-migrator classes" (did_v2_go_forward_class_audit.md:2123).
- a fit is about its input's subject. "Decided by Jess Haley, 2026-11-10 [a fit is about its" (did_v2_go_forward_class_audit.md:2125).
- voltage-to-firing-rate writers found. "Decided by Jess Haley, 2026-11-10 [voltage-to-firing-rate" (did_v2_go_forward_class_audit.md:2127).
- site map waits with contact geometry. "Decided by Jess Haley, 2026-11-10 [site map waits with" (did_v2_go_forward_class_audit.md:2129).
- unnamed measurement kind needs a map. "Decided by Jess Haley, 2026-11-10 [unnamed measurement kind" (did_v2_go_forward_class_audit.md:2131).
- distance and its metadata are one statement. "Decided by Jess Haley, 2026-11-10 [distance and its" (did_v2_go_forward_class_audit.md:2133).
- stimulus presentation leftovers wait for a dataset. "Decided by Jess Haley, 2026-11-10 [stimulus presentation" (did_v2_go_forward_class_audit.md:2135).
- probes read from the derived index. "Decided by Jess Haley, 2026-11-10 [probes read from the" (did_v2_go_forward_class_audit.md:2137).
- assertion wins while written. "Decided by Jess Haley, 2026-11-10 [assertion wins while" (did_v2_go_forward_class_audit.md:2139).
- probes from the index keep v1's duplicates. "Decided by Jess Haley, 2026-11-10 [probes from the index" (did_v2_go_forward_class_audit.md:2141).
- valid interval waits for a dataset. "Decided by Jess Haley, 2026-11-10 [valid interval waits for" (did_v2_go_forward_class_audit.md:2143).
- focus on classes in the corpora. "Decided by Jess Haley, 2026-11-10 [focus on classes in the" (did_v2_go_forward_class_audit.md:2145).
- unlinked device is not an element. "Decided by Jess Haley, 2026-11-11 [unlinked device is not" (did_v2_go_forward_class_audit.md:2148).
- jrclust settings-file name dropped. "Decided by Jess Haley, 2026-11-11 [jrclust settings-file" (did_v2_go_forward_class_audit.md:2150).
- tuning stated value is a condition. "Decided by Jess Haley, 2026-11-11 [tuning stated value is a" (did_v2_go_forward_class_audit.md:2152).
- tuning fit coefficients named by symbol. "Decided by Jess Haley, 2026-11-11 [tuning fit coefficients" (did_v2_go_forward_class_audit.md:2154).
- contrast sensitivity repeated fit is a known v1 defect. "Decided by Jess Haley, 2026-11-12 [contrast sensitivity" (did_v2_go_forward_class_audit.md:2156).
- known v1 defects list. "Decided by Jess Haley, 2026-11-12 [known v1 defects list]: (" (did_v2_go_forward_class_audit.md:2158).
- Dab gets a v2 import. "Decided by Jess Haley, 2026-11-12 [Dab gets a v2 import]: (" (did_v2_go_forward_class_audit.md:2160).
- archive segment lengths measured after the second pass. "Decided by Jess Haley, 2026-11-12 [archive segment lengths" (did_v2_go_forward_class_audit.md:2162).
- archive file list compared as a set. "Decided by Jess Haley, 2026-11-12 [archive file list" (did_v2_go_forward_class_audit.md:2164).
- uneven time rewritten from the epoch start. "Decided by Jess Haley, 2026-11-12 [uneven time rewritten" (did_v2_go_forward_class_audit.md:2166).
- bath concentration prefixes convert to molar. "Decided by Jess Haley, 2026-11-12 [bath concentration" (did_v2_go_forward_class_audit.md:2168).
- ids from content when v1 states none. "Decided by Jess Haley, 2026-11-12 [ids from content when v1" (did_v2_go_forward_class_audit.md:2170).
- pipeline order counts from 0. "Decided by Jess Haley, 2026-11-12 [pipeline order counts" (did_v2_go_forward_class_audit.md:2172).
- copyright year precision is year. "Decided by Jess Haley, 2026-11-12 [copyright year precision" (did_v2_go_forward_class_audit.md:2174).
- copyright from another tool is emitted. "Decided by Jess Haley, 2026-11-12 [copyright from another" (did_v2_go_forward_class_audit.md:2176).
- pipeline steps use member of. "Decided by Jess Haley, 2026-11-12 [pipeline steps use" (did_v2_go_forward_class_audit.md:2178).
- dataset DOI on the version. "Decided by Jess Haley, 2026-11-12 [dataset DOI on the" (did_v2_go_forward_class_audit.md:2180).
- first documentation exported. "Decided by Jess Haley, 2026-11-12 [first documentation" (did_v2_go_forward_class_audit.md:2182).
- v2 makers write v2 directly. "Decided by Jess Haley, 2026-11-12 [v2 makers write v2" (did_v2_go_forward_class_audit.md:2184).
- author roles read from author edges. "Decided by Jess Haley, 2026-11-12 [author roles read from" (did_v2_go_forward_class_audit.md:2186).
- depends on name not written when it equals the edge. "Decided by Jess Haley, 2026-11-12 [depends on name not" (did_v2_go_forward_class_audit.md:2188).
- tuning axes named from the varied property. "Decided by Jess Haley, 2026-11-12 [tuning axes named from" (did_v2_go_forward_class_audit.md:2190).
- openMINDS terms map through equivalent. "Decided by Jess Haley, 2026-11-12 [openMINDS terms map" (did_v2_go_forward_class_audit.md:2192).
- input signal treatment is a method parameter. "Decided by Jess Haley, 2026-11-12 [input signal treatment" (did_v2_go_forward_class_audit.md:2194).
- spike unit quality and mean waveform terms. "Decided by Jess Haley, 2026-11-12 [spike unit quality and" (did_v2_go_forward_class_audit.md:2196).
- observes retires on a matching manipulation. "Decided by Jess Haley, 2026-11-12 [observes retires on a" (did_v2_go_forward_class_audit.md:2198).
- response type harmonics are integers. "Decided by Jess Haley, 2026-11-12 [response type harmonics" (did_v2_go_forward_class_audit.md:2200).
- response computed from the spike times. "Decided by Jess Haley, 2026-11-12 [response computed from" (did_v2_go_forward_class_audit.md:2202).
- agreeing untied sources count as one. "Decided by Jess Haley, 2026-11-12 [agreeing untied sources" (did_v2_go_forward_class_audit.md:2204).
- orphaned response settings are an accepted loss. "Decided by Jess Haley, 2026-11-12 [orphaned response" (did_v2_go_forward_class_audit.md:2206).
- ingest writes v2 directly. "Decided by Jess Haley, 2026-11-17 [ingest writes v2" (did_v2_go_forward_class_audit.md:2208).
- event channels are time-valued observations. "Decided by Jess Haley, 2026-11-17 [event channels are" (did_v2_go_forward_class_audit.md:2210).
- ingested body members use the schema's names. "Decided by Jess Haley, 2026-11-17 [ingested body members" (did_v2_go_forward_class_audit.md:2212).
- scale carries the reader's unit. "Decided by Jess Haley, 2026-11-17 [scale carries the" (did_v2_go_forward_class_audit.md:2214).
- event channel variable terms. "Decided by Jess Haley, 2026-11-17 [event channel variable" (did_v2_go_forward_class_audit.md:2216).
- event channel observes its wired device. "Decided by Jess Haley, 2026-11-17 [event channel observes" (did_v2_go_forward_class_audit.md:2218).
- unpacked event bodies are uncompressed. "Decided by Jess Haley, 2026-11-17 [unpacked event bodies" (did_v2_go_forward_class_audit.md:2220).
- unpacked events file is removed. "Decided by Jess Haley, 2026-11-17 [unpacked events file is" (did_v2_go_forward_class_audit.md:2222).
- removed file locations are an accepted loss. "Decided by Jess Haley, 2026-11-18 [removed file locations" (did_v2_go_forward_class_audit.md:2224).
- removed time segment locations are an accepted loss. "Decided by Jess Haley, 2026-11-19 [removed time segment" (did_v2_go_forward_class_audit.md:2226).
- several marker numbers are a second dimension. "Decided by Jess Haley, 2026-11-17 [several marker numbers" (did_v2_go_forward_class_audit.md:2228).
- marker code position term. "Decided by Jess Haley, 2026-11-19 [marker code position" (did_v2_go_forward_class_audit.md:2230).
- channel list rows get v2 homes. "Decided by Jess Haley, 2026-11-17 [channel list rows get v2" (did_v2_go_forward_class_audit.md:2232).
- event row defaults are notation. "Decided by Jess Haley, 2026-11-18 [event row defaults are" (did_v2_go_forward_class_audit.md:2234).
- channel name is an identifier. "Decided by Jess Haley, 2026-11-17 [channel name is an" (did_v2_go_forward_class_audit.md:2236).
- ingested block terms confirmed. "Decided by Jess Haley, 2026-11-17 [ingested block terms" (did_v2_go_forward_class_audit.md:2238).
- migrated body members renamed. "Decided by Jess Haley, 2026-11-17 [migrated body members" (did_v2_go_forward_class_audit.md:2240).
- stimulator link lives in the presentations. "Decided by Jess Haley, 2026-11-17 [stimulator link lives in" (did_v2_go_forward_class_audit.md:2242).
- observes retires in the second pass. "Decided by Jess Haley, 2026-11-17 [observes retires in the" (did_v2_go_forward_class_audit.md:2244).
- observes kept on several entities. "Decided by Jess Haley, 2026-11-19 [observes kept on several" (did_v2_go_forward_class_audit.md:2246).
- bath manipulation retires observes. "Decided by Jess Haley, 2026-11-19 [bath manipulation" (did_v2_go_forward_class_audit.md:2248).
- time channel is a per-channel covariate. "Decided by Jess Haley, 2026-11-17 [time channel is a" (did_v2_go_forward_class_audit.md:2250).
- harmonic is a field beside the response type. "Decided by Jess Haley, 2026-11-17 [harmonic is a field" (did_v2_go_forward_class_audit.md:2252).
- no transfer term on Haley moves. "Decided by Jess Haley, 2026-11-17 [no transfer term on" (did_v2_go_forward_class_audit.md:2254).
- digital scale is unitless. "Decided by Jess Haley, 2026-11-17 [digital scale is" (did_v2_go_forward_class_audit.md:2256).
- duplicate parts merged in DID. "Decided by Jess Haley, 2026-11-17 [duplicate parts merged" (did_v2_go_forward_class_audit.md:2258).
- part re-keyed when its side arrives. "Decided by Jess Haley, 2026-11-17 [part re-keyed when its" (did_v2_go_forward_class_audit.md:2260).
- tidy the spatial status. "Decided by Jess Haley, 2026-11-17 [tidy the spatial" (did_v2_go_forward_class_audit.md:2262).
- tied multi-clock sources wait for a dataset. "Decided by Jess Haley, 2026-11-17 [tied multi-clock sources" (did_v2_go_forward_class_audit.md:2264).
- tuning label choices confirmed. "Decided by Jess Haley, 2026-11-17 [tuning label choices" (did_v2_go_forward_class_audit.md:2266).
- copyright round-trip losses. "Decided by Jess Haley, 2026-11-17 [copyright round-trip" (did_v2_go_forward_class_audit.md:2268).
- non-specimen channel groups get their own owner. "Decided by Jess Haley, 2026-11-17 [non-specimen channel" (did_v2_go_forward_class_audit.md:2270).
- documentation identifier prefers a DOI. "Decided by Jess Haley, 2026-11-17 [documentation identifier" (did_v2_go_forward_class_audit.md:2272).
- role source left to the import. "Decided by Jess Haley, 2026-11-17 [role source left to the" (did_v2_go_forward_class_audit.md:2274).
- Dab stimulators with deferred baths read the animal. "Decided by Jess Haley, 2026-11-19 [Dab stimulators with" (did_v2_go_forward_class_audit.md:2276).
- openMINDS ids rebuild the subject terms. "Decided by Jess Haley, 2026-11-19 [openMINDS ids rebuild" (did_v2_go_forward_class_audit.md:2278).
- region part ids computed. "Decided by Jess Haley, 2026-11-19 [region part ids" (did_v2_go_forward_class_audit.md:2280).
- metadata editor id and datestamp not kept. "Decided by Jess Haley, 2026-11-19 [metadata editor id and" (did_v2_go_forward_class_audit.md:2282).
- awaiting carry rows cite an issue. "Decided by Jess Haley, 2026-11-19 [awaiting carry rows cite" (did_v2_go_forward_class_audit.md:2284).
- BNST neuron types registered. "Decided by Jess Haley, 2026-11-19 [BNST neuron types" (did_v2_go_forward_class_audit.md:2286).
- hartley frame times are onset times. "Decided by Jess Haley, 2026-11-19 [hartley frame times are" (did_v2_go_forward_class_audit.md:2288).
- knockin is NCIT Knock-in. "Decided by Jess Haley, 2026-11-19 [knockin is NCIT" (did_v2_go_forward_class_audit.md:2290).
- carry-056 waits for a dataset. "Decided by Jess Haley, 2026-11-19 [carry-056 waits for a" (did_v2_go_forward_class_audit.md:2292).
- openMINDS minted ids are an accepted loss. "Decided by Jess Haley, 2026-11-19 [openMINDS minted ids are" (did_v2_go_forward_class_audit.md:2294).
- read speed check after getprobes. "Decided by Jess Haley, 2026-11-19 [read speed check after" (did_v2_go_forward_class_audit.md:2296).
- session anchors pass removed. "Decided by Jess Haley, 2026-11-19 [session anchors pass" (did_v2_go_forward_class_audit.md:2298).
- DID first pass keeps observes. "Decided by Jess Haley, 2026-11-19 [DID first pass keeps" (did_v2_go_forward_class_audit.md:2300).
- channel group owners details. "Decided by Jess Haley, 2026-11-19 [channel group owners" (did_v2_go_forward_class_audit.md:2302).
- strain fields checked after the second pass. "Decided by Jess Haley, 2026-11-19 [strain fields checked" (did_v2_go_forward_class_audit.md:2304).
- carry rows cite issues, not OPEN_WORK. "Decided by Jess Haley, 2026-11-19 [carry rows cite issues" (did_v2_go_forward_class_audit.md:2306).
- local identifier required only where looked up. "Decided by Jess Haley, 2026-11-19 [local identifier" (did_v2_go_forward_class_audit.md:2308).
- metadata editor form is the source. "Decided by Jess Haley, 2026-11-19 [metadata editor form is" (did_v2_go_forward_class_audit.md:2310).
- lab-made strain ids are an accepted loss too. "Decided by Jess Haley, 2026-11-19 [lab-made strain ids are" (did_v2_go_forward_class_audit.md:2312).
- metadata editor graph compared with its form. "Decided by Jess Haley, 2026-11-20 [metadata editor graph" (did_v2_go_forward_class_audit.md:2314).
- strain entities per dataset. "Decided by Jess Haley, 2026-11-22 [strain entities per" (did_v2_go_forward_class_audit.md:2316).
- side said about its region. "Decided by Jess Haley, 2026-11-25 [side said about its" (did_v2_go_forward_class_audit.md:2318).
- openMINDS graph with a carried form. "Decided by Jess Haley, 2026-11-25 [openMINDS graph with a" (did_v2_go_forward_class_audit.md:2320).
- several metadata forms are malformed. "Decided by Jess Haley, 2026-11-25 [several metadata forms" (did_v2_go_forward_class_audit.md:2322).
- carry-116 kept. "Decided by Jess Haley, 2026-11-25 [carry-116 kept]: (" (did_v2_go_forward_class_audit.md:2324).
- carry-116 home is the instance list. "Decided by Jess Haley, 2026-11-26 [carry-116 home is the" (did_v2_go_forward_class_audit.md:2326).
- Haley B2 and B6 leave too. "Decided by Jess Haley, 2026-11-26 [Haley B2 and B6 leave" (did_v2_go_forward_class_audit.md:2328).
- dataset map lines belong to the imports. "Decided by Jess Haley, 2026-11-26 [dataset map lines belong" (did_v2_go_forward_class_audit.md:2330).
- malformed cases cite carry-120. "Decided by Jess Haley, 2026-11-26 [malformed cases cite" (did_v2_go_forward_class_audit.md:2332).
- recording attribution only for recordings. "Decided by Jess Haley, 2026-11-26 [recording attribution" (did_v2_go_forward_class_audit.md:2334).
- generic stage does not guess from words. "Decided by Jess Haley, 2026-11-26 [generic stage does not" (did_v2_go_forward_class_audit.md:2336).
- second pass carries labels and unknown clocks. "Decided by Jess Haley, 2026-11-26 [second pass carries" (did_v2_go_forward_class_audit.md:2338).
- NewStim recipes applied by default. "Decided by Jess Haley, 2026-11-26 [NewStim recipes applied" (did_v2_go_forward_class_audit.md:2340).
- corpus code bins closed. "Decided by Jess Haley, 2026-11-26 [corpus code bins" (did_v2_go_forward_class_audit.md:2342).
- build state lives in issues. "Decided by Jess Haley, 2026-11-26 [build state lives in" (did_v2_go_forward_class_audit.md:2344).
- element whose probe maps name another subject is malformed. "Decided by Jess Haley, 2026-11-26 [element whose probe maps" (did_v2_go_forward_class_audit.md:2346).
- presentation clock read from its time file. "Decided by Jess Haley, 2026-11-26 [presentation clock read" (did_v2_go_forward_class_audit.md:2348).
- Dab map re-parents region parts under slices. "Decided by Jess Haley, 2026-11-26 [Dab map re-parents" (did_v2_go_forward_class_audit.md:2350).
- instrument of an epoch interaction is a link. "Decided by Jess Haley, 2026-11-26 [instrument of an epoch" (did_v2_go_forward_class_audit.md:2352).
- decision tests check rules, not counts. "Decided by Jess Haley, 2026-11-26 [decision tests check" (did_v2_go_forward_class_audit.md:2354).
- ngrid block into sampled_body. "Decided by Jess Haley, 2026-10-23 [ngrid block into" (did_v2_image_model_plan.md:226).
- 2026-10-09. "TEAM-SIGN-OFF: jess / 2026-10-09 -- membership of a session" (did_v2_linked_session_plan.md:95).
- linked_session withdrawn. "Decided by Jess Haley, 2026-10-25 [linked_session" (did_v2_linked_session_plan.md:97).
- nested studies. "Decided by Jess Haley, 2026-10-23 [nested studies]: a study" (did_v2_linked_session_plan.md:99).
- older linked_session reader deleted. "Decided by Jess Haley, 2026-10-31 [older linked_session" (did_v2_linked_session_plan.md:101).
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
- one shape for measured numbers. "Decided by Jess Haley, 2026-11-17 [one shape for measured" (did_v2_numeric_shape_plan.md:283).
- numeric shape details. "Decided by Jess Haley, 2026-11-17 [numeric shape details]: (" (did_v2_numeric_shape_plan.md:285).
- series readings share a source record. "Decided by Jess Haley, 2026-11-17 [series readings share a" (did_v2_numeric_shape_plan.md:287).
- no migrated database is kept. "Decided by Jess Haley, 2026-11-19 [no migrated database is" (did_v2_numeric_shape_plan.md:289).
- numeric step 3 leftovers. "Decided by Jess Haley, 2026-11-19 [numeric step 3" (did_v2_numeric_shape_plan.md:291).
- om Time is seconds. "Decided by Jess Haley, 2026-11-19 [om Time is seconds]: (" (did_v2_numeric_shape_plan.md:293).
- source numeric is number or text. "Decided by Jess Haley, 2026-11-19 [source numeric is number" (did_v2_numeric_shape_plan.md:295).
- logical value declared like the rest. "Decided by Jess Haley, 2026-11-26 [logical value declared" (did_v2_numeric_shape_plan.md:297).
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
- calculation-os-optional. "Decided by Jess Haley, 2026-10-21 [calculation-os-optional]" (did_v2_spatial_transcriptomics_plan.md:298).
- formulation strain ingredient. "TEAM-SIGN-OFF [formulation strain ingredient]" (did_v2_spatial_transcriptomics_plan.md:614).
- ontology image is an observation of its region. "Decided by Jess Haley, 2026-10-21 [ontology image is an" (did_v2_spatial_transcriptomics_plan.md:616).
- non-area image node. "Decided by Jess Haley, 2026-10-21 [non-area image node]: on" (did_v2_spatial_transcriptomics_plan.md:618).
- calculation-software-optional decided. "Decided by Jess Haley, 2026-10-22" (did_v2_spatial_transcriptomics_plan.md:622).
- non-area image node, revisited. "Decided by Jess Haley, 2026-10-22 [non-area image node" (did_v2_spatial_transcriptomics_plan.md:624).
- coordinate system names. "Decided by Jess Haley, 2026-10-22 [coordinate system names]" (did_v2_spatial_transcriptomics_plan.md:626).
- tissue section counts. "Decided by Jess Haley, 2026-11-07 [tissue section counts]: (" (did_v2_spatial_transcriptomics_plan.md:635).
- tiles are opaque bodies. "Decided by Jess Haley, 2026-11-07 [tiles are opaque" (did_v2_spatial_transcriptomics_plan.md:637).
- spatial transcriptomics is EFO. "Decided by Jess Haley, 2026-11-07 [spatial transcriptomics" (did_v2_spatial_transcriptomics_plan.md:639).
- UMI count term. "Decided by Jess Haley, 2026-11-07 [UMI count term]: (" (did_v2_spatial_transcriptomics_plan.md:641).
- spatial transcriptomics row is EFO. "Decided by Jess Haley, 2026-11-08 [spatial transcriptomics" (did_v2_spatial_transcriptomics_plan.md:643).
- UMI count synonym kept. "Decided by Jess Haley, 2026-11-08 [UMI count synonym kept]" (did_v2_spatial_transcriptomics_plan.md:645).
- gene totals kept whole. "Decided by Jess Haley, 2026-11-09 [gene totals kept whole]" (did_v2_spatial_transcriptomics_plan.md:647).
- spatial counts during the session. "Decided by Jess Haley, 2026-11-09 [spatial counts during" (did_v2_spatial_transcriptomics_plan.md:649).
- spatial label as notes. "Decided by Jess Haley, 2026-11-09 [spatial label as notes]" (did_v2_spatial_transcriptomics_plan.md:651).
- spatial chip is a device. "Decided by Jess Haley, 2026-11-09 [spatial chip is a" (did_v2_spatial_transcriptomics_plan.md:653).
- pipeline version as text. "Decided by Jess Haley, 2026-11-09 [pipeline version as" (did_v2_spatial_transcriptomics_plan.md:655).
- one coordinate system per chip. "Decided by Jess Haley, 2026-11-09 [one coordinate system" (did_v2_spatial_transcriptomics_plan.md:659).
- cell table split. "Decided by Jess Haley, 2026-11-09 [cell table split]: (" (did_v2_spatial_transcriptomics_plan.md:661).
- cell id is NCIT Identifier. "Decided by Jess Haley, 2026-11-09 [cell id is NCIT" (did_v2_spatial_transcriptomics_plan.md:663).
- cell table terms. "Decided by Jess Haley, 2026-11-09 [cell table terms]: (" (did_v2_spatial_transcriptomics_plan.md:665).
- cell outlines converted. "Decided by Jess Haley, 2026-11-09 [cell outlines" (did_v2_spatial_transcriptomics_plan.md:667).
- area written without a unit. "Decided by Jess Haley, 2026-11-09 [area written without a" (did_v2_spatial_transcriptomics_plan.md:669).
- spatial field bindings superseded. "Decided by Jess Haley, 2026-11-09 [spatial field bindings" (did_v2_spatial_transcriptomics_plan.md:671).
- cell type label settings are method parameters. "Decided by Jess Haley, 2026-11-10 [cell type label settings" (did_v2_spatial_transcriptomics_plan.md:673).
- spatial transcriptomics waits for a dataset. "Decided by Jess Haley, 2026-11-10 [spatial transcriptomics" (did_v2_spatial_transcriptomics_plan.md:675).
- taxonomy level term waits for a dataset. "Decided by Jess Haley, 2026-11-19 [taxonomy level term" (did_v2_spatial_transcriptomics_plan.md:677).
- wiring recorded once. "Decided by Jess Haley, 2026-11-09 [wiring recorded once]: (" (did_v2_standing_wiring_plan.md:183).
- wiring per ingest. "Decided by Jess Haley, 2026-11-09 [wiring per ingest]: (" (did_v2_standing_wiring_plan.md:185).
- stimulator manipulation dropped. "Decided by Jess Haley, 2026-11-09 [stimulator manipulation" (did_v2_standing_wiring_plan.md:187).
- repeat on a time. "Decided by Jess Haley, 2026-11-09 [repeat on a time]: (" (did_v2_standing_wiring_plan.md:193).
- probe map rows compared as a set. "Decided by Jess Haley, 2026-11-09 [probe map rows compared" (did_v2_standing_wiring_plan.md:195).
- acquisition system is a device entity. "Decided by Jess Haley, 2026-11-19 [acquisition system is a" (did_v2_standing_wiring_plan.md:197).
- migration mints the device by name. "Decided by Jess Haley, 2026-11-19 [migration mints the" (did_v2_standing_wiring_plan.md:199).
- a rig's clock belongs to its device. "Decided by Jess Haley, 2026-11-19 [a rig's clock belongs to" (did_v2_standing_wiring_plan.md:201).
- wiring read from the database only. "Decided by Jess Haley, 2026-11-19 [wiring read from the" (did_v2_standing_wiring_plan.md:203).
- no new hidden epoch-id files. "Decided by Jess Haley, 2026-11-19 [no new hidden epoch-id" (did_v2_standing_wiring_plan.md:205).
- only wired channels recorded. "Decided by Jess Haley, 2026-11-19 [only wired channels" (did_v2_standing_wiring_plan.md:207).
- one device per session. "Decided by Jess Haley, 2026-11-19 [one device per session]" (did_v2_standing_wiring_plan.md:209).
- stimulator has no subject of its own. "Decided by Jess Haley, 2026-11-19 [stimulator has no" (did_v2_standing_wiring_plan.md:211).
- stimulator subject carried as needing information. "Decided by Jess Haley, 2026-11-19 [stimulator subject" (did_v2_standing_wiring_plan.md:213).
- one-field carry in the migration report. "Decided by Jess Haley, 2026-11-19 [one-field carry in the" (did_v2_standing_wiring_plan.md:215).
- recording probe subject carried the same way. "Decided by Jess Haley, 2026-11-19 [recording probe subject" (did_v2_standing_wiring_plan.md:217).
- uneven time groups and mismatches. "Decided by Jess Haley, 2026-11-19 [uneven time groups and" (did_v2_standing_wiring_plan.md:219).
- time channel row is notation. "Decided by Jess Haley, 2026-11-19 [time channel row is" (did_v2_standing_wiring_plan.md:221).
- text channel entries are a JSON array. "Decided by Jess Haley, 2026-11-19 [text channel entries are" (did_v2_standing_wiring_plan.md:223).
- time row and text channel readings. "Decided by Jess Haley, 2026-11-19 [time row and text" (did_v2_standing_wiring_plan.md:228).
- archive with no digital channel. "Decided by Jess Haley, 2026-11-19 [archive with no digital" (did_v2_standing_wiring_plan.md:230).
- device id required and named by the rig. "Decided by Jess Haley, 2026-11-19 [device id required and" (did_v2_standing_wiring_plan.md:232).
- readtimeseries timed with NDI Cloud. "Decided by Jess Haley, 2026-11-19 [readtimeseries timed" (did_v2_standing_wiring_plan.md:234).
- acquisition configuration renamed. "Decided by Jess Haley, 2026-11-19 [acquisition" (did_v2_standing_wiring_plan.md:236).
- time group with several time channels split. "Decided by Jess Haley, 2026-11-19 [time group with several" (did_v2_standing_wiring_plan.md:238).
- NDI-compress keeps a V2 branch. "Decided by Jess Haley, 2026-11-19 [NDI-compress keeps a V2" (did_v2_standing_wiring_plan.md:240).
- multi-code markers keep every code. "Decided by Jess Haley, 2026-11-19 [multi-code markers keep" (did_v2_standing_wiring_plan.md:242).
- Intan aux names no time channel. "Decided by Jess Haley, 2026-11-19 [Intan aux names no time" (did_v2_standing_wiring_plan.md:244).
- session folder wiring migrated. "Decided by Jess Haley, 2026-11-19 [session folder wiring" (did_v2_standing_wiring_plan.md:246).
- stimulus log owned by its presentation. "Decided by Jess Haley, 2026-11-19 [stimulus log owned by" (did_v2_standing_wiring_plan.md:248).
- rig device written by NDI writers. "Decided by Jess Haley, 2026-11-22 [rig device written by" (did_v2_standing_wiring_plan.md:250).
- stimulus log fallback is a manipulation. "Decided by Jess Haley, 2026-11-25 [stimulus log fallback is" (did_v2_standing_wiring_plan.md:252).
- unused split time channel kept. "Decided by Jess Haley, 2026-11-25 [unused split time" (did_v2_standing_wiring_plan.md:254).
- time channels out of order are malformed. "Decided by Jess Haley, 2026-11-25 [time channels out of" (did_v2_standing_wiring_plan.md:256).
- unnamed rig is malformed. "Decided by Jess Haley, 2026-11-26 [unnamed rig is" (did_v2_standing_wiring_plan.md:258).
- no migration before the time-reading fix. "Decided by Jess Haley, 2026-11-26 [no migration before the" (did_v2_standing_wiring_plan.md:260).
- no observes relation in v2. "Decided by Jess Haley, 2026-11-26 [no observes relation in" (did_v2_standing_wiring_plan.md:262).
- epochs added after migration read as v1. "Decided by Jess Haley, 2026-11-26 [epochs added after" (did_v2_standing_wiring_plan.md:264).
- stimulus -- visual_grating_manipulation reconciliation. "TEAM-SIGN-OFF [stimulus -- visual_grating_manipulation" (did_v2_stimulus_model_plan.md:304).
- onsets on the sequence, #73 audit 2 D11. "TEAM-SIGN-OFF [onsets on the sequence, #73 audit 2 D11]" (did_v2_stimulus_model_plan.md:372).
- presentation with no subject. "Decided by Jess Haley, 2026-10-21 [presentation with no" (did_v2_stimulus_model_plan.md:396).
- response parameters as a shared method. "Decided by Jess Haley, 2026-10-21 [response parameters as a" (did_v2_stimulus_response_model_plan.md:612).
- control input told apart by its document. "Decided by Jess Haley, 2026-10-21 [control input told apart" (did_v2_stimulus_response_model_plan.md:614).
- empty response settings. "Decided by Jess Haley, 2026-10-21 [empty response" (did_v2_stimulus_response_model_plan.md:616).
- control record is a calculation. "Decided by Jess Haley, 2026-10-21 [control record is a" (did_v2_stimulus_response_model_plan.md:618).
- presentation times from the file. "Decided by Jess Haley, 2026-10-22 [presentation times from" (did_v2_stimulus_response_model_plan.md:624).
- presentation file declared. "Decided by Jess Haley, 2026-10-22 [presentation file" (did_v2_stimulus_response_model_plan.md:627).
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
- tenet amendments 2026-10-21. "TEAM-SIGN-OFF [tenet amendments 2026-10-21], below): one" (did_v2_tenets.md:868).
- tenet amendments 2026-10-20. "TEAM-SIGN-OFF [tenet amendments 2026-10-20]: jess /" (did_v2_tenets.md:1093).
- tenet amendments 2026-10-21. "TEAM-SIGN-OFF [tenet amendments 2026-10-21]" (did_v2_tenets.md:1095).
- tenet T20, group entities. "TEAM-SIGN-OFF [tenet T20, group entities]" (did_v2_tenets.md:1096).
- tenet signature text. "Decided by Jess Haley, 2026-10-22 [tenet signature text]" (did_v2_tenets.md:1098).
- T1 and T5 signed. "Decided by Jess Haley, 2026-10-22 [T1 and T5 signed]: the" (did_v2_tenets.md:1100).
- T2 time-varying property. "Decided by Jess Haley, 2026-10-22 [T2 time-varying" (did_v2_tenets.md:1102).
- ordered inputs. "Decided by Jess Haley, 2026-10-22 [ordered inputs]: T20's" (did_v2_tenets.md:1104).
- tenet stale names. "Decided by Jess Haley, 2026-10-22 [tenet stale names]: the" (did_v2_tenets.md:1106).
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
- oridir half-height values. "Decided by Jess Haley, 2026-11-09 [oridir half-height" (did_v2_tuning_model_plan.md:275).
- frequency tuning keeps Inf. "Decided by Jess Haley, 2026-11-09 [frequency tuning keeps" (did_v2_tuning_model_plan.md:277).
- tuning selection rule stated once. "Decided by Jess Haley, 2026-11-09 [tuning selection rule" (did_v2_tuning_model_plan.md:279).
- calculator mixin dropped (#73). "TEAM-SIGN-OFF [calculator mixin dropped (#73)]" (team_signoff_lines_DRAFT.md:13).
- observation vs calculation (#73). "TEAM-SIGN-OFF [observation vs calculation (#73)]" (team_signoff_lines_DRAFT.md:16).
- tuning restructure (#73). "TEAM-SIGN-OFF [tuning restructure (#73)]" (team_signoff_lines_DRAFT.md:19).

## v1 source side (from the coverage ledger)

| disposition | count |
|---|---|
| consumed by migrator (no tombstone) | 95 |
| no V_eta home, no migrator -- UNVERIFIED | 14 |
| UNMAPPED (needs a V_eta home) | 3 |
| test/demo fixture (non-production) | 2 |
| dissolved → subject | 1 |
| persist | 1 |

**UNVERIFIED** -- no V_eta home, no migrator, fate never established. These strand today:

- `app`
- `calculator`
- `epochclocktimes`
- `epochid`
- `filter`
- `generic_file`
- `imageCollection`
- `imageStack_parameters`
- `ngrid`
- `projectvar`
- `stimulus_parameter_table`
- `stimulus_response`
- `stimulus_response_scalar_parameters`
- `valid_interval`

