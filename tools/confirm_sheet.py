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
    if not targets:
        return B_NO_EMISSION
    # A migrator that emits only the source class name is a PASSTHROUGH: the
    # document validates against its own v1 tombstone and nothing was folded.
    # That is a legitimate end state for some classes and a deferral for
    # others, and the two are indistinguishable from here -- which is exactly
    # why it is a separate question rather than folded into CONFIRM.
    if {t.lower() for t in targets} == {v1_class.lower()}:
        return B_PASSTHROUGH
    return B_CONFIRM


def build(ledger, targets_map, stage=1):
    rows, unclassified = [], []
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
            "emits": e.get("targets") or [],
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
            p("      emits      : %s" % (", ".join(r["emits"]) or "(none recorded)"))
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
