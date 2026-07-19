# V_eta — The Final Class Set (161 persist)

*The classes that survive to V1. Generated from the built schema (`tools/build_v_eta.py`
→ `schemas/V_eta/`), NOT hand-typed — regenerate rather than edit by memory. Category order:
spine → entities → **composites (data_type) before leaves** → time_reference → data_body (exactly 2)
→ infra. Companion: `V_eta_6_7_walkthrough_STATE.md` (the ⑥/⑦ audit + chunk status).*

| Category | n |
|---|--:|
| ① Statement spine & genus | 14 |
| ② Entities | 8 |
| ③ Quantity & substance composites (data_type) | 30 |
| ④ Data-type leaf tier | 73 |
| ⑤ time_reference family | 8 |
| ⑥ data_body family | 2 |
| ⑦ Acquisition & infra (keep) | 26 |
| **Persist total** | **161** |

## ① Statement spine & genus (14)
`app`, `base`, `data`, `data_body`, `data_type`, `directed_relation`, `entity`, `relation`, `subject_assertion`, `subject_interaction`, `subject_manipulation`, `subject_observation`, `subject_statement`, `undirected_relation`

## ② Entities (8) — the referenceable-identity genus (each carries `global_identifier`)
`subject`, `person`, `organization`, `publication`, `award`, `dataset`, `web_resource`, `session`

## ③ Quantity & substance composites (30) — the building blocks the leaves carry

**Dimensional (27):** `acceleration`, `amount`, `angle`, `angular_velocity`, `area`, `capacitance`, `charge`, `concentration`, `conductance`, `count`, `current`, `duration`, `energy`, `force`, `frequency`, `intensity`, `length`, `mass`, `ph`, `power`, `pressure`, `resistance`, `score`, `temperature`, `velocity`, `voltage`, `volume`

**Substance (3, currently ⊂ base — candidate to reparent under `data_type`):** `chemical`, `dose`, `formulation`

## ④ Data-type leaf tier (73) — one class per quantity × statement kind
`acceleration_assertion`, `acceleration_observation`, `amount_assertion`, `amount_observation`, `angle_assertion`, `angle_observation`, `angular_velocity_assertion`, `angular_velocity_observation`, `area_assertion`, `area_observation`, `capacitance_assertion`, `capacitance_observation`, `charge_assertion`, `charge_observation`, `concentration_assertion`, `concentration_manipulation`, `concentration_observation`, `conductance_assertion`, `conductance_observation`, `count_assertion`, `count_observation`, `current_assertion`, `current_manipulation`, `current_observation`, `dataseries_observation`, `date_assertion`, `dose_manipulation`, `duration_assertion`, `duration_observation`, `energy_assertion`, `energy_observation`, `force_assertion`, `force_manipulation`, `force_observation`, `formulation_manipulation`, `frequency_assertion`, `frequency_manipulation`, `frequency_observation`, `image_observation`, `imageseries_observation`, `intensity_assertion`, `intensity_manipulation`, `intensity_observation`, `length_assertion`, `length_observation`, `mass_assertion`, `mass_observation`, `numeric_assertion`, `ph_assertion`, `ph_observation`, `power_assertion`, `power_observation`, `pressure_assertion`, `pressure_manipulation`, `pressure_observation`, `resistance_assertion`, `resistance_observation`, `score_assertion`, `score_observation`, `temperature_assertion`, `temperature_manipulation`, `temperature_observation`, `term_assertion`, `term_manipulation`, `term_observation`, `timeseries_observation`, `velocity_assertion`, `velocity_observation`, `voltage_assertion`, `voltage_manipulation`, `voltage_observation`, `volume_assertion`, `volume_observation`

## ⑤ time_reference family (8)
`time_reference`, `event_relative_reference`, `epoch_relative_reference`, `session_bounded_reference`, `utc_reference`, `session_relative_reference`, `epoch_bounded_reference`, `event_bounded_reference`

## ⑥ data_body family (2) — EXACTLY two; all format/series carriers phase out (2.D fold)
`sampled_body`, `opaque_body`

## ⑦ Acquisition & infrastructure — KEEP (26)

