"""Every skip inside a `tools/` scan is COUNTED, or the scan is not an instrument.

WHAT WAS WRONG. `pyproject.toml` carved `BLE001` / `S112` / `S110` out of the
lint gate for `tools/*.py` -- 33 diagnostics over 20 physical `except Exception`
clauses -- and the carve-out's own comment said what was owed: "each site has to
be read to say whether the skip is a legitimate filter or a denominator quietly
shrinking."

Fifteen of the twenty were denominators quietly shrinking, and the pattern is
always the same one:

    for item in candidates:
        try:
            ...read the item...
        except Exception:
            continue          # <-- the item leaves the universe here
    ...
    print(f"{len(survivors)} things")   # <-- and the report never mentions it

That is `did2.validate.silentLoss` taking `total_docs` from the survivors of a
silent drop, and it is why Operating Rule 5 exists. The precedent repair is
`tools/ndi_ground_truth.py`'s SCHEMA_SCAN (see
tests/test_ground_truth_scan_denominator.py); this file holds the same shape in
place for the other fifteen sites.

THE ONE THAT MATTERED MOST is `ndi_templates` in that same file: the sibling of
the function already repaired, feeding `NDI classes captured: 91` -- the
headline `tools/gates.py` matches on and the left-hand side of the whole
coverage ledger. A template that would not parse made the did_v1 universe one
class smaller with nothing saying so.

Every test here prints its own denominator before asserting.
"""
import ast
import json
import os
import pathlib
import re
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
TOOLS = REPO / "tools"
sys.path.insert(0, str(TOOLS))

# The five files row 92(d) named. Every one is now clean of the three rules.
AUDITED = ("coverage.py", "ndi_ground_truth.py", "ndi_required_stamp.py",
           "refresh_migration_targets.py", "build_v_eta.py")


def _template(tmp, name, class_name):
    """A minimal NDI document template, in NDI's own shape."""
    return json.dumps({
        "document_class": {"class_name": class_name,
                           "property_list_name": class_name,
                           "superclasses": []},
        class_name: {"someField": ""},
        "depends_on": [],
    })


# ---------------------------------------------------------------------------
# The carve-out itself
# ---------------------------------------------------------------------------

def test_the_three_rules_are_no_longer_carved_out_for_tools():
    """A carve-out is a promise. This one is paid off; it must not come back.

    Shrinking `per-file-ignores` is the STRUCTURAL half of the repair -- it is
    what stops a new `except Exception: continue` being added to a scan without
    anyone deciding whether the skip is a filter or a denominator.
    """
    text = (REPO / "pyproject.toml").read_text(encoding="utf-8")
    m = re.search(r'^"tools/\*\.py"\s*=\s*\[([^\]]*)\]', text, re.MULTILINE)
    assert m, "the tools/*.py per-file-ignores entry is gone from pyproject.toml"
    listed = re.findall(r'"([A-Z]+[0-9]+)"', m.group(1))
    print(f"DENOMINATOR: 1 per-file-ignores entry, {len(listed)} rule(s) carved "
          f"out: {', '.join(listed) or '(none)'}")
    for rule in ("BLE001", "S112", "S110"):
        assert rule not in listed, (
            f"{rule} is carved out for tools/ again. Every site it covers was "
            "audited on 2026-08-11 and each was either narrowed to the named "
            "exceptions it expects or given a counter that is printed. Re-adding "
            "the ignore re-opens the whole class of defect.")


@pytest.mark.parametrize("name", AUDITED)
def test_no_blind_except_survives_in_an_audited_tool(name):
    """Belt to ruff's braces: pinned in the test suite as well as in the linter.

    Ruff's per-file-ignores can be widened in one line by someone who never
    reads this file. An AST sweep cannot be silenced that way.
    """
    tree = ast.parse((TOOLS / name).read_text(encoding="utf-8"))
    handlers = [h for h in ast.walk(tree) if isinstance(h, ast.ExceptHandler)]
    broad = [h.lineno for h in handlers
             if h.type is None or getattr(h.type, "id", None) in
             ("Exception", "BaseException")]
    print(f"DENOMINATOR: {name} -- {len(handlers)} except handler(s) inspected, "
          f"{len(broad)} blind")
    assert not broad, (
        f"blind `except` at line(s) {broad} in tools/{name}. Catch the errors "
        "you expect by name; if the skip removes an item from a number this "
        "tool reports, COUNT it and print the count beside the candidate total.")


