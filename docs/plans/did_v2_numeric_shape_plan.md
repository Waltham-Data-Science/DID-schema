# did_v2 numeric shape plan: one shape for measured numbers

Decided 2026-11-17 (see the decision line at the end). Drafted by Claude in conversation with Jess Haley, 2026-11-17.

## 1. The rule in one line

A statement's `value` holds the same fields as a list item, minus `variable` and `along`.
Value classes keep their canonically named number (volts, grams, ...); list items name it `numeric` and give its `unit`.
Everything the source wrote is `source_<field>`.

## 2. A statement's value (the 30 numeric value classes)

Today (voltage):

    voltage
        value
            volts               canonical number, in volts
            source_value        the number as the source wrote it
            source_unit         the unit the source gave
            approximate         true or false
            tolerance
                minus           in volts
                plus            in volts

Proposed (voltage):

    voltage
        value
            volts               canonical number, in volts (unchanged)
            source_numeric      the number as the source wrote it (was source_value)
            source_unit         the unit the source gave (unchanged)
            approximate         true or false (unchanged)
            tolerance           (unchanged)
                minus           in volts
                plus            in volts

Every numeric value class changes the same way: source_value becomes source_numeric.
Concentration keeps its seven canonical fields (molar, grams_per_liter, grams_per_gram,
liters_per_liter, particles_per_liter, osmolar, optical_density); exactly one is filled.

Each value class file also declares its canonical field and unit, so code can read any
statement's number without a hand-written table:

    canonical
        field               volts
        unit                om:volt

(concentration declares seven field / unit pairs.)

## 3. The other value classes

Every value class's `value` is a block of that class's own fields, as voltage's is
(`voltage.value.volts`). One class is not a block today, and becomes one:

Today:

    logical
        value                   true or false (the value itself)

Proposed:

    logical
        value
            logical             true or false

Unchanged, already blocks of their own fields:

    term
        value
            node
            name
    text
        value
            text
            language
    count
        value
            count
            approximate
            tolerance
    label
        value
            name

## 4. A list item (covariates, conditions, method parameters, compression parameters)

Today:

    item
        variable                what the item states
        along                   dimension indices (covariates only)
        unit                    canonical unit (meaningless for term, text, logical, count)
        source_unit
        approximate
        exactly one of:
            quantity
                value           canonical number(s)
                source_value
            origin              (covariates only, with spacing)
                value
                source_value
            spacing             (covariates only)
                value
                source_value
            count
            term
            text
            logical
            matrix              an array at each position; no source value
            key                 (covariates only)
            index               with key only
        cyclic                  (covariates only)

Proposed:

    item
        variable                what the item states
        along                   dimension indices (covariates only)
        approximate             true or false
        exactly one of:
            numeric             canonical number(s); an array at each position adds dimensions
            origin              where regular positions start (covariates only)
            count               whole numbers, no unit
            term                terms, or labels with no node
            text                free text
            logical             true or false
            key                 positions taken from another document (covariates only)
        with numeric:
            unit                canonical unit
            source_numeric      the number(s) as the source wrote them
            source_unit         the unit the source gave
            tolerance
                minus           in unit
                plus            in unit
        with origin:
            spacing             step between regular positions
            unit                canonical unit
            source_origin
            source_spacing
            source_unit
        with key:
            index               which entry of the keyed document each position takes
        cyclic                  last position wraps to the first (covariates only)

Removed: the quantity wrapper; matrix; origin.value, origin.source_value, spacing.value,
spacing.source_value; unit and source_unit beside forms that have no unit.

## 5. Examples

A recording's per-channel scale (a covariate on its data body)

Today:

    variable                    Unit Conversion Factor
    along                       [1]
    unit                        volt
    source_unit                 microvolt
    quantity
        value                   [1.95e-7, 1.95e-7, ...]
        source_value            [0.195, 0.195, ...]

Proposed:

    variable                    Unit Conversion Factor
    along                       [1]
    numeric                     [1.95e-7, 1.95e-7, ...]
    unit                        volt
    source_numeric              [0.195, 0.195, ...]
    source_unit                 microvolt

The same recording's per-channel offset (unitless, in raw counts)

Proposed:

    variable                    signal offset configuration
    along                       [1]
    numeric                     [32768, 32768, ...]
    source_numeric              [32768, 32768, ...]

An evenly spaced time axis

Today:

    variable                    time
    along                       [0]
    unit                        second
    origin
        value                   0
        source_value            0
    spacing
        value                   3.33e-5
        source_value            3.33e-5

