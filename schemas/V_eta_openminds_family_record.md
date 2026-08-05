# V_eta — board family #17, openMINDS. Walkthrough record.

**STATUS: DECIDED AND SIGNED OFF. Build deferred (TaskList #56).**

TEAM-SIGN-OFF: jess, 2026-08-05 -- strain is an entity with a repeatable global_identifier and a recursive background_strain_# self-edge; strain_id is an optional edge on term_assertion; species and strain stay sibling assertions.

> **How this line got here, stated plainly.** The standing rule (Operating Rule 4)
> is that Claude never writes a sign-off line; the team writes it. On 2026-08-05
> the team gave explicit instruction to add this one, so Claude transcribed it.
> That is a real weakening: the guarantee drops from *structurally impossible* to
> *depends on Claude reporting the conversation accurately*, which is precisely the
> kind of thing that does not survive a compaction. Replace this line with the
> team's own wording whenever convenient.
>
> **This is the SECOND such transcription in this session** — the first is in
> `V_eta_frequency_filter_model_plan.md`, whose note says Claude must not transcribe
> another "without the same explicit instruction, in the same session." Both
> conditions held. But two is a pattern, not an exception, and the next one should
> be typed by the team rather than requested from Claude.

**Provenance of this document.** It was reconstructed from the session transcript
after a compaction, because the walkthrough had been conducted entirely in chat and
chat does not survive compaction. 45 turns, 8 of them team turns. That is the
failure this document exists to stop repeating: a design walkthrough that leaves no
artifact is a walkthrough that has to be held twice.

---

## Setup — one writer, four classes

`+ndi/+database/+fun/openMINDSobj2ndi_document.m` is a single function switching
only on where the object attaches:

```matlab
dependency_type = ''         →  'openminds'            no dependency
dependency_type = 'subject'  →  'openminds_subject'    dep subject_id
dependency_type = 'element'  →  'openminds_element'    dep element_id
dependency_type = 'stimulus' →  'openminds_stimulus'   dep stimulus_element_id
```

Identical body in all four — `{openminds_type, matlab_type, openminds_id, fields}`.
They differ ONLY by which edge they carry: four classes encoding one thing × four
referents. That is the T4/T7 case — the attachment is a **role**, and roles are
edges, not subclasses. Three of the four already migrate 1→1 to `term_assertion`;
the unattached one has no migrator because it has no referent to assert about.

## The histogram — 119,166 real corpus documents (JH, Dab, B)

```
openminds* documents by class          openminds_type histogram
  10337  openminds_subject               3744  Species
    635  openminds_stimulus              2365  GeneticStrainType
    404  openminds_element               2365  Strain
      8  openminds                       1871  BiologicalSex
                                          635  StimulationApproach
                                          404  CellType
```

**Every type is a controlled-vocabulary term.** Not one `Person`, `Funding`,
`SoftwareVersion` or `Dataset` in 11,384 documents. So the three attached siblings
→ `term_assertion` is confirmed by data, not merely plausible.

---

# PART 1 — `openminds_import`: REMOVED. Landed.

Commit `8006d18`, 495 tests pass. The team gave the call in the walkthrough; the
reversal is recorded in `V_eta_tenet_audit.md`, which carried the original entry.

Evidence supporting removal:

- **Nothing emitted it.** Zero documents, no migrator, no importer, not even the
  round-trip CI test — the "emitter gap" the tenet audit already flagged.
- **A V_eta invention, not a v1 source.** Absent from the coverage ledger;
  provenance `V_eta`. Removing it strands no existing data.
- **Nothing referenced it** — only `index.json`, its own file, and the builder.
- Its content is `software` provenance anyway: `crosswalk_version` is *which
  version of a translation program ran*, which R1 already models as a `software`
  entity + `execution_environment`.

Recorded as a **REVERSAL**, not a silent deletion: the audit carried it as
**FINAL — PERSIST**, and that original decision persisted it *only on condition
that an emitter be scheduled*. None ever was.

Two consequences handled rather than left dangling:

- The binding registry said openMINDS `version` stays null because it is *"pinned
  by the import-provenance document (single source of truth)."* With the class gone
  that pointed at nothing — and it never carried a value. It now reads
  **UNRESOLVED**, deferred to whenever an import path exists.
- The test asserting the class existed is **inverted, not deleted** — it now
  asserts absence, so a return has to be deliberate. (The suite caught the removal.
  That was correct behaviour.)

**Carried forward, unresolved:** `software_id` currently lives on
`subject_interaction`, but an import is not a subject interaction — it is
document-level provenance, and `openminds_import` hung off `dataset`. So "just use
the software dep" does not fit as-is: either an import becomes a real statement, or
`software_id` needs a home above `subject_interaction`. `source_iri` also has no
home; `global_identifier` with `scheme='IRI'` is a candidate.

---

# PART 2 — the composite-vocabulary question. OPEN.

## What it is — 2,362 documents, not 8

```
WITH openminds_N edges (composite)      WITHOUT (leaf terms)
  2362  openminds_subject  Strain         3742  openminds_subject  Species
     3  openminds          Strain         2362  openminds_subject  GeneticStrainType
                                          1871  openminds_subject  BiologicalSex
                                           635  openminds_stimulus StimulationApproach
                                           404  openminds_element  CellType
```

A **leaf term** is self-contained (`Species = "E. coli", NCBITaxon:562`);
collapsing it to a `term_assertion` loses nothing. A **composite** is a vocabulary
object built from other vocabulary objects:

```
name: "N2"   description: "Genotype: C. elegans wild isolate."
ontologyIdentifier: "WBStrain:00000001"
geneticStrainType: [ndi://…]  species: [ndi://…]  backgroundStrain: null   <- a root
name: "DA609"   backgroundStrain: [ndi://…]     <- descends
```

`backgroundStrain` is an **array** and **recursive**.

**CORRECTED — this line previously read "the pedigree *can* go deeper, but most
people do not reference more than one level." Two of the four production writers
go deeper than that, so the assumption was wrong and would have shaped the schema
badly.** Read from the writers, which are the ground truth:

```matlab
% +ndi/+setup/+conv/+hunsberger/SubjectInformationCreator.m:70-107
strain  "ArcCreERT2 x eYFP"   EMPTY:00000288   transgenic
   backgroundStrain = [ArcCreERT2, eYFP]         <- TWO parents
        ArcCreERT2            EMPTY:00000284   transgenic
            backgroundStrain = SvEv              <- SECOND level
        eYFP                  EMPTY:00000287   transgenic
            backgroundStrain = SvEv              <- the SAME node again
                SvEv          NCIT:C37334      wildtype   (root)

% +ndi/+setup/+conv/+dabrowska/working.m:46
st_trans.backgroundStrain = [st_sd st_wi];        <- a second two-parent case
```

Two consequences the model must satisfy:

**It is a DAG, not a tree.** `SvEv` is reached by two distinct paths. The
repeatable `background_strain_# -> strain` edge handles this natively; a NESTED
background block would have DUPLICATED SvEv under both parents, and the two copies
could then disagree. This is a concrete instance of the inline-structure failure
already removed from `acquisition_epoch.clocks`, `epochclocktimes` and
`distance_metadata`.

**A real F1 cross, not a hypothetical.** `ArcCreERT2 x eYFP` is production data
today.

## The Strain object, as production code builds it

```matlab
openminds.core.research.Strain
    name                 'ArcCreERT2 x eYFP' | "129S/SvEv" | "SD"
    species              -> openminds.controlledterms.Species
    ontologyIdentifier   'NCIT:C37334' | "RRID:RGD_70508" | 'EMPTY:00000284'
    description          <- ndi.ontology.lookup(...) definition, NOT free text
    geneticStrainType    'wildtype' | 'transgenic' | "knockin" | 'wild type'
    backgroundStrain     -> Strain, or an ARRAY of Strain
```

**Three identifier regimes, and the 115 identifier-less strains are a LAB PRACTICE
difference, not a property of lab-made strains:**

```
NCIT:C37334          hunsberger  SvEv                    NCI Thesaurus
RRID:RGD_70508       dabrowska   SD                      Rat Genome Database
RRID:RGD_13508588    dabrowska   WI
EMPTY:00000284/7/8   hunsberger  ArcCreERT2, eYFP, cross MINTED via ndi.ontology.lookup
(none)               dabrowska   OTR-IRES-Cre, AVP-Cre, CRF-Cre
```

Hunsberger mints `EMPTY:` CURIEs for its lab-made strains; Dabrowska sets only
`name`. So `identifier` MUST be optional on the strain document — the schema
cannot require what the writer does not produce. `geneticStrainType` is also
unnormalised across writers (`'wildtype'` vs `'wild type'`), which is a T8 binding
job.

**The dedup case is visible in the code, not only in the counts.** `st_sd` and
`st_wi` are constructed INSIDE `getStrain`, so every invocation builds fresh Strain
objects — which is why there are 2,365 Strain documents for roughly ten distinct
strains.

**Why this is urgent, not theoretical.** `openminds_subject` migrates 1→1 to a
single `term_assertion`. The migrator reads `fields.preferredOntologyIdentifier`
and `fields.name` and **never looks at `depends_on` or `backgroundStrain`**. So for
2,362 composite Strain documents the background-strain link, the genetic-type link
and the description are **dropped today, silently, in a migration that passes every
gate.** Stated as what the code does — the census would show this as data simply
absent from the output, and that has not been measured.

## Measured evidence

```
subjects with openMINDS docs : 1871
  1 strain : 1380 subjects        pairing recoverable by elimination
  2 strains:  491 subjects        pairing AMBIGUOUS when flattened   (26%)

Strain documents            : 2365
  with ontologyIdentifier   : 2250   (WBStrain:…)
  with NO identifier at all :  115   AVP-Cre, OTR-IRES-Cre, CRF-Cre
                                     — all three have background + genetic type
Species  : 3744   NO edges -> leaf
CellType :  404   NO edges -> leaf   (BNST neuron subtypes — natural kinds)
```

One subject carried **seven** openMINDS docs: Species ×2 (duplicated),
GeneticStrainType {wildtype, transgenic}, Strain {PR811, N2}, BiologicalSex. The
PR811 strain's edges point at documents already attached to the same subject — so
**no fact is lost**, only **which goes with which**. Flattened, nothing says PR811
is the transgenic one derived from wildtype background N2; the reverse reading is
equally consistent and biologically wrong. The duplicated Species is itself a
fingerprint of the pairing — one per strain.

## What is settled, and why

**1. The pairing is genuinely lost when flattened.** One strain → recoverable by
elimination. Two strains → not. 491 subjects, 26%. Not an edge case.

**2. `directed_relation` CANNOT connect two `term_assertion`s.** Both endpoints are
declared `entity`; a `term_assertion` is a `subject_assertion`. It would *validate*
(`must_refer` is existence-only, not type-checked) while violating the declared
contract — the "conventional, not declared" failure T14 exists to stop.

**3. Widening `directed_relation` to statements is the wrong shape anyway.**
"PR811 derived_from N2" is a fact about strains in the world — true before this
worm existed, true after. Relating two of the worm's assertions says the derivation
happened in this animal. And with 491 two-strain subjects it would restate one
pedigree **491 times**: 491 chances to disagree, nothing to catch a divergence.
Same failure mode as `app` stamped into 16 classes, which R1 fixed by extracting
`software`.

**4. Cite-and-done cannot be the model.** It fails on the 115 unregistered lab
strains, and those are the *scientifically interesting* ones — a new transgenic
line is usually what the paper is about. A schema that can represent a strain only
when an external registry already describes it would silently drop precisely the
novel work. (Whether WormBase publishes the pedigree behind `WBStrain:…` is
**unknown** — `rest.wormbase.org` is not on this environment's egress allowlist.
Moot for the class decision, per this point.)

**5. The pedigree works as a self-edge — no new relation machinery needed.**

```
strain
  name / description / identifier      (WBStrain:… or EMPTY:…)
  depends_on: background_strain_# -> strain    (repeatable, recursive, arbitrary depth)
              species             -> …
              genetic_strain_type -> …
```

**6. Reusability is NOT sufficient for `entity` — the schema already proves it.**
`time_reference ⊂ base`, `frequency_filter ⊂ base`, `sampled_body`, `opaque_body`
are all referenced, deduplicable, non-entities. Two distinct axes:

- **referenceable** — own document, can be pointed at, deduplicated.
- **entity** — additionally has identity in the world: a name, and an identifier
  someone outside this database could resolve.

`sampled_body` is the clean counter-example: the body points **at** the statement,
has no name, and nobody creates "a data body" as a thing.

## The proposed rule — MADE vs FOUND

> **A term graduates to its own document when the thing it names was MADE, not FOUND.**

| | | |
|---|---|---|
| **found** | species, biological sex, developmental stage, anatomical location, phenotype | An external ontology enumerates them and publishes everything true about them. A CURIE is complete. **Never graduates.** |
| **made** | **strain**, **cell line**, **instrument/probe model**, **material formulation** | Constructed from other things; the construction record exists only in the lab that made it. A CURIE names it and has nowhere to put the parentage. **Graduates.** |
| **neither** | temperature, position, electrode offset voltage, spike cluster assignment, imaged region | Measured quantities, not kinds. Already have `data_type`s. Not candidates. |

**This is openMINDS's own namespace split, arrived at independently** — which is
the main reason to trust it:

```
openminds.controlledterms.*   Species, CellType, BiologicalSex,        -> leaf terms
                              GeneticStrainType, StimulationApproach
openminds.core.research.*     Strain (+ cell lines, tissue samples,    -> identity + lineage
                              engineered constructs when they appear)
```

Future graduates are typed **by the source**, not re-decided by us each time.

Team corroboration: lab-made cell lines. All 404 CellType docs in this corpus are
natural kinds (BNST neuron subtypes, 0 edges), but a CRISPR line is `core.research`
in openMINDS, not `controlledterms.CellType` — the rule predicts it without being
told.

Note `genetic strain type` is currently emitted as a **sibling assertion on the
subject** (~2,365 docs) when it is really a property of the strain. That is the
duplication test firing on live data.

## The `EMPTY:` counter, and what it changed

The team's counter: *"we have the EMPTY ontology precisely so that a unique
identifier can be made for a new strain or cell type."*

**Accepted — it kills the identifier argument.** `EMPTY:` is the project's own
namespace and can mint an identifier for an unpublished strain, so "no registry
knows it" does not by itself force a document. What survives is the **pedigree**: a
CURIE is a *name*, and a name has no fields. `EMPTY:avp-cre` says two documents
mean the same strain; it gives you nowhere to write that its background is
C57BL/6J.

## Where a graduate can come from — the answer to "at any time"

The team's remaining worry was that other terms could graduate at any time. They
can, and the reason is structural: **two of the four sources of a `variable` are
unbounded, and both take the name from data rather than from a decision.**

Bounded (someone chose these; they are in code):

```
$ grep -rn "jOntologyTerm('', *'" --include=*.m .        # +migrators_j
   4 anatomical location   1 temperature   1 spike cluster assignment
   1 probe model   1 position   1 imaged region   1 electrode offset voltage

build_v_eta.py   SUBJECT_STATEMENT_BINDINGS  (all subject_defining)
   species(NCBITaxon)  instrument type(OBI)  cell type(CL)
   material type(CHEBI)  developmental stage(UBERON)
```

Unbounded (the data names the variable):

```matlab
openminds_subject.m:70
    case 'species'; … case 'strain'; … case 'geneticstraintype'; …
    otherwise;  name = deCamel(typeSuffix(omType));     <- any openMINDS type ever

ontology_table_row.m:451
    node  = getCharField(row, 'ontology_name');
    label = getCharField(row, 'name');
    variable = struct('node', node, 'name', label);     <- a spreadsheet column header
```

`ontology_table_row` then routes by substring:

```matlab
if containsAny(hay, {'species', 'sex', 'strain', 'genotype', 'taxon'})
    body = makeTermAssertion(preBody, variable, valueTerm(row));
```

A lab imports a table with a column called `cell line` or `plasmid` and a
`term_assertion` appears carrying a variable nobody reviewed, bound to nothing,
matching no case.

**Applying MADE/FOUND to the bounded set yields zero further graduates.** Strain
arrived through the unbounded door — which is the point. So the two things needed
are different in kind:

1. **A rule for when a candidate appears** — MADE/FOUND, above. Decidable now.
2. **A gate that says a candidate appeared** — neither unbounded door has one.
   `deCamel` mints silently; the spreadsheet column mints silently. That is #32
   (nothing requires `variable` itself to resolve) and #54 (the vocabulary checker
   does not look here).

