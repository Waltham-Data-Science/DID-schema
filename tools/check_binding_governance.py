#!/usr/bin/env python3
"""#32 -- BINDING GOVERNANCE (T8): the instrument that makes every binding fact
countable, and every binding fact that is stored twice checkable.

WHY THIS EXISTS
---------------
T8 says controlled vocabularies are HARD-VALIDATED, not advisory: a `value_set`
declares an admissible set, a binding registry maps `variable` (and
`method` + `variable`) to a value_set or a leaf, and an ontology-aware validator
resolves values against it. What the repository actually holds is three
DIFFERENT binding shapes, declared in two places, checked by almost nothing:

  SHAPE 1  keyed_by       `term.value` -> "resolve against the registry row for
                          this document's `variable`"           (1 field)
  SHAPE 2  inline enum    `root` + `values`, an admissible set copied ONTO the
                          field                                 (7 fields)
  SHAPE 3  term_set       `vocabulary` + `term_set`, naming an openMINDS
                          instance library catalogued in the registry
                                                                (3 fields)
  SHAPE 4  node_form      the three pivot fields (subject_statement.variable,
                          subject_interaction.method,
                          interaction_purpose.purpose): a LEXICAL rule on the
                          value's `node` -- must be a well-formed CURIE -- and
                          no admissible set                      (3 fields)
  SHAPE 5  strength-only  a strength and nothing else. ZERO fields today: this
                          is what the three pivot fields were between #32
                          increment 1 and increment 2.           (0 fields)

Nothing enforced any of it until #32 increment 2. `+did2/+schema/cache.m
validateConstraints` handled maxLength / minLength / minimum / maximum / enum
and dropped everything else into `otherwise` (tolerated); it now carries a
`binding` case raising three distinct ids -- bindingValueMissing /
bindingNodeMalformed / bindingValueNotInSet -- behind
`did2.schema.cache.strictMode('BindingConformance')`, which is DISARMED by
default. So on today's tree `binding` is STILL declarative in effect, and
deliberately: the declarations are cheap to get right while an inconsistency
costs nothing, and expensive once the switch is armed.

NOTHING MATLAB-SIDE WAS EXECUTED when that case was written (no MATLAB in the
environment), so treat the paragraph above as the declared design of the other
repository, not as a measurement of it. What IS executed here is the grammar
lock: the CURIE literal below is character-identical to cache.m's, asserted by
tests/test_binding_governance.py.

The specific failure this tool was built to catch had ALREADY HAPPENED and was
invisible: `root: did_clocktype` names ONE value_set and is defined inline in
FOUR places with TWO different member lists (4 terms on the new time-model
fields, 9 on the two legacy `epoch_*` carriers). A named set with no single
definition is the strain/epoch "drift test" from CLAUDE.md, one layer up --
the same vocabulary resolves differently depending on which class you read.

WHAT IT CHECKS  (each finding is a COUNT with a denominator and a ratchet)
-------------------------------------------------------------------------
  B1  binding keys used by live declarations that the META-SCHEMA does not
      declare -- and meta-schema keys no declaration uses.
  B2  whether the meta-schema's `binding` object accepts arbitrary keys.
  B3  a named value_set (`root`) whose inline definitions DISAGREE.
  B4  `values` element shape vs the bound field's declared `type`.
  B5  strength stated BOTH on the field and in the registry -- and whether the
      two copies agree. (The team's call, 2026-08-10: the FIELD is
      authoritative and the registry must agree where it also states one.)
      Scans ALL FOUR registry lists, not just entity_field_bindings, and
      reports the field side too: see strength_agreement().
  B6  bound fields with no catalogue row in the registry at all.
  B7  the D9 LEAF-SELECTION GAP -- the concrete cost of leaving #32 open. The
      signed `subjectmeasurement` fold says the typed leaf "must be chosen
      through the D9 registry"; every normative `subject_statement_bindings`
      row binds to `term_assertion`, and the only dimensional row in the file
      sits under `binding_examples`, which the registry's own notes call
      illustrative. So the lookup resolves nothing for `age`, and DID-matlab
      shipped `jQuantityLeaf` as a documented keyword-table stand-in.
  B8  CURIE prefixes used by admissible sets that CURIE_lookups_meta.json does
      not register. This is the `time:` repair recurring: a CURIE whose prefix
      expands to nothing is a binding that LOOKS governed and is not.
  B9  bindings that are structurally UNENFORCEABLE as declared -- what an
      ontology-aware validator would have nothing to resolve against.

WHAT IT DELIBERATELY DOES NOT DO
--------------------------------
IT DECIDES NOTHING. Which vocabulary a field binds to, whether the field or the
registry is authoritative, and whether `binding` should be enforced are TEAM
calls (operating rule 4). This tool reports; every finding is phrased as a
count and an option list, never as an instruction. B3's two `did_clocktype`
definitions in particular have a KNOWN, recorded cause -- the eight legacy
time_reference classes stay until their migrators move -- so the finding is
that the transitional state is unrecorded and unbounded, not that it is wrong.

It also does NOT read the corpus. It cannot: no corpus report is checked into
either repository. Every count here is over SCHEMA DECLARATIONS. How many real
documents a required binding would quarantine is UNMEASURED, and the numbers
below must not be quoted as if they were document counts.

Usage:  python3 tools/check_binding_governance.py
        python3 tools/check_binding_governance.py --enforce   # exit 1 if grown
        python3 tools/check_binding_governance.py --json
"""

