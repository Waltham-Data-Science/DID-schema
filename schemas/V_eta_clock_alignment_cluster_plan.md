# V_eta — the clock alignment cluster (was syncrule / syncgraph / syncrule_mapping)

**DECIDED with the team, 2026-08-06. Build deferred. NO `TEAM-SIGN-OFF` LINE** —
the marker is the team's to write (Operating Rule 4).

**The team's words:** *"Record the whole cluster."* Reached over a long walkthrough in
which the team rejected four successive Claude proposals on naming and modelling
grounds; each rejection is recorded below with what it changed, because in every case
the objection was right and the reasoning is the useful part.

**SUPERSEDES** the `syncrule_mapping` and `sync configuration` sections of
`V_eta_infra_family_decisions.md`. Those sections contain statements now known false;
they are marked there and point here.

---

## GROUND TRUTH

```
DENOMINATOR   91 NDI templates on origin/main;  1,002 .m files
              5 corpora (20211116, B, Dab, JH, Soph), 221,813 v1 documents
              223 V_eta class schemas
```

### The three templates

```
syncrule ⊂ base                          template depends_on: (none)
   ndi_syncrule_class  "ndi.time.syncrule"
   parameters          []                 UNDECLARED

syncgraph ⊂ base                          template depends_on: []
   ndi_syncgraph_class "ndi_syncgraph"
   -- BUT syncgraph_schema.json:4 declares
      "depends_on": [ { "name": "syncrule_id", "mustbenotempty": 0 } ]

syncrule_mapping ⊂ base                   deps: syncgraph_id, syncrule_id
   cost         double
   mapping      matrix
   epochnode_a / epochnode_b {
      epoch_id, epoch_session_id, epochprobemap, epoch_clock,
      t0_t1, objectname, objectclass }
```

### Volumes (test-code.yml run #257 / 0458dae, 2026-07-29; quarantine 0 on all five)

```
                      20211116     B    Dab    JH   Soph
syncrule                     2    26     26     -     64
syncgraph                    1    13     13     -     32     ~one per session
session                      1    14     16     3     33
syncrule_mapping.epochid  (empty required edge)
                             -  2484   2484     -    348     = 5,316, 100% empty
```

### The four rule implementations, and their real parameter sets

```
filematch                        number_fullpath_matches (default 2)
filefind                         number_fullpath_matches (default 1), syncfilename,
                                 daqsystem1, daqsystem2
commonTriggersOverlappingEpochs  daqsystem1_name, daqsystem2_name, daqsystem_ch1,
                                 daqsystem_ch2, epochclocktype, minEmbeddedFileOverlap,
                                 errorOnFailure
randomPulses                     same, minus minEmbeddedFileOverlap
```

Each set is CLOSED and validated in code (`ischar`/`isnumeric` checks with explicit
defaults). `parameters` is therefore not an open bag — it is the union of four closed
sets.

---

## WHAT THE THREE CLASSES ACTUALLY ARE

**`syncrule` — a strategy for aligning two devices' clocks.** One job:
`apply(epochnode_a, epochnode_b)` → `(cost, mapping)`. Configured once when the rig is
set up. The document holds the strategy's identity and its knobs.

**`syncgraph` — NOT a persisted graph.** The runtime object builds a graph whose nodes
are (epoch, clock) timelines and whose edges are alignments, then finds shortest paths
so time can be converted between devices never directly aligned. That graph is
**computed and cached at runtime** (`buildgraphinfo`, `cached_graphinfo`,
`set_cached_graphinfo`) and never stored. What the DOCUMENT holds is the
**curated set of rules in force** (`syncgraph.m:850` writes them,
`:891` reads them back) plus the implementation identity. It is a session property by
construction — `session.m:830`, `ndi_session_obj.syncgraph.newdocument()`.

**`syncrule_mapping` — the computed answer, and it is PRIMARY DATA.**

```
commonTriggersOverlappingEpochs.m:153-167
   % 2. Look for existing syncrule_mapping in database
   ... if ~isempty(existing_docs)
          cost    = doc.document_properties.syncrule_mapping.cost;
          mapping = ndi.time.timemapping(doc.document_properties.syncrule_mapping.mapping);
          return;                                    % NEVER recomputes
```

