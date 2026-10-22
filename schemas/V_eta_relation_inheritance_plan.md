# V_eta: what a relation passes, records' own relation, and `session_id` as an edge

Written 2026-10-20 at Jess Haley's request, from the Haley import's tenet audit
(T-1). Built ahead of signature at her request ("build it", 2026-10-20) and
signed by her 2026-10-21 (the `TEAM-SIGN-OFF [relation inheritance]` line at the
end). Built in did-schema#88
(`tools/build_v_eta.py` section 12.16), VH-Lab/DID-matlab#218 and
VH-Lab/NDI-matlab#1021. did-schema `main` is unchanged.

## The problem

**`part_of` meant two things.** `binding_registry_meta.json`'s `part_of` row
(BFO:0000050) allowed the physical types (organism, culture, tissue, cell,
group, device, material) and, since the study plan (signed 2026-09-30, "widen
part_of to session->study, study->dataset, study->study"), the records session,
study and dataset. So one relation said both "is a portion of" (a slice of a
brain) and "is filed under" (a session in a study, a study in a dataset).

**T17 gives each relation one inheritance rule, chosen by its name.** An
assertion about a whole is true of each part. That is right for material and
wrong for records: on the one-entity schema the dataset's short name, version,
licence, release date, citation and authors are assertions
(`ndi.setup.V2.entityDocuments`), so every study and every session read as
having them, and a study had two short names. NDI hard-coded the rule as lists
of relation names (`ndi.entity`, `{'part_of','sample_of','aliquot_of','passage_of'}`).

The same cause produced three findings: #52 (patches `part_of` plates took the
plate's kind; #107 changed it to `contained_in`), T-1 (the dataset's assertions
reached its studies and sessions) and T-3 (a plate's exclusion cannot reach its
worms through `contained_in`). Choosing a relation silently chose what passes
along it, and nothing made anyone check the second choice. Organizations had
already avoided this with their own `suborganization_of`.

**`base.session_id` was the one link in V_eta that was not an edge.** It is the
session's id, stamped on every document since 2018 (`.ndi/unique_reference.txt`),
long before the session became a document (2024-02-12, NDI-matlab 08158724,
"made session a document"). When it did, the `ndi.document` constructor gave
that document a fresh `base.id` like any other, so a session had two ids of the
same format (`did.ido.unique_id`, 33 characters): `base.session_id`, which
everything joins on, and the session document's `base.id`, which only relations
pointed at. Nothing in v1 refers to a session document by its `base.id`.

## The decision (proposed)

1. **Every relation declares what passes along it.** Each `relation_bindings`
   row carries a required `passes`:

   | value | what reaches the child from the parent | rows |
   |---|---|---|
   | `assertions` | an assertion about the parent is true of the child | part_of, sample_of, aliquot_of, passage_of, instance_of |
   | `distributive` | a statement or relation marked `distributive` on the group is true of each member | member_of |
   | `context` | the parent's interactions overlapping the stay, as context, never fact | contained_in |
   | `nothing` | nothing | every other row |

   A row with no `passes` stops the build; there is no default. T17 describes
   the four values, and a reader takes them from the registry, so the schema
   and the reader cannot disagree and a new relation works without code.
   `same_as` is `nothing`: it joins two records of one thing (T18), which a
   reader applies as identity before walking any relation.

