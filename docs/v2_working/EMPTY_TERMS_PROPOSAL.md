# Terms the migration writes with no registered node: proposal (research only, nothing decided)

**Every row below is Proposed (not decided).** Nothing was minted, committed, pushed or posted.
No file in any repository was written; `git status --short` in did-schema printed nothing after
the run. Scratch files in this folder: `batch.json` (33 rows), `propose_out.txt` (full
`propose_terms.py` output), `ols/*.json|txt` (OLS4 and Wikidata answers), `dl/` (NIF-Ontology,
NDIcalc-vis-matlab and vhlab-toolbox-matlab clones, read only).

## Denominators (first)

| what | count | source |
|---|---|---|
| did-schema HEAD | 06451d7 "[markdown cleanup and rename]: the JSON registers are renamed too" | `git log --oneline -1` |
| measured unregistered-term lines | 102 lines, 56 distinct (name, node), from 28 of 117 fixture bodies | `phase1-unregistered-terms.txt` |
| of those, asked about here | 35 distinct names (all present in the list) | brief; checked by script |
| asked about here, not in the list | 3: bath solution, single unit, multi-unit (from decisions) | `V_eta_go_forward_class_audit.md` [bath is two statements], [sorted units are cells or groups] |
| in the list, not asked about | 21 (end of this document) | same script |
| term registry entries | 865 | `schemas/registry/did_v2_term_registry.json` `terms` |
| CURIE registry prefixes | 56 | `propose_terms.py` DENOMINATOR line |
| EMPTY ids allocated | EMPTY:0000001-0000405; next free 0000406 | empty-ontology 25188df (`V2`), `grep -o 'EMPTY_0000[0-9]*' empty-edit.owl \| sort -u \| tail` printed 0000403-0000405 |
| NDI v1 truth | NDI-matlab locked `main` 3cb19a85 | `tools/sibling_lock.json` |
| DID-matlab | locked head a502c76 | same |
| NIF-Ontology | e0b6941 (2026-07-24 slim sync) | `git clone --filter=blob:none` |
| NDIcalc-vis-matlab | 00e3e0f | same |

Hosts: OLS4 (`www.ebi.ac.uk/ols4/api/search`) answered every query. Wikidata `wbsearchentities`
answered, then HTTP 429 on later calls. **InterLex could not be searched**: `scicrunch.org/api/1/ilx/search`
and `api.scicrunch.io/elastic` returned 401 (they need an API key), `scicrunch.org/scicrunch/interlex/search`
returned 403, `uri.interlex.org/base/ilx_0107265.json` returned 520. The SciCrunch RRID resolver
(`scicrunch.org/resolver/RRID:SCR_016422.json`) answered. No request carried an email address.

## `propose_terms.py` result

    EMPTY_ONTOLOGY=<scratch>/sib/empty-ontology python3 tools/propose_terms.py <scratch>/emptyterms/batch.json \
        --decided "PROPOSED (not decided)" --first-used-in "migration unregistered terms (phase1)"   # exit 0

    DENOMINATOR: 33 row(s) read from .../emptyterms/batch.json; 865 registered term(s); 56 CURIE prefix(es); empty-ontology read from .../sib/empty-ontology/...
    SUMMARY: 9 REGISTERED, 0 USE REGISTRY, 24 ADD, 0 FAIL

9 REGISTERED (reuse, nothing to add), 6 ADD with an existing ontology node, 18 ADD staged (an EMPTY
id each). The printed rows carry `"decided": "PROPOSED (not decided)"`; a team decision fills that.

## Summary of verdicts (38 items)

| verdict | items | terms |
|---|---|---|
| **existing term** | 12 | 8 already registered (element type -> Equipment Type, ndi element class -> software class, imaged region -> Anatomic Site, waveform window start -> analysis window start, filter type -> Chebyshev type I filter + high-pass filter, filter high -> passband low edge, filter order, filter ripple -> passband ripple); 4 need a registry row (Numeric Value, Model Number, clustered data set, fraction) |
| **new EMPTY** | 18 items, 17 distinct terms (+1 unmeasured sibling) | the two acquisition timestamps share one term; "depth position on device" is added for the unmeasured third probe axis |
| **not a term** | 8 | ndi.probe.timeseries, ndi.calc.vis.contrast_sensitivity, linear, filter.do filter, filter.filter low, kilosort, kiasort, threshold |

