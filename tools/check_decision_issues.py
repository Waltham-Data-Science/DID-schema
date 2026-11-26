"""Every decision line with a build left names an open issue that tracks it.

[build state lives in issues] (Jess Haley, 2026-11-26,
did_v2_go_forward_class_audit.md): a decision line records the decision; whether
its build is done lives in the issue tracker. A line whose build is not done says
so with a pending marker (`Build pending:`, or `Build pending (...)` as the
spatial transcriptomics plan writes it) and names the issue with
`Tracked in: <owner/repo>#<n>[, <owner/repo>#<n> ...]`.

Rules:
  D1  a decision line with a pending marker names at least one issue after
      `Tracked in:`;
  D2  at least one issue it names is open in the committed snapshot
      `tools/decision_issues.json`. A line whose every issue is closed still
      says a build is left, so the record and the tracker disagree;
  D3  every issue it names is in the snapshot (otherwise NOT MEASURED, which
      fails: run `--refresh`).

The gate runs offline against the snapshot. `--refresh` rewrites it from GitHub
(network; commit it deliberately). `--live` also compares the snapshot with
GitHub now. The report states its denominator first (Operating Rule 5).

    python3 tools/check_decision_issues.py
    python3 tools/check_decision_issues.py --refresh
    python3 tools/check_decision_issues.py --live
"""
import argparse
import datetime
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import doc_paths  # noqa: E402
from check_open_work_issues import fetch_issue  # noqa: E402
from decision_citations import match_decided_by  # noqa: E402

SNAPSHOT = os.path.join(HERE, "decision_issues.json")
PENDING = re.compile(r"Build pending ?[:(]")
TRACKED = re.compile(r"Tracked in: ((?:[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+#\d+(?:, )?)+)")
REF = re.compile(r"([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)#(\d+)")


def issue_key(repo, number):
    """`owner/repo#n`, lower-cased so did-schema and DID-schema are one repo."""
    return f"{repo.lower()}#{int(number)}"


def tracked_issues(line):
    """Every `owner/repo#n` named after `Tracked in:` on the line, in order."""
    keys = []
    for m in TRACKED.finditer(line):
        for r, n in REF.findall(m.group(1)):
            k = issue_key(r, n)
            if k not in keys:
                keys.append(k)
    return keys


def pending_lines(docs_dir=None):
    """(decision lines read, [{document, line, tag, issues}]) for lines with a build left."""
    read, out = 0, []
    for path in doc_paths.record_documents(docs_dir):
        with open(path, encoding="utf-8") as fh:
            for n, line in enumerate(fh, 1):
                parsed = match_decided_by(line)
                if not parsed and not line.startswith("TEAM-SIGN-OFF"):
                    continue
                read += 1
                if PENDING.search(line):
                    out.append({"document": os.path.basename(path), "line": n,
                                "tag": parsed["tag"] if parsed else None,
                                "issues": tracked_issues(line)})
    return read, out


def check(pending, snapshot):
    """The failures, one string each."""
    issues = (snapshot or {}).get("issues", {})
    fails = []
    for p in pending:
        where = f"{p['document']}:{p['line']} [{p['tag']}]"
        if not p["issues"]:
            fails.append(f"D1 {where}: a build is left and no issue is named (`Tracked in:`)")
            continue
        missing = [k for k in p["issues"] if k not in issues]
        if missing:
            fails.append(f"D3 {where}: {', '.join(missing)} not in the snapshot "
                         "(NOT MEASURED; run --refresh)")
            continue
        if not any(issues[k].get("state") == "open" for k in p["issues"]):
            fails.append(f"D2 {where}: a build is left but every issue it names is closed "
                         f"({', '.join(p['issues'])})")
    return fails


def refresh(pending, fetch=fetch_issue, now=None):
    keys = sorted({k for p in pending for k in p["issues"]})
    now = now or datetime.datetime.now(datetime.timezone.utc)
    return {"why": "The state of the GitHub issues that decision lines with a build "
                   "left name in `Tracked in:`, read offline by "
                   "tools/check_decision_issues.py. Written by `--refresh` (network); "
                   "moved deliberately and committed. [build state lives in issues], "
                   "Jess Haley, 2026-11-26.",
            "fetched_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "issues": {k: fetch(k) for k in keys}}


def load_snapshot(path=SNAPSHOT):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except OSError:
        return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--refresh", action="store_true",
                    help="rewrite tools/decision_issues.json from GitHub")
    ap.add_argument("--live", action="store_true",
                    help="also compare the snapshot with GitHub now")
    args = ap.parse_args(argv)
    read, pending = pending_lines()

    if args.refresh:
        try:
            snap = refresh(pending)
        except OSError as e:
            print(f"REFRESH FAILED, nothing written: {e}")
            return 2
        with open(SNAPSHOT, "w", encoding="utf-8") as f:
            json.dump(snap, f, indent=4, sort_keys=True)
            f.write("\n")
        print(f"wrote {os.path.relpath(SNAPSHOT, REPO)}: {len(snap['issues'])} issue(s), "
              f"fetched {snap['fetched_at']}")

    snap = load_snapshot()
    cited = sorted({k for p in pending for k in p["issues"]})
    print(f"DENOMINATOR: {read} decision line(s) read in docs/**/*.md (not docs/generated/), "
          f"{len(pending)} with a build left, {len(cited)} distinct issue(s) named")
    if snap is None:
        print("  snapshot: tools/decision_issues.json is missing (NOT MEASURED)")
    else:
        print(f"  snapshot: {len(snap.get('issues', {}))} issue(s), fetched "
              f"{snap.get('fetched_at')} (an issue closed after that is not seen)")
    fails = check(pending, snap)

    if args.live and snap is not None:
        drift, unreached = [], []
        for k in cited:
            try:
                now = fetch_issue(k)
            except OSError as e:
                unreached.append(str(e))
                continue
            was = snap.get("issues", {}).get(k, {}).get("state")
            if now["state"] != was:
                drift.append(f"{k}: snapshot {was}, GitHub {now['state']}")
        print(f"LIVE: {len(cited) - len(unreached)} of {len(cited)} issue(s) compared, "
              f"{len(drift)} differ from the snapshot")
        for d in drift:
            print(f"  DIFFERS {d}")
        if drift:
            fails.append(f"LIVE: {len(drift)} issue(s) differ from the snapshot; run --refresh")

    for f in fails:
        print(f"  FAIL {f}")
    print(f"decision lines with a build left: {len(pending)}; failures: {len(fails)}")
    if read == 0:
        print("FAIL: no decision line read; nothing was checked")
        return 1
    if fails:
        return 1
    print("OK: every decision line with a build left names an open issue")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
