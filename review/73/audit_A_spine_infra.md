# Audit A — spine, entities, time, bodies, infra (44 persist classes)

**Denominator.** 44 of 44 scoped classes read in full from the built JSON (every field, nested field, edge and documentation string), plus `image.json` and `did_schema_meta.json` for two cross-checks. Yardstick: `V_eta_tenets.md` and `V_eta_spatial_transcriptomics_plan.md` read in full. Seven plan documents read in the sections that bear on these classes, each to its last dated amendment: `data_body_model_plan`, `method_parameters_plan`, `epoch_plan`, `time_reference_model_plan`, `clock_alignment_cluster_plan`, `subject_calculation_plan`, `daq_family_decisions` (the last only via grep). That is 9 documents. Plan docs I did not open for any class are not evidence either way.

**Summary.** 45 findings: 4 VIOLATION, 16 INCONSISTENCY, 11 STALE-DOC, 14 QUESTION. #31 is counted as STALE-DOC; it is also an inconsistency. The pre-found items are not re-reported. Where I add judgement to one, it is marked *(judgement on pre-found)*.

The most severe, in brief:
- The built schema contradicts three signed decisions: `subject_interaction.sample_time` still exists, the inline `method_parameters` is a free-form bag, and `conditions` was never restructured.
- A standalone `data_type` document (item 19) has nowhere to put its `datum_type` or its `storage_mode`.
- The same facts are modelled twice: the run environment (inline block and entity edge), the device channels (inline field and document), and the rig (`instrument_id` and `acquisition_system_id`).

---

## subject_interaction

