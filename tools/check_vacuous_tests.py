#!/usr/bin/env python3
"""Find tests that can PASS WHILE CHECKING NOTHING.

WHY THIS EXISTS
---------------
A test that filters a collection and then asserts a property of every element
passes trivially when that collection is empty -- and an empty pass is
indistinguishable from a real one in the output. That is exactly the failure
this project keeps paying for in its instruments:

  * `silentLoss` printed "0 empty edges" for two days while reading nothing.
  * `census_digest` printed a clean report having aggregated zero files, and
    exited 0.
  * `test_uncurated_rows_really_do_have_a_migrator` asserted a property of the
    uncurated rows and, the moment that set reached zero, verified nothing while
    still reporting success.

The first two were caught by adding a DENOMINATOR. This applies the same rule
one level up, to the tests themselves.

THE HEURISTIC, and its limits stated plainly
--------------------------------------------
A test function is FLAGGED when it contains a `for` loop whose iterable is not a
literal, whose body contains an assertion, and the function never constrains the
size of anything. It over-flags: a loop over a hardcoded dict of expectations
can never be empty, and `ALLOW` below records the ones reviewed and found safe,
with the reason. It is a starting point, NOT an instruction -- the same caveat
`check_tombstones.py` carries.

Usage:  python3 tools/check_vacuous_tests.py [--enforce]
"""
import ast
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

# Reviewed and found SAFE, with the reason. An entry here is a claim that the
# loop cannot be empty -- not that the test is unimportant.
ALLOW = {
    ("test_veta.py", "test_openminds_controlled_term_fields_bound"):
        "iterates a hardcoded 3-entry `expected` dict; cannot be empty",
    # The five sweeps in test_schemas.py draw from exactly two sources -- the
    # base schema's field list and the schema directory -- and both are pinned
    # once by test_the_sweeps_have_a_denominator in that same file. The tool
    # works per function and cannot see a guard living in a sibling test, so the
    # claim is recorded here where it can be checked by reading that test.
    ("test_schemas.py", "test_field_types_are_valid"):
        "sources pinned by test_schemas.py::test_the_sweeps_have_a_denominator",
    ("test_schemas.py", "test_all_field_names_match_pattern"):
        "sources pinned by test_schemas.py::test_the_sweeps_have_a_denominator",
    ("test_schemas.py", "test_all_versions_are_semver"):
        "sources pinned by test_schemas.py::test_the_sweeps_have_a_denominator",
    ("test_schemas.py", "test_all_field_types_are_valid"):
        "sources pinned by test_schemas.py::test_the_sweeps_have_a_denominator",
}


def size_constrained(fn):
    for n in ast.walk(fn):
        if isinstance(n, ast.Assert):
            t = n.test
            if "'len'" in ast.dump(t):
                return True
            if isinstance(t, (ast.Name, ast.Attribute, ast.UnaryOp)):
                return True
            if isinstance(t, ast.Compare) and isinstance(t.left, (ast.Name, ast.Call)):
                return True
    return False


def scan(path):
    out = []
    with open(path) as fh:
        tree = ast.parse(fh.read())
    for fn in ast.walk(tree):
        if not isinstance(fn, ast.FunctionDef) or not fn.name.startswith("test"):
            continue
        loops = [n for n in ast.walk(fn) if isinstance(n, ast.For)
                 and not isinstance(n.iter, (ast.List, ast.Tuple, ast.Set))]
        if not any(isinstance(x, ast.Assert) for L in loops for x in ast.walk(L)):
            continue
        if size_constrained(fn):
            continue
        out.append(fn.name)
    return out


def main(argv):
    enforce = "--enforce" in argv
    files = sorted(glob.glob(os.path.join(REPO, "tests", "**", "*.py"),
                             recursive=True))
    files = [f for f in files if "test" in os.path.basename(f)]
    flagged, allowed = [], 0
    for path in files:
        base = os.path.basename(path)
        for name in scan(path):
            if (base, name) in ALLOW:
                allowed += 1
                continue
            flagged.append((os.path.relpath(path, REPO), name))

    # DENOMINATOR FIRST, unconditionally -- this tool must not become the thing
    # it is looking for.
    print(f"VACUOUS-TEST SWEEP: {len(files)} test file(s) parsed, "
          f"{allowed} allow-listed, {len(flagged)} flagged")
    for rel, name in flagged:
        print(f"  {rel}::{name}")
    if flagged and enforce:
        print("\nEach flagged test loops over a collection that may be empty and "
              "asserts nothing about its size, so it can pass having checked "
              "nothing. Add a denominator assertion, or add it to ALLOW with the "
              "reason it cannot be empty.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
