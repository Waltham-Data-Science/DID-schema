"""Integrity of ``schemas/V_delta/index.json`` against the per-class schema files.

``index.json`` carries a per-entry ``superclasses`` mirror that MUST equal each
class's own ``document_class.superclasses``. If it drifts, any consumer that
resolves ``isa()`` / inheritance from the index (rather than from the class
files) silently gets false negatives -- which is exactly what happened: the
mirror had dropped every non-``base`` parent for 14 classes.

This is also the first V_delta-tier test (``test_schemas.py`` parametrizes only
V_beta / V_gamma), so it doubles as basic coverage that V_delta exists and
every indexed class file is loadable.
"""
import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_PATH = os.path.join(ROOT, "schemas", "V_delta", "index.json")
ALL_ANCESTORS_PATH = os.path.join(ROOT, "schemas", "V_delta", "all_ancestors.json")


def superclass_names(superclasses):
    """Class-name strings from a superclasses list (handles {class_name} or str)."""
    names = []
    for sc in superclasses or []:
        if isinstance(sc, dict) and "class_name" in sc:
            names.append(sc["class_name"])
        elif isinstance(sc, str):
            names.append(sc)
    return names


with open(INDEX_PATH, encoding="utf-8") as _fh:
    _INDEX = json.load(_fh)
_ENTRIES = _INDEX["schemas"]
_IDS = [e["class_name"] for e in _ENTRIES]
_CLASS_NAMES = {e["class_name"] for e in _ENTRIES}


def _file_superclasses(entry):
    with open(os.path.join(ROOT, entry["path"]), encoding="utf-8") as fh:
        doc = json.load(fh)
    return superclass_names((doc.get("document_class") or {}).get("superclasses"))


@pytest.mark.parametrize("entry", _ENTRIES, ids=_IDS)
def test_index_superclasses_match_file(entry):
    file_sc = set(_file_superclasses(entry))
    index_sc = set(superclass_names(entry.get("superclasses")))
    assert index_sc == file_sc, (
        f"{entry['class_name']}: index.json superclasses {sorted(index_sc)} "
        f"!= document_class.superclasses {sorted(file_sc)} "
        f"(missing from index: {sorted(file_sc - index_sc)}; "
        f"extra in index: {sorted(index_sc - file_sc)})"
    )


@pytest.mark.parametrize("entry", _ENTRIES, ids=_IDS)
def test_index_superclasses_resolve(entry):
    for parent in superclass_names(entry.get("superclasses")):
        assert parent in _CLASS_NAMES, (
            f"{entry['class_name']}: superclass '{parent}' is not a class_name in index.json"
        )


def test_all_ancestors_matches_transitive_closure():
    """The published flattened ancestor map must equal the closure of the files."""
    if not os.path.exists(ALL_ANCESTORS_PATH):
        pytest.skip("all_ancestors.json not present")
    with open(ALL_ANCESTORS_PATH, encoding="utf-8") as fh:
        published = json.load(fh)

    direct = {e["class_name"]: _file_superclasses(e) for e in _ENTRIES}

    def closure(cls, seen):
        for parent in direct.get(cls, []):
            if parent not in seen:
                seen.add(parent)
                closure(parent, seen)
        return seen

    expected = {cn: sorted(closure(cn, set())) for cn in direct}
    assert published == expected
