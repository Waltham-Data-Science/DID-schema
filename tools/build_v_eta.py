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
DELETE = {"scalar_observation", "scalar_manipulation", "annotation", "group_assignment",
          "derivation", "placement", "stimulus_manipulation", "stimulus_approach",
          "oneepoch", "epochclocktimes", "valid_interval", "session_extent",
          "mock"}
# `mock` (a bare `ismock` integer flag) is test-only scaffolding — nothing in the
# corpora or NDI constructs it (`ndi.document('mock')` appears nowhere; the
# +ndi/+mock/ package is a helper namespace, not this class). A production
# go-forward schema shouldn't carry a "this document is fake" class. Dropped.
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

# Remove the genomics families entirely (not corpus-exercised; "don't draft what
# we have no use for"). Expression (expression_observation,
# spatial_expression_observation, expression_matrix_data + 13 variants) AND the
# reference/sequence families (reference_data, reference_sequence_data + fasta,
# reference_annotation_data + gff3/gtf, sequence_read_data + bam/cram/fastq). The
# "reference" concept is deferred to a general tag class (Option B) added when
# there is an actual data_body to tag; the bespoke genomics data classes go now.
for _pat in ("expression*.json", "spatial_expression*.json",
             "reference_*.json", "sequence_read*.json"):
    for _p in glob.glob(os.path.join(VETA, "*", _pat)):
        os.remove(_p)

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
sub["document_class"]["superclasses"] = [{"class_name": "entity"}]   # re-root under entity
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


# --- parameters (D10 qualifiers): conditions the statement was taken under ---
# A list of typed {variable, value}. Each parameter names its `variable` and
# carries exactly ONE nested data-type block (term / count / quantity). The
# "exactly one populated" rule is an INGEST validator, not meta-schema-enforced
# (the closed meta-schema has no oneOf); the full per-dimension type set is a
# provisional extension (D10, open for future review). Value cardinality: an
# array of length 1 (a constant condition) or the measurement's value length
# (one label per reading). Typed by data type via the D9 registry keyed on
# `variable`.
def _param_block(name, doc_text, value_type, value_subs=None):
    return subfield(name, "structure", doc_text, blank={}, sub_fields=[
        subfield("value", value_type,
                 "Typed value(s); an array — length 1 (a constant condition) or the "
                 "measurement's value length (one label per reading).",
                 scalar=False, blank=[], sub_fields=value_subs)])

PARAMETERS = field(
    "parameters", "structure",
    "D10 qualifiers: the conditions a statement was taken under, as a list of typed "
    "{variable, value} entries. Each names its `variable` and carries exactly one "
    "nested data-type block (term / count / quantity). 'Exactly one populated' is an "
    "ingest validator (the closed meta-schema has no oneOf); the full per-dimension "
    "type set is a provisional extension (D10). Value cardinality: length 1 (a "
    "constant condition) or the measurement's value length (one per reading). Typed "
    "by data type via the D9 registry keyed on `variable`.",
    non_empty=False, scalar=False, blank=[], default=[], sub_fields=[
        subfield("variable", "ontology_term",
                 "The condition's name (arm direction, OD600, trial type); "
                 "registry-keyed for its value_set (D9).", non_empty=True),
        _param_block("term", "Categorical value(s): an ontology-term array.",
                     "ontology_term"),
        _param_block("count", "Integer count value(s).", "structure", value_subs=[
            subfield("value", "integer", "The count.", blank=0),
            subfield("unit", "ontology_term", "Optional unit."),
            subfield("approximate", "boolean", "Approximate flag.", blank=False)]),
        _param_block("quantity",
                     "Dimensioned numeric value(s); the dimension is carried by "
                     "`variable` + the D9 registry.", "structure", value_subs=[
            subfield("source_unit", "char", "As-recorded unit."),
            subfield("source_value", "double", "As-recorded value.", blank=0.0),
            subfield("approximate", "boolean", "Approximate flag.", blank=False)]),
    ])

write("stable", "subject_statement",
      doc("subject_statement", ["base"], abstract=True, version="1.0.0",
          deps=[SUBJECT_ID], fields=[VARIABLE, PARAMETERS]))

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

write("stable", "relation",
      doc("relation", ["base"], abstract=True, fields=[]))

REL_TERM = field("relation", "ontology_term",
                 "The specific relationship as an enumerated ontology term "
                 "(RO-backed). directed: part_of/contained_in/member_of "
                 "(containment) or derived_from/aliquot_of/sample_of/passage_of "
                 "(provenance). V_eta declares the corpus-exercised minimum (D6).",
                 non_empty=True)
REL_METHOD = field("method", "ontology_term",
                   "Optional: the procedure that produced a provenance/creation "
                   "relation — the `how` (surgical_dissection, cell_culture_passage, "
                   "biological_pooling, biological_reproduction, aliquoting, …). This "
                   "absorbs the retired `derivation` class's `derivation_method`: a "
                   "timed `derived_from`/`sample_of`/… relation with a `method` and a "
                   "`time_reference` IS the creation event (e.g. a birth = "
                   "`derived_from` + method `biological_reproduction`), so there is no "
                   "separate manipulation-tier derivation document. Empty for standing "
                   "structural relations (part_of, member_of).", non_empty=False)
write("stable", "directed_relation",
      doc("directed_relation", ["relation"],
          deps=[dep("child", "entity", "The finer/subordinate/derived ENTITY (any "
                    "entity — subject part, dataset, award, …)."),
                dep("parent", "entity", "The whole/group/source/target ENTITY."),
                dep("time_reference_#", "time_reference",
                    "Optional: when an EVENT relation happened (e.g. `encountered`, or "
                    "a `derived_from` creation event), as one or more time_reference "
                    "anchors — so an event-relation can be the timestamped record you "
                    "anchor other times against (an `event_relative_reference`). Empty "
                    "for timeless relations (part_of). (D10 multi-party binding.)",
                    non_empty=False, multiple=True)],
          fields=[REL_TERM, REL_METHOD,
                  field("sequence", "integer",
                        "Optional ordinal for ordered relations (e.g. author "
                        "position on a dataset `has_author` edge). Empty for "
                        "unordered relations.", non_empty=False)]))
