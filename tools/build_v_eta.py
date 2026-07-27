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
    # ⑥/⑦ chunk (e): `element` is retired (subjects replaced elements), so the
    # epoch document's name is stale. It is an epoch of a data ACQUISITION. The
    # rename loop propagates this across class_name + superclasses + must_refer.
    "element_epoch": "acquisition_epoch",
    # entity rename for openMINDS alignment: our grant entity is openMINDS `Funding`
    # (awardTitle + awardNumber + funder). Propagates class_name + superclasses +
    # must_refer across any inherited references; the fresh V_eta defs already say
    # `funding`, so this only catches stragglers.
    "award": "funding",
}
for d in DIMS:
    RENAME[f"scalar_{d}"] = d                       # shape mixin
    RENAME[f"scalar_{d}_observation"] = f"{d}_observation"

# classes deleted outright; when they appear as a superclass, replace per SUPER_SUB
DELETE = {"scalar_observation", "scalar_manipulation", "annotation", "group_assignment",
          "derivation", "placement", "stimulus_manipulation", "stimulus_approach",
          "oneepoch", "epochclocktimes", "valid_interval", "session_extent",
          "mock",
          # 2.D opaque fold (slice A): generic_file dissolves into opaque_body
          # (uninterpreted bytes + a small format/filename descriptor). No class
          # references it (checked), so deletion is clean; DID-matlab
          # migrators_j.generic_file folds v1 docs. (image stays -- it is the
          # image_observation geometry mixin, part of the NDI-side sampled fold;
          # image_collection is a separate per-class call.)
          "generic_file",
          # 2.D encoding-in-name slice: timeseries_data_{binary,csv,edf} are EMPTY
          # subtypes of timeseries_data whose only content is the FORMAT encoded in
          # the class name. Per "encoding becomes a field", the format is already
          # carried by the dataseries_data ancestor's `storage.format` -- so the
          # subtypes are redundant and dissolve. They are forward-looking draft
          # classes with no v1 source (0 migrator refs, 0 corpus presence, nothing
          # subclasses them -- checked), so deletion is schema-only.
          "timeseries_data_binary", "timeseries_data_csv", "timeseries_data_edf",
          # 2.D slice C: the draft dataseries carrier family dissolves under
          # Option 1 -- its header (axes/channels/storage) is carried by
          # acquisition_epoch and its payload by sampled_body (content_hash
          # preserved onto sampled_body). Forward-looking draft classes with no v1
          # source (0 migrator refs, 0 corpus presence; nothing outside the family
          # references them -- checked), so deletion is schema-only. (zarr SURVIVES
          # as the ⊂ base storage-recipe descriptor -- load-bearing for directory's
          # zarr_implicit manifest; ephys_zarr/image_zarr are stable/corpus-risky
          # and dataseries_pyramid pairs with pyraview -> slice D.)
          "dataseries_data", "timeseries_data", "imageseries_data",
          # 2.D slice D (image_collection): a bag of image files. Nothing creates
          # it -- 0 references in NDI-matlab or DID-matlab, not a did_v1 source
          # class -- so like generic_file it dissolves schema-only, with the corpus
          # run as the presence probe. Intended fold: -> opaque_body (the image
          # bytes as an uninterpreted attachment). If the probe ever quarantines
          # (a historical corpus carries one), add a migrators_j split that mints an
          # image_observation of its element_id subject + an opaque_body. `image`
          # itself STAYS (it is image_observation's geometry mixin -- checked).
          "image_collection",
          # 2.D slice D orphans: ephys_zarr / image_zarr / dataseries_pyramid are
          # forward-looking zarr/pyramid subtypes with NO source -- 0 refs in NDI,
          # 0 migrators, no v1 doc definition -- so 0 corpus presence. Like
          # image_collection they dissolve schema-only (corpus run is the probe).
          # Intended fold if ever present: -> sampled_body (the sampled ephys/image
          # signal) with the acquisition header on acquisition_epoch and the zarr
          # recipe via the KEPT `zarr` descriptor. `pyraview` is NOT here -- it has
          # real presence (NDI writes it, migrators_j.pyraview) and is a genuine
          # observation-tier fold (with #9).
          "ephys_zarr", "image_zarr", "dataseries_pyramid",
          # Phase 1 source-class cleanup: these are dissolved by J migrators
          # (dataset_remote/dataset_session_info/session_in_a_dataset ->
          # directed_relations per ⑥-E; metadata_editor -> dataset + entities +
          # relations), so no V_eta doc is of these classes -- they linger only as
          # v1 SOURCE names. Each has a migrators_j.* dissolver (checked) and no
          # surviving class references it (checked), so deletion is clean; the
          # corpus run is the 0-presence probe. (openminds/openminds_stimulus/
          # openminds_element are NOT here -- they still lack migrators; measurement
          # is entangled with #9 -- both held.)
          "dataset_remote", "dataset_session_info", "session_in_a_dataset",
          "metadata_editor"}
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
# local_identifier is REQUIRED on subject -- schema-enforced (a subject must be
# nameable), not an ingest convention. This is legal because `entity` (the parent)
# declares no local_identifier, so subject is *adding* a required field, not
# overriding a parent-optional one (which DID placement forbids). The same field is
# declared OPTIONAL on the other entities below.
for _f in sub["fields"]:
    if _f["name"] == "local_identifier":
        _f["mustBeNonEmpty"] = True
        _f["documentation"] = (
            "Human-facing handle for this subject, unique within its dataset. "
            "REQUIRED on subjects; the same field is optional on every other "
            "entity (see local_identifier there).")
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


# --- conditions (D10 qualifiers): conditions the statement was taken under ---
# Renamed from `parameters` (2026-07) for clarity: it holds the EXPERIMENTAL
# conditions of each reading -- both the varied condition (its value is the per-reading
# array, i.e. the independent-variable axis) and the held-fixed conditions (length-1
# covariates); an independent variable is just the condition whose value varies. This
# is distinct from `subject_interaction.method_parameters` (the algorithm's config /
# calculator input_parameters -- HOW it was computed, not the conditions it was taken
# under). The unrelated `parameters` blocks on daqreader/syncrule/filter are separate
# fields and keep their name.
# A list of typed {variable, value}. Each condition names its `variable` and
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

CONDITIONS = field(
    "conditions", "structure",
    "D10 qualifiers: the experimental conditions a statement was taken under, as a "
    "list of typed {variable, value} entries. Each names its `variable` and carries "
    "exactly one nested data-type block (term / count / quantity). A condition whose "
    "value is a per-reading ARRAY is the independent-variable axis (e.g. a tuning "
    "curve's direction); a length-1 value is a held-fixed covariate -- same kind of "
    "thing, distinguished only by cardinality. Distinct from "
    "`subject_interaction.method_parameters` (the algorithm's config -- how it was "
    "computed). 'Exactly one populated' is an ingest validator (the closed "
    "meta-schema has no oneOf); the full per-dimension type set is a provisional "
    "extension (D10). Value cardinality: length 1 (a constant condition) or the "
    "measurement's value length (one per reading). Typed by data type via the D9 "
    "registry keyed on `variable`.",
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
          deps=[SUBJECT_ID], fields=[VARIABLE, CONDITIONS]))

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
METHOD_PARAMS = field(
    "method_parameters", "structure",
    "Optional configuration of a COMPUTED value's algorithm -- the calculator "
    "input_parameters that produced it (D-C analysis tier). Present only when "
    "`method` names an algorithm; free-form (the knob set varies per calculator). "
    "Retaining it keeps the computation reproducible from the observation packet "
    "(paper Fig. 3E). Lives on the packet-head observation, once per calculation.",
    non_empty=False, scalar=True, blank={}, default={})
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

# software_id + execution_environment: document-GENERATION provenance for a value a
# program produced (supersedes the v1 `app` mixin; Item-1 decision in
# V_eta_tenet_audit.md R1). The software is a citable FAIR ENTITY (T9, ≈ openMINDS
# SoftwareVersion) referenced by a typed edge (T7 -- the agent role, like instrument_id),
# NOT an inherited block: one `software` doc, many lightweight refs (dedup). Optional and
# available to EVERY interaction direction (calculation ~always; computed observation /
# software-delivered manipulation optionally) -- so it lives here on the shared parent,
# not baked into one direction. The per-RUN environment (the actual os/interpreter this
# run used -- provenance of THIS execution, distinct from the software's identity and from
# openMINDS SoftwareVersion.operatingSystem, which is the SUPPORTED os) rides beside it as
# an optional descriptor block.
SOFTWARE_ID = dep("software_id", "software",
                  "Optional: the software that produced this value, modeled as a "
                  "`software` entity (name + version + citation id). The agent for a "
                  "computation; distinct from instrument_id (a measuring device) and "
                  "from derived_from (the input data). Empty for hand/DAQ measurements; "
                  "populated on calculations, optional on computed observations. "
                  "Supersedes the v1 `app` block.", non_empty=False)
EXEC_ENV = field(
    "execution_environment", "structure",
    "Optional per-run provenance of a software-produced value: the actual OS + "
    "interpreter the producing run used. This is provenance of THIS execution, distinct "
    "from the software's identity (the `software` entity) and from the SUPPORTED os "
    "(openMINDS SoftwareVersion.operatingSystem). Empty for hand/DAQ measurements.",
    non_empty=False, scalar=True, blank={}, default={},
    sub_fields=[
        subfield("os", "char", "Operating system the run executed on.", non_empty=False),
        subfield("os_version", "char", "Operating-system version.", non_empty=False),
        subfield("interpreter", "char",
                 "Language/interpreter the run used (e.g. MATLAB, Python).",
                 non_empty=False),
        subfield("interpreter_version", "char", "Interpreter version.", non_empty=False),
    ])