2. **Records get their own relation, `included_in`** (`schema:isPartOf`,
   schema.org's "is part of" for works and collections). Child session or
   study; parent study or dataset. It passes nothing. A session is
   `included_in` its study or its dataset, and a study `included_in` its
   dataset or a larger study. This replaces `part_of` in the study plan's
   widening and in the linked-session plan's membership rule; everything else
   in both stands.

3. **`part_of` is physical again:** the physical types only.

4. **`session_id` is an edge.** `base` loses the field and gains one required
   edge, `session_id`, on every document: the `entity` of type session or
   dataset the document is stored with. A session or dataset entity's
   `base.id` is its session id, so it points at itself (the session's own
   searches, scoped by this edge, must find it). Dataset-level documents
   (people, strains, studies, the dataset) point at the dataset entity. Storage
   scope, never membership: membership is `included_in`.

   - **Migration:** a migrated session entity takes the v1 session id as its
     `base.id`, and every migrated document's `session_id` edge points at it.
     That re-ids one document per session; nothing in v1 refers to the old one.
   - **NDI:** v1 documents keep the field (NDI still writes v1). A query on
     `base.session_id` against a V2 database is answered from the edge, and
     `ndi.document.session_id()` reads whichever the document has.

## Not decided here

- **NDI Cloud.** Its server is in no repository this work can see. If it
  filters or indexes on `base.session_id`, a V2 upload needs a server change or
  an upload step that adds the field back for the server. To ask before
  publishing a V2 dataset.
## Decided with it (Jess Haley, 2026-10-20; tenet text added as PROPOSALS)

- **T5:** pick the relation by what the child is (a portion of the parent's
  material → `part_of`; a separate thing in or on it → `contained_in`; one of a
  group → `member_of`; a record under a record → `included_in`), then check that
  everything its `passes` sends down is true of the child.
- **T-3:** an assertion about a container stays on the container. A plate's
  exclusion does not pass to its worms; `contained_in` keeps `passes: context`.
  An analysis asks the containers, and NDI's reader offers that as one call.
- **T1:** coarse kind is `entity.type`, finer kind one `term_assertion`; an
  entity's own edges are `time_reference_id` and `session_id`.
- **A dataset folder's own record is the dataset entity** (Jess Haley,
  2026-10-20). A dataset folder is opened like a session and has its own
  session id; on this shape the dataset entity's `base.id` is that id, and
  no separate session-type record is written beside it. The folder's
  reference (`.ndi/reference.txt`) is housekeeping and is NOT written into the
  dataset entity's `local_identifier`, so nothing about the disk enters the
  published record.

To be signed: every relation_bindings row declares `passes` (assertions / distributive / context / nothing; no default); records are related by `included_in` (schema:isPartOf, passes nothing) and `part_of` is physical only; `base.session_id` becomes the required `session_id` edge to the session or dataset entity, whose base.id is its session id

TEAM-SIGN-OFF [relation inheritance]: jess / 2026-10-21 -- every relation_bindings row declares `passes` (assertions / distributive / context / nothing; no default); records are related by `included_in` (schema:isPartOf, passes nothing) and `part_of` is physical only; `base.session_id` becomes the required `session_id` edge to the session or dataset entity, whose base.id is its session id; a dataset folder's own record is the dataset entity and its reference stays in reference.txt; T5 picks a relation by what the child is; T17 keeps an assertion about a container on the container; T1 states entity.type for the coarse kind and one term assertion for the finer kind.

## 2026-10-22 -- tenet audit: relation vocabulary and endpoints

Decided by Jess Haley, 2026-10-22 [vocabulary nodes]: every relation name and entity type gets an ontology node, and T19 says relation and entity-type vocabularies are terms like any other (answer "G6a"). K0 ("look fine"): part_of BFO:0000050, included_in schema:isPartOf, member_of RO:0002350; has_author schema:author, cites schema:citation, funded_by schema:funding, issued_by schema:funder, affiliated_with schema:affiliation, has_custodian schema:maintainer, contributed_by schema:contributor, copyright_holder schema:copyrightHolder, input_data schema:isBasedOn, suborganization_of schema:parentOrganization, documented_by schema:subjectOf; new EMPTY terms follows protocol, distributed as, paired with; entity types organism COB:0000022, cell CL:0000000, group NCIT:C43359, device COB:0001300, strain NCIT:C14419, product schema:Product, software IAO:0000010, person NCIT:C25190, organization OBI:0000245, funding NCIT:C16644, dataset NCIT:C47824, publication IAO:0000311, protocol OBI:0000272, session NCIT:C67447. K1 ("k1a"): contained_in is RO:0001025 located in (RO:0001018 is obsolete in RO). K2 ("k2b"): derived_from is narrowed to material that is used up, so RO:0001000 fits. K3 ("k3a"): the prefixes SIO and owl are registered; alternative_of is SIO:000497, same_as is owl:sameAs. K4 ("developed by as producer is probably fine"; reuse where a fit exists): developed_by schema:producer, sold_by OBI:0000647 has_supplier, encountered RO:0002437, awarded_to schema:fundedItem, hosted_by schema:provider; instance_of, distributed_as, paired_with, gene alias mapping and follows_protocol stay EMPTY terms; orthologous gene mapping is a new EMPTY term, EMPTY:0000386, not RO:HOM0000017, which relates genes, not gene lists ("agree"), and both gene-mapping rows keep endpoint types ["term"]. K5 ("a"): sample_of, aliquot_of and passage_of become ONE relation on RO's "derives from part of" (ENVO:01003004); aliquot_of and passage_of are retired (0 writers). L1 ("a"): a relation's stored `name` is the ontology label ("part of", "member of", "derives from part of") and code matches relations by node, in every writer and reader in did-schema, DID-matlab and NDI. Clarified by Jess Haley the same day: the term registry holds nodes, not synonyms; the old snake_case names need no registry entry, because code matches by node and no published V2 data carries them. L2 ("L2 yes"): the same for entity types and channel types. L3 ("L3a"): tissue UBERON:0000479, study NCIT:C63536 Study, material BFO:0000040 material entity, epoch EMPTY:0000383 recording epoch. Built: did-schema dc116fd (stored names are labels; derived_from keeps its handle, see [derived from general]).

