# EMPTY synonym proposals, second pass (genuine alternative names)

Source: empty-ontology `claude/audit-terms-2026-10-22` at FETCH_HEAD `24d316a268e0bbf25cf141244db32e4f0470a9b9`,
`src/ontology/empty-edit.owl` (copied to `edit.owl` here; parsed by `parse.py` into `terms.json`).
Rules applied: the synonym rules decided by Jess Haley on 2026-10-22 (empty-ontology `docs/conventions.md` section 4).
Everything below is **Proposed (not decided)**.

Denominators: 386 EMPTY declarations, 32 deprecated, **354 live** (348 classes, 6 object properties), all 354 read
(label, definition, comment, existing synonyms). 29 live terms already carry 35 synonyms.
OLS4: all 354 searched in bulk (537 queries: label, the part after the colon, and a trimmed core; `ols_results.json`),
plus 89 targeted searches and 44 scoped-synonym lookups through the OLS4 v2 entities API (`targeted_log.txt`).
"Evidence" quotes OLS4 output from 2026-10-22. Scope in the evidence column is the source ontology's scope where OLS4 returned one.

## A. Proposals (one row per synonym)

| id | label | proposed synonym | scope | abbr? | evidence | conf. |
|---|---|---|---|---|---|---|
| EMPTY:0000081 | identifier | ID | exact | yes | NCIT:C25364 Identifier, exact synonym "ID" (also AFO identifier syn "ID") | high |
| EMPTY:0000128 | subject identifier | subject ID | exact | no (contains an abbreviation) | NCIT:C83083 Subject Identifier, exact "Subject ID" | high |
| EMPTY:0000091 | timepoint | time point | exact | no | NCIT:C68568 Timepoint, exact "Time Point" | high |
| EMPTY:0000091 | timepoint | point in time | exact | no | NCIT:C68568, exact "Point in Time" | high |
| EMPTY:0000201 | date of birth | birth date | exact | no | NCIT:C68615 Birth Date, exact "Date of Birth" (label is "Birth Date") | high |
| EMPTY:0000201 | date of birth | DOB | exact | yes | NCIT:C68615, exact "DOB" | high |
| EMPTY:0000248 | mean fluorescence intensity | MFI | exact | yes | NCIT:C163046, exact "MFI", "Mean Fluorescence Intensity" | high |
| EMPTY:0000089 | timestamp | time stamp | exact | no | NCIT:C72669 Computer Time Stamp, exact "Time Stamp", "Timestamp" | high |
| EMPTY:0000182 | dorsal dentate gyrus of hippocampal formation | dorsal dentate gyrus | exact | no | UBERON:0001885 dentate gyrus of hippocampal formation, exact "dentate gyrus" | high |
| EMPTY:0000183 | ventral dentate gyrus of hippocampal formation | ventral dentate gyrus | exact | no | UBERON:0001885, exact "dentate gyrus" | high |
| EMPTY:0000184 | dorsal CA3 | dorsal CA3 field of hippocampus | exact | no | UBERON:0003883 label "CA3 field of hippocampus"; exact "CA3" | high |
| EMPTY:0000185 | ventral CA3 | ventral CA3 field of hippocampus | exact | no | UBERON:0003883 (as above) | high |
| EMPTY:0000186 | dorsal CA1 | dorsal CA1 field of hippocampus | exact | no | UBERON:0003881 label "CA1 field of hippocampus"; exact "CA1", "cornu ammonis 1" | high |
| EMPTY:0000187 | ventral CA1 | ventral CA1 field of hippocampus | exact | no | UBERON:0003881 (as above) | high |
| EMPTY:0000186 | dorsal CA1 | dCA1 | exact | yes | sibling pattern already in the file: 0000182 "dDG", 0000184 "dCA3" (typed OMO:0003000); UBERON:0003881 exact "CA1". No ontology lists "dCA1" itself | medium |
| EMPTY:0000187 | ventral CA1 | vCA1 | exact | yes | sibling pattern: 0000183 "vDG", 0000185 "vCA3"; UBERON:0003881 exact "CA1". No ontology lists "vCA1" itself | medium |
| EMPTY:0000229 | echocardiogram acquisition | echocardiography | exact | no | NCIT:C16525 Echocardiography Test, exact "Echocardiography"; term definition is the procedure | high |
| EMPTY:0000227 | data-independent acquisition (DIA) | data-independent acquisition | exact | no | MS:1003215 label "data-independent acquisition" | medium |
| EMPTY:0000227 | data-independent acquisition (DIA) | DIA | exact | yes | MS:1003215, exact "DIA"; NCIT:C161786 syn "DIA" | medium |
| EMPTY:0000082 | universally unique identifier | globally unique identifier | exact | no | NCIT:C54100, exact "Globally Unique Identifier" | medium |
| EMPTY:0000082 | universally unique identifier | GUID | exact | yes | NCIT:C54100, exact "GUID" (team may prefer related: GUID is also used for Microsoft's variant) | medium |
| EMPTY:0000269 | potassium phosphate monobasic solution | potassium dihydrogen phosphate solution | exact | no | CHEBI:63036 label/IUPAC name "potassium dihydrogen phosphate" (related syn "Potassium phosphate monobasic"); the term's own definition gives this name | high |
| EMPTY:0000270 | potassium phosphate dibasic solution | dipotassium hydrogen phosphate solution | exact | no | CHEBI:131527 label/IUPAC name "dipotassium hydrogen phosphate" (related syn "Potassium phosphate, dibasic"); own definition gives this name | high |
| EMPTY:0000267 | magnesium sulfate solution | MgSO4 solution | exact | no (formula; follows existing "KH2PO4 solution" on 0000269, untyped) | CHEBI:32599 magnesium sulfate, syn "MgSO4" | medium |
| EMPTY:0000268 | calcium chloride solution | CaCl2 solution | exact | no (formula, as above) | CHEBI:3312 calcium dichloride, syn "CaCl2" | medium |
| EMPTY:0000313 | dipotassium hydrogen phosphate trihydrate | potassium phosphate dibasic trihydrate | exact | no | CHEBI:131527 related syn "potassium dibasic phosphate trihydrate" (catalogue-style name) | medium |
| EMPTY:0000070 | type II BNST neuron | type II neuron of the bed nucleus of the stria terminalis | exact | no | UBERON:0001880 bed nucleus of stria terminalis, exact "bed nucleus of the stria terminalis"; UBERON:0034894 syn "lateral subdivision of BNST" shows BNST = that nucleus; own definition expands it | medium |
| EMPTY:0000072 | type I BNST neuron | type I neuron of the bed nucleus of the stria terminalis | exact | no | as above | medium |
| EMPTY:0000073 | type III BNST neuron | type III neuron of the bed nucleus of the stria terminalis | exact | no | as above | medium |
| EMPTY:0000004 | acoustic startle response measurement | acoustic startle reaction measurement | exact | no | CMO:0001519 acoustic startle response measurement, exact "acoustic startle reaction measurement" | high |
| EMPTY:0000004 | acoustic startle response measurement | ASR measurement | exact | no (contains abbreviation) | definitions of EMPTY:0000005 and 0000053 write "Acoustic Startle Response (ASR)" | medium |
| EMPTY:0000005 | acoustic startle response derived measurement | calculated acoustic startle response measurement | exact | no | CMO:0002046 label (exact syn "calculated acoustic startle reaction measurement"); own definition: "a value calculated, inferred, or derived" | medium |
| EMPTY:0000003 | elevated plus maze measurement | EPM measurement | exact | no (contains abbreviation) | own definition "Elevated Plus Maze (EPM)"; MMO:0000262 related "EPM test"; CMO:0004021 syn "... in an EPM" | medium |
| EMPTY:0000287 | normalization to background illumination | flat-field correction | exact | no | BAO:0040003 background correction, alternative term "flat field correction; shading correction"; EMPTY definition (divide by an image of the light source) is the flat-field method | medium |
| EMPTY:0000287 | normalization to background illumination | shading correction | related | no | BAO:0040003 (as above); shading correction can also be done by subtraction, so not always interchangeable | medium |
| EMPTY:0000258 | fluorescence imaging data | fluorescence micrograph | related | no | CHMO:0001895 fluorescence micrograph, exact "fluorescence microscopy image"; EMPTY term also covers video, so related | medium |
| EMPTY:0000258 | fluorescence imaging data | fluorescence microscopy image | related | no | CHMO:0001895 exact syn (as above) | medium |
| EMPTY:0000300 | brightfield imaging | bright-field imaging | exact | no | spelling variant; FBbi:00000243 is spelled "bright-field microscopy" | medium |
| EMPTY:0000300 | brightfield imaging | brightfield microscopy | related | no | NCIT:C19827 Brightfield Microscopy; BAO:0000457; EMPTY definition allows a camera without a microscope, so related | medium |
| EMPTY:0000327 | reference mark | fiducial marker | exact | no | NCIT:C82602 Fiducial Marker (exact "Fiduciary Marker", "Spatial Fiducials"); EMPTY definition: a mark placed to register images to a common frame | medium |
| EMPTY:0000325 | bacterial patch | bacterial lawn | related | no | WBPhenotype:0000402 "avoids bacterial lawn", WBPhenotype:0002373 (the C. elegans community name); a lawn usually covers a plate, a patch is discrete: related, not exact | medium |
| EMPTY:0000239 | C. elegans strain | Caenorhabditis elegans strain | exact | no | NCBITaxon:6239 label "Caenorhabditis elegans"; own definition "A specific strain of Caenorhabditis elegans" | medium |
| EMPTY:0000109 | C. elegans developmental stage | C. elegans life stage | exact | no | EFO:0000399 developmental stage, exact "life cycle stage"; WBls terms are labelled "C. elegans life stage ..." (e.g. WBls:0000821) | medium |
| EMPTY:0000167 | cell count | cell number | exact | no | MeSH D002452 Cell Count, entry term "Cell Number" (MeSH entry terms carry no scope) | medium |
| EMPTY:0000254 | Escherichia coli OP50: heat-killed | heat-killed Escherichia coli OP50 | exact | no | word-order variant of the label; NCBITaxon:637912 Escherichia coli OP50 (exact "Escherichia coli strain OP50") | low |
| EMPTY:0000200 | treatment: CNO or saline administration | treatment: clozapine N-oxide or saline administration | exact | no | CHEBI:169893 Clozapine N-oxide (CNO is not among its OLS synonyms) | low |
| EMPTY:0000168 | EYFP average cell count | enhanced yellow fluorescent protein average cell count | exact | no | MI:1118 enhanced yellow fluorescent protein tag, exact "eyfp"; FBbi:00000084 EYFP | low |
| EMPTY:0000369 | offset time | stop time | related | no | NCIT:C82573 End Time, exact "stop time"; related for the same reason as "end time" (section C) | low |
| EMPTY:0000340 | droplet | drop | related | no | ENVO:01000831 droplet, related "drop" | low |
| EMPTY:0000348 | oblique illumination imaging | oblique illumination | related | no | FBbi:00000285 oblique illumination | low |
| EMPTY:0000055 | postnatal day | P | exact | yes | own definition: "Often abbreviated ... with a capital P (as in P0, P10, etc)". One letter makes searches noisy; no ontology evidence for "PND" (OLS "PND" hits are drugs and vaccines) | low |
| EMPTY:0000090 | duration | time duration | exact | no | NCIT:C25330 Duration, syn "Time Duration" | low |

## B. Patterns (one decision covers many terms; not expanded into rows)

| pattern | terms | evidence | note |
|---|---|---|---|
| "<X> identifier" gets "<X> ID" | 0000051, 0000052, 0000087, 0000096, 0000103, 0000104, 0000112, 0000113, 0000123, 0000134, 0000139, 0000153, 0000172, 0000188, 0000224, 0000225 | NCIT:C25364 exact "ID"; NCIT:C83083 exact "Subject ID" | Only 0000081 and 0000128 have their own ontology evidence (section A) |
| "elevated plus maze: closed arm ..." gets "... enclosed arm ..." | 0000025 to 0000043 (19 terms) | MMO:0000265 enclosed arm of elevated plus maze apparatus, exact "closed arm of elevated plus maze apparatus" | The variants are exact, but 19 extra synonyms add little for search |
| paradigm prefix abbreviations (EPM, FPS, ASR) | 48 EPM terms, 0000053/57/58/67/93 (FPS), 0000060 to 0000065 (ASR) | own definitions write "(EPM)", "(FPS)", "(ASR)" | No ontology lists "FPS" for fear-potentiated startle (OLS: 0 hits for the phrase). A prefix that is the same on every term would be better handled in the definition |
| "C. elegans ..." gets "Caenorhabditis elegans ..." | about 30 terms | NCBITaxon:6239 | Only 0000239 is proposed above |

## C. Existing synonyms whose scope looks wrong under the rules

| id | label | synonym (now) | proposed | evidence |
|---|---|---|---|---|
| EMPTY:0000368 | onset time | "start time" exact | **related** | Jess Haley's decided example (2026-10-22). The term's own comment says "SIO start time 000669 / NCIT Start Time C78441 mean the start of a process, which for a presentation is stimopen". At FETCH_HEAD 24d316a it is still `hasExactSynonym` (line 2990) |
| EMPTY:0000369 | offset time | "end time" exact | **related** (by analogy; not itself decided) | The same comment: NCIT End Time C82573 / stimclose versus offset. Line 2998 is still `hasExactSynonym` |
| EMPTY:0000261 | arbitrary unit per millisecond | "AU/ms" exact, untyped | maybe add OMO:0003000 | It is an abbreviation, like "NGM". Optional, and a question for the team: is a unit symbol an "abbreviation"? |
| EMPTY:0000236 | McCutcheon index | "chemotactic ratio" exact | keep; I could not verify it | OLS4 has 0 hits for "McCutcheon", "chemotaxis index" and "straightness index". **Do not** add "chemotaxis index": in C. elegans work it names a different count-based measure (from memory, not shown) |

No other existing synonym looks wrong. Checked: UUID, OME-NGFF, NGM, NGM agar, the NGM without peptone variants,
LB + carbenicillin, S Basal / S basal buffer, the S Complete forms, KH2PO4/K2HPO4 solution, cholesterol in ethanol,
K2HPO4 trihydrate, folder, GMM clustering, QDA, TLS, tetanic light stimulation, dDG/vDG/dCA3/vCA3, ai/ao/di/do, and the two
previous names (0000105, 0000137).

## D. Considered, no evidence (not proposed)

- 0000228 slide scanner image acquisition: "whole slide imaging" / "WSI". OLS: 0 hits for "whole slide imaging", "whole slide", "virtual slide" or "slide scanning".
- 0000264 LB with carbenicillin: "lysogeny broth with carbenicillin" / "Luria-Bertani". OLS: 0 hits for "lysogeny broth" and "Luria-Bertani".
- 0000163 contextual fear conditioning measurement: "CFC". The OLS "CFC" hits are genes and taxa.
- 0000302 distance transform: "distance map". The only OLS hit is EDAM:operation_2937, which is about plotting.
- 0000384 signed distance to region boundary: "signed distance function". OLS: no relevant hit.
- 0000308 bin width: "bin size". OLS: 2 irrelevant hits.
- 0000288 circularity: "form factor", "isoperimetric quotient". AFO, TFO and ENM circularity carry no synonyms.
- 0000301 video tracking: "animal tracking", "pose estimation". OLS: 0 hits; MMO:0000760 is a different thing.
- 0000336 agar plug transfer: "chunking". OLS hits unrelated (WormBook usage, not shown).
- 0000337 worm picking: "picking". No evidence.
- 0000237 mean velocity: the definition says "average speed", and PATO:0000008 speed has only related "velocity". This is a label/definition mismatch, not a synonym.
- 0000061 sampling rate: "sampling frequency". AFO:AFR_0001250 lists it, but OLS returned no scope.
- 0000177 / 0000175 freezing: CMO:0001044 related "percent of time spent in freezing behavior". Related only, and low value.
- 0000352 / 0000353 anterior/posterior end point: "head" / "tail". No evidence.
- 0000309 video frame: "frame index". No evidence.
- 0000360 chemogenetics, 0000363 optogenetics: MeSH "Chemogenetic Techniques", "Optogenetic Techniques". These are plural or technique forms, of low value.
- 0000325 bacterial patch: "lawn" is related only (row in A), never exact.
- Every other live term: OLS returned no hit with a usable synonym, or the term is a lab/paradigm-specific composite (the EPM, FPS, CFC and C. elegans assay columns, the strains BAB9001 to 9005, TM5848 and PT3602, treatment/purpose/approach values, NDI-specific identifiers and formats) for which no genuine alternative name exists.
