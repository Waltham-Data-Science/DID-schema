# V_eta discovery notes — corpus measurements (did_v1 → V_eta)

Grounds the "measure before build" decisions (D3, D6) and the migrator dispatch
tables in **real corpus data**, not guesses. The corpora are public JSON on S3
(`https://ndi-programming-development.s3.us-east-1.amazonaws.com/<NAME>.zip`) —
not in any repo — so this analysis was done directly in Python on the `did_v1`
documents (no MATLAB needed; MATLAB is only for *running* the migrator, via CI).

Corpora analyzed so far: **B** (12,917 docs, 18 classes) and **Dab** (27,561
docs, 26 classes). B is DAQ/ephys infrastructure only; Dab carries the
subject-side hard transforms.

## Class coverage

| corpus | hard-transform sources present | falls through to default `+migrators/` (1→1) |
|---|---|---|
| **B** | *(none)* | subject, element, element_epoch, daqsystem/daqreader*, syncrule*, stimulus_presentation, control_stimulus_ids, session*, filenavigator — all carry over with the `schema_version` tag |
| **Dab** | `treatment` (49), `ontologyTableRow` (6,205), `probe_location` (404), `stimulus_bath` (1,605 — **deferred** to the NDI second pass, as in V_zeta) | openminds_subject/stimulus/element, + the B infrastructure set |

No class in either corpus quarantines: every class is either a `+migrators_j/`
target, a deferred `stimulus_bath`, or a design-neutral fall-through. `treatment_drug`
and `virus_injection` do **not** appear in B or Dab.

## `treatment` (Dab: 49 docs) — one dominant pattern

**All 49 are the "Target Location" edge case** the migration plan flagged:

```
treatment.ontologyName = "EMPTY:0000074"
treatment.name         = "Optogenetic Tetanus Stimulation Target Location"
treatment.numeric_value = []                      (0/49 carry a number)
treatment.string_value = a UBERON CURIE           (49/49 — the attributed locus)
```

So in Dab, `treatment` never dispatches to dose/thermal/procedure — it is
**purely a locus attribution**: the act is optogenetic-tetanus stimulation, and
`string_value` names the targeted region.

- **Dispatch rule (data-grounded):** `name` ends in `"Target Location"` **and**
  `string_value` matches a CURIE ⇒ the act is a `term_manipulation` (variable =
  the stimulation term, name minus the "Target Location" role-suffix), and the
  region is the **locus**.
- **D3 answer — the locus volume is small.** Distinct UBERON terms:
  `UBERON:0001930` (15), `UBERON:0001929` (16), `UBERON:0002034` (18) — 3 regions
  across **49 (subject, region) pairs = 49 loci** (one per subject; no per-subject
  dedup savings, and 0 loci in B). This is the whole attributed-locus volume in
  these corpora. **Conclusion:** the narrow first-pass policy is sufficient —
  *located-by-default* (emit a `term_observation` location value: `variable` = a
  spatial relation like `primary_target`, `value` = the UBERON term) with an
  allowlist to *mint* Path-S part-subjects only where a per-locus biography is
  needed. The full corpus-wide find-or-create/dedup **service is not warranted for
  B/Dab** (49 loci, all distinct subjects). Revisit if a larger corpus (JH) shows
  a high, repeated-per-animal locus volume.

## `ontologyTableRow` (Dab: 6,205 rows, 62 distinct columns)

Two assays, both with `EMPTY:` placeholder `ontologyNodes` (so dispatch is by the
**value type**, not the ontology branch — real term mapping is a curation
follow-up):

- **Fear-potentiated / acoustic-startle** (~6,160 rows): `ExperimentalTrialNumber`,
  `…TrialTypeIdentifier`, `…ApparatusChamberIdentifier`, `…NumberOfSamples`,
  `…SamplingRate`, `…StartleWindowOnsetAmplitude`, `…MaximumAmplitude`,
  `…TimeToMaximumAmplitude`, `…AverageAmplitude`, `ExperimentTrialExecutionTimestamp`,
  `…ExperimentalPhaseOrTestName`, `ExperimentalGroupCode`, `SubjectLocalIdentifier`.
