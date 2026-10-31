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
| target classes | 115 |
| settled (persist) | 94 |
| `retire`, file still in the tree (open: delete it once nothing passes through it, [one folder, final classes only]) | 21 |
| **still open (`in_progress`)** | **0** |
| **`retire` with no migrator YET** | **1** |
| **open classes in all** | **21** |
| &nbsp;&nbsp;decided (cites a decision line), awaiting build | 20 |
| &nbsp;&nbsp;**proposed (not decided), awaiting review** | **1** |

| open-class BUILD/PROOF state (derived, see below) | count |
|---|---|
| (a) nothing built (the decision state is a separate column) | 2 |
| (b) built, awaiting corpus proof | 19 |
| (c) corpus: 0 survivors in the corpora read | 0 |
| (?) UNMEASURED -- no build evidence was ever taken | 0 |

## What is actually left on the 21 open classes

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
| build: migrator files inspected | 442 |
| build: &nbsp;&nbsp;-- of those, per-document migrator | 215 |
| build: &nbsp;&nbsp;-- of those, batch post-pass | 227 |
| build: V_zeta files DELIBERATELY EXCLUDED (`+migrators`, `+migrators_i`, `+migrators_e`) | 4 |
| build: migrator lines inspected | 82517 |
| build: &nbsp;&nbsp;-- of those, per-document migrator | 45818 |
| build: &nbsp;&nbsp;-- of those, batch post-pass | 36699 |
| build: classes queried | 21 |
| build: open classes MINTED as a document class | 4 |
| build: &nbsp;&nbsp;-- open classes minted in a per-document migrator (rows overlap) | 3 |
| build: &nbsp;&nbsp;-- open classes minted in a batch post-pass (rows overlap) | 1 |
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

### Where the 21 open classes sit

| state | classes |
|---|---|
| (a) nothing built (the decision state is a separate column) | 2 |
| (b) built, awaiting corpus proof | 19 |
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
| 1 | `b.document_class = struct('class_name', '<class>', ...)` | 32 | 4 | 28 |
| 2 | `b.document_class = classBlock('<class>', {supers})` | 0 | 0 | 0 |
| 3 | `b.document_class.class_name = '<class>';` | 3 | 3 | 0 |
| 4 | `did2.build.statement('<direction>', ..., 'ValueKind', '<kind>')`, `did2.build.document('<class>', ...)` or a fixed-class builder | 73 | 44 | 29 |
| 5 | a wrapper of idiom 4: `jStatement(preBody, '<class>', ...)` | 44 | 44 | 0 |
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
| `DID-matlab:convert/+roundtrip/daqreader_mfdaq_epochdata_ingested.m:55` | `CLASS;` |
| `DID-matlab:convert/+roundtrip/daqsystem.m:54` | `CLASS` |
| `DID-matlab:convert/+roundtrip/epochfiles_ingested.m:67` | `CLASS` |
| `DID-matlab:convert/+roundtrip/filenavigator.m:43` | `CLASS` |
| `DID-matlab:convert/+roundtrip/image.m:61` | `CLASS` |
| `DID-matlab:convert/+roundtrip/imageStack.m:117` | `CLASS` |
| `DID-matlab:convert/+roundtrip/private/calcParts.m:150` | `v1Class` |
| `DID-matlab:convert/+roundtrip/private/demoInverse.m:23` | `v1Class` |
| `DID-matlab:convert/+roundtrip/private/methodDocParts.m:79` | `v1Class` |
| `DID-matlab:convert/+roundtrip/private/openmindsInverse.m:94` | `v1Class` |
| `DID-matlab:convert/+roundtrip/stimulus_response_scalar_parameters_basic.m:131` | `CLASS` |
| `DID-matlab:convert/+roundtrip/subjectmeasurement.m:93` | `CLASS` |
| `DID-matlab:convert/+roundtrip/syncgraph.m:40` | `CLASS` |
| `DID-matlab:convert/+roundtrip/syncrule.m:114` | `CLASS` |
| `DID-matlab:convert/resolveEpochProbemap.m:1512` | `entry.class` |
| `DID-matlab:convert/resolveEpochProbemap.m:904` | `kind.className` |
| `DID-matlab:convert/universalRenames.m:256` | `v2ClassName;` |
| `DID-matlab:migrators_j/private/jMeasurementFold.m:109` | `observation + leaf` |
| `DID-matlab:migrators_j/treatment.m:153` | `manipulation + kind` |

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
| `acquisition_epoch` | decided | (b) | 18 consuming reference(s) (2 per-document migrator, 16 batch post-pass); minted as a document class at 1 site(s) (1 per-document migrator) | 1 (1+0) | 1 (1+0) | 2 (0+2) | 71 (31+40) | n/a -- not measured |
| `app` | decided | (b) | 20 consuming reference(s) (12 per-document migrator, 8 batch post-pass); decided target(s) built: `entity (software)` | - | 5 (1+4) | 13 (11+2) | 426 (256+170) | n/a -- not measured |
| `calculator` | decided | (a) | *none* | - | - | 2 (2+0) | 129 (79+50) | n/a -- not measured |
| `control_stimulus_ids` | decided | (b) | migrator `DID-matlab:migrators_j/control_stimulus_ids.m`; 13 consuming reference(s) (13 per-document migrator) | - | - | 6 (2+4) | 35 (28+7) | n/a -- not measured |
| `daqreader` | decided | (b) | migrator `DID-matlab:migrators_j/daqreader.m`; 5 consuming reference(s) (5 per-document migrator); decided target(s) built: `entity (software)` | - | 5 (2+3) | 7 (5+2) | 73 (53+20) | n/a -- not measured |
| `daqreader_epochdata_ingested` | decided | (b) | migrator `DID-matlab:migrators_j/daqreader_epochdata_ingested.m`; 3 consuming reference(s) (3 per-document migrator); minted as a document class at 1 site(s) (1 per-document migrator); decided target(s) built: `relative_time_reference` | 1 (1+0) | 2 (2+0) | 9 (6+3) | 42 (26+16) | n/a -- not measured |
| `daqreader_image_epochdata_ingested` | decided | (b) | migrator `DID-matlab:migrators_j/daqreader_image_epochdata_ingested.m`; decided target(s) built: `observation + intensity`, `relative_time_reference`, `sampled_body` | - | - | 4 (2+2) | 19 (13+6) | n/a -- not measured |
| `ensemble` | decided | (b) | 2 consuming reference(s) (1 per-document migrator, 1 batch post-pass); decided target(s) built: `entity (subject)`, `directed_relation`, `sampled_body` | - | - | - | 38 (33+5) | n/a -- not measured |
| `epochfiles_ingested` | decided | (b) | migrator `DID-matlab:migrators_j/epochfiles_ingested.m`; 26 consuming reference(s) (3 per-document migrator, 23 batch post-pass); minted as a document class at 1 site(s) (1 per-document migrator); decided target(s) built: `ingestion_manifest` | 1 (1+0) | 2 (1+1) | 7 (4+3) | 77 (26+51) | n/a -- not measured |
| `epochid` | decided | (b) | 31 consuming reference(s) (17 per-document migrator, 14 batch post-pass) | - | - | 39 (23+16) | 153 (99+54) | n/a -- not measured |
| `filenavigator` | decided | (b) | migrator `DID-matlab:migrators_j/filenavigator.m`; 4 consuming reference(s) (4 per-document migrator); decided target(s) built: `epoch_file_pattern` | - | 1 (0+1) | 5 (3+2) | 37 (26+11) | n/a -- not measured |
| `generic_file` | decided | (b) | 1 consuming reference(s) (1 batch post-pass); decided target(s) built: `observation + term`, `opaque_body` | - | - | 1 (0+1) | 43 (15+28) | n/a -- not measured |
| `openminds` | decided | (b) | migrator `DID-matlab:migrators_j/openminds.m`; 33 consuming reference(s) (20 per-document migrator, 13 batch post-pass) | - | 1 (0+1) | 10 (7+3) | 122 (72+50) | n/a -- not measured |
| `openminds_stimulus` | proposed (not decided) | (b) | migrator `DID-matlab:migrators_j/openminds_stimulus.m`; 1 consuming reference(s) (1 per-document migrator) | - | - | 5 (3+2) | 25 (18+7) | n/a -- not measured |
| `stimulus_presentation` | decided | (b) | migrator `DID-matlab:migrators_j/stimulus_presentation.m`; 9 consuming reference(s) (4 per-document migrator, 5 batch post-pass); decided target(s) built: `item`, `manipulation + item` | - | - | 5 (1+4) | 56 (41+15) | n/a -- not measured |
| `stimulus_response` | decided | (b) | 3 consuming reference(s) (3 per-document migrator) | - | 1 (0+1) | 3 (3+0) | 34 (21+13) | n/a -- not measured |
| `stimulus_response_scalar` | decided | (b) | migrator `DID-matlab:migrators_j/stimulus_response_scalar.m`; 10 consuming reference(s) (10 batch post-pass); minted as a document class at 1 site(s) (1 batch post-pass); decided target(s) built: `calculation + harmonic_component` | 1 (0+1) | 1 (0+1) | 12 (7+5) | 52 (18+34) | n/a -- not measured |
| `stimulus_response_scalar_parameters` | decided | (a) | *none* | - | - | - | 3 (1+2) | n/a -- not measured |
| `stimulus_response_scalar_parameters_basic` | decided | (b) | migrator `DID-matlab:migrators_j/stimulus_response_scalar_parameters_basic.m`; decided target(s) built: `method` | - | - | 5 (2+3) | 20 (6+14) | n/a -- not measured |
| `syncrule` | decided | (b) | migrator `DID-matlab:migrators_j/syncrule.m`; 8 consuming reference(s) (3 per-document migrator, 5 batch post-pass); decided target(s) built: `clock_alignment_configuration` | - | 1 (0+1) | 7 (5+2) | 63 (42+21) | n/a -- not measured |
| `valid_interval` | decided | (b) | 2 consuming reference(s) (2 batch post-pass); decided target(s) built: `observation + time` | - | - | 2 (0+2) | 25 (8+17) | n/a -- not measured |

#### (a) nothing built (the decision state is a separate column) -- 2

- `calculator` (decided) -- NAMED as a string value at 2 site(s), per-document migrator: `DID-matlab:migrators_j/private/jCalculation.m:524 (named)`, `DID-matlab:migrators_j/private/jCalculation.m:553 (named)`; mentioned in 79 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:1027 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:1045 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:500 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:591 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:608 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:767 (comment_mention)` ...; mentioned in 50 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/+roundtrip/contrastsensitivity_calc.m:17 (comment_mention)`, `DID-matlab:convert/+roundtrip/contrastsensitivity_calc.m:5 (comment_mention)`, `DID-matlab:convert/+roundtrip/contrastsensitivity_calc.m:9 (comment_mention)`, `DID-matlab:convert/+roundtrip/contrasttuning_calc.m:17 (comment_mention)`, `DID-matlab:convert/+roundtrip/contrasttuning_calc.m:5 (comment_mention)`, `DID-matlab:convert/+roundtrip/contrasttuning_calc.m:9 (comment_mention)` ...
- `stimulus_response_scalar_parameters` (decided) -- mentioned in 1 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/stimulus_response_scalar_parameters_basic.m:130 (comment_mention)`; mentioned in 2 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/+roundtrip/stimulus_response_scalar_parameters_basic.m:9 (comment_mention)`, `DID-matlab:convert/rawV1Classes.m:90 (comment_mention)`

#### (b) built, awaiting corpus proof -- 19

