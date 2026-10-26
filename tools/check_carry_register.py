#!/usr/bin/env python3
"""The carry register's gate (Jess Haley, 2026-10-26,
V_eta_go_forward_class_audit.md [carry register] and [one correct reading]).

schemas/V_eta_carry_register.json lists every reason the generic migration
carries a v1 document whole as v1, so that a carry is never read as "V2 is
missing a field". This checks, and fails on any of:

  C1  the file's shape: `kinds` is exactly the four decided kinds
      (awaiting_home, needs_mapping, not_modelled, malformed); every row has
      a unique `id`, a `v1_class`, a non-empty `fields` list, `when`, a
      `kind` from `kinds`, a `kind_basis` (stated | decided | proposed) and a
      `decision` {document, tag}; and the keys its kind requires:
        awaiting_home  `open_work` (an OPEN_WORK row number; null FAILS, so
                       no home is awaited untracked) and `home`
        needs_mapping  `homes` (a non-empty list), `decides`, `resolved_by`
        not_modelled   `do_not` {line, class, fields}
        malformed      nothing more
      and no other keys.
  C2  a row's `v1_class` that is not a v1 source class of the coverage ledger
      (schemas/V_eta_coverage_ledger.json); `*` is allowed for a reason that can hit any
      class ([renames carry is temporary])
  C3  a row's decision that does not resolve to an accepted decision line
      (tools/decision_citations.py resolve(): a `Decided by` line by a team
      member, or a TEAM-SIGN-OFF line, carrying the tag)
  C4  a `not_modelled` row whose `do_not` names a class the schema does not
      hold (the rule could not be checked), or a class that DECLARES one of
      the forbidden fields or edges, itself or through a superclass. The
      failure quotes the `do_not` line.
  C5  an `awaiting_home` row whose `open_work` number is not a row of the
      "## OPEN" section of schemas/V_eta_OPEN_WORK.md (a completed row fails:
      the home is no longer tracked as awaited).
      (Jess Haley, 2026-10-26: "make the register check fail when missing
      the open work entry".)

It prints its denominator first. A `proposed` kind is reported, never
failed: it is open, not wrong.

Usage: python3 tools/check_carry_register.py
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decision_citations as dc  # noqa: E402

REGISTER = os.path.join(ROOT, "schemas", "V_eta_carry_register.json")
LEDGER = os.path.join(ROOT, "schemas", "V_eta_coverage_ledger.json")
OPEN_WORK = os.path.join(ROOT, "schemas", "V_eta_OPEN_WORK.md")
VETA = os.path.join(ROOT, "schemas", "did_v2")
INDEX = os.path.join(VETA, "index.json")

KINDS = ["awaiting_home", "needs_mapping", "not_modelled", "malformed"]
BASES = ("stated", "decided", "proposed")
COMMON = {"id", "v1_class", "fields", "when", "kind", "kind_basis", "decision"}
BY_KIND = {
    "awaiting_home": {"open_work", "home"},
    "needs_mapping": {"homes", "decides", "resolved_by"},
    "not_modelled": {"do_not"},
    "malformed": set(),
}


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _text(v):
    return isinstance(v, str) and bool(v.strip())


def check_shape(reg):
    """C1. Returns failures."""
    out = []
    if reg.get("kinds") != KINDS:
        out.append(f"C1 `kinds` is {reg.get('kinds')!r}, not {KINDS!r}")
    rows = reg.get("rows")
    if not isinstance(rows, list):
        return out + ["C1 `rows` is not a list"]
    seen = set()
    for i, r in enumerate(rows):
        where = f"row {i + 1} ({r.get('id') if isinstance(r, dict) else r!r})"
        if not isinstance(r, dict):
            out.append(f"C1 {where}: not an object")
            continue
        rid = r.get("id")
        if not _text(rid):
            out.append(f"C1 {where}: no id")
        elif rid in seen:
            out.append(f"C1 {where}: id {rid!r} is used twice")
        seen.add(rid)
        kind = r.get("kind")
        if kind not in BY_KIND:
            out.append(f"C1 {where}: kind {kind!r}, not one of {KINDS}")
            continue
        want = COMMON | BY_KIND[kind]
        if set(r) != want:
            missing, extra = sorted(want - set(r)), sorted(set(r) - want)
            out.append(f"C1 {where}: keys for kind {kind}: missing {missing}, unexpected {extra}")
            continue
        for k in ("v1_class", "when"):
            if not _text(r[k]):
                out.append(f"C1 {where}: `{k}` is empty")
        if not (isinstance(r["fields"], list) and r["fields"]
                and all(_text(f) for f in r["fields"])):
            out.append(f"C1 {where}: `fields` is not a non-empty list of names")
        if r["kind_basis"] not in BASES:
            out.append(f"C1 {where}: kind_basis {r['kind_basis']!r}, not one of {BASES}")
        d = r["decision"]
        if not (isinstance(d, dict) and set(d) == {"document", "tag"}
                and _text(d["document"]) and _text(d["tag"])):
            out.append(f"C1 {where}: `decision` is not {{document, tag}}")
        if kind == "awaiting_home":
            ow = r["open_work"]
            if not (isinstance(ow, int) and not isinstance(ow, bool) and ow > 0):
                out.append(f"C1 {where}: `open_work` is {ow!r}, not an OPEN_WORK row number")
            if not _text(r["home"]):
                out.append(f"C1 {where}: `home` is empty")
        elif kind == "needs_mapping":
            if not (isinstance(r["homes"], list) and r["homes"]
                    and all(_text(h) for h in r["homes"])):
                out.append(f"C1 {where}: `homes` is not a non-empty list")
            for k in ("decides", "resolved_by"):
                if not _text(r[k]):
                    out.append(f"C1 {where}: `{k}` is empty")
        elif kind == "not_modelled":
            dn = r["do_not"]
            if not (isinstance(dn, dict) and set(dn) == {"line", "class", "fields"}
                    and _text(dn["line"]) and _text(dn["class"])
                    and isinstance(dn["fields"], list) and dn["fields"]
                    and all(_text(f) for f in dn["fields"])):
                out.append(f"C1 {where}: `do_not` is not {{line, class, fields}}")
    return out


ANY_CLASS = "*"


def check_v1_classes(rows, v1_classes):
    """C2. `*` is a reason that can hit any class ([renames carry is
    temporary], Jess Haley, 2026-10-26)."""
    return [f"C2 {r['id']}: v1_class {r['v1_class']!r} is not a v1 source class "
            f"of the coverage ledger" for r in rows
            if isinstance(r, dict) and r.get("v1_class") != ANY_CLASS
            and r.get("v1_class") not in v1_classes]


def check_decisions(rows, resolve=dc.resolve):
    """C3. Returns (failures, number resolved)."""
    out, ok = [], 0
    for r in rows:
        d = r.get("decision") if isinstance(r, dict) else None
        if not isinstance(d, dict):
            continue
        rec = resolve(d.get("document"), d.get("tag"))
        if rec.get("resolved"):
            ok += 1
        else:
            out.append(f"C3 {r.get('id')}: [{d.get('tag')}] in {d.get('document')} does "
                       f"not resolve: {rec.get('why')}")
    return out, ok


def class_tree(index_path=INDEX):
    """{class_name: (declared names, [superclass names])} for every class."""
    tree = {}
    for e in _load(index_path)["schemas"]:
        d = _load(os.path.join(ROOT, e["path"]))
        names = {x["name"] for x in d.get("fields", []) + d.get("depends_on", [])}
        supers = [s["class_name"] for s in d.get("document_class", {}).get("superclasses", [])]
        tree[e["class_name"]] = (names, supers)
    return tree


def declares(tree, cls, name):
    """The class in `tree` that declares `name` for `cls`, itself or by inheritance."""
    todo, seen = [cls], set()
    while todo:
        c = todo.pop(0)
        if c in seen or c not in tree:
            continue
        seen.add(c)
        names, supers = tree[c]
        if name in names:
            return c
        todo += supers
    return None


def check_do_not(rows, tree):
    """C4. Returns (failures, number of (class, field) pairs checked)."""
    out, n = [], 0
    for r in rows:
        if not isinstance(r, dict) or r.get("kind") != "not_modelled":
            continue
        dn = r.get("do_not")
        if not isinstance(dn, dict):
            continue
        cls = dn.get("class")
        if cls not in tree:
            out.append(f"C4 {r['id']}: do_not names class {cls!r}, which the schema does "
                       f"not hold, so the rule cannot be checked. do_not: \"{dn.get('line')}\"")
            continue
        for f in dn.get("fields") or []:
            n += 1
            owner = declares(tree, cls, f)
            if owner:
                via = "" if owner == cls else f" (inherited from {owner})"
                out.append(f"C4 {r['id']}: {cls} declares {f!r}{via}, which the register "
                           f"forbids. do_not: \"{dn.get('line')}\"")
    return out, n


def open_rows(text):
    """The row numbers listed in the OPEN_WORK index's "## OPEN" section (its
    own table and the other-repository table), not the COMPLETED rows or the
    verbatim decisions below them."""
    head = text.split("\n## OPEN", 1)[-1].split("\n## ", 1)[0]
    out = set()
    for ln in head.splitlines():
        m = re.match(r"\|\s*(\d+)\s*\|", ln)
        if m:
            out.add(int(m.group(1)))
    return out


def check_open_work(rows, known):
    """C5. Returns (failures, rows checked)."""
    out, n = [], 0
    for r in rows:
        if not (isinstance(r, dict) and r.get("kind") == "awaiting_home"):
            continue
        ow = r.get("open_work")
        if not isinstance(ow, int) or isinstance(ow, bool):
            continue  # C1 reports it
        n += 1
        if ow not in known:
            out.append(f"C5 {r['id']}: open_work #{ow} is not an OPEN row of "
                       f"schemas/V_eta_OPEN_WORK.md")
    return out, n


def main():
    reg = _load(REGISTER)
    rows = reg.get("rows") if isinstance(reg.get("rows"), list) else []
    print(f"DENOMINATOR: {len(rows)} carry register row(s) read from "
          f"schemas/V_eta_carry_register.json")
    failures = check_shape(reg)
    by_kind = {k: sum(1 for r in rows if isinstance(r, dict) and r.get("kind") == k)
               for k in KINDS}
    print("  by kind: " + ", ".join(f"{k} {n}" for k, n in by_kind.items()))
    ledger = _load(LEDGER)
    v1 = {r.get("v1_class") for r in ledger.get("rows", [])}
    print(f"C2: {len(rows)} v1_class value(s) compared with {len(v1)} ledger v1 class(es)")
    failures += check_v1_classes(rows, v1)
    dfail, ok = check_decisions(rows)
    print(f"C3: {len(rows)} decision citation(s), {ok} resolved")
    failures += dfail
    tree = class_tree()
    nfail, n = check_do_not(rows, tree)
    n_nm = by_kind["not_modelled"]
    print(f"C4: {n_nm} not_modelled row(s), {n} (class, field) pair(s) checked "
          f"against {len(tree)} class(es)")
    failures += nfail
    with open(OPEN_WORK, encoding="utf-8") as f:
        known = open_rows(f.read())
    ofail, n_ow = check_open_work(rows, known)
    print(f"C5: {n_ow} awaiting_home open_work number(s) checked against "
          f"{len(known)} OPEN row(s) of V_eta_OPEN_WORK.md")
    failures += ofail
    n_prop = sum(1 for r in rows if isinstance(r, dict) and r.get("kind_basis") == "proposed")
    print(f"  kinds proposed by Claude, not stated by the decision: {n_prop} of {len(rows)}")
    for f in failures:
        print("  FAIL " + f)
    print(f"carry register rows read: {len(rows)}")
    if failures:
        print(f"FAIL: {len(failures)} problem(s)")
        return 1
    print("OK: every row well formed, every decision resolves, no not_modelled line contradicted")
    return 0


if __name__ == "__main__":
    sys.exit(main())
