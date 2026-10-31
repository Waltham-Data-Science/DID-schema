# G53 build plan: [assay labels batch 1] to [assay labels batch 6]

READ-ONLY planning output. Nothing here is decided; every step and every option below is
**Proposed (not decided)**. Written 2026-10-30 by a read-only agent; no repository was edited.
The scratch evidence (owl copies, per-node grep files) lived in a session scratchpad that is not
kept; every command needed to re-derive it is quoted below. Its questions are logged as
docs/V2_PLAN.md G69.

## 0. What was read (denominators first)

| what | value | command |
|---|---|---|
| did-schema | HEAD 7c209d5 (branch `claude/ecstatic-pascal-md91fw`, 4 commits ahead of `origin/main` 3d0d1bf; both hold the six decision lines) | `git rev-parse HEAD origin/main`; `git grep -c "assay labels batch" origin/main -- docs/plans/did_v2_go_forward_class_audit.md` -> 6, same on HEAD |
| decision lines read | 6 (`[assay labels batch 1]`..`[assay labels batch 6]`, lines 1702-1720) | `grep -n "assay labels batch" docs/plans/did_v2_go_forward_class_audit.md` |
| empty-ontology | `origin/V2` b1a12e2 (2026-10-29, PR #32 merge); `origin/main` 68fa1b5 | `git rev-parse origin/V2 origin/main` |
| empty-edit.owl classes declared | 408 | `grep -c 'Declaration(Class(obo:EMPTY_'` on `git show origin/V2:src/ontology/empty-edit.owl` |
| NDI-matlab | `origin/V2` 3ddc46e (PR #1105 merge). NB the lock's `head` is 3e0a2ca; this plan reads `origin/V2` as asked | `git rev-parse origin/V2`; `tools/sibling_lock.json` |
| DID-matlab | `origin/V2` d914a8c (PR #303 merge). Lock head 3c6c4d7 | same |
| ndi-ontology-matlab | `origin/main` 7b51308 (cloned read-only into scratch `g53/ext/`) | `git log -1 origin/main` |
| EMPTY terms the six lines touch | **91** (tier A 70, tier B 21) | row->node map parsed from `docs/v2_working/EMPTY_ASSAY_LABELS_PROPOSAL.md`, checked: 91 rows, all match the proposal's node column |
| term registry rows | 914 | `json.load(...)['terms']` |
| of the 91, registered in the term registry | **0** | `git grep -c -P "$PAT" HEAD -- schemas/registry/did_v2_term_registry.json schemas/did_v2` -> no output, exit=1 |

`$PAT` (all 91 nodes, both spellings) is in `g53/pat.txt`:
`EMPTY[:_](0000003|0000004|...|0000257)(?![0-9])`.

---

## 1. One row per EMPTY term: current label, decided outcome, tag

Labels are from `git show origin/V2:src/ontology/empty-edit.owl` (and are identical on
empty-ontology `origin/main` for all 91: checked by the same parse of `origin/main`'s edit file,
"main-label-same" for every row). "obsolete -> X" means the decision line maps the node to an
existing term X; batches 1 and 2 say "made obsolete with `consider`" explicitly, batches 3-5 say
"->" and batch 6's Build pending says "obsoletes with `consider`" (see AMBIGUITY Q3).
Loc = location condition, Dir = direction condition, Meth = method.

Quoted decision words, per tag:
- **b1** `[assay labels batch 1]` ("approve a1-a3. Though these are dab dataset specific"): "A1 EMPTY:0000006 ... -> variable CMO:0000960 ..., location MMO:0000266 ..., direction PATO:0045091 "north", method MMO:0000262 ...; A2 EMPTY:0000007 (south) -> the same with PATO:0045093 "south"; A3 EMPTY:0000008 ... -> CMO:0004010 ..., method MMO:0000262." Build pending: "empty-ontology (EMPTY:0000006-0000008 made obsolete with `consider` the replacing term)".
- **b2** ("I approve the batch 2 lists"): "A4 EMPTY:0000009 ..., A5 EMPTY:0000010 (south) and A6 EMPTY:0000011 (total) -> no existing term ..., so the EMPTY term is relabelled "number of head entries into a discrete space" ...; A7 EMPTY:0000012 (north) and A8 EMPTY:0000013 (south) "- time" -> CMO:0000958 ...; A9 EMPTY:0000014 -> CMO:0004014". Build pending: "empty-ontology (A4-A6 relabelled, with a general definition; A7-A9 made obsolete with `consider`)".
- **b3** ("Yes", to batch 3): "A10 EMPTY:0000015 -> CMO:0004075 ...; A11-A13 EMPTY:0000016-0000018 -> no existing term, relabelled "latency to first entry into a discrete space" ...; A14-A16 EMPTY:0000019-0000021 -> ... relabelled "time spent moving towards a discrete space" ...; A17-A19 EMPTY:0000022-0000024 -> CMO:0001043 ...; A20, A21 EMPTY:0000025, 0000026 -> CMO:0000960, location MMO:0000265 ..., direction PATO:0045094 west / PATO:0045092 east; A22 EMPTY:0000027 -> CMO:0004009".
- **b4** ("Yes"): "location MMO:0000265 ... and method MMO:0000262 throughout ...: A23-A25 EMPTY:0000028-0000030 -> relabelled "number of head entries into a discrete space" (as A4-A6) ...; A26, A27 EMPTY:0000031, 0000032 -> CMO:0000958 ...; A28 EMPTY:0000033 -> CMO:0004012 ...; A29 EMPTY:0000034 -> CMO:0000959 ... (no closed-arm term); A30-A32 EMPTY:0000035-0000037 -> relabelled "latency to first entry into a discrete space" ...; A33-A35 EMPTY:0000038-0000040 -> relabelled "time spent moving towards a discrete space" ...; A36 EMPTY:0000041 -> CMO:0001043 ..., west."
- **b5** ("Otherwise agreed", with "A57 lookup" and the chamber as an entity): see rows A37-A61 below; "Open: A46 "test identifier" and A59 "encounter identifier" ..., and the method terms of A47-A49, A56 (fear-potentiated startle: no term exists) and A50-A55 (acoustic startle: OBI:0003710 only if recorded in an anechoic chamber)."
- **b6** ("this looks good", after B13 and grouping classes were discussed): see rows A62-A70, B*; "grouping classes (B1, B4-B6, B8-B10, B14-B19) are made obsolete once no child remains, kept otherwise; A46 EMPTY:0000051 and A59 EMPTY:0000139 stay relabelled "test identifier" and "encounter identifier"". Build pending: "empty-ontology (relabels with general definitions, obsoletes with `consider`)".

| row | node | current label (origin/V2) | decided outcome | variable / location / direction / method | tag |
|---|---|---|---|---|---|
| A1 | EMPTY:0000006 | elevated plus maze: open arm (north) - entries | obsolete -> CMO:0000960 | Loc MMO:0000266; Dir PATO:0045091 north; Meth MMO:0000262 | b1 |
| A2 | EMPTY:0000007 | elevated plus maze: open arm (south) - entries | obsolete -> CMO:0000960 | Loc MMO:0000266; Dir PATO:0045093 south; Meth MMO:0000262 | b1 |
| A3 | EMPTY:0000008 | elevated plus maze: open arm total entries | obsolete -> CMO:0004010 | Meth MMO:0000262 | b1 |
| A4 | EMPTY:0000009 | elevated plus maze: open arm (north) - head entries | relabel "number of head entries into a discrete space" | Loc MMO:0000266; Dir north; Meth MMO:0000262 | b2 |
| A5 | EMPTY:0000010 | elevated plus maze: open arm (south) - head entries | relabel (same label) | Loc MMO:0000266; Dir south; Meth MMO:0000262 | b2 |
| A6 | EMPTY:0000011 | elevated plus maze: open arm total head entries | relabel (same label) | Loc MMO:0000266; no Dir; Meth MMO:0000262 | b2 |
| A7 | EMPTY:0000012 | elevated plus maze: open arm (north) - time | obsolete -> CMO:0000958 | Loc MMO:0000266; Dir north; Meth MMO:0000262 | b2 |
| A8 | EMPTY:0000013 | elevated plus maze: open arm (south) - time | obsolete -> CMO:0000958 | Loc MMO:0000266; Dir south; Meth MMO:0000262 | b2 |
| A9 | EMPTY:0000014 | elevated plus maze: open arm total time | obsolete -> CMO:0004014 | Meth MMO:0000262 | b2 |
| A10 | EMPTY:0000015 | elevated plus maze: open arm total - percent time during test duration | obsolete -> CMO:0004075 | Meth MMO:0000262 | b3 |
| A11 | EMPTY:0000016 | elevated plus maze: open arm (north) - latency to first entry | relabel "latency to first entry into a discrete space" | Loc MMO:0000266; north; MMO:0000262 | b3 |
| A12 | EMPTY:0000017 | elevated plus maze: open arm (south) - latency to first entry | relabel (same) | Loc MMO:0000266; south; MMO:0000262 | b3 |
| A13 | EMPTY:0000018 | elevated plus maze: open arm total latency to first entry | relabel (same) | Loc MMO:0000266; none; MMO:0000262 | b3 |
| A14 | EMPTY:0000019 | elevated plus maze: open arm (north) - time moving towards | relabel "time spent moving towards a discrete space" | Loc MMO:0000266; north; MMO:0000262 | b3 |
| A15 | EMPTY:0000020 | elevated plus maze: open arm (south) - time moving towards | relabel (same) | Loc MMO:0000266; south | b3 |
| A16 | EMPTY:0000021 | elevated plus maze: open arm total time moving towards | relabel (same) | Loc MMO:0000266; none | b3 |
| A17 | EMPTY:0000022 | elevated plus maze: open arm (north) - time freezing | obsolete -> CMO:0001043 | Loc MMO:0000266; north; MMO:0000262 | b3 |
| A18 | EMPTY:0000023 | elevated plus maze: open arm (south) - time freezing | obsolete -> CMO:0001043 | Loc MMO:0000266; south | b3 |
| A19 | EMPTY:0000024 | elevated plus maze: open arm total time freezing | obsolete -> CMO:0001043 | Loc MMO:0000266; none | b3 |
| A20 | EMPTY:0000025 | elevated plus maze: closed arm (west) - entries | obsolete -> CMO:0000960 | Loc MMO:0000265; Dir PATO:0045094 west; MMO:0000262 | b3 |
| A21 | EMPTY:0000026 | elevated plus maze: closed arm (east) - entries | obsolete -> CMO:0000960 | Loc MMO:0000265; Dir PATO:0045092 east | b3 |
| A22 | EMPTY:0000027 | elevated plus maze: closed arm total entries | obsolete -> CMO:0004009 | Meth MMO:0000262 | b3 |
| A23 | EMPTY:0000028 | elevated plus maze: closed arm (west) - head entries | relabel "number of head entries into a discrete space" | Loc MMO:0000265; west; MMO:0000262 | b4 |
| A24 | EMPTY:0000029 | elevated plus maze: closed arm (east) - head entries | relabel (same) | Loc MMO:0000265; east | b4 |
| A25 | EMPTY:0000030 | elevated plus maze: closed arm total head entries | relabel (same) | Loc MMO:0000265; none | b4 |
| A26 | EMPTY:0000031 | elevated plus maze: closed arm (west) - time | obsolete -> CMO:0000958 | Loc MMO:0000265; west | b4 |
| A27 | EMPTY:0000032 | elevated plus maze: closed arm (east) - time | obsolete -> CMO:0000958 | Loc MMO:0000265; east | b4 |
| A28 | EMPTY:0000033 | elevated plus maze: closed arm total time | obsolete -> CMO:0004012 | Loc MMO:0000265 ("throughout"); MMO:0000262 | b4 |
| A29 | EMPTY:0000034 | elevated plus maze: closed arm total - percent time during test duration | obsolete -> CMO:0000959 | Loc MMO:0000265 ("throughout"); MMO:0000262 | b4 |
| A30 | EMPTY:0000035 | elevated plus maze: closed arm (west) - latency to first entry | relabel "latency to first entry into a discrete space" | Loc MMO:0000265; west | b4 |
| A31 | EMPTY:0000036 | elevated plus maze: closed arm (east) - latency to first entry | relabel (same) | Loc MMO:0000265; east | b4 |
| A32 | EMPTY:0000037 | elevated plus maze: closed arm total latency to first entry | relabel (same) | Loc MMO:0000265; none | b4 |
| A33 | EMPTY:0000038 | elevated plus maze: closed arm (west) - time moving towards | relabel "time spent moving towards a discrete space" | Loc MMO:0000265; west | b4 |
| A34 | EMPTY:0000039 | elevated plus maze: closed arm (east) - time moving towards | relabel (same) | Loc MMO:0000265; east | b4 |
| A35 | EMPTY:0000040 | elevated plus maze: closed arm total time moving towards | relabel (same) | Loc MMO:0000265; none | b4 |
| A36 | EMPTY:0000041 | elevated plus maze: closed arm (west) - time freezing | obsolete -> CMO:0001043 | Loc MMO:0000265; west | b4 |
| A37 | EMPTY:0000042 | elevated plus maze: closed arm (east) - time freezing | obsolete -> CMO:0001043 | Loc MMO:0000265; Dir PATO:0045092 east; MMO:0000262 | b5 |
| A38 | EMPTY:0000043 | elevated plus maze: closed arm total time freezing | obsolete -> CMO:0001043 | Loc MMO:0000265; none | b5 |
| A39 | EMPTY:0000044 | elevated plus maze: center - entries | obsolete -> CMO:0000960 | Loc MMO:0000263 "center of elevated plus maze apparatus"; MMO:0000262 | b5 |
| A40 | EMPTY:0000045 | elevated plus maze: center - head entries | relabel "number of head entries into a discrete space" | Loc MMO:0000263; MMO:0000262 | b5 |
| A41 | EMPTY:0000046 | elevated plus maze: center - time | obsolete -> CMO:0000958 | Loc MMO:0000263 | b5 |
| A42 | EMPTY:0000047 | elevated plus maze: center - percent time during test duration | obsolete -> CMO:0000959 | Loc MMO:0000263 | b5 |
| A43 | EMPTY:0000048 | elevated plus maze: center - latency to first entry | relabel "latency to first entry into a discrete space" | Loc MMO:0000263 | b5 |
| A44 | EMPTY:0000049 | elevated plus maze: center - time moving towards | relabel "time spent moving towards a discrete space" | Loc MMO:0000263 | b5 |
| A45 | EMPTY:0000050 | elevated plus maze: center - time freezing | obsolete -> CMO:0001043 | Loc MMO:0000263 | b5 |
| A46 | EMPTY:0000051 | elevated plus maze: test identifier | relabel "test identifier" ("mapped by the Dab and Haley imports") | Meth MMO:0000262 (b5: "method MMO:0000262 for A37-A46") | b6 (b5 left it open) |
| A47 | EMPTY:0000053 | fear-potentiated startle: baseline acoustic startle response amplitude | obsolete -> CMO:0001520 "with a baseline phase condition" | method OPEN (b5) | b5 |
| A48 | EMPTY:0000057 | fear-potentiated startle: trial type identifier | relabel "trial type" | method OPEN (b5) | b5 |
| A49 | EMPTY:0000058 | fear-potentiated startle: apparatus chamber identifier | "no variable: the chamber is a device entity whose `local_identifier` is the value (T1)" | method OPEN (b5) | b5 |
| A50 | EMPTY:0000060 | acoustic startle response: number of samples | obsolete -> AFO:AFR_0000956 "number of sampled points" | method OPEN (b5) | b5 |
| A51 | EMPTY:0000061 | acoustic startle response: sampling rate | obsolete -> NCIT:C142234 "Digital Sampling Rate" | method OPEN | b5 |
| A52 | EMPTY:0000062 | acoustic startle response: startle window onset amplitude | relabel "amplitude at analysis window onset" | method OPEN | b5 |
| A53 | EMPTY:0000063 | acoustic startle response: maximum amplitude | obsolete -> EMPTY:0000349 "peak amplitude" | method OPEN | b5 |
| A54 | EMPTY:0000064 | acoustic startle response: time to maximum amplitude | obsolete -> NCIT:C156560 "Peak Response Amplitude Latency" | method OPEN | b5 |
| A55 | EMPTY:0000065 | acoustic startle response: average amplitude | obsolete -> variable NCIT:C70831 "Amplitude", method OBI:0200079 "arithmetic mean calculation" | (assay method OPEN) | b5 |
| A56 | EMPTY:0000067 | fear-potentiated startle: experimental phase or test name | obsolete -> NCIT:C25257 "Phase" | method OPEN | b5 |
| A57 | EMPTY:0000068 | elevated plus maze: test duration | obsolete -> SNOMEDCT:252129004 "Test duration" | Meth MMO:0000262 | b5 |
| A58 | EMPTY:0000129 | C. elegans behavioral assay: video recording | obsolete -> NCIT:C91063 "Video Recording" ("NDI-matlab and DID-matlab reference EMPTY:0000129: code first") | - | b5 |
| A59 | EMPTY:0000139 | C. elegans behavioral assay: encounter identifier | relabel "encounter identifier" ("mapped by the Dab and Haley imports") | - | b6 (b5 left it open) |
| A60 | EMPTY:0000173 | contextual fear conditioning: block type | obsolete -> variable NCIT:C86947 "Block", "the block's kind as a term value" | Meth MMO:0000572 | b5 |
| A61 | EMPTY:0000174 | contextual fear conditioning: block minute | "no variable: the statement's time, an offset from the block's start in minutes (UO:0000031)" | Meth MMO:0000572 | b5 |
| A62 | EMPTY:0000175 | contextual fear conditioning: time freezing | obsolete -> CMO:0001043 | Meth MMO:0000572 | b6 |
| A63 | EMPTY:0000176 | contextual fear conditioning: block duration | obsolete -> NCIT:C25330 "Duration" | Meth MMO:0000572 | b6 |
| A64 | EMPTY:0000177 | contextual fear conditioning: percent time freezing | obsolete -> CMO:0001044 | Meth MMO:0000572 | b6 |
| A65 | EMPTY:0000232 | C. elegans chemotaxis assay parameter: chemoattractant mixture table | "the chemoattractant mixture is a `formulation` document referenced by the assay's method, variable NCIT:C45305 "Mixture"" | Meth BAO:0010269 | b6 |
| A66 | EMPTY:0000233 | C. elegans chemotaxis assay parameter: chemoattractant mixture volume | obsolete -> NCIT:C25335 "Volume" | Meth BAO:0010269 | b6 |
| A67 | EMPTY:0000234 | C. elegans chemotaxis assay parameter: assay duration | obsolete -> NCIT:C25330 "Duration" | Meth BAO:0010269 | b6 |
| A68 | EMPTY:0000236 | C. elegans chemotaxis assay measurement: McCutcheon index | relabel "McCutcheon index" ("no term anywhere") | Meth BAO:0010269 | b6 |
| A69 | EMPTY:0000237 | C. elegans chemotaxis assay measurement: mean velocity | obsolete -> PATO:0000008 "speed", method OBI:0200079 | (assay Meth BAO:0010269) | b6 |
| A70 | EMPTY:0000257 | C. elegans chemotaxis assay: video recording | obsolete -> NCIT:C91063 "Video Recording" | Meth BAO:0010269 | b6 |
| B1 | EMPTY:0000003 | elevated plus maze measurement | grouping: "made obsolete once no child remains, kept otherwise" | - | b6 |
| B2 | EMPTY:0000004 | acoustic startle response measurement | obsolete -> CMO:0001519 | - | b6 |
| B3 | EMPTY:0000005 | acoustic startle response derived measurement | obsolete -> CMO:0002046 | - | b6 |
| B4 | EMPTY:0000092 | elevated plus maze parameter | grouping (as B1) | - | b6 |
| B5 | EMPTY:0000093 | fear-potentiated startle parameter | grouping | - | b6 |
| B6 | EMPTY:0000097 | C. elegans assay parameter | grouping | - | b6 |
| B7 | EMPTY:0000099 | C. elegans assay phase | obsolete -> NCIT:C25257 "Phase" | - | b6 |
| B8 | EMPTY:0000100 | C. elegans behavioral assay measurement | grouping | - | b6 |
| B9 | EMPTY:0000101 | C. elegans behavioral assay parameter | grouping | - | b6 |
| B10 | EMPTY:0000102 | C. elegans cultivation parameter | grouping | - | b6 |
| B11 | EMPTY:0000109 | C. elegans developmental stage | obsolete -> NCIT:C43531 "Developmental Stage" ("values from WBls") | - | b6 |
| B12 | EMPTY:0000114 | C. elegans picked timestamp | "no variable (picking is a transfer manipulation, NCIT:C48167 "Transfer", at the statement's time)" | - | b6 |
| B13 | EMPTY:0000115 | C. elegans behavioral assay label | "obsolete, `consider` the Haley study entity" | - | b6 |
| B14 | EMPTY:0000150 | bacterial fluorescence assay measurement | grouping | - | b6 |
| B15 | EMPTY:0000163 | contextual fear conditioning measurement | grouping | - | b6 |
| B16 | EMPTY:0000164 | contextual fear conditioning parameter | grouping | - | b6 |
| B17 | EMPTY:0000231 | C. elegans chemotaxis assay parameter | grouping | - | b6 |
| B18 | EMPTY:0000235 | C. elegans chemotaxis assay measurement | grouping | - | b6 |
| B19 | EMPTY:0000239 | C. elegans strain | grouping | - | b6 |
| B20 | EMPTY:0000255 | C. elegans transfer method: M9 buffer wash | relabel "M9 buffer wash transfer" | - | b6 |
| B21 | EMPTY:0000256 | C. elegans transfer method: titanium pick | relabel "pick transfer" | - | b6 |

Tally: relabel 28 nodes (A4-6, A11-16, A23-25, A30-35, A40, A43, A44, A46, A48, A52, A59, A68, B20, B21);
grouping (conditional) 13 (B1, B4-B6, B8-B10, B14-B19); "no variable" 4 (A49, A61, B12, plus A65's
formulation document); B13 obsolete with a non-term consider; the rest (45) obsolete -> an existing term.

Hierarchy facts from `origin/V2:src/ontology/empty-edit.owl` (`SubClassOf(obo:EMPTY_x obo:EMPTY_y)`
parse, `g53/owlinfo.json`) that the grouping rule depends on:

| grouping node | children today | children outside the 91 |
|---|---|---|
| B1 0000003 | 0000006-0000050 (all A1-A45), 0000068 | none |
| B2 0000004 | 0000053, 0000062, 0000063, 0000064, 0000065 | none |
| B3 0000005 | none | - |
| B4 0000092 | 0000051, 0000068 | none |
| B5 0000093 | 0000057, 0000058, 0000060, 0000061, 0000067 | none |
| B6 0000097 | 0000099, 0000101, 0000102, 0000109, 0000114 | none |
| B8 0000100 | 0000129, 0000235, **0000274** "time to slow down" | 0000274 |
| B9 0000101 | 0000115, 0000231 | none |
| B10 0000102 | **none** | - |
| B13 0000115 (not a grouping row) | **0000292** "encounter type" | 0000292 |
| B14 0000150 | **none** | - |
| B15 0000163 | 0000175, 0000176, 0000177 | none |
| B16 0000164 | 0000173, 0000174, 0000176 | none |
| B17 0000231 | 0000232, 0000233, 0000234 | none |
| B18 0000235 | 0000236, 0000237 | none |
| B19 0000239 | **0000240-0000246** (strains BAB9001..BAB9005 ...) | 7 strains |
| A58 0000129 | 0000257 | none |

---

## 2. Where each term is written or read today

Commands (run per node; `$row`, `$node` 7 digits, `$label` the origin/V2 label; script
`g53/grep_all.sh` and `g53/grep_label_i.sh`, outputs one file per row/repo/kind in `g53/hits/`):

    git -C <repo> grep -n -P "EMPTY[:_]${node}(?![0-9])" <ref>     # node, both spellings
    git -C <repo> grep -n -i -F -- "$label" <ref>                  # current label, ignoring case

Refs: NDI-matlab `origin/V2`, DID-matlab `origin/V2`, did-schema `HEAD`, empty-ontology `origin/V2`.
The label grep is **case-insensitive** on purpose: a case-sensitive first pass missed every Dab
dictionary entry, which writes "EMPTY:Elevated Plus Maze: open arm (north) - entries" (capitalised).

### 2a. All 91 nodes at once, hits per file

    PAT='EMPTY[:_](0000003|...|0000257)(?![0-9])'   # g53/pat.txt
    == NDI-matlab: git grep -c -P "$PAT" origin/V2
    origin/V2:src/ndi/+ndi/+setup/+conv/+babu/import.m:1
    origin/V2:src/ndi/+ndi/+setup/+conv/+babu/treatments.json:2
    origin/V2:src/ndi/+ndi/+setup/+conv/+dabrowska/tutorial_67f723d574f5f79c6062389d.html:1
    origin/V2:src/ndi/+ndi/+setup/+conv/+haley/doImport.m:1
    origin/V2:src/ndi/+ndi/+setup/+conv/+haley/tutorial_682e7772cdf3f24938176fac.html:1
    origin/V2:src/ndi/docs/NDI-matlab/tutorials/datasets/Francesconi_et_al_2025/1_getting_started.md:1
    origin/V2:tests/+ndi/+unittest/+migrate/TestMigrateLocalEta.m:1
    == DID-matlab: git grep -c -P "$PAT" origin/V2
    origin/V2:tests/+did2/+unittest/testRawV1RoundTripImage.m:11
    origin/V2:tests/+did2/+unittest/testRawV1RoundTripPosition.m:2
    origin/V2:tests/+did2/+unittest/testRawV1RoundTripTreatment.m:1
    == did-schema: git grep -c -P "$PAT" HEAD
    HEAD:docs/v2_working/DAB_COLUMN_ROWS_DRAFT.md:68
    HEAD:docs/v2_working/EMPTY_ASSAY_LABELS_PROPOSAL.md:96
    HEAD:review/tenet-audit-2026-10-22/synonym_audit_alternative_names.md:7
    HEAD:review/tenet-audit-2026-10-22/synonym_audit_writer_strings.md:91
    HEAD:schemas/generated/did_v2_coverage_ledger.json:1
    HEAD:docs/generated/did_v2_coverage_ledger.md:1
    HEAD:docs/plans/did_v2_go_forward_class_audit.md:6
    HEAD:schemas/generated/did_v2_migration_targets.json:1
    HEAD:tests/test_term_registry.py:2
    == empty-ontology: git grep -c -P "$PAT" origin/V2
    origin/V2:docs/conventions.md:1
    origin/V2:empty-base.json:331   (and empty-base.obo/.owl, empty-full.*, empty-simple.*, empty.*: release artefacts)
    origin/V2:src/ontology/empty-edit.owl:535
    origin/V2:src/ontology/rename_map.tsv:80

    == git grep -c -P "$PAT" HEAD -- schemas/registry/did_v2_term_registry.json schemas/did_v2
    (no output) exit=1        -> none of the 91 is in the term registry, binding registry or any class file

DID-matlab `src/`: `git -C DID-matlab grep -c -P 'EMPTY[:_]0000(129|256|257)(?![0-9])' origin/V2 -- src`
printed nothing, exit 1. So every DID-matlab hit is a **test fixture** (v1 documents in the shape
NDI's writers give them), not a reader in `src/`.

did-schema non-record hits: `schemas/V_eta_coverage_ledger.{md,json}` and
`schemas/generated/did_v2_migration_targets.json` carry one authored flag sentence each ("JH's 7,007 are
EMPTY:0000129-133", the `ontologyLabel` row); `tests/test_term_registry.py:262-263` uses
EMPTY:0000003 / 0000004 as synthetic R12 fixtures (names "w", "x"; not read against the ontology).
The empty-ontology release artefacts (`empty-base.owl` etc.) were last regenerated 2026-04-04
(`git log -3 origin/V2 -- empty-base.owl` -> 8a82df7 "new release with Babu terms"); V2 PRs edit
only `src/ontology/empty-edit.owl` (last three: 8ce2cb1, 64dbbb8, 1e6793d, 2026-10-27..30).

### 2b. Per-node counts (node hits / case-insensitive label hits)

NDI = NDI-matlab origin/V2, DID = DID-matlab origin/V2, DS = did-schema HEAD, EO = empty-ontology
origin/V2 (EO counts include the 12 release artefacts). Every DS hit is in the files listed in 2a
(plan documents, review notes, the proposal) plus the label hits in
`docs/v2_working/DATASET_SPECIFIC_AUDIT.md`, `docs/v2_working/ISSUE_SORT_2026-10-27.md`; none is
in a registry or class file.

| row | node | NDI node | NDI label | DID node | DID label | DS node | DS label | EO node | EO label |
|---|---|---|---|---|---|---|---|---|---|
| A1 | 0000006 | 2 | 2 | 0 | 0 | 8 | 3 | 26 | 15 |
| A2 | 0000007 | 0 | 1 | 0 | 0 | 4 | 2 | 26 | 14 |
| A3 | 0000008 | 0 | 1 | 0 | 0 | 4 | 3 | 26 | 14 |
| A4 | 0000009 | 0 | 1 | 0 | 0 | 4 | 3 | 26 | 14 |
| A5 | 0000010 | 0 | 1 | 0 | 0 | 4 | 2 | 26 | 14 |
| A6 | 0000011 | 0 | 1 | 0 | 0 | 4 | 2 | 26 | 14 |
| A7 | 0000012 | 0 | 3 | 0 | 0 | 5 | 6 | 31 | 42 |
| A8 | 0000013 | 0 | 3 | 0 | 0 | 4 | 6 | 31 | 42 |
| A9 | 0000014 | 0 | 3 | 0 | 0 | 4 | 6 | 31 | 42 |
| A10 | 0000015 | 0 | 1 | 0 | 0 | 5 | 3 | 26 | 14 |
| A11 | 0000016 | 0 | 1 | 0 | 0 | 4 | 2 | 31 | 14 |
| A12 | 0000017 | 0 | 1 | 0 | 0 | 3 | 2 | 31 | 14 |
| A13 | 0000018 | 0 | 1 | 0 | 0 | 3 | 2 | 31 | 14 |
| A14 | 0000019 | 0 | 1 | 0 | 0 | 4 | 2 | 31 | 14 |
| A15 | 0000020 | 0 | 1 | 0 | 0 | 3 | 2 | 31 | 14 |
| A16 | 0000021 | 0 | 1 | 0 | 0 | 3 | 2 | 31 | 14 |
| A17 | 0000022 | 0 | 1 | 0 | 0 | 4 | 2 | 31 | 14 |
| A18 | 0000023 | 0 | 1 | 0 | 0 | 3 | 2 | 31 | 14 |
| A19 | 0000024 | 0 | 1 | 0 | 0 | 3 | 2 | 31 | 14 |
| A20 | 0000025 | 0 | 1 | 0 | 0 | 4 | 2 | 27 | 14 |
| A21 | 0000026 | 0 | 1 | 0 | 0 | 3 | 2 | 27 | 14 |
| A22 | 0000027 | 0 | 1 | 0 | 0 | 4 | 2 | 27 | 14 |
| A23 | 0000028 | 0 | 1 | 0 | 0 | 5 | 2 | 27 | 14 |
| A24 | 0000029 | 0 | 1 | 0 | 0 | 3 | 2 | 27 | 14 |
| A25 | 0000030 | 0 | 1 | 0 | 0 | 3 | 2 | 27 | 14 |
| A26 | 0000031 | 0 | 3 | 0 | 0 | 4 | 6 | 32 | 42 |
| A27 | 0000032 | 0 | 3 | 0 | 0 | 3 | 6 | 32 | 42 |
| A28 | 0000033 | 0 | 3 | 0 | 0 | 4 | 6 | 32 | 42 |
| A29 | 0000034 | 0 | 1 | 0 | 0 | 4 | 2 | 27 | 14 |
| A30 | 0000035 | 0 | 1 | 0 | 0 | 4 | 2 | 32 | 14 |
| A31 | 0000036 | 0 | 1 | 0 | 0 | 3 | 2 | 32 | 14 |
| A32 | 0000037 | 0 | 1 | 0 | 0 | 3 | 2 | 32 | 14 |
| A33 | 0000038 | 0 | 1 | 0 | 0 | 4 | 2 | 32 | 14 |
| A34 | 0000039 | 0 | 1 | 0 | 0 | 3 | 2 | 32 | 14 |
| A35 | 0000040 | 0 | 1 | 0 | 0 | 3 | 2 | 32 | 14 |
| A36 | 0000041 | 0 | 1 | 0 | 0 | 4 | 2 | 32 | 14 |
| A37 | 0000042 | 0 | 1 | 0 | 0 | 4 | 2 | 32 | 14 |
| A38 | 0000043 | 0 | 1 | 0 | 0 | 3 | 2 | 32 | 14 |
| A39 | 0000044 | 0 | 1 | 0 | 0 | 4 | 2 | 26 | 14 |
| A40 | 0000045 | 0 | 1 | 0 | 0 | 4 | 2 | 26 | 14 |
| A41 | 0000046 | 0 | 3 | 0 | 0 | 4 | 6 | 31 | 42 |
| A42 | 0000047 | 0 | 1 | 0 | 0 | 4 | 2 | 26 | 14 |
| A43 | 0000048 | 0 | 1 | 0 | 0 | 4 | 2 | 31 | 14 |
| A44 | 0000049 | 0 | 1 | 0 | 0 | 4 | 2 | 31 | 14 |
| A45 | 0000050 | 0 | 1 | 0 | 0 | 4 | 2 | 31 | 14 |
| A46 | 0000051 | 0 | 1 | 0 | 0 | 4 | 2 | 27 | 14 |
| A47 | 0000053 | 0 | 0 | 0 | 0 | 3 | 2 | 31 | 14 |
| A48 | 0000057 | 0 | 1 | 0 | 0 | 5 | 2 | 32 | 14 |
| A49 | 0000058 | 0 | 1 | 0 | 0 | 5 | 2 | 27 | 14 |
| A50 | 0000060 | 0 | 1 | 0 | 0 | 4 | 2 | 26 | 14 |
| A51 | 0000061 | 0 | 1 | 0 | 0 | 5 | 2 | 26 | 14 |
| A52 | 0000062 | 0 | 1 | 0 | 0 | 4 | 2 | 31 | 14 |
| A53 | 0000063 | 0 | 1 | 0 | 0 | 5 | 2 | 31 | 14 |
| A54 | 0000064 | 0 | 1 | 0 | 0 | 5 | 2 | 31 | 14 |
| A55 | 0000065 | 0 | 1 | 0 | 0 | 4 | 2 | 31 | 14 |
| A56 | 0000067 | 0 | 1 | 0 | 0 | 5 | 2 | 31 | 14 |
| A57 | 0000068 | 0 | 1 | 0 | 0 | 6 | 2 | 36 | 14 |
| A58 | 0000129 | 3 | 2 | 9 | 0 | 8 | 2 | 43 | 18 |
| A59 | 0000139 | 0 | 1 | 0 | 0 | 3 | 2 | 27 | 14 |
| A60 | 0000173 | 0 | 1 | 0 | 0 | 3 | 2 | 31 | 14 |
| A61 | 0000174 | 0 | 1 | 0 | 0 | 3 | 2 | 31 | 14 |
| A62 | 0000175 | 0 | 1 | 0 | 0 | 3 | 2 | 26 | 14 |
| A63 | 0000176 | 0 | 1 | 0 | 0 | 3 | 2 | 31 | 14 |
| A64 | 0000177 | 0 | 1 | 0 | 0 | 3 | 2 | 26 | 14 |
| A65 | 0000232 | 0 | 1 | 0 | 0 | 3 | 2 | 25 | 14 |
| A66 | 0000233 | 0 | 1 | 0 | 0 | 3 | 2 | 25 | 14 |
| A67 | 0000234 | 0 | 1 | 0 | 0 | 3 | 2 | 25 | 14 |
| A68 | 0000236 | 0 | 1 | 0 | 0 | 4 | 2 | 26 | 14 |
| A69 | 0000237 | 0 | 1 | 0 | 0 | 3 | 2 | 25 | 14 |
| A70 | 0000257 | 1 | 0 | 3 | 0 | 4 | 2 | 25 | 14 |
| B1 | 0000003 | 0 | 0 | 0 | 0 | 5 | 3 | 625 | 198 |
| B2 | 0000004 | 0 | 0 | 0 | 0 | 6 | 6 | 93 | 35 |
| B3 | 0000005 | 0 | 0 | 0 | 0 | 5 | 3 | 27 | 14 |
| B4 | 0000092 | 0 | 0 | 0 | 0 | 2 | 2 | 52 | 22 |
| B5 | 0000093 | 0 | 0 | 0 | 0 | 2 | 2 | 91 | 34 |
| B6 | 0000097 | 0 | 0 | 2 | 0 | 2 | 2 | 91 | 34 |
| B7 | 0000099 | 0 | 1 | 0 | 0 | 4 | 2 | 31 | 14 |
| B8 | 0000100 | 0 | 0 | 0 | 0 | 2 | 2 | 149 | 54 |
| B9 | 0000101 | 0 | 0 | 0 | 0 | 2 | 2 | 100 | 38 |
| B10 | 0000102 | 0 | 0 | 0 | 0 | 2 | 2 | 26 | 14 |
| B11 | 0000109 | 0 | 2 | 0 | 0 | 4 | 3 | 31 | 14 |
| B12 | 0000114 | 0 | 2 | 0 | 0 | 3 | 2 | 31 | 14 |
| B13 | 0000115 | 0 | 1 | 0 | 0 | 3 | 2 | 32 | 14 |
| B14 | 0000150 | 0 | 0 | 0 | 0 | 2 | 2 | 98 | 38 |
| B15 | 0000163 | 0 | 0 | 0 | 0 | 2 | 3 | 65 | 26 |
| B16 | 0000164 | 0 | 0 | 0 | 0 | 2 | 2 | 64 | 26 |
| B17 | 0000231 | 0 | 3 | 0 | 0 | 2 | 9 | 64 | 69 |
| B18 | 0000235 | 0 | 2 | 0 | 0 | 2 | 6 | 51 | 50 |
| B19 | 0000239 | 0 | 2 | 0 | 0 | 3 | 3 | 116 | 120 |
| B20 | 0000255 | 1 | 1 | 0 | 0 | 4 | 2 | 25 | 14 |
| B21 | 0000256 | 1 | 1 | 1 | 1 | 2 | 2 | 25 | 14 |

(Label counts above 1 for A7-A9, A26-A28, A41, B17, B18, B19 come from substring matches: e.g.
"elevated plus maze: open arm (north) - time" is a prefix of "... - time freezing"/"... - time
moving towards"; "C. elegans chemotaxis assay parameter" is a prefix of its children's labels;
B19's 2 NDI hits are prose in `+haley/import_V2_decisions.md` lines 37 and 275.)

### 2c. The NDI-matlab and DID-matlab sites, by what they do

Writers / readers **by node** (`git grep -n -P 'EMPTY[:_]0000(006|129|255|256|257|097)(?![0-9])' origin/V2`):

| repo | site | what | nodes |
|---|---|---|---|
| NDI | `src/ndi/+ndi/+setup/+conv/+haley/doImport.m:426` `ndi.ontology.lookup('EMPTY:0000129')` | v1 Haley import: looks the node up and writes its **definition** into `imageStack.label` | 129 |
| NDI | `src/ndi/+ndi/+setup/+conv/+babu/import.m:468` `ndi.ontology.lookup('EMPTY:0000257')` | v1 Babu import, same pattern | 257 |
| NDI | `src/ndi/+ndi/+setup/+conv/+babu/treatments.json:224-231` `"method_name": "C. elegans transfer method: M9 buffer wash"`, `"method_ontologyNode": "EMPTY:0000255"` (and titanium pick / 0000256) | v1 Babu treatment writer: writes node AND current label | 255, 256 |
| NDI | `tests/+ndi/+unittest/+migrate/TestMigrateLocalEta.m:557` `rawLabel(stack.id(), 'EMPTY:0000129')` | test fixture | 129 |
| NDI | `Francesconi_et_al_2025/1_getting_started.md:344`, `+dabrowska/tutorial_*.html:79`, `+haley/tutorial_*.html` | documentation / generated tutorial output | 006, 129 |
| DID | `tests/+did2/+unittest/testRawV1RoundTripImage.m` (11 lines: 20, 30, 132, 436, 459, 523, 535, 549, 552, 569, 576) | v1 fixtures modelled on the Haley/Babu writers | 129, 257 |
| DID | `tests/+did2/+unittest/testRawV1RoundTripPosition.m:197,217` `ontology_node_a = 'EMPTY:0000097'` | v1 fixture | 097 |
| DID | `tests/+did2/+unittest/testRawV1RoundTripTreatment.m:721-722` `'method_name', 'C. elegans transfer method: titanium pick'` / `'method_ontologyNode', 'EMPTY:0000256'` | v1 fixture | 256 |

Writers **by label** (case-insensitive label grep; every one is a v1 `tableDoc_dictionary.json`
mapping a column to `"EMPTY:<label>"`, which the import passes to `ndi.ontology.lookup`):

| dictionary (NDI-matlab origin/V2) | rows whose current label it names |
|---|---|
| `src/ndi/+ndi/+setup/+conv/+dabrowska/tableDoc_dictionary.json` | 56 rows: A1-A46, A48-A57 (all of tier A1-A57 except A47) |
| `src/ndi/+ndi/+setup/+conv/+hunsberger/tableDoc_dictionary.json` lines 8-12 | A60-A64 (BlockType, BlockMinute, CFCSeconds, CFCDuration, CFCFreezing) |
| `src/ndi/+ndi/+setup/+conv/+babu/tableDoc_dictionary.json` lines 3-7 | A65-A69 (mixture_table, odorVolume, duration, CI, speed) |
| `src/ndi/+ndi/+setup/+conv/+haley/tableDoc_dictionary.json` lines 3, 14-15, 24, 29-30, 42 | B7 (assayPhase), B11 (growthAge, age), B12 (growthTimePicked, timePicked), B13 (assayType), A59 (encounterNum) |

Command for the Dab count: `grep -l "dabrowska/tableDoc_dictionary" g53/hits/*_NDI_labeli.txt | wc -l` -> 56.
A47 (EMPTY:0000053, "fear-potentiated startle: baseline acoustic startle response amplitude"):
node grep 0 and label grep 0 in NDI-matlab origin/V2 (files `g53/hits/A47_NDI_node.txt`,
`A47_NDI_labeli.txt` are empty). No writer found by those two searches; that is not evidence
that no dataset holds it.

How a by-label lookup resolves (ndi-ontology-matlab `origin/main` 7b51308,
`src/ndi/+ndi/+ontology/EMPTY.m`): sources in order `OWL_URL_MAIN` (empty-ontology `main`
`empty-base.owl`), then `OWL_URL_V2_EDIT` (`V2/src/ontology/empty-edit.owl`), then V2's
`empty-base.owl`, then development; match is `strcmpi(thisId, fragment) || strcmpi(thisName, fragment)`
(lines 117, 163). So: (i) a relabel or obsoletion merged to empty-ontology `V2` does not change
what NDI's lookup returns until it reaches `main`'s release file (main is read first, and every
one of the 91 is on main with its current label); (ii) once it reaches main, every by-label
dictionary entry above stops resolving (`"obsolete " + label`, or the new label); a by-node lookup
keeps resolving (the node and, per conventions §6, the definition are kept).

The Haley **V2** import already writes the replacing terms for two rows, by node:
`src/ndi/+ndi/+setup/+conv/+haley/private/haleyTerm.m:56` `'video recording', 'NCIT:C91063'`
and `:199` `'developmental stage', 'NCIT:C43531'` (`git grep -n -F -e 'NCIT:C91063' -e 'NCIT:C43531' origin/V2 -- src`).
No V2 import in NDI-matlab origin/V2 writes CMO, MMO, NCIT:C25257, NCIT:C48167 or BAO:0010269:
`git grep -c -F '<curie>' origin/V2` printed nothing for each of `CMO:`, `MMO:`, `NCIT:C25257`,
`NCIT:C48167`, `BAO:0010269`.
There is no Dab, Babu or Hunsberger V2 importer file: `git ls-tree -r --name-only origin/V2 | grep -i V2 | grep -i -E 'dab|babu|hunsberg'`
lists only `+babu/import_V2_decisions.md` and `+dabrowska/V2_decisions.md` (decision logs). The
Dab V2 path today is the migration plus `ndi.migrate.internal.sliceTetanus` (`V2_decisions.md`
header); its EPM/FPS `ontologyTableRow` columns are drafted in did-schema
`docs/v2_working/DAB_COLUMN_ROWS_DRAFT.md` (header: "Every row below is Proposed (not decided)").

ndi-ontology-matlab: "PR #16 open" in the brief is out of date. `git log -4 origin/main` ->
`7b51308 2026-10-29 23:45:57 -0700 Merge pull request #16 from Waltham-Data-Science/claude/cmo-mmo-readers`
(over `087e000 Lookups for CMO and MMO`); `git ls-tree --name-only origin/main src/ndi/+ndi/+ontology/`
lists `CMO.m` and `MMO.m`, and also `AFO.m BAO.m NCIT.m OBI.m PATO.m SNOMED.m UO.m WBls.m`.
Its prefix for SNOMED is `SNOMED` (`ontology_list.json:78 {"prefix": "SNOMED", ...}`;
`git grep -n -i SNOMEDCT origin/main` finds only a URL comment in `SNOMED.m:9`), while
did-schema writes `SNOMEDCT` (CURIE registry `spelling: SNOMEDCT`, `SNOMED` listed as a synonym).
Whether `ndi.ontology.lookup('SNOMEDCT:252129004')` resolves was not tested (see Q14).

---

## 3. Build order (siblings first), PR-sized, per repository

Constraints applied (CLAUDE.md "Changes the siblings must follow land in the siblings first",
items 2 and 3; rule 4's `Build pending` / `Built:`):
- A reader that compares by label moves to the node **before** the label changes (item 3).
- A writer moves to the new node **before** the old node is obsoleted (item 2).
- Registry rows land with or before what writes them.
- R7 (`tools/check_term_registry.py` `check_empty`) compares each *registered* EMPTY row's name
  and definition with the empty-ontology checkout's `src/ontology/empty-edit.owl` (working tree of
  `$EMPTY_ONTOLOGY` or a sibling folder); an `obsolete` row also matches "obsolete " + name. None
  of the 91 is registered today (2a), so obsoleting/relabelling in empty-ontology breaks no
  existing did-schema row. A NEW registry row for a relabelled EMPTY term must carry the new label
  and new definition, so it can only pass R7 against a checkout that already has the relabel:
  the empty-ontology PR merges first and the registry row lands right after (or both PRs are
  checked against the empty-ontology branch). CI reports R7 NOT CHECKED (CLAUDE.md §3), so this
  ordering is enforced only by a local `tools/gates.py` run.

Step order (each step one PR unless noted):

**Step 1. did-schema: register the existing-ontology replacement terms** (no EMPTY rows yet).
The 33 rows in §5 table 5a (CMO, MMO, PATO direction, NCIT, AFO, OBI, BAO, SNOMEDCT, ...), each
with its ontology's label and definition. They break nothing (no reader), and they must exist
before any import writes them (did2.build's `TermRegistry` mode refuses an unregistered term).
Run `tools/gates.py`; R4 checks prefixes (all ten prefixes are already in
`CURIE_lookups_meta.json`: CMO and MMO added in 0983b84). Record nothing as Built for imports.
Same PR may change the six lines' `ndi-ontology-matlab (CMO and MMO readers)` to
`Built: ndi-ontology-matlab 7b51308` (positive evidence in 2c), if the team agrees.

**Step 2. NDI-matlab: by-label readers move to node** (siblings-first item 3), one PR:
- `+dabrowska/tableDoc_dictionary.json` (56 entries), `+hunsberger/tableDoc_dictionary.json`
  (5), `+babu/tableDoc_dictionary.json` (5), `+haley/tableDoc_dictionary.json` (7 entries, 5 rows):
  replace `"EMPTY:<label>"` with `"EMPTY:00000nn"` (EMPTY.m matches id or name, so the v1 import
  output is unchanged: same node, same label, same definition while main is unchanged).
- `+babu/treatments.json` `method_name` for 255/256: decide whether the v1 writer keeps writing
  the old label text (Q10).
- Must merge **before** the empty-ontology change reaches empty-ontology `main` (not before it
  reaches `V2`; 2c (i)). Whether it is needed at all depends on Q9.

**Step 3. NDI-matlab and DID-matlab: the EMPTY:0000129 / 0000256 / 0000257 "readers first"**
(b5, b6 Build pending). Positive findings: NDI's two `src` sites (haley `doImport.m:426`, babu
`import.m:468`) look up by **node** and write the definition; obsoleting keeps node and
definition (conventions §6), so they do not break. DID-matlab has **no** `src` reader of 129/256/
257 (`git grep ... -- src` exit 1); its hits are v1 fixtures, which stay valid v1 input. What
"readers first" should change is therefore not settled by the code (Q8). Candidate PRs:
- NDI-matlab: the V2 path that turns a v1 `ontologyLabel`/`imageStack` carrying 129/257 into
  NCIT:C91063 (none exists today: carried, `ontologyLabel` is a GUARDED PASSTHROUGH per the
  coverage ledger row);
- DID-matlab: nothing in `src`; the fixtures need no change unless a mapping is added.

**Step 4. empty-ontology (`V2`): relabels and obsoletes**, one PR (or one per batch):
- 28 relabels (or fewer, Q1) with a new general definition each (Q4), the old label kept as an
  `OMO:0003008` previous-name synonym (conventions §4: every one of the 91 labels is in the
  released `main`), and a comment citing the batch tag (§5).
- Obsoletes: `owl:deprecated true`, "obsolete " label prefix, `oboInOwl:consider` per
  replacement (Q3), comment "Obsolete: replaced by *label* (*id*); ...", keep the definition,
  drop superclasses and synonyms (conventions §6).
- Re-parent what loses its parent: relabelled children of obsoleted parents (A52 under B2;
  EMPTY:0000292 "encounter type" under B13) and, if Q2 says so, the generalised relabels under B1.
- Grouping classes: obsolete only those left with no live child (Q5). Applying the rule
  mechanically to today's hierarchy, assuming relabelled terms keep their parents: obsolete B15,
  B16, B17, then B9 (115 and 231 obsolete), B3 (no children), B10 and B14 (no children now);
  B6 depends on B9 and B10 (then obsolete); keep B1, B4, B5, B18 (relabelled children), B8
  (0000274), B19 (7 strains).
- Every obsoleted node is already safe for the two NDI by-node readers (Step 3).
- Lands on `V2` only; NDI sees it after the next `main` release (2c). Step 2 must precede that release.

**Step 5. did-schema: EMPTY registry rows for the relabelled terms that a V2 import writes**,
immediately after Step 4 merges (R7 against the V2 checkout). Rows from table 5b. Only the
relabels some import will write need rows; b6 says "registry rows, with the Dab and Haley
imports that write them", so these may instead ride with Step 6's import PRs, as long as each
lands no later than its writer. Obsoleted EMPTY nodes need no row (no V2 writer; R10 `obsolete:
{consider}` is for "a term the ontology made obsolete, kept while something still writes it").

**Step 6. NDI-matlab: the per-dataset V2 imports that write the new terms** (one PR per dataset):
- Dab ("applied by the Dab import ([migration not generalizable])"): EPM/FPS/ASR rows -> the
  variables, MMO location / PATO direction conditions, method MMO:0000262; A49 chamber as a device
  entity; A57 SNOMEDCT. Needs the DAB_COLUMN_ROWS draft decided (it is Proposed).
- Haley: A59 "encounter identifier", B7 Phase, B11 (already NCIT:C43531 in `haleyTerm.m`), B12
  transfer manipulation, B13 -> study entity, A58 (already NCIT:C91063 in `haleyTerm.m:56`).
- Babu (A65-A70, B20, B21) and Hunsberger (A60-A64): their v1 dictionaries write these terms
  (2c), but the decision lines name only "the Dab and Haley imports" (Q7).

**Step 7. did-schema: close the lines.** For each repository, change the six lines'
`Build pending: <repo> (...)` to `Built: <repo> <commit>` in the same or next did-schema PR
(rule 4). The authored flag sentence "JH's 7,007 are EMPTY:0000129-133" in
`schemas/generated/did_v2_migration_targets.json` (and the generated ledger) describes v1 data and stays true.

---

## 4. AMBIGUITIES (questions for the team; not resolved here)

**Q1. Several nodes, one label.** b2, b3, b4 and b5 relabel 7 nodes each to the same three labels:
"number of head entries into a discrete space" (0000009, 0000010, 0000011, 0000028, 0000029,
0000030, 0000045), "latency to first entry into a discrete space" (0000016-0000018,
0000035-0000037, 0000048), "time spent moving towards a discrete space" (0000019-0000021,
0000038-0000040, 0000049). b2 says "the EMPTY term is relabelled" (singular) while naming three.
R2 (`check_term_registry.py`: "two entries with the same name, ignoring case, spaces, underscores
and hyphens") fails on two registry rows with one name, and an ontology with seven classes of one
label breaks label lookup (EMPTY.m returns the first match). Options: (a) relabel one node per
label (which: the lowest, 0000009 / 0000016 / 0000019?) and obsolete the other six with `consider`
it; (b) relabel all seven, register only one; (c) mint one new general term per label and
obsolete all 21.

**Q2. Parents of a generalised relabel.** The relabelled A-terms keep `SubClassOf EMPTY:0000003`
"elevated plus maze measurement" (and 0000090 / 0000091). A general label under an assay-named
parent contradicts the relabel. Options: (a) keep the parents; (b) move them under the general
parents only (EMPTY:0000002 "behavioral measurement", 0000090 "duration", 0000091 "timepoint");
(c) other. The answer decides whether B1, B4, B5, B18 keep a child (Q5).

**Q3. What `consider` lists.** Conventions §6: "`oboInOwl:consider` for each replacement term".
For A1 is that CMO:0000960 only, or CMO:0000960 + MMO:0000266 + PATO:0045091 + MMO:0000262?
b3-b5 write "->" without "obsolete": confirm every "-> <existing term>" row is an obsoletion.

**Q4. Definitions for the relabels.** b2 "with a general definition", b6 "relabels with general
definitions"; no definition text is given for any of the 10 new labels. Options: (a) Claude drafts
from the current definitions with the assay and units stripped (conventions §3: no units), for
approval; (b) the team writes them. R7 needs the registry definition to equal the ontology's.

**Q5. "Made obsolete once no child remains".** (i) Does "child" mean a live (non-obsolete) child?
(ii) B10 (0000102) and B14 (0000150) have no children on V2 today: obsolete now? (iii) With what
`consider` (convention requires one; there is no replacing term for a grouping class)? (iv) Does
the rule cascade (B17 -> B9 -> B6)? (v) B6 0000097 is used as a v1 fixture value in DID-matlab
`testRawV1RoundTripPosition.m:197,217`: no impact expected (v1 value), confirm.

**Q6. Children of obsoleted non-grouping terms.** B13 (0000115) has child EMPTY:0000292 "encounter
type" (not in the 91); B2 (0000004) has A52's 0000062 (relabelled, live). New parents for both?

**Q7. Which imports.** b5/b6 Build pending name "the Dab and Haley imports". The v1 writers of
A60-A64 are Hunsberger's dictionary and of A65-A69, B20, B21 are Babu's (2c). Are the Babu and
Hunsberger V2 imports in scope, and should the lines name them?

**Q8. What "EMPTY:0000129 / 0000256 / 0000257 readers first" requires.** NDI `src` reads 129 and
257 by node (definition copied into `imageStack.label`); DID-matlab `src` has no reader (grep exit
1, tests only). Options: (a) no reader change is needed, because node and definition survive
obsoletion; the line becomes `Built:` with that evidence; (b) the v1 writers (Haley `doImport.m`,
Babu `import.m`, `treatments.json`) move to NCIT:C91063 / the new labels (that changes what new
v1 imports write); (c) a V2 mapping (NDI second pass or DID migrator) of v1 labels 129/257 to
NCIT:C91063 is the "reader" meant.

**Q9. v1 dictionaries' by-label lookups.** 73 dictionary entries look terms up by label (2c).
Should they move to nodes (Step 2) before the empty-ontology change is released to `main`, or are
the v1 importers frozen ("The existing `doImport.m` is left unchanged", Dab `V2_decisions.md`)?

**Q10. Babu `treatments.json` writes `method_name` = the old label of 255/256 with the node.**
After the relabel the written name and the ontology label differ. Keep (v1 data as written), or
change the writer to the new label?

**Q11. Obsoleted terms with no replacing term.** A49 (0000058: "no variable", chamber is a device
entity), A61 (0000174: the statement's time), B12 (0000114: a transfer manipulation, NCIT:C48167),
A65 (0000232: a `formulation` document; variable NCIT:C45305), B13 (0000115: "consider the Haley
study entity"). Obsolete all five? With which `consider` CURIE: none / NCIT:C48167 for B12 /
NCIT:C45305 for A65 / UO:0000031 for A61? An entity is not a term, so what does B13's
`consider` hold (a CURIE string is the convention)?

**Q12. Replaced registry rows: obsolete-marked or deleted?** Moot today for the 91: none is in the
registry (2a, exit 1). R10 allows `obsolete: {consider: <node>}` only for "a term the ontology made
obsolete, kept while something still writes it". Question for later: if a V2 import ever writes
one of the obsoleted nodes, is it registered with `obsolete`, or refused?

**Q13. Open method terms.** b5: "Open: ... the method terms of A47-A49, A56 (fear-potentiated
startle: no term exists) and A50-A55 (acoustic startle: OBI:0003710 only if recorded in an
anechoic chamber)". b6 settles A46 and A59 but says nothing on these methods. Still open? Also A47's
"baseline phase condition": which term is the value (NCIT:C25257 Phase as variable; baseline as
what node)?

**Q14. Unit and spelling clashes in the registry.**
(a) A61's "minutes (UO:0000031)": the registry already holds `om:minute-Time` named "minute";
registering UO:0000031 "minute" fails R2. Use `om:minute-Time` (OM is the unit default; UO is
registered "for one unit OM lacks: pH"), or register UO:0000031 under another name?
(b) A57 SNOMEDCT:252129004: ndi-ontology-matlab's prefix is `SNOMED`; does `SNOMEDCT:` resolve in
`ndi.ontology.lookup`? (not tested). Also b5: "SNOMED gives no definition": R5 requires a
definition only for EMPTY and staged rows, so a SNOMEDCT row may carry none; confirm.
(c) NCIT:C25330 "Duration" (A63, A67) vs live EMPTY:0000090 "duration" (parent of many EMPTY
terms); NCIT:C70831 "Amplitude" (A55) vs live EMPTY:0000162 "amplitude"; CMO:0001519 vs B2's own
label. Not registry clashes (neither EMPTY term is registered), but T19 duplicates in the
ontology: obsolete EMPTY:0000090 / 0000162 too? (Not in the decision lines.)

**Q15. Location/direction for the "total" rows.** b1 gives A3 (open arm total) only a variable and
method; b3 A10, A22 likewise; b4 says location MMO:0000265 "throughout" (so A28, A29 get it). Do A3,
A9, A10, A22 carry location MMO:0000266 / MMO:0000265? And the "total" relabel rows (A6, A13, A16,
A25, A32, A35) get the location with "none" direction: confirm "none" means no direction condition.

**Q16. B11 values "from WBls"** and A60's "the block's kind as a term value": no value terms are
named. A closed `values` list in `binding_registry_meta.json`, or any WBls term?

---

## 5. New registry rows needed

Checked against `schemas/registry/did_v2_term_registry.json` at did-schema HEAD (914 rows): by node (exact,
case-insensitive), by node suffix, and by name/synonym with R2's normalisation (lower case, spaces,
`_` and `-` removed). Script output: every CURIE below "NOT IN REGISTRY" except the four marked;
name clashes only where noted.

Already registered (no new row): EMPTY:0000349 "peak amplitude", NCIT:C91063 "Video Recording",
PATO:0000008 "speed", NCIT:C43531 "Developmental Stage" (each `decided`, `obsolete: False`).

### 5a. Existing-ontology terms (definition source: the ontology, via OLS4; the decision lines give labels only)

| node | label (as in the decision line) | used by | clash |
|---|---|---|---|
| CMO:0000960 | number of entries into a discrete space in an experimental apparatus | A1, A2, A20, A21, A39 | none |
| CMO:0004010 | number of entries into an open arm of an elevated plus maze | A3 | none |
| CMO:0000958 | amount of experiment time spent in a discrete space in an experimental apparatus | A7, A8, A26, A27, A41 | none |
| CMO:0004014 | total amount of experiment time spent in the open arms of an elevated plus maze | A9 | none |
| CMO:0004075 | ratio of time spent in the open arms to total test time in an elevated plus maze | A10 | none |
| CMO:0001043 | amount of time spent in voluntary immobility | A17-A19, A36-A38, A45, A62 | none |
| CMO:0004009 | number of entries into an enclosed arm of an elevated plus maze | A22 | none |
| CMO:0004012 | total amount of experiment time spent in an enclosed arm of an elevated plus maze | A28 | none |
| CMO:0000959 | percentage of experiment time spent in a discrete space in an experimental apparatus | A29, A42 | none |
| CMO:0001520 | amplitude of the acoustic startle response | A47 | none |
| CMO:0001044 | percent of time spent in voluntary immobility | A64 | none |
| CMO:0001519 | acoustic startle response measurement | B2 (grouping; only if something writes it) | same label as EMPTY:0000004 in the ontology (not registered) |
| CMO:0002046 | calculated acoustic startle response measurement | B3 (grouping; only if written) | none |
| MMO:0000262 | elevated plus maze apparatus method | A1-A46, A57 | none |
| MMO:0000263 | center of elevated plus maze apparatus | A39-A45 | none |
| MMO:0000265 | enclosed arm of elevated plus maze apparatus | A20, A21, A23-A38 | none (EMPTY:0000265 "S basal" shares only the digits) |
| MMO:0000266 | open arm of elevated plus maze apparatus | A1, A2, A4-A8, A11-A19 | none (EMPTY:0000266 "S medium" shares only the digits) |
| MMO:0000572 | contextual fear conditioning test | A60-A64 | none |
| PATO:0045091 | north | A1, A4, A7, A11, A14, A17 | none (registry "North Korea"/"North Macedonia" are different normalised names) |
| PATO:0045093 | south | A2, A5, A8, A12, A15, A18 | none |
| PATO:0045094 | west | A20, A23, A26, A30, A33, A36 | none |
| PATO:0045092 | east | A21, A24, A27, A31, A34, A37 | none |
| AFO:AFR_0000956 | number of sampled points | A50 | none |
| NCIT:C142234 | Digital Sampling Rate | A51 | none |
| NCIT:C156560 | Peak Response Amplitude Latency | A54 | none |
| NCIT:C70831 | Amplitude | A55 | none in registry (Q14c) |
| OBI:0200079 | arithmetic mean calculation | A55, A69 | none (registry has NCIT:C53319 "Arithmetic Mean", a different name) |
| NCIT:C25257 | Phase | A56, B7 (and A47's condition?) | none |
| SNOMEDCT:252129004 | Test duration | A57 | none; no SNOMEDCT row exists yet (Q14b) |
| NCIT:C86947 | Block | A60 | none |
| NCIT:C25330 | Duration | A63, A67 | none in registry (Q14c) |
| NCIT:C45305 | Mixture | A65 | none |
| NCIT:C25335 | Volume | A66 | none |
| BAO:0010269 | chemotaxis assay | A65-A70 | none |
| NCIT:C48167 | Transfer | B12 | none |
| UO:0000031 | minute | A61 | **R2 clash** with `om:minute-Time` "minute" (Q14a) |
| OBI:0003710 | (anechoic chamber assay, conditional) | A50-A55, only if decided | not decided (Q13) |

33 unconditional rows (CMO 11, MMO 5, PATO 4, NCIT 9, AFO 1, OBI 1, BAO 1, SNOMEDCT 1, counted
without CMO:0001519, CMO:0002046, UO:0000031 and OBI:0003710, which wait on Q5/Q14/Q13).

### 5b. EMPTY terms kept and relabelled (definition source: the empty-ontology relabel PR, Q4; R7 must match)

| node(s) | new label | written by | clash |
|---|---|---|---|
| one of 0000009/10/11/28/29/30/45 (Q1) | number of head entries into a discrete space | Dab | none |
| one of 0000016/17/18/35/36/37/48 (Q1) | latency to first entry into a discrete space | Dab | none |
| one of 0000019/20/21/38/39/40/49 (Q1) | time spent moving towards a discrete space | Dab | none |
| 0000051 | test identifier | Dab (and Haley, b6) | none |
| 0000057 | trial type | Dab | none |
| 0000062 | amplitude at analysis window onset | Dab | none |
| 0000139 | encounter identifier | Haley (and Dab, b6) | none |
| 0000236 | McCutcheon index | Babu (Q7) | none |
| 0000255 | M9 buffer wash transfer | Babu (Q7) | none |
| 0000256 | pick transfer | Babu (Q7) | none |

Name checks (R2 normalisation) against the registry and against every EMPTY label in
`origin/V2:src/ontology/empty-edit.owl`: all ten new labels -> no registry clash, no existing EMPTY
label clash (script output in this session: "registry name/synonym clash: None | owl EMPTY label
clash: None" for each).
