# Audit: dataset-specific and meaning-guessing rules in NDI-matlab `+migrate`

READ-ONLY. Nothing was edited, committed or checked out. NDI-matlab at `670f36268` (detached, the locked head; `git rev-parse --short HEAD` printed `670f36268`).

## Denominator (first)

- **.m files under `src/ndi/+ndi/+migrate/`: 37** (`find ... -name '*.m' | wc -l` printed `37`; 19032 lines total, 12662 non-comment lines after stripping `%` lines).
- **Read in full (every code line, comment-stripped copy with original line numbers): 19**: `+internal/` epochSeriesBodies, ontologyRowSubjects, ontologyLabelSubjects, strainAssembly, subjectStrainAssembly, sliceTetanus, pathSPromotion, imagedEntitySubjects, recordingAttribution, stimulusRecipe, gratingRecipe, stimulusMethod, stimulusPresentationToItem, stimulusBathToBath, sessionCohort, datasetScope, navigatorEpochFiles, settleIngestedFiles, locatedFileFacts.
- **Read in part (main logic read; trailing small helpers not read): 7**: `local.m` (code lines 1-2835 read; 2836-3743, which hold report and print helpers, grep only), hartleyBasisGratings (to line 400 of 538), softwareDedup (to 632 of 686), epochAnchorFold (to 662 of 737), ensembleMembership (to about 525 of 744), bodyResolver (function list, the epoch-clock section, and a grep of the subject routes), etaShape (grep, plus the `curie` function).
- **Grep only: 11**: withSessionId, remapIds, dimensionTermCensus, ensembleGateReport, cloud, cloudClient, uploadVDeltaBodies, termRegistryOff, runStateRef, v1AttachedFile, Contents.m (0 code lines).
- In the grep-only and partly-read files, **"no finding" means "not measured"**, not "clean".
- **Out of scope, one line each:**
  - The `did2.convert.*` passes that `local.m` calls in DID-matlab are not audited here: epochMint, resolveSessionAnchors, resolveEpochProbemap, resolveResponseParameters, foldGenericFiles, resolveValidIntervals, resolveClockAlignment, resolveOpenmindsCitations, resolveDatasetEntities, and **resolveLawnPlateSubjects**. That last one is JH (E. coli lawn and plate), it is called from the generic stage at `local.m` around line 1054, and it cites [lawn in plate] in `V_eta_relation_inheritance_plan.md`.
  - `ndi.vintage.map` (read by softwareDedup) and `ndi.v2.vocab*` are not audited either.
  - `src/ndi/+ndi/+setup/+conv/+haley/` is a per-dataset raw-source import, the right place for dataset meaning, and was not audited. The same folder also holds `+babu`, `+birren`, `+dabrowska` (with `V2_decisions.md`, which sliceTetanus cites), `+gluckman`, `+hunsberger`, `+marder` and `+vhlab` (`ls +setup/+conv/`).

Decision tags were searched in two places: the code comments (`grep -rnoE "Decided...|Jess Haley, 2026-...|TEAM-SIGN-OFF..."` over `+migrate`) and `/home/user/DID-schema/schemas/*.md` (`grep -lE "(Decided by ... |TEAM-SIGN-OFF ?)\[<tag>"`, excluding the generated STATUS and coverage_ledger files). Tests were searched in `tests/+ndi/+unittest/+migrate/*.m` by pass name and by the rule's literal string.

**All bins below are PROPOSED (not decided).**

---

## Bin B: meaning tied to one dataset's shape (PROPOSED: move to that dataset's map; the generic stage carries the item as lossless v1)

