# #73 review — open items after the 2026-09-25 class-set audit

Working list, saved so it survives the session. **It records questions, not decisions**:
decided items are in `schemas/V_eta_spatial_transcriptomics_plan.md` (items 1–49), and
nothing here is signed. Source reports are beside this file (`audit_A_*`, `audit_B_*`,
`audit_C_*`, `audit_mechanical_output.txt`).

## Parked for their own discussion
1. **`control_designation`.** Which presented items are controls. Proposed: a `logical`
   (true/false per item) calculation. Open: is it a statement about the animal's presentation
   or a property of the sequence; what its subject is; `logical` vs a `term` (control / test /
   …). Needs `logical_calculation` restored. Its edges are untouched by T15 until decided.
2. **`fitcurve` → a standalone `model_fit` data type** (item 49): equation, named parameters,
   independent/dependent variables, constraints, goodness, sampled fit; the tuning
   `model_fit[]` entry would share it. `polynomial` stays separate.
3. **Duplicate declarations (audit item 5).**
   - `software.name`, `strain.name`, `method_parameters.name` vs `base.name`: one fact in two
     places? (a) block field is the name, `base.name` left alone; (b) drop the block fields,
     use `base.name` (emitter + NDI reader changes). Claude leans (b).
   - `subject_calculation` redeclares `software_id` only to make it required. Proposed: a
     declared, gated rule "a subclass may tighten an inherited edge to required"; any other
     redeclaration fails.

## Decisions still to walk through (audit group A)
4. **T12 leaves with no written warrant:** `voltage_`, `current_`, `force_`,
   `concentration_manipulation` (a code comment only; `concentration_manipulation` overlaps
   `dose_manipulation`); `gain_assertion` / `gain_observation`.
5. **`logical_observation`: keep or retire** (no user since `valid_interval` moved to
   `time_observation`; tied to item 1).
6. **Facts modelled twice:** inline `execution_environment` vs the `runtime_environment_id`
   edge; `subject_interaction.channels` vs `acquisition_channels`; `acquisition_system_id` on
   interactions vs `epoch.instrument_id` → `entity` (a union target is now expressible).
7. **`chemical` / `formulation` / `dose`** declare the substance+amount shape separately and
   already disagree; `chemical.value.amount` is typed `concentration` while an `amount`
   (moles) type exists.
8. **`area` in square meters beside `volume` in liters** (practical units).
9. **Standalone data-type documents** have nowhere for `datum_type`, `storage_mode` or
   `key_labels_id`; `image.keys.labels_from` cannot work on a standalone image; where a
   referenced value's `keys` live.
10. **`acquisition_metadata_file`:** bytes outside the two data bodies, `_file` in the name
    (T6/T11), and its doc (TSV) vs the ledger (`.nbf.tgz`) disagree.
11. **`method_parameters.other`** is an untyped bag.
12. **`clock_alignment_configuration` vs `method_parameters`** (open in the clock plan).
13. **`session_id`** edge and `base.session_id` hold different ids on one document.
14. **Binding value sets** are spelled three ways (bare names, CURIE strings, `{node,name}`).
15. **Container words** (`metadata`, `data`) in signed infra class names.
16. **`tuning_curve`:** `response_units` is free text; `independent_variables[]` has no
    source fields or labels; mean/stddev/stderr vs item 15's "another column is a key".
17. **`harmonic_component`** uses flat `control_real`/`control_imaginary` where tuning nests
    `control`.
18. **`receptive_field.value.storage_mode`** duplicates the statement's `storage_mode`.
19. **`clock_alignment`** inherits `polynomial.value` and `relation.value_id` (T6 question).
20. **`ngrid`: delete vs fold into `sampled_body`** — the record disagrees with itself.

## Signed but never built (audit group B) — build items with cross-repo work
21. Retire `subject_interaction.sample_time` (data_body sign-off 2026-08-14); nine call
    sites across both repos still write it; 28 composites' docs still cite it.
22. Give the inline `subject_interaction.method_parameters` the signed `parameter[]` shape.
23. Restructure `conditions` per data_body Amendment 2 (cardinality 1, descriptors up,
    `count` flattened).
24. Bind `keys.unit` (Amendment 1) — first needs a unit vocabulary chosen (binding
    worksheet row 1).
25. Bring `contrast_sensitivity` in line with the #73 tuning shape (`model_fit.goodness`,
    `interpolated_values.c50`, fits/significance placement).

## Worksheets to fill (beside this file)
- `veta_term_worksheet_73.csv` — 71 terms to find or mint (axis, direction, origin, assay,
  variable). Ontology registries were unreachable from the review container.
- `veta_binding_worksheet_73.csv` — 24 fields needing a value set and strength.

## Governance
- 182 → 180 persist classes. Of the 180-odd audited: ~46 signed in current form, 16 signed
  then revised without a new signature, 4 field-level only, 19 decided but unsigned, 97 with
  no decision record (mostly the inherited quantity family). See `govtable.md`.
- The #73 decisions (items 1–49) carry no `TEAM-SIGN-OFF` line. `team_signoff_lines_DRAFT.md`
  is an out-of-date draft, not a signature.
- `tools/status_board.py` counts a sign-off quoted inside a code block
  (`V_eta_method_parameters_plan.md:683`) and still counts the superseded 2026-09-22 spatial
  sign-off (`V_eta_go_forward_class_audit.md:796`).

## To verify
- Whether a v1 `hartley_calc` document carries a `hartley_calc` block with fields of its own
  (needs NDIcalc-vis-matlab's writer; not attached in the review container).

## Cross-repo follow-ups
The DID-matlab and NDI-matlab checklists live in PR #76's description. Not yet added there:
`neuron_extracellular.m` emits the item-48 calculations (`label_calculation` for
`cluster_index`/`quality_label`, `score_calculation`, `voltage_calculation`, each with
`input_id` → the sorting output).
