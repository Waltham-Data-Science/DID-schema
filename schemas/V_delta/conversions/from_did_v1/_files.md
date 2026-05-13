# File handling: did_v1 → V_delta

> This is the **generalized** file-handling specification for the
> did_v1 → V_delta migration. Per-document-type conversion docs should
> link here for anything that follows these generic rules, and only
> document type-specific behavior locally.

This file is a **skeleton**. Sections marked `TODO` need domain input
before the migration engine can be implemented.

## Scope

What counts as a "file" in this document? In DID terminology, any binary
blob, external path, or hash-addressed content that a document instance
references (rather than embeds inline). Examples to consider:

- TODO: enumerate the file-reference fields that appear across did_v1
  document types (e.g., raw recording files, processed outputs, image
  stacks, zarr archives).

## did_v1 file-reference shape

TODO: describe how did_v1 documents reference files today — field names,
path formats (absolute? relative? hash-addressed?), whether integrity is
verified, and what container/database layout assumptions exist.

## V_delta file-reference shape

TODO: describe the target file-reference shape under V_delta. Anchor
choices in `V_delta_SPEC.md` once finalized.

## Migration rules

For each migration scenario, specify the rule. Stubs follow.

### Path rewriting

TODO: when did_v1 paths are absolute and the V_delta layout requires
relative or hash-addressed paths, how are old paths translated? What
happens if the original file is no longer on disk?

### Integrity verification

TODO: does V_delta require a hash on file references? If so, how is it
computed during migration, and what happens on hash mismatch (fail,
warn, or annotate)?

### Orphan files

TODO: files that are on disk but no document references them, and
references that point at files no longer on disk. Specify the policy
for each.

### Large file handling

TODO: any size-based branching (e.g., inline vs. external) at the
V_delta layer.

### Container/database boundaries

TODO: when a document is migrated across databases (or out of one and
into a fresh V_delta container), how are file references rewritten?

## Open questions

- Are file references stored on the document instance itself, or on a
  side index?
- Should the migration engine ever copy file content, or only update
  references?
- What is the policy for files referenced by both a did_v1 document and
  a V_delta document during a transitional period?
