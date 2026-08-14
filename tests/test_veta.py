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
import contextlib
import glob
import io
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


def test_local_identifier_required_on_subject_and_session_optional_elsewhere():
    """local_identifier is a schema-enforced handle: REQUIRED where the handle is
    how people name the thing, OPTIONAL on every other entity, and NOT declared on
    the abstract `entity` parent (so a child *adds* a required field rather than
    illegally overriding a parent-optional one). Requiredness is expressed by
    placement, like the timing model — not an ingest convention.

    `session` MOVED FROM THE OPTIONAL LIST TO THE REQUIRED ONE on 2026-08-13, and
    the move is a rename, not a new obligation. It used to carry BOTH an optional
    `local_identifier` and a required-in-practice `reference` — one slot spelled
    two ways, which is exactly the drift the naming tenets exist to prevent. The
    signed change deletes the optional slot and renames `reference` into it:

        TEAM-SIGN-OFF [session]: jess@walthamdatascience.com / 2026-08-13
          "session.reference becomes local_identifier, required, matching
           subject and epoch."

    Every did_v1 session document carries the value already (NDI's own template
    declares `session.reference` and nothing else), so requiring it quarantines
    nothing that was previously valid.
    """
    # the parent stays neutral (no local_identifier -> no forbidden override)
    assert _local_id("entity") is None
    # the handle is the name: required
    for e in ("subject", "session"):
        f = _local_id(e)
        assert f is not None, f"{e} should carry a required local_identifier"
        assert f["mustBeNonEmpty"] is True, f"{e}.local_identifier must be required"
    # every other entity carries it, optional
    for e in ("dataset", "person", "organization", "publication", "funding",
              "web_resource"):
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
            f"{name} has no V_eta schema; a document of this class reaches validation "
            "as an undeclared class and is lost")
        assert disp[name] == "retire", (
            f"{name} is a v1 SOURCE tombstone, never a go-forward class")

    # generic_file, from +setup/+conv/+babu/import.m:526-531 and :575-580 --
    # all five fields, the file, and the document_id edge.
    gf = RECORDS["generic_file"][1]
    assert {f["name"] for f in gf["fields"]} == {
        "filename", "format_ontology", "checksum", "date_created", "date_updated"}
    assert [f["name"] for f in gf["file"]] == ["generic_file.ext"]
    assert [d["name"] for d in gf["depends_on"]] == ["document_id"]

    # THE FIELD THAT BLOCKED THE FOLD, NOW INVERTED. This assertion read
    #
    #     assert "content_hash" not in ...opaque_body fields...
    #         "opaque_body gained content_hash -- the fold is no longer blocked
    #          on it; re-open the disposition"
    #
    # and it did exactly the job it was written for: the team re-opened the
    # disposition on 2026-08-11 and chose option (a), so opaque_body gained
    # content_hash and the fold was built. INVERTED, NOT DELETED -- a test
    # written from the same premise as the code cannot catch the code, and this
    # one was written from the premise that the fold is blocked. Deleting it
    # would leave nothing asserting the checksum has somewhere to land; the
    # three `epochid` tests were inverted for the same reason.
    assert "checksum" in {f["name"] for f in gf["fields"]}
    assert "content_hash" in {f["name"] for f in RECORDS["opaque_body"][1]["fields"]}, \
        ("opaque_body LOST content_hash -- the generic_file -> opaque_body fold "
         "(did2.convert.foldGenericFiles) drops the MD5 ndi.fun.file.MD5 "
         "computes, which is the one field whose whole purpose is not to be lost")
    ch = next(f for f in RECORDS["opaque_body"][1]["fields"]
              if f["name"] == "content_hash")
    assert ch["mustBeNonEmpty"] is False, (
        "content_hash is optional on the SIGNED data_body model; requiring it "
        "would quarantine every opaque_body minted from a source that computes "
        "no hash (jSorterOutput's external sorter directories, for one)")
    # ONLY the one field. The rest of the #45 data_body tier is a separate,
    # larger, deferred item and parts of it are blocked on #32 -- so `format`,
    # `filename` and `description` must still be on the CHILD, not hoisted, and
    # `compression` must still be absent. If `compression` ever appears without
    # content_hash's documentation saying which byte stream it covers, that is
    # the plan's own open question 3 going unanswered.
    ob_fields = {f["name"] for f in RECORDS["opaque_body"][1]["fields"]}
    assert "compression" not in ob_fields, (
        "opaque_body gained `compression` -- then content_hash must state "
        "whether it hashes the compressed or the decompressed bytes "
        "(V_eta_data_body_model_plan.md, open question 3)")
    assert {"format", "filename", "description"} <= ob_fields
    assert not RECORDS["data_body"][1]["fields"], (
        "the data_body hoist (#45) has started -- it is blocked on #32 and is "
        "not what the generic_file fold was authorised to build")

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


def test_image_collection_is_a_tombstone_not_a_dissolution():
    """INVERTED 2026-08-11, not updated -- the old assertion WAS the old premise.

    This test read `assert "image_collection" not in RECORDS`, and it passed for
    as long as it did because it was written from the same belief as the build
    comment it guarded: that nothing creates the class, so nothing can strand.
    A test written from the code's own premise cannot catch the code. Team
    decision 2026-08-11: give it a v1-shaped tombstone, because a class no
    in-tree writer produces is exactly the one that arrives from a dataset
    nobody has migrated yet, and with no schema such a document quarantines.

    `image` itself is UNAFFECTED and is asserted alongside, so that a build which
    deleted the wrong one of the two would fail here rather than half-pass.
    """
    assert "image_collection" in RECORDS, (
        "image_collection is a did_v1 SOURCE class with an NDI template and no "
        "migrator; deleting its schema is the stranding case")
    assert "image" in RECORDS
    assert "image" in _chain("image_observation")


def test_image_collection_tombstone_matches_the_ndi_ground_truth_artifact():
    """Denominator-first, and BOTH directions -- the image_stack lesson.

    `image_stack`'s restatement got NDI's deps and fields right and then declared
    a file NDI does not write while leaving the file it does write undeclared:
    both directions of the audit at once, on every passed-through document. So
    this compares by EQUALITY, not by subset. A tombstone that declares more than
    NDI does is a `did2:validation:undeclaredField` waiting to happen from the
    other side -- and for this class the surplus is not hypothetical, since the
    V_alpha snapshot it was carried in on (schemas/V_alpha/imageCollection.json)
    declares FIVE names NDI has never had: `element_id`, `collection_file`,
    `num_images`, `image_format`, `description`.

    The generated artifact is the authority; this test is prose about it.
    """
    # KEYED BY NDI'S OWN SPELLING. The artifact is an extract of NDI, so its keys
    # are camelCase; V_eta is snake_case. Looking this up as `image_collection`
    # would be the `demo_ndi` failure -- a lookup that cannot match, reported as
    # an absence.
    gt = _ndi_ground_truth()["classes"]["imageCollection"]
    rec = RECORDS["image_collection"][1]

    # denominator, stated before any verdict
    assert (len(gt["depends_on"]), len(gt["fields"]), len(gt["files"])) == (1, 2, 0), (
        f'the NDI ground truth for imageCollection changed shape ({len(gt["depends_on"])} dep(s), {len(gt["fields"])} field(s), {len(gt["files"])} file(s)) -- re-read the template before trusting this')

    ours_deps = {d["name"] for d in rec["depends_on"]}
    ours_fields = {f["name"] for f in rec["fields"]}
    ours_files = {f["name"] for f in rec.get("file", [])}
    ours_supers = [s["class_name"] for s in rec["document_class"]["superclasses"]]

    assert ours_deps == set(gt["depends_on"]), (
        "depends_on diverges from NDI: missing {!r}, invented {!r}".format(sorted(set(gt["depends_on"]) - ours_deps),
           sorted(ours_deps - set(gt["depends_on"]))))
    assert ours_fields == set(gt["fields"]), (
        "fields diverge from NDI: missing {!r}, invented {!r}".format(sorted(set(gt["fields"]) - ours_fields),
           sorted(ours_fields - set(gt["fields"]))))
    assert ours_supers == gt["superclasses"], (
        "superclass chain diverges from NDI: {!r} vs {!r}".format(ours_supers, gt["superclasses"]))

    # THE FILE BLOCK, asserted separately from the sets above because it is the
    # one part universalRenames carries through VERBATIM (skip = {'document_class',
    # 'depends_on', 'file', 'files'}, DID-matlab +did2/+convert/universalRenames.m:308)
    # and `did2.validate.fileList` compares it by exact strcmp. NDI declares NO
    # file for this class; V_zeta declared `collection_file`.
    assert ours_files == set(gt["files"]) == set(), (
        f"NDI's imageCollection declares no file; this tombstone declares {sorted(ours_files)!r}. A "
        "file name is did_v1 spelling carried through verbatim -- declaring one "
        "no document has is the image_stack defect repeated.")


