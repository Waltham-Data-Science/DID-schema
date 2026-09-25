# #73 review — open items after the 2026-09-25 class-set audit

> **STATUS at end of 2026-09-25 session.** DONE (decided + built schema-side, items 50–56 in
> the decision record): 3 (names/duplicate declarations → item 54, plus `method_parameters`
> `name`), 4 (leaves only when needed → item 50), 5 (`logical_observation` retired → item 52),
> 6a (run environment → two `software` edges, item 53), 6b (channels → `acquisition_channels`,
> item 56), 6c (`epoch.instrument_id` dropped, item 55); also `image` retired (item 51) and
> cardinality only on repeated edges. TABLED: 1 (`control_designation`; findings below),
> 2 (`fitcurve` / `model_fit`). NEXT: 7 onward. Item 56's required edge is kept optional in the
> schema until the DID-matlab rig-minting pass lands. PR #76's checklist covers items 1–56.
> **Later the same session:** DONE 8 (area stays m², item 57), 13 (session_id edges dropped,
> item 57), 16 (`response_unit` term, item 57), 18 (`receptive_field.value` storage_mode/method
> dropped, item 57), 20 (ngrid stays until the last passthrough, item 57); BUILT the signed
> 21 (`sample_time` retired), 22 (inline `method_parameters` = `parameter[]`), 23 (`conditions`
> Amendment 2). TABLED 17 (`harmonic_component` control shape) and 19 (`clock_alignment`
> inheritance). **25 IS NOT SIGNED** -- it was filed here as signed-unbuilt, but the governance
> audit reads `contrast_sensitivity` DECIDED-UNSIGNED and the tuning sign-off is scoped to
> tuning. Its small T14 fix (`model_fit.goodness` declares no fields) and the placement question
> (fits/significance on the composite vs the leaf, as tuning does) need a team call.
> Still open for decision: 7, 9, 10, 11, 12, 14, 15, 24 (blocked on the unit vocabulary).

Working list, saved so it survives the session. **It records questions, not decisions**:
decided items are in `schemas/V_eta_spatial_transcriptomics_plan.md` (items 1–49), and
nothing here is signed. Source reports are beside this file (`audit_A_*`, `audit_B_*`,
`audit_C_*`, `audit_mechanical_output.txt`).

## Parked for their own discussion
1. **`control_designation`.** Which presented items are controls. Proposed: a `logical`
   (true/false per item) calculation. Open: is it a statement about the animal's presentation
   or a property of the sequence; what its subject is; `logical` vs a `term` (control / test /
   …). Needs `logical_calculation` restored. Its edges are untouched by T15 until decided.
   **Tabled 2026-09-25 with findings:** the v1 field is a PER-TRIAL PAIRING (each trial's
   paired blank trial, 1-based, NaN = none; `tuning_response.m:616-660`), not a list of
   controls. Since NDI#912 (`tuning_response.m:293-298`) the response calculation reduces it
   to "which stimulus is the blank" before calling vlt; no other reader uses the pairing.
   Options discussed and not chosen: (a) standalone class ⊂ base, corrected to the pairing;
   (b) fold into `harmonic_component_calculation` (`control_trial` per reading + method in
   method_parameters) -- user unsure; (c) keep only "which stimulus is the control"
   (`visual_grating.blank` already has it) and treat the pairing as a vlt-rebuilt cache.
   Unmeasured: whether any corpus has control docs with no response doc.
2. **`fitcurve` → a standalone `model_fit` data type** (item 49): equation, named parameters,
   independent/dependent variables, constraints, goodness, sampled fit; the tuning
   `model_fit[]` entry would share it. `polynomial` stays separate.
3. **Duplicate declarations (audit item 5).**
   - `software.name`, `strain.name`, `method_parameters.name` vs `base.name`: one fact in two
     places? (a) block field is the name, `base.name` left alone; (b) drop the block fields,
     use `base.name` (emitter + NDI reader changes). Claude leans (b).
   - `subject_calculation` redeclares `software_id` only to make it required. Proposed: a
     declared, gated rule "a subclass may tighten an inherited edge to required"; any other
     redeclaration fails.

## Decisions still to walk through (audit group A)
4. **T12 leaves with no written warrant:** `voltage_`, `current_`, `force_`,
   `concentration_manipulation` (a code comment only; `concentration_manipulation` overlaps
   `dose_manipulation`); `gain_assertion` / `gain_observation`.