write("stable", "undirected_relation",
      doc("undirected_relation", ["relation"],
          deps=[dep("entities", "entity", "The unordered pair of entities "
                    "(exactly two); order is meaningless.", multiple=True)],
          fields=[field("relation", "ontology_term",
                        "An association term (paired_with, same_as).",
                        non_empty=True)]))


# ---------- 5b. entity genus + identity entities (dataset metadata redesign) ----
# Referenceable identities share a genus: subject, person, organization,
# publication, award, dataset. They carry a cross-reference `global_identifier`
# and are the *things* other docs point at. Non-subject entities use TYPED
# identity fields (not statements): their attributes are intrinsic identity, not
# provenanced measurements, and names/titles/DOIs are not ontology terms, so
# term_assertion does not fit. Everything relational (authorship, funding,
# citation, affiliation) is a `directed_relation` at the entity layer (generalized
# above): dataset -has_author-> person (+ sequence), dataset -funded_by-> award,
# award -issued_by-> organization, person -affiliated_with-> organization,
# dataset -cites-> publication.
GLOBAL_ID = field(
    "global_identifier", "structure",
    "Cross-reference identifier(s) for this entity (ORCID | ROR | DOI | PMID | "
    "PMCID | RRID | UDI | …). Array — e.g. a publication carries DOI+PMID+PMCID.",
    non_empty=False, scalar=False, blank=[], default=[],
    sub_fields=[subfield("scheme", "char", "Identifier scheme."),
                subfield("value", "char", "Identifier value within the scheme.")])
write("stable", "entity",
      doc("entity", ["base"], abstract=True, fields=[GLOBAL_ID]))

write("stable", "person", doc("person", ["entity"], fields=[
    field("given_name", "char", "Given (personal) name; may include middle "
          "names/initials (given/family per the international convention)."),
    field("family_name", "char", "Family (sur)name."),
    field("email", "char", "Contact email; meaningful when acting as a contact.",
          non_empty=False)]))
write("stable", "organization", doc("organization", ["entity"], fields=[
    field("name", "char", "Organization name (funder or affiliation); ROR via "
          "global_identifier. Location is not stored — it lives in the ROR record.")]))
write("stable", "publication", doc("publication", ["entity"], fields=[
    field("title", "char", "Publication title."),
    field("date", "char", "Publication date/year.", non_empty=False),
    field("authors", "char", "Author citation string — external, NOT decomposed "
          "into person entities (cited papers' authors stay coarse).",
          non_empty=False)]))
write("stable", "award", doc("award", ["entity"], fields=[
    field("title", "char", "Award/grant title; award number / grant DOI via "
          "global_identifier. Its funder is a `directed_relation` -> organization.",
          non_empty=False)]))
# web_resource IS an entity: a referenceable external resource (a documentation
# page, a data repository, a protocol, a code repo, a homepage). Its identity IS
# its URL (carried on global_identifier, scheme="URL"), so it needs no extra
# fields beyond an optional human label. A dataset's documentation/repository/
# homepage links are NOT string fields on the dataset — they are references, and
# in this model references are relations: dataset -documented_by-> web_resource,
# dataset -stored_at-> web_resource. (A DOI reference to a paper is a
# `directed_relation -> publication`; a DOI/URI to a resource is one -> web_resource.)
write("stable", "web_resource", doc("web_resource", ["entity"], fields=[
    field("label", "char", "Optional human-readable label for the resource "
          "(e.g. 'full documentation', 'GitHub repo'); the URL rides on "
          "global_identifier (scheme='URL').", non_empty=False)]))
# dataset IS the entity (target of the metadata_editor decomposition — a follow-up
# migrator reshapes the Soph metadata_structure blob into this + person/award/
# publication entities + relations; metadata_editor is kept as the source until then).
# Documentation/homepage/repository links are NOT fields here — they are
# `directed_relation`s -> web_resource / -> publication (references are relations).
write("stable", "dataset", doc("dataset", ["entity"], fields=[
    field("full_name", "char", "Full dataset name."),
    field("short_name", "char", "Short dataset name.", non_empty=False),
    field("version", "char", "Version identifier.", non_empty=False),
    field("description", "char", "Dataset description / abstract.", non_empty=False),
    field("license", "char", "License.", non_empty=False),
    field("release_date", "char", "Release date.", non_empty=False)]))

# session JOINS the entity genus. A recording session is the most-referenced
# identity in the schema (base.session_id is on nearly every document) and is
# exactly a "referenceable identity other docs point at" — so it belongs with
# subject/dataset/person as an `entity`, gaining `global_identifier` (a cloud /
# DANDI session id has a home) and, crucially, becoming a valid directed_relation
# endpoint. That is what lets the session<->dataset membership (the legacy
# `session_in_a_dataset` / `dataset_session_info` bundles) become a first-class
# `directed_relation` (session -part_of-> dataset) rather than a loose char id, and
# session provenance (session -derived_from-> session) become a relation too. Only
# the superclass changes — every existing `session_id` dep still resolves
# (must_refer is declarative), so there is no blast radius.
sess = load(os.path.join(VETA, "stable", "session.json"))
sess["document_class"]["superclasses"] = [{"class_name": "entity"}]
write("stable", "session", sess)


# ---------- 6. (value_set removed) ----------
# The `value_set` document class is DROPPED: it was orphaned (nothing referenced
# it as a document; no `must_refer -> value_set`) and redundant with the binding
# registry, which already carries the admissible-set definition inline per
# variable (root/expansion/source/members). The registry
# (binding_registry_meta.json) is the single source of admissible-value sets; an
# admissible set is a registry entry, not a stored document. (Q1.)


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

