# V_eta prefix spelling -- write a CURIE's prefix the way it is cited

**Status: SIGNED 2026-10-19 (the `TEAM-SIGN-OFF [prefix spelling]` line is at the end of section 4). BUILT 2026-10-20** (DID-schema 437beee: registry `spelling`/`spelling_source`/`synonyms`, `_spell_curie`; DID-matlab 5d5aa44: `curieKey`/`curieSpelling`; NDI-matlab f38c91dd: `ndi.v2.curie*`, Haley strains `WormBase:WBStrain…`). Not yet run in MATLAB CI. Asked for by Jess
(Haley import identifier review, 2026-10-19: "I'd rather store identifiers as
people cite them"; option B, each identifier's own registry decides the
spelling).

## 1. What happens today

`schemas/V_eta/stable/CURIE_lookups_meta.json`, `description`:

> Prefixes are matched case-insensitively; by convention prefixes are written
> in lowercase inside documents and annotations.

Three places act on the convention, and they do not agree:

| where | what it does | example |
|---|---|---|
| `tools/build_v_eta.py`, section 6 (`_lower_prefix`) | lowercases the prefix of every `node` / `root_node` in the schema's own class files and binding registry | `"node": "ncit:..."`, `"node": "time:..."` |
| NDI `+ndi/+setup/+V2/curie.m:36` | lowercases every `entity.global_identifier` prefix the import writes | `rrid:WB-STRAIN:WBStrain00004246`, `wormbase:WBStrain00004246` |
| the import's term nodes (`did2.build.term`) | **no** normalisation; written as the spec gives them | `NCBITaxon:6239`, `WBStrain:00004246`, `PATO:0001340` |

So one dataset already holds both spellings: `wormbase:WBStrain00004246` as an
identifier and `WBStrain:00004246` as a node.

Matching is unaffected by any of this. The registry matches prefixes
case-insensitively, and so does `ndi.ontology.lookup`
(`getOntologyNameFromPrefix`, `strcmpi`, ndi-ontology-matlab `9d8fc03`), whose
own prefix list is already mixed case (`CL`, `Chebi`, `NCBITaxon`, `RRID`,
`Uberon`, `WBStrain`, `wormbase`, ...).

## 2. Proposal

**P1. A prefix is written the way its issuer cites it.** Each registry entry
gains `spelling` (the prefix as written in documents) and `spelling_source`
(where that spelling comes from). The registry's key stays the lowercase
Bioregistry prefix, so nothing that looks a prefix up changes.

**P2. A reader recognises a prefix by its key, its `spelling` or any of its
`synonyms`, ignoring case.** `rrid:X` and `RRID:X` are the same identifier,
and so are `pubmed:123` and `PMID:123`. Each entry gains `synonyms`, taken from
Bioregistry's `synonyms` (fetched 2026-10-19: `pubmed` -> MEDLINE, PMID,
PubMed, PubMed ID, pmid; `pmc` -> PMC, PMCID; `orcid` -> ORCID, ORCiD; `rrid`
-> none). Without them a document written `PMID:123` would not resolve,
because `pmid` is not the key `pubmed` in any case. A writer emits `spelling`.
No two entries may share a key, spelling or synonym (case-insensitively); a
test checks this. The Haley import already maps the scheme names `pmid` and
`pmcid` to these entries by hand (`curie.m`, `case 'pmid'` / `case 'pmcid'`);
that mapping would read the registry's synonyms instead.

**P3. The rule covers term nodes as well as identifiers.** One spelling per
prefix everywhere, so `NCBITaxon:6239` (a node) and an `NCBITaxon:` identifier
look the same. `build_v_eta.py`'s `_lower_prefix` becomes "rewrite to
`spelling`".

**P4. Writers that build a CURIE from a scheme name use `spelling`.** In the
Haley import that is `curie.m`, which stops lowercasing.

The `description` sentence becomes:

> Prefixes are matched case-insensitively and written as each entry's
> `spelling`, the form the identifier's issuer cites.

