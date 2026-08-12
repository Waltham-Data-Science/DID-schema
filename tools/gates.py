#!/usr/bin/env python3
"""ONE entry point for the regenerate-and-gate chain.

    python3 tools/gates.py            regenerate the artifacts, then gate
    python3 tools/gates.py --check    same chain in a scratch mirror; the
                                      working tree is NOT touched
    python3 tools/gates.py --explain  print the derived order and the
                                      evidence for every edge, run nothing

WHY THIS EXISTS. `tools/build_v_eta.py` is the file every schema change goes
through, and the cost of an edit is not the file: it is that FOUR generated
artifacts must be regenerated and a chain of checkers re-run afterwards, IN
DEPENDENCY ORDER, and until now every agent retyped that sequence by hand. The
commit log carries the same seven-to-nine commands over and over, sometimes
reordered, sometimes a step short:

    $ git log --format=%B -20 | grep -n "^GATES\\|^Gates:"
    168:GATES: ndi_ground_truth.py OK | build_v_eta.py 245 schemas | pytest ...
    410:Gates: build_v_eta.py 245 schemas; pytest 1211 passed (1210 + 1 added ...
    516:Gates: build_v_eta 245 schemas; pytest 1210 passed (1201 before ...
    857:GATES

A reordering is not cosmetic here. `coverage.py` reads the BUILT
`V_eta/index.json`; `status_board.py` reads the ledger `coverage.py` writes;
`build_v_eta.py` reads the ground truth `ndi_ground_truth.py` writes. Run them
out of order and every artifact is refreshed, every mtime is new, and the
contents describe a tree that no longer exists. That is the failure this
project punishes hardest, and it leaves no trace.

THE ORDER IS DERIVED, NOT DECLARED. `ORDER` below is a topological sort of
`EDGES`, and every edge names the artifact it is about plus a WITNESS -- a
literal the consumer's own source must contain if it really reads that
artifact. `--explain` re-checks all of them and fails on any edge it cannot
substantiate, so an invented dependency cannot survive here as a comment.

RULE 5, THROUGHOUT. The step count prints FIRST and UNCONDITIONALLY, before
anything runs; every step prints its own headline count; a step whose headline
pattern does not match its output is a FAILURE, not a pass -- because a step
that runs and prints nothing is indistinguishable from a step that was skipped,
which is `silentLoss` and the census digest one layer up.

EXIT CODE. Non-zero if ANY step failed, produced no headline, or was skipped
because a producer it depends on failed. Independent steps keep running after a
failure -- a developer wants every failure, not the first -- but a run with a
failure in it NEVER exits 0.
"""

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable or "python3"


# --------------------------------------------------------------------------
# THE STEPS
# --------------------------------------------------------------------------
# `writes`   -- repo-relative paths the step generates. Used by --check to
#               decide what to diff, and by nothing else.
# `headline` -- a regex with ONE group, matched against the step's combined
#               output. No match => the step FAILS. Deliberately strict: this
#               is the only thing standing between "ran and reported" and
#               "did nothing quietly".
# `always`   -- gate steps that read no generated artifact still run when a
#               producer fails.

def find_repo(name, env):
    """Locate a sibling checkout the way coverage.py and status_board.py do.

    The tools do not agree on this -- coverage.py/status_board.py search
    $NDI_MATLAB|$DID_MATLAB then /home/user then ../, ndi_ground_truth.py and
    check_empty_ontology_nodes.py read $NDI_MATLAB_PATH|$DID_MATLAB_PATH with
    an absolute default, check_tombstones.py reads $DID_MATLAB then ../ -- so
    this takes the UNION. Over-detecting is the safe direction: it makes the
    driver TRY the step and report a real failure, instead of skipping it and
    reporting a smaller chain as complete.

    An explicitly SET environment variable is AUTHORITATIVE, present or not.
    `NDI_MATLAB=/nowhere` therefore means "there is no NDI-matlab here" rather
    than silently falling through to /home/user -- which is what lets a
    sibling-less CI be reproduced on a machine that has the siblings."""
    for var in (env, env + "_PATH"):
        if os.environ.get(var) is not None:
            p = os.environ[var]
            return p if p and os.path.isdir(p) else None
    for cand in (os.path.join("/home/user", name),
                 os.path.join(os.path.dirname(REPO), name)):
        if os.path.isdir(cand):
            return cand
    return None


SIBLINGS = {"NDI-matlab": find_repo("NDI-matlab", "NDI_MATLAB"),
            "DID-matlab": find_repo("DID-matlab", "DID_MATLAB")}

# A path that cannot exist, used to say "absent" to a child in the one language
# every one of these tools understands.
_NO_SIBLING = os.path.join(REPO, ".gates-no-such-sibling")


def child_env():
    """One sibling answer for the whole chain.

    The tools do not resolve siblings the same way, and the difference is not
    academic: check_tombstones.py looks ONLY at $DID_MATLAB then ../DID-matlab,
    while coverage.py and status_board.py also try /home/user. Run the chain
    from a checkout that is not beside DID-matlab and check_tombstones reports
    BLOCKING 6 -- every tombstone graded as a passthrough because it found no
    migrators -- while the driver's own header says the sibling was found. A
    gate that fails on where the repository happens to sit is worse than no
    gate: it is a red build with a true-looking cause.

    So the driver resolves ONCE and tells every child, in all four spellings,
    including when the answer is "absent" -- otherwise a child falls back to a
    default the driver already rejected and the two disagree again."""
    env = dict(os.environ)
    for name, var in (("NDI-matlab", "NDI_MATLAB"), ("DID-matlab", "DID_MATLAB")):
        p = SIBLINGS.get(name) or _NO_SIBLING
        env[var] = p
        env[var + "_PATH"] = p
    return env