si = doc("subject_interaction", ["subject_statement"], abstract=True, version="3.0.0",
         deps=[TIME_REF_REQ, INSTRUMENT, SOFTWARE_ID],
         fields=[METHOD, METHOD_PARAMS, SAMPLE_TIME, EXEC_ENV])
write("stable", "subject_interaction", si)

# derived_from: computation provenance on OBSERVATIONS (D-C analysis tier). A
# COMPUTED observation -- one whose subject_interaction.method names the algorithm
# -- records the input statement(s) it was derived from (e.g. an OSI
# score_observation derived_from the raw tuning-curve frequency_observation). This
# is the provenance INVERSE of directed_relation: directed_relation is
# entity->entity (child/parent), derived_from is statement->statement. It is typed
# to a `subject_statement` leaf and MUST NOT point at an `entity`. It lives on
# subject_observation only -- a manipulation is imposed and an assertion is
# declared, neither is "derived". Optional and repeatable (_#): a single fit has
# one input, an aggregate calc (contrast_sensitivity) has many. Reference typing
# is declarative (did2.validate.references is existence-only); a type-enforcing
# check would be a separate validator.
DERIVED_FROM = dep(
    "derived_from_#", "subject_statement",
    "The subject_statement leaf(s) this value was COMPUTED from (its inputs). "
    "Present only on computed observations, whose subject_interaction.method names "
    "the algorithm. Typed to a statement leaf -- never an entity; the provenance "
    "inverse of directed_relation's entity->entity child/parent.",
    non_empty=False)
so = load(os.path.join(VETA, "stable", "subject_observation.json"))
so.setdefault("depends_on", []).append(DERIVED_FROM)
write("stable", "subject_observation", so)

# subject_calculation: the COMPUTED statement direction (Lepsky et al., the
# calculator-motif paper). A calculator produces ONE output document type; in V_eta
# that output is a subject_calculation LEAF pairing this direction with a result
# composite data_type -- exactly as visual_grating_manipulation pairs
# subject_manipulation with visual_grating. It inherits from subject_interaction the
# algorithm identity (`method`), the calculator input_parameters
# (`method_parameters`, Fig 3E), `sample_time`, the required `time_reference`, and the
# generating-software provenance (`software_id` -> `software` entity + the optional
# `execution_environment`, Item-1 decision -- supersedes the old `app` superclass; paper
# Fig 4 / FAIR §4.2). It carries `derived_from_#` -- the input statement(s) the
# calculation consumed (what the paper stores in the output document's depends_on).
# Distinct direction, NOT an observation: the measured stimulus_response is the
# observation, a tuning curve / fit is a calculation (paper §3.2-3.3). Experimental
# conditions (the tuning axis + covariates) ride on the inherited subject_statement.conditions.
write("stable", "subject_calculation",
      doc("subject_calculation", ["subject_interaction"], abstract=True,
          deps=[DERIVED_FROM]))


# ---------- 4. subject_assertion genus + leaves ----------

# genus: abstract, isa subject_statement, value on leaves. An assertion is a
# TIMELESS fact, so it declares NO time_reference at all -- timelessness is a schema
# guarantee, not a convention. (A claim that needs a date IS a date_assertion, whose
# date is its value; the required time anchor lives on subject_interaction instead.)
write("stable", "subject_assertion",
      doc("subject_assertion", ["subject_statement"], abstract=True, version="3.0.0",
          deps=[], fields=[]))

# term_assertion: one bound ontology term (species, sex, strain, region, kind)
TERM_VALUE = field(
    "value", "ontology_term",
    "The asserted concept as a bound term (species, sex, strain, instrument "
    "type). The admissible vocabulary is a variable-keyed binding (D9).",
    non_empty=True, scalar=True,
    constraints={"binding": {"keyed_by": "variable", "expansion": "descendants",
                             "node_kind": "class", "strength": "required"}})
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
                    "entity — subject part, dataset, funding, …)."),
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
# publication, funding, dataset. They carry a cross-reference `global_identifier`
# and are the *things* other docs point at. Non-subject entities use TYPED
# identity fields (not statements): their attributes are intrinsic identity, not
# provenanced measurements, and names/titles/DOIs are not ontology terms, so
# term_assertion does not fit. Everything relational (authorship, funding,
# citation, affiliation) is a `directed_relation` at the entity layer (generalized
# above): dataset -has_author-> person (+ sequence), dataset -funded_by-> funding,
# funding -issued_by-> organization, person -affiliated_with-> organization,
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

# The human-facing local handle. Declared OPTIONAL on each entity below and
# REQUIRED on subject (above). It is NOT on `entity` itself: a parent-optional +
# child-required override is forbidden by DID placement, and requiredness is
# instead expressed by WHERE it is declared (subject: required; others: optional) --
# the same pattern the timing model uses for time_reference. Distinct from an
# entity's domain name/title (person name, dataset short_name, …): this is the
# stable cross-reference key within a dataset.
LOCAL_ID_OPT = field(
    "local_identifier", "char",
    "Optional human-facing handle for this entity, used to cross-reference it "
    "within its dataset (distinct from any display name/title). Required on "
    "subject; optional here.", non_empty=False)

# openMINDS Person: givenName/familyName/alternateName/contactInformation(email) ->
# fields; digitalIdentifier(ORCID) -> entity.global_identifier{scheme='ORCID'};
# affiliation -> directed_relation -> organization (affiliated_with). Nothing dropped.
write("stable", "person", doc("person", ["entity"], fields=[
    field("given_name", "char", "Given (personal) name; may include middle "
          "names/initials (given/family per the international convention). "
          "(openMINDS Person.givenName.)"),
    field("family_name", "char", "Family (sur)name. (openMINDS Person.familyName.)"),
    field("alternate_name", "string", "Alternate name(s) / aliases for the person "
          "(openMINDS Person.alternateName); repeatable.",
          non_empty=False, scalar=False),
    field("email", "char", "Contact email; meaningful when acting as a contact. "
          "(openMINDS Person.contactInformation -> ContactInformation.email.)",
          non_empty=False), LOCAL_ID_OPT]))
write("stable", "organization", doc("organization", ["entity"], fields=[
    field("full_name", "char", "Organization full name (funder or affiliation); "
          "ROR via global_identifier. Location is not stored — it lives in the ROR "
          "record. (openMINDS Organization.fullName.)"),
    field("short_name", "char", "Organization short name / acronym (e.g. 'NIH'); "
          "openMINDS Organization.shortName.", non_empty=False),
    LOCAL_ID_OPT]))
write("stable", "publication", doc("publication", ["entity"], fields=[
    field("title", "char", "Publication title."),
    field("date", "char", "Publication date/year.", non_empty=False),
    field("authors", "char", "Author citation string — external, NOT decomposed "
          "into person entities (cited papers' authors stay coarse).",
          non_empty=False), LOCAL_ID_OPT]))
write("stable", "funding", doc("funding", ["entity"], fields=[
    field("title", "char", "Award/grant title (openMINDS Funding.awardTitle); the "
          "award number / grant DOI rides on global_identifier{scheme='AwardNumber'} "
          "(openMINDS Funding.awardNumber). Its funder is a `directed_relation` -> "
          "organization (openMINDS Funding.funder).",
          non_empty=False), LOCAL_ID_OPT]))
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
          "global_identifier (scheme='URL').", non_empty=False), LOCAL_ID_OPT]))
# software IS an entity (Item-1 decision, V_eta_tenet_audit.md R1): a citable FAIR
# program (≈ openMINDS SoftwareVersion), the AGENT that produced a computed value.
# Referenced by a typed `software_id` edge on subject_interaction (T7), not embedded as
# the v1 `app` mixin -- one doc, many refs (dedup). Identity fields are TYPED (name /
# version), not statements (they are intrinsic identity, not provenanced measurements).
# The citation id (RRID | SWHID | DOI) and the homepage/repository URL ride on the
# inherited `global_identifier` (scheme='RRID'|'SWHID'|'DOI'|'URL'), same as the other
# entities. Fuller openMINDS parity (developer -> person, funding -> funding, supported
# operatingSystem/programmingLanguage as bound terms) is the openMINDS-crosswalk step.
# The per-RUN environment is NOT here -- it is provenance of the producing act, on
# subject_interaction.execution_environment.
write("stable", "software", doc("software", ["entity"], fields=[
    field("name", "char", "Software name/title (openMINDS SoftwareVersion.fullName / "
          "shortName)."),
    field("version", "char", "Version identifier (openMINDS "
          "SoftwareVersion.versionIdentifier); the citation id and homepage/repository "
          "URL ride on global_identifier.", non_empty=False),
    LOCAL_ID_OPT]))
