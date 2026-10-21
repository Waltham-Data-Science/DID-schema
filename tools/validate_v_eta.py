#!/usr/bin/env python3
"""Validate schemas/V_eta, which is the SOURCE (OPEN_WORK #128, 2026-10-21).

Until 2026-10-21 `tools/build_v_eta.py` rebuilt `schemas/V_eta/` from V_zeta by
replaying ~43 dated sections. The built JSON is now edited directly, and this
tool checks every rule the builder used to guarantee by construction.

A change to a class: edit its JSON under schemas/V_eta/<tier>/, add or edit
its `index.json` entry's `disposition` if the class is new, then run
`python3 tools/gates.py`.

TWO KINDS OF THING
------------------
RULES (R1-R16) are checks only. A failure names the file and what is wrong;
the fix is an edit to the JSON.

DERIVED pieces (D1-D4) are copies of a fact held elsewhere, so they are
written, not hand-edited:
  D1  index.json: tier, class_version, maturity_level, superclasses and path of
      every class, read from its file. `disposition` / `disposition_note` are
      DATA in index.json (the source of a class's disposition) and are kept.
  D2  stable/term_registry_meta.json: schemas/V_eta_term_registry.json, with
      a header, for did2.build.
  D3  directed_relation.relation / undirected_relation.relation binding values:
      the registry's relation_bindings rows of that carrier, in order.
  D4  `ndi_mustBeNonEmpty` on depends_on entries: NDI's required-ness from
      schemas/V_eta_ndi_ground_truth.json (tools/ndi_required_stamp.py).
Default mode writes them; --check writes nothing and fails if any differs.
The registry's `strength` column is derived too, by
tools/regen_binding_strengths.py (its own gates step).

The data the rules need that is not in the tree (retired class names, the
rename map, the v1 edge families) is in tools/veta_record.py.

It prints its denominator first (Operating Rule 5).

Usage:  python3 tools/validate_v_eta.py           # write D1-D4, check all
        python3 tools/validate_v_eta.py --check   # write nothing
"""
import argparse
import copy
import glob
import importlib.util
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VETA = os.path.join(ROOT, "schemas", "V_eta")
TERM_SOURCE = os.path.join(ROOT, "schemas", "V_eta_term_registry.json")
GT_PATH = os.path.join(ROOT, "schemas", "V_eta_ndi_ground_truth.json")
TARGETS_PATH = os.path.join(ROOT, "schemas", "V_eta_migration_targets.json")


def _load_module(name, fname):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fname))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


REC = _load_module("_veta_record", "veta_record.py")
TIERS = REC.TIERS
META_FILES = REC.META_FILES

# Files written by something other than json.dump(indent=4): ndi_reserved_keys
# is NDI's file copied verbatim, the term registry copy keeps non-ASCII text.
VERBATIM = {"ndi_reserved_keys.json"}
NON_ASCII = {"term_registry_meta.json"}
DISPOSITIONS = {"persist", "retire", "in_progress"}
PASSES = {"assertions", "distributive", "context", "nothing"}
ENTRY_LISTS = ("conditions", "parameters")
# the time_reference families governed by the uniqueness rule (#52, CHANGE 5)
REFERENT_UNIQUE = {("directed_relation", "time_reference_id"): "value.clock",
                   ("interaction", "time_reference_id"): "value.clock",
                   ("entity", "time_reference_id"): "value.clock"}


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def dumps(obj, ascii_=True):
    return json.dumps(obj, indent=4, ensure_ascii=ascii_) + "\n"


def walk_fields(fields, path=""):
    for f in fields or []:
        p = path + f["name"]
        yield p, f
        yield from walk_fields(f.get("fields"), p + ".")


