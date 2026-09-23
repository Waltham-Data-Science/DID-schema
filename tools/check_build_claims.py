#!/usr/bin/env python3
"""Does a CODE COMMENT assert a build state the signed record contradicts?

WHY THIS EXISTS
---------------
`check_signoff_header_staleness.py` polices build claims in the tail of a
`TEAM-SIGN-OFF` line (its rule 3). Every claim it can see lives in a markdown
document in THIS repository. The five defects that prompted this tool all lived
somewhere else entirely -- in MATLAB comments, in the sibling repositories:

  * `pyraview.m` said the `epoch_id` edge "needs a schema increment and belongs
    with the epoch family (#60)". TEAM-SIGN-OFF [epoch] FORBIDS that edge on a
    `subject_interaction` descendant. Acting on the comment would have built
    the one thing the signature rules out.
  * `pyraview.m` said the epoch-extent half was "signed and NOT YET BUILT".
    `epochMint.py`'s `epochExtentReferences` had been minting it for days.
  * `element_epoch.m` labelled two of its four dissolution targets `UNSIGNED`
    -- #45 (data_body) and #30 (raw recording observation) -- and concluded
    that dissolving "would strand the payload". Both had been signed for days.
    That comment is the STATED REASON the dissolution has not been built.
  * `daqreader_epochdata_ingested.m` said "#30, NOT BUILT" where #30's
    assembler is live at `element.m:118`.
  * `jRecordingObservation.m` QUOTED that sibling comment as its evidence.

The last one is the shape worth naming: a wrong sentence in one file became a
citation in another, and a reader checking the citation found it faithful.

WHAT IT CHECKS, AND WHAT IT REFUSES TO
--------------------------------------
Two rules, and BOTH FIRE ONLY ON POSITIVE EVIDENCE (Operating Rule 3). A claim
the record neither confirms nor contradicts is UNDECIDABLE and is counted, never
failed. "Nobody looked" stays a third state.

  RULE A -- SIGNEDNESS. ON ONE LINE, a comment asserts something is UNSIGNED /
  not signed, and either names a plan document that carries a `TEAM-SIGN-OFF`
  line, or LABELS a `#nn` whose committed row names such a document. The
  signature EXISTS: that is positive evidence, not an absence argument.

  Both halves are deliberately narrow, and each width was set by a false
  positive it had to exclude -- see `signature_index` (why a family NAME is not
  evidence), and the adjacency note in the adjudication loop (why a `#nn` in a
  subordinate clause is not evidence). The tool errs toward UNDECIDABLE.

  RULE B -- COMPLETEDNESS. A comment asserts `#nn` is NOT BUILT, and
  `V_eta_OPEN_WORK.md` lists row #nn under `## COMPLETED`.

WHAT IT DOES NOT DO, DELIBERATELY: it never decides whether something is built.
No artifact in these repositories answers that per comment, and inventing an
inference would repeat the governance-in-the-completion-chain error -- reporting
bookkeeping as progress. A `NOT BUILT` claim about an item still filed under
`## OPEN` is left alone, because the record agrees with it.

THAT LIMIT IS LOAD-BEARING AND COST ONE OF THE FIVE. `#30` is signed twice, its
assembler is live, and its row is STILL under `## OPEN` -- so rule B cannot see
the three "#30, NOT BUILT" comments, and only rule A reaches the ones that name
the plan. The record understating progress is a documented, recurring condition
here; a checker built on it would inherit the lag. Rule A is the stronger of the
two for exactly that reason: a signature is appended once and never retracted.

RULE C is REPORT-ONLY and never fails: a build claim whose surrounding window
quotes a `.m` path is CITING A COMMENT AS EVIDENCE. That is not wrong on its
face -- `jRecordingObservation.m` was quoting a real sibling -- so it is
surfaced as a count rather than a verdict.

EXEMPTION
---------
A correction note that REPRODUCES the stale wording as history is exempt when

    HISTORICAL-BUILD-CLAIM

appears on the line or within two either side. `HISTORICAL-SIGNOFF-CLAIM` is
honored too, since the two overlap and it is already in use across both
repositories.

Usage:  python3 tools/check_build_claims.py
        python3 tools/check_build_claims.py --enforce
"""

import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SCHEMA_DIR = os.path.join(REPO, "schemas")
OPEN_WORK = os.path.join(SCHEMA_DIR, "V_eta_OPEN_WORK.md")