import argparse
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
VETA = os.path.join(REPO, "schemas", "V_eta")
TIERS = ("stable", "draft", "deprecated")

REGISTRY_FILE = "binding_registry_meta.json"
META_FILE = "did_schema_meta.json"
CURIE_FILE = "CURIE_lookups_meta.json"

# The registry's list-valued blocks, and whether they are NORMATIVE. The
# registry's own `notes` say `binding_examples` "holds illustrative rows only
# and is not swept data" -- so a lookup that resolves only against
# binding_examples resolves nothing. B7 turns on exactly that distinction.
REGISTRY_LISTS = {
    "subject_statement_bindings": True,
    "relation_bindings": True,
    "entity_field_bindings": True,
    "binding_examples": False,
}

# A CURIE-looking token: a prefix, a colon, then a local part. Deliberately
# loose on the local part (OBO uses digits, OWL-Time uses camelCase names).
#
# THIS LITERAL IS SHARED ACROSS TWO REPOSITORIES AND TWO LANGUAGES. DID-matlab
# `+did2/+schema/cache.m` isCurieToken carries the same string character for
# character, because `node_form: curie` is decided here and enforced there --
# and two implementations of one grammar drifting apart is exactly the
# `did_clocktype` failure B3 exists to catch, one repo further out.
# tests/test_binding_governance.py::test_the_curie_grammar_is_identical_in_cache_m
# is the lock. No capture groups: nothing reads them (the prefix is taken with
# `split(":", 1)`), and their absence is what lets the two literals be equal.
CURIE_PATTERN = r"^[A-Za-z][A-Za-z0-9_.\-]*:[A-Za-z0-9_][A-Za-z0-9_.\-]*$"
CURIE = re.compile(CURIE_PATTERN)

# ---------------------------------------------------------------------------
# BASELINES. Each count may FALL freely; any INCREASE fails under --enforce.
# Set 2026-08-10, when the sweep was written, from the tree as it stood. Every
# one of them is DEBT, not an approval: raising a baseline is a deliberate act
# that has to move a number and say why, exactly as check_empty_ontology_nodes
# and check_duplicate_field_declarations do.
# ---------------------------------------------------------------------------

# B1: `root` (7 uses) and `source` (8 uses) are used by live bindings and are
# not properties of the meta-schema's `binding` object. tests/test_veta.py
# ::test_binding_is_formalized_in_meta_schema ASSERTS their absence from the
# meta-schema, while build_v_eta.py emits them on 8 fields -- the two halves of
# the repository disagree about what a binding is, and additionalProperties
# (B2) is what lets both stand.
BASELINE_UNDECLARED_KEY_USES = 15

# B3: `did_clocktype`, defined 4 places with 2 distinct member lists.
BASELINE_VALUE_SET_DISAGREEMENTS = 1

# B4: three ontology_term-typed fields carry BARE STRINGS in `values`
# (frequency_filter.algorithm, frequency_filter.band,
# relative_reference.value.relation) where the two clock bindings carry
# `{node, name}` NodeRefs. build_v_eta.py states the rule in its own comment
# -- "values are NodeRefs, not bare strings, because the field is now
# ontology_term" -- and three declarations do not follow it.
BASELINE_VALUE_SHAPE_MISMATCHES = 3

