# V_eta — the `frequency_filter` model

*Walked through with the team on the real corpus document. Nothing built yet.*

TEAM-SIGN-OFF: jess, 2026-07-30. Approved the frequency_filter model as written below: a referenced document under base rather than an entity, band edges rather than a single cutoff, typed gain fields rather than a coefficients bag, no sample_rate, and the name frequency_filter.

> **How this line got here, stated plainly.** The standing rule is that Claude
> never writes a sign-off line; the team writes it. On 2026-07-30 the team gave
> explicit verbal instruction to mark this one, so Claude transcribed it. That is
> a real weakening: the guarantee drops from *structurally impossible* to
> *depends on Claude reporting the conversation accurately*, which is precisely
> the kind of thing that does not survive a compaction. Replace this line with
> the team's own wording whenever convenient. Claude must not transcribe another
> without the same explicit instruction, in the same session.

## The evidence — a real document, not a fixture

From the PRED corpus (`PRED/41269628e2d51bf1_40a0cb9f87794ccb.json`), the only real
`filter` block available:

```json
{
  "type": "high",
  "label": "high",
  "algorithm": "chebyshev_1",
  "parameters": {
    "sampleFrequency": 20000,
    "order": 4,
    "filterFrequency": 300,
    "passBandRipple": 0.8,
    "stopbandAttentuation": NaN
  }
}
```

A 4th-order Chebyshev-I high-pass at 300 Hz on a 20 kHz signal — the standard
extracellular spike-band filter. It rides as a superclass block on `pyraview`, and on
nothing else in V_eta.

**This corrected a guess.** The filter was first assumed to be the anti-alias filter for
pyraview's decimation pyramid. It is not — it is the signal conditioning applied to the
recording itself. Only reading a real document showed that, and it changes the disposition:
the filter is not an artefact of how a cache was built, it is **part of what the stored
numbers mean**. 300-Hz-high-passed voltage is a different quantity from raw voltage.

The matching writers confirm the shape (`grep` over NDI `origin/main`):

```
+util/downsampleTimeseries.m:79   [b, a] = cheby1(4, 0.8, LP / (fs/2), 'low');
+app/spikeextractor.m:44          [b,a] = cheby1(order, ..., filter_high/(0.5*sample_rate), 'high');
+test/+daq/sg_flat.m:57           [b,a] = cheby1(4, 0.8, 300/(0.5*30000), 'high');
```

## The model

```
frequency_filter  ⊂ base            a referenced document, NOT an entity

  algorithm             ontology_term   T8: chebyshev_1 | chebyshev_2 | butterworth |
                                            elliptic | bessel | fir
  band                  ontology_term   T8: high_pass | low_pass | band_pass | band_stop
  passband              { low, high }   `frequency`; an absent edge means open
  stopband              { low, high }   band_stop only
  order                 integer
  passband_ripple       `gain`          optional -- Chebyshev I, elliptic
  stopband_attenuation  `gain`          optional -- Chebyshev II, elliptic

referenced by:   <observation>.filter_id → frequency_filter
```

## Why each part, including three reversals

### It is NOT a `data_type`

A `data_type` is a **quantity** — `voltage`, `duration`, `image`, `tuning_curve`. Nothing
"has a filter value"; a filter is a transformation applied to something that does. Minting
one here fails T12: the axis it adds is method detail, not a new quantity.

### It is NOT an `entity` — reversed

Every entity in V_eta is a thing in the world with citable identity:

```
dataset  funding  organization  person  publication  session  software  subject  web_resource
```

The tier exists to carry `global_identifier` (ORCID, ROR, DOI, PMID, RRID). A filter has no
such identifier and never will, so that field would be permanently empty. There is also an
internal-consistency argument: a calculator's `input_parameters` recur just as often and were
*not* promoted to an entity.

**But an entity is not required to be referenced.** `must_refer` is existence-only, and
`time_reference ⊂ base` is already a referenced, deduplicable, non-entity document. Same
shape here — the dedup benefit without the false claim of FAIR citability.

### Band edges, not a single `cutoff` — reversed

One `cutoff` only works for high-pass and low-pass. Band edges cover every case uniformly:

```
high-pass   passband  [300, Nyquist]
low-pass    passband  [0, 300]
band-pass   passband  [300, 3000]
band-stop   stopband  [59, 61]        <- a notch REJECTS a band
```

`band` is still required and is not merely derivable from the numbers, because band-stop is
the inverse of the other three. Named edges beat a positional array: T14 exists to stop a
reader needing to know a convention.

### Typed `gain` fields, not a `coefficients` bag — reversed

Two reasons the first draft was wrong.

**The word is taken.** `[b,a] = cheby1(...)` — `b` and `a` *are* the filter coefficients.
`filter.coefficients` holding `{passband_ripple: 0.8}` would be read as `b`/`a` by anyone
with signal-processing background.

**The shape is wrong.** The tuning model uses a bag because fit forms vary unboundedly. The
IIR family is closed: order + band edges, plus at most ripple and/or attenuation. The tuning
re-audit already established the rule — the empirical scalars stayed typed and queryable
because flattening them into a `{name,value}` bag was a real query regression. "Every
recording high-passed with under 1 dB of ripple" must stay a query.

The `gain` data_type (canonical `decibels`) was added for exactly these two fields.

### NO `sample_rate` — a specification, not a realisation

MATLAB's designers take *normalised* frequency (`300/(0.5*30000)`), so realised coefficients
depend on the sample rate. That forces a choice, and it is created by making this a shared
document:

- **specification** — "4th-order Chebyshev-I high-pass at 300 Hz". Deduplicates across every
  recording that used it; the rate is already on the recording (`sample_time.dt`).
- **realisation** — the actual coefficients. Needs `sample_rate`, and then dedup only works
  within one rate.

