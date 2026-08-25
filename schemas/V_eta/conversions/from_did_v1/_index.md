# did_v1 -> V_eta conversion index

Enumerates every `did_v1` document class a migrator must convert to **V_eta**
(Brainstorm J), with status. The **authoritative field-level mapping** is
`schemas/V_eta_migration_plan.md` (Part D per-class + Part C new machinery);
these per-class docs carry the detailed field moves and each hard/semi doc opens
with a strict-J retarget banner (the body below is retained V_zeta reference).
Cross-cutting renames: [`_universal_renames.md`](_universal_renames.md); file
handling: [`_files.md`](_files.md).

## Hard transforms (subject-side restructuring)

| did_v1 source | V_eta target(s) | Status | Doc |
|---|---|---|---|
| `treatment` | `dose_manipulation` / `temperature_manipulation` / `<quantity>_manipulation` / `term_manipulation` (+ anchor; + part-`subject` + `part_of` when attributed, else a `term_observation` location value) | drafted | [treatment.md](treatment.md) |
| `ontology_table_row` | per column -> a `subject_assertion` (timeless) or `subject_observation` (timed) leaf + anchor; anatomy -> Path S (1->N) | drafted | [ontology_table_row.md](ontology_table_row.md) |
| `subject_group` | bare `subject` (v3.0.0; no `is_group`) | drafted | [subject_group.md](subject_group.md) |
| `treatment_drug` | `dose_manipulation` (drug on the chemical term) + anchor | drafted | [treatment_drug.md](treatment_drug.md) |
| `virus_injection` | `dose_manipulation` / `formulation_manipulation` (virus on the chemical term) + anchor | drafted | [virus_injection.md](virus_injection.md) |
| `treatment_transfer` | `term_manipulation` + a provenance `directed_relation` (D4) | drafted | [treatment_transfer.md](treatment_transfer.md) |

## Semi-mechanical (D5 -> `term_observation`)

| did_v1 source | V_eta target | Status | Doc |
|---|---|---|---|
| `probe_location` | `term_observation` (probe-subject; spatial-relation `variable`) | drafted | [probe_location.md](probe_location.md) |
| `ontology_image` | `term_observation` (region term; image file -> body) | drafted | [ontology_image.md](ontology_image.md) |
| `ontology_label` | `term_observation` / `term_assertion` (label term) | drafted | [ontology_label.md](ontology_label.md) |

## Mechanical (design-neutral; carry over unchanged, token-retargeted)

`contrast_tuning`(+`_calc`), `contrast_sensitivity_calc`,
`orientation_direction_tuning`/`oridirtuning_calc`,
`spatial_frequency_tuning`(+`_calc`), `speed_tuning`(+`_calc`),
`temporal_frequency_tuning`(+`_calc`), `reverse_correlation`,
`hartley_reverse_correlation`, `hartley_calc` -- no subject-side surface.

## Notes

- **Not migrated:** `stimloopsplitter_calc` (deprecated per domain owner).
- **Relations minted (D6):** only `part_of` (Path S) + one provenance term
  (`sample_of`/`derived_from`, `treatment_transfer`); confirmed in discovery mode.