# B5: strength disagreements between field and registry. MUST STAY 0 -- the
# team's 2026-08-10 call makes the field authoritative and the registry
# required to agree. tests/test_veta.py::test_field_and_registry_strengths_agree
# is the hard gate; this is the reported twin.
BASELINE_STRENGTH_DISAGREEMENTS = 0

# B6: bound fields with no registry catalogue row (11 of 14 today: only the
# three `dataset` openMINDS fields are catalogued).
BASELINE_UNCATALOGUED_BOUND_FIELDS = 11

# B8: distinct CURIE prefixes used by admissible sets that CURIE_lookups_meta
# does not register, matched CASE-INSENSITIVELY (the generous reading).
# NCBITaxon, CL, CHEBI (registry root_nodes) + BFO, RO (relation nodes).
BASELINE_UNREGISTERED_PREFIXES = 5

# B9: bindings an ontology-aware validator would have nothing to resolve
# against, as declared. LOWERED 7 -> 4 by #32 increment 2, and the drop is the
# whole point of that increment rather than a re-scoping of the count: the three
# pivot fields moved from strength-only (a declaration with nothing behind it)
# to `node_form: curie`, which a validator CAN check with no ontology loaded.
# The remaining four are the 3 openMINDS `dataset` fields (the vocabulary's
# pinned `version` is null, so there is no instance library to resolve against)
# and `term.value` (whose keyed_by lookup reaches a registry holding 5 rows, all
# term_assertion).
#
# READ THE NUMBER NARROWLY. "Enforceable" here means a validator has SOMETHING
# to check, not that the check is the one T8 wants. `node_form` proves a value
# is shaped like a term reference; it says nothing about whether the term
# EXISTS. Membership for `variable` needs NDIC.txt, which moved to
# VH-Lab/ndi-ontology-matlab (commit 2c19bf24c) -- a repository this session
# could not attach -- so the membership half of #32 is untouched and these three
# would still resolve nothing against a value set.
BASELINE_UNENFORCEABLE = 4


def load(path):
    with open(path) as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# collection
# ---------------------------------------------------------------------------

def doc_files(veta=VETA):
    """The three maturity tiers, and a COUNT of what was deliberately skipped.

    `examples/` also holds document_class files. They are instance samples, not
    class declarations, and test_veta.py's own sweep excludes them the same way
    -- but "how many did you not look at" is part of a denominator, so it is
    returned rather than left silent.
    """
    out = []
    for tier in TIERS:
        for p in sorted(glob.glob(os.path.join(veta, tier, "*.json"))):
            d = load(p)
            if isinstance(d, dict) and "document_class" in d:
                out.append((tier, p, d))
    skipped = 0
    for p in glob.glob(os.path.join(veta, "**", "*.json"), recursive=True):
        rel = os.path.relpath(p, veta).split(os.sep)[0]
        if rel in TIERS:
            continue
        try:
            d = load(p)
        except (OSError, ValueError):
            continue
        if isinstance(d, dict) and "document_class" in d:
            skipped += 1
    return out, skipped


def bound_fields(files):
    """Every field declaration in the built set that carries constraints.binding.

    Returns (rows, n_files, n_fields) so the denominator is a measurement and
    not an assumption -- a walker that stopped descending would otherwise
    report "no bindings" and read as clean.
    """
    rows = []
    n_fields = 0

    def walk(flds, prefix, cls, tier):
        nonlocal n_fields
        for f in flds or []:
            name = f.get("name", "?")
            here = prefix + name
            n_fields += 1
            b = (f.get("constraints") or {}).get("binding")
            if isinstance(b, dict):
                rows.append({
                    "class": cls,
                    "field": here,
                    "tier": tier,
                    "type": f.get("type"),
                    "binding": b,
                })
            walk(f.get("fields"), here + ".", cls, tier)

    for tier, _p, d in files:
        walk(d.get("fields"), "", d["document_class"]["class_name"], tier)
    return rows, len(files), n_fields


def shape_of(b):
    if "keyed_by" in b:
        return "keyed_by"
    if "term_set" in b or "vocabulary" in b:
        return "term_set"
    if "values" in b or "root" in b or "root_node" in b or "ontology" in b:
        return "inline_set"
    # SHAPE 5, added by #32 increment 2. `node_form` names no admissible SET,
    # so it is not an inline_set -- but unlike a bare strength it does state a
    # checkable property of the value, which is why B9 stops counting it as
    # unenforceable. Ordered LAST among the positives so that a binding which
    # carries both an admissible set and a node_form still reports as the
    # stronger shape.
    if "node_form" in b:
        return "node_form"
    return "strength_only"


