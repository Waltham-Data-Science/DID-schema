#!/usr/bin/env python3
"""Generate schemas/V_eta_STATUS.md -- the single generated record of V_eta state.

WHY THIS EXISTS
---------------
V_eta state lives in 27 plan documents, a 400-line CLAUDE.md and a 52-item task
list, and no two agree. Prose cannot be checked, so it rots and is then cited:
"no session document exists anywhere", "all 0-usage, safe to delete",
"dissolved (rename/decompose)" -- each was a written claim that was wrong and
that nothing could catch.

This file replaces PROSE STATE with DERIVED STATE. The plan documents keep the
rationale (why a model was chosen -- what prose is genuinely good for); this
board owns the answer to "how much is left, and what exactly".

THE ONE PIECE OF JUDGEMENT, MADE EXPLICIT
-----------------------------------------
`FAMILIES` below groups the still-open classes into decision units. That mapping
is a human call and cannot be derived, so it is written here in the open rather
than implied across a dozen documents. It is CHECKED: every in_progress class
must belong to exactly one family, and the generator FAILS if a class appears
that no family claims. A new open class can therefore never be silently dropped
from the count -- the failure this project has hit four separate times.

Usage:  python3 tools/status_board.py [--check]
        --check exits non-zero if the committed board is out of date.
"""

import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(REPO, "schemas", "V_eta", "index.json")
LEDGER = os.path.join(REPO, "schemas", "V_eta_coverage_ledger.json")
OUT = os.path.join(REPO, "schemas", "V_eta_STATUS.md")

# Decision families for the still-open (in_progress) classes.
#   name -> (member classes, plan document or None, one-line statement of the call)
# `plan` names a file under schemas/ that RECORDS A DECISION. A family with a
# plan is DECIDED-BUT-UNBUILT: the model is settled, the schema has not changed.
# A family with plan=None is genuinely UNDECIDED and is what closing V_eta means.
FAMILIES = [
    ("time_reference", [
        "time_reference", "session_bounded_reference", "session_relative_reference",
        "epoch_bounded_reference", "epoch_relative_reference",
        "event_bounded_reference", "event_relative_reference", "utc_reference"],
     "V_eta_time_reference_model_plan.md",
     "8 classes collapse to absolute_reference + relative_reference"),

    ("stimulus", ["stimulus_presentation"],
     "V_eta_stimulus_model_plan.md",
     "timed_sequence data_type + timed_sequence_manipulation leaf"),

    ("ensemble", ["ensemble"],
     "V_eta_ensemble_plan.md",
     "group subject + epoch-scoped member_of edges + rebuildable cache"),

    ("image / ngrid", ["ngrid"],
     "V_eta_image_model_plan.md",
     "ngrid phases into sampled_body; image is a standalone data_type"),

    ("acquisition epoch", ["acquisition_epoch", "epochid", "epochfiles_ingested"],
     None,
     "epoch header contents + whether clocks dissolve into time_references"),

    ("daq ingestion", [
        "daqreader", "daqreader_epochdata_ingested",
        "daqreader_image_epochdata_ingested", "daqmetadatareader",
        "daqmetadatareader_epochdata_ingested", "daqsystem",
        "dataseries_channel_map"],
     None,
     "do the ingested-cache classes persist, fold, or become opaque_body"),

    ("sync", ["syncgraph", "syncrule", "syncrule_mapping"],
     None,
     "is the sync graph V_eta data or NDI runtime state"),

    ("file navigation", ["filenavigator", "directory", "filter"],
     None,
     "do path/navigation classes belong in an archival schema at all"),

    ("openMINDS", ["openminds_import"],
     None,
     "import provenance vs crosswalk; entangled with the openminds_* sources"),

    ("software", ["app"],
     None,
     "app -> software rename landed; dedup + openMINDS crosswalk outstanding"),

    ("misc singletons", [
        "binaryseries_parameters", "control_designation", "interaction_purpose",
        "projectvar"],
     None,
     "four unrelated classes, each its own small call"),

    ("demo / mock", ["demo_ndi", "demo_ndi_mock"],
     None,
     "test fixtures; decide whether they ship in the set"),
]


def load():
    with open(INDEX) as fh:
        idx = json.load(fh)
    with open(LEDGER) as fh:
        led = json.load(fh)
    return idx["schemas"], led["rows"]