- `acquisition_epoch` (decided) -- consumed at 2 site(s), per-document migrator: `NDI-matlab:ndi_second_pass/ensembleMembership.m:574 (guard)`, `NDI-matlab:ndi_second_pass/ensembleMembership.m:681 (guard)`; consumed at 16 site(s), batch post-pass: `DID-matlab:convert/+roundtrip/element_epoch.m:33 (guard)`, `DID-matlab:convert/epochMint.m:3381 (guard)`, `DID-matlab:convert/epochMint.m:3382 (field_read)`, `DID-matlab:convert/epochMint.m:3383 (field_read)`, `DID-matlab:convert/epochMint.m:3386 (field_read)`, `DID-matlab:convert/epochMint.m:876 (guard)` ...; MINTED as a document class at 1 site(s), per-document migrator: `DID-matlab:migrators_j/element_epoch.m:199 (emitted_class)`; a block of this name is WRITTEN at 1 site(s), per-document migrator: `DID-matlab:migrators_j/element_epoch.m:201 (field_write)`; NAMED as a string value at 2 site(s), batch post-pass: `DID-matlab:convert/+roundtrip/element_epoch.m:45 (named)`, `DID-matlab:convert/v1_to_v2.m:1870 (named)`; mentioned in 31 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:714 (comment_mention)`, `DID-matlab:migrators_j/daqreader_image_epochdata_ingested.m:168 (comment_mention)`, `DID-matlab:migrators_j/element_epoch.m:111 (comment_mention)`, `DID-matlab:migrators_j/element_epoch.m:113 (comment_mention)`, `DID-matlab:migrators_j/element_epoch.m:117 (comment_mention)`, `DID-matlab:migrators_j/element_epoch.m:121 (comment_mention)` ...; mentioned in 40 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/+roundtrip/element_epoch.m:3 (comment_mention)`, `DID-matlab:convert/epochMint.m:25 (comment_mention)`, `DID-matlab:convert/epochMint.m:27 (comment_mention)`, `DID-matlab:convert/epochMint.m:3370 (comment_mention)`, `DID-matlab:convert/epochMint.m:3459 (comment_mention)`, `DID-matlab:convert/epochMint.m:3578 (comment_mention)` ...
- `app` (decided) -- consumed at 12 site(s), per-document migrator: `DID-matlab:migrators_j/private/jMethodParameters.m:110 (guard)`, `DID-matlab:migrators_j/private/jMethodParameters.m:112 (field_read)`, `DID-matlab:migrators_j/private/jSoftwareFromApp.m:124 (guard)`, `DID-matlab:migrators_j/private/jSoftwareFromApp.m:125 (field_read)`, `NDI-matlab:ndi_second_pass/appSoftware.m:42 (guard)`, `NDI-matlab:ndi_second_pass/appSoftware.m:43 (field_read)` ...; consumed at 8 site(s), batch post-pass: `DID-matlab:convert/+roundtrip/private/parkedMethodBlocks.m:13 (guard)`, `DID-matlab:convert/+roundtrip/private/parkedMethodBlocks.m:14 (field_read)`, `DID-matlab:convert/+v1read/readApp.m:43 (guard)`, `DID-matlab:convert/+v1read/readApp.m:44 (field_read)`, `DID-matlab:convert/+v1read/readApp.m:48 (field_read)`, `DID-matlab:convert/resolveValidIntervals.m:666 (guard)` ...; a block of this name is WRITTEN at 1 site(s), per-document migrator: `DID-matlab:migrators_j/private/jMethodParameters.m:137 (field_write)`; a block of this name is WRITTEN at 4 site(s), batch post-pass: `DID-matlab:convert/+roundtrip/private/calcParts.m:167 (field_write)`, `DID-matlab:convert/+roundtrip/private/methodDocParts.m:101 (field_write)`, `DID-matlab:convert/+roundtrip/private/parkedMethodBlocks.m:21 (field_write)`, `DID-matlab:convert/universalRenames.m:315 (field_write)`; NAMED as a string value at 11 site(s), per-document migrator: `DID-matlab:migrators_j/fitcurve.m:83 (named)`, `DID-matlab:migrators_j/jrclust_clusters.m:170 (named)`, `DID-matlab:migrators_j/kiasort_clusters.m:50 (named)`, `DID-matlab:migrators_j/kilosort_clusters.m:51 (named)`, `DID-matlab:migrators_j/neuron_extracellular.m:719 (named)`, `DID-matlab:migrators_j/private/jCalculation.m:524 (named)` ...; NAMED as a string value at 2 site(s), batch post-pass: `DID-matlab:convert/+roundtrip/private/parkedMethodBlocks.m:22 (named)`, `DID-matlab:convert/resolveValidIntervals.m:1121 (named)`; mentioned in 256 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:1058 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:143 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:159 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:405 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:406 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:493 (comment_mention)` ...; mentioned in 170 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/+roundtrip/contrast_tuning.m:12 (comment_mention)`, `DID-matlab:convert/+roundtrip/contrast_tuning.m:8 (comment_mention)`, `DID-matlab:convert/+roundtrip/contrastsensitivity_calc.m:12 (comment_mention)`, `DID-matlab:convert/+roundtrip/contrastsensitivity_calc.m:9 (comment_mention)`, `DID-matlab:convert/+roundtrip/contrasttuning_calc.m:12 (comment_mention)`, `DID-matlab:convert/+roundtrip/contrasttuning_calc.m:9 (comment_mention)` ...; target(s) BUILT: `entity (software)`
- `control_stimulus_ids` (decided) -- migrator `DID-matlab:migrators_j/control_stimulus_ids.m`; consumed at 13 site(s), per-document migrator: `DID-matlab:migrators_j/control_stimulus_ids.m:104 (guard)`, `DID-matlab:migrators_j/control_stimulus_ids.m:105 (field_read)`, `NDI-matlab:ndi_second_pass/controlRecordsByPresentation.m:77 (guard)`, `NDI-matlab:ndi_second_pass/stimulusPresentationToItem.m:1032 (guard)`, `NDI-matlab:ndi_second_pass/stimulusPresentationToItem.m:1033 (field_read)`, `NDI-matlab:ndi_second_pass/stimulusPresentationToItem.m:1043 (guard)` ...; NAMED as a string value at 2 site(s), per-document migrator: `DID-matlab:migrators_j/control_stimulus_ids.m:141 (named)`, `NDI-matlab:ndi_second_pass/stimulusPresentationToItem.m:1034 (named)`; NAMED as a string value at 4 site(s), batch post-pass: `DID-matlab:convert/+roundtrip/control_stimulus_ids.m:23 (named)`, `DID-matlab:convert/rawV1Classes.m:571 (named)`, `DID-matlab:convert/tuningBatchIndex.m:113 (named)`, `DID-matlab:convert/v1_to_v2.m:1592 (named)`; mentioned in 28 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:612 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:613 (comment_mention)`, `DID-matlab:migrators_j/control_stimulus_ids.m:110 (comment_mention)`, `DID-matlab:migrators_j/control_stimulus_ids.m:116 (comment_mention)`, `DID-matlab:migrators_j/control_stimulus_ids.m:121 (comment_mention)`, `DID-matlab:migrators_j/control_stimulus_ids.m:136 (comment_mention)` ...; mentioned in 7 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/+roundtrip/control_stimulus_ids.m:17 (comment_mention)`, `DID-matlab:convert/+roundtrip/control_stimulus_ids.m:2 (comment_mention)`, `DID-matlab:convert/+roundtrip/control_stimulus_ids.m:5 (comment_mention)`, `DID-matlab:convert/+roundtrip/control_stimulus_ids.m:6 (comment_mention)`, `DID-matlab:convert/rawV1Classes.m:351 (comment_mention)`, `DID-matlab:convert/universalRenames.m:501 (comment_mention)` ...
- `daqreader` (decided) -- migrator `DID-matlab:migrators_j/daqreader.m`; consumed at 5 site(s), per-document migrator: `DID-matlab:migrators_j/daqreader.m:138 (guard)`, `DID-matlab:migrators_j/daqreader.m:139 (field_read)`, `DID-matlab:migrators_j/daqreader.m:140 (field_read)`, `DID-matlab:migrators_j/daqreader_ndr.m:157 (field_read)`, `DID-matlab:migrators_j/daqreader_ndr.m:98 (guard)`; a block of this name is WRITTEN at 2 site(s), per-document migrator: `DID-matlab:migrators_j/daqreader_ndr.m:102 (field_write)`, `DID-matlab:migrators_j/daqreader_ndr.m:99 (field_write)`; a block of this name is WRITTEN at 3 site(s), batch post-pass: `DID-matlab:convert/+roundtrip/daqreader.m:43 (field_write)`, `DID-matlab:convert/+roundtrip/daqreader.m:46 (field_write)`, `DID-matlab:convert/+roundtrip/daqreader_ndr.m:40 (field_write)`; NAMED as a string value at 5 site(s), per-document migrator: `DID-matlab:migrators_j/daqreader.m:130 (named)`, `DID-matlab:migrators_j/daqreader.m:132 (named)`, `DID-matlab:migrators_j/daqreader.m:160 (named)`, `DID-matlab:migrators_j/daqreader_ndr.m:52 (named)`, `DID-matlab:migrators_j/daqreader_ndr.m:65 (named)`; NAMED as a string value at 2 site(s), batch post-pass: `DID-matlab:convert/+roundtrip/daqreader.m:26 (named)`, `DID-matlab:convert/rawV1Classes.m:510 (named)`; mentioned in 53 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:191 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:246 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:637 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:638 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:654 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:657 (comment_mention)` ...; mentioned in 20 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/+roundtrip/daqreader.m:11 (comment_mention)`, `DID-matlab:convert/+roundtrip/daqreader.m:12 (comment_mention)`, `DID-matlab:convert/+roundtrip/daqreader.m:19 (comment_mention)`, `DID-matlab:convert/+roundtrip/daqreader.m:2 (comment_mention)`, `DID-matlab:convert/+roundtrip/daqreader.m:4 (comment_mention)`, `DID-matlab:convert/+roundtrip/daqreader.m:5 (comment_mention)` ...; target(s) BUILT: `entity (software)`
- `daqreader_epochdata_ingested` (decided) -- migrator `DID-matlab:migrators_j/daqreader_epochdata_ingested.m`; consumed at 3 site(s), per-document migrator: `DID-matlab:migrators_j/daqreader_mfdaq_epochdata_ingested.m:120 (field_read)`, `DID-matlab:migrators_j/daqreader_mfdaq_epochdata_ingested.m:94 (guard)`, `DID-matlab:migrators_j/daqreader_mfdaq_epochdata_ingested.m:95 (field_read)`; MINTED as a document class at 1 site(s), per-document migrator: `DID-matlab:migrators_j/daqreader_mfdaq_epochdata_ingested.m:90 (emitted_class)`; a block of this name is WRITTEN at 2 site(s), per-document migrator: `DID-matlab:migrators_j/daqreader_mfdaq_epochdata_ingested.m:102 (field_write)`, `DID-matlab:migrators_j/daqreader_mfdaq_epochdata_ingested.m:96 (field_write)`; NAMED as a string value at 6 site(s), per-document migrator: `DID-matlab:migrators_j/daqreader_epochdata_ingested.m:124 (named)`, `DID-matlab:migrators_j/daqreader_epochdata_ingested.m:127 (named)`, `DID-matlab:migrators_j/daqreader_epochdata_ingested.m:143 (named)`, `DID-matlab:migrators_j/daqreader_image_epochdata_ingested.m:317 (named)`, `DID-matlab:migrators_j/daqreader_image_epochdata_ingested.m:334 (named)`, `NDI-matlab:ndi_second_pass/sliceTetanus.m:128 (named)`; NAMED as a string value at 3 site(s), batch post-pass: `DID-matlab:convert/+roundtrip/daqreader_epochdata_ingested.m:15 (named)`, `DID-matlab:convert/+roundtrip/daqreader_mfdaq_epochdata_ingested.m:33 (named)`, `DID-matlab:convert/rawV1Classes.m:532 (named)`; mentioned in 26 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:640 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:649 (comment_mention)`, `DID-matlab:migrators_j/daqreader.m:55 (comment_mention)`, `DID-matlab:migrators_j/daqreader_epochdata_ingested.m:110 (comment_mention)`, `DID-matlab:migrators_j/daqreader_epochdata_ingested.m:98 (comment_mention)`, `DID-matlab:migrators_j/daqreader_image_epochdata_ingested.m:20 (comment_mention)` ...; mentioned in 16 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/+roundtrip/daqreader_epochdata_ingested.m:2 (comment_mention)`, `DID-matlab:convert/+roundtrip/daqreader_epochdata_ingested.m:4 (comment_mention)`, `DID-matlab:convert/+roundtrip/daqreader_epochdata_ingested.m:5 (comment_mention)`, `DID-matlab:convert/+roundtrip/daqreader_mfdaq_epochdata_ingested.m:11 (comment_mention)`, `DID-matlab:convert/+roundtrip/daqreader_mfdaq_epochdata_ingested.m:20 (comment_mention)`, `DID-matlab:convert/+roundtrip/daqreader_mfdaq_epochdata_ingested.m:7 (comment_mention)` ...; target(s) BUILT: `relative_time_reference`
- `daqreader_image_epochdata_ingested` (decided) -- migrator `DID-matlab:migrators_j/daqreader_image_epochdata_ingested.m`; NAMED as a string value at 2 site(s), per-document migrator: `DID-matlab:migrators_j/daqreader_image_epochdata_ingested.m:315 (named)`, `DID-matlab:migrators_j/daqreader_image_epochdata_ingested.m:320 (named)`; NAMED as a string value at 2 site(s), batch post-pass: `DID-matlab:convert/+roundtrip/daqreader_image_epochdata_ingested.m:15 (named)`, `DID-matlab:convert/rawV1Classes.m:533 (named)`; mentioned in 13 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:643 (comment_mention)`, `DID-matlab:migrators_j/daqreader.m:56 (comment_mention)`, `DID-matlab:migrators_j/daqreader_epochdata_ingested.m:52 (comment_mention)`, `DID-matlab:migrators_j/daqreader_image_epochdata_ingested.m:119 (comment_mention)`, `DID-matlab:migrators_j/daqreader_image_epochdata_ingested.m:120 (comment_mention)`, `DID-matlab:migrators_j/daqreader_image_epochdata_ingested.m:155 (comment_mention)` ...; mentioned in 6 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/+roundtrip/daqreader_image_epochdata_ingested.m:2 (comment_mention)`, `DID-matlab:convert/+roundtrip/daqreader_image_epochdata_ingested.m:4 (comment_mention)`, `DID-matlab:convert/+roundtrip/daqreader_image_epochdata_ingested.m:5 (comment_mention)`, `DID-matlab:convert/epochMint.m:252 (comment_mention)`, `DID-matlab:convert/epochMint.m:317 (comment_mention)`, `DID-matlab:convert/rawV1Classes.m:196 (comment_mention)`; target(s) BUILT: `observation + intensity`, `relative_time_reference`, `sampled_body`
- `ensemble` (decided) -- consumed at 1 site(s), per-document migrator: `NDI-matlab:ndi_second_pass/ensembleMembership.m:411 (guard)`; consumed at 1 site(s), batch post-pass: `DID-matlab:convert/resolveEpochProbemap.m:824 (guard)`; mentioned in 33 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:708 (comment_mention)`, `DID-matlab:migrators_j/element.m:151 (comment_mention)`, `DID-matlab:migrators_j/element.m:184 (comment_mention)`, `DID-matlab:migrators_j/element.m:7 (comment_mention)`, `DID-matlab:migrators_j/element_epoch.m:100 (comment_mention)`, `DID-matlab:migrators_j/element_epoch.m:101 (comment_mention)` ...; mentioned in 5 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/resolveEpochProbemap.m:772 (comment_mention)`, `DID-matlab:convert/resolveEpochProbemap.m:825 (comment_mention)`, `DID-matlab:convert/resolveEpochProbemap.m:826 (comment_mention)`, `DID-matlab:convert/resolveEpochProbemap.m:829 (comment_mention)`, `DID-matlab:convert/resolveResponseParameters.m:103 (comment_mention)`; target(s) BUILT: `entity (subject)`, `directed_relation`, `sampled_body`
- `epochfiles_ingested` (decided) -- migrator `DID-matlab:migrators_j/epochfiles_ingested.m`; consumed at 3 site(s), per-document migrator: `NDI-matlab:ndi_second_pass/navigatorEpochFiles.m:63 (guard)`, `NDI-matlab:ndi_second_pass/navigatorEpochFiles.m:64 (guard)`, `NDI-matlab:ndi_second_pass/navigatorEpochFiles.m:68 (field_read)`; consumed at 23 site(s), batch post-pass: `DID-matlab:convert/+roundtrip/syncrule_mapping.m:182 (guard)`, `DID-matlab:convert/+roundtrip/syncrule_mapping.m:185 (field_read)`, `DID-matlab:convert/+roundtrip/syncrule_mapping.m:246 (guard)`, `DID-matlab:convert/+roundtrip/syncrule_mapping.m:247 (guard)`, `DID-matlab:convert/epochMint.m:3008 (guard)`, `DID-matlab:convert/epochMint.m:3100 (guard)` ...; MINTED as a document class at 1 site(s), per-document migrator: `NDI-matlab:ndi_second_pass/navigatorEpochFiles.m:101 (emitted_class)`; a block of this name is WRITTEN at 1 site(s), per-document migrator: `NDI-matlab:ndi_second_pass/navigatorEpochFiles.m:111 (field_write)`; a block of this name is WRITTEN at 1 site(s), batch post-pass: `DID-matlab:convert/+roundtrip/epochfiles_ingested.m:71 (field_write)`; NAMED as a string value at 4 site(s), per-document migrator: `DID-matlab:migrators_j/epochfiles_ingested.m:290 (named)`, `DID-matlab:migrators_j/epochfiles_ingested.m:296 (named)`, `NDI-matlab:ndi_second_pass/navigatorEpochFiles.m:102 (named)`, `NDI-matlab:ndi_second_pass/sliceTetanus.m:137 (named)`; NAMED as a string value at 3 site(s), batch post-pass: `DID-matlab:convert/+roundtrip/epochfiles_ingested.m:43 (named)`, `DID-matlab:convert/nTrodeElectrodeCounts.m:98 (named)`, `DID-matlab:convert/rawV1Classes.m:504 (named)`; mentioned in 26 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:177 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:715 (comment_mention)`, `DID-matlab:migrators_j/element.m:198 (comment_mention)`, `DID-matlab:migrators_j/element.m:36 (comment_mention)`, `DID-matlab:migrators_j/epochfiles_ingested.m:115 (comment_mention)`, `DID-matlab:migrators_j/epochfiles_ingested.m:192 (comment_mention)` ...; mentioned in 51 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/+roundtrip/epochfiles_ingested.m:11 (comment_mention)`, `DID-matlab:convert/+roundtrip/epochfiles_ingested.m:2 (comment_mention)`, `DID-matlab:convert/+roundtrip/epochfiles_ingested.m:26 (comment_mention)`, `DID-matlab:convert/+roundtrip/epochfiles_ingested.m:27 (comment_mention)`, `DID-matlab:convert/+roundtrip/epochfiles_ingested.m:28 (comment_mention)`, `DID-matlab:convert/+roundtrip/epochfiles_ingested.m:35 (comment_mention)` ...; target(s) BUILT: `ingestion_manifest`
- `epochid` (decided) -- consumed at 17 site(s), per-document migrator: `DID-matlab:migrators_j/private/jMethodParameters.m:141 (guard)`, `DID-matlab:migrators_j/private/jMethodParameters.m:144 (guard)`, `NDI-matlab:ndi_second_pass/bodyResolver.m:675 (guard)`, `NDI-matlab:ndi_second_pass/bodyResolver.m:676 (guard)`, `NDI-matlab:ndi_second_pass/bodyResolver.m:677 (field_read)`, `NDI-matlab:ndi_second_pass/ensembleMembership.m:707 (guard)` ...; consumed at 14 site(s), batch post-pass: `DID-matlab:convert/+roundtrip/private/parkedMethodBlocks.m:24 (guard)`, `DID-matlab:convert/epochMint.m:1110 (guard)`, `DID-matlab:convert/epochMint.m:1120 (guard)`, `DID-matlab:convert/epochMint.m:2080 (guard)`, `DID-matlab:convert/epochMint.m:2081 (field_read)`, `DID-matlab:convert/resolveDeferredBaths.m:617 (guard)` ...; NAMED as a string value at 23 site(s), per-document migrator: `DID-matlab:migrators_j/daqreader_epochdata_ingested.m:125 (named)`, `DID-matlab:migrators_j/daqreader_image_epochdata_ingested.m:318 (named)`, `DID-matlab:migrators_j/epochfiles_ingested.m:280 (named)`, `DID-matlab:migrators_j/oneepoch.m:144 (named)`, `DID-matlab:migrators_j/openminds_stimulus.m:113 (named)`, `DID-matlab:migrators_j/private/jMethodParameters.m:142 (named)` ...; NAMED as a string value at 16 site(s), batch post-pass: `DID-matlab:convert/+roundtrip/element_epoch.m:62 (named)`, `DID-matlab:convert/+roundtrip/element_epoch.m:64 (named)`, `DID-matlab:convert/+roundtrip/oneepoch.m:60 (named)`, `DID-matlab:convert/+roundtrip/oneepoch.m:62 (named)`, `DID-matlab:convert/+roundtrip/private/parkedMethodBlocks.m:25 (named)`, `DID-matlab:convert/+roundtrip/private/parkedMethodBlocks.m:26 (named)` ...; mentioned in 99 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:158 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:161 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader_epochdata_ingested.m:27 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader_epochdata_ingested.m:34 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader_epochdata_ingested.m:36 (comment_mention)`, `DID-matlab:migrators_j/daqmetadatareader_epochdata_ingested.m:40 (comment_mention)` ...; mentioned in 54 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/+roundtrip/daqreader_mfdaq_epochdata_ingested.m:18 (comment_mention)`, `DID-matlab:convert/+roundtrip/daqreader_mfdaq_epochdata_ingested.m:8 (comment_mention)`, `DID-matlab:convert/+roundtrip/element_epoch.m:15 (comment_mention)`, `DID-matlab:convert/+roundtrip/element_epoch.m:6 (comment_mention)`, `DID-matlab:convert/+roundtrip/oneepoch.m:14 (comment_mention)`, `DID-matlab:convert/+roundtrip/oneepoch.m:5 (comment_mention)` ...
- `filenavigator` (decided) -- migrator `DID-matlab:migrators_j/filenavigator.m`; consumed at 4 site(s), per-document migrator: `DID-matlab:migrators_j/filenavigator.m:154 (guard)`, `DID-matlab:migrators_j/filenavigator.m:155 (field_read)`, `DID-matlab:migrators_j/filenavigator.m:156 (field_read)`, `NDI-matlab:ndi_second_pass/navigatorEpochFiles.m:83 (field_read)`; a block of this name is WRITTEN at 1 site(s), batch post-pass: `DID-matlab:convert/+roundtrip/filenavigator.m:46 (field_write)`; NAMED as a string value at 3 site(s), per-document migrator: `DID-matlab:migrators_j/filenavigator.m:145 (named)`, `DID-matlab:migrators_j/filenavigator.m:148 (named)`, `DID-matlab:migrators_j/filenavigator.m:171 (named)`; NAMED as a string value at 2 site(s), batch post-pass: `DID-matlab:convert/+roundtrip/filenavigator.m:28 (named)`, `DID-matlab:convert/rawV1Classes.m:509 (named)`; mentioned in 26 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:175 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:235 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:499 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:538 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:732 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:733 (comment_mention)` ...; mentioned in 11 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/+roundtrip/epochfiles_ingested.m:25 (comment_mention)`, `DID-matlab:convert/+roundtrip/filenavigator.m:2 (comment_mention)`, `DID-matlab:convert/+roundtrip/filenavigator.m:22 (comment_mention)`, `DID-matlab:convert/+roundtrip/filenavigator.m:4 (comment_mention)`, `DID-matlab:convert/+roundtrip/filenavigator.m:5 (comment_mention)`, `DID-matlab:convert/+roundtrip/private/cell2strOf.m:7 (comment_mention)` ...; target(s) BUILT: `epoch_file_pattern`
- `generic_file` (decided) -- consumed at 1 site(s), batch post-pass: `DID-matlab:convert/foldGenericFiles.m:524 (guard)`; NAMED as a string value at 1 site(s), batch post-pass: `DID-matlab:convert/foldGenericFiles.m:580 (named)`; mentioned in 15 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:398 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:402 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:411 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:414 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:432 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:719 (comment_mention)` ...; mentioned in 28 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/foldGenericFiles.m:100 (comment_mention)`, `DID-matlab:convert/foldGenericFiles.m:108 (comment_mention)`, `DID-matlab:convert/foldGenericFiles.m:124 (comment_mention)`, `DID-matlab:convert/foldGenericFiles.m:138 (comment_mention)`, `DID-matlab:convert/foldGenericFiles.m:1459 (comment_mention)`, `DID-matlab:convert/foldGenericFiles.m:150 (comment_mention)` ...; target(s) BUILT: `observation + term`, `opaque_body`
- `openminds` (decided) -- migrator `DID-matlab:migrators_j/openminds.m`; consumed at 20 site(s), per-document migrator: `DID-matlab:migrators_j/openminds.m:138 (guard)`, `DID-matlab:migrators_j/openminds.m:139 (field_read)`, `DID-matlab:migrators_j/openminds.m:144 (field_read)`, `DID-matlab:migrators_j/openminds_element.m:57 (guard)`, `DID-matlab:migrators_j/openminds_element.m:69 (guard)`, `DID-matlab:migrators_j/openminds_element.m:70 (field_read)` ...; consumed at 13 site(s), batch post-pass: `DID-matlab:convert/+roundtrip/openminds_subject.m:40 (guard)`, `DID-matlab:convert/+roundtrip/openminds_subject.m:49 (field_read)`, `DID-matlab:convert/+roundtrip/openminds_subject.m:88 (field_read)`, `DID-matlab:convert/+roundtrip/openminds_subject.m:91 (field_read)`, `DID-matlab:convert/openmindsIdRebuilds.m:97 (guard)`, `DID-matlab:convert/openmindsIdRebuilds.m:98 (field_read)` ...; a block of this name is WRITTEN at 1 site(s), batch post-pass: `DID-matlab:convert/+roundtrip/private/openmindsInverse.m:98 (field_write)`; NAMED as a string value at 7 site(s), per-document migrator: `DID-matlab:migrators_j/openminds.m:161 (named)`, `DID-matlab:migrators_j/openminds.m:163 (named)`, `DID-matlab:migrators_j/openminds_element.m:58 (named)`, `DID-matlab:migrators_j/openminds_stimulus.m:111 (named)`, `DID-matlab:migrators_j/openminds_subject.m:54 (named)`, `NDI-matlab:ndi_second_pass/sliceTetanus.m:149 (named)` ...; NAMED as a string value at 3 site(s), batch post-pass: `DID-matlab:convert/+roundtrip/openminds.m:23 (named)`, `DID-matlab:convert/+roundtrip/private/openmindsInverse.m:95 (named)`, `DID-matlab:convert/rawV1Classes.m:578 (named)`; mentioned in 72 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:840 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:841 (comment_mention)`, `DID-matlab:migrators_j/openminds.m:101 (comment_mention)`, `DID-matlab:migrators_j/openminds.m:110 (comment_mention)`, `DID-matlab:migrators_j/openminds.m:112 (comment_mention)`, `DID-matlab:migrators_j/openminds.m:113 (comment_mention)` ...; mentioned in 50 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/+entities/Contents.m:10 (comment_mention)`, `DID-matlab:convert/+roundtrip/openminds.m:17 (comment_mention)`, `DID-matlab:convert/+roundtrip/openminds.m:2 (comment_mention)`, `DID-matlab:convert/+roundtrip/openminds.m:4 (comment_mention)`, `DID-matlab:convert/+roundtrip/openminds.m:5 (comment_mention)`, `DID-matlab:convert/+roundtrip/private/openmindsInverse.m:16 (comment_mention)` ...
- `openminds_stimulus` (proposed (not decided)) -- migrator `DID-matlab:migrators_j/openminds_stimulus.m`; consumed at 1 site(s), per-document migrator: `NDI-matlab:ndi_second_pass/sliceTetanus.m:531 (guard)`; NAMED as a string value at 3 site(s), per-document migrator: `DID-matlab:migrators_j/openminds_stimulus.m:112 (named)`, `DID-matlab:migrators_j/openminds_stimulus.m:115 (named)`, `NDI-matlab:ndi_second_pass/subjectStrainAssembly.m:998 (named)`; NAMED as a string value at 2 site(s), batch post-pass: `DID-matlab:convert/+roundtrip/openminds_stimulus.m:24 (named)`, `DID-matlab:convert/rawV1Classes.m:581 (named)`; mentioned in 18 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:845 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:846 (comment_mention)`, `DID-matlab:migrators_j/element.m:73 (comment_mention)`, `DID-matlab:migrators_j/filenavigator.m:64 (comment_mention)`, `DID-matlab:migrators_j/openminds_stimulus.m:2 (comment_mention)`, `DID-matlab:migrators_j/openminds_stimulus.m:20 (comment_mention)` ...; mentioned in 7 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/+roundtrip/openminds_stimulus.m:18 (comment_mention)`, `DID-matlab:convert/+roundtrip/openminds_stimulus.m:2 (comment_mention)`, `DID-matlab:convert/+roundtrip/openminds_stimulus.m:5 (comment_mention)`, `DID-matlab:convert/+roundtrip/openminds_stimulus.m:6 (comment_mention)`, `DID-matlab:convert/+roundtrip/openminds_stimulus.m:8 (comment_mention)`, `DID-matlab:convert/rawV1Classes.m:473 (comment_mention)` ...
- `stimulus_presentation` (decided) -- migrator `DID-matlab:migrators_j/stimulus_presentation.m`; consumed at 4 site(s), per-document migrator: `NDI-matlab:ndi_second_pass/hartleyBasisGratings.m:357 (guard)`, `NDI-matlab:ndi_second_pass/hartleyBasisGratings.m:360 (field_read)`, `NDI-matlab:ndi_second_pass/stimulusPresentationToItem.m:1581 (guard)`, `NDI-matlab:ndi_second_pass/stimulusPresentationToItem.m:1582 (field_read)`; consumed at 5 site(s), batch post-pass: `DID-matlab:convert/stimulusPresentationSpecs.m:76 (guard)`, `DID-matlab:convert/stimulusPresentationSpecs.m:82 (guard)`, `DID-matlab:convert/stimulusPresentationSpecs.m:85 (field_read)`, `DID-matlab:convert/tuningBatchIndex.m:171 (guard)`, `DID-matlab:convert/tuningBatchIndex.m:174 (field_read)`; NAMED as a string value at 1 site(s), per-document migrator: `DID-matlab:migrators_j/stimulus_presentation.m:191 (named)`; NAMED as a string value at 4 site(s), batch post-pass: `DID-matlab:convert/rawV1Classes.m:561 (named)`, `DID-matlab:convert/stimulusPresentationSpecs.m:49 (named)`, `DID-matlab:convert/tuningBatchIndex.m:112 (named)`, `DID-matlab:convert/v1_to_v2.m:1591 (named)`; mentioned in 41 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:978 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:979 (comment_mention)`, `DID-matlab:migrators_j/control_stimulus_ids.m:117 (comment_mention)`, `DID-matlab:migrators_j/control_stimulus_ids.m:123 (comment_mention)`, `DID-matlab:migrators_j/control_stimulus_ids.m:126 (comment_mention)`, `DID-matlab:migrators_j/control_stimulus_ids.m:129 (comment_mention)` ...; mentioned in 15 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/+roundtrip/stimulus_presentation.m:14 (comment_mention)`, `DID-matlab:convert/+roundtrip/stimulus_presentation.m:2 (comment_mention)`, `DID-matlab:convert/+roundtrip/stimulus_presentation.m:5 (comment_mention)`, `DID-matlab:convert/+roundtrip/stimulus_presentation.m:6 (comment_mention)`, `DID-matlab:convert/rawV1Classes.m:184 (comment_mention)`, `DID-matlab:convert/rawV1Classes.m:186 (comment_mention)` ...; target(s) BUILT: `item`, `manipulation + item`
- `stimulus_response` (decided) -- consumed at 3 site(s), per-document migrator: `NDI-matlab:ndi_second_pass/bodyResolver.m:628 (guard)`, `NDI-matlab:ndi_second_pass/bodyResolver.m:650 (guard)`, `NDI-matlab:ndi_second_pass/bodyResolver.m:656 (guard)`; a block of this name is WRITTEN at 1 site(s), batch post-pass: `DID-matlab:convert/+roundtrip/stimulus_response_scalar.m:149 (field_write)`; NAMED as a string value at 3 site(s), per-document migrator: `DID-matlab:migrators_j/stimulus_response_scalar.m:153 (named)`, `DID-matlab:migrators_j/stimulus_response_scalar.m:154 (named)`, `DID-matlab:migrators_j/stimulus_response_scalar.m:192 (named)`; mentioned in 21 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/stimulus_presentation.m:52 (comment_mention)`, `DID-matlab:migrators_j/stimulus_response_scalar.m:103 (comment_mention)`, `DID-matlab:migrators_j/stimulus_response_scalar.m:107 (comment_mention)`, `DID-matlab:migrators_j/stimulus_response_scalar.m:25 (comment_mention)`, `DID-matlab:migrators_j/stimulus_response_scalar.m:55 (comment_mention)`, `DID-matlab:migrators_j/stimulus_response_scalar.m:58 (comment_mention)` ...; mentioned in 13 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/+roundtrip/stimulus_response_scalar.m:30 (comment_mention)`, `DID-matlab:convert/+roundtrip/stimulus_response_scalar.m:36 (comment_mention)`, `DID-matlab:convert/+roundtrip/stimulus_response_scalar.m:7 (comment_mention)`, `DID-matlab:convert/epochIndex.m:241 (comment_mention)`, `DID-matlab:convert/epochIndex.m:292 (comment_mention)`, `DID-matlab:convert/epochMint.m:1343 (comment_mention)` ...
- `stimulus_response_scalar` (decided) -- migrator `DID-matlab:migrators_j/stimulus_response_scalar.m`; consumed at 10 site(s), batch post-pass: `DID-matlab:convert/+roundtrip/stimulus_response_scalar.m:63 (guard)`, `DID-matlab:convert/epochMint.m:1378 (guard)`, `DID-matlab:convert/epochMint.m:2375 (field_read)`, `DID-matlab:convert/tuningBatchIndex.m:156 (guard)`, `DID-matlab:convert/tuningBatchIndex.m:157 (field_read)`, `DID-matlab:convert/tuningBatchIndex.m:158 (field_read)` ...; MINTED as a document class at 1 site(s), batch post-pass: `DID-matlab:convert/+roundtrip/stimulus_response_scalar.m:140 (emitted_class)`; a block of this name is WRITTEN at 1 site(s), batch post-pass: `DID-matlab:convert/+roundtrip/stimulus_response_scalar.m:165 (field_write)`; NAMED as a string value at 7 site(s), per-document migrator: `DID-matlab:migrators_j/stimulus_response_scalar.m:152 (named)`, `DID-matlab:migrators_j/stimulus_response_scalar.m:157 (named)`, `DID-matlab:migrators_j/stimulus_response_scalar.m:165 (named)`, `DID-matlab:migrators_j/stimulus_response_scalar.m:196 (named)`, `DID-matlab:migrators_j/stimulus_response_scalar.m:309 (named)`, `DID-matlab:migrators_j/stimulus_response_scalar.m:325 (named)` ...; NAMED as a string value at 5 site(s), batch post-pass: `DID-matlab:convert/epochMint.m:1401 (named)`, `DID-matlab:convert/epochMint.m:2374 (named)`, `DID-matlab:convert/rawV1Classes.m:501 (named)`, `DID-matlab:convert/resolveResponseParameters.m:297 (named)`, `DID-matlab:convert/tuningBatchIndex.m:111 (named)`; mentioned in 18 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:982 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:983 (comment_mention)`, `DID-matlab:migrators_j/control_stimulus_ids.m:118 (comment_mention)`, `DID-matlab:migrators_j/private/jResponseRenameCollisions.m:3 (comment_mention)`, `DID-matlab:migrators_j/stimulus_presentation.m:38 (comment_mention)`, `DID-matlab:migrators_j/stimulus_response_scalar.m:103 (comment_mention)` ...; mentioned in 34 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/+roundtrip/stimulus_response_scalar.m:2 (comment_mention)`, `DID-matlab:convert/+roundtrip/stimulus_response_scalar.m:3 (comment_mention)`, `DID-matlab:convert/+roundtrip/stimulus_response_scalar.m:40 (comment_mention)`, `DID-matlab:convert/+roundtrip/stimulus_response_scalar.m:42 (comment_mention)`, `DID-matlab:convert/+roundtrip/stimulus_response_scalar.m:49 (comment_mention)`, `DID-matlab:convert/+roundtrip/stimulus_response_scalar.m:5 (comment_mention)` ...; target(s) BUILT: `calculation + harmonic_component`
- `stimulus_response_scalar_parameters_basic` (decided) -- migrator `DID-matlab:migrators_j/stimulus_response_scalar_parameters_basic.m`; NAMED as a string value at 2 site(s), per-document migrator: `DID-matlab:migrators_j/stimulus_response_scalar_parameters_basic.m:154 (named)`, `DID-matlab:migrators_j/stimulus_response_scalar_parameters_basic.m:163 (named)`; NAMED as a string value at 3 site(s), batch post-pass: `DID-matlab:convert/+roundtrip/stimulus_response_scalar_parameters_basic.m:57 (named)`, `DID-matlab:convert/rawV1Classes.m:502 (named)`, `DID-matlab:convert/resolveResponseParameters.m:296 (named)`; mentioned in 6 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:987 (comment_mention)`, `DID-matlab:migrators_j/private/jResponseRenameCollisions.m:4 (comment_mention)`, `DID-matlab:migrators_j/stimulus_response_scalar_parameters_basic.m:129 (comment_mention)`, `DID-matlab:migrators_j/stimulus_response_scalar_parameters_basic.m:140 (comment_mention)`, `DID-matlab:migrators_j/stimulus_response_scalar_parameters_basic.m:18 (comment_mention)`, `DID-matlab:migrators_j/stimulus_response_scalar_parameters_basic.m:98 (comment_mention)`; mentioned in 14 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/+roundtrip/stimulus_response_scalar_parameters_basic.m:13 (comment_mention)`, `DID-matlab:convert/+roundtrip/stimulus_response_scalar_parameters_basic.m:3 (comment_mention)`, `DID-matlab:convert/+roundtrip/stimulus_response_scalar_parameters_basic.m:50 (comment_mention)`, `DID-matlab:convert/+roundtrip/stimulus_response_scalar_parameters_basic.m:6 (comment_mention)`, `DID-matlab:convert/+roundtrip/stimulus_response_scalar_parameters_basic.m:8 (comment_mention)`, `DID-matlab:convert/rawV1Classes.m:89 (comment_mention)` ...; target(s) BUILT: `method`
- `syncrule` (decided) -- migrator `DID-matlab:migrators_j/syncrule.m`; consumed at 3 site(s), per-document migrator: `DID-matlab:migrators_j/syncrule.m:170 (guard)`, `DID-matlab:migrators_j/syncrule.m:171 (field_read)`, `DID-matlab:migrators_j/syncrule.m:273 (field_read)`; consumed at 5 site(s), batch post-pass: `DID-matlab:convert/resolveClockAlignment.m:355 (guard)`, `DID-matlab:convert/resolveClockAlignment.m:359 (guard)`, `DID-matlab:convert/resolveClockAlignment.m:363 (field_read)`, `DID-matlab:convert/resolveClockAlignment.m:420 (field_read)`, `DID-matlab:convert/resolveClockAlignment.m:421 (guard)`; a block of this name is WRITTEN at 1 site(s), batch post-pass: `DID-matlab:convert/+roundtrip/syncrule.m:117 (field_write)`; NAMED as a string value at 5 site(s), per-document migrator: `DID-matlab:migrators_j/private/jAcquisitionChannels.m:115 (named)`, `DID-matlab:migrators_j/private/jAcquisitionChannels.m:117 (named)`, `DID-matlab:migrators_j/syncrule.m:162 (named)`, `DID-matlab:migrators_j/syncrule.m:164 (named)`, `DID-matlab:migrators_j/syncrule.m:291 (named)`; NAMED as a string value at 2 site(s), batch post-pass: `DID-matlab:convert/+roundtrip/syncrule.m:48 (named)`, `DID-matlab:convert/rawV1Classes.m:513 (named)`; mentioned in 42 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:1014 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:1015 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:504 (comment_mention)`, `DID-matlab:migrators_j/daqsystem.m:99 (comment_mention)`, `DID-matlab:migrators_j/private/jAcquisitionChannels.m:104 (comment_mention)`, `DID-matlab:migrators_j/private/jAcquisitionChannels.m:15 (comment_mention)` ...; mentioned in 21 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/+roundtrip/syncrule.m:19 (comment_mention)`, `DID-matlab:convert/+roundtrip/syncrule.m:2 (comment_mention)`, `DID-matlab:convert/+roundtrip/syncrule.m:20 (comment_mention)`, `DID-matlab:convert/+roundtrip/syncrule.m:4 (comment_mention)`, `DID-matlab:convert/+roundtrip/syncrule.m:41 (comment_mention)`, `DID-matlab:convert/+roundtrip/syncrule.m:5 (comment_mention)` ...; target(s) BUILT: `clock_alignment_configuration`
- `valid_interval` (decided) -- consumed at 2 site(s), batch post-pass: `DID-matlab:convert/resolveValidIntervals.m:637 (guard)`, `DID-matlab:convert/resolveValidIntervals.m:662 (guard)`; NAMED as a string value at 2 site(s), batch post-pass: `DID-matlab:convert/resolveValidIntervals.m:640 (named)`, `DID-matlab:convert/resolveValidIntervals.m:665 (named)`; mentioned in 8 COMMENT(s) -- prose, counts toward nothing, per-document migrator: `DID-matlab:migrators_j/Contents.m:398 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:404 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:412 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:432 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:434 (comment_mention)`, `DID-matlab:migrators_j/Contents.m:461 (comment_mention)` ...; mentioned in 17 COMMENT(s) -- prose, counts toward nothing, batch post-pass: `DID-matlab:convert/resolveValidIntervals.m:1104 (comment_mention)`, `DID-matlab:convert/resolveValidIntervals.m:1111 (comment_mention)`, `DID-matlab:convert/resolveValidIntervals.m:1165 (comment_mention)`, `DID-matlab:convert/resolveValidIntervals.m:1167 (comment_mention)`, `DID-matlab:convert/resolveValidIntervals.m:129 (comment_mention)`, `DID-matlab:convert/resolveValidIntervals.m:144 (comment_mention)` ...; target(s) BUILT: `observation + time`