| # | file:function (line hint) | what it decides | decision tag cited | test |
|---|---|---|---|---|
| B1 | epochSeriesBodies:`jhOwners` (~225), called from the main loop (~144) | Recognises JH worm-track bodies: an `epoch_binary_data.vhsb` whose owners' statement variables are exactly `PATO:0000140` (position), `EMPTY:0000384` (distance) or `EMPTY:0000297` (item). Such bodies are routed to `splitJH`. | `V_eta_epoch_plan.md` [JH position and distance], [JH build choices] (Jess Haley, 2026-10-22 / 10-23) | TestEpochSeriesBodies `testAJHPositionIsSplitIntoTrackDocumentsArray`, `testAJHDistance*` |
| B2 | epochSeriesBodies:`splitJH` (~245) | The source column layout: cols 1:2 minus 0.5 become pixel x,y; col 3 minus 1 becomes a 0-based patch index (fill 255, or 65535 past 254 patches); col 1 is distance; col 2 is dropped. It mints `ingested` sampled bodies with JH descriptions ("worm", "distanceLawnEdge", "closestLawnID"), refuses irregular frame times, and builds frame / body-part / X-Y axes. | same, plus [JH signed distance in metres] (`V_eta_epoch_plan.md`) | TestEpochSeriesBodies (4 JH tests) |
| B3 | epochSeriesBodies:`videoScaleIndex` / `scaleOf` / `videoScale` (~352-452) | Scale for metres: reads a v1 `imageStack` sampled body's covariate spacing labelled `om:micrometre` as **pixels per mm**, then `mpp = 1e-3/scale`. It joins through `member_of` groups and refuses when scales are ambiguous. | [JH signed distance in metres], [imageStack scale label kept] (`V_eta_epoch_plan.md`) | `testAJHDistanceIsSplitIntoMetresByTheVideosScale`, `...WithTwoVideoScales...`, `testAVideoScaleInAnotherUnitIsNotRead` |
| B4 | epochSeriesBodies:`bodyPartOf` (~510) | String match on the instrument element's `local_identifier`: `_head_` gives anterior end point (EMPTY:0000352), `_tail_` gives posterior end point (EMPTY:0000353), anything else is body midpoint (EMPTY:0000137). | none found for the head/tail string rule. Searched epochSeriesBodies.m comments and `schemas/*.md` for `_head_` and "anterior end point": no hit outside the generated ledger. | TestEpochSeriesBodies (literal `_head_` appears in the fixture) |
| B5a | sliceTetanus (top-level, ~194-211) | Recognises Dabrowska slice baths by **element name regex** `^bath_(.+)_([a-z])$` plus the animal's `local_identifier` ending in `_<postfix>`. It mints one `tissue` entity per slice, `part_of` the animal. | sliceTetanus.m header: "DECIDED BY JESS HALEY, 2026-10-21" citing NDI `+setup/+conv/+dabrowska/V2_decisions.md`; did-schema `V_eta_go_forward_class_audit.md` [sliceTetanus stays in NDI] (2026-10-23) | TestSliceTetanus, TestMigrateLocalEtaDab (fixture `dab_slice_tetanus_v1.json`) |
| B5b | sliceTetanus:`animalKeyOfEpoch` (~654) | Regex on `.mat` **file paths** (`/Mon D YYYY/` nested date folders). It mints a **new organism**, writes its `local_identifier` by string replacement, and copies its strain relation and assertions. | same header decision | TestSliceTetanus |
| B5c | sliceTetanus (~148-161, ~445-537) | `openminds_stimulus` labels `EMPTY:0000220` / `EMPTY:0000221`, or names ending "before/after optogenetic tetanus". From these it **infers** one tetanus manipulation (`EMPTY:0000358`), timed between the last "before" epoch and the first "after" epoch, and removes the label documents. | same | TestSliceTetanus, TestMigrateLocalEtaDab |
| B5d | sliceTetanus:`folderParameters` / `tlsFolder` (~748, ~689) | Regex on the folder name `TLS <n> Hz <n> s` to get frequency and duration method parameters. | same | TestSliceTetanus, TestMigrateLocalEtaDab (literal `TLS`) |
| B5e | sliceTetanus (~162-176, ~555-612) | A `treatment` with ontologyName `EMPTY:0000074`, or a name ending "tetanus stimulation target location", becomes the target-region condition. It supersedes and removes the per-animal treatment manipulations, their site observations, their part-subjects and their anchors. | same | TestSliceTetanus |
| B5f | sliceTetanus (~337-416) | Re-attributes statements and `observes` relations from the animal to the slice, matching by the instrument element's **name suffix** `_<postfix>`. | same | TestSliceTetanus |
| B5g | sliceTetanus:`dsOr` (~817) | When a subject has no datestamp, writes the fabricated `'2024-01-01T00:00:00.000Z'`. | none found (searched header and `schemas/*.md` for 2024-01-01) | none found (searched tests for `2024-01-01`) |
| B6 | imagedEntitySubjects:`depictedSubject` / `plateIdOfHandle` / `rowDataKeyFor` (~587-749) | Haley plate join: a table-row column named `bacterial plate identifier` is joined to a subject whose `local_identifier` contains `/plate/<id>` (option `PlateHandleJoin`, default true). | Header: "team decision taken in session, 2026-08-11" (quoted, with no name or tag). No tagged `Decided by` line found (searched `schemas/*.md` for "bacterial plate identifier", "plate handle", "/plate/"). | TestImagedEntitySubjects `testEcoliImageIsAttributedToItsPlateSubject`, `testPlateHandle*`, `testBarePlateHandleAlsoResolves` |
| B7 | local.m main body (~1054) calls `did2.convert.resolveLawnPlateSubjects` | JH E. coli lawn and plate subjects minted inside the generic chain. The code is DID-side (not audited); listed because the generic stage calls it unconditionally. | [lawn in plate] `V_eta_relation_inheritance_plan.md` | not in NDI tests except a mention in TestImagedEntitySubjects |

