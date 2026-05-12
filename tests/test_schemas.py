"""Tests for the structural correctness of schema files.

Parametrized across every active schema version (V_beta and V_gamma).
"""

import glob
import os
import re

from conftest import (
    load_json,
    schema_class_version,
    schema_classname,
    schema_superclasses,
    superclass_classname,
)

# V_beta type set: the primitives.
VALID_TYPES_BASE = {
    "did_uid", "char", "string", "integer", "double",
    "matrix", "timestamp", "boolean", "structure",
}

# V_gamma adds named composite types: the SI-dimensioned family (duration,
# volume, mass, length, voltage, current, frequency) plus ontology_term.
VALID_TYPES_BY_VERSION = {
    "V_beta":  VALID_TYPES_BASE,
    "V_gamma": VALID_TYPES_BASE | {
        "duration", "volume", "mass", "length", "voltage", "current",
        "frequency", "ontology_term",
    },
}

# V_gamma refactored four schemas into ontology_term fields, bumping their
# _class_version from 1.0.0 to 2.0.0. probe_location is one of them.
PROBE_LOCATION_VERSION = {
    "V_beta":  "1.0.0",
    "V_gamma": "2.0.0",
}

# probe_location field layout per version.
PROBE_LOCATION_FIELDS = {
    "V_beta":  {"names": {"ontology_name", "name"},
                "ontology_name_type": "char"},
    "V_gamma": {"names": {"location"},
                "ontology_name_type": None},
}

META_ONLY_FILES = {"did_schema_meta.json", "CURIE_lookups_meta.json"}

FIELD_NAME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")


def all_schema_files(schemas_dir):
    """All document-type schema files in the flat version directory."""
    paths = glob.glob(os.path.join(schemas_dir, "*.json"))
    return [p for p in paths if os.path.basename(p) not in META_ONLY_FILES]


class TestBaseSchema:
    """Structural tests for the base schema. Applies to every version."""

    def test_classname(self, base_schema):
        assert schema_classname(base_schema) == "base"

    def test_version_is_semver(self, base_schema):
        assert SEMVER_RE.match(schema_class_version(base_schema))

    def test_no_superclasses(self, base_schema):
        assert schema_superclasses(base_schema) == []

    def test_has_four_fields(self, base_schema):
        assert len(base_schema["_fields"]) == 4

    def test_field_names(self, base_schema):
        names = [f["_name"] for f in base_schema["_fields"]]
        assert names == ["id", "session_id", "name", "datestamp"]

    def test_field_types_are_valid(self, base_schema, schema_version):
        valid = VALID_TYPES_BY_VERSION[schema_version]
        for field in base_schema["_fields"]:
            assert field["type"] in valid, (
                f"Field '{field['_name']}' has invalid type '{field['type']}'"
            )

    def test_all_field_names_match_pattern(self, base_schema):
        for field in base_schema["_fields"]:
            assert FIELD_NAME_RE.match(field["_name"]), (
                f"Field name '{field['_name']}' does not match naming pattern"
            )

    def test_required_field_keys_present(self, base_schema):
        required_keys = {
            "_name", "type", "_blank_value", "_default_value",
            "_mustBeNonEmpty", "_mustBeScalar", "_mustNotHaveNaN",
            "_queryable", "_ontology", "_documentation", "_constraints",
        }
        for field in base_schema["_fields"]:
            missing = required_keys - set(field.keys())
            assert not missing, (
                f"Field '{field['_name']}' missing keys: {missing}"
            )

    def test_ontology_is_object_or_null(self, base_schema, schema_version):
        """Ontology annotation shape differs by version.

        V_beta uses {_namespace, _term, _name, _uri}; V_gamma uses {_node, _name}.
        """
        if schema_version == "V_beta":
            expected_keys = {"_namespace", "_term", "_name", "_uri"}
        else:
            expected_keys = {"_node", "_name"}
        for field in base_schema["_fields"]:
            ont = field["_ontology"]
            if ont is not None:
                assert isinstance(ont, dict)
                assert set(ont.keys()) == expected_keys, (
                    f"Field '{field['_name']}' ontology has keys "
                    f"{set(ont.keys())}, expected {expected_keys}"
                )


class TestProbeLocationSchema:
    """Structural tests for the probe_location schema."""

    def test_classname(self, probe_location_schema):
        assert schema_classname(probe_location_schema) == "probe_location"

    def test_class_version(self, probe_location_schema, schema_version):
        assert (
            schema_class_version(probe_location_schema)
            == PROBE_LOCATION_VERSION[schema_version]
        )

    def test_has_one_superclass(self, probe_location_schema):
        supers = schema_superclasses(probe_location_schema)
        assert len(supers) == 1
        assert superclass_classname(supers[0]) == "base"

    def test_superclass_reference_points_to_base(self, probe_location_schema):
        """The superclass _schema reference should mention the base schema."""
        path = schema_superclasses(probe_location_schema)[0]["_schema"]
        assert "base" in path and path.endswith(".json")

    def test_field_names(self, probe_location_schema, schema_version):
        names = {f["_name"] for f in probe_location_schema["_fields"]}
        assert names == PROBE_LOCATION_FIELDS[schema_version]["names"]

    def test_has_one_dependency(self, probe_location_schema):
        assert len(probe_location_schema["_depends_on"]) == 1
        dep = probe_location_schema["_depends_on"][0]
        assert dep["_name"] == "probe_id"
        assert dep["_mustBeNonEmpty"] is True

    def test_field_types_are_valid(self, probe_location_schema, schema_version):
        valid = VALID_TYPES_BY_VERSION[schema_version]
        for field in probe_location_schema["_fields"]:
            assert field["type"] in valid


