# Ground-truth repair plan — migrate FROM the current NDI templates, TO V_eta

**Status: Phase 0 DONE. Phases 1-4 are NOT authorised to build — decide first.**

## The problem in one paragraph

A migrator that reads a field the source document does not have produces an **empty but
perfectly valid** document. An all-blank composite still has fieldnames, so it satisfies
`mustBeNonEmpty`; an empty `depends_on` edge is skipped by `did2.validate.references`. So the
corpus gate reports 0 quarantine and 0 orphans while the data quietly goes missing. Three
confirmed instances (`distance_metadata`, `ontology_image`, `ontology_label`) plus a sweep that
flags ~23 more all share one root cause: **the migrators were written against DID-schema's own
`V_alpha` snapshot rather than the real NDI templates.**

The bad provenance is written down, which is how it spread:

```
schemas/V_alpha/<class>.json            <- our snapshot, NOT authoritative
  └─ V_delta/conversions/from_did_v1/*.md   "schema-shape ancestor in this repository is V_alpha/..."
       ├─ +did2/+convert/+migrators_j/*.m    written from the conversion doc
       ├─ tests fixtures                     built to match the migrator's assumption
       └─ NDI-matlab ndi.compat.fieldAliases "source of truth ... is the per-class conversion markdown"
```

Each layer cited the layer above instead of the NDI template, and the fixtures were built to
match the assumption — so the tests confirmed the assumption rather than testing it.

## The rule this plan establishes

> **The current NDI-matlab document templates (read from `origin/main`) are the single source
> of truth for the did_v1 side of every migration. `V_alpha`/`V_beta` are history, not
> evidence. Where a template and its WRITER disagree, the writer wins — the data follows the
> writer — and the disagreement is reported upstream.**
>
> **Every test fixture is built from the writer or the template, never from a DID-side schema.**

Adopting this means we never have to adjudicate "was `V_alpha` a bad copy, or did NDI drift?"
— `V_alpha` simply stops being evidence.

One consequence that *does* need adjudicating per class: **where NDI genuinely changed a
template**, documents in the old shape may exist in the corpora, so that migrator needs two
paths. **Where we invented the shape**, only one shape ever existed and the migrator needs one.
`ontologyImage` was the invented kind. NDI's git history answers this per class, cheaply.

---

## Phase 0 — establish ground truth  *(DONE — `tools/ndi_ground_truth.py` → `V_eta_ndi_ground_truth.json`)*

Produce a machine-readable reference every later phase checks against.

- **0.1** Extract the NDI templates from `origin/main`: class → fields → dependencies → files.
  Emitted as `V_eta_ndi_ground_truth.json` by `tools/ndi_ground_truth.py`.
- **0.2** Record **writer divergences** — where the shipped writer emits something the template
  does not declare. Known already:
  - `ontologyImage`: template `ontologyNode`, writer `ontologyNodes` (a comma-joined list of
    one *or more* CURIEs). Writer wins.
  - `hartley_reverse_correlation`: template `hartley_numbers: []`, writer a struct
    `{S, KXV, KYV, ORDER}`. Writer wins.
- **0.3** Per divergent class, classify from NDI git history: **NDI-CHANGED** (real drift, old
  documents may exist → migrator needs two paths) vs **DID-INVENTED** (our fabrication → one
  path). `ontologyImage` = DID-INVENTED (NDI created it 2025-07-03 with `ontologyNode`; our
  `V_alpha` entry was authored 2026-02 with a different shape).
- **0.4** Class inventory: present in NDI only / V_1 only / both. Tests the expectation that
  overlapping classes are identical, and fixes the scope.

**Phase 0 changes no migrator and no schema.** It only produces evidence.

### Phase 0 results