## Bin C: per-class meaning choice applied to every dataset (PROPOSED: becomes a workbook default a human confirms per dataset)

| # | file:function (line hint) | what it decides | decision tag cited | test |
|---|---|---|---|---|
| C1 | epochSeriesBodies main loop (~163-219) | An `opaque_body` named `epoch_binary_data.vhsb` whose owner is a `GO:0001508` observation becomes a sampled body with an "action potential" dimension; data_type comes from the vhsb header. | `V_eta_epoch_plan.md` [spike train body by bytes], [spike dimension term] | TestEpochSeriesBodies `testBytesHere...`, `testAnOwnerThatIsNotASpikeTrain...` |
| C2 | ontologyRowSubjects:`resolveRowSubject` (~401) | Who a table row is about: a `document_id` edge, then the column `SubjectDocumentIdentifier`, then (`LocalIdentifierJoin`, default **true**) the column `SubjectLocalIdentifier` matched by **label** to a subject's `local_identifier`. Row meaning then comes from DID's per-table refold. | none found. The header calls the local-identifier route a "TEAM QUESTION". Searched `schemas/*.md` for LocalIdentifierJoin / SubjectLocalIdentifier: hits only in `V_eta_discovery_notes.md` (not a decision). | TestOntologyRowSubjects, TestMigrateLocalEtaDab |
| C3 | ontologyLabelSubjects (~220-297) | Every `ontology_label` becomes a term **observation** of the labelled statement's subject, with variable `label` (no node), the target's first time reference, and `derived_from` the target. | Code cites `V_eta_migration_plan.md` D.2. No `Decided by` / TEAM-SIGN-OFF line found for it (searched `schemas/*.md` for "ontology_label"). | TestOntologyLabelSubjects |
| C4 | strainAssembly (~244-321, `strainStatements` ~498, `datasetLevel` ~378) | An openMINDS `Strain` becomes a `strain` entity. Species goes to `NCIT:C45293`, GST to `EMPTY:0000347`, phenotype becomes a name-only term, lab code and synonym become text, `backgroundStrain` becomes `derived_from`. At dataset scope, strains are merged by an attribute key. | `V_eta_entity_composition_plan.md` TEAM-SIGN-OFF; `V_eta_openminds_family_record.md` [shared entities at dataset level] | TestStrainAssembly, TestMigrateLocal |
| C5 | subjectStrainAssembly (~604-895) | Same as C4 for `openminds_subject`, plus subject `instance_of` strain. It **removes** background-strain assertions on the subject, GST assertions and duplicate species assertions, and dedups by content key (dataset scope). | `V_eta_openminds_family_record.md` [subject keeps only its own strain], [shared entities at dataset level] | TestSubjectStrainAssembly |
| C6 | pathSPromotion "sites" loop (~156-225) | An `anatomical location` observation sharing an anchor with a manipulation is read as "the manipulation targets that region". It mints a `tissue` region part `part_of` the subject, retargets the manipulation, and removes the observation. | `V_eta_go_forward_class_audit.md` [region parts] | TestPathSPromotion (about 30 tests) |
| C7 | pathSPromotion:`lateralityTable` (~500) | Hard-coded six-node side table (UBERON:0002812/0002813, NCIT:C32955/C33472, NCIT:C25229/C25228). It folds the side onto the part as a `NCIT:C25185` assertion. | [laterality on the part], [laterality variable] (`V_eta_go_forward_class_audit.md`) | `testAreaPlusHemisphereIsOnePartWithLaterality`, `testLateralityIsReadFromTheNodeNotTheLabel` |
| C8 | pathSPromotion:`isAnatomical`, "located" mode, label loop (~269-393, ~682) | Only a `uberon:` prefix counts as anatomy. Statements by a located instrument, and `label` observations with a UBERON term, are retargeted onto a part. Tissue is recognised by the `base.name` prefix `migrated_part_`. | [slice region chain] (`V_eta_go_forward_class_audit.md`); [region by condition and ...] (`V_eta_term_registry_plan.md`) | `testASiteConditionThatIsNotUberon...`, `testAnAnatomicalLabelTargetsThePart`, `testProbeLocationRetargetsTheRecording` |
| C9 | recordingAttribution (~193-250) | An observation about a probe with no instrument is re-pointed to the probe's specimen, taken from a donor observation or from the element's `observes`. When its own variable has no node, it **copies the donor's variable**. | [preview attribution without epoch files] (`V_eta_recording_observation_plan.md`); TEAM-SIGN-OFF [raw recording observation] | TestRecordingAttribution (`variable_carried`), TestMigrateLocalEtaPRED |
| C10 | softwareDedup (~190-424) | Identity rule: software with the same (name, version) is one entity. Version is read from `IAO:0000129` or the text "version number". Merged away: duplicate entities and their version assertions. `local_identifier` is rewritten to `name@version`. At dataset scope, entities move to the dataset level unless they are object software. | [software dedup after pass one], [object software scope] (`V_eta_go_forward_class_audit.md`); [shared entities at dataset level] | TestSoftwareDedup, TestSoftwareDedupAfterPassOne |
| C11 | epochAnchorFold:`clockTerm` (~630) | `approx_*` clocks become the base clock plus a 5 s `clock_tolerance`. | TEAM-SIGN-OFF [time_reference] (`V_eta_time_reference_model_plan.md:468`: "approx_ prefix de-encodes to an explicit clock_tolerance"). The **5 s value** is from NDI's `+time/clocktype.m` docstring per the code comment; no did-schema line states 5 s (searched the plan for "5 s" and "clock_tolerance": only unrelated hits). | TestEpochAnchorFold (approx_ cases) |
| C12 | bodyResolver:`epochClockOfElement` (~562) | Clock guess: element_epoch clock, else a `dev_local_time` epochclocktimes, else any clocktype, else the **default `dev_local_time`**. | none found (searched the bodyResolver header and `schemas/*.md` for "conventional default") | indirect: TestBathAssembly, TestEpochAnchorFold, TestMigrateLocalEta (literal `dev_local_time`) |
| C13 | stimulusPresentationToItem (~216-278) + bodyResolver subject routes + sessionCohort | Which animal was stimulated: responses, then epoch elements in the session, then the stimulator's subject. If several animals result, a "session cohort" group is minted and the statement is marked distributive; several via the stimulator is refused; the sibling-session route is disarmed. | Jess Haley 2026-10-21 "a" (code); bodyResolver header "Decided by Jess Haley 2026-10-21 (NDI-matlab PR #1021)"; `V_eta_stimulus_model_plan.md` [presentation with no ...] | TestStimulusPresentationCohort, TestStimulusPresentationItem |
| C14 | stimulusPresentationToItem:`itemManipulation` (~556) | Every `stimulus_presentation` becomes a manipulation with method **"visual stimulation"** and variable **"visual stimulus"**. | TEAM-SIGN-OFF [method] (`V_eta_method_plan.md`) | TestStimulusPresentationItem |
| C15 | stimulusPresentationToItem:`newStimKind` (~821) | NewStim class recognised by its required-field sets; `imageType` 1/2 means grating, 0 means bars, other values are other. | Jess Haley 2026-10-21 "recognise the class" (code); [non-grating stimuli as methods] (`V_eta_method_plan.md`) | TestStimulusPresentationItem, TestStimulusRecipe |
| C16 | stimulusRecipe (~74-172) | Per-kind method term and field-to-variable/unit tables. Heuristics: `random==1` means "sparse noise"; `bgpause` unit is seconds if `fps<0`; `pixSize<1` is read as a fraction; `sPhaseShift` rad to deg; `bit depth 8` added when there is colour; **a rectangle with short side <= 50 px means "flashed bar"**. | [flashed bar], [non-grating stimuli as methods], [spatial phase in degrees], [Hartley without enumeration] (`V_eta_method_plan.md`) | TestStimulusRecipe |
| C17 | gratingRecipe (~54-80) | Term from `imageType` (sinusoidal / square-wave / drifting grating); a blank is "blank screen". | `V_eta_method_plan.md` TEAM-SIGN-OFF [method] (signed 2026-10-21); "a blank is a blank" (Jess Haley 2026-10-21, code) | TestGratingRecipe, TestStimulusRecipe |
| C18 | hartleyBasisGratings:`basisRecipe` (~299) | Physical model: spatial phase -45 / 135 by the sign of `s`; SF in cycles per pixel; duration 1/fps; dedup across a session. | [hartley method implied] (`V_eta_ngrid_family_findings.md`); [Hartley without enumeration] (`V_eta_method_plan.md`) | TestHartleyBasisGratings, TestStimulusPassGating |
| C19 | stimulusBathToBath:`vetaBath` / `isGenericBath` (~271-383) | Mixture rows named `pH` or `osm`/`osmolarity` become formulation properties; the first chemical becomes the statement variable; a unit name "Molar" fills `molar`; a generic bath location (`NCIm:C0179246` or the name "bath") writes **no** site observation. | [bath is a manipulation], [treatment routes by location] (`V_eta_go_forward_class_audit.md`) | TestBathAssembly (generic bath); pH / osmolarity: none found (searched tests for `osmolarity`) |
| C20 | stimulusPresentationToItem:`controlCovariate` (~642) | `control_stimulus_ids` become a logical `XCO:0000099` covariate on the presentation; the control records are removed (local.m ~2944). | [control as covariate] (`V_eta_stimulus_response_model_plan.md`) | TestControlCovariate |