## A defect found while checking the above

`V_eta_openminds_crosswalk.json` claims the round-trip guarantee:

```
"Consumed by the round-trip CI test … asserts every openMINDS property has an
 explicit entry … so nothing is SILENTLY dropped."

types: DatasetVersion, Person, Organization, Funding, SoftwareVersion   (5)
tests/test_veta.py:614   # 1. completeness: the crosswalk covers the full
                         #    DatasetVersion surface, exactly.
```

The six openMINDS types that actually occur in the corpus — Species, Strain,
GeneticStrainType, BiologicalSex, StimulationApproach, CellType — are **none of
them**. The intersection with the crosswalk's five is empty. The guarantee is real
but covers zero real documents, which is why the dropped `backgroundStrain` never
tripped anything. Same shape as `silentLoss` reporting zeros while reading nothing:
an instrument whose denominator nobody stated. Recorded here, not fixed here.

## STILL OPEN — do NOT treat as decided

1. **`entity`, or plain referenced document under `base`?** Genuinely close.
   `base` matches the team's stated instinct ("an entity should be something
   concrete; the strain is a qualifier of the subject"), matches
   `time_reference`/`frequency_filter`, and the self-edge (5) removes the main
   reason to reach for `entity`. `entity` gives `global_identifier` natively
   (WBStrain / EMPTY both fit) and makes `directed_relation` available.
   **Claude argued three different positions on this in one conversation — weigh
   accordingly.**