class TestInheritanceResolution:
    """Test that superclass field flattening works correctly."""

    def test_probe_location_inherits_base_fields(
        self, base_schema, probe_location_schema, schema_version
    ):
        """probe_location's full field list is base fields + own fields."""
        base_names = [f["_name"] for f in base_schema["_fields"]]
        own_names = [f["_name"] for f in probe_location_schema["_fields"]]
        assert base_names[:4] == ["id", "session_id", "name", "datestamp"]
        expected_own = PROBE_LOCATION_FIELDS[schema_version]["names"]
        assert set(own_names) == expected_own

    def test_no_superclass_for_base(self, base_schema):
        """base has no superclasses."""
        assert schema_superclasses(base_schema) == []


class TestAllSchemaFilesConsistency:
    """Cross-cutting tests across all schema files in a given version."""

    def test_all_classnames_are_unique(self, schemas_dir):
        paths = all_schema_files(schemas_dir)
        classnames = [schema_classname(load_json(p)) for p in paths]
        assert len(classnames) == len(set(classnames)), (
            f"Duplicate classnames found in {schemas_dir}: {classnames}"
        )

    def test_all_versions_are_semver(self, schemas_dir):
        for path in all_schema_files(schemas_dir):
            schema = load_json(path)
            version = schema_class_version(schema)
            assert SEMVER_RE.match(version), (
                f"{path}: class_version '{version}' is not valid semver"
            )

    def test_all_field_types_are_valid(self, schemas_dir, schema_version):
        valid = VALID_TYPES_BY_VERSION[schema_version]
        for path in all_schema_files(schemas_dir):
            schema = load_json(path)
            for field in schema["_fields"]:
                assert field["type"] in valid, (
                    f"{path}: field '{field['_name']}' has invalid type "
                    f"'{field['type']}'"
                )

    def test_file_and_directory_names_do_not_collide(self, schemas_dir):
        """_file and _directory record names must not overlap within a schema."""
        for path in all_schema_files(schemas_dir):
            schema = load_json(path)
            file_names = {r["_name"] for r in schema.get("_file", [])}
            dir_names = {r["_name"] for r in schema.get("_directory", [])}
            overlap = file_names & dir_names
            assert not overlap, (
                f"{path}: _file and _directory share names: {overlap}"
            )


class TestDirectorySchema:
    """Structural tests for the directory document schema."""

    def test_classname(self, directory_schema):
        assert schema_classname(directory_schema) == "directory"

    def test_extends_base(self, directory_schema):
        supers = schema_superclasses(directory_schema)
        assert len(supers) == 1
        assert superclass_classname(supers[0]) == "base"

    def test_has_parent_doc_dependency(self, directory_schema):
        dep_names = [d["_name"] for d in directory_schema["_depends_on"]]
        assert "parent_doc_id" in dep_names
        parent_dep = next(
            d for d in directory_schema["_depends_on"] if d["_name"] == "parent_doc_id"
        )
        assert parent_dep["_mustBeNonEmpty"] is True

    def test_has_parent_directory_dependency(self, directory_schema):
        dep_names = [d["_name"] for d in directory_schema["_depends_on"]]
        assert "parent_directory_id" in dep_names
        parent_dir_dep = next(
            d for d in directory_schema["_depends_on"]
            if d["_name"] == "parent_directory_id"
        )
        assert parent_dir_dep["_mustBeNonEmpty"] is False

    def test_has_manifest_file(self, directory_schema):
        file_names = [f["_name"] for f in directory_schema.get("_file", [])]
        assert "manifest_file" in file_names

    def test_has_expected_fields(self, directory_schema):
        field_names = [f["_name"] for f in directory_schema["_fields"]]
        assert "dirname" in field_names
        assert "directory_role" in field_names
        assert "num_entries" in field_names
        assert "manifest_format" in field_names

    def test_dirname_must_be_non_empty(self, directory_schema):
        dirname_field = next(
            f for f in directory_schema["_fields"] if f["_name"] == "dirname"
        )
        assert dirname_field["_mustBeNonEmpty"] is True

    def test_directory_role_may_be_empty(self, directory_schema):
        role_field = next(
            f for f in directory_schema["_fields"] if f["_name"] == "directory_role"
        )
        assert role_field["_mustBeNonEmpty"] is False

    def test_manifest_format_default_is_jsonlines(self, directory_schema):
        fmt_field = next(
            f for f in directory_schema["_fields"] if f["_name"] == "manifest_format"
        )
        assert fmt_field["_default_value"] == "jsonlines"
