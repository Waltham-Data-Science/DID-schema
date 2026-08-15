#!/usr/bin/env python3
"""Does the prose still contain the numbers the tree actually holds?

WHY THIS EXISTS
---------------
This project's most expensive recurring defect is not a wrong schema. It is:
a fact lives in code or in a generated artifact, a NUMBER ABOUT that fact lives
in prose, and the prose drifts. On 2026-08-12 alone two hand sweeps corrected
roughly twenty numeric claims across `CLAUDE.md` and `schemas/V_eta_OPEN_WORK.md`
-- 224 vs 241 V_eta class names, 38 vs 41 `data_type` subclasses, 34 vs 38
registry rows, 8 vs 14 vs 13 bound fields, 17 vs 15 phase-8 deletions, 60 vs 67
tombstones compared, 45 vs 46 `time_reference` sites, 915 vs 1,002 NDI files.
Every one was found by a human or an agent reading carefully. NONE was found by
a machine, and several went stale again within hours: the gates step count was
rewritten three times in two days (16, then 18, then 19), each revision true for
about a day, and the note fixing it was stale before it was committed.

The response there was to forbid typing that number at all and tell the reader
to run `--explain | head -1`. That instinct is right. This tool generalises it:
for a bounded vocabulary of countable things, it DERIVES the number itself and
asks whether the prose still carries it.

THE CENTRAL DESIGN PROBLEM -- these documents quote wrong numbers ON PURPOSE
---------------------------------------------------------------------------
The house style for a correction is to write BOTH numbers:

    the registry is **38 rows, not 34**
    `data_type` now has **41** direct subclasses, not 38
    (**15 deleted** -- this line said 17 until 2026-08-10)

The wrong number is load-bearing: it records what the error was and what it
cost. A checker that fails on every correction note is a checker that gets
disabled, so ASSERTED and QUOTED-AS-HISTORY must be told apart.

`tools/check_signoff_header_staleness.py` solved its version of this with an
opt-in marker (`HISTORICAL-SIGNOFF-CLAIM`). THAT MECHANISM IS NOT AVAILABLE
HERE, and the reason is structural, not stylistic: markers would have to be
written into `CLAUDE.md` and into `schemas/*.md`, and Operating Rule 1 forbids
writing to `schemas/` at all. A rule that cannot be applied to the corpus it
governs is not a rule. So the distinction is INFERRED, from two properties the
corrections already have.

    THE RULE, stated once and in full:

    (1) LEXICAL DEMOTION. A number is QUOTED HISTORY when a correction
        connective governs it directly -- `not 34`, `said 17`, `was 915`,
        `until 60`, `previously 8`, or the left-hand side of an `old -> new`
        arrow pair. "Governs it directly" is deliberately tight: the cue must
        be the last thing before the number, separated only by punctuation and
        emphasis, so that a `NOT` forty characters upstream in an unrelated
        clause cannot demote a live claim. Everything else is a LIVE claim.

    (2) PRESENCE, NOT POSITION. A (document, noun) pair AGREES when the derived
        value appears among that document's LIVE claims for the noun. It is not
        required to be the only one, or the last one.

    Rule (2) is the one that makes this survive the corpus, and it is worth
    saying why it is also the honest rule. These documents are APPEND-ONLY: a
    correction is added below the text it corrects and the old text stays. So a
    document that has been corrected carries several values for one noun, and
    the question that actually matters -- the one the twenty hand-found defects
    all answer NO to -- is "does the record still contain the truth anywhere".
    Position cannot answer it: the phase-8 entry's LAST live claim is the `17`
    denominator of a historical audit, and the current `15` is written above it.
    Failing on that would be a false positive whose only "fix" is falsifying a
    dated measurement.

    WHAT THIS RULE DOES NOT CATCH, said plainly rather than discovered later:
    a document that carries the right number in one place and a stale one in
    another PASSES. The stale one is still REPORTED, by file and line, under
    SUPERSEDED -- counted, never dropped -- but it does not fail the gate. The
    alternative (fail unless every claim is current) cannot be implemented
    without markers, because a deliberately-quoted wrong number and a stale
    live one are textually identical once the correction connective is a
    sentence away.

    AND THE FAILURE MODE IS SAFE IN THE DIRECTION THAT MATTERS. Demotion is
    NARROW: when in doubt a number stays LIVE and gets checked. A claim the
    tool cannot resolve -- a noun whose derivation is unavailable in this
    checkout -- is reported by name under NOT DERIVABLE HERE and is never
    counted as agreement. Silently exempting is how a checker stops checking.

WHAT IS COUNTED
---------------
A bounded vocabulary, `NOUNS` below. Each entry owns its own derivation, and
every derivation reads the TREE or a GENERATED ARTIFACT -- never another piece
of prose. That is not decoration: a checker whose expected value comes from the
document it is checking agrees by construction, which is the defect one level
up (`tests/test_prose_counts.py` pins each derivation against an independent
recomputation, and asserts that no derivation opens a `.md` file).

RULE 5, FIRST AND UNCONDITIONALLY. The denominator prints before any verdict:
documents scanned, lines read, claims located, and the split into LIVE /
QUOTED-AS-HISTORY / NOT-DERIVABLE. A run that locates ZERO claims EXITS
NON-ZERO -- this repository has had a counter report clean while reading
nothing for two days, and "no disagreements" from a scan that matched no files
is that same zero.

Usage:  python3 tools/check_prose_counts.py
        python3 tools/check_prose_counts.py --enforce   (exit 1 on a disagreement)
        python3 tools/check_prose_counts.py --list      (the vocabulary + today's values)
"""

