# V_eta audit against tenets T1–T7 (read-only)

Tree: /home/user/DID-schema, branch `claude/ecstatic-pascal-md91fw`, HEAD = origin = `701a5de` (`git pull`: "Already up to date"; `git rev-parse HEAD origin/claude/ecstatic-pascal-md91fw` both `701a5dec75ca…`).
**Note:** during this audit, something other than this audit changed the working tree (14:45 UTC; `git diff --stat`: 7 files, including STATUS, the coverage ledger, decisions.json, and one new `Decided by` line each in the data_body plan ([index covariates]) and in the go_forward audit). `ps` showed 2 gates/coverage processes running. None of those edits changes a finding below. This audit wrote nothing to the repo.

Scratch evidence dumps: `(session scratchpad) audit/persist.txt` (all non-retire classes, every field with its type, binding and doc) and `.../audit/retire.txt`. Generator: `.../audit/dump.py`.

## (D) Denominators

| set | classes | fields (incl. nested) | edges | depth |
|---|---|---|---|---|
| stable persist | 69 (+5 meta files) | 931 | 40 | every field doc read |
| draft persist | 17 | 157 | 14 | every field doc read |
| stable in_progress | 7 | 84 | 7 | every field doc read |
| stable retire (v1 passthrough) | 70 | 399 | 79 | checked only for: inbound edges, superclasses, `file` entries |
| deprecated | 7 (6 retire, 1 in_progress) | 53 | 13 | checked only for inbound dependencies; `projectvar` read |
| **total** | **170** | **1624** | **153** | |

Binding registry: 34 `relation_bindings`, 19 `entity_type_bindings`, 1 `entity_field_bindings`, 11 `subject_statement_bindings`, all read. Term registry: read only where T1 points at it ("Sample Type").
Dependency on deprecated classes: 0 of the 140 edges in stable/draft point at a deprecated class, and no non-retire class names one. Non-retire classes that depend on retire classes: `acquisition_epoch`, `daqmetadatareader_epochdata_ingested`, `ensemble` and `stimulus_presentation` have superclass `epochid` (retire); `daqmetadatareader_epochdata_ingested.daqmetadatareader_id` points at `daqmetadatareader` (retire). All five are in_progress.

---

## (A) Violations (schema contradicts a tenet or a signed decision as written)

**A1. HIGH: a signed relation cannot be written. Bears on T4 ("Endpoints are typed depends_on") and T1/T2 ("configuration is its own class off `base`").**
- `binding_registry_meta.json` `relation_bindings` row `recorded_by`: `"child_types": ["epoch"], "parent_types": ["acquisition_system"]`.
- `V_eta_entity_composition_plan.md:190`: `TEAM-SIGN-OFF: jess / 2026-10-08 -- acquisition_system is configuration off base, with an optional device_id; epochs are recorded_by it`.
- `directed_relation.parent_id`: `must_refer_to_document_class: "entity,statement,value"`. `acquisition_system` has superclasses `['base']`, so it is none of these.
- Result: an epoch `recorded_by` its acquisition system fails referential typing. No later decision found that allows it.
- No `.m` writer of `recorded_by` turned up in /home/user/DID-matlab (`8eec66a`) or /home/user/NDI-matlab (`claude/v2-object-layer` `235801928`): `grep -rln recorded_by --include=*.m` returned nothing. So this is latent, not measured on a corpus.

**A2. MEDIUM: T6 "exactly two data bodies" (the one recorded exemption is `demo`).** Four in_progress classes declare their own `file`:
- `acquisition_epoch` (`epoch_binary_data.vhsb`)
- `daqmetadatareader_epochdata_ingested` (`data.bin`)
- `ensemble` (`neuron_names.txt`)
- `stimulus_presentation` (`presentation_time.bin`)

T6: "One exemption, recorded (#73 audit 2 D13): `demo` keeps a file record outside the two bodies". `acquisition_epoch.dimensions` says deriving from `data` "waits for the epoch-family re-walk, #73 audit 2 D13". That is a deferral, not an exemption. The 18 retire classes with `file` entries are v1 passthroughs and are not counted here.

