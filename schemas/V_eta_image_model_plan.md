# V_eta — the `image` model (DECIDED; build deferred)

*Worked design for how V_eta represents images/rasters, decided in the audit walkthrough
(R6). **All decisions below are FINAL; the BUILD is deferred** — batched with other
walkthrough decisions. When building, this doc is the spec. Cross-refs: `V_eta_tenets.md`
(T3/T6/T11/T12/T13), `V_eta_tenet_audit.md` (R6).*

## The one-line model

> **`image` is a `data_type` (a raster value). The DIRECTION says measured-vs-shown; the
> `storage_mode` says inline-vs-body-vs-reference; the DESCRIPTORS are always explicit on
> the composite; only the PIXELS move by `storage_mode`.**

One type × {2 directions} × {3 storage modes} covers every case raised (micrograph, visual
stimulus, multi-subject FOV, tiny inline filter/thumbnail).

## Decisions (final)

1. **`image` IS its own `data_type` composite** (T12). A raster is genuinely new value
   *structure* (not a scalar, not a term). Item-2's reparent (`image` `base` → abstract
   `data_type`) was correct; the earlier "remove the composite" (option B) was WRONG —
   it only looked at the measurement role and missed the stimulus role.

2. **Two directions** (T3):
   - `image_observation` = `subject_observation` + `image` — a micrograph *measured of* the
     subject (image_stack).
   - `image_manipulation` = `subject_manipulation` + `image` — an image/video *shown to* the
     subject as a visual stimulus (sibling of `visual_grating_manipulation`; `visual_grating`
     is a *parametric* stimulus, `image` is a *raster* stimulus). **NEW class to add.**

3. **`storage_mode` governs only the PIXELS** (T6), defaulting toward the simple end:
   - `inline` — small (a 3×3 filter, a thumbnail): pixels in `image.value` (a matrix).
   - `body` — large (micrograph/video): pixels in a data_body; **`opaque_body` is the
     default** (raw bytes — the composite already says how to read them, so *no
     duplication*); **`sampled_body`** is the escalation for *huge* volumes needing
     chunked/partial reads (OME-Zarr–style), and is the one place a controlled re-statement
     of `dtype`/`axes` on the body is justified (the array must be self-readable for chunk
     access).
   - `reference` — **occasional, opt-in**: one shared image referenced by several
     observations (a multi-subject FOV, each subject its own `image_observation` referencing
     the same image via `storage_mode: reference` + its own ROI). NOT the default; imposes
     no 1:1-body-ownership change on anyone else. "In most cases an image does not need to be
     referenceable."