class Tree:
    """Every class and meta file under the tiers, read once."""

    def __init__(self, veta):
        self.veta = veta
        self.classes = {}      # name -> (tier, path, doc)
        self.meta = {}         # basename -> (tier, path, doc)
        self.dupes = []
        self.unreadable = []
        for tier in TIERS:
            for p in sorted(glob.glob(os.path.join(veta, tier, "*.json"))):
                base = os.path.basename(p)
                try:
                    d = load(p)
                except (OSError, ValueError) as e:
                    self.unreadable.append(f"{p}: {e}")
                    continue
                if base in META_FILES:
                    self.meta[base] = (tier, p, d)
                    continue
                cn = (d.get("document_class") or {}).get("class_name")
                if cn in self.classes:
                    self.dupes.append(cn)
                self.classes[cn] = (tier, p, d)

    def doc(self, name):
        return self.classes[name][2]

    def chain(self, name, _seen=None):
        """Every ancestor, nearest first, each once."""
        out = []
        for s in self.doc(name)["document_class"]["superclasses"]:
            s = s["class_name"]
            if s in self.classes and s not in out:
                out.append(s)
                out += [x for x in self.chain(s) if x not in out]
        return out


# ---------------------------------------------------------------------------
# RULES. Each returns (n_checked, [failure, ...]).
# ---------------------------------------------------------------------------

def r1_format(t):
    """Every file under a tier is json.dump(indent=4) + newline, so a hand edit
    diffs like a build did."""
    bad, n = [], 0
    for tier in TIERS:
        for p in sorted(glob.glob(os.path.join(t.veta, tier, "*.json"))):
            base = os.path.basename(p)
            if base in VERBATIM:
                continue
            n += 1
            with open(p, encoding="utf-8") as f:
                s = f.read()
            if dumps(json.loads(s), base not in NON_ASCII) != s:
                bad.append(f"{tier}/{base} is not indent-4 json.dump output + newline")
    p = os.path.join(t.veta, "index.json")
    n += 1
    with open(p, encoding="utf-8") as f:
        s = f.read()
    if dumps(json.loads(s)) != s:
        bad.append("index.json is not indent-4 json.dump output + newline")
    return n, bad


def r2_identity(t):
    """class_name is the file name; one class per name across the tiers."""
    bad = [f"unreadable: {u}" for u in t.unreadable]
    bad += [f"{n} is declared twice" for n in t.dupes]
    for n, (tier, p, d) in t.classes.items():
        if n is None:
            bad.append(f"{p} has no document_class.class_name")
        elif os.path.basename(p) != n + ".json":
            bad.append(f"{p} declares class_name {n!r}")
    for sub in os.listdir(t.veta):
        full = os.path.join(t.veta, sub)
        if os.path.isdir(full) and sub not in TIERS and sub not in (
                "conversions", "microschemas", "examples"):
            bad.append(f"unexpected directory {sub}/")
    return len(t.classes), bad


def r3_fields(t, meta):
    """Every field, at any depth, has the meta-schema's required keys and a type
    from its enum; a char-like scalar has a text blank and default."""
    fd = meta["$defs"]["field_definition"]
    required = fd.get("required", [])
    types = set(fd["properties"]["type"]["enum"])
    bad, n = [], 0
    for cn, (_, _, d) in t.classes.items():
        for path, f in walk_fields(d.get("fields")):
            n += 1
            miss = [k for k in required if k not in f]
            if miss:
                bad.append(f"{cn}.{path} lacks {miss}")
            if f.get("type") not in types:
                bad.append(f"{cn}.{path} has type {f.get('type')!r}, not in the meta enum")
            if (f.get("type") in REC._CHARLIKE_BLANK_TYPES and f.get("mustBeScalar", True)
                    and not (isinstance(f.get("blank_value"), str)
                             and isinstance(f.get("default_value"), str))):
                bad.append(f"{cn}.{path} is {f['type']} but its blank/default is not text")
    return n, bad


