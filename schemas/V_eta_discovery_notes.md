# V_eta discovery notes — corpus measurements (did_v1 → V_eta)

Grounds the "measure before build" decisions (D3, D6) and the migrator dispatch
tables in **real corpus data**, not guesses. The corpora are public JSON on S3
(`https://ndi-programming-development.s3.us-east-1.amazonaws.com/<NAME>.zip`) —
not in any repo — so this analysis was done directly in Python on the `did_v1`
documents (no MATLAB needed; MATLAB is only for *running* the migrator, via CI).

Corpora analyzed: **B** (12,917 docs), **Dab** (27,561 docs), and **JH** (78,688
docs, 15 classes). B is DAQ/ephys infrastructure only; Dab and JH carry the
subject-side hard transforms at volume.

## JH (78,688 docs) — the largest, and it confirms/extends the picture

| class | n | migration |
|---|---|---|
| `ontologyTableRow` | **41,095** | the bulk — a *C. elegans* bacterial-encounter behavioral assay |
| `openminds_subject` | 9,032 | default fall-through |
| `ontologyLabel` | **7,007** | → `term_observation` (D5) — high volume |
| `imageStack` | **7,007** | → `data_body`/`subject_observation` (the storage case; increment 3) |
| `element`/`element_epoch` | 4,156 ea | carried (NDI infra) |
| `subject_group` | **353** | → bare `subject` (the migrator I implemented **is** exercised here) |
| `treatment` | 56 | food-restriction **onset/offset times** (a husbandry regime + time), `EMPTY:` nodes, **0 loci, 0 numeric_value** |

- **D3 confirmed at scale:** JH has **0** anatomical loci. Total across B+Dab+JH =
  **49** (all Dab optogenetic). Located-by-default is firmly the right call.
- **`treatment_drug` / `virus_injection` / `treatment_transfer` are absent from
  all three corpora** — those `+migrators_j/` migrators are unexercised; keep the
  classes, deprioritize the migrators.
- **`treatment` has two real patterns, no substances/thermal:** Dab = the
  Target-Location locus; JH = a husbandry regime (food restriction) with an
  onset/offset time → `term_manipulation` (variable = "food restriction") + a
  bounded time anchor. The dose/`<quantity>`_manipulation branches of the plan's
  dispatch table are **not** exercised by these corpora.
- **New numeric-type gaps (JH C. elegans):** velocities and decelerations
  (`velocity`, `acceleration`), plus radii (`length`), probabilities/circularity
  (`score`), bacterial density (`concentration`/`intensity`). See "gap" below.

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
- **Numeric-type gaps surfaced — now closed.** V_zeta seeded only 12 dimensioned
  numerics; discovery showed that is insufficient (Dab a.u. amplitudes; JH
  velocities/decelerations), and Brainstorm J §7 prescribes a *comprehensive*
  pre-seeded set anyway. V_eta now ships J §7's fuller set — added `intensity`,
  `velocity`, `acceleration`, `area`, `angle`, `angular_velocity`, `force`,
  `energy`, `power`, `charge`, `resistance`, `conductance`, `capacitance`,
  `amount`, `ph` (each with a value mixin + `_observation` + `_assertion` leaf;
  `intensity` also gets a `_manipulation`). So the FPS amplitudes →
  `intensity_observation` and the C. elegans velocities → `velocity_observation`.
- **Migrators needed for full Dab coverage:** `treatment` (the Target-Location
  pattern), `ontology_table_row` (int/str/date shape dispatch), `probe_location`
  (D5); `stimulus_bath` deferral; everything else falls through. `subject_group`
  and `treatment_transfer` (already implemented) are not exercised by B/Dab.

## The 11 ontology_table_row tables — column roles (grounds D10)

Grouping every `ontology_table_row` across the corpora by its column signature
gives **11 distinct tables**. They are NOT bags of subject facts — each is a
mini-record, and columns play four roles (**M** measurement · **Q** qualifier ·
**R** reference/foreign-key · **I** identity):

