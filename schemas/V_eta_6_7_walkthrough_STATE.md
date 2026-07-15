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
| **(b)** | data_body collisions → `sampled_body`: `daqreader_image_epochdata_ingested` (`file: frames.bin` + dims = an image-series), `epochfiles_ingested` (inline `files` list). BLOCKED on building the ⑤ data_body collapse (sampled_body/opaque_body fold). | ⏳ TODO | — |
| **(c)** | subtype-in-name de-encode: `daqreader_ndr` (`_ndr`), `daqreader_mfdaq_epochdata_ingested` (`_mfdaq`) → the subtype becomes a FIELD on `daqreader`/the ingested cache, not a class name. | ⏳ TODO | — |
| **(e)** | `element_epoch` — rename (element is retired, so the name is stale) + check its `storage` field → `data_body`. | ⏳ TODO | — |
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
