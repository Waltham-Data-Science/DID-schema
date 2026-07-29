#!/usr/bin/env python3
"""Phase 1.3 of V_eta_ground_truth_plan.md -- do the migrators speak the real
did_v1 vocabulary?

Compares every `+migrators_j` migrator's field reads against the NDI templates
captured in `V_eta_ndi_ground_truth.json`, and reports names that appear in
DID-schema's own `V_alpha` snapshot but in NO NDI template. Those are names the
migrator can only have picked up from the snapshot, and a migrator reading a
field the source document does not have emits an empty-but-valid document that
no existing gate can see.

REPORT-ONLY BY DEFAULT (exit 0). Phase 1 lands report-only across the board: the
census has to come first, because turning this red before any migrator is fixed
just blocks the pipeline. Pass --enforce to exit non-zero -- that is the Phase 2
end state, once the confirmed list is empty.

  python3 tools/check_migrator_vocabulary.py            # report, exit 0
  python3 tools/check_migrator_vocabulary.py --enforce  # exit 1 if any confirmed

Regenerate the ground truth first with tools/ndi_ground_truth.py.
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
GT = os.path.join(REPO, "schemas", "V_eta_ndi_ground_truth.json")

# Confirmed by reading the template AND the writer, so they are expected here
# until Phase 2 fixes them. Listing them keeps the report honest about what is
# known-broken versus newly appeared: a name showing up outside this set is a
# REGRESSION, and that is what --enforce should eventually catch first.
KNOWN_BROKEN = {
    "probe_geometry.m",       # none of channel_positions/position_units/probe_type exists
    "ontology_image.m",       # legacy path is dead code (Phase 0: DID-INVENTED)
    "ontology_label.m",       # ontologyLabel has only ever been {ontologyNode}
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--enforce", action="store_true",
                    help="exit non-zero when a confirmed offender is present "
                         "(Phase 2 end state; NOT the Phase 1 default)")
    a = ap.parse_args()

    if not os.path.exists(GT):
        sys.exit("missing %s -- run tools/ndi_ground_truth.py first"
                 % os.path.relpath(GT, REPO))
    gt = json.load(open(GT))
    reads = gt.get("migrator_reads", [])

    confirmed = [r for r in reads if r["confidence"] == "confirmed-vocabulary"]
    possible = [r for r in reads if r["confidence"] != "confirmed-vocabulary"]
    new = [r for r in confirmed if r["migrator"] not in KNOWN_BROKEN]

    print("migrator vocabulary check  (ground truth: NDI %s, %d classes)"
          % (gt.get("ndi_ref", "?"), gt["summary"]["ndi_classes"]))
    print()
    print("  reads invented names via an explicit idiom : %d" % len(confirmed))
    print("  mentions invented names only               : %d" % len(possible))
    print("  NOT on the known-broken list (regressions) : %d" % len(new))
    print()

    if confirmed:
        print("READS invented vocabulary (confirm each against template + writer):")
        for r in confirmed:
            mark = "NEW " if r["migrator"] not in KNOWN_BROKEN else "    "
            print("  %s%-34s %s" % (mark, r["migrator"],
                                    r["reads_names_absent_from_template"]))
        print()
    if possible:
        print("MENTIONS invented vocabulary (may be a comment -- verify by hand):")
        for r in possible:
            print("      %-34s %s" % (r["migrator"],
                                      r["mentions_names_absent_from_template"]))
        print()

    if a.enforce and confirmed:
        print("FAIL (--enforce): %d migrator(s) still read invented vocabulary."
              % len(confirmed))
        return 1

    print("REPORT ONLY -- not failing. Phase 1 is a census; enforcement is Phase 2.")
    if new:
        print("NOTE: %d migrator(s) are NOT on the known-broken list. A name "
              "appearing outside that set is a regression and wants a look now."
              % len(new))
    return 0


if __name__ == "__main__":
    sys.exit(main())
