# DID-schema — working context for Claude

# OPERATING RULES — read before doing anything, no exceptions

These exist because on 2026-07-29 a series of mistakes shared one property:
**they were biased toward things looking fine, or toward looking like progress
had been made.** All-zero counts read as clean. All-decided read as done. A grep
that could not have matched was reported as "this does not exist anywhere". An
error that is random is a nuisance; an error that always points at *we are
further along than we are* makes every report unusable. These five rules remove
the mechanisms, because a documented warning does not work — the "recurring
epistemic error" section below was READ and then committed again within the hour.

**1. DO NOT WRITE TO `schemas/`.** Not schema files, not plan documents, not
notes. Findings go to the chat or a scratch file. Nothing enters the record until
the user says "commit that". Research quietly becoming the record is how five
V_eta families Claude wrote up alone ended up reported to the team as decided.

**2. EVERY factual claim about NDI, a migrator, or a corpus ships with the
command output that proves it, in the same message.** If the output cannot be
pasted, the sentence is not written. "No session document exists anywhere" dies
instantly under this rule: the grep that produced it plainly did not show that.

**3. CONTRADICTING an existing comment, decision or document requires POSITIVE
EVIDENCE. Never absence.** `jSessionAnchor`'s note that its orphans were
discovery-mode was correct and was overridden with a failed search. Not finding
something is not evidence it is not there.

**4. ONLY THE TEAM DECIDES A V_eta DISPOSITION.** Claude may research and
propose; it may not record a decision. Enforced in `tools/status_board.py`: a
family counts as decided ONLY if its plan document carries a line

        TEAM-SIGN-OFF: <who/when> -- <what was decided>

Claude must never add that line. Without it the family renders as
"awaiting review" no matter what the FAMILIES table says.

**5. AN INSTRUMENT MUST REPORT ITS DENOMINATOR.** Any counter, census or report
states how many things it inspected, first and unconditionally. `silentLoss`
printed "0 empty edges" while reading nothing for two days, and the digest that
rendered it repeated the omission. A count without a denominator is not evidence.

**Scope: do exactly what was asked, and stop.** "Look at X if you like" is not
authorisation to change X. Ambiguity is resolved by asking, not by doing more.

---

## START HERE — the generated state artifacts (read these FIRST, before any prose)

Everything below this section is PROSE, and prose in this project has been wrong
often enough to be dangerous: "no session document exists anywhere", "all 0-usage,
safe to delete" (3 of 4 wrong), "dissolved (rename/decompose)" (32 rows asserted,
never verified), "the epoch link is the epochid dep" (no such dep). Each was
written down confidently and cost real time. **When prose and a generated artifact
disagree, the artifact wins. When prose makes a claim about NDI or a migrator, do
not repeat it — re-derive it with the tool.**

| artifact | what it answers | regenerate |
|---|---|---|
| **`schemas/V_eta_STATUS.md`** | **how much of V_eta is left, and exactly what** | `python3 tools/status_board.py` |
| `schemas/V_eta_coverage_ledger.md` / `.json` | every v1 source class → its V_eta target | `python3 tools/coverage.py` |
| `schemas/V_eta_final_class_set.md` | the authoritative persist set | `python3 tools/regen_final_class_set.py` |
| `schemas/V_eta_ndi_ground_truth.json` | what NDI templates + writers actually declare | `python3 tools/ndi_ground_truth.py` |

