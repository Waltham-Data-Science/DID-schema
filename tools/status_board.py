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
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(REPO, "schemas", "V_eta", "index.json")
LEDGER = os.path.join(REPO, "schemas", "V_eta_coverage_ledger.json")
OUT = os.path.join(REPO, "schemas", "V_eta_STATUS.md")

# Decision families for the still-open (in_progress) classes.
#   name -> (members, plan-or-None, one-line call, status)
#
# STATUS IS THREE-VALUED, and the distinction is the point:
#
#   "team"     DECIDED BY THE TEAM in a walkthrough. Only RENDERS as decided if
#              the cited plan document carries a TEAM-SIGN-OFF line (see SIGNOFF
#              below); without one it renders as "awaiting signature" -- Claude
#              cannot promote its own work to a decision.
#   "proposed" WRITTEN UP BY CLAUDE ALONE, nobody has checked the reasoning.
#              NOT a decision and must never be counted as one.
#   "open"     nobody has proposed anything yet.
#
# "team without a signature" and "Claude wrote this alone" were one bucket until
# the team pointed out they are different states: one needs a signature, the
# other needs someone to check the reasoning. Rendered separately now.
#
# An earlier version had only two states, so attaching a document to a family
# silently promoted it to "decided" -- and five families Claude wrote up alone
# were reported to the team as settled. A status board that launders a proposal
# into a decision is worse than no board.
FAMILIES = [
    ("time_reference", [
        "time_reference", "session_bounded_reference", "session_relative_reference",
        "epoch_bounded_reference", "epoch_relative_reference",
        "event_bounded_reference", "event_relative_reference", "utc_reference"],
     "V_eta_time_reference_model_plan.md",
     "8 classes collapse to absolute_reference + relative_reference",
     "team"),

    ("stimulus", ["stimulus_presentation"],
     "V_eta_stimulus_model_plan.md",
     "timed_sequence data_type + timed_sequence_manipulation leaf",
     "team"),

    ("ensemble", ["ensemble"],
     "V_eta_ensemble_plan.md",
     "group subject + epoch-scoped member_of edges + rebuildable cache",
     "team"),

    ("image / ngrid", ["ngrid"],
     "V_eta_image_model_plan.md",
     "ngrid phases into sampled_body; image is a standalone data_type",
     "team"),

    # DECIDED with the team 2026-08-05 ("I agree with B"), no signature yet.
    # epochid turned out NOT to be a disposal question: it is the JOIN MECHANISM
    # for the epoch-scoped half of the database -- 15 NDI classes carry the mixin
    # and 11+ live sites match epochid.epochid by exact_string. Third time this
    # session a depends_on sweep missed string-match references.
    ("epoch", ["acquisition_epoch", "epochid", "epochfiles_ingested"],
     "V_eta_epoch_plan.md",
     "MINT `epoch` ENTITY; element_epoch dissolves; epochid DROPPED; probemap -> edges (B)",
     "team"),

    # Split by the templates, not by the name prefix: three are a MATLAB class
    # name (configuration), three carry real epoch data or bytes, and one is not
    # on origin/main at all.
    # DECIDED with the team 2026-08-05, no signature yet. The earlier "not
    # archival" proposal was WRONG and is reversed in place: daqsystem.base.name
    # is a join key referenced BY NAME (epochprobemap devicestring, syncrule
    # parameters), which a depends_on check cannot see.
    ("daq configuration", ["daqsystem", "daqreader", "daqmetadatareader"],
     "V_eta_daq_family_decisions.md",
     "acquisition_system + metadata_reader keep ids; class names fold to software entities",
     "team"),

    ("daq ingested payloads", [
        "daqreader_epochdata_ingested",
        "daqmetadatareader_epochdata_ingested",
        "daqreader_image_epochdata_ingested"],
     "V_eta_daq_family_decisions.md",
     "-> relative_reference / opaque_body / image model; no new class",
     "proposed"),

    # DECIDED 2026-08-05. Writer check done: absent from NDI origin/main, zero code
    # mentions, provenance V_epsilon, zero migrators, zero schema references.
    ("dataseries_channel_map", ["dataseries_channel_map"],
     "V_eta_go_forward_class_audit.md",
     "DELETE -- a V_epsilon invention, never a did_v1 source, zero users", "team"),

    # The templates split this: syncgraph/syncrule are a MATLAB class name plus
    # parameters (runtime configuration), while syncrule_mapping carries the
    # COMPUTED epoch-to-epoch clock relationship -- real data, and the shape the
    # time model already covers.
    # DECIDED with the team 2026-08-05, no signature yet. The earlier "not
    # archival" proposal was WRONG the same way the daq one was: syncrule_mapping
    # references BOTH syncgraph_id and syncrule_id by edge, so dissolving either
    # dangles it. A live query (syncgraph.m:404-408) also reads fields V_eta has
    # already dropped -- see TaskList #58.
    ("sync configuration", ["syncgraph", "syncrule"],
     "V_eta_infra_family_decisions.md",
     "PERSIST as infra, ids preserved; class names fold to software entities",
     "team"),

    # NOT DECIDED. Claude marked this "team" on 2026-08-05 after a walkthrough;
    # the team corrected that -- they read the options and did not adopt one.
    # What IS established is negative and evidence-backed: the old "folds into
    # relative_reference" claim FAILS (two referents / two frames / an affine
    # transform is not a position on a timeline). clock_alignment is a PROPOSAL.
    ("sync mapping", ["syncrule_mapping"],
     "V_eta_infra_family_decisions.md",
     "clock_alignment PROPOSED (relation tier); the relative_reference fold is disproven",
     "proposed"),

    # `filter` was grouped here by a guess at its name. It is data/filter.json --
    # label/type/algorithm/parameters, a signal-processing description -- and
    # belongs with software/method, not with file paths.
    # SPLIT: filenavigator is DECIDED (-> file_navigator, id preserved, patterns
    # parsed into declared fields; see V_eta_daq_family_decisions.md). `directory`
    # is ABSENT from NDI origin/main and needs a writer check, not a disposition.
    # Status stays "open" because the family is not fully resolved -- the
    # inaccuracy is deliberately in the under-reporting direction.
    # CLOSED 2026-08-05. filenavigator was decided with the daq family; `directory`
    # is NOT a did_v1 source (provenance V_gamma, and CLAUDE.md already lists it as a
    # post-v1 DID class) -- it landed here by name association, the same mis-grouping
    # that once put `filter` in this family.
    ("file navigation", ["filenavigator", "directory"],
     "V_eta_daq_family_decisions.md",
     "filenavigator -> file_navigator (id preserved); `directory` is not a source",
     "team"),

    # openminds_import was REMOVED 2026-07-30 (team sign-off) -- nothing ever
    # emitted it. What is left is the v1 `openminds` carrier: the UNATTACHED
    # openMINDS objects, 8 documents, of which 3 are composite core.research.Strain.
    # SIGNED OFF 2026-08-05: strain is an entity with a repeatable
    # global_identifier + a recursive background_strain_# self-edge; strain_id is
    # an optional edge on term_assertion. Build deferred, TaskList #56. The
    # signature was TRANSCRIBED by Claude on explicit instruction -- see the note
    # at the top of the record before trusting it.
    ("openMINDS", ["openminds"],
     "V_eta_openminds_family_record.md",
     "strain -> entity + recursive background_strain_#; strain_id on term_assertion",
     "team"),

    # Split: the two classes have separate decisions and separate documents.
    ("software", ["app"],
     "V_eta_tenet_audit.md",
     "app -> software entity + software_id edge + execution_environment (R1)",
     "team"),

    ("frequency_filter", ["filter"],
     "V_eta_frequency_filter_model_plan.md",
     "referenced document (not entity); band edges; typed gain fields; no sample_rate",
     "team"),

    # ---- families for the `retire, but nothing decided` rows -------------------
    # These were invisible while the board counted only in_progress. Grouped by
    # what the TEMPLATES contain, not by name prefix -- the mistake that put
    # `filter` under file navigation and split the sync family wrongly.

    # All four are algorithm configuration for spike processing, all inherit `app`,
    # and THREE carry filter parameters of their own:
    #   spike_extraction_parameters(_modification): filter_type/low/high/order/ripple
    #   vmspikefilteringparameters:                 filter_algorithm, filter_algorithm_
    #                                               parameters, rm60Hz (a 60 Hz notch)
    # So v1 has a THIRD filter representation here, and this family cannot be
    # decided without the frequency_filter model it should reference.
    # vmspikefilteringparameters also mixes in `spiketimes` -- OUTPUT data sitting in
    # a parameters class.
    # DECIDED with the team 2026-08-05 (option C), no signature yet. Four classes
    # collapse to ONE `method_parameters` document -- named for the inline field it
    # is the shared-cardinality form of. The canonical parts (filter, threshold,
    # waveform window, refractory period) get TYPED; the idiosyncratic remainder is
    # honestly a bag. The specific block list is PROPOSED, not decided.
    ("spike processing parameters", [
        "spike_extraction_parameters", "spike_extraction_parameters_modification",
        "sorting_parameters", "vmspikefilteringparameters"],
     "V_eta_method_parameters_plan.md",
     "4 -> 1 `method_parameters` (id+name preserved); canonical parts typed, rest a bag",
     "team"),

    # The stimulus DESCRIPTION: a single ontology-keyed property, and a whole table
    # flattened into one `string` field. Both hang off stimulus_element_id. Likely
    # folds with the stimulus model, and their tombstones are already held for it --
    # but the model plan does not currently decide them, so they are counted here
    # rather than assumed covered.
    ("stimulus parameters", ["stimulus_parameter", "stimulus_parameter_table"],
     None,
     "stimulus description; likely folds with the stimulus model but not yet decided",
     "open"),

    # NOT the same thing as stimulus parameters: this is the MEASURED RESPONSE to a
    # presented stimulus -- stimulus_response carries element_id + stimulator_id +
    # presentation_id + control_id. It is the observation tier, and it is the input
    # the tuning calculators consumed, so it is entangled with the (decided) tuning
    # model and the raw-recording model.
    ("stimulus response", [
        "stimulus_response", "stimulus_response_scalar",
        "stimulus_response_scalar_parameters",
        "stimulus_response_scalar_parameters_basic"],
     None,
     "measured response to a stimulus -- observation tier, feeds the tuning fold",
     "open"),

    # A live NDI class with four in-tree emitters, parallel to the newer
    # `measurement`. CLAUDE.md once recorded it as dissolved into `measurement`;
    # that was FALSE and is corrected. {measurement, value, datestamp} on a subject.
    # DECIDED 2026-08-05. A real did_v1 template whose shape IS a subject
    # observation. All four in-tree emitters are TEST-session builders -- see the
    # CLAUDE.md correction in the audit document.
    ("subject measurement", ["subjectmeasurement"],
     "V_eta_go_forward_class_audit.md",
     "route through the `measurement` fold -- no new model, reuse the existing path",
     "team"),

    ("misc singletons", [
        "binaryseries_parameters", "control_designation", "interaction_purpose",
        "projectvar"],
     None,
     "four unrelated classes, each its own small call", "open"),

    # DECIDED 2026-08-05. Absent from NDI, provenance V_gamma, and referenced by
    # NOTHING -- not even the test suite.
    ("demo / mock", ["demo_ndi", "demo_ndi_mock"],
     "V_eta_go_forward_class_audit.md",
     "DELETE -- DID-side fixtures that nothing references", "team"),
]


