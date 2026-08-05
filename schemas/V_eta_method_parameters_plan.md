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
   depends_on: software_id -> software    WHICH program these configure
               filter_id   -> frequency_filter    the canonical part, EXTRACTED and typed
   <typed canonical blocks -- see below>
   parameters  structure                  the idiosyncratic remainder

subject_calculation  gains
   depends_on: method_parameters_id -> method_parameters      OPTIONAL
```

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
             value   double
             sign    enum [-1, 1] }                                        optional
   absorbs: threshold_method, threshold_parameter, threshold_sign
        AND vmspikefilteringparameters.threshold "0.030"
   WHY: every spike detector has one, and the method/value/sign decomposition is
   standard. It also UNIFIES two v1 representations that currently disagree -- one
   expresses the threshold in SD multiples, the other as an absolute string -- and
   the `method` field is exactly what disambiguates them.
   VALIDATES TODAY: `sign` as an enum. (`method` as a bound term validates nothing
   until #32.)

waveform_window  { start  duration      -0.00045
                   end    duration       0.001 }                           optional
   absorbs: spike_start_time, spike_end_time
   WHY: the signal window saved per detected spike -- a domain concept, and the same
   {start, end} shape as frequency_filter's passband/stopband.

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
sampling_rate, new_sampling_rate           FLAG: sampling_rate duplicates a fact the
                                           sampled_body already carries; only
                                           new_sampling_rate is configuration
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
