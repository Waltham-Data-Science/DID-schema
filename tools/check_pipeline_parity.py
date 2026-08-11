#!/usr/bin/env python3
"""Do the DID corpus gate and NDI production run the SAME batch post-passes?

WHY THIS EXISTS

The V_eta migration is two halves. `did2.convert.v1_to_v2` converts one
document at a time; a chain of BATCH POST-PASSES then runs over the whole
migrated corpus to do what a single-document migrator cannot -- mint epochs,
resolve session anchors, fold citation graphs, assemble subject tiers.

Nothing composes that chain in `DID-matlab/src`. Every pass has ZERO call
sites there, which is not a defect -- they are library functions, and the
CALLER composes them. There are two callers:

    DID-matlab tests/+did2/+unittest/+helpers/runCorpusDiscovery.m
        the six-corpus gate, ~633,000 documents, the expensive measurement
        this project trusts

    NDI-matlab src/ndi/+ndi/+migrate/
        what actually migrates a user's data

**Those two lists are allowed to differ, and they DO -- but nothing compared
them.** NDI's own source says so, in `+ndi/+migrate/+internal/epochAnchorFold.m`:

    it was invisible to the DID corpus gate because that gate runs the coarse
    did2.convert.resolveDeferredBaths instead, which NDI deliberately
    substitutes this assembler for ... two pipelines emitting different
    classes for one concept, and nothing comparing them.

and `+ndi/+migrate/local.m` records what that cost:

    Ten divergent rows is enough noise to hide an eleventh, which is precisely
    how resolveDatasetEntities came to sit unwired.

That is the failure mode. A DECLARED divergence is fine -- NDI supersedes
`resolveDeferredBaths` with `stimulusBathToBath` on purpose, and says so in
four places. An UNDECLARED one is a pass that runs in the gate and not in
production (so the corpus proves a pipeline nobody ships) or in production and
not in the gate (so it ships unmeasured). Both are invisible today, and one of
them has already happened.

WHAT THIS DOES NOT DO. It does not decide which side is right, it does not
require the lists to match, and it never edits either repo. It requires only
that every difference be DECLARED, with a reason, in `DECLARED_DIVERGENCES`
below. An undeclared difference is the failure.

RULE 5 THROUGHOUT. Both denominators print first and unconditionally: files
scanned and passes found, per side. A run that scanned nothing must not be
readable as a run that found no divergence -- that is the `silentLoss` defect,
which printed "0 empty edges" for two days while reading no documents.
"""
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The harness that composes the chain for the six-corpus gate.
HARNESS = os.path.join("tests", "+did2", "+unittest", "+helpers",
                       "runCorpusDiscovery.m")
# NDI's production migration package.
NDI_MIGRATE = os.path.join("src", "ndi", "+ndi", "+migrate")

# Not passes: the per-document converter and the cross-cutting rename step run
# inside v1_to_v2, not as batch post-passes, so they are not part of this
# comparison. `readers` is a subpackage, not a pass.
NOT_A_PASS = {"v1_to_v2", "universalRenames", "readers", "migrators",
              "migrators_e", "migrators_i", "migrators_j", "v"}

# ---------------------------------------------------------------------------
# THE DECLARED DIVERGENCES. Each entry is a pass that one side runs and the
# other deliberately does not, plus WHY -- and the why must be checkable
# against the source, not an assertion made here.
#
# Adding a row to this table is a claim that a human decided the divergence.
# It is deliberately inconvenient: a reason is required, and the reason is
# printed in the report every run, so a stale one is visible rather than
# buried.
# ---------------------------------------------------------------------------
DECLARED_DIVERGENCES = {
    "resolveDeferredBaths": (
        "HARNESS ONLY. NDI deliberately substitutes "
        "ndi.migrate.internal.stimulusBathToBath, which its own source calls "
        "\"the LIVE-session counterpart of the coarse "
        "did2.convert.resolveDeferredBaths.makeBathVeta\" "
        "(+ndi/+migrate/local.m, +ndi/+migrate/+internal/epochAnchorFold.m). "
        "CONSEQUENCE, recorded because it is not benign: the six-corpus gate "
        "measures the coarse pass, so NDI's bath assembly -- the one that "
        "ships -- is exercised by NDI's unit tests alone and by no corpus."),
}


def read(path):
    try:
        with open(path, errors="replace") as fh:
            return fh.read()
    except OSError:
        return None


def strip_matlab_comments(text):
    """Drop %-comments and %{ %} blocks.

    DELIBERATELY CRUDE, AND THE DIRECTION OF ERROR IS THE POINT. It does not
    understand a `%` inside a string literal, so it can over-strip. Over-
    stripping can only HIDE a call, which makes this report claim FEWER passes
    than exist -- it can never invent one. A false "undeclared divergence" is
    therefore possible only in the direction of a pass appearing absent, which
    a human reading the named list will spot; a false "everything agrees"
    would be the dangerous direction and this cannot produce it from a call it
    mis-parsed, only from a call it never saw.
    """
    out, in_block = [], False
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("%{"):
            in_block = True
            continue
        if s.startswith("%}"):
            in_block = False
            continue
        if in_block or s.startswith("%"):
            continue
        out.append(re.sub(r"%.*$", "", line))
    return "\n".join(out)


CALL = re.compile(r"did2\.convert\.([A-Za-z_][A-Za-z_0-9]*)")


def passes_in(text):
    return {m for m in CALL.findall(text) if m not in NOT_A_PASS}