## Bin A: generic and structural (PROPOSED: keep in the generic stage)

| # | file:function | what it does | tag / test |
|---|---|---|---|
| A1 | local.m: `resolveDeferred`, `recountSummary`, the revert-on-quarantine wrappers, `assertUniqueIds` | Orchestration; every pass in its own try/catch; refold through `did2.convert.v1_to_v2`. | TestMigrateLocal* |
| A2 | navigatorEpochFiles | Synthesises transient `epochfiles_ingested` from the session's file navigators; they are removed after the pass (local.m ~964). | `V_eta_recording_observation_plan.md` (Jess Haley 2026-10-21, cited) / none found by name in tests |
| A3 | locatedFileFacts | Size and MD5 of located files. | TestLocatedFileFacts |
| A4 | epochAnchorFold (everything except C11) | Joins `epoch_bounded_reference` to the minted epoch by (session, epoch string). | TestEpochAnchorFold |
| A5 | ensembleMembership | Ensemble map becomes `member_of` edges, epoch-scoped. | [ensemble retired] (code; Jess Haley 2026-10-22) / TestEnsembleMembership |
| A6 | datasetScope, withSessionId, remapIds, sessionCohort (shape only), v1AttachedFile, epochSeriesBodies `bytesHere` / `xDatumType` | Structural helpers. | TestV1AttachedFile, TestMigrateSessionId |
| A7 | ontologyRowSubjects / imagedEntitySubjects **`document_id`-edge routes** | Subject taken from an explicit v1 edge (no guessing). | TestOntologyRowSubjects, TestImagedEntitySubjects `testRowEdgeNamingASubjectResolves` |
| A8 | stimulusBathToBath:`parseMixture88` / `csvFields` | CSV parse of `mixture_table`. | TestBathAssembly |
| A9 | stimulusPresentationToItem timing (`fileTiming`, `trialTiming`), `carryFiles` | Onsets and offsets read from `presentation_time.bin` or inline; files carried. | [presentation times from the file] / TestStimulusPresentationItem |

