#!/usr/bin/env python3
"""The review sheet for the classes whose migration RUNS but was never CONFIRMED.

WHY THIS EXISTS
---------------
The completion ladder puts 68 of 102 v1 classes at stage 1: a migrator consumes
the class, and rung 2 -- "its decided target classes EXIST in the build" --
reads `not measured`. That reads like 68 classes of unbuilt work. It is not.

`V_eta_migration_targets.json` says so in its own header: `targets` is GENERATED
from the call graph, while `decided_targets` is AUTHORED and means specifically
"a signed decision no migrator implements yet". So `decided_targets` is only ever
populated where a gap is ALREADY KNOWN. A class whose migrator emits something,
with no recorded gap, carries no decided target at all -- and the ladder,
correctly, refuses to score a rung nobody answered.

    DENOMINATOR: 68 classes at stage 1
      carry generated targets   64
      carry an authored intent  67
      carry a caveat flag       66
      absent from the map        1

So the question in front of the team is not "what should these classes become".
It is "is what the migrator ALREADY emits the answer we want" -- 68 times. That
is a review, and a review needs a sheet.

THESE FIGURES MOVED ONCE ALREADY, AND BOTH REASONS ARE WORTH KNOWING. The stage
count rose 65 -> 68 because work LANDED (the demo collapse's two migrators, and
`generic_file` credited to its batch post-pass), which is the ladder working.
The "absent from the map" figure fell 5 -> 1 because THIS TOOL WAS WRONG: it
looked the map up by the ledger's did_v1 spelling only, and the map is keyed the
way migrator FILES are named. See `lookup`. Re-derive these numbers rather than
quoting them; the tool prints its own denominator every run.

WHAT THIS TOOL WILL NOT DO
--------------------------
It does not decide anything, and it does not write a `TEAM-SIGN-OFF` line
(Operating Rule 4). It sorts the open classes by WHAT KIND OF ANSWER each one
needs, quotes the evidence beside each, and stops. Every row lands in exactly
one bucket and the tool asserts that -- a class that fell out of the sort would
otherwise be a class nobody reviews.

It writes nothing by default. `--json PATH` / `--markdown PATH` are opt-in, and
neither defaults to anywhere inside `schemas/`.
"""
import argparse
import collections
import json
import os
import re
import sys

SCHEMA_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(SCHEMA_ROOT, "schemas", "V_eta_coverage_ledger.json")
TARGETS = os.path.join(SCHEMA_ROOT, "schemas", "V_eta_migration_targets.json")

# The buckets. ORDER IS THE ORDER A REVIEWER SHOULD WORK IN: the cheapest
# answers first, so a sitting that runs out of time has cleared the confirmable
# ones rather than a random third.
B_CONFIRM = "CONFIRM THE EMITTED SET"
B_PASSTHROUGH = "CONFIRM A PASSTHROUGH"
B_NO_EMISSION = "NO EMISSION RECORDED -- INVESTIGATE FIRST"
B_UNMAPPED = "ABSENT FROM THE TARGET MAP"
BUCKETS = [B_CONFIRM, B_PASSTHROUGH, B_NO_EMISSION, B_UNMAPPED]

BUCKET_ASK = {
    B_CONFIRM: ("The migrator emits a NEW target set and the intent is written "
                "down. The ask is yes/no on that set."),
    B_PASSTHROUGH: ("The migrator emits the class under its OWN v1 name -- the "
                    "document survives, unchanged, as a tombstone. The ask is "
                    "whether that is the intended END STATE or a deferral."),
    B_NO_EMISSION: ("The class is in the target map with an authored intent, but "
                    "the call graph resolved NO emitted class. That is a "
                    "question for whoever reads the migrator, not for the team "
                    "-- it may be a batch post-pass the graph cannot see."),
    B_UNMAPPED: ("Not in the curated target map at all. Nothing is recorded to "
                 "confirm; this needs a first pass before it can be reviewed."),
}