EXEMPT = ("HISTORICAL-BUILD-CLAIM", "HISTORICAL-SIGNOFF-CLAIM")
WINDOW = 2
# Max characters between an `UNSIGNED` token and the `#nn` it labels. See the
# adjacency note in the adjudication loop for the false positive this excludes.
ITEM_ADJACENCY = 15

# The comment trees that are scanned. Both siblings, because the defect crossed
# the boundary in both directions and a one-repo sweep would have found 3 of 5.
SCAN_ROOTS = [
    ("DID-matlab", os.path.join("src", "did", "+did2", "+convert")),
    ("NDI-matlab", os.path.join("src", "ndi", "+ndi", "+migrate")),
]

SIGNOFF_RE = re.compile(r"^TEAM-SIGN-OFF\s*\[([^\]]+)\]")
# GOVERNANCE VOCABULARY ONLY. A first draft also matched bare "no signature",
# which fired on `resolveLawnPlateSubjects.m` ("matched no signature" -- a TABLE
# signature) and on function signatures. The word is not owned by this project.
UNSIGNED_RE = re.compile(
    r"\bUNSIGNED\b|\bnot\s+signed\b|\bno\s+`?TEAM[\s_-]*SIGN[\s_-]*OFF`?\b",
    re.IGNORECASE)
NOTBUILT_RE = re.compile(r"\bnot\s+(?:yet\s+)?built\b", re.IGNORECASE)
ITEM_RE = re.compile(r"#(\d{1,3})\b")
PLAN_RE = re.compile(r"\b(V_eta_[A-Za-z0-9_]+\.md)\b")
MFILE_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\.m\b")


def _norm(s):
    """Lowercase and strip separators, so `data_body` matches `data body`."""
    return re.sub(r"[^a-z0-9]", "", s.lower())


def find_repo(name):
    for cand in (os.environ.get(name.upper().replace("-", "_")),
                 os.path.join("/home/user", name),
                 os.path.join(os.path.dirname(REPO), name)):
        if cand and os.path.isdir(cand):
            return cand
    return None


def signature_index():
    """(signature names, plan documents carrying >=1 signature).

    Read from the documents themselves rather than from V_eta_decisions.json:
    the generated artifact groups by FAMILY, and a comment names whatever it
    names.

    THE NAME INDEX IS BUILT AND THEN USED ONLY FOR REPORTING. A first draft
    adjudicated on it -- if a normalised signature name appeared anywhere in the
    window, the claim was contradicted -- and 7 of its 10 hits were false. The
    cause is that signature names are ORDINARY WORDS in the files being scanned:
    `epoch` matched every line of `epochMint.m` that mentioned an epoch, which
    is most of them, and `session` matched a sentence about table signatures.
    A gate crying wolf trains its readers to bump digits without looking, which
    is how a real drift gets bumped away too. Adjudication now requires a PLAN
    FILENAME, which no file mentions by accident."""
    names, plans = {}, {}
    read = 0
    for fn in sorted(os.listdir(SCHEMA_DIR)):
        if not fn.endswith(".md"):
            continue
        path = os.path.join(SCHEMA_DIR, fn)
        try:
            with open(path, encoding="utf-8") as fh:
                lines = fh.read().splitlines()
        except OSError:
            continue
        read += 1
        for ln in lines:
            m = SIGNOFF_RE.match(ln)
            if not m:
                continue
            raw = m.group(1).split("--")[0].strip()
            key = _norm(raw)
            if len(key) >= 4:        # `epoch` yes; a 1-3 char token matches noise
                names.setdefault(key, (raw, fn))
            plans.setdefault(fn, 0)
            plans[fn] += 1
    return names, plans, read