# dataset IS the entity (target of the metadata_editor decomposition — a follow-up
# migrator reshapes the Soph metadata_structure blob into this + person/funding/
# publication entities + relations; metadata_editor is kept as the source until then).
#
# openMINDS parity (Dataset + DatasetVersion collapsed into this one entity). Every
# openMINDS DatasetVersion property has a home so the object round-trips with no loss:
#   * SCALAR properties -> optional fields below, named inline (snake_case) with the
#     openMINDS property noted on each.
#   * REFERENCE properties are NOT fields — references are relations here:
#       author / custodian / otherContribution -> directed_relation -> person|organization
#           (the openMINDS contributor ROLE rides on the relation type: author vs custodian)
#       funding                                -> directed_relation -> funding
#       relatedPublication                     -> directed_relation -> publication
#       fullDocumentation / homepage / repository / protocol / supportChannel(url)
#                                              -> directed_relation -> web_resource
#       studiedSpecimen                        -> directed_relation -> subject
#       inputData                              -> directed_relation -> dataset|web_resource
#       isNewVersionOf / isAlternativeVersionOf -> directed_relation -> dataset
#       digitalIdentifier (DOI)                -> entity.global_identifier{scheme='DOI'}
#       type                                   -> implied by class (not stored per-instance)
write("stable", "dataset", doc("dataset", ["entity"], fields=[
    field("full_name", "char", "Full dataset name (openMINDS DatasetVersion.fullName)."),
    field("short_name", "char", "Short dataset name / acronym "
          "(openMINDS DatasetVersion.shortName).", non_empty=False),
    field("version", "char", "Version identifier "
          "(openMINDS DatasetVersion.versionIdentifier).", non_empty=False),
    field("version_innovation", "char", "What changed relative to the previous version "
          "-- the changelog note (openMINDS DatasetVersion.versionInnovation).",
          non_empty=False),
    field("description", "char", "Dataset description / abstract "
          "(openMINDS DatasetVersion.description).", non_empty=False),
    field("how_to_cite", "char", "Preferred citation string for this dataset version "
          "(openMINDS DatasetVersion.howToCite).", non_empty=False),
    field("keyword", "string", "Free-text keywords/tags describing the dataset "
          "(openMINDS DatasetVersion.keyword); repeatable.",
          non_empty=False, scalar=False),
    field("license", "char", "License (openMINDS DatasetVersion.license, a SPDX "
          "license identifier).", non_empty=False),
    # Controlled-term fields: ontology_term (node = openMINDS instance IRI, name =
    # label) with an inline `binding` naming the openMINDS term set directly (NOT
    # keyed by a sibling `variable` the way statement leaves are). See
    # V_eta_openminds_controlled_terms_binding_plan.md; cataloged in
    # binding_registry_meta.entity_field_bindings. CLOSED sets -> strength required;
    # the open/growing ExperimentalApproach -> preferred.
    field("accessibility", "ontology_term", "Access level of the data -- e.g. free "
          "access / controlled access / under embargo (openMINDS "
          "DatasetVersion.accessibility, controlled term ProductAccessibility).",
          non_empty=False, constraints={"binding": {
              "vocabulary": "openMINDS", "term_set": "ProductAccessibility",
              "strength": "required"}}),
    field("ethics_assessment", "ontology_term", "Whether/how the work required ethics "
          "review -- e.g. not required / EU compliant / EU non-compliant (openMINDS "
          "DatasetVersion.ethicsAssessment, controlled term EthicsAssessment).",
          non_empty=False, constraints={"binding": {
              "vocabulary": "openMINDS", "term_set": "EthicsAssessment",
              "strength": "required"}}),
    field("experimental_approach", "ontology_term", "Scientific method/approach used "
          "to acquire the data -- e.g. electrophysiology, behavior (openMINDS "
          "DatasetVersion.experimentalApproach, controlled term ExperimentalApproach); "
          "repeatable, open/growing set.", non_empty=False, scalar=False,
          constraints={"binding": {
              "vocabulary": "openMINDS", "term_set": "ExperimentalApproach",
              "strength": "preferred"}}),
    field("support_channel", "string", "Where to get support for this dataset -- an email "
          "address or discussion channel (openMINDS DatasetVersion.supportChannel); "
          "a support URL is instead a directed_relation -> web_resource. Repeatable.",
          non_empty=False, scalar=False),
    field("release_date", "char", "Release date "
          "(openMINDS DatasetVersion.releaseDate).", non_empty=False),
    field("copyright_year", "char", "Copyright year (openMINDS "
          "DatasetVersion.copyright -> Copyright.year); the holder is a "
          "directed_relation -> organization|person (copyright_holder).",
          non_empty=False),
    LOCAL_ID_OPT]))

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
if not any(f["name"] == "local_identifier" for f in sess.get("fields", [])):
    sess.setdefault("fields", []).append(LOCAL_ID_OPT)
write("stable", "session", sess)

# openMINDS import provenance. Records, per import, the exact openMINDS release and
# crosswalk version the metadata was decomposed under -- the SINGLE source of truth
# that controlled_vocabularies.openMINDS.version (binding registry) points at. A
# dataset's controlled-term field values (accessibility / ethics_assessment /
# experimental_approach) resolve their term-set IRIs against THIS release, and the
# round-trip CI test asserts consistency. One document per import event, tied to the
# dataset it populated (declarative dep). Not itself an entity -- it is provenance
# metadata about an import, not a referenceable identity.
write("draft", "openminds_import",
      doc("openminds_import", ["base"], maturity="draft",
          deps=[dep("dataset", "dataset",
                    "The dataset entity this import populated.", non_empty=False)],
          fields=[
              field("openminds_version", "char",
                    "The openMINDS release the source metadata was imported from "
                    "(e.g. 'v4'). Pins the controlled-term instance libraries the "
                    "dataset's accessibility / ethics_assessment / experimental_approach "
                    "values resolve against."),
              field("crosswalk_version", "char",
                    "Version of the openMINDS<->NDI crosswalk "
                    "(V_eta_openminds_crosswalk.json) used for the decomposition."),
              field("source_iri", "char",
                    "The openMINDS object/dataset IRI the import came from, where one "
                    "exists.", non_empty=False),
          ]))

# ---------- instrument: RETIRE (boundary re-audit) -------------------------------------
# `instrument` is a V_epsilon "review/infra" stub (base-only, no fields/deps) -- NOT a
# did_v1 source (absent from the coverage ledger), no migrator emits it. T7 already models
# a device as a `subject` + an `instrument_id` edge on `subject_interaction`, so the class
# carries nothing and strands nothing. Delete the copytree'd draft stub.
_instrument_p = os.path.join(VETA, "draft", "instrument.json")
if os.path.exists(_instrument_p):
    os.remove(_instrument_p)


# ---------- new-on-main NDI app outputs (D-C analysis tier, decomposition deferred) --
# ensemble / kilosort_clusters / kiasort_clusters were added to NDI-matlab main AFTER
# V_eta forked from V_zeta, so they had no V_eta home (coverage-ledger GAPS). They are
# D-C analysis-tier app outputs (spike sorting + neuron grouping).
#   kilosort_clusters / kiasort_clusters -- DECOMPOSED (#9/D-C): migrators_j fold each
#     sorter RUN into a count_observation (id-preserved handle) + opaque_body (the
#     external output directory) + session anchor. The schema below is RETAINED (not
#     yet phase-8-deleted) as a safety net -- an unmigratable edge-case doc quarantines
#     (non-gating) against it rather than erroring on an unknown class.
#   ensemble -- still PASSTHROUGH-retained (in_progress): its grain (a neuron grouping)
#     is a separate decision.
# `element_id` -> subject and `element_epoch_id` -> acquisition_epoch (elements/epochs
# were retargeted in strict J).
for _name, _dir in (("kilosort_clusters", "kilosort_directory"),
                    ("kiasort_clusters", "kiasort_directory")):
    write("stable", _name,
          doc(_name, ["base", "app"],
              deps=[dep("element_id", "subject",
                        "The recording element (a subject in V_eta) these sorted "
                        "clusters were computed from.")],
              fields=[
                  field(_dir, "char",
                        "Path to the sorter output directory (session-relative)."),
                  field("curated_output_md5_checksum", "char",
                        "MD5 checksum of the curated sorter output.", non_empty=False),
              ]))

write("stable", "ensemble",
      doc("ensemble", ["base", "epochid", "app"],
          deps=[dep("element_id", "subject",
                    "The recording element (a subject in V_eta) the ensemble was "
                    "computed from."),
                dep("element_epoch_id", "acquisition_epoch",
                    "The epoch over which the ensemble was defined.", non_empty=False)],
          fields=[
              field("ensemble_name", "char", "Name of the neuron ensemble."),
              field("value_type", "char",
                    "Type of the ensemble's value/activity representation.",
                    non_empty=False),
              field("value_description", "char",
                    "Free-text description of the ensemble value.", non_empty=False),
              field("num_neurons", "integer", "Number of neurons in the ensemble."),
              field("clocktype", "char",
                    "Clock type for the ensemble's epoch times.", non_empty=False),
          ]))


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

# visual_grating: a presented visual GRATING (periodic pattern; static or
# drifting) as a STRUCTURED multi-parameter value. Unlike a single-quantity leaf, a grating
# is inherently multi-parameter (orientation + spatial/temporal frequency + contrast
# + size), so it is its own data_type composite. A `stimulus_presentation` becomes a
# body-backed `visual_grating_manipulation` on the animal (the second pass resolves
# the animal; the time-varying stimulus rides in a sampled_body via storage_mode:body,
# the fixed parameters inline). NDI/vhlab source param names noted in ().
GRATING_SUBS = [
    subfield("angle", "double", "Orientation/direction of the grating, degrees "
             "(NDI 'angle')."),
    subfield("spatial_frequency", "double", "Spatial frequency, cycles/degree "
             "(NDI 'sFrequency')."),
    subfield("temporal_frequency", "double", "Temporal (drift) frequency, Hz "
             "(NDI 'tFrequency')."),
    subfield("contrast", "double", "Michelson contrast, 0-1 (NDI 'contrast')."),
    subfield("size", "double", "Stimulus size / aperture, degrees of visual angle "
             "(NDI 'size')."),
    subfield("position", "structure",
             "Screen position of the stimulus centre, degrees.", sub_fields=[
                 subfield("x", "double", "Horizontal position, degrees."),
                 subfield("y", "double", "Vertical position, degrees.")]),
    subfield("duration", "double", "Presentation duration, seconds."),
    subfield("is_blank", "boolean",
             "True for a control/blank (no-stimulus) trial (NDI 'isblank')."),
]
write("stable", "visual_grating",
      doc("visual_grating", ["base"], abstract=True, fields=[field(
          "value", "structure",
          "A presented visual grating (static or drifting) and its "
          "presentation parameters.", non_empty=True, blank={}, sub_fields=GRATING_SUBS)]))
