#!/usr/bin/env python3
"""Generate schemas/V_eta_STATUS.md -- the single generated record of V_eta state.

WHY THIS EXISTS
---------------
V_eta state lives in 27 plan documents, a 400-line CLAUDE.md and a 52-item task
list, and no two agree. Prose cannot be checked, so it rots and is then cited:
"no session document exists anywhere", "all 0-usage, safe to delete",
"dissolved (rename/decompose)" -- each was a written claim that was wrong and
that nothing could catch.

This file replaces PROSE STATE with DERIVED STATE. The plan documents keep the
rationale (why a model was chosen -- what prose is genuinely good for); this
board owns the answer to "how much is left, and what exactly".

THE ONE PIECE OF JUDGEMENT, MADE EXPLICIT
-----------------------------------------
`FAMILIES` below groups the still-open classes into decision units. That mapping
is a human call and cannot be derived, so it is written here in the open rather
than implied across a dozen documents. It is CHECKED: every in_progress class
must belong to exactly one family, and the generator FAILS if a class appears
that no family claims. A new open class can therefore never be silently dropped
from the count -- the failure this project has hit four separate times.

`in_progress` IS A DECLARATION, NOT A MEASUREMENT -- AND THAT IS THE OTHER HALF
------------------------------------------------------------------------------
Every one of the open classes is `in_progress` because a HUMAN WROTE ITS NAME in
a literal collection in `tools/build_v_eta.py`. Measured 2026-08-10, and the
denominator first:

    31 classes carry `disposition: in_progress` in the built index.json
       27 are keys of `_DECIDED_PENDING`   (a literal dict + two literal loops)
        4 are members of `_IN_PROGRESS`    (a literal set; 2 more of its 6
                                            members are deleted classes)
        0 are derived from any evidence about the work

`_disposition()` returns `in_progress` on membership alone. A class therefore
leaves the list only when a person deletes its line -- never because a migrator
landed, a test passed or a corpus went green. The count sat at 31 all day while
seven families were built, which is the SAME ONE-DIRECTIONAL BIAS this file
already records twice (the stale sign-off headers; the ledger's "dissolved
(rename/decompose)" labels): the artifact always claims LESS progress than the
record holds. It never produces a wrong build. It just makes the board unable to
answer the only question anyone asks of it.

The lines cannot simply be deleted, and the reason is a real one. For a v1
SOURCE class, flipping `in_progress -> retire` asserts that NO DOCUMENT of that
class survives migration -- the phase-8 criterion, which CLAUDE.md requires
CORPUS EVIDENCE for and which has already caught one over-eager deletion. So the
membership stays a team disposition (operating rule 4, and nothing here edits
it), and the board instead DERIVES, per open class, the two facts the
declaration cannot carry:

    (a) decided, nothing built        no migrator consumes it, no migrator MINTS
                                      it, no decided target schema exists
    (b) built, awaiting corpus proof  a migrator consumes it, MINTS it, and/or
                                      its decided target is built, but no census
                                      has shown 0 surviving documents
    (c) corpus-proven consumed        the last census read this class and found
                                      no document returned unchanged
    (?) UNMEASURED                    the evidence for this class was never
                                      taken -- printed as its own state, because
                                      absence of evidence is not evidence
                                      (operating rule 3)

WHAT (c) IS AND IS NOT
----------------------
(c) is EVIDENCE, never a disposition. `unconverted_by_class` counts documents a
migrator handed straight back; 0 of them is a fact about the corpora that were
read. It is NOT authority to retire a class, for two reasons that are printed
next to the number every time:

  * THE CORPORA ARE A SAMPLE OF DATASETS, NOT THE UNIVERSE (CLAUDE.md's standing
    caveat). A class absent from the six we run may be well represented in a
    dataset still waiting to migrate, which is what this migration is FOR.
  * THE REPORTS CARRY NO PER-CLASS SOURCE DENOMINATOR. `summary.by_class` counts
    OUTPUT class names, so a class that was fully consumed and a class that had
    no documents at all both come out at zero. "0 survived" and "0 existed" are
    indistinguishable from the report alone.

Usage:  python3 tools/status_board.py [--check]
                                      [--did /path/to/DID-matlab]
                                      [--ndi /path/to/NDI-matlab]
                                      [--census DIR ...]
        --check exits non-zero if the committed board is out of date.
"""

import argparse
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(REPO, "schemas", "V_eta", "index.json")
LEDGER = os.path.join(REPO, "schemas", "V_eta_coverage_ledger.json")
OUT = os.path.join(REPO, "schemas", "V_eta_STATUS.md")
# The machine-readable twin of the board, for the schema viewer.
#
# WHY IT EXISTS. Until 2026-08-09 the decisions lived ONLY in the FAMILIES table
# below and in the sign-off lines of the plan documents, so nothing downstream
# could see them. The viewer rendered the coverage ledger, where a settled class
# shows as `in_progress` with no hint that its model is decided, signed, and
# merely awaiting a build -- which reads as UNDECIDED. That is the same
# inversion this board already names: a record that reports settled work as
# open is the mirror of one that reports open work as settled, and both make
# the remaining-work count useless. The clock alignment cluster sat unbuilt for
# a day for exactly this reason, because two pieces of prose called a signed
# decision a proposal.
#
# Generated, never hand-edited, and stale-checked in CI like the other four.
DECISIONS_OUT = os.path.join(REPO, "schemas", "V_eta_decisions.json")

# Decision families for the still-open (in_progress) classes.
#   name -> (members, plan-or-None, one-line call, status)
#
# STATUS IS THREE-VALUED, and the distinction is the point:
#
#   "team"     DECIDED BY THE TEAM in a walkthrough. Only RENDERS as decided if
#              the cited plan document carries a TEAM-SIGN-OFF line (see SIGNOFF
#              below); without one it renders as "awaiting signature" -- Claude
#              cannot promote its own work to a decision.
#   "proposed" WRITTEN UP BY CLAUDE ALONE, nobody has checked the reasoning.
#              NOT a decision and must never be counted as one.
#   "open"     nobody has proposed anything yet.
#
# "team without a signature" and "Claude wrote this alone" were one bucket until
# the team pointed out they are different states: one needs a signature, the
# other needs someone to check the reasoning. Rendered separately now.
#
# An earlier version had only two states, so attaching a document to a family
# silently promoted it to "decided" -- and five families Claude wrote up alone
# were reported to the team as settled. A status board that launders a proposal
# into a decision is worse than no board.
FAMILIES = [
    # ADDED 2026-08-10, and the board is what demanded it. `generic_file` and
    # `valid_interval` were the last two did_v1 classes that stranded COMPLETELY
    # -- no V_eta schema AND no migrator, so a dataset carrying them lost them.
    # Both now have a tombstone restated from the WRITER, so the documents
    # survive under their own class via the identity passthrough. That closes the
    # STRANDING and closes nothing else: where each one belongs in V_eta is
    # undecided, and nobody has proposed a model.
    #
    # Status "open", NOT "proposed": a tombstone is preservation, not a proposal.
    # Marking it "proposed" would launder "we stopped losing these" into "we know
    # what they become", which is the exact laundering the three-valued status
    # exists to prevent.
    #
    # The two questions, both for the team:
    #   generic_file    the intended fold is opaque_body + a statement. opaque_body
    #                   is DRAFT and has NO content_hash, so folding today drops the
    #                   MD5 checksum -- the one field whose whole purpose is not
    #                   being lost. And no class yet says "this subject has this
    #                   file": generic_file's edge points at a SUBJECT,
    #                   opaque_body's at a STATEMENT.
    #   valid_interval  which tier? It is a curation judgement ABOUT a recording --
    #                   neither an observation of the subject nor a manipulation of
    #                   it. Note it has a SECOND production consumer nobody had
    #                   recorded: +app/+stimulus/tuning_response.m:253-256 uses it
    #                   to choose which stretch of signal to analyse, so losing it
    #                   would silently change tuning results, not just drop an
    #                   annotation.
    # A THIRD MEMBER, 2026-08-11, and this board is again what demanded it.
    # `imageCollection` was tombstoned by team decision on the same reasoning,
    # and the moment it gained a schema its ledger disposition became `retire`,
    # which put it in `unplanned_retire` -- retire, no migrator, no plan -- and
    # this generator refused to go green until a family claimed it. That is the
    # check working: a tombstone stops the stranding and leaves the modelling
    # question open, and an open question needs an owner.
    #
    # SPELLED `imageCollection`, in NDI's own camelCase, and NOT `image_collection`.
    # The two siblings are snake in NDI already, so this is the first member whose
    # spelling could go wrong -- and it would go wrong silently, because
    # `unclaimed` is a set difference (`open_work - claimed`): a member nobody can
    # match simply fails to claim anything and reappears in the ERROR list, while
    # the misspelling itself only shows up in `stale`, which is not fatal. The
    # name here must be the ledger's `v1_class`, which is NDI's spelling.
    #
    #   imageCollection  the WEAKEST-EVIDENCED of the three. `generic_file` and
    #                    `valid_interval` each have live production writers whose
    #                    behaviour arbitrates their template; this class has NONE
    #                    -- 0 of 1002 .m files on NDI origin/main, all three
    #                    spellings -- so its tombstone is the template alone and
    #                    there is nothing to check the template against. Nothing
    #                    NDI-side has ever written, read or named one; the only
    #                    thing pointing at the class is `image.json`'s
    #                    `imageCollection_id` dependency. Whether it becomes an
    #                    opaque_body attachment, a group of image_observations, or
    #                    is retired outright is UNDECIDED, and deciding it from a
    #                    template with no documents is the wrong-assumed-shape
    #                    failure that produced the ~2,078 distance_metadata
    #                    quarantines. It needs a real document first.
    ("stranded sources", ["generic_file", "valid_interval", "imageCollection"],
     None,
     "tombstoned so they stop stranding; tier and fold UNDECIDED",
     "open"),

    # FOUR MEMBERS LEFT THIS FAMILY 2026-08-11 (#65 increment 3a):
    # `epoch_relative_reference`, `event_bounded_reference`,
    # `event_relative_reference` and `utc_reference` are DELETED from the built
    # set, so the family may no longer claim them -- this generator fails on a
    # family citing an absent class, which is how the omission would have been
    # caught anyway. The signed decision is unchanged (it is still 8 classes
    # collapsing to 2); what changed is that four of them are now executed
    # rather than pending, on static evidence: no NDI template declares them
    # (0 of 91, normalised), nothing mints them under any of the three idioms
    # (0 sites across 187 +did2/+convert and 17 +ndi/+migrate files), no V_eta
    # schema references them, and no v1-source row exists in the ledger. See
    # `_DELETE_NO_V1_PROVENANCE` in tools/build_v_eta.py for the full evidence
    # block, including why they are NOT in `_DELETE_PHASE8`.
    #
    # THE OTHER THREE CONCRETE MEMBERS STAY AND MUST STAY: they are minted
    # today (session_relative 22 sites, session_bounded 1, epoch_bounded 1) as
    # a deliberate pass-1 handle. The root `time_reference` stays too.
    ("time_reference", [
        "time_reference", "session_bounded_reference", "session_relative_reference",
        "epoch_bounded_reference"],
     "V_eta_time_reference_model_plan.md",
     "8 classes collapse to absolute_reference + relative_reference "
     "(4 of the 8 executed 2026-08-11: epoch_relative_reference, "
     "event_bounded_reference, event_relative_reference, utc_reference deleted "
     "-- no template, no emitter, no reference; the other 4 await their emitters)",
     "team"),

    # control_designation MOVED here 2026-08-05: it is a V_eta TARGET minted from
    # control_stimulus_ids, points at timed_sequence, and the stimulus plan already
    # covers it at line 118 ("control_stimulus_ids -> control_designation --
    # RESOLVED"). It was never a "misc singleton".
    ("stimulus", ["stimulus_presentation", "control_designation"],
     "V_eta_stimulus_model_plan.md",
     "timed_sequence data_type + timed_sequence_manipulation leaf; control_designation resolved here",
     "team"),

    ("ensemble", ["ensemble"],
     "V_eta_ensemble_plan.md",
     "group subject + epoch-scoped member_of edges + rebuildable cache",
     "team"),

    # `imageStack_parameters` joined this family 2026-08-09, when image_stack and
    # image_stack_parameters came back OUT of _DELETE_PHASE8 so the guarded
    # passthrough has a schema to validate against. It is a `retire` row with no
    # migrator of its OWN -- it is a SUPERCLASS, consumed as a block by
    # image_stack.m -- so the board correctly flagged it as work nobody was
    # tracking the moment it reappeared. It is tracked here, with the raster
    # model it belongs to, rather than special-cased out of the count.
    ("image / ngrid", ["ngrid", "imageStack_parameters"],
     "V_eta_image_model_plan.md",
     "ngrid phases into sampled_body; image is a standalone data_type; the two "
     "image_stack tombstones are held until the subject is recoverable",
     "team"),

    # DECIDED with the team 2026-08-05 ("I agree with B"); SIGNED 2026-08-08.
    # epochid turned out NOT to be a disposal question: it is the JOIN MECHANISM
    # for the epoch-scoped half of the database -- 15 NDI classes carry the mixin
    # and 11+ live sites match epochid.epochid by exact_string. Third time this
    # session a depends_on sweep missed string-match references.
    # `epochfiles_ingested` is the v1 SOURCE tombstone that `ingestion_manifest`
    # replaces. It is claimed here rather than deleted: the rename removed the
    # schema file outright and 2,484 corpus-B documents then had no class to
    # validate against. It leaves when #60's migrator consumes it.
    # `ingestion_manifest` was ALSO listed here and has been pruned (2026-08-10).
    # The family list enumerates OPEN classes; `ingestion_manifest` is the settled
    # TARGET (`disposition: persist` in index.json), so listing it made the board
    # report its own resolved output as outstanding work -- and the board's
    # "families naming classes that are no longer open" section had been saying so.
    # The three that remain are all `in_progress`.
    ("epoch", ["acquisition_epoch", "epochid", "epochfiles_ingested"],
     "V_eta_epoch_plan.md",
     "MINT `epoch` ENTITY (+ OPTIONAL `instrument_id`, 2026-08-06); element_epoch "
     "dissolves; epochid DROPPED; probemap -> edges (B)",
     "team"),

    # Split by the templates, not by the name prefix: three are a MATLAB class
    # name (configuration), three carry real epoch data or bytes, and one is not
    # on origin/main at all.
    # DECIDED with the team 2026-08-05; SIGNED 2026-08-08. The earlier "not
    # archival" proposal was WRONG and is reversed in place: daqsystem.base.name
    # is a join key referenced BY NAME (epochprobemap devicestring, syncrule
    # parameters), which a depends_on check cannot see.
    ("daq configuration", ["daqsystem", "daqreader", "daqmetadatareader"],
     "V_eta_daq_family_decisions.md",
     "acquisition_system + `acquisition_metadata_reader` keep ids; class names fold to "
     "software entities",
     "team"),

    # WALKTHROUGH 2026-08-06 -> V_eta_ingested_payload_findings.md. Still "proposed":
    # the FINDINGS are facts but the team has not adopted the model.
    # An earlier one-liner said "no new class" -- that was WRONG. sampled_body and
    # opaque_body both declare depends_on: statement, and a per-epoch metadata blob is
    # not an observation of any subject, so it needs a carrier (`metadata_file`).
    # Biggest finding: daqreader_epochdata_ingested carries THE RECORDING ITSELF as
    # files attached under runtime-computed names (mfdaq.m:829,916,955), while BOTH the
    # NDI template and V_eta declare an EMPTY file_list -- a migrator reading the
    # declaration drops the only copy. Also kills R5's "<device>_epoch_cache" name.
    ("daq ingested payloads", [
        "daqreader_epochdata_ingested",
        "daqmetadatareader_epochdata_ingested",
        "daqreader_image_epochdata_ingested"],
     "V_eta_ingested_payload_findings.md",
     "reader one DECOMPOSES (per-clock relative_references + sampled_body) and retires; "
     "metadata one -> `acquisition_metadata_file`; image one folds into the image model",
     "team"),

    # `dataseries_channel_map` -- FAMILY CLOSED 2026-08-09. Decided 2026-08-05
    # (DELETE: a V_epsilon invention, never a did_v1 source, zero users) and BUILT on
    # 2026-08-09 when the team asked "does it have any V1 provenance? If no, delete
    # it" and the answer came back no on every check. The class is gone from the
    # built set (`_DELETE_NO_V1_PROVENANCE` in build_v_eta.py, which records the
    # evidence), so the family has nothing left to track.
    #
    # IT WAS FOUND BY A DISAGREEMENT, WHICH IS THE POINT. This board said DELETE,
    # decided by the team; `build_v_eta.py` said "R5 proposed -> channel_assignment
    # (awaiting review)". Two hand-maintained records, contradicting each other, and
    # neither wins automatically -- so the class sat undeleted while the board
    # counted it as settled. The re-verification confirmed THIS record and retired
    # the other. Sibling to the stale "#57 remains a PROPOSAL" sentence found the
    # same day, 474 lines above two sign-off lines saying otherwise.

    # The templates split this: syncgraph/syncrule are a MATLAB class name plus
    # parameters (runtime configuration), while syncrule_mapping carries the
    # COMPUTED epoch-to-epoch clock relationship -- real data, and the shape the
    # time model already covers.
    # DECIDED with the team 2026-08-05; SIGNED 2026-08-08. The earlier "not
    # archival" proposal was WRONG the same way the daq one was: syncrule_mapping
    # references BOTH syncgraph_id and syncrule_id by edge, so dissolving either
    # dangles it. A live query (syncgraph.m:404-408) also reads fields V_eta has
    # already dropped -- see TaskList #58.
    # REVISED 2026-08-06 with the whole cluster. PERSIST stands; the rest changed.
    # syncrule -> `clock_alignment_configuration` (base.id + base.name preserved):
    # `parameters` is NOT a bag but the union of four CLOSED sets, so the shared parts
    # become EDGES (2x acquisition_channels) and DECLARED fields (clock bound to
    # did_clocktype, 3 thresholds); errorOnFailure dropped as runtime behaviour.
    # syncgraph -> `clock_alignment_policy`: it earns existence on MEMBERSHIP (addrule/
    # removerule mean the in-force set is curated, not derivable from the session), and
    # its syncrule_id_# is NOT invented -- syncgraph.m:850 writes it and the NDI SCHEMA
    # declares it mustbenotempty:0, which V_eta wrongly tightened to required.
    ("sync configuration", ["syncgraph", "syncrule"],
     "V_eta_clock_alignment_cluster_plan.md",
     "syncrule -> `clock_alignment_configuration` (parameters DECLARED, devices become "
     "edges); syncgraph -> `clock_alignment_policy` (earns existence on membership)",
     "team"),

    # NOT DECIDED. Claude marked this "team" on 2026-08-05 after a walkthrough;
    # the team corrected that -- they read the options and did not adopt one.
    # What IS established is negative and evidence-backed: the old "folds into
    # relative_reference" claim FAILS (two referents / two frames / an affine
    # transform is not a position on a timeline). clock_alignment is a PROPOSAL.
    # DECIDED with the team 2026-08-06 ("Record the whole cluster"); SIGNED 2026-08-08.
    # syncrule_mapping -> `clock_alignment` (base.id preserved), a relation whose value
    # comes from a new `polynomial` data_type -- NOT {slope,intercept}, because
    # ndi.time.timemapping IS a polynomial by its own docstring and a 2-field shape
    # would be LOSSY. Endpoints are relative_reference DOCUMENTS (each carrying epoch +
    # clock), not clocktype terms. syncgraph_id restored; the invented required
    # `epochid` (5,316 docs, 100% empty) removed.
    ("sync mapping", ["syncrule_mapping"],
     "V_eta_clock_alignment_cluster_plan.md",
     "-> `clock_alignment` (relation + `polynomial` data_type); endpoints are "
     "relative_reference docs; syncgraph_id restored, invented epochid removed",
     "team"),

    # `filter` was grouped here by a guess at its name. It is data/filter.json --
    # label/type/algorithm/parameters, a signal-processing description -- and
    # belongs with software/method, not with file paths.
    # SPLIT: filenavigator is DECIDED (-> file_navigator, id preserved, patterns
    # parsed into declared fields; see V_eta_daq_family_decisions.md). `directory`
    # is ABSENT from NDI origin/main and needs a writer check, not a disposition.
    # Status stays "open" because the family is not fully resolved -- the
    # inaccuracy is deliberately in the under-reporting direction.
    # CLOSED 2026-08-05. filenavigator was decided with the daq family; `directory`
    # is NOT a did_v1 source (provenance V_gamma, and CLAUDE.md already lists it as a
    # post-v1 DID class) -- it landed here by name association, the same mis-grouping
    # that once put `filter` in this family.
    # `directory` was the second member here until 2026-08-11, when the team
    # DELETED the class (build_v_eta.py `_DELETE_NO_V1_PROVENANCE`, where the
    # measurement behind the call is recorded). It has to leave this list too:
    # `ghosts` below exits non-zero when FAMILIES names a class that is not in
    # the built index, which is exactly the check that stops a family from
    # quietly tracking something that no longer exists.
    ("file navigation", ["filenavigator"],
     "V_eta_daq_family_decisions.md",
     "filenavigator -> `epoch_file_pattern` (id preserved; patterns PARSED not eval'd); "
     "`directory` was not a source and is now deleted",
     "team"),

    # openminds_import was REMOVED 2026-07-30 (team sign-off) -- nothing ever
    # emitted it. What is left is the v1 `openminds` carrier: the UNATTACHED
    # openMINDS objects, 8 documents, of which 3 are composite core.research.Strain.
    # SIGNED OFF 2026-08-05: strain is an entity with a repeatable
    # global_identifier + a recursive background_strain_# self-edge; strain_id is
    # an optional edge on term_assertion. Build deferred, TaskList #56. The
    # signature was TRANSCRIBED by Claude on explicit instruction -- see the note
    # at the top of the record before trusting it.
    ("openMINDS", ["openminds"],
     "V_eta_openminds_family_record.md",
     "strain -> entity + recursive background_strain_#; strain_id on term_assertion",
     "team"),

    # Split: the two classes have separate decisions and separate documents.
    ("software", ["app"],
     "V_eta_tenet_audit.md",
     "app -> software entity + software_id edge + execution_environment (R1)",
     "team"),

    ("frequency_filter", ["filter"],
     "V_eta_frequency_filter_model_plan.md",
     "referenced document (not entity); band edges; typed gain fields; no sample_rate",
     "team"),

    # ---- families for the `retire, but nothing decided` rows -------------------
    # These were invisible while the board counted only in_progress. Grouped by
    # what the TEMPLATES contain, not by name prefix -- the mistake that put
    # `filter` under file navigation and split the sync family wrongly.

    # All four are algorithm configuration for spike processing, all inherit `app`,
    # and THREE carry filter parameters of their own:
    #   spike_extraction_parameters(_modification): filter_type/low/high/order/ripple
    #   vmspikefilteringparameters:                 filter_algorithm, filter_algorithm_
    #                                               parameters, rm60Hz (a 60 Hz notch)
    # So v1 has a THIRD filter representation here, and this family cannot be
    # decided without the frequency_filter model it should reference.
    # vmspikefilteringparameters also mixes in `spiketimes` -- OUTPUT data sitting in
    # a parameters class.
    # DECIDED with the team 2026-08-05 (option C); SIGNED 2026-08-09. Four classes
    # collapse to ONE `method_parameters` document -- named for the inline field it
    # is the shared-cardinality form of. The canonical parts (filter, threshold,
    # waveform window, refractory period) get TYPED; the idiosyncratic remainder is
    # honestly a bag. The specific block list is PROPOSED, not decided.
    ("spike processing parameters", [
        "spike_extraction_parameters", "spike_extraction_parameters_modification",
        "sorting_parameters", "vmspikefilteringparameters"],
     "V_eta_method_parameters_plan.md",
     "4 -> 1 `method_parameters` (id+name preserved); canonical parts typed, rest a bag",
     "team"),

    # The stimulus DESCRIPTION: a single ontology-keyed property, and a whole table
    # flattened into one `string` field. Both hang off stimulus_element_id. The
    # stimulus model plan was checked and does NOT mention either class, so "folds
    # with the stimulus model" was an assumption, not a fact.
    # DECIDED with the team 2026-08-06 (A + C); SIGNED 2026-08-08. stimulus_parameter
    # DISSOLVES: it is already a J statement (element -> subject, ontology_name ->
    # variable.node, name -> variable.name, value, epoch anchor), the leaf keyed by
    # the CURIE through D9 -- the Marder documents land as temperature_manipulation.
    # Direction is MANIPULATION: a parameter OF a stimulus is set, not measured.
    # BUILD GATED ON #32 (dissolution makes D9 load-bearing for arbitrary NDIC terms
    # and binding is unenforced). stimulus_parameter_table PASSES THROUGH -- the
    # projectvar disposition: real did_v1, no visible writer, one untyped field, no
    # documents to model against. Both V_eta shapes are wholly invented (not one
    # field or edge matches NDI), so the tombstone repair is required either way --
    # #43's held rows.
    ("stimulus parameters", ["stimulus_parameter", "stimulus_parameter_table"],
     "V_eta_stimulus_parameter_plan.md",
     "stimulus_parameter DISSOLVES to a typed leaf keyed by its CURIE (build gated on "
     "#32); stimulus_parameter_table PASSES THROUGH; both tombstones repaired",
     "team"),

    # NOT the same thing as stimulus parameters: this is the response to a presented
    # stimulus, computed by ndi.app.stimulus.tuning_response -- the input the tuning
    # calculators consumed. The two live classes sat OUTSIDE the J tier system
    # entirely (⊂ base, no direction, no data_type): a V_zeta carry-over that never
    # had a walkthrough.
    # DECIDED with the team 2026-08-06; SIGNED 2026-08-08. 4 classes -> 2: a
    # `harmonic_component` data_type (harmonic 0 = DC/mean, so v1's three
    # response_types are ONE field at three values) + a `harmonic_component_
    # calculation` leaf, id preserved. The parameters class FOLDS inline --
    # at most 6 distinct value-tuples can exist yet 11,440 documents carry them.
    # The first proposal, a `stimulus_response` data_type, was REJECTED by the
    # team on naming: it names a relationship, not a value (the ground `array`
    # was killed on). The field list is PROPOSED, not decided.
    ("stimulus response", [
        "stimulus_response", "stimulus_response_scalar",
        "stimulus_response_scalar_parameters",
        "stimulus_response_scalar_parameters_basic"],
     "V_eta_stimulus_response_model_plan.md",
     "4 -> 2: `harmonic_component` data_type + calculation leaf (id preserved); "
     "parameters fold inline, killing 11,440 empty required edges",
     "team"),

    # A live NDI class with four in-tree emitters, parallel to the newer
    # `measurement`. CLAUDE.md once recorded it as dissolved into `measurement`;
    # that was FALSE and is corrected. {measurement, value, datestamp} on a subject.
    # DECIDED 2026-08-05. A real did_v1 template whose shape IS a subject
    # observation. All four in-tree emitters are TEST-session builders -- see the
    # CLAUDE.md correction in the audit document.
    ("subject measurement", ["subjectmeasurement"],
     "V_eta_go_forward_class_audit.md",
     "route through the `measurement` fold -- no new class; `datestamp` is a TIME "
     "ANCHOR (-> absolute_reference), NOT a field (corrected 2026-08-06)",
     "team"),

    # DECIDED 2026-08-05. control_designation moved to the stimulus family (a V_eta
    # target already resolved there). interaction_purpose is a V_epsilon TARGET whose
    # only open item is its unbound `purpose` (#32), not a disposition.
    # THE ONE-LINER SAID `binaryseries_parameters -> sampled_body` UNTIL
    # 2026-08-11, AND THAT WAS THE OVERRULED READING. It was taking the side of
    # the section heading at V_eta_go_forward_class_audit.md:459 against the
    # TEAM-SIGN-OFF line at :3 in the same document -- the disagreement that held
    # this row in the coverage ledger's DISPUTED bucket, with the board's prose
    # quietly settling it one way while the ledger correctly refused to. The team
    # ruled that the SIGNATURE is what is intended, and the signature routes to
    # TWO mounts: `data_type` to the STATEMENT unconditionally, and the axis
    # entry to `subject_statement` or `sampled_body` by `storage_mode`. Both are
    # now recorded (tools/coverage.py DECIDED_TARGETS_BY_SIGNOFF), so this line
    # names both -- prose and artifact agreeing by construction rather than by
    # nobody noticing.
    ("misc singletons", [
        "binaryseries_parameters", "interaction_purpose", "projectvar"],
     "V_eta_go_forward_class_audit.md",
     "binaryseries_parameters -> subject_statement + sampled_body (the two axis mounts, by storage_mode); projectvar PASSES THROUGH (needs real docs); interaction_purpose is a target (#32)",
     "team"),

    # DECIDED 2026-08-05. Absent from NDI, provenance V_gamma, and referenced by
    # NOTHING -- not even the test suite.
    # `demo / mock` REMOVED 2026-08-06 -- the family is CLOSED, not pending. Its three
    # classes (mock, demo_ndi, demo_ndi_mock) collapsed into ONE `demo` class carrying an
    # is_mock flag, and `demo` is BUILT and persists, so no open class remains for a
    # family to track. See V_eta_go_forward_class_audit.md section 3.
]