def r4_references(t):
    """Every superclass and every must_refer_to_document_class (a comma list)
    names a class in the tree."""
    bad, n = [], 0
    for cn, (_, _, d) in t.classes.items():
        for s in d["document_class"].get("superclasses", []):
            n += 1
            if s["class_name"] not in t.classes:
                bad.append(f"{cn} names superclass {s['class_name']!r}, not in the tree")
        for e in d.get("depends_on", []):
            for target in filter(None, (e.get("must_refer_to_document_class") or "").split(",")):
                n += 1
                if target.strip() not in t.classes:
                    bad.append(f"{cn}.{e['name']} must refer to {target!r}, not in the tree")
    return n, bad


def r5_retired(t):
    """A class or edge name the builder retired does not come back."""
    bad = [f"{n} is a retired class name (tools/veta_record.py RETIRED_CLASSES)"
           for n in sorted(set(t.classes) & REC.RETIRED_CLASSES)]
    n = 0
    for cn, (_, _, d) in t.classes.items():
        for e in d.get("depends_on", []):
            n += 1
            if e["name"] in REC.RETIRED_EDGES:
                bad.append(f"{cn} declares retired edge {e['name']!r}")
    return len(t.classes) + n, bad


def r6_edges(t):
    """T15: a repeated edge has one name, not `name_#` (three v1 tombstone
    families excepted); min_count/max_count only beside `multiple`."""
    bad, n = [], 0
    for cn, (_, _, d) in t.classes.items():
        for e in d.get("depends_on", []):
            n += 1
            if e["name"].endswith("_#") and e["name"] not in REC.T15_V1_FAMILIES:
                bad.append(f"{cn}.{e['name']} is numbered (T15)")
            if ("min_count" in e or "max_count" in e) and not e.get("multiple") \
                    and not e["name"].endswith("_#"):
                bad.append(f"{cn}.{e['name']} carries min/max_count without `multiple`")
    return n, bad


def r7_inheritance(t):
    """An inherited edge is not redeclared (audit 2 D12: tighten it with
    `require_inherited`), and `require_inherited` names something inherited
    and not already required."""
    bad, n = [], 0
    for cn, (_, _, d) in t.classes.items():
        mine = {e["name"] for e in d.get("depends_on", [])}
        anc = t.chain(cn)
        for s in anc:
            for e in t.doc(s).get("depends_on", []):
                n += 1
                if e["name"] in mine and (cn, e["name"]) not in REC.A2_V1_REDECLARED:
                    bad.append(f"{cn} redeclares {e['name']!r} inherited from {s}")
        if "require_inherited" in d:
            inh = {}
            for s in anc:
                for x in t.doc(s).get("depends_on", []) + t.doc(s).get("fields", []):
                    inh.setdefault(x["name"], x.get("mustBeNonEmpty", False))
            for name in d["require_inherited"]:
                n += 1
                if name not in inh:
                    bad.append(f"{cn}.require_inherited names {name!r}, not inherited")
                elif inh[name]:
                    bad.append(f"{cn}.require_inherited {name!r} is already required")
    return n, bad


def r8_referent_unique(t):
    """The time_reference uniqueness rule (#52) is declared on exactly its
    three families."""
    found = {}
    for cn, (_, _, d) in t.classes.items():
        for e in d.get("depends_on", []):
            if "referent_unique_by" in e:
                found[(cn, e["name"])] = e["referent_unique_by"]
    bad = []
    if found != REFERENT_UNIQUE:
        bad.append(f"referent_unique_by is declared on {sorted(found.items())}, "
                   f"expected {sorted(REFERENT_UNIQUE.items())}")
    return len(found), bad