# WHO OWES THE ANSWER. Two of the four buckets are not the team's to answer, and
# saying so is the difference between "68 questions" and "64 questions plus 4
# pieces of homework". A reviewer handed all 68 undifferentiated cannot tell
# which ones they are BLOCKED on versus merely uninformed about.
ANSWER_FROM = {B_CONFIRM: "team", B_PASSTHROUGH: "team",
               B_NO_EMISSION: "migrator reader", B_UNMAPPED: "migrator reader"}

# THE OPTIONS ARE NAMED, NOT IMPLIED. The sheet's first version printed the
# emitted set in the declarative and expected a reviewer to infer that a
# question was being asked -- and the team read it, correctly, as a report of
# decisions already taken. A question a reader has to reconstruct is a
# question that gets answered by silence.
#
# `unsure` is a REAL answer and is deliberately not a null. "Nobody has looked"
# and "we looked and could not agree" are different facts, which is the same
# three-state rule the corpus rung is built on -- an unanswered row and a row
# parked for discussion must never collapse into each other.
OPT_UNSURE = ("unsure", "Not sure — needs discussion")
BUCKET_OPTIONS = {
    B_CONFIRM: [("yes", "Yes — that is the target we want"),
                ("no", "No — it should emit something else"), OPT_UNSURE],
    B_PASSTHROUGH: [("end_state", "End state — the tombstone is correct"),
                    ("deferral", "Deferral — a fold is still owed"), OPT_UNSURE],
}


def question_for(bucket, v1_class, emits, second_pass=(), final=None,
                 partial=False):
    """The row's ask, in the INTERROGATIVE, self-contained enough to answer alone.

    Self-contained matters more than brevity here: these are read one at a time,
    days apart, by someone who did not write the migrator. A question that says
    "is that right?" while the "that" lives three lines above in a differently
    formatted block is how the first sheet read as a set of assertions.
    """
    if bucket == B_CONFIRM:
        if not emits and second_pass:
            # Said differently ON PURPOSE: a reviewer needs to know the pass-1
            # migrator emits NOTHING here, because "it produces X" would read as
            # a single-document fold and the failure modes are not the same one
            # -- a batch pass only fires when its referents are in the batch.
            return ("Migrating `%s` emits nothing in pass 1; a batch post-pass "
                    "then produces %s. Is that the end state we want for `%s`?"
                    % (v1_class, ", ".join(second_pass), v1_class))
        # THE QUESTION NAMES DESTINATIONS, NOT EVERY MINTED CLASS. It used to
        # recite `targets` verbatim, so `daqreader_ndr` was put to the team as
        # "produces daqreader, acquisition_reader, software" -- and `daqreader`
        # is folded away in the same pass. Asking someone to confirm an end
        # state while listing classes that are not end states is a question that
        # cannot be answered as written.
        shown = final if final is not None else list(emits)
        emitted = ", ".join(shown) if shown else "(nothing recorded)"
        q = ("Migrating `%s` today ends as %s. Is that the end state we "
             "want for `%s`?" % (v1_class, emitted, v1_class))
        if partial:
            # Do not ask for a confirmation the evidence cannot support.
            q += (" NOTE: that set is a LOWER BOUND -- at least one emission "
                  "could not be read from the code, so answering `yes` here "
                  "confirms less than it appears to.")
        return q
    if bucket == B_PASSTHROUGH:
        return ("`%s` is folded into nothing -- its documents survive under "
                "their own v1 name as a tombstone. Is that the intended end "
                "state, or work still owed?" % v1_class)
    if bucket == B_NO_EMISSION:
        return ("`%s` has an authored intent but the call graph resolved no "
                "emitted class. Someone must read the migrator before this can "
                "be put to the team." % v1_class)
    return ("`%s` is absent from the curated target map. There is nothing "
            "recorded to confirm yet." % v1_class)


def load(path):
    with open(path) as fh:
        return json.load(fh)


def snake(name):
    """camelCase -> snake_case, as universalRenames and coverage.py do it."""
    s = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", str(name))
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    return s.lower()


