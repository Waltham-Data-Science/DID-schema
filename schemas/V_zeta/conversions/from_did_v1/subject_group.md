# `subject_group` → `subject` (`is_group: true`)  [Brainstorm I]

Status: **drafted**

`subject_group` is **deprecated** in V_zeta (see `V_zeta_SPEC.md`,
"Deprecated / folded" table). A group of subjects is modeled as a
`subject` flagged `is_group: true`, and membership becomes
`group_assignment` events.

## Mapping (per document, 1 → 1)

| did_v1 `subject_group` | V_zeta `subject` | Transformation |
|---|---|---|
| (class) `subject_group` | (class) `subject`, `is_group: true` | class fold |
| `subject_group.group_name` (optional; absent in v1 corpus) | `subject.local_identifier` | char copy |
| `subject_group.description` (optional) | `subject.description` | char copy |
| — | `subject.is_biological` | `false` (a group is not a biological individual) |
| `base.*` | `base.*` | carried unchanged (same document id) |

The legacy `subject_group` document is an (essentially empty) marker; it
carries **no members** — membership is expressed by member subjects
referencing the group. So the per-document migration produces only the
group `subject`.

## Membership → `group_assignment` (relational, NDI layer)

In V_zeta, member→group membership is event-sourced as `group_assignment`
annotations (member `subject_id` + `group_id`). **However, did_v1 does not
record group membership anywhere**: the `subject_group` body is empty and no
v1 document depends on a `subject_group` (verified across the did_v1 document
set). There is therefore **no v1 source to migrate into `group_assignment`**
— synthesizing edges would invent data. The migration is complete with the
group `subject` alone; `group_assignment` is a forward-looking class for
newly authored data, not a migration target. If a specific corpus turns out
to encode membership out-of-band (e.g., a lab-specific table), that becomes
a targeted, corpus-specific NDI-layer pass at that time.

## Engine

Routed by `did2.convert.v1_to_v2` under `TargetVersion='V_zeta'` to
`+did2/+convert/+migrators_e/subject_group.m`. A 1 → 1 fold; the default
`V_zeta` target is unaffected (it keeps `subject_group` as-is).