## 3. The spellings

Bioregistry's `preferred_prefix` (fetched 2026-10-19) is already the cited
form for most entries. They differ only where the issuer cites the identifier
some other way (marked **differs**).

| key | Bioregistry preferred | proposed `spelling` | source | note |
|---|---|---|---|---|
| iao | IAO | IAO | OBO PURL `IAO_` | |
| uberon | UBERON | UBERON | OBO PURL | |
| pato | PATO | PATO | OBO PURL | |
| emapa | EMAPA | EMAPA | OBO PURL | |
| ncit | NCIT | NCIT | OBO PURL | |
| stato | STATO | STATO | OBO PURL | |
| obi | OBI | OBI | OBO PURL | |
| bfo | BFO | BFO | OBO PURL | |
| ro | RO | RO | OBO PURL | |
| cl | CL | CL | OBO PURL | |
| chebi | CHEBI | CHEBI | OBO PURL | |
| wbls | WBls | WBls | OBO PURL | |
| wbphenotype | WBPhenotype | WBPhenotype | OBO PURL | |
| wbbt | WBbt | WBbt | OBO PURL | |
| ncbitaxon | NCBITaxon | NCBITaxon | OBO PURL | |
| schema | schema | schema | schema.org | |
| time | time | time | W3C OWL-Time | |
| swh | swh | swh | the SWHID itself begins `swh:` | |
| wikidata | wikidata | wikidata | Bioregistry (Wikidata states no CURIE form) | |
| wormbase | WormBase | WormBase | Bioregistry | |
| rrid | rrid | **RRID** | SciCrunch record `properCitation`, e.g. `RRID:WB-STRAIN:WBStrain00004246` (checked 2026-10-19) | **differs** |
| pubmed | pubmed | **PMID** | NCBI's name for the id (PMC FAQ: "The PMID is a unique reference number for PubMed citations") | **differs**; Q2 (Jess) |
| pmc | pmc | **PMCID** | NCBI's name for the id (PMC FAQ: "The PMCID is a unique reference number or identifier that is assigned to every article that is accepted into PMC") | **differs**; Q2 (Jess) |
| orcid | orcid | **ORCID** | issuer gives no CURIE (its API returns `uri: https://orcid.org/...` and a bare `path`), so the issuer's name, per Q1 | **differs**; Q1 (Jess) |
| ror | ror | **ROR** | issuer gives no CURIE ("The preferred form of the ROR ID is the full URL"; a short form `ror.org/<id>` is allowed), so the issuer's name, per Q1 | **differs**; Q1 |
| doi | doi | doi | Crossref now asks for the URL and says DOIs should "not be preceded by doi: or DOI:"; the CURIE form it recommended until 2017 was `doi:10.NNNN/doisuffix`, lowercase. Q1 keeps a CURIE, so that form | Q1 |
| cellosaurus | cellosaurus | **RRID** (value `CVCL_xxxx`) | SciCrunch record for HeLa: `curie: RRID:CVCL_0030` | **differs**; Q3 (Jess) |
| addgene | addgene | **RRID** (value `Addgene_xxxxx`) | SciCrunch record: `properCitation: RRID:Addgene_12345` | **differs**; Q3 (Jess) |
| allen_ccf_v3, empty, placeholder, ndicloud | -- | unchanged | ours | |

Spellings marked "OBO PURL" are the capitalisation of the ID space in the
entry's existing `uri_base` (`.../obo/NCBITaxon_`), so they can be checked
mechanically. The other rows were checked against each issuer on
2026-10-19; the evidence is in section 3b.

**Rule for an issuer that gives no CURIE form** (ORCID, ROR, PubChem, SNOMED):
write the issuer's own name for the identifier (Q1, Jess). DOI is the
exception only because its issuer did once give a CURIE form.

## 3a. Prefixes in use that the registry cannot read today (added 2026-10-19, Jess: "add all three")

