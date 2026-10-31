# One-reading review of the generic migration's inference points

This is research only. No repository was written, committed or checked out. Every verdict is **Proposed (not decided)**.

The rule under test is "Decided by Jess Haley, 2026-10-26 [one correct reading]" (did-schema `docs/plans/did_v2_go_forward_class_audit.md`, at `e5b8b6e`). It reads together with [carry register], [lossless means round trip] and [dataset-specific logic leaves the generic migration], all dated 2026-10-26.

## 0. Heads and denominators

**Code read (working trees, unchanged):**
- DID-matlab `scratchpad/lossless/DID-matlab`: `e1e3aee`, branch `claude/lossless-generic`.
- NDI-matlab `scratchpad/lossless/NDI-matlab`: `c8a47d0e2`, branch `claude/lossless-generic`.
- Both are the same heads as `dsaudit/DATASET_SPECIFIC_AUDIT.md`. Neither is the merged `V2` head.

**v1 writers:** NDI-matlab locked `main` `3cb19a85f` (`dropcensus/wt/ndi_main`).

**Files in scope:**

| repo | `.m` files | lines |
|---|---|---|
| DID `src/did/+did2/+convert/**` | 220 | 44,456 |
| NDI `src/ndi/+ndi/+migrate/**` | 38 | 19,670 |

**Grepped:** all 258 files, code only (`tools/codeonly.py` strips comments), for `contains|startsWith|endsWith|regexp|strfind|strncmpi|ismember|strcmpi(`. That found 118 DID hit lines in 41 files and 58 NDI hit lines in 15 files. Every hit was read in context. The output is `onereading/did_match.txt` and `onereading/ndi_match.txt`.

**Read in full (code part), 9 DID files:**
- `+migrators_j/treatment.m` (266 lines) and `treatment_drug.m` (119)
- `private/`: `jTreatmentRoute.m`, `jQuantityLeaf.m`, `jMeasurementFold.m`, `jResponseVariable.m`, `jRecordingModality.m`, `jTreatmentAnchor.m`, `jSessionAnchor.m`

**Read in part (ranges cited in the tables).**
- DID: `ontology_table_row.m` (30-164, 590-875), `jDoseValue`, `jTreatmentBodies`, `measurement`, `subjectmeasurement`, `element`, `resolveEpochProbemap` (2165-2240), `image_stack` (185-330), `jQuantity`, `jSourceUnit`, `entityDoc`, `stimulus_response_scalar`, `foldGenericFiles` (1431-1446).
- NDI: `pathSPromotion` (1-80, 140-240), `recordingAttribution`, `bodyResolver` (560-605), `stimulusBathToBath`, `stimulusPresentationToItem` (200-330, 579-608, 844-905, 982-1044), `local.m` (800-830, 2160-2180).

**Grep only:** the remaining roughly 225 files. No finding there means **not measured**, not "one reading".

**Reused, not re-read:** the earlier audits' rows, cited by their IDs:
- `audit_DID.md` B/C rows
- `audit_NDI.md` B/C rows
- `dsaudit` D1-D13 and N1-N8
- `DROP_CENSUS.md`

**v1 writers read (NDI `main`):**
- `+ndi/+app/+stimulus/decoder.m:125-140`
- `+ndi/app.m:85-111`
- `+ndi/+app/+stimulus/tuning_response.m:600-662`
- `+setup/+conv/+babu/TreatmentCreator.m:123-129`
- the templates and schemas for `electrode_offset_voltage` and `treatment_transfer`

**Corpora:** the four held zips, read by script with `python3 -I`: 20211116 (1,220 docs), Dab (27,561), JH (78,688), Soph (101,427). Unreadable files were skipped, not counted. The scripts are in `onereading/scripts/` (`vals.py`, `otrsim.py`). B, PRED, Babu, Hunsberger and Birren are **not held**: 0 there means not measured.

**Nothing was executed in MATLAB.** `otrsim.py` re-implements the keyword table of `ontology_table_row.m:607-719` in Python. Its output is a simulation of what that code would choose, not a run.