2. **How does the subject point at the strain?** The loose end in the `base`
   option. A `term_assertion`'s value is an inline `{node,name}`, not an edge. So
   either the statement gains an edge, or `subject` gains a `strain_id` dep, or
   strain becomes an entity so `directed_relation` carries it. `entity` has no
   loose end here; `base` does. (If strain is an entity, "this worm is of strain
   PR811" arguably stops being a `term_assertion` and becomes `member_of` — a
   strain is a population.)
3. **Migration cost, unpriced** — ~2,362 documents change how they migrate.
4. **Re-take the corpus numbers.** The corpora were not on the container when this
   was written; the figures above are from the walkthrough scan, not re-derived.
5. **`openminds` (the unattached class, 8 docs)** — the family's nominal member
   never got its own disposition. 3 of the 8 are composite Strains; the other 5 are
   leaf terms with an empty `openminds` dep.
6. **The `otherwise -> deCamel` branch** — unbounded variable minting, no binding,
   no check. Related to #32/#54.
7. **`software_id` above `subject_interaction`** — carried forward from Part 1.

## Corrections made during this walkthrough (recorded so they do not come back)

- **"has a citable identifier" as the entity criterion — WRONG.** Species, cell
  type, material type, instrument type and developmental stage are all equally
  citable; the criterion would promote all five, plus antibodies, plasmids, viruses
  and equipment models when they arrive. It fails the cascade test.
