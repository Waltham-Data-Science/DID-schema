# did_query_model.md — Abstract Query Model for DID/NDI

## Purpose

This document specifies the **abstract query model** that the DID/NDI schema
system promises. It is language-agnostic. Concrete implementations live in
consumer repositories — currently `DID-matlab` (`+did/query.m`) and
`NDI-matlab` (`+ndi/query.m`, which extends the DID model) — and may add
language-specific conveniences, but they must implement the operators and
semantics defined here.

This file is the contract that the schema layer relies on when a field
declares `_queryable: true`. It is **not** an implementation guide.

## Relationship to `_queryable`

A field with `_queryable: true` is promised to be addressable by the
operators in this document. A field with `_queryable: false` is not — it
may be retrieved as part of the document body but is not guaranteed to be
indexed for search.

Whether `_queryable` is honoured by a particular backend (and how) is the
database layer's responsibility. This document specifies *what* a query
means; it does not specify *how* it is evaluated.

## Query value model

A query is a tree of **search structures** combined by boolean operators.
A single search structure has four parts:

| Part         | Description |
|--------------|-------------|
| `field`      | Dot-path selector identifying a target inside a document, or `""` for whole-document predicates such as `isa`. |
| `operation`  | One of the operator names below. May be prefixed with `~` to negate (see "Negation"). |
| `param1`     | First operator parameter (string, number, array, or unused). |
| `param2`     | Second operator parameter (used by a few operators; otherwise unused). |

Search structures combine via boolean composition (see "Composition" below).
Implementations expose this either as method calls (`and`, `or`) or as
array/object literals; either is conformant.

## Field selector

`field` is a **dot-path string** that names a location inside a document:

- `"id"` — the top-level `id` field.
- `"datestamp"` — top-level scalar field.
- `"sample_rate.hertz"` — sub-field of a named composite or generic structure.
- `"axes"` — a field whose value is an array (operators below describe what
  can be asked of it).
- `""` — empty selector; only valid with operators that do not need a field
  (currently `isa`).

Dot-paths address one level of nesting per `.`. **Wildcards and array
indices are not part of the field selector.** Reaching into the elements of
an array is done by the operator (`hasanysubfield_contains_string`,
`hasmember`), not by the path.

## Operators (core)

These operators are required of every conformant implementation.

### Scalar predicates

| Operator           | `param1`              | `param2` | Meaning |
|--------------------|-----------------------|----------|---------|
| `exact_string`     | string                | —        | Field value is exactly the string in `param1`. |
| `contains_string`  | string                | —        | Field value contains `param1` as a substring. |
| `regexp`           | regex string          | —        | Field value matches the regular expression in `param1`. |
| `exact_number`     | number or array       | —        | Field value equals `param1` (same size and element values). |
| `lessthan`         | number                | —        | Field value `<` `param1`. |
| `lessthaneq`       | number                | —        | Field value `<=` `param1`. |
| `greaterthan`      | number                | —        | Field value `>` `param1`. |
| `greaterthaneq`    | number                | —        | Field value `>=` `param1`. |
| `hasfield`         | —                     | —        | The field exists in the document. No comparison; presence only. |

### Array predicates

| Operator                          | `param1`     | `param2` | Meaning |
|-----------------------------------|--------------|----------|---------|
| `hasmember`                       | scalar value | —        | Field value is an array and `param1` is one of its elements (membership test on a flat array). |
| `hasanysubfield_contains_string`  | sub-field name | string | Field value is an **array of structures** such that at least one element has a sub-field named `param1` whose value contains the string in `param2`. This is the only built-in any-element quantifier; it is restricted to substring matching on string sub-fields. |

### Document-level predicates

| Operator     | `param1`       | `param2`       | Meaning |
|--------------|----------------|----------------|---------|
| `isa`        | classname      | —              | Document is of class `param1` or has `param1` somewhere in its superclass chain. `field` must be `""`. |
| `depends_on` | dependency name| dependency value | Document has a `_depends_on` entry whose name is `param1` and whose value is `param2`. |

