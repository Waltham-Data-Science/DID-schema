# Universal renames: did_v1 → V_delta

> These transformations apply to **every** did_v1 document and to
> **every** schema file as it is migrated to V_delta. Per-class
> conversion markdowns (under `conversions/from_did_v1/<class_name>.md`)
> assume these renames have been applied and document only the
> per-class field-level changes on top.
>
> `_files.md` is a sibling document covering generic file-reference
> handling, which is a separate concern from these renames.

For each rule below the arrow direction is `did_v1 → V_delta`.

## 1. Underscore-prefix structural keys are unprefixed

V_alpha-era schema files (`schemas/V_alpha/*.json`) decorated every
structural key with a leading underscore: `_classname`,
`_class_version`, `_maturity_level`, `_superclasses`, `_depends_on`,
`_file`, `_fields`, and inside each field-spec entry `_name`,
`_blank_value`, `_default_value`, `_mustBeNonEmpty`, `_mustBeScalar`,
`_mustNotHaveNaN`, `_queryable`, `_ontology`, `_documentation`,
`_constraints`. The leading underscore was a sigil to distinguish
DID structural keys from user payload.

V_gamma dropped the sigil from every structural key and V_delta
inherits that convention. The rename is mechanical:

| did_v1 (V_alpha) key | V_delta key |
|---|---|
| `_classname` | `class_name` *(also moved under `document_class`; see §3)* |
| `_class_version` | `class_version` *(also moved under `document_class`; see §3)* |
| `_maturity_level` | `maturity_level` *(also moved under `document_class`; see §3)* |
| `_superclasses` | `superclasses` *(also moved under `document_class`; see §3)* |
| `_depends_on` | `depends_on` |
| `_file` | `file` |
| `_fields` | `fields` |
| `_name` (inside `_fields[i]`) | `name` |
| `_blank_value` | `blank_value` |
| `_default_value` | `default_value` |
| `_mustBeNonEmpty` | `mustBeNonEmpty` |
| `_mustBeScalar` | `mustBeScalar` |
| `_mustNotHaveNaN` | `mustNotHaveNaN` |
| `_queryable` | `queryable` |
| `_ontology` | `ontology` |
| `_documentation` | `documentation` |
| `_constraints` | `constraints` |

`type` was already unprefixed in V_alpha and is unchanged.

In `_depends_on[i]` and `_file[i]` the same rule applies to inner keys
(`_name` → `name`, `_documentation` → `documentation`,
`_must_refer_to_document_class` → `must_refer_to_document_class`,
`_mustBeNonEmpty` → `mustBeNonEmpty`).

## 2. `_classname` is now `document_class.class_name`

Rule §1 strips the underscore prefix; this rule additionally relocates
the class-identity keys into a nested `document_class` block. The full
rewrite is:

```text
did_v1                                V_delta
------                                -------
"_classname":      "x"          →    "document_class": {
"_class_version":  "1.0.0"      →        "class_name":      "x",
"_maturity_level": "..."        →        "class_version":   "1.0.0",
"_superclasses":   [ ... ]      →        "maturity_level":  "stable",
                                          "superclasses":    [ ... ]
                                      }
```

`depends_on`, `file`, and `fields` remain top-level — `document_class`
is for class-identity metadata only. This relocation was introduced in
V_gamma; see `V_gamma_notes.md` § "Class metadata under a top-level
`document_class` header" for the rationale.

For the `maturity_level` value mapping, see §5.

## 3. Snake_case for class names, field names, and filenames

V_alpha allowed camelCase identifiers (e.g., `ontologyImage`,
`SpikeInterfaceSortingOutputs`, `ontologyName`). V_beta and later
require all class names, field names, and filenames to match
`^[a-z][a-z0-9_]*$`. The per-class conversion markdowns list any
identifier renames they trigger. Common cases inherited from V_beta:

| did_v1 identifier | V_delta identifier |
|---|---|
| `ontologyImage` (class) | `ontology_image` |
| `ontologyLabel` (class) | `ontology_label` |
| `ontologyTableRow` (class) | `ontology_table_row` |
| `imageCollection` (class) | `image_collection` |
| `imageStack` (class) | `image_stack` |
| `imageStack_parameters` (class) | `image_stack_parameters` |
| `demoNDI` (class) | `demo_ndi` |
| `demoNDIMock` (class) | `demo_ndi_mock` |
| `SpikeInterfaceSortingOutputs` (class) | `spike_interface_sorting_outputs` |
| `ontologyName` (field) | `ontology_name` |
| `ontologyNodes` (field) | `ontology_nodes` |
| `dataType` (field) | `data_type` |
| `nativeRate` (field) | `native_rate` |
| `nativeStartTime` (field) | `native_start_time` |
| `decimationLevels` (field) | `decimation_levels` |
| `decimationSamplingRates` (field) | `decimation_sampling_rates` |
| `decimationStartTimes` (field) | `decimation_start_times` |
| `variableNames` (field) | `variable_names` |

See `V_beta_notes.md` for the full V_alpha → V_beta rename table.
Filenames track the class name (one schema file per class, named
`<class_name>.json`).

## 4. Superclass references drop the schema-path token

V_alpha entries in `_superclasses` were two-key objects whose second
key was a `$NDISCHEMAPATH`-prefixed path string:

```json
{ "_classname": "base", "_schema": "$NDISCHEMAPATH/base/schema.json" }
```

V_gamma renamed the keys (§1) and dropped the `$NDISCHEMAPATH` prefix
convention while still permitting an explicit `schema` path key.
V_delta removes the `schema` key entirely: a superclass reference in a
**schema file** is `{"class_name": "<x>"}` only. The validator
resolves the superclass by `class_name` through
`schemas/V_delta/index.json`. The meta-schema enforces this via
`additionalProperties: false` on superclass references.

```text
did_v1                                                 V_delta
{ "_classname": "base",                                { "class_name": "base" }
  "_schema":    "$NDISCHEMAPATH/base/schema.json" }
```

In **document instances**, the superclass-reference key set is
different — `class_name` plus `class_version` (a pinned snapshot of
the inheritance chain). That convention was set in V_gamma and is
unchanged in V_delta. See `V_gamma_SPEC.md` § "Schema-reference forms".

## 5. `maturity_level` enum is `{stable, draft, deprecated}`

V_alpha allowed `_maturity_level ∈ {"work_in_progress", "mature"}`.
V_delta replaces the vocabulary with `{stable, draft, deprecated}`
and additionally requires that the value match the tier-folder a
schema file lives in (`schemas/V_delta/<tier>/`).

Migration mapping for did_v1 documents and schemas carried into
V_delta:

| did_v1 `_maturity_level` | V_delta `maturity_level` |
|---|---|
| `"mature"` | `"stable"` |
| `"work_in_progress"` | `"stable"` *(default placement; a separate domain-review pass may re-tier specific schemas to `draft` or `deprecated`)* |

The meta-schema (`did_schema_meta.json`) enforces the V_delta enum.
See `V_delta_SPEC.md` § 3.

## 6. Ontology annotation reshape (4-key → 2-key)

In V_alpha, the field-level `_ontology` slot was a four-key object:

```json
"_ontology": {
    "_namespace": "iao",
    "_term":      "0000219",
    "_name":      "denotes",
    "_uri":       "http://purl.obolibrary.org/obo/IAO_0000219"
}
```

V_gamma collapsed this to a two-key CURIE-based shape:

```json
"ontology": {
    "node": "iao:0000219",
    "name": "denotes"
}
```

V_delta inherits the V_gamma shape. The rewrite rule is:

      node = "<lowercased _namespace>:<_term>"
      name = <_name>

The `_uri` field is dropped; consumers reconstruct the URI through
`CURIE_lookups_meta.json`. `ontology: null` (annotation absent) is
still valid.

The ontology-annotation reshape is a schema-file-syntax change — it
describes the *field*, not the documents validated against the field
— and so does **not** trigger a `class_version` bump. See
`V_gamma_notes.md` § "Annotation-shape change is not a version bump".

## 7. Class-scoped property blocks (document instances)

V_gamma re-established and V_delta inherits the **class-scoped
property block** wire shape for document instances. A document is
structured as:

```text
{
    "document_class": { ... },         ← class-identity header
    "depends_on":     [ ... ],         ← cross-document references
    "<class_name_1>": { ... },         ← one block per class in the
    "<class_name_2>": { ... },           inheritance chain, keyed by
    ...                                  the *declaring* class's name
}
```

