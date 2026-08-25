#!/usr/bin/env python3
"""#69 -- when a child redeclares an ancestor's field, WHICH WAY did it move?

WHY THIS EXISTS
---------------
`tools/check_duplicate_field_declarations.py` answers "is this field name
declared twice in one chain?" and stops there. It counts NAMES. It never opens
the two declarations, so a child that redeclares `mustBeNonEmpty: true` over an
ancestor's `false` -- or, the dangerous direction, `false` over the ancestor's
`true` -- is indistinguishable from a child that repeats the ancestor verbatim.

Both are silent. `resolvePlacement`'s collision check fires only WITHIN one
`targetBlock`, and the default `placement=declaring_class` puts ancestor and
descendant in DIFFERENT blocks, so a cross-block redeclaration trips nothing --
in `+did2/+schema`, in `+did2/+validate`, or in this repo. And the constraint
half is doubly silent, because `validateConstraints` reads only maxLength /
minLength / minimum / maximum / enum and drops every other key into a tolerated
`otherwise`: a `binding`, an `element_type` or a `cols` that a child rewrote is
not merely unreported, it is unread.

So this tool opens both declarations and classifies the move:

    IDENTICAL   every constraint-bearing attribute matches. Harmless, noisy --
                two storage locations for one fact, which is #69's other half.
    TIGHTENED   the descendant's copy admits a STRICT SUBSET of what the
                ancestor's admits.
    LOOSENED    the descendant's copy admits MORE.
    DIVERGENT   the differences do not order: some tighten and some loosen, the
                `type` changed, a subfield was added or removed, or the attribute
                that differs has no defined tighten/loosen ordering at all.

DIVERGENT IS NOT A SOFT VERDICT. It is where the tool says "I cannot tell", and
it is counted separately for exactly that reason -- an unordered difference read
as "probably fine" is the mechanism this project has paid for repeatedly.

"REDECLARES", NOT "OVERRIDES" -- AND THE DIFFERENCE MATTERS
-----------------------------------------------------------
A descendant's declaration does NOT replace its ancestor's. From the meta-schema
in this repository, `did_schema_meta.json`, the `placement` field's own words:

    "Optional per-field opt-in to placement on the concrete subclass's block
     instead of the declaring class's block on document instances. Default when
     omitted is 'declaring_class' [...] Collisions are a hard error reported at
     class-cache build time: (a) two ancestors that both place the same field
     name into the concrete-class block, or (b) any class in the chain [...]
     that declares a field whose name matches a placement: concrete_class
     decla[ration]"

Neither collision case covers the default. Both copies are therefore LIVE, in
different blocks, at the same time -- and the verdict here describes the
DIRECTION IN WHICH THE TWO COPIES OF ONE FACT DISAGREE, not a constraint the
child relaxed away. Today that is the drift test from CLAUDE.md one layer down:
`element.name` and `element.base.name` are the same fact under two different
rules, and which rule applies depends only on which block a writer happened to
fill. If #69's fix lands and the copies are MERGED into the ancestor's entry,
the identical verdict becomes the subtype-substitutability question directly --
which is why the direction is worth recording before the merge, not after.

TWO THINGS EVERY ROW NOW CARRIES, BECAUSE A VERDICT ALONE IS NOT EVIDENCE
-------------------------------------------------------------------------
A bare LOOSENED does not say whether the child is wrong or the ancestor was
over-tightened, and the first run gave a reader nothing to answer that with. Two
mechanical facts, both DERIVED rather than hand-listed, are now printed per row.

1. **v1 PROVENANCE.** Read off `schemas/V_eta_ndi_ground_truth.json` (which
   `tools/ndi_ground_truth.py` extracts from NDI `origin/main`): does did_v1
   ITSELF declare this field in BOTH blocks? If it does, the shadow is not
   V_eta's -- a source tombstone that dropped it would stop matching the writer,
   which is the one thing tombstones exist to do. If it does not, the second
   storage location was minted on this side and "which block is authoritative"
   is a live question. Names are matched with underscores stripped and case
   folded, because V_eta is snake_case and NDI is camelCase and a sweep that
   forgets it reports zero hits against a repository that never contained the
   string it searched for. LIMIT, stated so it is not mistaken for a finding: a
   class V_eta RENAMED from its did_v1 source matches nothing here and reports
   NO-DID-V1-CLASS. That is "not looked up", not "not in NDI".

2. **WHETHER A VALIDATOR READS THE ATTRIBUTE THAT MOVED.** Dropping `maxLength`
   is a live relaxation -- `validateConstraints` raises `did2:validation:maxLength`
   on it. Rewriting `element_type` is not, today: it falls into the same
   function's tolerated `otherwise`. Both are LOOSENED/DIVERGENT rows and they
   are not the same kind of problem, so each diff line is tagged ENFORCED,
   GATED-OFF (the machinery exists behind a disarmed switch) or DECLARATIVE
   (nothing reads it). The tags come from `+did2/+schema/cache.m` and are cited
   at `ENFORCEMENT` below.

WHAT IT DOES NOT DO
-------------------
IT DECIDES NOTHING and it ENFORCES NOTHING (operating rules 4 and the report-only
landing asked for on #69). There is no baseline and no ratchet: the enforcement
threshold is a team call, and this run exists to put real numbers in front of it.
`--enforce` deliberately fails until someone SETS `ENFORCEMENT_THRESHOLD` below.

The provenance column is EVIDENCE, NOT A DISPOSITION. "did_v1 declares it too"
is a strong argument that a tombstone must keep the field; it is not an argument
that the two copies may disagree about `maxLength`. Those are different
questions and the tool answers only the first.

It also reads SCHEMA DECLARATIONS ONLY. It does not read the corpus -- no corpus
report is checked into this repository -- so nothing here is a document count,
and how many real documents a LOOSENED row would admit is UNMEASURED.

WHAT IT FOUND ON THE FIRST RUN (2026-08-10, schemas/V_eta as built)
--------------------------------------------------------------------
Recorded so a later run can be compared against it. These are counts, not
dispositions -- every row below is for the team to decide.

    241 classes loaded (stable=220, draft=17, deprecated=4), 981 inheritance
    edges declared and 981 RESOLVED, 2,197 field declarations and 456
    depends_on declarations read, 4 files skipped (the meta files, which carry
    no document_class.class_name), 0 unparseable, 0 unresolved superclasses.

    FIELDS       9 redeclaration pairs: 2 IDENTICAL, 1 TIGHTENED, 3 LOOSENED,
                 3 DIVERGENT.
    depends_on   2 redeclaration pairs, both IDENTICAL (documentation only).

RE-RUN 2026-08-12. THE ROW SET IS UNCHANGED; THE DENOMINATOR IS NOT.

    239 classes loaded (stable=216, draft=19, deprecated=4), 982 inheritance
    edges declared and 982 RESOLVED, 2,177 field declarations and 460
    depends_on declarations read, 4 files skipped, 0 unparseable, 0 unresolved.

    FIELDS       9 pairs: 2 IDENTICAL, 1 TIGHTENED, 3 LOOSENED, 3 DIVERGENT
    depends_on   2 pairs, both IDENTICAL

Two classes left `stable` and two arrived in `draft` between the runs and twenty
field declarations went with them, so "9 again" is a re-derivation and not a
cached number. The same nine were re-derived a second time against COMMITTED
HEAD, not the working tree, because two other sessions were mid-edit in
`schemas/` at the time; both reads agree.

The 9 field pairs are EXACTLY the 9 rows `check_duplicate_field_declarations.py`
reports at its baseline, which is the cross-check that matters: the name-level
tool and the constraint-level tool see the same set, so neither is reading a
different corpus than it thinks. What is NEW is that only 2 of the 9 are
constraint-identical. Seven differ, and four of those differ in a direction the
name-level count could never have shown.

THE TWO TOOLS DO NOT READ THE SAME TIERS, AND THE AGREEMENT ABOVE IS ABOUT
FIELDS ONLY. The name-level tool loads `stable` + `draft` (235 classes); this
one also loads `deprecated` (239). Nothing in `deprecated` adds a FIELD pair, so
the nine coincide -- but one of the two `depends_on` pairs
(`image_stack.document_id` over `image_stack_parameters`) is deprecated-over-
deprecated and is INVISIBLE to the name-level tool by construction.

RELATED, AND DELIBERATELY NOT DUPLICATED HERE
---------------------------------------------
The sibling instance of "one fact stored twice, and nothing checks the copies
against each other" -- binding `strength` stated BOTH on a field and in
`entity_field_bindings` -- already has an instrument: `check_binding_governance.py`
finding B5. This tool covers the ancestor/descendant axis; B5 covers the
field/registry axis. Run both.

Usage:  python3 tools/check_constraint_refinement.py
        python3 tools/check_constraint_refinement.py --json
        python3 tools/check_constraint_refinement.py --show-identical
        python3 tools/check_constraint_refinement.py --enforce   # fails: unset
"""

