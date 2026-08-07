# V_eta Go-Forward Class Audit — J-cohesiveness of every live class

*The go-forward V_eta schema = `stable/` + `draft/` (the tiers CI assembles into
`DID_SCHEMA_PATH`; `deprecated/` is excluded). **258** classes. This audit gives
**every** one a J-disposition so the whole set can be reviewed for Brainstorm-J
cohesiveness — not just the families touched piecemeal (D-A…D-E).*

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

**The team's words:** *"I agree with the 4 proposals."* NO `TEAM-SIGN-OFF` LINE —
the marker is the team's to write (Operating Rule 4).

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

### DISPOSITION

**PASSTHROUGH**, agreeing with `V_eta_tenet_audit.md`'s re-audit, which reached this
independently and was right. A corpus 0-document check is still required before any
future drop — absence from the five corpora we test is not absence.

## 4. `subjectmeasurement` — route through the `measurement` fold

A REAL did_v1 template:

```json
subjectmeasurement  ⊂ base   dep: subject_id
  { measurement: "", value: "", datestamp: "" }
```

Its shape is a subject observation outright — `measurement="age"`, `value=30`, a
date. That is `variable` + value + date, the same target `measurement` already folds
to, and `measurement`'s migrator plus a `subjectmeasurement` tombstone both landed
under TaskList #41. **No new model: one migrator reusing the existing path.**

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