DAQ/sync/epoch/navigator, storage descriptor, index/geometry, stimulus bodies-of-record, test fixtures:

`daqsystem`, `daqreader`, `daqreader_epochdata_ingested`, `daqreader_image_epochdata_ingested`, `daqmetadatareader`, `daqmetadatareader_epochdata_ingested`, `epochfiles_ingested`, `epochid`, `acquisition_epoch`, `filenavigator`, `syncgraph`, `syncrule`, `syncrule_mapping`, `directory`, `ngrid`, `dataseries_channel_map`, `binaryseries_parameters`, `filter`, `stimulus_presentation`, `control_stimulus_ids`, `demo_ndi`, `demo_ndi_mock`, `interaction_purpose`, `instrument`

*De-encoded (no longer classes): `daqreader_ndr` → fields on `daqreader`; `daqreader_mfdaq_epochdata_ingested` → `parameters` field on `daqreader_epochdata_ingested` (chunk c). Chunk b (Option A): the `*_epochdata_ingested` caches stay device-layer ⑦ infra — NOT folded to `sampled_body` (no subject at the device layer; the subject enters downstream on the observation). Redundant `epochid` superclass mixin dropped (dep-only). The imaging observation tier (movie→slice-subject `sampled_body` + ROI→neuron part-subjects) → #9 (D-C).*
*Pending transforms within ⑦ (see walkthrough STATE doc): `element_epoch` rename (e); governance sweep. `instrument`/`interaction_purpose` subject-domain — keep-or-fold call open.*

---

## NOT in the final set

**Sources to delete (Phase-8, 9)** — dissolved by migrators, deleted once corpora prove them:

- ✅ **DELETED (Phase 1):** `dataset_remote`, `dataset_session_info`, `session_in_a_dataset`, `metadata_editor` (have J dissolvers; no surviving referencer).
- ⏳ **HELD:** `openminds`, `openminds_stimulus`, `openminds_element` — still lack migrators (only `openminds_subject` is dissolved); the openMINDS decomposition must be completed before they can go. `element` — retired but still a superclass of live things (check usage). `measurement` — entangled with #9 (referenced by the analysis tier); phases out there.

**Analysis tier to decompose (D-C, 39)** — → `*_observation`s + `data_body` + `derived_from`:

`binnedspikeratevm`, `contrast_sensitivity_calc`, `contrast_tuning`, `contrast_tuning_calc`, `fitcurve`, `hartley_calc`, `hartley_reverse_correlation`, `jrclust_clusters`, `neuron_extracellular`, `oridirtuning_calc`, `orientation_direction_tuning`, `reverse_correlation`, `simple_calc`, `site2channelmap`, `sorting_parameters`, `spatial_frequency_tuning`, `spatial_frequency_tuning_calc`, `speed_tuning`, `speed_tuning_calc`, `spike_clusters`, `spike_extraction_parameters`, `spike_extraction_parameters_modification`, `spike_interface_sorting_outputs`, `spikewaves`, `stimulus_parameter`, `stimulus_parameter_table`, `stimulus_response`, `stimulus_response_scalar`, `stimulus_response_scalar_parameters`, `stimulus_response_scalar_parameters_basic`, `stimulus_tuningcurve`, `temporal_frequency_tuning`, `temporal_frequency_tuning_calc`, `tuning_fit`, `tuningcurve_calc`, `vmneuralresponseresiduals`, `vmspikefilteringparameters`, `vmspikefit`, `vmspikesummary`

**Phase out → `data_body` (2.D fold, 14):**

`dataseries_data`, `dataseries_pyramid`, `ephys_zarr`, `generic_file`, `image`, `image_collection`, `image_zarr`, `imageseries_data`, `pyraview`, `timeseries_data`, `timeseries_data_binary`, `timeseries_data_csv`, `timeseries_data_edf`, `zarr`

**Phase out → observations, needs-NDI / D10-11 (8):**

`probe_location`, `probe_geometry`, `electrode_offset_voltage`, `position_metadata`, `distance_metadata`, `ontology_label`, `ontology_table_row`, `ontology_image`

**Pre-J holdovers → phase out (2):**

`calculator`, `measurement`