class Step:
    def __init__(self, name, argv, kind, headline, headline_label,
                 writes=(), check_argv=None, external=False, requires=(),
                 needs_paths=()):
        self.name = name
        self.argv = list(argv)
        self.kind = kind                      # "generate" | "gate"
        self.headline = re.compile(headline, re.MULTILINE)
        self.headline_label = headline_label
        self.writes = list(writes)
        # Sibling checkouts this step READS. Named, not guessed: `--explain`
        # requires the step's own source to mention each one.
        self.requires = list(requires)
        # Repo-relative paths that must EXIST for the step to have anything to
        # measure. Same footing as `requires`: a step whose subject is absent
        # is reported as NOT RUNNABLE HERE under --ci -- named and counted --
        # and is never rendered as a pass. The one case is the web viewer's
        # served tree, which is gitignored and produced by `npm run build`, so
        # a CI checkout legitimately has none.
        self.needs_paths = list(needs_paths)
        # A tool that has its OWN --check: composed rather than reimplemented.
        self.check_argv = list(check_argv) if check_argv else None
        self.external = external              # not a tools/*.py script

    @property
    def blocks_dependents(self):
        """DERIVED, not declared: only a step that WRITES an artifact can leave
        a stale one behind, so only a step that writes may force its dependents
        to be skipped. A failing report-only gate (pytest, the targets --check)
        is a failure of the run, never a reason to stop measuring."""
        return bool(self.writes)

    @property
    def missing_siblings(self):
        return [n for n in self.requires if not SIBLINGS.get(n)]

    @property
    def missing_paths(self):
        return [p for p in self.needs_paths
                if not os.path.exists(os.path.join(REPO, p))]

    @property
    def unavailable(self):
        """Everything that makes this step un-measurable HERE, in one list, so
        the header, the run loop and the summary cannot disagree about it."""
        return ([f"sibling {n}" for n in self.missing_siblings]
                + [f"path {p}" for p in self.missing_paths])

    def source_path(self):
        """The file whose content backs this step's declarations, if any."""
        for a in self.argv:
            if a.endswith(".py"):
                return a
        return None

    def __repr__(self):
        return f"Step({self.name})"


def _t(script, *args):
    return [PY, os.path.join("tools", script)] + list(args)


