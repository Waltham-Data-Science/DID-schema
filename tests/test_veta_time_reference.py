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
`time_reference.is_approximate` still exists and the retiring subclasses THAT
STILL HAVE EMITTERS are still present. That is not an oversight and it is not
laziness: removing a declared field while emitters still write it raises
`did2:validation:undeclaredField` (+did2/+schema/cache.m:695-706) on all 127,719
live anchors, and deleting a class whose documents still exist is the
`epochfiles_ingested` regression that cost 2,484 quarantines. The tests below
assert the CURRENT, deliberate state and say what must be true before it changes,
so that increment 3 is a decision someone makes rather than a thing that drifts.

INCREMENT 3a LANDED 2026-08-11 and this paragraph used to say "the six retiring
subclasses" (there were seven). FOUR of the seven -- `epoch_relative_reference`,
`event_bounded_reference`, `event_relative_reference`, `utc_reference` -- are
now DELETED. They were the members with no NDI template, no emitter under any
of the three mint idioms, and no reference from any V_eta schema, so the
quarantine argument above never applied to them: it is entirely about the
session pair. The remaining three are minted today and stay. Both halves are
now pinned, `RETIRING` and `COLLAPSED_AWAY`, because a class quietly coming
BACK is the failure mode a present-only guard cannot see.

