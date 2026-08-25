#!/usr/bin/env python3
"""Does any plan document claim to be unsigned while carrying a signature?

WHY THIS EXISTS
---------------
Sign-offs are appended at the BOTTOM of a plan document. The reader's summary of
its state is at the TOP. Nothing kept the two in agreement, so a document could --
and repeatedly did -- open with "NO `TEAM-SIGN-OFF` LINE, the marker is the team's
to write" while carrying that marker several hundred lines below.

This is not a cosmetic defect. It cost real time three separate ways:

  * `V_eta_clock_alignment_cluster_plan.md` sat unbuilt for a day because its
    header said the family was awaiting a signature that had been present for 474
    lines. That was found by accident.
  * `V_eta_stimulus_parameter_plan.md` had the identical defect for two days,
    found on 2026-08-10 while looking for something else.
  * The same sweep then found FOUR MORE: `V_eta_epoch_plan.md`,
    `V_eta_ingested_payload_findings.md`, `V_eta_stimulus_response_model_plan.md`
    and `V_eta_daq_family_decisions.md`. Six documents, five signed families, all
    reading as unsigned to anyone who stopped at the header.

The failure mode is specific and one-directional: the header always claims LESS
progress than the record holds, so the cost is always work not done rather than
work wrongly done. `status_board.py` was never fooled -- it reads the signature,
not the prose -- which is exactly why nobody noticed. The board said "signed" and
the document said "unsigned", and the human read the document.

WHAT IT CHECKS
--------------
One rule, mechanical: a file containing a line that starts with `TEAM-SIGN-OFF`
must not ALSO contain an assertion that no such line exists. The assertion is
matched loosely (any casing, backticks optional) so a paraphrase does not slip
through, and a line that merely QUOTES the old claim in a correction note is
exempted by the marker below.

    HISTORICAL-SIGNOFF-CLAIM

Put that marker on, or immediately adjacent to, a line that reproduces the stale
wording as history rather than asserting it. Every correction written on
2026-08-10 does this, which is why they do not re-trip the check.

It does NOT check that the signature matches the section, the family, or the
build state. It checks the one thing that was wrong six times.

KNOWN LIMITATION -- it cannot tell WHICH document a claim is about
-----------------------------------------------------------------
The rule is "a file must not assert that IT is unsigned", but the match is on
wording alone. A signed document that truthfully says *another* document has no
signature line trips it as a false positive. That happened on 2026-08-10:
`V_eta_epoch_plan.md` (signed) recorded that the raw-recording plan is not, and
the gate fired.

The fix is NOT to exempt it -- `HISTORICAL-SIGNOFF-CLAIM` means "this quotes a
claim that used to be made", and a live true statement about a different file is
not that. Write cross-document claims as "<doc> is not yet signed" instead, and
keep the `NO TEAM-SIGN-OFF LINE` phrasing for what a document says about itself.
The narrow wording is deliberate: broadening the regex to catch paraphrases would
make this ambiguity common instead of rare.

THE SECOND RULE -- the same lie in the tool source
--------------------------------------------------
Fixing the six documents surfaced SEVEN MORE instances one layer down, in
`tools/status_board.py` itself: seven `FAMILIES` entries carried a comment saying
"DECIDED with the team <date>, no signature yet" for families that the board's own
generated output reports as signed. The board rendered "0 awaiting a signature"
while its source said the opposite about seven of the eighteen.

So: if `V_eta_decisions.json` reports ZERO families awaiting a signature, no file
under `tools/` may claim any family is awaiting one. Driven off the generated
artifact rather than a hardcoded expectation, so it relaxes automatically the
moment a genuinely unsigned family appears. Phrases that are RENDERING STRINGS
("awaiting a signature" as a heading the board prints) are not claims about a
family and are not matched -- only the "no signature yet" assertion form is.

THE THIRD RULE -- a BUILD claim inside the signature itself
-----------------------------------------------------------
Rules 1 and 2 police whether a document admits it is SIGNED. Neither looks at
what a signature SAYS, and a signature's tail routinely carries a build state.
Found 2026-08-15, walking PRED's target classes:

  * `V_eta_go_forward_class_audit.md` `TEAM-SIGN-OFF [session]` ends "NOT YET
    BUILT" and names three artifacts. All three exist -- the schema field, the
    migrator, and the NDI-matlab read site.
  * `V_eta_OPEN_WORK.md` `TEAM-SIGN-OFF [epoch extent -- row #113]` ends "NOT
    YET BUILT". `did2.convert.epochMint` mints the extent references and
    carries twelve `epoch_extent_*` counters for them.

Same one-directional shape as rules 1 and 2 -- the record claims LESS progress
than exists, so the cost is a build repeated rather than a build wrongly made.
And the same cause: the claim and the thing it describes are updated by
different acts, with nothing between them.

THE RULE CANNOT BE "IS IT ACTUALLY BUILT" -- no artifact in this repo answers
that per signature, and inventing an inference would be worse than the gap.
What it CAN require is that the claim be maintained: a signature line asserting
`NOT BUILT` / `NOT YET BUILT` must have a dated

    BUILD-STATE:

line within twenty lines BELOW it (two above, for a lead-in), carrying the
command output that establishes the state as of that date.

CRITICALLY, THE FIX IS NEVER TO EDIT THE SIGNATURE. Operating Rule 4 says the
`TEAM-SIGN-OFF` line is the team's; striking "NOT YET BUILT" out of one would
rewrite what was signed. The note goes BESIDE it, which is also why the window
is asymmetric -- signatures are appended at the bottom of a document and there
is often nothing above them.

Usage:  python3 tools/check_signoff_header_staleness.py
        python3 tools/check_signoff_header_staleness.py --enforce
"""

