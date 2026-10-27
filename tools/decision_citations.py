"""Which classes are DECIDED, and the line that decided each one.

THE RULE (Operating Rule 4, CLAUDE.md: THE TEAM DECIDES; CLAUDE PROPOSES)
--------------------------------------------------------------------------
A class is DECIDED if and only if it CITES a decision line that exists. A
citation is a document and a tag:

    ("did_v2_epoch_plan.md", "epoch")

and it RESOLVES when that document holds an accepted decision line the tag
names. Two forms of decision line are read:

    TEAM-SIGN-OFF [<tag>]: <who/when> -- <what was decided>
    Decided by <name>, <YYYY-MM-DD> [<tag>]: <what was decided>

A `TEAM-SIGN-OFF` line with a `[tag]` is named by that tag; an untagged one
(the older form, still valid) is named by its DATE.

A `Decided by` line counts ONLY when (2026-10-21, Jess Haley):
  * <name> is a member of TEAM (below -- the one place the team is listed);
  * it carries a `[tag]`. An untagged `Decided by` line is REPORTED (a
    rejected line in the census, with the reason), never counted: a date names
    every decision made that day, so it cannot name one;
  * its tag is UNIQUE among the document's `Decided by` lines. Two lines with
    one tag are both reported and neither counts, so a citation always names
    exactly one line.
It is named by its tag only.

Anything else renders "Proposed (not decided)": a class with no citation, and a
class whose every citation fails to resolve. A citation that fails to resolve
is also an ERROR the board reports and fails on, because it is a record that
points nowhere -- a typo, or a decision that was superseded.

WHAT THIS REPLACES
------------------
Until 2026-10-21 `tools/status_board.py` grouped classes into decision
FAMILIES, and a class was decided when its family's tag matched a sign-off in
the family's document. That was one indirection too many: a signature whose tag
named no family reached nothing (47 such lines on the day it was removed), and
the family's one-line summary was Claude-authored prose standing beside the
team's words. Each class now cites the line itself, and the board shows that
line's own text.

WHERE A CITATION MAY POINT
--------------------------
A document is a bare file name (`did_v2_epoch_plan.md`), which resolves to the
unique file of that name under `docs/` (`tools/doc_paths.py`; [markdown cleanup
and rename] part (5)), or a path from the repository root
(`review/73/OPEN_ITEMS.md`). The generated markdown
files (GENERATED_MARKDOWN) are never read: they quote decisions, they do not
hold them.

Claude may add or correct a CITATION (it points at a line a team member's
decision is recorded on). Claude records a `Decided by` line only for what a
team member said, and never writes a `TEAM-SIGN-OFF` line.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import doc_paths

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# The documents' root: every bare name resolves to the unique file of that
# name under it (doc_paths.resolve). Tests point it at a temporary folder.
DOCS = doc_paths.DOCS

SIGNOFF = "TEAM-SIGN-OFF:"
KIND_SIGNOFF = "TEAM-SIGN-OFF"
KIND_DECIDED_BY = "Decided by"

# THE TEAM -- the people whose decisions count (CLAUDE.md Operating Rule 4).
# The one place this list is kept; every reader of `Decided by` lines asks
# is_team_member() rather than carrying its own copy.
TEAM = ("Jess Haley", "Steve Van Hooser")


def is_team_member(name):
    """True when `name` is exactly a TEAM member's name (whitespace-normalised)."""
    return " ".join((name or "").split()) in TEAM

DECIDED = "decided"
PROPOSED = "proposed (not decided)"

# GENERATED MARKDOWN IS NOT A RECORD OF ANYTHING; it is a copy of one. Checked
# in tests against the `.md` files `tools/gates.py` declares its steps write.
GENERATED_MARKDOWN = ("did_v2_STATUS.md", "did_v2_coverage_ledger.md",
                      "did_v2_final_class_set.md")