Every prefix in use was compared with the 32 registry keys and their
Bioregistry synonyms. "In use" = the Haley spec (nodes and identifier
schemes), every `node` / `root_node` under `schemas/V_eta/`, and
ndi-ontology-matlab `origin/main` `ontology_list.json` (the prefixes
`ndi.ontology.lookup` accepts). Three kinds of gap:

**(i) Synonyms.** All of Bioregistry's `synonyms` are imported (so `ChEBI`,
`NCIt`, `Uberon`, `wb`, `taxonomy`, ... resolve). One more is ours, because
Bioregistry does not list it and `ndi.ontology` uses it:

| synonym | entry | source |
|---|---|---|
| `NCBIT` | `ncbitaxon` | `ndi.ontology` (`NCBIT -> NCBITaxon`) |

**(ii) `WBStrain:` is written `WormBase:WBStrain...` (option (b)).** The two
forms split one id differently -- `WBStrain:00004246` (prefix `WBStrain`, id
`00004246`) and `WormBase:WBStrain00004246` (prefix `WormBase`, id
`WBStrain00004246`) -- so `WBStrain` cannot be a plain synonym of `wormbase`.
A strain node is written in the WormBase/Bioregistry form, the same as the
strain's identifier, so a strain has one form everywhere. A reader still meets
`WBStrain:<digits>` in older data and in `ndi.ontology` input; it is read as
`WormBase:WBStrain<digits>` (a REWRITE rule, not a synonym: the registry
records it on the `wormbase` entry as `{"legacy_prefix": "WBStrain",
"id_prefix": "WBStrain"}`). The Haley spec's 13 strain `node`s change to this
form when this is built.

The same split exists for EDAM: `ndi.ontology` accepts `format:1929`, and
EDAM's own id is `format_1929` under the `EDAM` idspace. **Q5 (Jess: yes):**
treated like `WBStrain` -- written `EDAM:format_1929`, `format:1929` read by
rewrite.

**(iii) New entries.** Seven prefixes `ndi.ontology` accepts, plus one used in
a V_eta conversion example, have no registry entry, so nothing written with
them can be pattern-checked or turned into a web address. From Bioregistry
(fetched 2026-10-19) unless noted:

| new key | Bioregistry preferred | proposed spelling | uri_base | pattern | synonyms | note |
|---|---|---|---|---|---|---|
| `om` | om | **om** | `http://www.ontology-of-units-of-measure.org/resource/om-2/` | none (ids are names, `om:metre`) | | the OM README: "**Namespace prefix:** `om`", and `om:metre`, `om:kilogram`; `ndi.ontology` writes `OM`, which still matches |
| `edam` | edam | **EDAM** | `http://edamontology.org/` | `^(data\|topic\|operation\|format)_\d{4}$` | `format` by rewrite (Q5) | `EDAM_dev.owl` declares idspace `EDAM` -> `http://edamontology.org/`, so `EDAM:format_1929` |
| `efo` | EFO | EFO | `http://www.ebi.ac.uk/efo/EFO_` | `^\d{7}$` | | |
| `pubchem.compound` | pubchem.compound | **PubChem** | `https://pubchem.ncbi.nlm.nih.gov/compound/` | `^\d+$` | CID, PUBCHEM_CID, Pubchem, ... | issuer gives no CURIE (its API labels the id `CID`, a word other databases also use), so the issuer's name; `ndi.ontology` writes `PubChem` |
| `snomedct` | snomedct | **SNOMEDCT** -- NOT CHECKED | `http://purl.bioontology.org/ontology/SNOMEDCT/` | `^(\w+)?\d+$` | SNOMED, SCTID, ... | snomed.org could not be read from here; the issuer's name by the rule above. No data uses it yet |
| `ncim` | ncim | **NCIm** | `http://ncim.nci.nih.gov/ncimbrowser/ConceptReport.jsp?dictionary=NCI%20MetaThesaurus&code=` | `^C\d+$` | | NCI's EVS: "The NCI Metathesaurus (NCIm) includes ..."; `ndi.ontology` writes `NCIm` |
| `ndic` | -- (ours) | **NDIC** | to fill from ndi-ontology-matlab | to fill | | NDI's own vocabulary; `ndi.ontology` writes `NDIC`; one V_eta conversion example writes `ndic:` |
| `fbdv` | FBdv | FBdv | `http://purl.obolibrary.org/obo/FBdv_` | `^\d{8}$` | | one V_eta conversion example (`ontology_table_row.md`) |

