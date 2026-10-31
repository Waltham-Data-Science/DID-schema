#!/usr/bin/env python3
"""The sibling lock: the exact NDI-matlab / DID-matlab / NDIcalc-vis-matlab
commits this repository is built and checked against.

    python3 tools/sibling_lock.py            print the lock (same as --show)
    python3 tools/sibling_lock.py --check    verify the sibling checkouts
                                             against the lock; exit 1 on any
                                             mismatch, with the command to fix it
    python3 tools/sibling_lock.py --update   record the siblings' current HEAD
                                             and origin/main into the lock
    python3 tools/sibling_lock.py --get NDI-matlab head
                                             print one locked sha (CI uses it)

NDIcalc-vis-matlab, THE THIRD SIBLING. Jess Haley's decision of 2026-10-27,
`did_v2_go_forward_class_audit.md` [lock NDIcalc-vis-matlab]: it joins the lock,
pinned at the commit the tuning templates are read from (00e3e0f), so a tuning
template cannot change under did-schema unnoticed. It has no V2 line: the
templates are read from its `main`, so its `head` and `main` are the same
commit and `head_ref` is `main`. No tool in this repository reads its files
yet; the lock records it, `--check` verifies a present checkout
($NDICALC_VIS_MATLAB, then /home/user, then ../) and reports an absent one NOT
CHECKED, like the other two. A future reader of its templates reads the locked
`main` through `main_refs("NDIcalc-vis-matlab")`.

WHY. The chain (`tools/gates.py`) regenerates committed artifacts and runs gates
against two sibling repositories: their working trees, and NDI-matlab's
`origin/main` (the v1 truth `coverage.py`, `ndi_ground_truth.py` and
`check_prose_counts.py` read). Those refs move without any change here. Twice on
2026-10-23 NDI `origin/main` gained `.m` files (1,300 -> 1,305 -> 1,307), which
turned `check_prose_counts` red and changed generated files, forcing drift-fix
commits unrelated to any did-schema change (dc650e8, 5cba5a4). Decided by Jess
Haley, 2026-10-23, in conversation: lock the exact sibling commits in a
committed file, and build and check against those. Moving the lock is a
deliberate commit (`--update`, then `tools/gates.py`, then commit both).

THE LOCK FILE, `tools/sibling_lock.json`, holds per sibling:
  head   -- the commit the sibling's WORKING TREE must be at;
  main   -- the commit every read of that sibling's `origin/main` reads instead;
  head_ref / url -- where `head` came from and where CI clones it (information).

HOW IT IS ENFORCED -- one mechanism, VERIFY, not materialise:
  * `main` is read by every tool that used to read `origin/main`, through
    `main_refs()` below: the tool asks git for the locked sha itself, so the
    answer does not depend on when the clone was last fetched.
  * `head` is VERIFIED, never checked out for you. `gates.py` prints the lock
    first and refuses to run when a present sibling's HEAD differs, naming the
    `git checkout` that fixes it. A worktree materialised at the locked sha
    would mean writing into another repository's `.git` on every run, and this
    project's sibling checkouts are shared by agents (CLAUDE.md, "One working
    copy per agent"); a check that only reads cannot disturb one.
  * CI checks out exactly `head` (`--get`), so there the check is a formality
    that proves the checkout step did what it says.

A MISSING OR STALE LOCK IS REPORTED, NEVER IGNORED. No lock file: `--check`
and `gates.py` fail. Without a lock `main_refs()` falls back to
`origin/main` then `main` -- the pre-lock behaviour -- so a tool run outside the
chain still answers, and the chain is what refuses.

`$DID_SCHEMA_SIBLING_LOCK` names another lock file (tests use it). Set to an
empty string it means "no lock".
"""

import argparse
import datetime
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
LOCK_PATH = os.path.join(HERE, "sibling_lock.json")
ENV = "DID_SCHEMA_SIBLING_LOCK"

# name -> (environment variable, clone url). Every sibling the lock covers; the
# chain's steps read the first two, NDIcalc-vis-matlab is locked and verified.
SIBLINGS = {
    "NDI-matlab": ("NDI_MATLAB", "https://github.com/VH-Lab/NDI-matlab.git"),
    "DID-matlab": ("DID_MATLAB", "https://github.com/VH-Lab/DID-matlab.git"),
    "NDIcalc-vis-matlab": ("NDICALC_VIS_MATLAB",
                           "https://github.com/VH-Lab/NDIcalc-vis-matlab.git"),
}

