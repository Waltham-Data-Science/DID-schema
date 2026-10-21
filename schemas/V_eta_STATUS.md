# V_eta status board (GENERATED -- do not hand-edit)

Regenerate with `python3 tools/status_board.py`. CI runs `--check`.

State lives here. The plan documents under `schemas/` keep the RATIONALE
for each model; this board owns *how much is left and what exactly*.

**A class is DECIDED only when it cites a decision line that exists**: a
`TEAM-SIGN-OFF [tag]` line, or a `Decided by Jess Haley, <date>:` line, in
the document its citation names (`tools/decision_citations.py`). Anything
else is **Proposed (not decided)**, whatever any prose says.

## Where V_eta stands

| | count |
|---|---|
| target classes | 175 |
| settled (persist) | 91 |
| settled (retire) | 76 |
| **still open (`in_progress`)** | **8** |
| **`retire` with no migrator YET** | **3** |
| **open classes in all** | **11** |
| &nbsp;&nbsp;decided (cites a decision line), awaiting build | 11 |
| &nbsp;&nbsp;**proposed (not decided), awaiting review** | **0** |

| open-class BUILD/PROOF state (derived, see below) | count |
|---|---|
| (a) nothing built (the decision state is a separate column) | 2 |
| (b) built, awaiting corpus proof | 6 |
| (c) corpus: 0 survivors in the corpora read | 0 |
| (?) UNMEASURED -- no build evidence was ever taken | 0 |

## What is actually left on the 8 open classes

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
| build: migrator files inspected | 197 |
| build: &nbsp;&nbsp;-- of those, per-document migrator | 166 |
| build: &nbsp;&nbsp;-- of those, batch post-pass | 31 |
| build: V_zeta files DELIBERATELY EXCLUDED (`+migrators`, `+migrators_i`, `+migrators_e`) | 22 |
| build: migrator lines inspected | 48297 |
| build: &nbsp;&nbsp;-- of those, per-document migrator | 31889 |
| build: &nbsp;&nbsp;-- of those, batch post-pass | 16408 |
| build: classes queried | 8 |
| build: open classes MINTED as a document class | 1 |
| build: &nbsp;&nbsp;-- open classes minted in a per-document migrator (rows overlap) | 1 |
| build: &nbsp;&nbsp;-- open classes minted in a batch post-pass (rows overlap) | 0 |
| build: of those, discounted (decision retires the class) | 0 |
| build: `document_class` writes whose class name is a VARIABLE | 11 |
| build: &nbsp;&nbsp;-- of those, in a per-document migrator | 7 |
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

### Where the 8 open classes sit

| state | classes |
|---|---|
| (a) nothing built (the decision state is a separate column) | 2 |
| (b) built, awaiting corpus proof | 6 |
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
| 1 | `b.document_class = struct('class_name', '<class>', ...)` | 71 | 56 | 15 |
| 2 | `b.document_class = classBlock('<class>', {supers})` | 20 | 19 | 1 |
| 3 | `b.document_class.class_name = '<class>';` | 5 | 5 | 0 |
| - | class name is a VARIABLE -- unresolved here | 11 | 7 | 4 |

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
| `DID-matlab:convert/+entities/entityDoc.m:58` | `className` |
| `DID-matlab:convert/resolveEpochProbemap.m:646` | `entry.class` |
| `DID-matlab:convert/resolveLawnPlateSubjects.m:1333` | `leafClass` |
| `DID-matlab:convert/universalRenames.m:240` | `v2ClassName;` |
| `DID-matlab:migrators_j/dataset_remote.m:70` | `className` |
| `DID-matlab:migrators_j/ontology_table_row.m:248` | `leafClass` |
| `DID-matlab:migrators_j/ontology_table_row.m:783` | `className` |
| `DID-matlab:migrators_j/private/jCalculation.m:94` | `concreteClass` |
| `DID-matlab:migrators_j/private/jRecordingObservation.m:275` | `e.class` |
| `DID-matlab:migrators_j/private/jStartInteraction.m:36` | `className` |
| `DID-matlab:migrators_j/spatial_gene_expression_pyramid.m:130` | `CLASS;` |

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

