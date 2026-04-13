"""Tests for the structural correctness of schema files."""

import glob
import os
import re

import pytest

from conftest import SCHEMAS_DIR, load_json

VALID_TYPES = {
    "did_uid", "char", "string", "integer", "double",
    "matrix", "timestamp", "boolean", "structure",
}

FIELD_NAME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")


class TestBaseSchema:
    """Structural tests for the base schema."""

    def test_classname(self, base_schema):
        assert base_schema["_classname"] == "base"

    def test_version_is_semver(self, base_schema):
        assert SEMVER_RE.match(base_schema["_class_version"])

    def test_no_superclasses(self, base_schema):
        assert base_schema["_superclasses"] == []

    def test_has_four_fields(self, base_schema):
        assert len(base_schema["_fields"]) == 4

    def test_field_names(self, base_schema):
        names = [f["_name"] for f in base_schema["_fields"]]
        assert names == ["id", "session_id", "name", "datestamp"]

    def test_field_types_are_valid(self, base_schema):
        for field in base_schema["_fields"]:
            assert field["type"] in VALID_TYPES, (
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

    def test_ontology_is_object_or_null(self, base_schema):
        for field in base_schema["_fields"]:
            ont = field["_ontology"]
            if ont is not None:
                assert isinstance(ont, dict)
                assert "_namespace" in ont
                assert "_term" in ont
                assert "_uri" in ont


class TestProbeLocationSchema:
    """Structural tests for the probe_location schema."""

    def test_classname(self, probe_location_schema):
        assert probe_location_schema["_classname"] == "probe_location"

    def test_has_one_superclass(self, probe_location_schema):
        assert len(probe_location_schema["_superclasses"]) == 1
        assert probe_location_schema["_superclasses"][0]["_classname"] == "base"

    def test_superclass_schema_path_is_resolvable(self, probe_location_schema):
        """The superclass schema path should reference base/schema.json."""
        path = probe_location_schema["_superclasses"][0]["_schema"]
        assert path.endswith("base/schema.json")

    def test_has_two_own_fields(self, probe_location_schema):
        assert len(probe_location_schema["_fields"]) == 2

    def test_has_one_dependency(self, probe_location_schema):
        assert len(probe_location_schema["_depends_on"]) == 1
        dep = probe_location_schema["_depends_on"][0]
        assert dep["_name"] == "probe_id"
        assert dep["_mustBeNonEmpty"] is True

    def test_field_types_are_valid(self, probe_location_schema):
        for field in probe_location_schema["_fields"]:
            assert field["type"] in VALID_TYPES


class TestInheritanceResolution:
    """Test that superclass field flattening works correctly."""

    def test_probe_location_inherits_base_fields(self, base_schema, probe_location_schema):
        """probe_location's all_fields should be base fields + own fields."""
        all_fields = base_schema["_fields"] + probe_location_schema["_fields"]
        assert len(all_fields) == 6

        names = [f["_name"] for f in all_fields]
        # base fields come first
        assert names[:4] == ["id", "session_id", "name", "datestamp"]
        # then own fields
        assert "ontology_name" in names
        # Note: "name" appears in both base and probe_location, which is a
        # known duplication in the current schema design

    def test_no_superclass_for_base(self, base_schema):
        """base has no superclasses, so its all_fields equals its fields."""
        assert base_schema["_superclasses"] == []


class TestAllSchemaFilesConsistency:
    """Cross-cutting tests across all schema files in the repo."""

    def _get_all_schemas(self):
        paths = glob.glob(os.path.join(SCHEMAS_DIR, "**", "schema.json"), recursive=True)
        return [(p, load_json(p)) for p in paths]

    def test_all_classnames_are_unique(self):
        schemas = self._get_all_schemas()
        classnames = [s["_classname"] for _, s in schemas]
        assert len(classnames) == len(set(classnames)), (
            f"Duplicate classnames found: {classnames}"
        )

    def test_all_versions_are_semver(self):
        for path, schema in self._get_all_schemas():
            assert SEMVER_RE.match(schema["_class_version"]), (
                f"{path}: _class_version '{schema['_class_version']}' is not valid semver"
            )

    def test_all_field_types_are_valid(self):
        for path, schema in self._get_all_schemas():
            for field in schema["_fields"]:
                assert field["type"] in VALID_TYPES, (
                    f"{path}: field '{field['_name']}' has invalid type '{field['type']}'"
                )

    def test_file_and_directory_names_do_not_collide(self):
        """_file and _directory record names must not overlap within a schema."""
        for path, schema in self._get_all_schemas():
            file_names = {r["_name"] for r in schema.get("_file", [])}
            dir_names = {r["_name"] for r in schema.get("_directory", [])}
            overlap = file_names & dir_names
            assert not overlap, (
                f"{path}: _file and _directory share names: {overlap}"
            )


class TestDirectorySchema:
    """Structural tests for the directory document schema."""

    def test_classname(self, directory_schema):
        assert directory_schema["_classname"] == "directory"

    def test_extends_base(self, directory_schema):
        assert len(directory_schema["_superclasses"]) == 1
        assert directory_schema["_superclasses"][0]["_classname"] == "base"

    def test_has_parent_doc_dependency(self, directory_schema):
        dep_names = [d["_name"] for d in directory_schema["_depends_on"]]
        assert "parent_doc_id" in dep_names
        parent_dep = next(d for d in directory_schema["_depends_on"] if d["_name"] == "parent_doc_id")
        assert parent_dep["_mustBeNonEmpty"] is True

    def test_has_parent_directory_dependency(self, directory_schema):
        dep_names = [d["_name"] for d in directory_schema["_depends_on"]]
        assert "parent_directory_id" in dep_names
        parent_dir_dep = next(d for d in directory_schema["_depends_on"] if d["_name"] == "parent_directory_id")
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
        dirname_field = next(f for f in directory_schema["_fields"] if f["_name"] == "dirname")
        assert dirname_field["_mustBeNonEmpty"] is True

    def test_directory_role_may_be_empty(self, directory_schema):
        role_field = next(f for f in directory_schema["_fields"] if f["_name"] == "directory_role")
        assert role_field["_mustBeNonEmpty"] is False

    def test_manifest_format_default_is_jsonlines(self, directory_schema):
        fmt_field = next(f for f in directory_schema["_fields"] if f["_name"] == "manifest_format")
        assert fmt_field["_default_value"] == "jsonlines"
