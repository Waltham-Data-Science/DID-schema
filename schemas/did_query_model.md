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
- `"axes"` — a field whose value is an array (scalar operators below treat
  the array as an atomic value; `[*]` iteration is described in
  "Array-iteration paths" below).
- `""` — empty selector; only valid with operators that do not need a field
  (currently `isa`).

Dot-paths address one level of nesting per `.`. Array iteration is
expressed with the `[*]` suffix on a segment that names an array (see
below). Numeric indices (e.g., `axes[0]`) are not part of the selector.

## Array-iteration paths

When a path segment names an **array-of-structure** field (i.e., a
`type: "structure"` field whose `_mustBeScalar: false` makes the value an
array of objects), appending `[*]` to that segment iterates over its
elements. Operators applied to a sub-path beyond `[*]` evaluate against
each element in turn, and the search structure matches the document if
**any** element satisfies the operator (existential semantics, analogous
to MongoDB's array dot-paths and to SQL's `EXISTS` over `json_each`).

Examples:

- `"axes[*].name"` — the `name` sub-field of each element of the `axes`
  array.
- `"multiscales[*].datasets[*].path"` — the `path` sub-field of each
  element of each `multiscales` element's `datasets` sub-array. Multiple
  `[*]` segments compose: the document matches if there exists `(i, j)`
  such that `multiscales[i].datasets[j].path` satisfies the operator.
- `"channels[*].window.min"` — `[*]` may be followed by ordinary scalar
  sub-paths; `window.min` is read out of each element.

Any operator from the table below may be used with an `[*]` path. The
existing operator `hasanysubfield_contains_string` is a backward-compatible
shorthand for `<array_field>[*].<sub_field>` + `contains_string`; the
shorthand remains supported for legacy queries.

### Independent vs. correlated array predicates

Two queries combined with `and()`/`or()` are evaluated **independently per
search structure**. Two `[*]` predicates over the same array do not
necessarily refer to the same element. For example, this query —

```
and(
  ndi.query('axes[*].name', 'exact_string', 'z'),
  ndi.query('axes[*].unit', 'exact_string', 'micrometer')
)
```

— matches a document if *some* axis has name `z` **and** *some* axis has
unit `micrometer`, possibly different axes. This is independent
quantifier semantics.

**Correlated predicates** (asking whether the same array element
simultaneously satisfies multiple conditions) are not part of v1 of the
array-iteration extension. Workaround: where the natural query requires
correlated semantics, denormalise to a scalar shadow field (e.g.,
`axis_z_unit`) on the document, or compose the test in consumer code after
retrieval. Correlated quantifiers — analogous to MongoDB's `$elemMatch` or
JSONPath filter expressions — are a candidate for a future model
revision.

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
| `hasanysubfield_contains_string`  | sub-field name | string | Legacy shorthand. Field value is an **array of structures** such that at least one element has a sub-field named `param1` whose value contains the string in `param2`. Equivalent to using `contains_string` with a `[*]` path: `<field>[*].<sub_field>`. The shorthand remains supported. |

Beyond these dedicated operators, **any scalar operator may be used with
an `[*]` path** to express existential quantification over an
array-of-structure field. For example:

- `field = "axes[*].unit"`, `operation = "exact_string"`, `param1 = "micrometer"` — any axis with unit exactly `micrometer`.
- `field = "channels[*].window.min"`, `operation = "lessthan"`, `param1 = 100` — any channel whose window minimum is below 100.
- `field = "multiscales[*].datasets[*].path"`, `operation = "regexp"`, `param1 = "^0/"` — any pyramid level whose path starts with `0/`.

See "Array-iteration paths" above for the full semantics and for the
independent vs. correlated discussion.

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

1. **Correlated multi-predicate on the same array element.** Two queries
   combined with `and()` over `[*]` paths into the same array do not
   necessarily refer to the same element (see "Independent vs. correlated
   array predicates" above). Asking "exists an element with sub-field
   A = x **and** sub-field B = y in the *same* element" is not directly
   expressible in v1. Workaround: store the correlated pair in a
   denormalised scalar field, or compose the test in consumer code after
   retrieval.

2. **Per-element comparisons on numeric arrays / matrices.** `exact_number`
   tests whole-array equality. There is no built-in "any element of the
   matrix is greater than X" or "the third element equals Y." `[*]`
   iteration applies to array-of-structure fields, not to flat numeric
   matrices. Workaround: surface the queryable scalar as its own field
   (e.g., `pixels_x` alongside a `shape` matrix).

3. **Cross-document joins inside a single query.** Each query evaluates
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