The stored document short-circuits computation. Only past that early return does the
rule reach `epochnode_a.underlying_epochs.underlying`, `count_embedded_matches` and
`daqsystem_a.epochtable()` — i.e. **the RAW DEVICE FILES**. So this is *not* a
rebuildable cache in the `ensemble` sense (that one rebuilds from archived per-neuron
trains); it cannot be rebuilt from an archive at all. `syncgraph.ingest` recomputes the
graph but writes only `if match==0 % we don't have it already saved` (`:296`) — saved
mappings win.

`cost` is consumed, not an artifact: written `syncgraph.m:299`, read
`commonTriggersOverlappingEpochs.m:165`, `randomPulses.m:159`, `syncgraph.m:939`.

---

## THE MODEL

```
polynomial ⊂ data_type                                        ABSTRACT composite
   value {
      coefficients  matrix   HIGHEST ORDER FIRST (polyval convention) -- DOCUMENT THIS
      degree        integer  numel(coefficients) - 1
   }

clock_alignment ⊂ relation, polynomial                        base.id PRESERVED
   relation  ontology_term    "temporally aligned with"
   cost      double           the path-finding edge weight
   depends_on:
      from_reference                  -> relative_reference             REQUIRED
      to_reference                    -> relative_reference             REQUIRED
      clock_alignment_configuration_id -> clock_alignment_configuration REQUIRED
      clock_alignment_policy_id       -> clock_alignment_policy         REQUIRED

clock_alignment_configuration ⊂ base        (was syncrule)   base.id + base.name PRESERVED
   clock                          ontology_term  BOUND did_clocktype   <- epochclocktype
   minimum_matching_file_paths    integer   optional   <- number_fullpath_matches
   sync_file_name                 char      optional   <- syncfilename
   minimum_embedded_file_overlap  integer   optional   <- minEmbeddedFileOverlap
   depends_on:
      software_id            -> software                <- ndi_syncrule_class (R1)
      acquisition_channels_# -> acquisition_channels    EXACTLY 2

clock_alignment_policy ⊂ base               (was syncgraph)  base.id PRESERVED
   depends_on:
      session_id                       -> session                        REQUIRED
      software_id                      -> software           <- ndi_syncgraph_class (R1)
      clock_alignment_configuration_#  -> clock_alignment_configuration  OPTIONAL

acquisition_channels ⊂ base
   channels[] {
      type     ontology_term  BOUND {ai | ao | di | do}   (daqsystemstring.m:53-56)
      numbers  matrix         [27 28 45 88]
   }
   depends_on:
      acquisition_system_id -> acquisition_system          the DEVICENAME half
```

### The devicestring decomposition

```
'mydevice:ai27-28,45,88;di1-4'
   mydevice       device name    -> acquisition_system_id
   ;              separates channel-TYPE GROUPS
   ai / di        one type per group
   27-28,45,88    that group's numbers -> [27 28 45 88]

=> channels[0] = { type: ai, numbers: [27 28 45 88] }
   channels[1] = { type: di, numbers: [1 2 3 4] }
```

`type` is scalar **per entry** because a group is by definition one type; `numbers` is
the list. They are NOT equal-length parallel arrays. The flat alternative (type
repeated per number) is expressible and easier to filter, but repeats the type N times
and discards the grouping the source actually stores.

---

## FOUR CLAUDE PROPOSALS THE TEAM REJECTED, AND WHY EACH WAS RIGHT

**1. `stimulus_response`-style narrow naming → `linear_mapping` → `polynomial`.**
Claude proposed `time_mapping {slope, intercept}`, then `linear_mapping`, justified by
*"`acquisition_epoch.channels` already carries gain/offset."* The team asked where
`acquisition_epoch.channels` came from. **It is a V_eta INVENTION on a class this
migration retires** — the epoch plan already flags `axes`/`channels`/`storage` as
existing in no NDI template. A sweep confirms: **0 of 91 NDI templates declare a
gain/offset pair.** The precedent was a phantom.

