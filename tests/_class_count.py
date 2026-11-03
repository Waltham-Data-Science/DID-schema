"""The number of class files a whole-tree sweep must read: its DENOMINATOR.

Derived, not pinned. Until 2026-11-03 some twenty sweeps asserted `> 100`
class files, a floor that only stood in for "the tree was found and read". It
tracked the class count, so it went red when [handed-on are v1 as written]
(Jess Haley, 2026-11-03, did_v2_go_forward_class_audit.md) deleted five retire
classes and the tree went from 103 to 98 class files, although nothing was
lost.

The count comes from the hand-written registry
schemas/registry/did_v2_class_dispositions.json, not from the tree the sweeps
read: tools/validate_v_eta.py requires exactly one row per class file (a class
file with no row and a row with no class file both fail), so the registry and
the tree agree whenever the chain is green, and a sweep that reads fewer
classes than the registry lists has lost part of the tree. A deleted class
leaves the registry in the same change, so this moves with it.
"""
import json
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLASS_DISPOSITIONS = os.path.join(REPO_ROOT, "schemas", "registry",
                                  "did_v2_class_dispositions.json")


def registered_class_count():
    """Rows in the class-disposition registry: one per class file."""
    with open(CLASS_DISPOSITIONS) as fh:
        n = len(json.load(fh)["classes"])
    # an empty or unread registry must not make every sweep's floor zero
    assert n > 0, f"{CLASS_DISPOSITIONS} lists no class"
    return n


CLASS_COUNT = registered_class_count()
