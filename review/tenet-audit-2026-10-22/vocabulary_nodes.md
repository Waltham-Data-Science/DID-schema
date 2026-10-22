# DID vocabularies → ontology nodes: draft mapping (Proposed, not decided)

Prepared 2026-10-22 for Jess Haley. This is a proposal; nothing here has been decided.
did-schema is at `claude/ecstatic-pascal-md91fw` @ `cbae082`. Nothing was written under /home/user/DID-schema.

Where things came from:
- Bindings: `schemas/V_eta/stable/binding_registry_meta.json`. I read `relation_bindings` (**34 rows**) and `entity_type_bindings` (**19 rows**).
- Channel types: NDI-matlab `origin/main` @ `639f2c41f`, `src/ndi/+ndi/+daq/+system/mfdaq.m` `mfdaq_prefix`. It has **18 prefixes**, and `claude/v2-object-layer` has the same 18.
- Definitions: EBI OLS4 (`/api/search` and `/api/ontologies/{ont}/{terms|properties}?iri=`). For schema.org I used the OLS `schemaorg_https` ontology, and for owl:sameAs the W3C `owl.ttl`. The query scripts are in `scratchpad/olsq/` (`q.py`, `id2.py`, `sdo.py`).
- Prefixes accepted by the registry: `schemas/V_eta/stable/CURIE_lookups_meta.json`, 50 prefixes, rule R4 in `tools/check_term_registry.py`. Of the prefixes proposed below, **SIO and owl are not registered**. Every other prefix used (BFO RO schema COB OBI IAO NCIT CL UBERON EMPTY) is registered.
- Term registry: `schemas/V_eta_term_registry.json` has **508 terms**. It has no rows with the prefix RO, BFO, schema, COB or CL. So **none of the 5 relation nodes that already exist are registry rows**, and every node chosen here would need a registry row (T19: "registered before it is used").

Fit: **exact** means the definition matches in the child→parent direction. **close** means usable, with the caveat stated. **EMPTY** means no fitting term was found.
Proposed EMPTY ids are **provisional and run in sequence from the next free id, EMPTY:0000370** (see the end of this file).

---

## 1. relation_bindings (34 rows read)