`EMPTY` is already the `empty` entry (case only). **Decided with Jess 2026-10-20 (at build time): the `empty` entry's spelling is `EMPTY`**, as the ontology writes its own ids (`EMPTY:0000276`; IRIs `EMPTY_`), replacing "unchanged" in the table above. Also decided then: `credit` stays Bioregistry's `credit`; `mco`, `micro` and `zeco` (used by the Haley import's terms) get entries spelled `MCO`, `MICRO`, `ZECO` (OBO PURLs). The Haley spec's `URL` and
`AwardNumber` are identifier scheme words, not prefixes; `curie.m` already
writes a URL as-is and an award number as a local id, and they need no entry.

## 3b. How the spellings were checked (2026-10-19)

| issuer | source read | what it says |
|---|---|---|
| SciCrunch (RRID) | `scicrunch.org/resolver/RRID:<id>.json` | `properCitation` `RRID:WB-STRAIN:WBStrain00004246`, `RRID:Addgene_12345`; `curie` `RRID:CVCL_0030` |
| Crossref (DOI) | crossref.org/display-guidelines | "always be displayed as a full URL ... not be preceded by doi: or DOI:"; until 2017 it "recommended that DOIs be displayed in the format doi:10.NNNN/doisuffix" |
| ROR | ror.readme.io/docs/display | "The preferred form of the ROR ID is the full URL"; a short form is allowed |
| ORCID | pub.orcid.org API | `{"uri": "https://orcid.org/0000-0002-1825-0097", "path": "0000-0002-1825-0097"}`, no CURIE (info.orcid.org returned 403) |
| NCBI (PMID, PMCID) | pmc.ncbi.nlm.nih.gov/about/public-access-info | names the ids `PMID` and `PMCID` |
| OM | github HajoRijgersberg/OM README | "Namespace prefix: `om`" |
| EDAM | edamontology `EDAM_dev.owl` | `idspace` `EDAM http://edamontology.org/` (and `EDAM_format`, `EDAM_data`, ...) |
| PubChem | PUG REST `compound/cid/2244` | the id is labelled `CID`; no CURIE form (its docs pages sit behind a browser check) |
| NCI EVS (NCIm) | EVS API terminology metadata | "The NCI Metathesaurus (NCIm) ..." |
| SNOMED International | snomed.org | **not read** (404 / unreachable) |

Two results changed the draft: OM's issuer writes `om`, lowercase (the draft
had `OM`), and DOI stays lowercase `doi`.

## 4. Answers so far (Jess, 2026-10-19) -- recorded, not signed

- **Q1:** a CURIE, not a URL: `ORCID:0000-0001-6282-7124`, likewise `ROR:`. The
  issuer's display URL is rebuilt from the entry's `uri_base`; the `pattern`
  check keeps working; one identifier has one shape. **DOI is written `doi:`**
  (lowercase), as the DOI Handbook's presentation formats give it
  ("doi:10.1006/jmbi.1998.2354"); checked 2026-10-19, accepted by Jess the same day.
- **Q2:** `PMID:` and `PMCID:`. The registry keys stay `pubmed` / `pmc`; only
  the written spelling changes.
- **Q3:** RRID. A Cellosaurus line is written `RRID:CVCL_0030` and an Addgene
  plasmid `RRID:Addgene_12345`; the `cellosaurus` / `addgene` entries stay for
  lookup, but the value changes form (it carries `CVCL_` / `Addgene_`), so a
  writer given a `cellosaurus` or `addgene` scheme converts it.