- **`EMPTY:` on 404 CellType docs flagged as a possible unmet CL binding —
  RETRACTED.** `EMPTY:` is the project's own custom ontology, legitimate.
- **"those five are the bound vocabulary variables" — WRONG.** They are the
  `subject_defining` subset. The registry also has `binding_examples` (4,
  non-normative), `relation_bindings` (26) and `entity_field_bindings` (3, all on
  `dataset`).
- **"unattached `openminds` is a shared pool at scale" — WRONG.** 8 documents,
  0.07%.
- **`variable: background strain`** (distinguish by variable rather than a graph) —
  **fails** on the multi-background case: with two backgrounds each having their
  own genetic type, the ambiguity returns one level down.

---

# PART 3 — the drift problem, and referenceable data. OPEN.

Added after the team rejected the framing in Part 2. Nothing here is decided.

## The defect in the MADE/FOUND rule as first stated

The team's objection: *as we process more datasets, terms already stored as
`term_assertion`s in one dataset might qualify for their own document in a new one
— and we explicitly want to avoid the same kind of metadata being stored different
ways across datasets.*

**The rule as written in Part 2 is an INSTANCE-level test, and that causes exactly
that drift.** Dataset A's `cell type` is a BNST neuron subtype: found, stays a
`term_assertion`. Dataset B arrives with a CRISPR line: made, graduates to a
document. The same metadata is now stored two ways in one archive and every query
must know both shapes.

The walkthrough had already established why it cannot be instance-level —
*"it has to be answered once for the class, on the worst case"* — and the Part 2
table did not carry that through. That is the error.

Deciding once per variable on the worst case removes drift but costs prophecy:
every variable that could **conceivably** carry lineage would have to be promoted
now, before evidence. That is the T12 violation. **The way out is to stop making
graduation a change of representation.**

## Three options

**A — decide per variable now, on the worst case.** One shape forever. Costs
speculative promotion of cell type, material type, instrument type, probably
anatomical location. T12 violation, and it is guesswork.

**B — decide per variable on current evidence; re-decide when a counterexample
arrives.** Invariant becomes *one variable, one representation, at any point in
time*. No drift at any moment, no prophecy. Costs a **re-migration** of existing
documents on each graduation, plus an instrument to detect graduation.

**C — the value is invariant; the document is additive.** The statement ALWAYS
keeps its inline `{node, name}`. When a term also has structure, a separate
document carries it and the statement gains an OPTIONAL edge. Graduation stops
being a re-representation and becomes an annotation; nothing already written
changes shape.

## Why C is the current recommendation (an argument, not a decision)

- **No drift, by construction.** Every `cell type` assertion is identical in every
  dataset, forever. A lab-made line adds a document and an edge; existing
  assertions are untouched.
- **No prophecy.** Promote when evidence arrives. T12 satisfied.
- **No query regression.** `"species = C. elegans"` stays a one-hop inline match.
  Making the value an edge would put a hop in front of EVERY term query — the same
  category of regression the tuning re-audit rejected when it kept the empirical
  scalars typed rather than flattening them into a bag.
- **It is the shape already in use.** `time_reference` and `frequency_filter` are
  values pulled into referenced documents so they dedup and can grow. C is that,
  minus the removal of the inline value.

Cost, and it is real: the node/name is denormalized — in the statement and in the
document — so they can disagree. Checkable, not silent, but it needs the check.

## The schema change C implies

```
strain                     ONE new class -- the only new class
term_assertion
  depends_on:  strain_id -> strain     OPTIONAL, non_empty=False
  value: {node, name}                  UNCHANGED, inline, queryable
```

**CORRECTION — a generic `term_id` on the `term` mixin was proposed first and was
wrong twice over.** The team caught it: *"why would it be called a term_id? Would
that not argue that strain should be a child of term?"* Both halves of that are
right.

**(a) It breaks the edge-naming convention.** Every edge in the schema is named for
its TARGET class, not for the field it hangs off:

```
DENOMINATOR: 227 schema files, 97 dependency declarations, 45 distinct names
element_id 29   subject_id 6   probe_id 4   daqreader_id 3
timed_sequence_id 2   sorting_parameters_id 2   filter_id 1  (-> frequency_filter)
```

So the edge to a `strain` document is `strain_id`, exactly parallel to
`filter_id -> frequency_filter`.

**(b) It implied `strain ⊂ term`, which is false.** Carrying an identifier and a
name does not make a thing a term — all nine entities have that shape and none
subclasses `term`:

```
person ORCID + given_name/family_name   organization ROR + full_name/short_name
publication DOI + title                 software RRID + name/version
```

The distinction the name obscured: `term.value = {WBStrain:00000002, "PR811"}` is a
REFERENCE to PR811; the `strain` document is our record of PR811 ITSELF. Making
strain a child of term would say "PR811 is a kind of value," collapsing the name
into the thing named. The existing pattern is the proof: a statement is ABOUT a
subject, the subject has its own document, and the statement points at it with
`subject_id` rather than putting the subject in a term value.

**(c) The generic edge was also speculative.** It was a general mechanism built for
general targets that do not exist — today `strain` is the only thing it could ever
point at. That is precisely the T12 violation option C was supposed to avoid, built
while claiming to avoid it. When a `cell_line` appears it gets its own class and its
own `cell_line_id`, decided then, on evidence.

Worked example, the real seven-document subject (worm_17):

