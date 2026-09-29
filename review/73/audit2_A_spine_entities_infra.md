# Audit A2: spine, entities, time, bodies, infra (44 classes)

Read-only review of the built V_eta tree at branch `claude/ecstatic-pascal-md91fw`, HEAD `51250ef`, 2026-09-29. Nothing was edited except this file, and nothing is decided here.

## Denominator

- **Classes:** 44 of 44 scoped classes read in full from the built JSON, plus `stable/did_schema_meta.json` and `stable/binding_registry_meta.json`. That covers every field, every nested field, every edge, every file record and every documentation string.
- **Counts:** 313 field declarations (nested ones included), 47 edges, 2 file records, and **362 documentation strings (226 distinct)**.
- **Yardstick:** read in full: `V_eta_tenets.md` (T1–T15), `V_eta_spatial_transcriptomics_plan.md` (items 1–70), `review/73/OPEN_ITEMS.md` and the previous audit `review/73/audit_A_spine_infra.md`.
- **Plan documents checked:** read only in the sections that bear on these classes:
  - `V_eta_method_parameters_plan.md`: top amendments, the MODEL section and the FINAL MODEL section.
  - `V_eta_data_body_model_plan.md`: top amendment index.
  - `V_eta_recording_observation_plan.md`: grep for `observes`.
  - `review/73/veta_binding_worksheet_73.csv`: all 24 rows.
- **Mechanical pass denominator:** 213 class schemas in the tree, 564 distinct field names, 72 distinct edge names and 34 file names were used as the "exists" set.
- **Previously reported items:** items OPEN_ITEMS marks TABLED/BLOCKED (e.g. 24, binding `keys.unit`) are not reported again as new.

## Summary

