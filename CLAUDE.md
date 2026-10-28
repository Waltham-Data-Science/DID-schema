# DID-schema: working context for Claude

This repository holds V_eta, the schema that NDI V2 is built on. It also holds
the tools that check it and the record of every decision about it. This file
says how to work here today. It is not a history. The history is in git and in
the plan documents under `schemas/`.

---

## 1. Operating rules (read before doing anything, no exceptions)

These rules exist because a run of mistakes shared one property: **they were
biased toward things looking fine, or toward looking like progress had been
made.** All-zero counts read as clean. All-decided read as done. A grep that
could not have matched was reported as "this does not exist anywhere". An error
that is random is a nuisance; an error that always points at *we are further
along than we are* makes every report unusable. The same error has also run the
other way (absence read as a failure, a plan header claiming less than its
signatures). Both directions are the same defect.

**1. DO NOT WRITE TO `schemas/` unless asked.** Not schema files, not plan
documents, not notes. Findings go to the chat or a scratch file. Nothing enters
the record until the user says "commit that". Research quietly becoming the
record is how five V_eta families Claude wrote up alone ended up reported to the
team as decided.
*[CLARIFICATION, for approval: an edit the user asked for (a class change, a
registry row) is allowed. It is still not committed until they say so.]*

**2. EVERY factual claim about NDI, a migrator, or a corpus ships with the
command output that proves it, in the same message.** If the output cannot be
pasted, the sentence is not written.

**3. CONTRADICTING an existing comment, decision or document requires POSITIVE
EVIDENCE. Never absence.** Not finding something is not evidence it is not
there.