| # | current name | child → parent (roles) | proposed node | ontology label | definition (quoted) | fit | EMPTY label + definition / note |
|---|---|---|---|---|---|---|---|
| 1 | part_of | part → whole | BFO:0000050 (existing) | part of | "a core relation that holds between a part and its whole" | exact | keep |
| 2 | included_in | record → record it is filed under | schema:isPartOf (existing) | isPartOf | "Indicates an item or CreativeWork that this item, or CreativeWork (in some sense), is part of." | close | Keep. "In some sense" is broad, but the direction is right. |
| 3 | contained_in | contained → container | **RO:0001018 (existing) is OBSOLETE in RO**. Proposed: RO:0001025 | located in | "a relation between two independent continuants, the target and the location, in which the target is entirely within the location" | close | **FLAG.** OLS reports RO:0001018 as "obsolete contained in", `is_obsolete: true`, `term_replaced_by: null`, and points to obo-relations issue #693. "Entirely within" fits a worm on a patch or a plate in an incubator. It fits a thing lying *on* a surface less well. |
| 4 | member_of | member → group | RO:0002350 (existing) | member of | "is member of is a mereological relation between a item and a collection." | exact | Keep. In RO, RO:0002350 is a child of BFO:0000050, which is consistent with DID. |
| 5 | derived_from | derivative → source | RO:0001000 (existing) | derives from | "a relation between two distinct material entities, the new entity and the old entity, in which the new entity begins to exist when the old entity ceases to exist, and the new entity inherits the significant portion of the matter of the old entity" | close | **FLAG.** The RO term is narrower than the row. The row has `child_types: []` and `parent_types: []` (any document), but RO requires material entities and requires the source to stop existing. T19 says "never narrower than true". For derivation between information entities, schema:isBasedOn fits better, but row 21 is proposed for it. |
| 6 | sample_of | sample → sampled source | EMPTY:0000370 | — | — | none → EMPTY | **"sample of"**: a relation between a portion or specimen taken from something and the thing it was taken from, which continues to exist. Nearest found: classes NCIT:C19157 Specimen and OBI:0100051 specimen, but no relation. |
| 7 | aliquot_of | aliquot → parent quantity | EMPTY:0000371 | — | — | none → EMPTY | **"aliquot of"**: a relation between one of several measured portions divided from a quantity of material and that quantity. NCIT:C25414 "Aliquot" exists, but it is a class. Jess: should this be a sub-property of part_of (T5 "portion of the parent's own material")? |
| 8 | passage_of | passage → parent culture | EMPTY:0000372 | — | — | none → EMPTY | **"passage of"**: a relation between a culture started by transferring part of another culture to fresh medium and the culture it was transferred from. NCIT:C54573 "Passage" exists, but it is a process class. |
| 9 | encountered | encountering subject → encountered subject | RO:0002437 | biotically interacts with | "An interaction relationship in which at least one of the partners is an organism and the other is either an organism or an abiotic entity with which the organism interacts." | close | **FLAG.** The RO term is symmetric, so the DID direction would be lost. The fallback is EMPTY "encountered": a relation from a subject to another subject it came into contact with. NCIT:C62143 "Encounter" is a registered **class**, not a relation. |
| 10 | measured_distance_to | — | — | — | — | retiring | Retiring (decision G5). No term needed. |
| 11 | has_author | dataset → person | schema:author | author | "The author of this content or rating. …" | exact | |
| 12 | cites | dataset → publication | schema:citation | citation | "A citation or reference to another creative work, such as another publication, web page, scholarly article, etc." | exact | SIO:000277 "cites" also fits, but SIO is not a registered prefix. |
| 13 | funded_by | dataset → funding | schema:funding | funding | "A [[Grant]] that directly or indirectly provide funding or sponsorship for this item." | exact | |
| 14 | issued_by | funding → organization | schema:funder | funder | "A person or organization that supports (sponsors) something through some kind of financial contribution." | close | The domain includes MonetaryGrant, so this is close. |
| 15 | affiliated_with | person → organization | schema:affiliation | affiliation | "An organization that this person is affiliated with. …" | exact | |
| 16 | documented_by | entity/formulation → protocol/publication/software | schema:subjectOf | subjectOf | "A CreativeWork or Event about this Thing." | close | "About" is weaker than "documented by". IAO:0000136 "is about" runs the **inverse** direction (document → thing). |
| 17 | has_custodian | dataset → person/org | schema:maintainer | maintainer | "A maintainer of a [[Dataset]], software package …, or other [[Project]]. A maintainer is a [[Person]] or [[Organization]] that manages contributions to, and/or publication of, some … artifact." | close | No custodian term was found. |
| 18 | contributed_by | dataset → person/org | schema:contributor | contributor | "A secondary contributor to the CreativeWork or Event." | exact | |
| 19 | copyright_holder | dataset → org/person | schema:copyrightHolder | copyrightHolder | "The party holding the legal copyright to the CreativeWork." | exact | |
| 20 | alternative_of | dataset version → alternative version | SIO:000497 | is version of | "is version of is a relation that holds between any two versions in which one is a subsequent or alternate version of (through a branch)." | close | **The SIO prefix would need adding** to CURIE_lookups_meta. The fallback is EMPTY "alternative version of": a relation between two versions of one work that neither supersedes. |
| 21 | input_data | derived dataset → input dataset | schema:isBasedOn | isBasedOn | "A resource from which this work is derived or from which it is a modification or adaptation." | exact | |
| 22 | follows_protocol | dataset → protocol | EMPTY:0000373 | — | — | none → EMPTY | **"follows protocol"**: a relation between a body of work and a written procedure it was carried out by. No relation was found in RO, OBI, IAO, BFO or SIO. The only hit was HSO "follows surveillance protocol", which is too narrow. |
| 23 | suborganization_of | child org → parent org | schema:parentOrganization | parentOrganization | "The larger organization that this organization is a [[subOrganization]] of, if any." | exact | |
| 24 | instance_of | unit/member → product or strain | EMPTY:0000374 | — | — | none → EMPTY | **"instance of"**: a relation between a particular thing and the product or genetic line of which it is one individual. schema:model ("The model of the product …") fits only the product half. **FLAG:** this one row covers two meanings. |
| 25 | awarded_to | funding → person/org | schema:fundedItem | fundedItem | "Indicates something directly or indirectly funded or sponsored through a [[Grant]]." | close | Its range includes Person and Organization. **FLAG:** it is also the inverse of row 13's meaning. |
| 26 | orthologous gene mapping | mapped gene list → target gene list | RO:HOM0000017 | in orthology relationship with | "Historical homology that involves genes that diverged after a speciation event." | close | The RO term relates genes, not gene lists, and it is symmetric. **FLAG:** the name has spaces, unlike every other relation name. |
| 27 | gene alias mapping | mapped gene list → target gene list | EMPTY:0000375 | — | — | none → EMPTY | **"gene alias mapping"**: a relation between a list of gene names and the list that gives each gene under another of its names. OIO hasExactSynonym is an annotation property, and its prefix is not registered. |
| 28 | paired_with (undirected) | an entity in a pair | EMPTY:0000376 | — | — | none → EMPTY | **"paired with"**: a symmetric relation between two entities that belong together as a pair. Nothing fitting was found. RO:0018035 (matched molecular pair) is chemistry-only. |
| 29 | same_as (undirected) | the same thing recorded twice | owl:sameAs | sameAs | "The property that determines that two given individuals are equal." | exact | **The `owl` prefix would need adding.** schema:sameAs is a URL to a reference page, which is a different meaning. The fallback is EMPTY "same as". |
| 30 | sold_by | product → vendor | schema:seller | seller | "An entity which offers (sells / leases / lends / loans) the services / goods. …" | close | The domain is Offer, not Product. OBI:0000304 is_manufactured_by is a different meaning, because a vendor is not always the manufacturer. |
| 31 | developed_by | software → organization | schema:creator | creator | "The creator/author of this CreativeWork. This is the same as the Author property for CreativeWork." | close | **FLAG:** by its own definition it is a near-synonym of row 11's schema:author. |
| 32 | hosted_by | dataset → org hosting a copy | schema:provider | provider | "The service provider, service operator, or service performer; the goods producer. …" | close | **FLAG:** this is a weak fit. The fallback is EMPTY "hosted by". |
| 33 | distributed_as | strain → product | EMPTY:0000377 | — | — | none → EMPTY | **"distributed as"**: a relation between a genetic line and a product under which it is supplied. |
| 34 | recorded_by | — | — | — | — | retiring | Retiring (decision A1). No term needed. |