def member_names(values):
    """Normalise an admissible-set member list to comparable names.

    A member is either a NodeRef `{node, name}` or a bare string. Comparing on
    the name is what makes the did_clocktype disagreement visible at all: the
    two definitions differ in MEMBERSHIP, not merely in wire shape.
    """
    out = []
    for v in values or []:
        out.append(v.get("name", "") if isinstance(v, dict) else str(v))
    return tuple(sorted(out))


def curie_tokens(obj):
    """Every CURIE-looking string anywhere inside a JSON value."""
    found = []
    if isinstance(obj, str):
        if CURIE.match(obj):
            found.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            found += curie_tokens(v)
    elif isinstance(obj, list):
        for v in obj:
            found += curie_tokens(v)
    return found


def strength_agreement(rows, reg):
    """B5 -- the field/registry strength axis, in BOTH directions.

    The team's call (2026-08-10) is that STRENGTH IS AUTHORITATIVE ON THE FIELD
    and the registry must agree wherever it also states one. Until #32
    increment 2 this compared `entity_field_bindings` ONLY, so it checked three
    rows out of thirty-eight and reported "pairs_checked: 3" -- true, and easy
    to read as "the registry has been checked". The other two normative lists
    were not so much clean as UNVISITED: a `strength` added to a
    `subject_statement_bindings` or `relation_bindings` row would have been an
    unchecked second copy of an authoritative fact, which is the whole defect
    this finding exists to prevent.

    Now every list is scanned, and a row is handled by WHAT IT CAN BE COMPARED
    AGAINST rather than by which list it sits in:

      names class+field   -> resolve to the bound field and compare. Today only
                             `entity_field_bindings` rows do; nothing stops
                             another list from doing so, and if one ever does it
                             is checked from the first commit rather than the
                             first incident.
      states a strength,
      names no field      -> UNRESOLVABLE, and counted. A strength is an
                             authority statement about a field; stated where no
                             field can be identified, nothing can agree with it
                             and nothing can contradict it. Zero such rows today
                             -- the ratchet is what keeps it zero.
      neither             -> skipped, and counted in the denominator.

    The FIELD side is reported too, because "checked 3 of 38 rows" and "checked
    3 of 14 fields" are different denominators and only one of them was ever
    printed. A field whose binding states a strength that no registry row of ANY
    list resolves to is stored in exactly one place -- fine under the team's
    call, and worth seeing, because it is the population that would silently
    grow a second copy. That list is the same 11 fields B6 reports today, by
    coincidence of the registry: B6 asks only about `entity_field_bindings`,
    this asks about every list, so the two diverge the moment another list names
    a field.

    Returns the finding dict. Pulled out of run() as a pure function of (rows,
    registry) so a test can hand it a registry shape that does not exist in the
    tree yet -- a test that can only read the live files cannot check a rule
    about rows nobody has written.
    """
    field_index = {(row["class"], row["field"]): row for row in rows}
    scanned = 0
    named_a_field = 0
    stated_a_strength = 0
    pairs, disagreements = [], []
    registry_named_fields = set()

    for list_name in REGISTRY_LISTS:
        for entry in reg.get(list_name, []):
            scanned += 1
            reg_strength = entry.get("strength")
            has_strength = reg_strength is not None
            stated_a_strength += 1 if has_strength else 0
            key = (entry.get("class"), entry.get("field"))
            names_field = key[0] is not None and key[1] is not None
            if not names_field:
                if has_strength:
                    disagreements.append({
                        "list": list_name, "class": key[0], "field": key[1],
                        "field_strength": None, "registry_strength": reg_strength,
                        "why": "registry row states a strength but names no "
                               "field, so no field declaration can agree with it"})
                continue
            named_a_field += 1
            registry_named_fields.add(key)
            row = field_index.get(key)
            if row is None:
                disagreements.append({
                    "list": list_name, "class": key[0], "field": key[1],
                    "field_strength": None, "registry_strength": reg_strength,
                    "why": "registry names a field that declares no binding"})
                continue
            fld_strength = row["binding"].get("strength")
            pairs.append({"list": list_name, "class": key[0], "field": key[1],
                          "field_strength": fld_strength,
                          "registry_strength": reg_strength})
            if has_strength and fld_strength != reg_strength:
                disagreements.append({
                    "list": list_name, "class": key[0], "field": key[1],
                    "field_strength": fld_strength,
                    "registry_strength": reg_strength,
                    "why": "the two stored copies differ"})

    with_strength = [row for row in rows if row["binding"].get("strength")]
    only_on_field = [{"class": row["class"], "field": row["field"],
                      "strength": row["binding"].get("strength")}
                     for row in with_strength
                     if (row["class"], row["field"]) not in registry_named_fields]

    return {
        "count": len(disagreements),
        "registry_lists_scanned": len(REGISTRY_LISTS),
        "registry_rows_scanned": scanned,
        "registry_rows_naming_a_field": named_a_field,
        "registry_rows_stating_a_strength": stated_a_strength,
        "pairs_checked": len(pairs),
        "pairs": pairs,
        "detail": disagreements,
        "bound_fields_scanned": len(rows),
        "bound_fields_stating_a_strength": len(with_strength),
        "bound_fields_with_no_registry_row": sorted(
            only_on_field, key=lambda x: (x["class"], x["field"])),
        "registry_rows_with_no_strength": sum(
            1 for k, norm in REGISTRY_LISTS.items() if norm
            for e in reg.get(k, []) if "strength" not in e),
    }