- **Q4:** the rule covers term nodes AND identifiers (P3 stands).
- **3a:** add the synonyms, write `WBStrain` nodes as `WormBase:WBStrain...`
  (option (b)), and add the missing entries.
- **Q5:** yes; EDAM's `format:1929` is written `EDAM:format_1929` and the old
  form read by rewrite.

To be signed: a CURIE's prefix is written as its issuer cites it (the registry entry's `spelling`, e.g. `ORCID:`, `ROR:`, `PMID:`, `PMCID:`, `RRID:`, `doi:`, `WormBase:`, `EDAM:format_`), for identifiers and term nodes alike; readers match a prefix by key, spelling or synonym, ignoring case; the registry keys stay the lowercase Bioregistry prefixes.
TEAM-SIGN-OFF [prefix spelling]: jess@walthamdatascience.com / 2026-10-19 -- a CURIE's prefix is written as its issuer cites it (the registry entry's spelling: ORCID:, ROR:, PMID:, PMCID:, RRID:, doi:, WormBase:, EDAM:format_), for identifiers and term nodes alike; readers match a prefix by key, spelling or synonym, ignoring case; registry keys stay the lowercase Bioregistry prefixes.

## 4a. The questions as first posed

**Q1. Identifiers whose issuer cites a URL, not a CURIE (ORCID, ROR, DOI).**
`entity.global_identifier` already accepts a full IRI where no prefix fits.
Options:
- (a) keep a CURIE, spelled `ORCID:` / `ROR:` / `DOI:`;
- (b) keep the lowercase Bioregistry form (`orcid:`, `ror:`, `doi:`);
- (c) store the full URL, exactly as the issuer cites it.

(c) is the most literal reading of "as people cite them". Its cost: the
prefix registry's `pattern` check no longer applies to these, and the same
person could appear as an `orcid:` CURIE in one dataset and a URL in another
(the drift test, `did_v2_openminds_family_record.md` Part 3).

**Q2. PubMed and PMC: rename the prefix, or keep the key and change only
case?** `PMID`/`PMCID` are not the same word as `pubmed`/`pmc`, so this is a
second name for the same entry, not a capitalisation. Bioregistry lists
`pmid` as a synonym of `pubmed`.

**Q3. Cellosaurus and Addgene cite through RRID.** Keep their own prefixes
(spelled `Cellosaurus:` / `Addgene:`), or write them as RRIDs?

**Q4. Term nodes (P3).** Apply the rule to nodes too (one spelling
everywhere), or to identifiers only? Applying it reverses the lowercasing
`build_v_eta.py` section 6 did on 2026-10-08 (signed with
`did_v2_entity_composition_plan.md` sec. 6). This proposal would amend that
section.

## 5. What a build would touch (not started)

- **DID-schema:** `build_v_eta.py` section 6 (add `spelling`,
  `spelling_source` and `synonyms`; replace `_lower_prefix`); the registry `description`; a
  test that every entry has a `spelling` that matches its key
  case-insensitively, and that every node and identifier in the built schema
  uses it.
- **NDI:** `+V2/curie.m` writes `spelling` and reads synonyms from the
  registry; the Haley spec's 13 strain nodes become `WormBase:WBStrain...`;
  tests for the identifiers and nodes it produces.
- **ndi-ontology-matlab:** none required (it already matches
  case-insensitively and accepts `wormbase:`); its `WBStrain` and `format`
  entries keep working for old input.
- **DID-matlab:** none known. No `lower(` on a prefix was found under
  `src/did/+did2` (search: `grep -rn "lower(" src/did/+did2/+build`, 0 hits).
- **Already-written data:** none to migrate. Matching is case-insensitive, and
  no published dataset holds V_eta identifiers yet.

## 6. Found while drafting (not part of the proposal)

The built schema uses two node prefixes that have no registry entry:
`ndic:` (1 node) and `fbdv:` (1 node). Count:
`grep -rhoE '"node": "[A-Za-z]+:' schemas/V_eta/ | sort | uniq -c`.
