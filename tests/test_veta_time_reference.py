"""V_eta #65 -- the time-reference collapse, schema side (increment 2).

STATUS: written and run 2026-08-10 against the built V_eta set. This file is
Python and this container has one. The MATLAB half of #65
(`did2.convert.resolveSessionAnchors`, `jAbsoluteReference`,
`jEpochClockReferences` and `tests/+did2/+unittest/testTimeReferenceCollapse.m`)
has NEVER been executed -- there is no MATLAB here. Nothing in this file proves
anything about the migrators.

Guards the SIGNED shape (`schemas/V_eta_time_reference_model_plan.md:468`,
TEAM-SIGN-OFF [time_reference], jess@walthamdatascience.com / 2026-08-08):

    CHANGE 1  `end` becomes `duration` on BOTH children -- anchor and extent are
              independent facts, and two instants make the exactness of their
              difference unrecoverable.
    CHANGE 2  every VALUE-LEVEL `approximate` is deleted; approximateness lives
              only where there is a quantity to qualify.
    CHANGE 3  `clock` is a bound ontology_term (built in increment 1).
    CHANGE 4  the `approx_` prefix de-encodes to `clock_tolerance` ON THE ROOT.

WHY A SEPARATE FILE. `tests/test_veta.py` is large and shared; its #67 block
already pins the four clock terms and the two RETIRING classes, and those
assertions must keep passing unchanged. This file pins only what increment 2
CHANGED, so a failure here names the walkthrough item that regressed.

WHAT THIS FILE DELIBERATELY ASSERTS IS *NOT* DONE
-------------------------------------------------
`time_reference.is_approximate` still exists and the six retiring subclasses are
still present. That is not an oversight and it is not laziness: removing a
declared field while emitters still write it raises
`did2:validation:undeclaredField` (+did2/+schema/cache.m:695-706) on all 127,719
live anchors, and deleting a class whose documents still exist is the
`epochfiles_ingested` regression that cost 2,484 quarantines. The tests below
assert the CURRENT, deliberate state and say what must be true before it changes,
so that increment 3 is a decision someone makes rather than a thing that drifts.

DENOMINATOR NOTE: each test that counts states what it counted.
"""
import glob
import json
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VETA = os.path.join(REPO_ROOT, "schemas", "V_eta")

# The eight the collapse targets. Named here rather than derived so a class
# silently disappearing from the build is a FAILURE and not a quieter test.
RETIRING = (
    "session_relative_reference",
    "session_bounded_reference",
    "epoch_relative_reference",
    "epoch_bounded_reference",
    "event_relative_reference",
    "event_bounded_reference",
    "utc_reference",
)
TARGETS = ("absolute_reference", "relative_reference")


def _built():
    out = {}
    for path in sorted(glob.glob(os.path.join(VETA, "*", "*.json"))):
        with open(path) as fh:
            d = json.load(fh)
        if "document_class" not in d:
            continue
        out[d["document_class"]["class_name"]] = (
            os.path.basename(os.path.dirname(path)), d)
    return out


BUILT = _built()


def _field(schema, name):
    for f in schema.get("fields", []):
        if f["name"] == name:
            return f
    raise AssertionError(
        "%s has no field %r; it has %r"
        % (schema["document_class"]["class_name"], name,
           [f["name"] for f in schema.get("fields", [])]))


def _sub(field, name):
    for f in field.get("fields", []):
        if f["name"] == name:
            return f
    raise AssertionError(
        "%r has no sub-field %r; it has %r"
        % (field["name"], name, [f["name"] for f in field.get("fields", [])]))


def _subnames(field):
    return [f["name"] for f in field.get("fields", [])]


# ---------------------------------------------------------------- the family

def test_the_two_targets_exist_under_the_abstract_root():
    """DENOMINATOR: 2 target classes + 1 abstract root, all three inspected."""
    root_tier, root = BUILT["time_reference"]
    assert root["document_class"].get("abstract") is True
    assert [s["class_name"] for s in root["document_class"]["superclasses"]] == ["base"]
    for name in TARGETS:
        _tier, d = BUILT[name]
        assert [s["class_name"] for s in d["document_class"]["superclasses"]] == \
            ["time_reference"], name


