"""V_eta (Brainstorm J) schema-set integrity tests.

Validate the V_eta set on its own terms: every schema file passes the
meta-schema, index.json agrees with disk, superclass and dependency references
resolve, the tier folder matches maturity_level, and the Brainstorm-J subject
model composes (bare-identity subject, restored subject_statement, the
subject_relation branch, the subject_assertion genus, and the renamed
subject_observation / subject_manipulation direction classes).

Scope note: the leaf-tier depth (dose/formulation composites replacing the
pharmacological family, the dataseries -> data_body consolidation, and the
meta-schema `binding` formalization) is an in-progress follow-up; those tests
land with that increment.
"""
import glob
import json
import os

import jsonschema
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_tool(name):
    """Load tools/<name>.py by PATH.

    `tools/` is not a package (no __init__.py) and the project installs with
    `pip install -e .`, so `import tools.<name>` happens to resolve locally --
    the repo root is on sys.path when pytest is run from it -- and raises
    ModuleNotFoundError in CI. Loading by path works in both, and does not
    depend on where pytest was invoked from.
    """
    import importlib.util
    path = os.path.join(REPO_ROOT, "tools", name + ".py")
    spec = importlib.util.spec_from_file_location("_veta_tool_" + name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
VETA = os.path.join(REPO_ROOT, "schemas", "V_eta")
TIERS = ["stable", "draft", "deprecated"]
META_FILES = {"did_schema_meta.json", "CURIE_lookups_meta.json", "ndi_reserved_keys.json",
              "binding_registry_meta.json"}


def _load(path):
    with open(path) as f:
        return json.load(f)


META = _load(os.path.join(VETA, "stable", "did_schema_meta.json"))
INDEX = _load(os.path.join(VETA, "index.json"))


def _doc_files():
    out = []
    for tier in TIERS:
        for p in sorted(glob.glob(os.path.join(VETA, tier, "*.json"))):
            if os.path.basename(p) not in META_FILES:
                out.append((tier, p))
    return out


def _records():
    recs = {}
    for tier, p in _doc_files():
        d = _load(p)
        recs[d["document_class"]["class_name"]] = (tier, d)
    return recs


DOC_FILES = _doc_files()
RECORDS = _records()


@pytest.mark.parametrize("tier,path", DOC_FILES, ids=[os.path.basename(p) for _, p in DOC_FILES])
def test_file_passes_meta_schema(tier, path):
    jsonschema.validate(instance=_load(path), schema=META)


@pytest.mark.parametrize("tier,path", DOC_FILES, ids=[os.path.basename(p) for _, p in DOC_FILES])
def test_filename_matches_class_and_tier(tier, path):
    dc = _load(path)["document_class"]
    assert dc["class_name"] + ".json" == os.path.basename(path)
    assert dc["maturity_level"] == tier


def test_index_agrees_with_disk():
    on_disk = set(RECORDS) | {f[:-5] for f in META_FILES}
    in_index = {e["class_name"] for e in INDEX["schemas"]}
    assert on_disk == in_index, f"index/disk drift: {on_disk ^ in_index}"
    assert INDEX["set_version"] == "V_eta"
    assert INDEX["based_on"] == "V_zeta"


def test_superclasses_resolve():
    # DENOMINATOR. Without it this passes when RECORDS is EMPTY -- a build that
    # produced no schemas would go green on the sweep that exists to check them
    # all. Same failure as a census reporting 0 while reading nothing.
    assert len(RECORDS) > 200, f"only {len(RECORDS)} schemas loaded"
    names = set(RECORDS)
    for name, (_, d) in RECORDS.items():
        for s in d["document_class"]["superclasses"]:
            assert s["class_name"] in names, f"{name} -> missing superclass {s['class_name']}"


def test_dependencies_resolve():
    names = set(RECORDS)
    for name, (_, d) in RECORDS.items():
        for dep in d.get("depends_on", []):
            for tok in [t for t in dep["must_refer_to_document_class"].split(",") if t]:
                assert tok in names, f"{name}.{dep['name']} -> missing class {tok}"


def _chain(name):
    out = [name]
    for s in RECORDS[name][1]["document_class"]["superclasses"]:
        out += _chain(s["class_name"])
    return out


def _flat_field_types(name):
    types = {}
    for c in reversed(_chain(name)):
        for f in RECORDS[c][1].get("fields", []):
            types[f["name"]] = f["type"]
    return types


def _flat_dep_names(name):
    deps = set()
    for c in _chain(name):
        for dep in RECORDS[c][1].get("depends_on", []):
            deps.add(dep["name"])
    return deps


# ---- Brainstorm J: subject side ----

def test_subject_is_bare_identity():
    """is_group / is_biological removed; kind is a term_assertion, not a flag."""
    fields = {f["name"] for f in RECORDS["subject"][1]["fields"]}
    assert fields == {"local_identifier", "description"}, fields
    assert RECORDS["subject"][1]["document_class"]["class_version"] == "3.0.0"
    assert RECORDS["subject"][1]["depends_on"] == []


def test_subject_statement_restored_and_owns_variable():
    """subject_statement is the abstract parent owning subject_id + variable."""
    assert "subject_statement" in RECORDS
    dc = RECORDS["subject_statement"][1]["document_class"]
    assert dc.get("abstract") is True
    assert dc["superclasses"] == [{"class_name": "base"}]
    assert _flat_field_types("subject_statement").get("variable") == "ontology_term"
    assert "subject_id" in _flat_dep_names("subject_statement")


def test_interaction_and_assertion_are_statement_children():
    for child in ("subject_interaction", "subject_assertion"):
        assert "subject_statement" in _chain(child), f"{child} not under subject_statement"


def test_spine_composes_onto_every_interaction():
    """Every interaction leaf inherits subject_id, variable, required time, method."""
    for name in RECORDS:
        if "subject_interaction" not in _chain(name):
            continue
        ft, deps = _flat_field_types(name), _flat_dep_names(name)
        assert "subject_id" in deps, f"{name} missing subject_id"
        assert "time_reference_#" in deps, f"{name} missing time_reference"
        assert ft.get("variable") == "ontology_term", f"{name} missing variable"
        assert ft.get("method") == "ontology_term", f"{name} missing method"
        assert ft.get("sample_time") == "structure", f"{name} missing sample_time"


def test_path_t_removed_and_element_id_retired():
    """Path T target_structure and V_zeta's element_id are gone from the spine."""
    ft = _flat_field_types("subject_interaction")
    assert "target_structure" not in ft
    assert "element_id" not in _flat_dep_names("subject_interaction")


def test_instrument_id_is_optional_device_edge():
    deps = {d["name"]: d for d in RECORDS["subject_interaction"][1]["depends_on"]}
    assert "instrument_id" in deps
    assert deps["instrument_id"]["mustBeNonEmpty"] is False
    assert deps["instrument_id"]["must_refer_to_document_class"] == "subject"


def test_derived_from_is_statement_typed_provenance():
    # A computed observation records its inputs via derived_from_#, typed to a
    # subject_statement leaf (NEVER an entity) -- the provenance inverse of
    # directed_relation's entity->entity child/parent.
    deps = {d["name"]: d for d in RECORDS["subject_observation"][1]["depends_on"]}
    assert "derived_from_#" in deps
    df = deps["derived_from_#"]
    assert df["must_refer_to_document_class"] == "subject_statement"
    assert df["must_refer_to_document_class"] != "entity"
    assert df["mustBeNonEmpty"] is False
    # inherited by the value leaves (a computed observation is a leaf)...
    assert "derived_from_#" in _flat_dep_names("angle_observation")
    assert "derived_from_#" in _flat_dep_names("score_observation")
    # ...but NOT on manipulations or assertions: computation is an observation mode
    # (a manipulation is imposed, an assertion is declared -- neither is derived).
    assert "derived_from_#" not in _flat_dep_names("subject_manipulation")
    assert "derived_from_#" not in _flat_dep_names("term_assertion")


def test_direction_classes_renamed():
    for new in ("subject_observation", "subject_manipulation"):
        assert new in RECORDS
    for old in ("observation", "manipulation", "annotation", "group_assignment"):
        assert old not in RECORDS, f"{old} should be gone in V_eta"


def test_leaf_tier_named_by_data_type_no_scalar_prefix():
    """Observation leaves are <dim>_observation (one word, no scalar_ prefix)."""
    for dim in ("mass", "temperature", "length", "duration", "volume", "pressure",
                "frequency", "voltage", "current", "concentration", "count", "score",
                "intensity"):
        leaf = f"{dim}_observation"
        assert leaf in RECORDS, f"missing {leaf}"
        assert f"scalar_{dim}_observation" not in RECORDS
        assert "subject_observation" in _chain(leaf)
        assert _flat_field_types(leaf).get("value") == dim
    # categorical -> the single term_observation; no scalar umbrella
    assert "term_observation" in RECORDS and "categorical_observation" not in RECORDS
    assert "scalar_observation" not in RECORDS and "scalar_manipulation" not in RECORDS


def test_subject_assertion_is_genus_with_typed_leaves():
    dc = RECORDS["subject_assertion"][1]["document_class"]
    assert dc.get("abstract") is True and "subject_statement" in _chain("subject_assertion")
    assert "term_assertion" in RECORDS and "date_assertion" in RECORDS
    # Every assertion leaf is direction x data_type, like every other leaf (finding A).
    # The `numeric_assertion` genus is gone: it held no fields and existed only to carry
    # a `mustBeScalar` flag, which cost an `isa <data_type>` query the assertions.
    assert "numeric_assertion" not in RECORDS
    for leaf, composite in (("mass_assertion", "mass"), ("voltage_assertion", "voltage"),
                            ("term_assertion", "term"), ("date_assertion", "date")):
        chain = [s["class_name"]
                 for s in RECORDS[leaf][1]["document_class"]["superclasses"]]
        assert chain == ["subject_assertion", composite], f"{leaf} chain {chain}"
        assert not RECORDS[leaf][1].get("fields"), f"{leaf} should own no fields"
    # the value is inherited from the composite, so `isa <data_type>` spans directions
    assert _flat_field_types("mass_assertion").get("value") == "mass"
    assert "mass" in _chain("mass_assertion") and "mass" in _chain("mass_observation")


def test_relation_branch():
    # subject_relation was renamed to `relation` and generalized to entity<->entity.
    assert "subject_relation" not in RECORDS
    assert RECORDS["relation"][1]["document_class"].get("abstract") is True
    for cls, endpoints in (("directed_relation", {"child", "parent"}),
                           ("undirected_relation", {"entities"})):
        assert "relation" in _chain(cls)
        assert endpoints <= _flat_dep_names(cls), f"{cls} endpoints {endpoints}"
        assert _flat_field_types(cls).get("relation") == "ontology_term"


def test_entity_genus():
    assert RECORDS["entity"][1]["document_class"].get("abstract") is True
    for e in ("subject", "person", "organization", "publication", "funding",
              "dataset", "web_resource", "session"):
        assert "entity" in _chain(e), f"{e} should descend from entity"
    # directed_relation endpoints are entities now, not just subjects
    dr = {d["name"]: d for d in RECORDS["directed_relation"][1]["depends_on"]}
    assert dr["child"]["must_refer_to_document_class"] == "entity"
    # dataset documentation/homepage links are relations -> web_resource, not fields
    dataset_fields = {f["name"] for f in RECORDS["dataset"][1]["fields"]}
    assert "documentation" not in dataset_fields


def _local_id(cls):
    fs = {f["name"]: f for f in RECORDS[cls][1].get("fields", [])}
    return fs.get("local_identifier")


def test_local_identifier_required_on_subject_optional_elsewhere():
    """local_identifier is a schema-enforced handle: REQUIRED on subject, OPTIONAL
    on every other entity, and NOT declared on the abstract `entity` parent (so
    subject *adds* a required field rather than illegally overriding a
    parent-optional one). Requiredness is expressed by placement, like the timing
    model — not an ingest convention."""
    # the parent stays neutral (no local_identifier -> no forbidden override)
    assert _local_id("entity") is None
    # subject requires it
    sub = _local_id("subject")
    assert sub is not None and sub["mustBeNonEmpty"] is True
    # every other entity carries it, optional
    for e in ("dataset", "person", "organization", "publication", "funding",
              "web_resource", "session"):
        f = _local_id(e)
        assert f is not None, f"{e} should carry an optional local_identifier"
        assert f["mustBeNonEmpty"] is False, f"{e}.local_identifier must be optional"


def test_demo_family_collapsed_to_one_class():
    """REWRITTEN TWICE IN ONE DAY, and both moves are the point.

    (1) It began as `test_mock_class_dropped`, asserting `mock` should NOT exist
        because "nothing constructs it". That premise was FALSE -- NDI's
        demoNDIMock IS-A mock, and ndi.calc.example.simple sets
        numberOfSelfTests = 2 and writes those documents against a LIVE session.
        The test asserted the defect (CLAUDE.md: a test written from the same
        premise as the code cannot catch the code), so it was inverted.

    (2) Inverting it exposed that `demo_ndi_mock` carries NO FIELDS OF ITS OWN --
        its entire content is "I am a mock demo". That is a flag, not a kind of
        thing, which is the same test the time_reference collapse turned on
        (`mode` was cardinality, not a class axis). A mock voltage_observation
        would still be a voltage observation.

    So three classes collapse to one: `demo` with an `is_mock` boolean. `mock`
    and `demo_ndi_mock` cease to exist, and `demo` drops the framework's own name
    out of a class name in the framework's own schema (T13).

    OPEN, and the team's to settle: whether mock documents should be REFUSED at
    migration rather than carried flagged. If they are to be carried, the flag
    arguably belongs on `base` so ANY document is checkable -- not built that way
    for one bearer today.
    """
    assert "demo" in RECORDS
    for gone in ("mock", "demo_ndi", "demo_ndi_mock"):
        assert gone not in RECORDS, f"{gone} should have collapsed into `demo`"

    fields = {f["name"]: f for f in RECORDS["demo"][1]["fields"]}
    assert set(fields) == {"value", "is_mock"}, set(fields)
    # Typed from the WRITER, not the template: the did_v1 template says char, but
    # ndi.calc.example.simple sets 5/10 and queries with exact_number.
    assert fields["value"]["type"] == "double"
    assert fields["is_mock"]["type"] == "boolean"
    assert fields["is_mock"]["default_value"] is False
    # The required file was dropped by V_eta -- silent file loss. It is back.
    assert [f["name"] for f in RECORDS["demo"][1].get("file", [])] == ["filename1.ext"]


def test_value_set_class_dropped():
    """value_set is dropped (Q1): orphaned + redundant with the binding registry,
    which carries the admissible-set definition inline. The registry META still
    uses value_set as a string key (see the binding-registry test below)."""
    assert "value_set" not in RECORDS


def test_timing_cadence_moved_off_time_reference():
    """time_reference.sampling removed; the cadence lives in sample_time (D1)."""
    tr_fields = {f["name"] for f in RECORDS["time_reference"][1]["fields"]}
    assert "sampling" not in tr_fields
    assert _flat_field_types("subject_interaction").get("sample_time") == "structure"


# ---- increment 2: leaf-tier depth ----

def test_manipulation_tier_is_strict_j():
    """No delivery-method family, no escape hatch (D8); data-type-named leaves."""
    for gone in ("injection", "bath", "stimulus_bath", "pharmacological_manipulation",
                 "generic_manipulation", "generic_scalar", "generic_scalar_observation",
                 "generic_scalar_manipulation", "biological_transfer"):
        assert gone not in RECORDS, f"{gone} must be retired in strict J"
    for leaf in ("dose_manipulation", "formulation_manipulation", "term_manipulation",
                 "temperature_manipulation"):
        assert leaf in RECORDS and "subject_manipulation" in _chain(leaf)
    # composites are structure-typed value mixins
    for comp in ("dose", "formulation", "chemical"):
        assert comp in RECORDS
        assert _flat_field_types(comp).get("value") == "structure"
    assert "dose" in _chain("dose_manipulation")
    # term_manipulation carries a bound term value (payload-free acts live here)
    assert _flat_field_types("term_manipulation").get("value") == "ontology_term"


def test_storage_mode_on_statement():
    ft = _flat_field_types("subject_statement")
    assert ft.get("storage_mode") == "char"
    sm = next(f for f in RECORDS["subject_statement"][1]["fields"]
              if f["name"] == "storage_mode")
    assert set(sm["constraints"]["enum"]) == {"inline", "reference", "body"}


def test_conditions_on_statement():
    """subject_statement carries a `conditions` list (D10 qualifiers, renamed from
    `parameters`) of typed {variable, value} entries — each with a variable plus
    nested term/count/quantity data-type blocks (exactly-one is an ingest validator,
    provisional). A per-reading array value is the independent-variable axis; a
    length-1 value is a held-fixed covariate."""
    ft = _flat_field_types("subject_statement")
    assert ft.get("conditions") == "structure"
    assert ft.get("parameters") is None, "old `parameters` name must be gone"
    params = next(f for f in RECORDS["subject_statement"][1]["fields"]
                  if f["name"] == "conditions")
    # a list (non-scalar), not a single struct
    assert params["mustBeScalar"] is False
    sub = {f["name"]: f for f in params["fields"]}
    assert sub["variable"]["type"] == "ontology_term"
    # the three nested typed value blocks, each holding an array `value`
    for block in ("term", "count", "quantity"):
        assert block in sub, f"conditions missing {block} block"
        val = next(f for f in sub[block]["fields"] if f["name"] == "value")
        assert val["mustBeScalar"] is False, f"{block}.value must be an array"
    assert sub["term"]["fields"][0]["type"] == "ontology_term"


def test_session_bounded_reference():
    """A bounded [start, end] window relative to the session/assay (D10 multi-party
    binding) — no parent interaction/epoch required."""
    assert "session_bounded_reference" in RECORDS
    assert "time_reference" in _chain("session_bounded_reference")
    ft = _flat_field_types("session_bounded_reference")
    assert ft.get("start") == "duration" and ft.get("end") == "duration"
    # no required deps (session rides on base.session_id)
    deps = RECORDS["session_bounded_reference"][1]["depends_on"]
    assert all(not d.get("mustBeNonEmpty") for d in deps)


def test_directed_relation_optional_time_reference():
    """An event-relation (e.g. encountered) can carry when — an optional
    time_reference dep so the relation is the timestamped record (D10)."""
    deps = {d["name"]: d for d in RECORDS["directed_relation"][1]["depends_on"]}
    assert "time_reference_#" in deps
    assert deps["time_reference_#"]["mustBeNonEmpty"] is False
    # child/parent stay required
    assert deps["child"]["mustBeNonEmpty"] is True


def test_assertion_is_timeless():
    """Timing model: requiredness is expressed by WHERE time_reference is declared.
    subject_interaction REQUIRES it (event); subject_assertion declares NONE at all
    (a timeless fact cannot even carry a clock anchor); the shared subject_statement
    parent stays neutral. So it is never a uniform parent-optional flag."""
    # DENOMINATOR: count the assertions actually examined, so a chain lookup
    # that silently stopped matching cannot leave this passing on zero classes.
    seen = 0
    for name in RECORDS:
        chain = _chain(name)
        if "subject_assertion" not in chain and name != "subject_assertion":
            continue
        seen += 1
        deps = _flat_dep_names(name)
        assert "time_reference_#" not in deps, \
            f"{name} is an assertion — it must not declare time_reference"
    assert seen > 1, f"only {seen} assertion class(es) examined"
    # the parent declares no time either; only the interaction branch requires it
    assert "time_reference_#" not in _flat_dep_names("subject_statement")
    assert _flat_dep_names("subject_interaction")  # (interaction side checked above)


def test_data_body_classes():
    assert RECORDS["data_body"][1]["document_class"].get("abstract") is True
    # `statement` is declared per child, not on the abstract parent (placement
    # pattern): required on sampled_body (a statement's stream), optional on
    # opaque_body (may be a standalone attachment).
    assert "statement" not in _flat_dep_names("data_body")
    for body in ("sampled_body", "opaque_body"):
        assert "data_body" in _chain(body)
        assert RECORDS[body][0] == "draft"
    sampled_deps = {d["name"]: d for d in RECORDS["sampled_body"][1]["depends_on"]}
    assert sampled_deps["statement"]["mustBeNonEmpty"] is True
    opaque_deps = {d["name"]: d for d in RECORDS["opaque_body"][1]["depends_on"]}
    assert opaque_deps["statement"]["mustBeNonEmpty"] is False
    sft = _flat_field_types("sampled_body")
    assert sft.get("datum") == "structure" and sft.get("sample_time") == "structure"
    assert sft.get("summary") == "structure"
    # 2.D Option 1: sampled_body stays LEAN (a no-daq derived body needs only
    # datum + sample_time + bytes). The acquisition header lives on
    # acquisition_epoch. The ONE opt-in addition is `axes` for multi-dim derived
    # data with no epoch -- optional (array-of-records), so it never burdens the
    # common scalar/time-series case.
    sampled_axes = next(f for f in RECORDS["sampled_body"][1]["fields"]
                        if f["name"] == "axes")
    assert sampled_axes["mustBeNonEmpty"] is False
    assert sampled_axes["mustBeScalar"] is False
    # opaque_body carries a small descriptor (generic_file is INTENDED to fold onto
    # it, 2.D slice A -- see test_the_two_stranding_classes_have_a_tombstone for why
    # that fold is not built and what opaque_body still lacks).
    of = {f["name"] for f in RECORDS["opaque_body"][1]["fields"]}
    assert {"format", "filename", "description"} <= of


def test_the_two_stranding_classes_have_a_tombstone():
    """`generic_file` and `valid_interval` are REAL did_v1 classes that had NO V_eta
    schema AND no migrator -- the only two in that state. With neither, a document
    of these classes is not migrated, not passed through and not quarantined; it is
    lost.

    THIS TEST REPLACES `test_generic_file_folded_to_opaque_body`, which asserted
    `"generic_file" not in RECORDS`. That assertion was TRUE and it was pinning the
    stranding: the fold it named was never built (0 of 82 migrators_j entries match
    generic|valid), so "dissolves into opaque_body" described an intention, and the
    test made the intention indistinguishable from the outcome. Inverted rather than
    deleted, for the same reason the three `epochid` tests were inverted.

    What is asserted now is the tombstone, NOT a model: both classes are v1 SOURCE
    names marked `retire`, restated from the NDI writer, holding v1 documents alive
    until the team signs a model. The fold to opaque_body is still the intended
    destination for generic_file -- it cannot happen yet because opaque_body has no
    content_hash to hold the MD5 `checksum`, which is checked here so that the day
    it gains one, this test says so."""
    disp = {e["class_name"]: e.get("disposition") for e in INDEX["schemas"]}
    for name in ("generic_file", "valid_interval"):
        assert name in RECORDS, (
            "%s has no V_eta schema; a document of this class reaches validation "
            "as an undeclared class and is lost" % name)
        assert disp[name] == "retire", (
            "%s is a v1 SOURCE tombstone, never a go-forward class" % name)

    # generic_file, from +setup/+conv/+babu/import.m:526-531 and :575-580 --
    # all five fields, the file, and the document_id edge.
    gf = RECORDS["generic_file"][1]
    assert {f["name"] for f in gf["fields"]} == {
        "filename", "format_ontology", "checksum", "date_created", "date_updated"}
    assert [f["name"] for f in gf["file"]] == ["generic_file.ext"]
    assert [d["name"] for d in gf["depends_on"]] == ["document_id"]

    # THE FIELD THAT BLOCKS THE FOLD. opaque_body has format/filename/description
    # and no content_hash (#45, blocked on #32), so folding today drops the MD5.
    assert "checksum" in {f["name"] for f in gf["fields"]}
    assert "content_hash" not in {f["name"] for f in RECORDS["opaque_body"][1]["fields"]}, \
        ("opaque_body gained content_hash -- the generic_file -> opaque_body fold is "
         "no longer blocked on it; re-open the disposition")

    # valid_interval, from markgarbage.m:55-58,93-95. `session_ID` is the
    # writer-vs-template divergence: ndi_timereference_struct returns it
    # (timereference.m:110) and NO NDI template has ever declared it, so an
    # undeclared it would be `undeclaredField` on every real document. It keeps its
    # CAMEL spelling because universalRenames snake_cases only a block's immediate
    # field names and this one is nested (universalRenames.m:302-347).
    vi = RECORDS["valid_interval"][1]
    assert {f["name"] for f in vi["fields"]} == {
        "timeref_structt0", "t0", "timeref_structt1", "t1"}
    for blk in ("timeref_structt0", "timeref_structt1"):
        subs = next(f for f in vi["fields"] if f["name"] == blk)["fields"]
        assert {s["name"] for s in subs} == {
            "referent_epochsetname", "referent_classname", "clocktypestring",
            "epoch", "session_ID", "time"}
        # NDI's clocktype vocabulary is NINE values (clocktype.m:69-71); the V_zeta
        # shape this replaces enumerated SIX, so approx_exp_global_time,
        # approx_dev_global_time and inherited would each have quarantined a real
        # document on a constraint DID invented. A tombstone enumerates nothing.
        ct = next(s for s in subs if s["name"] == "clocktypestring")
        assert ct["constraints"] == {}, \
            "a tombstone must not enumerate a vocabulary it cannot bound"


def test_timeseries_encoding_subtypes_dissolved():
    """2.D encoding-in-name slice: timeseries_data_{binary,csv,edf} were EMPTY
    subtypes whose only content was the FORMAT in the class name. The format is
    already carried by the dataseries_data ancestor's storage.format, so they
    dissolve; the timeseries_data parent (the series carrier) is retained."""
    for enc in ("timeseries_data_binary", "timeseries_data_csv", "timeseries_data_edf"):
        assert enc not in RECORDS


def test_dataseries_carrier_family_dissolved():
    """2.D slice C: the draft dataseries carrier family dissolves under Option 1 --
    header (axes/channels/storage) -> acquisition_epoch, payload -> sampled_body.
    content_hash is preserved onto sampled_body. zarr SURVIVES as the storage-recipe
    descriptor (load-bearing for directory's zarr_implicit manifest)."""
    for c in ("dataseries_data", "timeseries_data", "imageseries_data"):
        assert c not in RECORDS
    assert "zarr" in RECORDS  # kept: storage descriptor
    sampled_fields = {f["name"] for f in RECORDS["sampled_body"][1]["fields"]}
    assert "content_hash" in sampled_fields


def test_image_collection_dissolved_image_kept():
    """2.D slice D: image_collection (a bag of image files, created by nothing)
    dissolves schema-only (intended fold -> opaque_body). image itself STAYS --
    it is image_observation's geometry mixin."""
    assert "image_collection" not in RECORDS
    assert "image" in RECORDS
    assert "image" in _chain("image_observation")


def test_zarr_pyramid_orphans_dissolved():
    """2.D slice D: ephys_zarr / image_zarr / dataseries_pyramid are forward-looking
    subtypes with NO source (0 NDI refs, 0 migrators, no v1 doc def) -> 0 corpus
    presence -> dissolve schema-only. zarr STAYS (storage descriptor); pyraview
    STAYS (real NDI presence -> observation-tier fold with #9)."""
    for c in ("ephys_zarr", "image_zarr", "dataseries_pyramid"):
        assert c not in RECORDS
    assert "zarr" in RECORDS and "pyraview" in RECORDS


def test_data_type_value_is_body_backable():
    """§A.7/§A.9: a value's location is storage_mode (inline | body), not a class, so
    a data-type leaf (voltage_observation, ...) can be body-backed (value in a
    sampled_body). The composites' `value` must therefore NOT be unconditionally
    required -- otherwise a body-backed quantity observation quarantines on the empty
    inline value. Inline-requiredness is an ingest validator, not the meta-schema."""
    for comp in ("voltage", "frequency", "mass", "current", "temperature"):
        fields = {f["name"]: f for f in RECORDS[comp][1]["fields"]}
        assert fields["value"]["mustBeNonEmpty"] is False, comp


def test_phase1_source_cleanup_and_dep_typing():
    """Phase 1: dissolved source classes deleted (they have J dissolvers + no
    surviving referencer); and the surviving-infra deps get their now-settled
    targets (epochid -> acquisition_epoch on the ingested caches; directory
    nesting). openminds*/measurement are intentionally NOT deleted yet."""
    for gone in ("dataset_remote", "dataset_session_info", "session_in_a_dataset",
                 "metadata_editor"):
        assert gone not in RECORDS
    # still present (held): need migrators / entangled with #9
    assert "openminds" in RECORDS and "measurement" in RECORDS
    def _dep(cls, name):
        return next(d for d in RECORDS[cls][1]["depends_on"] if d["name"] == name)
    # `daqreader_epochdata_ingested` USED to be asserted here as carrying an
    # `epochid` DEPENDENCY typed to acquisition_epoch. It has none, and never did:
    # all three NDI ingest templates declare exactly ONE dependency, daqreader_id,
    # and `epochid` is a SUPERCLASS contributing a block that holds the epoch-id
    # STRING. This test was asserting the invented shape. See the correction in
    # V_eta_6_7_walkthrough_STATE.md.
    assert not any(d["name"] == "epochid"
                   for d in RECORDS["daqreader_epochdata_ingested"][1]["depends_on"]), \
        "did_v1 has no epochid dependency -- epochid is a superclass block"
    assert _dep("daqreader_epochdata_ingested", "daqreader_id") is not None
    # #60, INVERTED: this asserted that `epochfiles_ingested` carried an `epochid`
    # edge typed to acquisition_epoch. Both halves were wrong. NDI writes
    # `filenavigator_id` and V_eta had DROPPED it, declaring the invented `epochid`
    # REQUIRED instead -- empty on all 6,921 corpus documents. The class is now
    # `ingestion_manifest` (the old name encoded a MODE, the T13 error `_ndr` and
    # `_mfdaq` were de-encoded for) and carries the real edge plus an epoch edge.
    # AND INVERTED AGAIN, 2026-08-09, for the same reason one layer along: this
    # asserted the source class was GONE, which is what the build did -- it
    # deleted `epochfiles_ingested` the moment `ingestion_manifest` was minted.
    # Nothing migrates those documents yet (#60's migrator half), so every one
    # reached validation under a class with no schema: corpus B run #2, 2,484
    # quarantines, on a 0-quarantine gate. A test written from the same premise
    # as the code cannot catch the code. The tombstone stays until a migrator
    # provably consumes it, which is what _DELETE_PHASE8 exists to enforce and
    # what deleting the file directly bypassed.
    assert "epochfiles_ingested" in RECORDS, (
        "the v1 source tombstone must survive until #60's migrator consumes it -- "
        "deleting it quarantined 2,484 documents in corpus B")
    assert _dep("epochfiles_ingested", "filenavigator_id") is not None, \
        "the source tombstone must carry the edge NDI actually writes"
    assert "ingestion_manifest" in RECORDS
    assert _dep("ingestion_manifest", "filenavigator_id")["mustBeNonEmpty"] is True
    assert _dep("ingestion_manifest", "epoch_id")["must_refer_to_document_class"] == "epoch"
    assert not any(d["name"] == "epochid"
                   for d in RECORDS["ingestion_manifest"][1]["depends_on"])
    assert _dep("directory", "parent_directory_id")["must_refer_to_document_class"] == "directory"


def test_daqreader_ndr_de_encoded():
    """Chunk c: daqreader_ndr encoded a reader subtype in the CLASS NAME. It
    dissolves; its distinguishing fields de-encode onto the generic daqreader as
    OPTIONAL (the subtype is discriminated by ndi_daqreader_class), and the
    subtype-prefixed field name (ndr_reader_string) is dropped -> reader_string."""
    assert "daqreader_ndr" not in RECORDS
    dr = {f["name"]: f for f in RECORDS["daqreader"][1]["fields"]}
    assert dr.get("reader_string", {}).get("mustBeNonEmpty") is False
    # INVERTED 2026-08-10, not updated. This asserted that `file_extension` is
    # CARRIED onto daqreader -- the behaviour the signed daq-configuration
    # decision deletes ("the invented `file_extension` and `metadata_names` are
    # DELETED"). The test was written from the same premise as the code, so it
    # could only ever confirm it; the fix is to assert the opposite, the same way
    # the three `epochid` tests had to be inverted rather than edited.
    #
    # "Invented" is measured: across 1,002 .m files and every template/schema on
    # NDI origin/main, `file_extension` and `metadata_names` each have ZERO hits.
    # No real document carries either, so dropping the declaration cannot trip
    # `undeclaredField` -- and declaring a field no document has is the
    # wrong-assumed-shape defect that produced ~2,078 quarantines.
    assert "file_extension" not in dr, (
        "file_extension is deleted by the signed decision; it has 0 hits in NDI")
    assert "ndr_reader_string" not in dr and "ndi_daqreader_ndr_class" not in dr


def test_mfdaq_ingested_de_encoded():
    """Chunk c: daqreader_mfdaq_epochdata_ingested encoded the reader subtype
    (`mfdaq`) in its CLASS NAME. It dissolves onto the generic
    daqreader_epochdata_ingested -- its only distinguishing content, `parameters`,
    becomes an OPTIONAL field (empty for readers that do not slice by segment)."""
    assert "daqreader_mfdaq_epochdata_ingested" not in RECORDS
    dri = {f["name"]: f for f in RECORDS["daqreader_epochdata_ingested"][1]["fields"]}
    assert "parameters" in dri
    assert dri["parameters"].get("mustBeNonEmpty") is False


def test_ingested_caches_epochid_dep_only():
    """The epochdata_ingested caches stay device-layer ⑦ infra (NOT folded to
    sampled_body -- they carry no subject). That half of chunk (b) stands.

    THE OTHER HALF DID NOT. This test used to assert `epochid not in supers`,
    on the premise that "the epoch link is the inherited required epochid DEP".
    There is no such dependency in did_v1 -- `epochid` is a SUPERCLASS whose
    block holds the epoch-id STRING (`t00001`), set explicitly by both concrete
    writers. Dropping the mixin left the epoch identity with nowhere to land,
    and the same false premise shipped as an rmfield() in the mfdaq migrator
    that deleted it outright. The assertion is inverted here so the superclass
    is required, not forbidden."""
    img = RECORDS["daqreader_image_epochdata_ingested"][1]
    supers = {s.get("class_name") for s in img["document_class"]["superclasses"]}
    assert "epochid" in supers, \
        "epochid is a did_v1 superclass of the ingest caches, not a dependency"
    assert "daqreader_epochdata_ingested" in supers
    # the caches are NOT collapsed into the data_body genus
    assert "sampled_body" not in supers


def test_binding_is_formalized_in_meta_schema():
    """D9: the `binding` block is a validated property of `constraints`, not an
    advisory free-form key."""
    binding = META["$defs"]["field_definition"]["properties"]["constraints"] \
        .get("properties", {}).get("binding")
    assert binding is not None and binding["type"] == "object"
    # inline admissible-set spec: keyed_by / values / ontology+root_node (Q: the
    # separately-named value_set is dropped; source->ontology, root->root_node).
    assert "keyed_by" in binding["properties"] and "values" in binding["properties"]
    assert "ontology" in binding["properties"] and "root_node" in binding["properties"]
    assert "value_set" not in binding["properties"]
    assert "source" not in binding["properties"] and "root" not in binding["properties"]
    # controlled-vocabulary (openMINDS) binding: a directly-named term set
    assert {"vocabulary", "term_set", "vocabulary_version"} <= set(binding["properties"])


def test_openminds_controlled_term_fields_bound():
    """openMINDS controlled-term fields on dataset (accessibility / ethics_assessment /
    experimental_approach) are ontology_term-typed and carry an inline `binding` that
    names the openMINDS term set DIRECTLY (not keyed by a sibling `variable`). The
    (class, field) -> term_set mapping is cataloged in entity_field_bindings, and the
    referenced instance library is pinned once in controlled_vocabularies -- never
    copied inline as `values`."""
    ds = _load(os.path.join(VETA, "stable", "dataset.json"))
    fields = {f["name"]: f for f in ds["fields"]}
    reg = _load(os.path.join(VETA, "stable", "binding_registry_meta.json"))
    efb = {(r["class"], r["field"]): r for r in reg["entity_field_bindings"]}
    assert reg["controlled_vocabularies"]["openMINDS"]["iri_base"]
    expected = {
        "accessibility": ("ProductAccessibility", "required", True),
        "ethics_assessment": ("EthicsAssessment", "required", True),
        "experimental_approach": ("ExperimentalApproach", "preferred", False),
    }
    for name, (term_set, strength, closed) in expected.items():
        f = fields[name]
        assert f["type"] == "ontology_term", name
        b = f["constraints"]["binding"]
        assert b["vocabulary"] == "openMINDS" and b["term_set"] == term_set
        assert b["strength"] == strength
        assert "keyed_by" not in b and "values" not in b   # named directly, not copied
        row = efb[("dataset", name)]
        assert row["term_set"] == term_set and row["closed"] is closed
        assert row["strength"] == strength
    # experimental_approach is the open/growing set -> repeatable (list-valued)
    assert fields["experimental_approach"]["mustBeScalar"] is False


# openMINDS DatasetVersion property surface (openMINDS core, the release the crosswalk
# is authored against). The crosswalk must give EVERY one an explicit home so nothing
# is silently dropped -- that is the round-trip guarantee.
OPENMINDS_DATASETVERSION_PROPS = {
    "accessibility", "author", "copyright", "custodian", "description",
    "digitalIdentifier", "ethicsAssessment", "experimentalApproach",
    "fullDocumentation", "fullName", "funding", "homepage", "howToCite", "inputData",
    "isAlternativeVersionOf", "isNewVersionOf", "keyword", "license",
    "otherContribution", "protocol", "relatedPublication", "releaseDate", "repository",
    "shortName", "studiedSpecimen", "supportChannel", "type", "versionIdentifier",
    "versionInnovation",
}


def test_openminds_crosswalk_round_trips():
    """Round-trip guarantee: every openMINDS property has an EXPLICIT crosswalk entry
    whose target resolves to a real V_eta field / relation term / global_identifier --
    or is explicitly implied/projection/deferred (visible, never silently dropped).
    This is the enforcement point behind the openMINDS field parity."""
    xw = _load(os.path.join(REPO_ROOT, "schemas", "V_eta_openminds_crosswalk.json"))
    reg = _load(os.path.join(VETA, "stable", "binding_registry_meta.json"))
    relation_terms = {r["relation"]["name"] for r in reg["relation_bindings"]}

    # 1. completeness: the crosswalk covers the full DatasetVersion surface, exactly.
    dv = xw["types"]["DatasetVersion"]["properties"]
    assert set(dv) == OPENMINDS_DATASETVERSION_PROPS, (
        "crosswalk DatasetVersion drift: "
        f"missing={OPENMINDS_DATASETVERSION_PROPS - set(dv)} "
        f"extra={set(dv) - OPENMINDS_DATASETVERSION_PROPS}")

    # 2. no property is deferred -- every one has a concrete home (field / relation /
    #    global_identifier) or an explicit non-stored disposition (implied /
    #    projection). "deferred" (a designed-but-unbuilt home) is not allowed.
    for type_name, spec in xw["types"].items():
        for prop, e in spec["properties"].items():
            assert e["target_kind"] != "deferred", \
                f"{type_name}.{prop} is deferred -- give it a home"
    valid_kinds = {"field", "relation", "global_identifier", "implied", "projection"}
    for type_name, spec in xw["types"].items():
        entity_cls = spec["ndi_entity"]
        ent = _load(os.path.join(VETA, "stable", entity_cls + ".json"))
        field_names = {f["name"] for f in ent["fields"]}
        for prop, e in spec["properties"].items():
            kind = e["target_kind"]
            assert kind in valid_kinds, f"{type_name}.{prop}: bad kind {kind}"
            if kind == "field":
                assert e["ndi_target"] in field_names, \
                    f"{type_name}.{prop} -> field {e['ndi_target']} absent on {entity_cls}"
            elif kind == "relation":
                assert e["ndi_target"] in relation_terms, \
                    f"{type_name}.{prop} -> unknown relation term {e['ndi_target']}"
            elif kind in ("global_identifier", "implied", "projection", "deferred"):
                # explicit, non-silent: must carry a target or an explaining note.
                assert e.get("ndi_target") or e.get("notes"), \
                    f"{type_name}.{prop}: {kind} entry must be explained"

    # 3. every controlled-term field binding is reflected in the crosswalk as a field
    #    with the matching term_set (registry <-> crosswalk agreement).
    for row in reg["entity_field_bindings"]:
        props = xw["types"]["DatasetVersion"]["properties"]
        hit = [p for p, e in props.items()
               if e.get("ndi_target") == row["field"] and e.get("term_set")]
        assert hit, f"binding {row['field']} not crosswalked as a term field"
        assert props[hit[0]]["term_set"] == row["term_set"]


def test_software_crosswalks_to_openminds_softwareversion():
    """R1 kept the entity named `software` (not `software_version`) -- version is a
    field, not part of the name (T13). openMINDS parity is therefore a crosswalk-entry
    concern, and this is that entry."""
    xw = _load(os.path.join(REPO_ROOT, "schemas", "V_eta_openminds_crosswalk.json"))
    sv = xw["types"]["SoftwareVersion"]
    assert sv["ndi_entity"] == "software"
    props = sv["properties"]
    assert props["fullName"]["ndi_target"] == "name"
    assert props["versionIdentifier"]["ndi_target"] == "version"
    # the per-run environment is NOT on the entity: openMINDS operatingSystem /
    # programmingLanguage describe the software, ours describe the run, so they are
    # explicitly projections onto subject_interaction.execution_environment (R1).
    for prop in ("operatingSystem", "programmingLanguage"):
        assert props[prop]["target_kind"] == "projection"
        assert "execution_environment" in props[prop]["notes"]


def test_ndi_class_handles_marked_needs_ndi():
    """Governance sweep: each kept device/sync infra class that discriminates its
    implementation by an NDI-runtime class name flags that `ndi_<x>_class` field
    `needs_ndi` -- DID keeps the value for round-trip but cannot resolve the class
    (it lives in NDI-matlab). The marker is a declared, meta-schema-valid property."""
    assert "needs_ndi" in META["$defs"]["field_definition"]["properties"]
    expected = {
        "daqsystem": "ndi_daqsystem_class",
        "daqreader": "ndi_daqreader_class",
        "daqmetadatareader": "ndi_daqmetadatareader_class",
        "filenavigator": "ndi_filenavigator_class",
        "syncgraph": "ndi_syncgraph_class",
        "syncrule": "ndi_syncrule_class",
    }
    for cls, fname in expected.items():
        d = RECORDS[cls][1]
        f = next(f for f in d["fields"] if f["name"] == fname)
        assert f.get("needs_ndi") is True, f"{cls}.{fname} not marked needs_ndi"
    # every needs_ndi field is an ndi_<x>_class handle (no over-marking)
    for _tier, d in RECORDS.values():
        for f in d.get("fields", []):
            if f.get("needs_ndi"):
                assert f["name"].startswith("ndi_") and f["name"].endswith("_class")


def test_syncrule_mapping_epochnode_routed_through_time_reference():
    """Governance part 3: the sync epoch nodes state their clock time through the
    time_reference model -- each epochnode_* carries a `time_reference` sub-structure
    (epoch_bounded_reference shape: kind + epoch_clock + epoch_id), not bare
    epoch_clock/epoch_id char fields. epoch_id stays a name (epoch is not a doc), so
    it is an embedded reference, not a dep."""
    d = RECORDS["syncrule_mapping"][1]
    for node in ("epochnode_a", "epochnode_b"):
        f = next(f for f in d["fields"] if f["name"] == node)
        subs = {s["name"]: s for s in f["fields"]}
        # the bare clock fields are gone from the top level of the node
        assert "epoch_clock" not in subs and "epoch_id" not in subs
        tr = subs["time_reference"]
        assert tr["type"] == "structure"
        tr_subs = {s["name"] for s in tr["fields"]}
        assert {"kind", "epoch_clock", "epoch_id"} <= tr_subs
        # node metadata is retained
        assert {"epoch_session_id", "epochprobemap", "objectclass"} <= set(subs)
        # #58: objectname is READ BY A LIVE NDI QUERY (syncgraph.m:406-407) and was
        # dropped by this reshape; t0_t1 went with it. Both restored.
        assert {"objectname", "t0_t1"} <= set(subs)
    # #58, INVERTED: this test used to assert an `epochid` dependency existed and was
    # untyped "by design". There is no such dependency in did_v1 -- NDI's template AND
    # schema declare `syncgraph_id` + `syncrule_id`, both "mustbenotempty": 1 -- and it
    # was empty on all 5,316 corpus documents, one of the five invented-empty-edge rows.
    # The edge the live query actually reads is `syncgraph_id`.
    names = {x["name"] for x in d["depends_on"]}
    assert "epochid" not in names
    assert names == {"syncgraph_id", "syncrule_id"}
    assert all(x["mustBeNonEmpty"] for x in d["depends_on"])


def test_writer_set_dependencies_are_reported():
    """#54: the ground truth reports the dependency names NDI's WRITERS set, and
    which of them nothing declares -- the direction neither checker could see.

    `set_dependency_value` / `add_dependency_value_n` with 'ErrorIfNotFound', 0 APPEND
    an entry no schema declares (did/document.m:262-266), and the validator allows
    undeclared depends_on entries wholesale (+did2/+schema/cache.m:598). So an edge can
    exist in every real document, be declared nowhere, and be dropped in silence.

    THIS TEST WAS REWRITTEN 2026-08-09, and both halves of why matter.

    It used to assert that `openminds` appears in the undeclared list. That stopped
    being true for a GOOD reason -- the ground truth now reads NDI's schema documents
    as well as its templates, and `openminds_schema.json` declares the edge -- so the
    undeclared list is legitimately empty and the old assertion was pinning a defect
    in place.

    But an empty list is exactly what silentLoss taught us never to trust, so the
    guard moved to the DENOMINATOR. That was not theoretical: the sweep's regex
    required the dependency name as the SECOND argument, matching only the functional
    form `set_dependency_value(doc, 'name', id)`. NDI writes METHOD calls,
    `doc.set_dependency_value('name', id)`, so the scan found 5 call sites in 1,002
    files -- missing all five in tuning_response.m:323-328 and all three in
    system.m:489-497 -- and reported "0 undeclared", which read as a clean result. It
    was a property of the regex. Printing the denominator is what exposed it.

    So: zero undeclared is allowed and is the current answer. A scan that looked at
    almost nothing is not."""
    with open(os.path.join(REPO_ROOT, "schemas",
                           "V_eta_ndi_ground_truth.json")) as fh:
        gt = json.load(fh)
    assert "writer_dependencies" in gt, "the #54 sweep is missing from the ground truth"
    scan = gt["summary"].get("writer_dependency_scan")
    assert scan, "the sweep reports no denominator -- its zero cannot be believed"

    assert scan["m_files_scanned"] > 500, (
        f"only {scan['m_files_scanned']} .m file(s) scanned: "
        "the sweep is not reading NDI")
    assert scan["dependency_call_sites"] >= 100, (
        f"only {scan['dependency_call_sites']} dependency call site(s) found "
        f"across {scan['m_files_scanned']} files -- the previous regex found 5 "
        "here because it required the name as the SECOND argument, and NDI "
        "writes method calls")

    # Positive controls: edges we have READ in the writer with our own eyes, so a
    # future regex change that silently narrows the scan again fails here.
    written = set(scan["distinct_dependencies_written"])
    for name, site in (
            ("stimulus_response_scalar_parameters_id", "tuning_response.m:323"),
            ("stimulator_id", "tuning_response.m:328"),
            ("stimulus_control_id", "tuning_response.m:327"),
            ("daqmetadatareader_id", "system.m:496"),
            ("syncrule_id", "syncgraph.m:850"),
            ("openminds", "openMINDSobj2ndi_document.m")):
        assert name in written, (
            f"{name} is set at {site} and the sweep did not see it")

    for r in gt["writer_dependencies"]:
        assert r["writer_sites"], "a row with no call site is not evidence"


def test_method_parameters_is_the_inline_field_plus_an_identity():
    """#74: the settings document carries the SAME field name as the inline field,
    and no domain-specific fields at all.

    Three class names were rejected before this one, each for promising generality
    a domain-specific class cannot deliver. The resolution was that the typed knobs
    never belonged on a class -- they belong in the settings SHAPE, whose identity
    is a bound `variable`, exactly as the `axis` entry solves the same problem."""
    assert "method_parameters" in RECORDS
    d = RECORDS["method_parameters"][1]
    names = {f["name"] for f in d["fields"]}
    # the same name in both mount points -- `parameters` was vacated when the
    # statement's field became `conditions`
    assert "method_parameters" in names
    assert "parameters" not in names
    entry = next(f for f in d["fields"] if f["name"] == "method_parameters")
    assert entry["mustBeScalar"] is False, "the settings are a LIST of entries"
    subs = {s["name"] for s in entry["fields"]}
    assert {"variable", "value", "term", "text"} <= subs
    # identity is the bound variable; no unit field and no data_type field
    assert "unit" not in subs and "data_type" not in subs
    var = next(s for s in entry["fields"] if s["name"] == "variable")
    assert var["type"] == "ontology_term"
    # no domain fields leaked onto the class
    assert not ({"threshold", "refractory_period", "waveform_window"} & names)
    deps = {x["name"]: x for x in d["depends_on"]}
    assert set(deps) == {"software_id", "subject_id", "epoch_id", "derived_from_id"}
    # the self-edge is lineage, and points at its own class
    assert deps["derived_from_id"]["must_refer_to_document_class"] == "method_parameters"
    assert deps["derived_from_id"]["mustBeNonEmpty"] is False


def test_settings_edge_is_on_the_interaction_branch_only():
    """#74: only `subject_interaction` gets the edge. The assertion branch is
    timeless and methodless -- "this animal is of strain PR811" has no algorithm --
    so 30 assertion leaves must NOT inherit it."""
    assert "method_parameters_id" in _flat_dep_names("subject_interaction")
    assert "method_parameters_id" in _flat_dep_names("voltage_observation")
    assert "method_parameters_id" not in _flat_dep_names("subject_assertion")
    assert "method_parameters_id" not in _flat_dep_names("term_assertion")
    # and it stays optional: a run with unnamed knobs uses the inline field
    dep = next(x for x in RECORDS["subject_interaction"][1]["depends_on"]
               if x["name"] == "method_parameters_id")
    assert dep["mustBeNonEmpty"] is False


def test_strain_is_an_entity_with_a_recursive_pedigree():
    """#56: `strain` is an ENTITY, not a plain document, and its pedigree is a
    recursive self-edge.

    `entity` was chosen for `global_identifier` -- a REPEATABLE {scheme, value}
    that subsumes openMINDS's three separate identifier slots and the four schemes
    in our data (WBStrain, NCIT, RRID, EMPTY). A shared background strain is then
    stored ONCE and referenced, which a nested background block would have
    duplicated into every descendant."""
    assert "strain" in RECORDS
    _tier, d = RECORDS["strain"]
    assert [s["class_name"] for s in d["document_class"]["superclasses"]] == ["entity"]
    ft = _flat_field_types("strain")
    # global_identifier comes from entity and must stay OPTIONAL: Dabrowska's Cre
    # lines carry no identifier at all, and a schema must not demand what the
    # writer never produces.
    gi = next(f for f in RECORDS["entity"][1]["fields"] if f["name"] == "global_identifier")
    assert gi["mustBeNonEmpty"] is False
    assert gi["mustBeScalar"] is False, "global_identifier must be repeatable"
    # required BY openMINDS, not by us
    for required in ("name", "species", "genetic_strain_type"):
        f = next(x for x in d["fields"] if x["name"] == required)
        assert f["mustBeNonEmpty"] is True, f"{required} must be required"
    assert ft.get("species") == "ontology_term"
    bg = next(x for x in d["depends_on"] if x["name"] == "background_strain_#")
    assert bg["must_refer_to_document_class"] == "strain", "the pedigree is recursive"
    assert bg["min_count"] == 0 and bg["max_count"] == 2


def test_term_assertion_keeps_its_inline_value_and_gains_strain_id():
    """#56: the assertion carries BOTH the inline term value and an optional edge.

    That is not the general rule -- `epoch` drops its inline string entirely in
    favour of its edge. The difference is the drift test: dropping strain's inline
    value would make `variable: strain` resolve two ways depending on whether a
    pedigree document happened to exist. 115 strains carry no identifier and may
    warrant no document at all."""
    deps = {x["name"]: x for x in RECORDS["term_assertion"][1].get("depends_on", [])}
    assert "strain_id" in deps
    assert deps["strain_id"]["mustBeNonEmpty"] is False, (
        "a strain document is optional -- the assertion must stand alone")
    assert deps["strain_id"]["must_refer_to_document_class"] == "strain"
    # the inline value survives: term_assertion still inherits `term`'s value
    assert "term" in _chain("term_assertion")


def test_numbered_edge_families_declare_cardinality():
    """#63: a `name_#` family declares min_count/max_count, and never claims
    `mustBeNonEmpty`.

    `mustBeNonEmpty` cannot describe a family -- a MISSING instance is not a blank
    one, and `silentLoss.requiredDependencies` excludes numbered edges for exactly
    that reason. Three families were nonetheless declared required and verified by
    nothing. The count is the checkable fact, so it is the one that gets declared;
    leaving the old flag set would keep two flags disagreeing about one thing."""
    fams = []
    for name, (_tier, d) in RECORDS.items():
        for dep in d.get("depends_on", []):
            if dep["name"].endswith("_#"):
                fams.append((name, dep))
    assert fams, "no numbered edge families found -- the sweep is broken"
    for cls, dep in fams:
        assert "min_count" in dep, f"{cls}.{dep['name']} declares no min_count"
        assert dep["mustBeNonEmpty"] is False, (
            f"{cls}.{dep['name']} still claims mustBeNonEmpty, which cannot "
            "describe a family")
        if "max_count" in dep:
            assert dep["max_count"] >= max(dep["min_count"], 1)
    # the spine and the purpose edge are the two that must be PRESENT
    required = {(c, d["name"]) for c, d in fams if d["min_count"] >= 1}
    assert ("subject_interaction", "time_reference_#") in required
    assert ("interaction_purpose", "interaction_id_#") in required
    # NDI's own schema says syncrule_id_# may be empty -- V_eta had tightened it
    sg = next(d for c, d in fams if c == "syncgraph" and d["name"] == "syncrule_id_#")
    assert sg["min_count"] == 0


def test_data_body_carrier_dispositions():
    """2.D collapse: data_body has EXACTLY 2 members; the format/series carriers are
    folded/placed. `image` is KEPT (image_observation's geometry mixin, so it must
    persist); zarr (orphaned descriptor) and pyraview (folds with #9) are leaving."""
    bodies = {r[1]["document_class"]["class_name"]
              for r in RECORDS.values()
              if "data_body" in {s["class_name"]
                                 for s in r[1]["document_class"].get("superclasses", [])}}
    assert bodies == {"sampled_body", "opaque_body"}
    disp = {e["class_name"]: e.get("disposition") for e in INDEX["schemas"]}
    # image is KEPT (image_observation's geometry mixin) but its final ⑥/⑦
    # disposition is not settled, so it is in_progress -- crucially NOT retire (that
    # was the bug: retiring the mixin of a persisting leaf).
    assert disp["image"] != "retire", "image is a kept geometry mixin, not retiring"
    assert disp["image_observation"] == "persist"
    assert disp["zarr"] == "retire" and disp["pyraview"] == "retire"
    # a persisting class never has a RETIRING superclass (the image bug: a kept
    # class whose mixin was marked retire). in_progress supers are fine -- they are
    # kept infra whose ⑥/⑦ disposition is just not finalized.
    for _tier, d in RECORDS.values():
        if disp.get(d["document_class"]["class_name"]) == "persist":
            for s in d["document_class"].get("superclasses", []):
                assert disp.get(s["class_name"], "persist") != "retire", \
                    f"{d['document_class']['class_name']} persists but super " \
                    f"{s['class_name']} is retiring"


def test_no_revived_classes_in_migrators():
    """Guardrail (tools/coverage.py): every class_name a V_eta migrator EMITS must
    exist in the built schema (or the tracked known-non-V_eta allow-list). Catches
    reviving a dead class / inventing a non-existent one -- the stimulus_manipulation
    / bath error class -- in <1s. Skips when the sibling migrator repos are absent."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "coverage_tool", os.path.join(REPO_ROOT, "tools", "coverage.py"))
    cov = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cov)
    emitted = cov.emitted_classes()
    if not emitted:
        pytest.skip("migrator sibling repos not checked out")
    new, _ack = cov.guardrail(cov.veta_index(), emitted)
    assert not new, f"migrators emit classes absent from the V_eta schema: {new}"


def test_visual_grating_manipulation_leaf():
    """A presented visual stimulus is a body-backable subject_manipulation leaf whose
    data type is a structured multi-parameter `visual_grating` composite (a grating
    is orientation + spatial/temporal freq + contrast at once, so not a single-quantity
    leaf). stimulus_presentation folds to this on the animal in the second pass."""
    comp = RECORDS["visual_grating"][1]
    assert "data_type" in _chain("visual_grating")
    val = next(f for f in comp["fields"] if f["name"] == "value")
    subs = {s["name"] for s in val["fields"]}
    assert {"angle", "spatial_frequency", "temporal_frequency", "contrast",
            "size", "position", "duration", "is_blank"} <= subs
    leaf = RECORDS["visual_grating_manipulation"][1]
    supers = {s["class_name"] for s in leaf["document_class"]["superclasses"]}
    assert supers == {"subject_manipulation", "visual_grating"}


def test_openminds_import_is_absent():
    """openminds_import was REMOVED 2026-07-30 by team sign-off, reversing the earlier
    "PERSIST as (7) provenance" call.

    INVERTED, not deleted. This test previously asserted the class existed and that
    the registry's openMINDS `version` stayed null because the import-provenance
    document was "the single source of truth" it resolved from. Both halves needed
    reversing together: nothing ever emitted the class -- zero documents, no
    migrator, no importer, not even the round-trip test -- so the "source of truth"
    resolved nothing, and the null was not deferral, it was absence.

    Asserting the ABSENCE keeps the reversal honest: if the class comes back, it
    comes back with an emitter and a decision, not by accident.
    """
    assert "openminds_import" not in RECORDS, (
        "openminds_import was removed by team decision; re-adding it needs an "
        "import path that actually stamps it (see V_eta_tenet_audit.md)")
    reg = _load(os.path.join(VETA, "stable", "binding_registry_meta.json"))
    om = reg["controlled_vocabularies"]["openMINDS"]
    assert om["version"] is None
    # the note must not promise resolution from a class that no longer exists
    assert "UNRESOLVED" in om["notes"], (
        "the registry still claims the openMINDS version is resolved elsewhere")


def _leaf_ok(concrete, cls):
    """A binding `class` must be a concrete (non-abstract) subject_statement leaf."""
    dc = concrete.get(cls)
    return dc is not None and not dc.get("abstract", False)


def test_binding_registry_meta_present():
    """D9: the binding registry ships with the subject_defining bindings (the kind
    ingestion invariant) folded into subject_statement_bindings as a flagged
    subset, not a separate kind_variables list."""
    reg = _load(os.path.join(VETA, "stable", "binding_registry_meta.json"))
    # the old separate lists are gone -- folded into subject_statement_bindings
    assert "kind_variables" not in reg and "subject_kind_variables" not in reg
    ssb = reg["subject_statement_bindings"]
    defining = [b for b in ssb if b.get("subject_defining")]
    names = {b["variable"]["name"] for b in defining}
    assert {"species", "instrument type", "cell type"} <= names
    # each subject_defining row is a term_assertion drawing from an ontology subtree
    for b in defining:
        assert b["class"] == "term_assertion"
        assert b.get("ontology") and b.get("root_node")
    in_index = {e["class_name"]: e for e in INDEX["schemas"]}
    assert in_index["binding_registry_meta"].get("is_meta") is True


def test_binding_examples_well_formed():
    """binding_examples is a SEPARATE block (never mistaken for swept data). Each
    row carries a NodeRef `variable` and a concrete subject_statement leaf `class`;
    no `data_type` (the leaf fixes the type). A term-valued leaf pins an admissible
    set (values | ontology+root_node) -- with `values` given as NodeRefs, not bare
    strings -- and a dimensional leaf carries none."""
    reg = _load(os.path.join(VETA, "stable", "binding_registry_meta.json"))
    assert "bindings" not in reg  # renamed -> subject_statement_bindings
    concrete = {r[1]["document_class"]["class_name"]: r[1]["document_class"]
                for r in RECORDS.values()}
    # every real binding AND every example must name a concrete leaf, no data_type
    for b in reg["subject_statement_bindings"] + reg["binding_examples"]:
        assert set(b["variable"]) >= {"node", "name"}
        assert _leaf_ok(concrete, b["class"]), f"{b['class']} must be a concrete leaf"
        assert "data_type" not in b, "the leaf class replaces data_type"
        if "method" in b:
            assert set(b["method"]) >= {"node", "name"}
    forms = set()
    for b in reg["binding_examples"]:
        has_vals = "values" in b
        has_sub = "ontology" in b and "root_node" in b
        if b["class"].startswith("term_"):
            assert has_vals ^ has_sub, f"term leaf needs one set spec: {b}"
            forms.add("values" if has_vals else "subtree")
            if has_vals:  # values are ontology-term NodeRefs, not bare strings
                assert all(isinstance(v, dict) and {"node", "name"} <= set(v)
                           for v in b["values"]), f"values must be NodeRefs: {b}"
        else:
            assert not has_vals and not has_sub, \
                f"dimensional leaf {b['class']} needs no spec"
    # both term-set forms demonstrated, plus at least one method+variable row
    assert forms == {"values", "subtree"}
    assert any("method" in b for b in reg["binding_examples"])


def test_relation_bindings_present():
    """D6: the binding registry enumerates the admissible directed/undirected
    relation terms — the single source of truth for `directed_relation.relation`
    values (subject-side + entity-side), each pinned to its carrier `class` with
    typed `from`/`to` endpoints."""
    reg = _load(os.path.join(VETA, "stable", "binding_registry_meta.json"))
    assert "relation_vocabulary" not in reg  # renamed -> relation_bindings
    vocab = {r["relation"]["name"]: r for r in reg["relation_bindings"]}
    # the subject-side terms the migrators already emit + the new entity-layer terms
    for term in ("part_of", "member_of", "derived_from", "observes", "encountered",
                 "has_author", "funded_by", "issued_by", "affiliated_with", "cites",
                 "documented_by", "stored_at", "hosted_by",
                 # openMINDS crosswalk-parity terms (deferred -> minted)
                 "has_custodian", "contributed_by", "copyright_holder",
                 "alternative_of", "input_data", "has_homepage", "follows_protocol",
                 "suborganization_of"):
        assert term in vocab, f"{term} missing from relation_bindings"
    # term identity is a {node, name} NodeRef, mirroring variable/method.
    assert all({"node", "name"} <= set(r["relation"]) for r in vocab.values())
    # directed endpoints are child/parent, matching the schema directed_relation
    # child/parent deps (not the old advisory `category`).
    assert all({"relation", "class", "child_types", "parent_types"} <= set(r)
               for r in vocab.values())
    assert all(r["class"] in ("directed_relation", "undirected_relation")
               for r in vocab.values())
    # every current term is directed (undirected/member_types reserved but unused)
    assert all(r["class"] == "directed_relation" for r in vocab.values())
    assert all("member_types" not in r for r in vocab.values())
    assert vocab["part_of"]["relation"]["node"] == "BFO:0000050"
    # every endpoint type is a real class OR an abstract genus (entity/subject)
    known = {r[1]["document_class"]["class_name"] for r in RECORDS.values()}
    for r in vocab.values():
        for t in r["child_types"] + r["parent_types"]:
            assert t in known, f"{r['relation']['name']} endpoint {t} unknown"
    # member_of retargets to subject (a group is a subject; subject_group is gone)
    assert vocab["member_of"]["parent_types"] == ["subject"]
    # entity-layer endpoint types match what the migrators mint
    assert vocab["has_author"]["child_types"] == ["dataset"]
    assert vocab["has_author"]["parent_types"] == ["person"]


# ------------------------------------------------- value-cell convention conformance
# Every `data_type` composite exposes its payload at ONE predictable slot, `value`.
# That is what makes T3's `direction x data_type` factoring mechanical: `mass.value`
# means the same under mass_observation and mass_assertion. The rule was unwritten for
# most of the project's life and two classes silently drifted off it, so it is a test
# now rather than a convention.
# Empty: every data_type composite conforms. (contrast_sensitivity was the last
# exception -- its flat v1 bag is now reshaped onto a `value` cell with a model_fit
# array. Keep this set empty; a new entry needs a recorded reason and an exit plan.)
_VALUE_SLOT_EXCEPTIONS = set()


def _data_type_composites():
    for name, (tier, d) in RECORDS.items():
        chain = [s["class_name"] for s in d["document_class"].get("superclasses", [])]
        if "data_type" in chain:
            yield name, d


def test_data_type_composites_expose_one_value_slot():
    offenders = {}
    for name, d in _data_type_composites():
        if name in _VALUE_SLOT_EXCEPTIONS:
            continue
        names = [f["name"] for f in d.get("fields", [])]
        if names != ["value"]:
            offenders[name] = names
    assert not offenders, (
        "data_type composites must expose exactly one payload field named "
        f"`value` (descriptors ride INSIDE the cell, beside the payload): {offenders!r}")


def test_value_slot_exceptions_are_still_real():
    # Guard the guard: if an exception has been fixed, it must leave this set, so the
    # allowlist cannot quietly outlive the problem it documents.
    for name in _VALUE_SLOT_EXCEPTIONS:
        assert name in RECORDS, f"{name} is no longer a class; drop it from the allowlist"
        names = [f["name"] for f in RECORDS[name][1].get("fields", [])]
        assert names != ["value"], (
            f"{name} now conforms — remove it from _VALUE_SLOT_EXCEPTIONS")


def test_named_composite_cells_declare_their_layout():
    # A named composite type must declare its sub-fields inline: a type that is only an
    # enum string is undeclared, and undeclared internals are an opaque blob to the
    # validator, the query-path generator and the viewer alike.
    named = set(META["$defs"]["field_definition"]["properties"]["type"]["enum"]) - {
        "did_uid", "char", "string", "integer", "double", "matrix", "timestamp",
        "boolean", "structure"}
    missing = []

    def walk(cls, fields, prefix):
        for f in fields or []:
            path = f"{prefix}.{f['name']}"
            if f["type"] in named and not f.get("fields"):
                missing.append(f"{cls}:{path} (type {f['type']})")
            walk(cls, f.get("fields"), path)

    for name, (tier, d) in RECORDS.items():
        walk(name, d.get("fields"), name)
    assert not missing, (
        f"named composite cells missing declared sub_fields: {missing[:20]!r}")


def test_dimensioned_cells_carry_source_provenance():
    # Every dimensioned cell keeps the raw input losslessly beside the canonical, so a
    # unit conversion is never destructive. (count/score/ontology_term are the
    # documented exceptions: a count has no dimensional scaling, a score is
    # scale-relative, a term is an identity.)
    exempt = {"count", "score", "ontology_term"}
    bad = []
    for name, (tier, d) in RECORDS.items():
        for f in d.get("fields", []):
            t = f["type"]
            if t in exempt or not f.get("fields"):
                continue
            subs = {sf["name"] for sf in f["fields"]}
            if ("source_unit" in subs or "source_value" in subs) and not {
                    "source_unit", "source_value", "approximate"} <= subs:
                bad.append(f"{name}.{f['name']} ({t}): {sorted(subs)}")
    assert not bad, f"dimensioned cells missing the source triple: {bad!r}"


def test_no_new_duplicate_field_declarations_in_a_chain():
    # #69's cheap interim, asserted here as well as in CI so a local run catches it.
    #
    # A subclass that redeclares an ancestor's field creates TWO live storage
    # locations for one fact and nothing says which wins. It is invisible by
    # construction: resolvePlacement's collision check fires only within one
    # targetBlock, and the default placement puts ancestor and descendant in
    # DIFFERENT blocks, so the redeclaration never trips it -- and a cross-block
    # duplicate name is checked nowhere else either.
    #
    # A RATCHET, not a zero. Six of the nine known rows are V1 FIDELITY: NDI's
    # own templates declare a class-block `name` beside `base.name`, and a
    # tombstone that dropped it would stop matching the writer. See the evidence
    # quoted in tools/check_duplicate_field_declarations.py.
    # LOADED BY PATH, not imported. `tools/` has no __init__.py and the package
    # is installed with `pip install -e .`, so `import tools.x` resolves locally
    # (cwd on sys.path) and raises ModuleNotFoundError in CI. Running only
    # `pytest tests/test_veta.py` locally hid it; CI runs the whole suite.
    mod = _load_tool("check_duplicate_field_declarations")

    classes = mod.load_classes()
    assert classes, "no V_eta classes were read -- the check would pass vacuously"
    rows = mod.find_duplicates(classes)
    assert len(rows) <= mod.BASELINE, (
        f"new duplicate field declaration(s): {[(c, f, o) for c, f, o in rows][:20]!r}")
    assert len(rows) == mod.BASELINE, (
        f"BASELINE is stale ({len(rows)} found, baseline {mod.BASELINE}) -- "
        "lower it so the ratchet keeps the ground it won")


def test_no_signed_plan_document_claims_to_be_unsigned():
    # A plan document's sign-off is APPENDED AT THE BOTTOM; the reader's summary
    # of its state is at the TOP; nothing kept the two in agreement. Six documents
    # ended up asserting "NO `TEAM-SIGN-OFF` LINE" while carrying that line
    # hundreds of lines below, and the clock-alignment cluster sat unbuilt for a
    # day because of it. The status board never saw the problem -- it reads the
    # signature, not the prose -- so nothing existed that could have caught this.
    #
    # Asserted here as well as in CI so a local run catches it before a push.
    mod = _load_tool("check_signoff_header_staleness")

    import glob as _glob
    import os as _os
    paths = _glob.glob(_os.path.join(mod.SCHEMA_DIR, "*.md"))
    rows, read, signed = mod.scan(paths)
    # DENOMINATORS, asserted rather than printed: a glob that matched nothing,
    # or a corpus of plan documents that somehow carried no signatures at all,
    # would make "0 stale" true and meaningless.
    assert read > 0, "no schemas/*.md files were read -- the check is vacuous"
    assert signed > 0, (
        "no plan document carries a TEAM-SIGN-OFF line -- either the marker "
        "changed shape or the glob is wrong; either way this check is vacuous")
    assert not rows, (
        "signed plan document(s) asserting they are unsigned: "
        f"{[(mod.os.path.basename(p), n) for p, n, _ in rows]!r}")


def test_ndi_schema_documents_are_all_read():
    """The ground truth reads NDI's SCHEMA documents, not just its templates -- and
    says how many, in what shape, and how many it could not parse.

    THREE WAYS THIS SWEEP SILENTLY READ NOTHING, all found on 2026-08-09:

    1. It did not read schema_documents at all. A dependency can be declared in the
       schema and NOT in the template -- `syncgraph.json` has `depends_on: []` while
       `syncgraph_schema.json` declares `syncrule_id` -- so V_eta was reported as
       inventing an edge it had declared correctly.

    2. Schema documents key the class as `classname`, not the template's
       `document_class.class_name`. Reading the template spelling matched nothing
       and returned a clean empty dict.

    3. FIVE of the 89 files are JSON Schema draft 2019-09, not the flat shape, with
       dependency names as `const` under properties.depends_on.items[]. They are the
       whole `vhlab_voltage2firingrate` family -- whose WRITER is in no repository we
       have, so this schema is the only ground truth that exists for it. Skipping
       them made `binnedspikeratevm.sorting_parameters_id` read as a DID invention.

    And two files are not valid JSON at all: `"parameters": [-Inf,Inf,0]` is MATLAB,
    not JSON, so a strict parse threw away both files INCLUDING their well-formed
    depends_on blocks. One of them is `valid_interval`, an UNVERIFIED coverage row.
    """
    with open(os.path.join(REPO_ROOT, "schemas",
                           "V_eta_ndi_ground_truth.json")) as fh:
        gt = json.load(fh)
    scan = gt["summary"].get("ndi_schema_document_scan")
    assert scan, "no denominator for the schema-document sweep"
    assert scan["files"] > 80, (
        f"only {scan['files']} schema document(s) read -- "
        "the sweep is not finding NDI's set")
    assert scan["json_schema_form"] >= 5, (
        "the JSON Schema-shaped documents are being skipped again "
        f"({scan['json_schema_form']} found)")
    assert scan["unparseable"] == 0, (
        f"{scan['unparseable']} schema document(s) could not be parsed; the "
        "MATLAB -Inf fallback has stopped working or NDI has a new malformation")

    classes = gt["classes"]
    # positive controls, one per failure mode above
    assert "syncrule_id" in classes["syncgraph"]["depends_on"], \
        "schema-only dependency lost: syncgraph declares syncrule_id in its schema"
    assert "sorting_parameters_id" in classes["binnedspikeratevm"]["depends_on"], \
        "JSON Schema-shaped document lost: binnedspikeratevm declares this"
    assert "element_id" in classes["valid_interval"]["depends_on"], \
        "the -Inf fallback is not working: valid_interval_schema.json declares this"


# ---------------------------------------------------------------------------
# The decision families artifact (schemas/V_eta_decisions.json).
#
# WHY IT IS TESTED HERE. The board's own staleness check proves the file is
# REGENERATED; these prove it is USABLE -- that the viewer's join key exists,
# that a family cannot claim a class twice, and above all that "signed" is
# never asserted without a sign-off line. That last one is the whole point of
# the artifact: it now carries a `signed: true` flag into a UI, so a bug that
# set it wrongly would launder a proposal into a decision on a screen, one step
# further from the plan document than the board ever was.
# ---------------------------------------------------------------------------

DECISIONS = os.path.join(REPO_ROOT, "schemas", "V_eta_decisions.json")


def _decisions():
    with open(DECISIONS) as fh:
        return json.load(fh)


def test_decisions_artifact_exists_and_covers_every_open_class():
    dec = _decisions()
    with open(os.path.join(REPO_ROOT, "schemas", "V_eta", "index.json")) as fh:
        idx = json.load(fh)
    open_classes = {s["class_name"] for s in idx["schemas"]
                    if s.get("disposition") == "in_progress"}
    claimed = set(dec["by_class"])
    missing = sorted(open_classes - claimed)
    assert not missing, (
        f"in_progress classes claimed by no decision family: {missing}. An open "
        "class nobody tracks is the failure the status board exists to prevent.")
    # The denominator, asserted rather than assumed: the artifact must agree
    # with the index it was generated from.
    assert dec["summary"]["open_classes"] == len(open_classes)


def test_no_class_is_claimed_by_two_families():
    dec = _decisions()
    seen = {}
    for fam in dec["families"]:
        for m in fam["members"]:
            name = m["class_name"]
            assert name not in seen, (
                f"{name} is claimed by both {seen[name]} and {fam['name']}; two "
                "families owning one class means two places to decide it.")
            seen[name] = fam["name"]


def test_signed_is_never_asserted_without_a_signoff_line():
    for fam in _decisions()["families"]:
        if fam["signed"]:
            assert fam["status"] == "team", (
                f"{fam['name']} is marked signed but its status is "
                f"{fam['status']!r} -- only a team decision can be signed.")
            assert fam["signoff"], (
                f"{fam['name']} claims signed with no sign-off text")
            assert fam["state"] == "signed_awaiting_build"
        else:
            assert fam["state"] != "signed_awaiting_build"
            assert not fam["signoff"]


def test_every_family_plan_document_exists():
    fams = _decisions()["families"]
    assert fams, "no decision families -- this sweep would check nothing"
    for fam in fams:
        if fam["plan"]:
            path = os.path.join(REPO_ROOT, "schemas", fam["plan"])
            assert os.path.exists(path), (
                f"{fam['name']} cites {fam['plan']}, which does not exist -- the "
                "viewer renders that path as the place the decision is recorded.")


def test_the_viewer_actually_syncs_the_decisions_artifact():
    # A generated artifact nobody copies into the app is a file that changes
    # nothing. The coverage ledger had this wiring; the decisions did not, and
    # the deploy workflow's path filter needed the same explicit line because
    # `schemas/V_*/**` does not match a file sitting directly under schemas/.
    with open(os.path.join(REPO_ROOT, "web", "scripts", "sync-schemas.mjs")) as fh:
        sync = fh.read()
    assert "V_eta_decisions.json" in sync
    assert "decisions.json" in sync
    with open(os.path.join(
            REPO_ROOT, ".github", "workflows", "deploy-web.yml")) as fh:
        deploy = fh.read()
    assert "V_*_decisions.json" in deploy, (
        "deploy-web.yml will not redeploy when the decisions change")


def test_target_source_distinguishes_emitted_from_passthrough():
    """The ledger must not assert `X -> X` for a class no migrator touches.

    The fallback used to be `targets = [vname]` with the comment
    "passthrough/rename: same-name class is the target" -- an ASSERTION wearing
    the clothes of an observation. 34 of 102 rows had no curated entry, and 15
    of those carry a SIGNED decision naming a DIFFERENT target, so the ledger
    was quietly contradicting the plan documents. Same shape as the old
    "dissolved (rename/decompose)" label on 32 rows: a default that reads as a
    finding.
    """
    with open(os.path.join(REPO_ROOT, "schemas",
                           "V_eta_coverage_ledger.json")) as fh:
        rows = json.load(fh)["rows"]
    assert rows, "empty ledger -- the sweep is broken"
    for r in rows:
        assert r["target_source"] in (
            "emitted", "decided", "uncurated", "passthrough", "unknown"), (
            f"{r['v1_class']} has target_source {r['target_source']!r}")
        # a passthrough names exactly the same-name class and nothing else
        if r["target_source"] == "passthrough":
            assert r["targets"] == [r["veta_class"]], (
                f"{r['v1_class']} is a passthrough but names targets "
                f"{r['targets']} rather than its own V_eta class")
            assert not r["migrator"], (
                f"{r['v1_class']} has a migrator yet is labelled a passthrough. "
                "A migrator with no curated entry is `uncurated`, not a "
                "passthrough -- this exact case (control_stimulus_ids) is what "
                "caught the first draft of this split.")
    # The denominator, so a sweep that silently stopped classifying is visible.
    kinds = {k: sum(1 for r in rows if r["target_source"] == k)
             for k in ("emitted", "decided", "uncurated", "passthrough", "unknown")}
    # This equality is the denominator, and it EARNED its keep on 2026-08-10:
    # adding the `decided` state moved 31 rows out of the four names listed here,
    # and the sum caught it immediately -- 71 != 102 -- where the per-row
    # membership assertion above had already been widened and passed. A tally
    # that only counts the states it knows about would have reported a clean
    # sweep over two thirds of the ledger.
    assert sum(kinds.values()) == len(rows), (
        "%d rows classified out of %d -- a state is missing from this tally"
        % (sum(kinds.values()), len(rows)))
    assert kinds["emitted"] > 0 and kinds["passthrough"] > 0


def test_no_passthrough_row_claims_a_migrator_emits_it():
    """Every curated (`emitted`) row must really have a migrator or a second pass.

    Catches the inverse mistake: marking a row emitted because a decision says
    so, which would make the ledger claim a migration nobody wrote -- the mirror
    of the bug this split fixes, and the reason the decided target is NOT
    written into the curated map.

    IT FIRED FOR REAL on 2026-08-10, when 28 per-class accounts were written for
    classes whose families are signed but unbuilt. Merely ADDING a curated entry
    flipped each row to `emitted` -- exactly the false claim above, since no
    migrator produces any of them. The fix was not to relax this assertion but to
    give coverage.py a fifth state, `decided`, for an entry that records a signed
    disposition while claiming no emission. This test still holds `emitted` to its
    full meaning; the sibling below holds `decided` to its own.
    """
    with open(os.path.join(REPO_ROOT, "schemas",
                           "V_eta_coverage_ledger.json")) as fh:
        rows = json.load(fh)["rows"]
    assert sum(1 for r in rows if r["target_source"] == "emitted") > 0, (
        "no emitted rows -- this sweep would check nothing")
    for r in rows:
        if r["target_source"] == "emitted":
            assert r["migrator"] or r["second_pass"] or r["carried"], (
                f"{r['v1_class']} is marked emitted but no migrator, second "
                "pass or carried class backs it")


def test_decided_rows_record_a_disposition_without_claiming_a_migration():
    """`decided` means signed-and-unbuilt, and must not drift into either neighbour.

    Two ways the state could rot, so both are asserted. It must not absorb rows a
    migrator DOES implement -- that is `emitted`, and keeping them apart is the
    entire point. And it must not become a bucket for rows with no recorded
    account -- that is `passthrough` or `unknown`; every `decided` row has to
    carry the prose that justifies the label.
    """
    with open(os.path.join(REPO_ROOT, "schemas",
                           "V_eta_coverage_ledger.json")) as fh:
        rows = json.load(fh)["rows"]
    decided = [r for r in rows if r["target_source"] == "decided"]
    assert decided, "no decided rows -- this sweep would check nothing"
    for r in decided:
        assert not r["targets"], (
            f"{r['v1_class']} is `decided` but names emitted targets -- if a "
            "migrator produces them the row is `emitted`")
        assert (r.get("how") or "").strip(), (
            f"{r['v1_class']} is `decided` with no `how` -- the label claims an "
            "account exists, so one must")


def test_uncurated_stays_at_zero():
    """RATCHET at 0: every migrator must have a curated target entry.

    `uncurated` means a migrator runs and nothing records what it emits. All
    five that existed (control_stimulus_ids, image, measurement,
    kilosort_clusters, kiasort_clusters) were closed by reading the migrators,
    so the honest guard is now that the count cannot climb back up -- adding a
    migrator without a curated row is a deliberate act that has to move this
    baseline.

    A RATCHET RATHER THAN THE PROPERTY TEST IT REPLACES. That test asserted
    "every uncurated row has a migrator" and, at zero rows, passed while
    checking nothing -- indistinguishable from a test that verified something.
    Same defect as a census reporting 0 while reading no documents.
    """
    with open(os.path.join(REPO_ROOT, "schemas",
                           "V_eta_coverage_ledger.json")) as fh:
        rows = json.load(fh)["rows"]
    unc = sorted(r["v1_class"] for r in rows if r["target_source"] == "uncurated")
    assert unc == [], (
        f"{len(unc)} migrator(s) with no entry in V_eta_migration_targets.json: "
        f"{unc}. The ledger cannot say what they emit, so it says nothing -- add "
        "the row by READING THE MIGRATOR, never by copying what a plan intends.")
    # the denominator, so a sweep that silently stopped classifying is visible
    assert len(rows) > 0 and any(r["target_source"] == "emitted" for r in rows)


# ---------------------------------------------------------------------------
# #32 binding governance, increment 1 (team decision 2026-08-10: "preferred
# first, strength on the field", then "C for now" -- strength only, no
# admissible set named yet).
# ---------------------------------------------------------------------------

_PIVOT_BINDINGS = [
    ("subject_statement", "variable"),
    ("subject_interaction", "method"),
    ("interaction_purpose", "purpose"),
]


def test_the_three_pivot_fields_are_bound_at_preferred():
    """`term.value` resolves keyed_by `variable`, so the key deciding what every
    term value may be must itself be governed. All three carried
    `constraints = {}` until this landed."""
    for cls, fname in _PIVOT_BINDINGS:
        _tier, d = RECORDS[cls]
        hit = [f for f in d["fields"] if f["name"] == fname]
        assert hit, f"{cls} declares no field {fname!r}"
        b = (hit[0].get("constraints") or {}).get("binding")
        assert b, f"{cls}.{fname} carries no binding"
        assert b["strength"] == "preferred", (
            f"{cls}.{fname} is {b['strength']!r}. `required` is the INTENDED end "
            "state but must not be set until a corpus has measured how many real "
            "documents would fail it -- flipping blind on a 0-quarantine gate is "
            "what produced 2,484 corpus-B quarantines.")


def test_the_pivot_bindings_name_no_admissible_set_yet():
    """Option C, deliberately: strength only.

    The meta-schema offers exactly two ways to name an admissible set -- an
    ontology subtree (`ontology` + `root_node`) or a static `values`
    enumeration -- and neither is decided for these fields. The registry's
    subject_statement_bindings answer a DIFFERENT question (given
    variable = species, what may the VALUE be). Asserting the absence keeps a
    later guess from arriving silently: adding a root node is a decision, and
    this test makes it one that has to be taken deliberately.
    """
    for cls, fname in _PIVOT_BINDINGS:
        _tier, d = RECORDS[cls]
        fld = next(f for f in d["fields"] if f["name"] == fname)
        b = fld["constraints"]["binding"]
        assert set(b) == {"strength"}, (
            f"{cls}.{fname} binding grew keys {sorted(set(b) - {'strength'})}. "
            "Naming an admissible set is a separate decision (option A or B).")


def test_field_and_registry_strengths_agree():
    """Strength is authoritative ON THE FIELD (team, 2026-08-10) -- and three
    facts are nonetheless stored twice.

    dataset.accessibility / ethics_assessment / experimental_approach state
    their strength both in the field constraint and in the registry's
    entity_field_bindings. They agree today, but nothing checked them against
    each other, so they agreed by coincidence. This makes it by construction.
    """
    # NOT in RECORDS: the registry is a meta file with no `document_class`, so
    # it is not a schema record. Load it by path.
    with open(os.path.join(VETA, "stable", "binding_registry_meta.json")) as fh:
        reg = json.load(fh)
    efb = {(r["class"], r["field"]): r.get("strength")
           for r in reg["entity_field_bindings"]}
    assert efb, "no entity_field_bindings rows -- this check would verify nothing"
    checked = 0
    for (cls, fname), reg_strength in efb.items():
        _t, d = RECORDS[cls]
        hit = [f for f in d["fields"] if f["name"] == fname]
        assert hit, f"registry names {cls}.{fname}, which the schema does not declare"
        b = (hit[0].get("constraints") or {}).get("binding") or {}
        assert b.get("strength") == reg_strength, (
            f"{cls}.{fname}: field says {b.get('strength')!r}, registry says "
            f"{reg_strength!r}. The FIELD is authoritative; update the registry "
            "row to match, or drop it.")
        checked += 1
    assert checked == len(efb)


# ---------------------------------------------------------------------------
# #67 -- the did_clocktype vocabulary: 9 NDI clocktypes -> 4 staged ontology terms
# ---------------------------------------------------------------------------
#
# GROUND TRUTH, and it is NOT derived from anything on the DID side. Read from
# NDI-matlab origin/main:
#
#   $ git show origin/main:src/ndi/+ndi/+time/clocktype.m
#     switch type
#       case {'utc','approx_utc','exp_global_time','approx_exp_global_time',...
#             'dev_global_time', 'approx_dev_global_time', 'dev_local_time', ...
#             'no_time','inherited'}
#
# Transcribed here because CI does not have NDI-matlab checked out;
# test_ndi_clocktype_transcription_matches_ndi re-reads the real file and fails
# loudly whenever the repo IS present, so this constant cannot rot unnoticed.
NDI_CLOCKTYPES = {
    "utc", "approx_utc", "exp_global_time", "approx_exp_global_time",
    "dev_global_time", "approx_dev_global_time", "dev_local_time",
    "no_time", "inherited",
}

# The FOUR the signed walkthrough keeps (V_eta_time_reference_model_plan.md:468,
# TEAM-SIGN-OFF [time_reference] 2026-08-08, CHANGE 3 + CHANGE 4).
DID_CLOCKTYPE_TERMS = ["utc", "dev_local_time", "dev_global_time", "exp_global_time"]

# Every field that carries the vocabulary. Gate 1 of the clock-alignment sign-off
# says clock_alignment_configuration.clock "must use the same four" as the time
# model -- so both are listed and the test compares them to each other, not each
# to a separate expectation.
_CLOCKTYPE_FIELDS = [
    ("relative_reference", ("value", "clock")),
    ("clock_alignment_configuration", ("clock",)),
]


def _field_at(record, path):
    fields = record["fields"]
    node = None
    for name in path:
        hit = [f for f in fields if f["name"] == name]
        assert hit, f"no field {name!r} in {[f['name'] for f in fields]}"
        node = hit[0]
        fields = node.get("fields", [])
    return node


def test_did_clocktype_partitions_ndi_nine():
    """The four kept terms are a real subset of NDI's nine, and the five dropped
    ones are dropped for the reasons the sign-off gives -- not by accident.

    This is the check that a test written from the build script's own premise
    would miss: it starts from NDI's list, not from ours.
    """
    kept = set(DID_CLOCKTYPE_TERMS)
    assert len(DID_CLOCKTYPE_TERMS) == 4, DID_CLOCKTYPE_TERMS
    assert kept <= NDI_CLOCKTYPES, sorted(kept - NDI_CLOCKTYPES)
    dropped = NDI_CLOCKTYPES - kept
    assert dropped == {
        # CHANGE 4: the approx_ prefix de-encodes to time_reference.clock_tolerance
        # { seconds: 5 }. It must NOT fold into a boolean -- the five seconds would
        # be lost.
        "approx_utc", "approx_exp_global_time", "approx_dev_global_time",
        # CHANGE 4: an epoch_clock asserting "this thing keeps no time". V_eta's
        # translation is NO TIMES => NO REFERENCE: no document, not a value.
        "no_time",
        # CHANGE 4: a resolution instruction; `relative_to` already IS that
        # pointer and can name WHICH device. Recorded in the plan as an
        # ABSENCE-BASED call awaiting a corpus check, so it is left UNMINTED
        # rather than declared nonexistent.
        "inherited",
    }, sorted(dropped)


def test_ndi_clocktype_transcription_matches_ndi():
    """Re-read NDI's own clocktype.m when the repo is present, so NDI_CLOCKTYPES
    above cannot silently drift from the source it claims to quote.

    SKIPPED in CI (no NDI-matlab checkout). That is a real limitation, stated
    rather than papered over: in CI the constant is a transcription and nothing
    more.
    """
    import re
    import subprocess
    ndi = os.environ.get("NDI_MATLAB_PATH", "/home/user/NDI-matlab")
    if not os.path.isdir(os.path.join(ndi, ".git")):
        pytest.skip(f"NDI-matlab not checked out at {ndi}")
    try:
        src = subprocess.run(
            ["git", "show", "origin/main:src/ndi/+ndi/+time/clocktype.m"],
            cwd=ndi, capture_output=True, text=True, check=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        pytest.skip(f"cannot read clocktype.m from origin/main: {exc}")
    # the `case {...}` list inside setclocktype() is the authority: the docstring
    # tables are prose and could disagree with the code.
    m = re.search(r"case \{('.*?')\}\s*\n", src, re.DOTALL)
    assert m, "clocktype.m no longer has a `case {...}` validity list -- re-read it"
    found = set(re.findall(r"'([a-z_]+)'", m.group(1)))
    assert found == NDI_CLOCKTYPES, (
        f"NDI_CLOCKTYPES is stale. clocktype.m now validates {sorted(found)}; "
        f"the constant says {sorted(NDI_CLOCKTYPES)}")


def test_clock_fields_are_ontology_terms_bound_to_the_same_four():
    """#67 CHANGE 3: `clock` is an ontology_term, not a bare char -- `relation`
    beside it already is one and `variable` is one everywhere.

    Both carriers share ONE binding, which is what gate 1 of the clock-alignment
    sign-off actually asks for; asserting each against its own copy of the list
    would let them drift apart while both tests stayed green.
    """
    seen = []
    for cls, path in _CLOCKTYPE_FIELDS:
        assert cls in RECORDS, f"{cls} is not in the built schema set"
        _tier, d = RECORDS[cls]
        fld = _field_at(d, path)
        where = cls + "." + ".".join(path)
        assert fld["type"] == "ontology_term", f"{where} is {fld['type']!r}"
        # the named-type expansion must have given it the {node, name} cell
        assert [f["name"] for f in fld.get("fields", [])] == ["node", "name"], where
        assert fld["blank_value"] == {"node": "", "name": ""}, where
        b = fld["constraints"]["binding"]
        assert b["root"] == "did_clocktype", where
        assert b["strength"] == "required", where
        # values are NodeRefs, not bare strings -- the field is a {node, name}
        # cell, so a bare "utc" cannot say which half it is. Same rule the
        # registry already states (test_binding_examples_well_formed).
        assert [v["name"] for v in b["values"]] == DID_CLOCKTYPE_TERMS, where
        assert all(set(v) == {"node", "name"} for v in b["values"]), where
        # maxLength was a char-cell constraint and has no meaning on a NodeRef
        assert "maxLength" not in fld["constraints"], where
        seen.append(b)
    assert len(seen) == len(_CLOCKTYPE_FIELDS) == 2
    assert seen[0] == seen[1], (
        "the two did_clocktype carriers have diverged; gate 1 of the "
        "clock-alignment sign-off requires the SAME four")


def test_clocktype_nodes_are_staged_empty_not_invented():
    """The four nodes are EMPTY, deliberately.

    An NDI-side CURIE would be `NDIC:<identifier>` (NDI writes
    ['NDIC:' int2str(item.Identifier)] in +setup/+conv/+marder/
    temptable2stimulusparameters.m:25 and +setup/+stimulus/+vhlab/
    add_stimulus_approach.m:51). The table those identifiers come from,
    ndi_common/controlled_vocabulary/NDIC.txt, was removed from NDI-matlab in
    commit 2c19bf24c ("moved to ndi-ontology-matlab") and its last in-tree
    revision holds no clock terms. So there is no authority in scope that can
    assign one, and an invented integer would be a fabricated CURIE.

    This test exists so that when the nodes ARE minted, the minting is a
    deliberate edit with a real source -- not a value that appeared.
    """
    checked = 0
    for cls, path in _CLOCKTYPE_FIELDS:
        _tier, d = RECORDS[cls]
        b = _field_at(d, path)["constraints"]["binding"]
        assert len(b["values"]) == 4, cls
        assert all(v["node"] == "" for v in b["values"]), (
            f"{cls}: a clocktype node was filled in. If a real NDIC CURIE was "
            "assigned, update this test and cite the source; do not invent one.")
        checked += len(b["values"])
    assert checked == 8, (
        f"expected 8 staged nodes (4 terms x 2 carriers); inspected {checked}")


def test_retiring_epoch_clock_fields_untouched_by_67():
    """#67 does NOT touch the eight retiring reference classes.

    Increment 1 of the time-reference collapse is ADDITIVE ONLY: the v1-era
    classes stay until the migrators move, and 24 files still emit
    session_relative_reference. Their `epoch_clock` keeps NDI's full nine and
    stays a char, because that is what the emitters write today. Narrowing it
    here would quarantine live documents -- the epochfiles_ingested regression.
    """
    checked = 0
    for cls in ("epoch_bounded_reference", "epoch_relative_reference"):
        if cls not in RECORDS:          # gone once increment 3 lands
            continue
        _tier, d = RECORDS[cls]
        fld = _field_at(d, ("epoch_clock",))
        assert fld["type"] == "char", cls
        b = fld["constraints"]["binding"]
        assert set(b["values"]) == NDI_CLOCKTYPES, (
            f"{cls}.epoch_clock no longer carries NDI's nine: {sorted(b['values'])}")
        checked += 1
    assert checked == 2, (
        f"expected both retiring reference classes; found {checked}. If increment "
        "3 deleted them, delete this test with it.")


def test_no_list_valued_field_is_typed_char():
    """A `char` field that is not scalar CANNOT validate, so it must not exist.

    +did2/+schema/cache.m:965-970 accepts only a char array or a SCALAR string
    for `char`; the `string` branch (cache.m:971-1001) is the one written to
    accept the cell-of-chars MATLAB's jsondecode produces from a JSON array. So
    `type: char` + `mustBeScalar: false` is a contradiction the schema can state
    and the validator can only reject -- every real multi-valued document
    quarantines on `did2:validation:typeMismatch`.

    THREE FIELDS HELD THIS SHAPE until 2026-08-10 -- `epoch_file_pattern`'s two
    pattern lists and `strain.synonym` -- and none had been exercised, because no
    migrator emitted any of them yet. It was found by an agent writing the
    filenavigator fold, which would have been the first thing to hit it.

    A ZERO, not a ratchet: there is no legitimate instance of this combination.
    """
    bad = []

    def walk(cls, fields, prefix=""):
        for f in fields:
            if f.get("type") == "char" and f.get("mustBeScalar") is False:
                bad.append((cls, prefix + f["name"]))
            for sub in f.get("fields") or []:
                walk(cls, [sub], prefix + f["name"] + ".")

    seen = 0
    for cls, (_tier, body) in RECORDS.items():
        seen += 1
        walk(cls, body.get("fields", []))
    assert seen > 0, "no classes read -- this sweep would pass vacuously"
    assert not bad, (
        "list-valued fields typed `char` cannot validate; use `string`: %r" % (bad,))


def test_ngrid_tombstone_is_the_did_v1_shape_and_carries_coordinates():
    """#46 gate 2, made EXECUTABLE. The `ngrid` tombstone is restated from the
    WRITER, and nothing in Python asserted it until now.

    The schema half of that repair (build_v_eta.py) and the migrator half
    (DID-matlab +migrators_j/+super/ngrid.m) are LOCKSTEP -- either alone
    quarantines every consumer -- but the migrator half is covered only by
    `tests/+did2/+unittest/testNgridCoordinates.m`, which has NEVER RUN (there is
    no MATLAB in the container it was written in). So until this test the entire
    repair had zero executable coverage, and a re-introduction of the invented
    names would have gone green.

    did_v1 GROUND TRUTH, NDI origin/main @ 42c94e5 (read 2026-08-10):

        database_documents/data/ngrid.json
            "ngrid": {data_size, data_type, data_dim, coordinates}
            superclasses [base];  NO depends_on;  NO files
        schema_documents/data/ngrid_schema.json  -- the same four, typed
        the ONLY writer: +ndi/+fun/+data/mat2ngrid.m, which sets exactly those four

    `ndims` and `dim_sizes` are the V_DELTA MIGRATOR'S OUTPUT, not v1 fields;
    `dim_labels`, the `element_id` dep and `ngrid_file` appear in no NDI template,
    schema or writer. V_eta declared all five, with `ndims` REQUIRED -- so a real
    document quarantined on that alone.

    `coordinates` is asserted PRESENT, not landed. Its decided destination is
    `axes[k].values` (V_eta_image_model_plan.md, TEAM-SIGN-OFF 2026-08-08), which
    belongs to the data_body tier (#45, blocked on #32). Asserting a home would
    assert a build that has not happened; asserting the CARRY is what stops the
    silent deletion coming back.
    """
    assert "ngrid" in RECORDS, (
        "#46 is NOT retirement-ready: both consumers are unfolded, so the "
        "tombstone must survive -- see test_ngrid_may_not_be_retired_while_consumers_exist")
    tier, d = RECORDS["ngrid"]
    fields = {f["name"]: f for f in d.get("fields", [])}
    assert set(fields) == {"data_size", "data_type", "data_dim", "coordinates"}, (
        "the tombstone must declare the four did_v1 names and nothing else; got %r"
        % (sorted(fields),))
    # the V_delta migrator's output, and the three downstream inventions
    for invented in ("ndims", "dim_sizes", "dim_labels"):
        assert invented not in fields, (
            "%s has no did_v1 existence -- it is V_delta output or a downstream "
            "invention, and declaring it (REQUIRED, for ndims) quarantines every "
            "real document" % invented)
    assert d.get("depends_on") == [], "did_v1 ngrid declares no dependencies"
    assert d.get("file") == [], (
        "did_v1 ngrid declares no file of its own -- the CONSUMER does "
        "(`ontologyImage.ngrid` in ontologyImage.json's file_list)")
    assert [s["class_name"] for s in d["document_class"]["superclasses"]] == ["base"]


def test_ngrid_may_not_be_retired_while_consumers_exist():
    """#46's GATE, made mechanical instead of remembered.

    `ngrid` retirement is gated on BOTH consumers, and the record has already
    been wrong about that once: build_v_eta.py called `reverse_correlation`
    "its only consumer", which is the sentence V_eta_ngrid_family_findings.md F4
    says made `ngrid` look like a one-class item when it is not.

    Deleting a source tombstone whose documents still arrive is not hypothetical
    damage: it is the `epochfiles_ingested` regression, 2,484 quarantines in
    corpus B on a 0-quarantine gate, caused by a rename that bypassed
    `_DELETE_PHASE8` by removing the file directly. This test closes the same
    door for `ngrid` -- whichever way a future build removes it.

    The gate is derived from the BUILT SET, so it cannot go stale the way the
    comment did: if any V_eta class still declares `ngrid` a superclass, those
    documents reach validation carrying an `ngrid` block, and a missing tombstone
    means `undeclaredField` on every one of them.
    """
    consumers = sorted(
        name for name, (_t, body) in RECORDS.items()
        if any(s.get("class_name") == "ngrid"
               for s in body["document_class"]["superclasses"]))
    # DENOMINATOR FIRST. Without it this passes when RECORDS is empty.
    assert len(RECORDS) > 200, f"only {len(RECORDS)} schemas loaded"
    if "ngrid" not in RECORDS:
        assert not consumers, (
            "`ngrid` was retired while %d class(es) still declare it a superclass "
            "(%s). Retirement is gated on BOTH consumers (#46): ontology_image "
            "(#47) and hartley_calc via reverse_correlation (#48). Fold them "
            "first, or every passthrough quarantines on undeclaredField."
            % (len(consumers), ", ".join(consumers)))
        return
    # Today: the gate is CLOSED, and this records who is holding it shut, so a
    # reader does not have to take the prose's word for the count.
    assert consumers == ["ontology_image", "reverse_correlation"], (
        "the ngrid consumer set changed: %r. Re-derive #46's gate before acting "
        "-- `hartley_calc` reaches ngrid through reverse_correlation, so the "
        "chain is hartley_calc -> hartley_reverse_correlation -> "
        "reverse_correlation -> ngrid." % (consumers,))