DEFAULT_WHY = (
    "The chain regenerates committed artifacts against NDI-matlab and "
    "DID-matlab. Their refs move without any change here (NDI origin/main "
    "gained .m files twice on 2026-10-23), so the chain builds and checks "
    "against these exact commits. Moving them is a deliberate commit "
    "(tools/sibling_lock.py --update). Decided by Jess Haley, 2026-10-23, "
    "in conversation.")


class LockError(Exception):
    """The lock file exists but cannot be used."""


def lock_path():
    """The lock file in use: `$DID_SCHEMA_SIBLING_LOCK` if set, else the
    committed one. An empty value means no lock (returns None)."""
    p = os.environ.get(ENV)
    if p is None:
        return LOCK_PATH
    return p or None


def load(path=None):
    """The lock as a dict, or None when there is no lock file.

    A file that exists but is malformed raises LockError: an unreadable lock is
    not the same fact as an absent one."""
    path = path if path is not None else lock_path()
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            lk = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        raise LockError(f"{path}: {exc}") from exc
    sib = lk.get("siblings") if isinstance(lk, dict) else None
    if not isinstance(sib, dict) or not sib:
        raise LockError(f"{path}: no `siblings` map")
    for name, rec in sib.items():
        for key in ("head", "main"):
            v = rec.get(key) if isinstance(rec, dict) else None
            if not (isinstance(v, str) and len(v) == 40
                    and all(c in "0123456789abcdef" for c in v)):
                raise LockError(f"{path}: {name}.{key} is not a full sha: {v!r}")
    return lk


def main_refs(name, path=None):
    """The candidates for reading sibling `name`'s main, as (label, rev) pairs.

    `label` is what a tool WRITES (it stays `origin/main`, so artifacts do not
    churn with the sha); `rev` is what it passes to git. With a lock there is
    exactly one candidate, the locked sha, and NO fallback: a locked commit the
    clone does not hold is a failure to report, not a reason to read something
    else. Without a lock: the pre-lock order, origin/main then main."""
    try:
        lk = load(path)
    except LockError:
        lk = None
    rec = (lk or {}).get("siblings", {}).get(name)
    if rec:
        return [("origin/main", rec["main"])]
    return [("origin/main", "origin/main"), ("main", "main")]


def find_repo(name, env):
    """The sibling checkout, resolved exactly as tools/gates.py resolves it:
    an explicitly SET variable is authoritative, then /home/user, then ../."""
    for var in (env, env + "_PATH"):
        if os.environ.get(var) is not None:
            p = os.environ[var]
            return p if p and os.path.isdir(p) else None
    for cand in (os.path.join("/home/user", name),
                 os.path.join(os.path.dirname(REPO), name)):
        if os.path.isdir(cand):
            return cand
    return None


def _git(path, *args):
    r = subprocess.run(["git", "-C", path] + list(args),
                       capture_output=True, text=True, check=False)
    return r.stdout.strip() if r.returncode == 0 else None


def _has_commit(path, sha):
    return _git(path, "cat-file", "-e", f"{sha}^{{commit}}") is not None


