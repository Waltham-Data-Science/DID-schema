# Spatial transcriptomics (#73) -- running record, NOT in schemas/ (Rule 1)
Decided by jess in the #73 review session, 2026-09-23, unless marked open.

## Agreed
1. Transcript counts = count_observation of the tissue section, axes [x, y, gene];
   bin1 is the measurement, bin2..bin32 are derived, rebuildable bodies.
2. Cells are an AXIS, not subjects (option b): the segmentation is one statement over a
   `cell` axis; every per-cell fact is another statement over that axis.
3. Observation vs calculation by provenance (BUILT, PR #76): segmentation, per-cell
   measures and labels are calculations.
4. New data_type `position` = coordinates + frame; centroids -> position_calculation;
   probe_geometry sites -> position_observation. (`point` rejected: coordinates are
   lengths in ISQ, but a position needs a frame that `length` cannot carry.)
5. Frame = its own shared thing, carrying origin, orientation, per-axis scale to metres
   (or `scale: unknown`). Position values stored in FRAME units; metres computed through
   the frame by one shared resolver (store once, look up -- same reasoning as the
   valid_interval re-derive decision).
6. Frame SCOPE: build acquisition-grid frames (Stereo-seq, image stacks, Haley worm
   video pixels) + device frames (probe_geometry). Design for, don't build, subject-
   landmark (stereotaxic) and atlas (CCF) frames. Visual space stays as RF axes.

7. A FRAME is exactly three things (2026-09-24): (1) ORIGIN -- always on something
   (probe tip, image corner, bregma of an animal, the atlas); (2) the MEANING of each
   coordinate, in order, incl. its positive direction (count = 2-D vs 3-D; handedness
   follows); (3) the STEP SIZE PER COORDINATE -- metres (canonical) or unknown.
   Transforms between frames (registration) are NOT part of a frame; deferred.
   Reset of 2026-09-24: frames are decided WITHOUT reference to array `axes`.

8. STEP SIZE is PER COORDINATE (non-square pixels).
9. FRAME SHAPE (2026-09-24), class `reference_frame`:
     depends_on  relative_to -> <document>   REQUIRED; what the origin is on (reuses the
                                             time model's anchor edge -- same concept)
     origin      ontology_term               which point on it is zero (probe tip, bregma,
                                             image upper-left corner). SAME CONCEPT as the
                                             array axis `origin` (where something's zero sits
                                             relative to something else); a term here only
                                             because a root frame is not measured within
                                             another frame. Doc must say so in one line.
     dimensions[]                            one per dimension, in coordinate order
        axis                ontology_term    the line (image x = NCIT:C44477, AP axis, ...)
        positive_direction  ontology_term    which end is positive ("image right",
                                             "posterior") -- must be one end of `axis`
        spacing             length cell      one unit step; ABSENT = unknown (uncalibrated)
   Names rejected, with reasons: meaning (vague); variable (loaded; a frame is not a
   statement); increases_toward (awkward); direction (T2 "epistemic direction");
   axes (the array structure); zero_point / landmark (a second name for `origin`).
   AMENDED 2026-09-24: `axis` holds AXIS terms (image horizontal axis, AP axis, shank
   axis), NOT NCIT:C44477/C44478 "X-/Y-coordinate" (those name coordinate VALUES; they
   map to how v1 labels the numbers, and a migrator uses them to recognise image x/y).
   Axis terms to be found or minted -- none proposed (NCIT/OLS unreachable here).
   A reference frame is ALWAYS REQUIRED: position.coordinate_system_id REQUIRED; an image
   gets its own frame whose relative_to points at the image. No point-at-the-image case.
   CLASS NAME: `coordinate_system` (not reference_frame / frame_reference: a frame is the
   space things are measured in -- time's `clock` -- not an anchored "when/where").
   `spatial_reference` is RESERVED for a future "where this statement applies" document
   (the true counterpart of time_reference); nothing needs it yet.
   Direction terms must say WHOSE right (image vs anatomical). Cartesian frames only.
   Position values: coordinates[k] along dimensions[k], in spacing units;
   metres = coordinate x spacing.meters.

10. TIME NAMING FIX (option A, 2026-09-24): `absolute_reference` -> `absolute_time_reference`,
    `relative_reference` -> `relative_time_reference`; root `time_reference` and the
    `time_reference_#` edge unchanged. BUILT on PR #76 as 6bdf2bf (old names acknowledged in coverage.py KNOWN_NON_VETA until DID-matlab renames). Grammar: `<domain>_reference` = an anchored when/where
    document; `file_reference` reads in the same (domain-stated) sense.
    Cost measured: DID-matlab 'relative_reference' 8 files, 'absolute_reference' 2;
    NDI V_eta branch relative_reference 4.
    FINDING: the signed 8->2 time collapse (2026-08-08) is mostly UNBUILT on the migrator
    side -- 'session_relative_reference' still in 23 DID-matlab files + 2 NDI files.

11. BOUNDARIES (2026-09-24): a boundary is a position_calculation over axes [cell, vertex].
    (1) Vertices are CONVERTED TO SECTION COORDINATES at migration (vertex = centroid +
        stored offset; v1 stores them relative to the centroid, contour_reference:
        centroid). One coordinate system per section, not one per cell.
    (2) "Closed loop" = option (b): a new axis-entry field `cyclic: true` ("after the last
        index comes the first"; absent = false). Self-intersection is DOCUMENTED ("may
        self-intersect; render as an outline"), not enforced.
        `polygon` data type (c) REJECTED for now per T12 test 3 (a simple polygon is
        position x cardinality; the only extra fact is closure). TRIGGER TO REVISIT (c):
        polygons with HOLES or MULTIPLE PARTS. v1 has neither: cell contours (one ragged
        ring per cell) and probe_geometry.contour_x/_y (one ring) are both simple.
    Ragged vertex axis (4-24 per cell) -> the sparse/ragged layout item, still open.

12. DOCUMENT-ENUMERATED AXIS (2026-09-24): an axis may take its positions from the ROWS of
    another document, in its order, instead of an inline `labels` list.
      depends_on  axis_labels_# -> <document>        an ordinary DID edge (resolved and
                                                     orphan-checked like any other)
      axes[k]     labels_from: "axis_labels_<n>"     names that edge; XOR with `labels`
    `n` must equal the referenced document's row count. Uses: gene axis -> geneList;
    cell axis (labels, areas, counts, boundaries) -> the segmentation. Datasets are
    comparable exactly when their gene axes point at the same geneList, otherwise a
    geneListMapping is required. A document used via labels_from must carry an
    EXPLICIT index column (NDI already does: genes.tsv gene_index, cells.tsv cell_index).
    Precedent: timed_sequence (distinct items by edge + index array), which differs in
    that its items are separate documents, ours are rows of one document.
13. INDEX ORIGIN (2026-09-24): option (a) -- ONE V_eta-wide rule, 0-BASED, stated once in the
    schema documentation. MATLAB-side migrators convert (+/-1). Applies to labels_from
    rows AND to timed_sequence.value.presentation_order (whose base is undeclared today).
    NOTED, NOT FIXED: timed_sequence declares its edge as `presented_id` (single) though it
    holds several references -- should be `presented_id_#` (same fix control_designation got).

14. BODY DESCRIPTION = A TABLE, NOT AN ARRAY (2026-09-24). Supersedes the `axes`-based
    storage proposals of the same day (arrays list; per-axis storage kinds; stored_with;
    paired) -- none of those is adopted.
      keys[]    what you look a value up by. May carry: variable {node,name}, n, regular,
                origin, spacing, unit, source_unit, labels, labels_from, cyclic.
                NEVER datum_type.
      values[]  the answer columns. Carry: variable {node,name}, datum_type, unit,
                source_unit. NEVER grid fields.
      complete  true = every combination of key values has a row (dense grid; regular keys
                are generated, not stored); false = only listed rows exist (ragged/sparse).
    Byte packing (offsets, header counts, x/y pairs) is an ENCODING named in
    data_body.format, from a short list documented once in the schema (like `gzip`):
    e.g. dense-C, grouped-by-first-key/1 (== NDI contours.bin), ndi-sgep-tile/1 (== NDI
    tile.bin), so NDI's existing files are described unchanged, no rewrite at migration.
    Examples: recording keys[time,channel] values[voltage]; outlines keys[cell,corner]
    values[x,y]; tile keys[x,y,gene] values[count].
    Name chosen: keys + values (jess), knowingly beside the T14 `value` payload slot.
    REVISES the signed data_body axis entry (2026-08-14).
    SCOPE (b), decided 2026-09-24: `axes` -> `keys` in ALL FOUR places (subject_statement,
    image.value, acquisition_epoch, sampled_body). `values` ONLY on sampled_body -- the
    one place with raw bytes and no data type of its own; elsewhere the data type's `value`
    slot (or image.dtype) already types the answer, so a values list would duplicate it.
    OPEN KNOCK-ON: (a) the axis entry's own `values` field (explicit numeric coordinates)
    must be renamed inside keys[] to avoid keys[k].values (LEFT FOR NOW, jess).

15. NO `values` ANYWHERE -- OPTION (A), decided 2026-09-24 (jess). REVISES item 14: its
    `values[]` list and SCOPE (b)'s "values ONLY on sampled_body" are both withdrawn.
    RULE: a body holds exactly ONE kind of value; anything else that looks like a column
    is a KEY.
      - the value's MEANING comes from the data type / statement `variable`;
      - its TYPE is `subject_statement.datum_type`, ONCE (signed data_body decision
        2026-08-14: "extent is per-body, type is per-statement" -- pyraview writes N
        bodies of one type), never repeated on a body;
      - its BYTE PACKING is data_body.format (named encodings, item 14).
    Tested against:
      ephys            keys[time, channel]                        -> voltage
      pyraview level   keys[time, channel, statistic{minimum,maximum}] -> voltage
                       (evidence: NDI origin/main
                        +gui/+app/+pyraview/transformPlotData.m:68,83 -- min/max per
                        bin; so min/max is a labelled key, not a 2nd value column)
      confocal stack   keys[y, x, channel, z]                     -> fluorescence
      gene tile        keys[cell, gene]                           -> count
      cell outlines    keys[cell, vertex(cyclic)]                 -> position (x/y from
                                                                     the coordinate_system)
      ensemble cache   keys[neuron] + grouped-by-first-key/1      -> spike time
    CONDITION / REVISIT TRIGGER: a real dataset with two DIFFERENT measured quantities
    (different unit or type) side by side that cannot be restated as a key. None found --
    NOT evidence none exists (Rule 3). If one appears, ADD `values` back (additive,
    breaks nothing).
    Item 14's knock-on (a) (renaming the key's explicit-coordinates `values` field) is
    now only about avoiding confusion with the T14 `value` slot, not with a sibling list.

16. IMAGE DATA TYPE, decided 2026-09-24 (jess). REVISES R6 decision 4
    (V_eta_image_model_plan.md).
      axes         -> keys (item 14 scope)
      channels     DROPPED -- a channel key's `labels` ({node,name} terms, T8) say it
      color_model  DROPPED -- read off the channel key: no channel key / n=1 = grayscale;
                   labels red/green/blue = rgb; otherwise multichannel. Kept, it could
                   disagree with the key (rgb with labels GCaMP, tdTomato).
      dtype        DROPPED -- duplicates subject_statement.datum_type (the later, signed
                   home). R6's reason (not recoverable from an inline matrix) still holds;
                   it is now answered by datum_type.
      pixels       STAYS (inline payload).
    Resulting image.value: { keys[], complete, pixels (inline only) }.
    WORDING FIX NEEDED: subject_statement.datum_type says it is absent "for an inline
    composite with no numeric payload" -- say explicitly that inline pixels ARE a numeric
    payload, so datum_type is required for an inline image.

17. MANY FILES PER BODY (chunking), 2026-09-24 (jess).
    1A: the split is described ON THE KEYS: `chunk` = positions per chunk along that key
        (name under discussion; standard zarr/HDF5 term; DID already says "chunk grid").
        Chunk k numbered row-major over the chunk grid, 0-based; absent file = empty chunk;
        a key with no `chunk` is not split.
    2:  members named body_data_k.
    FILE NUMBERING: (ii) -- ZERO-BASED, body_data_0 is chunk 0. This DIVERGES from
        DID-matlab's file series today (addFileSeries: "INDICES ARE ONE-BASED ... NAME_1";
        manifest itself is zero-based). -> FOLLOW-UP in DID-matlab (+ NDI makePyramid /
        tileFileName / spatialGeneExpressionTiles.md, demoNDISeries*). NOT the Dab
        `_seg.nbf_#` files: those are plain file_list NAME_#, a different mechanism.
    P1, decided 2026-09-24 (jess): EVERY body is a DID file series. data_body declares
        `body_data` as a series (V_eta `file` entries gain a `series` flag; builder emits
        files.file_series). An unchunked body is a 1-chunk grid: member body_data_0.
        ONE rule: chunk k (row-major, 0-based) == member body_data_k; absent member ==
        empty chunk. Cost: ~65-byte manifest per body. (P2, two declared files
        body_data + body_chunk, rejected.) Constraint that forced the choice: series-ness
        is declared per CLASS (NDI demoNDISeries.json files.file_series), and DID refuses
        colliding plain/series declarations (DID-matlab 974991a, four refusals).
    FOLLOW-UPS (other repos, for the PR #76 list): DID-matlab addFileSeries zero-based
        members; every body-writing migrator writes a series; NDI makePyramid/tileFileName
        zero-based; v1 tile.bin_N re-keyed to body_data_{N - tile_index_origin} at
        migration (bytes untouched).
    ACCEPTED 2026-09-24 (jess): name `chunk` kept; ONE BODY PER ARRAY (new body where the
        array changes, series member where only the bytes split); per-member hash
        RECORDED AS A GAP, nothing designed (manifest `flags` leaves room).
    (was OPEN) per-member content_hash (nothing stores one; manifest has uid +
        optional source name only); one-body-per-array vs one-doc-per-file.
    EVIDENCE: DID-matlab docs/notes/file_series_manifest.md -- series exists because "a
        tiled image pyramid level is ~28,000 files, and one file_info struct per member is
        ~8-11 MB of JSON in a document blob that is returned whole on every read"
        (VH-Lab/DID-matlab#173). No V_eta schema declares file_series yet.

18. NOTHING CARRIED FORWARD (2026-09-24, jess): none of the 8 v1 classes
    (spatialGeneExpressionPyramid/Tiles/Cells, cellTypeLabels, geneList, geneListMapping,
    fileReference, geneExpression) survives as a V_eta class. All are MIGRATED into the
    V_eta design. The copied classes built by #64/71298fd (spatial_gene_expression_*,
    cell_type_labels, gene_list, gene_list_mapping, file_reference, gene_expression) are
    therefore v1 tombstones to be replaced, and their ledger rung-3 `yes` (target = itself)
    is NOT Bar-2.

19. DATA TYPES CONCRETE + CONTENT-NOT-CLAIM (2026-09-24, jess accepted the reasoning; adopted
    as the prerequisite of item 21). Every data_type composite becomes instantiable (today
    40 of 42 are abstract; only timed_sequence + visual_grating are concrete), because T6's
    `storage_mode: reference` needs a standalone value document to point at -- otherwise
    `reference` is impossible for 40 data types. RULE: a standalone data_type document is
    CONTENT, NOT A CLAIM; it says nothing until a statement references it; the statement
    carries subject + stance. Motivating case (jess): a voltage-clamp command waveform
    stored once and referenced by many voltage manipulations.
20. BODY OWNER WIDENED (same basis as 19): data_body.statement may point at a statement OR a
    standalone data_type document (a large shared value -- image, waveform, term list --
    needs a body). must_refer is declarative, so this is a documentation change.
21. geneList -> a STANDALONE `term` DOCUMENT (2026-09-24, jess). Not term_assertion: no
    subject fits (not the animal -- NDI geneList.md "a property of a reference, not of any
    one animal"; not the annotation -- a published reference resource is a T9 ENTITY, not a
    T1/T5 subject). The list is the LABELS of the count statement's gene key, i.e. part of
    that statement's value stored by reference (T6). T12 test 3: a list of terms is still
    `term` (length-N value). value_set is not the home (dropped: schema-level registry, not
    dataset data). Shape: keys [index, n], complete; body = index/node/name table;
    base.name = label. n_genes -> key n; gene_id_namespace -> the node CURIE prefix;
    gene_name_completeness / n_duplicate_gene_names DROPPED (computable; the "join on node,
    never name" warning goes into documentation). Provenance: see item 22.

22. PROVENANCE EDGE (2026-09-24, jess): option A -- a `directed_relation` with relation
    `derived_from`, `child` WIDENED to accept standalone data documents (today child/parent
    -> entity). gene list -derived_from-> annotation; annotation -derived_from-> assembly.
    Rejected: B (a source_id edge on every data_type; T4 says relationships are documents),
    C (name only; unqueryable).
    ENTITY CLASS, decided 2026-09-24 (jess): the annotation and the assembly are `dataset`s
    (versioned, citable bodies of data: version/full_name/release_date/how_to_cite fit).
    NOT web_resource: per signed D-F (V_eta_nonsubject_cohesiveness_plan.md) a web_resource
    is WHERE a thing lives (`dataset -stored_at-> web_resource`, `documented_by`), never
    the thing. A URL, if known, is a web_resource via `stored_at`. "Ours" vs "reference"
    is read off the graph (D-F: `session -part_of-> dataset` = ours; reached only by
    `derived_from` = reference) -- no new field. Annotation vs assembly told apart by the
    relation (annotation -derived_from-> assembly) + full_name; no entity-kind mechanism.
    Same home later for atlases (CCF). Migration: v1 has only strings (genome_assembly,
    annotation_source) -- entities minted with a name, no identifier.

23. geneList leftover (2026-09-24): `gene_symbol_namespace` DROPPED -- the symbols come from
    the annotation dataset the list is derived_from (item 22); the join key is `node`,
    whose CURIE prefix names its own namespace. (Proposed; jess did not object.)

24. geneListMapping (2026-09-24, jess). An earlier draft (a relation with the pair table as
    its body; undirected for symmetric) was REJECTED on jess's two questions:
      - undirected_relation's `entities` are unordered, but the pair table has a first and
        second list; and "list A orthologous to list B" is false -- GENES are orthologous,
        lists "map to" each other;
      - a relation has no variable / data type, so the score had no defined meaning,
        breaking item 15.
    DECIDED SHAPE:
      pairs  = a standalone `score` document (content, item 19), keys [gene of A
               (labels_from axis_labels_1), gene of B (labels_from axis_labels_2)],
               complete false, value.scale names the rubric (e.g. orthology confidence).
               No score column -> a standalone `logical` (true per listed pair).
               Body = NDI mapping.tsv UNCHANGED (TSV text, header row naming the key/value
               columns) -- no new byte-layout name needed.
      claim  = a `directed_relation`: child = list A (map from), parent = list B (map to;
               parent doc already reads "whole/group/source/target"), relation term
               "orthologous gene mapping" | "gene alias mapping" (find or mint),
               method = tool + version, plus a NEW edge to the pairs document
               (`value_id`, name open) -- T6 value-by-reference applied to a relation.
      symmetric -> a property of the mapping type (still one direction on paper).
      n_pairs, n_genes_mapped_a/_b, has_score DROPPED (computable).
    ALSO DECIDED:
      - `method` MOVES UP from directed_relation to the abstract `relation` (optional);
        it was on directed only because it absorbed the retired `derivation` class's
        derivation_method (creation events); nothing undirected needed one before.
      - data_body's owner edge `statement` RENAMED `owner` (owner may now be a statement or
        a standalone data document).
      - non-symmetric mappings need no separate class (directed already).
    OPEN: the two relation terms; the edge name `value_id`.

25. fileReference -> option A (2026-09-24, jess): an external file NOT held in the database
    is an UNHELD BODY of the statement whose value it stores -- a second body of that
    statement, file recorded by location with ingest 0 (DID add_file: "a reference rather
    than bytes to take"). The .gef = an opaque_body of the count_observation (format
    "Stereo-seq GEF"); the .h5ad = an unheld body of the segmentation calculation.
    Basis: T6 (every carrier incl. generic_file phases into bodies); multiple bodies per
    statement already signed (pyraview); generic_file already folded to opaque_body.
    data_body GAINS `hash_algorithm` (fixes the existing gap: content_hash "the algorithm
    is not declared") and `size_bytes`. originalPath -> the file's recorded location (a
    hint). source_file_id edges dissolve (the body's owner edge carries the link).
    Rejected B: a new external-file entity + derived_from (recreates the generic_file vs
    body split V_eta removed).
    FILE DATES KEPT (2026-09-24, jess): dateCreated/dateUpdated (v1 datenum numbers) become
    optional data_body fields `file_created` / `file_modified`, typed `timestamp` (instants,
    not dates), migrator converts datenum -> ISO 8601. Named file_* so they cannot be
    confused with the document's own base.datestamp. Apply to every body, held or not.
    VERIFY BEFORE BUILD (DID-matlab): how validation treats a non-ingested LOCAL path that
    no longer exists -- PR #182 made missing required files an error ("Some required files
    are missing", database.m:2142); a URL location is exempt from ingestion, a local one
    is unconfirmed.

26. geneExpression DISSOLVES (2026-09-24, jess): no class, no fields.
      assay        -> the observation's `method` term (Stereo-seq, Visium, 10x ...) [T2/T7]
      count_units  -> the `variable` ("UMI count" vs "read count") [T12 test 1: different
                      things counted, not different units]
      count_type   raw -> nothing (it is what a count_observation is);
                   normalized/log-normalized -> a DIFFERENT statement: a score_calculation
                   (variable "normalized expression", score.scale names the transform, e.g.
                   "log1p counts per 10,000", method = the normalization, derived_from the
                   raw count_observation) [rule C]. A raw-vs-normalized mix-up becomes
                   impossible by class.
    NDI's writer always sets count_type 'raw', count_units 'UMI' (+gene/makePyramid.m:220).
    TERMS TO FIND OR MINT: assay terms; variables UMI count / read count / normalized
    expression.

27. cellTypeLabels (2026-09-24, jess). Each labeling is its own statement over the cell key
    (several competing labelings coexist, per NDI makeCellTypeLabels.m).
    SUPERVISED CALL -> `term_calculation` about the tissue section: variable "cell type"
      (or "cell subclass" where taxonomy_level matters and the terms don't imply it),
      keys [cell (labels_from axis_labels_1 -> the segmentation)], complete false
      (UNLABELED cells have no row -- replaces n_unlabeled), method = assignment_method,
      derived_from_# -> the count_observation. Values are ontology terms: term.value is
      ALREADY bound strength REQUIRED, source ontology (term.json) -- atlas types with no CL
      term use the atlas's published ids or a MINTED term (jess: node required; mint when
      missing). My "preferred binding" suggestion was WRONG and is withdrawn.
    UNSUPERVISED CLUSTERING -> NOT a term, NOT a count: a sparse `logical_calculation`
      (cluster MEMBERSHIP) over keys [cell (labels_from segmentation), cluster (n = k, NO
      labels -- positions only)], value true per member. Rejected: count ("cluster 3" is
      not three of anything); term (term.value must be an ontology term, and minting
      per-run, renumbered-on-rerun labels would pollute a shared vocabulary). A cluster
      cannot be mistaken for a cell type because it has no term -- NDI's is_unsupervised
      protection, carried structurally. Naming a cluster later = a NEW term_calculation.
      New leaf `logical_calculation` = direction x data type (T3).
      REVISIT (not changed now): the spike_clusters -> count fold has the same flaw.
    REFERENCE ATLAS (reference_document_id) -> the atlas is a `dataset` entity (as item 22),
      linked by a `directed_relation` derived_from, child = the labeling statement, parent =
      the atlas: option (b). REQUIRES widening directed_relation.child to statements (item
      22 widened it for standalone data only). Rejected (a): letting derived_from_# point at
      entities -- it is documented "never an entity" (predates this review, 687613c), and
      derived_from_# is declared on calculations only, so OBSERVATIONS with external
      references (the counts used the genome annotation) would need the relation route
      anyway: (a) would give two mechanisms for one fact. Rule: derived_from_# = in-dataset
      statement inputs (keeps rule C readable off the document); any external reference,
      from any document, = a directed_relation.
    FIELDS: label -> base.name; label_name (source column) -> body `description`;
      n_cells/n_categories/n_unlabeled DROPPED (computable / absence); is_unsupervised ->
      the two shapes above; cells_document_id -> labels_from.

28. THE CELL LIST (spatialGeneExpressionCells), 2026-09-24 (jess): option B -- its own
    statement, a `logical_calculation` about the tissue section, variable "cell detected",
    method = the segmentation (SAW CellBin: NUCLEUS segmentation + dilation -- say so),
    derived_from_# -> stain image observation + count_observation, keys [cell, n = 80369,
    key `values` = source cell_id (traceability; the key-entry field whose rename is
    knock-on (a))], complete true, value true per cell. EVERY other per-cell statement --
    centroids included -- points at it via labels_from.
    Rejected A (centroid statement as the anchor): (1) dissociated cells (NDI geneList.md
    anticipates dissociated RNA-seq) have NO centroid, so the anchor would vary by dataset;
    (2) it ties cell identity to one measurement -- recomputing centroids would strand every
    labels_from. Rejected C (no anchor): "same cells" would be convention, not stated.
    cells.tsv DECOMPOSES, one statement per column, all calculations about the section over
    [cell]:  x,y -> position_calculation "cell centroid"; contours.bin ->
    position_calculation "cell boundary" [cell, vertex cyclic] (item 11), body format
    grouped-by-first-key/1; area -> area_calculation; dnb_count -> count_calculation
    "capture spots in cell"; total_counts -> count_calculation "UMI count";
    n_genes -> count_calculation "detected gene count".
    FIELDS: segmentation_method -> method; segmentation_dilation -> method_parameters;
    coordinate_units -> the coordinate_system; contour_reference -> gone (converted,
    item 11); contours_present -> presence of the boundary statement; n_cells -> key n;
    n_vertices_per_cell / data_type_* / contour_format_version -> body format;
    label -> base.name.
    BONUS: counts, centroids and boundaries share ONE coordinate_system document, so NDI's
    documented silent origin-displacement bug (spatialGeneExpressionCells.md, "The
    coordinate rule") cannot occur.

29. PYRAMID LEFTOVERS + ZOOM LEVELS + GENE TOTALS (2026-09-24, jess).
    ZOOM LEVELS: bin 1 = the count_observation's source body (authoritative, no marker);
      bins 2..32 = further bodies of the SAME observation, each its own body document
      (one body per array; per-level spacing on each body's keys, as pyraview), marked
      `is_cache: true` (T6: regenerable, no authority, safe to drop and rebuild).
      NEW FIELD: `is_cache` -- T6 requires it, NO schema declares it today
      (grep '"is_cache"' schemas/V_eta -> 0).
      STORAGE TIERS WORK PER DOCUMENT: NDI ndi.cloud.api.files.setFileTier "copies every
      file the given documents reference to TARGETTIER" (STANDARD | STANDARD_IA |
      GLACIER_IR | GLACIER | DEEP_ARCHIVE). So bin 1 can go GLACIER while caches stay
      STANDARD -- possible only because each level is its own body document. Natural policy:
      source cold, caches warm. Trade-off: rebuilding a cache from a cold bin 1 waits for a
      restore.
      MORE ZOOMS LATER: append a new body document pointing at the same observation
      (data_body owner doc: "a stream appends more bodies without rewriting the anchor");
      nothing else changes. Dropping a level is equally local.
    GENE TOTALS (gene_totals.tsv) KEPT as a CACHED `count_calculation` (jess overruled my
      "drop"): about the tissue section, variable "UMI count" (whole section), keys [gene
      (labels_from the gene list)], derived_from_# -> the count_observation, is_cache true.
      Written by NDI makePyramid.m:227-229 ("Summing per-gene totals"); no reader found on
      NDI main, so the RECORDED WARRANT (T6 cache test 4) is jess's: per-gene abundance
      without reading -- or restoring from Glacier -- the full bin-1 grid.
      => `is_cache` must be declarable on a STATEMENT as well as a body. PROPOSED placement:
      on `data` (common parent of statements and bodies) -- OPEN, confirm at build.
    PYRAMID FIELDS: chip_serial -> an instrument subject (the capture chip; local_identifier
      = serial) via instrument_id [T7]; pipeline_version -> a `software` entity (SAW 7.1.2)
      via software_id; base_pixel_size_x/_y + pixel_size_units -> coordinate_system spacing;
      origin_x/_y -> the y/x keys' `origin`; origin_corner -> the coordinate_system's
      positive_direction terms; byte_order -> body format; label -> base.name;
      extent_x/_y, bin_sizes, tile_rows/_columns, index_order DROPPED (computable / fixed
      by the chunk rule, item 17).

30. `value_id` (2026-09-24, jess): ONE generic, role-named edge for "my value lives in that
    document", declared ONCE per parent class -- on `subject_statement` and on `relation`.
    Replaces the placeholder in item 24. Reasons: every statement edge is named by ROLE
    (subject_id, instrument_id -> subject, axis_labels_#), T7; with item 19 reference mode
    applies to every leaf, so type-named edges would be ~80 separate declarations;
    one checkable rule: storage_mode reference <=> value_id present; the target's class
    already says its type.
    RENAME (signed stimulus model -> NEEDS TEAM SIGN-OFF): timed_sequence_manipulation.
    timed_sequence_id ("For storage_mode:reference ... the shared timed_sequence body")
    -> value_id. Writers: NDI (V_eta branch) +migrate/+internal/
    stimulusPresentationToTimedSequence.m, +migrate/local.m, test
    TestStimulusPresentationTimedSequenceMultiSubject.m.
    NOT renamed: control_designation.timed_sequence_id ("The presentation whose stimuli
    these controls annotate") -- a different role, not a statement; written by DID-matlab
    control_stimulus_ids.m.

31. `redundant` -- replaces T6's `is_cache` (2026-09-24, jess). Name: "cache" connotes
    transient/possibly-stale and collides with NDI's in-memory ndi.cache (cleared by
    clearAllCaches); `redundant` names T6's test ("adds no information the source lacks").
    NO `is_` prefix (see the T13 rule, BUILT 8db2c1b). PLACEMENT: on `data_body` and
    `subject_calculation` ONLY -- the only places a cache can exist (an observation's source
    is outside the dataset; assertions/manipulations/standalone content are not derived).
    A calculation is NOT redundant by default: redundant = the narrow deterministic,
    lossless, choice-free subset (zoom levels, gene totals); clusterings, label transfers,
    fits stay authoritative. RULE: nothing may cite a redundant document as a provenance
    input (derived_from_# points at the source, never at a redundant copy). T6's text uses
    "cache" throughout -- the tenet wording needs amending when this is built.
    Item 29's `is_cache` references read as `redundant`.

32. KEY `values` KEEPS ITS NAME (2026-09-24, jess): knock-on (a) of item 14 is CLOSED with no
    rename. The clash that motivated it was the body `values[]` column list, removed by
    item 15; the key sits in the subject_statement block and the payload `value` in the
    data-type block, never side by side. "The contrast values tested" is the domain
    phrasing. (`coordinates` considered and withdrawn.) Cell source IDs do NOT go here
    (see 33) -- a source id names a position, it does not place it.

33. NEW DATA TYPE `label` (2026-09-24, jess). RULE: a TERM is anything with a namespace and
    an id (CL:..., UBERON:..., ENSEMBL:... -- the gene list STAYS `term`, item 21 stands).
    Anything meaningful only LOCALLY (a source id, a cluster number, a condition name) is a
    `label`: a term without a node.
        term.value  = { node, name }
        label.value = { name }          name: string, REQUIRED (a string even when it looks
                                        numeric: leading zeros, >2^53 ids)
    Scope = the document it appears in; whose labels they are is said by the variable.
    BOUNDARY TEST for a categorical VALUE: meant to be shared/compared across datasets ->
    a term (mint one if none exists, per jess's node-required rule); confined to one source
    or run -> a label. "L2/3 IT CTX" from a published atlas = term; "cluster 3 of this
    Leiden run" = label.
    Key `labels` entries may be terms OR labels.
    Name chosen over local_label / category / tag. The v1 `label` field (-> base.name) is
    going away, so the word means one thing.
    CONSEQUENCES:
      item 28 REVISED: the cell-list anchor is a `label_calculation`, variable "SAW source
        cell identifier", keys [cell, n] (plain positions), value per cell = the source id
        (was: logical "cell detected", all true, ids stuffed into the key's values).
        Everything else still labels_from it.
      item 27 REVISED: an unsupervised clustering is a `label_calculation`, variable
        "cluster assignment", one label per cell (cell 0 -> "3"); complete false for
        unassigned cells. Replaces the sparse logical membership over [cell, cluster].
        NDI's is_unsupervised protection holds structurally: a cell-type call needs a TERM,
        a cluster is a LABEL. Membership (logical) only if a method assigns several clusters
        per cell (soft clustering); Leiden does not.
      The spike_clusters -> count revisit (item 27) now points at label too.

34. DID-MATLAB CHECKS (2026-09-24), DID-matlab @ 47cf8ba (claude/v-eta-migration-plan-35jj1z),
    NDI V_eta branch HEAD + origin/main. FINDINGS, not decisions.
    (1) UNHELD BODIES (item 25) -- they VALIDATE today, but by a fail-open, not by design.
        Legacy did.database.checkfiles step 3 calls canfindonefile (database.m:2253): any
        location that is NOT an existing local file sets found=true (the else branch is
        unconditional), so a dead local path passes, same as a URL. add_docs copies only
        when location.ingest is true (sqlitedb.m ~545), so ingest 0 copies nothing.
        did2 (the migration writer) checks file NAMES only (validate/fileList.m), never
        existence. RISK: the comment intends "not a local file", the code says "not an
        existing file" -- if DID tightens that, dead local paths on unheld bodies fail.
        => unheld bodies should NOT rely on it: need an explicit "not held" marker DID
        honours (DID-matlab change), or record the location as a non-'file' type.
    (2) derived_from_# TARGETS -- the "statement inputs only" rule is broken in 5 places:
        - +migrators_j/hartley_calc.m:598 -- derived_from_1 on a BODY (the windowed spike
          times), pointing at the neuron SUBJECT (an entity). Bodies do not declare the edge.
        - +migrators_j/private/jCalculation.m:124 -- derived_from_1 -> the v1
          stimulus_tuningcurve / stimulus_response_scalar / stimulus_response id; those
          pass through as v1 tombstones, not statement leaves.
        - +migrators_j/control_stimulus_ids.m:123 -- control_designation (subclass of base,
          not a calculation) carries derived_from_1 -> the presentation id.
        - NDI +migrate/+internal/ontologyLabelSubjects.m:284 -- a term_OBSERVATION with
          derived_from_1. #73 (built, dfc5306) removed derived_from_# from observations,
          so this output no longer validates; by rule C it should be a term_calculation.
        - (jComputedScalar.m: dead code, already on the PR #76 list.)
        directed_relation CHILD already non-entity: NDI ensembleMembership.m:558 mints
        `derived_from` with child = the ensemble CACHE carrier, parent = neuron -- a live
        precedent for item 27's widening. (jTuningFold.m does it too but has no callers.)
    (3) ZERO-BASED FILE SERIES (item 17) -- scope measured:
        DID-matlab: document.m (addFileSeries rejects index<1 at :1034; ONE-BASED
        documented at :803, :960, :991, :1066), database.m (:769-871 member lookup,
        mustBePositive at :798), +file/readSeriesManifest.m, readSeriesManifestUid.m,
        writeSeriesManifest.m (slot i one-based in MATLAB; the ON-DISK manifest is already
        zero-based -- format unchanged), sqlitedb.m member naming; tests TestSeriesMemberFetch,
        TestDocumentFileSeries, TestFileSeriesRoundTrip, TestCustomFileHandlerContext.
        NDI origin/main: +database/+internal/list_binary_files.m, +gene/makePyramid.m:403-407,
        tileFileName.m, tileIndexFromName.m, tileIndexOrigin.m, ~11 tests.
        EXISTING DATA IS ALREADY MIXED: NDI tileFileName.m -- "Pyramids built before the
        one-based convention was honoured name their first tile tile.bin_0 and record no
        tile_index_origin". So both conventions exist in real data and migration must read
        tile_index_origin either way (item 17's re-key rule already does). Note NDI's tiles
        template declares plain file_list `tile.bin_#`, NOT a file_series.
        DECIDED 2026-09-24 (jess): SWITCH DID FILE SERIES TO ZERO-BASED OUTRIGHT -- members
        NAME_0.., addFileSeries accepts index 0, no per-series origin field. Rejected: a
        recorded per-series origin. CONSEQUENCE: any series already stored as NAME_1.. (in
        the NDI cloud or local sessions since 2026-09-06) needs renaming -- not checked from
        here; the DID-matlab change must find and handle them. NDI's pre-series zero-based
        pyramids (tile.bin_0, no tile_index_origin) already match.

## Order agreed
anchoring -> sketch landmark/atlas against it as a test -> full landmark/atlas later.

## Open
- frame: does an image still need its own reference_frame, or can a position point at the image? (leaning: always a frame doc)
- vocabulary: direction/axis/origin terms mostly unminted (NDIC gap); image directions certainly
- grid frame vs the count statement's own x/y axes (double statement of 0.5 um)
- data-body: many files per body (tiles); knock-on (a) of item 14
- geneList / geneListMapping / fileReference; small defects (data_type_* field names,
  integer booleans, label vs base.name, datenum dates)
- unbuilt classes: count_calculation, length/area/term calculations, position + leaves
- this revises the 2026-09-22 [spatial_transcriptomics_family] sign-off

35. SPIKE-SORTER TARGET -> label_calculation (2026-09-24, jess). BUILT on PR #76 as 7fa543c:
    the three sorter rows' flags + a dated amendment in V_eta_subject_calculation_plan.md.
    CORRECTION of my own earlier claim: spike_clusters is NOT folded to count today -- its
    migrator passes it through to the NDI second pass (+migrators_j/spike_clusters.m);
    the count fold was withdrawn because it read a nonexistent field (num_spikes).
    PR #76 body now also carries item 34's derived_from_# misuses + NDI
    ontologyLabelSubjects.m (term_observation with derived_from_1 -- breaks against #76).

36. EDGE FAMILIES (2026-09-24, jess).
    (1) "Make all match": every repeated edge is a `_#` family AND carries `multiple`.
        BUILT on PR #76 as 1321501: presented_id -> presented_id_#; undirected_relation
        entities -> entities_# (min/max 2); derived_from_# gains `multiple`;
        test_repeated_edges_are_numbered_families pins it.
    (2) OPTION C: edge-family members are numbered FROM 0 everywhere V_eta mints them
        (time_reference_0, derived_from_0, presented_id_0, axis_labels_0 ...), so a 0-based
        index (item 13) names its edge directly: presentation_order value k -> presented_id_k.
        Consistent with 0-based file-series members (item 34). Rejected (a) 0-based index
        into 1-numbered edges (off-by-one); (b) 1-based presentation_order exception.
        EXEMPTION (same rule as T13 booleans): did_v1 passthrough tombstones keep v1's
        numbering -- NDI's add_dependency_value_n appends name_(n+1), i.e. from _1
        (DID-matlab +did/document.m:397), and v1 ensemble `neuron_id_#` suffix IS the
        1-based column index.
        SCOPE MEASURED: schema side is small -- 1 example (examples/
        scalar_temperature_observation_series.json time_reference_1), docstrings/comments
        in build_v_eta.py + 3 test files, 2 conversion docs; the family declarations are
        `_#` templates and do not change. EMITTERS: DID-matlab src 63 quoted `name_1`
        literals + 8 sprintf('%s_%d') sites; NDI V_eta branch +migrate 9 literals; plus
        DID's add_dependency_value_n (n+1) for anything V_eta-minted through it.
        NOT WRITTEN into schemas/ yet; item 13's 0-based index rule isn't in the tenets
        either.
    UPDATE 2026-09-24: BUILT on PR #76 as 7daa4c0 -- T14 bullet "Counting starts at 0"
    (indexes, edge families, file-series members; covers item 13 too);
    timed_sequence.presentation_order documents value k -> presented_id_k; the V_zeta-copied
    example renumbered by the build. The "tombstone exemption" was DROPPED: migrators read
    v1 numbering and never re-emit it. CORRECTION: three v1 tombstones DO declare families
    (ensemble neuron_id_#, daqsystem daqmetadatareader_id_#, syncgraph syncrule_id_#) --
    my first draft of the tenet said none did; fixed before commit. They need no change: a
    `_#` template matches any member number. Emitter work is on the PR #76 checklists.

37. harmonic_component_calculation RESTORED -- option A (2026-09-25, jess).
    History: signed 2026-08-08 (V_eta_stimulus_response_model_plan.md:541, TEAM-SIGN-OFF
    [stimulus response]) and built/folded; DELETED 2026-09-21 by issue #67 decision 10 (no
    reason stated; the adjacent decision 13 "_calculation suffix reserved for calculator
    outputs" is the implied one -- stimulus_response_scalar comes from the
    ndi.app.stimulus.tuning_response APP). Since then +migrators_j/stimulus_response_scalar.m
    is a guarded passthrough and the ledger row has EMPTY decided_targets; the
    `harmonic_component` data_type is draft, abstract, with ZERO subclasses (stranded).
    WHY RESTORE: #73's rule C (built, dfc5306) decides calculation by PROVENANCE, not by
    whether a calculator ran; a stimulus response is computed from the spike train + the
    stimulus presentation, both in the dataset -> a calculation. Decision 13's premise is
    superseded.
    SHAPE: harmonic_component_calculation <= [subject_calculation, harmonic_component], id
    PRESERVED, the signed 08-08 mapping (in git history): element_id -> subject_id,
    stimulator_id -> instrument_id, stimulus_control_id -> derived_from, params_basic ->
    method_parameters. Rebuilt under today's conventions (keys: trial, stimulus via
    labels_from; 0-based; value_id).
    SIDE EFFECTS: fixes the jCalculation.m:124 derived_from_1 -> tombstone misuse (the
    tuning curve's input becomes a real statement again); closes a Bar-2 regression on the
    corpora carrying stimulus_response_scalar (20211116, Soph, B were recorded at Bar-2 in
    August while the fold existed) -- INFERRED from the ledger row, NOT re-measured (no
    MATLAB here).
    REJECTED: fold into tuning_curve (a curve averages trials; per-trial data lost); keep
    the passthrough.
    Revises issue #67 decision 10.
