"""V_zeta (Brainstorm I) schema-set integrity tests.

V_zeta is not in conftest's SCHEMA_VERSIONS parametrization (that covers the
V_beta / V_gamma wire-shape matrix). These tests validate the V_zeta set on
its own terms: every schema file passes the meta-schema, index.json agrees
with disk, superclass and dependency references resolve, tier folder matches
maturity_level, and the Brainstorm-I spine composes onto its leaves.
"""
import glob
import json
import os

import jsonschema
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VZETA = os.path.join(REPO_ROOT, "schemas", "V_zeta")
TIERS = ["stable", "draft", "deprecated"]
META_FILES = {"did_schema_meta.json", "CURIE_lookups_meta.json", "ndi_reserved_keys.json"}


def _load(path):
    with open(path) as f:
        return json.load(f)


META = _load(os.path.join(VZETA, "stable", "did_schema_meta.json"))
INDEX = _load(os.path.join(VZETA, "index.json"))


def _doc_files():
    out = []
    for tier in TIERS:
        for p in sorted(glob.glob(os.path.join(VZETA, tier, "*.json"))):
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
    d = _load(path)
    dc = d["document_class"]
    assert dc["class_name"] + ".json" == os.path.basename(path)
    assert dc["maturity_level"] == tier, f"{dc['class_name']} maturity != {tier}/ folder"


def test_index_agrees_with_disk():
    on_disk = set(RECORDS) | {f[:-5] for f in META_FILES}
    in_index = {e["class_name"] for e in INDEX["schemas"]}
    assert on_disk == in_index, f"index/disk drift: {on_disk ^ in_index}"
    assert INDEX["set_version"] == "V_zeta"


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


def test_spine_composes_onto_every_interaction():
    """Every subject_interaction leaf inherits the Brainstorm-I skeleton."""
    for name in RECORDS:
        if "subject_interaction" not in _chain(name):
            continue
        ft = _flat_field_types(name)
        deps = _flat_dep_names(name)
        assert "subject_id" in deps, f"{name} missing subject_id"
        assert "time_reference_#" in deps, f"{name} missing time_reference"
        assert ft.get("method") == "ontology_term", f"{name} missing spine method"
        assert ft.get("variable") == "ontology_term", f"{name} missing spine variable"
        assert ft.get("target_structure") == "ontology_term", f"{name} missing target_structure"


def test_element_id_is_optional_individuated_referent_on_spine():
    """Brainstorm I completes the referent set on the spine: subject_id is the
    whole specimen, target_structure the ontological KIND of locus, and
    element_id the specific individuated part / derived entity (an ndi element
    that is part of the subject but is neither a group nor an anatomical
    ontology term). It is an OPTIONAL dependency, not a class -- identity stays
    OFF the class (the EPM lesson)."""
    deps = {d["name"]: d for d in RECORDS["subject_interaction"][1]["depends_on"]}
    assert "element_id" in deps, "subject_interaction must offer element_id"
    assert deps["element_id"]["mustBeNonEmpty"] is False, "element_id must be optional"
    assert deps["element_id"]["must_refer_to_document_class"] == "element"
    assert deps["element_id"].get("multiple", False) is False, "element_id is single"
    # every interaction leaf (observation and manipulation) inherits it
    for name in RECORDS:
        if "subject_interaction" in _chain(name):
            assert "element_id" in _flat_dep_names(name), f"{name} missing element_id"


def test_session_relative_reference_has_no_redundant_session_edge():
    """session_id rides on base.session_id (every DID document carries it), so
    the ordinal anchor declares no session_id depends_on edge -- the redundant
    edge only produced discovery-mode reference-integrity orphans (the session
    document is not part of a corpus dump)."""
    assert "session_id" not in _flat_dep_names("session_relative_reference"), \
        "session_relative_reference should not declare a redundant session_id edge"


def test_shape_typed_scalar_leaves_present():
    """Brainstorm I names observation leaves by data-type (shape), not property."""
    for dim, vtype in {
        "mass": "mass", "length": "length", "duration": "duration",
        "volume": "volume", "temperature": "temperature", "pressure": "pressure",
        "frequency": "frequency", "voltage": "voltage", "current": "current",
        "concentration": "concentration", "count": "count", "score": "score",
    }.items():
        leaf = f"scalar_{dim}_observation"
        assert leaf in RECORDS, f"missing {leaf}"
        assert _flat_field_types(leaf).get("value") == vtype
        assert "observation" in _chain(leaf)


def test_no_brainstorm_e_property_leaves():
    """The E property-named observation tier is gone (superseded by I)."""
    for gone in ["body_weight_observation", "core_temperature_observation",
                 "developmental_stage_observation", "categorical_concept",
                 "subject_statement"]:
        assert gone not in RECORDS, f"{gone} should not exist in V_zeta"


def test_no_pure_identity_manipulation_classes():
    """A manipulation is a class only when it adds STRUCTURE; the pure-identity
    procedural_/environmental_manipulation classes fold into generic_manipulation."""
    for gone in ["procedural_manipulation", "environmental_manipulation"]:
        assert gone not in RECORDS, f"{gone} is pure-identity; must not exist"
    # the payload-free escape hatch exists and is a concrete manipulation leaf
    assert "generic_manipulation" in RECORDS
    assert "manipulation" in _chain("generic_manipulation")
    assert RECORDS["generic_manipulation"][1]["document_class"].get("abstract") is not True
    # biological_transfer earns its class via donor_id and re-parents onto manipulation
    assert RECORDS["biological_transfer"][1]["document_class"]["superclasses"] == \
        [{"class_name": "manipulation"}]
    assert "donor_id" in _flat_dep_names("biological_transfer")
    # shared prose lives on the abstract manipulation base (inherited by all leaves)
    assert _flat_field_types("generic_manipulation").get("notes") == "char"
    assert _flat_field_types("injection").get("notes") == "char"


def test_sample_time_retired():
    """Series timing lives in the shaped time_reference, not a sample_time array."""
    for name in ["scalar_observation", "scalar_manipulation"]:
        ft = _flat_field_types(name)
        assert "sample_time" not in ft, f"{name} still declares sample_time"
    tr = RECORDS["time_reference"][1]
    sampling = [f for f in tr["fields"] if f["name"] == "sampling"]
    assert sampling and sampling[0]["type"] == "structure"