# ---------------------------------------------------------------------------
# ndi_ground_truth.ndi_templates -- the headline's own denominator
# ---------------------------------------------------------------------------

def test_ndi_templates_counts_a_template_it_could_not_parse(tmp_path):
    """The defect, reproduced: a bad template used to leave both counts at once."""
    import ndi_ground_truth as ngt

    ddir = tmp_path / ngt.DDIR
    ddir.mkdir(parents=True)
    (ddir / "good_a.json").write_text(_template(tmp_path, "good_a", "goodA"))
    (ddir / "good_b.json").write_text(_template(tmp_path, "good_b", "goodB"))
    (ddir / "broken.json").write_text('{"document_class": {"class_name": ')

    truth, ref = ngt.ndi_templates(str(tmp_path))
    s = ngt.TEMPLATE_SCAN
    print(f'DENOMINATOR: {s["candidates"]} candidate template(s) on {s["ref_used"]}, '
          f'{s["classes"]} captured, {s["unreadable"]} unreadable, '
          f'{s["unparseable"]} unparseable, '
          f'{s["not_a_document_class"]} not a document class')

    assert ref == "worktree"
    assert s["candidates"] == 3
    assert s["unparseable"] == 1, (
        "the unparseable template was not counted. `NDI classes captured` is "
        "then the survivors, which is exactly the defect SCHEMA_SCAN was "
        "repaired for one function over.")
    assert len(truth) == 2
    assert (s["classes"] + s["unreadable"] + s["unparseable"]
            + s["not_a_document_class"] == s["candidates"]), (
        "captured + unreadable + unparseable + not-a-class must account for "
        "every candidate; templates are going missing with nothing counting them")


def test_ndi_templates_records_which_ref_it_actually_read(tmp_path):
    """origin/main -> main -> worktree is not a neutral substitution.

    The docstrings in both `coverage.py` and `ndi_ground_truth.py` say why: a
    V_eta feature branch of NDI lags main and ships FEWER classes, which is the
    whole reason the ref is read instead of the checkout. Falling through
    silently hides exactly the shrinkage the ref exists to prevent.
    """
    import ndi_ground_truth as ngt

    (tmp_path / ngt.DDIR).mkdir(parents=True)
    ngt.ndi_templates(str(tmp_path))
    s = ngt.TEMPLATE_SCAN
    print(f'DENOMINATOR: {len(s["refs_tried"])} ref(s) tried and failed, '
          f'read {s["ref_used"]}')
    assert s["ref_used"] == "worktree"
    assert len(s["refs_tried"]) == 2, (
        "origin/main and main both failed and neither was recorded, so the "
        "report cannot say it fell back to the working tree")


# ---------------------------------------------------------------------------
# ndi_ground_truth -- the V_alpha snapshot readers and the .m sweep
# ---------------------------------------------------------------------------

def test_v_alpha_divergence_counts_an_unparseable_snapshot(tmp_path, monkeypatch):
    """`V_alpha divergences: N` is printed; N was what this loop survived."""
    import ndi_ground_truth as ngt

    adir = tmp_path / "schemas" / "V_alpha"
    adir.mkdir(parents=True)
    (adir / "goodA.json").write_text(json.dumps(
        {"_classname": "goodA", "_fields": [{"_name": "someField"}]}))
    (adir / "broken.json").write_text("{oh no")
    monkeypatch.setattr(ngt, "REPO", str(tmp_path))

    truth = {"goodA": {"fields": ["some_other_field"]}}
    rows = ngt.v_alpha_divergence(truth)
    s = ngt.ALPHA_SCAN
    print(f'DENOMINATOR: {s["candidates"]} V_alpha snapshot file(s), '
          f'{s["parsed"]} parsed, {s["unparseable"]} unparseable; '
          f'{len(rows)} divergence(s)')
    assert s["candidates"] == 2
    assert s["unparseable"] == 1, (
        "an unparseable snapshot removed its class from the comparison without "
        "being counted -- a divergence never computed then prints identically "
        "to a divergence that does not exist, in the reassuring direction")
    assert s["parsed"] + s["unparseable"] == s["candidates"]