# session_bounded_reference (D10 multi-party binding): a bounded [start, end]
# window relative to the session/assay origin, needing NO parent interaction or
# epoch. This is the shared hub a multi-party event's measurements (and its
# event-relation) depend on — e.g. one C. elegans encounter window
# (onset..offset). Session identity rides on base.session_id, so no dep is
# required. Fills the gap between session_relative_reference (ordinal, no metric)
# and event_/epoch_relative_reference (which require a parent event/epoch).
_DUR = {"approximate": False, "source_unit": "", "source_value": 0.0}
write("stable", "session_bounded_reference",
      doc("session_bounded_reference", ["time_reference"], fields=[
          field("relation", "char",
                "Ordinal relation to the session (default 'during').",
                non_empty=False, blank="during", default="during"),
          field("start", "duration",
                "Window start, relative to the session/assay origin.",
                non_empty=False, blank=_DUR, default=_DUR),
          field("end", "duration",
                "Window end, relative to the session/assay origin.",
                non_empty=False, blank=_DUR, default=_DUR)]))


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

# image_observation: the body-backed data-type leaf the did_v1 `image_stack`
# (7,007 docs in JH) folds onto (§C.4). The pixel frames live in a
# sampled_body/opaque_body (storage_mode: body); the stable `image` mixin carries
# the inline geometry/format metadata (image_type/format/resolution). Draft: the
# broader imageseries/dataseries/timeseries_observation branch this begins to
# supersede is retired WITH the NDI-side ingest work (see the header note), not
# here -- so this addition is purely additive and does not touch that branch.
write("draft", "image_observation",
      doc("image_observation", ["subject_observation", "image"], maturity="draft"))


# ---------- 11b. pre-seed J §7's comprehensive numeric set ----------
# V_zeta shipped only 12 dimensioned numerics. J §7 prescribes a comprehensive
# pre-seeded set; discovery confirmed the gap (Dab startle amplitudes = a.u. ->
# intensity; JH C. elegans velocities/decelerations -> velocity/acceleration).
# Each new numeric gets a value mixin + an _observation + an _assertion leaf
# (a _manipulation is added only for a quantity something is imposed as; the
# existing temperature/pressure/frequency manipulations carry over from V_zeta).
CELL = {"approximate": False, "source_unit": "", "source_value": 0.0}
NUMERIC_SEED = [
    ("intensity", "dimensionless (a.u.) — dF/F, fluorescence, ratios, amplitudes"),
    ("velocity", "m/s"), ("acceleration", "m/s^2"), ("area", "m^2"),
    ("angle", "rad"), ("angular_velocity", "rad/s"), ("force", "N"),
    ("energy", "J"), ("power", "W"), ("charge", "C"), ("resistance", "ohm"),
    ("conductance", "S"), ("capacitance", "F"), ("amount", "mol"),
    ("ph", "pH (log scale)"),
]
for name, unit in NUMERIC_SEED:
    write("stable", name,
          doc(name, ["base"], abstract=True, fields=[field(
              "value", name,
              "A %s value cell (canonical + lossless source). Series-as-cardinality: "
              "an array of the cell; per-sample timing is the statement's sample_time."
              % unit, non_empty=True, scalar=False, blank=[], default=[CELL])]))
    write("stable", name + "_observation",
          doc(name + "_observation", ["subject_observation", name]))
    write("stable", name + "_assertion",
          doc(name + "_assertion", ["numeric_assertion"], fields=[field(
              "value", name, "A scalar %s value cell." % unit,
              non_empty=True, scalar=True, blank=CELL, default=CELL)]))
# intensity is also imposable (e.g. a stimulus a.u. level)
write("stable", "intensity_manipulation",
      doc("intensity_manipulation", ["subject_manipulation", "intensity"]))


# ---------- 12. formalize `binding` in the meta-schema (D9) ----------
# The constraints subschema is an open object; add a `binding` property so binding
# blocks are structurally validated (require keyed_by) without constraining the
# other constraint keywords (maxLength, enum, …).

meta = load(os.path.join(VETA, "stable", "did_schema_meta.json"))
type_enum = meta["$defs"]["field_definition"]["properties"]["type"]["enum"]
for _seed_name, _ in NUMERIC_SEED:          # J §7 comprehensive numeric set
    if _seed_name not in type_enum:
        type_enum.append(_seed_name)
constraints_schema = meta["$defs"]["field_definition"]["properties"]["constraints"]
constraints_schema["properties"] = {
    "binding": {
        "type": "object",
        "description": "Controlled-vocabulary binding for a term value: either "
                       "keyed on another field (usually `variable`, ontology "
                       "expansion) or an inline admissible set given as a static "
                       "enumeration (`values`) or an ontology subtree "
                       "(`ontology` + `root_node`). Enforced by the "
                       "ontology-aware validator (D9).",
        "properties": {
            "keyed_by": {"type": "string"},
            "expansion": {"type": "string"},
            "node_kind": {"type": "string"},
            "strength": {"type": "string",
                         "enum": ["required", "preferred", "suggested"]},
            "ontology": {"type": "string"},
            "root_node": {"type": "string"},
            "values": {"type": "array"},
        },
    }
}
with open(os.path.join(VETA, "stable", "did_schema_meta.json"), "w") as f:
    json.dump(meta, f, indent=4)
    f.write("\n")


# ---------- 13. binding-registry meta-file + kind-variable set (D9) ----------

