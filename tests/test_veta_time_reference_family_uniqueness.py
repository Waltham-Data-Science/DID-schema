"""V_eta #52 -- the ONE rule a `time_reference_#` family has to obey.

STATUS: written and run 2026-08-10 against the built V_eta set. This file is
Python and this container has one. The MEASURING half of #52 lives in
DID-matlab (`did2.validate.silentLoss/family_uniqueness_violation`, tested by
`tests/+did2/+unittest/testFamilyUniqueness.m`) and HAS NEVER BEEN EXECUTED --
there is no MATLAB here. Nothing in this file proves anything about that code.

#52'S TITLE IS STALE. It reads "role-name the `time_reference_#` statement
edges"; the row in `schemas/V_eta_OPEN_WORK.md` shrank it on 2026-08-08 to one
rule, and `V_eta_time_reference_model_plan.md` CHANGE 5 (:642, inside the SIGNED
2026-08-08 walkthrough section) records why. Four things multiple references on
one document could have meant:

    1. split-anchored interval   NO INSTANCE EXISTS -- every markvalidinterval
                                 call site passes ONE reference for both ends.
                                 So there are NO `start_anchor`/`end_anchor`
                                 edges, and this file asserts their absence.
    2. same extent, N clocks     LIVE (an epoch's epochtable is one
                                 (clock, interval) pair per entry, several per
                                 epoch). The discriminator ALREADY EXISTS,
                                 inside the referenced document: `value.clock`.
    3. recurrence                dissolves into N statements (T4).
    4. epoch extent + statement time    different documents, never a conflict.

Leaving only:

    Within a `time_reference_#` family every member describes the same instant
    or extent, and `value.clock` is UNIQUE across the family.

WHAT THIS FILE CAN AND CANNOT CHECK. It checks the DECLARATION -- that the rule
is written down, machine-readably, on every family it governs, and on no family
it does not. It CANNOT check the rule itself: `value.clock` is a property of the
REFERENCED document, so verifying it needs the other documents in hand. That is
a batch property and it is measured in `did2.validate.silentLoss`. A per-document
version would silently pass whenever it could not resolve a target, which is the
"all-zero census reads as clean" failure this repository has paid for twice.

DENOMINATOR NOTE: every test that counts states what it counted.
"""
import json
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VETA = os.path.join(REPO_ROOT, "schemas", "V_eta")

# The three, named rather than derived. Deriving "every family whose target is a
# time_reference" would let a family drop out of the rule the day a target class
# is renamed -- an absence turning into a reassuring silence, which is the shape
# of every epistemic error recorded in CLAUDE.md.
GOVERNED = {
    ("subject_interaction", "time_reference_#"),
    ("directed_relation", "time_reference_#"),
    ("epoch", "time_reference_#"),
}
UNIQUE_BY = "value.clock"


def _index():
    with open(os.path.join(VETA, "index.json")) as f:
        return json.load(f)["schemas"]


def _load(entry):
    with open(os.path.join(REPO_ROOT, entry["path"])) as f:
        return json.load(f)


def _families():
    """Every numbered `depends_on` family in the built set, as
    {(class_name, edge_name): dependency_object}. Reads index.json, which is
    AUTHORITATIVE -- examples/ carries document instances whose depends_on
    entries are concrete (`time_reference_1`), not families, and treating one as
    a class declaration is an error already recorded in the plan document."""
    out = {}
    for e in _index():
        d = _load(e)
        for dep in d.get("depends_on") or []:
            if "#" in dep.get("name", ""):
                out[(e["class_name"], dep["name"])] = dep
    return out


def test_the_meta_schema_can_express_the_rule_at_all():
    # Without this the declaration below is an undeclared key and every schema
    # fails meta-validation (`additionalProperties: false`).
    with open(os.path.join(VETA, "stable", "did_schema_meta.json")) as f:
        meta = json.load(f)
    props = meta["$defs"]["dependency_object"]["properties"]
    assert "referent_unique_by" in props, (
        "the meta-schema has no way to say what distinguishes two members of a "
        "family; #63 added min_count/max_count and stopped at HOW MANY")
    desc = props["referent_unique_by"]["description"]
    # The name and the description both have to carry the hard part, because the
    # hard part is the only thing a reader can get wrong: the path is evaluated
    # on the REFERENCED document.
    assert "REFERENCED DOCUMENT" in desc.upper()
    assert "silentLoss" in desc, (
        "the declaration must say where the rule is measured, or it is a "
        "sentence nothing enforces")


def test_every_time_reference_family_declares_the_rule():
    fams = _families()
    print(f'DENOMINATOR: {len(fams)} numbered edge families in the built set')
    for key in sorted(GOVERNED):
        assert key in fams, (
            "{}.{} does not exist -- the uniqueness rule has no home. If the "
            "family was renamed, move the rule; do not drop it.".format(*key))
        dep = fams[key]
        assert dep.get("referent_unique_by") == UNIQUE_BY, (
            "{}.{} must declare referent_unique_by={!r}; got {!r}".format(key[0], key[1], UNIQUE_BY, dep.get("referent_unique_by")))


