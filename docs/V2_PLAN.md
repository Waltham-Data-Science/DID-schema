# V2 migration plan

This is the working plan, not the record. Decisions live in their `Decided by`
lines, mostly in `schemas/V_eta_go_forward_class_audit.md`. Open work is
indexed in `schemas/V_eta_OPEN_WORK.md`. When this file and either of those
disagree, they win.

Last updated 2026-10-26.

## The goal

1. **The generic migration of v1 is lossless.** Every v1 document either
   lands in a V2 shape or is carried unchanged as v1. Nothing is dropped and
   nothing is invented. A value may be dropped only if V2 can be migrated
   back to v1 without it ([lossless means round trip]). The generic stage
   writes V2 only when the v1 document alone gives exactly one correct
   reading ([one correct reading]).
2. **Every carry has a reason on record.** Each reason is a row in the carry
   register (`schemas/V_eta_carry_register.json`, [carry register]):
   awaiting a home, needs a dataset mapping, not modelled, or malformed. An
   awaiting-home row must point at an open OPEN_WORK row
   ([awaiting home is tracked]).
3. **Carried documents are fixed later**, one of two ways:
   - a **V2 home**, a schema decision. Once it is built, the generic
     migration converts that case.
   - a **dataset map**, for meaning only that dataset knows. It runs after
     the generic migration and may also refine V2 documents the generic
     stage wrote ([dataset map edits V2]).

## Where we are

| step | state |
|---|---|
| Document stamps `did_v1` / `did_v2` | done |
| No invented values | done |
| Lossless rule: a partly placed document is carried as v1 | done (DID #247, NDI #1067) |
| Drop census: 14 questions | answered; decisions recorded (did-schema #128) |
| Census builds | done: did-schema #131, empty-ontology #26 and #27, DID-matlab #250, NDI-matlab #1072 |
| Dataset-specific logic out of the generic migration | done for Haley (covered by the Haley V2 import) and JH; **Babu is now covered by nothing** (see question 7) |
| Schema set renamed `did_v2` (did-schema part) | done (#132); siblings still accept both names |
| Carry register and its gate | did-schema #134, CI green, waiting to merge |
| Dataset map: may edit V2 documents; one file per dataset in NDI-matlab, its own step | decided (#141) |

## What's next, in order

1. **Merge the carry register** (#134). Then DID-matlab and NDI-matlab make
   every carry note cite its register row, with a test.
2. **Build the dataset map.** First the open design questions (below), then
   the step that applies a map, then the Dab map (sliceTetanus moves out of
   the generic second pass, [sliceTetanus to Dab map]). The design draft is
   `docs/v2_working/DATASET_MAP_PROPOSAL.md`.
3. **The remaining questions** below.
4. **The remaining renames**, siblings first: `description` becomes `notes`;
   the retired classes and `deprecated/` leave the V2 set; DID-matlab and
   NDI-matlab drop the old `V_eta` name. These take one more corpus run, so
   they are batched with the code the questions produce.
5. **Markdown out of `schemas/`**, once the delete list is approved
   (`docs/v2_working/MARKDOWN_PLAN.md`).
6. **Haley re-run** (Jess), then the remaining dataset maps.
7. **v1 set in did-schema** (decided): once NDI's V2 replaces v1, the v1
   definitions move into did-schema as a frozen `did_v1` set.

## Open questions for the team

Dataset map:

1. (Decided, [dataset map location]: one file per dataset in NDI-matlab,
   applied by its own step on the written V2 database.)
2. Does the Haley dataset need a map, or does its V2 import cover
   everything?
3. May a map row match on label words, or only on exact v1 values?
4. An opto animal with a target-location treatment but no tetanus run:
   carry it as v1, or record a term assertion on the animal?
5. Should Claude draft the Dab EPM / FPS column rows for review?
6. Where does the Dab reproduction test live (NDI or DID)?
7. Babu: a map, or a V2 import from the source data? Its media and heat
   routing is now covered by nothing.

Migration:

8. Bath variable: a bath statement's variable is the first mixture row
   (1,172 Dab ACSF baths say "sodium chloride"). One fixed generic variable,
   or the manipulated ingredient named by the dataset map?
9. Element entity types: should "device" be used only for direct
   acquisition elements?
10. 20211116: its 252 element epochs cannot be tied to an acquisition system,
    so they are carried. Option: keep the session-anchored reference when
    all of an epoch's extents come from one untied source and agree.
11. Ingested sessions: where does `session_reference` go, and what happens
    to an ingested session's creator class? 48 documents are carried until
    this is answered.
12. `chooseLevel` can pick a level that stores no bytes when two levels tie.
    Should it skip file-less levels?
13. NDI `get_ingested_document` looks up the ingested stimulus file by
    epoch id and reader id, which the converted body no longer has. Not
    checked.
14. openMINDS: the crosswalk has no technique or data-type entries, and a
    test note says dataset terms are "not openMINDS instance IRIs", which
    sits uneasily with T2.

## Working documents

`docs/v2_working/` holds the research behind recent decisions. These are
proposals and measurements at the commits they name, not the record:

| file | what it is |
|---|---|
| `DROP_CENSUS.md` | the 14 drop-census questions |
| `carry_fields_TABLE.md` | which v1 fields blocked a fold (lossless carries) |
| `DATASET_SPECIFIC_AUDIT.md` | dataset-specific logic in the generic migration |
| `ONE_READING_REVIEW.md` | the one-correct-reading review |
| `TERMS_PROPOSAL.md` | the census terms proposal |
| `MARKDOWN_PLAN.md` | which Markdown under `schemas/` to delete or move |
| `DATASET_MAP_PROPOSAL.md` | the dataset map design draft |

## How we work

- Claude asks questions one at a time, or in small batches if they are
  simple, in plain terms, naming the document types.
- A decision is recorded only when a team member says it, in their words.
- DID-matlab merges before NDI-matlab. A schema change the siblings must
  follow lands in the siblings first.
- CI: pushes to a branch with no PR run the quick checks only. Open one PR
  per repository once its work is in, so the corpora run once.
