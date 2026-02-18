# Schemas with Undefined Sub-field Structure

These schemas contain fields typed as `char` that actually hold serialised JSON
(objects or arrays). The current schemas truncate at that level — the internal
structure of these fields is not yet defined. Examples are needed so the
sub-fields can be filled out.

---

## JSON Object Fields (key-value structures, internal keys unknown)

These are the highest-priority items: they hold arbitrary key-value data whose
keys and value types are not defined in the schema.

| # | Schema | Field | Status |
|---|--------|-------|--------|
| ~~1~~ | ~~`daq/syncgraph`~~ | ~~`graph_structure`~~ | **DONE** — Changed to `structure` type with `fields: []`; dynamic keys document graph nodes/edges. |
| ~~2~~ | ~~`data/fitcurve`~~ | ~~`fit_parameters`~~ | **DONE** — Changed to `structure` type with `fields: []`; `dynamic_keys_from: "fit_function"`. |
| ~~3~~ | ~~`data/ontologyTableRow`~~ | ~~`row_data`~~ | **DONE** — Replaced with 4 proper fields: `names`, `variableNames`, `ontologyNodes` (all comma-separated char), and `data` (structure type with dynamic keys from `variableNames`; requires special evaluator). |
| ~~4~~ | ~~`metadata/openminds`~~ | ~~`openminds_data`~~ | **DONE** — Changed to `structure` type with `fields: []`; `conforms_to: "openminds_type"`. |
| ~~5~~ | ~~`metadata/openminds_element`~~ | ~~`openminds_data`~~ | **DONE** — Changed to `structure` type with `fields: []`; `conforms_to: "openminds_type"`. |
| ~~6~~ | ~~`metadata/openminds_stimulus`~~ | ~~`openminds_data`~~ | **DONE** — Changed to `structure` type with `fields: []`; `conforms_to: "openminds_type"`. |
| ~~7~~ | ~~`metadata/openminds_subject`~~ | ~~`openminds_data`~~ | **DONE** — Changed to `structure` type with `fields: []`; `conforms_to: "openminds_type"`. |
| ~~8~~ | ~~`ingestion/syncrule_mapping`~~ | ~~`mapping_data`~~ | **DONE** — Changed to `structure` type with `fields: []`; dynamic keys are implementation-defined by the sync rule. |
| ~~9~~ | ~~`sorting/SpikeInterfaceSortingOutputs`~~ | ~~`sorter_parameters`~~ | **DONE** — Changed to `structure` type with `fields: []`; `dynamic_keys_from: "sorter_name"`. |
| ~~10~~ | ~~`apps/spikesorter/sorting_parameters`~~ | ~~`parameters`~~ | **DONE** — Changed to `structure` type with `fields: []`; `dynamic_keys_from: "sorter_name"`. |
| ~~11~~ | ~~`apps/calculators/tuningcurve_calc`~~ | ~~`result_data`~~ | **DONE** — Changed to `structure` type with `fields: []`; `dynamic_keys_from: "calculator_name"`. |
| ~~12~~ | ~~`apps/vhlab_voltage2firingrate/vmspikefit`~~ | ~~`fit_parameters`~~ | **DONE** — Changed to `structure` type with `fields: []`; `dynamic_keys_from: "fit_function"`. |
| ~~13~~ | ~~`apps/spikeextractor/spike_extraction_parameters_modification`~~ | ~~`modified_fields`~~ | **DONE** — Changed to `structure` type with `fields: []`; `dynamic_keys: true` (one key per modified field). |
| ~~14~~ | ~~`probe/site2channelmap`~~ | ~~`site_to_channel`~~ | **DONE** — Changed to `structure` type with `fields: []`; `dynamic_keys: true`, `value_type: "integer"`. |

---

## JSON Array Fields with Structured Elements (element structure unknown)

These hold arrays where each element has internal structure (e.g., coordinate
pairs, interval pairs) that is not yet defined.

