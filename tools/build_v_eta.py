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
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VZETA = os.path.join(ROOT, "schemas", "V_zeta")
VETA = os.path.join(ROOT, "schemas", "V_eta")
TIERS = ["stable", "draft", "deprecated"]
META_FILES = {"did_schema_meta.json", "CURIE_lookups_meta.json", "ndi_reserved_keys.json",
              "binding_registry_meta.json"}

DIMS = ["mass", "length", "volume", "duration", "temperature", "pressure",
        "frequency", "voltage", "current", "concentration", "count", "score"]


# ---------- helpers ----------

# The types DID-matlab's validator will accept ONLY as char/scalar-string.
# `src/did/+did2/+schema/cache.m:1764` validateTypeShape:
#
#     case {'char', 'did_uid', 'timestamp'}
#         if ~(ischar(value) || (isstring(value) && isscalar(value)))
#             error('did2:validation:typeMismatch', ...
#
# `string` is NOT in that case (it has its own, wider one) but a bare '' is
# accepted there too, so it rides along in the ladders below.
#
# WHY THIS IS A NAMED CONSTANT AND NOT THREE LITERALS IN TWO LADDERS: it was
# two literals in two ladders, and `timestamp` was in neither. Both ladders
# fell through to `0.0`, so `subjectmeasurement.datestamp` and
# `absolute_reference.value.start.utc` were emitted with a DOUBLE blank for a
# type the validator accepts only as char -- a blank document built from the
# schema cache would have failed its own type check. `base.datestamp` was
# right only because it is copied verbatim from the V_zeta snapshot and never
# passes through these helpers. See tests/test_veta_blank_values_typecheck.py,
# which scans EVERY field of EVERY built schema against the validator's
# accepted shapes rather than special-casing this one type.
# `date` JOINS THE CHAR-LIKE SET 2026-08-13, and it is a NEW dtype rather than
# a relabelling of `timestamp`. A calendar date and a wall-clock instant are
# different facts with different precision, and conflating them INVENTS data:
# `publication.date` is documented "Publication date/year", so forcing it into
# an ISO 8601 UTC instant manufactures a month, a day and a time that no source
# supplied. `date` is deliberately PARTIAL-PRECISION -- `YYYY`, `YYYY-MM` and
# `YYYY-MM-DD` are all well-formed -- which is exactly what `timestamp` must
# NOT accept once it is constrained.
#
# It is char-like for the same reason `timestamp` is: the validator's
# `validateTypeShape` accepts these as char/scalar-string, so the blank value
# must be '' and not 0.0. tests/test_veta_blank_values_typecheck.py scans every
# field of every built schema against the validator's accepted shapes, so a
# type added here and NOT taught to the MATLAB side fails there rather than
# silently emitting 0.0 into a char slot.
_CHARLIKE_BLANK_TYPES = ("char", "string", "did_uid", "timestamp", "date")


def subfield(name, ftype, doc, *, non_empty=False, scalar=True, blank=None,
             constraints=None, sub_fields=None):
    if blank is None:
        blank = {"node": "", "name": ""} if ftype == "ontology_term" else (
            "" if ftype in _CHARLIKE_BLANK_TYPES else (
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
            [] if not scalar else ("" if ftype in _CHARLIKE_BLANK_TYPES else (
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


# The 14-value datum vocabulary, copied from `zarr.dtype` (signed plan, "WHAT IS
# BOUND"): the class is deleted but its enumeration was the considered one, and
# reusing it keeps V_eta readable against the wider array-storage world.
#
# `char` IS DELIBERATELY ABSENT and that is the plan's own finding -- the
# normalisation map says "char -> DECISION: no canonical in the 14", and open
# item 6 ("`char` and complex datum types are decisions, not mappings") is NOT
# closed. Nothing is invented here to paper over it.
DATUM_TYPES = [
    "uint8", "uint16", "uint32", "uint64", "int8", "int16", "int32",
     "int64", "float16", "float32", "float64", "complex64",
     "complex128", "bool",
]


def axis_subfields():
    """The ONE axis entry. TEAM-SIGN-OFF [data_body] 2026-08-14 + AMENDMENT 1.

    A SHARED BUILDER RATHER THAN THREE COPIES, BECAUSE "ONE AXIS ENTRY" IS THE
    DECISION ITSELF. The signed addendum's section 5 is titled "ALL THREE AXES
    DECLARATIONS FOLD INTO THE ONE ENTRY", and three hand-maintained copies of a
    shape whose whole purpose is to stop being three shapes would re-create the
    defect on the first divergent edit -- which is how the tree acquired three
    incompatible spellings of regular-vs-enumerated in the first place.

    A FUNCTION, not a module-level constant: each caller mounts the result under
    its own documentation, and a shared mutable list would let one caller's edit
    leak into the next.

    THE THREE MOUNTS, and the fourth that is deliberately absent:
        sampled_body.axes        the body's own extent
        image.value.axes         the raster cell's extent, when inline
        acquisition_epoch.axes   the epoch header's extent
        zarr.axes                NOT FOLDED. Decision 10 DELETES zarr rather
                                 than migrating it, so folding its axes would be
                                 work on a class on its way out. This is why the
                                 plan's denominator reads 3 where a sweep of the
                                 built tree reads 4.
    """
    return [
              subfield("variable", "ontology_term",
                       "What varies along this dimension (time, spatial "
                       "position, contrast, ...). UNIQUE within the list -- "
                       "that uniqueness is what makes 'which axis is X' well "
                       "defined.",
                       non_empty=True),
              subfield("unit", "ontology_term",
                       "Canonical unit of `origin`/`spacing`/`values`. Angles "
                       "are RADIANS, per angle.value.radians and the SI "
                       "convention every other quantity in V_eta follows. "
                       "Absent for a categorical axis, which uses `labels`."),
              subfield("source_unit", "char",
                       "The unit exactly as the source gave it. OMITTED when "
                       "the source unit is already canonical."),
              subfield("approximate", "boolean",
                       "Applies to the whole axis.", blank=False),
              subfield("n", "integer",
                       "Number of coordinates along this axis; equals the "
                       "extent of the value it indexes.",
                       non_empty=True, scalar=True, blank=0),
              subfield("regular", "boolean",
                       "True: coordinates are generated from origin + spacing. "
                       "False: they are stored, in `values` or `labels`.",
                       blank=False),
              subfield("origin", "structure",
                       "Where the axis starts. REQUIRED iff `regular`.",
                       sub_fields=[
                           subfield("value", "double", "Canonical value.", blank=0.0),
                           subfield("source_value", "double",
                                    "As-recorded value.", blank=0.0)]),
              subfield("spacing", "structure",
                       "The step. REQUIRED iff `regular`.",
                       sub_fields=[
                           subfield("value", "double", "Canonical value.", blank=0.0),
                           subfield("source_value", "double",
                                    "As-recorded value.", blank=0.0)]),
              subfield("values", "structure",
                       "The coordinates themselves. REQUIRED iff NOT `regular` "
                       "and numeric. XOR with `labels`.",
                       sub_fields=[
                           subfield("values", "matrix", "Canonical values.", blank=[]),
                           subfield("source_values", "matrix",
                                    "As-recorded values.", blank=[])]),
              # blank is the helper's ontology_term default ({node,name}), NOT
              # []. A non-scalar ontology_term whose blank is `[]` fails its own
              # type check -- cache.m:1764 wants a struct -- and
              # test_veta_blank_values_typecheck catches exactly that. The two
              # other non-scalar ontology_terms in the schema
              # (dataset.experimental_approach, strain.disease_model) use the
              # struct blank; conditions.term.value carries `[]` and sits in
              # that test's pinned baseline, so it is the exception, not the
              # pattern to copy.
              subfield("labels", "ontology_term",
                       "Categorical coordinates. REQUIRED iff NOT `regular` "
                       "and categorical. XOR with `values`.",
                       scalar=False)
    ]


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
          "oneepoch", "epochclocktimes", "session_extent",
          "mock",
          # `valid_interval` and `generic_file` WERE HERE, and are deliberately not,
          # as of 2026-08-10. Both are REAL PRODUCTION did_v1 classes with an NDI
          # template, a shipped schema and a live writer; deleting the schema while
          # no migrator consumes the documents is the stranding case, not the
          # dissolution case. Restated as SOURCE TOMBSTONES further down (search
          # `_tombstone("generic_file"` / `_tombstone("valid_interval"`). The
          # evidence and the two reversals are written out there rather than here,
          # because it is the tombstone a future reader needs to check, not the
          # absence of a set member. Note in particular what the deleted comment
          # ASSERTED -- "DID-matlab migrators_j.generic_file folds v1 docs":
          #
          #     ls src/did/+did2/+convert/+migrators_j/ | grep -i 'generic\|valid'
          #         (no output)
          #     ls src/did/+did2/+convert/+migrators/   | grep -i 'generic\|valid'
          #         (no output -- so not even the V_delta fallback has one)
          #
          # The denominator is the whole package (83 entries when this was
          # written, and moving -- the load-bearing number is the ZERO, so the
          # check is stated as the command rather than as a ratio that goes
          # stale the next time somebody adds a migrator).
          #
          # There is no such migrator and there never was. A build comment claimed
          # a consumer that does not exist, and that claim is why the deletion read
          # as safe.
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
          # `image_collection` WAS HERE, and is deliberately not, as of
          # 2026-08-11 (team decision: treat it as a tombstone). The comment that
          # stood here read "a bag of image files. Nothing creates it -- 0
          # references in NDI-matlab or DID-matlab, NOT A did_v1 SOURCE CLASS --
          # so like generic_file it dissolves schema-only". Three problems, and
          # the middle one is the operating-rule violation:
          #
          #   (1) "not a did_v1 source class" is FALSE. The template ships on NDI
          #       origin/main and coverage.py counts it as one of the 102 v1
          #       sources -- it is one of the four UNVERIFIED rows, by name.
          #
          #         $ git -C NDI-matlab grep -l -i imagecollection origin/main
          #         origin/main:src/ndi/ndi_common/database_documents/data/image.json
          #         origin/main:src/ndi/ndi_common/database_documents/data/imageCollection.json
          #         origin/main:src/ndi/ndi_common/schema_documents/data/imageCollection_schema.json
          #         origin/main:src/ndi/ndi_common/schema_documents/data/image_schema.json
          #
          #   (2) "like generic_file it dissolves schema-only" -- generic_file came
          #       OUT of this set on 2026-08-10, for this exact reason. The
          #       comparison outlived the thing it compared to.
          #
          #   (3) "mints an image_observation of its ELEMENT_ID subject" reads a
          #       field NDI's template does not have. imageCollection depends on
          #       `subject_id`; `element_id` is the V_alpha snapshot's invention
          #       (schemas/V_alpha/imageCollection.json), carried into V_zeta along
          #       with `collection_file`, `num_images`, `image_format` and
          #       `description` -- FIVE names, none of which is in NDI. The
          #       V_zeta shape and NDI's shape have NOTHING in common but `base`.
          #
          # Nothing WRITES one today (0 of 1002 .m files on origin/main, all three
          # spellings), and per the standing rule that is not a bound: a class no
          # in-tree writer produces is precisely the one that arrives from a
          # dataset nobody has migrated yet, and the corpora are a SAMPLE. With no
          # schema, such a document quarantines. Restated below as a SOURCE
          # TOMBSTONE from the template -- search `_tombstone("image_collection"`.
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

# `datum` COLLAPSES TO `datum_type`, AND IT MOVES TO THE STATEMENT (signed sec.5
# + the signature: "datum collapses to datum_type on the statement"). Of the old
# four sub-fields only `dtype` survives: `unit` was EMPTY at 4 of 4 writers and
# the value's unit comes from `variable`; `shape` was read two different ways by
# its own writers and is now `[axes.n]` in array order; `kind` was scalar-vs-array,
# which is the axis COUNT, and its one `record` use is a labelled categorical axis.
#
# IT IS NOT SCHEMA-REQUIRED, AND THAT DEPARTS FROM THE WORD "REQUIRED" IN THE
# PLAN. Recorded rather than done quietly. The plan says REQUIRED in sec.5 and
# says "DECLARED ON data_body" in "WHAT IS BOUND" -- two placements, and the
# signature plus the later addendum both settle on the STATEMENT. But required
# on the statement is not buildable against the 14-value vocabulary:
#
#     DENOMINATOR: 241 V_eta classes; 78 CONCRETE classes descend from
#                  subject_statement, and all 78 carry a data_type composite.
#     The 14 values are all NUMERIC, and the plan's own map records
#     "char -> DECISION: no canonical in the 14" with open item 6 still OPEN.
#
# So a `term_observation`, whose payload is a CURIE, has no legal value to put
# there -- and #38 (NonVacuousFields) is armed, so a blank required field
# quarantines. Making it required would quarantine most of the corpus to satisfy
# a word.
#
# The requirement is therefore CONDITIONAL AND DOCUMENTED, exactly as
# `byte_order` and `datum_order` are one commit back: the condition ("the value
# has a byte representation") is a property of the document, which this schema
# layer cannot express. If the team wants it enforced, the way in is a 15th
# value for non-numeric payloads, or declaring it on `data_body` per the other
# reading -- both team calls, neither made here.
DATUM_TYPE = field(
    "datum_type", "char",
    "How this statement's VALUES are encoded. REQUIRED in practice whenever the "
    "value has a byte representation (storage_mode `body` or `reference`); "
    "absent for a value that is a term or an inline composite with no numeric "
    "payload.",
    non_empty=False, constraints={"enum": DATUM_TYPES})

SOURCE_DATUM_TYPE = field(
    "source_datum_type", "char",
    "The source's own spelling, OMITTED when it is already canonical. Kept "
    "because the map is NOT invertible -- `bool` maps back to `logical` OR "
    "`ubit1`, and `char` has no canonical at all -- so retaining it makes the "
    "normalisation AUDITABLE: the corpus can be queried afterwards to verify "
    "every `float64` came from a `double` rather than from a default.",
    non_empty=False)

STATEMENT_AXES = field(
    "axes", "structure",
    "Index dimensions of this statement's value, in array order: axes[k] IS "
    "array dimension k. Time is an ordinary axis. Populated when the value is "
    "INLINE on the statement or lives behind a single external REFERENCE; when "
    "storage_mode is `body` the axes live on each data_body instead, because "
    "each body has its own extent.",
    non_empty=False, scalar=False, blank=[], sub_fields=axis_subfields())

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
          deps=[SUBJECT_ID],
          fields=[VARIABLE, CONDITIONS, STATEMENT_AXES,
                  DATUM_TYPE, SOURCE_DATUM_TYPE]))

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

# NO `epoch_id` HERE, DELIBERATELY -- team decision, jess, 2026-08-10:
#   "Use the reference chain, don't add the direct edge"
#
# The epoch plan's signed line reads "epochid is DROPPED in favour of a uniform
# epoch_id edge", and read literally that would put one on every epoch-scoped
# document, this class included. It does not, and the omission is written here
# rather than left silent, because an unexplained absence is what someone
# "completing the family" would helpfully fix.
#
# A statement already reaches its epoch:
#   subject_interaction --time_reference_#--> relative_reference
#                       --relative_to------> epoch
# A direct edge would store one fact twice, which is the hazard the epoch plan
# itself flags for base.session_id vs part_of and marks "Flagged, not solved".
# Two copies of one fact agree by coincidence until something checks them, and
# nothing here would.
#
# `directed_relation` KEEPS its optional epoch_id and that is not inconsistent:
# it is signed separately under the ensemble decision ("EPOCH-SCOPED member_of
# edges carrying their epoch"), where the epoch is the edge's OWN content -- the
# per-epoch roster changes epoch to epoch -- rather than a restatement of when
# the statement happened.
#
# KNOWN WEAK LINK, recorded so it is not discovered as a surprise: the chain is
# guaranteed by `min_count: 1` on time_reference_# (see the edge-family table
# below), but that entry is mustBeNonEmpty=False, so a statement carrying
# `time_reference_1 = ''` satisfies the family and reaches no epoch. The armed
# RequiredDependencies gate keys on mustBeNonEmpty and will NOT catch it. That
# is the invented-empty-edge shape one link along, and tightening it is the
# thing to do before anyone argues the direct edge is needed after all.
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
# `term` — the ③ composite the term leaves were missing. Every other leaf family pairs a
# direction with a data_type; term_observation / term_manipulation / term_assertion each
# declared their own `value` instead, which is why an `isa term` query could not span them
# (walkthrough finding B). Given T8/T12 make `term_*` the standard answer for every
# controlled vocabulary, this is the most-used value kind in the model -- it earns a
# composite. One payload slot, T14.
#
# BINDING STRENGTH: `required`, uniformly. The v1 leaves had drifted apart -- observation
# `preferred`, manipulation + assertion `required` -- but there is no reason the strength
# should vary by statement DIRECTION: a term is a term, and every one of them must resolve
# against the binding registry. If a vocabulary cannot express something observed, the fix
# is to extend the vocabulary, not to weaken the constraint on the observation (T8:
# controlled vocabularies are hard-validated, NOT advisory). Hoisting to the shared `term`
# composite makes that uniformity structural rather than a thing three leaves have to agree
# on. Note the validator does not enforce `binding` yet (validateConstraints handles only
# maxLength/minLength/minimum/maximum/enum), so this is declarative until the
# ontology-aware validator T8 describes exists -- but it declares the right rule.
TERM_VALUE = field(
    "value", "ontology_term",
    "The bound term this statement is about — asserted (species, sex, strain, instrument "
    "type), observed (developmental stage, health status, behaviour, anatomical site), or "
    "imposed (a procedure, a regime, a transferred material). The admissible vocabulary is "
    "a variable-keyed binding (D9), REQUIRED for every direction: a term must resolve "
    "against the registry whether it is observed, imposed or asserted. An unrepresentable "
    "concept is a reason to extend the vocabulary, not to weaken the binding (T8).",
    non_empty=True, scalar=True,
    constraints={"binding": {"keyed_by": "variable", "expansion": "descendants",
                             "node_kind": "class", "strength": "required",
                             "source": "ontology"}})
write("stable", "term",
      doc("term", ["data_type"], abstract=True, fields=[TERM_VALUE]))
write("stable", "term_assertion",
      doc("term_assertion", ["subject_assertion", "term"]))

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
# `date` — the ③ composite for a real date (walkthrough finding B, same as `term`).
write("stable", "date",
      doc("date", ["data_type"], abstract=True, fields=[DATE_VALUE]))
write("stable", "date_assertion",
      doc("date_assertion", ["subject_assertion", "date"]))

# The dimensioned assertions pair with their composite, exactly like the observations
# (walkthrough finding A). They previously hung off a `numeric_assertion` genus and
# REDECLARED `value` locally -- same name, same type, differing ONLY in `mustBeScalar`
# (true vs the composite's false, per J §5 "an assertion is one cell, no series"). That
# one flag cost an `isa <data_type>` lineage query: it returned observations and silently
# missed every assertion, because the chain had no `voltage` in it. It also sat against
# T12 rule 3 (cardinality is not a class distinction).
#
# `mustBeScalar: false` PERMITS a scalar, it does not require an array -- so pairing
# changes no document's shape, it only stops the schema from GUARANTEEING one cell. That
# guarantee is prospective anyway: nothing emits a dimensioned assertion (across all 102
# v1 sources the only assertion targets are term_assertion and date_assertion), so these
# are pre-seeded scaffolding. Whether "one cell" should be re-enforceable -- a subclass
# TIGHTENING a constraint rather than redeclaring it -- is deferred to the binding
# governance pass (TaskList #32), which is already the "make declarations enforced"
# workstream.
#
# `numeric_assertion` is therefore deleted: 0 fields, 0 remaining members, and it existed
# only to host the cardinality flag.
for d in DIMS:
    write("stable", f"{d}_assertion",
          doc(f"{d}_assertion", ["subject_assertion", d]))


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
                    non_empty=False, multiple=True),
                # ---- #60: the `epoch_id` slot, the second half of a recorded blocker
                # V_eta_OPEN_WORK.md's "Blockers found in DID-schema, each of which
                # stops a signed model being finished" carries this row verbatim:
                # "`directed_relation` has no `epoch_id` slot, AND no migrator mints
                # an `epoch`" -> "the ensemble's `member_of` edges cannot be
                # epoch-scoped, so the per-epoch MAP document cannot be consumed and
                # stays a passthrough".
                #
                # The blocker had two halves and the OTHER one closed first:
                # `did2.convert.epochMint` now mints one `epoch` per distinct
                # (base.session_id, epoch-id string). This is the half that lives in
                # this repository.
                #
                # SIGNED, twice, from two directions:
                #   ensemble  TEAM-SIGN-OFF [ensemble] jess 2026-08-06 -- members are
                #             "EPOCH-SCOPED member_of edges carrying their epoch and
                #             column order". `sequence` (below) already carries the
                #             column order; the epoch was the missing half.
                #   epoch     TEAM-SIGN-OFF [epoch] jess 2026-08-08 -- "epochid is
                #             DROPPED in favour of a UNIFORM epoch_id edge". Uniform
                #             means this name, on every class that needs it:
                #             acquisition_metadata_file, ingestion_manifest and
                #             method_parameters already spell it `epoch_id -> epoch`.
                #
                # IT IS NOT `time_reference_#` RESTATED, which is the objection to
                # answer before adding a second temporal-looking edge. That family
                # says WHEN the relation happened. This says WHICH RECORDING the
                # relation was observed in -- scope, not timing -- and the ensemble
                # is exactly why the difference is load-bearing: the recorded neuron
                # set CHANGES epoch to epoch, so the same (child, parent) pair is a
                # different membership fact in a different epoch. A timestamp cannot
                # express that; an edge to the epoch can.
                #
                # OPTIONAL, and not by default: every relation outside the ensemble
                # (part_of, has_author, derived_from) has no epoch, and #37's
                # strictMode('RequiredDependencies') is now ARMED -- a required edge
                # nothing can fill is the invented-empty-edge pattern that put six
                # classes at 100% empty. `member_of` will fill it in the NDI second
                # pass, which is the only place the per-epoch roster can be read.
                dep("epoch_id", "epoch",
                    "OPTIONAL scope: the recording this relation was observed in, "
                    "for relations whose truth is per-epoch. The ensemble's "
                    "`member_of` edges are the signed case -- the recorded neuron "
                    "set changes epoch to epoch, so the roster is preserved as one "
                    "edge per (member, epoch) rather than lost to the cache. NOT a "
                    "restatement of `time_reference_#`: that says WHEN the relation "
                    "happened, this says WHICH RECORDING it holds in. Empty for "
                    "every timeless or session-wide relation (part_of, has_author, "
                    "derived_from), which is why it is optional.",
                    non_empty=False)],
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
# ---- #66: the ingested-payload family gets a carrier that can EXIST --------
# The earlier claim that this family "needs no new class" was WRONG for a
# structural reason: `sampled_body` and `opaque_body` BOTH declare
# `depends_on: statement`. A body must hang off a statement, and a per-epoch
# metadata blob is not an observation of any subject -- there is no statement for
# it to hang from. So it needs a thin infra carrier, which is what it already is.
#
# NAMED 2026-08-06. Claude first proposed `ingested_payload`; the team said it
# seemed wrong, and it was -- it repeats the very mode-in-name this rename
# removes (`_epochdata_ingested`, the same T13 error as `_ndr` and `_mfdaq`).
#
# `acquisition_metadata_reader` is minted with it because the carrier's REQUIRED
# edge points at it. Additive: it does not touch `daqmetadatareader`, whose fold
# is #59 and gated on #37.
write("stable", "acquisition_metadata_reader",
      doc("acquisition_metadata_reader", ["base"], fields=[
          field("metadata_file_pattern", "char",
                "Pattern matching the metadata files this reader consumes "
                "(e.g. \".*\\\\.tsv\\\\>\").", non_empty=False)],
          deps=[dep("software_id", "software",
                    "The reader program itself, as a `software` entity -- the R1 "
                    "replacement for an NDI class-handle string.",
                    non_empty=False)]))
# `acquisition_reader` -- THE MISSING SIBLING, and the gap it closes is a
# measured one rather than a symmetry argument.
#
# The signed daq decision (V_eta_daq_family_decisions.md:471) says "daqreader
# DISSOLVES into a `software` entity" AND, in the same sentence, that
# `reader_string` is "KEPT as the de-encoded daqreader_ndr.ndr_reader_string".
# Both cannot hold: `software` declares name / version / local_identifier and
# nothing else, so a document carrying a reader string had nowhere to put it.
# `+migrators_j/daqreader.m` has been holding that line with a guard -- "A
# POPULATED `reader_string` => PASS THROUGH" -- so those documents never
# dissolved at all; they stayed `daqreader`, a class the signature retires.
#
# IT IS NOT HYPOTHETICAL. Both `daqreader_ndr` documents in the PRED corpus
# carry one:
#
#     daqreader_ndr {"ndr_reader_string": "intan",
#                    "ndi_daqreader_ndr_class": "ndi.daq.reader.mfdaq.ndr"}
#
# The shape is NOT invented here -- it is the one its sibling already has.
# `acquisition_metadata_reader` is exactly "a reader that carries its own
# configuration field and points at a `software` entity for its implementation
# class", and that is what a daq reader is too. The asymmetry was the accident.
write("stable", "acquisition_reader",
      doc("acquisition_reader", ["base"], fields=[
          field("reader_string", "char",
                "Reader/file-type string (e.g. 'intan', 'SpikeGadgets') -- the "
                "de-encoded did_v1 `daqreader_ndr.ndr_reader_string`. Optional: "
                "the concrete reader is discriminated by its `software` entity, "
                "and only some readers take a format selector.",
                non_empty=False)],
          deps=[dep("software_id", "software",
                    "The reader program itself, as a `software` entity -- the R1 "
                    "replacement for an NDI class-handle string. Same edge, same "
                    "meaning and same optionality as on "
                    "`acquisition_metadata_reader`.",
                    non_empty=False)]))
write("stable", "acquisition_metadata_file",
      doc("acquisition_metadata_file", ["base"], fields=[],
          deps=[dep("acquisition_metadata_reader_id", "acquisition_metadata_reader",
                    "The reader whose output these bytes are.", non_empty=True),
                dep("epoch_id", "epoch",
                    "The epoch these bytes were ingested for.", non_empty=True)]))
_amf_tier, _amf_path = path_of("acquisition_metadata_file")
_amf = load(_amf_path)
_amf["file"] = [{"name": "data.bin",
                 "documentation":
                     "The reader's ingested bytes for this epoch. The ONLY content "
                     "this class has -- it declares no fields. Do NOT type the "
                     "payload: the readers produce TSV in the cases seen, but "
                     "nothing declares that, and proposing a shape from a template "
                     "alone is what produced the ~2,078 distance_metadata "
                     "quarantines."}]
write(_amf_tier, "acquisition_metadata_file", _amf)

# ---- #74: MINT `method_parameters` -- settings with an identity ------------
# SIGNED 2026-08-09. The class is the existing inline
# `subject_interaction.method_parameters` field PLUS an identity, and nothing
# more: no domain fields, which is what finally makes a general name truthful
# after `method_parameters`, `analysis_protocol` and `calculation_protocol` were
# each rejected for promising generality a domain-specific class cannot deliver.
#
# WHY THE CLASS EXISTS AT ALL, and it is not about fields: v1 gives these
# settings a `base.name` that two apps look up by exact_string
# (`spikeextractor.m:372`, `spikesorter.m:373`) and three document types point at
# by id. Dissolve them into their outputs and the 11,448-orphan failure returns,
# with the name lookup having nowhere to look.
#
# ROUTING, decided per class and globally so it cannot drift: the source gave the
# settings a name and an id and things point at them -> a document; otherwise
# inline. A calculator's `input_parameters` has neither -- 2 templates carry the
# block and ZERO dependencies anywhere in NDI are named for it.
#
# THIS IS THE ADDITIVE HALF ONLY. Retyping the inline field from `structure` to
# `parameter[]` breaks every calculator migration (`jCalculation.m:99` writes a
# struct there), so it is a cross-repo lockstep and rides with the migrator.
_PARAMETER_SUBS = [
    subfield("variable", "ontology_term",
             "WHAT knob this is. BOUND, and UNIQUE within the list. Modelled on "
             "the `axis` entry: identity lives in a bound variable, so "
             "domain-specific knobs are DATA rather than schema, and no class or "
             "field has to be minted per program. Its dimension comes from the "
             "registry -- there is NO unit field and NO data_type field.",
             non_empty=True),
    subfield("value", "structure",
             "Numeric knobs. The canonical value plus what the source wrote.",
             sub_fields=[
                 subfield("value", "double", "Canonical value.", blank=0.0),
                 subfield("source_unit", "char", "As-recorded unit."),
                 subfield("source_value", "char", "As-recorded value, VERBATIM -- "
                          "v1 writes a threshold as the string \"0.030\", and the "
                          "string is kept whatever the registry later says."),
             ]),
    subfield("term", "ontology_term",
             "Categorical knobs (e.g. a threshold method)."),
    subfield("text", "char", "Free-string knobs."),
]
write("stable", "method_parameters", doc("method_parameters", ["base"], fields=[
    field("name", "char",
          "The protocol's name, e.g. \"default\". OPTIONAL: a scoped variant "
          "need not be named. "
          "CITATION CORRECTED 2026-08-12 -- this read \"the string "
          "spikeextractor.m:372 and spikesorter.m:373 query by exact_string\", "
          "and those two lines query `base.name`, NOT this field: "
          "ndi.query('base.name','exact_string',extraction_parameters_name,'') "
          "and ndi.query('base.name','exact_string',sorting_parameters_name,''), "
          "re-read from NDI origin/main. `method_parameters` inherits `base`, so "
          "this declaration is a SECOND COPY of a name the apps read from the "
          "`base` block -- one fact in two live storage locations, which is #69. "
          "WHICH BLOCK IS AUTHORITATIVE IS AN OPEN TEAM DECISION riding with "
          "binding governance; nothing here settles it, and the field and its "
          "constraints are unchanged. Do not delete either copy on this note. "
          "The block comment above is correct as written: it always said "
          "`base.name`, and only this string disagreed with it.",
          non_empty=False),
    field("method_parameters", "structure",
          "The settings themselves. SAME FIELD NAME as the inline field on "
          "`subject_interaction`, deliberately: one list means one thing in both "
          "mount points, exactly as `axes` mounts on two classes under one name. "
          "`parameters` was REJECTED -- that name was vacated when the statement's "
          "field became `conditions`, and a document already carries three "
          "variable-keyed lists (conditions, axes, method_parameters) that must "
          "not be confusable.",
          non_empty=False, scalar=False, sub_fields=_PARAMETER_SUBS),
    field("other", "structure",
          "The undeclared long tail -- read_time, overlap, graphical_mode, PCA "
          "feature counts. Kept whole rather than dropped; a knob nobody will "
          "query does not earn a bound variable.", non_empty=False)],
    deps=[dep("software_id", "software",
              "Which program these settings configure.", non_empty=False),
          dep("subject_id", "subject",
              "OPTIONAL scope: settings that apply to ONE recording. Precedence "
              "comes from THIS and epoch_id -- not from the self-edge.",
              non_empty=False),
          dep("epoch_id", "epoch",
              "OPTIONAL scope: settings that apply to ONE epoch.", non_empty=False),
          dep("derived_from_id", "method_parameters",
              "The named protocol this one is a variant of. LINEAGE ONLY -- it "
              "records origin, not precedence, and the variant carries a COMPLETE "
              "copy of every setting rather than a diff. Reuses the word the "
              "schema already spends on this relation (`derived_from_#` on "
              "calculations and observations); `parent_id` was rejected because it "
              "implies the child inherits, and it does not.",
              non_empty=False)]))

# The edge goes on `subject_interaction`, NOT `subject_statement`: the statement
# tier splits two ways and only one has a method at all. `subject_assertion` and
# its 30 leaves are timeless and methodless -- "this animal is of strain PR811"
# has no algorithm.
_si_tier, _si_path = path_of("subject_interaction")
_si = load(_si_path)
if not any(x["name"] == "method_parameters_id" for x in _si.get("depends_on", [])):
    _si["depends_on"].append(
        dep("method_parameters_id", "method_parameters",
            "OPTIONAL: named, shared settings this run used. A statement carries "
            "the inline `method_parameters` field OR this edge, NEVER BOTH (team, "
            "2026-08-09) -- one fact, one place, so a reader never has to know "
            "which wins.", non_empty=False))
write(_si_tier, "subject_interaction", _si)

# ---- #60: MINT `epoch` -- the class the whole time model assumed existed ----
# SIGNED 2026-08-08. An epoch is not an interval, it is a RECORDING: minted from
# one acquisition device's files for one run (`ndi.file.navigator.m:271`,
# id = ['epoch_' ndi.ido.unique_id()], written to a hidden file beside them), and
# everything derived from it -- probes, elements, spike trains -- INHERITS that id
# rather than minting its own (`ndi.element.m:276,293`). Two daqsystems recording
# the same wall-clock period get two DIFFERENT epochs, which is why its temporal
# extent is a property of it and not its identity.
#
# Nothing had ever minted one. The time-reference model was written assuming an
# epoch IS a document, and 11,118 `acquisition_epoch` documents carried clock data
# that nothing pointed at, while `epochid.epochid` was matched by `exact_string` at
# 30 live NDI sites. This class turns those string joins into edges.
#
# `local_identifier` is declared HERE and REQUIRED rather than inherited: `entity`
# deliberately declares none precisely so a child can ADD it as required (the same
# reason `subject` does), and the v1 epochid string is the handle every one of
# those 30 sites joins on -- losing it would break them.
write("stable", "epoch", doc("epoch", ["entity"], fields=[
    field("local_identifier", "char",
          "The v1 epochid string ('epoch_4126958b19a21a41_...'), PRESERVED as the "
          "handle. REQUIRED: 30 live NDI sites match it by exact_string, and 15 NDI "
          "templates carry the `epochid` superclass whose join it is.",
          non_empty=True)],
    deps=[dep("session_id", "session",
              "The session this recording belongs to.", non_empty=True),
          dep("time_reference_#", "relative_reference",
              "The epoch's own extent. One entry per (clock, extent) pair -- the "
              "real per-clock extents live in "
              "`daqreader_epochdata_ingested.epochtable`, one pair per entry, which "
              "is what makes this family well defined under the #52 uniqueness rule.",
              non_empty=False, multiple=True),
          dep("instrument_id", "entity",
              "The acquisition device this epoch was recorded from. OPTIONAL, and "
              "typed to `entity` rather than `subject`: an epoch's instrument may be "
              "an `acquisition_system`, which is not a subject. Added because a "
              "daqsystem does not own a period of time -- the missing fact was the "
              "recording device, not a misnamed one.",
              non_empty=False)]))
_ep_tier, _ep_path = path_of("epoch")
_ep = load(_ep_path)
for _x in _ep.get("depends_on", []):
    if _x["name"] == "time_reference_#":
        # min 0: an epoch whose clock extents were never recorded is still an
        # epoch, and 11,118 v1 documents are in exactly that state. Per #63 --
        # `mustBeNonEmpty` cannot say this.
        _x["min_count"] = 0
write(_ep_tier, "epoch", _ep)

# ---- #60, defect 3: acquisition_epoch DROPPED the `.vhsb` payload declaration --
# The fourth of V_eta_epoch_plan.md's four defects -- "the `.vhsb` payload was
# dropped" -- which that plan files under "REPAIRS, NOT DECISIONS, and true under
# either option". It is fixed here rather than riding with the dissolution,
# because the dissolution is BLOCKED (#65 -> #67/#32) and this class keeps
# carrying real documents in the meantime.
#
#   NDI template   database_documents/element_epoch.json
#                  "files": { "file_list": [ "epoch_binary_data.vhsb" ] }
#   V_eta          acquisition_epoch  "file": []
#
# `acquisition_epoch` IS `element_epoch` -- RENAME[element_epoch] at line 138 --
# so those documents arrive here, and they arrive CARRYING the file: the
# migrator's own header records the measurement ("corpus B: every element_epoch
# body has `files.file_list = {'epoch_binary_data.vhsb'}` with an ndicloud
# location", +migrators_j/element_epoch.m). So this is the `image_stack` bug in
# its undeclared direction, on a class whose every document trips it.
#
# NOT snake_cased, and that is the whole trap: `universalRenames.m:308` skips the
# structural keys outright (`skip = {'document_class','depends_on','file',
# 'files'}`), so a migrated document reaches the validator still spelling the
# file NDI's way. The literal `file_list` entry is what every other tombstone
# already uses (`spikewaves.vsw`, `data.bin`, `generic_file.ext`, `imageStack`).
#
# The build order matters and is deliberate: `oneepoch` (built further down)
# already declares this same file and its comment says, in its own words, that
# `acquisition_epoch` does not and "this class should not inherit the bug". The
# two now agree, which is correct -- in NDI, `oneepoch`'s ONLY superclass is
# `element_epoch`, so it inherits the declaration there and V_eta must flatten it
# because the rename leaves no such parent to inherit from.
#
# MEASURED, sweeping every NDI template against its V_eta home THROUGH the
# RENAME map -- which is the step that hid this one, exactly as it hid
# `element_epoch` -> `acquisition_epoch` from check_tombstones before that tool
# learned to read renames:
#
#     DENOMINATOR: 91 NDI templates on origin/main; 243 V_eta classes, 21
#                  declaring a file; 64 NDI classes have a V_eta home
#                  (read "242 / 19" until 2026-08-11; the ensemble build added
#                  a file declaration and image_stack was restored. The same
#                  counter is quoted in testFileList.m -- re-derive it, do not
#                  copy it, which is how the pair drifted together.)
#     MISMATCHES: 5 -- acquisition_epoch (THIS), ensemble, image (all three
#                  undeclared), jrclust_clusters (declared, no template), and
#                  `oneepoch`, which is a FALSE POSITIVE: NDI declares the file
#                  on its parent, so a chain-resolved read gives
#                  `epoch_binary_data.vhsb` and V_eta's flattened declaration is
#                  already right. The other three are other families' classes
#                  and are REPORTED, not touched.
#     SINCE: `ensemble` was fixed with its own family (#29, TEAM-SIGN-OFF
#                  [ensemble] jess 2026-08-06) -- `neuron_names.txt`, declared
#                  where the class is written, further down this file. `image`
#                  and `jrclust_clusters` remain reported and untouched, and
#                  check_tombstones --enforce-files still names them.
_ae_tier, _ae_path = path_of("acquisition_epoch")
_ae = load(_ae_path)
_ae["file"] = [{"name": "epoch_binary_data.vhsb",
                "documentation":
                    "The element's samples for this epoch, written by"
                    " ndi.element.timeseries.addepoch. NDI's OWN file_list entry"
                    " verbatim, NOT snake_cased -- universalRenames skips the"
                    " `file`/`files` keys, so a migrated document still carries"
                    " this spelling. Under the signed #60 model this payload"
                    " becomes a `sampled_body`; until that lands (blocked on"
                    " #65 -> #67/#32) the bytes stay here and must be"
                    " DECLARED, or every document carries an undeclared file."}]
# ---- the THIRD axes declaration folds into the one entry --------------------
# Signed addendum section 5. This one carried the WORST of the three shapes:
# {name, kind, length, regularity, spacing, unit, sample_rate}, where
# `sample_rate` is `spacing` inverted -- a FREQUENCY stating the same fact that
# `sample_time.dt` states as a DURATION. That is the "fourth spelling" the
# plan's ground-truth section counts, and the team's words were: every one
# carries the regularity flag and an origin, NONE carries `sample_rate`.
#
# NO LOCKSTEP MIGRATOR CHANGE IS NEEDED HERE, AND THAT IS MEASURED RATHER THAN
# ASSUMED -- it is the difference between this declaration and
# `image.value.axes`, which does have a live writer. `axes` is a V_zeta
# INVENTION: NDI's own `element_epoch` template declares exactly two fields, and
# neither is this one.
#
#     $ python3 -c "import json; c=json.load(open(
#           'schemas/V_eta_ndi_ground_truth.json'))['classes']
#       print([f['name'] for f in c['element_epoch']['fields']])"
#       ['epoch_clock', 't0_t1']
#       DENOMINATOR: 91 NDI class(es) in the ground truth artifact
#
# So no did_v1 document can carry an `axes` block, and the only V_eta-path
# handler of the class -- `migrators_j/element_epoch.m`, which renames the block
# wholesale (`v2Body.acquisition_epoch = v2Body.element_epoch`) -- authors no
# fields. A passthrough cannot produce what the source never had. The one writer
# of the old shape, `migrators_i/image_stack.m`, is on the V_zeta path only
# (`v1_to_v2.m` selects `migrators_i.` for target V_zeta and `migrators_j.` for
# V_eta), so it never reaches this class in a V_eta run.
_ae_fields = [f for f in _ae["fields"] if f["name"] != "axes"]
_ae_fields.append(
    field("axes", "structure",
          "Index dimensions of this epoch's data, in array order: axes[k] IS "
          "array dimension k. Time is an ordinary axis. Empty for a bare "
          "scalar.",
          non_empty=False, scalar=False, blank=[],
          sub_fields=axis_subfields()))
_ae["fields"] = _ae_fields
write(_ae_tier, "acquisition_epoch", _ae)

# ---- #59 / file navigation: MINT `epoch_file_pattern` + `acquisition_system` ----
# Both SIGNED in V_eta_daq_family_decisions.md (two TEAM-SIGN-OFF lines, one per
# family: "file navigation" jess 2026-08-06, "daq configuration" jess 2026-08-08).
#
# SCHEMA HALF ONLY, and that is safe here in a way it is NOT for the rest of this
# cluster. These two classes are ADDITIVE -- nothing emits them yet, so no corpus
# document can validate against them and none can be made hollow by them. The
# DESTRUCTIVE half of the same decision (dissolving daqreader into `software`,
# retiring `filenavigator`/`daqsystem`) must ship WITH its migrators: deleting a
# source tombstone ahead of its migrator is what put 2,484 corpus-B documents in
# quarantine when the epoch family landed.
#
# ON THE #37 GATE, re-read before building rather than taken from the summary.
# The condition in the plan is an OR, not a block: "Either #37 lands first, or the
# first corpus run checks those five edge names BY NAME in the silentLoss output
# rather than trusting quarantine=0." That hazard is a MIGRATOR emitting an
# unpopulated edge, which cannot occur while no migrator exists. The escape branch
# is also now cheap: silentLoss reports empty required edges by name and the census
# digest renders them, so the names below are watchable the moment a migrator
# does land. They are: software_id (on THREE classes since 2026-08-12 --
# `epoch_file_pattern`, `acquisition_metadata_reader` AND `acquisition_system`;
# this line said "both" while the count was two), reader_id,
# epoch_file_pattern_id, acquisition_metadata_reader_#.
#
# `epoch_file_pattern` is where epoch identity ENTERS THE ARCHIVE. Of 1,002 NDI .m
# files exactly two mint an epoch id, and the real one is
# `ndi.file.navigator.m:271` (`id = ['epoch_' ndi.ido.unique_id()]`, written beside
# the files); everything downstream inherits it. The two v1 parameter strings were
# EVAL'd; they become declared pattern lists (T14: structure is declared, not
# conventional). The `#` in {'#\.rhd\>', '#\.tsv\>'} is load-bearing -- files
# sharing an unknown common stem are ONE epoch.
write("stable", "epoch_file_pattern", doc("epoch_file_pattern", ["base"], fields=[
    # `string`, NOT `char`. A LIST-VALUED FIELD CANNOT BE `char`:
    # +did2/+schema/cache.m:965-970 accepts only a char array or a
    # SCALAR string for `char`, while the `string` branch
    # (cache.m:971-1001) was written to accept the cell-of-chars
    # MATLAB's jsondecode produces for a JSON array. Declared `char`,
    # every multi-pattern navigator QUARANTINES on typeMismatch.
    field("data_file_pattern", "string",
          "Which files comprise ONE epoch, as declared patterns "
          "({'#\\\\.rhd\\\\>', '#\\\\.tsv\\\\>'}). PARSED, never eval'd: the v1 "
          "form was a string handed to eval. `#` matches an unknown common stem, "
          "so a group of files sharing it is one epoch.",
          scalar=False),
    field("epoch_map_pattern", "string",
          "Which of the epoch's files is the probe-map file "
          "({'(.*)epochprobemap.ndi'}). Same parsed-not-eval'd rule.",
          scalar=False),
    field("epoch_map_format", "char",
          "How to parse the probe-map file "
          "('ndi.epoch.epochprobemap_daqsystem').")],
    deps=[dep("software_id", "software",
              "The implementation that applies this rule (the v1 filenavigator "
              "class name became an edge, not a string field).",
              non_empty=False)]))

# `acquisition_system` is the recording rig. `⊂ entity`, NOT `⊂ base`, so
# `epoch.instrument_id -> entity` reaches it; it sits beside `software` and
# `session`. It is NOT `⊂ subject` -- T1's bare subject is what statements are
# ABOUT, and a rig is what does the recording.
#
# base.name is PRESERVED and load-bearing: it is THE JOIN KEY. `daqsystem.base.name`
# is matched by strcmpi in `+ndi/+daq/system.m:229` (probe -> device attribution),
# named in every `syncrule.parameters.daqsystem1_name`, and queried by exact_string
# in `+ndi/+time/syncgraph.m:404-408`. A depends_on sweep saw none of that.
#
# ---- #59, THE SECOND SOFTWARE EDGE: `software_id` (team, 2026-08-12) --------
# DECIDED BY jess@walthamdatascience.com on 2026-08-12, option A of the two the
# daqsystem migrator's header put up: "`acquisition_system` gains a SECOND
# software edge so `ndi_daqsystem_class` has a home." Recorded in prose here
# because Claude may not write a signature line; the signed decision document
# for this family is V_eta_daq_family_decisions.md.
#
# WHAT IT CLOSES. The signed model (V_eta_daq_family_decisions.md:265) says "The
# class NAMES all move to deduplicated `software` entities" -- and it gave three
# of the four an edge to move along while `acquisition_system` declared
# `"fields": []` and one software edge, `reader_id`, already spoken for by the
# daqreader. So `daqsystem.ndi_daqsystem_class` had nowhere to land, and
# migrators_j/daqsystem.m GUARDED its whole fold on that: every real did_v1
# document passed through unconverted rather than lose the field.
#
# THE FIELD IS NOT DEAD WEIGHT, and the reason a literal grep says otherwise is
# that its name is CONSTRUCTED at the reader:
#
#     +ndi/+database/+fun/ndi_document2ndi_object.m:38-42
#         obj_struct = getfield(doc.document_properties, obj_parent_string);
#         obj_string = getfield(obj_struct,['ndi_' obj_parent_string '_class']);
#         o = eval([obj_string '(ndi_session_obj, ndi_document_obj);']);
#
# reached from +ndi/session.m:167-169 (daqsystem_load). It is the
# object-reconstruction key, and the SAME generic site reads
# `ndi_daqreader_class`, `ndi_daqmetadatareader_class` and
# `ndi_filenavigator_class` -- the three that already have their edge.
#
# WHY THE NAME IS `software_id` AND NOT A NEW WORD. T11: "One canonical spelling
# per concept." The concept here -- THIS document's own implementation class,
# folded to a `software` entity -- is already spelled `software_id` on both
# siblings minted in this same block, from the same signed decision:
#
#     epoch_file_pattern.software_id           <- ndi_filenavigator_class
#     acquisition_metadata_reader.software_id  <- ndi_daqmetadatareader_class
#
# (and on `method_parameters` / `subject_interaction` for the same "the software
# that did this" sense). Minting `system_software_id` or `implementation_id`
# would be a SECOND spelling of one concept, which is the thing T11 forbids;
# `implementation`/`system_software` are also container-altitude words T13 warns
# off, and `application` is ruled out by name in T13.
#
# AND THE PAIR READS COHERENTLY, which is the test the two edges have to pass
# together, because both point at `software`:
#
#     software_id  the rig's OWN implementation class -- what this document IS
#                  ('ndi.daq.system.mfdaq' / 'ndi.daq.system.image')
#     reader_id    a DIFFERENT component's identity, reached through v1's
#                  `daqreader_id` -- what this rig acquires THROUGH
#
# `reader_id` names a role because it points OUT at another component; the
# unqualified `software_id` is this class's own implementation, exactly as on
# the two siblings. That is a learnable rule, not two ad-hoc names.
#
# WHY OPTIONAL, AND THIS IS THE PART THAT COSTS DOCUMENTS IF IT IS WRONG.
# #37 RequiredDependencies is ARMED BY DEFAULT (DID-matlab
# +did2/+schema/cache.m:967-968, `~envFlagIsOff('DID_ENFORCE_REQUIRED_DEPENDENCIES')`),
# so a REQUIRED edge that cannot always be populated now QUARANTINES the
# document rather than passing silently. It cannot always be populated:
#
#     $ git show origin/main:src/ndi/ndi_common/schema_documents/daq/\
#           daqsystem_schema.json
#         { "name": "ndi_daqsystem_class", "type": "string",
#           "default_value": "", ... }        <- NO "mustbenotempty"
#
# NDI's own schema lets the field be empty, and jSoftware returns [] for an
# empty name ("no identity -> no entity"), so the fold has a real path on which
# there is no software document to point at -- the path every daqsystem test in
# testMigratorsJDaqConfiguration.m has been driving while the guard stood.
# `non_empty=False` matches all three edges already on this class, and matches
# `software_id` on both siblings.
write("stable", "acquisition_system", doc("acquisition_system", ["entity"],
    deps=[dep("software_id", "software",
              "The implementation of the acquisition system itself (v1's "
              "`daqsystem.ndi_daqsystem_class`, e.g. 'ndi.daq.system.mfdaq', "
              "became an edge rather than a string field -- the same fold "
              "`epoch_file_pattern` and `acquisition_metadata_reader` make of "
              "their own class names). It is the object-reconstruction key read "
              "at +ndi/+database/+fun/ndi_document2ndi_object.m:38-42 through a "
              "CONSTRUCTED field name, so no literal grep finds the reader. "
              "Distinct from `reader_id`, which names a DIFFERENT component.",
              non_empty=False),
          dep("reader_id", "acquisition_reader",
              "The reader this system acquires through. REPOINTED from `software` "
              "to `acquisition_reader`: the parenthesis here used to read \"it is "
              "the only one of the four with no parameters of its own\", and that "
              "was the error -- `reader_string` is a parameter of its own, and "
              "pointing straight at `software` left it homeless (both PRED "
              "`daqreader_ndr` documents carry one). The edge now has the same "
              "shape as `acquisition_metadata_reader_#`: a reader class that owns "
              "its configuration and points on at the `software` that implements "
              "it.",
              non_empty=False),
          dep("epoch_file_pattern_id", "epoch_file_pattern",
              "The rule that decides which files form one epoch on this system.",
              non_empty=False),
          dep("acquisition_metadata_reader_#", "acquisition_metadata_reader",
              "The companion-spreadsheet reader(s), if any.",
              non_empty=False, multiple=True)]))

# ---- #32 BINDING GOVERNANCE, increment 1: bind the three pivot fields -------
# TEAM DECISION 2026-08-10, in two parts:
#   "preferred first, strength on the field"   -- the staging and the authority
#   "C for now"                                -- strength ONLY, no admissible
#                                                 set named yet
#
# WHY THESE THREE. `term.value` is bound `keyed_by: variable`, so the admissible
# values of every term depend on `variable` -- and `variable` itself carried
# `constraints = {}`. The key the whole system pivots on was the one thing
# nothing required to resolve, which is how the same concept can be spelled two
# ways in two datasets and store as two different facts (the drift test in
# V_eta_openminds_family_record.md Part 3). `method` and `purpose` are the same
# shape: unbound ontology_term fields that T8 says the registry governs.
#
# WHY `preferred` AND NOT `required`. Nothing measures how many real documents
# would fail a required binding, and flipping blind on a 0-quarantine gate is
# what produced 2,484 corpus-B quarantines when the epoch schema half landed.
# `preferred` costs nothing today, states the intent declaratively, and makes
# the exposure countable BEFORE anyone chooses to fail on it.
#
# WHY NO `ontology`/`root_node`/`values` YET (option C). The meta-schema offers
# exactly two ways to name an admissible set -- an ontology subtree, or a static
# enumeration -- and NEITHER is decided for these fields. The registry's
# `subject_statement_bindings` rows answer a DIFFERENT question ("given
# variable = species, what may the VALUE be"), not what `variable` itself may
# be. Inventing a root node here would be the fabrication this repair track
# exists to remove, so the binding declares its strength and stops.
#
# ---- #32 BINDING GOVERNANCE, increment 2: give the three a SHAPE -----------
# Increment 1 (above) declared a strength and stopped, because neither of the
# two ways the meta-schema offered to name an admissible set was decided. That
# left `binding: {strength: preferred}` -- a declaration with NOTHING behind it,
# which check_binding_governance.py B9 counts as unenforceable, correctly.
#
# `node_form: curie` is the third thing a binding can say, and it is the one
# that needs no ontology: the bound value's `node` must be a syntactically
# well-formed CURIE (`prefix:local`). It does NOT say the prefix expands, and it
# does NOT say the term exists -- MEMBERSHIP is still out of scope, because the
# admissible value set for `variable` lives in NDIC.txt, which moved to
# VH-Lab/ndi-ontology-matlab (commit 2c19bf24c), a repository this work did not
# have. So this is the shape half of "a resolvable term reference", declared
# separately from the membership half so that adding the second later does not
# have to relitigate the first.
#
# STRENGTH STAYS `preferred`, DELIBERATELY, AND THE COST IS NOT ZERO. The
# registry's OWN rows carry `"variable": {"node": "", "name": "species"}` -- an
# empty node on all five subject_statement_bindings rows -- so a `required`
# node_form binding would reject the vocabulary file that defines the binding.
# That is positive evidence of a non-zero cost, not an absence of evidence, and
# it is why the DID-matlab side ships DISARMED as well: cache.m only rejects
# when the binding says `required`, and no binding says `required` AND
# `node_form` today. Two independent brakes, either of which alone keeps the
# corpus green.
#
# WHAT `binding` IS AND IS NOT, RESTATED because the previous version of this
# paragraph said flatly "`binding` is not enforced" and that sentence would now
# be false. DID-matlab did2.schema.cache/validateConstraints gained a `binding`
# case (increment 2, same commit as this) which rejects with three distinct ids
# -- bindingValueMissing / bindingNodeMalformed / bindingValueNotInSet. It is
# reached ONLY when did2.schema.cache.strictMode('BindingConformance') is armed,
# and that switch is DISARMED by default (DID_ENFORCE_BINDING_CONFORMANCE=1
# arms it), so on today's tree the case returns before reading anything. NOTHING
# MATLAB-SIDE HAS BEEN EXECUTED -- there is no MATLAB in the environment this
# was written in -- so read that as the declared design, not as a measured
# behaviour.
_BIND_PREFERRED = [
    ("subject_statement", "variable"),
    ("subject_interaction", "method"),
    ("interaction_purpose", "purpose"),
]
for _cls, _fname in _BIND_PREFERRED:
    _t, _p = path_of(_cls)
    if _t is None:
        raise SystemExit(f"#32: no V_eta schema named {_cls!r}")
    _d = load(_p)
    _hit = [f for f in _d.get("fields", []) if f["name"] == _fname]
    if not _hit:
        raise SystemExit(f"#32: {_cls} declares no field {_fname!r}")
    _f = _hit[0]
    if _f["type"] != "ontology_term":
        raise SystemExit("#32: {}.{} is {!r}, not ontology_term".format(_cls, _fname, _f["type"]))
    _f.setdefault("constraints", {})["binding"] = {"strength": "preferred",
                                                   "node_form": "curie"}
    write(_t, _cls, _d)

# ---- #56: `strain` is an ENTITY, and term_assertion may point at one --------
# Team call 2026-08-05 (V_eta_openminds_family_record.md Part 6). `entity` was
# chosen over a plain `base` document because it supplies `global_identifier` as
# a REPEATABLE {scheme, value}: openMINDS spends three slots on strain
# identifiers (ontologyIdentifier, digitalIdentifier -> RRID, alternateIdentifier
# -> MGI/RGD) and the four schemes in our data (WBStrain, NCIT, RRID, EMPTY) are
# exactly what one repeatable pair subsumes. Choosing `base` would have meant
# re-declaring that concept locally and losing "find anything by external
# identifier" as one uniform query.
#
# The three REQUIRED fields are required BY openMINDS, not by us.
# `global_identifier` stays OPTIONAL because Dabrowska's Cre lines carry no
# identifier at all -- the schema must not demand what the writer never produces.
#
# NOTE `ontology_term` here is the FIELD TYPE (the {node, name} cell), NOT the
# `term` data_type class. Those are different things and the record says the
# distinction was confused earlier.
write("stable", "strain", doc("strain", ["entity"], fields=[
    field("name", "char",
          "The strain's name as the source gives it (e.g. 'Escherichia coli "
          "OP50', 'ArcCreERT2 x eYFP').", non_empty=True),
    field("species", "ontology_term",
          "The species this strain belongs to. Bound to NCBITaxon. REQUIRED by "
          "openMINDS. V_eta deliberately does NOT adopt openMINDS's polymorphic "
          "specimen.species slot -- species and strain stay SIBLING assertions "
          "on a subject (record Parts 4 and 5).", non_empty=True),
    field("genetic_strain_type", "ontology_term",
          "wildtype | transgenic | knockout | ... REQUIRED by openMINDS, and it "
          "lives HERE rather than on the subject: ~2,365 `genetic strain type` "
          "assertions move off subjects onto the strain document. Unnormalised "
          "across writers ('wildtype' vs 'wild type') -- the binding work has "
          "to reconcile that.", non_empty=True),
    field("description", "char", "Free-text description as the source gives it.",
          non_empty=False),
    field("phenotype", "char", "Observable phenotype, where the source states one.",
          non_empty=False),
    field("breeding_type", "ontology_term",
          "openMINDS BreedingType, where stated.", non_empty=False),
    field("disease_model", "ontology_term", "Disease or disease model this strain "
          "models. No writer populates it yet; the slot exists so it has "
          "somewhere to land instead of being dropped.",
          non_empty=False, scalar=False),
    field("laboratory_code", "char",
          "ILAR laboratory code, where the source gives one.", non_empty=False,
          constraints={"pattern": "^$|^[A-Z]([a-z]?)+$"}),
    field("stock_number", "structure", "Vendor stock/catalogue number.",
          non_empty=False, sub_fields=[
              subfield("vendor", "char", "The vendor or repository."),
              subfield("code", "char", "Its catalogue/stock code."),
          ]),
    # `string` not `char`, same reason as epoch_file_pattern's two pattern
    # lists: a cell-of-chars cannot validate against the `char` branch.
    field("synonym", "string", "Other names the source uses for this strain.",
          non_empty=False, scalar=False),
    LOCAL_ID_OPT],
    deps=[dep("background_strain_#", "strain",
                    "The strain(s) this one was derived from -- a RECURSIVE "
                    "self-edge forming a DAG, so a cross names both parents and "
                    "a shared background is stored ONCE rather than duplicated "
                    "into every descendant. A root strain has none.",
              non_empty=False, multiple=True)]))
_st_tier, _st_path = path_of("strain")
_st = load(_st_path)
for _x in _st.get("depends_on", []):
    if _x["name"] == "background_strain_#":
        # 0..2: a root strain has no parent; the real Hunsberger F1 cross names
        # exactly two. Declared per #63 -- `mustBeNonEmpty` cannot say this.
        _x["min_count"] = 0
        _x["max_count"] = 2
write(_st_tier, "strain", _st)

# The edge, on the ASSERTION -- not on `subject` (record Part 5: most subjects
# are devices). The assertion KEEPS its inline `term.value = {node, name}` and
# GAINS this edge: the inline value is a complete fact on its own (a CURIE names
# a real thing), 115 strains carry no identifier and may warrant no document, and
# the value is the statement's CONTENT rather than a join key. Dropping it would
# make `variable: strain` resolve two ways depending on whether a pedigree
# happened to exist -- drift. `epoch` went the OTHER way for the opposite
# reasons; neither is a precedent for the other.
_ta_tier, _ta_path = path_of("term_assertion")
_ta = load(_ta_path)
if not any(x["name"] == "strain_id" for x in _ta.get("depends_on", [])):
    _ta.setdefault("depends_on", []).append(
        dep("strain_id", "strain",
            "OPTIONAL: the strain document this assertion's term names, when one "
            "exists. Named for its target per the convention measured across 97 "
            "dependency declarations (45 distinct names, all `<target>_id`) -- "
            "NOT a generic `term_id`.", non_empty=False))
write(_ta_tier, "term_assertion", _ta)

write("stable", "publication", doc("publication", ["entity"], fields=[
    field("title", "char", "Publication title."),
    field("publication_date", "date",
          "Publication date. PARTIAL PRECISION IS THE POINT: a publication may "
          "be recorded as a year, a year-month or a full date, and `date` "
          "accepts all three -- which is why this is not a `timestamp`. Renamed "
          "from the bare `date` 2026-08-13: `date` alone names the KIND of value "
          "and not the fact, and `<noun>_<kind>` is this schema's measured house "
          "style (13 `_name`, 11 `_time`, 10 `_type`, 5 `_id`; 0 bare "
          "participles in 472 field names).",
          non_empty=False),
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
    field("release_date", "date", "Release date "
          "(openMINDS DatasetVersion.releaseDate). `date`, not `timestamp`: a "
          "release is dated, not instantaneous, and openMINDS supplies no time "
          "of day to put in one. The NAME is already `<noun>_<kind>` and is "
          "unchanged -- it is the field the naming survey measured the house "
          "style against.", non_empty=False),
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

# ---- TEAM-SIGNED 2026-08-13 ------------------------------------------------
# THREE INVENTED FIELDS GO. NDI's template declares exactly one:
#     git show origin/main:src/ndi/ndi_common/database_documents/session.json
#       "session": { "reference": "" }
# No `type`, no `date`, no `purpose`, and ndi.session.dir writes only
# `session.reference`. They came from the V_zeta snapshot, so no writer can
# fill them -- the `daqreader.file_extension` pattern, deleted this month for
# exactly this reason.
_gone = {"type", "date", "purpose"}
_before = len(sess.get("fields", []))
sess["fields"] = [f for f in sess.get("fields", []) if f["name"] not in _gone]
if _before - len(sess["fields"]) != len(_gone):
    raise SystemExit("build_v_eta: session should have declared all of %s; "
                     "removed %d" % (sorted(_gone), _before - len(sess["fields"])))

# `reference` -> `local_identifier`, REQUIRED. `subject` and `epoch` both name
# this same fact `local_identifier` and both require it; session was the only
# entity using a different word for it, AND carried a second, optional
# `local_identifier` besides. One slot, one name, matching its siblings.
sess["fields"] = [f for f in sess["fields"] if f["name"] != "local_identifier"]
_ref = [f for f in sess["fields"] if f["name"] == "reference"]
if len(_ref) != 1:
    raise SystemExit("build_v_eta: session must declare exactly one "
                     "`reference`; found %d" % len(_ref))
_ref[0]["name"] = "local_identifier"
_ref[0]["mustBeNonEmpty"] = True
_ref[0]["documentation"] = (
    "Human-facing handle for this session, unique within its dataset. Renamed "
    "from `reference` 2026-08-13 to match `subject` and `epoch`.")
write("stable", "session", sess)

# openminds_import: REMOVED 2026-07-30 (team sign-off), REVERSING the earlier
# "PERSIST as (7) provenance, maturity draft" call recorded in V_eta_tenet_audit.md.
#
# The reversal is on the evidence, not a change of taste:
#   * NOTHING EMITS IT. Zero documents, no migrator, no importer, not even the
#     openMINDS round-trip CI test. It has never validated a document, which is
#     exactly the "persisting is right ONLY paired with a scheduled emitter" caveat
#     the original audit attached to its own decision -- and no emitter was ever
#     scheduled.
#   * It is a V_eta INVENTION, not a did_v1 source (absent from the coverage ledger;
#     provenance origin = V_eta), so removing it strands no existing data.
#   * Nothing references it.
#   * Its content is arguably provenance of a CONVERSION -- crosswalk_version is
#     "which version of a translation program ran", which is what the `software`
#     entity + software_id edge already model (R1). Keeping a bespoke class is a
#     second representation of one fact.
#
# Re-add when there is an import path to stamp it. At that point the open question
# is whether it should be a class at all or a software reference, and having a real
# emitter is what will answer it. The one field with no obvious existing home is
# `source_iri`; `global_identifier` with scheme='IRI' is the candidate.

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
#   ensemble -- PASSTHROUGH-retained in pass 1, and the grain is no longer "a separate
#     decision": TEAM-SIGN-OFF [ensemble] jess 2026-08-06 settled it (group subject,
#     epoch-scoped `member_of` edges, rebuildable cache). What stays passthrough is the
#     MAP document, deliberately -- V_eta_ensemble_plan.md deferred task 5: "until then
#     it stays a green passthrough -- do NOT phase-8-delete early", because the
#     verify-before-delete gate (0 stranded per-neuron trains) has not run on a corpus.
#     Which makes this tombstone LOAD-BEARING: it is the only thing standing between a
#     real map document and a quarantine, so it must state what the document CARRIES.
#     See the restatement below.
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

# ---- #29 ensemble: the two things the map document CARRIES and the tombstone did not
# declare. Both measured by tools/check_tombstones.py before this change:
#
#     LOSSY  passthrough ensemble
#         real dependencies not declared: neuron_id
#     FILE   passthrough ensemble
#         real files the tombstone does NOT declare: neuron_names.txt
#
# (1) `neuron_id_#` -- THE ROSTER, AND THE REASON THE PLAN'S OWN PREMISE WAS WRONG.
# V_eta_ensemble_plan.md migration-constraint 1 said the neuron ids lived only inside
# `neuron_names.txt`, so `member_of` needed file-byte access and therefore the NDI
# second pass. The ids are `depends_on` EDGES on the map document, written in column
# order by the same loop that writes the names:
#
#   git show origin/main:src/ndi/+ndi/+element/ensemble.m        (buildMapDoc)
#     272   mapdoc = mapdoc.set_dependency_value('element_id', obj.id());
#     273   mapdoc = mapdoc.set_dependency_value('element_epoch_id', epochdoc.id());
#     274   for i = 1:numel(neuron_ids)
#     275       mapdoc = mapdoc.add_dependency_value_n('neuron_id', neuron_ids{i});
#     277   mapdoc = mapdoc.add_file('neuron_names.txt', names_tempfile);
#
#   git show origin/main:src/ndi/ndi_common/schema_documents/ensemble/ensemble_schema.json
#     "depends_on": [
#         { "name": "element_id",       "mustbenotempty": 1},
#         { "name": "element_epoch_id", "mustbenotempty": 1},
#         { "name": "neuron_id",        "mustbenotempty": 0}
#     ]
#
# WHY IT SURVIVED: the TEMPLATE
# (database_documents/ensemble/ensemble.json) declares element_id and element_epoch_id
# and NOTHING ELSE -- `neuron_id` appears only in the SCHEMA and the WRITER. That is the
# ground-truth rule (*where template and WRITER disagree, the WRITER wins*) firing on a
# divergence inside NDI's own pair, and it is why check_tombstones, which reads the
# TEMPLATE, could not have raised this row on its own -- it raised it because
# ndi_ground_truth.py reads the schema too.
#
# Declared as a `_#` FAMILY because `add_dependency_value_n` appends `neuron_id_1`,
# `neuron_id_2`, ... (DID-matlab +did/document.m add_dependency_value_n), so the suffix
# index IS the column index. min_count 0 (below, in _EDGE_COUNTS): NDI's own schema says
# "mustbenotempty": 0, and the family flag is cleared there for the reason #63 records --
# a missing instance is not a blank one.
#
# TYPED TO `subject`, matching `element_id` directly above: a neuron is an element, and
# `migrators_j.element` promotes an element to a subject with its id PRESERVED, so the
# stored id still resolves after migration. must_refer is existence-only, never
# type-checked, so this is declarative either way.
#
# DECLARING THIS CANNOT QUARANTINE ANYTHING. `+did2/+schema/cache.m` allows `depends_on`
# wholesale as a top-level key and never checks individual dependency NAMES; the only
# edge check is #37's required-edges gate, which keys on mustBeNonEmpty and excludes
# numbered families. So before this change the edges passed through UNDECLARED and
# silently -- the shape that let six classes reach 100% empty required edges -- and after
# it the schema simply states the fact.
#
# (2) `neuron_names.txt` -- the file block, the `image_stack` shape exactly. NDI declares
# it in BOTH halves of its pair and the writer attaches it (:277, above):
#
#   database_documents/ensemble/ensemble.json  "files": {"file_list": ["neuron_names.txt"]}
#   schema_documents/ensemble/ensemble_schema.json
#                                              "file": [{"name": "neuron_names.txt",
#                                                        "mustbenotempty": 1}]
#
# The name is NDI's OWN spelling and is NOT snake_cased on the way through:
# universalRenames.m:308 skips the structural keys outright
# (`skip = {'document_class','depends_on','file','files'}`), so a passed-through document
# reaches validation still carrying it. `did2.validate.fileList` compares by exact strcmp
# (fileList.m:93,99). A file divergence never quarantines -- which is why it is dangerous:
# the failure mode is a payload that is stranded or unfindable while every gate stays
# green.
#
# NOT DECLARED HERE, deliberately: the second pass's `member_of` / `derived_from` edges.
# They are `directed_relation` documents, not fields of this class, and pass 1 must not
# emit an edge it cannot resolve.
_ensemble = doc("ensemble", ["base", "epochid", "app"],
                deps=[dep("element_id", "subject",
                          "The recording element (a subject in V_eta) the ensemble was "
                          "computed from."),
                      dep("element_epoch_id", "acquisition_epoch",
                          "The epoch over which the ensemble was defined.",
                          non_empty=False),
                      dep("neuron_id_#", "subject",
                          "The constituent neurons, in COLUMN ORDER -- the per-epoch "
                          "roster of the ensemble. NDI writes these with "
                          "`add_dependency_value_n` (+ndi/+element/ensemble.m:274-276), "
                          "so the `_1`/`_2` suffix is the column index into the combined "
                          "marked-point-process binary, and `neuron_names.txt` carries "
                          "the NAMES of this same roster rather than the roster itself. "
                          "Typed to `subject` because a neuron is an element and "
                          "`migrators_j.element` promotes an element to a subject with "
                          "its id PRESERVED. This is what the NDI second pass "
                          "(ndi.migrate.internal.ensembleMembership) reads to mint the "
                          "signed epoch-scoped `member_of` edges; the plan's original "
                          "premise that it had to read the file bytes was WRONG.",
                          non_empty=False, multiple=True)],
                fields=[
                    field("ensemble_name", "char", "Name of the neuron ensemble."),
                    field("value_type", "char",
                          "Type of the ensemble's value/activity representation.",
                          non_empty=False),
                    field("value_description", "char",
                          "Free-text description of the ensemble value.",
                          non_empty=False),
                    field("num_neurons", "integer",
                          "Number of neurons in the ensemble. DERIVABLE from the "
                          "`neuron_id_#` family and dropped by the signed model when the "
                          "map document dissolves (T11); restated here because a "
                          "PASSTHROUGH document still carries it and an undeclared field "
                          "quarantines."),
                    field("clocktype", "char",
                          "Clock type for the ensemble's epoch times.", non_empty=False),
                ])
_ensemble["file"] = [{
    "name": "neuron_names.txt",
    "documentation":
        "The constituent neuron NAMES, one per line, in the same column order as the "
        "`neuron_id_#` family -- written by +ndi/+element/ensemble.m:255-256 and attached "
        "at :277. NDI's OWN file_list entry verbatim, NOT snake_cased: universalRenames "
        "skips the `file`/`files` keys (universalRenames.m:308), so a passed-through "
        "document still carries this spelling and `did2.validate.fileList` compares it by "
        "exact strcmp. The names are `e.elementstring()` of the elements the "
        "`neuron_id_#` edges already point at (+ndi/+fun/+ensemble/load.m), so this file "
        "adds no fact the edges lack -- it is declared because the document CARRIES it, "
        "not because anything needs to read it."}]
write("stable", "ensemble", _ensemble)


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


# ---------- 7b. the demo/mock family: THREE CLASSES COLLAPSE TO ONE ----------
# History, because two reversals landed here in one day. The DELETE call was reversed
# (the grep searched the snake_case name against camelCase NDI, so it could not have
# matched). Reversing it exposed that PASSTHROUGH was not achievable either -- V_eta's
# versions were wholly invented and could not admit a real document:
#
#   NDI  demoNDI ⊂ base       value, FILE filename1.ext   |  V_eta had demo_param1/2, no file
#   NDI  demoNDIMock ⊂ mock, demoNDI                      |  V_eta had ⊂ base only
#   NDI  mock ⊂ base          ismock                      |  V_eta had NO SUCH CLASS
#
# THE COLLAPSE (team, 2026-08-06). `demoNDIMock` has ZERO fields of its own: its entire
# content is "I am a mock demo". That is a FLAG, not a kind of thing -- the same test
# the time_reference collapse turned on, where `mode` stopped being a class axis and
# became "are start/end populated?". A mock voltage_observation would still be a voltage
# observation, so mock-ness is a property of a document, not a species of one.
#
#   3 classes -> 1.  `mock` and `demo_ndi_mock` cease to exist.
#
# NAMES: `demo`, not `demo_ndi`. The framework's own name has no business inside a class
# name in the framework's own schema (T13).
#
# COSTS, recorded rather than glossed:
#   * ndi.calc.example.simple queries ndi.query('','isa','demoNDIMock','') -- that isa
#     has no target once the class is gone. A v1-runtime query against v1 documents, the
#     same category as every other rename, but a real break.
#   * `mock` stops being available as a marker other classes could carry. It had ONE
#     bearer in 91 templates, so a general marker for one user was the anticipatory
#     error we have now made twice; if mock documents are ever to be carried-and-flagged
#     rather than refused at migration, the flag belongs on `base`, not on a parallel
#     hierarchy. That question is open.
#
# `value` is typed from the WRITER, not the template: the template says "" (char) but
# ndi.calc.example.simple sets 5 and 10 and queries with 'exact_number'. Writer wins.
_demo = doc("demo", ["base"], fields=[
    field("value", "double",
          "The demonstration value the example calculator reads "
          "(ndi.calc.example.simple queries demoNDI.value by exact_number). Typed from "
          "the WRITER: the did_v1 template declares char, the writer sets numbers."),
    field("is_mock", "boolean",
          "TRUE when this document is self-test/demonstration data rather than a record "
          "of an experiment. Carried from did_v1 `mock.ismock`, which demoNDIMock held "
          "as a superclass. The ONLY marker separating self-test artefacts from real "
          "data -- ndi.calc.example.simple sets numberOfSelfTests = 2 and writes these "
          "documents against a LIVE session.",
          non_empty=False, blank=False, default=False)])
_demo["file"] = [{
    "name": "filename1.ext",
    "documentation": "Required by the did_v1 demoNDI schema, and inherited by "
                     "demoNDIMock. V_eta had dropped it -- silent file loss."}]
write("stable", "demo", _demo)

# did_v1 demoNDI -> demo, and demoNDIMock -> demo with is_mock TRUE (the migrator sets
# the flag; there is no second class to route to).
for _gone in ("demo_ndi", "demo_ndi_mock", "mock"):
    _t, _p = path_of(_gone)
    if _p and os.path.exists(_p):
        os.remove(_p)


# ---------- 8a. register the `time` CURIE prefix (OWL-Time) ----------
# REPAIR. Increment 1 below binds `relative_reference.value.relation` to OWL-Time
# CURIEs (time:intervalBefore, ...), but `time` was NOT one of the 11 registered
# prefixes, so those CURIEs expanded to nothing -- a binding that LOOKS governed and
# is not, which is worse than a plain enum. Registering it is the fix, and OWL-Time is
# a W3C standard with a stable namespace, so nothing has to be minted.
_curie = load(os.path.join(VETA, "stable", "CURIE_lookups_meta.json"))
_curie["prefixes"]["time"] = {
    "label": "OWL-Time (W3C Time Ontology)",
    "uri_base": "http://www.w3.org/2006/time#",
    "uri_style": "fragment",
    "approximate": False,
    "documentation": "W3C Time Ontology in OWL. Expansion rule: 'time:intervalDuring' "
                     "-> 'http://www.w3.org/2006/time#intervalDuring'. Used by "
                     "relative_reference.value.relation for Allen's thirteen interval "
                     "relations. A W3C Recommendation, so terms are stable and nothing "
                     "needs minting.",
}
with open(os.path.join(VETA, "stable", "CURIE_lookups_meta.json"), "w") as _f:
    json.dump(_curie, _f, indent=2)
    _f.write("\n")


# ---------- 8b. THE TIME-REFERENCE COLLAPSE -- increment 1 (TaskList #65) ----------
# V_eta_time_reference_model_plan.md: eight classes collapse to TWO under the abstract
# `time_reference` root. `origin` (session/epoch/event/utc) is a RELATION -> it becomes
# the `relative_to` edge; `mode` (bounded/relative) is CARDINALITY -> it becomes "are
# start/end populated?". `mode` was not even self-consistent: in the session pair it
# meant with-metric vs without, in the event pair whole-extent vs offset.
#
# INCREMENT 1 IS ADDITIVE ONLY. The eight source classes STAY until the migrators move
# (24 files emit session_relative_reference, 5 emit epoch_bounded_reference, 1 emits
# session_bounded_reference). Deleting them here would red the corpus gate, and the
# project rule is: build the target, move the emitters, then delete the source.

# ---------- #67: the did_clocktype vocabulary, 9 members -> 4 ontology terms ----------
#
# GROUND TRUTH, read from NDI origin/main (NOT from a DID-side schema):
#
#   git show origin/main:src/ndi/+ndi/+time/clocktype.m
#     switch type
#       case {'utc','approx_utc','exp_global_time','approx_exp_global_time',...
#             'dev_global_time', 'approx_dev_global_time', 'dev_local_time', ...
#             'no_time','inherited'}
#
# NINE members, and the 9-member list this binding used to carry was a faithful copy
# of them. The signed time-model walkthrough
# (V_eta_time_reference_model_plan.md:468, TEAM-SIGN-OFF [time_reference],
# jess@walthamdatascience.com / 2026-08-08) cuts it to FOUR:
#
#   CHANGE 4  the `approx_` prefix is mode-in-a-name (T13) hiding a NUMBER in a
#             docstring (T14). approx_utc / approx_exp_global_time /
#             approx_dev_global_time de-encode to the bare clock plus an explicit
#             clock_tolerance { seconds: 5 } on the time_reference ROOT. The
#             migrator supplies the 5 from writer semantics -- transcription.
#   CHANGE 4  `no_time` leaves the value_set: it is an epoch_clock asserting "this
#             thing keeps no time", never a timeline a time is expressed on. Its
#             V_eta translation is NO TIMES => NO REFERENCE -- no document at all.
#   CHANGE 4  `inherited` leaves the value_set: it is a resolution instruction, and
#             `relative_to` already IS that pointer. The plan records this as an
#             ABSENCE-BASED call and asks for a corpus check before the term is
#             dropped for good; leaving it unminted (rather than deleted from NDI)
#             is exactly what that caveat permits.
#
# CHANGE 3 makes `clock` an `ontology_term` -- `relation` beside it already is one,
# and `variable` is one everywhere; a bare char between them was the odd one out.
#
# *** THE NODES ARE STAGED EMPTY, AND THAT IS NOT AN OVERSIGHT. ***
# An NDI-side CURIE for these four would live in the NDIC namespace -- NDI writes
# `['NDIC:' int2str(item.Identifier)]` (+setup/+conv/+marder/temptable2stimulusparameters.m:25,
# +setup/+stimulus/+vhlab/add_stimulus_approach.m:51) against a controlled-vocabulary
# table. That table (`ndi_common/controlled_vocabulary/NDIC.txt`) was REMOVED from
# NDI-matlab in commit 2c19bf24c ("Remove NDIC.txt controlled vocabulary (moved to
# ndi-ontology-matlab)") and its last in-tree revision contains NO clock terms. So the
# authority that assigns NDIC identifiers is not in any repository in scope, and an
# invented integer would be a fabricated CURIE -- the precise failure mode this
# project's operating rules exist to prevent. The terms are therefore staged as
# `{node: '', name: <NDI's own string>}`, which is the ESTABLISHED practice
# (V_eta_clock_alignment_cluster_plan.md §5, and 33 live migrator sites), and the
# backlog is counted -- see tools/check_empty_ontology_nodes.py.
#
# `values` are NodeRefs, not bare strings, because the field is now `ontology_term`:
# a bare "utc" beside a `{node, name}` cell cannot say which half it is. That shape is
# the one the registry already documents for a term-valued admissible set
# ("values are ontology-term NodeRefs, not bare strings",
# tests/test_veta.py::test_binding_examples_well_formed).
_CLOCK_TERMS = [
    {"node": "", "name": "utc"},
    {"node": "", "name": "dev_local_time"},
    {"node": "", "name": "dev_global_time"},
    {"node": "", "name": "exp_global_time"},
]

_CLOCK_BINDING = {
    "binding": {"root": "did_clocktype", "expansion": "value_set",
                "values": _CLOCK_TERMS,
                "strength": "required", "source": "value_set"}}

# The old `relation` was a bare char enum covering 6 of Allen's 13 interval relations,
# with `concurrent_with` ambiguous between equals and overlaps. It becomes an
# ontology_term bound to OWL-Time, all thirteen.
_OWL_TIME_BINDING = {
    "binding": {"root": "owl_time_interval", "expansion": "value_set",
                "values": ["time:intervalBefore", "time:intervalAfter",
                           "time:intervalMeets", "time:intervalMetBy",
                           "time:intervalOverlaps", "time:intervalOverlappedBy",
                           "time:intervalStarts", "time:intervalStartedBy",
                           "time:intervalDuring", "time:intervalContains",
                           "time:intervalFinishes", "time:intervalFinishedBy",
                           "time:intervalEquals"],
                "strength": "required", "source": "value_set"}}

# ---------- #65 INCREMENT 2: the SIGNED walkthrough shape ----------------------
# V_eta_time_reference_model_plan.md:468, TEAM-SIGN-OFF [time_reference],
# jess@walthamdatascience.com / 2026-08-08. Increment 1 (above) built the two target
# classes from the plan's ORIGINAL sections; the walkthrough section at the BOTTOM of
# that file supersedes them, and the plan says so in its own words ("Read this section,
# not the ones above"). Increment 2 moves the built shape onto the signed one:
#
#   CHANGE 1  `end` becomes `duration`. ANCHOR and EXTENT are independent facts -- the
#             team's case is "approximately 10 hours after another event, but exactly 60
#             minutes in duration", which start+end cannot express because a fuzzy anchor
#             makes both offsets fuzzy and the exactness of their DIFFERENCE is
#             unrecoverable. Informationally equivalent (end = start + duration).
#             absolute_reference takes the same change for the same reason.
#   CHANGE 2  every VALUE-LEVEL `approximate` is DELETED (`value.approximate` on both
#             children). Approximateness lives ONLY where there is a quantity to qualify
#             -- the start/duration cells already carry their own `approximate`, and when
#             neither is present the assertion is purely qualitative (an Allen relation is
#             true or false; "approximately during the session" is not a weaker claim, it
#             is not a claim). THE ABSENCE IS THE IMPRECISION.
#   CHANGE 3  `clock` is a bound `ontology_term` -- already built in increment 1.
#   CHANGE 4  the `approx_` prefix de-encodes to `clock_tolerance` ON THE ROOT (below),
#             because a UTC time good to +/-5 s can land on EITHER class.
#
# THREE distinct precisions, none duplicating another (the walkthrough's own table):
#   clock_tolerance        the TIMELINE is good to +/-5 s   applies to EVERY value on it
#   start.approximate      the ANCHOR is imprecise          this document only
#   duration.approximate   the EXTENT is imprecise          this document only
#
# *** WHAT INCREMENT 2 DELIBERATELY DOES NOT DO, AND WHY -- READ BEFORE "FINISHING" IT ***
# `time_reference.is_approximate` is NOT removed, and the six retiring subclasses are NOT
# deleted. Both are blocked on the SAME thing, and it is not tidiness:
#
#   +did2/+schema/cache.m:695-706 is a STRICT-FIELDS check -- a property block carrying a
#   field the placement-resolved layout does not declare raises
#   did2:validation:undeclaredField. Every live emitter writes
#   `anchor.time_reference = struct('is_approximate', true)` (16 jSessionAnchor call
#   sites + 11 inline copies on the V_eta path). Dropping the declaration while those
#   emitters stand would quarantine 127,719 documents on a 0-quarantine gate -- the
#   epochfiles_ingested regression, at 50x the size.
#
# The emitters cannot simply be moved either: `relative_reference.relative_to` is
# REQUIRED, and a pass-1 migrator CANNOT fill it. It has `base.session_id`, while the
# edge needs the session DOCUMENT's `base.id`, which is a FRESH uid
# (NDI-matlab +ndi/document.m:57-58 `document_properties.base.id = ndiido.id()`;
# +ndi/session.m:215 sets only `base.session_id`). Resolving one to the other is a
# corpus-wide grouping -- the same wall jEpochDocId, distance_metadata and ontology_label
# hit. Emitting the edge empty instead would manufacture the single largest instance of
# the invented-empty-edge pattern this project has recorded. So the fold is a BATCH PASS
# (DID-matlab did2.convert.resolveSessionAnchors), and increment 3 -- drop
# `is_approximate`, delete the six subclasses -- lands only after a corpus run reports
# ZERO surviving session_*_reference documents.
_ABSOLUTE_REFERENCE_SUBS = [
    subfield("start", "structure",
             "The ANCHOR: the wall-clock instant this reference is pinned to. A nested "
             "cell rather than flat `start_utc`/`source_start` fields so the canonical "
             "value and its source provenance travel together, exactly as every "
             "dimensioned value does (T14).",
             sub_fields=[
                 subfield("utc", "timestamp",
                          "Canonical UTC instant -- the normalised, cross-document "
                          "comparable value."),
                 subfield("source_value", "char",
                          "The instant exactly as the source wrote it, before "
                          "normalisation. ALWAYS set when a source string exists; `utc` "
                          "is filled only when the string can be read WITHOUT guessing "
                          "(an unlabelled local time is not convertible)."),
                 subfield("source_timezone", "char",
                          "IANA time zone name as the source gave it (e.g. "
                          "'America/New_York')."),
                 subfield("source_utc_offset", "char",
                          "UTC offset as the source gave it (e.g. '-05:00'), when only "
                          "an offset was available and no zone name."),
                 subfield("approximate", "boolean",
                          "TRUE when the ANCHOR is imprecise. Distinct from "
                          "`duration.approximate` (the EXTENT) and from "
                          "`time_reference.clock_tolerance` (the TIMELINE)."),
             ]),
    subfield("duration", "duration",
             "The EXTENT, measured from `start`. ABSENT means an INSTANT, not an "
             "interval. CHANGE 1: this replaces `end_utc`, so 'started around 09:00, ran "
             "exactly 60 minutes' is expressible -- with two instants both inherit the "
             "anchor's fuzziness and the exactness of the span is lost."),
    subfield("source_end", "char",
             "The end instant verbatim, when the source expressed the interval as TWO "
             "INSTANTS. NOT renamed `source_duration`: the source wrote an end instant, "
             "not a quantity of time, and filing it in a duration's source slot would "
             "label it as something it is not (the distance_metadata assumed-shape error). "
             "`end` is exactly recoverable as start + duration, so what this preserves is "
             "the SOURCE'S SHAPE, not one of our fields."),
]

_RELATIVE_REFERENCE_SUBS = [
    subfield("relation", "ontology_term",
             "The qualitative interval relation to the referent, when no metric offset "
             "exists (OWL-Time; all thirteen Allen relations).",
             constraints=_OWL_TIME_BINDING),
    subfield("clock", "ontology_term",
             "WHICH timeline within the referent the offsets are measured on. NDI times "
             "an epoch on several clocks at once and they drift, so '10 seconds in' is "
             "ambiguous until the clock is named. FOUR terms (#67): the `approx_` "
             "variants de-encode to time_reference.clock_tolerance, `no_time` means "
             "NO REFERENCE AT ALL, and `inherited` is what `relative_to` already says. "
             "Nodes are STAGED EMPTY -- no NDIC identifier can be assigned from any "
             "repository in scope; see the build script for the evidence.",
             constraints=_CLOCK_BINDING),
    subfield("start", "duration",
             "The ANCHOR: offset of this reference from the referent named by "
             "`relative_to`, on the named clock. ABSENT together with `duration` means "
             "the `relation` alone is asserted -- which is the honest state for the "
             "107,308 'during the session' anchors, and is why no value-level "
             "`approximate` flag is needed to say 'we do not know exactly when'."),
    subfield("duration", "duration",
             "The EXTENT, measured from `start`. ABSENT means an INSTANT. CHANGE 1: this "
             "replaces `end`, so an approximate anchor and an exact span are separately "
             "expressible."),
]

write("stable", "absolute_reference",
      doc("absolute_reference", ["time_reference"], version="2.0.0", fields=[
          field("value", "structure",
                "A wall-clock instant or interval. Carries NO dependency: it is "
                "interpretable on its own, which is what distinguishes it from "
                "relative_reference. ANCHOR (`start`) and EXTENT (`duration`) are "
                "separate facts with separate precisions.",
                non_empty=True, sub_fields=_ABSOLUTE_REFERENCE_SUBS)]))

write("stable", "relative_reference",
      doc("relative_reference", ["time_reference"], version="2.0.0",
          deps=[dep("relative_to", "base",
                    "What the time is measured against -- an epoch, a session, an "
                    "interaction, another reference. REQUIRED (team call): a relative "
                    "time with no referent is not interpretable. NOT fillable in pass 1: "
                    "a migrator holds `base.session_id`, and the edge needs the session "
                    "DOCUMENT's `base.id`, which is a different, freshly minted uid "
                    "(NDI-matlab +ndi/document.m:57-58). did2.convert.resolveSessionAnchors "
                    "is the batch pass that resolves it.")],
          fields=[
          field("value", "structure",
                "A time measured against the referent named by `relative_to`. `start` "
                "(the anchor) and `duration` (the extent) are duration cells, so "
                "canonical seconds plus source-unit preservation come for free. ONE "
                "ANCHOR PER DOCUMENT: an interval whose ends are anchored differently "
                "becomes TWO documents (no split-anchored instance exists -- every "
                "markvalidinterval call site passes the same reference for both ends).",
                non_empty=True, sub_fields=_RELATIVE_REFERENCE_SUBS)]))

# ---------- CHANGE 4: `clock_tolerance` on the ABSTRACT ROOT --------------------
# The `approx_` prefix is mode-in-a-name (T13) AND it hides a NUMBER in a docstring (T14):
#
#   NDI-matlab +ndi/+time/clocktype.m:21  'approx_utc'  | ... (within 5 seconds)
#                                    :23  'approx_exp_global_time'   | (within 5s)
#                                    :26  'approx_dev_global_time'   | (within 5 s)
#   NDI-matlab +ndi/+epoch/epochset.m:554-558  degrades utc -> approx_utc, etc.
#
# It must NOT fold into a boolean -- that has no magnitude and the five seconds would be
# lost. It de-encodes to DATA: the bare clock plus `clock_tolerance {seconds: 5}`.
#
# ON THE ROOT, not on relative_reference. The team caught this: a UTC time good to +/-5 s
# can land on EITHER class -- as a wall-clock instant it is an absolute_reference, as
# offsets measured in UTC seconds from a referent it is a relative_reference with
# `clock: utc`. Putting the tolerance on the relative class only would silently drop it
# for every absolute one.
_tr = load(os.path.join(VETA, "stable", "time_reference.json"))
_tr["document_class"]["class_version"] = "4.0.0"
_tr["fields"] = [f for f in _tr["fields"] if f["name"] != "clock_tolerance"]
for _f in _tr["fields"]:
    if _f["name"] == "is_approximate":
        # RETIRING, NOT KEPT. It survives increment 2 only because removing a declared
        # field while emitters still write it raises did2:validation:undeclaredField
        # (+did2/+schema/cache.m:695-706) on every one of the 127,719 live anchors.
        # Increment 3 removes it WITH the six retiring subclasses, gated on a corpus run
        # reporting zero surviving session_*_reference documents.
        _f["documentation"] = (
            "DEPRECATED, retiring with the six session_/epoch_/event_ reference "
            "subclasses (#65 increment 3). CHANGE 2 of the signed walkthrough deletes it: "
            "approximateness belongs where there is a quantity to qualify (start / "
            "duration / clock_tolerance), and the field is empirically vacuous -- eleven "
            "writers, every one a hardcoded `true`, expressing 'we do not know exactly "
            "when', which having no start and no duration already says. THE ABSENCE IS "
            "THE IMPRECISION. Not removed yet ONLY because the strict-fields check would "
            "quarantine every live anchor whose emitter still writes it.")
_tr["fields"].append(field(
    "clock_tolerance", "duration",
    "The stated precision of the TIMELINE these times are expressed on -- NOT of any one "
    "value. ABSENT = no stated tolerance. De-encoded from NDI's `approx_` clocktype "
    "prefix, which documents +/-5 s in a docstring "
    "(+ndi/+time/clocktype.m:21,23,26): approx_utc -> clock: utc + clock_tolerance "
    "{seconds: 5}. The migrator supplies the 5 from writer semantics -- transcription, "
    "not invention. On the ROOT because a tolerance-bearing UTC time can be an "
    "absolute_reference (a wall-clock instant) or a relative_reference (offsets on the "
    "UTC clock); for absolute_reference the timeline is UTC by construction.",
    non_empty=False))
write("stable", "time_reference", _tr)


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
    # PHASE ADDED, team, 2026-08-17: "Add phase."
    #
    # It is what distinguishes half the Hartley basis. `hartleyrange.m` returns
    # each (kx,ky) pair TWICE, once with s=-1 and once with s=+1
    # (`s = [-ones(numel(I),1); ones(numel(I),1)]`), and the Hartley function
    # cas = cos + sin is a 45-degree-offset cosine, so the sign is a 180-degree
    # phase flip. Measured on 20211116: 1680 distinct (kx,ky) pairs x 2 signs =
    # 3360 distinct stimuli, and 41*41-1 -- the DC term, excluded by `F_ > 0` --
    # accounts for the 1680 exactly.
    #
    # WITHOUT THIS FIELD THE SIGN HAS NOWHERE TO GO and 3360 distinct gratings
    # fold into 1680 indistinguishable pairs: a silent halving of the stimulus
    # set that no counter we have would see, because each emitted document
    # would be individually valid.
    subfield("phase", "double", "Spatial phase of the grating, degrees. For a "
             "Hartley basis function the sign s=-1 is +180 relative to s=+1 "
             "(cas = cos + sin, a 45-degree-offset cosine)."),
    # THE PIXEL-DOMAIN SOURCE VALUES. Team 2026-08-17: "we definitely shouldn't
    # be dropping fields."
    #
    # `spatial_frequency`, `size` and `position` above are all declared in
    # DEGREES OF VISUAL ANGLE, and for a Hartley stimulus none of the three can
    # be computed. `hartleyrange.m` derives cycles/degree as
    #     F_ = sqrt(kx^2+ky^2)/M * pixels_per_cm * distance * tan(1 deg)
    # and `pixels_per_cm` comes from `NewStimGlobals` -- rig calibration. It is
    # not in the document and not anywhere else: a sweep of all 1,220 documents
    # in 20211116 across 229 distinct field names found no screen, monitor or
    # pixel calibration of any kind.
    #
    # The PIXEL-domain quantities ARE exactly computable. Writing them into the
    # degree-domain fields would store one quantity under another's name, which
    # is the silent unit error this repository already paid for once with
    # Hz-vs-spikes-per-bin. Leaving them out drops them. So they are carried
    # here beside the canonical fields, in the T14 shape every other quantity in
    # V_eta uses (`duration.value` = {seconds, source_unit, source_value,
    # approximate}; `angle.value` = {radians, ...}).
    #
    # One multiplication recovers the canonical values the day the calibration
    # is known. Until then nothing is lost and nothing is misstated.
    subfield("source_geometry", "structure",
             "As-recorded stimulus geometry, in the units the source used, for "
             "when the degree-domain fields above cannot be computed. Populated "
             "when `pixels_per_degree` is unknown; the canonical fields are then "
             "left unset rather than filled with a differently-united number.",
             sub_fields=[
                 subfield("spatial_frequency", "double",
                          "Spatial frequency as recorded, in `unit`. For a "
                          "Hartley index this is sqrt(kx^2+ky^2)/M."),
                 subfield("size", "double",
                          "Aperture extent as recorded, in `unit`."),
                 subfield("position", "structure",
                          "Stimulus centre as recorded, in `unit`.", sub_fields=[
                              subfield("x", "double", "Horizontal, in `unit`."),
                              subfield("y", "double", "Vertical, in `unit`.")]),
                 subfield("unit", "char",
                          "The unit these values are in: 'cycles/pixel' for "
                          "spatial_frequency and 'pixel' for size and position "
                          "when the source is a screen geometry."),
                 subfield("pixels_per_degree", "double",
                          "The missing conversion factor, when it becomes known. "
                          "Left unset by migration: it is rig calibration "
                          "(NewStimGlobals `pixels_per_cm` x distance x "
                          "tan(1 deg)) and no did_v1 document records it."),
             ]),
]
# ABSTRACT REMOVED, team, 2026-08-17: "Making visual_grating abstract false."
# Same flag, same reason, same day as `timed_sequence`. The signed stimulus
# model requires N STANDALONE `visual_grating` documents that a
# `timed_sequence`'s `presented_id` can point at -- and
# `+did2/+schema/cache.m` raises `did2:validation:abstractInstantiation` for any
# document naming an abstract class, so the model's central case was forbidden
# by its own target class.
#
# THE MEASUREMENT THAT MADE THIS URGENT, over the built set:
#     41 direct subclasses of `data_type`; 40 abstract, 1 concrete
# The single concrete one was `timed_sequence`, made so yesterday. So
# `presented_id -> data_type` -- a deliberately BROAD edge, meant to accept any
# presented stimulus -- had essentially nothing it could legally reference.
# Whether the other 39 should also be reconsidered is NOT decided here; this
# changes the one class the team named.
write("stable", "visual_grating",
      doc("visual_grating", ["base"], fields=[field(
          "value", "structure",
          "A presented visual grating (static or drifting) and its "
          "presentation parameters.", non_empty=True, blank={}, sub_fields=GRATING_SUBS)]))
# ---------- tuning collapse (R2/R3): the 6 old composites are CONSUMED ----------
# The 5 tuning "result" classes + the raw `stimulus_tuningcurve` no longer become their
# own composites/leaves -- they COLLAPSE to the one `tuning_curve` + `tuning_curve_calculation`
# (added below, V_eta_tuning_model_plan.md). Each is now a CONSUMED source: the tuning
# migrators (migrators_j, retargeted) reshape its v1 block into the `tuning_curve` value and
# fold it 1->1 (id-preserved) into `tuning_curve_calculation`. So delete the copytree'd
# source composites here (their docs migrate; downstream refs resolve to the preserved id).
for _old in ("orientation_direction_tuning", "contrast_tuning",
             "spatial_frequency_tuning", "temporal_frequency_tuning",
             "speed_tuning", "stimulus_tuningcurve"):
    _op = os.path.join(VETA, "stable", _old + ".json")
    if os.path.exists(_op):
        os.remove(_op)

# ---------- tuning_curve: the R2/R3 collapse TARGET (re-audit) ----------------------
# V_eta_tuning_model_plan.md: the 6 overlapping tuning composites collapse to ONE
# `tuning_curve` data_type (independent variable rides `subject_statement.variable`, T11)
# + an ARRAY of `model_fit` entries {model (T8 term), coefficients, goodness} + TYPED,
# queryable metric sub-blocks (significance / circular_statistics / interpolated_values --
# NOT a {name,value} bag, T13) + ONE `tuning_curve_calculation` leaf. Added ADDITIVELY
# alongside the shipped per-tuning composites; the calculator RE-TARGET (migrators_j
# jCalculation → this leaf) + removal of the 6 old composites is the coupled DID-matlab
# + corpus step (0-orphan re-verify). Abstract data_type composite so _disposition
# persists it structurally (the "tuning" stem would otherwise hit the retire heuristic).
_TUNING_MODEL_FIT_SUBS = [
    subfield("model", "ontology_term",
             "The fitted model as a controlled term (T8): double_gaussian | naka_rushton | "
             "difference_of_gaussians | movshon | spline | gausslog | priebe | …."),
    subfield("coefficients", "structure",
             "The fit coefficients (named, per the `model`).", non_empty=False),
    subfield("goodness", "structure",
             "Fit-quality scalars (r², residual, …).", non_empty=False),
]
_TUNING_CURVE_SUBS = [
    subfield("independent_values", "matrix",
             "The independent-variable axis samples.", scalar=False),
    subfield("response_mean", "matrix", "Per-sample mean response.", scalar=False),
    subfield("response_stddev", "matrix", "Per-sample response stddev.", scalar=False),
    subfield("response_stderr", "matrix", "Per-sample response stderr.", scalar=False),
    subfield("individual_responses", "matrix",
             "Trial-level responses (real/imaginary preserved where present).", scalar=False),
    subfield("control_response", "structure",
             "The control/blank response block.", non_empty=False),
    subfield("response_units", "char", "Units of the response."),
    subfield("model_fit", "structure",
             "ARRAY of fitted models, each {model, coefficients, goodness}; a curve may carry "
             "several co-existing fits.", scalar=False, non_empty=False,
             sub_fields=_TUNING_MODEL_FIT_SUBS),
    subfield("significance", "structure",
             "Statistical significance sub-block (visual-response / across-stimuli ANOVA p) — "
             "typed, queryable fields.", non_empty=False),
    subfield("circular_statistics", "structure",
             "Circular-statistics sub-block (circular_variance, orientation/direction "
             "preference, Hotelling) — typed, queryable fields.", non_empty=False),
    subfield("interpolated_values", "structure",
             "Fitless interpolated summaries (c50, l50, h50, pref, bandwidth, low/high-pass "
             "index) — typed, queryable fields.", non_empty=False),
]
write("draft", "tuning_curve",
      doc("tuning_curve", ["data_type"], abstract=True, maturity="draft",
          fields=[field("value", "structure",
                        "A response-vs-independent-variable tuning curve, with an ARRAY of "
                        "model fits and typed summary-statistic sub-blocks.",
                        non_empty=True, blank={}, sub_fields=_TUNING_CURVE_SUBS)]))
write("draft", "tuning_curve_calculation",
      doc("tuning_curve_calculation", ["subject_calculation", "tuning_curve"],
          maturity="draft"))

# ---------- #61 harmonic_component: the stimulus-response composite ------------------
# SIGNED. A stimulus response is a HARMONIC of the response at the stimulus
# frequency -- DC, F1, F2 -- as a complex value, with its control counterpart
# beside it. v1 spread that across a scalar/vector/tuning zoo whose parameters
# class carried the LARGEST instance of the invented-empty-edge pattern (11,440
# documents, the edge declared the wrong way round).
#
# ADDITIVE ONLY here: the composite + its calculation leaf. The v1 folds, the
# recovered `instrument_id`/`derived_from_#` edges and the `axes[] variable:
# stimulus` reshape are migrator work, and the 3 stimulus tombstones held under
# #43 ride with them.
_HARMONIC_SUBS = [
    subfield("harmonic", "integer",
             "Which harmonic of the stimulus frequency: 0 = DC, 1 = F1, 2 = F2.",
             blank=0),
    # MATRIX, NOT SCALAR -- ONE COEFFICIENT PER READING. Corrected 2026-08-10.
    # These four were built as scalar `double` while the plan says `matrix, one
    # coefficient per reading` (V_eta_stimulus_response_model_plan.md:276-279),
    # and the plan is right: the v1 writer fills them from a COLUMN, one row per
    # stimulus presentation (+ndi/+app/+stimulus/tuning_response.m:309-313), so a
    # real document carries as many coefficients as it has readings.
    #
    # It had not bitten yet, and would not have for a while, which is the part
    # worth recording: `+did2/+schema/cache.m` validates a block's TOP-LEVEL
    # fields and never recurses into a `structure`'s sub-fields, so a wrong
    # sub-field type is unenforced today. It would have surfaced the moment
    # sub-field validation landed -- against documents already written in the
    # wrong shape. `harmonic` stays scalar: there is exactly one harmonic number
    # per component, which is what makes the component a component.
    subfield("real", "matrix", "Real part of the response at this harmonic, one "
             "coefficient per reading.", scalar=False),
    subfield("imaginary", "matrix", "Imaginary part, one per reading.",
             scalar=False),
    subfield("control_real", "matrix",
             "Real part of the CONTROL response, one per reading. Kept beside the "
             "response rather than in a separate document: v1 stores them together "
             "and a control is meaningless apart from what it controls for.",
             scalar=False),
    subfield("control_imaginary", "matrix",
             "Imaginary part of the control, one per reading.", scalar=False),
]
write("draft", "harmonic_component",
      doc("harmonic_component", ["data_type"], abstract=True, maturity="draft",
          fields=[field("value", "structure",
                        "One harmonic of a response to a periodic stimulus, complex, "
                        "with its control counterpart.",
                        non_empty=True, blank={}, sub_fields=_HARMONIC_SUBS)]))
write("draft", "harmonic_component_calculation",
      doc("harmonic_component_calculation",
          ["subject_calculation", "harmonic_component"], maturity="draft"))

# ---------- #57 the clock alignment cluster: SCHEMA HALF -----------------------------
# SIGNED 2026-08-08, two families, in V_eta_clock_alignment_cluster_plan.md:477 and :479.
#
# THIS BUILD IS THE SCHEMA HALF ONLY, and the reason is written in the signature
# itself -- "Gates carried on these signatures, none waived by them":
#
#   gate 1  #67 GATES THIS CLUSTER. `clock_alignment_configuration.clock` binds to
#           did_clocktype, which the time-model walkthrough cut from 9 terms to 4.
#           The four NAMES are known; their ontology NODES are not minted. Staged
#           per the plan's own §5 -- `{node: '', name: ...}` is already the practice
#           at 34 migrator sites -- and the backlog is counted by #70's ratchet.
#   gate 2  `clock_alignment.relation` needs a term. "Temporally aligned with" is a
#           MAPPING predicate, not an OWL-Time interval relation, so it cannot reuse
#           relative_reference's binding. Staged the same way.
#   gate 3  "EXACTLY 2" was prose until #63 landed. #63 HAS landed, so
#           `acquisition_channels_#` gets a real min_count/max_count of 2 below --
#           this gate is now MET.
#   gate 4  #58 rides with this build. Already shipped as the interim repair.
#
# So: the classes are minted; the MIGRATORS are not written, and the v1 syncrule /
# syncgraph / syncrule_mapping tombstones STAY until a migrator provably consumes
# them. Deleting a source ahead of its migrator is what cost 2,484 quarantines this
# same day.
#
# `acquisition_channels.acquisition_system_id` IS TYPED, and this comment used to be the
# reason it was not. IT SAID: "declared UNTYPED: `acquisition_system` is #59's class and
# does not exist yet (#59 is itself GATED on #37). Typing an edge at a class that is
# absent fails test_dependencies_resolve, and inventing the class here to satisfy it
# would be building #59 sideways." That was TRUE THE DAY IT WAS WRITTEN and stopped being
# true the next day. Both halves have since lapsed, and the lapse is the whole content of
# #57(b):
#
#     $ git log -1 --format="%h %ai %s" 9180524     <- wrote the comment
#     9180524 2026-08-09 #57 clock alignment: correct the stale prose, build the schema half
#     $ git log -1 --format="%h %ai %s" 8a3cc51     <- minted the class, one day later
#     8a3cc51 2026-08-10 Mint epoch_file_pattern + acquisition_system -- the last two ...
#     $ git merge-base --is-ancestor 9180524 8a3cc51 && echo ANCESTOR
#     ANCESTOR
#
# The class is on disk today -- `schemas/V_eta/stable/acquisition_system.json`, ⊂ entity,
# maturity stable -- so `test_dependencies_resolve` now RESOLVES the token instead of
# failing on it, and nothing is being invented here: the target was named by the SIGNED
# model block of this cluster's own plan, `V_eta_clock_alignment_cluster_plan.md:167`
# ("acquisition_system_id -> acquisition_system    the DEVICENAME half"), and
# `acquisition_system ⊂ entity` is TEAM-SIGN-OFF [daq configuration], jess 2026-08-08
# (`V_eta_daq_family_decisions.md:471,476`). #37 is likewise no longer a gate: it is
# ARMED BY DEFAULT (`DID-matlab +did2/+schema/cache.m:968`).
#
# WHAT THIS CHANGE IS NOT, said plainly because the reassuring reading is available.
# `must_refer_to_document_class` is DECLARATIVE -- existence-only, not type-checked
# (`DID-matlab +migrators_j/daqreader.m:59`) -- and the edge is OPTIONAL and is EMITTED BY
# NOTHING today: `migrators_j/private/jAcquisitionChannels.m:98` omits it deliberately,
# because a syncrule stores a device NAME and resolving name -> id needs the migrated-id
# graph a single-document migrator does not have. So typing it changes no validation
# outcome on any document that exists. It records what the edge means, before a second
# pass fills it. REQUIRED-NESS IS UNTOUCHED (`non_empty=False`, as it was): this edge has
# no NDI template to demand it, and a required edge nothing can populate is precisely the
# invented-empty-edge pattern that put tens of thousands of hollow documents in the census.
write("draft", "polynomial",
      doc("polynomial", ["data_type"], abstract=True, maturity="draft",
          fields=[field("value", "structure",
                        "A polynomial, as its coefficients.",
                        non_empty=True, blank={}, sub_fields=[
              subfield("coefficients", "matrix",
                       "Coefficients, HIGHEST ORDER FIRST -- MATLAB's polyval "
                       "convention. Documented because the opposite convention is "
                       "equally common and the two are silently interchangeable.",
                       scalar=False),
              subfield("degree", "integer",
                       "numel(coefficients) - 1. DERIVABLE, and kept anyway: the "
                       "did2 query layer has no length predicate, so `degree > 1` "
                       "-- which alignments are non-linear, the interesting question "
                       "about a clock mapping -- is expressible ONLY if degree is "
                       "stored. Same test that kept `axis.n` and dropped "
                       "`ngrid.data_size`: derivable AT QUERY TIME, not derivable in "
                       "code. CHECKED against coefficients, so it is an index rather "
                       "than a second source of truth.", blank=0),
          ])]))

write("draft", "clock_alignment",
      doc("clock_alignment", ["relation", "polynomial"], maturity="draft",
          deps=[
              dep("from_reference", "relative_reference",
                  "The timeline this alignment maps FROM. The rule is symmetric but "
                  "its OUTPUT is directed, which is why these are named endpoints and "
                  "not a `_#` family.", non_empty=True),
              dep("to_reference", "relative_reference",
                  "The timeline this alignment maps TO.", non_empty=True),
              dep("clock_alignment_configuration_id", "clock_alignment_configuration",
                  "The rule that produced this alignment.", non_empty=True),
              dep("clock_alignment_policy_id", "clock_alignment_policy",
                  "The policy this alignment belongs to.", non_empty=True),
          ],
          fields=[
              field("relation", "ontology_term",
                    "\"Temporally aligned with\". STAGED with an empty node (#67/#70): "
                    "this is a MAPPING predicate, not an OWL-Time interval relation, so "
                    "it cannot reuse relative_reference's binding and needs an NDIC term."),
              field("cost", "double",
                    "The path-finding edge weight. On the leaf rather than inside "
                    "`value` because it is a property of the ALIGNMENT, not of the "
                    "polynomial."),
          ]))

write("draft", "clock_alignment_configuration",
      doc("clock_alignment_configuration", ["base"], maturity="draft",
          deps=[
              dep("software_id", "software",
                  "The implementation that computes this alignment -- v1's "
                  "`ndi_syncrule_class`, folded to a software entity (R1).",
                  non_empty=False),
              dep("acquisition_channels_#", "acquisition_channels",
                  "The two channel groups this rule relates. EXACTLY 2 and UNORDERED: "
                  "the rule is symmetric, so neither endpoint is 'first'.",
                  non_empty=False, multiple=True),
          ],
          fields=[
              field("clock", "ontology_term",
                    "The clock this rule aligns, from did_clocktype -- the SAME FOUR "
                    "terms as relative_reference.value.clock, which is what gate 1 of "
                    "this cluster's sign-off requires. Nodes STAGED EMPTY (#67/#70): no "
                    "NDIC identifier can be assigned from any repository in scope. "
                    "<- v1 `epochclocktype`.",
                    constraints=_CLOCK_BINDING),
              field("minimum_matching_file_paths", "integer",
                    "How many full path components must match. <- v1 "
                    "`number_fullpath_matches`.", blank=0),
              field("sync_file_name", "char",
                    "The sync file to read. <- v1 `syncfilename`."),
              field("minimum_embedded_file_overlap", "integer",
                    "Minimum overlap required between embedded files. <- v1 "
                    "`minEmbeddedFileOverlap`.", blank=0),
          ]))

write("draft", "clock_alignment_policy",
      doc("clock_alignment_policy", ["base"], maturity="draft",
          deps=[
              dep("session_id", "session",
                  "The session whose clocks this policy governs.", non_empty=True),
              dep("software_id", "software",
                  "v1's `ndi_syncgraph_class`, folded to a software entity (R1).",
                  non_empty=False),
              dep("clock_alignment_configuration_#", "clock_alignment_configuration",
                  "The rules this policy applies. OPTIONAL -- a policy with no rules "
                  "yet is legitimate, which is what NDI's own "
                  "\"mustbenotempty\": 0 on syncrule_id says.",
                  non_empty=False, multiple=True),
          ]))

write("draft", "acquisition_channels",
      doc("acquisition_channels", ["base"], maturity="draft",
          deps=[dep("acquisition_system_id", "acquisition_system",
                    "The device half of v1's devicestring -- the rig this channel "
                    "group is read on. THIS DOCUMENTATION READ 'UNTYPED for now: "
                    "`acquisition_system` is #59's class and does not exist yet' "
                    "until 2026-08-12; the class was minted 2026-08-10 (⊂ entity, "
                    "stable) and the sentence outlived its reason. OPTIONAL and "
                    "emitted by nothing today: a syncrule stores a device NAME, "
                    "which rides on `base.name`, and resolving name -> document id "
                    "needs the migrated-id graph a single-document migrator does "
                    "not have (DID-matlab jAcquisitionChannels.m). The type says "
                    "what the edge will mean when a second pass fills it.",
                    non_empty=False)],
          fields=[field("channels", "structure",
                        "One entry per channel-TYPE GROUP, as v1's devicestring "
                        "stores them ('mydevice:ai27-28,45,88;di1-4'). `type` is "
                        "scalar PER ENTRY because a group is by definition one type; "
                        "`numbers` is the list. NOT equal-length parallel arrays -- "
                        "the flat form repeats the type N times and discards the "
                        "grouping the source actually stores.",
                        non_empty=False, scalar=False, blank=[], sub_fields=[
              subfield("type", "ontology_term",
                       "ai | ao | di | do (daqsystemstring.m:53-56)."),
              subfield("numbers", "matrix", "That group's channel numbers.",
                       scalar=False),
          ])]))

# ---------- timed_sequence: the stimulus-presentation TARGET (re-audit) --------------
# V_eta_stimulus_model_plan.md: a stimulus presentation = an ordered, timed list of
# references to stimulus `data_type` docs. `timed_sequence` (data_type; neutral name so a
# future `_observation` leaf is possible) references the DISTINCT presented data_type docs
# (`presented_id → data_type`, broad) + a `presentation_order` index-array playlist;
# `timed_sequence_manipulation` (leaf) adds subject + instrument (stimulator, T7) + time.
# storage_mode governs inline-vs-shared (multi-subject → a shared timed_sequence doc
# referenced by N manipulations). Decompose of v1 stimulus_presentation (around its
# preserved id) is the coupled DID-matlab 2nd-pass step. Additive here.
# ABSTRACT REMOVED, team, 2026-08-17: "It doesn't need to be abstract."
# It was `abstract=True`, and that flag CONTRADICTED the signed model it was
# built to serve. `+did2/+schema/cache.m` raises
# `did2:validation:abstractInstantiation` for any document naming an abstract
# class, while the plan's multi-subject `storage_mode: reference` case needs a
# STANDALONE `timed_sequence` as body-of-record -- "a shared timed_sequence doc
# referenced by N manipulations", three lines above. So the one case the class
# exists to model was the one case it forbade. Nothing had noticed because
# nothing mints the class yet: 0 mint sites in either repo, and the edge that
# already points at it (`+migrators_j/control_stimulus_ids.m:122`,
# `timed_sequence_id`) resolves only because v1 `stimulus_presentation` still
# passes through carrying that id.
write("draft", "timed_sequence",
      doc("timed_sequence", ["data_type"], maturity="draft",
          deps=[dep("presented_id", "data_type",
                    "References to the DISTINCT presented stimulus data_type docs "
                    "(deduped); the playlist indexes these.", non_empty=False, multiple=True)],
          fields=[field("value", "structure",
                        "An ordered, timed list of references to presented data_type docs.",
                        non_empty=True, blank={}, sub_fields=[
              subfield("presentation_order", "matrix",
                       "Playlist: an index array into the `presented_id` references, one "
                       "entry per trial (distinct-refs + index-array encoding).", scalar=False),
          ])]))
write("draft", "timed_sequence_manipulation",
      doc("timed_sequence_manipulation", ["subject_manipulation", "timed_sequence"],
          maturity="draft",
          deps=[dep("timed_sequence_id", "timed_sequence",
                    "For storage_mode:reference (multi-subject) — the shared timed_sequence "
                    "body this manipulation presents.", non_empty=False)]))

# ---------- control_designation: derived control-stimulus annotation (re-audit) ------
# Was `control_stimulus_ids` (drops the `ids` container word, T13). A DERIVED annotation
# (the tuning_response app computes it): references the timed_sequence + carries which
# presented stimuli are the control reference + the derivation method; marked derived
# (derived_from). NOT baked into the immutable stimulus body. Additive target; the
# migrator (control_stimulus_ids → control_designation) is the coupled DID-matlab step.
write("draft", "control_designation",
      doc("control_designation", ["base"], maturity="draft",
          deps=[
              dep("timed_sequence_id", "timed_sequence",
                  "The presentation whose stimuli these controls annotate.", non_empty=False),
              # `derived_from_#`, NOT `derived_from_1`. Found 2026-08-08 in the stimulus
              # sign-off review: this was the ONLY class in the set declaring a CONCRETE
              # numbered edge instance where the FAMILY belongs. `subject_calculation` and
              # `subject_observation` both declare `derived_from_#`; a schema declares the
              # template name and a DOCUMENT names the instances. Hardcoding `_1` also caps
              # the provenance at one antecedent, which T10 does not.
              dep("derived_from_#", "subject_interaction",
                  "Provenance: the analysis/interaction(s) this designation was derived "
                  "from (T10). Cardinality is unexpressed until #63.", non_empty=False),
          ],
          fields=[
              field("control_stimulus", "matrix",
                    "Indices/ids (into the timed_sequence) of the presented stimuli that "
                    "serve as the control reference.", scalar=False),
              field("method", "structure",
                    "How the control designation was derived "
                    "(method / controlid / controlid_value).", non_empty=False),
          ]))

# contrast_sensitivity: the ndi.calc.vis.contrast_sensitivity output
# (contrast_sensitivity_calc) is a FLAT bag of sensitivity/gain/c50/p-value matrices
# with NO result-composite superclass -- so AUTHOR a `contrast_sensitivity` data_type
# composite from the calc's own result fields (input_parameters is inherited from
# `calculator`, not one of them, so it is naturally excluded), and add the leaf.
# Unlike tuningcurve_calc, contrast_sensitivity_calc HAS element_id -> it folds
# single-doc (migrators_j.contrast_sensitivity_calc).
# RESHAPED (walkthrough): the first cut copied the v1 fields VERBATIM, which carried the
# flat bag forward -- 21 top-level fields, five metric families each suffixed
# _rb/_rbn/_rbns, plus `parameters_*`. Two tenet breaks: T11 (the suffixes encode a
# VARIANT in the field name -- the same smell as `_ndr`/`_mfdaq` in a class name) and T13
# (`parameters` is a banned container word; the tuning pass renamed exactly this concept
# to `coefficients`). The conversion doc settles what the suffixes ARE: RB / RBN / RBNS
# are three **Naka-Rushton fit variants**. So they are FITS, and the tuning model already
# has the right shape for that -- a `model_fit` ARRAY. Each variant becomes one entry
# carrying its own coefficients AND the per-spatial-frequency metrics derived from that
# fit; the fit-less and significance scalars become the same TYPED sub-blocks
# `interpolated_values` / `significance` that tuning_curve uses. Every v1 field is
# preserved. contrast_sensitivity stays its OWN class (it aggregates ACROSS spatial
# frequencies rather than being one curve) -- the collapse was never the issue, the
# unreshaped bag was.
_CS_FIT_SUBS = [
    subfield("model", "ontology_term",
             "The fitted Naka-Rushton variant as a controlled term (T8): "
             "naka_rushton_rb | naka_rushton_rbn | naka_rushton_rbns."),
    # v1 stores `parameters_<variant>` as a bare double VECTOR, not a named struct (unlike
    # the tuning fits, whose coefficients arrive already named) -- so this is a matrix, and
    # the element names stay a follow-up: naming them requires the NDIcalc-vis Naka-Rushton
    # parameter ORDER, and inventing Rmax/C50/n/offset without checking would be a guess.
    subfield("coefficients", "matrix",
             "Fitted Naka-Rushton coefficients, as the v1 `parameters_<variant>` vector. "
             "Element naming is a follow-up (needs the NDIcalc-vis parameter order).",
             scalar=False),
    subfield("goodness", "structure",
             "Fit-quality scalars (r², residual, …).", non_empty=False),
    subfield("sensitivity", "matrix",
             "Contrast sensitivity per spatial frequency, from THIS fit.", scalar=False),
    subfield("relative_max_gain", "matrix",
             "Relative maximum gain per spatial frequency, from THIS fit.", scalar=False),
    subfield("empirical_c50", "matrix",
             "Empirical C50 per spatial frequency, from THIS fit.", scalar=False),
    subfield("saturation_index", "matrix",
             "Saturation index per spatial frequency, from THIS fit.", scalar=False),
]
_CS_SUBS = [
    subfield("spatial_frequencies", "matrix",
             "The independent axis: the spatial frequencies the profile is over.",
             scalar=False),
    subfield("model_fit", "structure",
             "ARRAY of fitted models, one entry per Naka-Rushton variant (RB / RBN / "
             "RBNS), each carrying its coefficients and the metrics derived from it.",
             scalar=False, non_empty=False, sub_fields=_CS_FIT_SUBS),
    subfield("interpolated_values", "structure",
             "Fit-less interpolated summaries — typed, queryable.", non_empty=False,
             sub_fields=[subfield("c50", "matrix",
                                  "Fit-less interpolated C50 per spatial frequency "
                                  "(v1 `fitless_interpolated_c50`).", scalar=False)]),
    subfield("significance", "structure",
             "Statistical significance sub-block — typed, queryable.", non_empty=False,
             sub_fields=[
                 subfield("visual_response_p_bonferroni", "matrix",
                          "Bonferroni-corrected visual-response p per spatial frequency.",
                          scalar=False),
                 subfield("response_varies_p_bonferroni", "matrix",
                          "Bonferroni-corrected response-varies p per spatial frequency.",
                          scalar=False),
             ]),
    subfield("is_modulated_response", "boolean",
             "True when the response is modulated (F1) rather than mean (F0)."),
    subfield("response_type", "char", "Which response measure the profile was built on."),
]
write("stable", "contrast_sensitivity",
      doc("contrast_sensitivity", ["data_type"], abstract=True,
          fields=[field("value", "structure",
                        "A contrast-sensitivity profile across spatial frequencies, with "
                        "an ARRAY of Naka-Rushton fit variants and typed summary "
                        "sub-blocks.", non_empty=True, blank={}, sub_fields=_CS_SUBS)]))
write("stable", "contrast_sensitivity_calculation",
      doc("contrast_sensitivity_calculation",
          ["subject_calculation", "contrast_sensitivity"]))

# receptive_field: the result of a reverse-correlation / subspace-sampling
# calculation -- a spatiotemporal response volume over (x, y, time-lag).
# TEAM-SIGN-OFF [receptive field fold] + [receptive field naming],
# V_eta_ngrid_family_findings.md, 2026-08-17.
#
# WHY A NEW COMPOSITE (T12, all four cheaper axes checked and failed).
#   1. same shape, different `variable`?  No -- nothing existing carries an
#      (x, y, lag) volume. `tuning_curve` is response against ONE independent
#      variable.
#   2. a controlled term?  No.
#   3. same quantity, different cardinality/storage?  No -- a different
#      measurement structure, not a longer `value`.
#   4. a role or relationship?  No.
# So it is T12's "genuinely new structured object", and T10's
# one-calculator-one-document-type contract applies.
#
# WHY NOT `spike_triggered_average`, which was the obvious alternative: T11 says
# a name reading as HOW IT WAS MADE is a smell and the how belongs in `method`.
# STA is the method. `hartley_receptive_field` fails the same rule twice over.
# The method rides as a bound term in `value.method` -- which is exactly how the
# v1 document already separates it (`reverse_correlation.method = 'Hartley'`).
#
# THE PAYLOAD IS NOT INLINE, and that is the one way this composite differs from
# its three siblings. `tuning_curve`, `contrast_sensitivity` and
# `harmonic_component` hold small results as inline matrices; a receptive field
# is 200x200x36 doubles per plane (~23 MB for the pair on real 20211116 data),
# so it goes to `sampled_body` via `storage_mode` and this composite carries the
# DESCRIPTORS. That follows the `image` precedent, not the `tuning_curve` one.
#
# TWO PLANES, TWO BODIES -- and the source data is what decided it, not taste.
# v1 `ngrid.data_dim` is [200,200,36,2] while `ngrid.coordinates` has 436
# entries and the dims sum to 438: the writer gave coordinates to three axes and
# NONE to the length-2 one, because it is not a coordinate axis. It is two
# quantities (the STA and its significance) sharing a volume.
_RF_SUBS = [
    subfield("method", "ontology_term",
             "How the field was estimated -- e.g. Hartley subspace reverse "
             "correlation. The METHOD, never part of the class name (T11).",
             sub_fields=[subfield("node", "char", "CURIE, when bound."),
                         subfield("name", "char", "As-recorded method name.")]),
    subfield("storage_mode", "char",
             "Where the response volume lives. `body` for a sampled_body per "
             "plane, which is the only mode a real receptive field uses."),
    subfield("planes", "structure",
             "ARRAY, one entry per emitted body in emission order, naming what "
             "that body holds. A receptive field and its significance map are "
             "DIFFERENT QUANTITIES that happen to share a grid, so they are "
             "separate bodies rather than a length-2 axis -- the v1 writer says "
             "the same by giving that dimension no coordinates.",
             scalar=False, non_empty=True, sub_fields=[
                 subfield("quantity", "ontology_term",
                          "What this plane holds (the response estimate, or its "
                          "significance).",
                          sub_fields=[subfield("node", "char", "CURIE, when bound."),
                                      subfield("name", "char", "As-recorded name.")]),
             ]),
]
write("stable", "receptive_field",
      doc("receptive_field", ["data_type"], abstract=True,
          fields=[field("value", "structure",
                        "A spatiotemporal receptive field: the response volume "
                        "over two spatial axes and a time lag, with the "
                        "estimation method and one entry per stored plane. The "
                        "volume itself lives in `sampled_body` documents; the "
                        "axes (including real lag coordinates) are declared "
                        "there, on `axes[]`.",
                        non_empty=True, blank={}, sub_fields=_RF_SUBS)]))
write("stable", "receptive_field_calculation",
      doc("receptive_field_calculation",
          ["subject_calculation", "receptive_field"]))

write("stable", "visual_grating_manipulation",
      doc("visual_grating_manipulation",
          ["subject_manipulation", "visual_grating"]))
# term_manipulation: the imposed act/agent — a procedure (craniotomy), a regime (dark
# rearing), or a transferred material. Payload-free acts live here; there is NO generic
# escape hatch (D8). Value now inherited from the `term` composite (finding B).
write("stable", "term_manipulation",
      doc("term_manipulation", ["subject_manipulation", "term"]))
# term_observation arrives via the copytree (RENAME categorical_observation ->
# term_observation), so repoint it here rather than at a write site: pair it with the
# `term` composite and drop its locally-declared value (finding B). Its binding was the
# `preferred` one, which is exactly what the hoisted TERM_VALUE carries.
write("stable", "term_observation",
      doc("term_observation", ["subject_observation", "term"]))


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
# drop ndi_daqreader_ndr_class (redundant with the parent's ndi_daqreader_class
# discriminator).
#
# THIS LINE SAID "carry file_extension" AND WAS CONTRADICTED EIGHT LINES BELOW,
# where the same comment block says it is NOT carried and cites the signed
# decision that DELETED it. Corrected 2026-08-12. The built set agrees with the
# deletion, not with the sentence:
#
#     DENOMINATOR: 247 json files under schemas/V_eta
#       declaring `file_extension`: 0
#
# The identical stale sentence was also sitting in DID-matlab's
# `migrators_j/daqreader_ndr.m` docstring and in `testMigratorsJ.m`, in both
# cases a few lines above an assertion that the field is absent. Three copies of
# one wrong clause, none of which could be reached from the others -- which is
# the argument for stating a fact once and deriving the rest.
_rs = _drn_f["ndr_reader_string"]
_rs["name"] = "reader_string"
_rs["mustBeNonEmpty"] = False
_rs["documentation"] = ("Reader/file-type string (e.g. 'intan', 'SpikeGadgets') "
    "for a reader that needs one; formerly daqreader_ndr.ndr_reader_string. "
    "Optional -- the concrete reader is discriminated by ndi_daqreader_class.")
# `file_extension` is NOT carried, and `metadata_names` is dropped from
# daqmetadatareader below. Both are DELETED by the signed daq-configuration
# decision ("the invented `file_extension` and `metadata_names` are DELETED"),
# and "invented" is measured, not asserted:
#
#   DENOMINATOR: 1,002 .m files + every template/schema on NDI origin/main
#     git grep -l "metadata_names"  origin/main -- '*.m' '*.json'  ->  0 files
#     git grep -l "file_extension"  origin/main -- '*.m' '*.json'  ->  0 files
#
# Zero hits means no real document carries either, so REMOVING the declaration
# cannot trip `undeclaredField` on anything -- which is the direction that
# matters. Declaring a field no document has is the wrong-assumed-shape defect
# that produced ~2,078 quarantines; these two are the same defect caught before
# a passthrough exercised it.
_dr["fields"] += [_rs]
_dmr_tier, _dmr_path = path_of("daqmetadatareader")
_dmr = load(_dmr_path)
_dmr["fields"] = [f for f in _dmr["fields"] if f["name"] != "metadata_names"]
write(_dmr_tier, "daqmetadatareader", _dmr)
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

# ---- ngrid: restate the SOURCE TOMBSTONE from the WRITER (#46 gate 2) ----
#
# NDI origin/main, verified 2026-08-10:
#
#   git show origin/main:src/ndi/ndi_common/database_documents/data/ngrid.json
#       "ngrid": { "data_size": "", "data_type": "", "data_dim": "",
#                  "coordinates": "" }
#       superclasses: [ base ]        depends_on: (none)      files: (none)
#   git show origin/main:src/ndi/ndi_common/schema_documents/data/ngrid_schema.json
#       data_size   integer  "The size of each sample in bytes"
#       data_type   string   "The data type (float32, uint16, etc)"
#       data_dim    matrix   "Vector with the dimensions of the data"
#       coordinates matrix   "Not sure"
#   the only writer: +ndi/+fun/+data/mat2ngrid.m -- sets exactly those four.
#
# The tombstone declared `ndims` (REQUIRED), `dim_sizes`, `dim_labels`, an
# `element_id` dependency and an `ngrid_file`. Of those, `ndims` and `dim_sizes`
# are the V_DELTA MIGRATOR'S OUTPUT (+did2/+convert/+migrators/ngrid.m renames
# data_dim -> dim_sizes and derives ndims = numel(data_dim)); `dim_labels`,
# `element_id` and `ngrid_file` appear in NO NDI template or schema at all
# (`git grep -c ndims -- src/ndi/ndi_common/*` returns nothing).
#
# WHY THIS IS SAFE TO FLIP, AND WHY IT HAD TO BE FLIPPED WITH THE MIGRATOR.
# `applySuperclassMigrators` (v1_to_v2.m) is NOT bypassed by the migrators_j
# split -- it runs the V_delta `ngrid` superclass migrator on every V_eta
# document declaring `ngrid`, BEFORE the concrete migrator. That migrator does
# `rmfield(block,'coordinates')` and `rmfield(block,'data_size')`. So under
# V_eta today, `ngrid.coordinates` is DELETED on every ontologyImage and every
# hartley_calc document, which testMigratorsJ already records as "a known,
# separate data loss". DID-matlab now ships a V_eta superclass migrator
# (+migrators_j/+super/ngrid.m) that carries the v1 block VERBATIM, so the four
# real fields are what reaches validation and this tombstone must declare them.
# The two changes are lockstep: either alone quarantines every consumer.
#
# `coordinates` IS CARRIED, NOT GIVEN A HOME. Its destination is decided
# (V_eta_image_model_plan.md, signed 2026-08-08: "ngrid.coordinates -> split by
# data_dim, one slice per axis, into axes[k].values") but `axes[].values` is
# part of the data_body tier (#45), which is BLOCKED ON #32. Until that lands
# the data rides through on the passthrough rather than being deleted. Likewise
# `data_size` is marked for the drop the same plan records (bytes-per-element is
# `datum_type` restated) -- but the drop belongs to the FOLD, not to a
# passthrough, so it is declared and carried here.
#
# `ngrid` STAYS in _IN_PROGRESS (R4). Retiring it is gated on BOTH consumers
# (F4): `ontologyImage` (NDI, +setup/+NDIMaker/imageDocMaker.m:121) and
# `hartley_calc` (NDIcalc-vis-matlab, out of session scope). Neither raster has
# been folded, so nothing may be deleted.
_ngrid = load(os.path.join(VETA, "stable", "ngrid.json"))
_ngrid["document_class"]["class_version"] = "2.0.0"
_ngrid["document_class"]["superclasses"] = [{"class_name": "base"}]
_ngrid["depends_on"] = []
# NDI's `ngrid` declares NO file of its own -- the CONSUMER declares it
# (`ontologyImage.ngrid` in ontologyImage.json's file_list). `ngrid_file` is a
# downstream invention and is removed so did2.validate.fileList stops reporting
# it declared-but-absent on every real document.
_ngrid["file"] = []
_ngrid["fields"] = [
    field("data_size", "integer",
          "Bytes per element (`props.bytes/numel(x)` in mat2ngrid). RESTATES"
          " data_type and is marked for the drop at the fold"
          " (V_eta_image_model_plan.md); declared here because a passthrough"
          " must validate against what the document actually carries.",
          blank=0),
    field("data_type", "char",
          "The numeric class of the grid values ('double', 'uint16', 'ubit1'"
          " for logical). `class(x)` in mat2ngrid.",
          constraints={"maxLength": 64}),
    field("data_dim", "matrix",
          "`size(x)` -- the extent of each dimension, one entry per dimension."
          " NOT `dim_sizes`: that name is the V_delta migrator's output.",
          scalar=False, constraints={"element_type": "integer", "min_value": 1}),
    field("coordinates", "matrix",
          "Vertically concatenated coordinate positions, size [sum(data_dim),1]"
          " -- split by data_dim to recover one coordinate vector per axis."
          " CARRIED, NOT DROPPED: its decided destination is `axes[k].values`"
          " (V_eta_image_model_plan.md), which belongs to the data_body tier"
          " (#45, blocked on #32). The v1 format ADMITS real positions"
          " (`mat2ngrid(X,c1,...,cn)`); the one in-tree caller passes a single"
          " argument, so every ontologyImage document's coordinates are the"
          " default index vector -- which is a fact about today's writers, not"
          " about the format.",
          scalar=False),
]
write("stable", "ngrid", _ngrid)

# ---- ontology_image: make the SOURCE TOMBSTONE hold real v1 documents ----
# THERE IS ONE SHAPE, NOT TWO. This block used to open "NDI redefined
# `ontologyImage` upstream, so two incompatible vintages are both did_v1" and
# declared a vintage A -- {ontology_name, ontology_region} + an `element_id` edge
# -- alongside the real one. Vintage A has never existed. It is DID-schema's own
# V_alpha/V_beta snapshot, re-labelled "legacy" and then read back as did_v1
# ground truth: the ground-truth-track fabrication this repair track exists to
# remove. The migrator's header carried the same correction from 2026-08-09;
# the schema did not, so the fabricated fields were still being BUILT.
#
# RE-VERIFIED 2026-08-11 against NDI origin/main, before removing anything. The
# earlier write-up of this evidence was itself partly wrong, so both the
# corrected citations and the conclusion are recorded here.
#
#   (i) THE CLASS TEMPLATE, EVERY REVISION IT HAS EVER HAD. Four revisions of a
#       file named ontologyImage.json exist; three define the class and all
#       three carry {ontologyNode} + ontologyTableRow_id:
#
#         $ git rev-list --all -- '*ontologyImage.json'   # 4 revisions
#         b33d8ce64  src/ndi/ndi_common/database_documents/data/ontologyImage.json
#         88096f341  ndi_common/database_documents/data/ontologyImage.json
#         40b7dfbff  ndi_common/database_documents/data/ontologyImage.json
#         27daa610e  ndi_common/database_documents/ontologyImage.json
#              ... first three:  "class_name": "ontologyImage",
#                                "depends_on": [{"name": "ontologyTableRow_id"}],
#                                "ontologyImage": {"ontologyNode": ""}
#
#       The FOURTH, 27daa610e ("Create ontologyImage.json"), is the one that
#       looks like vintage A and is not: it is a verbatim copy of the
#       spectrogram template sitting at that path --
#         "class_name": "spectrogram", ... "depends_on": [{"name":"element_id"}]
#       -- replaced by the real content in the next commit to touch the file. It
#       has an `element_id` edge because it is NOT an ontologyImage. So no
#       revision of the CLASS has ever declared `element_id`.
#
#       CITATION CORRECTED: the record (CLAUDE.md, migrators_j/ontology_image.m)
#       said this was "exactly ONE commit, `0ae099c`". Both halves are wrong --
#       --diff-filter=A returns TWO commits (27daa610e, then 40b7dfbff, which is
#       the move into data/), and 0ae099c4a is "Merge pull request #716 ...
#       claude/add-dataset-summary-utility", unrelated to this file. The
#       conclusion the miscitation supported is nevertheless correct, and is now
#       supported by content rather than by a commit count.
#
#  (ii) THE FABRICATED FIELD NAMES, BOTH SPELLINGS, CASE-INSENSITIVE.
#       `ontology_region`/`ontologyRegion` appear in ZERO JSON files anywhere in
#       NDI history:
#
#         $ git log --all --oneline -S"ontology_region" -- '*.json'   # (nothing)
#         $ git log --all --oneline -S"ontologyRegion"  -- '*.json'   # (nothing)
#
#       `ontology_name`/`ontologyName` DO occur in templates -- measurement,
#       treatment, treatment_drug, virus_injection, and a probe-location demo --
#       and in none of them is the class ontologyImage:
#
#         $ git log --all -S"ontologyName" -- '*database_documents*' '*schema_documents*'
#         60e323065  measurement.json, measurement_schema.json
#         0dc856047  treatment/treatment_drug.json, treatment/virus_injection.json
#         9aa6b053c  treatment/treatment_drug.json
#         14e621426  treatment.json
#
# (iii) THE WRITER, WHICH OUTRANKS THE TEMPLATE. One construction site in all of
#       NDI, and it sets one block field and one edge:
#
#         $ git grep -i "ontologyimage" origin/main -- '*.m'
#           imageDocMaker.m:122  ontologyImage_struct = struct('ontologyNodes', ontologyNodes);
#           imageDocMaker.m:125  doc = ndi.document('ontologyImage', ...
#           imageDocMaker.m:133  doc.set_dependency_value('ontologyTableRow_id', ...)
#           imageDocMaker.m:144  doc.add_file('ontologyImage.ngrid', filepath);
#
#       and `element_id` could not be added by a caller even if one tried:
#       ndi.document/set_dependency_value defaults to ErrorIfNotFound=1 and
#       errors on a name the template does not declare (document.m:707,732).
#
# WHAT IS REMOVED, AND WHY REMOVAL CANNOT QUARANTINE ANYTHING:
#   - `ontology_name`, `ontology_region`. These are the only removals with a
#     theoretical cost, because +did2/+schema/cache.m:744 raises
#     `undeclaredField` on a block key the schema does not declare. It is not
#     reachable: this tombstone is consulted ONLY on the passthrough arm, and
#     migrators_j/ontology_image.m takes that arm only when `ontology_nodes` or
#     `ontology_node` is non-empty. A document carrying either removed field
#     non-empty takes the MIGRATE arm instead and never validates against this
#     class; one carrying them empty-but-present would need NDI to have written
#     a key that (ii) shows no template has ever had.
#   - the `element_id` dependency. No cost at all in either direction: the
#     validator allows undeclared depends_on entries wholesale (cache.m's
#     allowedTop admits `depends_on` as a unit; only mustBeNonEmpty edges are
#     checked, and this one was non_empty=False), so removing it cannot
#     quarantine a document and leaving it would not have caught one.
#
# WHAT IS DELIBERATELY NOT TOUCHED:
#   - migrators_j/ontology_image.m keeps its vintage-A arm and its no-match
#     ERROR. An arm for a shape that cannot occur never fires, and the error is
#     the safe direction to be wrong in. The two stay consistent because a
#     vintage-A body is MIGRATED, never passed through, so it never meets this
#     schema.
#   - `ontology_nodes` stays declared although no template has it, because the
#     WRITER wins: imageDocMaker.m:122 writes the plural.
#   - `ontology_node` (the template's singular) stays UNDECLARED. That is the
#     pre-existing open question recorded in the tombstone-audit note, unchanged
#     by this edit and not decided here.
#   - `ontology_table_row_id` keeps its snake_case spelling against NDI's
#     camelCase `ontologyTableRow_id`. Raised in the migrator header as a
#     convention call for a human; not decided here.
#
# The rest of the original note still holds: a deferred document is passed
# through UNCHANGED, so this tombstone must declare the real shape faithfully or
# the passthrough would quarantine on the undeclared `ngrid` block. `ngrid` is a
# superclass for that reason -- and it is why retiring `ngrid` is gated on BOTH
# its consumers (hartley_calc and ontologyImage). See
# V_eta_ngrid_family_findings.md.
_oimg = load(os.path.join(VETA, "stable", "ontology_image.json"))
_oimg["document_class"]["superclasses"] = [
    {"class_name": "base"}, {"class_name": "ngrid"}]
_oimg["document_class"]["class_version"] = "2.0.0"
_oimg["depends_on"] = [
    dep("ontology_table_row_id", "ontology_table_row",
        "The metadata table row giving this image its data context. NOT a subject"
        " -- resolving the subject through it is the NDI second pass's job, which"
        " is why these documents are deferred rather than migrated. The only edge"
        " the class has ever declared, and the only one its writer sets.",
        non_empty=False),
]
_oimg["fields"] = [
    field("ontology_nodes", "char",
          "One or more ontology CURIEs for what the image depicts, comma-joined and"
          " sorted, each normalised through ndi.ontology.lookup. The v1 template's"
          " singular `ontologyNode` is stale; the writer and its own lookup query"
          " both use the plural."),
]
# ---- the RASTER's carrier, and its home under R6 (#47) ----
# NDI declares the payload file on the CONSUMER, not on `ngrid`:
#
#   git show origin/main:src/ndi/ndi_common/database_documents/data/ontologyImage.json
#       "files": { "file_list": [ "ontologyImage.ngrid" ] }
#   git show origin/main:src/ndi/ndi_common/schema_documents/data/ontologyImage_schema.json
#       "file": [ { "name": "ontologyImage.ngrid", "mustbenotempty": 1 } ]
#   +ndi/+setup/+NDIMaker/imageDocMaker.m:139  ndi.fun.data.writengrid(image, ...)
#
# The tombstone declared `ontology_image_file`, a name no NDI template or writer
# has ever used, and `did2.convert.universalRenames` skips the `file`/`files`
# keys outright (universalRenames.m:308), so a real document arrives carrying
# `ontologyImage.ngrid` verbatim. The mismatch is not a quarantine -- nothing in
# +did2/+schema/cache.m looks inside the file wrapper -- but it is exactly the
# pair `did2.validate.fileList` exists to report (declared_but_absent +
# present_but_undeclared), on every vintage-B document.
#
# #47, ANSWERED: the raster's R6 home is an `image_observation` (+ a data_body)
# beside the term observations -- and it CANNOT be minted in pass 1. Vintage B's
# only edge is `ontologyTableRow_id`, and `subject_statement.subject_id` declares
# `must_refer_to_document_class: subject`, so an image_observation emitted here
# would carry an empty required subject edge: the husk pattern, 4,563 JH
# documents' worth, that the image_stack guard was just added to stop. So the
# home is a SECOND-PASS target and the pass-1 obligation is to carry the raster
# INTACT -- which is what this file declaration plus the ngrid restatement above
# now do (the `ngrid` block, `coordinates` included, and the bytes).
_oimg["file"] = [
    {"name": "ontologyImage.ngrid",
     "documentation":
         "The raster, written by ndi.fun.data.writengrid (little-endian, dtype"
         " = ngrid.data_type, extent = ngrid.data_dim). Carried verbatim on the"
         " vintage-B passthrough; its R6 home is an image_observation minted by"
         " the NDI second pass, once the ontologyTableRow edge resolves to a"
         " subject. The name is NDI's own: universalRenames does not touch the"
         " file/files keys, so it arrives unchanged."},
]
write("stable", "ontology_image", _oimg)

# ---- simple_calc: make the SOURCE TOMBSTONE hold real v1 documents -------
# Every part of this class was wrong. It declared `result_value` + `result_units`,
# a REQUIRED `element_id` edge to a subject, and a `calculator` parent. The real
# NDI template (ndi_common/database_documents/apps/calculations/simple_calc.json,
# written by +ndi/+calc/+example/simple.m) is:
#     simple_calc: { input_parameters: {answer: N}, answer: N }
#     depends_on:  document_id      <- the INPUT DOCUMENT, not a subject
#     superclasses: base, app       <- `calculator` is a V_delta invention
# There are NO UNITS anywhere in the class, so the migrator's unit-dispatch
# (Hz -> frequency, V -> voltage, ...) had nothing to dispatch on, and there is
# no subject-bearing edge, so a single-document migrator cannot say who the
# result is about. migrators_j.simple_calc therefore DEFERS to the NDI second
# pass and passes the document through unchanged -- which means this tombstone
# must declare the real shape or the passthrough would quarantine on the
# undeclared `answer`/`input_parameters` fields and the undeclared `app` block.
# See V_eta_ground_truth_plan.md.
_scalc = load(os.path.join(VETA, "stable", "simple_calc.json"))
_scalc["document_class"]["superclasses"] = [
    {"class_name": "base"}, {"class_name": "app"}]
_scalc["document_class"]["class_version"] = "2.0.0"
_scalc["depends_on"] = [
    dep("document_id", "base",
        "The input document this calculation was run on. NOT a subject -- resolving"
        " the subject through it needs the migrated-id graph, which is why this"
        " class is deferred to the NDI second pass rather than migrated here.",
        non_empty=False),
]
_scalc["fields"] = [
    field("answer", "double",
          "The calculation result. The v1 example calculator copies it straight"
          " from input_parameters.answer. Dimensionless -- the class carries no"
          " units field at all."),
    field("input_parameters", "structure",
          "The calculator's input configuration, as supplied by the v1 writer.",
          sub_fields=[
              field("answer", "double",
                    "The input value the example calculator echoes as its answer."),
          ]),
]
write("stable", "simple_calc", _scalc)

# ---- seven more SOURCE TOMBSTONES restated from the real did_v1 shape ----
#
# Same repair as simple_calc, applied to the seven classes whose migrators were
# reading field names no did_v1 document has. Each of those migrators is now a
# guarded passthrough (see the DID-matlab +migrators_j headers), so the document
# arrives at validation in its ORIGINAL shape -- and the validator is strict in
# both directions: `did2:validation:undeclaredField` rejects any block field the
# schema does not declare, and `mustBeNonEmpty` rejects a declared field the real
# document does not carry. A tombstone written from the V_alpha snapshot
# therefore quarantines the very documents it exists to preserve.
#
# Every shape below is taken from the NDI `origin/main` pair -- the property
# template under ndi_common/database_documents/ for the field NAMES and the
# matching ndi_common/schema_documents/ file for the TYPES and the required
# dependencies. Nothing here is inferred from a DID-side schema.
#
# These are deferrals, not models: they hold real documents intact until the NDI
# second pass, which can see the migrated-id graph and read file bytes. See
# V_eta_migrator_vocabulary_audit.md for the per-class evidence.

def _tombstone(name, supers, deps, fields, files=()):
    """Restate a source tombstone from the real did_v1 template + schema.

    Resolves the class's OWN tier rather than assuming `stable` -- `projectvar`
    lives in `deprecated/`, and hardcoding the tier crashed the build partway
    through, leaving a half-written V_eta behind."""
    tier, path = path_of(name)
    if tier is None:
        raise SystemExit(f"_tombstone: no V_eta schema named {name!r} in any tier")
    t = load(path)
    t["document_class"]["superclasses"] = [{"class_name": s} for s in supers]
    t["document_class"]["class_version"] = "2.0.0"
    t["depends_on"] = deps
    t["fields"] = fields
    t["file"] = [{"name": n, "documentation": d} for n, d in files]
    write(tier, name, t)


# spike_clusters -- the sorter's per-spike cluster assignments. The payload is
# the spike_cluster.bin BYTES; a single-document migrator carries files without
# reading them (the pyraview precedent), so no count is derivable in pass 1.
_tombstone(
    "spike_clusters", ["base", "app"],
    [dep("sorting_parameters_id", "sorting_parameters",
         "The sorting run's parameters.", non_empty=False),
     dep("element_id", "subject",
         "The recording element, promoted to a subject with its id preserved by"
         " migrators_j.element (device-as-subject, D2).", non_empty=False),
     dep("extraction_parameters_id", "spike_extraction_parameters",
         "The spike-extraction parameters the sorted waveforms came from.",
         non_empty=False),
     dep("spikewaves_doc_id", "spikewaves",
         "The spikewaves document holding the waveforms that were sorted.",
         non_empty=False)],
    [field("epoch_info", "structure",
           "Per-epoch bookkeeping for the sorted run, as written by the v1 app."),
     field("clusterinfo", "structure",
           "One entry per cluster, as written by the v1 app.", scalar=False),
     field("waveform_sample_times", "matrix",
           "Sample times for the spike waveforms.", scalar=False)],
    files=[("spike_cluster.bin",
            "The per-spike cluster assignments, as bytes.")])

# spikewaves -- extracted waveform snippets. `extraction_name` is the only
# property field; the counts the old migrator reported live in the .vsw header.
_tombstone(
    "spikewaves", ["base", "epochid", "app"],
    [dep("element_id", "subject",
         "The recording element, promoted to a subject with its id preserved.",
         non_empty=False),
     dep("extraction_parameters_id", "spike_extraction_parameters",
         "The extraction parameters used.", non_empty=False)],
    [field("extraction_name", "string",
           "The name of the extraction parameters document.")],
    files=[("spikewaves.vsw", "The waveform snippets (binary, with a header)."),
           ("spiketimes.bin", "The spike times, as bytes.")])

# spike_interface_sorting_outputs -- `depends_on: []` in NDI, so the document
# names NO subject at all; the sorted units are inside sorting.sioutputs.zip.
# The zero declared dependencies are why pass 1 cannot say who this is about.
_tombstone(
    "spike_interface_sorting_outputs", ["base"], [],
    [field("sorter_name", "string",
           "The spike sorter used (e.g. kilosort2, herdingspikes)."),
     field("sample_rate", "integer",
           "Sampling rate of the recording, in Hz.", queryable=False),
     field("unit", "string",
           "Time unit used for spike times (typically 'ms' or 's').",
           queryable=False)],
    files=[("sorting.sioutputs.zip",
            "The SpikeInterface sorting outputs, as an archive.")])

# site2channelmap -- `map` is a column of channel indices whose i-th element
# means "site i of the referenced probe_geometry". Its meaning is only
# recoverable by joining to that document, which pass 1 cannot do.
_tombstone(
    "site2channelmap", ["base"],
    [dep("probe_id", "subject",
         "The probe, promoted to a subject with its id preserved.",
         non_empty=False),
     dep("probe_geometry_id", "probe_geometry",
         "The geometry document whose site ordering indexes `map`.",
         non_empty=False)],
    [field("map", "matrix",
           "Column of channel indices; the i-th element is the channel wired to"
           " site i of the referenced probe_geometry.",
           scalar=False, queryable=False)])

# binnedspikeratevm -- NDI ships templates and schemas for the
# vhlab_voltage2firingrate app but NO writer, in any repository we can reach
# (NDI-matlab, NDIcalc-vis/-ephys/-marder/-birren, vhlab-toolbox). So the
# encoding of the "string"-typed observation fields is undocumented, and
# nothing states whether the binned values are rates or per-bin counts -- at
# the template's binsize of 0.030 s those differ by a factor of 33. The old
# migrator hardcoded Hz. Deferred until a writer or a real document settles it.
#
# NOTE a genuine source disagreement: the template's first dependency is
# `vmspikefilteringparameters_id`, the schema's is `sorting_parameters_id`.
# With no writer there is nothing to arbitrate, so both are declared optional.
_tombstone(
    "binnedspikeratevm", ["base", "epochid", "app"],
    [dep("vmspikefilteringparameters_id", "vmspikefilteringparameters",
         "The Vm spike-filtering parameters (the NDI TEMPLATE's first"
         " dependency).", non_empty=False),
     dep("sorting_parameters_id", "sorting_parameters",
         "The sorting parameters (what the NDI SCHEMA declares in the same slot"
         " -- template and schema disagree and there is no writer to arbitrate).",
         non_empty=False),
     dep("element_id", "subject",
         "The recording element, promoted to a subject with its id preserved.",
         non_empty=False)],
    [field("parameters", "structure",
           "The binning configuration written by the v1 app.",
           sub_fields=[
               field("binsize", "double", "Bin width in seconds."),
               field("vm_baseline_correction", "double",
                     "Whether the Vm baseline was corrected."),
               field("vm_baseline_correct_time", "double",
                     "The time window used for baseline correction."),
               field("vm_baseline_correct_func", "string",
                     "The baseline-correction function (e.g. 'median')."),
               field("number_of_points", "double",
                     "The number of points per bin."),
           ]),
     field("voltage_observations", "string",
           "The Vm observations. Encoding undocumented -- typed `string` by the"
           " NDI schema, with no writer to say how values are packed."),
     field("firingrate_observations", "string",
           "The binned firing observations. Encoding undocumented, and the"
           " quantity (rate vs per-bin count) is not stated anywhere."),
     field("stimids", "string", "The stimulus ids per bin. Encoding undocumented."),
     field("timepoints", "string", "The bin timepoints. Encoding undocumented."),
     field("exactbintime", "string",
           "The exact bin times. Encoding undocumented.")])

# vmneuralresponseresiduals -- same app, same missing writer. `goodness_of_fit`
# is declared `["number", "string"]` in the NDI schema; DID's meta-schema has no
# union type, so it is declared `string` here (the type the template's own value
# has) and the union is recorded in the documentation. Nothing documents the
# metric's range or polarity, so no fold can honestly normalise it.
_tombstone(
    "vmneuralresponseresiduals", ["base"],
    [dep("element_id", "subject",
         "The recording element, promoted to a subject with its id preserved."
         " This is the class's ONLY dependency -- the vmspikefit_id edge the old"
         " migrator read does not exist.", non_empty=False)],
    [field("element_epochid", "string", "The epoch this fit covers."),
     field("parameters", "structure", "The fit configuration.",
           sub_fields=[
               field("number_traces", "double", "How many traces were fit."),
               field("samples_per_trace", "matrix",
                     "Samples in each trace.", scalar=False),
               field("units", "string", "The units of the trace signal."),
           ]),
     field("column_labels", "structure",
           "Names for the columns of the residual trace file.",
           sub_fields=[
               field("first_column", "string", "Typically 'Time (s)'."),
               field("second_column", "string", "Typically 'Raw signal'."),
               field("third_column", "string",
                     "Typically 'Raw signal with spikes'."),
               field("fourth_column", "string", "Typically 'Fit signal'."),
               field("fifth_column", "string", "Typically 'Residual signal'."),
           ]),
     field("goodness_of_fit", "string",
           "The fit quality. NDI declares the type as number-or-string and"
           " documents neither range nor polarity, so it is carried verbatim"
           " rather than folded into a score."),
     field("total_power", "string",
           "Total signal power. Number-or-string in NDI; carried verbatim."),
     field("residual_power", "string",
           "Residual signal power. Number-or-string in NDI; carried verbatim.")])

# ontology_label -- the label value is fine; the REFERENT is the problem. The
# real class has exactly one dependency, `document_id`, pointing at the document
# being labelled. The old migrator asked for element_id/subject_id/probe_id --
# none of which exist -- so it emitted an empty subject edge AND discarded the
# document_id edge, keeping the term and losing what the term was about. The
# second pass can follow document_id through to a subject; pass 1 cannot.
_tombstone(
    "ontology_label", ["base"],
    [dep("document_id", "base",
         "The document this label is about. NOT a subject -- reaching the"
         " subject means following this edge through the migrated-id graph,"
         " which is why the class is deferred to the NDI second pass.",
         non_empty=False)],
    [field("ontology_node", "string",
           "The ontology node id as ontology:nodeID (e.g. 'UBERON:3373')."
           " Spelled `ontologyNode` in did_v1; snake_cased by universalRenames.")])

# ---- the last two vhlab_voltage2firingrate classes ----------------------
# Found by re-checking the detector's "mentions only" bucket, which had been
# taken on trust. Both are the same story as their three siblings above, and
# neither had ever been confirmed against a template.
#
# WHY THEY HID: all five classes of this app are template-and-schema only --
# there is no writer in NDI-matlab, NDIcalc-vis/-ephys/-marder/-birren or
# vhlab-toolbox -- and none of their documents appears in the five corpora under
# test. Three separately broken classes never tripped a gate because the corpora
# do not exercise these paths.
#
# THAT IS NOT A CLAIM THAT NO DOCUMENTS EXIST. The corpora are a SAMPLE OF
# DATASETS, not the universe of them; a class absent from what we test may be
# well represented in a dataset still waiting to migrate, which is precisely what
# this migration is for. So these tombstones must be correct IF documents exist,
# because we cannot show they do not -- "no corpus we looked at has one" is not
# grounds to defer, retire, or half-repair anything.

# vmspikesummary -- the migrator read mean_vm / mean_firing_rate / num_spikes /
# recording_duration and emitted one inline scalar observation per hit. The real
# class shares NO field name with that, and everything it does have is an ARRAY,
# so even the near-miss num_spikes -> number_of_spikes would have failed the
# migrator's isscalar guard. All four reads missed, so the document already fell
# through to the carry-unchanged branch -- a passthrough the counter can see,
# which is how it stayed merely wrong rather than destructive.
#
# The content is a mean spike waveform plus eight spike-shape medians. Modelling
# those needs units and array semantics (per channel? per epoch?) that only a
# writer could settle, and there is none. Deferred with the document intact.
_tombstone(
    "vmspikesummary", ["base", "epochid"],
    [dep("element_id", "subject",
         "The recording element, promoted to a subject with its id preserved.",
         non_empty=False),
     dep("spike_extraction_id", "spike_extraction_parameters",
         "The extraction this summary was computed from. The tombstone declared"
         " only element_id before; this edge was being dropped.",
         non_empty=False)],
    [field("mean_spikewave", "matrix",
           "The mean spike waveform.", scalar=False),
     field("sample_times", "matrix",
           "Sample times for mean_spikewave.", scalar=False),
     field("number_of_spikes", "matrix",
           "How many spikes the mean was taken over. An ARRAY, not a scalar --"
           " the old `num_spikes` read required a scalar and would have failed"
           " even with the name corrected.", scalar=False),
     field("median_spikekink_vm", "matrix",
           "Median membrane potential at the spike kink.", scalar=False),
     field("median_voltageofhalfmaximum", "matrix",
           "Median voltage at half maximum.", scalar=False),
     field("median_fullwidthhalfmaximum", "matrix",
           "Median full width at half maximum.", scalar=False),
     field("median_presk_halfwidthmaximum", "matrix",
           "Median pre-spike half-width at maximum.", scalar=False),
     field("median_postsk_halfwidthmaximum", "matrix",
           "Median post-spike half-width at maximum. Present in the NDI"
           " TEMPLATE but absent from the NDI schema, which instead repeats"
           " median_fullwidthhalfmaximum and median_presk_halfwidthmaximum --"
           " a copy-paste slip on the schema side. The template is the"
           " authority for field names, so it is declared here.", scalar=False),
     field("median_max_dvdt", "matrix",
           "Median maximum dV/dt.", scalar=False),
     field("median_kink_index", "matrix",
           "Median kink index.", scalar=False),
     field("slope_criterion", "string",
           "The slope criterion used. NDI types this string-or-number; the"
           " meta-schema has no union type, so it is declared string (which"
           " also accepts an empty numeric).", scalar=False)])

# vmspikefilteringparameters -- the worst of the three, because there is NO
# migrator at all: the document passes through by default, straight into a
# tombstone that declared `filter_type` and `filter_window`. Neither exists, and
# `undeclaredField` would have rejected every real field it carries. No migrator
# is needed -- a correct tombstone IS the whole fix.
#
# Types follow the NDI schema, which disagrees with its own template on two
# fields: `threshold` and `spiketimes` are typed `number` there while the
# template's literal values are the strings "0.030" and "". The schema is the
# declared type authority (same call made for binnedspikeratevm.parameters.binsize).
_tombstone(
    "vmspikefilteringparameters", ["base", "epochid", "app"],
    [dep("element_id", "subject",
         "The recording element, promoted to a subject with its id preserved.",
         non_empty=False)],
    [field("sampling_rate", "double", "The source sampling rate."),
     field("new_sampling_rate", "double", "The resampled rate."),
     field("threshold", "double",
           "The spike-detection threshold. Typed `number` by the NDI schema;"
           " the template's literal value is the string \"0.030\"."),
     field("spiketimes", "double",
           "Typed `number` by the NDI schema; the template's literal value is"
           " an empty string. With no writer, neither can be confirmed."),
     field("filter_algorithm", "string", "The filter algorithm used."),
     field("filter_algorithm_parameters", "structure",
           "Name/value pairs configuring the filter algorithm.", scalar=False,
           sub_fields=[
               field("filter_algorithm_parameter_name", "string",
                     "The parameter's name."),
               field("filter_algorithm_parameter_value", "string",
                     "The parameter's value."),
           ]),
     field("rm60_hz", "double",
           "Whether 60 Hz line noise was removed. Spelled `rm60Hz` in did_v1;"
           " snake_cased by universalRenames."),
     field("refract", "double", "The refractory period, in seconds.")])

# ---- the spike-extraction parameter pair ---------------------------------
# Found by tools/check_tombstones.py, ranked first of its BLOCKING tier: unlike
# the vhlab_voltage2firingrate family these have a real writer and are referenced
# by spikewaves, spike_clusters and vmspikesummary, so real corpora plausibly
# hold them.
#
# Both declared a shape with almost nothing in common with the real class. The
# real one is a flat bundle of FIFTEEN algorithm settings -- windowing, filter
# design, and a three-part threshold spec -- taken verbatim from the NDI
# templates under ndi_common/database_documents/apps/spikeextractor/.
#
# THE THRESHOLD IS THREE FIELDS, NOT ONE, and that is the substance of the error.
# The tombstone declared a single REQUIRED `threshold` scalar plus a
# `threshold_type`. The real class separates `threshold_method` (how the
# threshold is computed, e.g. 'standard_deviation'), `threshold_parameter` (the
# number fed to that method, e.g. -4) and `threshold_sign` (which crossing
# direction counts). A lone `threshold: -4` means nothing without knowing it is
# four standard deviations rather than -4 volts -- so this was not just a missing
# field, it was a required field that could not be filled correctly even by hand.
#
# NO MIGRATOR, DELIBERATELY. These are algorithm configuration, and every class
# that consumes them (spikewaves, spike_clusters) is itself a deferred
# passthrough whose payload lives in files pass 1 cannot read. Modelling the
# parameters as a `method` + `method_parameters` only makes sense alongside the
# statement they parameterise, which is second-pass work. Until then a correct
# tombstone is the whole job -- exactly the vmspikefilteringparameters case.
#
# NO NDI SCHEMA FILE EXISTS for either class, so the types below come from the
# template literals, which are the only evidence there is. `do_filter` is written
# as the number 1 and is plainly a flag, but it is declared `double` rather than
# `boolean`: the boolean check would reject any other numeric value, and nothing
# in NDI promises there isn't one.
_SPIKE_EXTRACTION_FIELDS = [
    field("center_range_time", "double",
          "Window around the peak used to centre a detected spike, in seconds."),
    field("overlap", "double",
          "Fractional overlap between successive read windows."),
    field("read_time", "double", "Length of each read window, in seconds."),
    field("refractory_time", "double",
          "Minimum separation between two accepted spikes, in seconds."),
    field("spike_start_time", "double",
          "Start of the extracted waveform relative to the peak, in seconds"
          " (negative -- the snippet begins before the peak)."),
    field("spike_end_time", "double",
          "End of the extracted waveform relative to the peak, in seconds."),
    field("do_filter", "double",
          "Whether the signal was filtered before detection. Written as 1/0 by"
          " the writer; declared numeric rather than boolean because nothing in"
          " NDI promises no other value occurs."),
    field("filter_type", "string", "Filter design used (e.g. 'cheby1high')."),
    field("filter_low", "double", "Low cutoff frequency, in Hz."),
    field("filter_high", "double", "High cutoff frequency, in Hz."),
    field("filter_order", "double", "Filter order."),
    field("filter_ripple", "double", "Passband ripple, for designs that take one."),
    field("threshold_method", "string",
          "HOW the detection threshold is computed (e.g. 'standard_deviation')."
          " Meaningless apart from threshold_parameter -- the two together are"
          " the threshold, which is why a lone scalar could not express it."),
    field("threshold_parameter", "double",
          "The number threshold_method consumes (e.g. -4 = four standard"
          " deviations below the mean). NOT a voltage on its own."),
    field("threshold_sign", "double",
          "Which crossing direction counts as a spike (-1 = downward)."),
]

_tombstone(
    "spike_extraction_parameters", ["base", "app"],
    [],   # the real class declares NO dependencies; `element_id` was invented
    list(_SPIKE_EXTRACTION_FIELDS))

# The modification document carries the SAME fifteen settings -- it is a revised
# parameter set, not a description of a revision, so the old `modified_fields` /
# `modification_reason` pair described a document that does not exist. What it
# adds is two edges, and BOTH were undeclared while a third was invented.
_tombstone(
    "spike_extraction_parameters_modification", ["base", "app"],
    [dep("extraction_parameters_id", "spike_extraction_parameters",
         "The parameter set this one revises.", non_empty=False),
     dep("element_id", "subject",
         "The recording element the revision applies to, promoted to a subject"
         " with its id preserved (device-as-subject, D2).", non_empty=False)],
    list(_SPIKE_EXTRACTION_FIELDS))

# ---- BLOCKING tombstones from the check_tombstones.py first run -----------
# Each of these would have quarantined a real did_v1 document. Shapes established
# by the round-2 research pass; evidence in V_eta_tombstone_audit.md.

# sorting_parameters -- 6 flat scalars, NO dependencies (the tombstone invented
# `element_id`), no files, base+app. Unlike its spike_extraction_parameters
# sibling an NDI schema file DOES exist and is authoritative for types. The
# tombstone required `sorter_name`, which is not a field of this class at all.
# Its id is load-bearing: spike_clusters.sorting_parameters_id points at it.
_tombstone(
    "sorting_parameters", ["base", "app"], [],
    [field("graphical_mode", "integer",
           "0/1 -- interactive GUI clustering vs automatic KlustaKwik."),
     field("num_pca_features", "integer",
           "PCA features fed to clustering (automatic mode only)."),
     field("interpolation", "double",
           "Spline oversampling factor for spike waveforms; >1 triggers"
           " resampling. Typed double by the NDI schema while its default and"
           " all five siblings are integers; the writer rounds it. The schema's"
           " [1,10000] bound is contradicted by the writer's clamp to [1,10] --"
           " writer wins for semantics, neither changes the shape."),
     field("min_clusters", "integer", "KlustaKwik minimum cluster count."),
     field("max_clusters", "integer", "KlustaKwik maximum cluster count."),
     field("num_start", "integer", "Random restarts for KlustaKwik.")])

# binaryseries_parameters -- A DEAD TEMPLATE. No .m file in NDI has ever written,
# read or subclassed it; zero commits in all history. Its six fields paraphrase
# the .vhsb header -- a format-descriptor mixin that was never wired up. The real
# binary-series carrier is acquisition_epoch, which does NOT list it as a
# superclass. Kept (not deleted) pending the R5 disposition call, but recorded
# truthfully: the tombstone required num_channels + sample_rate, neither of which
# exists.
#
# TYPES come from the NDI schema. The template supplies `""` for the three
# integer fields, so a fixture built from the template alone would be
# type-invalid against the schema -- a disagreement worth knowing, not resolving.
# The schema also documents time_size/data_size as BYTES with default 32 and type
# float32; 32 bytes is not float32, 32 BITS is, and the vhsb reference
# implementation uses bits. The doc strings below say bits.
#
# THAT DISAGREEMENT IS NOW RESOLVED IN THE MIGRATOR, NOT HERE, and the reason is
# that the schema had no way to resolve it. Against +did2/+schema/cache.m there
# is NO empty representation of a scalar-required integer that validates:
# validateTypeShape runs UNCONDITIONALLY on any field present in the block
# (cache.m:1169 -- there is no is-empty short circuit ahead of it), `integer`
# demands isnumeric (cache.m:1318) so `""` is a typeMismatch, and `[]` is numeric
# but fails mustBeScalar (cache.m:1200). Since `ndi.document(...)` fills a new
# document from the template and then assigns ONLY the name/value pairs the
# caller passed (+ndi/document.m:54-56), a document carrying the template's own
# defaults could not validate. What DOES validate is ABSENCE: an absent field
# that is not mustBeNonEmpty returns early at cache.m:1157-1163. So
# migrators_j/binaryseries_parameters.m DROPS the empty-char placeholder --
# absence is what "" means here and it is the only spelling that passes -- and
# ERRORS on a non-empty char rather than parsing it, because this class has no
# writer anywhere in NDI to say what encoding was intended.
#
# NOT A binaryseries_parameters SPECIAL CASE. Sweeping all 91 NDI
# database_documents templates against the V_eta classes they map to finds 33
# fields whose TEMPLATE LITERAL cannot validate against the type V_eta declares,
# across 20 classes. Only three of those classes have no migrator to overwrite
# the placeholder with a real value, and so are exposed on the passthrough path:
# this one, `stimulus_parameter` (`value`) and `imageStack_parameters`
# (`timestamp`). The other two are other families' calls.
_tombstone(
    "binaryseries_parameters", ["base"], [],
    [field("time_size", "integer",
           "Size of each time (independent-variable) sample, in BITS (the NDI"
           " schema says bytes, which cannot be right at default 32 with type"
           " float32; the vhsb reference implementation uses bits). NDI's"
           " template literal for this field is the CHAR \"\", which cannot"
           " validate as an integer and has no empty integer spelling that can;"
           " migrators_j/binaryseries_parameters.m drops the placeholder so the"
           " field is simply ABSENT when unset."),
     field("time_type", "string",
           "Data type of the time sample (uint32, float32, ...)."),
     field("data_size", "integer",
           "Size of each data (dependent-variable) sample, in BITS -- see"
           " time_size. Same empty-char placeholder, same handling."),
     field("data_type", "string",
           "Data type of the data sample. NOTE this field name collides with"
           " V_eta's `data_type` CATEGORY name; it survives universalRenames"
           " unchanged and is unrelated -- asserted here for a long time with no"
           " test behind it, now gated by"
           " tests/+did2/+unittest/testMiscSingletons.m."),
     field("data_dim", "integer",
           "Dimension of each data sample. Same empty-char placeholder, same"
           " handling."),
     field("samples_regular_intervals", "integer",
           "0/1 -- whether samples are at regular intervals. The template's"
           " literal here is a real 0, not the empty char, so it needs no"
           " normalisation.")])

# projectvar -- a project-scoped scratch key/value variable.
#
# THE NDI SCHEMA DECLARES A FIELD THAT DOES NOT EXIST. It has `date` (timestamp);
# the template AND the writer both have `data` (the payload). This is not a
# casing typo -- each file is missing the other's field entirely. WRITER WINS: it
# is `data`. A shape built from the schema would read a field no document has and
# drop the only field carrying payload.
#
# The sole writer (+ndi/+database/+fun/projectvardef.m) sets only base.name,
# type, description and data -- never project, user or lab, and never any
# dependency, so element_id is empty on every real document despite the schema
# marking it mustbenotempty (consistent with the known fact that depends_on
# non-emptiness is enforced nowhere).
_tombstone(
    "projectvar", ["base"],
    [dep("element_id", "subject",
         "The element this variable is about. The sole writer never populates"
         " it, so it is empty on every real document.", non_empty=False)],
    [field("project", "string", "Name of the project. Never set by the writer."),
     field("type", "string", "Free user-chosen type string."),
     field("user", "string", "Free user-chosen user string. Never set by the writer."),
     field("lab", "string", "Free user-chosen lab string. Never set by the writer."),
     field("description", "string", "Free user-chosen description of the work."),
     field("data", "string",
           "The variable's payload -- an ARBITRARY value passed by the caller."
           " Declared `string` because that is the template's literal (`\"\"`)"
           " and `string` also accepts an empty numeric; the meta-schema has no"
           " union or any type, so a non-empty NUMERIC payload would fail. Same"
           " limitation as vmneuralresponseresiduals.goodness_of_fit. THIS IS"
           " STILL OPEN, and it is why the class is filed as needing real"
           " documents rather than modelled: the failure is a hard quarantine"
           " (did2:validation:typeMismatch, +did2/+schema/cache.m:1290-1310),"
           " not a silent loss, and it is pinned by"
           " testMiscSingletons/testProjectvarNumericPayloadQuarantinesToday so"
           " nobody meets it first on a corpus run.")])

# The daqreader ingest cache family. `epochid` is a SUPERCLASS contributing a
# block that holds the epoch-id STRING -- it is NOT a dependency, and the old
# tombstone declared exactly that invented edge (typed to acquisition_epoch)
# while omitting the superclass, so the epoch string had nowhere to land. See the
# correction in V_eta_6_7_walkthrough_STATE.md; the same false premise shipped as
# an rmfield() in the mfdaq migrator.
#
# These carry no subject and no scientific quantity: their entire referent is
# daqreader_id plus an epoch-id string that is meaningless without the
# epoch/element graph. Promoting them to observations in pass 1 would repeat the
# distance_metadata mistake -- minting unresolvable edges. Keep the bytes and the
# header intact; model them in the second pass.
_tombstone(
    "daqreader_epochdata_ingested", ["base", "epochid"],
    [dep("daqreader_id", "daqreader",
         "The DAQ reader whose epoch this caches.", non_empty=False)],
    [field("epochtable", "structure",
           "Epoch-table snapshot. Nested (not renamed -- universalRenames leaves"
           " nested struct values alone): `epochclock` = clock-type strings,"
           " `t0_t1` = a 2xN matrix, one COLUMN per epochclock."),
     field("parameters", "structure",
           "OPTIONAL, and not a did_v1 field of this class -- it is the"
           " de-encode target from ⑥/⑦ chunk (c), which dissolved"
           " `daqreader_mfdaq_epochdata_ingested` (subtype encoded in the class"
           " NAME) by folding its one mfdaq-specific field onto this generic"
           " parent. Kept when restating this tombstone from the NDI template:"
           " the template does not have it, but the migrator emits it, so"
           " dropping it would quarantine every migrated mfdaq cache.",
           sub_fields=[
               field("sample_analog_segment", "double",
                     "Analog segmentation cutoff. Template default 1e6."),
               field("sample_digital_segment", "double",
                     "Digital segmentation cutoff. The WRITER uses 1e7 while the"
                     " template says 1e6 -- writer wins."),
           ])])

# daqreader_image_epochdata_ingested -- the tombstone had depends_on: [] (dropping
# the real mustbenotempty daqreader_id) and omitted `metadata` entirely, which NDI
# added after the V_eta fork (commit fa30f2903).
_tombstone(
    "daqreader_image_epochdata_ingested",
    ["base", "daqreader_epochdata_ingested", "epochid"],
    [dep("daqreader_id", "daqreader",
         "The DAQ reader whose epoch this caches. Declared mustbenotempty by"
         " NDI; the tombstone previously declared no dependencies at all.",
         non_empty=False)],
    [field("dimension_order", "string", "Axis order over {Y,X,C,Z,T}."),
     field("dimension_size", "matrix",
           "[Y X C Z T] extent.", scalar=False),
     field("data_type", "string", "Numeric class of the stored pixels."),
     field("num_frames", "integer",
           "Frames stored along T (and Z when present)."),
     field("frametimes", "matrix",
           "Per-frame time in epoch-clock units. The writer forces a 1xN row and"
           " uses NaN for clockless epochs -- an empty [] fails validation.",
           scalar=False),
     field("clocktype", "string", "Epoch clock, e.g. 'dev_local_time', 'no_time'."),
     field("metadata", "structure",
           "Standardized image-acquisition metadata. Added by NDI after the"
           " V_eta fork, which is why the tombstone lacked it.",
           sub_fields=[
               field("israster", "boolean", "Whether acquisition was raster-scanned."),
               field("frame_period", "double", "Seconds per frame."),
               field("line_period", "double", "Seconds per line."),
               field("dwell_time", "double", "Per-pixel dwell time, in seconds."),
               field("lines_per_frame", "double", "Lines per frame."),
               field("pixels_per_line", "double", "Pixels per line."),
               field("bidirectional", "boolean", "Whether scanning was bidirectional."),
           ])],
    files=[("frames.bin",
            ("Flat raw binary, column-major, in `data_type`. The NDI schema marks"
            " it optional but the writer always writes it."))])

# electrode_offset_voltage -- the ONE genuinely live fallback of the five audited.
# Its migrator was corrected to the real field names; the tombstone was not, so a
# document taking the discovery fallback quarantines on undeclared `offset`.
#
# The fallback is reachable from ordinary writer output: makeVoltageOffsets.m
# sets offset straight from readtable('MEoffset.txt') with no validation, so a
# blank/NA cell becomes NaN -> [] after a JSON round-trip, and ONE non-numeric
# entry types the whole column as text, taking out every row of the file.
_tombstone(
    "electrode_offset_voltage", ["base"],
    [dep("probe_id", "subject",
         "The probe, promoted to a subject with its id preserved"
         " (device-as-subject, D2).", non_empty=False)],
    [field("offset", "double",
           "The DC offset, a SCALAR (one document per CSV row, not a per-channel"
           " array). Volts, inferred from the writer's `offsetV` column name."),
     field("temperature", "double",
           "The temperature the offset was measured at. The NDI schema"
           " explicitly documents this as able to be NaN or empty, so it is"
           " neither required nor NaN-checked.")])

# measurement -- byte-for-byte the shape of `treatment` (same four fields, same
# three dependency names, same superclass), and treatment already has a
# dissolving migrator. This is its OBSERVATION-direction twin. The tombstone
# required `measurement_class`, which does not exist, and declared an
# `element_id` edge the class does not have while omitting all three real ones.
#
# It gets a migrator (migrators_j/measurement.m) AND a correct tombstone: the
# migrator folds only the rows it can type honestly and carries the rest
# through, so the tombstone is the landing place for everything unresolved --
# notably date-of-birth, which `treatment.m` explicitly routes OUT of its tier
# and which has no V_eta observation leaf (there is no date_observation).
_tombstone(
    "measurement", ["base"],
    [dep("subject_id", "subject",
         "The subject measured. The writer always populates this.",
         non_empty=False),
     dep("manipulation_id", "subject_manipulation",
         "Optional link to a manipulation. NEVER set by any writer on"
         " origin/main.", non_empty=False),
     dep("protocol_id", "base",
         "Optional link to a protocol. NEVER set by any writer on origin/main.",
         non_empty=False)],
    [field("ontology_name", "string",
           "The CURIE of the measured quantity (e.g. NCIT:C81328 = weight)."
           " Spelled `ontologyName` in did_v1. ALWAYS a resolved CURIE -- the"
           " writer gets it from ndi.ontology.lookup and errors if lookup"
           " fails, so this binding is genuine."),
     field("name", "string", "The human label of that ontology node."),
     field("numeric_value", "matrix",
           "The numeric value of the measurement.", scalar=False),
     field("string_value", "string",
           "The string value. POLYMORPHIC -- the consumer (ndi +fun/+docTable/"
           "treatment.m) dispatches it as numeric, datetime, a nested ontology"
           " CURIE, or plain prose, based on the dataType the ontology lookup"
           " returns for the node.")])

# ---- daqmetadatareader_epochdata_ingested: RESTORE THE DROPPED FILE -------
# Found 2026-08-08 in the ingested-payload sign-off review. The class has NO FIELDS AT
# ALL -- its entire content is the attached file -- and both V_zeta and V_eta declared
# `file: []` while NDI declares it REQUIRED:
#
#     schema_documents/ingestion/daqmetadatareader_epochdata_ingested_schema.json
#         "file": [ { "name": "data.bin", "mustbenotempty": 1 } ]
#     database_documents/.../daqmetadatareader_epochdata_ingested.json
#         "files": { "file_list": [ "data.bin" ] }
#
# So a fieldless class declared nothing it carries. This is #64's gap INVERTED: not an
# attachment nobody declared, but a DECLARED file V_eta stopped declaring -- across 2,659
# documents (B 1242 / Dab 1242 / Soph 175) that pass through whole with no migrator.
# `mustBeNonEmpty` on a `file` is not the decorative case: unlike depends_on, nothing
# skips it.
_tombstone(
    "daqmetadatareader_epochdata_ingested", ["base", "epochid"],
    [dep("daqmetadatareader_id", "daqmetadatareader",
         "The metadata reader whose output these bytes are. REQUIRED in NDI"
         " (\"mustbenotempty\": 1).", non_empty=True)],
    [],
    files=[("data.bin",
            ("The metadata reader's ingested bytes for this epoch. The ONLY content"
            " this class has -- it declares no fields. Do NOT type the payload: the"
            " readers produce TSV in the cases seen, but nothing declares that, and"
            " proposing a shape from a template alone is what produced the ~2,078"
            " distance_metadata quarantines."))])

# ---- syncrule_mapping: restore the edge and the fields a LIVE query reads --
# #58. `+ndi/+time/syncgraph.m:404-408` finds saved rules with a three-part query:
#
#   ndi.query('','isa','syncrule_mapping') &
#   ndi.query('','depends_on','syncgraph_id', syncgraph.id()) &
#   ( ndi.query('syncrule_mapping.epochnode_a.objectname','exact_string', daqsystem.name) |
#     ndi.query('syncrule_mapping.epochnode_b.objectname','exact_string', daqsystem.name) )
#
# V_eta declared NEITHER of the two things that query reads. It declared a
# REQUIRED `epochid` dependency instead -- a name no did_v1 document has, empty on
# all 5,316 documents (one of the five invented-empty-edge rows), while NDI's
# template and schema both declare `syncgraph_id` + `syncrule_id` with
# "mustbenotempty": 1. And `objectname` was dropped from both epoch nodes.
#
# `objectname` and `t0_t1` are restored in the `_epochnode` builder further down --
# that builder REBUILDS the node field list, so anything added here is discarded.
# `t0_t1` (the node's time bounds) was dropped by the same reshape and had not been
# noticed; it is restored with `objectname` rather than quietly left out.
#
# NOTE the `time_reference` sub-structure keeps its current `epoch_bounded_reference`
# shape here. That class does not survive the time-reference collapse, and this whole
# class dissolves into `clock_alignment` when the clock-alignment cluster is built --
# this is the interim repair that stops the loss, NOT the model.
_srm_tier, _srm_path = path_of("syncrule_mapping")
_srm = load(_srm_path)
_srm["depends_on"] = [
    dep("syncgraph_id", "syncgraph",
        "The sync graph these saved rules belong to. REQUIRED in NDI"
        " (\"mustbenotempty\": 1) and READ BY A LIVE QUERY"
        " (+ndi/+time/syncgraph.m:404-408).", non_empty=True),
    dep("syncrule_id", "syncrule",
        "The rule that produced this mapping. REQUIRED in NDI"
        " (\"mustbenotempty\": 1).", non_empty=True),
]
write(_srm_tier, "syncrule_mapping", _srm)

# ---- openminds_stimulus: the edge is `stimulus_element_id` ----------------
# The V_zeta base declared `stimulus_id`, a name NO did_v1 document has. NDI's
# template AND its schema AND its writer all agree on `stimulus_element_id`:
#
#   database_documents/metadata/openminds_stimulus.json  depends_on stimulus_element_id
#   schema_documents/metadata/openminds_stimulus_schema.json
#                                       { "name": "stimulus_element_id", "mustbenotempty": 1 }
#   +ndi/+database/+fun/openMINDSobj2ndi_document.m:58   dependency_name = 'stimulus_element_id';
#
# So every one of the ~635 documents carried an edge the tombstone did not
# declare, while the migrator looked for one that does not exist -- a further
# instance of the invented-empty-edge pattern (#71). Superclasses already match
# NDI (base, epochid, openminds); only the edge name was wrong.
_tombstone(
    "openminds_stimulus", ["base", "openminds", "epochid"],
    [dep("stimulus_element_id", "",
         "The stimulus ELEMENT this openMINDS term describes. Named as NDI's"
         " template, schema and writer all name it; the earlier `stimulus_id`"
         " was a DID-side invention that no did_v1 document carries.",
         non_empty=True)],
    [])

# ---- the rest of the Phase-2 tombstones the migrator repairs left behind ---
# SAME DEFECT, FOUR MORE CLASSES. Phase 2 fixed the migrators that READ invented
# field names and guarded the ones that could not be fixed. It never touched the
# TOMBSTONES, so four more classes still declare the V_alpha shape.
#
# `probe_geometry` is the sharpest: its tombstone declares `channel_positions`,
# `position_units` and `probe_type` -- THE EXACT THREE NAMES ITS OWN MIGRATOR
# RAISES ON, by name, as proof that a body was built against our schema instead
# of a real document (migrators_j/probe_geometry.m:70-77) -- plus a REQUIRED
# `num_channels` no document has. The schema describes the shape the migrator
# rejects as impossible.
#
# Types come from NDI's schema documents, which is why this is only possible now:
# the flat ones were readable but unread, and the vhlab family's are JSON Schema.
# `image_stack` + `image_stack_parameters` -- RESTATED 2026-08-09, at the moment
# they came back out of _DELETE_PHASE8. They were deleted before the Phase-2b
# sweep ever compared them against NDI, so they carry the V_alpha shape like the
# other four, and a passthrough must not be handed a schema that misdescribes it.
#
# Both invented an edge and dropped the real ones. imageStack really depends on
# `subject_id` + `document_id` (the latter pointing at the ontologyTableRow that
# gives the image its data context); V_eta declared `element_id`, which no NDI
# template has. imageStack_parameters really depends on `document_id`; V_eta
# declared `imagestack_id`, likewise invented -- and backwards, since the
# parameters block is a SUPERCLASS of imageStack, not a thing it points at.
#
# The 9 parameter fields already matched NDI exactly and are restated unchanged
# so the pair is read from one source rather than half-trusted.
#
# THE ATTACHED FILE IS NAMED `imageStack`, NOT `imagestack_file` -- CORRECTED
# 2026-08-10. The restatement above got the deps and the fields from NDI and
# then invented the FILE name, which is the one part of a document universal
# renaming never touches: `snakeCasePropertyBlocks` skips the structural keys
# outright (`skip = {'document_class', 'depends_on', 'file', 'files'}`,
# DID-matlab +did2/+convert/universalRenames.m:308), so a passed-through
# document reaches validation still carrying NDI's spelling.
#
#   NDI template  database_documents/data/imageStack.json
#                 "files": { "file_list": [ "imageStack" ] }
#   NDI writers   add_file('imageStack', ...) at ALL EIGHT attachment sites,
#                 with no exceptions -- haley/doImport.m:441, 469, 485, 504
#                 (the four that set a subject) and :797, :815, :831 (the three
#                 subject-less ones, attached to the documents built at 789,
#                 811, 827), plus babu/import.m:483.
#
# So the tombstone declared a file no document has, while the file every
# document does have was undeclared -- BOTH directions of the #64 audit at
# once, 4,563 JH documents each way. `did2.validate.fileList` compares by exact
# strcmp (fileList.m:93,99) and does not normalise, and `check_tombstones.py`
# does not compare files at all, which is why this one survived a green
# tombstone run: no instrument we had was looking at it.
#
# The convention this now follows is the one every other tombstone already
# used -- NDI's literal file_list entry (`spikewaves.vsw`, `data.bin`,
# `sorting.sioutputs.zip`, `generic_file.ext`). A file name is PAYLOAD, not an
# identifier, so V_eta's snake_case rule does not reach it.
_tombstone(
    "image_stack", ["base", "image_stack_parameters"],
    [dep("subject_id", "subject",
         "The subject depicted. OPTIONAL because NDI's own writer leaves it"
         " empty on three of its seven imageStack sites"
         " (+setup/+conv/+haley/doImport.m:789,811,827 -- the image / mask /"
         " closest-patch loop set only document_id), which is why 4,563 JH"
         " documents migrated into observations about nobody.", non_empty=False),
     dep("document_id", "",
         "The ontologyTableRow giving this image its data context. Untyped: the"
         " referent is a table row, and resolving a SUBJECT through it is the"
         " second pass's job, not this schema's.", non_empty=False)],
    [field("label", "char", "Prose definition of the image type, from the"
           " ontology term the importer looked up."),
     field("format_ontology", "char", "CURIE for the file format (e.g."
           " NCIT:C70631 for TIFF).")],
    files=[("imageStack", ("The image stack file. The name is NDI's OWN"
            " file_list entry, verbatim, NOT a snake_cased one -- see the note"
            " above."))])

_tombstone(
    "image_stack_parameters", ["base"],
    [dep("document_id", "",
         "NDI's only dependency on this class. Untyped for the same reason as"
         " imageStack's.", non_empty=False)],
    [field("dimension_order", "char", "Axis order, e.g. 'YX' or 'YXT'."),
     field("dimension_labels", "char", "Comma-joined axis names."),
     field("dimension_size", "matrix", "Extent per axis.", scalar=False),
     field("dimension_scale", "matrix", "Physical size per pixel, per axis.",
           scalar=False),
     field("dimension_scale_units", "char", "Comma-joined units for the scales."),
     field("data_type", "char", "Pixel type, e.g. uint8/uint16."),
     field("data_limits", "matrix", "Representable range for the pixel type.",
           scalar=False),
     field("timestamp", "double", "Acquisition time as a MATLAB datenum."),
     field("clocktype", "char", "Which clock the timestamp is on.")])

_tombstone(
    "probe_geometry", ["base"],
    [dep("probe_id", "subject",
         "The probe this geometry describes, promoted to a subject with its id"
         " preserved (device-as-subject, D2). NDI's only dependency here;"
         " V_eta had none.", non_empty=False)],
    [field("site_locations_leftright", "matrix",
           "Per-site left-right coordinate.", scalar=False),
     field("site_locations_frontback", "matrix",
           "Per-site front-back coordinate.", scalar=False),
     field("site_locations_depth", "matrix",
           "Per-site depth coordinate.", scalar=False),
     field("probe_model", "string", "The probe model name."),
     field("manufacturer", "string", "Who made the probe."),
     field("shank_id", "matrix", "Which shank each site sits on.", scalar=False),
     field("contact_shape", "char", "The contact geometry (e.g. circle, square)."),
     field("contact_shape_width", "matrix", "Contact width, per site.", scalar=False),
     field("contact_shape_height", "matrix", "Contact height, per site.", scalar=False),
     field("contact_shape_radius", "matrix", "Contact radius, per site.", scalar=False),
     field("ndim", "integer", "How many spatial dimensions the layout uses."),
     field("unit", "char", "The unit the site coordinates are stated in."),
     field("has_planar_contour", "integer",
           "Whether a planar outline is supplied (NDI types this integer, not"
           " boolean)."),
     field("contour_x", "matrix", "Planar outline, x.", scalar=False),
     field("contour_y", "matrix", "Planar outline, y.", scalar=False)],
    ())

# `position_metadata` declared a REQUIRED `measurement` that no document has --
# and `measurement` is the name the MIGRATOR gives its OUTPUT field, not an
# input. The tombstone had been written from the migrator's target rather than
# from the source, so the one real descriptive field, `ontologyNode`, was
# undeclared. The migrator's own header states the correct v1 shape.
_tombstone(
    "position_metadata", ["base"],
    [dep("element_id", "subject",
         "The element whose position was recorded, promoted to a subject with"
         " its id preserved. The numeric coordinates live in THAT timeseries"
         " document, not in this one.", non_empty=False)],
    [field("ontology_node", "string",
           "WHAT kind of position this is -- a CURIE for the body part or"
           " landmark (e.g. a C. elegans head/midpoint/tail term). The"
           " migrator maps this to its output's `measurement`; the two are not"
           " the same field, and naming the tombstone after the output is how"
           " the real one went undeclared."),
     field("dimensions", "string",
           "Per-axis coordinate-column CURIEs.", scalar=False),
     field("units", "string", "The CURIE for the coordinate unit (e.g. pixels).")],
    ())

# `filter` IS NOT ONE OF THESE, and nearly being "repaired" is the lesson.
# check_tombstones reports `declared but in no NDI template: filter_type` +
# `real fields the tombstone does NOT declare: type`, and both are TRUE of the
# v1 template and IRRELEVANT, because a live migrator performs that rename:
#
#   +did2/+convert/+migrators/filter.m:29-34
#       block.filter_type = char(block.type);  block = rmfield(block, 'type');
#
# and it still runs under V_eta. runConcreteMigrator falls back to the V_delta
# `+migrators` package whenever no `migrators_j` entry exists (v1_to_v2.m:393-402),
# there is no migrators_j/filter.m, and filter is a SUPERCLASS migrator applied to
# everything declaring filter -- `pyraview`, chiefly. So the migrated document
# carries `filter_type` and NOT `type`, and the tombstone is already correct.
# Declaring `type` would have left the real field undeclared and the declared one
# permanently blank -- introducing the exact defect this block exists to remove.
#
# This is the checker's documented limit doing real damage rather than
# theoretical damage: it compares a tombstone against the v1 TEMPLATE and cannot
# see a migrator that legitimately renames. Its output is a starting point, not
# an instruction. Check what runs before acting on a row.

# `fitcurve` is `vmspikefit`'s twin, with one extra defect. Same invented
# `fit_function`, same missing real fields -- and it declared an `element_id`
# NDI DOES NOT HAVE. That one is not cosmetic: see the finding recorded in
# V_eta_OPEN_WORK.md under #35, because the migrator reads it for the subject.
_tombstone(
    "fitcurve", ["base"],
    [dep("fit_example_data_id", "",
         "Example data for the fit. NDI's ONLY dependency on this class."
         " Left untyped -- the referent class is not established.",
         non_empty=False)],
    [field("fit_name", "string", "The name of the fit."),
     field("fit_equation", "string",
           "The fitted equation; the migrator uses it as the observation's"
           " `method`. V_eta called this `fit_function`, a name no NDI template"
           " has ever carried."),
     field("fit_parameters", "matrix", "The fitted parameter values.", scalar=False),
     field("fit_parameter_names", "string",
           "Names of the fitted parameters, positionally matching"
           " fit_parameters.", scalar=False),
     field("fit_independent_variable_names", "string",
           "Names of the independent variables.", scalar=False),
     field("fit_dependent_variable_names", "string",
           "Names of the dependent variables.", scalar=False),
     field("fit_sse", "string",
           "Sum of squared errors. Unbounded, units squared, LOWER IS BETTER --"
           " NOT the 0..1 higher-is-better `goodness_of_fit` V_eta declared."
           " NDI types it `string`."),
     field("fit_constraints", "structure",
           "The constraints the fit was run under.", scalar=False),
     field("fit_data", "structure",
           "The data the fit was computed over. Unlike vmspikefit, this class"
           " DOES ship the data, so r^2 is derivable here -- deliberately not"
           " derived, because doing it on one side only would leave two classes"
           " emitting the same variable name for different quantities.")],
    ())

# ---- vmspikefit: the MIGRATOR was repaired and its TOMBSTONE was not ------
# Phase 2 fixed `migrators_j/vmspikefit.m` to read `fit_equation` and `fit_sse`
# after finding that `fit_function` and `r_squared` have NEVER existed on the NDI
# template -- 0 commits across NDI's history mention either, against 7 for
# fit_equation and fit_sse; both names came from DID-schema's own V_alpha
# snapshot. The tombstone was left declaring exactly those two invented names,
# with `fit_function` marked REQUIRED, and declaring none of the seven real ones.
#
# NDI origin/main, apps/vhlab_voltage2firingrate/vmspikefit.json:
#
#   superclasses  base, epochid, app          (V_eta had base alone)
#   depends_on    fit_input_id, element_id    (V_eta had element_id alone)
#   vmspikefit    fit_name, fit_equation, fit_parameters, fit_parameter_names,
#                 fit_sse, fit_sse_perpoint, fit_constraints
#   files         NONE                        (V_eta invented `vmspikefit_file`)
#
# NOT CURRENTLY A QUARANTINE, and the reason is worth stating rather than
# assuming: the migrator consumes every vmspikefit document (1 -> a
# score_observation + the session anchor) and emits no vmspikefit, so nothing
# reaches validation under this class and the required-but-nonexistent
# `fit_function` never fires. That is luck, not design -- the class is not in
# _DELETE_PHASE8, so the schema still advertises itself as describing this
# document, and it describes a document that has never existed.
#
# The `depends_on` here comes from NDI's SCHEMA document, which is the ONLY
# ground truth available for this family: the vhlab_voltage2firingrate WRITER is
# in no repository we have. Those five schema files are JSON Schema draft
# 2019-09 rather than the flat shape and were being skipped in silence until
# 2026-08-09, which is why `fit_input_id` had never shown up as missing.
_tombstone(
    "vmspikefit", ["base", "epochid", "app"],
    [dep("fit_input_id", "",
         "The document this fit was computed FROM. Declared by NDI's template"
         " AND its schema; V_eta had dropped it. Left untyped -- the input class"
         " is not established and the vhlab_voltage2firingrate writer is in no"
         " repository we have.", non_empty=False),
     dep("element_id", "subject",
         "The recording element, promoted to a subject with its id preserved by"
         " migrators_j.element (device-as-subject, D2).", non_empty=False)],
    [field("fit_name", "char", "The name of the fit."),
     field("fit_equation", "char",
           "The fitted equation. The migrator uses this as the observation's"
           " `method`. V_eta previously called this `fit_function`, a name no"
           " NDI template has ever carried."),
     field("fit_parameters", "structure",
           "The fitted parameter values. NOT re-expressed by the migrator --"
           " a fit's parameters fold to a method / settings document, a"
           " per-class decision that is still open."),
     field("fit_parameter_names", "string",
           "The names of the fitted parameters, positionally matching"
           " fit_parameters.", scalar=False),
     field("fit_sse", "double",
           "SUM OF SQUARED ERRORS. Unbounded, in the fitted variable's units"
           " squared, and LOWER IS BETTER -- it is NOT the r^2 the old"
           " `r_squared` field claimed, which is bounded 0..1 and higher-is-"
           "better. Substituting one for the other would have inverted every"
           " downstream comparison while looking like a rename."),
     field("fit_sse_perpoint", "double",
           "SSE normalised per point -- the figure that compares across fits of"
           " different lengths."),
     field("fit_constraints", "structure",
           "The constraints the fit was run under"
           " ({fit_constraint_name, fit_constraint_value}).", scalar=False)],
    ())

# ---- daqsystem / daqmetadatareader: the SAME inversion, one tier over -----
# Found 2026-08-09 by re-reading check_tombstones' LOSSY tier, which had been
# reporting `daqsystem: real dependencies not declared: daqmetadatareader_id`
# for as long as the checker has existed.
#
# NDI origin/main -- template, schema and writer:
#
#   daq/daqsystem.json          depends_on filenavigator_id, daqreader_id,
#                                          daqmetadatareader_id
#   daqsystem_schema.json       filenavigator_id  "mustbenotempty": 1
#                               daqreader_id      "mustbenotempty": 1
#                               daqmetadatareader_id "mustbenotempty": 0
#   daq/daqmetadatareader.json  depends_on []                <- NONE
#
#   +ndi/+daq/system.m:489-497
#       set_dependency_value('filenavigator_id', ...)
#       set_dependency_value('daqreader_id', ...)
#       for i = 1:numel(obj.daqmetadatareader)
#           add_dependency_value_n('daqmetadatareader_id', ...)   <- A FAMILY
#   +ndi/+daq/system.m:48
#       dependency_value_n('daqmetadatareader_id', 'ErrorIfNotFound', 0)
#
# So V_eta pointed the edge the wrong way here too: it put a REQUIRED
# `daqsystem_id` on `daqmetadatareader` -- a name no did_v1 document has, empty
# on all 59 documents, 100% of the class, one of the census's invented-empty-edge
# rows -- and dropped the edge NDI actually writes.
#
# The real edge is a NUMBERED FAMILY, not a scalar: the writer LOOPS, and the
# reader uses the `_n` API. A daqsystem may have several metadata readers, or
# none -- the loop simply does not execute -- so min_count is 0, which is also
# what NDI's own "mustbenotempty": 0 says.
#
# NO CORPUS RISK, for the same reason as the stimulus_response repair: the
# documents already carry these ids and references.m already resolves them.
_dqs_tier, _dqs_path = path_of("daqsystem")
if _dqs_path:
    _dqs = load(_dqs_path)
    _dqs["depends_on"] = [
        dep("filenavigator_id", "filenavigator",
            "The file navigator this system reads through. REQUIRED in NDI"
            " (\"mustbenotempty\": 1).", non_empty=True),
        dep("daqreader_id", "daqreader",
            "The reader that decodes this system's files. REQUIRED in NDI"
            " (\"mustbenotempty\": 1).", non_empty=True),
        dep("daqmetadatareader_id_#", "daqmetadatareader",
            "The metadata readers attached to this system. A FAMILY, not a"
            " scalar: +ndi/+daq/system.m:495-497 loops with"
            " add_dependency_value_n and :48 reads with dependency_value_n."
            " OPTIONAL (NDI's schema says \"mustbenotempty\": 0, and a system"
            " with no metadata reader never enters the loop).",
            non_empty=False, multiple=True),
    ]
    write(_dqs_tier, "daqsystem", _dqs)

_dqm_tier, _dqm_path = path_of("daqmetadatareader")
if _dqm_path:
    _dqm = load(_dqm_path)
    # NDI declares NO dependencies on this class. `daqsystem_id` was invented,
    # required, and empty on 100% of its 59 documents -- which validated clean,
    # because +did2/+validate/references.m:90 skips empty edges. The real edge
    # lives on daqsystem, above, and points the other way.
    _dqm["depends_on"] = []
    write(_dqm_tier, "daqmetadatareader", _dqm)

# ---- stimulus_response family: the edge was declared BACKWARDS ------------
# #61. THE LARGEST INSTANCE of the invented-empty-edge pattern -- 11,440
# documents (Soph 11,167 / 20211116 273), 100% of the class, every one carrying
# an edge no did_v1 document has while the edge NDI does write was dropped.
#
# NDI origin/main, template and schema agreeing:
#
#   stimulus_response.json          depends_on element_id, stimulator_id,
#                                              stimulus_presentation_id,
#                                              stimulus_control_id
#   stimulus_response_schema.json   all four "mustbenotempty": 1
#   stimulus_response_scalar.json   depends_on stimulus_response_scalar_parameters_id
#   ..._scalar_schema.json          "mustbenotempty": 1
#   ..._scalar_parameters.json      depends_on []          <- NONE. AT ALL.
#
# and the writer sets all five, unconditionally, at one call site:
#
#   +ndi/+app/+stimulus/tuning_response.m:323-328
#       set_dependency_value('stimulus_response_scalar_parameters_id', param_doc{1}.id())
#       set_dependency_value('element_id', ndi_timeseries_obj.id())
#       set_dependency_value('stimulus_presentation_id', stim_doc.id())
#       set_dependency_value('stimulus_control_id', control_doc.id())
#       set_dependency_value('stimulator_id', ndi_stim_obj.id())
#
# So V_eta had it exactly inverted: the PARAMETERS document was made to point at
# the response (required, and empty on all 11,440), when in NDI the response
# points at its parameters. `stimulus_response_scalar.stimulus_response_id` is
# the same error one class down -- an invented name whose v1 antecedent, as the
# 8d note further below already suspected, was `stimulus_response_scalar_parameters_id`.
# That note is now answered with the template rather than left as a suspicion.
#
# Two REAL edges were also simply missing: `stimulator_id` (T7 -- the instrument
# that delivered the stimulus) and `stimulus_control_id` (the control the
# response is measured against). Both are required in NDI and both were dropped,
# so a migrated response could not say what stimulated the subject or what it was
# compared with.
#
# Required-ness here is POSITIVE EVIDENCE, not a guess: NDI's schema marks every
# one "mustbenotempty": 1 and one writer sets all five together. That is the
# check CLAUDE.md demands before a required edge is declared, and it is the check
# that was skipped when these were invented.
_srs_tier, _srs_path = path_of("stimulus_response")
if _srs_path:
    _srs = load(_srs_path)
    _srs["depends_on"] = [
        dep("element_id", "subject",
            "The element (e.g. neuron) whose response was measured. REQUIRED in"
            " NDI (\"mustbenotempty\": 1).", non_empty=True),
        dep("stimulator_id", "subject",
            "The stimulator element that delivered the stimulus -- T7's"
            " instrument role. REQUIRED in NDI (\"mustbenotempty\": 1) and set at"
            " +ndi/+app/+stimulus/tuning_response.m:328; V_eta had DROPPED it, so"
            " a migrated response could not say what stimulated the subject.",
            non_empty=True),
        dep("stimulus_presentation_id", "stimulus_presentation",
            "The presentation this response was measured against. REQUIRED in"
            " NDI (\"mustbenotempty\": 1).", non_empty=True),
        dep("stimulus_control_id", "",
            "The control this response is compared with. REQUIRED in NDI"
            " (\"mustbenotempty\": 1) and set at tuning_response.m:327; V_eta had"
            " DROPPED it. Left untyped: the control is another stimulus_response"
            " document and typing it rides with the stimulus model.",
            non_empty=True),
    ]
    # REPAIR 3 of the signed plan: `response_file` is INVENTED and is deleted.
    #
    #   git show origin/main:src/ndi/ndi_common/database_documents/stimulus/\
    #       stimulus_response.json  |  grep -c 'files\|file_list'   ->  0
    #
    # NOT ONE of the four templates in this family declares a file, and the
    # writer builds all of them with plain `ndi.document(...)` + block structs
    # (tuning_response.m:276-281 and :320-322) -- there is no
    # `add_file`/`.ext` call anywhere in `compute_stimulus_response_scalar`.
    # The declaration came from DID-schema's own V_alpha snapshot, like the
    # reversed parameters edge above.
    #
    # It is not a live quarantine today: a declared file is not required to be
    # present, so a real (file-less) document passes. What it does is assert, to
    # every reader of the schema, that a response has a payload file -- so a
    # second pass could go looking for one, and `did2.validate.isFragment` gets
    # a declaration it can never satisfy. Deleting it costs nothing and removes
    # a standing invitation to build against a file that has never existed.
    _srs["file"] = []
    write(_srs_tier, "stimulus_response", _srs)

_srsc_tier, _srsc_path = path_of("stimulus_response_scalar")
if _srsc_path:
    _srsc = load(_srsc_path)
    _srsc["depends_on"] = [
        dep("stimulus_response_scalar_parameters_id",
            "stimulus_response_scalar_parameters",
            "The parameters document that produced these scalar responses."
            " THE DIRECTION MATTERS: in NDI the response points at its"
            " parameters, never the reverse. REQUIRED (\"mustbenotempty\": 1),"
            " set at tuning_response.m:323. Replaces `stimulus_response_id`, a"
            " name no did_v1 document carries.", non_empty=True),
    ]
    write(_srsc_tier, "stimulus_response_scalar", _srsc)

_srsp_tier, _srsp_path = path_of("stimulus_response_scalar_parameters")
if _srsp_path:
    _srsp = load(_srsp_path)
    # NDI's template declares NO dependencies on this class. The required
    # `stimulus_response_scalar_id` was invented, pointed the wrong way, and was
    # empty on 100% of 11,440 documents -- which validated clean, because
    # +did2/+validate/references.m:90 skips empty edges. Removing it is the
    # repair; the real edge lives on the child, above.
    _srsp["depends_on"] = []
    write(_srsp_tier, "stimulus_response_scalar_parameters", _srsp)

# ---- _parameters_basic.freq_response: it is a HARMONIC NUMBER, not a flag --
# #61, REPAIR 4 of the signed plan's "REPAIRS THIS CARRIES (needed under any
# model)" list. This is the one repair in that list that had NOT been built; the
# other four landed with the edge-direction fix above and with the migrators.
#
# The field was declared `integer {min: 0, max: 1}` and documented "1 if this
# scalar response is a frequency-domain measurement, 0 otherwise" -- i.e. as a
# boolean. It is not one. From the writer, NDI origin/main
# `+ndi/+app/+stimulus/tuning_response.m`:
#
#   :202   freq_response_commands = [0 1 2];      <- the DEFAULT sweep
#   :204   freq_response_commands = 0;            <- when no stimulus has a
#                                                    fundamental frequency
#   :207   freq_response_commands = freq_response;   <- CALLER-SUPPLIED, unbounded
#   :260   freq_response = freq_response_commands(f);
#   :262-266  if freq_response==0, response_type='mean'; else ['F' int2str(...)]
#   :276-281  vlt.data.var2struct(... 'freq_response' ...)  -> the document
#
# So the stored value is the harmonic index: 0 = DC/mean, 1 = F1, 2 = F2 -- and
# `max: 1` is a claim that would reject every F2 document. F2 is not exotic: it
# is one third of the default sweep, so roughly a third of the 11,440 documents
# in the corpora carry freq_response = 2.
#
# TWO INDEPENDENT ERRORS, and only the second one is why nothing has broken yet:
#   (a) the BOUND is wrong -- 1 where the writer emits 0/1/2 and permits more;
#   (b) the KEY is wrong -- `+did2/+schema/cache.m` validateConstraints (:1340)
#       switches on `maxLength | minLength | minimum | maximum | enum` and its
#       `otherwise` branch silently TOLERATES unrecognised keys, so `min`/`max`
#       are INERT. The declaration has never been enforced.
# Spelling the key correctly without fixing the bound would quarantine a third
# of the class the day someone normalised the constraint vocabulary. Both halves
# are repaired together, here, rather than left as a trap.
#
# NO `maximum` IS DECLARED, deliberately. :207 takes `freq_response` straight
# from the caller, so 3 is representable; a bound we cannot derive from the
# writer is exactly the kind of invention this repair track exists to remove.
# `minimum: 0` is safe under the same rule -- a harmonic index is a count, the
# template default is 0, and an empty value passes (`any([] < 0)` is false).
#
# `isspike` is left ALONE. Its {min:0, max:1} is equally inert but its INTENT is
# correct (the writer sets 0 or 1 and nothing else, :176/:179-182), so rewriting
# its key would newly ENFORCE a rule on 11,440 live documents to no benefit.
# Recorded rather than fixed: 4 fields in the built set carry the inert spelling
# (element.reference, element.direct, and these two).
_srsb_tier, _srsb_path = path_of("stimulus_response_scalar_parameters_basic")
if _srsb_path:
    _srsb = load(_srsb_path)
    for _f in _srsb.get("fields", []):
        if _f["name"] != "freq_response":
            continue
        _f["constraints"] = {"minimum": 0}
        _f["documentation"] = (
            "The HARMONIC of the stimulus fundamental this response reduces to: "
            "0 = DC (the writer's 'mean'), 1 = F1, 2 = F2. NOT a boolean -- it "
            "was declared {min:0,max:1} and documented as a frequency-domain "
            "flag, which would reject every F2 document. "
            "+ndi/+app/+stimulus/tuning_response.m:202 sweeps [0 1 2] by default "
            "and :207 takes the value from the caller, so no maximum is "
            "declared. :262-266 derives `response_type` from it, which is why "
            "the harmonic is recoverable from the response document alone and "
            "this document is foldable."
        )
    write(_srsb_tier, "stimulus_response_scalar_parameters_basic", _srsb)

# ---- stimulus_parameter_table: DEMOTE to deprecated/ ----------------------
# Decided 2026-08-08 in the stimulus-parameters sign-off review. The team's
# objection: "it seems weird to pass a bad V1 doc through."
#
# It is not a modelling problem, it is a FILING problem. The disposition is
# right -- a real did_v1 class (shipped template), NO writer anywhere in NDI's
# 915 .m files, ONE untyped field (`string[]`), and ZERO documents in any of the
# five corpora (census run #257, and no list was truncated: the digest caps at 15
# and the longest is 12). There is nothing to model against, and deleting is
# forbidden by the corpora-are-a-sample rule.
#
# But `projectvar` -- the precedent the plan cites for exactly this call, and for
# exactly the same reasons -- lives in `deprecated/`, and this one sat in
# `stable/`. So the document did not merely pass through: it passed through into
# a class ADVERTISING ITSELF as part of the go-forward model, with nothing in the
# artifact to tell a consumer otherwise. The unmodelled state was visible only in
# a CI census line.
#
# Demoting makes "passthrough" honest: bytes preserved, and the schema set states
# plainly that this is a v1 shape nobody has modelled.
_spt_tier, _spt_path = path_of("stimulus_parameter_table")
if _spt_tier and _spt_tier != "deprecated":
    _spt = load(_spt_path)
    _spt["document_class"]["maturity_level"] = "deprecated"
    write("deprecated", "stimulus_parameter_table", _spt)
    os.remove(_spt_path)

# ---- the two stimulus-parameter tombstones, restated from NDI -------------
#
# Two of the three rows `check_tombstones.py` still reports as BLOCKING. They
# were held for the stimulus model deliberately; the stimulus-parameters
# sign-off (V_eta_stimulus_parameter_plan.md:205) is that hold coming due, and
# it names this repair explicitly: "both tombstones rewritten to the NDI shape".
# It is required under BOTH signed options -- dissolution (A) still has to hold
# real documents intact until its own gate lifts, and passthrough (C) is nothing
# BUT the tombstone.
#
# What was here shared ZERO field names and ZERO edge names with NDI:
#
#   stimulus_parameter        NDI  ontology_name, name, value    dep stimulus_element_id
#                             was  parameter_name, parameter_values, parameter_units
#                                                                dep stimulus_presentation_id (REQUIRED)
#   stimulus_parameter_table  NDI  string                        dep stimulus_element_id
#                             was  parameter_names, table_data, num_stimuli
#                                                                dep stimulus_presentation_id (REQUIRED)
#
# So a passthrough would have quarantined every document twice over --
# `undeclaredField` on what the document DOES carry, `missingField` on the
# invented required name -- the wrong-assumed-shape failure that produced the
# ~2,078 distance_metadata quarantines.
#
# Shapes are NDI origin/main, template for the names and schema_documents for
# the types. Three readings are NOT a straight copy, and each is recorded:
#
#  1. `value` is typed `double`, not char. The database_documents template's
#     placeholder is `""`, which is what the plan's OPEN item 2 read; the
#     SCHEMA says `"type": "double"` and the writer assigns numbers
#     (temptable2stimulusparameters.m:44,58,64 -- `last_match.temp{1}` and its
#     two indexed forms). Schema and writer agree, so there is no
#     template-vs-writer conflict to resolve: the placeholder is a default, not
#     a type. It is NOT scalar-constrained -- the "constant" branch assigns the
#     whole cell contents, which need not be one element.
#  2. `string` is typed `string`, not NDI's `char`. `char` in did2 requires
#     ischar (cache.m validateTypeShape), and this field's declared default is
#     `[]`, which jsondecode returns as an empty DOUBLE -- so `char` would
#     reject the class's own default value. `string` accepts char,
#     cell-of-chars and the empty-numeric sentinel. A deliberate widening on a
#     preservation tombstone, stated here rather than left to be rediscovered.
#  3. The required-ness of `stimulus_element_id` DIFFERS between the two, and
#     not by oversight. NDI marks it `mustbenotempty: 1` on both. For
#     `stimulus_parameter` that is verified against the writer -- all three
#     ndi.document sites call set_dependency_value('stimulus_element_id', ...)
#     immediately after construction -- so it is declared required here.
#     `stimulus_parameter_table` has NO writer anywhere in NDI, so nothing
#     establishes that a real document populates it, and once #37 makes
#     mustBeNonEmpty on an edge actually enforced (it is skipped today by
#     +did2/+validate/references.m:90) that declaration becomes a quarantine
#     gate on documents we have never seen. Declared non-required, which is the
#     preserving direction for a class with nothing to model against.
_tombstone(
    "stimulus_parameter", ["base", "epochid"],
    [dep("stimulus_element_id", "subject",
         "The stimulus ELEMENT this parameter is a parameter of, promoted to a"
         " subject with its id preserved by migrators_j.element. Required: all"
         " three writer sites set it.",
         non_empty=True)],
    [field("ontology_name", "string",
           "The parameter's identity as a CURIE (e.g. NDIC:12). This is the"
           " field the live NDI queries pivot on"
           " (find_epochids_with_temperature.m:25, marder/demo.m:24)."),
     field("name", "string",
           "The human label for the parameter (e.g. 'Command temperature"
           " constant')."),
     field("value", "double",
           "The parameter's value. Numeric per NDI's schema and per the writer;"
           " the template's `\"\"` is a placeholder, not a type. Not"
           " scalar-constrained -- the constant branch assigns a whole cell.",
           scalar=False)])

_tombstone(
    "stimulus_parameter_table", ["base", "epochid"],
    [dep("stimulus_element_id", "subject",
         "The stimulus ELEMENT this table belongs to. NDI's schema marks it"
         " required; declared non-required here because the class has no writer"
         " anywhere, so no real document is known to populate it.",
         non_empty=False)],
    [field("string", "string",
           "The one field the class has. NDI documents it as 'an array of the"
           " order of stimulus presentation (each stimulus has an integer ID)'"
           " while typing it char -- an unresolved v1 shape, preserved as"
           " written. UNMODELLED: no writer, no reader, no documents.",
           scalar=False, queryable=False)])

# ---- stimulus_presentation: the last BLOCKING tombstone -------------------
#
# The third of the three tombstones held back for the stimulus model. What was
# holding it was the MODEL (what a presentation becomes); what is repaired here
# is the SOURCE SHAPE, which does not depend on the model at all.
#
# THE INVENTED EDGE. V_eta declared `element_id` required. NDI has never had
# such a dependency on this class -- template and schema both declare exactly
# one, `stimulus_element_id`, and the schema marks it `mustbenotempty: 1`:
#
#   $ git show origin/main:.../database_documents/stimulus/stimulus_presentation.json
#     "depends_on": [ { "name": "stimulus_element_id", "value": "" } ]
#   $ git show origin/main:.../schema_documents/.../stimulus_presentation_schema.json
#     "depends_on": [ { "name": "stimulus_element_id", "mustbenotempty": 1 } ]
#
# Both writers set it unconditionally and neither writes `element_id`:
#   +app/+stimulus/decoder.m:138
#       nd = set_dependency_value(nd,'stimulus_element_id',ndi_element_stim.id());
#   +mock/+fun/stimulus_presentation.m:136   (the same call)
#
# This is the 2,670-document row of the invented-empty-edge pattern -- 100% of
# the class, in four corpora (B 1242 / Dab 1242 / Soph 175 / 20211116 11). The
# edge is empty because nothing in v1 ever filled a field of that name, and it
# validated clean only because +did2/+validate/references.m:90 skips empty
# edges. Renaming the edge is the repair; there is no data to recover, because
# the real edge was being DROPPED while the invented one was carried.
#
# THREE PLACES THE WRITER BEATS THE TEMPLATE, all preserved here:
#  1. `app` stays in the superclasses. The template lists only base + epochid,
#     but decoder.m:135-137 constructs the document as
#     `E.newdocument(...) + ndi_app_stimulus_decoder_obj.newdocument()`, and the
#     right-hand term is what fills app.name/version/url/os/... So a real
#     document HAS an app block, and dropping the superclass would make every
#     one of them trip `undeclaredBlock` on the passthrough path.
#  2. `presentation_time` is a struct ARRAY (one entry per trial), not the
#     scalar the template's example shows -- decoder.m:107,124 build it with
#     `presentation_time(end+1)`. Hence scalar=False.
#  3. `stimuli` is likewise a struct ARRAY, one entry per DISTINCT stimulus:
#     tuning_response.m:194-195 loops `stimuli(j).parameters`.
#
# `presentation_time` is the DEPRECATED vintage and is NOT required. NDI moved
# it into presentation_time.bin ("we now put this in a file", decoder.m:133)
# but still reads the inline form when present, with a deprecation warning
# (decoder.m:154-157). Both vintages are real did_v1 documents, so the block is
# declared and optional -- required would quarantine every current document,
# absent would quarantine every old one.
_tombstone(
    "stimulus_presentation", ["base", "app", "epochid"],
    [dep("stimulus_element_id", "subject",
         "The STIMULATOR element -- NDI's only dependency on this class, in its"
         " template, in its schema (mustbenotempty: 1), at decoder.m:138 and in"
         " the mock. Typed `subject` because migrators_j.element promotes"
         " elements to subjects with their ids preserved, so the edge resolves."
         " REPLACES an invented `element_id` that no NDI document has ever"
         " carried.",
         non_empty=True)],
    [field("presentation_order", "matrix",
           "One 1-based index into `stimuli` per TRIAL, in presentation order"
           " (decoder.m:132 writes data.stimid(:)).",
           scalar=False),
     field("stimuli", "structure",
           "The stimulus dictionary: one entry per DISTINCT stimulus, each"
           " carrying an open-shape, generator-specific `parameters` block."
           " A struct ARRAY per the writer (tuning_response.m:194 indexes"
           " stimuli(j)), not the scalar the template's example shows.",
           scalar=False,
           sub_fields=[subfield("parameters", "structure",
                                "Open-shape and generator-specific: what the"
                                " stimulus generator recorded for this"
                                " stimulus. Left unmodelled on purpose -- the"
                                " parameters become typed fields of the"
                                " referenced stimulus data_type documents in"
                                " the second pass, not here.",
                                sub_fields=[])]),
     field("presentation_time", "structure",
           "The DEPRECATED vintage of per-trial timing: on the block instead of"
           " in presentation_time.bin. A struct ARRAY, one entry per trial."
           " decoder.m:154-157 still reads it (with a deprecation warning) and"
           " the template still declares it, so documents of both vintages are"
           " real did_v1. Optional, never required.",
           scalar=False, queryable=False,
           sub_fields=[subfield("clocktype", "string",
                                "Which clock the times below are in."),
                       subfield("stimopen", "double",
                                "When the stimulus object opened."),
                       subfield("onset", "double", "Stimulus onset time."),
                       subfield("offset", "double", "Stimulus offset time."),
                       subfield("stimclose", "double",
                                "When the stimulus object closed."),
                       subfield("stimevents", "matrix",
                                "Per-trial stimulus events. UNTYPED: nobody has"
                                " read real ones, so the shape is preserved"
                                " rather than declared.",
                                scalar=False)])],
    files=[("presentation_time.bin",
            ("Per-trial onsets/offsets, the CURRENT vintage. Absent on the"
            " deprecated inline vintage, so the file is declared, not"
            " required."))])

# ---- oneepoch: a did_v1 class that had NO V_eta schema at all -------------
#
# Not a wrong schema. NONE. `oneepoch` was tagged non-production in
# coverage.py's `_NONPROD_CLASSES`, which suppresses the coverage gap, so it
# reached 2026-08-10 with no schema, no migrator and no row on any worklist.
# A real document quarantines TODAY -- measured, not predicted (scratch probe 8,
# DID-matlab run 31423494433):
#
#     v1_to_v2(oneepoch_body, Validate=true, TargetVersion='V_eta')
#         migrated: 0   quarantine: 1
#         reason: No schema file for class "oneepoch"
#
# It IS production. `ndi.element.oneepoch` concatenates an element's N epochs
# into one; the writer is `src/ndi/element.m:387`, inside `addepoch`, and the
# reader is `+ndi/+element/oneepoch.m:78-80`. Both in src/, neither in tests/.
#
# WHAT THE CLASS ACTUALLY IS: the record of a CONCATENATION, not an epoch. Its
# one own field, `epoch_ids`, is the comma-joined list of the source epochs that
# were glued together. Everything else arrives by INHERITANCE -- `element_epoch`
# is its only declared superclass in NDI's template.
#
# The team chose fork A1 for the go-forward model on 2026-08-10 (the
# concatenation becomes a typed observation whose `derived_from_#` edges point at
# the N per-epoch observations; NO `epoch` entity is minted for the synthetic
# `whole_session_<ref>` id). That build is GATED on the raw-recording model being
# signed. THIS IS NOT THAT BUILD -- it is the passthrough repair that keeps the
# documents alive in the meantime, required under every fork.
#
# THE CHAIN AND THE FIELD NAMES WERE MEASURED, and one of them is not what the
# did_v1 template says:
#
#   * `oneepoch` keeps its own name -- nothing renames it.
#   * The chain is `base, epochid`, NOT NDI's `element_epoch, base, epochid`.
#     V_eta renames `element_epoch` to `acquisition_epoch`, so no class of that
#     name exists to inherit from. `migrators_j/oneepoch.m` folds the inherited
#     block onto the concrete one so the strict top-level check
#     (`did2:validation:undeclaredBlock`) has nothing left to reject.
#   * The block declares `clocks`, NOT `epoch_clock` + `t0_t1`. The BASE
#     superclass migrator (`did2.convert.migrators.element_epoch`) runs first and
#     has already collapsed the did_v1 pair into the array-of-records `clocks`.
#     Declaring the did_v1 names here would reject every real document. This is
#     the one place a tombstone deliberately does NOT restate the template shape,
#     and the reason is that the template shape never reaches the validator.
#
# `element_id` is REQUIRED, matching NDI (`element_epoch_schema.json`:
# `mustbenotempty: 1`) AND the writer -- `element.m:392` sets it unconditionally,
# outside the if/else that chooses between element_epoch and oneepoch.
#
# The `.vhsb` file is declared, which `acquisition_epoch` does NOT do. That is a
# known, separately-recorded defect on that class ("the dropped .vhsb payload" is
# one of the four in V_eta_epoch_plan.md); this class should not inherit the bug.
write("stable", "oneepoch",
      doc("oneepoch", ["base", "epochid"], version="2.0.0",
          deps=[dep("element_id", "subject",
                    "The element whose epochs were concatenated, promoted to a"
                    " subject with its id preserved by migrators_j.element."
                    " REQUIRED: NDI marks it so and element.m:392 always sets it.",
                    non_empty=True)],
          fields=[
              field("clocks", "structure",
                    "The concatenated epoch's extent, one record per clock."
                    " did_v1 stores this as `epoch_clock` (a COMMA-JOINED list of"
                    " every clock, oneepoch.m:124) plus a 2-by-N `t0_t1` matrix;"
                    " the base element_epoch migrator collapses that pair into"
                    " these records before validation ever sees the document."
                    " Under fork A1 these become relative_reference documents.",
                    scalar=False,
                    sub_fields=[
                        field("name", "char", "The clock identifier."),
                        field("t0", "double", "Start time in that clock."),
                        field("t1", "double", "End time in that clock."),
                    ]),
              field("epoch_ids", "string",
                    "The epoch ids that were concatenated, comma-joined, exactly"
                    " as did_v1 stores them. THE ONLY FIELD THE CLASS DECLARES"
                    " ITSELF, and the whole reason it is distinct from"
                    " element_epoch. Under fork A1 these resolve to"
                    " `derived_from_#` edges on the concatenated observation.",
                    scalar=False),
          ]))
_oe_tier, _oe_path = path_of("oneepoch")
_oe = load(_oe_path)
_oe["file"] = [{"name": "epoch_binary_data.vhsb",
                "documentation": "The concatenated samples, written by"
                                 " ndi.element.timeseries.addepoch from"
                                 " (timepoints, datapoints). Under fork A1 this"
                                 " becomes a sampled_body."}]
write(_oe_tier, "oneepoch", _oe)

# ---- subjectmeasurement: the ledger's last UNMAPPED class gets a home -----
#
# THE CLASS HAD NO V_eta SCHEMA AT ALL. `coverage.py` asserted, in
# `_PRE_ZETA_DISSOLVED`, that `subjectmeasurement` had dissolved into
# `measurement`. NDI NEVER DID THAT: subjectmeasurement is still a shipped
# template with four in-tree emitters, and `measurement` is a NEWER PARALLEL
# class added 2026-01-05, not a replacement. The false entry made the row read
# as deliberately retired while it in fact had nowhere to go. Removing it (this
# session) surfaced the gap; this closes it.
#
# TOMBSTONE ONLY, NO MIGRATOR, and both halves of that are deliberate.
#
# Not retired: none of the five corpora under test holds one of these, and all
# four emitters are test/demo builders writing the same hardcoded fixture
# (`measurement='age'`, `value=30`). It would be easy to call the class dead --
# and wrong. THE CORPORA ARE A SAMPLE OF DATASETS, not the universe; a dataset
# still waiting to migrate may be full of these, and those datasets are what the
# migration is for. Retiring on "we saw none" is the same inference that put the
# false dissolution claim in the ledger to begin with.
#
# Not modelled: `measurement` is FREE TEXT ('age') with no ontology binding --
# unlike measurement.ontology_name, which its writer resolves through
# ndi.ontology.lookup and errors if lookup fails -- and `value` carries NO UNIT
# anywhere in the class, template, or writer. `age = 30` is 30 of what? Days,
# weeks, years? Nothing says, and that is unknowable however many documents
# exist. A typed observation would have to invent the unit, which is precisely
# the failure this repair track exists to undo. So the document is preserved
# intact and lands in unconverted_by_class, where it is visible, until something
# real needs it modelled.
#
# NOTE FOR WHOEVER WRITES THE MIGRATOR: `subjectmeasurement.datestamp` SHADOWS
# `base.datestamp`. Harmless at validation (blocks are namespaced), but a
# migrator reading "the datestamp" must say which one it means.
write("stable", "subjectmeasurement", doc(
    "subjectmeasurement", ["base"],
    deps=[dep("subject_id", "subject",
              "The subject measured. Declared mustbenotempty by NDI.",
              non_empty=False)],
    fields=[
        field("measurement", "string",
              "The name of the measurement taken (e.g. 'age'). FREE TEXT --"
              " unbound, with no ontology term, unlike measurement.ontology_name"
              " which is always a resolved CURIE."),
        field("value", "matrix",
              "The value of the measurement. NO UNIT is recorded anywhere in the"
              " class, its template, or its writer, so the number is not"
              " interpretable on its own.", scalar=False),
        field("datestamp", "timestamp",
              "When the measurement was taken. SHADOWS base.datestamp -- a"
              " migrator must disambiguate."),
    ]))

# neuron_extracellular -- NOT an offender: its migrator reads the real
# `cluster_index` and `quality_number` (the detector's `quality` hit was a local
# MATLAB variable name, not a field read), and the tombstone's field list already
# matches the template exactly. Only the dependency list was short: the real
# class also carries spike_clusters_id, which was silently unreachable.
_nx = load(os.path.join(VETA, "stable", "neuron_extracellular.json"))
_nx["depends_on"].append(
    dep("spike_clusters_id", "spike_clusters",
        "The sorted-cluster document this unit came from. Declared by the NDI"
        " template; the tombstone previously listed only element_id.",
        non_empty=False))
write("stable", "neuron_extracellular", _nx)


# ==========================================================================
# THE LAST TWO did_v1 CLASSES THAT STRANDED COMPLETELY
# ==========================================================================
# `generic_file` and `valid_interval` had NO V_eta schema and NO migrator. Every
# other v1 class has at least one of the two. With neither, a document of these
# classes reaches validation as an undeclared class -- it is not migrated, not
# passed through, not quarantined-and-preserved. It is lost.
#
# Both were in DELETE. Neither deletion was made against the real class:
#
#   generic_file   deleted as a "2.D opaque fold (slice A)" into opaque_body, on
#                  a comment asserting `migrators_j.generic_file folds v1 docs`.
#                  0 of 82 migrators_j entries match generic|valid.
#   valid_interval deleted with no comment at all, in the same set-literal line
#                  as the ⑤ time-family classes (oneepoch, epochclocktimes,
#                  session_extent) -- which DO have dispositions.
#
# NEITHER IS BEING MODELLED HERE. Both get a source tombstone restated from the
# WRITER and nothing else, which is the vmspikefilteringparameters shape: with no
# migrator the document reaches validation in its did_v1 form, and a correct
# tombstone IS the whole fix. Marked `retire` in _RET_SOURCES so neither counts
# as a go-forward V_eta class -- these are v1 source names holding v1 documents
# alive until a model is SIGNED, exactly like `subjectmeasurement`.

# ---- generic_file --------------------------------------------------------
# WRITER CHECK, NDI origin/main, by BARE CLASS NAME across all 1467 files (not by
# one call idiom -- the mistake that nearly lost valid_interval):
#
#   git grep -c -I "generic_file" origin/main
#     src/ndi/+ndi/+cloud/+download/downloadGenericFiles.m           8
#     src/ndi/+ndi/+setup/+conv/+babu/import.m                      10
#     src/ndi/ndi_common/database_documents/data/generic_file.json   6
#     src/ndi/ndi_common/schema_documents/data/generic_file_schema.json  3
#     tests/+ndi/+unittest/+cloud/DownloadGenericFilesTest.m        13
#   (genericFile / genericfile: 0 files.  GenericFile: the 2 camel-named .m files
#    above, i.e. the function name, not a class spelling.)
#
# TWO PRODUCTION CONSTRUCTION SITES, +setup/+conv/+babu/import.m:526-531 (plasmid)
# and :575-580 (LC-MS), both identical in shape:
#
#   generic_file = struct('filename',<file>,'formatOntology','EMPTY:0000253', ...
#       'checksum',checksum,'dateCreated',dateCreated,'dateUpdated',dateUpdated);
#   doc = ndi.document('generic_file','generic_file',generic_file) + session.newdocument();
#   doc = doc.add_file('generic_file.ext',lcmsFile,'delete_original',0);
#   doc = doc.set_dependency_value('document_id',<subject_group or subject id>);
#
# So ALL FIVE fields are always populated, the file is ALWAYS attached, and the
# `document_id` edge is ALWAYS set. universalRenames snake_cases immediate block
# fields, so the migrator/validator sees format_ontology / date_created /
# date_updated (raw_fields in V_eta_ndi_ground_truth.json confirm the v1
# spellings) -- the ground-truth extract agrees field-for-field.
#
# TYPES. dateCreated/dateUpdated are MATLAB datenums -- `convertTo(...,'datenum')`
# at import.m:522-523,571-572 -- and generic_file_schema.json types both `double`.
# Writer and schema AGREE, so `double` it is. The TEMPLATE literal is `""` for all
# five fields; that is the placeholder trap, not evidence about documents, and no
# document this writer produces carries it.
#
# THE EDGE RESOLVES AFTER MIGRATION, which is not obvious and was checked rather
# than assumed: the plasmid branch points `document_id` at a `subject_group`, and
# subject_group is dissolved. But migrators_j/subject_group.m is a 1->1 fold to
# `subject` that carries the v1 `base` block through verbatim, so the id is
# PRESERVED and the edge still lands. Typed `subject` for that reason; the LC-MS
# branch points at a subject id directly.
#
# THE FOLD IS NOW BUILT, AND THE TOMBSTONE STAYS. Team decision 2026-08-11
# (V_eta_OPEN_WORK.md, "generic_file folds to opaque_body + a subject_statement"),
# option (a) verbatim: "opaque_body + a subject_statement whose variable comes
# from that sibling label". It runs DID-side as did2.convert.foldGenericFiles,
# a BATCH pass -- the `variable` lives in a different document (the sibling
# ontologyLabel), so nothing per-document can reach it.
#
# THE TOMBSTONE IS NOT DELETED and must not be. The fold REFUSES rather than
# guesses (no label / two labels / no document_id / referent not in the batch),
# and a refused document stays in exactly this v1 form. Deleting the class would
# turn every refusal into a quarantine -- the epochfiles_ingested regression, and
# the same mistake image_stack made and had reversed.
#
# WHAT CHANGED SINCE THE "no fold is built" NOTE THAT STOOD HERE:
#   - opaque_body GAINED content_hash (see the ⑥ section below), so `checksum`
#     lands. That was the blocker this comment named.
#   - the "no statement class exists" half was half-right and is corrected: the
#     DIRECTION was decided by the team, and `subject_id` resolves because
#     migrators_j.subject_group folds 1->1 with the id preserved (already
#     reasoned out in the dep documentation below).
# WHAT IS STILL OPEN, AND IS STATED IN THE PASS'S OWN HEADER RATHER THAN HIDDEN:
#   - `date_created` / `date_updated` have NO home in the SIGNED data_body model
#     (sec.6 lists format / compression / filename / content_hash / description
#     and no dates), so the fold carries them nowhere. They survive only on a
#     REFUSED document. This is a second lost field, smaller than `checksum` and
#     not named by the decision, which said the remaining blocker was one field.
#   - the leaf class. `subject_statement` is ABSTRACT
#     (did2:validation:abstractInstantiation), every concrete statement is
#     direction x data_type (T3), and NO data_type composite carries an
#     uninterpreted payload. See foldGenericFiles.m for the choice made and why.
_tombstone(
    "generic_file", ["base"],
    [dep("document_id", "subject",
         "The document this file belongs to. NDI's ONLY dependency on this"
         " class, and its schema marks it mustbenotempty: 0. The writer always"
         " sets it -- to a `subject_group` id (plasmid branch) or a subject id"
         " (LC-MS branch). Typed `subject` because migrators_j.subject_group"
         " folds 1->1 to `subject` carrying the v1 `base` block, so the id is"
         " preserved and the edge resolves after migration. Declared OPTIONAL"
         " anyway: must_refer is existence-only and a tombstone must not reject"
         " a document an older writer produced.",
         non_empty=False)],
    [field("filename", "string",
           "The original full file path and name, verbatim from the source"
           " tree (e.g. '/Users/lab/Documents/YYMMDD/subject/file.jpg')."),
     field("format_ontology", "string",
           "An ontology node naming the FILE FORMAT, as `ontology:nodeID`. The"
           " writer emits 'EMPTY:0000253' for plasmid files and"
           " 'EDAM:format_3620' for the LC-MS tables. Spelled `formatOntology`"
           " in did_v1; snake_cased by universalRenames. NOT declared"
           " `ontology_term`: v1 stores a bare CURIE string, not the"
           " {node, name} pair that composite requires, and manufacturing the"
           " `name` half is exactly the invention a tombstone must not make."),
     field("checksum", "string",
           "The MD5 checksum of the file (ndi.fun.file.MD5). THIS FIELD USED TO"
           " BLOCK THE opaque_body FOLD -- opaque_body had no content_hash, so"
           " folding would have dropped it. opaque_body now declares"
           " `content_hash` and did2.convert.foldGenericFiles carries this"
           " value into it verbatim."),
     field("date_created", "double",
           "When the file was created, as a MATLAB datenum. Typed `double` by"
           " generic_file_schema.json AND written as a datenum double by the"
           " writer (convertTo(...,'datenum')) -- they agree. The template's"
           " literal `\"\"` is a placeholder; no document from this writer"
           " carries it. Spelled `dateCreated` in did_v1."),
     field("date_updated", "double",
           "When the file was last updated, as a MATLAB datenum. Same"
           " writer/schema agreement as date_created. Spelled `dateUpdated`"
           " in did_v1.")],
    files=[("generic_file.ext",
            ("The file itself, uninterpreted bytes. NDI names the slot with a"
            " literal `.ext` -- the real extension is recoverable only from"
            " `filename`, which is what downloadGenericFiles.m:107-126 does."))])

# ---- image_collection ----------------------------------------------------
# TEAM DECISION 2026-08-11: treat `imageCollection` as a tombstone. It is the
# migration's one genuine unhomed class -- no V_eta home, no migrator -- and two
# INDEPENDENT instruments already say so: the coverage ledger's UNVERIFIED row
# and the NDI required-ness stamp's NOT-COMPARED bucket. It came out of DELETE
# in the same change; the corrected record of what that comment claimed is up
# there, not repeated here.
#
# WRITER CHECK, NDI origin/main -- AND THIS ONE HAS NO WRITER, WHICH IS ITSELF
# THE FINDING. Stated as the commands, with the denominator first, because the
# whole claim rests on a zero and this repository has twice reported a zero that
# was a property of the query (`demo_ndi` against a repo that spells it
# `demoNDI`; `valid_interval` against one call idiom out of several):
#
#   $ git -C NDI-matlab ls-tree -r origin/main --name-only | grep -c '\.m$'
#   1002                                            <- the denominator
#   $ git -C NDI-matlab grep -l -i imageCollection      origin/main -- '*.m' | wc -l
#   0
#   $ git -C NDI-matlab grep -l    image_collection     origin/main -- '*.m' | wc -l
#   0
#   $ git -C NDI-matlab grep -l -i imagecollection      origin/main -- '*.m' | wc -l
#   0
#
# All three spellings, over every .m file on origin/main: 0. No construction
# site, no reader, no name mention. So THE TEMPLATE IS THE ONLY EVIDENCE THERE
# IS -- there is no writer to check it against, and the standing rule "where
# template and WRITER disagree the WRITER wins" simply cannot fire here. Every
# field, type and dependency below therefore comes from the NDI pair and nothing
# else, and that is a weaker footing than `generic_file`'s two live call sites.
# Say so rather than let the tombstone read as equally well-founded.
#
#   database_documents/data/imageCollection.json      (the property template)
#       superclasses  base
#       depends_on    subject_id
#       imageCollection { label, format }
#   schema_documents/data/imageCollection_schema.json (types + requiredness)
#       depends_on    subject_id   mustbenotempty: 0
#       label   string   queryable 1
#       format  string   queryable 1
#
# NO `files` BLOCK, IN EITHER FILE -- and that is the point at which the
# image_stack defect of 2026-08-10 would repeat if this were written from the
# V_zeta shape instead. V_zeta declares a file named `collection_file`, inherited
# from schemas/V_alpha/imageCollection.json; NDI declares no file at all.
# universalRenames SKIPS the structural keys outright (`skip =
# {'document_class','depends_on','file','files'}`, DID-matlab
# +did2/+convert/universalRenames.m:308), so a file name reaches validation in
# did_v1 spelling, VERBATIM -- which means declaring one NDI does not write is
# not a harmless extra, it is `did2.validate.fileList` comparing by exact strcmp
# against a slot no document fills. So: `files=()`, deliberately, and if a real
# document ever turns up carrying an attachment, its NDI-side name is what goes
# here -- not a snake_cased invention.
#
# `image.json` declares an `imageCollection_id` dependency, which is the only
# thing in NDI that points at this class. V_eta's `image` is the R6 data_type and
# carries no dependencies at all, so nothing here needs to resolve that edge; it
# is recorded because it is why the class exists.
#
# Everything is OPTIONAL. NDI's own schema marks the single dependency
# `mustbenotempty: 0`, and with no writer there is no evidence any field is
# reliably populated -- a required field would be this tombstone quarantining the
# documents it exists to preserve, which is the whole failure mode of the
# Phase-2b sweep.
_tombstone(
    "image_collection", ["base"],
    [dep("subject_id", "subject",
         "The subject the collected images depict. NDI's ONLY dependency on this"
         " class, and its schema marks it mustbenotempty: 0. NOT `element_id` --"
         " that name comes from the V_alpha snapshot (schemas/V_alpha/"
         "imageCollection.json) and appears in no NDI template.",
         non_empty=False)],
    [field("label", "string",
           "A text label associated with the image collection. NDI's own"
           " documentation string; typed `string` by imageCollection_schema.json."),
     field("format", "string",
           "The format of the imageCollection (e.g. 'tiff', 'svs', 'czi'). NDI's"
           " own documentation string and examples. NOT `image_format` -- that"
           " spelling is the V_alpha snapshot's, not NDI's.")])

# ---- valid_interval ------------------------------------------------------
# WRITER CHECK, NDI origin/main. The call-idiom trap reproduces exactly:
#
#   git grep -c -I "ndi.document('valid_interval'" origin/main   ->  0 files
#   git grep -c -I "valid_interval" origin/main
#     src/ndi/+ndi/+app/markgarbage.m                                 5
#     src/ndi/ndi_common/database_documents/apps/markgarbage/valid_interval.json  5
#     src/ndi/ndi_common/resources/ndiDocumentAttributes.json         1
#     src/ndi/ndi_common/schema_documents/apps/markgarbage/valid_interval_schema.json  2
#
# THE WRITER, markgarbage.m:64-97 (savevalidinterval):
#
#   [vi,~] = loadvalidinterval(epochset);       % read the existing array back
#   vi(end+1) = validintervalstruct;            % APPEND
#   clearvalidinterval(epochset);               % delete the old document
#   newdoc = session.newdocument('valid_interval','valid_interval',vi) + newdocument();
#   newdoc = newdoc.set_dependency_value('element_id', epochset.id());
#
# and each entry, from markvalidinterval at :55-58, is
# {timeref_structt0, t0, timeref_structt1, t1}.
#
# A SECOND PRODUCTION CONSUMER, not previously recorded: the tuning pipeline.
# +ndi/+app/+stimulus/tuning_response.m:253-256 calls loadvalidinterval and then
# identifyvalidintervals, and uses the result to choose the stretch of signal it
# reads. So losing this class does not only lose a curation annotation -- it
# silently changes what data a re-run of the tuning calculators would analyse.
#
# WRITER vs TEMPLATE, and the writer wins: `session_ID`.
# markgarbage.m:55,57 fill both timeref blocks from
# ndi.time.timereference.ndi_timereference_struct(), which returns SIX fields
# (timereference.m:106-111): referent_epochsetname, referent_classname,
# clocktypestring, epoch, session_ID, time. The TEMPLATE declares only five --
# no session_ID -- and never has:
#
#   git log --all --oneline -S"session_ID" -- '*valid_interval.json'   ->  0 commits
#
# Undeclared, that sixth field is `did2:validation:undeclaredField` on every real
# document. It is declared here in its CAMEL spelling deliberately:
# universalRenames snake_cases only the IMMEDIATE field names of a block
# (universalRenames.m:302-347 -- "nested struct values are left alone"), and
# session_ID is nested one level down inside timeref_structt0/t1.
#
# TWO FABRICATED CONSTRAINTS REMOVED from the V_zeta shape this replaces:
#   - clocktypestring carried an `enum` of SIX values. The real vocabulary is
#     NINE (clocktype.m:69-71): utc, approx_utc, exp_global_time,
#     approx_exp_global_time, dev_global_time, approx_dev_global_time,
#     dev_local_time, no_time, inherited. The three the enum omitted --
#     approx_exp_global_time, approx_dev_global_time, inherited -- would each
#     have quarantined a real document on a constraint DID invented. Declared
#     with NO enum rather than with the corrected nine: a tombstone's job is to
#     let a v1 document survive, and older writers are not evidence-checkable.
#   - `epoch` was typed `char`, and `time` + the timeref blocks were REQUIRED.
#     timereference.m:71 sets `epoch = []` whenever the clock does not need one,
#     and its own header says the epoch is "either a string or a number"
#     (timereference.m:26,102). `char` rejects BOTH -- validateTypeShape
#     (cache.m) accepts only char/string for `char`, while `string` also accepts
#     an empty numeric. Declared `string` for that reason, the same call already
#     made for vmspikesummary.slope_criterion. RESIDUAL RISK, RAISED NOT HIDDEN:
#     a NUMERIC epoch number still fails the type check, and the meta-schema has
#     no union type. An open question for a human, not something to paper over.
#
# WHY NO MODEL IS BUILT. `V_eta_time_reference_model_plan.md` already reasons
# about this class (its decision C is about markvalidinterval's two independently
# anchored ends), but that plan's BUILD is deferred, and there is no leaf that
# says "this stretch of the recording is good data" -- valid_interval is neither
# an observation of the subject nor a manipulation of it, it is a curation
# judgement ABOUT a recording. Naming that tier is a team call.
#
# THE ONE THING THIS TOMBSTONE CANNOT EXPRESS -- read the report, this is an open
# question, not a solved problem. `valid_interval` is the ONLY one of NDI's 91
# templates whose property block is a JSON ARRAY rather than an object (checked
# mechanically: 91 template files, 91 parsed, 0 unparseable, 1 array block). The
# writer APPENDS, so a probe with three marked intervals has ONE document holding
# a 3-element struct array -- accumulation is the normal path, not an edge case.
# The DID meta-schema declares `fields` on a scalar block and has no way to say
# "the block is an array of these". The declaration below is therefore correct for
# the single-interval document (the template's own shape) and UNDER-SPECIFIED for
# a multi-interval one. It is still strictly better than no schema at all, which
# is what this class had.
#
# CONSEQUENCE FOR tools/check_tombstones.py -- DO NOT ACT ON ITS ROW HERE. Because
# the block is an array, ndi_ground_truth.py reads `fields: []` for this class, so
# the checker reports
#
#     COSMETIC  passthrough valid_interval
#         declared but in no NDI template: t0, t1, timeref_structt0, timeref_structt1
#
# All four ARE in the template. Following that row and deleting them would
# re-strand the class -- the same trap as the ontology_image / `ontologyNodes`
# row, arriving through the block's SHAPE rather than through a field spelling.
_VALID_INTERVAL_TIMEREF_SUBS = [
    field("referent_epochsetname", "string",
          "epochsetname() of the referent -- the probe/element/daq system whose"
          " clock this time is expressed in."),
    field("referent_classname", "string",
          "MATLAB class of the referent (e.g. 'ndi.probe.timeseries.mfdaq')."
          " With referent_epochsetname it is how v1 re-finds the object:"
          " session.findexpobj(name, classname) at timereference.m:46."),
    field("clocktypestring", "string",
          "The clock this time is measured on. NDI's vocabulary is NINE values"
          " (clocktype.m:69-71): utc, approx_utc, exp_global_time,"
          " approx_exp_global_time, dev_global_time, approx_dev_global_time,"
          " dev_local_time, no_time, inherited. Deliberately declared with NO"
          " enum -- the V_zeta shape this replaces enumerated only six and would"
          " have rejected the other three."),
    field("epoch", "string",
          "The epoch providing the time origin. Required only when the clocktype"
          " needsepoch(); otherwise timereference.m:71 leaves it EMPTY. NDI"
          " documents it as 'either a string or a number' -- declared `string`"
          " because that type also accepts the empty-numeric case, but a numeric"
          " epoch number would still fail the type check and the meta-schema has"
          " no union type. Open question."),
    field("session_ID", "string",
          "The session containing the epoch. WRITTEN BY THE WRITER"
          " (timereference.m:110, via ndi_timereference_struct) and DECLARED BY"
          " NO NDI TEMPLATE -- 0 commits in valid_interval.json's history mention"
          " it. Declared here because the writer wins, and because an undeclared"
          " block field is `undeclaredField` on every real document. Kept in its"
          " CAMEL spelling on purpose: universalRenames snake_cases only a"
          " block's immediate field names, and this one is nested."),
    field("time", "double",
          "The time offset, in the units of clocktypestring, that serves as the"
          " origin."),
]
_tombstone(
    "valid_interval", ["base", "app"],
    [dep("element_id", "subject",
         "The element -- in practice a PROBE, since savevalidinterval errors on"
         " anything else (markgarbage.m:76-78) -- whose data these intervals"
         " judge. Typed `subject` because migrators_j.element promotes elements"
         " to subjects with their ids preserved. NDI's schema marks it"
         " mustbenotempty: 1 and the writer always sets it (markgarbage.m:95);"
         " declared OPTIONAL here to match every sibling tombstone and because a"
         " tombstone must not be the thing that rejects a v1 document.",
         non_empty=False)],
    [field("timeref_structt0", "structure",
           "The time reference the interval's START is expressed against"
           " (markgarbage.m:55).", sub_fields=_VALID_INTERVAL_TIMEREF_SUBS),
     field("t0", "double",
           "Start of the valid interval, in the units of timeref_structt0."),
     field("timeref_structt1", "structure",
           "The time reference the interval's END is expressed against"
           " (markgarbage.m:57). SEPARATE from timeref_structt0 by design:"
           " markvalidinterval takes an independent timeref for each end.",
           sub_fields=_VALID_INTERVAL_TIMEREF_SUBS),
     field("t1", "double",
           "End of the valid interval, in the units of timeref_structt1.")],
    ())

# ==========================================================================
# `logical` + `logical_observation` -- the GO-FORWARD HOME for valid_interval
# ==========================================================================
# TEAM DECISION 2026-08-12, jess@walthamdatascience.com: `validity` and
# `validity_observation` are REPLACED by `logical` and `logical_observation`.
#
# THE HISTORY, KEPT ACCURATE BECAUSE IT HAS BEEN MIS-RECORDED ONCE ALREADY.
# On 2026-08-11 the team ASKED *"Should valid interval be a new class that takes
# a subject statement, shares its time reference and states true or false for
# each value?"* and then said *"Can we skip this decision for now?"*. That
# question was written up as a decision and put in a signature (OPEN_WORK #103);
# it was NOT one. The shape below is still BUILT AHEAD OF THAT DECISION. What
# WAS decided, on 2026-08-12, is the CLASS NAMING -- the rename this block
# implements. Do not read the rename's decidedness as covering the model.
#
# WHY THE RENAME (the team's own reasoning, recorded so it is not paraphrased
# away). The 32 `*_observation` data_types name a KIND OF VALUE -- length,
# intensity, count, score, term, image. `validity` was the only one naming a
# SEMANTIC: what the measurement is ABOUT. The semantic belongs in
# `subject_statement.variable`, and that is not a theory -- it is what the live
# table-column pass already does. `resolveLawnPlateSubjects.m:1106-1113` maps
# EIGHT source columns onto THREE data_types, SIX of them onto the single
# `intensity_observation`, told apart only by `variable`
# (`:689 variableTerm(c{1})` -> `:1317 body.subject_statement.variable`):
#
#     bacterialpatchborderpeakfluorescenceintensity   intensity_observation
#     bacterialpatchborderedgefluorescenceintensity   intensity_observation
#     bacterialpatchborderfluorescenceamplitude       intensity_observation
#     bacterialpatchmeanfluorescenceamplitude         intensity_observation
#     bacterialpatchcenterfluorescenceamplitude       intensity_observation
#     bacterialpatchbordertocenterfluorescenceratio   intensity_observation
#
# It is also the error R2/R3 already fixed once, one tier up: six v1 tuning
# classes named by their INDEPENDENT VARIABLE collapsed into one `tuning_curve`
# with the variable carried as a `variable` (T11, V_eta_tuning_model_plan.md).
#
# WHY `logical` AND NOT `boolean`. `boolean` is IMPOSSIBLE, not merely
# undesirable: it is a hard-coded primitive in the validator's type switch --
# DID-matlab `src/did/+did2/+schema/cache.m:1793`,
#
#     case 'boolean'
#         if ~(islogical(value) || (isnumeric(value) && all(value(:) == 0 | value(:) == 1)))
#             error('did2:validation:typeMismatch', ...
#
# so a COMPOSITE of that name would send every struct-valued field carrying it
# into that scalar/array check. `logical` follows the EXISTING precedent
# exactly: the data_type `term` wraps the field type `ontology_term`; the
# data_type `logical` wraps the field type `boolean`. Different strings, no
# collision, same shape.
#
# THE TOMBSTONE ABOVE IS NOT DELETED AND IS NOT SUPERSEDED. It keeps the v1
# documents alive under their own class; these two classes are where the fact
# GOES FORWARD. Both live for as long as `did2.convert.resolveValidIntervals`
# has not been shown, on a corpus, to decompose every source document -- the
# verify-before-delete rule this project has now paid for twice
# (epochfiles_ingested, image_stack).
#
# WHY A NEW COMPOSITE AT ALL (T12, the parsimony test -- run, not skipped).
#   1. same shape, different meaning?   NO -- no existing composite carries a
#                                       BOOLEAN. `count` is an integer + a
#                                       semantic unit, `score` a double + a
#                                       rubric, `term` a {node,name} pair.
#   2. a controlled term?               The team asked for true/false, twice.
#                                       A `term_observation` over a two-member
#                                       value_set would encode a boolean as a
#                                       vocabulary, which is T13's "name the
#                                       content" failure one level down.
#   3. same quantity, other cardinality? There is no such quantity yet.
#   4. a role or relationship?          NO -- it is a value about a subject.
# So 1-4 all fail and a composite is warranted. It is the ONLY boolean-valued
# data_type in V_eta and it is meant to stay that way: a second boolean fact
# ("did the animal respond?", "was the epoch a control?", "was this trial
# aborted?") reuses `logical` and changes `variable` (rule 1). That is exactly
# what the name buys -- `validity` could not have been reused for any of them.
#
# NO NESTED CELL. The old `validity` shape was a `value` of type `validity`
# wrapping a one-field struct `{value: boolean}` -- `value.value`, a wrapper
# around nothing. The other composites nest because they carry PROVENANCE:
# `length` wraps meters + source_unit + source_value, `count` wraps value +
# unit + approximate. A boolean has no unit, no source unit, and cannot be
# approximate. The precedent for a bare payload is `term`, whose `value` is
# typed `ontology_term` directly. So the sub-field list is DELETED, not
# renamed, and `logical` is NOT registered in the meta-schema's
# `field_definition.type` enum -- nothing declares a field of type `logical`,
# and an enum entry with no declared layout would fail
# test_named_composite_cells_declare_their_layout.
#
# THE STANCE IS `_observation`, and that is a judgement worth stating (T13: the
# stance word must be TRUE, not convenient). It is not an `_assertion`: an
# assertion is a TIMELESS fact and declares no `time_reference_#` edge, and the
# entire content here is "over THIS stretch of time". It is not a
# `_manipulation` (nothing is done TO the subject) and not a `_calculation`
# (markgarbage is a human curation act, not a computation -- there is no
# algorithm and no input document). What remains is the observation: a curator
# looked at the recording and reports what they saw of it.
#
# HAZARD 1 -- ABSENCE MUST KEEP MEANING "VALID". `ndi.app.markgarbage` is
# OPT-IN. Today, NO `valid_interval` document for an element means the WHOLE
# epoch is good data; that is the semantics `identifyvalidintervals` implements
# (markgarbage.m:172-176: `if isempty(vi); intervals = [t0 t1]; return; end`).
# So:
#   * NOTHING declares a dependency on `logical` or `logical_observation`,
#     and neither is a superclass of anything. Nothing can require one.
#     tests/test_veta.py::test_absence_of_a_logical_statement_must_keep_meaning_valid
#     is the mechanical gate on that, over every built schema. (This comment
#     used to cite `test_validity_is_never_required_by_anything`, a test that
#     has never existed under that name in this repository -- the assertion is
#     the first half of the test named above.)
#   * NO document is minted for an element that has none -- the migration path
#     reads `valid_interval` documents and nothing else.
#   * the reading rule is DECLARED on the class (T14: a convention that lives
#     in prose is not a convention), so a consumer that never read this file
#     still gets it right.
#   THE RULE IS NOW SCOPED BY `variable`, AND IT HAD TO BE. `validity` named
#   the semantic, so "absence of every statement of this class" and "absence of
#   every statement about data validity" were the same sentence. `logical` is
#   generic, so they are not: a subject with no statement about "was this trial
#   aborted" says nothing whatever about its data validity. The declared rule
#   below therefore reads "absence of every `logical` statement about a
#   SUBJECT'S DATA VALIDITY", which is what the v1 semantics actually is.
#
# HAZARD 2 -- ORDER IS NOT LOAD-BEARING, AND THE OLD COMMENT HERE SAID THE
# OPPOSITE. It read: *"`+app/+stimulus/tuning_response.m:253-256` restricts the
# stretch of signal it analyses to `interval(1,1)`..`interval(1,2)` -- the FIRST
# interval. In v1 that order is array-append order"*, and it is what `sequence`
# existed for. THAT IS WRONG, and the positive evidence is the two call sites
# themselves, read from NDI `origin/main` (42c94e53b):
#
#     $ git show origin/main:src/ndi/+ndi/+app/+stimulus/tuning_response.m
#       253:  vi = gapp.loadvalidinterval(ndi_timeseries_obj);
#       254:  interval = gapp.identifyvalidintervals(ndi_timeseries_obj,timeref,0,Inf);
#       256:  [data,t_raw,timeref] = readtimeseries(..., interval(1,1), interval(1,2));
#
# `interval` is the RETURN VALUE of `identifyvalidintervals`; the stored array
# `vi` is loaded into a variable that is then never read. And
# `identifyvalidintervals` (markgarbage.m:178-204) does this:
#
#     for i=1:size(vi,1)
#         ...
#         explicitly_good_intervals = vlt.math.interval_add( ...
#             explicitly_good_intervals, [epoch_t0_out epoch_t1_out]);
#     end
#
# -- it iterates EVERY row and accumulates through a set union. It never indexes
# `vi` by position. So v1's append order is invisible to its only consumer: it
# is a storage artifact, not a fact. `sequence` IS DELETED.
#   LIMIT OF THIS CHECK, STATED RATHER THAN GLOSSED: `vlt.math.interval_add` is
#   in vhlab-toolbox-matlab, which is not in this container and could not be
#   attached, so whether the union SORTS its output was not read from source.
#   The claim above does not depend on it -- `interval(1,1)` indexes the union's
#   output, not the stored array, and one v1 document's rows are unordered
#   INPUT to that union either way -- but the sort behaviour itself is
#   unverified here.
#
# HAZARD 3 -- VALIDITY INHERITS, AND THAT IS NOT DECIDED HERE.
# `loadvalidinterval` falls back to `underlying_element` when a derived element
# has no intervals of its own (markgarbage.m:146-155). That is a QUERY-TIME rule
# in NDI, and whether V_eta re-derives it through `derived_from` or materialises
# it onto the derived subject is an OPEN SUB-QUESTION for the team. NOTHING here
# forecloses either answer:
#   * `subject_id` is the element the v1 document named and nothing else, so a
#     re-derivation still has the exact v1 graph to walk;
#   * `subject_observation.derived_from_#` already exists (optional, min_count
#     0), so a materialising decision has its edge with no schema change.
# What a later decision WOULD have to change is written out in
# did2.convert.resolveValidIntervals's header, next to the counter that
# measures how often the fallback could fire.
write("draft", "logical",
      doc("logical", ["data_type"], abstract=True, maturity="draft",
          fields=[field(
              "value", "boolean",
              "The truth value(s) this statement asserts. WHAT the boolean is"
              " ABOUT lives in `subject_statement.variable`, not in the class"
              " name -- that is the whole reason this class is `logical` and"
              " not `validity`. Series-as-cardinality (Brainstorm I): an ARRAY,"
              " length 1 for a single judgement. NO NESTED CELL: a boolean has"
              " no unit, no source unit and cannot be approximate, so there is"
              " no provenance triple to wrap it in (`term.value` is typed"
              " `ontology_term` directly for the same reason)."
              " FOR THE `valid_interval` FOLD, EACH CELL IS ONE INTERVAL, NOT"
              " ONE SAMPLE. A per-sample validity mask needs the sample grid,"
              " and no migrator reads file bytes to learn it (confirmed via"
              " pyraview) -- the mask is derivable from the intervals by anyone"
              " holding the grid, the reverse is lossy, and a mask over a long"
              " recording is exactly the rebuildable cache T6/T10 say not to"
              " store as source."
              " ABSENCE OF *EVERY* `logical` STATEMENT ABOUT A SUBJECT'S DATA"
              " VALIDITY MEANS ITS DATA IS VALID -- ndi.app.markgarbage is"
              " opt-in and identifyvalidintervals returns the whole requested"
              " span when it finds no record (markgarbage.m:172-176). The rule"
              " is scoped BY `variable` because this class is generic: no"
              " statement about some OTHER boolean variable says anything about"
              " validity."
              " THAT RULE IS SCOPED TO *NO STATEMENT AT ALL*, AND IT DOES NOT"
              " EXTEND TO THE GAPS BETWEEN STATEMENTS. WHAT A GAP MEANS IS"
              " UNDEFINED HERE AND IS AN OPEN TEAM DECISION -- do not read one"
              " as valid. In v1 it is the opposite: `markvalidinterval` marks a"
              " valid interval '(all else is garbage)' (markgarbage.m:42), and"
              " once ANY interval projects into an epoch"
              " identifyvalidintervals returns ONLY the marked ones"
              " (markgarbage.m:200-204), so a v1 gap is GARBAGE. Decomposing"
              " one v1 document into N statements does not carry that closure,"
              " so it is deliberately NOT claimed rather than silently"
              " inverted. Declared here rather"
              " than left to prose (T14) because a reader who assumes"
              " 'no statement = unknown' silently reclassifies every epoch in"
              " every dataset that never ran markgarbage."
              " ========== READING RULES FOR A V_eta CONSUMER (team,"
              " 2026-08-12). Declared here and not left in prose (T14), for the"
              " same reason the absence rule above is: a consumer that never"
              " read our plan documents still has to get these right, and every"
              " way of getting them wrong is SILENT. They govern V_eta"
              " consumers; they change nothing about ndi.app.markgarbage."
              " (1) INHERITANCE WALKS THE WHOLE `derived_from` CHAIN,"
              " TRANSITIVELY. A subject with no `logical` statement for a given"
              " `variable` inherits from its `derived_from` ancestors to ANY"
              " DEPTH -- electrode -> filtered -> neuron reaches the electrode."
              " The chain is in the migrated graph:"
              " `migrators_j/element.m:130-131` emits a `derived_from` lineage"
              " relation for every `underlying_element_id`. WHAT THIS DIVERGES"
              " FROM, STATED PRECISELY: it is NOT depth. NDI's"
              " `loadvalidinterval` fallback DOES recurse -- markgarbage.m:149"
              " calls `loadvalidinterval` on `underlying_element` and that"
              " function contains the same fallback block. The divergences are"
              " (a) the EDGE: NDI walks `underlying_element`, a property of a"
              " live NDI runtime object; V_eta walks `derived_from`, an edge in"
              " the migrated document graph, which is the only lineage a"
              " consumer holding documents can see; and (b) the SCOPE: v1 has"
              " one kind of validity and no `variable`, so its walk cannot be"
              " scoped and this one MUST be -- inheriting a statement about"
              " some other boolean variable would be a different fact"
              " altogether."
              " (2) INHERITANCE YIELDS THE STATEMENT WITH ITS ANCHOR, NEVER THE"
              " INTERVAL NUMBERS ALONE. The times mean nothing without the"
              " `time_reference_#` that anchors them, so an inheriting consumer"
              " converts through the syncgraph exactly as if it had asked about"
              " the ancestor directly. This MIRRORS v1 rather than diverging"
              " from it: `identifyvalidintervals` rebuilds each interval's own"
              " anchor (`ndi.time.timereference(session, vi(i).timeref_structt0)`"
              " at markgarbage.m:181-182) and calls"
              " `syncgraph.time_convert` into the caller's frame"
              " (markgarbage.m:184-189)."
              " (3) THERE ARE THREE STATES, NOT TWO, AND THE THIRD IS A"
              " DELIBERATE BREAK FROM v1. No statement anywhere in the chain"
              " => VALID (the absence rule above, unchanged). Statements found"
              " and projected => USE THEM. Statements found but NONE could be"
              " projected into the caller's frame => UNKNOWN, AND NOT VALID."
              " v1 collapses the third into the first: an unprojectable"
              " interval is skipped with the comment `so we say the region is"
              " valid, we have no restrictions to add` (markgarbage.m:190), and"
              " if none projects the function returns `baseline_interval` --"
              " the ENTIRE requested span (markgarbage.m:198-199). So in v1 a"
              " clock mismatch reads as 'all of this data is good'. The two"
              " facts are opposites: 'nobody marked this' and 'somebody marked"
              " this and we could not read their clock'. Only the first is good"
              " data. RULE 1 MAKES THIS MATTER MORE OFTEN, not less -- walking"
              " the whole chain multiplies the chances of reaching an ancestor"
              " whose anchor does not project."
              " (4) THE FAILURE MUST BE COUNTABLE. A consumer REPORTS the"
              " number of inherited statements it could not project. A silent"
              " permissive fallback is the failure this project has paid for"
              " repeatedly (silentLoss printing 0 while reading nothing), and"
              " rule 3 is unenforceable without a number: 'unknown' and 'valid'"
              " are indistinguishable in the output otherwise. =========="
              " TRUE = this stretch is GOOD DATA, FALSE = this stretch is"
              " GARBAGE. did_v1 could only express TRUE -- validity was encoded"
              " in the CLASS NAME (`valid_interval`), so 'this stretch is bad'"
              " was expressible only as absence, and markgarbage's own author"
              " wrote the gap down: `% developer note: it would be great to"
              " have a 'markinvalidinterval' companion` (markgarbage.m:40). A"
              " migrated document therefore always carries TRUE; FALSE is"
              " reachable only by a writer that states invalidity directly.",
              non_empty=True, scalar=False, blank=[])]))
# NO FIELDS AT ALL -- the same as `length_observation` and `count_observation`.
# `sequence` is gone with HAZARD 2 (see above); everything else the leaf needs
# (`subject_id`, `variable`, `time_reference_#`) is INHERITED from
# subject_statement / subject_interaction, which is what "takes a subject
# statement" meant.
write("draft", "logical_observation",
      doc("logical_observation", ["subject_observation", "logical"],
          maturity="draft"))


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
# THE HOIST (#45 step 2, signed sec.6). Everything about the BYTES moves here;
# the statement says what the values ARE, the body says how the bytes ENCODE
# them. `data_body` carried NOTHING before this -- the five fields sat on the
# children, `format`/`filename`/`description` on opaque_body only, and
# `content_hash` on both.
#
# THE `statement` EDGE IS REQUIRED, AND THAT IS THE HALF THE PLAN LEFT OPEN.
# It said "ONE required-ness, settled here" without saying which; the children
# disagreed (sampled_body REQUIRED, opaque_body OPTIONAL) and a child cannot
# tighten a parent field (#69), so the hoist forces one answer. Team decision
# 2026-08-14, on this measurement:
#
#     DENOMINATOR: 195 .m file(s) under DID-matlab +convert/, 842 under
#                  NDI-matlab src/; code paths that MINT a data_body: 3
#       DID  +migrators_j/private/jSorterOutput.m              sets statement
#       DID  foldGenericFiles.m                                sets statement
#       NDI  +migrate/+internal/stimulusPresentationToManipulation.m  sets it
#
# Three of three. The "free-standing attachment leaves it empty" case that
# opaque_body's own documentation described has ZERO emitters, and that
# docstring line is deleted here rather than left describing a shape nothing
# produces.
#
# THIS IS NOT THE CORPUS-ABSENCE ARGUMENT THIS PROJECT HAS BEEN BURNED BY. V_eta
# documents are not found in the wild, they are GENERATED, by exactly those
# three paths -- so "no emitter can leave it empty" is a claim about the
# generator, not about a sample, and it is complete for migrated data.
#
# AND THE DIRECTION IS WHY IT IS DONE NOW. #37 is armed, so required is
# enforced from the first run, at a cost measured at zero today. Loosening later
# is always free; tightening stops being free the moment something relies on the
# looseness. The plan makes this same argument one field over, about `count`'s
# placement: "Zero writers means no legacy to preserve. If it is not aligned
# now, the first writer cements the third pattern permanently."
data_body = doc("data_body", ["base"], abstract=True, maturity="draft",
                deps=[STATEMENT_REQ], fields=[
    field("format", "char",
          "Container / MIME format of the carried bytes (e.g. 'application/pdf', "
          "'image/tiff', 'tiff'). A descriptor only.",
          non_empty=False),
    # NEW. The unbuilt half of the 2.D "encoding becomes a field" decision that
    # `migrators_j/image.m` has been waiting on: v1 `image.compression` carries
    # 'lzw' beside format 'tiff' and had nowhere to land.
    field("compression", "char",
          "Compression applied within or around `format` (e.g. 'lzw', 'gzip'). "
          "Empty when the bytes are stored uncompressed.",
          non_empty=False),
    field("filename", "char", "Original filename of the payload, if any.",
          non_empty=False),
    # "WHICH BYTES" (plan open question 3) IS SETTLED HERE, because `compression`
    # arriving is exactly what made it ambiguous -- the old opaque_body
    # documentation said so and asked for this answer by name. THE BYTES AS
    # STORED, and the reason is the v1 source rather than taste:
    # `generic_file.checksum` is the MD5 `ndi.fun.file.MD5` computes over the
    # file ON DISK, i.e. after whatever compression was applied. Hashing the
    # decompressed form would change what a migrated hash MEANS relative to the
    # v1 value it carries, and would make the hash uncheckable without first
    # decompressing.
    field("content_hash", "char",
          "Optional hash of the payload bytes AS STORED in `body_data` -- after "
          "`compression`, not before. A natural dedup / integrity key, checkable "
          "without decoding. did_v1 source: `generic_file.checksum`, the "
          "32-character lowercase MD5 ndi.fun.file.MD5 computes over the stored "
          "file; the algorithm is not declared by this field and is not "
          "recoverable from it.",
          non_empty=False),
    field("description", "char", "Human description of the payload.",
          non_empty=False),
])
data_body["file"] = BODY_FILE
write("draft", "data_body", data_body)

# filter_id (team decision, 2026-07-30): the frequency filter these SAMPLES went
# through. It lives on the BODY, not on subject_interaction, because it
# characterises the bytes -- read level1.bin without knowing it is 300 Hz
# high-passed and the numbers mislead (T14: what a consumer must know to read a
# value is declared where the value is). It also sits beside sample_time / axes /
# datum, which are the same kind of fact.
#
# NOT on subject_interaction, where software_id and instrument_id live: those are
# AGENTS, universally applicable even when unrecorded. A frequency filter is
# INAPPLICABLE to most statements -- a mass_observation of a mouse cannot have one.
# Universally-optional and inapplicable-to-most are different, and only the first
# belongs on a shared parent.
#
# Per-body also stays correct for pyraview, whose fold mints one body per
# resolution level: levels 2..N have been through additional anti-alias filtering
# during decimation, which a single document-level filter could not express.
FILTER_ID = dep("filter_id", "frequency_filter",
                "Optional: the frequency filter these samples passed through. See "
                "V_eta_frequency_filter_model_plan.md.", non_empty=False)
# STATEMENT_REQ IS GONE FROM HERE -- it is inherited from data_body now, at the
# same required-ness this class already declared, so nothing about a sampled_body
# changed. `content_hash` likewise moved up. FILTER_ID stays: a frequency filter
# is INAPPLICABLE to an opaque body, and the note above says why that belongs on
# the child rather than the shared parent.
sampled = doc("sampled_body", ["data_body"], maturity="draft",
              deps=[FILTER_ID], fields=[
    # `datum` IS GONE. Its `dtype` became `subject_statement.datum_type`; `unit`,
    # `shape` and `kind` were dropped for the reasons recorded on that field.
    # `record` is retired as a datum kind -- its one real use (dtype `double`
    # over [nTrials,7], the grating parameters) is a LABELLED CATEGORICAL AXIS,
    # and a genuinely heterogeneous record was never representable here anyway,
    # there being one dtype field.
    # `sample_time` IS GONE FROM THE BODY (signed sec.2, step 5: "time becomes an
    # ordinary axis" and "both sample_time blocks retire"). Its five sub-fields
    # map onto the axis entry below with nothing left over:
    #     regular -> regular   t0 -> origin   dt -> spacing
    #     n       -> n         offsets -> values
    # and the rate-vs-period drift resolves on the way, because an axis states
    # `spacing` in its own quantity rather than as a `frequency` here and a
    # `duration` there.
    #
    # ALL FIVE WRITERS CONVERTED FIRST, which for a removal is transient-free (an
    # optional field a writer stops emitting validates against the old schema
    # too): DID-matlab pyraview / image_stack / jrclust_clusters / jNgridBody via
    # the shared jSampledBody, and NDI stimulusPresentationToManipulation. The
    # STATEMENT-side `subject_interaction.sample_time` is a DIFFERENT field, is
    # still declared, and is still written by nine call sites across both repos.
    # `summary` IS DROPPED, NOT DEFERRED IN PLACE (#68, signed sec.9). It
    # declared a "searchable value + time rollup" and was minted EMPTY on every
    # body jSampledBody ever produced -- `{value: {}, time: {}}` -- with no
    # writer filling either half and no reader consulting one. A block that is
    # always empty but looks structural is the vacuous composite #38 exists to
    # catch. The migrator half (DID-matlab 3792240) landed FIRST, which for a
    # removal is transient-free: an optional field a writer stops emitting
    # validates against the old schema too.
    # THE AXIS ENTRY. TEAM-SIGN-OFF [data_body] 2026-08-14, with AMENDMENT 1 of
    # the same day. It replaces THREE encodings of regular-vs-enumerated
    # (subject_interaction.sample_time.kind / sampled_body.sample_time.regular /
    # the old axes[].regularity) plus a fourth spelling of the same fact
    # (acquisition_epoch.axes.sample_rate, a frequency, against sample_time.dt,
    # a duration).
    #
    # TIME IS AN ORDINARY AXIS now: `t0 -> origin`, `dt -> spacing`, `n -> n`,
    # `offsets -> values`. `sample_rate` goes away because an axis stores its
    # spacing in its own quantity.
    #
    # THE OLD SHAPE COULD NOT STORE WHAT IT DECLARED: `regularity: irregular`
    # was declarable with NOWHERE to put the coordinates, and there was no
    # `origin`, so even a regular axis could not say where it starts.
    #
    # `unit` IS PRESENT AND IS A BOUND TERM -- this is AMENDMENT 1 reversing the
    # signed plan's own "THERE IS NO `unit` FIELD". The registry was to carry
    # the canonical unit, but `spatial frequency` has none it can express (no
    # `spatial_frequency` data_type; cycles-per-degree is inverse-angle, which
    # nothing declares; and the registry row shape for a unit DOES NOT EXIST --
    # 4 lists, no dimension key, no unit key). A missing row would have made the
    # number SILENTLY MEANINGLESS; carrying the unit makes the worst case an
    # UNVALIDATED number instead. Bound, not char: the plan's objection was to a
    # FREE-TEXT unit beside a bound `variable`, and an ontology_term is not an
    # escape hatch. The pattern is already in the schema twice -- voltage.value
    # is canonical-plus-source, conditions.count.value carries a bound unit.
    #
    # `name` and `kind` GO. `name`'s own examples ('contrast', 'orientation')
    # ARE variables, and a free-text name beside a bound `variable` is what makes
    # the binding pointless. `kind` was one of THREE unrelated fields called
    # `kind` (datum.kind, this, sample_time.kind).
    field("axes", "structure",
          "Index dimensions of this body, in array order: axes[k] IS array "
          "dimension k. Time is an ordinary axis. Empty for a bare scalar.",
          non_empty=False, scalar=False, blank=[],
          sub_fields=axis_subfields()),
    # `content_hash` USED TO BE DECLARED HERE and is now on data_body -- it is a
    # fact about the BYTES, which is what the hoist sorts by, and declaring it on
    # both children was the duplication the hoist removes.
    #
    # THE TWO ORDERS, named at the same altitude on purpose (signed sec.6):
    # bytes within a datum, data within the array. `endianness`/`chunk_order`
    # were rejected for reading as unrelated concepts. Neither is required by
    # the schema, because neither is universally applicable -- a single-byte
    # datum has no byte order and a 1-D body has no datum order -- and a
    # required field that is inapplicable to real bodies is the invented-empty
    # pattern. The REQUIREMENT the plan states ("REQUIRED when datum_type is
    # multi-byte", "REQUIRED when there is more than one axis") is conditional
    # on the body's own shape, which this schema layer cannot express; it is
    # stated in the documentation so a writer knows when it must fill them.
    field("byte_order", "char",
          "'little' | 'big' -- the order of bytes WITHIN one datum. REQUIRED in "
          "practice whenever `datum_type` is multi-byte; meaningless, and left "
          "empty, for single-byte data.",
          non_empty=False),
    field("datum_order", "char",
          "'C' | 'F' -- the order of DATA within the array: C is row-major "
          "(last axis fastest), F is column-major (first axis fastest, MATLAB's "
          "native layout). REQUIRED in practice whenever there is more than one "
          "axis; meaningless, and left empty, for a 1-D body.",
          non_empty=False),
])
sampled["file"] = BODY_FILE
write("draft", "sampled_body", sampled)

# EMPTIED BY THE HOIST, deliberately, and the plan says so in as many words:
# "nothing of its own -- its content is 'these bytes are not an array', which the
# class name states." All four fields it used to declare are on `data_body` now,
# and the `statement` edge with them. `data_body` has EXACTLY two members; that
# is not reopened here.
opaque = doc("opaque_body", ["data_body"], maturity="draft", deps=[], fields=[])
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
# image model decision 4 (V_eta_image_model_plan.md): descriptors ALWAYS explicit on the
# composite (dtype is NOT recoverable from an inline matrix). image is a STANDALONE
# data_type -- `array` is KILLED, so image does NOT subclass anything and carries its own
# N-D descriptors + picture semantics. Replaces the old image_type/format/x_/y_resolution.
# ONE payload slot, like every other data_type: the descriptors ride INSIDE the cell,
# beside the pixels -- exactly as `source_unit` rides beside `source_value` in a dimensioned
# cell. (image previously hoisted dtype/axes/color_model/channels alongside `value`, making
# it 1 of only 2 composites that broke the single-`value` convention. Placement only: R6's
# "descriptors ALWAYS explicit" still holds, they are just declared one level in.)
_img["fields"] = [
    field("value", "structure",
          "The raster cell: the pixels plus the descriptors needed to interpret them. "
          "Self-describing, so the cell can be read without consulting the producer.",
          non_empty=True, blank={}, sub_fields=[
              subfield("pixels", "matrix",
                       "The raster; populated iff storage_mode:inline, else empty (the "
                       "pixels live in a data_body). N-D, never scalar.", scalar=False,
                       blank=[]),
              subfield("dtype", "char",
                       "Pixel data type (uint16 | uint8 | single | …). NOT recoverable "
                       "from an inline matrix, so always explicit (R6 decision 4)."),
              # FOLDED INTO THE ONE AXIS ENTRY, 2026-08-14 -- signed addendum
              # section 5. The old shape here was {name, length, spacing, unit},
              # the WEAKEST of the three: no `regularity` at all, so it declared
              # a `spacing` with no way to say whether spacing was even
              # meaningful, and (like the other two) no `origin`, so it could not
              # say where an axis starts.
              #
              # THE MOUNT IS CORRECT AS IT STANDS, and section 5 warned that this
              # one is not a pure rename because of it: axes live with the thing
              # whose extent they describe (section 7), so a raster whose pixels
              # are INLINE in `value.pixels` carries its axes right here, beside
              # them. What is NOT yet done is the other arm -- when storage_mode
              # is `body` the axes belong on each sampled_body, and
              # `migrators_j/image_stack.m` still fills this cell while emitting
              # storage_mode:body. That move is deferred WITH the `sample_time`
              # retirement rather than split from it: image_stack's spatial
              # calibration lives here and its time axis lives in
              # `sampled_body.sample_time`, and the signed model turns BOTH into
              # ordinary axes on the body. Moving one without the other would
              # leave a body with space but no time.
              subfield("axes", "structure",
                       "Index dimensions of the raster, in array order (Y,X,C,Z,T) — the "
                       "full N-D calibration the old x/y_resolution lost. Populated when "
                       "the pixels are inline; when they live in a data_body, the axes "
                       "live with the body.",
                       scalar=False, blank=[], sub_fields=axis_subfields()),
              subfield("color_model", "ontology_term",
                       "grayscale | rgb | multichannel (T8-bound)."),
              subfield("channels", "string",
                       "Per-channel labels (e.g. ['GCaMP','tdTomato']).", scalar=False,
                       blank=[]),
          ]),
]
write("stable", "image", _img)

# `ontology_table_row_id` -- the metadata row that gives this image its data
# context. Added 2026-08-11 at the team's direction, after image_stack.m was found
# to DROP the did_v1 `document_id` edge on its fold arm for want of anywhere to put
# it: image_observation and its seven ancestors declare six edges between them
# (subject_id, time_reference_#, instrument_id, software_id, method_parameters_id,
# derived_from_#) and not one means "the metadata row this image belongs to".
# `derived_from_#` is the near miss and is wrong twice -- typed to
# `subject_statement` (the row migrates to an `ontology_table_row`) and it asserts
# COMPUTATION, which this is not.
#
# The name is NOT invented: stable/ontology_image.json already declares exactly
# this edge, with this target class, for the identical relationship.
#
# OPTIONAL, and that is load-bearing. There are EIGHT ndi.document('imageStack')
# sites on NDI origin/main and they form THREE populations, not two:
#   haley behaviour  (doImport.m 421/461/477/496)  subject_id AND document_id
#   haley E. coli    (doImport.m 789/811/827)      document_id only -> guard arm
#   babu             (import.m:474)                subject_id only, NO document_id
# The babu site reaches the fold arm with no edge to carry, so a REQUIRED edge
# here would quarantine it -- the invented-empty-edge pattern, with the
# RequiredDependencies gate now armed and the corpus at 0 over 627,526 documents.
#
# Declaring the slot does not by itself carry anything: migrators_j/image_stack.m
# still drops the edge, and `testImageStackFoldDropsDocumentIdForWantOfASlot` pins
# that. The carry is the follow-up, and it must be conditional on the edge being
# present in the source.
_img_obs = doc("image_observation", ["subject_observation", "image"], maturity="draft")
_img_obs["depends_on"] = list(_img_obs.get("depends_on") or []) + [
    dep("ontology_table_row_id", "ontology_table_row", non_empty=False,
        doc=("The metadata table row giving this image its data context (e.g. the "
             "behaviour plate row carrying its OD600 / CFU / lawn-volume "
             "covariates). NOT a subject, and NOT provenance: it is the row the "
             "did_v1 `document_id` edge named. Optional -- the babu writer emits "
             "an imageStack with a subject and no such row."))]
write("draft", "image_observation", _img_obs)
# image_manipulation: an image/video SHOWN to the subject as a visual stimulus (raster
# sibling of visual_grating_manipulation, which is a parametric stimulus). image model
# decision 2 (V_eta_image_model_plan.md). Referenced by a timed_sequence as one presented
# `data_type` doc (the stimulus model), or used standalone.
write("draft", "image_manipulation",
      doc("image_manipulation", ["subject_manipulation", "image"], maturity="draft"))


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
    # gain: a logarithmic ratio in dB. Added for the frequency_filter model -- passband
    # ripple is an allowed gain VARIATION and stopband attenuation is a gain REDUCTION,
    # both quoted in dB. Typed rather than dropped in a parameter bag so "every recording
    # high-passed with under 1 dB of ripple" stays a query (the tuning re-audit lesson:
    # flattening typed scalars into a {name,value} bag was a real query regression).
    ("gain", "dB (logarithmic ratio -- gain, ripple, attenuation)"),
]
for name, unit in NUMERIC_SEED:
    write("stable", name,
          doc(name, ["base"], abstract=True, fields=[field(
              "value", name,
              f"A {unit} value cell (canonical + lossless source). Series-as-cardinality: "
              "an array of the cell; per-sample timing is the statement's sample_time.", non_empty=True, scalar=False, blank=[], default=[CELL])]))
    write("stable", name + "_observation",
          doc(name + "_observation", ["subject_observation", name]))
    write("stable", name + "_assertion",
          doc(name + "_assertion", ["subject_assertion", name]))
# intensity is also imposable (e.g. a stimulus a.u. level)
write("stable", "intensity_manipulation",
      doc("intensity_manipulation", ["subject_manipulation", "intensity"]))


# ---------- 11c. frequency_filter ----------
# The signal conditioning applied to a recording, as a REFERENCED DOCUMENT.
# Decided with the team against the one real corpus document available
# (PRED 41269628e2d51bf1) -- see V_eta_frequency_filter_model_plan.md, which
# carries the sign-off and the full reasoning. Summary of the four calls:
#
#   NOT a data_type   -- a data_type is a QUANTITY. Nothing "has a filter value";
#                        a filter transforms something that does (T12).
#   NOT an entity     -- every entity here is a citable thing in the world and the
#                        tier exists to carry global_identifier. A filter has none
#                        and never will. But an entity is not required to be
#                        REFERENCED: time_reference is already a referenced,
#                        deduplicable document under base. Same shape.
#   BAND EDGES        -- one `cutoff` only works for high/low pass. Edges cover all
#                        four cases; `band` is still needed because band_stop is the
#                        inverse of the other three, not derivable from the numbers.
#   TYPED gain FIELDS -- not a `coefficients` bag. `coefficients` already means the
#                        b/a arrays in this domain, and the IIR family is CLOSED, so
#                        typed keeps "under 1 dB of ripple" queryable (the tuning
#                        re-audit lesson).
#
# NO sample_rate: this is the SPECIFICATION, not the realisation. Realised
# coefficients depend on the rate (MATLAB takes normalised frequency), but the rate
# is already on the recording -- storing it here would duplicate it and break dedup
# across rates.
write("stable", "frequency_filter", doc("frequency_filter", ["base"], fields=[
    field("algorithm", "ontology_term",
          "The filter design family (chebyshev_1 | chebyshev_2 | butterworth | "
          "elliptic | bessel | fir). Determines which of the optional gain fields "
          "apply.", non_empty=True,
          constraints={"binding": {"root": "did_filter_algorithm",
                                   "expansion": "value_set",
                                   "values": ["chebyshev_1", "chebyshev_2",
                                              "butterworth", "elliptic", "bessel",
                                              "fir"],
                                   "strength": "required", "source": "value_set"}}),
    field("band", "ontology_term",
          "Which frequencies survive: high_pass | low_pass | band_pass | band_stop. "
          "NOT derivable from the edges alone -- band_stop REJECTS the interval the "
          "others would keep.", non_empty=True,
          constraints={"binding": {"root": "did_filter_band",
                                   "expansion": "value_set",
                                   "values": ["high_pass", "low_pass", "band_pass",
                                              "band_stop"],
                                   "strength": "required", "source": "value_set"}}),
    field("passband", "structure",
          "The interval that is kept. An absent edge means open: a high_pass has a "
          "low edge and no high edge, a low_pass the reverse.", sub_fields=[
              subfield("low", "frequency", "Lower edge of the passband."),
              subfield("high", "frequency", "Upper edge of the passband."),
          ]),
    field("stopband", "structure",
          "The interval that is rejected. band_stop (notch) only.", sub_fields=[
              subfield("low", "frequency", "Lower edge of the stopband."),
              subfield("high", "frequency", "Upper edge of the stopband."),
          ]),
    field("order", "integer",
          "Filter order -- how steeply the response rolls off.", non_empty=False),
    field("passband_ripple", "gain",
          "Permitted gain variation within the passband. Chebyshev I and elliptic "
          "only; ABSENT (never NaN) for designs that have no passband ripple. The "
          "v1 source writes NaN for the inapplicable one -- the same hollow-value "
          "pattern the time model rejected.", non_empty=False),
    field("stopband_attenuation", "gain",
          "Guaranteed gain reduction within the stopband. Chebyshev II and elliptic "
          "only; ABSENT for designs that have no stopband specification. NOTE the v1 "
          "field is misspelled `stopbandAttentuation` in the NDI template AND in the "
          "data -- a migrator reading the correct spelling gets nothing, silently.",
          non_empty=False),
]))


# ---------- 12. formalize `binding` in the meta-schema (D9) ----------
# The constraints subschema is an open object; add a `binding` property so binding
# blocks are structurally validated (require keyed_by) without constraining the
# other constraint keywords (maxLength, enum, …).

meta = load(os.path.join(VETA, "stable", "did_schema_meta.json"))
type_enum = meta["$defs"]["field_definition"]["properties"]["type"]["enum"]
for _seed_name, _ in NUMERIC_SEED:          # J §7 comprehensive numeric set
    if _seed_name not in type_enum:
        type_enum.append(_seed_name)
# `date` -- a PRIMITIVE, joining the enum beside `timestamp` rather than as a
# composite. It declares no sub-fields and needs none: like `char`, `did_uid`
# and `timestamp` it is a scalar string, so it does not trip
# test_named_composite_cells_declare_their_layout (which requires a layout only
# of NON-primitive members). It exists because a calendar date and a wall-clock
# instant are different facts: `timestamp` is an ISO 8601 UTC INSTANT, `date` is
# a calendar date at whatever precision the source gave -- `YYYY`, `YYYY-MM` or
# `YYYY-MM-DD`. Typing a year-granularity publication date as `timestamp`
# invents a month, a day and a time.
if "date" not in type_enum:
    type_enum.append("date")

# ---- `base.datestamp` -> `base.creation_timestamp` -------------------------
# THE FIELD IS INHERITED FROM V_zeta AND NOTHING HERE TOUCHED IT, which is why
# the rename needs an explicit transform rather than an edit to a `field()`
# call: `base.json` is copied wholesale and `datestamp` rode through unchanged.
#
# WHY THE NAME. `datestamp` names the CONTAINER (a stamp), not the content (a
# creation time), which T13 rules out. The replacement follows the house style
# as MEASURED rather than as preferred: `<noun>_<kind>` across 472 field names
# (13 `_name`, 11 `_time`, 10 `_type`, 6 `_value`, 5 `_id`) and ZERO bare past
# participles -- so `created`, which reads better in isolation, would have been
# the only one of its kind in the schema.
#
# AND THE KIND WORD IS `_timestamp`, NOT `_time`. All 22 existing
# `_time`/`_times` fields are NUMERIC (13 double, 6 matrix, 3 structure) --
# offsets and durations in seconds, never wall-clock instants -- so a
# `timestamp`-typed `_time` would collide with an established meaning. That
# `_timestamp` echoes its own type is not an objection here: `_id`, `_name`,
# `_type`, `_value` and `_unit` all do, and they are the convention.
#
# THE MIGRATOR SIDE IS ONE FUNCTION, NOT 65 EDITS:
# did2.convert.v1_to_v2/renameOutboundBaseFields renames on the way OUT, after
# ensureClassBlocks and before validation -- the only point every body passes
# through, passthroughs included. Migrators keep reading and writing did_v1
# spelling internally and not one of them changed.
# ---- the epoch handle gains the extent, by COPYING relative_reference.value --
# TEAM GRANT 2026-08-13: "you can change any of the transitional schema... as
# long as they aren't in V_eta's final schema." `epoch_bounded_reference` is a
# pass-1 HANDLE -- it is consumed by ndi.migrate.internal.epochAnchorFold and is
# NOT in the persist set (V_eta_final_class_set.md's tier 5 is exactly
# `absolute_reference`, `relative_reference`), so a slot added here never reaches
# the schema we keep.
#
# WHY IT IS NEEDED. pyraview is epoch-scoped by declaration and carries the
# epoch's extent in its v1 `epochclocktimes` block (PRED: t0_t1 = [0, 28.12495],
# dev_local_time). The handle could carry the epoch IDENTITY and the CLOCK but
# had NO slot for an interval, so the extent had no transport between pass 1 and
# did2.convert.epochMint -- which is where the extent is minted onto the epoch's
# own `time_reference_#`.
#
# COPIED, NOT RE-DECLARED, and that is the point: the fold's job becomes a
# straight copy of `value` into the `relative_reference` it emits, with no
# translation step to get wrong, and the two shapes CANNOT DRIFT -- change
# relative_reference.value and this follows on the next build.
_rr_tier, _rr_path = path_of("relative_reference")
_rr_value = [f for f in load(_rr_path)["fields"] if f["name"] == "value"]
if len(_rr_value) != 1:
    raise SystemExit("build_v_eta: relative_reference must declare exactly one "
                     "`value` field; found %d" % len(_rr_value))
_ebr_tier, _ebr_path = path_of("epoch_bounded_reference")
_ebr = load(_ebr_path)
if not any(f["name"] == "value" for f in _ebr["fields"]):
    _v = json.loads(json.dumps(_rr_value[0]))      # deep copy

    def _strip_governance(node):
        # THE COPY CARRIES SHAPE, NOT GOVERNANCE. relative_reference.value's
        # `relation` and `clock` are BOUND (OWL-Time, and the four clock terms),
        # and those bindings belong to the class we KEEP. Copying them onto a
        # transitional handle would grow the bound-field count -- which
        # check_binding_governance ratchets on, correctly -- and would put
        # governance on a class that is deleted after the fold. The fold target
        # enforces the vocabulary; the handle only has to carry the numbers.
        node["constraints"] = {}
        # AND NORMALISE THE COMPOSITE BLANK. A named composite (`duration`,
        # `ontology_term`) whose blank_value is a scalar is a document that
        # cannot validate against its own declared type -- cache.m:1764 --
        # which tests/test_veta_blank_values_typecheck.py ratchets on. The
        # copy inherits whatever the source declared; a composite blank is {}.
        # KEYED ON TYPE, NOT ON SHAPE. This patch runs BEFORE the step that
        # expands composite sub-fields, so at copy time a `duration` field has
        # no `fields` key yet and a shape test silently does nothing -- which
        # is exactly what the first version of this did.
        if node.get("type") not in _CHARLIKE_BLANK_TYPES + (
                "integer", "double", "boolean", "matrix"):
            node["blank_value"] = {}
            node["default_value"] = {}
        for _sf in node.get("fields") or []:
            _strip_governance(_sf)

    _strip_governance(_v)
    _v["mustBeNonEmpty"] = False                   # a handle may carry no extent
    _v["documentation"] = (
        "The epoch's extent and clock, shaped EXACTLY as relative_reference."
        "value so the fold is a copy rather than a translation. OPTIONAL here "
        "and required there: a handle may name an epoch without knowing its "
        "bounds, which is the `no times => no reference` rule applied to the "
        "transitional class. Populated from the did_v1 `epochclocktimes` block.")
    _ebr["fields"].append(_v)
    write(_ebr_tier, "epoch_bounded_reference", _ebr)

_base_tier, _base_path = path_of("base")
_base = load(_base_path)
_renamed = 0
for _f in _base.get("fields", []):
    if _f["name"] == "datestamp":
        _f["name"] = "creation_timestamp"
        _f["documentation"] = (
            "UTC timestamp of document creation, ISO 8601. Renamed from "
            "`datestamp` 2026-08-13: `datestamp` named the container rather "
            "than the content (T13), and `_timestamp` is the kind word "
            "because every existing `_time` field in V_eta is a numeric "
            "offset or duration, not an instant.")
        _renamed += 1
if _renamed != 1:
    raise SystemExit(
        "build_v_eta: expected exactly ONE `datestamp` field on `base`, "
        "found %d -- the rename is no longer describing the tree" % _renamed)
write(_base_tier, "base", _base)
# `validity` USED TO BE APPENDED HERE, and its replacement deliberately is not.
# The enum is `field_definition.type` -- the types a FIELD may declare -- and it
# needed an entry only because `validity.value` was typed `validity` (a nested
# cell wrapping one boolean). `logical.value` is typed `boolean`, which is
# already a primitive in this enum and in DID-matlab's own type switch
# (cache.m:1793), so `logical` names no field type and belongs to no enum. An
# entry for it would also FAIL test_named_composite_cells_declare_their_layout,
# which requires every non-primitive enum member to declare sub-fields.
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
                       "(`ontology` + `root_node`), plus `node_form` for the "
                       "value's lexical shape. Read by DID-matlab "
                       "did2.schema.cache/validateConstraints behind the "
                       "BindingConformance switch, which is DISARMED by "
                       "default; the full ontology-aware resolution T8 "
                       "describes (D9) does not exist yet.",
        "properties": {
            "keyed_by": {"type": "string"},
            "expansion": {"type": "string"},
            "node_kind": {"type": "string"},
            # #32 increment 2. The ONLY part of a binding that is checkable
            # with no ontology loaded: the LEXICAL FORM of the `node` slot.
            # `curie` says the bound value's node must be a syntactically
            # well-formed CURIE (`prefix:local`). It says NOTHING about whether
            # the prefix expands or the term exists -- membership needs NDIC.txt
            # (moved to VH-Lab/ndi-ontology-matlab, commit 2c19bf24c) and is out
            # of scope. Declared here so the three pivot fields that use it do
            # not show up as undeclared keys in
            # tools/check_binding_governance.py B1.
            "node_form": {"type": "string", "enum": ["curie"]},
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
# ---- #63: cardinality on a numbered edge family ----------------------------
# `mustBeNonEmpty: true` on a `name_#` family is BOTH unenforceable AND
# meaningless. `silentLoss.requiredDependencies` excludes numbered edges, and its
# reasoning is right: you cannot check a blank `time_reference_3`, because a
# MISSING instance of a family is not the same thing as a blank one. So three
# families have been declared REQUIRED and verified by nothing.
#
# What IS checkable is HOW MANY instances exist, and the meta-schema had no way
# to say it. Two optional integers fix that. They are declared here rather than
# reusing `mustBeNonEmpty` because they answer a different question, and leaving
# the old flag to mean "required" on a family it cannot describe is what produced
# the false assurance in the first place.
_dep_props = meta["$defs"]["dependency_object"]["properties"]
_dep_props["min_count"] = {
    "type": "integer",
    "minimum": 0,
    "description": "For a numbered family (`name_#`): the minimum number of "
                   "instances a valid document must carry. `mustBeNonEmpty` "
                   "cannot express this -- a missing instance is not a blank "
                   "one -- so a family that must be present says min_count: 1. "
                   "Omit on a non-numbered dependency.",
}
_dep_props["max_count"] = {
    "type": "integer",
    "minimum": 1,
    "description": "For a numbered family (`name_#`): the maximum number of "
                   "instances a valid document may carry. Omit for unbounded.",
}
# ---- #52: what makes two members of one family DIFFERENT -------------------
# #63 said HOW MANY members a family may carry. It could not say what makes two
# of them distinct, so `time_reference_1` and `time_reference_2` on one document
# were UNDEFINED IN MEANING -- a bare index cannot tell a start-anchor from a
# same-instant-other-clock from a recurrence.
#
# `V_eta_time_reference_model_plan.md` CHANGE 5 (signed section, :642) closed
# that by ELIMINATION rather than by naming the edges: split-anchored intervals
# have NO INSTANCE (every markvalidinterval call site passes the same reference
# for both ends), recurrence dissolves into N statements (T4), and epoch extent
# vs statement time are never on the same document. The ONE case that is live is
# SAME EXTENT, N CLOCKS -- and its discriminator already exists inside the
# REFERENCED document, as `value.clock`. So the rule is a uniqueness constraint,
# not a set of role names, and #52's title ("role-name the edges") is stale.
#
# THE PATH IS RESOLVED ON THE REFERENCED DOCUMENT, NOT ON THE REFERRING ONE.
# That is the whole difficulty and the reason this key is named `referent_`:
# nothing on the document carrying `time_reference_2` says what makes it
# different from `time_reference_1`. A per-document validator therefore CANNOT
# check this; it is a batch property, measured by did2.validate.silentLoss where
# the other documents are in hand.
_dep_props["referent_unique_by"] = {
    "type": "string",
    "description": "For a numbered family (`name_#`): a dotted field path "
                   "evaluated ON THE REFERENCED DOCUMENT. No two members of "
                   "the family may refer to documents that agree on that path "
                   "-- the path is what distinguishes one member from another, "
                   "and without it a bare `_1`/`_2` index carries no meaning. "
                   "Resolving it requires the referenced documents, so this is "
                   "a BATCH property: it is measured report-only by "
                   "did2.validate.silentLoss and cannot be checked by a "
                   "per-document validator. Omit on a non-numbered dependency, "
                   "and on a family whose members are deliberately "
                   "indistinguishable (`derived_from_#`: N inputs, no ordering "
                   "and no uniqueness rule has been decided).",
}
# ---- NDI's OWN required-ness verdict, recorded alongside ours --------------
# Stamped by stamp_ndi_required() at the end of this build from
# V_eta_ndi_ground_truth.json. It is a SEPARATE key from `mustBeNonEmpty`
# because it is a DIFFERENT FACT: `mustBeNonEmpty` is what V_eta enforces,
# `ndi_mustBeNonEmpty` is what NDI declared about the did_v1 class this one
# came from. Merging them would make an armed gate key on a foreign schema's
# opinion.
#
# THE KEY IS OPTIONAL AND ITS ABSENCE MEANS "NDI STATED NOTHING", never
# "optional". Absence covers three real conditions the stamp counts separately:
# the class has no did_v1 source at all, the source's schema document is in the
# JSON Schema form (which has no `mustbenotempty` anywhere), or V_eta renamed
# or dropped the edge so no name matched. A consumer that reads absence as
# `false` manufactures agreement out of silence.
_dep_props["ndi_mustBeNonEmpty"] = {
    "type": "boolean",
    "description": "NDI's OWN `mustbenotempty` verdict for the corresponding "
                   "did_v1 edge, copied verbatim from the class's NDI schema "
                   "document (schemas/V_eta_ndi_ground_truth.json). REPORT "
                   "ONLY: nothing validates, quarantines or gates on it -- "
                   "`mustBeNonEmpty` alone does that, and this key never "
                   "changes it. It exists so did2.validate.silentLoss can "
                   "census the edges NDI declares REQUIRED that V_eta declares "
                   "OPTIONAL, which are otherwise outside every counter: the "
                   "census reads `mustBeNonEmpty`, so an edge V_eta relaxed is "
                   "not merely counted as zero, it is not looked at. ABSENT "
                   "means NDI stated nothing (no did_v1 source, a JSON "
                   "Schema-form schema document, or no matching edge name) and "
                   "must not be read as `false`.",
}

with open(os.path.join(VETA, "stable", "did_schema_meta.json"), "w") as f:
    json.dump(meta, f, indent=4)
    f.write("\n")

# The seven numbered families, with the counts that are actually true of them.
# Each `mustBeNonEmpty` on a family is CLEARED at the same time: it never meant
# anything there, and leaving it would keep two flags disagreeing about one fact.
_EDGE_COUNTS = {
    # the statement spine: an interaction without a time reference is not a
    # statement about when anything happened
    ("subject_interaction", "time_reference_#"): (1, None),
    # a purpose with no interaction is a purpose for nothing
    ("interaction_purpose", "interaction_id_#"): (1, None),
    # NDI's OWN schema says "mustbenotempty": 0 for this one -- V_eta tightened
    # it wrongly, and a syncgraph with no rules yet is legitimate
    ("syncgraph", "syncrule_id_#"): (0, None),
    # provenance: real when present, absent for a directly-measured value
    ("subject_calculation", "derived_from_#"): (0, None),
    ("subject_observation", "derived_from_#"): (0, None),
    ("control_designation", "derived_from_#"): (0, None),
    # a relation may state times or not
    ("directed_relation", "time_reference_#"): (0, None),
    # a daq system may have several metadata readers or none: the writer LOOPS
    # (+ndi/+daq/system.m:495-497, add_dependency_value_n) and NDI's own schema
    # says "mustbenotempty": 0
    ("daqsystem", "daqmetadatareader_id_#"): (0, None),
    # ...and the V_eta class it becomes, same rule, same evidence. The plan left
    # this one as prose -- "carries the same unexpressed cardinality as
    # acquisition_channels_#, prose until #63 lands" -- and #63 has landed, so
    # the number gets declared rather than described. Re-derived from the code
    # rather than copied from the row above: the writer LOOPS over a cell array
    # (system.m:496, add_dependency_value_n) so it is genuinely a family, and the
    # reader passes ErrorIfNotFound,0 (system.m:48) so none is legal. Unbounded:
    # nothing in NDI caps it. Note the template declares the edge SINGULAR while
    # the writer uses the _n family form -- writer wins, as always here.
    ("acquisition_system", "acquisition_metadata_reader_#"): (0, None),
    # #57 gate 3, NOW MET. The sign-off recorded "EXACTLY 2 is prose until #63
    # lands" -- #63 has landed, so the cardinality the rule actually has is
    # declared and checkable instead of being a sentence in a plan.
    ("clock_alignment_configuration", "acquisition_channels_#"): (2, 2),
    # a policy with no rules yet is legitimate -- NDI's own syncgraph schema says
    # "mustbenotempty": 0 for syncrule_id
    ("clock_alignment_policy", "clock_alignment_configuration_#"): (0, None),
    # #29 ensemble: the per-epoch neuron roster. NDI's own schema says
    # "mustbenotempty": 0 for `neuron_id` (schema_documents/ensemble/
    # ensemble_schema.json), and the writer LOOPS with add_dependency_value_n
    # (+ndi/+element/ensemble.m:274-276) so it is genuinely a family. Unbounded:
    # nothing in NDI caps the number of neurons in an ensemble. min 0 rather than
    # 1 because that is what NDI declares -- NOT because an empty ensemble makes
    # sense; tightening it to 1 would be a NEW required edge on a passthrough
    # class, which is the invented-empty-edge pattern this project already paid
    # for six times.
    ("ensemble", "neuron_id_#"): (0, None),
}
for (_cls, _edge), (_lo, _hi) in _EDGE_COUNTS.items():
    _t, _p = path_of(_cls)
    if not _p:
        continue
    _d = load(_p)
    _changed = False
    for _x in _d.get("depends_on", []):
        if _x["name"] != _edge:
            continue
        _x["min_count"] = _lo
        if _hi is not None:
            _x["max_count"] = _hi
        # a family cannot be "non-empty"; the count says what is required
        _x["mustBeNonEmpty"] = False
        _changed = True
    if _changed:
        write(_t, _cls, _d)

# ---- #52: the uniqueness rule, declared on every time_reference family ------
# ONE rule, from the signed CHANGE 5:
#
#     Within a `time_reference_#` family, every member describes the same
#     instant or extent, and `value.clock` must be UNIQUE across the family.
#
# THE THREE FAMILIES ARE NAMED, NOT DERIVED. Deriving them from "every family
# whose target is a time_reference" would make a family silently drop out of the
# rule the day someone renames a target class -- the shape of every absence bug
# in this repository. If a fourth one appears, it is added here deliberately.
#
# DELIBERATELY NOT DECLARED on `derived_from_#`, `interaction_id_#`,
# `syncrule_id_#`, `acquisition_channels_#`, `daqmetadatareader_id_#`,
# `acquisition_metadata_reader_#` or `clock_alignment_configuration_#`: for each
# of those the members are genuinely several DIFFERENT things, and no uniqueness
# rule has been decided. Scope is #52's row and nothing wider.
_EDGE_REFERENT_UNIQUE = {
    ("subject_interaction", "time_reference_#"): "value.clock",
    ("directed_relation",   "time_reference_#"): "value.clock",
    ("epoch",               "time_reference_#"): "value.clock",
}
_UNIQ_DOC = (
    " #52 (V_eta_time_reference_model_plan.md CHANGE 5): within this family "
    "every member describes THE SAME instant or extent, and `value.clock` on "
    "the REFERENCED document must be unique across the family -- that clock is "
    "what makes two members different, and the `_1`/`_2` index means nothing on "
    "its own. Split-anchored intervals are NOT what a second member is for: "
    "they have no instance (every markvalidinterval call site passes one "
    "reference for both ends), so there are no `start_anchor`/`end_anchor` "
    "edges. Measured report-only, in batch, by did2.validate.silentLoss "
    "(`family_uniqueness_violation`); a per-document validator cannot see the "
    "referenced document and must not pretend to check it."
)
for (_cls, _edge), _path in _EDGE_REFERENT_UNIQUE.items():
    _t, _p = path_of(_cls)
    if not _p:
        raise SystemExit(
            f"#52: class {_cls} has no built schema -- the uniqueness rule would be "
            "declared on nothing.")
    _d = load(_p)
    _changed = False
    for _x in _d.get("depends_on", []):
        if _x["name"] != _edge:
            continue
        _x["referent_unique_by"] = _path
        if _UNIQ_DOC.strip() not in _x.get("documentation", ""):
            _x["documentation"] = _x.get("documentation", "").rstrip() + _UNIQ_DOC
        _changed = True
    if not _changed:
        raise SystemExit(
            f"#52: {_cls} declares no `{_edge}` family -- the uniqueness rule has no "
            "home. Fix the map, do not drop the rule.")
    write(_t, _cls, _d)


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
    #
    # timed + ordered, BOTH SET 2026-08-10 (team delegated the call after the
    # semantics were established). They were false, and the signed ensemble
    # model requires both -- two committed artifacts in direct contradiction.
    #
    # The contradiction resolves once you read what these flags MEAN, which is
    # documented at _rel above and is CAPABILITY, not constraint:
    #   ordered -- "the directed_relation `sequence` field is semantically
    #              meaningful ... every directed edge *has* an optional
    #              sequence; ordered marks the ones where it carries meaning"
    #   timed   -- "the edge denotes an event that may carry a `method` / time
    #              anchor"
    # Neither forces anything on any edge. Compare the rest of this table:
    # `has_author` is ordered because author order means something, and the
    # provenance rows are timed under a comment reading "the creation event MAY
    # carry a time_reference". Setting both here therefore ADDS no requirement;
    # it stops the registry denying a meaning the model depends on.
    #
    # Both are true of the ensemble, which is the only thing that mints these:
    # a member_of edge carries the neuron's COLUMN ORDER in the combined spike
    # matrix (so `sequence` is meaningful), and the recorded neuron set changes
    # epoch to epoch, so the roster is EPOCH-SCOPED (so the edge denotes a
    # timed event). Note the epoch-scoping cannot be expressed yet --
    # directed_relation has no epoch_id slot -- so `timed` here is currently
    # the honest declaration of a fact the schema cannot yet carry.
    #
    # CAVEAT, stated because the flags are per RELATION TERM and not per use:
    # this asserts `sequence` MAY be meaningful on every member_of edge, not
    # just the ensemble's. Under the capability reading that is correct and
    # costs nothing. It would be wrong under a constraint reading -- and
    # nothing enforces `binding` today, so if that reading is ever adopted,
    # this row is one of the first to re-examine.
    _rel("member_of", "RO:0002350", "the member", "the group",
         ["subject"], ["subject"], timed=True, ordered=True),
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
        # UNRESOLVED, and deliberately so. This used to read "pinned by the
        # import-provenance document (single source of truth)" -- but
        # openminds_import was removed 2026-07-30 because nothing ever emitted it,
        # so that sentence pointed at a class that no longer exists AND never
        # carried a value. Leaving the old note would have been a promise resolved
        # by nothing: exactly the stale-prose failure this project keeps hitting.
        #
        # It stays null until an openMINDS import path exists. Whatever records the
        # release then -- a re-added provenance class, a `software` reference, or a
        # literal pin here -- is decided WITH that import path, not before it.
        "version": None,
        "iri_base": "https://openminds.ebrains.eu/instances/",
        "notes": "openMINDS controlled-term instance libraries; each term_set is a "
                 "flat instance library (IRI + label), not an ontology subtree. "
                 "`version` is UNRESOLVED: no import path stamps a release yet.",
    },
}

# NO `strength` KEY HERE, AND ITS ABSENCE IS THE POINT (#32).
#
# These three rows used to state `strength` alongside the field constraint on
# dataset.accessibility / .ethics_assessment / .experimental_approach. Both
# copies said the same thing and NOTHING compared them: they agreed by
# coincidence. The FIELD IS AUTHORITATIVE, so the registry's copy is now a
# DERIVED column, written by `tools/regen_binding_strengths.py` immediately
# after this build in `tools/gates.py`. Restating it here would restore exactly
# the second source of truth that was removed -- the generator would overwrite
# it, so the literal would be inert, and an editor would reasonably believe
# they had changed something.
#
# To change how hard one of these is enforced, edit the field's
# `constraints.binding.strength` in the `dataset` class above and re-run
# `python3 tools/gates.py`.
ENTITY_FIELD_BINDINGS = [
    {"class": "dataset", "field": "accessibility",
     "vocabulary": "openMINDS", "term_set": "ProductAccessibility",
     "closed": True},
    {"class": "dataset", "field": "ethics_assessment",
     "vocabulary": "openMINDS", "term_set": "EthicsAssessment",
     "closed": True},
    {"class": "dataset", "field": "experimental_approach",
     "vocabulary": "openMINDS", "term_set": "ExperimentalApproach",
     "closed": False},
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

# E402: deliberately here, beside the conversion block that uses it, and
# aliased so it cannot collide with the module-level `re`. The sibling
# late import at the foot of this file carries the same directive.
import re as _re  # noqa: E402

CONV = os.path.join(VETA, "conversions", "from_did_v1")
_dims_re = "|".join(DIMS)

for p in sorted(glob.glob(os.path.join(CONV, "*.md"))):
    b = os.path.basename(p)
    if b in ("_index.md",):
        continue
    s = Path(p).read_text()
    s = _re.sub(rf"scalar_({_dims_re})_observation", r"\1_observation", s)
    s = _re.sub(rf"`scalar_({_dims_re})`", r"`\1`", s)
    s = _re.sub(rf"\bscalar_({_dims_re})\b", r"\1", s)
    s = s.replace("scalar_observation", "subject_observation")
    s = s.replace("scalar_manipulation", "subject_manipulation")
    s = s.replace("categorical_observation", "term_observation")
    s = s.replace("V_zeta", "V_eta").replace("Brainstorm I", "Brainstorm J")
    s = s.replace("Brainstorm-I", "Brainstorm-J")
    Path(p).write_text(s)

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
    s = Path(p).read_text()
    if "V_eta retarget" not in s.split("\n\n")[0]:
        Path(p).write_text(banner + "\n\n" + s)

# fan-out note in _universal_renames.md
ur = os.path.join(CONV, "_universal_renames.md")
s = Path(ur).read_text()
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
    Path(ur).write_text(s)

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
    # `acquisition_system_id` is NOT in this map and that is deliberate, not an
    # omission: it is DECLARED with its target at its own mint site (the
    # `acquisition_channels` write above), the way every J-authored dep() call
    # names its class. This map is the RETROFIT sweep for edges that arrived
    # untyped in the copied V_zeta tree. Typing it in both places would store one
    # fact twice, and the two copies would agree only by coincidence -- the
    # defect binding-registry `strength` was rebuilt to remove.
    # `parent_directory_id` was typed here until 2026-08-11. It existed ONLY on
    # `directory.json`, which the team deleted (see _DELETE_NO_V1_PROVENANCE),
    # so the entry now types an edge no schema declares. `parent_doc_id` stays:
    # the generic parent document is any doc (root `base`).
    "parent_doc_id": "base",
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

# ---- #60: epochfiles_ingested -> `ingestion_manifest`, with the REAL edge ----
# SIGNED 2026-08-08. Two separate defects in one class:
#
#   1. THE NAME encodes a MODE (`_ingested`), the same T13 error `_ndr` and
#      `_mfdaq` were de-encoded for. The document is a manifest of what was
#      ingested for one epoch; that is what it should be called. It EARNS its
#      existence (T12): nothing else records which files were physically copied
#      into the archive, so deleting it makes "what did this epoch physically
#      consist of" unanswerable.
#   2. THE EDGE was invented. V_eta declared `epochid -> acquisition_epoch`
#      REQUIRED and DROPPED the one NDI writes -- `filenavigator_id` --
#      leaving 6,921 documents with a required edge that is empty in 100% of
#      them. Restored here, alongside a real `epoch_id`.
#
# `epochprobemap` is REMOVED: it decomposes into edges (option B in the plan).
# The v1 `epoch_id` CHAR field goes with it -- the edge replaces the string, which
# is the whole point of minting `epoch`.
_efi_tier, _efi_path = path_of("epochfiles_ingested")
if _efi_path:
    _efi = load(_efi_path)
    _efi["document_class"]["class_name"] = "ingestion_manifest"
    _efi["document_class"]["class_version"] = "2.0.0"
    _efi["depends_on"] = [
        dep("filenavigator_id", "filenavigator",
            "The file navigator that produced this manifest. REQUIRED, and "
            "RESTORED: this is the edge NDI actually writes, which V_eta had "
            "dropped in favour of an invented `epochid`.", non_empty=True),
        dep("epoch_id", "epoch",
            "The epoch these files were ingested for. Replaces the invented "
            "`epochid` edge, which was empty on all 6,921 documents.",
            non_empty=True),
    ]
    _efi["fields"] = [f for f in _efi.get("fields", [])
                      if f["name"] not in ("epoch_id", "epochprobemap")]
    write(_efi_tier, "ingestion_manifest", _efi)

    # THE SOURCE TOMBSTONE STAYS UNTIL A MIGRATOR CONSUMES IT.
    #
    # This block used to `os.remove(_efi_path)` and register the RENAME, deleting
    # `epochfiles_ingested` the moment `ingestion_manifest` was minted. Nothing
    # migrates those documents yet -- that is #60's migrator half -- so every one
    # of them arrived at validation under a class that no longer had a schema.
    # Corpus B, run #2: 2,484 quarantines, "No schema file for class
    # epochfiles_ingested". The 0-quarantine gate, broken by a rename.
    #
    # This is exactly what _DELETE_PHASE8 exists to prevent -- a source class may
    # be removed ONLY once its documents provably cannot survive migration -- and
    # the rename bypassed it by deleting the file directly. Restated here from the
    # NDI template so the documents pass through validating, and removed for real
    # when the fold lands and the corpus proves it.
    #
    # NDI origin/main, epochfiles_ingested.json: depends_on filenavigator_id;
    # block {epoch_id, files[], epochprobemap}.
    _tombstone(
        "epochfiles_ingested", ["base"],
        [dep("filenavigator_id", "filenavigator",
             "The file navigator that produced this manifest -- the edge NDI"
             " writes.", non_empty=False)],
        [field("epoch_id", "char",
               "The epoch id STRING as did_v1 records it. Becomes the"
               " `epoch_id` EDGE on ingestion_manifest once `epoch` documents"
               " are minted (#60's migrator half)."),
         field("files", "string", "The files ingested for this epoch.",
               scalar=False),
         field("epochprobemap", "char",
               "The probe map for this epoch. Decomposes into edges under the"
               " signed model; carried verbatim until that is built, because"
               " dropping it now would be loss with no destination.")])

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
                     # TYPE CORRECTED 2026-08-10: it was `structure`; it is a
                     # CHAR. NDI serialises it before storing --
                     # `syncgraph.m:313-314` calls `.epochprobemap.serialize()`,
                     # and `epochprobemap_daqsystem.m:136-143` documents that
                     # method as "Create a CHARACTER ARRAY representation". The
                     # NDI template agrees (`"epochprobemap": ""`, lines 30 and
                     # 39), so there is no writer-beats-template judgement here;
                     # the DID side was simply wrong.
                     #
                     # It did not quarantine anything, because cache.m's
                     # validateField type-checks only the IMMEDIATE fields of a
                     # property block and this sits two levels down -- which is
                     # exactly why it survived. It is corrected before that
                     # non-recursion is ever tightened.
                     subfield("epochprobemap", "string",
                              "The probe map at this epoch, SERIALISED. NDI stores "
                              "the character-array form produced by "
                              "ndi.epoch.epochprobemap_daqsystem.serialize() "
                              "(syncgraph.m:313-314), carrying name / reference / "
                              "type / devicestring / subjectstring for every probe "
                              "on the epoch. Typed `string` rather than `char` "
                              "because an absent value decodes as an empty double, "
                              "which `char` rejects."),
                     subfield("objectclass", "char",
                              "The NDI object class of this epoch node."),
                     # #58: both restored here rather than in the interim-repair
                     # block above, because this builder REBUILDS the node field
                     # list and silently discarded anything added earlier.
                     subfield("objectname", "char",
                              "The name of the object (daq system / element) this "
                              "epoch node belongs to. READ BY A LIVE NDI QUERY by "
                              "exact_string (+ndi/+time/syncgraph.m:406-407) -- "
                              "dropping it broke saved-rule lookup."),
                     subfield("t0_t1", "matrix",
                              "The node's [t0 t1] bounds on its own clock. Dropped "
                              "by the same reshape that dropped objectname."),
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
        json.dump(d, f, indent=4)
        f.write("\n")
for tier in ("stable", "draft"):
    p = os.path.join(VETA, tier, "data_body.json")
    if os.path.exists(p):
        d = load(p)
        d["document_class"]["superclasses"] = [{"class_name": "data"}]
        with open(p, "w") as f:
            json.dump(d, f, indent=4)
            f.write("\n")

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

# ---------- 15. expand the named-composite types into DECLARED sub_fields -------------
# The named types (`voltage`, `duration`, `ontology_term`, ...) were an ENUM STRING and
# nothing more: `field("value", "voltage", ...)` declared no sub-fields, the blank omitted
# the canonical key, and the real layout lived only in the meta-schema's PROSE plus string
# literals in migrator code (`struct('celsius', ..., 'source_unit', ...)`). Consequences:
# the validator could only check `isstruct` inside a cell, the query-path generator could
# emit NOTHING for any measured value (26 of 35 composites emitted no path at all), and the
# convention was unenforceable. Declare the layout ONCE, inline, so every consumer --
# validator, query paths, viewer, docs -- reads the schema instead of hardcoding it.
#
# Canonical names for the 9 single-canonical types + concentration are ATTESTED in migrator
# code (canonicalComposite('celsius'|'hertz'|'seconds'|'liters'|'kilograms'|'meters'|'volts'|
# 'amperes'|'mmhg'), 'molar'), so those are RECORDED, not invented. The J §7 pre-seeded
# numerics have no attested canonical (nothing populates them yet), so their canonical key is
# named here from the documented SI unit, following the same spelled-out-plural convention.
_DIM_CANON = {
    # --- attested in migrator code (do NOT rename without a coupled migrator change) ---
    "duration": ["seconds"], "volume": ["liters"], "mass": ["kilograms"],
    "length": ["meters"], "voltage": ["volts"], "current": ["amperes"],
    "frequency": ["hertz"], "temperature": ["celsius"], "pressure": ["mmhg"],
    # multi-canonical BY DESIGN: concentration units do not collapse to one canonical
    # (mass/volume <-> molar needs molecular weight). All OPTIONAL; the migrator fills
    # whichever the source unit is computable into.
    "concentration": ["molar", "grams_per_liter", "mass_fraction", "volume_fraction",
                      "particles_per_liter"],
    # --- J §7 pre-seeded set: canonical named from the documented SI unit ---
    "velocity": ["meters_per_second"], "acceleration": ["meters_per_second_squared"],
    "area": ["square_meters"], "angle": ["radians"],
    "angular_velocity": ["radians_per_second"], "force": ["newtons"],
    "energy": ["joules"], "power": ["watts"], "charge": ["coulombs"],
    "resistance": ["ohms"], "conductance": ["siemens"], "capacitance": ["farads"],
    "amount": ["moles"],
    # dimensionless: nothing to canonicalise, but the cell keeps the family shape so the
    # set stays uniform (source_unit carries the a.u. label / pH scale note).
    "intensity": ["arbitrary_units"], "ph": ["ph"],
    # gain is a LOGARITHMIC RATIO, so decibels IS its canonical -- unlike the other
    # dimensionless entries there is a real, standard scale to normalise onto. Named for
    # the QUANTITY (gain), not the unit (decibel), per the family rule that gives
    # `voltage` not `volt` and `frequency` not `hertz`.
    "gain": ["decibels"],
}
# count / score are the documented EXCEPTIONS to the canonical+source triple: a count has no
# dimensional scaling (its unit is semantic, not convertible) and a score is scale-relative.
# ontology_term is the third named composite -- {node, name} -- declared so the IDENTITY
# field of every statement (`variable.node`, T2) becomes a real typed, queryable path.
_DIM_SPECIAL = {
    "count": [
        subfield("value", "integer", "The discrete count."),
        subfield("unit", "ontology_term",
                 "What is counted (cells / individuals / spikes / events) -- semantic, "
                 "NOT dimensional: counts do not normalise across units."),
        subfield("approximate", "boolean", "True when the count is approximate."),
    ],
    "score": [
        subfield("value", "double", "The score (double, so half-integer steps are legal)."),
        subfield("scale", "ontology_term",
                 "The scoring rubric (e.g. Murine Body Condition Score)."),
        subfield("scale_min", "double", "Lower bound of the scale."),
        subfield("scale_max", "double", "Upper bound of the scale."),
        subfield("approximate", "boolean", "True when the score is approximate."),
    ],
    "ontology_term": [
        subfield("node", "char", "The CURIE (prefix resolved via CURIE_lookups_meta.json)."),
        subfield("name", "char", "The human-readable label."),
    ],
    # `validity` HAD AN ENTRY HERE and `logical` deliberately has none. The entry
    # declared a one-sub-field cell `{value: boolean}`, i.e. `validity.value.value`
    # -- a wrapper around nothing. The reason given for it was that a cell buys a
    # query path; a bare `boolean` field already has one (`logical.value`), and the
    # composites that DO nest are the ones with provenance to carry (canonical +
    # source_unit + source_value, or count's semantic unit). A truth value has none
    # of that, so it is declared as a bare typed field, following `term.value`
    # (typed `ontology_term` directly).
}

def _named_type_subfields(tname):
    """Declared sub-fields for a named composite type, or None if not a named type."""
    if tname in _DIM_SPECIAL:
        return [dict(sf) for sf in _DIM_SPECIAL[tname]]
    if tname in _DIM_CANON:
        canon = _DIM_CANON[tname]
        multi = len(canon) > 1
        note = (" (OPTIONAL -- filled when the source unit is computable into it; "
                "concentration has no single canonical)") if multi else \
               " -- the normalised, cross-document comparable number"
        subs = [subfield(c, "double", f"Canonical {tname} value{note}.")
                for c in canon]
        subs += [
            subfield("source_unit", "char",
                     "The unit exactly as given by the source (lossless provenance)."),
            subfield("source_value", "double",
                     "The number as given by the source, in `source_unit`."),
            subfield("approximate", "boolean", "True when the value is approximate."),
        ]
        return subs
    return None

def _expand_named_types(fields):
    """Recursively attach declared sub_fields to every named-composite-typed field."""
    n = 0
    for f in fields or []:
        subs = _named_type_subfields(f.get("type"))
        if subs is not None and not f.get("fields"):
            f["fields"] = subs
            n += 1
        if f.get("fields"):
            n += _expand_named_types(f["fields"])
    return n

_expanded = 0
for _tier in ("stable", "draft", "deprecated"):
    _dir = os.path.join(VETA, _tier)
    if not os.path.isdir(_dir):
        continue
    for _fn in sorted(os.listdir(_dir)):
        if not _fn.endswith(".json") or _fn.endswith("_meta.json"):
            continue
        _obj = load(os.path.join(_dir, _fn))
        if "fields" not in _obj:
            continue
        if _expand_named_types(_obj["fields"]):
            _expanded += 1
            write(_tier, _fn[:-5], _obj)
print(f"V_eta named-type expansion: declared sub_fields in {_expanded} schema(s)")

# the meta-schema's `fields` description predates this use ("structure type fields")
_m = load(os.path.join(VETA, "stable", "did_schema_meta.json"))
_m["$defs"]["field_definition"]["properties"]["fields"]["description"] = (
    "Nested field definitions. Used for `structure` fields AND for the named composite "
    "types (duration/voltage/count/score/ontology_term/...), whose canonical + "
    "source-provenance layout is declared inline so validators, query-path generation and "
    "docs read one source of truth instead of hardcoding it.")
write("stable", "did_schema_meta", _m)


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
    "subject_group", "image_stack", "image_stack_parameters",
    # A did_v1 SOURCE class with a tombstone but no migrator: it passes through
    # intact, awaiting a model. Marked here so it is not counted as a go-forward
    # V_eta class in the final set.
    "subjectmeasurement",
    # Same shape: a did_v1 SOURCE class whose tombstone exists only to keep its
    # documents alive until fork A1's observation model is signed and built. It
    # has a migrator, but that migrator is a block FOLD (it keeps the class), not
    # a dissolution -- so this is still a source, not a go-forward class.
    "oneepoch",
    # The last two did_v1 classes that stranded COMPLETELY -- no V_eta schema AND
    # no migrator. Now tombstoned (search `_tombstone("generic_file"`), which
    # makes them a v1 SOURCE name holding v1 documents, never a go-forward class:
    #   generic_file    the fold to opaque_body + a statement is BUILT
    #                   (did2.convert.foldGenericFiles, team decision 2026-08-11);
    #                   the tombstone STAYS because the fold refuses rather than
    #                   guesses, and a refused document needs this class to
    #                   validate against.
    #   valid_interval  a curation judgement about a recording -- neither an
    #                   observation of the subject nor a manipulation of it. The
    #                   time-reference plan reasons about it; its build is deferred.
    # Both awaiting a TEAM decision, exactly like subjectmeasurement above.
    "generic_file", "valid_interval",
    # THE THIRD, added 2026-08-11 -- and the one with the least behind it.
    # `image_collection` had no V_eta schema and no migrator either, but unlike
    # the two above it also has NO WRITER anywhere in NDI (0 of 1002 .m files on
    # origin/main, all three spellings), so its tombstone is built from the
    # template alone. It is a v1 SOURCE name holding v1 documents, never a
    # go-forward class; the model call is open, exactly like the two above.
    "image_collection"}
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
# `zarr` LEFT THIS SET when it was deleted outright (see
# _DELETE_NO_V1_PROVENANCE): a class that does not exist cannot be a
# retained carrier, and leaving it here would have the final class set
# report a disposition for a name nothing declares.
_RET_CARRIERS = {"pyraview"}
# consumed v1 source: migrators_j.control_stimulus_ids emits `control_designation`
# (renamed per T13 -- the `ids` container word is dropped), so its docs migrate away.
_RET_RENAMED_SOURCES = {"control_stimulus_ids"}
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
# ⑦ directory, and `filter`. (The R4/R5-superseded index/geometry + ingested-cache classes
# -- ngrid, dataseries_channel_map, binaryseries_parameters, the *_epochdata_ingested caches
# -- moved OUT of KEEP into _DECIDED_PENDING below: decided to fold/rename, build deferred.)
_KEEP_INFRA = {"daqsystem", "daqreader", "daqmetadatareader",
    "epochfiles_ingested", "epochid",
    "acquisition_epoch", "filenavigator", "syncgraph", "syncrule", "syncrule_mapping",
    # `directory` was here until 2026-08-11, when the team deleted it (see
    # _DELETE_NO_V1_PROVENANCE). Keeping it in KEEP_INFRA would mark a class
    # that no longer exists as settled infrastructure.
    "filter"}

# DECIDED but BUILD-DEFERRED. The ⑥/⑦ walkthrough KEEP (above) was SUPERSEDED for these
# classes by later decisions -- R4 (`ngrid`/RF map fold into `sampled_body`) and R5 (infra
# renames, T11/T13). They still PHYSICALLY persist in the current build (so corpus validation
# is unaffected), but their fate is DECIDED: they fold or rename. Report `in_progress` with the
# decided target so the ledger/viewer stops reading a bare `persist` for a class we have
# already voted to change. The BUILD is coupled/cross-repo work, hence deferred:
#   - `ngrid` -> `sampled_body` has TWO consumers, not one. This line used to read
#     "coupled to `reverse_correlation` (its only consumer, already `retire`/D-C): the RF
#     map becomes a `sampled_body` value, then `ngrid` has no consumer." That is FALSE, and
#     it is the sentence `V_eta_ngrid_family_findings.md` F4 says "made `ngrid` look like a
#     one-class item when it is not". Folding the RF map alone leaves a live consumer, and
#     deleting `ngrid` on the strength of it would strand every `ontology_image` passthrough
#     -- the `epochfiles_ingested` regression (2,484 quarantines in corpus B) exactly.
#     RE-MEASURED against NDI origin/main @ 42c94e5, 2026-08-10:
#
#         DENOMINATOR: 91 NDI templates under ndi_common/database_documents,
#                      all 91 read; 1,467 files on origin/main, 9 mention `ngrid`
#                      (case-insensitive, bare name -- not one call shape).
#         templates whose superclasses cite data/ngrid.json:   ontologyImage   (1)
#         V_eta classes declaring `ngrid` a superclass:        ontology_image,
#                                                              reverse_correlation
#                      (243 V_eta class files inspected; hartley_calc reaches it as
#                       hartley_calc -> hartley_reverse_correlation ->
#                       reverse_correlation -> ngrid)
#
#     So: consumer A = `ontologyImage` (NDI, +setup/+NDIMaker/imageDocMaker.m:121), whose
#     vintage-B documents PASS THROUGH carrying the block and whose raster's R6 home is a
#     second-pass `image_observation` (#47) -- its only edge is `ontologyTableRow_id` and a
#     table row is not a subject. Consumer B = `hartley_calc` (NDIcalc-vis-matlab, #48),
#     whose repo is out of session scope. NEITHER is folded, so `ngrid` may not be deleted.
#   - the R5 renames land in cross-repo lockstep with the NDI writers (they emit these strings).
_DECIDED_PENDING = {
    "ngrid":
        "R4: folds into sampled_body. RETIREMENT IS GATED ON BOTH CONSUMERS (#46), "
        "not on the RF map alone: ontology_image (#47, second pass -- its only edge "
        "is ontologyTableRow_id and a table row is not a subject) and hartley_calc "
        "via reverse_correlation (#48, NDIcalc-vis-matlab, out of session scope). "
        "The block is now CARRIED VERBATIM by migrators_j/+super/ngrid.m; "
        "`coordinates` rides through undeleted until axes[].values exists (#45)",
    # THE TIME-REFERENCE COLLAPSE (#65). Increment 1 built the two targets
    # (absolute_reference, relative_reference); these eight stay until the migrators
    # move, because 24 files emit session_relative_reference, 5 emit
    # epoch_bounded_reference and 1 emits session_bounded_reference. Deleting them
    # before the emitters move would red the corpus gate.
    "time_reference":
        "#65 increment 2 DONE (the SIGNED walkthrough shape: end -> duration, "
        "value-level `approximate` deleted, `clock_tolerance` on the root). Stays "
        "as the abstract root; `is_approximate` is DEPRECATED and leaves in "
        "increment 3, gated on did2.convert.resolveSessionAnchors reporting "
        "refused_total 0 and zero surviving session_*_reference documents",
    "session_relative_reference":
        "#65 -> relative_reference (relative_to -> session; relation only, no metric). "
        "107,308 documents -- the largest emitter",
    "session_bounded_reference":
        "#65 -> relative_reference (relative_to -> session; start/end populated). "
        "20,411 documents",
    "epoch_relative_reference":
        "#65 -> relative_reference (relative_to -> epoch). ZERO documents; no migrator "
        "has ever emitted one",
    "epoch_bounded_reference":
        "#65 -> relative_reference (relative_to -> epoch; start/end populated). ZERO "
        "documents, but 5 migrator files name it",
    "event_relative_reference":
        "#65 -> relative_reference (relative_to -> the event document). ZERO documents",
    "event_bounded_reference":
        "#65 -> relative_reference (relative_to -> the event document). ZERO documents",
    "utc_reference":
        "#65 -> absolute_reference. ZERO documents. The class was named for the "
        "canonical frame; the target is named for the KIND, the same reason the class "
        "is `voltage` and not `volt`",
    # R5 targets were named in an earlier naming pass, but the ⑦ walkthrough RE-OPENED
    # this tier ("the KEEP predated T11/T13 scrutiny; needs a naming + governance
    # confirmation"), so the rename is NOT authorised to land yet. Proposed targets kept
    # here so the review has something concrete to react to.
    "binaryseries_parameters": "R5 proposed → acquisition_layout (awaiting review)",
    "daqreader_epochdata_ingested": "R5 proposed → daqreader_epoch_cache (awaiting review)",
    "daqmetadatareader_epochdata_ingested":
        "R5 proposed → daqmetadatareader_epoch_cache (awaiting review)",
    "daqreader_image_epochdata_ingested":
        "R5 proposed → fold into the daqreader cache + a modality field; ALSO needs the "
        "factual `_image` question answered by NDI (distinct cache shape, or modality "
        "label?) (awaiting review)",
}

# ---- ④ leaf-tier walkthrough findings (this session) --------------------------------
# (A) The ASSERTION family bypasses its data_type. `voltage_assertion` is a
# `numeric_assertion`, NOT `subject_assertion` + `voltage`; it redeclares `value` locally
# as a scalar rather than inheriting the composite. The reason is real -- J §5 makes an
# assertion one cell, no series, while the composites declare `value` array-valued, so it
# cannot be inherited as-is. But it costs two things:
#   * `isa <data_type>` MISSES assertions -- the chain has no `voltage` in it, so a
#     "every voltage statement" lineage query returns observations only. A real asymmetry.
#   * T12 rule 3 says cardinality is NOT a class distinction ("same quantity, different
#     cardinality -> same composite, length-N value"). A `numeric_assertion` genus that
#     exists ONLY to host the scalar case is close to the split T12 forbids.
# Marked in_progress: either the leaves pair with their composite (and scalar-ness becomes
# a constraint, not a genus), or the split stays and the reason gets recorded next to the
# classes -- which is what T12 requires of a look-alike family either way.
# Derived from the numeric lists so the marking self-maintains as the family grows.
# (A) RESOLVED: the dimensioned assertions now pair with their composite and the
# `numeric_assertion` genus is deleted (finding A closed). The one-cell guarantee it
# carried is a constraint-tightening question, deferred to TaskList #32.

# (B) `term` and `date` have NO ③ composite, so their leaves declare `value` locally --
# the only leaf families without a composite partner. Given T8/T12 make `term_*` the
# standard answer for every controlled vocabulary, `term` is arguably the most-used value
# kind in the model and the one missing its composite.
# (B) RESOLVED: `term` and `date` composites now exist and the four leaves pair with them
# (finding B closed). Left here as a marker of what was fixed, not as a pending item.

# ---- ⑤ time_reference: family consistency pass (walkthrough) ------------------------
# Three findings, so the whole family is re-opened rather than patched piecemeal:
#  1. BUG: `epoch_bounded_reference` / `epoch_relative_reference` carry a dep literally
#     named `element_id` -- naming the RETIRED `element` class -- and its must_refer is
#     `subject`, not `acquisition_epoch`. An epoch reference names a dead class and points
#     at the wrong target; the element_epoch → acquisition_epoch rename missed these deps.
#  2. `bounded` vs `relative` do not denote the same shape across the family (T11 says the
#     name encodes the shape): session_bounded has start/end but session_relative does not;
#     epoch_bounded has NO bounds while epoch_relative has t0+start+end; event_bounded has
#     no fields at all. Same suffix, different shapes -- inverted between session and epoch.
#  3. `relation` is governed inconsistently (T8 "hard-validated, not advisory"):
#     session_relative_reference.relation carries a proper enum; its sibling
#     session_bounded_reference.relation is a bare `char` with NO constraints.
for _t in ("time_reference", "utc_reference", "session_bounded_reference",
           "session_relative_reference", "epoch_bounded_reference",
           "epoch_relative_reference", "event_bounded_reference",
           "event_relative_reference"):
    _DECIDED_PENDING[_t] = ("time_reference family consistency pass: `element_id` dep "
                            "names the retired `element` (must_refer=subject, should be "
                            "acquisition_epoch); bounded/relative suffixes carry different "
                            "shapes across session/epoch/event (T11); `relation` enum-bound "
                            "on one sibling, bare char on the other (T8)")

# ---- ⑦ acquisition/infra: tier re-opened (walkthrough) ------------------------------
# The ⑥/⑦ walkthrough closed this tier as "reviewed, KEEP", but R5 then showed that
# decision predated T11/T13 scrutiny -- five of the kept classes turned out to need
# renames or a fold. Re-open the rest for the same naming/governance confirmation rather
# than trusting a KEEP that has already proven incomplete. Several are NDI-owned (the
# writers emit these class strings), so any rename lands as a cross-repo lockstep.
for _i in ("acquisition_epoch", "control_designation", "daqmetadatareader", "daqreader",
           "daqsystem", "epochfiles_ingested", "epochid", "filenavigator",
           "filter", "interaction_purpose", "syncgraph", "syncrule", "syncrule_mapping"):
    _DECIDED_PENDING[_i] = ("⑦ infra tier re-opened: the KEEP predated T11/T13 scrutiny "
                            "(R5 found 5 of its siblings needed renames/folds); needs a "
                            "naming + governance confirmation, NDI lockstep where the "
                            "writers own the class string")

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
#   - projectvar                      : infra, unsettled.
#   - ensemble                        : grain A (acquisition-infra) decided, but its NDI
#                                       second-pass member_of relations are pending
#                                       (V_eta_ensemble_plan.md) -- kept in_progress until then.
# NOTE: `instrument` RETIRED (deleted above, boundary re-audit). `openminds_import`
# REMOVED 2026-07-30 by team sign-off, reversing its earlier PERSIST call -- nothing
# ever emitted it (see the removal note above). projectvar/demo_ndi = green passthrough (re-audit: their
# retire evidence was false -- they ARE ndi v1 sources; corpus 0-doc check before any drop).
# WALKTHROUGH (this session): `interaction_purpose` -> PERSIST (re-audit KEPT it as a
# standalone annotation class and it is already built to that shape: purpose term +
# comment + interaction_id_# -> subject_interaction, so "pending" was stale).
# `control_stimulus_ids` -> RETIRE: it is a CONSUMED v1 source; migrators_j
# control_stimulus_ids.m emits the renamed `control_designation` target, so its docs
# migrate away. projectvar / demo_ndi(_mock) STAY in_progress by explicit call.
_IN_PROGRESS = {"app", "stimulus_presentation",
    "demo_ndi", "demo_ndi_mock",
    "projectvar", "ensemble"}

def _disposition(name, doc=None):
    # An EXPLICIT decided-pending marker wins over every heuristic below (including the
    # structural persist rules): we have already voted to fold/rename/reshape these, so a
    # bare `persist` from the structure would misreport a settled decision as done.
    if name in _DECIDED_PENDING:
        return ("in_progress", _DECIDED_PENDING[name])
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
    if name in _KEEP_INFRA:
        return ("persist", None)                 # ⑥/⑦ walkthrough KEEP (closed)
    if name in _RET_SOURCES:
        return ("retire", "Phase-8 source (migrator → delete)")
    if name in _RET_SERIES_OBS:
        return ("retire", "§A.9: series-observation branch → quantity leaves + data_body")
    if name in _RET_HOLDOVER or _ANALYSIS_RE.search(name):
        return ("retire", "D-C analysis-tier decompose")
    if name in _RET_CARRIERS:
        return ("retire", "2.D → data_body fold")
    if name in _RET_RENAMED_SOURCES:
        return ("retire", "consumed → control_designation (renamed target)")
    if name in _RET_TOOBS:
        return ("retire", "→ observations (needs-NDI / D10-11)")
    if name in _IN_PROGRESS:
        return ("in_progress", "⑥/⑦ walkthrough pending")
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
# schema (no superclass / typed dep) and unemitted by any migrator.
#
# NOTE the RESULT class names. This paragraph used to read "(orientation_direction_
# tuning, contrast_sensitivity, stimulus_tuningcurve) are REUSED as persisting ③
# composites and are NOT deleted". THAT IS TRUE OF ONE OF THE THREE. Measured
# 2026-08-11 against the built tree:
#
#       orientation_direction_tuning   ABSENT
#       contrast_sensitivity           PRESENT (stable/)
#       stimulus_tuningcurve           ABSENT
#
# The two absent ones are removed ~4,700 lines above, by the R2/R3 tuning-collapse
# loop: the 5 tuning result classes plus the raw `stimulus_tuningcurve` collapse into
# the single `tuning_curve` + `tuning_curve_calculation` pair, and their copytree'd
# source composites are `os.remove`d there. So they ARE deleted -- by a different
# mechanism, in a different place, under a decision (R2/R3) this set knows nothing
# about.
#
# THE CONCLUSION SURVIVES AND THE REASON DOES NOT, which is the part worth keeping
# straight: only wrapper names belong in `_DELETE_PHASE8`, and that is still correct
# -- but not because the result names are all kept. Reading this comment to answer
# "does class X survive the build?" would have given the wrong answer for two of the
# three classes it names, and it is exactly the question someone tidying this set
# would ask. `contrast_sensitivity` is the only one that really is reused.
_DELETE_PHASE8 = {
    "treatment", "treatment_drug", "treatment_transfer", "virus_injection",
    "subject_group",
    # `image_stack` and `image_stack_parameters` were HERE, and are deliberately
    # not, as of 2026-08-09. They qualified under criterion (a) -- a completed
    # dissolver consumes every document -- which is TRUE and beside the point:
    # 4,563 JH documents are consumed into `image_observation`s with an EMPTY
    # subject_id, because three of the seven imageStack construction sites in
    # NDI's +setup/+conv/+haley/doImport.m (lines 789, 811, 827 -- the image /
    # mask / closest-patch loop) set only `document_id` and never `subject_id`.
    # The criterion tests whether documents DISAPPEAR, not whether what replaces
    # them says anything, and these say nothing about nobody.
    #
    # The migrator now guards -- no subject, no observation, pass the document
    # through -- and a passthrough must have a schema to validate against, so
    # these two come back. Deleting a source tombstone ahead of its migrator is
    # exactly what put 2,484 corpus-B documents in quarantine when the epoch
    # family landed.
    #
    # They leave again when the subject is recoverable (see the note in
    # migrators_j/image_stack.m) and a corpus proves 0 survivors.
    "dataseries_observation", "timeseries_observation", "imageseries_observation",
    "oridirtuning_calc", "contrast_tuning_calc", "spatial_frequency_tuning_calc",
    "temporal_frequency_tuning_calc", "speed_tuning_calc", "contrast_sensitivity_calc",
    "tuningcurve_calc",
}
# A SEPARATE SET, DELIBERATELY. _DELETE_PHASE8 above means "a did_v1 SOURCE whose
# documents are provably consumed by a completed migrator" -- its whole contract is
# about not stranding live documents. These are a different category with a
# different justification: DID-SIDE INVENTIONS THAT WERE NEVER A did_v1 SOURCE.
# No document of these classes can arrive from a migration, because the class name
# did not exist before DID invented it. Folding them into the set above would blur
# a distinction that exists to keep deletions safe.
#
# `dataseries_channel_map` -- deleted 2026-08-09 on the team's instruction ("does it
# have any V1 provenance? If no, delete it"). Every check run before deleting, and
# the absence-based ones in NDI's OWN SPELLING, because a disposition resting on
# absence is what produced the `demo_ndi`/`demoNDI` error:
#
#   provenance file   `dataseries_channel_map | draft | V_epsilon | review/infra`
#                     -- origin V_epsilon, NOT did_v1. The provenance record is the
#                     arbiter of what counts as a v1 source.
#   version history   absent from V_alpha (the did_v1 snapshot), V_beta, V_delta;
#                     first appears in V_epsilon/draft.
#   NDI templates     absent from all of them under NORMALISED matching
#                     (lowercase, underscores stripped) -- the mechanical form of
#                     the demo_ndi check, not a raw snake_case grep.
#   NDI whole repo    zero files mention the string in ANY casing.
#   near-miss check   NDI's real `site2channelmap` is a DIFFERENT class -- deps
#                     probe_id/probe_geometry_id vs element_id/element_epoch_id,
#                     block field `map` vs `channels` -- and is separately homed in
#                     the coverage ledger (-> count_observation, retire).
#   migrators         no migrator in ANY package reads or emits it.
#   references        no V_eta schema depends on it or subclasses it. Its only
#                     remaining mention is a SENTENCE in `acquisition_epoch`'s field
#                     documentation, and that class dissolves under the epoch model.
#   coverage ledger   no v1-source row, as expected for an invention.
#
# NOT `zarr`, though it is the same category and CLAUDE.md already calls it "DELETED
# not migrated": its removal rides with the data_body model (#45), which is blocked.
#
# ---------------------------------------------------------------------------
# THE #65 TIME-REFERENCE COLLAPSE, INCREMENT 3a -- four of the seven concrete
# legacy reference classes, 2026-08-11.
#
# THIS SET, NOT `_DELETE_PHASE8`, AND THE DIFFERENCE IS THE WHOLE POINT. The
# task that produced this edit said to use `_DELETE_PHASE8`. That set's own
# contract is "a did_v1 SOURCE whose documents are provably consumed by a
# COMPLETED migrator". Neither half is true here: these four were never a
# did_v1 source (provenance V_epsilon), and no migrator consumes them because
# no migrator ever produced one. Putting them in `_DELETE_PHASE8` would have
# recorded two claims that are false in order to reach a deletion that is
# right for a different reason -- exactly the blurring the paragraph at the
# top of this block exists to prevent.
#
# THE SIGNED DECISION: `V_eta_time_reference_model_plan.md`,
# TEAM-SIGN-OFF [time_reference] jess@walthamdatascience.com / 2026-08-08 --
# 8 classes collapse to `absolute_reference` + `relative_reference`. The 8 are
# the abstract root plus its seven concrete children; the root STAYS.
#
# THE OTHER THREE CHILDREN ARE NOT TOUCHED, AND THE REASON IS EVIDENCE, NOT
# CAUTION. `session_relative_reference` (22 mint sites), `session_bounded_
# reference` (1) and `epoch_bounded_reference` (1) are minted TODAY -- a
# deliberate pass-1 handle, because a migrator cannot emit `relative_reference`
# without the session DOCUMENT's id. Deleting a class its emitters still mint
# is the `epochfiles_ingested` regression: 2,484 corpus-B quarantines.
#
# EVERY CHECK, RE-RUN FOR EACH OF THE FOUR SEPARATELY, WITH ITS DENOMINATOR.
# The absence-based ones are run under NORMALISED matching (lowercase,
# underscores stripped) because V_eta is snake_case and NDI is camelCase --
# the `demo_ndi`/`demoNDI` failure -- and every sweep was run against the five
# LIVE siblings first as a POSITIVE CONTROL, so a zero here is a measurement
# and not a property of the query.
#
#   NDI templates     0 of 91 templates on NDI-matlab origin/main declare any
#                     of the four, under normalised matching. Stronger, and
#                     the reason this one is not delicate: NOT ONE of the 91
#                     class_names contains the substring `reference` at all.
#                     There is no camelCase spelling to have missed.
#   version history   absent from V_alpha (the did_v1 snapshot), V_beta and
#                     V_delta; first appear in V_epsilon/stable.
#   provenance file   all four `| stable | V_epsilon |` in
#                     V_eta_class_provenance.md. Origin V_epsilon, NOT did_v1.
#   migrators         0 mint sites, across ALL THREE idioms, over the 187 .m
#                     files of DID-matlab +did2/+convert (the 24 batch
#                     post-passes included) and the 17 of NDI-matlab
#                     +ndi/+migrate. The sweep enumerates the FULL minted set
#                     -- 45 distinct class names, from 77 idiom-1 sites, 21
#                     idiom-2 (`classBlock`) and 4 idiom-3 -- and none of the
#                     four is in it. The 17 mints whose class name is a
#                     VARIABLE are resolved, not counted as a zero: 16 take
#                     their value from string literals, and the four names
#                     occur as a string literal NOWHERE in either repo (the
#                     complete `*reference*` literal inventory of those 204
#                     files is 14 distinct strings, none of them these). The
#                     17th, universalRenames.m:88, COMPUTES its name as
#                     `v1ToVDeltaClassName(snakeCase(v1 class))`; that map is
#                     two rows (contrasttuning_calc, contrastsensitivity_calc)
#                     and no NDI class snake-cases into any of the four.
#   whole-repo sweep  normalised, over 443 DID-matlab and 1,262 NDI-matlab
#                     files: 2 lines total, BOTH inside `%` comments
#                     (migrators_j/stimulus_response_scalar.m:184 says
#                     `epoch_relative_reference` "was the other candidate";
#                     resolveSessionAnchors.m:43 says the `epoch_*`/`event_*`/
#                     `utc_reference` classes are NOT touched there). A comment
#                     is not an emitter. The same sweep returns 411 lines for
#                     `relative_reference` and 188 for `session_relative_
#                     reference`, which is what makes these zeros readable.
#   V_eta schemas     0 superclass references and 0 `must_refer_to_document_
#                     class` references, over 243 class-declaring schema files.
#   coverage ledger   no v1-source row in V_eta_coverage_ledger.{md,json}; no
#                     row in V_eta_migration_targets.json; absent from
#                     V_eta_ndi_ground_truth.json. As expected for inventions.
#   corpus            NOT MEASURED, AND SAID SO RATHER THAN COUNTED AS ZERO.
#                     No corpus report is reachable from this checkout --
#                     V_eta_STATUS.md's own denominator reads `*-summary.json`
#                     reports read: 0, corpora named: NONE. The record (the
#                     plan document, and CLAUDE.md quoting it) says these
#                     classes had zero documents across five corpora, and run
#                     31508009545 was still `pending` when this landed. THE
#                     STATIC EVIDENCE IS WHAT CARRIES THIS DELETION. The
#                     corpora are a SAMPLE; absence from them would not be
#                     absence in the universe, and is not what is relied on.
#
# TWO RESIDUES, RECORDED BECAUSE THEY OUTLIVE THIS EDIT AND ARE NOT FIXED HERE:
#   1. `schemas/V_eta/examples/utc_reference_grid.json` is an EXAMPLE DOCUMENT
#      instance of `utc_reference`. It is copied in from V_zeta, not generated,
#      so this delete loop (which walks TIERS only) does not reach it. It
#      strands no real data -- an example is illustrative -- but the built tree
#      now ships an example of a class it does not define.
#   2. `directed_relation`'s `time_reference_#` field documentation names
#      `event_relative_reference` in PROSE (see the `write()` call above). It
#      is documentation, not a structural reference, so it does not block the
#      deletion; under the collapse the right word is `relative_reference`.
# Both are left for the team: fixing 1 means hand-editing under `schemas/`
# (operating rule 1) and fixing 2 is a change to another class's schema.
#
# ALSO LEFT ALONE DELIBERATELY: section 8e's `EVENT_ANCHOR` transform still
# names `event_relative_reference` / `event_bounded_reference`. It runs BEFORE
# this loop and is already guarded by `if not p: continue`, so it becomes a
# no-op rather than an error. It is dead for these two classes; it is not
# removed here because that is a transform change, not a disposition change.
_DELETE_NO_V1_PROVENANCE = {
    "dataseries_channel_map",
    # TEAM DECISION 2026-08-14: delete `zarr`, per signed sec.10 "zarr is
    # DELETED, not migrated". Provenance V_gamma -- a DID-side invention that
    # was never a did_v1 class, so no NDI document can be one. Measured before
    # the deletion, in the same shape as `directory` above, and every figure is
    # zero:
    #
    #     DENOMINATOR: 248 V_eta schema file(s), 91 NDI template class(es),
    #                  195 .m file(s) under DID-matlab +convert/
    #     V_eta schemas SUBCLASSING zarr          NONE
    #     V_eta schemas DEPENDING on zarr         NONE
    #     migrators/passes minting or consuming   NONE
    #     NDI class names normalising to "zarr"   NONE
    #
    # THE TWO STRING MATCHES THAT REMAIN ARE NOT REFERENCES TO THE CLASS, and
    # are checked rather than assumed -- this repository has twice mistaken a
    # string match for a reference. `acquisition_epoch.storage.format` carries
    # the documentation "Physical encoding (vhsb | zarr | ome_ngff | ...)", a
    # FORMAT VALUE; and `+migrators_j/daqreader_image_epochdata_ingested.m:163`
    # names it in a COMMENT listing classes it does not emit.
    #
    # ITS `codecs[]` IS NOT COPIED ANYWHERE, which is the substantive half of
    # the decision: it models per-chunk ARRAY codecs, while the compression
    # V_eta actually meets is archives (`.nbf.tgz`, `.zip`) and `tiff`+`lzw` --
    # which is what the new `data_body.compression` char carries.
    "zarr",
    # TEAM DECISION 2026-08-11 (jess, in session): delete `directory`.
    #
    # Provenance V_gamma, "review/infra" -- a DID-side invention that was never
    # a did_v1 class, so no NDI document can be one. Measured before the call,
    # and every figure is zero:
    #
    #     DENOMINATOR: 245 V_eta schema files, 91 NDI templates, 4 code trees
    #     V_eta schemas subclassing it            NONE
    #     V_eta schemas depending on it           NONE (its only dep edge was
    #                                             its OWN parent_directory_id)
    #     migrators/passes minting it             NONE
    #     migrators/passes consuming it           NONE
    #     directory_role / manifest_format /
    #       base_uri anywhere in any code         0
    #     NDI class names normalising to
    #       "directory"                           NONE
    #
    # THE ONE STRING MATCH IN CODE IS NOT THIS CLASS. `jSorterOutput.m:134`
    # writes `struct('format', 'directory', ...)` on an `opaque_body` -- a
    # FORMAT VALUE meaning "these bytes are a directory". status_board.py
    # already carries a comment about that exact trap. Grepping the bare word
    # would have found 200+ hits, nearly all `fileparts`/`dirname` calls; the
    # check that decides this is the three DISTINCTIVE field names, which
    # appear nowhere at all.
    #
    # The normalisation sweep was run because this disposition rests on
    # ABSENCE, and that is how `demo_ndi` was nearly deleted -- dispositioned
    # on a grep for a spelling NDI has never contained (it is `demoNDI`).
    # No NDI class name normalises to "directory".
    #
    # RESIDUAL RISK, stated because it is the one thing not measured: this came
    # from V_gamma, so a V_gamma/V_delta-era migrated database could hold
    # `directory` documents, which this deletion would leave with no schema --
    # the `image_stack` failure, where phase-8 deletion turned 4,563 documents
    # into "No schema file for class". The team accepted that risk knowingly;
    # the remedy if such a database turns up is a `deprecated/` tombstone, the
    # same one that restored `image_stack`.
    "directory",
    "epoch_relative_reference",
    "event_bounded_reference",
    "event_relative_reference",
    "utc_reference",
}

_deleted = []
_deleted_invented = []
# A SHRINKING DENOMINATOR. This loop decides which schemas are REMOVED from the
# built set, and a file it could not read was silently not a candidate: the
# class survived the delete and the printed `removed N` shrank to match, so
# both halves of the evidence moved together. The three counters below are what
# make "nothing qualified" and "nothing could be asked" different sentences.
_delete_scan = {"candidates": 0, "unreadable": 0}
for tier in TIERS:
    for p in glob.glob(os.path.join(VETA, tier, "*.json")):
        base = os.path.basename(p)
        if base in META_FILES:
            continue
        _delete_scan["candidates"] += 1
        try:
            cn = load(p)["document_class"]["class_name"]
        except (OSError, json.JSONDecodeError, KeyError, TypeError):
            _delete_scan["unreadable"] += 1
            continue
        if cn in _DELETE_PHASE8:
            os.remove(p)
            _deleted.append(cn)
        elif cn in _DELETE_NO_V1_PROVENANCE:
            os.remove(p)
            _deleted_invented.append(cn)
print(f'V_eta delete pass: DENOMINATOR {_delete_scan["candidates"]} schema file(s) '
      f'inspected, {_delete_scan["unreadable"]} UNREADABLE; '
      f'{len(_deleted)} phase-8 + {len(_deleted_invented)} no-v1-provenance removed')
if _delete_scan["unreadable"]:
    print("  *** A SCHEMA FILE THAT COULD NOT BE READ WAS NOT CONSIDERED FOR "
          "DELETION. It is still in the built set.")
if _deleted:
    print(f"V_eta Phase-8 delete: removed {len(_deleted)} consumed source schemas: "
          + ", ".join(sorted(_deleted)))
if _deleted_invented:
    print(f"V_eta delete (no v1 provenance): removed {len(_deleted_invented)}: "
          + ", ".join(sorted(_deleted_invented)))


# ---------- NDI REQUIRED-NESS STAMP  (report-only instrumentation) ----------
# The logic lives in tools/ndi_required_stamp.py so it can be imported and
# tested WITHOUT running a build. A property that can only be exercised by
# executing this 6,700-line script is a property nothing tests, and the one
# thing this stamp must prove is a NEGATIVE -- that it never touches a
# `mustBeNonEmpty` value.
#
# Loaded BY PATH rather than by name: `tools/` is not a package, so an
# `import ndi_required_stamp` resolves only when the interpreter's cwd happens
# to put it on sys.path. tests/test_veta.py's `_load_tool` exists for the same
# reason -- it works in CI and from any directory.
import importlib.util as _ilu  # noqa: E402

_spec = _ilu.spec_from_file_location(
    "_veta_ndi_required_stamp", os.path.join(ROOT, "tools", "ndi_required_stamp.py"))
_nrs = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_nrs)
stamp_ndi_required, render_stamp_report = _nrs.stamp_ndi_required, _nrs.render_stamp_report

_GT_PATH = os.path.join(ROOT, "schemas", "V_eta_ndi_ground_truth.json")

_MIGRATION_TARGETS_PATH = os.path.join(
    ROOT, "schemas", "V_eta_migration_targets.json")

# `_DELETE_PHASE8` and the migration-target map are what split "NOT MEASURED"
# into causes. They are PASSED IN rather than re-derived inside the stamp: the
# deleted set is this file's own datum, and the target map is the record of
# what each migrator actually emits (`tools/refresh_migration_targets.py`,
# whose `--check` gates.py runs, so it is not stale in a green run). The
# coverage ledger says the same things but is generated AFTER this step, so
# reading it here would report the PREVIOUS run's answer.
_NDI_REQ = stamp_ndi_required(VETA, _GT_PATH, RENAME, TIERS, META_FILES,
                              deleted_phase8=_DELETE_PHASE8,
                              targets_path=_MIGRATION_TARGETS_PATH)
for _line in render_stamp_report(_NDI_REQ):
    print(_line)

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
