"""V_eta #57(b) -- `acquisition_channels.acquisition_system_id` points at
`acquisition_system`, and this file exists so the edge cannot drift back to
untyped or sideways to another class.

WHY THE EDGE WAS UNTYPED, AND WHY THAT REASON IS GONE. The dependency was
declared with `must_refer_to_document_class: ""` and documented "UNTYPED for
now: `acquisition_system` is #59's class and does not exist yet". That was
accurate on 2026-08-09 (`9180524`). The class was minted on 2026-08-10
(`8a3cc51`, a DESCENDANT of that commit) and the sentence was never revisited,
so a generated artifact went on publishing a premise that had lapsed. The target
itself is not a new decision: the signed model block of this cluster's plan names
it -- `V_eta_clock_alignment_cluster_plan.md:167`, "acquisition_system_id ->
acquisition_system    the DEVICENAME half" -- and `acquisition_system ⊂ entity`
is TEAM-SIGN-OFF [daq configuration], jess 2026-08-08.

WHAT THIS FILE CAN AND CANNOT CHECK, because the difference is easy to overstate.
`must_refer_to_document_class` is DECLARATIVE in did2 -- existence-only, never
type-checked -- so NOTHING HERE PROVES A RUNTIME PROPERTY. The edge is also
OPTIONAL and is emitted by nothing today: `DID-matlab
+migrators_j/private/jAcquisitionChannels.m` omits it on purpose, because a
syncrule stores a device NAME and resolving name -> document id needs the
migrated-id graph a single-document migrator does not have. So these tests pin a
DECLARATION and say so; they do not pin a validation outcome, and no document in
any corpus behaves differently because they pass.

THE ASSERTION IS THE CLASS NAME, NOT "non-empty". A test that only checked the
field was populated would go green again the moment someone typed the edge at
the wrong class, which is the failure mode the empty string was one step away
from all along.

DENOMINATOR NOTE: every test that counts states what it counted.
"""
import json
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VETA = os.path.join(REPO_ROOT, "schemas", "V_eta")

EDGE = "acquisition_system_id"
HOLDER = "acquisition_channels"
TARGET = "acquisition_system"

# The stale sentence, quoted so its RETURN is a test failure rather than a
# re-reading. Kept as a fragment: the wording around it may legitimately change.
LAPSED_REASON = "does not exist yet"
QUOTE_MARKER = "THIS DOCUMENTATION READ"


def _index():
    with open(os.path.join(VETA, "index.json")) as f:
        return json.load(f)["schemas"]


def _load(entry):
    with open(os.path.join(REPO_ROOT, entry["path"])) as f:
        return json.load(f)


def _entries():
    return {e["class_name"]: e for e in _index()}


def _the_edge():
    """The one `acquisition_system_id` dependency object, or a hard failure.
    Never a silent [] -- a helper that returns nothing when it finds nothing
    turns every assertion below into a vacuous pass."""
    deps = _load(_entries()[HOLDER]).get("depends_on") or []
    named = [d for d in deps if d.get("name") == EDGE]
    assert len(named) == 1, (
        f"expected exactly one {HOLDER}.{EDGE} dependency, found {len(named)}")
    return named[0]


def test_the_target_class_exists_in_the_built_set():
    """The half of the old reason that was a fact about the world. If this ever
    fails, the edge should go back to untyped rather than pointing at a name
    with nothing behind it -- that is the state #57(b) came out of."""
    entries = _entries()
    print(f"DENOMINATOR: {len(entries)} classes in the built V_eta index")
    assert TARGET in entries, (
        f"{TARGET} is not in the built set; the typing below has no referent")
    d = _load(entries[TARGET])
    supers = [s["class_name"] for s in d["document_class"]["superclasses"]]
    assert supers == ["entity"], (
        f"{TARGET} is ⊂ {supers}, not ⊂ entity -- the daq configuration "
        "sign-off says entity, so a change here is a decision, not a drift")
    assert d["document_class"]["maturity_level"] == "stable"


