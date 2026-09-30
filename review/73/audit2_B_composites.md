# Audit 2 B: the 45 data_type composites (2026-09-29, HEAD 51250ef)

## Denominator

I read 45 of 45 composite schemas in full, every field and sub-field at every depth, every
edge and every documentation string (`schemas/V_eta/{stable,draft}/<class>.json`; none of the 45
is under `deprecated/`). I also read the parents `data` and `data_type` and the leaf
`tuning_curve_calculation` in full. For cross-checks I read the field lists and edges of
`data_body`, `sampled_body`, `subject_statement`, `subject_interaction`, `subject_calculation`,
`timed_sequence_manipulation`, the four `*_calculation` leaves of structured composites,
`reverse_correlation`, `hartley_reverse_correlation`, `hartley_calc`, `clock_alignment`,
`relation`, `fitcurve` (v1 tombstone) and `ngrid`.

Yardstick, read in full: `V_eta_tenets.md` (504 lines), `V_eta_spatial_transcriptomics_plan.md`
(items 1–70, 534 lines), `review/73/OPEN_ITEMS.md` (253 lines), and the previous audit
`review/73/audit_B_composites.md` (27 findings). Partial reads: `V_eta_tuning_model_plan.md`
:205-216, `V_eta_stimulus_model_plan.md` :175-215, `tools/build_v_eta.py` :9850-9895 and greps.
Validator behaviour was read from the local DID-matlab checkout (`claude/v-eta-migration-plan-35jj1z`
at `47cf8ba`, not fetched): `+did2/+schema/cache.m` :845-875 and :1915-2049.

Mechanical pass: 219 json files under `schemas/V_eta/`, 213 with a `document_class`, giving
213 class names, 564 distinct field names (any depth) and 72 distinct edge names. In scope:
423 documentation strings, 190 extracted tokens, 44 not resolved (judged below).

This report is read-only. It decides nothing; every suggestion is for the team.

## Summary

| category | count |
|---|---|
| VIOLATION | 1 |
| INCONSISTENCY | 10 |
| STALE-DOC | 7 |
| QUESTION | 12 |
| **total** | **30** |

The five most important:
1. **#10 INCONSISTENCY:** `term`, `label`, `date`, `position` and `polynomial` declare `value` `mustBeScalar: true` (which the validator enforces), so the keyed arrays that items 21 and 28 build on them (a gene list, one label per cell) cannot be stored inline. `datum_type` has no string type, so labels and terms cannot go in a sampled body either.
2. **#14 INCONSISTENCY:** `tuning_curve` and `contrast_sensitivity` declare their dimensions twice: the inherited `data.keys` and `value.independent_variables[]`, in two different entry shapes. The per-trial axis of `individual` is declared in neither.
3. **#19 VIOLATION (T14/T13):** `contrast_sensitivity.value.model_fit.coefficients` is an unnamed matrix: "Element naming is a follow-up".
4. **#11 QUESTION:** `term.value` has a REQUIRED binding `keyed_by: variable`, but a standalone `term` document (the item-21 gene list) has no `variable`.
5. **#23 INCONSISTENCY:** `receptive_field.value.planes[k]` names "emitted body k in emission order", but bodies are not ordered or listed (T6), so a plane cannot be matched to its body.

## Quantity-cell comparison table

`src` = `source_value` + `source_unit`; `apx` = `approximate`; `scal` = whether top-level `value` is `mustBeScalar`. Doc template A = "A typed X value (shape-library mixin). Identity classes that read or impose…"; template B = "A <unit> value cell (canonical + lossless source)…".

