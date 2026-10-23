# Tenet-audit decisions, Jess Haley, 2026-10-22 — build spec

Source of truth for the audit batch. Every item below was decided by Jess Haley in
conversation on 2026-10-22 (her answer in quotes). Each becomes a
`Decided by Jess Haley, 2026-10-22 [<tag>]: ...` line in the named plan document,
in the same commit as its build (CLAUDE.md rule 4). Nothing here may be recorded
as decided beyond what is written.

Evidence files (scratchpad): audit/T1-T7.md, audit/T8-T14.md, audit/T15-T20.md,
acq_compare.md, vocab_nodes.md.

## EMPTY id allocation (next free was EMPTY:0000370; registry max 0000369)

| id | label | definition |
|---|---|---|
| EMPTY:0000370 | analog input channel | A channel through which an acquisition system samples a continuously valued signal. (synonym `ai`) |
| EMPTY:0000371 | analog output channel | A channel through which an acquisition system emits a continuously valued signal. (`ao`) |
| EMPTY:0000372 | digital input channel | A channel through which an acquisition system samples a two-state signal. (`di`) |
| EMPTY:0000373 | digital output channel | A channel through which an acquisition system emits a two-state signal. (`do`) |
| EMPTY:0000374 | time channel | A channel whose values are the times at which the other channels were sampled. (`t`) |
| EMPTY:0000375 | auxiliary input channel | A channel through which an acquisition system samples a signal that supports, rather than is, the primary measurement. (`ax`) |
| EMPTY:0000376 | event channel | A channel whose values are the times at which events occurred. (`e`) |
| EMPTY:0000377 | marker channel | A channel whose values are codes, each at the time it was recorded. (`mk`) |
| EMPTY:0000378 | follows protocol | (relation) between a body of work and a written procedure it was carried out by. |
| EMPTY:0000379 | distributed as | (relation) between a genetic line and a product under which it is supplied. |
| EMPTY:0000380 | paired with | (symmetric relation) between two entities that belong together as a pair. |
| EMPTY:0000381 | gene alias mapping | (relation) between a list of gene names and the list that gives each gene under another of its names. |
| EMPTY:0000382 | instance of | (relation) between a particular thing and the product or genetic line of which it is one individual. |
| EMPTY:0000383 | recording epoch | One continuous stretch of recording by one acquisition system. (entity type `epoch`) |
| EMPTY:0000384 | signed distance to region boundary | The distance from a point to the nearest boundary of a region, positive inside the region and negative outside it. |
| EMPTY:0000385 | seeding volume | The volume of a solution or suspension placed to seed a culture. |
| EMPTY:0000386 | orthologous gene mapping | (relation) between a list of genes and a list giving each gene's ortholog in another species. |