**Decision tags** were grepped in `schemas/*.md`, excluding STATUS and the ledger. "None found" means that grep returned 0 lines.

## 1. Inference points

**(b) Readings.** "1" means the v1 document by itself admits one correct V2 reading. ">1" gives a counter-example a lab could write; where the example is real, the corpus count is given.

**Verdict:**
- **K** = KEEP
- **NM** = NEEDS_MAPPING (carry as v1 with a register row; the row names the V2 homes and what decides between them)
- **U** = UNCLEAR

### 1a. DID pass 1: class-wide choices

| # | where | (a) chooses / from | (b) readings | (c) decision | (d) |
|---|---|---|---|---|---|
| I1 | `ontology_table_row.m:migrateRow` 607-651 | Per column: skip it (identity words), make it an **assertion** (species/sex/strain/genotype/taxon, dob, any date-like string), or else an **observation**. Every column is about the row's subject. | >1. **In corpus (simulated):** <br>• Dab EPM column "treatment: CNO or saline administration" = 'Saline' becomes a term **observation**, but it is a manipulation. <br>• "experiment trial execution timestamp" becomes a date **assertion** about the rat, but it is the trial's time. <br>• "trial type identifier" ('Startle 95 dB Trial') and "data exclusion flag" become observations of the rat. | None for the fallback. [subject local identifier is an identifier] (2026-10-25): "which entity each column is about is not generic". [table rows into the dataset audit] (2026-10-26) asks for this audit. | **NM**. Homes: assertion / observation / manipulation / condition / time anchor, per column. Decided by the table's column map. |
| I2 | same, `dispatchNumeric` 654-719. `jQuantity.m:19-22` does not refuse a unit whose kind differs from the chosen kind. | Value kind from label words; default `intensity`. | >1. **In corpus (simulated):** <br>• Dab "open arm total - percent time during test duration" 39.97 becomes **time**. <br>• "apparatus chamber identifier" 6 becomes **count**. <br>• "experimental group code" becomes **intensity**. <br>• "time to maximum amplitude" 72 becomes time with no unit. | None found (`dispatchNumeric`, D8/D10). | **NM**. Same homes as I1. Decided by the column's own term and unit, in the dataset map. |
| I3 | `measurement.m:87-97` gives `jMeasurementFold` → `jQuantityLeaf.m` with `wordBoundary=false` | Mass / temperature / length / time from substrings of node + label. No unit (`jQuantity(leaf, v, '')`). | >1. 'age' matches "voltage", "average", "dosage", "percentage", "image". "average speed" becomes time. | TEAM-SIGN-OFF [subject measurement] (2026-08-06) covers routing only. None for the table. | **NM**. 0 in held corpora; writers are Babu and Hunsberger. |
| I3b | `subjectmeasurement.m:158` (same fold, `wordBoundary=true`) | Same table on the free-text `measurement` name. | >1, but rarer: "weight change (%)" becomes mass. | Same | **U**. Lean NM for any value whose unit is not stated. |
| I4 | `treatment.m:87-91` | A CURIE-shaped `string_value` is taken as an **Anatomic Site** observation (then promoted by NDI `pathSPromotion`). | >1. A "food restriction" row whose `string_value` is `NCBITaxon:562` (the food) would become a site. | Only the Dab "target location" idiom was ever meant. Those rows are now carried (`treatment.m:79-84`). | **NM**. 0 in held corpora. |
| I5 | `treatment.m:128-131`, `makeTemperatureManipulation` 198-206 | Words cool/cold/heat/warm/thermal/temperature make a **temperature** manipulation. `numeric_value` is written as °C. | >1. In "cold-water swim training" with 10 (minutes), or "heat lamp" with 2 (hours), the number is not a temperature. v1 `treatment` has no unit field. | None for the word list (audit_DID C4). | **NM**. 0 in held corpora. |
| I6 | `treatment.m:132-143`, then `jTreatmentBodies.m:121-124` | Substance words (inject, virus, drug, vehicle, bath, chebi:) make a **dose**, or an immersion when the location is the bath. | >1. A label "bath application of TTX" with no location field hits the `bath` **word**, but the route reads only the location, so it becomes a **dose** with route `unknown`. | [treatment routes by location] (2026-10-21) | **NM** whenever the route is `unknown`. Homes: immersion or dose. Decided by the location. |
| I7 | `treatment.m:144-151` (about 30 procedure words) | A **term manipulation** valued by its own variable. A date-like `string_value` goes to `notes`. | >1. **In corpus:** <br>• "Natural left/right eye opening" (Soph 39, 20211116 2) is not an act of the experimenter: it reads as an observation of development. <br>• JH "food restriction onset time" / "offset time" (56) carry the date as notes, anchored "during the session". Each onset/offset pair is one restriction interval. | None for the list (audit_DID C4) | **NM**. Homes: manipulation (with interval) or observation. Decided by the term's meaning, in the dataset map. Total 122 docs held. |
| I8 | `treatment.m:termNumberKind` 218-245 | EMPTY:0000199 → its number is time in hours. | Writer-specific (vhlab). | [termNumberKind is per-dataset] (2026-10-25): move it out. **Still in the code.** | **NM** (decided; build not done) |
| I9 | `jTreatmentRoute.m:64-82` | No location → `unknown` → dose with NaN. Any non-bath, non-medium location → dose. | Bath → immersion: 1 reading. Body site → dose: 1 reading. **No location:** >1 (a drug in culture medium, Birren-style, is an immersion; an injection is a dose). **"drinking water", "culture medium":** >1. | [treatment routes by location], [immersion or dose] (2026-10-21) | **K** for bath and body site. **NM** for none or a non-anatomical location. |
| I10 | `jTreatmentRoute.m:isMedium` 85-96 | Babu agar plate medium / ambient air → `exposure` | >1 | [babu-media] (2026-10-21). The [one correct reading] text uses it as its own example ("Babu: MICRO:0000480 -> exposure"). | **NM** (Babu map) |
| I11 | `treatment_drug.m:isHeatOnly/makeHeat` 81-119 | An all-"heat" mixture → temperature manipulation | Babu-specific | [babu-media] | **NM** (Babu map) |
| I12 | Primary chemical as `variable`: `treatment_drug.m:44`; `resolveDeferredBaths.m:426, 528-531`; NDI `stimulusBathToBath.m:259, 456-461` | The statement's variable is mixture row 1. | >1. **In corpus:** <br>• Dab 1,041 ACSF baths → variable "sodium chloride". <br>• 131 more baths are ACSF + the antagonist d(CH2)5: still "sodium chloride", though the antagonist is what changed. | [bath is a manipulation] (2026-10-21) is silent on this. None found for "primary/first chemical". | **NM**, or a team rule that one fixed generic variable holds for every bath |
| I13 | `jDoseValue.m` amount vs concentration (`amountSlot`) | A dose slot or the ingredient's concentration, by the unit's dimension | 1 (the unit's dimension decides) | [dose per ingredient], [unknown-amount-slot] | **K** |
| I14 | `jDoseValue.m:isVehicle` 260-275 | saline/vehicle per body mass → placeholder | — | [dose per ingredient] | **K**: it now carries as v1 (`jTreatmentBodies.m:101-109`) |
| I15 | `element.m:elementEntityType` 222-234 | `entity.type`: spikes/neuron/cell → cell; ensemble → group; **otherwise → device** | >1. **In corpus:** JH `position` / `distance` elements (4,156, not direct) are worm-track signals, not devices. A `spikes` element can be multi-unit (not one cell). | Code: "PROPOSED, unsigned". None found. | **NM** for non-direct elements outside the table. **U** for spikes (1,709 held). |
| I16 | `jRecordingModality.m:186-269` (and its twin `resolveEpochProbemap.m:localModality`) | Modality from NDI's probe-type vocabulary (exact match) | 1 for n-trode, patch-Vm, patch-I, imaging, ecg/eeg. **>1** for `patch` / `sharp`: both voltage and current are written, though a recording holds one. `event` → stimulator (a lick or TTL "event" probe is not a stimulator). | TEAM-SIGN-OFF [raw recording observation] (2026-08-10) | **K** for exact types (Dab patch-Vm 202, patch-I 202; n-trode 205). **U** for `patch`, `sharp`, `event` (0 held). |
| I17 | `resolveEpochProbemap.m:derivedSeriesKind` 2167-2229 | `position`: video tracking, 10 s gap. `distance`: bacterial patch. | Haley-only | [JH position and distance] (2026-10-22), now under [dataset-specific logic leaves …] | **NM** (Haley map; dsaudit D6). `spikes` row: **K**. |
| I18 | `jResponseVariable.m:63-75` | **Variable** from unit spelling: Hz → "neural firing rate"; df/f → dF/F | >1 for Hz: a tuning curve of a non-spike response in Hz (lick rate, LFP peak frequency). The unit is notation; the variable is not. | [response variable], [dF/F as variable] (2026-10-22); [spelling is notation] (2026-10-26) | **U**. K if the build requires the response's element to be `spikes`, else NM. Held: all 34,690 `response_units` are `[]` (Soph 34,606, 20211116 84), so this branch is never hit. |
| I19 | `image_stack.m:197-317` | Mask/map by label words. Region by Haley words. Otherwise an **observation** of "image intensity". | >1. A "segmentation" or "label image" without the words "mask" / "label map" becomes intensity. A derived image (a projection) becomes an observation. | [migrated masks are logical] (2026-10-22) decides the shape, not the detection | **NM** (mask/map detection; Haley words, dsaudit D5). **U** for the non-mask default. JH 7,007 all carried today (`document_id`, 191-197). |
| I20 | `ontology_image.m:340-350` | uberon → Anatomic Site; else an "ontology node" condition | >1 for non-uberon | [ontology image is an observation of its region] (2026-10-21). [non-area image node, revisited] (2026-10-22) is **reopened, NOT decided**. | **K** for uberon. **NM** for non-area (0 held). |
| I21 | `lightsheet_zarr_pyramid.m` (method SPIM, variable Fluorescence Intensity); `foldGenericFiles.m:isNgffSource` 1431-1446 | A non-NGFF dtype → TIFF folder | 1 while the writers are only NDI's `makePyramid` / `fromSPIM`. The class name says light sheet. | [no-source pyramid gets a file-less store body] (2026-10-25) states the dtype rule | **K** (writer-grounded). **U** if a third writer appears. |
| I22 | `jTreatmentAnchor.m:transferAnchor` 39-57 | Empty `clocktype` → `dev_local_time`. `timestamp` always in **seconds**. | >1 and partly wrong. The NDI schema says the timestamp is "a datenum (if global clock) or in seconds (if local clock)", so a global clock means days. With no clocktype, the clock is unstated. | [transfer onset] (2026-10-21; the Babu writer sets `dev_local_time`) | **NM** for empty or global clocktype (0 held) |
| I23 | `electrode_offset_voltage.m` | `offset` in V | 1. The NDI schema says "measured in volts (V)". Note: `temperature` is "in degrees C" by the same schema, yet it is written with no unit. | none needed | **K** |
| I24 | `jSourceUnit.m` (e.g. 'C' → °C) + `jQuantity.m:19-22` | Unit spelling → term | 1 per spelling in context. But a kind mismatch is silently kept (I2). | [spelling is notation] | **K**. Add a refusal when the unit's kind differs from the value kind. |
| I25 | `stimulus_response_scalar.m:248-261`; `resolveResponseParameters` (empty normalization → 0) | Harmonic from `response_type`; empty → 0 | 1. Writer doc: "[] or 0) No normalization". | TEAM-SIGN-OFF [stimulus response] | **K** |
| I26 | Dataset maps already listed: `resolveLawnPlateSubjects`, encounter map, patch-geometry map (`ontology_table_row.m:67-109`), sliceTetanus, imagedEntitySubjects plate join, epochSeriesBodies JH split | — | — | [Haley logic leaves …], [sliceTetanus to Dab map], [dataset-specific logic leaves …] | **NM** (dsaudit D1-D3, N1, N3, N4) |

### 1b. NDI second pass

| # | where | (a) chooses / from | (b) readings | (c) decision | (d) |
|---|---|---|---|---|---|
| N1 | `ontologyRowSubjects.m:resolveRowSubject` (route 3: `SubjectLocalIdentifier` label match), then the DID refold | The row's subject, then I1/I2 for every column | Subject: 1 (an identifier, exact, unique in the session). Columns: >1 (I1, I2). | [subject local identifier is an identifier] (2026-10-25) | **K** for the subject join. **NM** for the columns. Dab 6,205 rows rely only on route 3 (dsaudit §3); whether each resolves is not measured. |
| N2 | `ontologyLabelSubjects.m:155, 294-308` | Every `ontology_label` → a term **observation** (variable "label") of the target's subject | >1. Jess, 2026-10-22: "Ontology label was meant to add conditions or other qualifiers". | Code cites migration_plan D.2. No decision line found. | **NM**. Homes: observation or condition on the target. JH `ontologyLabel` 7,007; their targets are carried today, so not reached (not measured). |
| N3 | `pathSPromotion.m` 'sites', 156-225 | A co-anchored site + manipulation (one source document: anchors are minted per document, `jSessionAnchor.m`) → a region part | 1 when the site came from an explicit location field (`treatment_drug` / `virus_injection` location). Inherits I4 when it came from a CURIE `string_value`. | [region parts] (2026-10-21), [site scaffolding not a loss] (2026-10-26) | **K** (location fields); **NM** via I4 |
| N4 | `pathSPromotion.m:lateralityTable`, `isAnatomical` (uberon) | Side vs area, from term nodes | 1 | [laterality on the part] | **K** |
| N5 | `recordingAttribution.m:205-237` | Specimen (and an EMPTY variable) from the probe's donor observation; conflicting donors are refused (175-176) | 1 | [preview attribution without epoch files]; TEAM-SIGN-OFF [raw recording observation] | **K** |
| N6 | `bodyResolver.m:epochClockOfElement` 562-601 | Clock for a bath's epoch anchor. Prefers `dev_local_time`; **defaults to `dev_local_time`** when no clock is recorded. | >1 when nothing is recorded | None found. It conflicts with [no invented values] (2026-10-25). | **NM** (or `malformed`) for the default arm. Not measured on Dab's 1,605 baths. |
| N7 | `stimulusPresentationToItem.m:238-296` | Who received the stimulus: a response, then the epoch's elements, then the stimulator. More than 1 animal → a session cohort, distributive. | 1 via the response route. >1 via the epoch route with several animals (two animals recorded, one viewing). | Jess Haley 2026-10-21 ("a"); [presentation with no subject] | **K** for response / stimulator. **NM** for an epoch-route cohort. |
| N8 | `itemManipulation` 579-608 | Method "visual stimulation", variable "visual stimulus" for **every** presentation, including kind `unrecognised` (`unplacedPresentationFields` 1023-1025 does not refuse it) | 1 for the five NewStim classes, recognised by their exact required-field sets (all 1,428 held). >1 for `unrecognised` (any `ndi.app.stimulus.decoder` input). | [NewStim recipes are a default] (2026-10-25): "offered by the decision workbook" | **K** for recognised NewStim. **NM** for unrecognised. |
| N9 | `stimulusRecipe.m` interpretations: flashed bar if the short side is ≤50 px; `random==1` → sparse noise; `pixSize<1` read as a fraction; `bgpause` in s if `fps<0` | Stimulus terms | Defaults, by their own decision | [flashed bar] etc.; [NewStim recipes are a default] = bin C, a **workbook default** | **U**. Is a confirmed per-software default "one reading"? |
| N10 | `epochAnchorFold` `approx_*` → 5 s tolerance | Tolerance | 1. NDI `+time/clocktype.m` defines "within 5 s". | TEAM-SIGN-OFF [time_reference] | **K** |
| N11 | `stimulusBathToBath.m:306-315` / `resolveDeferredBaths.m:447-452` | Rows named pH / osm → formulation properties | 1. Note: osmolarity vs osmolality is told apart only by the unit. | None for the row rule | **K** |
| N12 | `softwareDedup`, `strainAssembly`, `subjectStrainAssembly`, `etaShape:curie` | Identity by (name, version); openMINDS typed fields | 1 | [software dedup after pass one], [WBStrain prefix is generic] | **K** |

## 2. Re-check of the 2026-10-25/26 decisions that place values generically

| decision | passes? | reasons |
|---|---|---|
| [neuron derived from its sorting run] (10-25) | **PASS** | The edge's own name, `jrclust_clusters_id`, names the run. `prov:wasDerivedFrom` is its one reading. |
| [session membership records linked or ingested] (10-25) | **PASS** | `is_linked` is a boolean that NDI sets in `add_ingested_session` / `add_linked_session`. The opener class and its arguments are copied verbatim. Restated inputs are dropped only when equal. |
| [dataset form terms] (10-25) | **PASS** | A closed openMINDS list. A value outside it carries the form as v1. |
| [presentation app is software] (10-26) | **FAIL (wrong reading)** | **Positive evidence.** <br>• NDI `main` `decoder.m:135-137` builds each `stimulus_presentation` as `E.newdocument(...) + ndi_app_stimulus_decoder_obj.newdocument()`. <br>• `app.m:94-111` stamps the decoding machine's `computer` and MATLAB version. <br>• All 1,428 held presentations say `ndi_app_stimulus_decoder`, `MACA64`, MATLAB 23.2 / 24.2. <br>So `app` is the software that DECODED and WROTE the record, not the software that presented the stimulus. As the manipulation's `software_id` it states the latter. This is the same reasoning as [small unread settings] (1): "where the settings were SAVED". |
| [run environment on interactions] (10-26) | **FAIL** | Same evidence. The text "the machine the stimulus program ran on" is contradicted by the writer. Moving the two edges to `interaction` may still be right for other sources; this source does not support it. |
| [control selection on the presentation method] (10-26) | **FAIL (wrong reading)** | NDI `tuning_response.m:600-661` (`ndi_app_tuning_response`) computes `control_stimulus_ids` after the fact. Its method ("pseudorandom", `isblank`=1, the `findclosest` pairing) is an ANALYSIS rule. As the presentation **manipulation's** method it says the experimenter presented the controls that way. One reading exists: a calculation, or the covariate's provenance. |
| [image file details placed] (10-26) | **PASS** | `format` and `compression` map field to field. `imageCollection_id` → `member_of` a group (T20). `data_limits` is written only when it differs, as a neutral "value range", which covers both a display range and a data range. |
| [spelling is notation] (10-26) | **PASS for units; U for I18** | Spelling → unit term is notation. Spelling → **variable** (`jResponseVariable`) is an inference (I18). It is moot in the held corpora (all `response_units` empty). |
| [device clocks on one epoch] (10-26) | **PASS, with its stated build check** | (1) relies on NDI navigators sharing an id only for one recording folder. (2) needs each epoch tied to exactly one acquisition system. Where the device-string parse ("vhvis_spike2:mk1") is not unique, it must carry, not guess. (4) already carries a disagreement. |
| [site scaffolding not a loss] (10-26) | **PASS** where the site came from a declared location field; **FAIL via I4** | The scaffolding is minted from one v1 document, and the part keeps the term. But a site taken from a CURIE-shaped `string_value` (`treatment.m:87-91`) is a guess. 0 held. |
| [restated values checked], [hartley leftovers checked], [writer default is not set], [probe contact geometry carried], [small unread settings], [compression block and empty levels], [clock terms get nodes] (10-26) | **PASS** | Each is equality-guarded, writer-cited, a direct field-to-field placement, or a carry. |
| [no-source pyramid gets a file-less store body] (10-25) | **PASS (U if a new writer)** | dtype → format holds for NDI's two writers only (I21). |
| [NewStim recipes are a default] (10-25) | **Conflict with the code** | The decision says the recipes are a workbook default (bin C). The code applies them inside the generic second pass (N8, N9). |
| [termNumberKind is per-dataset] (10-25) | **Not built** | Still at `treatment.m:218-245` (I8). |
| [babu-media] (10-21) | **FAIL** | It is [one correct reading]'s own example (I10, I11). |

## 3. Questions for the team (plain language, most impactful first)

1. **Dabrowska `ontologyTableRow` (6,205 rows: 6,160 fear-potentiated startle, 45 elevated plus maze).** Today each column's role and kind is guessed from words in its label. For example:
   - "CNO or saline administration" becomes an observation;
   - "percent time" becomes a time;
   - "chamber identifier" becomes a count.

   Carry these rows as v1 (`needs_mapping`), with the Dab map naming each column's entity, direction, kind and unit?
2. **Who "used" the software on a `stimulus_presentation` (1,428 documents) and a `control_stimulus_ids`?** Both `app` blocks are NDI's own decoder and tuning-response apps, run on the analysis Mac. They are not the stimulus program. Should [presentation app is software], [run environment on interactions] and [control selection on the presentation method] be re-decided, so these record the document's provenance (a calculation) rather than the manipulation's software and method?
3. **Bath variable (`stimulus_bath`, 1,605 in Dab; also `treatment_drug`).** The statement's variable is the first mixture row, so 1,172 ACSF baths say "sodium chloride", including the 131 with an antagonist. Should there be one fixed generic variable for every bath, or should each be carried with the manipulated ingredient named by the dataset map?
4. **`treatment` label-word routing (122 held: Soph 64, JH 56, 20211116 2).** Should these carry as v1 with a `needs_mapping` row?
   - "Natural eye opening" becomes a manipulation.
   - JH "food restriction onset/offset time" becomes a manipulation with the date in its notes, rather than one timed restriction.
   - Temperature words make the number a temperature in °C.
5. **Element entity type (JH 4,156 `position` / `distance` elements become devices; 1,709 `spikes` elements become cells).** Keep "device" only for direct (acquisition) elements, and carry derived elements of other types?
6. **Treatments with no recorded location, or a non-body location (Babu, Birren, Hunsberger writers; 0 held).** Should these carry as v1 rather than become a dose with a NaN amount? The Babu agar, air and heat rows go to the Babu map, as [one correct reading] itself says.
7. **Unstated clocks.** These cases default to `dev_local_time`:
   - a `treatment_transfer` with no `clocktype`;
   - a bath epoch with no clock record.

   A global-clock transfer is also written in seconds, though NDI stores days. Carry these instead?
8. **Image and label meaning (JH 7,007 `imageStack` and 7,007 `ontologyLabel`, all carried today).** Should these carry as `needs_mapping` once their table-row edge is placed?
   - mask or map detected by words in the label;
   - a non-mask image always read as an observed intensity;
   - every `ontology_label` read as an observation, when Jess said labels add "conditions or other qualifiers".

## 4. Not verified

- No MATLAB was run. I1/I2's corpus outcomes come from a Python re-implementation of the keyword table (`scripts/otrsim.py`). Whether the NDI refold actually reaches each Dab row (route 3 resolving) is not measured.
- NDI second-pass frequencies (N3, N6, N7) are not measured.
- B, PRED, Babu, Hunsberger and Birren are not held.
- The about 225 grep-only files may hold inference points the string-match grep could not see (for example, a `switch` on a value). Not measured.