| class | decision | state | build evidence | minted (M+B) | field writes (M+B) | named (M+B) | comments (M+B) | survivors |
|---|---|---|---|---|---|---|---|---|
| `acquisition_epoch` | decided | (b) | 6 consuming reference(s) (1 per-document migrator, 5 batch post-pass); minted as a document class at 1 site(s) (1 per-document migrator) | 1 (1+0) | 1 (1+0) | - | 46 (29+17) | n/a -- not measured |
| `app` | decided | (b) | 5 consuming reference(s) (2 per-document migrator, 3 batch post-pass); decided target(s) built: `software` | - | 2 (1+1) | 1 (0+1) | 187 (151+36) | n/a -- not measured |
| `binaryseries_parameters` | decided | (b) | migrator `DID-matlab:migrators_j/binaryseries_parameters.m`; decided target(s) built: `statement`, `sampled_body` | - | - | 1 (1+0) | 15 (15+0) | n/a -- not measured |
| `daqmetadatareader_epochdata_ingested` | decided | (b) | migrator `DID-matlab:migrators_j/daqmetadatareader_epochdata_ingested.m`; 2 consuming reference(s) (2 batch post-pass); decided target(s) built: `opaque_body` | - | - | 2 (0+2) | 18 (10+8) | n/a -- not measured |
| `ensemble` | decided | (b) | 1 consuming reference(s) (1 per-document migrator); decided target(s) built: `subject`, `directed_relation`, `sampled_body` | - | - | - | 25 (23+2) | n/a -- not measured |
| `interaction_purpose` | decided | (a) | *none* | - | - | - | 3 (3+0) | n/a -- not measured |
| `projectvar` | decided | (a) | *none* | - | - | - | 3 (3+0) | n/a -- not measured |
| `stimulus_presentation` | decided | (b) | migrator `DID-matlab:migrators_j/stimulus_presentation.m`; 6 consuming reference(s) (6 per-document migrator); decided target(s) built: `item`, `item_manipulation` | - | - | - | 41 (39+2) | n/a -- not measured |

#### (a) nothing built (the decision state is a separate column) -- 2

- `interaction_purpose` (decided) -- mentioned in 3 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/openminds_stimulus.m:49 (comment_mention)`, `DID-matlab:migrators_j/openminds_stimulus.m:50 (comment_mention)`, `DID-matlab:migrators_j/openminds_stimulus.m:70 (comment_mention)`
- `projectvar` (decided) -- mentioned in 3 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:360 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:378 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:38 (comment_mention)`

#### (b) built, awaiting corpus proof -- 6