# ---------- D6 relation vocabulary ----------
# The admissible relation terms carried on `directed_relation.relation` /
# `undirected_relation.relation` (an ontology_term whose `name` is one of these).
# The schema field is free-form (validated as an ontology_term, not against this
# list), so this registry is the SINGLE enumerated source of truth for consumer
# tooling and the D6 curation.
#
#   node          backing CURIE (RO/BFO where a standard term exists; "" = an open
#                 D6 curation slot, not yet mapped).
#   class         the carrier document class the term is minted as -- the fact that
#                 governs endpoint symmetry and which optional fields are meaningful:
#                   directed_relation   -> asymmetric (parent != child); may carry
#                                          `sequence` (see ordered) and `method`.
#                   undirected_relation -> symmetric member set (`member_types`).
#                 This pins term -> class (a `part_of` minted as undirected is an
#                 error the validator can catch). All current terms are directed.
#   child_types /
#   parent_types  the entity/data classes admissible at each endpoint of a directed
#                 edge (child --name--> parent). [] = an open slot pending D6.
#                 (An undirected term would use `member_types` instead.)
#   *_role        human gloss of each endpoint.
#   ordered       the directed_relation `sequence` field is semantically meaningful
#                 (e.g. author order). class alone does not imply this -- every
#                 directed edge *has* an optional sequence; ordered marks the ones
#                 where it carries meaning.
#   timed         the edge denotes an event that may carry a `method` / time anchor.
def _rel(name, node, child_role, parent_role, child_types, parent_types,
         *, cls="directed_relation", timed=False, ordered=False):
    return {"name": name, "node": node, "class": cls,
            "child_role": child_role, "parent_role": parent_role,
            "child_types": child_types, "parent_types": parent_types,
            "timed": timed, "ordered": ordered}

RELATION_VOCABULARY = [
    # containment / structure
    _rel("part_of", "BFO:0000050", "the part", "the whole",
         ["session"], ["dataset"]),
    _rel("contained_in", "RO:0001018", "the contained", "the container",
         [], []),
    _rel("member_of", "RO:0002350", "the member", "the group",
         ["subject"], ["subject_group"]),
    # provenance / creation (timed: the creation event may carry a time_reference)
    _rel("derived_from", "RO:0001000", "the derivative", "the source",
         [], [], timed=True),
    _rel("sample_of", "", "the sample", "the sampled source",
         ["subject"], ["subject"], timed=True),
    _rel("aliquot_of", "", "the aliquot", "the parent quantity",
         ["subject"], ["subject"], timed=True),
    _rel("passage_of", "", "the passage", "the parent culture",
         ["subject"], ["subject"], timed=True),
    # agent / instrument role
    _rel("observes", "", "the instrument-subject", "the observed specimen",
         ["subject"], ["subject"]),
    # event
    _rel("encountered", "", "the encountering subject", "the encountered subject",
         ["subject"], ["subject"], timed=True),
    # bibliographic (entity layer)
    _rel("has_author", "", "the dataset", "the author (person)",
         ["dataset"], ["person"], ordered=True),
    _rel("cites", "", "the citing dataset", "the cited publication",
         ["dataset"], ["publication"]),
    # funding (entity layer)
    _rel("funded_by", "", "the funded dataset", "the award",
         ["dataset"], ["award"]),
    _rel("issued_by", "", "the award", "the issuing organization",
         ["award"], ["organization"]),
    # affiliation (entity layer)
    _rel("affiliated_with", "", "the person", "the organization",
         ["person"], ["organization"]),
    # reference / storage (entity layer)
    _rel("documented_by", "", "the documented entity", "the web_resource",
         ["entity"], ["web_resource"]),
    _rel("stored_at", "", "the stored dataset",
         "the web_resource location of the remote copy",
         ["dataset"], ["web_resource"]),
    _rel("hosted_by", "", "the web_resource", "the hosting organization",
         ["web_resource"], ["organization"]),
]

binding_registry = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "https://did-schema.example.org/meta/binding_registry_meta.json",
    "title": "Binding registry for DID/NDI V_eta",
    "description": "Two coordinated registries keyed on ontology nodes. VALUE "
                   "bindings map a statement's `variable.node` (and, on "
                   "interactions, `method.node`) within a carrier `class` to the "
                   "admissible set for its term value, given inline as either a "
                   "`data_type`, an enumerated `values` list, or an ontology "
                   "subtree (`ontology` + `root_node`). RELATION bindings "
                   "(`relation_vocabulary`) map a `relation.node` to its carrier "
                   "`class` (directed_relation / undirected_relation) and the "
                   "admissible endpoint entity types. `kind_variables` declares the "
                   "kind-defining variables whose presence marks a subject's kind "
                   "(D9). Consumer tooling resolves a value or endpoint against the "
                   "matching binding at validation time.",
    # kind_variables: variable -> admissible ontology subtree. Each is a value
    # binding whose set is always a subtree (ontology + root_node), so no inline
    # `values`/`data_type`. `variable.node` is the property CURIE (\"\" = open slot).
    "kind_variables": [
        {"variable": {"node": "", "name": "species"},
         "ontology": "NCBITaxon", "root_node": "NCBITaxon:1"},
        {"variable": {"node": "", "name": "instrument type"},
         "ontology": "OBI", "root_node": "OBI:0000968"},
        {"variable": {"node": "", "name": "cell type"},
         "ontology": "CL", "root_node": "CL:0000000"},
        {"variable": {"node": "", "name": "material type"},
         "ontology": "CHEBI", "root_node": "CHEBI:24431"},
        {"variable": {"node": "", "name": "developmental stage"},
         "ontology": "UBERON", "root_node": "UBERON:0000105"},
    ],
    # Populated by the D3/D6 corpus sweep. Each row (a VALUE binding) has shape:
    #   {"variable": {"node", "name"}, "method"?: {"node", "name"},
    #    "class": "subject_observation" | "subject_manipulation" | "subject_assertion",
    #    then EXACTLY ONE admissible-set spec:
    #      "data_type": "<numeric composite>"      (e.g. mass, voltage) OR
    #      "values": [ ... ]                       (static enumeration) OR
    #      "ontology": "<prefix>", "root_node": "<CURIE>"   (subtree)}
    "bindings": [],
    "relation_vocabulary": RELATION_VOCABULARY,
    "notes": "VALUE bindings (`bindings`) are keyed on `variable.node` (+ "
             "`method.node` on interactions) within a carrier `class` "
             "(subject_observation / subject_manipulation / subject_assertion); "
             "the admissible set is given inline as `data_type`, `values`, or "
             "`ontology`+`root_node` (there is no separately-named value_set). They "
             "are populated by the D3/D6 corpus sweep. `kind_variables` makes the "
             "subject-kind ingestion invariant precise; a subject is expected to "
             "carry >=1 term_assertion whose variable is in this set (checked at "
             "ingest). RELATION bindings (`relation_vocabulary`) enumerate the "
             "admissible relation terms (D6): the value carried on "
             "`directed_relation.relation` / `undirected_relation.relation` is a "
             "member of this set. `class` pins the term to its carrier "
             "(directed_relation / undirected_relation) and thus its endpoint "
             "symmetry; `child_types`/`parent_types` (directed) or `member_types` "
             "(undirected) constrain the endpoint entity classes. `node` is the "
             "backing ontology CURIE (RO/BFO where one exists; \"\" = an open D6 "
             "curation slot). `ordered` marks terms where the directed `sequence` "
             "field is meaningful; `timed` marks event edges that may carry a "
             "`method`/time anchor.",
}
with open(os.path.join(VETA, "stable", "binding_registry_meta.json"), "w") as f:
    json.dump(binding_registry, f, indent=4)
    f.write("\n")


