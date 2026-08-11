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
                 writes=(), check_argv=None, external=False, requires=()):
        self.name = name
        self.argv = list(argv)
        self.kind = kind                      # "generate" | "gate"
        self.headline = re.compile(headline, re.M)
        self.headline_label = headline_label
        self.writes = list(writes)
        # Sibling checkouts this step READS. Named, not guessed: `--explain`
        # requires the step's own source to mention each one.
        self.requires = list(requires)
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

    def source_path(self):
        """The file whose content backs this step's declarations, if any."""
        for a in self.argv:
            if a.endswith(".py"):
                return a
        return None

    def __repr__(self):
        return "Step(%s)" % self.name


def _t(script, *args):
    return [PY, os.path.join("tools", script)] + list(args)


STEPS = [
    # READ THIS BEFORE ACTING ON A `V_eta_ndi_ground_truth.json DIFFERS` ROW.
    # That artifact is NOT reproducible from NDI `origin/main`, even though it
    # records `ndi_ref: "origin/main"` and the tool's own docstring says it
    # reads origin/main and never a feature branch. One function breaks that:
    #
    #     tools/ndi_ground_truth.py:734
    #         for line in sh("log", "--all", "--reverse", "--diff-filter=A",
    #
    # `--all`, so the `v_alpha_divergence[].provenance` verdicts depend on which
    # OTHER refs happen to exist in whoever's NDI clone. Regenerating it in a
    # clone with a different ref set moves 12 of the 67 rows and the headline
    # counts with them:
    #
    #     committed     DID-INVENTED 47 | NDI-CHANGED 0 | UNKNOWN 20
    #     regenerated   DID-INVENTED 36 | NDI-CHANGED 0 | UNKNOWN 31
    #
    # The committed values cannot have come from origin/main. `filter` is
    # recorded as "first NDI version 2026-04-24", but the commit that adds
    # filter.json on origin/main is 68b17ce0b, 2026-02-24 --
    # `git merge-base --is-ancestor 68b17ce0b origin/main` succeeds -- and the
    # function takes the FIRST add in `--reverse` order, so an origin/main read
    # could only ever have said February. The other 11 rows now say "no
    # add-commit found" because no *.json add in April 2026 is reachable here at
    # all.
    #
    # So a DIFFERS row here is a question about the two CLONES, not about this
    # repository, and regenerating would REPLACE 11 verdicts with UNKNOWN --
    # a loss of record dressed as a refresh. Do not commit that refresh; fix the
    # `--all` first, with the team.
    Step("ndi_ground_truth", _t("ndi_ground_truth.py"), "generate",
         r"^NDI classes captured:\s+(\d+)", "NDI classes captured",
         writes=["schemas/V_eta_ndi_ground_truth.json"],
         requires=["NDI-matlab", "DID-matlab"]),

    Step("build_v_eta", _t("build_v_eta.py"), "generate",
         r"^V_eta built: (\d+) schemas", "schemas built",
         writes=["schemas/V_eta"]),

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

    Step("ruff", ["ruff", "check", "tests"], "gate",
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

    Step("check_binding_governance", _t("check_binding_governance.py"), "gate",
         r"V_eta document_class files walked\s+: (\d+)", "class files walked"),

    Step("check_empty_ontology_nodes", _t("check_empty_ontology_nodes.py"), "gate",
         r"V_eta schema files inspected\s+: (\d+)", "schema files inspected",
         requires=["DID-matlab"]),

    Step("check_vacuous_tests", _t("check_vacuous_tests.py", "--enforce"), "gate",
         r"VACUOUS-TEST SWEEP: (\d+) test file\(s\) parsed", "test files parsed"),

    Step("check_signoff_header_staleness",
         _t("check_signoff_header_staleness.py", "--enforce"), "gate",
         r"^DENOMINATOR: (\d+) markdown file\(s\)", "plan documents read"),
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
        return False, "no match for %r in %s" % (self.witness, self.witness_file)


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

    Edge("build_v_eta", "check_constraint_refinement", "schemas/V_eta",
         "same sweep, one level deeper -- it opens the built declarations.",
         "tools/check_constraint_refinement.py", r'"V_eta"'),

    Edge("build_v_eta", "check_binding_governance", "schemas/V_eta",
         "the binding registry it audits is written by the build.",
         "tools/check_binding_governance.py", r'"V_eta"'),

    Edge("build_v_eta", "check_empty_ontology_nodes", "schemas/V_eta",
         "the schema half of the sweep walks the built ontology_term fields.",
         "tools/check_empty_ontology_nodes.py", r'"V_eta"'),

    Edge("build_v_eta", "pytest", "schemas/V_eta",
         "most of tests/test_veta.py asserts against the BUILT tree; running "
         "pytest before the build tests the previous schema set and passes.",
         "tests/test_veta.py", r'"V_eta"'),
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
                raise KeyError("edge names an unknown step: %s" % n)
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
        raise ValueError("dependency cycle among: %s"
                         % sorted(set(names) - set(out)))
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
                           env=child_env())
        out = (p.stdout or "") + (p.stderr or "")
        rc = p.returncode
    except FileNotFoundError as exc:
        return dict(rc=127, out="%s\n" % exc, secs=time.time() - t0,
                    headline=None, missing_tool=True)
    m = step.headline.search(out)
    return dict(rc=rc, out=out, secs=time.time() - t0,
                headline=m.group(1) if m else None, missing_tool=False)


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
        p = subprocess.run(["diff", "-rq", a, b], capture_output=True, text=True)
        if p.returncode == 0:
            return True, ""
        return False, p.stdout.strip()
    p = subprocess.run(["diff", "-u", a, b], capture_output=True, text=True)
    if p.returncode == 0:
        return True, ""
    changed = sum(1 for ln in p.stdout.splitlines()
                  if ln[:1] in "+-" and not ln.startswith(("+++", "---")))
    return False, "%d changed line(s)" % changed


# --------------------------------------------------------------------------

def explain(root=REPO, out=print):
    order = derive_order()
    out("DENOMINATOR: %d steps declared, %d dependency edge(s) to substantiate"
        % (len(STEPS), len(EDGES)))
    out("")
    out("DERIVED ORDER (topological sort of the edges below; ties by declaration order)")
    for i, n in enumerate(order, 1):
        s = BY_NAME[n]
        ups = sorted({e.producer for e in EDGES if e.consumer == n},
                     key=order.index)
        out("  %2d. %-34s %-9s after: %s"
            % (i, n, s.kind, ", ".join(ups) or "-"))
    out("")
    out("EDGES -- each reason is CHECKED, not asserted: the witness is a literal")
    out("the CONSUMER's own source must contain to be reading that artifact.")
    bad = 0
    for e in EDGES:
        ok, detail = e.substantiated(root)
        if not ok:
            bad += 1
        out("  [%s] %s -> %s" % ("OK" if ok else "UNSUBSTANTIATED",
                                 e.producer, e.consumer))
        out("       artifact: %s" % e.artifact)
        out("       reason  : %s" % e.reason)
        out("       witness : %s in %s" % (detail, e.witness_file) if ok
            else "       witness : %s" % detail)
    out("")
    out("EDGES SUBSTANTIATED: %d of %d" % (len(EDGES) - bad, len(EDGES)))
    out("")
    out("SIBLING CHECKOUTS -- the reason CI cannot run the whole chain.")
    needs = [s for s in STEPS if s.requires]
    out("DENOMINATOR: %d of %d steps read a sibling repository" % (len(needs), len(STEPS)))
    for n, p in sorted(SIBLINGS.items()):
        out("  %-12s %s" % (n, p or "NOT FOUND"))
    for s in needs:
        src = s.source_path()
        unnamed = []
        if src and os.path.exists(os.path.join(root, src)):
            with open(os.path.join(root, src), errors="replace") as fh:
                body = fh.read()
            unnamed = [n for n in s.requires if n not in body]
        mark = "OK" if not unnamed else "UNSUBSTANTIATED"
        out("  [%s] %-34s needs %s%s"
            % (mark, s.name, ", ".join(s.requires),
               "" if not unnamed else "  -- %s never named in %s" % (unnamed, src)))
        if unnamed:
            bad += 1
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
                         "steps that need an NDI-matlab / DID-matlab checkout "
                         "the workflow does not have")
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
    print("DENOMINATOR: %d steps will run (%d generate, %d gate); "
          "%d dependency edges, %d substantiated"
          % (len(steps), len(gens), len(steps) - len(gens), len(EDGES), ok_edges))
    print("            order: %s" % " -> ".join(order))
    unavailable = [s.name for s in steps if s.missing_siblings]
    if unavailable:
        print("            NOT RUNNABLE HERE (%d): %s"
              % (len(unavailable), ", ".join(unavailable)))
        for n, p in sorted(SIBLINGS.items()):
            print("              sibling %-12s %s" % (n, p or "NOT FOUND"))
        if not a.ci:
            print("              these will be ATTEMPTED anyway and will fail; "
                  "pass --ci to report them as not-runnable instead.")
    print("=" * 78)
    sys.stdout.flush()

    if ok_edges != len(EDGES):
        print("FAIL: %d dependency edge(s) could not be substantiated. "
              "Run --explain." % (len(EDGES) - ok_edges))
        return 1

    mirror = None
    watched = sorted({w for s in STEPS for w in s.writes})
    before = _snapshot(watched, REPO)
    will_generate = [s for s in steps
                     if s.kind == "generate" and not (a.ci and s.missing_siblings)]
    if a.check and will_generate:
        mirror = tempfile.mkdtemp(prefix="veta-gates-check-")
        n = mirror_tracked_tree(REPO, mirror)
        print("scratch mirror: %s  (%d tracked file(s) copied)" % (mirror, n))
        print()

    results, failed, skipped, composed_failed, no_sibling = {}, [], [], [], []
    t_all = time.time()
    for i, s in enumerate(steps, 1):
        if a.ci and s.missing_siblings:
            # NOT a failure and NOT a skip: the checkout simply is not here.
            # It must still be COUNTED and NAMED, or a shorter chain would read
            # as a complete one -- which is the whole defect this file is about.
            no_sibling.append(s.name)
            print("[%2d/%2d] %-34s NO-SIBLING (%s absent; step not attempted)"
                  % (i, len(steps), s.name, ", ".join(s.missing_siblings)))
            continue
        blockers = [f for f in failed + skipped
                    if BY_NAME[f].blocks_dependents
                    and s.name in DEPENDENTS.get(f, ())]
        if blockers:
            skipped.append(s.name)
            print("[%2d/%2d] %-34s SKIPPED   (producer failed: %s)"
                  % (i, len(steps), s.name, ", ".join(blockers)))
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
            why = "   executable not found: %s" % s.argv[0]
        elif r["rc"] != 0:
            status = "FAIL"
            why = "   exit=%d" % r["rc"]
        elif r["headline"] is None:
            status = "NO-HEADLINE"
            why = ("   exit=0 but the step never printed %r -- a step that "
                   "reports nothing is indistinguishable from one that was "
                   "skipped" % s.headline_label)
        else:
            status = "OK"
        print("[%2d/%2d] %-34s %-11s %6.2fs   %s"
              % (i, len(steps), s.name, status, r["secs"],
                 ("%s: %s" % (r["headline"], s.headline_label))
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
        print("DENOMINATOR: %d generated artifact(s) compared" % len(arts))
        for rel in arts:
            same, detail = diff_artifact(rel, mirror, REPO)
            print("  %-42s %s%s" % (rel, "IDENTICAL" if same else "DIFFERS",
                                    ("  -- " + detail.replace("\n", "; ")[:160])
                                    if detail else ""))
            if not same:
                diffs.append(rel)
        # NOT CHECKED is not the same as CHECKED AND CLEAN. Say so, with names.
        print("  NOT COMPARED (their generator did not run here): %d%s"
              % (len(not_compared),
                 (" -- " + ", ".join(not_compared)) if not_compared else ""))
        # Compose the tools that ship their own --check rather than trusting
        # only our diff. Two instruments, one question.
        print()
        print("COMPOSED --check (each tool's own, against the working tree)")
        composed = [s for s in steps if s.check_argv and s.name in results]
        print("DENOMINATOR: %d step(s) ship a --check of their own; %d run here"
              % (len([s for s in steps if s.check_argv]), len(composed)))
        for s in composed:
            p = subprocess.run(s.check_argv, cwd=REPO, capture_output=True,
                               text=True, env=child_env())
            print("  %-42s exit=%d" % (s.name + " --check", p.returncode))
            if p.returncode != 0:
                for ln in (p.stdout + p.stderr).strip().splitlines()[-6:]:
                    print("        | " + ln)
                composed_failed.append(s.name)

    # ---------------- did we keep our hands off the tree? -------------------
    after = _snapshot(watched, REPO)
    touched = sorted(k for k in before if before[k] != after.get(k))
    if a.check:
        print()
        print("WORKING-TREE GUARD: %d watched path(s); %d changed during the run"
              % (len(watched), len(touched)))
        for k in touched:
            print("  CHANGED: %s" % k)
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
    print("SUMMARY: %d step(s) declared, %d ran, %d passed, %d failed, %d skipped, "
          "%d not runnable here"
          % (len(steps), ran, ran - len(failed), len(failed), len(skipped),
             len(no_sibling)))
    if no_sibling:
        print("  NOT RUNNABLE HERE: %s  (needs an NDI-matlab / DID-matlab "
              "checkout; NOT evidence they would pass)" % ", ".join(no_sibling))
    if failed:
        print("  FAILED : %s" % ", ".join(failed))
    if skipped:
        print("  SKIPPED: %s  (a producer they depend on failed)" % ", ".join(skipped))
    if composed_failed:
        print("  COMPOSED --check FAILED: %s" % ", ".join(composed_failed))
    if a.check:
        print("  ARTIFACTS DIFFERING FROM THE COMMITTED COPY: %d%s"
              % (len(diffs), (" -- " + ", ".join(diffs)) if diffs else ""))
    print("  WALL CLOCK: %.2fs total" % (time.time() - t_all))
    for n in order:
        if n in results:
            print("      %-34s %6.2fs" % (n, results[n]["secs"]))
    print("=" * 78)

    if mirror:
        shutil.rmtree(mirror, ignore_errors=True)

    if failed or skipped or composed_failed or (a.check and (diffs or touched)):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
