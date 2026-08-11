# V_eta status board (GENERATED -- do not hand-edit)

Regenerate with `python3 tools/status_board.py`. CI runs `--check`.

State lives here. The plan documents under `schemas/` keep the RATIONALE
for each model; this board owns *how much is left and what exactly*.

## Where V_eta stands

| | count |
|---|---|
| target classes | 247 |
| settled (persist) | 164 |
| settled (retire) | 52 |
| **still open (`in_progress`)** | **31** |
| **`retire` with no migrator YET** | **1** |
| open **decision families** | **19** |
| &nbsp;&nbsp;DECIDED and signed off, awaiting build | 18 |
| &nbsp;&nbsp;decided in a walkthrough, **awaiting a signature** | 0 |
| &nbsp;&nbsp;**written up by Claude alone, unreviewed** | **0** |
| &nbsp;&nbsp;nobody has proposed anything yet | 1 |

| open-class BUILD/PROOF state (derived, see below) | count |
|---|---|
| (a) decided, nothing built | 7 |
| (b) built, awaiting corpus proof | 24 |
| (c) corpus: 0 survivors in the corpora read | 0 |
| (?) UNMEASURED -- no build evidence was ever taken | 0 |

The class count is not the work count. 31 open classes are 19 decisions, because most open classes move as a family.

**1 of those 19 are not settled**: 0 awaiting a signature on a decision already taken, 0 written up by Claude alone and unreviewed, 1 with nothing proposed. Only 18 are signed off.

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
| build: V_eta migrator packages read | `DID-matlab:migrators_j`, `NDI-matlab:ndi_second_pass`, `DID-matlab:convert` |
| build: &nbsp;&nbsp;-- of those, per-document migrator | `DID-matlab:migrators_j`, `NDI-matlab:ndi_second_pass` |
| build: &nbsp;&nbsp;-- of those, batch post-pass | `DID-matlab:convert` |
| build: migrator files inspected | 163 |
| build: &nbsp;&nbsp;-- of those, per-document migrator | 139 |
| build: &nbsp;&nbsp;-- of those, batch post-pass | 24 |
| build: V_zeta files DELIBERATELY EXCLUDED (`+migrators`, `+migrators_i`, `+migrators_e`) | 38 |
| build: migrator lines inspected | 28825 |
| build: &nbsp;&nbsp;-- of those, per-document migrator | 20094 |
| build: &nbsp;&nbsp;-- of those, batch post-pass | 8731 |
| build: classes queried | 31 |
| build: open classes MINTED as a document class | 8 |
| build: &nbsp;&nbsp;-- open classes minted in a per-document migrator (rows overlap) | 8 |
| build: &nbsp;&nbsp;-- open classes minted in a batch post-pass (rows overlap) | 1 |
| build: of those, discounted (decision retires the class) | 3 |
| build: `document_class` writes whose class name is a VARIABLE | 9 |
| build: &nbsp;&nbsp;-- of those, in a per-document migrator | 6 |
| build: &nbsp;&nbsp;-- of those, in a batch post-pass | 3 |
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
| (a) decided, nothing built | 7 |
| (b) built, awaiting corpus proof | 24 |
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
| 1 | `b.document_class = struct('class_name', '<class>', ...)` | 63 | 49 | 14 |
| 2 | `b.document_class = classBlock('<class>', {supers})` | 15 | 15 | 0 |
| 3 | `b.document_class.class_name = '<class>';` | 4 | 4 | 0 |
| - | class name is a VARIABLE -- unresolved here | 9 | 6 | 3 |

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
count at **3**; this run measures **11**
(9 in a per-document migrator; 2 in a batch post-pass).
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
| `DID-matlab:convert/+entities/entityDoc.m:58` | `className` |
| `DID-matlab:convert/resolveLawnPlateSubjects.m:1096` | `leafClass` |
| `DID-matlab:convert/universalRenames.m:88` | `v2ClassName;` |
| `DID-matlab:migrators_j/dataset_remote.m:70` | `className` |
| `DID-matlab:migrators_j/ontology_table_row.m:248` | `leafClass` |
| `DID-matlab:migrators_j/ontology_table_row.m:779` | `className` |
| `DID-matlab:migrators_j/private/jCalculation.m:67` | `leafClass` |
| `DID-matlab:migrators_j/private/jRecordingObservation.m:209` | `e.class` |
| `DID-matlab:migrators_j/private/jStartInteraction.m:36` | `className` |

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
two committed records, not a settled fact: `V_eta_migration_targets.json`
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