def test_image_collection_tombstone_requires_nothing():
    """A tombstone must not quarantine the documents it exists to preserve.

    There is NO WRITER for this class anywhere in NDI (0 of 1002 .m files on
    origin/main, all three spellings), so nothing establishes that any field is
    reliably populated -- and NDI's own schema marks the single dependency
    `mustbenotempty: 0`. Requiring anything here would be inventing a guarantee
    from a template, which is the wrong-assumed-shape failure that produced the
    ~2,078 distance_metadata quarantines.
    """
    rec = RECORDS["image_collection"][1]
    req_deps = [d["name"] for d in rec["depends_on"] if d.get("mustBeNonEmpty")]
    req_fields = [f["name"] for f in rec["fields"] if f.get("mustBeNonEmpty")]
    assert not req_deps and not req_fields, (
        f"required with no writer to justify it -- deps {req_deps!r}, fields {req_fields!r}")


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
    # `directory` USED to be asserted here as carrying a self-referential
    # `parent_directory_id` typed to itself. The team DELETED the class on
    # 2026-08-11 (build_v_eta.py `_DELETE_NO_V1_PROVENANCE`, where the
    # measurement behind the call is recorded): provenance V_gamma, never a
    # did_v1 class, nothing subclassed it, nothing depended on it, nothing
    # minted or consumed it, and its three distinctive field names appeared in
    # no code anywhere.
    #
    # INVERTED rather than deleted. Asserting the class is GONE keeps this line
    # doing work: a `directory.json` reappearing -- from a stray copytree, a
    # revert, or a V_gamma import -- would otherwise pass unnoticed, and the
    # edge it declares points at itself, so nothing else would catch it either.
    assert "directory" not in RECORDS, (
        "`directory` is back in the built set; it was deleted by team decision "
        "2026-08-11 and nothing should be reintroducing it")


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
    # #32 increment 2: the lexical-shape key. Declared with a CLOSED enum -- one
    # member -- because a `node_form` the validator does not recognise is
    # tolerated at runtime (an old validator must not invent a verdict about a
    # newer rule), so an unknown value would otherwise be accepted in silence at
    # BOTH ends and enforce nothing anywhere.
    assert binding["properties"]["node_form"] == {"type": "string",
                                                  "enum": ["curie"]}


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
    # `date` joins the PRIMITIVE set 2026-08-13, beside `timestamp`. It is a
    # scalar string (the validator accepts it on the char branch), so it has no
    # internals to declare and is not the kind of thing this test is about --
    # which is named COMPOSITE cells whose layout would otherwise be opaque.
    named = set(META["$defs"]["field_definition"]["properties"]["type"]["enum"]) - {
        "did_uid", "char", "string", "integer", "double", "matrix", "timestamp",
        "date", "boolean", "structure"}
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
    # AND THE AXIS ENTRY, which hoists the triple RATHER THAN DROPPING IT
    # (2026-08-14, AMENDMENT 1 + 2 to the data_body plan). An axis carries
    # `unit`, `source_unit` and `approximate` at the TOP of the entry, shared by
    # whichever value form it uses, and the per-slot `origin`/`spacing`/`values`
    # then carry `value` + `source_value`. Splitting the triple across two levels
    # is the POINT -- one axis has one unit and one approximate flag, and
    # `jMeasureArray` proves the per-element copies were always identical:
    # `m(k) = struct('source_unit', char(unit), ..., 'approximate', false)`.
    # `conditions` is the same shape for the same reason (AMENDMENT 2).
    hoisted = {("sampled_body", "axes"), ("subject_statement", "axes")}
    bad = []
    for name, (tier, d) in RECORDS.items():
        for f in d.get("fields", []):
            t = f["type"]
            if t in exempt or not f.get("fields"):
                continue
            if (name, f["name"]) in hoisted:
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
    # A RATCHET, not a zero. Most rows are V1 FIDELITY: NDI's own templates
    # declare a class-block `name` beside `base.name`, and a tombstone that
    # dropped it would stop matching the writer. The fidelity split is DERIVED
    # from schemas/V_eta_ndi_ground_truth.json -- see the tests below, and the
    # tool's docstring for why the hand list it replaced had to go.
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


def test_duplicate_field_fidelity_split_is_derived_from_the_ground_truth():
    """The V1-FIDELITY split must come from NDI, not from a list beside it.

    THE HAND LIST DRIFTED, in the direction that costs documents: the module
    docstring said "six of the nine rows are V1 FIDELITY" and named
    `stimulus_parameter.name` as the sixth while the set held five and omitted
    it, so a field NDI's own schema declares was filed under "no template forces
    this -- OPEN: which block is authoritative?". Acting on that bucket means
    dropping the field from a PURE PASSTHROUGH tombstone, which leaves it
    undeclared on every real document and quarantines all of them.

    So this asserts the property the list could not have: every V1-FIDELITY
    verdict is RE-DERIVED here, straight out of the ground truth artifact, by
    code that shares nothing with the tool's classifier but the artifact itself.
    """
    mod = _load_tool("check_duplicate_field_declarations")

    classes = mod.load_classes()
    gt_index, gt_stats = mod.load_ground_truth()
    # DENOMINATORS, asserted rather than printed. A missing artifact would make
    # every row NOT-DERIVABLE, and "0 misfiled rows" would be true and vacuous.
    assert gt_stats["present"], (
        f"ground truth artifact not read ({gt_stats['error']}) -- this check "
        "would pass while classifying nothing")
    assert gt_stats["classes"] > 0 and gt_stats["field_names"] > 0, gt_stats
    rows = mod.find_duplicates(classes)
    assert rows, "no duplicate rows at all -- the check would pass vacuously"

    classified, _ = mod.classify(rows, gt_index, gt_stats)
    assert len(classified) == len(rows)

    # Independent re-derivation: read the raw artifact, not the tool's index.
    with open(mod.GROUND_TRUTH) as fh:
        raw = json.load(fh)
    norm = mod._norm
    v1 = {norm(cn): {norm(f) for f in (e.get("fields") or [])}
          for cn, e in (raw.get("classes") or {}).items()}

    for r in classified:
        declaring = [o for o in r["owners"]
                     if norm(o) in v1 and norm(r["name"]) in v1[norm(o)]]
        unknown = [o for o in r["owners"] if norm(o) not in v1]
        if r["derived"] == mod.V1_FIDELITY:
            assert len(declaring) >= 2, (
                f"{r['leaf']}.{r['name']} is filed V1-FIDELITY but did_v1 "
                f"declares it in {declaring!r}, fewer than two blocks")
        elif r["derived"] == mod.V_ETA_SHADOW:
            assert not unknown and len(declaring) < 2, (
                f"{r['leaf']}.{r['name']} is filed V_eta-SHADOW but "
                f"unknown={unknown!r} declaring={declaring!r}")
        else:
            assert r["derived"] == mod.NOT_DERIVABLE, r
            assert unknown, (
                f"{r['leaf']}.{r['name']} is filed NOT-DERIVABLE but every "
                "declaring class has a did_v1 counterpart -- the ground truth "
                "could have answered it")

    # The exact row the drift misfiled. Its provenance is NDI's, so it must
    # never come back as an open question a reader might close by deleting.
    sp = [r for r in classified
          if (r["leaf"], r["name"]) == ("stimulus_parameter", "name")]
    assert sp and sp[0]["derived"] == mod.V1_FIDELITY, (
        "stimulus_parameter.name must derive as V1-FIDELITY -- NDI's schema "
        f"declares it and migrators_j/stimulus_parameter.m passes documents "
        f"through unchanged; got {sp!r}")


