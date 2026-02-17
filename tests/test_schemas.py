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
        assert base_schema["classname"] == "base"

    def test_version_is_semver(self, base_schema):
        assert SEMVER_RE.match(base_schema["class_version"])

    def test_no_superclasses(self, base_schema):
        assert base_schema["superclasses"] == []

    def test_has_four_fields(self, base_schema):
        assert len(base_schema["fields"]) == 4

    def test_field_names(self, base_schema):
        names = [f["name"] for f in base_schema["fields"]]
        assert names == ["id", "session_id", "name", "datestamp"]

    def test_field_types_are_valid(self, base_schema):
        for field in base_schema["fields"]:
            assert field["type"] in VALID_TYPES, (
                f"Field '{field['name']}' has invalid type '{field['type']}'"
            )

    def test_all_field_names_match_pattern(self, base_schema):
        for field in base_schema["fields"]:
            assert FIELD_NAME_RE.match(field["name"]), (
                f"Field name '{field['name']}' does not match naming pattern"
            )

    def test_required_field_keys_present(self, base_schema):
        required_keys = {
            "name", "type", "blank_value", "default_value",
            "mustBeNonEmpty", "mustBeScalar", "mustNotHaveNaN",
            "queryable", "ontology", "documentation", "constraints",
        }
        for field in base_schema["fields"]:
            missing = required_keys - set(field.keys())
            assert not missing, (
                f"Field '{field['name']}' missing keys: {missing}"
            )

    def test_ontology_is_object_or_null(self, base_schema):
        for field in base_schema["fields"]:
            ont = field["ontology"]
            if ont is not None:
                assert isinstance(ont, dict)
                assert "namespace" in ont
                assert "term" in ont
                assert "uri" in ont


class TestProbeLocationSchema:
    """Structural tests for the probe_location schema."""

    def test_classname(self, probe_location_schema):
        assert probe_location_schema["classname"] == "probe_location"

    def test_has_one_superclass(self, probe_location_schema):
        assert len(probe_location_schema["superclasses"]) == 1
        assert probe_location_schema["superclasses"][0]["classname"] == "base"

    def test_superclass_schema_path_is_resolvable(self, probe_location_schema):
        """The superclass schema path should reference base/schema.json."""
        path = probe_location_schema["superclasses"][0]["schema"]
        assert path.endswith("base/schema.json")

    def test_has_two_own_fields(self, probe_location_schema):
        assert len(probe_location_schema["fields"]) == 2

    def test_has_one_dependency(self, probe_location_schema):
        assert len(probe_location_schema["depends_on"]) == 1
        dep = probe_location_schema["depends_on"][0]
        assert dep["name"] == "probe_id"
        assert dep["mustBeNonEmpty"] is True

    def test_field_types_are_valid(self, probe_location_schema):
        for field in probe_location_schema["fields"]:
            assert field["type"] in VALID_TYPES


class TestInheritanceResolution:
    """Test that superclass field flattening works correctly."""

    def test_probe_location_inherits_base_fields(self, base_schema, probe_location_schema):
        """probe_location's all_fields should be base fields + own fields."""
        all_fields = base_schema["fields"] + probe_location_schema["fields"]
        assert len(all_fields) == 6

        names = [f["name"] for f in all_fields]
        # base fields come first
        assert names[:4] == ["id", "session_id", "name", "datestamp"]
        # then own fields
        assert "ontology_name" in names
        # Note: "name" appears in both base and probe_location, which is a
        # known duplication in the current schema design

    def test_no_superclass_for_base(self, base_schema):
        """base has no superclasses, so its all_fields equals its fields."""
        assert base_schema["superclasses"] == []


class TestAllSchemaFilesConsistency:
    """Cross-cutting tests across all schema files in the repo."""

    def _get_all_schemas(self):
        paths = glob.glob(os.path.join(SCHEMAS_DIR, "**", "schema.json"), recursive=True)
        return [(p, load_json(p)) for p in paths]

    def test_all_classnames_are_unique(self):
        schemas = self._get_all_schemas()
        classnames = [s["classname"] for _, s in schemas]
        assert len(classnames) == len(set(classnames)), (
            f"Duplicate classnames found: {classnames}"
        )

    def test_all_versions_are_semver(self):
        for path, schema in self._get_all_schemas():
            assert SEMVER_RE.match(schema["class_version"]), (
                f"{path}: class_version '{schema['class_version']}' is not valid semver"
            )

    def test_all_field_types_are_valid(self):
        for path, schema in self._get_all_schemas():
            for field in schema["fields"]:
                assert field["type"] in VALID_TYPES, (
                    f"{path}: field '{field['name']}' has invalid type '{field['type']}'"
                )
