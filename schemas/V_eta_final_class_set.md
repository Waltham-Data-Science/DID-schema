# V_eta — The Final Class Set (191)

*The classes that will exist in the finished V_eta schema, once the phase-outs are
decomposed/retired. Companion to `V_eta_go_forward_class_audit.md` (dispositions) and
`V_eta_class_provenance.md` (origins). Counts: **191 keep · 49 phase-out · 18 undecided**
of 258 current go-forward classes.*

## ① Statement spine & genus (15)
base, app, subject, subject_statement, subject_assertion, numeric_assertion,
subject_interaction, subject_observation, subject_manipulation, subject_relation,
directed_relation, undirected_relation, time_reference, data_body, value_set

## ② Data-type leaf tier (72) — one class per quantity × statement kind
**observation + assertion** (23 dims): acceleration, amount, angle, angular_velocity,
area, capacitance, charge, concentration, conductance, count, current, duration,
energy, force, length, mass, ph, power, resistance, score, velocity, voltage, volume
**observation + assertion + manipulation** (4 dims): frequency, intensity, pressure, temperature
**non-dimensional leaves:** term_observation, image_observation, dataseries_observation,
timeseries_observation, imageseries_observation, expression_observation,
spatial_expression_observation, term_assertion, date_assertion, dose_manipulation,
formulation_manipulation, term_manipulation, stimulus_manipulation, placement

## ③ Quantity & substance composites (30)
the 27 dimension abstracts (angle, voltage, frequency, …) + dose, formulation, chemical

## ④ time_reference family (7)
utc_reference, epoch_bounded_reference, epoch_relative_reference, event_bounded_reference,
event_relative_reference, session_bounded_reference, session_relative_reference

## ⑤ data_body family (34)
sampled_body, opaque_body, dataseries_data, timeseries_data(+_binary/_csv/_edf),
imageseries_data, expression_matrix_data (+13 format variants), reference_data,
reference_annotation_data(+_gff3/_gtf), reference_sequence_data(+3 fasta),
sequence_read_data(+_bam/_cram/_fastq)

## ⑥ Acquisition / session infra — D-A (23)
daqsystem, daqreader(+_ndr/_epochdata_ingested/_mfdaq_epochdata_ingested/_image_epochdata_ingested),
daqmetadatareader(+_epochdata_ingested), filenavigator, epochid, epochfiles_ingested,
epochclocktimes, element_epoch, oneepoch, valid_interval, syncgraph, syncrule,
syncrule_mapping, session, session_extent, session_in_a_dataset, dataset_remote, dataset_session_info

## ⑦ Stimulus bodies-of-record (2)
stimulus_presentation, control_stimulus_ids

## ⑧ Infra / meta (8)
directory, metadata_editor, mock, ndi_reserved_keys, zarr, demo_ndi, demo_ndi_mock, interaction_purpose

---

## NOT in the final set

**Phase-out (49)** — decomposed/retired then deleted: element + openMINDS(×4); the
analysis zoo (calc/tuning ×20, spike-sorting ×13, stimulus_response ×4); probe/spatial
measurements ×5; `ontology_label`; `measurement` (redundant with the observation tier;
carries an ndi_ class-path + JSON blob → needs-NDI).

**Undecided (18)** — data/file representation (generic_file, image, image_collection,
image_zarr, ephys_zarr, ngrid, binaryseries_parameters, filter, pyraview,
dataseries_channel_map, dataseries_pyramid: → data_body vs kept index/DSP infra);
`instrument` (redundant with device-as-subject + term_assertion?); `neuron_extracellular`;
`ontology_table_row`, `ontology_image`; `stimulus_parameter`, `stimulus_parameter_table`,
`stimulus_approach`.
