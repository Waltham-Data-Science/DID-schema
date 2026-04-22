"""Tests for the V_beta minischema/profile mechanism and new field types.

These tests are self-contained: they resolve their own paths and do not rely
on the pre-existing fixtures infrastructure (which predates the V_beta flat
layout and is known-stale).

Covered:
- did_schema_meta.json is a valid Draft 7 schema.
- profile_meta.json is a valid Draft 7 schema.
- The new treatment.json validates against did_schema_meta.json.
- The canonical virus_injection profile validates against profile_meta.json.
- The type enum accepts ontology, quantity, relative_quantity.
- _shape_from_minischema: true exempts a structure field from needing _fields.
- _shape_from_minischema: omitted or false still requires _fields on structure.
- Retired schemas (treatment_drug, virus_injection) are absent.
- profile_meta.json enforces canonical_unit and canonical_unit_label on quantity.
- profile_meta.json enforces reference on relative_quantity.
- profile_meta.json forbids canonical_unit on ontology type.
"""

import json
import os

import jsonschema
import pytest


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V_BETA = os.path.join(REPO_ROOT, "schemas", "V_beta")
PROFILES = os.path.join(V_BETA, "profiles")


def load(*parts):
    with open(os.path.join(*parts)) as f:
        return json.load(f)


@pytest.fixture
def did_meta():
    return load(V_BETA, "did_schema_meta.json")


@pytest.fixture
def profile_meta():
    return load(V_BETA, "profile_meta.json")


@pytest.fixture
def minimal_schema():
    """A minimal valid schema file with one char field; mutate for negative tests."""
    return {
        "_classname": "mini_test",
        "_class_version": "1.0.0",
        "_maturity_level": "work_in_progress",
        "_superclasses": [],
        "_depends_on": [],
        "_fields": [
            {
                "_name": "note",
                "type": "char",
                "_blank_value": "",
                "_default_value": "",
                "_mustBeNonEmpty": False,
                "_mustBeScalar": True,
                "_mustNotHaveNaN": False,
                "_queryable": False,
                "_ontology": None,
                "_documentation": "A note.",
                "_constraints": {},
            }
        ],
    }


def _field(type_, **overrides):
    """Build a minimal field definition with all required keys."""
    base = {
        "_name": "f",
        "type": type_,
        "_blank_value": None,
        "_default_value": None,
        "_mustBeNonEmpty": False,
        "_mustBeScalar": True,
        "_mustNotHaveNaN": False,
        "_queryable": False,
        "_ontology": None,
        "_documentation": "test",
        "_constraints": {},
    }
    base.update(overrides)
    return base


class TestMetaSchemasAreValidDraft7:
    def test_did_schema_meta_is_valid(self, did_meta):
        jsonschema.Draft7Validator.check_schema(did_meta)

    def test_profile_meta_is_valid(self, profile_meta):
        jsonschema.Draft7Validator.check_schema(profile_meta)


class TestTreatmentSchema:
    def test_treatment_validates(self, did_meta):
        treatment = load(V_BETA, "treatment.json")
        jsonschema.validate(instance=treatment, schema=did_meta)

    def test_treatment_manipulation_delegates_shape(self):
        treatment = load(V_BETA, "treatment.json")
        manip = next(
            f for f in treatment["_fields"] if f["_name"] == "manipulation"
        )
        assert manip["type"] == "structure"
        assert manip.get("_shape_from_minischema") is True
        assert "_fields" not in manip  # delegated; no inline shape


class TestRetiredSchemas:
    def test_treatment_drug_removed(self):
        assert not os.path.exists(os.path.join(V_BETA, "treatment_drug.json"))

    def test_virus_injection_removed(self):
        assert not os.path.exists(os.path.join(V_BETA, "virus_injection.json"))

    def test_stimulus_bath_retained(self):
        """stimulus_bath is not a treatment; it should remain untouched."""
        assert os.path.exists(os.path.join(V_BETA, "stimulus_bath.json"))