import argparse
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SCHEMA_DIR = os.path.join(REPO, "schemas")
DECISIONS = os.path.join(SCHEMA_DIR, "V_eta_decisions.json")
TOOLS_DIR = HERE

# "NO `TEAM-SIGN-OFF` LINE", "no TEAM-SIGN-OFF line", "NO TEAM SIGN-OFF LINE".
NO_SIGNOFF_RE = re.compile(r"\bno\s+`?team[\s_-]*sign[\s_-]*off`?\s+line\b", re.IGNORECASE)
HAS_SIGNOFF_RE = re.compile(r"^TEAM-SIGN-OFF\b")
EXEMPT = "HISTORICAL-SIGNOFF-CLAIM"

# The assertion form only. "awaiting a signature" is a heading the board PRINTS
# for whatever is genuinely unsigned, and matching it would flag the renderer.
UNSIGNED_CLAIM_RE = re.compile(r"\bno\s+signature\s+yet\b", re.IGNORECASE)

# RULE 3 -- a build claim in the TAIL of a signature line. See the module
# docstring. Matched ONLY on lines that are themselves signatures.
BUILD_CLAIM_RE = re.compile(r"\bnot\s+(?:yet\s+)?built\b", re.IGNORECASE)
BUILD_STATE = "BUILD-STATE:"
# The note goes AFTER the signature, because a signature is appended at the
# bottom of a document and there is frequently nothing above it. Asymmetric on
# purpose; 2 lines of slack above covers a note written as a lead-in.
BUILD_WINDOW_BEFORE = 2
BUILD_WINDOW_AFTER = 20


def families_awaiting_signature():
    """Read the GENERATED decisions doc, not a hardcoded expectation.

    Returns (count, total) or (None, None) if the artifact is unreadable -- which
    is itself reported rather than silently treated as zero."""
    try:
        import json
        with open(DECISIONS, encoding="utf-8") as fh:
            fams = json.load(fh)["families"]
    except (OSError, KeyError, ValueError):
        return None, None
    awaiting = [f for f in fams if f.get("state") == "awaiting_signature"]
    return len(awaiting), len(fams)


def scan_tools_for_unsigned_claims():
    """Rows where tool source says a family is unsigned. Returns (rows, files)."""
    rows = []
    files = 0
    for name in sorted(os.listdir(TOOLS_DIR)):
        if not name.endswith(".py") or name == os.path.basename(__file__):
            continue
        path = os.path.join(TOOLS_DIR, name)
        try:
            with open(path, encoding="utf-8") as fh:
                lines = fh.read().splitlines()
        except OSError:
            continue
        files += 1
        for i, ln in enumerate(lines):
            if UNSIGNED_CLAIM_RE.search(ln):
                window = lines[max(0, i - 2):i + 3]
                if any(EXEMPT in w for w in window):
                    continue
                rows.append((path, i + 1, ln.strip()))
    return rows, files


def scan_signoff_build_claims(paths):
    """RULE 3: signature lines asserting NOT (YET) BUILT with no adjacent note.

    Returns (rows, claims_found). `claims_found` is the denominator that
    matters -- "0 unaccompanied" means nothing without "out of how many build
    claims", and a regex that stopped matching would print the same zero."""
    rows = []
    claims = 0
    for path in sorted(paths):
        try:
            with open(path, encoding="utf-8") as fh:
                lines = fh.read().splitlines()
        except OSError:
            continue
        for i, ln in enumerate(lines):
            if not HAS_SIGNOFF_RE.match(ln):
                continue
            if not BUILD_CLAIM_RE.search(ln):
                continue
            claims += 1
            lo = max(0, i - BUILD_WINDOW_BEFORE)
            hi = i + BUILD_WINDOW_AFTER + 1
            if any(BUILD_STATE in w for w in lines[lo:hi]):
                continue
            rows.append((path, i + 1, ln.strip()[:160]))
    return rows, claims