```
term_assertion  subject_id->worm_17  variable:{name:"strain"}
                value:{WBStrain:00000002, "PR811"}
                depends_on: strain_id -> str_pr811        <- the only addition

strain   base.id: str_pr811                 ONE document, shared by every PR811 worm
         name: "PR811"    identifier: WBStrain:00000002
         species:             {NCBITaxon:6239, "C. elegans"}   INLINE ontology_term
         genetic_strain_type: {…, "transgenic"}                INLINE ontology_term
         depends_on: background_strain_1 -> str_n2             a REAL edge
```

## Two structural findings that constrain the answer

**1. `term` has exactly three concrete forms and all are statements about a
subject.** Verified across the built set:

```
DENOMINATOR: 222 classes scanned
classes with data_type as ANY ancestor : 114   (38 abstract, 76 concrete)
of the 76 concrete: composed with a DIRECTION : 76
                    NO direction               :  0
```

Data types ARE real documents — 76 of them. But a data type becomes a document
only by being composed with a direction (T3, `leaf = direction x data_type`), with
zero exceptions. So no edge can point at "a term document": the only term
documents are `term_assertion` / `term_observation` / `term_manipulation`, and a
strain's pedigree is not a fact about any one animal.

**This rules the data_type tier out for strain on structural grounds.** A strain
has no direction. The tier options are exactly two — `⊂ base` (like
`frequency_filter`, `time_reference`) or `⊂ entity`. Open item 1 narrows from a
three-way to a two-way for a reason that is not a judgement call.

**2. Why terms are inline is not convenience — a bound term is ALREADY a
reference.** `NCBITaxon:6239` is a foreign key into a global registry; the
deduplication is done by NCBITaxon, for everyone, permanently. Minting a local
`species` document so 3,744 assertions can point at it would be building a local
copy of an external registry and owning the sync.

So linking directly to a data_type is not an upgrade over inline — for a term it is
a **downgrade**, replacing a global identifier with a local one. It breaks in
exactly one case: **local structure the CURIE cannot carry.** `EMPTY:avp-cre` names
the strain but has nowhere to record that its background is C57BL/6J. That is the
whole of strain's claim, and it is why strain is the only graduate.

For NUMERIC data types, lifting the value out is incoherent rather than merely
unhelpful: a free-floating `temperature` document is `22.5` with no claim attached.
The meaning comes from the direction. And there is no dedup to win — measurements
are unique.

## On "referenceable data" — two needs, and one is already built

**Citable data is solved.** Every statement leaf has its own `base.id`; every data
body is a SEPARATE document with its own id; `derived_from` chains already link
computed results to inputs.

```
sampled_body   CONCRETE  ⊂ data_body    dep: statement, filter_id
opaque_body    CONCRETE  ⊂ data_body    dep: statement
```

The body points AT the statement, so the citable unit is "this observation" rather
than "these bytes" — bytes without the claim they support are not citable science.

**Shared KINDS is the unsolved need**, and strain is its first instance. What such
a document is, is neither a statement (no direction) nor obviously an entity: a
thing with identity and lineage. That tier does not exist in V_eta yet.

## The fork this opens, undecided

```
A.  one class per kind     strain, cell_line, plasmid, viral_construct, probe_model
                           T12-friendly: mint when evidence arrives.
                           Cost: N classes accumulating over time.

B.  one general class      research_object { kind, name, identifier, lineage edges }
                           Cost: a discriminator field naming a class (the
                           ndi_<x>_class smell), and the fields genuinely differ
                           (a plasmid has a sequence; a strain has a background;
                           a probe model has a geometry).
```

Claude leans A — the fields differ substantively and T12 says mint on evidence.
An argument, not a decision.

**The `term_id` correction above settles the EDGE half of this fork even while the
class half stays open.** Whichever way A/B goes, the edge is named for its target:
`strain_id -> strain` today, `cell_line_id -> cell_line` if and when one appears.
There is no generic edge, because there is no generic target — and inventing one
was the speculative move option C exists to avoid.

## What C does NOT buy

| question | C's answer |
|---|---|
| **Inline value, or edge?** | Never varies. Value always inline; edge additive. **Drift eliminated structurally.** |
| **Whose property is this variable?** | Still answered **once, globally, per variable**; changing it later is a re-migration. |

Worked through on the real subject: `species` stays asserted on worm_17 (it is
`subject_defining`, and not every subject has a strain — a wild-caught animal, a
human, a cell culture), so the subject's species and the strain's species are
BOTH real and denormalized on purpose. The DUPLICATE species assertion collapses
to one — deduplicating identical assertions, not dropping a representation.

But `genetic strain type` is a property of PR811, not of worm_17; those subject-
level assertions are flattening artifacts and move to the strain document. That is
a **one-time global re-migration of ~2,365 assertions**, not a per-dataset choice.

## The two checks C requires

```
1. DENORMALIZATION.  For every statement carrying strain_id, assert
   statement.term.value == the referenced document's name/identifier.
   Report: "checked N of M term statements (N carry strain_id)."

2. DRIFT.  For every distinct `variable` in the corpus, assert it appears in
   exactly ONE representation.
   Report: "inspected V distinct variables across D datasets, S statements."
```

Check 2 answers the team's question without requiring anyone to predict which terms
graduate: it DETECTS graduation. Under C its expected output is trivially clean,
because the representation never varies — only whether an optional edge is present.

Both report their denominator first, unconditionally (Rule 5).

## Open in Part 3

1. **A vs B vs C** — no decision.
2. **If C: one class per kind, or one general class?**
3. **`strain ⊂ base` or `⊂ entity`** — narrowed to two by finding 1, still open.
4. **Field-level bindings.** An inline `strain.species` cannot use the
   `keyed_by: variable` binding — there is no `variable` on a strain document. It
   needs a FIELD-level binding to NCBITaxon, which is the `entity_field_bindings`
   mechanism (3 today, all on `dataset`). Lands in #32.
5. **The per-variable "whose property is this" table** — needs writing once,
   globally, for every variable in play.

---

# PART 4 — read from the openMINDS source itself

The openMINDS repositories were cloned to the container (`openMINDS_core` v4,
`openMINDS_controlledTerms` v3, `openMINDS_MATLAB` all versions) so the claims below
are read from the standard rather than recalled. **The clones are EPHEMERAL** —
re-clone from `github.com/openMetadataInitiative/` to re-check.

