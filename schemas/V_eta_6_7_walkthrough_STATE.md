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
| **(b)** | **Option A (decided):** the `*_epochdata_ingested` caches are DEVICE-LAYER infra (keyed `{daqreader, epoch}`, NO subject — one raw cache feeds many downstream ROI/channel observations, the subject enters one layer down on the observation/element). They are NOT folded into `sampled_body` (that would force a `subject_statement` the device layer lacks). Tidy only: drop the redundant `epochid` **superclass** mixin from `daqreader_image_epochdata_ingested` (dep-only — the epoch link is the required `epochid` dep → `element_epoch`). `epochfiles_ingested` stays infra untouched (governance typing later). The imaging *observation* tier (movie → `imageseries_observation` of the slice-subject + ROI traces → neuron part-subjects via `part_of`/`derived_from`) is separate NDI-side work → tracked under #9 (D-C). | ✅ DONE | (this batch) |
| **(c)** | subtype-in-name de-encode: `daqreader_ndr` (`_ndr`) → fields onto `daqreader`; `daqreader_mfdaq_epochdata_ingested` (`_mfdaq`) → `parameters` field onto the generic `daqreader_epochdata_ingested`, class dissolves. Both no longer classes. | ✅ DONE | `daqreader_ndr` earlier (green 29628333511); `_mfdaq` this batch |
| **(e)** | `element_epoch` → **`acquisition_epoch`** (element retired; keep `storage` for now — the data_body fold is deferred). ATOMIC 3-repo rename (a LIVE class: NDI writes v1 `element_epoch`, DID migrates it, the NDI V_eta second pass READS it by class name). Surface: **DID-schema** — `RENAME["element_epoch"]="acquisition_epoch"` (propagates class file + superclass + must_refer across `stimulus_response`/`dataseries_channel_map`/`image_stack_parameters`) + prose/`topics.json`. **DID-matlab** — the `element_epoch` migrator, `image_stack.m` (mints it), `pyraview.m`, tests (`testMigrators*`); v1 source defs `*_document_element_epoch.json` stay v1-named. **NDI-matlab** — ONLY the `+migrate/+internal/` V_eta-read refs (`bodyResolver.m` classNameOf/subField, ~4 refs); NDI runtime writers (`timeseries.m`/`tuning_response.m`/`f0_f1_responses.m`/`element.m`) stay `element_epoch` (they write v1). Safety nets: DID corpus run + NDI run-tests. **RESOLVED to DID-ONLY:** NDI's `bodyResolver` refs read the v1 INPUT shape (`element_epoch.epoch_clock`, `epochclocktimes`) to resolve subjects/clocks — v1-read, unchanged; no V_eta consumer of `acquisition_epoch` in NDI. `image_stack` mints element_epoch only for V_zeta (V_eta migration is single-stage → migrators_j + base fallback; migrators_i does not run). So: DID-schema `RENAME` (done) + DID-matlab `migrators_j/element_epoch.m` (reuse base clocks transform, rename class+block) + test. `storage`→data_body deferred. | ✅ DONE (pending corpus) | (this batch) |
| **gov** | Governance sweep across the kept infra: type every untyped `*_id` dep with `must_refer_to_document_class`; the 7 `ndi_<x>_class` handles → needs-NDI (coordinate with NDI-matlab); route embedded clock times through `time_reference`. | ⏳ TODO | — |

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
  `imageseries_data`, `ephys_zarr`, `image_zarr`, `zarr`, `image`, `image_collection`,
  `generic_file`, `pyraview`. Index/geometry infra KEPT: `ngrid`, `dataseries_channel_map`,
  `binaryseries_parameters`, `filter`.
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
