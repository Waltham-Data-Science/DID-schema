# V_eta — the spike processing parameters family → one `method_parameters` class

**DECIDED with the team, 2026-08-05. RE-DECIDED and SIGNED 2026-08-09. Build deferred
(#74).** The shape below the "FINAL MODEL" heading supersedes the class described in the
first half of this document; everything above it stands as rationale.

TEAM-SIGN-OFF [spike processing parameters]: jess, 2026-08-09 -- the four settings classes fold into ONE generic `method_parameters` document (id and `base.name` preserved; optional `software_id`, `subject_id`, `epoch_id -> epoch`, and a `derived_from_id` self-edge carrying LINEAGE only); the settings shape is a `parameter[]` entry modelled on the `axis` entry, identity in a bound `variable`, with no `unit` field and no `data_type` field; it keeps the field name `method_parameters` in BOTH mount points, inline on `subject_interaction` and in the document; routing is decided per class -- a name and an id in the source means a document, otherwise inline -- and a statement carries the inline field or the edge, never both.

> **FOURTH TRANSCRIPTION.** Claude wrote this line on explicit instruction ("Sign it"),
> 2026-08-09. The openMINDS record's note, written yesterday, said the third should be the
> last. It was not. Every transcription trades a structural guarantee for Claude's account
> of the conversation, and this document is a live demonstration of why that matters: three
> class names, a field rename and an edge name were proposed and withdrawn inside one
> sitting, and each withdrawal depended on the team reading carefully. Replace this line
> with the team's own wording when convenient.

**The team's words:** on the three options — *"A: one method_parameters with a bag.
B: a parameters leaf per calculation leaf. C: extract canonical concepts to typed
shared slots; bag the genuinely idiosyncratic"* — **"Let's go with C and record it."**

Covers `spike_extraction_parameters`, `spike_extraction_parameters_modification`,
`sorting_parameters`, `vmspikefilteringparameters`.

---

## Ground truth — the four templates

```
spike_extraction_parameters               ⊂ base, app     no deps
   center_range_time 0.0005  overlap 0.5  read_time 30  refractory_time 0.001
   spike_start_time -0.00045  spike_end_time 0.001
   do_filter 1  filter_type "cheby1high"  filter_low 0  filter_high 300
   filter_order 4  filter_ripple 0.8
   threshold_method "standard_deviation"  threshold_parameter -4  threshold_sign -1

spike_extraction_parameters_modification  ⊂ base, app
   deps: extraction_parameters_id, element_id      IDENTICAL payload (a full override)

sorting_parameters                        ⊂ base, app     no deps
   graphical_mode 1  num_pca_features 10  interpolation 3
   min_clusters 3  max_clusters 10  num_start 5

vmspikefilteringparameters                ⊂ base, epochid, app   dep: element_id
   sampling_rate 0  new_sampling_rate 0  threshold "0.030"  refract 0.0025
   spiketimes ""                            <- OUTPUT DATA in a config document
   filter_algorithm "0"  filter_algorithm_parameters [{name, value}]  rm60Hz 1
```

## Reference check — ids and names are load-bearing

```
BY EDGE   extraction_parameters_id -> spike_extraction_parameters_modification,
                                      spikewaves, spike_clusters
          sorting_parameters_id    -> spike_clusters

BY STRING spikesorter.m:373   ndi.query('base.name','exact_string', sorting_parameters_name)
          spikeextractor.m:373,393   isa spike_extraction_parameters / _modification
```

`sorting_parameters.base.name` is matched by `exact_string` — the same name-join as
`daqsystem`. **`base.id` AND `base.name` must both be preserved.**

---

## THE MODEL — four classes collapse to one

```
method_parameters  ⊂ base
   base.name                              "default" -- the key spikesorter.m:373 looks up
   depends_on: software_id -> software        WHICH program these configure
               filter_id  -> frequency_filter the canonical part, EXTRACTED and typed
               subject_id -> subject          OPTIONAL -- scoped to one element-subject
               epoch_id   -> epoch            OPTIONAL -- scoped to one epoch
               derived_from_id -> method_parameters OPTIONAL -- the protocol this is a tweak of
   <typed canonical blocks -- see below>
   parameters  structure                  the idiosyncratic remainder

subject_calculation  gains
   depends_on: method_parameters_id -> method_parameters      OPTIONAL
```

The last three edges were ADDED 2026-08-08 — see "THREE FIXES" below. They are
OPTIONAL and each mirrors an edge v1 actually carries, so they are not the
invented-empty-edge pattern (that is a REQUIRED edge NDI does not have).

```
spike_extraction_parameters       -> method_parameters   id + base.name PRESERVED
sorting_parameters                -> method_parameters   id + base.name PRESERVED
vmspikefilteringparameters        -> method_parameters   (+ spiketimes OUT to a sampled_body)
spike_extraction_parameters_modification
                                  -> a SECOND method_parameters document
                                     (v1 carries the FULL payload, not a diff, so it is
                                      another parameter set -- not an overlay)
```

The v1 edges keep resolving because ids are preserved: `spikewaves
.extraction_parameters_id`, `spike_clusters.sorting_parameters_id`,
`spike_clusters.extraction_parameters_id`.

### The name is `method_parameters`, matching the inline field

`subject_interaction` already carries an inline `method_parameters` structure. The
class is the **same concept at a different cardinality** — inline when the knobs are
one run's, a document when they are named and shared. Naming them differently would
have implied they were different things. Same shape as `strain`: an inline value
plus an optional edge to a document carrying the concept with more structure.

### The edge is on `subject_calculation`, NOT `subject_interaction`

Claude first proposed `subject_interaction`, arguing an observation might cite a
named acquisition config. **The team pushed back and the evidence agrees:** in all of
v1, only app outputs reference a parameters document (`spikewaves`,
`spike_clusters` — both calculations). No observation does. Widening it would be
building for a hypothetical. If a manipulation ever needs it, that is a widening
with evidence at the time.

---

## WHY C, AND WHY NOT B

**B — a parameters leaf per calculation leaf** — was rejected on two grounds:

1. **It is a look-alike family**, which T12 names outright: *"an unexplained
   look-alike family is a T12 violation to revisit."* A class per calculator encodes
   *which program* in the class name — a "how", which the meta-principle rules out.
2. **It breaks extensibility.** A new calculator in `NDIcalc-ephys` would need a
   schema change in THIS repo before it could store its parameters. `data_type`
   composites justify that cost because a new quantity is rare and principled; a
   program's knobs are neither.

**A — everything in a bag** — is what the signed-off `frequency_filter` document
already argued for *open, author-specific* knobs. C keeps that and adds the other
half of the same document's reasoning: the **canonical** parts get typed.

## Storage mode does NOT gate this

Asked whether this needed the wider inline/reference/body conversation first: **no.**
T6's `storage_mode` governs where a value's payload physically lives *without
changing what the value means*, and it applies to a `data_type`'s `value`.
`method_parameters` is not a `data_type`. This question is about **identity** — is
this a thing other things point at — not about storage. It resolves the same way
whatever #45 decides about `sampled_body.axes[]` and the acquisition header.

---

# THE CANONICAL EXTRACTION — PROPOSED, NOT DECIDED

**The answer to "which canonical CLASSES to add" is: none.** Only something with
identity independent of the statement that mentions it earns a class.
`frequency_filter` did — *"4th-order Chebyshev-I high-pass at 300 Hz"* is a
recurring, nameable specification. A threshold of −4 SD is not; it is a number and a
method. **So the canonical concepts here want to be TYPED BLOCKS on
`method_parameters`, not referenced documents.** Zero new classes beyond
`method_parameters` itself.

All the field types needed already exist:

```
DENOMINATOR: 227 schema files
  duration       11 uses      gain            3 uses
  ontology_term  32 uses      voltage         1 use       frequency  6 uses
  (no existing threshold-ish data_type)
```

### Proposed blocks

```
filter_id -> frequency_filter        ALREADY SIGNED OFF, an edge not a block
   absorbs: do_filter, filter_type, filter_low, filter_high, filter_order,
            filter_ripple  |  rm60Hz (a band_stop notch, stopband [59,61] --
            literally the worked example in the frequency_filter plan)  |
            filter_algorithm + filter_algorithm_parameters

threshold  { method  ontology_term    "standard_deviation" | absolute voltage | ...
             value   { value, source_unit, source_value }
             sign    enum [-1, 1] }                                        optional
   absorbs: threshold_method, threshold_parameter, threshold_sign
        AND vmspikefilteringparameters.threshold "0.030"
   WHY: every spike detector has one, and the method/value/sign decomposition is
   standard. It also UNIFIES two v1 representations that currently disagree -- one
   expresses the threshold in SD multiples, the other as an absolute string -- and
   the `method` field is exactly what disambiguates them.
   VALIDATES TODAY: `sign` as an enum. (`method` as a bound term validates nothing
   until #32.)

waveform_window  { start     duration   -0.00045   offset from the detection instant
                   duration  duration    0.00145 } optional
   absorbs: spike_start_time, spike_end_time   (duration = end - start, computed by the
            migrator; `end` is exactly recoverable and is NOT stored)
   WHY start + duration, REVISED 2026-08-08: see "THREE FIXES" below. The original
   {start, end} was justified by analogy to frequency_filter's passband/stopband --
   a false analogy: a passband's low and high are two independent positions on the
   frequency axis, while a waveform window's two numbers are an ANCHOR and an EXTENT.
   The time_reference family made exactly this change and is SIGNED.

refractory_period  duration                                                optional
   absorbs: refractory_time (0.001)  AND  refract (0.0025)
   WHY: two v1 names for one concept. Typing it UNIFIES them, which is the
   losslessness win -- today a query cannot see they are the same thing.
```

### What stays in the bag, deliberately

```
center_range_time, overlap, read_time      this program's chunked-read strategy
graphical_mode                             a GUI flag; arguably not archival at all
num_pca_features, interpolation, num_start  algorithm-specific
min_clusters, max_clusters                 JUDGMENT CALL -- bounding a cluster search
                                           is arguably canonical, but the shape varies
                                           by algorithm (k vs a range vs nonparametric)
sampling_rate, new_sampling_rate           SETTLED 2026-08-08, no longer a flag: #45
                                           makes time an ordinary axis, so the
                                           sampled_body's axis entry owns the rate
                                           outright. Only new_sampling_rate is
                                           configuration; sampling_rate is DROPPED,
                                           not bagged.
```

### What typed blocks actually buy — measured, not assumed

```
validateConstraints handles: maxLength, minLength, minimum, maximum, enum
binding is NOT enforced (#32)
```

So `threshold.sign` as `enum [-1,1]` **validates today**. `threshold.method` as a
bound term validates nothing until #32. A bag validates nothing beyond `isstruct` —
the exact T14 failure that left 26 of 35 composites with no query path.

Queries this makes real: *"which extractions used a −4 SD threshold"*, *"which used
a refractory period under 2 ms"*. Queries it does not: anything about `read_time` —
correctly, since nobody will ask.

---

# WHY THIS IS A DOCUMENT WHILE A CALCULATOR'S `input_parameters` STAYS INLINE

**Recovered from the walkthrough on 2026-08-06 and recorded then; it was argued in
conversation on 2026-08-05 and not written down.** The team asked: *"So it seems
like this an identical problem to the calculation classes. Is that true?"* The
answer — **not identical, and v1 itself draws the line** — is the rule that decides
where any future algorithm configuration goes, so it belongs in the record.

## The measured contrast

```
DENOMINATOR: 91 NDI templates on origin/main

tuningcurve_calc.json  (apps/calculators/)
   "tuningcurve_calc": { "input_parameters": { independent_label, independent_parameter,
                                               best_algorithm "empirical_maximum",
                                               selection[{property,operation,value}] },
                         "log": [], "depends_on": [ stimulus_response_scalar_id ] }
   -> input_parameters is a NESTED FIELD. No base.id of its own, no base.name,
      nothing points at it.

templates carrying an `input_parameters` block          46
edges named input_parameters_id / calc_parameters_id     0     (git grep, *.m + *.json)

spike_extraction_parameters / sorting_parameters
   own document, own base.id, own base.name
   referred to by 3 templates:
      apps/spikeextractor/spike_extraction_parameters_modification.json
      apps/spikeextractor/spikewaves.json
      apps/spikesorter/spike_clusters.json
   AND looked up BY NAME:
      spikeextractor.m:372  ndi.query('base.name','exact_string',extraction_parameters_name,'')
      spikesorter.m:373     ndi.query('base.name','exact_string',sorting_parameters_name,'')
```

## The rule

> **Is this a PROTOCOL — named, shared, reused across many outputs — or ONE RUN'S
> KNOBS, chosen once and incidental to a single calculation?**
>
> Protocol → its own document; `base.id` **and** `base.name` preserved; referenced by edge.
> Run's knobs → the inline `method_parameters` structure on the statement.

**The observable signature of a protocol, for the next ambiguous case: does v1 give
it a `base.name` that something looks up?** That is not cargo-culting v1's shape —
the lab's own practice made the distinction (one got an id, a name, three referring
edges and a by-name query; the other got a nested struct), and losslessness means
preserving a distinction the source actually made.

