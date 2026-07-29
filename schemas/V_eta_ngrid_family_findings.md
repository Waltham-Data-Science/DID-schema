# V_eta — `ngrid` family findings (RF / Hartley + `ontology_image`)

**Status: FINDINGS ONLY. Nothing here is a decision.** This file records facts established
by reading the actual v1 writers, so that the design discussion for group F does not have to
re-derive them. Two fixes are queued off the back of it (`ontology_image.region`, then
`ngrid`); both are still to be designed with the team.

## Evidence base

Everything below is read from source, not inferred from our own schemas:

| repo | what it gave us |
|---|---|
| `VH-Lab/NDIcalc-vis-matlab` @ `65718ed` (added to session scope 2026-07-29, shallow clone) | the real Hartley writer + the v1 templates for `hartley_calc` / `reverse_correlation` / `hartley_reverse_correlation` |
| `VH-Lab/NDI-matlab` | the v1 `ngrid` template, `ontologyImage` template, `imageDocMaker`, `mat2ngrid` |
| `VH-Lab/DID-matlab` | the `ngrid` + `ontology_image` migrators and their unit fixtures |

> ⚠️ The NDIcalc-vis clone is **ephemeral** (remote container, reclaimed on idle). Re-add the
> repo if these need re-checking; that is why they are written down here.

---

## F1 — The RF family is ONE document class, not four

`+ndi/+calc/+vis/hartley.m:448` constructs a single document:

```matlab
doc{end+1} = ndi.document(ndi_calculator_obj.doc_document_types{1}, ...   % 'hartley_calc'
    'hartley_calc',                parameters, ...
    'hartley_reverse_correlation', hartley_reverse_correlation, ...
    'reverse_correlation',         reverse_correlation, ...
    'ngrid',                       ngridp) + ndi_calculator_obj.newdocument();
doc{end} = doc{end}.set_dependency_value('element_id', element_doc.id());
doc{end} = doc{end}.set_dependency_value('stimulus_presentation_id', stimulus_presentation_docs{i}.id());
```

- **`reverse_correlation` and `hartley_reverse_correlation` are superclass-only.** A repo-wide
  grep finds no other writer; the only other reference is a test *comparator* that reads the
  block. **No standalone documents of either class exist**, so retiring them strands nothing.
- **`calculator` is not a v1 class at all** — origin V_delta, an abstract parent invented to
  host `input_parameters` under a `placement: concrete_class` contract. `calcCommon.m`'s header
  states it "contributes nothing of its own to instance bodies".
- **Both dependencies are set explicitly on the one document**, so `element_id` is genuinely
  populated — single-doc subject resolution works, exactly as for `tuningcurve_calc`. No NDI
  second pass is needed to attribute the RF result to a subject.
- Corpus population: **≥210 `hartley_calc` docs in 20211116** (attested by
  `testMigrators.m:457`). Exact per-corpus counts were not obtainable — the Actions artifact
  blob host is blocked by the session proxy.

**Consequence:** group F is a single-document fold, materially smaller than the
"tuning-collapse-sized" estimate recorded earlier in `V_eta_tenet_audit.md`.

## F2 — The RF payload is TWO co-registered volumes, not one map

```matlab
ngridp.data_dim = [size(sta) 2];
fwrite(fid, cat(4, sta, p_val), 'double');
```

The `.ngrid` file is a 4-D `[T × X × Y × 2]` double array: plane 1 is the spike-triggered
average, plane 2 is a per-voxel p-value map. Any value model has to carry both, or say
explicitly which one it keeps.

## F3 — `ngrid.coordinates` carries real data and we delete it

The writer populates it (`hartley.m:443`):

```matlab
ngridp.coordinates = [ T_coords(:); X_coords(:); Y_coords(:) ];
```

and `DID-matlab/+did2/+convert/+migrators/ngrid.m` does `rmfield(block, 'coordinates')`
(also `data_size`), per a PLAN.md §9.6 conversion default ("no V_delta counterpart… dropped").

The convention is general, not Hartley-specific — `ndi.fun.data.mat2ngrid` documents
`coordinates` as *"Vertically concatenated coordinate positions, size [sum(data_dim), 1]"*.
It is one flat vector, split by `data_dim`, so it is **losslessly recoverable** — and currently
discarded.

