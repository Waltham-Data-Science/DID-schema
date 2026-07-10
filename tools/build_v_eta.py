#!/usr/bin/env python3
"""Deterministic V_zeta -> V_eta (Brainstorm J) transform.

Runs IN PLACE on schemas/V_eta (a fresh copy of schemas/V_zeta). Re-runnable:
it reads the pristine V_zeta tree for anything it needs and rewrites V_eta.

Implements V_eta_SPEC sections 1-8: the subject-side core (bare subject,
subject_relation, restored subject_statement, subject_assertion genus,
subject_interaction re-root + subject_observation/subject_manipulation, Path S,
timing relocation), the strict-J leaf tier (data-type-named manipulations +
dose/formulation/chemical composites + term_manipulation; no delivery-method
family, no escape hatch), storage_mode + data_body/sampled_body/opaque_body, and
the hard-validated binding registry (formalized `binding` block + value_set +
binding_registry_meta with the kind-variable set).

Still carried unchanged (a tracked follow-up, so the set validates): the V_zeta
dataseries_/timeseries_/imageseries_ observation + *_data body classes and
element_epoch/generic_file/expression_matrix_data are NOT yet collapsed onto the
data-type leaves + sampled_body (that consolidation is entangled with NDI-side
infrastructure and lands with the NDI-matlab work). The did_v1 -> V_eta
conversion docs are still V_zeta-targeted pending retarget.

Usage:  python3 tools/build_v_eta.py
"""
import glob
import json
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VZETA = os.path.join(ROOT, "schemas", "V_zeta")
VETA = os.path.join(ROOT, "schemas", "V_eta")
TIERS = ["stable", "draft", "deprecated"]
META_FILES = {"did_schema_meta.json", "CURIE_lookups_meta.json", "ndi_reserved_keys.json",
              "binding_registry_meta.json"}

DIMS = ["mass", "length", "volume", "duration", "temperature", "pressure",
        "frequency", "voltage", "current", "concentration", "count", "score"]


# ---------- helpers ----------

def subfield(name, ftype, doc, *, non_empty=False, scalar=True, blank=None,
             constraints=None, sub_fields=None):
    if blank is None:
        blank = {"node": "", "name": ""} if ftype == "ontology_term" else (
            "" if ftype in ("char", "string") else (
                [] if ftype == "matrix" or not scalar else (
                    0 if ftype == "integer" else (
                        {} if ftype == "structure" else 0.0))))
    obj = {"name": name, "type": ftype, "blank_value": blank, "default_value": blank,
           "mustBeNonEmpty": non_empty, "mustBeScalar": scalar, "mustNotHaveNaN": False,
           "queryable": True, "ontology": None, "documentation": doc,
           "constraints": constraints or {}}
    if ftype == "structure":
        obj["fields"] = sub_fields or []
    return obj


def field(name, ftype, doc, *, non_empty=False, scalar=True, queryable=True,
          blank=None, default=None, constraints=None, ontology=None, sub_fields=None):
    if blank is None:
        blank = {"node": "", "name": ""} if ftype == "ontology_term" else (
            [] if not scalar else ("" if ftype in ("char", "string") else (
                False if ftype == "boolean" else ({} if ftype == "structure" else 0.0))))
    if default is None:
        default = blank
    obj = {
        "name": name, "type": ftype, "blank_value": blank, "default_value": default,
        "mustBeNonEmpty": non_empty, "mustBeScalar": scalar, "mustNotHaveNaN": False,
        "queryable": queryable, "ontology": ontology, "documentation": doc,
        "constraints": constraints or {},
    }
    if ftype == "structure":
        obj["fields"] = sub_fields or []
    return obj


def dep(name, cls, doc, *, non_empty=True, multiple=False):
    d = {"name": name, "mustBeNonEmpty": non_empty, "documentation": doc,
         "must_refer_to_document_class": cls}
    if multiple:
        d["multiple"] = True
    return d


def dclass(name, supers, *, abstract=False, version="1.0.0", maturity="stable"):
    dc = {"class_name": name, "class_version": version,
          "superclasses": [{"class_name": s} for s in supers],
          "maturity_level": maturity}
    if abstract:
        dc["abstract"] = True
    return dc


