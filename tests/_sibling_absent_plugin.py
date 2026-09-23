"""Pytest plugin: make the sibling repositories UNFINDABLE, as on a runner.

WHY THIS EXISTS
---------------
Two tests in a row were red on their FIRST CI run, both for the same reason, and
both passed locally every time. `tests.yml`'s MAIN job clones both siblings; its
`older-pythons` matrix jobs run pytest ALONE. A test that asserts on
sibling-derived output passes in the first and fails in the second, and nothing
local reproduces the second.

Configuration cannot reproduce it. Every `find_repo` in `tools/` tries
`$DID_MATLAB`, then `/home/user/<name>`, then `<dirname of schema root>/<name>`
-- and `/home/user/DID-matlab` EXISTS in the authoring container whatever the
environment says. Pointing the env vars at `/nonexistent` proves nothing; the
lookup falls through to the hardcoded path and succeeds. CLAUDE.md's own words:

    Every local run finds DID-matlab at `/home/user/DID-matlab`, so this is
    invisible outside CI -- do not test the fix locally and conclude anything.

HOW IT PATCHES, AND WHY NOT THE OBVIOUS WAY
-------------------------------------------
The first draft walked `sys.modules` for anything loaded out of `tools/` with a
`find_repo` attribute and replaced it. IT PATCHED NOTHING -- 0 of them -- because
the test modules load their tools with

    spec = importlib.util.spec_from_file_location("check_build_claims", TOOL)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

which never registers the module in `sys.modules`. The walk had nothing to find.
That draft's own denominator guard is what caught it, and the guard is the only
reason this file is correct now -- the suite reported `1744 passed` under a
simulation that simulated nothing, and the exit code was 1 with the reason
printed above it.

So the patch goes UNDERNEATH every implementation instead of at each one:
`os.path.isdir` returns False for any path naming a sibling checkout root. Every
`find_repo` -- however its module was loaded, whoever wrote it, whichever of the
three candidates it is testing -- then returns None. That is exactly the runner's
condition: not a broken sibling, not an empty directory, a lookup that finds
nothing.

THE PATCH DENIES EXACT PATHS, NOT A BASENAME, and that distinction was learned
the same way as everything else here. Matching any directory CALLED
`DID-matlab` broke `tests/test_pipeline_parity.py`, which CONSTRUCTS fake
sibling checkouts in a tmp dir and points `$DID_MATLAB` / `$NDI_MATLAB` at them
to exercise the tool. Hiding those hid the fixture, and three tests failed with
`NOT RUNNABLE HERE` -- a third simulation artefact wearing the costume of a
finding.

It is also the more faithful rule: on a runner the sibling checkout is not
there, while a directory a test just built IS. So only the candidate roots a
real `find_repo` would resolve are denied -- `/home/user/<name>` and
`<dirname of the schema root>/<name>` -- and anything a test constructs for
itself stays visible.

WHAT A PASS MEANS, AND WHAT IT DOES NOT
---------------------------------------
A pass means: with no siblings, every test either passes or SKIPS WITH A STATED
REASON, and no tool reports a smaller universe while exiting 0. It does NOT mean
the tools are correct -- their real coverage is the ordinary run, where the
siblings are present.

NOT A PRODUCTION HOOK. Nothing in `tools/` knows this file exists; there is no
environment variable a tool honours and no branch a tool takes. The patch lives
in the test process only.
"""
import os
import tempfile

SIBLINGS = ("DID-matlab", "NDI-matlab")

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# The concrete candidates every find_repo in tools/ tries, minus the env var
# (popped below so the fallbacks are what gets exercised).
HIDDEN_ROOTS = frozenset(
    os.path.normpath(os.path.join(parent, name))
    for name in SIBLINGS
    for parent in ("/home/user", os.path.dirname(_REPO)))

# THE PATCH MUST REACH CHILD INTERPRETERS TOO, and the first working draft did
# not. Several tests check reachability in the PARENT and then run the tool in a
# SUBPROCESS. `test_ground_truth_scan_denominator` is the clearest: it asks
# `_ndi_checkout()` (patched here -> None), then runs the scan via
# `subprocess.run` in a fresh interpreter where nothing is patched -- so the
# CHILD found the sibling and printed a full denominator while the PARENT
# expected "NDI-matlab not found".
#
# THAT FAILURE WAS AN ARTEFACT OF THE SIMULATION, NOT A DEFECT IN THE TOOL, and
# it presented as one: a red test whose message reads like a real finding
# ("a run that read nothing must name what it could not read"). Reporting it
# would have been exactly the wrong conclusion this plugin exists to prevent --
# a harness that manufactures the defect it was built to detect.
#
# `sitecustomize` is imported automatically at interpreter startup when it is
# importable, so writing one onto PYTHONPATH applies the same patch in every
# child without any tool knowing this file exists.
_SITECUSTOMIZE = f"""\
import os
_real = os.path.isdir
_hidden = {sorted(HIDDEN_ROOTS)!r}


def _isdir(p):
    try:
        if os.path.normpath(str(p)) in _hidden:
            return False
    except (TypeError, ValueError):
        pass
    return _real(p)


os.path.isdir = _isdir
"""

_denied = []
_real_isdir = os.path.isdir


def _looks_like_sibling_root(path):
    """Is this path a sibling CHECKOUT ROOT (not something inside one)?

    Exact-path, not basename: a test that BUILDS a sibling fixture must still
    see it (see the note above `HIDDEN_ROOTS`)."""
    try:
        return os.path.normpath(str(path)) in HIDDEN_ROOTS
    except (TypeError, ValueError):
        return False


def _isdir(path):
    if _looks_like_sibling_root(path):
        _denied.append(str(path))
        return False
    return _real_isdir(path)


_tmpdir = None


def pytest_configure(config):
    """Patch BEFORE collection, so a module-level find_repo call is covered too."""
    global _tmpdir
    os.path.isdir = _isdir
    for name in SIBLINGS:
        os.environ.pop(name.upper().replace("-", "_"), None)
    _tmpdir = tempfile.mkdtemp(prefix="sibling-absent-")
    with open(os.path.join(_tmpdir, "sitecustomize.py"), "w") as fh:
        fh.write(_SITECUSTOMIZE)
    prev = os.environ.get("PYTHONPATH", "")
    os.environ["PYTHONPATH"] = _tmpdir + (os.pathsep + prev if prev else "")


def pytest_unconfigure(config):
    os.path.isdir = _real_isdir


def pytest_report_header(config):
    return (f"sibling-absent simulation: {', '.join(SIBLINGS)} hidden; "
            f"isdir denials so far {len(_denied)}")


def pytest_sessionfinish(session, exitstatus):
    """A simulation that simulated nothing must not read as a pass.

    THE DENOMINATOR IS THE POINT. The previous draft patched 0 lookups and the
    suite reported `1744 passed`; only this guard distinguished that from a real
    run. If no lookup was ever denied, the tests under simulation never asked
    where a sibling was, so the run proves nothing about the condition it exists
    to reproduce."""
    if not _denied:
        print("\nSIBLING-ABSENT SIMULATION DENIED 0 LOOKUPS -- no test asked "
              "where a sibling was, so nothing was simulated. This is a "
              "failure, not a pass.")
        session.exitstatus = 1
    else:
        print(f"\nsibling-absent simulation: {len(_denied)} isdir lookup(s) "
              f"denied across {len(set(_denied))} distinct path(s)")
