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
    # Each verdict below was reached by reading the NDI template AND the writer,
    # not by trusting this tool. Two distinct failure modes turned up:
    #
    #   HOLLOW    -- the migrator emits a document with blank content
    #                (did2.validate.silentLoss counts these)
    #   PASSTHROUGH -- the read finds nothing, so the migrator falls to its
    #                "carry unchanged" branch and the document is NEVER MIGRATED.
    #                silentLoss CANNOT see this one: the carried document is a
    #                perfectly valid v1-class document. It is camouflaged because
    #                the codebase has *intentional* passthroughs too, so an
    #                accidental one looks exactly like a deliberate deferral.
    "probe_geometry.m",
    #   PASSTHROUGH. Reads channel_positions/position_units/probe_type; the real
    #   template has site_locations_{leftright,frontback,depth}, unit, probe_model,
    #   manufacturer, contact_shape*, contour_*. Not one name overlaps.
    "electrode_offset_voltage.m",
    #   PASSTHROUGH. Reads offset_voltages; the real field is `offset`. Also reads
    #   voltage_units, which does not exist (template has offset, temperature), so
    #   units are lost even once the value is found.
    "site2channelmap.m",
    #   PASSTHROUGH. Reads num_sites; the real template has only `map`.
    "spike_interface_sorting_outputs.m",
    #   PASSTHROUGH. Reads num_units; the real template has sample_rate,
    #   sorter_name, unit -- the count presumably comes from numel(unit).
    "ontology_image.m",
    #   HOLLOW (fixed) -- legacy path is dead code, Phase 0 says DID-INVENTED.
    "ontology_label.m",
    #   ontologyLabel has only ever been {ontologyNode}. The migrator prefers the
    #   real ontology_node idiom, so it WORKS; the invented branch is dead code.
    "daqreader_ndr.m",
    #   BENIGN. Reads the real ndr_reader_string correctly; the file_extension
    #   branch is guarded by isfield and simply never fires. Dead, not lossy.
    #
    # ---- confirmed in the second pass (broadened detection) ----------------
    # These read through local getField/getCharField helpers, which the first
    # pattern missed. All are genuine code reads -- none is a comment or a write.
    # A THIRD failure mode shows up here, alongside HOLLOW and PASSTHROUGH:
    #   FRAGMENT -- the read fails, the payload is skipped, and the migrator
    #              emits only its side documents (e.g. a lone session anchor).
    "simple_calc.m",
    #   FRAGMENT, and the worst of the eight. Reads result_value/result_units;
    #   the real template has `answer` and `input_parameters`. When the value is
    #   not numeric it emits ONLY the anchor -- the calculated result is dropped
    #   entirely and a stray time-reference document is all that lands.
    "fitcurve.m",
    #   HOLLOW. Reads fit_function + goodness_of_fit; the real template has
    #   fit_equation, fit_sse, fit_name, fit_parameters, fit_constraints. Looks
    #   like a straight rename (fit_function->fit_equation, goodness->fit_sse).
    "vmspikefit.m",
    #   HOLLOW. Same shape as fitcurve: reads fit_function + r_squared against a
    #   template of fit_equation, fit_sse, fit_sse_perpoint, fit_parameters.
    "binnedspikeratevm.m",
    #   HOLLOW. Reads bin_size + num_bins; the real template has exactbintime,
    #   timepoints, firingrate_observations, voltage_observations, stimids,
    #   parameters. The actual binned data is in fields it never looks at.
    "spike_clusters.m",
    #   HOLLOW. Reads num_spikes; the real template has clusterinfo, epoch_info,
    #   waveform_sample_times.
    "vmneuralresponseresiduals.m",
    #   HOLLOW. Reads mean_residual; the real template has residual_power,
    #   total_power and goodness_of_fit -- the residual is derivable from those,
    #   but the field read does not exist.
    "spikewaves.m",
    #   PARTIAL. Reads the REAL extraction_name plus invented num_spikes and
    #   samples_per_spike, which default to 0. The document lands; the counts
    #   are silently zeroed.
    "subject_group.m",
    #   COSMETIC. The NDI template block is literally {} and no writer sets any
    #   field -- grouping is carried entirely by numbered subject_id depends_on
    #   edges, which this migrator reads correctly. Only the group's name and
    #   description are lost, so structure survives and labels degrade.
}

