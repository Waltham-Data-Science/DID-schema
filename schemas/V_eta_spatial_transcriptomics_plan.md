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
44. **`angle`'s canonical unit is DEGREES, everywhere** (2026-09-25). Amends the data_body
    plan's §2 ("ANGLES ARE RADIANS"), whose premise -- strict SI slot names -- the schema no
    longer holds; V_eta is practical SI. **`visual_grating` is rebuilt with typed cells:**
    angle, phase, size and position are `angle` cells; spatial frequency a
    `spatial_frequency` cell; temporal frequency a `frequency` cell; duration a `time` cell;
    contrast a `score` cell whose `scale` names the definition. `source_geometry` folds into
    the cells' source fields; `pixels_per_degree` stays. Every value keeps its canonical
    plus the original value and unit (T14).
45. **New type `spatial_frequency`** (canonical cycles per degree of visual angle), draft,
    composite only. Not `frequency`, which is per unit time (hertz) and keeps its name:
    unqualified "frequency" means per time across sampling, oscillation and drift rates.
46. **`score` gains `source_value` + `source_unit`**, like every other quantity cell
    (contrast recorded as 50 % -> value 0.5, source_value 50, source_unit "%"). A separate
    `ratio` type was rejected: `score`'s named scale also records WHICH contrast definition.
47. **`angular_velocity`'s canonical unit is degrees per second** (2026-09-25), following
    `angle` (item 44).