# ---------- subject_calculation family (VERTICAL SLICE: oridir) ----------
# Reframe the tuning "result" classes into data_type COMPOSITES + subject_calculation
# LEAFS, exactly like visual_grating -> visual_grating_manipulation. FIRST SLICE:
# orientation_direction_tuning (the paper's Fig 4 exemplar). The result class already
# carries the structured output (properties / tuning_curve / significance / vector /
# fit) as a base-bag; reparent it to `data_type` (making it the composite) and add
# the `<composite>_calculation` leaf. The old oridirtuning_calc CLASS is retained for
# now (its docs migrate 1->1 to the leaf; retire/phase-8-delete is a follow-up).
# The tuning "result" classes each reparent from a base-bag to a `data_type`
# COMPOSITE (abstract, result blocks kept) + gain a `<composite>_calculation` leaf.
# Safe: each is consumed by a migrator, never instantiated concretely.
for _tune in ("orientation_direction_tuning", "contrast_tuning",
              "spatial_frequency_tuning", "temporal_frequency_tuning",
              "speed_tuning"):
    _t = load(os.path.join(VETA, "stable", _tune + ".json"))
    _t["document_class"]["superclasses"] = [{"class_name": "data_type"}]
    _t["document_class"]["abstract"] = True
    write("stable", _tune, _t)
    write("stable", _tune + "_calculation",
          doc(_tune + "_calculation", ["subject_calculation", _tune]))

# tuning_curve: the ndi.calc.tuningcurve output (tuningcurve_calc) -- the raw curve
# every fit calc searches for. Reparent stimulus_tuningcurve into an ABSTRACT
# `data_type` composite (it becomes a superclass; the concrete migrated docs are the
# leaf) and add the stimulus_tuningcurve_calculation leaf. The MIGRATOR is single-doc
# (migrators_j.tuningcurve_calc + migrators_j.stimulus_tuningcurve): an earlier note
# claimed tuningcurve_calc carried no subject, but a real doc IS-A stimulus_tuningcurve
# and so inherits a POPULATED element_id (the writer sets it from the consumed
# stimulus_response_scalar, ndi.app.stimulus.tuning_response.tuning_curve line 499), so
# element_id -> subject_id, id-preserved, exactly like the other vision calculators. Both
# the calculator-framework doc (tuningcurve_calc) and the raw app curve
# (stimulus_tuningcurve) fold to the same leaf so downstream stimulus_tuningcurve_id refs
# resolve to either.
_st = load(os.path.join(VETA, "stable", "stimulus_tuningcurve.json"))
_st["document_class"]["superclasses"] = [{"class_name": "data_type"}]
_st["document_class"]["abstract"] = True
_st["depends_on"] = []
write("stable", "stimulus_tuningcurve", _st)
write("stable", "stimulus_tuningcurve_calculation",
      doc("stimulus_tuningcurve_calculation",
          ["subject_calculation", "stimulus_tuningcurve"]))

# contrast_sensitivity: the ndi.calc.vis.contrast_sensitivity output
# (contrast_sensitivity_calc) is a FLAT bag of sensitivity/gain/c50/p-value matrices
# with NO result-composite superclass -- so AUTHOR a `contrast_sensitivity` data_type
# composite from the calc's own result fields (input_parameters is inherited from
# `calculator`, not one of them, so it is naturally excluded), and add the leaf.
# Unlike tuningcurve_calc, contrast_sensitivity_calc HAS element_id -> it folds
# single-doc (migrators_j.contrast_sensitivity_calc).
_cs_src = load(os.path.join(VETA, "stable", "contrast_sensitivity_calc.json"))
write("stable", "contrast_sensitivity",
      doc("contrast_sensitivity", ["data_type"], abstract=True,
          fields=_cs_src.get("fields", [])))
write("stable", "contrast_sensitivity_calculation",
      doc("contrast_sensitivity_calculation",
          ["subject_calculation", "contrast_sensitivity"]))

write("stable", "visual_grating_manipulation",
      doc("visual_grating_manipulation",
          ["subject_manipulation", "visual_grating"]))
write("stable", "term_manipulation",
      doc("term_manipulation", ["subject_manipulation"], fields=[field(
          "value", "ontology_term",
          "The imposed act/agent as a bound term — a procedure (craniotomy), a "
          "regime (dark rearing), or a transferred material. Payload-free acts "
          "live here; there is NO generic escape hatch (D8).", non_empty=True,
          constraints={"binding": {"keyed_by": "variable", "expansion": "descendants",
                                   "node_kind": "class", "strength": "required",
                                   "source": "ontology"}})]))


# ---------- 10c. de-encode daqreader subtype-in-name classes (chunk c) ----------
# `daqreader_ndr` encodes a reader subtype in the CLASS NAME. That subtype is
# already discriminated by `ndi_daqreader_class`, so the class dissolves: its
# distinguishing fields de-encode onto the generic `daqreader` as OPTIONAL fields
# (only populated for the readers that need them). Nothing references it (checked);
# DID-matlab migrators_j.daqreader_ndr folds existing v1 docs onto daqreader.
_drn = load(os.path.join(VETA, "stable", "daqreader_ndr.json"))
_drn_f = {f["name"]: f for f in _drn["fields"]}
_dr = load(os.path.join(VETA, "stable", "daqreader.json"))
_dr["document_class"]["class_version"] = "2.0.0"
# ndr_reader_string -> reader_string (drop the subtype prefix), now optional;
# carry file_extension; drop ndi_daqreader_ndr_class (redundant with the parent's
# ndi_daqreader_class discriminator).
_rs = _drn_f["ndr_reader_string"]
_rs["name"] = "reader_string"
_rs["mustBeNonEmpty"] = False
_rs["documentation"] = ("Reader/file-type string (e.g. 'intan', 'SpikeGadgets') "
    "for a reader that needs one; formerly daqreader_ndr.ndr_reader_string. "
    "Optional -- the concrete reader is discriminated by ndi_daqreader_class.")
_dr["fields"] += [_rs, _drn_f["file_extension"]]
write("stable", "daqreader", _dr)
os.remove(os.path.join(VETA, "stable", "daqreader_ndr.json"))


# ---------- 10c'. de-encode the epochdata_ingested subtype pair (chunks b + c) ----
# The two epochdata_ingested subtypes are DEVICE-LAYER ingested caches (a daqreader's
# verbatim snapshot of an epoch's bytes, keyed by {daqreader, epoch}). They carry NO
# subject -- one raw cache feeds many downstream ROI/channel elements, and the
# subject enters one layer down on the observation/element (Option A: caches stay ⑦
# infra, NOT folded into sampled_body, which would force a subject_statement the
# device layer does not have). Two tidies:
#
#  (c) `daqreader_mfdaq_epochdata_ingested` encodes the reader subtype (`mfdaq`) in
#      its CLASS NAME; its only distinguishing content is a `parameters` block. The
#      class dissolves onto the generic `daqreader_epochdata_ingested` (parameters
#      becomes an OPTIONAL field, empty for readers that do not slice by segment).
#  (b) both subtypes redundantly re-mix `epochid` as a SUPERCLASS on top of
#      `daqreader_epochdata_ingested`, which already links the epoch via its required
#      `epochid` DEP (-> element_epoch, where the epoch name lives). The inline
#      epochid block duplicates that name, so the mixin is dropped (dep-only): one
#      home for the epoch link. daqreader_id + epochid deps carry all identity.
#
# DID-matlab migrators_j.daqreader_mfdaq_epochdata_ingested folds v1 mfdaq docs onto
# daqreader_epochdata_ingested; migrators_i.image_stack mints the image cache without
# the epochid mixin. Both cannot regress the corpus: a v1 subtype doc lacking the
# inherited required epochid dep already quarantines before this change.
_dri = load(os.path.join(VETA, "stable", "daqreader_epochdata_ingested.json"))
_drm = load(os.path.join(VETA, "stable", "daqreader_mfdaq_epochdata_ingested.json"))
_drm_f = {f["name"]: f for f in _drm["fields"]}
_params = _drm_f["parameters"]
_params["documentation"] = (
    "Reader-specific parameters captured when the epoch was ingested. Optional --"
    " empty for readers that do not slice the source recording. The sub-fields seen"
    " in the v1 corpora are the MFDAQ reader's per-segment sample-count cutoffs;"
    " formerly the standalone daqreader_mfdaq_epochdata_ingested class.")
_dri["document_class"]["class_version"] = "2.0.0"
_dri["fields"].append(_params)
write("stable", "daqreader_epochdata_ingested", _dri)
os.remove(os.path.join(VETA, "stable", "daqreader_mfdaq_epochdata_ingested.json"))

# dep-only: strip the redundant `epochid` superclass mixin from the image cache
# (its epoch identity is carried by the inherited required `epochid` dep).
_dimg = load(os.path.join(VETA, "stable", "daqreader_image_epochdata_ingested.json"))
_dimg["document_class"]["superclasses"] = [
    s for s in _dimg["document_class"]["superclasses"]
    if s.get("class_name") != "epochid"]
_dimg["document_class"]["class_version"] = "2.0.0"
write("stable", "daqreader_image_epochdata_ingested", _dimg)


# ---------- 11. storage_mode + data_body (sampled_/opaque_) ----------

ss = load(os.path.join(VETA, "stable", "subject_statement.json"))
ss["fields"].append(field(
    "storage_mode", "char",
    "How the value is supplied: inline | reference | body. Machine-set at ingest "
    "by type and size (§8); assertions are always inline.",
    non_empty=False, blank="inline", default="inline",
    constraints={"enum": ["inline", "reference", "body"]}))
write("stable", "subject_statement", ss)