def r9_bindings(t, meta):
    """A binding sits on an ontology_term, uses only the meta-schema's keys,
    states a strength, and lists its values as {node, name} terms."""
    allowed = set(meta["$defs"]["field_definition"]["properties"]["constraints"]
                  ["properties"]["binding"]["properties"])
    bad, n = [], 0
    for cn, (_, _, d) in t.classes.items():
        for path, f in walk_fields(d.get("fields")):
            b = (f.get("constraints") or {}).get("binding")
            if b is None:
                continue
            n += 1
            where = f"{cn}.{path}"
            if f["type"] != "ontology_term":
                bad.append(f"{where} is bound but typed {f['type']!r}")
            extra = set(b) - allowed
            if extra:
                bad.append(f"{where} binding has keys the meta-schema lacks: {sorted(extra)}")
            if b.get("strength") not in ("preferred", "required"):
                bad.append(f"{where} binding strength is {b.get('strength')!r}")
            for v in b.get("values", []):
                if not (isinstance(v, dict) and {"node", "name"} <= set(v)):
                    bad.append(f"{where} binding value {v!r} is not a {{node, name}} term")
    return n, bad


def r10_registry(t, reg):
    """Every relation row says what it `passes` (12.16: no default); the
    contributor roles are the CRediT set, each with a node."""
    bad, n = [], 0
    for r in reg.get("relation_bindings", []):
        n += 1
        if r.get("passes") not in PASSES:
            bad.append(f"relation `{r['relation']['name']}` passes {r.get('passes')!r}, "
                       f"not one of {sorted(PASSES)}")
    roles = next((f for f in t.doc("directed_relation")["fields"] if f["name"] == "roles"), None)
    if roles is None:
        bad.append("directed_relation declares no `roles`")
    else:
        vals = roles["constraints"]["binding"].get("values", [])
        n += len(vals)
        if sorted(v["name"] for v in vals) != sorted(REC.CREDIT_ROLES):
            bad.append("directed_relation.roles values are not the CRediT roles")
        bad += [f"contributor role {v['name']!r} has no node" for v in vals if not v.get("node")]
    return n, bad


def _prefix_index(prefixes):
    ix, clash = {}, []
    for k, e in prefixes.items():
        names = [k] + list(e.get("synonyms", []))
        if "written_as" not in e:
            names.append(e.get("spelling") or k)
        for nm in names:
            old = ix.setdefault(nm.lower(), k)
            if old != k:
                clash.append(f"prefix name {nm!r} names both {old!r} and {k!r}")
    return ix, clash


def r11_curies(t, reg, curie):
    """Prefix spelling (signed 2026-10-19): no two prefix entries share a name,
    and every term node in the classes and the binding registry has a
    registered prefix, written in its entry's spelling."""
    prefixes = curie.get("prefixes", {})
    ix, bad = _prefix_index(prefixes)
    spelled = {e.get("spelling") or k for k, e in prefixes.items() if "written_as" not in e}
    nodes = []

    def scan(x, where):
        if isinstance(x, dict):
            for k, v in x.items():
                if k == "node" and isinstance(v, str) and v:
                    nodes.append((where, v))
                else:
                    scan(v, where)
        elif isinstance(x, list):
            for v in x:
                scan(v, where)
    for cn, (_, _, d) in t.classes.items():
        scan(d, cn)
    scan(reg, "binding_registry_meta")
    for where, v in nodes:
        if ":" not in v:
            bad.append(f"{where}: node {v!r} is not a CURIE")
            continue
        p = v.split(":", 1)[0]
        if p.lower() not in ix:
            bad.append(f"{where}: node {v!r} has an unregistered prefix")
        elif p not in spelled:
            bad.append(f"{where}: node {v!r} is not written in its prefix's spelling")
    return len(nodes), bad