## THE DECISIVE FINDING — openMINDS already made this exact decision

```
$ for v in v1.0 v2.0 v3.0 v4.0 v5.0 latest; do find $v -iname "Strain.m"; done
v1.0     +openminds/+controlledterms/Strain.m
v2.0     +openminds/+controlledterms/Strain.m
v3.0     +openminds/+core/+research/Strain.m      <- PROMOTED
v4.0     +openminds/+core/+research/Strain.m
v5.0     +openminds/+core/+research/Strain.m
latest   +openminds/+core/+research/Strain.m
```

The v2.0 class:

```matlab
classdef Strain < openminds.abstract.ControlledTerm
    definition, description, identifier, name, ontologyIdentifier
```

Name + CURIE + alternate identifiers — **exactly the flat term V_eta stores today.**
The standard hit the same limitation and resolved it by promoting the class, and
that has held for three major versions. This is not an analogy; it is the same
decision, already made upstream.

## WHY the boundary is where it is — measured, not argued

```
DENOMINATOR: 113 controlled-term schemas in openMINDS_controlledTerms v3
  extending controlledTerm            : 112 of 113  (the 113th IS controlledTerm)
  carrying _linkedTypes/_embeddedTypes:   1 of 113  (termSuggestion, a meta-type)
```

The `controlledTerm` base schema in full:

```
required: name
name  definition  description  synonym[]
preferredOntologyIdentifier (IRI)   otherOntologyIdentifier[] (IRI)
preferredCrossReference     (IRI)   otherCrossReference[]     (IRI)
```

**A controlled term has NO EDGES. There is no slot for structure.** So the
controlledTerms / core.research split is not a taxonomy convention — it is
structural: a term cannot hold a graph, and an object can.

**This answers the team's "other terms could graduate at any time" worry with a
measured rate.** A controlled term cannot grow structure in place; graduating
requires MOVING it to another module, and openMINDS has done that exactly ONCE
across five major versions. The 112 others remain flat by construction.

Note our migrator reads 2 of the 8 controlled-term properties
(`preferredOntologyIdentifier`, `name`). `definition`, `description`, `synonym`,
`otherOntologyIdentifier`, `otherCrossReference` and `preferredCrossReference` are
dropped for every term type — 3,744 Species, 2,365 GeneticStrainType, 1,871
BiologicalSex, 635 StimulationApproach, 404 CellType. Whether they are POPULATED in
our data is unchecked; the read is 2-of-8 either way.

## The 23 `core.research` types, mapped to V_eta

```
activity  behavioralProtocol  configuration  customPropertySet  deviceUsage
experimentalActivity  numericalProperty  propertyValueList  protocol
protocolExecution  specimen  specimenSet  specimenState  strain  stringProperty
subject  subjectGroup  subjectGroupState  subjectState  tissueSample
tissueSampleCollection  tissueSampleCollectionState  tissueSampleState
```

| openMINDS | V_eta home |
|---|---|
| subject, specimen, tissueSample, tissueSampleCollection, specimenSet | `subject` (entity); `element.m` already promotes parts to subjects |
| subjectGroup | group subject + epoch-scoped `member_of` (the ensemble decision, T1) |
| subjectState, subjectGroupState, specimenState, tissueSampleState, tissueSampleCollectionState | **the statement spine** — a state is a time-indexed property bundle, which is what `subject_observation` + `time_reference` replaced |
| protocol, protocolExecution, behavioralProtocol, activity, experimentalActivity | `subject_interaction` + `method` + `interaction_purpose`; `software` / `execution_environment` (R1) |
| deviceUsage | `instrument_id` — a role, so an edge (T7) |
| configuration, numericalProperty, stringProperty, customPropertySet, propertyValueList | `method_parameters` + `conditions` (D10) |
| **strain** | **nothing — the open question** |

**`strain` is the only one of the 23 with no V_eta home, and the only one NDI
references** (36 of 36 `core.research` mentions). Promoting it opens no queue.

The other 22 are not "terms that might graduate" — they are already **subjects**,
**statements**, or **methods**. Strain is unique in being a first-class research
object that V_eta stores only as a term value.

## `specimen` / `subject` / `tissueSample`, and the polymorphic species slot

`specimen` is an ABSTRACT base (no `_type`); `subject` and `tissueSample` both
`_extends` it.

```
specimen        required: species
  species              -> controlledTerms/Species  OR  core/Strain     <-- !!
  biologicalSex        -> controlledTerms/BiologicalSex
  internalIdentifier   the label used inside the data files
  lookupLabel

subject         _extends specimen   required: studiedState
  isPartOf -> core/SubjectGroup[]      studiedState -> core/SubjectState[]

tissueSample    _extends specimen   required: origin, studiedState, type
  type      -> controlledTerms/TissueSampleType
  origin    -> controlledTerms/CellType | Organ | OrganismSubstance
  anatomicalLocation[]   laterality[] (MAXITEMS 2)
  isPartOf -> core/TissueSampleCollection[]   studiedState -> core/TissueSampleState[]
```

**openMINDS has NO separate strain property.** The instruction is explicit: *"Add
the species OR STRAIN (a sub-type of a genetic variant of species) of this
specimen."* Since `Strain` itself requires a `species`, the strain SUBSUMES the
species rather than sitting beside it:

```
subject --species--> Strain "PR811" --species--> Species "C. elegans"
                            \--backgroundStrain--> Strain "N2"
```

**`tissueSample` has NO lineage edge to the animal it came from** — `origin` is a
CellType/Organ/OrganismSubstance TERM and `isPartOf` points at a collection, not a
parent specimen. So a tissue sample is not a made-thing-with-pedigree. Strain
remains the only one.

## NDI FLATTENS the spec's nesting BEFORE our migrator sees it

`+ndi/+setup/+NDIMaker/subjectMaker.m:265-271`:

```matlab
species_docs = openMINDSobj2ndi_document(subjectInfo.species{i}, ..., 'subject', main_subject_doc_id);
strain_docs  = openMINDSobj2ndi_document(subjectInfo.strain{i},  ..., 'subject', main_subject_doc_id);
```

`SubjectInformationCreator.create` returns four PARALLEL outputs
(`[subjectIdentifier, strain, species, biologicalSex]`) and never assembles an
openMINDS `Subject` with the polymorphic slot. So `subject -> strain -> species`
becomes three SIBLING documents hanging off the subject.

