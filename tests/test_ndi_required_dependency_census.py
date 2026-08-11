"""The "NDI requires it, V_eta does not" census -- schema side.

WHAT IS BEING GUARDED
---------------------
`did2.validate.silentLoss/requiredDependencies` returns names only for edges
declared `mustBeNonEmpty` in the V_eta class chain. So an edge V_eta RELAXED is
not counted as zero by the empty-edge census -- it is never looked at. The
corpus's "0 empty required edges" is therefore SILENT about that whole set. The
`ndi_mustBeNonEmpty` marker exists to make the set countable, and these tests
lock the three properties that make the count readable:

  1. the marker carries NDI's verdict, resolved through the RENAME map;
  2. it NEVER changes a `mustBeNonEmpty` value, so it cannot move the armed
     RequiredDependencies gate or the 0-quarantine corpus result;
  3. absence of the marker means "NDI stated nothing" and is kept distinct from
     "NDI said optional" -- three states, not two.

Every test here is written to fail on the MUTATION it names, and each mutation
was run.
"""
import copy
import glob
import importlib.util
import json
import os
import shutil

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VETA = os.path.join(REPO_ROOT, "schemas", "V_eta")
GT_PATH = os.path.join(REPO_ROOT, "schemas", "V_eta_ndi_ground_truth.json")
TIERS = ["stable", "draft", "deprecated"]
META_FILES = {"did_schema_meta.json", "CURIE_lookups_meta.json",
              "ndi_reserved_keys.json", "binding_registry_meta.json"}