def r12_vocabulary_slots(t):
    """`source_unit` is a bound term with a blank-term default (12.19); every
    `variable` of a statement, key, condition or method parameter is a bound
    term (T8 parity, 2026-10-04)."""
    blank = {"node": "", "name": ""}
    bad, n = [], 0
    for cn, (_, _, d) in t.classes.items():
        for path, f in walk_fields(d.get("fields")):
            parts = path.split(".")
            b = (f.get("constraints") or {}).get("binding") or {}
            if f["name"] == "source_unit":
                n += 1
                if f["type"] != "ontology_term" or b.get("node_form") != "curie" \
                        or f.get("blank_value") != blank or f.get("default_value") != blank:
                    bad.append(f"{cn}.{path} is not a bound blank-default term")
            if f["name"] == "variable" and (
                    (cn == "statement" and path == "variable")
                    or (len(parts) > 1 and parts[-2] in ("keys",) + ENTRY_LISTS)):
                n += 1
                if f["type"] != "ontology_term" or b.get("node_form") != "curie":
                    bad.append(f"{cn}.{path} is not a bound term")
    return n, bad


def _shape(x):
    if isinstance(x, dict):
        return {k: _shape(v) for k, v in x.items()
                if k not in ("documentation", "mustBeNonEmpty")}
    if isinstance(x, list):
        return [_shape(v) for v in x]
    return x


def r13_one_shape(t):
    """ONE method shape (2026-10-21) and ONE entry (data_body AMENDMENT 3): every
    inline `method` block {term, parameters} and the `method` document's own
    term + parameters are the same shape; every `conditions` and `parameters`
    entry list has the same fields. Documentation and required-ness may differ."""
    blocks, entries = {}, {}
    for cn, (_, _, d) in t.classes.items():
        if cn == "method":
            blocks[cn] = [f for f in d["fields"] if f["name"] in ("term", "parameters")]
        for path, f in walk_fields(d.get("fields")):
            subs = [x["name"] for x in f.get("fields") or []]
            if f["name"] == "method" and f["type"] == "structure" and subs == ["term", "parameters"]:
                blocks[f"{cn}.{path}"] = f["fields"]
            if f["name"] in ENTRY_LISTS and "variable" in subs:
                entries[f"{cn}.{path}"] = f["fields"]
    bad = []
    for label, group in (("method block", blocks), ("entry list", entries)):
        shapes = {}
        for where, x in group.items():
            shapes.setdefault(json.dumps(_shape(x), sort_keys=True), []).append(where)
        if len(shapes) > 1:
            bad.append(f"{len(shapes)} {label} shapes: "
                       + " | ".join(", ".join(v) for v in shapes.values()))
    if "method" not in blocks or len(blocks) < 2:
        bad.append(f"expected the method document and inline method blocks, found {sorted(blocks)}")
    return len(blocks) + len(entries), bad


def r14_values(t):
    """Every direct subclass of `value` declares exactly one `value` field."""
    bad, n = [], 0
    for cn, (_, _, d) in t.classes.items():
        if any(s["class_name"] == "value" for s in d["document_class"]["superclasses"]):
            n += 1
            k = sum(1 for f in d["fields"] if f["name"] == "value")
            if k != 1:
                bad.append(f"{cn} declares {k} `value` fields")
    return n, bad


def r15_value_sets(reg):
    """A binding row's closed `values` list (Jess Haley, 2026-10-21): a list of
    {node, name} terms, each the one the term registry holds under that node
    and name; an empty list is legal (nothing admitted yet). A row marked
    `term_valued: false` (its value is data, not a term) names no admissible
    set at all."""
    src = load(TERM_SOURCE)
    by_node = {(t.get("node") or "").lower(): t for t in src.get("terms", []) if t.get("node")}
    bad, n = [], 0
    for r in reg.get("subject_statement_bindings", []):
        var = (r.get("variable") or {}).get("name", "?")
        if r.get("term_valued") is False:
            sets = [k for k in ("values", "ontology", "root_node", "node_form") if k in r]
            if sets:
                bad.append(f"binding `{var}` is term_valued false but names an admissible set: {sets}")
            continue
        if "values" not in r:
            continue
        if not isinstance(r["values"], list):
            bad.append(f"binding `{var}` values is not a list")
            continue
        seen = set()
        for v in r["values"]:
            n += 1
            if not (isinstance(v, dict) and {"node", "name"} <= set(v)):
                bad.append(f"binding `{var}` value {v!r} is not a {{node, name}} term")
                continue
            t = by_node.get(v["node"].lower())
            if t is None:
                bad.append(f"binding `{var}` value {v['node']} is not in the term registry")
            elif t["name"] != v["name"]:
                bad.append(f"binding `{var}` value {v['node']} is named {v['name']!r}, "
                           f"registered as {t['name']!r}")
            if v["node"].lower() in seen:
                bad.append(f"binding `{var}` lists {v['node']} twice")
            seen.add(v["node"].lower())
    return n, bad


