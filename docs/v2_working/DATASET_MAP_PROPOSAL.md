# The per-dataset map: a design proposal

**Proposed (not decided).** Claude, 2026-10-26. Nothing here is built. The team
(Jess Haley, Steve Van Hooser) decides.

## Heads read

| repo | ref read | commit |
|---|---|---|
| did-schema | local checkout, branch `claude/ecstatic-pascal-md91fw` (decision lines) | 660c16c |
| did-schema | worktree `scratchpad/wtcr`, branch `claude/carry-register` (the register) | d89858e |
| DID-matlab | `origin/V2` (after `git fetch origin V2`; HEAD not moved) | f6486be (#250) |
| NDI-matlab | `origin/V2` (after `git fetch origin V2`; HEAD not moved) | 9b990616d (#1072) |

All code citations below are `git show origin/V2:<path>` at those commits.
"By reading" means I read the code and did not run it. No MATLAB was run.

The decision lines are in `docs/plans/did_v2_go_forward_class_audit.md` (did-schema
660c16c): [one correct reading] :1220, [carry register] :1200,
[dataset-specific logic leaves the generic migration] :1208,
[Haley logic leaves the generic migration] :1206, [sliceTetanus to Dab map]
:1152, [dataset audit batch 1 and 2] :1228, [one-reading quick answers] :1238,
[table rows into the dataset audit] :1212, [migration not generalizable] :1096,
[v1 import stages] :1100.

---

## 1. What exists today

### 1.1 No map, and no hook for one

- No dataset map file and no code that applies one. `git grep -n -i
  "needs_mapping\|dataset map\|datasetMap\|dataset_map" origin/V2 -- src tests
  .github` in NDI-matlab returns one hit, a test comment
  (`tests/+ndi/+unittest/+migrate/TestMigrateLocalEta20211116.m:321`).
- `ndi.migrate.local` has no per-dataset option. Its arguments are DryRun,
  Backup, ContinueOnError, Verbose, Validate, (SchemaCache), TargetVersion,
  SoftwareDedupAfterPassOne (`src/ndi/+ndi/+migrate/local.m:184-191`). Every
  second-pass step runs on every dataset.

### 1.2 Where carried documents end up

- Pass 1 (DID) carries a document by returning its input unchanged with a
  `carried_as_v1` report note (`+did2/+convert/+migrators_j/treatment.m:211-218`,
  `carryAsV1`; `+did2/+convert/v1_to_v2.m:331-350` swaps in the untouched
  source body).
- The note text starts `needs_mapping:` when the document has several readings
  (`+migrators_j/private/jCarryWhy.m:10-11`). The note lives in the run report,
  not on the document.
- At the end of NDI's second pass, `carryUnchangedAsV1` replaces every document
  no step changed with its v1 source, stamped `did_v1`
  (`local.m:1112-1149`). These are written into the same V2 sqlite file as the
  V2 documents (`local.m:1165-1192`). So a carried document sits in the
  dataset's V2 database as a `did_v1` document.

### 1.3 Where `needs_mapping` carries are made (DID-matlab f6486be)

| # | site | v1 class | when | homes named in the note |
|---|---|---|---|---|
| M1 | `+migrators_j/treatment.m:129-133` | `treatment` | node is not ChEBI and its term states no number unit | manipulation (dose / exposure / temperature / term) or observation |
| M2 | `+migrators_j/private/jTreatmentBodies.m:81-89` (route from `jTreatmentRoute.m:62-64`) | `treatment`, `treatment_drug`, `virus_injection` (ChEBI substance) | no location recorded | manipulation: immersion or dose |
| M3 | `jTreatmentBodies.m:90-95` (route `jTreatmentRoute.m:79-81`) | same | location is neither bath nor UBERON | manipulation: dose / exposure / temperature |
| M4 | `+migrators_j/image_stack.m:258-277` | `image_stack` | label reads as a mask or map | calculation (logical mask / label map) or observation |
| M5 | `+migrators_j/ontology_table_row.m:67-82` | `ontology_table_row` (with a subject) | always | per column: assertion / observation / manipulation |

M5 is reached for real rows through NDI's refold: `ontologyRowSubjects` adds
the subject edge and re-folds the row through pass 1
(`src/ndi/+ndi/+migrate/+internal/ontologyRowSubjects.m:1-18`). By reading,
the refold now returns the row unchanged, so it ends carried.

### 1.4 The carry register (did-schema `claude/carry-register` d89858e)

`schemas/registry/did_v2_carry_register.json`: 21 rows (8 `malformed`, 7
`awaiting_home`, 4 `not_modelled`, 2 `needs_mapping`; counted with a
one-line Python read of `rows`). The two `needs_mapping` rows:

| id | v1 class | homes | resolved_by |
|---|---|---|---|
| carry-020 | `treatment` | exposure; dose | "the Babu dataset map entry, e.g. \"Babu: MICRO:0000480 -> exposure\"" |
| carry-021 | `treatment_drug` | temperature manipulation; dose | "the Babu dataset map entry for its heat treatments (not yet written)" |

`resolved_by` is free text. `tools/check_carry_register.py` (C1-C4, header
:1-40) checks the shape and the decision tag, not `resolved_by`.

**Gap.** The code makes five kinds of `needs_mapping` carry (M1-M5); the
register holds two. M1, M2, M4 and M5 have no register row. Since M3 is now
"any non-UBERON location" (`jTreatmentRoute.m:41-47`), carry-020/021 describe
it only by its Babu example.

### 1.5 Per-dataset material that exists (NDI-matlab 9b990616d)

| dataset | what | input | where |
|---|---|---|---|
| Haley (JH) | a full V2 import, 13 stages | **raw source only** (`import_V2(dataParentDir, ...)`, args at `+setup/+conv/+haley/import_V2.m:149-166`; no v1-document input) | `+haley/import_V2.m`, `import_V2_spec.json` (sections: organizations ... `ecoli_patch_layout`, `corrections`), `import_V2_decisions.md` (prose log), `trackDocuments.m`, `encounterDocuments.m`, `geometryDocuments.m`, ... |
| template | a starter V2 import | raw source | `+template/import_V2.m`. Its header states the rule "Dataset-specific mapping lives in the SPEC (import_V2_spec.json) ... The code stays generic" (:30-34) and "Every choice is recorded in the DECISION LOG" (:35-36) |
| Dabrowska (Dab) | v1 import `doImport.m` (unchanged); a decision log `V2_decisions.md` (9 decided rows, all 2026-10-21); v1 data dictionaries (`tableDoc_dictionary.json`, `dabrowska_mixtures_dictionary.json`, `dabrowska_bathtargets.json`) | v1 import reads raw | `+setup/+conv/+dabrowska/`. The code that carries the V2 decisions is NOT there: it is `+migrate/+internal/sliceTetanus.m` (938 lines), called from the generic second pass (`local.m:965-980`, `V2_decisions.md:7-10`) |
| Babu | v1 import only (`import.m`, `treatments.json`, ...) | raw | `+setup/+conv/+babu/` (no V2 file) |

### 1.6 What #1072 and #250 removed, and where it went

| piece | removed by | went to |
|---|---|---|
| NDI `imagedEntitySubjects.m` (whole, 1,042 lines) and its call | NDI #1072 (`git diff --stat e0177b345d 9b990616d`) | deleted. No caller left (`git grep imagedEntitySubjects origin/V2`: comments only) |
| NDI call of `did2.convert.resolveLawnPlateSubjects` | NDI #1072 (`local.m` diff) | DID keeps the function, uncalled, marked `WIRING-EXEMPT` (`+did2/+convert/resolveLawnPlateSubjects.m:33-39`) |
| NDI `epochSeriesBodies.m` JH position/distance split | NDI #1072 (448 lines changed; header now "NOT THE JH SERIES") | deleted; the Haley import makes tracks from source (`+haley/trackDocuments.m`) |
| DID `ontology_table_row.m` encounter and patch-geometry maps | DID #250 (778 lines changed) | deleted ("NO PER-TABLE MAPS", `ontology_table_row.m:14-21`); Haley import (`encounterDocuments.m`, `geometryDocuments.m`) |
| DID `resolveEpochProbemap.m` JH position/distance | DID #250 | deleted; "such an epoch stays a plain acquisition_epoch, and the Haley V2 import makes the tracks" (`resolveEpochProbemap.m:2084-2086`) |
| DID `image_stack.m` Haley region words | DID #250 | deleted; mask/map now carried (M4) |
| DID Babu media (`isMedium`) and heat (`isHeatOnly`) | DID #250 | deleted (`git grep isMedium\|isHeatOnly origin/V2 -- src`: none); now M3 carries, resolved by "the Babu map" (carry-020/021). No Babu map or Babu V2 import exists |
| NDI `sliceTetanus` | **not removed** | still in the generic second pass (`local.m:965-980`); [sliceTetanus to Dab map] is "Build pending" |

So nothing removed tonight moved into a map. The Haley pieces are covered by
the Haley import from raw source. The Babu pieces are not covered by anything
yet.

### 1.7 Where a map could be applied

The second pass has fixed steps in order (`migrateStepMark` calls,
`local.m:296-1195`): ... `epochMint` (850) ... `resolveEpochProbemap` (921) ...
`resolveSliceTetanus` (980), `resolvePathS(located)` (998) ...
`carryUnchangedAsV1` (1149), `settleIngestedFiles` (1163), write (1192).

Two facts constrain where a map can run:

1. `pathSPromotion('located')` runs after `sliceTetanus` on purpose: "AFTER
   sliceTetanus (it matches slice statements by the animal they are about, and
   a statement it moved onto a slice is not moved again)" (`local.m:984-989`).
   A map step that runs after the whole generic pass would run after this.
2. `sliceTetanus` needs the v1 bodies, the migrated structs and `epochMint`'s
   epoch index (`sliceTetanus.m:1-21`). All three are in memory inside
   `local.m`. After the write, only the database is left.

Three places, Proposed (not decided):

| option | where | for | against |
|---|---|---|---|
| A | inside `local.m`, one hook step before `carryUnchangedAsV1`, given a `DatasetMap` option | has every input; a mapped document is "changed" so it is not stamped `did_v1`; no reload | edits the generic stage, which [migration not generalizable] calls "frozen"; still runs after `pathS(located)` |
| B | a hook at `sliceTetanus`'s slot (before `pathS(located)`) | Dab output stays identical to today | the generic pass then has dataset slots; harder to say the generic stage is "done" |
| C | a separate step, `ndi.migrate.applyDatasetMap(path, map)`, run on the written V2 database | generic stage untouched and frozen; re-runnable after a map edit without re-migrating; easy to test "generic + map" | `sliceTetanus` must be adapted to read from the database (the epoch index is the `epoch` documents); Dab region parts made by `pathS(located)` on the animal must be redone by the map |

**Proposed: C**, with the map's own steps allowed to call the generic
`pathSPromotion` again on what they changed. Reason: it is the only option
that keeps the generic stage frozen, and it matches [v1 import stages]
("generic stage is lossless plumbing; meaning comes from a per-dataset decision
workbook"). Option A is the fallback if adapting `sliceTetanus` costs too much.

---

## 2. What a map must resolve

| # | thing | v1 class | V2 home(s) | today | dataset(s) |
|---|---|---|---|---|---|
| R1 | register carry-020 (medium / air) | `treatment` | exposure (manipulation valued by formulation); dose | carried (M3) | Babu |
| R2 | register carry-021 (heat) | `treatment_drug` | temperature manipulation; dose | carried (M3) | Babu |
| R3 | M1, a treatment whose term states no kind (no register row) | `treatment` | manipulation of a value kind; term manipulation; observation | carried | Dab (49, the target-location rows), Soph, JH, 20211116 (counts from the scratch audit `dsaudit/DATASET_SPECIFIC_AUDIT.md` D10, at older heads; not re-measured) |
| R4 | M2, substance with no location (no register row) | `treatment`, `treatment_drug`, `virus_injection` | immersion; dose | carried | Babu, Birren, Hunsberger writers (none in the corpora, same audit) |
| R5 | M4, mask / map image (no register row) | `image_stack` | calculation (logical) of a region; label map; observation | carried | Haley (covered by the Haley import) |
| R6 | M5, table row with a subject (no register row) | `ontology_table_row` | per column: assertion / observation / manipulation, with entity, value kind, unit | carried | Dab EPM / FPS, Babu, Hunsberger, Haley |
| R7 | `sliceTetanus` | `stimulus_bath` (as written V2 baths), `element`, `subject`, `openminds_stimulus` (before/after labels EMPTY:0000220/0000221), `treatment` (EMPTY:0000074), epoch files | slice `entity` type `tissue` + `part_of`; tetanus `manipulation` (EMPTY:0000358) with a `relative_time_reference`; a nested-date animal; statements moved to the slice; labels dropped | runs in the generic pass | Dab |
| R8 | `resolveLawnPlateSubjects` (lawn/plate subjects, patch relabel) | `ontology_table_row` (E. coli tables) | subject, relation, observations | function kept, uncalled | Haley (Haley import) |
| R9 | encounter + patch-geometry table maps | `ontology_table_row` | encounter windows; patch entities | deleted | Haley (Haley import) |
| R10 | JH position / distance tracks | element epochs, `.vhsb` bodies | track calculations | deleted | Haley (Haley import) |
| R11 | `imagedEntitySubjects` plate join | `image_stack` | the image's subject | deleted ([dataset audit batch 1 and 2] (5): "retired") | Haley |

R8-R11 need no map if the Haley V2 dataset comes only from the Haley import
(see Q3).

---

## 3. Proposed shape of the map (Proposed, not decided)

### 3.1 Location and format

- One JSON file per dataset, **in NDI-matlab, beside that dataset's importer**:
  `src/ndi/+ndi/+setup/+conv/+<lab>/V2_map.json`, next to the existing
  `V2_decisions.md` (Dab) or `import_V2_decisions.md` (Haley).
- Why NDI-matlab: the per-dataset importers, specs and decision logs already
  live there (§1.5), and the template's rule is "Dataset-specific mapping lives
  in the SPEC ... The code stays generic" (`+template/import_V2.m:30-34`).
  Why not did-schema: a map is one dataset's meaning, not schema.
- The map is the machine-read part of the dataset's decision workbook
  ([v1 import stages]). The `.md` log stays the prose record. Every map row
  cites a decided row of that log.

### 3.2 Two kinds of row

A table-like rule cannot express `sliceTetanus` (it matches by naming patterns,
folder dates and epoch times; `sliceTetanus.m:26-71`). So two kinds:

**`rule`**: data only, applied by one generic applier.

```json
{
  "id": "dab-r01",
  "kind": "rule",
  "resolves": "carry-0NN",
  "decision": {"document": "V2_decisions.md", "row": 2},
  "status": "proposed",
  "match": {
    "v1_class": "treatment",
    "equals": {"treatment.ontologyName": "EMPTY:0000074"}
  },
  "home": {"class": "manipulation", "value_kind": "term"},
  "settings": {"variable": "EMPTY:0000074", "value_from": "treatment.string_value"}
}
```

- `match` is exact equality on v1 field values (a node, a name, a column key).
  No label-word patterns: each distinct value is its own row, so each is a
  recorded choice.
- `home` names a class (and value kind) in did-schema `schemas/did_v2/`.
- `settings` are what the home needs that the v1 document does not state
  (variable node, unit, direction, which entity a column is about).

**`pass`**: names a dataset function, for logic that is not a lookup.

```json
{
  "id": "dab-p01",
  "kind": "pass",
  "function": "ndi.setup.conv.dabrowska.sliceTetanus",
  "decision": {"document": "V2_decisions.md", "rows": [1, 2, 3, 4, 5, 6, 7]},
  "status": "proposed",
  "consumes": ["stimulus_bath", "element", "subject", "openminds_stimulus", "treatment"],
  "emits": ["entity(tissue)", "entity(organism)", "directed_relation(part_of)", "manipulation+term", "relative_time_reference"],
  "after": [],
  "then_rerun": ["pathSPromotion:located"],
  "test": "TestSliceTetanus"
}
```

The function moves from `+migrate/+internal/` into the dataset's package.

### 3.3 How it is applied

- **Tool:** `ndi.migrate.applyDatasetMap(path, mapFile)` (NDI-matlab), run
  after `ndi.migrate.local` on the written V2 database (option C, §1.7).
- **Order:** `pass` rows in file order (each may declare `after`), then `rule`
  rows. A pass may ask for a generic step to be re-run on what it changed
  (`then_rerun`).
- **Lossless:** a `rule` reads only `did_v1` documents. A document no row
  matches stays `did_v1`, unchanged. A matched document is replaced by its V2
  reading with its source id kept (as the generic migrators do), and must pass
  the round trip of [lossless means round trip]. A row that matches but cannot
  place every field leaves the document carried ([partly placed is carried as
  v1]) and counts it.
- **Idempotent:** a rule cannot match twice, because its output is no longer
  `did_v1`. A pass must detect its own output (e.g. the slice entities exist)
  and do nothing; tested by running the map twice and comparing.
- **Report, denominators first:** documents read; `did_v1` documents read; per
  row: matched, written, left carried (with why). Then `did_v1` documents left,
  by register row id.

### 3.4 How it is validated (gates)

- **NDI-matlab test** (one per map file, in CI): the file's shape; every
  `resolves` id exists in did-schema's carry register and is a `needs_mapping`
  row; every term node is in the term registry; every `home.class` is in
  `schemas/generated/index.json`; every `match` field exists in the NDI v1
  template of that class (`origin/main`); every `decision` row exists in the
  dataset's log; every `pass` function exists and has its `test`.
- **Corpus test** for a dataset with a corpus: generic + map run on the corpus
  zip; for Dab, the result must match today's output ([sliceTetanus to Dab
  map]), document for document, except for differences the team lists.
- **did-schema gate** (an addition to `tools/check_carry_register.py`): a
  `needs_mapping` row's `resolved_by` becomes a list of map row references
  (`NDI-matlab:+dabrowska/V2_map.json#dab-r01`) or the literal `"none yet"`.
  A reference that does not resolve at the locked NDI head fails; `"none yet"`
  is listed, not failed.

### 3.5 Relation to the carry register

- A map `rule` resolves exactly one register row (`resolves`). A register
  `needs_mapping` row lists the map rows that resolve it, per dataset
  (`resolved_by`). Both directions are checked (§3.4).
- A register row stays: the generic stage still carries the document. The map
  only removes the carry for the dataset whose map has a row.
- First, register rows are needed for M1, M2, M4, M5 (§1.4 gap).

---

## 4. Dab as the first map

Proposed rows for `src/ndi/+ndi/+setup/+conv/+dabrowska/V2_map.json`. Every
one is Proposed (not decided).

| id | kind | match / function | home and settings | decided basis | register |
|---|---|---|---|---|---|
| dab-p01 | pass | `ndi.setup.conv.dabrowska.sliceTetanus` (moved from `+migrate/+internal/sliceTetanus.m`) | slices (`entity` type `tissue`, `part_of` animal); one tetanus `manipulation` per run, method EMPTY:0000358; window on `exp_global_time`; nested-date animal; protocol parameters from `TLS <f> Hz <d> s` folders; before/after labels dropped after rebuild; then re-run `pathSPromotion` (located) | `V2_decisions.md` rows 1-7, 9 (DECIDED, Jess Haley, 2026-10-21); [sliceTetanus to Dab map] | none (it is not a carry; see Q5) |
| dab-r01 | rule | `treatment`, `treatment.ontologyName` = EMPTY:0000074, `name` = "Optogenetic Tetanus Stimulation Target Location", `string_value` one of UBERON:0001930 / UBERON:0002034 / UBERON:0001929 (`doImport.m:282-283, 301-305`) | consumed by dab-p01: the condition (variable EMPTY:0000074, value the UBERON node) on the run's tetanus manipulation (`V2_decisions.md` row 2). For an animal with no run: see Q6 | row 2; [one-reading quick answers] (Q4) keeps the name | new row for M1 |
| dab-r02 | rule | `ontology_table_row`, column `Treatment` (`tableDoc_dictionary.json`: "EMPTY:Treatment: CNO or saline administration"), EPM table | a manipulation of the row's subject (dose of CNO or of saline?) | none: open (Q7) | new row for M5 |
| dab-r03 ... | rule | `ontology_table_row`, one row per EPM / FPS column key in `tableDoc_dictionary.json` (entries, head entries, time, percent time, latency, ...) | an `observation` of the row's subject, value kind and unit per column (count, duration in s, percent, ...) | none: open (Q7). The scratch one-reading review lists "percent time becomes a time" and "chamber identifier becomes a count" as wrong guesses of the old code | new row for M5 |
| dab-r0x | rule | the table row's subject: `SubjectString` = "EMPTY:Subject local identifier" | the subject found by local-identifier match (route 3, "Dabrowska's only route", [dataset audit batch 1 and 2] (3)) | decided for the generic stage | n/a |
| (bath) | none proposed | `stimulus_bath` | stays generic: the bath is an immersion by its location NCIm:C0179246 (`dabrowska_bathtargets.json`; `stimulusBathToBath.m:44-55`) | [bath is a manipulation] | n/a |

**Bath variable, if the team wants it in the map.** The bath's `variable` is
the first mixture row (`stimulusBathToBath.m:259, 456-461`;
`resolveDeferredBaths.m:426, 528-531`). The scratch one-reading review
(question 3) reports 1,172 Dab ACSF baths that say "sodium chloride",
131 of them with the antagonist d(CH2)5 (not re-measured here). No decision
line answers it (grep of the class audit for "primary chemical" / "first
mixture row": no hit). If the answer is "the map names it", the Dab map gets
one rule per mixture (from `dabrowska_mixtures_dictionary.json`) naming the
manipulated ingredient. See Q8.

---

## 5. Open questions for the team

Each answerable in one line.

1. **Where does the map run?** (a) a separate step on the written database
   (proposed), (b) a hook before `carryUnchangedAsV1`, (c) a hook at
   `sliceTetanus`'s slot?
2. **Where does the map file live?** NDI-matlab beside the importer
   (proposed), or did-schema?
3. **Does a dataset with a V2 import from source (Haley) need a map at all?**
   Proposed: no; its V2 dataset is the import, and its generic output stays
   plumbing.
4. **May a map row match on label words**, or only on exact values (proposed:
   exact values only)?
5. **May a map change or remove documents the generic stage wrote as V2**, not
   only resolve carries? `sliceTetanus` does both: it moves baths and
   statements written on the animal, and drops the 635 approach labels.
6. **An opto animal with a target-location treatment but no tetanus run:**
   carried as v1, or a term assertion on the animal? (`sliceTetanus.m:577-580`
   kept the old manipulation for such an animal.)
7. **Dab EPM / FPS columns:** may Claude draft one row per column for Jess to
   check, with "CNO or saline" as a dose manipulation?
8. **Bath variable:** one fixed generic variable for every bath, or the
   manipulated ingredient named in each dataset's map?
9. **Register first?** Add `needs_mapping` register rows for M1, M2, M4, M5
   before the Dab map, and make `resolved_by` a list of map row references?
10. **The Dab reproduction test:** NDI's `TestMigrateLocalEtaDab` (generic +
    map), or a DID-matlab corpus test as the decision line says? DID's corpus
    harness does not run NDI's second pass (`git grep -i slicetetanus
    origin/V2 -- tests tools .github` in DID-matlab: no hit).
11. **Babu:** a Babu map from v1 documents, or a Babu V2 import from source
    (as [babu-media] said: "Plates are ... minted in a proper Babu V2 import
    from source")?

### Things that seem to pull against a decision line

- **[sliceTetanus to Dab map] (:1152) says "the generic stage carries those
  documents as v1".** Today the generic stage writes the Dab baths, the
  per-epoch statements and the approach labels as V2 on the animal, and
  `sliceTetanus` re-shapes them (`local.m:972-978`, the failure message names
  exactly these). Without the pass they stay V2 on the animal, not carried.
  So either the generic stage must recognise Dab documents to carry them
  (dataset logic in the generic stage, against [dataset-specific logic leaves
  the generic migration] :1208), or the map must edit V2 documents (Q5).
- **Ordering.** `pathSPromotion('located')` runs after `sliceTetanus` because
  it depends on the slices (`local.m:984-989`). Moving `sliceTetanus` after
  the generic pass changes what `pathSPromotion` does for Dab unless the map
  re-runs it. "Generic + map reproduces today's output" ([sliceTetanus to Dab
  map]) needs that re-run.
- **By reading, `sliceTetanus`'s treatment step may now find nothing.** It
  removes the per-animal tetanus treatment manipulation, found as a V2
  `manipulation` with variable EMPTY:0000074 (`sliceTetanus.m:567-583`). Since
  DID #250 a `treatment` with node EMPTY:0000074 is carried (M1:
  `treatment.m:119-133`; EMPTY:0000074 has `number_unit: false` in the term
  registry, did-schema 660c16c). It still reads the region from the v1 body
  (`sliceTetanus.m:162-176`), so the condition is still written. Not run;
  `treatment_manipulations_found` on the next Dab e2e run will show it.
- **[one correct reading] (:1220) vs. the bath variable.** A bath whose
  variable is its first mixture row may be "a V2 document whose meaning might
  be wrong" (131 antagonist baths say "sodium chloride", scratch review). The
  generic stage still writes it. Not a contradiction until Q8 is answered.
- **[v1 import stages] (:1100) says "one pipeline, two inputs (raw source or
  v1 documents)".** The Haley import takes raw source only
  (`import_V2.m:149-166`), and the map proposed here is a second, separate
  pipeline for v1 documents. If the decision means one runner for both, the
  map applier should become a stage of the `import_V2` runner instead. Ask
  before building.
- **[migration not generalizable] (:1096) says the generic stage is "then
  frozen".** Options A and B edit it; option C does not.