DENOMINATOR NOTE: each test that counts states what it counted.
"""
import glob
import json
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VETA = os.path.join(REPO_ROOT, "schemas", "V_eta")

# The seven concrete classes the collapse targets, SPLIT 2026-08-11 into the
# ones that must still be present and the ones that must now be GONE. Named
# here rather than derived, in BOTH directions, so that neither a class
# disappearing nor a class coming back is a quieter test.
#
# `RETIRING` was all seven until increment 3a. It is now the three that are
# still MINTED by live emitters, and deleting one of those strands documents:
#
#     session_relative_reference   22 mint sites   107,308 documents
#     session_bounded_reference     1 mint site     20,411 documents
#     epoch_bounded_reference       1 mint site     (ndi_second_pass)
#
RETIRING = (
    "session_relative_reference",
    "session_bounded_reference",
    "epoch_bounded_reference",
)
# DELETED BY INCREMENT 3a (#65), 2026-08-11. Nothing mints these, nothing
# references them and no NDI template declares them, so the signed collapse is
# EXECUTED for them rather than pending. Listed so that a rebuild which brings
# any of them back fails loudly -- the mirror image of `RETIRING`, and the half
# a one-directional guard cannot cover.
COLLAPSED_AWAY = (
    "epoch_relative_reference",
    "event_bounded_reference",
    "event_relative_reference",
    "utc_reference",
)
TARGETS = ("absolute_reference", "relative_reference")


def _built():
    """The built CLASS set. `examples/` is EXCLUDED, and that exclusion was
    missing until 2026-08-11, when `test_the_collapsed_reference_classes_stay_
    deleted` reported `utc_reference` "came back" after the class file had been
    deleted. It had not. `schemas/V_eta/examples/utc_reference_grid.json` is an
    example DOCUMENT INSTANCE and carries a `document_class` block naming its
    class, so a glob over `V_eta/*/*.json` reads it as a class declaration.

    This is the error the signed plan already records as Claude's error #1
    ("the sweep treated any file with a `document_class` block as a class
    declaration"), still live in this helper. It was INVISIBLE while
    `stable/utc_reference.json` existed, because `examples` sorts before
    `stable` and the real class simply overwrote the example -- the two agreed
    by accident of ordering. `index.json` is the authoritative list and
    `examples/` is not in it.
    """
    out = {}
    for path in sorted(glob.glob(os.path.join(VETA, "*", "*.json"))):
        if os.path.basename(os.path.dirname(path)) == "examples":
            continue
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

    DENOMINATOR: 2 target classes, both inspected, and the count is ASSERTED --
    see the note below on why a stated denominator was not enough here.
    """
    checked = 0
    for name in TARGETS:
        _tier, d = BUILT[name]
        subs = _subnames(_field(d, "value"))
        # `"approximate" not in subs` is a NEGATIVE assertion, and it is equally
        # true of an EMPTY `subs` -- the `demo_ndi` grep in test form, where zero
        # hits was a property of the query rather than of the repository. This
        # test passed unchanged against a build whose `value` block on BOTH
        # children declared no sub-fields at all (demonstrated 2026-08-10 on a
        # perturbed copy). So pin that there is something to search FIRST, and
        # pin it with the two cells the docstring's own argument depends on:
        # `start.approximate` and `duration.approximate` are what make a
        # value-level flag redundant, so if they are gone the argument for
        # deleting it is gone too and this test must stop passing.
        assert subs, (name, "value declares no sub-fields; nothing was searched")
        assert "start" in subs and "duration" in subs, (name, subs)
        assert "approximate" not in subs, (name, subs)
        checked += 1
    assert checked == 2


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
    silently dropped its tolerance.

    DENOMINATOR: 1 abstract root + 2 target classes, all three inspected, and the
    count is ASSERTED. The two `not in` assertions here are the same negative
    shape as CHANGE 2's and carry the same hazard -- `clock_tolerance` is absent
    from an empty list too -- so each collection is pinned non-empty before it is
    searched. Verified 2026-08-10: with `value.fields` emptied on both children
    this test passed unchanged.
    """
    _t, root = BUILT["time_reference"]
    root_own = [f["name"] for f in root["fields"]]
    assert "clock_tolerance" in root_own, root_own
    checked = 0
    for name in TARGETS:
        _tier, d = BUILT[name]
        own = [f["name"] for f in d["fields"]]
        subs = _subnames(_field(d, "value"))
        assert "value" in own, (name, own)
        assert subs, (name, "value declares no sub-fields; nothing was searched")
        assert "clock_tolerance" not in own, (name, own)
        assert "clock_tolerance" not in subs, (name, subs)
        checked += 1
    assert checked == 2


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

def test_the_still_minted_retiring_classes_are_still_present():
    """NOT DONE, ON PURPOSE, and this test is the record of why.

    A class removed from the built set has no schema to validate against, so
    every surviving document of it quarantines. That is the epochfiles_ingested
    regression -- 2,484 quarantines on a 0-quarantine gate -- and here the
    exposure is 127,719 documents.

    THE GATE FOR DELETING THEM: a corpus run in which
    `session_anchor_fold.refused_total` is 0 AND no session_*_reference appears
    in `by_class`. Delete this test WITH the classes.

    NARROWED 2026-08-11, NOT WEAKENED. It named all seven concrete classes and
    the 127,719-document exposure it cites is entirely the session pair; the
    four with no emitter contributed nothing to it. They are now deleted, and
    the ground this test vacated is covered in the OPPOSITE direction by
    `test_the_collapsed_reference_classes_stay_deleted` below -- so the family
    is guarded both ways rather than one class fewer.

    DENOMINATOR: 3 classes named, all 3 looked up.
    """
    assert len(RETIRING) == 3
    missing = [c for c in RETIRING if c not in BUILT]
    assert missing == [], (
        "the retiring reference classes were deleted before their documents "
        "were folded: %r" % (missing,))


def test_the_collapsed_reference_classes_stay_deleted():
    """THE OTHER DIRECTION, and it exists because absence is the easy thing to
    lose. A class silently reappearing in the built set is not a loud event:
    nothing quarantines, no gate reddens, and the collapse simply stops having
    happened. That is the shape of every error CLAUDE.md records -- a thing
    that reads as fine.

    These four were deleted on POSITIVE evidence, re-derived per class:

        0 of 91 NDI templates on origin/main declare any of them (normalised
          match; not one of the 91 class_names contains `reference` at all)
        0 mint sites across all three idioms, over the 187 .m files of
          DID-matlab +did2/+convert and the 17 of NDI-matlab +ndi/+migrate
          (45 distinct class names ARE minted there; none is one of these)
        0 superclass and 0 must_refer_to_document_class references over the
          built V_eta class files
        0 v1-source rows in the coverage ledger / migration targets

    The corpus was NOT the evidence and must not become it: no corpus report is
    reachable from this checkout, and the corpora are a sample either way.

    DENOMINATOR: 4 classes named, all 4 looked up, against a built set whose
    size is asserted first so an empty RECORDS cannot pass this.
    """
    assert len(BUILT) > 200, f"only {len(BUILT)} schemas loaded"
    assert len(COLLAPSED_AWAY) == 4
    back = [c for c in COLLAPSED_AWAY if c in BUILT]
    assert back == [], (
        "%r came back into the built set. The #65 collapse deletes them "
        "(build_v_eta.py `_DELETE_NO_V1_PROVENANCE`); a rebuild that restores "
        "one has either dropped the entry or acquired an emitter, and an "
        "emitter is a decision, not a build artifact." % (back,))


def test_the_collapsed_reference_classes_are_deleted_by_the_named_mechanism():
    """The class being absent is not the same fact as it being DELETED ON
    PURPOSE. A copytree that simply never carried it, a renamed file, a build
    step that quietly skipped -- all produce the same absence, and the test
    above would pass for every one of them.

    So pin the mechanism too: each of the four must be a member of
    `_DELETE_NO_V1_PROVENANCE`, the set whose contract is "a DID-side invention
    that was never a did_v1 source". They are deliberately NOT in
    `_DELETE_PHASE8`, whose contract is "a did_v1 SOURCE provably consumed by a
    completed migrator" -- neither half of which is true here, and asserting
    the wrong set is how a deletion acquires a justification it never earned.

    DENOMINATOR: the tool source is read and both literal sets are evaluated;
    each is asserted non-empty before it is used.
    """
    src = open(os.path.join(REPO_ROOT, "tools", "build_v_eta.py")).read()
    start = src.index("_DELETE_PHASE8 = {")
    end = src.index("_deleted = []", start)
    ns = {}
    exec(src[start:end], ns)          # noqa: S102 -- reading the tool's own literals
    phase8 = ns["_DELETE_PHASE8"]
    invented = ns["_DELETE_NO_V1_PROVENANCE"]
    assert phase8 and invented, "both literal sets must be populated"
    for cls in COLLAPSED_AWAY:
        assert cls in invented, (
            "%s is no longer in _DELETE_NO_V1_PROVENANCE -- its absence from "
            "the built set is now unexplained" % cls)
        assert cls not in phase8, (
            "%s is in _DELETE_PHASE8, which asserts it is a did_v1 source "
            "consumed by a completed migrator. It is neither: its provenance "
            "is V_epsilon and no migrator has ever emitted one." % cls)
    # The three still-minted siblings must be in NEITHER set.
    for cls in RETIRING:
        assert cls not in phase8 and cls not in invented, (
            "%s is minted by live emitters and may not be queued for deletion "
            "-- that is the epochfiles_ingested regression" % cls)


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
