# V_eta — the stimulus response family → `harmonic_component` + one calculation leaf

**DECIDED with the team 2026-08-06; SIGNED OFF 2026-08-08 — the `TEAM-SIGN-OFF
[stimulus response]` line is at the bottom of this document, and it signs WITH the
three mapping revisions recorded there. Build still deferred.**

<!-- HISTORICAL-SIGNOFF-CLAIM -->
*This header asserted "NO `TEAM-SIGN-OFF` LINE" until 2026-08-10, two days after
the signature was added below it. Corrected; the staleness is now CI-gated.*

**The team's words:** on the revised proposal — *"Okay. I like this. Add it to the
report."*

Covers `stimulus_response`, `stimulus_response_scalar`,
`stimulus_response_scalar_parameters`, `stimulus_response_scalar_parameters_basic`.

---

## GROUND TRUTH

```
DENOMINATOR   91 NDI templates on origin/main;  1,002 .m files
RE-DERIVED 2026-08-13: 91 NDI templates on origin/main; 1,003 .m files. The did_v1 ground truth did NOT move -- 0 template diffs across the NDI main merge, still 91; main gained one .m file, so only the denominator shifted. RE-DERIVED AGAIN 2026-08-15: 91 NDI templates on origin/main; 1,005 .m files. NDI main moved to 928b1cd5 and two of its nine commits add test .m files (closeAndRemoveDir.m, TestRayoLabStims.m). The did_v1 ground truth is STILL unmoved -- 91 templates, 0 diffs; only the denominator shifted.
              5 corpora (20211116, B, Dab, JH, Soph), 221,813 v1 documents
              60 migrators_j files, of which touching this family: 0
              220 V_eta class schemas; 114 with `data_type` as an ancestor
```

### The four templates

```
stimulus_response          ⊂ base            SUPERCLASS ONLY -- never instantiated
   deps: element_id, stimulator_id, stimulus_presentation_id, stimulus_control_id
   stimulator_epochid, element_epochid       two epoch STRING joins

stimulus_response_scalar   ⊂ base, stimulus_response
   dep:  stimulus_response_scalar_parameters_id
   response_type    'mean' | 'F1' | 'F2'
   responses { stimid[], response_real[], response_imaginary[],
               control_response_real[], control_response_imaginary[] }

stimulus_response_scalar_parameters        ⊂ base    ZERO FIELDS -- superclass only
stimulus_response_scalar_parameters_basic  ⊂ base, ..._parameters
   temporalfreqfunc, freq_response, prestimulus_time,
   prestimulus_normalization, isspike, spiketrain_dt
```

### One writer

`+ndi/+app/+stimulus/tuning_response.m`, `compute_stimulus_response_scalar`. The only
`ndi.document(...)` calls in the family are at `:279` (`_parameters_basic`) and `:320`
(`stimulus_response_scalar`) — so `stimulus_response` and
`stimulus_response_scalar_parameters` are never instantiated.

`tuning_response.m:202` sets `freq_response_commands = [0 1 2]`, so **one recording
yields three documents**, one per reduction.

### Corpus presence

```
                                          20211116        B      Dab       JH      Soph      TOTAL
stimulus_response_scalar_parameters_basic       273        0        0        0    11,167     11,440
stimulus_response_scalar                        273        0        0        0     9,851     10,124
stimulus_response / ..._parameters                0        0        0        0         0          0
```

All in `unconverted: document(s) returned unchanged` — no migrator exists, they pass
through whole. Source: test-code.yml run #257 / 0458dae, 2026-07-29, quarantine 0 on
all five.

---

## WHAT V_ETA HAS TODAY, AND WHY IT IS WRONG

`stimulus_response` is a plain concrete class hanging directly off `base` — **outside
the J tier system entirely**: no statement direction, no `data_type`, no subject. It
is a V_zeta carry-over that never had a J walkthrough. That is why this family sat on
the board under "nobody has proposed anything yet."