| class | family | state | build evidence | minted (M+B) | field writes (M+B) | named (M+B) | comments (M+B) | survivors |
|---|---|---|---|---|---|---|---|---|
| `acquisition_epoch` | epoch | (b) | minted as a document class at 1 site(s) (1 per-document migrator) | 1 (1+0) | 1 (1+0) | - | 23 (22+1) | n/a -- not measured |
| `app` | software | (b) | 5 consuming reference(s) (2 per-document migrator, 3 batch post-pass); decided target(s) built: `software` | - | 2 (1+1) | 1 (0+1) | 174 (138+36) | n/a -- not measured |
| `binaryseries_parameters` | misc singletons | (b) | migrator `DID-matlab:migrators_j/binaryseries_parameters.m` | - | - | 1 (1+0) | 9 (9+0) | n/a -- not measured |
| `control_designation` | stimulus | (b) | minted as a document class at 1 site(s) (1 per-document migrator) | 1 (1+0) | 1 (1+0) | - | 5 (5+0) | n/a -- not measured |
| `daqmetadatareader` | daq configuration | (b) | migrator `DID-matlab:migrators_j/daqmetadatareader.m`; 3 consuming reference(s) (3 per-document migrator); decided target(s) built: `acquisition_metadata_reader` | - | - | - | 16 (16+0) | n/a -- not measured |
| `daqmetadatareader_epochdata_ingested` | daq ingested payloads | (b) | migrator `DID-matlab:migrators_j/daqmetadatareader_epochdata_ingested.m`; decided target(s) built: `acquisition_metadata_file` | - | - | - | 8 (8+0) | n/a -- not measured |
| `daqreader` | daq configuration | (b) | migrator `DID-matlab:migrators_j/daqreader.m`; 4 consuming reference(s) (4 per-document migrator); minted as a document class at 1 site(s) (1 per-document migrator); decided target(s) built: `software` | 1 (1+0) | 2 (2+0) | - | 28 (28+0) | n/a -- not measured |
| `daqreader_epochdata_ingested` | daq ingested payloads | (b) | migrator `DID-matlab:migrators_j/daqreader_epochdata_ingested.m`; 3 consuming reference(s) (3 per-document migrator); minted as a document class at 1 site(s) (1 per-document migrator); decided target(s) built: `relative_reference` | 1 (1+0) | 2 (2+0) | 2 (2+0) | 17 (16+1) | n/a -- not measured |
| `daqreader_image_epochdata_ingested` | daq ingested payloads | (b) | migrator `DID-matlab:migrators_j/daqreader_image_epochdata_ingested.m`; decided target(s) built: `image_observation`, `relative_reference`, `sampled_body` | - | - | - | 4 (4+0) | n/a -- not measured |
| `daqsystem` | daq configuration | (b) | migrator `DID-matlab:migrators_j/daqsystem.m`; 3 consuming reference(s) (3 per-document migrator); decided target(s) built: `acquisition_system` | - | - | - | 17 (17+0) | n/a -- not measured |
| `directory` | file navigation | (a) | *none* | - | - | 1 (1+0) | 23 (14+9) | n/a -- not measured |
| `ensemble` | ensemble | (b) | 1 consuming reference(s) (1 per-document migrator); decided target(s) built: `subject`, `directed_relation`, `sampled_body` | - | - | - | 18 (16+2) | n/a -- not measured |
| `epoch_bounded_reference` | time_reference | (b) | 6 consuming reference(s) (6 per-document migrator) | 1 (1+0) discounted | 1 (1+0) | 2 (2+0) | 30 (26+4) | n/a -- not measured |
| `epoch_relative_reference` | time_reference | (a) | *none* | - | - | - | 1 (1+0) | n/a -- not measured |
| `epochfiles_ingested` | epoch | (b) | migrator `DID-matlab:migrators_j/epochfiles_ingested.m` | - | - | - | 15 (10+5) | n/a -- not measured |
| `epochid` | epoch | (b) | 11 consuming reference(s) (10 per-document migrator, 1 batch post-pass) | - | 1 (1+0) | 8 (7+1) | 68 (60+8) | n/a -- not measured |
| `event_bounded_reference` | time_reference | (a) | *none* | - | - | - | - | n/a -- not measured |
| `event_relative_reference` | time_reference | (a) | *none* | - | - | - | - | n/a -- not measured |
| `filenavigator` | file navigation | (b) | migrator `DID-matlab:migrators_j/filenavigator.m`; 3 consuming reference(s) (3 per-document migrator); decided target(s) built: `epoch_file_pattern` | - | - | - | 17 (16+1) | n/a -- not measured |
| `filter` | frequency_filter | (b) | 2 consuming reference(s) (2 per-document migrator) | - | - | 2 (2+0) | 36 (32+4) | n/a -- not measured |
| `interaction_purpose` | misc singletons | (a) | *none* | - | - | - | 3 (3+0) | n/a -- not measured |
| `ngrid` | image / ngrid | (b) | 2 consuming reference(s) (2 per-document migrator) | - | 1 (1+0) | - | 25 (22+3) | n/a -- not measured |
| `projectvar` | misc singletons | (a) | *none* | - | - | - | 1 (1+0) | n/a -- not measured |
| `session_bounded_reference` | time_reference | (b) | 1 consuming reference(s) (1 batch post-pass) | 1 (1+0) discounted | 1 (1+0) | - | 10 (3+7) | n/a -- not measured |
| `session_relative_reference` | time_reference | (b) | 1 consuming reference(s) (1 batch post-pass) | 11 (9+2) discounted | 11 (9+2) | - | 27 (19+8) | n/a -- not measured |
| `stimulus_presentation` | stimulus | (b) | migrator `DID-matlab:migrators_j/stimulus_presentation.m`; 2 consuming reference(s) (2 per-document migrator) | - | - | - | 25 (23+2) | n/a -- not measured |
| `syncgraph` | sync configuration | (b) | migrator `DID-matlab:migrators_j/syncgraph.m`; 2 consuming reference(s) (2 per-document migrator); decided target(s) built: `clock_alignment_policy` | - | - | - | 29 (26+3) | n/a -- not measured |
| `syncrule` | sync configuration | (b) | migrator `DID-matlab:migrators_j/syncrule.m`; 2 consuming reference(s) (2 per-document migrator); decided target(s) built: `clock_alignment_configuration` | - | - | - | 33 (33+0) | n/a -- not measured |
| `syncrule_mapping` | sync mapping | (b) | migrator `DID-matlab:migrators_j/syncrule_mapping.m`; 2 consuming reference(s) (2 per-document migrator); minted as a document class at 1 site(s) (1 per-document migrator); decided target(s) built: `clock_alignment` | 1 (1+0) | 1 (1+0) | - | 23 (22+1) | n/a -- not measured |
| `time_reference` | time_reference | (b) | 2 consuming reference(s) (1 per-document migrator, 1 batch post-pass) | - | 17 (14+3) | 22 (18+4) | 37 (34+3) | n/a -- not measured |
| `utc_reference` | time_reference | (a) | *none* | - | - | - | 1 (0+1) | n/a -- not measured |