import argparse
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SCHEMA_ROOT = os.path.join(REPO, "schemas", "V_eta")

# The did_v1 truth, extracted from NDI origin/main by tools/ndi_ground_truth.py.
# READ, never written here. Its absence is REPORTED, not worked around: a
# provenance column that quietly says "not in NDI" because the file was missing
# is the exact failure mode this repository keeps paying for.
GROUND_TRUTH = os.path.join(REPO, "schemas", "V_eta_ndi_ground_truth.json")

# Tiers named by schemas/V_eta/index.json. Read all three, and REPORT which of
# them was actually found on disk, so "0 rows" and "read nothing" cannot look
# alike from the output.
TIERS = ("stable", "draft", "deprecated")

# REPORT-ONLY, BY DESIGN. #69 landed reporting so the team can pick a threshold
# from real counts rather than from a guess. Setting this to an int turns
# --enforce into a ratchet (count may fall, may not grow); leaving it None makes
# --enforce FAIL LOUDLY rather than pass while checking nothing.
ENFORCEMENT_THRESHOLD = None

# ---------------------------------------------------------------------------
# What counts as a constraint, and which way each one points.
# ---------------------------------------------------------------------------

# Field-level booleans. False -> True narrows the admissible set.
BOOL_CONSTRAINTS = ("mustBeNonEmpty", "mustBeScalar", "mustNotHaveNaN")

# Attributes that are NOT constraints: they change what the field means, is
# named, or can be searched by -- not what it admits. Differences are listed
# under the row but never classified as tighten/loosen.
NON_CONSTRAINT_ATTRS = ("documentation", "blank_value", "default_value",
                        "ontology", "queryable", "placement", "needs_ndi",
                        "discriminator")

# constraints.* keys with a defined ordering. A LARGER value is tighter for the
# first group (a floor rises), a SMALLER value is tighter for the second (a
# ceiling falls). Absent -> present always tightens; present -> absent loosens.
NUMERIC_LARGER_IS_TIGHTER = ("minimum", "min", "min_value", "minLength")
NUMERIC_SMALLER_IS_TIGHTER = ("maximum", "max", "maxLength")

