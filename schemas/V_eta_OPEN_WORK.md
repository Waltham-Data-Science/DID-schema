# V_eta — OPEN WORK (the committed index)

**This file is the index of remaining V_eta work.** Every `#nn` in the plan documents points
at a row here. Since 2026-10-21 each open row is one line pointing at its GitHub issue, and
the evidence lives in the issue. The full text this file carried until then (reconciliation
audits, long row prose, completed-row write-ups) is in git: `git show 6523cb1:schemas/V_eta_OPEN_WORK.md`.

`python3 tools/status_board.py` owns *decision* state. This file owns *build and repair* state.

Only Jess Haley decides. An issue marked "Proposed (not decided)" is a proposal.

---

## OPEN

Tracked in this repository (label `V2`, milestone "V2 -> main"):

| # | item -> issue |
|---|---|
| 30 | raw recordings as typed observations: Guard A has no value kind (the assembler is live) -> https://github.com/Waltham-Data-Science/DID-schema/issues/104 |
| 31 | stimulus model: non-grating stimuli need a value model; unfolded presentations need a disposition -> https://github.com/Waltham-Data-Science/DID-schema/issues/94 |
| 32 | binding governance (T8): the remaining clause is #129 -> https://github.com/Waltham-Data-Science/DID-schema/issues/89 |
| 46 | retire `ngrid`, gated on both consumers -> https://github.com/Waltham-Data-Science/DID-schema/issues/92 |
| 48 | `receptive_field.value` declares no fields; the hartley_calc fold quarantines -> https://github.com/Waltham-Data-Science/DID-schema/issues/93 |
| 57 | clock alignment cluster: is `acquisition_channels`' own dependency set covered by the signature? -> https://github.com/Waltham-Data-Science/DID-schema/issues/95 |
| 62 | `stimulus_parameter` dissolution, blocked on a Marder corpus -> https://github.com/Waltham-Data-Science/DID-schema/issues/96 |
| 66 | `daqreader_*_epochdata_ingested` declare no `epoch_id` -> https://github.com/Waltham-Data-Science/DID-schema/issues/105 |
| 67 | mint the four NDI clocktype terms and fill their empty nodes -> https://github.com/Waltham-Data-Science/DID-schema/issues/97 |
| 68 | a value rollup for `sampled_body` -> https://github.com/Waltham-Data-Science/DID-schema/issues/98 |
| 69 | a child cannot tighten a parent field; redeclaration is silent -> https://github.com/Waltham-Data-Science/DID-schema/issues/99 |
| 72 | the unattached `openminds` documents, group B (group A is NDI-side) -> https://github.com/Waltham-Data-Science/DID-schema/issues/100 |
| 73 | is `metadata_editor` always written with the openMINDS dataset graph? -> https://github.com/Waltham-Data-Science/DID-schema/issues/100 |
| 76 | does one approach cover several interactions? (also #76a) -> https://github.com/Waltham-Data-Science/DID-schema/issues/101 |
| 81 | `oneepoch`: fork A1 is chosen, not signed -> https://github.com/Waltham-Data-Science/DID-schema/issues/102 |
| 83 | pre-`base` documents: `base.type` / `base.database_version` (also #84(g), #84(h)) -> https://github.com/Waltham-Data-Science/DID-schema/issues/103 |
| 105 | how many pre-repair `ontologyTableRow` documents carry a plural `document_id`? -> https://github.com/Waltham-Data-Science/DID-schema/issues/111 |
| 108 | `binaryseries_parameters` has no edges: what do its parameters attach to? -> https://github.com/Waltham-Data-Science/DID-schema/issues/109 |
| 112 | `tuning_curve.response_units` is never filled by a v1 writer -> https://github.com/Waltham-Data-Science/DID-schema/issues/110 |
| 114 | `ngrid`: deleted (signed) versus migrated (later decision) -> https://github.com/Waltham-Data-Science/DID-schema/issues/92 |
| 115 | registry rows: which units are admissible for a variable -> https://github.com/Waltham-Data-Science/DID-schema/issues/90 |
| 118 | no value kind for an undimensioned observation (with #30(a)) -> https://github.com/Waltham-Data-Science/DID-schema/issues/104 |
| 124 | corpus proof for the spatial-transcriptomics family, deferred -> https://github.com/Waltham-Data-Science/DID-schema/issues/106 |
| 125 | spatial-transcriptomics tiles and cells onto the data_body fields -> https://github.com/Waltham-Data-Science/DID-schema/issues/91 |
| 126 | controlled-term bindings for the spatial-transcriptomics fields -> https://github.com/Waltham-Data-Science/DID-schema/issues/107 |
| 129 | bindings become `required`: `variable`, and a node on every term -> https://github.com/Waltham-Data-Science/DID-schema/issues/89 |

Open items without a row number:

- `syncrule_mapping` declares `epochnode_*.t0_t1` as a scalar; the writer stores two numbers -> https://github.com/Waltham-Data-Science/DID-schema/issues/108
- no value kind carries an uninterpreted payload (the `generic_file` case) -> https://github.com/Waltham-Data-Science/DID-schema/issues/104

### Open in another repository (not tracked here)

| row | repository | what is open |
|---|---|---|
| 9 | DID-matlab / NDI-matlab | D-C spike half: 7 spike classes (`spikewaves`, `spike_clusters`, `vmspikesummary`, `binnedspikeratevm`, `site2channelmap`, `vmneuralresponseresiduals`, `spike_interface_sorting_outputs`) pass through to an NDI second pass that does not exist |
| 45 | DID-matlab / NDI-matlab | data_body: the schema tier is built; `sample_time` is still named in 15 `.m` files under DID-matlab `src` at DID-matlab #218 `c74f4e0` (port to #88 merged at `229c12e`), 4 of them on non-comment lines (`grep -rl sample_time --include=*.m src`; was 25 on ecstatic before the port, 2026-10-21) |
| 47 | DID-matlab | the `ontology_image` vintage-B raster arm in `+migrators_j/ontology_image.m`; decided target `observation + intensity` + `sampled_body` (ledger); at DID-matlab #218 `c74f4e0` (port to #88 merged at `229c12e`) the migrator emits `observation + term` and `relative_time_reference` only, so the ledger row `ontologyImage` still reads rung 3 `no` |
| 60 | DID-matlab / NDI-matlab | epoch family migrator half: `acquisition_epoch` stays the carrier until the ensemble second pass lands |
| 61 | DID-matlab | `stimulus_response_scalar.m` is a passthrough; the ledger names a `harmonic_component` calculation as the decided target, which it does not emit (rung 3 `no`) |
| 65 | DID-matlab / NDI-matlab | time-reference collapse: the schema side is complete. At DID-matlab #218 `c74f4e0` (port to #88 merged at `229c12e`) NO `+convert` file mints `session_relative_reference` (the status board's mint detector over 190 V_eta-path files finds 0 sites; `private/jSessionAnchor.m:36` mints `relative_time_reference` through `did2.build.relativeTimeReference`), and NDI `claude/v-eta-migration-plan-35jj1z` (`095debb22`) names it only in comments and messages. Residual: two code READS of the old name (`epochMint.m:2502`, `resolveSessionAnchors.m:423`) and the PARTIAL `treatment` target row, which can only gain. Closing the row is Jess's call |
| 74 | DID-matlab | settings model migrator half (`method_parameters`, now `method`): retype the inline slot in lockstep with `jCalculation.m`; the four spike-settings classes. At DID-matlab #218 `c74f4e0` (port to #88 merged at `229c12e`) the four (`sorting_parameters`, `spike_extraction_parameters`, `spike_extraction_parameters_modification`, `vmspikefilteringparameters`) emit `method` (`private/jMethodParameters.m:150`; ledger rung 3 `yes` on all four); whether the inline slot is done was not re-checked |
| 79 | DID-matlab | family-count measurement: the port-88 digest prints `EDGE-FAMILY CARDINALITY VIOLATIONS: 0` with no denominator line, so it is not evidence yet |
| 103 | DID-matlab | `valid_interval`: the decided target is `observation + time` (was spelled `time_observation`; ledger); `resolveValidIntervals` is dormant and emits nothing (rung 3 `no`; its header still reads "DORMANT BY DECISION" at `c74f4e0`) |
| 113 step 3 | DID-matlab | see the epoch-extent sign-off below: steps 1-2 built, step 3 ruled out; the ledger row `epochclocktimes` -> `relative_time_reference` still reads rung 3 `no` |
| 119b / 122 | DID-matlab | spatial-transcriptomics migrators exist (8); on #88 the pyramid passes through |
| 127 | empty-ontology | EMPTY duplicate and synonym review, deferred until the Dabrowska, Babu and Hunsberger datasets are migrated (Jess Haley, 2026-10-21); full list in `git show 6523cb1:schemas/V_eta_OPEN_WORK.md` |
| 128 | DID-matlab / NDI-matlab | the DID-schema half is done (`tools/build_v_eta.py` and the `V_alpha`..`V_zeta` trees are deleted); residual: NDI `stimulusBathToBath.m:122` defaults `targetVersion = 'V_zeta'`, and DID-matlab has 25 `.m` files that mention V_epsilon or V_zeta at DID-matlab #218 `c74f4e0` (port to #88 merged at `229c12e`) (`grep -rlE 'V_epsilon|V_zeta' --include=*.m .`; was 28) |

## COMPLETED (kept so the `#nn` numbering stays stable)

| # | what completed |
|---|---|
| 1-8, 10-24, 26, 33, 36, 39-42, 44, 49, 50, 55 | subject only: descriptions lost in the 2026-08-08 re-provisioning |
| 25 | software follow-ups: `softwareDedup.m` and the openMINDS crosswalk exist |
| 27 | R5 infra renames: a phantom; all five items were decided away or rejected (reconciliation 2026-10-21) |
| 28 | boundary-class dispositions: six built, the other two moved to #29 and #31; nothing left under this row |
| 29 | ensemble second pass (`ensembleMembership.m`) |
| 34 | Phase 1 gates: two armed by default (`RequiredDependencies`, `NonVacuousFields`), one disarmed on purpose |
| 35 | Phase 2 migrator vocabulary sweep reads 0 and enforces |
| 37 | `mustBeNonEmpty` on `depends_on` is enforced |
| 38 | an all-blank composite counts as empty |
| 43 | the last BLOCKING tombstone; `check_tombstones.py` BLOCKING = 0 |
| 51 | `session` documents present in every corpus (run 31327383671) |
| 52 | `time_reference_#` uniqueness rule built; whether its signature covers it is asked in #95 |
| 53 | `ontology_table_row` subjects: `ontologyRowSubjects` wired at NDI `local.m:1386`; Dab e2e 6205 of 6205 resolved |
| 54 | NDI schema-document and writer-dependency scans |
| 56 | `strain` is an entity, schema half (since superseded by the entity merge, 2026-10-08) |
| 58 | `syncrule_mapping`: the live NDI query works again |
| 59 | `acquisition_system` and the daq class-name to software fold |
| 63 | numbered edge families declare their cardinality (the measurement is #79) |
| 64 | the file-list detector exists |
| 70 | the empty-node backlog is visible and ratcheted |
| 71 | `openminds_stimulus` stops emitting hollow statements |
| 75 | there were never two signed plans |
| 77 | `measurement.m` was not a regression |
| 78 | strain migrator second pass (`strainAssembly.m`; emits the pre-#88 strain shape, NDI-side) |
| 80 | six signed plan documents told readers they were unsigned; gated by `check_signoff_header_staleness.py` |
| 82 | the `directory` / `interaction_purpose` / `projectvar` audit |
| 84-102, 104, 106, 107 | 2026-08-11/12 session decisions, findings and corrections (a log, not work); #84(g)/(h) are carried by #103 |
| 109 | `epochfiles_ingested` clause conflict, closed by #66 increment 3 (2026-08-22) |
| 110 | `stimulus_response_scalar_parameters_basic` fold armed per document (DID-matlab `71f80e0`) |
| 111 | `demo` collapse: `+migrators_j/demo_ndi.m` and `demo_ndi_mock.m` exist |
| 113 | `epochclocktimes` epoch extent: two steps built, the third ruled out (see the sign-off below); emission is listed under cross-repo |
| 116 | the added-epoch reader (closed 2026-08-17) |
| 117 | spike train as `time_observation` / `spike` (DID-matlab `3ceada5`) |
| 119 | `duration` -> `time` (`stable/time.json`) |
| 119b | pyramid `⊂ subject_observation` reshape: a phantom; that class is gone |
| 120 | `NCIT:C16608` "Gene Expression" registered |
| 121 | spatial-transcriptomics tombstones and ledger rows |
| 123 | `testMigratorsJSpatialTranscriptomics.m` |

Items from the 2026-08-10 list "DECISIONS WAITING ON THE TEAM" (A2 `element_epochid` destroyed by the
stimulus-response fold; A6 `is_cache` in no schema; B2 `patch`/`sharp` emit two observations;
B3 `image_observation.subject_id`; B4 `threshold_sign`; B5 `measurement.m` substring matching;
C2-C5) were not re-verified on 2026-10-21. Their text is in `git show 6523cb1:schemas/V_eta_OPEN_WORK.md`.

---

## DECISIONS RECORDED IN THIS FILE (verbatim)

### DECISION 2026-08-10 — a statement reaches its epoch through the REFERENCE CHAIN, not a direct edge

Team decision, jess@walthamdatascience.com, 2026-08-10, verbatim:

> "Use the reference chain, don't add the direct edge"

**What it settles.** The epoch family's signed line reads *"epochid is DROPPED in favour of a
uniform `epoch_id` edge"*, and the epoch plan says every epoch-scoped document gains one. Read
literally that includes `subject_interaction`. It does not get one. A statement reaches its
epoch by:

        subject_interaction --time_reference_#--> relative_reference
                            --relative_to------> epoch

A direct edge would store one fact in two places — the hazard the epoch plan itself raises for
`base.session_id` vs `part_of` and marks "Flagged, not solved". Two copies of one fact agree by
coincidence until something checks them, and nothing would.

**`directed_relation` KEEPS its optional `epoch_id`, and that is not an inconsistency.** It is
signed separately under the ensemble decision ("EPOCH-SCOPED `member_of` edges carrying their
epoch"): there the epoch is the edge's OWN content, because the recorded roster changes from
epoch to epoch. On a statement it would be a restatement of when the statement happened.

**THE SIGNED PLAN LINE NOW UNDER-DESCRIBES THIS, AND ONLY THE TEAM MAY AMEND IT.**
`V_eta_epoch_plan.md:849` still says "uniform `epoch_id` edge". This entry does NOT amend it and
no `TEAM-SIGN-OFF` line was added or edited — that is the team's to write. Recorded here so the HISTORICAL-SIGNOFF-CLAIM
decision is not lost while the plan says something broader than what was decided.

**KNOWN WEAK LINK — measured, and the reason to revisit this if anything does.**

        DENOMINATOR: 3 classes read from the built set (subject_interaction,
                     directed_relation, subject_statement)

        subject_interaction  time_reference_#  mustBeNonEmpty=False  min_count=1
        directed_relation    epoch_id          mustBeNonEmpty=False  (optional by design)

`min_count: 1` guarantees the family EXISTS on every `subject_interaction`, and
`relative_reference.relative_to` is REQUIRED, so a populated reference does resolve. But
`mustBeNonEmpty` is False, so `time_reference_1 = ''` satisfies the family and reaches no
epoch — and the newly ARMED `RequiredDependencies` gate keys on `mustBeNonEmpty`, so it will
not catch it. This is the invented-empty-edge pattern one link along the chain. **Tighten that
before concluding the chain is insufficient** — an empty reference would otherwise look like
evidence the direct edge was needed, when it is evidence the edge we have is unenforced.

The deliberate omission is stated at the `subject_interaction` definition in
`tools/build_v_eta.py`, not left silent, because an unexplained absence is exactly what someone
"completing the family" would helpfully fix.

---

### TEAM DECISION 2026-08-11 — the E. coli lawns and plates are subjects, in two tiers

Team decision, jess@walthamdatascience.com, 2026-08-11, verbatim:

> "Yes, each lawn can be a subject and a plate of lawns is another subject where each lawn
> is a member of it"

This is RICHER than the single plate-subject that was scoped from the scouting pass. Two
subject tiers plus a group relation:

        lawn   (a bacterial patch)   -> subject
        plate  (a plate of lawns)    -> subject, the GROUP
        lawn --member_of--> plate

**No TEAM-SIGN-OFF line has been added by Claude.** The governing plan document still needs HISTORICAL-SIGNOFF-CLAIM
the team's signature; this entry records the decision so it is not lost, and the board will
keep rendering the family as awaiting review until that line exists.

#### The source data supports both tiers — read from NDI `origin/main`

`+setup/+conv/+haley/doImport.m`, Step 8 (`session = sessions{2}`, the E. coli session):

        plateVariables   keyed  plateID              14 cols  expID, OD600Label, peptoneFlag,
                                                              timePoured, bacteriaStrain, CFU,
                                                              OD600Real, OD600, lawnVolume, ...
        imageVariables   keyed  {plateID, imageID}    4 cols
        patchVariables   keyed  {imageID, patchID}   10 cols  lawnRadius, circularity, yPeak,
                                                              yOuterEdge, borderAmplitude,
                                                              meanAmplitude, centerAmplitude,
                                                              borderCenterRatio

So the LAWN is already a first-class row with its own geometry and fluorescence measures —
it is not something that has to be invented to carry the decision.

#### Consequences and constraints, each established rather than assumed

1. **Membership is a TWO-HOP join.** `patchVariables` keys on `imageID`, NOT `plateID`, so
   lawn → plate runs patch → image → plate. Both hops are STRING joins on `data` values,
   because no Haley `table2ontologyTableRowDocs` call passes `dependencyVariable` — every
   row's `depends_on` is `[{document_id, ""}]`. Both hops must be scoped to
   `base.session_id`: `plateID` COLLIDES across the two Haley sessions (`doImport.m:166`
   adds `expType*1000`, `:729` does not), and both sessions land in ONE `ndi.dataset.dir`.

2. **`local_identifier` must be qualified.** `patchID` is `1:numPatch` WITHIN a plate
   (`doImport.m:275`), so `'0001'` recurs on every plate, and `jEnsureLocalId` does no
   dataset-level qualification. Unqualified lawn ids collide immediately.

3. **`member_of` already exists and is already bound.** The registry carries it with
   `timed=True, ordered=True`, and the ensemble decision uses the same relation for
   epoch-scoped group membership. This is not a new relation.

4. **Do NOT bundle the strain edge.** `bacteriaStrain` is a document-id STRING sitting in
   `data` (`doImport.m:734`), not an edge. Minting `strain_id` from it is a second
   unverified-resolvability edge — the shape that turned `distance_metadata` from a quiet
   passthrough into a GATING orphan failure. Separate step, separate decision.

5. **No corpus can grade this.** `runCorpusDiscovery` runs five passes and ZERO
   `ndi.migrate.*`, so NDI-side subject resolution is invisible to the corpus gate. The
   scouting recommendation is to build the join DID-SIDE as a batch post-pass, since it
   needs only documents already in the migrated batch — no session, no database, no file
   bytes — the same criterion that put `epochMint` and `resolveSessionAnchors` DID-side.

#### What it unblocks

4,563 JH `image_stack` documents stop being observations about nobody, and the ~4,563
`ontology_label` documents that inherit their subject through the image unblock with them
(`ndi.migrate.internal.ontologyLabelSubjects.m:59-73` records that bucket as blocked on
exactly this). The plate's OD600 / CFU / lawn-volume covariates and the lawn's geometry
become real observations rather than dropped columns.

#### REFINEMENT, same day — mint a tier only where it is MEASURED

Team, jess, 2026-08-11, verbatim:

> "It's only necessary to make all subjects if we take measurements of both which I think in
> most cases is true"

So the two tiers are **conditional on the data, not structural**. A subject is minted for a
tier only where that tier's row carries at least one non-empty measurement; a subject with
nothing said about it is the hollow document `did2.validate.isFragment` and the
vacuous-required-field check exist to catch, and this build must not manufacture them.
`member_of` needs both ends, so where only one tier is minted no relation is emitted.

The expectation holds on the COLUMNS — both tiers carry real measures:

        plate  OD600Real, CFU, OD600, lawnVolume, peptoneFlag, + timestamps
        lawn   lawnRadius, circularity, yPeak, yOuterEdge, borderAmplitude,
               meanAmplitude, centerAmplitude, borderCenterRatio

**But a column existing is not a value existing.** All 24 columns exist by construction in
the tables; whether a given ROW has values is per-document and checkable only at migration
time. The team's "in most cases" is therefore an expectation to MEASURE, not an assumption
to build on — and the build reports these states separately, never summed:

        no E. coli tables in this corpus            (did not look)
        row present, no measurements                (looked, nothing to say)
        row present, measurements, subject minted   (the intended case)
        minted one tier only, member_of withheld    (and which tier)

A non-zero "row present, no measurements" is a finding, not a passthrough statistic: it
would mean the expectation does not hold for some population, and it is to be reported with
its count rather than absorbed into a total.

---

### TEAM DECISION 2026-08-11 — `local_identifier` on patches is the (experiment, plate, patch) TRIPLE

Team, jess@walthamdatascience.com, 2026-08-11, verbatim:

> "each experiment #, plate #, and patch # combo should be unique and should dictate the
> local identifier for all patches. None should be labeled just patch #"

**Applies to ALL patches, not only the new E. coli lawns.** The C. elegans patch subjects
minted today by `applyPatchGeometryMap` in `+migrators_j/ontology_table_row.m` use a bare
`patchID` via `jEnsureLocalId` — that is what the directive forbids, and they are re-labelled
to the same triple. One agent owns the convention for both, because two agents would ship two
spellings of one identifier inside a single dataset.

#### The collision this fixes, and why nothing smaller would

`patchID` is `1:numPatch` **WITHIN a plate** (`doImport.m:275`), so `'0001'` recurs on every
plate. `jEnsureLocalId` does no dataset-level qualification, and both Haley sessions land in
ONE `ndi.dataset.dir`. `subject.local_identifier` is REQUIRED and documented *"unique within
its dataset"* — so the documented invariant was FALSE before any lawn work.

**The collision is INTRA-session** (between plates inside one session), which is why
session-scoping would not have rescued it. Contrast `epochMint`, which keys
`(session_id, local_identifier)` because epoch id strings collide ACROSS sessions — 142 of
corpus B's 149. Same field, different collision geometry, different fix. Only the triple works
here.

#### Why the change is safe

`local_identifier` is a HUMAN HANDLE, not a join key: `base.id` is the key, so changing a
handle dangles nothing. `epochMint` is the one place this project joins on it, and that is for
`epoch` entities, not subjects.

#### The constraint that follows from it

The triple is NOT on the patch row. `patchVariables` keys on `{imageID, patchID}`;
`imageVariables` carries `plateID`; `plateVariables` carries `expID`. So forming the
identifier needs the SAME two-hop join (patch → image → plate) that `member_of` needs. **If a
hop fails the identifier cannot be formed, and `local_identifier` is REQUIRED — so a subject
that cannot be named must not be minted.** Refuse and count, never fall back to a bare
`patchID`. A test asserts that a bare-`patchID` identifier FAILS, so the directive cannot
silently regress.

---

### TEAM DECISION 2026-08-11 — "Do B": build the openMINDS citation migrator

Team, jess@walthamdatascience.com, 2026-08-11, verbatim: **"Do B"**, against the three options
recorded above (A accept the loss / B write the migrator / C require `metadata_editor`).

**B IS ADDITIVE, NOT A REPLACEMENT.** The graph stores only a DOI for a related publication —
no title, no PMID, no PMCID; NDI's reader recovers those by NETWORK LOOKUP
(`resolveRelatedPublication`), while the editor path carries all four. Neither store dominates,
0 of 6 corpora carry both, and a migrator must not fabricate the difference. The
`metadata_editor` path is NOT removed or weakened.

**Shape, as briefed to the build:** pass-1 guarded passthrough for `openminds` (branch on
`matlab_type`, ERROR on an unknown shape per the `ontology_image` pattern) plus a batch
assembler in `+did2/+convert/` wired at all four call sites, running BEFORE
`resolveDatasetEntities` so its rich `dataset` wins that pass's richness ranking against the
`dataset_remote` stubs. It emits the same six entity classes `metadata_editor.m` emits;
`entityDoc`/`relationDoc`/`orgFor`/`buildGids` are reused unchanged and only the READERS
differ. `person` can be id-preserving 1:1, which `metadata_editor.m:117` cannot.

**`ndidataset2metadataeditorstruct.m` IS THE SPECIFICATION** — NDI's own reader that rebuilds
the editor structure from the graph. Whatever it queries is what the migrator must consume.
Nobody had read it as a spec before.

**The orphan guard is the thing most likely to turn a green run red:** consumed `openminds`
documents are referenced by surviving ones through `openminds_1..n`, so consumption must be
all-or-none per connected component.

Subject-side openMINDS types (Subject, BiologicalSex, Species, Strain, RRID, StockNumber) are
OUT OF SCOPE — they overlap the existing `openminds_subject` route and the signed strain
decision.

**Neither decision carries a `TEAM-SIGN-OFF` line written by Claude.** The board will keep
rendering these families as awaiting review until the team writes one.

---

### TEAM DECISION 2026-08-11 — `generic_file` folds to `opaque_body` + a `subject_statement`

Team, jess@walthamdatascience.com, 2026-08-11, verbatim: **"opaque_body + a subject_statement
whose variable comes from that sibling label — 'subject S has a plasmid map, here are the
bytes.' Is the correct way"** — option (a) of the two put to the team. Option (b) (bytes hung
directly off the subject, `format_ontology` as its own descriptor, semantic type lost) is
REJECTED.

**THE JOIN IS A CHAIN, AND IT IS VERIFIED, NOT ASSUMED.** Read from the writer,
`+setup/+conv/+babu/import.m` on NDI `origin/main`:

        ontologyLabel --document_id--> generic_file --document_id--> subject_group
          :534 / :584                    :531 / :581

        plasmid   label ontologyNode EDAM:data_1286   file formatOntology EMPTY:0000253
        LCMS      label ontologyNode EDAM:data_2536   file formatOntology EDAM:format_3620

The label says WHAT THE DATA IS; `formatOntology` says HOW IT IS ENCODED. Those are exactly
`variable` and `format` in V_eta, so the decision is not a mapping invented for this class —
it is the two facts NDI already stores, landing in the two slots that already exist.

**TWO CORRECTIONS TO THE RECORD, both of which made this EASIER than it was written up.**

1. **THERE IS NO NAME COLLISION.** `CLAUDE.md` says "V_eta already folded a `generic_file`
   concept into `opaque_body`, so the class name is taken — reconcile before building." Nothing
   in V_eta is named `generic_file` except the tombstone. What existed was a test asserting
   `"generic_file" not in RECORDS`, which was TRUE and was PINNING THE STRANDING: the fold it
   named was never built (0 of 82 `migrators_j` entries match `generic|valid`), so "dissolves
   into opaque_body" described an intention and the test made the intention indistinguishable
   from the outcome. Already inverted in `tests/test_veta.py`.

2. **`ontology_label` NO LONGER DISCARDS `document_id`.** The recorded loss was real and is
   FIXED — `ontology_label.m` became a guarded passthrough (commit `5d22f22`), so the edge that
   is the ONLY join back to the labelled document survives migration. Option (a) was put to the
   team with the caveat that it "cannot complete until that edge is preserved". That caveat is
   already satisfied and should not be re-raised.

**NOTHING REFERENCES `generic_file` BY ID.**

        DENOMINATOR: 91 NDI templates on origin/main, 1002 .m files searched
        RE-DERIVED 2026-08-13: 91 NDI templates on origin/main; 1,003 .m files. The did_v1 ground truth did NOT move -- 0 template diffs across the NDI main merge, still 91; main gained one .m file, so only the denominator shifted. RE-DERIVED AGAIN 2026-08-15: 91 NDI templates on origin/main; 1,005 .m files. NDI main moved to 928b1cd5 and two of its nine commits add test .m files (closeAndRemoveDir.m, TestRayoLabStims.m). The did_v1 ground truth is STILL unmoved -- 91 templates, 0 diffs; only the denominator shifted.
        NDI templates declaring generic_file_id or valid_interval_id     0
        DID-matlab migrator references to either id                      0

Found by query, never by edge. So a decompose cannot strand a referent — the opposite of the
calculator dissolution, which changed ids and produced 11,448 orphans in Soph.

**IT IS A DID-SIDE BATCH PASS, NOT A SINGLE-DOCUMENT MIGRATOR.** The `variable` lives in a
DIFFERENT DOCUMENT, so no per-document migrator can reach it. Everything needed —
`generic_file`, its `ontologyLabel`, the subject group — is already in the migrated batch, which
is the standing criterion for DID-side rather than an NDI second pass. The file bytes are never
read; only the declaration is carried.

**THE ONE REMAINING BLOCKER IS ONE FIELD.** `opaque_body` has `format`, `filename` and
`description` and NO `content_hash`, so folding today would DROP the MD5 the writer computes
(`ndi.fun.file.MD5`). `content_hash` is part of the already-signed `data_body` model. The
existing test asserts the absence, so the day `opaque_body` gains the field the suite says so
and this fold unblocks.

**STILL OPEN, NOT DECIDED HERE:** `valid_interval` — 1→N (one statement per interval, each with
its two `relative_reference` documents per the time model's decision C) versus keeping the
inline array on one statement. Put to the team at the same time; only `generic_file` was
answered.

**No `TEAM-SIGN-OFF` line is written by Claude.** The board keeps rendering this family as HISTORICAL-SIGNOFF-CLAIM
awaiting review until the team writes one.

---

### TEAM DECISION 2026-08-11 — `valid_interval` becomes a boolean-valued `subject_statement`

Team, jess@walthamdatascience.com, 2026-08-11, verbatim: **"Should valid interval be a new
class that takes a subject statement, shares its time reference and states true or false for
each value?"** — put as a question, restated twice, and taken as the decision. So: a NEW class,
`subject_statement`-derived, sharing its time reference, carrying a BOOLEAN per entry.

**THE BOOLEAN CLOSES A GAP NDI ITSELF RECORDED.** Not a V_eta refinement — the missing half of
the class, written down by its own author:

    $ git show origin/main:src/ndi/+ndi/+app/markgarbage.m | sed -n '40,41p'
        % developer note: it would be great to have a 'markinvalidinterval' companion
        function b = markvalidinterval(ndi_app_markgarbage_obj, ndi_epochset_obj, t0, ...

Validity is encoded in the CLASS NAME today, so "this stretch is bad" is expressible only as
absence. A true/false value makes valid and invalid symmetric in one representation. This is
also why the alternative put to the team — 1 to N, one statement per interval — is WORSE: N
statements that all mean "valid" cannot express invalidity either.

**THE REFERENT.** `element_id` -> the element, and elements are promoted to subjects with ids
PRESERVED, so this is an ordinary statement about a subject.

**THE TIME REFERENCE: SHARE BY DEFAULT, SPLIT WHERE THE WRITER DIFFERS.** Each v1 interval
carries TWO independent anchors — the signature is
`markvalidinterval(epochset, t0, timeref_t0, t1, timeref_t1)` and the stored struct is
`{timeref_structt0, t0, timeref_structt1, t1}`. The time model's DECISION C already governs
this: one `relative_to` + one `frame` govern both ends where they agree, and an interval whose
ends are anchored differently becomes TWO reference documents on the statement — nesting an
anchor block per end is explicitly rejected. The new class needs no new rule; it follows that one.

**"EACH VALUE" IS PER INTERVAL, NOT PER SAMPLE.** Per-interval is migratable: the intervals are
literally in the document. Per-sample (a validity mask over the time axis) is NOT — the migrator
never reads file bytes, so it does not know the sample grid and would have to fabricate one. The
mask is derivable from the intervals by anyone holding the grid; the reverse is lossy; and a mask
over a long recording is large and rebuildable, which is the same explicitly-derived-cache
pattern already used for the ensemble (T10).

**THREE THINGS THE BUILD MUST NOT QUIETLY BREAK.**

1. **ABSENCE MUST KEEP MEANING VALID.** `markgarbage` is opt-in: today, NO `valid_interval`
   document means the whole epoch is good. If the new class states true/false explicitly, absence
   must still mean valid, or migrating any dataset without markgarbage documents silently
   reclassifies every epoch from "all good" to "unknown". Nothing we currently gate on would
   catch that. The class must not be required.

2. **VALIDITY INHERITS, AND A FLAT STATEMENT LOSES IT.** `loadvalidinterval` falls back to
   `underlying_element` when a derived element has none. That is a query-time rule in NDI. Stored
   flat against one subject, the inheritance disappears unless it is re-derived through the
   `derived_from` chain or materialised. OPEN SUB-QUESTION, not decided here.

3. **ORDER IS LOAD-BEARING.** There is a SECOND consumer nobody had recorded —
   `+app/+stimulus/tuning_response.m:253-254` loads valid intervals and restricts its read window
   to `interval(1,1)`..`interval(1,2)`, the FIRST interval only:

       $ git show origin/main:src/ndi/+ndi/+app/+stimulus/tuning_response.m | sed -n '255p'
         [data,t_raw,timeref] = readtimeseries(ndi_timeseries_obj, ts_epoch_timeref.epoch, ...
             interval(1,1), interval(1,2));

   In v1 that order is array-append order (`vi(end+1) = validintervalstruct`). Decomposing to
   several statements makes "first" undefined unless order is preserved explicitly. So this class
   is load-bearing for ANALYSIS, not just bookkeeping.

**NOTHING REFERENCES IT BY ID** (0 of 91 NDI templates, 0 DID-matlab migrator references), so a
decompose cannot strand a referent.

**No `TEAM-SIGN-OFF` line is written by Claude.** The board keeps rendering this family as HISTORICAL-SIGNOFF-CLAIM
awaiting review until the team writes one.

---

### CORRECTION 2026-08-11 — the `generic_file` decision note above got two things wrong

Written by Claude, after the build. The decision itself is UNCHANGED and correct; two of the
FACTS I recorded beside it were not, and both erred in the direction this project punishes —
they made the remaining work look smaller and tidier than it is.

**1. "THE ONE REMAINING BLOCKER IS ONE FIELD" WAS TWO FIELDS.** `content_hash` was one. The
other is that `date_created` and `date_updated` — filesystem datenums the writer computes at
`+setup/+conv/+babu/import.m:522-523` and `:571-572` — have **NO HOME**. The signed
`data_body` model lists `format`, `compression`, `filename`, `content_hash` and `description`,
and no dates. `build_v_eta.py` already carried a comment saying exactly this ("no content_hash
... and no created/updated dates"); my summary said one field and was wrong against a note
already in the tree.

The fold DROPS them and COUNTS the drop (`date_fields_dropped`, 1 in the fixture run) rather
than inventing a slot, which is right. **This is an open modelling question, not a closed one:
where do a file's creation and modification timestamps live?** It is a sibling of the "DATE OF
BIRTH has no home" item already recorded in `CLAUDE.md` — the same shape, one tier down.

**2. THE JOIN IS NOT ALWAYS TO A `subject_group`.** That is the PLASMID branch. The LC-MS
branch fills `document_id` from `lcmsTable.SubjectDocumentIdentifier`, itself filled at
`import.m:550` from `subjectTable.SubjectDocumentIdentifier` — a **subject** id — and only the
single `All_set` row is overwritten with the group id at `:562`. So the referent is sometimes a
subject and sometimes a group. The V_eta tombstone had this right (`must_refer_to_document_class:
subject`); my note narrowed it. The built pass checks that the id RESOLVES IN THE BATCH and
never checks its class, which is the correct behaviour and is what makes the narrowing harmless
in code but not in the record.

### TEAM DECISION 2026-08-11 — `generic_file`'s timestamps are DROPPED AND COUNTED

Team, jess@walthamdatascience.com, 2026-08-11, verbatim: **"Dropped and counted."** — asked
whether `date_created` / `date_updated` should be added to `data_body`. They should not. The
fold's existing behaviour stands: the dates are discarded and the discard is COUNTED
(`date_fields_dropped`), so the loss is visible in every corpus report rather than silent.

**THE EVIDENCE, re-derived from NDI `origin/main` rather than argued:**

        DENOMINATOR: 91 NDI templates; 3 carry any date-ish field
          generic_file           -> dateCreated, dateUpdated   <- the only FILE dates
          imageStack_parameters  -> timestamp
          treatment_transfer     -> timestamp

1. **`data_body` is a SHARED tier.** Every `sampled_body` and `opaque_body` inherits it. Two
   fields serving ONE source class out of 91 would land on hundreds of thousands of documents
   that have no file at all.

2. **They are not properties of the data.** `ndi.fun.file.dateCreated` shells out to `stat`
   (Linux/macOS) or `dir /T:C` (Windows) and returns NaT when it cannot tell — it is the
   filesystem birth time ON WHICHEVER MACHINE RAN THE IMPORTER. `filename`, `format` and
   `content_hash` survive a copy unchanged; ctime and mtime do not. `content_hash` is exactly
   the field that makes ctime redundant for identity.

3. **Nothing reads them.** The only non-writer references in NDI are two test files setting
   them to 0 (`DownloadGenericFilesTest.m:53-54`, `:137-138`); `downloadGenericFiles.m:109`
   reads `generic_file.filename` only.

**THE TWO DATES ARE NOT EQUAL, and this is the part to remember if it is ever re-opened.**
`dateCreated` is almost always the copy/import moment. `dateUpdated` often survives a copy and
can be the real last-modified time — and NDI ITSELF treats mtime as meaningful in one place:
`+setup/+conv/+babu/import.m:438` uses `ndi.fun.file.dateUpdated(imStackFile)` as the
imageStack `timestamp`, an acquisition-time proxy. **Note WHERE it put it: a typed `timestamp`
on the DOMAIN CLASS, not on the byte carrier.** If these are ever kept, that is the shape to
copy — or an `absolute_reference` on the statement, which is machinery V_eta already has and
which costs no field on a shared tier. If only one is kept, keep `dateUpdated`.

**STANDING CAVEAT:** ZERO `generic_file` documents appear in any of the six corpora, so there is
no usage evidence in either direction. Per the standing rule, that is not evidence they are
unused — `generic_file` is written by the Babu converter for datasets not among the six. The
counter is what will say if a real dataset ever brings some.

---

### TEAM DECISION 2026-08-11 — `valid_interval` inheritance is RE-DERIVED, not materialised

Team, jess@walthamdatascience.com, 2026-08-11, verbatim: **"Re-derive seems right to me"** —
answering the sub-question left open by the `valid_interval` decision above.

**WHAT WAS DECIDED.** A validity statement is stored ONCE, on the element it was measured for.
Anything asking about a DERIVED element follows `derived_from` up the chain and uses the
statement it finds there. The migration writes no copies onto derived elements.

**IT PRESERVES NDI'S EXISTING SEMANTICS EXACTLY.** This is not a new rule — it is the rule
`ndi.app.markgarbage` already implements. `loadvalidinterval` finds nothing on the element it
was asked about and falls back to `underlying_element` AT THE MOMENT OF THE QUERY. Materialising
would have replaced a query-time walk with migration-time copies, i.e. changed the semantics
into something faster to read and capable of going stale.

**WHY, IN ONE LINE:** the same quality judgement stored N times can be corrected in one place
and left wrong in the others, with nothing to flag the disagreement. That is the failure this
project keeps paying for, and it is worse for a QUALITY judgement than for data, because a stale
"this stretch is good" is silently wrong rather than visibly missing.

**THE COST IS REAL AND LANDS ON CONSUMERS, NOT ON THE MIGRATION.** Every "is this good data?"
question must walk `derived_from`. A consumer that forgets gets "no validity information"
instead of the right answer — and per hazard 1 of the parent decision, absence MEANS VALID, so
a forgotten walk reads as *all good* rather than as an error. **That is the sharp edge of this
choice and it should be built against, not just noted:** the walk belongs in ONE shared
resolver, written once, rather than reimplemented by each caller.

        v1 consumers of validity, for scale:
          ndi.app.markgarbage            loadvalidinterval / identifyvalidintervals
          +app/+stimulus/tuning_response.m:253-255   (uses interval(1,...) only)

**`inheritance_candidates` IS NOT MOOT — ITS PURPOSE CHANGES.** It was built to DECIDE this
question; the team decided on principle instead. It still matters, now as a SIZE: it counts the
subjects NDI's `underlying_element` fallback actually serves, which is exactly how many
documents depend on the walk existing. A zero means no corpus we hold exercises inheritance at
all (and per the standing rule that is a fact about the sample, not about the universe); a large
number means the shared resolver is load-bearing rather than theoretical. Read it as scope for
the consumer-side work, not as evidence for or against the decision.

**AND A ZERO CARRIES NO INFORMATION AT ALL TODAY. SHARPENED after the build reported it.**
The sentence above ("a zero means no corpus we hold exercises inheritance") is too generous to
the counter. `inheritance_candidates` is conditional on `sources_seen`, and **all six corpora
hold ZERO `valid_interval` documents** — so the counter is STRUCTURALLY zero on everything we
currently measure, whatever the truth about inheritance is. **Never read it without
`sources_seen` beside it.** Zero sources and zero candidates is "we did not look", not "we
looked and found none" — this repository's oldest failure, in a counter built this week.

This also settles, retrospectively, that the team was right to decide this on principle rather
than wait for the measurement: the measurement could not have arrived from the corpora we hold.
It becomes informative the first time a dataset carrying markgarbage documents is migrated.

**NOTHING IN THE BUILD NEEDS UNDOING.** The `valid_interval` build was instructed to leave both
answers open, so the stored form — one statement per source, ids preserved — is already what
re-derive requires. What this decision ADDS is the consumer-side resolver, which is new work and
is not yet written.

**No `TEAM-SIGN-OFF` line is written by Claude.** HISTORICAL-SIGNOFF-CLAIM

---

### TEAM DELEGATION 2026-08-11 — binding governance, ONE question, delegated

Team, jess@walthamdatascience.com, 2026-08-11, verbatim:

> **"Do binding governance as you see fit. We can always change later."**

**THIS IS A DELEGATION OF ONE QUESTION, NOT OF THE FAMILY, and the question it delegates is
the MECHANISM for a rule the team had ALREADY SIGNED the day before.** Recorded verbatim so a
later reader cannot widen it. What it did NOT authorise, spelled out because each was live and
adjacent while the work was done:

- **NOT arming binding conformance.** The switch stays off (see below).
- **NOT naming an admissible set** for `variable` / `method` / `purpose` (option C stands).
- **NOT changing any class's disposition, and no migrator was touched.**

#### The rule was already signed; only the mechanism was open

`V_eta_tenet_audit.md`, TEAM-SIGN-OFF [binding governance], jess, 2026-08-10:

> ... **STRENGTH IS AUTHORITATIVE ON THE FIELD**, with the registry required to agree where
> it also states one ...

So "which is authoritative" — the second of #32's two open questions, and the one
`CLAUDE.md` still described as undecided — was decided on 2026-08-10. The 2026-08-11
delegation covers HOW that is made true: derive, check, or leave it to a test.

#### What was built (2026-08-11)

**THE FIELD IS AUTHORITATIVE. The registry's `strength` is DERIVED and regenerated, never
hand-edited.**

        DENOMINATOR: 4 registry lists, 38 rows -- 5 subject_statement_bindings,
                     26 relation_bindings, 3 entity_field_bindings,
                     4 binding_examples (illustrative).
                     34 normative; 3 carry a strength, all entity_field_bindings.
                     14 bound field declarations, over 243 document_class files
                     and 1026 field declarations walked; 2 of the bindings are
                     NESTED (relative_reference.value.relation / .frame).
                     14 of 14 declare a strength. 11 of 14 have NO registry row.
        OVERLAP:     3 -- dataset.accessibility / .ethics_assessment /
                     .experimental_approach, stated in BOTH places. They agreed.
                     Nothing made them agree.

1. **`tools/regen_binding_strengths.py`** derives each registry row's `strength` from the
   field constraint. Wired into `tools/gates.py` between `build_v_eta` (which writes BOTH
   sides) and `pytest` / `check_binding_governance` (which read the filled column) — 17
   steps now, 19 edges, all substantiated. `build_v_eta.py` **no longer hand-authors the
   key**: restoring it would be inert, which is worse than wrong, because an editor would
   change a literal, see the built file agree, and believe the rule had moved.
2. **Disagreement fails, four ways** — `gates.py --check`'s artifact diff (the registry is
   named as its own row), the tool's own `--check` in the composed block,
   `test_veta.py::test_field_and_registry_strengths_agree`, and
   `check_binding_governance.py` **now run with `--enforce`** (B5's baseline is 0; the driver
   had been running that ratchet report-only, so a disagreement printed and exited 0).
3. **A BINDING WITH NO `strength` IS AN ERROR.** Not inherited, not defaulted, not skipped.
   Both candidate defaults are wrong in a dangerous direction: `preferred` makes an ungoverned
   field read as governed, `required` arms a gate nobody measured on a 0-quarantine corpus.
   Enforced at TWO scopes, because the generator can only refuse the 3 rows the registry
   catalogues: the tool errors on a row it cannot derive, and
   `test_binding_strength_derivation.py::test_every_binding_in_the_built_tree_declares_a_strength`
   asserts it over all 14 declarations, **including the 11 that no registry row watches**.

**WHY DERIVE RATHER THAN MOVE THE TRUTH TO THE REGISTRY.** The validator already walks the
class chain and holds `constraints.binding` when `checkBinding` runs, so a registry read at
validation time re-implements a lookup it has already done against a file it does not open.
Making the registry authoritative would need a strength on **31 rows** (34 normative, 3 carry
one) purely to relocate a fact — 31 new hand-authored assertions, each able to disagree with a
field. And the registry's real job is a CATALOGUE — *what* is bound, to *which* vocabulary —
answerable without walking 249 files, which is a different question from how hard it is
enforced.

#### STILL OPEN — and NOT delegated

- **The admissible set for `variable` / `method` / `purpose` (option C, the other half of
  T8).** All three now carry `{strength: preferred, node_form: curie}`, which binds the FORM
  and not the VALUE SET: a CURIE that resolves to nothing passes. T8's actual claim — the
  registry maps `variable` onto a value_set — is **unimplemented for the field the whole
  system pivots on** (`term.value` is `keyed_by: variable`, and that lookup reaches 5 rows,
  all of them `term_assertion`). **BLOCKED**: membership needs NDIC.txt, which moved to
  `VH-Lab/ndi-ontology-matlab`, a repository this session could not attach. Recorded, not
  built.
- **Arming binding conformance.** `+did2/+schema/cache.m` carries a `case 'binding'` calling
  `checkBinding`, gated by `strictMode('BindingConformance')`, **DISARMED by default** and
  asserted so by `testBindingConformanceIsDISARMEDByDefault`. It stays off. Arming it is a
  separate decision with a separate blast radius, and nothing has counted how many real
  documents a `required` binding would quarantine.
- **`strength` is not yet formalised in the meta-schema.** The no-default rule is enforced by
  the generator and by pytest, not by `did_schema_meta.json`'s `binding` object — which also
  does not declare `root` / `source` (B1, 15 undeclared key uses) and accepts arbitrary keys
  (B2). Formalising it is the same edit as closing B1/B2 and should ride with them.

---

### DEFERRED 2026-08-11 — what a GAP between `validity` statements means

Team, jess@walthamdatascience.com, 2026-08-11, verbatim: **"Can we skip this decision for
now?"** — yes. **DEFERRED, NOT RESOLVED.** Recorded here with the defect stated, so that parking
it costs nothing later.

**THE DEFECT, and it is in what was built today.** v1 semantics, from the writer:

        markgarbage.m:42   % MARKVALIDINTERVAL - mark a valid interval in an epoch
                           %                     (all else is garbage)
        markgarbage.m:172  if isempty(vi); intervals = [t0 t1]; return; end   <- no record: ALL valid
        markgarbage.m:200  if isempty(explicitly_good_intervals)
                               intervals = baseline_interval;                 <- none project here: ALL valid
                           else
                               intervals = explicitly_good_intervals;         <- ONLY these; GAPS ARE GARBAGE
                           end

So a v1 document makes a CLOSED-WORLD claim: the marked set is complete, and every gap inside
the epoch is garbage. The build decomposes one document into N statements, each saying "this
stretch is valid". **The closure does not survive the decomposition.** A v1 document saying
"only 10-50s is usable" becomes statements that a reader applying the class-level absence rule
reads as "everything is usable" — the exact inversion.

**WHAT WAS DONE WHILE DEFERRING (no decision taken, no behaviour changed).** The class
documentation used to state the absence rule unqualified, which invited that reading. It now
says the rule is scoped to NO STATEMENT AT ALL, that gaps are UNDEFINED and an open team
decision, and that v1's own answer is the opposite. **An undefined gap is safe to defer; a gap
silently read as valid is not.**

**THE TWO SHAPES THAT REMAIN** (both were costed; the other two are impossible, see below):

  **A — keep the decomposition, declare closure per statement.** Each statement carries an
  `exhaustive_over` edge to the epoch: *within this epoch, the statements sharing this subject
  and variable are the complete list.* Buildable today; `directed_relation.order` (`sequence` until T20) already exists. **Its
  weakness is that set identity is IMPLICIT** — a filtered query, a partial batch, or one
  statement quarantined leaves the survivors still claiming exhaustiveness, and the reader
  concludes the gaps are good data.

  **B — do not decompose; one statement carries the set.** `value` is already an ARRAY, so one
  statement holds N cells with `time_reference_1..N` and one `exhaustive` flag. Closest to v1 —
  one document in, one out — and **the document IS the set, so it cannot be partially present.**
  Blocked on role-naming the numbered references: pairing cell *i* with `time_reference_i` is
  positional today, and multiple references on one statement are already recorded as UNDEFINED
  in meaning until that lands.

**TWO SHAPES ARE NOT MERELY UNATTRACTIVE, THEY ARE UNBUILDABLE.** "Emit the complement as
`false` statements" and "invert the polarity and store only the bad" both need the epoch's
extent to compute the gaps. It does not exist:

        epoch             fields: ['local_identifier']
                          deps  : ['session_id','time_reference_#','instrument_id']
        acquisition_epoch fields: ['clocks','axes','channels','storage']

`epochMint` assigns the minted epoch no times at all. Do not re-propose either without first
giving the epoch an extent.

**WHY THIS SURFACED:** the team observed that ontology table rows also flag validity, and that a
spreadsheet flag means *this cell is no good* rather than *this cell is absent*. Both sources
agree that absence means valid; they differ in CLOSURE — markgarbage marks the good and claims
the rest is bad (closed world), a spreadsheet flags the bad and says nothing about the rest
(open world). That difference is what the gap question is. `ontology_table_row.m:470-490`
already refuses logical columns for want of a boolean leaf ("a logical wants a boolean leaf"),
so the second source is real and currently unmigrated.

---

### Team sign-offs

TEAM-SIGN-OFF [stranded sources]: jess@walthamdatascience.com, 2026-08-11 -- generic_file folds to term_observation + opaque_body; imageCollection is a tombstone. Both are BUILT and ran in 6 of 6 corpora in run 31522068566. THIS SIGNATURE COVERS TWO CLASSES, NOT THREE. `valid_interval` IS NOT SIGNED AND IS NOT DECIDED -- an earlier revision of this line included it, which was Claude's error: the team ASKED whether valid_interval should take that shape and then said "Can we skip this decision for now?", and a question was recorded as an answer. Corrected 2026-08-11 when the team caught it. WRITTEN BY CLAUDE AT THE TEAM'S EXPLICIT INSTRUCTION ("Please write the sign off for me. I give you permission this time."), a one-time authorisation and not a precedent: Operating Rule 4 otherwise forbids Claude from adding this line, and the next one is the team's to write.

*(Row #113's own text is in `git show 6523cb1:schemas/V_eta_OPEN_WORK.md`; "the row above" below refers to it.)*

**CORRECTION TO ROW #113, 2026-08-13, AND IT ENLARGES THE ROW.** The row above
says the epoch END TIME and CLOCK FRAME are lost. True, and incomplete: **the epoch
IDENTITY is dropped too, and recovering it comes FIRST.** Positive evidence, from
NDI's own template and from the migrator:

        $ git show origin/main:src/ndi/ndi_common/database_documents/data/pyraview.json
          superclasses: ['epochclocktimes.json', 'filter.json']

        $ grep -n "epochid" DID-matlab/.../+migrators_j/pyraview.m
          (no matches -- 0 of 267 lines)

`pyraview` is EPOCH-SCOPED BY DECLARATION: `epochclocktimes` is one of its two
superclasses, and that mixin carries the `epochid` block (which is why PRED's
document has one). Belonging to an epoch is part of what a pyraview IS. The
migrator reads NEITHER block, so migration loses the epoch dimension in two
pieces -- `epochid.epochid` (PRED: `EST_VISUAL_PREDROGA`) and the extent
(`t0_t1 = [0, 28.12495]`, `dev_local_time`).

**A CLAIM MADE EARLIER IN THE SAME SESSION WAS WRONG AND IS WITHDRAWN HERE:**
"epochMint already mints PRED's epoch from `epochid.epochid`". The v1 SOURCE
carries it; the MIGRATED bodies do not, and `epochMint` reads migrated bodies.
PRED's pyraview is the only document in that corpus carrying an epoch id, so
**PRED currently gets NO epoch minted at all** and there is nothing for a
`relative_reference` to anchor to. The two were conflated; they are not the same.

**SO THE BUILD IS THREE STEPS, NOT ONE**, and the signed decision describes only
the middle one:
  1. pyraview's output carries the epoch id forward, onto a body whose class
     DECLARES it -- a schema question first, since an undeclared block quarantines.
  2. epochMint mints the extent as a `relative_reference` off that epoch's
     `time_reference_#`.   <- the signed part
  3. pyraview's emitted observation gains its `epoch_id` edge once the epoch
     exists -- the deferred rewire `jEpochDocId`'s header describes, and the
     reason that seam returns '' for every did_v1 document today.

Step 3 makes this the first real instance of the epoch family (#60) landing,
not a pyraview-local fix. NOTHING IS BUILT.

TEAM-SIGN-OFF [epoch extent -- row #113]: jess@walthamdatascience.com / 2026-08-13 -- epochMint OWNS the epoch extent: it mints the relative_reference carrying the extent and clock frame, hung off the epoch's time_reference_#. pyraview.m stops dropping the epochclocktimes block so the mint can see it. REJECTED: adding a value slot to `epoch_bounded_reference`, which is not in the persist set. NOT YET BUILT.
    (Recorded by Claude at the signer's explicit consent, given in session_01BenWtpJyRu3QhEZqCErpwm after the decision was stated in conversation. Operating Rule 4 normally forbids Claude writing this line; the signer waived that here. The DECISION is the signer's -- this is transcription, not authorship.)

BUILD-STATE: 2026-08-15 -- **TWO OF THE THREE STEPS ARE BUILT; STEP 3 IS NOT.**
The signature above ends "NOT YET BUILT" and the row prose above it ends
"NOTHING IS BUILT". Both are stale, and the signature is NOT edited (Operating
Rule 4 -- the line is the team's), so the state is recorded here beside it.
HISTORICAL-SIGNOFF-CLAIM. Read step by step, because "partly built" is the
answer and a single verdict either way would be wrong:

        STEP 1 -- pyraview carries the epoch id forward.  BUILT.
          DID-matlab .../+migrators_j/pyraview.m:177
            epochRef.document_class = classBlock('epoch_bounded_reference', ...
          :244  obs.depends_on(end+1) = struct('name','time_reference_2', ...)
          The handle is emitted and hung off the observation as the SECOND
          member of the time_reference_# family; the two members differ by
          `value.clock` (the session anchor names none, this names
          dev_local_time), which is the CHANGE 5 uniqueness rule.

        STEP 2 -- epochMint mints the extent.  BUILT.  <- the signed part
          DID-matlab .../+convert/epochMint.m
          1663:%EPOCHEXTENTREFERENCES One `relative_reference` per DISTINCT
                clock of an epoch.
          1719:    ref.document_class = struct('class_name','relative_reference', ...
           414:    'epoch_extent_references_emitted',     0, ...
           776:        report.epoch_extent_references_emitted + numel(refs);
          Twelve `epoch_extent_*` counters, four of them NAMED REFUSAL REASONS,
          so a run that mints nothing says which refusal fired.

        STEP 3 -- the observation gains its `epoch_id` EDGE.  **NOT DEFERRED --
          FORBIDDEN. STEP 3 IS A PHANTOM AND MUST NOT BE BUILT.** Corrected
          hours after this note first called it a pending schema increment; the
          correction is below, because it is the more useful half.

**CORRECTION, 2026-08-15, THE SAME DAY THIS NOTE WAS WRITTEN.** Step 3 above
originally read *"NOT BUILT, and it is a SCHEMA increment, not a migrator
change"*, sourced to `pyraview.m:254-256`. Every FACT in that source sentence is
true and its CONCLUSION is backwards. TEAM-SIGN-OFF [epoch]
(`V_eta_epoch_plan.md:869`), verbatim: HISTORICAL-SIGNOFF-CLAIM

  > a document reaches its epoch through the TIME_REFERENCE CHAIN
  > (subject_interaction -> time_reference_# -> relative_reference ->
  > relative_to -> epoch) -- a direct `epoch_id` edge is added ONLY where the
  > epoch is the document's own content (`directed_relation`, per the ensemble
  > sign-off), **NOT on subject_interaction**

`voltage_observation` is UNDER `subject_interaction`, and the four classes that
DO declare `epoch_id` are exactly the four that are not:

        DENOMINATOR: 245 json file(s) under schemas/V_eta/ read; 241 class(es)
                     indexed; 4 declare an epoch_id edge
          acquisition_metadata_file  <- base                    required
          directed_relation          <- relation <- base        optional
          ingestion_manifest         <- base                    required
          method_parameters          <- base                    optional
          voltage_observation        <- subject_observation
                                     <- subject_interaction ... <- EXCLUDED

So `time_reference_2` IS the epoch link the signed model specifies, and steps 1
and 2 are the whole of what this signature asks pyraview and epochMint to do.
**All three steps are accounted for: two built, one ruled out. Nothing in this
row is outstanding.**

`jEpochDocId.m:11` -- *"THIS RETURNS '' FOR EVERY did_v1 DOCUMENT TODAY, BY
CONSTRUCTION"* -- is correct and is about those four classes, not about
observations. It is not evidence of a gap here.

**HOW THIS GOT WRITTEN, because the mechanism matters more than the row.** The
row's own closing sentence -- *"Step 3 makes this the first real instance of the
epoch family (#60) landing"* -- predates the 2026-08-10 amendment that added the
NOT-on-subject_interaction clause, and nothing reconciled the two. It was then
read forward as pending work, by me, inside a `BUILD-STATE:` note whose entire
purpose was to stop build claims going stale. That is tell (3) of the 2026-08-12
open-list reconciliation -- *a phantom: work REJECTED by a signature rather than
deferred* -- and the #52 shape exactly: a note left standing that instructs the
one build a signature rules out. `pyraview.m:254` carried the same sentence and
is corrected in the same pass (DID-matlab).

**AND IT IS THE FIRST ERROR IN THIS FILE'S DANGEROUS DIRECTION IN SOME TIME.**
The plan-header staleness, the governance rung and the open-list reconciliation
all UNDERSTATED progress; the cost was work repeated. This one OVERSTATED what
remains, and its cost would have been a schema edit that contradicts a
signature. Both are the same defect and neither direction is the safe one.

**UNVERIFIED:** every line above is read from source in a container with no
MATLAB. What a PRED run proves is narrower and is asserted NDI-side, not here:
`TestMigrateLocalEtaPRED.m:205/:208/:211` -- `epoch_bounded_reference` absent,
`epoch` and `relative_reference` present.

---

**COUNT CORRECTION, 2026-08-17 — `receptive_field` and `receptive_field_calculation` were
minted** (TEAM-SIGN-OFF [receptive field naming], `V_eta_ngrid_family_findings.md`). The
dated measurements above are left exactly as taken; this is the live claim beside them:

        DENOMINATOR: 249 json file(s) under schemas/V_eta/ read
        243 distinct V_eta class names
        42 direct subclasses of `data_type`

Only the COMPOSITE is a `data_type` subclass — the leaf hangs off
`subject_calculation` — which is why the class count moved by two and the
data_type-subclass count by one. One signed decision moved four counters at once
(these three plus the inert-set canary in `tests/test_veta_stimulus_response.py`),
which is the per-document cost `check_prose_counts` exists to find.

### TEAM DECISIONS 2026-08-20 — two calls made to close Soph's Bar-2 gap

Recorded here as prose, NOT as a `TEAM-SIGN-OFF` marker (Operating Rule 4); if the
epoch/stimulus plan documents need a formal signature to move their board state, the
team adds it. Both calls were made by jess@walthamdatascience.com after the first
full-corpus Soph e2e run (run #7, `02698b58c`) revealed the three unfolded survivors
recorded in the MEASURED section above (`epochfiles_ingested` 349, `syncrule_mapping`
348, `stimulus_presentation` 2). Neither call is new modelling — each resolves a live
ambiguity in an ALREADY-SIGNED plan.

**DECISION #2 — `epochfiles_ingested` → `ingestion_manifest`: `epochprobemap` decomposes
to EDGES (option B), built BEFORE the fold ("B-first").** The signed #60 epoch plan
carries a self-contradiction — *"epochprobemap REMOVED — decomposes into edges (option B)"*
AND *"B as the model, A as pass-1 behaviour"* — and `build_v_eta.py` built the class in
B-shape (no probemap field), so pass 1 has nowhere to put a field that is populated on
2,484/2,484 corpus-B documents (`name/reference/type/devicestring/subjectstring`,
per-epoch neuron/device/subject attribution). The team chose **B-first**: build the
probemap→edges decomposition (the final shape), then fold `epochfiles_ingested`. This
picks the "give it a home via edges, don't keep it as text" horn and closes the option-A
interim. Evidence basis: `+migrators_j/epochfiles_ingested.m` BLOCKER 2 (the migrator's
own guarded-passthrough header).

**DECISION #3 — build the stimulus decompose NOW.** The #31 stimulus model is signed
(`timed_sequence` + `timed_sequence_manipulation`, the ensemble/dedup pattern) but
unbuilt and four-way blocked (no subject knowable at pass 1; the stimulus dictionary
lives in referenced docs that do not exist yet; dedup is whole-corpus; `timed_sequence`
is declared `"abstract": true`). The superseded `stimulusPresentationToManipulation`
assembler still runs unconditionally in NDI `local.m` and mints the old
`visual_grating_manipulation` shape (Soph pass-1 had 175 `stimulus_presentation`, only 2
survive — the rest folded to the superseded target). The team chose to **take on the full
second-pass decompose now**: un-abstract `timed_sequence` (itself a team call per the
2026-08-10 correction note in this file), build the whole-corpus dedup + the manipulation
leaf + the `relative_reference`/per-trial `sampled_body`, and RETIRE the superseded NDI
assembler rather than extend it. Evidence basis: `+migrators_j/stimulus_presentation.m`
(the four-blocker header + the "one more thing the second pass must not do" section).

**CORRECTION 2026-08-20 (same day) — THE PARAGRAPH ABOVE IS BASED ON STALE STATE;
MOST OF #3 IS ALREADY BUILT.** A design pass verified against the branch that the
premise ("the superseded assembler still runs; 173/175 fold to the superseded shape")
is PRE-2026-08-17. On this branch, positive evidence from the code:

        $ grep -n stimulusPresentationToTimedSequence NDI-matlab/src/ndi/+ndi/+migrate/local.m
        2154:  ndi.migrate.internal.stimulusPresentationToTimedSequence( ...
        $ grep -c '"abstract"' DID-schema/schemas/V_eta/draft/timed_sequence.json \
              DID-schema/schemas/V_eta/stable/visual_grating.json
        0
        0

  The second pass calls the NEW `stimulusPresentationToTimedSequence` (the superseded
  `stimulusPresentationToManipulation` is gated off, retained only for the
  presentation-less single-grating case); `timed_sequence` and `visual_grating` are
  ALREADY un-abstracted (team decision 2026-08-17, `build_v_eta.py`). So the Soph
  presentations that dropped out of the survivor census almost certainly folded to the
  CORRECT `timed_sequence_manipulation`, not the superseded shape. The "take it on now"
  call is therefore largely MOOT. WHAT ACTUALLY REMAINS: (a) DONE 2026-08-20 — the three
  decompose tests were wired into `test-eta-migrate.yml` (they had never run on a
  claude/** push, so the two-emitter exclusivity guard was unchecked); (b) re-measure
  Soph post-decompose to confirm 0 orphans; (c) the ONE genuine open build — the
  multi-subject `storage_mode: reference` case has no emitter (the code takes `animals{1}`
  only, always `inline`), which is team-gated; (d) two schema/dedup questions (the
  `presented_id` family `_#` marker; confirming the dedup key is `isequal` on the emitted
  grating value, not a hash of raw parameters). This correction points the direction this
  file is NOT known for — LESS to build than claimed — and is recorded so no agent
  re-builds the 2026-08-17 work.

Build order chosen: (1) `syncrule_mapping` post-`epochMint` anchoring (decision-free,
smallest), (2) #2 `epochprobemap`→edges then the `epochfiles_ingested` fold, (3) #3 the
stimulus decompose. Each lands with fixture tests then a full-corpus verify.

---

## DATED MEASUREMENTS (verbatim)

### MEASURED — all five corpora, run #2 (2026-08-09)

`test-corpus.yml` run #2 at DID-matlab `6a9421b` / DID-schema `61f9439`. All six
jobs green. **The numbers below were read out of the per-job STDOUT: the reports
were never uploaded (see the artifact-path defect, fixed in `e532dae`), so the
digest aggregated nothing.** JH, PRED and 20211116 were not read in detail — only
Soph, B and Dab are quoted here.

        corpus B    12,917 docs   6,207 carry an epoch id,   149 distinct
                    epoch_ 0 / whole_session_ 0 / other 149 (6,207 docs)
                    142 id(s) span >1 session
                    session documents 14   distinct session_id 14
                    approaches 0
        Soph       101,427 docs   4,931 carry an epoch id,    18 distinct
                    epoch_ 0 / whole_session_ 0 / other 18 (4,931 docs)
                    12 id(s) span >1 session
                    session documents 33   distinct session_id 33
                    approaches 0
        Dab         27,561 docs  10,052 carry an epoch id, 1,754 distinct
                    epoch_ 1,605 (3,845 docs) / whole_session_ 0 / other 149 (6,207 docs)
                    142 id(s) span >1 session
                    session documents 16   distinct session_id 16
                    approaches 635 over 635 epochs

**1. A CORRECTION TO WHAT WAS WRITTEN HERE AFTER CORPUS B ALONE.** That entry said
*"the prefix analysis describes no document in this corpus"* and generalised from
one corpus. **Dab has 1,605 distinct `epoch_` ids over 3,845 documents**, so the
`ndi.file.navigator` writer the plan is built around IS represented. The earlier
sentence was true of B and Soph and false as a general claim. This is the corpora-
are-a-sample rule catching me one entry after I invoked it.

**2. WHAT DOES HOLD, ON ALL THREE: ZERO `whole_session_` ids anywhere.** The
synthetic-collision hazard the plan devotes its HAZARD section to has **no
instances at all** in the measured corpora. It is a real writer and may appear in
a dataset still waiting to migrate — but nothing here exercises it.

**3. THE REAL COLLISION IS IN THE BUCKET THE PLAN DOES NOT MODEL.** The
cross-session count tracks the `other` bucket exactly: B has only `other` ids and
142 collide; Dab has the same 149 `other` ids and the same 142 collide, while its
1,605 `epoch_` ids add none. So **`epoch_<uid>` is globally unique exactly as the
plan says, and the collisions are entirely among the bare local names** (the
`"t00023"` shape). **Grouping on `epochid.epochid` alone would fuse epochs across
sessions**; the key must be at least `(base.session_id, epochid.epochid)`.
(Note B's `other` figures — 149 distinct, 6,207 docs, 142 colliding — are
IDENTICAL to Dab's. The two corpora appear to share documents. Not investigated;
do not treat B and Dab as independent samples without checking.)

**4. #51 IS ANSWERED, AND CLEANLY: session documents match distinct session ids
1:1 in all three — 14/14, 33/33, 16/16.** The referent a REQUIRED `relative_to`
needs exists. This is the check fork A was gated on. JH, PRED and 20211116 still
to read.

**5. #76 IS NOT ANSWERED, AND THE RESULT AS PRINTED CANNOT BE TRUSTED.** Dab holds
all 635 approaches, over 635 distinct epochs — exactly one approach per epoch —
and reported **635 approach epochs with NO presentation document**, i.e. every
one. Dab is known to hold ~1,242 `stimulus_presentation` documents, so either the
approaches and the presentations genuinely carry disjoint epoch ids, or the census
never saw the presentations. **The census as run could not tell those apart: it
reported no denominator for the presentation side.** Fixed in `e532dae`
(`presentation_doc_count`, `presentation_docs_with_epoch`); re-run before reading
anything into this. Dab also printed one distribution row with a BLANK subject
count against 0 epochs — a phantom row from an empty distribution, also fixed.

**6. THE STIMULUS-RESPONSE REPAIR IS CONFIRMED ON REAL DATA.** Soph's silent-loss
census now reads **175 empty required edges, 0 vacuous required fields**, and the
only row is `stimulus_presentation.element_id` (held for #31). The 11,167
`stimulus_response_scalar_parameters_basic.stimulus_response_scalar_id` empties
that dominated the previous census are GONE — that schema half was in the
`61f9439` the run picked up.

**7. QUARANTINES ARE ENTIRELY THE `epochfiles_ingested` REGRESSION**: Dab 4,088,
B 2,484, Soph 349 — every quarantine in every corpus, one cause, fixed in
`8987265`. A re-run should return all five to 0.

### MEASURED 2026-08-20 — the FIRST full-corpus Soph Bar-2 census (e2e run #7, `02698b58c`)

The Soph NDI end-to-end test (`ndi.unittest.migrate.TestMigrateLocalEtaSoph`) ran over the
WHOLE corpus for the first time — every prior Soph e2e either timed out (OOM at 2h41m in the
shared job; the standalone run hit the 350-min cap twice) or was cut to a 25000-document
SUBSET to localise the migration sink. The three perf fixes (`buildV1Sqlite` one-transaction
build, `bodyResolver` O(n²)→O(n), and the DID-matlab `sqlitedb.add` per-document→per-batch
commit) brought the full run in at **2h43m**, well under the 6-hour runner cap. Job
`96442236315` conclusion **success**; `5 Passed, 0 Failed, 0 Incomplete; 9771.9 s`.

**THE SUBSET UNDER-REPORTED BAR-2, AND THAT IS THE FINDING.** The 25k subset (first 25000
documents) showed survivors `params_basic 3708 / subject 970 / session 14 / stimulus_presentation 1`
and was reported as "Soph at Bar-2 modulo the signed #61 deferral". The full corpus contains
`epochfiles_ingested` and `syncrule_mapping` documents that sit BEYOND the first 25000, so the
subset could not see them. **The corpora are a sample and so is a subset** — the same standing
rule, one level in.

Both census stages quoted verbatim from the run log; nothing transcribed from memory.

```
PASS 1 — unconverted (migrator returned its input)
  DENOMINATOR: 101427 read, 212954 migrated, 0 quarantined; fragments 0
  unconverted: 21781, by class (7):
    11167  stimulus_response_scalar_parameters_basic
     9851  stimulus_response_scalar
      349  epochfiles_ingested
      175  stimulus_presentation
      175  daqmetadatareader_epochdata_ingested
       32  syncgraph
       32  subject

BAR-2 FINAL-OUTPUT V1 SURVIVOR CENSUS (after the batch post-pass chain)
  DENOMINATOR: 101427 source doc(s), 212954 destination doc(s)
  v1 source class names still labelling a destination document: 6
    11167  stimulus_response_scalar_parameters_basic  SIGNED verify-before-delete deferral (#61)
     3169  subject                 persist (v1 class IS the V_eta class)
      349  epochfiles_ingested     UNFOLDED — a Bar-2 gap
      348  syncrule_mapping        UNFOLDED — a Bar-2 gap
       33  session                 persist (v1 class IS the V_eta class)
        2  stimulus_presentation   UNFOLDED — a Bar-2 gap

READ-BACK (one of Soph's 33 sessions): daqsystem_load 3, getelements 27
```

**THE SECOND PASSES WORKED.** `stimulus_response_scalar` (9851), `daqmetadatareader_epochdata_ingested`
(175) and `syncgraph` (32) are all present in the pass-1 unconverted list and ABSENT from the
final survivor census — `resolveResponseParameters`, the metadata-reader arming in `epochMint`,
and `resolveClockAlignment` consumed them. The test PASSED because its survivor census is
report-only; the hard gates it asserts (0 quarantine, session opens on `did2sqlite`, calc
id-preservation, read-back) are all green.

**WHERE SOPH STANDS, and it decides nothing — Operating Rule 4.** Bar-1 is achieved on the
full corpus (0 quarantine, 0 dangling, read-back works). Bar-2 is NOT fully reached: beyond
the signed #61 deferral and the two persist classes, THREE unfolded survivor classes remain,
each mapping to a tracked, still-pending build:

| survivor | count | tracked as |
|---|---|---|
| `epochfiles_ingested` | 349 | #60 epoch family (renamed `ingestion_manifest`; tombstone leaves when the fold lands + a corpus proves it) |
| `syncrule_mapping` | 348 | #57/#60 — the clock-alignment row already records this as "STILL OPEN, gated on #60's epoch pass" |
| `stimulus_presentation` | 2 | #31 stimulus model (#43 held for #31) |

So the subset's "Bar-2 modulo the signed deferral" was optimistic by three tracked items.
None is a new discovery; all three are already on the build queue. The first full-corpus
verify the clock-alignment row (#57) asked for now EXISTS, and it confirms `syncrule_mapping`
must stay until #60's epoch pass lands.

### MEASURED 2026-08-10 — corpus run 31415147934 (`02854c7`), census digest job 93561591223

Two questions that three builds were each blocked on are now answered from the same run.
The digest text is quoted verbatim; nothing here is transcribed from memory.

```
REPORT SEARCH: 6 file(s) matching *-summary.json under 'corpus-reports',
               'tests/corpus-reports' (3 director(ies) walked, 0 duplicate(s) collapsed)
DENOMINATOR:   6 corpora, 221,827 v1 documents read, 0 unreadable
               (20211116 1220 / B 12917 / Dab 27561 / JH 78688 / PRED 14 / Soph 101427)
```

#### #51 RE-CONFIRMED on a second, later run. A `session` document exists in every corpus, one per session id.

Row 51 already records this from run 31327383671 (2026-08-09). This is an INDEPENDENT
re-measurement on a different run of a different commit, and it agrees to the document.

```
20211116   session documents: 1    (distinct base.session_id: 1)
B          session documents: 14   (distinct base.session_id: 14)
Dab        session documents: 16   (distinct base.session_id: 16)
JH         session documents: 3    (distinct base.session_id: 3)
PRED       session documents: 1    (distinct base.session_id: 1)
Soph       session documents: 33   (distinct base.session_id: 33)
```

Six of six, and in every corpus the count EQUALS the number of distinct session ids — so
there is no session whose document is missing. This is the fork-A verification
`V_eta_time_reference_model_plan.md` made a prerequisite for **`relative_to` REQUIRED**, and
it is the measured refutation of the old "no session document exists anywhere" claim. That
claim came from a grep that could not have matched; this comes from the census.

**`relative_to` REQUIRED has no remaining prerequisite.**

#### THE EPOCH MINT MUST KEY ON `(session_id, epoch_id)`, NOT ON THE ID STRING

The epoch plan named ONE grouping hazard — the synthetic `whole_session_<reference>` id, which
is minted per ELEMENT and so evaluates the same for every element in a session. That hazard
measures **ZERO in all six corpora**. A *different* hazard is non-zero:

```
                 synthetic (whole_session_) ids   ids spanning >1 session
20211116                     0                            0
B                            0                          142        <-- of 149 distinct
Dab                          0                          142        <-- of 1754 distinct
JH                           0                            0
PRED                         0                            0
Soph                         0                           12        <-- of 18 distinct
```

**One `epoch` document per distinct `epochid.epochid` string would FUSE epochs that belong to
different sessions** — 142 strings in B, 142 in Dab, 12 in Soph. In B that is 142 of 149
distinct ids, i.e. almost the whole corpus. The mint key must be the PAIR.

Two things worth stating plainly about this row:

1. **The plan predicted hazard A and the instrument found hazard B.** The prediction was
   sound reasoning about a writer; it was simply not the failure the data has. This is the
   argument for measuring before minting, made concrete.
2. **B and Dab report identical figures** for the `other` bucket (149 distinct / 6207 docs /
   142 spanning). Two corpora agreeing to the document is more likely a shared source than a
   coincidence, but nothing here establishes that — flagged, not asserted, and it does not
   change the disposition either way.

#### The 2,670-document `stimulus_presentation.element_id` row, per corpus

```
B 1242 / Dab 1242 / Soph 175 / 20211116 11        total 2,670
```

Repaired 2026-08-10 by the `stimulus_presentation` tombstone (the invented `element_id` is
replaced by NDI's real `stimulus_element_id`). **That is a prediction until a corpus run at or
after that commit reports it**, exactly like the `image_stack` guard. The same run still
carries `image_observation.subject_id` at 4,563 (JH), also pre-guard.

**MEASURED 2026-08-10, corpus run 31438980133 (`fd36421`) — the prediction HELD on the two
corpora that finished.** Both report zero, and both report a non-zero denominator alongside,
so this is a measurement and not a dead instrument:

```
DENOMINATOR: 2 of 4 affected corpora reported; Dab and Soph were CANCELLED mid-flight
             (test-corpus.yml sets concurrency cancel-in-progress, and a later push
             killed them), so they are UNMEASURED, not zero.

  B          12917 v1 documents read, 0 unreadable
             silent-loss: 0 empty required edge(s), 0 vacuous required field(s)
             was 1,242                                          -> 0
  20211116   silent-loss: 0 empty required edge(s)
             was 11                                             -> 0

  Dab        was 1,242                                          -> NOT MEASURED
  Soph       was   175                                          -> NOT MEASURED
```

So 1,253 of the 2,670 documents are confirmed repaired on real data and the remaining 1,417
are merely expected. B is the meaningful one: it is the largest single contributor to the row
and it also returns `quarantine_count: 0` and `fragments: 0`, so the repair did not buy the
empty edge back as a quarantine somewhere else.

**The same run found a NEW gating orphan, in the class this row's sibling repair created.**
`clock_alignment_policy.session_id` dangled on BOTH reporting corpora — 1 of 2814 edges on
20211116 and **13 of 19069 on B** — and in both cases it is 100% of the class (1 of 1
syncgraph, 13 of 13). Cause and fix are recorded in the header of
`DID-matlab/src/did/+did2/+convert/+migrators_j/syncgraph.m`: the migrator filled a
`must_refer_to_document_class: session` edge from `base.session_id`, which is a DIFFERENT ID
SPACE from a session document's `base.id` (`ndi.document.m:57` mints one, `ndi.session.m:215`
sets the other, separately). `did2.convert.epochMint` had refused that exact assumption in
its own header; `syncgraph.m` was written in parallel and made it. The fold is now gated
behind `jSessionDocId`, which answers `''` by construction in pass 1, so every real document
passes through until a batch pass supplies the id. **Not yet re-measured** — the fix
(`fef145f`) postdates the run that found it.

---

### MEASURED 2026-08-12 — WHICH v1 CLASSES A CORPUS RUN CAN EVER PROVE, AND WHICH 57 IT CANNOT

Re-derived in-session by fetching all six corpus archives from the public S3
prefix and censusing them by `document_class.class_name` (normalised: lowercase,
underscores stripped). Independent of `sourceCensus.m`, and it lands on the same
figure the harness prints for itself (`epochMint.m:39`), which is why it can be
quoted:

        DENOMINATOR: 6 corpora, 221,827 v1 documents censused, 0 unparseable
        20211116 1,220 (21 classes) + B 12,917 (18) + Dab 27,561 (26)
        + JH 78,688 (15) + PRED 14 (10) + Soph 101,427 (32)
        distinct normalised class names across all six: 45
        ledger rows: 102   PRESENT in >=1 corpus: 45   ABSENT from all six: 57

**So the CORPUS-PROVEN rung can never exceed 45 of 102 with the corpora we
hold.** The 57 are UNTESTED, NOT CLEAN — the standing "the corpora are a SAMPLE,
not the universe" rule, finally carrying a number.

**THE 57 ARE NOT ONE THING, AND ONLY THE LAST GROUP SHOULD WORRY ANYONE.**

        A. test/demo fixture, non-production                              3
           demoNDI, demoNDIMock, mock
        B. deleted / superclass-only, zero documents BY CONSTRUCTION      2
           stimulus_response, stimulus_response_scalar_parameters
        C. vhlab app/calculator class -- no NDI template, lives in the
           NDIcalc-* repos, which these corpora are not the population for 5
           contrast_tuning, spatial_frequency_tuning, speed_tuning,
           speed_tuning_calc, temporal_frequency_tuning
        D. REAL NDI PRODUCTION CLASS, absent from our sample            47

**PART OF D IS AN ARTIFACT OF COUNTING BY `class_name`, AND SAYING SO MATTERS
MORE THAN THE NUMBER.** `base`, `app`, `epochid` and `filter` are SUPERCLASSES
carried inside other documents; they are present in the corpora in every sense
except the one this census measures. `animalsubject` dissolves into `subject`.
Counting them as "absent" overstates the gap, exactly as counting them as
"present" would understate it — the honest form is to name the reason.

**THE PART OF D THAT IS A REAL, NAMED HOLE — whole families no corpus we hold
exercises:**

        spike sorting   kilosort_clusters, kiasort_clusters, spike_clusters,
                        spikewaves, spike_extraction_parameters,
                        spike_extraction_parameters_modification,
                        sorting_parameters, SpikeInterfaceSortingOutputs
        vmspike*        vmspikefit, vmspikesummary, vmspikefilteringparameters,
                        vmneuralresponseresiduals, binnedspikeratevm
        treatment       treatment_drug, treatment_transfer, virus_injection
        imaging         image, ontologyImage, imageCollection
        other           probe_geometry, measurement, subjectmeasurement,
                        electrode_offset_voltage, site2channelmap, fitcurve,
                        simple_calc, oneepoch, generic_file, valid_interval,
                        projectvar, ngrid, binaryseries_parameters,
                        epochclocktimes, dataset_session_info, ensemble,
                        daqreader_epochdata_ingested,
                        daqreader_image_epochdata_ingested,
                        stimulus_parameter, stimulus_parameter_table,
                        stimulus_tuningcurve, orientation_direction_tuning,
                        imageStack_parameters

**TWO CONSEQUENCES THAT ARE NOT OBVIOUS FROM THE COUNT.**

1. **THE MIGRATION'S OWN DISSOLVERS ARE UNEXERCISED ON REAL DATA.**
   `virus_injection` and the treatment family are consumed by COMPLETED
   `migrators_i` dissolvers — three of the classes `_DELETE_PHASE8` removes on
   the strength of that completion — and no corpus has ever driven them. The
   phase-8 criterion asks whether a class's documents can SURVIVE migration; it
   has never been asked of these with a document in hand.
2. **`vmspikefilteringparameters` IS ON THIS LIST, WHICH ANSWERS AN OPEN
   QUESTION WITH A "CANNOT".** Its tombstone rejects the document its own guard
   preserves (threshold: template writes a string, V_eta declares double;
   spiketimes: declared `mustBeScalar` while the guard fires precisely when it
   is an array). The blast radius was recorded as UNMEASURED. It cannot be
   measured against data we hold, because no corpus we have contains one.

**WHAT WOULD ACTUALLY MOVE THIS, stated as a request rather than a wish:** not
"more corpora" but THREE targeted datasets — one carrying spike-sorting output,
one carrying the treatment/virus family, one carrying images. Between them they
reach a large share of the 47. This is a DATA-ACCESS ask, not a schedule item,
and it is the kind that gets more expensive the later it is raised.

### Re-derived counts

RE-DERIVED 2026-08-21 (ndi_m_files, `check_prose_counts`): 91 NDI templates on origin/main; 1,012 .m files (`git ls-tree -r origin/main | grep -c '\.m$'` = 1012 at 5df51cf9; +7 since the 1,005 reading). The did_v1 ground truth is STILL unmoved -- 91 templates, 0 template diffs; only the denominator shifted.

RE-DERIVED 2026-08-21 (ndi_m_files, sibling drift): NDI `origin/main` advanced to `1c0fe1283` (PR #882, parallel-workers), so `git ls-tree -r origin/main | grep -c '\.m$'` = **1013** (was 1012). The did_v1 ground truth is UNMOVED -- 91 templates, 0 template diffs; only the denominator shifted. Re-derive, do not quote.

RE-DERIVED 2026-09-22 (#67 calculator restructure + sibling drift, `check_prose_counts`): 113 v1 ledger rows in the coverage ledger; classes compared: 68 in check_tombstones.py; 254 distinct V_eta class names; 260 json file(s) under schemas/V_eta; 102 NDI templates on origin/main; 1,179 .m files. Re-derive rather than quote; #67 added `calculator` + `runtime_environment` + the `tuning_curve`/`tuning_curve_calculation` families (11 new classes total), and NDI `origin/main` gained 11 templates (gene-expression family + demoNDISeries pair + fileReference).

RE-DERIVED 2026-09-23 (spatial-transcriptomics family landed via #64 commit `71298fd`, `check_prose_counts`): **262 distinct V_eta class names** (was 254; +8 spatial-transcriptomics classes); **268 json file(s) under `schemas/V_eta`** (was 260; +8); registry has 39 rows (was 38; +1 NCIT:C16608 binding for the pyramid); classes compared: 76 (was 68; +8 new source tombstones); 102 NDI templates on origin/main; 1,180 .m files (was 1,179; sibling drift, one .m file). The 8 additions are `gene_expression`, `spatial_gene_expression_pyramid` (reshaped to `⊂ [base, gene_expression, subject_observation]`), `spatial_gene_expression_cells`, `spatial_gene_expression_tiles`, `cell_type_labels`, `gene_list_mapping`, `file_reference`, `gene_list`. Re-derive with `python3 tools/check_prose_counts.py`, do not quote these directly.

RE-DERIVED 2026-09-23 (#73 calculator restructure: `calculator` mixin dropped, 5 tuning markers dropped, 6 `*_calc` leaves -> 5 `*_tuning_calculation` + concrete `tuning_curve_calculation`; `check_prose_counts` re-derives all nouns): **256 distinct V_eta class names** (was 262; -5 markers, -6 `*_calc` leaves, +5 renamed leaves); **262 json file(s) under `schemas/V_eta/`** (was 268; same -6); tombstones classes compared: 74 (was 76; `orientation_direction_tuning` and `tuningcurve_calc` left for "no tombstone" 17 -> 19 when they joined `_DELETE_PHASE8`, and LOSSY fell 11 -> 9 because the V_eta classes that had taken those two did_v1 names never declared their real fields); **20 deleted** in `_DELETE_PHASE8` (was 11; +4 v1 calc tombstones `oridirtuning_calc`, `tuningcurve_calc`, `spatial_frequency_tuning_calc`, `temporal_frequency_tuning_calc`, +5 v1 result tombstones `orientation_direction_tuning`, `contrast_tuning`, `spatial_frequency_tuning`, `temporal_frequency_tuning`, `speed_tuning`). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-09-25 (the #73 review build; `check_prose_counts` re-derives all nouns): the build added label, label_calculation, coordinate_system, position, position_observation, position_calculation, count/area/score/term_calculation and restored harmonic_component_calculation. Live figures: **267 distinct V_eta class names** (was 256); **273 json file(s) under `schemas/V_eta/`** (was 262); **44 direct subclasses** of `data_type` (was 42; +`label`, +`position`) -- and since #73 item 19 NONE of them is abstract. Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-09-25 (plan_documents, `check_prose_counts`): **56 markdown files under `schemas/`** (was 55; +`V_eta_spatial_transcriptomics_plan.md`, the #73 review's decision record). Re-derive with `ls schemas/*.md | wc -l`, do not quote.

RE-DERIVED 2026-09-25 (#65 increment 3b: `session_relative_reference`, `session_bounded_reference` and `epoch_bounded_reference` deleted schema-first, `is_approximate` removed from `time_reference`; `check_prose_counts` re-derives all nouns): **264 distinct V_eta class names** (was 267); **270 json file(s) under `schemas/V_eta/`** (was 273); **12 fields carry a binding** (was 13 -- `epoch_bounded_reference.epoch_clock` left with its class). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-09-25 (#73 review item 45: the new `spatial_frequency` composite; `check_prose_counts` re-derives all nouns): **265 distinct V_eta class names** (was 264); **271 json file(s) under `schemas/V_eta/`** (was 270); **45 direct subclasses** of `data_type` (was 44). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-09-25 (#73 review item 48: the new `voltage_calculation` leaf; `check_prose_counts` re-derives all nouns): **266 distinct V_eta class names** (was 265); **272 json file(s) under `schemas/V_eta/`** (was 271). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-09-25 (#73 review item 50: 51 unused statement leaves deleted; `check_prose_counts` re-derives all nouns): **215 distinct V_eta class names** (was 266); **221 json file(s) under `schemas/V_eta/`** (was 272). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-09-25 (#73 review item 51: the V_eta `image` data_type and `image_observation` retired, `image` restated as the did_v1 tombstone; `check_prose_counts` re-derives all nouns): **214 distinct V_eta class names** (was 215); **220 json file(s) under `schemas/V_eta/`** (was 221); **44 direct subclasses** of `data_type` (was 45). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-09-25 (#73 review item 52: `logical_observation` retired; `check_prose_counts` re-derives all nouns): **213 distinct V_eta class names** (was 214); **219 json file(s) under `schemas/V_eta/`** (was 220). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-09-25 (#73 review item 53: the run-environment entity split into two `software` edges and deleted; `check_prose_counts` re-derives all nouns): **212 distinct V_eta class names** (was 213); **218 json file(s) under `schemas/V_eta/`** (was 219). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-09-25 (ndi_m_files, sibling drift; `check_prose_counts`): NDI `origin/main` at `0a2cdeccb`: 102 NDI templates on origin/main; 1,181 .m files (was 1,180; `git ls-tree -r origin/main | grep -c '\.m$'` = 1181). Only the denominator moved. Re-derive, do not quote.

RE-DERIVED 2026-09-25 (#73 review item 59: `product` minted, `amount` renamed `substance_amount`; `check_prose_counts` re-derives all nouns): **213 distinct V_eta class names** (was 212); **219 json file(s) under `schemas/V_eta/`** (was 218); **44 direct subclasses** of `data_type` (unchanged: `substance_amount` replaces `amount`, and `product` is an entity). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-09-25 (#73 review item 61: `acquisition_metadata_file` retired; `check_prose_counts` re-derives all nouns): **212 distinct V_eta class names** (was 213); **218 json file(s) under `schemas/V_eta/`** (was 219). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-09-29 (#73 review item 67: `control_designation` deleted; `check_prose_counts` re-derives all nouns): **211 distinct V_eta class names** (was 212); **217 json file(s) under `schemas/V_eta/`** (was 218). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-09-29 (#73 review item 68: `model_fit` + `model_fit_calculation` minted; `check_prose_counts` re-derives all nouns): **213 distinct V_eta class names** (was 211); **219 json file(s) under `schemas/V_eta/`** (was 217); **45 direct subclasses** of `data_type` (was 44; +`model_fit`). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-09-29 (#73 audit 2 batched build; `check_prose_counts` re-derives all nouns): **18 fields carry a binding** (was 12; +6 bound by decision -- `tuning_curve`/`contrast_sensitivity` `value.response_type` (D3), `directed_relation`/`undirected_relation` `relation` and `acquisition_channels.channels.type` (D5), `entity.global_identifier.scheme` (D9)); the registry has **42** rows (was 39; relation_bindings 26 -> 29: `observes` dropped, the two gene-mapping rows and the first two undirected rows added, D5). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-09-29 (#73 audit 2 mechanical C9 dropped the two V_zeta example documents under `schemas/V_eta/examples/`; `check_prose_counts` re-derives all nouns): **211 distinct V_eta class names** (was 213; the examples named `scalar_temperature_observation` and `utc_reference`, classes V_eta does not define); **217 json file(s) under `schemas/V_eta/`** (was 219). No class was added or removed. Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-09-30 (the `study` entity; `check_prose_counts` re-derives all nouns): **212 distinct V_eta class names** (was 211); **218 json file(s) under `schemas/V_eta/`** (was 217); **20 fields carry a binding** (was 18; +`study.factors`, +`study.design`). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-09-30 (the `instance_of` relation, instrument subject -> product; `check_prose_counts` re-derives all nouns): the registry has **43** rows (was 42; relation_bindings 29 -> 30). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-09-30 (`directed_relation.roles` + the `awarded_to` relation; `check_prose_counts` re-derives all nouns): **21 fields carry a binding** (was 20; +`directed_relation.roles`); the registry has **44** rows (was 43; relation_bindings 30 -> 31). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-09-30 (plan_documents, `check_prose_counts`): **57 markdown files under `schemas/`** (was 56; +`V_eta_study_plan.md`, the sign-off record for `study`, `instance_of`, `awarded_to` and contributor `roles`). Re-derive with `ls schemas/*.md | wc -l`, do not quote.

RE-DERIVED 2026-10-02 (`subject.type` and `distributive`, did-schema PR #84; `check_prose_counts` re-derives all nouns): **22 fields carry a binding** (was 21; +`subject.type`, bound to the seven coarse subject kinds; `distributive` is an unbound boolean). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-10-03 (`formulation.value.type`, did-schema PR #84; `check_prose_counts` re-derives all nouns): **23 fields carry a binding** (was 22; +`formulation.value.type`, bound like `subject_statement.variable`). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-10-03 (did-schema PR #86: the `humidity` composite, its `humidity_observation` leaf, and the `length_calculation`, `velocity_calculation` and `intensity_calculation` leaves, for the Haley import's stages 9-10; `check_prose_counts` re-derives all nouns): **217 distinct V_eta class names** (was 212); **223 json file(s) under `schemas/V_eta/`** (was 218). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-10-04 (the tenet audit, did-schema PR #87: `humidity` moved under `data_type`, where #86 should have put it; `check_prose_counts` re-derives all nouns): **46 direct subclasses** of `data_type` (was 45; +`humidity`). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-10-04 (the tenet audit, did-schema PR #87: `relation.method` and the `variable` of keys, conditions and method parameters bound like `subject_statement.variable`; `check_prose_counts` re-derives all nouns): **31 fields carry a binding** (was 23; +8). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-10-04 (`timed_sequence` becomes `item`, signed in `V_eta_study_plan.md`: the class and its manipulation leaf renamed, plus the new `item_calculation` leaf; `check_prose_counts` re-derives all nouns): **218 distinct V_eta class names** (was 217); **224 json file(s) under `schemas/V_eta/`** (was 223). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-10-05 (the `time_calculation` and `acceleration_calculation` leaves, for the Haley import's stage 11; `check_prose_counts` re-derives all nouns): **220 distinct V_eta class names** (was 218); **226 json file(s) under `schemas/V_eta/`** (was 224). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-10-08 (one `entity` class and statements by composition, a PROPOSAL built ahead of signature, `V_eta_entity_composition_plan.md`; `check_prose_counts` re-derives all nouns): **25 fields carry a binding** (was 31: the five bound fields of the merged dataset and study classes, `subject.type` and `entity.global_identifier.scheme` went, `entity.type` came); **47 direct subclasses** of `value` (`data_type` until 2026-10-08; was 46, +`text`); **58 markdown files under `schemas/`** (was 57; +`V_eta_entity_composition_plan.md`); the registry has **65** rows (was 44; subject_statement 6 -> 11, relation 31 -> 30, entity_field 3 -> 1, + entity_type 19); classes compared: 72 (in `check_tombstones.py --enforce`); **166 distinct V_eta class names** (was 220; -42 join leaves, -13 entity classes, +`text`); **172 json file(s) under `schemas/V_eta/`** (was 226). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-10-08 (every v1 calculator keeps its named class, Jess; `check_prose_counts` re-derives all nouns): **169 distinct V_eta class names** (was 166; +`contrast_sensitivity_calculation`, `receptive_field_calculation`, `speed_tuning_calculation`); **175 json file(s) under `schemas/V_eta/`** (was 172). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-10-09 (`linked_session`, a PROPOSAL built ahead of signature in `draft/`, `V_eta_linked_session_plan.md`; `check_prose_counts` re-derives all nouns): **170 distinct V_eta class names** (was 169); **176 json file(s) under `schemas/V_eta/`** (was 175); **59 markdown files under `schemas/`** (was 58; +`V_eta_linked_session_plan.md`). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-10-14 (plan_documents, `check_prose_counts`): **60 markdown files under `schemas/`** (was 59; +`V_eta_duplicate_entities_plan.md`, a PROPOSAL: when two records are `same_as`). Re-derive with `ls schemas/*.md | wc -l`, do not quote.

RE-DERIVED 2026-10-14 (ndi_m_files, sibling drift; `check_prose_counts`): NDI `origin/main` at `695e8d86`: 1,236 .m files (`git ls-tree -r origin/main | grep -c '\.m$'` = 1236). Only the denominator moved. Re-derive, do not quote.

RE-DERIVED 2026-10-14 (NDI-matlab#979 merged `lightsheetZarrPyramid` and `lightsheetZarrLevel` into NDI `origin/main`, restated here as v1 tombstones `lightsheet_zarr_pyramid` / `lightsheet_zarr_level`; `check_prose_counts` re-derives all nouns): **115 v1 ledger rows** in the V_eta coverage ledger (was 113); **104 NDI templates** on origin/main (was 102); **172 distinct V_eta class names** (was 170); **178 json file(s) under `schemas/V_eta/`** (was 176). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-10-14 (`data_body.format` becomes a bound `ontology_term`, Jess, lightsheet point 4; `check_prose_counts` re-derives all nouns): **26 fields carry a binding** (was 25; +`data_body.format`, bound `{strength: preferred, node_form: curie}`). Re-derive with `python3 tools/regen_binding_strengths.py --check | head -1`, do not quote.

RE-DERIVED 2026-10-15 (`developed_by` and `hosted_by`, Jess, from the Haley import's stage-2 report; `check_prose_counts` re-derives all nouns): the registry has **67** rows (was 65; relation_bindings 30 -> 32: `developed_by` software -> organization, `hosted_by` dataset -> organization). Re-derive with `python3 tools/regen_binding_strengths.py --check | head -1`, do not quote.

RE-DERIVED 2026-10-15 (`distributed_as`, Jess, Haley import decision #17; `check_prose_counts` re-derives all nouns): the registry has **68** rows (was 67; relation_bindings 32 -> 33: `distributed_as` strain -> product). Re-derive with `python3 tools/regen_binding_strengths.py --check | head -1`, do not quote.

RE-DERIVED 2026-10-19 (ndi_m_files, sibling drift; `check_prose_counts`): NDI `origin/main` at `358b2fbf`: 1,300 .m files (`git ls-tree -r origin/main | grep -c '\.m$'` = 1300). Only the denominator moved. Re-derive, do not quote.

RE-DERIVED 2026-10-23 (ndi_m_files, sibling drift; `check_prose_counts`): NDI `origin/main` at `004585cec`: 1,305 .m files (`git ls-tree -r origin/main | grep -c '\.m$'` = 1305). Only the denominator moved. Re-derive, do not quote.

RE-DERIVED 2026-10-23 (ndi_m_files, sibling drift; `check_prose_counts`): NDI `origin/main` at `3cb19a85f`: 1,307 .m files (`git ls-tree -r origin/main | grep -c '\.m$'` = 1307). Only the denominator moved. Re-derive, do not quote.

RE-DERIVED 2026-10-19 (plan_documents, `check_prose_counts`): **61 markdown files under `schemas/`** (was 60; +`V_eta_prefix_spelling_plan.md`, a PROPOSAL: write a CURIE prefix the way its issuer cites it). Re-derive with `ls schemas/*.md | wc -l`, do not quote.

RE-DERIVED 2026-10-20 (the term registry, tenet T19, `V_eta_term_registry_plan.md`; `check_prose_counts` re-derives all nouns): **179 json file(s) under `schemas/V_eta/`** (was 178; +`stable/term_registry_meta.json`, a meta file, so the class count is unchanged); **62 markdown files under `schemas/`** (was 61; +`V_eta_term_registry_plan.md`). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-10-20 (`V_eta_relation_inheritance_plan.md`, a proposal built ahead of signature; `check_prose_counts` re-derives all nouns): **63 markdown files under `schemas/`** (was 62; +`V_eta_relation_inheritance_plan.md`); the registry has **69** rows (was 68; relation_bindings 33 -> 34: `included_in`). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-10-21 (`source_unit` becomes a bound term, a PROPOSAL built ahead of signature at Jess's request, `V_eta_source_unit_plan.md`; `check_prose_counts` re-derives all nouns): **94 fields carry a binding** (was 26; +68, every `source_unit` declaration, bound `{strength: preferred, node_form: curie}`); **64 markdown files under `schemas/`** (was 63; +`V_eta_source_unit_plan.md`). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-10-21 (one `method` shape and `visual_grating` deleted, a PROPOSAL built ahead of signature at Jess's request, `V_eta_method_plan.md`; `check_prose_counts` re-derives all nouns): **170 distinct V_eta class names** (was 172; -`visual_grating`, -`spatial_frequency`; `method_parameters` renamed `method`); **177 json file(s) under `schemas/V_eta/`** (was 179); **45 direct subclasses** of `value` (was 47); **88 fields carry a binding** (was 94: -10 `source_unit` cells of the two deleted classes, +4 for the `method.term` / `method.parameters` entries on `relation`, `clock_alignment_configuration` and `method`); **65 markdown files under `schemas/`** (was 64; +`V_eta_method_plan.md`). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-10-21 (`culture type`, EMPTY:0000357, the kind of a `culture` entity, Jess Haley, from the Haley V2 import: a bacterial patch states its kind with it instead of NCIT Sample Type; `check_prose_counts` re-derives all nouns): the registry has **66** rows (was 65; subject_statement 11 -> 12). Re-derive with `python3 tools/regen_binding_strengths.py --check | head -1`, do not quote.

RE-DERIVED 2026-10-21 (a dose states per-ingredient amounts, Jess Haley [dose per ingredient]: `dose.value.ingredients` entries carry `mass`, `volume`, `substance_amount`, `count`, `amount_per_body_mass`; `check_prose_counts` re-derives all nouns): **92 fields carry a binding** (was 88; +4, the `source_unit` of the four non-count quantities in a dose ingredient entry). Re-derive with `python3 tools/regen_binding_strengths.py --check | head -1`, do not quote.

RE-DERIVED 2026-10-22 (tenet audit, relation vocabulary: Jess Haley [epoch to system link], [distance], [vocabulary nodes] K5, [clock alignment relation bound]; `check_prose_counts` re-derives all nouns): the registry has **62** rows (was 65; relation_bindings 34 -> 31: -recorded_by, -measured_distance_to, -aliquot_of, -passage_of, +the `clock_alignment` row); **95 fields carry a binding** (+`clock_alignment.relation`). Re-derive with `python3 tools/regen_binding_strengths.py --check | head -1`, do not quote.

RE-DERIVED 2026-10-22 (tenet audit, units and value kinds: Jess Haley [units bound], [remaining units bound], [one fit entry], [irradiance]; `check_prose_counts` re-derives all nouns): **115 fields carry a binding** (was 95; +20: 8 entry and covariate units, 2 response units, the fit entry's model and two units on three classes, the irradiance source unit); **171 distinct V_eta class names** (was 170; +`irradiance`); **178 json file(s) under `schemas/V_eta/`** (was 177); **46 direct subclasses** of `value` (was 45). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-10-22 (Jess Haley [harmonic response unit bound]; `check_prose_counts` re-derives all nouns): **116 fields carry a binding** (was 115; +`harmonic_component.response_unit`). Re-derive with `check_prose_counts`, do not quote.