**That is the origin of the ambiguity, one layer UPSTREAM of the migrator** — and
it explains how a strain's own species arrives as a subject-attached document.

## The full `Strain` schema — 13 properties; NDI sets 6

```
required: geneticStrainType, name, species

name                  string
species               -> controlledTerms/Species          REQUIRED
geneticStrainType     -> controlledTerms/GeneticStrainType REQUIRED
backgroundStrain      -> core/Strain    array, minItems 1, MAXITEMS 2
description           string
ontologyIdentifier    ARRAY of IRIs
digitalIdentifier     -> core/RRID
alternateIdentifier   array (MGI / RGD ids)
breedingType          -> controlledTerms/BreedingType
diseaseModel          -> controlledTerms/Disease | DiseaseModel
laboratoryCode        string, pattern ^[A-Z]([a-z]?)+$   (ILAR code)
phenotype             string
stockNumber           -> core/StockNumber (vendor)
synonym               array
```

### Four corrections this forces

1. **`backgroundStrain` is capped at 2**, not unbounded — *"If two strains
   contributed equally, state both."* DEPTH is unbounded (recursive link); BREADTH
   is 2. Hunsberger's `[ArcCreERT2, eYFP]` sits exactly at the cap. An earlier note
   here said "arbitrary depth, two parents"; depth is right, breadth is a spec
   constraint we can enforce.
2. **`geneticStrainType` is REQUIRED on the strain.** This settles the "whose
   property is it" question from the source side: openMINDS says the genetic type
   is a mandatory property OF THE STRAIN, not of the animal. Moving the ~2,365
   subject-level assertions onto the strain is what the source model already says.
3. **RRID belongs in `digitalIdentifier`, not `ontologyIdentifier`.** Dabrowska
   writes `'ontologyIdentifier', "RRID:RGD_70508"`. Per the ground-truth rule the
   WRITER wins for did_v1 truth, but it means our `identifier` slot receives two
   different kinds of thing.
4. **`ontologyIdentifier` is an ARRAY of IRIs**; NDI writes a scalar string.

### What NDI drops entirely

`alternateIdentifier`, `breedingType`, `diseaseModel`, `laboratoryCode`,
`phenotype`, `stockNumber`, `synonym`. **`diseaseModel` is the notable one** — a
strain being a model for a human disease is scientifically load-bearing and has
nowhere to go today.

## CORRECTION to Part 2's generalisation

Part 2 said a lab-made cell line would be `core.research` rather than
`controlledterms.CellType`, and used that to argue the MADE/FOUND rule generalises.
**The listing does not support it — there is no `cellLine` schema in
`core/research`.** The nearest type is `tissueSample`, and
`controlledTerms/cellCultureType` + `cellType` exist on the term side. So the
"openMINDS already draws this line" claim is narrower than presented: the
`Strain`-in-`core.research` vs `Species`/`CellType`/`BiologicalSex`/
`GeneticStrainType`-in-`controlledTerms` split is real and measured, but it does
not predict where a future cell line would land.

---

# PART 5 — the edge placement is CLOSED. `subject.strain_id` is rejected.

Team objection, and it is decisive: **not all subjects are biological.**

```
element.m:5-6   "signal or sorted unit -- is a `subject`. The element document
                 therefore becomes a `subject` with its id PRESERVED"
element.m:25    instrument_id -> subject

element_id is 29 of the 97 dependency declarations -- the most common edge in the
schema. Non-biological subjects are the MAJORITY of the population, not a corner.
```

A `subject.strain_id` field would be **structurally present and permanently empty
on every device subject** — the hollow-document shape `silentLoss` and `isFragment`
exist to catch, built in at the schema level.

## The general principle this restates

A fact that applies to SOME subjects is a **statement**. A fact that applies to ALL
of them is a **field**. That is why `species` and `biological sex` are
`term_assertion`s and why `subject` carries only `local_identifier` and
`description`. Strain follows the rule already in force:

```
term_assertion  variable:{name:"strain"}  value:{WBStrain:00000002,"PR811"}
                depends_on: strain_id -> str_pr811
```

A device subject simply has no strain assertion. Nothing empty, nothing to
validate against.

## Why V_eta CANNOT inherit openMINDS's placement

`specimen.species` works in openMINDS because **an openMINDS specimen is biological
by definition** — `specimen` is the abstract base of `subject` and `tissueSample`,
and `species` is REQUIRED on it. V_eta's `subject` is deliberately broader: it
absorbed elements, probes and sorted units so their ids could be preserved.

So the divergence recorded in Part 4 is not a preference. Their model is coherent
BECAUSE their subject is narrower than ours; adopting their placement would import
a required-biological assumption our subject tier cannot satisfy. The crosswalk
should record this as a structural divergence, not an omission.

## Status of the strain question after Part 5

```
SETTLED (evidence, not sign-off)
  strain needs its own deduplicated document
  the pedigree is a recursive self-edge, background_strain_# (0..2, DAG)
  the edge lives on the term_assertion as strain_id, NOT on subject
  species + strain stay SIBLING assertions (no polymorphic slot)
  genetic_strain_type moves onto the strain document (openMINDS requires it there)
  identifier must be OPTIONAL (Dabrowska writes none)

OPEN -- ONE ITEM
  strain ⊂ base   or   strain ⊂ entity
```

`entity` is abstract and adds exactly one optional field,
`global_identifier {scheme, value}`. Choosing `base` does not avoid that concept —
it re-declares it locally and gives up "find anything by external identifier" as a
uniform query. The four schemes in play (`WBStrain:`, `NCIT:`, `RRID:`, `EMPTY:`)
are the shape `{scheme, value}` exists for. Claude leans `entity`; the team's
stated instinct is that entities should be concrete things a lab owns, which favours
`base`. **This is a tier-definition call and it belongs to the team.**

---

# PART 6 — the model. `strain ⊂ entity`. Team call, 2026-08-05.

**The team chose `entity` over `base`.** That was the last open item in the strain
question. Everything below follows from it plus the evidence in Parts 2–5.

**SIGNED OFF 2026-08-05** — the line is at the top of this document, with a note
recording that Claude transcribed it on explicit instruction rather than the team
typing it. Read that note before trusting the signature.

## What `entity` gives, and why it settled the identifier problem

