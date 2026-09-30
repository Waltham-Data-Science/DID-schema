# Audit C — ④ statement leaves + governance of the 182 persist classes

READ-ONLY. DID-schema HEAD `29bf9d6`. Nothing decided, no sign-off written. Every status below is a classification of the record, not a disposition.

## Summary

**Job 1, leaves.** DENOMINATOR: 91 leaf classes listed under ④ in `schemas/V_eta_final_class_set.md`, 91 built files read (0 missing, 0 duplicated), 47 ③ composites. 86 leaves are `super: [subject_<direction>, <composite>]`, direction first, and declare no fields and no deps. 5 leaves have a single parent, `tuning_curve_calculation`, which is the signed and #73-amended shape. **7 leaves declare content:** the 6 tuning-calculation leaves (fields) plus `image_observation` and `term_assertion` (one optional edge each). No leaf has an extra parent or a wrong parent order. No stable leaf sits on a draft composite.
Findings: 2 INCONSISTENCY, 3 STALE-DOC, 4 QUESTION (below).

**Job 2, governance.** DENOMINATOR: 56 `schemas/*.md` read, 3 generated files excluded (the `status_board.GENERATED_MARKDOWN` list), 53 scanned with `status_board.scan_signoff_lines`. That found 50 line-initial `TEAM-SIGN-OFF` lines, all accepted by the parser. Two of the 50 should not count as decisions:
- `V_eta_method_parameters_plan.md:683` is a QUOTATION inside a code fence.
- `V_eta_go_forward_class_audit.md:796` was superseded by #73.

`status_board.signed_families()` gives 25 of the 27 families as signed. **Every family is keyed by v1 SOURCE classes, so the board certifies no V_eta target class directly.** For that reason the table below matches the text of each sign-off against the class, by hand.