import argparse
import ast
import glob
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SCHEMA_DIR = os.path.join(REPO, "schemas")
VETA = os.path.join(SCHEMA_DIR, "V_eta")
LEDGER = os.path.join(SCHEMA_DIR, "V_eta_coverage_ledger.json")
GROUND_TRUTH = os.path.join(SCHEMA_DIR, "V_eta_ndi_ground_truth.json")
REGISTRY = os.path.join(VETA, "stable", "binding_registry_meta.json")
BUILDER = os.path.join(HERE, "build_v_eta.py")


# --------------------------------------------------------------------------
# SIBLING CHECKOUTS -- resolved the way tools/gates.py resolves them, so a
# missing one produces a NAMED not-derivable noun rather than a silent zero.
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


class Unavailable(Exception):
    """A derivation that cannot run in THIS checkout. Named, never zero."""


# --------------------------------------------------------------------------
# THE DERIVATIONS -- tree and generated artifacts only. No .md is opened here.
# --------------------------------------------------------------------------

def _veta_docs():
    """(json file count, [document_class block, ...]) over the BUILT V_eta set."""
    if not os.path.isdir(VETA):
        raise Unavailable("schemas/V_eta is not built -- run tools/build_v_eta.py")
    files, blocks = 0, []
    for root, _dirs, names in os.walk(VETA):
        for n in sorted(names):
            if not n.endswith(".json"):
                continue
            files += 1
            try:
                with open(os.path.join(root, n), encoding="utf-8") as fh:
                    doc = json.load(fh)
            except (OSError, ValueError):
                continue
            if isinstance(doc, dict) and isinstance(doc.get("document_class"), dict):
                blocks.append(doc["document_class"])
    return files, blocks


def derive_veta_schema_files():
    return _veta_docs()[0]


def derive_veta_class_names():
    _files, blocks = _veta_docs()
    return len({b["class_name"] for b in blocks
                if isinstance(b.get("class_name"), str)})


def derive_data_type_subclasses():
    _files, blocks = _veta_docs()
    out = set()
    for b in blocks:
        for sup in b.get("superclasses") or []:
            if (isinstance(sup, dict) and sup.get("class_name") == "data_type"
                    and isinstance(b.get("class_name"), str)):
                out.add(b["class_name"])
    return len(out)


def _load_json(path, what):
    if not os.path.exists(path):
        raise Unavailable(f"{what} is absent: {os.path.relpath(path, REPO)}")
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError) as exc:
        raise Unavailable(f"{what} is unreadable: {exc}") from exc


def derive_ndi_templates():
    """NDI production templates, from the generated ground truth artifact."""
    gt = _load_json(GROUND_TRUTH, "V_eta_ndi_ground_truth.json")
    classes = gt.get("classes")
    if not isinstance(classes, dict):
        raise Unavailable("ground truth carries no `classes` map")
    return len(classes)


def derive_ledger_rows():
    led = _load_json(LEDGER, "V_eta_coverage_ledger.json")
    rows = led.get("rows")
    if not isinstance(rows, list):
        raise Unavailable("coverage ledger carries no `rows` list")
    return len(rows)