# `statement` is declared by the CHILDREN, not the abstract parent: a sampled_body
# is always the value stream of a statement (REQUIRED), but an opaque_body may be a
# statement's opaque value OR a standalone attached file (OPTIONAL). Placing it per
# child (parent neutral) expresses that without a forbidden parent-optional /
# child-required override -- the same pattern used for local_identifier / time_reference.
STATEMENT_REQ = dep("statement", "subject_statement",
                    "The one statement this body belongs to (reverse pointer); a "
                    "stream appends more bodies without rewriting the anchor.")
STATEMENT_OPT = dep("statement", "subject_statement",
                    "The statement this body is the opaque value of, if any; a "
                    "free-standing attachment leaves it empty.", non_empty=False)
BODY_FILE = [{"name": "body_data", "documentation": "The byte payload (>=1 file)."}]
data_body = doc("data_body", ["base"], abstract=True, maturity="draft")
data_body["file"] = BODY_FILE
write("draft", "data_body", data_body)

sampled = doc("sampled_body", ["data_body"], maturity="draft", deps=[STATEMENT_REQ], fields=[
    field("datum", "structure", "The per-sample value type (kind/dtype/unit/shape).",
          blank={}, sub_fields=[
              subfield("kind", "char", "scalar | array | record.", non_empty=True,
                       blank="scalar",
                       constraints={"enum": ["scalar", "array", "record"]}),
              subfield("dtype", "char", "Numeric dtype (float64, int16, …)."),
              subfield("unit", "char", "The per-sample value unit."),
              subfield("shape", "matrix", "array only: intra-datum dims.")]),
    field("sample_time", "structure",
          "The body-local timeline (D1 — the single home for a body-backed value). "
          "Regular grid (regular=true: t0 + k*dt, n samples) OR enumerated "
          "(regular=false: explicit per-sample times in `offsets`) -- mirroring the "
          "spine sample_time's grid/enumerated split, so an irregular series (e.g. a "
          "stimulus presentation's trial onsets) states its times as an array.",
          blank={}, sub_fields=[
              subfield("regular", "boolean", "Regular grid vs enumerated.",
                       blank=True),
              subfield("t0", "duration", "Local start offset from the anchor."),
              subfield("dt", "duration", "regular: sample spacing."),
              subfield("n", "integer", "Sample count."),
              subfield("offsets", "matrix",
                       "enumerated (regular=false): the explicit per-sample times "
                       "from the anchor -- the array of sample times (e.g. trial "
                       "onsets).")]),
    field("summary", "structure", "The searchable value + time rollup.",
          blank={}, sub_fields=[
              subfield("value", "structure", "Per-type value rollup.", blank={}),
              subfield("time", "structure", "min/max/n over sample_time.",
                       blank={})]),
    # Optional NON-time index axes for a multi-dimensional body (e.g. a derived
    # tuning curve over [contrast x orientation]). The TIME axis is sample_time;
    # this describes the OTHER dims. Absent for plain scalar/time series and for
    # device data whose acquisition axes/channels live on acquisition_epoch --
    # keeping the body lean is the whole point of the no-daq case (a bare derived
    # signal needs none of the acquisition header). 2.D Option 1.
    field("axes", "structure",
          "Optional non-time index dimensions for a multi-dimensional body "
          "(the time axis is sample_time). Populated only for multi-dim derived "
          "data that has no acquisition_epoch to carry axes; empty otherwise.",
          non_empty=False, scalar=False, blank=[], sub_fields=[
              subfield("name", "char", "Axis name (e.g. 'contrast', 'orientation').",
                       non_empty=True),
              subfield("kind", "char",
                       "Axis kind (index | space_x | space_y | wavelength | ...)."),
              subfield("length", "integer", "Number of coordinates along this axis.",
                       scalar=True, blank=0),
              subfield("regularity", "char", "regular | irregular.",
                       constraints={"enum": ["regular", "irregular"]}),
              subfield("spacing", "double", "Coordinate spacing when regular.",
                       scalar=True, blank=0.0),
              subfield("unit", "char", "Unit of the axis coordinate.")]),
    # Preserved from the dissolved dataseries_data carrier (2.D slice C): a
    # content hash of the payload bytes, usable as a natural dedup / integrity
    # key. Optional -- absent when not computed.
    field("content_hash", "char",
          "Optional content hash of the payload bytes; a natural dedup / "
          "integrity key. Formerly dataseries_data.content_hash.",
          non_empty=False),
])
sampled["file"] = BODY_FILE
write("draft", "sampled_body", sampled)

opaque = doc("opaque_body", ["data_body"], maturity="draft", deps=[STATEMENT_OPT], fields=[
    field("format", "char",
          "Container / MIME format of the bytes (e.g. 'application/pdf', "
          "'image/tiff'). A descriptor only -- the payload is uninterpreted; a "
          "container format is otherwise derivable from the stored bytes.",
          non_empty=False),
    field("filename", "char", "Original filename of the payload, if any.",
          non_empty=False),
    field("description", "char", "Human description of the opaque payload.",
          non_empty=False),
])
opaque["file"] = BODY_FILE
write("draft", "opaque_body", opaque)

# image_observation: the body-backed data-type leaf the did_v1 `image_stack`
# (7,007 docs in JH) folds onto (§C.4). The pixel frames live in a
# sampled_body/opaque_body (storage_mode: body); the stable `image` mixin carries
# the inline geometry/format metadata (image_type/format/resolution). Draft: the
# broader imageseries/dataseries/timeseries_observation branch this begins to
# supersede is retired WITH the NDI-side ingest work (see the header note), not
# here -- so this addition is purely additive and does not touch that branch.
# image: reparent base -> an abstract data_type COMPOSITE (Item-2 decision, R6). `image`
# is image_observation's geometry/format descriptor -- the "image" data_type, exactly as
# visual_grating is for visual_grating_manipulation. It is NOT an entity: openMINDS has no
# Image type (an image is a File = DATA), so the raster is a sampled_body (T6), not a
# citable agent like `software`. Drop the redundant `image_file` (the pixels live in the
# sampled_body -- the image_stack migrator emits storage_mode:body + a sampled_body, and
# sets only the geometry block, never image_file) and the dead `element_id` dep (element
# retired, D2); keep the geometry/format fields. Graduates to persist ③ via the
# abstract-data_type rule.
_img = load(os.path.join(VETA, "stable", "image.json"))
_img["document_class"]["superclasses"] = [{"class_name": "data_type"}]
_img["document_class"]["abstract"] = True
_img["depends_on"] = []
_img["file"] = []
write("stable", "image", _img)

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
# Governance: `needs_ndi` marks a field whose value is an NDI-runtime class handle
# (e.g. ndi_daqreader_class = 'ndi.daq.reader.mfdaq') that DID cannot resolve or
# validate on its own -- the concrete class lives in NDI-matlab. An advisory boolean
# (optional, absent == false); downstream NDI tooling keys off it. Declared here
# because field_definition is additionalProperties:false.
meta["$defs"]["field_definition"]["properties"]["needs_ndi"] = {
    "type": "boolean",
    "description": "True when this field carries an NDI-runtime class handle that "
                   "DID cannot resolve on its own (governance marker; the concrete "
                   "class is defined in NDI-matlab).",
}
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
            # Controlled-vocabulary (openMINDS) binding: a directly-named term set
            # rather than an ontology subtree or a variable-keyed lookup. See
            # entity_field_bindings in binding_registry_meta.json.
            "vocabulary": {"type": "string"},
            "term_set": {"type": "string"},
            "vocabulary_version": {"type": "string"},
        },
    }
}
with open(os.path.join(VETA, "stable", "did_schema_meta.json"), "w") as f:
    json.dump(meta, f, indent=4)
    f.write("\n")


# ---------- 13. binding-registry meta-file + kind-variable set (D9) ----------

# ---------- D6 relation bindings ----------
# The admissible relation terms carried on `directed_relation.relation` /
# `undirected_relation.relation` (an ontology_term whose `name` is one of these).
# The schema field is free-form (validated as an ontology_term, not against this
# list), so this registry is the SINGLE enumerated source of truth for consumer
# tooling and the D6 curation.
#
#   relation      {node, name} NodeRef -- the same shape value bindings use for
#                 `variable`/`method`. `node` is the backing CURIE where a standard
#                 term exists (RO/BFO); "" = an open D6 curation slot, keyed on the
#                 name until a CURIE is assigned.
#   class         the carrier document class the term is minted as -- the fact that
#                 governs endpoint symmetry and which optional fields are meaningful:
#                   directed_relation   -> asymmetric (from --name--> to); may carry
#                                          `sequence` (see ordered) and `method`.
#                   undirected_relation -> symmetric member set (`member_types`).
#                 This pins term -> class (a `part_of` minted as undirected is an
#                 error the validator can catch). All current terms are directed.
#   child_types /
#   parent_types  the entity/data classes admissible at each endpoint of a directed
#                 edge (child --name--> parent). These name the same fields as the
#                 schema `directed_relation.child` / `.parent` deps, so the registry
#                 matches the document exactly. Abstract types (`entity`, `subject`)
#                 mean "any of that genus"; [] = unconstrained (open, pending D6).
#                 Undirected relations do NOT use these -- see `member_types`.
#   *_role        human gloss of each endpoint.
#   ordered       the directed_relation `sequence` field is semantically meaningful
#                 (e.g. author order). class alone does not imply this -- every
#                 directed edge *has* an optional sequence; ordered marks the ones
#                 where it carries meaning.
#   timed         the edge denotes an event that may carry a `method` / time anchor.
def _rel(name, node, child_role, parent_role, child_types, parent_types,
         *, cls="directed_relation", timed=False, ordered=False):
    # Endpoints are `child`/`parent` for a directed edge, matching the schema deps.
    # An undirected term (none yet) would instead carry `member_types` (symmetric),
    # mirroring undirected_relation's single `entities` dep -- see the notes.
    return {"relation": {"node": node, "name": name}, "class": cls,
            "child_role": child_role, "parent_role": parent_role,
            "child_types": child_types, "parent_types": parent_types,
            "timed": timed, "ordered": ordered}