# ---------------------------------------------------------------------------
# the sweep
# ---------------------------------------------------------------------------

def run(veta=VETA):
    files, skipped = doc_files(veta)
    rows, n_files, n_fields = bound_fields(files)
    meta = load(os.path.join(veta, "stable", META_FILE))
    reg = load(os.path.join(veta, "stable", REGISTRY_FILE))
    curie = load(os.path.join(veta, "stable", CURIE_FILE))

    binding_meta = (meta["$defs"]["field_definition"]["properties"]["constraints"]
                    .get("properties", {}).get("binding", {}))
    declared_keys = set(binding_meta.get("properties", {}))

    r = {
        "denominator": {
            "schema_files": n_files,
            "document_class_files_outside_the_tiers_skipped": skipped,
            "field_declarations": n_fields,
            "bound_fields": len(rows),
            "registry_lists": {k: len(reg.get(k, [])) for k in REGISTRY_LISTS},
            "registry_rows_normative": sum(
                len(reg.get(k, [])) for k, norm in REGISTRY_LISTS.items() if norm),
            "registry_rows_illustrative": sum(
                len(reg.get(k, [])) for k, norm in REGISTRY_LISTS.items() if not norm),
            "curie_prefixes_registered": len(curie.get("prefixes", {})),
        },
        "inventory": [],
        "findings": {},
    }

    for row in sorted(rows, key=lambda x: (x["class"], x["field"])):
        b = row["binding"]
        r["inventory"].append({
            "class": row["class"], "field": row["field"], "tier": row["tier"],
            "type": row["type"], "shape": shape_of(b),
            "strength": b.get("strength"),
            "set": b.get("root") or b.get("term_set") or b.get("root_node") or "",
            "n_values": len(b.get("values") or []),
        })

    # -- the derived value_set catalogue ------------------------------------
    # NOT a decision and NOT a new source of truth: it is READ BACK from the
    # inline declarations, because there is nowhere else a named admissible set
    # is written down. `entity_field_bindings` catalogues the openMINDS term
    # sets centrally; a `root:`-named value_set is catalogued nowhere, so the
    # only way to see that `did_clocktype` means two different things is to
    # derive the catalogue and look. #45 (data_body) adds three more named sets
    # -- datum_type, byte_order, datum_order -- so the copy-paste this reveals
    # is about to happen three more times.
    catalogue = {}
    for row in rows:
        b = row["binding"]
        key = b.get("root") or b.get("root_node") or b.get("term_set")
        if not key:
            continue
        entry = catalogue.setdefault(key, {"carriers": [], "definitions": []})
        entry["carriers"].append(row["class"] + "." + row["field"])
        if "values" in b:
            members = list(member_names(b["values"]))
            if members not in entry["definitions"]:
                entry["definitions"].append(members)
    r["value_set_catalogue"] = {
        k: {"carriers": sorted(v["carriers"]),
            "n_definitions": len(v["definitions"]),
            "definitions": v["definitions"]}
        for k, v in sorted(catalogue.items())
    }

    # -- B1 -----------------------------------------------------------------
    used = {}
    for row in rows:
        for k in row["binding"]:
            used.setdefault(k, []).append(row["class"] + "." + row["field"])
    undeclared = {k: v for k, v in used.items() if k not in declared_keys}
    r["findings"]["B1_undeclared_binding_keys"] = {
        "count": sum(len(v) for v in undeclared.values()),
        "distinct_keys": sorted(undeclared),
        "sites": {k: sorted(v) for k, v in sorted(undeclared.items())},
        "declared_but_unused": sorted(declared_keys - set(used)),
        "meta_schema_declares": sorted(declared_keys),
    }

    # -- B2 -----------------------------------------------------------------
    addl = binding_meta.get("additionalProperties", None)
    r["findings"]["B2_binding_accepts_arbitrary_keys"] = {
        "count": 1 if addl is not False else 0,
        "additionalProperties": addl if addl is not None else "(absent -> true)",
    }

    # -- B3 -----------------------------------------------------------------
    by_set = {}
    for row in rows:
        b = row["binding"]
        key = b.get("root") or b.get("root_node")
        if key and "values" in b:
            by_set.setdefault(key, []).append(
                (row["class"] + "." + row["field"], member_names(b["values"])))
    disagree = {k: v for k, v in by_set.items() if len({m for _n, m in v}) > 1}
    r["findings"]["B3_value_set_definitions_disagree"] = {
        "count": len(disagree),
        "sets_inspected": len(by_set),
        "detail": {k: [{"carrier": n, "n": len(m), "members": list(m)} for n, m in v]
                   for k, v in sorted(disagree.items())},
    }

    # -- B4 -----------------------------------------------------------------
    mismatches = []
    for row in rows:
        vals = row["binding"].get("values")
        if not vals:
            continue
        kinds = {"noderef" if isinstance(v, dict) else "string" for v in vals}
        if len(kinds) > 1:
            mismatches.append({"class": row["class"], "field": row["field"],
                               "type": row["type"], "why": "mixed member shapes",
                               "kinds": sorted(kinds)})
        elif row["type"] == "ontology_term" and kinds == {"string"}:
            mismatches.append({"class": row["class"], "field": row["field"],
                               "type": row["type"],
                               "why": "ontology_term field, bare-string members",
                               "kinds": ["string"]})
        elif row["type"] != "ontology_term" and kinds == {"noderef"}:
            mismatches.append({"class": row["class"], "field": row["field"],
                               "type": row["type"],
                               "why": "non-term field, NodeRef members",
                               "kinds": ["noderef"]})
    r["findings"]["B4_value_shape_vs_field_type"] = {
        "count": len(mismatches),
        "sets_with_values": sum(1 for row in rows if row["binding"].get("values")),
        "detail": mismatches,
    }

    # -- B5 -----------------------------------------------------------------
    r["findings"]["B5_strength_stored_twice"] = strength_agreement(rows, reg)

    # -- B6 -----------------------------------------------------------------
    catalogued = {(e.get("class"), e.get("field"))
                  for e in reg.get("entity_field_bindings", [])}
    uncat = [{"class": row["class"], "field": row["field"],
              "shape": shape_of(row["binding"]),
              "strength": row["binding"].get("strength")}
             for row in rows if (row["class"], row["field"]) not in catalogued]
    r["findings"]["B6_bound_fields_not_in_registry"] = {
        "count": len(uncat),
        "of_bound_fields": len(rows),
        "detail": sorted(uncat, key=lambda x: (x["class"], x["field"])),
    }

    # -- B7 -----------------------------------------------------------------
    ssb = reg.get("subject_statement_bindings", [])
    ex = reg.get("binding_examples", [])
    by_class_norm = {}
    for e in ssb:
        by_class_norm.setdefault(e.get("class"), 0)
        by_class_norm[e.get("class")] += 1
    dim_norm = [e for e in ssb if e.get("class") != "term_assertion"]
    dim_ex = [e for e in ex if e.get("class") != "term_assertion"]
    r["findings"]["B7_d9_leaf_selection_gap"] = {
        # the count IS the gap: how many dimensional leaves a strict registry
        # lookup can resolve. 0 means the signed subjectmeasurement fold cannot
        # be implemented as signed.
        "count": 1 if not dim_norm else 0,
        "normative_rows": len(ssb),
        "normative_rows_by_target_class": by_class_norm,
        "normative_dimensional_rows": len(dim_norm),
        "illustrative_rows": len(ex),
        "illustrative_dimensional_rows": [
            {"variable": e.get("variable", {}).get("name"), "class": e.get("class")}
            for e in dim_ex],
    }

    # -- B8 -----------------------------------------------------------------
    prefixes = set(curie.get("prefixes", {}))
    lower = {p.lower() for p in prefixes}
    seen = {}
    scopes = [("field bindings", [row["binding"] for row in rows])]
    for k, norm in REGISTRY_LISTS.items():
        scopes.append((("registry." + k) + ("" if norm else " (illustrative)"),
                       reg.get(k, [])))
    for scope, blob in scopes:
        for tok in curie_tokens(blob):
            pfx = tok.split(":", 1)[0]
            seen.setdefault(pfx, {"tokens": set(), "scopes": set()})
            seen[pfx]["tokens"].add(tok)
            seen[pfx]["scopes"].add(scope)
    unreg_ci = sorted(p for p in seen if p.lower() not in lower)
    unreg_cs = sorted(p for p in seen if p not in prefixes)
    r["findings"]["B8_unregistered_curie_prefixes"] = {
        "count": len(unreg_ci),
        "prefixes_seen": sorted(seen),
        "registered": sorted(prefixes),
        "unregistered_case_insensitive": unreg_ci,
        "unregistered_case_sensitive": unreg_cs,
        "detail": {p: {"tokens": sorted(seen[p]["tokens"]),
                       "scopes": sorted(seen[p]["scopes"])}
                   for p in unreg_cs},
    }

    # -- B9 -----------------------------------------------------------------
    unenforceable = []
    vocabs = reg.get("controlled_vocabularies", {})
    for row in rows:
        b, shape = row["binding"], shape_of(row["binding"])
        who = {"class": row["class"], "field": row["field"],
               "strength": b.get("strength"), "shape": shape}
        if shape == "strength_only":
            unenforceable.append(dict(who, why=(
                "no admissible set named (option C, team 2026-08-10) -- a "
                "validator has nothing to resolve against")))
        elif shape == "keyed_by":
            unenforceable.append(dict(who, why=(
                "resolves through subject_statement_bindings, which holds "
                f"{len(ssb)} rows, all binding to term_assertion -- any other "
                "`variable` resolves to nothing")))
        elif shape == "term_set":
            v = vocabs.get(b.get("vocabulary"), {})
            if v.get("version") in (None, ""):
                unenforceable.append(dict(who, why=(
                    f"controlled_vocabularies[{b.get('vocabulary')!r}].version "
                    "is null -- no pinned instance library to resolve against")))
    r["findings"]["B9_unenforceable_as_declared"] = {
        "count": len(unenforceable),
        "of_bound_fields": len(rows),
        "detail": unenforceable,
    }

    return r


