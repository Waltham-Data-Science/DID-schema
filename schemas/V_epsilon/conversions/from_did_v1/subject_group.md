# Conversion: did_v1 → V_epsilon — `subject_group` → `subject` + `group_assignment`

## Identity

- **V_epsilon target classes:** `subject` (with `is_group = true`) and,
  when a member is named, a companion `group_assignment`.
  `subject_group` moves to `deprecated/`.
- **V_epsilon tier:** `stable` (`subject`), `draft` (`group_assignment`),
  `deprecated` (`subject_group`)
- **did_v1 source:**
  `ndi_common/schema_documents/subject_group_schema.json`: no fields;
  depends_on `subject_id` (opt) — an optional member reference.
- **Status:** `applied-in-tooling`
  (`DID-matlab/+did2/+convert/+migrators/subject_group.m`)

## Summary

With `subject` carrying `is_group`, the standalone `subject_group`
identity class is redundant (`Placement_and_Group_Assignment_Proposal.md`
§2). The migration rewrites the group into a `subject{is_group:true}`,
**carrying the legacy `base.id` forward so references to the group still
resolve**, and re-expresses any named member as an event-sourced
`group_assignment`.

## Field mapping

| did_v1 field | V_epsilon field | Transformation |
|---|---|---|
| (identity) | `subject` document | `base.id` carried; `subject.is_group = true`, `is_biological = false`, `local_identifier`/`description` empty |
| depends_on `subject_id` (member) | companion `group_assignment` | `group_assignment.depends_on`: `subject_id` = the member, `group_id` = the new subject's `base.id` |
| — | `group_assignment.batch_id` | empty |
| — | `group_assignment.time_reference_#` | omitted — legacy has no assignment time; backfill |

## Default values for new fields

`subject.is_group = true` (the whole point), `is_biological = false`. The
`subject` keeps the legacy `base.id` and `session_id`; the
`group_assignment` mints a fresh id and shares the `session_id`.

## Worked example

`subject_group` (id `G`, member `M`) → `subject{is_group:true}` with
`base.id = G`, plus `group_assignment{subject_id:M, group_id:G}`.

## Open questions

- The real legacy `subject_group` carries at most one optional member; a
  group with many members was represented by many `subject_group` docs or
  by member-side links. Multi-member groups may need a corpus-specific
  pass to mint one `group_assignment` per member.
- "Migrate-then-tighten": `group_assignment.group_id` targets `subject`;
  the migration must complete before any tightening of that reference.

## Cross-references

- `Placement_and_Group_Assignment_Proposal.md` §2, `Subject_Document_Proposal.md`
- Migrator: `DID-matlab/src/did/+did2/+convert/+migrators/subject_group.m`
- General file-handling rules: [`_files.md`](_files.md)
