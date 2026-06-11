# V_epsilon schemas

The `V_epsilon/` directory is the working set-version directory for the
sandbox iteration that follows V_delta. Like V_delta, V_epsilon is a
sandbox: contents are expected to change in place during this phase, and
consumers should not pin to V_epsilon as a stable target. The set will be
copied to `schemas/V1/` and frozen when ready (see `V_epsilon_SPEC.md`
§ "Promotion to V1").

This notes file tracks V_epsilon's status, the per-class inventory, the
decisions taken where the source proposals were open, and the open
follow-ups that will land as separate PRs.

## What V_epsilon changes versus V_delta

V_delta's changes were organizational; V_epsilon changes the **schema
content**. It implements the `subject_interaction` redesign drafted in the
`ndi-next-steps` repository under `Summer 2026/1_Ingestion/`. The
substantive differences are listed in `V_epsilon_SPEC.md`. In summary:

1. A new abstract `subject_interaction` spine (`observation` /
   `manipulation` / `annotation`) unifying observations, interventions, and
   curatorial classifications under one document family.
2. A new `time_reference` family (five concrete reference classes) that
   moves timing out of inline fields into referenced documents.
3. New observation, manipulation, and annotation family classes (scalar,
   categorical, dataseries, expression; procedural, pharmacological,
   environmental, stimulus, placement, derivation; group assignment).
4. New body classes (dataseries / expression / reference / sequence-read)
   and supporting standalone classes (`instrument`, `interaction_purpose`,
   re-scoped `stimulus_approach`).
5. Deprecation of the `treatment` family, `virus_injection`, and
   `subject_group`; re-rooting of `stimulus_bath`; facet additions on
   `subject`; additive header fields on `element_epoch`.

The meta-schema is unchanged. Every new class validates against the
existing `did_schema_meta.json`.

## Initial state

- All V_delta schema files (107 stable document classes + 3 meta files)
  were copied verbatim into `V_epsilon/` as the starting point.
- 79 new document classes were authored into `V_epsilon/draft/`.
- 3 existing classes were modified (`subject`, `element_epoch` in
  `stable/`; `stimulus_bath` re-rooted into `draft/`); 1 re-scoped class
  (`stimulus_approach`) was authored fresh into `draft/`.
- 5 classes were moved to `V_epsilon/deprecated/` (`treatment`,
  `treatment_drug`, `treatment_transfer`, `virus_injection`,
  `subject_group`).
- `index.json` was regenerated from disk: **187 entries** (101 stable,
  81 draft, 5 deprecated). `set_version` and `schema_version_value` are
  `"V_epsilon"`; `legacy_schema_version_values` is `["did_v1", "V_delta"]`.
- Every new and modified schema validates against `did_schema_meta.json`,
  the `index.json` agrees with disk (tier, maturity, paths), every
  superclass reference resolves by `class_name`, and every
  `must_refer_to_document_class` resolves.

## Decisions taken where the source proposals were open

The proposals left several load-bearing choices explicitly undecided. To
ship an internally consistent set, V_epsilon resolves each with a default,
recorded here and revisitable while the set is a sandbox.

- **Path A (class-per-family), not Path B (microschema body).** Every
  family proposal (`Scalar_*`, `Procedural_*`, `Injection_*`, …) is written
  as a concrete subclass with its own fields. Path A reuses V_delta's
  inheritance and required-field machinery with **no meta-schema change**;
  Path B would require building a microschema lookup/validation mechanism
  first. The proposal's own analysis judged the cost differential small
  because family churn is low. The V_delta `microschemas/_DESIGN.md`
  mechanism is therefore **not** used by V_epsilon.
- **`observation`/`manipulation`/`annotation` are abstract**, with only
  concrete family leaves instantiable (`document_class.abstract: true`).
- **Standalone leaf removal.** Two decision docs conflict;
  `Standalone_Removal_Decision.md` is the later one and wins. V_epsilon has
  **no** `standalone_*`/`daq_*`/`opaque_*` observation classes.
  `timeseries_observation` and `imageseries_observation` are concrete
  sub-genera of the abstract `dataseries_observation`. "Opaque" is treated
  as a body state (bytes retained as `generic_file`), not a class.