def derive_registry_rows():
    """Every row in binding_registry_meta.json, normative AND illustrative.

    The 34-vs-38 correction was exactly this: `binding_examples` is a row list
    and was not being counted. So the derivation counts LIST-valued keys, which
    cannot forget one."""
    reg = _load_json(REGISTRY, "binding_registry_meta.json")
    return sum(len(v) for v in reg.values() if isinstance(v, list))


def derive_bound_fields():
    """Fields carrying a `constraints.binding`, NESTED ONES INCLUDED.

    Delegated to `tools/regen_binding_strengths.py`, which owns this walk and
    prints it as its own denominator. Re-implementing it here is how the
    top-level-only sweep missed the two nested bindings and reported 14."""
    if not os.path.isdir(VETA):
        raise Unavailable("schemas/V_eta is not built -- run tools/build_v_eta.py")
    sys.path.insert(0, HERE)
    try:
        import regen_binding_strengths
    except ImportError as exc:            # pragma: no cover - defensive
        raise Unavailable(f"regen_binding_strengths is not importable: {exc}") from exc
    rows, _den = regen_binding_strengths.bound_fields()
    return len(rows)


def derive_migrator_files():
    """`.m` files in +migrators_j, Contents.m and private/ excluded."""
    did = find_repo("DID-matlab", "DID_MATLAB")
    if not did:
        raise Unavailable("DID-matlab checkout not found")
    pkg = os.path.join(did, "src", "did", "+did2", "+convert", "+migrators_j")
    if not os.path.isdir(pkg):
        raise Unavailable(f"+migrators_j not found under {did}")
    return len([n for n in os.listdir(pkg)
                if n.endswith(".m") and n != "Contents.m"])


def derive_didmatlab_m_files():
    did = find_repo("DID-matlab", "DID_MATLAB")
    if not did:
        raise Unavailable("DID-matlab checkout not found")
    src = os.path.join(did, "src")
    if not os.path.isdir(src):
        raise Unavailable(f"src/ not found under {did}")
    return sum(1 for root, _d, fs in os.walk(src)
               for f in fs if f.endswith(".m"))


def derive_ndi_m_files():
    """`.m` files on NDI `origin/main` -- the ref, not the working tree.

    The working tree is the V_eta feature branch and lags main; every figure
    this project quotes about NDI is an origin/main figure."""
    ndi = find_repo("NDI-matlab", "NDI_MATLAB")
    if not ndi:
        raise Unavailable("NDI-matlab checkout not found")
    for ref in ("origin/main", "main"):
        res = subprocess.run(["git", "-C", ndi, "ls-tree", "-r", "--name-only", ref],
                             capture_output=True, text=True, check=False)
        if res.returncode == 0:
            return sum(1 for p in res.stdout.split("\n") if p.endswith(".m"))
    raise Unavailable("neither origin/main nor main resolves in the NDI checkout")


def derive_plan_documents():
    return len(glob.glob(os.path.join(SCHEMA_DIR, "*.md")))