_DATE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
# Line-initial, after an optional list marker or bold opener. The date must be
# a real YYYY-MM-DD, so the template's `<date>` never matches. The NAME is
# captured whoever it is, so a line by someone outside TEAM is REPORTED rather
# than silently ignored; whether it counts is decided in scan_decision_lines.
_DECIDED_BY_RE = re.compile(
    r"^(?:[-*>]\s+)?(?:\*\*)?Decided by\s+(?P<name>[^,\[\]:\n]+?),\s*"
    r"(?P<date>\d{4}-\d{2}-\d{2})"
    r"\s*(?:\[(?P<tag>[^\]]+)\])?\s*(?:\*\*)?\s*:\s*(?P<rest>.*)$")


def match_decided_by(line):
    """A `Decided by <name>, <date> [<tag>]: ...` line, parsed, or None.

    Returns {name, date, tag (or None), rest, team (bool)}. The ONE parser of
    this form: coverage.py reads it through here too."""
    m = _DECIDED_BY_RE.match(line)
    if not m:
        return None
    tag = m.group("tag").strip() if m.group("tag") else None
    name = " ".join(m.group("name").split())
    return {"name": name, "date": m.group("date"), "tag": tag,
            "rest": m.group("rest").strip(), "team": is_team_member(name)}


# ---------------------------------------------------------------------------
# THE CITATIONS -- one entry per class, keyed by the v1 (ledger) name or the
# V_eta class name, matched EXACTLY (no lowercasing, no underscore stripping).
#
# Migrated 2026-10-21 from the 27 FAMILIES rows, one citation per member, so
# every class that was decided stays decided (proved in the commit that made
# this). The entries marked ADDED cite a signed line that names the class but
# that no family reached; each is explained beside it.
# ---------------------------------------------------------------------------
_ST = "did_v2_spatial_transcriptomics_plan.md"
_ST_REVIEW = (_ST, "spatial_transcriptomics_family")   # signs #73 review items 1-71
_ST_AUDIT2 = (_ST, "#73 audit 2, D1-D13")              # signs audit 2 D1-D13
_GFA = "did_v2_go_forward_class_audit.md"
# "Decided by Jess Haley, 2026-10-21 [epoch files as data bodies]: Migrated
# recordings link their epoch files as data bodies ..." -- names one
# observation per element per epoch, the `epochfiles_ingested` caches
# (non-ingested files) and the `daqreader_*_epochdata_ingested` archives
# (ingested files).
_REC_2026_10_21 = ("did_v2_recording_observation_plan.md", "epoch files as data bodies")

