# V_eta — the stimulus parameters family: dissolve one, pass the other through

**DECIDED with the team 2026-08-06; SIGNED OFF 2026-08-08 — the `TEAM-SIGN-OFF`
line is at the bottom of this document ("SIGNED OFF 2026-08-08").**

<!-- HISTORICAL-SIGNOFF-CLAIM -->
*This header read "NO `TEAM-SIGN-OFF` LINE" until 2026-08-10, two days after the
signature was added 200 lines below it. That is the same stale-header defect that
left the clock-alignment cluster sitting unbuilt: a reader who stops at the top of
the file is told the opposite of what the file records. Sign-offs get appended at
the bottom, so the top must be updated in the same commit or it becomes a lie by
omission.*

**The team's original words, verbatim:** *"I think I agree with A and C."* The
sign-off is where that hedge was resolved into a decision; the gates it carries are
listed under "Gates carried, none waived" and none of them were waived by signing.

**BUILD STATE (2026-08-10):** the tombstone repair — required under BOTH options,
and the part that actually stops the quarantines — is **BUILT**. Decision A's
dissolution is still gated, on two things now: binding governance (signed
2026-08-10 at `preferred`, which is not yet the admissible set A needs) and the
UNMEASURED D9 registry coverage in OPEN item 3, which needs a Marder corpus we do
not have. Decision C is complete (demotion + tombstone).

Covers `stimulus_parameter` and `stimulus_parameter_table`. These are the last two
classes that were on the board under "nobody has proposed anything yet."

---

## GROUND TRUTH

```
DENOMINATOR   91 NDI templates on origin/main;  1,002 .m files
RE-DERIVED 2026-08-13: 91 NDI templates on origin/main; 1,003 .m files. The did_v1 ground truth did NOT move -- 0 template diffs across the NDI main merge, still 91; main gained one .m file, so only the denominator shifted. RE-DERIVED AGAIN 2026-08-15: 91 NDI templates on origin/main; 1,005 .m files. NDI main moved to 928b1cd5 and two of its nine commits add test .m files (closeAndRemoveDir.m, TestRayoLabStims.m). The did_v1 ground truth is STILL unmoved -- 91 templates, 0 diffs; only the denominator shifted.
              5 corpora (20211116, B, Dab, JH, Soph), 221,813 v1 documents
              60 migrators_j files, of which touching this family: 0
```

### The two templates

```
stimulus_parameter        ⊂ base, epochid      dep: stimulus_element_id
   ontology_name  ""      a CURIE
   name           ""      the human label
   value          ""

stimulus_parameter_table  ⊂ base, epochid      dep: stimulus_element_id
   string         []      an array of strings -- the entire class
```

### `stimulus_parameter` is real, written, and read live

```
WRITTEN  +setup/+conv/+marder/temptable2stimulusparameters.m:46, :56, :63
         three ndi.document('stimulus_parameter',...) calls -- a production Marder-lab
         conversion turning a temperature table into documents

READ     find_epochids_with_temperature.m:25  query stimulus_parameter.ontology_name (exact_string)
         find_epochids_with_temperature.m:26  query stimulus_parameter.value        (exact_number)
         marder/demo.m:24                     query stimulus_parameter.ontology_name
         marder/demo.m:46                     reads  .stimulus_parameter.value
         marder/postsetup.m:28                isa search
```

The writer produces exactly three shapes, all temperature:

```
{ ontology_name: 'NDIC:<id>', name: 'Command temperature constant', value: <temp> }
{ ontology_name: 'NDIC:<id>', name: 'starting temperature',         value: <temp(1)> }
{ ontology_name: 'NDIC:<id>', name: 'ending temperature',           value: <temp(2)> }
```

### `stimulus_parameter_table` has no code at all

```
mentions in 1,002 .m files: 0      (no writer, no reader, no isa query)
```

Only the template exists.

### Corpus presence: ZERO for both — and that is not absence

Neither appears in any of the five `unconverted` lists, and those lists are COMPLETE,
not truncated: each sums exactly to its stated total (572 / 5164 / 6987 / 11986 /
22198). Source: test-code.yml run #257 / 0458dae, 2026-07-29, quarantine 0 on all five.