## This is not drift, by our own definition

Drift is *the same thing stored two ways, varying by dataset.* This is *two
different things, each with one shape, decided once per class, globally.*
`spike_extraction_parameters` is a protocol in every dataset;
`tuningcurve_calc.input_parameters` is run-knobs in every dataset. No dataset can
change the answer.

That is the same correction made to the MADE/FOUND test in
`V_eta_openminds_family_record.md`: MADE/FOUND failed because it was an
**instance-level** test and so resolved differently per dataset. This one is
**class-level**, which is why it holds.

## What it rules out

Folding `spike_extraction_parameters` into a per-run inline `method_parameters`
would not merely duplicate — **it would destroy an identity v1 maintains.** A named,
reusable lab protocol would become N copies of anonymous knobs, and `base.name` —
the field `spikeextractor.m:372` and `spikesorter.m:373` query on — would have
nowhere to live. This is the same failure mode as dissolving a calculator document
(the 11,448-orphan lesson), one level down: destroy the handle, break the consumers.

Complements `V_eta_frequency_filter_model_plan.md`'s *"Why this is typed while
calculator `input_parameters` stays a bag"* — that section decides **typed vs bag**;
this one decides **document vs inline**. Two different axes, same family.

---

## OPEN

1. **The block list above is PROPOSED**, not decided.
2. **Can a calculation carry BOTH the inline `method_parameters` field and the
   `method_parameters_id` edge?** Needs defining — an override, or an error? v1's
   `_modification` carries a full payload rather than a diff, so it is modelled here
   as a second document. Claude leans **forbid both**, revisit if a real overlay case
   appears.
