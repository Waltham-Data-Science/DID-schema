"""CHANGE 7 (time reference plan, 2026-10-02) and its amendment: every value that can
say it is `approximate` can also state HOW approximate -- `tolerance {minus, plus}`,
both >= 0, in the value's own unit -- except the four places where `approximate`
describes an axis key or a condition descriptor rather than a value.

Pinned as an exact set so that a new value cell added without a tolerance, or a
key/condition given one without a decision, fails here instead of drifting.
"""
import glob
import json
import os

ROOT = os.path.join(os.path.dirname(__file__), "..", "schemas", "V_eta")

# group 4 of the 2026-10-02 audit: `approximate` there applies to a whole axis key
# or condition descriptor (its spacing, origin, coordinates, or quantity), not to a
# value, so a bound would mean something new. Left out by decision, not omission.
NOT_VALUES = {
    "acquisition_epoch.keys",
    "data.keys",
    "data_body.conditions",
    "subject_statement.conditions",
}


def _load(path):
    with open(path) as fh:
        return json.load(fh)


def _places():
    files = [f for f in glob.glob(os.path.join(ROOT, "*", "*.json"))
             if "document_class" in _load(f)]
    out = []

    def walk(fields, cls, path):
        names = [x["name"] for x in fields]
        if "approximate" in names:
            tol = next((x for x in fields if x["name"] == "tolerance"), None)
            out.append((f"{cls}.{path}".rstrip("."), tol))
        for x in fields:
            if x.get("fields"):
                walk(x["fields"], cls, path + x["name"] + ".")

    for f in files:
        d = _load(f)
        walk(d.get("fields", []), d["document_class"]["class_name"], "")
    return files, out


def test_every_value_that_can_be_approximate_can_state_a_tolerance():
    files, places = _places()
    assert len(files) > 100, f"read {len(files)} class files -- schema tree not found?"
    assert len(places) > 50, f"only {len(places)} `approximate` declarations found"
    without = {p for p, tol in places if tol is None}
    assert without == NOT_VALUES, (
        f"DENOMINATOR: {len(places)} places declare `approximate`. Without a "
        f"tolerance, expected exactly the axis keys and condition descriptors.\n"
        f"  missing a tolerance (add one): {sorted(without - NOT_VALUES)}\n"
        f"  given one without a decision:  {sorted(NOT_VALUES - without)}")


def test_every_tolerance_is_a_non_negative_minus_plus_pair():
    _files, places = _places()
    tols = [(p, t) for p, t in places if t is not None]
    assert len(tols) >= 60, len(tols)
    for p, t in tols:
        assert t["type"] == "structure", p
        assert [x["name"] for x in t["fields"]] == ["minus", "plus"], p
        for b in t["fields"]:
            assert b["type"] == "double", (p, b["name"])
            assert b["constraints"].get("minimum") == 0, (p, b["name"])
        assert t["mustBeNonEmpty"] is False, p   # absent = none stated


def test_the_amendment_reaches_counts_scores_dates_and_the_dose_ratio():
    _files, places = _places()
    have = {p for p, t in places if t is not None}
    for p in ("count.value", "score.value", "date.value",
              "visual_grating.value.contrast", "dose.value.amount_per_body_mass",
              "dose.value.count"):
        assert p in have, p
