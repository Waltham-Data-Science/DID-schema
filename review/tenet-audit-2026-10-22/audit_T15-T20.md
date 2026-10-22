# Audit: V_eta (did-schema PR #88) against tenets T15-T20

Read-only. Nothing written under /home/user/DID-schema.

## Where and when this was measured

- did-schema `claude/ecstatic-pascal-md91fw` at `701a5de`. `git pull` printed "Already up to date."
- **The working tree changed while I was reading it.** Another process modified 7 files between 14:44 and 14:49 UTC: `V_eta_STATUS.md`, `V_eta_coverage_ledger.*`, `V_eta_data_body_model_plan.md` (it appended a `Decided by ... [index covariates]` line), `V_eta_decisions.json`, `V_eta_go_forward_class_audit.md` and `web/public/class_walkthrough.json`. I did not make these changes. None of the class files, the binding registry, the term registry or the tenets are among them.
- Sibling checkouts I used as evidence:
  - NDI-matlab: local `235801928`, which is behind `origin/claude/v2-object-layer` at `584b419`. I re-checked every NDI quote at `584b419`.
  - DID-matlab: detached at `8eec66a`.
  - empty-ontology: `claude/ome-zarr-format` at `214519f`.

## (D) Denominators

- **Classes:** `index.json` lists 168 rows in stable and draft. 5 are meta files, which leaves 163 classes:
  - stable: 69 persist, 7 in_progress, 70 retire;
  - draft: 17 persist.
- **Edges:** I scanned all 140 `depends_on` entries on the 163 classes by script. They use 70 distinct names. The 93 classes that are not retired carry 61 edges.
- **Fields:** I read the field lists of the 93 non-retired classes. For the 70 retired classes I checked only their edges.
- **Binding registry:**
  - relation_bindings: 34 rows, all read;
  - subject_statement_bindings: 11 rows, all read;
  - entity_type_bindings: 19 rows, all read;
  - entity_field_bindings: 1 row, read.
- **Term registry:** 508 terms, all `decided`.
  - I read the name and definition of 268 of them.
  - I did not read the 206 `wikidata:` terms (ethics jurisdiction countries) or the 34 `ILX:` terms (experimental approach) one by one; I only counted them.
- **`tools/check_term_registry.py`:** "DENOMINATOR: 508 term(s) ... R7: 112 EMPTY term(s) ... R8: 11 binding variable(s) ... FAIL: 4 problem(s)".
- **`tools/check_signoff_header_staleness.py`:** "65 markdown file(s) ... 34 carrying at least one TEAM-SIGN-OFF line ... No signed plan document claims to be unsigned. (34 checked)".

---

## HIGH

**H1. The `recorded_by` relation row cannot be stored as declared (B; T4/T15).**
- `binding_registry_meta.json` relation_bindings `recorded_by` says: `"child_types": ["epoch"], "parent_types": ["acquisition_system"]`.
- `directed_relation.json` `parent_id` says: `"must_refer_to_document_class": "entity,statement,value"`.
- `index.json` gives `acquisition_system` the superclasses `['base']`, so it is none of entity, statement or value.
- `acquisition_system.json` `device_id` documents it as: "The acquisition system itself is configuration -- which software reads which files -- not a thing in the world."

So the row's parent type and the edge's target class contradict each other.

**H2. The `member_of` row contradicts T20 and the entity-type registry (A/B).**
- T20 says: "the set is ONE entity of `type` group, with its finer kind as a term (cohort, ensemble, software pipeline, electrode array, ...), and each member is linked to it by `member_of`."
- The `member_of` row has `child_types` `["organism","culture","tissue","cell","group","device","material"]`. It leaves out `software`, so T20's own "software pipeline" (NDI-matlab #820) cannot pass this row.
- The same row has `parent_types` with those same 7 types, not just `group`. But:
  - entity_type_bindings `culture` reads "a mass grown as one, whose members are never entities";
  - entity_type_bindings `group` reads "an entity whose members are entities, by `member_of`".
- No decision line I found permits this.
- **Uncertain:** whether anything enforces `child_types`. A grep found `child_types` only in NDI-matlab `+migrate/+internal/ensembleMembership.m` (a comment: "must_refer is existence-only, never type-checked") and DID-matlab `+did2/+convert/resolveLawnPlateSubjects.m`. A grep that finds nothing is not evidence that nothing enforces it.