def doc(name, supers, *, abstract=False, version="1.0.0", maturity="stable",
        deps=None, fields=None):
    return {"document_class": dclass(name, supers, abstract=abstract, version=version,
                                     maturity=maturity),
            "depends_on": deps or [], "file": [], "fields": fields or []}


def load(p):
    with open(p) as f:
        return json.load(f)


def write(tier, name, obj):
    with open(os.path.join(VETA, tier, name + ".json"), "w") as f:
        json.dump(obj, f, indent=4)
        f.write("\n")


def path_of(name):
    for tier in TIERS:
        p = os.path.join(VETA, tier, name + ".json")
        if os.path.exists(p):
            return tier, p
    return None, None


# ---------- 0. fresh copy ----------

if os.path.exists(VETA):
    shutil.rmtree(VETA)
shutil.copytree(VZETA, VETA)


# ---------- 1. rename map (old class_name -> new class_name) ----------

RENAME = {
    "observation": "subject_observation",
    "manipulation": "subject_manipulation",
    "categorical_observation": "term_observation",
}
for d in DIMS:
    RENAME[f"scalar_{d}"] = d                       # shape mixin
    RENAME[f"scalar_{d}_observation"] = f"{d}_observation"

# classes deleted outright; when they appear as a superclass, replace per SUPER_SUB
DELETE = {"scalar_observation", "scalar_manipulation", "annotation", "group_assignment"}
SUPER_SUB = {"scalar_observation": "subject_observation",
             "scalar_manipulation": "subject_manipulation"}


def rewrite_superclasses(supers):
    out = []
    for s in supers:
        nm = s["class_name"]
        if nm in DELETE:
            repl = SUPER_SUB.get(nm)
            if repl:
                out.append({"class_name": repl})
            continue
        out.append({"class_name": RENAME.get(nm, nm)})
    # de-dup preserving order
    seen, dedup = set(), []
    for s in out:
        if s["class_name"] not in seen:
            seen.add(s["class_name"])
            dedup.append(s)
    return dedup


# apply deletes
for name in DELETE:
    tier, p = path_of(name)
    if p:
        os.remove(p)

# apply renames + superclass rewrites across every remaining file
for tier in TIERS:
    for p in sorted(glob.glob(os.path.join(VETA, tier, "*.json"))):
        if os.path.basename(p) in META_FILES:
            continue
        d = load(p)
        dc = d["document_class"]
        old = dc["class_name"]
        new = RENAME.get(old, old)
        dc["class_name"] = new
        dc["superclasses"] = rewrite_superclasses(dc["superclasses"])
        # rewrite must_refer_to_document_class tokens
        for dep_ in d.get("depends_on", []):
            toks = [t for t in dep_["must_refer_to_document_class"].split(",") if t]
            dep_["must_refer_to_document_class"] = ",".join(
                RENAME.get(t, t) for t in toks)
        os.remove(p)
        with open(os.path.join(VETA, tier, new + ".json"), "w") as f:
            json.dump(d, f, indent=4)
            f.write("\n")


# ---------- 2. subject -> bare identity (v3.0.0) ----------

sub = load(os.path.join(VETA, "stable", "subject.json"))
sub["document_class"]["class_version"] = "3.0.0"
sub["fields"] = [f for f in sub["fields"]
                 if f["name"] in ("local_identifier", "description")]
write("stable", "subject", sub)


# ---------- 3. subject_statement (restored) + spine re-root ----------

SUBJECT_ID = dep("subject_id", "subject",
                 "The subject this statement is about (the finest entity the "
                 "value directly describes; Brainstorm J objective-annotation rule).")
VARIABLE = field("variable", "ontology_term",
                 "The noun the statement concerns — the quantity/entity "
                 "(temperature, body weight, a drug, species). One name across "
                 "assertions, observations and manipulations, so identity search "
                 "is uniform.", non_empty=True)

write("stable", "subject_statement",
      doc("subject_statement", ["base"], abstract=True, version="1.0.0",
          deps=[SUBJECT_ID], fields=[VARIABLE]))

# subject_interaction: re-root under subject_statement; drop subject_id/variable
# (inherited), target_structure, element_id; add method, sample_time, instrument_id;
# keep required time_reference_#.
TIME_REF_REQ = dep("time_reference_#", "time_reference",
                   "When the interaction happened, as one or more time_reference "
                   "anchor documents. Required on interactions (Brainstorm J: an "
                   "interaction tightens time to required).", multiple=True)
