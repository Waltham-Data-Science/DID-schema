# V_eta — the spike processing parameters family → one `method_parameters` class

**DECIDED with the team, 2026-08-05. Build deferred. NO `TEAM-SIGN-OFF` LINE** —
the marker is the team's to write (Operating Rule 4).

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
               epoch_id   -> acquisition_epoch OPTIONAL -- scoped to one epoch
               overrides_id -> method_parameters OPTIONAL -- the set this one overrides
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
`overrides_id` (from `extraction_parameters_id`). Optional because the two global
protocols legitimately have none.

**The two shapes are both real and both must be expressible.** A protocol has a
`base.name` and no scope; an override has scope and modifies a named protocol. That
is not two classes — it is one class with optional scope, exactly as `strain` is one
class whose `background_strain_#` is optional.

**`overrides_id` is a role name, not `method_parameters_id`.** Same reasoning as
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
4. **NEW: the name `overrides_id`.** A judgement call, see FIX 1.
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
   parameters   parameter[]   REQUIRED   the SAME shape as the inline field (below)
   other        structure     optional   the undeclared long tail
   depends_on   software_id  -> software            optional
                subject_id   -> subject             optional -- scope
                epoch_id     -> acquisition_epoch   optional -- scope
                overrides_id -> method_parameters   optional -- the set this one replaces

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
2. **`data_type` is a CLASS with 38 direct subclasses**, not a field value. The data_body
   walkthrough already rejected `data_type` as a field name for precisely this reason
   when naming `datum_type`.
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
                                                                   overrides_id
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

## OPEN after this section

1. **Gated on the registry carrying dimension + canonical unit** (see the honest limit
   above). Shared with the axis entry -- one extension serves both.
2. **Which parameter variables to mint**, and the terms for them. Feeds the
   empty-node harvest.
3. `vmspikefilteringparameters` still has no migrator, and its tombstone declares fields
   the template does not have.
4. Corpus-wide dedup of identical settings documents -- a second pass, best done with the
   `software` entity dedup already queued.
5. The three superseded name proposals are recorded above deliberately; do not re-propose
   `analysis_protocol` or a detection subclass without reading why they failed.