# ---------- 14. retarget the did_v1 conversion docs to V_eta (Brainstorm J) ----------
# The conversions/ tree was copied from V_zeta. Retarget: bulk-rename safe tokens
# (handles the design-neutral tuning/calc docs), prepend strict-J banners to the
# hard/semi docs, rewrite the index, and add the fan-out note. Authoritative
# field-level mapping stays in V_eta_migration_plan.md Part D.

import re as _re
CONV = os.path.join(VETA, "conversions", "from_did_v1")
_dims_re = "|".join(DIMS)

for p in sorted(glob.glob(os.path.join(CONV, "*.md"))):
    b = os.path.basename(p)
    if b in ("_index.md",):
        continue
    s = open(p).read()
    s = _re.sub(rf"scalar_({_dims_re})_observation", r"\1_observation", s)
    s = _re.sub(rf"`scalar_({_dims_re})`", r"`\1`", s)
    s = _re.sub(rf"\bscalar_({_dims_re})\b", r"\1", s)
    s = s.replace("scalar_observation", "subject_observation")
    s = s.replace("scalar_manipulation", "subject_manipulation")
    s = s.replace("categorical_observation", "term_observation")
    s = s.replace("V_zeta", "V_eta").replace("Brainstorm I", "Brainstorm J")
    s = s.replace("Brainstorm-I", "Brainstorm-J")
    open(p, "w").write(s)

BANNERS = {
    "treatment.md": "> **V_eta retarget (Brainstorm J).** Target: data-type-named "
    "`subject_manipulation` leaves — `dose_manipulation` (substance; `dose`/`formulation`/"
    "`chemical` composite value), `temperature_manipulation` (thermal), another "
    "`<quantity>_manipulation`, or `term_manipulation` (payload-free procedure/regime). "
    "**No `injection`/`bath`/`generic_manipulation`** (retired in strict J, D8): route → "
    "`method`, substance → the `dose` composite. The focal site is **Path S** — an "
    "attributed structure becomes a part-`subject` + a `part_of` `directed_relation`; a "
    "merely-located structure is a `term_observation` value (no `target_structure`). "
    "Authoritative mapping: `V_eta_migration_plan.md` Parts C–D. Body below is retained "
    "V_zeta reference (token-retargeted).",
    "ontology_table_row.md": "> **V_eta retarget (Brainstorm J).** Each column → a "
    "`subject_assertion` leaf (timeless — `term_assertion`/`date_assertion`/`<dim>_assertion`) "
    "**or** a `subject_observation` leaf (timed — `<dim>_observation`/`term_observation`), by "
    "timelessness (D9/C.2). One-word quantity names (no `scalar_`); term columns → "
    "`term_observation`; DOB → `date_assertion`. Anatomy → Path S. See "
    "`V_eta_migration_plan.md` Part D.",
    "treatment_drug.md": "> **V_eta retarget.** → `dose_manipulation` (substance = `dose`/"
    "`formulation` composite; drug identity on the chemical term); route → `method`; site → "
    "Path S. Not `injection`.",
    "virus_injection.md": "> **V_eta retarget.** → `dose_manipulation`/`formulation_manipulation` "
    "(virus on the chemical term; titer/dilution in the composite); site → Path S. Not "
    "`injection (kind:virus)`.",
    "treatment_transfer.md": "> **V_eta retarget (D4).** → a `term_manipulation` for the "
    "transfer act **+ a provenance `directed_relation`** (recipient material "
    "`derived_from`/`sample_of` donor). No `biological_transfer` class; the donor is a "
    "relation, not a dependency.",
    "subject_group.md": "> **V_eta retarget.** → a **bare** `subject` (v3.0.0; "
    "`is_group`/`is_biological` removed — group-ness is derived from `member_of` edges). "
    "did_v1 records no membership, so no relations are synthesized.",
    "probe_location.md": "> **V_eta retarget (D5).** → a `term_observation` about the "
    "probe(-subject): `variable` = a spatial relation, `value` = the atlas term, + a "
    "synthesized time anchor.",
    "ontology_image.md": "> **V_eta retarget (D5).** → a `term_observation` about the imaged "
    "element/subject (region term as `value`, spatial-relation `variable`); any image file → "
    "an `opaque_body`/`sampled_body`.",
    "ontology_label.md": "> **V_eta retarget (D5).** → a `term_observation` (or "
    "`term_assertion` if genuinely timeless) about the labeled element/subject.",
}
for fn, banner in BANNERS.items():
    p = os.path.join(CONV, fn)
    s = open(p).read()
    if "V_eta retarget" not in s.split("\n\n")[0]:
        open(p, "w").write(banner + "\n\n" + s)

