"""Tests that validate schema files against the DID meta-schema (JSON Schema Draft 7).

Parametrized across every active schema version (V_beta and V_gamma).
"""

import glob
import os

import jsonschema
import pytest

from conftest import load_json

# Files in each schemas/V_*/ directory that are NOT document-type schemas
# and therefore should not be validated against the meta-schema.
META_ONLY_FILES = {"did_schema_meta.json", "CURIE_lookups_meta.json"}


def schema_files_in(schemas_dir):
    """All document-type schema files in the flat version directory."""
    paths = glob.glob(os.path.join(schemas_dir, "*.json"))
    return [p for p in paths if os.path.basename(p) not in META_ONLY_FILES]


class TestMetaSchemaValidation:
    """Every schema file must pass validation against did_schema_meta.json."""

    def test_base_schema_passes(self, meta_schema, base_schema):
        jsonschema.validate(instance=base_schema, schema=meta_schema)

    def test_probe_location_schema_passes(self, meta_schema, probe_location_schema):
        jsonschema.validate(instance=probe_location_schema, schema=meta_schema)

    def test_all_schema_files_pass(self, meta_schema, schemas_dir):
        """Validate every document-type schema file against the meta-schema."""
        files = schema_files_in(schemas_dir)
        assert len(files) >= 2, (
            f"Expected at least base and probe_location schemas in {schemas_dir}"
        )
        for path in files:
            data = load_json(path)
            jsonschema.validate(instance=data, schema=meta_schema), (
                f"Schema file failed meta-validation: {path}"
            )

    def test_invalid_schema_missing_classname_fails(
        self, meta_schema, invalid_schema_missing_classname
    ):
        with pytest.raises(jsonschema.ValidationError) as exc_info:
            jsonschema.validate(
                instance=invalid_schema_missing_classname, schema=meta_schema
            )
        assert "classname" in str(exc_info.value)

    def test_invalid_schema_bad_type_fails(self, meta_schema, base_schema):
        """A schema with an unrecognized type string must fail meta-validation."""
        bad = dict(base_schema)
        bad["_fields"] = [dict(base_schema["_fields"][0])]
        bad["_fields"][0]["type"] = "nonexistent_type"
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=bad, schema=meta_schema)

    def test_invalid_schema_extra_top_level_key_fails(self, meta_schema, base_schema):
        """A schema with an unrecognized top-level key must fail."""
        bad = dict(base_schema)
        bad["extra_key"] = "should not be here"
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=bad, schema=meta_schema)

    def test_invalid_schema_bad_classname_pattern_fails(self, meta_schema, base_schema):
        """_classname must match the snake_case/identifier pattern."""
        bad = dict(base_schema)
        bad["_classname"] = "123_invalid"
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=bad, schema=meta_schema)

    def test_invalid_schema_bad_version_pattern_fails(self, meta_schema, base_schema):
        """_class_version must match semver pattern."""
        bad = dict(base_schema)
        bad["_class_version"] = "not.a.version"
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=bad, schema=meta_schema)

    def test_directory_schema_passes(self, meta_schema, directory_schema):
        """The directory document schema must pass meta-validation."""
        jsonschema.validate(instance=directory_schema, schema=meta_schema)

    def test_schema_without_file_key_passes(self, meta_schema):
        """A schema that omits _file entirely should pass (it is optional)."""
        minimal = {
            "_classname": "no_file_test",
            "_class_version": "1.0.0",
            "_maturity_level": "work_in_progress",
            "_superclasses": [],
            "_depends_on": [],
            "_fields": [],
        }
        jsonschema.validate(instance=minimal, schema=meta_schema)

    def test_schema_with_directory_key_passes(self, meta_schema):
        """A schema with a _directory array should pass."""
        with_dir = {
            "_classname": "dir_test",
            "_class_version": "1.0.0",
            "_maturity_level": "work_in_progress",
            "_superclasses": [],
            "_depends_on": [],
            "_directory": [
                {
                    "_name": "raw_data",
                    "_documentation": "Raw acquisition files.",
                }
            ],
            "_fields": [],
        }
        jsonschema.validate(instance=with_dir, schema=meta_schema)

    def test_invalid_directory_record_missing_name_fails(self, meta_schema):
        """A _directory entry without _name must fail."""
        bad = {
            "_classname": "bad_dir_test",
            "_class_version": "1.0.0",
            "_maturity_level": "work_in_progress",
            "_superclasses": [],
            "_depends_on": [],
            "_directory": [
                {"_documentation": "Missing _name."}
            ],
            "_fields": [],
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=bad, schema=meta_schema)

    def test_invalid_directory_record_extra_key_fails(self, meta_schema):
        """A _directory entry with extra keys must fail."""
        bad = {
            "_classname": "bad_dir_test",
            "_class_version": "1.0.0",
            "_maturity_level": "work_in_progress",
            "_superclasses": [],
            "_depends_on": [],
            "_directory": [
                {
                    "_name": "raw_data",
                    "_documentation": "Raw data.",
                    "_extra": "not allowed",
                }
            ],
            "_fields": [],
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=bad, schema=meta_schema)