STEPS = [
    # THE `--all` DEFECT DESCRIBED HERE IS FIXED (2026-08-11). The note is kept
    # because the numbers it warned about were real and the RESOLUTION is not the
    # one it expected -- read it before quoting either set of counts.
    #
    # It said: `V_eta_ndi_ground_truth.json` is not reproducible from NDI
    # `origin/main` even though it records `ndi_ref: "origin/main"`, because
    # `classify_divergence` walked `git log --all`, so the
    # `v_alpha_divergence[].provenance` verdicts were a property of whichever
    # refs the local NDI clone happened to carry. That was correct, and it is
    # now demonstrated rather than argued: the OLD code run against a 39-ref
    # clone and against a 1-ref clone of the same origin/main tip produced
    # DIFFERENT artifacts (DID-INVENTED 36|UNKNOWN 31 vs 35|32); the new code
    # produces byte-identical output on both.
    #
    # It also said regenerating would REPLACE 11 DID-INVENTED verdicts with
    # UNKNOWN -- "a loss of record dressed as a refresh" -- and concluded the
    # refresh must not be committed. THE FIRST HALF IS RIGHT AND THE CONCLUSION
    # IS NOT. Those verdicts were read off refs the contract excludes:
    # `treatment_drug` from `origin/feature/newvhlabimport`, and `app` /
    # `element` / `projectvar` from `origin/audri_documents` (files under
    # `ndi_common/unified_documents/`, which is not the template directory at
    # all); 12 rows carried "first NDI version 2026-04-24", a date on which NO
    # commit reachable from ANY ref in this clone adds a template. A verdict
    # derived from a ref the contract excludes is not evidence, so withdrawing
    # it is a CORRECTION, not a regression.
    #
    # Pinning the ref alone would have been a second wrong answer: git's default
    # rename detection reports NDI's template renames as R, which
    # `--diff-filter=A` skips, and 14 of the 67 classes then read "no add-commit
    # found". With `--no-renames` every one of the 67 resolves to a real first
    # version on origin/main.
    #
    #     committed (--all, a clone we no longer have)  47 | 0 | 20
    #     origin/main, renames left on                  35 | 0 | 32
    #     origin/main, renames off  (LANDED)            39 | 1 | 27
    #
    # The 1 is `projectvar`, the first NDI-CHANGED verdict the record has ever
    # carried: its 2023-04-13 first version matches our V_alpha snapshot field
    # for field, so NDI really did change that template and old-shaped documents
    # may exist. The `--all` walk had hidden it behind an off-main file.
    #
    # Pinned by tests/test_ground_truth_provenance_ref.py.
    Step("ndi_ground_truth", _t("ndi_ground_truth.py"), "generate",
         r"^NDI classes captured:\s+(\d+)", "NDI classes captured",
         writes=["schemas/V_eta_ndi_ground_truth.json"],
         requires=["NDI-matlab", "DID-matlab"]),

    Step("build_v_eta", _t("build_v_eta.py"), "generate",
         r"^V_eta built: (\d+) schemas", "schemas built",
         writes=["schemas/V_eta"]),

    # #32. The registry's `strength` column is DERIVED from the field
    # constraints, which are authoritative -- so it must run AFTER the build
    # that writes both sides, and BEFORE anything that reads the registry.
    # `build_v_eta.py` deliberately emits the rows with NO strength; if this
    # step is dropped the column simply vanishes rather than going quietly
    # wrong, and the artifact diff below says so by name.
    Step("regen_binding_strengths", _t("regen_binding_strengths.py"), "generate",
         r"^DENOMINATOR: (\d+) bound field declaration\(s\) read",
         "bound field declarations",
         writes=["schemas/V_eta/stable/binding_registry_meta.json"],
         check_argv=_t("regen_binding_strengths.py", "--check")),

    # CHECK-ONLY, ALWAYS. `V_eta_migration_targets.json` is half CURATED and
    # half derived (the tool's own words), and a curated file is not this
    # driver's to rewrite -- but coverage.py reads it, so a drift must be
    # reported rather than silently carried. Never invoked without --check.
    Step("refresh_migration_targets",
         _t("refresh_migration_targets.py", "--check"), "gate",
         r"^DENOMINATOR: (\d+) class rows in V_eta_migration_targets\.json",
         "curated target rows", requires=["DID-matlab"]),

    Step("coverage", _t("coverage.py"), "generate",
         r"\((\d+) v1 classes", "v1 source classes in the ledger",
         writes=["schemas/V_eta_coverage_ledger.md",
                 "schemas/V_eta_coverage_ledger.json"],
         requires=["NDI-matlab", "DID-matlab"]),

    Step("regen_final_class_set", _t("regen_final_class_set.py"), "generate",
         r": (\d+) persist \(", "classes in the persist set",
         writes=["schemas/V_eta_final_class_set.md"]),

    Step("status_board", _t("status_board.py"), "generate",
         r"^\s*open classes: (\d+)", "open classes on the board",
         writes=["schemas/V_eta_STATUS.md", "schemas/V_eta_decisions.json"],
         check_argv=_t("status_board.py", "--check")),

    # ---- gates ----------------------------------------------------------
    Step("pytest", [PY, "-m", "pytest", "-q"], "gate",
         r"^(\d+) passed", "tests passed", external=True),

    # `tools` JOINED `tests` ON 2026-08-11. The step had read `tests` alone
    # since it was written, so the eighteen scripts that generate every artifact
    # under `schemas/` were linted by nothing -- 559 findings on first
    # measurement, including an undefined name that would have raised in
    # `status_board.py --check`. The residue is carved out by name in
    # pyproject.toml, with what each carve-out still owes.
    Step("ruff", ["ruff", "check", "tests", "tools"], "gate",
         r"(All checks passed!|Found \d+ errors?)", "ruff verdict",
         external=True),

    Step("check_migrator_vocabulary",
         _t("check_migrator_vocabulary.py", "--enforce"), "gate",
         r"still CONSUME invented names\s+: (\d+)", "migrators on invented names"),

    Step("check_tombstones", _t("check_tombstones.py", "--enforce"), "gate",
         r"^\s*BLOCKING\s+: (\d+)", "blocking tombstones",
         requires=["DID-matlab"]),

    Step("check_duplicate_field_declarations",
         _t("check_duplicate_field_declarations.py", "--enforce"), "gate",
         r"^DENOMINATOR: (\d+) V_eta classes read", "classes read"),

    Step("check_constraint_refinement",
         _t("check_constraint_refinement.py"), "gate",
         r"^\s*classes walked\s+(\d+)", "classes walked"),

    # --enforce, ADDED with #32. The tool's own usage line has offered it since
    # it was written; the driver ran it report-only, so B5 -- "a field and its
    # registry row disagree", baseline 0 -- printed the disagreement and exited
    # 0. A finding whose baseline is zero and whose exit code is zero is a
    # report, not a gate. Every other ratchet in this chain
    # (check_duplicate_field_declarations, check_vacuous_tests,
    # check_migrator_vocabulary, check_tombstones) is already run with it.
    Step("check_binding_governance",
         _t("check_binding_governance.py", "--enforce"), "gate",
         r"V_eta document_class files walked\s+: (\d+)", "class files walked"),

    Step("check_empty_ontology_nodes", _t("check_empty_ontology_nodes.py"), "gate",
         r"V_eta schema files inspected\s+: (\d+)", "schema files inspected",
         requires=["DID-matlab"]),

    Step("check_vacuous_tests", _t("check_vacuous_tests.py", "--enforce"), "gate",
         r"VACUOUS-TEST SWEEP: (\d+) test file\(s\) parsed", "test files parsed"),

    Step("check_signoff_header_staleness",
         _t("check_signoff_header_staleness.py", "--enforce"), "gate",
         r"^DENOMINATOR: (\d+) markdown file\(s\)", "plan documents read"),

    # READS BOTH SIBLINGS, so it is NOT RUNNABLE on a bare runner -- and that
    # is reported rather than counted as agreement. It compares the batch
    # post-pass chain the six-corpus gate composes against the one NDI
    # production composes. The lists are allowed to differ; an UNDECLARED
    # difference is a pass that either ships unmeasured or is measured but not
    # shipped. NDI's own source records both the divergence and what it cost:
    # "two pipelines emitting different classes for one concept, and nothing
    # comparing them", and "Ten divergent rows is enough noise to hide an
    # eleventh, which is precisely how resolveDatasetEntities came to sit
    # unwired." No artifact is written, so this declares no EDGES.
    Step("check_pipeline_parity",
         _t("check_pipeline_parity.py", "--enforce"), "gate",
         r"DENOMINATOR: (\d+) pass\(es\) named by the harness",
         "harness batch passes",
         requires=["DID-matlab", "NDI-matlab"]),

    # THE VIEWER SERVES COPIES, AND THE COPIES WERE GATED BY NOTHING. Four of
    # the artifacts this chain regenerates are read by the web viewer, which
    # cannot fetch them from `schemas/` -- `web/scripts/sync-schemas.mjs` copies
    # them into `web/public/`, and that copy is what a reader reads. Measured
    # 2026-08-12: the served ledger and the generated one disagreed on 5 of 102
    # rows, and `binaryseries_parameters` rendered as `disputed` in the panel
    # while the generated ledger had it resolved with a sign-off citation.
    #
    # NOT RUNNABLE ON A BARE RUNNER, and that is a property of the subject, not
    # of the gate: the 904 copied paths are gitignored and are produced by
    # `npm run build`'s prebuild hook, so a CI checkout has none of them. The
    # step therefore declares the path it needs and is reported NOT RUNNABLE
    # HERE when it is absent, on the same footing as a missing sibling
    # checkout: named, counted, never a pass.
    #
    # THE MARKER IS `web/public/schemas`, NOT `web/public`, and the difference
    # is not pedantry -- it was measured. `web/public/class_walkthrough.json`
    # is TRACKED (one file, committed 2026-08-12), so `web/public` DOES exist
    # in a bare checkout while none of the copied tree does. Keying on the
    # parent would have let this gate run on a runner and report 904 UNSERVED
    # paths: a red build whose cause is that the sync has not run, which on a
    # runner is correct. `web/public/schemas` is the sync script's own
    # `publicSchemas` root and exists only where the sync has run.
    #
    # THE TWO VIEWER GENERATORS. They are `generate` steps, not gates, and they
    # belong in this chain for the ordinary reason every other generator does:
    # they READ generated artifacts (the coverage ledger, the ground truth, the
    # built index, the tenets document) and WRITE a file that is COMMITTED. An
    # unchained generator whose output is committed is precisely the hole this
    # driver was built to close -- `--check` regenerates into a scratch mirror
    # and diffs, so a stale committed asset now fails there rather than being
    # noticed by a human.
    #
    # IT WAS ALREADY STALE WHEN THIS WAS WIRED, which is why it is wired.
    # `tools/coverage.py` gained a derived per-class `stage` column; all 102
    # ledger rows carry one. `class_walkthrough.json` was generated before that
    # landed and carries none, so the viewer's class page renders every class
    # with its ladder position missing. Nothing reported it: the freshness gate
    # compares a served copy against its SOURCE, and these two assets are
    # written into `web/public/` directly rather than copied into it, so they
    # were the two files that gate could only delegate on -- and it can only
    # delegate to a `--check` that something actually runs.
    #
    # UNLIKE `check_web_assets_fresh`, these declare NO `needs_paths`. That gate
    # needs the gitignored synced tree and is correctly NOT RUNNABLE HERE on a
    # runner; these two need only the repository and the siblings, so they run
    # in CI like every other generator.
    Step("gen_class_walkthrough", _t("gen_class_walkthrough.py"), "generate",
         r"^DENOMINATOR: (\d+) ledger row\(s\) read", "ledger rows read",
         writes=["web/public/class_walkthrough.json"],
         check_argv=_t("gen_class_walkthrough.py", "--check"),
         # DID-matlab ONLY, and the driver caught me declaring otherwise. I
         # wrote `requires=["NDI-matlab", "DID-matlab"]` by analogy with
         # `coverage` and `ndi_ground_truth`, which do read the NDI checkout.
         # This one does not: it takes NDI's declarations from
         # `V_eta_ndi_ground_truth.json`, an artifact of THIS repository, and
         # opens the NDI tree never. It scans the DID-matlab convert package
         # directly, so that requirement is real. A `requires` naming a
         # checkout the step never reads is not harmless -- it would report the
         # step NOT RUNNABLE HERE on a machine that legitimately has
         # everything it needs.
         requires=["DID-matlab"]),

    Step("tenet_map", _t("tenet_map.py"), "generate",
         r"^DENOMINATOR: (\d+) tenet\(s\) declared", "tenets declared",
         writes=["web/public/tenets.json"],
         check_argv=_t("tenet_map.py", "--check")),

    # It reads no artifact into a file of its own, so it declares no `writes`.
    Step("check_web_assets_fresh", _t("check_web_assets_fresh.py"), "gate",
         r"^DENOMINATOR: (\d+) served file\(s\) inspected", "served files inspected",
         needs_paths=[os.path.join("web", "public", "schemas")]),
]