INSTRUMENT = dep("instrument_id", "subject",
                 "Optional: the device that performed the method — an "
                 "instrument modeled as a subject (kind asserted via a "
                 "term_assertion). The agent role; subject_id is the patient. "
                 "Empty for hand measurements (D2).", non_empty=False)
METHOD = field("method", "ontology_term",
               "The verb: what was done (measure, inject, heat, stimulate). "
               "Present only on interactions; optional (the observation verb is "
               "nearly always 'measurement').", non_empty=False)
SAMPLE_TIME = field(
    "sample_time", "structure",
    "The per-sample cadence beside the value (Brainstorm J / D1): a compressed "
    "descriptor. The absolute anchor (t0, clock) comes from time_reference; this "
    "restates only the cadence. For body-backed values the cadence lives in "
    "sampled_body.sample_time instead.",
    non_empty=False, scalar=True, blank={}, default={},
    sub_fields=[
        subfield("kind", "char", "point | grid | enumerated.", non_empty=True,
                 blank="point", constraints={"enum": ["point", "grid", "enumerated"]}),
        subfield("dt", "duration", "grid only: sample spacing.", scalar=True),
        subfield("n", "integer", "grid only: sample count.", scalar=True),
        subfield("offsets", "matrix",
                 "enumerated only: explicit per-sample offsets from the anchor."),
    ])

si = doc("subject_interaction", ["subject_statement"], abstract=True, version="3.0.0",
         deps=[TIME_REF_REQ, INSTRUMENT], fields=[METHOD, SAMPLE_TIME])
write("stable", "subject_interaction", si)


# ---------- 4. subject_assertion genus + leaves ----------

TIME_REF_OPT = dep("time_reference_#", "time_reference",
                   "Optional anchor(s): an assertion is timeless, but a claim may "
                   "carry a date it was established.", non_empty=False, multiple=True)

# genus: abstract, isa subject_statement, adds optional time; value on leaves
write("stable", "subject_assertion",
      doc("subject_assertion", ["subject_statement"], abstract=True, version="3.0.0",
          deps=[TIME_REF_OPT], fields=[]))

# term_assertion: one bound ontology term (species, sex, strain, region, kind)
TERM_VALUE = field(
    "value", "ontology_term",
    "The asserted concept as a bound term (species, sex, strain, instrument "
    "type). The admissible vocabulary is a variable-keyed binding (D9).",
    non_empty=True, scalar=True,
    constraints={"binding": {"keyed_by": "variable", "expansion": "descendants",
                             "node_kind": "class", "strength": "required",
                             "source": "ontology"}})
write("stable", "term_assertion",
      doc("term_assertion", ["subject_assertion"], fields=[TERM_VALUE]))

# date_assertion: a timestamp value cell (instant + precision + source)
DATE_VALUE = field(
    "value", "structure",
    "A date value cell (a real date, not a duration).",
    non_empty=True, scalar=True, blank={}, default={},
    sub_fields=[
        subfield("instant", "char", "ISO-8601 UTC instant (sorts and ranges).",
                 non_empty=True),
        subfield("precision", "char", "year|month|day|hour|minute|second.",
                 non_empty=True, blank="day",
                 constraints={"enum": ["year", "month", "day", "hour", "minute",
                                       "second"]}),
        subfield("source", "char", "The raw input string, preserved."),
    ])
write("stable", "date_assertion",
      doc("date_assertion", ["subject_assertion"], fields=[DATE_VALUE]))

# numeric_assertion: abstract genus; dimensioned scalar leaves
write("stable", "numeric_assertion",
      doc("numeric_assertion", ["subject_assertion"], abstract=True, fields=[]))
for d in DIMS:
    val = field("value", d,
                f"A scalar {d} value cell (canonical + lossless source). An "
                f"assertion is scalar — one cell, no series (J §5).",
                non_empty=True, scalar=True,
                blank={"approximate": False, "source_unit": "", "source_value": 0.0},
                default={"approximate": False, "source_unit": "", "source_value": 0.0})
    write("stable", f"{d}_assertion",
          doc(f"{d}_assertion", ["numeric_assertion"], fields=[val]))


# ---------- 5. subject_relation branch ----------

write("stable", "subject_relation",
      doc("subject_relation", ["base"], abstract=True, fields=[]))