Built in did-schema with this line: every node above is a term registry row (EMPTY:0000378-0000383 and 0000386 staged until empty-ontology merges them), each relation row and each entity_type_bindings row carries its node, the prefixes ENVO, SIO and owl are registered (ENVO is needed for ENVO:01003004), and the aliquot_of and passage_of rows are deleted. The stored-name change of L1/L2 was held back at first and is now BUILT (did-schema dc116fd, after DID-matlab fde6a32 and NDI-matlab 3eca6f648 began matching by node), except `derived_from`, see [derived from general]. When this line was written, DID-matlab and NDI matched relations and entity types by these names (NDI `ndi.v2.relationPasses` and `ndi.v2.entityTypesFor`, DID-matlab `did2.validate.entityRequires`, and about 190 lines of NDI writers), so the binding rows keep their handles until those readers match by node; the name change then lands in all three repositories together. No node is decided for entity type `culture` (the draft table's OBI:0001876 cell culture was not ruled on), so its node stays empty.

Decided by Jess Haley, 2026-10-22 [member_of endpoints]: `member_of` has parent_types [group], and its child_types add `software` (answer "a sounds fine").

Decided by Jess Haley, 2026-10-22 [contained_in endpoints]: `contained_in` child and parent types are the physical entities (organism, culture, tissue, cell, material, device, group); records use `included_in` (answer "I2a").

Decided by Jess Haley, 2026-10-22 [clock alignment relation bound]: `clock_alignment.relation` is bound to the closed list of kinds resolveClockAlignment.m writes, with a relation_bindings row that passes nothing (answer "G3a"). Built: the `clock_alignment` row ("temporally aligned with", the one kind DID-matlab's jClockAlignmentBodies writes for resolveClockAlignment), whose values tools/validate_v_eta.py derives onto the field (D3). No node is decided for it.

Decided by Jess Haley, 2026-10-22 [distance]: `measured_distance_to` is retired. A distance is an observation or a calculation, variable PATO:0000040 (or the O3 term), about the measured-from entity; the reference is a `document` condition when it is fixed, or a covariate along time when it changes (answer "G5a").

Decided by Jess Haley, 2026-10-22 [derived from general]: `derived_from` is the general "derived from", node prov:wasDerivedFrom (W3C PROV: the construction of a new entity based on a pre-existing one), replacing RO:0001000, whose "the source ceases to exist" fits none of its writers (strain from background strain, neuron from recording subject, element lineage, treatment transfer, Haley seeding); this supersedes K2 (b) of [vocabulary nodes] (answer "1a"). Built: DID-matlab af27912 (node read from the binding row, compared by node); NDI-matlab 3eca6f648 (reads both nodes, writers take the row's node; no hard-coded RO:0001000 left). Build pending: did-schema (row node and name: PROV-O's rdfs:label for prov:wasDerivedFrom is "wasDerivedFrom", which DID-matlab did2.build.vocabulary cannot map to derived_from; the `prov` prefix is registered in dc116fd).

Decided by Jess Haley, 2026-10-22 [lawn in plate]: a bacterial lawn is `contained_in` its plate, not `member_of` it: a plate is a material, not a group, so [member_of endpoints] rejects it, and [contained_in endpoints] already allows material to material (answer "A2 a"). The plate's statements pass to the lawn as `context`, not `distributive`. Built: DID-matlab 5ca5825 (`+did2/+convert/resolveLawnPlateSubjects.m` writes contained_in; the file is DID's, not NDI's as first written here). NDI's own Haley V2 import already writes patch contained_in plate.
