"""The batch post-pass chains on both sides must agree, or say why not.

`tools/check_pipeline_parity.py` compares the pass list the six-corpus gate
composes (`runCorpusDiscovery.m`) against the list NDI production composes
(`+ndi/+migrate/`). They are ALLOWED to differ; what they may not do is differ
silently. NDI's own source records both the divergence and its cost:

    two pipelines emitting different classes for one concept, and nothing
    comparing them
        -- +ndi/+migrate/+internal/epochAnchorFold.m

    Ten divergent rows is enough noise to hide an eleventh, which is precisely
    how resolveDatasetEntities came to sit unwired.
        -- +ndi/+migrate/local.m

These tests hold down the properties that make the checker's ZERO trustworthy,
which is a different thing from testing that it currently reports zero. The
sibling repositories are not present in every environment, so anything needing
them skips explicitly rather than passing vacuously.
"""
import os
import subprocess
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = os.path.join(REPO_ROOT, "tools", "check_pipeline_parity.py")

sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
import check_pipeline_parity as cpp  # noqa: E402  (needs the sys.path line above)


def run(*args):
    return subprocess.run([sys.executable, TOOL, *args],
                          capture_output=True, text=True, check=False)


def siblings_present():
    return bool(cpp.find_repo("DID-matlab", "DID_MATLAB")
                and cpp.find_repo("NDI-matlab", "NDI_MATLAB"))


needs_siblings = pytest.mark.skipif(
    not siblings_present(),
    reason="needs DID-matlab and NDI-matlab checkouts")


# ---------------------------------------------------------------------------
# Properties that hold with or without the siblings.
# ---------------------------------------------------------------------------

def test_comments_cannot_contribute_a_pass():
    """The whole finding rests on this.

    All 14 NDI mentions of `resolveDeferredBaths` are COMMENTS explaining that
    NDI substitutes another assembler for it. If commented mentions counted as
    calls, the checker would report the two pipelines as agreeing -- the exact
    false negative it exists to prevent, and the most likely way for it to
    regress, since a plain grep counts them.
    """
    text = "% did2.convert.resolveDeferredBaths, which NDI replaces\n  %   see did2.convert.epochMint for the pattern\n%{\ndid2.convert.resolveSessionAnchors(r);\n%}\nout = did2.convert.foldGenericFiles(r);   % did2.convert.neverCalled"
    found = cpp.passes_in(cpp.strip_matlab_comments(text))
    assert found == {"foldGenericFiles"}, (
        f"comment text leaked into the pass set: {sorted(found)}")


def test_the_per_document_converter_is_not_counted_as_a_batch_pass():
    text = ("r = did2.convert.v1_to_v2(b);\n"
            "r = did2.convert.universalRenames(r);\n"
            "r = did2.convert.epochMint(r);\n")
    assert cpp.passes_in(cpp.strip_matlab_comments(text)) == {"epochMint"}


def test_every_declared_divergence_carries_a_reason():
    assert cpp.DECLARED_DIVERGENCES, (
        "the declaration table is empty -- if every divergence really is gone, "
        "leave the table empty deliberately and delete this test with a note, "
        "because an empty table also silences the stale-declaration check")
    for name, why in cpp.DECLARED_DIVERGENCES.items():
        assert isinstance(why, str) and len(why.split()) >= 8, (
            f"{name} is declared with no usable reason. A bare exemption is how a "
            "considered decision becomes indistinguishable from an oversight.")


def test_a_missing_sibling_reports_not_runnable_and_never_agreement():
    """An unaskable question must not render as a clean answer.

    `silentLoss` printed "0 empty edges" for two days while reading nothing.
    Here the equivalent would be "0 divergences" from a machine with no NDI
    checkout, which is the single most likely environment for this to run in.
    """
    env = dict(os.environ, DID_MATLAB="/nowhere", NDI_MATLAB="/nowhere")
    r = subprocess.run([sys.executable, TOOL], capture_output=True, text=True,
                       env=env, check=False)
    assert r.returncode == 0, "a missing sibling is not a failure"
    assert "NOT RUNNABLE HERE" in r.stdout
    assert "0 file(s) scanned" in r.stdout
    assert "says NOTHING about whether the two" in r.stdout
    assert "0 undeclared divergence" not in r.stdout, (
        "a run that scanned nothing printed a divergence verdict")


