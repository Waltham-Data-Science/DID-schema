# V2 homes for carry-050 (responses) and carry-056 (tuning)

This is a proposal for Jess Haley and Steve Van Hooser to decide. Nothing in it is decided, and every home below is **Proposed (not decided)**. No repository was committed to or pushed.

The questions are at the end. Each one can be answered in one line.

## 0. Heads, sources and denominators

**Heads read** (fresh clones, read only):

| repo | commit |
|---|---|
| did-schema `main` | `bd66f1a` |
| NDI-matlab `main` (v1 writers) | `3cb19a85f` |
| NDI-matlab `V2` (second pass) | `d88ea6cfb` |
| NDIcalc-vis-matlab | `00e3e0f` |
| DID-matlab `claude/phase2` | `3e63cef4` |

**Corpus:** the four zips present in this container: 20211116, Dab, JH and Soph. Corpus B is not here.

- They hold 208,896 v1 JSON documents in all (1,220 + 27,561 + 78,688 + 101,427), and every one of them parsed.
- Each zip was read in place, with nothing extracted, by scratchpad scripts in `homes/scripts/`:
  - `census.py` and `classes.py` for class counts;
  - `srs.py` and `ctlper.py` for responses;
  - `keys.py`, `spn.py`, `spn60.py` and `spl.py` for tuning;
  - an inline check for `abs`.
- Every count below comes from one of these scripts. The script is named next to each count.

**Class counts** (`classes.py`). These match the counts in the brief.

| v1 class | documents |
|---|---|
| `stimulus_response_scalar` | 10,124 (273 in 20211116, 9,851 in Soph) |
| `tuningcurve_calc` | 34,690 (84 in 20211116, 34,606 in Soph) |
| `contrasttuning_calc` | 22,896 (Soph) |
| `spatial_frequency_tuning_calc` | 2,804 (Soph) |
| `temporal_frequency_tuning_calc` | 2,800 (Soph) |
| `control_stimulus_ids` | 1,428 (11 + 1,242 + 175) |

**Not measured here:** I did not run the migrators, so how many documents would convert once these homes exist is not measured. The measurements below only show whether each field could be rebuilt from the other values that are kept.

## 1. carry-050: `stimulus_response_scalar` (OPEN_WORK row #137)

**Why it carries today.** DID-matlab `+migrators_j/stimulus_response_scalar.m:159-173` carries the whole document as v1 when either field below is set:

> `unplaced{end+1} = 'stimulus_response.stimulator_epochid';` ... `unplaced{end+1} = 'depends_on stimulus_control_id';`

### 1a. `stimulus_response.stimulator_epochid`

**Meaning.** It is the epoch of the stimulus presentation the response was computed against. NDI-matlab `main` `+ndi/+app/+stimulus/tuning_response.m:322-323`:

> `stimulus_response_struct = struct( 'stimulator_epochid', stim_doc.document_properties.epochid.epochid, ...`
> `'element_epochid', ts_epoch_timeref.epoch);`

**Corpus** (`srs.py`, denominator 10,124 responses):

- It is set on 10,124 of 10,124.
- It equals the response's own `element_epochid` on 10,124 of 10,124.
- It equals the referenced presentation's `epochid.epochid` on 10,124 of 10,124, with 0 that differ.

**Proposed home (not decided): no field.** Leave it unwritten when it equals `element_epochid`. That value is already kept as the response's epoch time reference (`stimulus_response_scalar.m:215-219`). This is the [restated values checked] pattern: the migrator checks that the two are equal, and carries the document as v1 only when they differ.

Under [device clocks on one epoch], equal ids from one session are one V2 epoch, so nothing is lost. If a future dataset has them differ, the later home would be a second `time_reference_id` whose referent is the stimulator's system. That rule already permits one reference per (clock, referent).

- **Change needed:** code only (DID-matlab `stimulus_response_scalar.m`). No schema change and no registry term.
- **Round trip:** exact. The reverse migrator copies `element_epochid`.

**Side note, not part of this proposal.** I found no place where NDI's second pass writes the v1 presentation's own `epochid.epochid` onto the V2 presentation:

