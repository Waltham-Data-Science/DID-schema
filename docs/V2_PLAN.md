# V2 migration plan

This is the working plan, not the record. Decisions live in their `Decided by`
lines, mostly in `schemas/V_eta_go_forward_class_audit.md`. Open work is
indexed in `schemas/V_eta_OPEN_WORK.md`. When this file and either of those
disagree, they win.

Last updated 2026-10-30.

## State at 2026-10-30 (pick up here)

Read this first after a break. Verify each PR's state on GitHub before acting;
this is a snapshot, not the record.

**Merged 2026-10-30:** DID-matlab #312, #313, #314, #315, #316, #318, #319,
#320, #321, #323; NDI-matlab #1106, #1107, #1111, #1113; empty-ontology #33.
did-schema #176 and #129 closed (superseded / stale).

**`Built:` marks still to record in did-schema** (find each PR's decision tag
in its PR body): DID-matlab #314 (clock nodes), #316 (v1 name own field),
#318 (canonical or needs info), #321 (spelling is notation), #323 (no retired
emitters); NDI-matlab #1106 (clock nodes), #1107 (strain openminds id), #1111
(final carry sweep). #312, #313, #315, #319, #320 are already marked (37a88d6).

**Open PRs, in merge order:**
1. DID-matlab fix PR, branch `claude/divergence-final-dependents`: adds
   `carryFinalDependents` (NDI-only, NDI-matlab #1111) to
   `crossRepoDivergenceTable`. `testBatchPassWiring` is red on DID-matlab V2
   until it merges.
2. DID-matlab #317 and NDI-matlab #1109: layout readers ([schema folders by
   family], siblings first). #1109's only red check ("V2 import (Haley) --
   fast") is red on NDI V2 too: see question L1 below.
3. did-schema #246 (this branch). After it merges: close #144 and #110
   (decision lines [differing stimulator epoch is malformed], [response unit
   slot settles 110]).
4. DID-matlab #325 (carry builds: oneepoch with its element, carry-156 n-trode
   count, carry-157 bath with no clock). Red until #246 merges (cites
   carry-156/157). After it merges: retire carry-148 in did-schema.
5. DID-matlab #304 (stimulator is SNOMEDCT:36645008; b4d626a), #322 (bath
   variable), #324 (last nine raw-v1 migrators): required checks green, corpus
   jobs were still running. #304 body still lists stimulator as carried; #324
   body still says MATLAB has not run. After #304: retire carry-121; mark the
   DID-matlab part of [stimulator is SNOMED CT Stimulator] Built.
6. ndi-ontology-matlab #17 (SNOMEDCT lookup): CI had not started. Then mark the
   ndi-ontology-matlab part of [stimulator is SNOMED CT Stimulator] Built.
7. NDI-matlab #1108, #1112 (only codecov/project red, -0.02%, looks like
   noise: #1113 test-only also fails it) and #1110 (codecov/patch 10% is a
   real coverage gap on the compression code). Team call.
8. Then the did-schema layout move (one PR): family subfolders, `retiring/`,
   `registry/` and `generated/` (split the authored parts of index.json and
   migration_targets.json), the Markdown move and `V_eta_*` -> `did_v2_*`
   rename redone on current main, README rewrite, web viewer reads. The
   sibling readers find files by basename; any rename beyond the
   `V_eta_`/`did_v2_` swap needs them updated first.

**Questions for Jess (batch 3, not yet asked; Proposed, not decided):**
- L1. NDI `TestLinkedSessions/testAnOlderLinkedSessionDocumentIsStillRead` is
  filtered because did-schema no longer declares `linked_session`, and the
  import workflow fails on any filtered test (red on NDI V2). Delete the test
  (the class is withdrawn) or let the workflow allow it?
- L2. Correction to the layout proposal: `quantity_list_meta.json` is written
  by `validate_v_eta.py` (D6), so it goes to `generated/`, not `registry/`.