**But `stimulus_parameter` has a production writer, and no Marder dataset is among the
five corpora.** This is precisely the corpora-are-a-sample case: absent here is not
absent, and nothing below may be justified by the zero.

### Nothing references either class by id

```
git grep "stimulus_parameter_id|stimulus_parameter_table_id" origin/main   -> EMPTY
templates mentioning either class: only their own two
```

So dissolution carries **no orphan risk**, unlike the calculators (the 11,448-orphan
lesson does not apply here).

---

## WHAT V_ETA HAS TODAY IS WHOLLY INVENTED

```
                          NDI                             V_eta
stimulus_parameter        ontology_name, name, value      parameter_name, parameter_values,
                                                          parameter_units
                          dep stimulus_element_id         dep stimulus_presentation_id (REQUIRED)
                          ⊂ base, epochid                 ⊂ base

stimulus_parameter_table  string[]                        parameter_names, table_data, num_stimuli
                          dep stimulus_element_id         dep stimulus_presentation_id (REQUIRED)
```

Not one field matches. Not one edge matches. Same shape as the `distance_metadata`
wrong-assumed-shape failure that produced ~2,078 quarantines.

**This diagnosis is not new here.** `V_eta_tombstone_audit.md:144-145` reached it
independently and marked both BLOCKING, held for #31. This plan is that held item
coming due.

Two consequences, which are separate problems:

1. **A passthrough would QUARANTINE every document** — the tombstone declares fields no
   real document has, and the validator is strict both ways.
2. **The renames break LIVE NDI queries** at the four sites above. Same class as #58,
   and in scope because they are inside NDI, not a downstream repo.

---

## DECISION A — `stimulus_parameter` DISSOLVES into a typed leaf keyed by its term

The document already *is* a J statement; it was simply never read as one.

```
stimulus_element_id   -> subject_id            (element -> subject)
ontology_name         -> variable.node         the CURIE
name                  -> variable.name         the human label
value                 -> the leaf's value
epochid               -> the time anchor       (per V_eta_epoch_plan.md; epochid is dropped,
                                                the epoch document carries the fact)
```

The **quantity** — and therefore which leaf — comes from the CURIE through the D9
registry, exactly the `measurement` fold used for `subjectmeasurement`. The Marder
documents land as **`temperature_manipulation`**.

### Why manipulation, not observation

A parameter *of a stimulus* is set by the experimenter, not measured off the
preparation. All three real shapes are commanded temperatures — *"Command temperature
constant"*, *"starting temperature"*, *"ending temperature"* — read out of a protocol
table, not off an instrument. The direction is not recorded in v1, so this is a reading
of what the class is for, and it is stated here rather than buried in a migrator.

### Why not B (keep a repaired generic class)

B would leave a class with no statement direction and no `data_type`, hanging off
`base` — the exact state `stimulus_response` was in and that the 2026-08-06 walkthrough
existed to correct. It defers the same work while adding a second such class.

### THE BUILD IS GATED ON #32

Dissolution makes the D9 registry load-bearing for arbitrary NDIC terms, and `binding`
is **not enforced by the validator** (it handles only maxLength / minLength / minimum /
maximum / enum). An unregistered CURIE would have no typed home and would dissolve into
nothing. So this is gated the way #59 is gated on #37: **decision final, build waits.**

---

## DECISION C — `stimulus_parameter_table` PASSES THROUGH, tombstone corrected

Same disposition as `projectvar`: a real did_v1 class, no writer visible in NDI, one
untyped field (`string[]`), and no documents anywhere to model against.

**Why not D (delete):** it fails the writer check. Unlike `dataseries_channel_map`,
which had **no NDI template at all** and was deleted on that ground, this has a shipped
template — it is did_v1 by provenance, and something may have written it before the
current tree. Deleting on the strength of "no emitter in the repo we happen to have" is
the reasoning the corpora-are-a-sample rule forbids.

Proposing a typed model from a template alone is the wrong-assumed-shape failure that
produced the `distance_metadata` quarantines — and, in this very family, the invented
V_eta fields above. **Real documents before any model.**

---

## THE TOMBSTONE REPAIR — required under every option