# fan-out note in _universal_renames.md
ur = os.path.join(CONV, "_universal_renames.md")
s = open(ur).read()
if "## 11. V_eta fan-out" not in s:
    marker = "## Cross-references"
    note = ("## 11. V_eta fan-out (Brainstorm J)\n\n"
            "Beyond the field-level renames above, a V_eta migrator may **emit "
            "additional documents alongside** the primary output (the 1→N "
            "cell-of-bodies mechanism):\n\n"
            "- a **part-`subject`** + a **`directed_relation`** (`part_of`) for an "
            "attributed anatomical locus under Path S (find-or-create, deduplicated "
            "per animal — Part C.1);\n"
            "- a **`subject_assertion`** for a timeless column split out of an "
            "`ontology_table_row` (Part C.2);\n"
            "- a **provenance `directed_relation`** for a `treatment_transfer` donor "
            "(D4); a **synthesized time anchor** for clockless rows.\n\n"
            "These are new destination shapes, not new rename rules.\n\n")
    s = s.replace(marker, note + marker, 1)
    open(ur, "w").write(s)

# rewrite the index (authoritative V_eta status table)
INDEX_MD = """# did_v1 -> V_eta conversion index

Enumerates every `did_v1` document class a migrator must convert to **V_eta**
(Brainstorm J), with status. The **authoritative field-level mapping** is
`schemas/V_eta_migration_plan.md` (Part D per-class + Part C new machinery);
these per-class docs carry the detailed field moves and each hard/semi doc opens
with a strict-J retarget banner (the body below is retained V_zeta reference).
Cross-cutting renames: [`_universal_renames.md`](_universal_renames.md); file
handling: [`_files.md`](_files.md).

## Hard transforms (subject-side restructuring)

| did_v1 source | V_eta target(s) | Status | Doc |
|---|---|---|---|
| `treatment` | `dose_manipulation` / `temperature_manipulation` / `<quantity>_manipulation` / `term_manipulation` (+ anchor; + part-`subject` + `part_of` when attributed, else a `term_observation` location value) | drafted | [treatment.md](treatment.md) |
| `ontology_table_row` | per column -> a `subject_assertion` (timeless) or `subject_observation` (timed) leaf + anchor; anatomy -> Path S (1->N) | drafted | [ontology_table_row.md](ontology_table_row.md) |
| `subject_group` | bare `subject` (v3.0.0; no `is_group`) | drafted | [subject_group.md](subject_group.md) |
| `treatment_drug` | `dose_manipulation` (drug on the chemical term) + anchor | drafted | [treatment_drug.md](treatment_drug.md) |
| `virus_injection` | `dose_manipulation` / `formulation_manipulation` (virus on the chemical term) + anchor | drafted | [virus_injection.md](virus_injection.md) |
| `treatment_transfer` | `term_manipulation` + a provenance `directed_relation` (D4) | drafted | [treatment_transfer.md](treatment_transfer.md) |

## Semi-mechanical (D5 -> `term_observation`)

| did_v1 source | V_eta target | Status | Doc |
|---|---|---|---|
| `probe_location` | `term_observation` (probe-subject; spatial-relation `variable`) | drafted | [probe_location.md](probe_location.md) |
| `ontology_image` | `term_observation` (region term; image file -> body) | drafted | [ontology_image.md](ontology_image.md) |
| `ontology_label` | `term_observation` / `term_assertion` (label term) | drafted | [ontology_label.md](ontology_label.md) |

## Mechanical (design-neutral; carry over unchanged, token-retargeted)

`contrast_tuning`(+`_calc`), `contrast_sensitivity_calc`,
`orientation_direction_tuning`/`oridirtuning_calc`,
`spatial_frequency_tuning`(+`_calc`), `speed_tuning`(+`_calc`),
`temporal_frequency_tuning`(+`_calc`), `reverse_correlation`,
`hartley_reverse_correlation`, `hartley_calc` -- no subject-side surface.

## Notes

- **Not migrated:** `stimloopsplitter_calc` (deprecated per domain owner).
- **Relations minted (D6):** only `part_of` (Path S) + one provenance term
  (`sample_of`/`derived_from`, `treatment_transfer`); confirmed in discovery mode.
"""
with open(os.path.join(CONV, "_index.md"), "w") as f:
    f.write(INDEX_MD)


# ---------- 8b. element retirement: must_refer element -> subject (D2) --------
# Brainstorm J fully retires the recording-side `element` class: everything it
# represented is a `subject` (device / part / derived signal). The DID-matlab
# migrator emits element -> subject (id preserved) + kind assertions + a lineage
# relation, so every dependency that pointed at `element` now resolves to the
# subject it became; retarget those must_refer tokens so the reference also
# type-checks. (The `element` class file itself is removed in the Phase-8
# cleanup, once the element_epoch / position / distance folds land.)
for tier in TIERS:
    for p in sorted(glob.glob(os.path.join(VETA, tier, "*.json"))):
        if os.path.basename(p) in META_FILES:
            continue
        d = load(p)
        dirty = False
        for dep_ in d.get("depends_on", []):
            toks = [t for t in dep_["must_refer_to_document_class"].split(",") if t]
            new_toks = ["subject" if t == "element" else t for t in toks]
            if new_toks != toks:
                dep_["must_refer_to_document_class"] = ",".join(new_toks)
                dirty = True
        if dirty:
            with open(p, "w") as f:
                json.dump(d, f, indent=4)
                f.write("\n")