**THE BIGGEST REMAINING ITEM IS A REVIEW, NOT A BUILD, AND ITS ENTRY POINT IS
`python3 tools/confirm_sheet.py`.** 68 of 102 v1 classes sit at ladder stage 1 —
a migrator RUNS and rung 2 reads `not measured` — which reads like 65 classes of
unwritten migration and is not. `V_eta_migration_targets.json` says why in its
own header: `targets` is GENERATED from the call graph while `decided_targets`
is AUTHORED and means *"a signed decision no migrator implements yet"*, so it is
populated ONLY where a gap is already known. A class whose migrator emits
something with no recorded gap carries none, and the ladder correctly refuses to
score a rung nobody answered. **So the question is not "what should these
become" but "is what the migrator ALREADY emits the answer we want", 68 times.**
The sheet sorts them by the KIND of answer each needs — **51** `CONFIRM THE
EMITTED SET`, 14 `CONFIRM A PASSTHROUGH` (asked separately: "the tombstone is the
end state" and "we deferred this" are indistinguishable in the data), **2** with
no emission recorded, 1 absent from the target map. **Those two counts read 50
and 3 until 2026-08-12**, and the row that moved is `stimulus_bath`: `classify()`
read only `targets`, which is GENERATED from the call graph and cannot see a
batch post-pass, so a class whose emission is recorded ONLY in the authored
`second_pass` was filed under *"investigate first, not a team question"* while
its question was ready to ask. That is emission shape (2) of
`V_eta_OPEN_WORK.md` row #107 — **the blind spot the ladder is already known to
have, repeating inside the sheet built to surface unanswered questions**, which
is worse than the original because the sheet is what a reviewer trusts to be
complete. Re-derive the four numbers with `python3 tools/confirm_sheet.py`
rather than quoting these. It **writes nothing by
default** and refuses to write into `schemas/` at all (Rule 1), so it cannot put
a proposal into the record on its own; `--markdown PATH` / `--json PATH` outside
`schemas/` are opt-in. It decides nothing and writes no signature (Rule 4).

**AND THE SHEET'S FIRST VERSION WAS UNANSWERABLE, WHICH NO GATE COULD HAVE
CAUGHT.** It printed `emits:` / `intent:` / `caveat:` per row — three
declaratives — and stated the ask ONCE, in a bucket header above fifty of them.
The team read it exactly as written: *"It reads as decisions have been made."*
Every fact on it was correct; the VOICE was wrong, and a question a reader has to
reconstruct gets answered by silence. Each row now leads with an interrogative
that names its own class and its own emitted set (so it can be answered alone,
days later, by someone who did not write the migrator), carries NAMED answer
options, and says WHO owes the answer — 64 of the 68 are the team's, 4 are a
migrator read that has to happen first. `tests/test_confirm_sheet.py` pins the
framing as an invariant, not the prose.

**DO NOT REGENERATE THESE ONE AT A TIME. RUN `python3 tools/gates.py`** — the
single entry point. It runs the whole regenerate-and-gate chain once, in an
order DERIVED from which tool reads which artifact (`--explain` prints the
order, the reason for every edge, and the witness that substantiates it), and a
batch of N schema edits then costs one regeneration instead of N. `--check`
does the same in a scratch mirror and diffs, writing nothing.

**THIS LINE SAID "All four are CHECKED IN CI and fail when stale, so they
cannot drift while unattended." THREE OF THE FOUR WERE NOT, AND NEITHER WAS THE
BUILT SCHEMA SET ITSELF.** Measured 2026-08-11: each artifact hand-mutated in a
clean checkout of HEAD, then the workflow's exact step list run against it with
the sibling repos absent, as on a runner.

        DENOMINATOR: 5 mutations, each in its own clean checkout, each run
                     through all 8 steps tests.yml then had
        coverage_ledger.md   + a row              CI GREEN  not detected
        final_class_set.md   + a row              CI GREEN  not detected
        ndi_ground_truth.json  writer_deps wiped  CI GREEN  not detected
        coverage_ledger.json - a row              CI RED    (status_board, by luck)
        V_eta/stable/strain.json + a field
          build_v_eta.py would never emit         CI GREEN  not detected

The last row is the one that matters: CI never ran `build_v_eta.py` at all, so
a hand-edit to `schemas/V_eta` — the tree the other three are derived FROM —
passed every gate. Only `V_eta_STATUS.md` was really protected. **`tests.yml`
now calls `tools/gates.py --ci` and owns no gate list of its own**
(`tests/test_gates.py::test_ci_owns_no_second_list_of_gates` fails if one comes
back), which closes the build and final-class-set holes.

**THE LAST TWO SENTENCES HERE SAID "the ground truth stays open on a runner: it
needs an NDI-matlab checkout CI does not have, and `--ci` reports it as NOT
RUNNABLE HERE rather than counting it as passed." THAT IS NO LONGER TRUE —
`tests.yml` CLONES BOTH SIBLINGS AND ALL EIGHTEEN STEPS RUN** (2026-08-11).
Six were being reported NOT RUNNABLE HERE — `ndi_ground_truth`,
`refresh_migration_targets`, `coverage`, `check_tombstones`,
`check_empty_ontology_nodes`, `check_pipeline_parity` — which was honest and
still left a third of the chain unexercised, including the two steps that
produce the coverage ledger and the ground truth. Both siblings are public
(`VH-Lab/NDI-matlab` and `VH-Lab/DID-matlab`, `"private": false`), so nothing
but a clone was ever in the way. Reproduced before it was pushed, in a clean
clone with the siblings fetched the way the workflow fetches them:

        SUMMARY: 18 step(s) declared, 18 ran, 18 passed, 0 failed,
                 0 skipped, 0 not runnable here
        ARTIFACTS DIFFERING FROM THE COMMITTED COPY: 0

Three properties of that clone are load-bearing and each fails QUIETLY if it
regresses, so each is asserted by `tests/test_ci_runs_the_whole_chain.py`:
the clone is FULL (a shallow one does not error — `coverage.py:217,226` and
`ndi_ground_truth.py:491,614` read `origin/main` (line numbers repointed
2026-08-12 -- they were `coverage.py:185` / `ndi_ground_truth.py:449,539`;
then `coverage.py:215,222` for a few hours, until the completion ladder landed
in the same file — see the citation audit), the ref lookup falls through,
and the tool reports a smaller universe); it checks out the FEATURE branch, not
main (`check_pipeline_parity` and the board's migrator evidence read NDI's
`ndi_second_pass/`, which exists only there — one checkout serves both readers
only because a full clone brings `origin/main` with it); and it exports
`NDI_MATLAB`/`DID_MATLAB`, which `find_repo` treats as authoritative. The
post-merge fallback to the default branch is ANNOUNCED in words rather than
taken silently.

`tools/status_board.py --check` additionally fails when an
`in_progress` class belongs to no decision family (an open question nobody is
tracking), when two families claim one class, or when a family cites a decision
document that does not exist.

**The status board is the answer to "where are we".** Do not reconstruct that from
the task list or from the plan documents — they disagree with each other. The plan
documents are RATIONALE (why a model was chosen); the board is STATE.

**AND SINCE 2026-08-12 THE COVERAGE LEDGER ANSWERS "HOW MUCH IS LEFT" PER CLASS, WHICH
IT DID NOT BEFORE. NOTHING ABOVE MENTIONED IT BECAUSE IT DID NOT EXIST.**
`tools/coverage.py` now derives a **COMPLETION LADDER** onto every row — `stage`, rungs
1..4, plus a `stage_rollup` in the ledger's `summary`. Re-derived here from the generated
artifact, not from the commit that added it:

        DENOMINATOR: 102 ledger rows read from schemas/V_eta_coverage_ledger.json;
                     102 classified, 0 unclassifiable
        HEADLINE  rung 1 `a migrator CONSUMES it` -- denominator 102:
                     yes 86 / no 16 / n/a 0 / NOT MEASURED 0
        by stage REACHED : 0:16  1:65  2:7  3:14  4:0
        per rung, satisfied INDEPENDENTLY of the ones below it:
                     1: 86   2: 25   3: 14   4: 0
        per-rung state counts:
          1  yes 86, no 16
          2  yes 25, n/a 3,  NOT MEASURED 74
          3  yes 14, no 11, n/a 3, NOT MEASURED 74
          4  NOT MEASURED 102

  The rung names are `coverage.py:1299-1305`: **0** source identified, **1** a migrator
  CONSUMES it, **2** its decided target classes EXIST in the build, **3** the migrator
  emits THE DECIDED targets, **4** **CORPUS-PROVEN**.

  **TWO PROPERTIES MUST TRAVEL WITH ANY NUMBER QUOTED FROM THAT LADDER, and both were
  learned the expensive way on the day it was built.**

  **(1) GOVERNANCE IS NOT IN THE COMPLETION CHAIN, AND IT USED TO BE RUNG 1.** In the
  first version the bottom rung was `disposition DECIDED`, every build rung sat behind
  it, and the tool reported the project's BOOKKEEPING as the migration's progress —
  `coverage.py:1237-1242` in its own words: *"a class with a working migrator reported
  stage 0 whenever no sign-off could be machine-found for it [...] **95 of 102 rows read
  'stage 0' while 86 of them had a migrator** consuming their documents."* Decidedness and
  builtness are ORTHOGONAL — a class can be built and unsigned (`valid_interval` was, in
  this file's own words) or signed and unbuilt (most of the decided families). Governance
  is now a FLAG in a column beside the stage (`coverage.py:1341`, four states, *"none of
  them is progress"*) and **the two must never be summed.** Note the DIRECTION that error
  pointed: pessimistic. A number nobody can act on is as useless as an optimistic one, and
  it is the third time this week the file's documented bias has run backwards.

  **(2) THE HEADLINE RUNG IS THE ONLY ONE WITH NO UNMEASURED ROWS.** Rung 1 has an answer
  on all 102 (86 yes / 16 no); rung 2 and rung 3 read `not measured` on **74** because no
  target is recorded for those rows; rung 4 reads `not measured` on **all 102** in every
  run in this container. That is why rung 1 leads the rollup, and why the tie between
  rungs 1 and 2 was broken toward the fully-measured one — stated on the record at
  `coverage.py:1279-1291` rather than left an accident of declaration order. **`not
  measured` is NEVER a `no`**: *"no corpus proved it" and "nobody looked" are different
  facts*, which is the `silentLoss` defect written into the type system.

  **SO THE HISTOGRAM MUST BE READ THROUGH WHAT STOPPED EACH CLIMB, WHICH THE LEDGER ALSO
  CARRIES (`blocked_by`, `blocked_by_state`) — AND ON THE MAJORITY IT IS A QUESTION NOBODY
  ASKED, NOT A FAILURE:**

        DENOMINATOR: 102 rows, each stopped at exactly one rung
        reached 0, blocked at rung 1, state `no`             16
        reached 1, blocked at rung 2, state `NOT MEASURED`   65   <- the bulk
        reached 2, blocked at rung 3, state `no`              7
        reached 3, blocked at rung 4, state `NOT MEASURED`   14

  Only **23** rows are stopped by positive evidence of something unbuilt (16 + 7); **79**
  are stopped by an unread rung. And quoting "16 rows at stage 0" as untouched work is
  wrong on a quarter of them: 4 of the 16 are CAPPED (a higher rung IS satisfied) and 3
  more are excused by a signed dissolution, leaving 9 `genuinely_untouched` — the ledger
  names all three sets in `stage_rollup.capped`.

**RUNG 4 HAS A CEILING, AND IT IS THE STANDING "THE CORPORA ARE A SAMPLE" RULE FINALLY
CARRYING A NUMBER.** Measured 2026-08-12 by reading all six corpus zips directly with
`did2.validate.sourceCensus`'s own reader, and recorded at
`DID-matlab tools/corpus_proven.py:59-73`:

        DENOMINATOR: 6 corpora, 221,827 v1 document(s), 0 skipped, 45 distinct
                     normalised v1 class name(s); 102 ledger rows
        addends: 20211116 1,220 + B 12,917 + Dab 27,561 + JH 78,688
                 + PRED 14 + Soph 101,427 = 221,827
          PRESENT in at least one corpus : 45   <- can read PROVEN
          ABSENT from all six            : 57   <- read NOT MEASURED, forever,
                                                  until a dataset holding them migrates
          in a corpus but not a ledger row: 0
        per corpus: 20211116 21, B 18, Dab 26, JH 15, PRED 10, Soph 32

**SO CORPUS PROOF CAN NEVER REACH MORE THAN 45 OF 102 WITH THE CORPORA WE HOLD, AND THE
45 IS ITSELF CONDITIONAL** on the run being globally clean (a corpus-level zero is a sound
upper bound for every class in it; a non-zero has to be attributed, and 25 of the 85
distinct target classes are reachable from more than one v1 source, so those are ambiguous
by construction and the tool says so instead of guessing). **THE 57 ARE UNTESTED, NOT
CLEAN — 56% of the v1 universe is outside the sample.** Put that number beside the rule
every time the rule is quoted: this file has paid four times for reading "absent from the
corpora we looked at" as "fine". **UNVERIFIED IN THIS CONTAINER:** the six figures above
come from the corpus zips and there is no MATLAB and no corpus artifact here (`find /
-name '*-summary.json'` matches only this session's own test temporaries). SETTLED BY:
`python3 tools/corpus_proven.py --schema-repo did-schema corpus-reports
tests/corpus-reports` on a real run's downloaded artifacts. Its 20 self-tests DO run here
and pass, over constructed reports.

The DID-matlab side has the same rule: `tools/census_digest.py` renders the corpus
census and `tools/test_census_digest.py` tests it in ~5 ms on the fast gate. The
census itself (`did2.validate.silentLoss`) is the instrument that finds hollow
documents; it reported zeros for two days because it was reading nothing, so
**always check `total_docs` is non-zero before believing any census number.**
The DIGEST had the same defect one layer up, and it survived one repair:
corpus run #3 (31315510527, 2026-08-09) ran six corpora for over an hour, went
GREEN on all six, downloaded five artifacts, wrote ten files — and printed
`NO CORPUS REPORTS FOUND`, then **exited 0**. Cause, from the runner's own log:
MATLAB's pwd during a corpus run is `tests/`, so reports land in
`tests/corpus-reports/`; `upload-artifact` given two search paths promotes the
artifact root to their least common ancestor (the repo root); so the download
lands them at `corpus-reports/tests/corpus-reports/` and a one-level glob
matches neither copy. *The two-path upload added to make the reports findable
is what moved them out of reach.* Now: the search is RECURSIVE over any number
of roots, **zero reports is a non-zero exit**, and the digest prints its own
denominator first (files matched, directories walked, paths read, named roots
that do not exist) so "found nothing" and "looked in the wrong place" are
distinguishable from the output alone. `test-code.yml` had the identical bug
independently — it digested `corpus-reports` from the repo root — so its
end-of-log census had been empty too. **`testCorpusPRED` also now writes a
report**: it is a hard 0-quarantine gate rather than a discovery run, so it
never went through `runCorpusDiscovery` and contributed NOTHING to the census —
a corpus we gate on but never measure is a denominator missing from every
figure we quote.

**TWO MORE DID-matlab INSTRUMENTS LANDED 2026-08-12 AND THIS FILE HAD NEVER HEARD OF
EITHER — zero mentions each until now.** Both are the same shape as `census_digest.py`:
a hand-maintained claim replaced by a generator plus a gate.

| tool | what it answers | where it runs |
|---|---|---|
| `DID-matlab tools/check_migrator_roster.py` | is every `+migrators_j` migrator in `Contents.m`, and does each have a covering test | `test-migrators-quick.yml:237` (+ its own tests at `:248`) |
| `DID-matlab tools/corpus_proven.py` | carries a corpus run's reports across the repo boundary into this repo's ladder and renders **rung 4, CORPUS-PROVEN** | `test-code.yml:307`, `test-corpus.yml:273`; self-tests on the fast gate at `test-migrators-quick.yml:205` |

`corpus_proven.py` does NOT reimplement the verdict — it invokes `DID-schema
tools/coverage.py`'s `load_corpus_evidence()` / `corpus_verdict()` across the repo
boundary, on the stated ground that *"two implementations of 'is this class proven' that
disagree is worse than one that is missing"*. What it owns is finding the reports
recursively over any number of roots, saying out loud where it looked, and CROSS-CHECKING
the rung it gets back against the census it fed in — a row marked proven whose class
appears in no census is an instrument fault, not a result. **Zero reports is a non-zero
exit**, for the reason recorded above. An instrument fault fails the step; a MIGRATION
defect (a rung coming back `no`) is report-only unless `--gate-on-failed-rung` is passed,
so a corpus failure still reaches the artifact.

## READ THESE BEFORE answering about V_eta class structure or the migration walkthrough
The conversation gets compacted and loses fine-grained state. The durable record
lives in these files — read them instead of re-deriving from memory:

- **`schemas/V_eta_tenets.md`** — the NORTH STAR: Brainstorm J's thesis + the 14 tenets
  (T1–T14, incl. T11 naming grammar, T12 "when is a new data_type warranted", T14
  "structure is declared, not conventional" — one `value` slot + inline cell layouts, T13 naming
  altitude/case). Answer
  design/naming/disposition questions FROM these, not from the class list.
- **`schemas/V_eta_tenet_audit.md`** — every persist/in_progress class bucketed vs the
  tenets: ✅ fully conceived / ⚠️ reconsider (R1–R6) / ❓ decide (the 11 boundary classes
  + deferred source folds). The go-forward worklist for closing V_eta. Its top
  **"Walkthrough decisions & build queue"** table is the live record of the item-by-item
  audit walkthrough — we DECIDE now and BATCH builds (team's request), so a decision can be
  FINAL while its build is deferred. R1 (app→software) built+green; R2/R3 (tuning collapse)
  + R6 (image standalone) now BUILT schema-side (tuning_curve/tuning_curve_calculation,
  image data_type + image_observation/_manipulation) + migrators — quick fixture gate GREEN,
  full-corpus 0-orphan re-verify **DONE + GREEN** (test-code.yml run #251 / 324b776, 2026-07-28:
  all 5 corpora 0 orphans AND 0 quarantine, 373/373 tests). STILL deferred: R4's ngrid→sampled_body
  fold (ngrid still in stable/), software dedup + openMINDS crosswalk, R5 renames, and the
  NDI second-pass assemblers (ensemble member_of+cache, raw-recording observation, timed_sequence
  decompose).
- **`schemas/V_eta_tuning_model_plan.md`** — the FINAL tuning-composite model (decided in the
  R2/R3 walkthrough; build deferred, TaskList #26). The 6 overlapping v1 tuning classes +
  5 fit shapes collapse to ONE `tuning_curve` `data_type` (independent variable = a
  `variable` per T11, not a name suffix) + an **ARRAY of `model_fit` entries** (each `{model`
  T8 term`, coefficients, goodness}`; NOT a class per fit) + ONE `tuning_curve_calculation`
  leaf. RE-AUDIT REVISED the first "single flexible bag, option A" draft: `model_fit` MUST be
  an array (freq tunings carry 5 co-existing fits), and the empirical summary scalars
  (circular_variance, ANOVA p, c50/pref/bandwidth) stay TYPED, queryable fields — NOT a
  `{name,value}` bag (flattening them was a real query regression). `stimulus_tuningcurve` =
  the fit-less `tuning_curve`. RE-TARGETS the already-shipped 12-calculator folds, so a corpus
  0-orphan re-verify is required (not assumed). NAMING PASS (final): fit entry = `{model`
  (bare bound term, not `model_name`)`, coefficients` (not `parameters`)`, goodness}`; metric
  sub-blocks `significance` / `circular_statistics` / `interpolated_values` (the `derived_summary`
  bag is killed).
- **`schemas/V_eta_recording_observation_plan.md`** — the FINAL raw-recording model (decided
  in the "voltage-attribution gap" walkthrough; build deferred, TaskList #30). A raw continuous
  recording = a `<modality>_observation` of the SPECIMEN (`subject_id`=specimen,
  `instrument_id`=the electrode/element-subject per T7, `variable`=modality voltage/current/
  image/…, body=`sampled_body`); REPLACES the loose `probe observes specimen` relation +
  bare-body path the migrators emit today. Closes the gap where raw signal was migrated as
  device-attached pieces with no typed observation + dropped modality/units.
- **`schemas/V_eta_stimulus_model_plan.md`** — the FINAL stimulus model (fresh-eyes re-audit;
  build deferred, SUPERSEDES #19). `timed_sequence` = a `data_type` (ordered+timed list of
  references to stimulus `data_type` docs — `presented_id → data_type`, broad; distinct refs +
  index-array playlist) + `timed_sequence_manipulation` leaf (`subject_manipulation` +
  `timed_sequence`; stimulator → `instrument_id` per T7). Distinct stimuli = standalone
  `visual_grating`/`image`/… docs (deduped, referenced — ensemble pattern). Multi-subject via
  `storage_mode` (shared `timed_sequence` reference). Presentation is DECOMPOSED around its
  preserved id, NOT dissolved. Moots the Hartley/sparse-noise per-type-composite question
  (stimulus type lives in the referenced doc). **Naming is FINAL, not provisional** — the
  plan's own "Resolved" section records `timed_sequence` + `timed_sequence_manipulation` as
  confirmed by the naming pass (neutral by design so a future `_observation` leaf is possible).
  This line said "provisional" long after the plan settled it; do not re-open on its word.

  **AN OPEN TEAM QUESTION FOUND 2026-08-12, AND IT IS THE ONE FINDING OF THAT PASS THAT
  POINTS THE DANGEROUS WAY: A LIVE, UNCONDITIONAL SECOND PASS EMITS THE SUPERSEDED SHAPE
  TODAY, WHILE THE SIGNED SHAPE HAS NO EMITTER AT ALL.** Recorded, not resolved —
  Operating Rule 4. HISTORICAL-SIGNOFF-CLAIM. Positive evidence, from the code:

        $ grep -n resolveStimulusPresentations \
              NDI-matlab/src/ndi/+ndi/+migrate/local.m
         714:            convertResult = resolveStimulusPresentations(convertResult, bodies, options);
        1927: function convertResult = resolveStimulusPresentations(convertResult, bodies, options)

        $ git log -1 --format="%h %ai %s" -- \
              src/ndi/+ndi/+migrate/+internal/stimulusPresentationToManipulation.m
        d5ec088e8 2026-07-22  migrate: stimulusPresentationToManipulation assembly (second pass)
        $ head -1 <that file>
        function [manipBody, bodyDoc, records] = stimulusPresentationToManipulation(...)
        %STIMULUSPRESENTATIONTOMANIPULATION Assemble a body-backed visual_grating_manipulation

  `:714` is in the second-pass chain and is not conditional — it is wrapped in a
  `try/catch` that warns and falls back to passthrough, nothing more. So a V_eta migration
  run today produces `visual_grating_manipulation`, which is the model this plan
  SUPERSEDES (`V_eta_stimulus_model_plan.md:111`, *"Supersedes #19
  (visual_grating_manipulation dissolve)"*, signed 2026-08-08 — **17 days AFTER** the
  assembler was committed, so the signature superseded a shape that was already running).

  **AND NOTHING MINTS THE SIGNED SHAPE:**

        $ cd NDI-matlab && grep -rl "timed_sequence" --include=*.m . | wc -l
        0

  **NOR CAN ANYTHING, TODAY:** `schemas/V_eta/draft/timed_sequence.json` carries
  `"abstract": true` at `:11`, and `+did2/+schema/cache.m` raises
  `did2:validation:abstractInstantiation` for any document naming an abstract class — so
  the signed multi-subject `storage_mode: reference` case, which needs a STANDALONE
  `timed_sequence` as body-of-record, cannot be instantiated at all until that flag is
  reconsidered. Both target classes are in `draft/`, not `stable/`.

  **WHAT IS AND IS NOT NEW HERE.** The plan already lists *"`visual_grating_manipulation`
  reconciliation (keep for presentation-less single gratings, or retire) — build-time"* at
  `:133`, so the reconciliation is a named item, not a discovery. **What nothing recorded
  is that the superseded path RUNS while the signed one has no emitter** — the two facts
  are in different repositories and neither file says the other half. That combination is
  a TEAM question (does the running assembler keep going, get gated, or get retired ahead
  of an emitter that does not exist yet?), and it is tracked as `V_eta_OPEN_WORK.md`
  row #31. **Do not resolve it by building, and do not resolve it by deleting.**
- **`schemas/V_eta_image_model_plan.md`** — the FINAL `image` model (decided in the R6
  walkthrough; build deferred, TaskList #24). image = a **standalone** `data_type` (raster
  value) — **`array` is KILLED** (re-audit: a bare N-D numeric grid duplicates sampled_body
  (T6) + names a container (T13), so `ngrid` phases into `sampled_body` and there is no `array`
  data_type; `image` does NOT subclass anything) across image_observation (measured) +
  image_manipulation (shown-as-stimulus); storage_mode governs only pixels
  (inline/opaque-body/reference);
  descriptors ALWAYS explicit on the composite (dtype/axes/color_model/channels) because dtype
  is NOT recoverable from an inline matrix; modality→variable; NOT an entity. Includes the
  strand-bug the build must fix.
- **BINDING GOVERNANCE (T8) — deferred follow-up, AFTER the current WIP items.** Recorded in
  `V_eta_tenet_audit.md` ("Deferred follow-up — binding governance"). Two open questions,
  evidence already gathered: (1) `subject_statement.variable`, `subject_interaction.method`
  and `interaction_purpose.purpose` are **completely unbound** (`constraints = {}`) even
  though T8 says the registry maps `variable` (and `method`+`variable`) to a value_set —
  `variable` is the key the whole system pivots on (`term.value` is `keyed_by: variable`)
  yet nothing requires `variable` itself to resolve. (2) Strength lives on the FIELD, not
  the registry: all 5 registry entries have `strength: null` while the field constraint does
  the work — decide which is authoritative before adding entries. **RE-MEASURED 2026-08-09,
  and this line is CORRECT — the count that was stale is the FIELD one.** The registry is
  populated, not empty: `binding_registry_meta.json` carries **34 rows** — 5
  `subject_statement_bindings`, 26 `relation_bindings`, 3 `entity_field_bindings` — and the
  "5 entries with no strength" are the `subject_statement_bindings` (0 of 5 carry the key;
  0 of the 26 relation rows do either). Only the 3 `entity_field_bindings` carry a strength.
  **EIGHT fields now carry a binding, not six** — `frequency_filter.algorithm` and `.band`
  were added since — and the overlap is exact and currently CONSISTENT: the 3 `dataset`
  fields state their strength BOTH on the field and in `entity_field_bindings`, and all
  three AGREE (required / required / preferred). The other five (`term.value`, the two
  `epoch_clock` fields, the two `frequency_filter` fields) exist ONLY on the field. So the
  question is live and it is not hypothetical: three facts are already stored twice, and
  they agree today by coincidence rather than by construction — nothing checks them against
  each other.

  **TWO CLAIMS IN THE PARAGRAPH ABOVE WERE STALE AND ARE CORRECTED HERE, 2026-08-11. Read
  the corrections; do not act on the paragraph.** Both were stale in the reassuring
  direction — one made a gap sound wider than it is, the other made a validator sound more
  ignorant than it is — but neither correction closes T8, and the part that is still open
  is named at the end.

  **CORRECTION 1 — "`binding` is NOT enforced by the validator yet (validateConstraints
  handles only maxLength/minLength/minimum/maximum/enum)". STALE. The machinery exists;
  only the switch is off.** `binding` is the SIXTH case in that switch, and it is gated:

        $ grep -n "case 'binding'" -A 10 \
              DID-matlab/src/did/+did2/+schema/cache.m
        1860:                    case 'binding'
        ...
        1869:                        did2.schema.cache.checkBinding(value, cval, qualifiedName);
        1870:                    otherwise
        1871:                        % Unrecognised constraint keys are tolerated;

  `checkBinding` raises `bindingValueMissing` / `bindingNodeMalformed` /
  `bindingValueNotInSet` behind `did2.schema.cache.strictMode('BindingConformance')`, and
  `tests/+did2/+unittest/testBindingConformance.m` opens with
  `testBindingConformanceIsDISARMEDByDefault` — *"the most important test in the file"* —
  asserting the default OFF rather than assuming it. **THE SWITCH STAYS OFF.** Arming it is
  a separate decision with a separate blast radius (nothing has measured how many real
  documents a `required` binding would quarantine), and it has not been made. So `binding`
  is still declarative IN EFFECT, and the old sentence's advice — cheap to get right now,
  expensive once a validator reads them — is exactly as true as it was; what changed is
  that "once a validator reads them" is now one boolean away, not one implementation away.

  **CORRECTION 2 — "`subject_statement.variable`, `subject_interaction.method` and
  `interaction_purpose.purpose` are completely unbound (`constraints = {}`)". STALE. All
  three carry `{strength: preferred, node_form: curie}`** (team sign-off 2026-08-10,
  `V_eta_tenet_audit.md`; increment 1 built). **THAT BINDS THE FORM, NOT THE VALUE SET.**
  `node_form: curie` says the value's `node` must be a well-formed CURIE; it says nothing
  about whether the term EXISTS or belongs to any admissible set. **T8's actual claim — that
  the registry maps `variable` (and `method`+`variable`) onto a value_set — REMAINS
  UNIMPLEMENTED for `variable`, the field the whole system pivots on** (`term.value` is
  `keyed_by: variable`, and that lookup reaches 5 rows, every one of them binding to
  `term_assertion`). The sign-off records this as option C, "no admissible set named yet",
  and it is BLOCKED: membership for `variable` needs NDIC.txt, which moved to
  `VH-Lab/ndi-ontology-matlab` — a repository this session could not attach. **Do not read
  correction 2 as "resolved". The form is checked; the vocabulary is not.**

  **The strength half IS decided and is now BUILT (#32, 2026-08-11).** The team signed
  *"STRENGTH IS AUTHORITATIVE ON THE FIELD, with the registry required to agree where it
  also states one"* on 2026-08-10, and on 2026-08-11 delegated the mechanism
  (*"Do binding governance as you see fit. We can always change later."*). The registry's
  `strength` is now a DERIVED column: `tools/regen_binding_strengths.py` reads it off the
  field constraint, `tools/gates.py` runs it after `build_v_eta` and before `pytest` /
  `check_binding_governance`, and `build_v_eta.py` no longer hand-authors the key at all.
  A hand-edited registry strength now fails three ways (the artifact diff, the tool's own
  `--check`, and `test_field_and_registry_strengths_agree`). **A BINDING WITH NO `strength`
  IS AN ERROR — no default, no inheritance:** `preferred` would make an ungoverned field
  read as governed and `required` would arm a gate nobody measured, so absence stops the
  generator instead of choosing. The counts in the paragraph above have also moved — the
  registry is **38 rows, not 34** (the 4 illustrative `binding_examples` were never counted),
  and **13 fields carry a binding, not eight** (it read 14 until 2026-08-12; the
  generator's own denominator is the authority and says 13), two of them NESTED
  (`relative_reference.value.relation` / `.frame`), which a top-level-only sweep misses.

  **THE 38 IS EXACT AND RE-CONFIRMED. THE 14 IS NOT, AND `.frame` NAMES A FIELD THAT
  DOES NOT EXIST.** Corrected 2026-08-12 from the generator's own denominator — which is
  the point, because this file typed a number beside a tool that prints one:

        $ python3 tools/regen_binding_strengths.py --check | head -1
        DENOMINATOR: 13 bound field declaration(s) read from 239 document_class
        file(s) (991 field declarations walked, 2 of the bindings NESTED);
        4 registry list(s), 38 row(s) (34 normative, 4 illustrative)

  Registry **38 = 5 subject_statement + 4 binding_examples + 26 relation + 3
  entity_field** ✓ exactly as recorded. Bound fields are **13, not 14** — the count is
  in the reassuring direction (one more field governed than really is), which is the
  smaller half of the error. The larger half is the NAME: the two nested bindings are
  `relative_reference.value.relation` and **`relative_reference.value.clock`**. There is
  no `frame` field on `relative_reference` — `grep -c frame` on the built schema returns
  0. **`frame` is the name the SUMMARY paragraph of the time-reference plan proposed
  ("`frame` not `clock`") and the SIGNED walkthrough section then did not adopt**: the
  signature at `V_eta_time_reference_model_plan.md:468` says *"`clock` becomes a bound
  ontology_term over FOUR terms"*, and the built schema binds `value.clock` over exactly
  four (`utc`, `dev_local_time`, `dev_global_time`, `exp_global_time`) and `value.relation`
  over all thirteen OWL-Time interval terms. HISTORICAL-SIGNOFF-CLAIM. So a reader who
  greps for `frame` finds nothing and concludes the binding is unbuilt; it is built under
  the other name. **This is the "read the plan's later sections, they supersede the
  summary" rule failing one level up — inside a correction note written to fix a
  different staleness.**

  The 13, listed so the next reader does not have to re-derive them:
  `clock_alignment_configuration.clock`, `dataset.accessibility` / `.ethics_assessment` /
  `.experimental_approach`, `epoch_bounded_reference.epoch_clock`,
  `frequency_filter.algorithm` / `.band`, `interaction_purpose.purpose`,
  `relative_reference.value.clock` / `.value.relation`, `subject_interaction.method`,
  `subject_statement.variable`, `term.value`. **`DID-matlab .../+schema/cache.m` carries
  the same stale 14** in its `case 'binding'` comment (*"14 bound fields exist in the whole
  of V_eta"*) — recorded here, not fixed there, per scope.
- **`schemas/V_eta_ngrid_family_findings.md`** — FACTS (not decisions) for group F, read from
  the real v1 writers: the RF family is **ONE** document class (`hartley_calc`; `reverse_correlation`
  + `hartley_reverse_correlation` are superclass-only, no docs, and `calculator` is a V_delta
  invention), its payload is a **two-plane** `[T×X×Y×2]` volume (STA + p-value), `element_id` IS
  populated so no NDI pass is needed for subject attribution, `ngrid` has a **second consumer**
  (`ontologyImage`) so retiring it is gated on both, `ngrid.coordinates` carries real data and is
  being **deleted** by the migrator. **`ontology_image` (F5) is FIXED**, and this paragraph's
  own account of WHY was wrong until 2026-08-09. It said NDI *redefined* `ontologyImage` so
  **TWO** vintages are both did_v1 — A (legacy `ontology_name`+`ontology_region`, dep
  `element_id`) and B (current NDI `ontology_nodes` = comma-joined multi-CURIE, dep
  `ontologyTableRow_id`, `ngrid` superclass). **THERE IS NO VINTAGE A. NDI NEVER REDEFINED THE
  CLASS.** **THE CONCLUSION HOLDS. TWO OF THE THREE CITATIONS UNDER IT DID NOT, and are
  replaced here (2026-08-11) with the check that actually establishes it.** The old text read
  *"`git log --all --diff-filter=A -- '*ontologyImage.json'` returns exactly ONE commit
  (`0ae099c`)"*. It returns **TWO**, and `0ae099c` is not one of them:

        $ git log --all --diff-filter=A --oneline -- '*ontologyImage.json'
        40b7dfbff Updated ontologyImage docs
        27daa610e Create ontologyImage.json
        $ git log -1 --format="%h %ai %s" 0ae099c
        0ae099c4a 2026-03-21 Merge pull request #716 from VH-Lab/claude/add-dataset-summary-utility

  A merge commit for an unrelated dataset-summary utility was standing as the proof. **The
  real evidence is CONTENT, and it is stronger, because it also explains what a careless
  reader would have mistaken for vintage A.** Four revisions of the path exist; three define
  the class and every one carries `ontologyTableRow_id`:

        b33d8ce64  class_name: ontologyImage   deps: ['ontologyTableRow_id']
        88096f341  class_name: ontologyImage   deps: ['ontologyTableRow_id']
        40b7dfbff  class_name: ontologyImage   deps: ['ontologyTableRow_id']
        27daa610e  class_name: spectrogram     deps: ['element_id']   <-- NOT ontologyImage

  The fourth, the "Create ontologyImage.json" commit, is a verbatim copy of the **spectrogram**
  template sitting at that path, replaced by the next commit to touch the file. So **no
  revision of the class has ever declared `element_id`** — and the one revision that does
  declare it is a different class entirely. That is almost certainly where "vintage A" came
  from. The third citation stands: `git log --all -S"ontologyRegion"` / `-S"ontology_region"`
  match only DID-side alias-table commits, never a template. NDI-matlab
  `04dcdf9` (2026-07-29) had already established the same thing while deleting four fabricated
  alias rows: *"ontologyImage created 2025-07-03, three commits total, always {ontologyNode}
  with an ontologyTableRow_id dependency. Never had ontology_name or ontology_region."*
  Vintage A came from DID-schema's own V_alpha/V_beta snapshot — the migrator's header says so
  in its own words ("legacy; DID-schema V_alpha/V_beta ancestry") and still calls it a did_v1
  vintage. It is the ground-truth-track fabrication one more time, wearing the word "legacy".
  **NOTHING IS BEING RIPPED OUT**: the migrator branches on shape and errors on no-match, so a
  branch for a shape that cannot occur simply never fires, and the tombstone's vintage-A fields
  are optional, so an absent field cannot trip `undeclaredField`. Both are safe as written and
  cost nothing. What was expensive was the RECORD — planning around a second vintage that has
  never existed. Read the disposition in `V_eta_OPEN_WORK.md` #47 ("ONE vintage, not two"),
  which was right, over this paragraph, which was not. The old `region` read matched NEITHER (it is the
  V_DELTA migrator's OUTPUT, and `migrators_j` runs INSTEAD of the V_delta migrator on a
  universalRenames-only body), so every doc became a silent husk. Now: A migrates, B PASSES
  THROUGH for the NDI second pass (a table row is not a subject), and anything else ERRORS.
  Also surfaced a systemic gap: `mustBeNonEmpty` on `depends_on` is declared everywhere and
  **enforced nowhere** (`validate/references.m` skips empty edges) — sibling to #32.
  **THAT HALF-SENTENCE IS STALE AS OF 2026-08-10 AND IS CORRECTED BELOW, at the
  invented-empty-edge entry. `references.m` still skips empty edges — that part is
  right and the code says it is right — but the enforcement moved somewhere else and
  is ARMED BY DEFAULT. Do not read "enforced nowhere" as current.**
  Evidence came from `VH-Lab/NDIcalc-vis-matlab` (added to scope; the clone is EPHEMERAL — re-add
  to re-check). **PROCESS: every remaining item in that doc is DECIDED BEFORE ANY BUILD.**
- **`schemas/V_eta_data_body_model_plan.md`** — the FINAL `data_body` tier (decided 2026-08-08 in
  the coordinates walkthrough; build deferred, TaskList #45; GATES #46). Started at "where do
  `ngrid.coordinates` go" and ended at the whole tier. ONE **axis entry** replaces THREE
  encodings of regular-vs-enumerated (`subject_interaction.sample_time.kind` /
  `sampled_body.sample_time.regular` / `axes[].regularity`) plus a fourth spelling of the same
  fact (`acquisition_epoch.axes.sample_rate` typed `frequency` vs `sample_time.dt` typed
  `duration`). **TIME BECOMES AN ORDINARY AXIS** — both `sample_time` blocks retire, and that is
  CROSS-REPO (NDI writes `sample_time` in 3 places; the STRING sweep found it, a structural sweep
  would not). `axes[]` mounts on BOTH `subject_statement` (inline) and `sampled_body` (body),
  mutually exclusive by `storage_mode` and CHECKED — statement-only is impossible because
  `pyraview` writes N bodies per statement with per-level `dt`/`t0`. **`conditions` is NOT an
  axis**: the D10 sentence "same kind of thing, distinguished only by cardinality" is WRONG
  (time is the commonest axis and has never been a condition) and `conditions` tightens to
  cardinality EXACTLY 1. `datum` collapses to `datum_type` and moves TO THE STATEMENT (the same
  `pyraview` loop indexes `dt`/`t0` by level but NOT `dataType`: extent is per-body, type is
  per-statement). NOT `data_type` — that is a CLASS with **41 direct subclasses** (38 when this was written); NOT
  `element_type` — v1 `element` has **223 hits across 95 of 1002 NDI files** (the file count read 915
  when this was written; the hit counts are as-of and were not re-derived); `datum` has ZERO v1
  meaning. **BOTH FIGURES RE-CHECKED 2026-08-12; the ARGUMENT survives both, the NUMBERS
  do not.** `data_type` now has **41** direct subclasses, not 38 (`DENOMINATOR: 247 json
  file(s) under schemas/V_eta/ read`) — it grew, so the "this name is taken" case is
  stronger, not weaker. The `element` figure is **NOT REPRODUCIBLE from its own
  description**: the denominator moved (`git ls-tree -r origin/main | grep -c '\.m$'` =
  **1002**, not 915, and `tools/coverage.py:116` already records 1,002), and no obvious
  reading lands on 223/95 — substring `element` gives 1780 hits across 177 files,
  word-boundary `\belement\b` gives 765 across 128, quoted `'element'` gives 25 across 13.
  A count whose method is not written down cannot be re-derived, which is Operating Rule 5
  arriving late: **the denominator was stated and the numerator's method was not.** Every
  reading is far above the threshold the argument needs, so `element_type` stays rejected. `data_body` gains `format` + `compression` (the unbuilt half of the 2.D "encoding
  becomes a field" decision, which `migrators_j/image.m:156-165` has been waiting on (was `:51-56`)) plus
  `filename`/`content_hash`/`description` and the `statement` edge — declared on both children
  today with OPPOSITE required-ness. `summary` is DROPPED (#68, empty + unread); `zarr` is
  DELETED not migrated (V_gamma invention, no v1 source, ZERO migrator references) and its
  `codecs[]` is NOT copied — it models per-chunk array codecs, and the live compression is
  archives (`.nbf.tgz`, `.zip`) and `tiff`+`lzw`. **CORRECTION recorded there**: a claim that
  numeric predicates inside an array of structs silently match everything was read off the
  LEGACY `+did/+datastructures/fieldsearch.m`; `did2` DOES support them
  (`compileQuery.m` → `queryable_array_elem.value_num`). ~~BLOCKED ON #32.~~
  **SIGNED AND UNBLOCKED 2026-08-14 — do not repeat the #32 block.** The plan now
  carries a `TEAM-SIGN-OFF [data_body]` line plus a walkthrough addendum and TWO
  amendments, and its own top now opens with a READ-THIS-FIRST amendment index.
  **AMENDMENT 1 REVERSES the plan's `THERE IS NO \`unit\` FIELD` line**: the axis
  carries `unit` as a bound `ontology_term`, so the D9 registry becomes a
  VALIDATION follow-up and **#32 and #115 are both OUT of the axis's path**. The
  prompt was that `spatial frequency` had no expressible canonical unit — no
  `spatial_frequency` data_type, cycles-per-degree is inverse-angle which nothing
  declares, and the registry row shape that would carry either DOES NOT EXIST
  (4 lists, no dimension key, no unit key). Angles are RADIANS, per
  `angle.value.radians`. AMENDMENT 2 restructures `conditions` for parity with the
  axis (four descriptors up, `count` flattens). Two corpus-sweep items remain and
  they gate the ENCODING FIELDS only, never the axis.
- **`schemas/V_eta_ground_truth_plan.md`** + **`schemas/V_eta_migrator_vocabulary_audit.md`** —
  THE REPAIR TRACK. Migrators were written against DID-schema's own `V_alpha` snapshot instead of
  the real NDI templates, so many read fields NO REAL DOCUMENT HAS and emit empty-but-valid
  documents that pass every gate. RULE: **NDI `origin/main` templates are the did_v1 truth; where
  template and WRITER disagree the WRITER wins; fixtures are built from the writer, never from a
  DID-side schema.** Phase 0 (ground truth extract, `tools/ndi_ground_truth.py` →
  `V_eta_ndi_ground_truth.json`) is DONE. Phase 1 is REPORT-ONLY-landed with **1.3 + 1.4
  BUILT** (the vocabulary sweep ENFORCES in DID-schema CI; `did2.validate.isFragment` closes the
  FRAGMENT mode). **1.1/1.2 are blocked on the census — which was measuring NOTHING**:
  `silentLoss` reported `total_docs=0` on all 5 corpora because `asStruct` asked `did2.document`
  for `document_properties` (the property is `documentProperties`), so every doc became `[]` and
  `toBodies` silently dropped them; `total_docs` was then taken from the survivors, making total
  failure and an empty batch identical. FIXED + tested (`testSilentLoss.m`); census must be
  RE-TAKEN. **17 offenders, not 15** — `vmspikesummary` (models a different document than exists:
  the real class is a mean spike WAVEFORM + 8 shape medians) and `vmspikefilteringparameters`
  (NO migrator at all, so it passed through into a tombstone declaring `filter_type`/`filter_window`,
  neither of which exists) were found by re-checking the detector's "mentions only" bucket. All
  BUILT: 6 fixed, 8 guarded passthroughs, 1 tombstone-only, 2 allow-listed benign.
- **`tools/check_tombstones.py`** + **`schemas/V_eta_tombstone_audit.md`** — PHASE 2b, NOT in the
  original plan. Every V_eta SOURCE TOMBSTONE compared against its NDI template: the tombstones
  were written from V_alpha too, so a passthrough would have QUARANTINED the documents it exists
  to preserve (the validator is strict BOTH ways — `undeclaredField` and `mustBeNonEmpty`).
  First run: 36 of 60 diverged. Now **BLOCKING 9 → 3** (the 3 left are `stimulus_parameter`,
  `stimulus_parameter_table`, `stimulus_presentation`, held for #31 deliberately).
  **"BLOCKING 9 → 3" IS STALE: IT IS NOW 0.** Re-run 2026-08-12, quoting the checker's
  own header rather than a sentence about it:

        $ python3 tools/check_tombstones.py | head -9
        V_eta source-tombstone check   (ground truth: NDI origin/main)
          classes compared : 67          <- the "60" above is also stale
          COLLISION        : 0
          BLOCKING         : 0   (a real document CANNOT validate)
          LOSSY            : 8   (real content has nowhere to land)
          COSMETIC         : 4   (invented declarations only)
          name reused      : 1   (image)
          skipped          : 4 nonprod, 3 chain-mixin, 17 no tombstone

  The three `stimulus_*` classes held for #31 no longer block. **LOSSY 8 is the live
  number and it is NOT zero** — `distance_metadata` and `element_epoch` are two of the
  eight, both already described in this file — so the row that matters moved from
  BLOCKING to LOSSY rather than disappearing. Direction: understating progress on the
  gating count, while the non-gating count it did not mention is where the work is.
  It reads the
  `RENAME` map, so renamed classes are compared instead of silently skipped — that hole hid
  `element_epoch`→`acquisition_epoch`, which declares `axes`/`channels`/`storage` that no NDI
  template has. THREE failure modes — hollow / passthrough / **fragment**
  (fragment is seen by NO counter). Biggest find: **`ontology_label` is NOT benign** — it
  discards the `document_id` edge (its only referent) and emits an empty `subject_id`, ~7,007
  docs, currently graded ✅ in the coverage audit. RECURRING TRAP: research agents keep claiming
  `element_id` is a dangling non-subject edge — it is NOT, `element.m` promotes elements to
  subjects with ids PRESERVED. OPEN: the `vhlab_voltage2firingrate` writer is in no repo we have
  (blocks `binnedspikeratevm`'s Hz-vs-spikes-per-bin, a silent 33× risk), and the 102-class v1
  universe may be too small (`NDIcalc-ephys-matlab` ships `spike_shape_calc`, absent from the
  ledger entirely). **LIMIT OF THE CHECKER, found 2026-08-08 — its output is a STARTING POINT,
  NOT AN INSTRUCTION.** It compares the tombstone against the NDI **template**, but the
  ground-truth rule is *where template and WRITER disagree, the WRITER wins* — and the checker
  cannot see that disagreement. Live case: it reports `ontology_image` is missing
  `ontology_node`, because `database_documents/.../ontologyImage.json` says `ontologyNode`
  (singular) — while `schema_documents/.../ontologyImage_schema.json` says `ontologyNodes` and
  `imageDocMaker.m:121-127` writes `struct('ontologyNodes', ontologyNodes)`. Following the
  checker there would have made the tombstone WORSE. Always check the writer before acting on a
  row.
- **`schemas/V_eta_time_reference_model_plan.md`** — the FINAL time model (decided in the ⑤
  walkthrough; build deferred). **8 classes collapse to 2**: `absolute_reference` +
  `relative_reference` under an abstract root. `origin` is a RELATION (an edge, T4/T7), `mode` is
  CARDINALITY (T12) — and `mode` meant TWO DIFFERENT THINGS (session = with/without metric; event
  = whole-extent/offset). T11's `<origin>_<mode>_reference` grammar is a NAMING RULE describing
  the old family, not a mandate it exist; amend T11 with the change. Both follow T14 one-`value`
  (canonical + source provenance, like `voltage`/`duration`), so `is_approximate` moves INTO the
  cell. `relation` → `ontology_term` bound to **OWL-Time** (the enum was bare char, 6 of Allen's
  13, `concurrent_with` ambiguous). `frame` not `clock` (it selects conception/birth for an
  organism as readily as dev_local_time for an epoch). `relative_to` not `event_id` (3 of 4
  referent kinds are not events). **`acquisition_epoch.clocks` DISSOLVES into time_references.**
  **NO TIMES ⇒ NO REFERENCE** (a NaN reference is a hollow document — the exact thing silentLoss
  + isFragment exist to catch). CORRECTION recorded there: `dev_local_time.t0` is NOT always 0 —
  `blackrock.m` sets it from the device hardware Timestamp; NDI's prose says the clock is SCOPED
  to epochs, not that it STARTS at zero. Volumes: 107,308 `session_relative_reference` + 20,411
  `session_bounded_reference`; epoch/event/utc classes have ZERO docs and **no migrator has ever
  emitted one**, so all epoch timing collapses to "during the session, approximately" while
  11,118 `acquisition_epoch` docs carry clock data nothing points at.
  **EVIDENCE PASS + 2 MORE DECISIONS (read the plan's later sections, they supersede the
  summary above):** NDI *already has this model* — `ndi.time.timereference` is
  `(referent, clocktype, epoch, time)`, i.e. `relative_to` + `frame`, arrived at independently;
  the `(referent, epoch)` pair collapses to ONE edge only because V_eta reifies the epoch as a
  document. The collapse is now MEASURED, not argued: the only two classes with documents are
  `{is_approximate, relation:'during'}` and the same plus `start`/`end`, and `relation` is
  `'during'` at all 14 emitter call sites — pure cardinality. **A: `relative_to` is REQUIRED**
  (team call). **A claim recorded here was WRONG and is corrected**: an earlier revision said NO
  `session` document exists anywhere, that only `session_in_a_dataset` is ever written, and that
  required `relative_to` was gated on minting one. **False.** `ndi.session.dir` creates and
  PERSISTS a session document on first open (`ndi.document('session','session.reference',...) +
  newdocument()` → `database_add`), reads it back from the database, and the coverage ledger
  already carries `session → session, persist` — a did_v1 source migrating 1:1 with its id
  preserved. So the referent EXISTS and required `relative_to` needs no prerequisite build. The
  error came from a grep that could not have matched the real call site, promoted to a claim —
  and it was then used to OVERRIDE `jSessionAnchor`'s correct note that its orphans were
  DISCOVERY-MODE (a subset batch need not contain the session doc; the edge resolves in a full
  migration). What remains is VERIFICATION, TaskList #51: read `by_class` for a `session` count
  per corpus before the build. **B: THERE IS NO `origin` FIELD and `t0` IS
  KILLED OUTRIGHT** — the anchor is not a property of the reference. Every
  `ndi.time.timereference` construction passes `0` except ONE (`tuning_response.m:92`, which
  passes `presentation_time(1).onset`, already stored on the stimulus document). So the anchor is
  either 0 (nothing to store) or an event that already has a document — point at it. My `origin`
  field recommendation was WRONG. This also CLOSES chaining: chains are normal and well-founded
  (observation → stimulus → epoch, every link a real document), terminating at an
  `acquisition_epoch`, a session, or an `absolute_reference`. **C: ONE ANCHOR PER DOCUMENT** — one
  `relative_to` + one `frame` govern both `start` and `end`; an interval whose ends are anchored
  differently (which `markvalidinterval(epochset, t0, timeref_t0, t1, timeref_t1)` permits) becomes
  TWO reference documents on the statement. Rejected nesting an anchor block per end — that is the
  inline structure removed from `acquisition_epoch.clocks`, `epochclocktimes`, `distance_metadata`
  and the tuning bag. **The model is now FULLY DECIDED; the remaining work is two DEFERRED,
  TRACKED items, not open design**: TaskList **#51** verify a `session` document is present in
  every corpus (a CHECK, not a build — see fork A) and TaskList **#52** role-name the `time_reference_#` statement edges (a bare index
  cannot distinguish start-anchor vs same-instant-other-frame vs recurrence; touches
  subject_interaction + directed_relation + every migrator writing them). Until #52 lands,
  multiple references on one statement are UNDEFINED in meaning — open item 2, recorded not
  overlooked. Also identifies `valid_interval` (an UNVERIFIED coverage row) =
  `ndi.app.markgarbage`'s record of which stretches of an epoch are good data.

  **BOTH OF THOSE "REMAINING ITEMS" ARE STALE, AND #52's IS STALE IN THE DANGEROUS
  DIRECTION — IT INSTRUCTS A BUILD THE SIGNED PLAN FORBIDS.** Corrected 2026-08-11.
  Read this; do not act on the paragraph above.

  **#51 IS ANSWERED, not deferred.** `V_eta_OPEN_WORK.md` ROW #51 -- an item number, not a
  line number; the row has MOVED TO `## COMPLETED` and its text is now at `:634-641`
  (it was `:375-383` this morning; `:375` is now the head of the new COMPLETED INDEX
  table, and `:385` is #51's one-line entry in it) -- 2026-08-09, corpus run
  31327383671: *"PASSES on all six ... 20211116 1/1, B 14/14, Dab 16/16, JH 3/3, PRED 1/1,
  Soph 33/33"* — session documents are 1:1 with the distinct `base.session_id` values, so
  the referent a required `relative_to` needs exists everywhere it would be demanded.

  **#52 IS NOT "ROLE-NAME THE EDGES" AND HAS NOT BEEN SINCE 2026-08-08.** `CHANGE 5` of the
  plan (`:642`) shrank it to ONE rule by ELIMINATION, and the elimination is the point:
  split-anchored intervals have NO INSTANCE, recurrence dissolves into N statements (T4), and
  epoch extent vs statement time are never on the same document. The one live case — SAME
  EXTENT, N CLOCKS — already carries its discriminator INSIDE the referenced document. So:

  > Within a `time_reference_#` family, every member describes the same instant or extent,
  > and `value.clock` must be UNIQUE across the family.

  **There are no `start_anchor`/`end_anchor` edges to build, and the plan says in its own
  words `DO NOT BUILD start_anchor/end_anchor until an instance appears`.** A reader who
  acted on the sentence above would build exactly the thing that was ruled out — which is
  why this correction is spelled out rather than the old text softened. `build_v_eta.py`
  says the same at `:5836` (was `:5441`): *"the rule is a uniqueness constraint, not a set of role names,
  and #52's title (\"role-name the edges\") is stale."*

  **THE REPLACEMENT RULE IS BUILT — schema side, and it is the ONLY half that is built.**
  Re-derived from the built tree, not from the commit that claims it:

        DENOMINATOR: 247 json file(s) under schemas/V_eta/ read
        schemas declaring `referent_unique_by`: 3
          stable/subject_interaction.json  time_reference_#  value.clock  (min_count 1)
          stable/directed_relation.json    time_reference_#  value.clock  (min_count 0)
          stable/epoch.json                time_reference_#  value.clock  (min_count 0)
        schema-declared time_reference edges anywhere: 4 -- the 4th is
          examples/scalar_temperature_observation_series.json, a document INSTANCE
          and not a class (the plan records that mis-read as one of Claude's two errors)

  Those 3 are declared by NAME in `build_v_eta.py` `_EDGE_REFERENT_UNIQUE`, deliberately
  not derived — *"deriving them ... would make a family silently drop out of the rule the
  day someone renames a target class"*. `tests/test_veta_time_reference_family_uniqueness.py`
  pins them. `did2.validate.silentLoss` reads the key and reports
  `family_uniqueness_violation` + a `uniqueness_denominator`;
  `did2.validate.timeReferenceFamilies` reads it too. **The rule is REPORT-ONLY IN BATCH
  BY CONSTRUCTION**: the discriminator lives on the REFERENCED document, so a per-document
  validator cannot see it and must not pretend to.

  **THE RULE HAS NEVER FIRED, AND THAT ZERO IS THE INSTRUMENT'S OWN WORDS, NOT MINE.**
  Corpus run 31464483119: `EDGE-FAMILY CARDINALITY VIOLATIONS: 0 document(s) across 0
  row(s)`, printed beside *"NOTHING IN REACH CARRIES TWO MEMBERS OF A GOVERNED FAMILY. The
  rule could not fire; the zero is 'untested', not 'clean'."* Do not quote it as a pass.

  **WHY IT CANNOT FIRE TODAY — measured over the whole DID-matlab tree, not assumed:**

        DENOMINATOR: was 260 .m file(s) under DID-matlab src/ scanned,
                     comment-only lines excluded
        -> 263 .m file(s) under DID-matlab src/ as of 2026-08-12: the demo
           collapse's migrator half added
           demo_ndi.m, demo_ndi_mock.m and private/jDemoFold.m. The sweep's
           CONCLUSION is unchanged -- none of the three writes a time_reference.
        -> 265 as of 2026-08-13: jBase.m (the central `base` block constructor)
           and +migrators_j/session.m (the class's first migrator, for the
           signed `reference` -> `local_identifier` rename). The sweep's
           CONCLUSION SURVIVES BOTH and the second one is worth saying out
           loud, because it is the first addition here that COULD have broken
           it: session.m writes no time_reference, but pyraview.m -- already
           counted -- now writes `time_reference_2` alongside its
           `time_reference_1`, so the claim "distinct N appearing as a literal:
           [1] ONLY EVER 1" below is STALE. See the epoch-extent work; PRED is
           the first corpus to carry a family of size 2.
        literal `time_reference_N` sites:  46, in 36 file(s)   (was 45 in 35;
                                            re-derived 2026-08-12, same method)
        distinct N appearing as a literal: [1]        <- ONLY EVER 1
        sites numbering a family PROGRAMMATICALLY: 1
              +did2/+convert/resolveValidIntervals.m:1000   (was :859)

  Every one of the 46 literal sites writes a single `time_reference_1` onto a DISTINCT
  emitted body — including the six files with more than one site, which are separate
  documents (`ontology_image` obs/imgObs; `treatment`/`treatment_drug`/`virus_injection`
  manip-or-dose + obs; `ontology_table_row`'s four helpers) or mutually exclusive branches
  (`jMeasurementFold.m:69` returns before `:84`). **So exactly ONE code path in the entire
  migration can emit a family of size > 1**, and it is a batch post-pass, not a migrator.

  **AND THAT ONE PATH IS THE REAL OPEN QUESTION, WHICH IS NOT ROLE-NAMING.**
  `resolveValidIntervals.m`'s split-anchor branch mints two instants when an interval's ends
  resolve to different anchors — and two anchors that differ by EPOCH while sharing a CLOCK
  satisfy neither half of the rule. The file says so itself at `:311-317` (was `:222-227`) and REPORTS it
  rather than emitting quietly. Its class is governed: `validity_observation ->
  subject_observation -> subject_interaction`, so the declared family covers it. The branch
  is predicted never to fire (every `markvalidinterval` call site passes one reference for
  both ends) and in run 31522068566 the pass saw **0 `valid_interval` documents in all six
  corpora**, so nothing has exercised it. **The corpora are a sample**: if an instance ever
  appears, what distinguishes two members that differ by epoch rather than clock is a TEAM
  decision, not a build.

  **WHAT IS ACTUALLY OUTSTANDING FOR #52 IS A SIGNATURE, NOT A MODEL — and it is the
  `valid_interval` shape (#103) one item over.** The plan's only `TEAM-SIGN-OFF` line is at
  `:468`; it heads the walkthrough section and enumerates FOUR things — the 8→2 collapse,
  anchor/extent separation, deleting value-level `approximate`, and `clock` becoming a bound
  term with `clock_tolerance`. Those are CHANGES 1–4. **CHANGE 5 is inside that section but
  is not among the four things the signature names.** `build_v_eta.py:5829` (was `:5425`) calls it
  *"CHANGE 5 (signed section, :642)"*, which is true as a statement about WHERE the text
  sits and reads as a statement about whether the rule was AGREED. Operating Rule 4 forbids
  resolving that here. Stated plainly so it is carried in the open: **the uniqueness rule is
  BUILT, and whether the signature at :468 was meant to reach it is a question for the team.**
- **`schemas/V_eta_final_class_set.md`** — the authoritative persist set (7
  categories). REGENERATE with `python3 tools/regen_final_class_set.py` (reads the
  built `V_eta/index.json` disposition markers) after every `build_v_eta.py`; never
  hand-edit. NOTE: its counts are only as good as the `disposition` markers in
  build_v_eta.py (`_RET_SOURCES`/`_RET_CARRIERS`/`_IN_PROGRESS`) — dissolved source
  classes not listed there (treatment-family, image_stack, subject_group) still show
  as `persist`; fix the markers, not the doc. CONVERSELY, `_disposition` now persists
  V_eta TARGET classes STRUCTURALLY (a `subject_calculation` leaf, or an abstract
  `data_type` composite) BEFORE the `_ANALYSIS_RE` name heuristic can retire them — the
  calc family's composites (orientation_direction_tuning, contrast_sensitivity,
  stimulus_tuningcurve, …) and `*_calculation` leaves share stems ("tuning") with the v1
  sources they consume, and were being wrongly retired. regen also routes a
  `subject_calculation`-chain class to the ④ leaf tier (not ③). Category order is fixed:
  ① spine → ② entities → ③ **composites (data_type)** → ④ leaf tier →
  ⑤ time_reference → ⑥ **data_body (EXACTLY 2: sampled_body, opaque_body)** → ⑦ infra.
- **`schemas/V_eta_6_7_walkthrough_STATE.md`** — the ⑥/⑦ (infra) walkthrough with
  per-chunk (a–e) status. Update the status table as chunks land.
- **`schemas/V_eta_nonsubject_cohesiveness_plan.md`** — decisions D-A…D-F.
- **`schemas/V_eta_go_forward_class_audit.md`** — per-class dispositions.
- **`schemas/V_eta_OPEN_WORK.md`** — the COMMITTED index of open work, and the thing `#nn`
  references in every plan document point at. Keep it current.
- The live task list (TaskList) — a working mirror of `V_eta_OPEN_WORK.md`. **IT IS NOT A
  DURABLE RECORD.** This line used to read "it survives compaction", which is true and is the
  wrong guarantee: on 2026-08-08 the container was RE-PROVISIONED mid-session (a cluster of
  `/root/.claude/` harness files rewritten at 21:18) and **all 68 tasks were wiped**, while the
  same event reset this repo's working tree 274 commits back to an older upstream revision.
  Everything PUSHED survived untouched; everything that lived only in a task description did
  not. **A finding is not recorded until it is committed.** "Compaction-safe" is not
  `git status` clean — clean only proves nothing written was left uncommitted. The check is:
  *is there anything in a task description, or in my head, that is not yet in a file?*

## Hard-won facts (do not re-litigate)
- `data_body` has EXACTLY two members: `sampled_body`, `opaque_body`. Every
  format/series carrier (`timeseries_data*`, `dataseries_data`, `zarr`,
  `ephys_zarr`, `image_zarr`, `image`, `generic_file`, `pyraview`, …) PHASES OUT
  into those two (encoding becomes a field). Never list them under data_body.
- `zarr` is a storage format (⊂ base), NOT a quantity composite.
- Composites (③) list BEFORE leaves (④). The user has asked for this repeatedly.
- must_refer is DECLARATIVE (existence-only validation), not type-checked.
- Corpus gate: 0 quarantine + 0 orphans; per-class counts shift as classes
  dissolve, total-doc counts are the invariant. Soph needs DID_RUN_SOPH_TEST=1.
- V1 SOURCE UNIVERSE = 102 (NOT 87, NOT 91). Two writers: (A) NDI production
  templates = **91 on NDI-matlab origin/main** — `tools/coverage.py` reads them from
  `origin/main` via git, NOT the working tree, because the V_eta NDI feature branch
  lags main and silently drops classes main added after the fork (ensemble,
  kilosort_clusters, kiasort_clusters, daqreader_image_epochdata_ingested — the
  first 3 now HOMED, task #21 done. D-C (#9): kilosort/kiasort_clusters now
  DECOMPOSE (count_observation + opaque_body + session anchor via
  migrators_j.private.jSorterOutput; schemas retained as a non-gating safety net,
  not yet phase-8-deleted); ensemble MODEL RE-DECIDED (`V_eta_ensemble_plan.md`,
  SUPERSEDES the old grain-A "carry the MAP doc as ⑦ infra"): per-neuron spike times =
  PRIMARY archival data (each neuron-subject, event times→sampled_body); the ensemble is
  a GROUP SUBJECT (id preserved, NO own data body) whose members are **EPOCH-SCOPED**
  `member_of` edges (T1 group-ness; re-audit: the recorded neuron set changes epoch-to-epoch,
  so each edge carries its epoch + column order — the per-epoch roster is preserved as edges,
  NOT lost to the cache); the combined (times,ids) marked-point-process = an explicitly-DERIVED,
  REBUILDABLE CACHE (`sampled_body` + `derived_from` the neurons, T10; user asked to keep
  it for fast windowed population reads, NOT as source of truth). The per-epoch MAP/legend
  doc DISSOLVES (column indices unnecessary once each train is keyed by its neuron-subject
  id; drop num_neurons/`app` superclass). **THE NEXT PARENTHESIS SAID THE SECOND PASS "needs
  the `neuron_names.txt` FILE READ". THAT PREMISE IS FALSE and was corrected in
  `V_eta_ensemble_plan.md:94-128` some time ago; this block never caught up.** The roster is
  carried as ordinary `depends_on` EDGES, not as file bytes — `origin/main
  src/ndi/+ndi/+element/ensemble.m:274-276`:

        for i = 1:numel(neuron_ids)
            mapdoc = mapdoc.add_dependency_value_n('neuron_id', neuron_ids{i});
        end
        mapdoc = mapdoc.add_file('neuron_names.txt', names_tempfile);

  The file is attached ALONGSIDE the edges; the neuron identities are already in the graph.
  So the pass needs neuron-id→subject resolution and NOTHING ELSE — which is why it could be
  built at all, and it HAS been (`NDI-matlab src/ndi/+ndi/+migrate/+internal/ensembleMembership.m`,
  `member_of` at :493-495, `derived_from` at :510-512). **This mattered: the false premise was
  the stated reason the pass had to live NDI-side, and it was quoted as justification in
  `DID-matlab tests/+did2/+unittest/testBatchPassWiring.m` until 2026-08-11.** The conclusion
  (NDI-side) survived on other grounds; the reason given for it did not. Kept as
  `member_of` + cache = NDI SECOND PASS (needs neuron-id→subject resolution; single-doc migrators carry
  files but do NOT read their bytes — confirmed via pyraview). Pass-1 keeps it a green
  passthrough; VERIFY-BEFORE-DELETE (0 stranded per-neuron trains) before dropping the
  combined bytes. (The ensemble ELEMENT → group-subject via the element migrator.)
  (B) vhlab app/calculator classes with
  no NDI template = 11 (contrast_tuning, the 3 other `*_tuning`, 7 `*_calc`), footprint
  = a bespoke migrator consuming them. Do NOT add post-v1 DID intermediate/target
  classes (zarr, directory, `*_observation`, data_body, openminds_import) to the v1
  side — provenance `origin` (`V_eta_class_provenance.md`) is the arbiter; only
  `did_v1`-origin (+ the 11 app classes) are sources. `coverage.py` also flags GAPS
  (no V_eta home + no migrator + absent from the V_zeta base = never reviewed):
  **THIS SAID "0 UNMAPPED + 4 UNVERIFIED". BOTH THE NUMBER AND THE VOCABULARY ARE STALE —
  re-derived from the ledger 2026-08-11: `gap` is False on all 102 rows and the UNVERIFIED
  bucket is gone**, replaced by a NARROWER `target_gap` that stands at **2** rows
  (`epochclocktimes`, `imageStack_parameters`), each labelled *"NO TARGET AND NO DISSOLUTION
  RECORDED -- a gap, not a decision"*. See the resolved account further down; do not quote
  the 4 as outstanding. The history of the concept is still worth keeping, because the
  failure it fixed is this file's signature error:
  the line before it read "currently
  NONE (0 gaps)", which was true only because the ledger asserted a conclusion it had no
  evidence for: every class with no V_eta home was labelled "dissolved (rename/decompose)"
  — 32 rows — turning each unknown into a reassuring claim. That was then split by whether a
  migrator actually CONSUMES the class (28 rows, genuinely accounted for) versus no home and
  no migrator (the 4 rows — `generic_file`, `imageCollection`, `imageStack_parameters`,
  `valid_interval` — labelled UNVERIFIED, all four since resolved; `subjectmeasurement` got
  its tombstone in the same pass). Separately, `_PRE_ZETA_DISSOLVED` carried a FALSE entry claiming
  `subjectmeasurement` dissolved into `measurement`. NDI never did that: it is still a
  shipped template, and `measurement` is a NEWER PARALLEL class (added 2026-01-05).
  **CORRECTED 2026-08-05 — this line said "FOUR in-tree emitters", which is numerically right
  and materially misleading: ALL FOUR are TEST-session builders** (`+test/+daq/
  build_intan_flat_exp.m`, `tests/+ndi/+unittest/+session/buildSession.m`,
  `buildSessionNDRIntan.m`, `buildSessionNDRAxon.m`; 7 files total including the template, its
  schema and `ndiDocumentAttributes.json`). There is NO production writer in-tree. That does
  NOT mean no real data exists — the corpora are a sample and older lab scripts could have
  written these — so the class still needs its migrator; DISPOSITION (team, 2026-08-05): route
  it through the `measurement` fold, no new model. The parallel-class fact this line exists to
  protect is unaffected. Every entry in that dict is an assertion about NDI and must be
  verified against `origin/main` before it is added.
  `V_eta_coverage_ledger.md` AND `.json` are generated — re-run
  `python3 tools/coverage.py` after schema/migrator changes. The web viewer's
  **Coverage ledger** panel (`web/src/Coverage.tsx`) renders the `.json`
  (sync-schemas copies it to `public/coverage.json`).
- PHASE-8 DELETION (started): `build_v_eta.py` `_DELETE_PHASE8` physically removes
  fully-consumed source tombstones from the built set (**15 deleted** — this line said 17
  until 2026-08-10, when `image_stack` and `image_stack_parameters` were RESTORED by team
  decision; re-derive with `_DELETE_PHASE8` rather than trusting any number written here).
  A class qualifies
  ONLY if its docs cannot survive migration: (a) a COMPLETED migrators_i dissolver
  (treatment family, virus_injection, subject_group — image_stack+params USED to be in
  this list and are deliberately no longer), (b)
  abstract/unminted in J (the 3 series-observation classes), or (c) a COMPLETED
  calculator composite-leaf fold — the 7 vision-calculator WRAPPERS (oridirtuning_calc,
  contrast_tuning_calc, spatial_/temporal_frequency_tuning_calc, speed_tuning_calc,
  contrast_sensitivity_calc, tuningcurve_calc) each migrate 1->1 into a `*_calculation`
  leaf (class changes), Soph+fixtures green; the RESULT class names + `stimulus_tuningcurve`
  are REUSED as persisting composites so are NOT deleted. All 17 verified
  unreferenced by any kept schema + unemitted by any migrator. HELD despite being in
  `_RET_SOURCES` (docs NOT provably consumed — deleting strands live docs):
  `element` (highest blast radius; needs a corpus per-class 0-survivor count) and
  `openminds*` (needs migrators / #9-entangled; guarded by
  test_phase1_source_cleanup_and_dep_typing — this test CAUGHT an over-eager delete).
  Deferred-calculator/carrier/to-observation retire classes STAY (docs pass through).
  The DID-matlab corpus CI (test-code.yml) is the final gate that no migrated doc
  still validates against a deleted class.
  **RE-AUDITED 2026-08-09, prompted by the `image_stack` husk.** The criterion asks whether
  a class's documents can SURVIVE migration — and `image_stack` satisfies it literally (every
  document is consumed) while 4,563 of them become observations about nobody. The criterion
  tests DISAPPEARANCE, not what replaces them. Re-checked all 17 against the census — and
  the audit below is the LAST STATE OF THE 17-CLASS SET, kept because its reasoning is what
  led to restoring two of them. **The set is now 15**: `image_stack` and
  `image_stack_parameters` were removed from `_DELETE_PHASE8`, which is exactly the outcome
  the row below argued for. HISTORICAL-SIGNOFF-CLAIM.

        DENOMINATOR: 17 deleted classes; 14 have a ledger row + a migrator,
                     3 have NO row (dataseries_/imageseries_/timeseries_observation
                     — abstract, unminted in J, so no document can exist: criterion
                     (b), sound by construction), and image_stack_parameters has no
                     migrator because it is a SUPERCLASS whose block image_stack.m
                     consumes.
        RESULT: of the emitted targets, exactly ONE appears in the empty-required-edge
                census — image_observation.subject_id, from image_stack. The calc
                family, the treatment family, subject_group and virus_injection
                produce no empty required edges, no fragments (0 in all six corpora)
                and no vacuous required fields (0 in all six).

  So the phase-8 set is clean except for the one already known — but note WHY we can say
  that: the instruments that distinguish "consumed" from "consumed into a husk"
  (`silentLoss` empty edges, `isFragment`, vacuous fields) did not exist when these
  deletions were made. The criterion did not catch `image_stack`; the census did. Standing
  caveat unchanged: the corpora are a sample.
- CALCULATORS: keep as COMPOSITE LEAFS (team decision from Lepsky et al., the
  calculator-motif paper; scope: `V_eta_subject_calculation_plan.md`). Do NOT
  DISSOLVE a `_calc` doc into observations — dissolution changes/removes its id, so
  every downstream reference DANGLES -> orphans (Soph went red with 11448 such
  orphans, 5445377; e.g. `contrast_sensitivity_calc.contrasttuning_id_* ->
  contrast_tuning_calc`). INSTEAD, a calculator output migrates 1->1, id- AND
  deps-PRESERVED, into a `subject_calculation` LEAF (`<result>_calculation` =
  `subject_calculation` + a result `data_type` composite; the fourth statement
  direction, ⊂ subject_interaction + app). Because the id is preserved and must_refer
  is existence-only, downstream refs resolve -> calculators un-defer with 0 orphans.
  DONE + green (fast fixture gates #17-#21, + the REAL orphan gate: Soph corpus
  run #2 / b3e2e10 SUCCESS 2026-07-23, ~101k docs, 0 orphans — the 11448-orphan
  dissolution failure does NOT recur): 11 of 12 vision calculators fold to
  `subject_calculation` composite leafs — the 5 tuning result classes, their 5 `*_calc`
  wrappers (oridirtuning_calc, contrast_tuning_calc,
  spatial_/temporal_frequency_tuning_calc, speed_tuning_calc), AND contrast_sensitivity
  (new composite+leaf, folds single-doc — its doc HAS element_id) — all via the shared
  `migrators_j.private.jCalculation` (result composite verbatim; input_parameters ->
  method_parameters; app kept; input -> derived_from_1). ALL 12 vision calculators now
  fold single-doc — `tuning_curve` (tuningcurve_calc + raw stimulus_tuningcurve) landed
  as migrators_j.tuningcurve_calc + migrators_j.stimulus_tuningcurve, both -> the
  `stimulus_tuningcurve_calculation` leaf (so downstream stimulus_tuningcurve_id refs
  resolve to either). **[SUPERSEDED by R2/R3 — see `V_eta_tuning_model_plan.md`: the per-tuning
  result classes + the `stimulus_tuningcurve_calculation` leaf named in this block COLLAPSED to
  the ONE `tuning_curve_calculation` leaf (+ `tuning_curve` composite); `contrast_sensitivity`
  stays on its own `contrast_sensitivity_calculation`. The id-preserving 1→1 fold mechanism +
  the 0-orphan result are unchanged — only the target leaf/composite NAMES changed.]** CORRECTION of an earlier "hard-won fact": tuningcurve_calc does
  NOT lack a subject — it IS-A stimulus_tuningcurve (v1 superclass) and inherits a
  POPULATED element_id (the writer sets it from the consumed stimulus_response_scalar,
  NDI-matlab +app/+stimulus/tuning_response.m line 499; verified against the calc mock
  doc). So element_id -> subject_id, id-preserved, NO NDI second pass needed. The raw
  stimulus_tuningcurve is the pre-calculator-framework curve (from ndi.app.stimulus.
  tuning_response); it also has element_id and folds the same way. Also: NDIcalc-vis
  `ndi.query` rename to the leaf names
  (naming B, separate repo, out of scope); `hartley`/RF -> 2.D data_body (stays deferred).
  The Soph gate (`test-soph-corpus.yml`) was repointed V_zeta->V_eta + this branch so it
  actually validates the fold. NOTE the D10
  statement-conditions field was renamed `parameters` -> `conditions` (axis =
  per-reading array, covariate = length-1); `method_parameters` holds the algorithm
  config (calculator input_parameters), a distinct slot.
- distance_metadata ~2078 JH quarantines ("required `endpoints` missing"): ROOT
  CAUSE (confirmed from the writer NDI-matlab `+setup/+conv/+haley/doImport.m` and
  the v1 template `ndi_common/database_documents/element/distance_metadata.json`):
  the v1 doc is FLAT — `ontologyNode_A/_B`, `integerIDs_A/_B`,
  `ontologyNumericValues_A/_B`, `ontologyStringValues_A/_B`, `units` — with NO nested
  `endpoints` and the numeric values genuinely `[]` (the distance lives in the
  associated `distance` timeseries ELEMENT, not the metadata doc). The migrator was
  written against an ASSUMED nested `endpoints.numeric_values` that does not exist in
  real docs → it always hits the no-vals passthrough → the flat doc fails the V_eta
  schema's required nested `endpoints` → quarantine. So the migrator NEVER worked on
  real corpus docs (its unit test used a wrong-shaped fixture). CORRECT FIX (NOT a
  casing tweak — a first camelCase attempt was WRONG and was reverted): map the flat
  A/B fields into the V_eta `endpoints` shape (integer_ids ← integerIDs_A/_B,
  string_ids ← ontologyStringValues_A/_B, node ← ontologyNode_A/_B) so it validates;
  the numeric distance is empty, so it CANNOT be a length_observation from the metadata
  doc alone. Part A (mint a measured_distance_to relation between the endpoint doc ids)
  was TRIED and REVERTED — the endpoint ids do NOT resolve in JH (4156 orphans = 2078×2,
  both endpoints dangle; the JH animal is likely an openminds_subject minting a NEW id,
  so the stored ontologyNode_A/_B are pre-migration ids), and it turned a non-gating
  quarantine into a GATING orphan failure. A single-doc migrator CANNOT mint a
  resolvable endpoint relation. DECISION: the correct rep is the NDI SECOND PASS
  (TaskList #18), which sees the migrated-id graph —
  decompose the distance timeseries ELEMENT into a length_observation of the
  graph-resolved animal subject (endpoint A), patch (endpoint B) as a spatial relation,
  consuming distance_metadata for the endpoint identities. The single-doc DID migrator
  lacks the element→subject graph + the timeseries values, so it CANNOT do this. STATUS:
  the flat→nested `endpoints` reshape (Part B of #18) SHIPPED and the ~2078 JH quarantines
  are GONE — corpus run #251 (2026-07-28) reports JH `quarantine_count: 0`, so this is no
  longer a standing quarantine. What REMAINS deferred is only the length_observation /
  spatial-relation modelling (the numeric distance still lives in the `distance` timeseries
  ELEMENT and needs the NDI second pass) — a data-completeness follow-up, not a gate.
- General migrator lesson: any NESTED sub-field a migrator reads needs a
  snake+camelCase fallback. AUDIT (this session) of every +migrators_j nested read:
  live nested multi-word reads were `syncrule_mapping.epochnode_*` (fixed) and
  `ontology_table_row.row.numeric_value` (defer WITH the D10/D11 redesign). Everything
  else reads BLOCK-level fields (snake-cased by universalRenames, safe) or PascalCase-
  by-design (metadata_editor's metadata_structure). NOTE distance_metadata is NOT a
  casing bug (see above) — it is a wrong-assumed-shape bug.

## Findings recorded here because they have no other home yet

- **`generic_file` needs `opaque_body` + a statement** (agreed in walkthrough). It is a REAL,
  PRODUCTION class — written by `+ndi/+setup/+conv/+babu/import.m` for plasmid and LCMS
  documents, read by `+ndi/+cloud/+download/downloadGenericFiles.m` — with `filename`,
  `formatOntology`, `dateCreated`, `dateUpdated`, `checksum` and a `generic_file.ext` file.
  Note V_eta
  already folded a `generic_file` concept into `opaque_body` (`test_generic_file_folded_to_opaque_body`),
  so the class name is taken — reconcile before building.

  **THE SENTENCE "It has NO V_eta home and NO migrator: a Babu dataset migrating today
  strands these" IS NO LONGER TRUE, and it is deleted rather than softened — left standing
  it reads as an argument to build a thing that exists.** BUILT and SIGNED 2026-08-11
  (`V_eta_OPEN_WORK.md`, "stranded sources"): `generic_file` folds to a `term_observation`
  + `opaque_body`, `imageCollection` becomes a tombstone, and the fold ran in 6 of 6 corpora
  in run 31522068566. It is a BATCH POST-PASS, `+did2/+convert/foldGenericFiles.m`, and
  DELIBERATELY not a per-document migrator — so looking for `+migrators_j/generic_file.m`
  finds nothing and always will. **THAT SIGNATURE COVERS TWO CLASSES, NOT THREE:**
  `valid_interval` was NOT signed, is still open, and its code
  (`+did2/+convert/resolveValidIntervals.m`) is running ahead of the decision by declaration.

  **THE LAST SENTENCE IS STALE AS OF 2026-08-12, AND SO IS THE SAME CLAIM WHERE IT REPEATS
  BELOW ("`valid_interval`'s MODEL IS STILL UNSIGNED — the board reports it as BUILT AHEAD
  OF THE DECISION"). `valid_interval` HAS A SIGNATURE, AND THE PASS IS DORMANT RATHER THAN
  RUNNING AHEAD.** Nothing is decided here — Operating Rule 4 — this records where the
  team's own record lives, because a reader acting on the stale sentence would go asking
  for a decision that exists. HISTORICAL-SIGNOFF-CLAIM. Positive evidence, from the
  generated board and from the plan document, not from prose about either:

        $ grep -c "TEAM-SIGN-OFF \[logical_observation\]" \
              schemas/V_eta_logical_observation_plan.md
        1                                   (the line is at :357, dated 2026-08-12)

        $ grep -n "valid_interval" schemas/V_eta_STATUS.md
        339: | **valid_interval** | 1 | BUILT AHEAD OF THE DECISION, AND NOW DORMANT
             BY IT. Decided AND SIGNED 2026-08-12 [...] that pass is DORMANT (census
             only, emits nothing) and the documents live on the v1 tombstone.
             Classes renamed validity -> logical

  Three consequences, each of which a reader would otherwise get wrong:
  **(1)** the class the pass will emit is **`logical_observation`**, not
  `validity_observation` — renamed 2026-08-12, so the sentence far above that describes
  its chain as *"`validity_observation -> subject_observation -> subject_interaction`"*
  names a class that no longer exists. It lives at `schemas/V_eta/draft/logical_observation.json`,
  in `draft/`, NOT `stable/`. **(2)** the pass **appends nothing**: it runs as a census.
  `+migrators_j/Contents.m` states the reason in its own words — *"the team chose to WAIT
  for `axes[]` (DID-schema OPEN_WORK #45 -> #32) rather than ship the 1->N
  one-statement-per-interval shape as an interim"*. **(3)** the target is ONE statement
  per source document carrying an ARRAY of booleans on a time axis, so it is BLOCKED ON
  `axes[]` — the same block as `data_body`, not an open modelling question.
  **This one points the file's usual direction backwards: it claims less settled than the
  record holds, and its cost is a decision re-litigated rather than a model wrongly built.**
- **THE 4 UNVERIFIED COVERAGE ROWS ARE RESOLVED AND THE BUCKET NO LONGER EXISTS.
  Re-derived from the generated ledger 2026-08-11 — the account below is HISTORY, kept
  for its writer evidence, and its two "STRANDS today" lines are FALSE NOW.** Both
  stranding classes were built, and `python3 tools/coverage.py` no longer emits an
  UNVERIFIED bucket at all:

        DENOMINATOR: 102 ledger rows read from schemas/V_eta_coverage_ledger.json
        gap = True:        0 rows      <- the old UNMAPPED/UNVERIFIED concept, gone
        target_gap = True: 2 rows      <- the replacement, and it is NARROWER

        generic_file           retire, target_source=passthrough, targets=['generic_file']
        valid_interval         retire, target_source=emitted
        imageCollection        retire, target_source=passthrough, targets=['image_collection']
        imageStack_parameters  retire, target_source=decided, targets=[]

  **THE FIX WAS A TOMBSTONE, NOT A MIGRATOR, AND THE DISTINCTION IS WHY A NAME-BASED
  SEARCH STILL FINDS NOTHING.** `generic_file` and `valid_interval` are DELIBERATELY
  without a per-document migrator (`DID-matlab .../+migrators_j/Contents.m:354`, corrected
  from `:348` — see the note below); they are
  restated from the WRITER in `build_v_eta.py`, marked `retire`, and handled by BATCH
  POST-PASSES — `+did2/+convert/foldGenericFiles.m` and `resolveValidIntervals.m`, both in
  the derived 9-pass chain above. So `ls +migrators_j/generic_file.m` fails and the class
  is fully handled: the absence is the design. **`valid_interval`'s MODEL IS STILL
  UNSIGNED** — the board reports it as BUILT AHEAD OF THE DECISION, which is a fact to
  carry in the open, not a gap to close by signing it. **[STALE — signed 2026-08-12; see
  the correction under the `generic_file` entry above. HISTORICAL-SIGNOFF-CLAIM.]**

  **THE `Contents.m:348` CITATION IS WRONG, AND IT IS WRONG IN THE WAY A CITATION CAN BE
  WORST: IT LANDS ON A REAL SENTENCE ABOUT A DIFFERENT CLASS.** Corrected 2026-08-12.
  Line 346 opens *"DELIBERATELY WITHOUT A MIGRATOR: `projectvar`"*; the sentence this
  file is citing is eight lines later:

        $ sed -n '346p;354p' \
              DID-matlab/src/did/+did2/+convert/+migrators_j/Contents.m
        346:%   DELIBERATELY WITHOUT A MIGRATOR: `projectvar`. TEAM-SIGN-OFF [misc
        354:%   ALSO DELIBERATELY WITHOUT A MIGRATOR: `generic_file` and `valid_interval`,

  So a reader who follows `:348` reads a `projectvar` sign-off and concludes the citation
  was misremembered, when the CLAIM is fully supported eight lines down. The claim stands;
  only the number was wrong. HISTORICAL-SIGNOFF-CLAIM.

  **AND THE LARGER HAZARD IS THE FILE ITSELF, NOT THE LINE NUMBER: `Contents.m` IS NOT A
  CENSUS OF MIGRATORS AND MUST NEVER BE READ AS ONE.** Measured 2026-08-12:

        DENOMINATOR: was 81 migrator .m file(s) in +did2/+convert/+migrators_j
        -> 83 as of 2026-08-12 (demo_ndi, demo_ndi_mock)
                     (Contents.m and private/ excluded)
          named anywhere in Contents.m : 43
          ABSENT from Contents.m       : 38

  Thirty-eight migrators that exist are unmentioned — `distance_metadata`, `fitcurve`,
  `syncrule_mapping`, `stimulus_presentation`, the whole `openminds_*` set, the four
  `*_tuning` classes, every `daqreader_*_epochdata_ingested`, and more.

  **THE PAIR OF NUMBERS ABOVE IS STALE IN THE WORST AVAILABLE WAY: ONE OF THE TWO IS
  STILL `43` AND NO LONGER MEANS WHAT IT SAID.** Corrected 2026-08-12, later the same
  day the block above was written. `38` went to **0** — a GENERATED ROSTER landed inside
  `Contents.m` (`DID-matlab fb38a29`, *"Contents.m named 43 of 81 migrators; the complete
  roster is now generated"*), one entry per migrator taken from that migrator's own H1
  summary, fenced between `BEGIN GENERATED ROSTER` / `END GENERATED ROSTER` markers, and
  `DID-matlab tools/check_migrator_roster.py` re-renders and diffs it as a gate. Its own
  denominator, run here:

        $ cd DID-matlab && python3 tools/check_migrator_roster.py
        DENOMINATOR: was 81 migrator .m file(s) in src/did/+did2/+convert/+migrators_j
        -> 83 migrator .m file(s) as of 2026-08-12 (demo_ndi, demo_ndi_mock);
           WITH NO TEST is now 0
        -> 84 migrator .m file(s) as of 2026-08-13: session.m. Its covering test had
           to be WRITTEN rather than found -- the roster gate counts a migrator
           covered when a quoted class-name literal appears in any test file,
           and 'session' appears as a quoted literal in dozens of unrelated
           tests, so the gate read WITH NO TEST: 0 the moment the file landed,
           without a line exercising it. testMigratorsJSession.m fills that
           hole; the gate's rule is unchanged, being sound for the other 83.
                     (Contents.m excluded); Contents.m is 64106 char(s);
                     61 test file(s) scanned in tests/+did2/+unittest
          mentioned in Contents.m:        81
          UNMENTIONED:                    0
          of the mentioned, described in the hand-written narrative
                            (outside the generated roster): 43
          with a covering test:           80
          WITH NO TEST:                   1   temporal_frequency_tuning
          pinned baseline UNTESTED:       1   temporal_frequency_tuning
        OK

  **`43` SURVIVED AND CHANGED MEANING, WHICH IS SUBTLER THAN A WRONG NUMBER.** It was
  *"named anywhere in `Contents.m`"* — the whole file. It is now *"described in the
  HAND-WRITTEN NARRATIVE"* — a subset of a file that names all 81. The two counts sat one
  line apart and only one moved, so a reader who spot-checks `43` finds it reproducible
  and reads the `38` beside it as current too. **A number that stays numerically right
  while its denominator's meaning shifts underneath it is not caught by re-running the
  number.**

  **THE CONCLUSION IS UNCHANGED AND IS WHY THE ROSTER EXISTS, so it is kept in the
  present tense: "absent from `Contents.m`" never meant "deliberately has no migrator",
  and it still does not** — that conclusion is available only from the file's three
  explicit `DELIBERATELY WITHOUT A MIGRATOR` sentences. This was the `demo_ndi` failure
  with a different query: a search whose zero result is a property of where you looked.
  **To ask whether a class has a migrator, list `+migrators_j/*.m`, read the ledger's
  `migrator` column, or read the GENERATED ROSTER — never the hand-written narrative.**

  Two footnotes to those three sentences, both of which this file had wrong:

        $ grep -n "DELIBERATELY WITHOUT A MIGRATOR" \
              DID-matlab/src/did/+did2/+convert/+migrators_j/Contents.m
        360:%   DELIBERATELY WITHOUT A MIGRATOR: `projectvar`. TEAM-SIGN-OFF [misc
        368:%   ALSO DELIBERATELY WITHOUT A MIGRATOR: `generic_file` and `valid_interval`,
        379:%   under "DELIBERATELY WITHOUT A MIGRATOR" just above. Both are restated from

  **(a) The citations `:346` / `:354` / `:365` DRIFTED to `:360` / `:368` / `:379`** — the
  roster was inserted above them. See the citation-audit entry far below, where the same
  drift is recorded against a correction that was itself written today.
  **(b) "which name four classes between them" is now THREE.** The fourth was
  `vmspikefilteringparameters`, and `Contents.m` withdrew it in its own words at
  `:384-400` (*"CITATION CORRECTED 2026-08-12. This named 'the vmspikefilteringparameters
  shape', and that class has NOT been tombstone-only since 2026-08-10: it has a migrator,
  and THIS FILE describes it at the `vmspikefilteringparameters` entry ~230 lines
  above"*), with `git merge-base --is-ancestor` showing the migrator predated the sentence
  citing its absence by 1h42m. HISTORICAL-SIGNOFF-CLAIM. The claim about `projectvar`,
  `generic_file` and `valid_interval` is unaffected and stands.

  **THE 2 REMAINING `target_gap` ROWS, which are the honest successor to this bucket** —
  both labelled *"NO TARGET AND NO DISSOLUTION RECORDED -- a gap, not a decision"*:
  `epochclocktimes` (consumed by a migrator, no tombstone) and `imageStack_parameters`
  (retire, no migrator — the FALSE ALARM below explains why it has none, and that
  explanation is still correct; what is missing is the RECORD, not the handling).

  The historical account, WRITER-CHECKED 2026-08-09 against NDI `origin/main`.
  They were not one bucket; they were three different situations, and only the checking was
  decision-free:

        DENOMINATOR: 4 rows, each searched for a template, a construction site and a reader

        generic_file           REAL, PRODUCTION.  2 construction sites in
                               +setup/+conv/+babu/import.m, read by
                               +cloud/+download/downloadGenericFiles.m. No V_eta home,
                               no migrator -> a Babu dataset STRANDS these today.
                               NOTE the name is already taken: V_eta folded a
                               `generic_file` concept into `opaque_body`.
        valid_interval         REAL, PRODUCTION.  ndi.app.markgarbage writes it at
                               markgarbage.m:93 and reads it at :130 and :141 -- the
                               record of which stretches of an epoch are good data.
                               No V_eta home, no migrator -> STRANDS today.
        imageStack_parameters  FALSE ALARM, CONFIRMED. It is a SUPERCLASS, so nothing
                               ever constructs it standalone; both production
                               converters pass its BLOCK as a name-value pair
                               (babu/import.m:475, haley/doImport.m:423) and
                               `image_stack.m` consumes it. The ledger flags it only
                               because no migrator is NAMED after it.
        imageCollection        ZERO mentions in ANY .m file on origin/main -- checked
                               as `imageCollection`, `image_collection` and
                               `imagecollection`, 0 files each. The template ships and
                               `image.json` declares an `imageCollection_id` dep, but
                               nothing in NDI writes, reads or names one.

  **`valid_interval` was nearly reported as having no writer.** `git grep "ndi.document('valid_interval'"`
  returns NOTHING, because markgarbage builds it through `session.newdocument('valid_interval', ...)`
  instead. The construction idiom is not uniform across NDI, so a writer check must grep the
  BARE CLASS NAME, never one call shape — the same failure mode as the `demo_ndi` spelling bug,
  arriving through the syntax rather than the name.

  **None of the four appears in any of the six corpora** (run 31327383671), which per the
  standing rule is NOT evidence they are unused: the corpora are a sample of datasets, and
  `generic_file` is written by the Babu converter for datasets not among them.
- **DATE OF BIRTH has no home** (TaskList #41). There is no `date_observation` leaf, and a birth
  date is arguably a property of the subject ENTITY rather than an observation of it —
  `treatment.m` already routes DOB out of its tier for that reason. Real Babu/Hunsberger DOB rows
  flow through `measurement` and currently pass through unmodelled. A team modelling call.
- **THE RECURRING EPISTEMIC ERROR, stated once so it stops recurring.** Four separate places
  turned *absence of evidence* into a reassuring claim: the coverage ledger's "dissolved
  (rename/decompose)" label (32 rows), ⑥/⑦ chunk (a)'s "all 0-usage" deletions (3 of 4 wrong),
  chunk (b)'s "the epoch link is the epochid dep" (there is no such dep), and my own "latent
  risk, not active loss" for the vhlab_voltage2firingrate family. **THE CORPORA ARE A SAMPLE OF
  DATASETS, NOT THE UNIVERSE** — a class absent from the five we test may be well represented in
  a dataset still waiting to migrate, which is what this migration is FOR. Nothing may be
  deferred, retired or half-repaired on the grounds that no corpus we looked at holds it. A
  deletion needs a WRITER CHECK against NDI `origin/main`.
- **THE SAME ERROR RAN BACKWARDS ONCE, AND IT IS WORTH THE SAME PARAGRAPH.** 2026-08-12,
  corpus run 31587869672 — the first run in which the CORPUS-PROVEN rung was computed from
  real reports. It reported **10 v1 classes FAILED**, and every one of them named one cause:

        FAILED  element    PRED: `orphan_count` is absent from the report
                                 -- NOT a zero (over 7014 document(s) in 6 corpus(es))

  **Nothing had failed.** `testCorpusPRED` is a hard 0-quarantine GATE, not a discovery run,
  so it never goes through `runCorpusDiscovery` and its report carries no
  `reference_integrity` block at all. `coverage.py`'s `corpus_verdict` appended that absence
  to `faults`, and any fault meant `no`. So *absence of evidence* became **a refutation** —
  the same collapse as the four above, pointing the other way. The direction is why it was
  caught in an hour rather than a month: this project's errors are usually reassuring, and a
  pessimistic one is conspicuous. **Both directions are the same defect. "Nobody looked" is
  a third state and must stay a third state.** Fixed: a corpus missing a counter is BLIND —
  named in the verdict, never a fault, and never a pass either (a blind corpus cannot enter
  `checked`, so a class seen only in blind corpora is `not measured`). Counters that ARE
  present are still read there, because suppressing a real quarantine because a sibling
  counter is missing would be the reassuring direction.
  `test_a_missing_counter_is_a_fault_not_a_zero` was **INVERTED, not updated** — it was
  wrong in its assertion while right in its comment, written from the same premise as the
  code, and the two agreed all the way into a production run.
- **`find_repo` FAILS SILENTLY ON A RUNNER, AND A LEDGER 11 ROWS SHORT LOOKS EXACTLY LIKE A
  LEDGER.** Same run, same log, second defect. The ledger it wrote had **91 rows** and
  reported **`rung 1: 10 yes / 81 no`**; the committed ledger has **102** and `86 yes / 16 no`.
  Reproduced exactly by forcing `DIDM = None`:

        find_repo saw DID-matlab at: /home/user/DID-matlab
        ledger: wrote schemas/V_eta_coverage_ledger.{md,json} (91 v1 classes)
        rung 1 a migrator CONSUMES it   10 yes / 81 no / 0 n/a / 0 NOT MEASURED

  `coverage.py:90` tries `$ENV`, then `/home/user/<name>`, then
  `<dirname of schema root>/<name>`. **On a runner `/home/user` does not exist**, and
  did-schema is checked out at `$GITHUB_WORKSPACE/did-schema`, so the last candidate for
  DID-matlab is `$GITHUB_WORKSPACE/DID-matlab` — *which is not the checkout, because the
  workspace directory IS the DID-matlab checkout*. `DIDM` came back None, `migrator_files()`
  returned an empty set, the 11 vhlab app classes with no NDI template were dropped, and the
  tool **exited 0 saying nothing**. It is the sibling of the shallow-clone trap CLAUDE.md
  already records for `origin/main`: not "it errored", but "it reported a smaller universe".
  `coverage.py` now announces both sibling paths FIRST, unconditionally, and names what is
  unreadable without them. **Every local run finds DID-matlab at `/home/user/DID-matlab`, so
  this is invisible outside CI — do not test the fix locally and conclude anything.**
- **A PLAN DOCUMENT'S HEADER IS NOT ITS STATE. READ THE BOTTOM, OR READ THE BOARD.**
  Sign-offs are APPENDED at the bottom of a plan document; the summary a reader stops at is
  at the top; nothing kept the two in agreement. On 2026-08-10 a mechanical sweep found
  **SIX documents asserting "NO `TEAM-SIGN-OFF` LINE" while carrying that line hundreds of
  lines below** — `V_eta_clock_alignment_cluster_plan.md` (found by accident a day earlier,
  after the family had sat unbuilt), `V_eta_epoch_plan.md`, `V_eta_ingested_payload_findings.md`,
  `V_eta_stimulus_response_model_plan.md`, `V_eta_daq_family_decisions.md`,
  `V_eta_stimulus_parameter_plan.md`, plus a partially-stale line in
  `V_eta_go_forward_class_audit.md` (two of its four proposals ARE signed).

        DENOMINATOR: 54 markdown files under schemas/, 54 read,
                     16 carrying at least one TEAM-SIGN-OFF line
        STALE:       6 documents + 1 partial

  This is the ONE-DIRECTIONAL sibling of the errors above, and the direction is what let it
  survive: the header always claims LESS progress than the record holds, so it never produced
  a wrong build — only work not done. **`status_board.py` was never fooled**, because it reads
  the signature rather than the prose; the human read the prose. That is the whole lesson —
  *when prose and a generated artifact disagree, the artifact wins* applies to a document's
  own header about itself. Now gated by `tools/check_signoff_header_staleness.py` (CI +
  pytest); a correction note that quotes the old wording is exempted by a
  `HISTORICAL-SIGNOFF-CLAIM` marker.

  **THE `54` IN THAT DENOMINATOR IS THE 2026-08-10 SWEEP'S OWN COUNT AND STAYS WHERE IT
  IS; THE CORPUS IS LARGER NOW.** Corrected 2026-08-12, and corrected BESIDE the block
  rather than inside it: a dated denominator is a measurement, and the sweep really did
  read 54 files that day, so overwriting the digit would falsify it. Re-derived here:

        $ ls schemas/*.md | wc -l
        55

        $ git log --since=2026-08-09 --diff-filter=AD --name-status \
              --format='%h %ad %s' --date=short -- 'schemas/*.md'
        ffc6fd7 2026-08-12  `validity` named a semantic, [...] it becomes `logical`
        A       schemas/V_eta_logical_observation_plan.md

  So there are **55 markdown files under `schemas/`, not 54**, and the entire difference is
  ONE document added on 2026-08-12 — nothing was deleted or renamed, which is why the
  correction is a single named cause rather than a drift nobody can attribute. The sweep's
  other two figures (16 documents carrying a signature; 6 stale + 1 partial) were NOT
  re-run and must not be read as current.

  **THIS WAS FOUND BY A MACHINE, WHICH IS NEW.** `tools/check_prose_counts.py` derives 13
  countable quantities from the tree and the generated artifacts and asks whether the prose
  still carries them; `plan_documents` is one of them. Every previous number in this file
  was corrected by a human or an agent reading carefully, which is why several went stale
  again within hours. The checker is ARMED (`--enforce` in `tools/gates.py`) as of
  2026-08-12, so a document asserting a countable number the tree does not hold now fails
  the chain instead of waiting to be noticed.

  **AND IT FIRED TWICE ON 2026-08-13, FOR TWO DIFFERENT REASONS, WHICH IS THE USEFUL
  PART.** Both are re-derived here as LIVE claims; every older figure in this file for
  these three nouns is superseded by the numbers in this block.

        DENOMINATOR: 3 countable noun(s) that moved, each re-derived from the tree

        ndi_m_files                 .m files on NDI origin/main
            $ git ls-tree -r origin/main | grep -c '\.m$' = **1003**
        veta_class_names      242   distinct V_eta class names
        veta_schema_files     248   json files under schemas/V_eta/
        265 .m file(s) under DID-matlab src/   -- jBase.m, the central `base`
            block constructor, plus +migrators_j/session.m, both added
            2026-08-13. THE SECOND ONE MOVES TWO NOUNS AT ONCE
            (`didmatlab_m_files` 264 -> 265 and `migrator_files` 83 -> 84),
            which is the same one-change-many-counters shape this block
            already records for a single schema addition.

  **The first cause was EXTERNAL: an NDI-matlab `origin/main` merge.** `ndi_m_files` moved
  1,002 -> 1,003 because main gained one `.m` file, which is a DENOMINATOR shift and
  nothing else — the did_v1 ground truth did not move (0 template diffs across the update,
  still 91 templates). Note what that means in practice: **merging the sibling repository
  can turn this repository's gate red without anyone editing this repository**, and the
  fetch alone is enough, because `coverage.py` and `ndi_ground_truth.py` read `origin/main`
  through git rather than the working tree.

  **`didmatlab_m_files` MOVED AGAIN ON 2026-08-14, 265 -> 267, AND BOTH ADDITIONS ARE
  OURS.** Re-derived from the tree, with the numerator's method written down beside it
  as the instrument-level finding at the end of this file asks:

        $ cd /home/user/DID-matlab && find src -name '*.m' | wc -l
        267 .m file(s) under DID-matlab src/
        $ git log --oneline --diff-filter=A --since=2026-08-13 --name-status -- 'src/**/*.m'
        72d6aea  A  src/did/+did2/+convert/+migrators_j/private/jDatumType.m
        37bf6a1  A  src/did/+did2/+convert/schemaVersionRank.m

  `jDatumType.m` is the `datum` -> `datum_type` normalisation map (signed sec.5);
  `schemaVersionRank.m` is the version comparison that `strcmp` was getting backwards.
  **NEITHER MOVES `migrator_files`** — `jDatumType.m` lives in `private/`, which that
  noun excludes, and `schemaVersionRank.m` is not in `+migrators_j` at all. So this is
  the one-change-many-counters shape recorded above running the OTHER way: two files
  landed and only one of the two DID-matlab nouns moved. A reader who assumes the pair
  move together will bump the wrong one.

  **AND THE SAME PASS FOUND A FALSE POSITIVE IN THE CHECKER ITSELF, which is worth more
  than the number it mis-flagged.** `V_eta_data_body_model_plan.md` says *"210 .m file(s)
  under DID-matlab src/did/+did2 scanned"* and was adjudicated DISAGREE against 267,
  because the noun's pattern matched `src/` as a PREFIX of `src/did/+did2`. **That is
  precisely the error `SCOPED_RE` exists to prevent** — *a count over a narrowed set is a
  different count, not a stale one* — arriving through the PATH instead of through a
  parenthesis, so a parenthesis-shaped guard could not see it. The pattern now carries a
  lookahead that rejects any deeper path, which recognises a subtree STRUCTURALLY and
  needs no vocabulary of narrowings. Direction: the checker was manufacturing a stale
  number where none existed — a gate crying wolf trains its readers to bump digits
  without looking, which is how a real drift gets bumped away too.

  **The second cause was OURS: minting `acquisition_reader`** (the missing sibling of
  `acquisition_metadata_reader`, so `daqreader`'s `reader_string` has a home). One new
  class moves BOTH `veta_class_names` (241 -> 242) and `veta_schema_files` (247 -> 248),
  and it also tripped the inert-set canary in
  `tests/test_veta_stimulus_response.py`, which asks for a re-derivation rather than a
  bump and got one. **A single schema addition invalidates prose counts in several
  documents at once**, so the cost of a stale number is paid per-document, not per-change.
- **THE OPEN LIST WAS RECONCILED IN BOTH DIRECTIONS ON 2026-08-12, AND THE ASYMMETRY IS
  THE FINDING: THE DANGEROUS DIRECTION WAS ALMOST CLEAN AND THE SAFE ONE WAS NOT.** Two
  passes over `V_eta_OPEN_WORK.md`, each verdict taken from a commit, a `file:line`, a
  generated-artifact figure or a test — never from the harness TaskList, which is the
  unreliable side of the comparison.

        FORWARD  (does anything called DONE turn out not to be? -- the direction
                  this file's five operating rules exist for)
        DENOMINATOR: 18 rows the mirror marked completed -- 30 37 38 43 51 54 56
                     57 58 59 63 64 65 67 70 71 75 76
          LANDED 13    PARTIAL 5    NOT LANDED 0    CANNOT TELL 0

        REVERSE  (does anything called OPEN turn out to be built? -- nobody had
                  ever asked)
        DENOMINATOR: 35 rows under `## OPEN`; 5 covered by the forward pass,
                     3 handed to build agents since (53, 61, 74), 27 unchecked.
                     All 27 checked.
          ALREADY DONE 8   (25 29 34 35 52 78 80 82)
          PARTIAL     10   (9 28 31 32 47 60 66 69 72 83)
          GENUINELY OPEN 4 (27 46 48 68)     BLOCKED 4 (45 62 73 81)
          CANNOT TELL 1    (79)

  **Together: of 30 OPEN rows checked, 11 were already built** — the 8 above plus the
  three build agents (53, 61, 74), all three of which wrote no production code because
  the work existed. **NOT ONE of the 18 rows called done was NOT LANDED.** So the list
  understated progress in eleven places and overstated it in none.

  **THE CAUSE IS MECHANICAL, NOT ATTITUDINAL, AND IT IS FOUR NAMED TELLS.** (1) *Work
  landed under a different name*: #78's build is `subjectStrainAssembly.m`, #25's is
  `softwareDedup.m`, #29's is `ensembleMembership.m` — none is a `+migrators_j/<class>.m`,
  so a name-based search finds none of them, and the same blind spot is why
  `foldGenericFiles.m` reads `no` on the ladder's rung 1. (2) *A row never revisited*:
  #80's own text begins **CLOSED 2026-08-10** and it sat under `## OPEN` for two days;
  settling it required no search at all. (3) *A phantom* — work asked for on a class
  deleted on the team's instruction, or REJECTED by a signature rather than deferred (two
  of the three are in #27 alone); carrying those as pending invites building what a
  signature forbids. (4) NEW: *a blocker dismantled in the OTHER repository and never
  propagated back*.

  **THAT FOURTH TELL IS `V_eta_OPEN_WORK.md` ROW #83, AND IT IS RECORDED HERE AS A STALE
  MARKER FOUND AND NOT FIXED.** The row reads *"NEEDS A TEAM CALL + A MEASUREMENT;
  nothing built"* and asks for a counter at `universalRenames.m`, on the stated evidence
  of *"0 hits for `database_version` across `src/` and `tests/` in DID-matlab"*. Both
  halves are wrong today:

        $ cd DID-matlab && grep -rln database_version src/ tests/ | wc -l
        10
        $ grep -n "moved_carrying_database_version\|moved_vintage_bodies_classified" \
              src/did/+did2/+convert/universalRenames.m
        114:%     moved_carrying_database_version         SINGLE-FIELD discriminators.
        151:%     moved_vintage_bodies_classified         THE CLASSIFIER'S OWN DENOMINATOR
        225:    'moved_carrying_database_version',          0, ...
        226:    'moved_vintage_bodies_classified',          0, ...

  The counter the row asks for is in the file the row nominates, with a four-vintage
  classifier beside it and five real fixtures under
  `tests/+did2/fixtures/ndi_document_vintages/`. **The `database_version` TEAM CALL is
  unaffected and is still open** — what lapsed is the row's claim that nothing was built
  and that nothing in the repository mentions the field. Not fixed here: this file does
  not own that row.

  **WHY THIS ENTRY IS HERE RATHER THAN IN THE OPEN LIST: it is the inverse of this file's
  documented bias, for the third time this week.** The bias is *"further along than we
  are"*; the plan-header staleness above, the coverage ladder's governance rung, and this
  reconciliation all point the other way. **The costs are different and neither is free.**
  Optimism produces a wrong build; pessimism produces work rebuilt, a decision
  re-litigated, and an agent dispatched at a task already finished — three for three, in
  this case. **Both directions need the same discipline, and a "safe" direction is not a
  reason to check less often.**
- **A TEST WRITTEN FROM THE SAME PREMISE AS THE CODE CANNOT CATCH THE CODE.** Three tests
  asserted the `epochid` bug (`test_phase1_source_cleanup_and_dep_typing`,
  `test_ingested_caches_epochid_dep_only`, `testMfdaqIngestedDeEncodesToDaqreaderEpochdataIngested`)
  and had to be INVERTED, not updated. The `silentLoss` counter had NO tests at all and shipped
  measuring nothing. `testFragmentCensus`'s first draft drove the detector through two migrators
  that had since been repaired, and failed correctly. Same shape as fixtures built from our own
  schema, one level up.
- **V_eta IS snake_case; NDI IS camelCase. A DISPOSITION THAT RESTS ON *ABSENCE* MUST USE
  NDI'S OWN SPELLING.** On 2026-08-06 `demo_ndi`/`demo_ndi_mock` were dispositioned DELETE
  on the evidence *"absent from NDI origin/main; referenced by NOTHING — not even the test
  suite."* Both claims were FALSE. The class is spelled **`demoNDI`**, both templates ship,
  and `+ndi/+calc/+example/simple.m` queries `demoNDI.value` and constructs `demoNDIMock`
  documents at five lines. **The grep searched `demo_ndi` against a repository that has
  never contained that string** — zero hits was a property of the query. This is the
  failure the operating rules name verbatim: *"a grep that could not have matched was
  reported as 'this does not exist anywhere'."* It survived a walkthrough, a commit and a
  board render, and was caught only because two documents happened to disagree.
  The mechanical version of the check, re-runnable: normalise both sides (lowercase,
  strip underscores) and list every V_eta name that matches an NDI name ONLY after
  normalisation.

        DENOMINATOR: 91 NDI template class_names, 224 V_eta class names
        AT RISK: 6
           demo_ndi <-> demoNDI                  <- THE BUG
           demo_ndi_mock <-> demoNDIMock         <- THE BUG
           ontology_image <-> ontologyImage             disposition rests on PRESENCE
           ontology_label <-> ontologyLabel             disposition rests on PRESENCE
           ontology_table_row <-> ontologyTableRow      disposition rests on PRESENCE
           spike_interface_sorting_outputs <-> SpikeInterfaceSortingOutputs   PRESENCE

  The other four were dispositioned from what they CONTAIN, so only `demo_ndi` was
  absence-based. **Re-run the sweep before any new disposition that turns on absence.**
  Sibling to the `depends_on` rule below: that one is about the KIND of reference, this
  one is about the SPELLING of the thing referenced.

  **THE SWEEP ABOVE WAS RE-RUN 2026-08-12, AS ITS OWN LAST SENTENCE INSTRUCTS, AND
  EVERY NUMBER IN IT HAS MOVED. Its recorded result is HISTORY — do not use the
  six-row table as the current at-risk list.** The V_eta side grew by 17 classes, and
  the two rows that WERE the bug are gone while three new rows arrived:

        DENOMINATOR: 91 template json file(s) on NDI origin/main, 0 unparseable
                     -> 91 distinct NDI template class_names
                     247 json file(s) under schemas/V_eta/ read
                     -> 241 distinct V_eta class names   (the note above said 224)
        AT RISK (match ONLY after lowercase + strip-underscores): 7, not 6
           image_collection <-> imageCollection                <- NEW
           image_stack <-> imageStack                          <- NEW
           image_stack_parameters <-> imageStack_parameters    <- NEW
           ontology_image <-> ontologyImage
           ontology_label <-> ontologyLabel
           ontology_table_row <-> ontologyTableRow
           spike_interface_sorting_outputs <-> SpikeInterfaceSortingOutputs

  `demo_ndi` and `demo_ndi_mock` are **no longer V_eta class names at all** (0 files
  under `schemas/V_eta/` declare either), while `demoNDI` and `demoNDIMock` both still
  ship on NDI `origin/main` — so the pair that taught the lesson has dropped out of the
  instrument that records it. The three new rows are the `image_stack` /
  `image_stack_parameters` restoration of 2026-08-10 plus the `imageCollection`
  tombstone, i.e. **the sweep gained rows because work landed, and nobody re-ran it.**
  That is the direction this file is NOT known for: the recorded list reads SAFER than
  reality — three camelCase/snake_case collisions that an absence-based grep could
  trip over were absent from the at-risk table for two days.

  **A SECOND STALE MARKER FROM THE SAME COLLAPSE, FOUND 2026-08-12 AND RECORDED NOT
  FIXED.** The pair that taught this lesson is gone from the schemas and is still named in
  the builder:

        $ sed -n '7284,7286p' tools/build_v_eta.py
        _IN_PROGRESS = {"app", "stimulus_presentation",
            "demo_ndi", "demo_ndi_mock",
            "projectvar", "ensemble"}

        DENOMINATOR: 247 json file(s) under schemas/V_eta/ read
        class names containing "demo": 1 -- `demo`, at stable/demo.json

  `build_v_eta.py:1864` performs the collapse in the same file (`for _gone in ("demo_ndi",
  "demo_ndi_mock", "mock")`, *"3 classes -> 1. `mock` and `demo_ndi_mock` cease to
  exist"*, team decision 2026-08-06), so one half of the file removes the classes and the
  other half still lists them as decided-pending. **The marker is INERT rather than
  wrong-in-effect** — `_disposition(name)` is only ever asked about names that exist, so a
  membership test for a name nothing declares can never fire — which is exactly why it
  survived a build, a regen and a board render. **It still misreports the final class
  set's inputs to anyone reading the markers instead of the tree**, which is the failure
  mode `V_eta_final_class_set.md`'s own note warns about one direction over ("its counts
  are only as good as the `disposition` markers"). Not fixed here, per scope; this file
  records it so the next person to touch `_IN_PROGRESS` finds it.

  A cross-check on the prose itself, same run: of **246** distinct backticked
  identifiers in this file, **79** name a real NDI or V_eta class exactly and **5**
  match one only after normalisation — `dataType`, `demo_ndi`, `demo_ndi_mock`,
  `epoch_id`, `imagecollection`. All five sit in sentences that are ABOUT the spelling
  difference, so there is no live mis-spelling in this document. The check is cheap;
  re-run it rather than assume that stays true.

- **A `depends_on` SWEEP IS NOT A REFERENCE CHECK. Grep for the NAME too.** Three times in one
  session (2026-08-05) a dependency-graph sweep came back empty or nearly empty while the real
  references were **string matches in ordinary fields**, and each time the "nothing references
  this" reading would have produced a DATA-LOSING decision:
  - `daqsystem` — `daqsystem_id` is referenced by NOTHING. But `daqsystem.base.name` is matched
    by `strcmpi` in `+ndi/+daq/system.m:229` (`getprobes` attributing probes to devices), named
    in every `syncrule.parameters.daqsystem1_name`/`_2_name`, and queried by `exact_string` in
    `+ndi/+time/syncgraph.m:404-408`. Dissolving it would have broken probe→device attribution.
  - `syncrule_mapping` — the same `syncgraph.m:404-408` query reads
    `epochnode_a/_b.objectname`, a field V_eta had already DROPPED, alongside a `syncgraph_id`
    edge V_eta had also dropped. A live in-tree query, broken two ways.
  - `epochid` — only `ensemble` references an epoch by EDGE. But `epochid.epochid` is matched by
    `exact_string` at **11+ live sites** (`+daq/metadatareader.m:164`, `+daq/reader.m:56`,
    `+element/timeseries.m:58`, `stimulusDocMaker.m:390,412`, `add_stimulus_approach.m:54,64`,
    `+app/spikeextractor.m:156,310,388`, `+app/+stimulus/decoder.m:114`,
    `finddocs_elementEpochType.m:32`), and **15 NDI classes carry the `epochid` superclass**.
    It is the join mechanism for the epoch-scoped half of the database.
  **Before any disposition: grep the class's `base.name`, its id STRING, and its distinctive
  field names across NDI `.m` files — not just `<class>_id` in the templates.** v1 joins by
  string wherever the referent is not itself a document, which is most of the interesting cases.
- **RE-DERIVED 2026-08-09 from corpus run 31327383671 — the first census that was actually
  READABLE (the digest had been aggregating nothing). The row set is now TWO rows, 7,233
  documents, and the composition is almost entirely different from the six below:**

        DENOMINATOR: 6 corpora, 0 unreadable, 0 skipped
        stimulus_presentation.element_id   2,670   B 1242 / Dab 1242 / Soph 175 / 20211116 11
        image_observation.subject_id       4,563   JH 4563                      <- NOT IN THE
                                                                                  TABLE BELOW
        TOTAL                              7,233

  **RE-CONFIRMED INDEPENDENTLY 2026-08-10, corpus run 31415147934 (`02854c7`): the same two
  rows, the same 2,670 + 4,563 = 7,233, over 562,448 documents inspected across 6 corpora,
  0 unreadable / 0 skipped, quarantine 0, fragments 0, vacuous required fields 0, edge-family
  cardinality violations 0.**

  **THE DENOMINATOR IN THIS PARAGRAPH SAID 562,422 AND WAS WRONG, AND THE SENTENCE THAT
  FOLLOWED IT — "this total is no longer hand-summed" — WAS ALSO WRONG, ABOUT ITSELF.**
  Corrected 2026-08-10 with the addends named, which is the whole repair:

        20211116  1,484  +  B  13,804  +  Dab  29,168
        +  JH  336,136  +  PRED  31  +  Soph  181,825   =  562,448

        recorded    562,422
        difference       26   =  B `inspected` 13,804 - B `migrated_count` 13,778

  The old figure is the six corpora with **corpus B's `migrated_count` substituted for its
  `inspected`**. B's own block prints both, one line apart (`total=12917 migrated=13778`,
  then `silent-loss: inspected 13804`), and the wrong one was picked up once and then quoted
  forward. And the digest could not have produced either number for that run:

        $ git log --oneline -S"ACROSS ALL CORPORA" -- tools/census_digest.py
        f9defe3 Digest: compute the cross-corpus total instead of asking a human to
        $ git show 02854c7:tools/census_digest.py | grep -n "ACROSS ALL CORPORA"
        exit=1

  `02854c7` is the run's head; `f9defe3` is the NEXT commit. The rollup did not exist yet, so
  the total was hand-summed by the same paragraph that claimed it was not — a reassurance
  about an instrument, standing in for the instrument. That is this file's own recurring error
  arriving one level up, and the direction is the usual one: a wrong number that reads as
  better-measured than it was.

  The rollup is real NOW and it prints its addends beside the total, each named, with the
  counter identified as neither `migrated` nor `total` — so the identical substitution is
  visible in the output rather than sourceless. `tools/test_census_digest.py` asserts BOTH
  sums, the right one and the one the substitution produces, so this account cannot go stale
  quietly. The instruction below to "re-derive the row set from a fresh census before quoting
  a total" still stands, and now applies to the total itself: **quote the digest's printed
  rollup, never a sum you performed.**

  **RE-MEASURED 2026-08-11. THE PREDICTION HELD, AND THE WHOLE ROW SET IS NOW ZERO.**
  This paragraph used to say the JH row of 4,563 was a *pre-guard* figure and that the
  guard taking it to zero was "a prediction, not a result". It is now a result. Corpus run
  **31464483119** (`52806b5`, all 7 jobs green, digest included), quoting the digest's own
  printed rollup rather than a sum performed here:

        DENOMINATOR: 6 corpus report(s) summed; 6 carried a readable silent-loss audit;
                     633432 document(s) inspected in total
        addends -- silent-loss `inspected`, NOT `migrated` and NOT `total`:
        20211116 1640 + B 14181 + Dab 30354 + JH 332916 + PRED 37 + Soph 254304 = 633432
        quarantined: 0       fragments: 0

        EMPTY REQUIRED EDGES:                0 document(s) across 0 row(s)
        VACUOUS REQUIRED FIELDS:             0 document(s) across 0 row(s)
        EDGE-FAMILY CARDINALITY VIOLATIONS:  0 document(s) across 0 row(s)

  So BOTH standing rows are gone: `image_observation.subject_id` (4,563, JH) and
  `stimulus_presentation.element_id` (2,670). The 7,233 total above is HISTORY — do not
  quote it as outstanding work. The denominator moved 562,448 -> 633,432.

  **THE NDI-REQUIRED / V_eta-OPTIONAL BUCKET RAN FOR THE FIRST TIME** and answers the
  question that motivated it (is `ontology_label.document_id` blank on any fraction, since
  it is the join key the deferred second pass needs?):

        633432  documents classified
            32  classes whose chain carries the marker
             7  classes declaring a RELAXED edge (7 distinct class/edge pairs)
         20850  documents declaring one
         20850    populated
             0    EMPTY  <-- the count

  **Mind the gap between 26 and 7.** The schema-side census found 26 divergences; only 7
  appear in these six corpora at all. The other 19 are UNMEASURED, not clean.

  **TWO ZEROES IN THAT RUN ARE NOT CLEAN AND THE DIGEST SAYS SO ITSELF.** Edge-family
  UNIQUENESS reports 0 violations and then prints *"NOTHING IN REACH CARRIES TWO MEMBERS OF
  A GOVERNED FAMILY. The rule could not fire; the zero is 'untested', not 'clean'."* And the
  epoch family is still unbuilt, with the size of it measured: **0 `epoch` documents in the
  batch, 0 `epoch_id` edges found, 305,480 time references terminating at a non-epoch
  document.** That last number is the one the epoch decision rests on.

  **THIS SAID "STILL TO CHECK": the digest reported "BATCH POST-PASSES: 2 expected in a
  V_eta run" and measured only `epochMint` and `resolveSessionAnchors`, and the question
  was whether the expectation was stale or only two passes really ran. IT IS CHECKED,
  ANSWERED AND NOW GATED (2026-08-11).** The expectation was stale, and the answer is
  NINE. The digest no longer carries a list of its own: `harness_pass_chain()` DERIVES the
  expected set by reading what the corpus harness actually composes, and `POST_PASSES` is
  demoted to a render table used only as an announced FLOOR when the derivation fails.

        DENOMINATOR: convert package .../+did2/+convert -- 15 .m file(s) read,
                     9 batch post-pass signature(s); call sites runCorpusDiscovery
                     (1526 lines, was 1428) and testCorpusPRED (368 lines, was
                     365), 10 pass(es)
                     composed each (9 + v1_to_v2, excluded by signature)
        chain, in call order: resolveDeferredBaths, resolveOpenmindsCitations,
                     resolveDatasetEntities, epochMint, resolveSessionAnchors,
                     resolveResponseParameters, resolveLawnPlateSubjects,
                     foldGenericFiles, resolveValidIntervals
        renderable 9   unrendered 0   unmeasured 0   not_in_chain 0

  **AND IT IS A GATE, NOT A WARNING.** A pass that runs over the whole corpus and attaches
  no report used to print `*** MEASURED BY NOTHING` and then exit 0. It now exits non-zero.
  Four conditions are armed with SEPARATE sentinels rather than one tidy gate, because they
  are different severities: `unmeasured` (nothing reaches any artifact), `unrendered` (the
  numbers are in the zip, the digest is blind), `not_in_chain` (counters printed for a pass
  that does not run — the reassuring direction), and the FLOOR path, where the other three
  report **NOT EVALUATED rather than 0** because on that path they are 0 by construction —
  a property of the render table, not a fact about the harness. Arming was gated on the
  count already being 0; it was, measured before anything changed.

  **The gate is evaluated ONCE**, in `digest()`, though three sites render the same derived
  fact — firing at each would count one defect three times in a six-corpus run and once in
  a one-corpus run. **UNVERIFIED, and it is the load-bearing gap:** every run above used
  SYNTHETIC reports. This container has no MATLAB and no corpus artifacts, so the armed
  gate has never been exercised against a real one.

  FIVE of the six rows below are now ZERO — the stimulus-response, epochfiles, syncrule
  mapping, openminds_stimulus and daqmetadatareader repairs all landed and are confirmed on
  real data (Soph's 11,167 alone). `stimulus_presentation.element_id` is unchanged at 2,670,
  which is a useful agreement between the old figure and the new instrument.
  **`image_observation.subject_id` is a NEW row, larger than four of the six originals, and
  its cause is NOT the pattern below**: NDI's own writer leaves the edge empty. Three of the
  seven `ndi.document('imageStack'...)` sites in `+setup/+conv/+haley/doImport.m` (lines 789,
  811, 827 — the image / mask / closest-patch loop) set ONLY `document_id`, never
  `subject_id`, so the source documents genuinely have no subject and `image_stack.m:189-200`
  (was `:48,78`) copies that emptiness into a required edge with no guard. The guarded-passthrough fix used
  for `fitcurve` / `openminds_stimulus` / `probe_geometry` DOES NOT APPLY UNCHANGED: both
  `image_stack` and `image_stack_parameters` are phase-8 DELETED, so passing a document
  through gives it no schema to validate against — 4,563 quarantines, the
  `epochfiles_ingested` regression exactly. Needs a team call, not a build.

  **THE TEAM CALL WAS MADE AND THE BUILD LANDED. The paragraph above is history — do not
  act on it.** Team decision 2026-08-10, verbatim: *"You can do option A now, C later for
  the E. coli images."* Option A = reverse the phase-8 deletion so the subject-less arm
  passes through; option C = resolve the subject in the NDI second pass, still deferred.
  Both classes are OUT of `_DELETE_PHASE8` (commit `49ba381`), their tombstones build into
  `deprecated/`, the guard is live at `migrators_j/image_stack.m:248` (was `:78`), and NOTHING is
  required on either tombstone — both deps optional, zero required fields — so a
  subject-less document cannot trip `mustBeNonEmpty`.

  **This entry is corrected in the DANGEROUS direction, which is why it is spelled out
  rather than deleted:** left standing, it reads as an argument for re-deleting two classes
  that were deliberately restored, and it would be read by someone tidying `_DELETE_PHASE8`.
  The phase-8 count in the section above is likewise stale — **15, not 17**.

  **A REAL DEFECT WAS FOUND IN THE RESTORED TOMBSTONE, 2026-08-10.** It declared file
  `imagestack_file`; NDI writes **`imageStack`** — template `"file_list": ["imageStack"]`,
  and `add_file('imageStack', ...)` at all EIGHT attachment sites (`haley/doImport.m`
  441/469/485/504/797/815/831, `babu/import.m:483`), no exceptions. The restatement took
  deps and fields from NDI and then snake_cased the one part a passthrough carries
  VERBATIM: `universalRenames.m:628` (was `:308`) skips the structural keys outright
  (`skip = {'document_class','depends_on','file','files'}`). So the tombstone declared a
  file no document has WHILE the file every document has was undeclared — both directions
  of the file audit at once, on every passed-through JH document.

        DENOMINATOR: 91 NDI templates read from origin/main; 20 V_eta schemas
                     declare a file (was 19; re-derived 2026-08-12 over 247
                     files); 1 mismatch among classes with a did_v1
                     template -- image_stack.

  Nothing was looking: `fileList.m` compares by exact `strcmp` (`:93,99`),
  `check_tombstones.py` does not compare files at all, and every `image_stack` fixture in
  `testTemplateLiteralTypeTraps.m` is built without a `files` block. A green tombstone run
  and four green MATLAB tests all missed it. **When restating a tombstone, the `file` block
  is did_v1 spelling like the rest — it is not renamed on the way through.**

- **THE INVENTED-EMPTY-EDGE PATTERN — the historical row set, KEPT FOR ITS SHAPE, NOT ITS
  NUMBERS.** It read "26,406 documents across FIVE classes from the census, plus a SIXTH
  added 2026-08-08 from a walkthrough histogram (openminds_stimulus, 635)". Re-derive the row
  set AND the sum from a fresh census before quoting either — see the re-derivation above.
  ONE cause. V_eta
  declares a REQUIRED `depends_on` that the NDI template does not have, while DROPPING the edge
  NDI does write. Every such document validates clean, because `+did2/+validate/references.m:90`
  SKIPS empty edges (`if isempty(documentId), continue;`) — so `mustBeNonEmpty` on a `depends_on`
  is decorative:

        stimulus_response_scalar_parameters_basic.stimulus_response_scalar_id
                                      11,440 docs  (Soph 11167 / 20211116 273)  NDI has the edge the OTHER WAY
        epochfiles_ingested.epochid    6,921 docs  (Dab 4088 / B 2484 / Soph 349)   NDI has filenavigator_id
        syncrule_mapping.epochid       5,316 docs  (B 2484 / Dab 2484 / Soph 348)   NDI has syncgraph_id
                                       ^^ REPAIRED 2026-08-09 (#58): the schema now declares
                                          syncgraph_id + syncrule_id, and objectname/t0_t1 are
                                          carried again. Row kept so the pattern's history stays legible.
        openminds_stimulus.stimulus_id   635 docs  REPAIRED 2026-08-09 (#71): pass 1 now emits
                                          nothing and passes the document through guarded; the
                                          tombstone declares stimulus_element_id.
        stimulus_presentation.element_id
                                       2,670 docs  (B 1242 / Dab 1242 / Soph 175 / 20211116 11)
                                                                            NDI's dep is named stimulus_element_id
        daqmetadatareader.daqsystem_id    59 docs  (100% of them)            NDI has NO deps at all


  **This line said "12,296 documents, three classes" until 2026-08-06 — an undercount by more
  than half, and it named the three SMALLEST.** The two stimulus-tier rows were found by the
  stimulus response walkthrough reading the same census (test-code.yml run #257 / 0458dae,
  2026-07-29) the original three came from; they were in the report all along and nobody had
  looked past the daq/sync families. The largest instance of the pattern is the one this note
  omitted. **Re-derive the row set from a fresh census before quoting a total.**
  In each case the count EQUALS the class's document count — 100% empty, never partially.
  `ontology_table_row`'s 76,766 empty `subject_id`s (#53) are the same failure one layer up.
  The blind spot is that `check_migrator_vocabulary.py` compares FIELDS and not `depends_on`
  (#54); the fix that would stop all of them is enforcing `mustBeNonEmpty` on edges (#37); the
  repairs are #53, #58, #61 and the ones recorded in `V_eta_epoch_plan.md` +
  `V_eta_stimulus_response_model_plan.md` (`stimulus_presentation.element_id` rides with the
  stimulus model, #31/#43). **Treat these as ONE problem, and check a new required edge against
  the NDI template before adding it.**

  **"THE FIX THAT WOULD STOP ALL OF THEM IS ENFORCING `mustBeNonEmpty` ON EDGES (#37)" READS
  AS OUTSTANDING WORK. IT IS BUILT AND ARMED BY DEFAULT, since 2026-08-10.** So does the
  sentence directly above it — *"`+did2/+validate/references.m:90` SKIPS empty edges … so
  `mustBeNonEmpty` on a `depends_on` is decorative"* — and so does the one in the `ontology_image`
  entry far above. All three are corrected here rather than edited away, because the
  half of them that is still TRUE is what made them survive: `references.m` really does
  skip empty edges, and the code now explains why that is CORRECT rather than a hole.
  This is the file's documented direction inverted — three sentences claiming LESS
  enforcement than exists, whose cost is a fix rebuilt, not a gate wrongly trusted.

  Positive evidence, from the two files themselves:

        $ sed -n '90,105p' DID-matlab/src/did/+did2/+validate/references.m
        90:        if isempty(documentId)
        91:            % THE LINE #37 IS ABOUT -- AND IT STAYS. It was read for a
        92:            % long time as the reason `mustBeNonEmpty` on a depends_on
        93:            % was decorative. It is only half the reason, and it is the
        94:            % half that is CORRECT: an edge with no id names no
        95:            % document, so it cannot dangle, and this function is the
        96:            % ORPHAN check. It is also handed no schema, so it cannot
        97:            % know which edges were declared required [...]
       101:            % The actual hole was that did2.schema.cache/validateDocument
       102:            % never looked at depends_on AT ALL. That is where the check
       103:            % now lives, behind
       104:            % did2.schema.cache.strictMode('RequiredDependencies')

        $ grep -n "'RequiredDependencies'" DID-matlab/src/did/+did2/+schema/cache.m
         787:            if did2.schema.cache.strictMode('RequiredDependencies')
         967:                    'RequiredDependencies', ...
         968:                        ~did2.schema.cache.envFlagIsOff('DID_ENFORCE_REQUIRED_DEPENDENCIES'), ...

  `~envFlagIsOff` means **ON unless explicitly disabled** — the opposite polarity from
  `BindingConformance` (#32), which uses `envFlag` so that unset and a typo both leave it
  OFF. `cache.m:72` states the arming and its price in one line: *"#37 RequiredDependencies
  ARMED -- 7,233 measured cost, ON PURPOSE"*. `NonVacuousFields` (#38) is armed the same way.
  So of the three switches, TWO are on by default and one is off, and this file described all
  three as off. **#37 is no longer the fix to build; it is a gate to reason about when a new
  required edge is added.**
- **WHEN AN INLINE VALUE STAYS ALONGSIDE ITS EDGE — and when only the edge survives.** Two
  decisions on 2026-08-05 went OPPOSITE ways and neither is a precedent for the other, so the
  test is written here rather than in one plan document. `strain` KEEPS its inline
  `term.value = {node, name}` AND gains `strain_id`; `epochid` is DROPPED ENTIRELY in favour of
  `epoch_id`. Three questions decide it:
  1. **Is the inline value a complete fact on its own?** A CURIE naming a real thing (`WBStrain:
     00000002`) is; a bare local id (`"t00023"`) is not.
  2. **Will the referenced document always exist?** 115 strains carry no identifier and may
     warrant no document, so the assertion must stand alone. One `epoch` is minted per distinct
     id, by construction, so its edge cannot dangle.
  3. **Is the value the document's CONTENT or a JOIN KEY?** A `term_assertion` *is* a statement
     about its value — strip it and the document says nothing. An epoch id is stapled on — strip
     it and the document still says everything it said.
  **The drift test is what actually decides it** (`V_eta_openminds_family_record.md` Part 3: a
  representation must not vary between datasets). Dropping strain's inline value would make
  `variable: strain` resolve two ways depending on whether a pedigree happened to exist.
  Dropping `epochid` creates no drift, because every epoch-scoped document gets its edge
  uniformly. In one line: **strain — the value IS the fact and the document is optional extra
  structure; epoch — the document IS the fact and the string was only ever a way to find it.**
- **THE CITATION AUDIT, 2026-08-12 — every `file:line` reference in this document, checked.
  Thirteen had drifted. THE INLINE CITATIONS HAVE BEEN REPOINTED AND THE OLD VALUE IS
  RECORDED BOTH BESIDE EACH ONE AND IN THE TABLE BELOW**, because this file's own doctrine
  is that *a drifted line number is worse than none: it looks precise*. Leaving twelve wrong
  numbers in place while recording them elsewhere would have kept the trap and added a
  footnote.

        DENOMINATOR: 59 distinct file+line citations extracted from this document
                     (DID-schema 9, DID-matlab 16, NDI-matlab 34)
          verified EXACT, the cited line still says what the sentence claims : 45
          DRIFTED, the file is right and the number is not                   : 13
          notation collision (an item number written as a line number)       :  1
          DEAD -- file does not exist where the sentence says to look        :  0

  The thirteen, old -> true:

        coverage.py:185               -> :215 + :222   the origin/main read + fallback
        ndi_ground_truth.py:449       -> :491          origin/main template read
        ndi_ground_truth.py:539       -> :614          the second origin/main read
        build_v_eta.py:5425           -> :5829         "CHANGE 5 (signed section, :642)"
        build_v_eta.py:5441           -> :5836         "#52's title [...] is stale"
        migrators_j/image.m:51-56     -> :156-165      format/compression deferral
        resolveValidIntervals.m:859   -> :1000         sprintf('time_reference_%d', r)
        resolveValidIntervals.m:222-227 -> :311-317    the #52 interaction, reported
        image_stack.m:48,78           -> :189-200      the guard's own explanation
        image_stack.m:78 (2nd cite)   -> :248          `if isempty(subjectId)`
        universalRenames.m:308        -> :628          skip = {'document_class', ...}
        Contents.m:348                -> :354          (see the note above)
        V_eta_OPEN_WORK.md:51         -> ROW #51, text at :375-383

  **THE NOTATION COLLISION IS WORTH ITS OWN SENTENCE.** `V_eta_OPEN_WORK.md` numbers its
  items `#nn` and this document cited one as `V_eta_OPEN_WORK.md:51`, which is
  indistinguishable from a line reference and lands on an unrelated paragraph about how
  `## COMPLETED` is formatted. Both notations are in use in this file. **Write
  `V_eta_OPEN_WORK.md` row #51, never `V_eta_OPEN_WORK.md:51`.**

  **WHAT DID NOT DRIFT IS THE MORE USEFUL HALF, because it says where citations survive.**
  All 34 NDI-matlab citations verified exact — the eleven `epochid.epochid` sites, the
  seven `ndi.document('imageStack')` sites and eight `add_file('imageStack')` sites, all
  three `markgarbage.m` lines, `syncgraph.m:404-408`, `system.m:229`, `tuning_response.m:92`
  and `:499`, `ensemble.m:274-276`. So did every `cache.m` line (1860/1869/1870/1871),
  `references.m:90`, `fileList.m:93,99`, `jMeasurementFold.m:69` and `:84`, and both plan-document
  references (`V_eta_time_reference_model_plan.md:642` and `:468`, which is still that
  document's ONLY `TEAM-SIGN-OFF` line — HISTORICAL-SIGNOFF-CLAIM). **Every one of the
  thirteen drifted citations points into a file THIS TEAM is actively editing; not one
  points into NDI**, which we only read. A citation's decay rate is the edit rate of the
  file it names, so a line number into `build_v_eta.py`, `coverage.py` or a `+migrators_j`
  file should be treated as a hint and re-grepped, while one into NDI can be trusted longer.

  **THREE OF THE THIRTEEN REPOINTED CITATIONS WERE STALE AGAIN WITHIN HOURS, AND THAT IS
  THE AUDIT'S OWN THESIS ARRIVING FASTER THAN IT PREDICTED.** Re-checked at the end of
  2026-08-12; the other ten are still exact.

        old -> repointed this morning -> TRUE at the end of the day
        coverage.py:185      -> :215,:222   -> :217 (docstring) + :226 (the ref loop)
        Contents.m:348       -> :354        -> :368
        OPEN_WORK.md:51      -> row #51 at  -> :634-641 (the row MOVED to `## COMPLETED`;
                                :375-383      :375 is now the head of a new index table
                                              and :385 is #51's entry in it)

  All three files were edited by THIS TEAM in the intervening hours, and every edit
  INSERTED above the cited line: the completion ladder went into `coverage.py`, the
  generated roster into `Contents.m`, a COMPLETED index table into `V_eta_OPEN_WORK.md`.
  **No correction was wrong when written and none survived the day.** The third is the
  worst-behaved of the three even though it was written as a WARNING about this exact
  notation — *"Write `V_eta_OPEN_WORK.md` row #51, never `V_eta_OPEN_WORK.md:51`"* — and
  the line range added to help a reader find the row drifted anyway. And the `Contents.m`
  case reproduces, exactly, the failure the audit
  singled out as the worst kind — the old number lands on a real sentence about something
  else:

        $ sed -n '346p;354p' DID-matlab/.../+migrators_j/Contents.m
        346:%                          `double`; validateTypeShape runs unconditionally on a
        354:%                          it is. All three writer sites DO set `value`, so this

  **The rule the audit derived — a citation's decay rate is the edit rate of the file it
  names — is right, and this is the strong form of it: for a file under active edit, hours
  is a realistic half-life, and repointing a number does not buy you a day.** For those
  files, cite by SEARCHABLE CONTENT (a grep pattern, a function name, a marker) and let
  the line number be a hint. Every one of the 34 NDI-matlab citations is still exact,
  across both audits.

  **TWO CITATIONS ARE CORRECT ONLY BECAUSE OF WHERE THEY SAY TO LOOK, and would read as
  dead otherwise.** `src/ndi/+ndi/+element/ensemble.m` does NOT exist in the NDI feature-branch
  working tree; it exists on `origin/main`, which is exactly what the sentence says
  (*"`origin/main src/ndi/+ndi/+element/ensemble.m:274-276`"*), and the quoted three lines
  are verbatim there. Likewise `imageDocMaker.m:121-127` and `jMeasurementFold.m:69` are
  cited by BASENAME and both files have moved directory
  (`+setup/+NDIMaker/imageDocMaker.m`, `+migrators_j/private/jMeasurementFold.m`). **A
  basename citation outlived a path change and a `origin/main` citation outlived a branch
  divergence — both survived because they were UNDER-specified in the right dimension.**
- **THE "X IS GATED / ENFORCED / CHECKED IN CI" CLAIMS, 2026-08-12 — ALL FOUND, ALL RUN.**
  This file has been wrong about exactly this before, in the reassuring direction (it said
  all four generated artifacts were CI-gated when three were not), so every such claim was
  followed to the gate rather than believed:

        DENOMINATOR: 11 "gated / enforced / checked in CI" claims located in this
                     document; 11 traced to a named gate; 11 gates exist and run;
                     0 found to be absent; 1 found to be ARMED where this file
                     says it is not (#37, corrected above)

        tests.yml calls tools/gates.py --ci and owns no gate list   tests.yml:167,200
        test_ci_owns_no_second_list_of_gates                        test_gates.py:120
        the sibling-clone properties (5 asserts, not 3)             test_ci_runs_the_whole_chain.py
        check_signoff_header_staleness: CI + pytest                 a gates step; test_veta.py, test_gates.py
        regen_binding_strengths after build, before pytest          the derived order, confirmed by --explain
        test_field_and_registry_strengths_agree                     test_veta.py:2029
        the migrator vocabulary sweep enforces in CI                a gates step
        referent_unique_by pinned by a test                         test_veta_time_reference_family_uniqueness.py
        silentLoss reads the key + reports a denominator            silentLoss.m:49-56,523-526
        timeReferenceFamilies reads it too                          timeReferenceFamilies.m:27,36,75
        test_census_digest on the fast gate                         test-migrators-quick.yml:189,196

  **Two of these are BETTER than claimed and the difference matters.**
  `test_ci_runs_the_whole_chain.py` asserts **five** properties, not the three this file
  enumerates — it also pins the missing-`origin/main` guard and the announced fallback.
  And the fast gate runs `test_census_digest_uniqueness.py` alongside `test_census_digest.py`.
  Understating a gate is the safe direction, and it is the direction found here.
- **WHAT THIS PASS COULD NOT VERIFY, NAMED SO THE GAP HAS A SHAPE.** Everything above was
  re-derived from files in this container. The following were NOT, and no sentence in this
  document should be read as re-confirmed on 2026-08-12:

        DENOMINATOR: 3 categories of unverifiable claim, and what would settle each

        every CORPUS figure          no MATLAB here and corpus artifacts cannot be
                                     downloaded. That covers 633,432 / 7,233 / 2,670 /
                                     4,563 / 562,448 / 305,480 / 20,850 / the six
                                     invented-empty-edge rows / 76,766 / ~7,007 /
                                     107,308 / 20,411 / 11,118 / the 11,448 orphans /
                                     115 strains, and every run id quoted.
                                     SETTLED BY: the digest's own printed rollup from a
                                     fresh run -- never a sum performed by a reader.
        `variable`'s admissible set  NDIC.txt lives in VH-Lab/ndi-ontology-matlab, which
                                     is not attached here (the T8 note already says so).
        the vhlab_voltage2firingrate the writer is in no repo we have. UNCHANGED.
                                     Still blocks binnedspikeratevm's Hz-vs-spikes-per-bin.

  **The armed batch-post-pass gate is still UNEXERCISED against a real report** — that
  caveat is already written above and this pass did not change it: every run behind it used
  SYNTHETIC reports, and this container still has no MATLAB.

  **AND ONE INSTRUMENT-LEVEL FINDING FROM THE PASS ITSELF.** Two numbers in this document
  are not re-derivable from their own descriptions: `element`'s *"223 hits across 95 of 915
  NDI files"* (no reading of "hits" reproduces it) and, in the same sentence, a denominator
  that has since moved to 1,002. Operating Rule 5 requires a denominator; **it does not
  require the NUMERATOR's method, and that is where both of these escaped.** A count is
  re-checkable only if the command that produced it is written down beside it — which is
  what Rule 2 asks for and what a figure quoted without its command quietly drops.

## Build / test
- **`python3 tools/gates.py` IS THE ENTRY POINT.** **NO STEP COUNT IS WRITTEN
  HERE ANY MORE — run `python3 tools/gates.py --explain | head -1`.** The steps
  run in an order derived from which tool reads which artifact, once for a whole
  batch of edits. `--explain` prints the order + the evidence for each edge; `--check`
  regenerates into a scratch mirror and diffs without touching the working tree;
  `--ci` is what `tests.yml` runs. It prints its step count first, a headline
  count per step, and FAILS a step that exits 0 while printing no headline.

  **THIS SAID "16 steps" AND "11.9 s, of which pytest 7.2 s"; BOTH ARE STALE,
  AND THE TIMING IS STALE BY MORE THAN 3x.** Re-measured 2026-08-11 on this
  container, quoting the tool's own denominator and its own per-step table:

        $ python3 tools/gates.py --explain | head -1
        DENOMINATOR: 18 steps declared, 19 dependency edge(s) to substantiate

        $ python3 tools/gates.py --check | tail
        SUMMARY: 18 step(s) declared, 18 ran, 18 passed, 0 failed, 0 skipped,
                 0 not runnable here
          ARTIFACTS DIFFERING FROM THE COMMITTED COPY: 0
          WALL CLOCK: 39.14s total
              pytest             31.16s
              ndi_ground_truth    3.83s
              status_board        1.18s
              ... the other 15 steps total 2.97s

  **pytest is now 80% of the chain, and that changes the advice rather than
  just the number.** The old line concluded "batching is worth it for
  CORRECTNESS, not for time" on the strength of an 11.9 s total. At 39 s the
  correctness argument is unchanged and the time argument now points the same
  way: N hand-typed regenerations cost N pytest runs. The two numbers below
  are the ones to re-measure before quoting — a step count is checked by CI
  (`test_gates.py::test_ci_owns_no_second_list_of_gates`), a wall clock is
  checked by nothing and drifts silently with the test suite.

  **AND BOTH DRIFTED AGAIN INSIDE ONE DAY. "18 steps / 19 edges" and "39.14s /
  pytest 31.16s" were written 2026-08-11 and were stale by 2026-08-12.**
  Re-measured on this container, quoting the tool's own denominator and its own
  per-step table, exactly as the block above instructs:

        $ python3 tools/gates.py --explain | head -1
        DENOMINATOR: 19 steps declared, 24 dependency edge(s) to substantiate

        $ python3 tools/gates.py --check | tail
        SUMMARY: 19 step(s) declared, 19 ran, 19 passed, 0 failed, 0 skipped,
                 0 not runnable here
          ARTIFACTS DIFFERING FROM THE COMMITTED COPY: 0
          WALL CLOCK: 41.56s total
              pytest             32.55s
              ndi_ground_truth    3.26s
              check_web_assets_fresh 2.18s
              status_board        1.07s
              ... the other 15 steps total 1.50s

  The nineteenth step is `check_web_assets_fresh` and it is third-slowest, so it
  moved BOTH numbers. **The sentence above — "a step count is checked by CI" —
  is TRUE and did not help.** `test_ci_owns_no_second_list_of_gates` checks that
  `tests.yml` does not keep a SECOND list; nothing checks that a number typed
  into prose matches the list. That is the same shape as every other error in
  this file: the artifact was right, the prose about the artifact was not.

  **AND IT DRIFTED AGAIN DURING THE HOUR THIS CORRECTION WAS BEING WRITTEN.** The
  block above was measured at 19 steps / 24 edges; before it was committed the
  chain was at **21 steps / 29 edges** (`gen_class_walkthrough` and `tenet_map`
  arrived), so a note written to fix a stale number was stale on arrival. **That
  is why the header no longer carries one.** Three revisions of the same sentence
  — 16, then 18, then 19 — were each true for about a day. A count that changes
  whenever anyone adds a gate does not belong in prose beside a tool that prints
  it. **Do not type a step count here again — run `--explain | head -1`.**
- The individual tools still work and are what the driver calls:
  `python3 tools/build_v_eta.py` rebuilds `schemas/V_eta/` (copytree V_zeta→V_eta
  then transforms). `python3 -m pytest tests/test_veta.py -q` checks the schema.
- Migrators live in DID-matlab `+did2/+convert/+migrators_j/`; corpus validation is
  DID-matlab `test-code.yml` (full, ~1–2h) and `test-migrators-quick.yml` (~2 min).
- **THREE GATES THAT MATTER TO THIS REPO DO NOT RUN IN `tools/gates.py`, AND NOTHING HERE
  SAID SO.** Added 2026-08-12. `gates.py` is the entry point for DID-schema, and it is
  still the whole of DID-schema — but two of the instruments that answer questions about
  V_eta live on the DID-matlab side and run in DID-matlab's workflows:

        DID-matlab  tools/check_migrator_roster.py     test-migrators-quick.yml:237
                    tools/test_check_migrator_roster.py                       :248
                    tools/test_corpus_proven.py                               :205
                    tools/corpus_proven.py             test-code.yml:307
                                                       test-corpus.yml:273
                    tools/census_digest.py             (already recorded above)

  `corpus_proven.py` is the only one that can move the coverage ladder's **rung 4**, and
  it reaches back across the repo boundary to call `DID-schema tools/coverage.py` rather
  than reimplementing the verdict. So `gates.py` green says nothing about rung 4, and
  never will: **the ladder's top rung is answered by a workflow in the other repository,
  and in this container it reads `not measured` on all 102 rows by construction.**


## CAN MATLAB READ A MIGRATED DATABASE? (2026-08-14) — the read path, recorded

**Everything above this section is about whether documents MIGRATE and VALIDATE.
None of it was ever about whether NDI can USE them, and until 2026-08-14 the
answer was NO — not for one document.** This is a record of what was built and
what is still open. It decides nothing and carries no signature.

**`ndi.session.dir` could not open a migrated session at all, and the cause was
not V_eta.** The two sqlite backends are DIFFERENT FORMATS:

        did2.database.sqlitedb   documents, superclasses, depends_on,
                                 queryable_array_elem, meta
                                 grep -c "branch"  ->  0
        did.implementations.sqlitedb (LEGACY)   branch-versioned:
          :144 SELECT DISTINCT branch_id FROM branches
          :172 insert_into_table('branches','branch_id,parent_id,timestamp',...)

`ndi.migrate.local` writes with the first (`local.m`, `db =
did2.database.sqlitedb(dstPath)`); `didsqlite.m:25` read with the second, so the
open failed before a document was touched: `'DID:SQLITEDB:OPEN' ... "branches"
table not found`. There is no branch table to add — the fix was a new backend.

**BUILT (NDI-matlab, branch `claude/v-eta-migration-plan-35jj1z`):**

| what | where |
|---|---|
| an ndi.database that speaks did2 | `+ndi/+database/+implementations/+database/did2sqlite.m` |
| makes the migrated file FINDABLE | `+ndi/+database/+fun/databasehierarchyinit.m`, entry 2, extension `V_eta.sqlite` |
| the vintage map + resolution | `+ndi/+vintage/` (map, entryFor, isaQuery, objectClass, edge, edge_n, edgeName, field) |
| element-specific reads | `+ndi/+vintage/` (elementLabel, elementSubjectDocs, elementFields) |
| syncrule parameter reassembly | `+ndi/+vintage/syncruleParameters.m` |
| hand-run walkthrough | `tools/veta_open_migrated_session.m` |

**THE DESIGN, IN ONE SENTENCE: NDI's object layer is defined over BOTH vintages
from one declaration, and is NOT ported off v1 — because NDI STILL WRITES v1.**
`ndi.session.dir` on a fresh directory creates a legacy database (only the first
hierarchy entry can create, and it is `didsqlite`), so a layer that spoke only
V_eta could not read a session NDI had just made.

**THE OBJECT-RECONSTRUCTION KEY LIVES IN THREE PLACES, and that is the single
most useful fact here.** v1 stores the MATLAB class to construct in a field
NAMED AFTER THE CLASS (`daqsystem.ndi_daqsystem_class`) — a CONSTRUCTED name, so
a literal grep finds only the writer and reports the field as unread. V_eta has
no such field:

        daqreader (v1 tombstone only)  still a field
        daqsystem / filenavigator / daqmetadatareader / daqreader /
          syncgraph / syncrule          a `software` ENTITY behind `software_id`
                                        (jSoftware is called with the class as NAME)
        element                         a `term_assertion` pointing IN via
                                        subject_id, variable `ndi element class`

**FIVE FRAMES OF ONE BUG WERE FOUND, four by CI and one by reading.** Every
failure was the same species: a CONSTRUCTOR indexing a document block by its v1
class name. `ndi.daq.system` -> `acquisition_reader`; `ndi.daq.reader.mfdaq.ndr`
-> `daqreader_ndr`; `ndi.element` -> `element`; plus the two earlier ones. **The
map covers CLASSES; it cannot tell you which CONSTRUCTORS hard-code a block
name.** Those are found by running, or by grepping
`document_properties\.<v1class>\.` across the read path.

**A NAME SURVIVING IN V_eta IS NOT EVIDENCE THE MIGRATOR EMITS IT.** `daqreader`
was left out of the map because `schemas/V_eta/stable/daqreader.json` exists and
keeps `ndi_daqreader_class` — both true, and both about the v1 TOMBSTONE. The
migrator emits `acquisition_reader` (`+migrators_j/daqreader.m:159`). Fifteen v1
class names still exist as tombstones; **ask what the migrator emits, never
whether the name is present.**

**WHAT IS TESTED, and its denominator.** e2e run 62, head `4714cb81e`:

        Totals:  27 Passed, 0 Failed, 0 Incomplete.   22.15 s

covering, through the ordinary object API on migrated PRED: the session opens
where the migrator left it; `daqsystem_load` returns 2 systems with their reader
/ navigator / metadata reader resolved through renamed edges and a `software_id`
hop; the syncgraph loads carrying its 1 RULE (its existence proves nothing — an
unfound syncgraph is rebuilt EMPTY with no error, so the rule count is the
assertion); `getelements` returns 2, rebuilt as
`ndi.probe.timeseries.mfdaq`/`.stimulator`. Every one of those returned `{}`
before, none of them errored.

**WHAT IS NOT TESTED, NOT DONE, OR DELIBERATELY LEFT:**

  * **`readtimeseries` is untested and cannot be tested from the corpus zips.**
    Measured 2026-08-14, all four: `find <corpus> -type f | grep -vc '\.json$'`
    = **0 non-JSON files** in PRED (14 docs), 20211116 (1,220), Dab (27,561) and
    Soph (101,427). They are DOCUMENT corpora. Dab's ingested documents DECLARE
    their binaries (`ai_group*_seg.nbf_#`) and the zip does not carry them.
  * **`getsubjects()` returns the apparatus.** On migrated PRED: 3 subjects —
    the animal plus both probes — because V_eta makes every identifiable thing a
    subject. Filtering is now one line using the same label; it changes an
    existing call's return for every user, so it is a TEAM decision, untouched.
  * **`daq/reader.m:82` reads `document_properties.epochid.epochid`** and is a
    live sixth frame for any INGESTED corpus. PRED is not ingested; Dab is.
  * **`element.m:463` reads the same path** in the added-epoch branch. PRED has
    no `epochid` documents; 20211116 and Soph have `element_epoch` (252 / 4,232).
  * The element lookup rests on a FREE-TEXT label with an empty ontology node,
    written `if ~isempty(ndiClass)` — so an element with no class name is
    invisible to it. NDI's own writer always sets the class (`element.m:543`),
    so anything NDI wrote is found. `TestElementLabelMatchesMigrator` pins the
    phrase across the repo boundary and asserts it is written at exactly ONE
    site; the bound-vocabulary version rides with T8, which is blocked on NDIC.
  * `element` name+reference are stored CONCATENATED in
    `subject.local_identifier` as `'%s (ref %s)'` with no escaping, so a name
    ending in " (ref X)" is ambiguous on the way back. A property of the format,
    not of the reader.

**THE FOUR CORPORA, MEASURED 2026-08-14 (all read directly from the zips), so
the next target can be chosen on evidence:**

        DENOMINATOR: 4 corpora censused; PRED covers 10 class(es)
        corpus         docs classes  NEW vs PRED   new docs
        20211116       1220      21           13         1185
        Dab           27561      26           17        26288
        Soph         101427      32           24        99395

  * **20211116** is the smallest step: the stimulus-response tier
    (`stimulus_response_scalar` 273 + `_parameters_basic` 273), the calculator
    tier (`hartley_calc` 210, `tuningcurve_calc` 84, `oridirtuning_calc` 42) and
    `element_epoch` (252). It shares 8 of PRED's 10 classes.
  * **Dab** is the widest: ingestion (9,419 docs), openMINDS (2,344),
    `ontologyTableRow` (6,205), `syncrule_mapping` (2,484 — the class with the
    live NDI query).
  * **Soph** is ~70% one path: the vision calculators (~70,600 of 101,427). It
    also holds 1,647 `element` documents, 800x PRED, which is the first real
    workout for the element assembler.
  * Only PRED holds `pyraview` and `daqreader_ndr`.
