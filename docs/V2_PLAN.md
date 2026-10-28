# V2 migration plan

This is the working plan, not the record. Decisions live in their `Decided by`
lines, mostly in `schemas/V_eta_go_forward_class_audit.md`. Open work is
indexed in `schemas/V_eta_OPEN_WORK.md`. When this file and either of those
disagree, they win.

Last updated 2026-10-27.

## Waiting for Jess

### Held and open (updated 2026-10-28, while Jess is away)

**Questions for Jess (answer in one line each):**

- **D1. Device kinds with no existing term (held 46/47).** Wikidata was reached
  2026-10-28 through its SPARQL service (the search API answers HTTP 429 here).
  It has **no** item for patch pipette, sharp electrode, an electrical
  stimulator, lick spout / lickometer, reward port or the cell-attached
  recording mode (only scholarly articles and patents matched; Q2705516
  "micropipette" is a liquid pipette, Q176366 "patch clamp" is the technique).
  OLS4 had none either (2026-10-27). Proposal: mint EMPTY terms for these six
  now, each with a one-line definition brought for approval; add a Wikidata id
  later as `equivalent` if one appears. [yes]
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

## How we work

- Claude asks questions one at a time, or in small batches if they are
  simple, in plain terms, naming the document types.
- A decision is recorded only when a team member says it, in their words.
- DID-matlab merges before NDI-matlab. A schema change the siblings must
  follow lands in the siblings first.
- CI: pushes to a branch with no PR run the quick checks only. Open one PR
  per repository once its work is in, so the corpora run once.