# ---------- 8c. governance: type unset _id references -------------------------
# Acquisition-infra and element-family dependencies shipped with an empty
# must_refer_to_document_class, so their reference type was unvalidated (a
# daqreader_id could point at anything and validate). Type the unambiguous ones.
# element / probe / device / agent references resolve to `subject` (element
# retired, device-as-subject -- this also catches the element_id deps the 8b
# rename missed because they were empty rather than "element"); the surviving
# acquisition classes get their own class. References into families still being
# restructured (stimulus, analysis/calc, spike sorting) are intentionally left
# untyped for now -- typing them would only need re-typing when those retire.
GOV_REF = {
    "element_id": "subject", "underlying_element_id": "subject",
    "probe_id": "subject", "stimulator_id": "subject",
    "recipient_id": "subject", "donor_id": "subject",
    "filenavigator_id": "filenavigator", "daqreader_id": "daqreader",
    "daqsystem_id": "daqsystem", "daqmetadatareader_id": "daqmetadatareader",
    "syncrule_id": "syncrule", "syncrule_id_#": "syncrule",
}
for tier in TIERS:
    for p in sorted(glob.glob(os.path.join(VETA, tier, "*.json"))):
        if os.path.basename(p) in META_FILES:
            continue
        d = load(p)
        dirty = False
        for dep_ in d.get("depends_on", []):
            if not dep_.get("must_refer_to_document_class", "") \
                    and dep_.get("name") in GOV_REF:
                dep_["must_refer_to_document_class"] = GOV_REF[dep_["name"]]
                dirty = True
        if dirty:
            with open(p, "w") as f:
                json.dump(d, f, indent=4)
                f.write("\n")


# ---------- 8d. governance: type the now-settled stimulus family -------------
# 8c deliberately left the stimulus family untyped ("still being restructured").
# D-B (V_eta_nonsubject_cohesiveness_plan §2.B) has now settled it: the stimulus
# documents are KEPT as bodies-of-record (stimulus_presentation carries the raw
# params; stimulus_response_scalar carries the computed responses), and the
# subject-side statements are minted downstream -- stimulus_manipulation by the
# NDI second pass (the animal subject is a recording-graph fact, not in the
# presentation doc), and the response -> observation by the D-C analysis
# decomposition. With the family settled, its one unambiguous edge can be typed:
# every empty `stimulus_presentation_id` genuinely points at a stimulus_presentation
# (control_stimulus_ids, stimulus_response, stimulus_parameter[_table]). The
# already-typed carriers (stimulus_manipulation, reverse_correlation, ...) are
# left as-is (fill-empties-only). `stimulus_response_scalar.stimulus_response_id`
# is left untyped: its v1 antecedent was stimulus_response_scalar_parameters_id
# (a parameters doc, not a response), so its referent class needs review first.
GOV_REF_STIM = {
    "stimulus_presentation_id": "stimulus_presentation",
}
for tier in TIERS:
    for p in sorted(glob.glob(os.path.join(VETA, tier, "*.json"))):
        if os.path.basename(p) in META_FILES:
            continue
        d = load(p)
        dirty = False
        for dep_ in d.get("depends_on", []):
            if not dep_.get("must_refer_to_document_class", "") \
                    and dep_.get("name") in GOV_REF_STIM:
                dep_["must_refer_to_document_class"] = GOV_REF_STIM[dep_["name"]]
                dirty = True
        if dirty:
            with open(p, "w") as f:
                json.dump(d, f, indent=4)
                f.write("\n")


# ---------- 8e. broaden event anchors for the derivation fold ----------------
# Retiring `derivation` (folded into directed_relation) means a creation/birth
# event is now a `directed_relation` (a subject_relation), NOT a subject_interaction.
# The event_* references anchor to `subject_interaction`; broaden them to also
# accept a `directed_relation` so developmental anchoring (e.g. "P25" =
# event_relative against the biological_reproduction event) still resolves.
# must_refer_to_document_class is comma-separated (a union of accepted classes).
EVENT_ANCHOR = {
    "event_relative_reference": "reference_event",
    "event_bounded_reference": "bounding_event",
}
for cls, depname in EVENT_ANCHOR.items():
    tier, p = path_of(cls)
    if not p:
        continue
    d = load(p)
    changed = False
    for dep_ in d.get("depends_on", []):
        if dep_.get("name") == depname:
            cur = dep_.get("must_refer_to_document_class", "")
            toks = [t for t in cur.split(",") if t]
            if "directed_relation" not in toks:
                toks.append("directed_relation")
                dep_["must_refer_to_document_class"] = ",".join(toks)
                changed = True
    if changed:
        with open(p, "w") as f:
            json.dump(d, f, indent=4)
            f.write("\n")


# ---------- 12. data genus (Q2): data -> {data_type, data_body} ---------------
# The quantity composites (angle, voltage, …) were flat `⊂ base`, and the data
# families (data_body vs the ⊂base genomics/series families) were fragmented.
# Introduce a `data` genus: data_type (the value-type composites) and data_body
# (bulk storage) both descend from it. Reparent the numeric composites under
# data_type and data_body under data. (Folding the genomics/series families under
# data_body is deferred pending the reference-role redesign — Q3.)
write("stable", "data", doc("data", ["base"], abstract=True, fields=[]))
write("stable", "data_type",
      doc("data_type", ["data"], abstract=True, fields=[]))
# dimensional composites + numeric seeds + the substance composites (dose /
# formulation / chemical): all are value TYPES a statement's leaf carries, so they
# belong under data_type alongside the dimensional ones (they were previously left
# ⊂ base — the inconsistency this closes).
DATA_TYPES = list(DIMS) + [n for n, _ in NUMERIC_SEED] + ["dose", "formulation", "chemical"]
for name in DATA_TYPES:
    p = os.path.join(VETA, "stable", name + ".json")
    if not os.path.exists(p):
        continue
    d = load(p)
    d["document_class"]["superclasses"] = [{"class_name": "data_type"}]
    with open(p, "w") as f:
        json.dump(d, f, indent=4); f.write("\n")
