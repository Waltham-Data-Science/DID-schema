"""Where a document named by bare name lives: the unique `docs/**/<name>`.

Decided by Jess Haley, 2026-10-26 [markdown cleanup and rename]
(`did_v2_go_forward_class_audit.md`), part (5): "a document cited by bare name
resolves to the unique file of that name under `docs/`, and a duplicate name
fails the gate." So moving a document between `docs/` subfolders never breaks
a citation, and a citation never has to say which subfolder it means.

Layout (part (3)): `docs/` (entry points), `docs/plans/` (flat),
`docs/generated/` (written by tools; they quote decisions, they hold none),
`docs/history/`, `docs/references/` (reference papers with a citation note
each), and the working notes already under `docs/`.

A name with a `/` in it is a path from the repository root and is returned as
such. Every reader of a document by name asks this module; none carries its
own copy of the layout.
"""

import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(REPO, "docs")
GENERATED = os.path.join(DOCS, "generated")
PLANS = os.path.join(DOCS, "plans")
HISTORY = os.path.join(DOCS, "history")
# Working notes: "a proposal or a measurement at the commits it names. It is
# not the record" (docs/v2_working/README.md).
WORKING = os.path.join(DOCS, "v2_working")
# Reference papers V2 follows, each a PDF with a citation and licence note
# beside it (`<author>_<year>_<topic>.md`).
REFERENCES = os.path.join(DOCS, "references")


class DuplicateDocumentName(ValueError):
    """Two documents under docs/ share a file name, so a bare name is ambiguous."""


def all_markdown(root=None):
    """Every `.md` under `root` (default `docs/`), sorted, as absolute paths."""
    root = root or DOCS
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for name in filenames:
            if name.endswith(".md"):
                out.append(os.path.join(dirpath, name))
    return sorted(out)


def name_index(root=None):
    """{basename: [paths]} for every `.md` under `root` (default `docs/`)."""
    idx = {}
    for path in all_markdown(root):
        idx.setdefault(os.path.basename(path), []).append(path)
    return idx


def duplicates(root=None):
    """{basename: [paths]} for every name held by more than one document."""
    return {k: v for k, v in name_index(root).items() if len(v) > 1}


def is_generated(path):
    """True for a document under `docs/generated/`."""
    return os.path.abspath(path).startswith(os.path.join(os.path.abspath(GENERATED), ""))


def record_documents(root=None):
    """The hand-written documents: every `.md` under `docs/` except `generated/`."""
    root = root or DOCS
    gen = os.path.join(os.path.abspath(os.path.join(root, "generated")), "")
    return [p for p in all_markdown(root)
            if not os.path.join(os.path.dirname(os.path.abspath(p)), "").startswith(gen)]


# The working plan: "This is the working plan, not the record" (its own
# header). Its figures are dated measurements, like the notes in v2_working/.
WORKING_PLAN = "V2_PLAN.md"


def current_documents(root=None):
    """The documents whose numbers are meant to be current: every `.md` under
    `docs/` except `v2_working/`, whose notes are dated measurements, and the
    working plan `docs/V2_PLAN.md` (not the record, by its own header)."""
    root = root or DOCS
    work = os.path.join(os.path.abspath(os.path.join(root, "v2_working")), "")
    plan = os.path.abspath(os.path.join(root, WORKING_PLAN))
    return [p for p in all_markdown(root)
            if not os.path.abspath(p).startswith(work) and os.path.abspath(p) != plan]


def resolve(document, root=None, strict=False):
    """The path a cited document names, or None when no such document exists.

    A bare name resolves to the unique `docs/**/<name>`. A name held by two
    documents raises DuplicateDocumentName when `strict`, and otherwise
    resolves to None (the caller reports it as not found; the duplicate itself
    is failed by `check_citations`). A name with a `/` is a path from the
    repository root.
    """
    if not document:
        return None
    if "/" in document or os.sep in document:
        return os.path.join(REPO, document)
    hits = name_index(root).get(document, [])
    if len(hits) == 1:
        return hits[0]
    if len(hits) > 1 and strict:
        raise DuplicateDocumentName(f"{document}: {', '.join(sorted(hits))}")
    return None


def path_for(document, root=None):
    """Like resolve(), but a name that resolves to nothing still gets a path
    (under `docs/plans/`), so a caller's 'does not exist' message names one."""
    return resolve(document, root) or os.path.join(root or PLANS, document)


def rel(path):
    """`path` relative to the repository root, with forward slashes."""
    return os.path.relpath(path, REPO).replace(os.sep, "/")


if __name__ == "__main__":
    import sys
    idx = name_index()
    dup = duplicates()
    print(f"DENOMINATOR: {sum(len(v) for v in idx.values())} document(s) under docs/, "
          f"{len(idx)} distinct name(s)")
    print(f"DUPLICATE NAMES: {len(dup)}")
    for name, paths in sorted(dup.items()):
        print(f"  {name}: " + ", ".join(rel(p) for p in paths))
    sys.exit(1 if dup else 0)