# ---------------------------------------------------------------------------
# reporting
# ---------------------------------------------------------------------------

BASELINES = {
    "B1_undeclared_binding_keys": BASELINE_UNDECLARED_KEY_USES,
    "B3_value_set_definitions_disagree": BASELINE_VALUE_SET_DISAGREEMENTS,
    "B4_value_shape_vs_field_type": BASELINE_VALUE_SHAPE_MISMATCHES,
    "B5_strength_stored_twice": BASELINE_STRENGTH_DISAGREEMENTS,
    "B6_bound_fields_not_in_registry": BASELINE_UNCATALOGUED_BOUND_FIELDS,
    "B8_unregistered_curie_prefixes": BASELINE_UNREGISTERED_PREFIXES,
    "B9_unenforceable_as_declared": BASELINE_UNENFORCEABLE,
}

TITLES = {
    "B1_undeclared_binding_keys":
        "binding keys used by declarations but NOT declared by the meta-schema",
    "B2_binding_accepts_arbitrary_keys":
        "the meta-schema's `binding` object accepts arbitrary keys",
    "B3_value_set_definitions_disagree":
        "named value_sets whose inline definitions DISAGREE",
    "B4_value_shape_vs_field_type":
        "`values` member shape disagrees with the bound field's type",
    "B5_strength_stored_twice":
        "strength stored on BOTH field and registry, and disagreeing",
    "B6_bound_fields_not_in_registry":
        "bound fields with no catalogue row in the registry",
    "B7_d9_leaf_selection_gap":
        "the D9 registry cannot select a dimensional leaf (jQuantityLeaf)",
    "B8_unregistered_curie_prefixes":
        "CURIE prefixes in admissible sets that CURIE_lookups_meta does not register",
    "B9_unenforceable_as_declared":
        "bindings a validator would have nothing to resolve against",
}


