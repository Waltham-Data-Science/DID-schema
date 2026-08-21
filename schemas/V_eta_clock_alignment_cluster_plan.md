# V_eta — the clock alignment cluster (was syncrule / syncgraph / syncrule_mapping)

**DECIDED with the team 2026-08-06; SIGNED OFF 2026-08-08 (both families — see the
two `TEAM-SIGN-OFF` lines near the bottom of this file); SCHEMA HALF BUILT 2026-08-09.**

**THIS HEADER SAID "Build deferred. NO `TEAM-SIGN-OFF` LINE" UNTIL 2026-08-09**
<!-- HISTORICAL-SIGNOFF-CLAIM: the quote above is history, not an assertion. --> — 474
lines above the two sign-off lines that had been sitting in this same file since
2026-08-08. Reading the header and stopping there is exactly how a signed decision got
reported back to the team as an open proposal, twice in one session. The board never
believed it: `status_board.py` derives from the sign-off lines themselves and had
counted this cluster as decided all along (Operating Rule 4 working as intended).

**WHAT IS BUILT AND WHAT IS NOT.** `polynomial`, `clock_alignment`,
`clock_alignment_configuration`, `clock_alignment_policy` and `acquisition_channels`
are minted. The MIGRATORS are not written, so `syncrule`, `syncgraph` and
`syncrule_mapping` remain as v1 source tombstones and must not be deleted until a
migrator provably consumes them. The gates recorded with the signatures are unchanged
except gate 3, which is now MET (see "Gates carried on these signatures").

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
RE-DERIVED 2026-08-13: 91 NDI templates on origin/main; 1,003 .m files. The did_v1 ground truth did NOT move -- 0 template diffs across the NDI main merge, still 91; main gained one .m file, so only the denominator shifted. RE-DERIVED AGAIN 2026-08-15: 91 NDI templates on origin/main; 1,005 .m files. NDI main moved to 928b1cd5 and two of its nine commits add test .m files (closeAndRemoveDir.m, TestRayoLabStims.m). The did_v1 ground truth is STILL unmoved -- 91 templates, 0 diffs; only the denominator shifted.
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

---

## RESOLVED 2026-08-08 — three items closed in the sign-off review

### 1. `acquisition_channels_#` is CORRECT. The rule is SYMMETRIC; its output is DIRECTED.

Raised as a possible contradiction with this document's own positional-edge rule:
`clock_alignment` uses `from_reference`/`to_reference` (distinct roles) while
`clock_alignment_configuration` uses `acquisition_channels_#` EXACTLY 2 (interchangeable
family) — and v1's source is `daqsystem1_name`/`daqsystem2_name`, the numbered form the rule
forbids. **The source settles it, and the plan was right.**

```matlab
+ndi/+time/+syncrule/commonTriggersOverlappingEpochs.m:110-140

   node_a_is_1 = strcmp(epochnode_a.objectname, p.daqsystem1_name);
   node_a_is_2 = strcmp(epochnode_a.objectname, p.daqsystem2_name);
   node_b_is_1 = strcmp(epochnode_b.objectname, p.daqsystem1_name);
   node_b_is_2 = strcmp(epochnode_b.objectname, p.daqsystem2_name);

   if ~((node_a_is_1 && node_b_is_2) || (node_a_is_2 && node_b_is_1))
       return; % Names do not match THE PAIR we are looking for
   end
   ...
   if node_a_is_1     % A is 1, B is 2
   else               % A is 2, B is 1
```

The rule accepts the pair **in either order** and then normalises which is 1 and which is 2.
Its own comment says *"the pair we are looking for"* — a pair, not an ordered pair. So the
`1`/`2` numbering in v1 is bookkeeping inside a struct, not a role assignment, and
`from_channels`/`to_channels` would assert a direction the rule explicitly normalises away.

**The output, however, IS directed**: `apply` returns `[cost, mapping]` only after fixing which
system is 1 and which is 2, so the polynomial converts one way. Hence:

```
clock_alignment_configuration    acquisition_channels_#   EXACTLY 2   an UNORDERED PAIR
clock_alignment                  from_reference / to_reference        a DIRECTED mapping
```

A rule is symmetric; its result is not. Both edge forms are correct and they differ for a
reason, not by oversight. **No change.**

### 2. `polynomial` as a `data_type` — RESOLVED, was open item 2

Open item 2 read: *"its siblings are quantities (`voltage`, `duration`); a polynomial is a
function. The stretch is recorded, not resolved."* **The premise is factually wrong.** Of the
**38 direct `data_type` subclasses**, several are not quantities at all:

```
image                 a raster
date                  an instant
chemical              a substance
formulation           a preparation
contrast_sensitivity  a fitted curve
```

`data_type` means *"the kind of thing a value is"*, not *"a dimensioned quantity"*. With the
second user already in the schema (`tuning_curve.value.model_fit.coefficients`), that is T12's
threshold met twice over. **`polynomial ⊂ data_type` is DECIDED, not a stretch.**

### 3. `degree` STAYS, and is CHECKED

It is exactly derivable (`numel(coefficients) - 1`), so by the rule that dropped
`ngrid.data_size` it should go — except **the query layer has no length predicate**:

```
did2 operators: exact_string, exact_string_anycase, contains_string, regexp, exact_number,
                lessthan/eq, greaterthan/eq, hasfield, hasmember,
                hasanysubfield_contains_string, hasanysubfield_exact_string,
                isa, depends_on, or                        -- NO length / size
```

So `degree > 1` ("which alignments are non-linear", which is the interesting question about a
clock mapping) is expressible **only if `degree` is stored**. The test is not "is it derivable
in code" but "is it derivable AT QUERY TIME" — the same test that kept `axis.n` and dropped
`ngrid.data_size`. So: **REQUIRED and CHECKED, `degree == numel(coefficients) - 1`**, making it
an index rather than a second source of truth.

### 4. Two items still to pin before the build (NOT blockers for the model)

- **`clock_alignment.relation`** is `ontology_term` but bound to WHAT. It cannot be OWL-Time:
  *"temporally aligned with"* is a mapping predicate, not an interval ordering. Needs an NDIC
  term — rides with **#67**.
- **`clock_alignment_configuration.clock`** is bound to `did_clocktype`, and the time-model
  walkthrough took that vocabulary from 9 terms to 4 with `clock` becoming an `ontology_term`.
  This class must use the same four. **#67 gates this cluster too**, which the plan did not say.

### 5. Placeholder ontology nodes are ALREADY the established practice

Recorded here because it came up as a general question. An `ontology_term` is `{node, name}`,
both `mustBeNonEmpty: false`, and the Brainstorm-J migrators already emit **34** terms with an
empty node and a human-readable name:

```
migrators_j/private/jOntologyTerm.m
   t = struct('node', char(node), 'name', char(name));

e.g. jOntologyTerm('', 'electrode offset voltage')      electrode_offset_voltage.m:81
     jOntologyTerm('', 'temperature')                   electrode_offset_voltage.m:91
     jOntologyTerm('', 'anatomical location')           treatment_drug.m:45
```

So a term can be staged as `{node: '', name: '<what it is>'}`, the migration can go green, and
the nodes can be minted afterwards. **The hazard to close alongside it:** an empty node is
indistinguishable from *"we looked and no term exists"* — so the backlog is invisible. The fix
is not a sentinel string but an instrument: a sweep that reports every emitted `ontology_term`
with an empty node, grouped by (class, field path, name), gated in CI on a count that must not
INCREASE — the same shape as the vocabulary sweep's *"flip to enforcing when the count reaches
zero."* Tracked as **#70**.

---

## SIGNED OFF 2026-08-08 — both families

Two families cite this one document, so both sign-off lines carry a `[family]` tag; an
untagged line would sign both at once, which is the hole `has_signoff` was built to close.

TEAM-SIGN-OFF [sync configuration]: jess@walthamdatascience.com / 2026-08-08 -- syncrule -> `clock_alignment_configuration` (parameters DECLARED not bagged, devices become `acquisition_channels_#` edges, EXACTLY 2 and UNORDERED); syncgraph -> `clock_alignment_policy`, earning its existence on membership; both preserve base.id, and syncrule_id_# is un-tightened back to NDI's optional.

TEAM-SIGN-OFF [sync mapping]: jess@walthamdatascience.com / 2026-08-08 -- syncrule_mapping -> `clock_alignment` (⊂ relation, polynomial), base.id PRESERVED; endpoints become from_reference / to_reference on relative_reference documents; syncgraph_id RESTORED and the invented required `epochid` (5,316 docs, 100% empty) REMOVED; `degree` kept and CHECKED.

### What the review changed, and what it confirmed