4. **Descriptors are ALWAYS explicit on the `image` composite** — never inferred from the
   pixels. **This is the load-bearing decision.** Rationale: *you cannot recover `dtype`
   from an inline matrix* — the doc is JSON and the field type is a generic `matrix`, so
   `uint16` `10` and `double` `10.0` serialize identically (signedness/bit-depth/float-vs-int
   erased; shape IS recoverable, dtype is NOT). Calibration/color/modality are never in the
   pixels at all. So they must be stored, and storing them on the composite makes the
   observation **self-describing and searchable without loading the payload** (search "all
   uint16 fluorescence stacks at 0.5 µm/px" by reading the small statement doc).

   `image` composite fields:
   - `dtype` (char) — `uint16` | `uint8` | `single` | … (was the misnamed `image_type`).
   - `axes` (structure[]) — per-axis `{name, length, spacing, unit}` (e.g. Y,X,C,Z,T);
     recovers the full N-D calibration the old `x/y_resolution` (2 axes only) *lost*.
   - `color_model` (ontology_term, T8 binding) — grayscale | rgb | multichannel.
   - `channels` (string[]) — per-channel labels (e.g. `['GCaMP','tdTomato']`).
   - `value` (matrix) — the pixels; populated **iff** `storage_mode: inline`, else empty.

5. **Modality → the `variable`**, not a field. The v1 `label` ("a two-photon stack") is the
   modality description; it already rides on `subject_statement.variable` as an ontology
   term. Not stored twice.

6. **`image` is NOT an entity** (contrast with `software`). openMINDS has no `Image` type —
   an image is a `File` = DATA — so its raster is a data_body, not a citable agent.

7. **The v1 `image` vs `image_stack` split IS the two-body split** (T6):
   - v1 `image` = `{label, format, compression}` + a single `imageFile` → an **encoded**
     still → `opaque_body` (format/compression describe the encoding).
   - v1 `image_stack` = `data_type`/`dimension_order`/`dimension_size`/`dimension_scale` →
     a **decoded** N-D array → `sampled_body` (or opaque per decision 3).

## Bugs this build must fix (found during the walkthrough)

- **Strand risk (introduced by Item-2's abstract reparent):** `image` is now abstract with
  **no `image` migrator**, so any standalone v1 `image` (encoded-file) doc would fail
  validation (abstract can't be instantiated). The fast gates don't catch it (no
  standalone-`image` fixture); the full corpus would. **The build MUST add the `image`
  migrator (below) — or, if standalone `image` docs are confirmed absent from corpora,
  record that.** This is the top build item.
- **`image_stack` migrator stamps `data_type` (uint16) into `image_type`** — dtype in the
  wrong (misnamed) slot, *duplicating* the body's `datum.dtype`. Route it to the `image`
  composite's `dtype` descriptor (decision 4) instead.
- **N-D calibration loss:** the migrator maps only `dimension_scale` X/Y into
  `x/y_resolution`; the Z/channel/time scale is dropped. `axes` recovers it.

## Deferred build tasks (the batch)

1. **`image` composite fields** → the decision-4 set (`dtype`, `axes`, `color_model`,
   `channels`, `value`); drop `image_type`/`image_format`/`x_resolution`/`y_resolution`/
   `resolution_units`.
2. **Add `image_manipulation`** = `subject_manipulation` + `image`.
3. **Fix `image_stack` migrator**: populate `datum.dtype` + `axes` (from `data_type`/
   `dimension_order`/`dimension_size`/`dimension_scale`); set the `image` composite descriptors
   inline; stop stamping `image_type`; `storage_mode: body` (opaque by default; sampled if
   chunked-read needed).
4. **Add `image` migrator** (encoded still → `image_observation` + `opaque_body`; carry
   `imageFile` via `file_list` like `pyraview`; `format`/`compression` → the opaque body's
   encoding; `label` → variable). Resolves the strand risk.
5. **Fixtures/tests**: an **inline** image_observation (small matrix in `value`), a
   **body** image_observation (opaque), an **image_manipulation** (stimulus), and — later —
   a **reference** multi-subject FOV.
6. **openMINDS crosswalk**: `format`/`color_model` ≈ openMINDS `ContentType`; note it.

## `ngrid` / `array` — KILLED as a data_type; `ngrid` → `sampled_body` (audit R4, re-audit REVISED)

**`array` is KILLED (final re-audit decision) — there is no `array` data_type.** `ngrid` is a
labeled N-D **numeric grid** whose bulk data was a file (`ngrid_file`) — i.e. a **format
carrier**, not a value type. By T6, every carrier (timeseries/dataseries/zarr/image-as-file/
generic_file/pyraview/…) **phases into the two data_bodies**, and `sampled_body` is *already*
"self-describing — sample-time axis + typed datum," which is exactly what a bare N-D numeric
grid is. So a generic `array` composite would **duplicate `sampled_body`** (T6) and **name a
container, not content** (T13, the dumping-ground smell). Decisions:
- **`ngrid` → phases into `sampled_body`** like every other carrier (drop `ngrid_file` +
  `element_id`). NOT a `data_type`.
- **`image` stays a STANDALONE `data_type`** — this **reverses the earlier `image ⊂ array`**;
  with no `array` parent there is nothing to duplicate, and `image` is genuinely meaningful (a
  raster *picture*: `dtype`/`axes`/`color_model`/`channels`), storing its pixels in a body.
- **Receptive-field fold:** `reverse_correlation` / `hartley_reverse_correlation` /
  `hartley_calc` still fold to `subject_calculation` leaves, but the RF map = a **`sampled_body`
  value** (meaning rides on the leaf's `variable`), **not** an `array` value.
- A **genuinely meaningful** numeric array (a `kernel`, a specific RF type) is minted as its
  *own named* `data_type` only when T12 warrants — never a generic `array`.
- **Principle this rests on:** a raw-numeric observation with no dimensioned meaning is valued
  by a **bare self-describing `sampled_body`** (its `dtype`/`axes` live on the body; the
  `variable` carries the label) — the dimensioned data_types (`voltage`, …) just *add* units on
  top. Built in the same batch (TaskList #24).

## Deferred / out of scope

- **`kernel` / small-matrix data_type** (e.g. a 3×3 conv filter): a kernel is *not* a
  picture — mint a distinct small-matrix `data_type` at a future date if needed. For now,
  `image` + `inline` can hold small rasters; kernels wait.
- **Reference (shared) case** beyond the opt-in `storage_mode: reference` mechanism — the
  full ROI-per-observation shape is only fleshed out when a real multi-subject-FOV corpus
  needs it.