VALUE_RULE = "value_inline_or_body"


def _is_blank(x):
    """Nothing filled: None, empty text, an empty list or structure, or a
    structure / list whose every leaf is blank ({node: '', name: ''} is a blank
    term). False and 0 are values, not blanks."""
    if x is None:
        return True
    if isinstance(x, str):
        return x == ""
    if isinstance(x, dict):
        return all(_is_blank(v) for v in x.values())
    if isinstance(x, list):
        return all(_is_blank(v) for v in x)
    return False


def value_inline_or_body(doc):
    """THE DOCUMENT CHECK for rule `value_inline_or_body` (Jess Haley,
    2026-10-21; decided, not signed; data_body AMENDMENT 5): a value document is
    inline (its `value` filled) or in data bodies (`data_body` true), never
    neither. DOC is the document's properties as a dict; `value` and
    `data_body` are read at the top level. Returns a list of failures (empty
    when the document passes). The enforcing validator is DID-matlab's; this is
    the reference statement of the rule that the tests pin."""
    if doc.get("data_body") is True:
        return []
    if _is_blank(doc.get("value")):
        return [(f"rule {VALUE_RULE}: `value` is empty and `data_body` is not true "
                 "-- the value is neither inline nor in data bodies")]
    return []


def r16_value_inline_or_body(t):
    """data_body AMENDMENT 5 (2026-10-21): `value` declares the rule
    `value_inline_or_body` over `value` and `data_body`, and NO class under
    `value` makes its inline `value` required -- the rule replaces the
    per-class `mustBeNonEmpty`, and a required inline value would refuse every
    body-backed document of that class."""
    bad = []
    rules = {r["name"]: r for r in t.doc("value").get("rules", [])}
    r = rules.get(VALUE_RULE)
    if r is None:
        bad.append(f"value declares no rule {VALUE_RULE!r}")
    elif sorted(r["fields"]) != ["data_body", "value"]:
        bad.append(f"rule {VALUE_RULE} covers {r['fields']}, expected value + data_body")
    n = 1
    for cn, (_, _, d) in t.classes.items():
        if cn == "value" or "value" not in t.chain(cn):
            continue
        for f in d.get("fields", []):
            if f["name"] == "value":
                n += 1
                if f.get("mustBeNonEmpty"):
                    bad.append(f"{cn}.value is mustBeNonEmpty; rule {VALUE_RULE} on `value` "
                               "replaces it (set it false)")
    return n, bad


RULES = [
    ("R1 canonical JSON layout", lambda c: r1_format(c["tree"])),
    ("R2 one class per name, named as its file", lambda c: r2_identity(c["tree"])),
    ("R3 field definitions", lambda c: r3_fields(c["tree"], c["meta"])),
    ("R4 superclasses and edge targets resolve", lambda c: r4_references(c["tree"])),
    ("R5 retired names stay retired", lambda c: r5_retired(c["tree"])),
    ("R6 edge names (T15) and cardinality", lambda c: r6_edges(c["tree"])),
    ("R7 inherited edges (audit 2 D12)", lambda c: r7_inheritance(c["tree"])),
    ("R8 the time_reference uniqueness rule (#52)", lambda c: r8_referent_unique(c["tree"])),
    ("R9 bindings", lambda c: r9_bindings(c["tree"], c["meta"])),
    ("R10 relation `passes` and contributor roles", lambda c: r10_registry(c["tree"], c["reg"])),
    ("R11 CURIE prefix spelling", lambda c: r11_curies(c["tree"], c["reg"], c["curie"])),
    ("R12 source_unit and variable are bound terms", lambda c: r12_vocabulary_slots(c["tree"])),
    ("R13 one method shape, one entry", lambda c: r13_one_shape(c["tree"])),
    ("R14 one `value` per value class", lambda c: r14_values(c["tree"])),
    ("R15 closed value sets are registered terms", lambda c: r15_value_sets(c["reg"])),
    ("R16 a value is inline or in bodies (value_inline_or_body)",
     lambda c: r16_value_inline_or_body(c["tree"])),
]