#### (a) decided, nothing built -- 7

- `directory` (file navigation) -- NAMED as a string value at 1 site(s), per-document migrator: `DID-matlab:migrators_j/private/jSorterOutput.m:134 (named)`; mentioned in 14 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/epochfiles_ingested.m:48 (comment_mention)`, `DID-matlab:migrators_j/filenavigator.m:11 (comment_mention)`, `DID-matlab:migrators_j/kiasort_clusters.m:9 (comment_mention)`, `DID-matlab:migrators_j/kilosort_clusters.m:10 (comment_mention)`, `DID-matlab:migrators_j/private/jSorterOutput.m:114 (comment_mention)`, `DID-matlab:migrators_j/private/jSorterOutput.m:13 (comment_mention)` ...; mentioned in 9 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/+readers/Contents.m:15 (comment_mention)`, `DID-matlab:convert/+readers/dumbJsonV1.m:4 (comment_mention)`, `DID-matlab:convert/+readers/dumbJsonV1.m:95 (comment_mention)`, `DID-matlab:convert/+readers/dumbJsonV1.m:96 (comment_mention)`, `DID-matlab:convert/Contents.m:12 (comment_mention)`, `DID-matlab:convert/epochMint.m:51 (comment_mention)` ...
- `epoch_relative_reference` (time_reference) -- mentioned in 1 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/stimulus_response_scalar.m:184 (comment_mention)`
- `event_bounded_reference` (time_reference) -- no evidence found
- `event_relative_reference` (time_reference) -- no evidence found
- `interaction_purpose` (misc singletons) -- mentioned in 3 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/openminds_stimulus.m:49 (comment_mention)`, `DID-matlab:migrators_j/openminds_stimulus.m:50 (comment_mention)`, `DID-matlab:migrators_j/openminds_stimulus.m:70 (comment_mention)`
- `projectvar` (misc singletons) -- mentioned in 1 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:340 (comment_mention)`
- `utc_reference` (time_reference) -- mentioned in 1 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/resolveSessionAnchors.m:43 (comment_mention)`

#### (b) built, awaiting corpus proof -- 24

