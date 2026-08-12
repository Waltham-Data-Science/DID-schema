# V_eta — `logical` / `logical_observation`, and what `valid_interval` becomes

*The plan document for the `valid_interval` family. Written 2026-08-12 to hold decisions the
team made that day and that had no home: the family carried `plan: None` in
`tools/status_board.py`, and `status_board.py --check` fails a family citing a document that
does not exist.*

**THIS DOCUMENT CARRIES NO SIGNATURE LINE, DELIBERATELY.** Operating Rule 4 forbids Claude
writing one, and this family has a specific history with that rule: on 2026-08-11 a QUESTION
the team asked was written up as their decision and put into a signature under their name
(`V_eta_OPEN_WORK.md` #103). **This document was written with NO signature, deliberately, and
the team dictated one on 2026-08-12 — it is at the foot of the file.** The decisions
transcribed below are real, and the signature was a separate act by a human, which is the
whole point of the rule. Its scope is NARROWER than this document: the open items in §7 are
outside it.

Decisions below are attributed in prose: **jess@walthamdatascience.com, 2026-08-12**, unless
another date is given.

---

## 0. State, in one table

| thing | state |
|---|---|
| `logical` + `logical_observation` schemas | **BUILT** (`draft` tier), replacing `validity` / `validity_observation` |
| `valid_interval` v1 tombstone | **BUILT and KEPT** — every source document lives here today |
| `did2.convert.resolveValidIntervals` | **DORMANT BY DECISION** — runs as a census, emits nothing |
| the migration model | **DECIDED: the ARRAY model**, and it **waits on `axes[]`** (#45 → #32) |
| the four reading rules | **DECIDED and DECLARED on the class** |
| a signature | **absent, correctly** |

---

## 1. The naming: `validity` → `logical`

**Decision.** `validity` and `validity_observation` are replaced by `logical` and
`logical_observation`.

**Why.** The 32 `*_observation` data_types name a **kind of value** — length, intensity,
count, score, term, image. `validity` was the only one naming a **semantic**: what the
measurement is *about*. The semantic belongs in `subject_statement.variable`.

That is not a theory about how the system should work; it is what the system already does.
`DID-matlab src/did/+did2/+convert/resolveLawnPlateSubjects.m:1106-1113` maps eight source
columns onto three data_types, **six of them onto the single `intensity_observation`**, told
apart only by `variable` (`:689 variableTerm(c{1})` → `:1317
body.subject_statement.variable`):

    bacterialpatchborderpeakfluorescenceintensity   intensity_observation
    bacterialpatchborderedgefluorescenceintensity   intensity_observation
    bacterialpatchborderfluorescenceamplitude       intensity_observation
    bacterialpatchmeanfluorescenceamplitude         intensity_observation
    bacterialpatchcenterfluorescenceamplitude       intensity_observation
    bacterialpatchbordertocenterfluorescenceratio   intensity_observation

It is also the error **R2/R3 already fixed one tier up**: six v1 tuning classes named by their
*independent variable* collapsed into one `tuning_curve` carrying that variable as a
`variable` (T11, `V_eta_tuning_model_plan.md`). `validity_observation` is the same mistake in
the same shape.

**Why not `boolean`.** It is impossible, not merely inelegant. `boolean` is a hard-coded
primitive in the validator's type switch — `DID-matlab src/did/+did2/+schema/cache.m:1793`:

    case 'boolean'
        if ~(islogical(value) || (isnumeric(value) && all(value(:) == 0 | value(:) == 1)))
            error('did2:validation:typeMismatch', ...

A composite named `boolean` would send every struct-valued field carrying it into that
scalar/array check.

**Why `logical` works.** It follows the existing precedent exactly:

| data_type (class) | field type it wraps |
|---|---|
| `term` | `ontology_term` |
| `logical` | `boolean` |

Different strings, no collision, same shape. The class name is **not** registered in the
meta-schema's `field_definition.type` enum — nothing declares a field *of type* `logical`, and
an enum member with no declared sub-fields would fail
`test_named_composite_cells_declare_their_layout`.

---

## 2. The shape: a bare value, no wrapper cell

    logical
      value   type `boolean`   mustBeScalar FALSE   mustBeNonEmpty TRUE   blank []

    logical_observation ⊂ {subject_observation, logical}
      (no fields at all)

**Decision.** `logical.value` is a bare boolean array. The `validity` shape it replaces was a
`value` of type `validity` wrapping a one-field struct `{value: boolean}` — i.e.
`value.value`, a wrapper around nothing.

**Why the other composites nest, and why this one does not.** They nest to carry
**provenance**: `length` wraps meters + `source_unit` + `source_value`; `count` wraps value +
a semantic unit + `approximate`. A truth value has no unit, no source unit, and cannot be
approximate. The precedent for a bare payload is `term`, whose `value` is typed
`ontology_term` directly. `logical_observation` declares **no fields at all**, the same as
`length_observation` and `count_observation`.

`default_value` is `[]`, matching `blank_value`. The old `validity` default was
`[{"value": true}]` — a validity-specific assumption that a *generic* boolean class must not
bake in. Required non-scalar fields with an empty default already exist
(`formulation.value.chemicals`, `distance_metadata.endpoints`, `acquisition_epoch.clocks`), so
this is the established shape, and the migrator sets the value explicitly in any case.

---

## 3. `sequence` is deleted, and the hazard it existed for is resolved

**HAZARD 2 used to read "ORDER IS LOAD-BEARING".** The premise was that
`NDI +ndi/+app/+stimulus/tuning_response.m:253-256` reads *the first entry of the stored
array*, so v1's append order (`markgarbage.m:89`, `vi(end+1) = validintervalstruct`) had to
survive the decomposition — carried in `logical_observation.sequence`.

**The premise is false.** Positive evidence, from NDI `origin/main` (`42c94e53b`):

    $ git show origin/main:src/ndi/+ndi/+app/+stimulus/tuning_response.m
      253:  vi       = gapp.loadvalidinterval(ndi_timeseries_obj);
      254:  interval = gapp.identifyvalidintervals(ndi_timeseries_obj,timeref,0,Inf);
      256:  [data,t_raw,timeref] = readtimeseries(..., interval(1,1), interval(1,2));

`interval` is the **return value of `identifyvalidintervals`**. The stored array `vi` is
loaded at `:253` into a variable that is then never read again. And `identifyvalidintervals`
(`markgarbage.m:178-196`) is:

    for i=1:size(vi,1)
        ...
        explicitly_good_intervals = vlt.math.interval_add( ...
            explicitly_good_intervals, [epoch_t0_out epoch_t1_out]);
    end

— it iterates **every** row and accumulates through a **set union**. It never indexes `vi` by
position. So v1's append order is invisible to its only consumer: a storage artifact, not a
fact.

**Limit of this check, stated rather than glossed.** `vlt.math.interval_add` lives in
`vhlab-toolbox-matlab`, which was not available in the container where this was re-verified,
so whether the union sorts its output was not read from source. The conclusion does not depend
on it: `interval(1,1)` indexes the union's output either way, and one source document's rows
are unordered *input* to that union.

**The shape of the error is the part worth keeping.** The schema declared `sequence`, the
migrator emitted it, and two MATLAB tests asserted it — three artifacts written from **one**
unchecked reading of a call site. That is CLAUDE.md's *"a test written from the same premise
as the code cannot catch the code."* The replacement test pins the deletion rather than
removing the assertion.

---

## 4. The migration model: the ARRAY, and it waits for `axes[]`

**Decision.** The target is **ONE `logical_observation` per source document**, carrying an
**array of booleans** with the intervals on a **time axis**.

**The 1→N decomposition is explicitly rejected as an interim step.** Verbatim: *"Axes is the
decision… I'd rather wait until axes is built and it can be migrated properly."*

Consequences, all built:

* `did2.convert.resolveValidIntervals` is **dormant**. It still runs, still reports, and
  **emits nothing**. `options.Decompose` (default **false**) guards the emission path.
* The decomposition logic is **preserved, not deleted** — the anchor resolution, the
  `(session, epoch-id)` pair keying, Decision C's split-anchor branch, the verb resolution and
  the eight refusal reasons are all needed unchanged when the array model is built; only the
  shape of the emitted body changes. `testValidIntervalDecompose.m` arms the flag so the
  preserved logic keeps being exercised rather than rotting unreferenced.
* The pass still **counts**: `sources_seen` and `intervals_seen` are the only measurement
  anyone has of how much `valid_interval` data is waiting on `axes[]`. Every emission counter
  is 0 **by decision**; every `refused_*` counter is 0 because it **was not evaluated**, which
  is not the same as "nothing was refused". `dormant` is reported as its own field.
* `valid_interval` documents live on their **v1 tombstone**, which declares nothing required
  and an optional `element_id`, so a passthrough cannot trip `mustBeNonEmpty` or
  `undeclaredField`.

**What unblocks it:** `axes[]` on `subject_statement` — `V_eta_data_body_model_plan.md`,
`V_eta_OPEN_WORK.md` #45, itself blocked on #32. Until that lands there is nowhere to put a
time axis, and a boolean array with no axis cannot say which stretch each element is about.

---

## 5. The four reading rules (team, 2026-08-12)

These govern **V_eta consumers**. They change nothing about `ndi.app.markgarbage`'s v1
behaviour, and no consumer is being written here. They are **declared on the class**
(`logical.value.documentation`) and not left in this document, for the same reason the absence
rule is (T14): a consumer that never read our prose still has to get them right, and every way
of getting them wrong is silent.

### RULE 0 (pre-existing, unchanged) — absence means VALID

Absence of *every* `logical` statement about a subject's **data validity** means its data is
valid. `ndi.app.markgarbage` is opt-in and `identifyvalidintervals` returns the whole requested
span when it finds no record (`markgarbage.m:174-177`).

The rule is now **scoped by `variable`**, and that scoping is load-bearing: `validity` named
the semantic, so "no statement of this class" and "no statement about data validity" were one
sentence. Under a generic `logical` they are not — a subject with no statement about some
other boolean says nothing about its data validity.

It is scoped to **no statement at all** and does **not** extend to the gaps *between*
statements. See the open items.

### RULE 1 — inheritance walks the whole `derived_from` chain, transitively

A subject with no `logical_observation` for a given `variable` inherits from its
`derived_from` ancestors, **to any depth** — electrode → filtered → neuron reaches the
electrode. The chain is in the migrated graph: `migrators_j/element.m:130-131` emits a
`derived_from` lineage relation for every `underlying_element_id`.

**A CORRECTION TO HOW THIS WAS PUT TO ME, recorded because Rule 3 forbids contradicting a
comment on absence and requires positive evidence for contradicting one on presence.** This
rule was handed over with the justification that NDI's `loadvalidinterval` *"checks
`underlying_element` exactly ONCE and does not recurse — so in NDI, electrode → filtered →
neuron never reaches the electrode."* **That is not what the code does.** From NDI
`origin/main`, `markgarbage.m:145-155`:

    145:  if isempty(vi) % underlying elements could still have garbage intervals
    147:      if isprop(ndi_epochset_obj,'underlying_element')
    148:          if ~isempty(ndi_epochset_obj.underlying_element)
    149:              [vi_try,mydoc_try] = ndi_app_markgarbage_obj.loadvalidinterval( ...
                          ndi_epochset_obj.underlying_element);

`:149` is a call to `loadvalidinterval` — the *same function*, which contains this same
fallback block. **It recurses, to any depth.** So depth is not the divergence, and the rule
should not be justified on it.

**What the real divergences are:**

1. **The edge.** NDI walks `underlying_element`, a property of a live NDI runtime object.
   V_eta walks `derived_from`, an edge in the migrated *document* graph — the only lineage a
   consumer holding documents can see. These are the same lineage only because
   `element.m:130-131` makes them so.
2. **The scope.** v1 has exactly one kind of validity and no `variable`, so its walk cannot be
   scoped and this one **must** be: inheriting a statement about some other boolean variable
   would be a different fact altogether.

The rule as decided is unaffected — it is what V_eta will do. Only the stated reason changes.

### RULE 2 — inheritance yields the statement **with its anchor**

Never the interval numbers alone. The times mean nothing without the `time_reference_#` that
anchors them, so an inheriting consumer converts through the syncgraph exactly as if it had
asked about the ancestor directly.

**This mirrors v1 rather than diverging from it**, and that is checkable —
`identifyvalidintervals` rebuilds each interval's own anchor and converts into the caller's
frame (`markgarbage.m:181-189`):

    181:  interval_t0_timeref = ndi.time.timereference(ndi_app_markgarbage_obj.session, vi(i).timeref_structt0);
    182:  interval_t1_timeref = ndi.time.timereference(ndi_app_markgarbage_obj.session, vi(i).timeref_structt1);
    184:  [epoch_t0_out, epoch_t0_timeref, ~] = ...
    185:      ndi_app_markgarbage_obj.session.syncgraph.time_convert(interval_t0_timeref, ...
    186:      vi(i).t0, timeref.referent, timeref.clocktype);

### RULE 3 — three states, not two. A deliberate break from v1.

| what the consumer finds | what it means |
|---|---|
| no statement anywhere in the chain | **VALID** (Rule 0, unchanged) |
| statements found and projected | **use them** |
| statements found, **none** projectable into the caller's frame | **UNKNOWN — NOT VALID** |

**In v1 the third collapses into the first.** An unprojectable interval is skipped with the
author's own comment (`markgarbage.m:190`):

    190:      % so we say the region is valid, we have no restrictions to add

and if none projects, the function returns the **entire requested span**
(`markgarbage.m:198-199`):

    198:  if isempty(explicitly_good_intervals)
    199:      intervals = baseline_interval;

So in v1, a clock mismatch silently reads as *"all of this data is good"*.

The two facts are **opposites** — "nobody marked this" versus "somebody marked this and we
could not read their clock" — and only the first should read as good data.

**RULE 1 makes this matter MORE often, not less.** Walking the whole chain multiplies the
chances of reaching an ancestor whose anchor does not project.

### RULE 4 — the failure must be countable

A consumer **reports** the number of inherited statements it could not project.

A silent permissive fallback is the exact failure this project keeps paying for — `silentLoss`
printed "0 empty edges" for two days while reading nothing. Rule 3 is unenforceable without a
number: "unknown" and "valid" are indistinguishable in the output otherwise.

---

## 6. The other two hazards, retargeted and intact

**HAZARD 1 — absence must keep meaning "valid".** Mechanically gated:
`tests/test_veta.py::test_absence_of_a_logical_statement_must_keep_meaning_valid` fails if any
schema declares a *required* edge to `logical` / `logical_observation`, or if `logical` gains
a second subclass, or if the declared absence rule loses either its wording or its `variable`
scoping. Nothing may require one.

*(The build comment used to cite a gate named `test_validity_is_never_required_by_anything`.
No test has ever existed under that name in this repository; the assertion is the first half
of the test named above. Corrected rather than reproduced.)*

**HAZARD 3 — inheritance.** RULE 1 above now answers *how* a consumer inherits. It does **not**
answer whether V_eta should ever **materialise** copies onto derived subjects instead of
re-deriving at read time. Nothing forecloses either answer: `subject_id` is the element the v1
document named and nothing else, and `subject_observation.derived_from_#` exists and is
optional. `tests/test_veta.py::test_logical_forecloses_neither_answer_on_the_inheritance_question`
is the gate.

---

## 7. Open items — not decided, not to be treated as decided

1. **What a GAP between statements means.** Deferred by the team on 2026-08-11 and still open.
   The absence rule is scoped to *no statement at all*; it does **not** extend to a gap. In v1
   the answer is the opposite: `markvalidinterval` marks a valid interval *"(all else is
   garbage)"* (`markgarbage.m:42`), and once any interval projects into an epoch,
   `identifyvalidintervals` returns **only** the marked ones (`markgarbage.m:198-201`) — so a
   v1 gap is garbage. Decomposing one v1 document into N statements does not carry that
   closure, so it is deliberately **not claimed** rather than silently inverted. The array
   model may dissolve this question entirely (one statement, one axis, no gaps between
   siblings), which is one more reason not to answer it before `axes[]` lands.
2. **Whether `axes[]` lands before any `valid_interval` migration.** Today the answer is yes by
   construction — the pass is dormant. If that ordering ever changes, it is a decision, not a
   default.
3. **Materialise vs re-derive** (HAZARD 3 above).
4. ~~**The signature.**~~ **SIGNED 2026-08-12** — see the TEAM-SIGN-OFF line at the foot of
   this document. It was dictated by the team and transcribed verbatim; one clause was
   CORRECTED before it was written, because the draft justified transitive inheritance as a
   *divergence* from NDI on the claim that `loadvalidinterval` checks `underlying_element`
   exactly once. That claim was false — the function calls ITSELF, so it already recurses to
   any depth — and signing the draft would have put a false justification into the record.
   The signature says *matching NDI* and names the real divergences instead. The items above
   (1-3) are NOT covered by it and remain open.

---

## 8. Where the code is

| file | what it holds |
|---|---|
| `tools/build_v_eta.py` (`logical` block) | the two schemas, the naming argument, the three hazards, the declared reading rules |
| `tests/test_veta.py` (`logical` block) | four tests, one per hazard plus the shape |
| `DID-matlab src/did/+did2/+convert/resolveValidIntervals.m` | the dormant pass + the preserved decomposition |
| `DID-matlab tests/+did2/+unittest/testValidIntervalDecompose.m` | dormancy gate + the preserved logic, armed |
| `DID-matlab tools/census_digest.py` | how the dormant report renders |
| `schemas/V_eta_migration_targets.json` (`valid_interval`) | the ledger's account of all of the above |

## TEAM SIGN-OFF

TEAM-SIGN-OFF [logical_observation]: jess@walthamdatascience.com / 2026-08-12 -- `validity` and `validity_observation` are replaced by `logical` + `logical_observation`; the semantic moves to `subject_statement.variable`, since a data_type names the KIND of value and not what it is about. `logical` carries ONE field, `value` typed `boolean` with mustBeScalar false -- a bare array, no wrapper cell (`boolean` is impossible as a class name: it is a primitive in the validator's type switch, cache.m:1793; `logical`:`boolean` mirrors the existing `term`:`ontology_term`). `logical_observation` declares no fields. `sequence` is deleted: NDI never reads interval order, because identifyvalidintervals accumulates through interval_add, a set union, and tuning_response.m:256 indexes THAT union rather than the stored array. THE ARRAY IS THE TARGET MODEL -- one statement per source document holding N booleans against a time axis -- and the 1->N decomposition is NOT shipped as an interim: migration WAITS for `axes[]` on `subject_statement` rather than migrating twice, so the pass is dormant by decision. Inheritance walks the whole `derived_from` chain TRANSITIVELY, MATCHING NDI, whose `loadvalidinterval` calls ITSELF on `underlying_element` and so already recurses to any depth; the divergences are the EDGE (V_eta walks `derived_from` in the migrated document graph, NDI walks a runtime object property) and the SCOPE (v1 has no `variable`, so its fallback cannot be per-variable). Inheritance yields the statement WITH ITS ANCHOR, never the interval numbers alone. Three states, a deliberate break from v1: no statement anywhere -> VALID; statements projected -> use them; statements found but none projectable into the caller's frame -> UNKNOWN, NOT VALID (v1 returns the entire requested span, so a clock mismatch reads as "all data good"). Consumers must count inherited statements they could not project. NOT COVERED BY THIS SIGNATURE: the gap semantics between statements (still undefined, still open), the timing of `axes[]`, and any change to ndi.app.markgarbage's v1 reader behaviour.