def lookup(targets_map, v1_class):
    """The curated row for a class, under EITHER spelling.

    THE LEDGER AND THE MAP ARE KEYED DIFFERENTLY, and this tool got it wrong
    the first time in the direction that manufactures work. The ledger keys
    rows by the did_v1 class name (`demoNDI`, `ontologyImage`); the map is keyed
    the way the migrator FILES are named, in snake_case (`demo_ndi`,
    `ontology_image`). Looking up by the ledger's spelling alone reported 8
    classes as ABSENT FROM THE TARGET MAP when 7 of them were present all along
    -- so a reviewer would have been handed seven classes to investigate that
    are already recorded.

    This is the third instance of the same trap in one day (`demo_ndi`/`demoNDI`
    in a disposition, then the walkthrough generator's migrator search), which
    is why it is a shared helper with a name rather than an inline `.get()`.
    """
    return targets_map.get(v1_class) or targets_map.get(snake(v1_class))


def classify(v1_class, entry):
    """Exactly one bucket per class, decided from recorded evidence only."""
    if entry is None:
        return B_UNMAPPED
    targets = entry.get("targets") or []
    # A CLASS THAT EMITS ONLY VIA A BATCH POST-PASS IS STILL EMITTING, and
    # reading `targets` alone hid that -- inside the very sheet built to surface
    # unanswered questions. `targets` is GENERATED from the call graph, which
    # cannot see a batch pass; `second_pass` is the authored record of what the
    # pass emits. `stimulus_bath` has an empty `targets` and two second-pass
    # emissions, and was being filed as "investigate first, not a team
    # question" while its question was ready to ask.
    #
    # This is emission shape (2) of `V_eta_OPEN_WORK.md` row #107 -- the shape
    # the ladder's rung 3 is already known to miss. Repeating a recorded blind
    # spot one layer up is worse than the original, because the sheet is what a
    # reviewer trusts to be complete.
    if not targets and not (entry.get("second_pass") or []):
        return B_NO_EMISSION
    # A migrator that emits only the source class name is a PASSTHROUGH: the
    # document validates against its own v1 tombstone and nothing was folded.
    # That is a legitimate end state for some classes and a deferral for
    # others, and the two are indistinguishable from here -- which is exactly
    # why it is a separate question rather than folded into CONFIRM.
    if {t.lower() for t in targets} == {v1_class.lower()}:
        return B_PASSTHROUGH
    return B_CONFIRM


# ---------------------------------------------------------------------------
# WHAT A DESTINATION ACTUALLY IS
# ---------------------------------------------------------------------------
# `targets` lists every class the migrator MINTS, and some of those are pass-1
# TRANSPORT HANDLES that a later pass folds away. Rendering them undifferentiated
# asked the team to confirm `daqreader`, `session_relative_reference` and
# `epoch_bounded_reference` as end states; none of the three is one, and all
# three are marked `in_progress` in the built set, which is exactly what "not in
# the persist set" means. Reported 2026-08-13: "I'm struggling to confirm those
# rows when you are showing me intermediate classes."
#
# The disposition is READ FROM THE BUILT INDEX, never hardcoded -- a hand list
# would go stale the day a class is promoted. What IS named here is the pass that
# performs each fold, because that fact lives in the other repository's code and
# no artifact in this one carries it.
_FOLDED_BY = {
    "session_relative_reference": "did2.convert.resolveSessionAnchors",
    "epoch_bounded_reference":    "ndi.migrate.internal.epochAnchorFold",
    "daqreader":                  "migrators_j/daqreader.m (same pass)",
}


def load_dispositions():
    """{class_name: disposition} from the built V_eta index, or {} with a why."""
    path = os.path.join(SCHEMA_ROOT, "schemas", "V_eta", "index.json")
    try:
        with open(path) as fh:
            idx = json.load(fh)
    except (OSError, ValueError) as exc:
        return {}, "the built V_eta index could not be read (%s)" % exc
    return ({s["class_name"]: s.get("disposition")
             for s in idx.get("schemas", [])}, "")


def destinations(emits, disp):
    """Split an emitted set into FINAL destinations and intermediates.

    An unknown disposition is neither -- it is reported as unknown rather than
    assumed final, because assuming final is the reassuring direction and this
    sheet is read as a decision aid.
    """
    final, intermediate, unknown = [], [], []
    for cls in emits:
        d = disp.get(cls)
        if d is None:
            unknown.append(cls)
        elif d == "persist":
            final.append(cls)
        else:
            intermediate.append((cls, d, _FOLDED_BY.get(cls, "")))
    return final, intermediate, unknown


