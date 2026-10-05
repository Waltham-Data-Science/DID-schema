# V_eta: `study`, `instance_of`, `awarded_to`, contributor `roles`

Four schema additions made for the Haley V2 import (NDI-matlab
`+ndi/+setup/+conv/+haley/import_V2_decisions.md`, entries 8, 11, 14, 18),
built in did-schema PR #78.

- `study` (draft entity): a unit of research with its own question and design,
  between the dataset and its sessions (ISA investigation / study / assay).
  Fields `name` (required), `short_name`, `description`, `factors` (the
  variables deliberately varied; same terms as statement `variable`), `design`.
  `part_of` widened: session -> study, study -> dataset, study -> study.
  Not `protocol` (a recipe) and not `experiment` (the source lab uses that word
  for both the study and the day).
- `instance_of` (relation, subject -> product): an instrument is a unit of a
  bought product. A relation rather than `subject.product_id` so the product can
  be added after the instrument without rewriting either document.
- `awarded_to` (relation, funding -> person/organization): an award's recipient.
- `directed_relation.roles` (bound, preferred): the 14 CRediT contributor roles
  plus `corresponding author`, on a `has_author` / `contributed_by` edge.

TEAM-SIGN-OFF: jess / 2026-09-30 -- add the study entity (name, short_name, description, factors, design) and widen part_of to session->study, study->dataset, study->study
TEAM-SIGN-OFF: jess / 2026-09-30 -- add the instance_of relation (subject -> product) instead of a subject.product_id field
TEAM-SIGN-OFF: jess / 2026-09-30 -- add the awarded_to relation (funding -> person/organization)
TEAM-SIGN-OFF: jess / 2026-09-30 -- add directed_relation.roles, bound to the 14 CRediT roles plus corresponding author

## Session fields (did-schema PR #79)

- `session.description` (optional): a free-text record of the session -- what
  was done, the lab notebook entry, notes about the day.
- `session.name` (optional): a display name beside `local_identifier`, which
  stays the stable handle (spaceless by convention; not schema-enforced).

TEAM-SIGN-OFF: jess / 2026-09-30 -- add optional session.description
TEAM-SIGN-OFF: jess / 2026-09-30 -- add optional session.name as a display name beside local_identifier

## Subject field (did-schema PR #80)

- `subject.name` (optional): a display name beside `local_identifier`, as
  `session.name`. `local_identifier` stays the stable, spaceless handle
  (`concentration_assayPlate0011`); `name` is for people ("Assay Plate 0011",
  "Axio Zoom.V16"), may carry spaces, need not be unique, and can be corrected
  without breaking anything, because nothing refers to a subject by name.
TEAM-SIGN-OFF: jess / 2026-10-01 -- add optional subject.name as a display name beside local_identifier

## `contained_in` is timed (did-schema PR #84)

- The relation registry marked `contained_in` `timed: false`, so a
  `contained_in` edge was not declared to carry a `time_reference`. The Haley
  import's stage 6 (NDI-matlab decision #52) gives every one a window: a worm is
  on its acclimation plate, then its food deprivation plate, then its assay
  plate, each from one transfer to the next. The flag now says `timed: true`,
  like `member_of`, `derived_from` and `sample_of`. Nothing enforced the flag,
  so no document changes; the registry now says what the documents do.
TEAM-SIGN-OFF: jess / 2026-10-02 -- contained_in is timed, like member_of

## `subject.type` (did-schema PR #84)

- `subject.type` (optional, bound, required strength): what kind of thing a
  subject is, at the coarsest level. Seven values:

  | value | meaning | examples |
  |---|---|---|
  | organism | one whole living individual | a worm, a mouse |
  | culture | a mass grown as one, whose members are never subjects | a bacterial lawn, a cell culture |
  | tissue | part of an organism | a slice, a biopsy, a brain region |
  | cell | one cell | a neuron, a sorted unit |
  | group | a subject whose members are subjects, by `member_of` | a cohort of worms, a neuron ensemble |
  | device | an instrument | a camera, a probe, an electrode |
  | material | a non-living object or substance | an agar plate, a dish |

