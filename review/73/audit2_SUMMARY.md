# Audit 2 — merged list (2026-09-29)

Sources: `audit2_A_spine_entities_infra.md` (A, 34 findings), `audit2_B_composites.md`
(B, 30), `audit2_C_leaves_crosscutting.md` (C, 20). **84 findings** over all 129 persist
classes, de-duplicated below into **13 decisions** and **one batch of mechanical fixes**.
Findings, not decisions: nothing here is recorded or built until decided.

Verified by hand against the tree and code before listing (the rest are the reviewers'
evidence, cited in their reports):
- B10: `term`, `label`, `date`, `position`, `polynomial` all declare top-level `value`
  `mustBeScalar: true`; DID-matlab `cache.m:1965` raises `did2:validation:notScalar`.
- C14: `spatial_gene_expression_pyramid` ⊂ [base, gene_expression, subject_observation];
  `gene_list_mapping` requires `gene_list_id_a` / `_b` (v1 writes camelCase).
- C1: NDI `apps/vhlab_voltage2firingrate/vmspikefit.json:15` declares `fit_input_id`.

## Decisions (walk in this order)

| # | topic | findings |
|---|---|---|
| D1 ✅ item 71 | Lists in single-value types: `term`, `label`, `date`, `position`, `polynomial` are scalar-only, yet items 21/28 store a gene list and one label per cell in them; `term`'s binding needs a `variable` a standalone `term` does not have | B10, B11 |
| D2 ✅ decided, build batched | One fit shape: `contrast_sensitivity` coefficients are an unnamed matrix, tuning's are a structure with no fields, `model_fit` (item 68) is a named list — three shapes, two vocabularies | B19, B20, B21, C3 |
| D3 ✅ decided, build batched | Tuning/contrast state their dimensions twice (`data.keys` and `independent_variables[]`); statistic columns in parallel; only tuning names its response unit; F0/F1 encoded four ways | B14, B15, B17, B18 |
| D4 | `parameter[]` value has no unit (signed "no unit field"; data_body Amendment 1 reversed the same rule for keys) | A17, A18 |
| D5 | Relation predicates: `relation` fields unbound while the registry lists 26 predicates nobody points at (stale: `observes`, no gene-mapping terms, no undirected rows); binding keys the meta-schema does not declare | A21, A6, A30 |
| D6 | ~10 conditional rules live only in prose (keys required on a sampled body, `origin`/`spacing` iff regular, `chunk` only on sampled, enumerations in prose, opaque `format` optional, cache warrant, time value / `clock` optional): declare, batch-check, or accept | A8–A11, A24 |
| D7 | Provenance and governance: `vmspikefit` → `score_observation` although its input is in the dataset; two more observation emitters that look computed; the calculation leaves rest on the unsigned provenance rule, which contradicts a signed line the record says "stands"; `jrclust_clusters` signed → `count_observation`, unsigned → `label_calculation`; 26 persist classes with no decision record | C1, C2, C18, C19 |
| D8 | Spatial tombstones are not the v1 shape (chain includes `subject_observation`; snake_case required edges) — restate from the v1 templates, as `hartley_calc` was | C14 |
| D9 | Entity details: `local_identifier` carries another id's term; where a URL / award number lives; `acquisition_system.name` optional though it is the key; vendor/catalog two ways; notes only on manipulations | A1, A3, A4, A5, A20 |
| D10 | Value-cell conventions: three default-value conventions, booleans defaulting `0.0`, `count`/`score` slot named `value` (`value.value`), `count.value.unit` not a unit; carried: `intensity`/`ph`, `mmhg`, `date` | B2–B7, B9, A32 |
| D11 | Stimulus/RF placement: `receptive_field` planes matched to bodies by an order bodies do not have; where "timed" lives in `timed_sequence`; the control stated twice (`control_item` and `visual_grating.blank`); grating `position` vs the `position` type | B23, B25, B26, B27 |
| D12 | Redeclaring an inherited edge to tighten it (`subject_calculation.software_id`) has no rule | A19, C17 |
| D13 | Smaller questions: a bought formulation must list ingredients; `fill_value` as a double array; `demo` carries bytes outside the bodies; no way for `value_id`/`owner_id`/… to name "a standalone value"; `acquisition_epoch`'s drifted keys copy; 13 infra tombstones `in_progress`; `parameter` in `epoch_parameter_reader`; draft vs stable placement; `file_pattern` names two things; nested `mustBeNonEmpty`/`mustBeScalar` possibly declarative only (DID-matlab) | B13, A12, A34, A22, C13, C16, C12, C4, A29, B8 |

## Decision log (build batched at the end, per jess 2026-09-29)

- **D1** (built, item 71): the five single-value types are list-capable; `datum_type` gains
  `utf8`; a standalone `term`'s binding is checked through the referencing key.
- **D2 — A** (jess, 2026-09-29): ONE declared fit entry shared by `tuning_curve_calculation.model_fit[]`,
  `contrast_sensitivity.value.model_fit[]` and the `model_fit` type: `model`,
  `coefficients[]{variable, value}` (named; labels where no term), `goodness{r2, sse}`,
  `sampled_fit`. Families keep their extras (tuning `metrics{...}`, contrast's four
  per-spatial-frequency arrays). Contrast's coefficients are named from NDIcalc-vis
  `+vis/+contrast/+indexes/fitindexes.m`: RB `[rm c50]`, RBN `[rm c50 n]`, RBNS
  `[rm c50 n s]`. Amends the shape (not the name) of tuning's `coefficients` in the signed
  tuning plan; record it as an amendment there.
- **D3** (jess, 2026-09-29), all three recommendations:
  (a) `tuning_curve` and `contrast_sensitivity` drop `value.independent_variables[]` and
  state their stimulus dimensions as the value's `keys` (categorical levels as `labels`);
  `individual` / `raw_individual` add one trailing trial dimension, stated in their docs.
  Amends the #67 name and item 66.
  (b) `mean`, `stddev`, `stderr`, `individual`, `raw_individual`, `control.*` stay named
  fields; T14 gains the rule "another reading of the same quantity is a key; a different
  statistic of it is its own field" (refines item 15).
  (c) `response_unit` (term) added to `harmonic_component` and `contrast_sensitivity`;
  `response_type` on tuning and contrast becomes a bound term naming the reduction (mean,
  peak, F0, F1, F2); `contrast_sensitivity.modulated_response` is dropped;
  `harmonic_component.harmonic` stays an integer.

## Mechanical fixes (no decision needed; one batch)

Stale documentation left by renames and decisions already made: A2, A7, A13, A14/B29,
A15, A16, A23/B24/C11 (`relative_to`, `presented_id_k`, `derived_from`), A25, A26, A27,
A28, A31, A33/B30/C10/C20 (tenets: T15 appendix, T2, `datum_type` placement), B1, B12
(`logical` doc), B22, B28, C6, C7, C8, C9 (example instances of undefined classes), C15,
and the binding worksheet rows naming `subject_statement.keys.*` / `image.value.keys.*`.

## Clean (no findings)
Every one of the 40 leaves has a recorded need, and no needed leaf is missing; no `_#`
edge on a V_eta class; every repeated edge declares `ordered`; no `is_`/`has_` boolean;
all 31 enumerated binding members are `{node, name}`; no persist class inherits a retired
class; 0 of 35 leaf-documentation tokens stale.