5. **`logical_observation`: keep or retire** (no user since `valid_interval` moved to
   `time_observation`; tied to item 1).
6. **Facts modelled twice:** inline `execution_environment` vs the `runtime_environment_id`
   edge; `subject_interaction.channels` vs `acquisition_channels`; `acquisition_system_id` on
   interactions vs `epoch.instrument_id` → `entity` (a union target is now expressible).
7. **`chemical` / `formulation` / `dose`** declare the substance+amount shape separately and
   already disagree; `chemical.value.amount` is typed `concentration` while an `amount`
   (moles) type exists.
   **DECIDED AND BUILT schema-side 2026-09-25 (jess; no sign-off line):** see
   `V_eta_spatial_transcriptomics_plan.md` item 59 -- chemical / formulation / dose are
   always documents; `formulation.ingredient_id` + `value.ingredients[]`; `dose.formulation_id`
   + how much given + `amount_per_body_mass`; new `product` entity; `route` dropped;
   `amount` -> `substance_amount`; `concentration` + `osmolar`.
8. **`area` in square meters beside `volume` in liters** (practical units).
9. **Standalone data-type documents** have nowhere for `datum_type`, `storage_mode` or
   `key_labels_id`; `image.keys.labels_from` cannot work on a standalone image; where a
   referenced value's `keys` live.
   **DECIDED AND BUILT schema-side 2026-09-25 (jess; no sign-off line):** item 60 -- value
   descriptors move to `data_type`; `storage_mode` -> the boolean `data_body`.
10. **`acquisition_metadata_file`:** bytes outside the two data bodies, `_file` in the name
    (T6/T11), and its doc (TSV) vs the ledger (`.nbf.tgz`) disagree.
    **DECIDED AND BUILT schema-side 2026-09-25 (jess; no sign-off line):** item 61 -- the
    class retires; `data.bin` becomes an `opaque_body` of the stimulator's term_manipulation.
11. **`method_parameters.other`** is an untyped bag.
12. **`clock_alignment_configuration` vs `method_parameters`** (open in the clock plan).
13. **`session_id`** edge and `base.session_id` hold different ids on one document.
14. **Binding value sets** are spelled three ways (bare names, CURIE strings, `{node,name}`).
15. **Container words** (`metadata`, `data`) in signed infra class names.
16. **`tuning_curve`:** `response_units` is free text; `independent_variables[]` has no
    source fields or labels; mean/stddev/stderr vs item 15's "another column is a key".
17. **`harmonic_component`** uses flat `control_real`/`control_imaginary` where tuning nests
    `control`.
18. **`receptive_field.value.storage_mode`** duplicates the statement's `storage_mode`.
19. **`clock_alignment`** inherits `polynomial.value` and `relation.value_id` (T6 question).
20. **`ngrid`: delete vs fold into `sampled_body`** — the record disagrees with itself.

## Signed but never built (audit group B) — build items with cross-repo work
21. Retire `subject_interaction.sample_time` (data_body sign-off 2026-08-14); nine call
    sites across both repos still write it; 28 composites' docs still cite it.
22. Give the inline `subject_interaction.method_parameters` the signed `parameter[]` shape.
23. Restructure `conditions` per data_body Amendment 2 (cardinality 1, descriptors up,
    `count` flattened).
24. Bind `keys.unit` (Amendment 1) — first needs a unit vocabulary chosen (binding
    worksheet row 1).
25. Bring `contrast_sensitivity` in line with the #73 tuning shape (`model_fit.goodness`,
    `interpolated_values.c50`, fits/significance placement).

## Lightsheet OME-Zarr (NDI-matlab PR #979, open; added 2026-09-25)
Two new v1 classes, `lightsheetZarrPyramid` and `lightsheetZarrLevel`, on NDI branch
`claude/lightsheet-zarr-ndi-viewer-djp5vk` (head `60a79cf0e`); not on NDI `origin/main` yet.
Writer facts (the writer wins over the docs): ONE pyramid per source volume
(`fromOMEZarr.m:12-13`; the branch README says one per reduction and is stale); one level per
unique array, the shared level 0 with `reduction_function 'none'`, reduced levels `'mean'` /
`'max'` (`makePyramid.m:12-19`, `:293`); chunk bytes as a 1-based `chunk.bin_#` series, written
only when `materializeChunks` is true, which defaults to FALSE (`:71`); codec `raw` or
`blosc-zstd` (`:73`), blosc with shuffle 1 (`:746-748`); `fill_value` always 0 (`:302`).