def test_duplicate_field_overrides_cannot_outvote_ndi_and_cannot_go_stale():
    """The hand list survives only as a NOT-DERIVABLE override, and a dead one fails.

    Both halves matter, and for opposite reasons. An override that could
    overrule the artifact would reintroduce the drift under a new name; an
    override nobody uses is an exception nobody is checking, which is exactly
    how the old list went wrong -- by omission, silently, for two days.
    """
    mod = _load_tool("check_duplicate_field_declarations")

    classes = mod.load_classes()
    gt_index, gt_stats = mod.load_ground_truth()
    assert gt_stats["present"], gt_stats
    rows = mod.find_duplicates(classes)

    derivable = [r for r in mod.classify(rows, gt_index, gt_stats)[0]
                 if r["derived"] != mod.NOT_DERIVABLE]
    undecided = [r for r in mod.classify(rows, gt_index, gt_stats)[0]
                 if r["derived"] == mod.NOT_DERIVABLE]
    assert derivable and undecided, (
        "this test needs one row of each kind to mean anything; got "
        f"{len(derivable)} derivable, {len(undecided)} not")

    # 1. An override on a row the artifact ANSWERS is refused, and the reported
    #    bucket stays the derived one -- NDI wins, the hand entry loses.
    victim = (derivable[0]["leaf"], derivable[0]["name"])
    wrong = mod.V_ETA_SHADOW if derivable[0]["derived"] == mod.V1_FIDELITY \
        else mod.V1_FIDELITY
    out, ovr = mod.classify(rows, gt_index, gt_stats,
                            {victim: (wrong, "a hand claim contradicting NDI")})
    got = next(r for r in out if (r["leaf"], r["name"]) == victim)
    assert victim in ovr["refused"], ovr
    assert got["bucket"] == got["derived"] != wrong, got

    # 2. An override on a NOT-DERIVABLE row applies.
    target = (undecided[0]["leaf"], undecided[0]["name"])
    out, ovr = mod.classify(rows, gt_index, gt_stats,
                            {target: (mod.V1_FIDELITY, "renamed from a v1 source")})
    got = next(r for r in out if (r["leaf"], r["name"]) == target)
    assert target in ovr["used"] and got["bucket"] == mod.V1_FIDELITY, (got, ovr)

    # 3. An override matching no row is reported unused...
    _, ovr = mod.classify(rows, gt_index, gt_stats,
                          {("no_such_class", "no_such_field"): (mod.V1_FIDELITY, "x")})
    assert ovr["unused"] == [("no_such_class", "no_such_field")], ovr

    # 4. ...and unused or refused overrides FAIL the tool, with or without
    #    --enforce. Driven through main() so the exit code is the thing tested.
    real = mod.OVERRIDES
    try:
        for bad, label in ((({("no_such_class", "no_such_field"):
                              (mod.V1_FIDELITY, "stale")}), "unused"),
                           (({victim: (wrong, "contradicts NDI")}), "refused")):
            mod.OVERRIDES = bad
            for argv in ([], ["--enforce"]):
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    code = mod.main(argv)
                assert code == 1, (
                    f"a {label} override exited {code} with argv={argv!r} -- a "
                    "silent stale exception is the defect this replaces")
                assert "FAIL:" in buf.getvalue(), buf.getvalue()
    finally:
        mod.OVERRIDES = real

    # 5. And the committed set is clean under the real overrides.
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        assert mod.main(["--enforce"]) == 0, buf.getvalue()


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
        f'{sum(kinds.values())} rows classified out of {len(rows)} -- a state is missing from this tally')
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
    """Still option C on the SET, and now a shape rule alongside it.

    THIS TEST DID ITS JOB AND WAS THEN AMENDED, which is the only honest way to
    record it. It asserted `set(b) == {"strength"}` -- a deliberate tripwire so
    that any growth of these three bindings had to be argued for -- and #32
    increment 2 tripped it by adding `node_form: curie`. The tripwire is kept,
    narrowed to what it was actually protecting: NO ADMISSIBLE SET may appear
    here by guesswork.

    The distinction the amendment turns on:

      an admissible SET  says which terms are allowed. Undecided for these
                         three, and undecidable in this repository -- the
                         candidate set for `variable` is NDIC.txt, which moved
                         to VH-Lab/ndi-ontology-matlab (commit 2c19bf24c).
                         Inventing a root node here would be the fabrication
                         the ground-truth track exists to remove.
      a SHAPE rule       says the value must be a term REFERENCE at all -- a
                         well-formed CURIE. It picks no vocabulary, so it
                         cannot be a wrong guess about one, and it is
                         checkable with nothing loaded.

    So `ontology` / `root_node` / `values` / `keyed_by` / `term_set` remain
    forbidden and `node_form` is admitted, by name.
    """
    forbidden = {"ontology", "root_node", "values", "keyed_by", "term_set",
                 "vocabulary", "root", "source"}
    for cls, fname in _PIVOT_BINDINGS:
        _tier, d = RECORDS[cls]
        fld = next(f for f in d["fields"] if f["name"] == fname)
        b = fld["constraints"]["binding"]
        assert set(b) == {"strength", "node_form"}, (
            f"{cls}.{fname} binding grew keys {sorted(set(b) - {'strength', 'node_form'})}. "
            "Naming an admissible set is a separate decision (option A or B).")
        assert not (set(b) & forbidden), (cls, fname, sorted(set(b) & forbidden))
        assert b["node_form"] == "curie", (cls, fname, b)


