# Queries — Griswold 2025 Worked Example

Five questions a researcher might want to ask against this dataset, each traced through the document graph. The resolution steps below are what a query engine or consumer library would have to do.

The goal is to find out where the **query surface is clean** and where it is **awkward or broken** — those failures go into `FINDINGS.md`.

---

## Query 1 — "What species was studied, and was it sex-balanced?"

**Resolution:**

1. Load all `core:SubjectGroup` documents for the dataset → `20_subject_group_control.json`, `21_subject_group_EO1.json`, `22_subject_group_EO2.json`.
2. Read `species` field → resolves to `openminds:species-mustela-putorius-furo` → *Mustela putorius furo* (ferret).
3. Read `biologicalSex` → all three groups: `controlledTerms:BiologicalSex/female`.

**Answer:** Ferret (*Mustela putorius furo*), female only.

**Assessment:** Clean. One field on each group resolves the question immediately. No NDI documents needed.

---

## Query 2 — "For subject EO1-01, what manipulations preceded the terminal recording, in order?"

**Resolution:**

1. Load `30_subject_EO1_01.json`.
2. Read `studiedState` → four state IRIs.
3. For each state, resolve and read `descendedFrom` to build the chain:
   - `P25-pre` → (none)
   - `P25-postopen` → descended from `P25-pre`
   - `P28-postexposure` → descended from `P25-postopen`
   - `P55-terminal` → descended from `P28-postexposure`
4. For each state transition, find the `core:ProtocolExecution` whose `input` is the earlier state and `output` is the later state:
   - `P25-pre` → `P25-postopen`: `protex-eyeopen-EO1-01` (protocol = `premature-eye-opening`)
   - `P25-postopen` → `P28-postexposure`: `protex-exposure-EO1-01` (protocol = `visual-exposure`)
   - `P28-postexposure` → `P55-terminal`: `protex-surgery-EO1-01` (protocol = `terminal-surgery`)
5. Order by `startTime` on each execution.

**Answer:** (1) P25 premature right-eye opening (2024-10-15), (2) P25–P28 unguided visual exposure (2 h/day × 4 days), (3) P55 terminal surgery (2024-11-14).

**Assessment:** Clean but **two-step**: first walk the state chain, then match executions by input/output. Consumers will want a helper that does this in one call. The openMINDS "everything is an Activity with input/output" pattern makes this work, but naive users will not discover it immediately.

---

## Query 3 — "Find all recordings that used a Plexon S probe in monocular V1 of a ferret with ≥28 days post-eye-opening."

**Resolution:**

1. Find all `ephys:ElectrodeArrayUsage` documents whose `device` is `openminds:griswold-device-plexon-s-probe`.
2. For each such usage, read `usedSpecimen` (a `SubjectState`) and `anatomicalLocationOfArray`.
3. Filter by anatomical target = V1 monocular (e.g. contains `openminds:griswold-target-v1-monocular`).
4. For each remaining usage, walk the state chain backwards through `descendedFrom` until reaching a state that is a `ProtocolExecution.output` whose protocol is `premature-eye-opening` or `natural-eye-opening`.
5. Compute the age at recording state minus the age at the eye-opening state. Filter by ≥ 28 days.

**Answer:** (for this example) `51_electrode_array_usage_EO1_01.json` — 30 days post-opening.

**Assessment:** **Awkward.** This works but is a multi-hop query requiring:

- Traversal of the `SubjectState.descendedFrom` chain.
- Identifying which state-transition was "eye opening" vs another manipulation.
- Age arithmetic with unit awareness.

This is the kind of query a neuroscientist would reasonably ask but that our document graph does not make easy. **Finding #1 in FINDINGS.md.**

---

## Query 4 — "For unit-001 in session EO1-01, give me all tuning curves and the derived selectivity indices."

**Resolution:**

1. From session `ndi-session-griswold-EO1-01`, find the `spikesort_output` via `depends_on` → `ndi-spikesort-griswold-EO1-01-session-01`.
2. Verify `unit-001` ∈ `unit_ids`.
3. Find all documents that `depends_on` the spikesort_output and have `classname` in {`stimulus_tuningcurve`, `fit_curve`, `analysis_output`} and reference `unit_id: "unit-001"`.
4. Return them.

**Answer:** 4 tuning curves (ori, dir, SF, TF), 3 fits (Movshon SF, Movshon TF, Naka-Rushton contrast), 1 indices doc.

**Assessment:** Clean. All within the NDI layer. This is the core use case that the existing `stimulus_tuningcurve` / `data/fitcurve` schemas already support.

---

## Query 5 — "What is the across-animal effect of premature eye opening on direction selectivity, and which documents are the evidence?"

**Resolution:**

1. Find all `analysis_output` documents with `method: "linear_mixed_effects"` and a name matching "direction selectivity" → `60_analysis_mixed_effects_direction_selectivity.json`.
2. Read `fixed_effects` → group coefficients with p-values.
3. For provenance, walk `included_subjects`, `included_sessions`, and the per-unit `tuning_curve` documents that would have gone in. (These are implicit, not explicit.)

**Answer:** Control intercept 0.155 (p<1e-11); EO1contra +0.036 (p=0.24, n.s.); EO1ipsi −0.048 (p=0.047, *); EO2 +0.021 (p=0.61, n.s.).

**Assessment:** The *answer* is clean. The **provenance trace is broken**: the analysis doc lists `included_subjects` and `included_sessions` but does *not* enumerate which `tuning_curve` / `analysis_output(indices)` documents were the inputs. A reader cannot recreate the dataset of 1−DCV values from the document graph alone. **Finding #2 in FINDINGS.md.**

---

## Summary of assessment

| Query | Works cleanly? | Issue |
|---|---|---|
| 1. Species, sex | ✅ | — |
| 2. Manipulation timeline | ⚠️ | Requires two-step traversal |
| 3. Probe + anatomy + age filter | ❌ | Multi-hop through state chain; no direct "days post eye opening" field |
| 4. Unit tuning + fits + indices | ✅ | — |
| 5. Across-animal analysis provenance | ❌ | Analysis doc does not enumerate input documents |

Three out of five queries expose friction. The specifics are captured in `FINDINGS.md`.