def test_an_empty_scan_on_one_side_is_a_broken_scan_not_a_finding(tmp_path):
    """If one side yields no passes, every pass on the other looks divergent.

    Reporting that as "N undeclared divergences" would send someone chasing
    eight phantom findings; reporting it as agreement would be worse. It has
    to be named as a broken scan.
    """
    did = tmp_path / "DID-matlab"
    harness = did / os.path.dirname(cpp.HARNESS)
    harness.mkdir(parents=True)
    (did / cpp.HARNESS).write_text(
        "r = did2.convert.epochMint(r);\n"
        "r = did2.convert.resolveSessionAnchors(r);\n")
    ndi = tmp_path / "NDI-matlab"
    (ndi / cpp.NDI_MIGRATE).mkdir(parents=True)
    (ndi / cpp.NDI_MIGRATE / "empty.m").write_text("% nothing here\n")

    env = dict(os.environ, DID_MATLAB=str(did), NDI_MATLAB=str(ndi))
    r = subprocess.run([sys.executable, TOOL, "--enforce"],
                       capture_output=True, text=True, env=env, check=False)
    assert "ONE SIDE NAMED NO PASSES AT ALL" in r.stdout, r.stdout
    assert r.returncode == 1


def test_an_undeclared_divergence_fails_under_enforce(tmp_path):
    did = tmp_path / "DID-matlab"
    (did / os.path.dirname(cpp.HARNESS)).mkdir(parents=True)
    (did / cpp.HARNESS).write_text(
        "r = did2.convert.epochMint(r);\n"
        "r = did2.convert.aPassNobodyDeclared(r);\n")
    ndi = tmp_path / "NDI-matlab"
    (ndi / cpp.NDI_MIGRATE).mkdir(parents=True)
    (ndi / cpp.NDI_MIGRATE / "local.m").write_text(
        "r = did2.convert.epochMint(r);\n")

    env = dict(os.environ, DID_MATLAB=str(did), NDI_MATLAB=str(ndi))
    r = subprocess.run([sys.executable, TOOL, "--enforce"],
                       capture_output=True, text=True, env=env, check=False)
    assert "*** UNDECLARED ***" in r.stdout
    assert "aPassNobodyDeclared" in r.stdout
    assert r.returncode == 1, "an undeclared divergence must fail --enforce"


def test_a_declaration_that_no_longer_diverges_is_reported_stale(tmp_path):
    """Stale in the reassuring direction: it reads as a considered decision
    about a state that has since changed. Same shape as the stale sign-off
    headers and the stale suppression comments this project already gates on.
    """
    did = tmp_path / "DID-matlab"
    (did / os.path.dirname(cpp.HARNESS)).mkdir(parents=True)
    (did / cpp.HARNESS).write_text("r = did2.convert.epochMint(r);\n")
    ndi = tmp_path / "NDI-matlab"
    (ndi / cpp.NDI_MIGRATE).mkdir(parents=True)
    (ndi / cpp.NDI_MIGRATE / "local.m").write_text(
        "r = did2.convert.epochMint(r);\n")

    env = dict(os.environ, DID_MATLAB=str(did), NDI_MATLAB=str(ndi))
    r = subprocess.run([sys.executable, TOOL, "--enforce"],
                       capture_output=True, text=True, env=env, check=False)
    assert "STALE DECLARATION" in r.stdout
    assert "resolveDeferredBaths" in r.stdout
    assert r.returncode == 1


# ---------------------------------------------------------------------------
# The live repositories.
# ---------------------------------------------------------------------------

@needs_siblings
def test_the_live_pipelines_have_no_undeclared_divergence():
    r = run("--enforce")
    assert r.returncode == 0, r.stdout + r.stderr


@needs_siblings
def test_both_sides_are_actually_read():
    """Guards the denominator itself.

    Every assertion above about "no undeclared divergence" is worthless if
    either side scanned zero files, so the pass counts are asserted non-zero
    here rather than inferred from a green result.
    """
    r = run()
    assert r.returncode == 0, r.stdout
    line = [ln for ln in r.stdout.splitlines() if "named by the harness" in ln]
    assert line, "the pass-count denominator is not printed at all"
    import re
    m = re.search(r"(\d+) pass\(es\) named by the harness, (\d+) by NDI, "
                  r"(\d+) in both", line[0])
    assert m, line[0]
    harness, ndi, both = (int(g) for g in m.groups())
    assert harness > 0 and ndi > 0, (
        f'one side named no passes (harness {harness}, NDI {ndi}) -- the comparison read nothing')
    assert both > 0, "the two pipelines share no pass at all, which cannot be right"
