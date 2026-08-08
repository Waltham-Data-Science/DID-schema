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
  **^^ THAT LINE IS FALSE. CORRECTED 2026-08-06 — see F3b below.**

Note also that V_eta's `ngrid` carries `dim_labels`, an `element_id` dependency and an
`ngrid_file`, **none of which have any v1 counterpart**; they were invented downstream and are
never populated from v1 data. And `reverse_correlation.dimension_labels` is set to `''` by the
writer, so it is empty in every real document despite the template default `"Time, X, Y"`.

## F3b — CORRECTION (2026-08-06): `coordinates` is NOT a real loss, for EITHER consumer

**FINDINGS ONLY. NO DECISION IS RECORDED HERE.** The team asked for the coordinates
question to be dug into before confirming the ngrid/image disposition; this is what the
digging found.

### The `ontologyImage` "real loss" claim above is false

```
DENOMINATOR: 1,002 .m files on NDI origin/main
callers of ndi.fun.data.mat2ngrid:  ONE

imageDocMaker.m:121   ngrid_struct = ndi.fun.data.mat2ngrid(image);      <- ONE argument
mat2ngrid.m           if nargin == 1:  coordinates := (1:size(x,i))' for each dim
                      (the docstring calls this the 'MAT2NGRID:defaultCoords' path)
```

The only writer never supplies coordinate vectors, so **every `ontologyImage`
document's `coordinates` is the default index vector** `[1..d1; 1..d2; …]` — carrying
no information beyond `data_dim`, which is stored separately. Dropping it loses
nothing.

So both consumers are lossless:

```
hartley_calc     duplicated in hartley_reverse_correlation
                 .reconstruction_properties.{t,x,y}_coords   (recorded earlier; NDIcalc-vis
                 is not in scope now, so this half is not re-verified)
ontologyImage    default indices                              (measured 2026-08-06)
```

### But there IS a gap — the mirror image of what was recorded

`ngrid.coordinates` today is indices. The v1 format nevertheless ADMITS real positions —
`mat2ngrid(X, c1, …, cn)` is a documented signature — and **`sampled_body` has nowhere
to receive them**:

```
sampled_body.sample_time      regular   boolean
                              dt        duration    regular case
                              offsets   matrix      enumerated: THE EXPLICIT VALUES

sampled_body.axes[]           regularity  char      "regular | irregular"
                              spacing     double    regular case
                                                    <-- NOTHING for the irregular case
```

`axes` can DECLARE `regularity: irregular` and then has nowhere to put the coordinates.
`sample_time` got the enumerated case right; `axes` did not. So retiring `ngrid` is
lossless **by accident** (no writer supplies real coordinates) rather than **by design**.

The obvious repair is one field mirroring the slot that already works —
`axes[].coordinates`, a matrix, irregular only, length == `length`. **NOT decided, NOT
built.** It belongs to TaskList #45, which is about this exact field.

### THREE encodings of one distinction (found while checking the above)

The team asked whether `sample_time` is allowed to be irregular. **It is — in both
places.** But the two are not the same shape, and a third variant sits next to them:

```
subject_interaction.sample_time.kind        char      point | grid | enumerated
sampled_body.sample_time.regular            boolean   regular grid vs enumerated
sampled_body.axes[].regularity              char      regular | irregular
```

One distinction, three encodings. `kind` can express `point`, which `regular` cannot;
`regular` is a boolean where the other two are chars; `regularity` uses a different
word pair again. By this project's own definition that is DRIFT — the same fact stored
differently in different places — and it is the kind T14 exists to prevent.

Also asymmetric: the body `sample_time` has `t0` (a start offset from the anchor) and
the inline one does not.

**No disposition is proposed for any of this.** It is recorded so the ngrid/image
signature is taken with the facts visible, and because #45 is the decision that owns
the field.

## F4 — `ngrid` has a SECOND consumer

`ngrid` is a superclass block on two classes:

| consumer | writer | disposition |
|---|---|---|
| `hartley_calc` | NDIcalc-vis `+ndi/+calc/+vis/hartley.m` | `retire` |
| `ontologyImage` | NDI `+ndi/+setup/+NDIMaker/imageDocMaker.m:125` | `retire` (→ `term_observation`) |

**Retiring `ngrid` is therefore gated on folding both**, not on the RF family alone. This is
the coupling that made `ngrid` look like a one-class item when it is not.

## F5 — `ontology_image` had TWO v1 vintages and the migrator matched NEITHER — **FIXED**

### The two vintages

NDI **redefined** `ontologyImage` upstream, so two incompatible shapes are both "did_v1":

| | **A — legacy** (DID-schema `V_alpha`/`V_beta` ancestry) | **B — current NDI production** |
|---|---|---|
| fields | `ontology_name`, `ontology_region` | `ontologyNode` (template) / `ontologyNodes` (writer) |
| depends_on | `element_id` | `ontologyTableRow_id` |
| file | `ontology_image_file` | `ontologyImage.ngrid` |
| superclasses | `base` | `base, ngrid` |

For vintage B the **template is stale and the plural is authoritative**: the writer sets
`struct('ontologyNodes', …)` and the class's own lookup is
`ndi.query('ontologyImage.ontologyNodes', 'exact_string', …)`. The value is a **comma-joined,
sorted string of one _or more_ CURIEs**, each normalised through `ndi.ontology.lookup`
(`imageDocMaker.m:80-85`).

### The bug

`+migrators_j/ontology_image.m` read `preBody.ontology_image.region`. `region` is **not a v1
field at all** — it is the *output* of the V_delta migrator
(`+did2/+convert/+migrators/ontology_image.m`), which composes it from vintage A's two chars.
But `v1_to_v2.m` routes a class to `migrators_j` **instead of** the V_delta migrator (the
`splitPackage` branch), so a J migrator receives a body that has been through
`universalRenames` **only**. The read therefore matched neither vintage — only the unit fixture,
which had been built to the V_delta output shape (`testMigratorsJ.m:1658`).

