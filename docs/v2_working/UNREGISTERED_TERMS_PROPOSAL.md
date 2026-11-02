# Unregistered terms the migration writes: proposal (2026-11-02, agent R)

**Everything below is Proposed (not decided).** It is for Jess Haley and Steve Van Hooser to decide.
No registry row, EMPTY term, schema file or plan document was written. Where a line says
"decided", it quotes a `Decided by` line already on did-schema `main` and says so.

## Denominators (first)

| what | count | source |
|---|---|---|
| input list | 4 corpora (20211116, B, Dab, JH); **89** rows; **74** distinct (term, field) pairs; **50** distinct term names | `scratchpad/Q_unregistered_corpus_41350143989.txt` (DID-matlab Test code run 41350143989); counted with `grep -E '^ +[0-9]+ +"'` (89), `... \| sort -u` (74), distinct names (50) |
| rows per corpus | 20211116: 65; B: 8; Dab: 16; JH: 0 | same file, its `--- UNREGISTERED TERMS (...)` headers |
| term registry read | **948** terms | did-schema `origin/main` 775f4b9, `schemas/registry/did_v2_term_registry.json` |
| registry check | each of the 50 names matched against registry names, case-insensitive (as `jLabel` / `did2.convert.registeredTerm` match): **0 exact matches** | script output in this session |
| EMPTY ids in empty-ontology `V2` | up to EMPTY:0000430; next free **0000431** | empty-ontology `origin/V2` 6511b77, `grep -o 'EMPTY_0000[0-9]*' src/ontology/empty-edit.owl \| sort -u \| tail` |
| OLS4 searches | 121 (`ebi.ac.uk/ols4/api/search`, 8 rows each; query lists `R-ols/q1.txt`, `q2.txt`, `q3.txt`) | `scratchpad/R-ols/q1.out`, `q2.out`, `q3.out` (+ 2 ontology-restricted `om` searches) |
| CURIE prefixes used here, all registered | snomedct, RRID, AFO, EDAM, PATO, IAO, OBI, BAO, NCIT (checked in `schemas/registry/CURIE_lookups_meta.json`) | this session |
| not searched | InterLex (needs an API key, as `docs/v2_working/EMPTY_TERMS_PROPOSAL.md` found), Wikidata, MGI/JAX | - |
| existing draft reused | `docs/v2_working/EMPTY_TERMS_PROPOSAL.md` (did-schema `main`): its rows for spike sort quality (#3 "unit isolation quality"), element type, ndi element class, ndi.probe.timeseries and spike cluster assignment are reused below | - |

## Summary (50 names)

| group | names | what the proposal says |
|---|---|---|
| A. already decided: not a term, the assertion stops when its build lands | 7 | element type, ndi element class, ndi.neuron, ndi.probe.timeseries.mfdaq, ndi.probe.timeseries.stimulator, patch-I, patch-Vm |
| B. a registered term already has the meaning; the migrator writes a name the registry does not hold | 5 | stimulus response, spike cluster assignment, strain, spiketrain dt, axis_1 / axis_2 (counted as 2) |
| C. existing ontology term, needs a registry row | 15 | voltage, current, stimulus, Orientation / orientation (2), lag, T, receptive field, sync file name, independent parameter, independent label, best algorithm, selection, X sample, Y sample |
| D. needs an EMPTY term | 8 | spike sort quality, mean spike waveform, double gaussian, represented quantity, response estimate, significance, minimum matching file paths, isspike |
| E. not a term (a value, a structure or data) | 12 | depends on.name, temporalfreqfunc, prestimulus normalization, orientation selection, spatial frequency selection, temporal frequency selection, stimulus sequence.frame times, stimulus sequence.hartley numbers.KXV / .KYV / .ORDER / .S (4) |
| F. strain values: wait on the Dab map | 3 | AVP-Cre, OTR-IRES-Cre, CRF-Cre |
| **total** | **50** | 7 + 5 + 15 + 8 + 12 + 3 |

If all of it were accepted: **8** new EMPTY terms (EMPTY:0000431-0000438), **15** new registry rows
with existing nodes, and migrator changes for groups B and E (DID-matlab). No new CURIE prefix.

---

## A. Already decided: not a term (7 names, all build pending)

| name (field, corpora) | the decision on `main` | what is left |
|---|---|---|
| element type (statement.variable; Dab 404) | Decided by Jess Haley, 2026-10-27 [element type is a device kind term]: the "element type" assertion is replaced by a device-kind term assertion; "a type with no decided term keeps today's assertion". | Build pending: NDI-matlab reads the kind first, then DID-matlab stops writing it. |
| patch-I, patch-Vm (term.value; Dab 202 each) | Decided by Jess Haley, 2026-11-01 [recording mode terms]: `-Vm` is OBI:0002185 "current clamp assay", `-I` is OBI:0002182 "voltage clamp assay", on the recording observation's `method.term`. | Built in DID-matlab #350 on the observation; the `element type` assertion that still holds these words stops with the build above. |
| ndi element class (statement.variable; 20211116 23, B 156, Dab 762) | Decided by Jess Haley, 2026-10-27 [ndi element class not kept]: the assertion is not written. | Build pending: NDI-matlab first, then DID-matlab `+migrators_j/element.m`. |
| ndi.neuron, ndi.probe.timeseries.mfdaq, ndi.probe.timeseries.stimulator (term.value) | Same decision: these are the values of that assertion. The existing draft's section 3 already called NDI class names "a code, not a concept". | Disappear with the assertion. |

## B. A registered term already has the meaning (5 names)

The fix is in the migrator (write the registered term), not in the registry.

| name (field; rows) | registered term | registry definition | why it fits |
|---|---|---|---|
| stimulus response (statement.variable; 20211116 273) | **EMPTY:0000398 neural response** | "The activity of a neuron or population of neurons measured in response to a stimulus." | `stimulus_response_scalar.m` writes it for a neuron's response to each stimulus. Exactly this meaning. |
| spike cluster assignment (statement.variable; 20211116 1) | **OBI:0000648 clustered data set** | "A data set that is produced as the output of a class discovery data transformation and consists of a data set with assigned discovered class labels." | The registry row's own `first_used_in` is "DID-matlab spike sorting outputs: spike cluster assignment", so the row exists for this use; `jSorterOutput.m:125` and `jrclust_clusters.m:146` still write the label. |
| strain (statement.variable; Dab 115) | **NCIT:C14419 Organism Strain** | "A population or type of organisms that is genetically different from others of the same species and possessing a set of defined characteristics." | `openminds_subject.m` `variableForType` writes the bare name `strain`. Alternative: add `strain` as a synonym of the row so the name resolves. |
| spiketrain dt (method.parameters[].variable; 20211116 546) | **EMPTY:0000308 bin width** | "A setting of a data transformation that groups values by a variable: the width of each group along that variable." | NDI `tuning_response.m:176` sets `spiketrain_dt` 0.001 s: the step at which spike times are binned into a train (did-schema `did_v2_stimulus_response_model_plan.md`, "Do the parameters get duplicated?"). |
| axis_1, axis_2 (data.dimensions[].term; 20211116 840 each) | **NCIT:C44477 X-Coordinate**, **NCIT:C44478 Y-Coordinate** | "A horizontal coordinate ..." / "A vertical coordinate ..." | `jNgridBody.m:483` invents `axis_<k>` when a v1 ngrid names no label. In these 840 the ngrid is the hartley reconstruction, whose dimensions are the stimulus grid columns and rows and the lag (NDIcalc-vis-matlab `hartley.docs.output.txt`: `data_dim` "[numel(X_coords) numel(X_coords) TMAX 2]"). `hartley_calc.m:488` supplies only `{'lag', '', ''}`. Which axis is first must be checked against `hartley.m` before the migrator names them. |

## C. Existing ontology term, needs a registry row (15 names)

| name (field; rows) | proposal | node | the ontology's definition | why / alternatives |
|---|---|---|---|---|
| voltage (statement.variable; B 1242, Dab 2846) | **voltage** | AFO:AFR_0001916 | "Voltage is a quality quantification facet which quantifies the difference in electric potential energy between two points per unit electric charge." | The recording observation's variable for electrodes (`resolveEpochProbemap.m:1892`, `:1925`). `afo` is a registered prefix ([afo prefix registered]). Alt: NCIT:C70813 Voltage ("The rate at which energy is drawn from a source ...", a worse definition); NCIT:C82324 Membrane Potential is narrower (not true of an extracellular electrode). |
| current (statement.variable; Dab 1604) | **Electrical Current** | NCIT:C48434 | "The movement of electrical charges in a conductor." | `resolveEpochProbemap.m:1927` (patch-I, sharp-I). Alt: OM:ElectricCurrent (no definition in OLS); AFO:AFR_0001856 electric current ("quantifies the ability to conduct an electrical charge", not the flow). Choosing AFO for voltage and NCIT for current mixes sources; the team may prefer one source for both. |
| stimulus (data.dimensions[].term, data.covariates[].variable; 20211116 546 each) | **Stimulus** | NCIT:C41210 | "An environmental event, agent, act, or influence that can be detected by a receptor in the body and will invariably produce a reaction in a living organism." | `stimulus_response_scalar.m:248-249`: one position per stimulus id. Alt: MI:2260 stimulus (MI prefix not registered). |
| Orientation, orientation (dimensions/covariates 84 each; statement.conditions 84) | **Orientation** | NCIT:C165680 | "The position or alignment of something relative to points of the compass, other specific directions, or some other indexing system." | One row serves both spellings (matching ignores case). The capitalised one is v1's `independent_label` text "Orientation"; the other is `tuningNames.m:84` (`angle` -> `orientation`). Not NCIT:C77821 (a person's awareness). |
| lag (data.dimensions[].term, data.covariates[].variable; 20211116 840 each) | **delay** | AFO:AFR_0001625 | "A delay is a process property that describes a difference in time between a process boundary and some other point in time." | The hartley reconstruction's time axis: "The reconstruction times relative to each event" (`hartley.docs.output.txt`, `T_coords`). No "time lag" term found (OLS: time lag, lag, latency, time delay). PATO:0001005 latency is marked "candidate for obsoletion" in OLS. |
| T (method.parameters[].variable; 20211116 210 each in two fields) | **delay** (same row as lag) | AFO:AFR_0001625 | as above | v1 `input_parameters.T` is the list of reconstruction times, the same values as the lag covariate (`hartley.m:436` `'T_coords', parameters.input_parameters.T`). Alternative: drop the parameter as redundant with the covariate; that needs the round trip to rebuild it (`+roundtrip/hartley_calc.m`). |
| X sample, Y sample (method.parameters[].variable; 20211116 210 each in two fields) | **step size** | AFO:AFR_0000950 | "The difference between two discrete points next to each other in a range of discrete values." | `hartley.m:437-438`: `1:X_sample:M`, the step between reconstructed grid columns (rows). Two parameters of one variable need something to tell them apart (a qualifier naming the axis, X-Coordinate / Y-Coordinate). If the team prefers two variables, two EMPTY terms instead. |
| receptive field (statement.variable; 20211116 210) | **Receptive field** | SNOMEDCT:68015005 | (OLS gives no definition for this SNOMED concept) | `hartley_calc.m:418`. No OBO term found (OLS: receptive field, visual receptive field). If a definition is required (registry rule: definitions on EMPTY and staged terms only), SNOMED is acceptable; otherwise an EMPTY term "receptive field" with a definition. The `snomedct` prefix is registered (existing draft, section 2 #13). |
| sync file name (method.parameters[].variable; 20211116 1, B 13, Dab 13 in two fields) | **File name** | EDAM:data_1050 | "The name (or part of a name) of a file (of any type)." | `syncrule.m:405`. The method (clock alignment, file match) carries "sync" (T19). Alt: registered NCIT:C47922 Pathname (a path, not a name). |
| independent parameter (method.parameters[].variable; 20211116 84 x2) | **Independent Variable** | NCIT:C191277 | "A variable that is not affected by other variables that the study is trying to understand. Independent variables influence dependent variables." | v1 `tuningcurve_calc.input_parameters.independent_parameter` (did-schema `did_v2_method_parameters_plan.md:275`); value is text (a stimulus parameter name). Alt: SIO:000920. |
| independent label (same; 84 x2) | **Label** | NCIT:C45561 | "A brief description given for purposes of identification; an identifying or descriptive marker that is attached to an object." | Display text for the independent variable ("Orientation"). Alternative: not a term; fold into the dimension's own term (Orientation above already holds the meaning) and let the round trip rebuild the text. |
| best algorithm (same; 84 x2) | **Algorithm** | NCIT:C16275 | "A defined procedure for solving a problem. ..." | Value `empirical_maximum` (text). The "best" goes in the document, not the term (T19). |
| selection (same; 84 x2) | **selection criterion** | OBI:0001755 | "A directive information entity which defines and states a principle of standard by which selection process may take place." | v1 `tuningcurve_calc.input_parameters.selection`. See group E for the three `<parameter> selection` names. |

## D. Needs an EMPTY term (8 names)

Labels follow empty-ontology `docs/conventions.md` (lower case; nothing the document already carries).
Ids would be EMPTY:0000431 onward, in this order.

| # | name (field; rows) | proposed label | draft definition | parent | OLS4 searches with no fit |
|---|---|---|---|---|---|
| 1 | spike sort quality (statement.variable; 20211116 42) | **unit isolation quality** (reused from the existing draft, #3) | A rating, made when a spike sorting is curated, of how well the spikes assigned to one sorted unit are separated from those of other neurons and from noise. | categorical measurement datum (OBI:0000938) | unit isolation quality, cluster quality, spike sorting quality, isolation distance, data quality (NCIT:C142491 is about information credibility) |
| 2 | mean spike waveform (statement.variable; 20211116 21) | **spike waveform** | The voltage of a recording around the time of a neuron's action potential, as a function of time from the action potential, on each channel that records it. | action potential (PATO:0001463) | mean waveform, spike waveform, average waveform, action potential waveform, extracellular action potential waveform. "mean" goes in the method (registered NCIT:C53319 Arithmetic Mean), per T19. Alternative: PATO:0001463 action potential itself as the variable (it is a membrane quality, not a recorded trace). |
| 3 | double gaussian (tuning_curve.value.model_fit[].model; 20211116 42) | **double Gaussian function** | A function of stimulus orientation made of a constant plus two Gaussians whose peaks are 180 degrees apart, with separate amplitudes and a shared width, used to describe an orientation and direction tuning curve. | curve fit model (BAO:0000625) | double gaussian, gaussian function, sum of gaussians, Gaussian curve fit, von Mises. Precedent: registered EMPTY:0000416 Naka-Rushton function. The exact formula must be read from the NDIcalc-vis-matlab fit code before minting (not read here). |
| 4 | represented quantity (data_body.conditions and statement.conditions variable; 20211116 420 each) | **represented quantity** | A qualifier of a value or data body that names which of several quantities computed together it holds. | data item (IAO:0000027) | No search fitted. Alternative: no qualifier at all, by emitting the two planes as two statements with their own variables (#5, #6); that is a modelling change in `hartley_calc.m:556-563`. |
| 5 | response estimate (condition term; 20211116 210 x2) | **spike-triggered average** | The average of the stimulus over the times preceding each of a neuron's spikes, at each delay before the spike. | data item (IAO:0000027) | spike-triggered average, spike triggered average, triggered average, event-triggered average, reverse correlation (0 relevant). NDIcalc: "The first plane ... is the spike-triggered average". |
| 6 | significance (condition term; 20211116 210 x2) | **null cumulative probability** | The value of the cumulative distribution function, under the null hypothesis that the events and the stimulus are unrelated, at an observed statistic; a two-tailed p-value is 2 min(c, 1 - c). | data item (IAO:0000027) | statistical significance, p-value, cumulative distribution function, cumulative probability. **Not** NCIT:C44185 / OBI:0000175 p-value: NDIcalc's documentation says the plane "holds the cumulative distribution function", not a p-value. |
| 7 | minimum matching file paths (method.parameters[].variable; 20211116 2, B 26, Dab 26 in two fields) | **minimum matching file count** | A setting of a file-matching rule: the least number of files two records must share for the rule to treat them as the same. | count (PATO:0000070) | number of matches, minimum number (0 relevant). v1 `syncrule` `number_fullpath_matches` (`syncrule.m:400`). |
| 8 | isspike (method.parameters[].variable; 20211116 546) | **event input** | A setting of a data transformation: whether its input is a series of event times (1) or a sampled signal (0). | data item (IAO:0000027) | No search fitted. NDI sets it from the element type (`tuning_response.m:178-182`), so it is not a fixed writer default and [writer default is not set] does not drop it. |

## E. Not a term (12 names)

| name (rows) | why | what instead (Proposed) |
|---|---|---|
| depends on.name (method.parameters; 20211116 84 x2) | v1's `depends_on` list copied into `input_parameters` and flattened by `jParameterList`: an edge name, a structure, not a concept. | Read as an input edge (the calculation's `input` edges already hold the ids), or dropped if it repeats them; either way the round trip must rebuild it. |
| temporalfreqfunc (546) | Its value is always `ndi.fun.stimulustemporalfrequency`, a function name, NDI `tuning_response.m:172` (`did_v2_stimulus_response_model_plan.md` table). | Not written when it equals that default ([writer default is not set] gives the principle for carrying; whether it also means "not written" is the question). If written, NCIT:C150832 Software Name (registered) with the text value. |
| prestimulus normalization (546) | Always `[]` from the writer (`tuning_response.m:175`): an empty value, no meaning to record. | Not written when empty. A non-empty value would need a term; registered OBI:0200169 normalization data transformation is the method, not the setting. |
| orientation selection, spatial frequency selection, temporal frequency selection (42 each x2) | `jCalculation.m:794` builds `[<parameter> ' selection']` = 'best': one meaning (a selection criterion) per stimulus parameter, with the parameter in the name. T19: the term is as general as the meaning allows. | One variable, OBI:0001755 selection criterion (group C), with the stimulus parameter named by a qualifier (Orientation, NCIT:C75389 Spatial Frequency, NCIT:C25515 Temporal Frequency, all registered or in group C). |
| stimulus sequence.frame times, stimulus sequence.hartley numbers.KXV, .KYV, .ORDER, .S (210 each x2) | These are the per-frame stimulus record (one value per stimulus frame, "kept in a binary file", NDIcalc `hartley.docs.output.txt`), not settings of the calculation. Flattened into parameter names by `jParameterList` (`hartley_calc.m:379`). | Data: a data body of the stimulus presentation (or of the calculation's input), with dimension "frame" (registered EMPTY:0000260) and variables per column. If the team keeps them as parameters, frame times would use registered EMPTY:0000368 onset time, and KXV/KYV/S/ORDER would need 4 EMPTY terms. A modelling question, not a naming one. |

## F. Strain values (3 names): wait on the Dab map

| names (term.value; Dab) | finding | proposal |
|---|---|---|
| AVP-Cre (49), OTR-IRES-Cre (56), CRF-Cre (10) | did-schema `did_v2_openminds_family_record.md:260`: "with NO identifier at all : 115 AVP-Cre, OTR-IRES-Cre, CRF-Cre — all three have background + genetic type". OLS4: no strain term (Avp Cre: 0; Crh Cre: rat lines only, RS:0004720, RS:0005319). EMPTY `V2` holds other transgenic strains (e.g. EMPTY_0000178) but none of these three. | T19 tier 2 first: if the Dabrowska lab can name the JAX/MMRRC line for each, use its RRID (the `RRID` prefix is registered). Otherwise three EMPTY strain terms, each with its background and genetic strain type as statements (the record's "pedigree" point). These are Dab questions, which Jess asked to keep for the Dab map. |

## Questions for the team (plain words)

1. Voltage and current: one source for both (all NCIT, all AFO, or OM like the registered `time`), or the best definition for each (AFO voltage, NCIT current)?
2. Should values that never change from what NDI's writer always writes (`temporalfreqfunc`, an empty `prestimulus normalization`) be left out of the V2 document, since the round trip can put them back?
3. The hartley per-frame stimulus record (frame times, kx, ky, S, order): keep it as method parameters, or move it to a data body?
4. The hartley "represented quantity" qualifier: keep one statement with two planes told apart by a qualifier, or two statements, one per plane?
5. For the three Cre lines: can the lab give the JAX/MMRRC stock numbers? (Dab question, for later.)