**Specification.** It is the reusable thing; the realisation is derived, and storing the rate
here would duplicate a fact the recording already carries.

### Named `frequency_filter`, not `filter`

`filter` is ambiguous in this domain — spatial filters, Kalman filters, median filters,
common-average referencing, and optical excitation/emission filters, which are physical parts
of a microscope. Every field here (`passband`, `stopband`, `order`, `ripple`) is a statement
about frequency response, so the name states the axis that makes the schema apply, and leaves
`spatial_filter` / `optical_filter` free.

*T12 was misapplied in an earlier draft to argue for the shorter name. T12 governs whether a
class EXISTS; T13 governs what it is CALLED. "Do not build for hypotheticals" is a reason not
to create a spatial-filter class today — not a reason to take a name that needs changing when
one appears.*

Rejected: `spectral_filter` (reads as wavelength), `digital_filter` (does not exclude
Kalman), `temporal_filter` (not the standard term), `linear_filter` (names the maths, not the
purpose), `iir_filter` (excludes FIR).

**Known cost:** `frequency_filter` shares a stem with the `frequency` data_type without being
the same kind of thing — one a quantity, the other a method. Judged acceptable, since
`passband`/`stopband` are `frequency`-typed and the relation is real.

## Why this is typed while calculator `input_parameters` stays a bag

The team's distinction, and it is the better justification:

- A calculator's `input_parameters` are the knobs of **one specific program**, chosen by
  whoever wrote it, with no cross-lab vocabulary and no closed set. Uninterpretable without
  that code. A free-form bag is honest.
- A frequency filter is **canonical**: "4th-order Chebyshev-I high-pass at 300 Hz, 0.8 dB
  ripple" is textbook, interpretable by anyone in signal processing with no reference to NDI.
  The parameter set is fixed by mathematics, not by an author.

That is the T8 axis exactly — one has a governable vocabulary and closed parameters, the
other cannot.

## Migration, and three defects in the source

v1 `filter` is a superclass block on `pyraview`. It becomes a separate `frequency_filter`
document plus a `filter_id` edge from the observation the pyraview fold already mints.

1. **`type` and `label` are both `"high"`** in the real document — duplicated. `type` maps to
   `band`; `label` is redundant and should not be carried without a reason.
2. **`stopbandAttentuation` is misspelled** in the NDI template *and* in the data. A migrator
   reading the correct spelling gets nothing, silently — the exact defect class the
   ground-truth track exists to catch.
3. **`NaN` marks inapplicable parameters.** Chebyshev-I has no stopband spec, so NDI writes
   `NaN`. Per the rule already set for time references (NO TIMES ⇒ NO REFERENCE), an
   inapplicable parameter is **absent**, never NaN.

## Open

- Whether `label` carries anything beyond `band` in other corpora — only one real document
  has been read.
- FIR is in the `algorithm` value_set but no FIR document has been seen; taps/window have no
  home yet. Not built speculatively.
- Which observation classes get `filter_id`. Today only `pyraview` carries a filter block,
  but the raw-recording model (`V_eta_recording_observation_plan.md`) is the natural owner.

## 2026-10-22 -- tenet audit

Decided by Jess Haley, 2026-10-22 [filters are methods]: `frequency_filter` is deleted (a V2 invention; 0 occurrences in the NDI ground truth; no tombstone). jFrequencyFilter writes a `method` document (term = the filter design; parameters the band, the passband and stopband edges in Hz, the filter order as a count, ripple and attenuation in dB), and a body's `filter_id` becomes `method_id` (answer "N1a"). NOT BUILT HERE YET, deliberately: DID-matlab's migrators still emit `frequency_filter` and `filter_id` (private/jFrequencyFilter.m, jSpikeExtractionSettings.m, vmspikefilteringparameters.m, pyraview.m, epochfiles_ingested.m, spike_extraction_parameters.m, hartley_calc.m, binaryseries_parameters.m; did2.build.sampledBody) and NDI's ensembleMembership reads `filter_id`, so deleting the class or renaming the edge now would fail their CI. The class and `sampled_body.filter_id` stay until DID-matlab's change lands; the deletion and the rename to `method_id` then land here in one commit.

Decided by Jess Haley, 2026-10-22 [filter terms from Wikidata]: the filter designs and the filter-band values take Wikidata items, the registered `wikidata` prefix (no OBO ontology has signal-filter terms; OBI's band-pass/long-pass/short-pass filters are optical): Butterworth filter wikidata:Q1018162, elliptic filter Q1051541, Bessel filter Q830123, finite impulse response filter Q117785; high-pass Q262754, low-pass Q918242, band-pass Q2718101, band-stop Q386022; each row's definition is written in the registry. Terms with no Wikidata item found (Chebyshev type I and II, passband and stopband edges, filter order, passband ripple, stopband attenuation, filter band) are EMPTY terms (answer "J6a"). Built: did-schema registry rows; empty-ontology #25 e1bdb0c (EMPTY:0000387-0000396). Chebyshev re-checked: Wikidata Chebyshev filter (Q718621) names both types together, so types I and II stay EMPTY with Q718621 as a cross-reference. Build pending: DID-matlab (jFrequencyFilter writes the nodes).

Decided by Jess Haley, 2026-10-22 [passband edges paired]: the passband low and high edges are two EMPTY terms defined as a pair ("passband low edge", "passband high edge"); NCIT:C94895 Filter Cutoff Frequency fits only the upper edge and names the cutoff, not the design edge, so it is a cross-reference on the high-edge term, not its node (answer "J7b"). Built: empty-ontology #25 e1bdb0c (EMPTY:0000390, 0000391), did-schema registry rows. Build pending: DID-matlab (jFrequencyFilter writes the nodes).