# ---------------------------------------------------------------------------
# DERIVED. Each returns {abs path: new text} for the files it would write.
# ---------------------------------------------------------------------------

def d1_index(t):
    p = os.path.join(t.veta, "index.json")
    idx = load(p)
    old = {e["class_name"]: e for e in idx["schemas"]}
    bad, schemas = [], []
    for tier in TIERS:
        for f in sorted(glob.glob(os.path.join(t.veta, tier, "*.json"))):
            base = os.path.basename(f)
            if base in META_FILES:
                schemas.append({"class_name": base[:-5], "tier": tier,
                                "class_version": None, "maturity_level": None,
                                "superclasses": [], "path": f"schemas/V_eta/{tier}/{base}",
                                "is_meta": True, "disposition": "persist"})
                continue
            dc = load(f)["document_class"]
            prev = old.get(dc["class_name"], {})
            disp = prev.get("disposition")
            if disp not in DISPOSITIONS:
                bad.append(f"index.json: {dc['class_name']} needs a `disposition`, one of "
                           f"{sorted(DISPOSITIONS)} (it is data: add it by hand)")
            e = {"class_name": dc["class_name"], "tier": tier,
                 "class_version": dc["class_version"],
                 "maturity_level": dc["maturity_level"],
                 "superclasses": [s["class_name"] for s in dc["superclasses"]],
                 "path": f"schemas/V_eta/{tier}/{base}", "disposition": disp}
            if "disposition_note" in prev:
                e["disposition_note"] = prev["disposition_note"]
            schemas.append(e)
    schemas.sort(key=lambda e: (0 if e.get("is_meta") else 1, e["class_name"]))
    idx["schemas"] = schemas
    return {p: dumps(idx)}, bad


def d2_term_registry(t):
    src = load(TERM_SOURCE)
    out = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": "https://did-schema.example.org/meta/term_registry_meta.json",
        "title": "Term registry for DID/NDI V_eta",
        "description": src["description"],
        "terms": src["terms"],
    }
    return {os.path.join(t.veta, "stable", "term_registry_meta.json"): dumps(out, False)}, []


def d3_relation_values(t, reg):
    out, bad = {}, []
    for carrier in ("directed_relation", "undirected_relation"):
        _, p, d = t.classes[carrier]
        d = copy.deepcopy(d)
        rows = [r["relation"] for r in reg["relation_bindings"] if r["class"] == carrier]
        if not rows:
            bad.append(f"no registry relation_bindings rows for {carrier}")
        f = next(x for x in d["fields"] if x["name"] == "relation")
        f["constraints"]["binding"]["values"] = [{"node": r["node"], "name": r["name"]}
                                                 for r in rows]
        out[p] = dumps(d)
    return out, bad