This is the part that actually stops documents being quarantined, and it is #43's held
rows. Both tombstones must be rewritten to the NDI shape:

```
stimulus_parameter        declare ontology_name, name, value; dep stimulus_element_id
stimulus_parameter_table  declare string; dep stimulus_element_id
```

Independently, the **live NDI queries** on `stimulus_parameter.ontology_name` and
`.value` need updating on the NDI-matlab side once A lands — the same cross-repo rename
problem as the NDIcalc-vis query renames, except in-scope.

---

## OPEN

1. **Units are not recorded.** `value` is a bare number; nothing in the document says
   degrees C. The same gap as the stimulus response family, and it will need the same
   answer (read it from the element, or resolve through the registry).
2. **`value` is typed `""` (char) in the template but written as a number** by
   `temptable2stimulusparameters.m`. Per the ground-truth rule the WRITER wins, so the
   migrator must accept both.
3. **The D9 registry coverage for NDIC terms is unmeasured.** Before the build, count
   how many distinct `ontology_name` values exist in a real Marder corpus and how many
   resolve. That measurement is the gate on A, and it needs a corpus we do not have.

---

## SIGNED OFF 2026-08-08

TEAM-SIGN-OFF [stimulus parameters]: jess@walthamdatascience.com / 2026-08-08 -- A + C: `stimulus_parameter` DISSOLVES into a typed statement leaf keyed by its CURIE (build GATED on #32); `stimulus_parameter_table` PASSES THROUGH and is DEMOTED to deprecated/; both tombstones rewritten to the NDI shape.

### What survives

```
stimulus_parameter        DOES NOT SURVIVE. Its documents become ordinary statements --
                          a Marder "command temperature = 11 C" comes out as a
                          `temperature_manipulation`. No class of this name remains.
stimulus_parameter_table  SURVIVES UNCHANGED, in deprecated/.
```

### The demotion — decided in this review

The team's objection: *"it seems weird to pass a bad V1 doc through."* Right, and it was a
FILING problem rather than a modelling one. `projectvar` — the precedent this plan cites for
exactly this disposition, for exactly these reasons — lives in `deprecated/`, and
`stimulus_parameter_table` sat in `stable/`. So the document did not merely pass through: it
passed through into a class **advertising itself as part of the go-forward model**, with
nothing in the artifact to tell a consumer otherwise. The unmodelled state was visible only in
a CI census line.

Demoted to `deprecated/` in `build_v_eta.py`. 226 schemas, 497 tests green.

### The corpus check — RUN, and it came back empty

```
census run #257 / 0458dae, all FIVE corpora, unconverted_by_class:
   20211116  11 classes    no stimulus_parameter, no stimulus_parameter_table
   B         11 classes    no
   Dab       11 classes    no
   JH         5 classes    no
   Soph      12 classes    no
   (no list was truncated -- the digest caps at 15 and the longest is 12)
```

ZERO documents of either class in the tested corpora. The Marder import DOES write
`stimulus_parameter` (`temptable2stimulusparameters.m:46,56,63`) — no Marder dataset is among
the five. So the writer is live and the sample simply does not contain its output; that is the
corpora-are-a-sample rule working exactly as intended, not evidence of absence.

`stimulus_parameter_table` has **no writer at all**: 0 hits across 915 NDI `.m` files.

### Gates carried, none waived

1. **A is GATED on #32**, hard. Dissolution makes the D9 registry load-bearing for arbitrary
   NDIC terms while `binding` is enforced by nothing, so an unregistered CURIE would have no
   typed home and would dissolve into nothing.
2. **The tombstone repair is required under every option** and is what actually stops the
   quarantines — both classes currently share ZERO field names with their NDI templates.
   These are two of #43's three BLOCKING rows.
3. **The live NDI queries** on `stimulus_parameter.ontology_name` and `.value` need updating
   once A lands. Cross-repo, in scope.
4. **`stimulus_parameter_table` stays unmodelled** until real documents exist. Its one field
   is an untyped `string[]`, and typing it from a template alone is the wrong-assumed-shape
   failure that produced the ~2,078 `distance_metadata` quarantines — and, in this very
   family, the six invented V_eta fields being repaired.