**H3. The tenet text says "not signed" for decisions that have been signed (C; CLAUDE.md "a plan's header is not its state").**
Six inline markers in `schemas/V_eta_tenets.md`, each with the line that signs it:

| tenet line | what it says | what signs it |
|---|---|---|
| 804, T17 | "Proposed amendment (2026-10-21 ... not signed)" | `TEAM-SIGN-OFF [tenet amendments 2026-10-21]`: "T17: one event given to several subjects is one distributive statement on a standing group" |
| 979, T20 | "Proposed 2026-10-21 at Jess Haley's request, not signed." | `TEAM-SIGN-OFF [tenet T20, group entities]` |
| 915, T19 | "Not signed." | `V_eta_term_registry_plan.md` `TEAM-SIGN-OFF [term registry]`: "tenet T19 (a term already used in an NDI dataset first, ...)" |
| 58, T2 | "proposed 2026-10-21, `V_eta_method_plan.md`, not signed" | `V_eta_method_plan.md` `TEAM-SIGN-OFF [method]`: "... T12/T13 amended" |
| 381, T12 | "not signed" | `TEAM-SIGN-OFF [method]` |
| 441, T13 | "not signed" | `TEAM-SIGN-OFF [method]` |

`check_signoff_header_staleness.py` reports none of these, because it checks document headers, not inline markers. That gap in the tool is itself a finding.

**H4. `ensemble` violates T15 and T20 (A).**
- `ensemble.json` (stable, `in_progress`) has the edge `"name": "neuron_id_#"` with `"multiple": true` and **no `ordered` key**. Its documentation says "in COLUMN ORDER ... the `_1`/`_2` suffix is the column index".
- This breaks three rules:
  - T15: "A repeated edge repeats its name; it is never numbered."
  - T15: "Every repeated edge states **`ordered`**."
  - T20: "Order is never encoded in ids, in edge-family numbering, or as a list of ids on the referencing statement."
- T20 and entity_type `group` ("a cohort, an ensemble") say an ensemble is a group entity.
- T15's exemption covers only "did_v1 tombstones". This class is not in `deprecated/`, and no decision line exempts an `in_progress` class.
- It is the only non-retired class out of the 93 with a numbered edge or a repeated edge without `ordered`. The other two such edges are on retired classes: `daqsystem.daqmetadatareader_id_#` and `syncgraph.syncrule_id_#`.

## MEDIUM

**M1. The `developmental stage` binding conflicts with T19's own example and with how the Haley import uses it (B).**
- The binding row reads `{"variable": "developmental stage" NCIT:C43531, "class": "assertion", "ontology": "UBERON", "root_node": "UBERON:0000105"}`.
- T19 says: "`L4 larva` is WBls:0000038". The registry holds it as `WBls:0000038` "L4 larva Ce". A WBls term is not under the UBERON root.
- NDI `import_V2_spec.json:2153` (at `584b419`) says: "One term observation per cohort ... Distributive ... Terms (haleyTerm): developmental stage NCIT:C43531, L4 larva Ce WBls:0000038 ..., visual inspection NCIT:C214703". So the import writes an observation with a method, while the binding names `assertion`.
- **Uncertain:** whether did2.build checks the subtree. `grep root_node` over DID-matlab `.m` files found nothing, which is not evidence either way.

**M2. The `Gene Expression` binding points at a retired class (B).**
- The row reads `"class": "spatial_gene_expression_pyramid"`.
- `index.json` lists that class as stable, `retire`.

**M3. T15's vocabulary paragraph and table are stale (C), and T15 contradicts itself.**
- The paragraph lists `subject_id`, `strain_id` and `method_parameters_id` among "14 names ... unchanged by T15". None of the three is among the 70 edge names on the 163 classes.
- The table has four stale rows:
  - `data` → `key_labels_id`, but `data.json` has `key_id`. T15's own bullet a few lines earlier says "`key_id` (... `key_labels_id` / `labels_from` until 2026-10-05)".
  - `timed_sequence` → `item_id`: the class is now `item`.
  - `strain` → `background_strain_id`: no such edge exists.
  - `method_parameters` → `parent_id`: the class is now `method`.
- The header says "BUILT ... (`tools/build_v_eta.py` section 12.7)". That script is deleted (CLAUDE.md §3).