def d4_ndi_stamp(t, report, overrides):
    """Strip every ndi_mustBeNonEmpty, re-stamp from the ground truth, in a
    scratch copy; return every class file's text. OVERRIDES (path -> text) are
    the earlier derived pieces' output, so D4 stamps what D3 wrote."""
    stamp = _load_module("_veta_ndi_required_stamp", "ndi_required_stamp.py")
    tmp = tempfile.mkdtemp(prefix="veta-stamp-")
    try:
        scratch = os.path.join(tmp, "V_eta")
        for tier in TIERS:
            os.makedirs(os.path.join(scratch, tier))
        for tier, p, d in t.classes.values():
            d = json.loads(overrides[p]) if p in overrides else copy.deepcopy(d)
            for e in d.get("depends_on", []):
                e.pop(stamp.MARKER, None)
            with open(os.path.join(scratch, tier, os.path.basename(p)), "w") as f:
                f.write(dumps(d))
        res = stamp.stamp_ndi_required(scratch, GT_PATH, REC.RENAME, TIERS, META_FILES,
                                       deleted_phase8=REC._DELETE_PHASE8,
                                       targets_path=TARGETS_PATH)
        if report:
            for line in stamp.render_stamp_report(res):
                print(line)
        out = {}
        for tier, p, _ in t.classes.values():
            with open(os.path.join(scratch, tier, os.path.basename(p))) as f:
                out[p] = f.read()
        bad = [] if res.get("ground_truth_readable") else [
            "the NDI ground truth is unreadable; the stamp cannot be derived"]
        return out, bad
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="write nothing; fail if a derived piece is stale")
    ap.add_argument("--veta", default=VETA, help=argparse.SUPPRESS)
    ap.add_argument("--quiet-stamp", action="store_true",
                    help="do not print the NDI required-ness stamp report")
    a = ap.parse_args(argv)

    t = Tree(a.veta)
    meta = t.meta["did_schema_meta.json"][2]
    reg = t.meta["binding_registry_meta.json"][2]
    curie = t.meta["CURIE_lookups_meta.json"][2]
    ctx = {"tree": t, "meta": meta, "reg": reg, "curie": curie}
    print(f"DENOMINATOR: {len(t.classes)} class file(s) and {len(t.meta)} meta file(s) "
          f"read from schemas/V_eta/{{{','.join(TIERS)}}}; {len(t.unreadable)} unreadable; "
          f"{len(RULES)} rule(s), 4 derived piece(s)")

    failed = 0
    for label, rule in RULES:
        n, bad = rule(ctx)
        status = "OK  " if not bad else "FAIL"
        print(f"  {status} {label}: {n} checked, {len(bad)} failure(s)")
        for b in bad[:40]:
            print(f"         {b}")
        if len(bad) > 40:
            print(f"         ... and {len(bad) - 40} more")
        failed += bool(bad)

    derived = [("D1 index.json", lambda: d1_index(t)),
               ("D2 term_registry_meta.json", lambda: d2_term_registry(t)),
               ("D3 relation binding values", lambda: d3_relation_values(t, reg)),
               ("D4 ndi_mustBeNonEmpty stamp",
                lambda: d4_ndi_stamp(t, not a.quiet_stamp, dict(writes)))]
    writes = {}
    for label, fn in derived:
        files, bad = fn()
        stale = []
        for p, text in files.items():
            cur = None
            if os.path.exists(p):
                with open(p, encoding="utf-8") as fh:
                    cur = fh.read()
            if p in writes and writes[p] != text:
                writes[p] = text        # D4 restamps what D3 wrote
            elif cur != text:
                stale.append(os.path.relpath(p, ROOT))
                writes[p] = text
        verdict = ("FAIL" if bad else ("STALE" if stale and a.check else
                                       ("WROTE" if stale else "OK  ")))
        print(f"  {verdict} {label}: {len(files)} file(s) derived, {len(stale)} differ")
        for b in bad:
            print(f"         {b}")
        for s in stale:
            print(f"         {'stale' if a.check else 'rewritten'}: {s}")
        failed += bool(bad) or (a.check and bool(stale))
    if not a.check:
        for p, text in writes.items():
            with open(p, "w", encoding="utf-8") as f:
                f.write(text)

    print(f"V_eta validated: {len(t.classes)} schemas, "
          f"{failed} rule(s) or derived piece(s) failing")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
