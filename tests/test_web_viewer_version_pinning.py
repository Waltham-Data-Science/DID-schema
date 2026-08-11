"""The viewer must not pin a schema-set version in a data path.

WHY THIS EXISTS. `web/src/Editor.tsx` fetched
`schemas/V_delta/stable/did_schema_meta.json` as a fixed string while every
other panel followed the set-version selector, whose default is V_eta. So the
"New schema" editor validated new schemas against a meta-schema two sets old.

That is not a cosmetic mismatch, because the meta-schema GREW:

    DENOMINATOR: 2 meta-schemas compared (V_delta, V_eta)
    paths present in V_eta and not V_delta    46
    paths present in V_delta and not V_eta     0

The 46 are exactly what this migration built -- `min_count` / `max_count`
(edge-family cardinality), `ndi_mustBeNonEmpty` on a dependency,
`referent_unique_by`, and the whole `binding` constraint. V_delta's
`dependency_object` declares `additionalProperties: false`, so those keys are
not merely unhinted, they are reported as ILLEGAL PROPERTIES:

    DENOMINATOR: 245 V_eta schema files
    use at least one of the four                          55
      ndi_mustBeNonEmpty 43 | min_count 14 | max_count 2 | referent_unique_by 3

55 of the classes ALREADY IN THE TREE could not have been authored in the
editor -- among them `subject_interaction`, `subject_observation` and `epoch`,
three of the spine classes a new author is most likely to imitate. The editor
would have taught the schema's own rules wrong, and nothing would have said so.

It survived because the viewer is not built by any gate on a feature branch:
`deploy-web.yml` triggers on `push: branches: [main]` only. A pinned path is
also invisible to every schema gate, since it is not a schema.

This test is the standing check for the CLASS of the bug, not the instance.
"""
import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO_ROOT, "web", "src")

# `schemas/V_<set>/` appearing in a data path. The set name is what must be a
# variable; matching the trailing slash keeps prose like "V_eta's meta-schema"
# out of it even when a comment survives stripping.
PINNED = re.compile(r"schemas/V_[a-z]+/")

# The ONE deliberate exception, and it is not a fetch path: `FALLBACK_VERSION`
# is the set shown when `versions.json` cannot be loaded at all (an older
# deployment without the manifest). It is a documented degraded mode rather
# than a pin -- and since the editor now labels the meta-schema it used, that
# mode announces itself in the UI instead of silently validating against the
# wrong set.
ALLOWED_CONST = "FALLBACK_VERSION"


def _sources():
    out = []
    for name in sorted(os.listdir(SRC)):
        if name.endswith((".ts", ".tsx")):
            with open(os.path.join(SRC, name)) as fh:
                out.append((name, fh.read()))
    assert out, "no viewer sources found under web/src -- this test would check nothing"
    return out


def _strip_comments(text):
    """Remove // line comments and /* */ blocks.

    Deliberately crude: it does not understand strings containing "//", so it
    can over-strip. Over-stripping only ever HIDES a violation, never invents
    one, so a false pass is possible and a false failure is not -- and a false
    pass here is caught by the companion test below, which asserts the real
    fetch sites are version-parameterised rather than merely un-pinned.
    """
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return "\n".join(re.sub(r"//.*$", "", ln) for ln in text.splitlines())


def test_no_viewer_source_pins_a_schema_set_in_a_data_path():
    offenders = []
    for name, text in _sources():
        for i, line in enumerate(_strip_comments(text).splitlines(), 1):
            if PINNED.search(line) and ALLOWED_CONST not in line:
                offenders.append("%s:%d: %s" % (name, i, line.strip()))
    assert not offenders, (
        "a viewer source hard-codes a schema set in a data path. The set must "
        "come from the version selector, or the panel shows one set's data "
        "while the header claims another:\n  " + "\n  ".join(offenders))


def test_the_meta_schema_fetch_is_parameterised_by_the_selected_version():
    """The positive half.

    Absence of the literal is not presence of the fix -- deleting the fetch
    would satisfy the test above. This asserts the editor still fetches a
    meta-schema AND that the set comes from a variable.
    """
    with open(os.path.join(SRC, "Editor.tsx")) as fh:
        body = _strip_comments(fh.read())
    m = re.search(r"fetch\(\s*`([^`]*did_schema_meta\.json)`", body)
    assert m, (
        "Editor.tsx no longer fetches a meta-schema through a template "
        "literal. If the mechanism changed, retarget this test -- do not "
        "delete it; an unvalidated editor is the failure it exists to catch.")
    path = m.group(1)
    assert "${version}" in path, (
        "the meta-schema path %r does not interpolate the selected version, so "
        "the editor validates against a fixed set again" % path)
    assert not PINNED.search(path), (
        "the meta-schema path %r still names a set literally" % path)


def test_every_set_the_picker_can_reach_actually_ships_a_meta_schema():
    """Following the selector must not be able to 404.

    The pin was at least always resolvable. Parameterising it trades that for a
    dependency on every selectable set carrying the file -- so check it, rather
    than assume it, and fail with the set named.
    """
    schemas_dir = os.path.join(REPO_ROOT, "schemas")
    sets = sorted(
        d for d in os.listdir(schemas_dir)
        if d.startswith("V_")
        and os.path.isfile(os.path.join(schemas_dir, d, "index.json")))
    assert sets, "no schema sets with an index.json -- nothing to check"
    missing = [
        s for s in sets
        if not os.path.isfile(
            os.path.join(schemas_dir, s, "stable", "did_schema_meta.json"))]
    assert not missing, (
        "%d of %d selectable set(s) ship no stable/did_schema_meta.json, so "
        "choosing one in the viewer breaks the editor: %s"
        % (len(missing), len(sets), ", ".join(missing)))


def test_the_editor_names_the_set_it_validated_against():
    """A caption that names a fixed set is worse than the pin it replaced.

    With the fetch following the selector, hard-coded prose saying "the V_delta
    meta-schema" would describe a different validator from the one that
    produced the errors beside it -- and it reads as confirmation, so nobody
    checks.
    """
    with open(os.path.join(SRC, "Editor.tsx")) as fh:
        body = fh.read()
    m = re.search(r"validated live against the(.{0,80}?)meta-schema", body,
                  flags=re.S)
    assert m, "the editor no longer tells the user what it validated against"
    caption = m.group(1)
    assert "{version" in caption, (
        "the editor's caption does not name the set from state; it reads %r"
        % " ".join(caption.split()))
    assert not re.search(r"V_[a-z]+", caption), (
        "the editor's caption names a set literally: %r"
        % " ".join(caption.split()))