CITATIONS = {
    # -- migrated from the families ---------------------------------------
    "calculator": [("did_v2_subject_calculation_plan.md", "calculator mixin dropped (#73)")],
    "generic_file": [("did_v2_OPEN_WORK.md", "stranded sources")],
    "imageCollection": [("did_v2_OPEN_WORK.md", "stranded sources")],
    # The second citation is the signed amendment the target map names
    # ("TEAM-SIGN-OFF [logical_observation amendment 1] 2026-08-18").
    "valid_interval": [("did_v2_logical_observation_plan.md", "logical_observation"),
                       ("did_v2_logical_observation_plan.md", "logical_observation amendment 1")],
    # The second citation is the row the target map's decision_note names
    # ("SIGNED 2026-08-13 -- see did_v2_OPEN_WORK.md row #113").
    "epochclocktimes": [("did_v2_time_reference_family_plan.md", "epochclocktimes"),
                        ("did_v2_OPEN_WORK.md", "epoch extent -- row #113")],
    "stimulus_presentation": [("did_v2_stimulus_model_plan.md", "stimulus")],
    "ensemble": [("did_v2_ensemble_plan.md", "ensemble")],
    "hartley_calc": [("did_v2_ngrid_family_findings.md", "receptive field fold")],
    "tuningcurve_calc": [(_GFA, "confirm sheet 2026-08-17")],
    "oridirtuning_calc": [(_GFA, "confirm sheet 2026-08-17")],
    "probe_location": [(_GFA, "confirm sheet 2026-08-17")],
    "treatment": [(_GFA, "confirm sheet 2026-08-17")],
    # ADDED: a second citation. The 2026-09-29 line amends this class's target
    # by name: "`kilosort_clusters`, `kiasort_clusters` and `jrclust_clusters`
    # migrate to `label_calculation`".
    "jrclust_clusters": [(_GFA, "confirm sheet 2026-08-17"),
                         (_GFA, "spike-sorter output, amends the 2026-08-17 confirm sheet")],
    "ngrid": [("did_v2_image_model_plan.md", "image / ngrid")],
    "imageStack_parameters": [("did_v2_image_model_plan.md", "image / ngrid")],
    "acquisition_epoch": [("did_v2_epoch_plan.md", "epoch")],
    "element_epoch": [("did_v2_epoch_plan.md", "epoch")],
    "epochid": [("did_v2_epoch_plan.md", "epoch")],
    "epochfiles_ingested": [("did_v2_epoch_plan.md", "epoch"), _REC_2026_10_21],
    "daqsystem": [("did_v2_daq_family_decisions.md", "daq configuration")],
    "daqreader": [("did_v2_daq_family_decisions.md", "daq configuration")],
    "daqmetadatareader": [("did_v2_daq_family_decisions.md", "daq configuration")],
    "daqreader_ndr": [("did_v2_daq_family_decisions.md", "daq configuration")],
    "daqreader_epochdata_ingested": [("did_v2_ingested_payload_findings.md", "daq ingested payloads"),
                                     _REC_2026_10_21],
    "daqmetadatareader_epochdata_ingested": [("did_v2_ingested_payload_findings.md", "daq ingested payloads")],
    "daqreader_image_epochdata_ingested": [("did_v2_ingested_payload_findings.md", "daq ingested payloads"),
                                           _REC_2026_10_21],
    "syncgraph": [("did_v2_clock_alignment_cluster_plan.md", "sync configuration")],
    "syncrule": [("did_v2_clock_alignment_cluster_plan.md", "sync configuration")],
    "syncrule_mapping": [("did_v2_clock_alignment_cluster_plan.md", "sync mapping")],
    "filenavigator": [("did_v2_daq_family_decisions.md", "file navigation")],
    # The two UNTAGGED sign-offs, cited by date (the old family join took the
    # document's first untagged line; these are those lines).
    "openminds": [("did_v2_openminds_family_record.md", "2026-08-08")],
    "filter": [("did_v2_frequency_filter_model_plan.md", "2026-07-30"),
               ("did_v2_frequency_filter_model_plan.md", "filters are methods")],
    "app": [("did_v2_tenet_audit.md", "software")],
    "spike_extraction_parameters": [("did_v2_method_parameters_plan.md", "spike processing parameters")],
    "spike_extraction_parameters_modification": [("did_v2_method_parameters_plan.md", "spike processing parameters")],
    "sorting_parameters": [("did_v2_method_parameters_plan.md", "spike processing parameters")],
    "vmspikefilteringparameters": [("did_v2_method_parameters_plan.md", "spike processing parameters")],
    "stimulus_parameter": [("did_v2_stimulus_parameter_plan.md", "stimulus parameters")],
    "stimulus_parameter_table": [("did_v2_stimulus_parameter_plan.md", "stimulus parameters")],
    "stimulus_response": [("did_v2_stimulus_response_model_plan.md", "stimulus response")],
    "stimulus_response_scalar": [("did_v2_stimulus_response_model_plan.md", "stimulus response")],
    "stimulus_response_scalar_parameters": [("did_v2_stimulus_response_model_plan.md", "stimulus response")],
    "stimulus_response_scalar_parameters_basic": [("did_v2_stimulus_response_model_plan.md", "stimulus response")],
    "subjectmeasurement": [(_GFA, "subject measurement")],
    "element": [("did_v2_recording_observation_plan.md", "raw recording observation"),
                _REC_2026_10_21],
    # The second citation is the signed amendment the target map names
    # ("SIGNED 2026-09-29 ([pyraview levels], did_v2_recording_observation_plan.md)").
    "pyraview": [("did_v2_recording_observation_plan.md", "raw recording observation"),
                 ("did_v2_recording_observation_plan.md",
                  "pyraview levels, amends the 2026-08-13 pyraview pyramid confirmation")],
    "subject": [(_GFA, "subject")],
    "session": [(_GFA, "session")],
    "binaryseries_parameters": [(_GFA, "misc singletons")],
    "interaction_purpose": [(_GFA, "misc singletons")],
    "projectvar": [(_GFA, "misc singletons")],
    "spatialGeneExpressionPyramid": [_ST_REVIEW],
    "spatialGeneExpressionCells": [_ST_REVIEW],
    "spatialGeneExpressionTiles": [_ST_REVIEW],
    "cellTypeLabels": [_ST_REVIEW],
    "geneListMapping": [_ST_REVIEW],
    "fileReference": [_ST_REVIEW],
    "geneList": [_ST_REVIEW],
    "geneExpression": [_ST_REVIEW],

    # -- ADDED 2026-10-21: signed lines that name the class, reached by no family.
    # The [spatial_transcriptomics_family] line signs "the #73 review decisions
    # recorded above as items 1 through 71 ... (items 50-53, 59, 61, 67 and 68
    # as written)"; each class below is NAMED in the item cited beside it.
    "neuron_extracellular": [_ST_REVIEW],   # item 48 names it
    "fitcurve": [_ST_REVIEW],               # item 68: "v1 `fitcurve` ... becomes a model_fit_calculation"
    "image": [_ST_REVIEW],                  # item 51: decided targets recorded for v1 `image`, `imageStack`, `ontologyImage`
    "imageStack": [_ST_REVIEW],             # item 51
    "ontologyImage": [_ST_REVIEW],          # item 51
    # item 67 (the [spatial_transcriptomics_family] line) named it first; that fold
    # (item.value.control_item) is superseded by "Decided by Jess Haley, 2026-10-22
    # [control as covariate]": the class becomes no V2 document.
    "control_stimulus_ids": [("did_v2_stimulus_response_model_plan.md", "control as covariate")],
    "probe_geometry": [_ST_REVIEW],         # item 50: position_observation "is now `probe_geometry`'s decided target"
    # The [#73 audit 2, D1-D13] line signs D1-D13 of review/73/audit2_SUMMARY.md's
    # decision log; D7 (a) reads "`vmspikefit` -> `model_fit_calculation`".
    "vmspikefit": [_ST_AUDIT2],
    # Named in the 2026-09-29 line: "`kilosort_clusters`, `kiasort_clusters` and
    # `jrclust_clusters` migrate to `label_calculation`".
    "kilosort_clusters": [(_GFA, "spike-sorter output, amends the 2026-08-17 confirm sheet")],
    "kiasort_clusters": [(_GFA, "spike-sorter output, amends the 2026-08-17 confirm sheet")],
    # Signed in review/73/OPEN_ITEMS.md: "the pyramid is an intensity observation
    # ...; level 0 is the measurement, reduced levels redundant; ... the store ...
    # an unheld opaque_body ...; the software entity is the builder".
    "lightsheetZarrPyramid": [("review/73/OPEN_ITEMS.md", "lightsheet migrator points 1-11")],
    "lightsheetZarrLevel": [("review/73/OPEN_ITEMS.md", "lightsheet migrator points 1-11")],
    # ADDED 2026-10-21 (later the same day): Jess's two "Decided by Jess Haley"
    # lines of that date. The bath line: "A bath is a manipulation whose value
    # is the formulation (pointed at through `value_id`), not a dose".
    "stimulus_bath": [(_GFA, "bath is a manipulation")],
    # The recording line names `daqreader_*_epochdata_ingested`; the mfdaq
    # subtype is one of them and was cited by nothing before.
    "daqreader_mfdaq_epochdata_ingested": [_REC_2026_10_21],
}


