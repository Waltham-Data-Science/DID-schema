# `subject_group` → `subject` (`is_group: true`)  [Brainstorm E]

Status: **drafted**

`subject_group` is **deprecated** in V_epsilon (see `V_epsilon_SPEC.md`,
"Deprecated / folded" table). A group of subjects is modeled as a
`subject` flagged `is_group: true`, and membership becomes
`group_assignment` events.

## Mapping (per document, 1 → 1)

| did_v1 `subject_group` | V_epsilon `subject` | Transformation |
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

The member→group edges become `group_assignment` events. Those are
**relational**: they require the member subjects that point at this group,
which a single `subject_group` document does not carry. They are therefore
assembled in the NDI layer (`ndi.migrate.local`), the same boundary used
for `stimulus_bath → bath`, not manufactured here. This per-document
migrator emits the group `subject` only; the assignments are a follow-up.

## Engine

Routed by `did2.convert.v1_to_v2` under `TargetVersion='V_epsilon'` to
`+did2/+convert/+migrators_e/subject_group.m`. A 1 → 1 fold; the default
`V_delta` target is unaffected (it keeps `subject_group` as-is).