def test_the_pivot_bindings_stay_preferred_because_the_registry_itself_would_fail():
    """WHY `required` is not affordable, stated as evidence rather than caution.

    binding_registry_meta.json's own `subject_statement_bindings` rows carry
    `"variable": {"node": "", "name": "species"}` -- an EMPTY node, on every
    row. A `required` node_form binding on `variable` would reject the very file
    that defines the vocabulary. That is positive evidence of a non-zero cost,
    not an absence of evidence, and it is the reason the DID-matlab validator
    (did2.schema.cache/checkBinding) rejects only on `required` and ships behind
    a switch that is disarmed by default.

    If someone ever fills those nodes in, this test fails and says to
    re-examine the strength -- which is the moment the question should be
    reopened.
    """
    reg = _load(os.path.join(VETA, "stable", "binding_registry_meta.json"))
    rows = reg["subject_statement_bindings"]
    assert rows, "no rows -- this test would verify nothing"
    without_node = [r for r in rows if not r["variable"].get("node")]
    assert len(without_node) == len(rows), (
        f"{len(rows) - len(without_node)} of {len(rows)} registry variable rows "
        "now carry a node. A `required` node_form may finally be affordable -- "
        "measure it on a corpus before changing anything.")


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

    NARROWED 2026-08-11 (#65 increment 3a), and narrowed rather than deleted.
    It named BOTH epoch reference classes and required `checked == 2`.
    `epoch_relative_reference` is now deleted -- it has no emitter, no NDI
    template and no referencing schema -- while `epoch_bounded_reference` is
    still minted (ndi_second_pass/stimulusBathToBath.m:166) and still needs
    exactly this guard. The `if cls not in RECORDS: continue` escape is GONE
    with it: a skip that silently satisfies the loop is how this assertion
    would go vacuous the day the surviving class disappears too.
    """
    assert "epoch_relative_reference" not in RECORDS, (
        "epoch_relative_reference came back; increment 3a deleted it")
    checked = 0
    for cls in ("epoch_bounded_reference",):
        _tier, d = RECORDS[cls]        # KeyError, deliberately, not a skip
        fld = _field_at(d, ("epoch_clock",))
        assert fld["type"] == "char", cls
        b = fld["constraints"]["binding"]
        assert set(b["values"]) == NDI_CLOCKTYPES, (
            f"{cls}.epoch_clock no longer carries NDI's nine: {sorted(b['values'])}")
        checked += 1
    assert checked == 1, (
        f"expected the one still-minted epoch reference class; found {checked}. "
        "If a later increment deletes it, delete this test with it -- do not "
        "let the count fall to zero and keep passing.")


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
        f"list-valued fields typed `char` cannot validate; use `string`: {bad!r}")


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
    _tier, d = RECORDS["ngrid"]
    fields = {f["name"]: f for f in d.get("fields", [])}
    assert set(fields) == {"data_size", "data_type", "data_dim", "coordinates"}, (
        f"the tombstone must declare the four did_v1 names and nothing else; got {sorted(fields)!r}")
    # the V_delta migrator's output, and the three downstream inventions
    for invented in ("ndims", "dim_sizes", "dim_labels"):
        assert invented not in fields, (
            f"{invented} has no did_v1 existence -- it is V_delta output or a downstream "
            "invention, and declaring it (REQUIRED, for ndims) quarantines every "
            "real document")
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
            f'`ngrid` was retired while {len(consumers)} class(es) still declare it a superclass ({", ".join(consumers)}). Retirement is gated on BOTH consumers (#46): ontology_image (#47) and hartley_calc via reverse_correlation (#48). Fold them first, or every passthrough quarantines on undeclaredField.')
        return
    # Today: the gate is CLOSED, and this records who is holding it shut, so a
    # reader does not have to take the prose's word for the count.
    assert consumers == ["ontology_image", "reverse_correlation"], (
        f"the ngrid consumer set changed: {consumers!r}. Re-derive #46's gate before acting "
        "-- `hartley_calc` reaches ngrid through reverse_correlation, so the "
        "chain is hartley_calc -> hartley_reverse_correlation -> "
        "reverse_correlation -> ngrid.")


def test_sampled_body_axes_now_has_the_coordinate_slot_ngrid_needs():
    """INVERTED 2026-08-14. This asserted the slot does NOT exist; it does now.

    THE TRIPWIRE WORKED, and that is worth recording before the assertion is
    changed. The old test was written as #47's GUARD 2 made executable: the ngrid
    fold refuses a document carrying explicit coordinates because
    `axes[k].values` did not exist, and the test pinned that PREMISE so the guard
    could not quietly outlive its reason. Its own words: "When #45 lands the
    slot, this test fails -- which is the signal that the refusal can be relaxed,
    rather than a guard quietly outliving its reason."

    #45 landed the slot (TEAM-SIGN-OFF [data_body] 2026-08-14 plus AMENDMENT 1),
    the test failed on the first build, and its failure message said exactly what
    to do. This is the rare case of a stale justification being caught BY
    CONSTRUCTION rather than by someone noticing.

    WHAT IS NOW OWED, AND IT IS NOT DONE HERE. The carry --
    `ngrid.coordinates -> axes[k].values` -- is #46/#48 work: retiring `ngrid` is
    gated on BOTH its consumers (`ngrid` itself and `ontologyImage`), and that is
    a signed plan of its own. Landing the SLOT does not land the CARRY, and
    `DID-matlab .../+migrators_j/private/jNgridBody.m:166` still raises
    `did2:convert:ngridCoordinatesHaveNoHome`. That refusal is now a DEFERRAL
    rather than a necessity, and it is correct to keep it until the carry is
    built: folding without carrying would DELETE real positions, which is the
    loss the guard exists to stop.

    So this test now asserts the slot's EXISTENCE -- the precondition the carry
    needs -- and the two-way pressure moves to the migrator half, where
    testNgridSampledBodyFold still pins the refusal.
    """
    assert "sampled_body" in RECORDS, "sampled_body is the ngrid fold's target"
    _tier, body = RECORDS["sampled_body"]
    axes = [f for f in body["fields"] if f["name"] == "axes"]
    assert len(axes) == 1, "sampled_body must declare exactly one `axes` field"
    sub = [s["name"] for s in axes[0].get("fields", [])]
    # DENOMINATOR FIRST, kept from the original: without it an empty sub-field
    # list would pass or fail for the wrong reason.
    assert len(sub) >= 4, (
        f"only {len(sub)} axis sub-field(s) read ({sub!r}) -- too few to conclude "
        "anything about a coordinate slot")
    assert "values" in sub, (
        f"`sampled_body.axes[]` declares {sub!r} with no `values`. The signed axis "
        "entry carries the coordinates for an irregular axis; without it the ngrid "
        "carry has nowhere to land and jNgridBody's refusal becomes permanent.")
    # and the slot has to be able to hold BOTH halves of a coordinate array
    vals = [f for f in axes[0]["fields"] if f["name"] == "values"]
    got = sorted(x["name"] for x in vals[0].get("fields", []))
    assert got == ["source_values", "values"], (
        f"`axes[].values` declares {got!r}; the canonical + as-recorded pair is what "
        "lets a fold carry coordinates without silently normalising them")


def test_the_ngrid_fold_targets_exist_and_can_hold_what_the_fold_emits():
    """The schema half of the #47 fold, checked against what the migrator emits.

    `migrators_j/ontology_image.m` mints an `image_observation` + a
    `sampled_body` on its subject-bearing arm. Both halves are LOCKSTEP: the
    migrator alone would quarantine every folded document, and this side alone
    would be an unused declaration. The migrator's own tests run under MATLAB
    only; this is the half that runs everywhere.

    Asserted from the BUILT set, so it cannot go stale the way a comment does.
    """
    assert len(RECORDS) > 200, f"only {len(RECORDS)} schemas loaded"

    # the statement the team named
    assert "image_observation" in RECORDS
    _t, obs = RECORDS["image_observation"]
    assert not obs["document_class"].get("abstract"), (
        "image_observation is the minted class; an abstract one cannot be "
        "instantiated (cache.m raises did2:validation:abstractInstantiation)")
    supers = [s["class_name"] for s in obs["document_class"]["superclasses"]]
    assert supers == ["subject_observation", "image"], (
        f"the migrator emits exactly these direct superclasses; got {supers!r}")

    # the body it is bound to
    _t, sb = RECORDS["sampled_body"]
    assert not sb["document_class"].get("abstract")
    edges = {e["name"]: e for e in sb.get("depends_on", [])}
    assert edges["statement"]["mustBeNonEmpty"] is True, (
        "the fold binds the body to the image_observation through `statement`; "
        "an optional edge here would let a body be minted belonging to nobody")

    # `datum.kind` must admit 'array' -- an ngrid is an N-D grid by definition,
    # and this is an ENUM, so a wrong word quarantines every folded body.
    datum = next(f for f in sb["fields"] if f["name"] == "datum")
    kind = next(s for s in datum["fields"] if s["name"] == "kind")
    assert "array" in kind["constraints"]["enum"], (
        "sampled_body.datum.kind no longer admits 'array': {!r}".format(kind["constraints"]["enum"]))

    # `axes[].name` is the one axis sub-field that is REQUIRED, which is why
    # jNgridBody emits positional names (`axis_1` ...) rather than blanks.
    axes = next(f for f in sb["fields"] if f["name"] == "axes")
    required = [s["name"] for s in axes["fields"] if s.get("mustBeNonEmpty")]
    # UPDATED 2026-08-14: was `["name"]`. The signed axis entry drops `name` --
    # its own examples ('contrast', 'orientation') ARE variables, and a
    # free-text name beside a bound `variable` is the escape hatch that makes
    # the binding pointless -- and requires `variable` and `n` instead. `n` is
    # required because an axis that cannot say how long it is cannot index
    # anything; that is the jrclust `n = 0` shape the plan refuses.
    assert required == ["variable", "n"], (
        f"the axis entry's required sub-fields changed to {required!r} -- jNgridBody fills "
        "`name` and leaves the rest defaulted, so a new requirement quarantines "
        "every folded body")

    # storage_mode 'body' is what says the pixels are in the sampled_body
    _t, stmt = RECORDS["subject_statement"]
    mode = next(f for f in stmt["fields"] if f["name"] == "storage_mode")
    assert "body" in mode["constraints"]["enum"]


def test_the_rf_family_is_superclass_only_so_repointing_it_would_strand_hartley():
    """WHY `reverse_correlation` KEEPS its `ngrid` superclass, recorded as a
    check rather than as prose.

    A discrepancy worth reconciling, and both halves of it are true:

      - The BUILT schema marks `reverse_correlation` CONCRETE (no `abstract`
        flag), and so is `hartley_reverse_correlation`.
      - `V_eta_ngrid_family_findings.md` F1 reads the WRITER
        (`NDIcalc-vis +ndi/+calc/+vis/hartley.m:448`) and finds ONE document
        constructed, of class `hartley_calc`, carrying the `hartley_calc`,
        `hartley_reverse_correlation`, `reverse_correlation` and `ngrid` blocks.
        Neither intermediate class is ever minted standalone.

    They agree once the question is split: the CLASSES are declared instantiable,
    and NO DOCUMENT OF EITHER IS EVER WRITTEN. The mechanical half of that is
    checked here — neither name appears in the 102-class v1 source universe, so
    the coverage ledger does not carry a row for either, so no did_v1 document
    can arrive under those names.

    THE CONSEQUENCE IS THE POINT. "Superclass-only" is exactly why
    `reverse_correlation` may NOT be re-pointed off `ngrid`: it has no documents
    of its own to fold, and the block it declares is inherited by `hartley_calc`,
    which HAS documents (>=210 in the 20211116 corpus). Removing the superclass
    would leave every one of them carrying an undeclared `ngrid` block —
    `undeclaredField`, on a 0-quarantine gate. The fold that would release it is
    the RF one (#48), and the repo it needs (VH-Lab/NDIcalc-vis-matlab) is not in
    scope.
    """
    ledger = _load(os.path.join(REPO_ROOT, "schemas", "V_eta_coverage_ledger.json"))
    rows = ledger["rows"]
    # DENOMINATOR FIRST. An empty ledger would make every "not a source" claim
    # below trivially true.
    assert len(rows) == 102, (
        f'the v1 source universe is 102 classes (91 NDI templates + 11 vhlab app classes); read {len(rows)}')
    v1 = {r["v1_class"] for r in rows}

    for name in ("reverse_correlation", "hartley_reverse_correlation"):
        assert name in RECORDS, f"{name} is still in the built set"
        assert name not in v1, (
            f"{name} became a v1 SOURCE class. F1 read the writer and found it "
            "superclass-only; if that changed, the ngrid gate changes with it.")
    # and the one class that IS a source, and that inherits ngrid through them
    assert "hartley_calc" in v1
    chain = [s["class_name"]
             for s in RECORDS["hartley_calc"][1]["document_class"]["superclasses"]]
    assert "hartley_reverse_correlation" in chain, (
        f"hartley_calc no longer reaches ngrid through the RF chain: {chain!r}")
    rc_supers = [s["class_name"]
                 for s in RECORDS["reverse_correlation"][1]["document_class"]["superclasses"]]
    assert "ngrid" in rc_supers, (
        "`reverse_correlation` was re-pointed off `ngrid` while `hartley_calc` "
        "still inherits from it and still passes through carrying an ngrid "
        "block. That is `undeclaredField` on every hartley_calc document. The "
        "release is the RF fold (#48), not a superclass edit.")


def test_image_stack_pair_survives_for_the_subject_less_passthrough():
    """The schema half of the image_stack guard, made mechanical.

    `migrators_j/image_stack.m` passes a subject-less document THROUGH (NDI's
    own writer leaves `subject_id` empty at +setup/+conv/+haley/doImport.m:789,
    811 and 827), and a passthrough validates against the SOURCE tombstone. Both
    classes were in `_DELETE_PHASE8` and came back out for exactly this reason.
    Re-deleting either strands 4,563 JH documents in quarantine -- the
    `epochfiles_ingested` regression, which is what happens when a tombstone is
    removed ahead of its migrator.

    The MATLAB side has its own guard (testTemplateLiteralTypeTraps.m,
    testImageStackParametersTombstoneStillExists); this is the one that fails in
    the fast Python gate, where the deletion would actually be made.
    """
    assert len(RECORDS) > 200, f"only {len(RECORDS)} schemas loaded"   # denominator
    for cls in ("image_stack", "image_stack_parameters"):
        assert cls in RECORDS, (
            f"`{cls}` was re-deleted. The subject-less passthrough in "
            "migrators_j/image_stack.m then has no schema to validate against: "
            "4,563 JH quarantines.")

    deps = {d["name"]: d for d in RECORDS["image_stack"][1]["depends_on"]}
    # The whole point of the reversal: NDI writes documents with no subject, so
    # requiring the edge is what created the husks in the first place.
    assert deps["subject_id"]["mustBeNonEmpty"] is False, (
        "subject_id must stay OPTIONAL -- three of NDI's seven imageStack sites "
        "never set it")
    assert "document_id" in deps, "NDI's imageStack declares document_id"
    assert "element_id" not in deps, (
        "`element_id` is the V_alpha invention this tombstone was restated to "
        "remove; no NDI template has it")


def test_image_stack_declares_ndis_own_file_name():
    """A tombstone must declare the file the document actually carries.

    `universalRenames` skips the structural keys outright -- `skip =
    {'document_class', 'depends_on', 'file', 'files'}` (DID-matlab
    +did2/+convert/universalRenames.m:308) -- so a passed-through document still
    carries NDI's spelling, `imageStack`, from `add_file('imageStack', ...)` at
    all eight attachment sites. The tombstone declared `imagestack_file`, a name
    no document has, which tripped BOTH directions of the #64 file audit at once
    (declared-but-absent AND present-but-undeclared) for every JH document.

    Nothing caught it: `did2.validate.fileList` compares by exact strcmp and
    does not normalise, and `check_tombstones.py` does not compare files at all.
    Hence this test.
    """
    files = [f["name"] for f in RECORDS["image_stack"][1].get("file", [])]
    assert files == ["imageStack"], (
        "image_stack must declare NDI's own file_list entry verbatim, not a "
        f"snake_cased invention; got {files!r}")


def test_openminds_stimulus_passthrough_keeps_the_second_pass_join_keys():
    """#75, the schema half. The 635 `StimulationApproach` documents go to
    `interaction_purpose` via the NDI second pass -- and pass 1 can only defer to
    that pass if the passthrough still carries the two facts the pass joins on.

    THE ROUTING IS SIGNED, twice, and by only one destination. Of the 23
    TEAM-SIGN-OFF lines under schemas/, exactly ONE names these documents:

        V_eta_go_forward_class_audit.md:3
        TEAM-SIGN-OFF [misc singletons]: jess, 2026-08-09 -- ... `interaction_purpose`
        is KEPT ... and is the destination for the 635 `StimulationApproach`
        documents via a second pass -- so #71 is repaired by re-targeting, with
        pass 1 emitting nothing ...

    and the [stimulus] sign-off's own body (V_eta_stimulus_model_plan.md:124-132)
    resolves the same way. The `term_assertion` route #75 called the second
    "signed plan" was never a plan: it was `migrators_j/openminds_stimulus.m`,
    and that file now emits nothing (`bodies = {preBody}` at :84).

    WHAT THIS PINS, and why each one is load-bearing rather than decorative:

    1. `stimulus_element_id`, not `stimulus_id`. NDI's template, its schema and
       `openMINDSobj2ndi_document.m:58` all name the edge `stimulus_element_id`;
       `stimulus_id` was a DID-side invention, and reading it is what produced 635
       empty subjects (#71). It is also the JOIN KEY: the approach document and the
       stimulus document both point at the same stimulator, which is the only path
       across the epoch-id namespace gap #76a measured (in Dab all 635 approach
       epoch ids carry an `epoch_` prefix and none of the 1,242 presentation epoch
       ids do -- the two classes share ZERO epoch ids).

    2. The `epochid` superclass, carrying its `epochid` field. This is the ENTIRE
       argument that decided `interaction_purpose` over `term_assertion`: the
       assertion tier is timeless by construction (`time_reference_#` lives on
       `subject_interaction`, the other branch), so an assertion cannot hold the
       epoch both NDI writers set (`stimulusDocMaker.m:407-412`,
       `add_stimulus_approach.m:59-65`). Drop the epoch from the passthrough and
       the second pass has nothing to resolve -- silently, because a passthrough
       that lost a field still validates.

    3. No fields and no other edges. A tombstone that grows a statement-shaped
       field is a migrator emitting again.

    Nothing else watches this: `check_tombstones.py` compares against the NDI
    template, which cannot express "this shape is what the deferred pass needs",
    and no MATLAB fixture pins the superclass chain."""
    assert len(RECORDS) > 200, f"only {len(RECORDS)} schemas loaded"   # denominator
    assert "openminds_stimulus" in RECORDS, (
        "the openminds_stimulus tombstone was deleted; migrators_j/"
        "openminds_stimulus.m passes every document through, so there would be "
        "no schema left to validate them against")

    tomb = RECORDS["openminds_stimulus"][1]

    deps = {d["name"]: d for d in tomb.get("depends_on", [])}
    assert set(deps) == {"stimulus_element_id"}, (
        f"openminds_stimulus declares exactly NDI's one edge; got {sorted(deps)!r}")
    assert "stimulus_id" not in deps, (
        "`stimulus_id` is the invented name that emptied 635 subjects (#71) -- "
        "NDI names this edge `stimulus_element_id` in template, schema and writer")
    assert deps["stimulus_element_id"]["mustBeNonEmpty"] is True, (
        "NDI's schema marks it `mustbenotempty: 1`, and the second pass needs it "
        "as the join key that crosses the epoch-id namespace gap (#76a)")

    chain = _chain("openminds_stimulus")
    assert "epochid" in chain, (
        "openminds_stimulus must keep the `epochid` superclass. The epoch is why "
        "these documents route to interaction_purpose instead of the timeless "
        "assertion tier; without it the deferred second pass has no epoch to "
        "resolve and the loss is silent")
    assert "openminds" in chain, "the openMINDS payload mixin is NDI's own"
    epoch_fields = {f["name"] for f in RECORDS["epochid"][1].get("fields", [])}
    assert "epochid" in epoch_fields, (
        "the epochid mixin must still declare the epochid field -- the superclass "
        "alone carries nothing")

    assert tomb.get("fields", []) == [], (
        "openminds_stimulus is a passthrough tombstone; a field here means pass 1 "
        "started emitting a statement again")

    # The destination the sign-off names must exist, and must not be emittable
    # with a blank required edge -- which is the standing reason the build stays
    # a second pass rather than a pass-1 migrator.
    assert "interaction_purpose" in RECORDS, (
        "the signed destination for these 635 documents no longer exists")
    ip = {d["name"]: d for d in RECORDS["interaction_purpose"][1]["depends_on"]}
    assert ip["interaction_id_#"]["min_count"] >= 1, (
        "interaction_id_# is REQUIRED, so a pass that cannot resolve an "
        "interaction must pass through rather than emit a blank edge")
    purpose = next(f for f in RECORDS["interaction_purpose"][1]["fields"]
                   if f["name"] == "purpose")
    assert purpose["mustBeScalar"] is True, (
        "one purpose per document is what keeps the v1 and V_eta counts equal at "
        "635: an epoch carrying two approach names was two v1 documents and "
        "becomes two interaction_purpose documents")


def test_acquisition_epoch_declares_the_vhsb_payload():
    """Defect 3 of the four in `V_eta_epoch_plan.md`, closed.

    `acquisition_epoch` IS `element_epoch` (the RENAME map entry at
    build_v_eta.py:138), and NDI's template declares a file on it:

        database_documents/element_epoch.json
            "files": { "file_list": [ "epoch_binary_data.vhsb" ] }

    V_eta declared `"file": []`, while every real document carries the payload
    -- measured on corpus B and recorded in the migrator's own header
    (+migrators_j/element_epoch.m: "every element_epoch body has
    `files.file_list = {'epoch_binary_data.vhsb'}` with an ndicloud location").
    That is the `image_stack` bug in its undeclared direction, on a class where
    100% of documents trip it.

    The name is NOT snake_cased: `universalRenames.m:308` skips the structural
    keys (`skip = {'document_class','depends_on','file','files'}`), so a
    migrated document reaches the validator still spelling it NDI's way.

    The plan files this under "repairs, not decisions, and true under either
    option", which is why it lands while the dissolution stays blocked on
    #65 -> #67/#32.
    """
    files = [f["name"] for f in RECORDS["acquisition_epoch"][1].get("file", [])]
    assert files == ["epoch_binary_data.vhsb"], (
        "acquisition_epoch must declare NDI's element_epoch file_list entry "
        f"verbatim -- its documents all carry it; got {files!r}")


def test_oneepoch_and_acquisition_epoch_agree_about_the_payload():
    """The two halves of one v1 shape must not disagree.

    In NDI, `oneepoch`'s ONLY declared superclass is `element_epoch`, so it
    INHERITS the `.vhsb` declaration and declares no file of its own. V_eta
    renames `element_epoch` to `acquisition_epoch` and re-roots `oneepoch` on
    `base, epochid`, so there is no parent left to inherit from and the
    declaration has to be flattened onto both.

    `oneepoch` was flattened first, and its build comment said so in its own
    words -- "the `.vhsb` file is declared, which `acquisition_epoch` does NOT
    do ... this class should not inherit the bug". This pins that the two now
    agree, so a future edit cannot silently re-open the gap from either side.
    """
    ae = [f["name"] for f in RECORDS["acquisition_epoch"][1].get("file", [])]
    oe = [f["name"] for f in RECORDS["oneepoch"][1].get("file", [])]
    assert ae == oe == ["epoch_binary_data.vhsb"], (
        "acquisition_epoch and oneepoch both carry the element_epoch payload "
        f"and must declare the same file; got {ae!r} and {oe!r}")


def test_directed_relation_has_an_optional_epoch_id_slot():
    """The DID-schema half of a recorded, signed blocker.

    `V_eta_OPEN_WORK.md` lists, under "Blockers found in DID-schema, each of
    which stops a signed model being finished":

        `directed_relation` has no `epoch_id` slot, and no migrator mints an
        `epoch`  ->  the ensemble's `member_of` edges CANNOT be epoch-scoped,
        so the per-epoch MAP document cannot be consumed and stays a
        passthrough.

    Both halves were required. `did2.convert.epochMint` closed the minting
    half; this is the schema half.

    Signed twice: TEAM-SIGN-OFF [ensemble] (jess, 2026-08-06) requires
    "EPOCH-SCOPED member_of edges carrying their epoch and column order", and
    TEAM-SIGN-OFF [epoch] (jess, 2026-08-08) drops `epochid` "in favour of a
    uniform epoch_id edge".

    OPTIONAL is load-bearing, not incidental: #37's
    strictMode('RequiredDependencies') is ARMED, and most relations (part_of,
    has_author, derived_from) have no epoch at all. A required edge here would
    rebuild the invented-empty-edge pattern under the repair's own name.
    """
    deps = {d["name"]: d for d in RECORDS["directed_relation"][1]["depends_on"]}
    assert "epoch_id" in deps, (
        "directed_relation needs an epoch_id slot or the signed ensemble model "
        "cannot express an epoch-scoped member_of edge")
    assert deps["epoch_id"]["must_refer_to_document_class"] == "epoch"
    assert deps["epoch_id"]["mustBeNonEmpty"] is False, (
        "epoch_id must stay OPTIONAL -- most relations have no epoch, and "
        "#37's RequiredDependencies gate is armed")
    # column order was already there; the epoch was the missing half.
    assert any(f["name"] == "sequence"
               for f in RECORDS["directed_relation"][1]["fields"])


def test_the_epoch_id_edge_is_spelled_the_same_way_everywhere():
    """"A UNIFORM epoch_id edge" is a claim a test can hold to.

    The epoch sign-off drops `epochid` "in favour of a uniform epoch_id edge".
    Uniform means one name and one target on every class that carries it -- if
    one class spelled it `epochid` or pointed it at `acquisition_epoch`, the
    join the whole family exists to create would be broken in that one place,
    and nothing else would notice.

    Denominator-style: this asserts over EVERY class that declares the edge, so
    a class added later is covered without editing the test.
    """
    holders = {
        name: {d["name"]: d for d in rec["depends_on"]}["epoch_id"]
        for name, (_tier, rec) in RECORDS.items()
        if any(d["name"] == "epoch_id" for d in rec.get("depends_on", []))
    }
    assert len(holders) >= 4, (
        "expected at least the four known holders (acquisition_metadata_file, "
        f"ingestion_manifest, method_parameters, directed_relation); got {sorted(holders)!r}")
    for name, d in sorted(holders.items()):
        assert d["must_refer_to_document_class"] == "epoch", (
            "{}.epoch_id must point at the minted `epoch` entity, not {!r}".format(name, d["must_refer_to_document_class"]))


# ---------------------------------------------------------------------------
# #29 -- the ensemble model (TEAM-SIGN-OFF [ensemble], jess, 2026-08-06)
# ---------------------------------------------------------------------------

def _ndi_ground_truth():
    with open(os.path.join(REPO_ROOT, "schemas",
                           "V_eta_ndi_ground_truth.json")) as fh:
        return json.load(fh)


def test_ensemble_declares_the_neuron_roster_it_carries():
    """The roster lives on EDGES, and the tombstone has to say so.

    `V_eta_ensemble_plan.md` migration-constraint 1 originally said the neuron
    ids lived only inside `neuron_names.txt`, so `member_of` needed file-byte
    access and therefore the NDI second pass. That premise is WRONG and the plan
    now records the correction: the ids are `depends_on` edges written in column
    order by the same loop that writes the names
    (+ndi/+element/ensemble.m:274-276, `add_dependency_value_n`), and NDI's own
    `ensemble_schema.json` declares `neuron_id` with `"mustbenotempty": 0`.

    It survived because the TEMPLATE declares only `element_id` and
    `element_epoch_id` -- `neuron_id` appears in the SCHEMA and the WRITER only.
    That is the ground-truth rule (*where template and writer disagree, the
    writer wins*) firing inside NDI's own pair.

    `ensemble` is a PASSTHROUGH, so this tombstone is the only thing standing
    between a real map document and a quarantine, and an undeclared edge passes
    through SILENTLY: `+did2/+schema/cache.m` allows `depends_on` wholesale and
    never checks individual dependency names. Silence is the shape that let six
    classes reach 100% empty required edges.

    A `_#` FAMILY, not a bare `neuron_id`: `add_dependency_value_n` appends
    `neuron_id_1`, `neuron_id_2`, ..., so the suffix index IS the column index
    the signed model asks `member_of` to carry.
    """
    deps = {d["name"]: d for d in RECORDS["ensemble"][1]["depends_on"]}
    assert "neuron_id_#" in deps, (
        "ensemble must declare the neuron roster as a numbered family; "
        f"declared: {sorted(deps)!r}")
    assert "neuron_id" not in deps, (
        "a bare `neuron_id` does not match what a document carries "
        "(`neuron_id_1`, `neuron_id_2`, ...)")
    nid = deps["neuron_id_#"]
    assert nid["must_refer_to_document_class"] == "subject", (
        "a neuron is an element, and migrators_j.element promotes an element to "
        "a subject with its id PRESERVED, so the stored id still resolves")
    # NDI says "mustbenotempty": 0. Tightening it would be a NEW required edge
    # on a passthrough class -- the invented-empty-edge pattern under a new name.
    assert nid["min_count"] == 0
    assert nid["mustBeNonEmpty"] is False


def test_ensemble_declares_ndis_own_file_name_not_a_snake_cased_one():
    """`neuron_names.txt` verbatim -- the `image_stack` shape, caught before it shipped.

    A passed-through document reaches validation still carrying NDI's spelling:
    `universalRenames.m:308` skips the structural keys outright
    (`skip = {'document_class','depends_on','file','files'}`), and
    `did2.validate.fileList` compares by exact `strcmp` (fileList.m:93,99).
    `image_stack` was restated with `imagestack_file` against NDI's `imageStack`
    and declared a file no document has while the file every document has went
    undeclared -- both directions of the audit at once, on every JH document.

    A file divergence never quarantines, which is exactly why it is dangerous:
    the payload is stranded or unfindable while every gate stays green.
    """
    files = [f["name"] for f in RECORDS["ensemble"][1].get("file", [])]
    assert files == ["neuron_names.txt"], (
        "ensemble carries NDI's `neuron_names.txt` (+ndi/+element/ensemble.m:277 "
        f"attaches it, and both halves of NDI's pair declare it); got {files!r}")


def test_ensemble_tombstone_matches_the_ndi_ground_truth_artifact():
    """Denominator-first: compare the whole declaration, not the two fields we fixed.

    The generated `V_eta_ndi_ground_truth.json` is the artifact; this test is
    prose about it, so the artifact wins when they disagree. Comparing the FULL
    surface is the point -- fixing the two rows a checker happened to name, and
    asserting only those, is how a restatement drifts on its third field.

    Numbered families are compared by their base name (`neuron_id_#` satisfies
    NDI's `neuron_id`), exactly as `tools/check_tombstones.py:_defamily` does.
    """
    gt = _ndi_ground_truth()["classes"]["ensemble"]
    rec = RECORDS["ensemble"][1]

    def defamily(n):
        return n.removesuffix("_#")

    ours_deps = {defamily(d["name"]) for d in rec["depends_on"]}
    ours_fields = {f["name"] for f in rec["fields"]}
    ours_files = {f["name"] for f in rec.get("file", [])}
    ours_supers = [s["class_name"]
                   for s in rec["document_class"]["superclasses"]]

    # denominator, stated before any verdict
    assert len(gt["depends_on"]) == 3 and len(gt["fields"]) == 5, (
        f'the ground truth for `ensemble` changed shape ({len(gt["depends_on"])} dep(s), {len(gt["fields"])} field(s)) -- re-read NDI before trusting this comparison')

    assert set(gt["depends_on"]) <= ours_deps, (
        "real dependencies with nowhere to land: {!r}".format(sorted(set(gt["depends_on"]) - ours_deps)))
    assert set(gt["fields"]) <= ours_fields, (
        "real fields with nowhere to land: {!r}".format(sorted(set(gt["fields"]) - ours_fields)))
    assert set(gt["files"]) <= ours_files, (
        "real files the tombstone does not declare: {!r}".format(sorted(set(gt["files"]) - ours_files)))
    assert ours_supers == gt["superclasses"], (
        "superclass chain diverges from NDI: {!r} vs {!r}".format(ours_supers, gt["superclasses"]))


def test_ensemble_pass_one_mints_no_membership_edge():
    """Pass 1 must not fake what only the second pass can resolve.

    The signed model's `member_of` / `derived_from` edges are
    `directed_relation` DOCUMENTS minted by
    `ndi.migrate.internal.ensembleMembership`, not fields of this class. If they
    ever appeared on the `ensemble` tombstone they would be edges pass 1 cannot
    fill, and #37's `strictMode('RequiredDependencies')` is ARMED -- an empty
    required edge now quarantines rather than passing silently.

    The slots the second pass needs live on `directed_relation` and are asserted
    by `test_directed_relation_has_an_optional_epoch_id_slot`; this asserts they
    are NOT duplicated here.
    """
    names = {d["name"] for d in RECORDS["ensemble"][1]["depends_on"]}
    for forbidden in ("member_of", "member_of_#", "derived_from", "derived_from_#",
                      "child", "parent"):
        assert forbidden not in names, (
            f"`{forbidden}` on the ensemble tombstone: membership is a relation DOCUMENT, "
            "and pass 1 cannot resolve it")


def test_member_of_registry_row_is_timed_and_ordered_as_the_signoff_requires():
    """The sign-off says the edge carries an epoch AND a column order.

    TEAM-SIGN-OFF [ensemble]: members are "EPOCH-SCOPED member_of edges carrying
    their epoch and column order". A registry row saying `timed: false,
    ordered: false` would contradict the signed model in the one place a future
    validator will read. `binding` is not enforced yet, so this costs nothing
    today and gets expensive the moment something reads it.
    """
    with open(os.path.join(VETA, "stable", "binding_registry_meta.json")) as fh:
        reg = json.load(fh)
    rows = [r for r in reg["relation_bindings"]
            if r["relation"]["name"] == "member_of"]
    assert len(rows) == 1, f'expected exactly one member_of row; got {len(rows)}'
    row = rows[0]
    assert row["class"] == "directed_relation"
    assert row["timed"] is True, "the epoch scope makes this edge timed"
    assert row["ordered"] is True, "column order makes this edge ordered"
    assert row["child_types"] == ["subject"] and row["parent_types"] == ["subject"], (
        "a neuron-subject is a member of an ensemble group-SUBJECT")


# ===================== `logical` -- the valid_interval go-forward home ============
#
# TEAM DECISION 2026-08-12 (jess@walthamdatascience.com): `validity` and
# `validity_observation` are REPLACED by `logical` and `logical_observation`.
# The 32 `*_observation` data_types name a KIND OF VALUE; `validity` was the
# only one naming a SEMANTIC, and a semantic belongs in
# `subject_statement.variable` -- which is what the live table-column pass
# already does (`resolveLawnPlateSubjects.m:1106-1113` sends six distinct
# fluorescence semantics to ONE `intensity_observation`, told apart by
# `variable`). `boolean` was impossible as a class name: it is a hard-coded
# primitive in DID-matlab's type switch (`+did2/+schema/cache.m:1793`), so a
# composite of that name would send every struct-valued field into that check.
# `logical` follows the `term`/`ontology_term` precedent -- the data_type name
# differs from the field-type name it wraps.
#
# THE MODEL ITSELF IS STILL UNSIGNED. The 2026-08-11 "decision" it rests on was
# a QUESTION recorded as an answer (OPEN_WORK #103); what is decided is the
# naming. The tests below are the hazards named with the model, one test each,
# so a regression names the hazard it re-opened rather than a field.


def test_logical_is_a_boolean_valued_statement_leaf():
    """The shape: a `subject_statement`-derived class carrying a BOOLEAN, sharing
    the statement family's time reference.

    `variable` (what is judged), `subject_id` (whose data) and `time_reference_#`
    (over which stretch) are all INHERITED -- from subject_statement and
    subject_interaction -- which is the whole point of "takes a subject
    statement". If the chain ever stops reaching subject_interaction, the class
    silently loses its time anchor and starts asserting over all time, so the
    chain is asserted here rather than assumed.
    """
    assert "logical" in RECORDS and "logical_observation" in RECORDS
    assert "validity" not in RECORDS and "validity_observation" not in RECORDS, (
        "the replaced classes are still built; a name that means the same thing "
        "twice is how a migrator ends up emitting the dead one")
    _tier, comp = RECORDS["logical"]
    assert comp["document_class"]["abstract"] is True
    assert [s["class_name"] for s in comp["document_class"]["superclasses"]] == ["data_type"]

    # T14: ONE payload slot, `value` -- and it is a BARE boolean array, not a
    # cell. The cell it replaced was `{value: boolean}`, i.e. `value.value`: a
    # wrapper around nothing. The composites that nest do so to carry provenance
    # (canonical + source_unit + source_value, or count's semantic unit); a truth
    # value has no unit, no source unit and cannot be approximate. `term.value`
    # is the precedent -- typed `ontology_term` directly.
    assert [f["name"] for f in comp["fields"]] == ["value"]
    val = comp["fields"][0]
    assert val["type"] == "boolean", (
        "the team asked for true/false. A term-valued 'valid'/'garbage' pair "
        "would encode a boolean as a vocabulary (T13) and would make the "
        "invalid half unreachable the same way the CLASS NAME did in v1")
    assert val["mustBeScalar"] is False and val["blank_value"] == []
    assert val["mustBeNonEmpty"] is True, (
        "a logical statement with no value says nothing at all -- exactly the "
        "hollow document silentLoss and isFragment exist to catch")
    assert "fields" not in val, (
        "`logical.value` grew a nested cell again. `value.value` is a wrapper "
        "around nothing; provenance is what earns a cell and a boolean has none")
    # And the class name is NOT a field type: `boolean` is the field type, and it
    # is a validator primitive, so `logical` must stay out of the meta enum.
    assert "logical" not in META["$defs"]["field_definition"]["properties"]["type"]["enum"]

    _, leaf = RECORDS["logical_observation"]
    assert [s["class_name"] for s in leaf["document_class"]["superclasses"]] == [
        "subject_observation", "logical"]
    assert leaf["fields"] == [], (
        "logical_observation declares fields. It has NONE, like "
        "length_observation and count_observation -- everything it needs is "
        "inherited, and `sequence` went with HAZARD 2")
    chain, seen = [], "subject_observation"
    while seen and seen in RECORDS:
        chain.append(seen)
        sup = RECORDS[seen][1]["document_class"]["superclasses"]
        seen = sup[0]["class_name"] if sup else None
    assert "subject_interaction" in chain and "subject_statement" in chain, (
        "logical_observation must reach subject_interaction (for "
        "time_reference_#) and subject_statement (for subject_id + variable); "
        f"chain was {chain!r}")


def test_absence_of_a_logical_statement_must_keep_meaning_valid():
    """HAZARD 1. `ndi.app.markgarbage` is OPT-IN: no `valid_interval` document
    means the whole epoch is good data (markgarbage.m:172-176 returns the whole
    requested span when it finds no record).

    A class that states true/false explicitly can destroy that in two ways, and
    both are mechanical, so both are gated here:

      * something REQUIRES a logical statement, so a subject without one reads
        as incomplete rather than as valid;
      * the reading rule lives only in prose, so a consumer assumes
        "no statement = unknown" and every epoch in every dataset that never ran
        markgarbage is silently reclassified.

    NOTHING WE CURRENTLY GATE ON WOULD CATCH EITHER. The corpus gate counts
    quarantines and orphans; a corpus with no markgarbage documents is 0/0 both
    before and after a reclassification that changes the meaning of every epoch
    in it.
    """
    offenders = []
    for name, (_tier, d) in RECORDS.items():
        for dep in d.get("depends_on", []):
            required = dep.get("mustBeNonEmpty") or (dep.get("min_count") or 0) > 0
            if dep.get("must_refer_to_document_class") in (
                    "logical", "logical_observation") and required:
                offenders.append("{}.{}".format(name, dep["name"]))
    assert offenders == [], (
        "these edges REQUIRE a logical statement: {}. Absence must stay a "
        "legal, meaningful state -- it is how every dataset that never ran "
        "markgarbage says 'all of this is good data'.".format(
            ", ".join(offenders)))

    # And nothing subclasses it into a position where a parent's requirement
    # could reach it.
    children = [n for n, (_t, d) in RECORDS.items()
                if any(s["class_name"] == "logical"
                       for s in d["document_class"]["superclasses"])]
    assert children == ["logical_observation"], (
        f"logical gained subclasses ({children!r}); each one is a new way for "
        "the boolean to become required somewhere")

    doc = RECORDS["logical"][1]["fields"][0]["documentation"]
    # SCOPED BY `variable`, and that scoping is load-bearing now that the class
    # is generic. `validity` named the semantic, so "no statement of this class"
    # and "no statement about data validity" were one sentence; under `logical`
    # they are not, and an unscoped rule would let a subject with no statement
    # about some unrelated boolean read as "data valid".
    assert "ABSENCE OF *EVERY* `logical` STATEMENT ABOUT A SUBJECT'S DATA "\
           "VALIDITY MEANS ITS DATA IS VALID" in doc, (
        "the absence rule is DECLARED (T14), not left in a plan document. A "
        "consumer that never read our prose has to get this right, because "
        "reading it wrong is silent")
    assert "scoped BY `variable`" in doc, (
        "the absence rule lost its `variable` scoping. Unscoped on a GENERIC "
        "boolean class it claims something about every subject that never "
        "carried a validity judgement at all")


def test_the_four_reading_rules_are_declared_on_the_class():
    """Team, 2026-08-12. FOUR reading rules for a V_eta consumer, DECLARED on
    the class rather than left in `V_eta_logical_observation_plan.md`.

    T14 is the reason, and it is the same reason the absence rule is declared:
    a consumer that never read our plan documents still has to get these right,
    and EVERY WAY OF GETTING THEM WRONG IS SILENT. A consumer that stops at the
    first `derived_from` hop, or that copies interval numbers without their
    anchor, or that reads "we could not project this" as "valid", produces
    documents that validate, a corpus that is 0-quarantine and 0-orphan, and
    an answer that is wrong about which stretches of a recording are usable.

    Each assertion below pins ONE rule by the clause that carries its meaning,
    not by a paraphrase -- a rule softened in the documentation should fail
    here rather than pass on a near-match.
    """
    doc = RECORDS["logical"][1]["fields"][0]["documentation"]

    # RULE 1 -- transitive, and over `derived_from` specifically.
    assert "INHERITANCE WALKS THE WHOLE `derived_from` CHAIN, TRANSITIVELY" in doc
    assert "ANY DEPTH" in doc, (
        "rule 1 lost its depth claim. A single-hop walk never reaches the "
        "electrode from a neuron, which is the case the rule exists for")
    # And the divergence from NDI is stated as what it IS. NDI's fallback DOES
    # recurse (markgarbage.m:149 calls loadvalidinterval on underlying_element,
    # and that function contains the same block), so a claim that V_eta
    # diverges by DEPTH would be false -- it diverges by EDGE and by SCOPE.
    assert "it is NOT depth" in doc, (
        "the divergence claim drifted back to depth. NDI recurses "
        "(markgarbage.m:149); V_eta differs by walking `derived_from` in the "
        "migrated graph and by scoping the walk to one `variable`")

    # RULE 2 -- the anchor travels with the statement.
    assert "NEVER THE" in doc and "INTERVAL NUMBERS ALONE" in doc
    assert "converts through the syncgraph" in doc

    # RULE 3 -- three states, and the third is NOT valid.
    assert "THERE ARE THREE STATES, NOT TWO" in doc
    assert "UNKNOWN, AND NOT VALID" in doc, (
        "the third state stopped being distinguished from the first. In v1 "
        "they collapse -- markgarbage.m:190 skips an unprojectable interval "
        "and :198-199 then returns the WHOLE requested span -- so a clock "
        "mismatch reads as 'all of this data is good'. That collapse is the "
        "thing this rule exists to break")

    # RULE 4 -- and the number, without which rule 3 cannot be checked.
    assert "THE FAILURE MUST BE COUNTABLE" in doc
    assert "REPORTS the" in doc and "could not project" in doc

    # AND IT MUST NOT CLAIM MORE THAN THAT. The rule is scoped to NO STATEMENT
    # AT ALL. It does NOT extend to the gaps BETWEEN statements, and v1's answer
    # there is the opposite: `markvalidinterval` marks a valid interval "(all
    # else is garbage)" (markgarbage.m:42), and once any interval projects into
    # an epoch, identifyvalidintervals returns ONLY the marked ones
    # (markgarbage.m:200-204). Decomposing one v1 document into N statements
    # does not carry that closure, so a reader who over-applies the absence rule
    # to a gap inverts the meaning of the document -- "only 10-50s is usable"
    # becomes "everything is usable".
    #
    # The team DEFERRED deciding what a gap means (2026-08-11). An UNDEFINED gap
    # is safe to defer; a gap silently read as valid is not. This pins the
    # scoping so the deferral cannot quietly become an answer.
    assert "DOES NOT EXTEND TO THE GAPS BETWEEN STATEMENTS" in doc, (
        "the absence rule lost its scope. Unqualified, it reads as 'any stretch "
        "with no statement is valid', which INVERTS a v1 document that marked "
        "the good stretches and meant the rest was garbage")
    assert "OPEN TEAM DECISION" in doc, (
        "the gap question stopped being marked open. It is deferred, not "
        "resolved -- if it has been decided, record the decision and change "
        "this assertion to pin the answer instead")


def test_logical_does_not_carry_a_v1_array_position():
    """HAZARD 2, RESOLVED AND INVERTED 2026-08-12. This test used to assert the
    OPPOSITE and was named `test_validity_carries_the_v1_array_position_that_
    order_is_load_bearing_for`.

    The old premise: `+app/+stimulus/tuning_response.m:253-256` reads
    `interval(1,1)`..`interval(1,2)` -- "the FIRST interval" -- so v1's
    array-append order (markgarbage.m:89) had to be carried through the
    decomposition, in `sequence`.

    The premise is false, and the evidence is the two call sites, read from NDI
    `origin/main` (42c94e53b). `interval` is the RETURN VALUE of
    `identifyvalidintervals`; the stored array `vi` is loaded at :253 into a
    variable that is never read again. And `identifyvalidintervals`
    (markgarbage.m:178-204) iterates `for i=1:size(vi,1)` accumulating through
    `vlt.math.interval_add` -- a SET UNION -- and never indexes `vi` by
    position. So the append order is invisible to its only consumer: a storage
    artifact, not a fact.

    This is the shape CLAUDE.md names under "A TEST WRITTEN FROM THE SAME
    PREMISE AS THE CODE CANNOT CATCH THE CODE" -- the schema, the migrator and
    the test all asserted one unchecked reading of a call site. So the
    replacement pins the DELETION rather than removing the test.
    """
    fields = RECORDS["logical_observation"][1]["fields"]
    assert fields == [], (
        f"logical_observation declares {[f['name'] for f in fields]!r}. It has "
        "no fields: `sequence` was deleted with HAZARD 2, and nothing else "
        "belongs on the leaf")
    # `sequence` itself is NOT retired as a concept -- directed_relation's is a
    # real order over a real sequence. Pinned so this deletion is not read as a
    # licence to delete that one.
    dr = [f for f in RECORDS["directed_relation"][1]["fields"]
          if f["name"] == "sequence"]
    assert len(dr) == 1 and dr[0]["type"] == "integer", (
        "directed_relation.sequence went with it; that one orders a genuine "
        "sequence and was never part of HAZARD 2")


def test_logical_forecloses_neither_answer_on_the_inheritance_question():
    """HAZARD 3, WHICH IS NOT DECIDED AND IS NOT CLAIMED HERE.

    `loadvalidinterval` falls back to `underlying_element` when a derived
    element has no intervals of its own (markgarbage.m:146-155) -- a QUERY-TIME
    rule in NDI. Whether V_eta re-derives that through the `derived_from` chain
    or materialises copies onto derived subjects is an OPEN SUB-QUESTION for the
    team.

    This test asserts only that both answers remain buildable: the edge a
    materialising decision would need already exists and is OPTIONAL (so pass 1
    is not obliged to fill it, and does not), and the statement points at the
    element the v1 document named, so a re-deriving decision still has the exact
    v1 graph to walk. It does NOT assert which answer is right.
    """
    inherited = RECORDS["subject_observation"][1]["depends_on"]
    df = [d for d in inherited if d["name"] == "derived_from_#"]
    assert len(df) == 1, (
        "subject_observation lost derived_from_# -- the edge a materialising "
        "answer to the inheritance question would ride on")
    assert df[0]["mustBeNonEmpty"] is False and (df[0].get("min_count") or 0) == 0, (
        "derived_from_# became required; pass 1 mints no such edge for a "
        "logical statement, so requiring it would quarantine every one of them "
        "and would ALSO pre-empt a team decision by making the materialising "
        "answer the only legal one")
    # The referent is the element-subject, unqualified: subject_statement's own
    # edge, typed `subject`, which is what element.m's id-preserving promotion
    # lands on.
    sid = [d for d in RECORDS["subject_statement"][1]["depends_on"]
           if d["name"] == "subject_id"]
    assert len(sid) == 1 and sid[0]["must_refer_to_document_class"] == "subject"
