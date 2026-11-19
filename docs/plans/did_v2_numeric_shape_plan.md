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

Decided by Jess Haley, 2026-11-17 [one shape for measured numbers]: ("The proposal is decided", after the conversation that shaped it: "I like the idea of unifying, but this feels like it's adding more nesting when I'd hoped to flatten", "i wonder if for value classes, we should keep the canonically named values?", "does just numeric work?", "yes, redraw the proposal with numeric", "I feel like logical.value.logical makes sense next to voltage.value.volts?", and the answers in section 8) this document is decided as written: value classes keep their canonically named fields (`volts`, `grams`, concentration's seven) and rename `source_value` to `source_numeric`, each class declaring its canonical field and unit; `logical.value` becomes the block `logical.value.logical`; every list item (covariates, conditions, method parameters, compression parameters, and `model_fit` coefficients and constraints) is flat, `numeric` with `unit`, `source_numeric`, `source_unit` and `tolerance`, or `origin` with `spacing`, `unit`, `source_origin`, `source_spacing`, `source_unit`; the `quantity` wrapper and `matrix` are removed; a statement's series is one value block whose canonical field is an array; units are bound (each unit's registry row gains `canonical_unit` and `factor`; `unit` is canonical; `source_unit` converts to it); `approximate` stays at the item and value level; `count` stays its own form; a unitless number is declared by its class. Built: DID-matlab 8c3f2d24 (#468: step 1, the validator and `did2.build` read both shapes). Built (step 2): DID-matlab b331a9ae (#473: the writers write the new shape), NDI-matlab 32d417b0a (#1254: readers read both shapes) and 52938e563 (#1258: the writers write the new shape); NDI-matlab unit suite run 44441090423 (2875 passed, 0 failed), B 44441122723, Dab 44441126630. Build pending: DID-matlab and NDI-matlab (readers drop the old shape after step 3), did-schema (the class files, the registry's `canonical_unit` and `factor` columns, then the old shape removed; corpora re-run), in the order of section 9. Tracked in: VH-Lab/DID-matlab#485, VH-Lab/NDI-matlab#1268, Waltham-Data-Science/did-schema#346.

Decided by Jess Haley, 2026-11-17 [numeric shape details]: ("11. Yes", "12. A", "13. A", to Claude's three questions from building step 1, DID-matlab #468) (1) `source_numeric` holds what the source held in the source's own type: a number where v1 stored a number, text where v1 stored text (e.g. a method parameter's "0.030"), so spellings are kept where they exist; the canonical `numeric` is always a number. (2) A relative time reference's `start`, `end` and `duration` (and `clock_tolerance`) are `time` values and rename `source_value` to `source_numeric`; only true timestamps (a date or an absolute time written as text) keep `source_value`. (3) A single number in a list item is written as a plain number, an array keeps its dimensions. Built: DID-matlab 8c3f2d24 (#468, step 1). Built (step 2): DID-matlab b331a9ae (#473). Build pending: did-schema (step 3 class files). Tracked in: VH-Lab/DID-matlab#485, Waltham-Data-Science/did-schema#346.

Decided by Jess Haley, 2026-11-17 [series readings share a source record]: ("Refuse and report" and "Yes, NaN + gap each", to Claude's two questions from building step 2, DID-matlab #473) (1) a series has one `source_unit` and one `tolerance`; a source series whose readings differ in source unit or tolerance is refused by the writer and reported by the run, never converted or split silently; (2) when only some readings of a series are not finite, they stay NaN in place in the canonical array, so positions stay aligned, and the run's report lists each missing reading as its own indexed gap. Built: DID-matlab b331a9ae (#473: a mixed series is refused, `did2:build:sizeMismatch`; NaN kept in place with an indexed gap per reading), after NDI-matlab 32d417b0a (#1254).
