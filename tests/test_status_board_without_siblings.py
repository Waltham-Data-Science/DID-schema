"""The board must regenerate IDENTICALLY where DID-matlab is absent.

WHAT THIS CATCHES, and it went uncaught for three consecutive CI runs on
2026-08-11. `tools/gates.py --ci` reported

    schemas/V_eta_STATUS.md   DIFFERS  -- 4 changed line(s)
    COMPOSED --check FAILED: status_board

on a runner, while the same regeneration reproduced nothing locally. Two
independent defects, and the first one is why the second stayed hidden:

  1. `batch_consumers` called `find_repo` instead of honouring `--did`, so
     "point both siblings at a path that does not exist" silently kept reading
     the real DID-matlab. The local reproduction attempt was not reproducing
     the CI condition at all.

  2. Every other evidence half falls back to the committed snapshot when the
     sibling is missing; that one did not. It rendered `0 batch post-pass
     file(s)` against a committed `10`, so `V_eta_STATUS.md` could NEVER be
     current on a machine without DID-matlab. A generated artifact that is
     unconditionally stale in CI is a gate that fails every run.

The fix has a third trap the test also pins: announcing REUSED *in the
artifact* is self-defeating, because then the file differs between a machine
with the sibling and one without -- the same staleness, one word longer. The
run's provenance goes to stdout; the artifact records only the finding. So this
file asserts BOTH: the bytes are identical, AND the reuse is stated out loud.
"""
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent


def _tracked_copy(dest):
    """A copy of the working tree containing only git-tracked files."""
    names = subprocess.run(["git", "ls-files"], cwd=REPO, capture_output=True,
                           text=True, check=True).stdout.split("\n")
    n = 0
    for rel in names:
        if not rel:
            continue
        src = REPO / rel
        if not src.is_file():
            continue
        dst = dest / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        n += 1
    return n


def _run_board(root, extra):
    return subprocess.run(
        [sys.executable, "tools/status_board.py", *extra],
        cwd=root, capture_output=True, text=True, check=False)


def test_the_board_is_byte_identical_with_no_sibling_checkout():
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp) / "repo"
        root.mkdir()
        copied = _tracked_copy(root)
        nowhere = str(root / "no-such-sibling")
        assert not os.path.isdir(nowhere)

        before = {rel: (root / rel).read_bytes()
                  for rel in ("schemas/V_eta_STATUS.md",
                              "schemas/V_eta_decisions.json")}
        p = _run_board(root, ["--did", nowhere, "--ndi", nowhere])
        after = {rel: (root / rel).read_bytes() for rel in before}

        print(f"DENOMINATOR: {copied} tracked file(s) copied, "
              f"{len(before)} generated artifact(s) compared, "
              f"exit={p.returncode}")
        assert p.returncode == 0, p.stdout + p.stderr
        changed = [rel for rel in before if before[rel] != after[rel]]
        assert not changed, (
            f"{changed} changed when regenerated with NO sibling checkout.\n"
            "The board must be reproducible from what this repository commits, "
            "or CI can never be green. Evidence that cannot be measured here "
            "has to come from the committed snapshot, not from a zero.\n"
            f"--- board stdout ---\n{p.stdout}")


def test_the_reuse_is_announced_on_stdout_and_not_written_into_the_artifact():
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp) / "repo"
        root.mkdir()
        _tracked_copy(root)
        nowhere = str(root / "no-such-sibling")
        p = _run_board(root, ["--did", nowhere, "--ndi", nowhere])

        lines = [ln.strip() for ln in p.stdout.splitlines()]
        reused = [ln for ln in lines if "REUSED from the committed snapshot" in ln]
        print(f"DENOMINATOR: {len(lines)} stdout line(s), "
              f"{len(reused)} announcing a reused snapshot")
        assert any("batch post-pass evidence" in ln for ln in reused), (
            "the batch post-pass sweep read no files and said so nowhere. "
            "A fallback that is not announced is indistinguishable from a "
            "measurement, which is the failure `silentLoss` and this whole "
            "evidence log exist to prevent.\n"
            f"--- board stdout ---\n{p.stdout}")

        board = (root / "schemas" / "V_eta_STATUS.md").read_text(encoding="utf-8")
        assert "REUSED from the committed snapshot" not in board, (
            "the artifact names its own provenance, so it now differs between "
            "a machine with DID-matlab and one without -- the same staleness "
            "this test exists to stop, one word longer. Provenance belongs on "
            "the evidence log; the artifact records the finding.")


def test_batch_consumers_takes_the_sibling_path_rather_than_finding_one():
    """The signature itself, because this is what made the bug unreproducible.

    A helper that reaches for `find_repo` while its caller was told `--did`
    cannot be tested by pointing `--did` anywhere: the "reproduction" reads the
    real checkout and reports success.
    """
    src = (REPO / "tools" / "status_board.py").read_text(encoding="utf-8")
    m = re.search(r"^def batch_consumers\(([^)]*)\):", src, re.MULTILINE)
    assert m, "batch_consumers is gone or renamed; this guard is now vacuous"
    params = [a.strip() for a in m.group(1).split(",")]
    assert len(params) == 2, (
        f"batch_consumers{tuple(params)} takes no sibling-path argument, so it "
        "must be discovering one. It ignored --did for exactly that reason.")
    body = src[m.end():src.index("\ndef ", m.end())]
    assert "find_repo(" not in body, (
        "batch_consumers calls find_repo again. The caller already resolved the "
        "checkout; discovering a second one is how --did stopped meaning "
        "anything.")
