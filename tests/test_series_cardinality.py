"""Series-as-cardinality prototype tests (Brainstorm E, Part 2).

Exercises the prototype on `core_temperature_observation`:
- the schema declares `value` and `sample_time` as arrays (mustBeScalar: false)
  of typed composites (D1/D4), and
- the worked example document satisfies the element-aligned-length invariant
  `len(value) == len(sample_time)` (D3) — which JSON Schema cannot express on a
  single field, so it ships here as the consumer/tooling check.

See Series_As_Cardinality_Proposal.md for the design.
"""

import json
import os

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRAFT = os.path.join(REPO_ROOT, "schemas", "V_epsilon", "draft")
EXAMPLES = os.path.join(REPO_ROOT, "schemas", "V_epsilon", "examples")
EXAMPLE_DOC = os.path.join(EXAMPLES, "core_temperature_observation_series.json")


def _load(path):
    with open(path) as f:
        return json.load(f)


def _field(schema, name):
    for fld in schema.get("fields", []):
        if fld.get("name") == name:
            return fld
    return None


def check_series_lengths(doc, value_path=("core_temperature_observation", "value"),
                         time_path=("core_temperature_observation", "sample_time")):
    """Consumer/tooling check for D3: the per-sample arrays are element-aligned.

    Returns a list of error strings (empty == valid). This is the validator
    JSON Schema cannot express, because it spans two fields.
    """
    errors = []
    vblock, vname = value_path
    tblock, tname = time_path
    value = doc.get(vblock, {}).get(vname)
    sample_time = doc.get(tblock, {}).get(tname)
    if not isinstance(value, list):
        errors.append(f"{vblock}.{vname} must be an array (series-as-cardinality)")
    if not isinstance(sample_time, list):
        errors.append(f"{tblock}.{tname} must be an array (series-as-cardinality)")
    if isinstance(value, list) and isinstance(sample_time, list):
        if len(value) != len(sample_time):
            errors.append(
                f"len({vname})={len(value)} != len({tname})={len(sample_time)} "
                "(arrays must be element-aligned)"
            )
    return errors


class TestSeriesSchema:
    def test_value_is_array_of_temperature(self):
        schema = _load(os.path.join(DRAFT, "core_temperature_observation.json"))
        value = _field(schema, "value")
        assert value is not None, "core_temperature_observation must declare value"
        assert value["type"] == "temperature"
        assert value["mustBeScalar"] is False, "value must be an array (cardinality)"

    def test_sample_time_is_array_of_duration(self):
        schema = _load(os.path.join(DRAFT, "core_temperature_observation.json"))
        st = _field(schema, "sample_time")
        assert st is not None, "core_temperature_observation must declare sample_time"
        assert st["type"] == "duration"
        assert st["mustBeScalar"] is False, "sample_time must be an array (cardinality)"


class TestSeriesExampleDocument:
    def test_example_exists_and_parses(self):
        assert os.path.exists(EXAMPLE_DOC)
        _load(EXAMPLE_DOC)

    def test_example_is_array_of_structures(self):
        doc = _load(EXAMPLE_DOC)
        value = doc["core_temperature_observation"]["value"]
        assert isinstance(value, list) and len(value) >= 1
        for sample in value:
            assert isinstance(sample, dict) and "celsius" in sample, (
                "value must be an array OF COMPOSITES (structures), not a bare "
                "numeric matrix, so existential [*] search stays available (D4)"
            )

    def test_example_satisfies_length_invariant(self):
        doc = _load(EXAMPLE_DOC)
        assert check_series_lengths(doc) == []

    def test_length_mismatch_is_caught(self):
        doc = _load(EXAMPLE_DOC)
        doc["core_temperature_observation"]["sample_time"].pop()  # break alignment
        errors = check_series_lengths(doc)
        assert errors and "element-aligned" in errors[0]

    def test_single_reading_is_cardinality_one(self):
        """A spot reading is the length-1 case of the same class."""
        doc = _load(EXAMPLE_DOC)
        doc["core_temperature_observation"]["value"] = [{"celsius": 37.0}]
        doc["core_temperature_observation"]["sample_time"] = [{"seconds": 0}]
        assert check_series_lengths(doc) == []