# Admissible-set keys: compare as sets. Subset tightens, superset loosens, an
# overlap that is neither is DIVERGENT.
SET_CONSTRAINTS = ("enum", "values")

# binding.strength, weakest to strongest.
STRENGTH_ORDER = ("none", "optional", "preferred", "required")

TIGHTEN, LOOSEN, UNORDERED, OTHER = "TIGHTEN", "LOOSEN", "UNORDERED", "OTHER"

# ---------------------------------------------------------------------------
# Does anything actually READ the attribute that moved?
# ---------------------------------------------------------------------------
# Every entry below is a line in DID-matlab src/did/+did2/+schema/cache.m,
# re-read 2026-08-12 rather than copied from a comment. A LOOSENED row on an
# ENFORCED attribute admits documents the ancestor's copy would reject TODAY; a
# LOOSENED row on a DECLARATIVE one is a disagreement nothing can act on yet.
# They are not the same finding and must not print the same.
#
#   validateConstraints (cache.m:1829) switches on exactly six keys --
#     maxLength minLength minimum maximum enum   (unconditional)
#     binding                                    (cache.m:1860, behind
#                                                 strictMode('BindingConformance'),
#                                                 which is DISARMED by default)
#   and drops everything else into a tolerated `otherwise` (cache.m:1870).
#
#   validateField enforces the field-level attributes directly --
#     type            validateTypeShape,        cache.m:1645
#     mustBeNonEmpty  missingField/emptyField,  cache.m:1635, 1649
#     mustBeScalar    notScalar,                cache.m:1678
#     mustNotHaveNaN  nanValue,                 cache.m:1682
ENFORCED = "ENFORCED"
GATED_OFF = "GATED-OFF"
DECLARATIVE = "DECLARATIVE"

ENFORCED_FIELD_ATTRS = ("type", "mustBeNonEmpty", "mustBeScalar",
                        "mustNotHaveNaN")
ENFORCED_CONSTRAINT_KEYS = ("maxLength", "minLength", "minimum", "maximum",
                            "enum")
GATED_CONSTRAINT_KEYS = ("binding",)


def enforcement_of(attr, kind="fields"):
    """ENFORCED / GATED-OFF / DECLARATIVE for one differing attribute name."""
    if kind == "depends_on":
        # `mustBeNonEmpty` on an EDGE is enforced -- see compare_edge, which
        # also explains why a child cannot use it to loosen anything.
        # `must_refer_to_document_class` appears in no validator: it is
        # existence-only by the standing decision in CLAUDE.md.
        return ENFORCED if attr == "mustBeNonEmpty" else DECLARATIVE
    if attr in ENFORCED_FIELD_ATTRS:
        return ENFORCED
    if attr.startswith("constraints."):
        key = attr.split(".", 2)[1]
        if key in ENFORCED_CONSTRAINT_KEYS:
            return ENFORCED
        if key in GATED_CONSTRAINT_KEYS:
            return GATED_OFF
    return DECLARATIVE


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_classes(root=SCHEMA_ROOT, tiers=TIERS):
    """Return (classes, stats).

    `classes` maps class_name -> (tier, schema dict). `stats` records every
    denominator this tool prints: which tier directories existed, how many files
    were seen, parsed, and SKIPPED with the reason. A file that cannot be read is
    counted, never dropped silently -- that is the whole `silentLoss` lesson.
    """
    classes = {}
    stats = {
        "root": root,
        "tiers_requested": list(tiers),
        "tiers_found": [],
        "tiers_missing": [],
        "files_seen": 0,
        "files_parsed": 0,
        "skipped_unparseable": [],
        "skipped_no_class_name": [],
        "skipped_duplicate_class_name": [],
        "per_tier": {},
    }
    for tier in tiers:
        d = os.path.join(root, tier)
        if not os.path.isdir(d):
            stats["tiers_missing"].append(tier)
            continue
        stats["tiers_found"].append(tier)
        n = 0
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".json") or fn == "index.json":
                continue
            path = os.path.join(d, fn)
            stats["files_seen"] += 1
            try:
                with open(path) as fh:
                    j = json.load(fh)
            except (OSError, ValueError) as exc:
                stats["skipped_unparseable"].append(f"{tier}/{fn}: {exc}")
                continue
            stats["files_parsed"] += 1
            cn = (j.get("document_class") or {}).get("class_name")
            if not cn:
                stats["skipped_no_class_name"].append(f"{tier}/{fn}")
                continue
            if cn in classes:
                stats["skipped_duplicate_class_name"].append(
                    f"{tier}/{fn} (class_name {cn!r} already loaded)")
                continue
            classes[cn] = (tier, j)
            n += 1
        stats["per_tier"][tier] = n
    return classes, stats


def _norm(s):
    """Fold a class or field name so snake_case and camelCase compare equal.

    V_eta is snake_case, NDI is camelCase, and a sweep that forgets it searches
    for a string the other repository has never contained -- `demo_ndi` against
    `demoNDI` cost this project a whole disposition. Underscores stripped, case
    folded, nothing else.
    """
    return str(s).replace("_", "").lower()