The relation rows name some types that are not in entity_type_bindings: `acquisition_system` (recorded_by, which is retiring), `formulation` (documented_by), `term` (rows 26 and 27) and `entity` (rows 16, 28 and 29).

## 2. entity_type_bindings (19 rows read)

| type | DID description | proposed node | ontology label | definition (quoted) | fit | note |
|---|---|---|---|---|---|---|
| organism | one whole living individual | COB:0000022 | organism | "A material entity that is a maximal functionally integrated unit that develops from a program encoded in a genome" | exact | OBI:0100026 is **obsolete** in OBI, and OBI now uses COB:0000022. NCIT:C14250 "A living entity." is an alternative. |
| culture | a mass grown as one: a bacterial lawn, a cell culture | OBI:0001876 | cell culture | "A material entity comprised of cultured cells and the media in which they are being propagated or stored." | close | A bacterial lawn is cultured cells plus medium, so it fits. EMPTY:0000357 "culture type" is the subtype variable. NCIT:C16478 "Culture" means human culture, which is the wrong sense. |
| tissue | part of an organism: a slice, a biopsy, a region | UBERON:0000479 | tissue | "Multicellular anatomical structure that consists of many cells of one or a few types, arranged in an extracellular matrix …" | close | **FLAG (ambiguous name).** The description mixes an in-situ region with a removed specimen. OBI:0001479 "specimen from organism" fits a slice or biopsy but not a region. UBERON:0000061 "anatomical structure" is registered, but it is "generated by coordinated expression of the organism's own genome", which a slice is not. |
| cell | one cell | CL:0000000 | cell | "… a cell is defined as a material entity and not an anatomical structure …" | exact | |
| group | an entity whose members are entities | NCIT:C43359 | Group | "Any number of entities (members) considered as a unit." | exact | |
| device | an instrument or a piece of apparatus | COB:0001300 | device | "A processed material entity which is designed to be capable of a process." | exact | OBI:0000968 is **obsolete**. NCIT:C62103 "An object contrived for a specific purpose." is an alternative. |
| material | a non-living object or substance: an agar plate | NCIT:C48187 | Material | "The tangible substance that goes into the makeup of a physical object." | close | **FLAG.** The NCIT term names the substance, not the object. BFO:0000040 material entity is too broad because it includes organisms. EMPTY:0000354's comment already records that no Material Type term exists. |
| strain | a genetically defined line | NCIT:C14419 | Organism Strain | "A population or type of organisms that is genetically different from others of the same species …" | exact | **Already registered and used in an NDI dataset** (Haley), so it is T19 step 1. R1 means the type must reuse that registry row, not add a second one. |
| product | something bought | schema:Product | Product | "Any offered product or service. …" | exact | NCIT:C51980 ("end result of a manufacturing process") is an alternative. |
| software | a program, at a version | IAO:0000010 | software | "Software is a plan specification composed of a series of instructions that can be interpreted by or directly executed by a processing unit." | exact | |
| person | a person | NCIT:C25190 | Person | "A human being." | exact | schema:Person is an alternative. |
| organization | an institution, a lab, a company, a funder | OBI:0000245 | organization | "An entity that can bear roles, has members, and has a set of organization rules. …" | exact | NCIT:C92453 "Organization" is the **wrong sense** ("The activity or result of distributing or disposing of things"). |
| funding | a grant or award | NCIT:C16644 | Grant | "A financial assistance mechanism through which money and/or direct assistance is provided to carry out approved activities." | exact | NCIT:C17769 Funding is "a sum of money", a different meaning. OBI:0001636 grant is organization-to-organization only. |
| dataset | a published body of data, at a version | NCIT:C47824 | Data Set | "A collection of related data records." | exact | The document carries "published" and the version (T19). IAO:0000100 is now labelled "homogenous data collection", which does not fit. |
| study | a unit of research with its own question and design | OBI:0000066 | investigation | "a planned process that consists of parts: planning, study design execution, documentation and which produce conclusion(s)." | close | **FLAG.** NCIT:C63536 Study is "A detailed examination, analysis, or critical inspection of a subject …". Both are acceptable, and Jess should pick one. |
| publication | an article or preprint | IAO:0000311 | publication | "A document that is the output of a publishing process." | exact | |
| protocol | a written procedure | OBI:0000272 | protocol | "A plan specification which has sufficient level of detail and quantitative information to communicate it between investigation agents …" | exact | |
| session | a period of work | NCIT:C67447 | Session | "Time, period, or term devoted to some activity." | exact | |
| epoch | one recording: the files one acquisition system wrote for one stretch of time | EMPTY:0000378 | — | — | none → EMPTY | **"recording epoch"**: one continuous stretch of recording by one acquisition system. **FLAG (ambiguous name).** om:Epoch is a time origin and NCIT:C71738 "Clinical Trial Epoch" is a study phase. Neither fits. |

