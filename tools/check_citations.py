#!/usr/bin/env python3
"""Does every `file:line` citation in the record still point at what it claims?

WHY THIS EXISTS
---------------
This project cites its evidence as `file:line`, and on 2026-08-12 that habit
was audited twice in one day. The morning sweep extracted 59 distinct citations
from `CLAUDE.md` and found THIRTEEN drifted -- the file right, the number
wrong. By evening, THREE of the thirteen repointed citations were stale AGAIN:

    coverage.py:185 -> :215,:222 (morning) -> :217,:226 (evening)
    Contents.m:348  -> :354      (morning) -> :368      (evening)
    OPEN_WORK.md row #51 at :375-383       -> :634-641  (the row MOVED)

Every one because somebody INSERTED text above the cited line. The audit's own
conclusion: *"for a file under active edit, hours is a realistic half-life, and
repointing a number does not buy you a day."* All 34 NDI-matlab citations were
exact in BOTH sweeps, because we only ever read that repository. A citation
decays at the edit rate of its target, and nothing was measuring it.

THE HARD PART IS NOT "DOES THE LINE EXIST"
------------------------------------------
Existence is nearly worthless. The worst case in the whole audit is
`Contents.m:348`, which pointed at a REAL SENTENCE ABOUT A DIFFERENT CLASS: a
reader follows it, reads something plausible, and concludes the citation was
misremembered when the underlying claim was fine. A checker that verifies the
file has 348 lines calls that a pass.

    THE RULE, stated once and in full:

    A citation VERIFIES when the cited line range still contains an ANCHOR --
    a fragment the citing text QUOTES VERBATIM -- and that anchor is
    DISTINCTIVE in the target file.

      * ANCHORS COME ONLY FROM QUOTED MATERIAL: a backticked span, a
        double-quoted or italic-quoted span, or the content of a transcript
        line (`346:%   DELIBERATELY WITHOUT A MIGRATOR...`). Bare identifiers
        from the surrounding prose are NOT anchors. That is a deliberate
        narrowing: this corpus quotes its targets constantly, and admitting
        every plausible-looking word would let one of a dozen candidates land
        inside the range by luck and call a drifted citation exact.

      * THE QUOTE MUST BE IN THE CITATION'S OWN SENTENCE. A quotation
        elsewhere in the paragraph is not evidence about this citation, in
        EITHER direction, and admitting one is not a small loosening: run
        against today's corpus it made `NDI_MATLAB` the anchor for a sentence
        about reading `origin/main`, and `depends_on` the anchor for a
        citation about `epochid.epochid` -- three fabricated drift findings,
        one of them off by a single line. The asymmetric version of the same
        idea (a distant quote may CONFIRM but not DENY) is worse still: it
        resolves doubt toward "fine", which is the bias this file's operating
        rules exist to remove.

      * DISTINCTIVE, and ASYMMETRICALLY SO. To CONFIRM, the anchor may match
        up to `CONFIRM_MAX_HITS` lines -- the hard part is that one of them
        falls inside the cited range. To DENY -- to tell a reader their
        citation is wrong -- it must live at EXACTLY ONE line and be ADJACENT
        to the citation (`DENY_MAX_HITS`, `DENY_REACH`). Tightening denial
        moves a citation into UNDECIDABLE, never into VERIFIED, so the
        asymmetry cannot resolve a doubt in favour of "fine".

      * MATCHING IS BIDIRECTIONAL CONTAINMENT on whitespace-normalised text:
        the anchor contains the line, or the line contains the anchor. Prose
        condenses -- `references.m:90` is cited beside
        `if isempty(documentId), continue;` while the file's line 90 reads
        `if isempty(documentId)`. One-way containment would call that drifted.

    AND THE FAILURE MODE IS UNDECIDABLE, NEVER A SILENT PASS. If the citing
    text quotes nothing, or quotes only fragments too common to locate, the
    citation is reported as UNDECIDABLE by name and reason. It is never counted
    as verified. A checker that resolves its doubts in favour of "fine" is the
    defect this repository has paid for four times.

WHAT IS DELIBERATE AND MUST NOT BE REPORTED AS A FAULT
------------------------------------------------------
Two properties of these citations are recorded in `CLAUDE.md` as deliberate,
and the audit calls them *"UNDER-specified in the right dimension"*:

  * `origin/main src/ndi/+ndi/+element/ensemble.m:274-276` does NOT exist in
    the NDI working tree -- it exists on `origin/main`, which is exactly what
    the sentence says. Resolution therefore falls through to the named ref, and
    such a citation is verified there and labelled, not called dead.
  * `imageDocMaker.m:121-127` and `jMeasurementFold.m:69` are cited by
    BASENAME and both files have since moved directory. A basename citation
    outlived a path change; resolution is by basename whenever the literal path
    does not exist.

THE `#nn` NOTATION COLLISION
----------------------------
`V_eta_OPEN_WORK.md` numbers its items `#nn`, and one citation was written
`V_eta_OPEN_WORK.md:51` -- indistinguishable from a line reference, landing on
unrelated prose. `CLAUDE.md` now forbids the form. A citation into a markdown
document that maintains an `#nn` item vocabulary, whose number is one of those
item ids and which does not verify as a line, is reported as a NOTATION
COLLISION rather than as drift: the number is probably right and the COLON is
wrong, and telling a reader to repoint it would be telling them to repoint
nothing.

RULE 5, FIRST AND UNCONDITIONALLY. The denominator prints before any verdict:
documents scanned, lines read, citations extracted (inline and transcript),
distinct target files, and the split into VERIFIED / DRIFTED / UNDECIDABLE /
NOTATION COLLISION / DEAD / NOT RESOLVABLE HERE. A run that extracts ZERO
citations EXITS NON-ZERO -- this repository has had a counter read clean while
inspecting nothing for two days, and "no drift" from a scan that matched no
files is that same zero.

Usage:  python3 tools/check_citations.py
        python3 tools/check_citations.py --enforce    (exit 1 on drift,
                                                       a dead file, or a
                                                       notation collision)
        python3 tools/check_citations.py --verbose    (every citation, verdict
                                                       and the anchor used)
        python3 tools/check_citations.py --document CLAUDE.md
"""