- **This reverses, for the coarse kind only, `V_eta_migration_plan.md` A.2**
  ("kind is a bound `term_assertion`, not a field") and the matching line of
  `V_eta_SPEC.md` §1. Why: the subject-defining assertions (species, cell type,
  instrument type, material type) cannot tell an organism from a tissue, a
  culture or a cell of the same species (a worm and the lawn it forages on both
  carry only a species), and A.2's "presence is an ingestion-layer invariant"
  was not built. The coarse kind is known when a subject is made; the finer kind
  (species, strain, cell type, instrument type) is often learned later and stays
  an assertion, as T1 intends.
- `group` brings back the removed `is_group`, but checkably: a group's members
  are subjects with a `member_of` edge to it, and only a group has them. That is
  a batch rule (across documents), not checked per document. A mass whose
  members will never be subjects (a lawn, a culture) is a `culture`.
  `is_biological` is not stored: it is every value except device and material.
- "cell population" was considered and dropped: it mixed a culture (biology)
  with an ensemble (a grouping of identified cells), which are `culture` and
  `group`.
- Named `type`, after `acquisition_channels.channels.type`; on `subject`,
  `subject_type` would repeat the class. Optional, because migrated v1 subjects
  carry no kind; a migrator may fill it from the v1 class.

## `distributive` (did-schema PR #84)

