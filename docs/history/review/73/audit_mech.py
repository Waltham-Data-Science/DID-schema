"""Mechanical audit of the V_eta persist set. Read-only; prints findings.
Every check prints its denominator first (Operating Rule 5)."""
import json, glob, os, re, collections

ROOT = "/home/user/DID-schema/schemas/V_eta"
idx = json.load(open(os.path.join(ROOT, "index.json")))["schemas"]
BY = {r["class_name"]: r for r in idx}
DISP = {r["class_name"]: r["disposition"] for r in idx}
META = {r["class_name"] for r in idx if r.get("is_meta")}
PERSIST = sorted(c for c, d in DISP.items() if d == "persist" and c not in META)
DOC = {}
for r in idx:
    p = os.path.join("/home/user/DID-schema", r["path"])
    DOC[r["class_name"]] = json.load(open(p))

def supers(c):
    return [s["class_name"] for s in DOC[c].get("document_class", {}).get("superclasses", [])]

def chain(c, seen=None):
    seen = seen if seen is not None else []
    for s in supers(c):
        if s in DOC and s not in seen:
            seen.append(s)
            chain(s, seen)
    return seen

def walk_fields(fields, prefix=""):
    for f in fields or []:
        path = prefix + f["name"]
        yield path, f
        yield from walk_fields(f.get("fields"), path + ".")

F = collections.defaultdict(list)
def find(check, cls, msg):
    F[check].append((cls, msg))

print(f"DENOMINATOR: {len(idx)} index rows; {len(PERSIST)} persist classes "
      f"(meta excluded: {sorted(META)})")

# 1. superclasses outside the persist set
for c in PERSIST:
    for s in supers(c):
        if s not in DOC:
            find("super_missing", c, f"superclass `{s}` does not exist")
        elif DISP.get(s) != "persist":
            find("super_not_persist", c, f"superclass `{s}` is {DISP.get(s)}")

# 2. depends_on targets
for c in PERSIST:
    for d in DOC[c].get("depends_on", []):
        tgt = d.get("must_refer_to_document_class")
        if not tgt:
            find("dep_untyped", c, f"edge `{d['name']}` has no must_refer_to_document_class")
            continue
        for t in [x.strip() for x in tgt.split(",")]:
            if t not in DOC:
                find("dep_target_missing", c, f"edge `{d['name']}` -> `{t}` (no such class)")
            elif DISP.get(t) != "persist":
                find("dep_target_not_persist", c, f"edge `{d['name']}` -> `{t}` ({DISP.get(t)})")
        n = d["name"]
        if n.endswith("_#") and not d.get("multiple"):
            find("family_no_multiple", c, f"`{n}` is a _# family without multiple")
        if d.get("multiple") and not n.endswith("_#"):
            find("multiple_not_family", c, f"`{n}` has multiple but no _#")
        if re.search(r"_\d+$", n):
            find("literal_numbered_edge", c, f"`{n}`")
        if not n.endswith("_id") and not n.endswith("_#"):
            find("edge_name_shape", c, f"`{n}` (not *_id / *_#)")
        if not (d.get("documentation") or "").strip():
            find("edge_undocumented", c, f"`{n}`")
        if re.search(r"[A-Z]", n):
            find("edge_camel", c, f"`{n}`")

# 3. field names
for c in PERSIST:
    for path, f in walk_fields(DOC[c].get("fields")):
        leaf = path.split(".")[-1]
        if re.match(r"(is|has|do|does)_", leaf) or re.match(r"(is|has)[a-z]", leaf) and leaf in ("isspike", "israster"):
            find("bool_prefix_T13", c, f"`{path}`")
        if re.search(r"[A-Z]", leaf):
            find("field_camel", c, f"`{path}`")
        if leaf.startswith("ndi_"):
            find("ndi_prefix_field", c, f"`{path}` (implementation class name as a field)")
        if leaf in ("axes", "is_cache", "timed_sequence_id", "is_approximate", "statement", "epochprobemap", "dtype", "color_model"):
            find("renamed_remnant", c, f"`{path}`")
        if not (f.get("documentation") or "").strip():
            find("field_undocumented", c, f"`{path}`")
        doc = (f.get("documentation") or "").lower()
        if f.get("type") in ("char", "string") and re.search(r"serializ|eval'd|<tab>|comma-separated|comma-joined|json string", doc):
            find("serialized_string_T14", c, f"`{path}` ({f.get('type')}): {doc[:100]}")

