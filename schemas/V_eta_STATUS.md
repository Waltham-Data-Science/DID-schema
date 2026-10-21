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
| build: migrator files inspected | 211 |
| build: &nbsp;&nbsp;-- of those, per-document migrator | 177 |
| build: &nbsp;&nbsp;-- of those, batch post-pass | 34 |
| build: V_zeta files DELIBERATELY EXCLUDED (`+migrators`, `+migrators_i`, `+migrators_e`) | 22 |
| build: migrator lines inspected | 49213 |
| build: &nbsp;&nbsp;-- of those, per-document migrator | 31059 |
| build: &nbsp;&nbsp;-- of those, batch post-pass | 18154 |
| build: classes queried | 8 |
| build: open classes MINTED as a document class | 1 |
| build: &nbsp;&nbsp;-- open classes minted in a per-document migrator (rows overlap) | 1 |
| build: &nbsp;&nbsp;-- open classes minted in a batch post-pass (rows overlap) | 0 |
| build: of those, discounted (decision retires the class) | 0 |
| build: `document_class` writes whose class name is a VARIABLE | 8 |
| build: &nbsp;&nbsp;-- of those, in a per-document migrator | 5 |
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
| 1 | `b.document_class = struct('class_name', '<class>', ...)` | 21 | 18 | 3 |
| 2 | `b.document_class = classBlock('<class>', {supers})` | 4 | 4 | 0 |
| 3 | `b.document_class.class_name = '<class>';` | 5 | 5 | 0 |
| 4 | *unrecognised* | 60 | 32 | 28 |
| 5 | *unrecognised* | 45 | 45 | 0 |
| - | class name is a VARIABLE -- unresolved here | 8 | 5 | 3 |

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
| `DID-matlab:convert/resolveEpochProbemap.m:1045` | `entry.class` |
| `DID-matlab:convert/resolveLawnPlateSubjects.m:1017` | `entry{1}` |
| `DID-matlab:convert/universalRenames.m:240` | `v2ClassName;` |
| `DID-matlab:migrators_j/ontology_table_row.m:233` | `measures{i, 2}` |
| `DID-matlab:migrators_j/ontology_table_row.m:379` | `measures{i, 2}` |
| `DID-matlab:migrators_j/ontology_table_row.m:650` | `observation + shapeClass` |
| `DID-matlab:migrators_j/private/jMeasurementFold.m:78` | `observation + leaf` |
| `DID-matlab:migrators_j/treatment.m:100` | `manipulation + kind` |

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
| `acquisition_epoch` | decided | (b) | 7 consuming reference(s) (1 per-document migrator, 6 batch post-pass); minted as a document class at 1 site(s) (1 per-document migrator) | 1 (1+0) | 1 (1+0) | - | 51 (28+23) | n/a -- not measured |
| `app` | decided | (b) | 5 consuming reference(s) (2 per-document migrator, 3 batch post-pass); decided target(s) built: `entity (software)` | - | 2 (1+1) | 1 (0+1) | 168 (132+36) | n/a -- not measured |
| `binaryseries_parameters` | decided | (b) | migrator `DID-matlab:migrators_j/binaryseries_parameters.m`; decided target(s) built: `statement`, `sampled_body` | - | - | 1 (1+0) | 15 (15+0) | n/a -- not measured |
| `daqmetadatareader_epochdata_ingested` | decided | (b) | migrator `DID-matlab:migrators_j/daqmetadatareader_epochdata_ingested.m`; 2 consuming reference(s) (2 batch post-pass); decided target(s) built: `opaque_body` | - | - | 2 (0+2) | 17 (9+8) | n/a -- not measured |
| `ensemble` | decided | (b) | 1 consuming reference(s) (1 per-document migrator); decided target(s) built: `entity (subject)`, `directed_relation`, `sampled_body` | - | - | 1 (1+0) | 25 (24+1) | n/a -- not measured |
| `interaction_purpose` | decided | (a) | *none* | - | - | - | 3 (3+0) | n/a -- not measured |
| `projectvar` | decided | (a) | *none* | - | - | - | 3 (3+0) | n/a -- not measured |
| `stimulus_presentation` | decided | (b) | migrator `DID-matlab:migrators_j/stimulus_presentation.m`; 6 consuming reference(s) (6 per-document migrator); decided target(s) built: `item`, `manipulation + item` | - | - | - | 41 (39+2) | n/a -- not measured |

#### (a) nothing built (the decision state is a separate column) -- 2

- `interaction_purpose` (decided) -- mentioned in 3 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/openminds_stimulus.m:49 (comment_mention)`, `DID-matlab:migrators_j/openminds_stimulus.m:50 (comment_mention)`, `DID-matlab:migrators_j/openminds_stimulus.m:70 (comment_mention)`
- `projectvar` (decided) -- mentioned in 3 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:360 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:378 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:38 (comment_mention)`

#### (b) built, awaiting corpus proof -- 6