| composite(s) | canonical slot(s) | src | apx | scal | doc | odd one out |
|---|---|:-:|:-:|:-:|:-:|---|
| acceleration, angular_velocity, area, capacitance, charge, conductance, energy, force, power, resistance, substance_amount, velocity | `meters_per_second_squared`, `degrees_per_second`, `square_meters`, `farads`, `coulombs`, `siemens`, `joules`, `newtons`, `watts`, `ohms`, `moles`, `meters_per_second` | yes | yes | no | B | — |
| angle, gain | `degrees`, `decibels` | yes | yes | no | B | — |
| intensity | `arbitrary_units` | yes | yes | no | B | calls an a.u. number "cross-document comparable" (#6) |
| ph | `ph` (the class name, not a unit) | yes | yes | no | B | `source_unit` has nothing to hold (#6) |
| spatial_frequency | `cycles_per_degree` | yes | yes | no | B | only one without the per-sample-timing sentence |
| current, frequency, length, mass, temperature, time, voltage, volume | `amperes`, `hertz`, `meters`, `grams`, `celsius`, `seconds`, `volts`, `liters` | yes | yes | no | **A** | stale "mixin" wording (#1) |
| pressure | `mmhg` | yes | yes | no | **A** | no dated decision for mmHg (#7) |
| concentration | six optional: `molar`, `grams_per_liter`, `mass_fraction`, `volume_fraction`, `particles_per_liter`, `osmolar` | yes | yes | no | **A** | multi-canonical by design (`build_v_eta.py:9877-9881`) |
| count | `value` (integer) + `unit` (term = what is counted) | **no** | yes | no | **A** | `value.value`; `unit` is not a unit (#4, #5) |
| score | `value` + `scale` term + `scale_min`/`scale_max` | yes (item 46) | yes | no | **A** | `value.value` (#4) |
| date | `instant` (ISO char) + `precision` (enum) | **`source`** only | **no** | **yes** | own | (#9) |
| term | `value` is an `ontology_term` | no | no | **yes** | own | required binding keyed by a `variable` it lacks (#11) |
| label | `name` | no | no | **yes** | own | (#10) |
| logical | bare boolean array | no | no | no | own | reason recorded ("a boolean has no unit…") |
| position | `coordinates` (matrix, spacing units) | no | no | **yes** | own | (#10) |
| polynomial | `coefficients` + `degree` | no | no | **yes** | own | — |
| *`data.keys[]`* (parent) | `origin`/`spacing` `{value, source_value}`, `values {values, source_values}`, `unit` term, `source_unit` | yes | per key | — | — | the axis form |
| *`subject_statement.conditions[]`* (cross-check) | `quantity.value {value, source_value}`, `unit` term, `source_unit`, `count`, `term` | yes | yes | — | — | a third quantity spelling |
| tuning_curve / contrast_sensitivity `independent_variables[]` | `values` + `unit` term | **no** | **no** | — | — | no `labels`, no `n` (#14) |
| model_fit `independent_variables[]` / `dependent_variable` | `variable` + `unit` term (no values) | no | no | — | — | same name as tuning's, different shape (#20) |

The default values also differ (#2): the 26 single-slot quantities default `value` to `[{"approximate": false, "source_unit": "", "source_value": 0.0}]` without the canonical slot. The same typed cells default to `0.0` when nested in `chemical`/`formulation`/`dose`, and to `{}` when nested in `visual_grating`.

## Structured-composite comparison

| idea | tuning_curve (+ leaf) | contrast_sensitivity | harmonic_component | model_fit | receptive_field | visual_grating / timed_sequence |
|---|---|---|---|---|---|---|
| independent variables | `value.independent_variables[] {variable, values, unit}` **and** inherited `keys` | same as tuning **and** `keys` | via `keys` only ("one per reading") | `independent_variables[] {variable, unit}` | via the bodies' `keys` | — |
| control | `value.control {mean, stddev, stderr, individual}` | — | `value.control {real, imaginary}` (item 69) | — | — | `visual_grating.value.blank` **and** `timed_sequence.value.control_item` (#26) |
| fits | leaf `model_fit[] {model, coefficients (struct, **no fields**), goodness, metrics, sampled_fit}` | composite `model_fit[] {model, coefficients (**unnamed matrix**), sensitivity, relative_max_gain, empirical_c50, saturation_index}` | — | `coefficients[] {variable, value}`, `constraints[]`, `goodness`, `sampled_fit` | — | — |
| goodness | `{r2, sse}` | dropped (item 66) | — | `{r2, sse}` (built from tuning's, `build_v_eta.py:3684-3689`) | — | — |
| significance | leaf `visual_response_anova_p`, `across_stimuli_anova_p` | `visual_response_p_bonferroni`, `response_varies_p_bonferroni` | — | — | a separate plane | — |
| half-max / c50 | `metrics.half_maximum_below` (tuning plan item 6) | `interpolated_values.c50`, `model_fit.empirical_c50` | — | — | — | — |
| response unit | `response_unit` term | none | **none** | `dependent_variable.unit` | `planes[].quantity` | — |
| F0 / F1 | `response_type` char ("'F1'") | `modulated_response` bool **and** `response_type` char | `harmonic` int (1 = F1) | — | — | — |
| per-reading arrays | `mean`/`stddev`/`stderr`/`individual`/`raw_individual` parallel columns | per-frequency matrices | `real`/`imaginary` | — | bodies | `presentation_order` |

## Findings

### Cross-cutting: the quantity cells

1. **STALE-DOC — "shape-library mixin" / "Identity classes … inherit this `value`".** Twelve composites say this: concentration, count, current, frequency, length, mass, pressure, score, temperature, time, voltage and volume. For example `voltage.value`: *"A typed voltage value (shape-library mixin). Identity classes that read or impose a voltage inherit this `value`."* T6 (`V_eta_tenets.md:171-172`) and item 19 say otherwise: *"every `data_type` composite is concrete"*, and a standalone document is valid content. A mixin cannot stand alone. The other 16 single-slot quantities use template B, so there are two doc templates for one cell shape. *Suggestion:* rewrite the twelve in template B's wording.

2. **INCONSISTENCY — three default-value conventions for one typed cell.** Top-level: `voltage.value` `default_value` is `[{"approximate": false, "source_unit": "", "source_value": 0.0}]`, and the canonical `volts` is missing (the same holds for all 26 single-slot quantities, while `count` and `score` do include their `value`). Nested in `dose.value.mass`, `formulation.value.ingredients.volume`, `chemical.value.concentration` and the rest, the default is `0.0`, a number for a structure type. Nested in `visual_grating.value.angle` and `.duration`, it is `{}`. *Suggestion:* generate one default per cell type and reuse it wherever the type is nested.

3. **INCONSISTENCY — booleans default to `0.0`.** Every `value.approximate` sub-field has `"blank_value": 0.0, "default_value": 0.0`, and so do `contrast_sensitivity.value.modulated_response` and `visual_grating.value.blank`. By contrast, `data.keys.approximate`, `data.keys.regular` and `data_type.data_body` use `false`. *Suggestion:* use `false` for every `boolean`.

4. **INCONSISTENCY (T14) — `count` and `score` name their canonical slot `value`, which gives `value.value`.** T14 (`V_eta_tenets.md:368`) says *"Every canonical slot names its complete unit"*. `count.value.unit` records a reason (*"semantic, NOT dimensional"*). For `score`, I searched the tenets and items 1–70 and found no recorded reason for `value`; item 46 added `source_value`/`source_unit` but left the slot name alone. *Suggestion:* record the reason next to `score`, or rename both slots.

5. **QUESTION (T13) — `count.value.unit` is not a unit.** Its documentation reads *"What is counted (cells / individuals / spikes / events) -- semantic, NOT dimensional"*. Everywhere else `unit` is a measurement unit waiting for the unit vocabulary: `data.keys.unit`, `independent_variables[].unit`, `tuning_curve.value.response_unit` (item 57, *"a term like every other unit"*, to be bound under item 24). When item 24 binds units, "cells" will not be in that set. T13: *"a field's noun must match its semantics"*. *Suggestion:* rename it to what it holds (for example `counted`), before item 24 binds `unit`.

6. **QUESTION (carried, previous #14) — `intensity` and `ph`.** `intensity.value.arbitrary_units` is documented as *"the normalised, cross-document comparable number"*, which an a.u. value is not without `variable`. `ph.value.source_unit` has no unit to hold. The class documentation also reads garbled: *"A dimensionless (a.u.) — dF/F, fluorescence, ratios, amplitudes value cell"*. *Suggestion:* give the dimensionless cells their own wording.

7. **QUESTION (carried, previous #13) — `pressure.value.mmhg`.** The builder calls it *"attested in migrator code"* (`build_v_eta.py:9856-9858`). `data.keys.unit` lists mmHg among the practical-SI units. I found no dated decision for it: I grepped items 1–70 and the tenets for `mmhg`/`mmHg` and found nothing. Area has since been decided (item 57), but pressure has not. *Suggestion:* a one-line team confirmation.

8. **QUESTION — nested `mustBeNonEmpty` / `mustBeScalar` look declarative only.** In the local DID-matlab checkout, `validateDocument` calls `validateField` only for top-level block fields (`cache.m:869`), and `grep -n "validateField("` finds that single call site. I found no code that applies these flags to sub-fields. So `date.value.instant`, `chemical.value.substance`, `formulation.value.ingredients`, `tuning_curve.value.independent_variables` and `model_fit.value.coefficients[].variable` are all "required" on paper only. The same explains `timed_sequence.value.control_item` (`integer`, `mustBeScalar: true`, `blank_value: []`) not failing. I did not fetch DID-matlab, and I did not check `validateTypeShape` for per-type descent. *Suggestion:* confirm with the DID-matlab owners before relying on any nested flag.

### date, term, label, position, polynomial, logical

9. **QUESTION (carried, previous #15) — `date` departs from the cell pattern.** It has `value.source` (*"The raw input string, preserved"*) rather than `source_value`/`source_unit`, has no `approximate` (the enum `precision` stands in), and declares `value` `mustBeScalar: true, mustBeNonEmpty: true`, where every quantity is an optional array. I found no recorded reason. *Suggestion:* record why a date is always single.

10. **INCONSISTENCY — scalar-only values cannot carry the keyed arrays the decisions build on them.** `term.value`, `label.value`, `date.value`, `position.value` and `polynomial.value` are `mustBeScalar: true`. The validator enforces this at top level (`cache.m:1965` raises `did2:validation:notScalar`; `isScalarValue` at `:2047` is `isscalar(value)`). The decisions do not fit:
    - Item 21: the gene list is *"a standalone `term` document -- the labels of the count statement's gene key"*, so it has many terms.
    - Item 28: a cell list is *"one label per cell"* on a `label_calculation`.
    - `position.value`'s own documentation: *"Many positions (centroids, outline vertices) are a key over the things positioned"*.
    - `data.keys`: *"On a data_type document it describes the INLINE value"*.
    - A body is no way out for labels and terms: `data_type.datum_type`'s enum has no char or string type.

    By contrast the quantities and `logical` are `mustBeScalar: false` (*"Series-as-cardinality"*). *Suggestion:* set `mustBeScalar: false` on these five, or record how a keyed term/label array is stored.

11. **QUESTION — `term`'s required binding cannot resolve on a standalone `term`.** `term.value` constraints: `{"binding": {"keyed_by": "variable", …, "strength": "required"}}`. `variable` is declared on `subject_statement` (field list: `variable`, `conditions`), not on `data`/`data_type`, so a standalone `term` document (item 21's gene list) has no key to bind by. The documentation also frames the composite as a claim, *"The bound term this statement is about"*, which contradicts T6's *"a standalone data-type document is CONTENT, NOT A CLAIM"*. *Suggestion:* say what a standalone `term` is bound by, and drop "this statement".

12. **STALE-DOC (carried, previous #25) — `logical.value` still describes the withdrawn `valid_interval` fold and calls its own future open.** It says *"`logical` has no current user; retire-or-hold is an open team call"*. Item 52 decided *"`logical` stays, like every data type"*, and item 24 names a user: the gene mapping's *"`score` (or `logical`) document"*. Roughly 90% of the string (the absence rule, reading rules 1–4, and the `markgarbage.m` citations) is about `valid_interval`, which now migrates to `time_observation`. It also says *"this statement asserts"* (T6, as in #11) and calls `derived_from` *"an edge"*: under T15 the edge is `input_id`, and `derived_from` is a `directed_relation`. *Suggestion:* cut to the first paragraph and move the reading rules to wherever `time_observation` validity is documented.

### chemical / formulation / dose

13. **QUESTION — a bought ready-made formulation must still list ingredients.** `formulation.ingredient_id` has `"min_count": 1`, and `formulation.value.ingredients` has `mustBeNonEmpty: true`. Yet `product_id` is *"for a mixture bought ready-made (PBS tablets, saline)"*. Item 59 does not say whether such a product must be decomposed. *Suggestion:* confirm, or allow `product_id` alone.

### tuning_curve / contrast_sensitivity / harmonic_component / model_fit

14. **INCONSISTENCY — dimensions are declared twice, in two shapes.** Both composites inherit `data.keys[]` (item 65 moved it up to `data`: *"it declares the keyed array shape once"*), and both also carry `value.independent_variables[]`. The keys entry is the full axis (`n`, `regular`, `origin`/`spacing`, `values {values, source_values}`, `labels`, `labels_from`, `source_unit`, `approximate`). The independent-variables entry is `{variable, values, unit}` only, although `unit` says *"absent for a categorical variable"* and there is no `labels` slot for one. `tuning_curve.value.individual` adds an axis neither declares: *"(independent_variables[] axes + a trial axis)"*. The name `independent_variables` is signed (#67), which predates keys moving onto the value (items 60/65). *Suggestion:* team call. Either `independent_variables[]` becomes the key list, or it is typed as the key entry and the `keys` for the curve are stated to be unused.

15. **QUESTION (carried, previous #18) — parallel statistic columns.** `tuning_curve.value.mean`, `.stddev`, `.stderr`, `.individual`, `.raw_individual` and `.control.*` are parallel matrices over one grid, whereas item 15 says *"anything that looks like another column is a key"*. Nothing recorded since. *Suggestion:* a team call on body storage for tuning curves.

16. **INCONSISTENCY — free-text fields remain beside a bound term.** Item 57 made `response_unit` a term. `tuning_curve.value.response_type` (*"e.g., 'mean', 'peak', 'F1'"*), `tuning_curve.value.coordinates` (*"'compass', 'cartesian'"*) and `contrast_sensitivity.value.response_type` are still `char`. *Suggestion:* make them terms (unbound until the vocabulary exists).

17. **INCONSISTENCY — F0/F1 is encoded four ways.**
    - `contrast_sensitivity.value.modulated_response` (boolean, *"modulated (F1) rather than mean (F0)"*);
    - `contrast_sensitivity.value.response_type` (char, the same fact again, on the same composite);
    - `tuning_curve.value.response_type` (char, *"'F1'"*);
    - `harmonic_component.value.harmonic` (integer, *"0 = DC, 1 = F1"*).

    *Suggestion:* one field shape, for example `harmonic` everywhere, or one bound `response_type` term.

18. **INCONSISTENCY — only tuning states its response unit.** `tuning_curve.value.response_unit` exists. `harmonic_component.value.real` / `.imaginary` (a response, for example spikes/s) have no unit field anywhere, and neither does `contrast_sensitivity`. *Suggestion:* add `response_unit` to `harmonic_component`.

19. **VIOLATION (T14, T13) — `contrast_sensitivity.value.model_fit.coefficients` is an unnamed matrix.** Its documentation: *"Fitted Naka-Rushton coefficients, as the v1 `parameters_<variant>` vector. Element naming is a follow-up (needs the NDIcalc-vis parameter order)."* T14: *"Anything a consumer must know in order to read a value is declared in the schema"*. T13: *"fit coefficients are a named `coefficients` block"*. Item 68's `model_fit.value.coefficients[] {variable, value}` now gives a declared shape for exactly this. For comparison (out of scope), the leaf `tuning_curve_calculation.model_fit.coefficients` is a `structure` with no declared sub-fields (*"named, per the `model`"*), which is the same T14 defect previous finding #4 raised for `goodness`. *Suggestion:* use `{variable, value}` entries.

20. **INCONSISTENCY (carried, remainder of previous #5) — three fit shapes and two vocabularies.**
    - Shapes: see the structured table. Metrics sit in a `metrics` block on tuning, but flat on `contrast_sensitivity.value.model_fit` (`sensitivity`, `relative_max_gain`, `empirical_c50`, `saturation_index`).
    - Half-maximum: `interpolated_values.c50` and `empirical_c50` keep the name that tuning plan item 6 retired (*"`l50` and `interpolated_c50` → `half_maximum_below`"*).
    - Significance: `*_p_bonferroni` here, `*_anova_p` on the tuning leaf.
    - Model terms: the variant is baked in here (`naka_rushton_rb | _rbn | _rbns`) but is plain `naka_rushton` in `tuning_curve_calculation.model_fit.model` and `model_fit.value.model`.
    - `independent_variables[]` means `{variable, values, unit}` on tuning and `{variable, unit}` on `model_fit`.

    Item 66 fixed the placement and goodness only. *Suggestion:* a naming pass over `contrast_sensitivity` against tuning plan item 6 and item 68.

21. **QUESTION — `model_fit.value.input_field` / `output_field` hold v1 paths.** *"Field path, in the fitted document, of the independent values ("mydocumenttype.x")"* (`<- v1 fit_data.input_data_field`). The fitted document is itself migrated, and its fields are renamed. Item 68 does not say whether the migrator rewrites the paths. *Suggestion:* state which vintage the path addresses.

### receptive_field

22. **STALE-DOC — `receptive_field.value` still promises a method.** It reads *"…with the estimation method and one entry per stored plane"*. Item 57: *"`receptive_field.value` drops `storage_mode` and `method`"*. The value now declares only `planes`. *Suggestion:* drop "the estimation method".

23. **INCONSISTENCY (T6) — `planes[k]` is matched to a body by an order bodies do not have.** `value.planes` says *"ARRAY, one entry per emitted body in emission order"*. T6 (`V_eta_tenets.md:127`): *"Bodies point at their owner (`owner_id`) and the owner does not list them"*, and `data_body` declares no position field (its fields are `format` … `redundant`, `conditions`). So nothing records which body is plane k. Item 58's body `conditions` could state the plane's quantity on the body itself. *Suggestion:* move `planes[].quantity` into each body's `conditions`, or give the body a declared position.

### timed_sequence

24. **STALE-DOC — T15 left an old edge name behind.** `timed_sequence.value.presentation_order`: *"each a 0-based index naming a `item_id` edge directly (value k -> `presented_id_k`)"*. T15 (`V_eta_tenets.md:424`): *"A repeated edge repeats its name; it is never numbered"*. The same text is in `tools/build_v_eta.py:3478`. *Suggestion:* "value k is the k-th `item_id` entry".

25. **QUESTION — where the "timed" part lives is not declared.** `timed_sequence.value` is *"An ordered, timed list"*, but it declares no time field. The stimulus plan puts onsets on a `sampled_body` owned by the `timed_sequence_manipulation` (`V_eta_stimulus_model_plan.md:186-193`). Item 60 then says that when `value_id` is present *"the statement's own value and descriptors are empty"*, and `data_body`/`keys` are descriptors. So a manipulation that points at a shared sequence cannot own the onsets, and the sequence's documentation does not say they are its own time key. *Suggestion:* state it on `presentation_order` (for example "per-trial onsets are this document's time key").

26. **QUESTION — the control is stated twice.** `timed_sequence.value.control_item` (item 67) and `visual_grating.value.blank` (*"True for a control/blank (no-stimulus) trial (NDI 'isblank')"*) can disagree. `blank`'s documentation also says "trial", although a `visual_grating` is a deduplicated stimulus document, not a trial. Item 67 derives `control_item` from `isblank`, but does not say whether `blank` stays as the source. *Suggestion:* record which one wins, and fix "trial".

### visual_grating

27. **QUESTION (carried, previous #3) — `visual_grating.value.position` versus the `position` data type.** It is a structure `{x, y}` of `angle` cells (item 44). The `position` data type requires `coordinate_system_id`. T13 asks that *"a field's noun must match its semantics"*. *Suggestion:* team call on the name (for example `center`).

28. **STALE-DOC — the inherited `score` documentation reads wrongly under `contrast`.** `visual_grating.value.contrast.scale`: *"The scoring rubric (e.g. Murine Body Condition Score)"*. `.contrast.value`: *"half-integer steps are legal"*. Cosmetic. *Suggestion:* let the builder override sub-field documentation per use.

### Parents and the yardstick

29. **STALE-DOC — `data_type.data_body` cites the wrong item.** It reads *"A document marked true with no body pointing at it has lost its data -- the batch check (item 58)"*. The rule is item 60 (*"`data_body` true ⇒ at least one body owns the document (batch check)"*). Item 58 is the body split. *Suggestion:* cite item 60.

30. **STALE-DOC — the tenets contradict themselves on where `datum_type` lives, and still list a deleted class.**
    - The tenets place `datum_type` on the statement three times: T3 `:84` *"its `datum_type` on the statement (#73)"*; T6 `:111` *"with `datum_type` on the statement"*; T14 `:359-360` *"`datum_type`, stated ONCE on the statement"*.
    - Against that: T6 `:108` and the built `data_type.datum_type` (*"the ONE place the value type lives"*), per item 60.
    - The T15 table rows `:472` and `:474` still list `control_designation`, which item 67 deleted.

    *Suggestion:* re-sync the four lines.

## Mechanical pass

Method (script in the session scratchpad):
- For each of the 423 documentation strings (fields and edges, all depths, all 45 composites), I extracted every backticked identifier, every `word_id` token and every dotted `a.b` token.
- I checked each token against the 213 class names, the 564 field names (any depth, any class), the 72 edge names, and the declared dotted paths (inheritance followed for `class.path`).
- 190 tokens were checked and 44 did not resolve.

| judgement | n | tokens |
|---|---|---|
| **genuine stale** | 2 | `presented_id_k` (backtick + `_id` form), `timed_sequence.value.presentation_order`. See #24. |
| `<- v1` provenance or history, legitimate | 14 | `spatial_frequencies`, `fitless_interpolated_c50` (contrast_sensitivity); `control_response_real`, `control_response_imaginary` (harmonic_component); `r_squared`, `fit_data.input_data_field` ×2, `fit_data.output_data_field` ×2 (model_fit); `stimulus_tuningcurve`, `response_units`, `axes` ×2 (tuning_curve, receptive_field; each says "renamed from"/"rather than"); `pixels_per_cm` (NewStimGlobals, visual_grating) |
| NDI code identifiers, inside the stale `logical` text (#12) | 9 | `baseline_interval`, `identifyvalidintervals`, `loadvalidinterval`, `markvalidinterval`, `underlying_element`, `ndi.app.markgarbage`, `ndi.time.timereference`, `syncgraph.time_convert` ×2 |
| names that exist but not as a class/field/edge | 3 | `ontology_term` (a field type), `validity` (a rejected class name, rhetorical), `derived_from` (a `directed_relation` relation, called "an edge": see #12) |
| placeholder or pattern | 3 | `mydocumenttype.x` (example path), `control_*` (a pattern), `independent_variables[].variable` (exists; my resolver's miss) |
| regex artefacts (`e.g`, `a.u`) | 13 | not identifiers |

Stale-word sweep over the same 423 strings (substring count):

| word | hits |
|---|---|
| `radian` | 0 |
| `kilogram` | 0 |
| `storage_mode` | 0 |
| `sample_time` | 0 |
| `image` | 0 |
| `control_designation` | 0 |
| `control_real` / `control_imaginary` | 0 |
| `_#` | 0 |
| `relative_to` | 0 |
| `item 58` | 0 |
| `is_` | 0 |
| `spatial_frequencies` | 1 (provenance) |
| `presented_id` | 1 (#24) |
| `valid_interval` | 1 (#12) |
| `axes` | 3 (two rename notes; `tuning_curve.value.individual` "a trial axis", #14) |
| `mixin` / `shape-library` | 12 (#1) |
| `Identity classes` | 10 (#1) |
| `metres` | 1 (`position.value`, where every slot says `meters`; cosmetic) |

No composite has an `is_`/`has_` boolean, a camelCase field, or a numbered edge.

## Previous audit (2026-09-25) — status

| # | previous finding | status | evidence |
|---|---|---|---|
| 1 | visual_grating angles in degrees vs radians | MOOT | item 44: degrees everywhere; `angle.value.degrees`, `visual_grating.value.angle` is an `angle` cell |
| 2 | grating units only in prose | FIXED | item 44; every grating number is a typed cell (`angle`, `spatial_frequency`, `frequency`, `time`, `score`) |
| 3 | `value.position` name vs `position` | STILL OPEN | #27 |
| 4 | `contrast_sensitivity` `goodness` has no fields | FIXED | item 66, `goodness` dropped; not in `value.model_fit` |
| 5 | fit shape and names differ from tuning | STILL OPEN (partly) | goodness fixed; coefficients, c50 and p-value names remain (#19, #20) |
| 6 | fits on composite vs leaf | FIXED | item 66 records why they stay on the composite |
| 7 | `hartley_reverse_correlation` class-name marker | MOOT | item 43: both are retired v1 tombstones again (`reverse_correlation` fields `method`, `dimension_labels`) |
| 8 | unmigrated `hartley_calc` cannot validate | FIXED | item 43 + OPEN_ITEMS "CHECKED AND FIXED 2026-09-29 (`d78f2fa`)"; `hartley_reverse_correlation` declares `hartley_numbers` etc. |
| 9 | receptive_field doc says `axes[]` | FIXED | now *"on `keys` (renamed from `axes`, #73 item 14)"*; new staleness in #22 |
| 10 | `receptive_field.value.storage_mode` | FIXED | item 57; `value` declares only `planes` |
| 11 | 28 composites cite `sample_time` | FIXED | item 21; 0 hits for `sample_time` in scope; docs say *"Per-sample timing is a time key"* |
| 12 | "SI" claims vs units used | FIXED | `data.keys.unit`: *"PRACTICAL SI … grams, liters, celsius, mmHg"* |
| 13 | practical-SI family consistency | STILL OPEN (partly) | area decided (item 57); mmHg undecided (#7) |
| 14 | `intensity` "comparable"; `ph` source_unit | STILL OPEN | #6 |
| 15 | count / score / date depart | STILL OPEN (partly) | score gained source fields (item 46); `score.value.value` (#4), date (#9) |
| 16 | `response_units` free text | FIXED (partly) | item 57 `response_unit` term; `response_type`/`coordinates` still char (#16) |
| 17 | `independent_variables[]` thinner than the key | STILL OPEN | now also duplicates the inherited `keys` (#14) |
| 18 | parallel statistic columns | STILL OPEN | #15 |
| 19 | `harmonic_component` flat `control_*` | FIXED | item 69; `value.control {real, imaginary}` |
| 20 | agent shape declared three times | FIXED | item 59; `formulation.ingredient_id` → `chemical,formulation`, `dose.formulation_id` |
| 21 | `chemical.value.amount` typed `concentration` | FIXED | item 59; field is now `chemical.value.concentration` |
| 22 | `dose.value.route` two homes | FIXED | item 59; no `route` in `dose` |
| 23 | clock_alignment inline value + `value_id` | FIXED (decided) | item 70; T3/T6 amended |
| 24 | polynomial doc says `axis.n` | FIXED | now *"the key entry's `n`"* |
| 25 | logical doc describes `valid_interval` | STILL OPEN | carries a SUPERSEDED note, but still says "open team call" against item 52 (#12) |
| 26 | `image` `labels_from` without an edge | MOOT | item 51 retired `image`; item 65 put `key_labels_id` on `data`, so every data type has it |
| 27 | tenets repeat `sample_time` / `summary` | FIXED | T2 `:43-44` and T6 `:111` updated; new tenet staleness in #30 |