Obsolete (empty-ontology, `oboInOwl:consider`): EMPTY:0000350 → EMPTY:0000384;
EMPTY:0000122 arena diameter → PATO:0001334; EMPTY:0000120 bacterial patch volume →
EMPTY:0000385. (EMPTY:0000140 already obsoleted in empty-ontology #24.)
The 6 EMPTY relation terms (0000378-0000382, 0000386) are the first OWL ObjectProperties in empty-ontology.

## Decisions

**A1 [epoch to system link]** ("A1 agreed"). Drop the `recorded_by` relation row.
An epoch reaches its acquisition system through the recording interaction's
`acquisition_channels_id` → `acquisition_channels.acquisition_system_id`.
`acquisition_system.device_id` is filled when known (Haley: the camera entity,
`instrumentFor` in sessionDocuments.m). Depends on B2.

**A2 [member_of endpoints]** ("a sounds fine"). `member_of`: parent_types = [group];
child_types add `software`.

**B1 [ingested epochs found]** ("B1a"). NDI vintage rule so the classic navigator's
`isa epochfiles_ingested & depends_on filenavigator_id` query (navigator.m ~514)
finds migrated `ingestion_manifest` documents via `epoch_file_pattern_id`; test on
migrated B (2,484 ingested epochs; Dab 4,088; Soph 349).

**B2 [channel types]** ("agreed, B2a with 10"; "should be real terms"). 
`acquisition_channels.channels.type` binds the 10 hardware channel types, root
NCIT:C44170 Channel: md → NCIT:C52095 Metadata, tx → NCIT:C25704 Text, and
EMPTY:0000370–0000377. The v1 prefix is each term's exact synonym. The 8 derived
read modes (dep den dimp dimn aep aen aimp aimn) get NO terms (0 uses in corpus
probemaps: B {mk,e,md,ai}, Dab {mk,e,ai,md,ao}, Soph {mk,e,md,ai}). Migrator maps
prefix → term; NDI vintage maps term → prefix for readers. Origin of the old
4-value list: d329ef0 copied daqsystemstring.m's example.

**C1 [calculator units]** ("C1a"). orientation_preference, direction_preference,
half_width_at_half_maximum: degree. spatial-frequency preferred_value: cycles per
degree. temporal-frequency preferred_value: Hz. Generic
tuning_curve_calculation.preferred_value takes its unit from the curve's covariate
`unit` (named rule).

**C2 [units bound]** ("C2a"). `unit` on covariates, conditions and method
parameters binds to registered unit terms; restore the canonical-unit list as a
gate in tools/ (read by check_term_registry).

**M1 [remaining units bound]** ("M1a"). Also bind `response_unit` (tuning_curve,
contrast_sensitivity) and the fit entry's unit fields; register missing units
(spikes per second; dF/F as a dimensionless ratio).

**D1 [tenet signature text]** ("a"). Tenets lines ~58/381/441 (method amendments;
signed by `V_eta_method_plan.md` TEAM-SIGN-OFF [method]), ~804 (T17; line 1019),
~979 (T20; line 1020): "not signed" → signed, citing the line.
`check_signoff_header_staleness.py` also catches in-text "not signed".
**N2 [T1 and T5 signed]** ("N2 yes"): Jess signed the T1 and T5 amendments on
2026-10-21; record a decision line so "signed by her" stands.

**D2 [ensemble retired]** ("a"). Retire the `ensemble` class. Migrate v1 ensembles
per `V_eta_migration_targets.json` ensemble.how: a group entity, `member_of` per
neuron carrying `order` (column order) and its epoch, per-neuron spike times in a
`sampled_body`.

**E [audit mechanical fixes]** ("E yes"): interaction.software_id doc (optional on
calculations); `matrix` docs drop "a vector is [a, b, c]"; tuning_curve "stimulus
condition term still to be chosen" → XCO:0000000; re-key the Gene Expression
binding row off retired spatial_gene_expression_pyramid; om:RelativeHumidity
definition; stale tenet names (timed_sequence, datum_type, `<value>_<direction>`
leaves T11, subject/web_resource T9, T15 table key_labels_id/strain/build_v_eta.py,
T2 method "proposed", T2 clock_alignment input_id exception); ~15 field docs with
retired names; EMPTY:0000140 marked obsolete in the registry (row removed once NDI
stops writing it).

**E2 [audit mechanical fixes 2]** ("E2 yes"): rule `variable_once` covers a body's
conditions; named rule for decision 6.3a (datum_order required on a
multi-dimensional sampled body; fix "Empty means F" doc); pattern-syntax docs
(syntax is the class behind software_id); acquisition_channels stale note and its
two uses; stale `acquisition_system ⊂ entity` / `acquisition_metadata_reader_#`
prose (daq decisions doc; daqsystem.m, vintage/map.m, isaQuery.m comments).

**F1 [epoch dissolution before merge]** ("i"). Build the SIGNED acquisition_epoch
dissolution (V_eta_epoch_plan.md TEAM-SIGN-OFF [epoch] 2026-08-08/08-17 and
AMENDMENT 1) before merge, with D2: DID pass 1 emits relative_reference + epoch
anchor + observation edges; NDI second pass attaches the sampled_body (dimensions +
covariates) to the element entity's observation (spikes: the neuron's spike-time
observation); port loadaddedepochs/readtimeseries (characterisation test NDI
0d97bc69f). acquisition_epoch then retires.

**F2 [logical entries]** ("F2a"). Add the `logical` form to conditions and method
parameters.

