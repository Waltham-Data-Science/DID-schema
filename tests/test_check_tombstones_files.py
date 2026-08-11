"""The file-block half of `tools/check_tombstones.py`.

WHY THIS FILE EXISTS
--------------------
On 2026-08-10 the `image_stack` tombstone declared its attachment as
`imagestack_file`. NDI writes `imageStack` -- the template's `file_list` says so,
and `add_file('imageStack', ...)` appears at all EIGHT attachment sites on NDI
origin/main (`+ndi/+setup/+conv/+haley/doImport.m:441,469,485,504,797,815,831`
and `+ndi/+setup/+conv/+babu/import.m:483`).

The rule that had never been written down: a passed-through document carries its
`file` block VERBATIM, because `+did2/+convert/universalRenames.m:308` skips the
structural keys (`skip = {'document_class','depends_on','file','files'}`). So a
tombstone restated from an NDI template must snake_case its FIELDS and must NOT
snake_case its FILE NAMES.

THREE things could have caught it and none did. `check_tombstones.py` compared
fields and dependencies and did not look at files at all. `did2.validate.fileList`
does look, by exact `strcmp`, but only at corpus time and only as a report. And
every `image_stack` fixture in `testTemplateLiteralTypeTraps.m` is built with no
`files` block, so four green MATLAB tests exercised nothing.

A test that merely asserted "no file divergence for image_stack today" would be
the fourth of those: it passes just as happily when the comparison does nothing.
So the first test below drives the comparison with the PRE-FIX tombstone and
requires it to fire, in BOTH directions, before the second test is allowed to
mean anything.
"""
import importlib.util
import json
import os
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_tool(name):
    """Load tools/<name>.py by PATH -- `tools/` is not a package."""
    path = os.path.join(REPO_ROOT, "tools", name + ".py")
    spec = importlib.util.spec_from_file_location("_ct_tool_" + name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CT = _load_tool("check_tombstones")
GT = json.load(open(os.path.join(REPO_ROOT, "schemas",
                                "V_eta_ndi_ground_truth.json")))
VETA = CT.veta_schemas()


def _fake_veta(class_name, file_names):
    """A minimal V_eta schema set: one class declaring `file_names`, plus the
    `base` it inherits, so the chain walk has something real to walk."""
    return {
        class_name: {
            "document_class": {"class_name": class_name,
                               "superclasses": [{"class_name": "base"}]},
            "file": [{"name": n} for n in file_names],
        },
        "base": {"document_class": {"class_name": "base", "superclasses": []}},
    }


def test_ndi_ground_truth_still_records_the_imagestack_file():
    """DENOMINATOR for everything below: the NDI side of the comparison is real.

    If the extractor ever stopped carrying `files`, every test in this file would
    pass while comparing an empty set against an empty set -- the exact shape of
    the failure the file audit exists to catch, one level up."""
    assert len(GT["classes"]) > 80, (
        "only %d NDI templates in the ground truth" % len(GT["classes"]))
    declaring = [c for c in GT["classes"] if CT.ndi_files(c, GT["classes"])]
    assert len(declaring) >= 15, (
        "only %d NDI templates declare a file; the extractor may have stopped "
        "reading `files.file_list`" % len(declaring))
    assert CT.ndi_files("imageStack", GT["classes"]) == {"imageStack"}


def test_the_file_comparison_catches_the_image_stack_defect():
    """THE REGRESSION TEST. Drive the comparison with the PRE-FIX tombstone.

    `imagestack_file` is what the tombstone declared until 2026-08-10. It trips
    BOTH directions at once, which is the signature of a snake_cased file name:
    the declared name matches nothing NDI writes, AND the name every real
    document carries is left undeclared. A comparison that reported only one of
    the two would still be broken."""
    div = CT.compare_file_block(
        "imageStack", GT["classes"], "image_stack",
        _fake_veta("image_stack", ["imagestack_file"]))
    assert div["declared_but_absent"] == ["imagestack_file"], (
        "the pre-fix tombstone declared a file no NDI template has and the "
        "checker did not report it: %r" % (div,))
    assert div["present_but_undeclared"] == ["imageStack"], (
        "every real imageStack document carries `imageStack` and the checker "
        "did not report it as undeclared: %r" % (div,))


def test_file_names_are_compared_verbatim_not_snake_cased():
    """The defect was a snake_case that should never have been applied.

    `universalRenames.m:308` skips the `file`/`files` keys outright, so the
    document arrives carrying NDI's own spelling. If anyone ever normalises the
    comparison to be "helpful", `imagestack_file` starts matching `imageStack`
    and the defect becomes invisible again -- this pins that shut."""
    assert CT.snake("imageStack") == "image_stack"
    div = CT.compare_file_block(
        "imageStack", GT["classes"], "image_stack",
        _fake_veta("image_stack", ["image_stack"]))
    assert div["declared_but_absent"] == ["image_stack"]
    assert div["present_but_undeclared"] == ["imageStack"]


def test_image_stack_tombstone_agrees_with_ndi_today():
    """The fix, asserted against the SHIPPED schema rather than a fixture.

    Only meaningful because the two tests above prove the comparison fires; the
    denominator assertions here stop it passing on an empty set."""
    assert "image_stack" in VETA, "the image_stack tombstone was deleted again"
    assert CT.veta_files("image_stack", VETA) == {"imageStack"}, (
        "image_stack must declare NDI's own file_list entry verbatim; got %r"
        % (sorted(CT.veta_files("image_stack", VETA)),))
    div = CT.compare_file_block("imageStack", GT["classes"], "image_stack", VETA)
    assert div == {"declared_but_absent": [], "present_but_undeclared": []}, (
        "image_stack diverges from NDI's file_list again: %r" % (div,))


def test_declared_files_are_read_through_the_class_chain():
    """Both sides walk the chain, as `fileList.m`'s `declaredFiles` does.

    NDI's `oneepoch` declares no `files` of its own and inherits
    `epoch_binary_data.vhsb` from `element_epoch`; V_eta's `sampled_body`
    inherits `body_data` from `data_body`. A leaf-only comparison would invent a
    divergence in both cases -- and a checker that cries wolf about correct
    declarations is one nobody reads."""
    assert GT["classes"]["oneepoch"].get("files") in (None, [], {}), (
        "oneepoch now declares its own files; this test's premise is stale")
    assert CT.ndi_files("oneepoch", GT["classes"]) == {"epoch_binary_data.vhsb"}

    assert "body_data" in CT.veta_files("data_body", VETA)
    assert "body_data" in CT.veta_files("sampled_body", VETA)


def test_the_two_directions_are_never_summed():
    """They are different failures: one loses the payload, one strands it.

    A single "N file mismatches" number cannot say which happened, and the
    image_stack defect was BOTH -- so a summed count would have read as one
    problem when it was two."""
    div = CT.compare_file_block(
        "imageStack", GT["classes"], "image_stack",
        _fake_veta("image_stack", ["imagestack_file"]))
    assert set(div) == {"declared_but_absent", "present_but_undeclared"}
    assert div["declared_but_absent"] != div["present_but_undeclared"]


def test_the_report_prints_its_denominator_before_any_row():
    """Operating rule 5, checked on the real output rather than trusted.

    The counts must appear whether or not any row does -- a file audit that
    printed nothing when it found nothing would be indistinguishable from one
    that inspected nothing, which is exactly how `silentLoss` shipped."""
    out = subprocess.run([sys.executable,
                          os.path.join(REPO_ROOT, "tools", "check_tombstones.py")],
                         capture_output=True, text=True, cwd=REPO_ROOT)
    assert out.returncode == 0, out.stderr
    body = out.stdout
    head = body.index("FILE BLOCK AUDIT")
    for label in ("NDI templates read", "V_eta schemas read",
                  "tombstones compared for files",
                  "DECLARED BUT ABSENT", "PRESENT BUT UNDECLARED"):
        assert label in body[head:], "the file audit never printed %r" % label
    first_row = body.find("\nFILE      ", head)
    if first_row != -1:
        assert body.index("tombstones compared for files") < first_row, (
            "a row was printed before the denominator")


def test_enforce_files_is_a_separate_switch_from_enforce():
    """The file audit must not change what `--enforce` gates on.

    `--enforce` grades QUARANTINE risk. A file divergence never quarantines --
    `+did2/+schema/cache.m:736` allows `file`/`files` as top-level keys and never
    looks inside -- so folding it in would make a green quarantine gate depend on
    a different question entirely."""
    tool = os.path.join(REPO_ROOT, "tools", "check_tombstones.py")
    plain = subprocess.run([sys.executable, tool, "--enforce"],
                           capture_output=True, text=True, cwd=REPO_ROOT)
    assert plain.returncode == 0, (
        "--enforce started failing on file rows:\n%s" % plain.stdout[-2000:])
    files = subprocess.run([sys.executable, tool, "--enforce-files"],
                           capture_output=True, text=True, cwd=REPO_ROOT)
    # Report the live state rather than asserting a number: the rows are real and
    # their repair is a schemas/ change this tool may not make.
    if files.returncode == 0:
        assert "classes with a file divergence  : 0" in files.stdout
    else:
        assert "FAIL (--enforce-files)" in files.stdout


def test_no_enforce_verdict_is_produced_without_the_tier_source():
    """A tool that cannot read an input must not grade with it.

    `passthrough` vs `migrated` is read from $DID_MATLAB. With no checkout every
    class reads as a passthrough, and a passthrough's tombstone is the only
    thing between its documents and a quarantine -- so six classes that ARE
    migrated were graded BLOCKING and `--enforce` exited 1 on a verdict computed
    from an input it never read.

    THAT IS WHY THIS TEST EXISTS RATHER THAN A SKIP. The DID-schema `tests`
    workflow was RED for every run on this branch from 14:58 on 2026-08-11
    onward, because the test above calls this tool DIRECTLY and so bypasses the
    `requires=["DID-matlab"]` that lets `tools/gates.py --ci` mark a
    sibling-dependent step NOT RUNNABLE. The local chain stayed green the whole
    time, because the siblings are present there. A false red is not the safe
    direction: a gate that fails on every run is one people stop reading, and a
    real seventh row would have landed in a report already written off.
    """
    tool = os.path.join(REPO_ROOT, "tools", "check_tombstones.py")
    env = dict(os.environ, DID_MATLAB="/nowhere")
    out = subprocess.run([sys.executable, tool, "--enforce"],
                         capture_output=True, text=True, cwd=REPO_ROOT, env=env)
    assert out.returncode == 0, (
        "--enforce still grades without its tier source:\n%s"
        % out.stdout[-1500:])
    assert "NOT RUNNABLE HERE" in out.stdout, (
        "the tool exited 0 without saying it produced no verdict -- which is "
        "worse than the failure it replaces, because 0 reads as a pass")
    assert "THIS IS NOT A PASS" in out.stdout
    assert "DENOMINATOR" in out.stdout, "no denominator on the not-runnable path"
    # The verdict must be withheld, not silently inverted: the rows are still
    # printed, so a reader can see what WOULD have been graded.
    assert "FAIL (--enforce)" not in out.stdout


def test_the_tier_source_being_present_still_grades():
    """The other half. Withholding the verdict everywhere would also be green.

    Without this, deleting the grading entirely would satisfy the test above --
    the same shape as the `return True` mutation that left 76 tests green in a
    neighbouring instrument today.
    """
    tool = os.path.join(REPO_ROOT, "tools", "check_tombstones.py")
    didm = os.environ.get("DID_MATLAB",
                          os.path.join(os.path.dirname(REPO_ROOT), "DID-matlab"))
    if not os.path.isdir(didm):
        import pytest
        pytest.skip("needs a DID-matlab checkout to exercise the grading path")
    out = subprocess.run([sys.executable, tool, "--enforce"],
                         capture_output=True, text=True, cwd=REPO_ROOT)
    assert "NOT RUNNABLE HERE" not in out.stdout, (
        "the tool withheld its verdict even though the tier source is present")