# Phase 2 outcome: these migrators no longer CONSUME an invented name -- the only
# place the name still appears is a guard that REJECTS a body carrying it, so a
# fixture or caller built against the V_alpha snapshot fails loudly instead of
# migrating silently. The detector cannot tell a guard from a read (both are
# `isfield(blk, 'name')`), so the distinction has to be recorded here.
#
# Keeping these visible rather than deleting them is deliberate: a guard removed
# by a later edit should show up as a regression, not vanish quietly.
RESOLVED_BY_GUARD = {
    "ontology_image.m":                 "vintage split; current NDI shape passes through",
    "probe_geometry.m":                 "one length_observation per real site-location axis",
    "electrode_offset_voltage.m":       "reads the real scalar offset + temperature",
    "simple_calc.m":                    "guarded passthrough -- no subject-bearing edge",
    "spike_clusters.m":                 "guarded passthrough -- count is in spike_cluster.bin",
    "spikewaves.m":                     "guarded passthrough -- counts are in the .vsw header",
    "spike_interface_sorting_outputs.m": "guarded passthrough -- class declares no dependencies",
    "site2channelmap.m":                "guarded passthrough -- `map` needs the probe_geometry join",
    "binnedspikeratevm.m":              "guarded passthrough -- no writer exists in any repository",
    "vmneuralresponseresiduals.m":      "guarded passthrough -- no writer; goodness_of_fit unspecified",
    "ontology_label.m":                 "guarded passthrough -- referent needs the migrated-id graph",
    "vmspikesummary.m":                 "guarded passthrough -- real class is a spike WAVEFORM + shape medians",
}

# A blind spot this tool structurally cannot cover, recorded so it is not
# mistaken for a clean bill: a class with NO migrator never appears here at all,
# because there is no source file to scan. `vmspikefilteringparameters` was
# exactly that -- no migrator, so it passed through by default into a tombstone
# declaring `filter_type`/`filter_window`, neither of which exists. It was found
# by reading the app's templates, not by any check. Coverage of unmigrated
# passthrough classes belongs to tools/coverage.py, not to this one.

# Also fixed, but WITHOUT a guard, so they correctly disappear from the report
# entirely. Recorded here only so the two resolution routes are both visible:
#   fitcurve.m, vmspikefit.m -- the invented fit_function/goodness_of_fit/
#   r_squared reads were replaced outright by the real fit_equation + fit_sse.
#   No guard was added because a fit-quality field is not a shape a caller could
#   plausibly synthesise; the rename is the whole repair. (fit_sse is unbounded,
#   in units squared, and LOWER is better, so it is reported as a residual --
#   writing it as an r-squared would have inverted every downstream comparison.)