def test_the_edge_is_typed_at_acquisition_system_specifically():
    entries = _entries()
    assert HOLDER in entries, f"{HOLDER} vanished from the built set"
    deps = _load(entries[HOLDER]).get("depends_on") or []
    named = [dep for dep in deps if dep.get("name") == EDGE]
    print(f"DENOMINATOR: {len(deps)} dependencies on {HOLDER}, "
          f"{len(named)} named {EDGE}")
    assert len(named) == 1, f"expected exactly one {EDGE} edge, got {len(named)}"
    got = named[0].get("must_refer_to_document_class", "")
    assert got == TARGET, (
        f"{HOLDER}.{EDGE} must refer to {TARGET!r}; got {got!r}. An empty "
        "string is the untyped state #57(b) closed; any OTHER class name is a "
        "modelling change and needs the team, not this test relaxed.")


def test_the_edge_stays_optional():
    """REQUIRED-NESS IS NOT WHAT #57(b) TOUCHED, and this pins that.

    No NDI template declares this edge -- it is a V_eta-side edge on a V_eta
    target class -- and nothing populates it today. Making it required would
    quarantine every `acquisition_channels` document the syncrule fold emits
    (#37 is armed by default), which is the invented-required-edge pattern this
    repository has already paid for at 26k documents."""
    dep = _the_edge()
    assert dep.get("mustBeNonEmpty") is False, (
        f"{HOLDER}.{EDGE} became required. Check the NDI template and the "
        "emitter before believing that is right: today nothing emits it.")


def test_the_lapsed_reason_is_not_still_published():
    """The defect was not the empty string on its own -- it was a generated
    artifact stating a reason that had expired. A correction that types the edge
    and leaves the sentence would be half a repair."""
    doc = _the_edge().get("documentation", "")
    assert doc, f"{HOLDER}.{EDGE} has no documentation at all"
    # The phrase may appear ONCE, and only INSIDE the quoted correction that
    # says it used to be the reason -- the house style, which keeps the record
    # legible instead of silently deleting it. Anywhere else it is the lapsed
    # justification standing again. Checked by POSITION, not by a keyword
    # appearing somewhere in the string: a keyword escape passes for any text
    # that happens to contain the word, which is how a guard goes quiet.
    quoted_at = doc.find(QUOTE_MARKER)
    for hit in [i for i in range(len(doc)) if doc.startswith(LAPSED_REASON, i)]:
        assert quoted_at != -1 and hit > quoted_at, (
            f"{HOLDER}.{EDGE} states {LAPSED_REASON!r} outside the quoted "
            f"correction ({QUOTE_MARKER!r}). The class was minted 2026-08-10; "
            "the reason lapsed with it, and a repair that types the edge while "
            "republishing the reason is half a repair.")


def test_no_other_schema_declares_this_edge_untyped():
    """Scope guard. `V_eta_epoch_plan.md:776` proposes the same edge name on a
    future `<modality>_observation`. If that lands untyped, the same lapse
    starts over one class along -- so this fails on the SECOND occurrence rather
    than after another year of it being nobody's item."""
    offenders, n, seen = [], 0, 0
    for e in _index():
        n += 1
        for dep in _load(e).get("depends_on") or []:
            if dep.get("name") != EDGE:
                continue
            seen += 1
            if dep.get("must_refer_to_document_class", "") != TARGET:
                offenders.append((e["class_name"],
                                  dep.get("must_refer_to_document_class", "")))
    print(f"DENOMINATOR: {n} index.json schemas read, "
          f"{seen} declare {EDGE}, {len(offenders)} not typed at {TARGET}")
    assert seen >= 1, f"no schema declares {EDGE} -- this file is testing nothing"
    assert offenders == [], (
        f"{EDGE} declared with a different target: {offenders}")