| # | Schema | Field | Status |
|---|--------|-------|--------|
| ~~15~~ | ~~`probe/probe_geometry`~~ | ~~`channel_positions`~~ | **DONE** — Changed to `matrix` type; Nx2 matrix of [x, y] positions, `element_type: "double"`. |
| ~~16~~ | ~~`apps/markgarbage/valid_interval`~~ | ~~`intervals`~~ | **DONE** — Changed to `matrix` type; Nx2 matrix of [t_start, t_end] pairs, `element_type: "double"`. |
| ~~17~~ | ~~`stimulus/stimulus_parameter_table`~~ | ~~`table_data`~~ | **DONE** — Changed to `matrix` type; 2D matrix (num_stimuli × num_parameters), `element_type: "double"`. |
| ~~18~~ | ~~`stimulus/stimulus_response_scalar_parameters`~~ | ~~`response_window`~~ | **N/A** — `stimulus_response_scalar_parameters` is an abstract placeholder class with no fields; concrete subclasses (e.g., `stimulus_response_scalar_parameters_basic`) define their own fields. The erroneous fields were removed from the base class schema. |
| ~~19~~ | ~~`stimulus/stimulus_response_scalar_parameters`~~ | ~~`baseline_window`~~ | **N/A** — See item 18. |

---

## JSON Array Fields with Simple Values (scalar elements, shape unclear)

These hold flat arrays of scalars (numbers, strings, IDs). The element type is
described in prose but the schema does not enforce it.

| # | Schema | Field | Status |
|---|--------|-------|--------|
| ~~20~~ | ~~`subject_group`~~ | ~~`subject_ids`~~ | **DONE** — Stays `char`; documentation updated to comma-separated list. |
| ~~21~~ | ~~`data/ngrid`~~ | ~~`dim_sizes`~~ | **DONE** — Changed to `matrix` type; `element_type: "integer"`, `min_value: 1`. |
| ~~22~~ | ~~`data/ngrid`~~ | ~~`dim_labels`~~ | **DONE** — Stays `char`; documentation updated to comma-separated list. |
| ~~23~~ | ~~`daq/daqmetadatareader`~~ | ~~`metadata_names`~~ | **DONE** — Stays `char`; documentation updated to comma-separated list. |
| ~~24~~ | ~~`probe/electrode_offset_voltage`~~ | ~~`offset_voltages`~~ | **DONE** — Changed to `matrix` type; `element_type: "double"`. |
| ~~25~~ | ~~`stimulus/control_stimulus_ids`~~ | ~~`control_ids`~~ | **DONE** — Stays `char`; documentation updated to comma-separated list. |
| ~~26~~ | ~~`stimulus/stimulus_parameter`~~ | ~~`parameter_values`~~ | **DONE** — Changed to `matrix` type; `element_type: "double"`. |
| ~~27~~ | ~~`stimulus/stimulus_parameter_table`~~ | ~~`parameter_names`~~ | **DONE** — Stays `char`; documentation updated to comma-separated list. |
| ~~28~~ | ~~`stimulus/stimulus_presentation`~~ | ~~`presentation_order`~~ | **DONE** — Changed to `matrix` type; `element_type: "integer"`. |
| ~~29~~ | ~~`stimulus/stimulus_response_scalar`~~ | ~~`stimulus_values`~~ | **DONE** — Changed to `matrix` type; `element_type: "double"`. |
| ~~30~~ | ~~`stimulus/stimulus_response_scalar`~~ | ~~`response_values`~~ | **DONE** — Changed to `matrix` type; `element_type: "double"`. |
| ~~31~~ | ~~`stimulus/stimulus_tuningcurve`~~ | ~~`independent_values`~~ | **DONE** — Changed to `matrix` type; `element_type: "double"`. |
| ~~32~~ | ~~`stimulus/stimulus_tuningcurve`~~ | ~~`response_mean`~~ | **DONE** — Changed to `matrix` type; `element_type: "double"`. |
| ~~33~~ | ~~`stimulus/stimulus_tuningcurve`~~ | ~~`response_stderr`~~ | **DONE** — Changed to `matrix` type; `element_type: "double"`. |

---

## Summary

All 33 fields across 22 schemas have been updated:

- **13** former `char` JSON object fields → `structure` type with `fields: []` and constraint hints
- **1** former `char` JSON object field → `structure` type (ontologyTableRow, done previously)
- **9** former `char` numeric array fields → `matrix` type with `element_type` constraint
- **3** former `char` 2D/window numeric array fields → `matrix` type with `shape`/`length` constraint (items 15–17; items 18–19 were N/A — the schema is a placeholder)
- **5** former `char` string array fields → remain `char`, documentation updated to comma-separated

### Convention summary

| Former encoding | New type | When |
|---|---|---|
| `"char"` holding JSON object | `structure` with `fields: []` | Key-value structure with dynamic/unknown keys |
| `"char"` holding numeric JSON array | `matrix` with `element_type` | 1D or 2D array of numbers |
| `"char"` holding string JSON array | `char` (comma-separated) | Array of strings or identifiers |