## Negation

An operator name prefixed with `~` evaluates to the boolean negation of the
operator. For example, `~exact_string` matches every document whose field
value is **not** exactly the supplied string.

Negation applies to every operator above **except** the boolean composition
operator `or` (negating a boolean is expressed by combining negated leaves,
not by negating the operator).

## Composition

Queries compose as boolean expressions:

- **AND** — the conjunction of two queries; a document matches iff it
  matches both.
- **OR**  — the disjunction of two queries; a document matches iff it
  matches at least one.
- **NOT** — negation is expressed at the leaf via the `~` operator prefix
  (see above), not as a separate composition node.

Implementations typically expose `and(q1, q2)` and `or(q1, q2)`; the
underlying value is a search-structure array (AND) or a single search
structure whose operator is `or` and whose `param1` is a search-structure
array (OR).

## Conventional queries

- **Match all documents.** `isa` against the universal base class (e.g.,
  `isa base`). The implementation may expose this as `all()`.
- **Match no documents.** `isa` against a name guaranteed not to exist in
  the class hierarchy. The implementation may expose this as `none()`.

## What is **not** expressible

The model is deliberately small. The following queries are out of scope and
schema authors must not assume `_queryable: true` makes them work:

1. **Non-substring quantifiers over arrays of structures.** Only
   `hasanysubfield_contains_string` walks into an array of structures, and
   only with `contains_string` semantics on a string sub-field. There is no
   built-in `hasanysubfield_exact_string`, `hasanysubfield_greaterthan`,
   etc. Workaround: store the queryable value in a shape that
   `contains_string` can answer (controlled-vocabulary strings with no
   substring overlap), or denormalise to a scalar shadow field.

2. **Correlated multi-predicate on the same array element.** Combining two
   `hasanysubfield_contains_string` queries with `and` finds documents
   where *some* element matches the first and *some* element matches the
   second — possibly different elements. Asking "exists an element with
   sub-field A = x **and** sub-field B = y in the same element" is not
   expressible. Workaround: store the correlated pair in a denormalised
   scalar field, or compose the test in consumer code after retrieval.

3. **Nested arrays of structures beyond one level.** A path like
   `multiscales.datasets.path` is a literal property path; it does not
   iterate. `hasanysubfield_contains_string` reaches one level into one
   array. Workaround: flatten the schema (one document per inner element)
   or surface the deeply nested value as a scalar shadow field.

4. **Per-element comparisons on numeric arrays / matrices.** `exact_number`
   tests whole-array equality. There is no built-in "any element of the
   array is greater than X" or "the third element equals Y." Workaround:
   surface the queryable scalar as its own field (e.g., `pixels_x`
   alongside a `shape` matrix).

5. **Cross-document joins inside a single query.** Each query evaluates
   against one document at a time. `depends_on` is the only cross-document
   primitive and it tests a static dependency declaration, not arbitrary
   join predicates. Multi-step queries are composed in consumer code by
   issuing successive queries.

These gaps are not bugs. They are the price of keeping the query model
small, indexable on any reasonable backend, and language-portable. Schema
design should respect them: a field is queryable in a useful sense only if
the natural questions about it map onto the operators above.

## Evolution

Adding an operator to this model is a model-level change. The procedure:

1. Update this document with the operator's signature, semantics, and the
   `_queryable` guarantee it implies.
2. Update consumer implementations (`DID-matlab`, `DID-python`, etc.) to
   support the new operator and the equivalent of the `~` negation prefix.
3. Update `query_use_cases.md` (if affected) to show the new operator in
   the worked examples.

Removing an operator is a breaking change to the model and requires the
same kind of coordinated migration as a SPEC-level MAJOR bump.

Adding a *language-specific convenience* in a particular implementation
(e.g., a new static constructor that desugars to existing operators) is
**not** a model-level change and does not need to be documented here.