```
class                                   NDI deps                                V_eta deps
stimulus_response                       element_id, stimulator_id,              stimulus_presentation_id*,
                                        stimulus_presentation_id,               element_id*
                                        stimulus_control_id
stimulus_response_scalar                stimulus_response_scalar_parameters_id  stimulus_response_id
stimulus_response_scalar_parameters     (none)                                  stimulus_response_scalar_id*
                                                                                (* = mustBeNonEmpty)
```

Five defects, each independent:

1. **`stimulator_id` and `stimulus_control_id` are dropped.** Both are set by the
   writer on every document. The control edge is not decoration —
   `control_response_real[]` is meaningless without knowing which stimuli were controls.
2. **The parameters edge is reversed** — V_eta requires the parameters to point at the
   response; NDI writes the response pointing at the parameters, and NDI's own schema
   declares it `"mustbenotempty": 1` (`stimulus_response_scalar_schema.json:5`).
3. **`stimulus_response` declares a `response_file`.** No NDI template in this family
   has a file. Invented.
4. **`freq_response` is modelled as a boolean** — `integer {min:0, max:1}`, documented
   as *"1 if frequency-domain, 0 otherwise"*. It is the harmonic NUMBER, 0/1/2. The
   constraint would reject every F2 document; it does not today only because the
   validator reads `minimum`/`maximum` and this says `min`/`max`
   (`+did2/+schema/cache.m:1043-1048`). Both halves are wrong independently.
5. **`stimulator_id` is a LIVE QUERY**, not merely lost data — see below.

---

## THE #37 PATTERN: TWO MORE CLASSES, NOT THREE

CLAUDE.md records the invented-empty-edge pattern as **three classes, 12,296
documents**. The same census shows two more, both in the stimulus tier:

```
epochfiles_ingested.epochid                                              6,921
syncrule_mapping.epochid                                                 5,316
daqmetadatareader.daqsystem_id                                              59
stimulus_response_scalar_parameters_basic.stimulus_response_scalar_id   11,440   <- NEW
stimulus_presentation.element_id                                         2,670   <- NEW
                                                                        ------
                                                                        26,406
```

`stimulus_presentation`'s NDI dep is named `stimulus_element_id`; V_eta renamed it and
made it required. In every one of the five the empty count **equals** the class's
document count — 100% empty, never partial, which is itself the detector.

**The largest single instance of the pattern is in this family.**

---

## THE TWO EVIDENCE QUESTIONS THE TEAM ASKED

### "Are the ids ever needed?" — yes, by one consumer, and it is not a document reference

Every mention of `stimulus_response_scalar_parameters_id` in the repo:

```
tuning_response.m:74     dependency_value(...)                            the writer
tuning_response.m:289    ndi.query('','depends_on',...,param_doc{1}.id()) the writer, dedup
tuning_response.m:323    set_dependency_value(...)                        the writer
stimulusResponse.m:371   dependency_value(...)                            >>> NOT the writer <<<
stimulus_response_scalar.json:14         the edge
stimulus_response_scalar_schema.json:5   "mustbenotempty": 1
```

`stimulusResponse.m:358-388`:

```matlab
function removeExistingResponses(obj, p, elems)
    % ... along with their scalar-parameter documents so none are left orphaned
    pid = docs{i}.dependency_value('stimulus_response_scalar_parameters_id','ErrorIfNotFound',0);
    pdocs = cat(2, pdocs, obj.session.database_search( ...
        ndi.query('base.id','exact_string', pid, '')));      % base.id STRING MATCH
    obj.session.database_rm(docs);
    obj.session.database_rm(pdocs);
```

The id is load-bearing, via a `base.id` `exact_string` match — the reference class a
`depends_on` sweep misses. **But it is used only for cascade delete.** No other
document points at these ids; the only document-to-document edge is
`stimulus_response_scalar.stimulus_response_scalar_parameters_id`, which the fold
absorbs. And the comment is itself evidence about what these documents *are*: NDI
treats a parameters document whose response is gone as **garbage**. A shared protocol
is never garbage when one consumer disappears.

