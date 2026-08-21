# V_eta status board (GENERATED -- do not hand-edit)

Regenerate with `python3 tools/status_board.py`. CI runs `--check`.

State lives here. The plan documents under `schemas/` keep the RATIONALE
for each model; this board owns *how much is left and what exactly*.

## Where V_eta stands

| | count |
|---|---|
| target classes | 245 |
| settled (persist) | 167 |
| settled (retire) | 52 |
| **still open (`in_progress`)** | **26** |
| **`retire` with no migrator YET** | **2** |
| open **decision families** | **26** |
| &nbsp;&nbsp;DECIDED and signed off, awaiting build | 26 |
| &nbsp;&nbsp;decided in a walkthrough, **awaiting a signature** | 0 |
| &nbsp;&nbsp;**written up by Claude alone, unreviewed** | **0** |
| &nbsp;&nbsp;nobody has proposed anything yet | 0 |

| open-class BUILD/PROOF state (derived, see below) | count |
|---|---|
| (a) decided, nothing built | 2 |
| (b) built, awaiting corpus proof | 24 |
| (c) corpus: 0 survivors in the corpora read | 0 |
| (?) UNMEASURED -- no build evidence was ever taken | 0 |

The class count is not the work count. 26 open classes are 26 decisions, because most open classes move as a family.

**0 of those 26 are not settled**: 0 awaiting a signature on a decision already taken, 0 written up by Claude alone and unreviewed, 0 with nothing proposed. Only 26 are signed off.

## What is actually left on the 26 open classes

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
| build: migrator files inspected | 182 |
| build: &nbsp;&nbsp;-- of those, per-document migrator | 154 |
| build: &nbsp;&nbsp;-- of those, batch post-pass | 28 |
| build: V_zeta files DELIBERATELY EXCLUDED (`+migrators`, `+migrators_i`, `+migrators_e`) | 38 |
| build: migrator lines inspected | 45615 |
| build: &nbsp;&nbsp;-- of those, per-document migrator | 30667 |
| build: &nbsp;&nbsp;-- of those, batch post-pass | 14948 |
| build: classes queried | 26 |
| build: open classes MINTED as a document class | 8 |
| build: &nbsp;&nbsp;-- open classes minted in a per-document migrator (rows overlap) | 8 |
| build: &nbsp;&nbsp;-- open classes minted in a batch post-pass (rows overlap) | 1 |
| build: of those, discounted (decision retires the class) | 3 |
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

### Where the 26 open classes sit

| state | classes |
|---|---|
| (a) decided, nothing built | 2 |
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
| 1 | `b.document_class = struct('class_name', '<class>', ...)` | 73 | 56 | 17 |
| 2 | `b.document_class = classBlock('<class>', {supers})` | 19 | 19 | 0 |
| 3 | `b.document_class.class_name = '<class>';` | 5 | 5 | 0 |
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
| `DID-matlab:convert/resolveEpochProbemap.m:605` | `entry.class` |
| `DID-matlab:convert/resolveLawnPlateSubjects.m:1333` | `leafClass` |
| `DID-matlab:convert/universalRenames.m:240` | `v2ClassName;` |
| `DID-matlab:migrators_j/dataset_remote.m:70` | `className` |
| `DID-matlab:migrators_j/ontology_table_row.m:248` | `leafClass` |
| `DID-matlab:migrators_j/ontology_table_row.m:783` | `className` |
| `DID-matlab:migrators_j/private/jCalculation.m:84` | `leafClass` |
| `DID-matlab:migrators_j/private/jRecordingObservation.m:275` | `e.class` |
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
| `acquisition_epoch` | epoch | (b) | 6 consuming reference(s) (1 per-document migrator, 5 batch post-pass); minted as a document class at 1 site(s) (1 per-document migrator) | 1 (1+0) | 1 (1+0) | - | 46 (29+17) | n/a -- not measured |
| `app` | software | (b) | 5 consuming reference(s) (2 per-document migrator, 3 batch post-pass); decided target(s) built: `software` | - | 2 (1+1) | 1 (0+1) | 199 (163+36) | n/a -- not measured |
| `binaryseries_parameters` | misc singletons | (b) | migrator `DID-matlab:migrators_j/binaryseries_parameters.m`; decided target(s) built: `subject_statement`, `sampled_body` | - | - | 1 (1+0) | 15 (15+0) | n/a -- not measured |
| `control_designation` | stimulus | (b) | minted as a document class at 1 site(s) (1 per-document migrator) | 1 (1+0) | 1 (1+0) | - | 8 (8+0) | n/a -- not measured |
| `daqmetadatareader` | daq configuration | (b) | migrator `DID-matlab:migrators_j/daqmetadatareader.m`; 3 consuming reference(s) (3 per-document migrator); decided target(s) built: `acquisition_metadata_reader` | - | - | - | 24 (24+0) | n/a -- not measured |
| `daqmetadatareader_epochdata_ingested` | daq ingested payloads | (b) | migrator `DID-matlab:migrators_j/daqmetadatareader_epochdata_ingested.m`; 2 consuming reference(s) (2 batch post-pass); decided target(s) built: `acquisition_metadata_file` | - | - | 2 (0+2) | 18 (10+8) | n/a -- not measured |
| `daqreader` | daq configuration | (b) | migrator `DID-matlab:migrators_j/daqreader.m`; 5 consuming reference(s) (5 per-document migrator); minted as a document class at 1 site(s) (1 per-document migrator); decided target(s) built: `software` | 1 (1+0) | 2 (2+0) | - | 51 (45+6) | n/a -- not measured |
| `daqreader_epochdata_ingested` | daq ingested payloads | (b) | migrator `DID-matlab:migrators_j/daqreader_epochdata_ingested.m`; 3 consuming reference(s) (3 per-document migrator); minted as a document class at 1 site(s) (1 per-document migrator); decided target(s) built: `relative_reference` | 1 (1+0) | 2 (2+0) | 2 (2+0) | 26 (20+6) | n/a -- not measured |
| `daqreader_image_epochdata_ingested` | daq ingested payloads | (b) | migrator `DID-matlab:migrators_j/daqreader_image_epochdata_ingested.m`; decided target(s) built: `image_observation`, `relative_reference`, `sampled_body` | - | - | - | 13 (11+2) | n/a -- not measured |
| `daqsystem` | daq configuration | (b) | migrator `DID-matlab:migrators_j/daqsystem.m`; 3 consuming reference(s) (3 per-document migrator); decided target(s) built: `acquisition_system` | - | - | - | 35 (33+2) | n/a -- not measured |
| `ensemble` | ensemble | (b) | 1 consuming reference(s) (1 per-document migrator); decided target(s) built: `subject`, `directed_relation`, `sampled_body` | - | - | - | 25 (23+2) | n/a -- not measured |
| `epoch_bounded_reference` | time_reference | (b) | 11 consuming reference(s) (11 per-document migrator) | 2 (2+0) discounted | 3 (3+0) | 2 (2+0) | 40 (36+4) | n/a -- not measured |
| `epochfiles_ingested` | epoch | (b) | migrator `DID-matlab:migrators_j/epochfiles_ingested.m`; 16 consuming reference(s) (16 batch post-pass); decided target(s) built: `ingestion_manifest` | - | - | - | 47 (18+29) | n/a -- not measured |
| `epochid` | epoch | (b) | 15 consuming reference(s) (14 per-document migrator, 1 batch post-pass) | - | 1 (1+0) | 16 (10+6) | 100 (78+22) | n/a -- not measured |
| `filenavigator` | file navigation | (b) | migrator `DID-matlab:migrators_j/filenavigator.m`; 3 consuming reference(s) (3 per-document migrator); decided target(s) built: `epoch_file_pattern` | - | - | - | 28 (27+1) | n/a -- not measured |
| `filter` | frequency_filter | (b) | 2 consuming reference(s) (2 per-document migrator); decided target(s) built: `frequency_filter` | - | - | 2 (2+0) | 39 (34+5) | n/a -- not measured |
| `interaction_purpose` | misc singletons | (a) | *none* | - | - | - | 3 (3+0) | n/a -- not measured |
| `ngrid` | image / ngrid | (b) | 8 consuming reference(s) (8 per-document migrator) | - | 1 (1+0) | - | 88 (85+3) | n/a -- not measured |
| `projectvar` | misc singletons | (a) | *none* | - | - | - | 3 (3+0) | n/a -- not measured |
| `session_bounded_reference` | time_reference | (b) | 1 consuming reference(s) (1 batch post-pass) | 1 (1+0) discounted | 1 (1+0) | 1 (0+1) | 15 (3+12) | n/a -- not measured |
| `session_relative_reference` | time_reference | (b) | 1 consuming reference(s) (1 batch post-pass) | 11 (9+2) discounted | 11 (9+2) | 1 (0+1) | 32 (19+13) | n/a -- not measured |
| `stimulus_presentation` | stimulus | (b) | migrator `DID-matlab:migrators_j/stimulus_presentation.m`; 6 consuming reference(s) (6 per-document migrator); decided target(s) built: `timed_sequence`, `timed_sequence_manipulation` | - | - | - | 45 (43+2) | n/a -- not measured |
| `syncgraph` | sync configuration | (b) | migrator `DID-matlab:migrators_j/syncgraph.m`; 5 consuming reference(s) (2 per-document migrator, 3 batch post-pass); decided target(s) built: `clock_alignment_policy` | - | - | - | 50 (31+19) | n/a -- not measured |
| `syncrule` | sync configuration | (b) | migrator `DID-matlab:migrators_j/syncrule.m`; 2 consuming reference(s) (2 per-document migrator); decided target(s) built: `clock_alignment_configuration` | - | - | - | 38 (36+2) | n/a -- not measured |
| `syncrule_mapping` | sync mapping | (b) | migrator `DID-matlab:migrators_j/syncrule_mapping.m`; 7 consuming reference(s) (2 per-document migrator, 5 batch post-pass); minted as a document class at 1 site(s) (1 per-document migrator); decided target(s) built: `clock_alignment` | 1 (1+0) | 1 (1+0) | 2 (0+2) | 47 (27+20) | n/a -- not measured |
| `time_reference` | time_reference | (b) | 5 consuming reference(s) (4 per-document migrator, 1 batch post-pass) | - | 18 (15+3) | 26 (19+7) | 46 (37+9) | n/a -- not measured |

