# V_eta — the #73 review: spatial transcriptomics, and the structure it needed

**Decided by jess in the #73 review, 2026-09-23 → 2026-09-25, and BUILT (schema side) on
PR #76.** This document is the decision record: what was decided, why, and what was
rejected. Items are numbered as they were decided so later documents can cite "item N".

**The team's `TEAM-SIGN-OFF` line for this record is not written here** — Operating Rule 4
reserves it for the team. Until it is added, `tools/status_board.py` shows the family
as awaiting review, which is the truth.

**It supersedes** the 2026-09-22 Corrected Option C decision for the spatial family
(`V_eta_go_forward_class_audit.md`, DID-schema#70), which kept the eight v1 classes as
verbatim copies, and **revises** issue #67 decision 10 (`harmonic_component_calculation`
deleted) — see item 37.

**Emitters follow.** DID-matlab and NDI still write the old shapes; their changes are the
checklists on PR #76. Until they land, documents written with the old names do not
validate against this schema.

---

## A. The data: what spatial transcriptomics records

A Stereo-seq chip captures transcripts at ~0.5 µm spots across a tissue section. NDI
stores it as a **pyramid** (the counts, binned 1…32), **tiles** (each level cut into
files), **cells** (a segmentation: centroids, outlines, per-cell measures), **cell type
labels**, a **gene list**, a **gene-list mapping** (orthologs/aliases), a **file
reference** (the source `.gef`, not held) and a shared **geneExpression** mixin.

1. **Counts are a `count_observation` of the tissue section**, keys [y, x, gene]. Bin 1
   is the measurement; bins 2–32 are derived, rebuildable levels (item 29).
2. **Cells are a KEY, not subjects.** The segmentation is one statement over a `cell`
   key; every per-cell fact is another statement over that key.
3. **Observation vs calculation is decided by provenance** (T2, built `dfc5306`):
   segmentation, per-cell measures and labels are calculations.
18. **Nothing is carried forward.** None of the eight v1 classes survives as a V_eta
    class; all are migrated into this design and stand as retired tombstones.

## B. Where things are: `position` and `coordinate_system`

4. **`position`** is a data type (coordinates in a coordinate system); centroids are a
   `position_calculation`, probe sites a `position_observation`. `point` was rejected:
   coordinates are lengths, but a position needs a frame `length` cannot carry.