```
CONFIRMED  acquisition_channels_#  EXACTLY 2, UNORDERED -- the rule accepts the pair in
                                   either order (commonTriggersOverlappingEpochs.m:115) and
                                   normalises after; `from_channels`/`to_channels` would
                                   assert a direction the source erases
CONFIRMED  from_reference/to_reference on the ALIGNMENT -- apply() returns its mapping only
                                   after fixing which system is 1, so the result IS directed
RESOLVED   polynomial ⊂ data_type  open item 2 closed: its premise was false (image, date,
                                   chemical, formulation, contrast_sensitivity are among the
                                   38 subclasses and none is a quantity)
RESOLVED   degree                  STAYS, REQUIRED + CHECKED (== numel(coefficients) - 1).
                                   Derivable in code but NOT at query time -- did2 has no
                                   length predicate, so `degree > 1` is expressible only if
                                   stored. Same test that kept axis.n and dropped ngrid.data_size
REJECTED   acquisition_channels_A/_B   `x_1`/`x_2` wearing letters; for an unordered pair it
                                   creates TWO representations of one fact with no tie-break.
                                   Cardinality belongs in the DECLARATION -> #63
```

### Gates carried on these signatures, none waived by them

1. **#67 gates this cluster**, which the plan did not previously say.
   `clock_alignment_configuration.clock` is bound to `did_clocktype`, and the time-model
   walkthrough took that vocabulary from 9 terms to 4 with `clock` becoming an
   `ontology_term`. This class must use the same four.
2. **`clock_alignment.relation` needs a term.** *"Temporally aligned with"* is a mapping
   predicate, NOT an OWL-Time interval relation, so it cannot use `relative_reference`'s
   binding. Stage it as `{node: '', name: 'temporally aligned with'}` — already the practice
   at 34 migrator sites — and harvest it under **#70**.
3. **"EXACTLY 2" is prose until #63 lands.** ~~The schema cannot express or check
   cardinality on a `name_#` family today.~~ **MET 2026-08-09**: #63 landed, and
   `clock_alignment_configuration.acquisition_channels_#` is now declared
   `min_count: 2, max_count: 2`. The cardinality the rule actually has is in the schema
   and checkable, instead of being a sentence in a plan.
4. **#58 rides with this build**: `syncgraph_id` restored and `objectname` recoverable via
   `epoch.instrument_id`. Both fix LIVE NDI queries and stand whether or not this model ships.

---

# FINDING — `syncrule` DOES NOT PASS THROUGH FOR THE REASON `syncgraph` DOES.
# 2026-08-14. Recorded, NOT resolved: the second half is a team question.

Scoping the move of the clock-alignment fold into the batch phase (the change
`syncgraph.m` describes as *"the ONE line that changes"*), on the evidence of a
real migrated PRED-like session that came back with BOTH `syncgraph` and
`syncrule` still present as v1 tombstones and NO `clock_alignment_*` document of
either kind.

