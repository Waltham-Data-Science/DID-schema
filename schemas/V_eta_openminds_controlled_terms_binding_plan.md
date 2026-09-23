# V_eta — binding spec for openMINDS controlled-term entity fields

Status: proposed → implemented in `build_v_eta.py` (this pass). Additive.

## Problem
Three new `dataset` fields carry openMINDS **controlled terms**, not free text:
`accessibility` (openMINDS `ProductAccessibility`), `ethics_assessment`
(`EthicsAssessment`), `experimental_approach` (`ExperimentalApproach`). Last pass
they were typed `char` to keep the round-trip lossless. They should instead resolve
against the openMINDS controlled vocabulary so the value is validated and carries the
openMINDS instance IRI (exact round-trip).

They are a **third binding shape**, distinct from the two the registry already models:
- `subject_statement_bindings` — keyed by **variable** (+ method). For statement
  LEAVES (term_assertion/term_observation) that all share one class; the binding is
  resolved at runtime from the value's sibling `variable`. Entities cannot carry this.
- `relation_bindings` — keyed by **relation term**. For directed/undirected edges.
- **(new) `entity_field_bindings`** — keyed by **(class, field)**. For a directly-named
  controlled-term FIELD on an entity. The field itself names its term set; nothing is
  keyed by a sibling `variable`.

## Design decisions

**D-1. Value type: `ontology_term`, not `char`.**
An openMINDS controlled instance has an IRI + label. Typing the field `ontology_term`
(a `{node, name}` NodeRef — the same shape `variable`/`method`/`relation` and the
enumerated term leaves already use) lets the value carry `node` = openMINDS instance
IRI, `name` = human label. Lossless round-trip AND validatable. `char` would drop the
IRI and validate nothing.

**D-2. Binding is declared INLINE on the field, keyed on the term set — not by variable.**
The field constraint is
```
constraints = {"binding": {"vocabulary": "openMINDS",
                           "term_set": "<ProductAccessibility|EthicsAssessment|ExperimentalApproach>",
                           "strength": "<required|preferred>"}}
```
`vocabulary` names the controlled-vocab namespace (openMINDS controlled terms are a flat
per-set instance library, NOT an ontology subtree — so this is a new key alongside the
existing `ontology`+`root_node` shape, not a reuse of it). `keyed_by` is ABSENT (that
key means "resolve via a sibling field"); here the term set is named directly.

**D-3. Reference the term set by name — do NOT freeze an enumerated copy inline.**
Consistent with the openMINDS philosophy already adopted for whole objects (adopt the
vocabulary, pin drift by crosswalk + version, don't copy the payload). The binding names
the `term_set`; the concrete instance library and its pinned release live once in
`controlled_vocabularies.openMINDS` (registry level) and are stamped by the
import-provenance document. Inlining `values` would create the drift the model rejects.

**D-4. `strength` follows set-closedness.**
- CLOSED sets (`ProductAccessibility` ~4, `EthicsAssessment` ~3): `strength: required`
  — the value MUST resolve to a member.
- OPEN/growing set (`ExperimentalApproach`, dozens and expanding upstream via
  TermSuggestion): `strength: preferred` — resolve when possible; an out-of-set value
  is a warning, not a reject, so a new upstream term doesn't fail ingest before we
  bump the pin.

**D-5. Registry stays the single catalog.** A new `entity_field_bindings` section lists
every (class, field) controlled-term binding, mirroring how `relation_bindings` catalogs
relation terms even though the schema field is free-form. Consumer tooling has one place
to enumerate every controlled vocabulary in the schema.

## Meta-schema (`did_schema_meta.json`) — add to the `binding` constraint properties
`vocabulary` (string), `term_set` (string), `vocabulary_version` (string, optional).
Existing keys (`keyed_by`, `expansion`, `node_kind`, `strength`, `ontology`,
`root_node`, `values`) unchanged.

## Registry (`binding_registry_meta.json`) — two additions
```
"controlled_vocabularies": {
    "openMINDS": {
        "version": null,                 # concrete release pinned by the import-provenance
                                          # doc (single source of truth); round-trip CI asserts it
        "iri_base": "https://openminds.ebrains.eu/instances/",
        "notes": "openMINDS controlled-term instance libraries; each term_set is a flat
                  instance library, not an ontology subtree."
    }
},
"entity_field_bindings": [
    {"class": "dataset", "field": "accessibility",
     "vocabulary": "openMINDS", "term_set": "ProductAccessibility",
     "strength": "required",  "closed": true},
    {"class": "dataset", "field": "ethics_assessment",
     "vocabulary": "openMINDS", "term_set": "EthicsAssessment",
     "strength": "required",  "closed": true},
    {"class": "dataset", "field": "experimental_approach",
     "vocabulary": "openMINDS", "term_set": "ExperimentalApproach",
     "strength": "preferred", "closed": false}
]
```

## Open decision (flagged for review)
- **Version pin location.** Above leaves `controlled_vocabularies.openMINDS.version =
  null`, with the concrete openMINDS release pinned in the (still-deferred)
  import-provenance document — single source of truth. If you'd rather freeze the
  release number directly in the registry, say which openMINDS version and I'll set it.
