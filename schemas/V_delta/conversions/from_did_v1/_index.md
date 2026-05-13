# did_v1 → V_delta conversion index

This file enumerates every V_delta document type that needs a conversion
doc from `did_v1`, and tracks its status. Update this index whenever a
new conversion doc is added or its status changes.

The corresponding template is [`_TEMPLATE.md`](_TEMPLATE.md). The shared
file-handling rules are in [`_files.md`](_files.md).

## Status legend

- **none** — no conversion doc exists yet
- **drafted** — markdown exists, awaiting domain review
- **reviewed** — domain-reviewed, awaiting implementation
- **applied-in-tooling** — implemented in the migration engine in
  `DID-matlab`, but not yet locked
- **frozen** — implemented, tested against real datasets, locked for
  V_delta
- **no-conversion-needed** — explicitly marked as having no did_v1
  predecessor (use a separate `no-conversion-needed.md` marker file in
  place of a full conversion doc; the doc is still listed here for
  visibility)

## Conversions

| V_delta class_name | did_v1 source | Status | Doc |
|---|---|---|---|

> This table is intentionally empty in the initial scaffolding commit.
> Conversion docs will be added one per row as the aggregation session
> and subsequent domain-review sessions populate them.

## Conventions

- One conversion markdown per V_delta document type. If a V_delta class
  has multiple did_v1 sources (e.g., the same V_delta concept was split
  across two did_v1 types), document the merge in a single file rather
  than splitting across multiple.
- If a V_delta class is genuinely new (no did_v1 ancestor), create
  `<class_name>_no_conversion_needed.md` with a one-line reason and add
  the row with status `no-conversion-needed`.
- File-handling behavior that follows the generic rules in `_files.md`
  should be linked, not restated.