## ? (unsure)

| # | file:function | what it decides | why unsure | tag / test |
|---|---|---|---|---|
| Q1 | etaShape:`curie` (~644) | Rewrites `WBStrain:<n>` to `WormBase:WBStrain<n>` (a C. elegans / JH prefix) in strain global identifiers. | It is a prefix-spelling rule, so arguably generic (A). But only one, dataset-driven prefix is hard-coded, and it rewrites the v1 string without keeping the source. | TEAM-SIGN-OFF [prefix spelling] (`V_eta_prefix_spelling_plan.md`), cited at etaShape.m:650 / TestStrainAssembly, TestSubjectStrainAssembly |
| Q2 | ontologyRowSubjects column names `SubjectDocumentIdentifier` / `SubjectLocalIdentifier` | The column names define the subject route. | They are NDI table-dictionary conventions used by more than one lab (the header cites the haley and dabrowska dictionaries), so they are neither clearly one dataset (B) nor clearly class-wide (C). | as C2 |
| Q3 | stimulusRecipe / newStimKind as a whole | The VH-lab NewStim parameter vocabulary. | It applies to every NewStim dataset (B, Soph, 20211116 ...), so it is C, but it is lab-software-specific rather than NDI-class-specific. | as C15/C16 |

---

## Places that block a lossless generic stage (information dropped or rewritten with no v1 carry-through)

