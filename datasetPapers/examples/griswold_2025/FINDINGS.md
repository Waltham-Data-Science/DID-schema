# Findings — Griswold 2025 Worked Example

This report captures what was awkward, what was missing, and what should change before writing any NDI schemas. Scored against the user-facing criteria: **flexible, standardized, easy to create, easy to search, intuitive**.

---

## Summary scorecard

| Criterion | Verdict | Notes |
|---|---|---|
| **Flexible** | ✅ Strong | The openMINDS `customPropertySet` escape hatch plus `stimulation:Stimulus.specification` handled every per-paradigm parameter without schema gymnastics. |
| **Standardized** | ⚠️ Mixed | 90 % of fields mapped to existing openMINDS types or controlled terms, but the factorial-stimulus pattern and sample-aligned epochs have no obvious openMINDS home and had to be NDI-native. |
| **Easy to create** | ❌ Not yet | ~28 openMINDS + ~16 NDI documents for one session of one subject. No researcher will author this by hand. Templates + a helper tool are needed. |
| **Easy to search** | ⚠️ Mixed | Simple per-document queries resolve cleanly (Queries 1, 4). Multi-hop queries through the provenance DAG (Queries 2, 3, 5) require careful walking. |
| **Intuitive** | ⚠️ Mixed | openMINDS's protocol/execution and subject/state patterns are conceptually clean but unfamiliar. A reader new to openMINDS needs about 15 minutes of orientation before the file tree makes sense. |

---

## Concrete findings (ordered by severity)

### F1 — Multi-hop queries through the state chain are awkward (severe)

**Evidence:** Query 3 (`find recordings ≥28 days post eye opening`) required four join steps: `ElectrodeArrayUsage` → `SubjectState` → walk `descendedFrom` → identify eye-opening `ProtocolExecution` → age arithmetic.

**Implication:** For any question that spans more than one openMINDS entity, naïve implementations will be slow and bug-prone. This is *not* a flaw in openMINDS — PROV-style DAGs always have this shape — but it does mean NDI consumer tooling must provide:

- A `walk_state_chain(subject)` helper that returns states in order with their associated protocol executions.
- A `days_since(subject_state, event_type)` helper for age arithmetic.
- A cached "materialized view" of flattened per-session metadata for common query patterns.

**Recommendation:** Before writing schemas, prototype a tiny query helper (Python or MATLAB, ~200 lines) that answers all five queries against the worked example. If the helper can't keep them under 20 lines each, either the graph shape is wrong or the helper API is wrong.

### F2 — Analysis provenance is under-specified (severe)

**Evidence:** Query 5 could not trace which individual tuning-curve documents fed into the mixed-effects analysis. The analysis doc lists `included_subjects` and `included_sessions`, but not the unit-level input documents.

**Implication:** Reproducibility breaks. If someone wants to re-run the mixed-effects fit on a filtered subset of units (e.g. excluding low-SNR ones) they can't, because the original input set isn't enumerated.

**Recommendation:** The `analysis_output` schema should require an explicit `inputs[]` list of document IDs (or a query spec that resolves to a stable ID list). For Griswold, the analysis doc would reference ~600 `analysis_output(indices)` documents — one per unit across all animals. That's a lot, but it's the correct structure.

### F3 — No home for factorial stimulus design in openMINDS (moderate)

**Evidence:** Stimulus Set 1 is an 8×4×6 = 192-cell factorial with shared blank control. openMINDS's `stimulation:Stimulus` is one-stimulus-per-document. We handled this by making an NDI-native `factor_design` doc plus one openMINDS `Stimulus` per *example* cell — but fully representing the experiment would need 192 `Stimulus` documents for Set 1 alone.

**Implication:** Authoring 192 near-identical openMINDS documents is prohibitive. Either (a) the factorial is represented entirely NDI-side with no openMINDS individual-stimulus documents (but then openMINDS-level search loses stimulus-level granularity), or (b) we propose a `stimulation:StimulusFactorDesign` upstream contribution.

**Recommendation:** For now, keep the factorial in NDI and reference each `StimulationActivity` → one `factor_design` via `customPropertySet.factorDesignRef` (as demonstrated). Consider an upstream contribution to openMINDS later.

### F4 — "Placement" vs "ElectrodeArrayUsage" — the openMINDS pattern is awkward for chronic/longitudinal studies (moderate)

**Evidence:** In Griswold the probe is used in one terminal session, so `ElectrodeArrayUsage` trivially spans one session. In Reikersdorfer (the carbon-fiber MEA paper), the same probe is chronically implanted for 11 months and records across hundreds of sessions. openMINDS's `DeviceUsage` has no explicit longitudinal model.

**Implication:** Not a problem for Griswold specifically, but when we do the Bhar stress-test example (or a hypothetical chronic example) we'll need to decide: one `ElectrodeArrayUsage` per session, or one persistent `ElectrodeArrayUsage` with many sessions pointing at it?