3. **`vmspikefilteringparameters` has NO migrator**, and its tombstone declares
   `filter_type`/`filter_window`, neither of which exists in the template. It is
   built from scratch either way; this decision only says what to build.
4. **`min_clusters`/`max_clusters` and the resampling pair** — judgment calls noted
   above, left in the bag pending a reason to type them.

---

# THREE FIXES + TWO ANSWERS — 2026-08-08 sign-off review

Everything above stands except where this section overrides it.

## FIX 1 — three v1 edges had no home, and would have been dropped

The model declared `software_id` and `filter_id` only. Read from NDI `origin/main`:

```
spike_extraction_parameters                deps: []                                  (a global protocol)
sorting_parameters                         deps: []                                  (a global protocol)
spike_extraction_parameters_modification   deps: [extraction_parameters_id, element_id]
vmspikefilteringparameters                 deps: [element_id]   superclasses: base, epochid, app
```

So `method_parameters` gains three OPTIONAL edges — `subject_id` (from `element_id`,
per D2 the element is promoted to a subject with its id preserved), `epoch_id`, and
`derived_from_id` (from `extraction_parameters_id`). Optional because the two global
protocols legitimately have none.

**The two shapes are both real and both must be expressible.** A protocol has a
`base.name` and no scope; an override has scope and modifies a named protocol. That
is not two classes — it is one class with optional scope, exactly as `strain` is one
class whose `background_strain_#` is optional.