# ---------------------------------------------------------------------------
# THE SCANNER
# ---------------------------------------------------------------------------
def scan_decision_lines(text):
    """Every decision line in `text`, ACCEPTED or REJECTED with a reason.

    THE ONE SCANNER: resolution and the census both read it, so the set of
    lines that COUNT and the set a report describes cannot drift apart. A
    rejected line is returned rather than dropped, so "no decision here" and
    "a decision written in a form nothing reads" stay distinguishable.

    Returns dicts: {line, kind, tag, date, keys, content, accepted,
    rejected_because}. `keys` are the names a citation may use for the line.

    Guards, each added after a real laundering path:
      * HTML comments are stripped first: a plan document that TELLS the team
        how to sign off carries the marker inside a comment.
      * A line inside a fenced code block is a QUOTATION, not a decision.
      * `SIGN-OFF SUPERSEDED [tag]: ...` retires the NEXT decision line with
        that tag in the same document.
      * The sign-off TEMPLATE's own slots (`<family>`, `<who/when>`, `<what was
        decided>`) mark a placeholder, not a decision.
      * Under 10 characters of decision text is not a decision.
    A `TEAM-SIGN-OFF` whose tag line ends at the colon continues on the next
    non-blank lines (multi-line sign-offs, 2026-09-22).
    """
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    marker = SIGNOFF.rstrip(":")
    out = []
    lines = text.splitlines()
    in_fence = False
    superseded = {}
    for n, raw in enumerate(lines, 1):
        line = raw.lstrip()
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        m_sup = re.match(r"SIGN-OFF SUPERSEDED\s*\[([^\]]+)\]\s*:?\s*(.*)$", line)
        if m_sup and not in_fence:
            superseded[m_sup.group(1).strip()] = m_sup.group(2).strip()
            continue
        m_dec = match_decided_by(line)
        who = None
        if m_dec:
            kind = KIND_DECIDED_BY
            date = m_dec["date"]
            tagged = m_dec["tag"]
            rest = m_dec["rest"]
            who = m_dec["name"]
        elif line.startswith(marker):
            kind = KIND_SIGNOFF
            rest = line[len(marker):].strip()
            tagged = None
            m = re.match(r"\[([^\]]+)\]\s*(.*)$", rest)
            if m:
                tagged, rest = m.group(1).strip(), m.group(2).strip()
            rest = rest.lstrip(":").strip()
            if not rest:
                _joined = []
                for _next in lines[n:]:
                    _stripped = _next.strip()
                    if not _stripped or _stripped.startswith(marker):
                        break
                    if _stripped[0] in "|#-*" and not _joined:
                        break
                    _joined.append(_stripped)
                    if len(_joined) >= 8 or ("-- " in _stripped and
                                             sum(len(s) for s in _joined) >= 20):
                        break
                if _joined:
                    rest = " ".join(_joined).lstrip(":").strip()
            dm = _DATE_RE.search(rest)
            date = dm.group(1) if dm else None
        else:
            continue
        why = None
        _slots = ("<family>", "<tag>", "<who/when>", "<what was decided>")
        _hit = [s for s in _slots if s in rest]
        if in_fence:
            why = "inside a fenced code block -- a quotation, not a signature"
        elif tagged is not None and tagged in superseded:
            why = "SUPERSEDED -- " + (superseded.pop(tagged) or "marked superseded")
        elif _hit:
            why = ("TEMPLATE PLACEHOLDER -- carries the unfilled slot %s, not a "
                   "decision" % _hit[0])
        elif len(rest) < 10:
            why = "under 10 characters after the marker -- not a decision"
        elif kind == KIND_DECIDED_BY and not is_team_member(who):
            why = ("NOT A TEAM MEMBER -- %r is not in TEAM %s; only the team "
                   "decides" % (who, list(TEAM)))
        elif kind == KIND_DECIDED_BY and not tagged:
            why = ("UNTAGGED -- a `Decided by` line must carry a [tag] "
                   "(`Decided by <name>, <date> [<tag>]: ...`); a date names "
                   "every decision of that day, so it cannot name this one")
        if kind == KIND_DECIDED_BY:
            keys = [tagged] if tagged else []
        else:
            keys = [tagged] if tagged is not None else ([date] if date else [])
        out.append({"line": n, "kind": kind, "tag": tagged, "date": date,
                    "who": who, "keys": keys, "content": rest,
                    "anchor": anchor_text(line),
                    "accepted": why is None, "rejected_because": why})
    # A `Decided by` tag must name ONE line: every accepted `Decided by` line
    # sharing its tag with another is reported, and none of them counts.
    seen = {}
    for e in out:
        if e["accepted"] and e["kind"] == KIND_DECIDED_BY:
            seen.setdefault(e["tag"], []).append(e)
    for tag, group in seen.items():
        if len(group) > 1:
            where = ", ".join(str(e["line"]) for e in group)
            for e in group:
                e["accepted"] = False
                e["rejected_because"] = (
                    "TAG NOT UNIQUE -- [%s] is on %d `Decided by` lines "
                    "(lines %s); a tag must name exactly one" % (tag, len(group), where))
    return out


