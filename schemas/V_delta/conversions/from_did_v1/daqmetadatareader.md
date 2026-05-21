# Conversion: did_v1 → V_delta — `daqmetadatareader`

## Identity

- **V_delta `class_name`:** `daqmetadatareader`
- **V_delta tier:** `stable`
- **V_delta schema path:** `schemas/V_delta/stable/daqmetadatareader.json`
- **did_v1 source:** `NDI-matlab/src/ndi/ndi_common/database_documents/daq/daqmetadatareader.json`
- **Status:** `applied-in-tooling`

## Summary

`daqmetadatareader` carries the metadata-reader class identifier for a DAQ
system's per-epoch metadata source. did_v1 stored only the implementing
MATLAB class plus an optional tab-separated file hook; V_delta renames the
class field, preserves the TSV hook as an optional pass-through, and adds
a forward-looking `metadata_names` field that lists the fields the reader
produces.

## Field mapping

| did_v1 field | V_delta field | Transformation | Notes |
|---|---|---|---|
| `daqmetadatareader.ndi_daqmetadatareader_class` | `daqmetadatareader.reader_class` | rename | Value preserved verbatim (e.g., `'ndi.daq.metadatareader'`) |
| `daqmetadatareader.tab_separated_file_parameter` | `daqmetadatareader.tab_separated_file_parameter` | identity | Optional pass-through hook for TSV-per-epoch metadata sources. See "Why the TSV hook survives" below. |
| — | `daqmetadatareader.metadata_names` | new field | Optional. Comma-separated list of metadata field names this reader can extract. v1 docs migrate with the field absent; `mustBeNonEmpty: false` lets validation pass. |

## Transformations in detail

The `ndi_daqmetadatareader_class → reader_class` rename is identity at the
value level — the migrator copies the v1 value into the V_delta key and
strips the v1 key. Implemented in
`did-matlab/src/did/+did2/+convert/+migrators/daqmetadatareader.m`.

The `tab_separated_file_parameter` pass-through is identity in both
directions. Migrator preserves a populated value; an absent v1 field
yields an absent V_delta field (the V_delta schema declares
`mustBeNonEmpty: false`).

## Why the TSV hook survives

The clean V_delta design pattern for "this reader handles a specific
file format" is a subclass — e.g., `daqmetadatareader_tsv` would
inherit from `daqmetadatareader` and declare its own
file-identification field. v1, however, took a lazier path: any
`daqmetadatareader` instance could opt into TSV-per-epoch reading by
populating `tab_separated_file_parameter` on the base class. Real
corpora use this pattern.

Dropping the field at the V_delta boundary would force a per-document
synthesis of a `daqmetadatareader_tsv` subclass at migration time. That
synthesis logic does not exist today, and inventing it adds risk for
no immediate gain. Preserving the v1 hook as an optional V_delta field
is the smaller, safer change. Future cleanup (deprecate the hook in
favour of subclass instances) can happen once the migration is in the
rear-view mirror.

## Default values for new fields

`metadata_names` is optional (`mustBeNonEmpty: false`). Migrated v1
documents do not populate it; new V_delta-shaped documents may.

## Worked example

did_v1 body:

```json
{
  "document_class": { "class_name": "daqmetadatareader", ... },
  "daqmetadatareader": {
    "ndi_daqmetadatareader_class":  "ndi.daq.metadatareader",
    "tab_separated_file_parameter": "epoch_metadata.tsv"
  }
}
```

V_delta body after migration:

```json
{
  "document_class": { "class_name": "daqmetadatareader", "class_version": "1.0.0", ... },
  "daqmetadatareader": {
    "reader_class":                  "ndi.daq.metadatareader",
    "tab_separated_file_parameter": "epoch_metadata.tsv"
  }
}
```

(`metadata_names` is absent — optional, no v1 source.)