SIGNOFF = "TEAM-SIGN-OFF:"


def has_signoff(plan):
    """True when the plan document carries an explicit team sign-off line.

    THE RULE THIS ENFORCES. Claude may research a family and write up a
    proposal; it may not record that proposal as the team's decision. On
    2026-07-29 the board had only two states, so attaching a document to a
    family promoted it to "decided" -- five families Claude wrote up alone were
    reported to the team as settled, along with a remaining-work count built on
    them.

    A decision now requires a line the TEAM writes, in the plan document:

        TEAM-SIGN-OFF: <who/when> -- <what was decided>

    Absent that line the family is displayed as awaiting review, no matter what
    the FAMILIES table claims. This is deliberately not a CI failure: a false
    RED is as useless as a false GREEN, and the honest state is simply "not
    signed off yet".
    """
    if not plan:
        return False
    path = os.path.join(REPO, "schemas", plan)
    if not os.path.exists(path):
        return False
    with open(path) as fh:
        text = fh.read()

    # STRIP HTML COMMENTS FIRST. The first version of this check counted any line
    # starting with the marker -- including the <!-- ... --> block in a plan
    # document that TELLS the team how to sign off. Claude wrote that instruction,
    # so Claude's own document promoted itself to "decided": the exact laundering
    # this function exists to prevent, arriving through a different door. Caught
    # only because the count was verified instead of trusted.
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)

    for line in text.splitlines():
        line = line.lstrip()
        if not line.startswith(SIGNOFF):
            continue
        rest = line[len(SIGNOFF):].strip()
        # A placeholder is not a sign-off. Require real content and no angle-bracket
        # template slots.
        if "<" in rest or ">" in rest:
            continue
        if len(rest) < 10:
            continue
        return True
    return False