Proposed:

    variable                    time
    along                       [0]
    origin                      0
    spacing                     3.33e-5
    unit                        second
    source_origin               0
    source_spacing              3.33e-5
    source_unit                 second

A body mass on an assertion

Today:

    mass
        value
            grams               25.1
            source_value        25.1
            source_unit         gram

Proposed:

    mass
        value
            grams               25.1
            source_numeric      25.1
            source_unit         gram

## 6. Rules

Removed:
- unit and source_unit absent for a term, text, logical or count item
- the matrix rules

Kept:
- concentration: exactly one canonical field filled

New:
- unit, source_numeric, source_unit and tolerance appear only with numeric
- spacing, source_origin and source_spacing appear only with origin; unit appears with numeric or origin
- numeric has a unit, unless the variable is unitless or the run's report lists a gap

## 7. Where it applies

List fields (11):
- covariates: data, acquisition_epoch (retiring)
- conditions: statement, directed_relation, data_body
- method parameters: interaction, relation, method, migration, clock_alignment_configuration
- compression parameters: data_body

Value classes renaming source_value to source_numeric (30): acceleration, angle, angular_velocity,
area, capacitance, charge, concentration, conductance, current, dose (two places), energy, force,
fraction, frequency, gain, humidity, intensity, irradiance, length, mass, ph, power, pressure,
resistance, score, substance_amount, temperature, time, velocity, voltage, volume.

Value class made a block (1): logical.

model_fit (used by tuning_curve and contrast_sensitivity): coefficients and constraints use the list
item shape.

Not changed: date and the time references keep source_value (the source's original text of a
timestamp, not a number).

Nothing stored changes: every number, unit and source record has one place in the new shape.

## 8. Questions answered by Jess Haley, 2026-11-17 (in conversation)

1. approximate: at the item / value level for every form ("1. A").
2. count: its own whole-number form ("2. A").
3. Unitless numbers: the class says "no unit" ("3. A"); and units are bound: each unit's
   registry row gains canonical_unit and factor; unit must be canonical; source_unit must
   convert to unit ("3. yes").
4. Series: one value block whose canonical field is an array, one source_unit and one
   approximate for the series ("4. A").
5. model_fit ("yes"): coefficients and constraints become ordinary list items (variable, numeric,
   unit, source_numeric, source_unit; unit optional, empty for migrated fits since v1 states none);
   independent_variables and dependent_variable stay {variable, unit}; goodness and sampled_fit unchanged.
6. Measure first: does any corpus document fill two concentration fields at once? (not run)

## 9. Order of work, once decided

1. DID-matlab: the validator and did2.build read both shapes.
2. DID-matlab and NDI-matlab writers write the new shape.
3. did-schema: the class files change; the old shape is removed.
4. Readers drop the old shape; corpora re-run.

## Decision