Proposed mapping (item 29 + item 51, no new class): the pyramid becomes an
`intensity_observation` (`element_id` becomes `instrument_id`, `pipeline_version` a `software`
entity); axes / voxel size / translation / units become keys [t, c, z, y, x]; `dtype` becomes
`datum_type` + `byte_order`; each level becomes a `sampled_body` (level 0 the measurement,
reduced levels `redundant`); `chunks` become each key's `chunk`, `chunk.bin_1..N` becomes
`body_data_0..N-1`; `source_file_id` becomes an unheld body (item 25).

Decisions needed before the schema and migrator can be written:
- **L1. Where a reduced level says mean vs max.** Same keys, different values; `sampled_body`
  has no field for it. Precedent: pyraview's min/max is a `statistic` key (item 15; decided,
  not yet emitted by DID-matlab `pyraview.m`).
  **Walked 2026-09-25 (jess agreed; not built, no sign-off line):** option C. `conditions`
  (the Amendment 2 shape) is added to **`data_body`**, so any body may carry them (a lossy or
  preview opaque copy differs in content, not only encoding). Rules: (1) keys are exactly the
  stored array's dimensions (`sampled_body` only), a length-1 stored dimension included and no
  key for a dimension not stored -- so lightsheet `t` is a key iff the store has it; (2) a
  condition is a one-value fact true of every value in its scope that is not a stored
  dimension; (3) on the statement when true of all bodies, on a body when true of that body
  only; (4) a variable appears at most once across a statement and any one of its bodies --
  checked in batch, since the body -> statement edge (`owner_id`) is kept and the statement
  does not list its bodies (a batch census also flags a `storage_mode: body` statement with no
  body); (5) inline values follow the same rules. The `conditions` doc is broadened beyond
  "experimental conditions". Lightsheet reduced levels carry `summary statistic: mean|maximum`
  as a body condition; pyraview's min/max stays a key (a stored dimension, n 2). Rejected: a
  one-position `statistic` key (A: a key for an unstored dimension), a `sampled_body.statistic`
  field (B), one observation per reduction, and a statement -> bodies edge (every added body
  would need a new statement id).