Two existing terms are also needed for slots the "not a term" items vacate: Spike sorting
(wikidata:Q2003571) and curve fitting data transformation (OBI:0200072), both ADD rows.

---

## 1. Existing terms (T19 steps 1 and 2)

| item (as written today) | proposal | node | definition (ontology's) | why it fits / note |
|---|---|---|---|---|
| numeric value (treatment, unlabelled number condition) | **Numeric Value** | NCIT:C81274 | "Information in the form of a numeral contained in a data field." | Exactly the unlabelled-number meaning ([treatment_number_unlabelled], `treatment.m`). ADD. Near: SIO:000070 measurement value (says it measures an attribute, which the source does not say). |
| element type | **Equipment Type** (registered) | NCIT:C178920 | "The type of equipment used." | Registered 2026-10-21 (binding variables). Applies to `device` elements only ([element types have no default]); see debatable choice 5. |
| ndi element class | **software class** (registered) | EMPTY:0000401 | "A class defined in a software library, named by its fully qualified name, ..." | Decided 2026-10-26 [census terms] for `session_creator`; same meaning. Its value (`ndi.probe.timeseries`) is text, section 3. |
| imaged region (ontology_image) | **Anatomic Site** (registered) | NCIT:C13717 | "Named locations of or within the body." | Already the variable for v1 `probe_location` / `treatment` locations; the image document carries "imaged" (T19). Near: NCIT:C85402 Imaging Region of Interest is a contour ROI, not an anatomical region; NCIT:C74298 Field of View is an extent. |
| probe model | **Model Number** | NCIT:C99285 | "The identifier assigned to a particular design of a device." | Sibling of registered Catalog Number NCIT:C99286. NDI fills `probe_model` from ProbeInterface `model_name` or a Kilosort map `name` (`fromProbeInterface.m:122-123`, `fromKilosortMap.m:120-121`): an identifier, so the value is **text**, not a term (today `probe_geometry.m` writes `ValueKind 'term'`). Alt: IAO:0000017 model number. ADD. |
| spike cluster assignment (jrclust/kilosort/kiasort) | **clustered data set** | OBI:0000648 | "A data set that is produced as the output of a class discovery data transformation and consists of a data set with assigned discovered class labels." | The per-spike label series is exactly this. OLS: cluster assignment, cluster label, spike cluster. ADD. |
| waveform window start | **analysis window start** (registered) | EMPTY:0000281 | "The start of the stretch of a time series a value was computed from, as a signed time from a reference time point ... negative before the reference, positive after." | The waveform is cut from that stretch; reference = the threshold crossing (`spikeextractor.m` doc: "Samples before the threshold to include"). Needs a duration sibling (section 2, #14). |
| filter.filter type `cheby1high` | **Chebyshev type I filter** + band **high-pass filter** (registered) | EMPTY:0000387, wikidata:Q262754 | registry rows | Decided [filters are methods], [filter terms from Wikidata]: the filter is a `method` document, not parameters of the spike extractor. `spikeextractor.m:40-44` builds `cheby1(order, ripple, filter_high/(0.5*sr), 'high')`. |
| filter.filter high | **passband low edge** (registered) | EMPTY:0000390 | "The lowest frequency a filter is designed to pass." | For a high-pass design `filter_high` is the cut-off below which it attenuates (same line). |
| filter.filter order | **filter order** (registered) | EMPTY:0000394 | | same decision |
| filter.filter ripple | **passband ripple** (registered) | EMPTY:0000395 | | `cheby1`'s second argument is passband ripple in dB |
| dilution (virus_injection `source_unit`) | **fraction** | UO:0000191 | "A dimensionless ratio unit which relates the part (the numerator) to the whole (the denominator)." | NDI documents the field as "Dilution factor (real number between 0 and 1)" (`virus_injection_schema.json`), i.e. strength relative to stock, so the number needs no conversion. ADD. Alt: UO:0000322 fold dilution ("ratio of concentration of two solutions"), idiomatic as 10 for 1:10, but needs 1/x. Note: `source_unit` records what the source wrote, and the source wrote no unit, so `source_unit` should arguably be empty and `fraction` go in `unit`. |

Supporting rows for vacated method slots (section 3):

| slot | proposal | node | definition |
|---|---|---|---|
| sorter run method (kilosort, kiasort, and jrclust) | **Spike sorting** | wikidata:Q2003571 | Wikidata: "techniques for the analysis of electrophysiological data" (thin; the row writes its own, as [filter terms from Wikidata] did): "A data transformation that assigns the action potentials detected in an extracellular recording to the putative neurons that fired them, by clustering their waveforms." No OBO term found (OLS: spike sorting, spike sorting software). |
| contrast-sensitivity calculator method | **curve fitting data transformation** | OBI:0200072 | "A curve fitting is a data transformation that has objective curve fitting and that consists of finding a curve which matches a series of data points ..." Alt: STATO:0000218 model fitting. |

## 2. New EMPTY terms (none found in an ontology)

Labels follow conventions rule 2 (lower case except proper names; nothing the document carries:
no "spike", "probe", "sorter" or "NDI" where the method or subject already says it). Definitions
follow rule 3 (genus + differentia, no units). The genus "A setting of ..." follows registered
EMPTY:0000305 *interpolation method*. Each would take the next id from EMPTY:0000406.

**Superseded rows (2026-10-27).** Rows 1, 2, 4, 7, 8 and 8a are struck through: by Jess Haley's decisions of
2026-10-27 in `V_eta_go_forward_class_audit.md` ([afo prefix registered], [n-trode is a multielectrode array],
[site positions are coordinates]) they are not minted, and each row names the existing term that takes its place.
The counts elsewhere in this document are as measured before those decisions.

| # | item(s) | label | definition | parent | why no existing term fits (OLS4 queries, near misses) |
|---|---|---|---|---|---|
| 1 | n-trode (element type value) | ~~**n-trode**~~ Superseded, not minted: Jess Haley, 2026-10-27, `V_eta_go_forward_class_audit.md` [n-trode is a multielectrode array]: wikidata:Q1952355 multielectrode array, with the number of electrodes as a statement on the device | An extracellular recording device made of a few electrodes placed close together, so that the spikes of a nearby neuron are recorded on several of its electrodes at once. | multielectrode array (wikidata:Q1952355) | Queries: tetrode, stereotrode, electrode array, multielectrode array, linear electrode array. No OBO tetrode/n-trode. OBI:0003808 multi-electrode array plate is a culture plate. Wikidata Q7706810 "Tetrode" (description "Biology" only) is narrower. NDI: "A bundle of N extracellular electrodes" (`PROBE-TYPES.md:19`, cited in `ELEMENT_TYPES_DRAFT.md`). Tetrode and stereotrode are narrower (n = 4, 2), not synonyms. **The other 36 element-type values in `ELEMENT_TYPES_DRAFT.md` need the same pass; only n-trode is measured here.** |
| 2 | acquisition timestamp (dev_local_time), acquisition timestamp (no_time) | ~~**acquisition time**~~ Superseded, not minted: Jess Haley, 2026-10-27, `V_eta_go_forward_class_audit.md` [afo prefix registered]: AFO:AFR_0001158 acquisition time | The time at which the data a statement describes were acquired, as read on the clock that recorded them. | time measurement datum (IAO:0000416) | Queries: acquisition time, acquisition date time, image acquisition date time, timestamp. NCIT:C181736 Image Acquisition Date ("The date that imaging data was acquired for a sample") is a date only and imaging-specific; AFO acquisition time (prefix not registered); NCIT:C94858 is a PET frame. **The clock leaves the label** (T19): today `image_stack.m:248` writes `['acquisition timestamp (' clk ')']`. `dev_local_time` has a registered node (EMPTY:0000403); `no_time` is NDI's "No timing information" (`clocktype.m:29`) and has none by [clock terms get nodes] item 2. Where the clock then goes (a second condition, or a time reference) is a modelling question, not a term. |
| 3 | spike sort quality (label and number) | **unit isolation quality** | A rating, made when a spike sorting is curated, of how well the spikes assigned to one sorted unit are separated from those of other neurons and from noise. | categorical measurement datum (OBI:0000938) | Queries: cluster quality, isolation quality, unit isolation, well isolated unit. Nothing in OLS. The values are sorter-specific: NDI `spikesorter.m:257-270` maps 'Excellent' 1, 'Good' 2, 'Multi-unit' 3, 'Not useable' 5, 'Unselected' -1; the Kilosort import uses labels "good"/"mua" (`+kilosort/probe.m:196`). One variable for the label and the number, as today. |
| 4 | spike sorter cluster index | ~~**cluster identifier**~~ Superseded, not minted: Jess Haley, 2026-10-27, `V_eta_go_forward_class_audit.md` [afo prefix registered]: AFO:AFR_0003339 cluster identifier | An identifier that a clustering gives to one of the clusters it found, unique only within the output of that clustering. | identifier (IAO:0020000) | Queries: cluster identifier, cluster label, class label. AFO:AFR_0003339 "cluster identifier" has this meaning but AFO is not a registered prefix (team choice: register `afo` instead). GENEPIO:0000136 and MS:1002407 are genomic / protein. OBI:0000963 categorical label is broader. |
| 5 | model fit (vmspikefit, fitcurve) | **model fit** | The result of fitting a mathematical model to data: the model, the values estimated for its coefficients, and measures of how well it fits. | data entity (IAO:0000027) | Queries: model fit, fitted model, model fitting, curve fitting. STATO:0000218 model fitting and OBI:0200072 are the *process* (fit the method slot, not the variable); BAO:0000625 curve fit model is the equation alone (it fits `model_fit.model`, the parent of #6); STATO:0000144 model parameter estimate is one coefficient. |
| 6 | naka rushton RB, RBN, RBNS | **Naka-Rushton function** | A saturating function of stimulus contrast c, R(c) = Rm c^n / (c^(n s) + c50^(n s)), with maximum response Rm, semi-saturation contrast c50, exponent n and saturation exponent s, used to describe how a response grows with contrast. | curve fit model (BAO:0000625) | Queries: Naka-Rushton, Naka-Rushton function, hyperbolic ratio function, contrast response function, Hill equation. Only BAO:0000435 Hill equation (ligand binding; same form for s = 1, different meaning). Wikidata: only an article. **One term, not three**: the variants differ only in which parameters were free. NDIcalc-vis-matlab `contrast_sensitivity.docs.output.txt`: RB = "[Rm C50]" 2-parameter, RBN = "[Rm C50 N]", RBNS = "[Rm C50 N S]" "with saturation"; `+vis/+contrast/naka_rushton_func.m`: "C.^N./(C.^(N*S)+c50.^(N*S)) ... If S is not specified, S is assumed to be 1", N defaults to 1. So RB = this function with constraints n = 1, s = 1; RBN with s = 1; RBNS none, in `model_fit.constraints` (which `jModelFit.m` already fills). |
| 7 | site location (left-right) | ~~**left-right position on device**~~ Superseded, not minted: Jess Haley, 2026-10-27, `V_eta_go_forward_class_audit.md` [site positions are coordinates]: NCIT:C44477 X-Coordinate, in the device's own frame | The position of a point of a device along the axis running from its left to its right as seen facing the device, negative to the left and positive to the right. | Coordinate (NCIT:C44465, registered) | NDI: "Left (negative)/ right (positive) site positions from facing the electrode" (`probe_geometry_schema.json`). Queries: electrode contact position, electrode site, recording site location, contact site. NCIT X-Coordinate (C44477) / Y-Coordinate (C44478) are registered but name no frame; NDI's axes are the device's own. Alternative: one variable Coordinate plus three axis terms (same count of mints). |
| 8 | site location (front-back) | ~~**front-back position on device**~~ Superseded, not minted: Jess Haley, 2026-10-27, `V_eta_go_forward_class_audit.md` [site positions are coordinates]: NCIT:C44478 Y-Coordinate, in the device's own frame | The position of a point of a device along the axis running from its front to its back as seen facing the device, negative toward the front and positive toward the back. | Coordinate (NCIT:C44465) | as #7; NDI "Front (negative)/ back (positive) site positions from facing the electrode" |
| 8a | site location (depth) **(not in the measured list; same migrator, `probe_geometry.m:88`)** | ~~**depth position on device**~~ Superseded, not minted: Jess Haley, 2026-10-27, `V_eta_go_forward_class_audit.md` [site positions are coordinates]: NCIT:C44479 Z-Coordinate, in the device's own frame | The position of a point of a device along the axis along which the device is inserted, measured from the device's own reference point. | Coordinate (NCIT:C44465) | as #7; NDI documents only "Depth of site positions", so the reference point and sign are not stated in v1; the definition must be checked with the team |
| 9 | center range time | **peak search window duration** | A setting of an event detector: the duration, starting at a threshold crossing, within which it searches for the extremum of the event to align the event on. | duration (PATO:0001309) | NDI: "center_range ... Range in samples to find spike center" (`spikeextractor.m` doc), used to centre waveforms (`:248`). Queries: peak alignment, alignment window, waveform window. NMR peak alignment is spectroscopy. |
| 10 | read time | **processing segment duration** | A setting of a method that processes a long signal in pieces: the duration of the piece of the signal it reads and processes at one time. | duration (PATO:0001309) | NDI: "Number of seconds to read in at a single time" (`spikeextractor.m:186`). Queries: recording chunk, data chunk length, buffer length, segment duration. Nothing. (It is a computational setting, but the parameter slot is a vocabulary slot, so it needs a node.) |
| 11 | standard-deviation threshold | **standard-deviation threshold** | A detection threshold given as a multiple of the standard deviation of the signal it is applied to. | Threshold (NCIT:C48228) | Queries: spike threshold, detection threshold, threshold, multiple of standard deviation. NCIT:C48228 "The lowest limit at which something becomes detectable or relevant" fits the **absolute** threshold (`absolute voltage threshold`, not in the measured list), which should take C48228 itself. The two stay separate quantities, as `jSpikeExtractionSettings.m` argues. |
| 12 | threshold sign | **threshold crossing direction** | A setting of an event detector: the direction in which a signal must cross the detection threshold for an event to be detected, -1 for a crossing from above to below and 1 for a crossing from below to above. | direction (PATO:0000039) | NDI: "Threshold crossing sign (-1 means high-to-low, 1 means low-to-high)". Queries: threshold crossing, threshold polarity. BAO:0002125 / NCIT:C161328 are qPCR cycle thresholds. PATO:0000039's own definition is a TODO, so the parent is weak. |
| 13 | refractory period | **detection refractory period** | A setting of an event detector: the shortest interval after a detected event within which no further event is accepted. | duration (PATO:0001309) | `vlt.signal.refractory(locs, refractory_samples)` drops events (`spikeextractor.m:235`). Existing terms all name the **physiological** period of a cell: wikidata:Q70578475 "electrophysiological refractory period" (registered prefix), SNOMED 251570008 "Nerve refractory period" and 10011003 (the `snomedct` prefix **is registered**, contrary to the brief), MeSH D012032 (prefix not registered). The detector's setting is chosen to mimic that period but is not a property of the cell. Related synonym "refractory period"; Q70578475 as cross-reference. Debatable choice 4. |
| 14 | waveform window duration | **analysis window duration** | The duration of the stretch of a time series a value was computed from, measured from its start (analysis window start). | duration (PATO:0001309) | Sibling of registered EMPTY:0000281 / 0000282. The decided shape is anchor + extent ("ANSWER 1 of the sign-off review", `jSpikeExtractionSettings.m`), so the registered *analysis window end* cannot be used. |
| 15 | bath solution ([bath is two statements]) | **bath solution** | A solution in which an organism, tissue preparation or cell is immersed during an experiment, and which sets its extracellular conditions. | Solution (NCIT:C70830) | Queries: bath solution, bathing solution, perfusion solution, extracellular solution, external solution, recording solution, artificial cerebrospinal fluid, physiological saline. REPRODUCE-ME `BathSolution` exists but has no definition and its prefix is not registered. XCO perfusates and XCO:0000830 aCSF are specific compositions and are conditions; they are candidates for the *value*, not the variable. |
| 16 | single unit ([sorted units are cells or groups]) | **single unit** | A sorted unit whose spikes are judged to come from one neuron. | categorical label (OBI:0000963) | Queries: single unit, single unit activity, sorted unit, neuron unit. OBI:0002187 single-unit recording and ECO:0006045 are assays / evidence. **InterLex not searched** (no key); NIF-Ontology e0b6941 `ttl/*.ttl` and `ttl/generated/*.ttl`, grep `(single\|multi)[- ]?unit`, printed nothing. The brief says InterLex has these terms: that is not contradicted here, only not checked. Check InterLex before minting. |
| 17 | multi-unit | **multi-unit** | A sorted unit whose spikes are judged to come from several neurons whose spikes cannot be told apart. | categorical label (OBI:0000963) | as #16; OBI:0002188 multi-unit recording is an assay |

Synonyms (rule 4): #13 related synonym "refractory period"; #6 related synonym "hyperbolic ratio
function" if the team accepts it; #1 none (tetrode and stereotrode are narrower). No lab codes
(`RB`, `cheby1high`, `site_locations_leftright`) are synonyms; they belong in the term comments.

## 3. Not terms

| item | why not | what instead |
|---|---|---|
| ndi.probe.timeseries | An NDI class name: a code, not a concept (conventions rule 4). | Text value of the "software class" (EMPTY:0000401) assertion, as `session_creator` is under [census terms]. Today `element.m` `kindAssertion` stages it as a term. |
| ndi.calc.vis.contrast_sensitivity (method term) | The calculator's class name, which already names the software entity (`jCalculation.m:135` `jSoftware(methodName, ...)`). | Method term = OBI:0200072 (section 1). **The same applies to every jCalculation caller**, which all pass a class name: `ndi.calc.vis.contrast`, `.spatial_frequency_tuning`, `.speed`, `.temporal_frequency_tuning`, `ndi.app.stimulus.tuning_response`, `ndi.calc.stimulus.tuningcurve` (grep of `+migrators_j/*.m`). Why only contrast_sensitivity appears in the measured list is not measured. |
| kilosort, kiasort (method term) | Software, not a method ([sorter software] already names the software entity from the v1 class). | Method term = Spike sorting (wikidata:Q2003571). The software entity carries `global_identifier` RRID:SCR_016422 for Kilosort (resolver: name "KiloSort", "Software tool that implements an integrated template matching framework for detecting and clustering spikes ..."). No RRID found for KIASORT or JRCLUST in NIF-Ontology `scicrunch-registry.ttl` (grep `kiasort\|jrclust` matched only IronClust SCR_018903). |
| linear (probe model value) | A test value, not a writer value: DID-matlab `testFixtureCorpus.m:1127` `'probe_model','linear','manufacturer','acme'`. NDI fills `probe_model` with a model identifier. | Text value under Model Number (section 1). |
| filter.do filter | A switch on whether the filter method exists. | `do_filter` 0 or `filter_type` 'none' (`spikeextractor.m:46`) = no filter method document; 1 = one. |
| filter.filter low | Not read by the writer for its only design: `makefilterstruct` uses `filter_order`, `filter_ripple` and `filter_high` (`spikeextractor.m:40-44`). | Default 0 ([writer default is not set]); a non-default value is a carry question, not a term. |
| threshold (contrast_sensitivity input parameter) | **A fixture artifact.** DID-matlab `testFixtureCorpus.m` `fx_contrast_sensitivity_calc` writes `'input_parameters', struct('threshold',1)`; the writer's own documentation says `input_parameters`: "The parameters the calculator was run with; empty for this calculator, which takes none." (NDIcalc-vis-matlab 00e3e0f `+ndi/+calc/+vis/docs/contrast_sensitivity.docs.output.txt`). | No term. The fixture should be corrected (DID-matlab). |
| (spike_extraction filter.* as a group) | Seven `filter.*` names come from `jSpikeExtractionSettings.m` grouping the filter fields "so the frequency_filter build can find them", then `jParameterList.m:39` flattening the group into parameter names. | Under [filters are methods] (decided) they become one filter `method` document using registered terms (section 1). Build pending in DID-matlab. |

Generalisation (T19): there is no case for one "spike sorting parameter" term: each parameter has
its own meaning and unit, and the method term already says "spike detection". Instead the labels
drop "spike" (detection refractory period, threshold crossing direction, peak search window
duration, analysis window duration) so they serve any event detector.

## 4. The five most debatable choices

1. **Software and calculator names leave the method slot.** kilosort / kiasort become Spike sorting
   (wikidata:Q2003571) with Kilosort's RRID on the software entity, and every
   `ndi.calc.*` class name becomes a general method term. This touches 7 calculator migrators, not
   the one measured. The alternative keeps names as method terms, with rrid:SCR_016422 as Kilosort's
   node (0 registry rows use an RRID node today) and an EMPTY term per calculator and sorter.
2. **Naka-Rushton: one term plus constraints**, rather than three terms for RB / RBN / RBNS. This
   needs `jContrastSensitivityValue.m` to write `constraints` (n = 1, s = 1; s = 1) instead of
   `naka rushton RB` names, and it relies on NDIcalc-vis-matlab's own documentation of the variants.
3. **single unit / multi-unit as EMPTY terms** before InterLex was searched (401/403 without a key).
   The brief says InterLex/NIF has them. If it does, they should be used, which needs the
   `interlex` prefix (already registered, 34 ILX rows). The second debatable point here is
   *unit isolation quality* carrying both the sorter's label and its number.
4. **refractory period as a new detector setting** rather than an existing physiology term
   (wikidata:Q70578475, or SNOMED 251570008 under the registered `snomedct` prefix). Reusing those
   would say the parameter is a property of the neuron. It also unifies with
   `vmspikefilteringparameters.refract`, so the choice covers both.
5. **element type -> Equipment Type (NCIT:C178920, registered)** for device elements, rather than an
   EMPTY "device type" that follows the *material type* / *culture type* precedent. The
   definition "The type of equipment used" is about use in a procedure, not about what the subject
   is. Separately, with no type assertion for sorted units, v1 `spikes` / `neuron` / `cell` all
   become `cell`, which is not a lossless round trip. That is a modelling question for
   [element types have no default].

Runner-up: the dilution unit (fraction as is, or fold dilution as 1/x), and whether
`source_unit` should stay empty.

## 5. Found in passing (not asked; recorded, not acted on)

- **`overlap` passes the registry by a name match only.** The spike extractor's `overlap` ("Overlap
  allowed", seconds of chunk overlap, `spikeextractor.m:262`) is staged as "overlap", which matches
  the registered `Overlap` NCIT:C54669, "The phenomenon of coinciding partially or wholly"
  (decided 2026-10-20 for the Haley import). The node's meaning is not the parameter's, so the
  gate passes it silently. A sibling of #10, "processing segment overlap", would fit.
- `probe_geometry.m` writes `probe model` with `ValueKind 'term'`, and `element.m` writes the NDI
  class as a term value. Both should be text (sections 1 and 3).

## 6. In the measured list, not covered here (21 distinct)

CC-BY-4.0 (`spdx:CC-BY-4.0`, a name-spelling mismatch: registered as "Creative Commons Attribution
4.0 International"), haloperidol `chebi:28001`, primary visual cortex / V1 `uberon:0002436`,
embryonic tissue `uberon:0000922`, transplantation, AAV-ChR2 `addgene:26973`, image axes c, t, x, y,
z, image intensity, `EDAM:3382` (no name), contrast, direction, spatial frequency, temporal
frequency, electrode offset voltage, temperature, tiff (registered as EDAM:format_3591; the writer
must give the node). Several have obvious candidates already in the registry (e.g. Imaging Signal
Intensity NCIT:C221750; staged "cycles per degree"), but none was researched for this batch.

## Count of new EMPTY ids this proposal would need

17 for the measured items (#1-#17 minus the shared acquisition time = 17 distinct), plus 1 for
the unmeasured depth axis (#8a): **18**, EMPTY:0000406-0000423 if minted in this order. Fewer if
InterLex has single / multi-unit (-2), if `afo` is registered for cluster identifier (-1), or if
the team keeps a physiology term for the refractory period (-1). New registry rows with existing
nodes: **6** (Numeric Value, Model Number, clustered data set, fraction, Spike sorting, curve
fitting data transformation). New CURIE prefixes: **none** (optional: `afo`). Each EMPTY term
also needs its rule-5 comment: the OLS queries listed above (2026-10-26), the decision that
adopts it, and the migrator that writes it.
