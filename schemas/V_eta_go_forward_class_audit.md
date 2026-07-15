# V_eta Go-Forward Class Audit — J-cohesiveness of every live class

*The go-forward V_eta schema = `stable/` + `draft/` (the tiers CI assembles into
`DID_SCHEMA_PATH`; `deprecated/` is excluded). **258** classes. This audit gives
**every** one a J-disposition so the whole set can be reviewed for Brainstorm-J
cohesiveness — not just the families touched piecemeal (D-A…D-E).*

**J-cohesiveness test:** a go-forward class must be one of — a `subject`; a
`subject_statement` (assertion / observation / manipulation); a `subject_relation`;
a `time_reference`; a `data_body`; a legitimate **acquisition/storage-infra** class;
or a **shared genus/composite** the above build on. Anything else is a holdover to
reshape or retire.

## Summary

| Disposition | n | Status |
|---|--:|---|
| **J-native by construction** (spine, leaves, dimension abstracts, time refs) | ~128 | ✅ conform to the J pattern; no action |
| **Decided track — implementation pending** (D-A infra, D-B stimulus, D-C analysis, 2.D data_body) | ~96 | ◑ disposition set; migrators/schema pending |
| **Retire — but still sitting in `stable`** (element, openMINDS family) | 5 | ⚠️ **Phase 8 deletion outstanding** |
| **Genuinely open — need a call** (neuron, filter, infra-scrutiny) | ~8 | ❓ this audit's new worklist |
| **Confirmed infra / meta keep** | ~6 | ✅ verified this pass |

The headline finding: **retired classes are still live.** `element` and the
openMINDS family were *decided* retired (element→subject; openMINDS→assertions) and
have working migrators, but the classes were never deleted from `stable/`, so they
still appear as go-forward. That is the Phase 8 cleanup, now concrete.

---

## 1. J-native by construction (~128) — ✅ no action

These *are* the J model; they conform by definition. Listed for review, not audit.

- **Spine / genus (15):** `base`, `app`, `subject`, `subject_statement`,
  `subject_interaction`, `subject_observation`, `subject_manipulation`,
  `subject_assertion`, `subject_relation`, `directed_relation`, `undirected_relation`,
  `time_reference`, `data_body`, `measurement`, `calculator`.†
- **Data-type observation leaves (34)** and **assertion leaves (30)** and
  **manipulation leaves (9):** the `*_observation` / `*_assertion` /
  `*_manipulation` tier (acceleration … volume, term/date/numeric, dose/formulation/
  temperature/pressure/intensity/frequency). One template per data type — the J
  anti-proliferation win.
- **Dimension / composite abstracts (26):** `angle`, `voltage`, `frequency`, `score`,
  `mass`, `zarr`, … (the units the leaves carry).
- **`time_reference` family (7):** `epoch_/event_/session_/utc_` `*_reference`.
- **Subject-side domain (7):** `dose`, `formulation`, `chemical`, `concentration`,
  `amount`, `instrument`, `interaction_purpose`.
- **Binding registry:** `value_set` (D9) — J-native.

† `calculator` is the one *non*-J-native item in this list — a pre-J NDI-app abstract
(see §3/D-C). It is J-native only in the sense that it parents nothing go-forward
once the analysis tier is decomposed; flagged for deletion with the zoo.

## 2. Decided tracks — disposition set, implementation pending (~96)

| Track | classes | Disposition |
|---|---|---|
| **D-A acquisition/session infra** (23) | `daq*`, `syncrule*`, `syncgraph`, `filenavigator`, `epoch*`, `session*`, `dataset*`, `element_epoch`, `oneepoch`, `valid_interval` | keep as infra + governance pass (type deps, declare shapes) |
| **D-B stimulus** (3) | `stimulus_presentation`, `control_stimulus_ids`, `openminds_stimulus`* | bodies-of-record; manipulation minted by NDI 2nd pass |
| **D-C analysis tier** (39) | the `*_calc` / `*_tuning` / `stimulus_response*` zoo **+** the spike-sorting family (`spikewaves`, `spike_clusters`, `vmspike*`, `binnedspikeratevm`, `jrclust_clusters`, `sorting_parameters`, …) | decompose → observations + `data_body` + `derived_from`; grain A; no genus |
| **2.D data-format** (34) | `sampled_/opaque_body`, `dataseries_/timeseries_/imageseries_data`, `expression_matrix_data_*`, `reference_*`, `sequence_read_data_*` | fold under `data_body` (mostly drafted) |