**Recommendation:** Defer to the Bhar / Reikersdorfer analysis. Flag this for the cyclic/longitudinal findings.

### F5 — Controlled terms that don't yet exist (moderate)

**Evidence:** The documents reference `controlledTerms:SubjectAttribute/eyes-closed`, `/one-eye-open-right`, `/anesthetized`, `/paralyzed`, `/artificially-ventilated`, `controlledTerms:VisualStimulusType/ambient-scene`, `controlledTerms:Technique/forceps-dissection`, `/receptive-field-mapping`, and `controlledTerms:UnitOfMeasurement/postnatal-day`. Not all of these exist in the openMINDS controlled-term instance sets.

**Implication:** For the worked example these are annotations-that-aspire-to-be-standard. For a real deployment, the project needs a policy: (a) submit missing terms upstream and wait, (b) fork controlledTerms locally, or (c) fall back to free text with ontology-IRI hints.

**Recommendation:** Adopt policy (a) as the default, with (c) as the transitional fallback. Keep a running list (this paper alone generated 10+ candidate terms).

### F6 — Time representation is inconsistent (moderate)

**Evidence:** openMINDS `Activity.startTime` / `endTime` are wall-clock ISO 8601. NDI `epoch.sample_range` is sample-indexed. NDI `session.date` is a calendar date. NDI `recording.duration_seconds` is a float. There is no single normalised time axis.

**Implication:** A query like "what happened in the recording at wall-clock 14:15:00" requires the consumer to compose `session.date` + offset-from-start. A query "what was the subject state at sample 7575000" requires resolving recording_start wall clock → sample 0.

**Recommendation:** The NDI `recording` doc should carry an explicit `start_time_utc` field aligned to sample 0, and the NDI `epoch` should be both `sample_range` and `wall_clock_range` (computed). This is probably a small additional field rather than a new schema.

### F7 — The openMINDS → NDI link direction is one-way (minor)

**Evidence:** NDI documents reference openMINDS instances by IRI. openMINDS documents do not reference NDI documents. This means given only an openMINDS `SubjectState`, you cannot discover which NDI `session`s used it without an external index.

**Implication:** A reverse index must be maintained outside either schema. For NDI Cloud this is a cloud-level concern, not a schema concern, but it should be called out.

**Recommendation:** NDI Cloud (or the consumer library) builds and maintains the reverse index. Do not try to solve this at the schema level.

### F8 — Filenames do not help the reader understand document relationships (minor)

**Evidence:** The numbered prefixes (`01_`, `10_`, `30_`) in both folders are only a human convenience. There's no machine-readable ordering or grouping.

**Implication:** Readers lean on the filenames for orientation; without them, finding a specific document in a flat directory of 40+ files is hard.

**Recommendation:** For archival deposits, keep the flat structure but also emit a `MANIFEST.json` that indexes all documents by classname, subject, session, and timestamp. Not a schema issue.

### F9 — Easy-to-create will require a template engine (minor)

**Evidence:** Looking at the 28 openMINDS documents, maybe 60 % of the content is boilerplate that could be auto-filled from a handful of paradigm-level inputs ("this is an in-vivo visual ephys experiment, ferret, Brandeis lab, published in eLife 2025, three-group design"). Researchers should not be hand-typing these.

**Recommendation:** A future CLI like `ndi new experiment --from-template visual-ephys-vertebrate` is the right shape. Scope for a later iteration — not needed before the schemas are agreed.

---

## What to change in the synthesis doc

Based on these findings, two amendments to `datasetPapers/summaries/00_schema_design_synthesis.md`:

1. **Open question #3 (how much should `analysis_output` be schema-constrained)** — Finding F2 says: require an `inputs[]` list of document IDs. This is the minimum for reproducibility.
2. **New open question:** What helper API does a consumer library need to expose so that typical researcher questions (Queries 1–5) take <20 lines to answer? This is not a schema question per se, but the schema shape constrains what's possible.

---

## What changes the Bhar example will likely expose that this one did not

Based on what Bhar has that Griswold doesn't:

- **Populational subjects** — `SubjectGroup` / `SubjectGroupState` should handle this, but the Bhar exchange assay (naïve worms transferred onto plates that held trained worms) is a cross-group provenance pattern we haven't tested.
- **Cyclic protocols** — the `Protocol.steps` + `depends_on` composition design from the synthesis doc needs to be actually rendered.
- **Substrate-as-measured-object** — the plate carries LC-MS observations that have no subject attached. Will require either `core:TissueSample` (awkward) or a new NDI-native `substrate` doc.
- **No data deposit** — "data availability: contact the authors" maps to what `core:UsageAgreement` in openMINDS; we didn't test this.
- **Cross-species exchange** — a single plate holds a history involving both *C. elegans* and *C. briggsae*, which is an inherently cross-reference provenance pattern.

If Bhar can be expressed cleanly with no more than one new NDI document type and no more than three new findings of F1/F2 severity, the overall design is validated. If it cannot, iterate.