def open_work_rows():
    """(item -> 'OPEN'|'COMPLETED', item -> plan documents named in its row).

    The second map is what lets a comment saying only `#45, UNSIGNED` be
    adjudicated at all: the number is opaque, its COMMITTED row is not."""
    rows = {}
    plans_for = {}
    section = None
    try:
        with open(OPEN_WORK, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError:
        return rows, plans_for, 0
    for ln in lines:
        if ln.startswith("## OPEN"):
            section = "OPEN"
            continue
        if ln.startswith("## COMPLETED"):
            section = "COMPLETED"
            continue
        if ln.startswith("## "):
            section = None
            continue
        m = re.match(r"\|\s*(\d+)\s*\|", ln)
        if m and section:
            num = int(m.group(1))
            rows.setdefault(num, section)
            plans_for.setdefault(num, sorted(set(PLAN_RE.findall(ln))))
    return rows, plans_for, len(lines)


def comment_lines(path):
    """(1-indexed lineno, text) for MATLAB comment lines only."""
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            raw = fh.read().splitlines()
    except OSError:
        return [], []
    out = [(i + 1, ln) for i, ln in enumerate(raw) if ln.lstrip().startswith("%")]
    return out, raw


def scan():
    sig_names, sig_plans, docs_read = signature_index()
    rows, item_plans, ow_lines = open_work_rows()

    files = 0
    comments = 0
    claims = []
    missing_repos = []

    for repo_name, subpath in SCAN_ROOTS:
        root = find_repo(repo_name)
        if root is None:
            missing_repos.append(repo_name)
            continue
        base = os.path.join(root, subpath)
        if not os.path.isdir(base):
            missing_repos.append(f"{repo_name}/{subpath}")
            continue
        for dirpath, _dirs, fnames in os.walk(base):
            for fn in sorted(fnames):
                if not fn.endswith(".m"):
                    continue
                path = os.path.join(dirpath, fn)
                files += 1
                cl, raw = comment_lines(path)
                comments += len(cl)
                for lineno, text in cl:
                    is_unsigned = bool(UNSIGNED_RE.search(text))
                    is_notbuilt = bool(NOTBUILT_RE.search(text))
                    if not (is_unsigned or is_notbuilt):
                        continue
                    lo = max(0, lineno - 1 - WINDOW)
                    hi = min(len(raw), lineno + WINDOW)
                    window = raw[lo:hi]
                    if any(mk in w for w in window for mk in EXEMPT):
                        continue
                    claims.append({
                        "repo": repo_name, "path": path, "lineno": lineno,
                        "text": text.strip(), "window": window,
                        "unsigned": is_unsigned, "notbuilt": is_notbuilt})

    # --- adjudicate, positive evidence only -------------------------------
    #
    # SAME LINE ONLY, not the +-2 window. The window is used for the exemption
    # marker and for RULE C, never for evidence. A first draft adjudicated over
    # the window and manufactured two false positives that way: a paragraph
    # saying "No TEAM-SIGN-OFF line exists for <X>" was convicted because an
    # unrelated plan filename sat two lines below it. Proximity is not aboutness.
    contradicted, undecidable, cites_comment = [], [], []
    for c in claims:
        line = c["text"]
        verdicts = []

        if c["unsigned"]:
            # (a) the claim names a plan document that carries a signature.
            for plan in PLAN_RE.findall(line):
                if sig_plans.get(plan) and plan != os.path.basename(OPEN_WORK):
                    verdicts.append(
                        f"RULE A: names {plan}, which carries "
                        f"{sig_plans[plan]} TEAM-SIGN-OFF line(s)")
            # (b) the claim LABELS #nn unsigned, and #nn's COMMITTED row names a
            #     signed plan. This is the path that reaches `#45, UNSIGNED` --
            #     the comment names only a number, and the number is resolvable.
            #
            #     ADJACENCY IS REQUIRED, and it is not decoration. `#nn,
            #     UNSIGNED` is a LABELLING idiom: the number is the subject. A
            #     number in a subordinate clause is not. Without this,
            #     `element_epoch.m:89` -- "fork A1 for it is chosen but NOT
            #     SIGNED, and is gated on #30 besides" -- was convicted for a
            #     claim about fork A1, on the strength of a #30 twenty-eight
            #     characters away in a different clause. Co-occurrence on one
            #     line is not aboutness any more than proximity across lines is.
            for m in UNSIGNED_RE.finditer(line):
                for im in ITEM_RE.finditer(line):
                    gap = (im.start() - m.end()) if im.start() >= m.end() \
                        else (m.start() - im.end())
                    if gap > ITEM_ADJACENCY:
                        continue
                    num = im.group(1)
                    for plan in item_plans.get(int(num), ()):
                        if sig_plans.get(plan):
                            verdicts.append(
                                f"RULE A: #{num} is labelled unsigned {gap} "
                                f"char(s) away; its row in V_eta_OPEN_WORK.md "
                                f"names {plan}, which carries "
                                f"{sig_plans[plan]} TEAM-SIGN-OFF line(s)")

        if c["notbuilt"]:
            for num in ITEM_RE.findall(line):
                if rows.get(int(num)) == "COMPLETED":
                    verdicts.append(
                        f"RULE B: #{num} is under `## COMPLETED` in "
                        "V_eta_OPEN_WORK.md")

        if MFILE_RE.search(" ".join(c["window"])):
            cites_comment.append(c)

        if verdicts:
            c["verdicts"] = sorted(set(verdicts))
            contradicted.append(c)
        else:
            undecidable.append(c)

    return {"files": files, "comments": comments, "claims": claims,
            "contradicted": contradicted, "undecidable": undecidable,
            "cites_comment": cites_comment, "docs_read": docs_read,
            "signatures": len(sig_names), "signed_plans": len(sig_plans),
            "rows": rows, "ow_lines": ow_lines, "missing_repos": missing_repos}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--enforce", action="store_true",
                    help="exit non-zero when the record contradicts a comment")
    args = ap.parse_args()

    r = scan()

    # DENOMINATOR FIRST, unconditionally (Operating Rule 5). "0 contradicted" is
    # meaningless without how many comment lines were read and how big the
    # signature index is -- a sweep that walked no files, or one whose signature
    # index came back empty, would print the same reassuring zero.
    print(f'DENOMINATOR: {r["files"]} .m file(s) walked across '
          f'{len(SCAN_ROOTS)} sibling comment tree(s), '
          f'{r["comments"]} comment line(s) read')
    print(f'             signature index: {r["signatures"]} distinct '
          f'TEAM-SIGN-OFF name(s) over {r["signed_plans"]} document(s), '
          f'from {r["docs_read"]} markdown file(s) under schemas/')
    n_open = sum(1 for v in r["rows"].values() if v == "OPEN")
    n_done = sum(1 for v in r["rows"].values() if v == "COMPLETED")
    print(f'             item index: {len(r["rows"])} numbered row(s) '
          f'({n_open} OPEN, {n_done} COMPLETED) from V_eta_OPEN_WORK.md '
          f'({r["ow_lines"]} lines)')
    print()

    if r["missing_repos"]:
        # NOT a pass. A sibling that is absent means the sweep read less than it
        # claims to, and this tool refuses to report a smaller universe quietly
        # -- the find_repo failure recorded in CLAUDE.md.
        print("UNREADABLE -- these comment trees were NOT scanned, so this run "
              "covers less than it says:")
        for m in r["missing_repos"]:
            print(f"  {m}")
        print("This is a failure, not a pass.")
        return 1
    if r["files"] == 0 or r["signatures"] == 0:
        print("NOTHING WAS READ (0 files, or an empty signature index). "
              "This is a failure, not a pass.")
        return 1

    print(f'BUILD-STATE CLAIMS LOCATED: {len(r["claims"])}')
    print(f'  CONTRADICTED by the signed record : {len(r["contradicted"])}')
    print(f'  UNDECIDABLE (record is silent)    : {len(r["undecidable"])}'
          '   <- never a failure; "nobody looked" is a third state')
    print(f'  citing a .m file as evidence      : {len(r["cites_comment"])}'
          '   <- RULE C, report-only')
    print()

    if r["cites_comment"]:
        print("RULE C -- a build claim whose window quotes a .m path. Not "
              "wrong on its face; surfaced so the practice stays visible:")
        for c in r["cites_comment"]:
            print(f'  {os.path.relpath(c["path"], os.path.dirname(REPO))}:{c["lineno"]}')
        print()

    if not r["contradicted"]:
        print(f'No comment asserts a build state the signed record contradicts. '
              f'({len(r["claims"])} claim(s) checked)')
        return 0

    print("CONTRADICTED -- the comment says one thing and the signed record "
          "says another:")
    for c in r["contradicted"]:
        print(f'  {os.path.relpath(c["path"], os.path.dirname(REPO))}:{c["lineno"]}')
        print(f'      {c["text"][:150]}')
        for v in c["verdicts"]:
            print(f'        {v}')
    print()
    print("FIX: correct the comment BESIDE the claim, quoting the signature. Do")
    print("     not delete the old wording -- mark it HISTORICAL-BUILD-CLAIM so")
    print("     the next reader sees what was believed and why it was wrong.")
    print("     A comment is never evidence about a decision; the signature is.")
    return 1 if args.enforce else 0


if __name__ == "__main__":
    sys.exit(main())
