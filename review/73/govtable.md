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