def load():
    with open(INDEX) as fh:
        idx = json.load(fh)
    with open(LEDGER) as fh:
        led = json.load(fh)
    return idx["schemas"], led["rows"]


def build():
    schemas, rows = load()

    # RETIRE IS NOT ALWAYS A DECISION. A row marked retire with NO migrator and NO
    # recorded `how` means the documents pass through untouched and nobody has
    # decided anything -- open work wearing a settled label. The board could not
    # see it because it counted only `in_progress`. Found when
    # spike_extraction_parameters turned out to hold filter_type / filter_low /
    # filter_high / filter_order / filter_ripple -- exactly the data the
    # frequency_filter model was just designed for -- while sitting outside every
    # decision family.
    #
    # Computed HERE, before anything renders: the first attempt built it down in
    # the ledger section and the header referenced it earlier in the same
    # function, which raised UnboundLocalError. A summary line must not depend on
    # a number computed after it.
    unplanned_retire = sorted(
        r["v1_class"] for r in rows
        if r["disposition"] == "retire" and not r["migrator"]
        and not (r.get("how") or "").strip())
    by_disp = {}
    for s in schemas:
        by_disp.setdefault(s.get("disposition", "(none)"), []).append(s["class_name"])
    open_classes = set(by_disp.get("in_progress", []))

    # THE CHECK: every open class must be claimed by exactly one family.
    claimed, dupes = set(), []
    for fam in FAMILIES:
        members = fam[1]
        for m in members:
            if m in claimed:
                dupes.append(m)
            claimed.add(m)
    # Open work is in_progress PLUS retire-with-no-plan. Before this, a family
    # claiming a retire row was reported as stale and the row stayed invisible.
    open_work = open_classes | set(unplanned_retire)
    unclaimed = sorted(open_work - claimed)
    stale = sorted(claimed - open_work)

    # A family may only claim to be DECIDED if the document recording that
    # decision exists. Otherwise "decided, awaiting build" is the same kind of
    # unbacked assertion this board replaces.
    missing_plans = [(f[0], f[2]) for f in FAMILIES
                     if f[2] and not os.path.exists(os.path.join(REPO, "schemas", f[2]))]

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
    # Tuple is (name, members, plan, question, status) -- status is index 4.
    # Indexed [3] on the first attempt and every count rendered 0, which is how
    # a status board lies quietly. Guarded below so an unknown status is loud.
    # A "team" claim is only honoured when the cited document carries the
    # sign-off line. Otherwise it is a proposal, whatever the table says.
    decided   = [f for f in FAMILIES if f[4] == "team" and has_signoff(f[2])]
    unsigned  = [f for f in FAMILIES if f[4] == "team" and not has_signoff(f[2])]
    proposed  = [f for f in FAMILIES if f[4] == "proposed"]
    undecided = [f for f in FAMILIES if f[4] == "open"]
    bad_status = [f[0] for f in FAMILIES
                  if f[4] not in ("team", "proposed", "open")]
    if len(decided) + len(unsigned) + len(proposed) + len(undecided) != len(FAMILIES):
        raise SystemExit(
            "status_board: %d families but %d classified -- unclassified: %s"
            % (len(FAMILIES), len(decided) + len(unsigned) + len(proposed) + len(undecided),
               bad_status))

    p("## Where V_eta stands")
    p("")
    p("| | count |")
    p("|---|---|")
    p("| target classes | %d |" % total)
    p("| settled (persist) | %d |" % n_persist)
    p("| settled (retire) | %d |" % n_retire)
    p("| **still open (`in_progress`)** | **%d** |" % n_open)
    p("| **`retire` with no migrator and no plan** | **%d** |" % len(unplanned_retire))
    p("| open **decision families** | **%d** |" % len(FAMILIES))
    p("| &nbsp;&nbsp;DECIDED and signed off, awaiting build | %d |" % len(decided))
    p("| &nbsp;&nbsp;decided in a walkthrough, **awaiting a signature** | %d |" % len(unsigned))
    p("| &nbsp;&nbsp;**written up by Claude alone, unreviewed** | **%d** |" % len(proposed))
    p("| &nbsp;&nbsp;nobody has proposed anything yet | %d |" % len(undecided))
    p("")
    p("The class count is not the work count. %d open classes are %d decisions, "
      "because most open classes move as a family." % (n_open, len(FAMILIES)))
    p("")
    p("**%d of those %d are not settled**: %d awaiting a signature on a decision "
      "already taken, %d written up by Claude alone and unreviewed, %d with "
      "nothing proposed. Only %d are signed off."
      % (len(unsigned) + len(proposed) + len(undecided), len(FAMILIES),
         len(unsigned), len(proposed), len(undecided), len(decided)))
    p("")

    p("## AWAITING A SIGNATURE -- decided with the team, not yet recorded")
    p("")
    p("These were settled in walkthroughs. They are not built and do not render as")
    p("decided because no document carries the sign-off line yet. Nothing here needs")
    p("re-deciding -- it needs recording.")
    p("")
    p("| family | classes | what was decided | document |")
    p("|---|---|---|---|")
    for name, members, plan, what, _ in unsigned:
        p("| **%s** | %d | %s | `%s` |" % (name, len(members), what, plan))
    p("")
    for name, members, _, _, _ in unsigned:
        p("- **%s**: %s" % (name, ", ".join("`%s`" % m for m in sorted(members))))
    p("")

    p("## WRITTEN UP BY CLAUDE ALONE -- nobody has checked the reasoning")
    p("")
    p("Each has template evidence and a written rationale, and **none of it has been")
    p("reviewed**. Counted as open work.")
    p("")
    p("To sign one off, add a line to its document:")
    p("")
    p("```")
    p("%s <who/when> -- <what was decided>" % SIGNOFF)
    p("```")
    p("")
    p("Until that line exists the family shows here regardless of what")
    p("`tools/status_board.py` claims -- Claude cannot promote its own work.")
    p("")
    p("| family | classes | proposal | written up in |")
    p("|---|---|---|---|")
    for name, members, plan, what, _ in proposed:
        p("| **%s** | %d | %s | `%s` |" % (name, len(members), what, plan))
    p("")
    for name, members, _, _, _ in proposed:
        p("- **%s**: %s" % (name, ", ".join("`%s`" % m for m in sorted(members))))
    p("")

    p("## Nobody has proposed anything yet")
    p("")
    p("| family | classes | the call to make |")
    p("|---|---|---|")
    for name, members, _, question, _ in undecided:
        p("| **%s** | %d | %s |" % (name, len(members), question))
    p("")
    for name, members, _, _, _ in undecided:
        p("- **%s**: %s" % (name, ", ".join("`%s`" % m for m in sorted(members))))
    p("")

    p("## DECIDED by the team, awaiting build")
    p("")
    p("The model is settled and recorded; the schema has not changed yet. Every")
    p("one of these re-targets migrators that are already written, which is why")
    p("migrator work before the target closes is rework.")
    p("")
    p("| family | classes | decision | recorded in |")
    p("|---|---|---|---|")
    for name, members, plan, what, _ in decided:
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
    if unplanned_retire:
        p("### `retire`, but nothing decided -- %d rows" % len(unplanned_retire))
        p("")
        p("Marked `retire` with **no migrator and no recorded plan**: the documents")
        p("pass through untouched. `retire` reads as settled, so these do not appear")
        p("in the family counts above -- but they are open work. Several hold real")
        p("data (e.g. `spike_extraction_parameters` carries filter_type / filter_low /")
        p("filter_high / filter_order / filter_ripple).")
        p("")
        for c in unplanned_retire:
            p("- `%s`" % c)
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