def test_change_1_end_is_gone_and_duration_is_the_extent():
    """CHANGE 1, on BOTH children.

    The team's case: "approximately 10 hours after another event, but exactly 60
    minutes in duration". With start+end both offsets inherit the anchor's
    fuzziness and the exactness of their DIFFERENCE is unrecoverable. `end` is
    recoverable as start + duration, so nothing is lost the other way.

    DENOMINATOR: 2 target classes, both inspected.
    """
    checked = 0
    for name in TARGETS:
        _tier, d = BUILT[name]
        value = _field(d, "value")
        subs = _subnames(value)
        assert "duration" in subs, (name, subs)
        assert "end" not in subs, (name, subs)
        assert "end_utc" not in subs, (name, subs)
        # the extent is a duration cell, so canonical seconds + source
        # provenance come for free
        assert _sub(value, "duration")["type"] == "duration", name
        checked += 1
    assert checked == 2


def test_change_2_no_value_level_approximate_survives():
    """CHANGE 2. `value.approximate` is deleted on both children.

    The argument, in two cases. (1) start or duration present -- the cells
    already say which fact is approximate, so a value-level flag can only restate
    or contradict them. (2) neither present -- the assertion is purely
    qualitative, and an Allen relation is true or false; "approximately during
    the session" is not a weaker claim, it is not a claim. THE ABSENCE IS THE
    IMPRECISION.

    DENOMINATOR: 2 target classes, both inspected.
    """
    for name in TARGETS:
        _tier, d = BUILT[name]
        subs = _subnames(_field(d, "value"))
        assert "approximate" not in subs, (name, subs)


def test_the_three_precisions_are_distinct_and_none_restates_another():
    """clock_tolerance (the TIMELINE) / start.approximate (the ANCHOR) /
    duration.approximate (the EXTENT). Each qualifies a different thing, which
    is why deleting the fourth (the value-level flag) lost nothing."""
    _t, root = BUILT["time_reference"]
    assert _field(root, "clock_tolerance")["type"] == "duration"

    _t, rel = BUILT["relative_reference"]
    value = _field(rel, "value")
    assert _sub(_sub(value, "start"), "approximate")["type"] == "boolean"
    assert _sub(_sub(value, "duration"), "approximate")["type"] == "boolean"

    _t, absolute = BUILT["absolute_reference"]
    value = _field(absolute, "value")
    assert _sub(_sub(value, "start"), "approximate")["type"] == "boolean"
    assert _sub(_sub(value, "duration"), "approximate")["type"] == "boolean"


def test_change_4_clock_tolerance_sits_on_the_ROOT_not_the_relative_child():
    """The team caught this one. A UTC time good to +/-5 s can land on EITHER
    class -- as a wall-clock instant it is an absolute_reference, as offsets
    measured in UTC seconds from a referent it is a relative_reference with
    `clock: utc`. On the relative child only, every absolute reference would have
    silently dropped its tolerance."""
    _t, root = BUILT["time_reference"]
    assert "clock_tolerance" in [f["name"] for f in root["fields"]]
    for name in TARGETS:
        _tier, d = BUILT[name]
        own = [f["name"] for f in d["fields"]]
        assert "clock_tolerance" not in own, name
        assert "clock_tolerance" not in _subnames(_field(d, "value")), name


# ------------------------------------------------- absolute_reference's shape

def test_absolute_reference_anchor_is_a_cell_carrying_its_own_provenance():
    """The flat start_utc / source_start / source_timezone fields are gone: the
    canonical instant and the string the source actually wrote travel together,
    exactly as every dimensioned value does (T14)."""
    _t, d = BUILT["absolute_reference"]
    value = _field(d, "value")
    assert _subnames(value) == ["start", "duration", "source_end"], _subnames(value)
    start = _sub(value, "start")
    assert _subnames(start) == [
        "utc", "source_value", "source_timezone", "source_utc_offset",
        "approximate"], _subnames(start)
    assert _sub(start, "utc")["type"] == "timestamp"
    # the canonical slot is OPTIONAL: an unlabelled local time is not
    # convertible, and recording the source string with an empty canonical is
    # the honest state
    assert _sub(start, "utc")["mustBeNonEmpty"] is False


def test_source_end_is_not_renamed_source_duration():
    """The source wrote an END INSTANT, not a quantity of time. Filing that
    string in a duration's source slot would label it as something it is not --
    the distance_metadata assumed-shape error. It stays at value level, as
    provenance of the SOURCE'S SHAPE rather than of one of our fields."""
    _t, d = BUILT["absolute_reference"]
    value = _field(d, "value")
    assert _sub(value, "source_end")["type"] == "char"
    assert "source_duration" not in _subnames(value)
    assert "source_duration" not in _subnames(_sub(value, "duration"))


# ------------------------------------------------- relative_reference's shape