- For **`hartley_calc`** the loss is *redundant*: the same values also sit per-axis and
  un-concatenated in `hartley_reverse_correlation.reconstruction_properties.{t,x,y}_coords`,
  which the migrator keeps.
- For **`ontologyImage`** it is **not** redundant — see F4. That is the real loss.

Note also that V_eta's `ngrid` carries `dim_labels`, an `element_id` dependency and an
`ngrid_file`, **none of which have any v1 counterpart**; they were invented downstream and are
never populated from v1 data. And `reverse_correlation.dimension_labels` is set to `''` by the
writer, so it is empty in every real document despite the template default `"Time, X, Y"`.

## F4 — `ngrid` has a SECOND consumer

`ngrid` is a superclass block on two classes:

| consumer | writer | disposition |
|---|---|---|
| `hartley_calc` | NDIcalc-vis `+ndi/+calc/+vis/hartley.m` | `retire` |
| `ontologyImage` | NDI `+ndi/+setup/+NDIMaker/imageDocMaker.m:125` | `retire` (→ `term_observation`) |

**Retiring `ngrid` is therefore gated on folding both**, not on the RF family alone. This is
the coupling that made `ngrid` look like a one-class item when it is not.

## F5 — `ontology_image.region` is a wrong-assumed-shape bug (same class as `distance_metadata`)

`+migrators_j/ontology_image.m` reads `preBody.ontology_image.region`. That field **does not
exist in any real v1 document.**

Evidence chain:

- The v1 NDI template declares `ontologyImage: { ontologyNode: "" }` (singular).
- The actual writer sets `struct('ontologyNodes', ontologyNodes)` (**plural**), and the class's
  own lookup query is `ndi.query('ontologyImage.ontologyNodes', 'exact_string', …)`. So the
  **template is stale and `ontologyNodes` is authoritative** — NDI disagrees with itself here.
- `ontologyNodes` is **a comma-joined, sorted string of one *or more* CURIEs**, each normalised
  through `ndi.ontology.lookup` (`imageDocMaker.m:80-85`).
- `universalRenames` snake-cases block and field names, so a real migrated body presents
  `ontology_image.ontology_nodes` — never `region`.
- `region` is a **DID-side invention**: it exists only in `V_eta/stable/ontology_image.json`.
  The migrator was written against our schema instead of the real v1 document.

**Effect:** every `ontologyImage` document migrates to a `term_observation` whose region term
is **empty**, silently — the code falls back to a blank term rather than quarantining, which is
why the corpus gate is green. The `.ngrid` block and the image file are not carried either, so
the picture is dropped as well.

**Why it survived:** `testMigratorsJ.m:1658` builds the fixture as
`v1.ontology_image = struct('region', struct('node', …, 'name', …))` — a shape no real document
has. Identical failure mode to `distance_metadata`, minus the quarantine that made that one
visible.

**Not yet confirmed against a real corpus document.** The reasoning is from writer + template +
rename rules; a corpus spot-check would settle it, and the plural/multi-term shape means the
fix is not a one-word rename (see below).

## F6 — Two of the RF document's blocks duplicate data that lives elsewhere

- `stimulus_properties` is copied out of the `stimulus_presentation` document
  (`hartley.m:379`, via `hartleystimdocstruct`). Under the stimulus model (#31) that content is
  already decided to live in referenced stimulus docs.
- `spiketimes` is copied from `element.readtimeseries(...)` (`hartley.m:391`). Under the
  ensemble model (#29) per-neuron spike times are primary archival data on the neuron-subject.

Both are therefore candidates for `derived_from` rather than carriage (T6/T10) — but resolving
either needs the migrated-id graph, i.e. an NDI second pass.

---

## Open — to be designed with the team, in this order

1. **`ontology_image.region` fix.** Not a rename: the real field is `ontology_nodes`, a
   comma-joined string of possibly several CURIEs, against a migrator that emits one term.
   Multi-term handling, the stale singular template, and the wrong unit fixture all have to be
   settled together.
2. **`ngrid`.** Gated on both consumers (F4). The live question is `coordinates` (F3) — where
   per-axis coordinates live in V_eta, given `sampled_body.axes[]` currently has `regularity`
   and `spacing` but **no explicit coordinate array**.
3. **The RF fold itself** (group F), now known to be a single-document job (F1) whose value is
   a two-plane volume (F2) with two duplicated input blocks (F6).