**`derived_from_id`, not `method_parameters_id`.** Same reasoning as
`background_strain_#` on `strain`: a self-edge must say WHICH role the target plays.
The name is the one judgement call here and the team may prefer another.

## FIX 2 — a LIVE three-way NDI query would have broken

`spike_extraction_parameters_modification` is found by epoch AND element AND base
parameter set, all at once:

```
origin/main:+ndi/+app/spikeextractor.m:388-391
   ndi.query('epochid.epochid','exact_string',epoch_string,'') & ...
   ndi.query('','depends_on','element_id',ndi_timeseries_obj.id()) & ...
   ndi.query('','depends_on','extraction_parameters_id',extraction_parameters_doc{1}.id());
```

and it is WRITTEN with an epoch the template does not declare:

```
origin/main:+ndi/+app/spikeextractor.m:309-313
   doc = ndi.document('spike_extraction_parameters_modification', ..., 'epochid.epochid', epoch_string) + ...
         ndi.document('base','base.name',extraction_name);
   doc = doc.set_dependency_value('extraction_parameters_id', extraction_doc.id());
   doc = doc.set_dependency_value('element_id', ndi_timeseries_obj.id());

origin/main:.../spike_extraction_parameters_modification.json     superclasses: base, app   <- NO epochid
```

**Writer and template disagree, so the WRITER wins** — the class is epoch-scoped in
practice. Without `epoch_id` the three-way lookup has nothing to match on. Same shape
as #58, found the same way, and the third instance this week of *the writer adds what
no template declares* (the others: the `openminds_#` pedigree edges, #54).

## FIX 3 — `sampling_rate` is settled, not a judgement call

#45 makes time an ordinary axis, so the `sampled_body` axis entry owns the sample
rate. `sampling_rate` is DROPPED as a duplicate rather than bagged; only
`new_sampling_rate` is configuration. Recorded in the bag list above.

## ANSWER 1 — the window is `start` + `duration`, not `start` + `end`

**The team asked, and the same question was already decided for `time_reference` on
2026-08-08 (SIGNED):** *"anchor and extent are separated (start + duration, NOT start
+ end)"*. The reasons transfer, and one more applies here:

1. **The frequency_filter analogy that justified `{start, end}` was FALSE.** A
   passband's `low` and `high` are two independent positions on the frequency axis.
   A waveform window's two numbers are an ANCHOR (where the saved snippet begins,
   relative to the detection instant) and an EXTENT (how much signal is kept). Those
   are different kinds of fact, and v1's own names say so — `spike_start_time` is
   negative, `spike_end_time` positive, both offsets from the same event.
2. **The extent is the quantity anyone actually uses.** Samples per waveform =
   duration x rate. `end` is arithmetic on the way to it.
3. **One interval shape across V_eta.** Having `time_reference` say `start`+`duration`
   while `method_parameters` says `start`+`end` re-creates in miniature exactly what
   #45 killed: one fact with two spellings, so no query can span them.

`end` is exactly recoverable (`start + duration`) and is NOT stored. Unlike
`time_reference`, there is **no `source_end`**: v1 writes a plain double with no
formatting worth preserving, whereas `source_end` exists there to keep a timestamp
string verbatim.

## ANSWER 2 — units: two of the three have them, and the third is why #32 matters

**Units are carried by the FIELD TYPE, never by a `unit` field.** This is settled
practice, and #45 restated it for axes: *"its dimension and canonical unit come from
the D9 registry -- THERE IS NO `unit` FIELD."*

```
waveform_window.start      duration   { seconds, source_unit, source_value }
waveform_window.duration   duration   { seconds, source_unit, source_value }
refractory_period          duration   { seconds, source_unit, source_value }
```

Canonical seconds plus what the source wrote — so `refractory_time` (0.001) and
`refract` (0.0025) unify into one queryable dimension while each keeps its
provenance. That is the losslessness win the extraction is for.

**`threshold.value` is the exception, and it is the interesting one: it has NO fixed
dimension.** The two v1 representations disagree about what kind of quantity a
threshold even is:

```
spike_extraction_parameters.threshold_parameter   -4        dimensionless (SD multiples)
vmspikefilteringparameters.threshold              "0.030"   volts, written as a STRING
```

So it can be neither `voltage`-typed (the first is not a voltage) nor a bare double
(the second would lose its dimension). It is a generic quantity cell
`{ value, source_unit, source_value }` whose **dimension is determined by
`threshold.method`** — dimensionless for `standard_deviation`, voltage for an
absolute threshold. That is the same mechanism as #45's axis, one level over: there,
the registry keys dimension by `variable`; here, by `method`.

**Consequence: this family is GATED ON #32, not merely improved by it.** Until
`method` resolves to a registry entry carrying a dimension, `threshold.value` is a
number whose meaning is only documented. `source_value` keeps `"0.030"` verbatim
either way, so nothing is lost while we wait — but a cross-dataset threshold query is
wrong until #32 lands. `sign` as `enum [-1, 1]` validates today, unchanged.

## STILL OPEN after this review

1. The block list remains PROPOSED (unchanged).
2. Inline `method_parameters` + the `method_parameters_id` edge together — still
   undefined; Claude still leans forbid both.
3. `vmspikefilteringparameters` still has NO migrator and a tombstone declaring
   fields the template does not have (unchanged; it is built from scratch).
4. The self-edge name was `overrides_id` when this section was written; it is now
   `derived_from_id` — see the section at the end of this document. SETTLED, not open.
5. **NEW: this family is gated on #32** — see ANSWER 2. It was previously listed as
   only improved by it.

---

# FINAL MODEL — 2026-08-09. SUPERSEDES the class shape above.

Everything above stands as RATIONALE. Where it describes the shape of the class, this
section replaces it. Reached in a sign-off walkthrough driven by the team's questions;
three of Claude's proposals were rejected on the way and the rejections were right.

## How we got here, because the path is the argument

The team rejected `method_parameters`, then `analysis_protocol`, then
`calculation_protocol`, on one consistent objection: **a class carrying `threshold` and
`refractory_period` cannot have a general name, and a class carrying them cannot cover
`sorting_parameters`, which has none of them.** Claude then proposed a
`event_detection_protocol` subclass, which is the look-alike family the team had
already rejected wearing a different hat.