def _load_tool(name):
    """Load tools/<name>.py BY PATH -- `tools/` is not a package, so an
    `import tools.<name>` resolves only when pytest happens to run from the
    repo root. Same helper, same reason, as tests/test_veta.py."""
    path = os.path.join(REPO_ROOT, "tools", name + ".py")
    spec = importlib.util.spec_from_file_location("_veta_tool_" + name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


NRS = _load_tool("ndi_required_stamp")


def _gt():
    with open(GT_PATH) as f:
        return json.load(f)


def _veta():
    out = {}
    for p in glob.glob(os.path.join(VETA, "*", "*.json")):
        if os.path.basename(p) in META_FILES:
            continue
        with open(p) as f:
            d = json.load(f)
        if "document_class" not in d:
            continue
        out[d["document_class"]["class_name"]] = d
    return out


def _deps(doc):
    return {e["name"]: e for e in doc.get("depends_on", [])}


def _rename_map():
    """build_v_eta.py's RENAME, parsed from source -- the same way
    check_tombstones.py reads it, so the two cannot drift."""
    import re
    with open(os.path.join(REPO_ROOT, "tools", "build_v_eta.py")) as f:
        src = f.read()
    m = re.search(r"^RENAME = \{(.*?)^\}", src, re.M | re.S)
    return dict(re.findall(r'"([A-Za-z0-9_]+)"\s*:\s*"([A-Za-z0-9_]+)"',
                           m.group(1)))


def _phase8_set():
    """build_v_eta.py's `_DELETE_PHASE8`, parsed from source for the same
    reason as RENAME above: the test must read the set the BUILD uses, not a
    copy of it written here that could agree with a stale expectation."""
    import re
    with open(os.path.join(REPO_ROOT, "tools", "build_v_eta.py")) as f:
        src = f.read()
    m = re.search(r"^_DELETE_PHASE8 = \{(.*?)^\}", src, re.M | re.S)
    return set(re.findall(r'"([A-Za-z0-9_]+)"', m.group(1)))


TARGETS_PATH = os.path.join(REPO_ROOT, "schemas", "V_eta_migration_targets.json")


def _targets_map():
    with open(TARGETS_PATH) as f:
        return json.load(f)["classes"]


def _run_stamp(**kw):
    """Run the stamp over a THROWAWAY COPY of the built tree.

    Never over `schemas/V_eta` itself: the tree is a checked-in generated
    artifact and a test that mutates it would make the staleness gate report a
    diff that the test, not the schema, produced."""
    tmp = os.path.join(REPO_ROOT, "schemas", ".V_eta_cause_test")
    if os.path.exists(tmp):
        shutil.rmtree(tmp)
    shutil.copytree(VETA, tmp)
    try:
        return NRS.stamp_ndi_required(tmp, GT_PATH, _rename_map(), TIERS,
                                      META_FILES, **kw)
    finally:
        shutil.rmtree(tmp)


def _run_stamp_with_causes():
    return _run_stamp(deleted_phase8=_phase8_set(), targets_path=TARGETS_PATH)


# ---------------------------------------------------------------- ground truth


def test_ground_truth_records_the_two_ndi_files_separately():
    """The TEMPLATE and the SCHEMA DOCUMENT are both NDI's own, and they say
    different kinds of thing -- the template's dependency entry is a slot with
    no required-ness at all, the flat schema document's carries the verdict. The
    extract must record each side rather than silently prefer one.

    MUTATION: drop `depends_on_schema` from the record -> this test fails.
    """
    rec = _gt()["classes"]["ontologyLabel"]
    assert rec["depends_on_template"] == ["document_id"]
    assert rec["depends_on_schema"] == ["document_id"]
    assert rec["depends_on_required"] == {"document_id": True}
    assert rec["schema_document_form"] == "flat"


def test_the_template_never_states_required_ness_and_that_is_measured():
    """`mustbenotempty` lives in NDI's schema documents, never its templates.
    That claim is the reason the extract reads the schema documents at all, so
    it is re-measured on every run instead of being written down once.

    MUTATION: hard-code templates_carrying_mustbenotempty to 1 -> fails.
    """
    scan = _gt()["summary"]["ndi_required_dependency_scan"]
    assert scan["templates_carrying_mustbenotempty"] == 0


def test_ndi_silence_is_not_recorded_as_optional():
    """Five NDI schema documents are JSON Schema draft-2019-09 and carry no
    `mustbenotempty` anywhere. Their classes must record an EMPTY verdict map
    and a form of `json_schema` -- not a map full of `false`.

    This is the absence-of-evidence error one field along: `false` would say
    "NDI agrees with us", which is the reassuring direction.

    MUTATION: default a missing `mustbenotempty` to False in
    ndi_ground_truth._schema_deps -> this test fails.
    """
    gt = _gt()
    js = [c for c, r in gt["classes"].items()
          if r["schema_document_form"] == "json_schema"]
    assert js, "no JSON Schema-form class found -- the scan cannot be checked"
    for c in js:
        assert gt["classes"][c]["depends_on_required"] == {}, (
            "%s states no required-ness in NDI; recording one invents it" % c)


def test_ground_truth_scan_carries_its_denominator():
    """Operating rule 5. A zero in the required-ness census has to be
    distinguishable from "no class was read", and only these counters do that.

    MUTATION: delete the ndi_required_dependency_scan block -> fails.
    """
    scan = _gt()["summary"]["ndi_required_dependency_scan"]
    for key in ("ndi_classes", "classes_with_flat_schema_document",
                "classes_with_json_schema_document",
                "classes_with_no_schema_document",
                "dependency_names_total",
                "dependency_names_with_a_required_statement",
                "dependency_names_required", "dependency_names_optional",
                "dependency_names_ndi_states_nothing_about"):
        assert key in scan, key
    assert scan["ndi_classes"] > 0, "an extract that read nothing"
    assert (scan["classes_with_flat_schema_document"]
            + scan["classes_with_json_schema_document"]
            + scan["classes_with_no_schema_document"]) == scan["ndi_classes"]
    assert (scan["dependency_names_required"]
            + scan["dependency_names_optional"]
            ) == scan["dependency_names_with_a_required_statement"]
    assert (scan["dependency_names_with_a_required_statement"]
            + scan["dependency_names_ndi_states_nothing_about"]
            ) == scan["dependency_names_total"]


# ------------------------------------------------------------------- the stamp


def test_the_motivating_case_is_marked():
    """`ontology_label.document_id`: NDI `mustbenotempty: 1`, V_eta
    `mustBeNonEmpty: false`. ~7,007 documents whose only referent this is, and
    the join key the deferred NDI second pass needs.

    MUTATION: remove the marker from the built schema -> fails.
    """
    dep = _deps(_veta()["ontology_label"])["document_id"]
    assert dep["ndi_mustBeNonEmpty"] is True
    assert dep["mustBeNonEmpty"] is False, (
        "REPORT ONLY -- this census must never tighten the edge it counts")


def test_the_marker_resolves_through_the_rename_map():
    """NDI `element_epoch` is V_eta `acquisition_epoch`. Matching by name alone
    drops every renamed class into "nothing to check", SILENTLY -- which is how
    this exact class escaped an earlier tombstone audit.

    MUTATION: drop the rename lookups from stamp_ndi_required's candidate list
    -> acquisition_epoch loses its marker and this test fails.
    """
    assert _rename_map().get("element_epoch") == "acquisition_epoch"
    dep = _deps(_veta()["acquisition_epoch"])["element_id"]
    assert dep["ndi_mustBeNonEmpty"] is True


def test_the_stamp_changes_no_mustBeNonEmpty_value():
    """THE LOAD-BEARING NEGATIVE. The corpus sits at 0 quarantined / 0 orphans
    with the RequiredDependencies gate ARMED, and that gate keys on
    `mustBeNonEmpty` alone. Run the stamp over a copy of the built tree and
    assert every `mustBeNonEmpty` -- and every other key -- is byte-identical
    afterwards, marker aside.

    MUTATION: make stamp_ndi_required write `mustBeNonEmpty` instead of the
    marker -> this test fails on the first divergent edge.
    """
    tmp = os.path.join(REPO_ROOT, "schemas", ".V_eta_stamp_test")
    if os.path.exists(tmp):
        shutil.rmtree(tmp)
    shutil.copytree(VETA, tmp)
    try:
        def without_marker(doc):
            # Stripped from BOTH sides. The copy is taken from the built tree,
            # which is ALREADY stamped, so comparing a stripped `now` against
            # an unstripped `was` would fail on the marker itself and say
            # nothing about the invariant.
            d = copy.deepcopy(doc)
            for e in d.get("depends_on", []):
                e.pop(NRS.MARKER, None)
            return d

        before = {}
        for p in glob.glob(os.path.join(tmp, "*", "*.json")):
            with open(p) as f:
                before[p] = without_marker(json.load(f))
        NRS.stamp_ndi_required(tmp, GT_PATH, _rename_map(), TIERS, META_FILES)
        for p, was in before.items():
            with open(p) as f:
                now = json.load(f)
            assert without_marker(now) == was, (
                "%s changed beyond the %s marker" % (p, NRS.MARKER))
    finally:
        shutil.rmtree(tmp)


def test_the_stamp_is_idempotent():
    """A second build must not accumulate or flip markers -- the built tree is
    a checked-in generated artifact and CI fails when it is stale, so a
    non-idempotent stamp would make every build report a spurious diff.

    MUTATION: append to a list instead of assigning the key -> fails.
    """
    tmp = os.path.join(REPO_ROOT, "schemas", ".V_eta_stamp_idem")
    if os.path.exists(tmp):
        shutil.rmtree(tmp)
    shutil.copytree(VETA, tmp)
    try:
        rn = _rename_map()
        a = NRS.stamp_ndi_required(tmp, GT_PATH, rn, TIERS, META_FILES)
        snap = {p: open(p).read() for p in glob.glob(os.path.join(tmp, "*", "*.json"))}
        b = NRS.stamp_ndi_required(tmp, GT_PATH, rn, TIERS, META_FILES)
        assert a == b
        for p, text in snap.items():
            assert open(p).read() == text, p
    finally:
        shutil.rmtree(tmp)


def test_the_marker_is_absent_where_ndi_stated_nothing():
    """Three states, not two. A class whose NDI schema document is in the JSON
    Schema form states no required-ness, so its V_eta edges must carry NO
    marker -- not `false`.

    MUTATION: stamp `False` for every unstated edge -> fails.
    """
    gt = _gt()
    veta = _veta()
    checked = 0
    for cn, rec in gt["classes"].items():
        if rec["schema_document_form"] != "json_schema":
            continue
        for cand in (cn, NRS.ndi_snake(cn), _rename_map().get(NRS.ndi_snake(cn))):
            if cand and cand in veta:
                for name, dep in _deps(veta[cand]).items():
                    assert NRS.MARKER not in dep, (
                        "%s.%s carries a verdict NDI never stated" % (cand, name))
                    checked += 1
                break
    assert checked > 0, (
        "no JSON Schema-form class resolved to a V_eta class -- this test "
        "asserted nothing, which is the zero it exists to prevent")


def test_the_marker_is_declared_in_the_meta_schema():
    """`additionalProperties: false` on a dependency object means an undeclared
    key makes every affected schema fail the meta-schema. It must be declared
    as a BOOLEAN and the door must stay shut for everything else.

    MUTATION: remove the ndi_mustBeNonEmpty property from the meta-schema ->
    43 test_file_passes_meta_schema cases fail (observed).
    """
    with open(os.path.join(VETA, "stable", "did_schema_meta.json")) as f:
        meta = json.load(f)
    dep = meta["$defs"]["dependency_object"]
    assert dep["additionalProperties"] is False, (
        "the meta-schema must not be loosened to admit the marker")
    prop = dep["properties"][NRS.MARKER]
    assert prop["type"] == "boolean"
    assert NRS.MARKER not in dep.get("required", []), (
        "the marker is optional -- absence means NDI stated nothing")


# --------------------------------------------------------- the two buckets


def test_the_two_buckets_never_overlap():
    """"an edge OUR schema requires is blank" and "an edge NDI requires is blank
    while we permit it" are DIFFERENT FACTS and are never summed. An edge must
    fall in exactly one bucket, or the armed gate's number becomes unreadable.

    MUTATION: change silentLoss's divergence test to `ndi_mustBeNonEmpty` alone
    (dropping `&& ~mustBeNonEmpty`) and the buckets overlap by 24 edges here.
    """
    ours, theirs = set(), set()
    for cn, doc in _veta().items():
        for name, dep in _deps(doc).items():
            if "#" in name:
                continue          # a family: a missing member is not a blank one
            if dep.get("mustBeNonEmpty"):
                ours.add((cn, name))
            elif dep.get(NRS.MARKER) is True:
                theirs.add((cn, name))
    assert ours and theirs, "one bucket is empty -- nothing was compared"
    assert not (ours & theirs)


def test_the_divergence_set_is_non_empty_and_names_the_planning_cases():
    """A guard against the census silently going to zero because the marker
    stopped being written. The exact membership is data and will change as
    V_eta closes cases; what must hold is that the set is non-empty and that
    the deferred-passthrough classes the second pass depends on are in it.

    MUTATION: skip the stamp entirely -> fails with an empty set.
    """
    rows = set()
    for cn, doc in _veta().items():
        for name, dep in _deps(doc).items():
            if dep.get(NRS.MARKER) is True and not dep.get("mustBeNonEmpty"):
                rows.add("%s.%s" % (cn, name))
    assert rows, "the census found nothing to count -- check the stamp ran"
    assert "ontology_label.document_id" in rows


@pytest.mark.parametrize("counter", NRS.COUNTERS)
def test_every_counter_is_reported(counter):
    """A counter that is accumulated and never assigned reports a zero meaning
    "not reported". silentLoss has shipped that bug once already (famKeys).

    MUTATION: delete any counter from the returned dict -> that case fails.
    """
    d = NRS.stamp_ndi_required(
        os.path.join(REPO_ROOT, "schemas", "does-not-exist"),
        GT_PATH, {}, TIERS, META_FILES)
    assert counter in d


# -------------------------------------------- NOT MEASURED, split into causes
#
# "NOT MEASURED" was ONE bucket printed beside the divergence counts, which
# invited reading the whole block as a clean bill of health. It is now two
# orthogonal partitions -- why the CLASS did not resolve, and whether the EDGE
# could be reached anyway -- plus a split of "no V_eta edge of that name" into
# renamed and dropped. These tests exist so a bucket cannot quietly stop
# partitioning, because a bucket that double-counts or drops always reads as
# better news than it is.


@pytest.mark.parametrize("label,total,parts", NRS.PARTITIONS)
def test_every_bucket_partitions_its_total(label, total, parts):
    """Each breakdown must sum to the number it breaks down.

    MUTATION: drop `edge_dropped` from NO_EDGE_CAUSES so the three no-edge
    causes become two -> the no-edge case fails, 6 != 7.
    """
    d = _run_stamp_with_causes()
    assert sum(d[p] for p in parts) == d[total], label


def test_the_stamp_reports_its_own_partition_verdict():
    """The partition check runs AT BUILD TIME, not only here. A test that runs
    on a developer's machine and nowhere else cannot stop a stale artifact from
    being committed by a build that printed a clean-looking report.

    MUTATION: return the counters without `partition_ok` -> fails.
    """
    d = _run_stamp_with_causes()
    assert d["partition_ok"] == 1
    assert NRS.partition_failures(d) == []


def test_every_unresolved_class_lands_in_exactly_one_cause():
    """The class lists, not just the counts. A class appearing under two causes
    would sum correctly in the class counter and still be double-counted in the
    edge counter.

    MUTATION: append to every matching cause instead of the first -> fails.
    """
    d = _run_stamp_with_causes()
    seen = []
    for cause, _ in NRS.UNRESOLVED_CAUSES:
        seen += [r.split(" (")[0] for r in d["unresolved_by_cause"][cause]]
    assert sorted(seen) == sorted(d["unresolved_classes"])
    assert len(seen) == len(set(seen)), "a class is in two cause buckets"


def test_the_source_deleted_bucket_is_the_real_delete_phase8_set():
    """POSITIVELY DETERMINED, not inferred from absence. A class is in this
    bucket only because build_v_eta.py's own `_DELETE_PHASE8` names it.

    MUTATION: classify on "the ledger says dissolved" instead -> the bucket
    gains classes the build never deleted and this fails.
    """
    d = _run_stamp_with_causes()
    p8 = _phase8_set()
    named = [r.split(" (")[0]
             for r in d["unresolved_by_cause"]["source_deleted"]]
    assert named, "the bucket is empty -- nothing was classified"
    for cn in named:
        assert cn in p8 or NRS.ndi_snake(cn) in p8, cn


def test_the_genuine_hole_bucket_holds_only_classes_with_no_migrator_row():
    """`no_home_no_migrator` is the ONE alarming cause, so its membership is
    checked against the migration-target map directly rather than trusted.

    MUTATION: fall through to this cause when a row exists but names nothing
    -> `imageStack_parameters`-shaped rows join it and this fails.
    """
    d = _run_stamp_with_causes()
    mt = _targets_map()
    named = [r.split(" (")[0]
             for r in d["unresolved_by_cause"]["no_home_no_migrator"]]
    assert named, (
        "the bucket is empty -- either every source is homed, which would be "
        "news, or the classification stopped running")
    for cn in named:
        assert cn not in mt and NRS.ndi_snake(cn) not in mt, cn


def test_a_renamed_edge_and_a_dropped_edge_are_different_facts():
    """`daqsystem.daqmetadatareader_id` is not missing -- V_eta spells it
    `daqmetadatareader_id_#`, a numbered family. Reporting it beside a genuinely
    dropped edge said the same thing about two different situations.

    MUTATION: delete the `renamed_to_family` branch so every unmatched edge is
    `dropped` -> fails on the family rows.
    """
    d = _run_stamp_with_causes()
    veta = _veta()
    rows = d["no_edge_by_cause"]["renamed_to_family"]
    assert rows, "no family rename found -- the branch asserted nothing"
    for row in rows:
        src_edge, target = row.split(" -> ")
        target = target.split("  ")[0]
        name = NRS.ndi_snake(src_edge.split(".", 1)[1])
        assert name + "_#" in _deps(veta[target]), row


def test_the_marker_is_written_on_exactly_the_compared_set():
    """The marker count over the whole built tree must equal the number of
    edges the by-name path compared -- so `edges_compared` is a count of real
    stamps and not of intentions.

    THIS TEST DOES NOT PROVE THE FOLD WRITES NOTHING, and the docstring says so
    because a first draft claimed it did. On today's data the single followed
    fold lands on `daqreader_epochdata_ingested.daqreader_id`, which its OWN
    NDI class already stamps with the same verdict, so stamping it a second
    time changes no count and this test stays green through that mutation.
    `test_a_followed_fold_is_compared_but_never_stamped` is the one that
    proves the negative, on a fixture built to be able to fail.

    MUTATION: helpfully stamp the `<name>_#` family member of a renamed edge
    (3 real cases) -> the marker count exceeds `edges_matched_by_name` and this
    fails. Note the mutation that stamps an INHERITED edge does NOT redden it,
    because `edges_inherited_not_stamped` is 0 on today's data and that branch
    never runs -- another negative this tree cannot currently exercise.
    """
    tmp = os.path.join(REPO_ROOT, "schemas", ".V_eta_fold_test")
    if os.path.exists(tmp):
        shutil.rmtree(tmp)
    shutil.copytree(VETA, tmp)
    try:
        for p in glob.glob(os.path.join(tmp, "*", "*.json")):
            with open(p) as f:
                doc = json.load(f)
            if "document_class" not in doc:
                continue
            changed = False
            for e in doc.get("depends_on", []):
                changed |= e.pop(NRS.MARKER, None) is not None
            if changed:
                with open(p, "w") as f:
                    json.dump(doc, f, indent=4)
                    f.write("\n")
        d = NRS.stamp_ndi_required(tmp, GT_PATH, _rename_map(), TIERS,
                                   META_FILES, deleted_phase8=_phase8_set(),
                                   targets_path=TARGETS_PATH)
        assert d["fold_followed"] > 0, (
            "no fold was followed, so this test asserted nothing about the "
            "negative it exists to prove")
        markers = 0
        for p in glob.glob(os.path.join(tmp, "*", "*.json")):
            with open(p) as f:
                doc = json.load(f)
            markers += sum(1 for e in doc.get("depends_on", [])
                           if NRS.MARKER in e)
        assert markers == d["edges_matched_by_name"]
    finally:
        shutil.rmtree(tmp)


def _synthetic_fold_case(tmp_path, targets, target_docs):
    """A miniature V_eta tree + ground truth + target map, for the fold rules.

    WHY A FIXTURE AND NOT THE REAL TREE. Two mutations of the fold logic --
    stamping the followed target, and picking the first holder instead of
    calling the case ambiguous -- were run against the real schemas and left
    all 76 tests GREEN. Not because the tests were weak, but because today's
    data cannot tell the difference: the ONE fold that can be followed
    (`daqreader_mfdaq_epochdata_ingested.daqreader_id` ->
    `daqreader_epochdata_ingested.daqreader_id`) lands on an edge its own NDI
    class already stamps with the same verdict, so stamping it again changes
    nothing observable; and every ambiguous case is ALSO inherited-only, so
    dropping the ambiguity branch only moves a count between two
    not-followed buckets. A negative that cannot fail is not proven, and the
    data that would prove it does not exist yet -- so it is constructed.
    """
    veta = os.path.join(tmp_path, "V_eta")
    os.makedirs(os.path.join(veta, "stable"))
    for cn, doc in target_docs.items():
        with open(os.path.join(veta, "stable", cn + ".json"), "w") as f:
            json.dump(doc, f)
    gt = os.path.join(tmp_path, "gt.json")
    with open(gt, "w") as f:
        json.dump({"classes": {"alphaSource": {
            "depends_on_required": {"thing_id": True}}}}, f)
    tp = os.path.join(tmp_path, "targets.json")
    with open(tp, "w") as f:
        json.dump({"classes": {"alpha_source": {"targets": targets}}}, f)
    d = NRS.stamp_ndi_required(veta, gt, {}, ["stable"], META_FILES,
                               deleted_phase8=set(), targets_path=tp)
    return veta, d


def _cls(cn, deps, supers=()):
    return {"document_class": {"class_name": cn, "class_version": 1,
                               "maturity_level": "stable",
                               "superclasses": [{"class_name": s}
                                                for s in supers]},
            "depends_on": deps}


def test_a_followed_fold_is_compared_but_never_stamped(tmp_path):
    """THE SECOND LOAD-BEARING NEGATIVE, on data that can show it fail.

    A folded verdict is NDI's opinion about the SOURCE class. Stamping it on
    the TARGET would assert it of every document of that target class,
    including documents that arrived from a different source entirely -- and
    `silentLoss` would then count them, so the corpus figure would move on the
    strength of a fold this repository followed by hand.

    MUTATION: `dep[MARKER] = bool(req)` in the fold branch -> fails.
    """
    veta, d = _synthetic_fold_case(
        str(tmp_path), ["alpha_target"],
        {"alpha_target": _cls("alpha_target",
                              [{"name": "thing_id", "mustBeNonEmpty": False}])})
    assert d["fold_followed"] == 1
    assert d["fold_divergences"] == 1, (
        "NDI requires the edge and the target relaxes it -- that is the "
        "divergence the fold exists to surface")
    assert d["fold_rows_already_compared_by_name"] == 0
    with open(os.path.join(veta, "stable", "alpha_target.json")) as f:
        dep = _deps(json.load(f))["thing_id"]
    assert NRS.MARKER not in dep, (
        "the fold stamped the target -- silentLoss would now count an edge "
        "no NDI class declares of that class")


def test_two_targets_declaring_the_edge_is_ambiguous_not_a_pick(tmp_path):
    """Which of several decomposition products carries NDI's requirement is a
    modelling question, not a lookup. Choosing one would manufacture a
    comparison, and a manufactured comparison is worse than a missing one --
    it enters the report as measured.

    MUTATION: drop the `len(holders) > 1` branch so `holders[0]` is used ->
    the case becomes `followed` and this fails.
    """
    _, d = _synthetic_fold_case(
        str(tmp_path), ["alpha_target", "beta_target"],
        {"alpha_target": _cls("alpha_target",
                              [{"name": "thing_id", "mustBeNonEmpty": False}]),
         "beta_target": _cls("beta_target",
                             [{"name": "thing_id", "mustBeNonEmpty": True}])})
    assert d["fold_followed"] == 0
    assert d["fold_unfollowed_ambiguous_across_targets"] == 1
    assert d["fold_divergences"] == 0


def test_an_edge_only_an_ancestor_declares_is_not_followed(tmp_path):
    """The same rule the by-name path already applies
    (`edges_inherited_not_stamped`), applied to the fold: an NDI fact about one
    class must not be read off a shared superclass that other sources reach.

    MUTATION: allow an inherited-only holder to be followed -> fails.
    """
    _, d = _synthetic_fold_case(
        str(tmp_path), ["alpha_target"],
        {"alpha_target": _cls("alpha_target", [], supers=["shared_root"]),
         "shared_root": _cls("shared_root",
                             [{"name": "thing_id", "mustBeNonEmpty": False}])})
    assert d["fold_followed"] == 0
    assert d["fold_unfollowed_inherited_only"] == 1


def test_fold_divergences_are_never_added_to_the_stamped_divergences():
    """Two different facts: one the corpus census can count (stamped), one it
    cannot see at all (followed by hand through the target map). Summing them
    would put a measured edge and an unmeasurable one in one figure.

    MUTATION: `d["divergences"] += 1` in the fold branch -> divergences stops
    equalling len(divergence_rows) and this fails.
    """
    d = _run_stamp_with_causes()
    assert d["divergences"] == len(d["divergence_rows"])
    assert d["fold_divergences"] == len(d["fold_divergence_rows"])
    assert not (set(d["divergence_rows"]) & set(d["fold_divergence_rows"]))


def test_causes_are_undetermined_when_the_inputs_are_not_supplied():
    """Absence of an input must not produce a cause. Without the deleted set
    and the target map, a phase-8 class and a genuinely unhomed one are
    indistinguishable -- so BOTH go to CAUSE NOT DETERMINED rather than to
    `no_home_no_migrator`, which would raise a false alarm, or to
    `source_deleted`, which would silence a real one.

    MUTATION: default `targets_map` to `{}` instead of None -> every class
    falls to `no_home_no_migrator` and this fails.
    """
    d = _run_stamp()
    assert d["targets_map_readable"] == 0
    assert d["phase8_set_supplied"] == 0
    assert (d["unresolved_classes_cause_undetermined"]
            == d["classes_with_no_v_eta_class"] > 0)
    others = [c for c, _ in NRS.UNRESOLVED_CAUSES if c != "cause_undetermined"]
    assert len(others) == len(NRS.UNRESOLVED_CAUSES) - 1 > 0, (
        "no cause other than 'undetermined' exists, so the loop below would "
        "pass having checked nothing")
    for cause in others:
        assert d["unresolved_classes_" + cause] == 0, cause
    text = "\n".join(NRS.render_stamp_report(d))
    assert "THE CAUSES BELOW COULD NOT BE DETERMINED" in text


def test_the_report_states_not_compared_beside_every_divergence_count():
    """The reader-facing requirement. The divergence figure carries its own
    denominator inline and the never-looked-at figure stands next to it, so
    "0 of 60 compared" and "0 of 5 compared, 55 never looked at" cannot render
    the same way.

    MUTATION: drop the "of %d" from the COMPARED line -> fails.
    """
    d = _run_stamp_with_causes()
    text = "\n".join(NRS.render_stamp_report(d))
    assert ("COMPARED:     %d of %d edge(s)"
            % (d["edges_compared"], d["edges_carrying_an_ndi_verdict"])) in text
    assert ("NOT COMPARED: %d of %d edge(s)"
            % (d["edges_not_compared"],
               d["edges_carrying_an_ndi_verdict"])) in text
    assert "NEVER LOOKED AT" in text
    assert "no figure in this report is the" in text
    assert ("of them %d are NDI-REQUIRED"
            % d["edges_not_compared_ndi_required"]) in text


def test_a_zero_comparison_count_cannot_render_as_a_pass():
    """0 divergences out of 0 compared is the reassuring shape this whole
    module exists to refuse. It must print as untested, in the repository's own
    words, not as agreement with NDI.

    MUTATION: delete the `edges_compared == 0` guard -> fails.
    """
    d = {k: 0 for k in NRS.COUNTERS}
    d.update(ground_truth_readable=1, ndi_classes_read=91,
             ndi_classes_with_a_verdict=57, ndi_required_edges=60,
             ndi_optional_edges=22, edges_carrying_an_ndi_verdict=82,
             classes_with_no_v_eta_class=57,
             edges_lost_to_unresolved_class=82,
             unresolved_classes_cause_undetermined=57,
             edges_unresolved_cause_undetermined=82,
             fold_unfollowed_no_targets_named=82,
             edges_not_compared=82, edges_not_compared_ndi_required=60,
             partition_ok=1)
    d["unresolved_classes"] = []
    d["unresolved_by_cause"] = {c: [] for c, _ in NRS.UNRESOLVED_CAUSES}
    d["no_edge_by_cause"] = {c: [] for c, _ in NRS.NO_EDGE_CAUSES}
    d["divergence_rows"] = []
    d["fold_divergence_rows"] = []
    text = "\n".join(NRS.render_stamp_report(d))
    assert "NOTHING WAS COMPARED AT ALL" in text
    assert "'untested', not 'clean'" in text


def test_a_broken_partition_is_reported_loudly_rather_than_rendered():
    """If the buckets stop adding up, every breakdown is unreliable and the
    report must say so instead of printing numbers that look fine.

    THE FIRST TWO ASSERTIONS GUARD THE CHECKER ITSELF, and they exist because
    the first draft of this file did not have them: replacing
    `partitions_hold` with `return True` left all 76 tests GREEN, since every
    other test asserts the partitions hold on data where they really do. A
    checker that has stopped checking and a checker that finds nothing wrong
    print the same clean result -- this repository's recurring error, arriving
    in the instrument that exists to catch it.

    MUTATION: `partitions_hold` -> `return True`  -> first assertion fails.
    MUTATION: make render ignore `partition_ok`   -> last assertion fails.
    """
    d = _run_stamp_with_causes()
    d["edge_dropped"] += 1                     # one edge counted twice
    assert NRS.partitions_hold(d) is False, (
        "the partition checker did not notice a bucket counted twice")
    assert NRS.partition_failures(d), "no failure was described"
    d["partition_ok"] = 1 if NRS.partitions_hold(d) else 0
    assert d["partition_ok"] == 0
    text = "\n".join(NRS.render_stamp_report(d))
    assert "A PARTITION DOES NOT ADD UP" in text


def test_an_unreadable_ground_truth_is_not_a_clean_zero():
    """With no extract to read, every count is a property of the run. The
    report must say so rather than print zeros.

    MUTATION: return the counters without ground_truth_readable=0 -> fails.
    """
    d = NRS.stamp_ndi_required(VETA, os.path.join(REPO_ROOT, "nope.json"),
                               {}, TIERS, META_FILES)
    assert d["ground_truth_readable"] == 0
    text = "\n".join(NRS.render_stamp_report(d))
    assert "COULD NOT BE READ" in text
    assert "DENOMINATOR" not in text, (
        "printing a denominator for a scan that read nothing is the exact "
        "reassurance this block exists to withhold")