1. **sliceTetanus `plan.removed`** (~532, ~582-643) deletes `openminds_stimulus` approach labels, treatment manipulations, their site observations, part-subjects and their anchors. It also writes `local_identifier`s from path regexes and fabricates the datestamp `2024-01-01` (`dsOr`). The only guard is "still referenced".
2. **subjectStrainAssembly** (~675-897) removes background-strain, GST and duplicate-species assertions.
   - Both strain passes ignore openMINDS Strain fields `breedingType`, `stockNumber`, `diseaseModel` and `lookupLabel`.
   - **strainAssembly** also ignores `digitalIdentifier` and `alternateIdentifier` (it reads only `ontologyIdentifier`, ~294) and removes the consumed Species/GST fragment documents (~338-364).
3. **pathSPromotion** removes the promoted site observations (`removeMask`, ~218/221) and strips the site condition (`dropCondition`). The fact survives only as the minted part's assertion; the v1 statement itself is gone.
4. **Stimulus presentations are consumed** (local.m ~2940).
   - For kind `grating`, `gratingRecipe` keeps only `angle`, `sFrequency`, `tFrequency`, `contrast` and `imageType`. Every other periodicstim field (`rect`, `chromhigh`/`chromlow`, `distance`, `nCycles`, `windowShape`, `dispprefs`, ...) is not written.
   - On the Hartley enumeration route, generator parameters other than `M`, `fps` and `contrast` are not carried.
   - `stimulusArray` keeps only `parameters` from cell-form stimuli.
   - Folded `control_stimulus_ids` documents are removed (local.m ~2944).