- `subject_statement.distributive` and `directed_relation.distributive`
  (optional boolean): on a statement or relation about a group, true means it
  holds of each member (a cohort moved to a plate: each worm was moved). Absent
  or false is the literal reading: it is about the group as a whole and says
  nothing about any member (a cohort's size). So nothing is applied to every
  member unless it says so.
- Prompted by the Haley import, which puts the transfers, plate windows,
  species and strain of a cohort of worms on the cohort, with each worm
  `member_of` it (NDI-matlab decisions #54 and stage 7).
TEAM-SIGN-OFF: jess / 2026-10-02 -- add optional subject.type (organism, culture, tissue, cell, group, device, material), superseding A.2 for the coarse kind only
TEAM-SIGN-OFF: jess / 2026-10-02 -- add optional distributive on subject_statement and directed_relation

## `documented_by` a recipe (did-schema PR #84)

- `documented_by` (child -> `web_resource`) allowed only an `entity` as the
  child. A `formulation` is a `data_type`, not an entity, so a standard recipe
  could not cite where it is written down. The child may now also be a
  `formulation`. Prompted by the Haley import: S-Complete and LB were made by
  the Salk media kitchen to the standard recipes, and WormBook (Stiernagle
  2006, "Maintenance of C. elegans", doi:10.1895/wormbook.1.101.1) is taken as
  their source, so each recipe is written out as ingredients and
  `documented_by` the WormBook chapter.

## `formulation.value.type` (did-schema PR #84)

- `formulation.value.type` (optional `ontology_term`, bound like
  `subject_statement.variable`: preferred strength, node in CURIE form): what
  kind of mixture a formulation is, the standard recipe or medium it is
  ("S-Complete", "LB", "NGM, 3% agar, no peptone"). The counterpart of
  `subject.type`, inside `value` beside `ingredients`, `ph` and
  `osmolarity` because a `data_type` exposes one payload field and its
  descriptors ride inside the cell (T14). `base.name` is refused in V_eta (#73 item 54), so a
  formulation had no name at all: it was identifiable only from its ingredient
  list, and two standard recipes `documented_by` the same source (WormBook's LB
  and S-Complete) could not be told apart.
- A term rather than a free-text name: it is given by name with its node staged
  until the ontology lookup, then is queryable across datasets ("everything
  grown in LB"). It classifies the recipe; the recipe is still its ingredients
  (or its product), so a term does not make a formulation a `chemical` (one
  pure substance, as bought). Left out for a one-off mixture, such as a day's
  OD600 0.5 dilution, which is no standard kind.
TEAM-SIGN-OFF: jess / 2026-10-03 -- a formulation may be documented_by a web_resource, so a standard recipe cites its source
TEAM-SIGN-OFF: jess / 2026-10-03 -- add optional formulation.value.type, a term naming what kind of mixture a recipe is

## `humidity` (did-schema PR #86)

- A new data type `humidity` (draft), with one leaf, `humidity_observation`.
  Its value cell's canonical slot is `percent_relative_humidity` (0-100), with
  `source_value`/`source_unit` keeping what the source wrote. Prompted by the
  Haley import's stage 9: each recording carries the room's temperature and
  relative humidity (`temp`, `humidity`, in %RH), and V_eta had no type for a
  humidity.
- Relative humidity is a dimensionless ratio with no SI unit; percent is the
  unit every room sensor reports, so it is canonical under practical SI (T14,
  below). The slot is named for the quantity and its scale, as a dimensionless
  quantity's slot is (T14), so 45 and 0.45 cannot be confused.
- Absolute humidity is a different quantity (mass of water per volume of air).
  When a source has it, it becomes a second slot on this type
  (`grams_per_cubic_meter`), as `concentration` carries several forms, rather
  than a second type.

## T14: canonical units are practical SI (did-schema PR #86)

- A new T14 bullet states the rule the schema already followed: canonical units
  are the units the field's practitioners use, not strict SI base units --
  grams (not kilograms), liters, celsius, mmhg, degrees (not radians), percent
  relative humidity -- with `source_value`/`source_unit` keeping what was
  written. Until now it lived only in builder text (`build_v_eta.py`) and plan
  amendments (#73 item 44 for degrees; mass to grams on 2026-09-23), so the
  tenets could not answer "which unit is canonical".
TEAM-SIGN-OFF: jess / 2026-10-03 -- add the humidity data type, canonical percent_relative_humidity, with a humidity_observation leaf
TEAM-SIGN-OFF: jess / 2026-10-03 -- T14: canonical units are practical SI

## `length_calculation`, `velocity_calculation`, `intensity_calculation` (did-schema PR #86)

- Three calculation leaves, each a statement direction crossed with an existing data
  type (T3), minted because the Haley import's stage 10 needs them. Under T2's rule a
  value computed from data in the dataset (the videos, the E. coli images) is a
  calculation, and these types had no calculation leaf:
  - `length_calculation`: a worm's distance to the nearest patch edge per frame
    (`distanceLawnEdge`); an E. coli patch's peak offset from its edge (`xPeak`).
  - `velocity_calculation`: a worm's smoothed speed per frame (`velocitySmooth`).
  - `intensity_calculation`: an E. coli patch's fluorescence profile against distance
    from its edge, its amplitudes (`borderAmplitude`, `centerAmplitude`, `yPeak`,
    `yOuterEdge`), and the fitted background image they were normalised by.
- Positions use the existing `position_calculation`, the patch and arena masks and
  `closestLawnID` the existing `label_calculation`, and circularity the existing
  `score_calculation`.
TEAM-SIGN-OFF: jess / 2026-10-03 -- add length_calculation, velocity_calculation and intensity_calculation leaves

## `timed_sequence` becomes `item` (did-schema PR #87)

- **`timed_sequence` is renamed `item` and generalised**: a value that names, at each
  position along its keys, ONE document out of an ordered list of distinct documents.
  Its structure does not change -- the distinct documents are the ordered, multiple
  `item_id` edges, and the value holds a 0-based position in that list -- but nothing
  in it is about stimuli or time any more.
  - Prompted by the Haley import's stage 10: `closestLawnID` is, per video frame, the
    patch nearest the worm. Its values are patch SUBJECTS, not text; `label` would
    store a name that only resembles a subject's local identifier.
  - Named for what the value is, like its neighbours `term` (an ontology term) and
    `label` (a local name): each value is an item of the listed set. The variable says
    what kind of item ("nearest patch", "visual stimulus"), so the type needs no
    qualifier (T13). Rejected: `item_index` (names the encoding, not the content),
    `reference` / `referent` (taken by the time references and `referent_id`),
    `document`, `entity` (taken), `member` (reads as `member_of`).
- **Changes:**
  - `item_id` may point at ANY document (was `data_type` only), so an item can be a
    subject. Still ordered, multiple, deduplicated.
  - `value.presentation_order` is renamed `value.item`: one 0-based position in
    `item_id` per position along the keys. A position with no item is empty: NaN
    inline, the body's `fill_value` when the values are in a body (a track's
    tens of thousands of frames are).
  - **Time is no longer built in.** The value's keys are the inherited `keys`, whatever
    the statement needs: a stimulus sequence keeps its onset key (`variable` time,
    irregular); the nearest patch is keyed by video frame.
  - `control_item` (which item is the control condition) and `offset` (per-position
    end times, only when the key is time) stay, optional.
  - Leaves: `timed_sequence_manipulation` is renamed `item_manipulation` (the stimulus
    sequence shown to a subject); a new `item_calculation` (the nearest patch,
    computed from a track and the patch mask). Both draft.
  - Supersedes, for `closestLawnID` only, the PR #86 note that it would be a
    `label_calculation`.
- **Everything that names the old classes moves with it**, as one change across
  three repositories, each with its own PR and CI, landing together:
  - did-schema: the builder, coverage, status and bar-2 tools and their tests;
    `visual_grating.blank`'s documentation.
  - DID-matlab: the stimulus migrators (`stimulus_presentation`,
    `control_stimulus_ids`, `hartley_calc`) and their tests.
  - NDI-matlab: the stimulus second pass (`stimulusPresentationToTimedSequence`,
    `local.m`) and its tests.
  - Dated records (plan documents, corpus results, CLAUDE.md) keep the name they were
    written with.

## Tenet audit, 2026-10-04 (did-schema PR #87)

Every non-deprecated class (212 of 217; 70 of them retired v1 tombstones, held to their
own v1-spelling rule) checked against T1-T16 on main `967f84a`. Passed with nothing
found: T13 (no `is_`/`has_` booleans, no camelCase), T15 (every edge `_id`, every
repeated edge `ordered`, no count on a single edge; `ensemble.neuron_id_#` is a v1
tombstone), T14 (one `value` payload, the full cell on all 29 dimensioned types, every
canonical slot names its unit), T3 (every leaf a direction x a data type, but see 1),
#73 item 54 (`local_identifier` only on subject, session, epoch). Fixed here:

1. **`humidity` is a concrete `data_type`** (it was `base` and abstract: PR #86 wrote it
   like `spatial_frequency` but left it out of the build's `DATA_TYPES` list, so it was
   never reparented, #73 item 19). A new test, `test_value_bearing_classes_are_data_types`,
   fails any class carrying a `value` that is not one, naming the time references and
   NDI's `demo` fixture as the only exemptions. No new decision: the signed rule, applied.
2. **T14's value-cell bullet catches up with CHANGE 7** (signed 2026-10-02): the cell is
   `{<canonical slot>, source_value, source_unit, approximate, tolerance}`, and the
   sentence "No per-value `uncertainty` field exists" goes. The meta-schema's description
   says the same.
3. **`variable` and `method` are documented as T16 says**: `variable` is a property, never
   the act; `method` is the technique, recorded only when it adds something, never a
   direction-restating word. The old `method` text recommended "measurement".
4. **`relation.method` is bound like `subject_interaction.method`** (preferred, CURIE form),
   its examples written as plain names.
5. **T6's cache paragraph speaks T15**: a cache body is owned by a calculation whose
   `input_id` edges name its sources (it said "marked `derived_from` its source
   subjects", and `data_body` has no such edge).
6. **`product` and `acquisition_channels` become stable**: stable classes point at them
   (`chemical`/`formulation`/`strain.product_id`, `subject_interaction.acquisition_channels_id`).
7. **Binding parity for `variable`**: the `variable` of a key (`data`, `acquisition_epoch`),
   a condition (`subject_statement`, `data_body`) and a method parameter
   (`subject_interaction`, `method_parameters`, `clock_alignment_configuration`) is bound
   like the statement's own (preferred, CURIE form). Units stay unbound (no unit registry,
   D9), as do model-fit coefficient names (the model's, not a property). Bound fields
   23 -> 31; the binding-governance baseline for uncatalogued bound fields 20 -> 28.

Not changed, still open: `strain.species`, `chemical.value.substance`,
`coordinate_system.origin`/axes and `score.value.scale` have no vocabulary to bind to
yet (T8, blocked on the ontology lookup). `subject_calculation` requires
`interpreter_id` and `operating_system_id`, which a compiled program (WormLab) does not
have an interpreter for: answered in the next section.

## `interpreter_id` is optional (did-schema PR #87)

- `subject_calculation.interpreter_id` becomes optional; `operating_system_id` stays
  required. #73 item 53 required both, assuming every calculator runs in an interpreter
  (MATLAB, Python). A compiled program -- WormLab, which produced the Haley import's
  tracks -- runs on an operating system with no interpreter, so a required edge would
  force an invented one. Present whenever the calculator runs in an interpreter.
## `key_id`: a key's positions from another document (did-schema PR #87)

- **`key_labels_id` is renamed `key_id`**, and the key field `labels_from` is renamed
  `positions_from`. Prompted by the Haley import's stage 11 (the encounters), discussed
  2026-10-05.
  - The edge says "this key's positions live in that document", so it mirrors
    `value_id` ("my value lives in that document").
  - The positions are not always labels: a worm's encounter list is its onset times.
    The rename says what is taken -- the positions -- not one kind of them.
- **It may point only at a `data_type` document** (was any document, `base`):
  - a statement leaf: the cell list (a `label_calculation`), a worm's encounter onsets
    (a `time_calculation`);
  - or a standalone value: the gene list (a standalone `term`, #73 review item 21).
  - Never a subject, an entity or a body. Statement leaves are data types too, so
    "only subject statements" would have excluded the signed gene list.
- **The meaning is unchanged:** position k along the key is entry k of the referenced
  document's value, which names it; `n` must equal its number of entries.
- **Nothing wrote the edge before the rename.** The DID-matlab builders that name it
  (`did2.build.key` `LabelsFrom`, `KeyLabelsIds` on bodies) follow in their own PR.
- **T14 gains a bullet** stating where a key's positions come from (listed, or taken
  from one document through `key_id`).

## Repeated events (did-schema PR #87)

- **T2 gains a paragraph on repeated events.** The time-reference rule (signed
  2026-09-30) allows a document ONE instant or extent between its time references, so
  N occurrences are never N time references on one document. The paragraph says what
  to do instead:
  - **a one-off event** is its own statement with its own time reference;
  - **a recurring event with its own measurements** (a worm's patch encounters) is a
    LIST statement whose value is the occurrences' onsets, plus one statement per
    measured quantity keyed by that list through `key_id`;
  - **a protocol repeating an action on a schedule** (a stimulus sequence, five
    identical doses) is an `item` keyed by onset.
- Considered for the encounters and rejected:
  - one set of documents per encounter (about 20 times the documents; it only pays
    off if single encounters need their own notes or corrections later);
  - one "encounter" data type bundling the measurements (T12: they already have types,
    and a bundle breaks queries such as "all speeds");
  - a repeating time reference ("every 10 min, 5 times"; a strict-schedule shorthand
    that conflicts with the one-extent rule, left until a dataset needs it).

## `time_calculation` and `acceleration_calculation` (did-schema PR #87)

- Two calculation leaves (T3: direction x data type, made when needed), for the Haley
  import's stage 11, computed from the tracks so calculations (T2 rule):
  - `time_calculation`: a worm's encounter onsets (the encounter list) and each
    encounter's time to slow down (`timeSlowDown`);
  - `acceleration_calculation`: the deceleration on entering a patch (`decelerate`,
    um/s^2 -> m/s^2).
- Both draft, like the other stage 10-11 leaves.

TEAM-SIGN-OFF: jess / 2026-10-04 -- timed_sequence becomes item: item_id may point at any document, value.item replaces presentation_order, keys as needed; item_manipulation and item_calculation leaves
TEAM-SIGN-OFF: jess / 2026-10-04 -- tenet audit fixes: humidity is a data_type; T14 cell includes tolerance; T6 cache via input_id; variable/method documented per T16; relation.method and key/condition/parameter variable bound like the statement's; product and acquisition_channels stable
TEAM-SIGN-OFF: jess / 2026-10-04 -- subject_calculation.interpreter_id is optional; operating_system_id stays required