- **Elevated Plus Maze** (~45 rows): the ~40-column EPM assay the plan predicted —
  `OpenArm{North,South,Total}` × `{Entries, HeadEntries, Time, LatencyToFirstEntry,
  TimeMovingTowards, PercentTime}`.

**Shape dispatch (from the actual `data` values):**

| value seen | → V_eta leaf | note |
|---|---|---|
| `int` count (trial #, NumberOfSamples, Entries) | `count_observation` | |
| `int` rate (SamplingRate = 1000) | `frequency_observation` | |
| `int` amplitude (Max/Average/Onset) | `voltage_`/`intensity_observation` | a.u.; **needs a dimensionless/intensity type** (see gap below) |
| `int`/elapsed (TimeToMaximumAmplitude, EPM Time/Latency) | `duration_observation` | |
| `%` (EPM PercentTime) | `score_observation` | bounded scale |
| `str` label (TrialType, PhaseOrTestName) | `term_observation` | timed classification |
| `str` timestamp (`8/19/2022 9:22:39 AM`) | `date_assertion` | parse to ISO-8601; timeless per-trial |
| `str` `SubjectLocalIdentifier` | *skip* | identity, already the subject |
| `int` `ExperimentalGroupCode` | `term_assertion` (or a group relation) | timeless group membership |

Most FPS/EPM columns are per-trial **measurements ⇒ `subject_observation`**;
the timeless ones (`SubjectLocalIdentifier` skip, `ExperimentalGroupCode`,
timestamp) are the `subject_assertion` side (C.2). A single row therefore fans out
to ~13 (FPS) or ~40 (EPM) documents + one shared anchor.

## `probe_location` (Dab: 404) — D5

```
probe_location = { ontology_name: "UBERON:0001880", name: "bed nucleus of stria terminalis (BNST)" }
depends_on: probe_id
```
→ a `term_observation` about the probe(-subject): `variable` = a spatial relation
(`location`), `value` = the collapsed `{node, name}` term, + a synthesized anchor
(D5). 404 of them — the largest D5 volume.

## Consequences for the build

- **D3 — resolved by measurement:** located-by-default + a mint allowlist; no
  standing dedup service for B/Dab. (Confirm against JH before locking.)
- **D6 — the exercised relation set is even smaller than expected:** in B/Dab the
  migration mints **no** `directed_relation` from `treatment`/`ontology_table_row`
  under located-by-default (loci become `term_observation` values, not
  part-subjects); the only provenance relation is `treatment_transfer`, which is
  **absent** from B/Dab. So `part_of`/provenance relations are exercised only if
  the mint allowlist fires or JH carries transfers — declare the minimum, wire on
  demand.
- **A real gap surfaced — now closed.** The startle **amplitude** columns are
  dimensionless (a.u.), and the meta-schema had no dimensionless numeric type.
  Per Brainstorm J §7 (`intensity` = "the one dimensionless numeric"), V_eta now
  ships an **`intensity`** type in the meta-schema enum plus `intensity`,
  `intensity_observation`, `intensity_manipulation`, and `intensity_assertion`
  — so the FPS amplitudes migrate to `intensity_observation`.
- **Migrators needed for full Dab coverage:** `treatment` (the Target-Location
  pattern), `ontology_table_row` (int/str/date shape dispatch), `probe_location`
  (D5); `stimulus_bath` deferral; everything else falls through. `subject_group`
  and `treatment_transfer` (already implemented) are not exercised by B/Dab.

*Method: `did_v1` JSON downloaded from the public S3 corpus prefix and analyzed in
Python. The MATLAB migrator + `Validate=true` end-to-end run is validated in CI;
this analysis grounds its dispatch tables in the real data.*