ANCHOR_LEN = 60


def anchor_text(line):
    """A verbatim prefix of a decision line, to quote beside its citation.

    Rendered as `<anchor>` (document:line), so tools/check_citations.py can
    VERIFY every citation a generated artifact prints: it confirms a citation
    when a quotation in the citation's own sentence is found on the cited line.
    A bare tag is not enough -- `data_body` or `raw recording observation`
    occurs on many lines of its own plan, so it locates nothing -- while the
    line's own opening (`TEAM-SIGN-OFF [tag]: who / date`, or `Decided by Jess
    Haley, <date>: <what>`) occurs once. Cut before any backtick or double
    quote (either would end the quotation) and at a word boundary.
    """
    # ". " too: check_citations ends the citation's sentence there, so the
    # quotation must not contain one.
    text = re.split(r'[`"]|\. ', " ".join(line.split()), maxsplit=1)[0].rstrip()
    if len(text) > ANCHOR_LEN:
        text = text[:ANCHOR_LEN].rsplit(" ", 1)[0]
    return text.rstrip(" ,;:-")


def cite_md(document, line, anchor):
    """"<anchor>" (document:line) as ONE sentence, so check_citations reads
    only this quotation as its evidence and no neighbouring one.

    DOUBLE QUOTES, not backticks: check_citations pairs backticks only around
    spans of 8+ characters, so a short code span earlier on the same table row
    (`app`) would pair with this quotation's opening backtick and swallow it."""
    return f'. "{anchor}" ({document}:{line}). '


