# V_eta: what a relation passes, records' own relation, and `session_id` as an edge

Written 2026-10-20 at Jess Haley's request, from the Haley import's tenet audit
(T-1). A PROPOSAL, built ahead of signature at her request ("build it",
2026-10-20); there is no `TEAM-SIGN-OFF` line yet. Built in did-schema#88
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

To be signed: every relation_bindings row declares `passes` (assertions / distributive / context / nothing; no default); records are related by `included_in` (schema:isPartOf, passes nothing) and `part_of` is physical only; `base.session_id` becomes the required `session_id` edge to the session or dataset entity, whose base.id is its session id
