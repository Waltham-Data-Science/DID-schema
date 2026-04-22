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

## Treatment consolidation and the minischema mechanism

The V_beta treatment family has been consolidated around a single generic
`treatment` document type that delegates its `manipulation` field's shape to
a profile (minischema) named on each document instance.

### Retired schemas

| V_beta (retired)          | Replaced by                                                    |
|---------------------------|----------------------------------------------------------------|
| `treatment_drug.json`     | `treatment.json` + a `drug_treatment` profile (to be authored) |
| `virus_injection.json`    | `treatment.json` + `profiles/virus_injection.json` (canonical) |

`stimulus_bath.json` was **not** retired — it depends on `element_id`, not
`subject_id`, and is a stimulus-delivery approach rather than a subject
treatment. It remains in the flat `V_beta/` directory unchanged. If the
stimulus family develops its own proliferation problem, the profile
mechanism established here is a candidate pattern for it too.

### New mechanism summary

- **New types in `did_schema_meta.json`:** `ontology`, `quantity`,
  `relative_quantity`. See the updated type table in `V_beta_SPEC.md`.
- **New field attribute:** `_shape_from_minischema` (boolean, optional) on
  `structure` fields. When `true`, the schema file omits nested `_fields` and
  the field's shape is supplied at runtime by a profile referenced on each
  document instance.
- **New top-level document key:** `_minischema`, mapping each profile-delegated
  field name to either `{ "_ref": "<profile_name>" }` or an inline `_fields`
  fragment.
- **New meta-schema:** `profile_meta.json` validates profile files. Canonical
  profiles live under `schemas/V_beta/profiles/`.

### Migration guidance for existing treatment documents

Existing `virus_injection` documents (if any) migrate by:

1. Re-classing the document as `treatment` (classname change; `_class_version`
   bumps to `2.0.0`).
2. Moving field values into a `manipulation` object whose keys match the
   canonical `virus_injection` profile's `_fields` names: `virus_construct`,
   `serotype`, `volume`, `titer`, `onset`, and optionally `injection_rate`,
   `promoter`.
3. Expanding numeric fields (`volume`, `titer`) into the `quantity` shape
   with a canonical-unit label matching the profile (`nl`, `gc_per_ml`) plus
   `source_value` and `source_unit` retained from the original record.
4. Adding a top-level `_minischema` key:
   `{ "manipulation": { "_ref": "virus_injection" } }`.

`treatment_drug` documents migrate similarly once a `drug_treatment`
canonical profile is authored. That is not done in this change; it is a
follow-on task tracked in `Ideas.md` / `todo.md`.
