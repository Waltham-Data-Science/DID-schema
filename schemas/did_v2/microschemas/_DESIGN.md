# Microschemas — Design (V_delta)

> **Status:** design proposal, not implemented. This document describes
> the intended shape of the microschema mechanism for V_delta. No
> meta-schema changes, no validator changes, and no actual microschemas
> have been added in this commit. The design is reviewable on its own;
> implementation will land in follow-up PRs.

## Purpose

V_delta has document classes that act as **registries for open-ended
variants** — most prominently `treatment` and `measurement`. Each variant
(a drug dose, a virus injection, a behavioral protocol, etc.) has its
own structured parameters, but the variants share a common identity
("this is a treatment"). Modeling every variant as its own document
class creates class explosion and pushes new variant authors through a
heavy schema-change workflow for what should be a small, frequent
operation.

Microschemas are the V_delta mechanism for this. A microschema is a
named, versioned schema fragment that describes the shape of a specific
field's body on a host document class, selected at validation time by
the value of a *discriminator field* on the document instance.

## Non-goals

- **Microschemas are not document classes.** They cannot be instantiated
  on their own, do not have a `document_class` header, do not
  participate in superclass inheritance, and cannot appear in
  `index.json`'s `schemas` section.
- **Microschemas are not a replacement for inheritance.** Calculator
  variants where each kind is distinct code should remain class-per-kind
  with their own schemas. Microschemas are for cases where variants
  share identity but vary in body shape.
- **Microschemas are not URL-resolvable.** All microschemas in V_delta
  resolve from local paths (central registry + optional local overlay).
  Network-fetched schemas are out of scope.

## File layout

```
schemas/V_delta/
├── stable/                       ← document classes
├── draft/
├── deprecated/
├── examples/
├── conversions/
├── microschemas/
│   ├── _DESIGN.md                ← this file
│   ├── treatment/                ← namespace per host class
│   │   ├── stable/
│   │   │   ├── drug.json
│   │   │   ├── virus_injection.json
│   │   │   └── stimulus_bath.json
│   │   ├── draft/
│   │   │   └── optogenetic_silencing.json
│   │   └── deprecated/
│   └── measurement/
│       ├── stable/
│       │   └── ...
│       └── draft/
└── index.json
```

**Conventions:**

- One directory per host class, named by the host class's `class_name`.
- Inside each host directory, the same `stable / draft / deprecated`
  tier folders used elsewhere in V_delta.
- Filename stem equals the *discriminator value* (`drug.json` registers
  the microschema for `treatment_kind: "drug"`).
- Reserved tier-folder names (`stable`, `draft`, `deprecated`) may not
  be used as discriminator values.
- A discriminator value may live in at most one tier folder for a given
  host class. Promoting `draft/` → `stable/` is a file move.

## Microschema file format

A microschema is a JSON **fragment**, not a full class schema. It has
two top-level keys: `microschema` (metadata) and `fields` (body shape).

```json
{
    "microschema": {
        "host_class": "treatment",
        "discriminator_value": "drug",
        "version": "1.0.0",
        "maturity_level": "stable"
    },
    "fields": [
        {
            "name": "drug_name",
            "type": "ontology_term",
            "blank_value": { "node": "", "name": "" },
            "default_value": { "node": "", "name": "" },
            "mustBeNonEmpty": true,
            "mustBeScalar": true,
            "mustNotHaveNaN": false,
            "queryable": true,
            "ontology": null,
            "documentation": "Identity of the administered substance, expressed as an ontology term.",
            "constraints": {}
        },
        {
            "name": "dose",
            "type": "double",
            "blank_value": 0,
            "default_value": 0,
            "mustBeNonEmpty": true,
            "mustBeScalar": true,
            "mustNotHaveNaN": true,
            "queryable": true,
            "ontology": null,
            "documentation": "Numeric dose administered, in dose_units.",
            "constraints": {}
        },
        {
            "name": "dose_units",
            "type": "char",
            "blank_value": "",
            "default_value": "",
            "mustBeNonEmpty": true,
            "mustBeScalar": true,
            "mustNotHaveNaN": false,
            "queryable": true,
            "ontology": null,
            "documentation": "Units of dose (e.g., 'mg/kg', 'µM').",
            "constraints": { "maxLength": 64 }
        },
        {
            "name": "route",
            "type": "char",
            "blank_value": "",
            "default_value": "",
            "mustBeNonEmpty": false,
            "mustBeScalar": true,
            "mustNotHaveNaN": false,
            "queryable": true,
            "ontology": null,
            "documentation": "Route of administration (e.g., 'IP', 'IV', 'topical').",
            "constraints": { "maxLength": 64 }
        }
    ]
}
```

**Rules:**