| measure | value |
|---|---|
| NDI classes captured (from `origin/main`) | **91** — matches `coverage.py`, so the two tools agree |
| V_alpha classes with a matching NDI template | 80 |
| of those, **disagreeing** with the template | **67** |
| provenance: **DID-INVENTED** (never matched NDI, even at NDI's first version) | **36** |
| provenance: **NDI-CHANGED** (matched, then NDI drifted) | **0** |
| provenance: UNKNOWN (earliest template predates the modern block format) | 31 |
| J migrators using vocabulary no template has | **22** (9 read via an explicit idiom, 13 mentioned only) |

**The expectation that overlapping classes are identical does not hold, and not because NDI
drifted.** Of the 36 divergences whose history is determinable, *every one* failed to match NDI
even at NDI's own first version — and there are **zero** confirmed cases of NDI changing a
template out from under us. `V_alpha` was largely never a copy of NDI.

Consequence for Phase 2: the "NDI changed it, so old-shaped documents exist, so the migrator
needs two paths" case is so far **hypothetical**. Default to ONE path — the current template
plus its writer — and only add a second path where a specific class proves it needs one.
(`ontology_image` currently has two; on this evidence its legacy path is dead code and should
be removed, which is a Phase 2 item.)

The 31 UNKNOWNs are undetermined, not clean: usually the earliest template predates the modern
property-block format, so the comparison is not meaningful that far back. They need reading by
hand.

## Phase 1 — make silence impossible  *(REPORT-ONLY LANDED)*

The ordering argument: while a broken migrator emits a valid empty document, **we cannot tell a
fixed migrator from a broken one**, and each check costs a ~2.5-hour corpus run. Visibility
first, or Phase 2 is done blind.

- **1.1** Enforce `mustBeNonEmpty` on `depends_on`. Currently declared across the schema and
  enforced **nowhere** — `validate/references.m` explicitly skips empty edges, and
  `schema/cache.m` never checks dependency non-emptiness at all.
- **1.2** Make an all-blank composite count as empty. `cache.m:947` `isEmptyValue` calls a
  struct empty only when it has **no fieldnames**, so `{node:'',name:''}` passes a required
  check.
- **1.3** CI sweep: every migrator's field reads vs the Phase-0 reference; fail on a name no
  template or writer has. (The exploratory script that found the 23 suspects is most of this.)

**Landed report-only:**
- `did2.validate.silentLoss` (DID-matlab) counts both holes per migration run and is wired into
  the v1_to_v2 summary, the corpus discovery printout, and the uploaded per-corpus JSON report.
  It raises nothing and changes no outcome; an audit failure is caught and recorded rather than
  propagated, so it cannot break a migration.
- `tools/check_migrator_vocabulary.py` (DID-schema) reports migrators speaking invented
  vocabulary, exit 0. `--enforce` exits non-zero and is the Phase 2 end state. It carries a
  `KNOWN_BROKEN` set so that a name appearing *outside* it reads as a **regression** — currently
  6 of the 9 confirmed offenders are outside it and want individual confirmation.

> **Land 1.1–1.3 REPORT-ONLY first.** Flipping straight to enforcing will light up a large
> number of quarantines and block the 0-quarantine gate before anything is fixed. Report-only
> gives the **census** — how many real documents each broken migrator touches — which is also
> what ranks Phase 2. Flip to enforcing when the count reaches zero.

## Phase 2 — fix the migrators, ranked by the Phase-1 census

Read only invented names (certainly emitting nothing), highest document count first, then the
mixed ones. Confirmed so far: **`probe_geometry`** reads `channel_positions`, `position_units`,
`probe_type` — the real template has *none* of those (`site_locations_*`, `unit`, `probe_model`,
`manufacturer`, `contact_shape*`, `contour_*`).

Per class, the same shape of fix: read template **and** writer → fix migrator → **rebuild the
fixture from the writer** → the 1.3 sweep guards it thereafter.

Already done early, as Phase-2 items: `ontology_image` (vintage split + guard) and
`ontology_table_row` id preservation. **The id-preservation change is still unverified beyond
the fast gate** — it changes ids corpus-wide and needs a full corpus run.

## Phase 3 — data loss that is not a name error

- `ngrid.coordinates` is populated by the writers and **deleted** by the migrator
  (`+migrators/ngrid.m` `rmfield`). Needs the `sampled_body.axes[]` decision — that block has
  `regularity`/`spacing` but no explicit coordinate array.
- `ngrid` retirement, gated on **both** consumers (`hartley_calc` and `ontologyImage`).
- The raster parked on the `ontology_image` passthrough needs a home (R6 `image_observation`).

## Phase 4 — remaining modelling

The RF/Hartley fold (group F) and the rest of the V_eta roadmap. Last on purpose: modelling on
top of migrators that do not read real data is building on sand, and the RF fold depends on
`hartley_reverse_correlation`, one of the known template-vs-writer disagreements.

---

## Standing rules this plan adds

1. **NDI `origin/main` templates are the did_v1 source of truth.** Not `V_alpha`, not the
   conversion markdown, not our V_eta schemas.
2. **Fixtures are built from the writer or the template.** Never from a DID-side schema. Every
   bug in this family survived because its fixture encoded the assumption.
3. **A migrator that cannot find what it needs errors.** It does not emit a blank document.
   Quarantine is visible; a husk is not.
