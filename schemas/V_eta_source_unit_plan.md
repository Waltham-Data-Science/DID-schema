# V_eta: `source_unit` is a term

Written 2026-10-21 at Jess Haley's request ("make source_unit a bound term", after
the Haley import's CFU count, NDI decision #129). Built ahead of signature at her
request. To be signed: the `TEAM-SIGN-OFF [source unit]` line at the end.

## The problem

Every dimensioned value (mass, length, time, concentration, ... -- 63 field
declarations in the built schema) keeps what its source said in two fields:
`source_value` and `source_unit`. `source_unit` was free text ("mm", "h",
"CFU/mL"), while the unit of an axis, key, condition or method parameter entry is
already an `ontology_term` (data_body amendment 1). So a unit was a term in one
place and a string in another, and a unit the canonical fields cannot express
(colony-forming units per millilitre, decision #129) could be written only as
text, with its registered term (NCIT:C68902) in no document.

## The decision (proposed)

1. **`source_unit` is an `ontology_term`** (`{node, name}`) on every dimensioned
   value, bound `{strength: preferred, node_form: curie}` like
   `statement.variable`. Its `name` is the term's label (tenet T19), not the
   source's spelling.
2. **The term is a registered term** (`schemas/V_eta_term_registry.json`), so
   did2.build's TermRegistry check covers it like any other term the import
   writes.
3. **No source unit, no term:** a value with no source unit leaves `source_unit`
   blank (`{node: "", name: ""}`), as it left the string empty.
4. **Migrated data** (when the migrators move to this shape): a v1 unit spelling
   is mapped to a registered term; a spelling no term matches is kept as the
   term's `name` with an empty `node`, and the migration reports it. It is not
   dropped and not guessed.
5. **The canonical fields do not change.** `grams`, `meters`, `particles_per_liter`,
   `od600`, ... still carry the comparable number; `source_unit` is provenance.

## The Haley import's units

The import writes nine source units. Each maps to a term, all from the Ontology
of units of Measure (`om:`, already a registered prefix) except where noted;
every OM identifier was read from `om-2.0.rdf` (github.com/HajoRijgersberg/OM).

| written | term |
|---|---|
| mm | om:millimetre |
| pixel | om:pixel (registered) |
| frame | EMPTY:0000260 frame (registered) |
| h | om:hour (registered) |
| uL | om:microlitre |
| um/s | om:micrometrePerSecond-Time |
| um/s^2 | om:micrometrePerSecond-TimeSquared |
| CFU/mL | NCIT:C68902 Colony Forming Unit per Milliliter (registered) |
| OD600 | NCIT:C73686 Absorbance Unit (amendment 1; signed first as om:one) |

## What it touches

- **did-schema:** `tools/build_v_eta.py` (one pass over every built class turns
  `source_unit` into a bound term, defaults included); the term registry gains the
  unit terms; tests.
- **DID-matlab #218:** the value builders' `SourceUnit` option takes a term; the
  TermRegistry check covers it; tests.
- **NDI #1021:** the Haley import's `SourceUnit` sites write terms; readers that
  show a value's source unit read the term's name; on did-schema `main` (the
  `current` leg) the string stays.
- **Migrators:** unchanged until they are ported to this shape (they are pinned to
  `v_eta-pre73`); item 4 applies then.

To be signed: `source_unit` is a bound ontology_term (the unit's registered term, its label as the name) on every dimensioned value; blank when the source gives no unit; a migrated spelling no term matches keeps its spelling as the name with an empty node and is reported; OD600's unit is om:one

TEAM-SIGN-OFF [source unit]: jess / 2026-10-21 -- `source_unit` is a bound ontology_term (the unit's registered term, its label as the name) on every dimensioned value; blank when the source gives no unit; a migrated spelling no term matches keeps its spelling as the name with an empty node and is reported; OD600's unit is om:one

## Amendment 1 (2026-10-21): OD600's unit is NCIT:C73686 Absorbance Unit

The sign-off above named om:one, OM's dimensionless unit, as the unit of an OD600
reading. An optical density has no dimension but does have a named unit, the
absorbance unit (-log10 of transmitted over incident light), and om:one says only
"no unit". Jess Haley chose NCIT:C73686 "Absorbance Unit" (2026-10-21): NCIT is
already a registered prefix and already names the OD600 method (NCIT:C85776). The
wavelength (600 nm) is said by the variable and method, not the unit. UO:0000269
"absorbance unit" is the same unit; it was not chosen because `uo` is not a
registered prefix. om:one leaves the term registry.

To be signed: amendment 1 -- OD600's unit is NCIT:C73686 Absorbance Unit, not om:one