- `acquisition_epoch` (decided) -- consumed at 1 site(s), per-document migrator: `NDI-matlab:ndi_second_pass/ensembleMembership.m:705 (guard)`; consumed at 5 site(s), batch post-pass: `DID-matlab:convert/epochMint.m:2550 (guard)`, `DID-matlab:convert/epochMint.m:2551 (field_read)`, `DID-matlab:convert/epochMint.m:2552 (field_read)`, `DID-matlab:convert/epochMint.m:2555 (field_read)`, `DID-matlab:convert/epochMint.m:803 (guard)`; MINTED as a document class at 1 site(s), per-document migrator: `DID-matlab:migrators_j/element_epoch.m:130 (emitted_class)`; a block of this name is WRITTEN at 1 site(s), per-document migrator: `DID-matlab:migrators_j/element_epoch.m:132 (field_write)`; mentioned in 29 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:665 (comment_mention)`, `DID-matlab:migrators_j/binaryseries_parameters.m:39 (comment_mention)`, `DID-matlab:migrators_j/daqreader_image_epochdata_ingested.m:168 (comment_mention)`, `DID-matlab:migrators_j/element_epoch.m:10 (comment_mention)`, `DID-matlab:migrators_j/element_epoch.m:100 (comment_mention)`, `DID-matlab:migrators_j/element_epoch.m:102 (comment_mention)` ...; mentioned in 17 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/epochMint.m:25 (comment_mention)`, `DID-matlab:convert/epochMint.m:2539 (comment_mention)`, `DID-matlab:convert/epochMint.m:2609 (comment_mention)`, `DID-matlab:convert/epochMint.m:27 (comment_mention)`, `DID-matlab:convert/epochMint.m:40 (comment_mention)`, `DID-matlab:convert/epochMint.m:442 (comment_mention)` ...
- `app` (decided) -- consumed at 2 site(s), per-document migrator: `DID-matlab:migrators_j/private/jSoftwareFromApp.m:124 (guard)`, `DID-matlab:migrators_j/private/jSoftwareFromApp.m:125 (field_read)`; consumed at 3 site(s), batch post-pass: `DID-matlab:convert/resolveValidIntervals.m:641 (guard)`, `DID-matlab:convert/universalRenames.m:285 (guard)`, `DID-matlab:convert/universalRenames.m:286 (field_read)`; a block of this name is WRITTEN at 1 site(s), per-document migrator: `DID-matlab:migrators_j/private/jMethodParameters.m:107 (field_write)`; a block of this name is WRITTEN at 1 site(s), batch post-pass: `DID-matlab:convert/universalRenames.m:287 (field_write)`; NAMED as a string value at 1 site(s), batch post-pass: `DID-matlab:convert/resolveValidIntervals.m:1094 (named)`; mentioned in 151 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:127 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:143 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:375 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:376 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:459 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:464 (comment_mention)` ...; mentioned in 36 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/calcCommon.m:25 (comment_mention)`, `DID-matlab:convert/calcCommon.m:28 (comment_mention)`, `DID-matlab:convert/resolveOpenmindsCitations.m:879 (comment_mention)`, `DID-matlab:convert/resolveValidIntervals.m:1065 (comment_mention)`, `DID-matlab:convert/resolveValidIntervals.m:1068 (comment_mention)`, `DID-matlab:convert/resolveValidIntervals.m:1069 (comment_mention)` ...; target(s) BUILT: `software`
- `binaryseries_parameters` (decided) -- migrator `DID-matlab:migrators_j/binaryseries_parameters.m`; NAMED as a string value at 1 site(s), per-document migrator: `DID-matlab:migrators_j/binaryseries_parameters.m:276 (named)`; mentioned in 15 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/+super/image_stack_parameters.m:94 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:308 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:537 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:538 (comment_mention)`, `DID-matlab:migrators_j/binaryseries_parameters.m:16 (comment_mention)`, `DID-matlab:migrators_j/binaryseries_parameters.m:189 (comment_mention)` ...; target(s) BUILT: `statement`, `sampled_body`
- `daqmetadatareader_epochdata_ingested` (decided) -- migrator `DID-matlab:migrators_j/daqmetadatareader_epochdata_ingested.m`; consumed at 2 site(s), batch post-pass: `DID-matlab:convert/epochMint.m:1049 (guard)`, `DID-matlab:convert/epochMint.m:1791 (field_read)`; NAMED as a string value at 2 site(s), batch post-pass: `DID-matlab:convert/epochMint.m:1080 (named)`, `DID-matlab:convert/epochMint.m:1790 (named)`; mentioned in 10 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:589 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader.m:20 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader.m:70 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader.m:77 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader_epochdata_ingested.m:21 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader_epochdata_ingested.m:25 (comment_mention)` ...; mentioned in 8 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/epochMint.m:1189 (comment_mention)`, `DID-matlab:convert/epochMint.m:211 (comment_mention)`, `DID-matlab:convert/epochMint.m:212 (comment_mention)`, `DID-matlab:convert/epochMint.m:24 (comment_mention)`, `DID-matlab:convert/epochMint.m:28 (comment_mention)`, `DID-matlab:convert/epochMint.m:287 (comment_mention)` ...; target(s) BUILT: `opaque_body`
- `ensemble` (decided) -- consumed at 1 site(s), per-document migrator: `NDI-matlab:ndi_second_pass/ensembleMembership.m:438 (guard)`; mentioned in 23 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/element_epoch.m:89 (comment_mention)`, `DID-matlab:migrators_j/element_epoch.m:91 (comment_mention)`, `DID-matlab:migrators_j/element_epoch.m:92 (comment_mention)`, `DID-matlab:migrators_j/hartley_calc.m:151 (comment_mention)`, `DID-matlab:migrators_j/private/jAcquisitionChannels.m:73 (comment_mention)`, `DID-matlab:migrators_j/private/jRecordingModality.m:240 (comment_mention)` ...; mentioned in 2 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/resolveLawnPlateSubjects.m:1358 (comment_mention)`, `DID-matlab:convert/resolveResponseParameters.m:71 (comment_mention)`; target(s) BUILT: `subject`, `directed_relation`, `sampled_body`
- `stimulus_presentation` (decided) -- migrator `DID-matlab:migrators_j/stimulus_presentation.m`; consumed at 6 site(s), per-document migrator: `NDI-matlab:ndi_second_pass/hartleyBasisGratings.m:354 (guard)`, `NDI-matlab:ndi_second_pass/hartleyBasisGratings.m:357 (field_read)`, `NDI-matlab:ndi_second_pass/stimulusPresentationToManipulation.m:47 (guard)`, `NDI-matlab:ndi_second_pass/stimulusPresentationToManipulation.m:48 (field_read)`, `NDI-matlab:ndi_second_pass/stimulusPresentationToTimedSequence.m:331 (guard)`, `NDI-matlab:ndi_second_pass/stimulusPresentationToTimedSequence.m:332 (field_read)`; mentioned in 39 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:909 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:910 (comment_mention)`, `DID-matlab:migrators_j/control_stimulus_ids.m:116 (comment_mention)`, `DID-matlab:migrators_j/control_stimulus_ids.m:32 (comment_mention)`, `DID-matlab:migrators_j/control_stimulus_ids.m:46 (comment_mention)`, `DID-matlab:migrators_j/control_stimulus_ids.m:74 (comment_mention)` ...; mentioned in 2 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/universalRenames.m:471 (comment_mention)`, `DID-matlab:convert/v1_to_v2.m:981 (comment_mention)`; target(s) BUILT: `item`, `item_manipulation`

## Proposed (not decided) -- awaiting review

DENOMINATOR: 11 open class(es); 0 cite no decision line that resolves.

None -- every open class cites a decision line that exists.

## Decided, awaiting build -- the open classes

DENOMINATOR: 11 open class(es); 11 cite a decision line that exists. The decision column is the line's own text, not a summary.

| class | targets built | decided in | decision |
|---|---|---|---|
| `acquisition_epoch` | no target recorded | `V_eta_epoch_plan.md`:884 `[epoch]` | jess@walthamdatascience.com / 2026-08-08, AMENDED 2026-08-10 -- MINT `epoch` as an entity (one per epoch id, local_identifier = the v1 epochid string, REQUIRED); acquisition_epoch dissolves and its clocks become relat... |
| `app` | 1 of 1 | `V_eta_tenet_audit.md`:16 `[software]` | jess, 2026-08-06 -- the `app` mixin is replaced by a `software` ENTITY (deduplicated by name+version) referenced from a statement by `software_id`, with the run-specific os / interpreter details in `execution_environm... |
| `binaryseries_parameters` | 2 of 2 | `V_eta_go_forward_class_audit.md`:9 `[misc singletons]` | jess, 2026-08-09 -- `binaryseries_parameters` folds into the data_body model and is retired (its `time_type` is the time axis's new `datum_type`, its `data_type` the statement's, `data_dim` the axis count, `samples_re... |
| `calculator` | no target recorded | `V_eta_subject_calculation_plan.md`:371 `[calculator mixin dropped (#73)]` | jess@walthamdatascience.com / 2026-09-29 -- (amends #67) the run environment is two `software` edges on `subject_calculation`, `interpreter_id` and `operating_system_id`; `runtime_environment` (and `execution_environm... |
| `daqmetadatareader_epochdata_ingested` | 1 of 1 | `V_eta_ingested_payload_findings.md`:276 `[daq ingested payloads]` | jess@walthamdatascience.com / 2026-08-08 -- ONE new class, `acquisition_metadata_file`; the reader and image classes RETIRE by decomposing into relative_reference + sampled_body + image_observation, all of which are n... |
| `ensemble` | 3 of 3 | `V_eta_ensemble_plan.md`:10 `[ensemble]` | jess, 2026-08-06 -- per-neuron spike times are the PRIMARY archival data (each neuron-subject, event times to a sampled_body); the ensemble is a GROUP SUBJECT with its id preserved and NO data body of its own, whose m... |
| `generic_file` | no target recorded | `V_eta_OPEN_WORK.md`:789 `[stranded sources]` | jess@walthamdatascience.com, 2026-08-11 -- generic_file folds to term_observation + opaque_body; imageCollection is a tombstone. Both are BUILT and ran in 6 of 6 corpora in run 31522068566. THIS SIGNATURE COVERS TWO C... |
| `imageCollection` | no target recorded | `V_eta_OPEN_WORK.md`:789 `[stranded sources]` | jess@walthamdatascience.com, 2026-08-11 -- generic_file folds to term_observation + opaque_body; imageCollection is a tombstone. Both are BUILT and ran in 6 of 6 corpora in run 31522068566. THIS SIGNATURE COVERS TWO C... |
| `interaction_purpose` | no target recorded | `V_eta_go_forward_class_audit.md`:9 `[misc singletons]` | jess, 2026-08-09 -- `binaryseries_parameters` folds into the data_body model and is retired (its `time_type` is the time axis's new `datum_type`, its `data_type` the statement's, `data_dim` the axis count, `samples_re... |
| `projectvar` | no target recorded | `V_eta_go_forward_class_audit.md`:9 `[misc singletons]` | jess, 2026-08-09 -- `binaryseries_parameters` folds into the data_body model and is retired (its `time_type` is the time axis's new `datum_type`, its `data_type` the statement's, `data_dim` the axis count, `samples_re... |
| `stimulus_presentation` | 2 of 2 | `V_eta_stimulus_model_plan.md`:258 `[stimulus]` | jess@walthamdatascience.com / 2026-08-08 -- `timed_sequence` (a data_type: deduped references to stimulus value documents + an index-array playlist) + `timed_sequence_manipulation` (the leaf); `control_stimulus_ids` -... |

## Every decision citation

DENOMINATOR: 71 class(es) cite 75 decision line(s); 0 citation(s) do not resolve. "targets built" counts the class's decided targets present in the built set (a target equal to the class is a passthrough and is not counted).

| class | disposition | targets built | decided in |
|---|---|---|---|
| `acquisition_epoch` | in_progress | no target recorded | `V_eta_epoch_plan.md`:884 `[epoch]` |
| `app` | in_progress | 1 of 1 | `V_eta_tenet_audit.md`:16 `[software]` |
| `binaryseries_parameters` | in_progress | 2 of 2 | `V_eta_go_forward_class_audit.md`:9 `[misc singletons]` |
| `calculator` | retire | no target recorded | `V_eta_subject_calculation_plan.md`:371 `[calculator mixin dropped (#73)]` |
| `cellTypeLabels` | retire | 4 of 4 | `V_eta_spatial_transcriptomics_plan.md`:565 `[spatial_transcriptomics_family]` |
| `control_stimulus_ids` | retire | 1 of 1 | `V_eta_spatial_transcriptomics_plan.md`:565 `[spatial_transcriptomics_family]` |
| `daqmetadatareader` | retire | 1 of 1 | `V_eta_daq_family_decisions.md`:479 `[daq configuration]` |
| `daqmetadatareader_epochdata_ingested` | in_progress | 1 of 1 | `V_eta_ingested_payload_findings.md`:276 `[daq ingested payloads]` |
| `daqreader` | retire | 1 of 1 | `V_eta_daq_family_decisions.md`:479 `[daq configuration]` |
| `daqreader_epochdata_ingested` | retire | 1 of 1 | `V_eta_ingested_payload_findings.md`:276 `[daq ingested payloads]` |
| `daqreader_image_epochdata_ingested` | retire | 3 of 3 | `V_eta_ingested_payload_findings.md`:276 `[daq ingested payloads]` |
| `daqreader_ndr` | consumed by migrator (no tombstone) | 3 of 3 | `V_eta_daq_family_decisions.md`:479 `[daq configuration]` |
| `daqsystem` | retire | 1 of 1 | `V_eta_daq_family_decisions.md`:479 `[daq configuration]` |
| `element` | retire | 10 of 10 | `V_eta_recording_observation_plan.md`:99 `[raw recording observation]` |
| `element_epoch` | consumed by migrator (no tombstone) | no target recorded | `V_eta_epoch_plan.md`:884 `[epoch]` |
| `ensemble` | in_progress | 3 of 3 | `V_eta_ensemble_plan.md`:10 `[ensemble]` |
| `epochclocktimes` | consumed by migrator (no tombstone) | 1 of 1 | `V_eta_time_reference_family_plan.md`:181 `[epochclocktimes]`; `V_eta_OPEN_WORK.md`:831 `[epoch extent -- row #113]` |
| `epochfiles_ingested` | retire | 1 of 1 | `V_eta_epoch_plan.md`:884 `[epoch]` |
| `epochid` | retire | no target recorded | `V_eta_epoch_plan.md`:884 `[epoch]` |
| `fileReference` | retire | 1 of 1 | `V_eta_spatial_transcriptomics_plan.md`:565 `[spatial_transcriptomics_family]` |
| `filenavigator` | retire | 1 of 1 | `V_eta_daq_family_decisions.md`:333 `[file navigation]` |
| `filter` | retire | 1 of 1 | `V_eta_frequency_filter_model_plan.md`:5 `[2026-07-30]` |
| `fitcurve` | retire | 1 of 1 | `V_eta_spatial_transcriptomics_plan.md`:565 `[spatial_transcriptomics_family]` |
| `geneExpression` | retire | no target recorded | `V_eta_spatial_transcriptomics_plan.md`:565 `[spatial_transcriptomics_family]` |
| `geneList` | retire | 4 of 4 | `V_eta_spatial_transcriptomics_plan.md`:565 `[spatial_transcriptomics_family]` |
| `geneListMapping` | retire | 3 of 3 | `V_eta_spatial_transcriptomics_plan.md`:565 `[spatial_transcriptomics_family]` |
| `generic_file` | retire | no target recorded | `V_eta_OPEN_WORK.md`:789 `[stranded sources]` |
| `hartley_calc` | retire | no target recorded | `V_eta_ngrid_family_findings.md`:358 `[receptive field fold]` |
| `image` | retire | 4 of 4 | `V_eta_spatial_transcriptomics_plan.md`:565 `[spatial_transcriptomics_family]` |
| `imageCollection` | retire | no target recorded | `V_eta_OPEN_WORK.md`:789 `[stranded sources]` |
| `imageStack` | retire | 4 of 4 | `V_eta_spatial_transcriptomics_plan.md`:565 `[spatial_transcriptomics_family]` |
| `imageStack_parameters` | retire | no target recorded | `V_eta_image_model_plan.md`:154 `[image / ngrid]` |
| `interaction_purpose` | in_progress | no target recorded | `V_eta_go_forward_class_audit.md`:9 `[misc singletons]` |
| `jrclust_clusters` | retire | 1 of 1 | `V_eta_go_forward_class_audit.md`:723 `[confirm sheet 2026-08-17]`; `V_eta_go_forward_class_audit.md`:871 `[spike-sorter output, amends the 2026-08-17 confirm sheet]` |
| `kiasort_clusters` | retire | 1 of 1 | `V_eta_go_forward_class_audit.md`:871 `[spike-sorter output, amends the 2026-08-17 confirm sheet]` |
| `kilosort_clusters` | retire | 1 of 1 | `V_eta_go_forward_class_audit.md`:871 `[spike-sorter output, amends the 2026-08-17 confirm sheet]` |
| `lightsheetZarrLevel` | retire | 1 of 1 | `review/73/OPEN_ITEMS.md`:317 `[lightsheet migrator points 1-11]` |
| `lightsheetZarrPyramid` | retire | 3 of 3 | `review/73/OPEN_ITEMS.md`:317 `[lightsheet migrator points 1-11]` |
| `neuron_extracellular` | retire | 7 of 7 | `V_eta_spatial_transcriptomics_plan.md`:565 `[spatial_transcriptomics_family]` |
| `ngrid` | retire | no target recorded | `V_eta_image_model_plan.md`:154 `[image / ngrid]` |
| `ontologyImage` | retire | 4 of 4 | `V_eta_spatial_transcriptomics_plan.md`:565 `[spatial_transcriptomics_family]` |
| `openminds` | retire | no target recorded | `V_eta_openminds_family_record.md`:10 `[2026-08-08]` |
| `oridirtuning_calc` | consumed by migrator (no tombstone) | 3 of 3 | `V_eta_go_forward_class_audit.md`:723 `[confirm sheet 2026-08-17]` |
| `probe_geometry` | retire | 3 of 3 | `V_eta_spatial_transcriptomics_plan.md`:565 `[spatial_transcriptomics_family]` |
| `probe_location` | retire | no target recorded | `V_eta_go_forward_class_audit.md`:723 `[confirm sheet 2026-08-17]` |
| `projectvar` | in_progress | no target recorded | `V_eta_go_forward_class_audit.md`:9 `[misc singletons]` |
| `pyraview` | retire | 1 of 1 | `V_eta_recording_observation_plan.md`:99 `[raw recording observation]`; `V_eta_recording_observation_plan.md`:111 `[pyraview levels, amends the 2026-08-13 pyraview pyramid confirmation]` |
| `session` | consumed by migrator (no tombstone) | no target recorded | `V_eta_go_forward_class_audit.md`:664 `[session]` |
| `sorting_parameters` | retire | 1 of 1 | `V_eta_method_parameters_plan.md`:32 `[spike processing parameters]` |
| `spatialGeneExpressionCells` | retire | 5 of 5 | `V_eta_spatial_transcriptomics_plan.md`:565 `[spatial_transcriptomics_family]` |
| `spatialGeneExpressionPyramid` | retire | 5 of 5 | `V_eta_spatial_transcriptomics_plan.md`:565 `[spatial_transcriptomics_family]` |
| `spatialGeneExpressionTiles` | retire | 1 of 1 | `V_eta_spatial_transcriptomics_plan.md`:565 `[spatial_transcriptomics_family]` |
| `spike_extraction_parameters` | retire | 1 of 1 | `V_eta_method_parameters_plan.md`:32 `[spike processing parameters]` |
| `spike_extraction_parameters_modification` | retire | 1 of 1 | `V_eta_method_parameters_plan.md`:32 `[spike processing parameters]` |
| `stimulus_parameter` | retire | no target recorded | `V_eta_stimulus_parameter_plan.md`:221 `[stimulus parameters]` |
| `stimulus_parameter_table` | retire | no target recorded | `V_eta_stimulus_parameter_plan.md`:221 `[stimulus parameters]` |
| `stimulus_presentation` | in_progress | 2 of 2 | `V_eta_stimulus_model_plan.md`:258 `[stimulus]` |
| `stimulus_response` | retire | no target recorded | `V_eta_stimulus_response_model_plan.md`:541 `[stimulus response]` |
| `stimulus_response_scalar` | retire | 1 of 1 | `V_eta_stimulus_response_model_plan.md`:541 `[stimulus response]` |
| `stimulus_response_scalar_parameters` | retire | no target recorded | `V_eta_stimulus_response_model_plan.md`:541 `[stimulus response]` |
| `stimulus_response_scalar_parameters_basic` | retire | 1 of 1 | `V_eta_stimulus_response_model_plan.md`:541 `[stimulus response]` |
| `subject` | consumed by migrator (no tombstone) | no target recorded | `V_eta_go_forward_class_audit.md`:697 `[subject]` |
| `subjectmeasurement` | retire | no target recorded | `V_eta_go_forward_class_audit.md`:336 `[subject measurement]` |
| `syncgraph` | retire | 1 of 1 | `V_eta_clock_alignment_cluster_plan.md`:506 `[sync configuration]` |
| `syncrule` | retire | 1 of 1 | `V_eta_clock_alignment_cluster_plan.md`:506 `[sync configuration]` |
| `syncrule_mapping` | retire | 1 of 1 | `V_eta_clock_alignment_cluster_plan.md`:508 `[sync mapping]` |
| `treatment` | consumed by migrator (no tombstone) | 7 of 7 | `V_eta_go_forward_class_audit.md`:723 `[confirm sheet 2026-08-17]` |
| `tuningcurve_calc` | consumed by migrator (no tombstone) | 3 of 3 | `V_eta_go_forward_class_audit.md`:723 `[confirm sheet 2026-08-17]` |
| `valid_interval` | retire | 1 of 1 | `V_eta_logical_observation_plan.md`:365 `[logical_observation]`; `V_eta_logical_observation_plan.md`:425 `[logical_observation amendment 1]` |
| `vmspikefilteringparameters` | retire | 1 of 1 | `V_eta_method_parameters_plan.md`:32 `[spike processing parameters]` |
| `vmspikefit` | retire | 1 of 1 | `V_eta_spatial_transcriptomics_plan.md`:567 `[#73 audit 2, D1-D13]` |

Every decided target these classes name is present in the built set, so
what remains for them is MIGRATOR work, not schema work.

## Decision lines no class cites

DENOMINATOR: 63 document(s) read (3 generated copies excluded); 123 decision line(s) accepted, 2 rejected; 38 cited by a class, 85 cited by none.

An uncited line is a decision the record holds that no class points at.
Most decide something that is not one class (a tenet, a naming rule, a
field). If one decides a class's disposition, that class should cite it.

- `V_eta_clock_alignment_cluster_plan.md`:638 `[sync configuration amendment 1]`
- `V_eta_data_body_model_plan.md`:673 `[data_body]`
- `V_eta_data_body_model_plan.md`:1281 `[data_body amendment 4]`
- `V_eta_data_body_model_plan.md`:1319 `[data_body amendment 3]`
- `V_eta_data_body_model_plan.md`:1337 (Decided by Jess Haley, 2026-10-21)
- `V_eta_data_body_model_plan.md`:1392 `[data_body amendment 5]`
- `V_eta_duplicate_entities_plan.md`:95 `[same_as]`
- `V_eta_ensemble_plan.md`:218 `[spike train leaf]`
- `V_eta_entity_composition_plan.md`:49 (TEAM-SIGN-OFF, 2026-10-08)
- `V_eta_entity_composition_plan.md`:61 (TEAM-SIGN-OFF, 2026-10-08)
- `V_eta_entity_composition_plan.md`:70 (TEAM-SIGN-OFF, 2026-10-08)
- `V_eta_entity_composition_plan.md`:116 (TEAM-SIGN-OFF, 2026-10-08)
- `V_eta_entity_composition_plan.md`:127 (TEAM-SIGN-OFF, 2026-10-08)
- `V_eta_entity_composition_plan.md`:148 (TEAM-SIGN-OFF, 2026-10-08)
- `V_eta_entity_composition_plan.md`:165 (TEAM-SIGN-OFF, 2026-10-08)
- `V_eta_entity_composition_plan.md`:176 (TEAM-SIGN-OFF, 2026-10-19)
- `V_eta_entity_composition_plan.md`:188 (TEAM-SIGN-OFF, 2026-10-08)
- `V_eta_entity_composition_plan.md`:195 (TEAM-SIGN-OFF, 2026-10-08)
- `V_eta_go_forward_class_audit.md`:228 `[dataseries_channel_map]`
- `V_eta_go_forward_class_audit.md`:725 `[confirm sheet 2026-08-22]`
- `V_eta_go_forward_class_audit.md`:727 (Decided by Jess Haley, 2026-10-21)
- `V_eta_go_forward_class_audit.md`:729 (Decided by Jess Haley, 2026-10-21)
- `V_eta_go_forward_class_audit.md`:753 (Decided by Jess Haley, 2026-10-21)
- `V_eta_go_forward_class_audit.md`:837 `[orientation_direction_tuning.json location]`
- `V_eta_go_forward_class_audit.md`:873 `[time anchors, amends the 2026-08-22 confirm sheet]`
- `V_eta_go_forward_class_audit.md`:875 `[dimensioned classes, batch confirmation]`
- `V_eta_linked_session_plan.md`:95 (TEAM-SIGN-OFF, 2026-10-09)
- `V_eta_method_parameters_plan.md`:862 `[parameter unit, #73 audit 2 D4]`
- `V_eta_method_plan.md`:188 `[method]`
- `V_eta_ngrid_family_findings.md`:381 `[receptive field naming]`
- `V_eta_openminds_family_record.md`:20 (TEAM-SIGN-OFF, 2026-08-05)
- `V_eta_openminds_family_record.md`:1329 (Decided by Jess Haley, 2026-10-21)
- `V_eta_openminds_family_record.md`:1333 (Decided by Jess Haley, 2026-10-21)
- `V_eta_prefix_spelling_plan.md`:202 `[prefix spelling]`
- `V_eta_recording_observation_plan.md`:115 (Decided by Jess Haley, 2026-10-21)
- `V_eta_relation_inheritance_plan.md`:113 `[relation inheritance]`
- `V_eta_source_unit_plan.md`:69 `[source unit]`
- `V_eta_source_unit_plan.md`:84 `[source unit amendment 1]`
- `V_eta_spatial_transcriptomics_plan.md`:595 `[formulation strain ingredient]`
- `V_eta_stimulus_model_plan.md`:304 `[stimulus -- visual_grating_manipulation reconciliation]`
- `V_eta_stimulus_model_plan.md`:372 `[onsets on the sequence, #73 audit 2 D11]`
- `V_eta_study_plan.md`:21 (TEAM-SIGN-OFF, 2026-09-30)
- `V_eta_study_plan.md`:28 (TEAM-SIGN-OFF, 2026-10-21)
- `V_eta_study_plan.md`:29 (TEAM-SIGN-OFF, 2026-09-30)
- `V_eta_study_plan.md`:30 (TEAM-SIGN-OFF, 2026-09-30)
- `V_eta_study_plan.md`:31 (TEAM-SIGN-OFF, 2026-09-30)
- `V_eta_study_plan.md`:40 (TEAM-SIGN-OFF, 2026-09-30)
- `V_eta_study_plan.md`:41 (TEAM-SIGN-OFF, 2026-09-30)
- `V_eta_study_plan.md`:50 (TEAM-SIGN-OFF, 2026-10-01)
- `V_eta_study_plan.md`:61 (TEAM-SIGN-OFF, 2026-10-02)
- `V_eta_study_plan.md`:110 (TEAM-SIGN-OFF, 2026-10-02)
- `V_eta_study_plan.md`:111 (TEAM-SIGN-OFF, 2026-10-02)
- `V_eta_study_plan.md`:142 (TEAM-SIGN-OFF, 2026-10-03)
- `V_eta_study_plan.md`:143 (TEAM-SIGN-OFF, 2026-10-03)
- `V_eta_study_plan.md`:171 (TEAM-SIGN-OFF, 2026-10-03)
- `V_eta_study_plan.md`:172 (TEAM-SIGN-OFF, 2026-10-03)
- `V_eta_study_plan.md`:189 (TEAM-SIGN-OFF, 2026-10-03)
- `V_eta_study_plan.md`:336 (TEAM-SIGN-OFF, 2026-10-04)
- `V_eta_study_plan.md`:337 (TEAM-SIGN-OFF, 2026-10-04)
- `V_eta_study_plan.md`:338 (TEAM-SIGN-OFF, 2026-10-04)
- `V_eta_study_plan.md`:339 (TEAM-SIGN-OFF, 2026-10-05)
- `V_eta_study_plan.md`:340 (TEAM-SIGN-OFF, 2026-10-05)
- `V_eta_study_plan.md`:341 (TEAM-SIGN-OFF, 2026-10-05)
- `V_eta_study_plan.md`:384 `[contributor role nodes]`
- `V_eta_subject_calculation_plan.md`:270 `[calculator + subject_calculation restructure]`
- `V_eta_subject_calculation_plan.md`:369 `[observation vs calculation, amends #67]`
- `V_eta_tenet_audit.md`:438 `[binding governance]`
- `V_eta_tenet_audit.md`:521 `[date dtype]`
- `V_eta_tenet_audit.md`:525 `[base naming]`
- `V_eta_tenet_audit.md`:529 `[time dtype]`
- `V_eta_tenets.md`:996 `[tenet amendments 2026-10-20]`
- `V_eta_tenets.md`:998 `[tenet amendments 2026-10-21]`
- `V_eta_tenets.md`:999 `[tenet T20, group entities]`
- `V_eta_term_registry_plan.md`:31 `[term registry]`
- `V_eta_term_registry_plan.md`:151 `[term registry closed value sets]`
- `V_eta_time_reference_model_plan.md`:468 `[time_reference]`
- `V_eta_time_reference_model_plan.md`:735 `[time_reference uniqueness rule]`
- `V_eta_time_reference_model_plan.md`:762 `[epoch and session wall-clock time]`
- `V_eta_time_reference_model_plan.md`:797 `[time_reference end]`
- `V_eta_time_reference_model_plan.md`:840 `[time_reference tolerance]`
- `V_eta_time_reference_model_plan.md`:861 `[time_reference tolerance amendment 1]`
- `V_eta_tuning_model_plan.md`:144 `[tuning_curve composite + tuning_curve_calculation leaf, restructure]`
- `V_eta_tuning_model_plan.md`:246 `[tuning shape, #73 audit 2 amendment]`
- `review/73/OPEN_ITEMS.md`:349 `[lightsheet reader questions R1-R6]`
- `review/73/OPEN_ITEMS.md`:362 `[developed_by, hosted_by, distributed_as]`

## v1 source side (from the coverage ledger)

| disposition | count |
|---|---|
| retire | 73 |
| consumed by migrator (no tombstone) | 30 |
| in_progress | 6 |
| test/demo fixture (non-production) | 2 |
| UNMAPPED (needs a V_eta home) | 2 |
| dissolved → subject | 1 |
| persist | 1 |

### `retire`, but NO MIGRATOR YET -- 3 rows

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

DENOMINATOR: 3 row(s), each searched for its BARE CLASS NAME as a quoted literal in 16 batch post-pass file(s) under `+did2/+convert` (comments stripped).

- `calculator` -- no per-class migrator and no batch post-pass names it; passes through today
- `generic_file` -- **NOT untouched**: consumed by `foldGenericFiles.m`
- `imageCollection` -- no per-class migrator and no batch post-pass names it; passes through today