**Found in the same function** — defect 5:

```matlab
responseQuery(...)  ndi.query('','isa','stimulus_response','') & ...
                    ndi.query('','depends_on','stimulator_id', p.id())
```

A live in-tree query on the edge V_eta drops. Same shape as the `syncrule_mapping`
break; belongs with **#58**, not with this modelling decision.

### "Do the parameters get duplicated?" — by at least 45×, provable from the code

Five of the six fields have fixed in-function defaults (`tuning_response.m:172-176`),
and **the only caller passes exactly one override** (`:133`, `'freq_response'`).
Callers checked: `tutorial_02_04.m:97,98`, `stimulusResponse.m:296`,
`mock/+fun/stimulus_response.m:99` — all route through `stimulus_responses()`, none
passes anything else.

```
temporalfreqfunc            always 'ndi.fun.stimulustemporalfrequency'   (:172)
prestimulus_time            always []                                    (:174)
prestimulus_normalization   always []                                    (:175)
spiketrain_dt               always 0.001                                 (:176)
isspike                     0 or 1, from the element type                (:178-182)
freq_response               0, 1 or 2                                    (:202)

=> AT MOST 6 DISTINCT PARAMETER VALUE-TUPLES, anywhere, ever
```

Against the observed counts, with the per-session dedup scope
(`q_e = ndi.query(E.searchquery())`):

```
              sessions   upper bound (6/session)   observed   duplication
  20211116           1                        6        273         45x
  Soph              33                      198     11,167         56x
```

**Not measured, marked as inference:** the likely mechanism is `q_match{2}`/`q_match{3}`
querying `prestimulus_time`/`prestimulus_normalization` with `'exact_number'` against
`[]` while the template stores `""`. `ndi.query`'s comparison semantics were not read.
The check that would settle it is a field histogram over a corpus.

Separately, the excess above 1:1 in Soph (11,167 params vs 9,851 responses) has a
visible cause: `tuning_response.m:287` does `E.database_rm(rdoc)` on re-run, removing
response documents but **not** their parameters documents. The GUI cleans those up; the
app path does not.

**Conclusion:** 11,440 documents whose entire content is one of **six** value-tuples,
kept alive by a cascade-delete helper that exists to throw them away. By the
protocol-vs-run-knobs rule (`V_eta_method_parameters_plan.md`) these are run knobs.
Folding them inline loses nothing, because two responses sharing a parameters document
are exactly two responses whose inline structures are equal.

---

## THE NAMING PASS — why the first proposal was rejected

Claude first proposed a `stimulus_response` `data_type`. **The team pushed back —
*"isn't that naming extremely vague?"* — and was right.**

A `data_type` names **what the value is** (`voltage`, `duration`, `image`,
`tuning_curve`). `stimulus_response` names **the role a number plays in an
experiment** — a relationship. The image re-audit killed `array` on the same ground:
*a bare N-D numeric grid duplicates `sampled_body` (T6) and names a container (T13).*
This is the same altitude failure with a relationship in place of a container. Second
symptom: the name constrains nothing, so it would accept anything measured near a
stimulus — which is how look-alike families start.

The vagueness was diagnostic. The composite was carrying three passengers that belong
elsewhere:

- the **quantity** (firing rate, voltage) is `variable`, which J already has;
- the **stimulus index** is a `conditions` axis — `subject_statement.conditions` is
  documented for exactly this: *"A condition whose value is a per-reading ARRAY is the
  independent-variable axis"*;
- what genuinely has no home is a **complex coefficient at harmonic *n*** with a paired
  control. `harmonic = 0` is the DC term, which is precisely v1's `'mean'` — so the
  three `response_type`s are one thing at three values, not two different things.

### The reuse sweep

```
DENOMINATOR: 114 classes with `data_type` as an ancestor
Swept every field, recursively, for: complex | imaginary | phase | amplitude | polar | magnitude

MATCHES: 2 of 114
  intensity     value                        "...dF/F, fluorescence, ratios, amplitudes..."  prose only; a real scalar
  tuning_curve  value.individual_responses   "Trial-level responses (real/imaginary preserved where present)."
```

