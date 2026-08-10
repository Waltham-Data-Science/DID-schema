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

    (a) decided, nothing built        no migrator names it, no decided target
                                      schema exists
    (b) built, awaiting corpus proof  a migrator consumes it and/or its decided
                                      target is built, but no census has shown
                                      0 surviving documents
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
import glob
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
    ("time_reference", [
        "time_reference", "session_bounded_reference", "session_relative_reference",
        "epoch_bounded_reference", "epoch_relative_reference",
        "event_bounded_reference", "event_relative_reference", "utc_reference"],
     "V_eta_time_reference_model_plan.md",
     "8 classes collapse to absolute_reference + relative_reference",
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
    ("file navigation", ["filenavigator", "directory"],
     "V_eta_daq_family_decisions.md",
     "filenavigator -> `epoch_file_pattern` (id preserved; patterns PARSED not eval'd); "
     "`directory` is not a source",
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
    ("misc singletons", [
        "binaryseries_parameters", "interaction_purpose", "projectvar"],
     "V_eta_go_forward_class_audit.md",
     "binaryseries_parameters -> sampled_body; projectvar PASSES THROUGH (needs real docs); interaction_purpose is a target (#32)",
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
# `field_write` and `named` are still reported per class -- "still emitted by N
# migrator file(s)" is a useful, and deliberately unflattering, fact about an
# open class -- they just do not make it (b).
#
# THE GUARD LIST IS NOT COSMETIC. Its first version held only isfield/isstruct
# and missed the SECOND PASS entirely: an NDI assembler selects its input with
# `if ~strcmp(classNameOf(s), 'ensemble'); continue; end`
# (ensembleMembership.m:227), which is the whole ensemble consumer and was being
# filed as a bare mention. A comparison names what the code is LOOKING FOR; an
# assignment names what it PRODUCES.
GUARD_FUNCS = ("isfield", "isstruct", "strcmp", "strcmpi", "ismember", "matches")
CONSUMING_KINDS = ("guard", "field_read")
REF_KINDS = ("guard", "field_read", "field_write", "named")


def scan_matlab_file(path, patterns):
    """Return ({class: [(line_no, kind)]}, n_lines) for one .m file."""
    hits, in_block = {}, False
    try:
        with open(path, errors="replace") as fh:
            lines = fh.readlines()
    except OSError:
        return hits, 0
    for lno, line in enumerate(lines, 1):
        s = line.strip()
        if in_block:
            if s == "%}":
                in_block = False
            continue
        if s == "%{":
            in_block = True
            continue
        code, lits = split_matlab_line(line)
        if not lits and not code.strip():
            continue
        eq = assignment_split(code)
        guardish = any(g in code for g in GUARD_FUNCS)
        by_name = {}
        for text, col in lits:
            by_name.setdefault(text, col)
        for cls, rx in patterns.items():
            if cls in by_name:
                hits.setdefault(cls, []).append(
                    (lno, "guard" if guardish else "named"))
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
MIGRATOR_PACKAGES = [
    ("did", "migrators_j", "src/did/+did2/+convert/+migrators_j"),
    ("ndi", "ndi_second_pass", "src/ndi/+ndi/+migrate/+internal"),
]

REF_CAP = 6            # refs listed per class in the artifact; the count is exact


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
      * A CLASS REACHED THROUGH A COMPUTED NAME is invisible (sprintf, a
        dispatch variable, a name assembled from a field). Nothing in
        +migrators_j does this today; if something starts, this scan will
        under-report, in the safe direction.
      * FIELD-ACCESS HITS CAN BE INCIDENTAL for the short names. `.filter` is
        matched in jSpikeExtractionSettings.m as a grouping key as well as in
        jFrequencyFilter.m as the v1 block. Every reference is listed with its
        file and line so the reading is checkable rather than trusted.
    """
    patterns = {c: re.compile(r"\.\s*" + re.escape(c) + r"\b") for c in classes}
    per_class, roots_read, roots_missing = {}, [], []
    files_read = lines_read = 0
    for kind, label, rel in MIGRATOR_PACKAGES:
        root = did_root if kind == "did" else ndi_root
        base = os.path.join(root, rel) if root else None
        if not base or not os.path.isdir(base):
            roots_missing.append(label)
            continue
        roots_read.append(label)
        for path in sorted(glob.glob(os.path.join(base, "**", "*.m"),
                                     recursive=True)):
            rel_path = "%s/%s" % (label, os.path.relpath(path, base))
            files_read += 1
            name = os.path.basename(path)[:-2]
            if name in classes and os.path.dirname(path) == base:
                per_class.setdefault(name, {}).setdefault("file", rel_path)
            hits, n_lines = scan_matlab_file(path, patterns)
            lines_read += n_lines
            for cls, spots in hits.items():
                refs = per_class.setdefault(cls, {}).setdefault("refs", [])
                for lno, why in spots:
                    refs.append(("%s:%d" % (rel_path, lno), why))

    if not roots_read:
        return None, {"available": False, "packages_read": [],
                      "packages_missing": roots_missing, "files_read": 0,
                      "lines_read": 0, "classes_queried": len(classes)}

    out = {}
    for cls in sorted(classes):
        ev = per_class.get(cls, {})
        refs = sorted(ev.get("refs", []))
        consuming = [r for r in refs if r[1] in CONSUMING_KINDS]
        other = [r for r in refs if r[1] not in CONSUMING_KINDS]
        out[cls] = {
            "migrator_file": ev.get("file"),
            "n_consuming_refs": len(consuming),
            "consuming_refs": ["%s (%s)" % r for r in consuming[:REF_CAP]],
            "n_emitting_refs": len(other),
            "emitting_refs": ["%s (%s)" % r for r in other[:REF_CAP]],
        }
    return out, {"available": True, "packages_read": roots_read,
                 "packages_missing": roots_missing, "files_read": files_read,
                 "lines_read": lines_read, "classes_queried": len(classes),
                 "ref_kinds": list(REF_KINDS),
                 "consuming_kinds": list(CONSUMING_KINDS)}


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
    src = {"available": bool(with_data),
           "reports_found": n_all,
           "reports_read": len(reports),
           "reports_unreadable": len(unreadable),
           "reports_with_survivor_data": len(with_data),
           "roots_walked": walked,
           "roots_missing": len(missing),
           "corpora": corpora,
           "source_documents": sum(int(r.get("total") or 0) for _n, r in reports),
           "classes_queried": len(classes)}
    if not with_data:
        return None, src

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
    return out, src


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
        n_emit = m.get("n_emitting_refs", 0) if measured else 0
        emit_refs = m.get("emitting_refs", []) if measured else []

        why = []
        if mfile:
            why.append("migrator `%s`" % mfile)
        if n_con:
            why.append("%d consuming reference(s)" % n_con)
        if built_t:
            why.append("decided target(s) built: %s"
                       % ", ".join("`%s`" % t for t in built_t))
        has_build = bool(mfile or n_con or built_t)

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
            "n_emitting_refs": n_emit,
            "emitting_refs": emit_refs,
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
                     "n_emitting_refs": r.get("n_emitting_refs", 0),
                     "emitting_refs": r.get("emitting_refs", [])}
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

    cen, cen_src = census_evidence(open_work, args.census)
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
    p("| build: V_eta migrator packages read | %s |"
      % (", ".join("`%s`" % s for s in msrc.get("packages_read") or []) or "**NONE**"))
    p("| build: migrator files inspected | %d |" % msrc.get("files_read", 0))
    p("| build: migrator lines inspected | %d |" % msrc.get("lines_read", 0))
    p("| build: classes queried | %d |" % msrc.get("classes_queried", 0))
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
    p("Only a CONSUMING reference makes a class (b) -- a migrator file named")
    p("after it, an `isfield(preBody, '<class>')` / `strcmp(classNameOf(s),")
    p("'<class>')` guard, or a read of `preBody.<class>`. A migrator that WRITES")
    p("the class (`x.<class> = ...`, `classBlock('<class>')`) or merely names it")
    p("as a value is counted")
    p("separately and shown as *still emitted*, because for an open class that is")
    p("evidence the decided change has **not** landed. Counting those as build")
    p("progress is what the first draft of this scan did: it made `directory`")
    p("look built off `struct('format', 'directory', ...)` and put all 18 of")
    p("`session_relative_reference`'s emission sites on the wrong side of the")
    p("ledger.")
    p("")
    p("**The `decided target(s) built` signal is the WEAKER of the two** and is")
    p("marked separately for that reason. A decided target can be a class that")
    p("already existed for other reasons -- `ensemble` reaches (b) on `subject`,")
    p("`directed_relation` and `sampled_body`, none of which was built for it. Read")
    p("a row whose only evidence is a built target as *the target exists*, not as")
    p("*the work is done*.")
    p("")
    p("| class | family | state | build evidence | still emitted | survivors |")
    p("|---|---|---|---|---|---|")
    for r in rowsv:
        surv = ("n/a -- not measured" if r["survivors"] is None
                else str(r["survivors"]))
        ev = "; ".join(r["build_evidence"]) or ("*not measured*"
                                                if not r["build_evidence_measured"]
                                                else "*none*")
        p("| `%s` | %s | %s | %s | %s | %s |"
          % (r["class_name"], r["family"] or "-",
             OPEN_STATE_LABEL[r["state"]].split(" ", 1)[0], ev,
             r["n_emitting_refs"] or "-", surv))
    p("")
    for k in (STATE_A, STATE_U, STATE_C, STATE_B):
        members = [r for r in rowsv if r["state"] == k]
        if not members:
            continue
        p("#### %s -- %d" % (OPEN_STATE_LABEL[k], len(members)))
        p("")
        for r in members:
            bits = []
            if r["migrator_file"]:
                bits.append("migrator `%s`" % r["migrator_file"])
            if r["n_consuming_refs"]:
                bits.append("consumed at %d site(s): %s%s"
                            % (r["n_consuming_refs"],
                               ", ".join("`%s`" % x for x in r["consuming_refs"]),
                               " ..." if r["n_consuming_refs"]
                               > len(r["consuming_refs"]) else ""))
            if r["n_emitting_refs"]:
                bits.append("still emitted/named at %d site(s): %s%s"
                            % (r["n_emitting_refs"],
                               ", ".join("`%s`" % x for x in r["emitting_refs"]),
                               " ..." if r["n_emitting_refs"]
                               > len(r["emitting_refs"]) else ""))
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
    p("The model is settled and recorded; the schema has not changed yet. Every")
    p("one of these re-targets migrators that are already written, which is why")
    p("migrator work before the target closes is rework.")
    p("")
    p("| family | classes | decision | recorded in |")
    p("|---|---|---|---|")
    for name, members, plan, what, _ in decided:
        p("| **%s** | %d | %s | `%s` |" % (name, len(members), what, plan))
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
        p("### `retire`, but NO MIGRATOR YET -- %d rows" % len(unplanned_retire))
        p("")
        p("Marked `retire` in the ledger with **no migrator and no `how` note**, so the")
        p("documents pass through untouched today. `retire` reads as settled, so these")
        p("do not appear in the family counts above -- but they are open work. Several")
        p("hold real data (e.g. `spike_extraction_parameters` carries filter_type /")
        p("filter_low / filter_high / filter_order / filter_ripple).")
        p("")
        p("**This heading used to say \"nothing decided\" / \"no recorded plan\", and that")
        p("was WRONG** -- it is computed from the LEDGER (disposition + migrator + `how`),")
        p("not from whether a decision exists. Checked 2026-08-08: **every one of these")
        p("rows is covered by a plan document**, and most are signed. The list means")
        p("\"no migrator has been written yet\", not \"nobody has decided\". A board that")
        p("reports settled work as undecided is the mirror of the failure this board")
        p("exists to prevent, and it cost a review pass to notice.")
        p("")
        for c in unplanned_retire:
            p("- `%s`" % c)
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