def load_ground_truth(path=GROUND_TRUTH):
    """Return (index, stats) for the did_v1 truth, or ({}, stats) if absent.

    `index` maps a NORMALISED did_v1 class name to the normalised names it
    declares, per kind. `stats` says whether the artifact was found and how much
    of it was read, so "no v1 counterpart" and "never opened the file" are
    distinguishable from the output alone.
    """
    stats = {"path": path, "present": False, "error": None,
             "ndi_ref": None, "classes": 0, "field_names": 0, "edge_names": 0}
    if not os.path.exists(path):
        stats["error"] = "artifact not present -- run tools/ndi_ground_truth.py"
        return {}, stats
    try:
        with open(path) as fh:
            gt = json.load(fh)
    except (OSError, ValueError) as exc:
        stats["error"] = f"unreadable: {exc}"
        return {}, stats
    stats["present"] = True
    stats["ndi_ref"] = gt.get("ndi_ref")
    index = {}
    for cn, entry in (gt.get("classes") or {}).items():
        fields = {_norm(f) for f in (entry.get("fields") or [])}
        edges = {_norm(e) for e in (entry.get("depends_on") or [])}
        index[_norm(cn)] = {"class": cn, "fields": fields, "depends_on": edges}
        stats["field_names"] += len(fields)
        stats["edge_names"] += len(edges)
    stats["classes"] = len(index)
    return index, stats


# Provenance codes. The first is the one that changes what a reader should do:
# did_v1 declares the field in BOTH blocks, so the second declaration is not
# V_eta's to remove.
P_V1_FIDELITY = "V1-FIDELITY"          # did_v1 declares it in both blocks
P_ADDED_ON_CHILD = "V_eta-ADDED-ON-CHILD"    # did_v1 has the parent's only
P_ADDED_ON_PARENT = "V_eta-ADDED-ON-PARENT"  # did_v1 has the child's only
P_ADDED_BOTH = "V_eta-ADDED-BOTH"      # both classes are did_v1, neither
                                       # declares this field -- V_eta's shadow
P_NO_V1_CLASS = "NO-DID-V1-CLASS"      # a V_eta target class, OR a rename this
                                       # lookup cannot follow. NOT "not in NDI".
P_UNKNOWN = "NOT-LOOKED-UP"            # the ground truth artifact was absent


def provenance(gt_index, gt_stats, child, parent, name, kind="fields"):
    """(code, one-line evidence) for one redeclaration pair."""
    if not gt_stats.get("present"):
        return P_UNKNOWN, f"ground truth artifact unavailable ({gt_stats.get('error')})"
    c = gt_index.get(_norm(child))
    p = gt_index.get(_norm(parent))
    if c is None or p is None:
        missing = [n for n, e in ((child, c), (parent, p)) if e is None]
        return P_NO_V1_CLASS, (
            "no did_v1 class matches " + " and ".join(repr(m) for m in missing)
            + " (a V_eta target class, or a rename this lookup cannot follow)")
    n = _norm(name)
    in_c, in_p = n in c[kind], n in p[kind]
    if in_c and in_p:
        return P_V1_FIDELITY, (
            f"did_v1 declares it in BOTH -- {p['class']}.{name} and "
            f"{c['class']}.{name}; dropping the child's would stop the "
            "tombstone matching the writer")
    if in_p and not in_c:
        return P_ADDED_ON_CHILD, (
            f"did_v1 declares {p['class']}.{name} only; the "
            f"{c['class']} block declaration was minted on this side")
    if in_c and not in_p:
        return P_ADDED_ON_PARENT, (
            f"did_v1 declares {c['class']}.{name} only; the "
            f"{p['class']} block declaration was minted on this side")
    return P_ADDED_BOTH, (
        f"both classes exist in did_v1 and NEITHER declares {name} in its own "
        "block -- both copies were minted on this side")


def annotate_provenance(rows, gt_index, gt_stats, kind="fields"):
    """Attach the v1 provenance to every row, in place. Returns `rows`."""
    for r in rows:
        code, why = provenance(gt_index, gt_stats, r["child"], r["parent"],
                               r["name"], kind)
        r["v1_provenance"] = code
        r["v1_evidence"] = why
    return rows


def ancestry(classes, cn):
    """(depths, edge_stats) for one leaf class.

    `depths` maps class_name -> shortest distance from `cn` (0 = the leaf
    itself). Breadth-first so "nearest declaration wins" is well defined under
    multiple inheritance. Every superclass reference is counted, and one that
    names a class we did not load is counted as UNRESOLVED rather than ignored:
    an unresolved edge is a comparison that did not happen.
    """
    depths = {cn: 0}
    order = [cn]
    edges_declared = 0
    unresolved = []
    queue = collections.deque([cn])
    while queue:
        cur = queue.popleft()
        entry = classes.get(cur)
        if entry is None:
            continue
        for s in (entry[1].get("document_class") or {}).get("superclasses") or []:
            sn = s.get("class_name")
            edges_declared += 1
            if not sn:
                unresolved.append(f"{cur} -> <superclass entry with no class_name>")
                continue
            if sn not in classes:
                unresolved.append(f"{cur} -> {sn}")
                continue
            if sn in depths:
                continue
            depths[sn] = depths[cur] + 1
            order.append(sn)
            queue.append(sn)
    return depths, order, edges_declared, unresolved


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------

def _as_set(v):
    """A constraint list as a set of JSON-canonical strings (elements may be dicts)."""
    if not isinstance(v, list):
        return None
    try:
        return {json.dumps(e, sort_keys=True) for e in v}
    except (TypeError, ValueError):
        return None


_MISSING = object()


