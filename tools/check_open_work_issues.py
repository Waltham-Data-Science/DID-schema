#!/usr/bin/env python3
"""Every row still under `## OPEN` in docs/did_v2_OPEN_WORK.md points at an
open GitHub issue, and the file takes no new rows.

Decided by Jess Haley, 2026-11-03 [open work lives in issues]
(`did_v2_go_forward_class_audit.md`): open work lives only in GitHub issues;
docs/did_v2_OPEN_WORK.md is frozen as a lookup table from row number to issue;
a gate checks that every row still in OPEN points at an open issue.

WHY THE ROW NUMBER STAYS. Carry register rows (`open_work`), plan documents
and sibling code comments cite `#nn`. Those citations keep working: the row
number is stable, and this file maps it to the issue that tracks the work.
`check_carry_register.py` C5 still requires an `awaiting_home` row's number to
be an OPEN row; this gate requires every OPEN row to point at an open issue.
Together: a home a carry awaits is tracked by an open issue.

HOW ISSUE STATE IS KNOWN WITHOUT THE NETWORK. No gate in the chain calls
GitHub, and CI runs the chain offline. So the state is a committed snapshot,
`tools/open_work_issues.json`, written by `--refresh` (which needs the
network) and read by the gate (which does not). Like `tools/sibling_lock.json`,
the snapshot is moved deliberately and committed. The gate prints the
snapshot's date first: a snapshot says what was true when it was taken, and an
issue closed after it is not seen until the next refresh. `--live` compares
the snapshot with GitHub now and reports NOT CHECKED when GitHub cannot be
reached; it never turns an unreachable network into a pass or a failure.

RULES (each failure names the rule):

  W1  FROZEN. An OPEN row's label is one of the rows OPEN when the file was
      frozen (FROZEN_OPEN), and no row anywhere in the file (OPEN or
      COMPLETED) carries a number above FROZEN_MAX. Rows may leave OPEN for
      COMPLETED; none may be added.
  W2  An OPEN row names a GitHub issue URL (the first one in the row is its
      issue).
  W3  That issue is in the snapshot. An issue the snapshot does not hold is
      NOT MEASURED, and the gate fails on it: run `--refresh`.
  W4  The snapshot says the issue is open.
  W5  AWAITING_ISSUE is a ratchet, not a waiver list. A row in it is
      reported, not failed, for W2-W4 until its issue is reopened or created;
      an entry whose row now passes, or is no longer OPEN, FAILS, so the list
      only shrinks.

It prints its denominator first.

Usage:
    python3 tools/check_open_work_issues.py            the gate (offline)
    python3 tools/check_open_work_issues.py --live     also compare the
                                                       snapshot with GitHub now
    python3 tools/check_open_work_issues.py --refresh  rewrite the snapshot
                                                       from GitHub (network)
"""
import argparse
import datetime
import json
import os
import re
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import doc_paths  # noqa: E402

OPEN_WORK = doc_paths.path_for("did_v2_OPEN_WORK.md")
SNAPSHOT = os.path.join(HERE, "open_work_issues.json")

# The OPEN rows on 2026-11-03, when the file was frozen ([open work lives in
# issues]). Labels as the file writes them in the first cell.
FROZEN_OPEN = (
    "30", "31", "32", "57", "66", "68", "72", "73", "124", "125", "126", "129",
    "130", "131", "132", "135", "136", "138", "139", "140", "143", "145", "146",
    "147", "148", "149", "150", "153", "154", "155", "156", "157", "158", "159",
    "162", "163", "164", "165",
    "9", "45", "47", "60", "61", "65", "74", "79", "103", "113 step 3",
    "119b / 122", "127", "128",
)
# The highest row number the file held when it was frozen.
FROZEN_MAX = 165

# W5. OPEN rows that do not yet point at an open issue, each with what makes
# it pass. Build pending on [open work lives in issues]: an entry leaves this
# list when its issue is reopened or created (and the row and the snapshot
# updated), or when the row moves to COMPLETED.
AWAITING_ISSUE = {
    # empty: row 31's issue, DID-schema #94, is open again (snapshot refreshed
    # 2026-11-09), so it no longer waits for an issue.
}