**M4. Registry terms against T19's own wording (A, partly uncertain).** All of these were decided by Jess Haley; none of the decisions states an exception to T19.
- **EMPTY:0000350 "signed distance from the nearest bacterial patch edge"** (decided 2026-10-20, "Haley import audit"). T19 says: "`reference point` = `nearest bacterial patch edge` ... What generalises is the frame (`distance`, `reference point`)". The registry also holds `distance` (PATO:0000040) and `Reference Point` (NCIT:C45793). So one meaning is stored two ways.
- **EMPTY:0000286 "distance end point"**, defined as "paired with the reference point (NCIT:C45793) it is measured from". T19 says: "A qualifier that only makes sense attached to another entry belongs inside that entry's term, not beside it."
- **EMPTY:0000140 "encounter onset time"** sits beside **EMPTY:0000368 "onset time"**. The second comes from data_body plan `Decided by ... [onset time]`: "Stimulus is redundant?". The same reasoning applies to "encounter". These are near-duplicates.
- **EMPTY:0000122 "arena diameter"** and **EMPTY:0000120 "bacterial patch volume"**. T19's last paragraph says: "a quantity only ever planned (a patch volume of 0.5 µL) keeps its plain term ... its variable stays general (`diameter`)". **Uncertain:** whether the arena and patch are the statement's entity in the import, which is what would make the class word redundant.

**M5. The relation and entity-type vocabularies are outside the term registry and T19's order (C).**
- 29 of the 34 relation_bindings rows have `"node": ""`.
- None of the 34 relation names is in `V_eta_term_registry.json`.
- Every `entity.type` value has `"node": ""`.
- The registry's description limits its scope to "a variable, method, unit, condition, parameter or key".
- T19 says: "A term reached at step 2 or 3 is registered before it is used."
- No tenet says whether relation and entity-type terms are exempt.

**M6. Distance is modelled two ways (B).**
- relation_bindings has `measured_distance_to` ("the measured-from subject" / "the reference subject").
- The registry carries distance as a statement variable with a reference-point condition (M4).
- `V_eta_distance_metadata_plan.md` says: "The `measured_distance_to` term stays in the registry for Part B's use". By T16 a distance is a property (a `variable`), not a relation.

**M7. Binding variable names do not match the registry's labels (B).**
- `check_term_registry.py` R8 prints these without failing:
  - "'species': NCIT:C45293 registered as 'Species'"
  - "'developmental stage': NCIT:C43531 registered as 'Developmental Stage'"
- NDI `import_V2_decisions.md` #100 records the rule: "A term's stored name is the ontology's label".

**M8. Edges on in_progress classes use the v1 word "element" (A, T15).**
- The edges are `acquisition_epoch.element_id` → entity, `ensemble.element_id`, `ensemble.element_epoch_id` → acquisition_epoch, and `stimulus_presentation.stimulus_element_id` → entity.
- T15 says: "Name it for its target class ... or for its role". "element" is neither a V_eta class nor an entity type (the 19 types are listed in entity_type_bindings).
- Separately, the epoch is modelled both as entity type `epoch` and as the class `acquisition_epoch`:
  - `ensemble.element_epoch_id` → `acquisition_epoch`;
  - `epoch_id` on `directed_relation`, `method` and `ingestion_manifest` → `entity`.

## LOW

**L1. Stale prose with retired names (B).**

| where | quoted text | why stale |
|---|---|---|
| `binding_registry_meta.json` `notes` | "e.g. mass_observation, dose_manipulation, term_assertion" | retired leaf classes (T3) |
| same | "Abstract types (entity, subject)" | retired subject class |
| same | "ordered marks terms where the directed sequence field is meaningful" | the field is `order` (T20 rename) |
| `statement.json` and `directed_relation.json` `distributive` | "`subject.type` group" | should be `entity.type` |
| `index.json` `notes` | "subject_relation documents, restored subject_statement/subject_assertion ... term_observation" | retired names |
| `ensemble.json` `neuron_id_#` | "Typed to `subject`" | retired subject class |
| `V_eta_term_registry.json` `description` | "tools/build_v_eta.py copies it" and "or key" | script deleted; keys replaced by AMENDMENT 6 |
| `V_eta_duplicate_entities_plan.md` "Where it is stored" | "like the `part_of` relations that make a session a member" | superseded by `included_in` (`TEAM-SIGN-OFF [relation inheritance]`). The T18 text in the tenets was updated; the plan was not. |

**L2. Two relation names and their endpoint types.**
- `orthologous gene mapping` and `gene alias mapping` contain spaces; every other relation name is snake_case.
- Their `child_role` "the mapped gene list" does not match `child_types ["term"]`.