## 3. Channel types (root + 18 NDI prefixes)

The root is NCIT:C44170 **Channel**: "An independent acquisition scheme, i.e., a route or conduit through which flows data consisting of one particular measurement using one particular parameter." (decided, B2 (a))

**FLAG:** NDI `origin/main` has **18** prefixes. The four analog-derived event types `aep aen aimp aimn` are missing from the task's list. All eight `*ep/*en/*mp/*mn` types are **read-time derivations** from a `di` or `ai` channel (`readevents_epochsamples`), not hardware channels. Jess: do they need terms at all? The `acquisition_channels.type` value set today holds only ai, ao, di and do.

The searches below found no matching term. I searched OLS4 for: "analog input", "analog output", "digital input", "digital output", "analog signal", "digital signal", "input channel", "output channel", "data channel", "event channel", "time channel", "auxiliary channel", "timestamp", "time stamp", "event marker", "marker", "TTL", "trigger signal", "digital event", "rising edge", "threshold crossing", "pulse", "logic level", "binary signal", "voltage signal". The searches ran across all ontologies and across NCIT, OBI, EDAM, IAO and STATO. I also checked NDIC.txt (27 lines) and empty-ontology labels. The only hits were modifiers, such as NCIT:C62251 Digital, NCIT:C43382 Signal, NCIT:C25499 Event and NCIT:C72669 Computer Time Stamp. NCIT:C177671 Marker ("A visual indicator of position, place or route") is the wrong sense. BioPortal and InterLex need API keys and were not queried, so **those were not searched**.