**A3. MEDIUM: a field's own documentation contradicts its declared requirement.**
- `interaction.software_id` doc: "REQUIRED on calculations (calculation.require_inherited)".
- `calculation.json`: `"require_inherited": []`.
- The schema is right. The doc is stale: `V_eta_spatial_transcriptomics_plan.md:610` reads "Decided by Jess Haley, 2026-10-22 [calculation-software-optional decided]: … a calculation's `software_id` is optional". A reader who trusts the doc writes or expects the wrong thing.

No other tenet violation was found in the 93 non-retire stable/draft classes. Checked and consistent:
- T1: no class has `entity` as a superclass. `entity` carries only identity fields plus `type`, `time_reference_id` and the inherited `session_id`. The 19 `entity.type` values equal the 19 `entity_type_bindings` names, in the same order.
- T2: `interaction.time_reference_id` has `min_count: 1`. `input_id` is declared on `calculation`, and on `clock_alignment` (see C1).
- T3: `assertion`, `observation`, `manipulation` and `calculation` each declare `value_kind {"root":"value","count":1}`. There are exactly 8 named vision calculators.
- T6:
  - `data_body` has exactly 2 subclasses.
  - `opaque_body` has `require_inherited ["format"]`, `sampled_body` has `["dimensions"]`, and `data_body.owner_id` has `min_count: 1`.
  - `redundant` is declared only on `data_body` and `calculation`.
  - `body_data` is a series.
  - No `keys`, `complete`, `control_item`, `method_parameters`, `storage_mode`, `summary` or `sequence` field name remains in stable/draft (grep over 168 files: 0 hits).
- T4: `undirected_relation.entity_id` has `min_count 2`, `max_count 2`.

---

## (B) Inconsistencies between classes and docs

**B1. MEDIUM: the "one variable once" rule omits body conditions.**
- `data` rule `variable_once` reads: "A variable appears at most once across a statement's `conditions`, its value's `covariates` and any one of its bodies' `covariates`".
- `statement.conditions` doc says "...any one of its bodies' covariates and conditions".
- `data_body.conditions` says "across the owner's conditions and covariates and this body's".
- T6 says "...and any one of its bodies'".
- The named rule therefore admits a duplicate that the docs forbid.

**B2. MEDIUM: one concept, two variables (the finer kind of a sample or material).**
- T1 amendment: "finer kind … is one `term` assertion (Sample Type for samples and materials …)".
- `V_eta_term_registry.json` registers "Sample Type" NCIT:C210102 ("decided": "Jess Haley, 2026-10-20"). `V_eta_term_registry_plan.md` says it is "registered as the variable that says what kind of thing a subject is (a patch's `bacterial patch`)".
- `subject_statement_bindings` holds no Sample Type row. Instead it binds `material type` EMPTY:0000354 and `culture type` EMPTY:0000357, the latter with values `[bacterial patch]` (TEAM-SIGN-OFF [term registry closed value sets] 2026-10-21).
- So a bacterial patch's kind has two candidate variables. Which one the Haley writer emits: not measured.

**B3. MEDIUM: epoch is modelled two ways.**
- `entity.type` includes `epoch`, and `ingestion_manifest.epoch_id`, `directed_relation.epoch_id` and `method.epoch_id` point at `entity`.
- `ensemble.element_epoch_id` instead points at `acquisition_epoch` (in_progress, a separate class with its own `clocks`, `dimensions`, `covariates` and `storage`).
- `acquisition_epoch.storage.format` is `char` ("vhsb | zarr | ome_ngff"), while the same concept on `data_body.format` is a bound `ontology_term`.
- `acquisition_epoch.storage.data_type` duplicates `value.data_type`. `value.data_type` doc: "the ONE place it lives".

**B4. MEDIUM: three copies of the "one fit entry", in three shapes.**
- `model_fit.value` (draft) has `equation`, `independent_variables`, `dependent_variable`, `constraints`, `input_field` and `output_field`.
- `tuning_curve_calculation.model_fit` and `contrast_sensitivity.value.model_fit` lack all of these and add `metrics` or per-frequency arrays.
- All three cite "#73 audit 2 D2: one fit entry for every fit".
- `model_fit.model` doc says "as a controlled term (T8)", but no binding is declared on any of the three.

