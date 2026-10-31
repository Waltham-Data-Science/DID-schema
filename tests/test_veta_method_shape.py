"""One `method` shape everywhere (V_eta_method_plan.md, 2026-10-21; Jess Haley: the
inline and standalone method blocks must never drift).

Every `method` structure field in the built tree -- at any depth, on any class --
and the standalone `method` document's own `term` + `parameters` must have the
same recursive (name, type, constraints) shape. Only documentation may differ per
site. `tools/build_v_eta.py` section 12.20 builds every site from one source; this
test checks the result rather than trusting the construction.
"""
import glob
import json
import os

ROOT = os.path.join(os.path.dirname(__file__), "..", "schemas", "did_v2")


def _shape(fields):
    return [(f["name"], f["type"], json.dumps(f.get("constraints") or {}, sort_keys=True),
             _shape(f.get("fields") or [])) for f in fields]


def _walk(fields, cls, path, sites, skipped):
    for f in fields or []:
        here = f"{cls}.{path}{f['name']}"
        if f["name"] == "method":
            if f["type"] == "structure":
                sites[here] = _shape(f.get("fields") or [])
            else:
                skipped.append(f"{here} ({f['type']})")
        _walk(f.get("fields"), cls, path + f["name"] + ".", sites, skipped)


def test_every_method_block_has_the_one_shape():
    files = sorted(glob.glob(os.path.join(ROOT, "**", "*.json"), recursive=True))
    classes, sites, skipped = 0, {}, []
    document = None
    for p in files:
        with open(p) as fh:
            d = json.load(fh)
        if "document_class" not in d:
            continue
        classes += 1
        cls = d["document_class"]["class_name"]
        _walk(d.get("fields"), cls, "", sites, skipped)
        if cls == "method":
            document = _shape([f for f in d["fields"] if f["name"] in ("term", "parameters")])
    print(f"DENOMINATOR: {len(files)} json file(s) read, {classes} class(es) walked; "
          f"{len(sites)} inline `method` structure(s) + the `method` document compared; "
          f"{len(skipped)} non-structure `method` field(s) skipped (did_v1 tombstones "
          f"keep the v1 spelling): {skipped}")
    assert classes > 100, f"read {classes} classes -- schema tree not found?"
    assert document is not None, "no `method` document class in the built tree"
    assert [x[0] for x in document] == ["term", "parameters"]
    assert {"interaction.method", "relation.method",
            "clock_alignment_configuration.method"} <= set(sites), sorted(sites)
    drifted = sorted(k for k, v in sites.items() if v != document)
    assert not drifted, (
        f"`method` blocks whose (name, type, constraints) shape differs from the "
        f"`method` document's term + parameters: {drifted}")
