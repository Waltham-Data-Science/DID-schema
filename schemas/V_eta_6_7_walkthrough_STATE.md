# V_eta ⑥+⑦ Walkthrough — LIVE STATE (survives compaction)

**Purpose:** this file is the durable record of the category-⑥/⑦ (acquisition +
infra) walkthrough, so the a/b/c/d/e chunking is NOT lost when the conversation is
summarized. Update the status column as chunks land. If you (Claude) are resuming
after a compaction, READ THIS FILE before re-deriving anything.

Recovered from session transcript turns 6113–6177 (the original a–e breakdown) +
reconciled with what actually shipped this session.

## The walkthrough chunks

| Chunk | Scope | Status | Commit |
|---|---|---|---|
| **(a)** | Delete the 4 time-redundant classes: `oneepoch`, `epochclocktimes`, `valid_interval`, `session_extent` (all 0-usage; `epochclocktimes` was a did_v1 superclass, `pyraview` auto-reparented) | ✅ DONE | `68fba28` |
| **(d)** | "Earns its keep?": `metadata_editor` → **decomposed** to `dataset` + person/org/award/publication/web_resource + relations (went further than keep/kill); `mock` → **dropped** | ✅ DONE | `517db1a`, `172c0b1` |
| **⑥-E** | Session/dataset infra: `session` → ⊂ entity; `dataset_remote` / `dataset_session_info` / `session_in_a_dataset` → **dissolved** to `directed_relation`s (`part_of` / `stored_at` / `hosted_by`) + bare `dataset` entity; `resolveDatasetEntities` post-pass | ✅ DONE | `d650301`, `ddb3071` |
| **(b)** | **Option A (decided):** the `*_epochdata_ingested` caches are DEVICE-LAYER infra (keyed `{daqreader, epoch}`, NO subject — one raw cache feeds many downstream ROI/channel observations, the subject enters one layer down on the observation/element). They are NOT folded into `sampled_body` (that would force a `subject_statement` the device layer lacks). `epochfiles_ingested` stays infra untouched. The imaging *observation* tier is separate NDI-side work → #9 (D-C). <br>⚠️ **THE "TIDY" HALF WAS BUILT ON A FALSE PREMISE — see the correction below.** | ⚠️ PARTLY WRONG | (this batch) |
| **(c)** | subtype-in-name de-encode: `daqreader_ndr` (`_ndr`) → fields onto `daqreader`; `daqreader_mfdaq_epochdata_ingested` (`_mfdaq`) → `parameters` field onto the generic `daqreader_epochdata_ingested`, class dissolves. Both no longer classes. | ✅ DONE | `daqreader_ndr` earlier (green 29628333511); `_mfdaq` this batch |
| **(e)** | `element_epoch` → **`acquisition_epoch`** (element retired; keep `storage` for now — the data_body fold is deferred). ATOMIC 3-repo rename (a LIVE class: NDI writes v1 `element_epoch`, DID migrates it, the NDI V_eta second pass READS it by class name). Surface: **DID-schema** — `RENAME["element_epoch"]="acquisition_epoch"` (propagates class file + superclass + must_refer across `stimulus_response`/`dataseries_channel_map`/`image_stack_parameters`) + prose/`topics.json`. **DID-matlab** — the `element_epoch` migrator, `image_stack.m` (mints it), `pyraview.m`, tests (`testMigrators*`); v1 source defs `*_document_element_epoch.json` stay v1-named. **NDI-matlab** — ONLY the `+migrate/+internal/` V_eta-read refs (`bodyResolver.m` classNameOf/subField, ~4 refs); NDI runtime writers (`timeseries.m`/`tuning_response.m`/`f0_f1_responses.m`/`element.m`) stay `element_epoch` (they write v1). Safety nets: DID corpus run + NDI run-tests. **RESOLVED to DID-ONLY:** NDI's `bodyResolver` refs read the v1 INPUT shape (`element_epoch.epoch_clock`, `epochclocktimes`) to resolve subjects/clocks — v1-read, unchanged; no V_eta consumer of `acquisition_epoch` in NDI. `image_stack` mints element_epoch only for V_zeta (V_eta migration is single-stage → migrators_j + base fallback; migrators_i does not run). So: DID-schema `RENAME` (done) + DID-matlab `migrators_j/element_epoch.m` (reuse base clocks transform, rename class+block) + test. `storage`→data_body deferred. | ✅ DONE (pending corpus) | (this batch) |
| **gov** | Governance sweep across the kept infra. **(1) Type untyped `*_id` deps — DONE:** the ingested-cache `epochid` deps → `acquisition_epoch`; the only remaining untyped dep, `syncrule_mapping.epochid`, is INTENTIONALLY untyped (it holds an epoch NAME, not a doc id — typing it would impose an unsatisfiable existence check). **(2) `ndi_<x>_class` handles → needs-NDI — DONE:** the 6 kept device/sync infra fields (`daqsystem`/`daqreader`/`daqmetadatareader`/`filenavigator`/`syncgraph`/`syncrule`) carry `needs_ndi: true`; `needs_ndi` declared as a meta-schema field property; test `test_ndi_class_handles_marked_needs_ndi`. **(3) Route embedded clock times through `time_reference` — DONE:** `syncrule_mapping.epochnode_a/b` now nest `epoch_clock` + `epoch_id` under a `time_reference` sub-structure (epoch_bounded_reference shape: kind + epoch_clock + epoch_id); `epoch_session_id`/`epochprobemap`/`objectclass` stay as node metadata. epoch_id stays a NAME (embedded ref, not a dep — epoch is not a standalone doc). Applied by DID-matlab `migrators_j.syncrule_mapping`. `acquisition_epoch.clocks` is intentionally left alone — it is the epoch's clock DEFINITION (the referent every epoch_bounded_reference points at), not a reference to route. | ✅ (1)+(2)+(3) DONE (pending corpus) | (this batch) |

