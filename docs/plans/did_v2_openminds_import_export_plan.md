# openMINDS import and export for v2: plan

**Status: Proposed (not decided).** Drafted by Claude on 2026-11-06, after Jess
Haley asked "Should we plan out both import and export next to each other?"
and then "Yes, draft the plan". Nothing here is decided until a decision line
below records it.

## 1. Why one plan for both directions

openMINDS is the metadata standard NDI exports to (EBRAINS and NDI Cloud). v2
needs both directions:

- **Import (openMINDS -> v2).** The makers and the metadata editor take
  openMINDS objects (species, strain, sex, people, organisations) and write
  NDI documents.
- **Export (v2 -> openMINDS).** A v2 dataset becomes openMINDS objects, which
  NDI-matlab #768 needs (openMINDS replaced `author` with contributions).

Both directions read the same mapping. If each direction codes the mapping
separately, the two drift apart and a round trip cannot be tested. This plan
puts the mapping in one place, the crosswalk, and makes both directions read
it.

## 2. What exists today (measured 2026-11-06)

**did-schema.**
- `schemas/registry/did_v2_openminds_crosswalk.json` (`crosswalk_version`
  1.1.0) maps openMINDS properties to v2 targets for five types:
  - DatasetVersion, 29 properties: field 2, assertion 11, relation 11,
    global_identifier 3, implied 1, projection 1;
  - Person, 6: assertion 4, global_identifier 1, relation 1;
  - Organization, 5: field 1, assertion 1, global_identifier 2, relation 1;
  - Funding, 3: field 2, relation 1;
  - SoftwareVersion, 8: field 2, assertion 1, global_identifier 3,
    projection 2.
- Some of its entries:
  - `releaseDate` -> assertion "release date" (date);
  - `license` -> assertion "license" (term);
  - `author` -> relation "author";
  - `custodian` -> relation "maintainer";
  - `Person.affiliation` -> relation "affiliation" to an organization;
  - `studiedSpecimen` -> projection, recomputed from the subjects.
- Its `$comment` calls the 2026-10-08 entity-composition mapping a PROPOSAL.
  That composition plan was later signed; whether the crosswalk itself is
  decided is question Q1 below.
- `tests/test_veta.py::test_openminds_crosswalk_round_trips` checks that
  every DatasetVersion property has an explicit entry, that none is
  `deferred`, and that every target resolves (a real entity field, a
  registered relation, a known CURIE scheme). It checks the table, not data.
- The term registry's `equivalent` column records openMINDS instances for
  terms, for example `openminds:species/musMusculus` for NCBITaxon:10090
  ([common species registered], [equivalents filled in did-schema]).