SIGNOFF = "TEAM-SIGN-OFF:"


def has_signoff(plan, family):
    """True when the plan document carries an explicit team sign-off line.

    Thin wrapper over find_signoff so there is exactly ONE parser. The guards
    below (HTML comments, [family] tags, template placeholders) are each there
    because a laundering path was found and closed; a second copy of this
    parsing for the JSON export would be a second place for them to drift.
    """
    return find_signoff(plan, family) is not None


def find_signoff(plan, family):
    """Return the sign-off line's content for this family, or None.

    THE RULE THIS ENFORCES. Claude may research a family and write up a
    proposal; it may not record that proposal as the team's decision. On
    2026-07-29 the board had only two states, so attaching a document to a
    family promoted it to "decided" -- five families Claude wrote up alone were
    reported to the team as settled, along with a remaining-work count built on
    them.

    A decision now requires a line the TEAM writes, in the plan document:

        TEAM-SIGN-OFF [<family>]: <who/when> -- <what was decided>

    The [family] tag is REQUIRED when a document is cited by more than one
    family; without it the line would sign all of them (see the check below).
    An untagged line is still honoured for a document cited by exactly one.

    Absent that line the family is displayed as awaiting review, no matter what
    the FAMILIES table claims. This is deliberately not a CI failure: a false
    RED is as useless as a false GREEN, and the honest state is simply "not
    signed off yet".
    """
    if not plan:
        return None
    path = os.path.join(REPO, "schemas", plan)
    if not os.path.exists(path):
        return None
    with open(path) as fh:
        text = fh.read()

    # STRIP HTML COMMENTS FIRST. The first version of this check counted any line
    # starting with the marker -- including the <!-- ... --> block in a plan
    # document that TELLS the team how to sign off. Claude wrote that instruction,
    # so Claude's own document promoted itself to "decided": the exact laundering
    # this function exists to prevent, arriving through a different door. Caught
    # only because the count was verified instead of trusted.
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)

    # A SIGN-OFF MUST BE UNAMBIGUOUS ABOUT WHAT IT SIGNS. Three plan documents are
    # cited by more than one family, so a bare marker in a shared document silently
    # signed every family citing it -- one line for `dataseries_channel_map` would
    # also have promoted `subject measurement`, `misc singletons` and `demo / mock`.
    # Same laundering as the HTML-comment hole above, through a different door, and
    # caught the same way: by checking instead of trusting.
    #
    #   TEAM-SIGN-OFF [family]: who, when -- what     signs THAT family only
    #   TEAM-SIGN-OFF: who, when -- what              signs the document, and counts
    #                                                 ONLY if exactly one family cites it
    shared = sum(1 for f in FAMILIES if f[2] == plan) > 1

    marker = SIGNOFF.rstrip(":")          # the tag sits BETWEEN the marker and the colon
    for line in text.splitlines():
        line = line.lstrip()
        if not line.startswith(marker):
            continue
        rest = line[len(marker):].strip()
        tagged = None
        m = re.match(r"\[([^\]]+)\]\s*(.*)$", rest)
        if m:
            tagged, rest = m.group(1).strip(), m.group(2).strip()
        rest = rest.lstrip(":").strip()
        # A placeholder is not a sign-off. Reject TEMPLATE SLOTS -- a PAIRED
        # <...> -- not any angle bracket: the first version rejected every line
        # containing "<" or ">", so a legitimate sign-off saying
        # "datestamp -> absolute_reference" was silently ignored and the family
        # kept rendering as unsigned. Caught by checking the blast radius instead
        # of trusting that writing the line was enough.
        if re.search(r"<[^>]*>", rest):
            continue
        if len(rest) < 10:
            continue
        if tagged is not None:
            if tagged == family:
                return rest
            continue
        # Untagged: only meaningful when the document belongs to one family.
        if not shared:
            return rest
    return None


def load():
    with open(INDEX) as fh:
        idx = json.load(fh)
    with open(LEDGER) as fh:
        led = json.load(fh)
    return idx["schemas"], led["rows"]


# ===========================================================================
# EVIDENCE LAYER -- the part of the board that is measured rather than declared
# ===========================================================================
#
# Two external sources, each optional, each reported with its own denominator:
#
#   MIGRATOR EVIDENCE  DID-matlab `+did2/+convert/+migrators_j` (the V_eta pass)
#                      and NDI-matlab `+ndi/+migrate/+internal` (the V_eta
#                      second pass). Answers "is anything built for this class".
#   CENSUS EVIDENCE    the per-corpus `*-summary.json` reports written by
#                      did2.unittest.helpers.writeCorpusReport. Answers "do
#                      documents of this class still survive migration".
#
# Neither repo is checked out in this repo's CI, so both are SNAPSHOTTED into
# the generated `V_eta_decisions.json` and reused verbatim when the live source
# is unreachable. That keeps `--check` meaningful: a developer with the sibling
# repos re-measures, and a change in the evidence changes the committed file
# exactly like a change in the schema does. Nothing time-stamped goes into the
# snapshot -- a wall-clock field would make every run differ from every other
# and turn the staleness check into noise.

def find_repo(name, env):
    """Locate a sibling repo the same way tools/coverage.py does."""
    for cand in (os.environ.get(env), os.path.join("/home/user", name),
                 os.path.join(os.path.dirname(REPO), name)):
        if cand and os.path.isdir(cand):
            return cand
    return None


def family_prose_vs_signoff(built_classes):
    """Class names the FAMILIES one-liner asserts that its sign-off never says.

    WHY IT EXISTS, AND WHAT IT WOULD HAVE CAUGHT.
    On 2026-08-11 `ngrid` was filed as a dissolution, corrected to a fold ->
    `sampled_body`, and the correction was wrong. Both commits read one half of
    `V_eta_image_model_plan.md`: one the R4 section heading ("`ngrid` ->
    `sampled_body`"), the other neither. The `TEAM-SIGN-OFF [image / ngrid]`
    line in that same document says "ngrid is DISSOLVED (deleted, not
    migrated)", and the FAMILIES table beside it here says "ngrid phases into
    sampled_body". Two independent readers, one document, opposite conclusions.

    The FAMILIES one-liner is CLAUDE-AUTHORED PROSE in a tool. The sign-off is
    the team's own words. Nothing kept them in agreement, and the failure mode
    is one-directional in the dangerous way: the prose names a concrete target
    class, which is what a reader acts on, while the signature may name only a
    model, a set of field destinations, or a deletion.

    So this sweeps for the SHAPE rather than waiting for the next instance:
    every V_eta class name the one-liner mentions is checked against the text of
    the sign-off that signs that family. A name the signature does not contain
    is UNSIGNED -- which is not automatically wrong, and is never resolved here.

    DELIBERATELY UNDER-FILTERED. Abstract roots (`data_type`, `entity`,
    `subject`) get used as ordinary words -- "a standalone data_type", "->
    entity" -- and would be the obvious things to suppress. They are NOT
    suppressed: a filter tuned on today's eight rows is a filter that hides
    tomorrow's real one, and eight lines across eighteen families is a
    perfectly readable amount of human checking. Erring toward showing too much
    is the safe direction here, and it is the direction this repository's
    mistakes have not gone.

    Returns {"families_checked", "rows": [(family, plan, [names]), ...],
             "multi_untagged": [(plan, n)]}.
    """
    out = {"families_checked": 0, "rows": [], "multi_untagged": []}
    seen_plans = set()
    for name, _members, plan, what, status in FAMILIES:
        if status != "team" or not plan:
            continue
        so = find_signoff(plan, name)
        if so is None:
            continue
        out["families_checked"] += 1
        named = {w for w in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", what)
                 if w in built_classes}
        missing = sorted(w for w in named if w not in so)
        if missing:
            out["rows"].append((name, plan, missing))
        # A SECOND HAZARD FOUND BY THE SAME SWEEP. `find_signoff` returns the
        # FIRST untagged sign-off line in a document cited by exactly one
        # family. `V_eta_openminds_family_record.md` carries TWO untagged ones
        # (2026-08-05, the strain model; 2026-08-08, Part 7), so the board
        # displays one of them and the FAMILIES one-liner paraphrases the
        # other. Neither is wrong; which one is being shown is simply not
        # something a reader can tell.
        if plan in seen_plans:
            continue
        seen_plans.add(plan)
        path = os.path.join(REPO, "schemas", plan)
        if not os.path.exists(path):
            continue
        with open(path) as fh:
            text = re.sub(r"<!--.*?-->", "", fh.read(), flags=re.S)
        untagged = [ln for ln in text.splitlines()
                    if ln.lstrip().startswith("TEAM-SIGN-OFF")
                    and not re.match(r"TEAM-SIGN-OFF\s*\[",
                                     ln.lstrip())]
        if len(untagged) > 1:
            out["multi_untagged"].append((plan, len(untagged)))
    return out