REL_TERM = field("relation", "ontology_term",
                 "The specific relationship as an enumerated ontology term "
                 "(RO-backed). directed: part_of/contained_in/member_of "
                 "(containment) or derived_from/aliquot_of/sample_of/passage_of "
                 "(provenance). V_eta declares the corpus-exercised minimum (D6).",
                 non_empty=True)
write("stable", "directed_relation",
      doc("directed_relation", ["subject_relation"],
          deps=[dep("child", "subject", "The finer/subordinate subject (a part, "
                    "member, or derivative)."),
                dep("parent", "subject", "The whole, group, or source subject.")],
          fields=[REL_TERM]))
write("stable", "undirected_relation",
      doc("undirected_relation", ["subject_relation"],
          deps=[dep("subjects", "subject", "The unordered pair of subjects "
                    "(exactly two); order is meaningless.", multiple=True)],
          fields=[field("relation", "ontology_term",
                        "An association term (paired_with, same_as).",
                        non_empty=True)]))


# ---------- 6. value_set (binding registry, D9) ----------

write("stable", "value_set",
      doc("value_set", ["base"],
          fields=[
              field("name", "char", "Human-readable name of this admissible set.",
                    non_empty=True, blank="", default=""),
              field("root", "ontology_term",
                    "The ontology root; admissible values are its descendants "
                    "when expansion=descendants.", non_empty=False),
              field("expansion", "char",
                    "descendants | self_and_descendants | enumerated.",
                    non_empty=True, blank="descendants", default="descendants"),
              field("members", "ontology_term",
                    "Explicit admissible terms when expansion=enumerated.",
                    non_empty=False, scalar=False, blank=[], default=[]),
              field("source", "char",
                    "The backing ontology/authority (NCBITaxon, OBI, CL, CHEBI, "
                    "UBERON, RO).", non_empty=False, blank="", default=""),
          ]))


# ---------- 7. value mixins: refresh doc (series timing note) ----------
# the <dim> shape mixins keep their array `value`; only the timing note is stale.
for d in DIMS + ["generic_scalar"]:
    tier, p = path_of(d)
    if not p:
        continue
    obj = load(p)
    for f in obj.get("fields", []):
        if f["name"] == "value" and "sample_time" in f.get("documentation", ""):
            f["documentation"] = f["documentation"].split(" Per-sample")[0] + \
                " Per-sample timing is the statement's sample_time cadence (D1)."
    write(tier, d, obj)


# ---------- 8. time_reference: drop `sampling` (cadence moved to sample_time) ----------

tr = load(os.path.join(VETA, "stable", "time_reference.json"))
tr["fields"] = [f for f in tr["fields"] if f["name"] != "sampling"]
tr["document_class"]["class_version"] = "3.0.0"
write("stable", "time_reference", tr)


# ---------- 10. manipulation tier: strict J (D4, D8) ----------
# Retire the delivery-method family and the escape hatches; a manipulation is a
# data-type-named leaf imposing a composite/term value. Route -> method, site ->
# Path S. biological_transfer -> term_manipulation + provenance relation (migrator).

for name in ["injection", "bath", "stimulus_bath", "pharmacological_manipulation",
             "generic_manipulation", "generic_scalar", "generic_scalar_observation",
             "generic_scalar_manipulation", "biological_transfer"]:
    tier, p = path_of(name)
    if p:
        os.remove(p)

# composite value mixins (structure-typed cells; J §7 named composites)
CHEM_SUBS = [subfield("substance", "ontology_term", "The chemical/biological agent "
                      "(CHEBI/NCBITaxon/…).", non_empty=True),
             subfield("amount", "concentration", "Optional amount/concentration.")]
write("stable", "chemical",
      doc("chemical", ["base"], abstract=True, fields=[field(
          "value", "structure", "A single agent: a substance term + optional amount.",
          non_empty=True, blank={}, sub_fields=CHEM_SUBS)]))
write("stable", "formulation",
      doc("formulation", ["base"], abstract=True, fields=[field(
          "value", "structure", "A formulation: one or more chemicals.",
          non_empty=True, blank={}, sub_fields=[
              subfield("chemicals", "structure", "The agents in this formulation.",
                       non_empty=True, scalar=False, sub_fields=CHEM_SUBS)])]))