1. **VIOLATION — `sample_time` is still declared.** Schema: `stable/subject_interaction.json` `fields[sample_time]` {kind, dt, n, offsets}. Signed: `V_eta_data_body_model_plan.md:648` TEAM-SIGN-OFF [data_body] says *"time becomes an ordinary axis and both sample_time blocks retire"*. Build step 5 (`:519`) reads *"retire sample_time from both schema sites."* The build admits the gap at `tools/build_v_eta.py:6486`: *"The STATEMENT-side `subject_interaction.sample_time` ... is still declared, and is still written by nine call sites across both repos."* It also duplicates `keys` ("Time is an ordinary key"). *Suggestion:* convert the nine writers, then delete the field. Until then, track it as a named open row, not only a build comment.
2. **STALE-DOC — `sample_time` doc points at a field that no longer exists.** It says *"For body-backed values the cadence lives in sampled_body.sample_time instead."* `draft/sampled_body.json` declares only `keys, complete, byte_order, datum_order`, and `build_v_eta.py:6473` says *"`sample_time` IS GONE FROM THE BODY"*. *Suggestion:* point the doc at `sampled_body.keys`.
3. **VIOLATION — inline `method_parameters` is an untyped free-form structure.** Schema: `fields[method_parameters]` is type `structure`, `mustBeScalar: true`, and has no sub-fields. Its doc says *"free-form (the knob set varies per calculator)"*. Signed: `V_eta_method_parameters_plan.md:7` says *"the settings shape is a `parameter[]` entry ... it keeps the field name `method_parameters` in BOTH mount points, inline on `subject_interaction` and in the document"*. `:697` repeats it: `subject_interaction.method_parameters[*].variable  inline`. This also breaks the T13 rule "No untyped {name, value} bags" and T14. The document form (`method_parameters.method_parameters`) is the declared `variable/value/term/text` list, so the two mount points the plan calls "the SAME field name and shape" (`:504`) now differ. *Suggestion:* give the inline field the same declared `parameter[]` shape.
4. **STALE-DOC — `method_parameters` doc scope.** It says *"Optional configuration of a COMPUTED value's algorithm ... Present only when `method` names an algorithm ... Lives on the packet-head observation, once per calculation."* The signed plan applies it to any interaction's settings, and routes them per class (`method_parameters_plan.md:618-623`). T2 (#73, `tenets.md:46-54`) removed "computed observation". *Suggestion:* rewrite as "the settings this run used; inline form of `method_parameters`".
5. **INCONSISTENCY — the run environment is modelled twice.** `fields[execution_environment]` is {os, os_version, interpreter, interpreter_version}, signed R1 (`V_eta_tenet_audit.md:10`). `subject_calculation.depends_on[runtime_environment_id]` is a REQUIRED edge to the `runtime_environment` entity, which has the same four fields (signed #67 item 3, `subject_calculation_plan.md:271`). Every calculation inherits both, and nothing says which one wins. The team already ruled against this for settings ("one fact, one place", `subject_interaction.depends_on[method_parameters_id]`). *Suggestion:* retire the inline block or state precedence. This is a team call.
6. **STALE-DOC — `software_id` doc.** It says *"populated on calculations, optional on computed observations"*. T2 (`tenets.md:52-53`) says *"there is no 'computed observation'"*. *Suggestion:* drop the clause.
7. **INCONSISTENCY — the rig is an `acquisition_system_id` here but an `instrument_id` on `epoch`.** `subject_interaction.depends_on[acquisition_system_id]` → `acquisition_system` sits beside `instrument_id` → `subject`. `epoch.depends_on[instrument_id]` → `entity` says *"an epoch's instrument may be an `acquisition_system`"*. So the same rig plays the instrument role on an epoch and gets its own dedicated edge on an interaction. *Suggestion:* pick one edge for "the rig" across both classes.
8. **INCONSISTENCY — the channel half of a devicestring is modelled twice.** Inline: `subject_interaction.fields[channels]` {type, numbers}. As a document: `acquisition_channels.fields[channels]`, with the identical shape and the same doc ("ai | ao | di | do (daqsystemstring.m:53-56)"). Both `channels.type` fields are unbound `ontology_term`s carrying a documented four-value enum. `subject_interaction.channels.type` is not in the pre-found unbound list. Compare `frequency_filter.algorithm/band`, which bind their enums as `value_set`. *Suggestion:* bind `type` to a value_set, and ask whether interactions should reference an `acquisition_channels` document instead.

## subject_statement

9. **VIOLATION — `conditions` was never restructured, and still allows per-reading arrays.**
   - Signed: `data_body_model_plan.md:648` says *"conditions tightens to cardinality 1"*.
   - Amendment 2 (Team, 2026-08-14, `:1009-1020`) says `unit`, `source_unit` and `approximate` move up beside `variable`, `count` flattens to `{ value : integer[] }`, and `quantity` becomes `{ value:double, source_value:double }[]`.
   - Built: `conditions` has no top-level unit/source_unit/approximate. `count.value[]` is still `{value, unit, approximate}`, and `quantity.value[]` is still `{source_unit, source_value, approximate}` with no canonical `value`.
   - Every `*.value` doc says *"length 1 (a constant condition) or the measurement's value length (one label per reading)"*.
   - The top-level doc keeps the sentence the plan rejects at `:191-205`, *"same kind of thing, distinguished only by cardinality"*. That sentence is confirmed.
   - *Suggestion:* build the Amendment 2 shape and cap every value at length 1.
10. **VIOLATION *(judgement on pre-found)* — `keys.unit` is unbound against a signed "BOUND".** The pre-found item lists it as unbound. The plan goes further: Amendment 1 (`data_body_model_plan.md:898-911`) says *"`unit` ontology_term ... BOUND, NOT FREE TEXT, and that distinction is the whole reason this is safe"*. The same passage calls `conditions.count.value.unit` *"a BOUND `unit`"*, and that field is also unbound. The same applies to `sampled_body.keys.unit` and `image.value.keys.unit`. *Suggestion:* add the binding, even at `preferred` strength.
11. **INCONSISTENCY — a standalone data_type document cannot declare its encoding or storage.** `datum_type` and `storage_mode` exist only on `subject_statement` (grep: `datum_type` appears only in subject_statement, sampled_body docs and image docs). Item 19 says *"Every data type is concrete ... a standalone data-type document"*. Item 20 says a body's owner *"may be a statement or a standalone data-type document"* (`data_body.owner` → `subject_statement,data_type`). Yet `image.value` says *"The pixel TYPE is `subject_statement.datum_type`"*, and `image.value.pixels` is *"populated iff storage_mode:inline"*. A standalone image, or a body-owning gene list, has neither field. `image.value.keys.labels_from` also names *"an `axis_labels_#` edge on this document"*, and `image` declares no such edge. *Suggestion:* decide where `datum_type`/`storage_mode`/`axis_labels_#` live for a standalone value: on `data_type`, or on the body. Team call.
12. **QUESTION — do the `keys` of a referenced value live on the statement or on the referenced document?** `keys` doc: *"Populated when the value is INLINE or behind a REFERENCE"*. That follows the 2026-08-14 addendum (`data_body_model_plan.md:835-840`): *"reference -> one external payload, one extent -> axes on the statement"*. Item 19 later changed what a reference IS: a standalone data_type document, which carries its own keys (`image.value.keys`). The addendum's own rule, *"Axes live with the thing whose extent they describe"*, now points at the referenced document, so a referenced image has keys in two places. *Suggestion:* re-ask the addendum question under item 19.
13. **QUESTION — `storage_mode` doc says "assertions are always inline".** `subject_statement` declares `value_id` for every statement, and amended T6 (`tenets.md:132-137`) says *"each statement that uses it points at it by its `value_id` edge"*. Item 21 avoids a `term_assertion` for the gene list, but only because no subject fits, not because assertions cannot reference. *Suggestion:* drop or justify the sentence.
14. **INCONSISTENCY — `keys.regular` is required in the plan, optional in the build.** Signed entry (`data_body_model_plan.md:121`): `regular  boolean  REQUIRED`. Built: `mustBeNonEmpty: false` on both mounts, with default `false`, so an absent flag silently reads as "irregular". *Suggestion:* require it, or record why not.
15. **QUESTION — `axis_labels_#` → `base` is broad now that unions exist.** `did_schema_meta.json:130` allows a comma-separated class list, and `directed_relation`/`data_body` use one. Item 28's referent is a statement. *Suggestion:* consider `subject_statement,data_type`.

## epoch

16. **INCONSISTENCY — the reason for `instrument_id → entity` has lapsed, and T7 disagrees with it.** `epoch_plan.md:832` says *"`must_refer_to_document_class` is a SINGLE class name. A union is not expressible."* The meta-schema now allows unions (`did_schema_meta.json:130` pattern `...(,[a-zA-Z]...)*`). Amended T7 (`tenets.md:146-147`) says *"The measuring/manipulating device is a subject ... linked by a typed `instrument_id`"*, while `epoch_plan.md:855` decides *"`acquisition_system` is NOT ⊂ subject"*. The plan itself leaves it open at `:869-870` ("Still a #32 item"). *Suggestion:* target `subject,acquisition_system`, and amend T7 to admit a non-subject instrument, or reverse the plan. Team call.
17. **INCONSISTENCY — `session_id` names two different ids.** `base.fields[session_id]` is a `did_uid` field, *"Unique identifier of the session this document belongs to"*. `epoch.depends_on[session_id]` and `clock_alignment_policy.depends_on[session_id]` are edges to the session DOCUMENT. `relative_time_reference.depends_on[relative_to]` states that these are *"a different, freshly minted uid"*. So one document carries two `session_id`s with different values. *Suggestion:* rename the edge, e.g. `session_document_id`, or record which one wins.
18. **STALE-DOC — `time_reference_#` doc says *"the `_1`/`_2` index means nothing on its own"*.** The same text appears on `subject_interaction` and `directed_relation`. T14 (`tenets.md:322-323`) says families are numbered from 0 (`time_reference_0`). *Suggestion:* say `_0`/`_1`.
19. **QUESTION — `epoch.time_reference_#` targets `relative_time_reference`, not `time_reference`.** The doc says *"One entry per (clock, extent) pair"*, and the clock set includes `utc`. `subject_interaction` and `directed_relation` target the root. *Suggestion:* confirm the narrowing is intended, or widen it to the root.

## data_body / sampled_body / opaque_body

20. **STALE-DOC — `content_hash` doc says *"the algorithm is not declared by this field and is not recoverable from it"*.** `hash_algorithm` now sits beside it (item 25). *Suggestion:* cross-reference `hash_algorithm`.
21. **STALE-DOC — `format` example `'tiff'` and `compression` "Empty when ... uncompressed".** Decided 2026-08-14 (`data_body_model_plan.md:746-750`): an IANA media type, a closed enum including `none`, and *"**NOT file extensions**"*. *Suggestion:* drop `'tiff'`, use `none`, and bind both once the corpus sweep lands.
22. **QUESTION — where does an unheld body's location live?** Item 25 says it is *"recorded by location, not ingested"*, and the `body_data` doc says the same. No field declares the location: `filename` is *"Original filename of the payload"*, and item 34 moves the "not held" marker to DID-matlab. T14 asks whether a reader can learn this from the schema alone. *Suggestion:* declare it, or name the DID file-series mechanism in the doc.

## directed_relation / relation / undirected_relation

23. **STALE-DOC — `directed_relation.time_reference_#` cites `event_relative_reference`.** `index.json` has no class of that name, and the time family is `absolute_time_reference`/`relative_time_reference`. *Suggestion:* reword it as "a relative_time_reference whose `relative_to` is this relation".
24. **INCONSISTENCY — timing and epoch scope are declared only on `directed_relation`.** `relation.method` was hoisted *"so undirected relations have it too (item 24)"*. `time_reference_#` and `epoch_id` stay on `directed_relation`, and `undirected_relation.entities_#` still targets only `entity`, while the directed endpoints now accept `entity,subject_statement,data_type`. *Suggestion:* apply the same parity argument, or record why undirected relations are timeless.
25. **QUESTION — the index base of `directed_relation.sequence` is undeclared.** T14 says *"every index is 0-based"*, and cites `sequence` as the place v1 numbering is restated. The doc ("author position") does not say which base. *Suggestion:* state 0-based.

## method_parameters

26. **STALE-DOC — the `method_parameters` field doc still says `axes`.** *"exactly as `axes` mounts on two classes"*; *"three variable-keyed lists (conditions, axes, method_parameters)"*. Item 14 says `axes → keys` in all four places. *Suggestion:* say `keys`.
27. **INCONSISTENCY — the settings list is required in the plan, optional in the build.** Plan FINAL MODEL (`method_parameters_plan.md:504`): `method_parameters  parameter[]  REQUIRED`. Built: `mustBeNonEmpty: false`. *Suggestion:* require it, or amend the plan.
28. **STALE-DOC *(judgement on pre-found)* — `variable` doc says *"BOUND, and UNIQUE within the list"*.** It carries no binding. The doc claims more enforcement than exists, which is the reassuring direction. *Suggestion:* say "to be bound".
29. **QUESTION — `other` is an untyped structure.** T13 (`tenets.md:281-288`) says *"No untyped {name, value} bags"*. The signed plan keeps `other` for the long tail (`:505`). It is a document class, not a composite, so T13's scope is arguable. Team call.
30. **QUESTION — `derived_from_id` reuses the `derived_from` word for lineage between settings documents.** Item 27 keeps `derived_from_#` *"statement-inputs-only"*, and item 22 models content lineage as a `directed_relation derived_from`. *Suggestion:* confirm this third use is intended.

## clock_alignment_configuration / clock_alignment_policy

31. **STALE-DOC + INCONSISTENCY — the channel-pair cardinality.** The `acquisition_channels_#` doc says *"EXACTLY 2 and UNORDERED"*. Amendment 1 (`clock_alignment_cluster_plan.md:625`, 2026-08-18) changed it to *"cardinality {0, 2}"*. Built: `min_count: 0, max_count: 2`, which also accepts 1. So the real rule lives only in prose (T14). *Suggestion:* fix the doc to {0,2}. Add a meta-schema way to exclude 1, or a named validator check.
32. **QUESTION — `clock_alignment_configuration` vs `method_parameters` is still open.** `clock_alignment_cluster_plan.md:362-365` records them as structurally identical, unresolved. The same shape recurs in `acquisition_reader.reader_string` and `epoch_file_pattern`. *Suggestion:* answer it deliberately, as the plan asks.

## strain

33. **INCONSISTENCY — docs claim bindings the schema lacks.** None of these is in the pre-found list:
    - `species`: *"Bound to NCBITaxon"*, `constraints: {}`.
    - `breeding_type`: *"openMINDS BreedingType"*, `constraints: {}`.
    - `genetic_strain_type`: an enum-like term, `constraints: {}`.
    - `disease_model`: unbound.
    `dataset` declares exactly this kind of openMINDS binding (`{"vocabulary":"openMINDS","term_set":...}`). *Suggestion:* add the bindings, `preferred` if not yet measured.

## coordinate_system

34. **INCONSISTENCY — `origin` is called "the same concept as a key's origin", but the two are different types with different meanings.** `coordinate_system.origin` is an `ontology_term`: *"WHICH point ... is zero"* (item 5-9). `keys.origin` is `{value, source_value}`: *"Where the axis starts"*, a coordinate value. Separately, `dimensions.spacing` is a `length` cell while `keys.spacing` is `{value, source_value}` with the unit on the key. *Suggestion:* drop the "same concept" sentence or rename one; decide one spacing shape.
35. **INCONSISTENCY — `dimensions.positive_direction` is also an unbound `ontology_term`.** It is not in the pre-found list. Item 5-9 lists direction terms among the unbuilt vocabulary (item F "Not built"). *Suggestion:* add it to the term worksheet.

## epoch_file_pattern / ingestion_manifest

36. **INCONSISTENCY — `epoch_map_format` keeps a MATLAB class name as a string.** Value: `'ndi.epoch.epochprobemap_daqsystem'`. The same class's `software_id` doc says *"the v1 filenavigator class name became an edge, not a string field"* (R1). *Suggestion:* fold it to a `software` edge, or make it a bound format term.
37. **QUESTION — `ingestion_manifest.files` mixes two conventions in one string list.** The doc says entries are *"either NDI-scheme URIs (e.g., 'epochid://t00001') or absolute filesystem paths"*. That is structure in a string convention (T14). The `epochid` scheme names a concept the epoch sign-off dropped, and the list overlaps item 25's unheld body. *Suggestion:* declare the two forms separately, or route these files through unheld bodies.

## acquisition_metadata_file / demo / infra naming

38. **QUESTION — `acquisition_metadata_file` is a third byte carrier outside `data_body`.** T6 (`tenets.md:87-93`) says *"exactly two data bodies ... Every carrier ... phases into those"*. T11 bans `_file` in a class name. This class carries `data.bin` directly. Its reason was that bodies need a statement (`V_eta_OPEN_WORK.md` row #66). Item 20 widened the owner to `data_type`, but still not to a bare blob, so the reason partly stands. `demo` also carries a file (`filename1.ext`). The docs also disagree about the payload: the schema says *"the readers produce TSV in the cases seen"* (`build_v_eta.py:1256`), while the coverage ledger row says *"`data.bin` is a .nbf.tgz archive under a generic name"*. *Suggestion:* team decides whether T6 admits this or `data_body.owner` widens. Reconcile the payload doc either way.
39. **QUESTION — container words in signed infra names.** T13 (`tenets.md:259-262`) lists `metadata` and `data` as container words, and T13 "Infra reach" says infra is not exempt. Examples: `acquisition_metadata_reader`, `acquisition_metadata_file`, `metadata_file_pattern`, `data_file_pattern`, and arguably `clock_alignment_configuration`. The names are signed (daq sign-off; clock plan `:235`). *Suggestion:* batch with R5/#27 if the team agrees.

## acquisition_system

40. **INCONSISTENCY — edge naming is mixed on one class.** `reader_id` (role-named) → `acquisition_reader` sits next to `acquisition_metadata_reader_#` (class-named). The recorded rule (`clock_alignment_cluster_plan.md:250-257`) names roles only when two endpoints differ in role. Neither edge here has a sibling in a different role. *Suggestion:* use `acquisition_reader_id`. *(Judgement on pre-found edge naming: the named-role edges `child/parent`, `from_/to_reference` and `relative_to` follow that recorded rule. The inconsistency is the `_id`-suffixed role names such as `reader_id` and `filter_id`, not the role names themselves.)*

## Bindings (cross-cutting)

41. **INCONSISTENCY — value-set `values` are encoded three ways.** `frequency_filter.algorithm` uses bare names (`"chebyshev_1"`). `relative_time_reference.value.relation` uses CURIE strings (`"time:intervalBefore"`). `relative_time_reference.value.clock` and `clock_alignment_configuration.clock` use `{node:"", name:"utc"}` objects. Nothing declares whether a value matches `node` or `name` (T14). *Suggestion:* one encoding, with the matched sub-field declared.

## entity family

42. **INCONSISTENCY — `local_identifier` is redeclared per class, not on `entity`.** Each class carries the same boilerplate, *"Required on subject; optional here."* The field is absent on `runtime_environment` and `acquisition_system`, which are both `⊂ entity`. *Suggestion:* declare it optional on `entity`, and tighten it on `subject`/`session`/`epoch`.
43. **QUESTION — `entity.global_identifier.scheme` is free `char`.** Its doc gives an enumerated set (*"ORCID | ROR | DOI | PMID | PMCID | RRID | UDI"*, plus `URL`, `AwardNumber` used by `web_resource`/`funding`). That is a T8 candidate. *Suggestion:* bind it.
44. **QUESTION — `runtime_environment ⊂ entity`.** It is per-run provenance (T9 lists FAIR entities; this is not one of them), yet it inherits `global_identifier`, which it cannot meaningfully carry. *Suggestion:* confirm `entity` is the right parent (see also #5).

## Tenets file

45. **STALE-DOC — the tenets carry four terms their own later decisions retired.** All four survive the 2026-09-25 amendments:
    - T2 (`:43`): *"a per-sample `sample_time` cadence"*. Retired by the [data_body] sign-off.
    - T6 (`:89`): *"`sampled_body` (self-describing — sample-time axis + typed datum + summary"*. `summary` was dropped, and the datum type moved to the statement (item 15).
    - T4 (`:75`): `subject_relation`. The built class is `relation`; `subject_relation` is not in `index.json`.
    - T11 (`:186`): *"time_reference = `<origin>_<mode>_reference`"*. The time-plan #73 amendment defines `<domain>_reference`, and item 10 uses the same wording.
    *Suggestion:* amend the four sentences.