**NDI-matlab `V2`.**
- `+ndi/+database/+fun/openMINDSobj2V2.m` (#1165) is the only v2 import. It
  turns openMINDS species, strain and sex objects into v2 term assertions
  about a subject. Its mapping is hard-coded, not read from the crosswalk.
- `openMINDSobj2ndi_document.m`, `openMINDSobj2struct.m`, and the metadata
  editor (`+database/+metadata_app/`, `+database/+metadata_ds_core/`) all go
  openMINDS -> v1 `openminds` documents.
- Nothing exports v2 to openMINDS.
- `+ndi/+cloud/+admin/+crossref/+conversion/` (one function per target field,
  NDI Cloud record -> Crossref) is the existing pattern for an export to an
  external standard.

**Not covered by the crosswalk:** Subject, SubjectState, SubjectGroup,
TissueSample, Strain, Species, Technique, Protocol, File. Item 14 of
`docs/V2_PLAN.md` "Open questions for the team" notes the missing technique
and data-type entries.

## 3. Proposed design

### 3.1 The crosswalk is the single mapping
- Both directions read `did_v2_openminds_crosswalk.json`. No mapping is
  hard-coded in NDI-matlab: the code dispatches on `target_kind` (field,
  assertion, relation, global_identifier, implied, projection).
- Terms (species, licence, approach, accessibility) map through the term
  registry's `equivalent` column. The export writes the openMINDS instance a
  term is equivalent to. The import finds the registered term whose
  `equivalent` is the openMINDS instance.
- New types are added to the crosswalk before any code uses them, and the
  did-schema round-trip test is extended to each new type (completeness
  against that type's openMINDS property list, at the pinned version).

### 3.2 openMINDS version
`latest` as pinned by openMINDS_MATLAB v0.12.0, NDI's current pin (G108(1),
Jess Haley 2026-11-06: "Latest"). Moving to a new version is a deliberate
change: re-pin, then update the crosswalk and its test.

### 3.3 One NDI-matlab package, two directions
```
+ndi/+openminds/
    crosswalk.m          % loads did_v2_openminds_crosswalk.json (via the did-schema loader)
    exportDataset.m      % v2 dataset -> {Dataset, DatasetVersion, Person..., Organization..., Funding...}
    exportPerson.m       % person entity + its assertions/relations -> Person (+ Contribution)
    exportSubject.m      % stage 2: subject entity + term assertions -> Subject, SubjectState
    importObjects.m      % openMINDS objects -> v2 documents (entity, assertions, relations)
    saveJSONLD.m         % optional: write exported objects as JSON-LD
```
- The export reads **database documents** (the dataset entity and its
  statements and relations), not NDI objects. In v2 the data is the
  documents, and keeping openMINDS out of NDI's core classes avoids making
  them depend on openMINDS_MATLAB.
- The import returns v2 documents built and checked with `did2.build`, and
  writes nothing itself. Writing goes through the v2 makers when they exist
  ([v2 makers after G84]).
- `openMINDSobj2V2.m` is folded into `importObjects.m` once the crosswalk
  covers Species, Strain and sex (stage 2).

### 3.4 Contributions and roles
- v2 contributors are relations from the dataset to each person, with CRediT
  roles (signed 2026-09-30). The export turns each into an openMINDS
  contribution. A 14-row table maps each CRediT role to an openMINDS
  contribution type (G108(2): "Draft it"). The table goes in the crosswalk.
- Author order is kept as one ordered authoring contribution. The
  corresponding author is not exported (G108(3): "Drop it").
- Affiliations: each person's affiliations as listed for that person within
  the dataset (G108(4): "A person's affiliations are listed for that person
  within the dataset tho, so yes"). To check while building: how v2 ties an
  affiliation relation to the dataset.

### 3.5 DatasetVersion now
`DatasetVersion` is exported in stage 1, not later (G108(5): "Why not just
add dataset version now?"). Its fields come from the dataset's assertions as
the crosswalk lists them (release date, licence, version identifier, and so
on). A required field the dataset does not state is reported as missing and
never invented.

### 3.6 Tests
- **did-schema:** the existing crosswalk test, extended to each new type.
- **NDI-matlab:**
  - export: the exported objects validate against the pinned openMINDS
    schema;
  - round trip: `importObjects(exportDataset(D))` gives back the same
    statements and relations for every mapped property, on a fixture
    dataset;
  - missing data: a dataset without a release date reports it missing.

## 4. Stages

| stage | scope | depends on |
|---|---|---|
| 0 | Decide the crosswalk (Q1). Draft the CRediT -> openMINDS table. Pin the version. | Jess |
| 1 | **Export, dataset level:** Dataset, DatasetVersion, Person, Organization, Funding, contributions; JSON-LD; schema test. | stage 0 |
| 2 | **Subjects, both directions:** add Subject, SubjectState, SubjectGroup, Species, Strain and sex to the crosswalk; exportSubject; importObjects with `openMINDSobj2V2` folded in; round-trip test. | stage 1; Q3 |
| 3 | **Samples, techniques, protocols, files:** crosswalk entries first (item 14), then both directions. | stage 2 |
| — | **Import used by writers:** the makers call `importObjects`. | [v2 makers after G84] |

Export can be built before the makers. Import code can be written and tested
in stage 2, but it is wired into writers only by the makers design.

## 5. Questions for the team

Jess Haley answered on 2026-11-06. These are operational answers to this
plan, not decision lines; the plan stays Proposed until it is decided.

- **Q1.** Is `did_v2_openminds_crosswalk.json` (1.1.0) the decided mapping?
  Answer: "I don't know. Explain", then "The review table sounds good. Prep
  it, but don't give it to me til tomorrow when we start reviewing the next
  set of open questions." **Open:** Claude reviews the crosswalk row by row
  with Jess, starting from a prepared review table.
- **Q2.** Package name and place: "Your proposal sounds good".
  `+ndi/+openminds/` in NDI-matlab.
- **Q3.** Stage order: "Whatever you think". Claude's choice: subjects in
  stage 2, as in section 4. The crosswalk has no subject types yet, and they
  bring in the import side, which waits on the makers.
- **Q4.** The CRediT -> openMINDS contribution-type table: "Explain", then
  "Yes". Claude drafts it for review.
- **Q5.** A required openMINDS field the dataset does not state: "Report".
  The export writes what it can and reports each missing field; it never
  invents a value.

## 6. Decisions recorded so far (G108, 2026-11-06)

Jess Haley's answers to docs/V2_PLAN.md G108 are recorded in
`did_v2_go_forward_class_audit.md`, tagged [openMINDS export answers]. In
summary: (1) "Latest"; (2) "Draft it"; (3) "Drop it"; (4) "A person's
affiliations are listed for that person within the dataset tho, so yes";
(5) "Why not just add dataset version now?"; (6) "Yes".