**B5. MEDIUM: entry value forms differ while the docs say "the same entry as a covariate's".**
- `statement.conditions`, `data_body.conditions`, `interaction`/`method`/`relation`/`clock_alignment_configuration` `method.parameters`: forms are `term`, `quantity`, `count`, `text`, `matrix`, with `quantity.source_value` typed `char`.
- `data.covariates` adds `logical`, `origin`/`spacing` and `document`, and types `quantity.source_value` as `matrix`.
- The char/numeric split is signed (AMENDMENT 3: "source_value as text" vs "source_value numeric"). The **missing `logical` on conditions and parameters is not covered by any decision I found**. The T16 amendment (signed) says "an activity may be the variable when a logical value says whether it happened", and a condition cannot hold one.

**B6. MEDIUM: decided term not reflected in the doc.**
- `tuning_curve.value` doc: "the `stimulus condition` term is still to be chosen".
- `V_eta_data_body_model_plan.md`: "Decided by Jess Haley, 2026-10-22 [stimulus condition term]: … is XCO:0000000 "experimental condition"".

**B7. MEDIUM: binding-registry rows are inconsistent.**
- One `subject_statement_bindings` row is keyed to a retire class: `{"variable": "Gene Expression", "class": "spatial_gene_expression_pyramid", "term_valued": false}`. It uses `term_valued` where every other row uses `value_kind`.
- Kind-defining rows (species, Equipment Type, cell type, material type, culture type, developmental stage) carry no `entity_type`. The dataset and study rows do. So "species for organisms" (T1) is not declared.
- `relation_bindings` `child_types`/`parent_types` mix entity types with class names: `documented_by` `["entity","formulation"]`, gene mappings `["term"]`, `recorded_by` `["acquisition_system"]`.

**B8. LOW: stale names in docs.**
- "all of which are also data_types" (the class was renamed `value` 2026-10-08) appears in `statement.value_id`, `relation.value_id`, `directed_relation.child_id`, `directed_relation.parent_id` and `data_body.owner_id`.
- "`subject.type` group" (the field is `entity.type`) appears in `statement.distributive` and `directed_relation.distributive`.
- `interaction.instrument_id`: "an instrument modeled as a subject (kind asserted via a term_assertion)". The coarse kind is now `entity.type` device (T1 amendment), and `term_assertion` is a retired leaf name.
- `ensemble.neuron_id_#` and `stimulus_presentation.stimulus_element_id` say "Typed to `subject`". Both point at `entity`.
- `logical.value` still carries a long `valid_interval` passage, "SUPERSEDED IN PART … migrates to `time_observation`" (a retired leaf name).
- `acquisition_epoch.element_id`: "The document ID of the element" (the `element` class is retire).

**B9. LOW: edges whose required entity type exists only in prose.**
- `instrument_id`, `software_id`, `interpreter_id`, `operating_system_id`, `product_id`, `device_id`, `epoch_id` and `base.session_id` all point at plain `entity`. Their docs say device, software, epoch or session.
- `entity_field_bindings` has 1 row (`entity.type`). Nothing declarative stops, for example, `instrument_id` from naming an organism. Whether the validator checks this: not measured.

**B10. LOW: "never both" rule has no schema rule.** "inline `method` OR `method_id`, NEVER BOTH" (`interaction.method_id`) appears in no class `rules` block. The 15 declared rules were listed and it is not among them. Validator code was not inspected, so enforcement is not measured.

**B11. LOW: same field name, different shape.** `coordinate_system.dimensions` is `{axis, positive_direction, spacing}` and `coordinate_system.origin` is an ontology_term. `data.dimensions` is `{term, n, chunk}` and `covariates.origin` is `{value, source_value}`. The doc acknowledges the difference: "The same concept as a covariate's `origin`".