def document_path(document):
    """A cited document: the unique `docs/**/<name>` for a bare name
    (doc_paths.resolve), else a path from the repo root. None when a bare name
    names no document, or more than one."""
    if not document:
        return None
    return doc_paths.resolve(document, root=DOCS)


_SCAN_CACHE = {}


def _scan_document(document):
    path = document_path(document)
    if path is None or not os.path.exists(path):
        return None
    if os.path.basename(path) in GENERATED_MARKDOWN:
        return None
    key = (path, os.path.getmtime(path))
    if key not in _SCAN_CACHE:
        with open(path, encoding="utf-8") as fh:
            _SCAN_CACHE[key] = scan_decision_lines(fh.read())
    return _SCAN_CACHE[key]


def resolve(document, tag):
    """One citation, resolved: the decision line it names, or why there is none."""
    rec = {"document": document, "tag": tag, "resolved": False,
           "line": None, "kind": None, "decision": None, "anchor": None,
           "matches": 0, "why": None}
    entries = _scan_document(document)
    if entries is None:
        rec["why"] = ("the document does not exist (or is a generated copy, "
                      "which holds no decisions)")
        return rec
    hits = [e for e in entries if e["accepted"] and tag in e["keys"]]
    if not hits:
        rejected = [e for e in entries if not e["accepted"] and tag in e["keys"]]
        rec["why"] = ("a line with this tag exists and is REJECTED: "
                      + rejected[0]["rejected_because"]) if rejected else (
                      "no accepted TEAM-SIGN-OFF or Decided-by line in the "
                      "document carries this tag (or, for an untagged "
                      "TEAM-SIGN-OFF, this date)")
        return rec
    first = hits[0]
    rec.update(resolved=True, line=first["line"], kind=first["kind"],
               decision=first["content"], anchor=first["anchor"],
               matches=len(hits))
    return rec


