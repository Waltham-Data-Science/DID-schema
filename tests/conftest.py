"""Shared fixtures for DID schema tests."""

import json
import os

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMAS_DIR = os.path.join(REPO_ROOT, "schemas")
FIXTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


def load_json(path):
    """Load a JSON file and return the parsed object."""
    with open(path) as f:
        return json.load(f)


@pytest.fixture
def schemas_dir():
    return SCHEMAS_DIR


@pytest.fixture
def fixtures_dir():
    return FIXTURES_DIR


@pytest.fixture
def meta_schema():
    return load_json(os.path.join(SCHEMAS_DIR, "meta", "did_schema_meta.json"))


@pytest.fixture
def base_schema():
    return load_json(os.path.join(SCHEMAS_DIR, "base", "schema.json"))


@pytest.fixture
def probe_location_schema():
    return load_json(os.path.join(SCHEMAS_DIR, "probe", "probe_location", "schema.json"))



@pytest.fixture
def valid_base_document():
    return load_json(os.path.join(FIXTURES_DIR, "valid_base_document.json"))


@pytest.fixture
def invalid_base_document_missing_id():
    return load_json(os.path.join(FIXTURES_DIR, "invalid_base_document_missing_id.json"))


@pytest.fixture
def invalid_base_document_bad_datestamp():
    return load_json(os.path.join(FIXTURES_DIR, "invalid_base_document_bad_datestamp.json"))


@pytest.fixture
def valid_probe_location_document():
    return load_json(os.path.join(FIXTURES_DIR, "valid_probe_location_document.json"))


@pytest.fixture
def invalid_schema_missing_classname():
    return load_json(os.path.join(FIXTURES_DIR, "invalid_schema_missing_classname.json"))