## ⚠️ CORRECTION — chunk (b)'s "drop the epochid mixin" was wrong

Chunk (b) recorded: *"drop the redundant `epochid` **superclass** mixin from
`daqreader_image_epochdata_ingested` (dep-only — the epoch link is the required `epochid`
dep → `element_epoch`)."*

**There is no `epochid` dependency in did_v1, and there never was.** Verified against all
three NDI templates on `origin/main`
(`ingestion/daqreader_{,image_,mfdaq_}epochdata_ingested.json`): the ONLY dependency any of
them declares is `daqreader_id`. `epochid` is a **superclass** contributing a block that
holds the epoch-id *string* (`t00001`), which both concrete writers set explicitly
(`+ndi/+daq/+reader/image.m`, `mfdaq.m`).

The decision shipped as `+migrators_j/daqreader_mfdaq_epochdata_ingested.m`:

```matlab
% dep-only: drop the stale inline epochid block (epoch link is the epochid dep).
if isfield(v2Body, 'epochid')
    v2Body = rmfield(v2Body, 'epochid');
end
```

So it **deletes the only record of which epoch the ingested bytes belong to**, and the
document still validates. This is the FRAGMENT failure mode from
`V_eta_migrator_vocabulary_audit.md`: no counter sees it. `did2.validate.silentLoss` cannot,
because nothing is left blank — the block is simply gone.

Also mis-stated by the same reasoning, on the DID side:
- `V_eta/stable/daqreader_epochdata_ingested.json` **invents an `epochid` dependency** typed
  to `acquisition_epoch` — the mirror image of the same error — and omits the `epochid`
  superclass, so the epoch string has nowhere to land.
- `V_eta/stable/daqreader_image_epochdata_ingested.json` has `depends_on: []`, dropping the
  real `mustbenotempty` `daqreader_id` edge, and omits the `metadata` block NDI added after
  the V_eta fork (commit `fa30f2903`).
- There is **no migrator for `daqreader_image_epochdata_ingested`** at all.

**Not yet fixed** — the correction is recorded here first so the decision is not re-derived
from the wrong premise. The lesson generalises: this chunk was decided from the DID-side
schema rather than the NDI template, which is the same root cause as the `V_alpha` migrator
mix-up tracked in `V_eta_ground_truth_plan.md`.

## ⚠️ STATUS — the walkthrough is NOT closed; R5 re-opened the ⑦ infra tier

The section below records the walkthrough closing with 18 classes graduated `in_progress` →
`persist`. **That graduation has since been reversed.** The R5 naming/governance pass found
that the KEEP decisions predated T11/T13 scrutiny (5 siblings needed renames or folds), so
the ⑦ infra tier was re-opened. The built index currently carries **35 `in_progress`
classes**, including the infra ones listed as graduated below.

Read the index (`schemas/V_eta/index.json` disposition markers), not this section, for the
live count. Kept for the decision history.

## WALKTHROUGH CLOSED — disposition graduated (this batch) — SUPERSEDED, see above

