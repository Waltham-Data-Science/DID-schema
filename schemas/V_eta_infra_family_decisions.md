# V_eta — the infra families: proposed dispositions (evidence, not assertion)

Read from the real NDI `origin/main` templates. Nothing built. This covers three
of the eight genuinely-undecided families on the status board.

**The test applied throughout:** does the class record *what happened in the
experiment* (archival — V_eta keeps it), or *how NDI was configured to read it on
one machine* (runtime — V_eta does not)? A migration target is an archival
record, not a serialisation of the tool that produced it.

## The templates, as they actually are

| class | depends_on | fields |
|---|---|---|
| `syncgraph` | — | `ndi_syncgraph_class` |
| `syncrule` | — | `ndi_syncrule_class`, `parameters` |
| `syncrule_mapping` | `syncgraph_id`, `syncrule_id` | `cost`, `mapping`, `epochnode_a`, `epochnode_b` |
| `filenavigator` | — | `ndi_filenavigator_class`, `fileparameters`, `epochprobemap_class`, `epochprobemap_fileparameters` |
| `filter` | — | `label`, `type`, `algorithm`, `parameters` |
| `projectvar` | `element_id` | `project`, `type`, `user`, `lab`, `description`, `data` |

## The "sync" family is TWO decisions, not one

The status board grouped these three together by name. The templates say they are
not alike.

**`syncgraph` and `syncrule` are runtime configuration.** Their entire content is
a MATLAB class name plus its parameters — `ndi_syncgraph_class`,
`ndi_syncrule_class` + `parameters`. They record *which code was configured to
align clocks*, not any alignment that resulted. This is the same `ndi_<x>_class`
shape the ⑥/⑦ governance sweep already flagged as needs-NDI.

→ **Proposed: not archival V_eta classes.** Where the provenance matters it is
the `software` + `method_parameters` shape already used for a calculator's
configuration — the identical problem, already solved once. Nothing new.

**`syncrule_mapping` is real measured data, and it is a time reference.**
`epochnode_a`, `epochnode_b`, `mapping`, `cost` is the *computed* relationship
between two epochs' clocks. That is not configuration; it is the answer.

And it is exactly the shape the time model just closed:

```
relative_reference   relative_to → the other epoch's acquisition_epoch
                     frame  = the clock the mapping is expressed in
                     start / end = the mapping
```

→ **Proposed: `syncrule_mapping` folds into `relative_reference`**, the class
decided in `V_eta_time_reference_model_plan.md`. `cost` is a fit quality —
either kept as a field on the reference or dropped as a solver artifact; that is
the one open sub-question here.

*This is why closing the target first pays.* The time model was settled on its
own evidence, and `syncrule_mapping` turns out to be a member of it. Deciding
this family in isolation would have invented a fourth representation of interval
time — after `acquisition_epoch.clocks`, `epochclocktimes` and the old
eight-class family.

## The "file navigation" family was mis-grouped

**`filter` is not navigation.** It lives at `data/filter.json` and carries
`label`, `type`, `algorithm`, `parameters` — a signal-processing filter
description. It belongs with software/method provenance, not with file paths.
Grouping it by a guess at its name was wrong; the status board's `FAMILIES` map
is corrected accordingly.

→ **Proposed: `filter` moves to the software/method family** — `algorithm` +
`parameters` is `software` + `method_parameters`.

**`filenavigator` is runtime, and machine-specific.** `ndi_filenavigator_class`,
`fileparameters`, `epochprobemap_class`, `epochprobemap_fileparameters` describe
how to locate epoch files *on the machine that made them*. Those paths do not
survive the dataset moving, which is what an archival migration is for.

→ **Proposed: not an archival V_eta class.**

**`directory` has no NDI template at all** — it is a post-v1 DID intermediate,
not a v1 source. Per the provenance rule (`V_eta_class_provenance.md`), only
`did_v1`-origin classes are sources.

→ **Proposed: out of scope as a source; disposition is a V_eta-side question
only.**

## `projectvar` — a genuine open call, and a small one

`project`, `type`, `user`, `lab`, `description`, `data`, attached to an
`element_id`. Free-form per-project user metadata on an element-subject. `data`
is an open bag.

Two honest options, and this one is a modelling call rather than an
evidence question:

1. **A `subject_statement`** with `variable` = the project-variable name — the
   same treatment `ontology_table_row` columns get. Makes it queryable, at the
   cost of forcing a `variable` binding onto free-form user text.
2. **Opaque passthrough** — preserve it exactly, model nothing, on the grounds
   that a free-form bag is not a measurement and forcing it into the statement
   tier fabricates structure the source never had.

No recommendation until someone says what these documents actually hold in
practice; the corpora will show it. **The one thing that must not happen is the
`ontology_table_row` failure repeated** — inventing a statement whose subject or
variable cannot be resolved, and emitting it hollow.

## What this closes

Of the eight undecided families, this proposes dispositions for **six classes**
across three families, and moves one class between families. The `sync` split
also removes a class from the undecided pile by absorbing it into an
already-decided model rather than inventing anything.

Nothing is built. `projectvar` remains genuinely open.