RELATION_VOCABULARY = [
    # containment / structure
    _rel("part_of", "BFO:0000050", "the part", "the whole",
         ["subject", "session"], ["subject", "dataset"]),
    _rel("contained_in", "RO:0001018", "the contained", "the container",
         [], []),
    # is_group was removed from subject, so a group IS just a subject with members.
    _rel("member_of", "RO:0002350", "the member", "the group",
         ["subject"], ["subject"]),
    # provenance / creation (timed: the creation event may carry a time_reference)
    _rel("derived_from", "RO:0001000", "the derivative", "the source",
         [], [], timed=True),
    _rel("sample_of", "", "the sample", "the sampled source",
         ["subject"], ["subject"], timed=True),
    _rel("aliquot_of", "", "the aliquot", "the parent quantity",
         ["subject"], ["subject"], timed=True),
    _rel("passage_of", "", "the passage", "the parent culture",
         ["subject"], ["subject"], timed=True),
    # agent / instrument role (a probe/instrument is modeled as a subject)
    _rel("observes", "", "the instrument-subject", "the observed specimen",
         ["subject"], ["subject"]),
    # event
    _rel("encountered", "", "the encountering subject", "the encountered subject",
         ["subject"], ["subject"], timed=True),
    # spatial measurement: the distance between two loci was measured (the values
    # live on the distance element's observation; this names the endpoints). Both
    # endpoints are id-preserved subjects (animal, patch). See
    # V_eta_distance_metadata_plan.md.
    _rel("measured_distance_to", "", "the measured-from subject",
         "the reference subject", ["subject"], ["subject"], timed=True),
    # bibliographic (entity layer)
    _rel("has_author", "", "the dataset", "the author (person)",
         ["dataset"], ["person"], ordered=True),
    _rel("cites", "", "the citing dataset", "the cited publication",
         ["dataset"], ["publication"]),
    # funding (entity layer)
    _rel("funded_by", "", "the funded dataset", "the funding",
         ["dataset"], ["funding"]),
    _rel("issued_by", "", "the funding", "the issuing organization",
         ["funding"], ["organization"]),
    # affiliation (entity layer)
    _rel("affiliated_with", "", "the person", "the organization",
         ["person"], ["organization"]),
    # reference / storage (entity layer)
    _rel("documented_by", "", "the documented entity", "the web_resource",
         ["entity"], ["web_resource"]),
    _rel("stored_at", "", "the stored dataset", "the web_resource (remote copy)",
         ["dataset"], ["web_resource"]),
    _rel("hosted_by", "", "the web_resource", "the hosting organization",
         ["web_resource"], ["organization"]),
    # openMINDS DatasetVersion contributor / reference terms (crosswalk parity).
    # Contributor ROLE is the term: has_author vs has_custodian vs contributed_by
    # (openMINDS author / custodian / otherContribution). Endpoints accept person OR
    # organization where openMINDS does.
    _rel("has_custodian", "", "the dataset", "the custodian (person/org)",
         ["dataset"], ["person", "organization"]),
    _rel("contributed_by", "", "the dataset", "the contributor (person/org)",
         ["dataset"], ["person", "organization"]),
    _rel("copyright_holder", "", "the dataset", "the copyright holder (org/person)",
         ["dataset"], ["organization", "person"]),
    # version lineage / inputs (openMINDS isAlternativeVersionOf / inputData;
    # isNewVersionOf reuses derived_from).
    _rel("alternative_of", "", "the dataset version", "the alternative version",
         ["dataset"], ["dataset"]),
    _rel("input_data", "", "the derived dataset", "the input dataset/resource",
         ["dataset"], ["dataset", "web_resource"], timed=True),
    # typed reference edges to web_resources (openMINDS homepage / protocol), distinct
    # from the generic documented_by so the reference kind is not lost.
    _rel("has_homepage", "", "the entity", "the homepage (web_resource)",
         ["dataset", "organization"], ["web_resource"]),
    _rel("follows_protocol", "", "the dataset", "the protocol (web_resource)",
         ["dataset"], ["web_resource"]),
    # organization hierarchy (openMINDS Organization.hasParent), kept distinct from
    # the subject/session part_of rather than widening that term's endpoints.
    _rel("suborganization_of", "", "the child organization", "the parent organization",
         ["organization"], ["organization"]),
]

# ---------- subject_statement bindings ----------
# variable (+ method) -> the concrete subject_statement LEAF class that carries the
# statement. The leaf fixes the value type (no data_type); a term-valued leaf
# additionally pins the admissible term set. `subject_defining: true` marks the
# variables whose presence establishes a subject's kind (the D9 ingest invariant);
# these are a flagged SUBSET of the same list, not a separate registry -- a subject
# carries many variables, only these define what it is. Each subject_defining row is
# a term_assertion drawing from an ontology subtree.
def _sdef(name, ontology, root_node):
    return {"variable": {"node": "", "name": name}, "class": "term_assertion",
            "ontology": ontology, "root_node": root_node, "subject_defining": True}

SUBJECT_STATEMENT_BINDINGS = [
    _sdef("species", "NCBITaxon", "NCBITaxon:1"),
    _sdef("instrument type", "OBI", "OBI:0000968"),
    _sdef("cell type", "CL", "CL:0000000"),
    _sdef("material type", "CHEBI", "CHEBI:24431"),
    _sdef("developmental stage", "UBERON", "UBERON:0000105"),
    # The D3/D6 corpus sweep appends the non-defining bindings here.
]

# ---------- controlled-vocabulary (openMINDS) entity-field bindings ----------
# The THIRD binding shape: a controlled-term FIELD named directly on an entity
# (not keyed by a sibling `variable` like a statement leaf, and not a relation
# term). Each row pins a (class, field) to an openMINDS controlled-term set. The
# field itself is ontology_term-typed with an inline `binding` naming the same
# term_set; this registry is the single catalog so consumer tooling can enumerate
# every controlled vocabulary in one place (parity with relation_bindings). The
# instance library is NOT copied inline (drift) -- it is referenced by name and its
# release is pinned once in controlled_vocabularies. `closed` marks fixed sets
# (strength required) vs open/growing sets (strength preferred).
CONTROLLED_VOCABULARIES = {
    "openMINDS": {
        "version": None,   # concrete openMINDS release pinned by the import-provenance
                           # document (single source of truth); round-trip CI asserts it
        "iri_base": "https://openminds.ebrains.eu/instances/",
        "notes": "openMINDS controlled-term instance libraries; each term_set is a "
                 "flat instance library (IRI + label), not an ontology subtree.",
    },
}

ENTITY_FIELD_BINDINGS = [
    {"class": "dataset", "field": "accessibility",
     "vocabulary": "openMINDS", "term_set": "ProductAccessibility",
     "strength": "required", "closed": True},
    {"class": "dataset", "field": "ethics_assessment",
     "vocabulary": "openMINDS", "term_set": "EthicsAssessment",
     "strength": "required", "closed": True},
    {"class": "dataset", "field": "experimental_approach",
     "vocabulary": "openMINDS", "term_set": "ExperimentalApproach",
     "strength": "preferred", "closed": False},
]

# Illustrative examples kept OUT of the live binding list so they never collide
# with or get mistaken for swept data. Each shows one shape (term leaf + subtree,
# term leaf + enumerated NodeRef values, dimensional leaf with no spec, and a
# method+variable interaction).
BINDING_EXAMPLES = [
    {"variable": {"node": "", "name": "brain region"},
     "class": "term_observation",
     "ontology": "UBERON", "root_node": "UBERON:0000955",
     "notes": "term leaf + subtree: a located structure is a term_observation "
              "whose value resolves against the UBERON brain subtree"},
    {"variable": {"node": "PATO:0000047", "name": "biological sex"},
     "class": "term_assertion",
     "values": [{"node": "PATO:0000384", "name": "male"},
                {"node": "PATO:0000383", "name": "female"},
                {"node": "PATO:0001340", "name": "hermaphrodite"}],
     "notes": "term leaf + enumeration: a fixed set of ontology terms (NodeRefs, "
              "not bare strings) rather than a subtree"},
    {"variable": {"node": "", "name": "body mass"},
     "class": "mass_observation",
     "notes": "dimensional leaf: mass_observation already fixes the value type, so "
              "no admissible-set spec is needed"},
    {"variable": {"node": "", "name": "holding potential"},
     "method": {"node": "", "name": "voltage clamp"},
     "class": "voltage_manipulation",
     "notes": "method + variable: on an interaction the binding is keyed by both "
              "the method and the variable"},
]