The team's next question dissolved it: *"aren't these the same kind of thing that
calculators use? How are we dealing with calculator parameters right now?"*

They are the same kind of thing. Every calculator's settings already go to ONE place:

```
migrators_j/private/jCalculation.m:99    'method_parameters', calcInputParameters(preBody), ...
migrators_j/private/jCalculation.m:112   srcBlk = rmfield(srcBlk, 'input_parameters');
schemas/V_eta/stable/subject_interaction.json
     { "name": "method_parameters", "type": "structure", "fields": [] }    <- nothing declared
```

So the naming failures were a symptom. The typed blocks did not belong on a new class at
all; they belonged in the settings SHAPE that all 47 interaction leaves already carry.

## THE CLASS

```
method_parameters  ⊂ base
   name         char          optional   the protocol name, e.g. "default" -- the string
                                         spikeextractor.m:372 / spikesorter.m:373 query
   method_parameters  parameter[]  REQUIRED  the SAME field name and shape as inline
   other        structure     optional   the undeclared long tail
   depends_on   software_id  -> software            optional
                subject_id   -> subject             optional -- scope
                epoch_id     -> epoch               optional -- scope
                derived_from_id -> method_parameters optional -- the protocol this is a tweak of

subject_interaction gains
   depends_on   method_parameters_id -> method_parameters   optional
```

The class is the existing inline field plus an identity. No domain fields, so the general
name is now truthful: any method's parameters really can live here.

**The edge is on `subject_interaction`, NOT `subject_statement`.** The statement tier
splits two ways and only one has a method at all:

```
subject_statement
  +-- subject_interaction  47 classes   method, method_parameters, time_reference, ...
  |      +-- subject_observation  33   +-- subject_manipulation 12   +-- subject_calculation 2
  +-- subject_assertion    30 classes   timeless; no method, so no parameters
```

## THE SHAPE — one `parameter` entry, used inline AND in the document

Modelled directly on the `axis` entry from the data_body walkthrough, which solves the
same problem: an open-ended set of domain-specific quantities that must not require a
class or a field per domain. Axes answered it by declaring ONE entry whose identity is a
BOUND `variable`, so "time" and "spatial frequency" are DATA, not schema.

```
parameter
   variable   ontology_term   REQUIRED   bound; UNIQUE within the list. Its dimension and
                                         canonical unit come from the registry -- there is
                                         NO unit field and NO data_type field.
   value      { value, source_unit, source_value }   numeric knobs
   term       ontology_term                          categorical knobs
   text       char                                   free strings
```

What that buys, concretely:

```
refractory_time 0.001   and   refract 0.0025      -> both `variable: refractory period`
                                                     one dimension, comparable at last
threshold_parameter -4  -> `variable: standard-deviation threshold`
threshold "0.030"       -> `variable: absolute voltage threshold`
```

**The threshold splits into TWO variables, and that is the point.** An earlier draft in
this document gave `threshold` one slot whose dimension depended on a sibling
`threshold_method` field. That was wrong for the same reason a `unit` field is wrong: the
variable must determine the dimension by itself. A standard-deviation multiple and a
voltage are not the same quantity and must not be numerically comparable.

Queries reach into the list the same way they reach into `axes[]` -- numeric predicates
inside an array of structs compile through `queryable_array_elem.value_num`
(`+did2/+database/compileQuery.m`), the correction already recorded in
`V_eta_data_body_model_plan.md`.

## WHY NO `data_type` FIELD ALONGSIDE `variable` — team question, 2026-08-09

Asked whether a parameter should carry a `data_type` so its unit is unambiguous. **No,
for three reasons, two of them decisions already taken.**

1. **The identical question was asked and answered for axes**, in the same walkthrough
   that produced the entry above: the variable carries dimension and canonical unit via
   the registry, and there is no unit field. Answering it differently here would put two
   spellings of one fact in the schema -- the exact defect the axis entry exists to
   remove (it collapsed THREE encodings of regular-vs-enumerated plus a fourth spelling
   of sample spacing).
