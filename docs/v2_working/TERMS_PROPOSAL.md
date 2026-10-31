# Terms for four decisions: proposal (research only, nothing decided)

Every term below is **Proposed (not decided)**. Nothing was written to any repository.
Scratch files in this folder: `batch.json` (the 244-row batch), `propose_out.txt` (the full
`propose_terms.py` output, 1609 lines), `openminds_values.tsv` (all 231 openMINDS values with
their verdicts), `tech.json` / `sdt.json` (the parsed openMINDS files), `ols*.txt` (OLS answers).

## Denominators (first)

| what | count | source |
|---|---|---|
| did-schema HEAD | 77cf59e "Record [clock terms get nodes]" | `git log --oneline -1` |
| term registry entries | 624 (1 with node "") | `schemas/registry/did_v2_term_registry.json` `terms` |
| CURIE registry prefixes | 55 | `schemas/V_eta/stable/CURIE_lookups_meta.json` |
| EMPTY ids allocated | EMPTY:0000001-0000398, none free below 399 | empty-ontology `V2` 2dc90d4 (= `origin/V2`), `src/ontology/empty-edit.owl`, `docs/conventions.md` rule 7 |
| openMINDS `technique` instances | 227 | openMINDS_instances main 3750716 (2026-10-21), `instances/latest/terminologies/technique/*.jsonld` |
| openMINDS `semanticDataType` instances | 4 | same commit, `.../semanticDataType/*.jsonld` |
| batch rows run through `propose_terms.py` | 244 (A 5, B 2+227+4, C 2, D 4) | `batch.json` |
| NDI v1 truth | NDI-matlab locked `main` 3cb19a85 (`tools/sibling_lock.json`) | `git show 3cb19a85:...` |

Hosts: OLS4 (`www.ebi.ac.uk/ols4/api/search`) reachable; GitHub API (`gh api`) **refused** for
openMINDS_instances ("GitHub access to this repository is not enabled for this session"), so I
used `git clone --depth 1 --filter=blob:none --sparse` over the git proxy, which worked;
Wikidata API reachable (one HTTP 429, then fine).

## `propose_terms.py` result (whole batch)

Command (run with the empty-ontology checkout so R7 is checked):

    EMPTY_ONTOLOGY=<scratch>/sib/empty-ontology python3 tools/propose_terms.py batch.json \
        --decided "PROPOSED (not decided)" --first-used-in "drop census terms"   # exit 1

    DENOMINATOR: 244 row(s) read from .../terms/batch.json; 624 registered term(s); 55 CURIE prefix(es); empty-ontology read from .../sib/empty-ontology/src/ontology/empty-edit.owl
    SUMMARY: 0 REGISTERED, 1 USE REGISTRY, 151 ADD, 94 FAIL