def _verdict_numeric(key, parent, child):
    if parent is _MISSING:
        return TIGHTEN          # child adds a bound the ancestor did not have
    if child is _MISSING:
        return LOOSEN           # child drops a bound the ancestor had
    if not isinstance(parent, (int, float)) or not isinstance(child, (int, float)):
        return UNORDERED
    if parent == child:
        return None
    larger_tighter = key in NUMERIC_LARGER_IS_TIGHTER
    child_tighter = (child > parent) if larger_tighter else (child < parent)
    return TIGHTEN if child_tighter else LOOSEN


def _verdict_set(parent, child):
    if parent is _MISSING:
        return TIGHTEN
    if child is _MISSING:
        return LOOSEN
    ps, cs = _as_set(parent), _as_set(child)
    if ps is None or cs is None:
        return UNORDERED
    if ps == cs:
        return None
    if cs < ps:
        return TIGHTEN
    if cs > ps:
        return LOOSEN
    return UNORDERED            # overlapping, neither contains the other


def _verdict_strength(parent, child):
    if parent is _MISSING:
        return TIGHTEN
    if child is _MISSING:
        return LOOSEN
    if parent == child:
        return None
    if parent not in STRENGTH_ORDER or child not in STRENGTH_ORDER:
        return UNORDERED
    pi, ci = STRENGTH_ORDER.index(parent), STRENGTH_ORDER.index(child)
    return TIGHTEN if ci > pi else LOOSEN


def compare_constraints(parent_c, child_c, path):
    """Diff two `constraints` objects. Returns [(path, attr, parent, child, verdict)]."""
    diffs = []
    parent_c = parent_c or {}
    child_c = child_c or {}
    for key in sorted(set(parent_c) | set(child_c)):
        pv = parent_c.get(key, _MISSING)
        cv = child_c.get(key, _MISSING)
        if pv is not _MISSING and cv is not _MISSING and pv == cv:
            continue
        attr = f"constraints.{key}"
        if key in NUMERIC_LARGER_IS_TIGHTER or key in NUMERIC_SMALLER_IS_TIGHTER:
            verdict = _verdict_numeric(key, pv, cv)
        elif key in SET_CONSTRAINTS:
            verdict = _verdict_set(pv, cv)
        elif key == "binding":
            # Only `strength` is ordered. Every other binding key names a
            # vocabulary, a root or an expansion rule -- rewriting one is a
            # DIFFERENT admissible set, not a narrower one, so it is UNORDERED
            # by construction rather than by omission.
            pb = pv if isinstance(pv, dict) else {}
            cb = cv if isinstance(cv, dict) else {}
            for bk in sorted(set(pb) | set(cb)):
                pbv = pb.get(bk, _MISSING)
                cbv = cb.get(bk, _MISSING)
                if pbv is not _MISSING and cbv is not _MISSING and pbv == cbv:
                    continue
                if bk == "strength":
                    v = _verdict_strength(pbv, cbv)
                elif bk == "values":
                    v = _verdict_set(pbv, cbv)
                else:
                    v = UNORDERED
                if v is not None:
                    diffs.append((path, f"constraints.binding.{bk}", pbv, cbv, v))
            continue
        else:
            verdict = UNORDERED
        if verdict is not None:
            diffs.append((path, attr, pv, cv, verdict))
    return diffs


def compare_field(parent_f, child_f, path):
    """Deep diff of one field declaration against its ancestor's.

    Walks nested `fields` by name, so a redeclaration that only differs three
    levels down is still seen. Structural moves (a subfield added or removed) are
    UNORDERED: adding a subfield does not narrow the admissible set of the
    subfield that was already there.
    """
    diffs = []

    if parent_f.get("type") != child_f.get("type"):
        diffs.append((path, "type", parent_f.get("type"),
                      child_f.get("type"), UNORDERED))

    for attr in BOOL_CONSTRAINTS:
        pv = parent_f.get(attr, _MISSING)
        cv = child_f.get(attr, _MISSING)
        if pv == cv:
            continue
        if pv is _MISSING or cv is _MISSING:
            verdict = UNORDERED
        else:
            verdict = TIGHTEN if (cv and not pv) else LOOSEN
        diffs.append((path, attr, pv, cv, verdict))

    for attr in NON_CONSTRAINT_ATTRS:
        pv = parent_f.get(attr, _MISSING)
        cv = child_f.get(attr, _MISSING)
        if pv != cv:
            diffs.append((path, attr, pv, cv, OTHER))

    diffs.extend(compare_constraints(parent_f.get("constraints"),
                                     child_f.get("constraints"), path))

    psubs = {f.get("name"): f for f in (parent_f.get("fields") or [])}
    csubs = {f.get("name"): f for f in (child_f.get("fields") or [])}
    for name in sorted(set(psubs) | set(csubs)):
        sub_path = f"{path}.{name}"
        if name not in csubs:
            diffs.append((sub_path, "<subfield>", "declared", "REMOVED", UNORDERED))
        elif name not in psubs:
            diffs.append((sub_path, "<subfield>", "absent", "ADDED", UNORDERED))
        else:
            diffs.extend(compare_field(psubs[name], csubs[name], sub_path))
    return diffs


def classify(diffs):
    """IDENTICAL / TIGHTENED / LOOSENED / DIVERGENT from a diff list."""
    verdicts = {d[4] for d in diffs}
    if UNORDERED in verdicts:
        return "DIVERGENT"
    if TIGHTEN in verdicts and LOOSEN in verdicts:
        return "DIVERGENT"
    if TIGHTEN in verdicts:
        return "TIGHTENED"
    if LOOSEN in verdicts:
        return "LOOSENED"
    return "IDENTICAL"          # OTHER-only diffs, or no diffs at all