import argparse
import glob
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SCHEMA_DIR = os.path.join(REPO, "schemas")


# --------------------------------------------------------------------------
# TUNING -- every threshold in one place, each with the reason it has that value
# --------------------------------------------------------------------------

# An anchor shorter than this cannot identify a line. `value`, `epoch`, `:90`
# are not evidence of anything.
MIN_ANCHOR = 8

# Distinctiveness, and it is ASYMMETRIC ON PURPOSE.
#
# To CONFIRM, an anchor may match a handful of lines: the hard part is that one
# of them falls inside the cited range, and a quotation from the citation's own
# sentence landing there is not luck.
#
# To DENY -- to tell a reader their citation is wrong -- the anchor must live
# at EXACTLY ONE line and that line must not be the cited one. An unambiguous
# relocation, or nothing. Measured against today's corpus this is the whole
# difference between a report worth reading and one worth ignoring: at a
# two-line threshold the tool called `references.m:90`, `system.m:229`,
# `tuning_response.m:92` and `ensemble.m:274-276` drifted on the strength of
# `mustBeNonEmpty`, `getprobes` and `epochid.epochid` -- words that appear in
# the sentence without being what it claims about that line. All four are
# exact. At one line, every one of them becomes UNDECIDABLE and every true
# finding survives.
#
# THIS IS NOT A BIAS TOWARD "FINE", AND THE DIRECTION IS WHY IT IS SAFE.
# Tightening DENIAL moves a citation into UNDECIDABLE -- named, counted, never
# reported as verified. Nothing can reach VERIFIED except an anchor landing
# inside the cited range.
CONFIRM_MAX_HITS = 6
DENY_MAX_HITS = 1

# ...and DENIAL also needs the quote to be ADJACENT to the citation, not merely
# in the same sentence. `_DELETE_PHASE8` and `migrators_j/image_stack.m:248`
# share a sentence seventy-five characters apart, in different clauses; the
# first is unique in the file and lands nowhere near the second's line, so
# uniqueness alone still forged a drift finding. A transcript anchor is at
# distance 0 by construction and is unaffected.
DENY_REACH = 60

# How far either side of the citation the "sentence" reaches when no sentence
# boundary is found. Hard-wrapped prose here runs to about ninety columns, so
# 300 characters is roughly three lines each way.
SENTENCE_SPAN = 300


# --------------------------------------------------------------------------
# SIBLING CHECKOUTS -- resolved exactly the way tools/gates.py resolves them
# --------------------------------------------------------------------------

def find_repo(name, env):
    for var in (env, env + "_PATH"):
        if os.environ.get(var) is not None:
            p = os.environ[var]
            return p if p and os.path.isdir(p) else None
    for cand in (os.path.join("/home/user", name),
                 os.path.join(os.path.dirname(REPO), name)):
        if os.path.isdir(cand):
            return cand
    return None


REPOS = {
    "DID-schema": REPO,
    "DID-matlab": find_repo("DID-matlab", "DID_MATLAB"),
    "NDI-matlab": find_repo("NDI-matlab", "NDI_MATLAB"),
}

# Extensions a citation can name. Bounded on purpose: an unbounded "anything
# with a dot" pattern reads `V_eta.STATUS` and `did2.validate.silentLoss:0` as
# paths and fills the report with things that were never citations.
EXTS = ("py", "m", "md", "json", "yml", "yaml", "tsx", "ts", "js")
EXT_RE = "|".join(EXTS)


# --------------------------------------------------------------------------
# EXTRACTION
# --------------------------------------------------------------------------
# TWO FORMS, and the second is the stronger one.
#
#   INLINE      `coverage.py:217,226`, `migrators_j/image.m:156-165`
#   TRANSCRIPT  an indented evidence block that names a file and then records
#               `<lineno>:<content>` lines. The content IS the claim, so the
#               anchor is exact by construction. This is also where the corpus
#               keeps its strongest evidence -- and where a stale block is
#               most misleading, because it looks like a command someone ran.

INLINE_RE = re.compile(
    r"(?<![\w/])((?:[\w+.\-]+/)*[\w+.\-]+\.(?:" + EXT_RE + r"))"
    r":(\d+(?:-\d+)?(?:,\d+(?:-\d+)?)*)(?![\d\w])")

# A path token anywhere on a line, used to give a transcript block its target.
PATH_RE = re.compile(
    r"(?<![\w/])((?:[\w+.\-]+/)*[\w+.\-]+\.(?:" + EXT_RE + r"))(?![\w])")

TRANSCRIPT_RE = re.compile(r"^(\s{2,})(\d{1,7}):(.*)$")