5. **epochSeriesBodies:splitJH** drops vhsb column 2 ("a constant 1"). It replaces the v1 opaque body (id kept) with values that have been shifted (minus 0.5, minus 1) or rescaled (pixels to metres, using a scale read from another document). The original bytes are not carried as such.
6. **epochAnchorFold** `rmfield`s `epoch_bounded_reference`, `epochid` and `time_reference`. The `approx_*` clock name is replaced by a clock plus a 5 s tolerance that is not in the v1 record.
7. **recordingAttribution** overwrites the observation's variable with the donor's (`variable_carried`, ~229-234). The v1 variable name is lost.
8. **softwareDedup** drops merged-away entities (only `global_identifier` is unioned), drops their version assertions, and rewrites the survivor's `local_identifier`.
9. **stimulusBathToBath**: the generic-bath location is not written. Mixture columns after the fifth are ignored. pH and osm rows move out of the ingredient list.
10. **settleIngestedFiles** flips `delete_original` to false, and when bytes are missing sets `ingest` to false and overwrites `location` with the store path. The v1 location value is not kept.
11. **ensembleMembership** dissolves maps and drops the combined (times, neurons) carrier bytes. This follows [ensemble retired] and runs only after it checks the trains are present.
12. **ontologyLabelSubjects** replaces the `ontology_label` with a term observation. Only `ontology_node` is read; any other label field is not carried.
13. **ontologyRowSubjects / imagedEntitySubjects** replace the passthrough row or image with DID's refold output, so lossless depends on the DID-side per-table maps (not audited).

Also noted: **no JH corpus test exists in NDI** (`grep -rln "JH\|haley" TestMigrate*.m` printed nothing). The corpus tests check these second-pass reports:

- TestMigrateLocalEta: dimensionTerms, epochAnchorFold, epochMint, stimulusSequence
- 20211116, B, Soph: stimulusSequence
- Dab: sliceTetanus
- PRED: epochAnchorFold, epochMint, recordingAttribution
- TestMigrateLocal: strainAssembly

## Key commands (as run)

```
cd .../sib/NDI-matlab && git rev-parse --short HEAD                  # 670f36268
find src/ndi/+ndi/+migrate -name '*.m' | wc -l                       # 37
find ... -name '*.m' | xargs wc -l                                   # 19032 total
awk '{if ($0 ~ /^[ \t]*%/) next; print NR": "$0}' <f>                # comment-stripped copies (12662 lines)
grep -n '^\s*function ' local.m
grep -nE "strcmpi?\(|contains\(|regexp|startsWith|endsWith|case |'[A-Za-z]+:[0-9A-Za-z_-]+'" nc/<small files>
grep -rnoE "(Decided[^.;]{0,80}|Jess Haley, 2026-[0-9-]+[^)]{0,60}|TEAM-SIGN-OFF[^.]{0,40}|V_eta_[a-z_]+_plan\.md[^)]{0,60})" --include=*.m src/ndi/+ndi/+migrate
cd /home/user/DID-schema && grep -lE "(Decided by [A-Z][a-z]+ [A-Za-z ]+, 2026-[0-9-]+ |TEAM-SIGN-OFF ?)\[<tag>" schemas/*.md
grep -n "_head_\|anterior end point" schemas/*.md ; grep -n "bacterial plate identifier\|plate handle\|/plate/" schemas/*.md
grep -n "5 s\|clock_tolerance" schemas/V_eta_time_reference_model_plan.md
cd tests/+ndi/+unittest/+migrate && grep -l -- "<pass or literal>" *.m
grep -oE "secondPass\.[A-Za-z]+" TestMigrateLocalEta*.m TestMigrateLocal.m | sort -u
ls src/ndi/+ndi/+setup/+conv/
```
