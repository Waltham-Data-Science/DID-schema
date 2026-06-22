"""Series-as-cardinality tests (Brainstorm E, Part 2).

After the step-2 rollout, series-as-cardinality is a property of the SHAPE
MIXINS, not a single prototype class:
- every scalar shape mixin (`scalar_temperature`, `scalar_mass`, ...) declares
  `value` as an array of typed composites (mustBeScalar: false, D1/D4), and
- the `scalar_observation` / `scalar_manipulation` genera carry the parallel
  `sample_time` array.
So a concrete class like `core_temperature_observation` inherits the
cardinality form (its own `fields` are empty); a single reading is the length-1
case. The element-aligned-length invariant `len(value) == len(sample_time)`
(D3) is a consumer/tooling check (JSON Schema cannot express it on one field),
shipped here.

See Series_As_Cardinality_Proposal.md for the design.
"""

import json
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRAFT = os.path.join(REPO_ROOT, "schemas", "V_epsilon", "draft")
EXAMPLES = os.path.join(REPO_ROOT, "schemas", "V_epsilon", "examples")
EXAMPLE_DOC = os.path.join(EXAMPLES, "core_temperature_observation_series.json")

SCALAR_MIXINS = [
    "scalar_mass", "scalar_length", "scalar_duration", "scalar_volume",
    "scalar_temperature", "scalar_pressure", "scalar_frequency", "scalar_voltage",
    "scalar_current", "scalar_concentration", "scalar_count", "scalar_score",
    "generic_scalar",
]


def _load(path):
    with open(path) as f:
        return json.load(f)


def _field(schema, name):
    for fld in schema.get("fields", []):
        if fld.get("name") == name:
            return fld
    return None


def check_series_lengths(doc, value_path=("scalar_temperature", "value"),
                         time_path=("scalar_observation", "sample_time")):
    """Consumer/tooling check for D3: the per-sample arrays are element-aligned.

    Returns a list of error strings (empty == valid). This is the validator
    JSON Schema cannot express, because it spans two fields. sample_time is
    optional (a single reading may omit it); the length check applies only
    when it is present.
    """
    errors = []
    vblock, vname = value_path
    tblock, tname = time_path
    value = doc.get(vblock, {}).get(vname)
    sample_time = doc.get(tblock, {}).get(tname)
    if not isinstance(value, list):
        errors.append(f"{vblock}.{vname} must be an array (series-as-cardinality)")
    if sample_time is not None:
        if not isinstance(sample_time, list):
            errors.append(f"{tblock}.{tname} must be an array (series-as-cardinality)")
        elif isinstance(value, list) and len(value) != len(sample_time):
            errors.append(
                f"len({vname})={len(value)} != len({tname})={len(sample_time)} "
                "(arrays must be element-aligned)"
            )
    return errors


class TestSeriesSchema:
    def test_every_scalar_mixin_value_is_an_array(self):
        for m in SCALAR_MIXINS:
            schema = _load(os.path.join(DRAFT, m + ".json"))
            value = _field(schema, "value")
            assert value is not None, f"{m} must declare value"
            assert value["mustBeScalar"] is False, \
                f"{m}.value must be an array (series-as-cardinality)"

    def test_sample_time_is_array_of_duration_on_genus(self):
        for genus in ("scalar_observation", "scalar_manipulation"):
            schema = _load(os.path.join(DRAFT, genus + ".json"))
            st = _field(schema, "sample_time")
            assert st is not None, f"{genus} must declare sample_time"
            assert st["type"] == "duration"
            assert st["mustBeScalar"] is False, "sample_time must be an array"

    def test_concrete_temperature_class_inherits_the_shape(self):
        # The concrete property class no longer overrides value/sample_time;
        # it inherits the array form from scalar_temperature / scalar_observation.
        schema = _load(os.path.join(DRAFT, "core_temperature_observation.json"))
        assert _field(schema, "value") is None
        assert _field(schema, "sample_time") is None


class TestSeriesExampleDocument:
    def test_example_exists_and_parses(self):
        assert os.path.exists(EXAMPLE_DOC)
        _load(EXAMPLE_DOC)

    def test_example_is_array_of_structures(self):
        doc = _load(EXAMPLE_DOC)
        value = doc["scalar_temperature"]["value"]
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
        doc["scalar_observation"]["sample_time"].pop()  # break alignment
        errors = check_series_lengths(doc)
        assert errors and "element-aligned" in errors[0]

    def test_single_reading_is_cardinality_one(self):
        """A spot reading is the length-1 case of the same class."""
        doc = _load(EXAMPLE_DOC)
        doc["scalar_temperature"]["value"] = [{"celsius": 37.0}]
        doc["scalar_observation"]["sample_time"] = [{"seconds": 0}]
        assert check_series_lengths(doc) == []