- `acquisition_epoch` (epoch) -- MINTED as a document class at 1 site(s), per-document migrator: `DID-matlab:migrators_j/element_epoch.m:99 (emitted_class)`; a block of this name is WRITTEN at 1 site(s), per-document migrator: `DID-matlab:migrators_j/element_epoch.m:101 (field_write)`; mentioned in 22 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/element_epoch.m:10 (comment_mention)`, `DID-matlab:migrators_j/element_epoch.m:12 (comment_mention)`, `DID-matlab:migrators_j/element_epoch.m:2 (comment_mention)`, `DID-matlab:migrators_j/element_epoch.m:33 (comment_mention)`, `DID-matlab:migrators_j/element_epoch.m:54 (comment_mention)`, `DID-matlab:migrators_j/element_epoch.m:69 (comment_mention)` ...; mentioned in 1 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/resolveValidIntervals.m:547 (comment_mention)`
- `app` (software) -- consumed at 2 site(s), per-document migrator: `DID-matlab:migrators_j/private/jSoftwareFromApp.m:91 (guard)`, `DID-matlab:migrators_j/private/jSoftwareFromApp.m:92 (field_read)`; consumed at 3 site(s), batch post-pass: `DID-matlab:convert/resolveValidIntervals.m:483 (guard)`, `DID-matlab:convert/universalRenames.m:122 (guard)`, `DID-matlab:convert/universalRenames.m:123 (field_read)`; a block of this name is WRITTEN at 1 site(s), per-document migrator: `DID-matlab:migrators_j/private/jMethodParameters.m:107 (field_write)`; a block of this name is WRITTEN at 1 site(s), batch post-pass: `DID-matlab:convert/universalRenames.m:124 (field_write)`; NAMED as a string value at 1 site(s), batch post-pass: `DID-matlab:convert/resolveValidIntervals.m:925 (named)`; mentioned in 138 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:113 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:129 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:355 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:356 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:412 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:417 (comment_mention)` ...; mentioned in 36 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/calcCommon.m:25 (comment_mention)`, `DID-matlab:convert/calcCommon.m:28 (comment_mention)`, `DID-matlab:convert/resolveOpenmindsCitations.m:860 (comment_mention)`, `DID-matlab:convert/resolveValidIntervals.m:128 (comment_mention)`, `DID-matlab:convert/resolveValidIntervals.m:217 (comment_mention)`, `DID-matlab:convert/resolveValidIntervals.m:264 (comment_mention)` ...; target(s) BUILT: `software`
- `binaryseries_parameters` (misc singletons) -- migrator `DID-matlab:migrators_j/binaryseries_parameters.m`; NAMED as a string value at 1 site(s), per-document migrator: `DID-matlab:migrators_j/binaryseries_parameters.m:119 (named)`; mentioned in 9 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/+super/image_stack_parameters.m:94 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:288 (comment_mention)`, `DID-matlab:migrators_j/binaryseries_parameters.m:16 (comment_mention)`, `DID-matlab:migrators_j/binaryseries_parameters.m:2 (comment_mention)`, `DID-matlab:migrators_j/binaryseries_parameters.m:36 (comment_mention)`, `DID-matlab:migrators_j/binaryseries_parameters.m:79 (comment_mention)` ...
- `control_designation` (stimulus) -- MINTED as a document class at 1 site(s), per-document migrator: `DID-matlab:migrators_j/control_stimulus_ids.m:111 (emitted_class)`; a block of this name is WRITTEN at 1 site(s), per-document migrator: `DID-matlab:migrators_j/control_stimulus_ids.m:133 (field_write)`; mentioned in 5 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/control_stimulus_ids.m:3 (comment_mention)`, `DID-matlab:migrators_j/control_stimulus_ids.m:53 (comment_mention)`, `DID-matlab:migrators_j/control_stimulus_ids.m:60 (comment_mention)`, `DID-matlab:migrators_j/control_stimulus_ids.m:72 (comment_mention)`, `DID-matlab:migrators_j/control_stimulus_ids.m:79 (comment_mention)`
- `daqmetadatareader` (daq configuration) -- migrator `DID-matlab:migrators_j/daqmetadatareader.m`; consumed at 3 site(s), per-document migrator: `DID-matlab:migrators_j/daqmetadatareader.m:100 (guard)`, `DID-matlab:migrators_j/daqmetadatareader.m:101 (field_read)`, `DID-matlab:migrators_j/daqmetadatareader.m:102 (field_read)`; mentioned in 16 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:171 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader.m:13 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader.m:2 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader.m:26 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader.m:29 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader.m:39 (comment_mention)` ...; target(s) BUILT: `acquisition_metadata_reader`
- `daqmetadatareader_epochdata_ingested` (daq ingested payloads) -- migrator `DID-matlab:migrators_j/daqmetadatareader_epochdata_ingested.m`; mentioned in 8 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/daqmetadatareader.m:20 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader.m:70 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader.m:77 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader_epochdata_ingested.m:21 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader_epochdata_ingested.m:25 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader_epochdata_ingested.m:30 (comment_mention)` ...; target(s) BUILT: `acquisition_metadata_file`
- `daqreader` (daq configuration) -- migrator `DID-matlab:migrators_j/daqreader.m`; consumed at 4 site(s), per-document migrator: `DID-matlab:migrators_j/daqreader.m:100 (guard)`, `DID-matlab:migrators_j/daqreader.m:101 (field_read)`, `DID-matlab:migrators_j/daqreader.m:102 (field_read)`, `DID-matlab:migrators_j/daqreader_ndr.m:21 (guard)`; MINTED as a document class at 1 site(s), per-document migrator: `DID-matlab:migrators_j/daqreader_ndr.m:14 (emitted_class)`; a block of this name is WRITTEN at 2 site(s), per-document migrator: `DID-matlab:migrators_j/daqreader_ndr.m:22 (field_write)`, `DID-matlab:migrators_j/daqreader_ndr.m:25 (field_write)`; mentioned in 28 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:160 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:208 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader_epochdata_ingested.m:65 (comment_mention)`, `DID-matlab:migrators_j/daqreader.m:12 (comment_mention)`, `DID-matlab:migrators_j/daqreader.m:2 (comment_mention)`, `DID-matlab:migrators_j/daqreader.m:20 (comment_mention)` ...; target(s) BUILT: `software`
- `daqreader_epochdata_ingested` (daq ingested payloads) -- migrator `DID-matlab:migrators_j/daqreader_epochdata_ingested.m`; consumed at 3 site(s), per-document migrator: `DID-matlab:migrators_j/daqreader_mfdaq_epochdata_ingested.m:40 (guard)`, `DID-matlab:migrators_j/daqreader_mfdaq_epochdata_ingested.m:41 (field_read)`, `DID-matlab:migrators_j/daqreader_mfdaq_epochdata_ingested.m:66 (field_read)`; MINTED as a document class at 1 site(s), per-document migrator: `DID-matlab:migrators_j/daqreader_mfdaq_epochdata_ingested.m:36 (emitted_class)`; a block of this name is WRITTEN at 2 site(s), per-document migrator: `DID-matlab:migrators_j/daqreader_mfdaq_epochdata_ingested.m:42 (field_write)`, `DID-matlab:migrators_j/daqreader_mfdaq_epochdata_ingested.m:48 (field_write)`; NAMED as a string value at 2 site(s), per-document migrator: `DID-matlab:migrators_j/daqreader_epochdata_ingested.m:84 (named)`, `DID-matlab:migrators_j/daqreader_image_epochdata_ingested.m:91 (named)`; mentioned in 16 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/daqreader.m:54 (comment_mention)`, `DID-matlab:migrators_j/daqreader_image_epochdata_ingested.m:20 (comment_mention)`, `DID-matlab:migrators_j/daqreader_image_epochdata_ingested.m:21 (comment_mention)`, `DID-matlab:migrators_j/daqreader_image_epochdata_ingested.m:30 (comment_mention)`, `DID-matlab:migrators_j/daqreader_image_epochdata_ingested.m:89 (comment_mention)`, `DID-matlab:migrators_j/daqreader_image_epochdata_ingested.m:9 (comment_mention)` ...; mentioned in 1 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/epochMint.m:513 (comment_mention)`; target(s) BUILT: `relative_reference`
- `daqreader_image_epochdata_ingested` (daq ingested payloads) -- migrator `DID-matlab:migrators_j/daqreader_image_epochdata_ingested.m`; mentioned in 4 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/daqreader.m:55 (comment_mention)`, `DID-matlab:migrators_j/daqreader_image_epochdata_ingested.m:25 (comment_mention)`, `DID-matlab:migrators_j/daqreader_image_epochdata_ingested.m:43 (comment_mention)`, `DID-matlab:migrators_j/private/jEpochDocId.m:23 (comment_mention)`; target(s) BUILT: `image_observation`, `relative_reference`, `sampled_body`
- `daqsystem` (daq configuration) -- migrator `DID-matlab:migrators_j/daqsystem.m`; consumed at 3 site(s), per-document migrator: `DID-matlab:migrators_j/daqsystem.m:144 (guard)`, `DID-matlab:migrators_j/daqsystem.m:145 (field_read)`, `DID-matlab:migrators_j/daqsystem.m:146 (field_read)`; mentioned in 17 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:145 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:162 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:183 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader.m:68 (comment_mention)`, `DID-matlab:migrators_j/daqreader.m:13 (comment_mention)`, `DID-matlab:migrators_j/daqreader.m:53 (comment_mention)` ...; target(s) BUILT: `acquisition_system`
- `ensemble` (ensemble) -- consumed at 1 site(s), per-document migrator: `NDI-matlab:ndi_second_pass/ensembleMembership.m:227 (guard)`; mentioned in 16 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/element.m:112 (comment_mention)`, `DID-matlab:migrators_j/element_epoch.m:58 (comment_mention)`, `DID-matlab:migrators_j/element_epoch.m:60 (comment_mention)`, `DID-matlab:migrators_j/element_epoch.m:61 (comment_mention)`, `DID-matlab:migrators_j/private/jAcquisitionChannels.m:57 (comment_mention)`, `DID-matlab:migrators_j/stimulus_presentation.m:13 (comment_mention)` ...; mentioned in 2 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/resolveLawnPlateSubjects.m:1121 (comment_mention)`, `DID-matlab:convert/resolveResponseParameters.m:42 (comment_mention)`; target(s) BUILT: `subject`, `directed_relation`, `sampled_body`
- `epoch_bounded_reference` (time_reference) -- consumed at 6 site(s), per-document migrator: `NDI-matlab:ndi_second_pass/epochAnchorFold.m:322 (guard)`, `NDI-matlab:ndi_second_pass/epochAnchorFold.m:424 (guard)`, `NDI-matlab:ndi_second_pass/epochAnchorFold.m:535 (guard)`, `NDI-matlab:ndi_second_pass/epochAnchorFold.m:536 (field_read)`, `NDI-matlab:ndi_second_pass/epochAnchorFold.m:537 (field_read)`, `NDI-matlab:ndi_second_pass/epochAnchorFold.m:538 (field_read)`; MINTED as a document class at 1 site(s), per-document migrator: `NDI-matlab:ndi_second_pass/stimulusBathToBath.m:166 (emitted_class)`; minted at 1 site(s) (1 per-document migrator), NOT counted as build progress: the signed decision retires this class in favour of `relative_reference`, so an emission is work still to undo; a block of this name is WRITTEN at 1 site(s), per-document migrator: `NDI-matlab:ndi_second_pass/stimulusBathToBath.m:176 (field_write)`; NAMED as a string value at 2 site(s), per-document migrator: `DID-matlab:migrators_j/syncrule_mapping.m:182 (named)`, `NDI-matlab:ndi_second_pass/epochAnchorFold.m:425 (named)`; mentioned in 26 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/stimulus_bath.m:23 (comment_mention)`, `DID-matlab:migrators_j/syncrule_mapping.m:176 (comment_mention)`, `DID-matlab:migrators_j/syncrule_mapping.m:71 (comment_mention)`, `NDI-matlab:ndi_second_pass/bodyResolver.m:17 (comment_mention)`, `NDI-matlab:ndi_second_pass/epochAnchorFold.m:114 (comment_mention)`, `NDI-matlab:ndi_second_pass/epochAnchorFold.m:141 (comment_mention)` ...; mentioned in 4 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/resolveDeferredBaths.m:15 (comment_mention)`, `DID-matlab:convert/resolveDeferredBaths.m:24 (comment_mention)`, `DID-matlab:convert/resolveSessionAnchors.m:45 (comment_mention)`, `DID-matlab:convert/resolveSessionAnchors.m:81 (comment_mention)`
- `epochfiles_ingested` (epoch) -- migrator `DID-matlab:migrators_j/epochfiles_ingested.m`; mentioned in 10 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:146 (comment_mention)`, `DID-matlab:migrators_j/epochfiles_ingested.m:121 (comment_mention)`, `DID-matlab:migrators_j/epochfiles_ingested.m:39 (comment_mention)`, `DID-matlab:migrators_j/epochfiles_ingested.m:60 (comment_mention)`, `DID-matlab:migrators_j/epochfiles_ingested.m:94 (comment_mention)`, `DID-matlab:migrators_j/filenavigator.m:52 (comment_mention)` ...; mentioned in 5 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/epochMint.m:106 (comment_mention)`, `DID-matlab:convert/epochMint.m:113 (comment_mention)`, `DID-matlab:convert/epochMint.m:126 (comment_mention)`, `DID-matlab:convert/resolveSessionAnchors.m:188 (comment_mention)`, `DID-matlab:convert/resolveValidIntervals.m:45 (comment_mention)`
- `epochid` (epoch) -- consumed at 10 site(s), per-document migrator: `DID-matlab:migrators_j/private/jMethodParameters.m:122 (guard)`, `NDI-matlab:ndi_second_pass/bodyResolver.m:216 (guard)`, `NDI-matlab:ndi_second_pass/bodyResolver.m:217 (guard)`, `NDI-matlab:ndi_second_pass/bodyResolver.m:218 (field_read)`, `NDI-matlab:ndi_second_pass/ensembleMembership.m:361 (guard)`, `NDI-matlab:ndi_second_pass/ensembleMembership.m:362 (field_read)` ...; consumed at 1 site(s), batch post-pass: `DID-matlab:convert/epochMint.m:416 (guard)`; a block of this name is WRITTEN at 1 site(s), per-document migrator: `DID-matlab:migrators_j/private/jMethodParameters.m:126 (field_write)`; NAMED as a string value at 7 site(s), per-document migrator: `DID-matlab:migrators_j/epochfiles_ingested.m:135 (named)`, `DID-matlab:migrators_j/private/jMethodParameters.m:123 (named)`, `NDI-matlab:ndi_second_pass/epochAnchorFold.m:428 (named)`, `NDI-matlab:ndi_second_pass/epochAnchorFold.m:517 (named)`, `NDI-matlab:ndi_second_pass/epochAnchorFold.m:521 (named)`, `NDI-matlab:ndi_second_pass/stimulusBathToBath.m:169 (named)` ...; NAMED as a string value at 1 site(s), batch post-pass: `DID-matlab:convert/epochMint.m:417 (named)`; mentioned in 60 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:128 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:130 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader_epochdata_ingested.m:22 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader_epochdata_ingested.m:29 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader_epochdata_ingested.m:31 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader_epochdata_ingested.m:35 (comment_mention)` ...; mentioned in 8 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/epochMint.m:102 (comment_mention)`, `DID-matlab:convert/epochMint.m:123 (comment_mention)`, `DID-matlab:convert/epochMint.m:137 (comment_mention)`, `DID-matlab:convert/epochMint.m:300 (comment_mention)`, `DID-matlab:convert/epochMint.m:397 (comment_mention)`, `DID-matlab:convert/epochMint.m:50 (comment_mention)` ...
- `filenavigator` (file navigation) -- migrator `DID-matlab:migrators_j/filenavigator.m`; consumed at 3 site(s), per-document migrator: `DID-matlab:migrators_j/filenavigator.m:121 (guard)`, `DID-matlab:migrators_j/filenavigator.m:122 (field_read)`, `DID-matlab:migrators_j/filenavigator.m:123 (field_read)`; mentioned in 16 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:144 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:416 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:455 (comment_mention)`, `DID-matlab:migrators_j/daqsystem.m:59 (comment_mention)`, `DID-matlab:migrators_j/epochfiles_ingested.m:10 (comment_mention)`, `DID-matlab:migrators_j/filenavigator.m:17 (comment_mention)` ...; mentioned in 1 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/v1_to_v2.m:559 (comment_mention)`; target(s) BUILT: `epoch_file_pattern`
- `filter` (frequency_filter) -- consumed at 2 site(s), per-document migrator: `DID-matlab:migrators_j/private/jFrequencyFilter.m:112 (guard)`, `DID-matlab:migrators_j/private/jFrequencyFilter.m:113 (field_read)`; NAMED as a string value at 2 site(s), per-document migrator: `DID-matlab:migrators_j/private/jSpikeExtractionSettings.m:159 (named)`, `DID-matlab:migrators_j/vmspikefilteringparameters.m:144 (named)`; mentioned in 32 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:277 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:286 (comment_mention)`, `DID-matlab:migrators_j/ontology_image.m:12 (comment_mention)`, `DID-matlab:migrators_j/private/jFrequencyFilter.m:105 (comment_mention)`, `DID-matlab:migrators_j/private/jFrequencyFilter.m:123 (comment_mention)`, `DID-matlab:migrators_j/private/jFrequencyFilter.m:126 (comment_mention)` ...; mentioned in 4 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/resolveSessionAnchors.m:57 (comment_mention)`, `DID-matlab:convert/universalRenames.m:244 (comment_mention)`, `DID-matlab:convert/universalRenames.m:245 (comment_mention)`, `DID-matlab:convert/universalRenames.m:35 (comment_mention)`
- `ngrid` (image / ngrid) -- consumed at 2 site(s), per-document migrator: `DID-matlab:migrators_j/+super/ngrid.m:100 (field_read)`, `DID-matlab:migrators_j/+super/ngrid.m:96 (guard)`; a block of this name is WRITTEN at 1 site(s), per-document migrator: `DID-matlab:migrators_j/+super/ngrid.m:115 (field_write)`; mentioned in 22 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/+super/ngrid.m:15 (comment_mention)`, `DID-matlab:migrators_j/+super/ngrid.m:2 (comment_mention)`, `DID-matlab:migrators_j/+super/ngrid.m:23 (comment_mention)`, `DID-matlab:migrators_j/+super/ngrid.m:30 (comment_mention)`, `DID-matlab:migrators_j/+super/ngrid.m:36 (comment_mention)`, `DID-matlab:migrators_j/+super/ngrid.m:37 (comment_mention)` ...; mentioned in 3 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/v1_to_v2.m:540 (comment_mention)`, `DID-matlab:convert/v1_to_v2.m:546 (comment_mention)`, `DID-matlab:convert/v1_to_v2.m:551 (comment_mention)`
- `session_bounded_reference` (time_reference) -- consumed at 1 site(s), batch post-pass: `DID-matlab:convert/resolveSessionAnchors.m:297 (guard)`; MINTED as a document class at 1 site(s), per-document migrator: `DID-matlab:migrators_j/ontology_table_row.m:275 (emitted_class)`; minted at 1 site(s) (1 per-document migrator), NOT counted as build progress: the signed decision retires this class in favour of `relative_reference`, so an emission is work still to undo; a block of this name is WRITTEN at 1 site(s), per-document migrator: `DID-matlab:migrators_j/ontology_table_row.m:281 (field_write)`; mentioned in 3 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/ontology_table_row.m:271 (comment_mention)`, `DID-matlab:migrators_j/ontology_table_row.m:35 (comment_mention)`, `NDI-matlab:ndi_second_pass/epochAnchorFold.m:87 (comment_mention)`; mentioned in 7 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/resolveSessionAnchors.m:196 (comment_mention)`, `DID-matlab:convert/resolveSessionAnchors.m:20 (comment_mention)`, `DID-matlab:convert/resolveSessionAnchors.m:32 (comment_mention)`, `DID-matlab:convert/resolveSessionAnchors.m:323 (comment_mention)`, `DID-matlab:convert/resolveSessionAnchors.m:524 (comment_mention)`, `DID-matlab:convert/resolveSessionAnchors.m:540 (comment_mention)` ...
- `session_relative_reference` (time_reference) -- consumed at 1 site(s), batch post-pass: `DID-matlab:convert/resolveSessionAnchors.m:296 (guard)`; MINTED as a document class at 9 site(s), per-document migrator: `DID-matlab:migrators_j/fitcurve.m:147 (emitted_class)`, `DID-matlab:migrators_j/image_stack.m:279 (emitted_class)`, `DID-matlab:migrators_j/jrclust_clusters.m:88 (emitted_class)`, `DID-matlab:migrators_j/neuron_extracellular.m:118 (emitted_class)`, `DID-matlab:migrators_j/ontology_table_row.m:867 (emitted_class)`, `DID-matlab:migrators_j/private/jSessionAnchor.m:60 (emitted_class)` ...; MINTED as a document class at 2 site(s), batch post-pass: `DID-matlab:convert/resolveDeferredBaths.m:177 (emitted_class)`, `DID-matlab:convert/resolveDeferredBaths.m:229 (emitted_class)`; minted at 11 site(s) (9 per-document migrator, 2 batch post-pass), NOT counted as build progress: the signed decision retires this class in favour of `relative_reference`, so an emission is work still to undo; a block of this name is WRITTEN at 9 site(s), per-document migrator: `DID-matlab:migrators_j/fitcurve.m:154 (field_write)`, `DID-matlab:migrators_j/image_stack.m:284 (field_write)`, `DID-matlab:migrators_j/jrclust_clusters.m:93 (field_write)`, `DID-matlab:migrators_j/neuron_extracellular.m:123 (field_write)`, `DID-matlab:migrators_j/ontology_table_row.m:875 (field_write)`, `DID-matlab:migrators_j/private/jSessionAnchor.m:68 (field_write)` ...; a block of this name is WRITTEN at 2 site(s), batch post-pass: `DID-matlab:convert/resolveDeferredBaths.m:188 (field_write)`, `DID-matlab:convert/resolveDeferredBaths.m:237 (field_write)`; mentioned in 19 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/fitcurve.m:13 (comment_mention)`, `DID-matlab:migrators_j/image_stack.m:25 (comment_mention)`, `DID-matlab:migrators_j/jrclust_clusters.m:20 (comment_mention)`, `DID-matlab:migrators_j/jrclust_clusters.m:40 (comment_mention)`, `DID-matlab:migrators_j/neuron_extracellular.m:132 (comment_mention)`, `DID-matlab:migrators_j/neuron_extracellular.m:19 (comment_mention)` ...; mentioned in 8 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/resolveDeferredBaths.m:13 (comment_mention)`, `DID-matlab:convert/resolveDeferredBaths.m:174 (comment_mention)`, `DID-matlab:convert/resolveDeferredBaths.m:183 (comment_mention)`, `DID-matlab:convert/resolveLawnPlateSubjects.m:289 (comment_mention)`, `DID-matlab:convert/resolveSessionAnchors.m:19 (comment_mention)`, `DID-matlab:convert/resolveSessionAnchors.m:194 (comment_mention)` ...
- `stimulus_presentation` (stimulus) -- migrator `DID-matlab:migrators_j/stimulus_presentation.m`; consumed at 2 site(s), per-document migrator: `NDI-matlab:ndi_second_pass/stimulusPresentationToManipulation.m:47 (guard)`, `NDI-matlab:ndi_second_pass/stimulusPresentationToManipulation.m:48 (field_read)`; mentioned in 23 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/control_stimulus_ids.m:116 (comment_mention)`, `DID-matlab:migrators_j/control_stimulus_ids.m:32 (comment_mention)`, `DID-matlab:migrators_j/control_stimulus_ids.m:46 (comment_mention)`, `DID-matlab:migrators_j/control_stimulus_ids.m:74 (comment_mention)`, `DID-matlab:migrators_j/control_stimulus_ids.m:89 (comment_mention)`, `DID-matlab:migrators_j/ontology_image.m:89 (comment_mention)` ...; mentioned in 2 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/universalRenames.m:151 (comment_mention)`, `DID-matlab:convert/v1_to_v2.m:672 (comment_mention)`
- `syncgraph` (sync configuration) -- migrator `DID-matlab:migrators_j/syncgraph.m`; consumed at 2 site(s), per-document migrator: `DID-matlab:migrators_j/syncgraph.m:128 (guard)`, `DID-matlab:migrators_j/syncgraph.m:129 (field_read)`; mentioned in 26 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:421 (comment_mention)`, `DID-matlab:migrators_j/private/jClockAlignmentBodies.m:62 (comment_mention)`, `DID-matlab:migrators_j/private/jClockAlignmentBodies.m:66 (comment_mention)`, `DID-matlab:migrators_j/private/jClockAlignmentBodies.m:71 (comment_mention)`, `DID-matlab:migrators_j/private/jSessionDocId.m:33 (comment_mention)`, `DID-matlab:migrators_j/private/jSoftware.m:34 (comment_mention)` ...; mentioned in 3 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/epochMint.m:151 (comment_mention)`, `DID-matlab:convert/epochMint.m:324 (comment_mention)`, `DID-matlab:convert/resolveValidIntervals.m:141 (comment_mention)`; target(s) BUILT: `clock_alignment_policy`
- `syncrule` (sync configuration) -- migrator `DID-matlab:migrators_j/syncrule.m`; consumed at 2 site(s), per-document migrator: `DID-matlab:migrators_j/syncrule.m:95 (guard)`, `DID-matlab:migrators_j/syncrule.m:96 (field_read)`; mentioned in 33 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:421 (comment_mention)`, `DID-matlab:migrators_j/daqsystem.m:83 (comment_mention)`, `DID-matlab:migrators_j/private/jAcquisitionChannels.m:15 (comment_mention)`, `DID-matlab:migrators_j/private/jAcquisitionChannels.m:18 (comment_mention)`, `DID-matlab:migrators_j/private/jAcquisitionChannels.m:2 (comment_mention)`, `DID-matlab:migrators_j/private/jAcquisitionChannels.m:30 (comment_mention)` ...; target(s) BUILT: `clock_alignment_configuration`
- `syncrule_mapping` (sync mapping) -- migrator `DID-matlab:migrators_j/syncrule_mapping.m`; consumed at 2 site(s), per-document migrator: `DID-matlab:migrators_j/syncrule_mapping.m:106 (guard)`, `DID-matlab:migrators_j/syncrule_mapping.m:107 (field_read)`; MINTED as a document class at 1 site(s), per-document migrator: `DID-matlab:migrators_j/syncrule_mapping.m:131 (emitted_class)`; a block of this name is WRITTEN at 1 site(s), per-document migrator: `DID-matlab:migrators_j/syncrule_mapping.m:149 (field_write)`; mentioned in 22 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/private/jClockAlignmentBodies.m:10 (comment_mention)`, `DID-matlab:migrators_j/private/jClockAlignmentBodies.m:170 (comment_mention)`, `DID-matlab:migrators_j/private/jClockAlignmentBodies.m:2 (comment_mention)`, `DID-matlab:migrators_j/private/jClockAlignmentBodies.m:7 (comment_mention)`, `DID-matlab:migrators_j/private/jClockAlignmentBodies.m:74 (comment_mention)`, `DID-matlab:migrators_j/stimulus_response_scalar.m:154 (comment_mention)` ...; mentioned in 1 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/resolveResponseParameters.m:457 (comment_mention)`; target(s) BUILT: `clock_alignment`
- `time_reference` (time_reference) -- consumed at 1 site(s), per-document migrator: `NDI-matlab:ndi_second_pass/epochAnchorFold.m:432 (guard)`; consumed at 1 site(s), batch post-pass: `DID-matlab:convert/resolveSessionAnchors.m:376 (guard)`; a block of this name is WRITTEN at 14 site(s), per-document migrator: `DID-matlab:migrators_j/fitcurve.m:153 (field_write)`, `DID-matlab:migrators_j/image_stack.m:283 (field_write)`, `DID-matlab:migrators_j/jrclust_clusters.m:92 (field_write)`, `DID-matlab:migrators_j/neuron_extracellular.m:122 (field_write)`, `DID-matlab:migrators_j/ontology_table_row.m:280 (field_write)`, `DID-matlab:migrators_j/ontology_table_row.m:874 (field_write)` ...; a block of this name is WRITTEN at 3 site(s), batch post-pass: `DID-matlab:convert/resolveDeferredBaths.m:187 (field_write)`, `DID-matlab:convert/resolveDeferredBaths.m:236 (field_write)`, `DID-matlab:convert/resolveValidIntervals.m:807 (field_write)`; NAMED as a string value at 18 site(s), per-document migrator: `DID-matlab:migrators_j/fitcurve.m:147 (named)`, `DID-matlab:migrators_j/image_stack.m:279 (named)`, `DID-matlab:migrators_j/jrclust_clusters.m:88 (named)`, `DID-matlab:migrators_j/neuron_extracellular.m:118 (named)`, `DID-matlab:migrators_j/ontology_table_row.m:276 (named)`, `DID-matlab:migrators_j/ontology_table_row.m:869 (named)` ...; NAMED as a string value at 4 site(s), batch post-pass: `DID-matlab:convert/resolveDeferredBaths.m:179 (named)`, `DID-matlab:convert/resolveDeferredBaths.m:231 (named)`, `DID-matlab:convert/resolveSessionAnchors.m:366 (named)`, `DID-matlab:convert/resolveValidIntervals.m:797 (named)`; mentioned in 34 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/neuron_extracellular.m:48 (comment_mention)`, `DID-matlab:migrators_j/ontology_table_row.m:172 (comment_mention)`, `DID-matlab:migrators_j/ontology_table_row.m:196 (comment_mention)`, `DID-matlab:migrators_j/ontology_table_row.m:199 (comment_mention)`, `DID-matlab:migrators_j/ontology_table_row.m:214 (comment_mention)`, `DID-matlab:migrators_j/ontology_table_row.m:31 (comment_mention)` ...; mentioned in 3 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/resolveSessionAnchors.m:185 (comment_mention)`, `DID-matlab:convert/resolveSessionAnchors.m:200 (comment_mention)`, `DID-matlab:convert/resolveSessionAnchors.m:202 (comment_mention)`

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
| **stranded sources** | 2 | tombstoned so they stop stranding; tier and fold UNDECIDED |

