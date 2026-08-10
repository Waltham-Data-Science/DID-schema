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

# "NO `TEAM-SIGN-OFF` LINE", "no TEAM-SIGN-OFF line", "NO TEAM SIGN-OFF LINE".
NO_SIGNOFF_RE = re.compile(r"\bno\s+`?team[\s_-]*sign[\s_-]*off`?\s+line\b", re.I)
HAS_SIGNOFF_RE = re.compile(r"^TEAM-SIGN-OFF\b")
EXEMPT = "HISTORICAL-SIGNOFF-CLAIM"


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
            rows.append((path, 0, "UNREADABLE: %s" % exc))
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
    print("DENOMINATOR: %d markdown file(s) under schemas/ globbed, %d read, "
          "%d carrying at least one TEAM-SIGN-OFF line" % (len(paths), read, signed))
    if read == 0:
        print("NOTHING WAS READ -- the glob matched no files. This is a failure, "
              "not a pass.")
        return 1
    print()

    if not rows:
        print("No signed plan document claims to be unsigned. (%d checked)" % signed)
        return 0

    print("STALE HEADERS -- these documents carry a TEAM-SIGN-OFF line AND assert "
          "that they do not:")
    for path, lineno, text in rows:
        print("  %s:%d" % (os.path.relpath(path, REPO), lineno))
        print("      %s" % text)
    print()
    print("FIX: update the header to point at the signature, and mark any quoted")
    print("     historical wording with %s." % EXEMPT)
    return 1 if args.enforce else 0


if __name__ == "__main__":
    sys.exit(main())