**No existing `data_type` holds a complex value.** The new class is a real gap, not a
missed reuse.

### Why it is NOT a fit-less `tuning_curve`

`stimulus_tuningcurve` is the fit-less `tuning_curve`, so reuse was checked. It fails: a
tuning curve's `independent_values` is a **physical variable** (direction, contrast),
and a response scalar is keyed by **stimulus id** — a reference, not a quantity. The
curve exists precisely because someone mapped id → parameter. Reusing the class would
put ids in a field meant for a variable.

---

## THE MODEL

```
harmonic_component              ⊂ data_type            ABSTRACT composite
   value  structure  {
      harmonic            integer   0 = DC/mean, 1 = F1, 2 = F2   (was freq_response + response_type)
      real                matrix    one coefficient per reading
      imaginary           matrix
      control_real        matrix    the matched control/blank coefficient
      control_imaginary   matrix
   }

harmonic_component_calculation  ⊂ subject_calculation, harmonic_component
   base.id PRESERVED
```

Mirrors `tuning_curve` / `tuning_curve_calculation`. The tier is `subject_calculation`
because this is computed — by a named program, under parameters that change the answer —
not measured; and because **`stimulus_tuningcurve`, the other output of this same file
and app, already folds to a calculation leaf** (`migrators_j.stimulus_tuningcurve`).
Treating two outputs of one app differently would be drift by our own definition.

### Dispositions

```
stimulus_response                          DELETE   superclass only, 0 docs, 0 ndi.document()
                                                    calls; its 4 edges re-home onto the leaf
stimulus_response_scalar                -> harmonic_component_calculation  1->1, id PRESERVED
stimulus_response_scalar_parameters        DELETE   0 fields, 0 docs, abstract
stimulus_response_scalar_parameters_basic  FOLD     -> method_parameters (inline); id dropped
```

### Mapping

```
element_id                  -> subject_id                     (element -> subject)
stimulator_id               -> instrument_id                  T7   -- RECOVERS a dropped edge
stimulus_presentation_id    -> derived_from_1
stimulus_control_id         -> derived_from_2                       -- RECOVERS a dropped edge
element_epochid             -> time_reference_1 anchor
stimulator_epochid          -> DROPPED (see below)
responses.stimid            -> conditions[{variable: stimulus, ...}]   the per-reading axis
responses.response_real/_imaginary          -> value.real / value.imaginary
responses.control_response_real/_imaginary  -> value.control_real / value.control_imaginary
response_type + freq_response               -> value.harmonic
temporalfreqfunc, prestimulus_time,
prestimulus_normalization, isspike,
spiketrain_dt                               -> method_parameters (inline)
```

`method_parameters` needs no new field — it already exists on `subject_interaction`.

The two inbound references keep resolving because the id is preserved:

```
stimulus_tuningcurve.stimulus_response_scalar_id  -> the leaf
tuningcurve_calc.stimulus_response_scalar_id      -> the leaf
```

### Why one epoch anchor, not two

