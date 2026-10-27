# V_eta: one thing recorded twice (`same_as`)

SIGNED 2026-10-19 (the `TEAM-SIGN-OFF [same_as]` line is under the "To be signed:"
line). Written 2026-10-14 at Jess Haley's request. BUILT 2026-10-20, not yet run in
MATLAB: tenet T18 in `did_v2_tenets.md`; the schema needed no change (`same_as` was
already bound, member types `entity`); the reader and the join are in NDI-matlab
(`ndi.entity` search and statements follow a `same_as` group, `ndi.entity/sameAs`
and `/disagreements`, `ndi.v2.sameAs`, `ndi.v2.sameAsMatches`, and
`ndi.dataset/add_linked_session` / `add_ingested_session` with `same_as_report`;
test `TestSameAs`). The physical merge is not built (not decided).

## The question

When a session made on its own joins a dataset, it can bring its own entity
for something the dataset already records: its own N2 strain, its own record
of a person, its own record of the microscope. Two documents then describe one
thing. This plan says how that is recorded, and, as important, when it is not.

## What exists

`same_as` is already a relation: an `undirected_relation` term, member types
`entity`, role "entities that are the same thing recorded twice (e.g. one
animal under two local identifiers)" (`binding_registry_meta.json`, #73 audit 2
D5). `did_v2_SPEC.md` adds that `same_as` "makes search *unify* the two records".
Nothing says when two records may be joined by it, and no reader follows it.

## Proposed tenet T18

> **T18 — `same_as` joins two records of one thing; it never joins two things of
> one kind.**
>
> Two entity documents are `same_as` only when they describe the very same
> thing: the same strain, the same person, the same physical instrument, the
> same animal. Two different things that are alike are not the same thing, and
> are never `same_as`:
>
> - a second instance of a kind is its own entity, `instance_of` the kind (T17's
>   fourth path): a second microscope of one model is `instance_of` the same
>   `product`; a second N2 worm is `instance_of` the same strain. They share the
>   kind through that relation and need nothing between them;
> - two records of the KIND itself are the duplicate: two N2 strain entities
>   are one strain, so they are `same_as`.
>
> **No id is deleted or rewritten to join them.** Both documents stay, with
> their ids, so every reference to either still resolves and the join can be
> undone by deleting the relation.

## How a match is found

A `same_as` is written only on evidence that names the thing itself:

| evidence | names | joins |
|---|---|---|
| the same identifier CURIE (`wormbase:WBStrain00000001`, `orcid:…`, `rrid:…`) on two entities of the same type | that strain, person or resource | the two entities |
| the same serial number (and manufacturer) on two devices | one instrument | the two devices |
| the same catalog / model number on two products | one product | the two products |

and never on:

- a shared kind: two devices with the same model number, or none, are two
  instruments until something names each one; two worms of one strain are two
  worms;
- a shared name alone: two entities called "N2" with no identifier may be two
  stocks. They are listed for a person to confirm, and the confirmation writes
  the `same_as`.

So the identifier must sit on the entity it identifies: a catalog number on the
`product`, a serial number on the device, a WBStrain id on the strain. A model
number recorded on a device would make every device of that model look like one.

## Where it is stored

In the dataset's database, like the `part_of` relations that make a session a
member (`did_v2_linked_session_plan.md`): that two sessions' records are one
thing is a fact about the dataset that holds both. A linked session's folder is
not written to.

## How it is read (for the build, after signing)

- A search treats a `same_as` group as one entity: searching for N2 finds the
  instances of either record.
- What is asserted of either record holds of the group (and, through
  `instance_of`, of each instance). Where the two disagree on a value, the
  reader reports the disagreement and does not pick one.
- Joining a session to a dataset reports the matches it found (written) and the
  name-only candidates (listed, not written).

## Not decided here

- **A physical merge**, keeping one record and pointing every edge at it, e.g.
  for a published dataset. If ever wanted, it must leave a redirect from each
  removed id to the one kept, so old references still resolve. A later decision.

To be signed: same_as joins two records of one thing and never two instances of one kind (tenet T18); it is written only on an identifier that names the thing itself, stored in the dataset, and no id is deleted or rewritten
TEAM-SIGN-OFF [same_as]: jess@walthamdatascience.com / 2026-10-19 -- as the To be signed line above states.