**G1 [developmental stage]** ("G1a, but also shouldn't a developmental stage
always be an observation since it is time dependent?"). Binding takes the stage from
an interaction (observation or calculation), never an assertion; roots
UBERON:0000105 + WBls life-stage root; binding names = ontology labels
("Developmental Stage", "Species").
**[T2 time-varying property]** ("add the tenet"): T2 gains "A property that can
change during an entity's life is never an assertion; it is stated by an
interaction, which carries its time."

**G2 [one fit entry]** ("G2a"). One fit entry: `model_fit`'s shape with `model`
bound; tuning and contrast calculators use it with their own results beside it.

**G3 [clock alignment relation bound]** ("G3a"). Bind `clock_alignment.relation` to
the closed list of kinds resolveClockAlignment.m writes; add a relation_bindings
row with passes: nothing.

**G4 [irradiance]** ("G4a"). New `irradiance` value kind, canonical W/m²;
`intensity` stays dimensionless; T12's example says a measured light intensity
uses `irradiance`.

**G5 [distance]** ("G5a"). Retire `measured_distance_to`. A distance is an
observation/calculation, variable PATO:0000040 (or the O3 signed term), about the
measured-from entity; the reference is a `document` condition (fixed) or covariate
along time (changing).

**G6 [vocabulary nodes]** ("G6a"). Every relation name and entity type gets a node;
T19 says relation and entity-type vocabularies are terms like any other. Table:
vocab_nodes.md with these rulings —
- K0 ("look fine"): part_of BFO:0000050, included_in schema:isPartOf, member_of
  RO:0002350; has_author schema:author, cites schema:citation, funded_by
  schema:funding, issued_by schema:funder, affiliated_with schema:affiliation,
  has_custodian schema:maintainer, contributed_by schema:contributor,
  copyright_holder schema:copyrightHolder, input_data schema:isBasedOn,
  suborganization_of schema:parentOrganization, documented_by schema:subjectOf;
  EMPTY: follows protocol, distributed as, paired with (sample of / passage of
  superseded by K5); entity types organism COB:0000022, cell CL:0000000, group
  NCIT:C43359, device COB:0001300, strain NCIT:C14419 (existing row), product
  schema:Product, software IAO:0000010, person NCIT:C25190, organization
  OBI:0000245, funding NCIT:C16644, dataset NCIT:C47824, publication IAO:0000311,
  protocol OBI:0000272, session NCIT:C67447; 8 channel EMPTY terms.
- K1 ("k1a"): contained_in node → RO:0001025 located in (RO:0001018 obsolete in
  ro 2026-09-04 release).
- K2 ("k2b"): derived_from narrowed to material that is used up, so RO:0001000 fits.
- K3 ("k3a"): register prefixes SIO and owl; alternative_of → SIO:000497,
  same_as → owl:sameAs.
- K4 ("developed by as producer is probably fine"; reuse where a fit exists):
  developed_by → schema:producer; sold_by → OBI:0000647 has_supplier; encountered →
  RO:0002437; awarded_to → schema:fundedItem; hosted_by → schema:provider;
  instance_of, distributed_as, paired_with, gene alias mapping, follows_protocol
  stay EMPTY (0 writers for follows_protocol / gene mappings).
  orthologous gene mapping ("agree"): new EMPTY:0000386 "orthologous gene mapping"
  (RO:HOM0000017 relates genes, not gene lists). Rows' endpoint types ["term"] are
  correct (a gene list is a standalone `term` value document, signed item 21).
  The gene_list_mapping migrator stays post-merge (task #100).
- K5 ("a"): sample_of, aliquot_of, passage_of → ONE relation on RO "derives from
  part of" (ENVO:01003004, published in RO); aliquot_of and passage_of retired
  (0 writers).
- L1 ("a"): a relation's stored `name` is the ontology label ("part of", "member
  of", "derives from part of"); code matches relations by node; snake_case handles
  become registry synonyms. All writers/readers in did-schema, DID-matlab, NDI.
- L2 ("L2 yes"): the same for entity types and channel types (e.g. "Grant",
  "Data Set", "analog input channel"); code matches by node.
- L3 ("L3a"): tissue UBERON:0000479; study NCIT:C63536 Study; material
  BFO:0000040 material entity; epoch EMPTY:0000383 recording epoch.

**H1 [software location]** ("H1a"). Software an NDI object is rebuilt from (behind
acquisition_system / acquisition_reader / epoch_file_pattern) stays in EACH
session in both paths; only descriptive software dedups to the dataset.
softwareDedup changes. Answers deferred decision 8: keep the three Haley software
entities (record under "Deferred decision 8" in V_eta_go_forward_class_audit.md).

**H2 [required acquisition edges]** ("H2a"). acquisition_system.reader_id and
epoch_file_pattern_id required.

**I1 [ordered inputs]** ("I1a"). T20 Boundary adds: a document's own list of
inputs (formulation/dose ingredients, calculation inputs, a policy's rules) is not a
group; those are repeated edges under T15, ordered when position pairs an edge with
a value entry or is an algorithm's order. T15 adds: an ordered repeated edge lists a
document's own inputs; a set referred to as a unit by several documents is a group
(T20). No schema change.

**I2 [contained_in endpoints]** ("I2a"). contained_in child/parent types: physical
entities (organism, culture, tissue, cell, material, device, group). Records use
included_in.

**M2 [instrument and device]** ("a"). Keep interaction.instrument_id and
acquisition_system.device_id; no rule ties them. Docs: instrument_id "the device
that sensed or acted on the subject (electrode, stimulator, camera, thermometer)";
device_id "the device that produced the files this system reads (a digitizer, a
camera, a computer); the same entity as an interaction's instrument when one device
does both".

**N1 [filters are methods]** ("N1a"). Delete `frequency_filter` (a V2 invention; 0
occurrences in NDI ground truth; no tombstone). jFrequencyFilter writes a `method`
document (term = filter design; parameters band, passband/stopband edges in Hz,
filter order (count), ripple/attenuation dB); a body's `filter_id` → `method_id`.

**O1 [significance with results]** ("O1a"). tuning_curve_calculation.significance
moves into its value beside the fit entry; contrast_sensitivity
`model_fit.empirical_c50` → `c50`.

**O2 [ratio slots named by unit]** ("O2a"). mass_fraction → grams_per_gram;
volume_fraction → liters_per_liter; od600 → optical_density with the wavelength
(600 nm) as a condition or in the source unit "OD600". Haley OD600 and formulation
writers change.

**O3 [Haley terms general]** ("O3 agreed"): EMPTY:0000350 → EMPTY:0000384 signed
distance to region boundary + a condition pointing at the region's mask; arena-mask
method parameter EMPTY:0000122 → PATO:0001334 diameter; EMPTY:0000120 → EMPTY:0000385
seeding volume. Lands before the Haley rerun (post-merge rerun). Keep distance end
point and the plate kinds.

**O4 [missing integers]** ("O4a"). Integer slots accept NaN for a missing position
(stored as literal NaN); validator: whole number or NaN.

**O5 [coordinate system names]** ("a"). coordinate_system.dimensions → `axes`;
coordinate_system.origin → `reference_point` (NCIT:C45793). `data` unchanged.

**O6 [method shared plus own]** ("O6a"). An interaction may carry `method_id` (shared)
AND an inline `method` whose parameters add settings only this run had: no variable
in both; inline term empty. A changed shared setting still makes a variant method
document with parent_id. Replaces "never both" (team 2026-08-09).

**P1 [rules and clock_alignment tenet]** ("P1a"). Named validator rules: an
assertion has no time dimension; method_id + inline method share no variable (O6).
T15 gains a clock_alignment paragraph (a relation with four named edges).

**P2 [serial number]** ("P2a"). A device's serial number is an assertion, variable
IAO:0000131 serial number, text value; manufacturer via instance_of → product →
sold_by. Registry row + T18 sentence.

Not decided / open: none.

## Added after the walk (Jess Haley, 2026-10-22)

**S1 [registry holds nodes]** ("Shouldn't it just need nodes?"): no synonym field in
the term registry. v1 channel prefix → node maps live in the DID migrator and NDI
vintage map; code matches relations / entity types / channel types by node.

**S2 [synonyms]** ("approve the removals and keeps"; "a"): a synonym is a genuine
alternative name (average/mean) or a standard abbreviation; old labels and lab
vocabulary are not. Abbreviations typed OMO:0003000; labels from a published
release kept as OMO:0003008 previous name; lab column names stay in the lab
dictionaries (mapping). empty-ontology gets a conventions document. Built in
empty-ontology PR #25.

**S3 [loose ends]** ("fix"): EMPTY:0000141 obsoleted (consider 0000369) in PR #25;
Hunsberger 8-digit EMPTY ids fixed when that import is built.

**S3b [ethics assessment to jurisdiction]** ("agreed, b"): DID-matlab
metadata_editor / entityDoc stop writing obsolete EMPTY:0000355. v1 EthicsAssessment
values map to the ethics jurisdiction (EMPTY:0000359) term: "EU compliant" and
"EU compliant +" → European Union (the "+" kept as a note: an additional assessment
by the data-sharing initiative); "US compliant" → United States; "not required" and
any other value → no statement, counted note. (openMINDS v4 ethics_assessment
instances.) 0 corpus documents carry the field today.

**H1 scope [object software]** ("both ok"): software that NDI rebuilds an object
from = every ndi.vintage.map class with an object_edge (acquisition system, reader,
file pattern, syncgraph/syncrule clock alignment) plus any reader_id; all stay in
their session. Built: NDI 6c4a27c14.

**[presentation file declared]** ("both ok"): `presentation_time.bin` is an optional
declared file on `item` and `manipulation` (the stimulus fold keeps it attached,
decision 7.1c).
