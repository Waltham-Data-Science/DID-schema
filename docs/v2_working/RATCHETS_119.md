# The growth ratchets (#119 part 2)

**Proposed (not decided).** #119 asks for every `BASELINE_*` ratchet to be listed, each placed on one side, with the reason, and for the team to decide on the list before any changes.

The two sides:
- **report:** print the count with its denominator on every run, and never fail on growth.
- **fail:** growth is itself a defect.

**Denominator:** `grep -n "^[A-Z_]*BASELINE[A-Z_]* *= *[0-9]" tools/*.py` finds 10 constants in 3 tools. The values below were measured on did-schema main 1e1eef9, with DID-matlab V2 80a94a0 for the migrator side, on 2026-10-30.

| tool | ratchet | baseline | today | proposed side | why |
|---|---|---|---|---|---|
| check_binding_governance | B1 `BASELINE_UNDECLARED_KEY_USES` | 15 | 0 | fail | A binding key the meta-schema does not declare is a defect. Growth means someone used an undeclared key. |
| check_binding_governance | B3 `BASELINE_VALUE_SET_DISAGREEMENTS` | 1 | 0 | fail | Two definitions of one value set that disagree are a defect. |
| check_binding_governance | B4 `BASELINE_VALUE_SHAPE_MISMATCHES` | 0 | 0 | fail | Already "MUST STAY 0". |
| check_binding_governance | B5 `BASELINE_STRENGTH_DISAGREEMENTS` | 0 | 0 | fail | Already "MUST STAY 0". |
| check_binding_governance | B6 `BASELINE_UNCATALOGUED_BOUND_FIELDS` | 116 | 95 | **report** | This is #119's example. Every binding the team decides (a `source_unit`, a `variable`, a `unit`) adds one, so growth is normal work. |
| check_binding_governance | B8 `BASELINE_UNREGISTERED_PREFIXES` | 5 | 0 | fail | A prefix the CURIE lookup does not register is a defect: the term cannot be resolved. |
| check_binding_governance | B9 `BASELINE_UNENFORCEABLE` | 4 | 1 | fail | A new binding with nothing to check against is a defect of that binding. |
| check_duplicate_field_declarations | `BASELINE` | 3 | 3 | fail | A new redeclaration is refused by [redeclarations only narrow]. The 3 that remain are the V1-ONLY-SLOT `name` rows. |
| check_empty_ontology_nodes | `BASELINE_MIGRATORS` | 16 | 16 | fail | A new term written with an empty node is #119's own example of a defect: "a new uncatalogued term". |
| check_empty_ontology_nodes | `BASELINE_SCHEMAS` | 20 | 20 | fail | Same, on the schema side: an enumerated term with no node. |

## Also for the team

Five ratchets sit above today's count: B1, B3, B6, B8 and B9. Under the existing practice, a ratchet is lowered so it keeps the ground won ("lower it so the ratchet keeps the ground it won"). #119 says not to change any of them before the team decides.

Two options:
- **(a)** lower each "fail" ratchet to today's count, and turn B6 into a report;
- **(b)** something else.

**Proposed:** (a). Only B6 changes behaviour.