# `and :499`, `-> :215`, `reads it at :130 and :141`. A line number with NO
# file names nothing this tool can resolve, and it is NOT extracted. Counted
# in the denominator instead, so "not extracted" is visible rather than a
# silent hole -- the corpus uses the form for the RIGHT-HAND side of nearly
# every repointing, which is exactly where a reader would look for a check.
BARE_LINE_REF_RE = re.compile(r"(?<![\w:/])`?:\d+(?:-\d+)?`?(?![\w:/])")

FENCE_RE = re.compile(r"^\s*(?:```|~~~)")


def norm(text):
    return re.sub(r"\s+", " ", text).strip()


def parse_spans(expr):
    """`217,226` -> [(217,217),(226,226)];  `49-56,523-526` -> two ranges."""
    spans = []
    for part in expr.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            lo, hi = part.split("-", 1)
            lo, hi = int(lo), int(hi)
            if hi < lo:
                lo, hi = hi, lo
            spans.append((lo, hi))
        else:
            spans.append((int(part), int(part)))
    return spans


class Citation:
    def __init__(self, doc, lineno, path, expr, kind, anchors, context,
                 hint_blob="", historical=False, out_of_scope=()):
        self.doc = doc                 # the citing markdown document
        self.lineno = lineno           # where the citation is written
        self.path = path               # the path as CITED
        self.expr = expr               # the raw line expression
        self.spans = parse_spans(expr)
        self.kind = kind               # "inline" | "transcript"
        # [(anchor_text, scope, distance_from_the_citation)]
        self.anchors = anchors
        self.context = context         # the citing text, for the report
        # The WHOLE surrounding unit, used only to decide which checkout the
        # citation is about. A 160-character excerpt was not enough: the
        # `Contents.m:348` correction names its repository three lines up.
        self.hint_blob = hint_blob or context
        # Quoted as the OLD, WRONG value of a citation that has since been
        # repointed. Exempt from the gate, counted and listed.
        self.historical = historical
        # `*-matlab` repositories the CITING DOCUMENT names and this container
        # does not have. Used only to keep an unresolvable citation out of the
        # DEAD bucket, with the repository named.
        self.out_of_scope = list(out_of_scope)

        self.verdict = None            # set by adjudicate()
        self.reason = ""
        self.resolved = None           # repo-relative resolved path
        self.repo = None
        self.via = "working tree"      # or "origin/main"
        self.anchor_used = None
        self.spans_confirmed = 0
        self.true_lines = []           # where the anchor DOES live, if it drifted

    @property
    def where(self):
        return f"{os.path.relpath(self.doc, REPO)}:{self.lineno}"

    @property
    def cited(self):
        return f"{self.path}:{self.expr}"

    @property
    def key(self):
        """A citation's IDENTITY is the thing it points at, not where it is
        written -- so `Contents.m:348` cited from four places is one drifted
        citation quoted four times. Both counts are reported."""
        return (self.path, self.expr)


def _blocks(lines):
    """Flatten wrapped prose into paragraph units, keeping a line map.

    Indented lines, fenced lines and table rows are ATOMIC -- joining them
    invents text nobody wrote. Returns [(text, [(char_offset, lineno)...])]."""
    out, cur, spans, pos = [], [], [], 0
    in_fence = False

    def flush():
        nonlocal cur, spans, pos
        if cur:
            out.append((" ".join(cur), spans))
        cur, spans, pos = [], [], 0

    for i, raw in enumerate(lines):
        fence = FENCE_RE.match(raw) is not None
        atomic = (in_fence or fence or raw.startswith("      ")
                  or raw.lstrip().startswith("|"))
        if fence:
            in_fence = not in_fence
        if raw.strip() == "":
            flush()
            continue
        if atomic:
            flush()
            out.append((raw.strip(), [(0, i + 1)]))
            continue
        piece = raw.strip()
        if cur:
            pos += 1
        spans.append((pos, i + 1))
        pos += len(piece)
        cur.append(piece)
    flush()
    return out


def _lineno_at(spans, offset):
    best = spans[0][1]
    for start, lineno in spans:
        if start <= offset:
            best = lineno
        else:
            break
    return best


QUOTE_RES = (
    re.compile(r"`([^`\n]{%d,})`" % MIN_ANCHOR),          # `code span`
    re.compile(r"\*\"([^\"\n]{%d,})\"\*" % MIN_ANCHOR),   # *"italic quote"*
    re.compile(r"\"([^\"\n]{%d,})\"" % MIN_ANCHOR),       # "plain quote"
)


def quoted_spans(text):
    """Every verbatim quotation in `text`, as (start, end, content)."""
    out = []
    for rx in QUOTE_RES:
        for m in rx.finditer(text):
            out.append((m.start(), m.end(), m.group(1)))
    return out


def _sentence_bounds(text, at):
    """The citation's own sentence, bounded to SENTENCE_SPAN either way."""
    lo = max(0, at - SENTENCE_SPAN)
    hi = min(len(text), at + SENTENCE_SPAN)
    left = text.rfind(". ", lo, at)
    if left != -1:
        lo = left + 2
    right = text.find(". ", at, hi)
    if right != -1:
        hi = right
    return lo, hi


def _usable_anchor(content, cited_path):
    """Reject quotations that are ABOUT the citation rather than FROM the file.

    A backticked `coverage.py:185` is the citation itself; a backticked
    `tools/coverage.py` is its name. Neither says anything about line 185."""
    c = norm(content)
    if len(c) < MIN_ANCHOR:
        return False
    if INLINE_RE.search(c):
        return False
    base = os.path.basename(cited_path)
    return not (c == base or c == cited_path)