| status | ① | ② | ③ | ④ | ⑤ | ⑥ | ⑦ | total |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| SIGNED (a sign-off names the class, or names it through a table or list it points to) | 0 | 13 | 10 | 13 | 1 | 0 | 9 | **46** |
| SIGNED, REVISED-UNSIGNED (signed under an older name or shape; the current form carries an unsigned #73 or later revision) | 2 | 0 | 1 | 8 | 2 | 2 | 1 | **16** |
| PARTIAL (a sign-off decides only a field or edge ON the class, not the class) | 4 | 0 | 0 | 0 | 0 | 0 | 0 | **4** |
| DECIDED-UNSIGNED | 0 | 0 | 7 | 10 | 0 | 0 | 2 | **19** |
| NO RECORD FOUND | 8 | 0 | 29 | 60 | 0 | 0 | 0 | **97** |
| **total** | 14 | 13 | 47 | 91 | 3 | 2 | 12 | **182** |

**Answer to "are there really 182 approved classes?"** No, not by the repository's own standard (Operating Rule 4).
- **46** carry a sign-off that names them in their current form.
- **16** more were signed in an earlier form and have since changed without a signature.
- **97** have no decision record I could find.
  - The largest block is the dimensioned-quantity composites (29) and their `_assertion` / `_observation` / `_manipulation` leaves (60), which came mostly from V_epsilon, V_zeta or early V_eta according to `V_eta_class_provenance.md`.
  - Their only positive mention is `V_eta_tenet_audit.md:99-121` ("✅ Fully conceived"). That is an audit's assessment ("conform to the tenets by construction"), not a decision, and it names leaves only as "≈72 of 78".
  - This absence is not evidence that they were never decided. They may predate the sign-off convention.

"Persist" is `_disposition()` in `tools/build_v_eta.py`, a build marker, not an approval.

## Job 1 — the direction × data_type grid

Legend: Y = a leaf exists, · = no leaf. The 5 per-family tuning leaves hang off `tuning_curve_calculation` and are counted on the `tuning_curve` row.

| composite | assertion | observation | manipulation | calculation |
|---|:-:|:-:|:-:|:-:|
| `acceleration` | Y | Y | · | · |
| `amount` | Y | Y | · | · |
| `angle` | Y | Y | · | · |
| `angular_velocity` | Y | Y | · | · |
| `area` | Y | Y | · | Y |
| `capacitance` | Y | Y | · | · |
| `charge` | Y | Y | · | · |
| `chemical` | · | · | · | · |
| `clock_alignment` | · | · | · | · |
| `concentration` | Y | Y | Y | · |
| `conductance` | Y | Y | · | · |
| `contrast_sensitivity` | · | · | · | Y |
| `count` | Y | Y | · | Y |
| `current` | Y | Y | Y | · |
| `date` | Y | · | · | · |
| `dose` | · | · | Y | · |
| `energy` | Y | Y | · | · |
| `force` | Y | Y | Y | · |
| `formulation` | · | · | Y | · |
| `frequency` | Y | Y | Y | · |
| `gain` | Y | Y | · | · |
| `harmonic_component` | · | · | · | Y |
| `hartley_reverse_correlation` | · | · | · | · |
| `image` | · | Y | Y | · |
| `intensity` | Y | Y | Y | · |
| `label` | · | · | · | Y |
| `length` | Y | Y | · | · |
| `logical` | · | Y | · | · |
| `mass` | Y | Y | · | · |
| `ph` | Y | Y | · | · |
| `polynomial` | · | · | · | · |
| `position` | · | Y | · | Y |
| `power` | Y | Y | · | · |
| `pressure` | Y | Y | Y | · |
| `receptive_field` | · | · | · | Y |
| `resistance` | Y | Y | · | · |
| `reverse_correlation` | · | · | · | · |
| `score` | Y | Y | · | Y |
| `temperature` | Y | Y | Y | · |
| `term` | Y | Y | Y | Y |
| `time` | Y | Y | · | · |
| `timed_sequence` | · | · | Y | · |
| `tuning_curve` | · | · | · | Y (+5 family leaves) |
| `velocity` | Y | Y | · | · |
| `visual_grating` | · | · | Y | · |
| `voltage` | Y | Y | Y | · |
| `volume` | Y | Y | · | · |

Column totals: assertion 30, observation 32, manipulation 14, calculation 10, plus the 5 tuning-family leaves, which makes 91. Five composites have **no leaf**: `chemical`, `polynomial`, `clock_alignment`, `reverse_correlation`, `hartley_reverse_correlation`.
- `polynomial` has no leaf by design: it is a parent of `clock_alignment` (sign-off at `V_eta_clock_alignment_cluster_plan.md:495`).
- `clock_alignment` is **filed under ③ but is not a data_type composite**: `draft/clock_alignment.json` has superclasses `[relation, polynomial]`. It is a relation that carries a polynomial value.

## Job 1 — leaf findings, most severe first

1. **INCONSISTENCY — `reverse_correlation` and `hartley_reverse_correlation` are fieldless marker subclasses of `receptive_field`, and the same review dropped the tuning markers for exactly that.**
   - Both are built as `superclasses: [receptive_field]` / `[reverse_correlation]`, with `fields: []`, `depends_on: []` (`stable/reverse_correlation.json`, `stable/hartley_reverse_correlation.json`), and both are persist.
   - The signed RF fold says the method "becomes a bound term on the composite, NOT part of the class name" (`V_eta_ngrid_family_findings.md:358`). `receptive_field.value.method` exists.
   - #73 dropped the five tuning markers on the same grounds: "abstract with no fields ... already `...variable`" (`V_eta_tuning_model_plan.md:167-172`).
   - Neither class has a leaf. Their only child is the retired `hartley_calc` tombstone (`V_eta_subject_calculation_plan.md:310-311`).
   - *Suggestion:* ask the team whether they go the way of the tuning markers, with `hartley_calc` re-parented onto `receptive_field`.

2. **INCONSISTENCY — `image_observation` declares a leaf-level edge whose target class is being retired.**
   - The edge is `draft/image_observation.json` `depends_on[0]` = `ontology_table_row_id → ontology_table_row` (optional).
   - `ontology_table_row` has `disposition: retire` in `index.json` ("→ observations (needs-NDI / D10-11)").
   - The signed R6 model says `image_observation ⊂ subject_observation, image — no fields of its own` (`V_eta_image_model_plan.md:159`).
   - The edge was added "at the team's direction" on 2026-08-11 (`tools/build_v_eta.py:6647-6649`), with no sign-off. The same comment says the emitter still drops it (`:6669-6672`).
   - *Suggestion:* decide where this edge should point once #53 fans `ontologyTableRow` out into typed statements, and record that decision in the image plan.

3. **STALE-DOC — `V_eta_migration_targets.json` still routes the stimulus second pass to the superseded leaf.**
   - `/classes/stimulus_presentation/second_pass = ["visual_grating_manipulation", "sampled_body"]`, and its `how` says "assembles ONE body-backed visual_grating_manipulation".
   - The signed target is `timed_sequence_manipulation`. `visual_grating_manipulation` is kept only for the presentation-less single-grating case (`V_eta_stimulus_model_plan.md:224`, `:270`).
   - `timed_sequence_manipulation` does not appear anywhere in that JSON (`grep -c '"timed_sequence_manipulation"'` = 0).
   - The two leaves may coexist, and that part is signed. Only the target map is stale.
   - *Suggestion:* repoint `second_pass` to `timed_sequence_manipulation`, `visual_grating`, `sampled_body`.

4. **STALE-DOC — the same JSON names a leaf that no longer exists.**
   - `"duration_observation"` occurs twice: in the `targets` of `measurement` and of `ontology_table_row`.
   - No `duration_observation.json` exists (renamed to `time_observation` by `[time dtype]`, `V_eta_tenet_audit.md:520`).
   - The DID-matlab migrator already emits `time_observation` (`+migrators_j/ontology_table_row.m:695`, local checkout at `47cf8ba`; `git fetch` not re-run, so the checkout may be behind origin).
   - *Suggestion:* re-run the targets refresh through `tools/gates.py` and confirm the stale name is gone.

5. **QUESTION — `logical_observation` persists with no consumer.**
   - Amendment 1 moved its only user (`valid_interval`) to `time_observation`, and left `logical` and `logical_observation` "minted and unused ... retired or held ... NOT decided" (`V_eta_logical_observation_plan.md:420`).
   - `logical` has since gained a standalone-value use (#73 item 24, `V_eta_spatial_transcriptomics_plan.md:105`). The leaf has not.
   - *Suggestion:* ask the team for a retire-or-hold decision on the leaf alone.

6. **QUESTION (T12) — manipulation leaves resting only on a code comment.**
   - `voltage_manipulation`, `current_manipulation`, `force_manipulation` and `concentration_manipulation` are minted at `tools/build_v_eta.py:8623-8628` ("IMPOSABLE subset of data_types (Q2) ... velocity, power, ph, angular_velocity are candidates left off pending confirmation").
   - `grep -rl` over `schemas/*.md` finds no plan document naming any of the four, and none is a target in `V_eta_migration_targets.json`.
   - `concentration_manipulation` also overlaps the signed `dose_manipulation` ("the delivered substance", `V_eta_go_forward_class_audit.md:719`).
   - *Suggestion:* record what "Q2" was, or put these four on the team list.

7. **QUESTION (T12) — `gain_assertion` / `gain_observation` have no warrant on record.**
   - Zero mentions in any `schemas/*.md` (`grep -lw` returns nothing), and no migrator target.
   - `gain` was minted "for exactly these two fields" of `frequency_filter` (`V_eta_frequency_filter_model_plan.md:125`), which uses it as a field type, not as a statement leaf.
   - Wider denominator: **53 of 91 leaves appear nowhere in `V_eta_migration_targets.json`**. That is not evidence they are unused (second passes such as `timed_sequence_manipulation` do not appear there either), but it is the population T12 would have to justify.
   - *Suggestion:* team review of leaves that have no emitter and no plan line.

8. **QUESTION (T2 provenance) — two v1 sources are routed to `_observation` leaves although their inputs are in the dataset.**
   - `fitcurve` → `score_observation` ("generic curve fit -> a goodness-of-fit score_observation").
   - `neuron_extracellular` → `score_observation` + `voltage_observation` (a sorted unit's sort quality and waveform).
   - Both are in `V_eta_migration_targets.json` `/classes/*/targets`.
   - Under the #73 provenance rule (`V_eta_tenets.md` T2, "inputs are other statements in the dataset → subject_calculation"), and by the same reasoning the team applied to sorters (`V_eta_subject_calculation_plan.md:338-356`), these read as calculations. `score_calculation` exists; `voltage_calculation` does not.
   - *Suggestion:* put both on the #73 follow-up list next to the sorter retarget.

9. **STALE-DOC — T2 and T3 prose still describe structure that decisions have retired.**
   - `V_eta_tenets.md` T2 says an interaction "adds ... a per-sample `sample_time` cadence". The signed data_body decision retires both `sample_time` blocks (`V_eta_data_body_model_plan.md:648`). The statement-side block is still built on `subject_interaction` and is recorded as a pending build (`tools/build_v_eta.py:6486-6487`), so all 61 observation, manipulation and calculation leaves still inherit it.
   - T3 says the undimensioned value's "`dtype`/`axes` live on the body" and cites "a receptive-field map" as the example. #73 item 14 renamed `axes → keys` and `dtype` is now `datum_type` (`V_eta_spatial_transcriptomics_plan.md:70`, `:79`), and a receptive field is now the signed `receptive_field` composite.
   - `V_eta_tenet_audit.md:120` still lists the deleted `numeric_assertion` among the conformant leaves.
   - *Suggestion:* amend T2, T3 and `tenet_audit.md:120` in the next prose pass.

**Checked and clean:**
- Leaf-level documentation, on the 7 leaves that carry any (all read): no mention of `axes`, `is_`, 1-based indexing or a deleted class. The one grid reference is `independent_variables[] order`, which matches the built `tuning_curve.value.independent_variables`.
- The tuning-leaf fields (`significance`, `model_fit` on the parent; `circular_statistics` on orientation/direction; `interpolated_values` on contrast, SF and TF; none on speed) match the #73 amendment item 4 exactly (`V_eta_tuning_model_plan.md:196-202`). This is a justified exception to "leaves are empty".
- `term_assertion.strain_id` is signed (`V_eta_openminds_family_record.md:20`).
- `visual_grating_manipulation` coexisting with `timed_sequence_manipulation` is signed (`V_eta_stimulus_model_plan.md:270`). Note that line is an ORPHAN tag (`:329`): it reaches no family on the board.

## Job 2 — governance table (182 persist classes)

Plan-document names are abbreviated, with the `V_eta_` prefix dropped: `spatial…plan` is `V_eta_spatial_transcriptomics_plan.md` and `tenet_audit` is `V_eta_tenet_audit.md`.

Three reading notes:
- **The "six classes" reference.** The openMINDS sign-off (`openminds_family_record.md:10`) covers "the six classes `metadata_editor` already emits". `:1268` lists SEVEN (it also includes `directed_relation`), so I matched only the six entities.
- **`harmonic_component_calculation` is classified SIGNED, against the brief's example.** `stimulus_response_model_plan.md:541` signs it. I found no sign-off for its #67 deletion, and #73 item 37 restores the signed shape.
- **Superseded sign-off.** The spatial sign-off (`go_forward_class_audit.md:796`) covers only retired classes, and #73 supersedes it.

| class | cat | status | evidence |
|---|---|---|---|
| `base` | ① | PARTIAL (field-level sign-off only) | tenet_audit.md:516 [base naming] (base.datestamp→creation_timestamp); audit only: tenet_audit.md:103 (✅ list), :303 ("reviewed, nothing flagged"); provenance did_v1 |
| `data` | ① | NO RECORD FOUND | audit only: tenet_audit.md:103 (✅ list), :303 ("reviewed, nothing flagged") |
| `data_body` | ① | SIGNED, REVISED-UNSIGNED | data_body_model_plan.md:648 [data_body]; revised unsigned by #73 items 17/20/25/31 (V_eta_spatial_transcriptomics_plan.md:80-85,:123,:108-111,:126) |
| `data_type` | ① | NO RECORD FOUND | audit only: tenet_audit.md:103 (✅ list), :303 ("reviewed, nothing flagged"); #73 item 19 (V_eta_spatial_transcriptomics_plan.md:91) keeps it abstract — unsigned |
| `directed_relation` | ① | PARTIAL (field-level sign-off only) | epoch_plan.md:878 [epoch] (epoch_id edge on directed_relation); audit only: tenet_audit.md:103 (✅ list), :303 ("reviewed, nothing flagged") |
| `entity` | ① | NO RECORD FOUND | audit only: tenet_audit.md:103 (✅ list), :303 ("reviewed, nothing flagged") |
| `relation` | ① | NO RECORD FOUND | audit only: tenet_audit.md:103 (✅ list), :303 ("reviewed, nothing flagged"); #73 items 24/30 add method/value_id (V_eta_spatial_transcriptomics_plan.md:105,:123) — unsigned |
| `subject_assertion` | ① | NO RECORD FOUND | audit only: tenet_audit.md:103 (✅ list), :303 ("reviewed, nothing flagged"); V_eta_SPEC.md:121-131 (spec); provenance V_epsilon |
| `subject_calculation` | ① | SIGNED, REVISED-UNSIGNED | subject_calculation_plan.md:265 [calculator + subject_calculation restructure] item (2); revised unsigned by #73 amendment :281-300 (calculator mixin dropped) and T2 amendment :317- |
| `subject_interaction` | ① | PARTIAL (field-level sign-off only) | tenet_audit.md:429 [binding governance] (method bound); audit only: tenet_audit.md:103 (✅ list), :303 ("reviewed, nothing flagged") |
| `subject_manipulation` | ① | NO RECORD FOUND | audit only: tenet_audit.md:103 (✅ list), :303 ("reviewed, nothing flagged"); provenance V_epsilon |
| `subject_observation` | ① | NO RECORD FOUND | audit only: tenet_audit.md:103 (✅ list), :303 ("reviewed, nothing flagged"); derived_from_# removed by #73 (subject_calculation_plan.md:317-, unsigned) |
| `subject_statement` | ① | PARTIAL (field-level sign-off only) | tenet_audit.md:429 [binding governance] (variable bound); audit only: tenet_audit.md:103 (✅ list), :303 ("reviewed, nothing flagged") |
| `undirected_relation` | ① | NO RECORD FOUND | audit only: tenet_audit.md:103 (✅ list), :303 ("reviewed, nothing flagged"); provenance V_eta |
| `acquisition_system` | ② | SIGNED | daq_family_decisions.md:471 [daq configuration] ("daqsystem -> acquisition_system ⊂ entity") |
| `dataset` | ② | SIGNED | openminds_family_record.md:10 (untagged; "six classes metadata_editor already emits", enumerated at :1268 — which lists SEVEN incl. directed_relation); field retype tenet_audit.md:512 |
| `epoch` | ② | SIGNED | epoch_plan.md:878 [epoch] ("MINT epoch as an entity") |
| `funding` | ② | SIGNED | openminds_family_record.md:10 by reference to :1268 (same six/seven caveat) |
| `organization` | ② | SIGNED | openminds_family_record.md:10 by reference to :1268 (same caveat) |
| `person` | ② | SIGNED | openminds_family_record.md:10 by reference to :1268 (same caveat) |
| `publication` | ② | SIGNED | openminds_family_record.md:10 by reference to :1268; field rename tenet_audit.md:512 [date dtype] |
| `runtime_environment` | ② | SIGNED | subject_calculation_plan.md:265 item (3) — stands per #73 amendment :283-285 ("items (3)-(5) stand") |
| `session` | ② | SIGNED | go_forward_class_audit.md:658 [session] |
| `software` | ② | SIGNED | tenet_audit.md:10 [software]; daq_family_decisions.md:519,:522 |
| `strain` | ② | SIGNED | openminds_family_record.md:20 and :10 (untagged) |
| `subject` | ② | SIGNED | go_forward_class_audit.md:691 [subject] |
| `web_resource` | ② | SIGNED | openminds_family_record.md:10 by reference to :1268 (same caveat) |
| `acceleration` | ③ | NO RECORD FOUND | audit only: tenet_audit.md:110-116 (✅ "fully conceived" — an assessment, not a decision) |
| `amount` | ③ | NO RECORD FOUND | audit only: tenet_audit.md:110-116 (✅ "fully conceived" — an assessment, not a decision) |
| `angle` | ③ | NO RECORD FOUND | audit only: tenet_audit.md:110-116 (✅ "fully conceived" — an assessment, not a decision) |
| `angular_velocity` | ③ | NO RECORD FOUND | audit only: tenet_audit.md:110-116 (✅ "fully conceived" — an assessment, not a decision) |
| `area` | ③ | NO RECORD FOUND | audit only: tenet_audit.md:110-116 (✅ "fully conceived" — an assessment, not a decision) |
| `capacitance` | ③ | NO RECORD FOUND | audit only: tenet_audit.md:110-116 (✅ "fully conceived" — an assessment, not a decision) |
| `charge` | ③ | NO RECORD FOUND | audit only: tenet_audit.md:110-116 (✅ "fully conceived" — an assessment, not a decision) |
| `chemical` | ③ | NO RECORD FOUND | audit only: tenet_audit.md:115 (substances, ✅ assessment) |
| `clock_alignment` | ③ | SIGNED | clock_alignment_cluster_plan.md:495 [sync mapping] ("clock_alignment (⊂ relation, polynomial)") |
| `concentration` | ③ | NO RECORD FOUND | audit only: tenet_audit.md:110-116 (✅ "fully conceived" — an assessment, not a decision) |
| `conductance` | ③ | NO RECORD FOUND | audit only: tenet_audit.md:110-116 (✅ "fully conceived" — an assessment, not a decision) |
| `contrast_sensitivity` | ③ | DECIDED-UNSIGNED | tenet_audit.md:376-385 ("RESHAPED and back to persist ... stays its own class") |
| `count` | ③ | NO RECORD FOUND | audit only: tenet_audit.md:110-116 (✅ "fully conceived" — an assessment, not a decision) |
| `current` | ③ | NO RECORD FOUND | audit only: tenet_audit.md:110-116 (✅ "fully conceived" — an assessment, not a decision) |
| `date` | ③ | DECIDED-UNSIGNED | tenet_audit.md:330 ((B) "term and date are now real ③ composites"); tenet_audit.md:512 [date dtype] signs the DTYPE, not this class |
| `dose` | ③ | NO RECORD FOUND | audit only: tenet_audit.md:115 (substances, ✅ assessment) |
| `energy` | ③ | NO RECORD FOUND | audit only: tenet_audit.md:110-116 (✅ "fully conceived" — an assessment, not a decision) |
| `force` | ③ | NO RECORD FOUND | audit only: tenet_audit.md:110-116 (✅ "fully conceived" — an assessment, not a decision) |
| `formulation` | ③ | NO RECORD FOUND | audit only: tenet_audit.md:115 (substances, ✅ assessment) |
| `frequency` | ③ | NO RECORD FOUND | audit only: tenet_audit.md:110-116 (✅ "fully conceived" — an assessment, not a decision) |
| `gain` | ③ | SIGNED | frequency_filter_model_plan.md:5 (untagged, "model as written below") + :125 ("The gain data_type ... was added for exactly these two fields") |
| `harmonic_component` | ③ | SIGNED | stimulus_response_model_plan.md:541 [stimulus response] |
| `hartley_reverse_correlation` | ③ | DECIDED-UNSIGNED | subject_calculation_plan.md:310-311 (#73 knock-on: hartley_calc ⊂ [base, hartley_reverse_correlation]) — presupposes it persists |
| `image` | ③ | SIGNED, REVISED-UNSIGNED | image_model_plan.md:144 [image / ngrid]; revised unsigned by #73 item 16 (V_eta_spatial_transcriptomics_plan.md:78, value = {keys, complete, pixels}) |
| `intensity` | ③ | NO RECORD FOUND | audit only: tenet_audit.md:110-116 (✅ "fully conceived" — an assessment, not a decision) |
| `label` | ③ | DECIDED-UNSIGNED | V_eta_spatial_transcriptomics_plan.md:129 item 33; T12 text tenets "team, 2026-09-24" |
| `length` | ③ | NO RECORD FOUND | audit only: tenet_audit.md:110-116 (✅ "fully conceived" — an assessment, not a decision) |
| `logical` | ③ | SIGNED | logical_observation_plan.md:360 [logical_observation]; :420 amendment leaves it "minted and unused", retire-or-hold NOT decided |
| `mass` | ③ | NO RECORD FOUND | audit only: tenet_audit.md:110-116 (✅ "fully conceived" — an assessment, not a decision) |
| `ph` | ③ | NO RECORD FOUND | audit only: tenet_audit.md:110-116 (✅ "fully conceived" — an assessment, not a decision) |
| `polynomial` | ③ | SIGNED | clock_alignment_cluster_plan.md:495 [sync mapping] (named as clock_alignment parent) |
| `position` | ③ | DECIDED-UNSIGNED | V_eta_spatial_transcriptomics_plan.md:41 item 4 |
| `power` | ③ | NO RECORD FOUND | audit only: tenet_audit.md:110-116 (✅ "fully conceived" — an assessment, not a decision) |
| `pressure` | ③ | NO RECORD FOUND | audit only: tenet_audit.md:110-116 (✅ "fully conceived" — an assessment, not a decision) |
| `receptive_field` | ③ | SIGNED | ngrid_family_findings.md:358 [receptive field fold], :381 [receptive field naming] |
| `resistance` | ③ | NO RECORD FOUND | audit only: tenet_audit.md:110-116 (✅ "fully conceived" — an assessment, not a decision) |
| `reverse_correlation` | ③ | DECIDED-UNSIGNED | V_eta_spatial_transcriptomics_plan.md:154 item 38 (ngrid dropped from it — presupposes it persists); ngrid_family_findings.md:358 signs only that its `method` becomes a term "NOT part of the class name" |
| `score` | ③ | NO RECORD FOUND | audit only: tenet_audit.md:110-116 (✅ "fully conceived" — an assessment, not a decision) |
| `temperature` | ③ | NO RECORD FOUND | audit only: tenet_audit.md:110-116 (✅ "fully conceived" — an assessment, not a decision) |
| `term` | ③ | DECIDED-UNSIGNED | tenet_audit.md:330 ((B)); used as standalone doc by #73 item 21 (V_eta_spatial_transcriptomics_plan.md:94) |
| `time` | ③ | SIGNED | tenet_audit.md:520 [time dtype] |
| `timed_sequence` | ③ | SIGNED | stimulus_model_plan.md:224 [stimulus] |
| `tuning_curve` | ③ | SIGNED | tuning_model_plan.md:144 item (2); #73 amendment keeps items (2)-(4) (:160-164) |
| `velocity` | ③ | NO RECORD FOUND | audit only: tenet_audit.md:110-116 (✅ "fully conceived" — an assessment, not a decision) |
| `visual_grating` | ③ | SIGNED | stimulus_model_plan.md:270 [stimulus -- visual_grating_manipulation reconciliation] (orphan tag, see :329) |
| `voltage` | ③ | NO RECORD FOUND | audit only: tenet_audit.md:110-116 (✅ "fully conceived" — an assessment, not a decision) |
| `volume` | ③ | NO RECORD FOUND | audit only: tenet_audit.md:110-116 (✅ "fully conceived" — an assessment, not a decision) |
| `acceleration_assertion` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `acceleration_observation` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed); emitted under the recording pattern `<modality>_observation` signed at recording_observation_plan.md:99 (pattern, class not named) |
| `amount_assertion` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `amount_observation` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `angle_assertion` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `angle_observation` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `angular_velocity_assertion` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `angular_velocity_observation` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `area_assertion` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `area_calculation` | ④ | DECIDED-UNSIGNED | V_eta_spatial_transcriptomics_plan.md:34-35 item 3 (per-cell measures are calculations), built list :179 |
| `area_observation` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `capacitance_assertion` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `capacitance_observation` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `charge_assertion` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `charge_observation` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `concentration_assertion` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `concentration_manipulation` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed); only rationale is a code comment build_v_eta.py:8623-8628 ("IMPOSABLE subset ... (Q2)"), no plan record |
| `concentration_observation` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `conductance_assertion` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `conductance_observation` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `contrast_sensitivity_calculation` | ④ | DECIDED-UNSIGNED | tenet_audit.md:376-385; subject_calculation_plan.md (composite-leaf rule) |
| `contrast_tuning_calculation` | ④ | SIGNED, REVISED-UNSIGNED | tuning_model_plan.md:144 item (1) as `contrasttuning_calc`; #73 rename, unsigned |
| `count_assertion` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `count_calculation` | ④ | DECIDED-UNSIGNED | V_eta_spatial_transcriptomics_plan.md:136-138 item 29 |
| `count_observation` | ④ | SIGNED | go_forward_class_audit.md:717 via table :710 (jrclust_clusters); its use for sorters is revised to label_calculation (subject_calculation_plan.md:338-356, unsigned) |
| `current_assertion` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `current_manipulation` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed); only rationale is a code comment build_v_eta.py:8623-8628 ("IMPOSABLE subset ... (Q2)"), no plan record |
| `current_observation` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed); emitted under the recording pattern `<modality>_observation` signed at recording_observation_plan.md:99 (pattern, class not named) |
| `date_assertion` | ④ | DECIDED-UNSIGNED | tenet_audit.md:330 ((B), date leaves pair with the new composite); V_eta_SPEC.md:128 |
| `dose_manipulation` | ④ | SIGNED | go_forward_class_audit.md:719 [confirm sheet 2026-08-22]; :717 via table :709 |
| `energy_assertion` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `energy_observation` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `force_assertion` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `force_manipulation` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed); only rationale is a code comment build_v_eta.py:8623-8628 ("IMPOSABLE subset ... (Q2)"), no plan record |
| `force_observation` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `formulation_manipulation` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `frequency_assertion` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `frequency_manipulation` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `frequency_observation` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `gain_assertion` | ④ | NO RECORD FOUND | no mention in any schemas/*.md (grep -lw returns none); gain composite exists for frequency_filter only (frequency_filter_model_plan.md:125) |
| `gain_observation` | ④ | NO RECORD FOUND | no mention in any schemas/*.md (grep -lw returns none); gain composite exists for frequency_filter only (frequency_filter_model_plan.md:125) |
| `harmonic_component_calculation` | ④ | SIGNED | stimulus_response_model_plan.md:541 [stimulus response]. Deleted by #67 decision 10 (no sign-off line found for that deletion) and restored by #73 item 37 (V_eta_spatial_transcriptomics_plan.md:148); the restoration returns it to the SIGNED 2026-08-08 shape |
| `image_manipulation` | ④ | DECIDED-UNSIGNED | image_model_plan.md:94 (build task 2) and :161 (under the "SIGNED OFF 2026-08-08" heading, but the line :144 names only ngrid + image) |
| `image_observation` | ④ | SIGNED, REVISED-UNSIGNED | ingested_payload_findings.md:276 [daq ingested payloads] ("image_observation, all of which are now themselves signed"); image_model_plan.md:159 "no fields of its own" — ontology_table_row_id edge added 2026-08-11 "at the team's direction" (build_v_eta.py:6647-6649), no sign-off |
| `intensity_assertion` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `intensity_manipulation` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `intensity_observation` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `label_calculation` | ④ | DECIDED-UNSIGNED | V_eta_spatial_transcriptomics_plan.md:115-119,:145 items 27/28/35; subject_calculation_plan.md:349 (2026-09-24 amendment) |
| `length_assertion` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `length_observation` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `logical_observation` | ④ | SIGNED | logical_observation_plan.md:360; its only use withdrawn by :420 amendment 1 — "retired or held ... NOT decided" |
| `mass_assertion` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `mass_observation` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `orientation_direction_tuning_calculation` | ④ | SIGNED, REVISED-UNSIGNED | tuning_model_plan.md:144 item (1) as `oridirtuning_calc`; renamed + typed block by #73 amendment :160- (items 3-4, :196-202), unsigned |
| `ph_assertion` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `ph_observation` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `position_calculation` | ④ | DECIDED-UNSIGNED | V_eta_spatial_transcriptomics_plan.md:41-42 item 4, :60 item 11 |
| `position_observation` | ④ | DECIDED-UNSIGNED | V_eta_spatial_transcriptomics_plan.md:41-42 item 4 |
| `power_assertion` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `power_observation` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `pressure_assertion` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `pressure_manipulation` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `pressure_observation` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `receptive_field_calculation` | ④ | SIGNED | ngrid_family_findings.md:358, :381 |
| `resistance_assertion` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `resistance_observation` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `score_assertion` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `score_calculation` | ④ | DECIDED-UNSIGNED | V_eta_spatial_transcriptomics_plan.md:112-114 item 26 |
| `score_observation` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `spatial_frequency_tuning_calculation` | ④ | SIGNED, REVISED-UNSIGNED | tuning_model_plan.md:144 item (1) as `spatial_frequency_tuning_calc`; #73 rename, unsigned |
| `speed_tuning_calculation` | ④ | SIGNED, REVISED-UNSIGNED | tuning_model_plan.md:144 item (1) as `speedtuning_calc`; #73 rename, unsigned |
| `temperature_assertion` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `temperature_manipulation` | ④ | SIGNED | go_forward_class_audit.md:717 via table :709 (treatment) |
| `temperature_observation` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed); emitted under the recording pattern `<modality>_observation` signed at recording_observation_plan.md:99 (pattern, class not named) |
| `temporal_frequency_tuning_calculation` | ④ | SIGNED, REVISED-UNSIGNED | tuning_model_plan.md:144 item (1) as `temporal_frequency_tuning_calc`; #73 rename, unsigned |
| `term_assertion` | ④ | SIGNED | openminds_family_record.md:20 (strain_id edge on term_assertion) |
| `term_calculation` | ④ | DECIDED-UNSIGNED | V_eta_spatial_transcriptomics_plan.md:115-117 item 27 |
| `term_manipulation` | ④ | SIGNED | go_forward_class_audit.md:717 via table :709 (treatment) |
| `term_observation` | ④ | SIGNED | OPEN_WORK.md:2969 [stranded sources]; go_forward_class_audit.md:717 via table :708-709; :719 |
| `time_assertion` | ④ | SIGNED | tenet_audit.md:520 [time dtype] |
| `time_observation` | ④ | SIGNED | tenet_audit.md:520 [time dtype]; ensemble_plan.md:218; logical_observation_plan.md:420 |
| `timed_sequence_manipulation` | ④ | SIGNED, REVISED-UNSIGNED | stimulus_model_plan.md:224 [stimulus]; #73 item 30 replaces its timed_sequence_id with value_id — "team sign-off owed" (V_eta_spatial_transcriptomics_plan.md:123-125) |
| `tuning_curve_calculation` | ④ | SIGNED, REVISED-UNSIGNED | tuning_model_plan.md:144 item (1) (as ABSTRACT leaf); made concrete + fields retyped by #73 amendment tuning_model_plan.md:160-, unsigned |
| `velocity_assertion` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `velocity_observation` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `visual_grating_manipulation` | ④ | SIGNED | stimulus_model_plan.md:270 (RETAINED for single-grating case; ORPHAN tag per :329 — reaches no family) |
| `voltage_assertion` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `voltage_manipulation` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed); only rationale is a code comment build_v_eta.py:8623-8628 ("IMPOSABLE subset ... (Q2)"), no plan record |
| `voltage_observation` | ④ | SIGNED | recording_observation_plan.md:106 [raw recording observation] (and :99 pattern `<modality>_observation`) |
| `volume_assertion` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `volume_observation` | ④ | NO RECORD FOUND | audit only: tenet_audit.md:117-121 (✅ "≈72 of 78" leaves, unnamed) |
| `absolute_time_reference` | ⑤ | SIGNED, REVISED-UNSIGNED | time_reference_model_plan.md:468 (as `absolute_reference`); renamed unsigned by #73 item 10 (V_eta_spatial_transcriptomics_plan.md:58) |
| `relative_time_reference` | ⑤ | SIGNED, REVISED-UNSIGNED | time_reference_model_plan.md:468 (as `relative_reference`); renamed unsigned by #73 item 10 (V_eta_spatial_transcriptomics_plan.md:58) |
| `time_reference` | ⑤ | SIGNED | time_reference_model_plan.md:468 [time_reference] ("clock_tolerance on the root") |
| `opaque_body` | ⑥ | SIGNED, REVISED-UNSIGNED | OPEN_WORK.md:2969 [stranded sources] ("generic_file folds to term_observation + opaque_body"); #73 items 17/25 unsigned |
| `sampled_body` | ⑥ | SIGNED, REVISED-UNSIGNED | data_body_model_plan.md:648 [data_body]; revised unsigned by #73 items 14/17 (V_eta_spatial_transcriptomics_plan.md:70,:80) |
| `acquisition_channels` | ⑦ | SIGNED | clock_alignment_cluster_plan.md:493 [sync configuration] ("devices become `acquisition_channels_#` edges"; edge targets class acquisition_channels in built clock_alignment_configuration.json) |
| `acquisition_metadata_file` | ⑦ | SIGNED | ingested_payload_findings.md:276 [daq ingested payloads] |
| `acquisition_metadata_reader` | ⑦ | SIGNED | daq_family_decisions.md:471 [daq configuration] |
| `acquisition_reader` | ⑦ | SIGNED | daq_family_decisions.md:519, :522 [daq configuration] |
| `clock_alignment_configuration` | ⑦ | SIGNED | clock_alignment_cluster_plan.md:493, :625 |
| `clock_alignment_policy` | ⑦ | SIGNED | clock_alignment_cluster_plan.md:493 [sync configuration] |
| `coordinate_system` | ⑦ | DECIDED-UNSIGNED | V_eta_spatial_transcriptomics_plan.md:44-57 items 5-9 |
| `demo` | ⑦ | DECIDED-UNSIGNED | go_forward_class_audit.md:285-299 ("THREE CLASSES COLLAPSE TO ONE", "The team's words: Let's do B.", 2026-08-06) — no sign-off line |
| `epoch_file_pattern` | ⑦ | SIGNED | daq_family_decisions.md:325 [file navigation] |
| `frequency_filter` | ⑦ | SIGNED | frequency_filter_model_plan.md:5 (untagged) |
| `ingestion_manifest` | ⑦ | SIGNED, REVISED-UNSIGNED | epoch_plan.md:878 [epoch] ("epochfiles_ingested becomes ingestion_manifest"); revised unsigned by #73 items 39/40 (V_eta_spatial_transcriptomics_plan.md:161,:169) |
| `method_parameters` | ⑦ | SIGNED | method_parameters_plan.md:7 [spike processing parameters] |

**How to re-derive.**
- The sign-off census comes from running `status_board.scan_signoff_lines` over `schemas/*.md`, minus `GENERATED_MARKDOWN`.
- Class names were matched with `(?<![\w])<class>(?![\w])` against each sign-off's own line or paragraph, then every hit was read by hand. Incidental word matches (`base`, `data`, `time`, `entity` used as ordinary words) were discarded.
- Scripts: `scratchpad/sig2.py`, `match.py` and `gov.py`.
