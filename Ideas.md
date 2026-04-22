# Ideas

Running list of design ideas to consider for future brainstorms.

- Rename the `subject` classname to `subject_identifier`. The current `subject`
  document would then become a document that carries metadata about the
  subject, and `subject_identifier` would be a `_depends_on` tag used to tie
  together all of a given subject's digital records.

- Allow globally immutable openMinds documents to be linked.

## Follow-on work for treatment consolidation

- Author a canonical `drug_treatment` profile under
  `schemas/V_beta/profiles/` that supersedes the retired `treatment_drug.json`
  schema. Required fields at minimum: `drug` (ontology), `dose` (quantity,
  canonical unit TBD by domain expert — likely `mg_per_kg` or `mg`), `route`
  (ontology). Optional: `onset` (relative_quantity, same shape as in
  `virus_injection`).

- Author a `mammalian_stereotaxic_virus_injection` profile that `extends:
  "virus_injection"` and adds required stereotaxic coordinate fields
  (`stereotaxic_ap`, `stereotaxic_ml`, `stereotaxic_dv` as `quantity` with
  canonical unit `mm`) plus a `target_region` field constrained to
  UBERON:brain descendants.

- Consider applying the same profile mechanism to the stimulus family
  (`stimulus_bath`, `stimulus_presentation`, etc.) once it is proven on
  treatments. Different domain (stimulus-to-element rather than
  treatment-to-subject) but the same `_shape_from_minischema` + `_minischema`
  mechanism would apply unchanged.

- Decide and document a canonical-unit convention for cross-profile
  coherence: when two profiles measure the same physical quantity, they must
  use the same canonical unit (e.g., all volumes in nL, all times in days or
  seconds, not mixed). A small registry table in this repo (or the spec)
  would help enforce this by review.