def test_no_other_family_silently_acquires_the_rule():
    # Scope guard, in the direction the row asks for. `derived_from_#` members
    # are N DIFFERENT inputs and no uniqueness rule has been decided for them;
    # a rule arriving there by accident would start counting violations that
    # nobody agreed are violations.
    fams = _families()
    carrying = {k for k, v in fams.items() if "referent_unique_by" in v}
    print(f'DENOMINATOR: {len(fams)} numbered families, {len(carrying)} declare referent_unique_by')
    assert carrying == GOVERNED, (
        f"unexpected families carrying the rule: {sorted(carrying - GOVERNED)}; missing: {sorted(GOVERNED - carrying)}")


def test_the_documentation_says_the_index_means_nothing_on_its_own():
    fams = _families()
    checked = 0
    for key in sorted(GOVERNED):
        doc = fams[key].get("documentation", "")
        assert "value.clock" in doc, (
            "{}.{}: the human-readable half must name the discriminator".format(*key))
        assert "start_anchor" in doc, (
            "{}.{}: the documentation must record that split-anchored "
            "intervals have NO instance, or the next reader re-derives the "
            "edges the row forbids".format(*key))
        checked += 1
    # DENOMINATOR, asserted rather than printed: a loop over a collection that
    # could be empty passes having checked nothing.
    print(f'DENOMINATOR: {len(GOVERNED)} governed families, {checked} documentation strings checked')
    assert checked == len(GOVERNED) == 3


def test_no_start_anchor_or_end_anchor_edge_was_built():
    """Operating rule 3, mechanically. The row says split-anchored intervals
    have NO INSTANCE and the named edges must NOT be built. This is a POSITIVE
    check that they are absent from the built set, so a future session that
    re-derives them from `markvalidinterval`'s signature trips a test rather
    than shipping."""
    offenders = []
    n = 0
    for e in _index():
        d = _load(e)
        n += 1
        for dep in d.get("depends_on") or []:
            if dep.get("name") in ("start_anchor", "end_anchor",
                                   "start_anchor_#", "end_anchor_#"):
                offenders.append((e["class_name"], dep["name"]))
    print(f'DENOMINATOR: {n} index.json schemas read')
    assert offenders == [], (
        "split-anchored intervals have NO INSTANCE (every markvalidinterval "
        f"call site passes one reference for both ends). Found: {offenders}")


def test_the_rule_is_checkable_on_exactly_one_class_today_and_says_so():
    """The uncomfortable measurement, recorded rather than smoothed over.

    `value.clock` exists on ONE class in the whole `time_reference` subtree.
    Two of the others -- `session_relative_reference` and
    `session_bounded_reference` -- are where every live anchor document
    currently sits, and they declare no clock at all. So on today's data the
    rule has almost nothing to compare, and any instrument reporting "0
    violations" is reporting "nothing was comparable", not "everything is
    fine". That is exactly the distinction the census denominators exist for.
    """
    entries = {e["class_name"]: e for e in _index()}
    children = {}
    for e in _index():
        for s in e.get("superclasses") or []:
            name = s if isinstance(s, str) else s.get("class_name")
            children.setdefault(name, []).append(e["class_name"])

    closure, stack = [], ["time_reference"]
    while stack:
        c = stack.pop()
        if c in closure:
            continue
        closure.append(c)
        stack += children.get(c, [])

    def has_clock(cls):
        d = _load(entries[cls])
        for f in d.get("fields") or []:
            if f.get("name") == "value":
                return any(sf.get("name") == "clock"
                           for sf in (f.get("fields") or []))
        return False

    with_clock = sorted(c for c in closure if has_clock(c))
    print(f'DENOMINATOR: {len(closure)} classes in the time_reference subtree; {len(with_clock)} declare value.clock: {with_clock}')
    # 1 -> 2 on 2026-08-13, and this is the deliberate update the message below
    # asks for. `epoch_bounded_reference` gained a `value` slot copied verbatim
    # from relative_reference so pyraview's epoch EXTENT has transport between
    # pass 1 and did2.convert.epochMint -- it had none, which is why the extent
    # could not be minted. The copy brings `value.clock` with it, so the handle
    # is now comparable by the same discriminator.
    #
    # THAT IS CORRECT RATHER THAN INCIDENTAL: the uniqueness rule says members
    # of one `time_reference_#` family must differ by clock, and a handle that
    # will BECOME a relative_reference has to satisfy the same rule or the fold
    # could turn a legal family into an illegal one. The handle is transitional
    # (not in the persist set -- tier 5 is absolute_reference +
    # relative_reference), so this list shrinks back to one when it is deleted.
    assert with_clock == ["epoch_bounded_reference", "relative_reference"], (
        f"the set of classes the rule can compare has changed: {with_clock}. If the "
        "collapse (#65 increment 3) has landed, this test's premise is the "
        "thing that moved -- update it deliberately.")
    # And the two that hold the documents today still have no clock. Stated as
    # an assertion so the day it stops being true is a visible event.
    for legacy in ("session_relative_reference", "session_bounded_reference"):
        assert legacy in entries, f"{legacy} vanished -- see the epochfiles_ingested " \
            "regression before deleting a class whose documents exist"
        assert not has_clock(legacy), (
            f"{legacy} now declares value.clock; the uniqueness rule became "
            "measurable on the 127,719 live anchors and the census must be "
            "re-read before anyone quotes a zero")