- `+migrate/+internal/stimulusPresentationToItem.m` on `V2` reads it only into `report.epoch_id` (`:257`).
- Its manipulation is anchored "during the session" (`:724-725`):

  > `m = removeEdge(m, 'time_reference_id');`
  > `m = addEdge(m, did2.convert.mintSessionDuring('marker'), presentationId);`

That is why this proposal relies on `element_epochid` and not on the presentation. Not finding a write is not proof that the epoch is lost. It needs checking against [lossless means round trip].

### 1b. `depends_on stimulus_control_id`

**Meaning.** It names the `control_stimulus_ids` record the response was computed with. The writer reads that record to choose the control trials, so it is a true input:

- `tuning_response.m:297-298`:

  > `cs_ids = control_doc.document_properties.control_stimulus_ids.control_stimulus_ids(:);`
  > `controlstimids = unique(stim_doc.document_properties.stimulus_presentation.presentation_order(cs_ids(~isnan(cs_ids))));`

- `:332`:

  > `response_doc{end} = response_doc{end}.set_dependency_value('stimulus_control_id', control_doc.id());`

**Corpus** (`srs.py`, `ctlper.py`):

- The edge is set on 10,124 of 10,124 responses. It resolves to a `control_stimulus_ids` record about the same presentation on 10,124 of 10,124.
- In these zips each presentation has at most 1 control record (1,428 records on 1,428 presentations). The writer allows several, though: it loops over every record of a presentation (`tuning_response.m:117-134`). So the edge cannot be inferred and must be stored.
- 210 of 273 responses in 20211116 name a record whose value is a scalar NaN. 1,358 of 9,851 in Soph name a record with NaN entries. Under [NaN control means no control], these convert.

**Proposed home (not decided): `input_id`, beside the presentation.** Under [control pairing is a calculation], each `control_stimulus_ids` record becomes a `calculation` that keeps the record's id (`stimulusPresentationToItem.m:181`, "base.id = THE RECORD's id"). The v1 edge therefore already resolves to that calculation.

`calculation.input_id` is `multiple`, unordered and typed to `statement` (`schemas/did_v2/stable/calculation.json`). Both inputs are statements:

- the presentation is a `manipulation`;
- the pairing is a `calculation` with the method term "control stimulus pairing".

So the two are told apart by the document each one names.

- **Change needed:** code only.
  - DID-matlab: write the control id into `input_id` and drop the carry.
  - NDI-matlab: a check after the control fold. When a control record stays v1 (carry-091, or anything else carried), the responses that name it must carry as well, because `input_id` must name a statement.
  - No schema change and no registry term. The method term is a label today.
- **Round trip:** exact. The input that is the presentation gives `stimulus_presentation_id`, and the input that is the pairing calculation gives `stimulus_control_id`.

## 2. carry-056: tuning calculators (OPEN_WORK row #143)

**Why it carries today.** DID-matlab `private/jCalculation.m:160-183` carries the whole document as v1 when `jTuningCurve` lists a field it has no home for. `jTuningCurve.m:57-60` lists them:

> `relative_max_gain / saturation_index / sensitivity, SF/TF's 'abs' block, stimulus_tuningcurve's stimid / presentation numbers.`

**Presence** (`keys.py`):

| field | set on |
|---|---|
| `stimid` | 34,690 of 34,690 `tuningcurve_calc` |
| `stimulus_presentation_number` | 34,690 of 34,690 |
| `log` | 33,068 of 34,690 (1,622 empty) |
| `stim_property_list` | 22,896 of 34,690 (11,794 empty) |
| the three contrast metrics | 22,896 of 22,896 `contrasttuning_calc`, on each of the 3 fits (68,688 fit blocks) |
| `abs` | 2,804 of 2,804 SF and 2,800 of 2,800 TF |

### 2a. `tuningcurve_calc`: `stimulus_tuningcurve.stimid`

**Meaning.** For each point on the curve, it is the number (1-based) of the stimulus, in the presentation's `stimuli` list, whose parameters gave that point. `tuning_response.m:464`:

> `tuning_curve.stimid(I) = n; % this stimid`