5–9. **`coordinate_system`** (the class name was chosen over `reference_frame`: a frame
   is the space things are measured in, like a clock, not an anchored "when/where"):
   - `relative_to` (REQUIRED edge) — the document the origin is ON (an image, a probe,
     a subject);
   - `origin` (term) — which point on it is zero (image upper-left corner, probe tip,
     bregma). The same concept as a key's `origin`;
   - `dimensions[]` — one per coordinate, in order: `axis` (an AXIS term — not NCIT's
     X-/Y-coordinate, which name values), `positive_direction` (must say whose: "image
     right"), `spacing` (a length; ABSENT = uncalibrated).

   `position.coordinate_system_id` is REQUIRED. Values are in spacing units; metres =
   coordinate × spacing. Cartesian only. Transforms between systems are not part of one.
   Scope: acquisition grids and device frames now; stereotaxic and atlas frames later.
   Rejected names: meaning, variable, increases_toward, direction, axes, zero_point.
10. **Time leaves say "time"** — `absolute_time_reference`, `relative_time_reference`
    (built `6bdf2bf`). `<domain>_reference` means an anchored when/where document.
11. **Boundaries** are a `position_calculation` over [cell, vertex], vertices converted
    to section coordinates at migration; a closed outline is a key with `cyclic: true`.
    A `polygon` type was rejected for now (revisit for holes or multi-part shapes).

## C. The body table: keys, one value, chunks

12. **A key may take its positions from another document's rows** — `labels_from`
    names an `axis_labels_#` edge; `n` must equal that document's row count, and the
    document carries an explicit index column.
13. **Every index is 0-based** — now T14 (built `7daa4c0`).
14. **`axes` → `keys`** in all four places (statement, image value, acquisition epoch,
    sampled body), with `complete` beside them (true = dense grid; false = only listed
    rows exist).
15. **No `values[]` column list.** A body holds exactly ONE kind of value; anything that
    looks like another column is a key (pyraview's min/max is a `statistic` key). The
    value's meaning is the data type/variable, its type `subject_statement.datum_type`
    (once), its byte packing `data_body.format`. Revisit only for two different measured
    quantities side by side that cannot be restated as a key.
16. **`image.value` = { keys, complete, pixels }.** `channels` became the channel key's
    labels, `color_model` is read off that key, and `dtype` is `datum_type`.
17. **Many files per body is a DID file series.** The split is `chunk` on each key;
    chunk *k* (row-major, from 0) is member `body_data_k`; a missing member is an empty
    chunk. EVERY body is a series (an unchunked body is `body_data_0`) — one rule, no
    special case. One body per ARRAY; a series member where only the bytes split. File
    series number from 0 (a DID-matlab change; any series already stored as `NAME_1…`
    must be renamed). Per-member hashes: a recorded gap.
32. **The key's `values` field keeps its name** (the clash that motivated a rename was
    the `values[]` list item 15 removed).

## D. Standalone values, labels, and relations

19. **Every data type is concrete.** T6's `storage_mode: reference` needs a standalone
    value document; a standalone data-type document is CONTENT, NOT A CLAIM.
20. **A body's owner** may be a statement or a standalone data-type document.
21. **The gene list is a standalone `term` document** — the labels of the count
    statement's gene key, stored once and shared. Not a `term_assertion`: no subject fits
    (not the animal — NDI: "a property of a reference, not of any one animal"; not the
    annotation, which is a T9 entity). Dropped: gene_name_completeness,
    n_duplicate_gene_names (computable; "join on node, never name" goes in the docs).
22. **Provenance of reference content** is a `directed_relation` `derived_from`: gene
    list → annotation → assembly, each a **`dataset`** entity (a `web_resource` is WHERE
    a thing lives, per the signed D-F). "Ours" vs "reference" is read off the graph.
23. `gene_symbol_namespace` is dropped (the annotation it came from is recorded).
24. **The gene-list mapping** is a `directed_relation` (list A → list B; relation
    "orthologous gene mapping" | "gene alias mapping"; `method` = tool + version) with
    `value_id` to a standalone `score` (or `logical`) document keyed [gene of A, gene of
    B]. `method` moved up to `relation`. An earlier draft (pairs as the relation's body,
    undirected) was rejected: unordered endpoints, and an untyped score.
25. **An external file not held in the database** (the source `.gef`) is an UNHELD body
    of the statement whose value it stores — recorded by location, not ingested.
    `data_body` gained `hash_algorithm`, `size_bytes`, `file_created`, `file_modified`.
    DID-matlab must give it an explicit "not held" marker (item 34).
26. **`geneExpression` dissolves:** assay → `method`; count_units → the `variable` (UMI
    count vs read count); normalized values → a `score_calculation` derived_from the raw
    counts.
27. **Cell type labels:** a supervised call is a `term_calculation` (values are ontology
    terms — mint one when none exists); an unsupervised clustering is a
    `label_calculation` (item 33). The reference atlas is a `dataset`, linked by a
    `derived_from` relation; `derived_from_#` stays statement-inputs-only.
28. **The cell list** is its own statement — a `label_calculation`, variable "SAW source
    cell identifier", one label per cell — and every per-cell statement (centroid,
    boundary, area, capture spots, UMI count, detected genes) points at it with
    `labels_from`. Anchoring on the centroids was rejected: dissociated cells have none.
30. **`value_id`** — one role-named edge for "my value lives in that document", on
    `subject_statement` and `relation`. Replaces `timed_sequence_manipulation`'s
    `timed_sequence_id` (a rename of a signed edge; team sign-off owed).
31. **`redundant`** replaces T6's `is_cache`, on `data_body` and `subject_calculation`
    only (the only places a cache can exist). Most calculations are not redundant;
    nothing may cite a redundant document as a provenance input.
33. **`label` — a term without a node.** A term has a namespace and an id; a label is
    meaningful only locally. Test: shared or compared across datasets → a term; confined
    to one source or run → a label. `label.value = {name}`.

## E. The pyramid, and the checks

29. **Zoom levels** are further bodies of the one observation, bins 2–32 `redundant`.
    NDI's cloud tiers storage per DOCUMENT, so bin 1 can go to Glacier while the caches
    stay warm; a new zoom is one more body. **Gene totals** are kept as a redundant
    `count_calculation` over [gene]. The chip is an instrument subject; the pipeline a
    `software` entity; the other pyramid fields are the coordinate system, key origins,
    or computable.