# VERIFIED BENIGN -- reads an invented name, but nothing is lost, and the
# evidence says so. `--enforce` does NOT fail on these.
#
# THIS IS NOT AN ESCAPE HATCH, and it must not become one. Every entry states
# (a) why the read is harmless and (b) WHAT WOULD MAKE IT STOP BEING HARMLESS,
# so a later reader can re-check instead of trusting the label -- the exact
# mistake that let `ontology_label` sit graded as benign while discarding the
# only edge to the thing it labelled.
#
# The bar: the read must be an ADDITIONAL, guarded read with a correct fallback,
# never a wrong read standing in for a right one. A migrator that reads the
# wrong name INSTEAD of the real one belongs in KNOWN_BROKEN and gets fixed.
VERIFIED_BENIGN = {
    "daqreader_ndr.m": (
        "`file_extension` is an isfield-guarded EXTRA carry alongside the real "
        "`ndr_reader_string`, which IS read correctly. The branch never fires "
        "on an origin/main document. Kept rather than deleted so an older "
        "corpus vintage carrying the field would still have it carried. "
        "STOPS BEING BENIGN IF: the real read (`ndr_reader_string`) is ever "
        "removed or renamed, leaving this as the only read."),
    "subject_group.m": (
        "`group_name`/`description` are isfield-guarded reads of a block NDI "
        "ships as literally `{}` -- all three writers construct subject_group "
        "with no property arguments at all -- and both fall back correctly "
        "(groupName via jEnsureLocalId, desc to ''). Nothing is lost because "
        "there is nothing there. NOTE the fallback means every migrated group "
        "satisfies a field documented 'Human-facing handle... REQUIRED' with a "
        "raw UUID (~353x); that is a quality-floor issue, not vocabulary loss. "
        "STOPS BEING BENIGN IF: NDI populates the subject_group block, at "
        "which point these become real reads and the fallback would mask them."),
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

    hits = [r for r in reads if r["confidence"] == "confirmed-vocabulary"]
    possible = [r for r in reads if r["confidence"] != "confirmed-vocabulary"]
    # A guarded migrator still MENTIONS the invented name -- in the isfield that
    # rejects it. That is the opposite of the defect, so it is not an offender.
    guarded = [r for r in hits if r["migrator"] in RESOLVED_BY_GUARD]
    benign = [r for r in hits if r["migrator"] in VERIFIED_BENIGN
              and r["migrator"] not in RESOLVED_BY_GUARD]
    confirmed = [r for r in hits if r["migrator"] not in RESOLVED_BY_GUARD
                 and r["migrator"] not in VERIFIED_BENIGN]
    new = [r for r in confirmed if r["migrator"] not in KNOWN_BROKEN]
    # An allow-listed migrator that no longer reads the name has been fixed or
    # rewritten. Say so, so the entry can be retired instead of lingering.
    stale_benign = sorted(set(VERIFIED_BENIGN)
                          - {r["migrator"] for r in hits})
    missing_guard = sorted(set(RESOLVED_BY_GUARD)
                           - {r["migrator"] for r in hits})

    print("migrator vocabulary check  (ground truth: NDI %s, %d classes)"
          % (gt.get("ndi_ref", "?"), gt["summary"]["ndi_classes"]))
    print()
    print("  still CONSUME invented names               : %d" % len(confirmed))
    print("  verified benign (allow-listed, with reason) : %d" % len(benign))
    print("  name present only in a rejection guard     : %d" % len(guarded))
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
    if guarded:
        print("GUARDED (fixed -- the name survives only to be rejected):")
        for r in sorted(guarded, key=lambda x: x["migrator"]):
            print("      %-34s %s" % (r["migrator"],
                                      RESOLVED_BY_GUARD[r["migrator"]]))
        print()
    if benign:
        print("VERIFIED BENIGN (allow-listed -- read is harmless, reason recorded):")
        for r in sorted(benign, key=lambda x: x["migrator"]):
            print("      %-34s %s" % (r["migrator"],
                                      r["reads_names_absent_from_template"]))
            print("          %s" % VERIFIED_BENIGN[r["migrator"]])
        print()
    if stale_benign:
        print("ALLOW-LIST STALE -- listed as verified benign, but the name is "
              "no longer read at all. The migrator was fixed; retire the entry:")
        for m in stale_benign:
            print("      %s" % m)
        print()
    if possible:
        print("MENTIONS invented vocabulary (may be a comment -- verify by hand):")
        for r in possible:
            print("      %-34s %s" % (r["migrator"],
                                      r["mentions_names_absent_from_template"]))
        print()
    if missing_guard:
        print("GUARD GONE -- listed as resolved, but the invented name is no "
              "longer present at all. Either the guard was dropped (a "
              "regression: the V_alpha shape would now migrate silently) or the "
              "entry is stale:")
        for m in missing_guard:
            print("      %s" % m)
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