**L3. `study design independent variable` row has no admissible set.**
- The row is term-valued but has no `values` and no `ontology`/`root_node`.
- The binding notes say: "Only a term-valued leaf carries an admissible-set spec (values or ontology+root_node)".
- R9 prints: "any registered term".

**L4. `contained_in` is unconstrained.**
- It has `child_types: []` and `parent_types: []`, so a record could be `contained_in` another record and receive `context`.
- T5 says `contained_in` is for "a separate thing located in or on it"; T17 says "records use `included_in`".

**L5. `om:RelativeHumidity` has the wrong definition.** It reads: "Mass flow is the movement of substances at equal rates or as a single body."

**L6. `material type` mixes physical kind with use (uncertain).**
- The closed values mix a kind (`Petri Dish` NCIT:C96141) with uses: `assay plate`, `acclimation plate` and `food deprivation plate` (EMPTY:0000319-0000321).
- "food deprivation plate" repeats what the `food availability` = `fasting` manipulation (T16 worked example) states.
- This may be against T19 ("names nothing the document already carries") and T7.

**L7. Second shapes for decided single shapes.**
- `frequency_filter` (persist) is a method by another shape: `algorithm` term plus typed setting fields. It is not in `V_eta_method_plan.md`'s touch list, which decided "One `method` shape".
- `acquisition_epoch.storage.format` is `char`, while `data_body.format` is an ontology term ([format is an ontology term]).
- `acquisition_epoch` copies `data`'s `dimensions` and `covariates` without deriving from `data`. Its own documentation acknowledges this: "the class does not derive from `data`".

**L8. Two edge names for one target.** `acquisition_system.device_id` and `interaction.instrument_id` both point at a device entity.

**L9. R7 fails for four EMPTY terms (a property of the checkout).**
- The output reads: "FAIL R7 EMPTY:0000366 ... 0000367 ... 0000368 ... 0000369: not in empty-ontology", against the local empty-ontology `claude/ome-zarr-format` at `214519f`.
- The registry entry for 0000368 says: "minted in empty-ontology PR #24, not yet merged".

## (C) Tenet gaps and conflicts

- **T15 vs T20 on ordered lists of entity ids.**
  - T15 allows repeated ordered edges: `dose.ingredient_id` and `formulation.ingredient_id` (→ `chemical,formulation,entity`, `ordered: true`).
  - T20 forbids order "as a list of ids on the referencing statement".
  - T20's boundary ("a sequence that IS the data") does not say whether paired ingredient lists qualify.
- **T20 covers sets of entities only.** `interaction_purpose.interaction_id` (`in_progress`, multiple, unordered) and `calculation.input_id` are sets of statements. No tenet says when those become a unit.
- **T18 has no place for a device serial number.** It names "the same serial number (and manufacturer) on two devices" as evidence for `same_as`. Across all 163 class files and the 508 registry terms, "serial" appears only in `spatial_gene_expression_pyramid.chip_serial` (retired) and `syncrule_mapping` documentation ("SERIALISED"). `entity.global_identifier` holds CURIEs or IRIs. **Uncertain:** whether `local_identifier` or an IRI is meant to carry it.
- **No tenet covers relation or entity-type term vocabulary** (M5).
- **T15 covers only edges.** The field name `order` means a position on `directed_relation` and the filter order on `frequency_filter` (line 838). Nothing covers field names that collide like this.
- **AMENDMENT 6 is reflected in the tenets** (lines 63, 225, 551-560). The exception is T15's table (M3), against the decision [tenets follow covariates].

## What matched (positive evidence)

- **T17 `passes` table vs the registry.** All 34 relation rows match: `assertions` = part_of, sample_of, aliquot_of, passage_of, instance_of; `distributive` = member_of; `context` = contained_in; `nothing` = all others, including `included_in`, `same_as` and `paired_with`.
- **T15 on non-retired classes.** Every edge on the 93 non-retired classes except `ensemble.neuron_id_#` ends in `_id`. Every repeated edge declares `ordered`.
- **T20.** `directed_relation.order` exists and is documented as "Named `sequence` until the T20 rename". `member_of` has `ordered: true`.
- **T18.** `same_as` is undirected, has `member_types ["entity"]` and passes `nothing`.
- **T16.** `statement.variable` documentation says "never the act (T16)". `assertion` carries no `method`.
