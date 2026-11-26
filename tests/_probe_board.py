"""A status board rendered with open classes, for tests of its machinery.

The open set is EMPTY since 2026-11-19 ([retired classes leave V2] step 3,
did_v2_go_forward_class_audit.md): the last eleven retire classes were deleted,
so the committed board (docs/generated/did_v2_STATUS.md and the
`open_class_state` block of schemas/generated/did_v2_decisions.json) has no
open-class row. The board's sweep and renderer still work on names, and these
eleven are still named all over the siblings' code as v1 classes, so a test of
the machinery asks the sweep about them, or reads a board rendered in a scratch
copy of the tracked tree whose index holds them as `retire` classes still in
the tree. Rendering needs the siblings: without them the copy can only reuse
the committed snapshot, which has no open row.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROBE_CLASSES = (
    "acquisition_epoch", "app", "calculator", "daqreader",
    "daqreader_epochdata_ingested", "daqreader_image_epochdata_ingested",
    "epochid", "filenavigator", "stimulus_presentation", "stimulus_response",
    "stimulus_response_scalar_parameters")

_CACHE = {}


def probe_board(did_root, ndi_root):
    """(status text, open_class_state) of the probe board; rendered once."""
    key = (did_root, ndi_root)
    if key in _CACHE:
        return _CACHE[key]
    tmp = tempfile.mkdtemp(prefix="probe-board-")
    try:
        names = subprocess.run(["git", "ls-files"], cwd=REPO_ROOT, check=True,
                               capture_output=True, text=True).stdout.split("\n")
        copied = 0
        for rel in names:
            src = os.path.join(REPO_ROOT, rel)
            if rel and os.path.isfile(src):
                dst = os.path.join(tmp, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                copied += 1
        assert copied > 0, "no tracked file was copied"
        ix = os.path.join(tmp, "schemas", "generated", "index.json")
        with open(ix) as fh:
            idx = json.load(fh)
        for cn in PROBE_CLASSES:
            idx["schemas"].append({
                "class_name": cn, "family": "retiring", "class_version": "1.0.0",
                "superclasses": ["base"],
                "path": f"schemas/did_v2/retiring/{cn}.json",
                "disposition": "retire",
                "disposition_note": "probe: deleted 2026-11-19, restored in a scratch copy"})
        with open(ix, "w") as fh:
            json.dump(idx, fh, indent=2)
        p = subprocess.run([sys.executable, "tools/status_board.py",
                            "--did", did_root, "--ndi", ndi_root],
                           cwd=tmp, capture_output=True, text=True, check=False)
        assert p.returncode == 0, p.stdout + p.stderr
        with open(os.path.join(tmp, "docs", "generated", "did_v2_STATUS.md")) as fh:
            text = fh.read()
        with open(os.path.join(tmp, "schemas", "generated", "did_v2_decisions.json")) as fh:
            ocs = json.load(fh)["open_class_state"]
    finally:
        shutil.rmtree(tmp)
    _CACHE[key] = (text, ocs)
    return _CACHE[key]
