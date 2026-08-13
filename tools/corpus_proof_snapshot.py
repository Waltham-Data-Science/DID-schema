#!/usr/bin/env python3
"""The last known CORPUS PROOF, as a committed artifact instead of a CI log.

WHY THIS EXISTS
---------------
Corpus run 31610970945 proved 44 of the 102 v1 classes against real data, with
0 failures. That number exists in exactly two places, and neither survives:
a GitHub Actions log, and a run artifact that expires. The committed ledger says
something different and correct-for-what-it-is -- `stage 4` reads `not measured`
for every row, because `coverage.py` is generated WITHOUT corpus reports on a
developer machine and rung 4 refuses to guess.

So the repository's own record of the migration says nothing has been proven,
while the strongest evidence we have says 44 classes have. Asked "show me", the
honest answer today is "open this log", and in ninety days it is "you can't".

THIS TOOL CARRIES THE MEASUREMENT ACROSS. `corpus_proven.py` (DID-matlab) already
writes `corpus-proven/v_eta_corpus_proven.json` during the census job; this reads
that file and commits its verdicts, with provenance, as
`schemas/V_eta_corpus_proof.json` + `.md`.

THE ONE RULE THAT MATTERS: A MEASUREMENT IS NEVER OVERWRITTEN BY AN ABSENCE.
Running this without a source, or with a source that measured nothing, LEAVES
THE SNAPSHOT ALONE and says so. That is not politeness -- it is the failure this
repository has paid for repeatedly in the other direction (`silentLoss` printing
0 while reading nothing; a ledger regenerated over a smaller universe). A tool
that regenerates a proof into "not measured" because it was run on a laptop
would erase the only durable copy of the number it exists to keep.

THE SNAPSHOT IS EVIDENCE, NOT A GATE. It records what a named run measured. It
does not re-derive anything, it cannot promote a class, and `--check` never
fails because the file is old -- staleness is REPORTED, with the age, so a
reader can weigh it. A proof that fails CI for being three weeks old would be
deleted within the month.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

SCHEMA_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAPSHOT = os.path.join(SCHEMA_ROOT, "schemas", "V_eta_corpus_proof.json")
SNAPSHOT_MD = os.path.join(SCHEMA_ROOT, "schemas", "V_eta_corpus_proof.md")

S_YES, S_NO, S_NOT_MEASURED = "yes", "no", "not measured"


def read_snapshot(path=None):
    """The committed snapshot, or None. A malformed file is an ERROR, not a None.

    RESOLVED AT CALL TIME, and that is not a style preference. The first draft
    wrote `path=SNAPSHOT`, which binds the module constant at DEFINITION time --
    so redirecting `SNAPSHOT` (what any harness must do to avoid writing into
    the real repo) left this reading the original path, returning None, and
    reporting "no snapshot" while a real one sat there. The anti-clobber rule
    below is built on this return value, so the guard silently did nothing and
    the exercise written to prove it passed while checking nothing.

    Distinguishing "no snapshot yet" from "the snapshot is unreadable" matters:
    the first is the honest starting state, the second is a broken record that
    would otherwise be silently replaced by whatever ran next.
    """
    path = path or SNAPSHOT
    if not os.path.exists(path):
        return None
    with open(path) as fh:
        blob = json.load(fh)
    if not isinstance(blob, dict) or "classes" not in blob:
        raise ValueError(f"{path} exists but carries no `classes` map")
    return blob


def measured_count(blob):
    """How many classes the snapshot actually has a verdict for."""
    if not blob:
        return 0
    return sum(1 for v in blob["classes"].values()
               if v.get("state") in (S_YES, S_NO))


def verdicts(src):
    """Per-class verdicts out of DID-matlab's corpus-proven document.

    THE SHAPE THIS FUNCTION EXISTS FOR, and the bug it replaces. The first
    draft read

        rows = src.get("rung", {}).get("rows") or src.get("rows") or []
        for r in rows: ...

    and `rung.rows` IS NOT A LIST OF ROWS -- it is a COUNT. `corpus_proven.py`
    sets `doc["rung"] = state["rung"]`, and that is the TALLY it builds while
    walking the ledger: `{"rows": len(rows), "yes": n, "no": n,
    "not_measured": n, "yes_classes": [...], "no_rows": [...]}`. So the read
    resolved `rows` to an integer and `for r in 102` raised TypeError on every
    real document -- run 31744202105 among them. The tool was written from a CI
    LOG rather than from the writer, which is the ground-truth rule this
    repository already has for migrators (`where template and WRITER disagree,
    the WRITER wins`) arriving one layer up, in a Python tool nobody had tested.

    WHAT THE SOURCE CAN AND CANNOT SAY. `yes_classes` and `no_rows` NAME their
    classes; `not_measured` is only ever a COUNT there. So a not-measured class
    cannot be listed from this source, and this returns the tally beside the
    map rather than letting a reader infer 0 from an empty section -- "nobody
    looked" must not collapse into "none".

    An unrecognised shape RAISES. Returning {} would be worse than crashing:
    the caller's anti-clobber rule turns an empty ingest into `REFUSING TO
    WRITE`, which reads exactly like the safe no-op it is designed to be, and a
    writer whose shape had changed under us would look like a quiet weekend.
    """
    rung = src.get("rung") if isinstance(src.get("rung"), dict) else {}
    classes = {}
    if "yes_classes" in rung or "no_rows" in rung:
        for name in rung.get("yes_classes") or []:
            classes[name] = {"state": S_YES, "why": ""}
        for row in rung.get("no_rows") or []:
            name = row.get("v1_class")
            if name:
                classes[name] = {"state": S_NO,
                                 "why": (row.get("why") or "")[:400]}
        return classes, rung

    # The per-row shape this tool was originally written for. No writer emits
    # it today; it is kept because a list is unambiguous and costs one isinstance.
    rows = next((c for c in (rung.get("rows"), src.get("rows"))
                 if isinstance(c, list)), None)
    if rows is None:
        raise ValueError(
            "the source names no per-class verdicts: `rung` carries %s and no "
            "`rows` list was found. Expected either `rung.yes_classes` / "
            "`rung.no_rows` (what DID-matlab tools/corpus_proven.py writes) or "
            "a list of row dicts."
            % (sorted(rung) if rung else "nothing"))
    for r in rows:
        name = r.get("v1_class")
        if not name:
            continue
        classes[name] = {"state": r.get("state") or r.get("corpus_verdict"),
                         "why": (r.get("why") or "")[:400]}
    return classes, rung


def ingest(source_path, run=None, sha=None, when=None):
    """Turn DID-matlab's `v_eta_corpus_proven.json` into a snapshot document."""
    with open(source_path) as fh:
        src = json.load(fh)
    classes, rung = verdicts(src)
    # PREFER THE SOURCE'S OWN TALLY over anything counted off `classes`, for
    # `not_measured` especially: the source knows the number and this file
    # cannot name the members, so counting the map would print 0 for a
    # population that exists. Rule 5's denominator, carried rather than re-derived.
    not_measured = rung.get("not_measured")
    if not isinstance(not_measured, int):
        not_measured = sum(1 for v in classes.values()
                           if v["state"] == S_NOT_MEASURED)
    rows_read = rung.get("rows")
    if not isinstance(rows_read, int):
        rows_read = len(classes)
    den = src.get("denominator") or {}
    return {
        "_comment": ("The last CORPUS PROOF carried out of CI. Written by "
                     "tools/corpus_proof_snapshot.py from DID-matlab's "
                     "corpus-proven/v_eta_corpus_proven.json. EVIDENCE, not a "
                     "gate: it records what a named run measured and is never "
                     "re-derived here."),
        "limits": ("`not_measured` is a COUNT carried from the source tally, "
                   "not a list: DID-matlab's corpus_proven.py names the classes "
                   "it proved and the ones that failed, and only counts the "
                   "ones nobody measured. An absent class name here means "
                   "UNNAMED, never `no`."),
        "provenance": {"run": run, "head_sha": sha,
                       "recorded_utc": when or datetime.now(timezone.utc)
                       .strftime("%Y-%m-%dT%H:%M:%SZ"),
                       "source_denominator": den},
        "counts": {
            "classes_with_a_verdict": sum(
                1 for v in classes.values() if v["state"] in (S_YES, S_NO)),
            "proven": sum(1 for v in classes.values() if v["state"] == S_YES),
            "failed": sum(1 for v in classes.values() if v["state"] == S_NO),
            "not_measured": not_measured,
            "classes_named": len(classes),
            "rows_read": rows_read,
        },
        "classes": classes,
    }


def render_md(blob):
    p = blob["provenance"]
    c = blob["counts"]
    gen = ("GENERATED by `python3 tools/corpus_proof_snapshot.py --from <file>`. "
           "Do not hand-edit.")
    what = ("This is EVIDENCE, not a gate: it records what one named run "
            "measured. The committed ledger's `stage 4` reads `not measured` on "
            "a developer machine by construction, because `coverage.py` is "
            "generated without corpus reports and rung 4 refuses to guess — so "
            "without this file the repository's own record says nothing has "
            "ever been proven.")
    tail = ("THE CORPORA ARE A SAMPLE OF DATASETS, NOT THE UNIVERSE. A class "
            "absent from all of them is UNTESTED — never clean, never failed.")
    unnamed = ("The source NAMES the proven and the failed classes and only "
               "COUNTS the not-measured ones, so this file cannot list them. "
               "A class missing from the sections below is UNNAMED HERE, which "
               "is not a verdict of any kind.")
    lines = [
        "# V_eta corpus proof — the last measurement carried out of CI", "",
        gen, "", what, "",
        f"- **run**: `{p.get('run') or 'unrecorded'}`",
        f"- **head sha**: `{p.get('head_sha') or 'unrecorded'}`",
        f"- **recorded**: {p.get('recorded_utc')}", "",
        "| verdict | classes |", "|---|---|",
        f"| PROVEN | **{c['proven']}** |",
        f"| FAILED | {c['failed']} |",
        f"| not measured (absent from every corpus, or unevaluable) | {c['not_measured']} |",
        f"| classes NAMED in this file | {c.get('classes_named', c['rows_read'])} |",
        f"| rows read | {c['rows_read']} |", "",
        unnamed, "",
        "## Proven", "",
    ]
    proven = sorted(n for n, v in blob["classes"].items() if v["state"] == S_YES)
    lines.append(", ".join(f"`{n}`" for n in proven) if proven else "_none_")
    failed = sorted(n for n, v in blob["classes"].items() if v["state"] == S_NO)
    if failed:
        lines += ["", "## Failed", ""]
        for n in failed:
            lines.append(f"- `{n}` — {blob['classes'][n]['why']}")
    lines += ["", tail, ""]
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--from", dest="source",
                    help="DID-matlab corpus-proven/v_eta_corpus_proven.json")
    ap.add_argument("--run", help="the CI run id the measurement came from")
    ap.add_argument("--sha", help="the head sha that run measured")
    ap.add_argument("--check", action="store_true",
                    help="report the committed snapshot; write nothing")
    args = ap.parse_args(argv)

    try:
        existing = read_snapshot()
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"corpus_proof_snapshot: THE COMMITTED SNAPSHOT IS UNREADABLE -- {exc}")
        print("  That is a broken record, not an absent one, and it is NOT "
              "replaced automatically. Fix or delete it deliberately.")
        return 1

    have = measured_count(existing)
    # RULE 5: the denominator, first and unconditionally.
    print("V_eta CORPUS PROOF snapshot")
    print("  DENOMINATOR: committed snapshot carries %d class verdict(s)%s"
          % (have,
             "" if not existing else
             " from run %s recorded %s"
             % (existing["provenance"].get("run") or "?",
                existing["provenance"].get("recorded_utc") or "?")))

    if args.check or not args.source:
        if not existing:
            print("  NO SNAPSHOT RECORDED YET. The repository therefore holds no "
                  "durable evidence of any corpus proof -- the numbers live only "
                  "in CI logs and expiring artifacts. Run a corpus job, then "
                  "`--from corpus-proven/v_eta_corpus_proven.json`.")
        else:
            c = existing["counts"]
            print("  PROVEN %d | FAILED %d | not measured %d (of %d rows read)"
                  % (c["proven"], c["failed"], c["not_measured"], c["rows_read"]))
            print("  This is EVIDENCE FROM A NAMED RUN, not a re-derivation, and "
                  "its age is for the reader to weigh -- staleness is reported "
                  "here and never fails a gate.")
        return 0

    fresh = ingest(args.source, run=args.run, sha=args.sha)
    got = measured_count(fresh)
    # THE ANTI-CLOBBER RULE. See the module docstring: an absence must never
    # overwrite a measurement, or the one durable copy of the number is erased
    # by running the tool in the wrong place.
    if got == 0 and have > 0:
        print("  *** REFUSING TO WRITE. The source measured 0 classes and the "
              "committed snapshot carries %d. A measurement is never "
              "overwritten by an absence; the snapshot is unchanged." % have)
        return 1
    with open(SNAPSHOT, "w") as fh:
        json.dump(fresh, fh, indent=1, sort_keys=True)
        fh.write("\n")
    with open(SNAPSHOT_MD, "w") as fh:
        fh.write(render_md(fresh))
    c = fresh["counts"]
    print("  WROTE %s + .md -- PROVEN %d | FAILED %d | not measured %d"
          % (os.path.relpath(SNAPSHOT, SCHEMA_ROOT),
             c["proven"], c["failed"], c["not_measured"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