2. **`data_type` is a CLASS with 41 direct subclasses**, not a field value. The data_body
   walkthrough already rejected `data_type` as a field name for precisely this reason
   when naming `datum_type`.

   **RE-DERIVED 2026-08-12: `data_type` now has 41 direct subclasses, not 38.** Corrected
   here because the correction did not arrive on its own — `CLAUDE.md` fixed this same
   figure earlier the same day, in its summary of the data_body walkthrough, i.e. in the
   file that QUOTES the fact and in neither of the two that STATE it. This page would
   otherwise have gone on saying 38 indefinitely.

        DENOMINATOR: 247 json file(s) under schemas/V_eta/ read
        RE-DERIVED 2026-08-15: 247 json file(s) under schemas/V_eta/. This read 248 on 2026-08-13, when `acquisition_reader` was minted; the step-2 data_body build then DELETED `zarr` (signed sec.10 -- a V_gamma invention with no v1 source), so the count went +1 then -1 and is back where it started.
        classes declaring `data_type` as a DIRECT superclass: 41

   **The point this item makes is unaffected, and is in fact stronger.** It says `data_type`
   is a CLASS rather than a field value; a class that has gained three more direct
   subclasses since the walkthrough is more thoroughly taken, not less. Nothing about
   `method_parameters` changes. Found by `tools/check_prose_counts.py`, which derives the
   count from the built tree rather than reading prose about it.
3. **A per-entry `data_type` makes `value` polymorphic** -- a voltage cell here, a
   duration cell there, chosen per row. That is openMINDS's polymorphic `specimen.species`
   slot, which V_eta examined and deliberately declined to adopt
   (`V_eta_openminds_family_record.md` Parts 4 and 5).

The cell keeps `source_unit` and `source_value` so the source's own spelling survives
whatever the registry says.

**HONEST LIMIT, stated because both axes and this depend on it:** the registry does NOT
carry dimension or canonical unit today. It has FIVE `subject_statement_bindings`, each
mapping a variable to an ontology and a root node:

```
DENOMINATOR: 5 subject_statement_bindings in binding_registry_meta.json
   species / instrument type / cell type / material type / developmental stage
   each -> { ontology, root_node, subject_defining: true }     NO dimension, NO unit
```

So "the dimension comes from the registry" is a design that requires the registry to be
extended, and that extension is the binding-governance prerequisite. Until it lands,
`source_unit` is the only unit information present, and a cross-program numeric query is
unreliable. Nothing is LOST meanwhile -- every source value is preserved verbatim.

## ROUTING — when settings become a document, decided once per class

```
The source gave the settings their own identity -- a name, an id, and documents
pointing at them  ->  a method_parameters DOCUMENT, id and name preserved.
Otherwise                                             ->  inline on the statement.
```

This is v1's own practice, not our invention. Spike extraction and sorting settings have
a `base.name` two apps query by string and three document types point at. A calculator's
`input_parameters` has no name and nothing has ever referred to it:

```
DENOMINATOR: 91 NDI templates on origin/main
   templates with an input_parameters block                                    2
   templates or code with a dependency named input_parameters_id / calc_parameters_id   0
```

Because the choice is made per class, globally, it is not drift: no dataset can change
the answer.

**FORBID BOTH — team call, 2026-08-09.** A statement carries the inline field or the
edge, never both. One fact, one place; otherwise a reader must know which wins.

## THE FOUR DOCUMENTS

```
spike_extraction_parameters               -> method_parameters   id + name "default" preserved
sorting_parameters                        -> method_parameters   id + name "default" preserved
vmspikefilteringparameters                -> method_parameters   + subject_id, epoch_id
spike_extraction_parameters_modification  -> method_parameters   + subject_id, epoch_id,
                                                                   derived_from_id
spikewaves      -> voltage_observation, method_parameters_id -> the extraction settings
spike_clusters  -> count_observation,   method_parameters_id -> the sorting settings
```

Bound entries where a variable exists (threshold, refractory period, waveform window
start and duration); `other` for the tail (`read_time`, `center_range_time`, `overlap`,
`graphical_mode`, `num_pca_features`, `interpolation`, `min_clusters`, `max_clusters`,
`num_start`, `filter_algorithm`). Filter settings continue to leave via
`filter_id -> frequency_filter`. `sampling_rate` is dropped as a duplicate of the body's
own axis; `spiketimes` leaves as an event-times observation.

## NAMESPACE CHECK — asked for and run, 2026-08-09

A class named `method_parameters` beside a field named `method_parameters` is safe.

```
DENOMINATOR: 223 classes, 429 distinct field names in schemas/V_eta
names already BOTH a class and a field: 19
   amount angle count data data_type date duration epochid formulation gain length
   measurement ph relation temperature term time_reference volume control_stimulus_ids
```

`+did2/+schema/cache.m:560-608` validates top-level keys against `blocksContributed` and
block fields against `fieldsByBlock` -- separate namespaces. `time_reference` is already
both a class and a field inside `syncrule_mapping`.