Every field declared by class `X` lives inside the document's `"X":
{ ... }` block. Inherited fields are **not** copied into the
subclass's block: they stay in the block of the class that declared
them. A class with zero declared fields still contributes an empty
block `{}`.

V_alpha already used class-scoped blocks (with a separate
`property_listname` knob); V_gamma collapsed that down so the block
key is the `class_name` verbatim. V_delta keeps the V_gamma form.

Migration consequences:

- Every did_v1 document is reshaped so its top-level keys are exactly
  `document_class`, `depends_on`, and one block per class in
  `{concrete class} ∪ {transitive superclasses}` (e.g., for a
  `probe_location` document: `base` and `probe_location`).
- The `base`-class fields (`id`, `session_id`, `name`, `datestamp`)
  live under the `base` block: paths `base.id`, `base.session_id`,
  `base.name`, `base.datestamp`. Any did_v1 document that carried
  these at the document's top level is rewritten into the `base`
  block; documents that already carried them under `base` are
  unchanged.
- The `property_listname` knob from V_alpha is removed; the block
  key must equal the declaring class's `class_name` exactly.

See `V_gamma_SPEC.md` § "JSON Format: Document Instances" for the
authoritative description.

## 8. `class_version` semantics under V_delta sandbox

V_delta is a sandbox set version (like V_gamma was); `class_version`
bumps are deferred until the V1 freeze. Schemas in
`schemas/V_delta/stable/` whose document shape differs from did_v1
nonetheless declare `class_version: "1.0.0"`. The
non-triviality of the migration for those classes is captured in this
directory (one markdown per class) rather than in a version flag.

This rule is purely V_delta-side bookkeeping; it imposes no
transformation on the did_v1 document being migrated.

## 9. `depends_on(k).id` → `depends_on(k).document_id`

Every did_v1 document carries cross-document references as an array of
two-key (sometimes three-key) entries:

```json
"_depends_on": [
    { "_name": "probe_id", "_id": "aabb...", "_version": "..." },
    ...
]
```

After rule §1 strips the underscore prefix the keys are `name`, `id`,
and optionally `version`. V_delta renames `id` → `document_id` and
drops `version` entirely. The result on every V_delta document
instance is:

```json
"depends_on": [
    { "name": "probe_id", "document_id": "aabb..." },
    ...
]
```

The rename motivation: `id` collided with the top-level
`base.id` field for the documents themselves; the earlier V_delta
draft used `value`, which avoided the collision but was uninformative
("a value of what?"). `document_id` says exactly what the field is —
a `did_uid` referring to another document — and the explicit
`document_` prefix disambiguates from any future id-shaped fields the
schema may add.

`version` is dropped because V_delta does not support per-document
version branches; cross-document references resolve to whichever
version of the target document is current in the database.

| did_v1 entry key | V_delta entry key |
|---|---|
| `id` | `document_id` |
| `version` | _(dropped)_ |
| `name` | `name` *(unchanged)* |

The universal-rename pass in `did2.convert.universalRenames`
(`renameDependsOnEntries`) implements this rule. It also tolerates
the earlier V_delta-draft key `value` as a synonym for `id` so
already-migrated corpora convert forward to `document_id` on next
read.

## 10. Planned: `schema_version` on every document

V_delta plans to add a required `schema_version` field on `base` (and
therefore on every inheriting document). Established values:

- `"V_delta"` — documents authored against V_delta
- `"did_v1"` — legacy documents still carrying the did_v1 shape, or
  documents in a holding state during migration

The migrator sets `base.schema_version = "V_delta"` on every output
document once the field exists. Whether the field is present in this
PR's `base.json` is tracked under "open follow-ups" in
`V_delta_notes.md`; conversion logic that relies on its existence
should branch on schema-introspection, not on a hard-coded
expectation.

## Cross-references

- File-reference handling (generic): [`_files.md`](_files.md)
- Conversion index: [`_index.md`](_index.md)
- Conversion template: [`_TEMPLATE.md`](_TEMPLATE.md)
- V_delta differences from V_gamma: [`V_delta_SPEC.md`](../../V_delta_SPEC.md)
- V_alpha → V_gamma rename history: `V_beta_notes.md`, `V_gamma_notes.md`
