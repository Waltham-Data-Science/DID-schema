# Dataset-specific code in the generic v2 migration: audit, 2026-11-02

For "Decided by Jess Haley, 2026-10-26 [dataset-specific logic leaves the
generic migration]" ("audit first"), did-schema
`docs/plans/did_v2_go_forward_class_audit.md`. Read-only: no code moved.
Every "where it goes" below is **Proposed (not decided)**.

## Heads

- DID-matlab `V2` c2749f87 (#364), `src/did/+did2/+convert/**`.
- NDI-matlab `V2` 28d38547 (#1146), `src/ndi/+ndi/+migrate/**`.
- Line numbers are for these heads. Search by the function name.

## Denominators (first)

- DID-matlab `+did2/+convert`: **400 `.m` files, 68,586 lines.**
- NDI-matlab `+ndi/+migrate`: **50 `.m` files, 21,037 lines.**
- **All 450 files were scanned** by `scratchpad/U_tools/dsscan.py`. It reads code
  lines only (`%` comments and `%{ %}` blocks removed). It uses six patterns:
  - lab and dataset names: haley, dabrowska, dab, soph, griswold, vhlab, vikko,
    babu, birren, gluckman, hunsberger, marder, fitzpatrick, vanhooser, saya,
    francesconi, bhar, jess;
  - corpus names: PRED, JH, 20211116, "corpus";
  - organism and assay words: elegans, e. coli, OP50, bacteri, lawn, agar,
    plate, encounter, worm, BNST, tetan, slice, elevated plus, EPM, FPS,
    startle, chemotax, McCutcheon;
  - id literals `'<16 hex>_<16 hex>'`;
  - file and folder patterns (`.vhsb`, `.tif`, `_position'`, `_distance'`, and
    any `regexp` with a digit or capture pattern);
  - subject-id literals `'...@<lab>.<tld>'`.
- `scratchpad/U_tools/curies.py` listed every CURIE literal in code (EMPTY,
  NCIm, NCIT, CHEBI, WBStrain, WBls, UBERON, MMO, CMO, MICRO, XCO, OM, BAO, OBI,
  PATO).
- Label-word routers were also searched: `containsAny`, `contains(lower`,
  `any(strcmpi`, `startsWith(lower`, `endsWith(lower`, `regexpi(`.
- **Hits: DID 78 in 49 files; NDI 66 in 9 files.** Every hit was read in
  context. Most DID hits are decision citations inside messages ("Jess Haley",
  "[... Haley ...]") or generic regexes (ISO dates, `chunk.bin_N`, zarr
  dtypes). They are not listed below. Full output:
  `scratchpad/U_dsscan_dm.txt` and `scratchpad/U_dsscan_nm.txt`.
- A file with no hit is **not measured** for meaning that has no name in it
  (for example a rule tuned to one dataset that names no lab). These patterns
  cannot find that.
- Nothing was executed. There is no MATLAB here.

## Since the last audit (`docs/v2_working/DATASET_SPECIFIC_AUDIT.md`)

That audit was measured on branch heads DID-matlab e1e3aee and NDI-matlab
c8a47d0e2. For each item it listed, these are the files at today's heads:

| old item | today |
|---|---|
| D1 `resolveLawnPlateSubjects.m` | file gone (`ls`: no such file) |
| D2, D3, D4 `ontology_table_row.m` encounter map, patch-geometry map, per-column fallback | the file is 74 lines and carries every row ([table rows carried as v1]) |
| D5 `image_stack.m` region words | gone. Mask/map detection by "mask" / "label map" stays (`isMask` 684-688, `isMap` 690-694); either one carries (carry-154 / carry-025, 378-398) ([Haley mask words leave the generic stage]) |
| D6 `resolveEpochProbemap.m` position/distance, `stemKey` | gone. `derivedSeriesKind` 2290-2313 has only `spikes` |
| D7, D8 `isMedium`, `isHeatOnly` | gone (grep: no match) |
| D9 `treatment.m:termNumberKind` | reads `number_unit` from the term registry (235-262), [term-stated unit is generic] |
| D10 `treatment.m` keyword router | the temperature, substance and procedure lists are gone. One list is left: item U2 below |
| N3 `imagedEntitySubjects.m`, N6 `ontologyRowSubjects.m` | files gone (`ls +internal/`) |
| N4 `epochSeriesBodies.m` `jhOwners` / `SplitJH` | gone (grep: no match) |
| N1 `sliceTetanus.m`, N5 the wiring in `local.m` | **still there** (U1 below) |

## Items found at these heads

Classes: **DS** = encodes one dataset's meaning; **G** = holds for any dataset
(decided where cited); **U** = unclear; **M** = only a message names a
dataset, and no logic depends on it.

| # | where | what it does | class | where it would go (Proposed, not decided) |
|---|---|---|---|---|
| U1 | NDI `+internal/sliceTetanus.m` (whole, 938 lines). Recognition 141-176 (`EMPTY:0000220` / `EMPTY:0000221`; names ending "before/after optogenetic tetanus"; `EMPTY:0000074`; "tetanus stimulation target location"); `^bath_(.+)_([a-z])$` at 199; the date-folder regex at 661; the TLS folder regex at 758. Wired at `local.m` 1071-1087 (`resolveSliceTetanus`, 2010-2118), printed as "SLICE / TETANUS (Dabrowska)" (`printSliceTetanus`, 2120-2147). | Mints Dabrowska brain slices from bath stimulator names. Adds the optogenetic-tetanus runs from TLS folder names. Moves baths and recordings from the animal to its slice. Drops the before/after labels. | **DS, Dabrowska.** Already decided: [sliceTetanus to Dab map] (Build pending: NDI-matlab, DID-matlab) and [dataset map edits V2] (Build pending: NDI-matlab, the map step). | The Dabrowska dataset map. `local.m` stops calling it, and the map step runs it after the generic migration ([dataset map edits V2]). The Dab corpus test (`TestMigrateLocalEtaDab`: 56 tetanus runs, 203 slices) moves with it. |
| U1b | NDI `+internal/pathSPromotion.m` `movableSubject` and its `onSlice` branch (249-258, 330-349) | Moves a statement about a region of a slice onto that region's part. | **G as written** (any tissue that is `part_of` something). Today only U1 makes slices. | Keep. It goes idle when U1 leaves the generic stage. |
| U2 | DID `+migrators_j/treatment.m` 130-136 | Carries a `treatment` as v1 (carry-032, "not a manipulation") when its node or name contains "date of birth", "non-survival experiment time" or "experiment time". "Non-survival experiment time" is vhlab's (`+vhlab/treatmentTable.m:89`, `'EMPTY:Treatment: Non-survival experiment time'`). | **U.** It routes by label words, but the result is a carry. Without the list, the same rows reach the final `else` and carry under carry-022 (183-191). The only difference is which register row is cited. | Delete the list and let carry-022 apply; or move it to the vhlab map with the row's real meaning. Either way the generic output is still a carry. |
| U3 | DID `+migrators_j/private/jDoseValue.m` `isVehicle` 294-307, used at 105 and 133 | A vehicle (node EFO:0002677, or a substance named "saline" or "vehicle") with an amount per body mass is a placeholder, not an ingredient amount. The header (45-50) says the case is Hunsberger's control group, written "saline, 1 mg/kg". | **U.** The rule (a vehicle carries no active ingredient) reads as general. Its trigger is one ontology node plus two names, from one writer. Decided as [dose per ingredient] (2026-10-21). | Keep as generic if the team reads it as a rule. Otherwise move the "copied placeholder" reading to the Hunsberger map and carry the row. |
| U4 | DID `+migrators_j/image_stack.m` `isMask` / `isMap` 684-694 | Mask-or-map detection by label words ("mask", "each pixel's value is the identifier", "label map"). | **G, decided** ([Haley mask words leave the generic stage]: "The generic stage keeps mask-vs-map detection"). Either way the result is a carry. | Keep. |
| G1 | DID `resolveDeferredBaths.m` 586-596 and NDI `+internal/stimulusBathToBath.m` 306-315 | A mixture row named `pH`, `osm` or `osmolarity` becomes the formulation's `ph` / `osmolarity`. | **G, decided** ([bath ph and osmolarity are formulation fields]). Three labs write these rows (Birren, Dabrowska, Marder mixtures). | Keep. See the open question on the osmolarity unit in the report. |
| G2 | DID `resolveDeferredBaths.m:isGenericBath` 763-775, `jTreatmentRoute.m:68`; NDI `stimulusBathToBath.m:389` | Location NCIm:C0179246, or the name "bath", is a whole-prep bath: the statement stays on the subject. | **G, decided** (Jess Haley, 2026-10-21, quoted in `stimulusBathToBath.m`'s header). | Keep. |
| G3 | DID `elementDeviceKind.m` 72-84; `resolveEpochProbemap.m:recordingModeMethod` 1610-1653 | NDI element types (lick-spout, reward-well, intraoral-cannula, optogenetic-fiber, imaging modes, patch / sharp modes) become device kinds and method terms. | **G, decided** ([element types batch 1], [element types batch 2], [recording mode terms], [imaging mode terms]). Keyed on NDI's element-type vocabulary, not on a dataset. | Keep. |
| G4 | NDI `+internal/stimulusRecipe.m`, `stimulusPresentationToItem.m` (the NewStim parameter lists at 757 and 1390-1392), `hartleyBasisGratings.m` | The NewStim / Hartley stimulus vocabulary (`fps`, the recipes). | **Per-software default, decided** ([NewStim recipes are a default]). Not one dataset's. | Keep (workbook default). |
| G5 | NDI `+internal/etaShape.m` 659-661 | `WBStrain:<n>` becomes `WormBase:WBStrain<n>`. | **G, decided** ([WBStrain prefix is generic]). | Keep. |
| G6 | NDI `+internal/ingestedArchiveBodies.m` 411, 421 | Reads NDI's own ingested file names (`ai_group1_seg.nbf_#`). | **G**: NDI's storage format, the same in every dataset. | Keep. |
| G7 | DID `unitQualityLabels.m:labelOf` 120-131 | Lower-cases the spike-sorter quality labels single / multi / good / mua / noise. | **G**: NDI's spike sorter writes them (`+ndi/+app/spikesorter.m:272`). | Keep. |
| M1 | DID `+migrators_j/hartley_calc.m` 329, 471; `neuron_extracellular.m` 567-568 | Error text cites corpus 20211116 as evidence for a structural refusal. | **M.** The condition is structural. Only the message names a corpus. | Keep the rule. Optionally drop the corpus name from the text. |
| M2 | DID `+migrators_j/epochfiles_ingested.m:285`, `stimulus_presentation.m:175` | Message text: "... of 6,921 corpus documents". | **M.** | As M1. |
| M3 | DID `+migrators_j/treatment_transfer.m` 36-39 | Carries every `treatment_transfer` (carry-107). The note names "Babu reimport" as where it is read. | **M** (decided [treatment transfer stays v1]). Carrying the class is generic. | Keep. |

## What this audit did not look at

- DID-matlab `+did2/+build`, `+did2/+schema`, and NDI-matlab outside
  `+ndi/+migrate`. These are not the generic migration stage.
- Rules tuned to one dataset that name nothing the patterns match. These
  would show up as corpus results that only one dataset produces. That is
  not measured here.
- The NDI importers under `+ndi/+setup/+conv/*` are the dataset maps and
  imports themselves, so they are out of scope.

## Proposed next steps (not decided)

1. U1 is the only remaining **DS** item. Its move is already decided and
   tracked: [sliceTetanus to Dab map] and [dataset map edits V2]. Both wait on
   NDI-matlab's map step.
2. The team decides U2 and U3 (questions in the report).
3. If the team agrees the list is complete, close the audit part of
   [dataset-specific logic leaves the generic migration]. Its remaining build
   is then the [sliceTetanus to Dab map] move.