def build(ledger, targets_map, stage=1):
    rows, unclassified = [], []
    disp, disp_why = load_dispositions()
    if disp_why:
        # NOT a silent degradation. Without dispositions every row would render
        # with no `ENDS AS` line at all, which reads exactly like a row whose
        # emissions are all final -- the reassuring direction, on the sheet the
        # team uses to decide. Say it once, loudly, and let the caller render it.
        unclassified.append(
            "*** DESTINATIONS UNAVAILABLE: %s. Every row below lists MINTED "
            "classes only; intermediates are NOT marked." % disp_why)
    for r in ledger["rows"]:
        if r["stage"]["reached"] != stage:
            continue
        cls = r["v1_class"]
        entry = lookup(targets_map, cls)
        bucket = classify(cls, entry)
        if bucket not in BUCKETS:
            unclassified.append(cls)
            continue
        e = entry or {}
        rows.append({
            "v1_class": cls,
            "bucket": bucket,
            "question": question_for(
                bucket, cls, e.get("targets") or [],
                e.get("second_pass") or [],
                final=destinations(e.get("targets") or [], disp)[0],
                partial=(e.get("target_completeness") or {}).get("state")
                        == "partial"),
            "options": [{"key": k, "label": v}
                        for k, v in BUCKET_OPTIONS.get(bucket, [])],
            "answer_from": ANSWER_FROM[bucket],
            "emits": e.get("targets") or [],
            "destinations": destinations(e.get("targets") or [], disp)[0],
            "intermediates": [
                {"class": c, "disposition": d, "folded_by": by}
                for c, d, by in destinations(e.get("targets") or [], disp)[1]],
            "destination_unknown": destinations(e.get("targets") or [], disp)[2],
            "target_completeness": e.get("target_completeness") or {},
            "carried": e.get("carried") or [],
            "second_pass": e.get("second_pass") or [],
            "intent": e.get("how") or "",
            "caveat": e.get("flags") or "",
            "governance": r["governance"]["state"],
            "corpus": r["stage"]["ladder"][3]["state"],
        })
    return rows, unclassified


def render(rows, unclassified, total_rows, stage, out=sys.stdout):
    def p(s=""):
        print(s, file=out)

    by = collections.Counter(r["bucket"] for r in rows)
    # RULE 5: the denominator, first and unconditionally.
    p("V_eta CONFIRM SHEET -- the classes whose migration runs but is unconfirmed")
    p("  DENOMINATOR: %d ledger row(s) read, %d at stage %d, %d sorted, "
      "%d UNSORTED" % (total_rows, len(rows) + len(unclassified), stage,
                       len(rows), len(unclassified)))
    for b in BUCKETS:
        p("    %-42s %3d" % (b, by.get(b, 0)))
    if unclassified:
        p("    *** %d CLASS(ES) FELL OUT OF EVERY BUCKET -- a class nobody "
          "reviews: %s" % (len(unclassified), ", ".join(sorted(unclassified))))
    p()
    p("  Governance and corpus state are shown per row and are NOT part of the")
    p("  sort: a class can be signed and unproven, or proven and unsigned.")
    p("  `not measured` on the corpus column means NOBODY LOOKED -- 57 of the")
    p("  102 v1 classes appear in none of the six corpora we hold, so for those")
    p("  it can never read anything else here.")
    p()
    for b in BUCKETS:
        mine = [r for r in rows if r["bucket"] == b]
        if not mine:
            continue
        p("=" * 78)
        p("%s  (%d)" % (b, len(mine)))
        p("  %s" % BUCKET_ASK[b])
        p("=" * 78)
        for r in sorted(mine, key=lambda x: x["v1_class"].lower()):
            p("  %s" % r["v1_class"])
            # THE QUESTION LEADS. Everything under it is the evidence for
            # answering it, and is indented to read as subordinate to it.
            p("      Q: %s" % r["question"])
            for o in r["options"]:
                p("         [ ] %s" % o["label"])
            p("      -- the evidence --")
            p("      emits      : %s" % (", ".join(r["emits"]) or "(none recorded)"))
            if r["destinations"]:
                p("      ENDS AS    : %s" % ", ".join(r["destinations"]))
            for it in r["intermediates"]:
                p("      intermediate: %s (%s) -- folded by %s"
                  % (it["class"], it["disposition"],
                     it["folded_by"] or "a later pass; emitter not recorded here"))
            for u in r["destination_unknown"]:
                p("      UNKNOWN    : %s is not in the built index -- neither a "
                  "destination nor an intermediate can be claimed" % u)
            tc = r["target_completeness"]
            if tc.get("state") == "partial":
                # THE ROW IS NOT ANSWERABLE FROM `emits` ALONE and the sheet has
                # to say so where the reader is looking. refresh_migration_targets
                # knew this and only printed it; the fact was lost between tools.
                p("      *** THE EMITTED SET ABOVE IS A LOWER BOUND -- this row "
                  "cannot be confirmed as an end state from it alone.")
                for site in tc.get("unresolved_sites", []):
                    p("          unread: %s" % site.get("why", ""))
                    p("                  %s" % site.get("site", ""))
            if r["carried"]:
                p("      attaches to: %s" % ", ".join(r["carried"]))
            if r["second_pass"]:
                p("      2nd pass   : %s" % ", ".join(r["second_pass"]))
            if r["intent"]:
                p("      intent     : %s" % r["intent"])
            if r["caveat"]:
                p("      caveat     : %s" % r["caveat"])
            p("      governance : %s        corpus: %s"
              % (r["governance"], r["corpus"]))
            p()
    return by