class TestVirusInjectionProfile:
    def test_validates_against_profile_meta(self, profile_meta):
        prof = load(PROFILES, "virus_injection.json")
        jsonschema.validate(instance=prof, schema=profile_meta)

    def test_expected_required_fields_present(self):
        prof = load(PROFILES, "virus_injection.json")
        names = [f["_name"] for f in prof["_fields"]]
        required_by_mustBeNonEmpty = [
            f["_name"] for f in prof["_fields"] if f["_mustBeNonEmpty"]
        ]
        assert "virus_construct" in required_by_mustBeNonEmpty
        assert "serotype" in required_by_mustBeNonEmpty
        assert "volume" in required_by_mustBeNonEmpty
        assert "titer" in required_by_mustBeNonEmpty
        assert "onset" in required_by_mustBeNonEmpty
        assert "injection_rate" in names  # optional
        assert "promoter" in names  # optional

    def test_volume_is_quantity_with_nl(self):
        prof = load(PROFILES, "virus_injection.json")
        volume = next(f for f in prof["_fields"] if f["_name"] == "volume")
        assert volume["type"] == "quantity"
        assert volume["_constraints"]["canonical_unit_label"] == "nl"
        assert volume["_constraints"]["canonical_unit"]["_namespace"] == "uo"

    def test_titer_is_quantity_with_gc_per_ml(self):
        prof = load(PROFILES, "virus_injection.json")
        titer = next(f for f in prof["_fields"] if f["_name"] == "titer")
        assert titer["type"] == "quantity"
        assert titer["_constraints"]["canonical_unit_label"] == "gc_per_ml"

    def test_onset_is_relative_quantity_with_reference(self):
        prof = load(PROFILES, "virus_injection.json")
        onset = next(f for f in prof["_fields"] if f["_name"] == "onset")
        assert onset["type"] == "relative_quantity"
        assert onset["_constraints"]["canonical_unit_label"] == "day"
        assert onset["_constraints"]["reference"] == "session_start"

    def test_serotype_has_descendant_of_constraint(self):
        prof = load(PROFILES, "virus_injection.json")
        serotype = next(f for f in prof["_fields"] if f["_name"] == "serotype")
        assert serotype["type"] == "ontology"
        assert serotype["_constraints"]["descendant_of"]["_name"] == "Parvoviridae"


class TestNewTypesAcceptedByMetaSchema:
    """The did_schema_meta.json type enum accepts ontology, quantity, relative_quantity."""

    def _wrap(self, field):
        return {
            "_classname": "wrap_test",
            "_class_version": "1.0.0",
            "_maturity_level": "work_in_progress",
            "_superclasses": [],
            "_depends_on": [],
            "_fields": [field],
        }

    def test_ontology_type_accepted(self, did_meta):
        jsonschema.validate(self._wrap(_field("ontology")), did_meta)

    def test_quantity_type_accepted(self, did_meta):
        jsonschema.validate(self._wrap(_field("quantity")), did_meta)

    def test_relative_quantity_type_accepted(self, did_meta):
        jsonschema.validate(self._wrap(_field("relative_quantity")), did_meta)

    def test_nonexistent_type_rejected(self, did_meta):
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(self._wrap(_field("not_a_type")), did_meta)


class TestShapeFromMinischema:
    """A structure field with _shape_from_minischema: true need not carry _fields."""

    def _wrap(self, field):
        return {
            "_classname": "wrap_test",
            "_class_version": "1.0.0",
            "_maturity_level": "work_in_progress",
            "_superclasses": [],
            "_depends_on": [],
            "_fields": [field],
        }

    def test_structure_without_fields_and_without_flag_fails(self, did_meta):
        f = _field("structure")
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(self._wrap(f), did_meta)

    def test_structure_with_flag_and_without_fields_passes(self, did_meta):
        f = _field("structure", _shape_from_minischema=True)
        jsonschema.validate(self._wrap(f), did_meta)

    def test_structure_with_fields_and_without_flag_passes(self, did_meta):
        f = _field("structure", _fields=[])
        jsonschema.validate(self._wrap(f), did_meta)

    def test_flag_false_still_requires_fields(self, did_meta):
        f = _field("structure", _shape_from_minischema=False)
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(self._wrap(f), did_meta)


