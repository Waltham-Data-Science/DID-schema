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
| D4 ✅ decided, build batched | `parameter[]` value has no unit (signed "no unit field"; data_body Amendment 1 reversed the same rule for keys) | A17, A18 |
| D5 ✅ decided, build batched | Relation predicates: `relation` fields unbound while the registry lists 26 predicates nobody points at (stale: `observes`, no gene-mapping terms, no undirected rows); binding keys the meta-schema does not declare | A21, A6, A30 |
| D6 ✅ decided, build batched | ~10 conditional rules live only in prose (keys required on a sampled body, `origin`/`spacing` iff regular, `chunk` only on sampled, enumerations in prose, opaque `format` optional, cache warrant, time value / `clock` optional): declare, batch-check, or accept | A8–A11, A24 |
| D7 ✅ decided, build batched | Provenance and governance: `vmspikefit` → `score_observation` although its input is in the dataset; two more observation emitters that look computed; the calculation leaves rest on the unsigned provenance rule, which contradicts a signed line the record says "stands"; `jrclust_clusters` signed → `count_observation`, unsigned → `label_calculation`; 26 persist classes with no decision record | C1, C2, C18, C19 |
| D8 ✅ decided, build batched | Spatial tombstones are not the v1 shape (chain includes `subject_observation`; snake_case required edges) — restate from the v1 templates, as `hartley_calc` was | C14 |
| D9 ✅ decided, build batched | Entity details: `local_identifier` carries another id's term; where a URL / award number lives; `acquisition_system.name` optional though it is the key; vendor/catalog two ways; notes only on manipulations | A1, A3, A4, A5, A20 |
| D10 ✅ decided, build batched | Value-cell conventions: three default-value conventions, booleans defaulting `0.0`, `count`/`score` slot named `value` (`value.value`), `count.value.unit` not a unit; carried: `intensity`/`ph`, `mmhg`, `date` | B2–B7, B9, A32 |
| D11 ✅ decided, build batched | Stimulus/RF placement: `receptive_field` planes matched to bodies by an order bodies do not have; where "timed" lives in `timed_sequence`; the control stated twice (`control_item` and `visual_grating.blank`); grating `position` vs the `position` type | B23, B25, B26, B27 |
| D12 ✅ decided, build batched | Redeclaring an inherited edge to tighten it (`subject_calculation.software_id`) has no rule | A19, C17 |
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
- **D4 — A** (jess, 2026-09-29): `parameter[]` gains a bound `unit` term beside `value`
  (entry becomes `{variable, unit, value{value, source_value}, source_unit, term, text}`,
  matching the key and condition entries); the canonical `value` is in `unit`; `unit` is
  unbound until the unit vocabulary is chosen (item 24). Applies at all three mounts.
  Amends the signed [spike processing parameters] "no `unit` field", as data_body
  Amendment 1 did for keys; the "modelled on the `axis` entry" wording is updated (A18).
- **D5** (jess, 2026-09-29), all four:
  (a) `directed_relation.relation` / `undirected_relation.relation` get a binding whose
  allowed values are generated at build time from the registry rows (one source),
  strength `preferred`.
  (b) the registry: drop `observes` (replaced by `instrument_id`); add item 24's
  "orthologous gene mapping" / "gene alias mapping"; allow `subject_statement` /
  `data_type` endpoints (items 22, 27); add undirected rows (`paired_with`, `same_as`).
  (c) the meta-schema declares `root` and `source`, and the binding object becomes
  `additionalProperties: false`.
  (d) `acquisition_channels.channels.type` bound now, required, to {ai, ao, di, do}
  (`daqsystemstring.m:53-56`); `strain.genetic_strain_type`, `strain.disease_model` and
  `dataset.license` (SPDX) added to the binding worksheet.