BY_NAME = {s.name: s for s in STEPS}


# --------------------------------------------------------------------------
# THE EDGES -- one row per "X must run before Y", each with the artifact it is
# about, WHY, and a witness that makes the reason checkable instead of asserted.
# --------------------------------------------------------------------------

class Edge:
    def __init__(self, producer, consumer, artifact, reason,
                 witness_file, witness):
        self.producer = producer
        self.consumer = consumer
        self.artifact = artifact
        self.reason = reason
        self.witness_file = witness_file
        self.witness = witness

    def substantiated(self, root=REPO):
        """Does the CONSUMER's own source contain the literal that proves it
        reads the PRODUCER's artifact? An edge that cannot answer yes is an
        edge somebody made up."""
        p = os.path.join(root, self.witness_file)
        if not os.path.exists(p):
            return False, "witness file missing: " + self.witness_file
        with open(p, errors="replace") as fh:
            src = fh.read()
        if re.search(self.witness, src):
            return True, self.witness
        return False, f"no match for {self.witness!r} in {self.witness_file}"


EDGES = [
    Edge("ndi_ground_truth", "build_v_eta",
         "schemas/V_eta_ndi_ground_truth.json",
         "build_v_eta.py loads the ground truth and stamps NDI's required-ness "
         "onto the built schemas as `ndi_mustBeNonEmpty`. Build first and the "
         "stamp describes the PREVIOUS NDI read.",
         "tools/build_v_eta.py", r"V_eta_ndi_ground_truth\.json"),

    Edge("ndi_ground_truth", "check_migrator_vocabulary",
         "schemas/V_eta_ndi_ground_truth.json",
         "the vocabulary sweep IS a query over `migrator_reads` in the ground "
         "truth; it exits early if the file is absent.",
         "tools/check_migrator_vocabulary.py", r"V_eta_ndi_ground_truth\.json"),

    Edge("ndi_ground_truth", "check_tombstones",
         "schemas/V_eta_ndi_ground_truth.json",
         "every tombstone row is a comparison against the NDI template captured "
         "in the ground truth.",
         "tools/check_tombstones.py", r"V_eta_ndi_ground_truth\.json"),

    Edge("build_v_eta", "check_tombstones", "schemas/V_eta",
         "the other side of each comparison is the BUILT tombstone, read from "
         "V_eta/index.json.",
         "tools/check_tombstones.py", r'"V_eta"'),

    Edge("build_v_eta", "refresh_migration_targets", "schemas/V_eta",
         "its INSTRUMENT CHECK asks whether every derived target name exists in "
         "the built V_eta set (via coverage.veta_index).",
         "tools/refresh_migration_targets.py", r"veta_index"),

    Edge("refresh_migration_targets", "coverage",
         "schemas/V_eta_migration_targets.json",
         "the ledger's `how`/target column comes from the curated targets file.",
         "tools/coverage.py", r"V_eta_migration_targets\.json"),

    Edge("build_v_eta", "coverage", "schemas/V_eta",
         "coverage.py reads schemas/V_eta/index.json to decide which v1 class "
         "has a V_eta home. Run it before the build and the ledger grades the "
         "previous schema set.",
         "tools/coverage.py", r'"V_eta", "index\.json"'),

    Edge("build_v_eta", "regen_final_class_set", "schemas/V_eta",
         "the persist set IS the `disposition` markers in the built "
         "V_eta/index.json -- there is no other source for it.",
         "tools/regen_final_class_set.py", r'"V_eta", "index\.json"'),

    Edge("build_v_eta", "status_board", "schemas/V_eta",
         "the board's class state is read from the built V_eta/index.json.",
         "tools/status_board.py", r'"V_eta", "index\.json"'),

    Edge("coverage", "status_board", "schemas/V_eta_coverage_ledger.json",
         "the board joins its class rows against the ledger JSON coverage.py "
         "writes. Board-before-ledger renders yesterday's coverage under "
         "today's schema set.",
         "tools/status_board.py", r"V_eta_coverage_ledger\.json"),

    Edge("status_board", "check_signoff_header_staleness",
         "schemas/V_eta_decisions.json",
         "the staleness gate compares each plan document's header against the "
         "signature state in V_eta_decisions.json, which status_board.py writes.",
         "tools/check_signoff_header_staleness.py", r"V_eta_decisions\.json"),

    Edge("build_v_eta", "check_duplicate_field_declarations", "schemas/V_eta",
         "it walks every class chain in the built schema root.",
         "tools/check_duplicate_field_declarations.py", r'"V_eta"'),

    Edge("ndi_ground_truth", "check_duplicate_field_declarations",
         "schemas/V_eta_ndi_ground_truth.json",
         "the V1-FIDELITY split is DERIVED from the ground truth (2026-08-12), "
         "not from a hand list beside it -- a row is NDI's own only if did_v1 "
         "declares the name in two of the declaring blocks. Read a stale "
         "artifact and a duplicate NDI forces reads as one V_eta invented, "
         "which is an invitation to delete a field every real document carries.",
         "tools/check_duplicate_field_declarations.py",
         r"V_eta_ndi_ground_truth\.json"),

    Edge("build_v_eta", "check_constraint_refinement", "schemas/V_eta",
         "same sweep, one level deeper -- it opens the built declarations.",
         "tools/check_constraint_refinement.py", r'"V_eta"'),

    # ADDED 2026-08-12. This reader had NO ground-truth edge while its four
    # siblings did -- build_v_eta, check_migrator_vocabulary, check_tombstones
    # and check_duplicate_field_declarations all declare one. It has read the
    # artifact since the #69 adjudication (`GROUND_TRUTH` at
    # check_constraint_refinement.py:174, used for the v1-provenance column that
    # decides whether a redeclaration is did_v1's own shadow or V_eta's).
    #
    # HARMLESS TODAY, AND ONLY BY LUCK: `ndi_ground_truth` already sorts early
    # enough that the artifact happens to be fresh when this step runs. That is
    # a property of the current topological order, not of anything declared --
    # so a future reordering could feed this gate a stale ground truth and its
    # provenance column would silently describe an older NDI. An undeclared
    # dependency that works by accident is the shape this whole file exists to
    # remove; `--explain` now has to substantiate it like every other edge.
    Edge("ndi_ground_truth", "check_constraint_refinement",
         "schemas/V_eta_ndi_ground_truth.json",
         "the v1-PROVENANCE column is read from the ground truth: a "
         "redeclaration is did_v1's own shadow only if NDI declares the name "
         "in two of the declaring blocks, and V_eta's otherwise. Read a stale "
         "artifact and a row NDI forces reads as one this side minted -- the "
         "same misreading that let a hand-maintained fidelity list invite the "
         "deletion of a field every passed-through document carries.",
         "tools/check_constraint_refinement.py",
         r"V_eta_ndi_ground_truth\.json"),

    Edge("build_v_eta", "check_binding_governance", "schemas/V_eta",
         "the binding registry it audits is written by the build.",
         "tools/check_binding_governance.py", r'"V_eta"'),

    # ---- #32: the derived strength column --------------------------------
    Edge("build_v_eta", "regen_binding_strengths", "schemas/V_eta",
         "both sides of the derivation are written by the build: the field "
         "constraints it reads (constraints.binding.strength) and the registry "
         "rows it fills. Regenerate before the build and the column describes "
         "the PREVIOUS schema set.",
         "tools/regen_binding_strengths.py", r'"V_eta"'),

    Edge("regen_binding_strengths", "check_binding_governance",
         "schemas/V_eta/stable/binding_registry_meta.json",
         "B5 compares each registry row's strength against the field's. Audit "
         "the registry before the column is derived and B5 grades a column "
         "build_v_eta.py deliberately leaves empty.",
         "tools/check_binding_governance.py", r"binding_registry_meta\.json"),

    Edge("regen_binding_strengths", "pytest",
         "schemas/V_eta/stable/binding_registry_meta.json",
         "test_veta.py::test_field_and_registry_strengths_agree opens the "
         "registry by path and compares it to the field declarations; run "
         "before the derivation and it tests the previous column.",
         "tests/test_veta.py", r"binding_registry_meta\.json"),

    Edge("build_v_eta", "check_empty_ontology_nodes", "schemas/V_eta",
         "the schema half of the sweep walks the built ontology_term fields.",
         "tools/check_empty_ontology_nodes.py", r'"V_eta"'),

    Edge("build_v_eta", "pytest", "schemas/V_eta",
         "most of tests/test_veta.py asserts against the BUILT tree; running "
         "pytest before the build tests the previous schema set and passes.",
         "tests/test_veta.py", r'"V_eta"'),

    # ---- the served copies -----------------------------------------------
    # All three producers write something the viewer serves a COPY of, so the
    # freshness comparison has to happen after they have run: grade the copies
    # first and they are compared against the artifacts as they were BEFORE
    # this chain regenerated them, which is a pass that means nothing.
    Edge("build_v_eta", "check_web_assets_fresh", "schemas/V_eta",
         "the whole V_eta set is copied into web/public/schemas/V_eta; the "
         "checker names V_eta as the set the viewer defaults to and fails when "
         "the contract stops serving it.",
         "tools/check_web_assets_fresh.py", r'GATED_SET = "V_eta"'),

    Edge("coverage", "check_web_assets_fresh",
         "schemas/V_eta_coverage_ledger.json",
         "web/public/coverage.json IS this ledger -- the copy that drifted, and "
         "the reason this gate exists. The checker requires the sync contract "
         "to serve it whenever it is present.",
         "tools/check_web_assets_fresh.py", r"V_eta_coverage_ledger\.json"),

    Edge("coverage", "gen_class_walkthrough",
         "schemas/V_eta_coverage_ledger.json",
         "the walkthrough is BUILT FROM the ledger -- one page per ledger row, "
         "carrying that row's disposition, targets, build_state and its derived "
         "`stage`. Generated before the ledger, it renders the previous "
         "ledger's classes; that is not hypothetical, it is how the asset came "
         "to be missing `stage` on all 102 rows.",
         "tools/gen_class_walkthrough.py", r"V_eta_coverage_ledger\.json"),

    Edge("ndi_ground_truth", "gen_class_walkthrough",
         "schemas/V_eta_ndi_ground_truth.json",
         "the page's `what NDI actually declares` panel is read from the ground "
         "truth, not from a V_eta schema. That direction is the whole repair "
         "track: a walkthrough built from our own schema would show the reader "
         "the shape we assumed rather than the shape NDI writes.",
         "tools/gen_class_walkthrough.py", r"V_eta_ndi_ground_truth\.json"),

    Edge("build_v_eta", "tenet_map", "schemas/V_eta",
         "every class a tenet row names is checked against the BUILT index "
         "before the row is allowed to render, which is what stops the table "
         "showing leadership a rename of a class that no longer exists -- it "
         "already rejected one (`dataseries_channel_map`, deleted 2026-08-09).",
         "tools/tenet_map.py", r"index\.json"),

    Edge("gen_class_walkthrough", "check_web_assets_fresh",
         "web/public/class_walkthrough.json",
         "the freshness gate cannot compare this asset against a source file -- "
         "it is written into web/public/ rather than copied there -- so it "
         "delegates to the generator's own --check. That delegation is only "
         "worth anything if something runs the generator first.",
         "tools/check_web_assets_fresh.py", r"class_walkthrough\.json"),

    Edge("tenet_map", "check_web_assets_fresh",
         "web/public/tenets.json",
         # THE WITNESS IS THE MECHANISM, NOT THE FILENAME, and the difference is
         # a fact about the gate rather than a convenience. `tenets.json` does
         # not appear in that tool at all: it PAIRS a directly-written asset
         # with its generator by looking the basename up in `tools/*.py` at run
         # time, so it names no such file and naming one would be the hand list
         # this repository keeps having to delete. The walkthrough edge above
         # substantiates on its filename only because that file is also cited in
         # the tool's artifact commentary -- an accident of documentation, not a
         # second mechanism.
         "the gate cannot compare this asset against a source: it is written "
         "into web/public/ rather than copied there. `find_generator` pairs it "
         "with `tenet_map.py` by basename and delegates freshness to that "
         "tool's own --check, which is worth nothing unless the generator has "
         "run first -- hence the edge.",
         "tools/check_web_assets_fresh.py", r"find_generator"),

    Edge("status_board", "check_web_assets_fresh",
         "schemas/V_eta_decisions.json",
         "web/public/decisions.json IS the decision families the board writes; "
         "a stale copy shows a signed family as undecided, which is the exact "
         "failure the artifact was added to remove.",
         "tools/check_web_assets_fresh.py", r"V_eta_decisions\.json"),
]