Decided by Jess Haley, 2026-11-17 [one shape for measured numbers]: ("The proposal is decided", after the conversation that shaped it: "I like the idea of unifying, but this feels like it's adding more nesting when I'd hoped to flatten", "i wonder if for value classes, we should keep the canonically named values?", "does just numeric work?", "yes, redraw the proposal with numeric", "I feel like logical.value.logical makes sense next to voltage.value.volts?", and the answers in section 8) this document is decided as written: value classes keep their canonically named fields (`volts`, `grams`, concentration's seven) and rename `source_value` to `source_numeric`, each class declaring its canonical field and unit; `logical.value` becomes the block `logical.value.logical`; every list item (covariates, conditions, method parameters, compression parameters, and `model_fit` coefficients and constraints) is flat, `numeric` with `unit`, `source_numeric`, `source_unit` and `tolerance`, or `origin` with `spacing`, `unit`, `source_origin`, `source_spacing`, `source_unit`; the `quantity` wrapper and `matrix` are removed; a statement's series is one value block whose canonical field is an array; units are bound (each unit's registry row gains `canonical_unit` and `factor`; `unit` is canonical; `source_unit` converts to it); `approximate` stays at the item and value level; `count` stays its own form; a unitless number is declared by its class. Built: DID-matlab 8c3f2d24 (#468: step 1, the validator and `did2.build` read both shapes). Built (step 2): DID-matlab b331a9ae (#473: the writers write the new shape), NDI-matlab 32d417b0a (#1254: readers read both shapes) and 52938e563 (#1258: the writers write the new shape); NDI-matlab unit suite run 44441090423 (2875 passed, 0 failed), B 44441122723, Dab 44441126630. Built (step 4, readers): DID-matlab c0db25bb (#511: `did2.read.numeric`, `did2.read.canonical` and the round-trip readers refuse the old shape) and NDI-matlab 0b287a75 (#1283: its readers refuse it). Built (did-schema, the old shape removed from the list items): this commit (`quantity` and `matrix` removed from the 10 list-item declarations, covariates, conditions, method parameters and compression parameters; a covariate's `origin` and `spacing` declared as flat numbers; the old `value` removed from model_fit's coefficients and constraints in its 3 declarations, model_fit, tuning_curve and contrast_sensitivity; checked against DID-matlab V2 f1a781b8 and NDI-matlab V2 0877c221). Built (siblings first for that removal): DID-matlab f1a781b8 (#523: its tests hold on a schema with and without the old list shape, old-shape fixtures written by hand) and NDI-matlab 0877c221 (#1298: TestNumericShapeReaders the same; `ndi.setup.conv.haley.densityDocuments` writes model_fit coefficients as `numeric`). Built (siblings first for the value cells): DID-matlab 45bf6655 (#525: `did2.schema.numericShapeFields` recognises a value cell by its `source_numeric` or its class's `canonical` list, not only by a declared numeric `source_value`; `did2.build.valueCell` writes a `logical` series as one `{logical}` block once the block is declared, and refuses the old shapes the schema no longer declares; its tests hold on a schema with and without the old value-cell shape, old-shape fixtures written by hand) and NDI-matlab 4a828675f (#1305: TestNumericShapeReaders the same; merged as ee9d7d05). Built (did-schema, the old shape removed from the value cells): this commit (`source_value` removed from the 32 value cells that declared it as a number, in 31 class files; `logical.value` declared as the block `{logical}`; `date` and the absolute time references keep their text `source_value`; checked against DID-matlab 5e5c34eb and NDI-matlab 149604996, the heads merged as 45bf6655 and ee9d7d05). Built: DID-matlab 45bf6655 (#525), the corpora re-run on V2 with did-schema main 75d52a0 (#380): Test code run 45730463340 (20211116, B, Dab, JH and PRED each "GENERIC MIGRATION (integrity + lossless): DONE") and Soph run 45730467580 (6 shards, each 0 ids lost, 0 still quarantined, 0 orphan edges). Built (NDI writer follow-up): NDI-matlab 4262043b (#1307: the Haley import spec writes `source_numeric`, 44 of 44 value cells). (The unit rows no writer converts are built under [numeric step 3 leftovers] and [om Time is seconds].) (A condition's or parameter's `source_numeric` is now declared, `number_or_text`, under [source numeric is number or text].) Built (did-schema step 3, declared beside the old shape): this commit (`source_numeric` on 32 value cells and 19 nested references; a `canonical` {field, unit} list on 29 value classes, checked by R11; `numeric` and `tolerance` on the 11 list items; model_fit coefficients and constraints with bound units; `canonical_unit` and `factor` on every term registry row, 61 unit rows filled, checked by R16). Tracked in: VH-Lab/DID-matlab#485, VH-Lab/NDI-matlab#1268, Waltham-Data-Science/did-schema#346.

Decided by Jess Haley, 2026-11-17 [numeric shape details]: ("11. Yes", "12. A", "13. A", to Claude's three questions from building step 1, DID-matlab #468) (1) `source_numeric` holds what the source held in the source's own type: a number where v1 stored a number, text where v1 stored text (e.g. a method parameter's "0.030"), so spellings are kept where they exist; the canonical `numeric` is always a number. (2) A relative time reference's `start`, `end` and `duration` (and `clock_tolerance`) are `time` values and rename `source_value` to `source_numeric`; only true timestamps (a date or an absolute time written as text) keep `source_value`. (3) A single number in a list item is written as a plain number, an array keeps its dimensions. Built: DID-matlab 8c3f2d24 (#468, step 1). Built (step 2): DID-matlab b331a9ae (#473). Built (did-schema step 3 class files): 164d5d44 (a relative time reference's `start`, `end` and `duration`, and `clock_tolerance`, are `time` values, which declare `source_numeric`; `date` and the absolute time references keep a text `source_value`), then (1)'s source's own type on the shared condition and method-parameter entry under [source numeric is number or text]. Tracked in: VH-Lab/DID-matlab#485, Waltham-Data-Science/did-schema#346.

Decided by Jess Haley, 2026-11-17 [series readings share a source record]: ("Refuse and report" and "Yes, NaN + gap each", to Claude's two questions from building step 2, DID-matlab #473) (1) a series has one `source_unit` and one `tolerance`; a source series whose readings differ in source unit or tolerance is refused by the writer and reported by the run, never converted or split silently; (2) when only some readings of a series are not finite, they stay NaN in place in the canonical array, so positions stay aligned, and the run's report lists each missing reading as its own indexed gap. Built: DID-matlab b331a9ae (#473: a mixed series is refused, `did2:build:sizeMismatch`; NaN kept in place with an indexed gap per reading), after NDI-matlab 32d417b0a (#1254).

Decided by Jess Haley, 2026-11-19 [no migrated database is kept]: ("No database exists that was already migrated that we care to keep", to Claude's question whether v2 databases migrated before DID-matlab #473 / NDI-matlab #1258 are re-migrated, upgraded on open, or read in the old shape) option (a): no v2 database migrated so far is kept, so readers drop the old numeric shape now (section 9 step 4) and an old database is migrated again from v1. The same holds for a database migrated before DID-matlab #480/#481 that holds v2 `acquisition_epoch` or `daqreader_epochdata_ingested` documents, whose classes are deleted. Built: DID-matlab c0db25bb (#511: `did2.read.numeric`, `did2.read.canonical` refuse the old shape, `did2:read:oldNumericShapeReMigrate`), NDI-matlab 0b287a75 (#1283: `ndi.vintage.splitSeriesRead`, `ndi.v2.covariateValues` refuse it, `ndi:v2:oldNumericShapeReMigrate`). Tracked in: Waltham-Data-Science/did-schema#346, VH-Lab/DID-matlab#485, VH-Lab/NDI-matlab#1268.

Decided by Jess Haley, 2026-11-19 [numeric step 3 leftovers]: ("I agree with both", after Jess: "what is factor?" and Claude's answer that canonical value = source value × factor) (1) `source_numeric` is declared, optional, on the shared condition and method-parameter entry, and filled only when the value is a number (T14, one entry shape); (2) the nine unit rows no writer converts each get themselves as `canonical_unit` with `factor` 1: microgram per millilitre, microlitre per millilitre, pixel, frame, CFU per millilitre, cell density, the UO fraction and `om:RelativeHumidity`; `om:Time` gets second as its canonical unit, with the factor of its stated unit. Built: did-schema (this commit: eight of the nine rows, each its own `canonical_unit` with `factor` 1: NCIT:C64572, NCIT:C69175, om:pixel, EMPTY:0000260 frame, NCIT:C68902, NCIT:C120538 Cell Density, UO:0000191 and om:RelativeHumidity). Built: DID-matlab ded029f4 (#510: a number given for a declared `source_numeric` on the entry is accepted, through the declared type `number_or_text` that [source numeric is number or text] chose; `did2.schema.numericShapeFields` adds its own `source_numeric` only while the schema does not declare the field), then did-schema (the entry's `source_numeric`, type `number_or_text`, on the nine copies of the shared condition and method-parameter entry, this commit). Built: did-schema (`om:Time`'s row: canonical second, factor 1, as [om Time is seconds] decides, this commit). Tracked in: Waltham-Data-Science/did-schema#346.

Decided by Jess Haley, 2026-11-19 [om Time is seconds]: ("For question 10, yes to canonical second", after Claude reported that `om:Time`'s registry row states no unit, so [numeric step 3 leftovers]'s "the factor of its stated unit" had nothing to apply to) `om:Time` gets second (`om:second-Time`) as its canonical unit, with factor 1. Built: did-schema (the row, this commit). Tracked in: Waltham-Data-Science/did-schema#346.

Decided by Jess Haley, 2026-11-19 [source numeric is number or text]: ("A", to Claude's question after explaining that `source_numeric` keeps the value as v1 wrote it, sometimes a number (`0.03`) and sometimes text (`"0.030"`, whose trailing zero is the stated precision), while the schema gives every declared field one type and DID-matlab enforces it) option (a): DID-matlab's builder and validator get one type that admits a number or text, and did-schema then declares `source_numeric` on the shared condition and method-parameter entry with that type; not (b) always text, not (c) left undeclared. Built: DID-matlab ded029f4 (#510, the type `number_or_text` in `+build/private/fillField.m` and `did2.schema.cache`), then did-schema (the declaration: `source_numeric` of type `number_or_text` on the shared condition and method-parameter entry, and `number_or_text` in the meta-schema's field types, this commit). Tracked in: Waltham-Data-Science/did-schema#346.

Decided by Jess Haley, 2026-11-26 [logical value declared like the rest]: ("Yes, it's not special", to Claude's recommendation) `logical.value` stays declared as a list like every other value class (did-schema #380); DID-matlab's validator enforces exactly one `{logical}` block. Nothing to build.
