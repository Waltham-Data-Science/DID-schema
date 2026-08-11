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