# ---------------------------------------------------------------------------
# The sweep
# ---------------------------------------------------------------------------

def _declarations(schema, kind):
    if kind == "fields":
        return {f.get("name"): f for f in (schema.get("fields") or [])
                if f.get("name")}
    return {e.get("name"): e for e in (schema.get("depends_on") or [])
            if e.get("name")}


def compare_edge(parent_e, child_e, path):
    """Diff two `depends_on` entries.

    THIS DOCSTRING SAID "`mustBeNonEmpty` on an edge is declared everywhere and
    enforced nowhere (`+did2/+validate/references.m` skips empty edges)". THAT
    IS STALE, and stale in the direction that makes a live gate read as
    decorative. Corrected 2026-08-12 from the code, not from a comment:

      * `references.m:90` does still skip empty edges -- and says in its own
        words that this is "the limit of what is knowable from this function's
        inputs", not a policy: it is the ORPHAN check and is handed no schema.
      * The check now lives in `cache.m:787-788`, behind
        `strictMode('RequiredDependencies')`, WHICH IS ARMED (2026-08-10, team's
        call, on a measured cost of 7,233 empty required edges). An edge
        declared `mustBeNonEmpty` and left blank raises
        `did2:validation:emptyRequiredDependency`.

    AND THE SEMANTICS ARE NOT THE FIELD SEMANTICS, which is why a LOOSEN here
    reads differently from a LOOSEN on a field. `requiredDependencies`
    (`cache.m:236-289`) collects every edge name declared `mustBeNonEmpty`
    ANYWHERE IN THE CHAIN and unions them -- `if ~logical(dep.mustBeNonEmpty);
    continue; end`, then add the name. So the STRICTEST declaration in the chain
    governs and a child CANNOT relax a required edge by redeclaring it `false`.
    The disagreement is still worth reporting (it is two copies of one fact
    saying different things, which is #69's other half) but it is not a hole a
    document can get through. Rows carry that caveat inline.

    `must_refer_to_document_class` is DECLARATIVE -- existence-only, never
    type-checked -- per the standing decision in CLAUDE.md.
    """
    diffs = []
    pv = parent_e.get("mustBeNonEmpty", _MISSING)
    cv = child_e.get("mustBeNonEmpty", _MISSING)
    if pv != cv:
        if pv is _MISSING or cv is _MISSING:
            diffs.append((path, "mustBeNonEmpty", pv, cv, UNORDERED))
        else:
            diffs.append((path, "mustBeNonEmpty", pv, cv,
                          TIGHTEN if (cv and not pv) else LOOSEN))
    pr = parent_e.get("must_refer_to_document_class", _MISSING)
    cr = child_e.get("must_refer_to_document_class", _MISSING)
    if pr != cr:
        # Retargeting an edge is a different referent, not a narrower one. Even
        # narrowing to a subclass is UNORDERED here, because must_refer is
        # existence-only and never type-checked -- there is no relation to narrow.
        diffs.append((path, "must_refer_to_document_class", pr, cr, UNORDERED))
    if parent_e.get("documentation") != child_e.get("documentation"):
        diffs.append((path, "documentation", parent_e.get("documentation"),
                      child_e.get("documentation"), OTHER))
    return diffs


def sweep(classes, kind="fields"):
    """Every field (or depends_on edge) a class redeclares from an ancestor.

    Returns (rows, stats). A row is one (child, parent, name) redeclaration pair,
    DEDUPLICATED across leaves -- `subject_statement`'s fields are inherited by
    dozens of leaves and the same pair would otherwise be reported dozens of
    times. `chains` records how many leaf chains exhibit the pair, so the noise
    the redeclaration actually causes is still visible.
    """
    stats = {
        "classes_walked": 0,
        "edges_declared": 0,
        "edges_resolved": 0,
        "edges_unresolved": [],
        "chains_with_ancestors": 0,
        "declarations_seen": 0,
        "comparisons": 0,
        "attr_diffs": collections.Counter(),
    }
    pairs = {}
    for cn in sorted(classes):
        stats["classes_walked"] += 1
        depths, order, declared, unresolved = ancestry(classes, cn)
        stats["edges_declared"] += declared
        stats["edges_resolved"] += declared - len(unresolved)
        stats["edges_unresolved"].extend(f"{cn}: {u}" for u in unresolved)
        if len(depths) > 1:
            stats["chains_with_ancestors"] += 1

        # name -> [(depth, class)] for every class in the chain that declares it
        owners = collections.defaultdict(list)
        for anc in order:
            decls = _declarations(classes[anc][1], kind)
            stats["declarations_seen"] += len(decls)
            for name in decls:
                owners[name].append((depths[anc], anc))

        for name, found in sorted(owners.items()):
            if len(found) < 2:
                continue
            found.sort()
            # Consecutive pairs by depth: each redeclaration against the
            # NEAREST declaration above it in the chain.
            for (cd, cc), (pd, pc) in zip(found, found[1:]):
                stats["comparisons"] += 1
                key = (cc, pc, name)
                if key in pairs:
                    pairs[key]["chains"] += 1
                    pairs[key]["leaves"].add(cn)
                    continue
                cf = _declarations(classes[cc][1], kind)[name]
                pf = _declarations(classes[pc][1], kind)[name]
                path = name
                diffs = (compare_field(pf, cf, path) if kind == "fields"
                         else compare_edge(pf, cf, path))
                for d in diffs:
                    stats["attr_diffs"][(d[1], d[4])] += 1
                pairs[key] = {
                    "child": cc, "child_depth": cd, "child_tier": classes[cc][0],
                    "parent": pc, "parent_depth": pd, "parent_tier": classes[pc][0],
                    "name": name, "verdict": classify(diffs), "diffs": diffs,
                    "chains": 1, "leaves": {cn},
                }
    rows = sorted(pairs.values(),
                  key=lambda r: (r["verdict"], r["child"], r["name"]))
    for r in rows:
        r["leaves"] = sorted(r["leaves"])
    return rows, stats


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def _fmt(v):
    if v is _MISSING:
        return "<absent>"
    s = json.dumps(v) if not isinstance(v, str) else repr(v)
    return s if len(s) <= 60 else s[:57] + "..."