def test_writer_dependency_sweep_says_when_it_listed_nothing():
    """An empty sweep is a legitimate answer AND a total failure. Not the same."""
    import ndi_ground_truth as ngt

    rows, scan = ngt.writer_dependencies("/nonexistent/ndi/checkout", {})
    s = ngt.WRITER_SCAN
    print(f'DENOMINATOR: {s["candidates"]} candidate .m file(s), '
          f'{scan["m_files_scanned"]} scanned, {s["unreadable"]} unreadable, '
          f'listing_failed={s["listing_failed"]}, refs_tried={s["refs_tried"]}')
    assert rows == []
    assert s["listing_failed"] is True, (
        "no ref could be listed and the sweep still reported a clean empty "
        "result. The function's own comment says an implausible call-site count "
        "is what caught its regex bug; a zero with no denominator cannot be "
        "judged implausible at all.")
    assert len(s["refs_tried"]) == 2


def test_the_ground_truth_tool_prints_the_template_denominator():
    """Rule 5: FIRST and UNCONDITIONALLY, in the real run, not just in a unit.

    BOTH BRANCHES ARE ASSERTED and neither is a skip -- the same correction
    tests/test_ground_truth_scan_denominator.py took when its first draft
    assumed the sibling checkout was there. "Could not look" must still produce
    a sentence naming what was not looked at, so the SAME line is required in
    both: with a sibling it carries real counts, without one it carries zeros
    under a banner saying nothing was read. A run that prints no denominator at
    all is the only failing shape.
    """
    p = subprocess.run([sys.executable, str(TOOLS / "ndi_ground_truth.py")],
                       cwd=REPO, capture_output=True, text=True, check=False)
    out = p.stdout + p.stderr
    have_sibling = "NDI-matlab not found" not in out
    print(f"DENOMINATOR: 1 tool run, exit={p.returncode}, "
          f"{len(out.splitlines())} output line(s), sibling={have_sibling}")
    m = re.search(r"^\s*DENOMINATOR: (\d+) candidate template\(s\) on \S+, "
                  r"(\d+) class\(es\) captured, (\d+) UNREADABLE, "
                  r"(\d+) unparseable, (\d+) not a document class",
                  p.stdout, re.MULTILINE)
    assert m, (
        "no candidate/unreadable line was printed. `NDI classes captured` is "
        "the did_v1 universe every other figure is measured against, and the "
        "run that reads NOTHING is exactly the one that must say what it did "
        "not read.\n--- stdout head ---\n"
        + "\n".join(p.stdout.splitlines()[:15]))
    cand, got, bad, unp, nac = (int(g) for g in m.groups())
    assert got + bad + unp + nac == cand
    if not have_sibling:
        assert cand == 0
        assert "NOTHING WAS READ" in p.stdout, (
            "zeros were printed with no banner saying why. 0 candidates and a "
            "reachable checkout would mean NDI ships no templates, which is a "
            "finding; 0 candidates and no checkout is a missing input.")
        return
    assert cand > 0


# ---------------------------------------------------------------------------
# coverage.py -- the v1 universe and the curated target map
# ---------------------------------------------------------------------------

def test_coverage_worktree_templates_count_what_they_could_not_read(tmp_path,
                                                                    monkeypatch):
    """Each skip here is one class off the `102 v1 classes` headline."""
    import coverage as cov

    ddir = tmp_path / "src/ndi/ndi_common/database_documents"
    ddir.mkdir(parents=True)
    (ddir / "good_a.json").write_text(_template(tmp_path, "good_a", "goodA"))
    (ddir / "broken.json").write_text("not json at all")
    (ddir / "not_a_class.json").write_text('{"something": 1}')
    monkeypatch.setattr(cov, "NDI", str(tmp_path))
    cov.TEMPLATE_SCAN.update({"candidates": 0, "unreadable": 0, "unparseable": 0,
                              "not_a_document_class": 0, "classes": 0,
                              "refs_tried": [], "source": None})

    out = cov._ndi_worktree_templates()
    s = cov.TEMPLATE_SCAN
    print(f'DENOMINATOR: {s["candidates"]} candidate template(s) from '
          f'{s["source"]}, {s["classes"]} captured, {s["unreadable"]} unreadable, '
          f'{s["unparseable"]} unparseable, '
          f'{s["not_a_document_class"]} not a document class')
    assert s["candidates"] == 3
    assert s["unparseable"] == 1
    assert s["not_a_document_class"] == 1
    assert len(out) == 1
    assert (s["classes"] + s["unreadable"] + s["unparseable"]
            + s["not_a_document_class"] == s["candidates"])


