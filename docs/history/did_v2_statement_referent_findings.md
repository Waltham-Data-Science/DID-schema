# V_eta — who can a statement be about? FACTS + one open question

**NOTHING HERE IS DECIDED.** This document exists because the question below has
now surfaced **twice from unrelated families**, was explored in depth in a
walkthrough, and was about to be lost to a compaction with nothing written down.
The measurements are re-derivable with the commands shown; the options are options.

## The gap, stated once

V_eta has **statement-level provenance and no session-level provenance.**

Two independent families hit it:

1. **openMINDS import** (`V_eta_openminds_family_record.md`, Part 1) — *"this
   dataset was imported by crosswalk vX"*. `openminds_import` hung off `dataset`.
2. **DAQ configuration** (`V_eta_daq_family_decisions.md`) — *"this session was
   acquired using reader X with parameters Y"*. 96 `daqsystem` documents in Soph
   against 181,760 migrated documents.

`method`, `method_parameters`, `software_id`, `instrument_id` and
`execution_environment` all live on **`subject_interaction`** — that is, on
statements about a **subject**. Neither case is a statement about a subject.

## FACT 1 — the referent is genuinely constrained today

```json
// subject_statement.depends_on
{ "name": "subject_id", "mustBeNonEmpty": true,
  "must_refer_to_document_class": "subject",
  "documentation": "The subject this statement is about (the finest entity the
                    value directly describes; Brainstorm J objective-annotation rule)." }
```

This is not a loose edge. It declares `subject`.

## FACT 2 — provenance lives on the INTERACTION tier, not the assertion tier

```
subject_statement    fields=[variable, conditions, storage_mode]   deps=[subject_id]
subject_assertion    fields=[]                                     deps=[]
subject_interaction  fields=[method, method_parameters, sample_time,
                             execution_environment]
                     deps=[time_reference_#, instrument_id, software_id]
subject_observation  deps=[derived_from_#]
```

`subject_assertion` has **zero fields and zero dependencies.** That is by design —
an assertion is a *timeless fact with no act*. **So an `entity_assertion` family
could not carry provenance at all**, which rules out the cheapest-looking option.

## FACT 3 — there is no valueless-act class, anywhere

```
DENOMINATOR: 222 classes scanned
CONCRETE descendants of subject_interaction : 46
  ...that pair with a data_type             : 46
  ...with NO data_type (a bare act)          :  0
```

Every statement in V_eta carries a measured value. That is T3 (`leaf = direction ×
data_type`) applied rigorously, with zero exceptions.

**So the gap is TWO-dimensional, not one:** provenance fails because its referent is
not a subject **and** because it has no value.

## FACT 4 — the blast radius of a rename

```
DENOMINATOR: 222 classes scanned
  descendants of subject_statement    : 81
  descendants of subject_interaction  : 49
  descendants of entity               :  9
     dataset funding organization person publication session software subject web_resource

migrator files writing subject_id   : 29
subject_id occurrences in migrators : 82
```

## THE OPTIONS (none adopted)

**A — widen the referent.** `must_refer_to_document_class: "subject"` → `"entity"`.
**One declaration.** Closes both instances with slots that already exist:

```
session acquired:  subject_id → session   method → "data acquisition"
                   software_id → the reader software entity
                   method_parameters → {fileparameters, …}
dataset imported:  subject_id → dataset   method → "metadata import"
                   software_id → the crosswalk software entity
```

*For:* T1 says *"the subject is a bare identity; there is no privileged level"* —
restricting **who may be spoken about** to one tier is itself a privileged level.
*Against:* the referent edge becomes polymorphic, so "all observations of subject X"
is no longer guaranteed homogeneous. That is a family resemblance to the
`specimen.species` Species-or-Strain slot which V_eta deliberately REJECTED (see
the openMINDS record, Parts 4–5) — not identical, but close enough to name.
*Also:* the five `subject_defining` bindings (species, instrument type, cell type,
material type, developmental stage) would need re-reading if a referent can be a
session. Lands in #32.
*NOTE:* widening alone is **not sufficient** — by FACT 3 there is still no concrete
class to instantiate for a valueless act.

**B — rename the spine `subject_*` → `entity_*`.** Separable from A, and much more
expensive: 81 classes, 82 migrator sites, every test, the ledger.
*Against, on the tenets' own terms:* T13 says name at the concept's altitude.
`entity_statement` names the referent's **tier** (an implementation fact);
`subject_statement` names its **role in the statement** — and "subject" in the
grammatical sense stays accurate when the referent is a session. Role is the higher
altitude, so the rename may go the wrong way.

**C — add ONE bare-act class.** An interaction with a non-subject referent and no
data_type. On the meta-principle litmus (*which of the four axes is genuinely new —
the subject, the direction, the data-type structure, or the relation?*) the answer
would be **the subject**, so it arguably passes. One class, no leaves.

**D — a full parallel `entity_*` family.** Preserves query homogeneity, but the leaf
tier doubles: 46 concrete interaction classes would need entity twins. That is the
zoo J exists to collapse, and it encodes the referent's *tier* in the class name — a
"where", which the meta-principle rules out. **Not recommended.**

**E — attach provenance to the statements the software actually produced.** Under
TaskList #30 raw recordings become `<modality>_observation`s, which already have
`software_id` and `method_parameters`. Zero schema change.
*Against:* `method_parameters` is an INLINE structure, so it does not deduplicate —
one per-session fact would be stamped onto ~180,000 documents, which is the
`app`-into-16-classes failure R1 exists to prevent. And it is blocked on #30.

## How the two instances were ACTUALLY resolved (neither used A–E)

- **daq**: `daqsystem` survives as `acquisition_system`, which was *already* the
  per-session configuration bundle — id and `base.name` preserved, parameters in
  declared fields. No new tier needed.
- **openMINDS import**: the class was removed; `software_id`-above-
  `subject_interaction` is recorded as an unresolved carry-forward.

**So the gap is currently WORKED AROUND, not closed.** Both resolutions happened to
have a per-session document available to hang things on. A family without one would
re-open this immediately — which is why it is written down rather than left in a
walkthrough that no longer exists.