The writer sets `stimulator_epochid` from `stim_doc.document_properties.epochid.epochid`
— a **copy of the referenced presentation's own epoch** — and `stimulus_presentation ⊂
epochid`, so that document carries it after the epoch fold. `element_epochid` comes from
`ts_epoch_timeref.epoch` and is recoverable from nothing.

This is the strain-vs-epoch test (CLAUDE.md) applied unchanged: the epoch string is a
**join key, not content**; the document is the fact; the referent always exists because
the writer always sets `stimulus_presentation_id`. One anchor also sidesteps **#52**,
since there are no sibling indexed edges to role-name.

The conservative alternative — keep both as fields — was considered and not taken.

### Worked example

Before, two documents (values from the writer, `tuning_response.m:296-330`, defaults
`:172-176`):

```json
{ "base": { "id": "412f...a1" },
  "depends_on": [
    { "name": "element_id",                             "value": "9c02...7e" },
    { "name": "stimulator_id",                          "value": "5daa...03" },
    { "name": "stimulus_presentation_id",               "value": "b671...ff" },
    { "name": "stimulus_control_id",                    "value": "20e8...4c" },
    { "name": "stimulus_response_scalar_parameters_id", "value": "77c1...9b" } ],
  "epochid": { "epochid": "t00003" },
  "stimulus_response": { "stimulator_epochid": "t00003", "element_epochid": "t00003" },
  "stimulus_response_scalar": {
     "response_type": "F1",
     "responses": { "stimid": [1,2,3,1,2,3],
                    "response_real":      [ 2.10, 5.44, 1.02, 2.31, 5.61, 0.94],
                    "response_imaginary": [ 0.31,-1.20, 0.08, 0.29,-1.11, 0.05],
                    "control_response_real":      [0.42,0.42,0.42,0.39,0.39,0.39],
                    "control_response_imaginary": [0.01,0.01,0.01,0.02,0.02,0.02] } } }

{ "base": { "id": "77c1...9b" },
  "stimulus_response_scalar_parameters_basic": {
     "temporalfreqfunc": "ndi.fun.stimulustemporalfrequency",
     "freq_response": 1, "prestimulus_time": [], "prestimulus_normalization": [],
     "isspike": 1, "spiketrain_dt": 0.001 } }
```

After, one document, id preserved:

```json
{ "base": { "id": "412f...a1" },
  "document_class": { "class_name": "harmonic_component_calculation" },
  "depends_on": [
    { "name": "subject_id",       "value": "9c02...7e" },
    { "name": "instrument_id",    "value": "5daa...03" },
    { "name": "derived_from_1",   "value": "b671...ff" },
    { "name": "derived_from_2",   "value": "20e8...4c" },
    { "name": "time_reference_1", "value": "<anchor>"  },
    { "name": "software_id",      "value": "<software>" } ],
  "subject_statement":   { "variable": "<see OPEN 1>", "storage_mode": "inline",
                           "conditions": [ { "variable": "stimulus",
                                             "count": { "value": [1,2,3,1,2,3] } } ] },
  "subject_interaction": {
     "method": "ndi.app.stimulus.tuning_response",
     "method_parameters": {
        "temporalfreqfunc": "ndi.fun.stimulustemporalfrequency",
        "prestimulus_time": [], "prestimulus_normalization": [],
        "isspike": 1, "spiketrain_dt": 0.001 } },
  "harmonic_component": { "value": {
     "harmonic": 1,
     "real":              [ 2.10, 5.44, 1.02, 2.31, 5.61, 0.94],
     "imaginary":         [ 0.31,-1.20, 0.08, 0.29,-1.11, 0.05],
     "control_real":      [0.42,0.42,0.42,0.39,0.39,0.39],
     "control_imaginary": [0.01,0.01,0.01,0.02,0.02,0.02] } } }
```

### Arithmetic

```
                              before      after
documents (5 corpora)         21,564     10,124     -11,440
empty required edges          11,440          0     the largest #37 instance, eliminated
V_eta classes                      4          2
```

---

## REPAIRS THIS CARRIES (needed under any model)

```
1  stimulator_id            RESTORED -- and it is a LIVE QUERY, stimulusResponse.m:341.
                            Route with #58, not with this modelling decision.
2  stimulus_control_id      RESTORED -- control_response_* is meaningless without it
3  response_file            DELETED -- invented; no NDI template in this family has a file
4  freq_response            was integer {min:0,max:1} documented as a boolean; it is the
                            harmonic number 0/1/2. {min,max} are INERT -- the validator
                            reads {minimum,maximum} (+did2/+schema/cache.m:1043-1048)