def batch_consumers(classes):
    """Which BATCH POST-PASSES name each of `classes`, by bare quoted literal.

    WHY IT EXISTS. The ledger's `migrator` column means one thing only: a file
    in `+migrators_j` / `+migrators` / `+migrators_i` is NAMED after this class.
    The board then printed "so the documents pass through untouched today",
    which is a different and stronger claim -- and on 2026-08-11 it was false
    for `generic_file`: `+did2/+convert/foldGenericFiles.m` folds it into a
    `term_observation` + an `opaque_body` (carrying `content_hash` from
    `checksum`), a batch post-pass with no per-class file to be named after.
    Absence in one directory, reported as absence everywhere.

    DELIBERATELY NARROW. It is run ONLY over the handful of rows the board is
    about to describe, never over all 102 -- a bare-name sweep across the whole
    ledger matches `'base'` in eight files and `'app'` in one, and a
    false-positive rate like that turns the instrument into noise. Over a
    candidate set of one or two named classes it is exact and checkable.

    The match is the BARE CLASS NAME as a quoted literal, per this project's own
    rule: the construction idiom is not uniform (`ndi.document('valid_interval')`
    finds nothing because `markgarbage` uses `session.newdocument`), so a search
    keyed on one call shape reports absence that is a property of the query.

    Returns {"files_scanned": n, "roots_missing": [...], "by_class": {cls: [files]}}.
    """
    didm = find_repo("DID-matlab", "DID_MATLAB")
    base = os.path.join(didm or "", "src/did/+did2/+convert")
    out = {"files_scanned": 0, "roots_missing": [], "by_class": {}}
    if not didm or not os.path.isdir(base):
        out["roots_missing"].append(base or "DID-matlab (not found)")
        return out
    # The per-class migrator packages are excluded: a hit there is the
    # `migrator` column's business and would double-count. `universalRenames`
    # and the drivers are excluded because they enumerate every class by
    # construction and would match everything.
    skip_dirs = {"+migrators", "+migrators_i", "+migrators_e", "+migrators_j"}
    skip_files = {"Contents.m", "universalRenames.m", "v1_to_v2.m",
                  "fromV1Database.m", "calcCommon.m"}
    texts = {}
    for name in sorted(os.listdir(base)):
        if name in skip_dirs or not name.endswith(".m") or name in skip_files:
            continue
        with open(os.path.join(base, name)) as fh:
            texts[name] = "\n".join(ln.split("%")[0] for ln in fh.read().splitlines())
    out["files_scanned"] = len(texts)
    for cls in classes:
        pat = re.compile(r"'%s'" % re.escape(cls))
        hit = sorted(n for n, t in texts.items() if pat.search(t))
        if hit:
            out["by_class"][cls] = hit
    return out


_IDENT = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")
# After one of these, a `'` is the TRANSPOSE operator, not the start of a string.
_TRANSPOSE_AFTER = _IDENT | set(")]}.'")


def split_matlab_line(line):
    """Split one MATLAB line into (code with strings blanked, [string literals]).

    WHY BOTH HALVES ARE NEEDED, AND WHY THEY MUST NOT BE SEARCHED TOGETHER.
    A class is consumed in one of two spellings:

        isfield(preBody, 'app')      a QUOTED NAME  -> search the literals
        blk = preBody.filter;        a FIELD ACCESS -> search the code

    Searching the raw text for `.app` finds it inside the string literal
    'ndi.app.stimulus.tuning_response' (stimulus_response_scalar.m:210), which
    is a MATLAB function path and has nothing to do with the `app` class. Two
    of the six shortest open class names collide that way, so the split is not
    a nicety.

    Comments are dropped -- a `%` outside a string, and the `...` continuation
    marker. THIS MATTERS IN THE OTHER DIRECTION TOO: +migrators_j documents its
    reasoning at length, and every migrator that mentions a class it does NOT
    touch mentions it in a comment. Counting those would report unbuilt work as
    built, which is the failure this whole board exists to prevent.

    KNOWN LIMIT: the transpose/quote disambiguation is a heuristic (a `'` after
    an identifier, `)`, `]`, `}`, `.` or `'` is read as transpose). It is the
    same heuristic every MATLAB syntax highlighter uses and it can be fooled by
    exotic lines; it cannot be fooled by anything in +migrators_j today.
    """
    out, lits = [], []
    i, n, prev = 0, len(line), ""
    while i < n:
        ch = line[i]
        if ch == "%":
            break
        if line.startswith("...", i):
            break
        if ch in "'\"" and not (ch == "'" and prev in _TRANSPOSE_AFTER):
            j, buf = i + 1, []
            while j < n:
                if line[j] == ch:
                    if j + 1 < n and line[j + 1] == ch:   # doubled = escaped
                        buf.append(ch)
                        j += 2
                        continue
                    break
                buf.append(line[j])
                j += 1
            lits.append(("".join(buf), i))
            out.append(" " * (j - i + 1))
            i, prev = j + 1, ch
            continue
        out.append(ch)
        if not ch.isspace():
            prev = ch
        i += 1
    return "".join(out), lits


# ===========================================================================
# EMISSION -- "a migrator BUILDS a document of this class"
# ===========================================================================
#
# WHY THIS EXISTS. Until 2026-08-10 the build signal could see a class only
# through the SOURCE side: a migrator file NAMED after it, an `isfield(preBody,
# '<class>')` guard, a read of `preBody.<class>`. Every one of those asks "does
# something consume this v1 block". None of them can see a V_eta TARGET that is
# MINTED by a migrator named after its v1 source, and that is a whole category:
#
#     control_designation   built, and rendered "(a) decided, nothing built".
#                           `migrators_j/control_stimulus_ids.m:111` is
#                           `v2Body.document_class = struct('class_name',
#                           'control_designation', ...)` -- the v1 source is
#                           `control_stimulus_ids`, the V_eta target is the
#                           renamed `control_designation`, and no file is or
#                           should be named after the target.
#
# The undercount is the same shape as the private-helper one `migrator_evidence`
# already documents (`app`, `filter`), one step further out: there the file name
# was the wrong key for a v1 SUPERCLASS BLOCK, here it is the wrong key for a
# V_eta TARGET. Both err in the reassuring-in-the-other-direction way this repo
# keeps hitting -- the artifact claims LESS progress than the record holds.
#
# THE PATTERNS ARE IMPORTED FROM tools/coverage.py, NOT RE-WRITTEN. coverage.py's
# guardrail already extracts every `'class_name', '<X>'` a V_eta migrator emits
# ("40 emitted class_names checked against V_eta schema"). A second regex here
# would be a second thing to keep in step with the migrators, and the two would
# disagree silently -- which is how this project produced two contradicting
# hand-maintained records of `dataseries_channel_map`.
#
# WHAT IS ADDED ON TOP OF coverage.py, AND WHY IT IS NOT DIVERGENCE. coverage.py
# needs a SUPERSET: its question is "does every class name this code writes down
# exist in the schema", and for that a superclass entry counts exactly as much as
# a document class. This board needs the narrower fact "a document OF THIS CLASS
# is produced", so two filters are applied to the same patterns:
#
#   * COMMENTS ARE DROPPED. +migrators_j documents its ground truth at length and
#     quotes NDI templates verbatim; counting a quoted class name as an emission
#     would report unbuilt work as built.
#   * SUPERCLASS ENTRIES ARE DROPPED. A `document_class` struct carries the
#     document's own `class_name` AND a `superclasses` array of more
#     `class_name`s. Measured on the 132 migrator files: coverage.py's raw sweep
#     reports 42 distinct names, of which 29 are document classes -- and the 13
#     it conflates include `time_reference` and `epochid`, both of which are
#     emitted ONLY as superclasses of something else and both of which are open
#     classes. Counting those would have moved two classes to "built" on the
#     strength of a superclass mixin.
#
# MATLAB continuation lines make this a STATEMENT-level question, not a
# line-level one: `stimulusBathToBath.m:68-75` spells one `document_class` struct
# across eight physical lines, with `'superclasses'` on line 71 and
# `'time_reference'` on line 72. A per-line rule reads line 72 as a document
# class. So statements are joined first, and the split is by POSITION within the
# joined statement.

