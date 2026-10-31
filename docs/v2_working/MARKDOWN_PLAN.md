# Markdown out of `schemas/`: inventory and cleanup plan (PROPOSED, not decided)

Implements `V_eta_go_forward_class_audit.md` [markdown out of schemas] (Decided by Jess Haley,
2026-10-25). Which files to delete is **Proposed (not decided)**: this is the list for the team
to approve. Safeguard treated as binding: a document holding decision lines is kept, or its
lines are moved, never lost. Nothing was written to any repository.

## Denominators (measured first)

- Tree measured: `/home/user/DID-schema` at HEAD `97239c6` (branch
  `claude/ecstatic-pascal-md91fw`). `git rev-list --left-right --count origin/main...HEAD` =
  `2 45`: HEAD is 45 commits ahead of and 2 behind the local `origin/main` ref (`6154b1a`, #130).
  No `git fetch` was run (read-only), so the remote may have moved. Re-run on the branch that does the move.
- `ls schemas/*.md | wc -l` = **65** files. All 65 inspected.
- Decision lines, via `tools/decision_citations.py` `scan_decision_lines` (the tool's own parser):
  **357** lines in **34** files (241 `Decided by`, 116 `TEAM-SIGN-OFF`; 355 accepted, 2 rejected:
  1 in go_forward_class_audit, 1 in method_parameters_plan). Plain `grep -cE '^(Decided by |TEAM-SIGN-OFF)'`
  gives 361 in the same 34 files (the 4 extra are inside code fences or HTML comments, which the parser skips).
  **31** files hold 0 lines: 3 generated and 28 hand-written.
- References: `git grep -lF <basename>` over tracked files in `tools/ schemas/ CLAUDE.md web/ .github/ tests/`,
  not counting the file itself. `web/public/` is untracked build output (2 tracked files) and is excluded.
  The "tools" column counts a name in code **or a comment**. The confirmed readers are listed in section 3.
- Also outside this count, but affected (section 5): 28 `.md` under `schemas/V_eta/` (27 in
  `conversions/from_did_v1/`, 1 `microschemas/_DESIGN.md`), 6 JSON artifacts at the `schemas/` top
  level, and 26 `.md` under `review/`.
- Siblings: `/home/user/DID-matlab` and `/home/user/NDI-matlab` are not present. Whether
  sibling code or workflows name a `schemas/*.md` path: **NOT CHECKED**. This must be checked before the move.

## 1. Inventory (65 rows)

DL = decision lines (parser). Refs = referencing files. Gen = generated. KB = size.
Rec: KEEP-P = keep, move to `docs/plans/`; KEEP-H = keep, move to `docs/history/`; KEEP-G = generated,
moves with its generator; KEEP-R = keep, `docs/` root; DEL-A = delete, no live referrer;
DEL-B = delete after fixing the pointers listed in section 4; ASK.

| # | file | what it is | last | KB | DL | refs | tools naming it | Rec |
|---|---|---|---|---|---|---|---|---|
| 1 | V_alpha_SPEC.md | spec of the V_alpha format (tree deleted) | 05-12 | 36 | 0 | 2 | - | DEL-A |
| 2 | V_alpha_notes.md | README for the deleted `V_alpha/` dir | 05-12 | 1 | 0 | 1 | - | DEL-A |
| 3 | V_beta_SPEC.md | spec of V_beta (tree deleted) | 05-12 | 38 | 0 | 5 | - | DEL-A |
| 4 | V_beta_notes.md | README for the deleted `V_beta/` dir | 05-12 | 3 | 0 | 3 | - | DEL-B |
| 5 | V_gamma_SPEC.md | spec of V_gamma (tree deleted) | 05-24 | 79 | 0 | 5 | - | DEL-B |
| 6 | V_gamma_notes.md | README for the deleted `V_gamma/` dir | 05-12 | 8 | 0 | 3 | - | DEL-B |
| 7 | V_delta_SPEC.md | spec of V_delta (tree deleted) | 05-23 | 7 | 0 | 5 | - | DEL-B |
| 8 | V_delta_notes.md | README for the deleted `V_delta/` dir | 05-22 | 6 | 0 | 1 | - | DEL-A |
| 9 | V_epsilon_SPEC.md | spec of V_epsilon (tree deleted) | 06-23 | 17 | 0 | 1 | - | DEL-A |
| 10 | V_epsilon_notes.md | README for the deleted `V_epsilon/` dir | 06-11 | 9 | 0 | 1 | - | DEL-A |
| 11 | V_zeta_SPEC.md | spec of V_zeta (tree deleted) | 07-04 | 18 | 0 | 1 | - | DEL-A |
| 12 | V_zeta_notes.md | README for the deleted `V_zeta/` dir | 07-04 | 11 | 0 | 0 | - | DEL-A |
| 13 | V_eta_notes.md | README for `V_eta/` as a sandbox "to be copied to V1"; cites deleted `build_v_eta.py` (2 hits) | 08-21 | 9 | 0 | 1 | - | DEL-B |
| 14 | V_eta_SPEC.md | V_eta format spec; CLAUDE.md §4: predates the entity merge | 08-21 | 14 | 0 | 10 | - | KEEP-H |
| 15 | did_query_model.md | abstract, language-neutral query model for DID/NDI | 05-12 | 11 | 0 | 2 | - | KEEP-R |
| 16 | V_eta_6_7_walkthrough_STATE.md | "LIVE STATE" of a walkthrough, now CLOSED (its line 119); holds informal "decided" prose | 08-21 | 15 | 0 | 3 | (tests/test_veta.py comment) | KEEP-H |
| 17 | V_eta_OPEN_WORK.md | the open-work index | 10-23 | 107 | 2 | 29 | 11 tools | KEEP-R |
| 18 | V_eta_STATUS.md | status board | 10-26 | 75 | 0 | 11 | status_board, gates, decision_citations | KEEP-G |
| 19 | V_eta_class_provenance.md | origin + disposition of each class; its banner says "PARTIALLY STALE", superseded for dispositions by final_class_set and the ledger | 08-21 | 17 | 0 | 3 | - | ASK |
| 20 | V_eta_clock_alignment_cluster_plan.md | syncrule/syncgraph -> clock alignment | 10-23 | 38 | 3 | 12 | check_signoff_header_staleness, decision_citations | KEEP-P |
| 21 | V_eta_coverage_ledger.md | coverage ledger | 10-26 | 183 | 0 | 11 | coverage, gates, decision_citations | KEEP-G |
| 22 | V_eta_daq_family_decisions.md | daq ingestion family dispositions | 10-22 | 29 | 4 | 15 | check_signoff…, decision_citations, tenet_map | KEEP-P |
| 23 | V_eta_data_body_model_plan.md | data_body model (axes, datum, encoding) | 10-23 | 109 | 47 | 28 | canonical_units, coverage, tenet_map | KEEP-P |
| 24 | V_eta_discovery_notes.md | corpus measurements from the pre-port shape (did_v1 -> V_eta) | 10-22 | 15 | 0 | 2 | - | KEEP-H |
| 25 | V_eta_distance_metadata_plan.md | distance_metadata reshape; "Part B deferred" | 08-21 | 6 | 0 | 0 | - | ASK |
| 26 | V_eta_duplicate_entities_plan.md | `same_as` for one thing recorded twice | 10-22 | 5 | 1 | 9 | tenet_map | KEEP-P |
| 27 | V_eta_ensemble_plan.md | ensemble model | 10-23 | 28 | 4 | 15 | decision_citations, tenet_map | KEEP-P |
| 28 | V_eta_entity_composition_plan.md | one entity class, statements by composition | 10-22 | 13 | 12 | 31 | 6 tools | KEEP-P |
| 29 | V_eta_epoch_plan.md | acquisition epoch family | 10-23 | 96 | 12 | 26 | check_signoff…, coverage, decision_citations, status_board | KEEP-P |
| 30 | V_eta_final_class_set.md | the persist set | 10-23 | 4 | 0 | 19 | regen_final_class_set, gates, check_veta_viewer, decision_citations; web; 3 workflows | KEEP-G |
| 31 | V_eta_frequency_filter_model_plan.md | frequency_filter model | 10-22 | 12 | 4 | 13 | coverage, decision_citations | KEEP-P |
| 32 | V_eta_go_forward_class_audit.md | class audit; the main decision log | 10-26 | 126 | 128 | 29 | check_signoff…, coverage, decision_citations, validate_v_eta | KEEP-P |
| 33 | V_eta_ground_truth_plan.md | "migrate from NDI templates" plan (CLAUDE.md §5) | 08-21 | 11 | 0 | 6 | check_migrator_vocabulary, ndi_ground_truth | KEEP-P |
| 34 | V_eta_image_model_plan.md | image model | 10-23 | 14 | 2 | 13 | coverage, decision_citations, tenet_map | KEEP-P |
| 35 | V_eta_infra_family_decisions.md | infra families: proposed dispositions; its own correction note says the replacement is "NOT DECIDED" | 08-21 | 15 | 0 | 2 | - | KEEP-H |
| 36 | V_eta_ingested_payload_findings.md | daq ingested-payload family | 10-23 | 18 | 1 | 6 | check_signoff…, decision_citations | KEEP-P |
| 37 | V_eta_linked_session_plan.md | linked and ingested sessions | 10-25 | 6 | 3 | 12 | - | KEEP-P |
| 38 | V_eta_logical_observation_plan.md | logical_observation, valid_interval | 10-22 | 28 | 2 | 10 | decision_citations, tenet_map | KEEP-P |
| 39 | V_eta_method_parameters_plan.md | spike-processing parameters -> method | 10-22 | 53 | 3 | 7 | decision_citations | KEEP-P |
| 40 | V_eta_method_plan.md | one method shape; stimuli as methods | 10-22 | 14 | 9 | 28 | check_duplicate_field_declarations, coverage | KEEP-P |
| 41 | V_eta_migration_plan.md | did_v1 -> V_eta migration plan (Brainstorm J); carries the HISTORICAL-SIGNOFF-CLAIM marker | 10-22 | 53 | 0 | 9 | - | KEEP-H |
| 42 | V_eta_migrator_vocabulary_audit.md | migrator vocabulary audit; informal "Decided as" prose | 10-22 | 20 | 0 | 1 | - | KEEP-H |
| 43 | V_eta_ngrid_family_findings.md | ngrid / RF / Hartley | 10-22 | 24 | 3 | 11 | check_citations, decision_citations | KEEP-P |
| 44 | V_eta_nonsubject_cohesiveness_plan.md | non-subject redesign; informal "Decided families" | 10-22 | 34 | 0 | 2 | - | KEEP-H |
| 45 | V_eta_openminds_controlled_terms_binding_plan.md | openMINDS controlled-term bindings ("implemented in build_v_eta.py") | 08-21 | 5 | 0 | 2 | tenet_map (reads it) | KEEP-H |
| 46 | V_eta_openminds_family_record.md | openMINDS walkthrough record | 10-22 | 68 | 4 | 12 | decision_citations, tenet_map | KEEP-P |
| 47 | V_eta_prefix_spelling_plan.md | CURIE prefix spelling | 10-22 | 17 | 1 | 13 | check_binding_governance, check_term_registry | KEEP-P |
| 48 | V_eta_recording_observation_plan.md | raw recordings as observations | 10-23 | 17 | 14 | 18 | decision_citations, tenet_map | KEEP-P |
| 49 | V_eta_relation_inheritance_plan.md | what a relation passes; session_id edge | 10-23 | 14 | 9 | 14 | - | KEEP-P |
| 50 | V_eta_second_pass_plan.md | NDI second-pass design ("Status: design") | 08-21 | 8 | 0 | 0 | - | ASK |
| 51 | V_eta_source_unit_plan.md | source_unit is a term | 10-22 | 5 | 2 | 54 | check_binding_governance | KEEP-P |
| 52 | V_eta_spatial_transcriptomics_plan.md | #73 review: spatial transcriptomics | 10-22 | 48 | 9 | 18 | coverage, decision_citations, tenet_map | KEEP-P |
| 53 | V_eta_statement_referent_findings.md | open question: who a statement can be about ("NOTHING HERE IS DECIDED") | 08-21 | 7 | 0 | 0 | - | ASK |
| 54 | V_eta_stimulus_model_plan.md | stimulus model | 10-23 | 26 | 4 | 14 | coverage, decision_citations | KEEP-P |
| 55 | V_eta_stimulus_parameter_plan.md | stimulus parameters family | 10-23 | 16 | 1 | 7 | check_signoff…, decision_citations | KEEP-P |
| 56 | V_eta_stimulus_response_model_plan.md | stimulus response family | 10-23 | 35 | 8 | 19 | bar2_gap, check_signoff…, coverage, decision_citations | KEEP-P |
| 57 | V_eta_study_plan.md | study, instance_of, awarded_to, roles | 10-22 | 25 | 24 | 21 | check_binding_governance, coverage | KEEP-P |
| 58 | V_eta_subject_calculation_plan.md | subject_calculation family | 09-29 | 25 | 3 | 9 | decision_citations | KEEP-P |
| 59 | V_eta_tenet_audit.md | tenet audit of the class set | 10-22 | 46 | 5 | 19 | decision_citations, tenet_map | KEEP-P |
| 60 | V_eta_tenets.md | tenets T1-T20 | 10-22 | 81 | 9 | 36 | tenet_map, check_veta_viewer, check_signoff…, coverage; web; 2 workflows | KEEP-R |
| 61 | V_eta_term_registry_plan.md | term registry (T19) | 10-22 | 15 | 9 | 16 | check_term_registry, gates | KEEP-P |
| 62 | V_eta_time_reference_family_plan.md | time_reference family scoping ("nothing built") | 08-21 | 12 | 1 | 7 | decision_citations | KEEP-P (MERGE? see 4) |
| 63 | V_eta_time_reference_model_plan.md | time_reference model | 10-02 | 48 | 6 | 24 | status_board | KEEP-P |
| 64 | V_eta_tombstone_audit.md | snapshot of `check_tombstones.py` output (header says "Generated by", but the tool writes no file) | 08-21 | 19 | 0 | 2 | - | DEL-B |
| 65 | V_eta_tuning_model_plan.md | tuning composite model | 10-23 | 20 | 8 | 12 | tenet_map | KEEP-P |

Totals: KEEP-P 33 (the 32 decision-line plan files plus ground_truth_plan), KEEP-R 3, KEEP-G 3, KEEP-H 8,
DEL-A 8, DEL-B 6, ASK 4. Sum 65. All 34 decision-line files are kept: 32 in plans/, plus OPEN_WORK and tenets at the docs/ root.

## 2. Proposed `docs/` layout

    docs/
      V_eta_tenets.md, V_eta_OPEN_WORK.md, did_query_model.md   (entry points)
      plans/      33 plan and decision documents; FLAT, so a bare document name stays unique
      generated/  V_eta_STATUS.md, V_eta_coverage_ledger.md, V_eta_final_class_set.md,
                  V_eta_corpus_proof.md (written by corpus_proof_snapshot.py; not in the tree now)
      history/    superseded documents kept for their record (8, plus any ASK kept)

File names stay the same in this step. Decision citations name a document by its basename (the
`CITATIONS` table, 58 class JSON files under `schemas/V_eta/`, tenet_map rows, and the coverage
NO_TARGET table). Renaming `V_eta_*` -> `did_v2_*` at the same time would touch all of those. ASK: rename in a later step?
Recommended rule: a bare document name resolves to the unique `docs/**/<name>`, and a duplicate
basename fails the gate. Then moving a file between subfolders never breaks a citation.

## 3. Tools and paths that must change

The tools that **glob or list all of `schemas/*.md`** must point at `docs/**/*.md`:
- `tools/decision_citations.py`: `SCHEMAS` (line ~61), `document_path` (bare name -> schemas/), the census
  `os.listdir(root)`, and `pending_builds` `glob(schemas/*.md)`. `GENERATED_MARKDOWN` stays by basename.
  This is the safeguard tool. Its census must read the same 357 lines after the move as before.
- `tools/check_signoff_header_staleness.py`: `SCHEMA_DIR` glob; `IN_TEXT_DOCS`.
- `tools/check_prose_counts.py`: `SCHEMA_DIR` glob (two places). The noun `plan_documents` ("N markdown
  files under schemas/") needs redefining or retiring. Its dated prose occurrences are in OPEN_WORK.
- `tools/check_citations.py`: the `SCHEMA_DIR` glob, and the repo-detection regex `schemas/` (line ~683).
- `tools/check_build_claims.py`: `OPEN_WORK` path, and `os.listdir(SCHEMA_DIR)` for `.md`.

The tools that **open or write named files**:
- `tools/status_board.py` `OUT`, `tools/coverage.py` `LEDGER` (the .md), `tools/regen_final_class_set.py` `OUT`,
  and `tools/corpus_proof_snapshot.py` `SNAPSHOT_MD` -> `docs/generated/`.
- `tools/gates.py`: the `writes=[...]` declarations for the three generated .md, the final_class_set entries
  (lines ~645-648), and comments.
- `tools/tenet_map.py`: `TENETS_DOC` and `read_doc` (`SCHEMAS / name`), which open the docs named in TENET_MAP rows.
- `tools/check_veta_viewer.py`; `web/src/veta/sources.ts` (`?raw` imports of final_class_set and tenets);
  `web/vite.config.ts` (the comment; `fs.allow` is the repo root, so no change is needed); `web/README.md`;
  `web/src/veta/VetaViewer.tsx`, `web/src/veta/grammar.json`.
- `.github/workflows/deploy-web.yml` and `web-build.yml`: the path filters on the two .md; `tests.yml` comments.
- Tests: 5 hard-code `schemas/<doc>.md` (test_status_board_without_siblings, test_tool_skip_denominators,
  test_veta_stimulus_response, test_veta_time_reference, test_veta_time_reference_family_uniqueness). 6 more join
  `schemas` with a .md or glob it (test_confirm_sheet, test_coverage_stage_ladder, test_gates,
  test_signoff_scanner_quotes_and_supersession, test_status_board_evidence, test_veta).
- `schemas/V_eta/stable/did_schema_meta.json` names `schemas/<doc>.md` by path. The other class JSON uses bare names.
- `CLAUDE.md`: §2 table paths, rule 1 ("DO NOT WRITE TO `schemas/`" becomes `schemas/` and `docs/`), §4 plan list,
  and the `OPEN_WORK` citation convention. Also `README.md`.
- Siblings: NOT CHECKED (not present). Grep DID-matlab and NDI-matlab for `schemas/[A-Za-z_]+\.md` first.
  If any sibling reads one, it changes first (CLAUDE.md §3 "siblings first").

Acceptance check for the move PR: `decision_citations` census line count before = after (357 lines,
34 files); `--pending --strict` gives the same result; and `python3 tools/gates.py --check` is green.

## 4. DELETE candidates (for team approval)

Every candidate holds **0** decision lines by the parser and by plain grep. Superseded-by evidence:
`ls -d schemas/*/` prints only `schemas/V_eta/`. `V_eta_OPEN_WORK.md` row #128 says "`tools/build_v_eta.py`
and the `V_alpha`..`V_zeta` trees are deleted". Git history keeps every deleted file.

**DEL-A, no live referrer.** Each file is named only by other files in this delete set.
1. `V_alpha_SPEC.md`: format spec for the deleted V_alpha tree. Superseded by V_eta_tenets + V_eta_SPEC.
2. `V_alpha_notes.md`: README for the deleted `V_alpha/` directory.
3. `V_beta_SPEC.md`: spec for the deleted V_beta tree. Named only by the V_alpha/V_beta/V_gamma spec and notes files.
4. `V_delta_notes.md`: README for the deleted `V_delta/`.
5. `V_epsilon_SPEC.md`: spec for the deleted V_epsilon tree. Named only by V_epsilon_notes.
6. `V_epsilon_notes.md`: README for the deleted `V_epsilon/`.
7. `V_zeta_SPEC.md`: spec for the deleted V_zeta tree. Named only by V_zeta_notes.
8. `V_zeta_notes.md`: README for the deleted `V_zeta/`. 0 referrers.

**DEL-B, delete after rewriting the pointers.** Each pointer becomes "(deleted; see git `<sha>`)" or is dropped.
9. `V_beta_notes.md` (deleted tree). Pointer: `schemas/V_eta/conversions/from_did_v1/_universal_renames.md`.
10. `V_gamma_SPEC.md` (deleted tree). Pointers: `schemas/V_eta/stable/CURIE_lookups_meta.json`,
    `schemas/V_eta/stable/did_schema_meta.json` (description text, so this is a schema-file edit),
    `conversions/from_did_v1/_universal_renames.md`, `review/73/audit_B_composites.md`,
    `review/tenet-audit-2026-10-22/audit_T8-T14.md`. ASK if the team wants it in history instead.
11. `V_gamma_notes.md` (deleted tree). Pointers: `conversions/from_did_v1/_universal_renames.md`, `probe_location.md`.
12. `V_delta_SPEC.md` (deleted tree). Pointers: `V_eta_SPEC.md`, `schemas/V_eta/microschemas/_DESIGN.md`.
13. `V_eta_notes.md`: describes `V_eta/` as a sandbox "copied to `schemas/V1/`", built by `build_v_eta.py`.
    Superseded by CLAUDE.md §3 ("The JSON under `schemas/V_eta/` is the source"; build script deleted, OPEN_WORK #128)
    and by [schema set renamed did_v2]. Pointer: `V_eta_migration_plan.md`.
14. `V_eta_tombstone_audit.md`: a frozen 2026-08-21 snapshot of the census that the `check_tombstones` gate step
    prints on every run (`gates.py --list` includes `check_tombstones`). Superseded by running the tool.
    Pointers: `V_eta_ground_truth_plan.md`, `V_eta_stimulus_parameter_plan.md`.

**ASK (the team decides; 0 decision lines in each).**
- `V_eta_class_provenance.md`: its banner says the dispositions are stale, but "the origin column still serves
  as the source-vs-target arbiter". Delete, or keep in history for the origin column?
- `V_eta_distance_metadata_plan.md`: is "Part B" still open? If yes, it becomes an OPEN_WORK row, then delete or history.
- `V_eta_second_pass_plan.md`: a 2026-08-21 design; NDI's second pass has since merged (#1021). Is it superseded? Not verified here.
- `V_eta_statement_referent_findings.md`: an open question with no referrer. Is it still open? If so, it needs an OPEN_WORK row before any delete.
- `V_eta_time_reference_family_plan.md` (1 line, cited by `decision_citations` for `epochclocktimes`): merge into
  `V_eta_time_reference_model_plan.md`? That would also change the citation document. Default: keep as is.

**Not proposed for deletion.** These hold informal "decided" prose that the parser does not count. Under the
safeguard they move to `docs/history/`: 6_7_walkthrough_STATE, migrator_vocabulary_audit,
nonsubject_cohesiveness_plan, migration_plan, infra_family_decisions. Also kept: openminds_controlled_terms_binding_plan
(tenet_map opens it), V_eta_SPEC (CLAUDE.md and README cite it), and discovery_notes.

## 5. Outside the 65, but needed for "`schemas/` holds only schema sets"

- 28 `.md` inside `schemas/V_eta/` (conversions/from_did_v1 x27, microschemas/_DESIGN.md): do they ship with
  `did_v2/` or move to `docs/`? ASK.
- 6 top-level JSON: `did_v2_coverage_ledger.json`, `did_v2_decisions.json`, `did_v2_migration_targets.json`,
  `did_v2_ndi_ground_truth.json`, `did_v2_openminds_crosswalk.json`, `did_v2_term_registry.json`. They are not schema
  sets, and many tools read them (status_board, coverage, validate_v_eta, check_term_registry, …). ASK: same step or later?
- `review/` (26 .md) and the root `Ideas.md` / `todo.md` are not covered by the decision. decision_citations
  reads `review/73/OPEN_ITEMS.md` by path.