## 1. THE DEFERRED-FOLD SEAM IS NARROWER THAN IT READS

        [2026-08-17: 85 migrator .m file(s) -- hartley_calc.m landed. The
         sweep's CONCLUSION is unaffected; it writes no clock alignment.]
        DENOMINATOR: 84 migrator .m file(s) in +migrators_j, comment-only
                     lines excluded, Contents.m excluded
        jSessionDocId CALLED IN CODE by: 1   -- syncgraph
        jEpochDocId   CALLED IN CODE by: 4   -- daqmetadatareader_epochdata_ingested,
                                                daqreader_epochdata_ingested,
                                                daqreader_image_epochdata_ingested,
                                                stimulus_response_scalar
        distinct migrators gated on either seam: 5

Several other files MENTION the seams in comments and do not call them, so a
substring sweep overstates this set. Five migrators, two seams.

## 2. `syncrule` IS NOT ONE OF THEM, AND THAT IS THE FINDING

`syncrule.m` never calls `jSessionDocId`. Its guard is a different one entirely:

        syncrule.m:112-116
            channelsA = jAcquisitionChannels(preBody, name1, ch1);
            channelsB = jAcquisitionChannels(preBody, name2, ch2);
            if isempty(channelsA) || isempty(channelsB)
                bodies = {preBody};      % THE GUARD
                return;

and `jAcquisitionChannels` returns `[]` when the device name is empty --
*"no device => nothing to say; the caller must then NOT emit the edge"*.

**THE RULE IN THE SESSION IS `ndi.time.syncrule.filematch`, AND IT CARRIES NO
DEVICES AT ALL.** From the class itself:

        origin/main src/ndi/+ndi/+time/+syncrule/filematch.m:25
            parameters = struct('number_fullpath_matches', 2);

No `daqsystem1_name`, no `daqsystem_ch1` -- nothing for `jAcquisitionChannels`
to read. A filematch rule synchronises by MATCHING FILE PATHS, not by comparing
trigger channels, so `name1`/`name2` are empty and the guard fires correctly.

## 3. WHAT THIS MEANS FOR THE BATCH-PHASE MOVE

**It would fold `syncgraph` and leave `syncrule` exactly where it is.** The two
documents look like one deferred item in a migrated session -- both v1
tombstones, both from the sync family -- and they are two unrelated situations:

  * `syncgraph` -- a DEFERRED FOLD. The model exists, the code exists, and it is
    waiting on a session-document id that only a batch pass can supply.
  * `syncrule` (filematch) -- an UNMODELLED RULE TYPE. The signed
    clock-alignment model is built around a device/channel pair, and a filematch
    rule has neither. There is nothing deferred; there is nothing to defer TO.

## 4. THE TEAM QUESTION

What does a `filematch` syncrule become? It states a real fact -- *these two
epochs are the same epoch because N components of their full paths match* --
and the signed `clock_alignment_configuration` has no slot for it. Options, none
chosen here:

  * a `clock_alignment_configuration` whose `method` is the match rule and whose
    device/channel slots are absent (widens the class);
  * a separate configuration class for path-matched alignment;
  * a deliberate passthrough, recorded as such rather than falling out of a
    guard written for a different case.

**Do not resolve this by widening `jAcquisitionChannels`.** Its refusal is
correct: a filematch rule genuinely has no channels, and inventing empty ones
would be the invented-empty-edge pattern this repository has paid for six times.

## 5. HOW MANY REAL DOCUMENTS THIS REACHES IS UNMEASURED

No corpus figure is quoted here because none was taken. `filematch` is the rule
in the one PRED-like session inspected; whether it is the common case across the
six corpora is not known, and the standing rule applies -- absent from the
corpora we hold is not evidence of anything.

---

TEAM-SIGN-OFF [sync configuration amendment 1]: jess@walthamdatascience.com / 2026-08-18 -- a FILE-BASED syncrule (a `filematch` rule, and any rule that names NO device pair) becomes a `clock_alignment_configuration` with its device/channel slots ABSENT and its file criterion carried in the fields the schema already declares (`minimum_matching_file_paths` from `number_fullpath_matches`, plus `sync_file_name` where present) + the `software` entity + base.id PRESERVED. This is option 1 of "## 4. THE TEAM QUESTION" above (the `method`/criterion form, no channels), NOT a separate class and NOT a passthrough. It AMENDS "devices become `acquisition_channels_#` edges, EXACTLY 2 and UNORDERED" in the [sync configuration] sign-off (:493) to `acquisition_channels_#` cardinality {0, 2}: a file-based rule carries 0, a device-pair rule (commonTriggers/randomPulses/filefind) still carries exactly 2. `jAcquisitionChannels` is NOT widened -- its refusal stays correct, and the migrator only emits the channel-less configuration when the rule names no device pair AND carries a file criterion. The `syncgraph` -> `clock_alignment_policy` DEFERRED FOLD (section 3) is un-gated in the same build by a batch pass that supplies the session-document id.

    (Recorded by Claude at the signer's explicit instruction. The signer was shown the scoped proposal -- that a `filematch` rule's `apply()` returns an identity `timemapping` and so IS a real alignment rule, that the schema already carries `minimum_matching_file_paths`/`sync_file_name`, and that the ONLY blocker was the EXACTLY-2 channel cardinality -- alongside the three options this document's section 4 records, and answered "Build it that way, both folds together", selecting option 1 (the channel-less `clock_alignment_configuration`) and authorising the paired `syncgraph` batch fold. The DECISION and its selection among the recorded options are the signer's; the transcription is Claude's, and Operating Rule 4 forbids Claude writing such a line unprompted. Corpus state at signing: 3 syncrule documents across PRED + 20211116 -- 2 filematch (unconverted, this amendment's target) + 1 filefind (already converts via 2 named devices); measured from the corpus zips, unverified by a MATLAB run in the authoring container.)


RE-DERIVED 2026-08-21 (ndi_m_files, `check_prose_counts`): 91 NDI templates on origin/main; 1,012 .m files (`git ls-tree -r origin/main | grep -c '\.m$'` = 1012 at 5df51cf9; +7 since the 1,005 reading). The did_v1 ground truth is STILL unmoved -- 91 templates, 0 template diffs; only the denominator shifted.


RE-DERIVED 2026-08-21 (ndi_m_files, sibling drift): NDI `origin/main` advanced to `1c0fe1283` (PR #882, parallel-workers), so `git ls-tree -r origin/main | grep -c '\.m$'` = **1013** (was 1012). The did_v1 ground truth is UNMOVED -- 91 templates, 0 template diffs; only the denominator shifted. Re-derive, do not quote.