- L3. Unit bindings (DID-matlab #320) are armed only by
  `DID_ENFORCE_UNIT_BINDINGS=1`. Writers give units outside the lists today
  (NDI Haley video time in `frame`; probe_geometry cm/nm; light-sheet axes).
  Widen the lists, carry those, or make the binding `preferred`?
- L4. Compression block (DID-matlab #319): codec terms gzip (EDAM:format_3989),
  LZW and Blosc (new EMPTY), and parameter variables (inner compressor,
  compression level, shuffle, block size).
- L5. #325 open points: more baths now carried in DID-only runs; an n-trode
  whose epochs disagree gets no count and no carry row; counts only from
  ingested epochs.
- Also held: ids for minted documents with no source id; carry-087 into
  carry-100; recognising a migrated element without the "ndi element class"
  assertion; Group vs ensemble; widening the equivalents fill (66 rows); a
  second-pass emitter for `purpose`; #1680 (Haley region names as "the map").

## Waiting for Jess

### Held and open (updated 2026-10-28, while Jess is away)

**Questions for Jess (answer in one line each):**

- **D1 (approved 2026-10-28).** Five device kinds minted on empty-ontology
  #31 (EMPTY:0000411-0000415), stacked on #30. Cell-attached is held: see G2.
- **G1. "text channel" vs NCIT Text.** [event lines are event channels] mints ANSWERED 2026-10-29: [text channel replaces NCIT Text] in `schemas/V_eta_go_forward_class_audit.md`.
  EMPTY "text channel" (empty-ontology #30, EMPTY:0000410). The term registry
  already gives the v1 prefix `tx` the channel type NCIT Text (C25704)
  ([channel types]). Should "text channel" replace NCIT Text there, or should
  both stay? [replace: NCIT Text means "the words of something written", not a
  channel; the other channel types are all "... channel"]
- **G2. Cell-attached recording.** [device kind labels and synonyms] defines an ANSWERED 2026-10-29: [cell-attached is OBI] in `schemas/V_eta_go_forward_class_audit.md`.
  EMPTY "cell-attached recording", but OBI:0002179 "cell-attached patch clamp
  assay" exists. T19 puts an existing term first. Use OBI:0002179 (keeping
  "cell-attached patch" and "on-cell recording" as notes), or mint anyway?
  [use OBI:0002179]
- **G3. Where a linked session's link lives, in NDI-written datasets ANSWERED 2026-10-29: [linked session link on a direct dataset relation] in `schemas/V_eta_go_forward_class_audit.md`.
  ([linked_session withdrawn]).** The migrator puts "database linking" and the
  Pathname on the session -> dataset `included_in` relation. NDI's writers
  (`ndi.dataset.addSessionV2`, `ndi.setup.V2.writeDataset`) file a session
  under its STUDIES, not directly under the dataset, so there may be no
  session -> dataset relation to carry the method, or several study relations.
  Options: (a) always write one direct session -> dataset `included_in`
  relation that carries the method (the study relations stay as they are);
  (b) put the method on every membership relation. [a: one place per fact, and
  it matches the migrated shape] The NDI build (its writers, `datasetSessions`,
  `datasetDatabaseFiles`, and `ndi.dataset`'s convert / unlink, which use the
  `linked_session` id today) waits on this.
- **G4. Allowed units ([allowed units are closed source_unit lists]).** ANSWERED 2026-10-29: [allowed units are source units] in `schemas/V_eta_go_forward_class_audit.md`.
  `source_unit` is the unit the SOURCE gave (the number in `source_value`);
  the canonical unit is fixed by the value class. Closing time's `source_unit`
  to [seconds] would refuse every source that gave milliseconds or minutes.
  Read the seed as the units a source may give (time: second, millisecond,
  minute, hour; spatial position: metre, millimetre, micrometre), each
  converted to the canonical one? There is also no binding row shape for this
  yet (the registry's lists are subject statement, relation, entity field and
  entity type bindings); proposed: a new list `unit_bindings`, one row per
  variable node: `{"variable": {node, name}, "source_units": [{node, name},
  ...]}`. [yes to both]
- **G5. The `abs` block holds interpolated values too (DID-matlab #272).**
  [absolute-value fits are fit entries] said to bring it back if `abs` held
  more than fits on |response|. It does: `abs.fitless` (L50, Pref, H50,
  bandwidth, low/high pass index of |response|) beside the five abs fits, in
  all 5,604 Soph SF/TF calculator documents; in 1,987 it differs from the main
  `fitless` (NDIcalc-vis-matlab 00e3e0f `spatial_frequency_tuning.m`,
  `temporal_frequency_tuning.m`). Proposed: `interpolated_values` becomes a
  list of entries like `model_fit`, each with the optional `response_transform`
  ("absolute value" on the abs one), so one calculation holds both and T10
  holds. Until answered, the second calculation stays (built E1 and E2 only).
  [yes] ANSWERED 2026-10-30 [interpolated values are a list].
- **G6. A single fitted model on the method (DID-matlab #272).** The T10 ANSWERED 2026-10-29: [fit model stated once] in `schemas/V_eta_go_forward_class_audit.md`.
  amendment says the method does not repeat the fitted functions; the decision
  line [one calculation per named calculator output] only says "no `function`
  list". So families whose fits all share one model (Naka-Rushton, Priebe,
  double Gaussian) still write one `{function: <model>}` method parameter
  beside the `model` in each fit entry. Drop it too? [yes: one place per fact]
- **G7. Deleting V2 `base.name` breaks the 73 `retire` classes in `stable/`.** ANSWERED 2026-10-29: (b), [base.name kept until retire classes leave] in `schemas/V_eta_go_forward_class_audit.md`.
  [carried v1 validates against NDI templates] deletes the 8 `deprecated/`
  tombstones and V2 `base.name`. But 73 classes marked `retire` remain in
  `stable/` (generic_file, valid_interval, syncrule, epochfiles_ingested,
  control_stimulus_ids, ...), and DID-matlab validates a v1 document passed
  through unchanged against the one of the same name. Those documents carry
  `base.name`, so with it deleted they fail: DID-matlab #274 against the
  deletion, run 40637773135: 33 failures, 43 x "Property block base carries
  undeclared field name". Options:
  (a) DID-matlab stamps an unchanged passthrough `did_v1` (not validated
  against V2) inside `v1_to_v2`; this moves the stamping [passthrough stays
  v1: how] put at the end of NDI's pipeline, so NDI's second pass would
  receive `did_v1` bodies;
  (b) keep V2 `base.name` until no document passes through under a `retire`
  class (each class converted or carried as v1), then delete it and the 73
  classes together;
  (c) delete the 73 `retire` classes now too and carry their documents as v1.
  [b: it changes nothing NDI relies on; the 8 `deprecated/` tombstones can go
  now, since nothing validates against them once DID-matlab #270's template
  check is in -- but only if (b) keeps `base.name`]
- **G8. The Naka-Rushton term ([Naka-Rushton is one function]).** The
  decision makes the RB / RBN / RBNS fits one model term; DID-matlab writes the
  model today as the bare label "Naka-Rushton" (`jTuningCurve.m` oneFunction).
  No existing term: OLS4 (2026-10-28) has no hit for "Naka-Rushton"; Wikidata
  Q52425525 is a scholarly article, not the function. Proposed EMPTY term:
  label "Naka-Rushton function", definition "A saturating function of contrast,
  R(c) = Rm c^n / (c^(n s) + c50^(n s)), used to describe the contrast response
  of a neuron.", exact synonym "Naka-Rushton equation", under NCIT:C16870 Mathematical
  Model (as the empty-ontology NCIT import already carries NCIT terms). Mint
  it? [yes] ANSWERED 2026-10-30 [Naka-Rushton function minted].
- **G9-G12. Real losses the whole-batch round trip found (DID-matlab #275,
  report-only; Test code run 40752793846; not patched in the inverses):**
  - **G9. `daqreader_mfdaq_epochdata_ingested`** (B 1,242, Dab 2,846). ANSWERED 2026-10-29: [segment length is the time chunk] in `schemas/V_eta_go_forward_class_audit.md`. Before that: the two segment lengths are what NDI's reader needs (`+ndi/+daq/+reader/mfdaq.m:245-253`), and NDI V2's ingest still writes this v1 document (`mfdaq.m:778-784`), so this is the V2 shape for ingested data: proposed, the `ingestion_manifest` carries an ingestion method with the two lengths as parameters, NDI's ingest and reader move to it first, then the migration writes it and drops the v1 document. Earlier text:
    `resolveEpochProbemap` retires the v1 archive once data bodies carry its
    files (the check reads files only). Lost: the v1 id (conflicts with
    [every v1 id survives]; e.g. B `4126900d95ad6706_c0a14ee8785c648f`), the
    archive datestamp, `parameters.sample_analog_segment` /
    `sample_digital_segment` (1e6 / 1e7 there) and the empty `file_list`
    slots. Proposed: keep the archive's id on one V2 document (the reader
    configuration) and its parameters as method parameters there. [yes]
  - **G10. openMINDS species text** (JH 3,312; sample ANSWERED 2026-10-29: [species text is the openMINDS equivalent] in `schemas/V_eta_go_forward_class_audit.md`.
    `41269430c5d0f59d_c09ab830daf16ec5`): v1 `definition` ("Caenorhabditis
    elegans is a species of nematode ...") and `synonym` ("C. elegans") are
    not in V2. [openMINDS subject leftovers] says they are "read back from the
    term", but nothing in DID holds openMINDS's text (the registry's
    NCBITaxon:6239 definition is empty). Proposed: register the definition and
    synonym on the term registry row, so the read-back has a source. [yes]
  - **G11. `openminds_element`** (Dab 404; sample ANSWERED 2026-10-29: [openMINDS element leftovers carried] in `schemas/V_eta_go_forward_class_audit.md`.
    `4126945af68c0fad_c0d698b17d043af0`): lost `openminds_id`
    ("CellType/12318b5f-...", a UUID per document) and `fields.description`;
    V2 holds only the term assertion. No decision covers element leftovers.
    Proposed: as for subjects, carry the document as v1 when it holds them,
    with a register row. [yes]
  - **G12. `probe_location` name** (Dab 404; sample ANSWERED 2026-10-29: [term names compare by node] in `schemas/V_eta_go_forward_class_audit.md`.
    `4126945af68c1b4b_40df43b5cb45324d`): v1 "bed nucleus of stria terminalis
    (BNST)", V2 the registry label "bed nucleus of stria terminalis"
    (UBERON:0001880). Is the v1 spelling notation (compare by node, the 404
    clear)? [yes: a term is identified by its node]
- **G13. Labels of a sync rule's trigger-channel parameters (DID-matlab
  #276).** A channel-based sync rule's two trigger channels become method
  parameters labelled `daqsystem ch1` / `daqsystem ch2`, the generic rule for
  an unread v1 parameter. Role-named labels ("from trigger channel" / "to
  trigger channel", matching the from/to rig edges) were not decided. Rename?
  [yes, to match the edges] ANSWERED 2026-10-30 [trigger channels named by their link].
- **G14-G17. From the element device-kind build (DID-matlab #277):**
  - **G14. Where the n-trode electrode count comes from.** [n-trode is a
    multielectrode array] puts the count on the device, but NDI's `element`
    template holds only `ndi_element_class`, `name`, `reference`, `type`,
    `direct`: no count on the v1 element. Read it from the epochprobemap
    channel list, from `probe_geometry` / `site2channelmap`, or elsewhere?
    [the epochprobemap channel list: every n-trode has one] ANSWERED
    2026-10-29 [n-trode count from the channel list].
  - **G15. One- vs two-photon imaging.** Both take OBI:0400169 microscope,
    so once the `element type` assertion is dropped the kind alone cannot
    rebuild which it was. Keep the mode, e.g. as a method term on the
    recording observation? [yes, as the patch / sharp modes are] ANSWERED
    2026-10-29 [imaging mode is a method term].
  - **G16. A sorted unit whose probe is not in the batch.** [unit direct and
    subject rebuild from the probe] cannot check its `subject_id`; today it
    converts with a `unit_probe_not_in_batch` note and the round trip reports
    `subject_id` lost. Carry it as v1 instead (needs a register row)? [yes] ANSWERED 2026-10-29 [unit with no probe in the batch carried].
  - **G17. The Equipment Type binding's root.** NCIT:C178920 "Equipment
    Type" is bound with root OBI:0000968 (ontology OBI), but most decided
    device kinds are NCIT or Wikidata terms; harmless only while
    BindingConformance stays off. Widen the binding to a closed list of the
    registered device kinds? [yes] ANSWERED 2026-10-29 [equipment type is the
    device kind list].
- **G18-G39. From the 2026-10-29 build round (DID-matlab #278-#285, NDI-matlab
  #1093). Each names the decision it holds; "[...]" is Claude's
  recommendation, Proposed (not decided).**
  - **G18. How pass 1 hands on a `control_stimulus_ids` record ([second pass
    reads control stimuli from v1]).** Joining `rawV1Classes` alone would
    quarantine every record in a validating run (the writer's `app.name` is
    undeclared on the tombstone). Carry it whole as v1 in pass 1, like
    `stimulus_presentation`? If so, widen carry-045 or add a row? ANSWERED 2026-10-30 [control records carried in pass 1].
  - **G19. A standalone item's control pairing ([control pairing points at ANSWERED 2026-10-29: [standalone item control stays carried] in `schemas/V_eta_go_forward_class_audit.md`.
    the presentation]).** A standalone item has no manipulation: what do the
    calculation's `entity_id` and `input_id` point at? (Today carry-090.)
  - **G20. A linked session not in the batch ([linked session reference ANSWERED 2026-10-29: [linked session not in the batch] in `schemas/V_eta_go_forward_class_audit.md`.
    follows the ingested rule]).** Its reference cannot be compared, so the
    membership is carried with no register row. Widen carry-069 (ingested
    only today) to linked sessions, or a new row?
  - **G21. An unstated `session_creator` ([session opener inputs]).** It still ANSWERED 2026-10-29: [unstated session creator carried] in `schemas/V_eta_go_forward_class_audit.md`.
    converts, with no "software class" parameter. Carry it under carry-119
    too?
  - **G22. A drug with an offset or duration but no onset ([drug end and ANSWERED 2026-10-29: [drug end without start needs mapping] in `schemas/V_eta_go_forward_class_audit.md`.
    duration on the anchor]).** An end needs a start (`end_consistent`).
    Carry the record whole as v1 (needs a register row)?
  - **G23. UTC onset, offset and duration that disagree.** Writing all three ANSWERED 2026-10-29: [drug times that disagree need mapping] in `schemas/V_eta_go_forward_class_audit.md`.
    fails `end_consistent`; writing one means choosing. Carry as malformed?
  - **G24. The image collection link ([image file details placed]).**
    `imageCollection_id` as `member_of` a group: who mints the group and with
    what id; does `member_of` start at the observation or the body; where do
    the collection's label, format and subject go? ANSWERED 2026-10-30 [image collection carried until a writer].
  - **G25. [image label goes to notes] before the rename.** `data_body` has ANSWERED 2026-10-29: [image label goes to the observation's notes] in `schemas/V_eta_go_forward_class_audit.md`.
    no `notes` yet, only `description`, which the stack's name already uses.
    Wait for the did_v2 rename, or write it elsewhere now?
  - **G26. What an `ngrid` body attaches to when there is no statement ANSWERED 2026-10-29: [ngrid with no statement carried] in `schemas/V_eta_go_forward_class_audit.md`.
    ([ngrid migrates to sampled bodies]):** an ontologyImage whose only edge
    is its table row, and a standalone `ngrid` (no NDI writer makes one).
  - **G27. [binaryseries parameters fold as decided].** The data body it ANSWERED 2026-10-29: [binaryseries parameters carried] in `schemas/V_eta_go_forward_class_audit.md`.
    describes cannot be found (no edges, no NDI writer). Carry it as v1 under
    a needs-home row?
  - **G28. Where the clock of "acquisition time" goes ([afo prefix
    registered]).** It sits in the label today and the round trip reads it
    from there. ANSWERED 2026-10-30 [acquisition time on its clock].
  - **G29. The general method term for tuning curves that are not fits,
    hartley_calc and stimulus_response_scalar ([method terms are
    general]),** and whether jrclust and the generic fits gain Spike sorting
    / curve fitting. ANSWERED 2026-10-30 [data analysis is the general method].
  - **G30. [oneepoch is a redundant calculation].** No "concatenation" term, ANSWERED 2026-10-29: [oneepoch method is data combination] in `schemas/V_eta_go_forward_class_audit.md`.
    no row for the device-local carry, the per-epoch `input_id` links need a
    batch pass, and what the calculation's value holds is not stated.
  - **G31. [old table rows counted and carried].** No register row covers it, ANSWERED 2026-10-29: [old table rows carried by NDI] in `schemas/V_eta_go_forward_class_audit.md`.
    and NDI's second pass reads these rows today: carry in DID's pass 1, or
    in NDI's?
  - **G32. [redeclarations only narrow].** All 8 current redeclarations are ANSWERED 2026-10-29: [redeclarations merge when base.name goes] in `schemas/V_eta_go_forward_class_audit.md`.
    `<class>.name` over `base.name`, which stays ([base.name kept until
    retire classes leave]). Which, if any, merge into the parent now?
  - **G33. "The fill" of [term equivalents recorded].** 0 of 896 registry
    rows carry an equivalent. A DID-matlab tool that proposes rows from
    openMINDS's mapping, or a one-time did-schema data change? ANSWERED 2026-10-30 [equivalents filled in did-schema].
  - **G34. An `app` field outside the control template (NDI-matlab #1093).**
    Read as malformed (carry-100), not as a software field. Right reading of
    [control record fields split]? ANSWERED 2026-10-30 [control records carried in pass 1].
  - **G35. Hartley generator keys the shared basis does not read** (`randState`,
    `rect`, `distance`, `chromhigh`, `reps`, ...): the basis is minted once
    per session, so the presentation has no method of its own. The
    manipulation's inline method? ANSWERED 2026-10-30 [Hartley settings on the inline method].
  - **G36. A second value of a key the grating recipe reads once.** 0 cases in
    B, Dab and 20211116. ANSWERED 2026-10-30 [image raw round trip and single-read keys].
  - **G37. The probe coordinate system ([site frame is a coordinate
    system]).** Its required `reference_point` and depth `positive_direction`
    are recorded as "unknown": which terms? The registry also lacks a z-axis
    and left/right, front/back terms. Jess (2026-10-29) asked why not
    `needs_mapping`; Claude: v1's `probe_geometry` template has no field for
    either, so every probe would stay v1; options (a) optional for everyone,
    (b') required, with an EMPTY "not stated in source" term the migration
    writes, (needs_mapping) every probe carried. [(b')] ANSWERED 2026-10-29
    [missing facts are needs info]: neither; a `needs_info` entry on the
    document names the missing field.
  - **G38. "Exactly one canonical" ([quantity reference type]).** DID-matlab's
    own writers fill no canonical for a concentration whose unit converts to
    none, and `{source_value: NaN}` for an unrecorded amount (decided
    2026-10-21). Does "exactly one" allow zero then, or must writers convert
    (and what of a unit that converts to none)? ANSWERED 2026-10-30 [canonical absent only as needs info].
  - **G39. Synonyms in the term registry.** [registry holds nodes]
    (2026-10-22) says the registry "carries no synonym field"; [spelling is
    notation] (2026-10-26) puts synonyms there, and did-schema ccd05db built
    them. Read the later decision as superseding the earlier? [yes] ANSWERED 2026-10-30 [synonyms supersede nodes only].
- **G40-G45. From the 2026-10-29 afternoon builds (DID-matlab #287-#289,
  NDI-matlab #1094). "[...]" is Claude's recommendation, Proposed (not decided).**
  - **G40. The linked-session link in NDI-written datasets ([linked session
    link on a direct dataset relation]; not built, NDI-matlab).** (1) Does an
    ingested session NDI writes also get the direct session -> dataset
    `included_in`, with "database ingestion" (EMPTY:0000399)? (2) When
    `convertLinkedSessionToIngested` / `convertIngestedSessionToLinked` run, is
    the direct relation replaced (new method) or edited? (3) Does its method
    carry only the Pathname, or also "software class" = `ndi.session.dir` as the
    DID-matlab migrator writes when `session_creator` is stated? (4) Relative
    Pathname when the session folder is inside the dataset folder (what NDI
    writes today), or always absolute? (5) Is `ndi.dataset.addSessionV2`, which
    also writes `linked_session`, in scope? [(1) yes, "database ingestion";
    (2) replaced; (3) both, as migrated; (4) relative inside, absolute outside;
    (5) yes] ANSWERED (1)-(3), 2026-10-29 [linked session link details]. Still
    open: (4) (Jess asked whether it should be relative at all; Claude: keep
    relative inside, so a dataset moved as one folder still finds its sessions,
    `ndi.v2.linkPath`); (5) `addSessionV2` is the shared helper that
    `add_linked_session` (`dataset.m:117`) and `add_ingested_session` (:208)
    call, not a public entry point; once no v1 branch remains ([v1 writes into
    a V2 session]) it should be folded back or renamed. (4), (5) ANSWERED
    2026-10-29 [linked session pathname], [addSessionV2 folded back].
  - **G41. Merging a redeclaration into the parent ([redeclarations only
    narrow]; not built).** The 8th redeclaration is `pyraview.label` over
    `filter.label` (identical; pyraview is `retire`), not a `name`. Hold it with
    the seven `name` ones? How does the validator know which are held: a list
    mirroring did-schema's `NARROW_ONLY_EXEMPT`, or a marker in the schema? Is a
    merged field then hosted only in the parent's block (a shape change)?
    [hold pyraview.label too; a schema marker; yes, parent's block only] MOOT 2026-10-30 [redeclaration merge moot]. Claude (2026-10-29) proposed it is moot, since every remaining redeclaration is a `name` over `base.name` and pyraview.label goes with pyraview; awaiting Jess.
  - **G42. A round trip for v1 `image` (DID-matlab #288).** `image` is read on
    the renamed path, so there is no raw-v1 inverse to carry the label back.
    Build one (it must rebuild `format` 'tiff' from EDAM:format_3591)? [yes,
    when `image` moves to the raw-v1 path] ANSWERED 2026-10-30 [image raw round trip and single-read keys].
  - **G43. Two vintage-B ontologyImage cases ([ngrid with no statement
    carried]).** One with no non-empty edge at all (NDI's `imageDocMaker.m:130`
    makes it when given no row), and one with a subject or element edge beside
    the row (no writer makes one). [carry the first like the row-only case
    (carry-124); the second is malformed] ANSWERED 2026-10-29 [vintage-B ontologyImage cases].
  - **G44. The global-clock `oneepoch` calculation ([oneepoch is a redundant
    calculation]; not built).** (1) Its `input_id` targets, the per-epoch
    recordings, exist in pass 1 only where an `epochfiles_ingested` cache
    exists; elsewhere NDI's second pass mints them: wait for NDI's pass, or
    carry? (2) The required `variable`: from the element type
    (`derivedSeriesKind`)? (3) DID cannot read the `.vhsb` bytes: a
    `sampled_body` with no extents, or an `opaque_body` as today? (4)
    `redundant: true` on the calculation, the body, or both? (5) Fork A1 mints
    no epoch for `whole_session_<ref>`: what is it anchored to? [(1) NDI's
    second pass links them; (2) yes; (3) opaque_body, re-described by NDI as
    today; (4) the body; (5) the session] ANSWERED 2026-10-30 [global-clock oneepoch details].
  - **G45. "Pre-repair" ([old table rows counted and carried], NDI-matlab
    #1094).** Read as: the row holds an edge value no `data` cell holds (NDI
    40dc9aa86 keeps each dependency column in `data`; before it the column
    was deleted). Right reading? [yes] MOOT 2026-10-30 [table rows carried as v1]: every row is carried, pre-repair or not.
- **G46. NDI's v1 writers in a V2 session ([one folder, final classes only]).**
  NDI-matlab V2's own v1 writers (spike sorter `+app/spikesorter.m:277`, spike
  extractor, element, probe location, openMINDS, syncgraph and others) still
  build v1-template documents; in a session with a V2 database NDI stores them
  through did2sqlite, which validates them (`did2sqlite.m:229-233` ->
  `sqlitedb.m:1285-1289`) against the retire file of the same name, unstamped.
  18 retire classes cannot be deleted while that holds. (a) V2 sessions accept
  only V2 documents: the writers move to V2 shapes or are refused first; (b) a
  v1 write into a V2 session is stamped v1 and checked against NDI's own
  template, as a carried document is. Not measured: whether any real session
  takes this path. [(b) now, (a) as the end state] ANSWERED 2026-10-29 [v1
  writes into a V2 session].
- **G47-G55. From the 2026-10-29 evening builds and the pending-line triage.
  "[...]" is Claude's recommendation, Proposed (not decided).**
  - **G47. A short last chunk ([segment length is the time chunk]).** `chunk`
    is documented as every file holding a full chunk, padding included; NDI's
    last segment is short (`+ndi/+daq/+reader/mfdaq.m` around :928). Allow a
    short last chunk? [yes: the last chunk holds what remains] ANSWERED
    2026-10-29 [short last chunk].
  - **G48. The V2 ingest shape (G9).** NDI V2's ingest writes only the v1
    `daqreader_mfdaq_epochdata_ingested` document (`mfdaq.m:778-798`) and the
    reader finds data only through it (`reader.m:44-61`); NDI's second pass does
    not re-describe segment files (`epochSeriesBodies.m:82-87` handles `.vhsb`
    only). Needed: how a reader and an epoch find the epoch's sampled bodies
    (one per channel group?), and which dimension term marks time. [one
    `sampled_body` per channel group, owned by the epoch's recording
    observation; time dimension term = the registry's time term] ANSWERED
    2026-10-29 [V2 ingest is one sampled body per channel group].
  - **G49. openMINDS strain leftovers ([openMINDS strain leftovers], #158).**
    The variable terms for the `breedingType` and `diseaseModel` assertions;
    the vendor -> CURIE prefix table beyond JAX and how the vendor is read (a
    separate openMINDS Organization document); how several identifiers fill
    `entity.global_identifier`; what "lookupLabel is rebuilt" means. ANSWERED 2026-10-30 [openMINDS strain leftovers settled].
  - **G50. Two retire classes the migration reshapes ([one folder, final
    classes only]).** `distance_metadata` and `oneepoch` are reshaped into the
    retire class rather than left as v1, so their files cannot go. Carry them
    whole as v1 (losing the decided reshape until their V2 homes are built), or
    build the homes first? [build the homes first: `oneepoch` is G44;
    `distance_metadata` needs its own decision] ANSWERED 2026-10-29 [reshaped
    retire classes carried]: carry them whole as v1 for now.
  - **G51. The age-at-injection variable ([age at injection is an
    observation]).** Which term is the variable of the age observation? ANSWERED 2026-10-30 [age is NCIT Age].
  - **G52. Dataset-specific logic left in the generic stage ([dataset-specific
    logic leaves the generic migration]).** Should the Haley encounter map
    (audit Q1) and the imageStack mask words (Q3,
    `docs/v2_working/DATASET_SPECIFIC_AUDIT.md`) leave the generic stage? ANSWERED 2026-10-30 [Haley mask words leave the generic stage].
  - **G53. The EMPTY assay labels ([old EMPTY labels generalised]).** Approve
    each row of `docs/v2_working/EMPTY_ASSAY_LABELS_PROPOSAL.md`. ANSWERED 2026-10-30 [assay labels batch 1]-[assay labels batch 6].
  - **G54. The element device-kind table ([element type is a device kind
    term]).** Approve the per-type table in `ELEMENT_TYPES_DRAFT.md` (with G15,
    G17). ANSWERED 2026-10-30 [element types batch 1]-[element types batch 4].
  - **G55. Element name and reference stored reversibly ([early migration
    pieces fixed], part 5; OPEN_WORK #142).** Which shape? ANSWERED 2026-10-29 [element name and reference stored apart].
  - **G56. Finding a term by a spelling of its name.** DID-matlab's term index
    matches a name lowercased only (`+did2/+schema/termIndex.m:70`), so "path
    name" does not find "Pathname"; relation and entity-type handles also ignore
    spaces, underscores and hyphens (`+did2/+build/vocabulary.m:161`). (a) Use
    that rule for registry names too (checked: no two of the 898 registry names
    collide under it); (b) add the spelling to the row's `synonyms` (read today
    by one migrator only). [(a)] ANSWERED 2026-10-29 [term names match
    ignoring spacing].
  - **G57. Decibels ([canonical absent only as needs info]).** A dB value is a
    log ratio: its linear value is 10^(x/10) for a power ratio and 10^(x/20)
    for an amplitude ratio, so DID-matlab's unit table gives it no canonical
    factor (`jSourceUnit.m` TERMONLY). Keep dB as its own canonical unit (no
    conversion), or convert to a linear ratio using the variable to tell power
    from amplitude? ANSWERED 2026-10-30 [decibels are their own canonical].
- **G58-G63. From the 2026-10-30 overnight builds. "[...]" is Claude's
  recommendation, Proposed (not decided).**
  - **G58. `stimulator` and its cascade ([element types batch 4]).** Carrying a
    v1 `stimulator` element (vhlab: a visual-stimulus computer; Marder: an
    electrical stimulator) carries everything that depends on it (carry-064):
    its element_epochs, and the probe-map stimulus manipulations lose their
    `instrument_id`, reaching Dab baths and vhlab stimulus data (DID-matlab
    #304). No general stimulator device term exists (OLS4, 2026-10-30). (a)
    carry anyway; (b) mint EMPTY "stimulator" ("A device that delivers a
    stimulus to a subject", under OBI device) for both writers, and drop the
    exact synonym "stimulator" from EMPTY:0000413. [(b)]
  - **G59. The V2 ingest's open details ([V2 ingest is one sampled body per
    channel group]).** NDI's live ingest knows the daq system, reader and v1
    epoch_id, but no recording observation exists then. (1) Owner: does the
    ingest mint the epoch and one observation per element from the
    epochprobemap, or one observation per daq-system epoch? Its variable and
    value kind, and for ti/di/ax groups? (2) `channel_list.bin` (names, types,
    groups, sample rates, offsets, scales): channel-dimension covariates, a
    separate opaque_body, or conditions? (3) The event/marker/text file (not
    sampled) and the `ti` time group: own bodies, or covariates? (4) Files are
    `<prefix>_group<g>_seg.nbf_<s>` from 1; the schema names members
    `body_data_k` from 0: rename, or map with 'Files'? (5) How the reader finds
    an epoch's bodies, and where the epochtable's t0/t1 and clocks go. (6) Is
    the v1 ingested document still written? (NDI-matlab agent report; nothing
    built.)
  - **G60. A dataset with no single `dataset` document ([linked session link
    details]).** NDI-matlab #1103 puts the link's method on the session's
    relation to its study when there is no dataset document, and makes a linked
    session with neither an error (`ndi:setup:V2:noLinkParent`). Right?
  - **G61. openMINDS fragment text beyond Species ([openMINDS strain
    leftovers]).** The decision stops storing a Species or GeneticStrainType
    fragment's definition and synonyms (read back from the term). Apply the
    same to breeding-type and disease-model fragments? (Reverted from NDI-matlab
    #1104 until decided.)
  - **G62. The remaining mode terms ([element type is a device kind term],
    [imaging mode is a method term]).** Recording modes voltage (-Vm) and
    current (-I, -Im), and imaging modes one-photon, two-photon and wide-field:
    which terms? (Claude to bring candidates from OLS4.)
  - **G63. The four NDI clock types (did-schema #97).** ANSWERED earlier (my
    mistake to ask): [clock terms get nodes] (Jess Haley, 2026-10-26) decided
    them, and the terms are registered (wikidata:Q1536, EMPTY:0000403-0000405);
    only the DID-matlab and NDI-matlab node comparison is left to build. `utc`,
    `dev_local_time`, `dev_global_time`, `exp_global_time` are bound with empty
    nodes. Mint four EMPTY terms (T19 names EMPTY the minting authority), or use
    existing terms where they exist (UTC has candidates)? Also open, each in its
    own issue: #105, #108, #110.
- **G64-G73. From the DID-matlab builds of 2026-10-30 (#305, #306) and the G53 build plan. "[...]" is
  Claude's recommendation, Proposed (not decided).**
  - **G64. Register `om:day` "day".** DID-matlab writes it as a source unit
    (jTreatmentAnchor already; #306 for the image-stack datenum and postnatal
    day), and it is not in the term registry (`om:hour` and `om:minute-Time`
    are). Register it? [yes: an existing OM unit, T19]
  - **G65. Shape of an acquisition time on a UTC clock (G28,
    [acquisition time on its clock]).** DID-matlab #306 writes a
    `relative_time_reference` to the session on clock utc, start = datenum x
    86400 s ("seconds since datenum 0, from the session"), copying
    jTreatmentAnchor. The other shape is an `absolute_time_reference` holding
    the ISO UTC instant. [absolute: a UTC instant is not an offset from the
    session, and the relative form's zero point is not the session's]
  - **G66. Hartley implied, after G29.** [hartley method implied] says
    "Hartley" is implied by the method term ndi.calc.vis.hartley; G29 replaces
    that term with EDAM "Data analysis", so DID-matlab #306's round trip infers
    Hartley from the `receptive_field_calculation` class instead. Amend the
    line to say so? [yes]
  - **G67. A formulation with no amount stated ([canonical absent only as
    needs info]).** When no ingredient states an amount, the value is blank and
    `value_inline_or_body` refuses it, so DID-matlab #305 keeps the old NaN
    there. (a) the value rule accepts a blank value that `needs_info` names;
    (b) keep NaN. Also: a missing canonical is named
    `formulation.value.ingredients(k).concentration.canonical`, a path that is
    not a declared field (a concentration has no single canonical). Keep that
    convention? [(a); yes]
  - **G68. Postnatal day 0.** `virus_AdministrationPND` defaults to 0 in NDI's
    template, and #306 writes 0 as age 0 days, because no decision treats it
    as unrecorded (unlike dilution). Keep, or treat 0 as not stated (needs
    info)? [needs info: the template default is indistinguishable from a
    recorded 0]
  - **G69. Building G53 ([assay labels batch 1]..[6]).** A read-only plan,
    docs/v2_working/G53_BUILD_PLAN.md, finds 91 EMPTY terms touched, none in the
    term registry, 73 v1 dictionary entries (Dab, Hunsberger, Babu, Haley)
    looking them up by LABEL, and no V2 importer yet for Dab, Babu or
    Hunsberger. Its section 4 has 16 questions; the ones that block a build:
    Q1, seven nodes each get the same three labels (R2 refuses duplicate names):
    [relabel the lowest node of each, obsolete the other six with `consider` it];
    Q2, a relabelled general term keeps its elevated-plus-maze parent? [no: move
    it under the general parent]; Q4, no definition is given for the ten
    relabels [Claude drafts from the current ones, assay and units stripped, for
    approval]; Q7, the Babu and Hunsberger imports also write these terms [in
    scope; name them]; Q8, "EMPTY:0000129/0000256/0000257 readers first" [NDI
    reads them by node, which survives obsoletion: nothing to build]; Q9, the v1
    dictionaries' label lookups [move them to nodes before empty-ontology
    releases the change to main]; Q11, five obsoletes with no replacing term
    [obsolete all five; `consider` as listed there, none for B13]; Q14(a),
    A61's UO:0000031 "minute" clashes with the registered `om:minute-Time`
    [use om:minute-Time].
  - **G70. #119 part 1 (skip OPEN_WORK's dated RE-DERIVED log in
    `check_prose_counts`).** Built and reverted the same hour: with the 64 log
    paragraphs skipped, OPEN_WORK keeps 4 older in-row counts that only the
    log's current figures were satisfying (lines 431, 523 and 568, "91 NDI
    templates"; line 963, "42 direct subclasses of `data_type`"), so the gate
    fails. (a) mark those in-row counts as dated (e.g. "at <date>: 91
    templates", which the check reads as history); (b) skip all of OPEN_WORK;
    (c) leave #119 part 1 as is. [(a): they are dated measurements, and the
    rest of the check keeps working]
  - **G71. A virus dilution ([canonical absent only as needs info]).**
    A virus injection's dilution is a v1 number with no unit (e.g. 1000; the
    migrator labels it `dilution`). DID-matlab #311 leaves it as it was (source value, no
    canonical). Carry it (carry-155; that carries every virus_injection with a
    dilution, 5 fixtures), or name its canonical in `needs_info` ("a source
    number with no unit")? [needs_info: a dilution is a ratio, nothing is
    unknown about the document but the unit]
  - **G72. Percent volume per volume.** Babu writes `Percent Volume per Volume`
    (NCIT:C48571, 11 rows); x0.01 to `concentration.liters_per_liter` is exact.
    Register NCIT:C48571 and convert, or keep the source only? (No fixture is
    affected today: every Babu treatment is carried by location.) [register and
    convert]
  - **G73. #119 part 2, the growth ratchets.** All ten `BASELINE_*` ratchets
    are listed in docs/v2_working/RATCHETS_119.md. Only B6 (bound fields with
    no catalogue row; 116, today 95) grows with normal decided work, so it
    becomes report-only. The other nine stay fail-on-growth, and the five that
    sit above today's count (B1, B3, B6, B8, B9) are lowered to it. [as listed]

- **E1. Tuning curves whose `stimid` list does not rebuild (DID-matlab #266).**
  Measured by a scratch run: 20211116, 20 of 84 curves rebuild exactly; Soph,
  5,991 of 34,606. Every failing curve printed (3 per corpus) selected
  `angle ... best`, and the angle "best" chose is stored only in the curve's
  `log` ("angle best value is 90."). May the rebuild read that value from the
  `log`? If yes, most of the 28,615 Soph carries would likely convert (not
  measured). [yes, the log is kept verbatim in `notes` anyway] ANSWERED 2026-10-28 [tuning best value is a condition] (marked 2026-10-29).
- **E2. One calculation with fits of several functions.** SF and TF hold five
  fitted functions in one calculation; the build writes the method parameter
  `function` as a JSON list (`["dog","movshon","movshon c","spline","gausslog"]`).
  Keep that, or drop the parameter and rely on each fit entry's `model`? [drop it:
  one place per fact] ANSWERED 2026-10-28 [absolute-value fits are fit entries] (marked 2026-10-29).
- **E3. Where the Priebe "what differs" goes.** The three Priebe fits are one
  equation (checked: NDIcalc-vis-matlab 00e3e0f, only xi's bounds differ). The
  build records "xi held at 0" in each fit entry's `constraints`, as for
  Naka-Rushton, not as method parameters. Confirm? [yes] ANSWERED 2026-10-28 [absolute-value fits are fit entries] (marked 2026-10-29).
- **F1. A presentation that names no epoch at all (NDI-matlab #1087).** B1 as
  built carries a presentation whose epoch the fold refuses (carry-109); one whose
  `epochid.epochid` is empty keeps its session anchor and is counted in
  `epoch_anchor.no_epoch_string`. Carry it with carry-109 too? [no: v1 named no
  epoch, so the session anchor loses nothing] ANSWERED 2026-10-28 [presentations without an epoch keep the session anchor] (marked 2026-10-29).
- **#208 (tabled by Jess until just before the `notes` storage pass):** rename
  `base`? rename the `session_id` edge? Comments on the issue hold the options.

**Done without Jess, per an earlier decision:** EEG. [ecg and eeg are
recorders] said to use a Wikidata electroencephalograph if one exists, else
register `scdo`. Wikidata has wikidata:Q4531135 "electroencephalograph"
(P279 chart recorder, diagnostic equipment; P366 electroencephalography), so
`eeg` takes it and `scdo` is not registered; its term registry row and
OBI:0003806 "electrocardiograph" were added.

**Builds in flight (2026-10-28):** DID-matlab #262-#270 (other decisions),
the DID-matlab tuning PR(s) (`claude/build-tuning-2026-10-27`), NDI-matlab
#1084 (presentations anchored to their epoch; then the B1 carry and the Babu /
Soph workbooks). Merged: NDI #1081-#1083, #1085, #1086; did-schema #192-#207.
Claude merges each when CI is green and marks decision lines Built.

**Plan to finish:** (1) answers recorded every ~10; (2) pending builds
(`python3 tools/decision_citations.py --pending`) built in parallel, siblings
first; (3) measurement gaps closed (whole-batch round trip inverses per batch
pass, named statements, bath link counters); (4) final corpus run, each corpus
reported done / not done; (5) dataset reimports (Babu, Haley, Soph) with their
decision workbooks. The issue sort is `docs/v2_working/ISSUE_SORT_2026-10-27.md`.
#176 stays HELD for Jess.

1. (Decided 2026-10-27, [cell spellings are one meaning]: `spikes`, `neuron`
   and `cell` all become entity type `cell`, nothing else kept; the round
   trip counts them as equivalent. Build pending: DID-matlab.)
   Correction decided 2026-10-27: [cell spellings amended], [element type
   is a device kind term], [ndi element class not kept]. Builds pending.
2. **New EMPTY terms, rechecked** (Jess, 2026-10-27: "I'm surprised
   acquisition time, model fit, and bath solution doesn't already exist";
   "Multi-electrode array sounds better to me as long as it's genuinely the
   same thing. Any other terms we should rethink against the v2 tenets?").
   OLS4 and Wikidata, 2026-10-27:
   - i, ii, iii decided 2026-10-27: [afo prefix registered] (with an AFO
     reader in ndi-ontology-matlab), [n-trode is a multielectrode array],
     [site positions are coordinates]. Builds pending.
   - Model fit: closest is BAO:0000434 "curve fit specification" ("Has curve
     fit parameters, curve fit method, properties like Hill coefficient");
     Claude to read its full definition before proposing it.
   - Bath solution: only REPRODUCE-ME "Bath Solution" (no id, no
     definition, prefix not registered); stays a new term.
   - The other 36 element-type values get the same check before any is
     proposed.
3. (Done: NDI-matlab #1074 merged, 38adc701b.)
4. **Phase 2 pilot findings** (DID-matlab `claude/phase2`, subject family
   switched to raw v1 with its round-trip check, CI green):
   - a. (Decided 2026-10-27, [v1 name is the entity name]: a non-empty v1
     `base.name` goes to `entity.name`, equal or not; 0 of 1,918 corpus
     subjects differ. Build pending: DID-matlab.)
   - b. (Decided 2026-10-27, [fields outside the template are malformed]: carried whole as v1 under one generic row, carry-100.) A field outside the NDI template (e.g. a stray `subject.strain`):
     today dropped silently; the round trip now catches it. Carry as v1
     ([partly placed is carried as v1])? Which kind? [carry; malformed when
     no NDI writer writes it, else awaiting home]. The same question now
     comes up in every family (responses 15d; the ingested data cache,
     where the migrator now carries such a document with no register row
     yet). One answer, one generic register row ("a field outside the
     NDI template"), for all classes? [yes]
   - c. (Decided 2026-10-27, [member edge number is notation]: `subject_id`
     and `subject_id_1` are the same edge. Build pending: DID-matlab.)
5. (Done: did-schema #162 merged (4b63810); DID-matlab phase 1 merged as
   #251 (1f83af39), all checks and both corpus jobs green: the baseline.
   NDI-matlab #1075 (its one test update) merged too (d88ea6cfb).)
6. (Done; see 3. did-schema #161 merged too. #162 waits on 9: merged
   alone it turns DID-matlab V2 red until phase 1 lands.)
7. (Done: NDI-matlab phase 3 merged as #1076, 4effe11e0; it also finds ontology labels under either class name.) **NDI-matlab phase 3 was built** (branch `claude/phase3`, 471cd5c66; e2e
   run 40423825794, 499 passed, 0 failed; full suite run 40423865456, 2,366
   passed, 0 failed): the ingested stimulus reader finds the body,
   `chooseLevel` skips empty levels, element identifier `<name> |
   <reference>` (writer and reader; the old `(ref X)` form still reads),
   light-sheet axes matched by node. Open its PR (runs the NDI corpora
   once) once DID-matlab writes the new element identifier? [yes]
8. **Ingested stimulus lookup reads description text**: the body has no
   epoch field, so NDI finds it by the text `<epoch> <reader id> ...` in
   `data_body.description`. It works (tested), but a queryable epoch field
   or epoch time reference would be sturdier. Leave as is, or open a
   follow-up? [open a follow-up; not urgent]
9. (Resolved, no answer needed: the 6 failures were NDI's end-to-end run
   reading did-schema `main` before #162 merged, plus one NDI test still
   asserting the older untied-epoch rule; fixed on NDI-matlab #1075.)
   Proposed (not decided): NDI's end-to-end workflow reads a did-schema
   branch of the same name, as it already does for DID-matlab, so a
   paired push run is measured against its own schema. [yes]
10. **Both siblings now read either file name** (`did_v2_*` first, then
    `V_eta_*`): DID-matlab `claude/did-v2-names` (dbb5cc00, quick CI and
    fixtures green), NDI-matlab `claude/did-v2-names` (e9e0daab). These ride
    the phase PRs; then did-schema can rename its files.
11. **Phase 2, treatment family switched to raw v1** (DID-matlab
    `claude/phase2`, 15a87ee9, quick CI 40428032943 green; treatment,
    treatment_drug, treatment_transfer, virus_injection). The round trip
    found v1 values today's migration does not keep. Today's behaviour is
    kept until you decide. In plain terms:
    - a. `treatment_drug` start offset and duration (`administration_offset_time`,
      `administration_duration`) are dropped. Put them on the treatment's
      time (its end / duration)? [yes]
    - b. `virus_injection.virus_AdministrationPND` (age at injection, days
      after birth) is dropped. Keep it as the subject's age at the
      injection? [yes]
    - c. `treatment_transfer.method_ontologyNode` is dropped (the method is
      written by label only). Write the node as the method term? [yes]
    - d. NDI's treatmentMaker writes `location_ontologyName` where the
      template says `location_ontologyNode`, so the writer's site node is
      never read. Read the writer's spelling too ("the writer wins")? It
      changes output. [yes]
    - e. A site label is rewritten to the registry label ("V1" becomes
      "primary visual cortex"), so the writer's label is lost. Is that
      fine (the term node is the same), or keep the original label too?
      [fine: same node, [spelling is notation]]
    - f. `table2treatment`'s group link (`manipulation_id`) is read by no
      migrator. Where does it go? [Claude to look and propose]
    - g. A transfer with a clock type but no time (Babu writes NaN) loses
      the clock; a transfer with an empty method name gets "transfer", an
      invented value. Carry both as malformed? [yes]
    - h. Documents universalRenames used to carry (an old `ndi_document`
      block beside `base`) now convert and lose the extra block. Which
      register rows should catch them? [Claude to propose rows]
    - (No question: a document with no `base` gets random ids; fixed on
      `claude/phase2` d00e9c68 by `mintKey`.)
12. **Phase 2, element switched to raw v1** (DID-matlab `claude/phase2`
    d00e9c68, quick CI 40432385112 green; `element_epoch` not yet). It
    builds [element local identifier is name and reference], the element
    type decisions, sorted units and [dependents of a carried document
    carry]. Questions:
    - a. A document carried as v1 only so NDI's second pass can convert it
      (`stimulus_presentation`, the ingested stimulus file) does NOT make
      its dependents carry; otherwise every stimulus response would be
      carried. Right? [yes]
    - b. A multi-unit group's name: the decision says "the unit's name"; the
      build writes `<name> | <reference>` like every element. OK? [yes:
      the reference tells two units of one name apart]
    - c. Quality labels other than single / multi (e.g. kilosort "good",
      "mua") count as no label, so the unit is carried for a map. Or map
      "good" to single and "mua" to multi in the generic stage? [carry:
      their meaning depends on the sorter's settings]
    - d. A unit's `direct` flag and `subject_id` are not kept when it has
      an underlying element (both are recoverable from that element).
      Accept? [yes]
    - e. carry-055's description in the register still describes the old
      `(ref X)` form. Update it to `<name> | <reference>`? [yes]
13. **Phase 2, element epochs** (DID-matlab `claude/phase2` 548723df, quick
    CI green): the first step (v1 epoch to its carrier) reads raw v1 and
    round-trips with nothing lost. The later batch step (into epoch, time
    references, observation and data body) is not round-tripped.
    - a. Add a whole-batch round trip of the final V2 shape? [yes, in
      phase 5, before the final corpus run]
    - b. A colliding `depends_on` name still cites carry-049 (the old
      renames row); [renames carry is temporary] wants a class-specific
      row. Add one row per class as they come up? [yes]
14. **openMINDS subjects** (10,401 corpus documents; next after tuning and
    stimulus responses). [confirm sheet matches] makes each one a single
    term assertion, but the v1 documents also hold `openminds_id`,
    `matlab_type`, the term's definition and synonyms, and for a strain its
    `openminds_1..3` links and 14 fields. A round trip would report all of
    these lost. Keep them (where?), or accept them as recoverable from the
    openMINDS term itself? [accept what the openMINDS term itself holds
    (definition, synonyms); keep `openminds_id` as the term node; ask
    again for the strain links]
15. **Stimulus responses: every real one is still carried** (DID-matlab
    `claude/phase2-srs` c2869ab0, quick CI green; the family now reads raw
    v1 and round-trips). NDI's only writer always sets the stimulator epoch
    and the control link, and carry-050 carries any response that has
    either ("awaiting a home", OPEN_WORK #137). So all 10,124 corpus
    responses stay v1. This is the largest remaining gap after tuning.
    - a. Homes for the two links: see `docs/v2_working/HOMES_RESPONSES_TUNING.md`
      questions 1-2 (the stimulator epoch always equals the response's own
      epoch, 10,124 of 10,124, so it need not be stored; the control link
      becomes an input edge to the control-pairing calculation). [yes to
      both]
    - b. The parameters document becomes a `method` but loses
      `freq_response` (mean, F1, F2) on all 11,440. Make it a method
      parameter? [yes: it is how the response was computed]
    - c. A response the migrator cannot read (no element, unknown response
      type, empty readings, wrong-length stimulus ids, an epoch with no
      document) is passed through without a register row. Carry it with a
      row (malformed)? [yes]
    - d. A field outside NDI's template is dropped silently on conversion.
      Carry the document instead, as for subjects (4b)? [yes, same answer
      as 4b]
    - e. A prestimulus normalization of `[]` is written as 0
      ([empty response settings]), so the round trip cannot tell them
      apart. Accept, since you decided they mean the same? [accept]
    - f. A carried v1 response keeps its edge to its parameters document,
      which is now a V2 `method`. Is a v1 document allowed to point at a V2
      one? [yes: an edge is an id, and a mixed database is expected until
      every home is built]
16. **Tuning calculations: most are still carried** (DID-matlab
    `claude/phase2` 182b66ca, quick CI green; six classes read raw v1, and
    each writer's own output round-trips with nothing lost). From a survey
    of the corpus zips (not a corpus run): 6,148 orientation/direction and
    1,431 contrast-sensitivity documents convert, but all 34,690 tuning
    curves, 22,896 contrast tunings and 5,604 spatial / temporal frequency
    tunings are carried (carry-056, OPEN_WORK #143), because each holds a
    field V2 has no place for. Together with 15, this is most of what is
    left.
    - a. Homes for the missing fields: drafted in
      `docs/v2_working/HOMES_RESPONSES_TUNING.md`, questions 3-7, each
      answerable in one line (stimulus ids as a covariate, presentation
      numbers rebuilt from them, `log` in notes, the property list as
      conditions, three contrast metrics added to the fit, `abs` as a
      second calculation). Only question 7 changes the schema.
    - f. All 22,896 contrast tuning curves record the same spatial
      frequency (0.04), which matches an NDI writer bug fixed later
      (NDI-matlab 49a875c94: "all N_deal tuning curves were built at the
      first value"). They are probably duplicates. Migrate them as they
      are (lossless), and flag them for the Soph dataset map? [yes]
    - b. The calculation's input edges are kept in order but lose their
      v1 names. Keep the names? [keep them: the order is a writer habit,
      not a rule]
    - c. Method parameter names lose the difference between `_` and a
      space. Accept as notation ([spelling is notation])? [accept]
    - d. Template `hotelling2test` vs writer `Hotelling2Test`: the same
      field ([spelling is notation])? [yes]
    - e. The tuning migrators do not yet follow [method terms are general]
      or [Naka-Rushton is one function]; they need the EMPTY terms of item
      2. Build them as soon as item 2 is approved? [yes]
    - (No question: the writers live in NDIcalc-vis-matlab, which the
      sibling lock does not cover. Worth adding to the lock later.)
17. **A stimulus presentation's epoch is lost (found 2026-10-27; already
    merged in NDI-matlab V2).** NDI's second pass turns a v1 presentation
    into a manipulation anchored "during the session" and writes its epoch
    id nowhere in V2 (`stimulusPresentationToItem.m`: read only into the
    report; its lossless check never looks at the `epochid` block). Today
    all 1,428 corpus presentations could still be rebuilt indirectly (from
    the ingested stimulus file's description text, or from carried v1
    responses), but those routes are fragile, and NDI's own stimulus code
    (`tuning_response`, `decoder`) needs the presentation's epoch to turn
    stimulus times into recording times. The fix needs your choice:
    - (a) anchor the presentation to its epoch entity (which DID's epoch
      step already makes), as the stimulus model plan describes; the
      clock comes from `presentation_time.bin` when it is there, else the
      epoch's own clock;
    - (b) keep the session anchor and add an edge to the epoch entity
      (a did-schema change);
    - (c) carry every presentation as v1 until (a) or (b) is built.
    [(a): it is the plan's own shape, and an epoch anchor is what NDI's
    stimulus code needs. Until it is built, (c), so nothing is lost.]
    Also: the response plan stops storing `stimulator_epochid` because "the
    presentation carries it" (and `HOMES_RESPONSES_TUNING.md` question 1
    relies on that). That waits for this fix.
18. **Phase 2 progress** (no answer needed): 20 of 95 DID-matlab migrators
    read raw v1 (DID-matlab `claude/phase2` 5dab317d, quick CI green):
    subjects, treatments, elements, element epochs, tuning, stimulus
    responses, and the ingested data / sync family (13,124 corpus
    documents surveyed, every one round-trips). The sync mapping row
    (carry-036) now also keeps a mapping carried when a field would be
    lost; its description will be updated to say so.
19. **Images** (DID-matlab `claude/phase2-image`, quick CI green;
    `imageStack` reads raw v1; all 14,014 image documents are JH). None of
    the 7,007 corpus image stacks converts today: 2,444 Haley behaviour
    stacks carry (carry-052), 4,563 Haley E. coli stacks pass through with
    no register row, and their 7,007 labels follow them. Haley is covered
    by the Haley V2 import, so this is about Babu-style stacks and the
    record.
    - a. The 4,563 E. coli stacks (no subject) pass through with no
      register row. Cite carry-052 (or a new row) so every carry has a
      reason? [yes, carry-052]
    - b. When a writer labels the axes ("height", "width"), the axis
      letters (`dimension_order`, e.g. "YX") are kept nowhere: every Babu
      video loses them. Keep the letter on each dimension? [yes: it is how
      the data array is laid out]
    - c. An image-stack field the fold has no home for (and a non-empty
      `base.name`) is still dropped silently. Carry with a row, as for
      calculations (carry-056)? [yes]
    - d. Babu's importer writes a frame rate where the time axis wants a
      frame spacing (`+babu/import.m:445-446`), and Haley's E. coli
      importer may swap width and height (`doImport.m:782`). Importer bugs,
      for the Babu decision (open question 7) and the Haley re-run. [flag
      both; no generic change]
    - (No question: `ontologyLabel` can switch only after NDI reads the v1
      class name; that NDI change is queued with phase 3.)
20. **Spike sorting** (DID-matlab `claude/phase2` ee1b509a, quick CI
    green; 25 classes now read raw v1). From a survey of the corpus zips:
    all 210 Hartley calculations, 61 of 62 jrclust cluster files and all
    1,511 extracellular neurons convert. Questions:
    - a. A neuron's v1 document id ends up on no V2 document. Keep it
      (e.g. on its waveform calculation)? [yes: a v1 id other documents
      may cite is never dropped]
    - b. Waveform sample times are stored as start + step, which rebuilds
      them to about 1e-19, not exactly, on all 1,511. Store the times
      themselves when start + step is not exact? [yes]
    - c. The jrclust writer's file name `jrclust.prm` (`base.name`) is
      dropped on 61 documents. Carry instead, as in 4a? [same answer as 4a]
    - d. Each extracellular neuron also mints its own "cell" entity beside
      the sorted-unit element, which [sorted units are cells or groups]
      already makes a cell or group: two entities for one unit. Point the
      neuron at the element's entity instead? [yes]
    - e. The speed-tuning writer's three fits (full, no speed, full speed)
      would all be called "Priebe fit". Tell them apart by their
      constraints (as [Naka-Rushton is one function] does)? [yes; carried
      until then]
    - f. `simple_calc` (no corpus documents): model it or retire it?
      [retire: no NDI writer at main writes it]
    - (No question: the speed-tuning class was never converted before:
      the old rename pass missed its v1 name. It is now read correctly.)
21. **Acquisition systems** (DID-matlab `claude/phase2` e4c77e4c, quick CI
    green; 33 classes now read raw v1). All 1,129 corpus documents of the
    eight classes (DAQ systems, file navigators, readers, metadata readers,
    sync rules and graphs, probe locations) convert, and every one
    round-trips. Two questions:
    - a. (Decided 2026-10-27, [probe location terms]: the three rows are added.) Probe locations: three of the four brain-region terms used in the
      corpora (UBERON:0001880, UBERON:0002813, UBERON:0002812) are not in
      the term registry. Add them (existing ontology terms, T19 step 2)?
      [yes]
    - b. A sync rule between two acquisition systems becomes an unordered
      pair; which was "system 1" survives only in the order of its edges.
      Keep it explicitly? [yes, cheap and exact]
    - (Other questions here are the same as 4a / 4b: a non-empty
      `base.name`, a field outside the template.)
22. **Baths and position** (DID-matlab `claude/phase2` 25388d34, quick CI
    green; 36 classes now read raw v1). From a survey of the corpus zips:
    all 1,605 Dab baths convert; 2,078 JH positions stay carried (carry-053,
    and JH is covered by its own import); 2,078 JH distances follow their
    carried elements. Questions:
    - a. DID's bath step drops each bath's stimulator link and epoch on
      all 1,605 baths, while NDI's bath step keeps both. Keep them in DID
      too (as NDI does)? [yes: one bath step, NDI's shape]. Found
      2026-10-27: this is a real loss under [lossless means round trip] on
      all 1,605 Dab baths; nothing records which epoch a bath belongs to
      (the epoch string itself survives on the epoch entity). The "969
      dropped" in the corpus report was a counting bug and is being fixed;
      this bath link is the only real loss behind it.
    - b. 1,172 ACSF baths: the pH and osmolarity rows become the
      formulation's `ph` / `osmolarity` and lose their term ids and their
      place in the table. Accept? [accept: the term ids are fixed by the
      field name]
    - c. `distance_metadata` converts to a class marked "retire". Carry it
      instead until it has a V2 home? [yes]
23. **Sessions, datasets, forms, presentations** (DID-matlab `claude/phase2`
    3db719c0, quick CI green; 41 classes now read raw v1). From a survey
    of the corpus zips: all 53 sessions, all 48 dataset memberships (open
    question 11 above is now answered by the build), 4 remote-dataset
    records and 1 form convert; 1,428 presentations are carried for NDI's
    second pass. Questions:
    - a. A converted record's own v1 id is kept nowhere when its V2 form
      takes another document's id (each session entity takes the session
      id; also membership, remote, form records; and 20a, the neuron). Keep
      every v1 id somewhere, or accept it when nothing refers to that id?
      [keep: one rule for all, a v1 id is never dropped; Claude to propose
      where it is stored]
    - b. `control_stimulus_ids` cannot switch yet: NDI's second pass reads
      the control record from pass 1's output instead of from the v1
      input. Make NDI read it from the input (as it does presentations)?
      [yes]
    - c. The dataset form's subject / species / strain / sex lists are
      still dropped (an earlier decision). Still right under [lossless
      means round trip]? [carry the form when they are not empty, until
      they have a home]
    - d. A remote dataset's organization id (a cloud id) is written as the
      organization's name. Make it an identifier? [yes]
24. **Phase 2 nearly complete** (DID-matlab `claude/phase2` 2599d51, quick
    CI green: 2,015 run, 0 failed; 72 of 95 migrators read raw v1; every
    off-template carry now cites carry-100). The other 23 stay on the old
    path for now: 13 by choice or waiting on you (openMINDS, item 14;
    `simple_calc`, `image`; `control_stimulus_ids`, 23b), and 10 for
    reasons Claude can settle or that need code order (sibling code that
    still compares the old class name goes first, as for ontology labels).
    Questions:
    - a. A carry for a wrong VALUE (not an extra field), e.g. a probe with
      the wrong number of dimensions, a kilosort checksum in the wrong
      case, a measurement with no statement: these cite no register row.
      Add one generic row, "a value no NDI writer produces" (malformed),
      as you did for extra fields? [yes]
    - b. Four spike classes (spike waves, spike clusters, binned spike
      rates, filter settings) still pass through with their `app` block.
      Switching them means carrying them, and then everything computed
      from them carries too. Keep them on the old path until their `app`
      block has a V2 home? [yes]
    - c. `dataset_session_info`, `fitcurve`, `vmspikefit`: no NDI writer
      and no fixed template. Retire them like `simple_calc`? [yes]
    - (No question, Claude's call: the four NDIcalc-vis tuning classes take
      their templates from NDIcalc-vis-matlab 00e3e0f, the commit already
      used for the tuning family. Done: DID-matlab #255 (6bfbb25), so 76 of
      95 read raw v1 and 19 remain; see item 26. `file_reference`, the light-sheet zarr
      classes and `ontology_table_row` switch after their NDI / DID batch
      readers accept both class names. `pyraview` is done: DID-matlab #256
      (dfd73b6); the epoch step already re-ran it on the raw v1 source, so
      it needed no code change there. 77 of 95; see item 27.)
25. (Decided 2026-10-27, [move the locked mains]. Build pending: did-schema.
    Follow-up asked: merge `main` into V2 in NDI-matlab (86 commits, 3
    conflicts: session.m, +lightsheet/view.m, a cloud file deleted on main)
    and DID-matlab (34 commits, clean)? Decided 2026-10-27, [merge main
    into V2]. Build pending.)
26. (Decided 2026-10-27: a. [lock NDIcalc-vis-matlab]; b. [tuning stray
    fields are malformed]. Builds pending.)
27. (b, c decided 2026-10-27: [unreached superclass migrators deleted],
    [unknown filter parameter is malformed]. a asked again: no V2 redesign
    is needed; V2 documents carry DID's `files` block, and `pyraview.m:323`
    drops each level's `file_info` (its stored-binary uid). Copy it onto
    the level body? Decided 2026-10-27, [pyraview level keeps its file info].)
    **Pyraview, after its switch (DID-matlab #256).** Only PRED holds a
    pyraview (1 document); its counts are unchanged by the switch.
    - a. `files.file_info` (file location, uid, ingest flags) is on no
      emitted document: each level body keeps only its file name. This
      was already so before the switch. Is that a loss under
      [lossless means round trip], or is `file_info` database bookkeeping
      the V2 database rebuilds? If a loss, the level bodies should keep it.
      Claude's recommendation: treat it as a loss and keep it, until
      someone shows the database rebuilds it.
    - b. Nothing reaches the old superclass migrators
      `+migrators/epochclocktimes.m` and `filter.m` any more (at NDI's
      locked main, only `pyraview` names either as a superclass). Delete
      them? Claude recommends yes; it fits [early migration pieces fixed]
      (1).
    - c. `filter.parameters` is free in the template, and the migrator
      reads five keys. Should an unknown key in it carry the document
      (carry-100)? Claude recommends yes.

28. **Light-sheet and file references, after their switch (DID-matlab
    #257; no corpus holds these classes, so only unit tests measure them).**
    - a. Existing round-trip losses kept: a pyramid loses `byte_order` (its
      levels carry it); a level loses `label`, `dtype`, its `subject_id`
      and `source_file_id` edges, and a reduced level's index. Keep any?
      [keep all: lossless means round trip]
    - b. A `fileReference` carried as v1 (e.g. for an extra field) can still
      be folded into a store body by the batch pass. Exempt carried
      records from the fold? [yes]
30. **Tuning carry split, built (DID-matlab #260): two scope choices to
    confirm.** No corpus count changed (carry-056: 84 in 20211116, all
    `tuningcurve_calc`; carry-100: 0 everywhere that ran; Soph not run).
    - a. The split also covers `hartley_calc` and `contrastsensitivity_calc`,
      which share the tuning fold, though the decision names only the
      tuning family. Keep? [yes: carry-100 already applies to every class]
    - (a decided 2026-10-27, [tuning split covers the shared fold]; b
      decided, [writer fields over the template are template fields]; 26c
      decided, [ground truth reads NDIcalc-vis templates].)
    - b. Fields the writer writes but the template omits (e.g.
      `tuningcurve_calc.stim_property_list`, the speed `control_stddev`)
      count as template fields, so an unhomed one is carry-056, not
      carry-100 ("where a template and its writer disagree, the writer
      wins"). Keep? [yes]
29. (Decided 2026-10-27: a. [number of electrodes minted]; b. [site frame
    is a coordinate system]. Builds pending.)

## The goal

1. **The generic migration of v1 is lossless.** Every v1 document either
   lands in a V2 shape or is carried unchanged as v1. Nothing is dropped and
   nothing is invented. A value may be dropped only if V2 can be migrated
   back to v1 without it ([lossless means round trip]). The generic stage
   writes V2 only when the v1 document alone gives exactly one correct
   reading ([one correct reading]).
2. **Every carry has a reason on record.** Each reason is a row in the carry
   register (`schemas/V_eta_carry_register.json`, [carry register]):
   awaiting a home, needs a dataset mapping, not modelled, or malformed. An
   awaiting-home row must point at an open OPEN_WORK row
   ([awaiting home is tracked]).
3. **Carried documents are fixed later**, one of two ways:
   - a **V2 home**, a schema decision. Once it is built, the generic
     migration converts that case.
   - a **dataset map**, for meaning only that dataset knows. It runs after
     the generic migration and may also refine V2 documents the generic
     stage wrote ([dataset map edits V2]).

## Where we are

| step | state |
|---|---|
| Document stamps `did_v1` / `did_v2` | done |
| No invented values | done |
| Lossless rule: a partly placed document is carried as v1 | done (DID #247, NDI #1067) |
| Drop census: 14 questions | answered; decisions recorded (did-schema #128) |
| Census builds | done: did-schema #131, empty-ontology #26 and #27, DID-matlab #250, NDI-matlab #1072 |
| Dataset-specific logic out of the generic migration | done for Haley (covered by the Haley V2 import) and JH; **Babu is now covered by nothing** (see question 7) |
| Schema set renamed `did_v2` (did-schema part) | done (#132); siblings still accept both names |
| Carry register and its gate | done (did-schema #134) |
| Dataset map: may edit V2 documents; one file per dataset in NDI-matlab, its own step | decided (#141) |

## The road to a complete generic migration

Agreed by Jess Haley, 2026-10-26 ("This sounds like a good plan. Make sure
is documented somewhere."). The decisions it builds are [carry register],
[awaiting home is tracked], [migrators read raw v1], [renames carry is
temporary], [early migration pieces fixed] and [migration reliability
practices].

**Done** for the generic migration means, per corpus: integrity (nothing
quarantined, orphaned or fragmented) AND lossless (every v1 item converted
or carried unchanged as v1), AND every carry has a register row (the check
fails otherwise), AND every class passes its round-trip check, AND no
dataset-specific logic is left in the generic stage. Each corpus is
reported done or not done, with what is missing.

One PR per repository per phase; the quick CI on pushes; the corpora once
per phase.

| phase | repo | what | needs from Jess |
|---|---|---|---|
| 0 | did-schema | merge the carry register (#151) | the proposed row kinds (one batch); the narrow register questions, two at a time |
| 1 | DID-matlab | carry notes cite register rows, citation check strict; deterministic ids; carry counts by row; TermRegistry on during migration; stamp check; delete `resolveLawnPlateSubjects`. One corpus run: the baseline later runs are diffed against | nothing new |
| 2 | DID-matlab | shared raw-v1 reading helpers; each class switched to raw v1 with its round-trip check (one agent per class family, merged in turn); superclass migrators, old `+migrators` and `ensureClassBlocks` removed; declared pass order; `universalRenames` deleted | answers as classes raise them |
| 3 | NDI-matlab (beside 2) | second-pass carries cite rows; element name and reference stored reversibly (#142); declared pass order | the element shape (#142) |
| 4 | all, siblings first | `description` -> `notes`; retired classes leave; the `V_eta` name dropped; did-schema then removes the old shapes. Batched with phase 2's corpus run | nothing new |
| 5 | all | one final corpus run; each corpus reported done or not done | review |

The general questions below (bath variable, element entity types, 20211116,
ingested sessions, `chooseLevel`, the ingested-file lookup) are answered
alongside, two at a time.

## What's next, in order

1. **Carry notes cite the register.** DID-matlab and NDI-matlab make every
   carry note cite its register row (#134 is merged), with a test.
2. **Build the dataset map.** First the open design questions (below), then
   the step that applies a map, then the Dab map (sliceTetanus moves out of
   the generic second pass, [sliceTetanus to Dab map]). The design draft is
   `docs/v2_working/DATASET_MAP_PROPOSAL.md`.
3. **The remaining questions** below.
4. **The remaining renames**, siblings first: `description` becomes `notes`;
   the retired classes and `deprecated/` leave the V2 set; DID-matlab and
   NDI-matlab drop the old `V_eta` name. These take one more corpus run, so
   they are batched with the code the questions produce.
5. **Markdown out of `schemas/`**, once the delete list is approved
   (`docs/v2_working/MARKDOWN_PLAN.md`).
6. **Haley re-run** (Jess), then the remaining dataset maps.
7. **v1 set in did-schema** (decided): once NDI's V2 replaces v1, the v1
   definitions move into did-schema as a frozen `did_v1` set.

## Open questions for the team

Dataset map:

1. (Decided, [dataset map location]: one file per dataset in NDI-matlab,
   applied by its own step on the written V2 database.)
2. (Decided, [no Haley map]: no; the Haley V2 import covers Haley.)
3. (Decided, [map rows match exact values]: exact v1 values only.)
4. (Decided, [opto target without a run]: a term assertion on the animal
   stating its target; no stimulation claimed.)
5. (Drafted: `docs/v2_working/DAB_COLUMN_ROWS_DRAFT.md`; its Dab questions
   wait, see "Dab map questions (later)".)
6. (Moved to "Dab map questions (later)".)
7. Babu: a map, or a V2 import from the source data? Its media and heat
   routing is now covered by nothing.

Migration:

8. Bath variable: a bath statement's variable is the first mixture row
   (1,172 Dab ACSF baths say "sodium chloride"). One fixed generic variable,
   or the manipulated ingredient named by the dataset map?
9. Element entity types: should "device" be used only for direct
   acquisition elements?
10. 20211116: its 252 element epochs cannot be tied to an acquisition system,
    so they are carried. Option: keep the session-anchored reference when
    all of an epoch's extents come from one untied source and agree.
11. Ingested sessions: where does `session_reference` go, and what happens
    to an ingested session's creator class? 48 documents are carried until
    this is answered.
12. `chooseLevel` can pick a level that stores no bytes when two levels tie.
    Should it skip file-less levels?
13. NDI `get_ingested_document` looks up the ingested stimulus file by
    epoch id and reader id, which the converted body no longer has. Not
    checked.
14. openMINDS: the crosswalk has no technique or data-type entries, and a
    test note says dataset terms are "not openMINDS instance IRIs", which
    sits uneasily with T2.

## Capitalisation (later)

Raised by Jess Haley, 2026-10-26: should NDI terms be standardised to lower
case (unless proper nouns), since matching ignores case? Proposed (not
decided): keep the registry `name` as the ontology's label (checkable), and
either (a) lower-case only for display, or (b) add an `ndi_name` column that
writers use. Changing a stored name that code compares goes siblings first.

## Dab map questions (later)

Saved 2026-10-26 (Jess Haley: "Save the dab questions for later. Our goal is
general migration right now."). Draft: `docs/v2_working/DAB_COLUMN_ROWS_DRAFT.md`.

- EPM "CNO or saline" column: what was given in this experiment (the general
  question, a treatment with no amount, is asked separately).
- EPM `TestIdentifier`: what is it (2..29, empty in 17 rows)?
- EPM `ExperimentalGroupCode`: the importer's experiment number (1 or 2), not
  a treatment group: a cohort group entity, or a label?
- EPM `DataExclusionFlag` (animals 239, 258, "not expressing mCherry"): an
  assertion, an observation, or a note?
- FPS: its 7 open columns (in the draft).
- Dab: should Claude draft the remaining Dab map rows (sliceTetanus as a pass,
  the EMPTY:0000074 rule)?
- Where the Dab reproduction test lives (NDI or DID).

## Working documents

`docs/v2_working/` holds the research behind recent decisions. These are
proposals and measurements at the commits they name, not the record:

| file | what it is |
|---|---|
| `DROP_CENSUS.md` | the 14 drop-census questions |
| `carry_fields_TABLE.md` | which v1 fields blocked a fold (lossless carries) |
| `DATASET_SPECIFIC_AUDIT.md` | dataset-specific logic in the generic migration |
| `ONE_READING_REVIEW.md` | the one-correct-reading review |
| `TERMS_PROPOSAL.md` | the census terms proposal |
| `MARKDOWN_PLAN.md` | which Markdown under `schemas/` to delete or move |
| `DATASET_MAP_PROPOSAL.md` | the dataset map design draft |
| `DAB_COLUMN_ROWS_DRAFT.md` | proposed Dab map rows for the EPM and FPS table columns |
| `HOMES_RESPONSES_TUNING.md` | proposed V2 homes for the stimulus response and tuning fields that keep about 73,000 documents in v1 |
| `EMPTY_ASSAY_LABELS_PROPOSAL.md` | the list of pre-2026-10-20 EMPTY labels that carry assay context, each with an existing ontology term or a general relabel ([old EMPTY labels generalised]) |

## How we work

- Claude asks questions one at a time, or in small batches if they are
  simple, in plain terms, naming the document types.
- A decision is recorded only when a team member says it, in their words.
- DID-matlab merges before NDI-matlab. A schema change the siblings must
  follow lands in the siblings first.
- CI: pushes to a branch with no PR run the quick checks only. Open one PR
  per repository once its work is in, so the corpora run once.