- `microschema.host_class` must match the parent directory name.
- `microschema.discriminator_value` must match the filename stem.
- `microschema.maturity_level` must match the tier folder (`stable` /
  `draft` / `deprecated`).
- `microschema.version` is semver. Like class_version, it tracks the
  microschema's own evolution.
- `fields` follows the same field-definition shape used in regular
  document class schemas (typed, with `blank_value`, `default_value`,
  etc.). Microschemas may use any type V_delta supports, including
  named composites and nested structures.
- Microschemas **may not** declare `superclasses`, `depends_on`,
  `file`, `directory`, or any other top-level keys reserved for
  document classes.

## Host class linking

A document class becomes a microschema host by declaring two fields with
specific `constraints`:

- A **discriminator field** (typically `char`) whose value names the
  microschema.
- A **body field** of type `structure` whose contents are validated by
  the selected microschema.

Example: `treatment.json` after host-conversion (sketch):

```jsonc
{
    "document_class": {
        "class_name": "treatment",
        "class_version": "2.0.0",
        "superclasses": [ { "class_name": "base" } ],
        "maturity_level": "stable"
    },
    "depends_on": [
        { "name": "subject_id", "mustBeNonEmpty": true,
          "documentation": "...", "must_refer_to_document_class": "subject" }
    ],
    "file": [],
    "fields": [
        {
            "name": "treatment_kind",
            "type": "char",
            "documentation": "Discriminator. Names a microschema under microschemas/treatment/<tier>/<treatment_kind>.json.",
            "constraints": {
                "maxLength": 64,
                "microschema_discriminator_for": "treatment.parameters"
            }
        },
        {
            "name": "parameters",
            "type": "structure",
            "documentation": "Kind-specific parameters; shape determined by treatment_kind.",
            "constraints": {
                "microschema_registry": "treatment",
                "microschema_keyed_by": "treatment_kind"
            }
        }
    ]
}
```

**Constraint keys (new in V_delta meta-schema):**

- On the discriminator field: `microschema_discriminator_for` —
  value is the dotted path of the body field this discriminator selects
  for. Advisory, not required for resolution; documentation aid.
- On the body field: `microschema_registry` (string, required) — the
  host-class-name namespace under `microschemas/`. Usually equals the
  document class's own `class_name`, but doesn't have to.
- On the body field: `microschema_keyed_by` (string, required) — the
  name of the discriminator field, relative to the same class block as
  the body field.

## Resolution rules

When validating a document instance:

1. Find the body field on a class in the inheritance chain that has
   `microschema_registry` and `microschema_keyed_by` constraints.
2. Read the value of the field named by `microschema_keyed_by` from the
   same class block on the document instance. Call this `D`.
3. Locate a microschema for `<registry>/<D>` by checking, in order:
   a. The **local overlay** (see "Local overlay" below).
   b. The **central registry** at
      `schemas/V_delta/microschemas/<registry>/<tier>/<D>.json` for any
      tier folder in which it exists.
4. If exactly one microschema is found, validate the body field's value
   against the microschema's `fields`.
5. If **both** local overlay and central registry define `<registry>/<D>`,
   the validator **MUST** raise an error. There is no precedence rule;
   the conflict is treated as authored ambiguity and refuses to validate
   until the user resolves it by removing one definition.
6. If **neither** defines `<registry>/<D>`, the validator **MUST** raise
   an error (strict policy; see below).

A microschema may appear in only one tier folder within the central
registry (CI-enforced — see "CI checks" below).

## Validation policy: strict (closed-set)

Documents whose discriminator value has no registered microschema in
either the local overlay or the central registry **fail validation**.
This is a deliberate choice:

- It prevents documents from being authored with parameter bodies that
  no one ever specified.
- It surfaces the need to register a new variant *before* documents
  accumulate.
- It makes the registry the source of truth for "what kinds of
  treatments exist."

The relief valve for "I want to experiment locally without a central
PR" is the local overlay, not policy relaxation.

## Local overlay

Authors and labs may extend the registry without committing to the
central repository by configuring a **local overlay directory**.

**Configuration:** an environment variable `DID_LOCAL_MICROSCHEMA_PATH`
points to a directory whose layout mirrors `schemas/V_delta/microschemas/`
under that root:

```
$DID_LOCAL_MICROSCHEMA_PATH/
├── treatment/
│   └── my_weird_optogenetic_protocol.json    ← no tier folder; overlay is flat per host
└── measurement/
    └── ...
```

Notes:

- The overlay does **not** use tier folders. Overlay microschemas have
  no tier concept; they are unreviewed personal/lab extensions.
- Overlay files must still conform to the microschema file format and
  rules (the `microschema.maturity_level` field on an overlay file is
  ignored).
- Overlay shadowing of a central microschema is **not allowed**: if a
  discriminator value exists in both the overlay and the central
  registry (any tier), validation errors out. The user must remove one.