write("stable", "dose",
      doc("dose", ["base"], abstract=True, fields=[field(
          "value", "structure", "A dose: a formulation delivered at a volume/route.",
          non_empty=True, blank={}, sub_fields=[
              subfield("formulation", "structure", "The substances delivered.",
                       sub_fields=[subfield("chemicals", "structure", "Agents.",
                                            scalar=False, sub_fields=CHEM_SUBS)]),
              subfield("volume", "volume", "Delivered volume (optional)."),
              subfield("route", "ontology_term",
                       "Route of administration (optional; else on method).")])]))

# data-type-named manipulation leaves
write("stable", "dose_manipulation",
      doc("dose_manipulation", ["subject_manipulation", "dose"]))
write("stable", "formulation_manipulation",
      doc("formulation_manipulation", ["subject_manipulation", "formulation"]))
write("stable", "term_manipulation",
      doc("term_manipulation", ["subject_manipulation"], fields=[field(
          "value", "ontology_term",
          "The imposed act/agent as a bound term — a procedure (craniotomy), a "
          "regime (dark rearing), or a transferred material. Payload-free acts "
          "live here; there is NO generic escape hatch (D8).", non_empty=True,
          constraints={"binding": {"keyed_by": "variable", "expansion": "descendants",
                                   "node_kind": "class", "strength": "required",
                                   "source": "ontology"}})]))


# ---------- 11. storage_mode + data_body (sampled_/opaque_) ----------

ss = load(os.path.join(VETA, "stable", "subject_statement.json"))
ss["fields"].append(field(
    "storage_mode", "char",
    "How the value is supplied: inline | reference | body. Machine-set at ingest "
    "by type and size (§8); assertions are always inline.",
    non_empty=False, blank="inline", default="inline",
    constraints={"enum": ["inline", "reference", "body"]}))
write("stable", "subject_statement", ss)

STATEMENT_DEP = dep("statement", "subject_statement",
                    "The one statement this body belongs to (reverse pointer); a "
                    "stream appends more bodies without rewriting the anchor.")
BODY_FILE = [{"name": "body_data", "documentation": "The byte payload (>=1 file)."}]
data_body = doc("data_body", ["base"], abstract=True, maturity="draft", deps=[STATEMENT_DEP])
data_body["file"] = BODY_FILE
write("draft", "data_body", data_body)

sampled = doc("sampled_body", ["data_body"], maturity="draft", fields=[
    field("datum", "structure", "The per-sample value type (kind/dtype/unit/shape).",
          blank={}, sub_fields=[
              subfield("kind", "char", "scalar | array | record.", non_empty=True,
                       blank="scalar",
                       constraints={"enum": ["scalar", "array", "record"]}),
              subfield("dtype", "char", "Numeric dtype (float64, int16, …)."),
              subfield("unit", "char", "The per-sample value unit."),
              subfield("shape", "matrix", "array only: intra-datum dims.")]),
    field("sample_time", "structure",
          "The body-local timeline (D1 — the single home for a body-backed value).",
          blank={}, sub_fields=[
              subfield("regular", "boolean", "Regular grid vs enumerated.",
                       blank=True),
              subfield("t0", "duration", "Local start offset from the anchor."),
              subfield("dt", "duration", "regular: sample spacing."),
              subfield("n", "integer", "Sample count.")]),
    field("summary", "structure", "The searchable value + time rollup.",
          blank={}, sub_fields=[
              subfield("value", "structure", "Per-type value rollup.", blank={}),
              subfield("time", "structure", "min/max/n over sample_time.",
                       blank={})]),
])
sampled["file"] = BODY_FILE
write("draft", "sampled_body", sampled)

opaque = doc("opaque_body", ["data_body"], maturity="draft")
opaque["file"] = BODY_FILE
write("draft", "opaque_body", opaque)


# ---------- 12. formalize `binding` in the meta-schema (D9) ----------
# The constraints subschema is an open object; add a `binding` property so binding
# blocks are structurally validated (require keyed_by) without constraining the
# other constraint keywords (maxLength, enum, …).