EDGE_UNION_CAVEAT = ("chain-union: cache.m:236-289 unions mustBeNonEmpty over "
                     "the WHOLE chain, so the strictest declaration governs "
                     "and a child cannot relax it")


def print_denominator(load_stats, field_stats, edge_stats, gt_stats):
    """FIRST and UNCONDITIONALLY, per operating rule 5.

    'Found nothing' and 'looked in the wrong place' must be distinguishable from
    the output alone, so this prints even when every count below it is zero.
    """
    print("DENOMINATOR")
    print(f"  schema root                     {load_stats['root']}")
    print(f"  tiers requested                 {', '.join(load_stats['tiers_requested'])}")
    print(f"  tiers found on disk             "
          f"{', '.join(load_stats['tiers_found']) or 'NONE'}")
    if load_stats["tiers_missing"]:
        print(f"  tiers NOT on disk               "
              f"{', '.join(load_stats['tiers_missing'])}")
    print(f"  json files seen                 {load_stats['files_seen']}")
    print(f"  json files parsed               {load_stats['files_parsed']}")
    per_tier = ", ".join(f"{k}={v}" for k, v in load_stats["per_tier"].items())
    print(f"  classes loaded                  "
          f"{sum(load_stats['per_tier'].values())}  ({per_tier})")
    print(f"  classes walked                  {field_stats['classes_walked']}")
    print(f"  chains with >=1 ancestor        {field_stats['chains_with_ancestors']}")
    print(f"  inheritance edges declared      {field_stats['edges_declared']}")
    print(f"  inheritance edges RESOLVED      {field_stats['edges_resolved']}")
    print(f"  inheritance edges UNRESOLVED    {len(field_stats['edges_unresolved'])}"
          "   (superclass names a class not loaded -- a comparison that did NOT happen)")
    print(f"  field declarations read         {field_stats['declarations_seen']}")
    print(f"  FIELD comparisons performed     {field_stats['comparisons']}"
          "   (redeclaration pairs, before dedup across leaves)")
    print(f"  depends_on declarations read    {edge_stats['declarations_seen']}")
    print(f"  EDGE comparisons performed      {edge_stats['comparisons']}")
    skipped = (len(load_stats["skipped_unparseable"])
               + len(load_stats["skipped_no_class_name"])
               + len(load_stats["skipped_duplicate_class_name"]))
    print(f"  declared-but-unreadable SKIPPED {skipped}")
    for label, key in (("unparseable json", "skipped_unparseable"),
                       ("no document_class.class_name", "skipped_no_class_name"),
                       ("duplicate class_name", "skipped_duplicate_class_name")):
        for item in load_stats[key]:
            print(f"      {label}: {item}")
    for item in field_stats["edges_unresolved"]:
        print(f"      unresolved superclass: {item}")
    print(f"  did_v1 ground truth artifact    "
          f"{'PRESENT' if gt_stats['present'] else 'ABSENT'}   {gt_stats['path']}")
    if gt_stats["present"]:
        print(f"    ndi_ref                       {gt_stats['ndi_ref']}")
        print(f"    did_v1 classes indexed        {gt_stats['classes']}")
        print(f"    did_v1 field names indexed    {gt_stats['field_names']}")
        print(f"    did_v1 depends_on names       {gt_stats['edge_names']}")
    else:
        print(f"    NOT READ: {gt_stats['error']}")
        print("    Every row below will read NOT-LOOKED-UP. That is the tool "
              "not having looked,")
        print("    NOT a finding that these fields are absent from did_v1.")
    print()