5  the reversed required edge on _parameters_basic disappears with the fold
```

## BUILD

One migrator plus one resolver pass. A single-document migrator cannot inline the
parameters — it cannot follow `stimulus_response_scalar_parameters_id` — but the
mechanism exists: `did2.convert.resolveDeferredBaths` resolves deferred documents
against the migrated batch with no live session. Same shape here.

**Gate before deleting the 11,440 parameter documents:** a corpus verify-before-delete,
as the ensemble fold got. The grep gate is already run — the ids have no archived
referent, only `stimulusResponse.m:371`'s cascade delete.

---

## OPEN

1. **`variable` versus the data_type.** `subject_statement.variable` is required, and
   `conditions` is *"typed by data type via the D9 registry keyed on `variable`."* If
   `variable = firing rate`, the registry keys to a frequency, but the value is a
   *complex harmonic coefficient of* firing rate. Encoding it as `"F1 firing rate"` is
   the exact mistake the tuning plan fixed (method in the name, T11). Claude's lean:
   `variable` names the underlying quantity and `harmonic` qualifies it on the value.
   **This is a D9 / #32 binding-governance question and is NOT decided here.**

2. **Where `variable` comes from at all.** The v1 documents record no units or modality;
   `isspike` only splits spike-derived from continuous. The resolver would need to read
   the migrated `element` document — the same walk `resolveDeferredBaths` does up
   `underlying_element_id`.

3. **`tuning_curve` duplicates these numbers.** `tuning_curve.value` already carries
   `individual_responses` *(real/imaginary preserved)*, `control_response` and
   `response_units`, because `tuning_response.m:458-467` copies them straight out of the
   response document. Both documents must survive (ids referenced), so this is not
   resolved here — but it is a real drift surface: "trial-level responses" has two
   queryable homes. Recorded, not overlooked.

4. **The `harmonic_component` field list is PROPOSED**, not decided — the same status as
   the block list in `V_eta_method_parameters_plan.md`.

---

## THREE REVISIONS 2026-08-08 — the MAPPING section above is superseded on these points

The model is unchanged: four classes to two, `harmonic_component` + its calculation leaf,
id preserved, parameters folded inline. Three mapping lines move.

### 1. `responses.stimid` is an AXIS, not a `conditions` entry

The mapping says:

```
responses.stimid  ->  conditions[{variable: stimulus, ...}]   "the per-reading axis"
```

**`conditions` tightened to cardinality EXACTLY 1 on 2026-08-08 and is explicitly NOT an
axis** (`V_eta_data_body_model_plan.md`, the D10 amendment). The test settled there: *does
element k of this entry say something about element k of the value?* `stimid` positionally
indexes `response_real` and `response_imaginary` — element k names the stimulus that element k
is a response TO. That is an axis by definition.

```
axes[1]
   variable   stimulus              ontology_term
   n          the trial count       CHECKED == length(value.real)
   regular    false
   values     the stimid sequence   (or `labels` if they resolve to terms rather than indices)