ISSUE_RE = re.compile(r"https://github\.com/([\w.-]+)/([\w.-]+)/issues/(\d+)")
INT_RE = re.compile(r"\d+")


def issue_key(owner, repo, number):
    return f"{owner}/{repo}#{int(number)}"


def _sections(text):
    """{section title: [lines]} for the `## ` sections."""
    out, cur = {}, None
    for ln in text.splitlines():
        if ln.startswith("## "):
            cur = ln[3:].strip()
            out[cur] = []
        elif cur is not None:
            out[cur].append(ln)
    return out


def table_rows(lines):
    """[(label, line)] for the table rows among `lines` (not headers or rules)."""
    out = []
    for ln in lines:
        if not ln.startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        label = cells[0] if cells else ""
        if not label or label in ("#", "row") or set(label) <= set("-: "):
            continue
        out.append((label, ln))
    return out


def parse(text):
    """(open rows [(label, line)], every row [(section, label, line)])."""
    secs = _sections(text)
    open_rows = table_rows(secs.get("OPEN", []))
    every = [(s, lab, ln) for s, lines in secs.items()
             if s.startswith(("OPEN", "COMPLETED"))
             for lab, ln in table_rows(lines)]
    return open_rows, every


def row_issue(line):
    """The row's issue: the first GitHub issue URL in it, as `owner/repo#n`."""
    m = ISSUE_RE.search(line)
    return issue_key(*m.groups()) if m else None


def check(text, snapshot, frozen_open=FROZEN_OPEN, frozen_max=FROZEN_MAX,
          awaiting=None):
    """Returns (failures, awaiting reports, open rows, issues cited)."""
    awaiting = AWAITING_ISSUE if awaiting is None else awaiting
    open_rows, every = parse(text)
    issues = (snapshot or {}).get("issues", {})
    fails, waits, cited = [], [], set()
    for sec, label, _ln in every:
        nums = [int(n) for n in INT_RE.findall(label)]
        if any(n > frozen_max for n in nums):
            fails.append(f"W1 row {label} ({sec}): a row number above {frozen_max}; "
                         f"the file is frozen, open work goes to a GitHub issue")
    open_labels = set()
    for label, line in open_rows:
        open_labels.add(label)
        if label not in frozen_open:
            fails.append(f"W1 row {label}: not an OPEN row when the file was frozen; "
                         f"open work goes to a GitHub issue")
            continue
        key = row_issue(line)
        if key:
            cited.add(key)
        if key is None:
            problem = "W2 names no GitHub issue"
        elif key not in issues:
            problem = f"W3 issue {key} is not in the snapshot (NOT MEASURED; run --refresh)"
        elif issues[key].get("state") != "open":
            problem = (f"W4 issue {key} is {issues[key].get('state')} "
                       f"({issues[key].get('state_reason')}) in the snapshot")
        else:
            problem = None
        if problem is None:
            if label in awaiting:
                fails.append(f"W5 row {label}: listed in AWAITING_ISSUE but points at "
                             f"open issue {key}; remove the entry")
        elif label in awaiting:
            waits.append(f"row {label}: {problem}; awaiting: {awaiting[label]}")
        else:
            fails.append(f"row {label}: {problem}")
    for label in sorted(set(awaiting) - open_labels):
        fails.append(f"W5 row {label}: listed in AWAITING_ISSUE but is not an OPEN row; "
                     f"remove the entry")
    return fails, waits, open_rows, cited


# ---- the snapshot ---------------------------------------------------------

def fetch_issue(key, timeout=30):
    """GitHub's REST answer for `owner/repo#n`, or raises OSError."""
    repo, num = key.split("#")
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/issues/{num}",
                                 headers={"Accept": "application/vnd.github+json"})
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        req.add_header("Authorization", f"Bearer {tok}")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            d = json.load(r)
    except (urllib.error.URLError, TimeoutError, ValueError) as e:
        raise OSError(f"{key}: {e}") from e
    return {"state": d.get("state"), "state_reason": d.get("state_reason"),
            "closed_at": d.get("closed_at"), "author": (d.get("user") or {}).get("login"),
            "title": d.get("title")}