- CI runs do not have an overlay path. Production data is therefore
  always validated against the central registry alone.

**Detection at load time:** when the validator initializes, it should
log (at INFO or higher) every overlay microschema it picks up, so users
have visibility into which non-central definitions are in play.

## Contribution funnel

Three levels of commitment, with matching review burden:

| Level | Where | Review | Visibility |
|---|---|---|---|
| **Personal/local** | `$DID_LOCAL_MICROSCHEMA_PATH/<host>/<kind>.json` | None | Author's machine only |
| **Draft (shared)** | `microschemas/<host>/draft/<kind>.json` | Light: correct format, CI passes, no obvious problems | Anyone using did-schema |
| **Stable (canonical)** | `microschemas/<host>/stable/<kind>.json` | Full: domain review, naming, ontology terms, field-level validation rules | Anyone using did-schema |

Promotion `draft/` → `stable/` is a file move plus an updated
`microschema.maturity_level` value, gated on stable-level review.

## CI checks

The following invariants are enforced by CI on `did-schema`:

1. **Filename ↔ metadata agreement.** For every microschema file,
   `microschema.host_class` matches the parent host directory and
   `microschema.discriminator_value` matches the filename stem.
2. **Tier ↔ metadata agreement.** `microschema.maturity_level` matches
   the tier folder it lives in.
3. **Tier uniqueness.** Within a host class, no discriminator value
   appears in more than one tier folder.
4. **Reserved-name protection.** `stable` / `draft` / `deprecated` are
   not used as discriminator values.
5. **Host-class existence.** Every `microschemas/<host>/` corresponds to
   a document class that exists in `schemas/V_delta/stable/<host>.json`
   (or draft/deprecated) AND that class declares a body field with a
   matching `microschema_registry`.
6. **No microschema declares document-class-only keys**
   (`document_class`, `superclasses`, `depends_on`, `file`,
   `directory`).
7. **Index agreement.** Every microschema file is listed in
   `index.json`'s `microschemas` section, and vice versa.

## `index.json` extension

The V_delta index gains a top-level `microschemas` array, parallel to
`schemas`:

```jsonc
{
    "set_version": "V_delta",
    "schemas": [ /* document classes */ ],
    "microschemas": [
        {
            "host_class": "treatment",
            "discriminator_value": "drug",
            "tier": "stable",
            "version": "1.0.0",
            "path": "schemas/V_delta/microschemas/treatment/stable/drug.json"
        }
    ]
}
```

## Open questions

These are not blocking the design but should be settled before or during
implementation:

1. **Versioning interaction.** What happens when a microschema is
   version-bumped (1.0.0 → 1.1.0)? Documents in the wild reference the
   discriminator value but don't pin a microschema version. Options:
   (a) only one version of a microschema can be live at a time
   (simplest); (b) microschemas keep all versions on disk and documents
   pin via a separate field. I'd default to (a) for V_delta.

2. **Inheritance interaction.** If `treatment` is a host and a subclass
   `treatment_drug` inherits from it, does `treatment_drug` have its own
   microschema registry, or does it share `treatment`'s? My read: it
   shares, because the body field is declared on `treatment`. Subclass
   document instances still consult `microschemas/treatment/...`. A
   subclass could declare *its own* body field with its own
   `microschema_registry` if it wants a separate registry, but that's
   probably rare.

3. **What stops a calculator from using microschemas instead of
   per-class declarations?** Nothing technically — `calculator`-style
   discrimination would work. But the convention should be: use
   microschemas for *open registries* (treatments, measurements), use
   per-class declarations for *closed kinds* (calculators, where each
   kind is distinct code). Worth stating in V_delta_SPEC.md so the
   right tool is reached for.

4. **Validator behavior for unknown registry.** If a body field
   declares `microschema_registry: "foobar"` and there's no
   `microschemas/foobar/` directory, is that a load-time error or a
   silent no-op? I'd say load-time error, caught by CI check (5).

5. **Overlay path security.** Should the validator refuse to follow
   symlinks in the overlay path? Or warn? Out of scope for the schema
   model but relevant for consumer tooling.

## Out of scope for this design

- The implementation of the meta-schema extensions (new `constraints`
  keys, new top-level `microschemas` index section).
- The validator rule implementing the resolution algorithm.
- Migration of the existing `treatment`, `treatment_drug`,
  `stimulus_bath`, `virus_injection`, `measurement`, etc. classes to the
  new model. That is its own PR with its own review.
- The DID-matlab side: loader updates, document-instance validation
  against the resolved microschema, examples authoring.

## Status

Design only — no microschemas added, no host classes converted, no
meta-schema changes, no CI checks implemented. Discussion is the
deliverable for this commit. Convert classes and add microschemas in
subsequent PRs once this design is reviewed.