- **`virus_injection` → `injection`** (`kind: "virus"`), per
  `Injection_Proposal.md`, overriding the earlier `Boundary_Mapping`
  "subclass under `biological_transfer`" sketch.
- **`time_reference` is a multiple dependency** (`time_reference_#`,
  `multiple: true`, ≥1 required) on `subject_interaction`.
- **`epoch_clock`** is a `char` carrying an advisory `required` binding to
  the NDI-matlab clocktype value set, rather than a hard JSON-Schema enum.
- **`instrument` is kept as a distinct class** (slim: `instrument_type` +
  `global_identifier`), rather than collapsed into fields on a daqless
  `element`. Flagged provisional below.
- **`element.subject_id` is left in place** (still optional). The
  proposals deprecate it for new writes, but that is a write-policy/tooling
  concern; the schema field is unchanged in V_epsilon and the deprecation
  is documented rather than enforced.
- **`derivation` is authored** with the field shape the
  `Subject_Interaction_Proposal.md` states (`source_subject_id_#`,
  `derivation_method`, `target_structure`), even though its dedicated
  field-level pass is still pending. Flagged provisional below.

## Provisional / not-yet-ratified content

Several source decisions are marked "provisional — agreed in discussion,
not yet ratified or landed." V_epsilon authors them so the set is complete
and coherent, but they are the most likely to change:

- The dataseries genus, the channel/axes header split, the
  `dataseries_channel_map` sidecar, and the `element_epoch` header
  additions (`Channel_Model_and_Daqless_Element_Decision.md`,
  `Dataseries_Body_Proposal.md`). The `element_epoch` change here is the
  conservative additive subset (optional `axes`/`channels`/`storage`); the
  fuller three-way header split (element / element_epoch / `dataSeriesType`
  registry) is **not** implemented.
- `instrument`'s survival as a class vs collapsing into `element` fields.
- `dataseries_pyramid` (name and dependency target are flagged TBD in
  `Multiresolution_Read_Proposal.md`).
- `derivation`'s field shape (pending its own focused pass).
- `stimulus_approach` v2 write-time invariants (cross-field consistency
  with the referenced presentation/manipulation) are documented in the
  proposal but enforced by tooling, not the schema.

## Not implemented in this pass (open follow-ups, separate PRs)

- **Binding registry as a meta-file.** `Binding_Registry_Proposal.md`
  describes a `measured_property → binding` registry meta-file (with its
  own small meta-schema) plus a `value_set` document class. V_epsilon
  carries `binding` blocks inline (advisory, in `constraints`) but does
  **not** add the registry meta-file, its meta-schema, or `value_set`.
- **`dataSeriesType` registry** (a `probetype2object`-style template, not a
  document class) and the per-element materialization policy — registry/
  tooling artifacts, not authored here.
- **Corpus index** — no new schema class (it is a collection of
  by-reference `dataseries_data` + companion documents); the work is an
  indexer/adapter, out of scope for the schema set.
- **`element` channel-identity list** and the full daqless-element rewrite
  — deferred with the provisional channel model above.
- **Conversion docs.** Per-class `conversions/from_did_v1/` and
  `from_v_delta/` migration markdowns for the new and deprecated classes
  are not written. The deprecation→replacement mapping in
  `V_epsilon_SPEC.md` §8 and the per-proposal migration notes are the
  current reference. A follow-up should populate `conversions/` and add a
  `from_v_delta/` path for the treatment-family split, the
  `virus_injection`/`treatment_drug` → `injection` merge, the
  `treatment_transfer` → `biological_transfer` move, and the
  `subject_group` → `group_assignment` migration.
- **CI checks.** An `index.json` ↔ disk consistency check, a
  superclass/`must_refer_to` resolution check, and a tier/`maturity_level`
  agreement check (all of which were run manually for this PR and pass)
  should be added to the test suite, parametrized to include V_epsilon.

## Carryover defect (pre-existing, not introduced here)

`V_epsilon/stable/hartley_calc.json` fails meta-schema validation: a `file`
record carries field-definition keys (`mustBeNonEmpty`, …) that the
meta-schema's `file_record` does not allow. This defect exists identically
in `V_delta/stable/hartley_calc.json` and was copied in verbatim. It is
left untouched here to avoid rewriting unrelated content; it should be
fixed in a dedicated cleanup (strip the file record down to `name` +
`documentation`).