The team then asked whether it should generalise to polynomial coefficients. It should,
and not on taste — **`ndi.time.timemapping` IS a polynomial by its own docstring**:

```
"the base class provides POLYNOMIAL mapping, although usually only linear mapping is used"
t_out = mapping(1)*t_in^N + mapping(2)*t_in^(N-1) + ... + mapping(N+1)
```

`{slope, intercept}` would have been **LOSSY** — a degree-2 mapping truncates. That is
the wrong-assumed-shape failure that produced the ~2,078 `distance_metadata`
quarantines, caught before the build this time. (`linear_mapping` was also
mathematically wrong: `y = mx + b` is affine, not linear.)

**COST, recorded:** `slope`/`intercept` stop being named fields, so *"which alignments
show clock drift"* becomes a query on `coefficients[0] != 1`. That is the query
regression the tuning re-audit warned about. Accepted because the alternative loses
data; `degree` is declared rather than derived to keep the common case findable.

**2. `frame` → `timeline` → back to `clock`.** The time plan chose `frame` over `clock`
because it *"generalises past clocks — for an organism it selects conception vs birth."*
Claude proposed `timeline` for legibility. The team objected that a timeline sounds like
a span with ordered events — which is what a session or epoch is, not a coordinate
system — and asked why not just `clock`, given the value_set is already
`did_clocktype`.

**Correct.** Nothing in V_eta has a non-clock frame today; the generalisation was
ANTICIPATORY, the same T12 error as (1). `clock` matches the existing 9-member
value_set and needs no new vocabulary. **This AMENDS the `frame` naming in
`V_eta_time_reference_model_plan.md`**, which is awaiting signature and therefore cheap
to amend.

**3. `channel_set` → `acquisition_channels`.** `_set` is a container word — the family
`array` was killed for (T13). The plural noun says what it holds without naming the box.

**4. `clock_alignment_rule` → `clock_alignment_configuration`.** The team said the name
meant nothing. It didn't: the document holds which two devices, which channels, which
method, and its thresholds — a procedure specification, not "a rule about alignment."

---

## THE POSITIONAL-EDGE RULE (generalised from this cluster)

Claude first proposed `acquisition_system_1` / `acquisition_system_2` with matching
`channel_1` / `channel_2`. The team asked what the positional issue was. It is
**TaskList #52 reintroduced**: the index carries meaning nothing declares.

```
name_#           an indexed FAMILY -- N members of the SAME role, interchangeable
                 derived_from_#, time_reference_#, metadata_reader_id_#

from_x / to_x    exactly two with DIFFERENT roles -- NAME the roles

x_1 / x_2        NEVER. The index is carrying undeclared meaning.
```

Applied here: `clock_alignment`'s endpoints have genuinely different roles (source and
target of the transform) → `from_reference` / `to_reference`. A configuration's two
devices are **interchangeable** — the rule matches forward or backward
(`filefind.m:133-135`) → `acquisition_channels_#`, a set of two. Making
`acquisition_channels` a **document** also solves the pairing, because device and
channels live together inside it, and removes the need for schema-level structure
sharing (there is none — see below).

---

## WHY `clock_alignment_policy` EXISTS (the T12 question, answered)

Claude twice suggested `syncgraph` might not earn existence — ~1 document per session,
and after repair its content is a software edge plus a rules list.

**It earns existence on MEMBERSHIP.** `syncgraph.addrule` and `removerule` both exist,
so the set of rules in force is NOT "every rule document in the session" — a rule can
exist in the database and not be in the graph. Folding the edges onto `session` would
reconstruct a different set; dropping them loses the fact entirely. Dropping the class
would additionally strand ~5,300 `syncgraph_id` edges.

The class was unnameable for as long as Claude tried to name the runtime object (a
graph). The document is not that. Named for what it holds — the set of alignment
configurations in force for a session — `clock_alignment_policy` follows.

---

## REPAIRS THIS CARRIES

