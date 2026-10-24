# Corpus-code audit: review sheet (2026-10-24)

**State: proposed, not decided.** Nothing here is a decision. `schemas/V_eta_go_forward_class_audit.md` cites it as `Proposed (not decided) [corpus code bins]`, and it waits for the team (Jess Haley and Steve Van Hooser) to confirm the bins and answer the questions below.

Read-only audit of the generic migration code at the locked heads: DID-matlab 7efd113 and NDI-matlab 670f362. Every bin is **PROPOSED**. The full reports, with file, function, decision tag and test for every row, are:

- `[DID-matlab.md](DID-matlab.md)`
- `[NDI-matlab.md](NDI-matlab.md)`

## Denominator

| repo | .m files | read in full | read in part | grep only |
|---|---|---|---|---|
| DID-matlab `+did2/+convert` | 218 | 24 | 22 | 172 |
| NDI-matlab `+ndi/+migrate` | 37 | 19 | 7 | 11 |

Where a file was searched by grep only, a missing finding means **not measured**, not clean. Each file got a code-only grep (comments stripped).

## Counts

| bin | DID | NDI | meaning |
|---|---|---|---|
| **B** one dataset's shape | 7 | 13 (7 are sliceTetanus) | moves to that dataset's map; the generic stage carries the item as v1 |
| **C** per-class default | 24 | 20 | becomes a workbook default, confirmed per dataset |
| **A** generic | 11 | 9 | stays |
| **?** | 1 | 3 | listed below |
| **blockers to lossless** | 15 | 13 | places that drop or rewrite information today |

## Bin B, by dataset

- **JH (Haley):**
  - DID: the encounter-table map, the patch-geometry map, the whole `resolveLawnPlateSubjects` pass, the `image_stack` mask-label matching, and the position/distance cases in `resolveEpochProbemap`.
  - NDI: `jhOwners`, `splitJH`, the video-scale reader, and the `_head_`/`_tail_` body-part string match in `epochSeriesBodies`, plus the plate join in `imagedEntitySubjects`.
  - **NDI has no JH corpus test.**
- **Dab (Dabrowska):** all of `sliceTetanus`, 7 rules. It uses element-name and file-path regexes, infers tetanus manipulations, and *deletes* documents. It is already decided to stay in NDI's second pass for now ([sliceTetanus stays in NDI]). As a dataset map, it moves next to `+setup/+conv/+dabrowska/V2_decisions.md`.
- **Babu:** the two media in `jTreatmentRoute:isMedium`, and the heat rows in `treatment_drug`. **There is no Babu corpus.** Only unit tests cover these.

## Questions for you (and Steve)

1. **Are the bins right?** In particular:
   - (a) DID `treatment:termNumberKind` reads one term as hours, and that term has a single writer (vhlab). B or C?
   - (b) NDI `etaShape:curie` rewrites `WBStrain:` to `WormBase:WBStrain`. A (prefix spelling) or B (JH)?
   - (c) `SubjectLocalIdentifier` / `SubjectDocumentIdentifier`: an NDI table-dictionary convention used by more than one lab. A or C?
   - (d) The NewStim recipes are lab software, not an NDI class. C as proposed?
2. **A decided rule is applied after it was reopened.** `ontology_image` still applies [non-area image node]. `V_eta_spatial_transcriptomics_plan.md` reopened it on 2026-10-22 as **not decided**. Should the code stop applying it?
3. **Fabricated values.** `'2024-01-01T00:00:00.000Z'` is written as a timestamp when the source has none. That happens in 14 DID files plus 2 NDI files. `image_stack` also defaults `YXCZT`/`uint16`, and `metadata_editor` writes `'(unnamed dataset)'`. Proposal: a lossless stage records "not stated" instead of a made-up value. Yes?
4. **The losslessness gap is the real work.** The worst cases:
   - `sliceTetanus` deletes documents;
   - the strain passes drop assertions and openMINDS fields (`breedingType`, `stockNumber`, `digitalIdentifier`, …);
   - `gratingRecipe` keeps 5 of the periodicstim fields;
   - the encounter map drops every unlisted column, and a missing onset becomes 0;
   - `position_metadata` drops `units`/`dimensions`;
   - the tuning migrators drop unmapped fields with only a note;
   - `treatment` quarantines instead of passing through.

   Proposal: the generic stage keeps the v1 document (or the dropped fields) whenever it can't place everything. Yes?
5. **Order of the move.** Proposal:
   1. Fix the blockers first, so the generic stage is lossless.
   2. Then move bin B into per-dataset maps, JH and Dab first. The corpus tests are the guard: generic stage + map == today's output.
   3. Bin C waits for the workbook.

## Caveats on the evidence

- The corpus tests run in discovery mode. They show integrity, not that a branch is right.
- The DID agent did not verify whether `epochMint`'s dropped duplicate clocks survive on the source document.
- I spot-checked four claims against the code, and all four held:
  - the 2024-01-01 count (14 DID files);
  - `sliceTetanus`'s `removed` plan;
  - `colNum` defaulting to 0;
  - the `[babu-media]` citation.
