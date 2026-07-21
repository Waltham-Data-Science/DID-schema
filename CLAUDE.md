# DID-schema — working context for Claude

## READ THESE BEFORE answering about V_eta class structure or the migration walkthrough
The conversation gets compacted and loses fine-grained state. The durable record
lives in these files — read them instead of re-deriving from memory:

- **`schemas/V_eta_final_class_set.md`** — the authoritative persist set (7
  categories). REGENERATE with `python3 tools/regen_final_class_set.py` (reads the
  built `V_eta/index.json` disposition markers) after every `build_v_eta.py`; never
  hand-edit. NOTE: its counts are only as good as the `disposition` markers in
  build_v_eta.py (`_RET_SOURCES`/`_RET_CARRIERS`/`_IN_PROGRESS`) — dissolved source
  classes not listed there (treatment-family, image_stack, subject_group) still show
  as `persist`; fix the markers, not the doc. Category order is fixed:
  ① spine → ② entities → ③ **composites (data_type)** → ④ leaf tier →
  ⑤ time_reference → ⑥ **data_body (EXACTLY 2: sampled_body, opaque_body)** → ⑦ infra.
- **`schemas/V_eta_6_7_walkthrough_STATE.md`** — the ⑥/⑦ (infra) walkthrough with
  per-chunk (a–e) status. Update the status table as chunks land.
- **`schemas/V_eta_nonsubject_cohesiveness_plan.md`** — decisions D-A…D-F.
- **`schemas/V_eta_go_forward_class_audit.md`** — per-class dispositions.
- The live task list (TaskList) — the remaining chunks/tracks; it survives
  compaction. Keep it current: mark chunks in_progress/completed as you go.

## Hard-won facts (do not re-litigate)
- `data_body` has EXACTLY two members: `sampled_body`, `opaque_body`. Every
  format/series carrier (`timeseries_data*`, `dataseries_data`, `zarr`,
  `ephys_zarr`, `image_zarr`, `image`, `generic_file`, `pyraview`, …) PHASES OUT
  into those two (encoding becomes a field). Never list them under data_body.
- `zarr` is a storage format (⊂ base), NOT a quantity composite.
- Composites (③) list BEFORE leaves (④). The user has asked for this repeatedly.
- must_refer is DECLARATIVE (existence-only validation), not type-checked.
- Corpus gate: 0 quarantine + 0 orphans; per-class counts shift as classes
  dissolve, total-doc counts are the invariant. Soph needs DID_RUN_SOPH_TEST=1.
- CALCULATORS ARE DEFERRED. Do NOT register `_calc` decomposition migrators
  (`<x>_calc.m` that split a calc doc into observations). The corpus stores calc
  outputs as `<x>_calc` docs that DOWNSTREAM calcs reference (e.g.
  `contrast_sensitivity_calc.contrasttuning_id_* -> contrast_tuning_calc`).
  Decomposing a `_calc` doc changes/removes its id, so every downstream reference
  DANGLES -> orphans (Soph went red with 11448 such orphans, 5445377). Passthrough
  of `_calc` docs validates against the RETAINED `_calc` schemas and keeps refs
  intact — that is the deferred-calculator green state. Un-defer only when the
  downstream calc CONSUMERS are migrated in the same pass.
- distance_metadata ~2078 JH quarantines ("required `endpoints` missing"): the JH
  files DO carry distance values — an empty read is a BUG, not real missing data.
  Root cause (suspected): `endpoints.numeric_values` is NESTED, so universalRenames
  leaves its raw v1 casing untouched; a camelCase source (`numericValues`) read
  snake-only comes back empty → the migrator's no-vals passthrough branch → the raw
  doc fails the required non-empty `endpoints` → quarantine. Fix applied: read
  numeric_values snake-first + camelCase fallback (like jGetCharAny). CONFIRM via the
  next corpus (the quarantine count should drop ~2078; JH's test does not gate
  quarantine, so watch the discovery report, not just pass/fail). General lesson:
  any NESTED sub-field a migrator reads needs the snake+camelCase fallback.

## Build / test
- `python3 tools/build_v_eta.py` rebuilds `schemas/V_eta/` (copytree V_zeta→V_eta
  then transforms). `python3 -m pytest tests/test_veta.py -q` checks the schema.
- Migrators live in DID-matlab `+did2/+convert/+migrators_j/`; corpus validation is
  DID-matlab `test-code.yml` (full, ~1–2h) and `test-migrators-quick.yml` (~2 min).
