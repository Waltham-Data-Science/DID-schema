# DRAFT sign-off lines -- NOT SIGNATURES, AND OUT OF DATE

Drafted by Claude on 2026-09-23 for the team to review and paste; nobody has signed them. They live
outside `schemas/`, so `tools/status_board.py` does not read them (it scans `schemas/*.md` only).

**Stale since drafting:** they say `derived_from_#` (now `input_id`, T15) and route spike-sorter
output to `count_calculation` (now `label_calculation`, #73 item 35). They also predate #73 items
37-49. Re-draft from `schemas/V_eta_spatial_transcriptomics_plan.md` before anyone signs.

---

--- paste at the end of schemas/V_eta_subject_calculation_plan.md (on its own line, blank line before it) ---
TEAM-SIGN-OFF [calculator mixin dropped (#73)]: jess@walthamdatascience.com / 2026-09-23 (dictated in the #73 review session; transcribed by Claude at jess's explicit request) -- the `calculator` mixin leaves every V_eta chain; `subject_calculation` ⊂ [subject_interaction] declares the required `software_id` + `runtime_environment_id` itself; `calculator` survives only as a `retire` v1 tombstone restating NDI's template; `hartley_calc` and `tuning_fit` no longer inherit from it. Revises items (1) and (2) of the 2026-09-21 signature above.

--- paste at the end of schemas/V_eta_subject_calculation_plan.md (on its own line, blank line before it) ---
TEAM-SIGN-OFF [observation vs calculation (#73)]: jess@walthamdatascience.com / 2026-09-23 (dictated in the #73 review session; transcribed by Claude at jess's explicit request) -- a statement whose inputs are other statements in the dataset is a `subject_calculation` and records them in `derived_from_#`; one produced from data held outside the dataset is a `subject_observation` with no `derived_from`. `derived_from_#` is removed from `subject_observation`. `oneepoch`'s concatenation becomes a calculation (fork A1's direction revised, option 1A). `valid_interval` inheritance stays re-derived. Spike-sorter output (`kilosort_clusters`, `kiasort_clusters`, `jrclust_clusters`) becomes `count_calculation`, revising the 2026-08-17 confirm sheet for `jrclust_clusters`.

--- paste at the end of schemas/V_eta_tuning_model_plan.md (on its own line, blank line before it) ---
TEAM-SIGN-OFF [tuning restructure (#73)]: jess@walthamdatascience.com / 2026-09-23 (dictated in the #73 review session; transcribed by Claude at jess's explicit request) -- the five tuning marker composites are dropped; `tuning_curve_calculation` is concrete ⊂ [subject_calculation, tuning_curve]; the leaves are renamed to `orientation_direction_tuning_calculation`, `contrast_tuning_calculation`, `spatial_frequency_tuning_calculation`, `temporal_frequency_tuning_calculation`, `speed_tuning_calculation`; `circular_statistics` / `interpolated_values` / `model_fit[]` {goodness, metrics, sampled_fit} are typed; the v1 contractions are renamed as in the #73 amendment above. Revises items (1) and (5) of the 2026-09-21 signature above.