def scan_harness(did_root):
    """The pass set the six-corpus gate composes. One named file, on purpose.

    Scanning all of `tests/` would sweep up per-pass unit tests, and a pass
    with its own test file but no place in the chain would read as composed.
    The chain is what this compares, so the chain's file is what is read.
    """
    path = os.path.join(did_root, HARNESS)
    text = read(path)
    if text is None:
        return None, {"files": 0, "missing": path}
    return passes_in(strip_matlab_comments(text)), {"files": 1, "path": path}


def scan_ndi(ndi_root):
    """The pass set NDI production composes, over its migration package."""
    root = os.path.join(ndi_root, NDI_MIGRATE)
    if not os.path.isdir(root):
        return None, {"files": 0, "missing": root}
    found, n = set(), 0
    for dirpath, _dirs, files in os.walk(root):
        for name in sorted(files):
            if not name.endswith(".m"):
                continue
            text = read(os.path.join(dirpath, name))
            if text is None:
                continue
            n += 1
            found |= passes_in(strip_matlab_comments(text))
    return found, {"files": n, "path": root}


def find_repo(name, env):
    """Locate a sibling checkout the way coverage.py and status_board.py do.

    AN EXPLICITLY SET ENVIRONMENT VARIABLE IS AUTHORITATIVE, PRESENT OR NOT --
    the same rule `tools/gates.py` states and for the same reason: it is what
    lets a sibling-less CI be reproduced on a machine that HAS the siblings.
    The first draft of this function fell through a set-but-missing variable to
    `/home/user`, so `NDI_MATLAB=/nowhere` silently found the real checkout and
    the not-runnable path could not be exercised at all. Its test caught that,
    which is the only reason it is written this way now.
    """
    if env in os.environ:
        p = os.environ[env]
        return p if p and os.path.isdir(p) else None
    for cand in (os.path.join("/home/user", name),
                 os.path.join(os.path.dirname(REPO), name)):
        if cand and os.path.isdir(cand):
            return cand
    return None


def main(argv):
    enforce = "--enforce" in argv
    did = find_repo("DID-matlab", "DID_MATLAB")
    ndi = find_repo("NDI-matlab", "NDI_MATLAB")

    print("BATCH POST-PASS PARITY -- the corpus gate's chain vs NDI production's")

    # RULE 5. Both denominators, before any result, and a missing sibling is
    # reported as NOT RUNNABLE rather than as agreement.
    if not did or not ndi:
        print("  DENOMINATOR: 0 file(s) scanned -- sibling checkout(s) absent")
        print(f'    DID-matlab: {did or "NOT FOUND"}')
        print(f'    NDI-matlab: {ndi or "NOT FOUND"}')
        print("  NOT RUNNABLE HERE. This says NOTHING about whether the two")
        print("  pipelines agree; it says the question was not asked.")
        return 0

    hset, hinfo = scan_harness(did)
    nset, ninfo = scan_ndi(ndi)
    if hset is None or nset is None:
        print(f'  DENOMINATOR: harness file(s) {hinfo["files"]}, NDI file(s) {ninfo["files"]}')
        for info in (hinfo, ninfo):
            if info.get("missing"):
                print("  MISSING: {}".format(info["missing"]))
        print("  NOT RUNNABLE HERE -- a source this reads is absent.")
        return 1 if enforce else 0

    both = hset & nset
    harness_only = hset - nset
    ndi_only = nset - hset

    print(f'  DENOMINATOR: {hinfo["files"]} harness file scanned ({os.path.basename(hinfo["path"])}), {ninfo["files"]} NDI file(s) scanned ({NDI_MIGRATE})')
    print(f'  DENOMINATOR: {len(hset)} pass(es) named by the harness, {len(nset)} by NDI, {len(both)} in both')
    print(f'  divergent: {len(harness_only)} harness-only, {len(ndi_only)} NDI-only')

    if not hset or not nset:
        print("  *** ONE SIDE NAMED NO PASSES AT ALL. Every pass on the other")
        print("      side reads as divergent, and the parity result below is")
        print("      meaningless -- this is a broken scan, not a finding.")
        return 1 if enforce else 0

    for label, group in (("HARNESS ONLY", harness_only), ("NDI ONLY", ndi_only)):
        if group:
            print(f'  {label} ({len(group)}):')
            for name in sorted(group):
                why = DECLARED_DIVERGENCES.get(name)
                print("    %-28s %s" % (name, "DECLARED" if why else
                                        "*** UNDECLARED ***"))
                if why:
                    for line in _wrap(why, 66):
                        print(f"      {line}")

    undeclared = sorted((harness_only | ndi_only) - set(DECLARED_DIVERGENCES))
    # A declaration for a pass that no longer diverges is stale in the
    # reassuring direction: it reads as a considered decision about a state
    # that has since changed, which is how a stale exemption survives.
    stale = sorted(set(DECLARED_DIVERGENCES) - (harness_only | ndi_only))
    if stale:
        print(f'  STALE DECLARATION(S) ({len(stale)}) -- these no longer diverge, so the recorded reason describes nothing:')
        for name in stale:
            print(f"    {name}")

    print(f'  RESULT: {len(undeclared)} undeclared divergence(s), {len(stale)} stale declaration(s)')
    if undeclared:
        print("  A pass on only one side is either shipped-but-unmeasured or")
        print("  measured-but-unshipped. Decide which, then declare it in")
        print("  DECLARED_DIVERGENCES with the reason -- do not delete the row.")
    if enforce and (undeclared or stale):
        return 1
    return 0


def _wrap(text, width):
    words, line, out = text.split(), "", []
    for w in words:
        if len(line) + len(w) + 1 > width:
            out.append(line)
            line = w
        else:
            line = (line + " " + w).strip()
    if line:
        out.append(line)
    return out


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