**Proposed home (not decided):** a covariate along the curve's dimension, with variable `stimulus` (a label) and the values verbatim. This is exactly how the response migrator already keeps the response's `stimid` (`stimulus_response_scalar.m:209-210`, `did2.build.covariate(jLabel('stimulus'), 0, 'Value', ...)`). Under T6 a covariate is "what is known about the positions along one or more dimensions". On a grid curve ([tuning grid]) the covariate runs along all the grid dimensions.

- **Change needed:** code only (`jTuningCurve.m` `rawCurve`).
- **Round trip:** exact.

### 2b. `tuningcurve_calc`: `stimulus_tuningcurve.stimulus_presentation_number`

**Meaning.** For each point, it lists the positions (1-based) of the input response's readings that went into that point. `tuning_response.m:463` and `:473`:

> `stimulus_indexes = find(stim_response_doc.document_properties.stimulus_response_scalar.responses.stimid==n);`
> `tuning_curve.stimulus_presentation_number{I} = stimulus_indexes;`

**It restates kept values** (`spn.py`, `spn60.py`, denominator 34,690). It equals `find(input_response.stimid == stimid(I))` for every point on 34,690 of 34,690 curves:

- 34,630 match exactly. JSON stores it as trials × points.
- 60 match once the NaN padding is removed. Those curves have points with unequal trial counts, and the writer's `vlt.data.cellarray2mat` (`:500`) pads them. I did not read `vlt`; the padding is what I observed.

**Proposed home (not decided): no field.** Leave it unwritten, with a check, by the [restated values checked] pattern. It is rebuilt from `stimid` (2a) and the input response's `stimid`, which is kept whether that response is converted or carried. When the check fails, the document is carried.

- **Change needed:** code only.
- **Round trip:** exact, provided the rebuild pads short columns with NaN.

### 2c. `tuningcurve_calc`: `tuningcurve_calc.log`

**Meaning.** It is a text trace of the run: which value the "best", "greatest" or "least" selection picked, and which value was dealt. NDI-matlab `+ndi/+calc/+stimulus/tuningcurve.m`:

- `:117`: `log_str = cat(2,log_str,[char(parameters.input_parameters.selection(i).property) ' best value is ' num2str(stim_property_value) ',']);`
- `:233`: `deal_log_str = cat(2,deal_log_str,['dealing ' deal_here.field ' = ' num2str(deal_here.param1) ',']);`
- `:241`: `tuningcurve_calc_here.log = cat(2,tuningcurve_calc_here.log,deal_log_str);`

**The stored text does not follow the current writer.** In 22,896 of 34,690 the log contains `sz_{1}`, for example `"angle best value is 90.sz_{1}dealing sFrequency = 0.04,"` (`tcsample.py`). That is the output of the writer before NDI-matlab `49a875c94` (2026-10-14), which changed the line to:

> `-  deal_log_str = cat(2,deal_str,[...` / `+  deal_log_str = cat(2,deal_log_str,[...`

So the text cannot be rebuilt by rule, and parsing it would not give [one correct reading].

**Proposed home (not decided):** `statement.notes`, verbatim. Its definition is "irreducible human prose about this statement -- what happened" (`schemas/did_v2/stable/statement.json`). An empty log writes nothing.

- **Change needed:** code only.
- **Round trip:** exact. If notes are absent, the rebuild writes `''`.

### 2d. `tuningcurve_calc`: `tuningcurve_calc.stim_property_list` {`names`, `values`}

**Meaning.** These are the stimulus properties the run dealt over, and the value this curve was built at. Each one is an `exact_number` constraint applied to every stimulus in the curve. `tuningcurve.m`:

- `:157`: `stim_property_list{end+1} = parameters.input_parameters.selection(i).property;`
- `:162`: `deal_constraints_here.operation = 'exact_number';`
- `:236`: `stim_property_list_values(stim_prop_index) = deal_here.param1;`
- `:242-243`: `tuningcurve_calc_here.stim_property_list.names = stim_property_list(:)';` / `.values = stim_property_list_values(:)';`

**Proposed home (not decided):** `statement.conditions`, one entry per name, in v1 order. Each entry is `{variable: the v1 name as a label (e.g. "sFrequency"), quantity.value: the value}`.