**B12. LOW: other loose ends.**
- Every `unit` (12), `response_unit` (3) and `native_unit` (1) field is unbound, while all 63 `source_unit` fields are bound `preferred`.
- `projectvar` sits in the `deprecated/` tier (tombstones) with disposition `in_progress`.
- `stimulus_presentation` and `ensemble` still inherit the v1 `app` class, although `interaction.software_id` "Supersedes the v1 `app` block".

---

## (C) Tenet gaps, conflicts and stale tenet text

**C1. MEDIUM: T2 conflicts with T15.** T2: "`input_id` is declared on `calculation` only". T15 (`V_eta_tenets.md` ~L632): "`input_id` is "what goes in" on a calculation … and on a clock alignment". The schema follows T15: `clock_alignment.input_id` points at `relative_time_reference`, `mustBeNonEmpty: true`. T2 needs the exception.

**C2. MEDIUM: T2 text is stale against a signed decision.**
- T2: "`method` (… `{term, parameters}` … proposed 2026-10-21, `V_eta_method_plan.md`, not signed …)".
- `V_eta_method_plan.md:188`: "TEAM-SIGN-OFF [method]: jess@walthamdatascience.com / 2026-10-21 -- one method shape {term, parameters} …".

**C3. MEDIUM (uncertain): T1 and T5 amendment signatures are not visible.**
- The T1 and T5 amendments say "signed by her 2026-10-21".
- The only sign-off line for the 2026-10-20 amendments (tenets L1017) lists "T6 … T14 … T16 … T19 … T3/T12-T16" and does not name T1 (T-4) or T5 (T-2).
- `grep 'T-4|T-2'` with sign/decided in `schemas/*.md` found nothing else.
- Absence elsewhere is not proof. This is flagged for the team to confirm.

**C4. LOW: T3 and T6 still use retired names.**
- T3 L119-120: "`timed_sequence`" and "`timed_sequence_manipulation`". The class has been `item` since 2026-10-04.
- T3 L156, T6 L195 and L198: "`datum_type` on the data type". The field is `value.data_type` (T2 itself says "`datum_type` is renamed `data_type`").
- T6 lists `datum_order` as a sampled_body layout field. It is declared on `data` (`data.datum_order`: "Declared on `sampled_body` only until 2026-10-20").
- T2 L76-77: "The leaves keep their names (`temperature_observation`, `term_assertion`)" is contradicted by the next paragraph ("there are no `temperature_observation` or `term_assertion` classes any more").
- Outside T1–T7, T15 L643 still cites "`timed_sequence.item_id`".
- AMENDMENT 6 [tenets follow covariates] says those passages were updated. The keys text was updated; these were not.

**C5. LOW: T7 is not aligned with T1.**
- T7: "The measuring/manipulating device is a subject (kind asserted)". Since the T1 amendment, the coarse kind is `entity.type` = device and only the finer kind is asserted (the `Equipment Type` binding).
- T7 also states no rule for the edge's target type (see B9).

**C6. LOW: modelling choices no tenet states.**
- T4 names only `directed_relation` and `undirected_relation`. `clock_alignment ⊂ relation, polynomial` has neither child/parent nor entity ends: it has 4 named edges. T3's relation-leaf note covers the value, not the endpoints.
- T2's interaction edge list omits `acquisition_channels_id` (interaction) and `interpreter_id`/`operating_system_id` (calculation).
- T2 says "An assertion has no act/series", but an assertion inherits `data.dimensions` and `covariates`, so a time-dimensioned assertion is not forbidden.
- T1's original "group-ness from incoming `member_of` edges" is not explicitly retired, though `entity.type` group now states it.
- The edge `key_id` keeps the retired "key" vocabulary while `keys` is gone (kept deliberately per AMENDMENT 6 "`document`: the 0-based position of a `key_id` entry"; a naming candidate only).

**C7. LOW (outside T1–T7, uncertain): `dose` vs T14 "missing is not a value".** `dose.value`: "A dose whose amount the source does not record … writes NaN in the quantity's canonical slot … (Jess Haley, 2026-10-21)". T14 (signed): "not attempted … no statement; attempted, not obtained: in an array, NaN". A given dose with an unrecorded amount fits neither case cleanly. Both lines are decisions, so the tenet should say which case governs.
