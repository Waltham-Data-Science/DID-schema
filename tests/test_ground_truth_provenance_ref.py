"""The provenance walk in `tools/ndi_ground_truth.py` must be REPRODUCIBLE.

`schemas/V_eta_ndi_ground_truth.json` records `ndi_ref: "origin/main"` and the
tool's docstring says it reads origin/main and never a feature branch. Until
2026-08-11 `classify_divergence` walked `--all`, so every
`v_alpha_divergence[].provenance` verdict was a property of whichever refs the
local NDI clone happened to carry. In the committed artifact 12 of 67 rows had
in fact been read off refs that are not ancestors of origin/main -- three from
`origin/audri_documents`, one from `origin/feature/newvhlabimport`, and eight
whose source ref no longer exists in any clone here at all.

These tests do not read NDI. They build a throwaway repository in which the
answer under the declared ref and the answer under `--all` DIFFER, so the
property is pinned by behaviour rather than by inspecting the argv:

  test_provenance_walk_ignores_refs_outside_ndi_ref
        an off-ref branch carries an EARLIER add of the same template basename,
        with different fields. Walking `--all` takes it (`--reverse` -> earliest
        first) and the verdict flips. Fails if the walk consults any ref other
        than the one it was given.

  test_provenance_walk_finds_a_template_that_arrived_by_rename
        the template's only add on the declared ref is a rename. Git's default
        rename detection reports it as R, which `--diff-filter=A` skips, so the
        class reads as "no add-commit found" -- a false UNKNOWN. On real NDI
        that alone accounted for 14 of the 67 classes. Fails if `--no-renames`
        is dropped.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))

import ndi_ground_truth as GT  # noqa: E402  (needs the sys.path line above)


def _git(repo, *args, when=None):
    env = dict(os.environ)
    env.update({
        "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.com",
    })
    if when:
        env["GIT_AUTHOR_DATE"] = when
        env["GIT_COMMITTER_DATE"] = when
    return subprocess.run(["git", "-C", str(repo)] + list(args),
                          capture_output=True, text=True, check=True, env=env)


def _template(fields):
    """An NDI-shaped document template declaring `fields` in its property block."""
    return json.dumps({
        "document_class": {
            "class_name": "widget",
            "property_list_name": "widget",
            "class_version": 1,
            "superclasses": [],
        },
        "widget": {f: [] for f in fields},
    }, indent=1)


def _write(repo, rel, text):
    p = os.path.join(str(repo), rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        f.write(text)


def _init(repo):
    _git(repo, "init", "-q", "-b", "main")
    _write(repo, "README.md", "root\n")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-qm", "root", when="2020-01-01T00:00:00+0000")


def _inputs(template_fields, alpha_fields):
    """The (truth, div) pair `classify_divergence` consumes.

    It recomputes the V_alpha field set as
        only_in_our_snapshot | (truth[cn].fields - only_in_ndi_template)
    so these two sets are what actually decide NDI-CHANGED vs DID-INVENTED.
    """
    template_fields, alpha_fields = set(template_fields), set(alpha_fields)
    truth = {"widget": {"fields": sorted(template_fields)}}
    div = {"widget": {
        "ndi_class": "widget",
        "only_in_our_snapshot": sorted(alpha_fields - template_fields),
        "only_in_ndi_template": sorted(template_fields - alpha_fields),
    }}
    return truth, div


def test_provenance_walk_ignores_refs_outside_ndi_ref(tmp_path):
    repo = tmp_path / "ndi"
    repo.mkdir()
    _init(repo)

    # An UNMERGED branch adds the same template basename EARLIER, with a
    # different field set. This is the shape of the real defect: `treatment_drug`
    # was classified from `origin/feature/newvhlabimport`, and `app` / `element` /
    # `projectvar` from `origin/audri_documents`.
    _git(repo, "checkout", "-q", "-b", "side")
    _write(repo, "elsewhere/widget.json", _template(["field_from_an_off_main_branch"]))
    _git(repo, "add", "elsewhere/widget.json")
    _git(repo, "commit", "-qm", "off-ref add", when="2020-02-01T00:00:00+0000")

    _git(repo, "checkout", "-q", "main")
    _write(repo, "database_documents/widget.json", _template(["field_on_main"]))
    _git(repo, "add", "database_documents/widget.json")
    _git(repo, "commit", "-qm", "on-ref add", when="2020-03-01T00:00:00+0000")

    truth, div = _inputs(["field_on_main"], ["field_on_main"])

    out = GT.classify_divergence(str(repo), "main", truth, div)["widget"]

    # The snapshot matches the first version ON THE DECLARED REF exactly, so the
    # only answer derivable from `main` is NDI-CHANGED. A walk that reaches the
    # `side` branch sees `field_from_an_off_main_branch` first and says
    # DID-INVENTED instead.
    assert out["verdict"] == "NDI-CHANGED", (
        f"provenance verdict came from outside the declared ref: {out!r}")
    assert out["first_version_fields"] == ["field_on_main"]
    assert out["why"] == "first NDI version 2020-03-01"

    # And the off-ref branch really would have changed the answer -- otherwise
    # this test would pass for a walk that still reads every ref.
    sole = GT.classify_divergence(str(repo), "side", truth, div)["widget"]
    assert sole["verdict"] == "DID-INVENTED"


def test_provenance_walk_finds_a_template_that_arrived_by_rename(tmp_path):
    repo = tmp_path / "ndi"
    repo.mkdir()
    _init(repo)

    _write(repo, "database_documents/legacy_widget.json", _template(["field_on_main"]))
    _git(repo, "add", "database_documents/legacy_widget.json")
    _git(repo, "commit", "-qm", "add under the old name",
         when="2020-02-01T00:00:00+0000")

    _git(repo, "mv", "database_documents/legacy_widget.json",
         "database_documents/widget.json")
    _git(repo, "commit", "-qm", "rename to the modern name",
         when="2020-03-01T00:00:00+0000")

    truth, div = _inputs(["field_on_main"], ["field_on_main"])

    out = GT.classify_divergence(str(repo), "main", truth, div)["widget"]

    assert out["verdict"] != "UNKNOWN", (
        "the template's only add on `main` is a rename and the walk missed it: "
        f"{out!r}")
    assert out["why"] == "first NDI version 2020-03-01"
    assert out["first_version_fields"] == ["field_on_main"]


def test_committed_artifact_ndi_ref_is_the_ref_the_walk_declares():
    """The artifact's `ndi_ref` is what the tests above pin the walk to."""
    path = os.path.join(REPO_ROOT, "schemas", "V_eta_ndi_ground_truth.json")
    doc = json.loads(Path(path).read_text())
    assert doc["ndi_ref"] == "origin/main"
    div = doc["v_alpha_divergence"]
    # DENOMINATOR first (operating rule 5): every row carries a provenance
    # verdict, and none of them may be the "the walk never found the file" kind
    # -- that reason is what 14 classes degraded to when the ref was pinned
    # without `--no-renames`.
    assert len(div) > 0
    assert all("provenance" in r for r in div)
    unlocated = [r["ndi_class"] for r in div
                 if r["provenance"].get("why", "").startswith(
                     ("no add-commit", "no ref to walk"))]
    assert unlocated == [], (
        f'{len(unlocated)} of {len(div)} divergent classes have no located first version on {doc["ndi_ref"]}: {unlocated}')