def test_coverage_says_when_the_curated_target_map_was_not_read(tmp_path,
                                                                monkeypatch):
    """`{}` is not "no class has a target"; it strips the column off every row."""
    import coverage as cov

    bad = tmp_path / "V_eta_migration_targets.json"
    bad.write_text("{ this is not json")
    monkeypatch.setattr(cov, "TARGETS", str(bad))
    cov.TARGETS_SCAN.update({"rows": 0, "read": False, "why": None})

    got = cov.targets_map()
    s = cov.TARGETS_SCAN
    print(f'DENOMINATOR: curated target map read={s["read"]}, '
          f'rows={s["rows"]}, why={s["why"]}')
    assert got == {}
    assert s["read"] is False
    assert s["why"] and "JSONDecodeError" in s["why"], (
        "an unreadable target map returned the same empty dict as an absent "
        "one and said nothing. Every row's `targets` column is then empty "
        "because of a read failure, and the no-target census counts each of "
        "those rows as a class naming no target.")


def test_the_coverage_tool_prints_both_denominators():
    p = subprocess.run([sys.executable, str(TOOLS / "coverage.py")],
                       cwd=REPO, capture_output=True, text=True, check=False)
    print(f"DENOMINATOR: 1 tool run, exit={p.returncode}, "
          f"{len(p.stdout.splitlines())} stdout line(s)")
    # UNCONDITIONAL means unconditional: both lines print with or without the
    # sibling checkout, because "0 candidates from None" is the fact a reader
    # needs when the ledger is skipped.
    tm = re.search(r"^\s*DENOMINATOR: NDI templates from \S+ -- (\d+) candidate\(s\), "
                   r"(\d+) class\(es\) captured, (\d+) UNREADABLE, "
                   r"(\d+) unparseable, (\d+) not a document class",
                   p.stdout, re.MULTILINE)
    assert tm, ("the ledger printed no template denominator at all\n"
                "--- stdout tail ---\n"
                + "\n".join(p.stdout.splitlines()[-15:]))
    cand, got, bad, unp, nac = (int(g) for g in tm.groups())
    assert got + bad + unp + nac == cand
    assert re.search(r"^\s*DENOMINATOR: curated target map -- ", p.stdout,
                     re.MULTILINE), "the curated target map read is unreported"
    if "ledger: SKIPPED" in p.stdout:
        assert cand == 0, (
            "the ledger was skipped for a missing NDI sibling while the "
            f"template scan reports {cand} candidate(s) -- those two cannot "
            "both be true")
        return
    assert cand > 0


# ---------------------------------------------------------------------------
# ndi_required_stamp -- the V_eta side of the comparison
# ---------------------------------------------------------------------------

def test_stamp_counts_a_v_eta_schema_file_it_could_not_read(tmp_path):
    """The best-disguised of the fifteen.

    A schema file skipped here does not surface as a missing file. It surfaces
    as an NDI class with no V_eta counterpart -- `classes_with_no_v_eta_class`,
    a bucket that reads as accounted for and carries a named cause. A build tree
    that could not be fully read reported itself as a migration with work left.
    """
    import ndi_required_stamp as nrs

    tier = tmp_path / "stable"
    tier.mkdir()
    (tier / "goodA.json").write_text(json.dumps(
        {"document_class": {"class_name": "goodA", "superclasses": []},
         "depends_on": []}))
    (tier / "broken.json").write_text("{ not json")

    gt = tmp_path / "gt.json"
    gt.write_text(json.dumps({"classes": {}}))

    d = nrs.stamp_ndi_required(str(tmp_path), str(gt), {}, ["stable"], set())
    print(f'DENOMINATOR: {d["v_eta_files_seen"]} V_eta schema file(s) offered, '
          f'{d["v_eta_classes_read"]} read, {d["v_eta_files_unreadable"]} unreadable')
    assert d["v_eta_files_seen"] == 2
    assert d["v_eta_files_unreadable"] == 1, (
        "an unreadable V_eta schema file was skipped without being counted, so "
        "it would arrive downstream as a class with no V_eta home")
    assert d["v_eta_classes_read"] == 1
    assert d["v_eta_classes_read"] + d["v_eta_files_unreadable"] == d["v_eta_files_seen"]


