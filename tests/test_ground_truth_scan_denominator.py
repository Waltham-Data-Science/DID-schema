"""The ground-truth scan must count what it FAILED to read, not just what it read.

WHAT WAS WRONG. `tools/ndi_ground_truth.py` reached every NDI schema document
through something that can fail -- `Path(p).read_text()` in a worktree, `git
show <ref>:<path>` against a ref -- and swallowed the failure:

    except Exception:
        continue
    ...
    stats["files"] = len(blobs)

so `files` was the SURVIVORS. A ref gone bad, or a file that could not be read,
subtracted itself from the numerator and the denominator in the same step: the
scan would report success over a universe that had quietly shrunk, and the
`91 NDI classes captured` headline `tools/gates.py` prints would simply have
said 90.

That is this repository's own named failure arriving in the tool the ground
truth comes from. `did2.validate.silentLoss` took `total_docs` from the
survivors of a silent drop and printed "0 empty edges" for two days while
reading nothing; Operating Rule 5 -- AN INSTRUMENT MUST REPORT ITS DENOMINATOR
-- is the rule that produced. These tests hold it in place here.
"""
import ast
import json
import os
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
TOOL = REPO / "tools" / "ndi_ground_truth.py"
OUT = REPO / "schemas" / "V_eta_ndi_ground_truth.json"


def _scan():
    doc = json.loads(OUT.read_text(encoding="utf-8"))
    for key in ("summary", "ndi_schema_document_scan"):
        doc = doc[key]
    return doc


def test_the_scan_records_both_halves_of_its_denominator():
    scan = _scan()
    for key in ("candidates", "unreadable", "files", "unparseable",
                "listing_failed"):
        assert key in scan, (
            f"`{key}` is missing from ndi_schema_document_scan. Without "
            "`candidates` and `unreadable` the scan reports only what it "
            "managed to read, which is how a shrinking universe reads as a "
            "clean one.")
    print(f'DENOMINATOR: {scan["candidates"]} candidate(s), {scan["files"]} read, '
          f'{scan["unreadable"]} unreadable, {scan["unparseable"]} unparseable')


def test_read_plus_unreadable_accounts_for_every_candidate():
    """The invariant that makes the two counters worth having."""
    scan = _scan()
    assert scan["files"] + scan["unreadable"] == scan["candidates"], (
        f'{scan["files"]} read + {scan["unreadable"]} unreadable != '
        f'{scan["candidates"]} candidates. Documents are going missing between '
        "listing and reading with nothing counting them.")
    assert scan["candidates"] > 0 or scan["listing_failed"], (
        "0 candidates and the listing did not fail -- that says NDI ships no "
        "schema documents at all, which would be a finding, not a default. "
        "Check the sibling checkout before believing any figure in this file.")


def test_no_broad_except_swallows_a_read_in_the_scan():
    """`except Exception` around the reads is what made the loss invisible.

    Pinned structurally rather than by rerunning the tool: the two loops that
    populate `blobs` must catch NAMED errors, so an unexpected failure crashes
    loudly instead of decrementing a denominator nobody prints.
    """
    tree = ast.parse(TOOL.read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and "schema" in n.name.lower()
              and any(isinstance(c, ast.Try) for c in ast.walk(n)))
    broad = []
    for handler in (h for h in ast.walk(fn) if isinstance(h, ast.ExceptHandler)):
        name = getattr(handler.type, "id", None)
        if name in ("Exception", "BaseException") or handler.type is None:
            broad.append(handler.lineno)
    print(f"DENOMINATOR: 1 function (`{fn.name}`), "
          f"{sum(1 for h in ast.walk(fn) if isinstance(h, ast.ExceptHandler))} "
          f"handler(s) inspected")
    assert not broad, (
        f"broad `except` at line(s) {broad} in `{fn.name}`. Catch the errors "
        "you expect (OSError, subprocess.CalledProcessError) and count them; a "
        "bare `except Exception: continue` around a read is exactly how "
        "`files` became the survivors.")


def _ndi_checkout():
    """The NDI-matlab this run can actually see, or None."""
    for var in ("NDI_MATLAB", "NDI_MATLAB_PATH"):
        if os.environ.get(var) is not None:
            p = os.environ[var]
            return p if p and os.path.isdir(p) else None
    return "/home/user/NDI-matlab" if os.path.isdir("/home/user/NDI-matlab") else None


def test_the_denominator_is_printed_unconditionally():
    """WITH a sibling the full denominator prints; WITHOUT one the tool must
    still say what it could not read.

    THE FIRST DRAFT OF THIS TEST ASSUMED THE SIBLING WAS THERE and turned CI
    red, because two of the three jobs check out this repository alone. The
    lesson is the one this repository keeps paying for from the other side: a
    test that only runs where the author's machine is configured is a test that
    measures the machine. Both branches are asserted, so neither environment
    gets a free pass -- and the no-sibling branch is NOT a skip, because "could
    not look" must still produce a sentence naming what was not looked at.
    """
    p = subprocess.run([sys.executable, str(TOOL)], cwd=REPO,
                       capture_output=True, text=True, check=False)
    out = p.stdout + p.stderr
    ndi = _ndi_checkout()
    print(f"DENOMINATOR: 1 tool run, exit={p.returncode}, "
          f"{len(out.splitlines())} output line(s), NDI-matlab={ndi!r}")

    if ndi is None:
        assert re.search(r"NDI-matlab not found", out), (
            "no NDI-matlab is reachable and the tool did not say so. A run that "
            "read nothing must name what it could not read; silence here is "
            "indistinguishable from a scan that found nothing.\n"
            + "\n".join(out.splitlines()[-15:]))
        return

    m = re.search(r"^\s*DENOMINATOR: (\d+) candidate schema document\(s\), "
                  r"(\d+) read, (\d+) UNREADABLE", p.stdout, re.MULTILINE)
    assert m, (
        "the scan printed no candidate/read/unreadable line. Operating Rule 5 "
        "asks for the denominator FIRST and UNCONDITIONALLY -- a run that "
        "reports only its findings cannot be distinguished from a run that "
        "found nothing to report.\n--- output tail ---\n"
        + "\n".join(out.splitlines()[-15:]))
    cand, read, bad = (int(g) for g in m.groups())
    assert read + bad == cand
