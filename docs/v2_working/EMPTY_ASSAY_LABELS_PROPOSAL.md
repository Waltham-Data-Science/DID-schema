# Old EMPTY labels that carry assay context: the list (proposal, nothing decided)

**Every row below is Proposed (not decided).** It is the list that
[old EMPTY labels generalised] (`docs/plans/did_v2_go_forward_class_audit.md`, Jess
Haley, 2026-10-27) asks Claude to draft: EMPTY terms minted before 2026-10-20
whose labels carry assay context. Per T19, each row first looks for an existing
ontology term (which would replace the EMPTY term), and otherwise proposes a
general relabel. Nothing changes before Jess approves each row. It answers
did-schema issue #116 (the relabel part). The issue's mechanical part (9 terms
with no definition, 276 with no provenance comment) is empty-ontology work and
is not done here.

## Denominators (first)

| what | count | source |
|---|---|---|
| empty-ontology read | c58b42f (`V2`, PR #29 merge) | `git -C empty-ontology rev-parse HEAD` |
| EMPTY classes declared | 400 | `Declaration(Class(obo:EMPTY_...))` in `src/ontology/empty-edit.owl` |
| of those, with a definition / a provenance comment | 391 / 124 (so 9 and 276 without, as #116 says) | `obo:IAO_0000115` / `rdfs:comment` assertions |
| minted before 2026-10-20 | 315 (286 live, 29 obsolete) | author date of the commit that first added the declaration (`git log --reverse -p` of the file) |
| **listed here** | **91**: tier A 70, tier B 21 | the selection below |
| live pre-2026-10-20 labels with a `:` or an assay word, not listed | 34 (named at the end, with why) | same script |
| listed rows held in the did-schema term registry | 0 of 91 | `schemas/registry/did_v2_term_registry.json` at this commit |
| listed rows referenced by code or docs | NDI-matlab 5 (EMPTY:0000006, 0000129, 0000255, 0000256, 0000257); DID-matlab 4 (0000097, 0000129, 0000256, 0000257) | `git grep -P 'EMPTY[:_][0-9]{7}(?![0-9])'` at the locked heads NDI-matlab a2ab2d152, DID-matlab 1447a432 |
| OLS4 searches | 162 label queries (full label, and the part after the colon) + 35 topic queries; 0 errors | `www.ebi.ac.uk/ols4/api/search` |

**Selection.** Tier A: a label of the form `<assay>: <thing>`, where the prefix
names an assay or test (elevated plus maze, fear-potentiated startle, acoustic
startle response, contextual fear conditioning, C. elegans behavioral or
chemotaxis assay). Tier B: a label without that form that still names an assay
or the organism (`C. elegans ...`, `... assay measurement`, `... parameter`).
Tier B is the less certain half: most of it are grouping classes (parents)
whose meaning *is* the assay, and the proposal for those is to keep them.

**What "existing ontology term" means here.** OLS4 search only; InterLex was not
searched. "None found" means these searches found nothing, not that no term
exists. Where an exact (assay-specific) term and a general one both exist, both
are named: per Jess's note on the decision ("many of them when generalized may be
existing ontology terms") the general one is what T19 asks for, with the assay
and the zone on the document.

**What any approved row needs before it is built** (not done here):
- empty-ontology first: a relabel changes the label (the old one kept as an
  OMO:0003008 previous name, empty-ontology `docs/conventions.md`); a replacement
  makes the EMPTY term obsolete with `consider` the replacing node.
- CMO (Clinical Measurement Ontology) is **not** in the CURIE registry
  (`schemas/registry/CURIE_lookups_meta.json`): a CMO row needs the prefix
  first (and ndi-ontology-matlab lookups).
- The did-schema term registry holds none of these rows today, so `check_term_registry`
  R7 is not affected until one is registered.
- The references in NDI-matlab (`+setup/+conv/+haley/doImport.m` EMPTY:0000129,
  `+babu/import.m` EMPTY:0000257, `+babu/treatments.json` EMPTY:0000255/0000256,
  two tutorials EMPTY:0000006) and DID-matlab tests (`testRawV1RoundTripImage.m`,
  `testRawV1RoundTripTreatment.m`, `testRawV1RoundTripPosition.m`) follow a
  replacement there first (CLAUDE.md section 3, rule 3), or read both nodes.
- `docs/v2_working/DAB_COLUMN_ROWS_DRAFT.md` uses the EPM and FPS nodes as its
  variables; an approved row changes that draft's variable.

## Tier A: `<assay>: <thing>` labels (70)

| row | node | label now | minted | referenced in (locked heads) | existing ontology term (T19) | proposal | the document carries instead | state |
|---|---|---|---|---|---|---|---|---|
| A1 | EMPTY:0000006 | elevated plus maze: open arm (north) - entries | 2026-01-18 | NDI-matlab | CMO:0000960 "number of entries into a discrete space in an experimental apparatus" (general) | replace by the existing term | location: open arm (north); method: the elevated plus maze test | Proposed (not decided) |
| A2 | EMPTY:0000007 | elevated plus maze: open arm (south) - entries | 2026-01-18 | none | CMO:0000960 "number of entries into a discrete space in an experimental apparatus" (general) | replace by the existing term | location: open arm (south); method: the elevated plus maze test | Proposed (not decided) |
| A3 | EMPTY:0000008 | elevated plus maze: open arm total entries | 2026-01-18 | none | CMO:0004010 "number of entries into an open arm of an elevated plus maze" (same meaning); or CMO:0000960 "number of entries into a discrete space in an experimental apparatus" (general) | replace by the existing term | location: open arms (both); method: the elevated plus maze test | Proposed (not decided) |
| A4 | EMPTY:0000009 | elevated plus maze: open arm (north) - head entries | 2026-01-18 | none | none found | relabel "number of head entries into a discrete space" | location: open arm (north); method: the elevated plus maze test | Proposed (not decided) |
| A5 | EMPTY:0000010 | elevated plus maze: open arm (south) - head entries | 2026-01-18 | none | none found | relabel "number of head entries into a discrete space" | location: open arm (south); method: the elevated plus maze test | Proposed (not decided) |
| A6 | EMPTY:0000011 | elevated plus maze: open arm total head entries | 2026-01-18 | none | none found | relabel "number of head entries into a discrete space" | location: open arms (both); method: the elevated plus maze test | Proposed (not decided) |
| A7 | EMPTY:0000012 | elevated plus maze: open arm (north) - time | 2026-01-18 | none | CMO:0000958 "amount of experiment time spent in a discrete space in an experimental apparatus" (general) | replace by the existing term | location: open arm (north); method: the elevated plus maze test | Proposed (not decided) |
| A8 | EMPTY:0000013 | elevated plus maze: open arm (south) - time | 2026-01-18 | none | CMO:0000958 "amount of experiment time spent in a discrete space in an experimental apparatus" (general) | replace by the existing term | location: open arm (south); method: the elevated plus maze test | Proposed (not decided) |
| A9 | EMPTY:0000014 | elevated plus maze: open arm total time | 2026-01-18 | none | CMO:0004014 "total amount of experiment time spent in the open arms of an elevated plus maze" (same meaning); or CMO:0000958 "amount of experiment time spent in a discrete space in an experimental apparatus" (general) | replace by the existing term | location: open arms (both); method: the elevated plus maze test | Proposed (not decided) |
| A10 | EMPTY:0000015 | elevated plus maze: open arm total - percent time during test duration | 2026-01-18 | none | CMO:0004075 "ratio of time spent in the open arms to total test time in an elevated plus maze" (same meaning; "fraction, quotient, or percentage"); or CMO:0000959 "percentage of experiment time spent in a discrete space in an experimental apparatus" (general) | replace by the existing term | location: open arms (both); method: the elevated plus maze test | Proposed (not decided) |
| A11 | EMPTY:0000016 | elevated plus maze: open arm (north) - latency to first entry | 2026-01-18 | none | none found (CMO:0001037 is time to first movement OUT of a space) | relabel "latency to first entry into a discrete space" | location: open arm (north); method: the elevated plus maze test | Proposed (not decided) |
| A12 | EMPTY:0000017 | elevated plus maze: open arm (south) - latency to first entry | 2026-01-18 | none | none found (CMO:0001037 is time to first movement OUT of a space) | relabel "latency to first entry into a discrete space" | location: open arm (south); method: the elevated plus maze test | Proposed (not decided) |
| A13 | EMPTY:0000018 | elevated plus maze: open arm total latency to first entry | 2026-01-18 | none | none found (CMO:0001037 is time to first movement OUT of a space) | relabel "latency to first entry into a discrete space" | location: open arms (both); method: the elevated plus maze test | Proposed (not decided) |
| A14 | EMPTY:0000019 | elevated plus maze: open arm (north) - time moving towards | 2026-01-18 | none | none found | relabel "time spent moving towards a discrete space" | location: open arm (north); method: the elevated plus maze test | Proposed (not decided) |
| A15 | EMPTY:0000020 | elevated plus maze: open arm (south) - time moving towards | 2026-01-18 | none | none found | relabel "time spent moving towards a discrete space" | location: open arm (south); method: the elevated plus maze test | Proposed (not decided) |
| A16 | EMPTY:0000021 | elevated plus maze: open arm total time moving towards | 2026-01-18 | none | none found | relabel "time spent moving towards a discrete space" | location: open arms (both); method: the elevated plus maze test | Proposed (not decided) |
| A17 | EMPTY:0000022 | elevated plus maze: open arm (north) - time freezing | 2026-01-18 | none | CMO:0001043 "amount of time spent in voluntary immobility" (general; its definition says "frozen") | replace by the existing term | location: open arm (north); method: the elevated plus maze test | Proposed (not decided) |
| A18 | EMPTY:0000023 | elevated plus maze: open arm (south) - time freezing | 2026-01-18 | none | CMO:0001043 "amount of time spent in voluntary immobility" (general; its definition says "frozen") | replace by the existing term | location: open arm (south); method: the elevated plus maze test | Proposed (not decided) |
| A19 | EMPTY:0000024 | elevated plus maze: open arm total time freezing | 2026-01-18 | none | CMO:0001043 "amount of time spent in voluntary immobility" (general; its definition says "frozen") | replace by the existing term | location: open arms (both); method: the elevated plus maze test | Proposed (not decided) |
| A20 | EMPTY:0000025 | elevated plus maze: closed arm (west) - entries | 2026-01-18 | none | CMO:0000960 "number of entries into a discrete space in an experimental apparatus" (general) | replace by the existing term | location: closed arm (west); method: the elevated plus maze test | Proposed (not decided) |
| A21 | EMPTY:0000026 | elevated plus maze: closed arm (east) - entries | 2026-01-18 | none | CMO:0000960 "number of entries into a discrete space in an experimental apparatus" (general) | replace by the existing term | location: closed arm (east); method: the elevated plus maze test | Proposed (not decided) |
| A22 | EMPTY:0000027 | elevated plus maze: closed arm total entries | 2026-01-18 | none | CMO:0004009 "number of entries into an enclosed arm of an elevated plus maze" (same meaning); or CMO:0000960 "number of entries into a discrete space in an experimental apparatus" (general) | replace by the existing term | location: closed arms (both); method: the elevated plus maze test | Proposed (not decided) |
| A23 | EMPTY:0000028 | elevated plus maze: closed arm (west) - head entries | 2026-01-18 | none | none found | relabel "number of head entries into a discrete space" | location: closed arm (west); method: the elevated plus maze test | Proposed (not decided) |
| A24 | EMPTY:0000029 | elevated plus maze: closed arm (east) - head entries | 2026-01-18 | none | none found | relabel "number of head entries into a discrete space" | location: closed arm (east); method: the elevated plus maze test | Proposed (not decided) |
| A25 | EMPTY:0000030 | elevated plus maze: closed arm total head entries | 2026-01-18 | none | none found | relabel "number of head entries into a discrete space" | location: closed arms (both); method: the elevated plus maze test | Proposed (not decided) |
| A26 | EMPTY:0000031 | elevated plus maze: closed arm (west) - time | 2026-01-18 | none | CMO:0000958 "amount of experiment time spent in a discrete space in an experimental apparatus" (general) | replace by the existing term | location: closed arm (west); method: the elevated plus maze test | Proposed (not decided) |
| A27 | EMPTY:0000032 | elevated plus maze: closed arm (east) - time | 2026-01-18 | none | CMO:0000958 "amount of experiment time spent in a discrete space in an experimental apparatus" (general) | replace by the existing term | location: closed arm (east); method: the elevated plus maze test | Proposed (not decided) |
| A28 | EMPTY:0000033 | elevated plus maze: closed arm total time | 2026-01-18 | none | CMO:0004012 "total amount of experiment time spent in an enclosed arm of an elevated plus maze" (same meaning); or CMO:0000958 "amount of experiment time spent in a discrete space in an experimental apparatus" (general) | replace by the existing term | location: closed arms (both); method: the elevated plus maze test | Proposed (not decided) |
| A29 | EMPTY:0000034 | elevated plus maze: closed arm total - percent time during test duration | 2026-01-18 | none | CMO:0000959 "percentage of experiment time spent in a discrete space in an experimental apparatus" (general) | replace by the existing term | location: closed arms (both); method: the elevated plus maze test | Proposed (not decided) |
| A30 | EMPTY:0000035 | elevated plus maze: closed arm (west) - latency to first entry | 2026-01-18 | none | none found (CMO:0001037 is time to first movement OUT of a space) | relabel "latency to first entry into a discrete space" | location: closed arm (west); method: the elevated plus maze test | Proposed (not decided) |
| A31 | EMPTY:0000036 | elevated plus maze: closed arm (east) - latency to first entry | 2026-01-18 | none | none found (CMO:0001037 is time to first movement OUT of a space) | relabel "latency to first entry into a discrete space" | location: closed arm (east); method: the elevated plus maze test | Proposed (not decided) |
| A32 | EMPTY:0000037 | elevated plus maze: closed arm total latency to first entry | 2026-01-18 | none | none found (CMO:0001037 is time to first movement OUT of a space) | relabel "latency to first entry into a discrete space" | location: closed arms (both); method: the elevated plus maze test | Proposed (not decided) |
| A33 | EMPTY:0000038 | elevated plus maze: closed arm (west) - time moving towards | 2026-01-18 | none | none found | relabel "time spent moving towards a discrete space" | location: closed arm (west); method: the elevated plus maze test | Proposed (not decided) |
| A34 | EMPTY:0000039 | elevated plus maze: closed arm (east) - time moving towards | 2026-01-18 | none | none found | relabel "time spent moving towards a discrete space" | location: closed arm (east); method: the elevated plus maze test | Proposed (not decided) |
| A35 | EMPTY:0000040 | elevated plus maze: closed arm total time moving towards | 2026-01-18 | none | none found | relabel "time spent moving towards a discrete space" | location: closed arms (both); method: the elevated plus maze test | Proposed (not decided) |
| A36 | EMPTY:0000041 | elevated plus maze: closed arm (west) - time freezing | 2026-01-18 | none | CMO:0001043 "amount of time spent in voluntary immobility" (general; its definition says "frozen") | replace by the existing term | location: closed arm (west); method: the elevated plus maze test | Proposed (not decided) |
| A37 | EMPTY:0000042 | elevated plus maze: closed arm (east) - time freezing | 2026-01-18 | none | CMO:0001043 "amount of time spent in voluntary immobility" (general; its definition says "frozen") | replace by the existing term | location: closed arm (east); method: the elevated plus maze test | Proposed (not decided) |
| A38 | EMPTY:0000043 | elevated plus maze: closed arm total time freezing | 2026-01-18 | none | CMO:0001043 "amount of time spent in voluntary immobility" (general; its definition says "frozen") | replace by the existing term | location: closed arms (both); method: the elevated plus maze test | Proposed (not decided) |
| A39 | EMPTY:0000044 | elevated plus maze: center - entries | 2026-01-18 | none | CMO:0000960 "number of entries into a discrete space in an experimental apparatus" (general) | replace by the existing term | location: center; method: the elevated plus maze test | Proposed (not decided) |
| A40 | EMPTY:0000045 | elevated plus maze: center - head entries | 2026-01-18 | none | none found | relabel "number of head entries into a discrete space" | location: center; method: the elevated plus maze test | Proposed (not decided) |
| A41 | EMPTY:0000046 | elevated plus maze: center - time | 2026-01-18 | none | CMO:0000958 "amount of experiment time spent in a discrete space in an experimental apparatus" (general) | replace by the existing term | location: center; method: the elevated plus maze test | Proposed (not decided) |
| A42 | EMPTY:0000047 | elevated plus maze: center - percent time during test duration | 2026-01-18 | none | CMO:0000959 "percentage of experiment time spent in a discrete space in an experimental apparatus" (general) | replace by the existing term | location: center; method: the elevated plus maze test | Proposed (not decided) |
| A43 | EMPTY:0000048 | elevated plus maze: center - latency to first entry | 2026-01-18 | none | none found (CMO:0001037 is time to first movement OUT of a space) | relabel "latency to first entry into a discrete space" | location: center; method: the elevated plus maze test | Proposed (not decided) |
| A44 | EMPTY:0000049 | elevated plus maze: center - time moving towards | 2026-01-18 | none | none found | relabel "time spent moving towards a discrete space" | location: center; method: the elevated plus maze test | Proposed (not decided) |
| A45 | EMPTY:0000050 | elevated plus maze: center - time freezing | 2026-01-18 | none | CMO:0001043 "amount of time spent in voluntary immobility" (general; its definition says "frozen") | replace by the existing term | location: center; method: the elevated plus maze test | Proposed (not decided) |
| A46 | EMPTY:0000051 | elevated plus maze: test identifier | 2026-01-18 | none | none found | relabel "test identifier" | method: the elevated plus maze test | Proposed (not decided) |
| A47 | EMPTY:0000053 | fear-potentiated startle: baseline acoustic startle response amplitude | 2026-01-18 | none | CMO:0001520 "amplitude of the acoustic startle response" (general) | replace by the existing term | phase: baseline (pre-conditioning); method: fear-potentiated startle | Proposed (not decided) |
| A48 | EMPTY:0000057 | fear-potentiated startle: trial type identifier | 2026-01-18 | none | none (NCIT:C49660 "Trial Type" is a clinical-trial design type) | relabel "trial type" | method: fear-potentiated startle | Proposed (not decided) |
| A49 | EMPTY:0000058 | fear-potentiated startle: apparatus chamber identifier | 2026-01-18 | none | none found | relabel "apparatus chamber identifier" | method: fear-potentiated startle | Proposed (not decided) |
| A50 | EMPTY:0000060 | acoustic startle response: number of samples | 2026-01-18 | none | none suitable (KISAO:0000326 is a simulation setting; MS:1000001 is a mass-spectrometry sample number) | relabel "number of samples" | method: acoustic startle response test | Proposed (not decided) |
| A51 | EMPTY:0000061 | acoustic startle response: sampling rate | 2026-01-18 | none | NCIT:C142234 "Digital Sampling Rate" ("the number of digital samples taken or recorded per unit of time") | replace by the existing term | method: acoustic startle response test | Proposed (not decided) |
| A52 | EMPTY:0000062 | acoustic startle response: startle window onset amplitude | 2026-01-18 | none | none found | relabel "amplitude at analysis window onset" | method: acoustic startle response test | Proposed (not decided) |
| A53 | EMPTY:0000063 | acoustic startle response: maximum amplitude | 2026-01-18 | none | EMPTY:0000349 "peak amplitude" (registered; T19 step 1), or NCIT:C156559 "Peak Response Amplitude" | replace by the existing term | method: acoustic startle response test | Proposed (not decided) |
| A54 | EMPTY:0000064 | acoustic startle response: time to maximum amplitude | 2026-01-18 | none | NCIT:C156560 "Peak Response Amplitude Latency" ("the time duration between the stimulus and the maximum response") | replace by the existing term | method: acoustic startle response test | Proposed (not decided) |
| A55 | EMPTY:0000065 | acoustic startle response: average amplitude | 2026-01-18 | none | none found | relabel "mean amplitude" | method: acoustic startle response test | Proposed (not decided) |
| A56 | EMPTY:0000067 | fear-potentiated startle: experimental phase or test name | 2026-01-18 | none | none found | relabel "experimental phase" (same meaning as EMPTY:0000099 below: one of the two would be made obsolete) | method: fear-potentiated startle | Proposed (not decided) |
| A57 | EMPTY:0000068 | elevated plus maze: test duration | 2026-01-18 | none | none usable (SNOMED 252129004 "Test duration": no SNOMED prefix in the CURIE registry) | relabel "test duration" | method: the elevated plus maze test | Proposed (not decided) |
| A58 | EMPTY:0000129 | C. elegans behavioral assay: video recording | 2026-01-18 | NDI-matlab, DID-matlab | NCIT:C91063 "Video Recording" (registered; already this term's parent) | replace by the existing term | the organism (subject entity), the assay (method) | Proposed (not decided) |
| A59 | EMPTY:0000139 | C. elegans behavioral assay: encounter identifier | 2026-01-18 | none | none (NCIT encounter ids are clinical encounters) | relabel "encounter identifier" | the organism (subject entity), the assay (method) | Proposed (not decided) |
| A60 | EMPTY:0000173 | contextual fear conditioning: block type | 2026-01-18 | none | none found | relabel "block type" | method: contextual fear conditioning | Proposed (not decided) |
| A61 | EMPTY:0000174 | contextual fear conditioning: block minute | 2026-01-18 | none | none found | relabel "minute within block" | method: contextual fear conditioning | Proposed (not decided) |
| A62 | EMPTY:0000175 | contextual fear conditioning: time freezing | 2026-01-18 | none | CMO:0001043 "amount of time spent in voluntary immobility" (general) | replace by the existing term | method: contextual fear conditioning | Proposed (not decided) |
| A63 | EMPTY:0000176 | contextual fear conditioning: block duration | 2026-01-18 | none | none found | relabel "block duration" | method: contextual fear conditioning | Proposed (not decided) |
| A64 | EMPTY:0000177 | contextual fear conditioning: percent time freezing | 2026-01-18 | none | CMO:0001044 "percent of time spent in voluntary immobility" (general) | replace by the existing term | method: contextual fear conditioning | Proposed (not decided) |
| A65 | EMPTY:0000232 | C. elegans chemotaxis assay parameter: chemoattractant mixture table | 2026-03-30 | none | none found | relabel "chemoattractant mixture table" | the assay (method: chemotaxis assay) | Proposed (not decided) |
| A66 | EMPTY:0000233 | C. elegans chemotaxis assay parameter: chemoattractant mixture volume | 2026-03-30 | none | none found | relabel "chemoattractant mixture volume" | the assay (method: chemotaxis assay) | Proposed (not decided) |
| A67 | EMPTY:0000234 | C. elegans chemotaxis assay parameter: assay duration | 2026-03-30 | none | none found (EMPTY:0000090 "duration" is broader) | relabel "assay duration" | the assay (method: chemotaxis assay) | Proposed (not decided) |
| A68 | EMPTY:0000236 | C. elegans chemotaxis assay measurement: McCutcheon index | 2026-03-30 | none | none found | relabel "McCutcheon index" | the assay (method: chemotaxis assay) | Proposed (not decided) |
| A69 | EMPTY:0000237 | C. elegans chemotaxis assay measurement: mean velocity | 2026-03-30 | none | PATO:0000008 "speed" (registered) with the mean as the statistic; none for "mean speed" | relabel "mean speed", or replace by PATO:0000008 if the document states the mean | the assay (method: chemotaxis assay); the organism (subject) | Proposed (not decided) |
| A70 | EMPTY:0000257 | C. elegans chemotaxis assay: video recording | 2026-04-01 | NDI-matlab, DID-matlab | NCIT:C91063 "Video Recording" (registered; this term's grandparent) | replace by the existing term | the organism (subject entity), the assay (method) | Proposed (not decided) |

## Tier B: other labels naming the assay or the organism (21)

| row | node | label now | minted | referenced in (locked heads) | existing ontology term (T19) | proposal | the document carries instead | state |
|---|---|---|---|---|---|---|---|---|
| B1 | EMPTY:0000003 | elevated plus maze measurement | 2026-01-18 | none | none for the category (CMO:0004021 is voluntary locomotion only) | keep: a grouping class whose meaning is the assay | (a grouping class: nothing moves) | Proposed (not decided) |
| B2 | EMPTY:0000004 | acoustic startle response measurement | 2026-01-18 | none | CMO:0001519 "acoustic startle response measurement" (same meaning) | replace by the existing term (grouping class) | (a grouping class: nothing moves) | Proposed (not decided) |
| B3 | EMPTY:0000005 | acoustic startle response derived measurement | 2026-01-18 | none | CMO:0002046 "calculated acoustic startle response measurement" (same meaning) | replace by the existing term (grouping class) | (a grouping class: nothing moves) | Proposed (not decided) |
| B4 | EMPTY:0000092 | elevated plus maze parameter | 2026-01-18 | none | none found | keep: a grouping class whose meaning is the assay | (a grouping class: nothing moves) | Proposed (not decided) |
| B5 | EMPTY:0000093 | fear-potentiated startle parameter | 2026-01-18 | none | none found | keep: a grouping class whose meaning is the assay | (a grouping class: nothing moves) | Proposed (not decided) |
| B6 | EMPTY:0000097 | C. elegans assay parameter | 2026-01-18 | DID-matlab | none found | keep: a grouping class whose meaning is the assay | (a grouping class: nothing moves) | Proposed (not decided) |
| B7 | EMPTY:0000099 | C. elegans assay phase | 2026-01-18 | none | none found | relabel "experimental phase" (same meaning as EMPTY:0000067 above) | the organism (subject) | Proposed (not decided) |
| B8 | EMPTY:0000100 | C. elegans behavioral assay measurement | 2026-01-18 | none | none found | keep: a grouping class whose meaning is the assay | (a grouping class: nothing moves) | Proposed (not decided) |
| B9 | EMPTY:0000101 | C. elegans behavioral assay parameter | 2026-01-18 | none | none found | keep: a grouping class whose meaning is the assay | (a grouping class: nothing moves) | Proposed (not decided) |
| B10 | EMPTY:0000102 | C. elegans cultivation parameter | 2026-01-18 | none | none found | keep: a grouping class whose meaning is the assay | (a grouping class: nothing moves) | Proposed (not decided) |
| B11 | EMPTY:0000109 | C. elegans developmental stage | 2026-01-18 | none | NCIT:C43531 "Developmental Stage" (registered); values from WBls (C. elegans life stage, WBls:0000825) | replace by the existing term | the organism (subject) | Proposed (not decided) |
| B12 | EMPTY:0000114 | C. elegans picked timestamp | 2026-01-18 | none | none found | relabel "organism transfer timestamp" | the organism (subject) | Proposed (not decided) |
| B13 | EMPTY:0000115 | C. elegans behavioral assay label | 2026-01-18 | none | none found | relabel "food patch layout" (its definition: the layout of food patches) | the assay (method) | Proposed (not decided) |
| B14 | EMPTY:0000150 | bacterial fluorescence assay measurement | 2026-01-18 | none | none found | keep: a grouping class whose meaning is the assay | (a grouping class: nothing moves) | Proposed (not decided) |
| B15 | EMPTY:0000163 | contextual fear conditioning measurement | 2026-01-18 | none | none (VT:0010529 is a trait, not a measurement) | keep: a grouping class whose meaning is the assay (it has no definition: issue #116) | (a grouping class: nothing moves) | Proposed (not decided) |
| B16 | EMPTY:0000164 | contextual fear conditioning parameter | 2026-01-18 | none | none found | keep: a grouping class whose meaning is the assay (it has no definition: issue #116) | (a grouping class: nothing moves) | Proposed (not decided) |
| B17 | EMPTY:0000231 | C. elegans chemotaxis assay parameter | 2026-03-30 | none | none found | keep: a grouping class whose meaning is the assay | (a grouping class: nothing moves) | Proposed (not decided) |
| B18 | EMPTY:0000235 | C. elegans chemotaxis assay measurement | 2026-03-30 | none | none found | keep: a grouping class whose meaning is the assay | (a grouping class: nothing moves) | Proposed (not decided) |
| B19 | EMPTY:0000239 | C. elegans strain | 2026-03-30 | none | NCIT:C14419 "Organism Strain" (registered) is broader | keep: a grouping class (parent of the C. elegans strain terms); the species is its meaning | (a grouping class: nothing moves) | Proposed (not decided) |
| B20 | EMPTY:0000255 | C. elegans transfer method: M9 buffer wash | 2026-03-30 | NDI-matlab | none found | relabel "M9 buffer wash transfer" | the organism (subject) | Proposed (not decided) |
| B21 | EMPTY:0000256 | C. elegans transfer method: titanium pick | 2026-03-31 | NDI-matlab, DID-matlab | none found | relabel "pick transfer" | the organism (subject) | Proposed (not decided) |

## Considered and not listed (34)

Live, minted before 2026-10-20, with a `:` in the label, not listed because the
prefix is not an assay:

- `treatment: ...` (EMPTY:0000190-0000204, 14 terms) and `approach: ...`
  (0000215-0000223, 9) and `purpose: ...` (0000206-0000213, 8): the prefix is the
  term's category (the v1 treatment, approach and purpose vocabularies), not an
  assay. Whether those prefixes are context T19 removes is a separate question.
- `bacterial patch center: X coordinate` / `Y coordinate` (0000124, 0000125): the
  prefix is the thing measured.
- `Escherichia coli OP50: heat-killed` (0000254): a strain and its state.

## How this was measured

Scripts and outputs were in the session's scratch area and were not kept
(`docs/v2_working/README.md`). The steps:

1. Parse `empty-edit.owl` (functional syntax) for each `obo:EMPTY_nnnnnnn`: label,
   definition, comments, `owl:deprecated`, `SubClassOf` parents.
2. Mint date: the first commit (`git log --reverse -p --date=short -- src/ontology/empty-edit.owl`)
   whose added lines declare the class.
3. OLS4: `api/search?q=<label>` and `q=<text after the colon>` (8 rows each,
   `isDefiningOntology=true`), then topic searches (`elevated plus maze` in CMO,
   `startle`, `freezing`, `time spent`, `entries`, `head dip`, `chemotaxis assay`,
   `sampling frequency`, `trial type`, C. elegans life stage, ...); each candidate's
   definition read with `queryFields=obo_id`.
4. References: `git grep -P 'EMPTY[:_][0-9]{7}(?![0-9])' HEAD` in each locked
   sibling (the lookahead matters: NDI-matlab `+hunsberger/doImport.m` writes
   eight-digit ids such as `EMPTY:00000289`, which a looser pattern reads as
   EMPTY:0000028).