def test_relative_to_is_required_and_says_it_cannot_be_filled_in_pass_one():
    """Fork A: a reference must name what it is measured against.

    The documentation carries the pass-1 blocker on purpose. A migrator holds
    `base.session_id`; the edge needs the session DOCUMENT's `base.id`, and NDI
    mints those independently (+ndi/document.m:57-58 vs +ndi/session.m:215).
    Anyone who reads this schema and reaches for jSessionAnchor needs to hit that
    sentence before they write an empty required edge into 127,719 documents.
    """
    _t, d = BUILT["relative_reference"]
    rel = next(x for x in d["depends_on"] if x["name"] == "relative_to")
    assert rel["mustBeNonEmpty"] is True
    assert rel["must_refer_to_document_class"] == "base"
    assert "resolveSessionAnchors" in rel["documentation"]


def test_relative_reference_value_is_exactly_the_signed_four():
    _t, d = BUILT["relative_reference"]
    assert _subnames(_field(d, "value")) == \
        ["relation", "clock", "start", "duration"]


def test_relation_still_binds_all_thirteen_allen_relations():
    """Unchanged by increment 2, asserted here because the fold's vocabulary map
    (resolveSessionAnchors.owlTimeTerm) reads it: five of v1's six enum members
    map onto these, and `concurrent_with` is REFUSED because it is ambiguous
    between intervalEquals and intervalOverlaps."""
    _t, d = BUILT["relative_reference"]
    binding = _sub(_field(d, "value"), "relation")["constraints"]["binding"]
    assert binding["root"] == "owl_time_interval"
    assert len(binding["values"]) == 13
    for curie in ("time:intervalBefore", "time:intervalAfter",
                  "time:intervalStarts", "time:intervalFinishes",
                  "time:intervalDuring", "time:intervalEquals",
                  "time:intervalOverlaps"):
        assert curie in binding["values"], curie


def test_the_time_curie_prefix_resolves():
    """A binding that LOOKS governed and is not is worse than a plain enum. The
    fold writes real `time:` CURIEs, so the prefix has to expand."""
    with open(os.path.join(VETA, "stable", "CURIE_lookups_meta.json")) as fh:
        curies = json.load(fh)
    assert curies["prefixes"]["time"]["uri_base"] == "http://www.w3.org/2006/time#"


# ------------------------------------------------- what increment 2 does NOT do

def test_the_six_retiring_classes_are_still_present():
    """NOT DONE, ON PURPOSE, and this test is the record of why.

    A class removed from the built set has no schema to validate against, so
    every surviving document of it quarantines. That is the epochfiles_ingested
    regression -- 2,484 quarantines on a 0-quarantine gate -- and here the
    exposure is 127,719 documents.

    THE GATE FOR DELETING THEM: a corpus run in which
    `session_anchor_fold.refused_total` is 0 AND no session_*_reference appears
    in `by_class`. Delete this test WITH the classes.

    DENOMINATOR: 7 classes named, all 7 looked up.
    """
    missing = [c for c in RETIRING if c not in BUILT]
    assert missing == [], (
        "the retiring reference classes were deleted before their documents "
        "were folded: %r" % (missing,))


def test_is_approximate_survives_on_the_root_and_says_it_is_deprecated():
    """CHANGE 2 deletes this field, and increment 2 does not, for a mechanical
    reason: the strict-fields check (+did2/+schema/cache.m:695-706) raises
    `undeclaredField` on any block carrying an undeclared field, and 16
    jSessionAnchor call sites plus 11 inline copies still write
    `time_reference.is_approximate`. Removing the declaration first would
    quarantine every live anchor.

    The documentation must SAY so, because a bare surviving field reads as a
    decision rather than as a queue.
    """
    _t, root = BUILT["time_reference"]
    fld = _field(root, "is_approximate")
    assert fld["mustBeNonEmpty"] is False
    doc = fld["documentation"]
    assert "DEPRECATED" in doc
    assert "increment 3" in doc


def test_the_targets_declare_no_field_the_retiring_classes_would_collide_with():
    """#69's silent-duplicate hazard, checked for this family specifically: a
    child redeclaring an ancestor's field creates two storage locations with
    nothing saying which is authoritative, and `resolvePlacement`'s collision
    check does not fire across blocks.

    DENOMINATOR: 2 targets x every field declared on the abstract root.
    """
    _t, root = BUILT["time_reference"]
    root_fields = {f["name"] for f in root["fields"]}
    for name in TARGETS:
        _tier, d = BUILT[name]
        own = {f["name"] for f in d["fields"]}
        assert not (own & root_fields), (name, sorted(own & root_fields))