| prefix | NDI meaning (reader/mfdaq.m, origin/main) | proposed node | label | definition | fit |
|---|---|---|---|---|---|
| md | metadata | NCIT:C52095 | Metadata | "Data about data; information that describes another set of data." | decided (B2) |
| tx | "Text mark channel (contains character string at specified time)" | NCIT:C25704 | Text | "The words of something written." | decided (B2) |
| ai | Analog input | EMPTY:0000379 | analog input channel | A channel through which an acquisition system samples a continuously valued signal. | EMPTY |
| ao | Analog output | EMPTY:0000380 | analog output channel | A channel through which an acquisition system emits a continuously valued signal. | EMPTY |
| di | Digital input | EMPTY:0000381 | digital input channel | A channel through which an acquisition system samples a two-state signal. | EMPTY |
| do | Digital output | EMPTY:0000382 | digital output channel | A channel through which an acquisition system emits a two-state signal. | EMPTY |
| t | Time | EMPTY:0000383 | time channel | A channel whose values are the times at which the other channels were sampled. | EMPTY (NCIT:C72669 is a stamp, not a channel) |
| ax | "Auxiliary channels" | EMPTY:0000384 | auxiliary input channel | A channel through which an acquisition system samples a signal that supports, rather than is, the primary measurement. | EMPTY. **FLAG:** NDI gives no definition. |
| e | "Event trigger (returns times of event trigger activation)" | EMPTY:0000385 | event channel | A channel whose values are the times at which events occurred. | EMPTY |
| mk | "Mark channel (contains int16 value at specified times)" | EMPTY:0000386 | marker channel | A channel whose values are codes, each at the time it was recorded. | EMPTY |
| dep | events at a digital channel's positive transitions | EMPTY:0000387 | rising-edge event channel | A channel of events at the times a two-state signal rises. | EMPTY (derived) |
| den | events at negative transitions | EMPTY:0000388 | falling-edge event channel | A channel of events at the times a two-state signal falls. | EMPTY (derived) |
| dimp | impulses: positive then negative transition | EMPTY:0000389 | positive pulse event channel | A channel of events at the rise and the following fall of each positive pulse in a two-state signal. | EMPTY (derived) |
| dimn | impulses: negative then positive transition | EMPTY:0000390 | negative pulse event channel | A channel of events at the fall and the following rise of each negative pulse in a two-state signal. | EMPTY (derived) |
| aep | analog upward threshold crossings | EMPTY:0000391 | upward threshold-crossing event channel | A channel of events at the times a continuously valued signal crosses a threshold upward. | EMPTY (derived; **not in the task list**) |
| aen | analog downward threshold crossings | EMPTY:0000392 | downward threshold-crossing event channel | A channel of events at the times a continuously valued signal crosses a threshold downward. | EMPTY (derived; not in the task list) |
| aimp | analog pulses above threshold | EMPTY:0000393 | above-threshold pulse event channel | A channel of events at the upward and the following downward threshold crossing of each pulse. | EMPTY (derived; not in the task list) |
| aimn | analog pulses below threshold | EMPTY:0000394 | below-threshold pulse event channel | A channel of events at the downward and the following upward threshold crossing of each pulse. | EMPTY (derived; not in the task list) |

T19 alternative (needs Jess's judgment): ai/ao/di/do could be split into "analog channel" and "digital channel", with direction stated elsewhere. The document has no direction field today, though, so the proposal keeps one term per value.

## 4. Next free EMPTY id

- Registry: 112 EMPTY rows. The highest is **EMPTY:0000369**.
- empty-ontology `src/ontology/empty-edit.owl`, highest id per branch (after `git fetch` of all heads):
  - `V2` 07cf4ed: EMPTY_0000367
  - `main` 68fa1b5: EMPTY_0000258
  - `claude/flashed-bar-ndi-binary` 5afd97f: EMPTY_0000367
  - `claude/ome-zarr-format` 214519f: EMPTY_0000365
  - `claude/onset-offset-time` f6b93d8: EMPTY_0000369
- No `EMPTY[:_]00003[7-9]x` appears in did-schema `schemas/` or `tools/`, or on any did-schema remote branch.
- **Next free: EMPTY:0000370.** This proposal would use 0000370–0000394 (25 terms).
- empty-edit.owl declares **0** ObjectProperties. The EMPTY relation terms (rows 6, 7, 8, 22, 24, 27, 28, 33) would be the first, which is a structural choice for Jess.
