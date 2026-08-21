"""Self-tests for bar2_gap.py -- run on the fast gate, no corpus artifacts needed.

They pin the CLASSIFICATION LOGIC against a synthetic ledger + synthetic report,
so they are stable regardless of the real ledger's current state. The one thing
they deliberately do NOT mock is the husk/bridge overlay -- that is the tool's
own knowledge and must be exercised as written.
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parent / "tools"
TOOL = TOOLS / "bar2_gap.py"
sys.path.insert(0, str(TOOLS))
import bar2_gap as B  # noqa: E402


def _row(rung3, targets=None, decided=None, target_source="emitted",
         disposition="in_progress"):
    ladder = [{"stage": 3, "state": rung3}]
    return {
        "v1_class": "x", "disposition": disposition,
        "targets": targets or [], "decided_targets": decided or [],
        "target_source": target_source,
        "stage": {"ladder": ladder},
    }


def test_rung3_no_is_superseded():
    v, _ = B.verdict_for("some_class",
                         _row("no", targets=["old"], decided=["new"]))
    assert v == "SUPERSEDED"


def test_rung3_yes_is_at_decided():
    v, _ = B.verdict_for("some_class", _row("yes", decided=["new"]))
    assert v == "AT_DECIDED"


def test_emitted_no_gap_is_at_decided():
    # rung 3 not-measured because emitted == decided (no authored gap)
    v, _ = B.verdict_for("tuningcurve_calc",
                         _row("not measured", targets=["tuning_curve_calculation"],
                              target_source="emitted"))
    assert v == "AT_DECIDED"


def test_no_target_is_undecided():
    v, _ = B.verdict_for("mystery",
                         _row("not measured", targets=[], target_source="unknown"))
    assert v == "UNDECIDED"


def test_persist_self_is_at_decided():
    v, _ = B.verdict_for("session",
                         _row("not measured", targets=["session"],
                              target_source="passthrough", disposition="persist"))
    assert v == "AT_DECIDED"


def test_husk_overlay_fires_regardless_of_ledger():
    # even with a rung-3 'yes' row, the husk overlay wins: source survives.
    v, _ = B.verdict_for("stimulus_response_scalar_parameters_basic",
                         _row("yes", decided=["method_parameters"]))
    assert v == "HUSK"


def test_bridge_overlay_fires():
    v, _ = B.verdict_for("epochfiles_ingested", _row("yes"))
    assert v == "BRIDGE"


def _write(tmp, name, census, quar=0, orph=0, frag=0):
    rep = {
        "corpus": name, "quarantine_count": quar,
        "reference_integrity": {"orphan_count": orph}, "fragment_count": frag,
        "source_census": {"total": sum(census.values()),
                          "by_class": {k: {"total_docs": v} for k, v in census.items()}},
    }
    p = Path(tmp) / f"{name}-summary.json"
    p.write_text(json.dumps(rep))
    return p


def _ledger(tmp, rows):
    p = Path(tmp) / "ledger.json"
    p.write_text(json.dumps({"rows": rows}))
    return p


def test_end_to_end_not_at_bar2(tmp_path):
    led = _ledger(tmp_path, [
        _row("no", targets=["stimulus_presentation"],
             decided=["timed_sequence_manipulation"]) | {"v1_class": "stimulus_presentation"},
        _row("yes", decided=["subject"]) | {"v1_class": "subject"},
    ])
    _write(tmp_path, "K", {"stimulus_presentation": 11, "subject": 3,
                           "stimulus_response_scalar_parameters_basic": 273})
    rc = B.run([str(tmp_path)], ledger_path=led)
    assert rc == 1  # a gap exists


def test_end_to_end_clean_corpus_is_at_bar2(tmp_path):
    led = _ledger(tmp_path, [
        _row("yes", decided=["subject"]) | {"v1_class": "subject"},
        _row("yes", decided=["session"]) | {"v1_class": "session"},
    ])
    _write(tmp_path, "Clean", {"subject": 3, "session": 1})
    rc = B.run([str(tmp_path)], ledger_path=led)
    assert rc == 0  # every present class AT_DECIDED and Bar-1 clean


def test_no_reports_returns_2(tmp_path):
    led = _ledger(tmp_path, [])
    rc = B.run([str(tmp_path)], ledger_path=led)
    assert rc == 2


def test_tool_runs_as_script(tmp_path):
    led = _ledger(tmp_path, [_row("yes", decided=["subject"]) | {"v1_class": "subject"}])
    _write(tmp_path, "S", {"subject": 3})
    out = subprocess.run([sys.executable, str(TOOL), str(tmp_path), "--ledger", str(led)],
                         capture_output=True, text=True, check=False)
    assert out.returncode == 0
    assert "DENOMINATOR" in out.stdout
    assert "corpus S" in out.stdout