def derive_phase8_deleted():
    """`_DELETE_PHASE8` read from build_v_eta.py's AST.

    Parsed, not grepped: the set literal is surrounded by comments naming the
    two classes that were REMOVED from it, and a grep for quoted strings counts
    those too."""
    if not os.path.exists(BUILDER):
        raise Unavailable("tools/build_v_eta.py is absent")
    with open(BUILDER, encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "_DELETE_PHASE8":
                return len(ast.literal_eval(node.value))
    raise Unavailable("_DELETE_PHASE8 not found in build_v_eta.py")


def derive_tombstones_compared():
    """Asked of `tools/check_tombstones.py`, which owns the skip logic.

    Its denominator is `len(ground_truth.classes) - skipped`, and the skip
    rules (nonprod, chain-mixin, no-tombstone, resolved through the RENAME map)
    are that tool's. Re-implementing them here would be a second list that
    drifts -- the thing this repository keeps having to delete."""
    tool = os.path.join(HERE, "check_tombstones.py")
    if not os.path.exists(tool):
        raise Unavailable("tools/check_tombstones.py is absent")
    res = subprocess.run([sys.executable, tool], capture_output=True, text=True,
                         cwd=REPO, check=False)
    m = re.search(r"^\s*classes compared\s*:\s*(\d+)", res.stdout, re.MULTILINE)
    if not m:
        raise Unavailable("check_tombstones.py printed no `classes compared` line "
                          "(it needs the DID-matlab checkout and the ground truth)")
    return int(m.group(1))


# --------------------------------------------------------------------------
# THE VOCABULARY
# --------------------------------------------------------------------------
# Every pattern has EXACTLY ONE capture group, and it captures the number that
# the noun is about -- not merely a number on the same line. `\d[\d,]*` so a
# thousands separator is read as one figure rather than two.

class Noun:
    def __init__(self, key, what, derive, patterns):
        self.key = key
        self.what = what
        self.derive = derive
        self.patterns = [re.compile(p) for p in patterns]
        for p in self.patterns:
            if p.groups != 1:
                raise ValueError(f"{key}: pattern must have exactly one group: {p.pattern}")


_N = r"(?<![\w.])(\d[\d,]*)"

NOUNS = [
    Noun("veta_schema_files", "json files under schemas/V_eta/",
         derive_veta_schema_files,
         [_N + r"\s+json files?(?:\(s\))?\s+under\s+`?schemas/V_eta",
          _N + r"\s+json file\(s\)\s+under\s+`?schemas/V_eta"]),

    Noun("veta_class_names", "distinct V_eta class names",
         derive_veta_class_names,
         [_N + r"\s+(?:distinct\s+)?V_eta class names"]),

    Noun("data_type_subclasses", "direct subclasses of `data_type`",
         derive_data_type_subclasses,
         [_N + r"\s*\**\s*direct subclasses"]),

    Noun("ndi_templates", "NDI production templates on origin/main",
         derive_ndi_templates,
         [_N + r"\s+NDI templates?\b",
          _N + r"\s+template json file\(s\) on NDI",
          _N + r"\s+on NDI-matlab origin/main"]),

    Noun("ledger_rows", "rows in the V_eta coverage ledger",
         derive_ledger_rows,
         [_N + r"\s+(?:v1\s+)?ledger rows?\b",
          _N + r"\s+ledger row\(s\)"]),

    Noun("registry_rows", "rows in binding_registry_meta.json",
         derive_registry_rows,
         [r"registry (?:is|was|were|has|had|carries|carried)\s+\**" + _N + r"\s*\**\s*rows",
          _N + r"\s+row\(s\)\s*\(\d+ normative"]),

    Noun("bound_fields", "V_eta fields carrying a `constraints.binding`",
         derive_bound_fields,
         [_N + r"\s*\**\s*(?:bound\s+)?fields?\s*\**\s*(?:now\s+)?carry(?:ing)?\s+a\s+binding",
          _N + r"\s+bound field declaration\(s\)"]),

    Noun("migrator_files", "migrator .m files in +migrators_j",
         derive_migrator_files,
         [_N + r"\s+migrator \.m file\(s\)"]),

    # THE PATH ITSELF NAMES THE SCOPE, and this pattern used to ignore that.
    # `210 .m file(s) under DID-matlab src/did/+did2 scanned` was adjudicated
    # against the WHOLE-TREE count (267) and reported DISAGREE, because `src/`
    # matched as a PREFIX of `src/did/+did2`. That is the same error SCOPED_RE
    # exists to prevent -- a count over a narrowed set is a different count,
    # not a stale one -- arriving through the path instead of through a
    # parenthesis, so the parenthesis-shaped guard could not see it.
    #
    # The lookahead rejects any DEEPER path while still matching the whole-tree
    # form (`src/ scanned`, `src/ as of 2026-08-12`), and it needs no vocabulary
    # of narrowings: a subtree is recognised structurally. A claim about a
    # subtree is now simply not a claim about this noun, which is why it drops
    # out of the adjudication entirely rather than joining the SCOPED bucket.
    Noun("didmatlab_m_files", ".m files under DID-matlab src/",
         derive_didmatlab_m_files,
         [_N + r"\s+\.m file\(s\) under DID-matlab src/(?![\w/+.])"]),

    Noun("ndi_m_files", ".m files on NDI origin/main",
         derive_ndi_m_files,
         [r"NDI templates on origin/main[;,]?\s+" + _N + r"\s+\.m files",
          r"\bof\s+" + _N + r"\s+NDI files",
          r"grep -c[^\n]{0,60}?\\\.m\$[^\n]{0,20}?=\s*\**" + _N]),

    Noun("plan_documents", "markdown documents under schemas/",
         derive_plan_documents,
         [_N + r"\s+markdown files?(?:\(s\))?\s+under\s+`?schemas/",
          _N + r"\s+markdown file\(s\)\s+under\s+`?schemas/"]),

    Noun("phase8_deleted", "classes in build_v_eta.py `_DELETE_PHASE8`",
         derive_phase8_deleted,
         [r"\*\*" + _N + r"\s+deleted\*\*",
          _N + r"\s+deleted classes\b",
          _N + r"\s+phase-8 deletions?\b"]),

    Noun("tombstones_compared", "source tombstones compared against NDI",
         derive_tombstones_compared,
         [r"classes compared\s*:\s*" + _N,
          r"\b\d+\s+of\s+" + _N + r"\s+diverged"]),
]

BY_KEY = {n.key: n for n in NOUNS}


# --------------------------------------------------------------------------
# LEXICAL DEMOTION -- rule (1)
# --------------------------------------------------------------------------
# The cue must be the LAST thing before the number, separated only by
# punctuation, emphasis and a very small filler set. Deliberately tight: an
# earlier draft allowed the cue anywhere in the preceding 46 characters, and
# that demoted `**38 direct subclasses**` in the sentence
# "NOT `data_type` -- that is a CLASS with **38 direct subclasses**", i.e. it
# silently exempted a LIVE claim. Narrow demotion errs toward checking.

_FILLER = r"[\s*_`~\"'(),.:;—–-]*"
_CUE = (r"(?:not|was|were|said|says|say|until|previously|formerly|"
        r"no longer|used to|instead of|rather than|read)")
DEMOTED_BEFORE_RE = re.compile(
    _CUE + _FILLER + r"(?:only|just|about|roughly|still|then|around)?" + _FILLER + r"$",
    re.IGNORECASE)

# `old -> new`: the arrow demotes what is on its LEFT, never what is on its
# right. `-> 241 distinct V_eta class names` is the CORRECTED value.
DEMOTED_AFTER_RE = re.compile(r"^\s*(?:->|→)\s*\d")

# THE CORRECTION PAIR. The house writes both numbers in one breath -- "**38
# rows, not 34**", "(**15 deleted** -- this line said 17)", "-> 241 distinct
# V_eta class names (the note above said 224)". The OLD value is bare: it does
# not repeat the noun, so no noun pattern can reach it, and without this it is
# invisible to the tool rather than exempt by it. It is attributed to the
# NEAREST noun match on its left, and only within `PAIR_REACH` characters --
# measured: the nearest wrong attribution in today's corpus sits 63 characters
# away, across a semicolon and a different subject.
CORRECTION_PAIR_RE = re.compile(
    r"\b(?:not|said|says|was|were|until|previously|formerly|"
    r"rather than|instead of|no longer)\s+\**(\d[\d,]*)\b", re.IGNORECASE)
PAIR_REACH = 40
# `until 2026-08-10` is a DATE, not the number the sentence used to carry.
DATEISH_RE = re.compile(r"^-\d")


# A COUNT OVER A NARROWED SET IS A DIFFERENT COUNT, and the corpus says so out
# loud: `245 json files under schemas/V_eta read (examples/ excluded)` is not a
# stale 247, it is 247 minus the two examples. Such a claim is REPORTED as
# SCOPED and left unchecked -- adjudicating it would need the vocabulary to
# model every narrowing anyone might write, and guessing is how a checker
# starts producing findings nobody can act on.
SCOPED_RE = re.compile(r"\([^)]{0,60}?exclud", re.IGNORECASE)
SCOPE_REACH = 60


def is_demoted(line, start, end):
    """Is the number at line[start:end] quoted as history rather than asserted?"""
    if DEMOTED_BEFORE_RE.search(line[:start]):
        return True
    return bool(DEMOTED_AFTER_RE.match(line[end:]))


def is_scoped(text, end):
    return SCOPED_RE.search(text[end:end + SCOPE_REACH]) is not None


# --------------------------------------------------------------------------
# THE SCAN
# --------------------------------------------------------------------------

class Claim:
    def __init__(self, path, lineno, noun, value, demoted, text, scoped=False):
        self.path = path
        self.lineno = lineno
        self.noun = noun
        self.value = value
        self.demoted = demoted
        self.scoped = scoped
        self.text = text

    @property
    def live(self):
        """ASSERTED: neither quoted as history nor narrowed to a sub-set."""
        return not self.demoted and not self.scoped

    @property
    def where(self):
        return f"{os.path.relpath(self.path, REPO)}:{self.lineno}"


def documents():
    """CLAUDE.md plus every markdown document under schemas/."""
    paths = [os.path.join(REPO, "CLAUDE.md")]
    paths += sorted(glob.glob(os.path.join(SCHEMA_DIR, "*.md")))
    return [p for p in paths if os.path.exists(p)]


FENCE_RE = re.compile(r"^\s*(?:```|~~~)")


def _atomic(line, in_fence):
    """Is this line a unit of its own rather than wrapped prose?

    JOINING THE WRONG TWO LINES INVENTS A CLAIM, and it did: a denominator
    block in `V_eta_OPEN_WORK.md` reads

        distinct normalised class names across all six: 45
        ledger rows: 102

    and joining them produced the phrase `45 ledger rows`, i.e. a ledger-row
    claim of 45 that nobody ever wrote. So the tabular forms -- fenced blocks,
    indented denominator tables, markdown table rows -- are never joined to
    anything. Only ordinary wrapped prose is."""
    return (in_fence
            or FENCE_RE.match(line) is not None
            or line.startswith("      ")
            or line.lstrip().startswith("|"))


def blocks(lines):
    """Split into units, each flattened to ONE string.

    THE CORPUS IS HARD-WRAPPED at about ninety characters, and a claim wraps
    like any other sentence: ``... origin/main | grep -c '\\.m$'` = `` ends one
    line and `**1002**, not 915` begins the next. A line-at-a-time scan cannot
    see that number at all -- it went looking for it, found only the stale
    `915` two lines above, and reported the document as carrying no current
    value. Flattening wrapped prose is what makes a wrapped claim reachable;
    `_atomic` is what stops the flattening from inventing one.

    Returns [(text, [(char_start, lineno), ...]), ...] so a match offset maps
    back to the line the NUMBER is actually on."""
    out, cur, spans = [], [], []
    pos = 0
    in_fence = False

    def flush():
        nonlocal cur, spans, pos
        if cur:
            out.append((" ".join(cur), spans))
        cur, spans, pos = [], [], 0

    for i, raw in enumerate(lines):
        fence_line = FENCE_RE.match(raw) is not None
        atomic = _atomic(raw, in_fence)
        if fence_line:
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
            pos += 1                      # the joining space
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


def scan(paths, nouns=None):
    """Locate every claim. Returns (claims, docs_read, lines_read, unreadable)."""
    nouns = nouns if nouns is not None else NOUNS
    claims, docs_read, lines_read, unreadable = [], 0, 0, []
    for path in paths:
        try:
            with open(path, encoding="utf-8") as fh:
                lines = fh.read().splitlines()
        except OSError as exc:
            unreadable.append((path, str(exc)))
            continue
        docs_read += 1
        lines_read += len(lines)
        for text, spans in blocks(lines):
            hits = []                     # (start, end, noun) of every noun match
            for noun in nouns:
                for pat in noun.patterns:
                    for m in pat.finditer(text):
                        raw = m.group(1)
                        hits.append((m.start(), m.end(), noun.key))
                        claims.append(Claim(
                            path, _lineno_at(spans, m.start(1)), noun.key,
                            int(raw.replace(",", "")),
                            is_demoted(text, m.start(1), m.end(1)),
                            _excerpt(text, m.start(1)),
                            scoped=is_scoped(text, m.end())))
            # The bare OLD half of a correction pair, attributed to the nearest
            # noun match on its left and only within reach.
            hits.sort()
            for m in CORRECTION_PAIR_RE.finditer(text):
                if DATEISH_RE.match(text[m.end(1):m.end(1) + 3]):
                    continue
                owner = None
                for start, end, key in hits:
                    if end <= m.start(1) and m.start(1) - end <= PAIR_REACH:
                        owner = key
                if owner is None:
                    continue
                claims.append(Claim(
                    path, _lineno_at(spans, m.start(1)), owner,
                    int(m.group(1).replace(",", "")), True,
                    _excerpt(text, m.start(1))))
    # One number can be matched by two patterns of the same noun, and the
    # pattern's own verdict wins over the correction-pair scan's -- so the
    # FIRST sighting is kept.
    seen, unique = set(), []
    for c in claims:
        key = (c.path, c.lineno, c.noun, c.value)
        if key in seen:
            continue
        seen.add(key)
        unique.append(c)
    return unique, docs_read, lines_read, unreadable


def _excerpt(text, at, width=150):
    lo = max(0, at - width // 2)
    return ("..." if lo else "") + text[lo:lo + width]


def derive_all(keys):
    """{key: value} and {key: reason} for the ones that cannot be derived here."""
    values, unavailable = {}, {}
    for key in keys:
        noun = BY_KEY[key]
        try:
            values[key] = noun.derive()
        except Unavailable as exc:
            # `Unavailable` ONLY. Anything else propagates: a derivation that
            # raises unexpectedly and is filed as "not derivable here" is a
            # denominator shrinking quietly, which is the defect this whole
            # tool is about. It should crash the run instead.
            unavailable[key] = str(exc)
    return values, unavailable


def adjudicate(claims, values, unavailable):
    """Rule (2): a (document, noun) pair AGREES when the derived value appears
    among that document's LIVE claims for the noun.

    Returns (agree, disagree, superseded, undecidable) where each is a list of
    (path, noun, derived_or_None, [claims])."""
    groups = {}
    for c in claims:
        groups.setdefault((c.path, c.noun), []).append(c)

    agree, disagree, superseded, undecidable = [], [], [], []
    for (path, noun), rows in sorted(groups.items(),
                                     key=lambda kv: (kv[0][0], kv[0][1])):
        if noun in unavailable:
            undecidable.append((path, noun, None, rows))
            continue
        derived = values[noun]
        live = [r for r in rows if r.live]
        if not live:
            # Every claim for this noun in this document is quoted history, so
            # the document never asserts a current value. That is a FAILURE
            # under --enforce, not a quiet exemption: it is also the state a
            # broken demotion rule produces, so a rule that exempted
            # everything would turn the whole corpus into this bucket instead
            # of into a clean run.
            undecidable.append((path, noun, derived, rows))
            continue
        if any(r.value == derived for r in live):
            agree.append((path, noun, derived, rows))
            stale = [r for r in live if r.value != derived]
            if stale:
                superseded.append((path, noun, derived, stale))
        else:
            disagree.append((path, noun, derived, live))
    return agree, disagree, superseded, undecidable


# --------------------------------------------------------------------------
# RENDER
# --------------------------------------------------------------------------

def render(paths, claims, docs_read, lines_read, unreadable,
           values, unavailable, agree, disagree, superseded, undecidable,
           out=print):
    # RULE 5: the denominator prints FIRST and UNCONDITIONALLY. "0 disagreements"
    # from a scan that matched no files is the same zero `silentLoss` printed
    # for two days.
    live = [c for c in claims if c.live]
    hist = [c for c in claims if c.demoted]
    scoped = [c for c in claims if c.scoped and not c.demoted]
    nd_claims = [c for c in claims if c.noun in unavailable]
    out(f"DENOMINATOR: {len(paths)} document(s) globbed, {docs_read} read, "
        f"{lines_read} line(s); {len(claims)} numeric claim(s) located "
        f"over a vocabulary of {len(NOUNS)} countable noun(s)")
    out(f"  claims ASSERTED (checked)            : {len(live)}")
    out(f"  claims QUOTED AS HISTORY (exempt)    : {len(hist)}")
    out(f"  claims SCOPED to a sub-set (exempt)  : {len(scoped)}")
    out(f"  claims whose noun is NOT DERIVABLE   : {len(nd_claims)}")
    out(f"  nouns with a claim in the corpus     : "
        f"{len({c.noun for c in claims})} of {len(NOUNS)}")
    out(f"  nouns DERIVED here                   : {len(values)}")
    out(f"  nouns NOT DERIVABLE here             : {len(unavailable)}")
    out(f"  (document, noun) pairs adjudicated   : "
        f"{len(agree) + len(disagree) + len(undecidable)}")
    out(f"    AGREE                              : {len(agree)}")
    out(f"    DISAGREE                           : {len(disagree)}")
    out(f"    UNDECIDABLE                        : {len(undecidable)}")
    out(f"  superseded claims inside AGREE pairs : "
        f"{sum(len(r) for _p, _n, _d, r in superseded)}")
    out("")

    # Conservation, so a bucket cannot be dropped quietly: every located claim
    # is ASSERTED, QUOTED-AS-HISTORY or SCOPED, and every one whose noun has no
    # derivation is named again in its own line above.
    assert len(live) + len(hist) + len(scoped) == len(claims)

    for path, exc in unreadable:
        out(f"UNREADABLE: {os.path.relpath(path, REPO)} -- {exc}")

    if scoped:
        out("SCOPED -- a count over a NARROWED set, exempt because it is a "
            "different count, not a stale one:")
        for c in scoped:
            out(f"  {c.where}  [{c.noun}]  says {c.value}")
            out(f"      {c.text[:140]}")
        out("")

    if unavailable:
        out("NOT DERIVABLE HERE -- named, never counted as agreement:")
        for key in sorted(unavailable):
            n = len([c for c in claims if c.noun == key])
            out(f"  {key:24s} {unavailable[key]}  ({n} claim(s) unchecked)")
        out("")

    if values:
        out("DERIVED TODAY:")
        for key in sorted(values):
            n = len([c for c in claims if c.noun == key])
            out(f"  {key:24s} {values[key]:>8}   {BY_KEY[key].what}  "
                f"({n} claim(s))")
        out("")

    if disagree:
        out("DISAGREE -- the document asserts a number the tree does not hold, "
            "and carries no live claim that matches:")
        for path, noun, derived, rows in disagree:
            out(f"  {os.path.relpath(path, REPO)}  [{noun}]  derived {derived}")
            for r in rows:
                out(f"      {r.where}  says {r.value}")
                out(f"          {r.text[:140]}")
        out("")

    if undecidable:
        out("UNDECIDABLE -- reported rather than exempted:")
        for path, noun, derived, rows in undecidable:
            why = ("noun not derivable here" if noun in unavailable
                   else "every claim in this document is quoted as history; "
                        "the document never asserts a current value")
            out(f"  {os.path.relpath(path, REPO)}  [{noun}]  "
                f"derived {derived if derived is not None else '?'}  -- {why}")
            for r in rows:
                out(f"      {r.where}  says {r.value}"
                    f"{'  (quoted as history)' if r.demoted else ''}")
        out("")

    if superseded:
        out("SUPERSEDED -- an earlier live number in a document that DOES carry "
            "the current one. Not a failure (the corrections are append-only), "
            "but listed so it is never silently dropped:")
        for path, noun, derived, rows in superseded:
            for r in rows:
                out(f"  {r.where}  [{noun}]  says {r.value}, derived {derived}")
        out("")

    if not disagree:
        out("No document asserts a countable number the tree does not hold.")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--enforce", action="store_true",
                    help="exit non-zero when a document disagrees with the tree")
    ap.add_argument("--list", action="store_true",
                    help="print the vocabulary and today's derived values, then stop")
    args = ap.parse_args(argv)

    if args.list:
        values, unavailable = derive_all([n.key for n in NOUNS])
        print(f"DENOMINATOR: {len(NOUNS)} countable noun(s) declared, "
              f"{len(values)} derivable here, {len(unavailable)} not")
        for n in NOUNS:
            got = values.get(n.key)
            print(f"  {n.key:24s} {str(got) if got is not None else 'n/a':>8}   {n.what}")
            for p in n.patterns:
                print(f"      pattern: {p.pattern}")
        for key in sorted(unavailable):
            print(f"  NOT DERIVABLE: {key} -- {unavailable[key]}")
        return 0

    paths = documents()
    claims, docs_read, lines_read, unreadable = scan(paths)

    # Derive only the nouns something actually claims -- some derivations shell
    # out, and a vocabulary entry nobody quotes costs nothing to leave unread.
    values, unavailable = derive_all(sorted({c.noun for c in claims}))
    agree, disagree, superseded, undecidable = adjudicate(claims, values, unavailable)

    render(paths, claims, docs_read, lines_read, unreadable,
           values, unavailable, agree, disagree, superseded, undecidable)

    if docs_read == 0 or not claims:
        print()
        print("NOTHING WAS LOCATED -- the scan matched no numeric claim. That is "
              "a FAILURE, not a pass: a checker that reads nothing prints the "
              "same clean zero as a checker that finds nothing wrong.")
        return 1

    # A pair whose noun is not derivable HERE is a gap in this checkout, not a
    # defect in the prose, so it never fails. A pair where every claim is
    # quoted history does fail: the document has stopped asserting anything.
    all_history = [p for p in undecidable if p[1] not in unavailable]
    return 1 if ((disagree or all_history) and args.enforce) else 0


if __name__ == "__main__":
    sys.exit(main())
