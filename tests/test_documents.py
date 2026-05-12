"""Tests for document fixture validation against their schemas.

These tests validate document instances by checking field values against
the constraints and rules defined in the schema files. Parametrized across
every active schema version (V_beta and V_gamma).
"""

import os
import re

from conftest import (
    entry_get,
    load_json,
    schema_depends_on,
    schema_fields,
    schema_superclasses,
    superclass_classname,
)

TIMESTAMP_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$"
)
DID_UID_RE = re.compile(r"^[0-9a-fA-F_]{33,}$")
CURIE_RE = re.compile(r"^[a-z][a-z0-9_]*:[^\s:]+$")


def schema_path_for_classname(classname, schemas_dir):
    """Resolve a classname to its schema file under the flat layout."""
    return os.path.join(schemas_dir, f"{classname}.json")


def doc_metadata(doc):
    """Return (classname, depends_on_list, class_block_keys) for a document.

    Supports both wire shapes:
    - V_beta: top-level "document_class" with sub-key "classname"; top-level
      "depends_on" (no underscore).
    - V_gamma: top-level "document_class" with sub-key "class_name"; top-level
      "depends_on" (no underscore, post-rename). See "JSON Format: Document
      Instances" in V_gamma_SPEC.md.
    """
    header = doc["document_class"]
    if "class_name" in header:
        classname = header["class_name"]
    else:
        classname = header["classname"]
    depends_on = doc.get("depends_on", doc.get("_depends_on", []))
    reserved = {"document_class", "_depends_on", "depends_on"}
    block_keys = [k for k, v in doc.items() if k not in reserved and isinstance(v, dict)]
    return classname, depends_on, block_keys


def load_schema_for_document(doc, schemas_dir):
    """Load the schema file referenced by a document's class metadata."""
    classname, _, _ = doc_metadata(doc)
    return load_json(schema_path_for_classname(classname, schemas_dir))


def get_all_fields(schema, schemas_dir):
    """Recursively resolve superclass fields and return flattened field list.

    Uses each superclass's class_name (V_gamma) or _classname (V_beta) to
    locate its schema file in the flat layout; the schema-path entry inside
    the superclass reference is ignored for resolution purposes.
    """
    fields = []
    for superclass in schema_superclasses(schema):
        super_schema = load_json(
            schema_path_for_classname(superclass_classname(superclass), schemas_dir)
        )
        fields.extend(get_all_fields(super_schema, schemas_dir))
    fields.extend(schema_fields(schema))
    return fields


def validate_document(doc, schemas_dir):
    """Validate a document against its schema. Returns list of error strings."""
    schema = load_schema_for_document(doc, schemas_dir)
    all_fields = get_all_fields(schema, schemas_dir)
    errors = []

    # Build a map of classname -> field data blocks in the document.
    # Field values live under class-named keys (e.g. "base", "probe_location").
    _, _, block_keys = doc_metadata(doc)
    field_blocks = {k: doc[k] for k in block_keys}

    for field_def in all_fields:
        name = entry_get(field_def, "name")
        field_type = field_def["type"]

        value = None
        found = False
        for block_data in field_blocks.values():
            if name in block_data:
                value = block_data[name]
                found = True
                break

        if not found:
            errors.append(f"Field '{name}' not found in document")
            continue

        # mustBeNonEmpty check (null/empty string/empty list/empty dict).
        if entry_get(field_def, "mustBeNonEmpty", default=False):
            if value is None or value == "" or value == [] or value == {}:
                errors.append(
                    f"Field '{name}' must be non-empty but got: {value!r}"
                )
                continue

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
            constraints = entry_get(field_def, "constraints", default={})
            max_len = constraints.get("maxLength")
            if max_len is not None and len(value) > max_len:
                errors.append(
                    f"Field '{name}' exceeds maxLength {max_len}: length={len(value)}"
                )

        if field_type in ("integer", "double") and isinstance(value, (int, float)):
            constraints = entry_get(field_def, "constraints", default={})
            min_val = constraints.get("minimum")
            max_val = constraints.get("maximum")
            if min_val is not None and value < min_val:
                errors.append(f"Field '{name}' below minimum {min_val}: {value}")
            if max_val is not None and value > max_val:
                errors.append(f"Field '{name}' above maximum {max_val}: {value}")

        if field_type == "ontology_term" and value is not None:
            if not isinstance(value, dict):
                errors.append(
                    f"Field '{name}' must be an object for ontology_term, got: {value!r}"
                )
            else:
                if set(value.keys()) != {"node", "name"}:
                    errors.append(
                        f"Field '{name}' ontology_term must have exactly "
                        f"'node' and 'name' keys, got: {sorted(value.keys())}"
                    )
                else:
                    node = value["node"]
                    if not isinstance(node, str) or not CURIE_RE.match(node):
                        errors.append(
                            f"Field '{name}' ontology_term.node is not a valid "
                            f"CURIE: {node!r}"
                        )

    # Validate depends_on. Each runtime entry's role name is in "name"
    # (V_beta and V_gamma wire shapes; V_beta had "_name", but post-rename
    # V_gamma also uses "name").
    _, doc_depends_on, _ = doc_metadata(doc)
    doc_deps = {
        (d.get("name") or d.get("_name")): d.get("value", "")
        for d in doc_depends_on
    }
    for dep_def in schema_depends_on(schema):
        dep_name = entry_get(dep_def, "name")
        if entry_get(dep_def, "mustBeNonEmpty", default=False):
            dep_value = doc_deps.get(dep_name, "")
            if not dep_value:
                errors.append(f"Dependency '{dep_name}' must be non-empty")

    return errors


class TestValidDocuments:
    """Valid document fixtures must pass validation."""

    def test_valid_base_document(self, valid_base_document, schemas_dir):
        errors = validate_document(valid_base_document, schemas_dir)
        assert errors == [], f"Valid base document had errors: {errors}"

    def test_valid_probe_location_document(
        self, valid_probe_location_document, schemas_dir
    ):
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

    def test_bad_datestamp_fails(
        self, invalid_base_document_bad_datestamp, schemas_dir
    ):
        errors = validate_document(invalid_base_document_bad_datestamp, schemas_dir)
        assert len(errors) > 0, "Expected validation errors for bad datestamp"
        assert any("datestamp" in e for e in errors), (
            f"Expected error about 'datestamp', got: {errors}"
        )