**34 new findings: 1 VIOLATION, 10 INCONSISTENCY, 15 STALE-DOC, 8 QUESTION.** Previous-audit status (45 items): **18 FIXED, 7 MOOT, 18 STILL OPEN, 2 mixed** (#38: fixed for `acquisition_metadata_file`, open for `demo`; #45: 3 of 4 tenet lines fixed).

The five most important:
1. **#17 VIOLATION.** The `parameter[]` shape (3 mounts) has no declared canonical unit. Its doc says the unit "comes from the registry", but no registry row shape has a unit key. This is the same rule Amendment 1 reversed for the key it was "modelled on".
2. **#26 STALE-DOC.** The `method_parameters.parent_id` doc says "`parent_id` was rejected", on the edge that is named `parent_id`.
3. **#27 STALE-DOC.** The `method_parameters.name` doc still calls name-vs-`base.name` "AN OPEN TEAM DECISION"; item 54 decided it. It also cites NDI readers of `base.name` that will not find V_eta documents.
4. **#21 INCONSISTENCY.** `directed_relation.relation` declares no binding, while `binding_registry_meta.relation_bindings` holds 26 predicates. That registry lacks item 24's mapping predicates, still lists the replaced `observes`, and has no undirected rows.
5. **#8 INCONSISTENCY.** About ten conditional requirements live only in prose, with no declaration and no named check (T14). Examples: keys required on a sampled body, `origin`/`spacing` iff `regular`, the `values`/`labels`/`labels_from` XOR, `chunk` only on sampled bodies, and `datum_type`/`byte_order`/`datum_order` "REQUIRED in practice".

---

## Findings

### entity family (subject, session, epoch, web_resource, funding, acquisition_system, strain, dataset, publication)

1. **INCONSISTENCY: `local_identifier` carries the ontology term of a different id.**
   - `stable/subject.json` `fields[local_identifier].ontology` = `iao:0000578 "centrally registered identifier"`. That is the same annotation as `base.id`.
   - `stable/session.json` `fields[local_identifier].ontology` = `ncit:C169028 "Study Unique Identifier"`. That is the same annotation as `base.session_id`.
   - `stable/epoch.json` `local_identifier.ontology` = `null`.
   - Both docs say the field is a local handle, "unique within its dataset". It is not centrally registered. So one field has three annotations, and two of them claim it is the document id.
   - *Suggestion:* give all three one local-identifier term (or `null`), and keep the id terms on `base`.
2. **STALE-DOC: the `subject.local_identifier` doc describes the pre-item-54 layout.**
   - `stable/subject.json` `fields[local_identifier].documentation`: *"REQUIRED on subjects; the same field is optional on every other entity (see local_identifier there)."*
   - Item 54 removed it from the eight other entities. Only `session` and `epoch` declare it, and both declare it REQUIRED.
   - *Suggestion:* "Required; also declared (required) on `session` and `epoch`."
3. **STALE-DOC: nothing in the built tree says where a `web_resource`'s URL, or a funding award number, lives.**
   - `stable/web_resource.json` declares only `name` (*"The resource's name (was `label`, #73 item 54)"*).
   - `stable/funding.json` declares only `name`.
   - The build comment says the URL is `global_identifier` with scheme `'URL'` (`tools/build_v_eta.py:1874,1883`). Item 53 relies on `software` carrying "an RRID, DOI, SWHID or Wikidata id" there.
   - But `stable/entity.json` `global_identifier.documentation` lists only *"ORCID | ROR | DOI | PMID | PMCID | RRID | UDI | …"*, and `scheme` is free `char` with doc *"Identifier scheme."* (previous #43).
   - The defining property of a web resource is therefore documented nowhere a reader of the schema looks (T14).
   - *Suggestion:* list the schemes in use (URL, SWHID, Wikidata, award number), and say on `web_resource` that its URL is `global_identifier[scheme=URL]`, or bind `scheme`.
4. **QUESTION: `acquisition_system.name` is optional, but the schema treats it as the lookup key.**
   - `stable/acquisition_system.json` `fields[name]`: `mustBeNonEmpty: false`. Its doc says *"NDI finds an acquisition system by this name ... so migrators must carry it."*
   - Item 56 makes the name the (session, name) resolution key and the only content of a minted rig.
   - *Suggestion:* require it, or record why a nameless rig is valid.
5. **INCONSISTENCY: vendor and catalog number are modelled two ways.**
   - `stable/strain.json` `fields[stock_number]` = `{vendor: char, code: char}`.
   - `draft/product.json` has `vendor_id -> organization` + `catalog_number`.
   - Item 59 names `strain.stock_number` an "expected later user" of `product`, so the deferral is recorded. The split is still live now.
   - *Suggestion:* keep it tracked as a named follow-up. It is not in OPEN_ITEMS.
6. **QUESTION: several enumerated or controlled terms are unbound and missing from the binding worksheet.**
   - `strain.genetic_strain_type`: *"wildtype | transgenic | knockout | ..."*, `constraints: {}`.
   - `strain.disease_model`: `{}`.
   - `acquisition_channels.channels.type`: *"ai | ao | di | do (daqsystemstring.m:53-56)"*, `{}`.
   - `dataset.license`: free `char`, doc *"a SPDX license identifier"*.
   - None of the four is among the 24 rows of `veta_binding_worksheet_73.csv`. Rows 23–24 cover only `strain.species` and `breeding_type`.
   - *Suggestion:* add them to the worksheet.
7. **STALE-DOC: `publication.publication_date` quotes a field-name census that no longer holds.**
   - The doc says: *"(13 `_name`, 11 `_time`, 10 `_type`, 5 `_id`; 0 bare participles in 472 field names)"*.
   - The tree now has 564 distinct field names (this pass's count), and `_time` fields were renamed widely. The figure has no method or date attached.
   - *Suggestion:* drop the numbers, or date them.

### data / data_type / data_body / sampled_body / opaque_body

8. **INCONSISTENCY: conditional requirements are prose, not declarations (T14).** Each of these is `mustBeNonEmpty: false` with a rule stated only in a documentation string:
   - `data.keys`: *"Required on a sampled_body"* (`draft/sampled_body.json` does not tighten it).
   - `keys.origin` and `keys.spacing`: *"REQUIRED iff `regular`"*.
   - `keys.values`: *"XOR with `labels`"*.
   - `keys.labels_from`: *"XOR with `labels`/`values`"*.
   - `keys.chunk`: *"sampled_body ONLY"*, though it is declared on `data` and inherited by `data_type` and `opaque_body`.
   - `data_type.datum_type`: *"REQUIRED in practice whenever ..."*.
   - `sampled_body.byte_order` and `.datum_order`: *"REQUIRED in practice whenever ..."*.

   None has a named validator check in the schema.
   - *Suggestion:* tighten `keys` on `sampled_body` (the precedent is `subject_calculation.software_id`), and list the remaining rules as named batch or DID-matlab checks.
9. **INCONSISTENCY: `sampled_body.byte_order` and `datum_order` declare their enumerations only in prose.**
   - `byte_order`: *"'little' | 'big'"*.
   - `datum_order`: *"'C' | 'F'"*.
   - Both are `char` with `constraints: {}`, while `data_type.datum_type` on the same value declares `constraints.enum`. `data_body.hash_algorithm` (*"e.g. 'MD5'"*) is also free.
   - *Suggestion:* add `enum` constraints.
10. **INCONSISTENCY: an `opaque_body` need not state its `format`.**
    - `draft/opaque_body.json` declares nothing, and `data_body.format` is optional.
    - Item 58 and T6 define the opaque body as *"bytes laid out by their own `format`"*. Without `format`, the bytes cannot be read from the schema alone.
    - *Suggestion:* require `format` on `opaque_body`, or record why not.
11. **INCONSISTENCY: T6's cache-warrant test cannot be met by a redundant body.**
    - T6 requires a cache to carry *"`redundant` + `derived_from`"* and a *"Recorded reason ... written next to it"*.
    - `data_body.redundant` says it adds nothing *"beyond another body of the same owner"*. But `data_body` has no edge naming that source body, and neither it nor `subject_calculation` has a slot for the recorded reason.
    - *Suggestion:* decide whether a redundant body names its source and its reason, or amend T6 for bodies.
12. **QUESTION: why is `fill_value` a double array?**
    - `draft/sampled_body.json` `fields[fill_value]`: type `double`, `mustBeScalar: false`, *"In `datum_type` encoding"*.
    - A body has one fill value. A double cannot hold every `int64`/`uint64` value exactly, nor a `complex` one.
    - *Suggestion:* state why it is an array and how the non-double datum types are written.
13. **STALE-DOC: "axis" survives in key documentation (item 14: `axes -> keys`).**
    - `data.keys.approximate`: *"Applies to the whole axis."*
    - `keys.n`: *"along this axis"*.
    - `keys.origin`: *"Where the axis starts"*.
    - `keys.unit`: *"a categorical axis"*.
    - `keys.variable`: *"'which axis is X'"*.
    - `sampled_body.datum_order`: *"last axis fastest ... more than one axis"*.
    - `coordinate_system.dimensions.axis` is a different, legitimate use.
    - *Suggestion:* say "key" or "dimension".
14. **STALE-DOC: `data_type.data_body` cites the wrong item.**
    - The doc says: *"A document marked true with no body pointing at it has lost its data -- the batch check (item 58)."*
    - That check is stated in item 60 (*"`data_body` true ⇒ at least one body owns the document (batch check)"*).
    - *Suggestion:* cite item 60.

### conditions (subject_statement, data_body)

15. **STALE-DOC: `conditions.term.value` still allows one value per reading.**
    - `stable/subject_statement.json` and `draft/data_body.json`, `fields[conditions].term.value`: *"length 1 (a constant condition) or the measurement's value length (one label per reading)"*.
    - The parent doc on the same field says *"Cardinality exactly 1"*, following data_body Amendment 2 and T6's *"one-value fact"*. The sibling `count.value` and `quantity.value` docs say *"Length 1"*.
    - The parent doc also calls the entries *"typed {variable, value} entries"*, but no `value` sub-field exists; the forms are `term`/`count`/`quantity`.
    - This is the remnant of previous #9.
    - *Suggestion:* fix both docs in both mounts. Consider declaring the shape once, as item 65 did for `keys`.

### subject_interaction / subject_calculation / subject_manipulation

16. **STALE-DOC: the `software_id` and `input_id` docs predate T2 and T15.**
    - `stable/subject_interaction.json` `depends_on[software_id]`: *"populated on calculations, optional on computed observations"*. T2 says there is no computed observation. It also says *"distinct from ... derived_from (the input data)"*.
    - `stable/subject_calculation.json` `depends_on[software_id]`: *"from `derived_from` (the input data)"*. The edge is `input_id` (T15).
    - `depends_on[input_id]`: *"the provenance inverse of directed_relation's entity->entity child/parent"*. `child_id`/`parent_id` now accept `entity,subject_statement,data_type`.
    - *Suggestion:* replace `derived_from` with `input_id`, drop the computed-observation clause, and drop "entity->entity".
17. **VIOLATION (T14): the `parameter[]` value has no declared canonical unit.**
    - It is declared three times, identically, and each copy is affected: `subject_interaction.method_parameters`, `method_parameters.method_parameters` and `clock_alignment_configuration.method_parameters`.
    - `value.value` is documented as *"Canonical value."* The `variable` doc says: *"Its dimension comes from the registry -- there is NO unit field"*.
    - `stable/binding_registry_meta.json` has no row shape that carries a unit. Its lists' keys are `subject_statement_bindings {class, ontology, root_node, subject_defining, variable}`, `relation_bindings {...}`, `entity_field_bindings {...}` and `binding_examples {...}`.
    - T14 says: *"Every canonical slot names its complete unit"*. data_body Amendment 1 reversed the same "no unit field" rule for the key entry, citing this missing registry row shape. The `parameter` entry is documented as "modelled on" that key entry (#18).
    - The signed method_parameters line (*"with no `unit` field"*) is the decision this contradicts, so this is a team call.
    - *Suggestion:* add a bound `unit` beside `value` as Amendment 1 did, or record where the unit is declared.
18. **STALE-DOC: all three `parameter[]` mounts say "Modelled on the `axis` entry".**
    - The entry is now a key (items 14 and 65), and that key has since gained `unit`. So "modelled on" no longer describes the two shapes.
    - *Suggestion:* reword, or tie it to #17.
19. **QUESTION: `subject_calculation.software_id` redeclares an inherited edge to tighten it, and no rule governs this.**
    - The doc says *"Redeclares -- and TIGHTENS to required -- the optional `software_id`"*.
    - OPEN_ITEMS item 3's second bullet proposed a declared rule ("a subclass may tighten an inherited edge to required"). Item 54 closed item 3's first bullet only.
    - *Suggestion:* decide the rule, since #8 needs the same mechanism.
20. **QUESTION: only manipulations carry free-text notes.**
    - `stable/subject_manipulation.json` `fields[notes]`: *"Irreducible human prose describing this event."* No other direction declares prose.
    - *Suggestion:* record why observations and calculations have no notes, or move the field to `subject_interaction`.

### directed_relation / relation / undirected_relation

21. **INCONSISTENCY: the relation predicate is unbound in the schema but enumerated in the registry, and the two disagree.**
    - `stable/directed_relation.json` `fields[relation]`: `constraints: {}`, doc *"an enumerated ontology term (RO-backed) ... V_eta declares the corpus-exercised minimum (D6)"*.
    - `stable/binding_registry_meta.json` `relation_bindings` holds 26 directed predicates, and nothing links field to registry:
      - It has no row for item 24's *"orthologous gene mapping" | "gene alias mapping"*.
      - It still lists `observes`. The recording plan says *"the `probe observes specimen` relation is REPLACED by the `instrument_id` edge"* (`V_eta_recording_observation_plan.md:34`).
      - Its `child_types`/`parent_types` never include `subject_statement` or `data_type`, although `child_id`/`parent_id` accept both (items 22, 27).
      - It has no undirected rows (`undirected_relation.relation`: *"paired_with, same_as"*).
    - Worksheet rows 16–17 list both fields as having no candidate set.
    - *Suggestion:* point the field binding at the registry, and reconcile the registry with items 22, 24 and 27.
22. **QUESTION: `value_id`, `owner_id`, `child_id` and `parent_id` cannot express "a standalone value".**
    - `subject_statement.value_id`, `relation.value_id`, `data_body.owner_id`, `directed_relation.child_id` and `parent_id` all target `data_type`.
    - Every statement leaf is `⊂ data_type` (T3), and so is `clock_alignment` (item 70). So `value_id` admits another claim, where T6 says it points at a standalone data-type document.
    - `must_refer` is existence-only (T8), so this is declarative only.
    - *Suggestion:* record that "standalone" is a batch rule, or name the check.

### time_reference family

23. **STALE-DOC: `relative_to` survives the T15 rename to `referent_id`.**
    - `stable/relative_time_reference.json`:
      - `fields[value]`: *"the referent named by `relative_to`"*.
      - `value.clock`: *"`inherited` is what `relative_to` already says"*.
      - `value.start`: *"offset ... from the referent named by `relative_to`"*.
    - `draft/coordinate_system.json` `fields[origin]`: *"WHICH point on `relative_to` is zero"*.
    - *Suggestion:* say `referent_id`.
24. **QUESTION: the time value is optional on both time leaves, and `clock` is optional where uniqueness is keyed on it.**
    - `relative_time_reference.value.clock` is optional. Yet its doc says *"'10 seconds in' is ambiguous until the clock is named"*, and all three `time_reference_id` families declare `referent_unique_by: "value.clock"`. An absent clock leaves the uniqueness rule undefined.
    - `absolute_time_reference.value.start` is optional, so an absolute reference can carry no time.
    - *Suggestion:* state the minimum content of each leaf, e.g. "`start` or `relation`", and clock required when `start` is present.

### clock_alignment

25. **STALE-DOC: the `clock_alignment.input_id` doc mentions a `_#` family.**
    - The doc says: *"which is why these are named endpoints and not a `_#` family."*
    - T15 removed `_#` from V_eta.
    - *Suggestion:* "not one repeated edge".

### method_parameters

26. **STALE-DOC: the `parent_id` doc contradicts its own name.**
    - `stable/method_parameters.json` `depends_on[parent_id]`: *"Reuses the word the schema already spends on this relation (`input_id` on calculations); `parent_id` was rejected because it implies the child inherits, and it does not."*
    - That was the rationale for the old `derived_from_id`. T15 renamed the edge to `parent_id` (T15 table row `method_parameters`).
    - *Suggestion:* rewrite it to T15's reason, and keep "LINEAGE ONLY, a complete copy, not a diff".
27. **STALE-DOC: the `method_parameters.name` doc calls a decided question open.**
    - The doc says: *"WHICH BLOCK IS AUTHORITATIVE IS AN OPEN TEAM DECISION ... Do not delete either copy on this note."*
    - Item 54 decided it: `base.name` is did_v1-only, and *"`method_parameters` (already)"* declares `name`.
    - The doc also records that NDI `spikeextractor.m:372` / `spikesorter.m:373` query `base.name`. V_eta documents will not write `base.name`, so those readers will miss migrated settings.
    - *Suggestion:* rewrite to item 54, and add the NDI reader change to the PR #76 checklist if it is not already there.
28. **STALE-DOC: the `method_parameters.subject_id` doc calls a subject a "recording".**
    - The doc says: *"settings that apply to ONE recording."*
    - The plan says *"OPTIONAL -- scoped to one element-subject"* (`V_eta_method_parameters_plan.md:83`). The recording is the epoch scope.
    - *Suggestion:* "to one subject (element)".

### infra

29. **INCONSISTENCY: `file_pattern` names two different things.**
    - `stable/epoch_file_pattern.json` `fields[file_pattern]`: `string[]` in NDI's `#`-stem syntax (*"{'#\\.rhd\\>', '#\\.tsv\\>'} ... `#` matches an unknown common stem"*).
    - `stable/epoch_parameter_reader.json` `fields[file_pattern]`: a scalar `char` regex (*"e.g. \".*\\.tsv\\>\""*).
    - Item 65 gave both the same name. The pattern language is declared on neither (T14).
    - *Suggestion:* declare the syntax per field, or name the fields apart.

### did_schema_meta

30. **INCONSISTENCY: bindings use keys the meta-schema does not declare.**
    - `root` is used on 5 fields and `source` on 6: `relative_time_reference.value.clock` and `.relation`, `clock_alignment_configuration.clock`, `frequency_filter.algorithm` and `.band`, plus `term.value`.
    - `stable/did_schema_meta.json` `field_definition.constraints.properties.binding.properties` declares neither. It declares `root_node`/`ontology` (0 uses among field bindings) and `vocabulary_version` (0 uses). Its doc describes the subtree form as *"`ontology` + `root_node`"*.
    - The binding object has no `additionalProperties: false`, so this passes silently.
    - *Suggestion:* declare `root`/`source`, or rename them to the declared keys.
31. **STALE-DOC: the meta-schema describes V_delta.**
    - `$id` and `title` say *"(V_delta)"*, and `maturity_level` points at *"schemas/V_delta/"*.
    - The description names a composite `'duration'`, but the class is `time` and no `duration.json` exists.
    - It says *"The canonicals are SI base units except for 'temperature' ... and 'pressure'"*, but mass is `grams`, volume `liters` and angle `degrees` (item 44).
    - It lists `score` as *"value, scale, scale_min, scale_max, approximate"*. Item 46 added `source_unit`/`source_value`, and `stable/score.json` has them.
    - *Suggestion:* rewrite the description for V_eta, or point it at the tenets.

### defaults (cross-cutting)

32. **INCONSISTENCY: some default values do not match their field's type.** This is a mechanical count over the 313 declarations.
    - 12 `boolean` fields default to `0.0` (every `approximate` inside a `time`/`frequency`/`gain`/`length` cell, and `absolute_time_reference.value.start.approximate`); 9 others default to `false`.
    - 3 `integer` fields default to `0.0`: `data_body.size_bytes`, `directed_relation.sequence`, `frequency_filter.order`.
    - `ingestion_manifest.files` is a `string` array defaulting to `""`; the 6 other string arrays default to `[]`.
    - The meta-schema says `default_value` *"Must pass validation"*.
    - *Suggestion:* normalise in the build.

### tenets (yardstick; outside the 44 classes)

33. **STALE-DOC: the tenets name retired edges and classes.**
    - `V_eta_tenets.md:50,55` (T2): *"records them in `derived_from_#`; `derived_from_#` is declared on `subject_calculation` only"*. T15, in the same file, renames it `input_id`.
    - `:91` (T4): *"`subject_relation` → `directed_relation`"*. No such class exists.
    - `:459` (T15 vocabulary): lists `acquisition_metadata_reader_id`, renamed `epoch_parameter_reader_id` by item 65.
    - `:472,:474,:481`: table rows for `control_designation` (deleted, item 67) and `acquisition_metadata_reader_#`.
    - T6's cache test says *"carries `redundant` + `derived_from`"*.
    - *Suggestion:* amend these lines, because the tenets are the yardstick.

### (one further note)

34. **QUESTION: `demo` still carries bytes outside the two data bodies.**
    - `stable/demo.json` `file[filename1.ext]`: *"Required by the did_v1 demoNDI schema ... V_eta had dropped it -- silent file loss."*
    - T6 says there are *"exactly two data bodies"*. `acquisition_metadata_file`, the other carrier in previous #38, was retired by item 61. `demo` is the one left, and no recorded reason exempts it.
    - *Suggestion:* record the exemption (a demo fixture), or give it an `opaque_body`.

---

## Mechanical pass

A script extracted every backticked token, and every `word_id` / `word.word` token, from the 362 documentation strings. Each token was checked against the tree's 213 class names, 564 field and sub-field names, 72 edge names and 34 file names.

**247 identifier-shaped tokens were checked; 81 did not resolve.** A path-aware second check of dotted tokens headed by a class name covered 16 tokens and flagged 1 (`daqsystem.base.name`, a v1 provenance path, which is fine).

**Genuinely stale: 6 tokens.** All are reported above.

| class :: string | token | finding |
|---|---|---|
| relative_time_reference :: value | `relative_to` | #23 |
| relative_time_reference :: value.clock | `relative_to` | #23 |
| relative_time_reference :: value.start | `relative_to` | #23 |
| coordinate_system :: origin | `relative_to` | #23 |
| clock_alignment :: input_id | `_#` | #25 |
| subject_calculation :: software_id | `derived_from` (as an edge) | #16 |

**Legitimate: 75 tokens.**

| group | count | tokens |
|---|---|---|
| v1 / NDI provenance | 22 | `full_name` ×2 and `title` ×2 (the "was ..." notes of item 54); `daqreader_ndr`, `daqreader_ndr.ndr_reader_string`, `epochclocktype`, `number_fullpath_matches`, `syncfilename`, `minEmbeddedFileOverlap`, `errorOnFailure`, `daqsystem1_name`, `stopbandAttentuation`, `mock.ismock`, `devicestring` ×2, `approx_` ×2, `no_time`, `inherited` (NDI clock types), `specimen.species` (openMINDS), `epochprobemap.ndi` |
| superseded names quoted in a change note | 6 | `start_utc`, `source_start`, `end_utc`, `end` ×2, `source_duration` |
| code / tool references | 19 | `did2.validate.silentLoss` ×3, `family_uniqueness_violation` ×3, `did2.convert.resolveSessionAnchors`, `ndi.fun.file.MD5`, `ndi.daq.system.mfdaq`, `ndi_document2ndi_object.m`, `document.m`, `daqsystemstring.m`, `ndi.calc.example.simple` ×2, `ndi.epoch.epochprobemap_daqsystem`, `ndi.query`, `spikesorter.m`, `spikeextractor.m` |
| value literals and relation-term names | 20 | `ubit1`, `float64`, `bool`, `char`, `double`; `encountered`, `member_of`, `has_author`, `derived_from` ×2 (as a relation term), `how`; `ordered` (an edge attribute); `body_data_0` and `body_data_k` ×2 (file-series members); `start_anchor`/`end_anchor` ×6 (named as NOT built) |
| naming-grammar suffixes | 6 | `_timestamp`, `_time` ×2, `_name`, `_type`, `_id` |
| undeclared shape name | 2 | `parameter[]` (the plan's name for the entry; no class or type declares it) |

**Blind spots of this pass**, found by a follow-up grep for retired vocabulary over the same 362 strings:
- `` `axis` `` in the three `parameter[]` docs resolved as a name, because `coordinate_system.dimensions.axis` exists (#18).
- Un-backticked prose was not tokenised. That is how *"computed observations"* and *"derived_from (the input data)"* in `subject_interaction.software_id` (#16) and the "axis" wording (#13) were missed by the first check and caught by the grep.
- The grep found no occurrence in these 362 strings of: `axes`, `storage_mode`, `sample_time`, `radians`, `kilograms`, `acquisition_metadata*`, `control_designation`, `image_observation`, `logical_observation`, `runtime_environment`, `execution_environment`, `session_relative_reference`, `is_approximate`, `axis_labels`, `presented_id`. A tree-wide grep for `acquisition_metadata|metadata_file_pattern|data_file_pattern` under `schemas/V_eta/` returns 0 files.

**Adjacent, not in scope:** `veta_binding_worksheet_73.csv` rows 1–3 and 9–11 name `subject_statement.keys.*`, `sampled_body.keys.*` and `image.value.keys.*`. After items 51, 60 and 65 these fields live on `data.keys`, and `image` is a v1 tombstone.

---

## Previous audit (review/73/audit_A_spine_infra.md, 45 findings): status

| # | title (short) | status | evidence |
|---|---|---|---|
| 1 | `sample_time` still declared | FIXED | not in `subject_interaction.json` fields; T2 records it retired (#73 item 21) |
| 2 | `sample_time` doc points at body | MOOT | field gone |
| 3 | inline `method_parameters` untyped | FIXED | `parameter[]` declared (item 22); see new #17 |
| 4 | `method_parameters` doc scope | FIXED | doc now "the SAME `parameter[]` shape as the `method_parameters` document" |
| 5 | run environment modelled twice | FIXED | item 53: `execution_environment` and `runtime_environment` gone; `interpreter_id`/`operating_system_id` on `subject_calculation` |
| 6 | `software_id` "computed observations" | STILL OPEN | same text in `subject_interaction.depends_on[software_id]` (new #16) |
| 7 | rig as two edges | MOOT | item 55 dropped `epoch.instrument_id`; item 56 dropped `subject_interaction.acquisition_system_id` |
| 8 | channels modelled twice | FIXED | item 56: only `acquisition_channels` plus `acquisition_channels_id`. The unbound `type` remains (new #6) |
| 9 | `conditions` not restructured | STILL OPEN (partly) | Amendment 2 shape built (item 23); the `term.value` per-reading doc remains (new #15) |
| 10 | `keys.unit` unbound | STILL OPEN (tabled) | OPEN_ITEMS 24, blocked on unit vocabulary |
| 11 | standalone value has no `datum_type`/storage | FIXED | item 60: `datum_type` and `data_body` on `data_type` |
| 12 | where a referenced value's keys live | FIXED | items 60 and 65: keys on `data`; the statement declares none |
| 13 | "assertions always inline" | MOOT | `storage_mode` deleted (item 60) |
| 14 | `keys.regular` optional vs signed REQUIRED | STILL OPEN | `data.keys.regular` `mustBeNonEmpty: false`, default `false` |
| 15 | `key_labels_id` → `base` broad | STILL OPEN | `data.json` `depends_on[key_labels_id].must_refer_to_document_class = "base"` |
| 16 | `epoch.instrument_id` union | MOOT | edge dropped (item 55) |
| 17 | two `session_id`s | FIXED | item 57 dropped the edges on `epoch` and `clock_alignment_policy` |
| 18 | `_1`/`_2` in family doc | FIXED | T15 rename; doc now "entries repeating one name (T15)" |
| 19 | `epoch.time_reference` targets relative only | STILL OPEN | `epoch.json` `time_reference_id → relative_time_reference` |
| 20 | `content_hash` vs algorithm | FIXED | doc: "The algorithm is declared beside it, in `hash_algorithm`" |
| 21 | `format`/`compression` examples | FIXED | `format` "IANA media type ... NOT a file extension"; `compression` empty-when-none agrees with L4 (`codec raw` = no compression) |
| 22 | unheld body location undeclared | STILL OPEN | `data_body` still has no location field; `file[body_data]` only says "recorded by location" |
| 23 | `event_relative_reference` cited | FIXED | gone from `directed_relation.time_reference_id` doc |
| 24 | undirected lacks time/epoch parity | STILL OPEN | `undirected_relation.entity_id → entity` only; no `time_reference_id`/`epoch_id` |
| 25 | `sequence` index base | STILL OPEN | doc unchanged: "Optional ordinal ..." |
| 26 | `axes` in `method_parameters` doc | STILL OPEN (partly) | field doc now says `keys`; `variable` doc still "Modelled on the `axis` entry" (new #18) |
| 27 | settings list optional vs plan REQUIRED | STILL OPEN | `method_parameters.method_parameters` `mustBeNonEmpty: false`; plan `:515` "REQUIRED" |
| 28 | `variable` doc claims BOUND | FIXED | "To be BOUND (not yet declared -- binding worksheet, 2026-09-25)" |
| 29 | `other` untyped bag | MOOT | deleted (item 62) |
| 30 | `derived_from_id` wording | MOOT | renamed `parent_id` (T15), but its doc now contradicts the name (new #26) |
| 31 | channel-pair cardinality doc | FIXED | doc "0 or 2 ... cannot exclude exactly 1; that check belongs to a validator" |
| 32 | clock config vs `method_parameters` | FIXED | item 63: inline `method_parameters[]`; the class keeps clock, channels and software |
| 33 | strain docs claim bindings | STILL OPEN (now honest) | docs say "INTENDED binding ... NOT YET DECLARED"; worksheet rows 23–24; `genetic_strain_type`/`disease_model` not in worksheet (new #6) |
| 34 | `origin` "same concept" + spacing shapes | STILL OPEN | `coordinate_system.origin` doc unchanged; `dimensions.spacing` is `length`, while `keys.spacing` is `{value, source_value}` |
| 35 | `positive_direction` unbound | STILL OPEN (tracked) | worksheet row 22 |
| 36 | `epoch_map_format` class string | STILL OPEN | `epoch_file_pattern.epoch_map_format` = "'ndi.epoch.epochprobemap_daqsystem'" |
| 37 | `ingestion_manifest.files` mixed forms | STILL OPEN | doc unchanged ("'epochid://t00001' or absolute filesystem paths") |
| 38 | third byte carrier | FIXED (`acquisition_metadata_file`) / open for `demo` | item 61 retired the class; `demo` file record remains (new #34) |
| 39 | container words in infra names | FIXED | item 65: `epoch_parameter_reader`, `file_pattern`; 0 files match `acquisition_metadata` |
| 40 | `reader_id` naming | STILL OPEN | T15 vocabulary keeps `reader_id` without a reason; target is `acquisition_reader` |
| 41 | binding values three ways | FIXED | item 64: all 5 value lists are `{node, name}`; meta requires it (see new #30 for `root`/`source`) |
| 42 | `local_identifier` redeclared per class | FIXED | item 54: only `subject`/`session`/`epoch`; subject doc now stale (new #2) |
| 43 | `global_identifier.scheme` free `char` | STILL OPEN | `entity.json` `scheme` `constraints: {}` (see new #3) |
| 44 | `runtime_environment ⊂ entity` | MOOT | class deleted (item 53) |
| 45 | tenets stale (4 terms) | FIXED 3 / STILL OPEN 1 | T2 `sample_time`, T6 `summary` and T11 grammar fixed; T4 `subject_relation` remains (`:91`); new stale lines in new #33 |

Totals: FIXED 18 (1, 3, 4, 5, 8, 11, 12, 17, 18, 20, 21, 23, 28, 31, 32, 39, 41, 42); MOOT 7 (2, 7, 13, 16, 29, 30, 44); STILL OPEN 18 (6, 9, 10, 14, 15, 19, 22, 24, 25, 26, 27, 33, 34, 35, 36, 37, 40, 43; rows marked "partly" count here); MIXED 2 (38, 45).