# --------------------------------------------------------------------------
# ORDER -- derived
# --------------------------------------------------------------------------

def derive_order(steps=STEPS, edges=EDGES):
    """Deterministic topological sort: Kahn's algorithm, ties broken by
    DECLARATION ORDER so the same graph always yields the same sequence and a
    test can assert it."""
    names = [s.name for s in steps]
    rank = {n: i for i, n in enumerate(names)}
    for e in edges:
        for n in (e.producer, e.consumer):
            if n not in rank:
                raise KeyError(f"edge names an unknown step: {n}")
    preds = {n: set() for n in names}
    succs = {n: set() for n in names}
    for e in edges:
        preds[e.consumer].add(e.producer)
        succs[e.producer].add(e.consumer)
    ready = sorted([n for n in names if not preds[n]], key=rank.get)
    out = []
    while ready:
        n = ready.pop(0)
        out.append(n)
        for m in sorted(succs[n], key=rank.get):
            preds[m].discard(n)
            if not preds[m] and m not in out and m not in ready:
                ready.append(m)
        ready.sort(key=rank.get)
    if len(out) != len(names):
        raise ValueError(f"dependency cycle among: {sorted(set(names) - set(out))}")
    return out


ORDER = derive_order()

# Every step that must be SKIPPED when a given step fails (transitive closure
# of the edges). Continuing past a failed producer would gate against a stale
# artifact and report it green, which is the whole defect this driver exists
# to stop.
def _dependents():
    succ = {s.name: set() for s in STEPS}
    for e in EDGES:
        succ[e.producer].add(e.consumer)
    closure = {}
    for n in succ:
        seen, stack = set(), list(succ[n])
        while stack:
            m = stack.pop()
            if m in seen:
                continue
            seen.add(m)
            stack.extend(succ[m])
        closure[n] = seen
    return closure


