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
    assert RECORDS["numeric_assertion"][1]["document_class"].get("abstract") is True
    # a dimensioned assertion leaf carries a scalar value cell (one cell, no series)
    mass = RECORDS["mass_assertion"][1]
    v = [f for f in mass["fields"] if f["name"] == "value"][0]
    assert v["type"] == "mass" and v["mustBeScalar"] is True


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
    for e in ("subject", "person", "organization", "publication", "award",
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
    for e in ("dataset", "person", "organization", "publication", "award",
              "web_resource", "session"):
        f = _local_id(e)
        assert f is not None, f"{e} should carry an optional local_identifier"
        assert f["mustBeNonEmpty"] is False, f"{e}.local_identifier must be optional"


def test_mock_class_dropped():
    """`mock` (a bare ismock flag) is test-only scaffolding — nothing constructs
    it; a production go-forward schema should not carry a 'this is fake' class."""
    assert "mock" not in RECORDS


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
    sm = [f for f in RECORDS["subject_statement"][1]["fields"]
          if f["name"] == "storage_mode"][0]
    assert set(sm["constraints"]["enum"]) == {"inline", "reference", "body"}


def test_parameters_on_statement():
    """subject_statement carries a `parameters` list (D10 qualifiers) of typed
    {variable, value} entries — each with a variable plus nested term/count/quantity
    data-type blocks (exactly-one is an ingest validator, provisional)."""
    ft = _flat_field_types("subject_statement")
    assert ft.get("parameters") == "structure"
    params = [f for f in RECORDS["subject_statement"][1]["fields"]
              if f["name"] == "parameters"][0]
    # a list (non-scalar), not a single struct
    assert params["mustBeScalar"] is False
    sub = {f["name"]: f for f in params["fields"]}
    assert sub["variable"]["type"] == "ontology_term"
    # the three nested typed value blocks, each holding an array `value`
    for block in ("term", "count", "quantity"):
        assert block in sub, f"parameters missing {block} block"
        val = [f for f in sub[block]["fields"] if f["name"] == "value"][0]
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
    for name in RECORDS:
        chain = _chain(name)
        if "subject_assertion" not in chain and name != "subject_assertion":
            continue
        deps = _flat_dep_names(name)
        assert "time_reference_#" not in deps, \
            f"{name} is an assertion — it must not declare time_reference"
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
    # opaque_body carries a small descriptor (generic_file folds onto it, 2.D slice A)
    of = {f["name"] for f in RECORDS["opaque_body"][1]["fields"]}
    assert {"format", "filename", "description"} <= of


def test_generic_file_folded_to_opaque_body():
    """2.D slice A: generic_file dissolves into opaque_body (no class of its own)."""
    assert "generic_file" not in RECORDS
    assert "opaque_body" in RECORDS


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
                 "documented_by", "stored_at", "hosted_by"):
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