```
1  syncgraph_id            RESTORED on the alignment -- NDI writes it, V_eta dropped it
2  epochid                 REMOVED -- invented, required, 100% empty, 5,316 documents
3  syncrule_id_#           NOT invented (Claude claimed it was). syncgraph.m:850 writes it
                           and syncgraph_schema.json:4 declares it. What V_eta got wrong is
                           narrower: it tightened NDI's "mustbenotempty": 0 into
                           mustBeNonEmpty: true. A rule-less graph is LEGAL in NDI.
4  parameters              GONE. Not a bag -- the union of four closed sets, so all three
                           surviving fields are DECLARED and queryable
5  errorOnFailure          DROPPED -- throw-or-return-quietly is runtime behaviour, not a
                           fact about the experiment (same call as graphical_mode)
6  epochnode_a/_b          DISSOLVED -- epoch_id, epoch_clock, epoch_session_id, t0_t1,
                           epochprobemap, objectclass all recoverable through the two
                           reference documents and the epoch they point at.
                           objectname is recoverable ONLY VIA epoch.instrument_id
                           (see the epoch plan's 2026-08-06 revision) -- it is
                           string-matched at EIGHT live sites:
                              syncgraph.m:404-408, :280, :283
                              commonTriggersOverlappingEpochs.m:157-158
                              filefind.m:133-134
```

Repairs 1 and 6 are also **#58**: they fix live NDI queries and stand whether or not
this model is adopted.

---

## A DETECTOR GAP FOUND HERE (not previously tracked)

```
silentLoss.m:222-224
   %REQUIREDDEPENDENCIES Names of depends_on entries declared mustBeNonEmpty
   %   anywhere in the class chain. Numbered edges (`derived_from_#`,
   %   `time_reference_#`) are template names, not concrete edges, so they are
   [EXCLUDED]
```

Correct in general — *"`derived_from_1` must be non-empty"* is meaningless as a blanket
rule — but it means **a REQUIRED NUMBERED EDGE CAN NEVER BE CHECKED**. That is how
`syncgraph.syncrule_id_#` (required in V_eta, 59 documents) stayed invisible. Distinct
from #37 (enforcement) and #54 (the vocabulary checker ignores `depends_on`).

## THERE IS NO STRUCTURE-SHARING MECHANISM

```
did_schema_meta.json $defs: document_class_header, superclass_reference,
                            dependency_object, file_record, directory_record,
                            ontology_object, field_definition
built classes using $ref / allOf / oneOf:  0 of 223
```

Those `$defs` describe the meta-schema's own grammar, not a facility for a class author
to reference a shared structure. A class's `fields` are inline and self-contained; the
only sharing mechanism is a **superclass**. This is why `acquisition_channels` is a
document rather than a mixin: two classes reference one shape by edge, and nothing
schema-level is needed.

---

## RENAME NOW, NOT IN R5

The R5 deferral (#27) rests on "cross-repo lockstep." **R5's own reverted attempt
disproved that and wrote it down:**

> the rename is **DID-only**, NOT a cross-repo lockstep — every NDI hit is a v1 WRITER
> and `+migrate/` has no V_eta-side reader of these strings, same as `element_epoch`.

The finding never propagated to the task title, which still says "cross-repo." The
remaining honest argument — *don't rename twice* — applies only while meaning is
unsettled. Here the meaning is settled in the same pass, so this is the cheapest moment
(the `element_epoch` precedent). `file_navigator` / `metadata_reader` still wait,
because their targets are unconfirmed, not because of a lockstep.

---

## OPEN

1. **`clock_alignment_configuration` vs `method_parameters`.** They are structurally
   identical: `base.name`, a software identity, typed canonical fields, a remainder.
   Claude leans keep-separate (their canonical fields share nothing), but the naming
   difficulty is the model asking a question and it should be answered deliberately.
2. **`polynomial` as a `data_type`.** Its siblings are quantities (`voltage`,
   `duration`); a polynomial is a function. The stretch is recorded, not resolved.
   Second user already in the schema: `tuning_curve.value.model_fit.coefficients`.
3. **The flat-vs-grouped channel form** (above) — grouped chosen, flat is defensible.
4. **`cost` on the leaf, not in `value`.** It is a property of the alignment, not of the
   polynomial. If a second `polynomial` user needs a goodness field, revisit whether
   this belongs in a shared place.