```

**This is the clearest casualty of the D10 amendment in the whole set** — a per-reading array
that had been filed as a qualifier because the old sentence said cardinality was the only
difference between a covariate and an axis.

Note the axis carries NO `unit` and NO `datum_type` field: the dimension comes from `variable`
via the D9 registry, and the payload's element type is `subject_statement.datum_type`. For an
index axis like this one that is a virtue — there is no unit slot to leave blank. **It does
mean the registry must distinguish "dimensionless" from "no entry"**, or an index axis and an
unregistered one are indistinguishable. Recorded against #32.

### 2. `element_epochid` anchors a `relative_reference`, not a `time_reference_1`

```
BEFORE  element_epochid -> time_reference_1 anchor
AFTER   element_epochid -> relative_reference
                              relative_to -> epoch
                              clock       -> ontology_term, one of the FOUR NDIC terms (#67)
                              start       -> anchor
                              duration    -> extent, ABSENT means an instant
```

The eight-class time family collapsed to two on 2026-08-08, and `end` became `duration`.
`stimulator_epochid` is still DROPPED — unchanged.

### 3. `derived_from_1` / `derived_from_2` — correct as INSTANCES, but they lose a role

```
stimulus_presentation_id -> derived_from_1
stimulus_control_id      -> derived_from_2
```

This is **not** the `x_1`/`x_2` anti-pattern: `derived_from_#` is a legitimate interchangeable
family, and a DOCUMENT naming its instances `_1` and `_2` is exactly right (the distinction the
`control_designation` fix turned on — a SCHEMA declares the template, a DOCUMENT names the
instances).

But once both are members of one family, **nothing records which antecedent was the CONTROL.**
The presentation and the control are not interchangeable to a consumer even though they are
both provenance. That is #52's question in a second family: a bare index cannot carry a role.

Left OPEN deliberately rather than fixed by inventing an edge name — it should be decided with
#52 and #63 together, since all three are the same question about numbered families.

---

## SIGNED OFF 2026-08-08

TEAM-SIGN-OFF [stimulus response]: jess@walthamdatascience.com / 2026-08-08 -- four classes to TWO: `harmonic_component` (data_type) + `harmonic_component_calculation` (⊂ subject_calculation, id PRESERVED); stimulus_response and stimulus_response_scalar_parameters DELETE (superclass-only, 0 docs); _parameters_basic FOLDS inline to method_parameters. Signed WITH the three mapping revisions above.

### The classes, as signed

```
harmonic_component ⊂ data_type                     ABSTRACT composite
   value { harmonic (0=DC, 1=F1, 2=F2), real, imaginary,
           control_real, control_imaginary }

harmonic_component_calculation ⊂ subject_calculation, harmonic_component
   base.id PRESERVED
   depends_on  subject_id     <- element_id
               instrument_id  <- stimulator_id            RECOVERS a dropped edge (T7)
               derived_from_# <- stimulus_presentation_id + stimulus_control_id
                                                          RECOVERS a dropped edge
               time_reference <- element_epochid, as a relative_reference (revision 2)
   axes[]      variable: stimulus  <- responses.stimid    (revision 1 -- NOT conditions)
```

### Repairs this carries

```
stimulus_response_scalar_parameters.stimulus_response_scalar_id
      INVENTED, REQUIRED, UNTYPED ('') -- inherited by _basic, which is where the
      11,440 empty documents come from. THE LARGEST INSTANCE of the 26,406-document
      invented-empty-edge pattern. NDI has the edge the OTHER WAY.
stimulus_response_scalar.stimulus_response_id
      the real edge (stimulus_response_scalar_parameters_id) DROPPED and a reverse
      one invented, also UNTYPED.
stimulus_response  stimulator_id and stimulus_control_id DROPPED by V_eta; both
      recovered by the fold, as instrument_id and a derived_from_# member.
```

### Gates carried, none waived

1. **#67** for the `clock` term on the epoch anchor.
2. **#63** for `derived_from_#` cardinality.
3. **#52 OPEN in a second family**: with the presentation and the control both members of
   `derived_from_#`, nothing records WHICH was the control. Decide with #52 and #63 together.
4. **#32** must distinguish "dimensionless" from "no entry" in the registry, or an index axis
   like `stimulus` is indistinguishable from an unregistered one.
5. **The parameters fold is safe on volume**: at most 6 distinct parameter tuples against
   11,440 documents, so inlining duplicates almost nothing.


RE-DERIVED 2026-08-21 (ndi_m_files, `check_prose_counts`): 91 NDI templates on origin/main; 1,012 .m files (`git ls-tree -r origin/main | grep -c '\.m$'` = 1012 at 5df51cf9; +7 since the 1,005 reading). The did_v1 ground truth is STILL unmoved -- 91 templates, 0 template diffs; only the denominator shifted.


RE-DERIVED 2026-08-21 (ndi_m_files, sibling drift): NDI `origin/main` advanced to `1c0fe1283` (PR #882, parallel-workers), so `git ls-tree -r origin/main | grep -c '\.m$'` = **1013** (was 1012). The did_v1 ground truth is UNMOVED -- 91 templates, 0 template diffs; only the denominator shifted. Re-derive, do not quote.
