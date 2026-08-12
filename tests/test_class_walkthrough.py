"""The per-class walkthrough asset the viewer reads, and the two ways it lies.

The asset (`web/public/class_walkthrough.json`) is COMMITTED, because the deploy
workflow runs `npm ci && npm run build` and nothing else -- no Python, no
sibling checkout. That buys a viewer that works on a runner and costs a file
that can go stale silently, so the freshness comparison below is the whole
reason this file exists.

The second failure is subtler and already happened once. The tool locates
migrator files by name; V_eta is snake_case and NDI is camelCase; the ledger
keys its rows by the NDI spelling. Searching one spelling reported 0 migrator
files for five classes that have had one for months, and it reported it as a
fact about DID-matlab rather than about the query. The generator cross-checks
itself against the ledger's own `migrator` boolean and records every
disagreement; `test_no_disagreement_with_the_ledger` is what makes that
recording load-bearing instead of decorative.
"""
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

import gen_class_walkthrough as gen  # noqa: E402

ASSET = REPO / "web" / "public" / "class_walkthrough.json"
LEDGER = REPO / "schemas" / "V_eta_coverage_ledger.json"


def _asset():
    assert ASSET.exists(), (
        f"{ASSET.relative_to(REPO)} is absent -- run "
        "`python3 tools/gen_class_walkthrough.py` and commit the result")
    return json.loads(ASSET.read_text(encoding="utf-8"))


def test_denominator_is_stated_and_non_vacuous():
    """An asset that inspected nothing must not read like an asset that found
    nothing. The counts are asserted against the ledger, not against a literal."""
    a = _asset()
    d = a["denominator"]
    rows = json.loads(LEDGER.read_text(encoding="utf-8"))["rows"]
    assert d["ledger_rows_read"] == len(rows) > 0
    assert len(a["classes"]) == len(rows)
    assert d["rows_with_an_ndi_declaration"] > 0
    assert d["built_veta_schemas"] > 0
    assert d["convert_package_files_scanned"] > 0


def test_every_ledger_row_has_an_entry():
    a = _asset()
    rows = json.loads(LEDGER.read_text(encoding="utf-8"))["rows"]
    missing = [r["v1_class"] for r in rows if r["v1_class"] not in a["classes"]]
    assert not missing, f"{len(missing)} ledger row(s) absent from the asset: {missing}"


def test_the_committed_asset_was_generated_with_the_siblings_present():
    """`did_matlab_available: false` would mean every consumer list in the file
    is ABSENT rather than empty -- and the viewer would render "no migrator"
    for all 102 classes. That must never be what gets committed."""
    a = _asset()
    assert a["denominator"]["did_matlab_available"] is True, (
        "the committed asset was generated without DID-matlab, so its consumer "
        "evidence is absent, not empty -- regenerate with the sibling present")


def test_no_disagreement_with_the_ledger():
    a = _asset()
    dis = a["denominator"]["ledger_disagreements"]
    assert dis == [], (
        f"{len(dis)} class(es) where this tool's migrator-file search and "
        f"tools/coverage.py's `migrator` boolean disagree: {dis}. One of the "
        "two is wrong and the viewer would show both.")


def test_quoted_name_search_is_not_a_substring_search():
    """`image` occurs inside `imageStack`, `ontologyImage` and
    `image_observation`. A substring sweep would attach half the convert
    package to the shortest class names in the ledger."""
    pat = gen._quoted_name_re("image")
    assert pat.search("doc = ndi.document('image', ...)")
    assert pat.search('x = "image";')
    assert not pat.search("doc = ndi.document('imageStack', ...)")
    assert not pat.search("s.did2.convert.migrators_j.image_observation('x')")
    assert not pat.search("% the image is written by ontologyImage")


@pytest.mark.skipif(gen.DIDM is None, reason="DID-matlab sibling absent")
def test_committed_asset_matches_the_generator():
    """The freshness gate. Regenerates in memory and compares bytes."""
    fresh = gen.serialize(gen.build())
    current = ASSET.read_text(encoding="utf-8")
    assert current == fresh, (
        f"{ASSET.relative_to(REPO)} is STALE -- run "
        "`python3 tools/gen_class_walkthrough.py` and commit the result")


def test_skip_condition_is_announced_rather_than_silent():
    """If DID-matlab is absent the freshness test above skips, and a skipped
    gate is a gate nobody ran. Say so out loud so the run's own log carries
    the hole."""
    if gen.DIDM is None:
        print("DENOMINATOR: 1 freshness comparison declared, 0 run -- "
              "DID-matlab absent, so the committed asset is UNVERIFIED here")
    else:
        print(f"DENOMINATOR: 1 freshness comparison declared, 1 run "
              f"(DID-matlab at {gen.DIDM})")