**Effect — a silent husk.** Every `ontologyImage` document became a `term_observation` with an
empty term and (vintage B) an empty `subject_id`, plus the raster and the provenance edge
dropped. Neither gate could see it:

- `isEmptyValue` (`cache.m:947`) calls a struct empty only if it has **no fieldnames**, so
  `{node:'',name:''}` satisfies `mustBeNonEmpty: true`.
- `depends_on` non-emptiness is **never validated anywhere**; `+did2/+validate/references.m`
  explicitly **skips empty edges**. So `subject_statement.subject_id`, declared
  `mustBeNonEmpty: true`, is unenforced.

Same failure mode as `distance_metadata` — a migrator written against an assumed shape, with a
fixture built to match the assumption — minus the quarantine that made that one visible.

### The fix (built)

**Vintage A → migrated here.** Everything needed is on the document: term from the two
coordinated chars (the `ontology_label` idiom), subject from `element_id`. 1 → 2.

**Vintage B → deferred to the NDI second pass, passed through UNCHANGED.** The terms are
resolvable, but the **subject is not**: the only edge is `ontologyTableRow_id`, and a table row
is not a subject (`subject_statement.subject_id` declares
`must_refer_to_document_class: subject`). The subject is reachable only *through* the table row,
which needs the migrated-id graph. Emitting an observation with an empty subject is precisely
the husk this fix exists to stop, so we emit nothing and leave the document intact — the same
strategy `stimulus_presentation` uses.

**The guard.** Any block matching neither vintage **errors**, so it quarantines visibly instead
of migrating to a husk. A body presenting `region` is rejected **by name**, since that shape can
only come from V_delta output or from a fixture built against our own schema.

**Schema consequence.** A passthrough must validate, so the `ontology_image` tombstone now
declares vintage B faithfully — `ngrid` back as a superclass, `ontology_nodes`,
`ontology_table_row_id` — alongside vintage A's two chars. This is a second reason retiring
`ngrid` is gated on both consumers (F4).

**The `ontologyTableRow_id` edge — DECIDED: preserve the row's id.** Passing the document
through keeps its edge to the `ontologyTableRow`, and the second pass has to follow that edge to
reach the subject. But `ontology_table_row` dissolves 1→N and gave **every** emitted body a fresh
id, so nothing carried the row's id afterwards and the edge pointed at something that no longer
existed. There is **no old-id → new-id map anywhere in the converter**, so id preservation is the
only mechanism that can make such an edge resolve — the same lesson the calculator fold paid
11,448 orphans for (T10). `ontology_table_row` now keeps the source id on **exactly one** emitted
body: the first, with siblings keeping fresh ids (the primary/sibling convention
`jStartInteraction` already uses). Every body it emits carries `subject_id`, so a follower lands
on one document and reads the subject straight off it. `makePatchSubject` already preserved the
id deliberately, so the step detects an existing preservation and leaves it alone rather than
minting two documents with one id. **Needs a full corpus run** — it changes ids corpus-wide, which
a fast gate cannot confirm.

**Still deferred:** the raster (the `ngrid` block + `.ngrid` file). Under R6 the natural target is
an `image_observation` beside the term observations — that belongs to the `ngrid` work.

**Not confirmed against a real corpus document.** The reasoning is from writer + template +
rename rules + routing. The guard is what will settle it: if any corpus holds a
neither-vintage document, the next run will quarantine it loudly instead of hiding it.

### Not affected

`ontology_label` reads `ontology_node` (its idiom 2), which **matches** the real
`ontologyLabel: {ontologyNode: ""}` template. It is correct as written.

### Left open — a systemic gap

`mustBeNonEmpty` on `depends_on` is declared across the schema and **enforced nowhere**. This
migrator is one instance; others could be hiding the same way. Sibling to task #32 (binding
declared but not validated).

## F6 — Two of the RF document's blocks duplicate data that lives elsewhere

- `stimulus_properties` is copied out of the `stimulus_presentation` document
  (`hartley.m:379`, via `hartleystimdocstruct`). Under the stimulus model (#31) that content is
  already decided to live in referenced stimulus docs.
- `spiketimes` is copied from `element.readtimeseries(...)` (`hartley.m:391`). Under the
  ensemble model (#29) per-neuron spike times are primary archival data on the neuron-subject.

Both are therefore candidates for `derived_from` rather than carriage (T6/T10) — but resolving
either needs the migrated-id graph, i.e. an NDI second pass.

---

## Open — DECIDE FIRST, THEN BUILD

> Standing process rule: every item below is **decided with the team before any code is
> written**. F5 was built because it was explicitly authorised; nothing else here is.

1. ~~**`ontology_image` fix.**~~ ✅ **DONE** — see F5.
2. **`ngrid`.** Gated on both consumers (F4). The live question is `coordinates` (F3) — where
   per-axis coordinates live in V_eta, given `sampled_body.axes[]` currently has `regularity`
   and `spacing` but **no explicit coordinate array**. Note vintage B's raster (`ngrid` block +
   `.ngrid` file) is now parked on the passthrough and needs a home here too.
3. **The RF fold itself** (group F), now known to be a single-document job (F1) whose value is
   a two-plane volume (F2) with two duplicated input blocks (F6).
4. **The unenforced-dependency gap** (F5, "Left open"): `mustBeNonEmpty` on `depends_on` is
   declared everywhere and validated nowhere. Scope unknown — this migrator is one instance.