```
entity  (abstract) ⊂ base
  global_identifier   structure   mustBeScalar: FALSE  <- an ARRAY
    scheme  char
    value   char
  "Cross-reference identifier(s) for this entity (ORCID | ROR | DOI | PMID |
   PMCID | RRID | UDI | ...). Array -- e.g. a publication carries DOI+PMID+PMCID."
```

openMINDS spends THREE slots on strain identifiers — `ontologyIdentifier` (array
of IRIs), `digitalIdentifier` (-> RRID), `alternateIdentifier` (array, MGI/RGD).
A single repeatable `{scheme, value}` subsumes all three, and the four schemes
already in our data (`WBStrain`, `NCIT`, `RRID`, `EMPTY`) are exactly what it is
shaped for. Choosing `base` would have meant re-declaring this concept locally and
losing "find anything by external identifier" as one uniform query.

## The class

```
strain  ⊂ entity

  name                  char              REQUIRED
  species               ontology_term     REQUIRED   binding -> NCBITaxon
  genetic_strain_type   ontology_term     REQUIRED   binding -> GeneticStrainType
  description           char              optional
  phenotype             char              optional
  breeding_type         ontology_term     optional   binding -> BreedingType
  disease_model         ontology_term[]   optional   binding -> Disease | DiseaseModel
  laboratory_code       char              optional   ILAR, ^[A-Z]([a-z]?)+$
  stock_number          { vendor, code }  optional
  synonym               char[]            optional
  local_identifier      char              optional   (LOCAL_ID_OPT, per entity convention)

  inherited from entity:
  global_identifier     [{scheme, value}] optional
                        schemes: WBStrain | NCIT | RRID | MGI | RGD | EMPTY

  depends_on:
    background_strain_#  -> strain    0..2, recursive, forms a DAG
```

The three REQUIRED fields are required BY openMINDS, not by us. `global_identifier`
is optional because Dabrowska's Cre lines carry no identifier at all — the schema
must not demand what the writer does not produce.

`ontology_term` here is the FIELD TYPE (the `{node, name}` cell, 32 existing uses
across 227 schema files), NOT the `term` data_type class. Those are different
things and the distinction was confused earlier in this record.

## Why the inline value STAYS (and why `epoch` does the opposite)

The assertion keeps its inline `{node, name}` **and** gains the edge. That is not
the general rule — `V_eta_epoch_plan.md` decided the opposite for `epochid`, which
is dropped entirely in favour of its edge. Recorded here so neither is misread as a
precedent for the other:

| | strain | epoch |
|---|---|---|
| inline value a complete fact alone? | **yes** — a CURIE naming a real thing | **no** — a bare local string |
| referenced document always exists? | **no** — 115 strains have no identifier | **yes** — minted per distinct id |
| value is content, or a join key? | **content** — the statement is *about* it | **join key** |

**The drift test decides it.** Dropping strain's inline value would make
`variable: strain` resolve two ways depending on whether a pedigree happened to
exist — drift. Dropping `epochid` creates none, because every epoch-scoped document
gets its edge uniformly.

> **strain: the value IS the fact; the document is optional extra structure.**
> **epoch: the document IS the fact; the string was only ever a way to find it.**

## The edge

```
term_assertion   variable:{name:"strain"}
                 value:{WBStrain:00000002, "PR811"}   UNCHANGED, inline, queryable
                 depends_on: strain_id -> strain      OPTIONAL, non_empty=False
```

Named for its target, per the convention measured in Part 3 (97 dependency
declarations, 45 distinct names, all `<target>_id`). NOT a generic `term_id`, and
NOT on `subject` (Part 5: most subjects are devices).

## Worked example — the real Hunsberger F1 cross

```
term_assertion  subject_id->mouse_44  variable:{name:"strain"}
                value:{EMPTY:00000288, "ArcCreERT2 x eYFP"}
                depends_on: strain_id -> str_cross

strain  str_cross     name "ArcCreERT2 x eYFP"   genetic_strain_type transgenic
        global_identifier [{scheme:"EMPTY", value:"00000288"}]
        species {NCBITaxon:10090, "Mus musculus"}
        depends_on: background_strain_1 -> str_arc
                    background_strain_2 -> str_eyfp

strain  str_arc       name "ArcCreERT2"    [{EMPTY, 00000284}]  transgenic
        depends_on: background_strain_1 -> str_svev
strain  str_eyfp      name "eYFP"          [{EMPTY, 00000287}]  transgenic
        depends_on: background_strain_1 -> str_svev
strain  str_svev      name "129S/SvEv"     [{NCIT, C37334}]     wildtype   (root)
```

`str_svev` is referenced twice and stored once — the DAG that a nested background
block would have duplicated.

## Migration consequences

1. **~2,362 composite Strain documents** stop dropping their pedigree. The
   migrator must read `depends_on` / `backgroundStrain`, which it does not today.
2. **~2,365 `genetic strain type` assertions move** off the subject onto the
   strain document (openMINDS requires it there). One-time, global.
3. **Duplicate `species` assertions dedupe** to one per subject.
4. **Strain documents dedupe** — roughly ten distinct strains behind 2,365
   documents, because `getStrain` constructs fresh objects per call.
5. **`species` and `strain` remain SIBLING assertions.** We deliberately do NOT
   adopt openMINDS's polymorphic `specimen.species` slot (Parts 4 and 5).
6. The **openMINDS crosswalk** gains `Strain`, and should record the polymorphic-slot
   divergence as structural rather than as an omission.

## Follow-ups this opens (tracked, not silently dropped)

- **T8 bindings**: `species`, `genetic_strain_type`, `breeding_type`,
  `disease_model` all need registry entries. `geneticStrainType` is unnormalised
  across writers (`'wildtype'` vs `'wild type'`). Lands in #32.
- **`diseaseModel`** currently has nowhere to go and is dropped; the field above
  gives it one, but no writer populates it yet.
- **RRID-in-the-wrong-slot**: Dabrowska writes `'ontologyIdentifier', "RRID:..."`.
  The migrator should map by CURIE prefix, not by source field name.
- **The 8-property controlled-term read** (Part 4): our migrator takes 2 of 8, so
  `definition`, `synonym` and cross-references are dropped for EVERY term type.
  Separate from strain; recorded so it is not lost.