## Proposed (not decided) -- awaiting review

DENOMINATOR: 21 open class(es); 1 cite no decision line that resolves.

| class | citations that did not resolve |
|---|---|
| `openminds_stimulus` | none recorded |

## Decided, awaiting build -- the open classes

DENOMINATOR: 21 open class(es); 20 cite a decision line that exists. The decision column is the line's own text, not a summary.

| class | targets built | decided in | decision |
|---|---|---|---|
| `acquisition_epoch` | no target recorded | [epoch]. "TEAM-SIGN-OFF [epoch]: jess@walthamdatascience.com /" (did_v2_epoch_plan.md:884). | jess@walthamdatascience.com / 2026-08-08, AMENDED 2026-08-10 -- MINT `epoch` as an entity (one per epoch id, local_identifier = the v1 epochid string, REQUIRED); acquisition_epoch dissolves and its clocks become relat... |
| `app` | 1 of 1 | [software]. "TEAM-SIGN-OFF [software]: jess, 2026-08-06 -- the" (did_v2_tenet_audit.md:16). | jess, 2026-08-06 -- the `app` mixin is replaced by a `software` ENTITY (deduplicated by name+version) referenced from a statement by `software_id`, with the run-specific os / interpreter details in `execution_environm...` |
| `calculator` | no target recorded | [calculator mixin dropped (#73)]. "TEAM-SIGN-OFF [calculator mixin dropped (#73)]" (did_v2_subject_calculation_plan.md:371). | jess@walthamdatascience.com / 2026-09-29 -- (amends #67) the run environment is two `software` edges on `subject_calculation`, `interpreter_id` and `operating_system_id`; `runtime_environment` (and `execution_environm...` |
| `control_stimulus_ids` | no target recorded | [control as covariate]. "Decided by Jess Haley, 2026-10-22 [control as covariate]" (did_v2_stimulus_response_model_plan.md:620). | the control of a stimulus presentation is a `logical` covariate `control condition` (XCO:0000099) along the presentation dimension of the stimulus `item` value (data_body plan AMENDMENT 6): true where the presentation... |
| `daqreader` | 1 of 1 | [daq configuration]. "TEAM-SIGN-OFF [daq configuration]" (did_v2_daq_family_decisions.md:489). | jess@walthamdatascience.com / 2026-08-08 -- daqreader DISSOLVES into a `software` entity (base.id preserved); daqmetadatareader -> `acquisition_metadata_reader`; daqsystem -> `acquisition_system` ⊂ entity, base.id AND... |
| `daqreader_epochdata_ingested` | 1 of 1 | [daq ingested payloads]. "TEAM-SIGN-OFF [daq ingested payloads]" (did_v2_ingested_payload_findings.md:276). | jess@walthamdatascience.com / 2026-08-08 -- ONE new class, `acquisition_metadata_file`; the reader and image classes RETIRE by decomposing into relative_reference + sampled_body + image_observation, all of which are n... |
| `daqreader_image_epochdata_ingested` | 3 of 3 | [daq ingested payloads]. "TEAM-SIGN-OFF [daq ingested payloads]" (did_v2_ingested_payload_findings.md:276). | jess@walthamdatascience.com / 2026-08-08 -- ONE new class, `acquisition_metadata_file`; the reader and image classes RETIRE by decomposing into relative_reference + sampled_body + image_observation, all of which are n... |
| `ensemble` | 3 of 3 | [ensemble]. "TEAM-SIGN-OFF [ensemble]: jess, 2026-08-06 -- per-neuron" (did_v2_ensemble_plan.md:10). | jess, 2026-08-06 -- per-neuron spike times are the PRIMARY archival data (each neuron-subject, event times to a sampled_body); the ensemble is a GROUP SUBJECT with its id preserved and NO data body of its own, whose m... |
| `epochfiles_ingested` | 1 of 1 | [epoch]. "TEAM-SIGN-OFF [epoch]: jess@walthamdatascience.com /" (did_v2_epoch_plan.md:884). | jess@walthamdatascience.com / 2026-08-08, AMENDED 2026-08-10 -- MINT `epoch` as an entity (one per epoch id, local_identifier = the v1 epochid string, REQUIRED); acquisition_epoch dissolves and its clocks become relat... |
| `epochid` | no target recorded | [epoch]. "TEAM-SIGN-OFF [epoch]: jess@walthamdatascience.com /" (did_v2_epoch_plan.md:884). | jess@walthamdatascience.com / 2026-08-08, AMENDED 2026-08-10 -- MINT `epoch` as an entity (one per epoch id, local_identifier = the v1 epochid string, REQUIRED); acquisition_epoch dissolves and its clocks become relat... |
| `filenavigator` | 1 of 1 | [file navigation]. "TEAM-SIGN-OFF [file navigation]: jess, 2026-08-06" (did_v2_daq_family_decisions.md:343). | jess, 2026-08-06 -- filenavigator becomes `epoch_file_pattern` with base.id preserved: the two eval'd parameter strings become declared pattern lists (data_file_pattern, epoch_map_pattern) plus epoch_map_format, and t... |
| `generic_file` | 2 of 2 | [stranded sources]. "TEAM-SIGN-OFF [stranded sources]" (did_v2_OPEN_WORK.md:824). | jess@walthamdatascience.com, 2026-08-11 -- generic_file folds to term_observation + opaque_body; imageCollection is a tombstone. Both are BUILT and ran in 6 of 6 corpora in run 31522068566. THIS SIGNATURE COVERS TWO C... |
| `openminds` | no target recorded | [2026-08-08]. "TEAM-SIGN-OFF: jess, 2026-08-08 -- Part 7: the 3 unattached" (did_v2_openminds_family_record.md:10). | jess, 2026-08-08 -- Part 7: the 3 unattached Strain documents become `strain` entities with their ids preserved and OP50-GFP's pedigree as `background_strain_1`; the other 5 documents are Species/GeneticStrainType fra... |
| `stimulus_presentation` | 2 of 2 | [stimulus]. "TEAM-SIGN-OFF [stimulus]: jess@walthamdatascience.com /" (did_v2_stimulus_model_plan.md:258). | jess@walthamdatascience.com / 2026-08-08 -- `timed_sequence` (a data_type: deduped references to stimulus value documents + an index-array playlist) + `timed_sequence_manipulation` (the leaf); `control_stimulus_ids` -... |
| `stimulus_response` | no target recorded | [stimulus response]. "TEAM-SIGN-OFF [stimulus response]" (did_v2_stimulus_response_model_plan.md:541). | jess@walthamdatascience.com / 2026-08-08 -- four classes to TWO: `harmonic_component` (data_type) + `harmonic_component_calculation` (⊂ subject_calculation, id PRESERVED); stimulus_response and stimulus_response_scala... |
| `stimulus_response_scalar` | 1 of 1 | [stimulus response]. "TEAM-SIGN-OFF [stimulus response]" (did_v2_stimulus_response_model_plan.md:541). | jess@walthamdatascience.com / 2026-08-08 -- four classes to TWO: `harmonic_component` (data_type) + `harmonic_component_calculation` (⊂ subject_calculation, id PRESERVED); stimulus_response and stimulus_response_scala... |
| `stimulus_response_scalar_parameters` | no target recorded | [stimulus response]. "TEAM-SIGN-OFF [stimulus response]" (did_v2_stimulus_response_model_plan.md:541). | jess@walthamdatascience.com / 2026-08-08 -- four classes to TWO: `harmonic_component` (data_type) + `harmonic_component_calculation` (⊂ subject_calculation, id PRESERVED); stimulus_response and stimulus_response_scala... |
| `stimulus_response_scalar_parameters_basic` | 1 of 1 | [stimulus response]. "TEAM-SIGN-OFF [stimulus response]" (did_v2_stimulus_response_model_plan.md:541). | jess@walthamdatascience.com / 2026-08-08 -- four classes to TWO: `harmonic_component` (data_type) + `harmonic_component_calculation` (⊂ subject_calculation, id PRESERVED); stimulus_response and stimulus_response_scala... |
| `syncrule` | 1 of 1 | [sync configuration]. "TEAM-SIGN-OFF [sync configuration]" (did_v2_clock_alignment_cluster_plan.md:506). | jess@walthamdatascience.com / 2026-08-08 -- syncrule -> `clock_alignment_configuration` (parameters DECLARED not bagged, devices become `acquisition_channels_#` edges, EXACTLY 2 and UNORDERED); syncgraph -> `clock_ali...` |
| `valid_interval` | 1 of 1 | [logical_observation]. "TEAM-SIGN-OFF [logical_observation]" (did_v2_logical_observation_plan.md:365). | jess@walthamdatascience.com / 2026-08-12 -- `validity` and `validity_observation` are replaced by `logical` + `logical_observation`; the semantic moves to `subject_statement.variable`, since a data_type names the KIND... |

## Every decision citation

DENOMINATOR: 73 class(es) cite 86 decision line(s); 0 citation(s) do not resolve. "targets built" counts the class's decided targets present in the built set (a target equal to the class is a passthrough and is not counted).

| class | disposition | targets built | decided in |
|---|---|---|---|
| `acquisition_epoch` | retire | no target recorded | [epoch]. "TEAM-SIGN-OFF [epoch]: jess@walthamdatascience.com /" (did_v2_epoch_plan.md:884). |
| `app` | retire | 1 of 1 | [software]. "TEAM-SIGN-OFF [software]: jess, 2026-08-06 -- the" (did_v2_tenet_audit.md:16). |
| `binaryseries_parameters` | consumed by migrator (no tombstone) | 2 of 2 | [misc singletons]. "TEAM-SIGN-OFF [misc singletons]: jess, 2026-08-09" (did_v2_go_forward_class_audit.md:9). |
| `calculator` | retire | no target recorded | [calculator mixin dropped (#73)]. "TEAM-SIGN-OFF [calculator mixin dropped (#73)]" (did_v2_subject_calculation_plan.md:371). |
| `cellTypeLabels` | consumed by migrator (no tombstone) | 4 of 4 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:572). |
| `control_stimulus_ids` | retire | no target recorded | [control as covariate]. "Decided by Jess Haley, 2026-10-22 [control as covariate]" (did_v2_stimulus_response_model_plan.md:620). |
| `daqmetadatareader` | consumed by migrator (no tombstone) | 1 of 1 | [daq configuration]. "TEAM-SIGN-OFF [daq configuration]" (did_v2_daq_family_decisions.md:489). |
| `daqmetadatareader_epochdata_ingested` | consumed by migrator (no tombstone) | 1 of 1 | [daq ingested payloads]. "TEAM-SIGN-OFF [daq ingested payloads]" (did_v2_ingested_payload_findings.md:276). |
| `daqreader` | retire | 1 of 1 | [daq configuration]. "TEAM-SIGN-OFF [daq configuration]" (did_v2_daq_family_decisions.md:489). |
| `daqreader_epochdata_ingested` | retire | 1 of 1 | [daq ingested payloads]. "TEAM-SIGN-OFF [daq ingested payloads]" (did_v2_ingested_payload_findings.md:276).; [epoch files as data bodies]. "Decided by Jess Haley, 2026-10-21 [epoch files as data" (did_v2_recording_observation_plan.md:115). |
| `daqreader_image_epochdata_ingested` | retire | 3 of 3 | [daq ingested payloads]. "TEAM-SIGN-OFF [daq ingested payloads]" (did_v2_ingested_payload_findings.md:276).; [epoch files as data bodies]. "Decided by Jess Haley, 2026-10-21 [epoch files as data" (did_v2_recording_observation_plan.md:115). |
| `daqreader_mfdaq_epochdata_ingested` | consumed by migrator (no tombstone) | 1 of 1 | [epoch files as data bodies]. "Decided by Jess Haley, 2026-10-21 [epoch files as data" (did_v2_recording_observation_plan.md:115). |
| `daqreader_ndr` | consumed by migrator (no tombstone) | 2 of 2 | [daq configuration]. "TEAM-SIGN-OFF [daq configuration]" (did_v2_daq_family_decisions.md:489). |
| `daqsystem` | consumed by migrator (no tombstone) | 1 of 1 | [daq configuration]. "TEAM-SIGN-OFF [daq configuration]" (did_v2_daq_family_decisions.md:489). |
| `element` | consumed by migrator (no tombstone) | 10 of 10 | [raw recording observation]. "TEAM-SIGN-OFF [raw recording observation]" (did_v2_recording_observation_plan.md:99).; [epoch files as data bodies]. "Decided by Jess Haley, 2026-10-21 [epoch files as data" (did_v2_recording_observation_plan.md:115). |
| `element_epoch` | consumed by migrator (no tombstone) | no target recorded | [epoch]. "TEAM-SIGN-OFF [epoch]: jess@walthamdatascience.com /" (did_v2_epoch_plan.md:884). |
| `ensemble` | retire | 3 of 3 | [ensemble]. "TEAM-SIGN-OFF [ensemble]: jess, 2026-08-06 -- per-neuron" (did_v2_ensemble_plan.md:10). |
| `epochclocktimes` | no V_eta home, no migrator -- UNVERIFIED | 1 of 1 | [epochclocktimes]. "TEAM-SIGN-OFF [epochclocktimes]" (did_v2_time_reference_family_plan.md:181).; [epoch extent -- row #113]. "TEAM-SIGN-OFF [epoch extent -- row #113]" (did_v2_OPEN_WORK.md:866). |
| `epochfiles_ingested` | retire | 1 of 1 | [epoch]. "TEAM-SIGN-OFF [epoch]: jess@walthamdatascience.com /" (did_v2_epoch_plan.md:884).; [epoch files as data bodies]. "Decided by Jess Haley, 2026-10-21 [epoch files as data" (did_v2_recording_observation_plan.md:115). |
| `epochid` | retire | no target recorded | [epoch]. "TEAM-SIGN-OFF [epoch]: jess@walthamdatascience.com /" (did_v2_epoch_plan.md:884). |
| `fileReference` | consumed by migrator (no tombstone) | 1 of 1 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:572). |
| `filenavigator` | retire | 1 of 1 | [file navigation]. "TEAM-SIGN-OFF [file navigation]: jess, 2026-08-06" (did_v2_daq_family_decisions.md:343). |
| `filter` | no V_eta home, no migrator -- UNVERIFIED | 1 of 1 | [2026-07-30]. "TEAM-SIGN-OFF: jess, 2026-07-30" (did_v2_frequency_filter_model_plan.md:5).; [filters are methods]. "Decided by Jess Haley, 2026-10-22 [filters are methods]" (did_v2_frequency_filter_model_plan.md:201). |
| `fitcurve` | consumed by migrator (no tombstone) | 1 of 1 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:572). |
| `geneExpression` | consumed by migrator (no tombstone) | no target recorded | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:572). |
| `geneList` | consumed by migrator (no tombstone) | 4 of 4 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:572). |
| `geneListMapping` | consumed by migrator (no tombstone) | 3 of 3 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:572). |
| `generic_file` | retire | 2 of 2 | [stranded sources]. "TEAM-SIGN-OFF [stranded sources]" (did_v2_OPEN_WORK.md:824). |
| `hartley_calc` | consumed by migrator (no tombstone) | 5 of 5 | [receptive field fold]. "TEAM-SIGN-OFF [receptive field fold]" (did_v2_ngrid_family_findings.md:358). |
| `image` | consumed by migrator (no tombstone) | 4 of 4 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:572). |
| `imageCollection` | no V_eta home, no migrator -- UNVERIFIED | no target recorded | [stranded sources]. "TEAM-SIGN-OFF [stranded sources]" (did_v2_OPEN_WORK.md:824).; [carried v1 validates against NDI templates]. "Decided by Jess Haley, 2026-10-27 [carried v1 validates" (did_v2_go_forward_class_audit.md:1496). |
| `imageStack` | consumed by migrator (no tombstone) | 4 of 4 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:572). |
| `imageStack_parameters` | no V_eta home, no migrator -- UNVERIFIED | no target recorded | [image / ngrid]. "TEAM-SIGN-OFF [image / ngrid]: jess@walthamdatascience.com" (did_v2_image_model_plan.md:154). |
| `jrclust_clusters` | consumed by migrator (no tombstone) | 1 of 1 | [confirm sheet 2026-08-17]. "TEAM-SIGN-OFF [confirm sheet 2026-08-17]" (did_v2_go_forward_class_audit.md:723).; [spike-sorter output, amends the 2026-08-17 confirm sheet]. "TEAM-SIGN-OFF [spike-sorter output, amends the 2026-08-17" (did_v2_go_forward_class_audit.md:1023). |
| `kiasort_clusters` | consumed by migrator (no tombstone) | 1 of 1 | [spike-sorter output, amends the 2026-08-17 confirm sheet]. "TEAM-SIGN-OFF [spike-sorter output, amends the 2026-08-17" (did_v2_go_forward_class_audit.md:1023). |
| `kilosort_clusters` | consumed by migrator (no tombstone) | 1 of 1 | [spike-sorter output, amends the 2026-08-17 confirm sheet]. "TEAM-SIGN-OFF [spike-sorter output, amends the 2026-08-17" (did_v2_go_forward_class_audit.md:1023). |
| `lightsheetZarrLevel` | consumed by migrator (no tombstone) | 1 of 1 | [lightsheet migrator points 1-11]. "TEAM-SIGN-OFF [lightsheet migrator points 1-11]" (OPEN_ITEMS.md:317). |
| `lightsheetZarrPyramid` | consumed by migrator (no tombstone) | 3 of 3 | [lightsheet migrator points 1-11]. "TEAM-SIGN-OFF [lightsheet migrator points 1-11]" (OPEN_ITEMS.md:317). |
| `neuron_extracellular` | consumed by migrator (no tombstone) | 7 of 7 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:572). |
| `ngrid` | consumed by migrator (no tombstone) | no target recorded | [image / ngrid]. "TEAM-SIGN-OFF [image / ngrid]: jess@walthamdatascience.com" (did_v2_image_model_plan.md:154). |
| `ontologyImage` | consumed by migrator (no tombstone) | 4 of 4 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:572). |
| `openminds` | retire | no target recorded | [2026-08-08]. "TEAM-SIGN-OFF: jess, 2026-08-08 -- Part 7: the 3 unattached" (did_v2_openminds_family_record.md:10). |
| `oridirtuning_calc` | consumed by migrator (no tombstone) | 3 of 3 | [confirm sheet 2026-08-17]. "TEAM-SIGN-OFF [confirm sheet 2026-08-17]" (did_v2_go_forward_class_audit.md:723). |
| `probe_geometry` | consumed by migrator (no tombstone) | 3 of 3 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:572). |
| `probe_location` | consumed by migrator (no tombstone) | 2 of 2 | [confirm sheet 2026-08-17]. "TEAM-SIGN-OFF [confirm sheet 2026-08-17]" (did_v2_go_forward_class_audit.md:723). |
| `projectvar` | no V_eta home, no migrator -- UNVERIFIED | no target recorded | [misc singletons]. "TEAM-SIGN-OFF [misc singletons]: jess, 2026-08-09" (did_v2_go_forward_class_audit.md:9).; [carried v1 validates against NDI templates]. "Decided by Jess Haley, 2026-10-27 [carried v1 validates" (did_v2_go_forward_class_audit.md:1496). |
| `purpose` | persist | no target recorded | [misc singletons]. "TEAM-SIGN-OFF [misc singletons]: jess, 2026-08-09" (did_v2_go_forward_class_audit.md:9).; [purpose class]. "Decided by Jess Haley, 2026-10-27 [purpose class]: (" (did_v2_go_forward_class_audit.md:1552). |
| `pyraview` | consumed by migrator (no tombstone) | 1 of 1 | [raw recording observation]. "TEAM-SIGN-OFF [raw recording observation]" (did_v2_recording_observation_plan.md:99).; [pyraview levels, amends the 2026-08-13 pyraview pyramid confirmation]. "TEAM-SIGN-OFF [pyraview levels, amends the 2026-08-13" (did_v2_recording_observation_plan.md:111). |
| `session` | consumed by migrator (no tombstone) | 1 of 1 | [session]. "TEAM-SIGN-OFF [session]: jess@walthamdatascience.com /" (did_v2_go_forward_class_audit.md:664). |
| `sorting_parameters` | consumed by migrator (no tombstone) | 1 of 1 | [spike processing parameters]. "TEAM-SIGN-OFF [spike processing parameters]: jess" (did_v2_method_parameters_plan.md:32). |
| `spatialGeneExpressionCells` | consumed by migrator (no tombstone) | 5 of 5 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:572). |
| `spatialGeneExpressionPyramid` | consumed by migrator (no tombstone) | 5 of 5 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:572). |
| `spatialGeneExpressionTiles` | consumed by migrator (no tombstone) | 1 of 1 | [spatial_transcriptomics_family]. "TEAM-SIGN-OFF [spatial_transcriptomics_family]" (did_v2_spatial_transcriptomics_plan.md:572). |
| `spike_extraction_parameters` | consumed by migrator (no tombstone) | 1 of 1 | [spike processing parameters]. "TEAM-SIGN-OFF [spike processing parameters]: jess" (did_v2_method_parameters_plan.md:32). |
| `spike_extraction_parameters_modification` | consumed by migrator (no tombstone) | 1 of 1 | [spike processing parameters]. "TEAM-SIGN-OFF [spike processing parameters]: jess" (did_v2_method_parameters_plan.md:32). |
| `stimulus_bath` | consumed by migrator (no tombstone) | 2 of 2 | [bath is a manipulation]. "Decided by Jess Haley, 2026-10-21 [bath is a manipulation]" (did_v2_go_forward_class_audit.md:727). |
| `stimulus_parameter` | consumed by migrator (no tombstone) | no target recorded | [stimulus parameters]. "TEAM-SIGN-OFF [stimulus parameters]" (did_v2_stimulus_parameter_plan.md:221). |
| `stimulus_parameter_table` | no V_eta home, no migrator -- UNVERIFIED | no target recorded | [stimulus parameters]. "TEAM-SIGN-OFF [stimulus parameters]" (did_v2_stimulus_parameter_plan.md:221).; [carried v1 validates against NDI templates]. "Decided by Jess Haley, 2026-10-27 [carried v1 validates" (did_v2_go_forward_class_audit.md:1496). |
| `stimulus_presentation` | retire | 2 of 2 | [stimulus]. "TEAM-SIGN-OFF [stimulus]: jess@walthamdatascience.com /" (did_v2_stimulus_model_plan.md:258). |
| `stimulus_response` | retire | no target recorded | [stimulus response]. "TEAM-SIGN-OFF [stimulus response]" (did_v2_stimulus_response_model_plan.md:541). |
| `stimulus_response_scalar` | retire | 1 of 1 | [stimulus response]. "TEAM-SIGN-OFF [stimulus response]" (did_v2_stimulus_response_model_plan.md:541). |
| `stimulus_response_scalar_parameters` | retire | no target recorded | [stimulus response]. "TEAM-SIGN-OFF [stimulus response]" (did_v2_stimulus_response_model_plan.md:541). |
| `stimulus_response_scalar_parameters_basic` | retire | 1 of 1 | [stimulus response]. "TEAM-SIGN-OFF [stimulus response]" (did_v2_stimulus_response_model_plan.md:541). |
| `subject` | consumed by migrator (no tombstone) | 1 of 1 | [subject]. "TEAM-SIGN-OFF [subject]: jess@walthamdatascience.com /" (did_v2_go_forward_class_audit.md:697). |
| `subjectmeasurement` | consumed by migrator (no tombstone) | no target recorded | [subject measurement]. "TEAM-SIGN-OFF [subject measurement]: jess, 2026-08-06" (did_v2_go_forward_class_audit.md:336). |
| `syncgraph` | consumed by migrator (no tombstone) | 1 of 1 | [sync configuration]. "TEAM-SIGN-OFF [sync configuration]" (did_v2_clock_alignment_cluster_plan.md:506). |
| `syncrule` | retire | 1 of 1 | [sync configuration]. "TEAM-SIGN-OFF [sync configuration]" (did_v2_clock_alignment_cluster_plan.md:506). |
| `syncrule_mapping` | consumed by migrator (no tombstone) | 1 of 1 | [sync mapping]. "TEAM-SIGN-OFF [sync mapping]: jess@walthamdatascience.com /" (did_v2_clock_alignment_cluster_plan.md:508). |
| `treatment` | consumed by migrator (no tombstone) | 7 of 7 | [confirm sheet 2026-08-17]. "TEAM-SIGN-OFF [confirm sheet 2026-08-17]" (did_v2_go_forward_class_audit.md:723). |
| `tuningcurve_calc` | consumed by migrator (no tombstone) | 3 of 3 | [confirm sheet 2026-08-17]. "TEAM-SIGN-OFF [confirm sheet 2026-08-17]" (did_v2_go_forward_class_audit.md:723). |
| `valid_interval` | retire | 1 of 1 | [logical_observation]. "TEAM-SIGN-OFF [logical_observation]" (did_v2_logical_observation_plan.md:365).; [logical_observation amendment 1]. "TEAM-SIGN-OFF [logical_observation amendment 1]" (did_v2_logical_observation_plan.md:425). |
| `vmspikefilteringparameters` | consumed by migrator (no tombstone) | 1 of 1 | [spike processing parameters]. "TEAM-SIGN-OFF [spike processing parameters]: jess" (did_v2_method_parameters_plan.md:32). |
| `vmspikefit` | consumed by migrator (no tombstone) | 1 of 1 | [#73 audit 2, D1-D13]. "TEAM-SIGN-OFF [#73 audit 2, D1-D13]" (did_v2_spatial_transcriptomics_plan.md:574). |

Every decided target these classes name is present in the built set, so
what remains for them is MIGRATOR work, not schema work.

## Decision lines no class cites

DENOMINATOR: 121 document(s) read (3 generated copies excluded); 620 decision line(s) accepted, 2 rejected; 44 cited by a class, 576 cited by none.

An uncited line is a decision the record holds that no class points at.
Most decide something that is not one class (a tenet, a naming rule, a
field). If one decides a class's disposition, that class should cite it.

- lightsheet reader questions R1-R6. "TEAM-SIGN-OFF [lightsheet reader questions R1-R6]" (OPEN_ITEMS.md:349).
- developed_by, hosted_by, distributed_as. "TEAM-SIGN-OFF [developed_by, hosted_by, distributed_as]" (OPEN_ITEMS.md:362).
- sync configuration amendment 1. "TEAM-SIGN-OFF [sync configuration amendment 1]" (did_v2_clock_alignment_cluster_plan.md:638).
- data_body. "TEAM-SIGN-OFF [data_body]: jess@walthamdatascience.com /" (did_v2_data_body_model_plan.md:673).
- data_body amendment 4. "TEAM-SIGN-OFF [data_body amendment 4]" (did_v2_data_body_model_plan.md:1287).
- data_body amendment 3. "TEAM-SIGN-OFF [data_body amendment 3]" (did_v2_data_body_model_plan.md:1325).
- data_type only for plain arrays. "Decided by Jess Haley, 2026-10-21 [data_type only for plain" (did_v2_data_body_model_plan.md:1343).
- data_body amendment 5. "TEAM-SIGN-OFF [data_body amendment 5]" (did_v2_data_body_model_plan.md:1398).
- sorter output by location. "Decided by Jess Haley, 2026-10-21 [sorter output by" (did_v2_data_body_model_plan.md:1402).
- format is an ontology term. "Decided by Jess Haley, 2026-10-14 [format is an ontology" (did_v2_data_body_model_plan.md:1404).
- NDI binary format. "Decided by Jess Haley, 2026-10-22 [NDI binary format]: the" (did_v2_data_body_model_plan.md:1406).
- covariates. "Decided by Jess Haley, 2026-10-22 [covariates]" (did_v2_data_body_model_plan.md:1475).
- conditions stay on the statement. "Decided by Jess Haley, 2026-10-22 [conditions stay on the" (did_v2_data_body_model_plan.md:1477).
- along by index. "Decided by Jess Haley, 2026-10-22 [along by index]" (did_v2_data_body_model_plan.md:1479).
- matrix covariate. "Decided by Jess Haley, 2026-10-22 [matrix covariate]: a" (did_v2_data_body_model_plan.md:1481).
- onset time. "Decided by Jess Haley, 2026-10-22 [onset time]: a stimulus" (did_v2_data_body_model_plan.md:1483).
- no complete. "Decided by Jess Haley, 2026-10-22 [no complete]" (did_v2_data_body_model_plan.md:1485).
- bare dimension. "Decided by Jess Haley, 2026-10-22 [bare dimension]: a" (did_v2_data_body_model_plan.md:1487).
- epoch covariates. "Decided by Jess Haley, 2026-10-22 [epoch covariates]" (did_v2_data_body_model_plan.md:1489).
- tenets follow covariates. "Decided by Jess Haley, 2026-10-22 [tenets follow" (did_v2_data_body_model_plan.md:1491).
- covariate terms. "Decided by Jess Haley, 2026-10-22 [covariate terms]: terms" (did_v2_data_body_model_plan.md:1493).
- presentation dimension term. "Decided by Jess Haley, 2026-10-22 [presentation dimension" (did_v2_data_body_model_plan.md:1497).
- onset and offset terms. "Decided by Jess Haley, 2026-10-22 [onset and offset terms]" (did_v2_data_body_model_plan.md:1499).
- row term deferred. "Decided by Jess Haley, 2026-10-22 [row term deferred]: the" (did_v2_data_body_model_plan.md:1501).
- tuning grid. "Decided by Jess Haley, 2026-10-22 [tuning grid]: a tuning" (did_v2_data_body_model_plan.md:1503).
- covariate details. "Decided by Jess Haley, 2026-10-22 [covariate details]" (did_v2_data_body_model_plan.md:1505).
- covariate rules named. "Decided by Jess Haley, 2026-10-22 [covariate rules named]" (did_v2_data_body_model_plan.md:1507).
- stimulus condition term. "Decided by Jess Haley, 2026-10-22 [stimulus condition" (did_v2_data_body_model_plan.md:1509).
- index covariates. "Decided by Jess Haley, 2026-10-22 [index covariates]: a" (did_v2_data_body_model_plan.md:1511).
- units bound. "Decided by Jess Haley, 2026-10-22 [units bound]" (did_v2_data_body_model_plan.md:1515).
- remaining units bound. "Decided by Jess Haley, 2026-10-22 [remaining units bound]" (did_v2_data_body_model_plan.md:1517).
- logical entries. "Decided by Jess Haley, 2026-10-22 [logical entries]: the" (did_v2_data_body_model_plan.md:1519).
- irradiance. "Decided by Jess Haley, 2026-10-22 [irradiance]: a new" (did_v2_data_body_model_plan.md:1521).
- ratio slots named by unit. "Decided by Jess Haley, 2026-10-22 [ratio slots named by" (did_v2_data_body_model_plan.md:1523).
- missing integers. "Decided by Jess Haley, 2026-10-22 [missing integers]" (did_v2_data_body_model_plan.md:1525).
- audit mechanical fixes 2. "Decided by Jess Haley, 2026-10-22 [audit mechanical fixes" (did_v2_data_body_model_plan.md:1527).
- audit mechanical fixes. "Decided by Jess Haley, 2026-10-22 [audit mechanical fixes]" (did_v2_data_body_model_plan.md:1531).
- harmonic response unit bound. "Decided by Jess Haley, 2026-10-22 [harmonic response unit" (did_v2_data_body_model_plan.md:1533).
- response variable. "Decided by Jess Haley, 2026-10-22 [response variable]: what" (did_v2_data_body_model_plan.md:1535).
- dF/F as variable. "Decided by Jess Haley, 2026-10-22 [dF/F as variable]: dF/F" (did_v2_data_body_model_plan.md:1537).
- response variable nodes. "Decided by Jess Haley, 2026-10-22 [response variable" (did_v2_data_body_model_plan.md:1539).
- unstated response variable. "Decided by Jess Haley, 2026-10-23 [unstated response" (did_v2_data_body_model_plan.md:1541).
- pressure in mmHg. "Decided by Jess Haley, 2026-10-22 [pressure in mmHg]: the" (did_v2_data_body_model_plan.md:1543).
- pH unit one. "Decided by Jess Haley, 2026-10-22 [pH unit one]: the" (did_v2_data_body_model_plan.md:1545).
- pH unit is UO pH. "Decided by Jess Haley, 2026-10-22 [pH unit is UO pH]: the" (did_v2_data_body_model_plan.md:1547).
- humidity in percent. "Decided by Jess Haley, 2026-10-22 [humidity in percent]: the" (did_v2_data_body_model_plan.md:1549).
- unit names are labels. "Decided by Jess Haley, 2026-10-22 [unit names are labels]" (did_v2_data_body_model_plan.md:1551).
- molar kept. "Decided by Jess Haley, 2026-10-22 [molar kept]: the" (did_v2_data_body_model_plan.md:1553).
- exact OM units. "Decided by Jess Haley, 2026-10-22 [exact OM units]: the" (did_v2_data_body_model_plan.md:1555).
- prefixed source units. "Decided by Jess Haley, 2026-10-22 [prefixed source units]" (did_v2_data_body_model_plan.md:1557).
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
- classes without a migrator carry as v1. "Decided by Jess Haley, 2026-10-31 [classes without a" (did_v2_go_forward_class_audit.md:1260).
- early migration pieces fixed. "Decided by Jess Haley, 2026-10-26 [early migration pieces" (did_v2_go_forward_class_audit.md:1262).
- migration reliability practices. "Decided by Jess Haley, 2026-10-26 [migration reliability" (did_v2_go_forward_class_audit.md:1264).
- carry register kinds 2. "Decided by Jess Haley, 2026-10-26 [carry register kinds 2]" (did_v2_go_forward_class_audit.md:1266).
- unnamed groups named by the map. "Decided by Jess Haley, 2026-10-26 [unnamed groups named by" (did_v2_go_forward_class_audit.md:1268).
- vehicle rate needs a map. "Decided by Jess Haley, 2026-10-26 [vehicle rate needs a" (did_v2_go_forward_class_audit.md:1270).
- second measurement value needs a map. "Decided by Jess Haley, 2026-10-26 [second measurement value" (did_v2_go_forward_class_audit.md:1272).
- ingested session membership. "Decided by Jess Haley, 2026-10-26 [ingested session" (did_v2_go_forward_class_audit.md:1274).
- data_limits not a pair is malformed. "Decided by Jess Haley, 2026-10-26 [data_limits not a pair" (did_v2_go_forward_class_audit.md:1276).
- pass-through filter sample frequency. "Decided by Jess Haley, 2026-10-26 [pass-through filter" (did_v2_go_forward_class_audit.md:1278).
- untied epochs keep the session anchor. "Decided by Jess Haley, 2026-10-26 [untied epochs keep the" (did_v2_go_forward_class_audit.md:1280).
- sorted units are cells or groups. "Decided by Jess Haley, 2026-10-26 [sorted units are cells" (did_v2_go_forward_class_audit.md:1282).
- unlabelled units need a map. "Decided by Jess Haley, 2026-10-26 [unlabelled units need a" (did_v2_go_forward_class_audit.md:1284).
- element types have no default. "Decided by Jess Haley, 2026-10-26 [element types have no" (did_v2_go_forward_class_audit.md:1286).
- dependents of a carried document carry. "Decided by Jess Haley, 2026-10-26 [dependents of a carried" (did_v2_go_forward_class_audit.md:1288).
- electrode spellings and imaging types are devices. "Decided by Jess Haley, 2026-10-26 [electrode spellings and" (did_v2_go_forward_class_audit.md:1290).
- event lines and environment probes are devices. "Decided by Jess Haley, 2026-10-26 [event lines and" (did_v2_go_forward_class_audit.md:1292).
- migrator writes the registry spelling. "Decided by Jess Haley, 2026-10-26 [migrator writes the" (did_v2_go_forward_class_audit.md:1294).
- location carries need a map. "Decided by Jess Haley, 2026-10-26 [location carries need a" (did_v2_go_forward_class_audit.md:1296).
- presentation outside the batch needs a map. "Decided by Jess Haley, 2026-10-26 [presentation outside the" (did_v2_go_forward_class_audit.md:1298).
- missing is_linked is malformed. "Decided by Jess Haley, 2026-10-26 [missing is_linked is" (did_v2_go_forward_class_audit.md:1300).
- term labels stay as the ontology spells them. "Decided by Jess Haley, 2026-10-26 [term labels stay as the" (did_v2_go_forward_class_audit.md:1302).
- element local identifier is name and reference. "Decided by Jess Haley, 2026-10-26 [element local identifier" (did_v2_go_forward_class_audit.md:1304).
- bath is two statements. "Decided by Jess Haley, 2026-10-26 [bath is two statements]" (did_v2_go_forward_class_audit.md:1306).
- chooseLevel skips empty levels. "Decided by Jess Haley, 2026-10-26 [chooseLevel skips empty" (did_v2_go_forward_class_audit.md:1308).
- ingested stimulus reader finds the body. "Decided by Jess Haley, 2026-10-26 [ingested stimulus reader" (did_v2_go_forward_class_audit.md:1310).
- markdown cleanup and rename. "Decided by Jess Haley, 2026-10-26 [markdown cleanup and" (did_v2_go_forward_class_audit.md:1312).
- pipeline defects are not carries. "Decided by Jess Haley, 2026-10-26 [pipeline defects are not" (did_v2_go_forward_class_audit.md:1314).
- unresolved recorded elements make a standalone item. "Decided by Jess Haley, 2026-10-26 [unresolved recorded" (did_v2_go_forward_class_audit.md:1316).
- extra field on an ingested stimulus file is malformed. "Decided by Jess Haley, 2026-10-26 [extra field on an" (did_v2_go_forward_class_audit.md:1318).
- NaN control means no control. "Decided by Jess Haley, 2026-10-26 [NaN control means no" (did_v2_go_forward_class_audit.md:1320).
- conflicting animal records need a map. "Decided by Jess Haley, 2026-10-26 [conflicting animal" (did_v2_go_forward_class_audit.md:1322).
- method terms are general. "Decided by Jess Haley, 2026-10-26 [method terms are" (did_v2_go_forward_class_audit.md:1324).
- Naka-Rushton is one function. "Decided by Jess Haley, 2026-10-26 [Naka-Rushton is one" (did_v2_go_forward_class_audit.md:1326).
- fields outside the template are malformed. "Decided by Jess Haley, 2026-10-27 [fields outside the" (did_v2_go_forward_class_audit.md:1328).
- probe location terms. "Decided by Jess Haley, 2026-10-27 [probe location terms]: (" (did_v2_go_forward_class_audit.md:1330).
- cell spellings are one meaning. "Decided by Jess Haley, 2026-10-27 [cell spellings are one" (did_v2_go_forward_class_audit.md:1332).
- v1 name is the entity name. "Decided by Jess Haley, 2026-10-27 [v1 name is the entity" (did_v2_go_forward_class_audit.md:1334).
- member edge number is notation. "Decided by Jess Haley, 2026-10-27 [member edge number is" (did_v2_go_forward_class_audit.md:1336).
- afo prefix registered. "Decided by Jess Haley, 2026-10-27 [afo prefix registered]: (" (did_v2_go_forward_class_audit.md:1338).
- n-trode is a multielectrode array. "Decided by Jess Haley, 2026-10-27 [n-trode is a" (did_v2_go_forward_class_audit.md:1340).
- site positions are coordinates. "Decided by Jess Haley, 2026-10-27 [site positions are" (did_v2_go_forward_class_audit.md:1342).
- move the locked mains. "Decided by Jess Haley, 2026-10-27 [move the locked mains]: (" (did_v2_go_forward_class_audit.md:1344).
- merge main into V2. "Decided by Jess Haley, 2026-10-27 [merge main into V2]: (" (did_v2_go_forward_class_audit.md:1346).
- lock NDIcalc-vis-matlab. "Decided by Jess Haley, 2026-10-27 [lock" (did_v2_go_forward_class_audit.md:1348).
- tuning stray fields are malformed. "Decided by Jess Haley, 2026-10-27 [tuning stray fields are" (did_v2_go_forward_class_audit.md:1350).
- cell spellings amended. "Decided by Jess Haley, 2026-10-27 [cell spellings amended]" (did_v2_go_forward_class_audit.md:1352).
- element type is a device kind term. "Decided by Jess Haley, 2026-10-27 [element type is a device" (did_v2_go_forward_class_audit.md:1354).
- ndi element class not kept. "Decided by Jess Haley, 2026-10-27 [ndi element class not" (did_v2_go_forward_class_audit.md:1356).
- number of electrodes minted. "Decided by Jess Haley, 2026-10-27 [number of electrodes" (did_v2_go_forward_class_audit.md:1358).
- site frame is a coordinate system. "Decided by Jess Haley, 2026-10-27 [site frame is a" (did_v2_go_forward_class_audit.md:1360).
- ground truth reads NDIcalc-vis templates. "Decided by Jess Haley, 2026-10-27 [ground truth reads" (did_v2_go_forward_class_audit.md:1362).
- writer fields over the template are template fields. "Decided by Jess Haley, 2026-10-27 [writer fields over the" (did_v2_go_forward_class_audit.md:1364).
- tuning split covers the shared fold. "Decided by Jess Haley, 2026-10-27 [tuning split covers the" (did_v2_go_forward_class_audit.md:1366).
- unreached superclass migrators deleted. "Decided by Jess Haley, 2026-10-27 [unreached superclass" (did_v2_go_forward_class_audit.md:1368).
- unknown filter parameter is malformed. "Decided by Jess Haley, 2026-10-27 [unknown filter parameter" (did_v2_go_forward_class_audit.md:1370).
- five probe kinds from NCIT. "Decided by Jess Haley, 2026-10-27 [five probe kinds from" (did_v2_go_forward_class_audit.md:1372).
- ecg and eeg are recorders. "Decided by Jess Haley, 2026-10-27 [ecg and eeg are" (did_v2_go_forward_class_audit.md:1374).
- imaging probes are microscopes or carried. "Decided by Jess Haley, 2026-10-27 [imaging probes are" (did_v2_go_forward_class_audit.md:1376).
- pyraview level keeps its file info. "Decided by Jess Haley, 2026-10-27 [pyraview level keeps its" (did_v2_go_forward_class_audit.md:1378).
- values no writer produces are malformed. "Decided by Jess Haley, 2026-10-27 [values no writer" (did_v2_go_forward_class_audit.md:1380).
- carried file references are not folded. "Decided by Jess Haley, 2026-10-27 [carried file references" (did_v2_go_forward_class_audit.md:1382).
- light-sheet level fields rebuild from the pyramid. "Decided by Jess Haley, 2026-10-27 [light-sheet level fields" (did_v2_go_forward_class_audit.md:1384).
- one bath shape. "Decided by Jess Haley, 2026-10-27 [one bath shape]: (" (did_v2_go_forward_class_audit.md:1386).
- group identifier includes the reference. "Decided by Jess Haley, 2026-10-27 [group identifier" (did_v2_go_forward_class_audit.md:1388).
- drug end and duration on the anchor. "Decided by Jess Haley, 2026-10-27 [drug end and duration on" (did_v2_go_forward_class_audit.md:1390).
- age at injection is an observation. "Decided by Jess Haley, 2026-10-27 [age at injection is an" (did_v2_go_forward_class_audit.md:1392).
- transfer method keeps its node. "Decided by Jess Haley, 2026-10-27 [transfer method keeps" (did_v2_go_forward_class_audit.md:1394).
- sync configuration stays a class. "Decided by Jess Haley, 2026-10-27 [sync configuration stays" (did_v2_go_forward_class_audit.md:1396).
- sync configuration links its rigs. "Decided by Jess Haley, 2026-10-27 [sync configuration links" (did_v2_go_forward_class_audit.md:1398).
- sync rule direction is recorded. "Decided by Jess Haley, 2026-10-27 [sync rule direction is" (did_v2_go_forward_class_audit.md:1400).
- acquisition channels kept for wiring. "Decided by Jess Haley, 2026-10-27 [acquisition channels" (did_v2_go_forward_class_audit.md:1402).
- handed-on documents do not carry dependents. "Decided by Jess Haley, 2026-10-27 [handed-on documents do" (did_v2_go_forward_class_audit.md:1404).
- unit direct and subject rebuild from the probe. "Decided by Jess Haley, 2026-10-27 [unit direct and subject" (did_v2_go_forward_class_audit.md:1406).
- broken transfer values are malformed. "Decided by Jess Haley, 2026-10-27 [broken transfer values" (did_v2_go_forward_class_audit.md:1408).
- treatment transfer stays v1. "Decided by Jess Haley, 2026-10-27 [treatment transfer stays" (did_v2_go_forward_class_audit.md:1410).
- bath ph and osmolarity are formulation fields. "Decided by Jess Haley, 2026-10-27 [bath ph and osmolarity" (did_v2_go_forward_class_audit.md:1412).
- light-sheet level label is a note. "Decided by Jess Haley, 2026-10-27 [light-sheet level label" (did_v2_go_forward_class_audit.md:1414).
- unreadable responses are malformed. "Decided by Jess Haley, 2026-10-27 [unreadable responses are" (did_v2_go_forward_class_audit.md:1416).
- unbuilt spike classes carry as needs home. "Decided by Jess Haley, 2026-10-27 [unbuilt spike classes" (did_v2_go_forward_class_audit.md:1418).
- input names rebuild from the input class. "Decided by Jess Haley, 2026-10-27 [input names rebuild from" (did_v2_go_forward_class_audit.md:1420).
- neuron uses the sorted unit's cell. "Decided by Jess Haley, 2026-10-27 [neuron uses the sorted" (did_v2_go_forward_class_audit.md:1422).
- sample times equal within one rounding step. "Decided by Jess Haley, 2026-10-27 [sample times equal" (did_v2_go_forward_class_audit.md:1424).
- contrast SF bug is a dataset decision. "Decided by Jess Haley, 2026-10-27 [contrast SF bug is a" (did_v2_go_forward_class_audit.md:1426).
- whole-batch round trip. "Decided by Jess Haley, 2026-10-27 [whole-batch round trip]" (did_v2_go_forward_class_audit.md:1428).
- carried documents may point at converted ones. "Decided by Jess Haley, 2026-10-27 [carried documents may" (did_v2_go_forward_class_audit.md:1430).
- simple_calc carries as needs home. "Decided by Jess Haley, 2026-10-27 [simple_calc carries as" (did_v2_go_forward_class_audit.md:1432).
- empty prestimulus normalization is zero. "Decided by Jess Haley, 2026-10-27 [empty prestimulus" (did_v2_go_forward_class_audit.md:1434).
- importer bugs are dataset decisions. "Decided by Jess Haley, 2026-10-27 [importer bugs are" (did_v2_go_forward_class_audit.md:1436).
- hotelling spellings are one field. "Decided by Jess Haley, 2026-10-27 [hotelling spellings are" (did_v2_go_forward_class_audit.md:1438).
- Priebe fits are one function. "Decided by Jess Haley, 2026-10-27 [Priebe fits are one" (did_v2_go_forward_class_audit.md:1440).
- NDI CI picks did-schema branch. "Decided by Jess Haley, 2026-10-27 [NDI CI picks did-schema" (did_v2_go_forward_class_audit.md:1442).
- sorter labels map. "Decided by Jess Haley, 2026-10-27 [sorter labels map]: (" (did_v2_go_forward_class_audit.md:1444).
- image stack name goes to notes. "Decided by Jess Haley, 2026-10-27 [image stack name goes to" (did_v2_go_forward_class_audit.md:1446).
- carry-055 wording follows the group identifier. "Decided by Jess Haley, 2026-10-27 [carry-055 wording" (did_v2_go_forward_class_audit.md:1448).
- treatment location name is the node. "Decided by Jess Haley, 2026-10-27 [treatment location name" (did_v2_go_forward_class_audit.md:1450).
- ingested stimulus body link follow-up. "Decided by Jess Haley, 2026-10-27 [ingested stimulus body" (did_v2_go_forward_class_audit.md:1452).
- cloud organization id is a global identifier. "Decided by Jess Haley, 2026-10-27 [cloud organization id is" (did_v2_go_forward_class_audit.md:1454).
- curve fitting is the fit method term. "Decided by Jess Haley, 2026-10-27 [curve fitting is the fit" (did_v2_go_forward_class_audit.md:1456).
- bath solution minted. "Decided by Jess Haley, 2026-10-27 [bath solution minted]: (" (did_v2_go_forward_class_audit.md:1458).
- second pass reads control stimuli from v1. "Decided by Jess Haley, 2026-10-27 [second pass reads" (did_v2_go_forward_class_audit.md:1460).
- tuning fits use curve fitting now. "Decided by Jess Haley, 2026-10-27 [tuning fits use curve" (did_v2_go_forward_class_audit.md:1462).
- presentation anchored to its epoch. "Decided by Jess Haley, 2026-10-27 [presentation anchored to" (did_v2_go_forward_class_audit.md:1464).
- response links: epoch rebuilt, control as input. "Decided by Jess Haley, 2026-10-27 [response links: epoch" (did_v2_go_forward_class_audit.md:1466).
- openMINDS subject leftovers. "Decided by Jess Haley, 2026-10-27 [openMINDS subject" (did_v2_go_forward_class_audit.md:1468).
- term equivalents recorded. "Decided by Jess Haley, 2026-10-27 [term equivalents" (did_v2_go_forward_class_audit.md:1470).
- dataset form lists carried until homed. "Decided by Jess Haley, 2026-10-27 [dataset form lists" (did_v2_go_forward_class_audit.md:1472).
- old ndi_document blocks carry. "Decided by Jess Haley, 2026-10-27 [old ndi_document blocks" (did_v2_go_forward_class_audit.md:1474).
- tuning stimids rebuild. "Decided by Jess Haley, 2026-10-27 [tuning stimids rebuild]" (did_v2_go_forward_class_audit.md:1476).
- tuning log in notes. "Decided by Jess Haley, 2026-10-27 [tuning log in notes]: (" (did_v2_go_forward_class_audit.md:1478).
- varied properties are conditions by V2 name. "Decided by Jess Haley, 2026-10-27 [varied properties are" (did_v2_go_forward_class_audit.md:1480).
- absolute-value fits are a second calculation. "Decided by Jess Haley, 2026-10-27 [absolute-value fits are" (did_v2_go_forward_class_audit.md:1482).
- contrast metrics added. "Decided by Jess Haley, 2026-10-27 [contrast metrics added]" (did_v2_go_forward_class_audit.md:1484).
- parameter names map by table. "Decided by Jess Haley, 2026-10-27 [parameter names map by" (did_v2_go_forward_class_audit.md:1486).
- E. coli stacks are a dataset decision. "Decided by Jess Haley, 2026-10-27 [E" (did_v2_go_forward_class_audit.md:1488).
- every v1 id survives. "Decided by Jess Haley, 2026-10-27 [every v1 id survives]: (" (did_v2_go_forward_class_audit.md:1490).
- axis letters derive from labels. "Decided by Jess Haley, 2026-10-27 [axis letters derive from" (did_v2_go_forward_class_audit.md:1492).
- v1 name goes to the class's own name field. "Decided by Jess Haley, 2026-10-27 [v1 name goes to the" (did_v2_go_forward_class_audit.md:1494).
- base.name kept until retire classes leave. "Decided by Jess Haley, 2026-10-29 [base.name kept until" (did_v2_go_forward_class_audit.md:1498).
- treatment groups are a dataset decision. "Decided by Jess Haley, 2026-10-27 [treatment groups are a" (did_v2_go_forward_class_audit.md:1500).
- fit classes kept; session list rebuilt. "Decided by Jess Haley, 2026-10-27 [fit classes kept" (did_v2_go_forward_class_audit.md:1502).
- event lines are event channels. "Decided by Jess Haley, 2026-10-27 [event lines are event" (did_v2_go_forward_class_audit.md:1504).
- labels are a field on what they label. "Decided by Jess Haley, 2026-10-27 [labels are a field on" (did_v2_go_forward_class_audit.md:1506).
- ontologyLabel row split. "Decided by Jess Haley, 2026-10-27 [ontologyLabel row" (did_v2_go_forward_class_audit.md:1508).
- openMINDS strain leftovers. "Decided by Jess Haley, 2026-10-27 [openMINDS strain" (did_v2_go_forward_class_audit.md:1510).
- control pairing points at the presentation. "Decided by Jess Haley, 2026-10-27 [control pairing points" (did_v2_go_forward_class_audit.md:1512).
- control record fields split. "Decided by Jess Haley, 2026-10-27 [control record fields" (did_v2_go_forward_class_audit.md:1514).
- unread stimulus parameters are method parameters. "Decided by Jess Haley, 2026-10-27 [unread stimulus" (did_v2_go_forward_class_audit.md:1516).
- session opener inputs. "Decided by Jess Haley, 2026-10-27 [session opener inputs]: (" (did_v2_go_forward_class_audit.md:1518).
- linked session reference follows the ingested rule. "Decided by Jess Haley, 2026-10-27 [linked session reference" (did_v2_go_forward_class_audit.md:1520).
- one affiliation relation each. "Decided by Jess Haley, 2026-10-27 [one affiliation relation" (did_v2_go_forward_class_audit.md:1522).
- position and its metadata are one statement. "Decided by Jess Haley, 2026-10-27 [position and its" (did_v2_go_forward_class_audit.md:1524).
- image stack link needs mapping. "Decided by Jess Haley, 2026-10-27 [image stack link needs" (did_v2_go_forward_class_audit.md:1526).
- image label goes to notes. "Decided by Jess Haley, 2026-10-27 [image label goes to" (did_v2_go_forward_class_audit.md:1528).
- hartley labels stay carried. "Decided by Jess Haley, 2026-10-27 [hartley labels stay" (did_v2_go_forward_class_audit.md:1530).
- filter label is the method name. "Decided by Jess Haley, 2026-10-27 [filter label is the" (did_v2_go_forward_class_audit.md:1532).
- contact geometry stays carried. "Decided by Jess Haley, 2026-10-27 [contact geometry stays" (did_v2_go_forward_class_audit.md:1534).
- scanner test issue closed. "Decided by Jess Haley, 2026-10-27 [scanner test issue" (did_v2_go_forward_class_audit.md:1536).
- old EMPTY labels generalised. "Decided by Jess Haley, 2026-10-27 [old EMPTY labels" (did_v2_go_forward_class_audit.md:1538).
- no about edge for now. "Decided by Jess Haley, 2026-10-27 [no about edge for now]: (" (did_v2_go_forward_class_audit.md:1540).
- old table rows counted and carried. "Decided by Jess Haley, 2026-10-27 [old table rows counted" (did_v2_go_forward_class_audit.md:1542).
- binaryseries parameters fold as decided. "Decided by Jess Haley, 2026-10-27 [binaryseries parameters" (did_v2_go_forward_class_audit.md:1544).
- Guard A amended. "Decided by Jess Haley, 2026-10-27 [Guard A amended]: (" (did_v2_go_forward_class_audit.md:1546).
- documents without base carry. "Decided by Jess Haley, 2026-10-27 [documents without base" (did_v2_go_forward_class_audit.md:1548).
- oneepoch is a redundant calculation. "Decided by Jess Haley, 2026-10-27 [oneepoch is a redundant" (did_v2_go_forward_class_audit.md:1550).
- redeclarations only narrow. "Decided by Jess Haley, 2026-10-27 [redeclarations only" (did_v2_go_forward_class_audit.md:1554).
- no value rollup now. "Decided by Jess Haley, 2026-10-27 [no value rollup now]: (" (did_v2_go_forward_class_audit.md:1556).
- ngrid migrates to sampled bodies. "Decided by Jess Haley, 2026-10-27 [ngrid migrates to" (did_v2_go_forward_class_audit.md:1558).
- allowed units are closed source_unit lists. "Decided by Jess Haley, 2026-10-27 [allowed units are closed" (did_v2_go_forward_class_audit.md:1560).
- quantity reference type. "Decided by Jess Haley, 2026-10-27 [quantity reference" (did_v2_go_forward_class_audit.md:1562).
- epoch-less presentations carry. "Decided by Jess Haley, 2026-10-27 [epoch-less presentations" (did_v2_go_forward_class_audit.md:1564).
- Babu and Soph workbooks. "Decided by Jess Haley, 2026-10-27 [Babu and Soph" (did_v2_go_forward_class_audit.md:1566).
- sample times within eight rounding steps. "Decided by Jess Haley, 2026-10-27 [sample times within" (did_v2_go_forward_class_audit.md:1568).
- a rebuilt document may lose its id. "Decided by Jess Haley, 2026-10-27 [a rebuilt document may" (did_v2_go_forward_class_audit.md:1570).
- jrclust default name is notation. "Decided by Jess Haley, 2026-10-27 [jrclust default name is" (did_v2_go_forward_class_audit.md:1572).
- organization needs a name or an identifier. "Decided by Jess Haley, 2026-10-27 [organization needs a" (did_v2_go_forward_class_audit.md:1574).
- empty ndi_document block is notation. "Decided by Jess Haley, 2026-10-27 [empty ndi_document block" (did_v2_go_forward_class_audit.md:1576).
- device kinds minted. "Decided by Jess Haley, 2026-10-28 [device kinds minted]: (" (did_v2_go_forward_class_audit.md:1578).
- device kind labels and synonyms. "Decided by Jess Haley, 2026-10-28 [device kind labels and" (did_v2_go_forward_class_audit.md:1580).
- tuning best value is a condition. "Decided by Jess Haley, 2026-10-28 [tuning best value is a" (did_v2_go_forward_class_audit.md:1582).
- one calculation per named calculator output. "Decided by Jess Haley, 2026-10-28 [one calculation per" (did_v2_go_forward_class_audit.md:1584).
- absolute-value fits are fit entries. "Decided by Jess Haley, 2026-10-28 [absolute-value fits are" (did_v2_go_forward_class_audit.md:1586).
- presentations without an epoch keep the session anchor. "Decided by Jess Haley, 2026-10-28 [presentations without an" (did_v2_go_forward_class_audit.md:1588).
- image label goes to the observation's notes. "Decided by Jess Haley, 2026-10-29 [image label goes to the" (did_v2_go_forward_class_audit.md:1590).
- binaryseries parameters carried. "Decided by Jess Haley, 2026-10-29 [binaryseries parameters" (did_v2_go_forward_class_audit.md:1592).
- ngrid with no statement carried. "Decided by Jess Haley, 2026-10-29 [ngrid with no statement" (did_v2_go_forward_class_audit.md:1594).
- old table rows carried by NDI. "Decided by Jess Haley, 2026-10-29 [old table rows carried" (did_v2_go_forward_class_audit.md:1596).
- allowed units are source units. "Decided by Jess Haley, 2026-10-29 [allowed units are source" (did_v2_go_forward_class_audit.md:1598).
- standalone item control stays carried. "Decided by Jess Haley, 2026-10-29 [standalone item control" (did_v2_go_forward_class_audit.md:1600).
- oneepoch method is data combination. "Decided by Jess Haley, 2026-10-29 [oneepoch method is data" (did_v2_go_forward_class_audit.md:1602).
- redeclarations merge when base.name goes. "Decided by Jess Haley, 2026-10-29 [redeclarations merge" (did_v2_go_forward_class_audit.md:1604).
- linked session not in the batch. "Decided by Jess Haley, 2026-10-29 [linked session not in" (did_v2_go_forward_class_audit.md:1606).
- unstated session creator carried. "Decided by Jess Haley, 2026-10-29 [unstated session creator" (did_v2_go_forward_class_audit.md:1608).
- drug end without start needs mapping. "Decided by Jess Haley, 2026-10-29 [drug end without start" (did_v2_go_forward_class_audit.md:1610).
- drug times that disagree need mapping. "Decided by Jess Haley, 2026-10-29 [drug times that disagree" (did_v2_go_forward_class_audit.md:1612).
- text channel replaces NCIT Text. "Decided by Jess Haley, 2026-10-29 [text channel replaces" (did_v2_go_forward_class_audit.md:1614).
- cell-attached is OBI. "Decided by Jess Haley, 2026-10-29 [cell-attached is OBI]: (" (did_v2_go_forward_class_audit.md:1616).
- linked session link on a direct dataset relation. "Decided by Jess Haley, 2026-10-29 [linked session link on a" (did_v2_go_forward_class_audit.md:1618).
- fit model stated once. "Decided by Jess Haley, 2026-10-29 [fit model stated once]: (" (did_v2_go_forward_class_audit.md:1620).
- term names compare by node. "Decided by Jess Haley, 2026-10-29 [term names compare by" (did_v2_go_forward_class_audit.md:1622).
- species text is the openMINDS equivalent. "Decided by Jess Haley, 2026-10-29 [species text is the" (did_v2_go_forward_class_audit.md:1624).
- openMINDS element leftovers carried. "Decided by Jess Haley, 2026-10-29 [openMINDS element" (did_v2_go_forward_class_audit.md:1626).
- segment length is the time chunk. "Decided by Jess Haley, 2026-10-29 [segment length is the" (did_v2_go_forward_class_audit.md:1628).
- one folder, final classes only. "Decided by Jess Haley, 2026-10-29 [one folder, final" (did_v2_go_forward_class_audit.md:1630).
- v1 writes into a V2 session. "Decided by Jess Haley, 2026-10-29 [v1 writes into a V2" (did_v2_go_forward_class_audit.md:1632).
- linked session link details. "Decided by Jess Haley, 2026-10-29 [linked session link" (did_v2_go_forward_class_audit.md:1634).
- reshaped retire classes carried. "Decided by Jess Haley, 2026-10-29 [reshaped retire classes" (did_v2_go_forward_class_audit.md:1636).
- linked session pathname. "Decided by Jess Haley, 2026-10-29 [linked session" (did_v2_go_forward_class_audit.md:1638).
- addSessionV2 folded back. "Decided by Jess Haley, 2026-10-29 [addSessionV2 folded" (did_v2_go_forward_class_audit.md:1640).
- term names match ignoring spacing. "Decided by Jess Haley, 2026-10-29 [term names match" (did_v2_go_forward_class_audit.md:1642).
- n-trode count from the channel list. "Decided by Jess Haley, 2026-10-29 [n-trode count from the" (did_v2_go_forward_class_audit.md:1644).
- imaging mode is a method term. "Decided by Jess Haley, 2026-10-29 [imaging mode is a method" (did_v2_go_forward_class_audit.md:1646).
- equipment type is the device kind list. "Decided by Jess Haley, 2026-10-29 [equipment type is the" (did_v2_go_forward_class_audit.md:1648).
- V2 ingest is one sampled body per channel group. "Decided by Jess Haley, 2026-10-29 [V2 ingest is one sampled" (did_v2_go_forward_class_audit.md:1650).
- short last chunk. "Decided by Jess Haley, 2026-10-29 [short last chunk]: (" (did_v2_go_forward_class_audit.md:1652).
- missing facts are needs info. "Decided by Jess Haley, 2026-10-29 [missing facts are needs" (did_v2_go_forward_class_audit.md:1654).
- vintage-B ontologyImage cases. "Decided by Jess Haley, 2026-10-29 [vintage-B ontologyImage" (did_v2_go_forward_class_audit.md:1656).
- element name and reference stored apart. "Decided by Jess Haley, 2026-10-29 [element name and" (did_v2_go_forward_class_audit.md:1658).
- unit with no probe in the batch carried. "Decided by Jess Haley, 2026-10-29 [unit with no probe in" (did_v2_go_forward_class_audit.md:1660).
- table rows carried as v1. "Decided by Jess Haley, 2026-10-30 [table rows carried as" (did_v2_go_forward_class_audit.md:1662).
- preset name stays on method. "Decided by Jess Haley, 2026-10-30 [preset name stays on" (did_v2_go_forward_class_audit.md:1664).
- redeclaration merge moot. "Decided by Jess Haley, 2026-10-30 [redeclaration merge" (did_v2_go_forward_class_audit.md:1666).
- element name kept apart, base.name carried. "Decided by Jess Haley, 2026-10-30 [element name kept apart" (did_v2_go_forward_class_audit.md:1668).
- Naka-Rushton function minted. "Decided by Jess Haley, 2026-10-30 [Naka-Rushton function" (did_v2_go_forward_class_audit.md:1670).
- synonyms supersede nodes only. "Decided by Jess Haley, 2026-10-30 [synonyms supersede nodes" (did_v2_go_forward_class_audit.md:1672).
- interpolated values are a list. "Decided by Jess Haley, 2026-10-30 [interpolated values are" (did_v2_go_forward_class_audit.md:1674).
- canonical absent only as needs info. "Decided by Jess Haley, 2026-10-30 [canonical absent only as" (did_v2_go_forward_class_audit.md:1676).
- trigger channels named by their link. "Decided by Jess Haley, 2026-10-30 [trigger channels named" (did_v2_go_forward_class_audit.md:1678).
- decibels are their own canonical. "Decided by Jess Haley, 2026-10-30 [decibels are their own" (did_v2_go_forward_class_audit.md:1680).
- Haley mask words leave the generic stage. "Decided by Jess Haley, 2026-10-30 [Haley mask words leave" (did_v2_go_forward_class_audit.md:1682).
- control records carried in pass 1. "Decided by Jess Haley, 2026-10-30 [control records carried" (did_v2_go_forward_class_audit.md:1684).
- image raw round trip and single-read keys. "Decided by Jess Haley, 2026-10-30 [image raw round trip and" (did_v2_go_forward_class_audit.md:1686).
- age is NCIT Age. "Decided by Jess Haley, 2026-10-30 [age is NCIT Age]: (" (did_v2_go_forward_class_audit.md:1688).
- equivalents filled in did-schema. "Decided by Jess Haley, 2026-10-30 [equivalents filled in" (did_v2_go_forward_class_audit.md:1690).
- Hartley settings on the inline method. "Decided by Jess Haley, 2026-10-30 [Hartley settings on the" (did_v2_go_forward_class_audit.md:1692).
- acquisition time on its clock. "Decided by Jess Haley, 2026-10-30 [acquisition time on its" (did_v2_go_forward_class_audit.md:1694).
- data analysis is the general method. "Decided by Jess Haley, 2026-10-30 [data analysis is the" (did_v2_go_forward_class_audit.md:1696).
- image collection carried until a writer. "Decided by Jess Haley, 2026-10-30 [image collection carried" (did_v2_go_forward_class_audit.md:1698).
- global-clock oneepoch details. "Decided by Jess Haley, 2026-10-30 [global-clock oneepoch" (did_v2_go_forward_class_audit.md:1700).
- openMINDS strain leftovers settled. "Decided by Jess Haley, 2026-10-30 [openMINDS strain" (did_v2_go_forward_class_audit.md:1702).
- assay labels batch 1. "Decided by Jess Haley, 2026-10-30 [assay labels batch 1]: (" (did_v2_go_forward_class_audit.md:1704).
- element types batch 1. "Decided by Jess Haley, 2026-10-30 [element types batch 1]: (" (did_v2_go_forward_class_audit.md:1706).
- assay labels batch 2. "Decided by Jess Haley, 2026-10-30 [assay labels batch 2]: (" (did_v2_go_forward_class_audit.md:1708).
- element types batch 2. "Decided by Jess Haley, 2026-10-30 [element types batch 2]: (" (did_v2_go_forward_class_audit.md:1710).
- assay labels batch 3. "Decided by Jess Haley, 2026-10-30 [assay labels batch 3]: (" (did_v2_go_forward_class_audit.md:1712).
- element types batch 3. "Decided by Jess Haley, 2026-10-30 [element types batch 3]: (" (did_v2_go_forward_class_audit.md:1714).
- element types batch 4. "Decided by Jess Haley, 2026-10-30 [element types batch 4]: (" (did_v2_go_forward_class_audit.md:1716).
- assay labels batch 4. "Decided by Jess Haley, 2026-10-30 [assay labels batch 4]: (" (did_v2_go_forward_class_audit.md:1718).
- assay labels batch 5. "Decided by Jess Haley, 2026-10-30 [assay labels batch 5]: (" (did_v2_go_forward_class_audit.md:1720).
- assay labels batch 6. "Decided by Jess Haley, 2026-10-30 [assay labels batch 6]: (" (did_v2_go_forward_class_audit.md:1722).
- raw v1 switch finished in batches. "Decided by Jess Haley, 2026-10-30 [raw v1 switch finished" (did_v2_go_forward_class_audit.md:1724).
- stimulator is SNOMED CT Stimulator. "Decided by Jess Haley, 2026-10-30 [stimulator is SNOMED CT" (did_v2_go_forward_class_audit.md:1726).
- global-clock oneepoch carried with its element. "Decided by Jess Haley, 2026-10-30 [global-clock oneepoch" (did_v2_go_forward_class_audit.md:1728).
- differing stimulator epoch is malformed. "Decided by Jess Haley, 2026-10-30 [differing stimulator" (did_v2_go_forward_class_audit.md:1730).
- response unit slot settles 110. "Decided by Jess Haley, 2026-10-30 [response unit slot" (did_v2_go_forward_class_audit.md:1732).
- schema folders by family. "Decided by Jess Haley, 2026-10-30 [schema folders by" (did_v2_go_forward_class_audit.md:1734).
- family roots and relation folder. "Decided by Jess Haley, 2026-10-31 [family roots and" (did_v2_go_forward_class_audit.md:1736).
- retire check now. "Decided by Jess Haley, 2026-10-31 [retire check now]: (" (did_v2_go_forward_class_audit.md:1738).
- purpose renamed now. "Decided by Jess Haley, 2026-10-31 [purpose renamed now]: (" (did_v2_go_forward_class_audit.md:1740).
- acquisition folder. "Decided by Jess Haley, 2026-10-31 [acquisition folder]: (" (did_v2_go_forward_class_audit.md:1742).
- clock alignment in time_reference. "Decided by Jess Haley, 2026-10-31 [clock alignment in" (did_v2_go_forward_class_audit.md:1744).
- reference papers as v2 guidance. "Decided by Jess Haley, 2026-10-31 [reference papers as v2" (did_v2_go_forward_class_audit.md:1746).
- gene list mapping is built. "Decided by Jess Haley, 2026-10-31 [gene list mapping is" (did_v2_go_forward_class_audit.md:1748).
- gene list mapping in the generic stage. "Decided by Jess Haley, 2026-10-31 [gene list mapping in the" (did_v2_go_forward_class_audit.md:1750).
- daqreader_ndr confirmed set. "Decided by Jess Haley, 2026-10-31 [daqreader_ndr confirmed" (did_v2_go_forward_class_audit.md:1752).
- layout calls stand. "Decided by Jess Haley, 2026-10-31 [layout calls stand]: (" (did_v2_go_forward_class_audit.md:1754).
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
- response parameters as a shared method. "Decided by Jess Haley, 2026-10-21 [response parameters as a" (did_v2_stimulus_response_model_plan.md:610).
- control input told apart by its document. "Decided by Jess Haley, 2026-10-21 [control input told apart" (did_v2_stimulus_response_model_plan.md:612).
- empty response settings. "Decided by Jess Haley, 2026-10-21 [empty response" (did_v2_stimulus_response_model_plan.md:614).
- control record is a calculation. "Decided by Jess Haley, 2026-10-21 [control record is a" (did_v2_stimulus_response_model_plan.md:616).
- presentation times from the file. "Decided by Jess Haley, 2026-10-22 [presentation times from" (did_v2_stimulus_response_model_plan.md:622).
- presentation file declared. "Decided by Jess Haley, 2026-10-22 [presentation file" (did_v2_stimulus_response_model_plan.md:625).
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
- tenet amendments 2026-10-21. "TEAM-SIGN-OFF [tenet amendments 2026-10-21], below): one" (did_v2_tenets.md:863).
- tenet amendments 2026-10-20. "TEAM-SIGN-OFF [tenet amendments 2026-10-20]: jess /" (did_v2_tenets.md:1088).
- tenet amendments 2026-10-21. "TEAM-SIGN-OFF [tenet amendments 2026-10-21]" (did_v2_tenets.md:1090).
- tenet T20, group entities. "TEAM-SIGN-OFF [tenet T20, group entities]" (did_v2_tenets.md:1091).
- tenet signature text. "Decided by Jess Haley, 2026-10-22 [tenet signature text]" (did_v2_tenets.md:1093).
- T1 and T5 signed. "Decided by Jess Haley, 2026-10-22 [T1 and T5 signed]: the" (did_v2_tenets.md:1095).
- T2 time-varying property. "Decided by Jess Haley, 2026-10-22 [T2 time-varying" (did_v2_tenets.md:1097).
- ordered inputs. "Decided by Jess Haley, 2026-10-22 [ordered inputs]: T20's" (did_v2_tenets.md:1099).
- tenet stale names. "Decided by Jess Haley, 2026-10-22 [tenet stale names]: the" (did_v2_tenets.md:1101).
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
- calculator mixin dropped (#73). "TEAM-SIGN-OFF [calculator mixin dropped (#73)]" (team_signoff_lines_DRAFT.md:13).
- observation vs calculation (#73). "TEAM-SIGN-OFF [observation vs calculation (#73)]" (team_signoff_lines_DRAFT.md:16).
- tuning restructure (#73). "TEAM-SIGN-OFF [tuning restructure (#73)]" (team_signoff_lines_DRAFT.md:19).

## v1 source side (from the coverage ledger)

| disposition | count |
|---|---|
| consumed by migrator (no tombstone) | 83 |
| retire | 20 |
| no V_eta home, no migrator -- UNVERIFIED | 6 |
| test/demo fixture (non-production) | 2 |
| UNMAPPED (needs a V_eta home) | 2 |
| dissolved → subject | 1 |
| persist | 1 |

### `retire`, but NO MIGRATOR YET -- 1 rows

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

DENOMINATOR: 1 row(s), each searched for its BARE CLASS NAME as a quoted literal in 49 batch post-pass file(s) under `+did2/+convert` (comments stripped).

- `calculator` -- no per-class migrator and no batch post-pass names it; passes through today

**UNVERIFIED** -- no V_eta home, no migrator, fate never established. These strand today:

- `epochclocktimes`
- `filter`
- `imageCollection`
- `imageStack_parameters`
- `projectvar`
- `stimulus_parameter_table`