binding_registry = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "https://did-schema.example.org/meta/binding_registry_meta.json",
    "title": "Binding registry for DID/NDI V_eta",
    "description": "Three coordinated registries, one per binding shape: "
                   "subject_statement_bindings (keyed by variable, for statement "
                   "leaves), relation_bindings (keyed by relation term, for edges), "
                   "and entity_field_bindings (keyed by class+field, for a "
                   "controlled-term field named directly on an entity -- e.g. the "
                   "openMINDS ProductAccessibility/EthicsAssessment/ExperimentalApproach "
                   "terms on dataset; the referenced instance libraries are pinned "
                   "once in controlled_vocabularies, not copied inline). "
                   "subject_statement_bindings map a "
                   "statement's variable (and, on interactions, method) to the "
                   "concrete subject_statement leaf class that carries it (e.g. "
                   "mass_observation, dose_manipulation, term_assertion). The leaf "
                   "fixes the value type, so there is no data_type; a term-valued "
                   "leaf additionally pins the admissible term set as an enumerated "
                   "values list (each an ontology term) or an ontology subtree "
                   "(ontology + root_node). Rows flagged subject_defining are the "
                   "kind-defining variables (D9). relation_bindings map a relation "
                   "term to its carrier class (directed_relation, with child -> "
                   "parent endpoints, / undirected_relation, with a symmetric "
                   "member set) and the admissible endpoint entity types. "
                   "Both registries are keyed on the term; an ontology node is "
                   "attached as the backing CURIE where a standard term exists, "
                   "otherwise the name is the key until one is assigned. Consumer "
                   "tooling resolves a value or endpoint against the matching "
                   "binding at validation time.",
    "subject_statement_bindings": SUBJECT_STATEMENT_BINDINGS,
    "binding_examples": BINDING_EXAMPLES,
    "relation_bindings": RELATION_VOCABULARY,
    "controlled_vocabularies": CONTROLLED_VOCABULARIES,
    "entity_field_bindings": ENTITY_FIELD_BINDINGS,
    "notes": "subject_statement_bindings are keyed on the variable (+ method on "
             "interactions) and name the concrete leaf class that carries the "
             "statement (e.g. mass_observation, dose_manipulation, term_assertion). "
             "The leaf fixes the value type -- there is no data_type and no "
             "separately-named value_set. Only a term-valued leaf carries an "
             "admissible-set spec (values or ontology+root_node); a dimensional "
             "leaf needs none. Rows flagged subject_defining make the subject-kind "
             "ingestion invariant precise: a subject is expected to carry >=1 "
             "term_assertion whose variable matches a subject_defining binding "
             "(checked at ingest). The remaining (non-defining) bindings are "
             "populated by the D3/D6 corpus sweep; binding_examples holds "
             "illustrative rows only and is not swept data. relation_bindings "
             "enumerate the admissible relation terms (D6): the value carried on "
             "directed_relation.relation / undirected_relation.relation is a member "
             "of this set. class pins the term to its carrier and thus its endpoint "
             "symmetry: a directed_relation carries child_types -> parent_types "
             "(matching the schema child/parent deps), an undirected_relation "
             "carries a symmetric member_types (matching its single entities dep). "
             "Abstract types (entity, subject) mean 'any of that genus'; [] = "
             "unconstrained. NOTE: every term today is directed_relation, so "
             "undirected_relation / member_types are reserved but currently unused "
             "-- the first symmetric relation added will exercise them. A relation "
             "`node` is the backing ontology CURIE (RO/BFO where one exists; "
             "\"\" = an open D6 slot). ordered marks terms where the directed "
             "sequence field is meaningful; timed marks event edges that may carry "
             "a method/time anchor.",
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
    # directory nesting (Phase 1): the parent directory is a directory; the
    # generic parent document is any doc (root `base`).
    "parent_directory_id": "directory", "parent_doc_id": "base",
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

# The epoch document is now a real standalone class (acquisition_epoch), so the
# ingested caches' `epochid` dep gets a target. Done PER-CLASS (not via GOV_REF):
# syncrule_mapping.epochid holds an epoch NAME, not a document id, so it stays
# untyped -- typing it would impose a doc-existence check its value can't satisfy.
for _c in ("daqreader_epochdata_ingested", "epochfiles_ingested"):
    _t, _p = path_of(_c)
    if _p:
        _d = load(_p)
        for _dep in _d.get("depends_on", []):
            if _dep.get("name") == "epochid" \
                    and not _dep.get("must_refer_to_document_class", ""):
                _dep["must_refer_to_document_class"] = "acquisition_epoch"
        write(_t, _c, _d)

# Governance: mark the `ndi_<x>_class` handles needs-NDI. Each of these kept device/
# sync infra classes discriminates its concrete implementation by an NDI-runtime
# class name it stores in an `ndi_<x>_class` field. DID keeps the field (round-trip)
# but cannot resolve or validate the class -- that lives in NDI-matlab -- so the
# field is flagged `needs_ndi` for downstream tooling. (The `epochid` on
# syncrule_mapping deliberately stays untyped above: it is an epoch NAME, not a doc
# id. Routing the epochnode_a/b + acquisition_epoch.clocks structures through
# time_reference is the remaining gov item -- a sync-layer change coordinated with
# NDI-matlab; see V_eta_6_7_walkthrough_STATE.md.)
NDI_CLASS_FIELDS = {
    "daqsystem": "ndi_daqsystem_class",
    "daqreader": "ndi_daqreader_class",
    "daqmetadatareader": "ndi_daqmetadatareader_class",
    "filenavigator": "ndi_filenavigator_class",
    "syncgraph": "ndi_syncgraph_class",
    "syncrule": "ndi_syncrule_class",
}
for _cls, _fname in NDI_CLASS_FIELDS.items():
    _t, _p = path_of(_cls)
    if not _p:
        continue
    _d = load(_p)
    for _f in _d.get("fields", []):
        if _f.get("name") == _fname:
            _f["needs_ndi"] = True
    write(_t, _cls, _d)

# Governance (gov part 3): route syncrule_mapping's epoch-node clock times through
# the time_reference model. Each epochnode_* embedded the epoch's clock as bare
# `epoch_clock` + `epoch_id` char fields -- a hand-rolled epoch reference duplicating
# epoch_bounded_reference. Nest them under a `time_reference` sub-structure shaped as
# an epoch_bounded_reference (kind + epoch_clock + epoch_id) so the sync layer states
# time in the canonical model, not bare strings. epoch_id stays a NAME (an epoch is
# not a standalone doc -- the same reason syncrule_mapping.epochid is left untyped
# above), so this is an embedded-shape normalization, NOT a doc dependency.
# epoch_session_id / epochprobemap / objectclass stay as node metadata. The
# reshape is applied to the corpus by DID-matlab migrators_j.syncrule_mapping.
def _epochnode(name, which):
    return field(name, "structure",
                 "Sync endpoint " + which + ": the epoch whose clock this mapping "
                 "relates. Its time flows through the time_reference model (an "
                 "embedded epoch_bounded_reference), not bare char.",
                 non_empty=False, sub_fields=[
                     subfield("time_reference", "structure",
                              "The epoch-clock reference this endpoint's times are "
                              "stated in (epoch_bounded_reference shape).",
                              sub_fields=[
                                  subfield("kind", "char", "The time_reference "
                                           "subclass modeled (epoch_bounded_reference)."),
                                  subfield("epoch_clock", "char", "The clock on the "
                                           "epoch (e.g. 'dev_local_time')."),
                                  subfield("epoch_id", "char", "The epoch NAME (an "
                                           "epoch is not a standalone doc, so a name, "
                                           "not a dep)."),
                              ]),
                     subfield("epoch_session_id", "char",
                              "The session the epoch belongs to."),
                     subfield("epochprobemap", "structure",
                              "The probe map at this epoch (NDI epoch-node metadata)."),
                     subfield("objectclass", "char",
                              "The NDI object class of this epoch node."),
                 ])

_t, _p = path_of("syncrule_mapping")
if _p:
    _d = load(_p)
    _d["fields"] = [
        _epochnode("epochnode_a", "A") if _f.get("name") == "epochnode_a" else
        _epochnode("epochnode_b", "B") if _f.get("name") == "epochnode_b" else _f
        for _f in _d.get("fields", [])
    ]
    write(_t, "syncrule_mapping", _d)


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
DATA_TYPES = list(DIMS) + [n for n, _ in NUMERIC_SEED] + ["dose", "formulation", "chemical",
    "visual_grating"]
for name in DATA_TYPES:
    p = os.path.join(VETA, "stable", name + ".json")
    if not os.path.exists(p):
        continue
    d = load(p)
    d["document_class"]["superclasses"] = [{"class_name": "data_type"}]
    # §A.7/§A.9 body-compat: a value's LOCATION is storage_mode (inline | reference
    # | body), NOT a class -- a data-type leaf (voltage_observation, ...) is
    # body-backed for a SERIES (value in a sampled_body) or inline for a SCALAR. The
    # closed meta-schema's mustBeNonEmpty is unconditional, so a required inline
    # `value` would quarantine every body-backed quantity observation
    # (image_observation only escapes this because `image` has no value field).
    # Relax `value` to optional (the leaves inherit it); inline-requiredness (value
    # present when storage_mode=inline) is an ingest validator (the D10 pattern),
    # not a closed-meta-schema constraint. This is what lets the #9 signal folds
    # (spikewaves->voltage_observation, binnedspikeratevm->frequency_observation)
    # be body-backed, per the J decision.
    for f in d.get("fields", []):
        if f.get("name") == "value":
            f["mustBeNonEmpty"] = False
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
    "session_in_a_dataset", "dataset_session_info",
    # v1 SOURCE classes dissolved by migrators_j (kept in-schema only until the
    # corpus proves the fold, then deleted -- NOT in the final set): the treatment
    # family -> manipulations, subject_group -> bare subject, image_stack(+params)
    # -> image_observation + sampled_body.
    "treatment", "treatment_drug", "treatment_transfer", "virus_injection",
    "subject_group", "image_stack", "image_stack_parameters"}
# The abstract dataseries_observation branch collapses into the quantity data-type
# leaves + data_body (§A.9): a body-backed series is <quantity>_observation +
# storage_mode:body, not a series-observation class. dataseries_observation is
# abstract (uninstantiable); timeseries_/imageseries_observation are unminted in J.
_RET_SERIES_OBS = {"dataseries_observation", "timeseries_observation",
    "imageseries_observation"}