def build():
    schemas, rows = load()
    by_disp = {}
    for s in schemas:
        by_disp.setdefault(s.get("disposition", "(none)"), []).append(s["class_name"])
    open_classes = set(by_disp.get("in_progress", []))

    # THE CHECK: every open class must be claimed by exactly one family.
    claimed, dupes = set(), []
    for _, members, _, _ in FAMILIES:
        for m in members:
            if m in claimed:
                dupes.append(m)
            claimed.add(m)
    unclaimed = sorted(open_classes - claimed)
    stale = sorted(claimed - open_classes)

    # A family may only claim to be DECIDED if the document recording that
    # decision exists. Otherwise "decided, awaiting build" is the same kind of
    # unbacked assertion this board replaces.
    missing_plans = [(n, pl) for n, _, pl, _ in FAMILIES
                     if pl and not os.path.exists(os.path.join(REPO, "schemas", pl))]

    L = []
    p = L.append
    p("# V_eta status board (GENERATED -- do not hand-edit)")
    p("")
    p("Regenerate with `python3 tools/status_board.py`. CI runs `--check`.")
    p("")
    p("State lives here. The plan documents under `schemas/` keep the RATIONALE")
    p("for each model; this board owns *how much is left and what exactly*.")
    p("")

    if unclaimed:
        p("## ERROR -- unclaimed open classes")
        p("")
        p("These are `in_progress` but belong to no decision family in")
        p("`tools/status_board.py`. An open class that no family claims is an open")
        p("question nobody is tracking. Add it to `FAMILIES` before continuing:")
        p("")
        for c in unclaimed:
            p("- `%s`" % c)
        p("")

    total = len(schemas)
    n_open = len(open_classes)
    n_persist = len(by_disp.get("persist", []))
    n_retire = len(by_disp.get("retire", []))
    # Index 2 is the plan document; index 1 is the member LIST, which is always
    # truthy. Getting this wrong reported every family as decided and printed an
    # empty "genuinely undecided" table -- a status board that says the work is
    # done is worse than no status board.
    decided = [f for f in FAMILIES if f[2]]
    undecided = [f for f in FAMILIES if not f[2]]

    p("## Where V_eta stands")
    p("")
    p("| | count |")
    p("|---|---|")
    p("| target classes | %d |" % total)
    p("| settled (persist) | %d |" % n_persist)
    p("| settled (retire) | %d |" % n_retire)
    p("| **still open** | **%d** |" % n_open)
    p("| open **decision families** | **%d** |" % len(FAMILIES))
    p("| &nbsp;&nbsp;of which decided, awaiting build | %d |" % len(decided))
    p("| &nbsp;&nbsp;of which genuinely undecided | %d |" % len(undecided))
    p("")
    p("The class count is not the work count. %d open classes are %d decisions, "
      "because most open classes move as a family." % (n_open, len(FAMILIES)))
    p("")

    p("## Genuinely undecided -- this is what closing V_eta means")
    p("")
    p("| family | classes | the call to make |")
    p("|---|---|---|")
    for name, members, _, question in undecided:
        p("| **%s** | %d | %s |" % (name, len(members), question))
    p("")
    for name, members, _, _ in undecided:
        p("- **%s**: %s" % (name, ", ".join("`%s`" % m for m in sorted(members))))
    p("")

    p("## Decided, awaiting build")
    p("")
    p("The model is settled and recorded; the schema has not changed yet. Every")
    p("one of these re-targets migrators that are already written, which is why")
    p("migrator work before the target closes is rework.")
    p("")
    p("| family | classes | decision | recorded in |")
    p("|---|---|---|---|")
    for name, members, plan, what in decided:
        p("| **%s** | %d | %s | `%s` |" % (name, len(members), what, plan))
    p("")

    # v1 source side
    led_disp = {}
    for r in rows:
        led_disp.setdefault(r["disposition"], []).append(r["v1_class"])
    unverified = sorted(led_disp.get("no V_eta home, no migrator -- UNVERIFIED", []))
    p("## v1 source side (from the coverage ledger)")
    p("")
    p("| disposition | count |")
    p("|---|---|")
    for k in sorted(led_disp, key=lambda k: -len(led_disp[k])):
        p("| %s | %d |" % (k, len(led_disp[k])))
    p("")
    if unverified:
        p("**UNVERIFIED** -- no V_eta home, no migrator, fate never established. "
          "These strand today:")
        p("")
        for c in unverified:
            p("- `%s`" % c)
        p("")

    if stale:
        p("## Families naming classes that are no longer open")
        p("")
        p("Settled or removed since the family was written -- prune from `FAMILIES`:")
        p("")
        for c in stale:
            p("- `%s`" % c)
        p("")
    if dupes:
        p("## ERROR -- classes claimed by more than one family")
        p("")
        for c in sorted(set(dupes)):
            p("- `%s`" % c)
        p("")

    if missing_plans:
        p("## ERROR -- families claiming a decision document that does not exist")
        p("")
        for n, pl in missing_plans:
            p("- **%s** -> `schemas/%s` (missing)" % (n, pl))
        p("")

    ok = not unclaimed and not dupes and not missing_plans
    return "\n".join(L) + "\n", ok


def main(argv):
    text, ok = build()
    if "--check" in argv:
        current = open(OUT).read() if os.path.exists(OUT) else ""
        if current != text:
            print("V_eta_STATUS.md is STALE. Run: python3 tools/status_board.py")
            return 1
        if not ok:
            print("Status board reports unclaimed or duplicated open classes.")
            return 1
        print("V_eta_STATUS.md is current.")
        return 0
    with open(OUT, "w") as fh:
        fh.write(text)
    print("wrote %s" % os.path.relpath(OUT, REPO))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