def anchors_for(text, start, end, cited_path):
    """Quotations inside the citation's own sentence, nearest first.

    Deliberately bounded to the sentence -- see the module docstring for the
    three fabricated findings that a paragraph-wide window produced."""
    lo, hi = _sentence_bounds(text, start)
    found, seen = [], set()
    spans = sorted(quoted_spans(text),
                   key=lambda q: min(abs(q[0] - end), abs(q[1] - start)))
    for qs, qe, content in spans:
        if qs < lo or qe > hi:
            continue
        if not _usable_anchor(content, cited_path):
            continue
        n = norm(content)
        if n in seen:
            continue
        seen.add(n)
        found.append((content, "sentence",
                      min(abs(qs - end), abs(qe - start))))
    return found


# --------------------------------------------------------------------------
# QUOTED AS HISTORY -- the same problem `check_prose_counts.py` has, and the
# same house style causing it. A correction here is written as `old -> new`,
# or `(was :308)`, or "THE `Contents.m:348` CITATION IS WRONG":
#
#       coverage.py:185               -> :215 + :222
#       `universalRenames.m:628` (was `:308`)
#       `build_v_eta.py:5829` (was `:5441`)
#
# The left-hand value is load-bearing -- it records what the error was -- and
# it is WRONG ON PURPOSE. A checker that fails on every correction note is a
# checker somebody disables, so the two are told apart lexically:
#
#   (a) an ARROW within `ARROW_REACH` characters to the right, with no
#       sentence boundary in between, demotes what is on its LEFT;
#   (b) a correction cue immediately to the left -- `was`, `said`, `old`,
#       `corrected from`, `no longer` -- separated only by punctuation,
#       emphasis and brackets.
#
# DEMOTION IS NARROW BY DESIGN: when in doubt a citation stays LIVE and gets
# checked. It is also never silent -- a demoted citation is still adjudicated,
# still counted, and still listed, under QUOTED AS HISTORY.
ARROW_REACH = 60
ARROW_AHEAD_RE = re.compile(r"^[^.\n]{0,%d}?(?:->|→)" % ARROW_REACH)
_FILLER = r"[\s*_`~\"'(),.:;\[\]—–-]*"
CUE_BEFORE_RE = re.compile(
    r"(?:was|were|said|says|old|previously|formerly|no longer|until|"
    r"corrected from|instead of|rather than|stale|wrong|drifted|never|"
    r"this morning|repointed)" + _FILLER + r"$", re.IGNORECASE)


def is_historical(text, start, end):
    return bool(CUE_BEFORE_RE.search(text[:start])
                or ARROW_AHEAD_RE.match(text[end:]))


def _transcript_anchor(content):
    """The recorded content of a `NNN:` transcript line, minus its elisions.

    `[...]` and a trailing `...` mark text the author cut; the longest intact
    fragment is what can honestly be looked for."""
    parts = re.split(r"\[\s*\.\.\.\s*\]|\.\.\.", content)
    best = max((norm(p) for p in parts), key=len, default="")
    return best


def extract(doc):
    """Every citation written in one markdown document.

    Returns (citations, lines_read, transcript_lines_without_a_target)."""
    with open(doc, encoding="utf-8") as fh:
        raw_text = fh.read()
    lines = raw_text.splitlines()
    off_scope = out_of_scope_repos(raw_text)

    cites = []
    bare = 0

    # ---- INLINE, over flattened prose so a wrapped citation is reachable ---
    for text, spans in _blocks(lines):
        for m in INLINE_RE.finditer(text):
            path, expr = m.group(1), m.group(2)
            cites.append(Citation(
                doc, _lineno_at(spans, m.start()), path, expr, "inline",
                anchors_for(text, m.start(), m.end(), path),
                _excerpt(text, m.start()), hint_blob=text,
                historical=is_historical(text, m.start(), m.end()),
                out_of_scope=off_scope))
        bare += len(BARE_LINE_REF_RE.findall(text))

    # ---- TRANSCRIPT, over RAW lines, with a rolling target ----------------
    # The target is the last path named on an indented line of the current
    # indented run. Prose at column 0 ends the run: a transcript's file context
    # never survives a return to ordinary text.
    target, run, orphans = None, [], 0
    for i, raw in enumerate(lines, 1):
        indented = raw.startswith("    ") or raw.strip() == ""
        if not indented:
            target, run = None, []
            continue
        run.append(raw.strip())
        tm = TRANSCRIPT_RE.match(raw)
        if tm:
            content = tm.group(3)
            anchor = _transcript_anchor(content)
            if len(anchor) < MIN_ANCHOR:
                continue
            if target is None:
                orphans += 1
                continue
            cites.append(Citation(doc, i, target, tm.group(2), "transcript",
                                  [(anchor, "transcript", 0)], norm(raw),
                                  hint_blob=" ".join(run),
                                  out_of_scope=off_scope))
            continue
        # Not a `NNN:` line -- does it name the file the block is about?
        pm = None
        for pm in PATH_RE.finditer(raw):
            pass
        if pm:
            target = pm.group(1)

    return cites, len(lines), orphans, bare


