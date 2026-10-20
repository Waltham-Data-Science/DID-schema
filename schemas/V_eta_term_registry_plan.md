# V_eta term registry: one term per meaning, across every NDI dataset

**Status: DECIDED BY JESS HALEY, 2026-10-20, AND BUILT. Not signed by the team.**
Tenet T19 (`V_eta_tenets.md`) is the rule; this document is the mechanism.

## The problem

Each import chose its own terms. The Haley import kept its 166 in a private
table (NDI-matlab `ndi.setup.conv.haley`'s `haleyTerm`), so the next dataset
could not see them: its mean could be STATO's *average value* or NCIT's
*Arithmetic Mean* while Haley's was a third choice, and a search for one would
miss the others. Nothing in DID-schema said which term to use for a variable,
a method, a unit or a statistic:

| what existed | what it covers | why it did not prevent drift |
|---|---|---|
| `binding_registry_meta.json` | 11 `subject_statement_bindings` (a variable's value must come from an ontology root) | constrains a value given its variable, never the variable, method, unit or statistic itself |
| NDIC.txt (ndi-ontology-matlab) | 26 NDI-minted terms | small and lab-specific |
| `haleyTerm` | the Haley terms | private to one converter |

## Decisions (Jess Haley, 2026-10-20)

1. **The term list lives in DID-schema**, beside the binding registry and its
   gates.
2. **An unregistered term is an error** in the writer, not a warning.
3. **The order to look for a term** (T19's first rule): a term already used in
   another NDI dataset (this registry), then a term in an existing ontology,
   and only when no term exists a new one minted in EMPTY. A term found at the
   second or third step is registered before it is used.

## What was built

**The registry** is authored in `schemas/V_eta_term_registry.json` and copied
by `tools/build_v_eta.py` into `schemas/V_eta/stable/term_registry_meta.json`,
where DID-matlab's schema cache loads it. Each entry:

| field | meaning |
|---|---|
| `name` | the term's name: the ontology's label (T19) |
| `node` | its CURIE, the prefix in the CURIE registry's spelling |
| `definition` | the ontology's definition; required for an EMPTY term |
| `status` | `decided` (has its node) or `staged` (registered by name; its node still to be found or minted) |
| `decided` | who decided it, and when |
| `first_used_in` | the dataset that first used it |

It starts with the Haley import's terms: the 169 reviewed on 2026-10-19 and
2026-10-20, then the 33 its census listed (NDI-matlab TestTermRegistry, which
runs the fixture import and collects every term the registry lacks): 7
existing-ontology terms decided earlier (four EDAM formats, PATO biological
sex, the OP50 and OP50-GFP strains a seeding dose names) and 26 lab labels
registered as `staged` (entity fields such as `version` and `email`, procedure
methods such as `pouring`, the encounter classification thresholds). The staged
terms are open item 3 below.

Two changes Jess decided later the same day: EMPTY:0000322 is renamed
`relative cell density` (nothing in the quantity is specific to bacteria), and
NCIT:C19827 Brightfield Microscopy is registered for the brightfield images
taken through a microscope (the E. coli plates); and NCIT:C210102 Sample Type
is registered as the variable that says what kind of thing a subject is (a
patch's `bacterial patch`). So 204 terms: 178 decided, 26 staged.

The 26 staged terms were then given nodes by T19's order (Jess, 2026-10-20; NDI
Haley decision #106), and none is staged now:
- **11 existing ontology terms**, each registered under the ontology's label:
  Diluent, Catalog Number, E-mail Address, Keyword, License, Abbreviation
  (`short name`) from NCIT; family name, given name, version number, author
  list from IAO; study design independent variable (`factors`) from OBI.
- **15 new EMPTY terms**, EMPTY:0000331-0000347 (Waltham-Data-Science/
  empty-ontology#22): the procedures seeding, pouring, incubation,
  refrigeration, ambient exposure, agar plug transfer and worm picking; the
  transfer setting `cleaning step`; the four encounter classification
  thresholds (under STATO cutoff); publication date and release date (under
  NCIT Date); and genetic strain type.
- **Two terms the census never saw**, because the fixture does not reach their
  code: `eyelash picking` (the multi-density transfer) and the transfer setting
  `droplet`, found by reading the import's spec and code, and minted the same
  way (EMPTY:0000338, 0000340).
- The procedures' parents are COB's process classes (OBI's moved there), so
  `cob` joins the CURIE registry.

So 206 terms, all decided; then NCIT:C96141 Petri Dish, an E. coli plate's sample type (NDI Haley decision #107), makes 207. The census is only as wide as the fixture: a term
written only on a path the fixture does not take is found by reading the code,
as these two were.

**The gate**, `tools/check_term_registry.py` (a step of `tools/gates.py`),
fails on: two entries for one node (prefix read by key, spelling or synonym)
or one name (ignoring case); a status that disagrees with its node; a prefix the
CURIE registry does not know or does not spell that way; an EMPTY or staged
term with no definition; and a built copy that differs from the source. It
checks nothing over the network.

**The writer check** (DID-matlab, `did2.build`): every ontology term it fills
in a vocabulary slot must be in the registry, or `did2:build:unregisteredTerm`.
`did2.schema.termRegistered` is the rule: a node is matched by its CURIE key
and must carry the registered name; a term with no node matches a staged entry;
a name registered with a node must be given with it.
`strictMode('TermRegistry')` is armed by default, and
`DID_ENFORCE_TERM_REGISTRY=0` disarms it. `did2.build.unregisteredTerms`
collects instead of failing, so one run can list every term an import still
needs.

**Not checked:**
- a schema with no registry (did-schema `main`);
- a field whose binding lists its own values (`entity.type`, a relation, a
  clock): that list already governs it;
- a statement's own value (`term.value`, a chemical's `substance`): that is
  what the data says, not the vocabulary it is said in;
- a model fit's coefficient names (`model_fit ... coefficients.variable`): a
  coefficient is named by its symbol in the model's equation (`a`, `b`), which
  tells the fit's coefficients apart; its node (STATO regression coefficient)
  still says what kind of coefficient it is;
- a migration: `did2.convert.v1_to_v2` and `foldGenericFiles` disarm the
  check, because a migrator transcribes the v1 source's own terms.

## Open

1. **A statement's term values.** A term value can be vocabulary (an encounter
   type: `exploit`, `sample`) or data (a species, a strain, a substance). The
   check leaves all of them out; whether vocabulary values should be checked,
   and how to tell them apart, is open.
2. **The migrators' terms.** A migrated dataset is an NDI dataset too, so by
   T19 its terms belong here. Registering them, then arming the check for
   migration, is a follow-up.
3. **The Haley import's lab labels.** DONE 2026-10-20: every staged term has a
   node (above). The mechanism stays for the next import: a term the census
   lists is registered as `staged`, then given a node by T19's order.
4. **Labels as of registration.** That a node's name is its ontology's label is
   checked when the term is decided, not on every run. An online re-check
   (OLS, OM's file) is not built.