- `acquisition_epoch` (decided) -- consumed at 1 site(s), per-document migrator: `NDI-matlab:ndi_second_pass/ensembleMembership.m:705 (guard)`; consumed at 6 site(s), batch post-pass: `DID-matlab:convert/epochMint.m:2908 (guard)`, `DID-matlab:convert/epochMint.m:2909 (field_read)`, `DID-matlab:convert/epochMint.m:2910 (field_read)`, `DID-matlab:convert/epochMint.m:2913 (field_read)`, `DID-matlab:convert/epochMint.m:829 (guard)`, `DID-matlab:convert/resolveEpochProbemap.m:332 (guard)`; MINTED as a document class at 1 site(s), per-document migrator: `DID-matlab:migrators_j/element_epoch.m:130 (emitted_class)`; a block of this name is WRITTEN at 1 site(s), per-document migrator: `DID-matlab:migrators_j/element_epoch.m:132 (field_write)`; mentioned in 28 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:667 (comment_mention)`, `DID-matlab:migrators_j/binaryseries_parameters.m:39 (comment_mention)`, `DID-matlab:migrators_j/daqreader_image_epochdata_ingested.m:168 (comment_mention)`, `DID-matlab:migrators_j/element_epoch.m:10 (comment_mention)`, `DID-matlab:migrators_j/element_epoch.m:100 (comment_mention)`, `DID-matlab:migrators_j/element_epoch.m:102 (comment_mention)` ...; mentioned in 23 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/epochMint.m:25 (comment_mention)`, `DID-matlab:convert/epochMint.m:27 (comment_mention)`, `DID-matlab:convert/epochMint.m:2897 (comment_mention)`, `DID-matlab:convert/epochMint.m:2967 (comment_mention)`, `DID-matlab:convert/epochMint.m:40 (comment_mention)`, `DID-matlab:convert/epochMint.m:453 (comment_mention)` ...
- `app` (decided) -- consumed at 2 site(s), per-document migrator: `DID-matlab:migrators_j/private/jSoftwareFromApp.m:124 (guard)`, `DID-matlab:migrators_j/private/jSoftwareFromApp.m:125 (field_read)`; consumed at 3 site(s), batch post-pass: `DID-matlab:convert/resolveValidIntervals.m:663 (guard)`, `DID-matlab:convert/universalRenames.m:285 (guard)`, `DID-matlab:convert/universalRenames.m:286 (field_read)`; a block of this name is WRITTEN at 1 site(s), per-document migrator: `DID-matlab:migrators_j/private/jMethodParameters.m:105 (field_write)`; a block of this name is WRITTEN at 1 site(s), batch post-pass: `DID-matlab:convert/universalRenames.m:287 (field_write)`; NAMED as a string value at 1 site(s), batch post-pass: `DID-matlab:convert/resolveValidIntervals.m:1119 (named)`; mentioned in 132 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:127 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:143 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:375 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:376 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:459 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:464 (comment_mention)` ...; mentioned in 36 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/calcCommon.m:25 (comment_mention)`, `DID-matlab:convert/calcCommon.m:28 (comment_mention)`, `DID-matlab:convert/resolveOpenmindsCitations.m:886 (comment_mention)`, `DID-matlab:convert/resolveValidIntervals.m:1090 (comment_mention)`, `DID-matlab:convert/resolveValidIntervals.m:1093 (comment_mention)`, `DID-matlab:convert/resolveValidIntervals.m:1094 (comment_mention)` ...; target(s) BUILT: `entity (software)`
- `binaryseries_parameters` (decided) -- migrator `DID-matlab:migrators_j/binaryseries_parameters.m`; NAMED as a string value at 1 site(s), per-document migrator: `DID-matlab:migrators_j/binaryseries_parameters.m:276 (named)`; mentioned in 15 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/+super/image_stack_parameters.m:94 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:308 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:537 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:538 (comment_mention)`, `DID-matlab:migrators_j/binaryseries_parameters.m:16 (comment_mention)`, `DID-matlab:migrators_j/binaryseries_parameters.m:189 (comment_mention)` ...; target(s) BUILT: `statement`, `sampled_body`
- `daqmetadatareader_epochdata_ingested` (decided) -- migrator `DID-matlab:migrators_j/daqmetadatareader_epochdata_ingested.m`; consumed at 2 site(s), batch post-pass: `DID-matlab:convert/epochMint.m:1096 (guard)`, `DID-matlab:convert/epochMint.m:2041 (field_read)`; NAMED as a string value at 2 site(s), batch post-pass: `DID-matlab:convert/epochMint.m:1127 (named)`, `DID-matlab:convert/epochMint.m:2040 (named)`; mentioned in 9 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:591 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader.m:20 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader.m:70 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader.m:77 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader_epochdata_ingested.m:21 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader_epochdata_ingested.m:25 (comment_mention)` ...; mentioned in 8 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/epochMint.m:1027 (comment_mention)`, `DID-matlab:convert/epochMint.m:1033 (comment_mention)`, `DID-matlab:convert/epochMint.m:1237 (comment_mention)`, `DID-matlab:convert/epochMint.m:215 (comment_mention)`, `DID-matlab:convert/epochMint.m:216 (comment_mention)`, `DID-matlab:convert/epochMint.m:24 (comment_mention)` ...; target(s) BUILT: `opaque_body`
- `ensemble` (decided) -- consumed at 1 site(s), per-document migrator: `NDI-matlab:ndi_second_pass/ensembleMembership.m:438 (guard)`; NAMED as a string value at 1 site(s), per-document migrator: `DID-matlab:migrators_j/element.m:215 (named)`; mentioned in 24 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/element.m:101 (comment_mention)`, `DID-matlab:migrators_j/element.m:210 (comment_mention)`, `DID-matlab:migrators_j/element_epoch.m:89 (comment_mention)`, `DID-matlab:migrators_j/element_epoch.m:91 (comment_mention)`, `DID-matlab:migrators_j/element_epoch.m:92 (comment_mention)`, `DID-matlab:migrators_j/hartley_calc.m:155 (comment_mention)` ...; mentioned in 1 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/resolveResponseParameters.m:71 (comment_mention)`; target(s) BUILT: `entity (subject)`, `directed_relation`, `sampled_body`
- `stimulus_presentation` (decided) -- migrator `DID-matlab:migrators_j/stimulus_presentation.m`; consumed at 6 site(s), per-document migrator: `NDI-matlab:ndi_second_pass/hartleyBasisGratings.m:354 (guard)`, `NDI-matlab:ndi_second_pass/hartleyBasisGratings.m:357 (field_read)`, `NDI-matlab:ndi_second_pass/stimulusPresentationToManipulation.m:47 (guard)`, `NDI-matlab:ndi_second_pass/stimulusPresentationToManipulation.m:48 (field_read)`, `NDI-matlab:ndi_second_pass/stimulusPresentationToTimedSequence.m:331 (guard)`, `NDI-matlab:ndi_second_pass/stimulusPresentationToTimedSequence.m:332 (field_read)`; mentioned in 39 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:913 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:914 (comment_mention)`, `DID-matlab:migrators_j/control_stimulus_ids.m:104 (comment_mention)`, `DID-matlab:migrators_j/control_stimulus_ids.m:32 (comment_mention)`, `DID-matlab:migrators_j/control_stimulus_ids.m:46 (comment_mention)`, `DID-matlab:migrators_j/control_stimulus_ids.m:74 (comment_mention)` ...; mentioned in 2 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/universalRenames.m:471 (comment_mention)`, `DID-matlab:convert/v1_to_v2.m:1029 (comment_mention)`; target(s) BUILT: `item`, `manipulation + item`

## Proposed (not decided) -- awaiting review

DENOMINATOR: 11 open class(es); 0 cite no decision line that resolves.

None -- every open class cites a decision line that exists.

## Decided, awaiting build -- the open classes

DENOMINATOR: 11 open class(es); 11 cite a decision line that exists. The decision column is the line's own text, not a summary.

| class | targets built | decided in | decision |
|---|---|---|---|
| `acquisition_epoch` | no target recorded | [epoch]. "TEAM-SIGN-OFF [epoch]: jess@walthamdatascience.com /" (V_eta_epoch_plan.md:884). | jess@walthamdatascience.com / 2026-08-08, AMENDED 2026-08-10 -- MINT `epoch` as an entity (one per epoch id, local_identifier = the v1 epochid string, REQUIRED); acquisition_epoch dissolves and its clocks become relat... |
| `app` | 1 of 1 | [software]. "TEAM-SIGN-OFF [software]: jess, 2026-08-06 -- the" (V_eta_tenet_audit.md:16). | jess, 2026-08-06 -- the `app` mixin is replaced by a `software` ENTITY (deduplicated by name+version) referenced from a statement by `software_id`, with the run-specific os / interpreter details in `execution_environm...` |
| `binaryseries_parameters` | 2 of 2 | [misc singletons]. "TEAM-SIGN-OFF [misc singletons]: jess, 2026-08-09" (V_eta_go_forward_class_audit.md:9). | jess, 2026-08-09 -- `binaryseries_parameters` folds into the data_body model and is retired (its `time_type` is the time axis's new `datum_type`, its `data_type` the statement's, `data_dim` the axis count, `samples_re...` |
| `calculator` | no target recorded | [calculator mixin dropped (#73)]. "TEAM-SIGN-OFF [calculator mixin dropped (#73)]" (V_eta_subject_calculation_plan.md:371). | jess@walthamdatascience.com / 2026-09-29 -- (amends #67) the run environment is two `software` edges on `subject_calculation`, `interpreter_id` and `operating_system_id`; `runtime_environment` (and `execution_environm...` |
| `daqmetadatareader_epochdata_ingested` | 1 of 1 | [daq ingested payloads]. "TEAM-SIGN-OFF [daq ingested payloads]" (V_eta_ingested_payload_findings.md:276). | jess@walthamdatascience.com / 2026-08-08 -- ONE new class, `acquisition_metadata_file`; the reader and image classes RETIRE by decomposing into relative_reference + sampled_body + image_observation, all of which are n... |
| `ensemble` | 3 of 3 | [ensemble]. "TEAM-SIGN-OFF [ensemble]: jess, 2026-08-06 -- per-neuron" (V_eta_ensemble_plan.md:10). | jess, 2026-08-06 -- per-neuron spike times are the PRIMARY archival data (each neuron-subject, event times to a sampled_body); the ensemble is a GROUP SUBJECT with its id preserved and NO data body of its own, whose m... |
| `generic_file` | no target recorded | [stranded sources]. "TEAM-SIGN-OFF [stranded sources]" (V_eta_OPEN_WORK.md:789). | jess@walthamdatascience.com, 2026-08-11 -- generic_file folds to term_observation + opaque_body; imageCollection is a tombstone. Both are BUILT and ran in 6 of 6 corpora in run 31522068566. THIS SIGNATURE COVERS TWO C... |
| `imageCollection` | no target recorded | [stranded sources]. "TEAM-SIGN-OFF [stranded sources]" (V_eta_OPEN_WORK.md:789). | jess@walthamdatascience.com, 2026-08-11 -- generic_file folds to term_observation + opaque_body; imageCollection is a tombstone. Both are BUILT and ran in 6 of 6 corpora in run 31522068566. THIS SIGNATURE COVERS TWO C... |
| `interaction_purpose` | no target recorded | [misc singletons]. "TEAM-SIGN-OFF [misc singletons]: jess, 2026-08-09" (V_eta_go_forward_class_audit.md:9). | jess, 2026-08-09 -- `binaryseries_parameters` folds into the data_body model and is retired (its `time_type` is the time axis's new `datum_type`, its `data_type` the statement's, `data_dim` the axis count, `samples_re...` |
| `projectvar` | no target recorded | [misc singletons]. "TEAM-SIGN-OFF [misc singletons]: jess, 2026-08-09" (V_eta_go_forward_class_audit.md:9). | jess, 2026-08-09 -- `binaryseries_parameters` folds into the data_body model and is retired (its `time_type` is the time axis's new `datum_type`, its `data_type` the statement's, `data_dim` the axis count, `samples_re...` |
| `stimulus_presentation` | 2 of 2 | [stimulus]. "TEAM-SIGN-OFF [stimulus]: jess@walthamdatascience.com /" (V_eta_stimulus_model_plan.md:258). | jess@walthamdatascience.com / 2026-08-08 -- `timed_sequence` (a data_type: deduped references to stimulus value documents + an index-array playlist) + `timed_sequence_manipulation` (the leaf); `control_stimulus_ids` -... |

## Every decision citation

DENOMINATOR: 73 class(es) cite 81 decision line(s); 0 citation(s) do not resolve. "targets built" counts the class's decided targets present in the built set (a target equal to the class is a passthrough and is not counted).

| class | disposition | targets built | decided in |
|---|---|---|---|
| `acquisition_epoch` | in_progress | no target recorded | [epoch]. "TEAM-SIGN-OFF [epoch]: jess@walthamdatascience.com /" (V_eta_epoch_plan.md:884). |
| `app` | in_progress | 1 of 1 | [software]. "TEAM-SIGN-OFF [software]: jess, 2026-08-06 -- the" (V_eta_tenet_audit.md:16). |
| `binaryseries_parameters` | in_progress | 2 of 2 | [misc singletons]. "TEAM-SIGN-OFF [misc singletons]: jess, 2026-08-09" (V_eta_go_forward_class_audit.md:9). |
| `calculator` | retire | no target recorded | [calculator mixin dropped (#73)]. "TEAM-SIGN-OFF [calculator mixin dropped (#73)]" (V_eta_subject_calculation_plan.md:371). |
| `cellTypeLabels` | retire | 4 of 4 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (V_eta_spatial_transcriptomics_plan.md:572). |
| `control_stimulus_ids` | retire | 1 of 1 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (V_eta_spatial_transcriptomics_plan.md:572). |
| `daqmetadatareader` | retire | 1 of 1 | [daq configuration]. "TEAM-SIGN-OFF [daq configuration]" (V_eta_daq_family_decisions.md:479). |
| `daqmetadatareader_epochdata_ingested` | in_progress | 1 of 1 | [daq ingested payloads]. "TEAM-SIGN-OFF [daq ingested payloads]" (V_eta_ingested_payload_findings.md:276). |
| `daqreader` | retire | 1 of 1 | [daq configuration]. "TEAM-SIGN-OFF [daq configuration]" (V_eta_daq_family_decisions.md:479). |
| `daqreader_epochdata_ingested` | retire | 1 of 1 | [daq ingested payloads]. "TEAM-SIGN-OFF [daq ingested payloads]" (V_eta_ingested_payload_findings.md:276).; [epoch files as data bodies]. "Decided by Jess Haley, 2026-10-21 [epoch files as data" (V_eta_recording_observation_plan.md:115). |
| `daqreader_image_epochdata_ingested` | retire | 3 of 3 | [daq ingested payloads]. "TEAM-SIGN-OFF [daq ingested payloads]" (V_eta_ingested_payload_findings.md:276).; [epoch files as data bodies]. "Decided by Jess Haley, 2026-10-21 [epoch files as data" (V_eta_recording_observation_plan.md:115). |
| `daqreader_mfdaq_epochdata_ingested` | consumed by migrator (no tombstone) | no target recorded | [epoch files as data bodies]. "Decided by Jess Haley, 2026-10-21 [epoch files as data" (V_eta_recording_observation_plan.md:115). |
| `daqreader_ndr` | consumed by migrator (no tombstone) | 3 of 3 | [daq configuration]. "TEAM-SIGN-OFF [daq configuration]" (V_eta_daq_family_decisions.md:479). |
| `daqsystem` | retire | 1 of 1 | [daq configuration]. "TEAM-SIGN-OFF [daq configuration]" (V_eta_daq_family_decisions.md:479). |
| `element` | retire | 10 of 10 | [raw recording observation]. "TEAM-SIGN-OFF [raw recording observation]" (V_eta_recording_observation_plan.md:99).; [epoch files as data bodies]. "Decided by Jess Haley, 2026-10-21 [epoch files as data" (V_eta_recording_observation_plan.md:115). |
| `element_epoch` | consumed by migrator (no tombstone) | no target recorded | [epoch]. "TEAM-SIGN-OFF [epoch]: jess@walthamdatascience.com /" (V_eta_epoch_plan.md:884). |
| `ensemble` | in_progress | 3 of 3 | [ensemble]. "TEAM-SIGN-OFF [ensemble]: jess, 2026-08-06 -- per-neuron" (V_eta_ensemble_plan.md:10). |
| `epochclocktimes` | consumed by migrator (no tombstone) | 1 of 1 | [epochclocktimes]. "TEAM-SIGN-OFF [epochclocktimes]" (V_eta_time_reference_family_plan.md:181).; [epoch extent -- row #113]. "TEAM-SIGN-OFF [epoch extent -- row #113]" (V_eta_OPEN_WORK.md:831). |
| `epochfiles_ingested` | retire | 1 of 1 | [epoch]. "TEAM-SIGN-OFF [epoch]: jess@walthamdatascience.com /" (V_eta_epoch_plan.md:884).; [epoch files as data bodies]. "Decided by Jess Haley, 2026-10-21 [epoch files as data" (V_eta_recording_observation_plan.md:115). |
| `epochid` | retire | no target recorded | [epoch]. "TEAM-SIGN-OFF [epoch]: jess@walthamdatascience.com /" (V_eta_epoch_plan.md:884). |
| `fileReference` | retire | 1 of 1 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (V_eta_spatial_transcriptomics_plan.md:572). |
| `filenavigator` | retire | 1 of 1 | [file navigation]. "TEAM-SIGN-OFF [file navigation]: jess, 2026-08-06" (V_eta_daq_family_decisions.md:333). |
| `filter` | retire | 1 of 1 | [2026-07-30]. "TEAM-SIGN-OFF: jess, 2026-07-30" (V_eta_frequency_filter_model_plan.md:5). |
| `fitcurve` | retire | 1 of 1 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (V_eta_spatial_transcriptomics_plan.md:572). |
| `geneExpression` | retire | no target recorded | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (V_eta_spatial_transcriptomics_plan.md:572). |
| `geneList` | retire | 4 of 4 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (V_eta_spatial_transcriptomics_plan.md:572). |
| `geneListMapping` | retire | 3 of 3 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (V_eta_spatial_transcriptomics_plan.md:572). |
| `generic_file` | retire | no target recorded | [stranded sources]. "TEAM-SIGN-OFF [stranded sources]" (V_eta_OPEN_WORK.md:789). |
| `hartley_calc` | retire | no target recorded | [receptive field fold]. "TEAM-SIGN-OFF [receptive field fold]" (V_eta_ngrid_family_findings.md:358). |
| `image` | retire | 4 of 4 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (V_eta_spatial_transcriptomics_plan.md:572). |
| `imageCollection` | retire | no target recorded | [stranded sources]. "TEAM-SIGN-OFF [stranded sources]" (V_eta_OPEN_WORK.md:789). |
| `imageStack` | retire | 4 of 4 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (V_eta_spatial_transcriptomics_plan.md:572). |
| `imageStack_parameters` | retire | no target recorded | [image / ngrid]. "TEAM-SIGN-OFF [image / ngrid]: jess@walthamdatascience.com" (V_eta_image_model_plan.md:154). |
| `interaction_purpose` | in_progress | no target recorded | [misc singletons]. "TEAM-SIGN-OFF [misc singletons]: jess, 2026-08-09" (V_eta_go_forward_class_audit.md:9). |
| `jrclust_clusters` | retire | 1 of 1 | [confirm sheet 2026-08-17]. "TEAM-SIGN-OFF [confirm sheet 2026-08-17]" (V_eta_go_forward_class_audit.md:723).; [spike-sorter output, amends the 2026-08-17 confirm sheet]. "TEAM-SIGN-OFF [spike-sorter output, amends the 2026-08-17" (V_eta_go_forward_class_audit.md:1023). |
| `kiasort_clusters` | retire | 1 of 1 | [spike-sorter output, amends the 2026-08-17 confirm sheet]. "TEAM-SIGN-OFF [spike-sorter output, amends the 2026-08-17" (V_eta_go_forward_class_audit.md:1023). |
| `kilosort_clusters` | retire | 1 of 1 | [spike-sorter output, amends the 2026-08-17 confirm sheet]. "TEAM-SIGN-OFF [spike-sorter output, amends the 2026-08-17" (V_eta_go_forward_class_audit.md:1023). |
| `lightsheetZarrLevel` | retire | 1 of 1 | [lightsheet migrator points 1-11]. "TEAM-SIGN-OFF [lightsheet migrator points 1-11]" (review/73/OPEN_ITEMS.md:317). |
| `lightsheetZarrPyramid` | retire | 3 of 3 | [lightsheet migrator points 1-11]. "TEAM-SIGN-OFF [lightsheet migrator points 1-11]" (review/73/OPEN_ITEMS.md:317). |
| `neuron_extracellular` | retire | 7 of 7 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (V_eta_spatial_transcriptomics_plan.md:572). |
| `ngrid` | retire | no target recorded | [image / ngrid]. "TEAM-SIGN-OFF [image / ngrid]: jess@walthamdatascience.com" (V_eta_image_model_plan.md:154). |
| `ontologyImage` | retire | 4 of 4 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (V_eta_spatial_transcriptomics_plan.md:572). |
| `openminds` | retire | no target recorded | [2026-08-08]. "TEAM-SIGN-OFF: jess, 2026-08-08 -- Part 7: the 3 unattached" (V_eta_openminds_family_record.md:10). |
| `oridirtuning_calc` | consumed by migrator (no tombstone) | 3 of 3 | [confirm sheet 2026-08-17]. "TEAM-SIGN-OFF [confirm sheet 2026-08-17]" (V_eta_go_forward_class_audit.md:723). |
| `probe_geometry` | retire | 3 of 3 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (V_eta_spatial_transcriptomics_plan.md:572). |
| `probe_location` | retire | no target recorded | [confirm sheet 2026-08-17]. "TEAM-SIGN-OFF [confirm sheet 2026-08-17]" (V_eta_go_forward_class_audit.md:723). |
| `projectvar` | in_progress | no target recorded | [misc singletons]. "TEAM-SIGN-OFF [misc singletons]: jess, 2026-08-09" (V_eta_go_forward_class_audit.md:9). |
| `pyraview` | retire | 1 of 1 | [raw recording observation]. "TEAM-SIGN-OFF [raw recording observation]" (V_eta_recording_observation_plan.md:99).; [pyraview levels, amends the 2026-08-13 pyraview pyramid confirmation]. "TEAM-SIGN-OFF [pyraview levels, amends the 2026-08-13" (V_eta_recording_observation_plan.md:111). |
| `session` | consumed by migrator (no tombstone) | 1 of 1 | [session]. "TEAM-SIGN-OFF [session]: jess@walthamdatascience.com /" (V_eta_go_forward_class_audit.md:664). |
| `sorting_parameters` | retire | 1 of 1 | [spike processing parameters]. "TEAM-SIGN-OFF [spike processing parameters]: jess" (V_eta_method_parameters_plan.md:32). |
| `spatialGeneExpressionCells` | retire | 5 of 5 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (V_eta_spatial_transcriptomics_plan.md:572). |
| `spatialGeneExpressionPyramid` | retire | 5 of 5 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (V_eta_spatial_transcriptomics_plan.md:572). |
| `spatialGeneExpressionTiles` | retire | 1 of 1 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (V_eta_spatial_transcriptomics_plan.md:572). |
| `spike_extraction_parameters` | retire | 1 of 1 | [spike processing parameters]. "TEAM-SIGN-OFF [spike processing parameters]: jess" (V_eta_method_parameters_plan.md:32). |
| `spike_extraction_parameters_modification` | retire | 1 of 1 | [spike processing parameters]. "TEAM-SIGN-OFF [spike processing parameters]: jess" (V_eta_method_parameters_plan.md:32). |
| `stimulus_bath` | consumed by migrator (no tombstone) | 2 of 2 | [bath is a manipulation]. "Decided by Jess Haley, 2026-10-21 [bath is a manipulation]" (V_eta_go_forward_class_audit.md:727). |
| `stimulus_parameter` | retire | no target recorded | [stimulus parameters]. "TEAM-SIGN-OFF [stimulus parameters]" (V_eta_stimulus_parameter_plan.md:221). |
| `stimulus_parameter_table` | retire | no target recorded | [stimulus parameters]. "TEAM-SIGN-OFF [stimulus parameters]" (V_eta_stimulus_parameter_plan.md:221). |
| `stimulus_presentation` | in_progress | 2 of 2 | [stimulus]. "TEAM-SIGN-OFF [stimulus]: jess@walthamdatascience.com /" (V_eta_stimulus_model_plan.md:258). |
| `stimulus_response` | retire | no target recorded | [stimulus response]. "TEAM-SIGN-OFF [stimulus response]" (V_eta_stimulus_response_model_plan.md:541). |
| `stimulus_response_scalar` | retire | 1 of 1 | [stimulus response]. "TEAM-SIGN-OFF [stimulus response]" (V_eta_stimulus_response_model_plan.md:541). |
| `stimulus_response_scalar_parameters` | retire | no target recorded | [stimulus response]. "TEAM-SIGN-OFF [stimulus response]" (V_eta_stimulus_response_model_plan.md:541). |
| `stimulus_response_scalar_parameters_basic` | retire | 1 of 1 | [stimulus response]. "TEAM-SIGN-OFF [stimulus response]" (V_eta_stimulus_response_model_plan.md:541). |
| `subject` | consumed by migrator (no tombstone) | 1 of 1 | [subject]. "TEAM-SIGN-OFF [subject]: jess@walthamdatascience.com /" (V_eta_go_forward_class_audit.md:697). |
| `subjectmeasurement` | retire | no target recorded | [subject measurement]. "TEAM-SIGN-OFF [subject measurement]: jess, 2026-08-06" (V_eta_go_forward_class_audit.md:336). |
| `syncgraph` | retire | 1 of 1 | [sync configuration]. "TEAM-SIGN-OFF [sync configuration]" (V_eta_clock_alignment_cluster_plan.md:506). |
| `syncrule` | retire | 1 of 1 | [sync configuration]. "TEAM-SIGN-OFF [sync configuration]" (V_eta_clock_alignment_cluster_plan.md:506). |
| `syncrule_mapping` | retire | 1 of 1 | [sync mapping]. "TEAM-SIGN-OFF [sync mapping]: jess@walthamdatascience.com /" (V_eta_clock_alignment_cluster_plan.md:508). |
| `treatment` | consumed by migrator (no tombstone) | 7 of 7 | [confirm sheet 2026-08-17]. "TEAM-SIGN-OFF [confirm sheet 2026-08-17]" (V_eta_go_forward_class_audit.md:723). |
| `tuningcurve_calc` | consumed by migrator (no tombstone) | 3 of 3 | [confirm sheet 2026-08-17]. "TEAM-SIGN-OFF [confirm sheet 2026-08-17]" (V_eta_go_forward_class_audit.md:723). |
| `valid_interval` | retire | 1 of 1 | [logical_observation]. "TEAM-SIGN-OFF [logical_observation]" (V_eta_logical_observation_plan.md:365).; [logical_observation amendment 1]. "TEAM-SIGN-OFF [logical_observation amendment 1]" (V_eta_logical_observation_plan.md:425). |
| `vmspikefilteringparameters` | retire | 1 of 1 | [spike processing parameters]. "TEAM-SIGN-OFF [spike processing parameters]: jess" (V_eta_method_parameters_plan.md:32). |
| `vmspikefit` | retire | 1 of 1 | [#73 audit 2, D1-D13]. "TEAM-SIGN-OFF [#73 audit 2, D1-D13]" (V_eta_spatial_transcriptomics_plan.md:574). |

Every decided target these classes name is present in the built set, so
what remains for them is MIGRATOR work, not schema work.

## Decision lines no class cites

DENOMINATOR: 63 document(s) read (3 generated copies excluded); 161 decision line(s) accepted, 2 rejected; 40 cited by a class, 121 cited by none.

An uncited line is a decision the record holds that no class points at.
Most decide something that is not one class (a tenet, a naming rule, a
field). If one decides a class's disposition, that class should cite it.

- sync configuration amendment 1. "TEAM-SIGN-OFF [sync configuration amendment 1]" (V_eta_clock_alignment_cluster_plan.md:638).
- data_body. "TEAM-SIGN-OFF [data_body]: jess@walthamdatascience.com /" (V_eta_data_body_model_plan.md:673).
- data_body amendment 4. "TEAM-SIGN-OFF [data_body amendment 4]" (V_eta_data_body_model_plan.md:1281).
- data_body amendment 3. "TEAM-SIGN-OFF [data_body amendment 3]" (V_eta_data_body_model_plan.md:1319).
- data_type only for plain arrays. "Decided by Jess Haley, 2026-10-21 [data_type only for plain" (V_eta_data_body_model_plan.md:1337).
- data_body amendment 5. "TEAM-SIGN-OFF [data_body amendment 5]" (V_eta_data_body_model_plan.md:1392).
- sorter output by location. "Decided by Jess Haley, 2026-10-21 [sorter output by" (V_eta_data_body_model_plan.md:1396).
- same_as. "TEAM-SIGN-OFF [same_as]: jess@walthamdatascience.com /" (V_eta_duplicate_entities_plan.md:95).
- spike train leaf. "TEAM-SIGN-OFF [spike train leaf]" (V_eta_ensemble_plan.md:218).
- 2026-10-08. "TEAM-SIGN-OFF: jess / 2026-10-08 -- statements are a" (V_eta_entity_composition_plan.md:49).
- 2026-10-08. "TEAM-SIGN-OFF: jess / 2026-10-08 -- datum_type is renamed" (V_eta_entity_composition_plan.md:61).
- 2026-10-08. "TEAM-SIGN-OFF: jess / 2026-10-08 -- add the text value kind" (V_eta_entity_composition_plan.md:70).
- 2026-10-08. "TEAM-SIGN-OFF: jess / 2026-10-08 -- one concrete entity" (V_eta_entity_composition_plan.md:116).
- entity type requires, report-only. "Decided by Jess Haley, 2026-10-21 [entity type requires" (V_eta_entity_composition_plan.md:118).
- 2026-10-08. "TEAM-SIGN-OFF: jess / 2026-10-08 -- strain is an" (V_eta_entity_composition_plan.md:129).
- 2026-10-08. "TEAM-SIGN-OFF: jess / 2026-10-08 -- global identifiers are" (V_eta_entity_composition_plan.md:150).
- 2026-10-08. "TEAM-SIGN-OFF: jess / 2026-10-08 -- web_resource and the" (V_eta_entity_composition_plan.md:167).
- 2026-10-19. "TEAM-SIGN-OFF: jess@walthamdatascience.com / 2026-10-19" (V_eta_entity_composition_plan.md:178).
- 2026-10-08. "TEAM-SIGN-OFF: jess / 2026-10-08 -- acquisition_system is" (V_eta_entity_composition_plan.md:190).
- 2026-10-08. "TEAM-SIGN-OFF: jess / 2026-10-08 -- method_parameters" (V_eta_entity_composition_plan.md:197).
- dataseries_channel_map. "TEAM-SIGN-OFF [dataseries_channel_map]: jess, 2026-08-06" (V_eta_go_forward_class_audit.md:228).
- confirm sheet 2026-08-22. "TEAM-SIGN-OFF [confirm sheet 2026-08-22]" (V_eta_go_forward_class_audit.md:725).
- immersion or dose. "Decided by Jess Haley, 2026-10-21 [immersion or dose]: A" (V_eta_go_forward_class_audit.md:729).
- unrecorded amount is NaN. "Decided by Jess Haley, 2026-10-21 [unrecorded amount is" (V_eta_go_forward_class_audit.md:731).
- prepared material recipe. "Decided by Jess Haley, 2026-10-21 [prepared material" (V_eta_go_forward_class_audit.md:768).
- seeding solution preparation day. "Decided by Jess Haley, 2026-10-21 [seeding solution" (V_eta_go_forward_class_audit.md:780).
- treatment routes by location. "Decided by Jess Haley, 2026-10-21 [treatment routes by" (V_eta_go_forward_class_audit.md:793).
- region parts. "Decided by Jess Haley, 2026-10-21 [region parts]" (V_eta_go_forward_class_audit.md:808).
- laterality on the part. "Decided by Jess Haley, 2026-10-21 [laterality on the part]" (V_eta_go_forward_class_audit.md:810).
- laterality variable. "Decided by Jess Haley, 2026-10-21 [laterality variable]" (V_eta_go_forward_class_audit.md:812).
- anatomy variable terms. "Decided by Jess Haley, 2026-10-21 [anatomy variable terms]" (V_eta_go_forward_class_audit.md:814).
- one part per side. "Decided by Jess Haley, 2026-10-21 [one part per side]" (V_eta_go_forward_class_audit.md:816).
- slice region chain. "Decided by Jess Haley, 2026-10-21 [slice region chain]: a" (V_eta_go_forward_class_audit.md:818).
- region anatomy is UBERON. "Decided by Jess Haley, 2026-10-21 [region anatomy is" (V_eta_go_forward_class_audit.md:820).
- babu-media. "Decided by Jess Haley, 2026-10-21 [babu-media]" (V_eta_go_forward_class_audit.md:852).
- virus-location. "Decided by Jess Haley, 2026-10-21 [virus-location]" (V_eta_go_forward_class_audit.md:865).
- unknown-amount-slot. "Decided by Jess Haley, 2026-10-21 [unknown-amount-slot]" (V_eta_go_forward_class_audit.md:881).
- dose per ingredient. "Decided by Jess Haley, 2026-10-21 [dose per ingredient]" (V_eta_go_forward_class_audit.md:892).
- multiple amount rows. "Decided by Jess Haley, 2026-10-21 [multiple amount rows]" (V_eta_go_forward_class_audit.md:904).
- named-chemical amount on the ingredient. "Decided by Jess Haley, 2026-10-21 [named-chemical amount on" (V_eta_go_forward_class_audit.md:906).
- blank per-body-mass on the ingredient. "Decided by Jess Haley, 2026-10-21 [blank per-body-mass on" (V_eta_go_forward_class_audit.md:908).
- generic treatment number. "Decided by Jess Haley, 2026-10-21 [generic treatment" (V_eta_go_forward_class_audit.md:910).
- treatment onset. "Decided by Jess Haley, 2026-10-21 [treatment onset]: a" (V_eta_go_forward_class_audit.md:912).
- virus injection onset. "Decided by Jess Haley, 2026-10-21 [virus injection onset]" (V_eta_go_forward_class_audit.md:914).
- transfer onset. "Decided by Jess Haley, 2026-10-21 [transfer onset]: a v1" (V_eta_go_forward_class_audit.md:916).
- orientation_direction_tuning.json location. "TEAM-SIGN-OFF [orientation_direction_tuning.json location]" (V_eta_go_forward_class_audit.md:989).
- time anchors, amends the 2026-08-22 confirm sheet. "TEAM-SIGN-OFF [time anchors, amends the 2026-08-22 confirm" (V_eta_go_forward_class_audit.md:1025).
- dimensioned classes, batch confirmation. "TEAM-SIGN-OFF [dimensioned classes, batch confirmation]" (V_eta_go_forward_class_audit.md:1027).
- 2026-10-09. "TEAM-SIGN-OFF: jess / 2026-10-09 -- membership of a session" (V_eta_linked_session_plan.md:95).
- parameter unit, #73 audit 2 D4. "TEAM-SIGN-OFF [parameter unit, #73 audit 2 D4]" (V_eta_method_parameters_plan.md:862).
- method. "TEAM-SIGN-OFF [method]: jess@walthamdatascience.com /" (V_eta_method_plan.md:188).
- receptive field naming. "TEAM-SIGN-OFF [receptive field naming]" (V_eta_ngrid_family_findings.md:381).
- hartley method implied. "Decided by Jess Haley, 2026-10-21 [hartley method implied]" (V_eta_ngrid_family_findings.md:419).
- 2026-08-05. "TEAM-SIGN-OFF: jess, 2026-08-05 -- strain is an entity with" (V_eta_openminds_family_record.md:20).
- subject keeps only its own strain. "Decided by Jess Haley, 2026-10-21 [subject keeps only its" (V_eta_openminds_family_record.md:1329).
- shared entities at dataset level. "Decided by Jess Haley, 2026-10-21 [shared entities at" (V_eta_openminds_family_record.md:1333).
- prefix spelling. "TEAM-SIGN-OFF [prefix spelling]" (V_eta_prefix_spelling_plan.md:202).
- spike trains as epoch bodies. "Decided by Jess Haley, 2026-10-21 [spike trains as epoch" (V_eta_recording_observation_plan.md:117).
- spike train variable. "Decided by Jess Haley, 2026-10-21 [spike train variable]: a" (V_eta_recording_observation_plan.md:119).
- ingested epoch documents retired. "Decided by Jess Haley, 2026-10-21 [ingested epoch documents" (V_eta_recording_observation_plan.md:121).
- archive compression. "Decided by Jess Haley, 2026-10-21 [archive compression]: a" (V_eta_recording_observation_plan.md:123).
- ingested epochs use the archive. "Decided by Jess Haley, 2026-10-21 [ingested epochs use the" (V_eta_recording_observation_plan.md:125).
- pyraview levels per epoch. "Decided by Jess Haley, 2026-10-21 [pyraview levels per" (V_eta_recording_observation_plan.md:127).
- pyraview leftovers. "Decided by Jess Haley, 2026-10-21 [pyraview leftovers]" (V_eta_recording_observation_plan.md:129).
- relation inheritance. "TEAM-SIGN-OFF [relation inheritance]: jess / 2026-10-21" (V_eta_relation_inheritance_plan.md:113).
- source unit. "TEAM-SIGN-OFF [source unit]: jess / 2026-10-21" (V_eta_source_unit_plan.md:69).
- source unit amendment 1. "TEAM-SIGN-OFF [source unit amendment 1]: jess / 2026-10-21" (V_eta_source_unit_plan.md:84).
- calculation-os-optional. "Decided by Jess Haley, 2026-10-21 [calculation-os-optional]" (V_eta_spatial_transcriptomics_plan.md:286).
- formulation strain ingredient. "TEAM-SIGN-OFF [formulation strain ingredient]" (V_eta_spatial_transcriptomics_plan.md:602).
- stimulus -- visual_grating_manipulation reconciliation. "TEAM-SIGN-OFF [stimulus -- visual_grating_manipulation" (V_eta_stimulus_model_plan.md:304).
- onsets on the sequence, #73 audit 2 D11. "TEAM-SIGN-OFF [onsets on the sequence, #73 audit 2 D11]" (V_eta_stimulus_model_plan.md:372).
- presentation with no subject. "Decided by Jess Haley, 2026-10-21 [presentation with no" (V_eta_stimulus_model_plan.md:396).
- response parameters as a shared method. "Decided by Jess Haley, 2026-10-21 [response parameters as a" (V_eta_stimulus_response_model_plan.md:604).
- control input told apart by its document. "Decided by Jess Haley, 2026-10-21 [control input told apart" (V_eta_stimulus_response_model_plan.md:606).
- empty response settings. "Decided by Jess Haley, 2026-10-21 [empty response" (V_eta_stimulus_response_model_plan.md:608).
- 2026-09-30. "TEAM-SIGN-OFF: jess / 2026-09-30 -- add the study entity" (V_eta_study_plan.md:21).
- 2026-10-21. "TEAM-SIGN-OFF: jess@walthamdatascience.com / 2026-10-21" (V_eta_study_plan.md:28).
- 2026-09-30. "TEAM-SIGN-OFF: jess / 2026-09-30 -- add the instance_of" (V_eta_study_plan.md:29).
- 2026-09-30. "TEAM-SIGN-OFF: jess / 2026-09-30 -- add the awarded_to" (V_eta_study_plan.md:30).
- 2026-09-30. "TEAM-SIGN-OFF: jess / 2026-09-30 -- add" (V_eta_study_plan.md:31).
- 2026-09-30. "TEAM-SIGN-OFF: jess / 2026-09-30 -- add optional" (V_eta_study_plan.md:40).
- 2026-09-30. "TEAM-SIGN-OFF: jess / 2026-09-30 -- add optional" (V_eta_study_plan.md:41).
- 2026-10-01. "TEAM-SIGN-OFF: jess / 2026-10-01 -- add optional" (V_eta_study_plan.md:50).
- 2026-10-02. "TEAM-SIGN-OFF: jess / 2026-10-02 -- contained_in is timed" (V_eta_study_plan.md:61).
- 2026-10-02. "TEAM-SIGN-OFF: jess / 2026-10-02 -- add optional" (V_eta_study_plan.md:110).
- 2026-10-02. "TEAM-SIGN-OFF: jess / 2026-10-02 -- add optional" (V_eta_study_plan.md:111).
- 2026-10-03. "TEAM-SIGN-OFF: jess / 2026-10-03 -- a formulation may be" (V_eta_study_plan.md:142).
- 2026-10-03. "TEAM-SIGN-OFF: jess / 2026-10-03 -- add optional" (V_eta_study_plan.md:143).
- 2026-10-03. "TEAM-SIGN-OFF: jess / 2026-10-03 -- add the humidity data" (V_eta_study_plan.md:171).
- 2026-10-03. "TEAM-SIGN-OFF: jess / 2026-10-03 -- T14: canonical units" (V_eta_study_plan.md:172).
- 2026-10-03. "TEAM-SIGN-OFF: jess / 2026-10-03 -- add length_calculation" (V_eta_study_plan.md:189).
- 2026-10-04. "TEAM-SIGN-OFF: jess / 2026-10-04 -- timed_sequence becomes" (V_eta_study_plan.md:336).
- 2026-10-04. "TEAM-SIGN-OFF: jess / 2026-10-04 -- tenet audit fixes" (V_eta_study_plan.md:337).
- 2026-10-04. "TEAM-SIGN-OFF: jess / 2026-10-04" (V_eta_study_plan.md:338).
- 2026-10-05. "TEAM-SIGN-OFF: jess / 2026-10-05 -- key_labels_id becomes" (V_eta_study_plan.md:339).
- 2026-10-05. "TEAM-SIGN-OFF: jess / 2026-10-05 -- T2 paragraph on" (V_eta_study_plan.md:340).
- 2026-10-05. "TEAM-SIGN-OFF: jess / 2026-10-05 -- add time_calculation" (V_eta_study_plan.md:341).
- contributor role nodes. "TEAM-SIGN-OFF [contributor role nodes]" (V_eta_study_plan.md:384).
- calculator + subject_calculation restructure. "TEAM-SIGN-OFF [calculator + subject_calculation" (V_eta_subject_calculation_plan.md:270).
- observation vs calculation, amends #67. "TEAM-SIGN-OFF [observation vs calculation, amends #67]" (V_eta_subject_calculation_plan.md:369).
- binding governance. "TEAM-SIGN-OFF [binding governance]: jess, 2026-08-10 -- bind" (V_eta_tenet_audit.md:438).
- date dtype. "TEAM-SIGN-OFF [date dtype]: jess@walthamdatascience.com /" (V_eta_tenet_audit.md:521).
- base naming. "TEAM-SIGN-OFF [base naming]: jess@walthamdatascience.com /" (V_eta_tenet_audit.md:525).
- time dtype. "TEAM-SIGN-OFF [time dtype]: jess@walthamdatascience.com /" (V_eta_tenet_audit.md:529).
- tenet amendments 2026-10-20. "TEAM-SIGN-OFF [tenet amendments 2026-10-20]: jess /" (V_eta_tenets.md:997).
- tenet amendments 2026-10-21. "TEAM-SIGN-OFF [tenet amendments 2026-10-21]" (V_eta_tenets.md:999).
- tenet T20, group entities. "TEAM-SIGN-OFF [tenet T20, group entities]" (V_eta_tenets.md:1000).
- term registry. "TEAM-SIGN-OFF [term registry]: jess@walthamdatascience.com" (V_eta_term_registry_plan.md:31).
- term registry closed value sets. "TEAM-SIGN-OFF [term registry closed value sets]" (V_eta_term_registry_plan.md:151).
- time_reference. "TEAM-SIGN-OFF [time_reference]: jess@walthamdatascience.com" (V_eta_time_reference_model_plan.md:468).
- time_reference uniqueness rule. "TEAM-SIGN-OFF [time_reference uniqueness rule]" (V_eta_time_reference_model_plan.md:735).
- epoch and session wall-clock time. "TEAM-SIGN-OFF [epoch and session wall-clock time]" (V_eta_time_reference_model_plan.md:762).
- time_reference end. "TEAM-SIGN-OFF [time_reference end]" (V_eta_time_reference_model_plan.md:797).
- time_reference tolerance. "TEAM-SIGN-OFF [time_reference tolerance]" (V_eta_time_reference_model_plan.md:840).
- time_reference tolerance amendment 1. "TEAM-SIGN-OFF [time_reference tolerance amendment 1]" (V_eta_time_reference_model_plan.md:861).
- tuning_curve composite + tuning_curve_calculation leaf, restructure. "TEAM-SIGN-OFF [tuning_curve composite +" (V_eta_tuning_model_plan.md:144).
- tuning shape, #73 audit 2 amendment. "TEAM-SIGN-OFF [tuning shape, #73 audit 2 amendment]" (V_eta_tuning_model_plan.md:246).
- complex trial responses. "Decided by Jess Haley, 2026-10-21 [complex trial" (V_eta_tuning_model_plan.md:250).
- pooled blank statistics. "Decided by Jess Haley, 2026-10-21 [pooled blank" (V_eta_tuning_model_plan.md:259).
- lightsheet reader questions R1-R6. "TEAM-SIGN-OFF [lightsheet reader questions R1-R6]" (review/73/OPEN_ITEMS.md:349).
- developed_by, hosted_by, distributed_as. "TEAM-SIGN-OFF [developed_by, hosted_by, distributed_as]" (review/73/OPEN_ITEMS.md:362).

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

DENOMINATOR: 3 row(s), each searched for its BARE CLASS NAME as a quoted literal in 19 batch post-pass file(s) under `+did2/+convert` (comments stripped).

- `calculator` -- no per-class migrator and no batch post-pass names it; passes through today
- `generic_file` -- **NOT untouched**: consumed by `foldGenericFiles.m`
- `imageCollection` -- no per-class migrator and no batch post-pass names it; passes through today

