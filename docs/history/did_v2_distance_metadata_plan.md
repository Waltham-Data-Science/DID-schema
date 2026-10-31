# V_eta — distance_metadata decomposition plan (TaskList #18)

Status: **reshape landed; Part B deferred.** The safe, orphan-free step is DONE —
`migrators_j.distance_metadata` now reshapes the FLAT v1 A/B endpoint fields into
the nested `endpoints` array the V_eta schema requires, so the retained
distance_metadata passthrough VALIDATES (clears the ~2078 JH quarantines). It emits
NO length_observation and mints NO endpoint relation (both need the second-pass
migrated-id graph; see below). Covered by `testMigratorsJ`
(testDistanceMetadataReshapesFlatEndpoints, transform) + `testFixtureCorpus`
(fx_distance_metadata, real flat shape, under schema validation). Part A stays
superseded; Part B (the body-backed length_observation with values) stays deferred
with the element-data -> observation tier (#9).

Grounded in the writer (NDI-matlab `+setup/+conv/+haley/doImport.m`), the v1 template
(`ndi_common/database_documents/element/distance_metadata.json`), the pass-1
`element` migrator, and the second-pass `bodyResolver`.

## What the v1 data is
A `distance_metadata` doc is FLAT and records the two ENDPOINTS of a distance
measurement, not the distance itself:
- `ontologyNode_A` = the **animal subject** document id; `ontologyStringValues_A` /
  `integerIDs_A` its labels.
- `ontologyNode_B` = a **patch** (`ontology_table_row`) document id; its labels.
- `ontologyNumericValues_A/_B` = `[]` — **empty by design**.
- `units` = e.g. `NCIT:C48367` (pixels).
- `depends_on element_id` -> the **distance timeseries element** (the actual
  distances over time live HERE, in the element's epoch data).

## Where the pieces already go in V_eta (pass-1)
- The distance **element** -> a `subject` (a derived "distance signal"),
  `derived_from` the animal (via `element.m`). Its id is preserved.
- The distance element's **timeseries values** -> element-epoch data; NOT yet an
  observation (this is the element-data -> observation decomposition, still open;
  overlaps the deferred D-C/data-body tier).
- The `distance_metadata` doc itself -> currently QUARANTINES (the migrator assumes
  a nested `endpoints.numeric_values` that does not exist -> no-vals passthrough ->
  the flat doc fails the required non-empty `endpoints`). ~2078 in JH. Non-gating
  (JH's test does not gate quarantine), so corpus is green regardless.

## The decomposition, split by difficulty
### UPDATE — Part A (endpoint relation) was TRIED and REVERTED (corpus 946faf95)
Emitting the `measured_distance_to` relation produced **4156 JH orphans = 2078 × 2**:
BOTH endpoints (`ontologyNode_A` animal AND `ontologyNode_B` patch) DANGLE in the JH
migrated set. The id-preservation assumption is FALSE for JH — the endpoint doc ids
stored in `ontologyNode_A/_B` are NOT the ids the referenced docs migrate to (the JH
animal is likely an `openminds_subject` whose migrator mints a NEW subject id; the
stored subjectDocID/patchDocID are pre-migration ids). Worse, this turned a
NON-gating quarantine into a GATING orphan failure (JH orphans gate; JH quarantine
does not). CONCLUSION: the endpoints can only be resolved by the SECOND PASS, which
sees the migrated-id graph — a single-doc DID migrator cannot mint a resolvable
endpoint relation. distance_metadata is left as PASSTHROUGH (quarantine, non-gating,
green) until Part B. The `measured_distance_to` term stays in the registry for Part
B's use.

**Part A (superseded) — the endpoint relation (does NOT work single-doc; see UPDATE).**
Mint a `directed_relation` between the two endpoint doc ids:
`ontologyNode_A` (animal) --`measured_distance_to`--> `ontologyNode_B` (patch).
This captures the real semantics and clears the quarantine. It needs NO graph, so
it is a PASS-1 (`migrators_j.distance_metadata`) rewrite (read the flat A/B fields;
emit the relation instead of the doomed length_observation).
  - **ORPHAN RISK — RESOLVED (code-confirmed; corpus-confirm on the next run):**
    `ontology_table_row.makePatchSubject` mints the patch as a bare V_eta `subject`
    that PRESERVES the source patch doc id (line ~267, "id preserved so the encounter
    parent resolves"). The animal endpoint (`ontologyNode_A`) is likewise an
    id-preserved `subject`. So BOTH endpoint ids survive migration -> the endpoint
    relation resolves, no orphan. (The per-column observations get fresh ids, but the
    patch SUBJECT keeps the doc id.) Still: watch the next corpus discovery report to
    confirm 0 new orphans from these relations.
  - A `measured_distance_to` (or `spatially_related_to`) relation term must be added
    to `relation_bindings` (child: subject; parent: subject|ontology_table_row/its
    successor).

**Part B — the length_observation with values (large, genuinely second-pass).**
Turn the distance signal (the element-subject's timeseries) into a body-backed
`length_observation` (units from `distance_metadata.units`), with the patch as the
spatial reference. Requires:
  - the element-data -> observation decomposition (turning an element's epoch
    timeseries into a `sampled_body` + `length_observation`) — NOT built; this is
    the broader element-data tier, overlapping deferred #9.
  - `bodyResolver.subjectOfElement(element_id)` to attach the observation to the
    animal (already available).
This is a new second-pass sub-pass (sibling of `pathSPromotion` /
`stimulusBathToBath`) that consumes `distance_metadata` for the endpoints + the
element-subject for the values.

## Recommended sequence
1. CONFIRM the patch-endpoint id behavior (does `ontology_table_row` preserve the
   patch doc id?) against a corpus discovery run. This gates Part A.
2. If safe, implement **Part A** (pass-1 endpoint relation + relation term). Small,
   testable, clears the 2078 quarantines. Corpus-validate.
3. **Part B** rides with the element-data -> observation decomposition (the deferred
   data-body/analysis tier). Defer until that machinery exists; do not fabricate a
   values-less length_observation.

## Do NOT
- Do NOT read `endpoints.numeric_values` (does not exist; the first fix did this and
  was reverted).
- Do NOT emit a `length_observation` from the metadata doc alone (no scalar there).
- Do NOT mint the endpoint relation until the patch-endpoint id is confirmed to
  survive migration (orphan risk).
