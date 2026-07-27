# V_eta Go-Forward Classes — Provenance & Disposition

*Every go-forward (`stable`+`draft`) class, its **origin** (earliest schema version the class name first appears, rename-aware; `did_v1` = present in the NDI production document set), and its J-disposition. NOTE: origin = when the NAME appeared, not 'unchanged since' — many `did_v1`-origin classes (e.g. `subject`, `measurement`) were fully reshaped by J; the true unexamined holdovers are `did_v1`-origin classes NOT in a decided track.*

| class | tier | origin | disposition |
|---|---|---|---|
| `acceleration` | stable | **V_eta** | J dim abstract |
| `acceleration_assertion` | stable | **V_eta** | J leaf |
| `acceleration_observation` | stable | **V_eta** | J leaf |
| `amount` | stable | **V_eta** | review/infra |
| `amount_assertion` | stable | **V_eta** | J leaf |
| `amount_observation` | stable | **V_eta** | J leaf |
| `angle` | stable | **V_eta** | J dim abstract |
| `angle_assertion` | stable | **V_eta** | J leaf |
| `angle_observation` | stable | **V_eta** | J leaf |
| `angular_velocity` | stable | **V_eta** | J dim abstract |
| `angular_velocity_assertion` | stable | **V_eta** | J leaf |
| `angular_velocity_observation` | stable | **V_eta** | J leaf |
| `app` | stable | **did_v1** | J spine |
| `area` | stable | **V_eta** | J dim abstract |
| `area_assertion` | stable | **V_eta** | J leaf |
| `area_observation` | stable | **V_eta** | J leaf |
| `base` | stable | **did_v1** | J spine |
| `binaryseries_parameters` | stable | **did_v1** | review/infra |
| `binnedspikeratevm` | stable | **did_v1** | D-C analysis tier |
| `calculator` | stable | **V_delta** | D-C analysis tier |
| `capacitance` | stable | **V_eta** | J dim abstract |
| `capacitance_assertion` | stable | **V_eta** | J leaf |
| `capacitance_observation` | stable | **V_eta** | J leaf |
| `charge` | stable | **V_eta** | J dim abstract |
| `charge_assertion` | stable | **V_eta** | J leaf |
| `charge_observation` | stable | **V_eta** | J leaf |
| `chemical` | stable | **V_eta** | review/infra |
| `concentration` | stable | **V_epsilon** | J dim abstract |
| `concentration_assertion` | stable | **V_eta** | J leaf |
| `concentration_observation` | stable | **V_epsilon** | J leaf |
| `conductance` | stable | **V_eta** | J dim abstract |
| `conductance_assertion` | stable | **V_eta** | J leaf |
| `conductance_observation` | stable | **V_eta** | J leaf |
| `contrast_sensitivity_calc` | stable | **V_delta** | D-C analysis tier |
| `contrast_tuning` | stable | **V_delta** | D-C analysis tier |
| `contrast_tuning_calc` | stable | **V_delta** | D-C analysis tier |
| `control_stimulus_ids` | stable | **did_v1** | D-B stimulus |
| `count` | stable | **V_epsilon** | J dim abstract |
| `count_assertion` | stable | **V_eta** | J leaf |
| `count_observation` | stable | **V_zeta** | J leaf |
| `current` | stable | **V_epsilon** | J dim abstract |
| `current_assertion` | stable | **V_eta** | J leaf |
| `current_observation` | stable | **V_zeta** | J leaf |
| `daqmetadatareader` | stable | **did_v1** | D-A infra |
| `daqmetadatareader_epochdata_ingested` | stable | **did_v1** | D-A infra |
| `daqreader` | stable | **did_v1** | D-A infra |
| `daqreader_epochdata_ingested` | stable | **did_v1** | D-A infra |
| `daqreader_image_epochdata_ingested` | stable | **V_zeta** | D-A infra |
| `daqreader_mfdaq_epochdata_ingested` | stable | **did_v1** | D-A infra |
| `daqreader_ndr` | stable | **did_v1** | D-A infra |
| `daqsystem` | stable | **did_v1** | D-A infra |
| `data_body` | draft | **V_eta** | 2.D data_body |
| `dataseries_channel_map` | draft | **V_epsilon** | review/infra |
| `dataseries_data` | draft | **V_epsilon** | 2.D data_body |
| `dataseries_observation` | draft | **V_epsilon** | J leaf |
| `dataseries_pyramid` | draft | **V_epsilon** | review/infra |
| `dataset_remote` | stable | **did_v1** | D-A infra |
| `dataset_session_info` | stable | **did_v1** | D-A infra |
| `date_assertion` | stable | **V_eta** | J leaf |
| `demo_ndi` | stable | **V_gamma** | review/infra |
| `demo_ndi_mock` | stable | **V_gamma** | review/infra |
| `directed_relation` | stable | **V_eta** | J relation |
| `directory` | stable | **V_gamma** | review/infra |
| `distance_metadata` | stable | **did_v1** | review/infra |
| `dose` | stable | **V_eta** | review/infra |
| `dose_manipulation` | stable | **V_eta** | J leaf |
| `duration` | stable | **V_epsilon** | J dim abstract |
| `duration_assertion` | stable | **V_eta** | J leaf |
| `duration_observation` | stable | **V_zeta** | J leaf |
| `electrode_offset_voltage` | stable | **did_v1** | review/infra |
| `element` | stable | **did_v1** | RETIRE (Phase 8) |
| `element_epoch` | stable | **did_v1** | D-A infra |
| `energy` | stable | **V_eta** | J dim abstract |
| `energy_assertion` | stable | **V_eta** | J leaf |
| `energy_observation` | stable | **V_eta** | J leaf |
| `ephys_zarr` | stable | **V_gamma** | review/infra |
| `epoch_bounded_reference` | stable | **V_epsilon** | D-A infra |
| `epoch_relative_reference` | stable | **V_epsilon** | D-A infra |
| `epochclocktimes` | stable | **did_v1** | D-A infra |
| `epochfiles_ingested` | stable | **did_v1** | D-A infra |
| `epochid` | stable | **did_v1** | D-A infra |
| `event_bounded_reference` | stable | **V_epsilon** | J time_ref |
| `event_relative_reference` | stable | **V_epsilon** | J time_ref |
| `expression_matrix_data` | draft | **V_epsilon** | 2.D data_body |
| `expression_matrix_data_cellranger_h5` | draft | **V_epsilon** | 2.D data_body |
| `expression_matrix_data_counts_table` | draft | **V_epsilon** | 2.D data_body |
| `expression_matrix_data_dia_report` | draft | **V_epsilon** | 2.D data_body |
| `expression_matrix_data_gef` | draft | **V_epsilon** | 2.D data_body |
| `expression_matrix_data_gem` | draft | **V_epsilon** | 2.D data_body |
| `expression_matrix_data_h5ad` | draft | **V_epsilon** | 2.D data_body |
| `expression_matrix_data_imzml` | draft | **V_epsilon** | 2.D data_body |
| `expression_matrix_data_loom` | draft | **V_epsilon** | 2.D data_body |
| `expression_matrix_data_maxquant` | draft | **V_epsilon** | 2.D data_body |
| `expression_matrix_data_mtx` | draft | **V_epsilon** | 2.D data_body |
| `expression_matrix_data_mzml` | draft | **V_epsilon** | 2.D data_body |
| `expression_matrix_data_mztab` | draft | **V_epsilon** | 2.D data_body |
| `expression_matrix_data_visium` | draft | **V_epsilon** | 2.D data_body |
| `expression_observation` | draft | **V_epsilon** | 2.D data_body |
| `filenavigator` | stable | **did_v1** | D-A infra |
| `filter` | stable | **did_v1** | review/infra |
| `fitcurve` | stable | **did_v1** | D-C analysis tier |
| `force` | stable | **V_eta** | J dim abstract |
| `force_assertion` | stable | **V_eta** | J leaf |
| `force_observation` | stable | **V_eta** | J leaf |
| `formulation` | stable | **V_eta** | review/infra |
| `formulation_manipulation` | stable | **V_eta** | J leaf |
| `frequency` | stable | **V_epsilon** | J dim abstract |
| `frequency_assertion` | stable | **V_eta** | J leaf |
| `frequency_manipulation` | stable | **V_epsilon** | J leaf |
| `frequency_observation` | stable | **V_zeta** | J leaf |
| `generic_file` | stable | **did_v1** | review/infra |
| `hartley_calc` | stable | **V_delta** | D-C analysis tier |
| `hartley_reverse_correlation` | stable | **V_delta** | D-C analysis tier |
| `image` | stable | **did_v1** | review/infra |
| `image_collection` | stable | **V_gamma** | review/infra |
| `image_observation` | draft | **V_eta** | J leaf |
| `image_zarr` | stable | **V_gamma** | review/infra |
| `imageseries_data` | draft | **V_epsilon** | 2.D data_body |
| `imageseries_observation` | draft | **V_epsilon** | J leaf |
| `instrument` | draft | **V_epsilon** | review/infra |
| `intensity` | stable | **V_eta** | J dim abstract |
| `intensity_assertion` | stable | **V_eta** | J leaf |
| `intensity_manipulation` | stable | **V_eta** | J leaf |
| `intensity_observation` | stable | **V_eta** | J leaf |
| `interaction_purpose` | stable | **V_epsilon** | review/infra |
| `jrclust_clusters` | stable | **did_v1** | D-C analysis tier |
| `length` | stable | **V_epsilon** | J dim abstract |
| `length_assertion` | stable | **V_eta** | J leaf |
| `length_observation` | stable | **V_zeta** | J leaf |
| `mass` | stable | **V_epsilon** | J dim abstract |
| `mass_assertion` | stable | **V_eta** | J leaf |
| `mass_observation` | stable | **V_zeta** | J leaf |
| `measurement` | stable | **did_v1** | J spine |
| `metadata_editor` | stable | **did_v1** | review/infra |
| `mock` | stable | **did_v1** | review/infra |
| `ndi_reserved_keys` | stable | **V_gamma** | review/infra |
| `neuron_extracellular` | stable | **did_v1** | review/infra |
| `ngrid` | stable | **did_v1** | review/infra |
| `numeric_assertion` | stable | **V_eta** | J leaf |
| `oneepoch` | stable | **did_v1** | D-A infra |
| `ontology_image` | stable | **V_gamma** | review/infra |
| `ontology_label` | stable | **V_gamma** | review/infra |
| `ontology_table_row` | stable | **V_gamma** | review/infra |
| `opaque_body` | draft | **V_eta** | 2.D data_body |
| `openminds` | stable | **did_v1** | RETIRE (Phase 8) |
| `openminds_element` | stable | **did_v1** | RETIRE (Phase 8) |
| `openminds_import` | draft | **V_eta** | PERSIST ⑦ provenance (emitter gap: openMINDS import path must stamp it; draft until exercised) |
| `openminds_stimulus` | stable | **did_v1** | RETIRE (Phase 8) |
| `openminds_subject` | stable | **did_v1** | RETIRE (Phase 8) |
| `oridirtuning_calc` | stable | **V_delta** | D-C analysis tier |
| `orientation_direction_tuning` | stable | **did_v1** | D-C analysis tier |
| `ph` | stable | **V_eta** | J dim abstract |
| `ph_assertion` | stable | **V_eta** | J leaf |
| `ph_observation` | stable | **V_eta** | J leaf |
| `placement` | stable | **V_epsilon** | J leaf |
| `position_metadata` | stable | **did_v1** | review/infra |
| `power` | stable | **V_eta** | J dim abstract |
| `power_assertion` | stable | **V_eta** | J leaf |
| `power_observation` | stable | **V_eta** | J leaf |
| `pressure` | stable | **V_epsilon** | J dim abstract |
| `pressure_assertion` | stable | **V_eta** | J leaf |
| `pressure_manipulation` | stable | **V_epsilon** | J leaf |
| `pressure_observation` | stable | **V_zeta** | J leaf |
| `probe_geometry` | stable | **did_v1** | review/infra |
| `probe_location` | stable | **did_v1** | review/infra |
| `pyraview` | stable | **did_v1** | review/infra |
| `reference_annotation_data` | draft | **V_epsilon** | 2.D data_body |
| `reference_annotation_data_gff3` | draft | **V_epsilon** | 2.D data_body |
| `reference_annotation_data_gtf` | draft | **V_epsilon** | 2.D data_body |
| `reference_data` | draft | **V_epsilon** | 2.D data_body |
| `reference_sequence_data` | draft | **V_epsilon** | 2.D data_body |
| `reference_sequence_data_fasta_genome` | draft | **V_epsilon** | 2.D data_body |
| `reference_sequence_data_fasta_protein` | draft | **V_epsilon** | 2.D data_body |
| `reference_sequence_data_fasta_transcriptome` | draft | **V_epsilon** | 2.D data_body |
| `resistance` | stable | **V_eta** | J dim abstract |
| `resistance_assertion` | stable | **V_eta** | J leaf |
| `resistance_observation` | stable | **V_eta** | J leaf |
| `reverse_correlation` | stable | **V_delta** | D-C analysis tier |
| `sampled_body` | draft | **V_eta** | 2.D data_body |
| `score` | stable | **V_epsilon** | J dim abstract |
| `score_assertion` | stable | **V_eta** | J leaf |
| `score_observation` | stable | **V_zeta** | J leaf |
| `sequence_read_data` | draft | **V_epsilon** | 2.D data_body |
| `sequence_read_data_bam` | draft | **V_epsilon** | 2.D data_body |
| `sequence_read_data_cram` | draft | **V_epsilon** | 2.D data_body |
| `sequence_read_data_fastq` | draft | **V_epsilon** | 2.D data_body |
| `session` | stable | **did_v1** | D-A infra |
| `session_bounded_reference` | stable | **V_eta** | D-A infra |
| `session_extent` | stable | **V_epsilon** | D-A infra |
| `session_in_a_dataset` | stable | **did_v1** | D-A infra |
| `session_relative_reference` | stable | **V_epsilon** | D-A infra |
| `simple_calc` | stable | **did_v1** | D-C analysis tier |
| `site2channelmap` | stable | **did_v1** | D-C analysis tier |
| `sorting_parameters` | stable | **did_v1** | D-C analysis tier |
| `spatial_expression_observation` | draft | **V_epsilon** | 2.D data_body |
| `spatial_frequency_tuning` | stable | **V_delta** | D-C analysis tier |
| `spatial_frequency_tuning_calc` | stable | **V_delta** | D-C analysis tier |
| `speed_tuning` | stable | **V_delta** | D-C analysis tier |
| `speed_tuning_calc` | stable | **V_delta** | D-C analysis tier |
| `spike_clusters` | stable | **did_v1** | D-C analysis tier |
| `spike_extraction_parameters` | stable | **did_v1** | D-C analysis tier |
| `spike_extraction_parameters_modification` | stable | **did_v1** | D-C analysis tier |
| `spike_interface_sorting_outputs` | stable | **V_gamma** | D-C analysis tier |
| `spikewaves` | stable | **did_v1** | D-C analysis tier |
| `stimulus_approach` | — (no V_eta schema) | **V_epsilon** | RETIRE — not a V_eta class; "approach" = a `StimulationApproach` ontology term → `interaction_purpose`; conditions → `term_observation` of the subject |
| `stimulus_manipulation` | stable | **V_epsilon** | J leaf |
| `stimulus_parameter` | stable | **did_v1** | D-C analysis tier |
| `stimulus_parameter_table` | stable | **did_v1** | D-C analysis tier |
| `stimulus_presentation` | stable | **did_v1** | D-B stimulus |
| `stimulus_response` | stable | **did_v1** | D-C analysis tier |
| `stimulus_response_scalar` | stable | **did_v1** | D-C analysis tier |
| `stimulus_response_scalar_parameters` | stable | **did_v1** | D-C analysis tier |
| `stimulus_response_scalar_parameters_basic` | stable | **did_v1** | D-C analysis tier |
| `stimulus_tuningcurve` | stable | **did_v1** | D-C analysis tier |
| `subject` | stable | **did_v1** | J spine |
| `subject_assertion` | stable | **V_epsilon** | J leaf |
| `subject_interaction` | stable | **V_epsilon** | J spine |
| `subject_manipulation` | stable | **V_epsilon** | J leaf |
| `subject_observation` | stable | **V_epsilon** | J leaf |
| `subject_relation` | stable | **V_eta** | J relation |
| `subject_statement` | stable | **V_epsilon** | J spine |
| `syncgraph` | stable | **did_v1** | D-A infra |
| `syncrule` | stable | **did_v1** | D-A infra |
| `syncrule_mapping` | stable | **did_v1** | D-A infra |
| `temperature` | stable | **V_epsilon** | J dim abstract |
| `temperature_assertion` | stable | **V_eta** | J leaf |
| `temperature_manipulation` | stable | **V_epsilon** | J leaf |
| `temperature_observation` | stable | **V_zeta** | J leaf |
| `temporal_frequency_tuning` | stable | **V_delta** | D-C analysis tier |
| `temporal_frequency_tuning_calc` | stable | **V_delta** | D-C analysis tier |
| `term_assertion` | stable | **V_eta** | J leaf |
| `term_manipulation` | stable | **V_eta** | J leaf |
| `term_observation` | stable | **V_epsilon** | J leaf |
| `time_reference` | stable | **V_epsilon** | J time_ref |
| `timeseries_data` | draft | **V_epsilon** | 2.D data_body |
| `timeseries_data_binary` | draft | **V_epsilon** | 2.D data_body |
| `timeseries_data_csv` | draft | **V_epsilon** | 2.D data_body |
| `timeseries_data_edf` | draft | **V_epsilon** | 2.D data_body |
| `timeseries_observation` | draft | **V_epsilon** | J leaf |
| `tuning_fit` | stable | **V_delta** | D-C analysis tier |
| `tuningcurve_calc` | stable | **did_v1** | D-C analysis tier |
| `undirected_relation` | stable | **V_eta** | J relation |
| `utc_reference` | stable | **V_epsilon** | J time_ref |
| `valid_interval` | stable | **did_v1** | D-A infra |
| `value_set` | stable | **V_eta** | review/infra |
| `velocity` | stable | **V_eta** | J dim abstract |
| `velocity_assertion` | stable | **V_eta** | J leaf |
| `velocity_observation` | stable | **V_eta** | J leaf |
| `vmneuralresponseresiduals` | stable | **did_v1** | D-C analysis tier |
| `vmspikefilteringparameters` | stable | **did_v1** | D-C analysis tier |
| `vmspikefit` | stable | **did_v1** | D-C analysis tier |
| `vmspikesummary` | stable | **did_v1** | D-C analysis tier |
| `voltage` | stable | **V_epsilon** | J dim abstract |
| `voltage_assertion` | stable | **V_eta** | J leaf |
| `voltage_observation` | stable | **V_zeta** | J leaf |
| `volume` | stable | **V_epsilon** | J dim abstract |
| `volume_assertion` | stable | **V_eta** | J leaf |
| `volume_observation` | stable | **V_zeta** | J leaf |
| `zarr` | stable | **V_gamma** | J dim abstract |