def markdown(rows, out):
    blurb = ("One row per v1 class whose migrator RUNS but whose target set was "
             "never confirmed. Nothing here is a decision; each row is a "
             "question with its evidence attached.")
    lines = ["# V_eta confirm sheet", "", blurb, ""]
    for b in BUCKETS:
        mine = [r for r in rows if r["bucket"] == b]
        if not mine:
            continue
        lines += ["## %s (%d)" % (b, len(mine)), "", BUCKET_ASK[b], "",
                  "| v1 class | emits | intent | caveat | governance | corpus |",
                  "|---|---|---|---|---|---|"]
        for r in sorted(mine, key=lambda x: x["v1_class"].lower()):
            def cell(s):
                return str(s).replace("|", "\\|").replace("\n", " ")
            lines.append("| `%s` | %s | %s | %s | %s | %s |" % (
                r["v1_class"], cell(", ".join(r["emits"]) or "—"),
                cell(r["intent"] or "—"), cell(r["caveat"] or "—"),
                cell(r["governance"]), cell(r["corpus"])))
        lines.append("")
    with open(out, "w") as fh:
        fh.write("\n".join(lines) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", type=int, default=1,
                    help="ladder stage to sheet (default 1)")
    ap.add_argument("--json", dest="json_out")
    ap.add_argument("--markdown", dest="md_out")
    args = ap.parse_args(argv)

    for path in (LEDGER, TARGETS):
        if not os.path.exists(path):
            sys.exit("confirm_sheet: %s is missing -- run tools/gates.py first"
                     % os.path.relpath(path, SCHEMA_ROOT))
    ledger = load(LEDGER)
    targets_map = load(TARGETS)["classes"]
    rows, unclassified = build(ledger, targets_map, stage=args.stage)
    render(rows, unclassified, len(ledger["rows"]), args.stage)

    for out in (args.json_out, args.md_out):
        if out and os.path.abspath(out).startswith(
                os.path.join(SCHEMA_ROOT, "schemas") + os.sep):
            sys.exit("confirm_sheet: refusing to write into schemas/ -- this "
                     "sheet is a proposal, and nothing enters the record "
                     "without the team (Operating Rule 1)")
    if args.json_out:
        with open(args.json_out, "w") as fh:
            json.dump({"stage": args.stage, "rows": rows,
                       "unsorted": unclassified}, fh, indent=1)
    if args.md_out:
        markdown(rows, args.md_out)
    return 1 if unclassified else 0


if __name__ == "__main__":
    sys.exit(main())
