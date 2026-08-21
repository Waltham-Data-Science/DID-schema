#!/usr/bin/env python3
"""bar2_gap.py -- the PER-CORPUS Bar-2 gap.

WHY THIS EXISTS. On 2026-08-21 a green corpus run was reported as "Bar-2 held."
It was not: a green run gates BAR-1 (0 quarantine, 0 orphans -- the documents
migrate and validate). BAR-2 is every document at its DECIDED FINAL V_eta shape,
and NO instrument emitted a per-corpus Bar-2 verdict. The coverage ladder is
keyed to the 102-class UNIVERSE, not to a corpus; its rung 3 reads `not measured`
both when a class is genuinely undecided AND when the migrator already emits the
decided target (no gap to flag) -- two opposite facts under one label; and it
does not see HUSKS (a class can emit its decided target while its SOURCE
documents survive undeleted). This tool answers, for the classes a SPECIFIC
corpus contains: is each at its decided final shape?

INPUTS
  * one or more `<corpus>-summary.json` corpus reports (the per-corpus v1 class
    census is `source_census.by_class`; keys are v1 SOURCE class names). Same
    files census_digest.py / corpus_proven.py read.
  * schemas/V_eta_coverage_ledger.json -- per-class `targets` (GENERATED: what
    the migrator emits), `decided_targets` (AUTHORED: a signed gap), `stage`
    (the ladder), `governance`, `disposition`, `target_source`.

VERDICT per (corpus, v1 class present in it)
  SUPERSEDED   ladder rung 3 == 'no' -- the migrator emits a shape the signed
               model SUPERSEDES (e.g. stimulus_presentation -> the old shape, not
               timed_sequence_manipulation). A definite Bar-2 failure.
  HUSK/BRIDGE  the class is in HUSK_BRIDGE below -- the migrator emits SOMETHING,
               but the source documents survive undeleted (a husk) or a raw v1
               string is preserved (a bridge). Not at final shape. The ladder
               cannot see this; the evidence is a batch-pass counter, cited.
  AT_DECIDED   the migrator emits the FULL decided target set (rung 3 yes, or
               rung 3 not-measured because emitted==decided with no authored gap
               and `target_source` is emitted/passthrough), AND not a husk/bridge.
               This is "at decided shape" -- still needs stage 4 (corpus-proof)
               to be PROVEN, which only a clean corpus run supplies.
  UNDECIDED    no decided shape is recorded (no targets, or target_source unknown)
               -- Bar-2 cannot even be assessed.

A corpus is at Bar-2 iff every class it contains is AT_DECIDED *and* the corpus
migrated globally clean (0 quarantine / orphan / fragment -- Bar-1, which this
tool takes from the report and REQUIRES, since a document at the right shape that
does not validate is not at Bar-2 either).

THE TOOL DECIDES NOTHING AND WRITES NO SIGNATURE. It reads the signed record and
reports. It prints its denominator first (Operating Rule 5).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEDGER = HERE.parent / "schemas" / "V_eta_coverage_ledger.json"


# ---- the husk/bridge overlay -------------------------------------------------
# The ladder's rung 3 says a migrator EMITS its decided target; it cannot see
# that the SOURCE documents also survive, or that a raw v1 string was kept as a
# bridge. Each entry is a v1 SOURCE class whose documents are NOT at final shape
# despite an emission, with the batch-pass counter that proves it. Remove an
# entry only when its counter goes to zero on a real run (verify-before-delete).
HUSK_BRIDGE = {
    "stimulus_response_scalar_parameters_basic": {
        "kind": "HUSK",
        "why": "resolveResponseParameters inlines it into method_parameters but "
               "NEVER deletes the source; the params_basic documents survive "
               "unreferenced.",
        "counter": "resolveResponseParameters: `<N> parameters documents ... "
                   "unreferenced, 0 deleted` (Soph run 49: 11167).",
        "clears_when": "the #61 verify-before-delete removes the folded sources.",
    },
    "epochfiles_ingested": {
        "kind": "BRIDGE",
        "why": "the serialized epochprobemap is preserved verbatim on "
               "ingestion_manifest because its stimulator/imaging rows do not "
               "decompose (only recording rows become observations).",
        "counter": "resolveEpochProbemap: `<N> stimulator` rows -> 0 observations "
                   "(Soph run 49: 1225 of 1399).",
        "clears_when": "the stimulus model (#31/#43) + image model (#24) "
                       "decompose the remaining rows and the string retires.",
    },
}


def load_ledger(path=LEDGER):
    d = json.loads(Path(path).read_text())
    return {r["v1_class"]: r for r in d["rows"]}


def norm(name: str) -> str:
    return "".join(ch for ch in str(name).lower() if ch.isalnum())


def rung3_state(row) -> str:
    st = row.get("stage") or {}
    for rung in st.get("ladder", []):
        if rung.get("stage") == 3:
            return rung.get("state", "?")
    return "?"


def verdict_for(v1_class, row):
    """Return (verdict, detail) for one v1 class using the ledger row."""
    if v1_class in HUSK_BRIDGE:
        hb = HUSK_BRIDGE[v1_class]
        return (hb["kind"], hb["why"])
    if row is None:
        return ("UNDECIDED", "class is not in the coverage ledger at all")
    r3 = rung3_state(row)
    disp = row.get("disposition", "?")
    targets = row.get("targets") or []
    decided = row.get("decided_targets") or []
    tsrc = row.get("target_source", "unknown")
    if r3 == "no":
        return ("SUPERSEDED",
                (f"ladder rung 3 = no: the migrator emits {targets or 'nothing'}, "
                 f"not the decided {decided}"))
    # rung 3 yes  -> emits the decided target set.
    if r3 == "yes":
        return ("AT_DECIDED", f"emits decided target(s) {decided or targets}")
    # rung 3 not-measured / n/a: no AUTHORED gap. Two cases.
    if targets and tsrc in ("emitted", "passthrough", "decided", "self"):
        return ("AT_DECIDED",
                (f"no authored gap; migrator emits {targets} "
                 f"(target_source={tsrc}, rung3={r3})"))
    if disp == "persist" and not decided:
        return ("AT_DECIDED", f"persist 1:1 (target_source={tsrc})")
    return ("UNDECIDED",
            (f"no decided shape recorded (targets={targets or '-'}, "
             f"target_source={tsrc}, disposition={disp}, rung3={r3})"))


AT = "AT_DECIDED"
FAIL_KINDS = ("SUPERSEDED", "HUSK", "BRIDGE", "UNDECIDED")


def read_report(path):
    rep = json.loads(Path(path).read_text())
    name = rep.get("corpus") or rep.get("name") or Path(path).stem.replace("-summary", "")
    sc = rep.get("source_census") or {}
    by_class = sc.get("by_class") or {}
    # per-class doc count (source census). value may be an int or a dict.
    census = {}
    for k, v in by_class.items():
        if isinstance(v, dict):
            census[k] = v.get("total_docs", v.get("count", 0))
        else:
            census[k] = v
    # global cleanliness (Bar-1) -- required for Bar-2.
    clean = {
        "quarantine": rep.get("quarantine_count", (rep.get("summary") or {}).get("quarantine_count", 0)),
        "orphans": ((rep.get("reference_integrity") or {}).get("orphan_count", 0)),
        "fragments": (rep.get("fragment_count", (rep.get("summary") or {}).get("fragment_count", 0))),
        "total": (sc.get("total") or rep.get("total") or sum(census.values())),
    }
    return name, census, clean


def find_reports(roots):
    out = []
    for root in roots:
        p = Path(root)
        if p.is_file() and p.name.endswith("-summary.json"):
            out.append(p)
        elif p.is_dir():
            out.extend(sorted(p.rglob("*-summary.json")))
    # de-dup by basename, keep first
    seen, uniq = set(), []
    for p in out:
        if p.name in seen:
            continue
        seen.add(p.name)
        uniq.append(p)
    return uniq


def run(roots, ledger_path=LEDGER, only=None, verbose=False):
    ledger = load_ledger(ledger_path)
    reports = find_reports(roots)
    print(f"DENOMINATOR: {len(roots)} root(s) named, {len(reports)} corpus "
          f"report(s) found; {len(ledger)} ledger rows")
    if not reports:
        print("*** NO CORPUS REPORTS FOUND -- Bar-2 is a per-corpus measure and "
              "needs the reports a real run uploads. Nothing to assess.")
        return 2
    any_gap = False
    for rp in reports:
        corpus, census, clean = read_report(rp)
        if only and corpus not in only:
            continue
        present = sorted(c for c, n in census.items() if (n or 0) > 0)
        print(f"\n================ corpus {corpus} "
              f"({len(present)} v1 class(es), {clean['total']} doc(s)) ================")
        bar1 = (clean["quarantine"] == 0 and clean["orphans"] == 0 and clean["fragments"] == 0)
        print(f"  BAR-1 (migrates+validates): quarantine {clean['quarantine']}, "
              f"orphans {clean['orphans']}, fragments {clean['fragments']} "
              f"-> {'PASS' if bar1 else 'FAIL'}")
        buckets = {AT: [], "SUPERSEDED": [], "HUSK": [], "BRIDGE": [], "UNDECIDED": []}
        for c in present:
            v, detail = verdict_for(c, ledger.get(c))
            buckets.setdefault(v, []).append((c, census[c], detail))
        n_at = len(buckets[AT])
        n_fail = sum(len(buckets[k]) for k in FAIL_KINDS)
        print(f"  BAR-2: {n_at}/{len(present)} classes AT DECIDED SHAPE; "
              f"{n_fail} NOT -- "
              + ", ".join(f"{k} {len(buckets[k])}" for k in FAIL_KINDS if buckets[k]))
        at_bar2 = bar1 and n_fail == 0
        print(f"  ==> corpus {corpus} at Bar-2 (decided shape + Bar-1 clean): "
              f"{'YES (pending stage-4 corpus-proof)' if at_bar2 else 'NO'}")
        for k in FAIL_KINDS:
            for c, n, detail in buckets[k]:
                print(f"      {k:10s} {c:44s} {n:>8} doc(s)  {detail}")
        if verbose:
            for c, n, detail in buckets[AT]:
                print(f"      {AT:10s} {c:44s} {n:>8} doc(s)  {detail}")
        any_gap = any_gap or not at_bar2
    return 1 if any_gap else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Per-corpus Bar-2 gap report.")
    ap.add_argument("roots", nargs="*", help="corpus report dirs/files (*-summary.json)")
    ap.add_argument("--ledger", default=str(LEDGER))
    ap.add_argument("--only", action="append", help="restrict to these corpus name(s)")
    ap.add_argument("--verbose", action="store_true", help="also list AT_DECIDED classes")
    ap.add_argument("--gate", action="store_true",
                    help="exit non-zero if any assessed corpus is not at Bar-2")
    a = ap.parse_args(argv)
    if not a.roots:
        ap.error("pass at least one corpus-report dir or *-summary.json file")
    rc = run(a.roots, a.ledger, set(a.only) if a.only else None, a.verbose)
    return rc if a.gate else 0


if __name__ == "__main__":
    sys.exit(main())