class TestProfileMetaConstraintRules:
    """profile_meta.json enforces type-specific _constraints requirements."""

    def _wrap_profile(self, field):
        return {
            "profile_name": "test_profile",
            "profile_version": "1.0.0",
            "_maturity_level": "work_in_progress",
            "extends": "",
            "profile_ontology": {
                "_namespace": "obi",
                "_term": "0000412",
                "_name": "test",
                "_uri": None,
            },
            "_documentation": "Test profile.",
            "_fields": [field],
            "promoted_fields": [],
        }

    def test_quantity_requires_canonical_unit_and_label(self, profile_meta):
        # Missing both required keys under _constraints
        bad = _field("quantity", _name="x")
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(self._wrap_profile(bad), profile_meta)

    def test_quantity_with_canonical_unit_and_label_passes(self, profile_meta):
        good = _field(
            "quantity",
            _name="x",
            _constraints={
                "canonical_unit": {
                    "_namespace": "uo",
                    "_term": "0000102",
                    "_name": "nanoliter",
                    "_uri": None,
                },
                "canonical_unit_label": "nl",
            },
        )
        jsonschema.validate(self._wrap_profile(good), profile_meta)

    def test_relative_quantity_requires_reference(self, profile_meta):
        # Has canonical_unit and label but no reference
        bad = _field(
            "relative_quantity",
            _name="x",
            _constraints={
                "canonical_unit": {
                    "_namespace": "uo",
                    "_term": "0000033",
                    "_name": "day",
                    "_uri": None,
                },
                "canonical_unit_label": "day",
            },
        )
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(self._wrap_profile(bad), profile_meta)

    def test_relative_quantity_with_reference_passes(self, profile_meta):
        good = _field(
            "relative_quantity",
            _name="x",
            _constraints={
                "canonical_unit": {
                    "_namespace": "uo",
                    "_term": "0000033",
                    "_name": "day",
                    "_uri": None,
                },
                "canonical_unit_label": "day",
                "reference": "session_start",
            },
        )
        jsonschema.validate(self._wrap_profile(good), profile_meta)

    def test_ontology_forbids_canonical_unit(self, profile_meta):
        bad = _field(
            "ontology",
            _name="x",
            _constraints={
                "canonical_unit": {
                    "_namespace": "uo",
                    "_term": "0000102",
                    "_name": "nanoliter",
                    "_uri": None,
                },
            },
        )
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(self._wrap_profile(bad), profile_meta)

    def test_ontology_with_descendant_of_passes(self, profile_meta):
        good = _field(
            "ontology",
            _name="x",
            _constraints={
                "descendant_of": {
                    "_namespace": "uberon",
                    "_term": "0000955",
                    "_name": "brain",
                    "_uri": None,
                },
            },
        )
        jsonschema.validate(self._wrap_profile(good), profile_meta)


class TestAllVBetaSchemasStillValidate:
    """Regression: all pre-existing V_beta schemas still validate against the updated meta-schema."""

    def test_all_flat_schemas_pass(self, did_meta):
        import glob

        files = sorted(glob.glob(os.path.join(V_BETA, "*.json")))
        # Exclude the meta-schemas themselves; they're not NDI schema files.
        files = [
            f for f in files
            if os.path.basename(f) not in {"did_schema_meta.json", "profile_meta.json"}
        ]
        assert len(files) > 10, "sanity check: at least 10 schema files expected"
        for path in files:
            data = load(path)
            jsonschema.validate(
                instance=data,
                schema=did_meta,
            )
