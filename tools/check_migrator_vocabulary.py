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