def citations_for(names, table=None):
    """Every citation for a class, by any of its names, EXACT match, deduplicated.

    Returns [(name_matched, document, tag)] in table order."""
    table = CITATIONS if table is None else table
    out, seen = [], set()
    for name in names:
        if not name:
            continue
        for doc, tag in table.get(name) or ():
            if (doc, tag) in seen:
                continue
            seen.add((doc, tag))
            out.append((name, doc, tag))
    return out


def decision_for(names, table=None):
    """The decision state of one class, from its own citations.

    DECIDED iff at least one citation resolves. Unresolved citations are
    returned beside it (and are an error at the board), never silently dropped.
    """
    cites = []
    for matched, doc, tag in citations_for(names, table):
        rec = resolve(doc, tag)
        rec["matched_name"] = matched
        cites.append(rec)
    resolved = [c for c in cites if c["resolved"]]
    return {"state": DECIDED if resolved else PROPOSED,
            "citations": cites,
            "decided_by": resolved[0] if resolved else None,
            "unresolved": [c for c in cites if not c["resolved"]]}


def unresolved_citations(table=None):
    """Every citation in the table that does not resolve: [(class, record)]."""
    table = CITATIONS if table is None else table
    bad = []
    for cls in sorted(table):
        for doc, tag in table[cls]:
            rec = resolve(doc, tag)
            if not rec["resolved"]:
                bad.append((cls, rec))
    return bad