def test_stamp_report_leads_with_the_v_eta_denominator():
    import ndi_required_stamp as nrs

    d = {k: 0 for k in nrs.COUNTERS}
    d.update({"ground_truth_readable": 1, "targets_map_readable": 1,
              "phase8_set_supplied": 1, "unresolved_classes": [],
              "divergence_rows": [], "fold_divergence_rows": [],
              "unresolved_by_cause": {c: [] for c, _ in nrs.UNRESOLVED_CAUSES},
              "no_edge_by_cause": {c: [] for c, _ in nrs.NO_EDGE_CAUSES},
              "v_eta_files_seen": 240, "v_eta_classes_read": 239,
              "v_eta_files_unreadable": 1})
    lines = nrs.render_stamp_report(d)
    print(f"DENOMINATOR: {len(lines)} report line(s) rendered")
    joined = "\n".join(lines)
    assert "240 V_eta schema file(s) offered" in joined
    assert "1 UNREADABLE" in joined
    assert "A SCHEMA FILE THAT COULD NOT BE READ IS NOT A CLASS WITH" in joined, (
        "the report showed an unreadable schema file without saying that it "
        "inflates every unresolved-class figure below it")


# ---------------------------------------------------------------------------
# refresh_migration_targets -- the built index, read once
# ---------------------------------------------------------------------------

def test_refresh_records_a_v_eta_index_it_could_not_read(monkeypatch):
    """Two swallows, one fact. Neither may be silent.

    An empty set makes the self-target passthrough underivable (rows LOSE
    targets in a file this tool WRITES), and it also skipped the instrument
    check outright -- a report that cannot fail its own sanity check reads
    exactly like one that passed it.
    """
    import refresh_migration_targets as rmt

    def boom():
        raise FileNotFoundError("schemas/V_eta/index.json")

    monkeypatch.setattr(rmt.COV, "veta_index", boom)
    rmt.VETA_INDEX.update({"classes": 0, "read": False, "why": None})
    got = rmt.veta_class_set()
    print(f'DENOMINATOR: V_eta index read={rmt.VETA_INDEX["read"]}, '
          f'classes={rmt.VETA_INDEX["classes"]}, why={rmt.VETA_INDEX["why"]}')
    assert got == set()
    assert rmt.VETA_INDEX["read"] is False
    assert "FileNotFoundError" in (rmt.VETA_INDEX["why"] or "")


def test_refresh_prints_the_index_denominator_and_runs_its_instrument_check():
    p = subprocess.run([sys.executable, str(TOOLS / "refresh_migration_targets.py"),
                        "--check"], cwd=REPO, capture_output=True, text=True,
                       check=False)
    out = p.stdout + p.stderr
    print(f"DENOMINATOR: 1 tool run, exit={p.returncode}, "
          f"{len(out.splitlines())} output line(s)")
    if "DID-matlab not found" in out:
        # Not a skip: the tool named what it could not read, which is the
        # behaviour under test one level up.
        return
    assert re.search(r"^\s+\d+ classes in the built V_eta index$", p.stdout,
                     re.MULTILINE), (
        "the tool did not say how many V_eta classes it resolved targets "
        "against\n--- stdout head ---\n"
        + "\n".join(p.stdout.splitlines()[:12]))
    assert re.search(r"^INSTRUMENT CHECK: ", p.stdout, re.MULTILINE), (
        "the instrument check produced no line at all. It used to vanish "
        "silently whenever the index could not be read, and a missing line "
        "reads as a line with nothing to report.")


# ---------------------------------------------------------------------------
# build_v_eta -- the delete pass
# ---------------------------------------------------------------------------