All chunks (a–e + gov) are ✅ DONE, so the walkthrough is CLOSED. The 18 decided-KEEP
infra classes graduated from `in_progress` → **persist (⑦)** via `build_v_eta.py`
`_KEEP_INFRA` (persist total 148→166; ⑦ infra 1→19; in_progress 29→11):
`daqsystem`, `daqreader`, `daqmetadatareader`, `daqreader_epochdata_ingested`,
`daqreader_image_epochdata_ingested`, `daqmetadatareader_epochdata_ingested`,
`epochfiles_ingested`, `epochid`, `acquisition_epoch`, `filenavigator`, `syncgraph`,
`syncrule`, `syncrule_mapping`, `directory`, `ngrid`, `dataseries_channel_map`,
`binaryseries_parameters`, `filter`.

RESOLVED SINCE this walkthrough (were `in_progress`, now decided):
`instrument` → **RETIRED** (roles are edges, T7; absent from disk); `app` → **`software`
entity + `software_id` edge** (R1); `image` → **standalone `image` `data_type`** (R6;
`array` killed); `stimulus_presentation` + `control_stimulus_ids` → **`timed_sequence` /
`timed_sequence_manipulation` / `control_designation`** (`V_eta_stimulus_model_plan.md`,
supersedes D-B); `ensemble` → **per-neuron-primary + group-subject + epoch-scoped
`member_of` + rebuildable cache** (`V_eta_ensemble_plan.md`, supersedes the old "grain A /
MAP-doc-as-infra" reading); `openminds_import` → **draft** maturity.

STILL `in_progress` — the genuinely-open classes the walkthrough left for a team call:
`interaction_purpose` (kept as a standalone subject-domain class — see the boundary-class
row in `V_eta_tenet_audit.md`); `demo_ndi`, `demo_ndi_mock` (test fixtures — passthrough);
`projectvar` (infra, passthrough).

## ⑥/⑦ sub-groups (the original grouping, for context)

- **⑥-A DAQ readers/systems** — KEEP infra, each carries `ndi_<x>_class` (needs-NDI):
  `daqsystem`, `daqreader`, `daqmetadatareader`, `filenavigator`; `daqreader_ndr` (→ chunk c).
- **⑥-B DAQ "ingested" caches:** `daqreader_epochdata_ingested`, `daqmetadatareader_epochdata_ingested`
  (KEEP, type deps); `daqreader_mfdaq_epochdata_ingested` (→ c); `daqreader_image_epochdata_ingested` (→ b).
- **⑥-C Epoch/time:** `epochid` ✅clean; `element_epoch` (→ e); the 4 deleted in (a).
  `epochfiles_ingested` (→ b).
- **⑥-D Sync** — KEEP infra (`ndi_*_class`): `syncgraph`, `syncrule`, `syncrule_mapping` (type `epochid`; route `epochnode_*` clock times through `time_reference` — gov).
- **⑥-E Session/dataset** — DONE (see table).
- **⑦ Infra/meta** — KEEP: `directory` (type the two `parent_*` deps — gov), `demo_ndi`,
  `demo_ndi_mock`, `interaction_purpose`; `ndi_reserved_keys` is a META file (not a class).

## Also surfaced by the ⑦ audit (this session) — belongs to OTHER tracks, not ⑥/⑦:

- **→ data_body (2.D fold):** `timeseries_data*`, `dataseries_data`, `dataseries_pyramid`,
  `imageseries_data`, `ephys_zarr`, `image_zarr`, `zarr`, `image_collection`,
  `generic_file`, `pyraview`. Index/geometry infra KEPT: `dataseries_channel_map`,
  `binaryseries_parameters`, `filter`.
  (**R6 update:** bare `image` is NOT in this list — it is now a ③ standalone `image`
  `data_type` composite; only its *pixels* phase into a `sampled_body` via `storage_mode`.
  `ngrid` likewise phases INTO `sampled_body` per R4 — it is no longer "kept index infra".)
- **→ observations (needs-NDI):** `probe_location`, `probe_geometry`, `electrode_offset_voltage`,
  `position_metadata`, `distance_metadata`.
- **→ observations (D10/D11):** `ontology_label`, `ontology_table_row`, `ontology_image`.
- **→ move to ④ composites:** `chemical`, `dose`, `formulation` (data_type composites, not infra).
- **pre-J holdovers → phase out:** `calculator` (parents the analysis zoo, goes with D-C),
  `measurement` (redundant with the observation tier).
- **subject-domain, needs a call:** `instrument`, `interaction_purpose`.

## Guardrail for future turns
Before answering "what's the final class set / where were we on ⑥/⑦", READ THIS FILE
and `V_eta_final_class_set.md`. Do NOT re-derive category membership from memory —
that is what produced the errors (zarr-in-④, data_body>2, ④/③ order). Category order
is: ① spine → ② entities → ③ **composites (data_type)** → ④ leaf tier → ⑤ time_reference
→ ⑥ data_body (EXACTLY 2: sampled_body, opaque_body) → ⑦ infra.