(151 + 94 + 1 = 246: two FAILs are batch-level R1 lines, not rows.) Verdicts for every
non-technique row, pasted:

    ADD          "database ingestion" (no node): row printed (staged: its node is still to be found or minted)
    ADD          "database linking" (no node): row printed (staged: ...)
    FAIL         "data ingestion" T4FS:0000290: R4 the CURIE registry does not know the prefix 'T4FS': add it (...CURIE_lookups_meta.json, with a `spelling`; ndi-ontology-matlab for lookups) before the term
    ADD          "software class" (no node): row printed (staged: ...)
    ADD          "Pathname" NCIT:C47922: row printed
    ADD          "Technique" NCIT:C16847: row printed
    ADD          "Scientific Data Type" NCIT:C175886: row printed
    ADD          "Range" NCIT:C38013: row printed
    ADD          "value range" (no node): row printed (staged: ...)
    ADD          "UTC" wikidata:Q1536: row printed (no definition given: the registry carries the ontology's)
    ADD          "device local time" (no node): row printed (staged: ...)
    ADD          "device global time" (no node): row printed (staged: ...)
    ADD          "experiment global time" (no node): row printed (staged: ...)
    FAIL         "derived data" / "experimental data" / "raw data" / "simulated data" (no node): R5 no node and no definition: find an ontology term or mint an EMPTY one, or give a definition to register it staged

Technique rows (227), tallied from the output (`openminds_values.tsv` has each one):

| verdict | n | why |
|---|---|---|
| ADD with a node | 32 | 26 ILX, 3 OBI, 3 EDAM (see note) |
| ADD staged (no node, openMINDS gives a definition) | 105 | needs an EMPTY id each |
| USE REGISTRY | 1 | "video tracking" is already EMPTY:0000301 under that name |
| FAIL R5 (no node, no definition in openMINDS) | 73 | |
| FAIL R4 prefix `MESH` unknown | 12 | |
| FAIL R4 prefix `CHMO` unknown | 1 | "fluorescence microscopy" CHMO:0000087 |
| FAIL R2 | 1 | "brightfield microscopy" ILX:0739719: the name is registered for NCIT:C19827 |
| FAIL R1 (batch) | 2 | two openMINDS terms share one node (below) |

Note: 48 technique values carry a `preferredOntologyIdentifier`: 29 InterLex, 12 MeSH, 3 OBI,
3 EDAM, 1 CHMO. Of the 29 ILX: 1 is the brightfield R2 clash, and 2 duplicate another's node,
leaving 26 clean ILX + 3 OBI + 3 EDAM = 32 clean ADDs, and the 2 duplicate rows were printed
but fail the batch check. 179 values have no identifier.

**The rows printed carry `"status": "decided"` with my `decided` text "PROPOSED (not decided)".
They are not to be pasted as they stand**: a team decision fills `decided`.

---

## A. [session membership records linked or ingested]

Decision text: `V_eta_go_forward_class_audit.md` line 1180 (grep the tag). v1 meaning, read at
NDI `main` 3cb19a85:
- `session_in_a_dataset.json` holds `is_linked`, `session_creator`, `session_creator_input1..6`.
- `dataset.m` add_linked_session sets `is_linked = 1`, `session_creator = class(ndi_session_obj)`,
  inputs from `creator_args()`; add_ingested_session sets `is_linked = 0` and blanks input2
  ("same relative path").
- `+session/dir.m` `creator_args`: `inputs{1} = reference; inputs{2} = getpath(); inputs{3} = id()`.
  So input1 and input3 restate reference and id (dropped as copies per the decision); input2 is
  the path.

**Method terms.** OLS searches (`olsA.txt`): data ingestion, ingest, data import, linked data,
data linking, data import process, database import, database link, database federation, data
virtualization, pointer, hyperlink, data copying, data transfer, external data reference.

| value | proposal | node | source / read from | note |
|---|---|---|---|---|
| ingested | **database ingestion** (EMPTY, new) | — (next free would be EMPTY:0000399+) | OLS4 search above | Definition: "A process in which the records held in one database are copied into another database, which thereafter holds them itself." |
| ingested (alternative) | data ingestion | T4FS:0000290 | `ols4/api/ontologies/t4fs/terms?obo_id=T4FS:0000290` | "Process of obtaining, importing, and processing data for later use or storage in a database. ..." Close, but includes processing/reformatting and is a food-safety ontology; prefix `T4FS` not in the CURIE registry (R4 FAIL). Team choice. |
| linked | **database linking** (EMPTY, new) | — | OLS4 searches above | Definition: "A process in which one database records a reference to another database stored elsewhere, whose records stay where they are and are read from there." Near misses: T4FS:0000423 data linkage and NCIT:C15424 Record Linkage Study mean record linkage of the same individual; NCIT:C48909 Pointer is an address, not a process. |

**Parameter variables** (`method.parameters` of a linked session):

| variable | proposal | node | read from | note |
|---|---|---|---|---|
| opener class (`session_creator`, e.g. `ndi.session.dir`) | **software class** (EMPTY, new) | — | OLS4: class name, constructor, object class, SWO `class` | Definition: "A class defined in a software library, named by its fully qualified name, whose constructor creates an object from a list of arguments." NCIT:C41106 Object Class is a data-modelling notion (ISO 11179), IAO:0000421 named class expression is OWL; neither names a code class. |
| session path (`session_creator_input2`) | **Pathname** | NCIT:C47922 | `ols4/api/ontologies/ncit/terms?obo_id=NCIT:C47922` | "The specification of a node (file or directory) in a hierarchical file system, usually specified by listing the nodes top-down." Existing term; T19 fits. (AFO "file path" also exists; AFO prefix not registered.) |

Unresolved for the team: whether other `creator_args` inputs (4-6) of other session classes need
variables; at `main`, `ndi.session.dir` uses only 3 (`dir.m` above). Not measured for other classes.

## B. [dataset form terms]

Decision text: line 1182. Precedent read: registry row `experimental approach` EMPTY:0000356
(definition "The general kind of scientific approach used to produce the data, ...", decided
"Jess Haley, 2026-10-21 (binding variables)"); owl comment says NCIT Research Technique
(C20368) was rejected as "narrower (behavior is not a lab technique)";
`V_eta_term_registry_plan.md` closed-value-sets table row: 40 openMINDS values by
`preferredOntologyIdentifier`, EMPTY:0000360-0000364 minted for the 5 with none.

**Variables** (OLS `olsB.txt`):

| variable | proposal | node | definition (from OLS) | alternatives seen |
|---|---|---|---|---|
| technique | **Technique** | NCIT:C16847 | "A practiced and regimented skill or series of actions." | NCIT:C20368 Research Technique ("Technique used in the laboratory for scientific research."): openMINDS techniques include non-laboratory ones (eye movement tracking, standardization, 3D computer graphic modeling), the same reason C20368 was rejected for experimental approach. ERO:0000007 technique (prefix not registered). |
| data type | **Scientific Data Type** | NCIT:C175886 | "The category of scientific data generated from an experiment or a study and/or recorded in a document or file." | NCIT:C42645 Data Type is the programming sense (string, integer): wrong. |

So no EMPTY variable is needed for B, unlike experimental approach.

**Closed value list: technique (227 values).** Full list with @id, identifier, CURIE and verdict:
`openminds_values.tsv`. Facts the team must decide on:
1. **179 of 227 have no `preferredOntologyIdentifier`.** By the experimental-approach precedent
   each would get an EMPTY id: 178 mints (one, "video tracking", is already EMPTY:0000301). Of
   the 179, 74 have no openMINDS `definition` (152 of 227 have one; "video tracking" is one of
   the 74 and is already registered), so **73 new terms would need definitions written**. Experimental approach
   needed 5 mints (EMPTY:0000360-0000364).
2. **Two identifiers are shared by two openMINDS terms**: ILX:0107265 = "Timm's staining" and
   "myelin staining"; ILX:0739494 = "differential interference contrast microscopy" and
   "infrared differential interference contrast video microscopy". The registry allows one
   entry per node (R1), so one of each pair needs another node.
3. **"brightfield microscopy"**: openMINDS gives ILX:0739719; the registry already holds the
   name for NCIT:C19827 (Haley import). R2: reuse NCIT:C19827 or not.
4. **12 MeSH and 1 CHMO identifiers** need new CURIE-registry prefixes (`mesh`, `chmo`). The MeSH
   values are written as `http://id.nlm.nih.gov/mesh/2018/M0512939` etc.: MeSH *concept* ids
   (`M...`) under a 2018 version path, not descriptor ids (`D...`). As given; not checked against
   current MeSH.
5. ILX IRIs come in two forms (`uri.interlex.org/base/ilx_N` and `uri.interlex.org/ilx_N`); both
   were written `ILX:N`, as the registry's 34 existing ILX rows are.
6. NDI's form stores techniques as `"name (SchemaName)"` and builds
   `openminds.controlledterms.<SchemaName>(name)` (`convertFormDataToDocuments.m`
   `convertTechnique`, NDI `main` 3cb19a85), so a form value may come from another openMINDS
   term set than `technique`; under the decision such a value carries the form whole as v1.
   Which other schema names occur is not measured.

**Closed value list: semantic data type (4 values).** None has a `preferredOntologyIdentifier`
and none has a `definition` in openMINDS (all fields null; e.g. `derivedData.jsonld`):

| name | openMINDS @id | identifier | existing ontology term seen (OLS) |
|---|---|---|---|
| derived data | `.../semanticDataType/derivedData` | none | none fits (NCIT:C41091 Derived Data Element is ISO 11179) |
| experimental data | `.../experimentalData` | none | EDAM:data_3108 "Experimental measurement" ("Raw data such as measurements ... from laboratory experiments") overlaps raw data; not proposed |
| raw data | `.../rawData` | none | NCIT:C142663 Raw Data, "The original information, collected from the primary source." Fits under T19 |
| simulated data | `.../simulatedData` | none | none fits (EDAM simulation terms are molecular) |

Proposal: raw data = NCIT:C142663 (existing term, T19); the other three EMPTY, with
definitions to be written (openMINDS gives none). Alternatively all four EMPTY, as the
experimental-approach precedent did without looking for other ontologies. Team choice.

**`derivedData`:** it matches the openMINDS semanticDataType instance
`https://openminds.om-i.org/instances/semanticDataType/derivedData` (name "derived data"), the
id NDI's `openminds.controlledterms.SemanticDataType(value)` resolves
(`convertFormDataToDocuments.m`: `datasetVersion.dataType = cellfun(@(value)
openminds.controlledterms.SemanticDataType(value), appUserData.DataType)`). The string
`derivedData` occurs nowhere in NDI-matlab `main` 3cb19a85 or V2 HEAD (`git grep -n derivedData`
returned nothing), so I cannot confirm from code that the form writes exactly that string.

## C. [image file details placed]

Decision text: line 1194. OLS searches (`olsC.txt`): value range, data range, range of values,
dynamic range, minimum and maximum value, intensity range, pixel value range; `range` within
STATO, SIO, OBI, NCIT, IAO; NCIT "Value Range", "Limits", "Lower and Upper Limit".

| proposal | node | definition | assessment |
|---|---|---|---|
| **Range** (existing) | NCIT:C38013 | "The difference between the lowest and highest numerical values; the limits or scale of variation." | Second sense ("the limits") is [min max]; first sense is a scalar difference. Usable only if the team reads it as the limits. |
| **value range** (EMPTY, new; recommended if C38013 is rejected) | — | "The lowest and highest values that the values of a data body may take, given as a pair [minimum maximum]." | |

Rejected: STATO:0000035 range (a measure of variation, a difference: scalar); NCIT:C94889
Dynamic Range (difference or ratio of an instrument's highest and lowest value); NCIT:C71474
Reference Range (interpretation of clinical results); LABO:0000135 (prefix not registered, a
value specification). T19 note: label "value range" names no image, since the body carries that.

## D. [clock terms get nodes]

Decision text: line 1216. Meaning read from NDI `src/ndi/+ndi/+time/clocktype.m` (V2 head
f27302632): `utc` "Universal coordinated time (within 0.1ms)"; `exp_global_time` "Experiment
global time (within 0.1ms)"; `dev_global_time` "A device keeps its own global time ... (that is,
it knows its own clock across recording epochs)"; `dev_local_time` "A device keeps its own local
time only within epochs".

**Staged nodes today:** none minted anywhere.
- Registry: `grep -n -i 'clock\|utc' schemas/registry/did_v2_term_registry.json` gives 1 line, an unrelated
  definition (line 4578); no clock term.
- empty-ontology `V2` `empty-edit.owl`: no label or definition naming a clock (grep `clock|utc`
  matched only the licence comment and unrelated text).
- Schemas: `node: ""` for all four in `relative_time_reference.json` (`value.clock`, binding
  root `did_clocktype`, strength required) and in `draft/clock_alignment_configuration.json`;
  `tools/check_empty_ontology_nodes.py` counts them in its baseline ("did_clocktype 8": four
  terms x two carriers), and says NDIC.txt left NDI-matlab in 2c19bf24c.

| value | proposal | node | read from | definition (EMPTY only) |
|---|---|---|---|---|
| utc | **UTC** (existing) | wikidata:Q1536 | Wikidata `wbsearchentities` "Coordinated Universal Time": `Q1536 \| UTC \| principal time standard that underlies civil times on Earth` | — |
| dev_local_time | **device local time** (EMPTY) | — | OLS: clock time, device clock, local time, system clock, global time, time scale | "A time scale kept by a recording device that runs only within one recording epoch, so that times on it cannot be compared across epochs." |
| dev_global_time | **device global time** (EMPTY) | — | same | "A time scale kept by a recording device that runs continuously across its recording epochs, so that times on it can be compared across those epochs of that device." |
| exp_global_time | **experiment global time** (EMPTY) | — | same | "A time scale shared by all the devices of an experiment, to which their own clocks are aligned, so that times from different devices can be compared." |

UTC alternatives: Common Core Ontologies `https://www.commoncoreontologies.org/ont00001537`
"Coordinated Universal Time" (seen only as an import in OLS `rbo`/`slso`,
`is_defining_ontology` False; prefix not registered). NCIT has only zone times relative to UTC
(C116256...). `wikidata` is already a registered prefix with 215 terms. Near misses for the
device clocks: NCIT:C207913 Clock Device Time ("A representation of time as measured by a clock
device, e.g., 12:30PM.") does not separate local / device-global / experiment-global.

Two consequences to flag (not resolved here):
1. The registry stores the ontology's label, so `utc` would be stored as **"UTC"**. The binding's
   value names today are `utc`, `dev_local_time`, ...; CLAUDE.md §3 rule 3 ("a name that code
   compares": code compares by node first, then the stored name changes) applies, so DID-matlab
   and NDI comparisons of `clock.name` must move to the node before the names change.
2. The `approx_*` variants, `no_time` and `inherited` stay out (the schema documentation says
   they de-encode elsewhere); no terms proposed for them.

## Count of new EMPTY ids this proposal would need

| decision | EMPTY mints |
|---|---|
| A | 3 (database ingestion, database linking, software class); 2 if T4FS:0000290 is taken |
| B variables | 0 |
| B technique values | 178 (179 without identifier, minus video tracking) plus any replacement for the 2 shared nodes |
| B data types | 3 (4 if raw data is not NCIT:C142663) |
| C | 0 or 1 |
| D | 3 |

New CURIE-registry prefixes needed: `mesh`, `chmo` (B); `t4fs` only if chosen (A).
Labels and definitions above follow `docs/conventions.md` rules 2-3 (genus + differentia, no
units, lower case); each new EMPTY term would also need the rule-5 comment (OLS queries above,
who decided, the decision tag).