#### (a) decided, nothing built -- 2

- `interaction_purpose` (misc singletons) -- mentioned in 3 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/openminds_stimulus.m:49 (comment_mention)`, `DID-matlab:migrators_j/openminds_stimulus.m:50 (comment_mention)`, `DID-matlab:migrators_j/openminds_stimulus.m:70 (comment_mention)`
- `projectvar` (misc singletons) -- mentioned in 3 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:360 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:378 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:38 (comment_mention)`

#### (b) built, awaiting corpus proof -- 24

- `acquisition_epoch` (epoch) -- consumed at 1 site(s), per-document migrator: `NDI-matlab:ndi_second_pass/ensembleMembership.m:705 (guard)`; consumed at 5 site(s), batch post-pass: `DID-matlab:convert/epochMint.m:2550 (guard)`, `DID-matlab:convert/epochMint.m:2551 (field_read)`, `DID-matlab:convert/epochMint.m:2552 (field_read)`, `DID-matlab:convert/epochMint.m:2555 (field_read)`, `DID-matlab:convert/epochMint.m:803 (guard)`; MINTED as a document class at 1 site(s), per-document migrator: `DID-matlab:migrators_j/element_epoch.m:130 (emitted_class)`; a block of this name is WRITTEN at 1 site(s), per-document migrator: `DID-matlab:migrators_j/element_epoch.m:132 (field_write)`; mentioned in 29 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:664 (comment_mention)`, `DID-matlab:migrators_j/binaryseries_parameters.m:39 (comment_mention)`, `DID-matlab:migrators_j/daqreader_image_epochdata_ingested.m:168 (comment_mention)`, `DID-matlab:migrators_j/element_epoch.m:10 (comment_mention)`, `DID-matlab:migrators_j/element_epoch.m:100 (comment_mention)`, `DID-matlab:migrators_j/element_epoch.m:102 (comment_mention)` ...; mentioned in 17 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/epochMint.m:25 (comment_mention)`, `DID-matlab:convert/epochMint.m:2539 (comment_mention)`, `DID-matlab:convert/epochMint.m:2609 (comment_mention)`, `DID-matlab:convert/epochMint.m:27 (comment_mention)`, `DID-matlab:convert/epochMint.m:40 (comment_mention)`, `DID-matlab:convert/epochMint.m:442 (comment_mention)` ...
- `app` (software) -- consumed at 2 site(s), per-document migrator: `DID-matlab:migrators_j/private/jSoftwareFromApp.m:124 (guard)`, `DID-matlab:migrators_j/private/jSoftwareFromApp.m:125 (field_read)`; consumed at 3 site(s), batch post-pass: `DID-matlab:convert/resolveValidIntervals.m:641 (guard)`, `DID-matlab:convert/universalRenames.m:285 (guard)`, `DID-matlab:convert/universalRenames.m:286 (field_read)`; a block of this name is WRITTEN at 1 site(s), per-document migrator: `DID-matlab:migrators_j/private/jMethodParameters.m:107 (field_write)`; a block of this name is WRITTEN at 1 site(s), batch post-pass: `DID-matlab:convert/universalRenames.m:287 (field_write)`; NAMED as a string value at 1 site(s), batch post-pass: `DID-matlab:convert/resolveValidIntervals.m:1094 (named)`; mentioned in 163 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:127 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:143 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:375 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:376 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:459 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:464 (comment_mention)` ...; mentioned in 36 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/calcCommon.m:25 (comment_mention)`, `DID-matlab:convert/calcCommon.m:28 (comment_mention)`, `DID-matlab:convert/resolveOpenmindsCitations.m:879 (comment_mention)`, `DID-matlab:convert/resolveValidIntervals.m:1065 (comment_mention)`, `DID-matlab:convert/resolveValidIntervals.m:1068 (comment_mention)`, `DID-matlab:convert/resolveValidIntervals.m:1069 (comment_mention)` ...; target(s) BUILT: `software`
- `binaryseries_parameters` (misc singletons) -- migrator `DID-matlab:migrators_j/binaryseries_parameters.m`; NAMED as a string value at 1 site(s), per-document migrator: `DID-matlab:migrators_j/binaryseries_parameters.m:276 (named)`; mentioned in 15 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/+super/image_stack_parameters.m:94 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:308 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:537 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:538 (comment_mention)`, `DID-matlab:migrators_j/binaryseries_parameters.m:16 (comment_mention)`, `DID-matlab:migrators_j/binaryseries_parameters.m:189 (comment_mention)` ...; target(s) BUILT: `subject_statement`, `sampled_body`
- `control_designation` (stimulus) -- MINTED as a document class at 1 site(s), per-document migrator: `DID-matlab:migrators_j/control_stimulus_ids.m:111 (emitted_class)`; a block of this name is WRITTEN at 1 site(s), per-document migrator: `DID-matlab:migrators_j/control_stimulus_ids.m:133 (field_write)`; mentioned in 8 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:575 (comment_mention)`, `DID-matlab:migrators_j/control_stimulus_ids.m:3 (comment_mention)`, `DID-matlab:migrators_j/control_stimulus_ids.m:53 (comment_mention)`, `DID-matlab:migrators_j/control_stimulus_ids.m:60 (comment_mention)`, `DID-matlab:migrators_j/control_stimulus_ids.m:72 (comment_mention)`, `DID-matlab:migrators_j/control_stimulus_ids.m:79 (comment_mention)` ...
- `daqmetadatareader` (daq configuration) -- migrator `DID-matlab:migrators_j/daqmetadatareader.m`; consumed at 3 site(s), per-document migrator: `DID-matlab:migrators_j/daqmetadatareader.m:100 (guard)`, `DID-matlab:migrators_j/daqmetadatareader.m:101 (field_read)`, `DID-matlab:migrators_j/daqmetadatareader.m:102 (field_read)`; mentioned in 24 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:185 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:218 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:584 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:585 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader.m:13 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader.m:2 (comment_mention)` ...; target(s) BUILT: `acquisition_metadata_reader`
- `daqmetadatareader_epochdata_ingested` (daq ingested payloads) -- migrator `DID-matlab:migrators_j/daqmetadatareader_epochdata_ingested.m`; consumed at 2 site(s), batch post-pass: `DID-matlab:convert/epochMint.m:1049 (guard)`, `DID-matlab:convert/epochMint.m:1791 (field_read)`; NAMED as a string value at 2 site(s), batch post-pass: `DID-matlab:convert/epochMint.m:1080 (named)`, `DID-matlab:convert/epochMint.m:1790 (named)`; mentioned in 10 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:588 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader.m:20 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader.m:70 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader.m:77 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader_epochdata_ingested.m:21 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader_epochdata_ingested.m:25 (comment_mention)` ...; mentioned in 8 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/epochMint.m:1189 (comment_mention)`, `DID-matlab:convert/epochMint.m:211 (comment_mention)`, `DID-matlab:convert/epochMint.m:212 (comment_mention)`, `DID-matlab:convert/epochMint.m:24 (comment_mention)`, `DID-matlab:convert/epochMint.m:28 (comment_mention)`, `DID-matlab:convert/epochMint.m:287 (comment_mention)` ...; target(s) BUILT: `acquisition_metadata_file`
- `daqreader` (daq configuration) -- migrator `DID-matlab:migrators_j/daqreader.m`; consumed at 5 site(s), per-document migrator: `DID-matlab:migrators_j/daqreader.m:109 (guard)`, `DID-matlab:migrators_j/daqreader.m:110 (field_read)`, `DID-matlab:migrators_j/daqreader.m:111 (field_read)`, `DID-matlab:migrators_j/daqreader_ndr.m:32 (guard)`, `DID-matlab:migrators_j/daqreader_ndr.m:90 (field_read)`; MINTED as a document class at 1 site(s), per-document migrator: `DID-matlab:migrators_j/daqreader_ndr.m:25 (emitted_class)`; a block of this name is WRITTEN at 2 site(s), per-document migrator: `DID-matlab:migrators_j/daqreader_ndr.m:33 (field_write)`, `DID-matlab:migrators_j/daqreader_ndr.m:36 (field_write)`; mentioned in 45 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:174 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:228 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:591 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:592 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:605 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:608 (comment_mention)` ...; mentioned in 6 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/epochMint.m:1202 (comment_mention)`, `DID-matlab:convert/epochMint.m:1749 (comment_mention)`, `DID-matlab:convert/epochMint.m:1771 (comment_mention)`, `DID-matlab:convert/epochMint.m:1787 (comment_mention)`, `DID-matlab:convert/epochMint.m:1888 (comment_mention)`, `DID-matlab:convert/epochMint.m:298 (comment_mention)`; target(s) BUILT: `software`
- `daqreader_epochdata_ingested` (daq ingested payloads) -- migrator `DID-matlab:migrators_j/daqreader_epochdata_ingested.m`; consumed at 3 site(s), per-document migrator: `DID-matlab:migrators_j/daqreader_mfdaq_epochdata_ingested.m:40 (guard)`, `DID-matlab:migrators_j/daqreader_mfdaq_epochdata_ingested.m:41 (field_read)`, `DID-matlab:migrators_j/daqreader_mfdaq_epochdata_ingested.m:66 (field_read)`; MINTED as a document class at 1 site(s), per-document migrator: `DID-matlab:migrators_j/daqreader_mfdaq_epochdata_ingested.m:36 (emitted_class)`; a block of this name is WRITTEN at 2 site(s), per-document migrator: `DID-matlab:migrators_j/daqreader_mfdaq_epochdata_ingested.m:42 (field_write)`, `DID-matlab:migrators_j/daqreader_mfdaq_epochdata_ingested.m:48 (field_write)`; NAMED as a string value at 2 site(s), per-document migrator: `DID-matlab:migrators_j/daqreader_epochdata_ingested.m:109 (named)`, `DID-matlab:migrators_j/daqreader_image_epochdata_ingested.m:307 (named)`; mentioned in 20 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:594 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:603 (comment_mention)`, `DID-matlab:migrators_j/daqreader.m:55 (comment_mention)`, `DID-matlab:migrators_j/daqreader_image_epochdata_ingested.m:20 (comment_mention)`, `DID-matlab:migrators_j/daqreader_image_epochdata_ingested.m:21 (comment_mention)`, `DID-matlab:migrators_j/daqreader_image_epochdata_ingested.m:274 (comment_mention)` ...; mentioned in 6 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/epochMint.m:1724 (comment_mention)`, `DID-matlab:convert/epochMint.m:245 (comment_mention)`, `DID-matlab:convert/epochMint.m:2584 (comment_mention)`, `DID-matlab:convert/epochMint.m:304 (comment_mention)`, `DID-matlab:convert/epochMint.m:312 (comment_mention)`, `DID-matlab:convert/epochMint.m:774 (comment_mention)`; target(s) BUILT: `relative_reference`
- `daqreader_image_epochdata_ingested` (daq ingested payloads) -- migrator `DID-matlab:migrators_j/daqreader_image_epochdata_ingested.m`; mentioned in 11 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:597 (comment_mention)`, `DID-matlab:migrators_j/daqreader.m:56 (comment_mention)`, `DID-matlab:migrators_j/daqreader_epochdata_ingested.m:52 (comment_mention)`, `DID-matlab:migrators_j/daqreader_image_epochdata_ingested.m:119 (comment_mention)`, `DID-matlab:migrators_j/daqreader_image_epochdata_ingested.m:120 (comment_mention)`, `DID-matlab:migrators_j/daqreader_image_epochdata_ingested.m:155 (comment_mention)` ...; mentioned in 2 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/epochMint.m:248 (comment_mention)`, `DID-matlab:convert/epochMint.m:313 (comment_mention)`; target(s) BUILT: `image_observation`, `relative_reference`, `sampled_body`
- `daqsystem` (daq configuration) -- migrator `DID-matlab:migrators_j/daqsystem.m`; consumed at 3 site(s), per-document migrator: `DID-matlab:migrators_j/daqsystem.m:240 (guard)`, `DID-matlab:migrators_j/daqsystem.m:241 (field_read)`, `DID-matlab:migrators_j/daqsystem.m:242 (field_read)`; mentioned in 33 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:159 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:176 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:197 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:613 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:614 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader.m:68 (comment_mention)` ...; mentioned in 2 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/resolveEpochProbemap.m:183 (comment_mention)`, `DID-matlab:convert/resolveEpochProbemap.m:184 (comment_mention)`; target(s) BUILT: `acquisition_system`
- `ensemble` (ensemble) -- consumed at 1 site(s), per-document migrator: `NDI-matlab:ndi_second_pass/ensembleMembership.m:438 (guard)`; mentioned in 23 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/element_epoch.m:89 (comment_mention)`, `DID-matlab:migrators_j/element_epoch.m:91 (comment_mention)`, `DID-matlab:migrators_j/element_epoch.m:92 (comment_mention)`, `DID-matlab:migrators_j/hartley_calc.m:151 (comment_mention)`, `DID-matlab:migrators_j/private/jAcquisitionChannels.m:73 (comment_mention)`, `DID-matlab:migrators_j/private/jRecordingModality.m:240 (comment_mention)` ...; mentioned in 2 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/resolveLawnPlateSubjects.m:1358 (comment_mention)`, `DID-matlab:convert/resolveResponseParameters.m:68 (comment_mention)`; target(s) BUILT: `subject`, `directed_relation`, `sampled_body`
- `epoch_bounded_reference` (time_reference) -- consumed at 11 site(s), per-document migrator: `NDI-matlab:ndi_second_pass/epochAnchorFold.m:361 (guard)`, `NDI-matlab:ndi_second_pass/epochAnchorFold.m:465 (guard)`, `NDI-matlab:ndi_second_pass/epochAnchorFold.m:466 (field_read)`, `NDI-matlab:ndi_second_pass/epochAnchorFold.m:467 (field_read)`, `NDI-matlab:ndi_second_pass/epochAnchorFold.m:468 (field_read)`, `NDI-matlab:ndi_second_pass/epochAnchorFold.m:469 (field_read)` ...; MINTED as a document class at 2 site(s), per-document migrator: `DID-matlab:migrators_j/pyraview.m:192 (emitted_class)`, `NDI-matlab:ndi_second_pass/stimulusBathToBath.m:166 (emitted_class)`; minted at 2 site(s) (2 per-document migrator), NOT counted as build progress: the signed decision retires this class in favour of `relative_reference`, so an emission is work still to undo; a block of this name is WRITTEN at 3 site(s), per-document migrator: `DID-matlab:migrators_j/pyraview.m:205 (field_write)`, `DID-matlab:migrators_j/pyraview.m:223 (field_write)`, `NDI-matlab:ndi_second_pass/stimulusBathToBath.m:176 (field_write)`; NAMED as a string value at 2 site(s), per-document migrator: `DID-matlab:migrators_j/syncrule_mapping.m:182 (named)`, `NDI-matlab:ndi_second_pass/epochAnchorFold.m:476 (named)`; mentioned in 36 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/pyraview.m:148 (comment_mention)`, `DID-matlab:migrators_j/pyraview.m:161 (comment_mention)`, `DID-matlab:migrators_j/pyraview.m:183 (comment_mention)`, `DID-matlab:migrators_j/pyraview.m:219 (comment_mention)`, `DID-matlab:migrators_j/pyraview.m:76 (comment_mention)`, `DID-matlab:migrators_j/stimulus_bath.m:23 (comment_mention)` ...; mentioned in 4 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/resolveDeferredBaths.m:15 (comment_mention)`, `DID-matlab:convert/resolveDeferredBaths.m:47 (comment_mention)`, `DID-matlab:convert/resolveSessionAnchors.m:108 (comment_mention)`, `DID-matlab:convert/resolveSessionAnchors.m:72 (comment_mention)`
- `epochfiles_ingested` (epoch) -- migrator `DID-matlab:migrators_j/epochfiles_ingested.m`; consumed at 16 site(s), batch post-pass: `DID-matlab:convert/epochMint.m:2237 (guard)`, `DID-matlab:convert/epochMint.m:2329 (guard)`, `DID-matlab:convert/epochMint.m:2330 (field_read)`, `DID-matlab:convert/epochMint.m:2331 (field_read)`, `DID-matlab:convert/epochMint.m:2334 (field_read)`, `DID-matlab:convert/resolveEpochProbemap.m:260 (guard)` ...; mentioned in 18 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:160 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:665 (comment_mention)`, `DID-matlab:migrators_j/epochfiles_ingested.m:115 (comment_mention)`, `DID-matlab:migrators_j/epochfiles_ingested.m:192 (comment_mention)`, `DID-matlab:migrators_j/epochfiles_ingested.m:203 (comment_mention)`, `DID-matlab:migrators_j/epochfiles_ingested.m:220 (comment_mention)` ...; mentioned in 29 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/epochMint.m:169 (comment_mention)`, `DID-matlab:convert/epochMint.m:186 (comment_mention)`, `DID-matlab:convert/epochMint.m:2083 (comment_mention)`, `DID-matlab:convert/epochMint.m:2090 (comment_mention)`, `DID-matlab:convert/epochMint.m:2091 (comment_mention)`, `DID-matlab:convert/epochMint.m:2164 (comment_mention)` ...; target(s) BUILT: `ingestion_manifest`
- `epochid` (epoch) -- consumed at 14 site(s), per-document migrator: `DID-matlab:migrators_j/private/jMethodParameters.m:122 (guard)`, `NDI-matlab:ndi_second_pass/bodyResolver.m:348 (guard)`, `NDI-matlab:ndi_second_pass/bodyResolver.m:349 (guard)`, `NDI-matlab:ndi_second_pass/bodyResolver.m:350 (field_read)`, `NDI-matlab:ndi_second_pass/ensembleMembership.m:731 (guard)`, `NDI-matlab:ndi_second_pass/ensembleMembership.m:732 (field_read)` ...; consumed at 1 site(s), batch post-pass: `DID-matlab:convert/epochMint.m:968 (guard)`; a block of this name is WRITTEN at 1 site(s), per-document migrator: `DID-matlab:migrators_j/private/jMethodParameters.m:126 (field_write)`; NAMED as a string value at 10 site(s), per-document migrator: `DID-matlab:migrators_j/epochfiles_ingested.m:265 (named)`, `DID-matlab:migrators_j/private/jMethodParameters.m:123 (named)`, `DID-matlab:migrators_j/pyraview.m:186 (named)`, `DID-matlab:migrators_j/pyraview.m:193 (named)`, `DID-matlab:migrators_j/pyraview.m:198 (named)`, `NDI-matlab:ndi_second_pass/epochAnchorFold.m:479 (named)` ...; NAMED as a string value at 6 site(s), batch post-pass: `DID-matlab:convert/epochMint.m:1056 (named)`, `DID-matlab:convert/epochMint.m:2026 (named)`, `DID-matlab:convert/epochMint.m:2031 (named)`, `DID-matlab:convert/epochMint.m:808 (named)`, `DID-matlab:convert/epochMint.m:969 (named)`, `DID-matlab:convert/resolveEpochProbemap.m:963 (named)`; mentioned in 78 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:142 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:144 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader_epochdata_ingested.m:22 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader_epochdata_ingested.m:29 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader_epochdata_ingested.m:31 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader_epochdata_ingested.m:35 (comment_mention)` ...; mentioned in 22 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/epochIndex.m:16 (comment_mention)`, `DID-matlab:convert/epochIndex.m:235 (comment_mention)`, `DID-matlab:convert/epochIndex.m:53 (comment_mention)`, `DID-matlab:convert/epochIndex.m:96 (comment_mention)`, `DID-matlab:convert/epochMint.m:1053 (comment_mention)`, `DID-matlab:convert/epochMint.m:113 (comment_mention)` ...
- `filenavigator` (file navigation) -- migrator `DID-matlab:migrators_j/filenavigator.m`; consumed at 3 site(s), per-document migrator: `DID-matlab:migrators_j/filenavigator.m:121 (guard)`, `DID-matlab:migrators_j/filenavigator.m:122 (field_read)`, `DID-matlab:migrators_j/filenavigator.m:123 (field_read)`; mentioned in 27 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:158 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:218 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:463 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:502 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:667 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:668 (comment_mention)` ...; mentioned in 1 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/v1_to_v2.m:811 (comment_mention)`; target(s) BUILT: `epoch_file_pattern`
- `filter` (frequency_filter) -- consumed at 2 site(s), per-document migrator: `DID-matlab:migrators_j/private/jFrequencyFilter.m:112 (guard)`, `DID-matlab:migrators_j/private/jFrequencyFilter.m:113 (field_read)`; NAMED as a string value at 2 site(s), per-document migrator: `DID-matlab:migrators_j/private/jSpikeExtractionSettings.m:159 (named)`, `DID-matlab:migrators_j/vmspikefilteringparameters.m:192 (named)`; mentioned in 34 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:297 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:306 (comment_mention)`, `DID-matlab:migrators_j/epochfiles_ingested.m:55 (comment_mention)`, `DID-matlab:migrators_j/ontology_image.m:24 (comment_mention)`, `DID-matlab:migrators_j/private/jFrequencyFilter.m:105 (comment_mention)`, `DID-matlab:migrators_j/private/jFrequencyFilter.m:123 (comment_mention)` ...; mentioned in 5 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/epochMint.m:2359 (comment_mention)`, `DID-matlab:convert/resolveSessionAnchors.m:84 (comment_mention)`, `DID-matlab:convert/universalRenames.m:35 (comment_mention)`, `DID-matlab:convert/universalRenames.m:564 (comment_mention)`, `DID-matlab:convert/universalRenames.m:565 (comment_mention)`; target(s) BUILT: `frequency_filter`
- `ngrid` (image / ngrid) -- consumed at 8 site(s), per-document migrator: `DID-matlab:migrators_j/+super/ngrid.m:125 (guard)`, `DID-matlab:migrators_j/+super/ngrid.m:129 (field_read)`, `DID-matlab:migrators_j/hartley_calc.m:268 (guard)`, `DID-matlab:migrators_j/hartley_calc.m:430 (field_read)`, `DID-matlab:migrators_j/ontology_image.m:273 (guard)`, `DID-matlab:migrators_j/ontology_image.m:387 (field_read)` ...; a block of this name is WRITTEN at 1 site(s), per-document migrator: `DID-matlab:migrators_j/+super/ngrid.m:144 (field_write)`; mentioned in 85 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/+super/ngrid.m:19 (comment_mention)`, `DID-matlab:migrators_j/+super/ngrid.m:2 (comment_mention)`, `DID-matlab:migrators_j/+super/ngrid.m:20 (comment_mention)`, `DID-matlab:migrators_j/+super/ngrid.m:21 (comment_mention)`, `DID-matlab:migrators_j/+super/ngrid.m:32 (comment_mention)`, `DID-matlab:migrators_j/+super/ngrid.m:38 (comment_mention)` ...; mentioned in 3 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/v1_to_v2.m:792 (comment_mention)`, `DID-matlab:convert/v1_to_v2.m:798 (comment_mention)`, `DID-matlab:convert/v1_to_v2.m:803 (comment_mention)`
- `session_bounded_reference` (time_reference) -- consumed at 1 site(s), batch post-pass: `DID-matlab:convert/resolveSessionAnchors.m:417 (guard)`; MINTED as a document class at 1 site(s), per-document migrator: `DID-matlab:migrators_j/ontology_table_row.m:275 (emitted_class)`; minted at 1 site(s) (1 per-document migrator), NOT counted as build progress: the signed decision retires this class in favour of `relative_reference`, so an emission is work still to undo; a block of this name is WRITTEN at 1 site(s), per-document migrator: `DID-matlab:migrators_j/ontology_table_row.m:281 (field_write)`; NAMED as a string value at 1 site(s), batch post-pass: `DID-matlab:convert/epochMint.m:2208 (named)`; mentioned in 3 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/ontology_table_row.m:271 (comment_mention)`, `DID-matlab:migrators_j/ontology_table_row.m:35 (comment_mention)`, `NDI-matlab:ndi_second_pass/epochAnchorFold.m:126 (comment_mention)`; mentioned in 12 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/resolveSessionAnchors.m:17 (comment_mention)`, `DID-matlab:convert/resolveSessionAnchors.m:19 (comment_mention)`, `DID-matlab:convert/resolveSessionAnchors.m:226 (comment_mention)`, `DID-matlab:convert/resolveSessionAnchors.m:237 (comment_mention)`, `DID-matlab:convert/resolveSessionAnchors.m:265 (comment_mention)`, `DID-matlab:convert/resolveSessionAnchors.m:39 (comment_mention)` ...
- `session_relative_reference` (time_reference) -- consumed at 1 site(s), batch post-pass: `DID-matlab:convert/resolveSessionAnchors.m:416 (guard)`; MINTED as a document class at 9 site(s), per-document migrator: `DID-matlab:migrators_j/fitcurve.m:147 (emitted_class)`, `DID-matlab:migrators_j/image_stack.m:279 (emitted_class)`, `DID-matlab:migrators_j/jrclust_clusters.m:85 (emitted_class)`, `DID-matlab:migrators_j/neuron_extracellular.m:357 (emitted_class)`, `DID-matlab:migrators_j/ontology_table_row.m:871 (emitted_class)`, `DID-matlab:migrators_j/private/jSessionAnchor.m:60 (emitted_class)` ...; MINTED as a document class at 2 site(s), batch post-pass: `DID-matlab:convert/resolveDeferredBaths.m:384 (emitted_class)`, `DID-matlab:convert/resolveDeferredBaths.m:436 (emitted_class)`; minted at 11 site(s) (9 per-document migrator, 2 batch post-pass), NOT counted as build progress: the signed decision retires this class in favour of `relative_reference`, so an emission is work still to undo; a block of this name is WRITTEN at 9 site(s), per-document migrator: `DID-matlab:migrators_j/fitcurve.m:154 (field_write)`, `DID-matlab:migrators_j/image_stack.m:284 (field_write)`, `DID-matlab:migrators_j/jrclust_clusters.m:90 (field_write)`, `DID-matlab:migrators_j/neuron_extracellular.m:362 (field_write)`, `DID-matlab:migrators_j/ontology_table_row.m:879 (field_write)`, `DID-matlab:migrators_j/private/jSessionAnchor.m:68 (field_write)` ...; a block of this name is WRITTEN at 2 site(s), batch post-pass: `DID-matlab:convert/resolveDeferredBaths.m:395 (field_write)`, `DID-matlab:convert/resolveDeferredBaths.m:444 (field_write)`; NAMED as a string value at 1 site(s), batch post-pass: `DID-matlab:convert/epochMint.m:2208 (named)`; mentioned in 19 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/fitcurve.m:13 (comment_mention)`, `DID-matlab:migrators_j/image_stack.m:25 (comment_mention)`, `DID-matlab:migrators_j/jrclust_clusters.m:21 (comment_mention)`, `DID-matlab:migrators_j/jrclust_clusters.m:41 (comment_mention)`, `DID-matlab:migrators_j/neuron_extracellular.m:250 (comment_mention)`, `DID-matlab:migrators_j/neuron_extracellular.m:27 (comment_mention)` ...; mentioned in 13 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/epochMint.m:2132 (comment_mention)`, `DID-matlab:convert/epochMint.m:2137 (comment_mention)`, `DID-matlab:convert/resolveDeferredBaths.m:13 (comment_mention)`, `DID-matlab:convert/resolveDeferredBaths.m:31 (comment_mention)`, `DID-matlab:convert/resolveDeferredBaths.m:381 (comment_mention)`, `DID-matlab:convert/resolveDeferredBaths.m:390 (comment_mention)` ...
- `stimulus_presentation` (stimulus) -- migrator `DID-matlab:migrators_j/stimulus_presentation.m`; consumed at 6 site(s), per-document migrator: `NDI-matlab:ndi_second_pass/hartleyBasisGratings.m:354 (guard)`, `NDI-matlab:ndi_second_pass/hartleyBasisGratings.m:357 (field_read)`, `NDI-matlab:ndi_second_pass/stimulusPresentationToManipulation.m:47 (guard)`, `NDI-matlab:ndi_second_pass/stimulusPresentationToManipulation.m:48 (field_read)`, `NDI-matlab:ndi_second_pass/stimulusPresentationToTimedSequence.m:259 (guard)`, `NDI-matlab:ndi_second_pass/stimulusPresentationToTimedSequence.m:260 (field_read)`; mentioned in 43 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:853 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:854 (comment_mention)`, `DID-matlab:migrators_j/control_stimulus_ids.m:116 (comment_mention)`, `DID-matlab:migrators_j/control_stimulus_ids.m:32 (comment_mention)`, `DID-matlab:migrators_j/control_stimulus_ids.m:46 (comment_mention)`, `DID-matlab:migrators_j/control_stimulus_ids.m:74 (comment_mention)` ...; mentioned in 2 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/universalRenames.m:471 (comment_mention)`, `DID-matlab:convert/v1_to_v2.m:1004 (comment_mention)`; target(s) BUILT: `timed_sequence`, `timed_sequence_manipulation`
- `syncgraph` (sync configuration) -- migrator `DID-matlab:migrators_j/syncgraph.m`; consumed at 2 site(s), per-document migrator: `DID-matlab:migrators_j/syncgraph.m:128 (guard)`, `DID-matlab:migrators_j/syncgraph.m:129 (field_read)`; consumed at 3 site(s), batch post-pass: `DID-matlab:convert/resolveClockAlignment.m:144 (guard)`, `DID-matlab:convert/resolveClockAlignment.m:162 (field_read)`, `DID-matlab:convert/resolveClockAlignment.m:168 (guard)`; mentioned in 31 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:468 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:895 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:896 (comment_mention)`, `DID-matlab:migrators_j/private/jClockAlignmentBodies.m:62 (comment_mention)`, `DID-matlab:migrators_j/private/jClockAlignmentBodies.m:66 (comment_mention)`, `DID-matlab:migrators_j/private/jClockAlignmentBodies.m:71 (comment_mention)` ...; mentioned in 19 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/epochIndex.m:243 (comment_mention)`, `DID-matlab:convert/epochMint.m:365 (comment_mention)`, `DID-matlab:convert/epochMint.m:717 (comment_mention)`, `DID-matlab:convert/resolveClockAlignment.m:139 (comment_mention)`, `DID-matlab:convert/resolveClockAlignment.m:140 (comment_mention)`, `DID-matlab:convert/resolveClockAlignment.m:16 (comment_mention)` ...; target(s) BUILT: `clock_alignment_policy`
- `syncrule` (sync configuration) -- migrator `DID-matlab:migrators_j/syncrule.m`; consumed at 2 site(s), per-document migrator: `DID-matlab:migrators_j/syncrule.m:95 (guard)`, `DID-matlab:migrators_j/syncrule.m:96 (field_read)`; mentioned in 36 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:468 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:897 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:898 (comment_mention)`, `DID-matlab:migrators_j/daqsystem.m:86 (comment_mention)`, `DID-matlab:migrators_j/private/jAcquisitionChannels.m:15 (comment_mention)`, `DID-matlab:migrators_j/private/jAcquisitionChannels.m:18 (comment_mention)` ...; mentioned in 2 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/epochMint.m:1351 (comment_mention)`, `DID-matlab:convert/resolveClockAlignment.m:19 (comment_mention)`; target(s) BUILT: `clock_alignment_configuration`
- `syncrule_mapping` (sync mapping) -- migrator `DID-matlab:migrators_j/syncrule_mapping.m`; consumed at 2 site(s), per-document migrator: `DID-matlab:migrators_j/syncrule_mapping.m:106 (guard)`, `DID-matlab:migrators_j/syncrule_mapping.m:107 (field_read)`; consumed at 5 site(s), batch post-pass: `DID-matlab:convert/epochMint.m:1364 (guard)`, `DID-matlab:convert/epochMint.m:1795 (field_read)`, `DID-matlab:convert/epochMint.m:2001 (guard)`, `DID-matlab:convert/epochMint.m:2002 (field_read)`, `DID-matlab:convert/epochMint.m:2005 (field_read)`; MINTED as a document class at 1 site(s), per-document migrator: `DID-matlab:migrators_j/syncrule_mapping.m:131 (emitted_class)`; a block of this name is WRITTEN at 1 site(s), per-document migrator: `DID-matlab:migrators_j/syncrule_mapping.m:149 (field_write)`; NAMED as a string value at 2 site(s), batch post-pass: `DID-matlab:convert/epochMint.m:1385 (named)`, `DID-matlab:convert/epochMint.m:1794 (named)`; mentioned in 27 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:899 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:900 (comment_mention)`, `DID-matlab:migrators_j/epochfiles_ingested.m:204 (comment_mention)`, `DID-matlab:migrators_j/private/jClockAlignmentBodies.m:10 (comment_mention)`, `DID-matlab:migrators_j/private/jClockAlignmentBodies.m:170 (comment_mention)`, `DID-matlab:migrators_j/private/jClockAlignmentBodies.m:173 (comment_mention)` ...; mentioned in 20 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/epochMint.m:1328 (comment_mention)`, `DID-matlab:convert/epochMint.m:1334 (comment_mention)`, `DID-matlab:convert/epochMint.m:1340 (comment_mention)`, `DID-matlab:convert/epochMint.m:1342 (comment_mention)`, `DID-matlab:convert/epochMint.m:1413 (comment_mention)`, `DID-matlab:convert/epochMint.m:1648 (comment_mention)` ...; target(s) BUILT: `clock_alignment`
- `time_reference` (time_reference) -- consumed at 4 site(s), per-document migrator: `DID-matlab:migrators_j/private/jClockAlignmentBodies.m:179 (guard)`, `DID-matlab:migrators_j/private/jClockAlignmentBodies.m:180 (field_read)`, `DID-matlab:migrators_j/private/jClockAlignmentBodies.m:181 (field_read)`, `NDI-matlab:ndi_second_pass/epochAnchorFold.m:483 (guard)`; consumed at 1 site(s), batch post-pass: `DID-matlab:convert/resolveSessionAnchors.m:560 (guard)`; a block of this name is WRITTEN at 15 site(s), per-document migrator: `DID-matlab:migrators_j/fitcurve.m:153 (field_write)`, `DID-matlab:migrators_j/image_stack.m:283 (field_write)`, `DID-matlab:migrators_j/jrclust_clusters.m:89 (field_write)`, `DID-matlab:migrators_j/neuron_extracellular.m:361 (field_write)`, `DID-matlab:migrators_j/ontology_table_row.m:280 (field_write)`, `DID-matlab:migrators_j/ontology_table_row.m:878 (field_write)` ...; a block of this name is WRITTEN at 3 site(s), batch post-pass: `DID-matlab:convert/resolveDeferredBaths.m:394 (field_write)`, `DID-matlab:convert/resolveDeferredBaths.m:443 (field_write)`, `DID-matlab:convert/resolveValidIntervals.m:965 (field_write)`; NAMED as a string value at 19 site(s), per-document migrator: `DID-matlab:migrators_j/fitcurve.m:147 (named)`, `DID-matlab:migrators_j/image_stack.m:279 (named)`, `DID-matlab:migrators_j/jrclust_clusters.m:85 (named)`, `DID-matlab:migrators_j/neuron_extracellular.m:357 (named)`, `DID-matlab:migrators_j/ontology_table_row.m:276 (named)`, `DID-matlab:migrators_j/ontology_table_row.m:873 (named)` ...; NAMED as a string value at 7 site(s), batch post-pass: `DID-matlab:convert/epochMint.m:2023 (named)`, `DID-matlab:convert/epochMint.m:2626 (named)`, `DID-matlab:convert/resolveDeferredBaths.m:386 (named)`, `DID-matlab:convert/resolveDeferredBaths.m:438 (named)`, `DID-matlab:convert/resolveEpochProbemap.m:638 (named)`, `DID-matlab:convert/resolveSessionAnchors.m:550 (named)` ...; mentioned in 37 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/daqreader_epochdata_ingested.m:21 (comment_mention)`, `DID-matlab:migrators_j/neuron_extracellular.m:250 (comment_mention)`, `DID-matlab:migrators_j/ontology_table_row.m:172 (comment_mention)`, `DID-matlab:migrators_j/ontology_table_row.m:196 (comment_mention)`, `DID-matlab:migrators_j/ontology_table_row.m:199 (comment_mention)`, `DID-matlab:migrators_j/ontology_table_row.m:214 (comment_mention)` ...; mentioned in 9 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/epochMint.m:1991 (comment_mention)`, `DID-matlab:convert/epochMint.m:2022 (comment_mention)`, `DID-matlab:convert/epochMint.m:2171 (comment_mention)`, `DID-matlab:convert/epochMint.m:2575 (comment_mention)`, `DID-matlab:convert/resolveEpochProbemap.m:630 (comment_mention)`, `DID-matlab:convert/resolveSessionAnchors.m:22 (comment_mention)` ...

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

**DENOMINATOR: 26 signed families. 16 named at least one decided target class and were checked against the built tree; 10 named none and are UNCHECKED HERE.**

Across the 16 checked: 30 distinct target class(es), 30 present in the built set, 0 not.

So for the checked families the schema half is DONE and what
remains is MIGRATOR work. Do not read those rows as a build
queue for schema.

**The other 10 are unchecked, NOT clean.** Nothing above says anything about them, and the reason differs per family:

- **stranded sources** (2 class(es)): 2 `generic_file`, `imageCollection` -- has a ledger row whose `decided_targets` is EMPTY -- the gap the ledger now flags by name
- **time_reference** (4 class(es)): 4 `epoch_bounded_reference`, `session_bounded_reference`, `session_relative_reference`, `time_reference` -- a V_eta target class, so the coverage ledger has no row for it (it is not a v1 source)
- **receptive field fold** (1 class(es)): 1 `hartley_calc` -- has a ledger row whose `decided_targets` is EMPTY -- the gap the ledger now flags by name
- **confirm sheet 2026-08-17** (5 class(es)): 5 `jrclust_clusters`, `oridirtuning_calc`, `probe_location`, `treatment`, `tuningcurve_calc` -- has a ledger row whose `decided_targets` is EMPTY -- the gap the ledger now flags by name
- **image / ngrid** (2 class(es)): 2 `imageStack_parameters`, `ngrid` -- has a ledger row whose `decided_targets` is EMPTY -- the gap the ledger now flags by name
- **openMINDS** (1 class(es)): 1 `openminds` -- has a ledger row whose `decided_targets` is EMPTY -- the gap the ledger now flags by name
- **stimulus parameters** (2 class(es)): 1 `stimulus_parameter` -- has a ledger row whose `decided_targets` is EMPTY -- the gap the ledger now flags by name; 1 `stimulus_parameter_table` -- its only decided target is ITSELF, a signed passthrough, which is stripped because it is not build evidence
- **subject measurement** (1 class(es)): 1 `subjectmeasurement` -- has a ledger row whose `decided_targets` is EMPTY -- the gap the ledger now flags by name
- **subject** (1 class(es)): 1 `subject` -- its only decided target is ITSELF, a signed passthrough, which is stripped because it is not build evidence
- **session** (1 class(es)): 1 `session` -- its only decided target is ITSELF, a signed passthrough, which is stripped because it is not build evidence

Only the `decided_targets` EMPTY bucket is a missing record. The
others are correct states that this check cannot use: a V_eta
target class has no v1 row to carry a target, and a signed
passthrough deliberately names no new class. `tools/coverage.py`
now records dissolution POSITIVELY (with the sign-off quoted) and
renders a row with neither a target nor a dissolution as an
explicit gap, so the empty bucket is enumerable rather than
indistinguishable from a settled one.

Every one of these re-targets migrators that are already written, which
is why migrator work before the target closes is rework.

| family | classes | targets built | decision | recorded in |
|---|---|---|---|---|
| **stranded sources** | 2 | no target recorded | generic_file -> term_observation + opaque_body; imageCollection -> tombstone. SIGNED 2026-08-11 | `V_eta_OPEN_WORK.md` |
| **logical_observation** | 1 | 1 of 1 | BUILT AHEAD OF THE DECISION, AND NOW DORMANT BY IT. Decided AND SIGNED 2026-08-12: the target is ONE logical_observation per source document carrying an ARRAY of booleans on a time axis, and it WAITS for axes[] (#45 -> #32); the 1->N decomposition resolveValidIntervals already contains is explicitly rejected as an interim, so that pass is DORMANT (census only, emits nothing) and the documents live on the v1 tombstone. Classes renamed validity -> logical | `V_eta_logical_observation_plan.md` |
| **epochclocktimes** | 1 | 1 of 1 | epochclocktimes == acquisition_epoch.clocks[], so its content becomes relative_reference documents; the class does not return. EQUIVALENCE ONLY -- Fork A (where the epoch anchor lives) is open and gates the build | `V_eta_time_reference_family_plan.md` |
| **time_reference** | 4 | no target recorded | 8 classes collapse to absolute_reference + relative_reference (4 of the 8 executed 2026-08-11: epoch_relative_reference, event_bounded_reference, event_relative_reference, utc_reference deleted -- no template, no emitter, no reference; the other 4 await their emitters) | `V_eta_time_reference_model_plan.md` |
| **stimulus** | 2 | 2 of 2 | timed_sequence data_type + timed_sequence_manipulation leaf; control_designation resolved here | `V_eta_stimulus_model_plan.md` |
| **ensemble** | 1 | 3 of 3 | group subject + epoch-scoped member_of edges + rebuildable cache | `V_eta_ensemble_plan.md` |
| **receptive field fold** | 1 | no target recorded | hartley_calc migrates 1->1 id-preserved into a receptive_field_calculation leaf + receptive_field composite, payload in TWO sampled_body documents (STA, p-value); ngrid.coordinates fold into axes[].values | `V_eta_ngrid_family_findings.md` |
| **confirm sheet 2026-08-17** | 5 | no target recorded | each migrates today to the set the confirm sheet recorded, and that set IS the intended end state; no further fold is owed | `V_eta_go_forward_class_audit.md` |
| **image / ngrid** | 2 | no target recorded | ngrid phases into sampled_body; image is a standalone data_type; the two image_stack tombstones are held until the subject is recoverable | `V_eta_image_model_plan.md` |
| **epoch** | 4 | 1 of 1 | MINT `epoch` ENTITY (+ OPTIONAL `instrument_id`, 2026-08-06); element_epoch dissolves; epochid DROPPED; probemap -> edges (B) | `V_eta_epoch_plan.md` |
| **daq configuration** | 4 | 5 of 5 | acquisition_system + `acquisition_metadata_reader` keep ids; class names fold to software entities | `V_eta_daq_family_decisions.md` |
| **daq ingested payloads** | 3 | 4 of 4 | reader one DECOMPOSES (per-clock relative_references + sampled_body) and retires; metadata one -> `acquisition_metadata_file`; image one folds into the image model | `V_eta_ingested_payload_findings.md` |
| **sync configuration** | 2 | 2 of 2 | syncrule -> `clock_alignment_configuration` (parameters DECLARED, devices become edges); syncgraph -> `clock_alignment_policy` (earns existence on membership) | `V_eta_clock_alignment_cluster_plan.md` |
| **sync mapping** | 1 | 1 of 1 | -> `clock_alignment` (relation + `polynomial` data_type); endpoints are relative_reference docs; syncgraph_id restored, invented epochid removed | `V_eta_clock_alignment_cluster_plan.md` |
| **file navigation** | 1 | 1 of 1 | filenavigator -> `epoch_file_pattern` (id preserved; patterns PARSED not eval'd); `directory` was not a source and is now deleted | `V_eta_daq_family_decisions.md` |
| **openMINDS** | 1 | no target recorded | strain -> entity + recursive background_strain_#; strain_id on term_assertion | `V_eta_openminds_family_record.md` |
| **software** | 1 | 1 of 1 | app -> software entity + software_id edge + execution_environment (R1) | `V_eta_tenet_audit.md` |
| **frequency_filter** | 1 | 1 of 1 | referenced document (not entity); band edges; typed gain fields; no sample_rate | `V_eta_frequency_filter_model_plan.md` |
| **spike processing parameters** | 4 | 1 of 1 | 4 -> 1 `method_parameters` (id+name preserved); canonical parts typed, rest a bag | `V_eta_method_parameters_plan.md` |
| **stimulus parameters** | 2 | no target recorded | stimulus_parameter DISSOLVES to a typed leaf keyed by its CURIE (build gated on #32); stimulus_parameter_table PASSES THROUGH; both tombstones repaired | `V_eta_stimulus_parameter_plan.md` |
| **stimulus response** | 4 | 2 of 2 | 4 -> 2: `harmonic_component` data_type + calculation leaf (id preserved); parameters fold inline, killing 11,440 empty required edges | `V_eta_stimulus_response_model_plan.md` |
| **subject measurement** | 1 | no target recorded | route through the `measurement` fold -- no new class; `datestamp` is a TIME ANCHOR (-> absolute_reference), NOT a field (corrected 2026-08-06) | `V_eta_go_forward_class_audit.md` |
| **raw recording observation** | 2 | 12 of 12 | a raw continuous recording IS a typed `<modality>_observation` of the SPECIMEN: subject_id = the specimen, instrument_id = the electrode in the instrument role (T7), variable = the modality from the element type, body = `sampled_body`; the loose `probe observes specimen` relation RETIRES in favour of the instrument_id edge, and ONLY where that edge was actually written. Guard A stands (an unmapped element type still yields a VALUED observation over a self-describing sampled_body with a queryable `modality_unresolved` flag, never a timeseries_observation or `array`). Multi-channel is ONE observation with a channel axis, not N. Specimen granularity is accepted as faithful-but-coarse. OPEN, NOT COVERED BY THE SIGNATURE: `pyraview` emits this model's SHAPE while attributing it to the element rather than the specimen and writing no instrument_id | `V_eta_recording_observation_plan.md` |
| **subject** | 1 | no target recorded | PASSTHROUGH IS THE END STATE, not a deferral -- 1 -> 1, base.id PRESERVED (subject_id is the most-referenced edge in the corpus). The did_v1 template and V_eta declare the same two fields; the superclass moves base -> entity, `local_identifier` becomes REQUIRED, and `datestamp` -> `creation_timestamp` arrives via the OUTBOUND rename rather than this migrator. No fold is owed and none should be built | `V_eta_go_forward_class_audit.md` |
| **session** | 1 | no target recorded | `reference` -> `local_identifier`, REQUIRED, matching subject and epoch, with the now-duplicate optional slot dropped; type/date/purpose DELETED as V_zeta inventions (NDI's template declares `reference` and nothing else). THREE PARTS, ALL BUILT 2026-08-13: schema, the class's first migrator, and the two NDI reads by path -- which accept BOTH spellings rather than moving, because a database may be pre- or post-migration. NDI's WRITE stays did_v1 on purpose: it validates against NDI's own template, which still declares `reference` | `V_eta_go_forward_class_audit.md` |
| **misc singletons** | 3 | 2 of 2 | binaryseries_parameters -> subject_statement + sampled_body (the two axis mounts, by storage_mode); projectvar PASSES THROUGH (needs real docs); interaction_purpose is a target (#32) | `V_eta_go_forward_class_audit.md` |

## Class names the family table asserts that its sign-off does not say

DENOMINATOR: 26 signed families checked; every V_eta class name in the family one-liner above was matched against the text of the `TEAM-SIGN-OFF` line that signs that family. 10 family/name pair(s) are UNSIGNED -- the prose names the class, the signature does not.

**THIS IS NOT A LIST OF ERRORS, AND NOTHING HERE IS RESOLVED BY A TOOL.**
The family one-liner is Claude-authored prose in `tools/status_board.py`;
the sign-off is the team's own words. An unsigned name may be a fair
paraphrase, a structural word used in passing (`data_type`, `entity`), or
a target nobody agreed to -- and only a person can tell which.

It exists because on 2026-08-11 `ngrid` was filed as a dissolution,
"corrected" to a fold into `sampled_body`, and the correction was wrong.
Both readings came from `V_eta_image_model_plan.md`; neither reader
reached the `TEAM-SIGN-OFF [image / ngrid]` line in it, which says
"ngrid is DISSOLVED (deleted, not migrated)". Sweeping for the SHAPE
then found a second instance immediately -- `binaryseries_parameters`,
whose section heading says "folds into `sampled_body`" while its
signature routes the fields to a statement and an axis and names no
class.

**ONE OF THE TWO IS NOW SETTLED, AND THE OTHER IS NOT.** This
paragraph said "Both are recorded DISPUTED in the coverage ledger,
with both citations and no choice made", and half of that went stale
the day it was written. The team ruled on 2026-08-11 that for
`binaryseries_parameters` the SIGNATURE is what is intended, so its
ledger row now records TWO decided targets -- `subject_statement` and
`sampled_body`, the two mounts the axis entry can take, selected per
document by `storage_mode`. `ngrid` is UNCHANGED and still DISPUTED:
nothing was decided about it, and the two rows only ever shared a
shape. Note that the ruling does NOT make either name a signed one --
both still appear in the table below, because the signature says "the
statement's" and "the axis", never a class name. That is the honest
state: a decided target, derived from the signature, not quoted from
it.

| family | unsigned class name(s) in the one-liner | sign-off in |
|---|---|---|
| **image / ngrid** | `data_type`, `image_stack`, `sampled_body`, `subject` | `V_eta_image_model_plan.md` |
| **sync mapping** | `data_type` | `V_eta_clock_alignment_cluster_plan.md` |
| **openMINDS** | `entity` | `V_eta_openminds_family_record.md` |
| **software** | `entity` | `V_eta_tenet_audit.md` |
| **raw recording observation** | `pyraview` | `V_eta_recording_observation_plan.md` |
| **misc singletons** | `sampled_body`, `subject_statement` | `V_eta_go_forward_class_audit.md` |

**AND: 1 document(s) carry more than one UNTAGGED `TEAM-SIGN-OFF`
line.** An untagged line signs the document, and counts only when
exactly one family cites it -- so `find_signoff` returns the FIRST
one and the reader cannot tell which was shown. Not wrong; not
visible either.

- `V_eta_openminds_family_record.md` -- 2 untagged sign-off lines

## v1 source side (from the coverage ledger)

| disposition | count |
|---|---|
| retire | 48 |
| consumed by migrator (no tombstone) | 28 |
| in_progress | 19 |
| persist | 4 |
| test/demo fixture (non-production) | 2 |
| dissolved → subject | 1 |

### `retire`, but NO MIGRATOR YET -- 2 rows

Marked `retire` in the ledger with **no per-class migrator and no `how`
note**. `retire` reads as settled, so these do not appear in the family
counts above -- but they are open work. Several hold real data (e.g.
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

DENOMINATOR: 2 row(s), each searched for its BARE CLASS NAME as a quoted literal in 13 batch post-pass file(s) under `+did2/+convert` (comments stripped).

- `generic_file` -- **NOT untouched**: consumed by `foldGenericFiles.m`
- `imageCollection` -- no per-class migrator and no batch post-pass names it; passes through today

## Families naming classes that are no longer open

Settled or removed since the family was written -- prune from `FAMILIES`:

- `daqreader_ndr`
- `element`
- `element_epoch`
- `epochclocktimes`
- `hartley_calc`
- `imageStack_parameters`
- `jrclust_clusters`
- `openminds`
- `oridirtuning_calc`
- `probe_location`
- `pyraview`
- `session`
- `sorting_parameters`
- `spike_extraction_parameters`
- `spike_extraction_parameters_modification`
- `stimulus_parameter`
- `stimulus_parameter_table`
- `stimulus_response`
- `stimulus_response_scalar`
- `stimulus_response_scalar_parameters`
- `stimulus_response_scalar_parameters_basic`
- `subject`
- `subjectmeasurement`
- `treatment`
- `tuningcurve_calc`
- `valid_interval`
- `vmspikefilteringparameters`

