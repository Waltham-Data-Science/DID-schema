"""Where the V2 schema files live: the one place the layout is written down.

Decided by Jess Haley, 2026-10-30 [schema folders by family]
(`did_v2_go_forward_class_audit.md`), amending [one folder, final classes only]
and item (6) of [markdown cleanup and rename]:

  schemas/did_v2/      class files only, in subfolders by family (a folder
                       means a family, never a tier or maturity): the core
                       classes at the top, and FAMILIES below, each
                       family's root class in its own folder ([family roots
                       and relation folder]); the retire
                       classes that remain live in `retiring/`. Class names
                       are unique across the tree.
  schemas/registry/    authored data: the term, binding, CURIE and carry
                       registers, reserved keys, the openMINDS crosswalk, the
                       meta-schema, the class dispositions and the authored
                       half of the migration targets.
  schemas/generated/   files only tools write: the index, the coverage
                       ledger, the decisions, the NDI ground truth,
                       term_registry_meta, class_disposition_meta,
                       quantity_list_meta and the derived half of the
                       migration targets.

A file that mixed authored and derived data was split so `generated/` is
purely tool-written: the index's hand-written `disposition` column is
`registry/did_v2_class_dispositions.json` (validate_v_eta copies it into
`generated/index.json`), and the migration targets' authored columns are
`registry/did_v2_migration_decisions.json` (`load_migration_targets` merges
the two halves for a reader).

The sibling readers (DID-matlab, NDI-matlab) find class files at any depth
under `schemas/did_v2/` and every other file by its UNIQUE basename anywhere
under `schemas/`, so a basename never repeats under `schemas/`
(`duplicate_basenames`, checked by validate_v_eta).

Every tool asks this module for a path; none carries its own copy of the
layout. `root` arguments name another repository root (a scratch mirror or a
test fixture).
"""

import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SET = "did_v2"
# [family roots and relation folder] (2026-10-31, amending [schema folders by
# family]): a family's root class lives in its family folder, as
# `time_reference/time_reference.json` does; `relation/` holds relation,
# directed_relation and undirected_relation. ROOTED_FAMILIES are the folders
# named after their root class; validate_v_eta checks that the root is there
# and that no class named after a family sits anywhere else.
ROOTED_FAMILIES = ("value", "calculation", "data_body", "time_reference", "relation")
FAMILIES = ROOTED_FAMILIES
RETIRING = "retiring"
FOLDERS = FAMILIES + (RETIRING,)
CORE = "core"   # the family name of a class at the top of schemas/did_v2/

# Authored registers and data (schemas/registry/), by basename.
REGISTRY_FILES = (
    "CURIE_lookups_meta.json",
    "binding_registry_meta.json",
    "did_schema_meta.json",
    "ndi_reserved_keys.json",
    "topics.json",
    "did_v2_term_registry.json",
    "did_v2_carry_register.json",
    "did_v2_openminds_crosswalk.json",
    "did_v2_class_dispositions.json",
    "did_v2_migration_decisions.json",
)
# Files only tools write (schemas/generated/), by basename.
GENERATED_FILES = (
    "index.json",
    "term_registry_meta.json",
    "class_disposition_meta.json",
    "quantity_list_meta.json",
    "did_v2_coverage_ledger.json",
    "did_v2_decisions.json",
    "did_v2_ndi_ground_truth.json",
    "did_v2_migration_targets.json",
    "did_v2_corpus_proof.json",
)
# The registries a class-set reader loads with the classes (the `*_meta.json`
# files and the reserved keys), wherever they live.
META_FILES = frozenset(n for n in REGISTRY_FILES + GENERATED_FILES
                       if n.endswith("_meta.json") or n == "ndi_reserved_keys.json")


def schemas_dir(root=None):
    return os.path.join(root or REPO, "schemas")


def classes_dir(root=None):
    """schemas/did_v2: class files only, at any depth."""
    return os.path.join(schemas_dir(root), SET)


def registry_dir(root=None):
    return os.path.join(schemas_dir(root), "registry")


def generated_dir(root=None):
    return os.path.join(schemas_dir(root), "generated")


def registry(name, root=None):
    """The path of an authored register, by basename."""
    return os.path.join(registry_dir(root), name)


def generated(name, root=None):
    """The path of a tool-written file, by basename."""
    return os.path.join(generated_dir(root), name)


def data_file(name, root=None):
    """registry/<name> or generated/<name>, by which list names it."""
    if name in REGISTRY_FILES:
        return registry(name, root)
    if name in GENERATED_FILES:
        return generated(name, root)
    raise KeyError(f"{name} is neither a registry nor a generated file")


# Named paths, for the readers that want one.
INDEX = generated("index.json")
TERM_REGISTRY = registry("did_v2_term_registry.json")
CARRY_REGISTER = registry("did_v2_carry_register.json")
OPENMINDS_CROSSWALK = registry("did_v2_openminds_crosswalk.json")
CLASS_DISPOSITIONS = registry("did_v2_class_dispositions.json")
MIGRATION_DECISIONS = registry("did_v2_migration_decisions.json")
MIGRATION_TARGETS = generated("did_v2_migration_targets.json")
COVERAGE_LEDGER_JSON = generated("did_v2_coverage_ledger.json")
DECISIONS_JSON = generated("did_v2_decisions.json")
NDI_GROUND_TRUTH = generated("did_v2_ndi_ground_truth.json")
CURIE_LOOKUPS = registry("CURIE_lookups_meta.json")
BINDING_REGISTRY = registry("binding_registry_meta.json")
DID_SCHEMA_META = registry("did_schema_meta.json")
NDI_RESERVED_KEYS = registry("ndi_reserved_keys.json")
TOPICS = registry("topics.json")
TERM_REGISTRY_META = generated("term_registry_meta.json")
CLASS_DISPOSITION_META = generated("class_disposition_meta.json")
QUANTITY_LIST_META = generated("quantity_list_meta.json")