34. **DID-matlab checks:** unheld bodies validate today only because
    `canfindonefile` passes any location that is not an existing file; four
    `derived_from_#` misuses (one NDI term_observation breaks against PR #76); the file
    series scope. All on the PR #76 checklists.
35. **Spike-sorter output** targets `label_calculation` (built `7fa543c`).
36. **Edge families:** every repeated edge is a `_#` family carrying `multiple` (built
    `1321501`); every family is numbered from 0 (T14, built `7daa4c0`).
37. **`harmonic_component_calculation` is restored.** Signed 2026-08-08, deleted by #67
    decision 10 on the premise that `_calculation` means "a calculator produced it".
    Rule C decides by provenance: a stimulus response is computed from data in the
    dataset. Restoring it also closes a Bar-2 regression inferred from the ledger (not
    re-measured) for the corpora carrying `stimulus_response_scalar`.

38. **`ngrid` is dropped from `reverse_correlation`** (2026-09-25; revises the #67 chain,
    which kept it from the v1 parent list without a stated reason). On a V_eta composite it
    is a v1 storage block (T6) duplicating what `receptive_field` says about its bodies and
    keys. The v1 `hartley_calc` tombstone now declares `ngrid` directly, so unmigrated
    `hartley_calc` documents still validate. This answers `V_eta_OPEN_WORK.md` row #87's
    objection ("re-pointing would strand hartley_calc"): the block moves to the tombstone
    rather than vanishing.
39. **`ingestion_manifest` drops `epochprobemap`** (2026-09-25, option B; revises the
    2026-08-21 lossless-round-trip addition). A serialized v1 table in a string is not
    V_eta (T6/T14). Its rows have homes or are refused: recording rows become
    `<modality>_observation`s, stimulator rows `term_manipulation`s (#66 increment 3),
    and imaging rows — no home until the image model (#24), and in no corpus held — are
    REFUSED by the migrator, visibly, rather than carried in the string. The stated
    read-back use was never built (no NDI file reads `ingestion_manifest`). The v1
    `epochfiles_ingested` tombstone keeps the field.
40. **`ingestion_manifest.filenavigator_id` → `epoch_file_pattern_id`** (2026-09-25, option
    A). The edge was restored 2026-08-08 under NDI's name, pointing at the v1
    `filenavigator` class; the signed file-navigation decision (2026-08-06) makes that
    class `epoch_file_pattern` with its id preserved, so the edge now names and targets
    the V_eta class, matching `acquisition_system.epoch_file_pattern_id`. Still REQUIRED.
    The v1 `epochfiles_ingested` tombstone keeps `filenavigator_id`.
41. **T15: edges are nouns ending `_id`, and a repeated edge repeats one name** (2026-09-25).
    No `_#` template and no numbered members: repetition is declared (`multiple`), order is
    declared (`ordered`), and the storage key gains a position. Chosen over `_k` numbering
    (option A) and a list-valued edge (option C). The vocabulary table is T15's appendix in
    `V_eta_tenets.md`; the names decided in review include `referent_id` (for `relative_to`),
    `parent_id` (method_parameters lineage), `input_id`/`output_id` (calculations, clock
    alignment), `item_id` (timed_sequence), `key_labels_id`, `entity_id`
    (undirected_relation). BUILT schema-side 2026-09-25 (build section 12.7, 21 edges across
    18 classes); repeated names cannot be stored until DID-matlab's depends_on gains a
    position.
    `control_designation`'s shape is parked for its own discussion.
42. **`image_observation` drops `ontology_table_row_id`** (2026-09-25, audit follow-up). The row
    class retires and decomposes into statements about the same subject the image shows (#53),
    so the link runs through `subject_id`.
43. **The v1 receptive-field chain goes back to its pre-2026-09-21 shape; supersedes
    item 38.** `reverse_correlation` and `hartley_reverse_correlation` are retired v1
    tombstones again, with their v1 fields (#67 had made them empty composites under
    `receptive_field`, so no unmigrated v1 `hartley_calc` document could validate:
    its blocks were undeclared and it lacked a required `receptive_field.value`).
    `hartley_calc` ⊂ [`base`, `hartley_reverse_correlation`] and reaches `ngrid`
    through `reverse_correlation`, as in v1. #67's requirement — confirmed with Steve
    via jess, 2026-09-25 — is one document class per calculator, not the v1 names:
    the Hartley calculator's document is `receptive_field_calculation`, and
    `receptive_field` stands alone.

## F. What is built (schema side), and what is not

**Built:** `label`, `label_calculation`, `position`, `position_observation`,
`position_calculation`, `coordinate_system`, `count_calculation`, `area_calculation`,
`score_calculation`, `term_calculation`, `harmonic_component_calculation`; `keys` +
`complete` + `labels_from` / `cyclic` / `chunk` + `axis_labels_#`; the image value;
`data_body.owner` + file series + identity fields + `redundant`; `relation.method` +
`value_id`; every data type concrete; the eight spatial copies retired, with their
decided targets in `V_eta_migration_targets.json`.

**Not built:** the vocabulary (the term worksheet — axis, direction, origin, assay and
variable terms; registries were unreachable from the review's container); every emitter
change (PR #76 checklists); the per-member hash (a recorded gap).