- **stranded sources**: `generic_file`, `valid_interval`

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
| retire | 47 |
| consumed by migrator (no tombstone) | 27 |
| in_progress | 19 |
| persist | 4 |
| test/demo fixture (non-production) | 3 |
| dissolved → subject | 1 |
| no V_eta home, no migrator -- UNVERIFIED | 1 |

### `retire`, but NO MIGRATOR YET -- 1 rows

Marked `retire` in the ledger with **no migrator and no `how` note**, so the
documents pass through untouched today. `retire` reads as settled, so these
do not appear in the family counts above -- but they are open work. Several
hold real data (e.g. `spike_extraction_parameters` carries filter_type /
filter_low / filter_high / filter_order / filter_ripple).

**This heading used to say "nothing decided" / "no recorded plan", and that
was WRONG** -- it is computed from the LEDGER (disposition + migrator + `how`),
not from whether a decision exists. Checked 2026-08-08: **every one of these
rows is covered by a plan document**, and most are signed. The list means
"no migrator has been written yet", not "nobody has decided". A board that
reports settled work as undecided is the mirror of the failure this board
exists to prevent, and it cost a review pass to notice.

- `generic_file`

**UNVERIFIED** -- no V_eta home, no migrator, fate never established. These strand today:

- `imageCollection`

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
- `valid_interval`
- `vmspikefilteringparameters`

