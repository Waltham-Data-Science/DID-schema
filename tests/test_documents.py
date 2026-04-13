"""Tests for document fixture validation against their schemas.

These tests validate document instances by checking field values against
the constraints and rules defined in the schema files. This replicates
the core validation logic that MATLAB/Python tooling would perform.
"""

import os
import re

import pytest

from conftest import SCHEMAS_DIR, load_json

TIMESTAMP_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$"
)
DID_UID_RE = re.compile(r"^[0-9a-fA-F_]{33,}$")


def resolve_schema_path(token_path, schemas_dir):
    """Replace $NDISCHEMAPATH token with the actual schemas directory."""
    return token_path.replace("$NDISCHEMAPATH", schemas_dir)


def load_schema_for_document(doc, schemas_dir):
    """Load the schema file referenced by a document's document_class."""
    schema_path = resolve_schema_path(doc["document_class"]["schema"], schemas_dir)
    return load_json(schema_path)


def get_all_fields(schema, schemas_dir):
    """Recursively resolve superclass fields and return flattened field list."""
    fields = []
    for superclass in schema.get("_superclasses", []):
        super_path = resolve_schema_path(superclass["_schema"], schemas_dir)
        super_schema = load_json(super_path)
        fields.extend(get_all_fields(super_schema, schemas_dir))
    fields.extend(schema["_fields"])
    return fields


def validate_document(doc, schemas_dir):
    """Validate a document against its schema. Returns list of error strings."""
    schema = load_schema_for_document(doc, schemas_dir)
    all_fields = get_all_fields(schema, schemas_dir)
    errors = []

    # Build a map of classname -> field data blocks in the document
    # The document stores field values under class-named keys (e.g., "base", "probe_location")
    field_blocks = {}
    for key, val in doc.items():
        if key not in ("document_class", "depends_on") and isinstance(val, dict):
            field_blocks[key] = val

    for field_def in all_fields:
        name = field_def["_name"]
        field_type = field_def["type"]

        # Find the value in the document's data blocks
        value = None
        found = False
        for block_name, block_data in field_blocks.items():
            if name in block_data:
                value = block_data[name]
                found = True
                break

        if not found:
            errors.append(f"Field '{name}' not found in document")
            continue

        # mustBeNonEmpty check
        if field_def.get("_mustBeNonEmpty", False):
            if value is None or value == "" or value == [] or value == {}:
                errors.append(
                    f"Field '{name}' must be non-empty but got: {value!r}"
                )
                continue

        # Type-specific validation
        if field_type == "timestamp" and isinstance(value, str) and value != "":
            if not TIMESTAMP_RE.match(value):
                errors.append(
                    f"Field '{name}' has invalid timestamp format: {value!r}"
                )

        if field_type == "did_uid" and isinstance(value, str) and value != "":
            if not DID_UID_RE.match(value):
                errors.append(
                    f"Field '{name}' has invalid DID UID format: {value!r}"
                )

        if field_type in ("char", "string") and isinstance(value, str):
            max_length = field_def.get("_constraints", {}).get("max_length")
            if max_length is not None and len(value) > max_length:
                errors.append(
                    f"Field '{name}' exceeds max_length {max_length}: length={len(value)}"
                )

        if field_type in ("integer", "double") and isinstance(value, (int, float)):
            constraints = field_def.get("_constraints", {})
            min_val = constraints.get("min")
            max_val = constraints.get("max")
            if min_val is not None and value < min_val:
                errors.append(f"Field '{name}' below minimum {min_val}: {value}")
            if max_val is not None and value > max_val:
                errors.append(f"Field '{name}' above maximum {max_val}: {value}")

    # Validate depends_on
    for dep_def in schema.get("_depends_on", []):
        dep_name = dep_def["_name"]
        doc_deps = {d["name"]: d.get("value", "") for d in doc.get("depends_on", [])}
        if dep_def.get("_mustBeNonEmpty", False):
            dep_value = doc_deps.get(dep_name, "")
            if not dep_value:
                errors.append(
                    f"Dependency '{dep_name}' must be non-empty"
                )

    return errors


class TestValidDocuments:
    """Valid document fixtures must pass validation."""

    def test_valid_base_document(self, valid_base_document, schemas_dir):
        errors = validate_document(valid_base_document, schemas_dir)
        assert errors == [], f"Valid base document had errors: {errors}"

    def test_valid_probe_location_document(self, valid_probe_location_document, schemas_dir):
        errors = validate_document(valid_probe_location_document, schemas_dir)
        assert errors == [], f"Valid probe_location document had errors: {errors}"


class TestInvalidDocuments:
    """Invalid document fixtures must fail validation with expected errors."""

    def test_missing_id_fails(self, invalid_base_document_missing_id, schemas_dir):
        errors = validate_document(invalid_base_document_missing_id, schemas_dir)
        assert len(errors) > 0, "Expected validation errors for missing id"
        assert any("id" in e and "non-empty" in e for e in errors), (
            f"Expected error about 'id' being non-empty, got: {errors}"
        )

    def test_bad_datestamp_fails(self, invalid_base_document_bad_datestamp, schemas_dir):
        errors = validate_document(invalid_base_document_bad_datestamp, schemas_dir)
        assert len(errors) > 0, "Expected validation errors for bad datestamp"
        assert any("datestamp" in e for e in errors), (
            f"Expected error about 'datestamp', got: {errors}"
        )
