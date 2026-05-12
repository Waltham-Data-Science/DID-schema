"""Shared fixtures for DID schema tests.

The test suite runs every parametrized fixture against each active schema
version (currently V_beta and V_gamma). V_alpha is retained in the repo but
is no longer covered by the test suite.
"""

import json
import os

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMAS_ROOT = os.path.join(REPO_ROOT, "schemas")
FIXTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")

SCHEMA_VERSIONS = ["V_beta", "V_gamma"]


def load_json(path):
    """Load a JSON file and return the parsed object."""
    with open(path) as f:
        return json.load(f)


def is_v_gamma(schema):
    """V_gamma schema files have the nested document_class header; V_beta does not."""
    return "document_class" in schema


def schema_classname(schema):
    """Read a schema file's class_name regardless of wire shape.

    V_beta schema files: top-level "_classname".
    V_gamma schema files: nested "document_class.class_name".
    """
    if is_v_gamma(schema):
        return schema["document_class"]["class_name"]
    return schema["_classname"]


def schema_class_version(schema):
    if is_v_gamma(schema):
        return schema["document_class"]["class_version"]
    return schema["_class_version"]


def schema_superclasses(schema):
    if is_v_gamma(schema):
        return schema["document_class"]["superclasses"]
    return schema["_superclasses"]


def superclass_classname(entry):
    """Read a superclass reference's classname (V_beta `_classname` or V_gamma `class_name`)."""
    if "class_name" in entry:
        return entry["class_name"]
    return entry["_classname"]


# NDI-extension keys lost their underscore prefix in V_gamma; V_beta retains
# them. These accessors take the V_gamma (unprefixed) base name and read
# whichever form is present.

def schema_fields(schema):
    return schema["fields"] if is_v_gamma(schema) else schema["_fields"]


def schema_depends_on(schema):
    return schema.get("depends_on", []) if is_v_gamma(schema) else schema.get("_depends_on", [])


def schema_file_records(schema):
    return schema.get("file", []) if is_v_gamma(schema) else schema.get("_file", [])


def schema_directory_records(schema):
    return schema.get("directory", []) if is_v_gamma(schema) else schema.get("_directory", [])


def entry_get(entry, base_key, default=None):
    """Read an NDI-extension key from a field / dep / file / dir entry.

    `base_key` is the V_gamma form (no underscore prefix). V_beta is read
    with the underscore-prefixed form.
    """
    if base_key in entry:
        return entry[base_key]
    underscore_key = f"_{base_key}"
    if underscore_key in entry:
        return entry[underscore_key]
    return default


def schemas_dir_for(version):
    return os.path.join(SCHEMAS_ROOT, version)


def fixtures_dir_for(version):
    return os.path.join(FIXTURES_DIR, version)


@pytest.fixture(params=SCHEMA_VERSIONS)
def schema_version(request):
    return request.param


@pytest.fixture
def schemas_dir(schema_version):
    return schemas_dir_for(schema_version)


@pytest.fixture
def version_fixtures_dir(schema_version):
    return fixtures_dir_for(schema_version)


@pytest.fixture
def fixtures_dir():
    return FIXTURES_DIR


@pytest.fixture
def meta_schema(schemas_dir):
    return load_json(os.path.join(schemas_dir, "did_schema_meta.json"))


@pytest.fixture
def base_schema(schemas_dir):
    return load_json(os.path.join(schemas_dir, "base.json"))


@pytest.fixture
def probe_location_schema(schemas_dir):
    return load_json(os.path.join(schemas_dir, "probe_location.json"))


@pytest.fixture
def directory_schema(schemas_dir):
    return load_json(os.path.join(schemas_dir, "directory.json"))


@pytest.fixture
def valid_base_document(version_fixtures_dir):
    return load_json(os.path.join(version_fixtures_dir, "valid_base_document.json"))


@pytest.fixture
def invalid_base_document_missing_id(version_fixtures_dir):
    return load_json(
        os.path.join(version_fixtures_dir, "invalid_base_document_missing_id.json")
    )


@pytest.fixture
def invalid_base_document_bad_datestamp(version_fixtures_dir):
    return load_json(
        os.path.join(version_fixtures_dir, "invalid_base_document_bad_datestamp.json")
    )


@pytest.fixture
def valid_probe_location_document(version_fixtures_dir):
    return load_json(
        os.path.join(version_fixtures_dir, "valid_probe_location_document.json")
    )


@pytest.fixture
def invalid_schema_missing_classname():
    return load_json(os.path.join(FIXTURES_DIR, "invalid_schema_missing_classname.json"))