# 4. field collision with an ancestor
own = {c: {p for p, _ in walk_fields(DOC[c].get("fields")) if "." not in p} for c in DOC}
for c in PERSIST:
    for a in chain(c):
        clash = own[c] & own.get(a, set())
        for x in sorted(clash):
            find("field_redeclared_from_ancestor", c, f"`{x}` also declared on ancestor `{a}`")
# 4b. dep redeclared from ancestor
owndep = {c: {d["name"] for d in DOC[c].get("depends_on", [])} for c in DOC}
for c in PERSIST:
    for a in chain(c):
        for x in sorted(owndep[c] & owndep.get(a, set())):
            find("dep_redeclared_from_ancestor", c, f"`{x}` also declared on ancestor `{a}`")
# 4c. two parents supplying the same field/dep (diamond collisions)
for c in PERSIST:
    ss = supers(c)
    for i in range(len(ss)):
        for j in range(i + 1, len(ss)):
            a, b = ss[i], ss[j]
            if a not in DOC or b not in DOC:
                continue
            fa = set().union(*[own[x] for x in [a] + chain(a)])
            fb = set().union(*[own[x] for x in [b] + chain(b)])
            common_anc = set([a] + chain(a)) & set([b] + chain(b))
            shared = (fa & fb) - set().union(*[own[x] for x in common_anc]) if common_anc else fa & fb
            for x in sorted(shared):
                find("diamond_field", c, f"`{x}` arrives from both `{a}` and `{b}`")

# 5. leaf grammar (T3/T11): statement leaf = direction x data type
DIRS = {"subject_observation": "observation", "subject_manipulation": "manipulation",
        "subject_assertion": "assertion", "subject_calculation": "calculation"}
DT = {c for c in DOC if "data_type" in chain(c) and "subject_statement" not in chain(c)}
for c in PERSIST:
    ch = chain(c)
    dirs = [d for d in DIRS if d in supers(c)]
    dts = [s for s in supers(c) if s in DT or s == "data_type"]
    if dirs and "subject_statement" in ch:
        if len(dts) != 1:
            find("leaf_parent_shape", c, f"direction {dirs} but data-type parents {dts}")
        else:
            want = f"{dts[0]}_{DIRS[dirs[0]]}"
            if c != want:
                find("leaf_name_T11", c, f"parents {supers(c)} -> grammar name `{want}`")
    for suf, d in [("_observation", "subject_observation"), ("_manipulation", "subject_manipulation"),
                   ("_assertion", "subject_assertion"), ("_calculation", "subject_calculation")]:
        if c.endswith(suf) and d not in ch and c != d:
            find("suffix_without_direction", c, f"named *{suf} but `{d}` not in chain {ch}")

# 6. abstract flags among persist
for c in PERSIST:
    dc = DOC[c].get("document_class", {})
    if DOC[c].get("abstract") or dc.get("abstract"):
        find("abstract_persist", c, f"abstract; in data_type={c in DT}")

# 7. tier: draft persist
for c in PERSIST:
    if BY[c]["tier"] != "stable":
        find("tier_draft", c, BY[c]["tier"])

# 8. data_type composites with no leaf and no use
users = collections.Counter()
for c in DOC:
    for s in supers(c):
        users[s] += 1
    for d in DOC[c].get("depends_on", []):
        for t in (d.get("must_refer_to_document_class") or "").split(","):
            users[t.strip()] += 1
for c in PERSIST:
    if c in DT and users[c] == 0:
        find("composite_unused", c, "no subclass and no edge targets it")

# 9. variable/method bindings (T8)
for c in PERSIST:
    for path, f in walk_fields(DOC[c].get("fields")):
        if path.split(".")[-1] in ("variable", "method", "purpose", "clock", "relation", "unit", "axis", "origin") \
                and f.get("type") == "ontology_term" and not (f.get("constraints") or {}).get("binding"):
            find("ontology_term_unbound_T8", c, f"`{path}`")

# 10. ontology_term vs char for vocabulary-ish names
for c in PERSIST:
    for path, f in walk_fields(DOC[c].get("fields")):
        leaf = path.split(".")[-1]
        if leaf in ("variable", "method", "unit", "modality", "species", "relation") and f.get("type") == "char":
            find("vocab_as_char_T8", c, f"`{path}` is char")

total = 0
for k in sorted(F):
    print(f"\n== {k}: {len(F[k])}")
    for cls, msg in F[k]:
        print(f"   {cls}: {msg}")
    total += len(F[k])
print(f"\nTOTAL findings: {total} across {len(F)} check(s) that fired; "
      f"checks with zero hits are not listed")