# 2.D data_body collapse: data_body has EXACTLY 2 members (sampled_body,
# opaque_body); every format/series carrier has been folded/placed. What LEAVES:
#   - zarr     an orphaned abstract storage-format descriptor (nothing subclasses
#              or deps it); it exits with the carrier fold -- an encoding is a field,
#              not a standalone class -- pending the corpus confirming no zarr docs.
#   - pyraview the one real observation-tier fold left (has NDI presence); folds to a
#              body-backed observation with #9 (deferred, needs the NDI second pass).
# `image` is NOT here: image_observation subclasses `image` (its geometry mixin), so
# image is a KEPT superclass -- retiring it would orphan a persisting class.
_RET_CARRIERS = {"zarr", "pyraview"}
_RET_TOOBS = {"probe_location", "probe_geometry", "electrode_offset_voltage",
    "position_metadata", "distance_metadata", "ontology_label", "ontology_table_row",
    "ontology_image"}
_RET_HOLDOVER = {"calculator", "measurement"}
_ANALYSIS_RE = _re.compile(r"(_calc$|_calc_|tuning|stimulus_response|spike|cluster|"
    r"vmspike|binnedspikerate|jrclust|sorting_param|neuron_extracellular|hartley|"
    r"oridir|reverse_correlation|fitcurve|tuning_fit|simple_calc|contrast_sensitivity|"
    r"site2channelmap|vmneuralresponse|stimulus_parameter)")
# ⑦ acquisition/infra classes the ⑥/⑦ walkthrough (V_eta_6_7_walkthrough_STATE.md,
# all chunks a-e + gov ✅) DECIDED to KEEP -- they graduate from in_progress to persist
# (⑦ infra) now that the walkthrough is closed. Each was held in-schema pending that
# closure; the decision is recorded here. Disposition-only (does not affect corpus
# validation). Groups: ⑥-A daq readers/systems (needs-NDI), ⑥-B ingested caches (Option
# A: device-layer infra, NOT folded to sampled_body), ⑥-C epoch/time, ⑥-D sync,
# ⑦ directory, and the index/geometry infra (ngrid, dataseries_channel_map,
# binaryseries_parameters, filter).
_KEEP_INFRA = {"daqsystem", "daqreader", "daqmetadatareader",
    "daqreader_epochdata_ingested", "daqreader_image_epochdata_ingested",
    "daqmetadatareader_epochdata_ingested", "epochfiles_ingested", "epochid",
    "acquisition_epoch", "filenavigator", "syncgraph", "syncrule", "syncrule_mapping",
    "directory", "ngrid", "dataseries_channel_map", "binaryseries_parameters", "filter"}

# Genuinely-unsettled classes that STAY in_progress -- each needs a team call the
# walkthrough deliberately left open:
#   - instrument, interaction_purpose : subject-domain, "needs a call".
#   - app                             : SUPERSEDED by the `software` entity + the
#                                       `software_id` edge (Item-1 decision, R1). Retires
#                                       once every generator (calc done; clusters/ensemble/
#                                       stimulus_presentation pending) extracts its app
#                                       block -> a software entity. Kept meanwhile because
#                                       those generator docs still embed an `app` block.
#   - stimulus_presentation, control_stimulus_ids : D-B stimulus bodies-of-record whose
#                                       sampled_body fate is still open.
#   - demo_ndi, demo_ndi_mock         : demo/test fixtures, place in the final set unsettled.
#   - openminds_import                : new provenance doc, provisional.
#   - projectvar                      : infra, unsettled.
#   - ensemble                        : grain A (acquisition-infra) decided, but its NDI
#                                       second-pass member_of relations are pending
#                                       (V_eta_ensemble_plan.md) -- kept in_progress until then.
# NOTE: `instrument` RETIRED (deleted above, boundary re-audit). openminds_import is now
# draft (persist + emitter gap). projectvar/demo_ndi = green passthrough (re-audit: their
# retire evidence was false -- they ARE ndi v1 sources; corpus 0-doc check before any drop).
_IN_PROGRESS = {"interaction_purpose", "app", "stimulus_presentation",
    "control_stimulus_ids", "demo_ndi", "demo_ndi_mock", "openminds_import",
    "projectvar", "ensemble"}

def _disposition(name, doc=None):
    # V_eta TARGET classes are built EXPLICITLY (write()/doc()), not carried as v1
    # source tombstones, so they always persist -- even when their name matches the
    # _ANALYSIS_RE source-tombstone heuristic (the calc family shares stems like
    # "tuning"/"contrast_sensitivity" with the v1 sources it consumes). Detect them
    # structurally so the rule self-maintains as the family grows:
    #   ④ a subject_calculation LEAF (e.g. orientation_direction_tuning_calculation,
    #      stimulus_tuningcurve_calculation) -- subject_calculation is a V_eta-native
    #      genus, never a retiring source; and
    #   ③ an ABSTRACT data_type COMPOSITE (e.g. orientation_direction_tuning,
    #      contrast_sensitivity, stimulus_tuningcurve) -- audited: every abstract
    #      data_type composite is a real ③ class, none retire.
    # The v1 CALC source tombstones still carried as a safety net (oridirtuning_calc,
    # tuningcurve_calc, contrast_sensitivity_calc, ...) keep the v1 `base` shape
    # (concrete, no data_type/subject_calculation chain), so _ANALYSIS_RE still retires
    # them below -- correct, their docs migrate into the leaf.
    if doc is not None:
        _dc = doc.get("document_class", {})
        _chain = [sc.get("class_name") for sc in _dc.get("superclasses", [])]
        if "subject_calculation" in _chain:
            return ("persist", None)
        if _dc.get("abstract") and "data_type" in _chain:
            return ("persist", None)
    if name in _KEEP_INFRA:   return ("persist", None)   # ⑥/⑦ walkthrough KEEP (closed)
    if name in _RET_SOURCES:  return ("retire", "Phase-8 source (migrator → delete)")
    if name in _RET_SERIES_OBS:
        return ("retire", "§A.9: series-observation branch → quantity leaves + data_body")
    if name in _RET_HOLDOVER or _ANALYSIS_RE.search(name):
        return ("retire", "D-C analysis-tier decompose")
    if name in _RET_CARRIERS: return ("retire", "2.D → data_body fold")
    if name in _RET_TOOBS:    return ("retire", "→ observations (needs-NDI / D10-11)")
    if name in _IN_PROGRESS:  return ("in_progress", "⑥/⑦ walkthrough pending")
    return ("persist", None)

# ---- Phase-8 deletion: physically drop the fully-consumed v1 SOURCE schemas that
# are carried only as V_zeta copytree tombstones (they made the coverage ledger show
# a retiring class as if it were a V_eta "home"). A class qualifies ONLY when its
# docs cannot survive migration:
#   (a) it has a COMPLETED migrators_i dissolver that decomposes every doc into other
#       classes (treatment family, virus_injection, subject_group, image_stack+params
#       -> manipulations / bare subject / image_observation + sampled_body), OR
#   (b) it is abstract / unminted in J, so no doc can exist (the series-observation
#       branch: dataseries_ is abstract; timeseries_/imageseries_ are never minted).
# All 10 are verified (coverage-style scan) unreferenced by any kept schema and
# unemitted by any migrator.
# DELIBERATELY HELD (NOT deleted), despite being in _RET_SOURCES -- their docs are
# not provably consumed yet, so deleting the schema would strand live docs:
#   - element    : the most common NDI doc; its J dissolver is not corpus-confirmed
#                  to leave zero survivors. Delete only after a corpus per-class count
#                  shows 0 migrated `element` docs (blast radius is the whole corpus).
#   - openminds* : need migrators / entangled with the #9 analysis-tier work
#                  (guarded by test_phase1_source_cleanup_and_dep_typing).
# The remaining 2.D carriers (_RET_CARRIERS: zarr, pyraview) and the to-observation
# holdovers (_RET_TOOBS: distance_metadata, ontology_*, ...) stay -- their docs pass
# through and MUST keep a schema. Un-defer those first, then extend this set.
#
# The 7 vision-calculator WRAPPER tombstones below graduated from "held" once the
# calculator composite-leaf fold landed (migrators_j.private.jCalculation; Soph corpus
# + fast fixtures GREEN, 0 orphans): each has a completed migrator that folds it 1->1,
# id-preserved, into a `*_calculation` subject_calculation leaf (its class changes), so
# no migrated doc keeps the wrapper class. All 7 verified unreferenced by any kept V_eta
# schema (no superclass / typed dep) and unemitted by any migrator. NOTE the RESULT
# class NAMES (orientation_direction_tuning, contrast_sensitivity, stimulus_tuningcurve)
# are REUSED as persisting ③ composites and are NOT deleted; only the wrapper names,
# which nothing reuses, qualify.
_DELETE_PHASE8 = {
    "treatment", "treatment_drug", "treatment_transfer", "virus_injection",
    "subject_group", "image_stack", "image_stack_parameters",
    "dataseries_observation", "timeseries_observation", "imageseries_observation",
    "oridirtuning_calc", "contrast_tuning_calc", "spatial_frequency_tuning_calc",
    "temporal_frequency_tuning_calc", "speed_tuning_calc", "contrast_sensitivity_calc",
    "tuningcurve_calc",
}
_deleted = []
for tier in TIERS:
    for p in glob.glob(os.path.join(VETA, tier, "*.json")):
        base = os.path.basename(p)
        if base in META_FILES:
            continue
        try:
            cn = load(p)["document_class"]["class_name"]
        except Exception:
            continue
        if cn in _DELETE_PHASE8:
            os.remove(p)
            _deleted.append(cn)
if _deleted:
    print(f"V_eta Phase-8 delete: removed {len(_deleted)} consumed source schemas: "
          + ", ".join(sorted(_deleted)))

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
        disp, track = _disposition(dc["class_name"], d)
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