def print_section(title, rows, stats, show_identical, kind="fields"):
    counts = collections.Counter(r["verdict"] for r in rows)
    print(title)
    print(f"  redeclaration pairs (deduped)   {len(rows)}")
    for v in ("IDENTICAL", "TIGHTENED", "LOOSENED", "DIVERGENT"):
        print(f"    {v:<12} {counts.get(v, 0)}")
    unordered = sum(n for (_, verdict), n in stats["attr_diffs"].items()
                    if verdict == UNORDERED)
    other = sum(n for (_, verdict), n in stats["attr_diffs"].items()
                if verdict == OTHER)
    print(f"  attribute differences with NO defined tighten/loosen ordering: {unordered}")
    print(f"  differences on NON-constraint attributes (doc/default/queryable): {other}")

    # The provenance split is the one a reader acts on, so it goes in the
    # summary and not only under the rows.
    prov = collections.Counter(r.get("v1_provenance", P_UNKNOWN) for r in rows)
    print("  v1 provenance of the shadow (did_v1 declares BOTH copies?):")
    for code in (P_V1_FIDELITY, P_ADDED_ON_CHILD, P_ADDED_ON_PARENT,
                 P_ADDED_BOTH, P_NO_V1_CLASS, P_UNKNOWN):
        if prov.get(code):
            print(f"    {code:<24} {prov[code]}")
    # A LOOSENED/DIVERGENT row on an attribute a validator READS is the
    # actionable subset. Counted here rather than left for a reader to spot.
    live = [r for r in rows
            if r["verdict"] in ("LOOSENED", "DIVERGENT")
            and any(enforcement_of(d[1], kind) == ENFORCED
                    for d in r["diffs"] if d[4] in (LOOSEN, UNORDERED))]
    print(f"  LOOSENED/DIVERGENT rows whose moved attribute IS read by a "
          f"validator: {len(live)}")
    print()

    for verdict in ("LOOSENED", "TIGHTENED", "DIVERGENT", "IDENTICAL"):
        sel = [r for r in rows if r["verdict"] == verdict]
        if not sel:
            continue
        if verdict == "IDENTICAL" and not show_identical:
            print(f"  {verdict} ({len(sel)}) -- constraint-identical redeclarations; "
                  "pass --show-identical to list them.")
            print()
            continue
        print(f"  {verdict} ({len(sel)})")
        for r in sel:
            print(f"    {r['child']}.{r['name']}  redeclares  {r['parent']}.{r['name']}"
                  f"   [{r['child_tier']} over {r['parent_tier']}; "
                  f"seen in {r['chains']} chain(s)]")
            print(f"        v1 provenance: {r.get('v1_provenance', P_UNKNOWN)} "
                  f"-- {r.get('v1_evidence', '')}")
            constraint_diffs = [d for d in r["diffs"] if d[4] != OTHER]
            other_diffs = [d for d in r["diffs"] if d[4] == OTHER]
            for path, attr, pv, cv, v in constraint_diffs:
                tag = enforcement_of(attr, kind)
                print(f"        {v:<9} [{tag:<11}] {path}.{attr}: "
                      f"{_fmt(pv)}  ->  {_fmt(cv)}")
                if kind == "depends_on" and attr == "mustBeNonEmpty":
                    print(f"                  ^ {EDGE_UNION_CAVEAT}")
            # PRINTED ON EVERY ROW NOW, not only on IDENTICAL ones. They were
            # counted in the summary and shown nowhere, which is a count
            # without its evidence -- and it hid a real one: the
            # subjectmeasurement.datestamp row differs on `blank_value` (0.0,
            # a NUMBER, in a field typed `timestamp`) as well as on
            # mustBeNonEmpty, and only the second was ever visible.
            for path, attr, pv, cv, _v in other_diffs:
                print(f"        (non-constraint) {path}.{attr}: "
                      f"{_fmt(pv)}  ->  {_fmt(cv)}")
        print()


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="#69: classify every field a V_eta class redeclares from an "
                    "ancestor as IDENTICAL / TIGHTENED / LOOSENED / DIVERGENT.")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--show-identical", action="store_true",
                    help="list the constraint-identical redeclarations too")
    ap.add_argument("--enforce", action="store_true",
                    help="exit 1 if the count has grown past ENFORCEMENT_THRESHOLD "
                         "(which is UNSET -- see the module docstring)")
    args = ap.parse_args(argv)

    classes, load_stats = load_classes()
    gt_index, gt_stats = load_ground_truth()
    field_rows, field_stats = sweep(classes, "fields")
    edge_rows, edge_stats = sweep(classes, "depends_on")
    annotate_provenance(field_rows, gt_index, gt_stats, "fields")
    annotate_provenance(edge_rows, gt_index, gt_stats, "depends_on")

    if args.json:
        print(json.dumps({
            "load": {k: v for k, v in load_stats.items()},
            "ground_truth": gt_stats,
            "fields": {"rows": [{k: v for k, v in r.items() if k != "diffs"}
                                for r in field_rows],
                       "stats": {k: v for k, v in field_stats.items()
                                 if k != "attr_diffs"}},
            "depends_on": {"rows": [{k: v for k, v in r.items() if k != "diffs"}
                                    for r in edge_rows],
                           "stats": {k: v for k, v in edge_stats.items()
                                     if k != "attr_diffs"}},
        }, indent=1, default=str))
        return 0

    print_denominator(load_stats, field_stats, edge_stats, gt_stats)
    print_section("FIELDS REDECLARED FROM AN ANCESTOR", field_rows, field_stats,
                  args.show_identical, "fields")
    print_section("depends_on EDGES REDECLARED FROM AN ANCESTOR", edge_rows,
                  edge_stats, args.show_identical, "depends_on")

    loosened = sum(1 for r in field_rows + edge_rows if r["verdict"] == "LOOSENED")
    divergent = sum(1 for r in field_rows + edge_rows if r["verdict"] == "DIVERGENT")
    print("REPORT-ONLY. Nothing here fails a build. The enforcement threshold is "
          "a TEAM call (#69);")
    print("this run exists to put the real counts in front of it: "
          f"{loosened} LOOSENED, {divergent} DIVERGENT.")

    if args.enforce:
        if ENFORCEMENT_THRESHOLD is None:
            print("\nFAIL: --enforce was passed but ENFORCEMENT_THRESHOLD is unset.")
            print("A gate that passes without a threshold is a gate that checks "
                  "nothing. Set it deliberately, with the count it was set from.")
            return 1
        total = len(field_rows) + len(edge_rows)
        if total > ENFORCEMENT_THRESHOLD:
            print(f"\nFAIL: {total} redeclaration(s), threshold "
                  f"{ENFORCEMENT_THRESHOLD}.")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