def _excerpt(text, at, width=160):
    lo = max(0, at - width // 3)
    return ("..." if lo else "") + text[lo:lo + width]


# --------------------------------------------------------------------------
# RESOLUTION
# --------------------------------------------------------------------------
# A citation names a path that may be literal, elided (`.../+migrators_j/
# Contents.m`), repo-qualified (`DID-matlab src/...`), or a BARE BASENAME whose
# file has since moved. All four are in the corpus and all four are deliberate,
# so resolution tries them in that order and reports HOW it resolved.

def _segments(path):
    """Path segments, normalised so a citation's shorthand still matches.

    FOUR SHORTHANDS ARE IN USE AND ALL FOUR ARE DELIBERATE:
      * a repo-qualified path -- `DID-matlab/src/did/.../Contents.m`
      * an ELISION -- `.../+migrators_j/Contents.m`
      * a MATLAB package directory written without its `+` --
        `migrators_j/image_stack.m` for `+migrators_j/image_stack.m`
      * a DOTTED NAMESPACE, which is how MATLAB itself names the file:
        `ndi.fun.session.diff.m` for `+ndi/+fun/+session/diff.m`
    Left literal, the first two match nothing, the third matches the wrong file
    (`image_stack.m` exists in `+migrators_i` too, so the tool reported an
    ambiguity the citation had already resolved), and the fourth reads as a
    basename no repository contains -- five citations were reported DEAD on
    that account, and `V_eta_OPEN_WORK.md` records an earlier hand audit
    making exactly the same mistake and correcting it."""
    if "/" not in path:
        stem, dot, ext = path.rpartition(".")
        if dot and ext == "m" and "." in stem:
            path = "/".join(stem.split(".")) + ".m"
    segs = [s for s in path.split("/") if s and s != "..."]
    if segs and segs[0] in REPOS:
        segs = segs[1:]
    return [s.removeprefix("+") for s in segs]


def _basename(path):
    return _segments(path)[-1]


class Tree:
    """One checkout, indexed by suffix and by basename, working tree + ref."""

    def __init__(self, name, root):
        self.name = name
        self.root = root
        self._paths = None
        self._by_base = None
        self._ref_paths = None
        self._ref_by_base = None
        self.ref = None

    def _walk(self):
        if self._paths is not None:
            return
        paths = []
        if self.root:
            for dirpath, dirnames, names in os.walk(self.root):
                dirnames[:] = [d for d in dirnames
                               if d not in (".git", "node_modules", "__pycache__")]
                rel = os.path.relpath(dirpath, self.root)
                for n in names:
                    paths.append(n if rel == "." else os.path.join(rel, n))
        self._paths = paths
        self._by_base = {}
        for p in paths:
            self._by_base.setdefault(os.path.basename(p), []).append(p)

    def _walk_ref(self):
        """`origin/main`, because a citation may deliberately point there."""
        if self._ref_paths is not None:
            return
        self._ref_paths, self._ref_by_base = [], {}
        if not self.root:
            return
        for ref in ("origin/main", "main"):
            res = subprocess.run(
                ["git", "-C", self.root, "ls-tree", "-r", "--name-only", ref],
                capture_output=True, text=True, check=False)
            if res.returncode == 0:
                self.ref = ref
                self._ref_paths = [p for p in res.stdout.split("\n") if p]
                for p in self._ref_paths:
                    self._ref_by_base.setdefault(os.path.basename(p), []).append(p)
                return

    def has_dir(self, cited):
        """Does this checkout contain the DIRECTORY the citation names?

        The test that separates `the file was deleted` from `that repository
        is not attached here`. Matched by normalised segment suffix, so
        `+migrators_j/` answers for `migrators_j/`."""
        want = _segments(cited)[:-1]
        if not want:
            return False
        self._walk()
        for p in self._paths:
            segs = _segments(p)[:-1]
            if len(segs) >= len(want) and segs[len(segs) - len(want):] == want:
                return True
        return False

    def match(self, cited):
        """Candidate paths for a cited path, working tree first then the ref.

        Returns (paths, where) where `where` is 'working tree' or the ref."""
        self._walk()
        hits = self._suffix_hits(self._paths, self._by_base, cited)
        if hits:
            return hits, "working tree"
        self._walk_ref()
        hits = self._suffix_hits(self._ref_paths, self._ref_by_base, cited)
        if hits:
            return hits, self.ref or "origin/main"
        return [], None

    @staticmethod
    def _suffix_hits(paths, by_base, cited):
        if not paths:
            return []
        candidates = by_base.get(_basename(cited), [])
        if not candidates:
            return []
        want = _segments(cited)
        exact = [p for p in candidates if _segments(p)[-len(want):] == want]
        # A bare basename whose file has MOVED -- deliberate, per CLAUDE.md.
        return exact if exact else list(candidates)


TREES = {name: Tree(name, root) for name, root in REPOS.items()}

# Which checkout a citation is about, inferred from the path and the sentence
# around it. Over-scoping is safe: an unfound path falls through to every tree
# and an ambiguity is REPORTED, never guessed.
REPO_HINTS = (
    ("NDI-matlab", re.compile(r"NDI-matlab|src/ndi|\+ndi/|ndi_common")),
    ("DID-matlab", re.compile(r"DID-matlab|\+did2|migrators_j|src/did")),
    ("DID-schema", re.compile(r"DID-schema|schemas/|tools/|web/src")),
)


def hinted_repos(cite):
    blob = cite.path + " " + cite.hint_blob
    return [name for name, rx in REPO_HINTS if rx.search(blob)]


def read_lines(tree, path, where):
    if where == "working tree":
        full = os.path.join(tree.root, path)
        try:
            with open(full, encoding="utf-8", errors="replace") as fh:
                return fh.read().splitlines()
        except OSError:
            return None
    res = subprocess.run(["git", "-C", tree.root, "show", f"{where}:{path}"],
                         capture_output=True, text=True, check=False)
    if res.returncode != 0:
        return None
    return res.stdout.splitlines()


class Unresolved(Exception):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


def resolve(cite):
    """(tree, path, where, lines) or raise Unresolved with a NAMED reason.

    EVERY checkout is searched, not the first that answers. `syncgraph.m` is a
    real file in BOTH NDI-matlab and DID-matlab, and taking whichever came
    first in a dict graded an NDI citation against a migrator of the same name.
    A hint in the citing text (`+ndi/`, `+did2/`, `migrators_j`) breaks the
    tie; without one the citation genuinely does not say which repository it
    means, and that is REPORTED rather than guessed."""
    missing = [n for n in REPOS if not REPOS.get(n)]
    found = {}
    for name in REPOS:
        if not REPOS.get(name):
            continue
        hits, where = TREES[name].match(cite.path)
        if hits:
            found[name] = (hits, where)
    if not found:
        if missing:
            raise Unresolved("checkout(s) absent here: " + ", ".join(sorted(missing)))
        seen_dir = [n for n in REPOS
                    if REPOS.get(n) and TREES[n].has_dir(cite.path)]
        if seen_dir:
            raise Unresolved(
                "the directory it names EXISTS in " + ", ".join(sorted(seen_dir))
                + " and carries no such file")
        raise Unresolved("no checkout carries that file OR the directory it "
                         "names, so a deleted file and an unattached "
                         "repository cannot be told apart here")

    if len(found) > 1:
        hinted = [n for n in hinted_repos(cite) if n in found]
        if len(hinted) != 1:
            raise Unresolved(
                "the citation does not say which checkout: that basename "
                "exists in " + ", ".join(sorted(found)))
        found = {hinted[0]: found[hinted[0]]}

    name = next(iter(found))
    tree = TREES[name]
    hits, where = found[name]
    if len(hits) > 1:
        raise Unresolved(f"{len(hits)} files share that basename in {tree.name}: "
                         + ", ".join(sorted(hits)[:3]))
    lines = read_lines(tree, hits[0], where)
    if lines is None:
        raise Unresolved(f"{hits[0]} is unreadable in {tree.name}")
    return tree, hits[0], where, lines


# --------------------------------------------------------------------------
# THE VERDICT
# --------------------------------------------------------------------------

def anchor_hits(anchor, lines):
    """Lines matched by BIDIRECTIONAL containment on normalised text.

    Prose condenses what it quotes -- `if isempty(documentId), continue;` in
    the sentence against `if isempty(documentId)` in the file -- so a one-way
    substring test reports a live citation as drifted."""
    a = norm(anchor)
    if len(a) < MIN_ANCHOR:
        return []
    out = []
    for i, line in enumerate(lines, 1):
        n = norm(line)
        if len(n) < MIN_ANCHOR:
            continue
        if a in n or n in a:
            out.append(i)
    return out


ITEM_RE = re.compile(
    r"^\s*(?:#{1,6}\s+)?(?:[-*]\s+)?(?:\|\s*)?(?:\*\*)?#(\d{1,4})\b", re.MULTILINE)
MIN_ITEM_VOCAB = 10


def item_ids(lines):
    """`#nn` item numbers a markdown document maintains, if it maintains any."""
    ids = {int(m.group(1)) for m in ITEM_RE.finditer("\n".join(lines))}
    return ids if len(ids) >= MIN_ITEM_VOCAB else set()


def adjudicate(cite):
    """Set cite.verdict to one of:

    VERIFIED   an anchor still lives inside the cited range
    DRIFTED    the anchor lives in the file, but NOT where the citation says
    UNDECIDABLE nothing quoted is distinctive enough to locate -- REPORTED,
                never silently passed
    COLLISION  an `#nn` item number written with a colon
    DEAD       the file is not there at all
    UNRESOLVABLE-HERE  a checkout this container does not have
    """
    try:
        tree, path, where, lines = resolve(cite)
    except Unresolved as exc:
        if "absent here" in exc.reason:
            cite.verdict, cite.reason = "UNRESOLVABLE-HERE", exc.reason
        elif "carries no such file" in exc.reason:
            cite.verdict, cite.reason = "DEAD", exc.reason
        elif "cannot be told apart here" in exc.reason:
            cite.verdict = "UNRESOLVABLE-HERE"
            cite.reason = exc.reason + (
                "; this document names out-of-scope repositor(y/ies): "
                + ", ".join(cite.out_of_scope) if cite.out_of_scope else "")
        else:
            cite.verdict, cite.reason = "UNDECIDABLE", exc.reason
        return cite

    cite.repo, cite.resolved, cite.via = tree.name, path, where

    ranked = []
    for anchor, scope, dist in cite.anchors:
        hits = anchor_hits(anchor, lines)
        if not hits or len(hits) > CONFIRM_MAX_HITS:
            continue
        ranked.append((anchor, scope, hits, dist))

    if not ranked:
        cite.verdict = "UNDECIDABLE"
        cite.reason = ("the citing text quotes nothing distinctive enough to "
                       "locate in the file"
                       if cite.anchors else
                       "the citing text quotes nothing verbatim")
        _maybe_collision(cite, lines)
        return cite

    confirmed, best = 0, None
    for lo, hi in cite.spans:
        for anchor, _scope, hits, _dist in ranked:
            if any(lo <= h <= hi for h in hits):
                confirmed += 1
                best = best or (anchor, hits)
                break
    cite.spans_confirmed = confirmed
    if confirmed:
        cite.verdict = "VERIFIED"
        cite.anchor_used = best[0]
        cite.reason = f"{confirmed}/{len(cite.spans)} span(s) confirmed"
        return cite

    unambiguous = [r for r in ranked
                   if len(r[2]) <= DENY_MAX_HITS and r[3] <= DENY_REACH]
    if not unambiguous:
        cite.verdict = "UNDECIDABLE"
        cite.anchor_used = ranked[0][0]
        cite.reason = ("nothing the sentence quotes is at the cited line, and "
                       "nothing it quotes is both unique in the file and "
                       "adjacent to the citation, so where the line went "
                       "cannot be said")
        _maybe_collision(cite, lines)
        return cite

    anchor, _scope, hits, _dist = unambiguous[0]
    cite.anchor_used = anchor
    cite.true_lines = hits
    if _maybe_collision(cite, lines):
        return cite
    cite.verdict = "DRIFTED"
    cite.reason = "the quoted text is at line(s) " + ",".join(str(h) for h in hits)
    return cite


def _maybe_collision(cite, lines):
    """An `#nn` item number written as `:nn`. Not drift -- a wrong NOTATION."""
    if not cite.path.endswith(".md") or len(cite.spans) != 1:
        return False
    n = cite.spans[0][0]
    if cite.spans[0][1] != n:
        return False
    if n not in item_ids(lines):
        return False
    cite.verdict = "COLLISION"
    cite.reason = (f"`{os.path.basename(cite.path)}:{n}` -- that document "
                   f"numbers an item #{n}; a colon makes an item number look "
                   f"like a line number. Write `row #{n}`.")
    return True


# --------------------------------------------------------------------------
# THE SCAN
# --------------------------------------------------------------------------

# DEAD MEANS "WE CAN SEE THE PLACE IT SAYS TO LOOK, AND IT IS NOT THERE."
#
# Some citations point into repositories this container has never had.
# `V_eta_ngrid_family_findings.md` opens with a table naming
# `VH-Lab/NDIcalc-vis-matlab` as the source of its evidence and adds *"the
# clone is EPHEMERAL"*; four of its citations are `hartley.m`, which lives
# there. Grading those DEAD would gate this repository on a checkout nobody
# has. Grading every unresolved citation in such a document as exempt is the
# opposite error, and it is the one that costs: `CLAUDE.md` mentions three
# out-of-scope repositories in passing, so a document-wide exemption swallowed
# its ONE genuinely broken citation (`DID-matlab tools/corpus_proven.py:59-73`
# -- absent from that checkout's working tree AND from its `origin/main`).
#
# So the discriminator is the DIRECTORY, not the prose. If the cited path names
# a directory that exists in one of our checkouts, the citation says to look
# somewhere we can see, and a missing file there is DEAD. If neither the file
# nor the directory it names is anywhere -- `+ndi/+calc/+vis/` does not exist
# in NDI-matlab at all, nor does a bare `hartley.m` -- we cannot tell a deleted
# file from an unattached repository, and the citation is UNRESOLVABLE-HERE,
# with any out-of-scope repository the document names printed beside it as the
# likely reason.
OUT_OF_SCOPE_RE = re.compile(
    r"(?<![\w-])([A-Za-z0-9_.]+(?:-[A-Za-z0-9_.]+)*-matlab)(?![\w-])")


def out_of_scope_repos(text):
    names = {m.group(1) for m in OUT_OF_SCOPE_RE.finditer(text)}
    known = {k.lower() for k in REPOS}
    return sorted(n for n in names if n.lower() not in known)


def documents(only=None):
    if only:
        return [os.path.abspath(p) for p in only]
    paths = [os.path.join(REPO, "CLAUDE.md")]
    paths += sorted(glob.glob(os.path.join(SCHEMA_DIR, "*.md")))
    return [p for p in paths if os.path.exists(p)]


def run(paths):
    cites, lines_read, orphans, bare, unreadable, read = [], 0, 0, 0, [], 0
    for doc in paths:
        try:
            found, nlines, orphan, nbare = extract(doc)
        except OSError as exc:
            unreadable.append((doc, str(exc)))
            continue
        read += 1
        lines_read += nlines
        orphans += orphan
        bare += nbare
        cites.extend(found)
    for c in cites:
        adjudicate(c)
    return cites, read, lines_read, orphans, bare, unreadable


# --------------------------------------------------------------------------
# RENDER
# --------------------------------------------------------------------------

ORDER = ["VERIFIED", "DRIFTED", "COLLISION", "DEAD", "UNDECIDABLE",
         "UNRESOLVABLE-HERE"]


def render(paths, cites, read, lines_read, orphans, bare, unreadable,
           verbose=False, out=print):
    live = [c for c in cites if not c.historical]
    hist = [c for c in cites if c.historical]
    by = {v: [c for c in live if c.verdict == v] for v in ORDER}
    inline = [c for c in cites if c.kind == "inline"]
    trans = [c for c in cites if c.kind == "transcript"]
    distinct = {c.key for c in cites}

    # RULE 5. The denominator prints FIRST and UNCONDITIONALLY -- "0 drifted"
    # from a scan that matched no document is the zero `silentLoss` printed for
    # two days.
    out(f"DENOMINATOR: {len(paths)} document(s) globbed, {read} read, "
        f"{lines_read} line(s); {len(cites)} citation(s) extracted "
        f"({len(inline)} inline, {len(trans)} transcript), "
        f"{len(distinct)} distinct file+line target(s)")
    out(f"  citations into {len({c.path for c in cites})} distinct cited path(s)")
    out(f"  QUOTED AS HISTORY (an `old -> new` left side)  : {len(hist):5d}"
        f"   -- adjudicated, listed, exempt from the gate")
    out(f"  LIVE, adjudicated below                        : {len(live):5d}")
    out(f"  transcript line(s) naming no file, SKIPPED     : {orphans:5d}")
    out(f"  bare `:NNN` refs carrying no file, NOT extract.: {bare:5d}")
    for v in ORDER:
        out(f"  {v:20s} : {len(by[v]):5d}"
            f"   ({len({c.key for c in by[v]})} distinct)")
    out("")
    assert sum(len(by[v]) for v in ORDER) == len(live), \
        "a citation landed in no bucket -- a verdict was dropped"

    for doc, exc in unreadable:
        out(f"UNREADABLE: {os.path.relpath(doc, REPO)} -- {exc}")

    absent = [n for n in REPOS if not REPOS.get(n)]
    out("CHECKOUTS: " + ", ".join(
        f"{n}={'absent' if not REPOS[n] else os.path.relpath(REPOS[n], '/')}"
        for n in sorted(REPOS)))
    if absent:
        out("  citations into the absent checkout(s) are UNRESOLVABLE-HERE, "
            "named and never counted as verified.")
    refs = sorted({c.via for c in cites if c.via not in (None, "working tree")})
    if refs:
        n = len([c for c in cites if c.via in refs])
        out(f"  {n} citation(s) resolved through a git ref ({', '.join(refs)}) "
            "because the file is not in the working tree -- DELIBERATE where "
            "the sentence says `origin/main`, not a fault.")
    out("")

    for v in ("DRIFTED", "COLLISION", "DEAD"):
        if not by[v]:
            continue
        out(f"{v} -- {len(by[v])} citation(s):")
        for c in sorted(by[v], key=lambda c: (c.doc, c.lineno)):
            out(f"  {c.where}  cites {c.cited}"
                + (f"  [{c.repo}:{c.resolved}" f"@{c.via}]" if c.resolved else ""))
            out(f"      {c.reason}")
            if c.anchor_used:
                out(f"      anchor: {c.anchor_used[:110]!r}")
        out("")

    if by["UNDECIDABLE"]:
        reasons = {}
        for c in by["UNDECIDABLE"]:
            reasons.setdefault(c.reason.split(":")[0], []).append(c)
        out("UNDECIDABLE -- reported, never counted as verified:")
        for reason, rows in sorted(reasons.items(), key=lambda kv: -len(kv[1])):
            out(f"  {len(rows):5d}  {reason}")
            for c in (rows if verbose else rows[:3]):
                out(f"          {c.where}  cites {c.cited}")
            if not verbose and len(rows) > 3:
                out(f"          ... and {len(rows) - 3} more (--verbose)")
        out("")

    if by["UNRESOLVABLE-HERE"]:
        out(f"UNRESOLVABLE HERE -- {len(by['UNRESOLVABLE-HERE'])} citation(s); "
            "a gap in this container, not a defect in the prose:")
        for c in sorted(by["UNRESOLVABLE-HERE"], key=lambda c: c.cited)[:10]:
            out(f"  {c.where}  cites {c.cited}  -- {c.reason}")
        out("")

    if hist:
        stale = [c for c in hist if c.verdict in ("DRIFTED", "DEAD", "COLLISION")]
        out(f"QUOTED AS HISTORY -- {len(hist)} citation(s) written as the OLD, "
            f"wrong side of a correction. Exempt; {len(stale)} of them do "
            "adjudicate as wrong, which is what makes them correction notes:")
        for c in sorted(hist, key=lambda c: (c.doc, c.lineno))[:20 if not verbose else None]:
            out(f"  {c.where}  cites {c.cited}  -> {c.verdict}")
        if not verbose and len(hist) > 20:
            out(f"  ... and {len(hist) - 20} more (--verbose)")
        out("")

    if verbose:
        out("EVERY CITATION:")
        for c in sorted(cites, key=lambda c: (c.doc, c.lineno)):
            out(f"  {c.where:52s} {c.cited:46s} {c.verdict:18s} "
                f"{'history' if c.historical else 'live':8s} "
                f"{c.kind:10s} {c.reason[:70]}")
        out("")

    if not by["DRIFTED"] and not by["DEAD"] and not by["COLLISION"]:
        out("No citation points at a line that no longer carries what the "
            "citing text quotes.")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--enforce", action="store_true",
                    help="exit non-zero when a citation has drifted, is dead, "
                         "or is an item number written as a line number")
    ap.add_argument("--verbose", action="store_true",
                    help="print every citation with its verdict and anchor")
    ap.add_argument("--document", action="append", default=None,
                    help="scan only this markdown document (repeatable)")
    args = ap.parse_args(argv)

    paths = documents(args.document)
    cites, read, lines_read, orphans, bare, unreadable = run(paths)
    render(paths, cites, read, lines_read, orphans, bare, unreadable, args.verbose)

    if read == 0 or not cites:
        print()
        print("NOTHING WAS EXTRACTED -- the scan located no `file:line` "
              "citation. That is a FAILURE, not a pass: a checker that reads "
              "nothing prints the same clean zero as a checker that finds "
              "nothing wrong.")
        return 1

    bad = [c for c in cites
           if not c.historical and c.verdict in ("DRIFTED", "DEAD", "COLLISION")]
    return 1 if (bad and args.enforce) else 0


if __name__ == "__main__":
    sys.exit(main())