def meta_path(name, root=None):
    """A `*_meta.json` registry (or ndi_reserved_keys.json) by basename."""
    if name not in META_FILES:
        raise KeyError(f"{name} is not a meta registry")
    return data_file(name, root)


def class_files(root=None, folders=None):
    """Every class file under schemas/did_v2/, sorted by repository path.

    `folders` limits the walk to those family folders (CORE for the top).
    Only `.json` files are classes; anything else is not read."""
    top = classes_dir(root)
    out = []
    for dirpath, dirnames, filenames in os.walk(top):
        dirnames[:] = sorted(d for d in dirnames if not d.startswith("."))
        fam = family_of_dir(dirpath, root)
        if folders is not None and fam not in folders:
            continue
        for f in sorted(filenames):
            if f.endswith(".json"):
                out.append(os.path.join(dirpath, f))
    return sorted(out, key=lambda p: rel(p, root))


def family_of_dir(dirpath, root=None):
    r = os.path.relpath(dirpath, classes_dir(root)).replace(os.sep, "/")
    return CORE if r == "." else r


def family(path, root=None):
    """The family folder a class file is in: CORE, a FAMILIES name, or RETIRING."""
    return family_of_dir(os.path.dirname(os.path.abspath(path)), root)


def class_index(root=None):
    """{class_name: path} from the file names (a class file is named after its class)."""
    return {os.path.basename(p)[:-5]: p for p in class_files(root)}


def class_path(name, root=None):
    """The file of class `name`, or None when no such class file exists."""
    return class_index(root).get(name)


def rel(path, root=None):
    """`path` relative to the repository root, with forward slashes."""
    return os.path.relpath(path, root or REPO).replace(os.sep, "/")


def duplicate_basenames(root=None):
    """{basename: [paths]} for every basename held by more than one file under
    schemas/. The siblings read a register by basename, so this must be empty."""
    seen = {}
    for dirpath, dirnames, filenames in os.walk(schemas_dir(root)):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for f in filenames:
            seen.setdefault(f, []).append(os.path.join(dirpath, f))
    return {k: sorted(v) for k, v in seen.items() if len(v) > 1 and k.endswith(".json")}


def load_migration_targets(root=None):
    """The migration target map as one document: the authored rows of
    registry/did_v2_migration_decisions.json with the generated `targets` and
    `target_completeness` of generated/did_v2_migration_targets.json merged in.
    The row set is the authored file's."""
    return load_migration_targets_from(registry("did_v2_migration_decisions.json", root),
                                       generated("did_v2_migration_targets.json", root))


def load_migration_targets_from(authored_path, generated_path):
    """load_migration_targets() for two named files. A missing generated half
    reads as no `targets` yet; an unreadable file raises (OSError,
    json.JSONDecodeError) so the caller can report it."""
    with open(authored_path) as fh:
        auth = json.load(fh)
    gen = {"classes": {}}
    if os.path.exists(generated_path):
        with open(generated_path) as fh:
            gen = json.load(fh)
    return merge_migration_targets(auth, gen)


def merge_migration_targets(auth, gen):
    """The two halves of the target map as one document {_comment, classes}."""
    classes = {}
    for cls, row in auth.get("classes", {}).items():
        merged = dict(row)
        g = gen.get("classes", {}).get(cls, {})
        for k in ("targets", "target_completeness"):
            if k in g:
                merged[k] = g[k]
        merged.setdefault("targets", [])
        classes[cls] = merged
    return {"_comment": auth.get("_comment"), "classes": classes}


def split_migration_targets(doc):
    """(generated_classes, authored_classes) for a merged target map."""
    gen, auth = {}, {}
    for cls, row in doc.get("classes", {}).items():
        gen[cls] = {k: row[k] for k in ("targets", "target_completeness") if k in row}
        auth[cls] = {k: v for k, v in row.items()
                     if k not in ("targets", "target_completeness")}
    return gen, auth


def folder_files(veta=None):
    """(family, path) for every .json under a class folder `veta` (default
    schemas/did_v2/), sorted; `veta` may be a copy of the folder anywhere."""
    veta = veta or classes_dir()
    out = []
    for dirpath, dirnames, filenames in os.walk(veta):
        dirnames[:] = sorted(d for d in dirnames if not d.startswith("."))
        r = os.path.relpath(dirpath, veta).replace(os.sep, "/")
        fam = CORE if r == "." else r
        for f in sorted(filenames):
            if f.endswith(".json"):
                out.append((fam, os.path.join(dirpath, f)))
    return out


def beside(veta, name):
    """registry/<name> or generated/<name> next to a class folder `veta`
    (schemas/did_v2 or a copy of the schemas/ tree anywhere)."""
    parent = os.path.dirname(os.path.abspath(veta))
    if name in REGISTRY_FILES:
        return os.path.join(parent, "registry", name)
    if name in GENERATED_FILES:
        return os.path.join(parent, "generated", name)
    raise KeyError(f"{name} is neither a registry nor a generated file")