- **L2. The value of a missing chunk.** Item 17 says a missing member is an "empty chunk" and
  never says what value it holds; the format declares `fill_value`.
  **Walked 2026-09-25 (jess agreed; not built, no sign-off line):** B + i. `fill_value` is
  added to `sampled_body` (optional, in `datum_type` encoding, meaningful only when
  `complete: true`). The `chunk` doc states: a dense body's chunks are stored at full chunk
  shape and positions at or past `n` are padding, not values (lightsheet `padPermuteBytes`
  `:791-800`, the Zarr v2 convention); a dense body's missing member holds `fill_value` and is
  not allowed without one (batch census flags it); a sparse body's (`complete: false`)
  missing member is no rows (the spatial tiles' "absent tile held nothing"). "Empty chunk"
  leaves the doc. Rejected: a fixed all-zeros rule (wrong where 0 is a real value), fill as a
  condition (an encoding fact, not a value fact), cut-short edge chunks, a per-body padding
  field.
- **L3. Levels with no bytes (the default).** Each level would be an unheld body recorded by
  location, and the store's `fileReference` a second unheld copy of level 0.
  **Walked 2026-09-25 (jess agreed; not built, no sign-off line):** B″. Evidence: by default
  no level holds bytes (`makePyramid.m:52-54`), a level's `chunks` is a planned re-tiling, not
  the store's (`:46-50`), and no level records its NGFF path. So: (a) the two body classes
  split by WHO LAYS OUT THE BYTES -- `sampled_body` = raw bytes laid out by V_eta (keys
  required, plus `byte_order` / `datum_order` / `chunk` / `fill_value`); `opaque_body` = bytes
  laid out by their own `format`, with keys OPTIONAL (the array as the format presents it) and
  no byte-layout fields; `keys` + `complete` move up to `data_body`, and `chunk` only on a
  sampled body is a checked rule (this amends L1 rule 1's "`sampled_body` only"); still
  exactly two body classes. (b) The OME-Zarr store becomes an unheld `opaque_body` (format
  OME-Zarr) of the statement with keys for the full-resolution array, taken from the pyramid
  document; `description` names the finest multiscales dataset. (c) Metadata-only level
  documents fold to nothing, reported as a count, after the migrator confirms no inbound edge.
  (d) Materialized levels become `sampled_body`s per L1/L2 beside the store body. (e) The
  store checksum (MD5 of `.zattrs` only, `makeSourceFile.m`) does NOT go into `content_hash`,
  which promises a hash of the payload. Rejected: one unheld sampled body per level (no
  location, wrong chunking), empty bodies (hollow documents), a plain keyless opaque body
  (loses shape and voxel size from the metadata), the store as a sampled body with no layout
  fields (B′).
- **L4. `blosc-zstd` with shuffle** is the first instance of the per-chunk codec the data_body
  plan sec.7 said had none, and named as the trigger for promoting `compression` to a list.
  Blosc's own chunk header is believed to record shuffle and element size (not checked here).
  **Walked 2026-09-25 (jess agreed; not built, no sign-off line):** no schema change.
  `compression: "blosc"`; `codec: "raw"` means no `compression`; `codec_params` (`clevel`,
  `blocksize`: write-time settings) is dropped. Checked here with python-blosc 1.11.4 on
  200,000 bytes of uint16 compressed as the writer does (typesize 2, zstd, clevel 5, shuffle):
  header bytes `[2, 1, 145, 2]` -- flags bit 0 (shuffle) = 1, compressor code 4 (zstd),
  typesize 2 -- and `blosc.decompress` with NO parameters round-trips. So the first real
  per-chunk codec is self-describing and one `compression` value holds; the data_body plan
  sec.7 gets a note saying so. NOT checked: the MATLAB `blosc.encodeChunk` NDI actually calls
  (the writer targets `numcodecs.Blosc`, the same format) -- the DID-matlab migrator test must
  decompress a real NDI chunk with no parameters before this is relied on.

**BUILT schema-side 2026-09-25 (L1-L3; L4 needs no schema change):** `data_body` gains
`keys`, `complete` (moved up from `sampled_body`), `conditions` and the `key_labels_id` edge;
`sampled_body` gains `fill_value`; the `chunk`, `keys`, `conditions` docs carry the rules;
tenets T6 / T13 / T15 table updated; data_body plan amendment note added.
`tests/test_veta.py::test_bodies_split_by_who_lays_out_the_bytes` pins it. The batch checks
(no variable repeated across a statement and one body; a dense body's missing member needs a
`fill_value`; `chunk` only on a sampled body's keys; a `storage_mode: body` statement with no
body) are DID-matlab work, not yet built.

Follow-ups once #979 merges (no new modelling): 2 tombstones + decided targets here (NDI
templates 102 -> 104 moves `coverage.py`, `check_tombstones`, `check_prose_counts`); 2 DID-matlab
migrators (+ NGFF dtype strings in `jDatumType`); NDI `+ndi/+vintage` entries for the
`isa`-query and dependency-name readers (`levelTable`, `LightsheetZarrManager`, `makePyramid`,
`fromOMEZarr`). Note for the NDI PR: the planned `chunk_index` side-field is unnecessary under
"a missing member is an empty chunk".

## Worksheets to fill (beside this file)
- `veta_term_worksheet_73.csv` — 71 terms to find or mint (axis, direction, origin, assay,
  variable). Ontology registries were unreachable from the review container.
- `veta_binding_worksheet_73.csv` — 24 fields needing a value set and strength.

## Governance
- 182 → 180 persist classes. Of the 180-odd audited: ~46 signed in current form, 16 signed
  then revised without a new signature, 4 field-level only, 19 decided but unsigned, 97 with
  no decision record (mostly the inherited quantity family). See `govtable.md`.
- The #73 decisions (items 1–49) carry no `TEAM-SIGN-OFF` line. `team_signoff_lines_DRAFT.md`
  is an out-of-date draft, not a signature.
- `tools/status_board.py` counts a sign-off quoted inside a code block
  (`V_eta_method_parameters_plan.md:683`) and still counts the superseded 2026-09-22 spatial
  sign-off (`V_eta_go_forward_class_audit.md:796`).

## To verify
- Whether a v1 `hartley_calc` document carries a `hartley_calc` block with fields of its own
  (needs NDIcalc-vis-matlab's writer; not attached in the review container).

## Cross-repo follow-ups
The DID-matlab and NDI-matlab checklists live in PR #76's description (updated 2026-09-25
for items 1–49, including the `neuron_extracellular.m` item-48 calculations).