DEPENDENTS = _dependents()


# --------------------------------------------------------------------------
# running
# --------------------------------------------------------------------------

def run_step(step, cwd):
    t0 = time.time()
    try:
        p = subprocess.run(step.argv, cwd=cwd, capture_output=True, text=True,
                           env=child_env(), check=False)
        out = (p.stdout or "") + (p.stderr or "")
        rc = p.returncode
    except FileNotFoundError as exc:
        return {"rc": 127, "out": f"{exc}\n", "secs": time.time() - t0,
                    "headline": None, "missing_tool": True}
    m = step.headline.search(out)
    return {"rc": rc, "out": out, "secs": time.time() - t0,
                "headline": m.group(1) if m else None, "missing_tool": False}


def _snapshot(paths, root):
    """Content digest of exactly the paths this driver could write. Narrow on
    purpose: other agents edit this tree concurrently, so a whole-tree hash
    would report their work as our mutation."""
    h = {}
    for rel in paths:
        p = os.path.join(root, rel)
        if os.path.isdir(p):
            d = hashlib.sha256()
            for base, dirs, files in os.walk(p):
                dirs.sort()
                for f in sorted(files):
                    fp = os.path.join(base, f)
                    d.update(os.path.relpath(fp, p).encode())
                    with open(fp, "rb") as fh:
                        d.update(fh.read())
            h[rel] = d.hexdigest()
        elif os.path.exists(p):
            with open(p, "rb") as fh:
                h[rel] = hashlib.sha256(fh.read()).hexdigest()
        else:
            h[rel] = "ABSENT"
    return h


