# V_eta: `study`, `instance_of`, `awarded_to`, contributor `roles`

Four schema additions made for the Haley V2 import (NDI-matlab
`+ndi/+setup/+conv/+haley/import_V2_decisions.md`, entries 8, 11, 14, 18),
built in did-schema PR #78.

- `study` (draft entity): a unit of research with its own question and design,
  between the dataset and its sessions (ISA investigation / study / assay).
  Fields `name` (required), `short_name`, `description`, `factors` (the
  variables deliberately varied; same terms as statement `variable`), `design`.
  `part_of` widened: session -> study, study -> dataset, study -> study.
  Not `protocol` (a recipe) and not `experiment` (the source lab uses that word
  for both the study and the day).
- `instance_of` (relation, subject -> product): an instrument is a unit of a
  bought product. A relation rather than `subject.product_id` so the product can
  be added after the instrument without rewriting either document.
- `awarded_to` (relation, funding -> person/organization): an award's recipient.
- `directed_relation.roles` (bound, preferred): the 14 CRediT contributor roles
  plus `corresponding author`, on a `has_author` / `contributed_by` edge.

TEAM-SIGN-OFF: jess / 2026-09-30 -- add the study entity (name, short_name, description, factors, design) and widen part_of to session->study, study->dataset, study->study
TEAM-SIGN-OFF: jess / 2026-09-30 -- add the instance_of relation (subject -> product) instead of a subject.product_id field
TEAM-SIGN-OFF: jess / 2026-09-30 -- add the awarded_to relation (funding -> person/organization)
TEAM-SIGN-OFF: jess / 2026-09-30 -- add directed_relation.roles, bound to the 14 CRediT roles plus corresponding author

## Session fields (did-schema PR #79)

- `session.description` (optional): a free-text record of the session -- what
  was done, the lab notebook entry, notes about the day.
- `session.name` (optional): a display name beside `local_identifier`, which
  stays the stable handle (spaceless by convention; not schema-enforced).

TEAM-SIGN-OFF: jess / 2026-09-30 -- add optional session.description
TEAM-SIGN-OFF: jess / 2026-09-30 -- add optional session.name as a display name beside local_identifier

## Subject field (did-schema PR #80)

- `subject.name` (optional): a display name beside `local_identifier`, as
  `session.name`. `local_identifier` stays the stable, spaceless handle
  (`concentration_assayPlate0011`); `name` is for people ("Assay Plate 0011",
  "Axio Zoom.V16"), may carry spaces, need not be unique, and can be corrected
  without breaking anything, because nothing refers to a subject by name.