def report(r):
    d = r["denominator"]
    print("BINDING GOVERNANCE (#32 / T8) -- schema-side sweep")
    print("  DENOMINATOR")
    print("    V_eta document_class files walked  : %d  (tiers %s)"
          % (d["schema_files"], "/".join(TIERS)))
    print("    document_class files NOT walked    : %d  (examples/, instance "
          "samples)" % d["document_class_files_outside_the_tiers_skipped"])
    print("    field declarations inspected       : %d  (nested sub-fields included)"
          % d["field_declarations"])
    print("    fields carrying constraints.binding: %d" % d["bound_fields"])
    print("    registry rows, NORMATIVE            : %d  %s"
          % (d["registry_rows_normative"],
             {k: v for k, v in d["registry_lists"].items() if REGISTRY_LISTS[k]}))
    print("    registry rows, ILLUSTRATIVE         : %d  %s"
          % (d["registry_rows_illustrative"],
             {k: v for k, v in d["registry_lists"].items() if not REGISTRY_LISTS[k]}))
    print("    CURIE prefixes registered           : %d" % d["curie_prefixes_registered"])
    print("    corpus documents inspected          : 0 -- NO corpus report is checked")
    print("                                          into either repo. Every count")
    print("                                          below is over DECLARATIONS.")
    print()

    print("INVENTORY -- every bound field")
    print("    %-32s %-22s %-14s %-13s %-10s %s"
          % ("class", "field", "type", "shape", "strength", "set (n)"))
    for i in r["inventory"]:
        print("    %-32s %-22s %-14s %-13s %-10s %s"
              % (i["class"], i["field"], i["type"], i["shape"],
                 i["strength"], "%s (%d)" % (i["set"] or "-", i["n_values"])))
    print()

    print("VALUE SET CATALOGUE (DERIVED -- no such catalogue is stored)")
    print("    A `root:`-named admissible set is written down NOWHERE central;")
    print("    it is copied onto each carrier. n_defs > 1 means the same name")
    print("    resolves two ways depending on which class you read.")
    for name, v in r["value_set_catalogue"].items():
        flag = "   <-- DRIFT" if v["n_definitions"] > 1 else ""
        print("    %-24s %d carrier(s), %d inline definition(s)%s"
              % (name, len(v["carriers"]), v["n_definitions"], flag))
        for c in v["carriers"]:
            print("        %s" % c)
        for i, dfn in enumerate(v["definitions"], 1):
            print("        def %d (%d members): %s" % (i, len(dfn), ", ".join(dfn)))
    print()

    for key, f in r["findings"].items():
        base = BASELINES.get(key)
        tag = "" if base is None else "  (baseline %d)" % base
        flag = ""
        if base is not None and f["count"] > base:
            flag = "   <-- GREW"
        print("%s  %s" % (key, TITLES[key]))
        print("    count: %d%s%s" % (f["count"], tag, flag))
        for k, v in f.items():
            if k == "count":
                continue
            if isinstance(v, (list, dict)) and not v:
                continue
            print("      %-36s %s" % (k + ":", json.dumps(v)))
        print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--veta", default=VETA)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--enforce", action="store_true",
                    help="exit 1 if any ratcheted count has GROWN")
    a = ap.parse_args()

    r = run(a.veta)
    if a.json:
        print(json.dumps(r, indent=2, sort_keys=True))
    else:
        report(r)

    if r["denominator"]["bound_fields"] == 0:
        print("ERROR: zero bound fields found -- the sweep read nothing, which is "
              "NOT the same as a clean result. Check --veta.", file=sys.stderr)
        return 2

    if a.enforce:
        grown = [(k, r["findings"][k]["count"], b)
                 for k, b in BASELINES.items() if r["findings"][k]["count"] > b]
        if grown:
            print("\nFAIL -- a binding-governance count GREW:", file=sys.stderr)
            for k, got, base in grown:
                print("  %-42s %d > baseline %d" % (k, got, base), file=sys.stderr)
            print("\nEither fix the declaration, or raise the baseline in "
                  "tools/check_binding_governance.py DELIBERATELY and say why.",
                  file=sys.stderr)
            return 1
        print("OK -- no binding-governance count grew.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
