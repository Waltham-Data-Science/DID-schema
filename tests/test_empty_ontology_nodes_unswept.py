"""check_empty_ontology_nodes: what the migrator-side text scan can and cannot see.

Lightsheet point 10 (Jess, 2026-10-14): migrators that build through did2.build
pass terms as plain text, so their empty nodes are invisible to the scan. The
report must count `did2.build.term('', ...)` and list every did2.build migrator
as NOT SWEPT, so its number is never read as the whole of it.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import check_empty_ontology_nodes as ceon


def _tree(tmp_path, files):
    root = tmp_path / "src" / "did" / "+did2" / "+convert" / "+migrators_j"
    root.mkdir(parents=True)
    for name, text in files.items():
        (root / name).write_text(text)
    return str(tmp_path)


def test_build_term_with_an_empty_node_is_counted(tmp_path):
    did = _tree(tmp_path, {"a.m": "t = did2.build.term('', 'z');\n"
                                  "u = jOntologyTerm('', 'x');\n"})
    files, rows = ceon.sweep(did)
    assert files == 1
    assert sorted(r["name"] for r in rows) == ["x", "z"]


def test_a_did2_build_migrator_is_listed_as_not_swept(tmp_path):
    did = _tree(tmp_path, {
        "built.m": "k = did2.build.key('z', 3);\n",
        "plain.m": "u = jOntologyTerm('', 'x');\n",
        "comment.m": "% did2.build.key('z', 3) only in a comment\n"})
    ceon.sweep(did)
    names = [os.path.basename(u) for u in ceon.sweep.unswept]
    assert names == ["built.m"]