def scan(paths):
    """Return (rows, denominator) where denominator is what was actually read."""
    rows = []
    read = 0
    signed = 0
    for path in sorted(paths):
        try:
            with open(path, encoding="utf-8") as fh:
                lines = fh.read().splitlines()
        except OSError as exc:
            rows.append((path, 0, f"UNREADABLE: {exc}"))
            continue
        read += 1
        signoffs = [i for i, ln in enumerate(lines) if HAS_SIGNOFF_RE.match(ln)]
        if not signoffs:
            continue
        signed += 1
        for i, ln in enumerate(lines):
            if not NO_SIGNOFF_RE.search(ln):
                continue
            # Exempt a correction note: the marker may be on the line itself or
            # within two lines either side, since the wording is usually quoted
            # inside a paragraph that explains it.
            window = lines[max(0, i - 2):i + 3]
            if any(EXEMPT in w for w in window):
                continue
            rows.append((path, i + 1, ln.strip()))
    return rows, read, signed


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--enforce", action="store_true",
                    help="exit non-zero if any stale header is found")
    args = ap.parse_args()

    paths = glob.glob(os.path.join(SCHEMA_DIR, "*.md"))
    rows, read, signed = scan(paths)

    # DENOMINATOR FIRST, unconditionally (Operating Rule 5). "0 stale" is
    # meaningless without "out of how many signed documents" -- a glob that
    # matched nothing would otherwise print the same reassuring zero.
    print(f'DENOMINATOR: {len(paths)} markdown file(s) under schemas/ globbed, {read} read, {signed} carrying at least one TEAM-SIGN-OFF line')
    if read == 0:
        print("NOTHING WAS READ -- the glob matched no files. This is a failure, "
              "not a pass.")
        return 1
    print()

    # RULE 2: the same lie in the tool source.
    awaiting, total = families_awaiting_signature()
    tool_rows, tool_files = [], 0
    if awaiting is None:
        print("V_eta_decisions.json is unreadable -- the tool-source rule could "
              "not run. That is a failure, not a pass.")
        return 1
    print(f'DECISIONS ARTIFACT: {total} family/families, {awaiting} awaiting a signature')
    if awaiting == 0:
        tool_rows, tool_files = scan_tools_for_unsigned_claims()
        print(f'TOOL SOURCE: {tool_files} .py file(s) under tools/ scanned for "no signature yet"')
    else:
        print(f'TOOL SOURCE: not scanned -- {awaiting} family/families really are awaiting a signature, so the claim may be true somewhere.')

    # RULE 3: a build claim in a signature's tail.
    build_rows, build_claims = scan_signoff_build_claims(paths)
    print(f'SIGNATURE BUILD CLAIMS: {build_claims} TEAM-SIGN-OFF line(s) assert NOT (YET) BUILT; {len(build_rows)} carry no adjacent {BUILD_STATE} note')
    print()

    if not rows and not tool_rows and not build_rows:
        print(f'No signed plan document claims to be unsigned. ({signed} checked)')
        if awaiting == 0:
            print("No tool source claims a family is awaiting a signature.")
        print(f'Every signature build claim carries a {BUILD_STATE} note. ({build_claims} checked)')
        return 0

    if rows:
        print("STALE HEADERS -- these documents carry a TEAM-SIGN-OFF line AND "
              "assert that they do not:")
        for path, lineno, text in rows:
            print(f'  {os.path.relpath(path, REPO)}:{lineno}')
            print(f"      {text}")
        print()
    if tool_rows:
        print("STALE TOOL SOURCE -- every family is signed, but these lines say "
              "otherwise:")
        for path, lineno, text in tool_rows:
            print(f'  {os.path.relpath(path, REPO)}:{lineno}')
            print(f"      {text}")
        print()
    if build_rows:
        print("SIGNATURE BUILD CLAIM WITH NO ADJACENT NOTE -- these signatures "
              "assert a build state and nothing keeps that assertion current:")
        for path, lineno, text in build_rows:
            print(f'  {os.path.relpath(path, REPO)}:{lineno}')
            print(f"      {text}")
        print()
        print(f"FIX: add a dated `{BUILD_STATE}` line within "
              f"{BUILD_WINDOW_AFTER} lines BELOW the signature, with the command "
              "output that establishes the current state.")
        print("     DO NOT EDIT THE SIGNATURE LINE -- Operating Rule 4. The note "
              "goes beside it; what the team signed is not rewritten.")
        print()
    print("FIX: point the claim at the signature that exists, and mark any quoted")
    print(f"     historical wording with {EXEMPT}.")
    return 1 if args.enforce else 0


if __name__ == "__main__":
    sys.exit(main())