def mirror_tracked_tree(root, dest):
    """Copy every TRACKED path into a scratch dir. Tracked, so the mirror is
    the versioned repo and nothing else; from the WORKING TREE, so a developer
    checking their own uncommitted edit sees its effect. On a clean checkout --
    which is what CI has -- the two are the same thing, and this is then
    literally "regenerate and diff against what is committed"."""
    files = subprocess.run(["git", "-C", root, "ls-files", "-z"],
                           capture_output=True, text=True, check=True)
    n = 0
    for rel in files.stdout.split("\0"):
        if not rel:
            continue
        src = os.path.join(root, rel)
        if not os.path.exists(src):
            continue
        dst = os.path.join(dest, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        n += 1
    return n


def diff_artifact(rel, mirror, root):
    """Return (identical, detail) for one generated artifact."""
    a, b = os.path.join(root, rel), os.path.join(mirror, rel)
    if os.path.isdir(b) or os.path.isdir(a):
        p = subprocess.run(["diff", "-rq", a, b], capture_output=True, text=True, check=False)
        if p.returncode == 0:
            return True, ""
        return False, p.stdout.strip()
    p = subprocess.run(["diff", "-u", a, b], capture_output=True, text=True, check=False)
    if p.returncode == 0:
        return True, ""
    body = [ln for ln in p.stdout.splitlines()
            if ln[:1] in "+-" and not ln.startswith(("+++", "---"))]
    # PRINT THE LINES, NOT JUST HOW MANY. On 2026-08-11 this said
    # "V_eta_STATUS.md DIFFERS -- 4 changed line(s)" on a runner for three
    # consecutive runs while the same command reproduced NOTHING locally, and
    # the count alone gave no way to tell an artifact that had genuinely
    # drifted from one whose generator behaves differently where the sibling
    # repos are absent. A gate that reports a magnitude and withholds the
    # evidence sends the reader back to guessing -- which is the whole failure
    # mode `AN INSTRUMENT MUST REPORT ITS DENOMINATOR` exists to stop.
    #
    # Bounded, because an artifact can legitimately differ by thousands of
    # lines and a CI log is read by scrolling: the first CAP lines, each
    # truncated, and the remainder counted rather than dropped silently.
    CAP, WIDTH = 12, 200
    detail = [f'{len(body)} changed line(s)']
    for ln in body[:CAP]:
        detail.append("      " + (ln[:WIDTH] + " ..." if len(ln) > WIDTH else ln))
    if len(body) > CAP:
        detail.append(f'      ... {len(body) - CAP} further changed line(s) not shown')
    return False, "\n".join(detail)


# --------------------------------------------------------------------------

def explain(root=REPO, out=print):
    order = derive_order()
    out(f'DENOMINATOR: {len(STEPS)} steps declared, {len(EDGES)} dependency edge(s) to substantiate')
    out("")
    out("DERIVED ORDER (topological sort of the edges below; ties by declaration order)")
    for i, n in enumerate(order, 1):
        s = BY_NAME[n]
        ups = sorted({e.producer for e in EDGES if e.consumer == n},
                     key=order.index)
        out(f'  {i:>2}. {n:<34} {s.kind:<9} after: {", ".join(ups) or "-"}')
    out("")
    out("EDGES -- each reason is CHECKED, not asserted: the witness is a literal")
    out("the CONSUMER's own source must contain to be reading that artifact.")
    bad = 0
    for e in EDGES:
        ok, detail = e.substantiated(root)
        if not ok:
            bad += 1
        out("  [{}] {} -> {}".format("OK" if ok else "UNSUBSTANTIATED",
                                 e.producer, e.consumer))
        out(f"       artifact: {e.artifact}")
        out(f"       reason  : {e.reason}")
        out(f"       witness : {detail} in {e.witness_file}" if ok
            else f"       witness : {detail}")
    out("")
    out(f'EDGES SUBSTANTIATED: {len(EDGES) - bad} of {len(EDGES)}')
    out("")
    out("SIBLING CHECKOUTS -- the reason CI cannot run the whole chain.")
    needs = [s for s in STEPS if s.requires]
    out(f'DENOMINATOR: {len(needs)} of {len(STEPS)} steps read a sibling repository')
    for n, p in sorted(SIBLINGS.items()):
        out(f'  {n:<12} {p or "NOT FOUND"}')
    for s in needs:
        src = s.source_path()
        unnamed = []
        if src and os.path.exists(os.path.join(root, src)):
            with open(os.path.join(root, src), errors="replace") as fh:
                body = fh.read()
            unnamed = [n for n in s.requires if n not in body]
        mark = "OK" if not unnamed else "UNSUBSTANTIATED"
        out(f'  [{mark}] {s.name:<34} needs {", ".join(s.requires)}{"" if not unnamed else f"  -- {unnamed} never named in {src}"}')
        if unnamed:
            bad += 1
    out("")
    out("PATH PRECONDITIONS -- a step whose SUBJECT is absent has nothing to")
    out("measure, and reporting that is not the same as passing.")
    needy = [s for s in STEPS if s.needs_paths]
    out(f'DENOMINATOR: {len(needy)} of {len(STEPS)} steps declare a path precondition')
    for s in needy:
        for p in s.needs_paths:
            here = os.path.exists(os.path.join(root, p))
            out(f'  [{"PRESENT" if here else "ABSENT"}] {s.name:<34} needs {p}')
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Run the V_eta regenerate-and-gate chain once, in order.")
    ap.add_argument("--check", action="store_true",
                    help="regenerate into a scratch mirror and diff; never "
                         "writes to the working tree")
    ap.add_argument("--explain", action="store_true",
                    help="print the derived order and its evidence; run nothing")
    ap.add_argument("--only", action="append", default=None, metavar="STEP",
                    help="run only these steps (still in derived order)")
    ap.add_argument("--list", action="store_true", help="print step names, one per line")
    ap.add_argument("--ci", action="store_true",
                    help="implies --check, and reports (rather than fails) the "
                         "steps whose subject is not on a runner -- an "
                         "NDI-matlab / DID-matlab checkout, or the viewer's "
                         "gitignored web/public tree")
    a = ap.parse_args(argv)
    if a.ci:
        a.check = True

    if a.list:
        for n in ORDER:
            print(n)
        return 0
    if a.explain:
        return explain()

    order = [n for n in ORDER if not a.only or n in a.only]
    steps = [BY_NAME[n] for n in order]
    gens = [s for s in steps if s.kind == "generate"]

    # ---------------- RULE 5: the denominator, first and unconditional ------
    ok_edges = sum(1 for e in EDGES if e.substantiated(REPO)[0])
    print("=" * 78)
    print("V_eta CHAIN -- %s" % ("--check (scratch mirror; working tree untouched)"
                                 if a.check else "regenerate + gate"))
    print(f'DENOMINATOR: {len(steps)} steps will run ({len(gens)} generate, {len(steps) - len(gens)} gate); {len(EDGES)} dependency edges, {ok_edges} substantiated')
    print("            order: {}".format(" -> ".join(order)))
    unavailable = [s.name for s in steps if s.unavailable]
    if unavailable:
        print(f'            NOT RUNNABLE HERE ({len(unavailable)}): {", ".join(unavailable)}')
        for n, p in sorted(SIBLINGS.items()):
            print(f'              sibling {n:<12} {p or "NOT FOUND"}')
        for s in steps:
            for p in s.missing_paths:
                print(f'              path    {p:<12} ABSENT (needed by {s.name})')
        if not a.ci:
            print("              these will be ATTEMPTED anyway and will fail; "
                  "pass --ci to report them as not-runnable instead.")
    print("=" * 78)
    sys.stdout.flush()

    if ok_edges != len(EDGES):
        print(f'FAIL: {len(EDGES) - ok_edges} dependency edge(s) could not be substantiated. Run --explain.')
        return 1

    mirror = None
    watched = sorted({w for s in STEPS for w in s.writes})
    before = _snapshot(watched, REPO)
    will_generate = [s for s in steps
                     if s.kind == "generate" and not (a.ci and s.unavailable)]
    if a.check and will_generate:
        mirror = tempfile.mkdtemp(prefix="veta-gates-check-")
        n = mirror_tracked_tree(REPO, mirror)
        print(f'scratch mirror: {mirror}  ({n} tracked file(s) copied)')
        print()

    results, failed, skipped, composed_failed, no_sibling = {}, [], [], [], []
    t_all = time.time()
    for i, s in enumerate(steps, 1):
        if a.ci and s.unavailable:
            # NOT a failure and NOT a skip: the checkout simply is not here.
            # It must still be COUNTED and NAMED, or a shorter chain would read
            # as a complete one -- which is the whole defect this file is about.
            no_sibling.append(s.name)
            print(f'[{i:>2}/{len(steps):>2}] {s.name:<34} NOT-RUNNABLE ({", ".join(s.unavailable)} absent here; step not attempted)')
            continue
        blockers = [f for f in failed + skipped
                    if BY_NAME[f].blocks_dependents
                    and s.name in DEPENDENTS.get(f, ())]
        if blockers:
            skipped.append(s.name)
            print(f'[{i:>2}/{len(steps):>2}] {s.name:<34} SKIPPED   (producer failed: {", ".join(blockers)})')
            continue

        # In --check the GENERATORS run inside the mirror; the read-only gates
        # run against the working tree, which is what a developer wants graded.
        cwd = mirror if (a.check and s.kind == "generate") else REPO
        argv_used = s.argv
        r = run_step(s, cwd)
        results[s.name] = r

        why = ""
        if r["missing_tool"]:
            status = "MISSING"
            why = f"   executable not found: {s.argv[0]}"
        elif r["rc"] != 0:
            status = "FAIL"
            why = f'   exit={r["rc"]}'
        elif r["headline"] is None:
            status = "NO-HEADLINE"
            why = (f"   exit=0 but the step never printed {s.headline_label!r} -- a step that "
                   "reports nothing is indistinguishable from one that was "
                   "skipped")
        else:
            status = "OK"
        print("[%2d/%2d] %-34s %-11s %6.2fs   %s"
              % (i, len(steps), s.name, status, r["secs"],
                 ("{}: {}".format(r["headline"], s.headline_label))
                 if r["headline"] else "(no headline)"))
        if why:
            print(why)
        if status != "OK":
            failed.append(s.name)
            tail = [ln for ln in r["out"].splitlines() if ln.strip()][-12:]
            for ln in tail:
                print("        | " + ln)
        sys.stdout.flush()
        del argv_used

    # ---------------- --check: the diff -------------------------------------
    diffs = []
    if a.check and not mirror:
        print()
        print("ARTIFACT DIFF: 0 artifact(s) compared -- no generator ran in this "
              "selection, so nothing was regenerated and nothing is claimed.")
    if a.check and mirror:
        print()
        print("ARTIFACT DIFF -- regenerated (scratch) vs committed (working tree)")
        arts = [w for s in steps if s.kind == "generate" and s.name in results
                for w in s.writes]
        not_compared = [w for s in steps if s.kind == "generate"
                        and s.name not in results for w in s.writes]
        print(f'DENOMINATOR: {len(arts)} generated artifact(s) compared')
        for rel in arts:
            same, detail = diff_artifact(rel, mirror, REPO)
            print("  %-42s %s%s" % (rel, "IDENTICAL" if same else "DIFFERS",
                                    ("  -- " + detail.replace("\n", "; ")[:160])
                                    if detail else ""))
            if not same:
                diffs.append(rel)
        # NOT CHECKED is not the same as CHECKED AND CLEAN. Say so, with names.
        print(f'  NOT COMPARED (their generator did not run here): {len(not_compared)}{(" -- " + ", ".join(not_compared)) if not_compared else ""}')
        # Compose the tools that ship their own --check rather than trusting
        # only our diff. Two instruments, one question.
        print()
        print("COMPOSED --check (each tool's own, against the working tree)")
        composed = [s for s in steps if s.check_argv and s.name in results]
        print(f'DENOMINATOR: {len([s for s in steps if s.check_argv])} step(s) ship a --check of their own; {len(composed)} run here')
        for s in composed:
            p = subprocess.run(s.check_argv, cwd=REPO, capture_output=True,
                               text=True, env=child_env(), check=False)
            print(f'  {s.name + " --check":<42} exit={p.returncode}')
            if p.returncode != 0:
                for ln in (p.stdout + p.stderr).strip().splitlines()[-6:]:
                    print("        | " + ln)
                composed_failed.append(s.name)

    # ---------------- did we keep our hands off the tree? -------------------
    after = _snapshot(watched, REPO)
    touched = sorted(k for k in before if before[k] != after.get(k))
    if a.check:
        print()
        print(f'WORKING-TREE GUARD: {len(watched)} watched path(s); {len(touched)} changed during the run')
        for k in touched:
            print(f"  CHANGED: {k}")
        if touched:
            print("  In --check every generator runs with cwd inside the scratch "
                  "mirror, so this driver wrote none of these. Either that is a "
                  "bug here or another process is regenerating concurrently -- "
                  "in both cases the diff above cannot be trusted, so this run "
                  "fails rather than reporting a verdict it did not earn.")

    # ---------------- summary ------------------------------------------------
    ran = len(results)
    print()
    print("=" * 78)
    print(f'SUMMARY: {len(steps)} step(s) declared, {ran} ran, {ran - len(failed)} passed, {len(failed)} failed, {len(skipped)} skipped, {len(no_sibling)} not runnable here')
    if no_sibling:
        print("  NOT RUNNABLE HERE: {}  (needs an NDI-matlab / DID-matlab "
              "checkout, or a path this checkout does not have; NOT evidence "
              "they would pass)".format(", ".join(no_sibling)))
    if failed:
        print("  FAILED : {}".format(", ".join(failed)))
    if skipped:
        print("  SKIPPED: {}  (a producer they depend on failed)".format(", ".join(skipped)))
    if composed_failed:
        print("  COMPOSED --check FAILED: {}".format(", ".join(composed_failed)))
    if a.check:
        print(f'  ARTIFACTS DIFFERING FROM THE COMMITTED COPY: {len(diffs)}{(" -- " + ", ".join(diffs)) if diffs else ""}')
    print(f'  WALL CLOCK: {time.time() - t_all:.2f}s total')
    for n in order:
        if n in results:
            print(f'      {n:<34} {results[n]["secs"]:6.2f}s')
    print("=" * 78)

    if mirror:
        shutil.rmtree(mirror, ignore_errors=True)

    if failed or skipped or composed_failed or (a.check and (diffs or touched)):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
