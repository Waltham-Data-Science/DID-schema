# Schemas with Undefined Sub-field Structure

These schemas contain fields typed as `char` that actually hold serialised JSON
(objects or arrays). The current schemas truncate at that level — the internal
structure of these fields is not yet defined. Examples are needed so the
sub-fields can be filled out.

---

## JSON Object Fields (key-value structures, internal keys unknown)

These are the highest-priority items: they hold arbitrary key-value data whose
keys and value types are not defined in the schema.

| # | Schema | Field | Current documentation |
|---|--------|-------|----------------------|
| 1 | `daq/syncgraph` | `graph_structure` | JSON representation of the synchronization graph connecting DAQ systems via sync rules. |
| 2 | `data/fitcurve` | `fit_parameters` | JSON object or array of the fitted parameter values. |
| 3 | `data/ontologyTableRow` | `row_data` | JSON object representing the key-value data for this ontology table row. |
| 4 | `metadata/openminds` | `openminds_data` | JSON object containing the openMINDS metadata fields. |
| 5 | `metadata/openminds_element` | `openminds_data` | JSON object containing the openMINDS metadata fields for this element. |
| 6 | `metadata/openminds_stimulus` | `openminds_data` | JSON object containing the openMINDS metadata fields for this stimulus. |
| 7 | `metadata/openminds_subject` | `openminds_data` | JSON object containing the openMINDS metadata fields for this subject. |
| 8 | `ingestion/syncrule_mapping` | `mapping_data` | JSON representation of the time mapping between clocks for this epoch. |
| 9 | `sorting/SpikeInterfaceSortingOutputs` | `sorter_parameters` | JSON object of the parameters used to run the sorter. |
| 10 | `apps/spikesorter/sorting_parameters` | `parameters` | JSON object of the parameters used for sorting. |
| 11 | `apps/calculators/tuningcurve_calc` | `result_data` | JSON object containing the tuning curve calculation results. |
| 12 | `apps/vhlab_voltage2firingrate/vmspikefit` | `fit_parameters` | JSON object of the fitted parameter values. |
| 13 | `apps/spikeextractor/spike_extraction_parameters_modification` | `modified_fields` | JSON object of field names and their modified values. |
| 14 | `probe/site2channelmap` | `site_to_channel` | JSON object mapping site numbers (keys) to DAQ channel numbers (values). |

---

## JSON Array Fields with Structured Elements (element structure unknown)

These hold arrays where each element has internal structure (e.g., coordinate
pairs, interval pairs) that is not yet defined.

| # | Schema | Field | Current documentation |
|---|--------|-------|----------------------|
| 15 | `probe/probe_geometry` | `channel_positions` | JSON array of [x, y] positions for each channel in position_units. |
| 16 | `apps/markgarbage/valid_interval` | `intervals` | JSON array of [start, end] time intervals (in seconds) that are considered valid (non-garbage). |
| 17 | `stimulus/stimulus_parameter_table` | `table_data` | JSON 2D array of parameter values (rows x columns). |
| 18 | `stimulus/stimulus_response_scalar_parameters` | `response_window` | JSON array [t_start, t_end] defining the time window for computing the scalar response (in seconds). |
| 19 | `stimulus/stimulus_response_scalar_parameters` | `baseline_window` | JSON array [t_start, t_end] defining the baseline time window (in seconds). |

---

## JSON Array Fields with Simple Values (scalar elements, shape unclear)

These hold flat arrays of scalars (numbers, strings, IDs). The element type is
described in prose but the schema does not enforce it.

| # | Schema | Field | Current documentation |
|---|--------|-------|----------------------|
| 20 | `subject_group` | `subject_ids` | A JSON array of subject document IDs belonging to this group. |
| 21 | `data/ngrid` | `dim_sizes` | The size of each dimension, serialised as a JSON array of integers. |
| 22 | `data/ngrid` | `dim_labels` | Labels for each dimension, serialised as a JSON array of strings. |
| 23 | `daq/daqmetadatareader` | `metadata_names` | JSON array of metadata field names this reader can extract. |
| 24 | `probe/electrode_offset_voltage` | `offset_voltages` | JSON array of offset voltage values for each electrode channel. |
| 25 | `stimulus/control_stimulus_ids` | `control_ids` | JSON array of control stimulus identifiers. |
| 26 | `stimulus/stimulus_parameter` | `parameter_values` | JSON array of the parameter values used across stimulus presentations. |
| 27 | `stimulus/stimulus_parameter_table` | `parameter_names` | JSON array of parameter names (column headers) in the table. |
| 28 | `stimulus/stimulus_presentation` | `presentation_order` | JSON array of stimulus indices in the order they were presented. |
| 29 | `stimulus/stimulus_response_scalar` | `stimulus_values` | JSON array of the independent stimulus parameter values. |
| 30 | `stimulus/stimulus_response_scalar` | `response_values` | JSON array of scalar response values (one per stimulus condition). |
| 31 | `stimulus/stimulus_tuningcurve` | `independent_values` | JSON array of the independent variable values. |
| 32 | `stimulus/stimulus_tuningcurve` | `response_mean` | JSON array of mean response values at each independent variable value. |
| 33 | `stimulus/stimulus_tuningcurve` | `response_stderr` | JSON array of standard error of mean for each response value. |

---

## Summary

- **14** fields hold JSON objects with completely undefined internal structure
- **5** fields hold JSON arrays where each element is itself structured
- **14** fields hold JSON arrays of simple scalars

**Total: 33 fields across 22 schemas** need examples to define their sub-field
structure.

### Next steps

Please provide example documents (or point to existing data) for any of the
above so I can expand the schemas with proper sub-field definitions.