def _coverage_class_emit_patterns():
    """`tools/coverage.py`'s `'class_name', '<X>'` patterns, imported.

    Loaded by path rather than by `import coverage`, because `coverage` is also
    a widely installed PyPI package and this file is exec'd by the test suite
    with an arbitrary sys.path. Failure is deliberately LOUD: falling back to a
    local copy of the regex is exactly the silent divergence this reuse exists
    to prevent.
    """
    import importlib.util
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "coverage.py")
    spec = importlib.util.spec_from_file_location(
        "_status_board_coverage_patterns", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return list(mod._CLASS_EMIT)


CLASS_EMIT = _coverage_class_emit_patterns()


def code_before_comment(line):
    """(the line up to its comment/continuation, does it continue?).

    Strings are left INTACT -- unlike `split_matlab_line`'s first return value,
    which blanks them, because the emission patterns match string literals. The
    cut point is taken from `split_matlab_line` rather than recomputed: that
    function already owns the transpose-versus-quote heuristic, and a second
    walk over the line would be a second place for it to be wrong.
    """
    code, _lits = split_matlab_line(line)
    n = len(code)
    return line[:n], line[n:].lstrip().startswith("...")


def logical_statements(lines):
    """Yield (text, spans) per MATLAB statement, continuations joined.

    `spans` is [(offset_in_text, physical_line_no)] so a match inside the joined
    text can be reported at the line a human will find it on. Comments and block
    comments are gone before anything is joined.
    """
    out, buf, spans = [], [], []
    in_block = False
    for lno, line in enumerate(lines, 1):
        s = line.strip()
        if in_block:
            if s == "%}":
                in_block = False
            continue
        if s == "%{":
            in_block = True
            continue
        piece, cont = code_before_comment(line)
        spans.append((sum(len(b) for b in buf), lno))
        buf.append(piece)
        if cont:
            continue
        text = "".join(buf)
        if text.strip():
            out.append((text, spans))
        buf, spans = [], []
    text = "".join(buf)
    if text.strip():
        out.append((text, spans))
    return out


def _line_of(spans, offset):
    lno = spans[0][1] if spans else 0
    for start, n in spans:
        if start <= offset:
            lno = n
        else:
            break
    return lno


# THREE MINT IDIOMS, NOT ONE -- and for four months this function knew about
# one of them.
#
# The docstring below used to say "every one of the 29 document-class emissions
# is written as `<body>.document_class = struct(...)`". Measured on the same
# files on 2026-08-11, that is 45 of the 62 `document_class` WRITES; the other
# 17 are two idioms a `'class_name'`-comma regex cannot see:
#
#   IDIOM 2  obs.document_class = classBlock('score_observation', {...})
#            `classBlock` is a LOCAL SUBFUNCTION, redefined in 8 files with two
#            different arities, which returns the struct. Nothing in the call
#            statement says `class_name` at all.
#   IDIOM 3  v2Body.document_class.class_name = 'acquisition_epoch';
#            The field write. Again no `'class_name', '<X>'` comma pair.
#
# THE COST WAS NOT HYPOTHETICAL. `session_relative_reference` -- a class whose
# whole open question is that it must STOP being emitted -- renders its mint
# count. With idiom 1 alone that count is 3. The real number is 9: six migrators
# (fitcurve, image_stack, jrclust_clusters, neuron_extracellular, pyraview,
# vmspikefit) mint it through `classBlock`. The board reported a THIRD of the
# outstanding work, in this repo's characteristic direction -- less left to do
# than there is. The six missed mints were not dropped; they were filed as
# `named`, i.e. as the weakest possible evidence, which is worse than dropping
# them because it looks like a measurement.
#
# IDIOM 2 IS RESOLVED FROM THE HELPER'S OWN SOURCE, NOT FROM ITS NAME. Nothing
# here knows the string "classBlock". A local function qualifies when its body
# assigns ITS OWN OUTPUT a struct that declares `superclasses` and takes its
# `class_name` from one of its PARAMETERS -- that is what a class block is, and
# nothing else in these packages does it. The parameter's INDEX is what is
# recorded, so the literal is read from the right argument at the call site and
# the superclass list (argument 2) cannot be mistaken for a mint. A helper that
# gains an argument, or is renamed, or is copied into a ninth file, is handled
# without an edit here; a hard-coded name would have to be chased.
#
# WHAT STILL CANNOT BE SEEN, STATED SO THE COUNT IS READ AS A FLOOR. When the
# class name is a VARIABLE -- `struct('class_name', leafClass, ...)`,
# `classBlock(e.class, ...)` -- the literal lives at a call site in another
# function and resolving it needs the CALL GRAPH. That is a real analysis and it
# already exists in `tools/refresh_migration_targets.py`, which walks from each
# migrator entry point through `private/` helpers substituting arguments for
# parameters. This function is deliberately the narrower, per-file one, so it
# reports those sites as UNRESOLVED and counts them, rather than passing over
# them in silence. Six such sites exist today and they are named in the board's
# own denominator table.
_DC_CLASS_NAME_WRITE = re.compile(r"document_class\s*\.\s*class_name\s*$")
# `'class_name', <bare identifier>` -- the value is a VARIABLE, so the literal is
# somewhere else. Deliberately separate from coverage.py's `CLASS_EMIT`, which
# matches only quoted values.
_SYMBOLIC_CLASS_NAME = re.compile(
    r"""['"]class_name['"]\s*,\s*([A-Za-z_]\w*(?:\.\w+)*)""")
_SINGLE_LITERAL = re.compile(r"^\s*'((?:[^']|'')*)'\s*;?\s*$")
_CALL_HEAD = re.compile(r"^\s*([A-Za-z_]\w*)\s*\(")
_FUNCTION_HEAD = re.compile(
    r"^\s*function\s+"
    r"(?:\[(?P<outs>[^\]]*)\]\s*=\s*|(?P<out1>[A-Za-z_]\w*)\s*=\s*)?"
    r"(?P<name>[A-Za-z_]\w*)\s*(?:\((?P<args>[^)]*)\))?")


def class_block_helpers(lines):
    """{local function name: index of its class-name PARAMETER}.

    A CLASS BLOCK HELPER is recognised by what it does, never by its name: it
    assigns its own output variable a struct that declares `superclasses` and
    whose `class_name` value is one of the function's own parameters. See the
    block comment above for why the shape and not the name.
    """
    heads = []
    in_block = False
    for i, line in enumerate(lines):
        s = line.strip()
        if in_block:
            if s == "%}":
                in_block = False
            continue
        if s == "%{":
            in_block = True
            continue
        if not s.startswith("function"):
            continue
        m = _FUNCTION_HEAD.match(line)
        if m:
            heads.append((i, m))
    out = {}
    for k, (i, m) in enumerate(heads):
        end = heads[k + 1][0] if k + 1 < len(heads) else len(lines)
        args = (m.group("args") or "").strip()
        params = [a.strip() for a in args.split(",") if a.strip()]
        outs = [o.strip()
                for o in (m.group("outs") or m.group("out1") or "").split(",")
                if o.strip()]
        if not params or not outs:
            continue
        for text, _spans in logical_statements(lines[i:end]):
            code, _lits = split_matlab_line(text)
            eq = assignment_split(code)
            if eq is None or text[:eq].strip() not in outs:
                continue
            rhs = text[eq + 1:]
            if "superclasses" not in rhs:
                continue
            cut = rhs.find("superclasses")
            for sm in _SYMBOLIC_CLASS_NAME.finditer(rhs[:cut]):
                if sm.group(1) in params:
                    out[m.group("name")] = params.index(sm.group(1))
    return out


def _top_level_args(text, code, open_paren):
    """Positional argument source strings of the call whose `(` is at
    `open_paren`. Depth is taken from `code` (strings blanked, same length as
    `text`) so a comma inside a literal cannot split an argument."""
    depth, start, args = 0, open_paren + 1, []
    for i in range(open_paren, len(code)):
        ch = code[i]
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
            if depth == 0:
                args.append((start, text[start:i]))
                return args
        elif ch == "," and depth == 1:
            args.append((start, text[start:i]))
            start = i + 1
    return args


def emitted_document_classes(lines, unresolved=None, idioms=None):
    """{(class_name, physical_line_no)} -- documents this file MINTS.

    Three idioms are recognised (see the block comment above). In every one, a
    match counts only when it is the class of a document being BUILT and not one
    of that document's ancestors:

      1. `<body>.document_class = struct('class_name', '<X>', ...)` -- the
         literal must appear AFTER the word `document_class` and BEFORE the word
         `superclasses` within its own joined statement. MATLAB continuations
         make this a statement-level question: `stimulusBathToBath.m:136-141`
         spells one such struct over six physical lines with `'superclasses'` on
         line 138, and a per-line rule reads line 139 as a document class.
      2. `<body>.document_class = <helper>('<X>', ...)` where `<helper>` is a
         local class-block function -- the literal is read from the argument at
         that helper's own class-name parameter INDEX, so the superclass
         argument beside it cannot be mistaken for a mint.
      3. `<body>.document_class.class_name = '<X>';`

    `unresolved`, if given a list, collects `(physical_line_no, expression)` for
    every `document_class` write whose class name is a VARIABLE. Those are mints
    this per-file analysis cannot name; they are counted and reported, never
    dropped. `idioms`, if given a dict, is tallied per idiom number so the
    artifact can state how many sites each shape accounts for instead of
    carrying a hand-written figure that goes stale.
    """
    def _tally(n):
        if idioms is not None:
            idioms[n] = idioms.get(n, 0) + 1
    found = set()
    helpers = class_block_helpers(lines)
    for text, spans in logical_statements(lines):
        anchor = text.find("document_class")
        if anchor < 0:
            continue
        code, _lits = split_matlab_line(text)
        eq = assignment_split(code)
        lhs = text[:eq] if eq is not None else ""
        rhs_off = (eq + 1) if eq is not None else 0
        hit = False

        # IDIOM 3 -- the field write. Checked first: its LHS also contains the
        # word `document_class`, so idiom 1's window would otherwise open on it.
        if _DC_CLASS_NAME_WRITE.search(lhs.rstrip()):
            rhs = text[rhs_off:]
            lm = _SINGLE_LITERAL.match(rhs)
            line = _line_of(spans, rhs_off)
            if lm:
                found.add((lm.group(1), line))
                _tally(3)
            elif unresolved is not None:
                unresolved.append((line, rhs.strip()[:80]))
            continue

        # IDIOM 1 -- the struct literal. Unchanged, including the anchor rule,
        # so nothing this function already saw can stop being seen.
        cut = text.find("superclasses")
        for pat in CLASS_EMIT:
            for m in pat.finditer(text):
                if m.start() < anchor:
                    continue
                if cut != -1 and m.start() > cut:
                    continue
                found.add((m.group(1), _line_of(spans, m.start())))
                _tally(1)
                hit = True

        # IDIOM 2 -- the local class-block helper.
        if "document_class" in lhs:
            cm = _CALL_HEAD.match(text[rhs_off:])
            if cm and cm.group(1) in helpers:
                idx = helpers[cm.group(1)]
                args = _top_level_args(text[rhs_off:], code[rhs_off:],
                                       cm.end() - 1)
                if idx < len(args):
                    start, src = args[idx]
                    lm = _SINGLE_LITERAL.match(src)
                    line = _line_of(spans, rhs_off + start)
                    if lm:
                        found.add((lm.group(1), line))
                        _tally(2)
                        hit = True
                    elif unresolved is not None:
                        unresolved.append((line, src.strip()[:80]))
                        hit = True

        # A `document_class` write whose class name resolved to nothing is a
        # mint this analysis cannot name. Rule 3: that is not a zero.
        if not hit and unresolved is not None and "document_class" in lhs:
            window = text[rhs_off:cut if cut != -1 else len(text)]
            for sm in _SYMBOLIC_CLASS_NAME.finditer(window):
                unresolved.append((_line_of(spans, rhs_off + sm.start()),
                                   sm.group(1)))
    return found


def assignment_split(code):
    """Column of the top-level `=` in a MATLAB statement, or None.

    Used to tell a READ from a WRITE, which is the difference between a migrator
    CONSUMING a class and a migrator EMITTING one -- see `REF_KINDS`. Skips
    ==, ~=, <= and >=, and anything inside brackets (so `f(a==b)` and
    `s.x(i) = 1` both read correctly).
    """
    depth = 0
    for i, ch in enumerate(code):
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        elif ch == "=" and depth == 0:
            if i + 1 < len(code) and code[i + 1] == "=":
                continue
            if i and code[i - 1] in "=~<>":
                continue
            return i
    return None


# WHY A REFERENCE'S KIND DECIDES WHETHER IT COUNTS.
#
# The first draft of this scan counted any mention, and it promoted classes in
# the REASSURING DIRECTION -- the exact bias this board exists to remove. Two
# live examples from the first run:
#
#   `directory`  matched jSorterOutput.m:77, which is
#                `body.opaque_body = struct('format', 'directory', ...)`.
#                That is a FORMAT VALUE, not the class. `directory` has nothing
#                built and was rendered as built.
#   `session_relative_reference`
#                matched 18 lines, every one of them a migrator EMITTING the
#                class (fitcurve.m:139 `classBlock('session_relative_reference',
#                {'time_reference'})`, then `anchor.session_relative_reference =
#                struct(...)`). The open work on that class is its COLLAPSE into
#                `relative_reference`; a migrator still writing the old class is
#                evidence the collapse has NOT landed, and counting it as
#                "built" inverted the meaning of the number.
#
# So a reference is classified, and only CONSUMPTION counts toward (b):
#
#   guard       `isfield(preBody, 'app')`        the migrator tests for the block
#               `strcmp(classNameOf(s),'ensemble')`  ... or dispatches on the class
#   field_read  `blk = preBody.filter;`          the migrator reads the block
#   field_write `anchor.time_reference = ...`    the migrator WRITES this class
#   named       `classBlock('x'), 'format','x'`  the name appears, nothing more
#
# `field_write` and `named` are still reported per class -- a fact about an open
# class that is deliberately unflattering -- they just do not make it (b).
#
# THEY ARE REPORTED SEPARATELY, EACH WITH ITS OWN COUNT, AND THAT IS THE POINT.
# Until 2026-08-11 the artifact summed them into one cell captioned "still
# emitted/named at N site(s)". `session_relative_reference`'s N was 15 and it was
# SIX MISSED MINTS plus NINE field writes -- three unlike facts wearing one
# number. Anyone reading it had no way to tell an outstanding emission from a
# block write, and the number was quoted onwards as though it were one kind of
# thing. A summed count of unlike categories is not a measurement; it is the
# shape of a measurement.
#
# `comment_mention` IS A SIXTH KIND, AND IT COUNTS TOWARD NOTHING AT ALL.
# Comments have always been dropped by `split_matlab_line` before this scan sees
# a line, so they have never inflated a count -- but "they are not in there" was
# a claim a reader had to take on trust, and this project does not run on trust.
# Counting them EXPLICITLY, in their own column, makes the claim checkable from
# the artifact: +migrators_j mentions `session_relative_reference` in 16 comments
# and every one of them is visible, in the column that counts toward nothing.
#
# THE GUARD LIST IS NOT COSMETIC. Its first version held only isfield/isstruct
# and missed the SECOND PASS entirely: an NDI assembler selects its input with
# `if ~strcmp(classNameOf(s), 'ensemble'); continue; end`
# (ensembleMembership.m:227), which is the whole ensemble consumer and was being
# filed as a bare mention. A comparison names what the code is LOOKING FOR; an
# assignment names what it PRODUCES.
#
# `emitted_class` IS THE FIFTH KIND, ADDED 2026-08-10, and it is the only one
# that is evidence about a V_eta TARGET rather than about a v1 source:
#
#   emitted_class  `b.document_class = struct('class_name','x', ...)`
#                  the migrator MINTS a document of this class
#
# It was previously swept up as `named` -- indistinguishable from
# `struct('format','directory', ...)` -- which is why `control_designation`
# rendered as "(a) decided, nothing built" while control_stimulus_ids.m:111 was
# building it. Whether it counts as BUILD PROGRESS is decided per class, in
# `RETIRED_BY_ITS_OWN_DECISION` below, and NOT here: for a class whose signed
# decision is that it stops existing, an emission means the opposite.
GUARD_FUNCS = ("isfield", "isstruct", "strcmp", "strcmpi", "ismember", "matches")
CONSUMING_KINDS = ("guard", "field_read")
EMITTED_CLASS_KIND = "emitted_class"
COMMENT_KIND = "comment_mention"
REF_KINDS = ("guard", "field_read", "field_write", "named", COMMENT_KIND,
             EMITTED_CLASS_KIND)
# Kinds that are evidence about CODE. `comment_mention` is prose and is excluded
# from every count that means anything; it is carried so its absence from those
# counts can be checked rather than believed.
CODE_KINDS = tuple(k for k in REF_KINDS if k != COMMENT_KIND)


def scan_matlab_file(path, patterns, unresolved=None, idioms=None):
    """Return ({class: [(line_no, kind)]}, n_lines) for one .m file.

    `unresolved`, if given a list, collects `(line_no, expression)` for every
    `document_class` write whose class name is a variable this per-file analysis
    cannot resolve to a literal -- mints that are real and unnamed, not absent.
    """
    hits, in_block = {}, False
    try:
        with open(path, errors="replace") as fh:
            lines = fh.readlines()
    except OSError:
        return hits, 0
    # Statement-level, so it is computed over the whole file before the
    # line-level sweep below can mis-file one of its hits as `named`.
    emissions = emitted_document_classes(lines, unresolved, idioms)
    word = {cls: re.compile(r"(?<![\w])" + re.escape(cls) + r"(?![\w])")
            for cls in patterns}
    for lno, line in enumerate(lines, 1):
        s = line.strip()
        if in_block:
            if s == "%}":
                in_block = False
            else:
                for cls, wrx in word.items():
                    if wrx.search(line):
                        hits.setdefault(cls, []).append((lno, COMMENT_KIND))
            continue
        if s == "%{":
            in_block = True
            continue
        code, lits = split_matlab_line(line)
        # Whatever `split_matlab_line` refused to read is a `%` comment or the
        # tail after a `...` continuation -- prose either way.
        prose = line[len(code):]
        if prose.strip():
            for cls, wrx in word.items():
                if wrx.search(prose):
                    hits.setdefault(cls, []).append((lno, COMMENT_KIND))
        if not lits and not code.strip():
            continue
        eq = assignment_split(code)
        guardish = any(g in code for g in GUARD_FUNCS)
        by_name = {}
        for text, col in lits:
            by_name.setdefault(text, col)
        for cls, rx in patterns.items():
            if cls in by_name:
                if (cls, lno) in emissions:
                    kind = EMITTED_CLASS_KIND
                elif guardish:
                    kind = "guard"
                else:
                    kind = "named"
                hits.setdefault(cls, []).append((lno, kind))
                continue
            if cls not in code:
                continue
            m = rx.search(code)
            if not m:
                continue
            kind = "field_read" if (eq is None or m.start() > eq) else "field_write"
            hits.setdefault(cls, []).append((lno, kind))
    return hits, len(lines)


# The V_eta migration is TWO passes, and both count as "something is built".
# +migrators (V_zeta) and +migrators_i (intermediate) are deliberately NOT
# scanned: a V_zeta migrator is not evidence that the V_eta target is built, and
# counting it would inflate (b) with work that predates every decision here.
#
# THE TWO PASSES LIVE IN DIFFERENT REPOSITORIES, AND EVERY SITE SAYS WHICH.
# The board used to print `ndi_second_pass/stimulusBathToBath.m:137` -- a package
# label and a path, with nothing naming the repository. A reader looking for that
# file in DID-matlab, which is where the board's other 130-odd files are and
# where its `--did` argument points, finds NOTHING: it is
# NDI-matlab `src/ndi/+ndi/+migrate/+internal/stimulusBathToBath.m`. A citation
# that cannot be followed to the repository holding it is not a citation, and a
# reader who cannot find the file has to choose between believing the board and
# believing their own search. So the repository is part of every reference now:
#     NDI-matlab:ndi_second_pass/stimulusBathToBath.m:137
#
# ---------------------------------------------------------------------------
# THE BOARD READ HALF THE V_eta PATH -- corrected 2026-08-11
# ---------------------------------------------------------------------------
# `+migrators_j` is the PER-DOCUMENT half of the DID-side pass: one file per v1
# class, each seeing one document at a time. The other half is the BATCH
# POST-PASSES, which run over the whole converted batch after the per-document
# migrators and do the work a single-document migrator provably cannot -- mint
# an epoch, resolve a session anchor, fold deferred baths. They live one
# directory UP, in `+did2/+convert` itself and in its `+entities/`/`+readers/`
# helper packages, and the scan roots did not name them. Re-derived census of
# `+did2/+convert`, which is the denominator this correction is measured
# against:
#
#     187  .m files under +did2/+convert
#     125    +migrators_j                     SCANNED, always was
#      22    +migrators           \
#       9    +migrators_i          >  38  V_zeta path   EXCLUDED, deliberately
#       7    +migrators_e         /
#      14    directly in +convert \
#       7    +entities/            >  24  V_eta batch post-passes  ADDED HERE
#       3    +readers/            /
#
# The 38 stay out for the reason at the top of this comment, and that exclusion
# is now EXPLICIT and COUNTED (`files_excluded_v_zeta`) instead of being an
# omission from a list: an exclusion nobody can see in the output is
# indistinguishable from a root somebody forgot, which is precisely how the 24
# went missing.
#
# THE TWO GROUPS ARE NEVER MERGED INTO ONE COUNT. A mint in a batch post-pass
# and a mint in a per-document migrator are different facts about a class -- the
# first says the whole-batch pass builds it, the second says the per-document
# pass does -- and this file has already paid once for summing unlike categories
# (see the `GUARD_FUNCS` block comment). Every count below is carried per group
# as well as in total, and the artifact prints the split.
GROUP_MIGRATOR = "per_document_migrator"
GROUP_BATCH = "batch_post_pass"
GROUP_LABEL = {
    GROUP_MIGRATOR: "per-document migrator",
    GROUP_BATCH: "batch post-pass",
}
GROUPS = (GROUP_MIGRATOR, GROUP_BATCH)

# The V_zeta / intermediate packages. NOT a cosmetic list: the batch root is the
# whole of `+did2/+convert`, so without these names the recursive walk would
# swallow the 38 files the board is right to ignore. `+migrators_j` is here too
# because it has its OWN root above -- reaching it twice would double every
# per-document count.
V_ZETA_PACKAGES = ("+migrators", "+migrators_i", "+migrators_e")
_CONVERT_ALREADY_SCANNED = ("+migrators_j",)

MIGRATOR_PACKAGES = [
    ("did", "DID-matlab", "migrators_j", "src/did/+did2/+convert/+migrators_j",
     GROUP_MIGRATOR, ()),
    ("ndi", "NDI-matlab", "ndi_second_pass", "src/ndi/+ndi/+migrate/+internal",
     GROUP_MIGRATOR, ()),
    # The batch post-passes. ONE recursive root with a NAMED exclusion, rather
    # than three enumerated roots: enumeration is what failed here, and a new
    # `+convert/+something` helper package would be missed again by a list.
    ("did", "DID-matlab", "convert", "src/did/+did2/+convert",
     GROUP_BATCH, V_ZETA_PACKAGES + _CONVERT_ALREADY_SCANNED),
]

REF_CAP = 6            # refs listed per class in the artifact; the count is exact


def package_files(base, skip_dirs):
    """(files under `base`, files pruned by `skip_dirs`) -- both counted.

    `os.walk` with pruning rather than `glob('**/*.m')`, because the batch root
    is the parent of the V_zeta packages and the exclusion has to be able to cut
    a subtree. The pruned files are RETURNED, keyed by the package that cut
    them, not discarded: "38 files were skipped on purpose" and "the root was
    wrong" have to be distinguishable from the output alone, which is the whole
    defect this root list is fixing -- and "skipped because it is V_zeta" has to
    be distinguishable from "skipped because another root already read it".
    """
    kept, skipped = [], {}
    for dirpath, dirs, names in os.walk(base):
        pruned = [d for d in dirs if d in skip_dirs]
        dirs[:] = sorted(d for d in dirs if d not in skip_dirs)
        for d in pruned:
            bucket = skipped.setdefault(d, [])
            for sdir, _sd, snames in os.walk(os.path.join(dirpath, d)):
                bucket.extend(os.path.join(sdir, nm) for nm in snames
                              if nm.endswith(".m"))
        kept.extend(os.path.join(dirpath, nm) for nm in sorted(names)
                    if nm.endswith(".m"))
    return sorted(kept), {d: sorted(v) for d, v in skipped.items()}


def migrator_evidence(classes, did_root, ndi_root):
    """Scan the V_eta migrator packages for every open class.

    THE SIGNAL IS DELIBERATELY WIDER THAN A FILENAME MATCH, and the reason is
    that filename matching UNDERCOUNTS in a specific, known way: several classes
    are v1 SUPERCLASS BLOCKS rather than standalone documents, so no file is
    named after them and they are consumed by a shared helper in `private/` --
    `app` by jSoftwareFromApp.m:64, `filter` by jFrequencyFilter.m:112. The
    coverage ledger's `migrator` boolean is exactly that filename match, and it
    reports `app` as having no migrator while jSoftwareFromApp folds it.

    WHAT THIS SIGNAL MISSES, stated so nobody reads it as more than it is:

      * A MIGRATOR THAT NAMES A CLASS IS NOT NECESSARILY CONSUMING IT. Several
        +migrators_j files exist only to pass their class THROUGH deliberately
        (daqsystem.m says so in its own header: the document "shows in
        unconverted_by_class at its full corpus count; that is the honest
        signal"). This scan cannot tell a fold from a passthrough. That is
        precisely why a build signal alone is state (b) and never (c) -- only
        the census can tell them apart.
      * A CLASS REACHED THROUGH A COMPUTED NAME is invisible to the MINT
        recogniser -- `struct('class_name', leafClass, ...)`,
        `classBlock(e.class, ...)`. Those sites are COUNTED and LISTED
        (`unresolved_mint_sites`) rather than passed over, because "the analysis
        could not read it" and "there is nothing there" are different facts and
        this project has paid for conflating them. Six exist today.
      * FIELD-ACCESS HITS CAN BE INCIDENTAL for the short names. `.filter` is
        matched in jSpikeExtractionSettings.m as a grouping key as well as in
        jFrequencyFilter.m as the v1 block. Every reference is listed with its
        file and line so the reading is checkable rather than trusted.

    EVERY OCCURRENCE LANDS IN EXACTLY ONE BUCKET, AND THE BUCKETS ARE NEVER
    SUMMED. `mint`, `consumed`, `field_write`, `named` and `comment_mention` are
    five different facts about a class; each is returned with its own count.

    NOR ARE THE TWO GROUPS SUMMED WITHOUT BEING SHOWN. Every bucket is returned
    per group (`by_group`) as well as in total, so a mint in a batch post-pass
    is never indistinguishable from a mint in a per-document migrator.
    """
    patterns = {c: re.compile(r"\.\s*" + re.escape(c) + r"\b") for c in classes}
    per_class, roots_read, roots_missing = {}, [], []
    unresolved_sites, idiom_counts = [], {}
    files_read = lines_read = 0
    excluded_files = {}
    by_group_files = {g: 0 for g in GROUPS}
    by_group_lines = {g: 0 for g in GROUPS}
    by_group_idioms = {g: {} for g in GROUPS}
    by_group_unresolved = {g: [] for g in GROUPS}
    for kind, repo, label, rel, group, skip_dirs in MIGRATOR_PACKAGES:
        root = did_root if kind == "did" else ndi_root
        base = os.path.join(root, rel) if root else None
        if not base or not os.path.isdir(base):
            roots_missing.append("%s:%s" % (repo, label))
            continue
        roots_read.append("%s:%s" % (repo, label))
        kept, skipped = package_files(base, set(skip_dirs))
        for pkg, paths in skipped.items():
            excluded_files.setdefault(pkg, []).extend(
                "%s:%s/%s" % (repo, label, os.path.relpath(p, base))
                for p in paths)
        for path in kept:
            rel_path = "%s:%s/%s" % (repo, label, os.path.relpath(path, base))
            files_read += 1
            by_group_files[group] += 1
            name = os.path.basename(path)[:-2]
            # A FILE NAMED AFTER A CLASS is the per-document migrator's naming
            # convention and only that group's: `+convert/epochMint.m` is not a
            # migrator for a class called `epochMint`. Recording a batch file
            # here would invent build evidence out of a filename.
            if (group == GROUP_MIGRATOR and name in classes
                    and os.path.dirname(path) == base):
                per_class.setdefault(name, {}).setdefault("file", rel_path)
            unresolved = []
            idioms_here = {}
            hits, n_lines = scan_matlab_file(path, patterns, unresolved,
                                             idioms_here)
            for k, v in idioms_here.items():
                idiom_counts[k] = idiom_counts.get(k, 0) + v
                by_group_idioms[group][k] = by_group_idioms[group].get(k, 0) + v
            lines_read += n_lines
            by_group_lines[group] += n_lines
            for lno, expr in unresolved:
                site = "%s:%d (%s)" % (rel_path, lno, expr)
                unresolved_sites.append(site)
                by_group_unresolved[group].append(site)
            for cls, spots in hits.items():
                refs = per_class.setdefault(cls, {}).setdefault("refs", [])
                for lno, why in spots:
                    refs.append(("%s:%d" % (rel_path, lno), why, group))

    if not roots_read:
        return None, {"available": False, "packages_read": [],
                      "packages_missing": roots_missing, "files_read": 0,
                      "lines_read": 0, "classes_queried": len(classes)}

    def _bucket(refs, kinds):
        """(count, capped citation list, per-group counts, per-group citations).

        The tuple carries the group, so the caller never has to guess it back
        out of a path.
        """
        sel = [r for r in refs if r[1] in kinds]
        n_by = {g: sum(1 for r in sel if r[2] == g) for g in GROUPS}
        refs_by = {g: ["%s (%s)" % (r[0], r[1])
                       for r in sel if r[2] == g][:REF_CAP] for g in GROUPS}
        return (len(sel), ["%s (%s)" % (r[0], r[1]) for r in sel[:REF_CAP]],
                n_by, refs_by)

    _BUCKETS = (
        ("consuming_refs", CONSUMING_KINDS),
        # THE CLASS THIS PASS MINTS -- a document of it is produced.
        ("emitted_class_refs", (EMITTED_CLASS_KIND,)),
        # A BLOCK OF THAT NAME IS WRITTEN -- `anchor.<class> = struct(...)`.
        # Not a mint: the mint is the `document_class` statement a few lines
        # above it, and counting the pair together double-counts one document
        # while making the two indistinguishable.
        ("field_write_refs", ("field_write",)),
        # THE NAME APPEARS IN CODE AND NOTHING MORE -- a string value such as
        # `struct('kind', 'epoch_bounded_reference', ...)`.
        ("named_refs", ("named",)),
        # PROSE. Counts toward nothing; carried so that can be verified.
        ("comment_mentions", (COMMENT_KIND,)),
    )

    out = {}
    n_with_emission = 0
    n_emission_by_group = {g: 0 for g in GROUPS}
    for cls in sorted(classes):
        ev = per_class.get(cls, {})
        refs = sorted(ev.get("refs", []))
        row = {"migrator_file": ev.get("file")}
        by_group = {g: {} for g in GROUPS}
        for key, kinds in _BUCKETS:
            n, cited, n_by, cited_by = _bucket(refs, kinds)
            nkey = "n_" + key
            row[nkey] = n
            row[key] = cited
            for g in GROUPS:
                by_group[g][nkey] = n_by[g]
                by_group[g][key] = cited_by[g]
        row["by_group"] = by_group
        if row["n_emitted_class_refs"]:
            n_with_emission += 1
        for g in GROUPS:
            if by_group[g]["n_emitted_class_refs"]:
                n_emission_by_group[g] += 1
        out[cls] = row
    return out, {"available": True, "packages_read": roots_read,
                 "packages_missing": roots_missing, "files_read": files_read,
                 "lines_read": lines_read, "classes_queried": len(classes),
                 "classes_emitted_as_document_class": n_with_emission,
                 "unresolved_mint_sites": sorted(unresolved_sites),
                 "n_unresolved_mint_sites": len(unresolved_sites),
                 # Sites per mint idiom, over ALL classes in these packages --
                 # not only the open ones queried. The artifact prints these
                 # rather than a hand-written figure that cannot go stale
                 # quietly.
                 "mint_sites_by_idiom": {str(k): idiom_counts[k]
                                         for k in sorted(idiom_counts)},
                 # THE SAME FIGURES SPLIT BY GROUP. Present so that no reader
                 # has to take "the batch post-passes are in there now" on
                 # trust: if this block is all zeros, the 24 were not read.
                 "groups": list(GROUPS),
                 "group_labels": dict(GROUP_LABEL),
                 "packages_by_group": {
                     g: ["%s:%s" % (repo, label)
                         for _k, repo, label, _r, grp, _s in MIGRATOR_PACKAGES
                         if grp == g and "%s:%s" % (repo, label) in roots_read]
                     for g in GROUPS},
                 "files_read_by_group": by_group_files,
                 "lines_read_by_group": by_group_lines,
                 "classes_emitted_as_document_class_by_group":
                     n_emission_by_group,
                 "mint_sites_by_idiom_by_group": {
                     g: {str(k): by_group_idioms[g][k]
                         for k in sorted(by_group_idioms[g])} for g in GROUPS},
                 "n_unresolved_mint_sites_by_group": {
                     g: len(by_group_unresolved[g]) for g in GROUPS},
                 "unresolved_mint_sites_by_group": {
                     g: sorted(by_group_unresolved[g]) for g in GROUPS},
                 # THE V_zeta EXCLUSION, COUNTED RATHER THAN ASSUMED. These
                 # files are skipped on purpose; a zero here would mean the
                 # exclusion stopped reaching them, not that they went away.
                 # `+migrators_j` is kept in its own row because it is skipped
                 # by the BATCH root for a different reason -- its own root
                 # already read it -- and folding the two would make 125 read
                 # files look like 125 ignored ones.
                 "v_zeta_packages_excluded": list(V_ZETA_PACKAGES),
                 "n_files_excluded_by_package": {
                     pkg: len(v) for pkg, v in sorted(excluded_files.items())},
                 "n_files_excluded_v_zeta": sum(
                     len(excluded_files.get(p, ())) for p in V_ZETA_PACKAGES),
                 "files_excluded_v_zeta": sorted(
                     f for p in V_ZETA_PACKAGES
                     for f in excluded_files.get(p, ())),
                 "ref_kinds": list(REF_KINDS),
                 "code_kinds": list(CODE_KINDS),
                 "comment_kind": COMMENT_KIND,
                 "consuming_kinds": list(CONSUMING_KINDS),
                 "emitted_class_kind": EMITTED_CLASS_KIND}


def find_census_reports(roots):
    """Every *-summary.json under each root, at ANY depth, deduped by basename.

    Mirrors DID-matlab tools/census_digest.py:find_reports, and for the same
    reason it is recursive there: MATLAB's pwd during a corpus run is `tests/`,
    and upload-artifact re-roots the paths, so a one-level glob matched neither
    copy and a six-corpus run reported nothing while exiting 0.
    """
    found, missing, walked = [], [], 0
    for root in roots:
        if not os.path.isdir(root):
            missing.append(root)
            continue
        for dirpath, _dirs, names in os.walk(root):
            walked += 1
            for nm in sorted(names):
                if nm.endswith("-summary.json"):
                    found.append(os.path.join(dirpath, nm))
    found.sort(key=lambda p: (len(p.split(os.sep)), p))
    chosen, seen = [], set()
    for p in found:
        b = os.path.basename(p)
        if b not in seen:
            seen.add(b)
            chosen.append(p)
    return chosen, missing, walked, len(found)


def census_evidence(classes, roots):
    """Per-class SURVIVOR counts from the corpus reports.

    `summary.unconverted_by_class` is the survivor count: v1_to_v2.m:186 bumps
    it when a migrator hands its input straight back (`isequaln(v2Bodies{1},
    v2Body)`). It is keyed by the POST-universalRenames class name, which is the
    same name the built index uses, so no translation is needed.

    THE PRESENCE OF THE KEY IS WHAT MATTERS, NOT ITS CONTENTS. A report with
    `unconverted_count: 0` and an EMPTY `unconverted_by_class` has measured
    every class and found no survivor -- that is real evidence. A report with no
    `unconverted_count` AT ALL has measured nothing, and its silence must not be
    read as a zero. The two are one missing key apart and were the difference
    between a census and a decoration for two days on the DID-matlab side.
    """
    paths, missing, walked, n_all = find_census_reports(roots)
    reports, unreadable = [], []
    for p in paths:
        try:
            with open(p) as fh:
                reports.append((os.path.basename(p), json.load(fh)))
        except (OSError, ValueError) as err:
            unreadable.append("%s (%s)" % (os.path.basename(p), err))

    with_data = [(n, r) for n, r in reports if "unconverted_count" in r]
    corpora = sorted({str(r.get("corpus") or n.replace("-summary.json", ""))
                      for n, r in reports})
    # WHERE WE LOOKED goes to the console, not into the artifact. It is a
    # property of the INVOCATION (which --census roots were passed), not of the
    # evidence, and a field that changes with the command line would make the
    # staleness check fire on nothing -- which is how a real check becomes an
    # ignored one.
    probe = {"roots_walked": walked, "roots_missing": missing,
             "reports_unreadable": unreadable}
    src = {"available": bool(with_data),
           "reports_found": n_all,
           "reports_read": len(reports),
           "reports_unreadable": len(unreadable),
           "reports_with_survivor_data": len(with_data),
           "corpora": corpora,
           "source_documents": sum(int(r.get("total") or 0) for _n, r in reports),
           "classes_queried": len(classes)}
    if not with_data:
        return None, src, probe

    out = {}
    for cls in sorted(classes):
        total, per = 0, {}
        for _n, r in with_data:
            tbl = r.get("unconverted_by_class") or {}
            if not isinstance(tbl, dict):
                tbl = {}
            n = int(tbl.get(cls) or 0)
            if n:
                per[str(r.get("corpus") or "?")] = n
            total += n
        out[cls] = {"survivors": total, "by_corpus": per}
    return out, src, probe


# AN EMISSION MEANS THE OPPOSITE FOR A CLASS THAT IS SUPPOSED TO DISAPPEAR.
#
# `emitted_class` says a migrator MINTS documents of this class. For a class the
# decision KEEPS, that is the build landing (`control_stimulus_ids.m` minting
# `control_designation`). For a class the decision RETIRES, the same fact is
# evidence the change has NOT landed -- and counting it as progress would invert
# the number, which is exactly what this file already records happening to
# `session_relative_reference` the first time the migrator scan was written.
#
# Nothing derivable separates the two. Both are `disposition: in_progress`;
# both are named as decided targets in `V_eta_migration_targets.json` (which
# still lists `session_relative_reference` as the target of 40+ sources, written
# before the time model collapsed it -- an open question, not a fact this tool
# may settle). So the distinction is written here, TRANSCRIBED FROM THE SIGNED
# DECISION, with the quote that licenses each entry. This is not a disposition:
# the disposition is the sign-off line in the plan document, and adding one is
# the team's job (operating rule 4). It is the board declining to read a
# retirement as a build.
#
# Entries are CHECKED: the replacement must exist in the built schema set, so a
# typo or a renamed replacement fails loudly instead of silently discounting a
# class forever.
RETIRED_BY_ITS_OWN_DECISION = {
    # V_eta_time_reference_model_plan.md:468 --
    #   "TEAM-SIGN-OFF [time_reference]: ... 8 classes collapse to
    #    absolute_reference + relative_reference ..."
    # Three of the eight are minted today -- session_relative_reference,
    # session_bounded_reference and epoch_bounded_reference -- and every site is
    # work the collapse has still to undo.
    #
    # NO LINE NUMBERS HERE, DELIBERATELY. This comment used to carry four
    # (`ontology_table_row.m:262/:669`, `private/jSessionAnchor.m:19`,
    # `treatment_transfer.m:101`), and on 2026-08-11 not one of them was a mint
    # any more: :262 is a scale-field struct, :669 is an `end`, and the other
    # two are comments. A hand-written citation in a source file is the one
    # thing in this pipeline nothing regenerates, so it goes stale silently
    # while the artifact beside it stays right. The live sites, with their
    # repositories, are listed in `schemas/V_eta_STATUS.md` under each class --
    # generated, and therefore correct or loudly broken.
    # FOUR ENTRIES REMOVED 2026-08-11 (#65 increment 3a):
    # `epoch_relative_reference` -> relative_reference,
    # `event_bounded_reference` -> relative_reference,
    # `event_relative_reference` -> relative_reference and
    # `utc_reference` -> absolute_reference are gone from this dict because the
    # CLASSES are gone from the built set. A discount only means anything for a
    # class that still has a board row to discount; keeping the keys made them
    # "discounted but claimed by no decision family", which
    # test_every_discounted_class_names_a_replacement_that_exists rejects --
    # correctly, since the sign-off a discount is transcribed from has to be
    # locatable through a family. The collapse they name is EXECUTED for those
    # four, not pending.
    "time_reference": "relative_reference",
    "session_bounded_reference": "relative_reference",
    "session_relative_reference": "relative_reference",
    "epoch_bounded_reference": "relative_reference",
    # V_eta_epoch_plan.md, signed 2026-08-08 -- the `epoch` ENTITY is minted and
    # `epochid` is DROPPED (the string mixin becomes an `epoch_id` EDGE on that
    # entity; `epoch_id` is a dependency name, not a class, so the replacement
    # CLASS is `epoch`). Listed to keep the rule general rather than fitted to
    # one family; it changes no state, because `epochid` reaches (b) on nine
    # CONSUMING references and is minted only as a superclass mixin anyway.
    "epochid": "epoch",
}


STATE_A = "a_nothing_built"
STATE_B = "b_built_awaiting_corpus_proof"
STATE_C = "c_corpus_zero_survivors"
STATE_U = "u_unmeasured"

OPEN_STATE_LABEL = {
    STATE_A: "(a) decided, nothing built",
    STATE_B: "(b) built, awaiting corpus proof",
    STATE_C: "(c) corpus: 0 survivors in the corpora read",
    STATE_U: "(?) UNMEASURED -- no build evidence was ever taken",
}


def open_class_state(open_work, schemas, rows, mig, mig_src, cen, cen_src):
    """Merge the two evidence halves into one derived row per open class.

    A class is BUILT when a V_eta migrator names it OR a decided target of its
    own is present in the built schema set. The second half matters because a
    family can be half-landed: `app`'s target `software` is built and shipping
    while `app` itself is still carried, and a migrator-only signal would call
    that nothing.

    A DECIDED TARGET THAT IS THE CLASS ITSELF IS NOT EVIDENCE. `projectvar`'s
    ledger row names `projectvar` as its own decided target (it passes through
    deliberately), and counting that would report every passthrough as built.
    """
    built_classes = {s["class_name"] for s in schemas}
    ledger = {r["v1_class"]: r for r in rows}
    fam_of = {m: f[0] for f in FAMILIES for m in f[1]}

    out = []
    for cls in sorted(open_work):
        row = ledger.get(cls) or {}
        decided = [t for t in (row.get("decided_targets") or []) if t != cls]
        built_t = [t for t in decided if t in built_classes]
        missing_t = [t for t in decided if t not in built_classes]

        m = (mig or {}).get(cls)
        measured = m is not None
        mfile = m.get("migrator_file") if measured else None
        n_con = m.get("n_consuming_refs", 0) if measured else 0
        con_refs = m.get("consuming_refs", []) if measured else []
        n_write = m.get("n_field_write_refs", 0) if measured else 0
        write_refs = m.get("field_write_refs", []) if measured else []
        n_named = m.get("n_named_refs", 0) if measured else 0
        named_refs = m.get("named_refs", []) if measured else []
        n_comment = m.get("n_comment_mentions", 0) if measured else 0
        comment_refs = m.get("comment_mentions", []) if measured else []
        n_mint = m.get("n_emitted_class_refs", 0) if measured else 0
        mint_refs = m.get("emitted_class_refs", []) if measured else []
        # THE SAME FIVE BUCKETS, SPLIT BY WHICH HALF OF THE V_eta PASS THEY CAME
        # FROM. A snapshot written before the batch roots existed carries no
        # `by_group`, so the fallback puts everything under the group that was
        # being read then rather than inventing a zero for either.
        by_group = (m.get("by_group") if measured else None) or {
            GROUP_MIGRATOR: {"n_consuming_refs": n_con,
                             "consuming_refs": con_refs,
                             "n_emitted_class_refs": n_mint,
                             "emitted_class_refs": mint_refs,
                             "n_field_write_refs": n_write,
                             "field_write_refs": write_refs,
                             "n_named_refs": n_named, "named_refs": named_refs,
                             "n_comment_mentions": n_comment,
                             "comment_mentions": comment_refs},
            GROUP_BATCH: {"n_consuming_refs": 0, "consuming_refs": [],
                          "n_emitted_class_refs": 0, "emitted_class_refs": [],
                          "n_field_write_refs": 0, "field_write_refs": [],
                          "n_named_refs": 0, "named_refs": [],
                          "n_comment_mentions": 0, "comment_mentions": []},
        }

        def _split(nkey):
            """`3 per-document migrator, 2 batch post-pass` -- never a bare sum."""
            return ", ".join("%d %s" % (by_group[g].get(nkey, 0), GROUP_LABEL[g])
                             for g in GROUPS if by_group[g].get(nkey, 0))

        # A MINTED CLASS IS BUILT -- unless the decision is that it stops
        # existing, in which case the mint is the work still outstanding.
        retired_to = RETIRED_BY_ITS_OWN_DECISION.get(cls)
        mint_counts = bool(n_mint) and retired_to is None
        discount = None
        if n_mint and retired_to is not None:
            discount = ("minted at %d site(s) (%s), NOT counted as build "
                        "progress: the signed decision retires this class in "
                        "favour of `%s`, so an emission is work still to undo"
                        % (n_mint, _split("n_emitted_class_refs"), retired_to))

        why = []
        if mfile:
            why.append("migrator `%s`" % mfile)
        if n_con:
            why.append("%d consuming reference(s) (%s)"
                       % (n_con, _split("n_consuming_refs")))
        if mint_counts:
            why.append("minted as a document class at %d site(s) (%s)"
                       % (n_mint, _split("n_emitted_class_refs")))
        if built_t:
            why.append("decided target(s) built: %s"
                       % ", ".join("`%s`" % t for t in built_t))
        has_build = bool(mfile or n_con or mint_counts or built_t)

        c = (cen or {}).get(cls)
        survivors = c.get("survivors") if c else None
        by_corpus = c.get("by_corpus") if c else {}

        if not measured and not built_t:
            # No migrator scan happened AND the ledger offers nothing, so this
            # class has no evidence either way. Rule 3: that is not "(a)".
            state = STATE_U
        elif not has_build:
            state = STATE_A
        elif survivors == 0:
            state = STATE_C
        else:
            state = STATE_B

        out.append({
            "class_name": cls,
            "family": fam_of.get(cls),
            "state": state,
            "state_label": OPEN_STATE_LABEL[state],
            "build_evidence": why,
            "migrator_file": mfile,
            "n_consuming_refs": n_con,
            "consuming_refs": con_refs,
            "n_emitted_class_refs": n_mint,
            "emitted_class_refs": mint_refs,
            "emission_counts_as_build": mint_counts,
            "retired_by_decision_in_favour_of": retired_to,
            "emission_discounted": discount,
            # THREE CATEGORIES, THREE COUNTS, NEVER A SUM. See the block comment
            # above `GUARD_FUNCS`: the single `n_emitting_refs` these replace
            # merged six missed mints with nine field writes under one caption.
            "n_field_write_refs": n_write,
            "field_write_refs": write_refs,
            "n_named_refs": n_named,
            "named_refs": named_refs,
            "n_comment_mentions": n_comment,
            "comment_mentions": comment_refs,
            # TWO HALVES OF ONE PASS, NEVER ONE UNDIFFERENTIATED COUNT. Every
            # bucket above is a total over both; this is the same evidence split
            # by whether it came from a per-document migrator or from a batch
            # post-pass, which are different facts about the class.
            "by_group": by_group,
            "decided_targets": decided,
            "decided_targets_built": built_t,
            "decided_targets_missing": missing_t,
            "survivors": survivors,
            "survivors_by_corpus": by_corpus,
            "build_evidence_measured": measured,
            "corpus_evidence_measured": c is not None,
        })
    return {"sources": {"migrator": mig_src, "census": cen_src},
            "state_labels": OPEN_STATE_LABEL,
            "counts": {k: sum(1 for r in out if r["state"] == k)
                       for k in OPEN_STATE_LABEL},
            "classes": out}


def committed_snapshot():
    """The `open_class_state` block already committed in V_eta_decisions.json."""
    try:
        with open(DECISIONS_OUT) as fh:
            return json.load(fh).get("open_class_state") or {}
    except (OSError, ValueError):
        return {}


def gather_evidence(open_work, schemas, rows, args, log):
    """Measure what is reachable; fall back to the committed snapshot otherwise.

    The fallback is what makes `--check` runnable in a CI job that checks out
    only this repo. It is a CACHE, so it is announced on stdout every time and
    never silently: `log` gets one line per half saying MEASURED or REUSED.
    """
    snap = committed_snapshot()
    snap_rows = {r["class_name"]: r for r in snap.get("classes", [])}
    snap_src = snap.get("sources", {})

    mig, mig_src = migrator_evidence(open_work, args.did, args.ndi)
    if mig is None:
        prior = {c: {"migrator_file": r.get("migrator_file"),
                     "n_consuming_refs": r.get("n_consuming_refs", 0),
                     "consuming_refs": r.get("consuming_refs", []),
                     "n_emitted_class_refs": r.get("n_emitted_class_refs", 0),
                     "emitted_class_refs": r.get("emitted_class_refs", []),
                     "n_field_write_refs": r.get("n_field_write_refs", 0),
                     "field_write_refs": r.get("field_write_refs", []),
                     "n_named_refs": r.get("n_named_refs", 0),
                     "named_refs": r.get("named_refs", []),
                     "n_comment_mentions": r.get("n_comment_mentions", 0),
                     "comment_mentions": r.get("comment_mentions", []),
                     "by_group": r.get("by_group")}
                 for c, r in snap_rows.items()
                 if r.get("build_evidence_measured")}
        if prior:
            mig = prior
            mig_src = snap_src.get("migrator", mig_src)
            log.append("migrator evidence: REUSED from the committed snapshot "
                       "(%d class(es)); no V_eta migrator package under %s or %s"
                       % (len(prior), args.did, args.ndi))
        else:
            log.append("migrator evidence: UNAVAILABLE and never snapshotted "
                       "(looked under %s and %s). Every open class renders as "
                       "UNMEASURED." % (args.did, args.ndi))
    else:
        log.append("migrator evidence: MEASURED -- %d file(s), %d line(s), "
                   "package(s) %s" % (mig_src["files_read"], mig_src["lines_read"],
                                      ", ".join(mig_src["packages_read"]) or "none"))

    cen, cen_src, probe = census_evidence(open_work, args.census)
    log.append("census roots: %d walked, %d missing (%s)"
               % (probe["roots_walked"], len(probe["roots_missing"]),
                  ", ".join(probe["roots_missing"]) or "none"))
    if cen is None:
        prior = {c: {"survivors": r.get("survivors"),
                     "by_corpus": r.get("survivors_by_corpus", {})}
                 for c, r in snap_rows.items()
                 if r.get("corpus_evidence_measured")}
        if prior:
            cen = prior
            cen_src = snap_src.get("census", cen_src)
            log.append("census evidence: REUSED from the committed snapshot "
                       "(%d class(es))" % len(prior))
        else:
            log.append("census evidence: NONE -- %d report(s) read, %d carried "
                       "an `unconverted_count`. State (c) is UNPROVABLE in this "
                       "run and no class is rendered as corpus-proven."
                       % (cen_src["reports_read"],
                          cen_src["reports_with_survivor_data"]))
    else:
        log.append("census evidence: MEASURED -- %d report(s) with survivor data "
                   "over %d document(s), corpora: %s"
                   % (cen_src["reports_with_survivor_data"],
                      cen_src["source_documents"],
                      ", ".join(cen_src["corpora"]) or "none"))

    return open_class_state(open_work, schemas, rows, mig, mig_src, cen, cen_src)


def render_open_state(p, ocs):
    """Render the derived open-class table. DENOMINATOR FIRST, unconditionally."""
    msrc = ocs["sources"]["migrator"]
    csrc = ocs["sources"]["census"]
    counts = ocs["counts"]
    rowsv = ocs["classes"]

    p("## What is actually left on the %d open classes" % len(rowsv))
    p("")
    p("`in_progress` is a HAND-WRITTEN DECLARATION: every one of these classes is")
    p("open because its name is a literal in `_DECIDED_PENDING` / `_IN_PROGRESS` in")
    p("`tools/build_v_eta.py`, and it leaves the list only when a person deletes")
    p("that line. Nothing about a landed migrator, a passing test or a green corpus")
    p("moves it. The table below does not change that membership -- only the team")
    p("decides a disposition -- it DERIVES, per class, how far the work has got.")
    p("")
    p("### The measurement and its denominator")
    p("")
    p("| evidence source | reach |")
    p("|---|---|")
    _pkg_by_group = msrc.get("packages_by_group") or {}
    _files_by_group = msrc.get("files_read_by_group") or {}
    _lines_by_group = msrc.get("lines_read_by_group") or {}
    _mint_by_group = msrc.get("classes_emitted_as_document_class_by_group") or {}
    _unres_by_group = msrc.get("n_unresolved_mint_sites_by_group") or {}
    p("| build: V_eta migrator packages read | %s |"
      % (", ".join("`%s`" % s for s in msrc.get("packages_read") or []) or "**NONE**"))
    for _g in GROUPS:
        p("| build: &nbsp;&nbsp;-- of those, %s | %s |"
          % (GROUP_LABEL[_g],
             ", ".join("`%s`" % s for s in _pkg_by_group.get(_g) or [])
             or "**NONE**"))
    p("| build: migrator files inspected | %d |" % msrc.get("files_read", 0))
    for _g in GROUPS:
        p("| build: &nbsp;&nbsp;-- of those, %s | %d |"
          % (GROUP_LABEL[_g], _files_by_group.get(_g, 0)))
    p("| build: V_zeta files DELIBERATELY EXCLUDED (`%s`) | %d |"
      % ("`, `".join(msrc.get("v_zeta_packages_excluded") or []),
         msrc.get("n_files_excluded_v_zeta", 0)))
    p("| build: migrator lines inspected | %d |" % msrc.get("lines_read", 0))
    for _g in GROUPS:
        p("| build: &nbsp;&nbsp;-- of those, %s | %d |"
          % (GROUP_LABEL[_g], _lines_by_group.get(_g, 0)))
    p("| build: classes queried | %d |" % msrc.get("classes_queried", 0))
    p("| build: open classes MINTED as a document class | %d |"
      % msrc.get("classes_emitted_as_document_class", 0))
    for _g in GROUPS:
        # NOT "of those" -- a class minted in both halves is in both rows, so
        # these two do not sum to the line above and must not read as if they
        # did. Two overlapping facts, stated as two.
        p("| build: &nbsp;&nbsp;-- open classes minted in a %s (rows overlap) "
          "| %d |" % (GROUP_LABEL[_g], _mint_by_group.get(_g, 0)))
    p("| build: of those, discounted (decision retires the class) | %d |"
      % sum(1 for r in rowsv if r.get("emission_discounted")))
    p("| build: `document_class` writes whose class name is a VARIABLE | %d |"
      % msrc.get("n_unresolved_mint_sites", 0))
    for _g in GROUPS:
        p("| build: &nbsp;&nbsp;-- of those, in a %s | %d |"
          % (GROUP_LABEL[_g], _unres_by_group.get(_g, 0)))
    p("| corpus: `*-summary.json` reports read | %d |" % csrc.get("reports_read", 0))
    p("| corpus: reports carrying an `unconverted_count` | %d |"
      % csrc.get("reports_with_survivor_data", 0))
    p("| corpus: documents behind those reports | %d |"
      % csrc.get("source_documents", 0))
    p("| corpus: corpora named | %s |"
      % (", ".join("`%s`" % c for c in csrc.get("corpora") or []) or "**NONE**"))
    p("")
    if not msrc.get("available") and not msrc.get("files_read"):
        p("**NO MIGRATOR PACKAGE WAS READ.** The build column below is not clean;")
        p("it is UNMEASURED. Re-run with `--did /path/to/DID-matlab`.")
        p("")
    if not csrc.get("reports_with_survivor_data"):
        p("**NO CORPUS SURVIVOR DATA.** %d report(s) were read and %d of them carry"
          % (csrc.get("reports_read", 0),
             csrc.get("reports_with_survivor_data", 0)))
        p("an `unconverted_count`, so **state (c) cannot be reached by any class in**")
        p("**this run** and none is rendered as corpus-proven. A report without that")
        p("key measured nothing; its silence is not a zero. Point `--census` at a")
        p("directory of corpus reports, or run the DID-matlab corpus gate.")
        p("")
    p("### Where the %d open classes sit" % len(rowsv))
    p("")
    p("| state | classes |")
    p("|---|---|")
    for k in (STATE_A, STATE_B, STATE_C, STATE_U):
        p("| %s | %d |" % (OPEN_STATE_LABEL[k], counts.get(k, 0)))
    p("")
    p("**(c) IS EVIDENCE, NOT A DISPOSITION.** 0 survivors is a fact about the")
    p("corpora that were read, and it may not be promoted to `retire` on its own:")
    p("the corpora are a SAMPLE of datasets, not the universe, and the reports carry")
    p("no per-class SOURCE denominator -- `by_class` counts OUTPUT names, so a class")
    p("fully consumed and a class with no documents at all both read as zero. Only")
    p("the team flips a disposition.")
    p("")
    p("### A REFERENCE IS CLASSIFIED BEFORE IT COUNTS")
    p("")
    p("Two kinds of reference make a class (b), and they answer different")
    p("questions.")
    p("")
    p("**CONSUMED** -- a migrator file named after it, an `isfield(preBody,")
    p("'<class>')` / `strcmp(classNameOf(s), '<class>')` guard, or a read of")
    p("`preBody.<class>`. That is evidence about a v1 SOURCE: something eats it.")
    p("")
    p("**MINTED** -- the migrator sets a document's class. That is evidence about")
    p("a V_eta TARGET: something builds it. The scan could not see this at all")
    p("until 2026-08-10, and the cost was concrete: `control_designation`")
    p("rendered as *decided, nothing built* while")
    p("`DID-matlab:migrators_j/control_stimulus_ids.m:111` was minting it -- no")
    p("file is named after the target of a rename, so a filename key can never")
    p("find one.")
    p("")
    p("### THE V_eta PASS HAS TWO HALVES AND THE BOARD READ ONE")
    p("")
    p("Corrected 2026-08-11. The DID-side V_eta pass is `+migrators_j` (one file")
    p("per v1 class, each seeing ONE document) **and** the BATCH POST-PASSES that")
    p("run over the whole converted batch afterwards and do what a single-document")
    p("migrator provably cannot -- mint an epoch, resolve a session anchor, fold")
    p("the deferred baths. Those live one directory UP, in `+did2/+convert` itself")
    p("and in its `+entities/` and `+readers/` helper packages, and the scan roots")
    p("did not name them. Re-derived census of `+did2/+convert`:")
    p("")
    p("| files | where | this board |")
    p("|---|---|---|")
    p("| 125 | `+migrators_j` | scans, always did |")
    p("| 38 | `+migrators` (22) + `+migrators_i` (9) + `+migrators_e` (7) | "
      "EXCLUDED, deliberately -- the V_zeta path |")
    p("| 24 | 14 in `+convert`, 7 in `+entities/`, 3 in `+readers/` | "
      "**ADDED 2026-08-11 -- previously invisible** |")
    p("| 187 | total `.m` under `+did2/+convert` | |")
    p("")
    p("The 38 stay out: a V_zeta migrator is not evidence a V_eta target is")
    p("built. That exclusion is now COUNTED in the denominator table above rather")
    p("than left as an omission from a list -- an exclusion nobody can see in the")
    p("output is indistinguishable from a root somebody forgot, which is exactly")
    p("how the 24 went missing.")
    p("")
    p("**THE TWO GROUPS ARE NEVER MERGED INTO ONE COUNT.** Every column below is")
    p("carried per group as well as in total, because *a batch post-pass mints")
    p("this class* and *a per-document migrator mints this class* are different")
    p("facts. Each site names its repository AND its package, so the group is")
    p("readable off any citation: `DID-matlab:convert/resolveDeferredBaths.m:177`")
    p("is a batch post-pass, `DID-matlab:migrators_j/fitcurve.m:139` is not.")
    p("")
    p("**THERE ARE THREE MINT IDIOMS AND UNTIL 2026-08-11 THIS BOARD KNEW ONE.**")
    p("")
    _idiom_shape = {
        "1": "`b.document_class = struct('class_name', '<class>', ...)`",
        "2": "`b.document_class = classBlock('<class>', {supers})`",
        "3": "`b.document_class.class_name = '<class>';`",
    }
    _by_idiom = msrc.get("mint_sites_by_idiom") or {}
    _idiom_by_group = msrc.get("mint_sites_by_idiom_by_group") or {}
    p("| idiom | shape | sites | %s |"
      % " | ".join(GROUP_LABEL[g] for g in GROUPS))
    p("|---|---|---|%s" % ("---|" * len(GROUPS)))
    for _k in sorted(set(_idiom_shape) | set(_by_idiom)):
        p("| %s | %s | %d | %s |"
          % (_k, _idiom_shape.get(_k, "*unrecognised*"), _by_idiom.get(_k, 0),
             " | ".join(str((_idiom_by_group.get(g) or {}).get(_k, 0))
                        for g in GROUPS)))
    p("| - | class name is a VARIABLE -- unresolved here | %d | %s |"
      % (msrc.get("n_unresolved_mint_sites", 0),
         " | ".join(str(_unres_by_group.get(g, 0)) for g in GROUPS)))
    p("")
    p("**THE THREE IDIOMS ARE RE-MEASURED IN THE NEW ROOTS, NOT ASSUMED TO CARRY")
    p("OVER.** The per-group columns are counted per file, so which idioms the")
    p("batch post-passes actually use is read off the table rather than asserted")
    p("in a sentence that can go stale; a zero there is a measured zero over the")
    p("file and line denominators above, and if a post-pass adopts `classBlock`")
    p("tomorrow the column moves on its own.")
    p("")
    p("Idioms 2 and 3 carry no `'class_name', '<X>'` comma pair, so the regex")
    p("imported from `tools/coverage.py` cannot see them. `classBlock` is a LOCAL")
    p("SUBFUNCTION, redefined in eight files with two different arities, and it is")
    p("recognised HERE BY ITS SHAPE, not its name: a local function that assigns")
    p("its own output a struct declaring `superclasses` whose `class_name` comes")
    p("from one of its parameters. The literal is then read from that parameter's")
    p("INDEX at each call site, so the superclass argument beside it cannot be")
    p("mistaken for a mint.")
    p("")
    _srr = next((r for r in rowsv
                 if r["class_name"] == "session_relative_reference"), None)
    p("**WHAT THE MISS COST, stated as the number and not as a lesson.**")
    p("`session_relative_reference` is a class whose whole open question is that")
    p("it must STOP being emitted. Idiom 1 in `+migrators_j` alone puts its mint")
    p("count at **3**; this run measures **%s**"
      % (_srr["n_emitted_class_refs"] if _srr else "n/a -- no longer open"))
    if _srr:
        _srr_g = _srr.get("by_group") or {}
        p("(%s)."
          % ("; ".join("%d in a %s"
                       % ((_srr_g.get(g) or {}).get("n_emitted_class_refs", 0),
                          GROUP_LABEL[g]) for g in GROUPS)))
    p("Two corrections got it there, and they are separate faults. Six migrators")
    p("(`fitcurve`, `image_stack`, `jrclust_clusters`, `neuron_extracellular`,")
    p("`pyraview`, `vmspikefit`) mint it through `classBlock`, which the")
    p("`'class_name'`-comma regex could not see; and the batch post-pass")
    p("`+convert/resolveDeferredBaths.m` mints it twice in a package the board")
    p("was not reading at all. The board reported a third of the outstanding")
    p("work, in this project's characteristic direction. Neither set was dropped")
    p("-- the six were filed as `named`, the weakest bucket, and the two were")
    p("filed nowhere, which is worse than dropping them because the first looks")
    p("like a measurement and the second looks like clean ground.")
    p("")
    p("**A `document_class` WRITE WHOSE CLASS NAME IS A VARIABLE IS COUNTED, NOT")
    p("SKIPPED.** `struct('class_name', leafClass, ...)` and")
    p("`classBlock(e.class, ...)` need the CALL GRAPH to resolve, which is")
    p("`tools/refresh_migration_targets.py`'s job, not this per-file scan's. Those")
    p("sites appear in the denominator table above. The mint counts in this")
    p("artifact are therefore a FLOOR.")
    p("")
    _unres = msrc.get("unresolved_mint_sites") or []
    if _unres:
        p("| unresolved `document_class` write | class name expression |")
        p("|---|---|")
        for _s in _unres:
            _site, _, _expr = _s.rpartition(" (")
            p("| `%s` | `%s` |" % (_site, _expr.rstrip(")")))
        p("")
    p("**THE OTHER CATEGORIES ARE REPORTED SEPARATELY AND ARE NEVER SUMMED.** A")
    p("migrator that WRITES a block of that name (`x.<class> = ...`), one that")
    p("merely NAMES it as a string value, and one that MENTIONS it in a comment")
    p("are three different facts, and a single cell reading *still emitted/named")
    p("at N site(s)* merged them. It also swallowed the six missed mints above.")
    p("Each now has its own column and its own count; comment mentions count")
    p("toward nothing and are shown so that can be checked rather than believed.")
    p("")
    p("**A MINT IS DISCOUNTED WHEN THE DECISION RETIRES THE CLASS.** For a class")
    p("whose signed decision is that it stops existing, minting it is the work")
    p("still outstanding, not progress -- so `session_relative_reference` and its")
    p("family stay where they are however many sites emit them. The list is")
    p("transcribed from the sign-off lines in")
    p("`tools/status_board.py:RETIRED_BY_ITS_OWN_DECISION`, and every replacement")
    p("named there is checked to exist. Note this is an OPEN CONTRADICTION between")
    p("two committed records, not a settled fact: `V_eta_migration_targets.json`")
    p("still lists `session_relative_reference` as a decided target of 40+ v1")
    p("sources, written before the time model collapsed it. The board takes the")
    p("under-reporting side and does not settle it.")
    p("")
    p("**The `decided target(s) built` signal is the WEAKER of the two** and is")
    p("marked separately for that reason. A decided target can be a class that")
    p("already existed for other reasons -- `ensemble` reaches (b) on `subject`,")
    p("`directed_relation` and `sampled_body`, none of which was built for it. Read")
    p("a row whose only evidence is a built target as *the target exists*, not as")
    p("*the work is done*.")
    p("")
    p("Each of the last four columns is one kind of fact and they are NOT added")
    p("together. `minted` = a document of this class is produced; `field writes`")
    p("= a block of that name is written; `named` = the name appears as a string")
    p("value; `comments` = prose, which counts toward nothing. Each cell is")
    p("written `total (M+B)` -- M from a per-document migrator, B from a batch")
    p("post-pass -- so no cell in this table is an undifferentiated count.")
    p("")
    p("| class | family | state | build evidence | minted (M+B) | field writes "
      "(M+B) | named (M+B) | comments (M+B) | survivors |")
    p("|---|---|---|---|---|---|---|---|---|")

    def _cell(r, nkey):
        """`9 (7+2)` -- the total, then the migrator/batch split. Never one number."""
        total = r.get(nkey) or 0
        if not total:
            return "-"
        g = r.get("by_group") or {}
        return "%d (%s)" % (total, "+".join(
            str((g.get(grp) or {}).get(nkey, 0)) for grp in GROUPS))

    for r in rowsv:
        surv = ("n/a -- not measured" if r["survivors"] is None
                else str(r["survivors"]))
        ev = "; ".join(r["build_evidence"]) or ("*not measured*"
                                                if not r["build_evidence_measured"]
                                                else "*none*")
        mint_cell = _cell(r, "n_emitted_class_refs")
        if r.get("emission_discounted") and mint_cell != "-":
            mint_cell += " discounted"
        p("| `%s` | %s | %s | %s | %s | %s | %s | %s | %s |"
          % (r["class_name"], r["family"] or "-",
             OPEN_STATE_LABEL[r["state"]].split(" ", 1)[0], ev,
             mint_cell, _cell(r, "n_field_write_refs"),
             _cell(r, "n_named_refs"), _cell(r, "n_comment_mentions"),
             surv))
    p("")
    for k in (STATE_A, STATE_U, STATE_C, STATE_B):
        members = [r for r in rowsv if r["state"] == k]
        if not members:
            continue
        p("#### %s -- %d" % (OPEN_STATE_LABEL[k], len(members)))
        p("")
        for r in members:
            bits = []
            grp = r.get("by_group") or {}

            def _per_group(_n, _refs, _caption, _row=r, _grp=grp):
                """One caption PER GROUP, never one caption over both.

                A site in `+convert/resolveDeferredBaths.m` and a site in
                `+migrators_j/fitcurve.m` say different things about a class --
                the batch pass builds it versus the per-document pass does --
                and this file has already paid once for a caption that summed
                unlike facts into one number.
                """
                said = []
                for g in GROUPS:
                    gr = _grp.get(g) or {}
                    n = gr.get(_n, 0)
                    if not n:
                        continue
                    cited = gr.get(_refs, [])
                    said.append(("%s, %s" % (_caption % n, GROUP_LABEL[g]))
                                + ": %s%s"
                                % (", ".join("`%s`" % x for x in cited),
                                   " ..." if n > len(cited) else ""))
                if said:
                    return said
                # No per-group breakdown at all (a snapshot older than the
                # split). Report the total and say it is not split, rather than
                # silently printing a group's worth of evidence as if it were
                # one group's.
                n = _row.get(_n) or 0
                if not n:
                    return []
                cited = _row.get(_refs, [])
                return [("%s, group NOT RECORDED in this snapshot: %s%s"
                         % (_caption % n,
                            ", ".join("`%s`" % x for x in cited),
                            " ..." if n > len(cited) else ""))]

            if r["migrator_file"]:
                bits.append("migrator `%s`" % r["migrator_file"])
            bits.extend(_per_group("n_consuming_refs", "consuming_refs",
                                   "consumed at %d site(s)"))
            bits.extend(_per_group("n_emitted_class_refs", "emitted_class_refs",
                                   "MINTED as a document class at %d site(s)"))
            if r.get("emission_discounted"):
                bits.append(r["emission_discounted"])
            # ONE CAPTION PER CATEGORY. The single "still emitted/named at N
            # site(s)" line these three replace merged mints the scan had
            # misfiled, block writes and string values into one number.
            for _n, _refs, _caption in (
                    ("n_field_write_refs", "field_write_refs",
                     "a block of this name is WRITTEN at %d site(s)"),
                    ("n_named_refs", "named_refs",
                     "NAMED as a string value at %d site(s)"),
                    ("n_comment_mentions", "comment_mentions",
                     "mentioned in %d COMMENT(s) -- prose, counts toward "
                     "nothing")):
                bits.extend(_per_group(_n, _refs, _caption))
            if r["decided_targets_built"]:
                bits.append("target(s) BUILT: %s"
                            % ", ".join("`%s`" % t
                                        for t in r["decided_targets_built"]))
            if r["decided_targets_missing"]:
                bits.append("target(s) NOT built: %s"
                            % ", ".join("`%s`" % t
                                        for t in r["decided_targets_missing"]))
            if r["survivors"]:
                bits.append("survivors %d (%s)"
                            % (r["survivors"],
                               ", ".join("%s %d" % kv for kv in
                                         sorted(r["survivors_by_corpus"].items()))))
            p("- `%s` (%s) -- %s"
              % (r["class_name"], r["family"] or "no family",
                 "; ".join(bits) or "no evidence found"))
        p("")


def open_class_names(schemas):
    """The `in_progress` set, computed once so build() and the evidence layer
    cannot disagree about what "open" means."""
    return {s["class_name"] for s in schemas
            if s.get("disposition") == "in_progress"}


def build(ocs=None):
    schemas, rows = load()

    # RETIRE IS NOT ALWAYS A DECISION. A row marked retire with NO migrator and NO
    # recorded `how` means the documents pass through untouched and nobody has
    # decided anything -- open work wearing a settled label. The board could not
    # see it because it counted only `in_progress`. Found when
    # spike_extraction_parameters turned out to hold filter_type / filter_low /
    # filter_high / filter_order / filter_ripple -- exactly the data the
    # frequency_filter model was just designed for -- while sitting outside every
    # decision family.
    #
    # Computed HERE, before anything renders: the first attempt built it down in
    # the ledger section and the header referenced it earlier in the same
    # function, which raised UnboundLocalError. A summary line must not depend on
    # a number computed after it.
    unplanned_retire = sorted(
        r["v1_class"] for r in rows
        if r["disposition"] == "retire" and not r["migrator"]
        and not (r.get("how") or "").strip())
    by_disp = {}
    for s in schemas:
        by_disp.setdefault(s.get("disposition", "(none)"), []).append(s["class_name"])
    open_classes = set(by_disp.get("in_progress", []))

    # THE CHECK: every open class must be claimed by exactly one family.
    claimed, dupes = set(), []
    for fam in FAMILIES:
        members = fam[1]
        for m in members:
            if m in claimed:
                dupes.append(m)
            claimed.add(m)
    # Open work is in_progress PLUS retire-with-no-plan. Before this, a family
    # claiming a retire row was reported as stale and the row stayed invisible.
    open_work = open_classes | set(unplanned_retire)
    unclaimed = sorted(open_work - claimed)
    stale = sorted(claimed - open_work)

    # A family may only claim to be DECIDED if the document recording that
    # decision exists. Otherwise "decided, awaiting build" is the same kind of
    # unbacked assertion this board replaces.
    missing_plans = [(f[0], f[2]) for f in FAMILIES
                     if f[2] and not os.path.exists(os.path.join(REPO, "schemas", f[2]))]

    L = []
    p = L.append
    p("# V_eta status board (GENERATED -- do not hand-edit)")
    p("")
    p("Regenerate with `python3 tools/status_board.py`. CI runs `--check`.")
    p("")
    p("State lives here. The plan documents under `schemas/` keep the RATIONALE")
    p("for each model; this board owns *how much is left and what exactly*.")
    p("")

    if unclaimed:
        p("## ERROR -- unclaimed open classes")
        p("")
        p("These are `in_progress` but belong to no decision family in")
        p("`tools/status_board.py`. An open class that no family claims is an open")
        p("question nobody is tracking. Add it to `FAMILIES` before continuing:")
        p("")
        for c in unclaimed:
            p("- `%s`" % c)
        p("")

    total = len(schemas)
    n_open = len(open_classes)
    n_persist = len(by_disp.get("persist", []))
    n_retire = len(by_disp.get("retire", []))
    # Index 2 is the plan document; index 1 is the member LIST, which is always
    # truthy. Getting this wrong reported every family as decided and printed an
    # empty "genuinely undecided" table -- a status board that says the work is
    # done is worse than no status board.
    # Tuple is (name, members, plan, question, status) -- status is index 4.
    # Indexed [3] on the first attempt and every count rendered 0, which is how
    # a status board lies quietly. Guarded below so an unknown status is loud.
    # A "team" claim is only honoured when the cited document carries the
    # sign-off line. Otherwise it is a proposal, whatever the table says.
    decided   = [f for f in FAMILIES if f[4] == "team" and has_signoff(f[2], f[0])]
    unsigned  = [f for f in FAMILIES if f[4] == "team" and not has_signoff(f[2], f[0])]
    proposed  = [f for f in FAMILIES if f[4] == "proposed"]
    undecided = [f for f in FAMILIES if f[4] == "open"]
    # A FAMILY MUST NOT CLAIM A CLASS THAT NO LONGER EXISTS. The check below has always
    # verified that every in_progress class belongs to a family; it never verified the
    # converse, so when three classes collapsed into one on 2026-08-06 the board went on
    # rendering "demo / mock | 2 | PASSTHROUGH ..." -- a stale one-liner about a
    # superseded model, listing two ghosts, and --check passed. A generated artifact that
    # looks current and is not is the exact failure this file exists to prevent.
    # A family may legitimately claim a class by its did_v1 LEDGER name rather
    # than its built-index name, and the two differ whenever NDI spells it in
    # camelCase: `imageStack_parameters` in the ledger is `image_stack_parameters`
    # in the index. The unclaimed-work check below draws retire-with-no-migrator
    # rows straight from the ledger, so it demands the v1 spelling -- while this
    # check demanded the index spelling, and no name could satisfy both. It first
    # bit when image_stack came back out of _DELETE_PHASE8; before that every
    # unplanned-retire row happened to be spelled identically in both places.
    # Accept either, so a family can claim the thing the board is asking it to.
    known = {e["class_name"] for e in schemas}
    known |= {r["v1_class"] for r in rows}

    # A DISCOUNT MUST NAME A REAL REPLACEMENT. `RETIRED_BY_ITS_OWN_DECISION`
    # suppresses build credit, so a typo or a since-renamed replacement would
    # hold a class at "(a) nothing built" forever, silently and in the direction
    # this board exists to stop -- the exact shape of the ledger's "dissolved
    # (rename/decompose)" labels. Fail loudly instead.
    built_now = {e["class_name"] for e in schemas}
    bad_repl = sorted((c, t) for c, t in RETIRED_BY_ITS_OWN_DECISION.items()
                      if t not in built_now)
    if bad_repl:
        sys.stderr.write(
            "status_board: RETIRED_BY_ITS_OWN_DECISION names %d replacement "
            "class(es) that are not in the built index: %s\n"
            "Each entry discounts a migrator's emission, so a stale name pins "
            "its class at 'nothing built' with no way to notice.\n"
            % (len(bad_repl), ", ".join("%s -> %s" % cr for cr in bad_repl)))
        sys.exit(1)

    ghosts = sorted({m for f in FAMILIES for m in f[1] if m not in known})
    if ghosts:
        sys.stderr.write(
            "FAMILIES claims %d class(es) that are not in the built index: %s\n"
            "A collapsed or deleted class must be removed from its family (or the "
            "family closed).\n" % (len(ghosts), ", ".join(ghosts)))
        sys.exit(1)

    bad_status = [f[0] for f in FAMILIES
                  if f[4] not in ("team", "proposed", "open")]
    if len(decided) + len(unsigned) + len(proposed) + len(undecided) != len(FAMILIES):
        raise SystemExit(
            "status_board: %d families but %d classified -- unclassified: %s"
            % (len(FAMILIES), len(decided) + len(unsigned) + len(proposed) + len(undecided),
               bad_status))

    p("## Where V_eta stands")
    p("")
    p("| | count |")
    p("|---|---|")
    p("| target classes | %d |" % total)
    p("| settled (persist) | %d |" % n_persist)
    p("| settled (retire) | %d |" % n_retire)
    p("| **still open (`in_progress`)** | **%d** |" % n_open)
    p("| **`retire` with no migrator YET** | **%d** |" % len(unplanned_retire))
    p("| open **decision families** | **%d** |" % len(FAMILIES))
    p("| &nbsp;&nbsp;DECIDED and signed off, awaiting build | %d |" % len(decided))
    p("| &nbsp;&nbsp;decided in a walkthrough, **awaiting a signature** | %d |" % len(unsigned))
    p("| &nbsp;&nbsp;**written up by Claude alone, unreviewed** | **%d** |" % len(proposed))
    p("| &nbsp;&nbsp;nobody has proposed anything yet | %d |" % len(undecided))
    p("")
    if ocs:
        c = ocs["counts"]
        p("| open-class BUILD/PROOF state (derived, see below) | count |")
        p("|---|---|")
        for k in (STATE_A, STATE_B, STATE_C, STATE_U):
            p("| %s | %d |" % (OPEN_STATE_LABEL[k], c.get(k, 0)))
        p("")
    p("The class count is not the work count. %d open classes are %d decisions, "
      "because most open classes move as a family." % (n_open, len(FAMILIES)))
    p("")
    p("**%d of those %d are not settled**: %d awaiting a signature on a decision "
      "already taken, %d written up by Claude alone and unreviewed, %d with "
      "nothing proposed. Only %d are signed off."
      % (len(unsigned) + len(proposed) + len(undecided), len(FAMILIES),
         len(unsigned), len(proposed), len(undecided), len(decided)))
    p("")

    # THE DERIVED HALF. Everything above this line is computed from committed
    # artifacts and from the FAMILIES table; everything in here is measured
    # against the migrator packages and the corpus census, or says it was not.
    if ocs:
        render_open_state(p, ocs)

    p("## AWAITING A SIGNATURE -- decided with the team, not yet recorded")
    p("")
    p("These were settled in walkthroughs. They are not built and do not render as")
    p("decided because no document carries the sign-off line yet. Nothing here needs")
    p("re-deciding -- it needs recording.")
    p("")
    p("| family | classes | what was decided | document |")
    p("|---|---|---|---|")
    for name, members, plan, what, _ in unsigned:
        p("| **%s** | %d | %s | `%s` |" % (name, len(members), what, plan))
    p("")
    for name, members, _, _, _ in unsigned:
        p("- **%s**: %s" % (name, ", ".join("`%s`" % m for m in sorted(members))))
    p("")

    p("## WRITTEN UP BY CLAUDE ALONE -- nobody has checked the reasoning")
    p("")
    p("Each has template evidence and a written rationale, and **none of it has been")
    p("reviewed**. Counted as open work.")
    p("")
    p("To sign one off, add a line to its document:")
    p("")
    p("```")
    p("%s [<family>] <who/when> -- <what was decided>" % SIGNOFF)
    p("```")
    p("")
    p("Until that line exists the family shows here regardless of what")
    p("`tools/status_board.py` claims -- Claude cannot promote its own work.")
    p("")
    p("| family | classes | proposal | written up in |")
    p("|---|---|---|---|")
    for name, members, plan, what, _ in proposed:
        p("| **%s** | %d | %s | `%s` |" % (name, len(members), what, plan))
    p("")
    for name, members, _, _, _ in proposed:
        p("- **%s**: %s" % (name, ", ".join("`%s`" % m for m in sorted(members))))
    p("")

    p("## Nobody has proposed anything yet")
    p("")
    p("| family | classes | the call to make |")
    p("|---|---|---|")
    for name, members, _, question, _ in undecided:
        p("| **%s** | %d | %s |" % (name, len(members), question))
    p("")
    for name, members, _, _, _ in undecided:
        p("- **%s**: %s" % (name, ", ".join("`%s`" % m for m in sorted(members))))
    p("")

    p("## DECIDED by the team, awaiting build")
    p("")
    # THIS SECTION USED TO ASSERT "the schema has not changed yet" AS A
    # HARDCODED STRING, printed under every family regardless of the tree.
    # By 2026-08-11 it was false for essentially all of them: a hand check of
    # the 26 target classes these families name found 25 present as schema
    # files and the 26th (`execution_environment`) present as a block on
    # `subject_interaction`. The sentence would have sent a reader to rebuild
    # the entire decided set.
    #
    # It is the project's own recurring error wearing the opposite sign. The
    # usual direction is a claim that reads as MORE progress than exists; this
    # one reads as LESS, which is why it survived so long -- understating never
    # produces a wrong build, only wasted work and a board nobody can plan
    # from. Both are the same defect: prose in a GENERATED artifact stating a
    # fact that the generator never checked.
    #
    # The join it needed already existed one layer down. `open_class_state`
    # computes `decided_targets` / `_built` / `_missing` per class. All this
    # does is lift that to the family and print it, so the claim moves with
    # the tree instead of with whoever last edited the string.
    tgt_by_class = {r["class_name"]: r for r in (ocs or {}).get("classes", [])}
    # THE LEDGER, DIRECTLY, AS A SECOND SOURCE -- because the first one cannot
    # see most of these families.
    #
    # `open_class_state` is built over `open_work`, which is the `in_progress`
    # V_eta SCHEMA classes plus retire-with-no-plan. Five signed families are
    # made of v1 SOURCE rows with disposition `retire` and a migrator, so they
    # have no `open_class_state` row at all -- and `family_targets` silently
    # skipped them (`if not row: continue`). The section below then printed
    #
    #     "No member of these families carries a `decided_targets` entry in the
    #      coverage ledger"
    #
    # about eleven families, and MEASURED 2026-08-11 that sentence was FALSE
    # for five of them: all four members of `spike processing parameters` carry
    # `decided_targets: [method_parameters]`, `stimulus response` carries
    # `harmonic_component_calculation` and `method_parameters`, and
    # `stimulus parameters` / `misc singletons` carry self-targets. The record
    # was there; nothing read it. An unchecked family reported as "carries no
    # entry" is a claim about the LEDGER derived from a lookup that never
    # touched the ledger -- absence of evidence, printed as evidence.
    built_classes_now = {s["class_name"] for s in schemas}
    ledger_by_class = {r["v1_class"]: r for r in rows}

    def _decided_of(member):
        """(built, missing, source) for one family member, ledger as fallback.

        A decided target that IS the class is dropped, exactly as
        `open_class_state` drops it: a deliberate passthrough is not evidence
        that anything was built.
        """
        row = tgt_by_class.get(member)
        if row:
            return (set(row.get("decided_targets_built") or []),
                    set(row.get("decided_targets_missing") or []),
                    "open_class_state")
        led = ledger_by_class.get(member)
        if not led:
            return set(), set(), None
        dec = [t for t in (led.get("decided_targets") or []) if t != member]
        return ({t for t in dec if t in built_classes_now},
                {t for t in dec if t not in built_classes_now},
                "coverage_ledger")

    def family_targets(members):
        """(built, missing) decided-target class names across a family."""
        built_t, missing_t = set(), set()
        for m in members:
            b, mi, _src = _decided_of(m)
            built_t |= b
            missing_t |= mi
        # A target both built and missing across two members is BUILT -- the
        # file exists; the other member simply has not been re-pointed at it.
        return built_t, (missing_t - built_t)

    def family_blank_causes(members):
        """Why a family contributed nothing -- measured, not assumed.

        Three different facts, and the old prose named only one of them:
          not_a_v1_source  the member is a V_eta TARGET class, so the ledger has
                           no row for it and never will (the whole
                           `time_reference` family is this).
          no_decided       there IS a ledger row and its `decided_targets` is
                           empty -- the gap the coverage ledger now flags.
          self_only        its only decided target is itself (a signed
                           passthrough), which is stripped as non-evidence.
        """
        causes = {}
        for m in members:
            led = ledger_by_class.get(m)
            if led is None:
                causes[m] = "not_a_v1_source"
            elif [t for t in (led.get("decided_targets") or []) if t != m]:
                causes[m] = "has_decided"
            elif led.get("decided_targets"):
                causes[m] = "self_only"
            else:
                causes[m] = "no_decided"
        return causes

    if not ocs:
        # RULE 5. No denominator available means the question was not asked,
        # and that is not the same as "nothing is missing".
        p("**TARGET-BUILD STATE NOT MEASURED IN THIS RUN.** The open-class")
        p("evidence layer did not run, so this section cannot say whether these")
        p("families' target schemas exist. Read that as UNKNOWN, not as unbuilt.")
    else:
        all_built, all_missing = set(), set()
        seen, unseen = [], []
        for name, members, _, _, _ in decided:
            b, m = family_targets(members)
            all_built |= b
            all_missing |= m
            (seen if (b or m) else unseen).append(name)
        all_missing -= all_built
        n_named = len(all_built) + len(all_missing)
        # THE CHECK'S OWN COVERAGE COMES FIRST, BEFORE ITS RESULT. The first
        # version of this block printed "13 named, 13 built, 0 missing" while
        # 11 of the 18 families had contributed NOTHING to those numbers, so a
        # reassuring "0 not built" was really "0 among the families I could
        # see". A count that does not say what it failed to look at is the
        # `silentLoss` defect, and writing the fix is not a licence to repeat
        # it one layer up.
        p("**DENOMINATOR: %d signed families. %d named at least one decided "
          "target class and were checked against the built tree; %d named none "
          "and are UNCHECKED HERE.**" % (len(decided), len(seen), len(unseen)))
        p("")
        p("Across the %d checked: %d distinct target class(es), %d present in "
          "the built set, %d not." % (len(seen), n_named, len(all_built),
                                      len(all_missing)))
        p("")
        if all_missing:
            p("The classes not yet present are the schema build queue:")
            p("")
            for t in sorted(all_missing):
                p("- `%s`" % t)
            p("")
        elif n_named:
            p("So for the checked families the schema half is DONE and what")
            p("remains is MIGRATOR work. Do not read those rows as a build")
            p("queue for schema.")
            p("")
        if unseen:
            # "no target recorded" splits SEVERAL ways and the split is the
            # point. A class that DISSOLVES correctly names no target
            # (`epochid`, dropped outright). A class whose target is fixed in a
            # signed plan but was never written down is a GAP. A class whose
            # decided target is ITSELF is a signed passthrough. And a family
            # member that is a V_eta TARGET rather than a v1 source has no
            # ledger row at all. Four facts; one blank cell.
            #
            # THIS BLOCK'S OWN PROSE WAS WRONG TWICE, BOTH TIMES IN THE
            # DIRECTION OF SOUNDING BETTER MEASURED THAN IT WAS.
            #
            #   94cacb3 cited "`epochid` and `ngrid`" as the dissolutions.
            #   0eb58d9 corrected `ngrid` to a fold -> `sampled_body`, citing
            #           the plan's R4 SECTION HEADING.
            #   Measured 2026-08-11: the `TEAM-SIGN-OFF [image / ngrid]` line in
            #           that same document reads "ngrid is DISSOLVED (deleted,
            #           not migrated)" and the plan's FINAL class block reads
            #           "ngrid   DELETED". Both commits read one half of one
            #           document. `coverage.py` now renders `ngrid` as DISPUTED
            #           rather than picking a side for the team.
            #
            # And the sentence this replaces -- "No member of these families
            # carries a `decided_targets` entry in the coverage ledger" -- was
            # FALSE for five of the eleven. It described the ledger without
            # reading it; the lookup only ever touched `open_class_state`,
            # which does not cover a `retire` v1 source row. The causes below
            # are MEASURED per member, so the claim cannot outrun the check
            # again.
            p("**The other %d are unchecked, NOT clean.** Nothing above says "
              "anything about them, and the reason differs per family:"
              % len(unseen))
            p("")
            _CAUSE = {
                "not_a_v1_source":
                    "a V_eta target class, so the coverage ledger has no row "
                    "for it (it is not a v1 source)",
                "no_decided":
                    "has a ledger row whose `decided_targets` is EMPTY -- the "
                    "gap the ledger now flags by name",
                "self_only":
                    "its only decided target is ITSELF, a signed passthrough, "
                    "which is stripped because it is not build evidence",
                "has_decided":
                    "DOES carry a decided target -- if this appears here the "
                    "join is broken, not the record",
            }
            for name in unseen:
                members = next(f[1] for f in decided if f[0] == name)
                causes = family_blank_causes(members)
                buckets = {}
                for m, c in causes.items():
                    buckets.setdefault(c, []).append(m)
                p("- **%s** (%d class(es)): %s" % (
                    name, len(members),
                    "; ".join("%d %s -- %s"
                              % (len(v), ", ".join("`%s`" % x for x in sorted(v)),
                                 _CAUSE[k])
                              for k, v in sorted(buckets.items()))))
            p("")
            p("Only the `decided_targets` EMPTY bucket is a missing record. The")
            p("others are correct states that this check cannot use: a V_eta")
            p("target class has no v1 row to carry a target, and a signed")
            p("passthrough deliberately names no new class. `tools/coverage.py`")
            p("now records dissolution POSITIVELY (with the sign-off quoted) and")
            p("renders a row with neither a target nor a dissolution as an")
            p("explicit gap, so the empty bucket is enumerable rather than")
            p("indistinguishable from a settled one.")
    p("")
    p("Every one of these re-targets migrators that are already written, which")
    p("is why migrator work before the target closes is rework.")
    p("")
    p("| family | classes | targets built | decision | recorded in |")
    p("|---|---|---|---|---|")
    for name, members, plan, what, _ in decided:
        if not ocs:
            cell = "not measured"
        else:
            b, m = family_targets(members)
            n = len(b) + len(m)
            cell = "%d of %d" % (len(b), n) if n else "no target recorded"
        p("| **%s** | %d | %s | %s | `%s` |"
          % (name, len(members), cell, what, plan))
    p("")

    # ---- the family table's own prose, checked against the signatures -------
    pvs = family_prose_vs_signoff({s["class_name"] for s in schemas})
    p("## Class names the family table asserts that its sign-off does not say")
    p("")
    p("DENOMINATOR: %d signed families checked; every V_eta class name in the "
      "family one-liner above was matched against the text of the "
      "`TEAM-SIGN-OFF` line that signs that family. %d family/name pair(s) are "
      "UNSIGNED -- the prose names the class, the signature does not."
      % (pvs["families_checked"], sum(len(r[2]) for r in pvs["rows"])))
    p("")
    p("**THIS IS NOT A LIST OF ERRORS, AND NOTHING HERE IS RESOLVED BY A TOOL.**")
    p("The family one-liner is Claude-authored prose in `tools/status_board.py`;")
    p("the sign-off is the team's own words. An unsigned name may be a fair")
    p("paraphrase, a structural word used in passing (`data_type`, `entity`), or")
    p("a target nobody agreed to -- and only a person can tell which.")
    p("")
    p("It exists because on 2026-08-11 `ngrid` was filed as a dissolution,")
    p("\"corrected\" to a fold into `sampled_body`, and the correction was wrong.")
    p("Both readings came from `V_eta_image_model_plan.md`; neither reader")
    p("reached the `TEAM-SIGN-OFF [image / ngrid]` line in it, which says")
    p("\"ngrid is DISSOLVED (deleted, not migrated)\". Sweeping for the SHAPE")
    p("then found a second instance immediately -- `binaryseries_parameters`,")
    p("whose section heading says \"folds into `sampled_body`\" while its")
    p("signature routes the fields to a statement and an axis and names no")
    p("class.")
    p("")
    p("**ONE OF THE TWO IS NOW SETTLED, AND THE OTHER IS NOT.** This")
    p("paragraph said \"Both are recorded DISPUTED in the coverage ledger,")
    p("with both citations and no choice made\", and half of that went stale")
    p("the day it was written. The team ruled on 2026-08-11 that for")
    p("`binaryseries_parameters` the SIGNATURE is what is intended, so its")
    p("ledger row now records TWO decided targets -- `subject_statement` and")
    p("`sampled_body`, the two mounts the axis entry can take, selected per")
    p("document by `storage_mode`. `ngrid` is UNCHANGED and still DISPUTED:")
    p("nothing was decided about it, and the two rows only ever shared a")
    p("shape. Note that the ruling does NOT make either name a signed one --")
    p("both still appear in the table below, because the signature says \"the")
    p("statement's\" and \"the axis\", never a class name. That is the honest")
    p("state: a decided target, derived from the signature, not quoted from")
    p("it.")
    p("")
    if pvs["rows"]:
        p("| family | unsigned class name(s) in the one-liner | sign-off in |")
        p("|---|---|---|")
        for name, plan, missing in pvs["rows"]:
            p("| **%s** | %s | `%s` |"
              % (name, ", ".join("`%s`" % m for m in missing), plan))
        p("")
    else:
        p("None -- every class name in every family one-liner appears in the")
        p("signature that signs it.")
        p("")
    if pvs["multi_untagged"]:
        p("**AND: %d document(s) carry more than one UNTAGGED `TEAM-SIGN-OFF`"
          % len(pvs["multi_untagged"]))
        p("line.** An untagged line signs the document, and counts only when")
        p("exactly one family cites it -- so `find_signoff` returns the FIRST")
        p("one and the reader cannot tell which was shown. Not wrong; not")
        p("visible either.")
        p("")
        for plan, n in pvs["multi_untagged"]:
            p("- `%s` -- %d untagged sign-off lines" % (plan, n))
        p("")

    # v1 source side
    led_disp = {}
    for r in rows:
        led_disp.setdefault(r["disposition"], []).append(r["v1_class"])

    unverified = sorted(led_disp.get("no V_eta home, no migrator -- UNVERIFIED", []))
    p("## v1 source side (from the coverage ledger)")
    p("")
    p("| disposition | count |")
    p("|---|---|")
    for k in sorted(led_disp, key=lambda k: -len(led_disp[k])):
        p("| %s | %d |" % (k, len(led_disp[k])))
    p("")
    if unplanned_retire:
        # MEASURED, NOT ASSUMED -- and it caught one immediately. See the note
        # under the heading below.
        batch_hits = batch_consumers(unplanned_retire)
        p("### `retire`, but NO MIGRATOR YET -- %d rows" % len(unplanned_retire))
        p("")
        p("Marked `retire` in the ledger with **no per-class migrator and no `how`")
        p("note**. `retire` reads as settled, so these do not appear in the family")
        p("counts above -- but they are open work. Several hold real data (e.g.")
        p("`spike_extraction_parameters` carries filter_type / filter_low /")
        p("filter_high / filter_order / filter_ripple).")
        p("")
        p("**THIS PARAGRAPH SAID \"so the documents pass through untouched today\"")
        p("and that was an INFERENCE from `no migrator`, not a measurement.** The")
        p("ledger's `migrator` column means \"a file in `+migrators_j` / `+migrators`")
        p("/ `+migrators_i` is named after this class\" -- it says nothing about the")
        p("BATCH POST-PASSES in `+did2/+convert`, which consume classes no")
        p("per-class migrator touches. Measured now, per row, below.")
        p("")
        p("**This heading used to say \"nothing decided\" / \"no recorded plan\", and that")
        p("was WRONG** -- it is computed from the LEDGER (disposition + migrator + `how`),")
        p("not from whether a decision exists. Checked 2026-08-08: **every one of these")
        p("rows is covered by a plan document**, and most are signed. The list means")
        p("\"no migrator has been written yet\", not \"nobody has decided\". A board that")
        p("reports settled work as undecided is the mirror of the failure this board")
        p("exists to prevent, and it cost a review pass to notice.")
        p("")
        p("DENOMINATOR: %d row(s), each searched for its BARE CLASS NAME as a "
          "quoted literal in %d batch post-pass file(s) under `+did2/+convert` "
          "(comments stripped)%s."
          % (len(unplanned_retire), batch_hits["files_scanned"],
             "" if batch_hits["files_scanned"]
             else " -- ZERO FILES READ, so every 'passes through' below is "
                  "UNMEASURED, not clean"))
        p("")
        for c in unplanned_retire:
            hits = batch_hits["by_class"].get(c) or []
            if hits:
                p("- `%s` -- **NOT untouched**: consumed by %s"
                  % (c, ", ".join("`%s`" % h for h in hits)))
            else:
                p("- `%s` -- no per-class migrator and no batch post-pass names "
                  "it; passes through today" % c)
        p("")

    if unverified:
        p("**UNVERIFIED** -- no V_eta home, no migrator, fate never established. "
          "These strand today:")
        p("")
        for c in unverified:
            p("- `%s`" % c)
        p("")

    if stale:
        p("## Families naming classes that are no longer open")
        p("")
        p("Settled or removed since the family was written -- prune from `FAMILIES`:")
        p("")
        for c in stale:
            p("- `%s`" % c)
        p("")
    if dupes:
        p("## ERROR -- classes claimed by more than one family")
        p("")
        for c in sorted(set(dupes)):
            p("- `%s`" % c)
        p("")

    if missing_plans:
        p("## ERROR -- families claiming a decision document that does not exist")
        p("")
        for n, pl in missing_plans:
            p("- **%s** -> `schemas/%s` (missing)" % (n, pl))
        p("")

    ok = not unclaimed and not dupes and not missing_plans
    return "\n".join(L) + "\n", ok


STATE_LABEL = {
    "signed_awaiting_build": "decided and signed off, awaiting build",
    "awaiting_signature": "decided in a walkthrough, awaiting a signature",
    "proposed_unreviewed": "written up by Claude alone, unreviewed",
    "open": "nobody has proposed anything yet",
}


def family_state(status, signed):
    """The four-valued state a family renders as.

    Mirrors the board's own buckets EXACTLY, and for the same reason: "the team
    decided this" and "a document exists" are different facts, and collapsing
    them is how five families Claude wrote alone were once reported as settled.
    A `team` family with no sign-off line is NOT signed, no matter what the
    FAMILIES table says.
    """
    if status == "team":
        return "signed_awaiting_build" if signed else "awaiting_signature"
    if status == "proposed":
        return "proposed_unreviewed"
    return "open"


def decisions_doc(ocs=None):
    """Build the machine-readable decisions artifact."""
    schemas, _rows = load()
    disp = {s["class_name"]: s.get("disposition", "(none)") for s in schemas}

    families, by_class = [], {}
    for name, members, plan, call, status in FAMILIES:
        line = find_signoff(plan, name)
        state = family_state(status, line is not None)
        # A member may already have been built out of `in_progress` (or deleted
        # outright) while its family is still tracked. Report the per-class
        # disposition alongside, so "the family is unbuilt" and "this particular
        # class is still open" stay distinguishable -- they are not the same
        # claim, and conflating them is what made `dataseries_channel_map` look
        # open for four days after it was decided.
        member_rows = [{"class_name": m, "disposition": disp.get(m, "(absent)")}
                       for m in members]
        fam = {
            "name": name,
            "members": member_rows,
            "open_members": [m["class_name"] for m in member_rows
                             if m["disposition"] == "in_progress"],
            "plan": plan,
            "decision": call,
            "status": status,
            "signed": line is not None,
            "signoff": line,
            "state": state,
            "state_label": STATE_LABEL[state],
        }
        families.append(fam)
        for m in members:
            by_class[m] = name

    counts = {}
    for k in STATE_LABEL:
        counts[k] = sum(1 for f in families if f["state"] == k)
    doc = {
        "title": "V_eta decision families (GENERATED -- do not hand-edit)",
        "description":
            "Regenerate with `python3 tools/status_board.py`. The human-readable "
            "twin is schemas/V_eta_STATUS.md. A family counts as decided ONLY "
            "when its plan document carries a TEAM-SIGN-OFF line; Claude cannot "
            "promote its own work.",
        "summary": {
            "families": len(families),
            "classes_claimed": len(by_class),
            "open_classes": sum(1 for v in disp.values() if v == "in_progress"),
            "by_state": counts,
            "state_labels": STATE_LABEL,
        },
        "families": families,
        "by_class": by_class,
    }
    if ocs:
        # THE EVIDENCE SNAPSHOT. It lives here, in a committed artifact, because
        # neither sibling repo is checked out in this repo's CI -- so this block
        # is what `--check` compares against and what a `--check`-only run reads
        # back. It carries no timestamps and no absolute paths on purpose: a
        # field that changes every run makes the staleness check meaningless.
        doc["open_class_state"] = ocs
    return doc


def decisions_text(ocs=None):
    return json.dumps(decisions_doc(ocs), indent=2, sort_keys=False) + "\n"


def parse_args(argv):
    ap = argparse.ArgumentParser(
        description="Generate schemas/V_eta_STATUS.md + V_eta_decisions.json.")
    ap.add_argument("--check", action="store_true",
                    help="exit non-zero if the committed board is out of date")
    ap.add_argument("--did", default=find_repo("DID-matlab", "DID_MATLAB")
                    or os.environ.get("DID_MATLAB_PATH", "/home/user/DID-matlab"),
                    help="DID-matlab checkout (the +migrators_j package)")
    ap.add_argument("--ndi", default=find_repo("NDI-matlab", "NDI_MATLAB")
                    or os.environ.get("NDI_MATLAB_PATH", "/home/user/NDI-matlab"),
                    help="NDI-matlab checkout (the V_eta second pass)")
    ap.add_argument("--census", action="append", default=None, metavar="DIR",
                    help="directory of corpus *-summary.json reports; repeatable. "
                         "Defaults to <did>/corpus-reports and "
                         "<did>/tests/corpus-reports.")
    args = ap.parse_args(argv[1:])
    if args.census is None:
        args.census = [os.path.join(args.did, "corpus-reports"),
                       os.path.join(args.did, "tests", "corpus-reports")]
    return args


def main(argv):
    args = parse_args(argv)
    schemas, rows = load()

    # DENOMINATOR FIRST, UNCONDITIONALLY, and to stdout rather than into the
    # artifact: the reader of a generated file must be able to tell a
    # measurement from a reused snapshot, and a run that measured nothing must
    # not look like a run that found nothing.
    log = []
    ocs = gather_evidence(open_class_names(schemas), schemas, rows, args, log)

    text, ok = build(ocs)
    dtext = decisions_text(ocs)

    print("status board evidence:")
    for line in log:
        print("  " + line)
    c = ocs["counts"]
    print("  open classes: %d -- %s"
          % (len(ocs["classes"]),
             ", ".join("%s %d" % (OPEN_STATE_LABEL[k].split(" ", 1)[0], c.get(k, 0))
                       for k in (STATE_A, STATE_B, STATE_C, STATE_U))))

    if args.check:
        current = open(OUT).read() if os.path.exists(OUT) else ""
        if current != text:
            print("V_eta_STATUS.md is STALE. Run: python3 tools/status_board.py")
            return 1
        dcur = open(DECISIONS_OUT).read() if os.path.exists(DECISIONS_OUT) else ""
        if dcur != dtext:
            print("V_eta_decisions.json is STALE. Run: python3 tools/status_board.py")
            return 1
        if not ok:
            print("Status board reports unclaimed or duplicated open classes.")
            return 1
        print("V_eta_STATUS.md + V_eta_decisions.json are current.")
        return 0
    with open(OUT, "w") as fh:
        fh.write(text)
    with open(DECISIONS_OUT, "w") as fh:
        fh.write(dtext)
    print("wrote %s" % os.path.relpath(OUT, REPO))
    print("wrote %s" % os.path.relpath(DECISIONS_OUT, REPO))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