def load_snapshot(path=SNAPSHOT):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except OSError:
        return None


def refresh(text, fetch=fetch_issue, now=None):
    """A new snapshot of every issue an OPEN row cites. Raises OSError."""
    open_rows, _ = parse(text)
    keys = sorted({k for k in (row_issue(ln) for _l, ln in open_rows) if k})
    now = now or datetime.datetime.now(datetime.timezone.utc)
    return {"why": "The state of the GitHub issues the OPEN rows of "
                   "docs/did_v2_OPEN_WORK.md point at, read by "
                   "tools/check_open_work_issues.py, which runs offline. Written by "
                   "`--refresh` (network); moved deliberately and committed. "
                   "[open work lives in issues], Jess Haley, 2026-11-03.",
            "fetched_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "issues": {k: fetch(k) for k in keys}}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--refresh", action="store_true",
                    help="rewrite tools/open_work_issues.json from GitHub")
    ap.add_argument("--live", action="store_true",
                    help="also compare the snapshot with GitHub now")
    args = ap.parse_args(argv)
    with open(OPEN_WORK, encoding="utf-8") as f:
        text = f.read()

    if args.refresh:
        try:
            snap = refresh(text)
        except OSError as e:
            print(f"REFRESH FAILED, nothing written: {e}")
            return 2
        with open(SNAPSHOT, "w", encoding="utf-8") as f:
            json.dump(snap, f, indent=4, sort_keys=True)
            f.write("\n")
        print(f"wrote {os.path.relpath(SNAPSHOT, REPO)}: {len(snap['issues'])} issue(s), "
              f"fetched {snap['fetched_at']}")

    snap = load_snapshot()
    fails, waits, open_rows, cited = check(text, snap)
    print(f"DENOMINATOR: {len(open_rows)} OPEN row(s) read from docs/did_v2_OPEN_WORK.md, "
          f"{len(cited)} distinct issue(s) cited")
    if snap is None:
        print("  snapshot: tools/open_work_issues.json is missing (NOT MEASURED)")
    else:
        print(f"  snapshot: {len(snap.get('issues', {}))} issue(s), fetched "
              f"{snap.get('fetched_at')} (an issue closed after that is not seen)")
    print(f"  frozen: {len(FROZEN_OPEN)} row(s) were OPEN at the freeze; "
          f"row numbers stop at {FROZEN_MAX}")

    if args.live:
        if snap is None:
            print("LIVE: NOT CHECKED (no snapshot to compare)")
        else:
            drift, unreached = [], []
            for k in sorted(cited):
                try:
                    now = fetch_issue(k)
                except OSError as e:
                    unreached.append(str(e))
                    continue
                was = snap.get("issues", {}).get(k, {}).get("state")
                if now["state"] != was:
                    drift.append(f"{k}: snapshot {was}, GitHub {now['state']}")
            if unreached:
                print(f"LIVE: NOT CHECKED for {len(unreached)} of {len(cited)} issue(s) "
                      f"(GitHub not reached); first: {unreached[0]}")
            print(f"LIVE: {len(cited) - len(unreached)} issue(s) compared, "
                  f"{len(drift)} differ from the snapshot")
            for d in drift:
                print(f"  DIFFERS {d}")
            if drift:
                fails.append(f"LIVE: {len(drift)} issue(s) differ from the snapshot; "
                             f"run --refresh")

    for w in waits:
        print(f"  AWAITING {w}")
    for f in fails:
        print(f"  FAIL {f}")
    print(f"OPEN rows read: {len(open_rows)}; awaiting an issue: {len(waits)}; "
          f"failures: {len(fails)}")
    if not open_rows:
        print("FAIL: no OPEN row read; nothing was checked")
        return 1
    if fails:
        return 1
    print("OK: every OPEN row points at an open issue or is listed as awaiting one")
    return 0


if __name__ == "__main__":
    sys.exit(main())