def verify(paths=None, path=None, out=print):
    """Print the lock and check each present sibling against it.

    Returns the number of problems. Rule 5: the denominator first -- how many
    siblings are locked, and which commits are being measured. An ABSENT
    sibling is reported NOT CHECKED (the chain reports its steps NOT RUNNABLE);
    it is neither a pass nor a failure of the lock."""
    shown = lock_path() if path is None else path
    try:
        lk = load(path)
    except LockError as exc:
        out(f"SIBLING LOCK: UNREADABLE -- {exc}")
        return 1
    if lk is None:
        out(f"SIBLING LOCK: MISSING ({shown or 'disabled by $' + ENV}) -- every "
            "sibling read is UNLOCKED, so the artifacts depend on when the "
            "siblings were last fetched.")
        out("  fix: python3 tools/sibling_lock.py --update   (then commit "
            "tools/sibling_lock.json)")
        return 1
    if paths is None:
        paths = {n: find_repo(n, env) for n, (env, _url) in SIBLINGS.items()}
    sib = lk["siblings"]
    out(f"SIBLING LOCK: {os.path.relpath(shown, REPO) if os.path.isabs(shown) else shown} "
        f"(dated {lk.get('date', '?')})")
    out(f"  DENOMINATOR: {len(sib)} sibling(s) locked; measured commits below")
    bad = 0
    for name in sorted(sib):
        rec = sib[name]
        p = paths.get(name)
        out(f"  {name:<18} head {rec['head'][:12]} ({rec.get('head_ref', '?')})  "
            f"main {rec['main'][:12]}  at {p or 'NOT FOUND'}")
        if not p:
            out(f"    NOT CHECKED: no {name} checkout here")
            continue
        head = _git(p, "rev-parse", "HEAD")
        if head != rec["head"]:
            bad += 1
            out(f"    *** HEAD MISMATCH: checkout is at {head or '?'}, the lock "
                f"says {rec['head']}.")
            out(f"    fix: git -C {p} fetch origin && git -C {p} checkout "
                f"--detach {rec['head']}")
            out("    or, to MOVE the lock deliberately: python3 "
                "tools/sibling_lock.py --update, regenerate, commit both.")
        if not _has_commit(p, rec["main"]):
            bad += 1
            out(f"    *** LOCKED MAIN {rec['main']} IS NOT IN THIS CLONE; every "
                "origin/main read would fail.")
            out(f"    fix: git -C {p} fetch origin")
        else:
            cur = _git(p, "rev-parse", "--verify", "-q", "origin/main")
            if cur and cur != rec["main"]:
                ahead = _git(p, "rev-list", "--count", f"{rec['main']}..{cur}")
                out(f"    note: origin/main is now {cur[:12]} ({ahead or '?'} commit(s) "
                    "past the lock). Not read; moving the lock is a deliberate commit.")
    out(f"  SIBLING LOCK: {bad} problem(s)")
    return bad


def update(paths=None, path=None, today=None, out=print):
    """Record each present sibling's HEAD and origin/main. A sibling that is
    absent keeps its existing entry (named as kept), so an update on a machine
    missing one checkout cannot silently drop it."""
    path = path or lock_path() or LOCK_PATH
    try:
        old = load(path) or {}
    except LockError:
        old = {}
    if paths is None:
        paths = {n: find_repo(n, env) for n, (env, _url) in SIBLINGS.items()}
    sib = dict(old.get("siblings", {}))
    rc = 0
    for name, (_env, url) in SIBLINGS.items():
        p = paths.get(name)
        if not p:
            out(f"  {name}: NOT FOUND -- {'kept the existing entry' if name in sib else 'NOT LOCKED'}")
            rc = rc if name in sib else 1
            continue
        head = _git(p, "rev-parse", "HEAD")
        main = (_git(p, "rev-parse", "--verify", "-q", "origin/main")
                or _git(p, "rev-parse", "--verify", "-q", "main"))
        ref = _git(p, "rev-parse", "--abbrev-ref", "HEAD")
        if not head or not main:
            out(f"  {name}: cannot resolve HEAD or origin/main in {p}")
            rc = 1
            continue
        sib[name] = {"url": url, "head_ref": ref if ref and ref != "HEAD"
                     else sib.get(name, {}).get("head_ref", "detached"),
                     "head": head, "main": main}
        out(f"  {name}: head {head} ({sib[name]['head_ref']}), main {main}")
    doc = {
        "why": old.get("why") or DEFAULT_WHY,
        "date": today or datetime.datetime.now(datetime.timezone.utc).date().isoformat(),
        "siblings": {n: sib[n] for n in sorted(sib)},
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=4)
        fh.write("\n")
    out(f"wrote {path}")
    return rc


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--check", action="store_true")
    g.add_argument("--update", action="store_true")
    g.add_argument("--show", action="store_true")
    g.add_argument("--get", nargs=2, metavar=("SIBLING", "FIELD"))
    a = ap.parse_args(argv)
    if a.get:
        try:
            lk = load()
        except LockError as exc:
            sys.exit(f"sibling lock unreadable: {exc}")
        if lk is None:
            sys.exit("no sibling lock (tools/sibling_lock.json)")
        try:
            print(lk["siblings"][a.get[0]][a.get[1]])
        except KeyError:
            sys.exit(f"the lock has no {a.get[0]}.{a.get[1]}")
        return 0
    if a.update:
        return update()
    bad = verify()
    return 1 if (bad and a.check) else 0


if __name__ == "__main__":
    sys.exit(main())