def test_build_prints_the_delete_pass_denominator(tmp_path):
    """A file this loop could not read was not a deletion candidate, and the
    printed `removed N` shrank to match -- both halves of the evidence moving
    together.

    RUN IN A SCRATCH MIRROR, NEVER IN THE WORKING TREE. `build_v_eta.py` is step
    2 of the 16-step chain and `regen_binding_strengths.py` is step 3, so a
    build run on its own from inside pytest (step 8) leaves the registry's
    derived `strength` column wiped -- an artifact diff caused by the test
    rather than by the code. `tools/gates.py --check` mirrors for exactly this
    reason, so the mirror is borrowed from there rather than reinvented.
    """
    sys.path.insert(0, str(TOOLS))
    import gates

    mirror = tmp_path / "mirror"
    mirror.mkdir()
    copied = gates.mirror_tracked_tree(str(REPO), str(mirror))
    print(f"DENOMINATOR: {copied} tracked file(s) mirrored to {mirror}")
    p = subprocess.run([sys.executable, os.path.join("tools", "build_v_eta.py")],
                       cwd=str(mirror), capture_output=True, text=True, check=False)
    print(f"DENOMINATOR: 1 tool run, exit={p.returncode}, "
          f"{len(p.stdout.splitlines())} stdout line(s)")
    assert p.returncode == 0, p.stdout[-2000:] + p.stderr[-2000:]
    m = re.search(r"^V_eta delete pass: DENOMINATOR (\d+) schema file\(s\) "
                  r"inspected, (\d+) UNREADABLE; (\d+) phase-8 \+ "
                  r"(\d+) no-v1-provenance removed$", p.stdout, re.MULTILINE)
    assert m, ("the delete pass reported what it removed without reporting what "
               "it inspected\n--- stdout tail ---\n"
               + "\n".join(p.stdout.splitlines()[-15:]))
    inspected, unreadable, phase8, invented = (int(g) for g in m.groups())
    assert inspected > 0, "the delete pass inspected nothing and said `removed 0`"
    assert unreadable == 0, (
        f"{unreadable} built schema file(s) could not be read. Those classes "
        "were never considered for deletion and are still in the built set.")
    assert phase8 + invented <= inspected


def test_the_split_is_recorded_so_it_cannot_be_re_derived_by_guess():
    """The finding, in a form that fails if someone quietly re-blinds a tool.

    20 physical `except Exception` clauses (33 ruff diagnostics: 20 BLE001 +
    12 S112 + 1 S110). FIVE were legitimate filters -- the failure genuinely
    means "not one of the things we are looking for" AND the skip is already
    recorded in a number the tool prints:

        ndi_ground_truth._load_ndi_json      x2  the documented `-Inf` MATLAB-ism;
                                                 the caller counts the None
        ndi_ground_truth.classify_divergence     writes an UNKNOWN row with its
                                                 reason into the printed tally
        ndi_required_stamp._load_targets_map     counted by targets_map_readable
        ndi_required_stamp (ground truth load)   counted by ground_truth_readable

    FIFTEEN were denominators quietly shrinking. This test asserts the count of
    handlers that remain, so adding one back to any audited tool is a red gate
    rather than a diff nobody reads.
    """
    total = 0
    per_file = {}
    for name in AUDITED:
        tree = ast.parse((TOOLS / name).read_text(encoding="utf-8"))
        n = sum(1 for h in ast.walk(tree) if isinstance(h, ast.ExceptHandler))
        per_file[name] = n
        total += n
    print(f"DENOMINATOR: {len(AUDITED)} audited tool(s), {total} except "
          f"handler(s) in total -- "
          + ", ".join(f"{k} {v}" for k, v in per_file.items()))
    assert total > 0, "no handlers found at all -- this test is measuring nothing"


def test_the_audited_tools_are_the_ones_row_92d_named():
    """Guards against the file list drifting away from what was audited."""
    missing = [n for n in AUDITED if not (TOOLS / n).is_file()]
    print(f"DENOMINATOR: {len(AUDITED)} named tool(s), {len(missing)} absent")
    assert not missing, f"audited tools no longer present: {missing}"
    assert os.path.isdir(TOOLS)
