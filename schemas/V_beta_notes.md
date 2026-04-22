# V_beta schemas

The `V_beta/` directory holds a snake_case-normalised copy of the V_alpha
schemas. Every file is a direct derivative of its V_alpha counterpart with
the following transformations:

- **Classnames** (top-level `_classname` values and any `_classname` inside
  `_superclasses` entries) are snake_case.
- **Field names** (every `_name` inside `_fields`, at any nesting depth) are
  snake_case.
- **Filenames** match their classnames (e.g. the schema for classname
  `spike_interface_sorting_outputs` lives in
  `spike_interface_sorting_outputs.json`).
- `_constraints` values that reference a field by name (e.g.
  `dynamic_keys_from`) were updated to the new snake_case field names so the
  schemas stay internally consistent.
- Prose in `_documentation` strings that named a renamed field or class was
  also updated for consistency. No other prose was changed.

Structural keys (`_classname`, `_class_version`, `_mustBeNonEmpty`, ...), JSON
Schema keywords, and `_depends_on` / `_file` / `_directory` `_name` values
were already snake_case in V_alpha and are unchanged.

## Renames applied (V_alpha → V_beta)

Classnames / filenames:

| V_alpha                         | V_beta                              |
|---------------------------------|-------------------------------------|
| `SpikeInterfaceSortingOutputs`  | `spike_interface_sorting_outputs`   |
| `demoNDI`                       | `demo_ndi`                          |
| `demoNDIMock`                   | `demo_ndi_mock`                     |
| `imageCollection`               | `image_collection`                  |
| `imageStack`                    | `image_stack`                       |
| `imageStack_parameters`         | `image_stack_parameters`            |
| `ontologyImage`                 | `ontology_image`                    |
| `ontologyLabel`                 | `ontology_label`                    |
| `ontologyTableRow`              | `ontology_table_row`                |

Field names:

| V_alpha                    | V_beta                       |
|----------------------------|------------------------------|
| `dataType`                 | `data_type`                  |
| `decimationLevels`         | `decimation_levels`          |
| `decimationSamplingRates`  | `decimation_sampling_rates`  |
| `decimationStartTimes`     | `decimation_start_times`     |
| `nativeRate`               | `native_rate`                |
| `nativeStartTime`          | `native_start_time`          |
| `ontologyName`             | `ontology_name`              |
| `ontologyNodes`            | `ontology_nodes`             |
| `variableNames`            | `variable_names`             |

## Status

V_beta schemas, like V_alpha, use the flat-directory layout (one JSON per
document type at the top of `V_beta/`) described in `V_beta_SPEC.md`. They
are **not** loaded by the meta-schema test suite.

V_beta is the current target format. Once migration from V_alpha to V_beta
is complete, the `V_alpha/` directory will be removed.

Do not add new document types to `V_beta/` without following the naming
requirements in `V_beta_SPEC.md`.