## CORRECTION — the epoch edge target, caught by the team 2026-08-09

Two blocks in this document said `epoch_id -> acquisition_epoch`. **Wrong.** The epoch
family is SIGNED and it mints `epoch` as an entity while `acquisition_epoch` DISSOLVES:

```
V_eta_epoch_plan.md:735
TEAM-SIGN-OFF [epoch]: ... MINT `epoch` as an entity (one per epoch id, local_identifier
= the v1 epochid string, REQUIRED); acquisition_epoch dissolves and its clocks become
relative_reference documents; epochid is DROPPED in favour of a uniform epoch_id edge ...
```

Both blocks now read `epoch_id -> epoch`. Recorded rather than silently patched, because
writing a dissolved class as an edge target is how a decision gets quietly un-made.

## FIELD NAMING — `method_parameters`, in BOTH mount points

The list keeps the name `method_parameters` wherever it appears; its entry type is
`parameter`.

```
subject_interaction.method_parameters[*].variable      inline
method_parameters.method_parameters[*].variable        the document
```

**CORRECTION, team 2026-08-09.** This section first said the field was renamed to
`parameters` in both places, following `axes`. **That was wrong, and the team caught it.**
`parameters` is a name this project DELIBERATELY VACATED:

```
CLAUDE.md:452
   the D10 statement-conditions field was renamed `parameters` -> `conditions`
   (axis = per-reading array, covariate = length-1); `method_parameters` holds the
   algorithm config (calculator input_parameters), a distinct slot.
```

Reviving it would have put `parameters` two lines from `conditions`, which was renamed
away from `parameters` for exactly that reason. And the crowding is about to get worse,
not better: under the data_body decision a single document carries THREE struct lists,
each keyed by a `variable`, and they must not be confusable.

```
subject_statement.conditions             what the experiment held or varied
subject_statement.axes                   the shape of the value
subject_interaction.method_parameters    how the algorithm was configured
```

The `axes` precedent still holds in the part that matters — ONE name for ONE shape across
both mount points — which `method_parameters` satisfies without touching a reserved word.

The block-and-field stutter `method_parameters.method_parameters` is real and accepted. It
has two precedents: `control_stimulus_ids.control_stimulus_ids` in the built V_eta schema,
and `epochid.epochid`, which is NDI's own. Preferable to reviving a name the team removed,
and to renaming the class a fourth time.

## `derived_from_id` — the self-edge, and a CORRECTION about what it carries

It is v1's `extraction_parameters_id` on `spike_extraction_parameters_modification`.

**The situation it comes from.** A lab defines one shared extraction protocol named
`"default"`. One recording then needs a different threshold — but `"default"` cannot be
edited, because every other extraction in the session already ran under it. So NDI writes
a SECOND document: all fifteen settings again with the threshold changed, recording which
protocol it is a variant of, which element it applies to, and which epoch.

```
origin/main:+ndi/+app/spikeextractor.m:388-391
   the app finds a variant by epoch AND element AND extraction_parameters_id
origin/main:.../spike_extraction_parameters_modification.json
   payload = the identical 15 fields -- a FULL copy, never a diff
```

**CORRECTION, team 2026-08-09.** An earlier version of this section said the edge carries
PRECEDENCE — that the variant "overrides" the base. **It does not.** Precedence comes from
the SCOPE fields: a settings document scoped to one element and one epoch applies there
because of `subject_id` and `epoch_id`, and the app prefers a scoped variant over an
unscoped protocol. The edge is a third filter on that search and a record of origin. It is
LINEAGE, nothing more. The name `overrides_id` described the behaviour the scope produces,
not what the edge holds, and has been dropped.

**The name is `derived_from_id`**, reusing the word the schema already spends on exactly
this relation one tier over:

```
subject_calculation.derived_from_#  -> subject_statement     the data a result came from
subject_observation.derived_from_#  -> subject_statement
method_parameters.derived_from_id   -> method_parameters     the protocol a variant came from
```

Singular and unnumbered, because a variant has exactly one origin in v1. Rejected:
`parent_id` (implies the child inherits, and it does not — the variant is a complete
standalone copy), `overrides_id` and `replaces_id` (both assert precedence the edge does
not carry), and `method_parameters_id` (names the target's class, not its role — the same
reason `strain` says `background_strain_#`).

The one cost, recorded: `derived_from_#` elsewhere means DATA lineage and this means
SETTINGS lineage. Judged a feature — one word, one relation — but a query that assumes
`derived_from` always points at a `subject_statement` must be checked.