- A condition is "a one-value fact true of EVERY value of the statement" (T6). A dealt value is exactly that.
- Conditions use T14's one entry shape.
- The label is verbatim, as the control-pairing calculation names its rule fields. Q5 offers the alternative.

**Change needed:** code only. **Round trip:** exact. The names come back in order, the values exactly, and an empty list writes no conditions.

**Note** (`spl.py`): all 22,896 dealt curves state `sFrequency` = 0.04. That fits the bug `49a875c94` fixed: "all N_deal tuning curves were built at the first value of the dealt property". The condition would still be true, because those curves *were* built at 0.04. The team may want to know that these 22,896 curves include duplicates.

### 2e. Contrast fits: `relative_max_gain`, `saturation_index`, `sensitivity`

**Meaning.** These are values read off each Naka-Rushton fit (RB, RBN, RBNS). NDIcalc-vis-matlab `+ndi/+calc/+vis/contrast_tuning.m:270-272`:

> `fit = setfield(fit,[prefixes{f} 'relative_max_gain'], fi.relative_max_gain);`
> `fit = setfield(fit,[prefixes{f} 'saturation_index'], fi.saturation_index);`
> `fit = setfield(fit,[prefixes{f} 'sensitivity'], vlt.data.colvec(fi.sensitivity));`

Each value, from `+vis/+contrast/+indexes/`:

- **Relative maximum gain:** `contrastfit2relativemaximumgain.m:9` "max(dR/dC)", on the fit normalised to its maximum after subtracting R(0) (`:27-29`). Heimel et al. 2005.
- **Saturation index:** `contrastfit2saturationindex.m:9` "SI = (Rmax - R(100)) / (Rmax - R(0))". It is NaN when undefined.
- **Sensitivity:** a 1 × 10 vector. `fitindexes.m:52-54` "contrast sensitivity with criteria of [1 ... 10] standard deviations of the control response", and `:111-116`. Each entry is 1/(the first contrast where the fit exceeds the criterion), or 0 if it never does (`contrastfit2sensitivity.m:8-11`). Its length is 10 on 68,688 of 68,688 fit blocks (inline check).

**Proposed home (not decided):** three optional fields in `tuning_curve.value.model_fit[].metrics`, named as `contrast_sensitivity.value.model_fit[]` already names the same three per-spatial-frequency values (`schemas/did_v2/stable/contrast_sensitivity.json`):

- `relative_max_gain` (double);
- `saturation_index` (double);
- `sensitivity` (matrix, 10 entries). Its documentation must declare that entry k is the criterion k × the control response's standard deviation (T14: "anything a consumer must know in order to read a value is declared").

These values are recomputable from the kept `sampled_fit` only by NDIcalc-vis code, so they are stored, not left out.

- **Change needed:**
  - a schema change: 3 fields on `tuning_curve.json` metrics, in did-schema;
  - then code in DID-matlab (`jTuningCurve.m` `oneFit`, `mmap` at `:503`).
  - No registry term.
  - Under rule 2 of "Changes the siblings must follow", adding optional fields breaks no sibling, so the schema can go first.
- **Round trip:** exact.

### 2f. Spatial and temporal frequency: the `abs` block

**Meaning.** It is the same fits and interpolated values, recomputed on the absolute value of the mean response curve. `spatial_frequency_tuning.m:291-300`:

> `resp_abs.curve(2,:) = abs(resp_abs.curve(2,:));`
> `abs_sf_props = vis.frequency.spatial_frequency_analysis(resp_abs);`
> `spatial_frequency_tuning.abs.fitless = abs_sf_props.fitless;` ... `spatial_frequency_tuning.abs.fit_gausslog = abs_sf_props.fit_gausslog;`

TF is the same (`temporal_frequency_tuning.m:294-303`). Each `abs` holds `fit_dog`, `fit_gausslog`, `fit_movshon`, `fit_movshon_c`, `fit_spline` and `fitless` on all 5,604 documents.

**It does not restate** (inline check):