- **D6** (jess, 2026-09-29), all three:
  (1) declare now: `keys` required on `sampled_body` (via D12's tightening rule);
  `byte_order` enum {little, big}, `datum_order` enum {C, F}; `hash_algorithm` enum
  {MD5, SHA-1, SHA-256, SHA-512}; `format` required on `opaque_body`;
  `absolute_time_reference.value.start` required.
  (2) a declared per-class `rules` list in the meta-schema (name, fields, one-line
  statement) for in-document conditions: `origin`/`spacing` iff `regular`;
  `values` XOR `labels` XOR `labels_from`; `chunk` only on a sampled body's keys;
  `datum_type` when the value has bytes; `relative_time_reference.value.clock` when
  `start` is present. DID-matlab implements them as named checks, report-only first.
  (3) T6 amended for bodies: a redundant body's source is its owner's non-redundant body
  (no new edge); the reason goes in `data_body.description`.
- **D7** (jess, 2026-09-29), all three:
  (a) `vmspikefit` → `model_fit_calculation` (`input_id` → `fit_input_id`, subject from
  `element_id`); `fit_sse_perpoint` → the shared fit entry's `goodness.sse_per_point`.
  Recorded as a decided target; the migrator follows (PR #76 checklist).
  (b) JH lawn-plate measures (radius, circularity, fluorescence): observation vs
  calculation decided during the JH raw-data mapping. `pyraview` → `redundant`
  `sampled_body`s owned by the recording's observation (second-pass join), not a second
  `voltage_observation`.
  (c) prepare a team sign-off sheet: every unsigned #73 decision; the four amendments to
  signed lines (`_calculation` reserved for calculators vs T2's provenance rule;
  `runtime_environment` "stands" vs item 53; `jrclust_clusters` count_observation vs
  label_calculation; the 08-22 confirm sheet naming `session_relative_reference`); the 26
  persist classes with no decision record. Each line independently signable; Claude
  writes no signature.
- **D8** (jess, 2026-09-29): restate the eight spatial tombstones from the v1 templates and
  writers (v1 chain, camelCase edge names, v1 fields, nothing required v1 does not write),
  as `hartley_calc` was in d78f2fa; fix `ontology_image`'s optional `ontologyTableRow_id`
  spelling. The spatial migrators move to the #73 design (PR #76 checklist); no
  intermediate shape is kept.
- **D9** (jess, 2026-09-29), all five:
  (a) `subject.local_identifier` and `session.local_identifier` lose the ontology terms
  copied from `base.id` / `base.session_id` (set `null`); "local identifier" goes on the
  term worksheet for all three entities.
  (b) `entity.global_identifier.scheme` bound (preferred) to {ORCID, ROR, DOI, PMID, PMCID,
  RRID, UDI, URL, AwardNumber, SWHID, Wikidata}; `web_resource` documents its URL as
  `global_identifier[scheme=URL]`, `funding` its award as `[scheme=AwardNumber]`.
  (c) `acquisition_system.name` required.
  (d) `strain` gains optional `product_id` -> `product`; `stock_number` dropped (vendor ->
  `organization`, code -> `catalog_number`); the openMINDS strain migrator follows.
  (e) `notes` moves from `subject_manipulation` up to `subject_interaction`, optional.
- **D10** (jess, 2026-09-29), revised in discussion:
  (a) the build generates ONE default per cell type (canonical slot included) and reuses it
  wherever the type is nested; `boolean` defaults `false`, `integer` `0`, string arrays `[]`
  (B2, B3, A32).
  (b)+(c) `count.value` becomes `{count, approximate}`: slot `value` -> `count`, and
  `count.value.unit` is DROPPED -- what is counted is the statement's `variable` (and
  `subject_id`); no migrator writes the field (`jSorterOutput.m:87-91` names it in
  `variable`, leaves the count block empty). `score.value.value` -> `score.value.score`.
  (d) T14 gains the value-cell rule: "Every value cell is `{<canonical slot>, source_value,
  source_unit, approximate}`, all but the canonical slot optional. A cell drops
  `source_value`/`source_unit` only when no conversion to the canonical slot exists (a
  count). A cell whose value can be stated at a coarser granularity than it is stored adds
  a declared `precision` (a date)." `intensity` and `ph` keep the full pattern; their docs
  are rewritten (intensity comparable only within one `variable`; ph the log-scale number,
  `source_unit` kept for provenance; the garbled intensity class doc fixed). No
  `uncertainty` field: no source states one per value (the one stated tolerance is
  `time_reference.clock_tolerance`); add it by amendment when a source carries it.
  (e) `pressure.value.mmhg` -> `pascals`; migrators convert, `source_unit` keeps "mmHg".
  (f) `date.value` = `{instant, precision, source_value, approximate}`: `source` ->
  `source_value`, and `approximate` added (precision = granularity, approximate =
  certainty; independent).
- **D11** (jess, 2026-09-29), all four:
  (a) `receptive_field.value.planes[]` is dropped; each `sampled_body` states what it holds
  as one body condition `{variable: "represented quantity", term: response estimate |
  significance}` (item 58's body `conditions`), so no body order is needed.
  (b) the onsets become `timed_sequence`'s own time key: `presentation_order` is indexed by
  trial, its one key is `variable: time`, irregular, values = the onsets (inline or body);
  per-trial offsets, where the source has them, are a named per-trial field `offset` on the
  same clock. The manipulation only points at the sequence (item 60 holds). Amends the
  signed stimulus plan's `:186-193` onset placement; goes on the D7c amendment list.
  (c) both stay: `timed_sequence.value.control_item` is the only source for "control
  trial"; `visual_grating.value.blank` is re-documented as a stimulus property ("True when
  this stimulus presents nothing (NDI `isblank`); whether it serves as the control is
  `timed_sequence.control_item`"). The migrator keeps deriving `control_item` from
  `isblank` (item 67).
  (d) `visual_grating.value.position` -> `center` (keeps its `angle` cells).
- **D12 — B** (jess, 2026-09-29). Measured first: 217 class files walked, 5 redeclared
  inherited edges (1 tightening: `subject_calculation.software_id`; 2 loosening:
  `hartley_calc.element_id` / `.stimulus_presentation_id` vs `reverse_correlation`; 2
  same-strength: `image_stack.document_id`, `daqreader_image_epochdata_ingested.daqreader_id`).
  DID-matlab `cache.m:373-426` `requiredDependencies` takes the chain UNION, so tightening
  is enforced and loosening is silently void.
  Rule: a class-level `require_inherited: [...]` names inherited edges or fields
  (`software_id`, `data.keys`) that the class makes required. The meta-schema declares it;
  a build gate checks every name resolves to something inherited and is not already
  required. `subject_calculation` replaces its `software_id` redeclaration with the list;
  `sampled_body` lists `data.keys` (D6). DID-matlab adds the names to the required set,
  report-only first. Redeclaring an inherited edge is forbidden, except same-strength
  redeclarations on a class restated from a did_v1 template (v1 fidelity); loosening fails
  the build everywhere, so `hartley_calc` drops its two redeclarations (no behaviour change:
  they are enforced required today).

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
