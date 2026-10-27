# V_eta Go-Forward Class Audit — J-cohesiveness of every live class

> **Vocabulary note (2026-10-21):** this document predates the one-entity schema
> (`V_eta_entity_composition_plan.md`, signed 2026-10-08) and uses its old names:
> `subject_statement` is now `statement`, `subject_id` is `entity_id`, `data_type` is
> `value`, and the separate entity classes (`subject`, `dataset`, `software`, ...) are one
> `entity` with a `type`. Its decisions stand under the new names.

TEAM-SIGN-OFF [misc singletons]: jess, 2026-08-09 -- `binaryseries_parameters` folds into the data_body model and is retired (its `time_type` is the time axis's new `datum_type`, its `data_type` the statement's, `data_dim` the axis count, `samples_regular_intervals` the axis `regular` flag); `interaction_purpose` is KEPT, conditionally on the stimulus build actually emitting it, and is the destination for the 635 `StimulationApproach` documents via a second pass -- so #71 is repaired by re-targeting, with pass 1 emitting nothing; `projectvar` stays a deprecated passthrough until real documents exist to model its untyped `data` field against. Whether `purpose` collapses to a field on `subject_interaction` stays open pending the corpus measurement.

> **This line is TAGGED `[misc singletons]` deliberately.** Three families cite this
> document — `dataseries_channel_map`, `subject measurement` and `misc singletons` — and an
> untagged marker would have signed all three at once. That is a hole the board's own
> checker closes, and it is why the tag is not optional here.
>
> **FIFTH TRANSCRIPTION.** Claude wrote this line on explicit instruction ("I accept the
> proposal and sign off on these 3 classes"), 2026-08-09. The standing request that the
> team type these itself is now three sittings old.

*The go-forward V_eta schema = `stable/` + `draft/`. **258** classes. This audit gives
**every** one a J-disposition so the whole set can be reviewed for Brainstorm-J
cohesiveness — not just the families touched piecemeal (D-A…D-E).*

> **CORRECTED 2026-08-10 — that parenthesis conflated the MODEL with the VALIDATION SET,
> and CI inherited the conflation.** The go-forward MODEL is `stable/` + `draft/`, which is
> what this audit is about. But `DID_SCHEMA_PATH` is what documents are VALIDATED against,
> and it now assembles all THREE tiers. `deprecated/` holds exactly the v1 shapes that
> deliberately pass through unmodelled — `projectvar`, `stimulus_parameter_table`,
> `image_stack` + `_parameters` — and a passthrough the validator cannot see QUARANTINES,
> which is the opposite of preserving it. Three of the four had never appeared in a tested
> corpus, so the defect never fired until the `image_stack` guard turned 4,563 JH documents
> into passthroughs: corpus run 31421715133 reported `No schema file for class
> "image_stack"` for every one. All six DID-matlab workflows now copy the tier.
> The original parenthesis said the tiers "CI assembles into `DID_SCHEMA_PATH`"; that is
> the sentence that was wrong, and it is removed rather than left standing above its own
> correction.

> **⚠️ STALE point-in-time snapshot (hand-maintained).** The class count (**258**) and several
> dispositions predate the post-J builds — the current build is ~200 classes; use the generated
> **`V_eta_final_class_set.md`** for the authoritative set. Known-stale entries: the D-C
> "calc/`*_tuning` zoo → observations + `data_body`, no genus" position was REVERSED —
> calculators are kept as id-preserved `subject_calculation` LEAFS (a `subject_calculation`
> direction was added), and the 6 tuning composites COLLAPSED to `tuning_curve` /
> `tuning_curve_calculation` (T10/R2/R3); the D-B `stimulus_presentation` model → `timed_sequence`;
> `app` → `software` (R1); `instrument` RETIRED; `zarr` is a storage format ⊂ `base` (not a
> dimension abstract); `value_set` was dropped (absent from disk).

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
| `ndi_reserved_keys` | meta file (no `document_class`) | keep (schema machinery) |
| `mock` | bare `ismock` test-flag `document_class` | ~~keep~~ **DROPPED** — test-only scaffolding, nothing constructs it; a production go-forward schema should not carry a "this is fake" class |
| `metadata_editor` | app metadata blob (the NDIMetaDataEditorApp `metadata_structure`) | **decomposed** → `dataset` + `person`/`organization`/`award`/`publication`/`web_resource` entities + `directed_relation`s (`migrators_j/metadata_editor.m`). Kept as the SOURCE class (Phase-8 deletion deferred, same as `element`/openMINDS) |
| `demo_ndi`, `demo_ndi_mock` | recognized `did_v1` source classes + migration-test fixtures | keep (not cruft — load-bearing for tests) |

**Entity model (new go-forward genus, §1-adjacent):** `entity` (abstract) roots the
referenceable-identity classes — `subject`, `person`, `organization`, `publication`,
`award`, `dataset`, `web_resource` — each carrying a `global_identifier[]`
{scheme, value} (ORCID/ROR/DOI/PMID/PMCID/RRID/UDI/URL). All cross-entity
relationships (authorship, funding, citation, affiliation, documentation) are
`directed_relation`s generalized to `entity ↔ entity`, distinguished by the relation
term. `subject_relation` was renamed `relation`; `value_set` was dropped (redundant
with the binding registry).

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

---

# FOUR SMALL DISPOSITIONS — team, 2026-08-05

**The team's words:** *"I agree with the 4 proposals."* **TWO of the four now carry
a signature, in this section**: `TEAM-SIGN-OFF [dataseries_channel_map]` (2026-08-06,
under proposal 1) and `TEAM-SIGN-OFF [subject measurement]` (2026-08-06, under
proposal 4). The other two need none — proposal 2 (`directory`) established that the
class is not a did_v1 source at all, so there was no disposition to sign, and
proposal 3 (`demo_ndi`) was REVERSED to passthrough before any signature.

<!-- HISTORICAL-SIGNOFF-CLAIM -->
*This line read "NO `TEAM-SIGN-OFF` LINE" until 2026-08-10, which was true when
written and false afterwards. Stated per-proposal rather than for the section,
because a blanket claim in either direction is what made it wrong.*

**Three of the four turned out not to be migration questions at all.** They were on
the board as "needs a writer check before any disposition"; the check showed they
are not did_v1 sources, so the question was mis-framed rather than open.

## 1. `dataseries_channel_map` — DELETE

```
NDI origin/main templates:  0        NDI code mentions:  0
provenance:                 V_epsilon, draft
DID migrators referencing:  0        V_eta schemas referencing:  0
```

Not a did_v1 source. Nothing emits it, nothing consumes it, it has never validated
a document. **Identical shape to `openminds_import`**, which was removed on the same
grounds.

## 2. `directory` — NOT A SOURCE. The question was mis-framed.

```
NDI origin/main:            ABSENT   provenance:  V_gamma, stable
DID migrators referencing:  7        V_eta schemas referencing:  3
```

It is **load-bearing on the DID side** — 7 migrators and 3 schemas use it — and
`CLAUDE.md` already says so:

> Do NOT add post-v1 DID intermediate/target classes (zarr, **directory**,
> `*_observation`, data_body, openminds_import) to the v1 side

So it was never a migration source and needed no writer check. It landed in the
"file navigation" family by name association — the same mis-grouping that once put
`filter` there.

**Consequence: the `file navigation` family CLOSES.** `filenavigator` was already
decided (`V_eta_daq_family_decisions.md` — `file_navigator ⊂ base`, `base.id`
preserved, patterns parsed into declared fields, `software_id` edge), and the family
was held open only by `directory`.

TEAM-SIGN-OFF [dataseries_channel_map]: jess, 2026-08-06 -- dataseries_channel_map is DELETED. It is a V_epsilon draft with no NDI template, no writer, no migrator and no referent; it has never validated a document.

*(Transcribed by Claude on the team's explicit instruction -- "Record dataseries_channel_map deletion as signed-off" -- the same way the openMINDS sign-off is recorded. The line is TAGGED with its family because this document is cited by four of them; an untagged line here would sign all four.)*

## 3. `demo_ndi` / `demo_ndi_mock` — ~~DELETE~~ **REVERSED 2026-08-06 → PASSTHROUGH**

**The DELETE call below was WRONG ON BOTH OF ITS FACTS. It is struck through rather
than deleted, because how it went wrong is the reusable part.**

```
~~NDI origin/main:            0 / 0    provenance:  V_gamma, stable~~
~~DID migrators referencing:  0 / 0    V_eta schemas referencing:  0 / 0~~
~~DID-side test fixtures that nothing references — not even the test suite.~~
```

### What is actually true

```
NDI origin/main templates                  BOTH SHIPPED
   src/ndi/ndi_common/database_documents/demoNDI.json
   src/ndi/ndi_common/database_documents/mock/demoNDIMock.json

demoNDI ⊂ base    value char    FILE: filename1.ext
demoNDIMock       inherits demoNDI, and therefore its required file

REFERENCED at 12+ sites, including a live calculator example:
   +ndi/+calc/+example/simple.m:100  ndi.query('demoNDI.value','exact_number',5,'')
                              :107   ndi.document('demoNDIMock','demoNDI',...)
                              :120, :126, :157
   +ndi/+test/+database/test_ndi_document.m:26, :33
```

### Why the original was wrong — the grep could not have matched

The DELETE evidence searched for the **snake_case V_eta name `demo_ndi`** against NDI,
where the class is spelled **camelCase `demoNDI`**. Zero hits was a property of the
query, not of the repository. This is the failure named verbatim in the operating
rules: *"a grep that could not have matched was reported as 'this does not exist
anywhere'."* Same shape as the `daqsystem` / `epochid` near-misses, one layer down: the
name, not the id.

### The cited test proves the OPPOSITE

`tests/+did2/+unittest/testConvertV1ToV2.m`, in
`testUniversalRenamesRenameClassNamesFalse...`:

```matlab
out = did2.convert.universalRenames(v1, 'RenameClassNames', false);
verifyEqual(testCase, out.document_class.class_name, 'demoNDI');
verifyFalse(testCase, isfield(out, 'demo_ndi'));
```

`demo_ndi` is absent **because the rename was switched OFF**. It asserts that camelCase
survives when renaming is disabled — it is not a drop-safety proof. Its own comment
says so: *"their on-disk schemas still spell classnames in camelCase (e.g., demoNDI)
and the legacy v1 validator compares the strings by exact match."*

### And this document contradicted itself

Line 110 of this same audit already said *"recognized `did_v1` source classes +
migration-test fixtures | keep (not cruft — load-bearing for tests)"*. Two sections,
opposite calls, and the later one shipped to the board.

### DISPOSITION -- REVISED AGAIN 2026-08-06: THREE CLASSES COLLAPSE TO ONE

**The team's words:** *"Let's do B."*

Repairing the family for passthrough exposed that `demo_ndi_mock` has **no fields of
its own**. Its entire content is *"I am a mock demo"* — a FLAG, not a kind of thing.
That is the same test the time-reference collapse turned on: `mode` was cardinality,
not a class axis. A mock `voltage_observation` would still be a voltage observation, so
mock-ness is a property of a document, not a species of one.

```
demo ⊂ base                                  BUILT, persists
   value    double     typed from the WRITER (template says char; simple.m sets 5/10
                       and queries with exact_number)
   is_mock  boolean    default false -- was `mock.ismock`, held as a superclass
   FILE: filename1.ext                       RESTORED; V_eta had dropped it

mock, demo_ndi, demo_ndi_mock                CEASE TO EXIST
```

`demo`, not `demo_ndi`: the framework's own name has no business inside a class name in
the framework's own schema (T13).

**The two costs, recorded rather than glossed.** `ndi.calc.example.simple` queries
`ndi.query('','isa','demoNDIMock','')` — that `isa` has no target once the class is
gone; a v1-runtime query against v1 documents, the same category as every other rename,
but a real break. And `mock` stops being available as a marker other classes could
carry; it had ONE bearer in 91 templates, so a general marker for one user was the
anticipatory error made twice already.

**OPEN, and the team's to settle:** whether mock documents should be REFUSED at
migration rather than carried flagged. Carrying them flagged is what is built. Refusing
them loudly is defensible. Refusing them silently is what V_eta was doing by accident.
If they are to be carried, the flag arguably belongs on `base` so ANY document is
checkable — not built that way for one bearer today.

---

The passthrough reasoning that led here is kept below, because the reversal chain is the
useful part.

**PASSTHROUGH**, agreeing with `V_eta_tenet_audit.md`'s re-audit, which reached this
independently and was right. A corpus 0-document check is still required before any
future drop — absence from the five corpora we test is not absence.

TEAM-SIGN-OFF [subject measurement]: jess, 2026-08-06 -- subjectmeasurement routes through the existing `measurement` fold with NO new class: subject_id carries over, `measurement` becomes the statement's `variable`, `value` becomes the value, and `datestamp` becomes the statement's TIME ANCHOR (time_reference_1 -> absolute_reference), NOT a field. Known gap, signed with: `value` carries no unit, so the typed leaf must be chosen through the D9 registry rather than from the template.

*(Transcribed by Claude on the team's explicit instruction -- "Sign both". TAGGED because this document is cited by three families.)*

## 4. `subjectmeasurement` — route through the `measurement` fold

A REAL did_v1 template:

```json
subjectmeasurement  ⊂ base   dep: subject_id
  { measurement: "", value: "", datestamp: "" }
```

Its shape is a subject observation outright, and the existing `measurement` fold is
the right route — `measurement`'s migrator plus a `subjectmeasurement` tombstone both
landed under TaskList #41. **No new class.**

### CORRECTED 2026-08-06 — `datestamp` is a TIME ANCHOR, not a field

The line above used to read *"`variable` + value + date"*, treating `datestamp` as a
third field. **That was wrong, and it would have dropped the measurement time.** The
team caught it: *"Why does it say datestamp? Shouldn't that be a time reference?"*

```
build_intan_flat_exp.m:62-66  and three test builders, identically:
   'subjectmeasurement.measurement','age',
   'subjectmeasurement.value',30,
   'subjectmeasurement.datestamp','2017-03-17T19:53:57.066Z'

NDI base.json:  "datestamp": "2018-12-05T18:36:47.241Z"   <- EVERY document has one
```

`datestamp` is a full ISO-8601 UTC **instant**, and `base` already carries the
record-creation stamp — so this is a SECOND timestamp, supplied by the caller, saying
**when the measurement was taken**. In J that is the statement's time anchor.
`subject_interaction` already REQUIRES `time_reference_#`, so the slot exists.

```
subjectmeasurement                     ->  <quantity>_observation (leaf keyed by `measurement` via D9)
   subject_id                              subject_id
   measurement  "age"                      variable
   value        30                         value
   datestamp    "2017-03-17T19:53:57.066Z" time_reference_1 -> absolute_reference
                                              value.start_utc    the instant
                                              value.source_start the string as written
```

**And it exposes a gap in the `measurement` fold itself: `measurement` has NO datestamp
field** (`ontologyName`, `name`, `numeric_value`, `string_value` only). Folding
`subjectmeasurement` into it *as a field mapping* would have lost the measurement time
outright. Routing the instant to `time_reference_#` is what makes the fold lossless.

This is also the **first real consumer of `absolute_reference`**, built 2026-08-06 with
no emitter — a wall-clock instant with no referent is exactly what that class is for.

**OPEN, and shared with #62:** `value: 30` carries NO UNIT. "age 30" is 30 of
something the document does not say. The leaf is keyed on `variable` through the D9
registry, so the unit has to come from the registry or from real documents — the same
gap as `stimulus_parameter` and the stimulus-response family. It does not change the
route; it does mean the typed leaf cannot be chosen from the template alone.

### CORRECTION to `CLAUDE.md` — "FOUR in-tree emitters" overstates it

That line was written to establish `subjectmeasurement` is a live production class
(correcting an earlier FALSE claim that it dissolved into `measurement`, which NDI
never did). The count is right and the characterisation is not — **all four emitters
are test-session builders**:

```
src/ndi/+ndi/+test/+daq/build_intan_flat_exp.m
tests/+ndi/+unittest/+session/buildSession.m
tests/+ndi/+unittest/+session/buildSessionNDRIntan.m
tests/+ndi/+unittest/+session/buildSessionNDRAxon.m
```

(plus the template, its schema, and `ndiDocumentAttributes.json` — 7 files total.)

**This is NOT a claim that no real data exists.** The corpora are a sample, and
older lab scripts could have written these documents; the class still needs its
migrator. What is corrected is only the impression of production writers in-tree.
The parallel-class fact the line exists to protect — that NDI never dissolved
`subjectmeasurement` into `measurement`, and `measurement` is a NEWER separate class
— is unaffected.

---

# THE "MISC SINGLETONS" FAMILY — team, 2026-08-05

**The team's words:** *"I agree with all of your recommendations."* NO
`TEAM-SIGN-OFF` LINE — the marker is the team's to write (Operating Rule 4).

**Two of the four were not migration questions**, the same mis-framing that put
`directory` in "file navigation":

```
binaryseries_parameters   did_v1, stable      a real v1 source
projectvar                did_v1, stable      a real v1 source
control_designation       V_eta TARGET        minted from control_stimulus_ids
interaction_purpose       V_epsilon TARGET
```

## `control_designation` — NOT a source; it belongs to the STIMULUS family

```
control_designation ⊂ base
   deps: timed_sequence_id -> timed_sequence,  derived_from_1 -> subject_interaction
   control_stimulus (matrix), method (structure)
```

It points at `timed_sequence`, the stimulus model's own class, and
`V_eta_stimulus_model_plan.md:118` already covers it:

> **`control_stimulus_ids` → `control_designation` — RESOLVED.**

So it is not a singleton and it is not undecided — it is inside a decided plan.
**Moved to the `stimulus` family on the board.**

## `interaction_purpose` — NOT a source; its only open item is its BINDING

```
interaction_purpose ⊂ base   dep: interaction_id_# -> subject_interaction
   purpose (ontology_term), comment (char)
```

Provenance V_epsilon — a DID-side target class. `CLAUDE.md`'s binding-governance
note already flags it: `interaction_purpose.purpose` is **completely unbound**
(`constraints = {}`) even though T8 says the registry maps such a term to a
value_set. **That is TaskList #32, not a disposition.**

## `binaryseries_parameters` — folds into `sampled_body`, no new decision

```
⊂ base, no deps
  time_size, time_type, data_size, data_type, data_dim, samples_regular_intervals

edge references: NONE    NDI code mentions: 0    subclasses: NONE    migrator: none
```

Those fields are the **byte layout of a binary time series** — element widths,
dtypes, dimensionality, whether sampling is regular. That is `sampled_body`'s job,
and the 2.D collapse already decided it: every format carrier phases into
`sampled_body`/`opaque_body` with the encoding as a field.

**Stated carefully:** zero emitters IN THIS REPO is not zero documents. Per the
corpora-are-a-sample rule the fold must be BUILT, not skipped — but it is a fold
into a home that already exists.

## `projectvar` — PASS THROUGH. Modelling it needs real documents first.

```
⊂ base   dep: element_id
  project, type, user, lab, description, data

ndi.database.fun.projectvardef(name, type, description, data)
   "shorthand function for building a 'projectvar' document"
```

An arbitrary named value attached to an element, tagged with project/user/lab. Most
of it maps cleanly — `element_id` -> a subject (`element.m` already promotes it),
`name`/`type` -> the statement's `variable`, `lab` -> an `organization`, `user` ->
a `person`. `project` has no home.

**`data` is an untyped char field holding anything**, and J needs to know which
`data_type` a value is. A char blob fits `term_observation` only if it is a term,
which it is not in general.

**There are no `projectvar` documents in any of the five corpora**, so there are no
real `data` values to type against. Proposing a typed model from the template alone
is precisely the wrong-assumed-shape failure that produced the ~2,078
`distance_metadata` quarantines — a migrator written against an assumed nested shape
that no real document had.

**So: pass through, and flag it as needing real documents before modelling.** One
class, no migrator today, nothing references it. Guessing its shape is how this
project has previously lost data.

---

## `interaction_purpose` — KEEP, but the justification is CONDITIONAL. 2026-08-09.

The team asked the right question: *if it has no v1 source and no justification for
existing, why not remove it?* That is the exact test that removed `openminds_import`,
and it has to be applied honestly here.

**The sweep, stated with its denominators:**

```
NDI origin/main                     files mentioning `interaction_purpose`:  0
DID-matlab src/ + tests/            hits:                                    0   (no migrator emits it)
V_eta schemas referencing it        only topics.json and index.json          (catalogues, not references)
provenance                          V_epsilon -- a DID-side class, never a v1 source
```

By the `openminds_import` test — nothing emits it, nothing references it, no v1 source —
it looks removable.

**It is not, and the difference is exactly the one that made `openminds_import` a
mistake.** `openminds_import` was persisted *on condition that an emitter be scheduled,
and none ever was.* Here an emitter IS scheduled, in a SIGNED plan:

```
V_eta_stimulus_model_plan.md:126-132
   a stimulus "approach" ... folds into `interaction_purpose` (an approach term on the
   epoch's interaction, via the openMINDS controlled-term path) ... No new class; the
   stale `stimulus_approach` provenance row is corrected to RETIRE.
```

So the class has a consumer waiting on the stimulus build, not a hypothetical one.

**AND there is a real candidate source already in the corpus** — 635 `openminds_stimulus`
documents carrying `StimulationApproach` terms, attached to a stimulus element and an
epoch. "The purpose of this interaction, in this epoch" is what `interaction_purpose`
says.

**WHICH SURFACES A CONFLICT — two signed plans send the same documents to different
places.** `migrators_j/openminds_stimulus.m` turns every one of those 635 into a
`term_assertion` on the stimulus-subject; the stimulus plan says an approach term becomes
an `interaction_purpose`. Both cannot be right. And the `term_assertion` route is
independently broken: those documents migrate with an EMPTY `subject_id` because the
migrator reads a dependency name that does not exist. Tracked as #75.

> **"TWO SIGNED PLANS" WAS WRONG, and #75 carried the error for two days under that
> title. Corrected 2026-08-11 when the row was closed.** The sentence names ONE plan
> document and ONE `.m` file, and then calls the pair two signed plans. Its own next
> clause gives it away: a signed plan does not "read a dependency name that does not
> exist" — a migrator does. **DENOMINATOR: 54 markdown files under `schemas/`, 54
> read, 24 `TEAM-SIGN-OFF` lines (23 real, plus the format template at
> `V_eta_STATUS.md:216`).** *[The 54 is that day's measurement and stays. There are
> **55 markdown files under `schemas/`** today -- one document added 2026-08-12,
> nothing deleted. The other two figures were NOT re-run.]* Exactly one names these documents — the `[misc singletons]`
> line at the top of THIS file, which sends them to `interaction_purpose`. Exactly two
> mention `term_assertion`, both in `V_eta_openminds_family_record.md` (:10, :20) and
> both about STRAIN; neither routes an approach term. The `term_assertion` route came
> from that record's *prose* ("three of the four already migrate 1→1 to
> `term_assertion`"), which was a DESCRIPTION OF THE MIGRATOR AS IT THEN STOOD, not a
> decision — and it is now stale twice over, since pass 1 stopped emitting.
>
> Why the mislabel mattered: Operating Rule 4 makes a clash between two sign-offs the
> one thing Claude may not resolve, so calling it that put a fixable code defect
> behind a stop sign. The cost was small only because the section below decided it
> anyway. **The check that would have caught it in one line: a sign-off is a
> `TEAM-SIGN-OFF` line, so before writing "two signed plans", name both lines.**
> `status_board.py` reads exactly that marker and was never fooled — the same lesson
> as #80, one level up.
>
> **ONE FIGURE IN THAT DENOMINATOR HAS SINCE MOVED, corrected 2026-08-12:**
> **there are 55 markdown files under `schemas/`, not 54.** The `54` above is LEFT AS
> WRITTEN — it is what the 2026-08-11 check actually read, and rewriting the denominator of
> a dated measurement into today's figure is how a record stops being a record. Re-derived:
>
> `$ ls schemas/*.md | wc -l` → `55`. The entire difference is ONE document added on
> 2026-08-12 (`V_eta_logical_observation_plan.md`, commit `ffc6fd7`); nothing was deleted
> or renamed, so the drift has a single named cause. **The `24 TEAM-SIGN-OFF lines` figure
> beside it was NOT re-derived** and this note does not correct it — read it as of
> 2026-08-11. **Nothing the paragraph concludes moves**: its finding is that exactly ONE
> signed line names these documents, and adding a document to the corpus cannot subtract
> from that.
>
> Found by `tools/check_prose_counts.py`, which derives the count from the tree and asks
> whether the prose still carries it, rather than by anyone re-reading this page.

**Recorded so this cannot rot the way `openminds_import` did:** if the stimulus build
lands and does NOT emit `interaction_purpose`, the class has no emitter and no consumer,
and it should be removed at that point rather than persisted for another year on the
strength of a plan that changed. The condition is now written down, which is the only
thing that was missing last time.

Its two other open items are unchanged and tracked elsewhere: `purpose` is a completely
unbound ontology term, and `interaction_id_#` is one of three numbered edge families
declared REQUIRED with nothing able to verify them.

### RESOLVED — the 635 approach documents go to `interaction_purpose`. 2026-08-09.

**What the v1 document actually records.** Both writers construct the same three-part
fact — an approach term, a stimulator, and an EPOCH:

```
origin/main:+ndi/+setup/+NDIMaker/stimulusDocMaker.m:407-412
   new_approach = openminds.controlledterms.StimulationApproach('name', ontologyLabel,
       'preferredOntologyIdentifier', ontologyNode, 'description', OntologyDescription);
   openMINDSobj2ndi_document(new_approach, session.id, 'stimulus', stimulator_id,
                             'epochid.epochid', epoch_id);

origin/main:+ndi/+setup/+stimulus/+vhlab/add_stimulus_approach.m:59-65   the same, on probe_id
```

All 635 are the same type — `openminds_stimulus` count and `StimulationApproach` count
are both 635 in the walkthrough histogram, so there is no mixed population to split.

**Why `term_assertion` is the wrong tier, decisively.** The assertion branch is TIMELESS
by construction — `subject_assertion` declares no fields and no edges, and
`time_reference_#` lives on `subject_interaction`, the OTHER branch. So an assertion
cannot carry an epoch. Migrating an epoch-scoped fact there does two wrong things at
once:

1. **It drops the epoch.** `migrators_j/openminds_stimulus.m` copies `base`,
   `subject_statement` and `term` and nothing else — the `epochid` the writer set is
   simply gone.
2. **It asserts something false.** A `term_assertion` on the stimulator says *this
   device IS-A spatial-frequency-tuning*, timelessly. The same stimulator serves a
   different approach in the next epoch — which is exactly why v1 scoped the document to
   an epoch in the first place.

The epoch scoping is the evidence: a property of the device would not need one.

**So the destination is `interaction_purpose`** — the purpose of what was done in that
epoch with that stimulator, which is what the class says and what the stimulus plan
already assigned it.

**Consequence for the two defects this touches:**

- **#71 is fixed by RE-TARGETING, not by renaming the dependency.** The migrator reads
  `stimulus_id` where NDI writes `stimulus_element_id`, producing 635 statements with an
  empty subject. Correcting the name would produce 635 well-formed statements that are
  still the wrong tier and still epoch-less. Pass 1 should instead PASS THESE THROUGH,
  guarded, and emit nothing.
- **The build is a SECOND PASS,** like the ensemble rosters and the raw-recording
  observations. `interaction_purpose.interaction_id_#` points at interactions, and the
  source names an epoch and a device, not interactions — resolving *which interactions
  happened in epoch E with stimulator P* needs the migrated graph, which a
  single-document migrator cannot see.

**And this settles `interaction_purpose`'s conditional keep**: its emitter is now a
concrete pass over 635 real documents, not a hypothetical one. The condition recorded
above still stands as written, but it is now expected to be met rather than merely hoped
for.


TEAM-SIGN-OFF [session]: jess@walthamdatascience.com / 2026-08-13 -- session.type, session.date and session.purpose are DELETED -- the did_v1 template declares only `reference` and no writer fills them (V_zeta inventions, same disposition as daqreader.file_extension). session.reference becomes `local_identifier`, REQUIRED, matching subject and epoch, and the now-duplicate optional local_identifier is dropped. THE RENAME IS A THREE-PART CHANGE: schema + migrator + NDI-matlab src/ndi/+ndi/+dataset/dir.m:69, which reads `document_properties.session.reference` directly off a retrieved document and returns nothing after the rename. NOT YET BUILT.
    (Recorded by Claude at the signer's explicit consent, given in session_01BenWtpJyRu3QhEZqCErpwm after the decision was stated in conversation. Operating Rule 4 normally forbids Claude writing this line; the signer waived that here. The DECISION is the signer's -- this is transcription, not authorship.)

BUILD-STATE: 2026-08-15 -- **BUILT, all three parts.** The signature above ends
"NOT YET BUILT" and that tail is now stale; it is NOT edited (Operating Rule 4 --
the line is the team's), so the current state is recorded here beside it.
HISTORICAL-SIGNOFF-CLAIM. The signature names three artifacts and each was
checked separately, because "the schema landed" has been mistaken for "the rename
landed" before:

        (1) SCHEMA   schemas/V_eta/stable/session.json
              superclasses : ['entity']
              fields       : [('local_identifier', mustBeNonEmpty=True)]
            -- one field, required. `type`, `date`, `purpose` and the duplicate
               optional `local_identifier` are all gone.
        (2) MIGRATOR DID-matlab .../+migrators_j/session.m
              :2  "%SESSION Brainstorm-J migrator: `reference` -> `local_identifier`"
              :43 "THE VALUE IS CARRIED, NEVER INVENTED."
        (3) NDI READ SITE  NDI-matlab src/ndi/+ndi/+dataset/dir.m
              :69-70 "BOTH VINTAGES. V_eta renamed session.reference ->
                      session.local_identifier (did-schema, signed 2026-08-13)."
              :76-79 if isfield(session_blk,'local_identifier') ... else ... .reference

The signature cites part (3) as `dir.m:69`, which still lands on the right
paragraph -- a citation into NDI outliving the edit, exactly as the citation
audit predicts for a repository we only read.

**WHY THIS NOTE EXISTS RATHER THAN A CORRECTED SIGNATURE.** Nothing kept the
signature's build claim in agreement with the build, and nothing could: the two
are updated by different acts. `tools/check_signoff_header_staleness.py` now
requires this `BUILD-STATE:` line beside any signature asserting NOT (YET)
BUILT, so the next one fails the chain instead of waiting to be walked into.

TEAM-SIGN-OFF [subject]: jess@walthamdatascience.com / 2026-08-13 -- `subject` is a PASSTHROUGH, and that is the END STATE, not a deferral: no fold is owed and none should be built. It migrates 1 -> 1 with `base.id` PRESERVED, which is load-bearing -- `subject_id` is the most-referenced edge in the corpus and a minted id would dangle every one of them. The did_v1 template declares exactly `local_identifier` and `description`, and V_eta declares exactly those two, so nothing is dropped and nothing is invented. THREE THINGS CHANGE AND NOTHING ELSE: the superclass moves `base` -> `entity` (adding one OPTIONAL `global_identifier`), `local_identifier` becomes REQUIRED (it was already populated on real documents -- PRED's sole subject carries `P03@amandalab.org` -- so the requirement quarantines nothing that was previously valid), and `base.datestamp` becomes `base.creation_timestamp` via the outbound rename rather than via this class's migrator. The migrator's only job is to guarantee the now-required `local_identifier` is non-empty; a subject with none quarantines rather than being given a manufactured handle.
    (Recorded by Claude at the signer's explicit consent, asked for and given in session_01BenWtpJyRu3QhEZqCErpwm: the line was quoted in full, the signer was told Operating Rule 4 forbids Claude writing it unprompted, and the signer answered "Yes. I confirm subject is a passthrough". The DECISION is the signer's -- this is transcription, not authorship.)

---

## Confirm-sheet answers, 2026-08-17

Five rows of `tools/confirm_sheet.py` were put to the team one at a time, each
with its emitted set, its intent and its caveat, and each answered YES — "that
is the target we want". The sheet asks whether what the migrator ALREADY emits
is the intended end state; these five were confirmed unchanged, so no build
follows from them.

| class | 20211116 docs | ENDS AS |
|---|---|---|
| `tuningcurve_calc` | 84 | `tuning_curve_calculation`, `software` |
| `oridirtuning_calc` | 42 | `tuning_curve_calculation`, `software` |
| `probe_location` | 2 | `term_observation` |
| `treatment` | 2 | `temperature_manipulation` / `dose_manipulation` / `term_manipulation` (one per row, dispatched) + `term_observation` |
| `jrclust_clusters` | 1 | `count_observation`, `sampled_body`, `software` |

`jrclust_clusters` carries a caveat the team accepted knowingly: it emits a
`sampled_body`, and 20211116 is a DOCUMENT-ONLY corpus (`find <corpus> -type f
| grep -vc '\.json$'` = 0), so that path cannot be exercised there. The team
will exercise it locally.

TEAM-SIGN-OFF [confirm sheet 2026-08-17]: jess@walthamdatascience.com / 2026-08-17 -- `tuningcurve_calc`, `oridirtuning_calc`, `probe_location`, `treatment` and `jrclust_clusters` each migrate today to the set recorded in the table above, and that set IS the intended end state. No further fold is owed for any of the five. Answered one at a time against the generated confirm sheet's evidence, not in bulk.

TEAM-SIGN-OFF [confirm sheet 2026-08-22]: jess@walthamdatascience.com / 2026-08-22 -- `stimulus_bath` migrates to a `dose_manipulation` (the delivered substance, a subject_manipulation leaf) + a `session_relative_reference` 'during' anchor + a CONDITIONAL `term_observation` (only when the source names a location), and that emitted set IS the intended end state. Deferred in pass 1 (`did2:convert:needsSessionContext`) by design, assembled by the `resolveDeferredBaths` batch pass. Strict-J D8 disposition -- the `bath`/`pharmacological_manipulation` family is retired -- matching the treatment family (`treatment_drug` / `virus_injection` also -> `dose_manipulation`). Answered against the generated confirm sheet and bar2_gap's Dab UNDECIDED flag (1,605 docs).

Decided by Jess Haley, 2026-10-21 [bath is a manipulation]: A bath is a manipulation whose value is the formulation (pointed at through `value_id`), not a dose; a dose always has an amount.

Decided by Jess Haley, 2026-10-21 [immersion or dose]: A subject immersed in a formulation (bath, perfusion, the Haley assay droplet) is a manipulation valued by the formulation; a subject given a quantity is a dose, and an unrecorded amount is stated as unknown, never left empty.

Decided by Jess Haley, 2026-10-21 [unrecorded amount is NaN]: An unrecorded amount is written as NaN in its quantity (e.g. a dose's volume.liters: NaN), and V2 stores NaN the way V1 does.

This changes the `dose_manipulation` half of the 2026-08-22 line above; the
anchor and the conditional location `term_observation` are unchanged. Why it
came up: a bath gives no amount, so the bath dose was written with an empty
`dose.value`, and the value rule (`value_inline_or_body`,
`V_eta_data_body_model_plan.md` AMENDMENT 5, with Jess's `value_id`
clarification) refuses a value that is neither inline, in bodies, nor taken
through `value_id`. `formulation` is a value kind (its superclass is `value`),
so the bath becomes a `manipulation` listing `formulation` as its value kind,
with an empty `value` and a `value_id` edge to the bath's `formulation`
document (the one listing the mixture's ingredients). `dose.json` no longer
says a dose may be empty for a bath.

The second 2026-10-21 line widens the first from baths to anything a subject
is immersed in. The test is immersion versus taking in a quantity: a subject
sitting in a formulation (a bath, perfusion) is a `manipulation` valued by the
formulation through `value_id`; a subject given an amount of it is a `dose`.
The Haley assay droplet is the case that prompted it: worms are picked with an
eyelash into a droplet of S-Complete, which evaporates before recording starts,
so the droplet is a transitory bath, not a dose. A dose whose amount the source
does not record states the amount as unknown rather than leaving `dose.value`
empty.

The third 2026-10-21 line says how: NaN in the quantity's canonical slot (a
dose of unrecorded volume is `dose.value.volume.liters: NaN`). V1 already
stores NaN: it writes documents with `did.datastructures.jsonencodenan`
(`jsonencode(..., 'ConvertInfAndNaN', false)`), so the text carries the
literal `NaN`. V2's `did2.document` wrote plain `jsonencode`, which turns a
scalar NaN into `null`, read back as `[]`, so an unknown amount came out of the
database as an absent one. DID-matlab now writes NaN, Infinity and -Infinity as
literals, as V1 does; `testSqliteDbNonFinite` tests the round trip through
`did2.database.sqlitedb` and SQLite's JSON functions. A NaN amount is a stated
value under `value_inline_or_body` (a number is not a blank). Which doses get
NaN, and in which quantity, is decided case by case; no migrator or import
writes it yet.

Decided by Jess Haley, 2026-10-21 [prepared material recipe]: "A prepared material made to a recipe (the Haley daily seeding suspension) is described by an assertion about the material whose value is the recipe formulation, through `value_id` (variable: composition, a registered term) -- not a dose."

The Haley V2 import wrote the daily seeding suspension (an entity of type
material) as a `dose` manipulation with no amount, which the value rule
(AMENDMENT 5) refuses. Nothing was given to the suspension; it was made to a
recipe. So it becomes an `assertion` about the suspension whose value kind is
`formulation`, with an empty `value` and a `value_id` edge to the recipe's
`formulation` document, `variable` = composition (PATO:0000025, registered in
`V_eta_term_registry.json`). `instance_of` does not fit: its registry row
allows only a `product` or `strain` parent, and `formulation` is a value, not
an entity. The suspension's OD600 and CFU observations are unchanged.

Decided by Jess Haley, 2026-10-21 [seeding solution preparation day]: "The seeding solution's preparation day goes on the solution entity's own time_reference_id (when it existed, from its preparation); the composition assertion stays timeless. A dilution is linked to the stock solution it was made from by a `derived_from` relation (dilution -> that day's stock)."

The first line's assertion was built at first with the time the dose had
carried, and `did2.build` refused it: an assertion is a timeless fact
(`V_eta_tenets.md`) and `assertion.json` declares no `time_reference_id`.
So the composition assertion has no time, and the day the solution was
prepared is the solution entity's own `time_reference_id` (`entity.json`:
"when this entity existed"). Each dilution is a `directed_relation`
`derived_from` (RO:0001000) with the dilution as child and that day's stock
solution as parent; the registry's `derived_from` row leaves `child_types`
and `parent_types` empty (unconstrained), so material to material needs no
registry change.

Decided by Jess Haley, 2026-10-21 [treatment routes by location]: "The v1 treatment migrators decide by the recorded location: a bath location makes the treatment an immersion (a manipulation valued by its formulation through value_id); a body site (intraperitoneal, a brain area, ...) makes it a dose, with the source's amount when it has one and otherwise NaN in the quantity; virus_injection is always a dose (an injection), its volume NaN when unrecorded, its dilution staying on the formulation; a generic treatment with no location stays a dose with NaN and is listed in the migration report as route unknown."

This applies the immersion-vs-dose line above to `treatment` (its substance
branch), `treatment_drug` and `virus_injection`, and settles how an unrecorded
amount is written for them: NaN in the dose's quantity. Built on DID-matlab
`claude/port-88` (`+migrators_j/private/jTreatmentRoute.m`,
`jTreatmentBodies.m`, `jDoseValue.m`). The bath test is the location term's
node `NCIm:C0179246` (the node NDI's Birren and Babu writers use) or its name
`bath`. A dose's amount is taken from a mixture row only when that row's unit
is an amount (mass, volume, or per body mass: Hunsberger writes `mg/kg`); a
row in a concentration unit (Molar, % v/v) stays on its ingredient, and
otherwise the dose carries `value.volume.liters` = NaN. A treatment with no
location is counted in `summary.migration_notes.route_unknown`. Whether NaN
survives a did2 write and read is DID-matlab #218's work, not this one's.

Decided by Jess Haley, 2026-10-21 [region parts]: "Any statement about an anatomical region of a subject — manipulation or observation — targets that region's part entity (one per subject and region, shared, type tissue, `part_of` the subject). A statement about the whole subject (a whole-prep or whole-slice bath, i.e. the generic 'bath' location NCIm:C0179246) targets the subject. This replaces D3's located-by-default."

Decided by Jess Haley, 2026-10-21 [laterality on the part]: when a probe records an area plus a hemisphere, the migrator makes one part entity for the area and states the hemisphere on it as a term assertion, not a second part entity.

Decided by Jess Haley, 2026-10-21 [laterality variable]: that assertion's variable is NCIT:C25185 "Laterality", and its value is the hemisphere term as the source wrote it (e.g. UBERON:0002812 left cerebral hemisphere).

Decided by Jess Haley, 2026-10-21 [anatomy variable terms]: the variable "anatomical location" (where a probe, treatment or bath acts) is NCIT:C13717 "Anatomic Site", and "anatomical structure" (what a region part entity is) is UBERON:0000061 "anatomical structure"; both are registered.

Decided by Jess Haley, 2026-10-21 [one part per side]: region parts are one per animal, area and side, so an animal recorded in left and right V1 has two parts, each with its own Laterality assertion.

Decided by Jess Haley, 2026-10-21 [slice region chain]: a recording from a region within a brain slice points at a region part entity that is a part of the slice, which is itself a part of the animal (animal -> slice -> region), so the bath on the slice and the recording share one chain.

Decided by Jess Haley, 2026-10-21 [region anatomy is UBERON]: a region part entity's anatomy term is UBERON; the migrator flags and counts any non-UBERON anatomy term it meets rather than mapping it.

The located-by-default policy it replaces (D3, `V_eta_discovery_notes.md` and
`V_eta_migration_plan.md` D3) was a first-pass cost call with no sign-off: a
site was a bare `anatomical location` value on the animal, and a part entity
was minted only where an intervention was co-anchored with it. Now every
statement about a region is about that region's part, an `entity` of type
`tissue` with a term assertion of its anatomical kind and a `part_of` relation
to the subject. There is one part per (subject, region), so an injection into a
region and a recording from it are about the same entity. What it means for
each source, as agreed in the same conversation:

- A bath at an anatomical location (Marder `marder_bathtargets.json`: `upper`
  UBERON:8910017-22, `lower` UBERON:8910010) targets the compartment's part.
  The generic bath (`NCIm:C0179246`, every Dabrowska bath and Marder's `bath`)
  targets the whole slice or prep, so NDI's `sliceTetanus` matching is
  unaffected.
- `treatment`, `treatment_drug` and `virus_injection` into a region already
  target the part (NDI `pathSPromotion`).
- A recording from a region (a probe with a `probe_location`, or a label naming
  a region from `ontology_label`) becomes an observation of the region's part,
  the same entity an injection into that region targets.

Built on NDI-matlab `claude/second-pass-88-regions`
(`+ndi/+migrate/+internal/pathSPromotion.m`, `stimulusBathToBath.m`,
`local.m`) and DID-matlab `claude/port-88` (`resolveDeferredBaths.m`: no
location observation for the generic bath). Not settled by this line and left
as they were, with counts in the pass's report: a probe with more than one
location (the Soph and 20211116 probes carry both `primary visual cortex` and a
cerebral hemisphere), a recording already moved onto a Dabrowska slice (a region
part of a slice), and a bath with no time reference to anchor its site on.

Decided by Jess Haley, 2026-10-21 [babu-media]: "In the v1 migration, Babu treatments located at agar plate medium (MICRO:0000480) or ambient air (XCO:0000918) are exposures of the worms: a manipulation of the worm subject valued by the formulation through value_id, not a dose, with no anatomical-location observation; a heat row (OM:Heat, 37 °C) is a temperature manipulation of the worms at each training time. Plates are not minted in the migration; they are minted in a proper Babu V2 import from source."

This settles the Babu case the location rule above did not fit: NDI's
`+babu/TreatmentCreator.m` writes its chemical, odour and OP50 rows as
`treatment_drug` documents located at agar plate medium or ambient air
(`+babu/treatments.json` `agar`, `air`), and the literal rule made them doses
with a NaN amount and an "anatomical location" of agar or air. Built on
DID-matlab `claude/port-88` (`47d0f4fa`): `jTreatmentRoute` routes the two
media to the immersion shape, and `treatment_drug` turns a mixture whose
every row is `OM:Heat` into a `temperature_manipulation` (`celsius` filled
from the NCIT:C42559 "Degree Celsius" unit). Babu writes one heat document per
training time, so each migrates to its own temperature manipulation.

Decided by Jess Haley, 2026-10-21 [virus-location]: "virus_injection follows the same location rule as the other treatments: a bath location makes it an immersion (a manipulation of the subject valued by the virus formulation through value_id, no location observation); a body site makes it a dose. A dilution of 0 is treated as not recorded (NaN), not as a measured 0."

This SUPERSEDES the "virus_injection is always a dose (an injection), its
volume NaN when unrecorded, its dilution staying on the formulation" part of
the treatment-location line above ([treatment-location], "The v1 treatment
migrators decide by the recorded location"); the rest of that line stands.
The case that prompted it: NDI's Birren writers (`+birren/TreatmentCreator.m`,
`createSayaTreatments.m`) record AAV DREADDs for cell cultures as
`virus_injection` located in the bath (NCIm:C0179246), with `dilution = 0`,
the template blank. Built on DID-matlab `claude/port-88` (`2c306d60`):
`virus_injection` is routed by `jTreatmentRoute` like `treatment_drug` (bath
-> a formulation-valued manipulation through `value_id`; a body site -> a dose
with `value.volume.liters` = NaN and the site observation; no location -> that
dose, counted as `route_unknown`), and a dilution of 0 leaves the virus
ingredient's concentration NaN with no "dilution" unit.

Decided by Jess Haley, 2026-10-21 [unknown-amount-slot]: When a dose's amount was not recorded and the kind of quantity is not known, the NaN goes in value.volume.liters; where the kind is known (from the source, the paper, or a case raised with the team), the NaN goes in that quantity instead, decided case by case.

Built on DID-matlab `claude/port-88` (`4ad0c1cc`, `private/jDoseValue.m`):
`value.volume.liters` stays the default, and when a source row states the
kind of amount (an amount unit: mass, volume, per body mass) but no number,
the NaN goes in that quantity with the unit as `source_unit`. No NDI writer on
`origin/main` writes such a row today (Hunsberger always gives 1 or 0.25
mg/kg; the Birren and Babu rows are concentrations), so a constructed test
covers it. A kind known only from a paper or a team case is not in the source
and is decided case by case, as the line says; nothing builds it generally.

Decided by Jess Haley, 2026-10-21 [dose per ingredient]: "A dose states the amount of the whole formulation in its top-level quantities, and the amount of any specific ingredient in `value.ingredients`, each entry paired by order with a repeated `ingredient_id` edge on the dose itself (0-based, the same convention as the formulation: exactly one entry per ingredient_id edge, same order); each ingredient_id on a dose must be one of the ingredients of the dose's formulation."

The motivating case is Hunsberger's alprazolam "1 mg/kg": an amount of the
active chemical per body mass, not of the injected solution (alprazolam in
saline). Built in `schemas/V_eta/stable/dose.json`: a repeated, ordered,
optional `ingredient_id` edge declared like the formulation's, and
`value.ingredients` (entries `mass`, `volume`, `substance_amount`, `count`,
`amount_per_body_mass`). Two named rules: `ingredients_match_edges` (one entry
per edge, same order) is checkable on the dose alone;
`ingredient_in_formulation` needs the formulation document, so it is a batch
or builder check, not a per-document one.

Decided by Jess Haley, 2026-10-21 [multiple amount rows]: when a v1 treatment carries more than one amount row, the migrator puts each amount in its matching dose slot (volume, mass, substance_amount, count, or an ingredient's amount_per_body_mass), instead of taking an amount only when exactly one row exists.

Decided by Jess Haley, 2026-10-21 [named-chemical amount on the ingredient]: a v1 treatment amount row in mass or substance-amount units that names a chemical goes into that chemical's dose ingredient entry (value.ingredients[k], paired with its ingredient_id edge), because it is the amount of that chemical delivered, not of the whole formulation; the dose's top-level mass is used only for a row that names no chemical. The formulation keeps the recipe (added amounts or final concentrations), not what one animal received.

Decided by Jess Haley, 2026-10-21 [blank per-body-mass on the ingredient]: a v1 per-body-mass amount row (e.g. mg/kg) that names a chemical but has no number goes into that chemical's dose ingredient entry with NaN as its value, the same place a filled-in row goes; it is not written at the dose's top level.

Decided by Jess Haley, 2026-10-21 [generic treatment number]: a generic v1 treatment's numeric_value is never read as an amount of an ingredient or of the dose; it is carried as the value the treatment's term says it is (the vhlab grating stimulation row's number is a duration in hours), and kept as an unlabelled number only when the term does not say.

Decided by Jess Haley, 2026-10-21 [treatment onset]: a migrated treatment manipulation is anchored at the v1 administration_onset_time when one is recorded, and at "during the session" only when none is.

Decided by Jess Haley, 2026-10-21 [virus injection onset]: a v1 virus_injection's virus_AdministrationDate is its onset, so the migrated manipulation is anchored at that date; "during the session" only when the date is absent.

Decided by Jess Haley, 2026-10-21 [transfer onset]: a v1 treatment_transfer's timestamp (clock dev_local_time, written by the Babu importer as a negative number of hours) is its onset, so the migrated transfer is anchored at that time on the session's local clock; "during the session" only when no timestamp is recorded.

WHAT THIS COSTS IF IT IS WRONG, stated because a confirmation is the cheapest
kind of signature to give and the hardest to revisit: these five account for 131
of 20211116's 1,220 documents. Two of them (`tuningcurve_calc`,
`oridirtuning_calc`) were already corpus-green under the Lepsky calculator fold
with 0 orphans, so the confirmation records a decision that had already been
made and had simply never been joined to a ledger row.

A SIXTH ROW WAS NOT CONFIRMED. `neuron_extracellular` was sent back for
investigation and the investigation found a real drop -- see the
`neuron_extracellular` section below.

PROVENANCE: Operating Rule 4 -- Claude typed this line under explicit
authorisation, "Do 3, and note the sign-offs" (jess, in session, 2026-08-17).
The five answers are the team's; the transcription is Claude's.

## `neuron_extracellular` — the sixth confirm-sheet row, NOT confirmed

Sent back for investigation rather than answered. The sheet's caveat read
"`mean_waveform` + cell-type `term_assertion` deferred", which understates it.
Re-derived from all 21 documents in 20211116:

        DENOMINATOR: 21 neuron_extracellular document(s) read

        field                          shape    distinct
        number_of_samples_per_channel  scalar    1/21     always 21
        number_of_channels             scalar    1/21     always 32
        mean_waveform                  21x32    21/21     -316.7 .. 259.4
        waveform_sample_times          21        1/21     -0.25 .. +0.75 ms
        cluster_index                  scalar   21/21     1..21
        quality_number                 scalar    2/21     1 or 4
        quality_label                  scalar    2/21     "multi" / "single"

        depends_on: element_id 21/21 populated, spike_clusters_id 0/21

Tracing every source field through `+migrators_j/neuron_extracellular.m`: only
`quality_number`, `element_id` and the `app` block reach an emitted document.
The source block is read for fields and never carried out, so what is DROPPED is

  * `mean_waveform` -- 672 numbers per document, UNIQUE to every neuron, 14,112
    in this corpus. The mean spike waveform across 32 channels: the most
    identifying physiological feature a sorted unit has.
  * `waveform_sample_times` -- its time base.
  * `cluster_index` -- the sorter's own label, unique per neuron. It survives
    only as text inside the derived subject's `local_identifier`,
    `unit_<cluster_index>`.
  * `number_of_channels` / `number_of_samples_per_channel` -- redundant, both
    derivable from the array shape.

**THE BLOCKER IN THE MIGRATOR'S OWN NOTE IS STALE.** It reads "needs a
body-serialization decision -- a sampled_body carries files, not an inline
matrix". That was true when written and is not now: `axes[]` landed 2026-08-14,
and the time base is EXACTLY REGULAR --

        21 entries, distinct steps: [5e-05]
        origin = -0.00025 s, spacing = 5e-05 s   (20 kHz)

-- so it needs no new machinery. The shape that follows from the signed
data_body model is a `voltage_observation` of the neuron-subject (microvolts
over time and channel) with a `sampled_body` carrying two axes: time REGULAR
with the origin and spacing above, and a channel axis of n = 32. The two count
fields drop as derivable, exactly as `ngrid.data_size` does.

**ONE HAZARD FOR WHOEVER BUILDS IT:** `spike_clusters_id` is declared and EMPTY
on all 21 documents IN THE SOURCE. That is not a V_eta defect, but a target or
tombstone that makes it required would quarantine all 21.

DECISION, team 2026-08-17: build the waveform fold BEFORE confirming the row --
"Let's investigate this one", then "Do 3". Not signed as a disposition here; the
signature belongs with the built fold.


TEAM-SIGN-OFF [orientation_direction_tuning.json location]:
Steve Van Hooser 2026-09-22 -- STAYS ON NDI-matlab post-retirement of
ndi.app.oridirtuning (VH-Lab/NDI-matlab#1001). Resolves #67 sub-question.

SIGN-OFF SUPERSEDED [spatial_transcriptomics_family]: jess@walthamdatascience.com / 2026-09-29 -- replaced by the #73 review, V_eta_spatial_transcriptomics_plan.md item 18 (nothing from the eight NDI spatial classes is carried forward). The signature below is left as signed.

TEAM-SIGN-OFF [spatial_transcriptomics_family]: Steve Van Hooser 2026-09-22 --
Corrected Option C for the spatial-transcriptomics family from
Waltham-Data-Science/DID-schema#70. Structural: `spatialGeneExpressionPyramid`
becomes ⊂ [geneExpression, subject_observation] (was ⊂ [base, geneExpression]),
picking up variable/method_parameters/sample_time/time_reference_# from the
subject_observation direction; the existing subject_id required-ness moves from
the class's own declaration to the inherited slot. `geneExpression` STAYS a
⊂ base shape mixin (assay/count_type/count_units) -- semantically a shape, not
an observation; the observation-ness lives on the concrete pyramid class that
binds it to a subject. The other five classes in #70 PERSIST as ⊂ base:
`spatialGeneExpressionCells` (data-of-record for pyramid observation, subject_id
required), `spatialGeneExpressionTiles` (same, subject_id optional because the
pyramid dep carries it), `cellTypeLabels` (labeling attached to a cells doc, not
directly to a subject; is_unsupervised flag load-bearing), `geneListMapping`
(between-entity relation with structure -- alias vs ortholog matters, not a
bare directed_relation), `fileReference` (DELIBERATELY NOT folded to
generic_file; the two coexist by design per the class's own .md doc --
generic_file holds bytes, fileReference records identity of an external file).
Also outside #70's 6 but confirmed here: `geneList` STAYS ⊂ base reference table.
Follow-ons deferred, not signed as part of this: `axes[]`/`format`/`compression`
migration for Cells/Tiles when 2.D data_body ships; T8 bindings for
contour_reference/segmentation_method/mapping_type/checksumAlgorithm/
formatOntology/origin_corner; a bound `variable` term for the pyramid
observation (needs to exist in NDIC or the registry before the reshape validates
end-to-end). Full reasoning in #70.

RE-DERIVED 2026-09-25 (plan_documents, `check_prose_counts`): **56 markdown files under `schemas/`** (was 55; +`V_eta_spatial_transcriptomics_plan.md`, the #73 review's decision record). Re-derive with `ls schemas/*.md | wc -l`, do not quote.

TEAM-SIGN-OFF [spike-sorter output, amends the 2026-08-17 confirm sheet]: jess@walthamdatascience.com / 2026-09-29 -- `kilosort_clusters`, `kiasort_clusters` and `jrclust_clusters` migrate to `label_calculation` (#73 item 35), not `count_observation`.

TEAM-SIGN-OFF [time anchors, amends the 2026-08-22 confirm sheet]: jess@walthamdatascience.com / 2026-09-29 -- where the 2026-08-22 confirm sheet names `session_relative_reference`, the target is `relative_time_reference` (#65 increment 3b deleted the session/epoch reference leaves).

TEAM-SIGN-OFF [dimensioned classes, batch confirmation]: jess@walthamdatascience.com / 2026-09-29 -- confirmed as persisting classes: the observations `acceleration_observation`, `concentration_observation`, `current_observation`, `frequency_observation`, `mass_observation`, `pressure_observation`, `temperature_observation`, `velocity_observation`, `volume_observation`; the composites `capacitance`, `conductance`, `current`, `energy`, `force`, `intensity`, `power`, `resistance`; `date_assertion`; `contrast_sensitivity_calculation`; `subject_assertion`; and the tuning leaves under their #73 names (`orientation_direction_tuning_calculation`, `contrast_tuning_calculation`, `spatial_frequency_tuning_calculation`, `temporal_frequency_tuning_calculation`, `speed_tuning_calculation`). (audit 2 C19; the two classes that finding counts but does not name are not covered.)

RE-DERIVED 2026-09-30 (plan_documents, `check_prose_counts`): **57 markdown files under `schemas/`** (was 56; +`V_eta_study_plan.md`). Re-derive with `ls schemas/*.md | wc -l`, do not quote.

RE-DERIVED 2026-10-08 (one `entity` class and statements by composition, a PROPOSAL built ahead of signature, `V_eta_entity_composition_plan.md`; `check_prose_counts` re-derives all nouns): **58 markdown files under `schemas/`** (was 57; +`V_eta_entity_composition_plan.md`). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-10-09 (`linked_session`, a PROPOSAL built ahead of signature, `V_eta_linked_session_plan.md`; `check_prose_counts` re-derives all nouns): **59 markdown files under `schemas/`** (was 58; +`V_eta_linked_session_plan.md`). Re-derive with `check_prose_counts`, do not quote these directly.

RE-DERIVED 2026-10-14 (plan_documents, `check_prose_counts`): **60 markdown files under `schemas/`** (was 59; +`V_eta_duplicate_entities_plan.md`, a PROPOSAL: when two records are `same_as`). Re-derive with `ls schemas/*.md | wc -l`, do not quote.

RE-DERIVED 2026-10-19 (plan_documents, `check_prose_counts`): **61 markdown files under `schemas/`** (was 60; +`V_eta_prefix_spelling_plan.md`, a PROPOSAL: write a CURIE prefix the way its issuer cites it). Re-derive with `ls schemas/*.md | wc -l`, do not quote.

RE-DERIVED 2026-10-20 (plan_documents, `check_prose_counts`): **62 markdown files under `schemas/`** (was 61; +`V_eta_term_registry_plan.md`, Jess Haley's decision: the term list lives in did-schema and an unregistered term is an error). Re-derive with `ls schemas/*.md | wc -l`, do not quote.

RE-DERIVED 2026-10-20 (plan_documents, `check_prose_counts`): **63 markdown files under `schemas/`** (was 62; +`V_eta_relation_inheritance_plan.md`). Re-derive with `ls schemas/*.md | wc -l`, do not quote.

RE-DERIVED 2026-10-21 (plan_documents, `check_prose_counts`): **64 markdown files under `schemas/`** (was 63; +`V_eta_source_unit_plan.md`). Re-derive with `ls schemas/*.md | wc -l`, do not quote.

RE-DERIVED 2026-10-21 (plan_documents, `check_prose_counts`): **65 markdown files under `schemas/`** (was 64; +`V_eta_method_plan.md`). Re-derive with `ls schemas/*.md | wc -l`, do not quote.

Decided by Jess Haley, 2026-10-21 [sorter input]: spike-sorter output (`jrclust_clusters`, `kilosort_clusters`, `kiasort_clusters`; a calculation with the `label` value kind, per the 2026-09-29 sign-off) takes as its input the per-epoch recording observations of the electrode it sorted, when they exist, falling back to the electrode entity when they do not (answer "1b").

Decided by Jess Haley, 2026-10-21 [sorter keys]: `kilosort_clusters` and `kiasort_clusters` carry no keys: the sorter's output folder is the value as-is, and "keys [spike]" applies only where the bytes are an array (as in `jrclust_clusters`) (answer "2a").

Decided by Jess Haley, 2026-10-22 [migrated masks are logical]: a migrated v1 imageStack mask is a calculation with the `logical` value kind (one per mask, 1 = inside), its variable the region it marks, as the native Haley import writes masks ([masks use the region variable], T-11); no method, because none is recorded. Replaces the label value kind and the "pixel label" variable. (Answer "3A".) Her calculations' software is her analysis package (spec `haley_analysis`, decision #60 of the Haley import), already so in the import.

Decided by Jess Haley, 2026-10-22 [sorter software]: a spike-sorter output with no `app` block names its software from its v1 class (jrclust, kilosort, kiasort); a sorted unit (`neuron_extracellular`) with no software record has no `software_id` (per [calculation-software-optional decided]), not an invented "spike sorter". (Answer "4c".)

Deferred by Jess Haley, 2026-10-22, to before the Haley V2 import: whether the Haley import's acquisition systems should carry the software entities naming NDI classes (`ndi.daq.system.image`, `ndi.file.navigator.bodies`, `ndi.daq.reader.image.ndr`; Haley import decisions #29, #33). Not decided; nothing changes until then.

Decided by Jess Haley, 2026-10-22 [migrated masks have no software]: a migrated v1 imageStack mask calculation carries no `software_id`, because v1 `imageStack` records none ([calculation-software-optional decided], V_eta_spatial_transcriptomics_plan.md); the native Haley import names her analysis package. Answer "2y".

Decided by Jess Haley, 2026-10-22 [encounter axis]: a Haley density estimate's dimension is NCIT:C62143 Encounter, with `onset time` as a covariate along it, not a dimension named "encounter onset time" (answer "7.4a").

Decided by Jess Haley, 2026-10-22 [software dedup after pass one]: duplicate software, operating-system and interpreter entities are merged right after the first pass, not only at the end, with a test that the final document set is unchanged (answer "10a"; Soph peaked at 14.4 GB RSS plus 5 GB swap on a 16 GB runner, 665k documents before the end-of-run merge, 224k after).

Deferred by Jess Haley, 2026-10-22, until before the Haley V2 rerun (after the merge): whether the Haley import's acquisition systems carry the NDI software entities ("8 defer for a little longer"; "Decision 8 needs to come before the Haley rerun").

Decided by Jess Haley, 2026-10-22 [software location]: software an NDI object is rebuilt from (the software behind acquisition_system, acquisition_reader and epoch_file_pattern) stays in EACH session, in both paths (the migrator and the Haley import); only descriptive software is merged to the dataset, and softwareDedup changes accordingly. This answers deferred decision 8 above: the Haley import keeps its three software entities (answer "H1a").

Decided by Jess Haley, 2026-10-22 [object software scope]: the software NDI rebuilds an object from is the software of every ndi.vintage.map class with an object_edge (acquisition system, reader, file pattern, syncgraph/syncrule clock alignment) plus any `reader_id`; all of it stays in its session (answer "both ok"). Built: NDI-matlab 6c4a27c14.

Decided by Jess Haley, 2026-10-22 [NDI ref fallback]: DID-matlab's Test code workflow resolves its NDI-matlab sibling by the same-name branch, then `claude/v2-object-layer` (NDI #1021's head, until #1021 merges), then `V2`, then `main`, instead of falling back straight to `main` (where `+ndi/+migrate` does not exist, so the cross-repo divergence check skipped); the integration branch is removed from it and from did-schema's tests.yml in the first commit after the merge (answers "9 A, but I think remove the object layer branch" and then "B"; the order with the integration branch ahead of `V2` is the one that keeps CI reading #1021 before the merge, as clarified to her on 2026-10-22).

Decided by Jess Haley, 2026-10-22 [NDI ref fallback, test-corpus]: DID-matlab's test-corpus.yml resolves NDI-matlab in the same order as [NDI ref fallback] (answer "yes to all three"). Built: DID-matlab 4963355.


## 2026-10-22 -- tenet audit: acquisition

Decided by Jess Haley, 2026-10-22 [epoch to system link]: the `recorded_by` relation row is dropped. An epoch reaches its acquisition system through the recording interaction's `acquisition_channels_id` and then `acquisition_channels.acquisition_system_id`; `acquisition_system.device_id` is filled when known (in the Haley import, the camera entity, `instrumentFor` in sessionDocuments.m). It depends on [channel types] (answer "A1 agreed").

Decided by Jess Haley, 2026-10-22 [channel types]: `acquisition_channels.channels.type` binds the 10 hardware channel types, rooted at NCIT:C44170 Channel: md NCIT:C52095 Metadata, tx NCIT:C25704 Text, and EMPTY:0000370-0000377 (analog input, analog output, digital input, digital output, time, auxiliary input, event and marker channel). The migrator maps the v1 prefixes to these terms, and NDI's vintage map maps them back for its readers; that map lives in their code, not in the term registry (Jess Haley's clarification the same day: the registry needs nodes, not synonyms), and code matches a channel type by its node. The 8 derived read modes (dep den dimp dimn aep aen aimp aimn) get no terms (0 uses in the corpus probemaps: B {mk,e,md,ai}, Dab {mk,e,ai,md,ao}, Soph {mk,e,md,ai}). Her answers: "agreed, B2a with 10"; "should be real terms". (The old 4-value list came from d329ef0, which copied daqsystemstring.m's example.)

Decided by Jess Haley, 2026-10-22 [required acquisition edges]: `acquisition_system.reader_id` and `epoch_file_pattern_id` are required (answer "H2a"). Built: both edges `mustBeNonEmpty`.

Decided by Jess Haley, 2026-10-22 [instrument and device]: `interaction.instrument_id` and `acquisition_system.device_id` are both kept and no rule ties them. instrument_id is "the device that sensed or acted on the subject (electrode, stimulator, camera, thermometer)"; device_id is "the device that produced the files this system reads (a digitizer, a camera, a computer); the same entity as an interaction's instrument when one device does both" (answer "a"). Built: the two edge documentations.

Decided by Jess Haley, 2026-10-22 [rig minting with edges]: the #73 item 56 rig-minting pass mints each acquisition system from its v1 daqsystem document, with `reader_id` and `epoch_file_pattern_id`; a devicestring naming a rig with no daqsystem document gets no system and is counted (measured 2026-10-22: 0 such rigs in B, Dab, Soph, 20211116, PRED) (answer "2a"). Built: DID-matlab d2b3558 (a daqsystem missing its reader or navigator is quarantined), af27912 (`rigs_without_daqsystem` count).

Decided by Jess Haley, 2026-10-23 [generic_file emitted set]: the set DID-matlab's batch pass `did2.convert.foldGenericFiles` emits for a v1 `generic_file` is the end state: an `observation + term` keeping the v1 id (its `variable` from the sibling `ontologyLabel`) plus an `opaque_body` holding the file; a document the pass cannot fold stays as it is, counted under its refusal reason (answer "K2 a"). Recorded as `confirmed_targets` in `V_eta_migration_targets.json`; [stranded sources] in `V_eta_OPEN_WORK.md` is the earlier decision this confirms.

Decided by Jess Haley, 2026-10-23 [v1 passthroughs accepted]: these 13 classes stay as v1 documents for now: binnedspikeratevm, distance_metadata, oneepoch, openminds, openminds_stimulus, simple_calc, spike_clusters, spikewaves, stimulus_parameter, vmneuralresponseresiduals, vmspikesummary, SpikeInterfaceSortingOutputs, ontologyLabel; any corpus holding one is reported not done until that class is built (`openminds` and `stimulus_parameter` keep their decided targets) (answer "K22 a").

Decided by Jess Haley, 2026-10-23 [sliceTetanus stays in NDI]: `sliceTetanus` stays in NDI's second pass until after the merge; moving it to DID's migrators would need re-proving on the corpora (answer "K23", as recommended).

Decided by Jess Haley, 2026-10-23 [confirm sheet matches]: what the migrator emits today is the end state for demoNDI and demoNDIMock (one `demo`, `mock` false/true), electrode_offset_voltage (a voltage observation of the probe, temperature as a condition), hartley_calc (receptive_field_calculation, two sampled bodies, spike-times body, anchor, software), openminds_element and openminds_subject (one term assertion), position_metadata (term observation, variable "position"), probe_location (term observation of the probe, atlas term) and subject_group (group entity plus member_of per member) (answers "K8, K9, K12, K16, K17, K18, K19 a"). Recorded only after the code was read and matched the description approved (DID-matlab 4667fb7). The other confirm-sheet answers of the same day (K5, K6, K7, K10, K11, K13, K14, K15, K20, K21) are NOT recorded: the code differs from what was described, and they go back to the team.

Decided by Jess Haley, 2026-10-23 [sibling lock]: did-schema's chain builds and checks against exact, locked sibling commits instead of moving refs ("lock now, copy the V1 templates into did-schema at the freeze"; "yes, do both"). `tools/sibling_lock.json` names NDI-matlab's and DID-matlab's head and `main` commits; `tools/sibling_lock.py --update` moves them in a deliberate commit; CI checks out the locked heads and no longer resolves branches, so [NDI ref fallback]'s did-schema half no longer applies. Copying the V1 templates and ground truth into did-schema at the V1 freeze removes the NDI `main` dependency altogether. Built: did-schema 030d611

Decided by Jess Haley, 2026-10-23 [migration not generalizable]: "migration from V1 to V2 is NOT generalizable and new imports and human decisions will need to be made" — generic migration is mechanical and lossless only, then frozen; a publishable V2 dataset comes from a per-dataset import with recorded human decisions.

Decided by Jess Haley, 2026-10-24 [migration kept]: "many datasets might exist as only v1" — generic migration is kept as the first stage of an import from v1, not dropped.

Decided by Jess Haley, 2026-10-24 [v1 import stages]: V2 reads v1 as stored; generic stage is lossless plumbing; meaning comes from a per-dataset decision workbook with defaults; one pipeline, two inputs (raw source or v1 documents).

Decided by Jess Haley, 2026-10-24 [optional additions]: "be able to add new information that didn't have a v1 home into a migrated V2" — common, optional V2 decisions in the workbook, built through the same builder and validator, logged as added at import.

Proposed (not decided) [corpus code bins]: existing corpus-specific migrator code is sorted A generic / B dataset map / C workbook default; audit committed in `review/corpus-code-audit-2026-10-24/` (2026-10-24), bins pending your and Steve's confirmation.

Decided by Jess Haley, 2026-10-23 [V_delta removed]: "there should be no mention of v_delta"; "Remove V_delta from anywhere it could confuse future claude or human users and cause regressions from V_eta". V_eta is the only migration target; V_delta's read-time conversion, migration target, database stamp, fixtures and documentation are removed from DID-matlab and NDI-matlab. Built: NDI-matlab f27302632 (#1054), DID-matlab a502c76 (#226)

Decided by Jess Haley, 2026-10-23 [v1 read as stored]: (answer "2a") V2 NDI reads a v1 document exactly as stored; the v1 constructors' own `depends_on` field tidying stays, as v1 behaviour. Built: NDI-matlab f27302632 (#1054)

Decided by Jess Haley, 2026-10-23 [cloud migrate refuses]: (answer "4a") `ndi.migrate.cloud` refuses to write until it runs the whole pipeline `ndi.migrate.local` runs; its dry-run report still works. Built: NDI-matlab f27302632 (#1054)

Decided by Jess Haley, 2026-10-23 [V2 stamp]: "new files should have V2 stamp" and (answer "5b") a database is stamped `V2` and any other stamp is refused; a file stamped `V_delta` is re-created by re-running its import. Built: DID-matlab a502c76 (#226)

Decided by Jess Haley, 2026-10-24 [#112 superseded]: ("yes close 112") did-schema keeps committing the sibling-dependent generated files (coverage ledger, status board, decisions JSON, class walkthrough); the sibling lock ([sibling lock], `tools/sibling_lock.json`) removes the drift that issue #112 (2026-10-22, "queue (a) for right after the merge") was opened to remove, since those files now change only when the lock is moved deliberately. Issue #112 is closed as superseded.

Decided by Jess Haley, 2026-10-24 [image_collection retired]: ("Retire image collection") `image_collection` is a tombstone, as [stranded sources] (V_eta_OPEN_WORK.md, 2026-08-11) already said: its class file moves from `stable/` to `deprecated/` so it can no longer be written as a V2 class; v1 `imageCollection` documents are read as stored.

Decided by Jess Haley, 2026-10-24 [V2 builder refuses retired]: ("You can do step 2 to refuse retired classes") `did2.build` refuses to create a new document of a class whose `disposition` is `retire`, naming its replacement where one is recorded; reading v1 and the generic migration are not affected. Built: DID-matlab 57e2327 (#230: did2.build refusal, strict mode RetiredClasses), did-schema (#127: D5 in tools/validate_v_eta.py derives `stable/class_disposition_meta.json`, which arms it; confirmed by Jess Haley, 2026-10-25: "Okay")

Decided by Jess Haley, 2026-10-23 [warn on v1 open]: (answer "1. yes") opening a dataset that still holds unmigrated v1 documents warns once. Built: NDI-matlab 9ec09fd (#1057: `NDI:V2:v1DocumentsPresent`, test TestWarnOnV1Open)

Decided by Jess Haley, 2026-10-23 [compat write layer removed]: (answer "3a") the `ndi.compat` write layer, which writes reshaped `probe_location` and `treatment` documents into v1 databases, is removed; v1 data is written as v1. Built: NDI-matlab 9ec09fd (#1057, test TestV1WriteShape)

Decided by Jess Haley, 2026-10-24 [passthrough stays v1]: ("Yes stamp V1") a v1 document the generic migration carries through unchanged stays a v1 document, stamped v1, rather than becoming a V_eta document of a retired class (at DID-matlab a502c76 the migration rows emit 29 classes marked `retire` this way). Build pending: DID-matlab (generic migration keeps the v1 stamp on passed-through documents)

Decided by Jess Haley, 2026-10-24 [passthrough stays v1: how]: ("2 agreed", "3 ok", answering the build questions on DID-matlab #230) "carried through unchanged" is judged after the whole pipeline: a document still unchanged at the end of `ndi.migrate.local` (after the DID batch passes and NDI's second pass) is stamped v1 there, so the second pass keeps receiving what it receives today; a v1 document is stored in the same V2 database, with V_eta validation skipped for it and counted. Built: DID-matlab 4dec9f1 (#242: `did_v1` stored without V_eta validation, counted by `sqlitedb.countV1`), NDI-matlab 2722339 (#1061: final stamping step, `ndi.migrate.internal.carryUnchangedAsV1`)

Decided by Jess Haley, 2026-10-25 [document stamps]: ("The v2 version") a v1 document's `document_class.schema_version` is `did_v1` and a V2 document's is `did_v2` (it is `V_eta` today); the schema set keeps its name, V_eta. Built in the order the siblings must follow: DID-matlab and NDI-matlab read both `V_eta` and `did_v2`, then did-schema's `schema_version_value` becomes `did_v2`, then the writers stamp `did_v2`. Built: DID-matlab 4dec9f1 (#242, read both), c451d75 (#245, writers stamp `did_v2`), 4c89542 (#246); NDI-matlab 2722339 (#1061), 98d0d11 (#1065), 25a1f83 (#1066); did-schema 6154b1a (#130, `schema_version_value` = `did_v2`)

Decided by Jess Haley, 2026-10-25 [V_eta stamp not accepted]: ("Nothing real was imported as V2. I'll rerun Haley. Stop accepting veta") once the writers stamp `did_v2`, a document stamped `V_eta` is no longer accepted; there is no alias, as for V_delta, and existing V2 imports (Haley) are re-run. Accepting both is only the transitional first step of [document stamps]. Built: DID-matlab 4c89542 (#246: `v2Stamps` = {'did_v2'}, a `V_eta` body is quarantined as `did2:convert:unknownSchemaVersion`), NDI-matlab 25a1f83 (#1066: writers call `did2.schema.v2Stamp()`)

Decided by Jess Haley, 2026-10-25 [termNumberKind is per-dataset]: (answer "1. B" to the corpus-code audit, `review/corpus-code-audit-2026-10-24/README.md` question 1a) DID-matlab `treatment:termNumberKind`, which reads the one term EMPTY:0000199 as a time in hours, is a meaning decision for the one dataset family whose importer writes that term (vhlab); it moves out of the generic migration into that dataset's map.

Decided by Jess Haley, 2026-10-25 [WBStrain prefix is generic]: (answer "A", question 1b) NDI-matlab `etaShape:curie` rewriting `WBStrain:<n>` to `WormBase:WBStrain<n>` is a prefix-spelling rule ([prefix spelling], `V_eta_prefix_spelling_plan.md`) and stays in the generic migration.

Decided by Jess Haley, 2026-10-25 [generic stage is lossless]: (answer "4. Yes", question 4) the generic migration keeps the v1 document, or the fields it dropped, whenever it cannot place everything; nothing it cannot place is dropped or rewritten. This applies to the places the audit lists under "What blocks a lossless generic stage" in `review/corpus-code-audit-2026-10-24/DID-matlab.md` and `NDI-matlab.md`. Built: DID-matlab 0eee7ee (#247), NDI-matlab e0177b3 (#1067); the further drops the drop census found are built under their own lines (2026-10-25/26)

Decided by Jess Haley, 2026-10-25 [subject local identifier is an identifier]: (question 1c) "subject local identifier is also an identifier. It should be treated the same as the document identifier, tho the document identifier is more certain": an ontologyTableRow's subject found by `SubjectDocumentIdentifier` or by `SubjectLocalIdentifier` is a generic rule (bin A), the document id taking precedence. "The only caveat is that each column of an ontology table row may not necessarily refer to that subject. For example in Haley a column may describe a patch or plate while the row names a worm": which entity each column is about is not generic; it is that table's (that dataset's) decision.

Decided by Jess Haley, 2026-10-25 [NewStim recipes are a default]: (question 1d, "okay") NDI-matlab's NewStim stimulus recipes (`stimulusRecipe`, `newStimKind`) are a per-software default (bin C): written once, offered by the decision workbook to every dataset recorded with NewStim.

Decided by Jess Haley, 2026-10-25 [no invented values]: (question 3, "Sounds good") where the v1 source does not state a value, the migration does not invent one: a creation timestamp (`base.datestamp`, written as `2024-01-01T00:00:00.000Z` in 16 files today) is the v1 source document's own datestamp, else the time the migration ran; a content value the source does not give (e.g. `image_stack`'s assumed `YXCZT` / `uint16`) is left empty where the V2 field allows it, and otherwise the document is carried through as v1 ([generic stage is lossless]). Built: DID-matlab 0949d61 (#243: `did2.convert.migrationTime` at every site, `image_stack` assumes no order or type), NDI-matlab 13dbcdc (#1062: one time pinned per `ndi.migrate.local` run)

Decided by Jess Haley, 2026-10-25 [dataset name not invented]: ("yes, record it that way") a V2 dataset's identity is its `entity.local_identifier`, which holds the v1 dataset `reference` (NDI `+setup/+V2/createDataset.m`; DID `+migrators_j/session.m` then `resolveDatasetEntities.m`). Its `full_name` is the metadata form's `DatasetFullName`, else `DatasetShortName`, else "not stated"; `'(unnamed dataset)'` is no longer written (DID `metadata_editor.m`, `resolveOpenmindsCitations.m`). (`full_name` becomes `entity.name`, which V_eta does not require; the "required" is a code comment only.) Built: DID-matlab 0949d61 (#243)

Decided by Jess Haley, 2026-10-25 [NDI CI picks DID branch]: ("1. Yes") NDI-matlab's workflows check out the DID-matlab branch with the same name as the NDI branch when one exists, else `V2`, as DID-matlab's workflows already do for NDI-matlab; a DID/NDI pair is then tested together and merged back to back, without a red window. Built: NDI-matlab 54aaea2 (#1064: the six V_eta migrate / V2 import workflows and run-tests print a `PICKED:` line)

Decided by Jess Haley, 2026-10-25 [merge when green]: ("2. Yes") Claude merges the remaining PRs of this chain without asking each time (the stamp switch, the [generic stage is lossless] builds, the bin-B moves into dataset maps, and did-schema #128 once `decision_citations.py --pending --strict` reports 0), each when its CI is green with the corpus runs finished, DID-matlab before NDI-matlab.

Decided by Jess Haley, 2026-10-25 [partly placed is carried as v1]: ("3. A") when the generic migration can place some but not all of a v1 document's fields, it carries the whole document as v1 (stamped `did_v1`) and leaves the rest to that dataset's map; it does not write a V2 document with the leftover fields kept beside it. This is how [generic stage is lossless] is built.

Decided by Jess Haley, 2026-10-25 [sliceTetanus to Dab map]: ("4. Yes") `sliceTetanus` is the first bin-B move and the Dab workbook pilot: it comes out of the generic stage (NDI's second pass) into the Dabrowska dataset map, the generic stage carries those documents as v1, and the Dab corpus test checks that generic stage + map reproduces today's output. This follows [sliceTetanus stays in NDI], which held it in NDI's second pass until after the merge. Build pending: NDI-matlab (move into the Dabrowska map), DID-matlab (corpus test)

Decided by Jess Haley, 2026-10-25 [Soph paused]: ("Can we just stop running soph for now?") the Soph corpus leaves DID-matlab's corpus matrix and expected set (reported as paused, not measured, never as passed), and NDI-matlab's Soph end-to-end runs only by hand; each still runs on demand by bumping a token in its own workflow file. Built: DID-matlab 010de3b (#248, `tools/corpus_matrix.py` PAUSED), NDI-matlab e965787 (#1069, `test-eta-migrate-soph.yml`)

Decided by Jess Haley, 2026-10-25 [lossless first, homes after]: ("1. Yes") DID-matlab #247 and NDI-matlab #1067 merge now, though on real data they carry most tuning-calculator, image-stack and encounter-row documents as v1 (`carry_fields_TABLE.md` of the lossless build); V2 homes for the blocking fields follow class by class, and the carried counts fall as each lands.

Decided by Jess Haley, 2026-10-25 [hartley method implied]: ("3. Yes") `hartley_calc`'s `reverse_correlation.method` ("Hartley" in all 210 documents of 20211116) is implied by the calculation's method term and needs no field of its own; it no longer blocks the fold. Built: DID-matlab 0eee7ee (#247, `hartley_calc.m`)

Decided by Jess Haley, 2026-10-25 [schema set renamed did_v2]: ("rename to did_v2 after the lossless work") the V2 schema set now named `V_eta` (`schemas/V_eta/`, `index.json` `set_version`, the `TargetVersion` value in DID-matlab and NDI-matlab) is renamed `did_v2`, matching the document stamp ([document stamps]); done after the [generic stage is lossless] work lands, siblings first (accept both names, then rename here, then drop `V_eta`). Built (DID-matlab part): DID-matlab f6486be (#250). Built (NDI-matlab part): NDI-matlab 9b99061 (#1072). Built (did-schema part): did-schema 35f3447 (#132: `schemas/V_eta/` moved to `schemas/did_v2/`, `set_version` did_v2; retired classes, `notes` and the Markdown not moved). Build pending: did-schema, DID-matlab, NDI-matlab (after the lossless PRs)

Decided by Jess Haley, 2026-10-25 [pyramid type kept as text]: ("4d") a lightsheet pyramid's `pyramid_type` (the source store's NGFF `multiscales.type`, copied verbatim by NDI's `makePyramid`) is kept verbatim as free text in the store body's `description`, beside the NGFF multiscales name, as 'NGFF multiscales type "..."'; it is descriptive only (NDI's lightsheetZarrPyramid.md: an earlier writer labelled mean pyramids `gaussian`; the levels' `reduction_function` is the reliable value). This replaces the drop decided 2026-10-15 (Jess, DID-matlab `lightsheet_zarr_pyramid.m` header). Built: DID-matlab 0eee7ee (#247), NDI-matlab e0177b3 (#1067)

Decided by Jess Haley, 2026-10-25 [no-source pyramid carried as v1]: ("I'm inclined to say it should be carried as v1 ... Whatever you think is best practice for a general migration is fine"; recommended: carry as v1) a lightsheet pyramid with no source file has no store body to hold its NGFF name and type, so a pyramid stating either is carried whole as v1 ([partly placed is carried as v1]); no body is minted to hold text, and nothing more is written to free text. Not built: replaced the same day by [no-source pyramid gets a file-less store body].

Decided by Jess Haley, 2026-10-25 [one free-text field: notes]: ("one field - notes") V2 has ONE free-text field, named `notes`: `entity.description` and `data_body.description` become `notes`, beside the existing `statement.notes`. Free text is a last resort (Jess: "We don't want to encourage users filling this out. free text is worse than all the places a term can be added"); text the migration writes there keeps its labelled form (e.g. 'NGFF multiscales type "..."', [pyramid type kept as text]). A renamed field, so the writers and readers in DID-matlab and NDI-matlab change first, then the schema; done with [schema set renamed did_v2]. Build pending: DID-matlab, NDI-matlab, did-schema (with the did_v2 rename)

Decided by Jess Haley, 2026-10-25 [no-source pyramid gets a file-less store body]: ("Go with the file-less store body for pyramids") a lightsheet pyramid with no source file still gets its store body: an unheld `opaque_body` owned by the observation with NO file member (`data_body`'s `body_data` sets no minimum; `opaque_body` requires only `format`), its `format` read from the pyramid's `dtype` by the rule the store fold already uses (an NGFF typestring is OME-Zarr, else TIFF), and its description holding the NGFF multiscales name and type ([pyramid type kept as text]) and saying that the source store's location is not recorded. Recommended reading, not stated by Jess: every pyramid with no source file gets one, whether or not it states a name or type. Replaces [no-source pyramid carried as v1], which was not built. Built: DID-matlab 0eee7ee (#247, e1e3aee)

Decided by Jess Haley, 2026-10-25 [notes on three classes]: ("agreed with your notes recommendation", option (a)) the one free-text field `notes` ([one free-text field: notes]) is declared on `statement` (as today), `entity` and `data_body` only, where `description` is renamed `notes`; `interaction_purpose.comment` is also renamed `notes` if that class survives its naming review. No other class gains it, and `notes` is not put on `base`. The `label` fields are all on retired classes and are out of scope. Build pending: DID-matlab, NDI-matlab, did-schema (with [schema set renamed did_v2])

Decided by Jess Haley, 2026-10-25 [retired classes leave V2]: ("Your proposal makes sense. Record that"; replaces her earlier "move all retired classes to deprecated" the same day, which was not built) a class whose `disposition` is `retire` is deleted from the V2 schema set, and the `deprecated/` tier goes with it: retired v1 types are not V2 classes, and a `did_v1` document is not read against the V2 set (DID-matlab `did2.schema.cache`). The retired names stay in `tools/veta_record.py` so tools still recognise them. Order, siblings first: (1) the generic migration stops writing retired classes as V2 documents (at the locked DID head the generated targets show `element_epoch` -> `acquisition_epoch`, `daqreader_ndr` -> `daqreader`, `daqreader_mfdaq_epochdata_ingested` -> `daqreader_epochdata_ingested`): each is carried as v1 until it has a V2 home ([generic stage is lossless]); and the two in-progress classes that inherit retired `epochid` (`stimulus_presentation`, `daqmetadatareader_epochdata_ingested`) get a decision; (2) the DID-matlab and NDI-matlab workflows stop copying `deprecated/*.json`; (3) did-schema deletes the retired class files; (4) the generic migration's exception to [V2 builder refuses retired] is removed. After the lossless work. Build pending: DID-matlab, NDI-matlab, did-schema

Decided by Jess Haley, 2026-10-25 [v1 set in did-schema]: ("Yes, add it to the plan as a decision") did-schema will hold two schema sets, `did_v1` and `did_v2`, matching the document stamps ([document stamps]). The v1 definitions (NDI-matlab `main` `src/ndi/ndi_common/database_documents/` and `schema_documents/`) move into did-schema as a FROZEN `did_v1` set once NDI's V2 replaces v1 and v1 stops changing; what still reads v1 (the migration, opening old datasets) then reads it from did-schema. Not before: NDI `main` is what current users run, and until then the sibling lock already pins the v1 commit read. Done after [schema set renamed did_v2]. Build pending: did-schema, NDI-matlab, DID-matlab (after V2 replaces v1 in NDI)

Decided by Jess Haley, 2026-10-25 [markdown out of schemas]: ("Yes, you should move the markdown files as well. We should probably clean those up too and delete ones that aren't needed") in the same step as [schema set renamed did_v2], the Markdown files under `schemas/` (plan documents, notes, the old V_alpha..V_delta specs) move out to a documents folder, so `schemas/` holds only schema sets (`did_v2/`, and `did_v1/` per [v1 set in did-schema]); and they are cleaned up, deleting the ones not needed. Proposed (not decided): which to delete is a list Claude prepares and the team approves, and a document holding decision lines is kept or its lines moved, never lost. Build pending: did-schema (with the did_v2 rename; the tools that read `schemas/*.md` follow)

Decided by Jess Haley, 2026-10-25 [neuron derived from its sorting run]: ("a", drop census question 1) a v1 `element` (a sorted neuron) whose `jrclust_clusters_id` names a JRCLUST run keeps that link as a `directed_relation` `prov:wasDerivedFrom` from the neuron entity to the JRCLUST `calculation` (DID-matlab `jrclust_clusters.m` keeps the v1 id, so the element migrator writes it alone), beside its `derived_from` the electrode; it was dropped before (1,554 Soph and 21 20211116 elements, drop census). Built: DID-matlab f6486be (#250)

Decided by Jess Haley, 2026-10-25 [session membership records linked or ingested]: ("Yes, record both"; drop census question 2) a v1 `session_in_a_dataset` keeps what its dropped fields mean: the session `part_of` dataset relation's `method.term` says whether the session was INGESTED into the dataset or LINKED into it (`is_linked`; NDI `ndi.dataset` add_ingested_session / add_linked_session), and for a linked session `method.parameters` hold the opener class (`session_creator`) and its arguments, among them the session's path (`session_creator_input2`): where that session's data is stored. Inputs that only restate the session's reference or id are dropped as copies. Terms: an existing ontology term first, a new EMPTY term only if none fits (T19). Jess: the corpora cannot show this, since published datasets must be ingested first. Replaces the drop in `session_in_a_dataset.m` and the `linked_session` document of V_eta_linked_session_plan.md ([linked_session withdrawn], there). Built (DID-matlab part): DID-matlab f6486be (#250). Build pending: did-schema (terms), DID-matlab

Decided by Jess Haley, 2026-10-25 [dataset form terms]: ("b", drop census question 3) a v1 `metadata_editor`'s `ExperimentalApproach`, `TechniquesEmployed` and `DataType` are kept as term assertions about the dataset entity: experimental approach by the existing binding (EMPTY:0000356, the 40 openMINDS `experimentalApproach` terms, [term registry closed value sets]); techniques and data type by two new dataset bindings valued by openMINDS terms (technique; semantic data type). A form value that is not in the list carries the form whole as v1 rather than being dropped. Replaces their drop as "per-subject projections" in `metadata_editor.m`. Jess: nothing required a `metadata_editor` document on a published dataset, so the corpora (mostly published) show few. Built (schema part): did-schema 02e2980 (#131: Technique 227 / Scientific Data Type 4 bindings). Built (DID-matlab part): DID-matlab f6486be (#250). Build pending: did-schema (two bindings, terms), DID-matlab

Decided by Jess Haley, 2026-10-26 [presentation app is software]: ("a", drop census question 4) a v1 `stimulus_presentation`'s `app` block becomes a `software` entity referenced by the presentation manipulation's `software_id`, with the run's OS and interpreter in its execution environment, deduplicated like all other software: rule R1 (TEAM-SIGN-OFF [software]), as DID's `jSoftwareFromApp` places `app` everywhere else. NDI's `stimulusPresentationToItem` dropped it (1,428 presentations: 20211116 11, Dab 1,242, Soph 175, drop census). Built: NDI-matlab 9b99061 (#1072)

Decided by Jess Haley, 2026-10-26 [control selection on the presentation method]: ("b", drop census question 5) a v1 `control_stimulus_ids`'s `control_stimulus_id_method` (how controls were chosen: `method`, e.g. "pseudorandom" or Dab's "psuedorandom", verbatim; `controlid` with `controlid_value`, e.g. `isblank` = 1) becomes method parameters on the presentation's `manipulation`, and its `app` becomes a `software` entity (R1, as [presentation app is software]). A covariate entry has no method slot (`data_body` `covariates`), so the rule goes on the manipulation. Adds to [control as covariate] (2026-10-22), which did not name these two. Not built as decided: replaced the same day by [control pairing is a calculation].

Decided by Jess Haley, 2026-10-26 [lossless means round trip]: ("as long as the information is 100% recoverable, that is lossless. Consider, can V2 be migrated back to V1. If yes, it's lossless.") the test of [generic stage is lossless] is a round trip: a v1 value may be left unwritten only when it is 100% recoverable from what V2 keeps, so that the V2 documents could be migrated back to the v1 ones. A value that only restates another kept value passes; a value nothing else states does not.

Decided by Jess Haley, 2026-10-26 [hartley leftovers checked]: ("7a", drop census question 7) the `hartley_calc` migrator drops `stimulus_properties` only when its VALUES (not only its keys) equal the presentation's generator settings, and `dimension_labels` only when empty, as TEAM-SIGN-OFF [receptive field fold] (2026-08-17) says ("dropped only when equal"); otherwise the document is carried whole as v1. Today 210/210 are equal and empty (drop census). Built: DID-matlab f6486be (#250)

Decided by Jess Haley, 2026-10-26 [restated values checked]: ("8a", drop census question 8) values that only restate a kept value stay unwritten ([lossless means round trip]): `ngrid.data_size` (from the datum type), `neuron_extracellular` `number_of_samples_per_channel` / `number_of_channels` (the waveform's axis lengths), a calculator block's inner `depends_on` copy (the top-level edges), `daqreader_ndr.ndi_daqreader_ndr_class` (the reader class). Where the code does not yet check the equality (the inner `depends_on`, the NDR class) a check is added; when a check fails (these two, and the neuron counts, which quarantine today) the document is carried whole as v1. Built: DID-matlab f6486be (#250)

Decided by Jess Haley, 2026-10-26 [image file details placed]: ("b"; "yes, record it that way", drop census question 9) a v1 `image` / `imageStack` that becomes a data body keeps all four details it dropped: `format` and `compression` go into `data_body`'s `format` and `compression` fields; the `imageCollection_id` edge becomes a `member_of` relation to a group entity (T20); `data_limits` is left unwritten when it equals its data type's range ([intmin intmax] of the type, [0 1] for `logical`: every NDI `main` writer sets it so, and NDI's schema defines it as "The minimum and maximum value for that data type"), recoverable from the datum type ([lossless means round trip]), and is written as a "value range" condition on the body only when it differs. Replaces the drops in `image_stack.m` and `image.m`. Built (DID-matlab part): DID-matlab f6486be (#250). Build pending: did-schema (terms), DID-matlab

Decided by Jess Haley, 2026-10-26 [probe contact geometry carried]: ("10a", drop census question 10) a v1 `probe_geometry` that sets any of `shank_id`, the contact shape and its width / height / radius, `manufacturer`, `has_planar_contour` or the contour is carried whole as v1 until V2 has a contact-geometry model; `probe_geometry.m` dropped them as "still deferred". None is set in today's corpora. Built: DID-matlab f6486be (#250)

Decided by Jess Haley, 2026-10-26 [small unread settings]: ("a, record 12 that way"; 2-4 "ok", drop census question 12) (1) a v1 `sorting_parameters`, `spike_extraction_parameters(_modification)` or `vmspikefilteringparameters` whose `app` block names an OS or interpreter is carried whole as v1. That OS is where the settings were SAVED (NDI `ndi.app/newdocument` stamps every app document), not a property of the recipe: V2 puts a run's OS and interpreter on the CALCULATION (`operating_system_id`, `interpreter_id`), and `method` is NOT to gain OS or interpreter links on this account. (2) a filter's `sampleFrequency` becomes a method parameter; a fractional order, or a `label` that differs from its `type`, carries the filter as v1. (3) `syncrule` settings the migrator does not read (e.g. `errorOnFailure`) become method parameters; one that cannot be written carries the rule as v1. (4) an `element_epoch` whose `t0_t1` does not match its clocks, or is missing or not numeric, is carried as v1; this also removes the start-0/end-0 clocks `element_epoch.m` invents today ([no invented values]). None occurs in today's corpora. Built: DID-matlab f6486be (#250)

Decided by Jess Haley, 2026-10-26 [carry register]: ("yes", to Claude's proposal after "How do we generally prevent this issue from happening to all of the passthrough cases?") every reason the generic migration carries a v1 document whole as v1 is a row in ONE carry register in did-schema, so that a carry is never read as "V2 is missing a field". Each row names the v1 class and field, the decision tag, and its KIND: `awaiting_home` (V2 should model it; names the open-work row), `not_modelled` (V2 models it elsewhere or not at all, by design; carries a "do not" line, e.g. "do not add OS links to `method`: V2 records a run's environment on the calculation"), or `malformed` (input no writer produces). Enforced both ways: every carry note a migrator writes cites its register row, and a DID-matlab test fails on a carry whose reason is not registered (generalising NDI's `verifyDeferralsAreDeclared`); a did-schema gate fails when a class gains a field or edge a `not_modelled` row forbids, quoting the "do not" line. The done report lists carried documents by kind. Built: did-schema #134 (the register and its gate), DID-matlab 1f83af39 (PR #251) (cite rows; strict citation check), NDI-matlab 38adc701b (PR #1074) (cite rows; the test)

Decided by Jess Haley, 2026-10-26 [compression block and empty levels]: ("yes, record 11 that way", drop census question 11) (1) `data_body.compression` (today `char`, a codec name only) becomes a `{term, parameters}` block, the shape `method` uses: the codec as a term, its settings (e.g. Blosc's inner compressor, level, shuffle, block size) as parameters, so that no body loses its write-time settings; a light-sheet level's `codec_params` go there. A field type change, so DID-matlab and NDI-matlab readers and writers change first; until then a level whose settings go beyond the codec name is carried whole as v1 (carry register, `awaiting_home`). (2) a `lightsheetZarrLevel` holding no bytes becomes a file-less `sampled_body` that keeps the level's id, dimensions and metadata and says no bytes are stored, as [no-source pyramid gets a file-less store body]; this replaces #73 L3(c) ("A level holding NO bytes -> nothing"), which left edges to the level orphaned. None occurs in today's corpora. Built (DID-matlab part): DID-matlab f6486be (#250). Build pending: DID-matlab, NDI-matlab, did-schema

Decided by Jess Haley, 2026-10-26 [spelling is notation]: ("yes, record it that way", on drop census question 14a) (1) `source_unit` stays a bound term ([source unit], 2026-10-21), not free text: its job is to make `source_value` machine-readable. (2) The test of [lossless means round trip] reads: V2 can be migrated back to a v1 document that states the same things; equivalent spellings of one registered term ("Hz", "spikes/s" -> om:hertz) are the same thing, and everything else must be recoverable exactly. (3) The spellings a migrator maps to a registered term are recorded in the term registry as that term's known synonyms, so the mapping is documented and reversible as a set; an unrecognised spelling stays as the term's name with an empty node and is reported, as today. For `jResponseVariable` (tuning `response_units`, decisions [response variable], [dF/F as variable], [unstated response variable]) this keeps today's mapping and adds the synonyms. Build pending: did-schema (synonyms in the term registry), DID-matlab

Decided by Jess Haley, 2026-10-26 [Haley logic leaves the generic migration]: ("14b, this is haley import specific and shouldn't be here at all. I'm not worried about haley-specific migration since we already have the v2 reimport written") DID-matlab `did2.convert.resolveLawnPlateSubjects` (the JH lawn / plate subjects and the C. elegans patch relabel to `exp/<e>/plate/<p>/patch/<q>`) is Haley-import logic and is removed from the generic migration; the Haley dataset's V2 shape comes from its V2 re-import (`ndi.setup.conv.haley.import_V2`), and the generic stage carries what it cannot place as v1 ([generic stage is lossless]). Proposed (not decided): the other Haley-specific pieces the 2026-10-24 audit lists leave with it -- DID `ontology_table_row.m`'s patch-geometry map (audit B2) and NDI `imagedEntitySubjects`'s plate join (audit B6). Built (DID-matlab part): DID-matlab f6486be (#250). Built (NDI-matlab part): NDI-matlab 9b99061 (#1072). Build pending: DID-matlab, NDI-matlab

Decided by Jess Haley, 2026-10-26 [dataset-specific logic leaves the generic migration]: ("yes, all dataset-specific should move out of the generic migration") every piece of the generic migration (DID-matlab `did2.convert`, NDI-matlab `ndi.migrate.local` and its second pass) that encodes one dataset's meaning moves to that dataset's import or map; the generic stage places what it can by rules that hold for any dataset and carries the rest as v1. Known so far: DID `resolveLawnPlateSubjects` ([Haley logic leaves the generic migration]), DID `ontology_table_row.m`'s patch-geometry map (2026-10-24 audit B2), NDI `imagedEntitySubjects`'s plate join (audit B6), and NDI's Dabrowska slice chain (`sliceTetanus`; [sliceTetanus to Dab map]). The rest are found by an audit of both repositories, brought to the team as a list. Built (DID-matlab part): DID-matlab f6486be (#250). Built (NDI-matlab part): NDI-matlab 9b99061 (#1072). Build pending: DID-matlab, NDI-matlab (audit first)

Decided by Jess Haley, 2026-10-26 [site scaffolding not a loss]: ("14c. agreed on your 2 suggested points", drop census question 14c) (1) NDI `pathSPromotion` deleting the `Anatomic Site` observation is not a loss: DID's pass 1 (`treatment.m` and its siblings) mints that observation with a NEW id as scaffolding beside the manipulation, which keeps the v1 id; the region term survives on the region part the manipulation is retargeted to ([region parts]), so the v1 treatment is recoverable ([lossless means round trip]). (2) Open work, after the lossless builds: pass 1 writes the final shape directly (manipulation, region part entity, its anatomical-structure assertion, `part_of` relation, anchor), the part's id COMPUTED from the subject id, region term and side so that every document naming one region of one subject yields the same part, and the batch pass only merges identical copies; a side stated in a separate v1 document still needs the batch pass. DID has no computed ids today (a new convention). Build pending: DID-matlab, NDI-matlab (open work, after the lossless builds)

Decided by Jess Haley, 2026-10-26 [table rows into the dataset audit]: ("ok", drop census question 14d) NDI `ontologyRowSubjects` / `imagedEntitySubjects` and the DID per-table maps they call are taken up by the audit of [dataset-specific logic leaves the generic migration], which brings back: which per-table maps are dataset-specific; what a generic table row becomes (proposed: one statement per ontology-tagged column); and the `SubjectLocalIdentifier` label match (on by default, a "TEAM QUESTION" in the code with no decision), with counts of rows that rely on it. Build pending: DID-matlab, NDI-matlab (after that audit)

Decided by Jess Haley, 2026-10-26 [device clocks on one epoch]: ("mostly agreed", drop census questions 6 and 13, with her follow-up "the epoch gets two relative time references which link to each device entity?" -- yes) an epoch is ONE RECORDING, which may hold files from several acquisition systems (v1 NDI: each system's file navigator lists the epoch; with a per-folder navigator, systems reading one folder share the epoch id, e.g. Soph "t00001" on vhintan and vhvis_spike2). (1) One V2 epoch per recording (session + epoch id), as `epochMint` merges today. (2) Each system's extent is its own `relative_time_reference` on the epoch (`time_reference_id`), `value.clock` e.g. `dev_local_time`, its `referent_id` THAT ACQUISITION SYSTEM's entity -- not the session, as `epochMint` anchors today; the device entities gain nothing. (3) A v1 `syncrule_mapping` becomes a `clock_alignment` between those two references, so Soph's 348 non-identity mappings (e.g. scale 1.0000024, offset -4.33 s) and Dab's 2,484 identity mappings survive; its endpoint `objectname` / `objectclass` are left unwritten only when they equal the referent system, and `epochprobemap` only when it equals the epoch's manifest, else the mapping is carried as v1 ([lossless means round trip]). (4) Two sources disagreeing about ONE system's clock extent is malformed and carries the second as v1. Amends: the `recording epoch` entity type definition (binding registry, EMPTY:0000383) to "one recording: the files written for one stretch of time, by one or more acquisition systems"; and [time_reference uniqueness rule] (2026-09-30) so that one document's time references are unique by clock AND referent. To check in the build: that every acquisition epoch document can be tied to its acquisition system (an element epoch through its probe's device string, e.g. "vhvis_spike2:mk1"). Built (schema part, partly): did-schema 02e2980 (#131: recording epoch description; the clock-and-referent rule documented, machine-readable referent_unique_by waits for DID-matlab). Built (DID-matlab part): DID-matlab f6486be (#250). Build pending: did-schema (definition, uniqueness rule), DID-matlab (`epochMint`, `jClockAlignmentBodies`)

Decided by Jess Haley, 2026-10-26 [clock terms get nodes]: ("yes, add it to the plan") the four `value.clock` values of `relative_time_reference` (`utc`, `dev_local_time`, `dev_global_time`, `exp_global_time`; a closed, required list bound to `did_clocktype`) get real nodes: an existing ontology term where one fits, else EMPTY terms minted in empty-ontology (T19); today every node is "" ("STAGED EMPTY"). Done with the other term additions the drop census needs ([session membership records linked or ingested], [dataset form terms], [image file details placed]). Built (terms registered): empty-ontology 25188df (#26), did-schema 02e2980 (#131); the binding's value names wait for DID-matlab and NDI-matlab to compare nodes. Build pending: empty-ontology, did-schema (term registry, binding)

Decided by Jess Haley, 2026-10-26 [writer default is not set]: ("probe geometry question 1: answer a") a v1 field whose value equals the v1 writer's own fixed default counts as not set ([lossless means round trip]: the default is recoverable), so it does not by itself carry a document as v1. First case: `probe_geometry.has_planar_contour` (NDI template default 1, `fromStruct` writes 0), which today would carry every writer-shaped probe geometry under [probe contact geometry carried]. Each default relied on is cited to its NDI `main` writer. Built: DID-matlab f6486be (#250)

Decided by Jess Haley, 2026-10-26 [one correct reading]: ("record the general rule and the new register kind") the generic migration writes a V2 document only when the v1 document by itself, with rules that hold for every dataset, gives EXACTLY ONE correct V2 reading; a V2 document whose meaning might be wrong (e.g. a medium the worms live on written as a dose) is never written. When the v1 document admits several readings it is carried whole as v1 with a [carry register] row of the new kind `needs_mapping`: the row names the V2 home(s), what decides between them, and the dataset map entry that resolves it (e.g. "Babu: MICRO:0000480 -> exposure"), which the generic tools then apply, so a carry never reads as "V2 has no home". The register kinds are `awaiting_home`, `needs_mapping`, `not_modelled`, `malformed`. Answers already given are to be re-checked against this rule (Jess: "Does that change any other answers ... WE should double check"). Built (DID-matlab part): DID-matlab f6486be (#250). Build pending: did-schema (register kind), DID-matlab, NDI-matlab (re-check first)

Decided by Jess Haley, 2026-10-26 [run environment on interactions]: ("A. a") the two optional run-environment edges `operating_system_id` and `interpreter_id` (today on `calculation`, [calculation-os-optional]) move up to `interaction`, so a manipulation and an observation have them too: a v1 `stimulus_presentation`'s `app` OS and interpreter are the machine the stimulus program ran on, and become software entities on those edges (1,428 presentations, drop census). Not for `method` ([small unread settings]). Built: did-schema 02e2980 (#131), NDI-matlab 9b99061 (#1072)

Decided by Jess Haley, 2026-10-26 [control pairing is a calculation]: ("yes, record the control record that way", after her question whether the control is "truly calculated after the manipulation") which stimuli are controls is a stimulus parameter known before stimulation (default `isblank` = 1, already on the V2 stimulus `method` documents); what NDI's `tuning_response` `control_stimulus` computes afterwards is the PAIRING of each presented stimulus with its control trial, by a rule (default "pseudorandom": the `controlid` stimulus in the same repetition; NDI-matlab main `+app/+stimulus/tuning_response.m` 551-658). A v1 `control_stimulus_ids` therefore becomes a `calculation` about the presentation: software `ndi_app_tuning_response` (from its `app`), method = the pairing rule (`control_stimulus_id_method`: method, controlid, controlid_value, verbatim), value = the per-trial pairing. Replaces [control selection on the presentation method] (the rule is that program's setting, not the presentation's) and amends [control as covariate]: the per-trial pairing is kept, not dropped; the `control condition` covariate may stay as a convenience (recoverable from `isblank`). Built (NDI-matlab part): NDI-matlab 9b99061 (#1072). Build pending: NDI-matlab (`local.m` control fold), did-schema (terms if needed)

Decided by Jess Haley, 2026-10-26 [census terms]: ("T1 yes, T2 b, T3 yes, T4 yes"; proposal `docs/v2_working/TERMS_PROPOSAL.md`, Claude, 2026-10-26) T1: two new EMPTY terms "database ingestion" and "database linking" for the session membership method ([session membership records linked or ingested]); a linked session's path is NCIT:C47922 Pathname; its opener class is a new EMPTY "software class". T2: the dataset form variables are NCIT:C16847 Technique and NCIT:C175886 Scientific Data Type ([dataset form terms]); their values are openMINDS controlled terms identified by openMINDS's own stable ids under a newly registered `openminds:` prefix (no EMPTY minting; 227 techniques, 4 semantic data types; Soph's "derivedData" is openMINDS semanticDataType derivedData). T3: a new EMPTY "value range" for [image file details placed] (NCIT:C38013 Range leads with a single difference). T4: the clock values get nodes ([clock terms get nodes]): `utc` -> wikidata:Q1536; new EMPTY "device local time", "device global time", "experiment global time" (definitions from NDI `clocktype.m`); the stored name becomes the term label, so DID-matlab and NDI-matlab compare clock nodes first before the schema changes. Built (the terms): empty-ontology 25188df (#26: EMPTY:0000399 database ingestion, 0000400 database linking, 0000401 software class, 0000402 value range, 0000403-0000405 the three clocks), did-schema 02e2980 (#131: `openminds:` prefix, registry rows, bindings). Built (DID-matlab part): DID-matlab f6486be (#250). Build pending: empty-ontology (7 EMPTY terms), did-schema (prefix, registry rows, bindings), DID-matlab, NDI-matlab

Decided by Jess Haley, 2026-10-26 [dataset audit batch 1 and 2]: ("yes to haley and babu"; "yes to all 3"; dataset-specific audit `docs/v2_working/DATASET_SPECIFIC_AUDIT.md`) under [dataset-specific logic leaves the generic migration] and [one correct reading]: (1) the Haley worm-track shapes (`resolveEpochProbemap.m` position/distance cases, stemKey, endpoint B, pixel frame) leave the generic migration -- such epochs stay plain acquisition epochs or carry as v1, and the Haley V2 import makes the tracks; this supersedes [JH position and distance] and [JH build choices] for the generic stage; (2) the Babu media/air/heat routing (`jTreatmentRoute.m` isMedium, `treatment_drug.m` isHeatOnly) leaves; those rows carry as v1 with a `needs_mapping` row naming exposure / temperature manipulation, superseding [babu-media] for the generic stage; (3) `ontologyRowSubjects` is built to match [subject local identifier is an identifier] (the document id wins when routes disagree), keeping the local-identifier label match (Dabrowska's only route); (4) table columns and `treatment` rows whose kind, direction or unit is chosen from label words carry as v1 with `needs_mapping` rows instead of a guessed reading; (5) NDI `imagedEntitySubjects` is retired. Built (DID-matlab part): DID-matlab f6486be (#250). Built (NDI-matlab part): NDI-matlab 9b99061 (#1072). Build pending: DID-matlab, NDI-matlab

Decided by Jess Haley, 2026-10-26 [term-stated unit is generic]: ("sure if the term lists a unit, we can derive the unit explicitly") when a term's definition states the unit its accompanying number takes, the generic migration derives that unit for any dataset: the unit is stated on the term's row in the term registry (not in migrator code), and a migrator reads it from there. First case: EMPTY:0000199 "treatment: grating direction-of-motion visual stimulation", defined "... (provided in hours)" (DID-matlab `treatment.m` termNumberKind). The v1 schema does not state it (NDI `treatment_schema.json`: numeric_value "The numeric value associated with a treatment"). Supersedes [termNumberKind is per-dataset]. Built (schema part): did-schema 02e2980 (#131: registry `number_unit`, rule R12; EMPTY:0000199 = om:hour). Built: DID-matlab f6486be (#250), did-schema 02e2980 (#131)

Decided by Jess Haley, 2026-10-26 [software_id is what produced the statement]: ("1 yes", after she found separate "recorded by" links duplicative) an interaction's `software_id` means one thing everywhere: the software that PRODUCED this statement -- for a calculation the program that computed it, for an acquired observation the program that acquired it, for a decoded stimulus presentation the decoder that produced the playlist from the stimulus files (NDI-matlab main `decoder.m` 135-137 stamps its `app`). The run-environment edges ([run environment on interactions]) describe that same run. So [presentation app is software] and [run environment on interactions] stand, read as "the program that produced the record" (not "the program that presented the stimulus"); no new links. A settings document's saved-on OS stays carried as v1 ([small unread settings] (1)). Built: did-schema 02e2980 (#131), NDI-matlab 9b99061 (#1072)

Decided by Jess Haley, 2026-10-26 [stimulus_presentation retired]: ("2a retire") `stimulus_presentation` (stable/, in_progress, superclasses base/app/epochid) is a v1 shape, not a V2 class: its V2 form is the decided decomposition (a `manipulation` with value kind `item` plus `method` documents, NDI second pass). Its disposition becomes `retire`; DID's pass 1 carries a v1 `stimulus_presentation` unchanged as v1 ([passthrough stays v1]) and NDI's second pass reads the v1 document. Removes one of the two in-progress inheritors of retired `epochid` ([retired classes leave V2]). Built (schema part): did-schema 02e2980 (#131: disposition retire). Built (DID-matlab part): DID-matlab f6486be (#250). Build pending: did-schema (disposition), DID-matlab, NDI-matlab

Decided by Jess Haley, 2026-10-26 [ingested stimulus file is a body of the presentation]: ("2b i") a v1 `daqmetadatareader_epochdata_ingested` (NDI-matlab main `+daq/metadatareader.m` ingest_epochfiles 126-145: the stored copy of an epoch's stimulus file, e.g. NewStim `stims.mat` read by `ndi.daq.metadatareader.NewStimStims`, as compressed `data.bin`, with the epoch id and a `daqmetadatareader_id` edge; Dab 1,242, Soph 175, 20211116 0 held) becomes an `opaque_body` owned by that epoch's stimulus-presentation `manipulation` (the raw source the playlist was decoded from), joined by session and epoch id in NDI's second pass; with no matching presentation it is carried as v1. Its class disposition becomes `retire`, the second in-progress inheritor of retired `epochid` ([retired classes leave V2]). Built (schema part): did-schema 02e2980 (#131: disposition retire). Built (DID-matlab part): DID-matlab f6486be (#250). Built (NDI-matlab part): NDI-matlab 9b99061 (#1072). Build pending: did-schema (disposition), NDI-matlab, DID-matlab (pass 1 carries it as v1 for the second pass)

Decided by Jess Haley, 2026-10-26 [one-reading quick answers]: ("Q1–Q5 yes"; one-reading review `docs/v2_working/ONE_READING_REVIEW.md`) (Q1) a treatment with no recorded location, or a non-body location, is carried as v1 instead of becoming a dose with a NaN amount; (Q2) a `treatment_transfer` with no clock type, or a bath epoch with no clock record, is carried as v1 instead of defaulting to `dev_local_time` ([no invented values]), and a global-clock time is written in its true unit (NDI stores days, not seconds); (Q3) JH `imageStack` / `ontologyLabel` readings chosen from label words (mask or map detection, every label as an observation) carry as `needs_mapping` ([one correct reading]); (Q4) the Dab treatment name "Optogenetic Tetanus Stimulation Target Location" is kept unchanged (the fold no longer strips "Target Location"), and its term EMPTY:0000074 is registered in the term registry; (Q5) a `jrclust_clusters` with an `ndi_document.name` (e.g. "jrclust.prm") stays carried as v1 until it has a home. Built (schema part): did-schema 02e2980 (#131: EMPTY:0000074 registered). Built (DID-matlab part): DID-matlab f6486be (#250). Build pending: DID-matlab, did-schema (EMPTY:0000074 row)

Decided by Jess Haley, 2026-10-26 [carry register kinds]: ("That's fine", to the 13 carry register rows whose kind Claude read from their decision lines, listed on did-schema PR #134, and to filing OPEN_WORK rows for the `awaiting_home` rows that had none) the kinds stand as read: `malformed` for carry-006 (`filter`, fractional order), carry-008 (`syncrule`, a setting that cannot be written), carry-009 (`element_epoch`, `t0_t1` not matching its clocks, missing or not numeric), carry-014 (`hartley_calc`, `stimulus_properties` differing from the generator settings), carry-016 (`calculator`, the inner `depends_on` copy differing), carry-017 (`daqreader_ndr`, the reader class differing from the reader string), carry-018 (`neuron_extracellular`, counts differing from the waveform) and carry-019 (`lightsheetZarrPyramid`, no source file and no dtype); `awaiting_home` for carry-007 (`filter.label`), carry-011 and carry-012 (`image` / `imageStack` `data_limits`), carry-013 (`imageStack` `imageCollection_id`) and carry-015 (`hartley_calc.dimension_labels`). The register marks them `kind_basis: decided`. OPEN_WORK #130 (carry-001, issue #135), #131 (carry-007, issue #136) and #132 (carry-010, issue #137) are filed.

Decided by Jess Haley, 2026-10-26 [awaiting home is tracked]: ("Yes, you can file those"; "You can make the register check fail when missing the open work entry") every `awaiting_home` row of the carry register names an OPEN_WORK row, and `tools/check_carry_register.py` FAILS a row with none, or whose row is not in the "## OPEN" section of `V_eta_OPEN_WORK.md` (C5), instead of listing it. The four rows that had none got OPEN_WORK #133 (carry-011, carry-012; issue #138), #134 (carry-013; issue #139) and #135 (carry-015; issue #140).

Decided by Jess Haley, 2026-10-26 [dataset map edits V2]: ("b", to Claude's question whether a dataset map (a) only converts documents the generic stage carried as v1, or (b) may also edit V2 documents the generic stage wrote) a dataset map runs AFTER the generic migration, which stays dataset-free and converts every document that has one correct reading exactly as today; the map then adds what only that dataset knows, and may change V2 documents the generic stage wrote (e.g. Dab: mint the slices, add the tetanus runs, move the baths and statements from the animal to its slice, drop the before/after labels), as well as convert carried v1 documents. Every change comes from a map row that cites the decision behind it. Build pending: NDI-matlab (the map step and the Dab map, [sliceTetanus to Dab map])

Decided by Jess Haley, 2026-10-26 [dataset map location]: ("i think your map plan sounds good", to Claude's proposal `docs/v2_working/DATASET_MAP_PROPOSAL.md`, option C) each dataset's map is one file in NDI-matlab, beside that dataset's importer and decision log, and is applied by its own step after the generic migration has written the V2 database, so a map can be re-run after an edit without migrating again; the generic second pass gets no dataset slots. Build pending: NDI-matlab (the map step, the Dab map)

Decided by Jess Haley, 2026-10-26 [no Haley map]: ("a", to Claude's question whether the Haley dataset needs a dataset map) Haley gets no dataset map: its V2 data comes from the Haley V2 import, which reads the source data, not the v1 documents ([Haley logic leaves the generic migration]). A generic migration of Haley's v1 documents may carry some of them, and nothing resolves those carries.

Decided by Jess Haley, 2026-10-26 [map rows match exact values]: ("A", to Claude's question whether a dataset map row may match on words in a label or only on exact v1 values) a dataset map row matches only exact v1 values (a term node, a class, a field value); it never matches on words in a label. A document no row matches exactly stays as the generic migration left it. Build pending: NDI-matlab (the map step)

Decided by Jess Haley, 2026-10-26 [opto target without a run]: ("B", to Claude's question what the Dab map does with an animal that has an "Optogenetic Tetanus Stimulation Target Location" treatment (EMPTY:0000074) but no tetanus run found in its recordings) the Dab map records the stated target as a term assertion on the animal ("its stimulation target was region X"), claiming no stimulation; today's `sliceTetanus` keeps the old manipulation on the animal instead (its `treatment_manipulations_kept_no_run` count). Build pending: NDI-matlab (the Dab map)

Decided by Jess Haley, 2026-10-26 [fraction value kind]: ("yes, add fraction", after asking "Why fraction instead of score?") V2 gains a `fraction` value kind for a part of a whole (e.g. the share of a test's time spent in an arm). Its canonical value is a plain ratio, 1 = the whole, in `om:one`; a percent is kept losslessly as `source_value` with `source_unit` `om:percent`. It is not a `score`: a score is a rating on a named rubric (`scale`, `scale_min`, `scale_max`), a fraction is a ratio that means the same in every dataset. Built: did-schema `schemas/did_v2/draft/fraction.json` (this commit)

Decided by Jess Haley, 2026-10-26 [migrators read raw v1]: ("yes, record both", after "What's the best design for a migrator? I feel like it's c") a migrator reads v1 exactly as v1 defines it (the NDI template and writer at the locked `main`), writes V2 only through the builder, and accounts for every v1 field; what is truly shared (`depends_on`, the `base` and `app` blocks, the stamp) becomes reading helpers each migrator calls on the raw v1 document, not a pass that rewrites it. Migrators switch one at a time, each with a check that every v1 template field is accounted for; `did2.convert.universalRenames` is deleted once the last one has switched; one full corpus run at the end, batched with the other sibling renames. OPEN_WORK #136. Partly built: DID-matlab e73aec7 (PR #253) (the helpers `+did2/+convert/+v1read/` and `+did2/+convert/+migrators_j/private/jRawBody.m`, `jRawAccount.m`, `jRawCarry.m`; 72 of the 95 `+migrators_j` migrators read raw v1, listed in `+did2/+convert/rawV1Classes.m`, each with a round trip); DID-matlab 6bfbb25 (PR #255) (contrast_tuning, spatial_frequency_tuning, temporal_frequency_tuning, speed_tuning: 76 of 95); DID-matlab dfd73b6 (PR #256) (pyraview: 77 of 95); DID-matlab 63c1ba1 (PR #257) (file_reference, lightsheet_zarr_level, lightsheet_zarr_pyramid: 80 of 95). Build pending: DID-matlab (switch the other 15: binnedspikeratevm, control_stimulus_ids, dataset_session_info, fitcurve, image, ontology_table_row, openminds, openminds_element, openminds_stimulus, openminds_subject, simple_calc, spike_clusters, spikewaves, vmspikefilteringparameters, vmspikefit; reasons in `rawV1Classes.m` NOT LISTED and PR #253 "Not switched"; then delete `universalRenames`, still called at `v1_to_v2.m:391` and `:1271`; then the one full corpus run)

Decided by Jess Haley, 2026-10-26 [renames carry is temporary]: ("yes, record both") the carry "universalRenames would discard" ends with [migrators read raw v1]: until the pass is deleted it is one carry register row for any class (`v1_class` `*`, carry-049, awaiting_home on OPEN_WORK #136), removed when the pass is deleted; a collision a raw-v1 migrator still meets becomes a class-specific row. Built: did-schema (carry-049; `check_carry_register.py` accepts `*`, this commit). Build pending: DID-matlab (at e73aec7 a collision a raw-v1 migrator meets still cites carry-049, `+did2/+convert/+migrators_j/private/jRawCarry.m:11-13`, not a class-specific row; `universalRenames` still runs for the 23 classes not switched), did-schema (remove carry-049 when `universalRenames` is deleted)

Decided by Jess Haley, 2026-10-26 [early migration pieces fixed]: ("I think we should fix all of these", to Claude's list of migration pieces from early V2 development) (1) superclass migrators and the old `+migrators` generation go: one migrator per class (with [migrators read raw v1]), and a class with no migrator is a recorded decision, not an identity fallback; (2) `ensureClassBlocks` padding goes: the builder produces a complete document; (3) the `TermRegistry` strict check stays on during migration (DID-matlab `v1_to_v2.m`, `epochMint.m`), an unregistered term becoming a carry with a register row or a registry row; (4) "already converted" is a stamp check (`did_v1` / `did_v2`), not a rank against `V_eta`; (5) element name and reference are stored reversibly (OPEN_WORK #142; NDI `+vintage/elementFields.m` packs them as '%s (ref %s)'); (6) the uncalled `resolveLawnPlateSubjects` and its mentions are deleted from DID-matlab ([dataset-specific logic leaves the generic migration]). Built: DID-matlab 1f83af39 (PR #251) (4: `+did2/+convert/isAlreadyTarget.m`, commit 00a87879; 6: `resolveLawnPlateSubjects` deleted, commit ad66d7bc). Partly built: DID-matlab e73aec7 (PR #253) (1: the 72 classes in `rawV1Classes.m` run one migrator each, with no superclass migrator; old `+migrators` wrappers nothing reached are deleted). Build pending: DID-matlab (1: the 23 classes not switched still reach `+did2/+convert/+migrators/` (`element_epoch`, `epochclocktimes`, `filter`, `ngrid`, and the `identity` fallback, `v1_to_v2.m:124`) and `+did2/+convert/+migrators_j/+super/` (`image_stack_parameters`, `ngrid`); 2: `ensureClassBlocks` still pads every converted body, `v1_to_v2.m:507`; 3: `TermRegistry` is still off during migration, `v1_to_v2.m:159`, `epochMint.m:396`), NDI-matlab (5), did-schema (5: the schema shape, once decided)

Decided by Jess Haley, 2026-10-26 [migration reliability practices]: ("Do all 4", to Claude's proposal) (a) a round-trip check per class: each converted document is migrated back to v1 and compared with its source, built with each class's switch to raw v1 ([migrators read raw v1]); (b) deterministic ids: a document the migration mints gets an id derived from its v1 source id and its role, so two runs on the same input are identical and can be diffed; (c) whole-dataset passes (DID-matlab `resolve*` post-passes, NDI-matlab's second pass) declare what they read and write, and their order is derived and checked, not kept in comments; (d) the migration report counts carries by carry register row, with its denominator. Partly built: DID-matlab 1f83af39 (PR #251) (b: `+did2/+convert/mintId.m`), e73aec7 (PR #253) (a: `+did2/+convert/+roundtrip/<class>.m` and `roundtrip.check` for the 72 classes that read raw v1, 22 `testRawV1RoundTrip<Family>` suites; b: `+did2/+convert/mintKey.m`, a document with no `base` block). Build pending: DID-matlab (a: the 23 classes not switched; b: ids are still random where a source states no id, `did.ido.unique_id()` at `mintId.m:83` and `:102`, `resolveEpochProbemap.m:1574`, `resolveOpenmindsCitations.m:1028`, `+did2/+convert/+migrators_j/private/jDatasetId.m:17`, `pyraview.m:97`, `image_stack.m:346`, `jrclust_clusters.m:107`; c; d), NDI-matlab (c, d)

Decided by Jess Haley, 2026-10-26 [carry register kinds 2]: ("1 yes", to Claude's list of the kinds it proposed for carry register rows carry-027 to carry-048 and carry-050 to carry-056) those kinds stand as proposed; the register marks them `kind_basis: decided`. (carry-034, `subject_group`, is reworded by the answer on unnamed groups.)

Decided by Jess Haley, 2026-10-26 [unnamed groups named by the map]: ("1. Yes", after "The local id is basically the user facing name. Each entity including groups should probably be required to have a user facing name, right?"; replaces her earlier "2 b") the `Group` entity type keeps requiring a `local_identifier`, its user-facing name; a v1 `subject_group` states none (NDI's template block is empty), so the generic migration carries it whole as v1 (DID-matlab `subject_group.m`, unchanged) as a `needs_mapping` carry (carry-034), and the dataset map gives the group its name, after which it converts with its `member_of` edges. Nothing is filled in by the generic stage: not a generated handle, not the document id ([no invented values]). Checked at the same time: every one of the 19 entity types already requires a user-facing name, `local_identifier` (dataset-local: organism, culture, tissue, cell, Group, device, material entity, Session, recording epoch) or `name` (shared: the other ten) (`binding_registry_meta.json` `entity_type_bindings`). Build pending: NDI-matlab (the dataset maps that name groups)

Decided by Jess Haley, 2026-10-26 [vehicle rate needs a map]: ("1 a") a v1 `treatment_drug` vehicle row whose amount is per body mass (e.g. saline "1 mg/kg", a writer placeholder; DID-matlab `jDoseValue.m`) is carried as v1, `needs_mapping` (carry-057): the dataset map says what was given. Build pending: NDI-matlab (the dataset maps)

Decided by Jess Haley, 2026-10-26 [second measurement value needs a map]: ("2 a") a v1 `measurement` or `subjectmeasurement` holding more than one value, or a string beside its number, is carried as v1, `needs_mapping` (carry-058, carry-059): what the second value means is the dataset's. Build pending: NDI-matlab (the dataset maps)

Decided by Jess Haley, 2026-10-26 [ingested session membership]: ("1. Yes", to Claude's proposal) for an INGESTED session, a v1 `session_in_a_dataset`'s `session_reference` is dropped when it equals the session entity's `local_identifier` (recoverable from it), and the creator class becomes a parameter of the "database ingestion" method on the session's `part_of` relation ([session membership records linked or ingested]); when `session_reference` differs, the document is carried as v1, `needs_mapping` (carry-060). Built: DID-matlab 1f83af39 (PR #251) (`jMembershipBodies.m`)

Decided by Jess Haley, 2026-10-26 [data_limits not a pair is malformed]: ("2. A") a valid `data_limits` [min max] pair is written as a value range ([image file details placed]), so carry-011 and carry-012 now catch only a `data_limits` that is not a finite [min max] pair: they become `malformed`, and OPEN_WORK #133 is completed.

Decided by Jess Haley, 2026-10-26 [pass-through filter sample frequency]: ("2. A", conditional on Claude checking that the body's own sample rate always matches) the `sampleFrequency` an all-pass pyraview filter states is not carried when it equals the pyraview's `native_rate`, which the V2 body keeps (`dt = 1/native_rate`): it is recoverable from it. Checked: NDI's writer sets both from one variable (NDI-matlab main `+gui/+app/+pyraview/makePyraviewDoc.m:53` `sr = probe.samplerate(epochid)`, `:58` `filterData([0], sr, filterband)`, `:157` `pyraviewStruct.nativeRate = sr`; `filterData.m:37` `sampleFrequency`, sr). A value that differs is carried as v1, `malformed` (carry-061). Built: DID-matlab 1f83af39 (PR #251) (`jFrequencyFilter.m`, `pyraview.m`)

Decided by Jess Haley, 2026-10-26 [untied epochs keep the session anchor]: ("2. Yes", to Claude's option under [device clocks on one epoch]) an element epoch that cannot be tied to an acquisition system (e.g. 20211116, which holds no epochprobemap: 0 of 252 tied) is not carried when all of its extents come from one untied source and agree: it keeps a session-anchored time reference, using only the times the epoch states. Extents that come from several sources, or disagree, still carry it. Built: DID-matlab 1f83af39 (PR #251) (`epochMint`), NDI-matlab d88ea6cfb (PR #1075, its test)

Decided by Jess Haley, 2026-10-26 [sorted units are cells or groups]: ("A'", after asking whether the source of sorted spikes is cells, a recording unit or tissue) a sorted unit (v1 `element` of type `spikes`) is an entity derived from its electrode and its sorting run ([neuron derived from its sorting run]): a SINGLE unit is a `cell`; a MULTI-unit cluster is a `Group` of cells whose members are not identified (no `member_of` rows; its local_identifier is the unit's name). Whether it is single or multi is an assertion by the sorting run, so a re-sort changes an assertion, not what the entity is. The raw recording stays an observation of the specimen with the electrode as instrument (TEAM-SIGN-OFF [raw recording observation]); tissue is where the cells are (`part_of` / located in), not the source of a sorted spike train. A unit with no single/multi label is not decided here. Built: DID-matlab e73aec7 (PR #253) (`+did2/+convert/+migrators_j/element.m` `elementEntityType`, `:333-348`)

Decided by Jess Haley, 2026-10-26 [unlabelled units need a map]: ("1. A") a sorted unit with no single/multi label (198 in the corpora: 134 Dab, 64 Soph, `scratchpad/elemtypes` census) is carried as v1, `needs_mapping` (carry-062): the dataset map says single or multi. Built: DID-matlab e73aec7 (PR #253) (`+did2/+convert/+migrators_j/element.m:344`, carry-062)

Decided by Jess Haley, 2026-10-26 [element types have no default]: ("yes, draft the element type list"; "2. Yes"; "2a") an element's entity type comes from a fixed list of element types whose meaning NDI fixes, with NO default (today's `otherwise -> device` in DID-matlab `element.m` `elementEntityType` goes). A registered probe type (NDI `probetype2object.json`) is a `device` ONLY when the element's `ndi_element_class` is `ndi.probe.*`; a derived element that copies its probe's type (NDI `oneepoch.m:63-64`, `downsample.m:41-44`) is not. `spikes`, `neuron` and `cell` are sorted units ([sorted units are cells or groups]); `ensemble` is a `Group`. Any other type, or a probe type on a non-probe class, is carried as v1, `needs_mapping` (carry-063). The full list is the draft `docs/v2_working/ELEMENT_TYPES_DRAFT.md` (Proposed, not decided) until its open questions are answered. Built: DID-matlab e73aec7 (PR #253) (`+did2/+convert/+migrators_j/element.m` `elementEntityType`, `:305`; no default, `:349` carries any other type under carry-063)

Decided by Jess Haley, 2026-10-26 [dependents of a carried document carry]: ("1A") a document whose edge points at a document carried as v1 (e.g. an `element_epoch`, `position_metadata` or spike train of a carried element) is carried too, down the chain, rather than converting with an edge to a v1 document (carry-064, any class). Built: DID-matlab e73aec7 (PR #253) (`+did2/+convert/v1_to_v2.m` `carryDependents`, `:1226`). Partly built: NDI-matlab 38adc701b (PR #1074) (a second-pass record blocked by a document carried as v1 counts under carry-064: `+ndi/+migrate/+internal/carryUnchangedAsV1.m:181`, `ontologyLabelSubjects.m:235`, `strainAssembly.m:309`, the control records in `+ndi/+migrate/local.m:2924`). Build pending: NDI-matlab (that every second-pass output whose edge names a document carried as v1 is carried too is not shown at 675742fe7: the code above counts the cases those steps record)

Decided by Jess Haley, 2026-10-26 [electrode spellings and imaging types are devices]: ("1 a", "2a") on an element whose `ndi_element_class` is `ndi.probe.*` ([element types have no default]): (1) the spelled-out electrode forms (`electrode-<spec>`, `<prefix>_electrode-<spec>`, e.g. `electrode-4`, `extracellular_electrode-4`) map to `device`, like the registered key `electrode-$`, though NDI's `probestruct2probe` accepts only exact keys; (2) NDI's four imaging element types (`docs/v2_working/ELEMENT_TYPES_DRAFT.md`) map to `device`: the camera or microscope is the instrument and the image data is an observation made with it. Built: DID-matlab e73aec7 (PR #253) (`+did2/+convert/+migrators_j/element.m` `elementEntityType`: `:322` the electrode spellings, `:317-321` the four imaging types, `device` only on `ndi.probe.*` `:323-325`)

Decided by Jess Haley, 2026-10-26 [event lines and environment probes are devices]: ("1a", "2a") on an `ndi.probe.*` class ([element types have no default]): an `event` element (a sync or trigger line, NDI's stimulator probe class) is a `device`, its pulses observations made with it; the environment probes `lick-spout`, `reward-well` and `intraoral-cannula` are `device`s (apparatus). Built: DID-matlab e73aec7 (PR #253) (`+did2/+convert/+migrators_j/element.m` `elementEntityType`, `:317-321`: `event`, `lick-spout`, `reward-well`, `intraoral-cannula`)

Decided by Jess Haley, 2026-10-26 [migrator writes the registry spelling]: ("1a. Though I think maybe it's worth revisiting") the migrator writes an entity type exactly as the registry names it (`Group`, NCIT:C43359), not `group`. Open: whether NDI terms should be standardised to lower case (unless proper nouns) — as presentation only, or as an `ndi_name` registry column beside the ontology label (Proposed, not decided; `docs/V2_PLAN.md`). Build pending: DID-matlab (`element.m`, `subject_group.m`)

Decided by Jess Haley, 2026-10-26 [location carries need a map]: ("2. A") carry-023 and carry-024 (a treatment with no recorded location, or a location that is not an UBERON body site) are `needs_mapping`, now confirmed (their decision line, [one-reading quick answers] Q1, says only "carried as v1"); the register marks them `kind_basis: decided`.

Decided by Jess Haley, 2026-10-26 [presentation outside the batch needs a map]: ("3 b") a v1 `hartley_calc` whose presentation is not in the migrated batch is carried as `needs_mapping` (carry-065), not `malformed`: the document is sound and its presentation is elsewhere. carry-040 keeps the inputs that are malformed in themselves.

Decided by Jess Haley, 2026-10-26 [missing is_linked is malformed]: ("4 a") a v1 `session_in_a_dataset` with an empty `is_linked` is carried as `malformed` (carry-066): NDI's template leaves it empty (`session_in_a_dataset.json:16`, `"is_linked": []`) and its writer always sets it (`ndi.dataset` `dataset.m:92` `= 1` linked, `:170` `= 0` ingested), so a missing flag is not writer-shaped and a default would be invented. Built: DID-matlab 1f83af39 (PR #251) (`jMembershipBodies.m`)

Decided by Jess Haley, 2026-10-26 [term labels stay as the ontology spells them]: ("Record the capitalization decision as you proposed", after asking what the genuinely better practice is) a term is identified by its node, never its label; the registry stores each term's label exactly as its source ontology spells it, so it can be checked and refreshed against the ontology (NCIT title-cases, e.g. `Group`; OBO ontologies use lower case); EMPTY's own terms follow the OBO convention, lower case except proper nouns and acronyms; any lower-casing for consistency is done where labels are DISPLAYED, never in what is stored. This settles the question [migrator writes the registry spelling] left open.

Decided by Jess Haley, 2026-10-26 [element local identifier is name and reference]: ("5 yes") a migrated element's `local_identifier` is NDI's own display form `<name> | <reference>` (NDI-matlab main `+ndi/element.m:341`, `[ndi_element_obj.name ' | ' int2str(ndi_element_obj.reference)]`), e.g. `leftcortex | 2`; the name alone is not unique (Soph holds `leftcortex` n-trodes with references 1, 2 and 3; 122 (name, type) pairs in Soph and 6 in Dab have more than one reference, census of the corpus zips, 2026-10-26). It is reversible: the reference is an integer, so splitting at the last ` | ` recovers both. Replaces the unescaped `'%s (ref %s)'` packing (OPEN_WORK #142). Built: DID-matlab e73aec7 (PR #253) (`+did2/+convert/+migrators_j/element.m:158`, `did2.convert.elementLocalIdentifier`). Built: NDI-matlab 4effe11e0 (PR #1076) (`+vintage/elementLocalIdentifier.m`, `elementNameReference.m`, `elementFields.m`, `elementDoc.m`; the old `(ref X)` form still reads)

Decided by Jess Haley, 2026-10-26 [bath is two statements]: ("6 yes do both") a v1 bath record makes (1) in the generic stage, a manipulation "the subject sat in this solution": variable a general bath-solution term, value the whole formulation, written for every bath, and (2) in the dataset map, a separate manipulation of the ingredient that was really changed (e.g. Dab's 131 antagonist changes among its 1,172 ACSF baths), its variable that ingredient. The variable is no longer the first mixture row (e.g. "sodium chloride"). Build pending: DID-matlab (the bath variable; term registry row for the general term), NDI-matlab (the Dab map)

Decided by Jess Haley, 2026-10-26 [chooseLevel skips empty levels]: ("7 a") NDI's `chooseLevel` skips a pyramid level that stores no bytes (the file-less `sampled_body` of [compression block and empty levels]); today, on a voxel-size tie, it takes whichever comes last, which can be the empty level. Built: NDI-matlab 4effe11e0 (PR #1076) (`chooseLevel`, with tests)

Decided by Jess Haley, 2026-10-26 [ingested stimulus reader finds the body]: ("8a") NDI's `ndi.daq.metadatareader.get_ingested_document` also finds a migrated ingested stimulus file as the presentation's data body, by session and epoch ([ingested stimulus file is a body of the presentation]), and reads the same `.nbf.tgz` file. Today it queries only the v1 shape (`depends_on daqmetadatareader_id` and `epochid.epochid`, NDI-matlab V2 `+daq/metadatareader.m:171-172`), and `readmetadata_ingested` returns `{}` without an error when nothing matches, so every stimulus-parameter read on a migrated ingested dataset would come back empty (from reading the code, not run). A test migrates an ingested epoch and reads its parameters back. Built: NDI-matlab 4effe11e0 (PR #1076) (`+daq/metadatareader.m`, `+vintage/ingestedStimulusKey.m`, test)

Decided by Jess Haley, 2026-10-26 [markdown cleanup and rename]: ("9 yes", "10 ok", "11 ok, but can we rename the v eta docs v2?", "12 yes", "1 did_v2_, 2 yes rename now"; plan `docs/v2_working/MARKDOWN_PLAN.md`) under [markdown out of schemas]: (1) the 14 delete candidates go (the `V_alpha`..`V_zeta` specs and notes and `V_eta_notes.md`; git keeps them; the pointers to the six DEL-B files become "(deleted; see git <sha>)"); (2) `V_eta_class_provenance.md`, `V_eta_distance_metadata_plan.md`, `V_eta_second_pass_plan.md` and `V_eta_statement_referent_findings.md` move to `docs/history/`; (3) the layout is `docs/` (entry points: tenets, OPEN_WORK, did_query_model), `docs/plans/` (flat), `docs/generated/`, `docs/history/`; (4) the documents are renamed now, in the same move, `V_eta_*` -> `did_v2_*`, every citation updated once; (5) a document cited by bare name resolves to the unique file of that name under `docs/`, and a duplicate name fails the gate. (6) ("A") the seven JSON registers and data files in `schemas/` (`V_eta_carry_register.json`, `V_eta_coverage_ledger.json`, `V_eta_decisions.json`, `V_eta_migration_targets.json`, `V_eta_ndi_ground_truth.json`, `V_eta_openminds_crosswalk.json`, `V_eta_term_registry.json`) are renamed `did_v2_*` in the same step and stay in `schemas/`. Siblings first: DID-matlab and NDI-matlab code that reads a renamed file accepts both names before the old ones go. (DID-matlab `tools/corpus_proven.py`, `tools/affected_corpora.py` and `test-corpus.yml` read `schemas/V_eta_coverage_ledger.json` / `V_eta_corpus_proof.json` by path.) Build pending: did-schema (the move, the rename, the citation rule), DID-matlab, NDI-matlab (files read by name)

Decided by Jess Haley, 2026-10-26 [pipeline defects are not carries]: ("B", to Claude's question whether carries caused by the migration itself rather than by the v1 data are register rows) a v1 document left unconverted because of the pipeline, not the data, is a DEFECT, never a carry register row: (1) a stale or incomplete V2 schema (DID-matlab `metadata_editor.m`, a form field with no binding; `pyraview.m` / `private/jFrequencyFilter.m`, the pre-[filters are methods] `frequency_filter` path); (2) an NDI second-pass re-fold whose output fails validation and is quarantined (`ndi.migrate.local`: table rows, labels, ensembles); (3) a second-pass step that throws and is caught. Such a run fails loudly, or its report lists the cases as errors apart from carries, and the cause is fixed in code. The carry register explains the data only. Built: DID-matlab 1f83af39 (PR #251) (commits 2495ef9a, 3c717eb8: `+did2/+convert/+migrators_j/metadata_editor.m:378` and `+did2/+convert/+migrators_j/private/jFrequencyFilter.m:254` raise `did2:convert:schemaTooOld`). Built: NDI-matlab 38adc701b (PR #1074) (re-fold quarantines and caught errors reported as errors)

Decided by Jess Haley, 2026-10-26 [unresolved recorded elements make a standalone item]: ("1 a") a v1 `stimulus_presentation` whose epoch records elements that resolve to no subject becomes a standalone item, as one with no element at all does (`V_eta_stimulus_model_plan.md` [presentation with no subject]), instead of being carried as v1. The drafted register row carry-082 is withdrawn. Built: NDI-matlab 38adc701b (PR #1074)

Decided by Jess Haley, 2026-10-26 [extra field on an ingested stimulus file is malformed]: ("2 a") a v1 `daqmetadatareader_epochdata_ingested` holding a block field or edge the presentation's data body does not write is carried as `malformed` (carry-087): NDI's template block is empty and its writer (`+daq/metadatareader.m` `ingest_epochfiles`) sets only the `daqmetadatareader_id` edge, so such a field is not writer-shaped.

Decided by Jess Haley, 2026-10-26 [NaN control means no control]: ("2 a", after Claude checked the writer) a v1 `control_stimulus_ids` whose control is NaN is converted, not carried: NDI's writer writes NaN when a stimulus set has no control (NDI-matlab main `+app/+stimulus/tuning_response.m:622` "if number of control stimuli is 0, that's okay, just give values of NaN", `:634` `cs_ids = nan(size(stimids))`), and its own reader skips NaN (`:298`). The control-pairing calculation ([control pairing is a calculation]) records NaN for such trials, meaning "no control"; carry-091 keeps only records broken in themselves. Built: NDI-matlab 38adc701b (PR #1074)

Decided by Jess Haley, 2026-10-26 [conflicting animal records need a map]: ("yes, cite one correct reading", after asking "why don't we just make the cohort? Is it that we can't tell if the multi-subject is a mistake?") several animals recorded together in a session already get one manipulation on the session's standing cohort (`V_eta_stimulus_model_plan.md` operating rule 2, T17 amendment signed 2026-10-21); only a presentation whose records name DIFFERENT animals (rule 4: "conflicting records are not a shared event") is carried, `needs_mapping`, citing [one correct reading] (carry-081): the generic stage cannot tell which record is right. Built: NDI-matlab 38adc701b (PR #1074).

Decided by Jess Haley, 2026-10-26 [method terms are general]: ("1. yes", proposal `docs/v2_working/EMPTY_TERMS_PROPOSAL.md`) a calculation's method term names the general procedure, not the tool or the NDI class that ran it: spike sorting is "Spike sorting" (wikidata:Q2003571), a fit is "curve fitting data transformation" (OBI:0200072); the specific tool (Kilosort, Kiasort, JRCLUST, an `ndi.calc.*` class) is the `software` entity on `software_id` ([software_id is what produced the statement]), carrying its RRID where one exists (Kilosort RRID:SCR_016422). Applies to all seven calculation migrators. Build pending: did-schema (registry rows), DID-matlab (the calculation migrators)

Decided by Jess Haley, 2026-10-26 [Naka-Rushton is one function]: ("2. yes") the Naka-Rushton fits are one model term, the function R(c) = Rm c^n / (c^(n s) + c50^(n s)) (NDIcalc-vis-matlab documents RB, RBN and RBNS as this function with different parameters free); RB is written as the constraints n = 1 and s = 1, RBN as s = 1, in the fit's existing constraints field, not as separate terms. Build pending: did-schema (the term), DID-matlab (the tuning fit migrators)

Decided by Jess Haley, 2026-10-27 [fields outside the template are malformed]: ("1. Yes", to Claude's proposal: "When a v1 document has a field NDI's template doesn't define, I'd carry the whole document as v1 under one generic \"malformed\" register row instead of dropping the field silently. This comes up in every class family.") a v1 document holding a field, block or edge that its class's NDI template (at the locked `main`) does not define, and that the migrator therefore does not read, is carried whole and unchanged as v1, kind `malformed`, under ONE generic carry-register row for every class (carry-100, `v1_class` "*"); the field is never dropped silently ([lossless means round trip], [partly placed is carried as v1]). Answers "Waiting for Jess" item 4b in `docs/V2_PLAN.md` and the same question for responses (15d), the ingested data cache, images (19c), spike sorting and acquisition systems. Built: did-schema (carry-100). Partly built: DID-matlab e73aec7 (PR #253) (the 72 classes that read raw v1 carry under carry-100, `+did2/+convert/+migrators_j/private/jRawCarry.m:36`). Build pending: DID-matlab (the 23 classes not switched, `rawV1Classes.m`, still take the renamed path, which drops such a field without a note, `jRawCarry.m:14-16`), NDI-matlab (second-pass carries of an off-template field cite carry-100)

Decided by Jess Haley, 2026-10-27 [probe location terms]: ("2. Yes", to Claude's proposal: "Probe locations in the corpora use UBERON:0001880, UBERON:0002813 and UBERON:0002812, which aren't in the term registry. They're existing ontology terms, so I'd add them as rows.") the term registry gains three existing UBERON terms, named as UBERON labels them ([term labels stay as the ontology spells them]): "bed nucleus of stria terminalis" (UBERON:0001880; Dab, 404 probe locations, written "bed nucleus of stria terminalis (BNST)"), "right cerebral hemisphere" (UBERON:0002813; 33) and "left cerebral hemisphere" (UBERON:0002812; 29). Counts from the four corpus zips (20211116, Dab, JH, Soph; 528 probe locations). Built: did-schema (registry rows)

Decided by Jess Haley, 2026-10-27 [cell spellings are one meaning]: ("1. Agree", after "Part of the goal is to represent each dataset in the most V2 way possible. Using the term element is not part of the v2 vocabulary", to Claude's proposal: "treat `spikes`, `neuron` and `cell` as three spellings of one meaning, as with [spelling is notation]: the document becomes entity type `cell` and nothing else, and the round trip accepts any of the three back") the v1 element type strings `spikes`, `neuron` and `cell` are not kept as a statement or a note; each becomes entity type `cell`, and the round trip counts the three as equivalent spellings. Build pending: DID-matlab (`+roundtrip/element.m` equivalents for the three spellings; no migrator change).

Decided by Jess Haley, 2026-10-27 [v1 name is the entity name]: ("I think if v1 has a name write it to entity.name regardless of if it's equal or not", after Claude found that 0 of 1,918 subjects in the 20211116, Dab, JH, Soph and PRED corpora have a `base.name` that differs from `subject.local_identifier`: 45 equal, 1,873 empty) a non-empty v1 `base.name` of a document that becomes an entity is written to `entity.name`, whether or not it equals the local identifier; an empty one writes nothing. Nothing is carried for it. Built: DID-matlab 4790a8a (PR #258) (`+migrators_j/private/jBaseName.m`, called by subject, subject_group, element, session and dataset_remote; their `+roundtrip/` inverses rebuild `base.name` from `entity.name`).

Decided by Jess Haley, 2026-10-27 [member edge number is notation]: ("3b. Agree", to Claude's proposal: "a v1 group whose one member link is spelled `subject_id`, with no number, comes back as `subject_id_1`; count them as the same, so no carry") a `subject_group` member edge spelled `subject_id` and one spelled `subject_id_1` are the same edge ([spelling is notation]); the round trip accepts either. Built: DID-matlab 4790a8a (PR #258) (`+roundtrip/subject_group.m` `sameMemberEdge`).

Decided by Jess Haley, 2026-10-27 [afo prefix registered]: ("I yes and create the reader in ontology matlab repo", to Claude's proposal: "Register the `afo` prefix? It already has 'acquisition time' and 'cluster identifier'") the Allotrope Foundation Ontology prefix `afo` is registered, and the proposed EMPTY terms "acquisition time" and "cluster identifier" are not minted: `AFO:AFR_0001158` "acquisition time" ("The acquisition time is the time when a signal is captured.") and `AFO:AFR_0003339` "cluster identifier" take their place. ndi-ontology-matlab gains a reader for AFO terms. Built: did-schema (`CURIE_lookups_meta.json` prefix entry by the prefix spelling plan; term registry rows); ndi-ontology-matlab 27d5823 (PR #15) (`+ndi/+ontology/AFO.m`). Build pending: DID-matlab (the migrators that write "acquisition time" and the cluster identifier use the AFO nodes).

Decided by Jess Haley, 2026-10-27 [n-trode is a multielectrode array]: ("Ii yes", after "Multi-electrode array sounds better to me as long as it's genuinely the same thing", to Claude's proposal: "Use multielectrode array (Q1952355) with an electrode count instead of n-trode? Its definition, 'devices that contain multiple microelectrodes through which neural signals are obtained or delivered', does cover tetrodes") an NDI `n-trode` probe is a device of type Wikidata Q1952355 "multielectrode array", with its number of electrodes as a statement on the device; no n-trode term is minted. Built: did-schema (term registry row for Q1952355). Build pending: did-schema (the electrode-count variable); DID-matlab (`+migrators_j/element.m` n-trode device type and the electrode-count statement).

Decided by Jess Haley, 2026-10-27 [site positions are coordinates]: ("Iii yes", to Claude's proposal: "Use NCIT's X, Y and Z coordinates for electrode site positions, with the device's own frame on the document?") the three proposed EMPTY terms for probe site positions (left-right, front-back and depth position on device) are not minted; site positions use the registered NCIT X-Coordinate (C44477), Y-Coordinate (C44478) and Z-Coordinate (C44479), all three already in the term registry, and the document carries that the frame is the device's own. Build pending: did-schema (how the document states the device frame); DID-matlab (`+migrators_j/probe_geometry.m`).

Decided by Jess Haley, 2026-10-27 [move the locked mains]: ("25. Yes", to Claude's proposal: "Move the locked `main` references? ... none touches a document template or writer. Moving them only changes a file count quoted in two plan documents") the sibling lock's `main` for NDI-matlab and DID-matlab moves to their current `origin/main`, with the regenerated artifacts and the prose counts in the same commit. Built: did-schema PR #183 (`tools/sibling_lock.json`: NDI-matlab main 441530d0f, DID-matlab main e4493aa; seven RE-DERIVED count lines).

Decided by Jess Haley, 2026-10-27 [merge main into V2]: ("25. Yes", to Claude's question: "Merge `main` into V2? ... DID-matlab merges cleanly (34 commits). NDI-matlab has 86 commits and three conflicts to resolve", recommended "as PRs into V2") `main` is merged into the `V2` line of DID-matlab and NDI-matlab, each as a PR into V2, conflicts resolved keeping both sides' intent, merged only when CI and the corpus runs are green; then the sibling lock heads move to the new V2 commits. Build pending: DID-matlab (merge PR), NDI-matlab (merge PR; conflicts in `session.m`, `+lightsheet/view.m`, `+cloud/+internal/resolveOrganizationId.m`), did-schema (lock heads).

Decided by Jess Haley, 2026-10-27 [lock NDIcalc-vis-matlab]: ("26 a. Yes", to Claude's proposal: "The tuning templates come from a third repo, NDIcalc-vis-matlab, at commit 00e3e0f. Nothing pins that ... pin it the same way") NDIcalc-vis-matlab joins the sibling lock, pinned at the commit the tuning templates are read from (00e3e0f), so a tuning template cannot change under did-schema unnoticed. Built: did-schema PR #185 (`tools/sibling_lock.json`: NDIcalc-vis-matlab head = main = 00e3e0f10; `tools/sibling_lock.py`, `tools/gates.py`, the CI checkout; no did-schema tool reads NDIcalc-vis templates).

Decided by Jess Haley, 2026-10-27 [tuning stray fields are malformed]: ("26 b. Yes", to Claude's proposal: "Stray fields go to carry-100, as in every other family. carry-056 keeps only real writer fields still waiting for a home") a tuning-family v1 document holding a field outside its NDI template is carried under carry-100 ([fields outside the template are malformed]); carry-056 keeps only fields an NDIcalc-vis writer does write that V2 has no home for yet. Built: DID-matlab 1befcc3 (PR #260) (`private/jCalculation.m` splits by `did2.convert.v1read.calculatorTemplate` and cites carry-100 through `jRawCarry`; also applied to `hartley_calc` and `contrastsensitivity_calc`, which share the fold); did-schema (carry-056 `fields` and `when` reworded).