def decision_census(docs_dir=None, table=None):
    """Where every decision line is, and which of them a class cites.

    RULE 5: the denominator first -- documents read, lines accepted and
    rejected -- then the two directions of the mismatch, SEPARATELY:

      uncited line          an accepted decision line no citation names. The
                            decision exists and no class points at it. Many of
                            these decide something that is not a class (a
                            tenet, a naming rule); the list is for a reader.
      unresolved citation   a citation that names no accepted line.
    """
    table = CITATIONS if table is None else table
    root = docs_dir or DOCS
    # Every document under docs/ by its bare name (a citation's name for it);
    # generated/ is excluded, as are the GENERATED_MARKDOWN names.
    where = {}
    files, excluded = [], []
    generated_dir = os.path.join(os.path.abspath(root), "generated")
    for path in doc_paths.all_markdown(root):
        name = os.path.basename(path)
        where[name] = path
        if name in GENERATED_MARKDOWN or \
                os.path.dirname(os.path.abspath(path)) == generated_dir:
            excluded.append(name)
        else:
            files.append(name)
    files.sort()
    excluded.sort()
    # Documents cited by a path from the repository root are read too, and named.
    outside = sorted({doc for v in table.values() for doc, _t in v
                      if "/" in doc})
    docs = files + outside

    cited_by = {}
    for cls, v in table.items():
        for doc, tag in v:
            cited_by.setdefault(doc, {}).setdefault(tag, []).append(cls)

    lines, rejected = [], []
    for name in docs:
        path = where.get(name) if "/" not in name else document_path(name)
        if not path or not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as fh:
            for e in scan_decision_lines(fh.read()):
                (lines if e["accepted"] else rejected).append(dict(e, document=name))
    excluded_markers = 0
    for name in excluded:
        path = where.get(name)
        if path and os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                excluded_markers += len(scan_decision_lines(fh.read()))

    def _cited(e):
        tags = cited_by.get(e["document"], {})
        return sorted({c for k in e["keys"] for c in tags.get(k, [])})

    uncited = [{"document": e["document"], "line": e["line"], "kind": e["kind"],
                "tag": e["tag"], "date": e["date"], "anchor": e["anchor"]}
               for e in lines if not _cited(e)]
    unresolved = unresolved_citations(table)
    by_kind = {}
    for e in lines:
        by_kind[e["kind"]] = by_kind.get(e["kind"], 0) + 1
    return {
        "documents_read": len(docs),
        "documents_read_outside_docs": outside,
        "documents_excluded_as_generated": excluded,
        "markers_inside_excluded_documents": excluded_markers,
        "accepted_lines": len(lines),
        "accepted_lines_by_kind": dict(sorted(by_kind.items())),
        "rejected_lines": [
            {"document": e["document"], "line": e["line"], "kind": e["kind"],
             "tag": e["tag"], "why": e["rejected_because"],
             "excerpt": e["content"][:120],
             "cited_by_classes": _cited(e)}
            for e in rejected],
        "classes_citing": len(table),
        "citations_total": sum(len(v) for v in table.values()),
        "citations_unresolved": [
            {"class": c, "document": r["document"], "tag": r["tag"],
             "why": r["why"]} for c, r in unresolved],
        "lines_cited": len(lines) - len(uncited),
        "uncited_lines": uncited,
    }


# ---------------------------------------------------------------------------
# PENDING BUILDS (2026-10-22, Jess Haley: "do c now")
# ---------------------------------------------------------------------------
# A decision whose build lives in another repository may be recorded before
# that build lands, so the record is never held back in an uncommitted tree.
# Its line says so with the marker `Build pending:` followed by the repository
# and what is to be built. When the build lands the marker is replaced by
# `Built: <repo> <commit>`. No marker may remain when the PR merges:
#
#     python3 tools/decision_citations.py --pending          # report
#     python3 tools/decision_citations.py --pending --strict # exit 1 if any
#
# The report states its denominator first (Operating Rule 5).

PENDING_MARKER = "Build pending:"


def pending_builds(docs_dir=None):
    """Every accepted-form decision line carrying the pending marker.

    Reads every hand-written document under `docs/` (doc_paths.record_documents).
    Returns (lines_read, pending) where pending is a list of
    {document, line, tag, excerpt}."""
    base = docs_dir or DOCS
    lines_read = 0
    pending = []
    for path in doc_paths.record_documents(base):
        with open(path, encoding="utf-8") as fh:
            for n, line in enumerate(fh, 1):
                parsed = match_decided_by(line)
                if not parsed and not line.startswith("TEAM-SIGN-OFF"):
                    continue
                lines_read += 1
                if PENDING_MARKER in line:
                    pending.append({"document": os.path.basename(path), "line": n,
                                    "tag": parsed["tag"] if parsed else None,
                                    "excerpt": line.strip()[:160]})
    return lines_read, pending


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pending", action="store_true",
                    help="list decision lines whose build is still pending in another repository")
    ap.add_argument("--strict", action="store_true",
                    help="with --pending: exit 1 if any remain (run before merging)")
    args = ap.parse_args()
    if not args.pending:
        ap.print_help()
        raise SystemExit(0)
    read, pend = pending_builds()
    print(f"DENOMINATOR: {read} decision line(s) read in docs/**/*.md (not docs/generated/)")
    print(f"PENDING BUILDS: {len(pend)}")
    for p in pend:
        print(f"  {p['document']}:{p['line']} [{p['tag']}] {p['excerpt']}")
    raise SystemExit(1 if (args.strict and pend) else 0)