meta = load(os.path.join(VETA, "stable", "did_schema_meta.json"))
constraints_schema = meta["$defs"]["field_definition"]["properties"]["constraints"]
constraints_schema["properties"] = {
    "binding": {
        "type": "object",
        "description": "Controlled-vocabulary binding for a term value: either "
                       "keyed on another field (usually `variable`, ontology "
                       "expansion) or a static enumerated value_set (root+values). "
                       "Enforced by the ontology-aware validator (D9).",
        "properties": {
            "keyed_by": {"type": "string"},
            "expansion": {"type": "string"},
            "node_kind": {"type": "string"},
            "strength": {"type": "string",
                         "enum": ["required", "preferred", "suggested"]},
            "source": {"type": "string"},
            "root": {"type": "string"},
            "value_set": {"type": "string"},
            "values": {"type": "array"},
        },
    }
}
with open(os.path.join(VETA, "stable", "did_schema_meta.json"), "w") as f:
    json.dump(meta, f, indent=4)
    f.write("\n")


# ---------- 13. binding-registry meta-file + kind-variable set (D9) ----------

binding_registry = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "https://did-schema.example.org/meta/binding_registry_meta.json",
    "title": "Binding registry for DID/NDI V_eta",
    "description": "Maps a statement's `variable` (and, on interactions, "
                   "method+variable) to the admissible value_set for its term "
                   "value, and declares the kind-defining variables whose presence "
                   "marks a subject's kind (D9). Consumer tooling resolves a term "
                   "value against the bound value_set at validation time.",
    "kind_variables": [
        {"variable": "species", "value_set": "organism_species",
         "root": "NCBITaxon:1", "source": "NCBITaxon"},
        {"variable": "instrument type", "value_set": "device_types",
         "root": "OBI:0000968", "source": "OBI"},
        {"variable": "cell type", "value_set": "cell_types",
         "root": "CL:0000000", "source": "CL"},
        {"variable": "material type", "value_set": "materials",
         "root": "CHEBI:24431", "source": "CHEBI"},
        {"variable": "developmental stage", "value_set": "dev_stages",
         "root": "UBERON:0000105", "source": "UBERON"},
    ],
    "bindings": [],
    "notes": "Corpus-derived variable->value_set bindings are added during "
             "discovery (D3/D6). The kind_variables list makes the subject-kind "
             "ingestion invariant precise; a subject is expected to carry >=1 "
             "term_assertion whose variable is in this set (checked at ingest).",
}
with open(os.path.join(VETA, "stable", "binding_registry_meta.json"), "w") as f:
    json.dump(binding_registry, f, indent=4)
    f.write("\n")


# ---------- 9. regenerate index.json ----------

idx = load(os.path.join(VETA, "index.json"))
idx["set_version"] = "V_eta"
idx["schema_version_value"] = "V_eta"
idx["based_on"] = "V_zeta"
idx["legacy_schema_version_values"] = ["did_v1", "V_zeta"]
idx["notes"] = ("Source of truth for class_name uniqueness and tier placement. "
                "V_eta implements Brainstorm J (ndi-next-steps Summer 2026/"
                "1_Ingestion): bare-identity subjects, subject_relation documents, "
                "restored subject_statement/subject_assertion, subject_observation/"
                "subject_manipulation, Path S locus, data-type leaves (no scalar_ "
                "prefix, no scalar/dataseries split, term_observation), storage_mode "
                "+ data_body, and a hard-validated binding registry. Supersedes "
                "V_zeta (Brainstorm I). NOTE: leaf-tier depth (dose composites, "
                "data_body, binding meta-schema) is an in-progress follow-up.")

schemas = []
for tier in TIERS:
    for p in sorted(glob.glob(os.path.join(VETA, tier, "*.json"))):
        base = os.path.basename(p)
        d = load(p)
        if base in META_FILES:
            schemas.append({"class_name": base[:-5], "tier": tier,
                            "class_version": None, "maturity_level": None,
                            "superclasses": [], "path": f"schemas/V_eta/{tier}/{base}",
                            "is_meta": True})
            continue
        dc = d["document_class"]
        schemas.append({"class_name": dc["class_name"], "tier": tier,
                        "class_version": dc["class_version"],
                        "maturity_level": dc["maturity_level"],
                        "superclasses": dc["superclasses"],
                        "path": f"schemas/V_eta/{tier}/{base}"})
schemas.sort(key=lambda e: (0 if e.get("is_meta") else 1, e["class_name"]))
idx["schemas"] = schemas
with open(os.path.join(VETA, "index.json"), "w") as f:
    json.dump(idx, f, indent=4)
    f.write("\n")

print(f"V_eta built: {len(schemas)} schemas across {TIERS}")