- `abs` equals the top-level blocks on 0 of 2,804 SF and 0 of 2,800 TF.
- That includes the 1,669 SF and 1,582 TF documents whose mean has no negative entry, where abs(mean) = mean. The fits are not reproducible, so `abs` must be stored.

**Proposed home (not decided): a second calculation of the same class.**

- Its `input_id` is the first calculation, which keeps the v1 id.
- Its method is the decided general term, "curve fitting data transformation" (OBI:0200072, [method terms are general]), with one parameter `{variable: "response transform" (label), term: "absolute value"}`.
- Its value carries only the curve's dimensions and covariates, `model_fit[]` (from `abs.fit_*`) and `interpolated_values` (from `abs.fitless`), using the same mapping as the top-level blocks.
- It stores no `mean`, because |mean| restates the parent's.

This reuses `spatial_frequency_tuning_calculation` and `temporal_frequency_tuning_calculation` unchanged. The alternative, an option for Q6, is a schema change: a new `response_transform` field on the fit entry (`model_fit.value`, rule R17) plus a second `interpolated_values` block.

- **Change needed:** code (DID-matlab `jCalculation` / `jTuningCurve`), plus one registry row, "absolute value", or a label until a term is chosen. The registry has 880 rows and none is "absolute value" (grep of `schemas/V_eta_term_registry.json`).
- **Round trip:** exact. The reverse migrator finds the child through its `input_id` and rebuilds `abs.*` from it. The child's id is new; v1 gave the `abs` block no id.

## 3. Summary

| row | field | proposed home (not decided) | change | round trip |
|---|---|---|---|---|
| carry-050 | `stimulator_epochid` | unwritten; equals `element_epochid` (checked) | code | exact |
| carry-050 | `stimulus_control_id` | `input_id` → the control-pairing calculation | code (DID, NDI) | exact |
| carry-056 | `stimid` | `stimulus` covariate on the curve's dimension | code | exact |
| carry-056 | `stimulus_presentation_number` | unwritten; rebuilt from `stimid` (checked) | code | exact |
| carry-056 | `log` | `notes`, verbatim | code | exact |
| carry-056 | `stim_property_list` | `conditions`, one per dealt property | code | exact |
| carry-056 | contrast `relative_max_gain`, `saturation_index`, `sensitivity` | 3 new `metrics` fields | schema + code | exact |
| carry-056 | SF/TF `abs` | a second calculation, method "absolute value" | code + 1 term | exact |

## 4. Questions

Each one can be answered in one line. My recommendation comes first.

1. **`stimulator_epochid`:** leave it unwritten when it equals the response's `element_epochid` (10,124 of 10,124), and carry the document when it does not? *Recommend: yes.*
2. **`stimulus_control_id`:** put it in the response's `input_id`, beside the presentation, pointing at the control-pairing calculation (same id), with the response carried whenever that control record stays v1? *Recommend: yes.*
3. **`stimid` and `stimulus_presentation_number`:** keep `stimid` as a `stimulus` covariate, and leave `stimulus_presentation_number` unwritten because it is rebuilt from it (34,690 of 34,690, checked)? *Recommend: yes.*
4. **`log`:** keep it verbatim in `notes`, because 22,896 of 34,690 logs come from an older writer and cannot be rebuilt by rule? *Recommend: yes.*
5. **`stim_property_list`:** make each dealt property a condition. Is its variable (a) the v1 name as a label (e.g. "sFrequency"), or (b) the variable the stimulus `method` documents use ("spatial frequency", NDI `stimulusRecipe.m:211`)? *Recommend: (a) for the generic stage, because it is exact and needs no table. Choose (b) if you want conditions and stimulus parameters to match by name.*
6. **SF/TF `abs`:** (a) a second calculation of the same class, with method parameter "response transform: absolute value", or (b) a schema change adding a transform field to the fit entry and a second `interpolated_values`? *Recommend: (a). It needs no schema change.*
7. **Contrast metrics:** add `relative_max_gain`, `saturation_index` and `sensitivity` (10 entries, criteria 1 to 10 × the control response's standard deviation) to the tuning fit entry's `metrics`, named as on `contrast_sensitivity`? *Recommend: yes.*