*`openminds_stimulus` is in the retire set (§3), not truly D-B.

## 3. Retire — decided, but still in `stable` ⚠️ (Phase 8)

| Class | Why retired | Migrator | Action |
|---|---|---|---|
| `element` | element dissolved → `subject` + lineage `directed_relation` (D2) | `migrators_j/element.m` ✅ | **delete from `stable/`** |
| `openminds` | openMINDS bundle not stored (J:92) | — | delete |
| `openminds_subject` | → `term_assertion`s on the subject | `migrators_j/openminds_subject.m` ✅ | delete |
| `openminds_element` | element + openMINDS, both retired | — | delete |
| `openminds_stimulus` | openMINDS metadata on a stimulus | — | delete |

These have working migrators (or nothing produces them), so they are **sources**, not
targets — they should not be go-forward classes. Deleting them is the Phase-8 cleanup;
it must run *after* the corpus proves the migrators, and needs the deprecated-tier
source shape retained for input recognition.

## 4. Genuinely open — need a call ❓ (this audit's worklist)

| Class | Shape | Question / proposed disposition |
|---|---|---|
| `neuron_extracellular` | `⊂ base,app`, `element_id` | A neuron **is a subject** in J. Decompose its fields → `term_assertion`s / observations on the neuron-subject? Or is it an analysis-tier (spike-sorting) output? **Needs a call.** |
| `position_metadata`, `distance_metadata` | `element_id` | Measured spatial quantities → `length_`/position `observation`s on the subject. (Was proposed as "1.4 position/distance → observations" — confirm + build.) |
| `probe_location` | `probe_id` | → `term_observation` — migrator exists ✅; confirm done. |
| `electrode_offset_voltage`, `probe_geometry` | `probe_id` | → `voltage_observation` / observation+`data_body`; **needs-NDI** (live NDI writers). |
| `generic_file`, `image`, `image_collection`, `image_zarr`, `ephys_zarr`, `ngrid`, `dataseries_channel_map`, `dataseries_pyramid`, `binaryseries_parameters`, `pyraview`, `filter` | `element_id` (mostly) | data/file representations → `data_body`/`opaque_body` (**2.D-adjacent**), *except* `ngrid`/`*_channel_map`/`filter` which are **index/geometry/DSP config** → keep as infra or ride on a `data_body`. Per-class call needed. |
| `ontology_image` | `element_id` | ontology term + image → `term_observation` + image `data_body` (D10/D11-adjacent). |

## 5. Confirmed infra / meta keep — verified this pass ✅

| Class | Role | Verdict |
|---|---|---|
| `directory` | storage descriptor (`base_uri`, `manifest_format`); referenced by `zarr` | legit **storage infra** — keep (owes D-A governance) |
| `ndi_reserved_keys`, `mock` | meta files (no `document_class`) | keep (schema machinery) |
| `metadata_editor` | app metadata blob | keep (app infra); minor governance |
| `demo_ndi`, `demo_ndi_mock` | recognized `did_v1` source classes + migration-test fixtures | keep (not cruft — load-bearing for tests) |

## Ontology / flat-table family (D10/D11 — separate track)

`ontology_label` (→ `term_observation`, migrator ✅), `ontology_table_row`
(flat-table, knowingly-wrong migrator pending D10/D11), `ontology_image` (§4). These
belong to the D10/D11 column-roles work, tracked in `ndi-next-steps` — noted here for
completeness.

---

## Net worklist coming out of this audit

1. **Phase 8 (concrete now):** delete the 5 retired classes (`element`, openMINDS ×4)
   from `stable/` once the corpus proves their migrators.
2. **Per-class calls (§4):** `neuron_extracellular` (subject vs analysis); the
   data-representation split (which → `data_body` vs kept-as-index/DSP-infra);
   `position_/distance_metadata` → observations (confirm + build).
3. **Governance (D-A):** the infra keeps (`directory`, `metadata_editor`, the DAQ
   family) owe the type-deps / declare-shapes pass.
4. Everything else is J-native (§1) or in a decided track (§2) — no new decision.

*Companion to `V_eta_nonsubject_cohesiveness_plan.md`. This audit closes the "have we
looked at every go-forward class?" question: yes — 258, each dispositioned.*