**4. THE TEAM DECIDES; CLAUDE PROPOSES.** The team is Jess Haley and Steve Van
Hooser. *(Rewritten 2026-10-21 at Jess Haley's request: the decision itself, not
a separate sign-off ritual, is what counts; and it is the team's, not one
person's.)*
- **A decision is what a team member says in conversation or review.** When a
  team member decides something ("yes, do (a)"), Claude records it in the plan
  document, in the same commit as the build:

        Decided by <name>, <YYYY-MM-DD> [<tag>]: <what was decided, in their words where possible>

  `<name>` is a team member's full name. `<tag>` is short and unique among that
  document's `Decided by` lines; a class cites the decision by document and tag.
  *(2026-10-22, Jess Haley.)* When the build lives in another repository, the
  line is committed at once and ends `Build pending: <repo> (<what>)`; when the
  build lands, that becomes `Built: <repo> <commit>`. Never hold a decision
  line in an uncommitted tree waiting for a sibling. A `Build pending` line
  may reach `main` once the team has decided it. Before a PR merges, every
  `Build pending` line it adds or changes must name a repository and what is
  left to build there. A build that lands marks its line `Built:` in the same
  or the next did-schema PR. `python3 tools/decision_citations.py --pending`
  lists what is still open. *(2026-10-26, Jess Haley: replaces "`--pending
  --strict` must report 0", which no PR could meet while builds wait on
  later work.)* `tools/decision_citations.py` keeps the team list (`TEAM`, the one place it is
  kept) and reports, without counting, a line by anyone else or a line with no
  tag.
- **Never upgrade a proposal.** Anything the team has not explicitly decided is
  written as "Proposed (not decided)". Claude never writes "Decided by",
  "approved" or "signed" for something a team member did not say — not from a
  summary, an agent's report, an inference, or a "they would agree". If unsure,
  ask.
- **The PR merge is the ratification.** Every `Decided by` line reaches `main`
  only through a PR the team reviews and merges, so a mis-attributed decision is
  caught in the diff.
- **Existing `TEAM-SIGN-OFF` lines stay valid** as the record of earlier
  decisions; no new ones are needed. A tool that reports decision state reads
  either form and cites the document; it never reports "no signature" for a
  decision that is recorded.

**5. AN INSTRUMENT MUST REPORT ITS DENOMINATOR.** Any counter, census or report
states how many things it inspected, first and unconditionally. A count without
a denominator is not evidence. "Not measured" is a third state; it is never
"no" and never "yes".

**Answer first, record after.** In a conversation with a team member, reply
before running the gate chain, committing or pushing. Record decisions and
other edits right after the reply, and batch them. Run `tools/gates.py` once
per batch, in the background, before the push. A decision is still committed
promptly (rule 4), but never ahead of the answer the team member is waiting
for. *(2026-10-26, Jess Haley.)*

**Scope: do exactly what was asked, and stop.** "Look at X if you like" is not
authorisation to change X. Ambiguity is resolved by asking, not by doing more.

### Integrity is a gate; done is the goal

*(2026-10-21, Jess Haley: "Bar-2 means done. Bar-1 is just a step to get to
Bar-2." The words "Bar-1" and "Bar-2" are retired. Records written before this
date, including dated corpus measurements in the plan documents, use the old
names: "Bar-1" there means integrity, "Bar-2" means done.)*

- **Integrity check:** nothing quarantined, orphaned or fragmented. It is a CI
  gate, never reported as progress. A green corpus run shows integrity and
  nothing more.
- **Done, per corpus:** integrity, AND every class that corpus contains at its
  decided final V_eta shape (no husks, no preserved raw bridges, no
  passed-through v1 tombstones, no superseded emissions), AND corpus-proven.
  Only the classes that corpus contains count.
- **Done, for a migrated corpus** *(2026-10-24, `V_eta_go_forward_class_audit.md`
  [migration not generalizable], [v1 import stages])*: integrity AND lossless
  (every v1 item is carried, at a V_eta shape or unchanged as v1). Generic
  migration is plumbing and is frozen; a v1 document carried unchanged is not a
  defect of the generic stage. A *publishable* V2 dataset is a per-dataset
  import whose meaning decisions are recorded in its decision workbook; the
  definition above applies to that import, not to the generic stage.
- Report each corpus as **done** or **not done**, with the list of what is
  missing, the number and the run. Never report integrity as done.
- Every corpus figure recorded before the migrator port landed on DID-matlab
  #218 (2026-10-21) was measured on the pre-#73 shape. It says nothing about
  the shape on PR #88.

---

## 2. Where state lives

**When prose and a generated artifact disagree, the artifact wins.** Prose in
this project has been wrong often enough to be dangerous, including this file.
Never quote a count from prose. Re-derive it with the tool that prints it.

| artifact | answers | made by |
|---|---|---|
| `schemas/V_eta_STATUS.md` + `schemas/V_eta_decisions.json` | how much of V_eta is left | `tools/status_board.py` |
| `schemas/V_eta_coverage_ledger.md` / `.json` | each v1 source class, its V_eta target, and its completion ladder stage | `tools/coverage.py` |
| `schemas/V_eta_final_class_set.md` | the persist set, by category | `tools/regen_final_class_set.py` |
| `schemas/V_eta_ndi_ground_truth.json` | what NDI templates and writers declare | `tools/ndi_ground_truth.py` |
| `schemas/V_eta_migration_targets.json` | per v1 class: emitted `targets` (generated) and authored `decided_targets`, `how`, `flags` | `tools/refresh_migration_targets.py` (the `targets` column only) |
| `schemas/did_v2/index.json` | tier, version and superclasses of every class (derived); `disposition` (hand-written) | `tools/validate_v_eta.py` |

Do not run these one at a time. Run the chain:

    python3 tools/gates.py              # regenerate everything, then gate
    python3 tools/gates.py --check      # same, in a scratch mirror; writes nothing
    python3 tools/gates.py --explain    # the order, why, and the evidence for each edge
    python3 tools/gates.py --list       # step names
    python3 tools/gates.py --only STEP  # one step (still in derived order)

`--explain | head -1` prints the step count. Do not write that count anywhere.
`--ci` is what CI runs: it implies `--check` and reports, rather than fails,
steps whose inputs are not on a runner.

**The chain measures the commits in the sibling lock, `tools/sibling_lock.json`**
(see "The sibling lock" in §3). `gates.py` prints the locked commits first and
refuses to run when a sibling checkout is not at its locked head. Moving the
lock is a deliberate commit:

    python3 tools/sibling_lock.py --check    # are the checkouts at the lock?
    python3 tools/sibling_lock.py --update   # record the siblings' HEAD and origin/main

Other tools worth knowing:

- `python3 tools/confirm_sheet.py`: the classes whose migrator runs but whose
  emitted set nobody has confirmed, each as a question the team can answer
  alone. It writes nothing by default and refuses to write into `schemas/`.
- `python3 tools/check_prose_counts.py`: finds numbers in this file and in
  `schemas/*.md` that the tree no longer holds. It is a gate.
- `python3 tools/check_citations.py --document <file>`: checks `file:line`
  citations still point at what they claim.
- `python3 tools/check_signoff_header_staleness.py`: finds a plan document whose
  header says "unsigned" while it carries a signature. A correction note that
  quotes old wording is exempted by the marker `HISTORICAL-SIGNOFF-CLAIM`.
- `python3 tools/propose_terms.py`: checks a batch of new terms against the term
  registry and prints the rows to add. It writes nothing.

Rung 4 of the coverage ladder (corpus-proven) is answered by DID-matlab's
`tools/corpus_proven.py` in DID-matlab's corpus workflows. In this container it
reads `not measured` on every row. That is a property of the container, not a
result.

The open-work index is `schemas/V_eta_OPEN_WORK.md`. Cite a row as
"`V_eta_OPEN_WORK.md` row #51", never with a colon after the file name (that
reads as a line number). A finding is
not recorded until it is committed: the task list does not survive a container
being re-provisioned.

---

## 3. Repositories, branches and CI

### The repositories

| repo | branch line | V2 migration PR (merged 2026-10-23) | what lives there |
|---|---|---|---|
| did-schema (Waltham-Data-Science) | `main` | #88 (and #120) | V_eta JSON, registries, plan documents, gate tools |
| DID-matlab (VH-Lab) | `V2` | #218 | `+did2/+convert/+migrators_j` (per-document migrators), `+did2/+convert/*.m` (batch post-passes), `+did2/+build` (V2 document builder), `+did2/+schema/cache.m` (validator) |
| NDI-matlab (VH-Lab) | `V2` | #1021 | the V2 object layer, the Haley V2 import, NDI's second pass; `origin/main` templates (at the locked sha, `tools/sibling_lock.json`) are the v1 truth |
| empty-ontology (Waltham-Data-Science) | `V2` | none (#22-#25 merged) | EMPTY terms, `src/ontology/empty-edit.owl`; term rules in `docs/conventions.md` (#25) |
| ndi-ontology-matlab (Waltham-Data-Science) | `main` | none (#11, #12, #14 merged) | ontology lookups, `NDIC.txt` |

did-schema also has a `V2` branch. Check with `git rev-parse origin/V2
origin/main` before assuming what it holds.

The V2 migration is merged: did-schema #88 into `main`, then DID-matlab #218
and NDI-matlab #1021 into `V2` (2026-10-23), after empty-ontology #22-#25 and
ndi-ontology-matlab #11, #12 and #14. Read a head with `git ls-remote` or
`git rev-parse` when you need it, never from this file.

If the local checkout may be behind, `git fetch` and compare with `origin`
before measuring anything. A measurement taken on a rewound tree looks exactly
like a measurement.

### The sibling lock

*(Decided by Jess Haley, 2026-10-23, in conversation: lock the exact sibling
commits in a committed file, and build and check against those; updating the
lock is a deliberate commit.)* NDI `origin/main` used to be read live, and it
moved twice on 2026-10-23, turning `check_prose_counts` red and changing
generated files with no change here (commits dc650e8, 5cba5a4).

`tools/sibling_lock.json` records, for NDI-matlab, DID-matlab and
NDIcalc-vis-matlab:

- `head`: the commit the sibling's working tree must be at (the siblings' `V2`
  line, recorded in `head_ref`);
- `main`: the commit every read of that sibling's `origin/main` reads instead.

NDIcalc-vis-matlab (`V_eta_go_forward_class_audit.md` [lock NDIcalc-vis-matlab])
has no `V2` line: its `head` and `main` are both the commit its tuning templates
are read from, on `main`. No tool here reads its files yet.

How each is used (`tools/sibling_lock.py` docstring has the reasons):

- **`main` is read, not checked out.** `coverage.py`, `ndi_ground_truth.py`,
  `check_prose_counts.py` (`ndi_m_files`) and `check_citations.py` ask
  `sibling_lock.main_refs(<sibling>)` for the rev, and git reads the locked sha.
  Artifacts still say `origin/main`; the ground truth also records the sha as
  `ndi_main_commit`. With no lock the tools fall back to the live
  `origin/main`, then `main`, and the chain refuses to run.
- **`head` is verified, never moved.** `gates.py` (and
  `sibling_lock.py --check`) fail on a present sibling whose HEAD is not the
  locked head, and print the `git checkout --detach <sha>` that fixes it. A
  locked `main` the clone does not hold also fails (`git fetch`). An absent
  sibling is NOT CHECKED. The live `origin/main` having moved past the lock is
  printed as a note, never read.
- **To move the lock:** put the siblings where you mean (`git fetch`, check out
  the new heads), run `python3 tools/sibling_lock.py --update`, then
  `python3 tools/gates.py`, and commit the lock with the regenerated artifacts.

### How this repository's CI checks out the siblings

`.github/workflows/tests.yml` runs `python3 tools/gates.py --ci` and owns no
gate list of its own (`tests/test_gates.py` fails if one comes back). It clones
NDI-matlab, DID-matlab and NDIcalc-vis-matlab in full and checks out, for
each, the locked `head`
(`python3 tools/sibling_lock.py --get <sibling> head`), detached. There is no
branch resolution and no fallback: a missing lock, or a locked commit a clone
does not hold, fails the step. It then runs `sibling_lock.py --check`.

(DID-matlab's own workflows still resolve NDI-matlab by branch name: Decided
(Jess Haley, 2026-10-22, `V_eta_go_forward_class_audit.md` [NDI ref fallback]),
the same-name branch, then `V2`, then `main`.)

Three details are load-bearing and fail quietly if they regress (all asserted
by `tests/test_ci_runs_the_whole_chain.py`): the clone is full, not shallow,
because `coverage.py` and `ndi_ground_truth.py` read NDI's locked `main`, which
is not the checked-out commit, and the ground truth walks history from it; the
checkout is the locked head (the `V2` line), while the locked `main` is still
reachable, and the step fails if it is not; and `NDI_MATLAB` / `DID_MATLAB` are
exported.

CI checks out no empty-ontology or ndi-ontology-matlab, and the lock does not
cover them. `check_term_registry` reports its rule R7 (EMPTY labels match the
ontology) as NOT CHECKED there.

Locally, `tools/gates.py` finds siblings through `$NDI_MATLAB` / `$DID_MATLAB`
/ `$NDICALC_VIS_MATLAB` first (an explicitly set variable is authoritative, even if empty), then
`/home/user/<repo>`, then `../<repo>`. Set the variables to the checkout you
mean, and put that checkout at the locked head; the chain will not run
otherwise. `check_term_registry` reads `$EMPTY_ONTOLOGY`, then a sibling
`empty-ontology` folder. The sibling folders must be named `NDI-matlab` and
`DID-matlab`: generated paths include the folder name.

### How the siblings' CI picks a did-schema ref

- DID-matlab `test-builder.yml` and `test-migrators-quick.yml`: a did-schema
  branch with the same name, else `main`.
- DID-matlab `test-code.yml`, `test-fixtures.yml`, `test-corpus.yml` and
  `test-soph-corpus.yml`: `main`.
- NDI-matlab `test-eta-migrate*.yml` and `test-import-v2.yml`:
  `DID_SCHEMA_REF: main`, `DID_MATLAB_REF: V2`.

Grep the workflow files for the current pins; do not trust this list. The pins
moved off the #88/#218 branch `claude/ecstatic-pascal-md91fw` after the merge.

### Changes the siblings must follow land in the siblings first

*(2026-10-22, Jess Haley, after a declared rule broke every sibling CI that
reads #88.)* did-schema is read live by DID-matlab and NDI-matlab CI, so a
schema change that their code must follow goes in this order:

1. **A new named rule:** DID-matlab's `+did2/+build/private/checkRules.m` (and
   its test) lands first; only then does a class declare the rule.
   `did2.build` refuses a rule it cannot check (`did2:build:unknownRule`).
2. **A removed or renamed field, a retired class, a required edge:** the
   writers and readers in DID-matlab and NDI-matlab change first (or read both
   shapes), then the schema removes the old shape.
3. **A name that code compares** (relation, entity type, channel type): code
   compares by node first, then the stored name changes.

The schema side records the decision line at once and builds the part that
breaks nothing; what waits is listed in the PR, not left implied.

**One working copy per agent.** An agent works in its own clone or worktree,
never in a checkout another agent or the main session is using. Two writers in
one working tree leave half-built changes that nobody can safely commit.

### The JSON under `schemas/did_v2/` is the source

There is no build script. `tools/build_v_eta.py` and the `V_alpha`..`V_zeta`
trees are deleted (OPEN_WORK #128). The tiers are `stable/` and `draft/`. The
`deprecated/` v1 tombstones were deleted ([carried v1 validates against NDI
templates]): a document carried whole as v1 is checked against NDI's v1
templates; the classes carried as v1 are `CARRIED_AS_V1` in
`tools/veta_record.py`.

**To change a class:**

1. Edit its file under `schemas/did_v2/<tier>/` (JSON, indent 4).
2. For a new class, add a hand-written `disposition` (`persist`, `retire` or
   `in_progress`) to its entry in `schemas/did_v2/index.json`. The other index
   fields are derived.
3. Run `python3 tools/gates.py`. Its `validate_v_eta` step checks the rules the
   old builder enforced and rewrites the derived pieces: `index.json`,
   `stable/term_registry_meta.json`, the relation value lists, and the
   `ndi_mustBeNonEmpty` stamp. Do not hand-edit those.

Data the old builder held that tools still read (the `RENAME` map, retired
class names, `_DELETE_PHASE8`) is in `tools/veta_record.py`. Re-adding a
retired name means deleting it there.

### The term registry (T19)

- Source: `schemas/V_eta_term_registry.json`. Built copy:
  `schemas/did_v2/stable/term_registry_meta.json` (derived; do not edit).
- It holds every ontology term a V2 import writes in a vocabulary slot.
  DID-matlab's `did2.build` refuses a term it does not hold (strict mode
  `TermRegistry`, armed by default; `did2.convert` turns it off while
  migrating).
- Order of preference (T19): a term already used in an NDI dataset, then an
  existing ontology term, and only then a new EMPTY term.
- `tools/check_term_registry.py` is a gate: one entry per node and per name,
  known and correctly spelled prefixes (`V_eta_prefix_spelling_plan.md`),
  definitions on EMPTY and staged terms, EMPTY labels matching the ontology,
  and closed value lists naming registered terms. Its docstring lists the
  rules.
- Use `tools/propose_terms.py` to prepare new rows.

### The binding registry

- `schemas/did_v2/stable/binding_registry_meta.json`. Its lists include
  `subject_statement_bindings` (variable-keyed statement bindings),
  `relation_bindings` (each row declares `passes`), `entity_field_bindings`
  and `entity_type_bindings` (what each `entity.type` requires).
- A `subject_statement_bindings` row may carry `values`: a closed list of
  registered terms (`V_eta_term_registry_plan.md`, "Closed value sets").
- A binding's `strength` is authoritative on the field. The registry's
  `strength` column is derived by `tools/regen_binding_strengths.py`.
- Variable bindings are `preferred`. Making them `required` is OPEN_WORK #129
  and waits for a corpus measurement.

---

## 4. The V2 model in brief

Read `schemas/V_eta_tenets.md` (T1–T20, each with its amendments and the
sign-off lines at the bottom) before any design or naming question. Answer from
the tenets, not from the class list. In one paragraph each:

- **One entity class.** Every identifiable thing is an `entity` with a bound,
  required `type` (organism, culture, device, session, dataset, …) and identity
  fields only. A finer kind is one term assertion. Strain is an `instance_of`
  relation. (T1; `V_eta_entity_composition_plan.md`.)
- **Statements by composition.** A statement's class is its direction:
  `assertion`, `observation`, `manipulation` or `calculation` (the last three
  are `interaction`s). Its value kind (`mass`, `term`, `text`, …) is a mixin
  listed in `superclasses`. There are no `<kind>_<direction>` leaf classes,
  except the named v1 calculators. A statement points at its entity by
  `entity_id`. (T2, T3; `V_eta_entity_composition_plan.md`.)
- **Method.** An interaction's method is one block, `{term, parameters}`,
  inline or by `method_id` to a standalone `method` document. (T2, T16;
  `V_eta_method_plan.md`.)
- **Value.** A value is inline, or in data bodies (`data_body: true`, with
  `sampled_body` / `opaque_body` documents pointing up at it). There are
  exactly two body classes. Keys, conditions and method parameters share one
  entry shape. (T6, T14; `V_eta_data_body_model_plan.md`, including its
  amendments.)
- **Relations.** Relations are documents. Each `relation_bindings` row declares
  what passes along it: `assertions`, `distributive`, `context` or `nothing`.
  Records use `included_in`. Every document has a required `session_id` edge.
  (T4, T5, T17; `V_eta_relation_inheritance_plan.md`.)
- **Groups.** A set referred to as a unit is one entity of type group, linked
  by `member_of`. Groups are standing, never minted per statement. Order lives
  on the membership relation. (T20.)
- **Terms.** A term is as general as its meaning allows; the document carries
  the rest. (T19; `V_eta_term_registry_plan.md`.)

Other signed plans to point at: `V_eta_time_reference_model_plan.md`,
`V_eta_stimulus_model_plan.md`, `V_eta_tuning_model_plan.md`,
`V_eta_recording_observation_plan.md`, `V_eta_study_plan.md`,
`V_eta_source_unit_plan.md`, `V_eta_prefix_spelling_plan.md`,
`V_eta_duplicate_entities_plan.md`, `V_eta_linked_session_plan.md`.
`V_eta_SPEC.md` predates the 2026-10-08 entity merge; where it disagrees with
the tenets or a signed plan, those win.

**A plan document's state is its decision lines, not its header.** Decisions
("Decided by <name>, <date> [<tag>]", or an older `TEAM-SIGN-OFF` line) are often
appended far below a summary that still says "proposed". Read the decision lines,
or the status board.

---

## 5. Hard-won lessons (one line each)

- **NDI `origin/main` templates are the v1 truth, and where a template and its
  writer disagree, the writer wins.** Build fixtures from the writer, never from
  a DID-side schema. (`schemas/V_eta_ground_truth_plan.md`.)
- **A `depends_on` sweep is not a reference check; grep the name too.** v1 joins
  by string in ordinary fields (e.g. `strcmpi(myprobemap.devicename, ...)` in
  NDI `+daq/system.m`; `epochnode_a.objectname` in `+time/syncgraph.m`).
- **V_eta is snake_case and NDI is camelCase.** An absence check must use NDI's
  spelling (`demoNDI`, not `demo_ndi`). `coverage.py` runs a normalised spelling
  sweep (search it for "spelling").
- **The corpora are a sample of datasets, not the universe.** A class absent
  from them is untested, not fine. Nothing is deferred, retired or deleted on
  that ground; a deletion needs a writer check against NDI `origin/main`.
- **Absence is not evidence, in either direction.** A search that could not
  have matched proves nothing, and a missing counter is "not measured", not a
  failure.
- **A test written from the same premise as the code cannot catch the code.**
  Several tests had to be inverted, not updated.
- **A plan's header is not its state.** Read the sign-off lines
  (`check_signoff_header_staleness.py`).
- **Citations into files under active edit decay in hours.** Cite by searchable
  content (a function name, a grep pattern, a marker); treat a line number as a
  hint (`check_citations.py`).
- **Instruments must report denominators.** `silentLoss` printed "0" for two
  days while reading nothing; check `total_docs` is non-zero before believing a
  census.
- **`find_repo` fails silently on a runner.** A missing sibling shrinks the
  universe instead of erroring. `gates.py` resolves siblings once and treats a
  set variable as authoritative; `coverage.py` prints the sibling paths it used
  first. A local run cannot show this bug.
- **A name surviving in V_eta is not evidence a migrator emits it.** Ask what
  the migrator emits.
- **`Contents.m` narrative is not a migrator census.** List
  `+migrators_j/*.m`, read the ledger's `migrator` column, or read the generated
  roster (DID-matlab `tools/check_migrator_roster.py`).

---

## 6. Open caveats (true at the heads named in the notes)

- **No corpus is reported done.** On DID-matlab 82453f4 (Test code run
  39907038888, 2026-10-23) every corpus passes integrity, and the done report
  reads "DONE on the DID side; PENDING the NDI e2e for the second-pass
  class(es)" for 20211116, B, Dab, JH and Soph. 13 v1 classes stay as v1
  documents by decision ([v1 passthroughs accepted]), so a corpus holding one
  is not done.
- **`BindingConformance` is disarmed by default.** DID-matlab
  `+did2/+schema/cache.m` reads it with `envFlag('DID_ENFORCE_BINDING_CONFORMANCE')`,
  so it is on only when set. `RequiredDependencies`, `NonVacuousFields` and
  `TermRegistry` are armed by default (`~envFlagIsOff(...)`).
- **Variable bindings are `preferred`, not `required`** (OPEN_WORK #129).
- **The value rule (`value_inline_or_body`) is decided, not signed**
  (`V_eta_data_body_model_plan.md`, AMENDMENT 5).
- **NDI `+daq/reader.m` reads `document_properties.epochid.epochid`** for
  ingested epochs. Whether this breaks on a migrated ingested corpus is
  unverified.
- **`readtimeseries` has no test on migrated data.** The corpus zips are
  document-only and carry no binary files. Unverified whether that changed.
- **Migrated `element` name and reference are stored together** as
  `'%s (ref %s)'` in `local_identifier`, without escaping
  (NDI `+vintage/elementFields.m`).
- **`imageStack_parameters` and the demo-series classes have no target and no
  dissolution recorded.** See the coverage ledger's no-target census.
- **`binnedspikeratevm`'s unit (Hz vs spikes per bin) cannot be read**: the
  `vhlab_voltage2firingrate` writer is in no repository we hold. Unverified
  whether that is still true.
