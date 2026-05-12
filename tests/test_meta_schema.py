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
META_ONLY_FILES = {"did_schema_meta.json", "CURIE_lookups_meta.json", "ndi_reserved_keys.json"}


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
        msg = str(exc_info.value)
        # V_beta reports missing "_classname"; V_gamma reports missing
        # "document_class". Either is acceptable.
        assert "_classname" in msg or "document_class" in msg

    def test_invalid_schema_bad_type_fails(self, meta_schema, base_schema, schema_version):
        """A schema with an unrecognized type string must fail meta-validation."""
        import copy
        bad = copy.deepcopy(base_schema)
        fields_key = "fields" if schema_version == "V_gamma" else "_fields"
        bad[fields_key][0]["type"] = "nonexistent_type"
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=bad, schema=meta_schema)

    def test_invalid_schema_extra_top_level_key_fails(self, meta_schema, base_schema):
        """A schema with an unrecognized top-level key must fail."""
        bad = dict(base_schema)
        bad["extra_key"] = "should not be here"
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=bad, schema=meta_schema)

    def test_invalid_schema_bad_classname_pattern_fails(
        self, meta_schema, base_schema, schema_version
    ):
        """class_name must match the snake_case/identifier pattern."""
        import copy
        bad = copy.deepcopy(base_schema)
        if schema_version == "V_gamma":
            bad["document_class"]["class_name"] = "123_invalid"
        else:
            bad["_classname"] = "123_invalid"
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=bad, schema=meta_schema)

    def test_invalid_schema_bad_version_pattern_fails(
        self, meta_schema, base_schema, schema_version
    ):
        """class_version must match semver pattern."""
        import copy
        bad = copy.deepcopy(base_schema)
        if schema_version == "V_gamma":
            bad["document_class"]["class_version"] = "not.a.version"
        else:
            bad["_class_version"] = "not.a.version"
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=bad, schema=meta_schema)

    def test_directory_schema_passes(self, meta_schema, directory_schema):
        """The directory document schema must pass meta-validation."""
        jsonschema.validate(instance=directory_schema, schema=meta_schema)

    def test_schema_without_file_key_passes(self, meta_schema, schema_version):
        """A schema that omits the file array entirely should pass (it is optional)."""
        minimal = _minimal_schema(schema_version, "no_file_test")
        jsonschema.validate(instance=minimal, schema=meta_schema)

    def test_schema_with_directory_key_passes(self, meta_schema, schema_version):
        """A schema with a directory array should pass."""
        with_dir = _minimal_schema(schema_version, "dir_test")
        keys = _key_names(schema_version)
        with_dir[keys["directory"]] = [
            {
                keys["name"]: "raw_data",
                keys["documentation"]: "Raw acquisition files.",
            }
        ]
        jsonschema.validate(instance=with_dir, schema=meta_schema)

    def test_invalid_directory_record_missing_name_fails(
        self, meta_schema, schema_version
    ):
        """A directory entry without a name must fail."""
        bad = _minimal_schema(schema_version, "bad_dir_test")
        keys = _key_names(schema_version)
        bad[keys["directory"]] = [{keys["documentation"]: "Missing name."}]
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=bad, schema=meta_schema)

    def test_invalid_directory_record_extra_key_fails(
        self, meta_schema, schema_version
    ):
        """A directory entry with extra keys must fail."""
        bad = _minimal_schema(schema_version, "bad_dir_test")
        keys = _key_names(schema_version)
        bad[keys["directory"]] = [
            {
                keys["name"]: "raw_data",
                keys["documentation"]: "Raw data.",
                "_extra": "not allowed",
            }
        ]
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=bad, schema=meta_schema)


def _key_names(version):
    """Return the wire-shape key names for NDI-extension keys in a given version.

    V_gamma drops the V_beta underscore prefix on every NDI-extension key.
    """
    if version == "V_gamma":
        return {
            "maturity_level": "maturity_level",
            "depends_on": "depends_on",
            "fields": "fields",
            "file": "file",
            "directory": "directory",
            "name": "name",
            "documentation": "documentation",
        }
    return {
        "maturity_level": "_maturity_level",
        "depends_on": "_depends_on",
        "fields": "_fields",
        "file": "_file",
        "directory": "_directory",
        "name": "_name",
        "documentation": "_documentation",
    }


def _minimal_schema(version, class_name):
    """Build a minimal valid schema in the wire shape for the given version."""
    keys = _key_names(version)
    if version == "V_gamma":
        return {
            "document_class": {
                "class_name": class_name,
                "class_version": "1.0.0",
                "superclasses": [],
                keys["maturity_level"]: "work_in_progress",
            },
            keys["depends_on"]: [],
            keys["fields"]: [],
        }
    return {
        "_classname": class_name,
        "_class_version": "1.0.0",
        keys["maturity_level"]: "work_in_progress",
        "_superclasses": [],
        keys["depends_on"]: [],
        keys["fields"]: [],
    }