for tier in ("stable", "draft"):
    p = os.path.join(VETA, tier, "data_body.json")
    if os.path.exists(p):
        d = load(p)
        d["document_class"]["superclasses"] = [{"class_name": "data"}]
        with open(p, "w") as f:
            json.dump(d, f, indent=4); f.write("\n")

# manipulation leaves for the IMPOSABLE subset of data_types (Q2). Observations /
# assertions apply to any measurable quantity; a manipulation only exists for a
# quantity an experimenter can IMPOSE. V_zeta shipped temperature/pressure/
# frequency/intensity; add the electrophysiology/mechanics imposables. (velocity,
# power, ph, angular_velocity are candidates left off pending confirmation.)
for name in ["voltage", "current", "force", "concentration"]:
    write("stable", name + "_manipulation",
          doc(name + "_manipulation", ["subject_manipulation", name]))


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

# ---- disposition: an auditable 3-state marker the viewer badges, so the tree
# distinguishes the FINAL go-forward set from what is leaving / not yet resolved.
#   persist     — settled go-forward class (the ~161 final set).
#   retire      — decided to dissolve/delete; NOT in final V1 (with a track note).
#   in_progress — persists in some form but its ⑥/⑦ disposition is NOT yet
#                 finalized (owes the governance sweep + pending walkthrough
#                 chunks b/c/e) — i.e. the acquisition/infra we have not walked yet.
# Keep these lists in sync with V_eta_final_class_set.md / the ⑥/⑦ walkthrough.
_RET_SOURCES = {"element", "openminds", "openminds_subject", "openminds_element",
    "openminds_stimulus", "metadata_editor", "dataset_remote",
    "session_in_a_dataset", "dataset_session_info"}
_RET_CARRIERS = {"timeseries_data", "timeseries_data_binary", "timeseries_data_csv",
    "timeseries_data_edf", "dataseries_data", "dataseries_pyramid", "imageseries_data",
    "ephys_zarr", "image_zarr", "zarr", "image", "image_collection", "generic_file",
    "pyraview"}
_RET_TOOBS = {"probe_location", "probe_geometry", "electrode_offset_voltage",
    "position_metadata", "distance_metadata", "ontology_label", "ontology_table_row",
    "ontology_image"}
_RET_HOLDOVER = {"calculator", "measurement"}
_ANALYSIS_RE = _re.compile(r"(_calc$|_calc_|tuning|stimulus_response|spike|cluster|"
    r"vmspike|binnedspikerate|jrclust|sorting_param|neuron_extracellular|hartley|"
    r"oridir|reverse_correlation|fitcurve|tuning_fit|simple_calc|contrast_sensitivity|"
    r"site2channelmap|vmneuralresponse|stimulus_parameter)")
_IN_PROGRESS = {"daqsystem", "daqreader", "daqmetadatareader", "daqreader_ndr",
    "daqreader_epochdata_ingested", "daqreader_image_epochdata_ingested",
    "daqreader_mfdaq_epochdata_ingested", "daqmetadatareader_epochdata_ingested",
    "epochfiles_ingested", "epochid", "element_epoch", "filenavigator", "syncgraph",
    "syncrule", "syncrule_mapping", "directory", "ngrid", "dataseries_channel_map",
    "binaryseries_parameters", "filter", "instrument", "interaction_purpose",
    # `app` genus (parents a mix of retiring analysis classes + the stimulus
    # bodies — its survival is unresolved) and its non-retiring children; the
    # D-B stimulus bodies-of-record whose sampled_body fate is still open; and the
    # demo/test fixtures whose place in the final V1 set is not settled.
    "app", "stimulus_presentation", "control_stimulus_ids",
    "demo_ndi", "demo_ndi_mock"}

def _disposition(name):
    if name in _RET_SOURCES:  return ("retire", "Phase-8 source (migrator → delete)")
    if name in _RET_HOLDOVER or _ANALYSIS_RE.search(name):
        return ("retire", "D-C analysis-tier decompose")
    if name in _RET_CARRIERS: return ("retire", "2.D → data_body fold")
    if name in _RET_TOOBS:    return ("retire", "→ observations (needs-NDI / D10-11)")
    if name in _IN_PROGRESS:  return ("in_progress", "⑥/⑦ walkthrough pending")
    return ("persist", None)

schemas = []
for tier in TIERS:
    for p in sorted(glob.glob(os.path.join(VETA, tier, "*.json"))):
        base = os.path.basename(p)
        d = load(p)
        if base in META_FILES:
            schemas.append({"class_name": base[:-5], "tier": tier,
                            "class_version": None, "maturity_level": None,
                            "superclasses": [], "path": f"schemas/V_eta/{tier}/{base}",
                            "is_meta": True, "disposition": "persist"})
            continue
        dc = d["document_class"]
        disp, track = _disposition(dc["class_name"])
        entry = {"class_name": dc["class_name"], "tier": tier,
                 "class_version": dc["class_version"],
                 "maturity_level": dc["maturity_level"],
                 # flatten to bare class-name strings (matching V_zeta and earlier
                 # index.json); the web viewer's buildTree keys the superclass map
                 # on these strings, so objects break nesting.
                 "superclasses": [sc["class_name"] for sc in dc["superclasses"]],
                 "path": f"schemas/V_eta/{tier}/{base}", "disposition": disp}
        if track:
            entry["disposition_note"] = track
        schemas.append(entry)
schemas.sort(key=lambda e: (0 if e.get("is_meta") else 1, e["class_name"]))
idx["schemas"] = schemas
with open(os.path.join(VETA, "index.json"), "w") as f:
    json.dump(idx, f, indent=4)
    f.write("\n")

print(f"V_eta built: {len(schemas)} schemas across {TIERS}")