48. **`neuron_extracellular` migrates to calculations** (2026-09-25). A sorted unit's
    statements are computed from the spike sort, so under the provenance rule each is a
    calculation with `input_id` -> the sorting output: `cluster_index` and `quality_label`
    -> `label_calculation` (a cluster index is a nominal label, not a count; supersedes
    the migrator's `count_assertion` stopgap), `quality_number` -> `score_calculation`,
    `mean_waveform` -> `voltage_calculation` (new leaf). The unit subject and its
    `derived_from` relation are unchanged.
49. **`fitcurve` is PARKED.** It is a calculation too, but its migrator drops the fit
    (only the SSE survives as a `score_observation`). The right target is a standalone
    `model_fit` data type (equation, named parameters and variables, constraints,
    goodness, sampled fit) that the tuning family's `model_fit[]` entry would share; that
    design is its own item. `polynomial` stays separate (a conversion rule, not a fit).
50. **Leaves exist only when needed** (2026-09-25). Every data_type stays. An
    `_observation` / `_manipulation` / `_assertion` / `_calculation` leaf is made by combining
    a direction with a data_type once something needs it: a migrator or second pass writes
    it, or a decision names it as a target. The rule is written into T3. **51 leaves are
    deleted**, measured over 1,232 `.m` files (DID-matlab + NDI-matlab `src`, V_eta
    branches, comments stripped, plus `jQuantityLeaf`'s runtime-built names) and
    `V_eta_migration_targets.json`: 48 had no writer and no decided use; three were written
    only by dead or superseded code (`angle_observation` by `jDecomposeScalars`, which
    nothing calls; `visual_grating_manipulation` by the old NDI assembler `local.m` no
    longer calls; `count_assertion`, replaced by item 48). **`image_manipulation` is
    among them**, reversing that part of the 2026-08-08 image plan: an image shown to the
    animal is an item of a `timed_sequence_manipulation` (stimulus model, signed the same
    day). `position_observation` stays: item 4 decided probe sites are one, and it is now
    `probe_geometry`'s decided target. The full list is `_DELETE_UNUSED_LEAVES` in
    `tools/build_v_eta.py`.
51. **`image` and `image_observation` retire** (2026-09-25). After item 16 the V_eta `image`
    data type held only `{ pixels, keys, complete }`: the generic keyed array T3 forbids
    (`array` was removed for exactly this), under a name that states the form rather than
    the quantity (T13), and with no quantity or structure of its own (T12). A raster now
    goes by what its pixels measure, keyed [y, x, (channel)]: brightness or fluorescence
    -> `intensity_observation`, a mask or label map -> `label_calculation`, a map of
    ontology terms -> `term_observation`, depth -> `length_observation`, raw values of
    unknown meaning -> a bare `sampled_body` (T3). A picture shown as a stimulus is a
    standalone document of that data type, an item of a `timed_sequence_manipulation`.
    This reverses the 2026-08-08 image plan. **The name `image` goes back to the did_v1
    class** (NDI `data/image.json`), restated as a retired tombstone, which also removes
    the name collision `migrators_j/image.m` refuses around. Decided targets are recorded
    for v1 `image`, `imageStack`, `ontologyImage`, `daqreader_image_epochdata_ingested`
    and `element`'s imaging arm. `ontologyImage` -> `intensity_observation` (its pixels are an
    ordinary numeric image; its ontology nodes describe the whole image and stay a
    `term_observation`, per NDI `imageDocMaker.m`).
52. **`logical_observation` retires** (2026-09-25). `valid_interval`, its only user, moved to
    `time_observation` (TEAM-SIGN-OFF [logical_observation amendment 1], 2026-08-18), which
    left the leaf's retire-or-hold question open. Under item 50's rule it goes: its only
    writer is `resolveValidIntervals.m`'s dormant path. `logical` stays, like every data type.
    The same check found `valid_interval`'s migration-targets note claiming the pass was
    RE-ARMED on 2026-08-18. It was not (the signed amendment says "IS NOT RE-ARMED YET", and
    the pass is still dormant at DID-matlab `775353d`); the note is corrected, and the
    rewrite to the signed shape is on the PR #76 DID-matlab checklist.
53. **The run environment is two pieces of software** (2026-09-25). The inline
    `subject_interaction.execution_environment` block is dropped: under the provenance rule
    every software-produced statement is a calculation, and every calculation already carried
    the environment as a required entity (#67), which `jCalculation.m` filled from the same
    value. That entity (`runtime_environment`, briefly renamed `execution_environment`) is
    then **deleted and split**: the interpreter (MATLAB R2023b) and the operating system
    (macOS 14.5) are each a name + version, which is `software`, so a calculation carries
    `interpreter_id` and `operating_system_id` -> `software`, both required, beside the
    calculator's own `software_id` (T12: one class for software; T15: the edge name gives the
    role). They sit on the calculation, so R1's "the OS this run used, not the OS the software
    supports" holds. `software` gains no ontology node: its inherited `global_identifier`
    already carries an RRID, DOI, SWHID or Wikidata id. Before the DID-matlab change lands, a
    corpus run must confirm every v1 `app` fills os and interpreter (a required edge
    quarantines a calculation that left them empty).
54. **Names live on the classes that have one; `base.name` is did_v1-only** (2026-09-25).
    A name is a property of some things, not of every document: observations, bodies and
    relations have none, and V_eta's `base.name` filled up with `migrated_*` placeholders
    (which several passes also use as hidden type tags). So V_eta documents stop writing
    `base.name`, and each class with a name declares `name`, V_eta's one word for what a
    thing is called: `software`, `strain`, `method_parameters` (already), `acquisition_system`
    (new: NDI finds a rig by its name), `dataset` and `organization` (was `full_name`; each
    keeps `short_name`), `publication` and `funding` (was `title`), `web_resource` (was
    `label`); `person` keeps its given/family/alternate names. **`local_identifier` is a key,
    not a name**: it stays required on `subject`, `session` and `epoch`, where the code keys
    on it (`epochIndex.m`, `resolveLawnPlateSubjects.m`, `session.m`), and comes off the
    eight other entities, none of which has a writer for it except `software`, whose
    `name@version` is a derived merge key. Subject, session and epoch get no `name` until
    something needs one. **`base.name` stays declared only for v1 documents that pass
    through** (about 30 classes; the validator rejects undeclared fields); V_eta emitters
    never write it, and it is deleted when the last passthrough class is converted.
    **Cardinality belongs to repeated edges** (same day): `min_count` / `max_count` appear
    only beside `multiple` (or a did_v1 `name_#` family). On a single edge they restated
    `mustBeNonEmpty`; they are removed from the three item-53 edges and the build fails if
    one returns.
55. **`epoch.instrument_id` is dropped** (2026-09-25). Current NDI mints a unique epoch id
    per file navigator (`+file/navigator.m:253-279`), but older data names epochs after
    their directory (`t00003`), shared by every rig recording it, and `epochMint` makes
    one `epoch` per (session, epoch name), so an epoch can have more than one rig. The
    rig stays where it is always correct, on each recording statement, and nothing ever
    wrote this edge. This reverses that part of the epoch sign-off (2026-08-08, amended
    2026-08-10).
56. **Channel wiring is one shape: an `acquisition_channels` document** (2026-09-25, 6b
    option B). A rig plus its channel groups was stored inline on every recording statement
    (`subject_interaction.channels` + `acquisition_system_id`) and, for sync, as an
    `acquisition_channels` document. A statement now points at a shared `acquisition_channels`
    document through `acquisition_channels_id` (the edge name `clock_alignment_configuration`
    already uses); the inline field and edge go. One document per distinct (rig, channels),
    so a wiring that does not change is stored once, not once per epoch. **An unresolved
    rig is created, not dropped:** the sync writer used to keep a device name it could not
    resolve on `base.name`, which item 54 retires. Now a batch pass resolves every device
    name by (session, name), and when no `acquisition_system` has that name it mints a
    minimal one whose `name` is the device name (every other rig edge is optional). So
    `acquisition_channels.acquisition_system_id` is **decided required**, and a rig's name
    lives only on `acquisition_system.name`. The schema keeps the edge optional until the
    DID-matlab minting pass lands: nothing fills it today, and required-edge enforcement
    (#37, on by default) would quarantine every document the sync fold emits.
57. **Small audit decisions** (2026-09-25).
    - `area` stays in square meters: it follows `length` (meters), as velocity and
      acceleration do; `volume` in liters is the deliberate practical exception (audit 8).
    - `receptive_field.value` drops `storage_mode` and `method`: they repeated the
      statement's own `storage_mode` and `subject_interaction.method` (audit 18).
    - `ngrid` is neither deleted nor folded now: the restored v1 `hartley_calc` chain and
      `ontologyImage` still inherit from it, so it goes with the last passthrough (audit 20).
    - `tuning_curve.value.response_units` (free text) becomes `response_unit`, an
      `ontology_term` like every other unit, unbound until the unit vocabulary is chosen
      (audit 16, item 24).
    - The `session_id` edges on `epoch` and `clock_alignment_policy` are dropped: every
      document names its session in `base.session_id`, and session documents are 1:1 with
      the distinct `base.session_id` values (#51, all six corpora). Reverses that part of the
      epoch sign-off (audit 13).
    - Tabled: `harmonic_component`'s control shape (audit 17) and `clock_alignment`'s
      inheritance (audit 19).

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