| rows | table | measured entity | role mix |
|---|---|---|---|
| 20,411 | JH *C. elegans* encounter (onset/offset, velocities, deceleration, exploit/sense probabilities, bacteria density) | the **worm** (behavior) + the encounter event | M responses + **R** `BacterialPatchDocumentIdentifier` + I |
| 7,204 | JH bacterial-patch fluorescence (radius, circularity, border/mean/center intensity + amplitudes, ratio) | the **bacterial patch** (not the worm!) | M + R image/patch ids |
| 6,206 | JH bacterial-patch geometry (OD600 target, volume, centre X/Y, radius, circularity) | the **patch** | M + R plate/patch ids |
| 6,160 | Dab fear-potentiated startle (onset/max/avg amplitude, time-to-max) | the **rat** (startle response) | M responses + **Q** trial type / chamber / phase / group / rate / #samples / timestamp + I |
| 3,312 | JH subject↔plate | — | **pure relation** (no measurements) |
| 1,656 | JH subject identity (identifier / local id / doc id) | — | **pure identity** |
| 1,521 | JH plate/image growth (growth duration, exposure time) | plate / image | M + R |
| 597 · 100 · 88 | JH plate-prep / session conditions (OD600, CFU, ambient temp/humidity, growth durations, dev stage, peptone/exclusion flags, seeding/storage timestamps) | **plate / session / environment** | mostly **Q** conditions + a few M (OD600, CFU, ambient) |
| 45 | Dab elevated plus maze — **51 columns** (per-arm entries / head-entries / time / %time / latency / time-moving / time-freezing for N/S/W/E/centre/totals) | the **rat** (behavior) | M responses + **Q** test id / **CNO-vs-saline treatment** / test duration / group / exclusion + I |

Takeaways that drive D10 (and a likely D11):
- **Qualifiers are pervasive** (trial type, phase, chamber, CNO/saline, exclusion
  flag, OD600, ambient temp) and are conditions *of* a measurement, not facts about
  the subject.
- **The measured entity is frequently not the animal** — 13k+ rows measure a
  *bacterial patch*; the plate-prep tables measure a *plate/session/environment*.
- **Two tables are pure relations / identity** and produce **no** observations.
- So the migrator needs a **column-role classifier** (M/Q/R/I) and **per-table
  subject resolution**, both discovery-tuned — the naive per-column→observation
  split (current `+migrators_j/ontology_table_row.m`) is wrong for most tables and
  will be revised once D10/D11 land.

## `imageStack` → `image_observation` + `sampled_body` (JH: 7,007 docs)

Grounded in the real JH `imageStack` docs. Each is `{label, formatOntology}` +
an `imageStack_parameters` mixin (dimension_order/size/scale, data_type,
clocktype, timestamp) + a `document_id` dependency, with **`subject_id` empty**.
The correct J mapping (only partly implementable per-document; the rest is a
second-pass join):

| source field | is | disposition |
|---|---|---|
| `formatOntology` (e.g. `NCIT:C85437`) | the **file type** (TIFF/MP4-like) | **dropped** — a container format is derivable from the stored bytes (and the short form already rides on `image.image_format`); an ontology term for it is a redundant projection |
| `label` (84–352 char prose) | the **definition** of the variable's ontology term | **dropped** — reconstructable as a projection; it is a description, not a name (1,299/6,000 exceed the 256 name cap) |
| `imageStack_parameters` | geometry/clock/dtype | `image` mixin + `sampled_body` (datum/sample_time) |
| files | the pixel bytes | `sampled_body` body_data |

**Two pieces need a second-pass cross-document join (deferred to discovery
curation), because the per-document migrator sees only one doc:**

- **`variable`** (the observed quantity) is the **linked `ontologyLabel`** — the
  image's `document_id` resolves to an `ontologyTableRow`/`ontologyLabel` whose
  `ontologyNode` is the "what". The per-doc migrator emits a non-empty
  **placeholder** (`{name: "image"}`) so the statement validates; the second pass
  replaces it with the label's term.
- **`subject`** should be the **plate or bacterial patch** the image depicts.
  `subject_id` is empty on the source; the subject is reachable only via
  `image.document_id → ontologyTableRow → BacterialPlate/PatchIdentifier` (a
  **local** id string), so it needs the local-id → subject-document mapping **and**
  minted **plate** subjects (the patch-geometry map already mints patch subjects;
  plate subjects are not minted yet). Until then the image_observation carries an
  empty `subject_id` (unattributed — the F1 pattern).

*Method: `did_v1` JSON downloaded from the public S3 corpus prefix and analyzed in
Python. The MATLAB migrator + `Validate=true` end-to-end run is validated in CI;
this analysis grounds its dispatch tables in the real data.*
